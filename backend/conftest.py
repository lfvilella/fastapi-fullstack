import os
import unittest.mock
import pytest
import app.models

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def use_db():
    db_path = "./sql_app_test.db"
    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    app.models.Base.metadata.create_all(engine)
    session = SessionLocal()

    with unittest.mock.patch("app.database.engine", engine):
        with unittest.mock.patch("app.database.SessionLocal", return_value=session):
            yield session
            session.close()

    app.models.Base.metadata.drop_all(engine)
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def db_session(use_db):
    return use_db