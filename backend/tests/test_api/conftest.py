import pytest
import collections
import datetime

from app import models


@pytest.fixture
def payload():
    return {"name": "root", "cpf_cnpj": "80962607401", "password": "123"}


@pytest.fixture
def create_db_entity(payload, session_maker):
    entity = models.Entity(
        cpf_cnpj="80962607401", type_entity="pf", name="root"
    )
    session = session_maker()
    session.add(entity)

    api_key = models.APIKey(cpf_cnpj=payload["cpf_cnpj"])
    session.add(api_key)

    session.flush()
    session.commit()

    DB_info = collections.namedtuple("DB_info", "entity api_key")
    return DB_info(entity=entity, api_key=api_key)
