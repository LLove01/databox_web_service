# routes/log_routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database.init_db import get_db
from ..database.models import Log
from ..models.schemas import LogSchema

router = APIRouter()


@router.get("/fetch-logs", response_model=List[LogSchema])
async def read_logs(db: Session = Depends(get_db)):
    logs = db.query(Log).all()
    return logs
