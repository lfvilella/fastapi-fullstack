import pytest
import collections
import datetime
from fastapi.testclient import TestClient

from app import api
from app import models
from app import security


client = TestClient(api.app)


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


@pytest.fixture
def create_db_charge(payload, session_maker):
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


@pytest.mark.usefixtures("use_db")
class TestReadCharge:
    def build_url(self, charge_id, api_key=None):
        return f"/v.1/charge/{charge_id}?api_key={api_key}"

    def test_valid_returns_ok(self, create_db_charge):
        request = client.get(
            self.build_url(
                create_db_charge.charge.id, create_db_charge.api_key.id
            )
        )
        assert request.status_code == 200

    def test_when_api_key_is_empty_returns_forbidden(self, create_db_charge):
        request = client.get(self.build_url(create_db_charge.charge.id, ""))
        assert request.status_code == 403

    def test_valid_returns_complete_body(self, create_db_charge):
        request = client.get(
            self.build_url(
                create_db_charge.charge.id, create_db_charge.api_key.id
            )
        )
        assert request.json() == {
            "id": create_db_charge.charge.id,
            "debtor_cpf_cnpj": create_db_charge.charge.debtor_cpf_cnpj,
            "creditor_cpf_cnpj": create_db_charge.charge.creditor_cpf_cnpj,
            "debito": create_db_charge.charge.debito,
            "is_active": create_db_charge.charge.is_active,
            "created_at": create_db_charge.charge.created_at.isoformat(),
            "payed_at": create_db_charge.charge.payed_at,
        }

    def test_valid_returns_same_info_on_db(
        self, create_db_charge, session_maker
    ):
        request = client.get(
            self.build_url(
                create_db_charge.charge.id, create_db_charge.api_key.id
            )
        )
        db_charge = session_maker().query(models.Charge).first()
        assert request.json() == {
            "id": db_charge.id,
            "debtor_cpf_cnpj": db_charge.debtor_cpf_cnpj,
            "creditor_cpf_cnpj": db_charge.creditor_cpf_cnpj,
            "debito": db_charge.debito,
            "is_active": db_charge.is_active,
            "created_at": db_charge.created_at.isoformat(),
            "payed_at": db_charge.payed_at,
        }

    def test_when_invalid_id_returns_not_found(self, create_db_charge):
        request = client.get(
            self.build_url("123fakeID", create_db_charge.api_key.id)
        )
        assert request.status_code == 404
        assert request.json().get("detail") == "Charge does not exist"


@pytest.mark.usefixtures("use_db")
class TestFilterCharge:
    def build_url(
        self,
        api_key,
        debtor_cpf_cnpj=None,
        creditor_cpf_cnpj=None,
        is_active=None,
    ):
        url = f"/v.1/charge?api_key={api_key}"
        if debtor_cpf_cnpj:
            url += f"&debtor_cpf_cnpj={debtor_cpf_cnpj}"

        if creditor_cpf_cnpj:
            url += f"&creditor_cpf_cnpj={creditor_cpf_cnpj}"

        if is_active:
            url += f"&is_active={is_active}"

        return url

    def test_valid_by_debtor_cpf_cnpj_returns_ok(self, create_db_charge):
        request = client.get(
            self.build_url(
                api_key=create_db_charge.api_key.id,
                debtor_cpf_cnpj=create_db_charge.charge.debtor_cpf_cnpj,
            )
        )
        assert request.status_code == 200

    def test_valid_by_creditor_cpf_cnpj_returns_ok(self, create_db_charge):
        request = client.get(
            self.build_url(
                api_key=create_db_charge.api_key.id,
                creditor_cpf_cnpj=create_db_charge.charge.creditor_cpf_cnpj,
            )
        )
        assert request.status_code == 200

    def test_valid_by_is_active_returns_ok(self, create_db_charge):
        request = client.get(
            self.build_url(
                api_key=create_db_charge.api_key.id,
                is_active=create_db_charge.charge.is_active,
            )
        )
        assert request.status_code == 200

    def test_valid_by_all_fields_returns_ok(self, create_db_charge):
        request = client.get(
            self.build_url(
                api_key=create_db_charge.api_key.id,
                debtor_cpf_cnpj=create_db_charge.charge.debtor_cpf_cnpj,
                creditor_cpf_cnpj=create_db_charge.charge.creditor_cpf_cnpj,
                is_active=create_db_charge.charge.is_active,
            )
        )
        assert request.status_code == 200

    def test_valid_returns_complete_body(self, create_db_charge):
        request = client.get(
            self.build_url(
                api_key=create_db_charge.api_key.id,
                debtor_cpf_cnpj=create_db_charge.charge.debtor_cpf_cnpj,
            )
        )
        assert request.json() == [
                {
                "id": create_db_charge.charge.id,
                "debtor_cpf_cnpj": create_db_charge.charge.debtor_cpf_cnpj,
                "creditor_cpf_cnpj": create_db_charge.charge.creditor_cpf_cnpj,
                "debito": create_db_charge.charge.debito,
                "is_active": create_db_charge.charge.is_active,
                "created_at": create_db_charge.charge.created_at.isoformat(),
                "payed_at": create_db_charge.charge.payed_at,
            }
        ]
    
    def test_valid_returns_same_info_on_db(self, create_db_charge, session_maker):
        request = client.get(
            self.build_url(
                api_key=create_db_charge.api_key.id,
                debtor_cpf_cnpj=create_db_charge.charge.debtor_cpf_cnpj,
            )
        )
        
        db_charge = session_maker().query(models.Charge).first()
        assert request.json() == [
                {
                "id": db_charge.id,
                "debtor_cpf_cnpj": db_charge.debtor_cpf_cnpj,
                "creditor_cpf_cnpj": db_charge.creditor_cpf_cnpj,
                "debito": db_charge.debito,
                "is_active": db_charge.is_active,
                "created_at": db_charge.created_at.isoformat(),
                "payed_at": db_charge.payed_at,
            }
        ]
    
    def test_invalid_debtor_cpf_cnpj_returns_unprocessable_entity(self, create_db_charge):
        request = client.get(
            self.build_url(
                api_key=create_db_charge.api_key.id,
                debtor_cpf_cnpj="123fake",
            )
        )
        assert request.status_code == 422
      
    def test_invalid_debtor_cpf_cnpj_returns_not_found(self, create_db_charge):
        request = client.get(
            self.build_url(
                api_key=create_db_charge.api_key.id,
                debtor_cpf_cnpj=create_db_charge.charge.creditor_cpf_cnpj,
            )
        )
        assert request.status_code == 404

    def test_invalid_creditor_cpf_cnpj_returns_unprocessable_entity(self, create_db_charge):
        request = client.get(
            self.build_url(
                api_key=create_db_charge.api_key.id,
                creditor_cpf_cnpj="123fake",
            )
        )
        assert request.status_code == 422

    def test_invalid_creditor_cpf_cnpj_returns_not_found(self, create_db_charge):
        request = client.get(
            self.build_url(
                api_key=create_db_charge.api_key.id,
                creditor_cpf_cnpj=create_db_charge.charge.debtor_cpf_cnpj,
            )
        )
        assert request.status_code == 404

    def test_invalid_is_active_returns_unprocessable_entity(self, create_db_charge):
        request = client.get(
            self.build_url(
                api_key=create_db_charge.api_key.id,
                is_active="fake",
            )
        )
        assert request.status_code == 422


@pytest.mark.usefixtures("use_db")
class TestPayment:
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
