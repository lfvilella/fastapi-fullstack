from fastapi.testclient import TestClient

from .api import app

client = TestClient(app)


def test_basic():
    response = client.get("/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_create_entity():
    response = client.post(
        "/v.1/entity",
        headers={"Content-Type": "application/json"},
        json={"name": "root", "cpf_cnpj": "80962607401", "password": "123"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "name": "root",
        "cpf_cnpj": "80962607401",
        "type_entity": "pf",
    }


def test_create_entity_existing():
    response = client.post(
        "/v.1/entity",
        headers={"Content-Type": "application/json"},
        json={"name": "root", "cpf_cnpj": "80962607401", "password": "123"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Entity alredy exist"}
