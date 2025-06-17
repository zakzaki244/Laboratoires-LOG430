import pytest
from app import app

API_TOKEN = "Supermarcher22102002"

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def auth_headers():
    return {"Authorization": f"Bearer {API_TOKEN}"}

def test_get_products(client):
    resp = client.get('/api/products', headers=auth_headers())
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)

def test_create_and_get_product(client):
    # Créer un produit
    payload = {
        "name": "TestOreoPytest",
        "category": "Snack",
        "price": 4.5,
        "stock": 22,
        "store_id": 1
    }
    resp = client.post('/api/products', json=payload, headers=auth_headers())
    assert resp.status_code == 201
    pid = resp.get_json()["id"]

    # Récupérer le produit créé
    resp = client.get(f'/api/products/{pid}', headers=auth_headers())
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "TestOreoPytest"
    assert data["stock"] == 22

def test_update_product(client):
    # Créer un produit
    payload = {
        "name": "TestUpdate",
        "category": "Boisson",
        "price": 2,
        "stock": 5,
        "store_id": 1
    }
    resp = client.post('/api/products', json=payload, headers=auth_headers())
    pid = resp.get_json()["id"]

    # Mettre à jour le produit
    update = {
        "name": "TestUpdateV2",
        "stock": 12
    }
    resp = client.put(f'/api/products/{pid}', json=update, headers=auth_headers())
    assert resp.status_code == 200

    # Vérifier la modification
    resp = client.get(f'/api/products/{pid}', headers=auth_headers())
    data = resp.get_json()
    assert data["name"] == "TestUpdateV2"
    assert data["stock"] == 12

def test_delete_product(client):
    # Créer un produit
    payload = {
        "name": "ToDelete",
        "category": "Snack",
        "price": 3,
        "stock": 1,
        "store_id": 1
    }
    resp = client.post('/api/products', json=payload, headers=auth_headers())
    pid = resp.get_json()["id"]

    # Supprimer le produit
    resp = client.delete(f'/api/products/{pid}', headers=auth_headers())
    assert resp.status_code == 200

    # Vérifier la suppression
    resp = client.get(f'/api/products/{pid}', headers=auth_headers())
    assert resp.status_code == 404
