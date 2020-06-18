import pytest
from fastapi.testclient import TestClient

from app import api
from app import models
from app import security


client = TestClient(api.app)


@pytest.mark.usefixtures("use_db")
class TestLogin:
    @pytest.fixture
    def create_db_entity_with_password(self, payload, session_maker):
        entity = models.Entity(
            cpf_cnpj=payload["cpf_cnpj"],
            name=payload["name"],
            hashed_password=security.get_password_hash(payload["password"]),
        )
        session = session_maker()
        session.add(entity)

        session.flush()
        session.commit()

        return entity

    def build_url(self):
        return f"/v.1/authenticate"

    def test_valid_returns_ok(
        self, payload, create_db_entity_with_password
    ):
        response = client.post(
            self.build_url(),
            json={
                "cpf_cnpj": create_db_entity_with_password.cpf_cnpj,
                "password": payload["password"],
            },
        )
        assert response.status_code == 200
        assert (
            response.json().get("cpf_cnpj")
            == create_db_entity_with_password.cpf_cnpj
        )

    def test_valid_saves_on_db(
        self, payload, create_db_entity_with_password, session_maker
    ):
        response = client.post(
            self.build_url(),
            json={
                "cpf_cnpj": create_db_entity_with_password.cpf_cnpj,
                "password": payload["password"],
            },
        )
        assert session_maker().query(models.APIKey).count() == 1

        db_api_key = session_maker().query(models.APIKey).first()
        assert db_api_key.id == response.json().get("api_key")
        assert db_api_key.cpf_cnpj == response.json().get("cpf_cnpj")

    def test_two_valids_returns_two_api_keys(
        self, payload, create_db_entity_with_password, session_maker
    ):
        client.post(
            self.build_url(),
            json={
                "cpf_cnpj": create_db_entity_with_password.cpf_cnpj,
                "password": payload["password"],
            },
        )
        assert session_maker().query(models.APIKey).count() == 1

        client.post(
            self.build_url(),
            json={
                "cpf_cnpj": create_db_entity_with_password.cpf_cnpj,
                "password": payload["password"],
            },
        )
        assert session_maker().query(models.APIKey).count() == 2

    def test_invalid_password_returns_unprocessable_entity(
        self, create_db_entity_with_password
    ):
        response = client.post(
            self.build_url(),
            json={
                "cpf_cnpj": create_db_entity_with_password.cpf_cnpj,
                "password": "nonono",
            },
        )
        response.status_code == 422
        response.json().get("msg") == "Invalid Crendentials"

    def test_cpf_cnpj_not_registered_returns_unprocessable_entity(
        self, create_db_entity_with_password
    ):
        response = client.post(
            self.build_url(),
            json={"cpf_cnpj": "03497961786765", "password": ""}
        )
        response.status_code == 422
        response.json().get("msg") == "Invalid Crendentials"


@pytest.mark.usefixtures("use_db")
class TestLogout:
    def build_url(self, api_key):
        return f"/v.1/authenticate?api_key={api_key}"

    def test_returns_no_content(self, create_db_entity):
        response = client.delete(self.build_url(create_db_entity.api_key.id))
        assert response.status_code == 204

    def test_delete_from_db(self, create_db_entity, session_maker):
        assert session_maker().query(models.APIKey).count() == 1
        client.delete(self.build_url(create_db_entity.api_key.id))
        assert session_maker().query(models.APIKey).count() == 0

    def test_when_invalid_api_key_returns_forbidden(self, create_db_entity):
        response = client.delete(self.build_url("fake"))
        assert response.status_code == 403
