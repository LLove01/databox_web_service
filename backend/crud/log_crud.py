from sqlalchemy.orm import Session
from ..database.models import Log


def create_log(db: Session, operation: str, service_provider: str, metrics_sent: str, num_of_kpis: int, success: bool, error_msg: str = None):
    db_log = Log(operation=operation, service_provider=service_provider,
                 metrics_sent=metrics_sent, num_of_kpis=num_of_kpis, success=success, error_msg=error_msg)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Log).offset(skip).limit(limit).all()
