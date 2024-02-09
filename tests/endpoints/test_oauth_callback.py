from fastapi.testclient import TestClient
import pytest
import json
from unittest.mock import patch, mock_open
from backend.main import app  # Adjust the import according to your project structure

client = TestClient(app)

# Mocking file read for OAuth2 secrets
mock_secrets_content = json.dumps({
    "web": {
        "client_id": "mock_client_id",
        "client_secret": "mock_client_secret"
    }
})


@patch('builtins.open', new_callable=mock_open, read_data=mock_secrets_content)
@patch('backend.components.oauth2.exchange_code_for_token')
def test_oauth_callback_missing_code(mock_exchange_code_for_token, mock_file,):
    response = client.get("/oauth-callback")

    assert response.status_code == 200
    assert response.json() == {"error": "Authorization code is missing"}


@patch('builtins.open', new_callable=mock_open, read_data=mock_secrets_content)
@patch('backend.components.oauth2.exchange_code_for_token')
def test_oauth_callback_exchange_failure(mock_exchange_code_for_token, mock_file,):
    # Simulating failure to fetch access token
    mock_exchange_code_for_token.return_value = {}

    response = client.get("/oauth-callback?code=authorization_code_example")

    assert response.status_code == 200
    assert response.json() == {'error': "400: Failed to fetch access token"}

# Note: Adjust the import paths according to your project structure
