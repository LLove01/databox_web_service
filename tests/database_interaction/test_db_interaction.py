import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database.models import Base, Log
from backend.database.database import SQLALCHEMY_DATABASE_URL

# Configure a test database URL
TEST_DATABASE_URL = "sqlite:///./test_logs.db"


@pytest.fixture(scope="session")
def engine():
    return create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )


@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(engine, tables):
    """Creates a new database session for a test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(
        autocommit=False, autoflush=False, bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


def test_create_log_entry(db_session):
    new_log = Log(
        operation="fetch",
        service_provider="github",
        metrics_sent='{"stars": 10, "forks": 5}',
        num_of_kpis=2,
        success=True,
        error_msg=None
    )
    db_session.add(new_log)
    db_session.commit()

    log_entry = db_session.query(Log).filter_by(operation="fetch").first()
    assert log_entry is not None
    assert log_entry.service_provider == "github"
    assert log_entry.success


def test_log_entry_failure(db_session):
    new_log = Log(
        operation="push",
        service_provider="databox",
        metrics_sent='{}',
        num_of_kpis=0,
        success=False,
        error_msg="Network error"
    )
    db_session.add(new_log)
    db_session.commit()

    log_entry = db_session.query(Log).filter_by(operation="push").first()
    assert log_entry is not None
    assert not log_entry.success
    assert log_entry.error_msg == "Network error"
