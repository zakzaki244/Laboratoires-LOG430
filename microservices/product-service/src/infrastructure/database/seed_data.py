"""
Script d'initialisation des produits par défaut
"""
from sqlalchemy.orm import Session
from .models import ProductModel
import logging

logger = logging.getLogger(__name__)

def seed_default_products(session: Session):
    """Initialiser les produits par défaut"""
    
    # Vérifier si les produits existent déjà
    if session.query(ProductModel).first():
        logger.info("Produits par défaut déjà créés")
        return
    
    default_products = [
        # Magasin 1 - Centre-Ville
        {"name": "Bananes", "description": "Bananes fraîches et sucrées, riches en potassium", "category": "Fruits", "price": 2.99, "stock": 50, "store_id": 1},
        {"name": "Pommes", "description": "Pommes rouges croquantes et savoureuses", "category": "Fruits", "price": 3.49, "stock": 30, "store_id": 1},
        {"name": "Lait 2%", "description": "Lait partiellement écrémé, source de calcium", "category": "Produits laitiers", "price": 4.99, "stock": 25, "store_id": 1},
        {"name": "Pain blanc", "description": "Pain blanc moelleux, parfait pour les sandwichs", "category": "Boulangerie", "price": 2.49, "stock": 20, "store_id": 1},
        {"name": "Œufs (douzaine)", "description": "Œufs frais de poules élevées au sol", "category": "Produits laitiers", "price": 3.99, "stock": 35, "store_id": 1},
        
        # Magasin 2 - Banlieue
        {"name": "Oranges", "description": "Oranges juteuses et riches en vitamine C", "category": "Fruits", "price": 4.99, "stock": 40, "store_id": 2},
        {"name": "Fromage cheddar", "description": "Fromage cheddar vieilli au goût authentique", "category": "Produits laitiers", "price": 6.99, "stock": 15, "store_id": 2},
        {"name": "Céréales", "description": "Céréales nutritives pour un petit-déjeuner équilibré", "category": "Épicerie", "price": 5.99, "stock": 28, "store_id": 2},
        {"name": "Yogourt", "description": "Yogourt nature riche en probiotiques", "category": "Produits laitiers", "price": 1.99, "stock": 45, "store_id": 2},
        {"name": "Pâtes", "description": "Pâtes italiennes de qualité supérieure", "category": "Épicerie", "price": 1.49, "stock": 60, "store_id": 2},
        
        # Magasin 3 - Express
        {"name": "Tomates", "description": "Tomates fraîches et rouges, parfaites pour les salades", "category": "Légumes", "price": 3.99, "stock": 25, "store_id": 3},
        {"name": "Carottes", "description": "Carottes croquantes et sucrées, riches en bêta-carotène", "category": "Légumes", "price": 2.49, "stock": 30, "store_id": 3},
        {"name": "Bœuf haché", "description": "Bœuf haché maigre de qualité supérieure", "category": "Viandes", "price": 12.99, "stock": 12, "store_id": 3},
        {"name": "Poulet", "description": "Poitrine de poulet fraîche et tendre", "category": "Viandes", "price": 8.99, "stock": 18, "store_id": 3},
        {"name": "Riz", "description": "Riz basmati aromatique et de qualité", "category": "Épicerie", "price": 3.99, "stock": 40, "store_id": 3}
    ]
    
    try:
        for product_data in default_products:
            product_model = ProductModel(
                name=product_data['name'],
                description=product_data['description'],
                category=product_data['category'],
                price=product_data['price'],
                stock=product_data['stock'],
                store_id=product_data['store_id'],
                currency="CAD"
            )
            session.add(product_model)
            logger.info(f"Produit créé: {product_data['name']} (Magasin {product_data['store_id']})")
        
        session.commit()
        logger.info("Tous les produits par défaut ont été créés avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors de la création des produits par défaut: {str(e)}")
        session.rollback()
        raise
