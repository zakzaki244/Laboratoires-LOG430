from src.db.db import SessionLocal
from src.db.db import init_db
from src.models.store import Store
from src.models.product import Product

from db import Base
init_db()
session = SessionLocal()

# --- Ajout magasins ---
def add_store(name):
    store = session.query(Store).filter_by(name=name).first()
    if not store:
        store = Store(name=name)
        session.add(store)
        session.commit()
    return store

magasin1 = add_store("Magasin A")
magasin2 = add_store("Magasin B")
centre = add_store("Centre Logistique")

# --- Ajout produits pour chaque magasin ---
if session.query(Product).filter_by(store_id=magasin1.id).count() == 0:
    produits1 = [
        Product(name="Bouteille d'eau", category="Boisson", price=1.5, stock=50, store=magasin1),
        Product(name="Chocolat", category="Snack", price=2.0, stock=30, store=magasin1),
    ]
    session.add_all(produits1)
    session.commit()

if session.query(Product).filter_by(store_id=magasin2.id).count() == 0:
    produits2 = [
        Product(name="Coca Cola", category="Boisson", price=1.5, stock=150, store=magasin2),
        Product(name="Sandwich", category="Snack", price=2.0, stock=400, store=magasin2),
    ]
    session.add_all(produits2)
    session.commit()

if session.query(Product).filter_by(store_id=centre.id).count() == 0:
    produits_centre = [
        Product(name="Coca Cola", category="Boisson", price=1.5, stock=500, store=centre),
        Product(name="Sandwich", category="Snack", price=2.0, stock=300, store=centre),
        Product(name="Oreo", category="Snack", price=2.0, stock=300, store=centre),
        Product(name="Viande hachée", category="Boucherie", price=2.0, stock=300, store=centre),
        Product(name="Détergent", category="Ménager", price=2.0, stock=300, store=centre),
    ]
    session.add_all(produits_centre)
    session.commit()

session.close()
print("BD initialisée !")
