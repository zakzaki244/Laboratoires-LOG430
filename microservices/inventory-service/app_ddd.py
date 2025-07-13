from flask import Flask, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics
import os
from functools import wraps

# Import des composants DDD
from src.infrastructure.database import create_database_engine, create_session_factory
from src.presentation.controllers import create_inventory_controller

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Configuration de la base de données
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://log430:laboratoire@db:5432/inventory_db')
engine = create_database_engine(DATABASE_URL)
SessionLocal = create_session_factory(engine)

# Configuration des services
PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'http://product-service:5002')
STORE_SERVICE_URL = os.getenv('STORE_SERVICE_URL', 'http://store-service:5001')
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
inventory_controller = create_inventory_controller(
    SessionLocal,
    PRODUCT_SERVICE_URL,
    STORE_SERVICE_URL,
    API_TOKEN
)

# Routes DDD
@app.route('/reappro-requests', methods=['POST'])
@token_required
def create_reappro_request():
    """Créer une nouvelle demande de réapprovisionnement"""
    return inventory_controller.create_reappro_request()

@app.route('/reappro-requests/<int:request_id>', methods=['GET'])
@token_required
def get_reappro_request(request_id):
    """Récupérer une demande de réapprovisionnement par ID"""
    return inventory_controller.get_reappro_request(request_id)

@app.route('/reappro-requests', methods=['GET'])
@token_required
def get_all_reappro_requests():
    """Récupérer toutes les demandes de réapprovisionnement"""
    return inventory_controller.get_all_reappro_requests()

@app.route('/stores/<int:store_id>/reappro-requests', methods=['GET'])
@token_required
def get_reappro_requests_by_store(store_id):
    """Récupérer toutes les demandes d'un magasin"""
    return inventory_controller.get_reappro_requests_by_store(store_id)

@app.route('/products/<int:product_id>/reappro-requests', methods=['GET'])
@token_required
def get_reappro_requests_by_product(product_id):
    """Récupérer toutes les demandes pour un produit"""
    return inventory_controller.get_reappro_requests_by_product(product_id)

@app.route('/reappro-requests/pending', methods=['GET'])
@token_required
def get_pending_reappro_requests():
    """Récupérer toutes les demandes en attente"""
    return inventory_controller.get_pending_reappro_requests()

@app.route('/reappro-requests/status/<string:status>', methods=['GET'])
@token_required
def get_reappro_requests_by_status(status):
    """Récupérer toutes les demandes avec un statut donné"""
    return inventory_controller.get_reappro_requests_by_status(status)

@app.route('/reappro-requests/<int:request_id>', methods=['PUT'])
@token_required
def update_reappro_request(request_id):
    """Mettre à jour une demande de réapprovisionnement"""
    return inventory_controller.update_reappro_request(request_id)

@app.route('/reappro-requests/<int:request_id>/process', methods=['POST'])
@token_required
def process_reappro_request(request_id):
    """Traiter une demande de réapprovisionnement (approuver ou rejeter)"""
    return inventory_controller.process_reappro_request(request_id)

@app.route('/reappro-requests/<int:request_id>/complete', methods=['POST'])
@token_required
def complete_reappro_request(request_id):
    """Marquer une demande comme terminée"""
    return inventory_controller.complete_reappro_request(request_id)

@app.route('/reappro-requests/<int:request_id>', methods=['DELETE'])
@token_required
def delete_reappro_request(request_id):
    """Supprimer une demande de réapprovisionnement"""
    return inventory_controller.delete_reappro_request(request_id)

@app.route('/reappro-requests/stats', methods=['GET'])
@token_required
def get_reappro_stats():
    """Récupérer les statistiques des demandes de réapprovisionnement"""
    return inventory_controller.get_reappro_stats()

@app.route('/health')
def health_check():
    return {"status": "healthy", "service": "inventory-service"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008, debug=True)
