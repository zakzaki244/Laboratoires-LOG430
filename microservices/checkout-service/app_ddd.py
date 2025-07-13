from flask import Flask, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics
import os
from functools import wraps

# Import des composants DDD
from src.infrastructure.database import create_database_engine, create_session_factory
from src.presentation.controllers import create_checkout_controller

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Configuration de la base de données
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://log430:laboratoire@db:5432/checkout_db')
engine = create_database_engine(DATABASE_URL)
SessionLocal = create_session_factory(engine)

# Configuration des services
CART_SERVICE_URL = os.getenv('CART_SERVICE_URL', 'http://cart-service:5006')
CUSTOMER_SERVICE_URL = os.getenv('CUSTOMER_SERVICE_URL', 'http://customer-service:5005')
SALES_SERVICE_URL = os.getenv('SALES_SERVICE_URL', 'http://sales-service:5003')
PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'http://product-service:5002')
API_TOKEN = "Supermarcher22102002"

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
checkout_controller = create_checkout_controller(
    SessionLocal,
    CART_SERVICE_URL,
    PRODUCT_SERVICE_URL,
    CUSTOMER_SERVICE_URL,
    SALES_SERVICE_URL,
    API_TOKEN
)

# Routes DDD
@app.route('/orders', methods=['POST'])
@token_required
def create_order():
    """Créer une nouvelle commande"""
    return checkout_controller.create_order()

@app.route('/orders/<int:order_id>', methods=['GET'])
@token_required
def get_order(order_id):
    """Récupérer une commande par ID"""
    return checkout_controller.get_order(order_id)

@app.route('/orders', methods=['GET'])
@token_required
def get_all_orders():
    """Récupérer toutes les commandes"""
    return checkout_controller.get_all_orders()

@app.route('/customers/<int:customer_id>/orders', methods=['GET'])
@token_required
def get_customer_orders(customer_id):
    """Récupérer toutes les commandes d'un client"""
    return checkout_controller.get_customer_orders(customer_id)

@app.route('/orders/<int:order_id>', methods=['PUT'])
@token_required
def update_order(order_id):
    """Mettre à jour une commande"""
    return checkout_controller.update_order(order_id)

@app.route('/orders/<int:order_id>/confirm', methods=['POST'])
@token_required
def confirm_order(order_id):
    """Confirmer une commande"""
    return checkout_controller.confirm_order(order_id)

@app.route('/orders/<int:order_id>/cancel', methods=['POST'])
@token_required
def cancel_order(order_id):
    """Annuler une commande"""
    return checkout_controller.cancel_order(order_id)

@app.route('/orders/<int:order_id>/payment', methods=['POST'])
@token_required
def process_payment(order_id):
    """Traiter le paiement d'une commande"""
    return checkout_controller.process_payment(order_id)

@app.route('/orders/<int:order_id>/ship', methods=['POST'])
@token_required
def ship_order(order_id):
    """Expédier une commande"""
    return checkout_controller.ship_order(order_id)

@app.route('/orders/<int:order_id>/deliver', methods=['POST'])
@token_required
def deliver_order(order_id):
    """Livrer une commande"""
    return checkout_controller.deliver_order(order_id)

@app.route('/customers/<int:customer_id>/checkout', methods=['POST'])
@token_required
def checkout_from_cart(customer_id):
    """Créer une commande à partir du panier"""
    return checkout_controller.checkout_from_cart(customer_id)

@app.route('/health')
def health_check():
    return {"status": "healthy", "service": "checkout-service"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007, debug=True)
