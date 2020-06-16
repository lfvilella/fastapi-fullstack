import pytest
import collections
from fastapi.testclient import TestClient

from app import api
from app import models
from app import security


client = TestClient(api.app)


@pytest.fixture
def payload():
    return {"name": "root", "cpf_cnpj": "80962607401", "password": "123"}


@pytest.mark.usefixtures("use_db")
class TestCreateEntity:
    def test_when_valid_post_returns_ok(self, payload):
        response = client.post("/v.1/entity", json=payload)
        assert response.status_code == 200

    def test_when_valid_post_returns_complete_body(self, payload):
        response = client.post("/v.1/entity", json=payload)
        assert response.json() == {
            "name": "root",
            "cpf_cnpj": "80962607401",
            "type_entity": "pf",
        }

    def test_when_valid_post_saves_on_db(self, payload, db_session):
        response = client.post("/v.1/entity", json=payload)

        assert db_session.query(models.Entity).count() == 1

        db_entity = db_session.query(models.Entity).first()
        assert True == security.verify_password(
            payload["password"], db_entity.hashed_password
        )
        assert payload["name"] == db_entity.name
        assert payload["cpf_cnpj"] == db_entity.cpf_cnpj

    def test_when_invalid_cpf_cnpj_post_returns_error_invalid_cpf_cnpj(self, payload):
        payload["cpf_cnpj"] = "12345678910"
        response = client.post("/v.1/entity", json=payload)
        assert response.ok == False
        assert response.json() == {
            "detail": [
                {
                    "loc": ["body", "entity", "cpf_cnpj"],
                    "msg": "Invalid CPF / CNPJ",
                    "type": "type_error",
                }
            ]
        }

    def test_when_empity_post_returns_unprocessable_entity(self):
        response = client.post("/v.1/entity", json={})
        assert response.status_code == 422

    def test_when_existing_post_returns_bad_request(self, payload):
        response = client.post("/v.1/entity", json=payload)
        response = client.post("/v.1/entity", json=payload)
        assert response.status_code == 400
        assert response.json() == {"detail": "Entity already exist"}


@pytest.mark.usefixtures("use_db")
class TestReadEntity:
    @pytest.fixture
    def create_db_entity(self, payload, db_session):
        entity = models.Entity(cpf_cnpj="80962607401", type_entity="pf", name="root",)
        db_session.add(entity)

        api_key = models.APIKey(cpf_cnpj=payload["cpf_cnpj"])
        db_session.add(api_key)

        db_session.flush()
        db_session.commit()

        DB_info = collections.namedtuple("DB_info", "entity api_key")
        return DB_info(entity=entity, api_key=api_key)

    def build_url(self, cpf_cnpj, api_key=None):
        return f"/v.1/entity/{cpf_cnpj}?api_key={api_key}"

    def test_when_api_key_is_empty_returns_forbidden(self, payload):
        request = client.get(self.build_url(payload["cpf_cnpj"], ""))
        assert request.status_code == 403

    def test_when_valid_get_returns_ok(self, create_db_entity):
        request = client.get(
            self.build_url(
                create_db_entity.entity.cpf_cnpj, create_db_entity.api_key.id
            )
        )
        assert request.status_code == 200

    def test_when_valid_get_returns_complete_body(self, create_db_entity):
        request = client.get(
            self.build_url(
                create_db_entity.entity.cpf_cnpj, create_db_entity.api_key.id
            )
        )
        assert request.json() == {
            "name": create_db_entity.entity.name,
            "cpf_cnpj": create_db_entity.entity.cpf_cnpj,
            "type_entity": create_db_entity.entity.type_entity,
        }

    def test_when_valid_get_is_same_info_on_db(self, create_db_entity, db_session):
        request = client.get(
            self.build_url(
                create_db_entity.entity.cpf_cnpj, create_db_entity.api_key.id
            )
        )
        db_entity = db_session.query(models.Entity).first()
        assert request.json() == {
            "name": db_entity.name,
            "cpf_cnpj": db_entity.cpf_cnpj,
            "type_entity": db_entity.type_entity,
        }

    def test_when_get_with_invalid_cpf_cnpj(self, create_db_entity):
        request = client.get(self.build_url("1234567891-011", create_db_entity.api_key.id))
        assert request.ok == False
        assert request.json() == {
            "detail": [
                {
                    "loc": ["path", "cpf_cnpj"],
                    "msg": "Invalid CPF / CNPJ",
                    "type": "type_error",
                }
            ]
        }
