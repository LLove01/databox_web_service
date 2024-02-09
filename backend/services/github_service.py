import requests
from fastapi import HTTPException


def fetch_github_metrics_service(repo_name: str, github_token: str):
    headers = {'Authorization': f'token {github_token}'} if github_token else {}
    github_url = f"https://api.github.com/repos/{repo_name}"
    response = requests.get(github_url, headers=headers)

    if response.status_code == 404:
        raise HTTPException(
            status_code=404, detail="GitHub repository not found.")
    elif response.status_code in [401, 403, 400]:
        raise HTTPException(status_code=401, detail="Invalid GitHub token.")
    elif response.status_code != 200:
        raise HTTPException(status_code=response.status_code,
                            detail="GitHub API error.")

    data = response.json()
    metrics = {
        'stars': data.get('stargazers_count', 0),
        'forks': data.get('forks_count', 0),
        'issues': data.get('open_issues_count', 0),
        'watchers': data.get('subscribers_count', 0),
    }
    metric_keys = list(metrics.keys())
    return metrics, metric_keys
