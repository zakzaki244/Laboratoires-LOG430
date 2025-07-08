from flask import Flask
from flask import Blueprint
from db.db import SessionLocal
from models.store import Store
from models.product import Product
from models.sale import Sale

class StoreService::
# --- Utilitaire : obtenir l'ID du centre logistique ---
def get_centre_logistique_id():
    from db.db import SessionLocal
    from models.store import Store
    session = SessionLocal()
    centre = session.query(Store).filter_by(name="Centre Logistique").first()
    centre_id = centre.id if centre else None
    session.close()
    return centre_id