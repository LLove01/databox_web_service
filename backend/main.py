from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from components.github import fetch_github_metrics
from components.oauth2 import exchange_code_for_token, fetch_data_with_client_library
from components.database import SessionLocal, init_db, Log
import os
import json
import uuid
from pydantic import BaseModel
from typing import List, Optional
from databox import Client
from sqlalchemy.orm import Session


app = FastAPI()

# Initialize the database
init_db()

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

SECRETS_PATH = os.getenv("OAUTH2_SECRETS_FILE")
REDIRECT_URI = "http://localhost:8000/oauth-callback"
access_tokens_storage = {}

# Dependency to get the DB session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


with open('oauth2_secrets.json', 'r') as secrets_file:
    secrets = json.load(secrets_file)
    google_client_id = secrets['web']['client_id']
    google_client_secret = secrets['web']['client_secret']


def generate_unique_identifier():
    return str(uuid.uuid4())


@app.get("/oauth-callback")
async def oauth_callback(code: str = None):
    if code is None:
        return {"error": "Authorization code is missing"}
    try:
        token_response = await exchange_code_for_token(code, google_client_id, google_client_secret, REDIRECT_URI)
        if "access_token" in token_response:
            user_identifier = generate_unique_identifier()
            access_tokens_storage[user_identifier] = token_response["access_token"]
            # Modify the redirect URL to send the user back to the main app with the user_id parameter
            frontend_url = f"http://localhost:3000/?user_id={user_identifier}"
            return RedirectResponse(url=frontend_url)
        else:
            return {"error": "Failed to fetch access token"}
    except Exception as e:
        return {"error": str(e)}


class AnalyticsRequest(BaseModel):
    user_id: str
    property_id: str


@app.post("/fetch-analytics-data")
async def fetch_analytics_data(request: AnalyticsRequest, db: Session = Depends(get_db)):
    print(f'user_id: {request.user_id}')
    print(f'property_id: {request.property_id}')

    access_token = access_tokens_storage.get(request.user_id)
    if not access_token:
        return JSONResponse({"error": "Authentication required or session expired"}, status_code=401)

    try:
        data = fetch_data_with_client_library(
            access_token, request.property_id)

        # Assuming 'data' is a dictionary with 'metricHeaders' containing the metrics' names
        if "metricHeaders" in data:
            metric_headers = data["metricHeaders"]
            # Convert list of metric headers to JSON string for logging
            metrics_data = json.dumps(metric_headers)
            num_of_kpis = len(metric_headers)
        else:
            metric_headers = []
            metrics_data = json.dumps([])
            num_of_kpis = 0

        # Log the successful fetch operation
        log_entry = Log(
            operation='fetch',
            service_provider='Google Analytics Data API',
            metrics_sent=metrics_data,
            num_of_kpis=num_of_kpis,
            success=True,
            error_msg=None
        )
        db.add(log_entry)
        db.commit()

        return JSONResponse({"gaData": data, "redirectUrl": "/"})
    except Exception as e:
        error_msg = str(e)

        # Log the failed fetch operation
        log_entry = Log(
            operation='fetch',
            service_provider='Google Analytics Data API',
            metrics_sent=metrics_data,  # Attempted metrics to fetch
            num_of_kpis=num_of_kpis,  # Number of KPIs attempted
            success=False,
            error_msg=error_msg
        )
        db.add(log_entry)
        db.commit()

        return JSONResponse({"error": "Failed to fetch GA data", "detail": error_msg}, status_code=401)


class RepoRequest(BaseModel):
    repo_name: str
    github_token: str


@app.post("/fetch-github-metrics")
async def fetch_github_metrics_endpoint(request: RepoRequest, db: Session = Depends(get_db)):
    # Initialize variables for logging
    success = False
    error_msg = None
    metrics_data = []

    try:
        metrics = fetch_github_metrics(request.repo_name, request.github_token)
        # Assuming 'metrics' is a dictionary with metric names as keys
        metric_keys = list(metrics.keys())
        # Convert list of metric keys to JSON string for logging
        metrics_data = json.dumps(metric_keys)
        num_of_kpis = len(metric_keys)
        success = True
        # Log the successful fetch operation
        log_entry = Log(
            operation='fetch',
            service_provider='Github API',
            metrics_sent=metrics_data,
            num_of_kpis=num_of_kpis,
            success=success,
            error_msg=error_msg
        )
        db.add(log_entry)
        db.commit()

        return metrics
    except Exception as e:
        error_msg = str(e)
        # Log the failed fetch operation
        log_entry = Log(
            operation='fetch',
            service_provider='Github API',
            metrics_sent=metrics_data,  # Empty or partial data may be logged
            # This will be 0 if metrics_data is empty
            num_of_kpis=len(metrics_data),
            success=success,
            error_msg=error_msg
        )
        db.add(log_entry)
        db.commit()

        raise HTTPException(status_code=400, detail=error_msg)


# Define a Pydantic model for the metrics payload
class Metric(BaseModel):
    name: str
    value: float
    date: Optional[str] = None
    attributes: Optional[dict] = None


class MetricsPayload(BaseModel):
    metrics: List[Metric]
    databox_access_token: str


@app.post("/send-metrics")
async def send_metrics(payload: MetricsPayload, db: Session = Depends(get_db)):
    print(f'metrics: {payload.metrics}')
    print(f'databox token: {payload.databox_access_token}')

    client = Client(payload.databox_access_token)

    # Prepare the data for Databox
    metrics_data = [
        {
            'key': metric.name,
            'value': metric.value,
            'date': metric.date,
            'attributes': metric.attributes
        } for metric in payload.metrics
    ]

    # Extract just the metric names (keys) for logging
    metric_keys = [metric['key'] for metric in metrics_data]

    # Attempt to send data to Databox
    success = False
    error_msg = None
    try:
        response = client.insert_all(metrics_data)
        success = True
    except Exception as e:
        error_msg = str(e)

    # Log the operation in the database
    log_entry = Log(
        operation='push',
        service_provider='Databox Push API',
        metrics_sent=json.dumps(metric_keys),  # Log only the keys
        num_of_kpis=len(metric_keys),
        success=success,
        error_msg=error_msg
    )
    db.add(log_entry)
    db.commit()

    if success:
        return {"message": "Metrics sent to Databox successfully."}
    else:
        raise HTTPException(status_code=500, detail=error_msg)
