"""
Script d'initialisation des données d'inventaire par défaut
"""
from sqlalchemy.orm import Session
from .models import InventoryItemModel
import logging

logger = logging.getLogger(__name__)

def seed_default_inventory(session: Session):
    """Initialiser l'inventaire par défaut"""
    
    # Vérifier si l'inventaire existe déjà
    if session.query(InventoryItemModel).first():
        logger.info("Inventaire par défaut déjà créé")
        return
    
    # Créer des éléments d'inventaire pour les produits (IDs 1-15)
    default_inventory = []
    
    # Magasin 1 - Produits 1-5
    for product_id in range(1, 6):
        default_inventory.append({
            "product_id": product_id,
            "store_id": 1,
            "quantity": 50 if product_id <= 2 else 25,  # Plus de fruits
            "min_threshold": 10,
            "max_threshold": 100
        })
    
    # Magasin 2 - Produits 6-10
    for product_id in range(6, 11):
        default_inventory.append({
            "product_id": product_id,
            "store_id": 2,
            "quantity": 40 if product_id == 6 else 30,  # Plus d'oranges
            "min_threshold": 15,
            "max_threshold": 80
        })
    
    # Magasin 3 - Produits 11-15
    for product_id in range(11, 16):
        default_inventory.append({
            "product_id": product_id,
            "store_id": 3,
            "quantity": 20 if product_id >= 13 else 30,  # Moins de viandes
            "min_threshold": 5,
            "max_threshold": 60
        })
    
    try:
        for inventory_data in default_inventory:
            inventory_model = InventoryItemModel(
                product_id=inventory_data['product_id'],
                store_id=inventory_data['store_id'],
                quantity=inventory_data['quantity'],
                min_threshold=inventory_data['min_threshold'],
                max_threshold=inventory_data['max_threshold'],
                is_active=True
            )
            session.add(inventory_model)
            logger.info(f"Inventaire créé: Produit {inventory_data['product_id']} - Magasin {inventory_data['store_id']}")
        
        session.commit()
        logger.info("Tous les éléments d'inventaire par défaut ont été créés avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'inventaire par défaut: {str(e)}")
        session.rollback()
        raise
