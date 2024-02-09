from fastapi.testclient import TestClient
import pytest
import requests_mock
from backend.main import app  # Adjust the import according to your project structure

client = TestClient(app)


def test_fetch_github_metrics_success():
    repo_name = "octocat/Hello-World"
    github_token = "ghp_exampleToken"
    mock_response = {
        "stargazers_count": 150,
        "forks_count": 100,
        "open_issues_count": 10,
        "subscribers_count": 75
    }

    with requests_mock.Mocker() as m:
        m.get(f"https://api.github.com/repos/{repo_name}", json=mock_response)

        response = client.post("/fetch-github-metrics", json={
            "repo_name": repo_name,
            "github_token": github_token
        })

        assert response.status_code == 200
        assert response.json() == {
            "stars": 150,
            "forks": 100,
            "issues": 10,
            "watchers": 75
        }


def test_fetch_github_metrics_invalid_token():
    # Simulate request with valid repo name but invalid token
    response = client.post(
        "/fetch-github-metrics",
        json={"repo_name": "example/repo", "github_token": "invalid_token"}
    )

    # Assert failure response
    # Assuming your endpoint returns 401 for unauthorized access
    assert response.status_code == 400
    assert response.json() == {"detail": "Failed to fetch GitHub metrics"}
