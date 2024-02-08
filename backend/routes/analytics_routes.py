# routes/analytics_routes.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..services.analytics_service import fetch_and_log_analytics_data
from ..database.init_db import get_db
from ..models.schemas import AnalyticsRequest  # Adjust import path as necessary
from fastapi.responses import JSONResponse
from backend.utilities.token_storage import access_tokens_storage


router = APIRouter()


@router.post("/fetch-analytics-data")
async def analytics_data_endpoint(request: AnalyticsRequest, db: Session = Depends(get_db)):
    user_id = request.user_id
    property_id = request.property_id
    # Ensure access_tokens_storage is accessible
    access_token = access_tokens_storage.get(user_id)

    if not access_token:
        return JSONResponse({"error": "Authentication required or session expired"}, status_code=401)

    try:
        data = await fetch_and_log_analytics_data(user_id, property_id, access_token, db)
        return JSONResponse({"gaData": data, "redirectUrl": "/"})
    except Exception as e:
        return JSONResponse({"error": "Failed to fetch GA data", "detail": str(e)}, status_code=401)
