from flask import Flask, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics
import os
from functools import wraps

# Import des composants DDD
from src.infrastructure.database import create_database_engine, create_session_factory
from src.presentation.controllers.customer_controller import create_customer_controller
from src.application.services.customer_service import CustomerService
from src.infrastructure.repositories.customer_repository_simple import SqlCustomerRepository

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Configuration de la base de données
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://log430:laboratoire@db:5432/customer_db')
engine = create_database_engine(DATABASE_URL)
SessionLocal = create_session_factory(engine)

# Configuration
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

# Création des services
def get_customer_service():
    """Factory pour créer le service customer avec une session"""
    session = SessionLocal()
    customer_repository = SqlCustomerRepository(session)
    return CustomerService(customer_repository)

# Création du contrôleur
customer_controller = create_customer_controller(SessionLocal)

# Enregistrement du blueprint
app.register_blueprint(customer_controller)

# Routes DDD
@app.route('/customers', methods=['POST'])
@token_required
def create_customer():
    """Créer un nouveau client"""
    return customer_controller.create_customer()

@app.route('/customers/<int:customer_id>', methods=['GET'])
@token_required
def get_customer(customer_id):
    """Récupérer un client par ID"""
    return customer_controller.get_customer(customer_id)

@app.route('/customers', methods=['GET'])
@token_required
def get_all_customers():
    """Récupérer tous les clients"""
    return customer_controller.get_all_customers()

@app.route('/customers/<int:customer_id>', methods=['PUT'])
@token_required
def update_customer(customer_id):
    """Mettre à jour un client"""
    return customer_controller.update_customer(customer_id)

@app.route('/customers/<int:customer_id>', methods=['DELETE'])
@token_required
def delete_customer(customer_id):
    """Supprimer un client"""
    return customer_controller.delete_customer(customer_id)

@app.route('/customers/email/<string:email>', methods=['GET'])
@token_required
def get_customer_by_email(email):
    """Récupérer un client par email"""
    return customer_controller.get_customer_by_email(email)

@app.route('/customers/<int:customer_id>/activate', methods=['POST'])
@token_required
def activate_customer(customer_id):
    """Activer un client"""
    return customer_controller.activate_customer(customer_id)

@app.route('/customers/<int:customer_id>/deactivate', methods=['POST'])
@token_required
def deactivate_customer(customer_id):
    """Désactiver un client"""
    return customer_controller.deactivate_customer(customer_id)

@app.route('/health')
def health_check():
    return {"status": "healthy", "service": "customer-service"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
