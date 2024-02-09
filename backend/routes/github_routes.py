from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
from ..database.init_db import get_db
from ..services.github_service import fetch_github_metrics_service
from ..models.schemas import RepoRequest
from ..crud.log_crud import create_log

router = APIRouter()


@router.post("/fetch-github-metrics")
async def fetch_github_metrics_endpoint(request: RepoRequest, db: Session = Depends(get_db)):
    try:
        metrics, metric_keys = fetch_github_metrics_service(
            request.repo_name, request.github_token)

        # Log the successful operation
        create_log(
            db=db,
            operation='fetch',
            service_provider='Github API',
            metrics_sent=json.dumps(metric_keys),  # Only log the keys
            num_of_kpis=len(metric_keys),
            success=True,
            error_msg=None
        )
        return metrics
    except HTTPException as http_exc:
        # Log the failed operation with specific error from the service
        create_log(
            db=db,
            operation='fetch',
            service_provider='Github API',
            metrics_sent=json.dumps([]),  # No metrics sent in case of failure
            num_of_kpis=0,
            success=False,
            error_msg=http_exc.detail  # Use the detail from the raised HTTPException
        )
        raise http_exc  # Re-raise the caught HTTPException to forward it to the client
