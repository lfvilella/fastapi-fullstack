import os
import unittest.mock
import pytest

import app.database

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def use_db():
    db_path = "./sql_app_test.db"
    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with unittest.mock.patch("app.database.engine", engine):
        with unittest.mock.patch("app.database.SessionLocal", SessionLocal):
            app.models.Base.metadata.create_all(app.database.engine)
            yield
            app.models.Base.metadata.drop_all(app.database.engine)
            if os.path.exists(db_path):
                os.remove(db_path)


@pytest.fixture
def db_session(use_db):
    session = app.database.SessionLocal()
    try:
        yield session
    finally:
        session.close()
