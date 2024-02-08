from fastapi.responses import JSONResponse
from ..components.oauth2 import fetch_data_with_client_library
from ..crud.log_crud import create_log
from sqlalchemy.orm import Session
import json


async def fetch_and_log_analytics_data(user_id: str, property_id: str, access_token: str, db: Session):
    try:
        data = fetch_data_with_client_library(access_token, property_id)

        # Assuming 'data' is a dictionary with 'metricHeaders' containing the metrics' names
        if "metricHeaders" in data:
            metric_headers = data["metricHeaders"]
            metrics_data = json.dumps(metric_headers)
            num_of_kpis = len(metric_headers)
        else:
            metric_headers = []
            metrics_data = json.dumps([])
            num_of_kpis = 0

        # Use create_log function for logging the successful operation
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

        # Use create_log function to log the failed operation
        create_log(
            db=db,
            operation='fetch',
            service_provider='Google Analytics Data API',
            metrics_sent=metrics_data,  # Attempted metrics to fetch
            num_of_kpis=num_of_kpis,  # Number of KPIs attempted
            success=False,
            error_msg=error_msg
        )

        # Return a JSONResponse indicating the failure
        return JSONResponse({"error": "Failed to fetch GA data", "detail": error_msg}, status_code=401)
