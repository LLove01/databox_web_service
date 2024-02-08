from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
from ..database.init_db import get_db
from ..services.databox_service import send_metrics_to_databox_service
from ..crud.log_crud import create_log  # Ensure this is correctly imported
from ..models.schemas import MetricsPayload

router = APIRouter()


@router.post("/send-metrics")
async def send_metrics(payload: MetricsPayload, db: Session = Depends(get_db)):
    # Extract the metric names for logging
    metric_keys = [metric.name for metric in payload.metrics]

    success, metric_keys = send_metrics_to_databox_service(
        payload.metrics, payload.databox_access_token)

    # Log the operation
    create_log(
        db=db,
        operation='push',
        service_provider='Databox',
        metrics_sent=json.dumps(metric_keys),
        num_of_kpis=len(metric_keys),
        success=success,
        error_msg="" if success else "Failed to send metrics"
    )

    if success:
        return {"message": "Metrics sent to Databox successfully."}
    else:
        raise HTTPException(status_code=500, detail="Failed to send metrics")
