from flask import Flask, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.infrastructure.repositories.customer_repository_impl import SqlCustomerRepository
from src.infrastructure.database import Base
from src.infrastructure.database.seed_data import seed_default_users
import os
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Configuration de la base de données
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://log430:laboratoire@db-customers:5432/customers_db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Configuration
API_TOKEN = "Supermarcher22102002"

# Authentification
def token_required(f):
    from functools import wraps
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

# Création des tables et initialisation des données
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Tables créées avec succès")
    
    # Initialiser les utilisateurs par défaut
    session = SessionLocal()
    seed_default_users(session)
    session.close()
    
except Exception as e:
    logger.error(f"Erreur lors de l'initialisation: {str(e)}")

# Fonction pour obtenir une session de base de données
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

@app.route('/api/customers/register', methods=['POST'])
def register():
    """Endpoint d'inscription d'un nouveau client"""
    try:
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['email', 'first_name', 'last_name', 'phone', 'password', 'address']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Tous les champs sont requis'}), 400
        
        # Validation de l'adresse
        address = data['address']
        if not isinstance(address, dict) or not all(key in address for key in ['street', 'city', 'postal_code', 'country']):
            return jsonify({'error': 'Format d\'adresse invalide'}), 400
        
        # Vérifier si l'email existe déjà
        existing_customer = customer_repository.get_by_email(data['email'])
        if existing_customer:
            return jsonify({'error': 'Email déjà utilisé'}), 400
        
        # Hasher le mot de passe
        password_hash = generate_password_hash(data['password'])
        
        # Créer le client
        customer_data = {
            'email': data['email'],
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'phone': data['phone'],
            'password_hash': password_hash,
            'address': address,
            'is_active': True
        }
        
        customer = customer_repository.create(customer_data)
        return jsonify({
            'message': 'Client créé avec succès',
            'customer_id': customer['id']
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/customers/login', methods=['POST'])
def login():
    """Endpoint de connexion d'un client"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email et mot de passe requis'}), 400
        
        # Trouver le client par email
        customer = customer_repository.get_by_email(data['email'])
        if not customer:
            return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
        
        # Vérifier le mot de passe
        if not check_password_hash(customer['password_hash'], data['password']):
            return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
        
        # Vérifier si le compte est actif
        if not customer.get('is_active', True):
            return jsonify({'error': 'Compte désactivé'}), 401
        
        return jsonify({
            'message': 'Connexion réussie',
            'customer': {
                'id': customer['id'],
                'email': customer['email'],
                'first_name': customer['first_name'],
                'last_name': customer['last_name']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    return {"status": "healthy", "service": "customer-service"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
