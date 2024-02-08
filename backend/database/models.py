from sqlalchemy import Column, String, Integer, Boolean, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    operation = Column(String)  # 'fetch' or 'push'
    service_provider = Column(String)  # 'github', 'GAD API', or 'databox'
    time_of_sending = Column(DateTime, default=func.now())
    metrics_sent = Column(String)  # JSON string of metrics sent
    num_of_kpis = Column(Integer)
    success = Column(Boolean)
    error_msg = Column(String, nullable=True)
