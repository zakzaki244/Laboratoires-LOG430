from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from prometheus_flask_exporter import PrometheusMetrics
import os
from functools import wraps

# Import des composants DDD
from src.infrastructure.database import Base
from src.infrastructure.database.seed_data import seed_default_stores
from src.presentation.controllers import create_store_controller

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Configuration de la base de données
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://log430:laboratoire@db:5433/stores_db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Configuration
API_TOKEN = "Supermarcher22102002"

# Création des tables
Base.metadata.create_all(bind=engine)

# Initialisation des données par défaut
try:
    session = SessionLocal()
    seed_default_stores(session)
    session.close()
    print("Données par défaut initialisées avec succès")
except Exception as e:
    print(f"Erreur lors de l'initialisation des données: {str(e)}")

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
store_controller = create_store_controller(SessionLocal)

# Routes DDD
@app.route('/api/stores', methods=['GET'])
@token_required
def get_stores():
    """Récupérer tous les magasins"""
    return store_controller.get_stores()

@app.route('/api/stores/<int:store_id>', methods=['GET'])
@token_required
def get_store(store_id):
    """Récupérer un magasin spécifique"""
    return store_controller.get_store(store_id)

@app.route('/api/stores', methods=['POST'])
@token_required
def create_store():
    """Créer un nouveau magasin"""
    return store_controller.create_store()

@app.route('/api/stores/<int:store_id>', methods=['PUT'])
@token_required
def update_store(store_id):
    """Mettre à jour un magasin"""
    return store_controller.update_store(store_id)

@app.route('/api/stores/<int:store_id>', methods=['DELETE'])
@token_required
def delete_store(store_id):
    """Supprimer un magasin"""
    return store_controller.delete_store(store_id)

@app.route('/health')
def health_check():
    return {"status": "healthy", "service": "store-service"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
