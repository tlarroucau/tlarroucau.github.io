import os
import re
from github import Github

def update_activity():
    # Get GitHub token from environment variable
    token = os.getenv('GH_TOKEN')
    if not token:
        print("Error: GH_TOKEN environment variable not set")
        return

    g = Github(token)
    user = g.get_user()

    # Get recently updated repositories
    repos = user.get_repos(sort="pushed", direction="desc")
    username = user.login
    
    top_repos = []
    count = 0
    for repo in repos:
        if count >= 3:
            break
        
        # Skip the portfolio repository itself
        if repo.name == "tlarroucau.github.io":
            continue
            
        # We allow forks and non-owned repos now, but we check for actual contribution
        
        try:
            # Count MY commits
            # Note: This might be slow for very large repos, but necessary for accuracy
            my_commits = repo.get_commits(author=username).totalCount
            
            # Count MY issues (created) - this includes PRs in GitHub API
            my_issues = repo.get_issues(creator=username).totalCount
            
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

if __name__ == "__main__":
    update_activity()
