from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch
from backend.main import app  # Adjust the import according to your project structure
from backend.utilities.token_storage import access_tokens_storage

client = TestClient(app)


@pytest.fixture
def mock_access_token():
    # Mocking access token retrieval for a given user
    access_tokens_storage['user_id_example'] = 'access_token_example'
    yield
    # Cleanup or reset the mock as necessary after tests run
    access_tokens_storage.pop('user_id_example', None)


@patch("backend.services.analytics_service.fetch_data_with_client_library")
@patch("backend.crud.log_crud.create_log")
def test_fetch_analytics_data_success(mock_create_log, mock_fetch_data, mock_access_token):
    mock_fetch_data.return_value = {
        "metricHeaders": [{"name": "views"}, {"name": "clicks"}]
    }

    response = client.post("/fetch-analytics-data", json={
        "user_id": "user_id_example",
        "property_id": "property_id_example"
    })

    assert response.status_code == 200
    data = response.json()
    assert "gaData" in data
    assert data["gaData"]["metricHeaders"] == [
        {"name": "views"}, {"name": "clicks"}]


@patch("backend.services.analytics_service.fetch_data_with_client_library")
@patch("backend.crud.log_crud.create_log")
def test_fetch_analytics_data_invalid_credentials(mock_create_log, mock_fetch_data, mock_access_token):
    mock_fetch_data.side_effect = Exception("Invalid credentials")

    response = client.post("/fetch-analytics-data", json={
        "user_id": "user_id_example",
        "property_id": "property_id_wrong"
    })

    assert response.status_code == 401
    assert response.json() == {
        "error": "Failed to fetch GA data", "detail": 'Object of type JSONResponse is not JSON serializable'}
