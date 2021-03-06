import pytest
import collections

from app import models
from app import data_access


@pytest.fixture
def payload():
    return {"name": "root", "cpf_cnpj": "80962607401", "password": "123"}


@pytest.fixture
def create_db_entity(session_maker):
    def _create(session=None, persist=True, **data):
        session = session or session_maker()
        entity = models.Entity(**data)
        session.add(entity)
        session.flush()
        if persist:
            session.commit()
        return entity

    return _create


@pytest.fixture
def db_entity_fixture(session_maker):
    entity = models.Entity(
        cpf_cnpj="80962607401", type_entity="pf", name="root"
    )
    session = session_maker()
    session.add(entity)

    api_key = data_access.create_api_key(
        session, entity.cpf_cnpj, persist=False
    )

    session.flush()
    session.commit()

    DB_info = collections.namedtuple("DB_info", "entity api_key")
    return DB_info(entity=entity, api_key=api_key)
