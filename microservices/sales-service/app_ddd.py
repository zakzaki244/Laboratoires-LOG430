from flask import Flask, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics
import os
from functools import wraps

# Import des composants DDD
from src.infrastructure.database import create_database_engine, create_session_factory
from src.presentation.controllers import create_sales_controller

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Configuration de la base de données
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://log430:laboratoire@db:5432/sales_db')
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
sales_controller = create_sales_controller(
    SessionLocal, 
    PRODUCT_SERVICE_URL, 
    STORE_SERVICE_URL, 
    API_TOKEN
)

# Routes DDD
@app.route('/sales', methods=['POST'])
@token_required
def create_sale():
    """Créer une nouvelle vente"""
    return sales_controller.create_sale()

@app.route('/sales/<int:sale_id>', methods=['GET'])
@token_required
def get_sale(sale_id):
    """Récupérer une vente par ID"""
    return sales_controller.get_sale(sale_id)

@app.route('/sales', methods=['GET'])
@token_required
def get_all_sales():
    """Récupérer toutes les ventes"""
    return sales_controller.get_all_sales()

@app.route('/stores/<int:store_id>/sales', methods=['GET'])
@token_required
def get_sales_by_store(store_id):
    """Récupérer les ventes d'un magasin"""
    return sales_controller.get_sales_by_store(store_id)

@app.route('/sales/stats', methods=['GET'])
@token_required
def get_sales_stats():
    """Récupérer les statistiques de ventes"""
    return sales_controller.get_sales_stats()

@app.route('/sales/report', methods=['GET'])
@token_required
def get_sales_report():
    """Générer un rapport de ventes"""
    return sales_controller.get_sales_report()

@app.route('/health')
def health_check():
    return {"status": "healthy", "service": "sales-service"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
