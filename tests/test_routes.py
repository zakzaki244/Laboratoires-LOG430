import pytest
from src.app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["username"] = "testuser"
            sess["role"] = "employe"
        yield client

def test_index(client):
    rv = client.get("/")
    assert rv.status_code == 200
    assert b"Systeme POS Web" in rv.data

def test_search_get(client):
    rv = client.get("/search")
    assert rv.status_code == 200
    assert b"Recherche de produits" in rv.data

def test_stock(client):
    rv = client.get("/stock")
    assert rv.status_code == 200
    assert b"Resultat du stock" in rv.data
