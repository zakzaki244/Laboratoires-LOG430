from flask import Flask
from flask import Blueprint
from src.db.db import SessionLocal
from src.models.store import Store
from src.models.product import Product
from src.models.sale import Sale


@app.context_processor
def inject_centre_id():
    return dict(centre_id=get_centre_logistique_id())

# --- Utilitaire : obtenir l'ID du centre logistique ---
def get_centre_logistique_id():
    from src.db.db import SessionLocal
    from src.models.store import Store
    session = SessionLocal()
    centre = session.query(Store).filter_by(name="Centre Logistique").first()
    centre_id = centre.id if centre else None
    session.close()
    return centre_id