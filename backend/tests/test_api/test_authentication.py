import pytest
from fastapi.testclient import TestClient

from app import api
from app import models
from app import data_access

client = TestClient(api.app)


@pytest.mark.usefixtures("use_db")
class TestLogin:
    @pytest.fixture
    def db_entity_fixture_with_password(
        self, payload, db_entity_fixture, session_maker
    ):
        session = session_maker()
        session.query(models.APIKey).delete()
        return data_access.entity_set_password(
            session,
            db_entity_fixture.entity.cpf_cnpj,
            password=payload["password"],
        )

    def build_url(self):
        return f"/api/v.1/authenticate"

    def test_valid_returns_ok(self, payload, db_entity_fixture_with_password):
        response = client.post(
            self.build_url(),
            json={
                "cpf_cnpj": db_entity_fixture_with_password.cpf_cnpj,
                "password": payload["password"],
            },
        )
        assert response.status_code == 200
        assert (
            response.json().get("cpf_cnpj")
            == db_entity_fixture_with_password.cpf_cnpj
        )

    def test_valid_saves_on_db(
        self, payload, db_entity_fixture_with_password, session_maker
    ):
        response = client.post(
            self.build_url(),
            json={
                "cpf_cnpj": db_entity_fixture_with_password.cpf_cnpj,
                "password": payload["password"],
            },
        )
        assert session_maker().query(models.APIKey).count() == 1

        db_api_key = session_maker().query(models.APIKey).first()
        assert db_api_key.id in response.json().get("api_key")
        assert db_api_key.cpf_cnpj == response.json().get("cpf_cnpj")

    def test_two_valids_returns_two_api_keys(
        self, payload, db_entity_fixture_with_password, session_maker
    ):
        client.post(
            self.build_url(),
            json={
                "cpf_cnpj": db_entity_fixture_with_password.cpf_cnpj,
                "password": payload["password"],
            },
        )
        assert session_maker().query(models.APIKey).count() == 1

        client.post(
            self.build_url(),
            json={
                "cpf_cnpj": db_entity_fixture_with_password.cpf_cnpj,
                "password": payload["password"],
            },
        )
        assert session_maker().query(models.APIKey).count() == 2

    def test_invalid_password_returns_unprocessable_entity(
        self, db_entity_fixture_with_password
    ):
        response = client.post(
            self.build_url(),
            json={
                "cpf_cnpj": db_entity_fixture_with_password.cpf_cnpj,
                "password": "nonono",
            },
        )
        response.status_code == 422
        response.json().get("msg") == "Invalid Crendentials"

    def test_cpf_cnpj_not_registered_returns_unprocessable_entity(
        self, db_entity_fixture_with_password
    ):
        response = client.post(
            self.build_url(),
            json={"cpf_cnpj": "03497961786765", "password": ""},
        )
        response.status_code == 422
        response.json().get("msg") == "Invalid Crendentials"


@pytest.mark.usefixtures("use_db")
class TestLogout:
    def build_url(self, api_key):
        return f"/api/v.1/authenticate?api_key={api_key}"

    def test_returns_no_content(self, db_entity_fixture):
        response = client.delete(self.build_url(db_entity_fixture.api_key))
        assert response.status_code == 204

    def test_delete_from_db(self, db_entity_fixture, session_maker):
        assert session_maker().query(models.APIKey).count() == 1
        client.delete(self.build_url(db_entity_fixture.api_key))
        assert session_maker().query(models.APIKey).count() == 0

    def test_when_invalid_api_key_returns_forbidden(self, db_entity_fixture):
        response = client.delete(self.build_url("fake"))
        assert response.status_code == 403
