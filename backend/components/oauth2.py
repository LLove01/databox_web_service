import httpx
from fastapi import HTTPException

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest
from google.oauth2.credentials import Credentials
import asyncio


async def exchange_code_for_token(code: str, client_id: str, client_secret: str, redirect_uri: str) -> dict:
    """
    Exchange authorization code for an access token.
    """
    token_url = "https://oauth2.googleapis.com/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data, headers=headers)
    if response.status_code != 200:
        raise HTTPException(
            status_code=400, detail="Failed to fetch access token")
    return response.json()


def fetch_data_with_client_library(access_token: str, property_id: str):
    credentials = Credentials(token=access_token)
    client = BetaAnalyticsDataClient(credentials=credentials)
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[{"name": "city"}],
        metrics=[
            {"name": "activeUsers"},  # Today's active users
            {"name": "eventCount"},    # Count of events occurred today
            {"name": "sessions"}
        ],
        date_ranges=[
            {"start_date": "10daysAgo", "end_date": "today"},
        ],
    )

    response = client.run_report(request=request)

    # Initialize processed_response with headers only
    processed_response = {
        "rows": [],
        "dimensionHeaders": [header.name for header in response.dimension_headers],
        "metricHeaders": [header.name for header in response.metric_headers]
    }

    if not response.rows:
        # If there are no rows, add a default row with zeros
        default_row = {
            # Adjust based on your dimensions if necessary
            "dimensions": ["N/A"],
            # Fill with zeros based on number of metrics
            "metrics": ["0" for _ in processed_response["metricHeaders"]]
        }
        processed_response["rows"].append(default_row)
    else:
        for row in response.rows:
            processed_row = {
                "dimensions": row.dimension_values,
                "metrics": row.metric_values
            }
            # Convert dimension and metric values to a serializable format
            processed_row["dimensions"] = [
                dim.value for dim in processed_row["dimensions"]]
            processed_row["metrics"] = [
                met.value for met in processed_row["metrics"]]
            processed_response["rows"].append(processed_row)

    return processed_response


async def fetch_data_background(access_token: str, property_id: str):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None, fetch_data_with_client_library, access_token, property_id
    )
