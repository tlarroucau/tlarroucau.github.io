import os
import re
import sys
from github import Github, GithubException

def update_activity():
    # Get GitHub token from environment variable
    token = os.getenv('GH_TOKEN')
    if not token:
        print("Error: GH_TOKEN environment variable not set")
        sys.exit(1)

    try:
        g = Github(token)
        user = g.get_user()
        print(f"Authenticated as: {user.login}")

        # Get recently updated repositories
        repos = user.get_repos(sort="pushed", direction="desc")
        username = user.login
        
        top_repos = []
        count = 0
        checked_count = 0
        
        # Check the first 30 recently pushed repos to find 3 active ones
        for repo in repos:
            if count >= 3:
                break
            if checked_count > 30:
                break
            
            checked_count += 1
            
            try:
                print(f"Checking {repo.full_name}...")
                
                # Skip the portfolio repository itself
                if repo.name == "tlarroucau.github.io":
                    continue
                
                # Count MY commits using Search API (more robust)
                try:
                    query = f"repo:{repo.full_name} author:{username}"
                    my_commits = g.search_commits(query).totalCount
                except Exception as e:
                    print(f"Error searching commits for {repo.full_name}: {e}")
                    my_commits = 0
                
                # Count MY issues/PRs using Search API
                try:
                    query = f"repo:{repo.full_name} author:{username}"
                    my_issues = g.search_issues(query).totalCount
                except Exception as e:
                    print(f"Error searching issues for {repo.full_name}: {e}")
                    my_issues = 0
                
                print(f"  Commits: {my_commits}, Issues: {my_issues}")
                
                # If I have 0 activity, skip this repo (even if it was pushed recently by someone else)
                if my_commits == 0 and my_issues == 0:
                    continue
                    
                repo_data = {
                    'repo': repo,
                    'commits': my_commits,
                    'issues': my_issues
                }
                
                top_repos.append(repo_data)
                count += 1
                
            except Exception as e:
                print(f"Skipping {repo.full_name} due to error: {e}")
                continue

        html_content = ""
        
        for item in top_repos:
            repo = item['repo']
            name = repo.full_name
            is_private = repo.private
            commits = item['commits']
            issues = item['issues']
            
            # Determine visibility tag and link
            if is_private:
                visibility_class = "private"
                visibility_text = "Private"
                # Private repos don't get a link
                name_html = f"<span>{name}</span>"
            else:
                visibility_class = "public"
                visibility_text = "Public"
                # Public repos get a link
                name_html = f'<a href="{repo.html_url}" target="_blank">{name}</a>'

            stats_text = []
            if commits > 0:
                stats_text.append(f"{commits} commits")
            if issues > 0:
                stats_text.append(f"{issues} issues/PRs")
            
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
        replacement = f'\\1{html_content}\n                \\3'
        
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

        # Write back to index.html
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        print("Successfully updated Recent Activity in index.html")
        
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_activity()
