from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from prometheus_flask_exporter import PrometheusMetrics
import os
from functools import wraps

# Import des composants DDD
from src.infrastructure.database import Base
from src.infrastructure.database.seed_data import seed_default_products
from src.presentation.controllers import create_product_controller

# Import du système d'authentification JWT
from microservices.shared.jwt_auth import (
    responsable_produit_required,
    management_required,
    authenticated_required,
)

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Configuration de la base de données
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://log430:laboratoire@db:5432/products_db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Configuration des services
STORE_SERVICE_URL = os.getenv('STORE_SERVICE_URL', 'http://store-service:5001')
API_TOKEN = "Supermarcher22102002"

# Création des tables
Base.metadata.create_all(bind=engine)

# Initialisation des données par défaut
try:
    session = SessionLocal()
    seed_default_products(session)
    session.close()
    print("Données par défaut initialisées avec succès")
except Exception as e:
    print(f"Erreur lors de l'initialisation des données: {str(e)}")

# Authentification legacy pour compatibilité
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        token = auth_header.split(" ")[1]
        if token != API_TOKEN:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

# Création du contrôleur
product_controller = create_product_controller(SessionLocal, STORE_SERVICE_URL, API_TOKEN)

# Routes DDD
@app.route('/api/products', methods=['GET'])
@authenticated_required  # Tous les utilisateurs connectés peuvent voir les produits
def get_products():
    """Récupérer tous les produits"""
    return product_controller.get_products()

@app.route('/api/products/<int:product_id>', methods=['GET'])
@authenticated_required  # Tous les utilisateurs connectés peuvent voir un produit
def get_product(product_id):
    """Récupérer un produit spécifique"""
    return product_controller.get_product(product_id)

@app.route('/api/products/search', methods=['GET'])
@authenticated_required  # Tous les utilisateurs connectés peuvent rechercher
def search_products():
    """Rechercher des produits par nom ou catégorie"""
    return product_controller.search_products()

@app.route('/api/products', methods=['POST'])
@responsable_produit_required  # Seul le responsable produit peut créer des produits
def create_product():
    """Créer un nouveau produit"""
    return product_controller.create_product()

@app.route('/api/products/<int:product_id>', methods=['PUT'])
@responsable_produit_required  # Seul le responsable produit peut modifier des produits
def update_product(product_id):
    """Mettre à jour un produit"""
    return product_controller.update_product(product_id)

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
@responsable_produit_required  # Seul le responsable produit peut supprimer des produits
def delete_product(product_id):
    """Supprimer un produit"""
    return product_controller.delete_product(product_id)

@app.route('/api/products/<int:product_id>/stock', methods=['PUT'])
@management_required  # Admin ou gestionnaire peuvent mettre à jour le stock
def update_stock(product_id):
    """Mettre à jour le stock d'un produit"""
    return product_controller.update_stock(product_id)

@app.route('/health')
def health_check():
    return {"status": "healthy", "service": "product-service"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
