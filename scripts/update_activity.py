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
    # We fetch a few more than 3 to filter out forks if desired, or just take the top ones
    repos = user.get_repos(sort="pushed", direction="desc")
    
    top_repos = []
    count = 0
    for repo in repos:
        if count >= 3:
            break
        # Optional: Skip forks if you only want original work
        # if repo.fork: continue
        
        top_repos.append(repo)
        count += 1

    html_content = ""
    
    for repo in top_repos:
        name = repo.full_name
        is_private = repo.private
        
        # Get commit count (this can be slow for large repos, so we might want to limit or cache)
        # For a personal portfolio, getting total count is usually fine.
        # Note: get_commits().totalCount is efficient in PyGithub (uses header info)
        try:
            commit_count = repo.get_commits().totalCount
        except:
            commit_count = 0
            
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

        html_content += f"""
                <div class="repo-item">
                    <div>
                        {name_html}
                        <span class="repo-tag {visibility_class}">{visibility_text}</span>
                    </div>
                    <span class="repo-stats">{commit_count} commits</span>
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
