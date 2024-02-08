import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database.init_db import get_db
from ..crud.log_crud import create_log
from ..services.github_service import fetch_github_metrics_service
from ..models.schemas import RepoRequest

router = APIRouter()


@router.post("/fetch-github-metrics")
async def fetch_github_metrics_endpoint(request: RepoRequest, db: Session = Depends(get_db)):
    try:
        metrics, metric_keys = fetch_github_metrics_service(
            request.repo_name, request.github_token)

        # Use the create_log function for logging
        create_log(
            db=db,
            operation='fetch',
            service_provider='Github API',
            metrics_sent=json.dumps(metric_keys),  # Only log the keys
            num_of_kpis=len(metric_keys),
            success=True,
            error_msg=None
        )
        print(f'metrics: {metrics}')
        return metrics
    except Exception as e:
        # Use the create_log function to log failed operations
        create_log(
            db=db,
            operation='fetch',
            service_provider='Github API',
            # Log an empty list if the operation fails
            metrics_sent=json.dumps([]),
            num_of_kpis=0,
            success=False,
            error_msg=str(e)
        )

        raise HTTPException(status_code=400, detail=str(e))
