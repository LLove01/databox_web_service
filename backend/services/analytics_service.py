from fastapi.responses import JSONResponse
from ..components.oauth2 import fetch_data_with_client_library
from ..crud.log_crud import create_log
from sqlalchemy.orm import Session
import json


async def fetch_and_log_analytics_data(user_id: str, property_id: str, access_token: str, db: Session):
    try:
        data = fetch_data_with_client_library(access_token, property_id)
        metric_headers = data.get("metricHeaders", [])
        metrics_data = json.dumps([header for header in metric_headers])
        num_of_kpis = len(metric_headers)

        create_log(
            db=db,
            operation='fetch',
            service_provider='Google Analytics Data API',
            metrics_sent=metrics_data,
            num_of_kpis=num_of_kpis,
            success=True,
            error_msg=None
        )

        return data

    except Exception as e:
        error_msg = str(e)
        status_code = 500  # Default to internal server error

        if "invalid credentials" in error_msg.lower():
            status_code = 401
        elif "not found" in error_msg.lower():
            status_code = 404
        elif "permission denied" in error_msg.lower():
            status_code = 403
        # Add more conditions as needed based on the errors encountered

        create_log(
            db=db,
            operation='fetch',
            service_provider='Google Analytics Data API',
            metrics_sent="[]",
            num_of_kpis=0,
            success=False,
            error_msg=error_msg
        )

        return JSONResponse({"error": "Failed to fetch GA data", "detail": error_msg}, status_code=status_code)
