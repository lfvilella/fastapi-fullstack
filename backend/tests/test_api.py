import pytest
from fastapi.testclient import TestClient

from app import api
from app import models
from app import security

client = TestClient(api.app)


@pytest.mark.usefixtures("use_db")
class TestCreateEntity:
    @pytest.fixture
    def payload(self):
        return {"name": "root", "cpf_cnpj": "80962607401", "password": "123"}

    def test_when_valid_post_returns_valid_response(self, payload):
        response = client.post("/v.1/entity", json=payload)
        assert response.status_code == 200
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

    def test_when_invalid_post_returns_422(self):
        response = client.post("/v.1/entity", json={})
        assert response.status_code == 422


# def test_create_entity_existing(use_db):
#     response = client.post(
#         "/v.1/entity",
#         headers={"Content-Type": "application/json"},
#         json={"name": "root", "cpf_cnpj": "80962607401", "password": "123"},
#     )
#     assert response.status_code == 400
#     assert response.json() == {"detail": "Entity alredy exist"}
