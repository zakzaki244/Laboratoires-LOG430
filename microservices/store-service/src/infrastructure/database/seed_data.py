"""
Script d'initialisation des magasins par défaut
"""
from sqlalchemy.orm import Session
from .models import StoreModel
import logging

logger = logging.getLogger(__name__)

def seed_default_stores(session: Session):
    """Initialiser les magasins par défaut"""
    
    # Vérifier si les magasins existent déjà
    if session.query(StoreModel).first():
        logger.info("Magasins par défaut déjà créés")
        return
    
    default_stores = [
        {
            "name": "Supermarché Centre-Ville",
            "address": "123 Rue Principale, Montréal, QC H1A 1B2",
            "phone": "514-555-0001"
        },
        {
            "name": "Supermarché Banlieue",
            "address": "456 Boulevard Suburban, Laval, QC H7A 2B3",
            "phone": "450-555-0002"
        },
        {
            "name": "Supermarché Express",
            "address": "789 Avenue Express, Longueuil, QC J4A 3C4",
            "phone": "450-555-0003"
        }
    ]
    
    try:
        for store_data in default_stores:
            store_model = StoreModel(
                name=store_data['name'],
                address=store_data['address'],
                phone=store_data['phone']
            )
            session.add(store_model)
            logger.info(f"Magasin créé: {store_data['name']}")
        
        session.commit()
        logger.info("Tous les magasins par défaut ont été créés avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors de la création des magasins par défaut: {str(e)}")
        session.rollback()
        raise
