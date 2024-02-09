# from fastapi.testclient import TestClient
# import pytest
# from unittest.mock import patch
# # Ensure this matches the actual import path of your FastAPI app
# from backend.main import app

# client = TestClient(app)


# @pytest.fixture
# def metrics_payload():
#     return {
#         "metrics": [
#             {"name": "page_views", "value": 100},
#             {"name": "clicks", "value": 50}
#         ],
#         "databox_access_token": "databox_test_token"
#     }


# @patch("backend.services.databox_service.send_metrics_to_databox_service")
# def test_send_metrics_success(mock_send_service, metrics_payload):
#     # Mock the service to simulate a successful operation
#     mock_send_service.return_value = (True, ["page_views", "clicks"])

#     response = client.post("/send-metrics", json=metrics_payload)

#     assert response.status_code == 200
#     assert response.json() == {
#         "message": "Metrics sent to Databox successfully."}
#     mock_send_service.assert_called_once_with(
#         metrics_payload["metrics"], metrics_payload["databox_access_token"]
#     )


# @patch("backend.services.databox_service.send_metrics_to_databox_service")
# def test_send_metrics_failure(mock_send_service, metrics_payload):
#     # Mock the service to simulate a failure in sending metrics
#     mock_send_service.return_value = (False, ["page_views", "clicks"])

#     response = client.post("/send-metrics", json=metrics_payload)

#     assert response.status_code == 500
#     assert response.json() == {"detail": "Failed to send metrics"}
#     mock_send_service.assert_called_once_with(
#         metrics_payload["metrics"], metrics_payload["databox_access_token"]
#     )
