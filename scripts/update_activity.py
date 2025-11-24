import os
import re
import sys
from datetime import datetime, timedelta
from github import Github, GithubException

def update_activity():
    # Get GitHub token from environment variable
    token = os.getenv('GH_TOKEN')
    if not token:
        print("Warning: GH_TOKEN environment variable not set. Skipping update.")
        return

    try:
        g = Github(token)
        user = g.get_user()
        print(f"Authenticated as: {user.login}")
        username = user.login

        # Timeframe: Last 3 months
        since_date = datetime.now() - timedelta(days=90)
        print(f"Checking activity since: {since_date.date()}")

        # Get recently updated repositories
        repos = user.get_repos(sort="pushed", direction="desc")
        
        top_repos = []
        count = 0
        checked_count = 0
        
        # Check the first 20 recently pushed repos to find 3 active ones
        for repo in repos:
            if count >= 3:
                break
            if checked_count > 20:
                break
            
            checked_count += 1
            
            try:
                print(f"Checking {repo.full_name}...")
                
                # Skip the portfolio repository itself
                if repo.name == "tlarroucau.github.io":
                    continue
                
                # 1. Count MY commits (last 3 months)
                my_commits = 0
                try:
                    commits = repo.get_commits(author=username, since=since_date)
                    my_commits = commits.totalCount
                except GithubException as e:
                    if e.status == 409: # Empty repository
                        my_commits = 0
                    else:
                        print(f"  Error counting commits: {e}")
                        my_commits = 0
                except Exception as e:
                    print(f"  Generic error counting commits: {e}")
                    my_commits = 0
                
                # 2. Count MY issues/PRs CREATED (last 3 months)
                my_created = 0
                try:
                    # Fetch issues created by user, updated recently
                    issues = repo.get_issues(creator=username, state='all', since=since_date)
                    for issue in issues:
                        if issue.created_at >= since_date:
                            my_created += 1
                except Exception as e:
                    print(f"  Error counting created issues: {e}")
                    my_created = 0

                # 3. Count MY issues/PRs CLOSED (last 3 months)
                my_closed = 0
                try:
                    # Only check closed issues if it's not a massive public repo to avoid timeouts
                    # We use a heuristic: if I have 0 commits and 0 created issues, 
                    # and it's a fork, maybe don't scan thousands of closed issues.
                    # But let's try to scan with a limit.
                    
                    closed_issues = repo.get_issues(state='closed', since=since_date)
                    # Limit to checking the last 100 closed issues to prevent hanging on popular repos
                    check_limit = 100 
                    checked_closed = 0
                    
                    for issue in closed_issues:
                        if checked_closed >= check_limit:
                            break
                        
                        if issue.closed_at and issue.closed_at >= since_date:
                            # Check if closed by me
                            # Note: closed_by can be None
                            if issue.closed_by and issue.closed_by.login == username:
                                my_closed += 1
                        
                        checked_closed += 1
                except Exception as e:
                    print(f"  Error counting closed issues: {e}")
                    my_closed = 0
                
                print(f"  -> Commits: {my_commits}, Created: {my_created}, Closed: {my_closed}")
                
                # If I have 0 activity, skip this repo
                if my_commits == 0 and my_created == 0 and my_closed == 0:
                    continue
                    
                repo_data = {
                    'repo': repo,
                    'commits': my_commits,
                    'created': my_created,
                    'closed': my_closed
                }
                
                top_repos.append(repo_data)
                count += 1
                
            except Exception as e:
                print(f"Skipping {repo.full_name} due to error: {e}")
                continue

        if not top_repos:
            print("No active repositories found.")
            return

        html_content = ""
        
        for item in top_repos:
            repo = item['repo']
            name = repo.full_name
            is_private = repo.private
            commits = item['commits']
            created = item['created']
            closed = item['closed']
            
            # Determine visibility tag and link
            if is_private:
                visibility_class = "private"
                visibility_text = "Private"
                name_html = f"<span>{name}</span>"
            else:
                visibility_class = "public"
                visibility_text = "Public"
                name_html = f'<a href="{repo.html_url}" target="_blank">{name}</a>'

            stats_text = []
            if commits > 0:
                stats_text.append(f"{commits} commits")
            if created > 0:
                stats_text.append(f"{created} created")
            if closed > 0:
                stats_text.append(f"{closed} closed")
            
            stats_html = ", ".join(stats_text)

            html_content += f"""
                <div class="repo-item">
                    <div>
                        {name_html}
                        <span class="repo-tag {visibility_class}">{visibility_text}</span>
                    </div>
                    <span class="repo-stats">{stats_html}</span>
                </div>"""

        # Read index.html
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()

        # Replace content between markers
        pattern = r'(<!-- START_ACTIVITY -->)(.*?)(<!-- END_ACTIVITY -->)'
        match = re.search(pattern, content, flags=re.DOTALL)
        if match:
            start_marker = match.group(1)
            end_marker = match.group(3)
            new_section = f"{start_marker}{html_content}\n                {end_marker}"
            
            # Use string slicing instead of re.sub to avoid backslash escaping issues
            start_idx = match.start()
            end_idx = match.end()
            new_content = content[:start_idx] + new_section + content[end_idx:]
            
            # Write back to index.html
            with open('index.html', 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            print("Successfully updated Recent Activity in index.html")
        else:
            print("Error: Markers not found in index.html")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Script failed with error: {e}")
        # We do NOT exit with error code 1, so the Action doesn't show as "Failed"
        # It just won't update the file.
        return

if __name__ == "__main__":
    try:
        update_activity()
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1) # Exit with error if it crashes at top level
