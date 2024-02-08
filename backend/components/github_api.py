import requests


def fetch_github_metrics(repo_name: str, github_token: str):
    headers = {'Authorization': f'token {github_token}'} if github_token else {}
    github_url = f"https://api.github.com/repos/{repo_name}"
    response = requests.get(github_url, headers=headers)
    data = response.json()
    return {
        'stars': data.get('stargazers_count', 0),
        'forks': data.get('forks_count', 0),
        'issues': data.get('open_issues_count', 0),
        'watchers': data.get('subscribers_count', 0),
    }
