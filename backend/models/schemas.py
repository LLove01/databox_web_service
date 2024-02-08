from pydantic import BaseModel
from typing import List, Optional


class Metric(BaseModel):
    name: str
    value: float
    date: Optional[str] = None
    attributes: Optional[dict] = None


class MetricsPayload(BaseModel):
    metrics: List[Metric]
    databox_access_token: str


class AnalyticsRequest(BaseModel):
    user_id: str
    property_id: str


class RepoRequest(BaseModel):
    repo_name: str
    github_token: str
