from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


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


class LogSchema(BaseModel):
    id: int
    operation: str
    service_provider: str
    time_of_sending: datetime
    metrics_sent: str
    num_of_kpis: int
    success: bool
    error_msg: Optional[str] = None

    class Config:
        orm_mode = True
