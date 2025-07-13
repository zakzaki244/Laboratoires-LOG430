from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from prometheus_flask_exporter import PrometheusMetrics
import os
import redis
from functools import wraps

# Import des composants DDD
from src.infrastructure.database import Base
from src.presentation.controllers import create_cart_controller

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Configuration de la base de données
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://log430:laboratoire@db:5432/cart_db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Configuration Redis
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379')
redis_client = redis.from_url(REDIS_URL)

# Configuration des services
PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'http://product-service:5002')
CUSTOMER_SERVICE_URL = os.getenv('CUSTOMER_SERVICE_URL', 'http://customer-service:5005')
API_TOKEN = "Supermarcher22102002"

# Création des tables
Base.metadata.create_all(bind=engine)

# Authentification
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
cart_controller = create_cart_controller(
    SessionLocal, 
    PRODUCT_SERVICE_URL, 
    CUSTOMER_SERVICE_URL,
    redis_client,
    API_TOKEN
)

# Routes DDD
@app.route('/carts', methods=['POST'])
@token_required
def create_cart():
    """Créer un nouveau panier"""
    return cart_controller.create_cart()

@app.route('/carts/<int:cart_id>', methods=['GET'])
@token_required
def get_cart(cart_id):
    """Récupérer un panier par son ID"""
    return cart_controller.get_cart(cart_id)

@app.route('/customers/<int:customer_id>/cart', methods=['GET'])
@token_required
def get_active_cart(customer_id):
    """Récupérer le panier actif d'un client"""
    return cart_controller.get_active_cart(customer_id)

@app.route('/customers/<int:customer_id>/cart/items', methods=['POST'])
@token_required
def add_to_cart(customer_id):
    """Ajouter un article au panier"""
    return cart_controller.add_to_cart(customer_id)

@app.route('/customers/<int:customer_id>/cart/items', methods=['PUT'])
@token_required
def update_cart_item(customer_id):
    """Mettre à jour un article du panier"""
    return cart_controller.update_cart_item(customer_id)

@app.route('/customers/<int:customer_id>/cart/items/<int:product_id>', methods=['DELETE'])
@token_required
def remove_from_cart(customer_id, product_id):
    """Supprimer un article du panier"""
    return cart_controller.remove_from_cart(customer_id, product_id)

@app.route('/customers/<int:customer_id>/cart/clear', methods=['POST'])
@token_required
def clear_cart(customer_id):
    """Vider le panier"""
    return cart_controller.clear_cart(customer_id)

@app.route('/health')
def health_check():
    return {"status": "healthy", "service": "cart-service"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)
