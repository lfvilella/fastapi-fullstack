import pytest
import collections
import datetime
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
    def test_when_valid_post_returns_created(self, payload):
        response = client.post("/v.1/entity", json=payload)
        assert response.status_code == 201

    def test_when_valid_post_returns_complete_body(self, payload):
        response = client.post("/v.1/entity", json=payload)
        assert response.json() == {
            "name": payload["name"],
            "cpf_cnpj": payload["cpf_cnpj"],
            "type_entity": "pf",
        }

    def test_when_valid_post_saves_on_db(self, payload, session_maker):
        response = client.post("/v.1/entity", json=payload)

        assert session_maker().query(models.Entity).count() == 1

        db_entity = session_maker().query(models.Entity).first()
        assert security.verify_password(
            payload["password"], db_entity.hashed_password
        )
        assert payload["name"] == db_entity.name
        assert payload["cpf_cnpj"] == db_entity.cpf_cnpj

    def test_when_invalid_cpf_cnpj_post_returns_error_invalid_cpf_cnpj(
        self, payload
    ):
        payload["cpf_cnpj"] = "12345678910"
        response = client.post("/v.1/entity", json=payload)
        assert response.ok == False
        assert (
            response.json().get("detail").pop(0).get("msg")
            == "Invalid CPF / CNPJ"
        )

    def test_when_empity_post_returns_unprocessable_entity(self):
        response = client.post("/v.1/entity", json={})
        assert response.status_code == 422

    def test_when_existing_post_returns_bad_request(self, payload):
        response = client.post("/v.1/entity", json=payload)
        response = client.post("/v.1/entity", json=payload)
        assert response.status_code == 400
        assert response.json() == {"detail": "Entity already exist"}


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


@pytest.mark.usefixtures("use_db")
class TestReadEntity:
    def build_url(self, cpf_cnpj, api_key=None):
        return f"/v.1/entity/{cpf_cnpj}?api_key={api_key}"

    def test_when_api_key_is_empty_returns_forbidden(self, create_db_entity):
        request = client.get(
            self.build_url(create_db_entity.entity.cpf_cnpj, "")
        )
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

    def test_when_valid_get_is_same_info_on_db(
        self, create_db_entity, session_maker
    ):
        request = client.get(
            self.build_url(
                create_db_entity.entity.cpf_cnpj, create_db_entity.api_key.id
            )
        )
        db_entity = session_maker().query(models.Entity).first()
        assert request.json() == {
            "name": db_entity.name,
            "cpf_cnpj": db_entity.cpf_cnpj,
            "type_entity": db_entity.type_entity,
        }

    def test_when_get_with_invalid_cpf_cnpj(self, create_db_entity):
        request = client.get(
            self.build_url("1234567891-011", create_db_entity.api_key.id)
        )
        assert request.ok == False
        assert (
            request.json().get("detail").pop(0).get("msg")
            == "Invalid CPF / CNPJ"
        )


@pytest.mark.usefixtures("use_db")
class TestCreateCharge:
    @pytest.fixture
    def payload_charge(self, create_db_entity):
        return {
            "debtor": {
                "name": "name-tester-without-entity",
                "cpf_cnpj": "03497961786765",
            },
            "creditor_cpf_cnpj": create_db_entity.entity.cpf_cnpj,
            "debito": 100,
        }

    def build_url(self, api_key=None):
        return f"/v.1/charge?api_key={api_key}"

    def test_when_valid_post_returns_created(
        self, payload_charge, create_db_entity
    ):
        response = client.post(
            self.build_url(create_db_entity.api_key.id), json=payload_charge
        )
        assert response.status_code == 201

    def test_when_valid_post_returns_complete_body(
        self, payload_charge, create_db_entity
    ):
        response = client.post(
            self.build_url(create_db_entity.api_key.id), json=payload_charge
        )
        assert (
            response.json().get("debtor_cpf_cnpj")
            == payload_charge["debtor"]["cpf_cnpj"]
        )
        assert (
            response.json().get("creditor_cpf_cnpj")
            == payload_charge["creditor_cpf_cnpj"]
        )
        assert response.json().get("debito") == payload_charge["debito"]
        assert response.json().get("is_active") == True
        assert response.json().get("payed_at") == None

    def test_when_valid_post_saves_on_db(
        self, payload_charge, create_db_entity, session_maker
    ):
        response = client.post(
            self.build_url(create_db_entity.api_key.id), json=payload_charge
        )

        assert session_maker().query(models.Charge).count() == 1

        db_charge = session_maker().query(models.Charge).first()
        assert (
            db_charge.debtor_cpf_cnpj == payload_charge["debtor"]["cpf_cnpj"]
        )
        assert (
            db_charge.creditor_cpf_cnpj == payload_charge["creditor_cpf_cnpj"]
        )
        assert db_charge.debito == payload_charge["debito"]
        assert db_charge.payed_at == None

    def test_when_api_key_is_empty_returns_forbidden(self, payload_charge):
        response = client.post(self.build_url(""), json=payload_charge)
        assert response.status_code == 403

    def test_when_invalid_cpf_cnpj_post_returns_error_invalid_cpf_cnpj(
        self, payload_charge, create_db_entity
    ):
        payload_charge["debtor"]["cpf_cnpj"] = "12345678910"
        response = client.post(
            self.build_url(create_db_entity.api_key.id), json=payload_charge
        )
        assert response.ok == False
        assert (
            response.json().get("detail").pop(0).get("msg")
            == "Invalid CPF / CNPJ"
        )

    def test_when_invalid_cpf_cnpj_post_returns_error_debtor_not_found(
        self, payload_charge, create_db_entity
    ):
        payload_charge["debtor"]["cpf_cnpj"] = "12345678910"
        response = client.post(
            self.build_url(create_db_entity.api_key.id), json=payload_charge
        )
        assert response.ok == False
        assert (
            response.json().get("detail").pop(1).get("msg")
            == "Debtor not found"
        )

    def test_when_invalid_creditor_cpf_cnpj_post_returns_error_invalid_cpf_cnpj(
        self, payload_charge, create_db_entity
    ):
        payload_charge["creditor_cpf_cnpj"] = "12345678910"
        response = client.post(
            self.build_url(create_db_entity.api_key.id), json=payload_charge
        )
        assert response.ok == False
        assert (
            response.json().get("detail").pop(0).get("msg")
            == "Invalid CPF / CNPJ"
        )

    def test_when_empity_post_returns_error_unprocessable_entity(
        self, create_db_entity
    ):
        response = client.post(
            self.build_url(create_db_entity.api_key.id), json={}
        )
        assert response.status_code == 422

    def test_when_add_debt_to_yourself_returns_invalid(
        self, payload_charge, create_db_entity
    ):
        payload_charge["debtor"]["cpf_cnpj"] = payload_charge[
            "creditor_cpf_cnpj"
        ]
        response = client.post(
            self.build_url(create_db_entity.api_key.id), json=payload_charge
        )
        assert response.ok == False
        assert (
            response.json().get("detail").pop(0).get("msg")
            == "You can not add debt for yourself"
        )

    def test_when_zero_debt_post_returns_error(
        self, payload_charge, create_db_entity
    ):
        payload_charge["debito"] = 0
        response = client.post(
            self.build_url(create_db_entity.api_key.id), json=payload_charge
        )
        assert response.ok == False
        assert (
            response.json().get("detail").pop(0).get("msg")
            == "ensure this value is greater than 0"
        )

    def test_when_negative_debt_post_returns_error(
        self, payload_charge, create_db_entity
    ):
        payload_charge["debito"] = -100
        response = client.post(
            self.build_url(create_db_entity.api_key.id), json=payload_charge
        )
        assert response.ok == False
        assert (
            response.json().get("detail").pop(0).get("msg")
            == "ensure this value is greater than 0"
        )


@pytest.mark.usefixtures("use_db")
class TestReadCharge:
    pass


@pytest.mark.usefixtures("use_db")
class TestPayment:
    @pytest.fixture
    def create_db_charge(self, payload, session_maker):
        db_charge = models.Charge(
            debtor_cpf_cnpj="03497961786765",
            creditor_cpf_cnpj=payload["cpf_cnpj"],
            debito=100,
            is_active=True,
            created_at=datetime.datetime.utcnow(),
            payed_at=None,
        )
        session = session_maker()
        session.add(db_charge)

        api_key = models.APIKey(cpf_cnpj=payload["cpf_cnpj"])
        session.add(api_key)

        session.flush()
        session.commit()

        DB_info = collections.namedtuple("DB_info", "charge api_key")
        return DB_info(charge=db_charge, api_key=api_key)

    def build_url(self, api_key=None):
        return f"/v.1/charge/payment?api_key={api_key}"

    def test_when_valid_payment_post_returns_ok(self, create_db_charge):
        response = client.post(
            self.build_url(create_db_charge.api_key.id),
            json={
                "id": create_db_charge.charge.id,
                "creditor_cpf_cnpj": create_db_charge.charge.creditor_cpf_cnpj,
            },
        )
        assert response.status_code == 200

    def test_when_valid_payment_post_returns_complete_body(
        self, payload, create_db_charge
    ):
        response = client.post(
            self.build_url(create_db_charge.api_key.id),
            json={
                "id": create_db_charge.charge.id,
                "creditor_cpf_cnpj": create_db_charge.charge.creditor_cpf_cnpj,
            },
        )
        data = response.json()
        assert data.get("id") == create_db_charge.charge.id
        assert (
            data.get("debtor_cpf_cnpj")
            == create_db_charge.charge.debtor_cpf_cnpj
        )
        assert data.get("creditor_cpf_cnpj") == payload["cpf_cnpj"]
        assert data.get("debito") == create_db_charge.charge.debito
        assert data.get("is_active") == False

        # Check only YY/MM/DD
        assert (
            data.get("created_at")
            == create_db_charge.charge.created_at.isoformat()
        )

        payed_at = datetime.datetime.utcnow().isoformat()
        assert data.get("payed_at")[:10:] == payed_at[:10:]

    def test_when_valid_payment_post_saves_on_db(
        self, create_db_charge, session_maker
    ):
        assert session_maker().query(models.Charge).count() == 1
        response = client.post(
            self.build_url(create_db_charge.api_key.id),
            json={
                "id": create_db_charge.charge.id,
                "creditor_cpf_cnpj": create_db_charge.charge.creditor_cpf_cnpj,
            },
        )
        assert session_maker().query(models.Charge).count() == 1

        db_charge = session_maker().query(models.Charge).first()
        assert response.json() == {
            "id": db_charge.id,
            "debtor_cpf_cnpj": db_charge.debtor_cpf_cnpj,
            "creditor_cpf_cnpj": db_charge.creditor_cpf_cnpj,
            "debito": db_charge.debito,
            "created_at": db_charge.created_at.isoformat(),
            "is_active": db_charge.is_active,
            "payed_at": db_charge.payed_at.isoformat(),
        }

    def test_when_invalid_payment_post_returns_unprocessable_entity(
        self, create_db_charge
    ):
        response = client.post(
            self.build_url(create_db_charge.api_key.id),
            json={"id": create_db_charge.charge.id, "creditor_cpf_cnpj": "",},
        )
        assert response.status_code == 422
        assert (
            response.json().get("detail").pop(0).get("msg")
            == "Invalid CPF / CNPJ"
        )

    def test_when_invalid_id_payment_post_returns_not_found(
        self, create_db_charge
    ):
        response = client.post(
            self.build_url(create_db_charge.api_key.id),
            json={
                "id": "",
                "creditor_cpf_cnpj": create_db_charge.charge.creditor_cpf_cnpj,
            },
        )
        assert response.status_code == 404


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

    def test_when_login_valid_post_returns_ok(
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

    def test_when_login_valid_post_saves_on_db(
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

    def test_when_two_login_valid_post_returns_two_api_keys(
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

        response = client.post(
            self.build_url(),
            json={
                "cpf_cnpj": create_db_entity_with_password.cpf_cnpj,
                "password": payload["password"],
            },
        )
        assert session_maker().query(models.APIKey).count() == 2

    def test_when_invalid_password_returns_unprocessable_entity(
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

    def test_when_cpf_cnpj_not_registered_returns_unprocessable_entity(
        self, create_db_entity_with_password
    ):
        response = client.post(
            self.build_url(),
            json={"cpf_cnpj": "03497961786765", "password": "",},
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
        response = client.delete(self.build_url(create_db_entity.api_key.id))
        assert session_maker().query(models.APIKey).count() == 0

    def test_when_invalid_api_key_returns_forbidden(self, create_db_entity):
        response = client.delete(self.build_url("fake"))
        assert response.status_code == 403
