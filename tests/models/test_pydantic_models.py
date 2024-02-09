import pytest
from pydantic import ValidationError
from datetime import datetime
from backend.models.schemas import Metric, MetricsPayload, AnalyticsRequest, RepoRequest


def test_metric_creation():
    metric_data = {
        "name": "page_views",
        "value": 100.0,
        "date": datetime.now().isoformat(),
        "attributes": {"page": "/home"}
    }
    metric = Metric(**metric_data)
    assert metric.name == metric_data["name"]
    assert metric.value == metric_data["value"]
    assert metric.date == metric_data["date"]
    assert metric.attributes == metric_data["attributes"]


def test_metrics_payload_creation():
    metrics_data = {
        "metrics": [
            {"name": "page_views", "value": 100.0},
            {"name": "clicks", "value": 50.0}
        ],
        "databox_access_token": "test_token"
    }
    payload = MetricsPayload(**metrics_data)
    assert len(payload.metrics) == 2
    assert payload.databox_access_token == metrics_data["databox_access_token"]


def test_analytics_request_validation():
    request_data = {
        "user_id": "user123",
        "property_id": "property456"
    }
    request = AnalyticsRequest(**request_data)
    assert request.user_id == request_data["user_id"]
    assert request.property_id == request_data["property_id"]


def test_repo_request_validation():
    repo_data = {
        "repo_name": "openai/gpt-3",
        "github_token": "ghp_testtoken"
    }
    repo_request = RepoRequest(**repo_data)
    assert repo_request.repo_name == repo_data["repo_name"]
    assert repo_request.github_token == repo_data["github_token"]


def test_metric_with_optional_fields():
    metric_data = {
        "name": "bounce_rate",
        "value": 75.0
    }
    metric = Metric(**metric_data)
    assert metric.name == metric_data["name"]
    assert metric.value == metric_data["value"]
    assert metric.date is None
    assert metric.attributes is None


def test_metric_validation_error():
    with pytest.raises(ValidationError):
        # Incorrect type for 'value'
        Metric(name="conversion_rate", value="high")
