from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # Path to your SQLite database

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    operation = Column(String)  # 'fetch' or 'push'
    service_provider = Column(String)  # 'github', 'GAD API', or 'databox'
    time_of_sending = Column(DateTime, default=func.now())
    metrics_sent = Column(String)  # A JSON field or stringified JSON
    num_of_kpis = Column(Integer)
    success = Column(Boolean)
    error_msg = Column(String, nullable=True)

# Use this function in your main FastAPI app to create database tables


def init_db():
    Base.metadata.create_all(bind=engine)
