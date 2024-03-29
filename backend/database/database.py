from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Or another database connection string
SQLALCHEMY_DATABASE_URL = "sqlite:///./logs.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
