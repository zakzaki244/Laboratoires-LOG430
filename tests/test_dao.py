import pytest
from src.dao import DAO
from src.models import Product
from src.db import Base, engine

@pytest.fixture(autouse=True, scope="function")
def setup_db():
    # Drop toutes les tables
    Base.metadata.drop_all(bind=engine)
    # Recrée toutes les tables
    Base.metadata.create_all(bind=engine)
    yield
    # Après le test, re-drop pour le prochain test
    Base.metadata.drop_all(bind=engine)


def test_create_and_search_product():
    dao = DAO()
    # Ajout produit test
    p = Product(name="Banane", category="Fruit", price=1.5, stock=20)
    dao.session.add(p)
    dao.session.commit()

    # Recherche par nom
    result = dao.search_products("Banane")
    assert len(result) == 1
    assert result[0].name == "Banane"

    # Recherche par catégorie
    result = dao.search_products("Fruit")
    assert len(result) == 1

def test_create_sale_and_delete():
    dao = DAO()
    # Ajoute un produit
    p = Product(name="Pomme", category="Fruit", price=1.0, stock=15)
    dao.session.add(p)
    dao.session.commit()

    # Création vente
    sale_id = dao.create_sale([(p, 5)])
    p = dao.get_product(p.id)
    assert p.stock == 10  # Stock décrémenté

    # Suppression vente
    dao.delete_sale(sale_id)
    p = dao.get_product(p.id)
    assert p.stock == 15  # Stock restauré

def test_list_stock():
    dao = DAO()
    dao.session.add(Product(name="Tomate", category="Légume", price=2, stock=30))
    dao.session.commit()
    stock = dao.list_stock()
    assert any(prod.name == "Tomate" for prod in stock)
