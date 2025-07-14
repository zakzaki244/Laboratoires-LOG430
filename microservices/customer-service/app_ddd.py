from flask import Flask, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from functools import wraps
import os
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Configuration de la base de données
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://log430:laboratoire@db:5432/customers_db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Configuration
API_TOKEN = "Supermarcher22102002"

# Import des modèles
from src.infrastructure.database.models import Base, CustomerModel, UserRole
from src.infrastructure.database.seed_data import seed_default_users
from src.utils.jwt_utils import generate_jwt_token

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

# Initialisation de la base de données
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Tables créées avec succès")
    
    # Initialiser les utilisateurs par défaut
    session = SessionLocal()
    seed_default_users(session)
    session.close()
    logger.info("Initialisation terminée")
    
except Exception as e:
    logger.error(f"Erreur lors de l'initialisation: {str(e)}")

# ========== ENDPOINTS ==========

@app.route('/api/customers/register', methods=['POST'])
@token_required
def register():
    """Endpoint d'inscription d'un nouveau client"""
    session = SessionLocal()
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
        existing_customer = session.query(CustomerModel).filter_by(email=data['email']).first()
        if existing_customer:
            return jsonify({'error': 'Email déjà utilisé'}), 400
        
        # Hasher le mot de passe
        password_hash = generate_password_hash(data['password'])
        
        # Créer le client
        customer_model = CustomerModel(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data['phone'],
            password_hash=password_hash,
            role=data.get('role', 'client'),
            store_id=data.get('store_id'),
            address=address,
            is_active=True
        )
        
        session.add(customer_model)
        session.commit()
        
        return jsonify({
            'message': 'Client créé avec succès',
            'customer': {
                'id': customer_model.id,
                'email': customer_model.email,
                'first_name': customer_model.first_name,
                'last_name': customer_model.last_name,
                'role': customer_model.role
            }
        }), 201
        
    except Exception as e:
        session.rollback()
        logger.error(f"Erreur lors de l'inscription: {str(e)}")
        return jsonify({'error': 'Erreur serveur'}), 500
    finally:
        session.close()

@app.route('/api/customers/login', methods=['POST'])
@token_required
def login():
    """Endpoint de connexion d'un client"""
    session = SessionLocal()
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email et mot de passe requis'}), 400
        
        # Rechercher le client
        customer = session.query(CustomerModel).filter_by(email=data['email']).first()
        
        if not customer or not check_password_hash(customer.password_hash, data['password']):
            return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
        
        if not customer.is_active:
            return jsonify({'error': 'Compte désactivé'}), 401
        
        # Génération du token JWT
        access_token = generate_jwt_token(customer.id, customer.email, customer.role)
        
        return jsonify({
            'message': 'Connexion réussie',
            'access_token': access_token,
            'role': customer.role,
            'customer': {
                'id': customer.id,
                'email': customer.email,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'role': customer.role,
                'store_id': customer.store_id
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la connexion: {str(e)}")
        return jsonify({'error': 'Erreur serveur'}), 500
    finally:
        session.close()

@app.route('/api/customers/<int:customer_id>', methods=['GET'])
@token_required
def get_customer(customer_id):
    """Récupérer un client par ID"""
    session = SessionLocal()
    try:
        customer = session.query(CustomerModel).filter_by(id=customer_id).first()
        
        if not customer:
            return jsonify({'error': 'Client non trouvé'}), 404
        
        return jsonify({
            'customer': {
                'id': customer.id,
                'email': customer.email,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'phone': customer.phone,
                'role': customer.role,
                'store_id': customer.store_id,
                'address': customer.address,
                'is_active': customer.is_active,
                'created_at': customer.created_at.isoformat(),
                'updated_at': customer.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du client: {str(e)}")
        return jsonify({'error': 'Erreur serveur'}), 500
    finally:
        session.close()

@app.route('/api/customers', methods=['GET'])
@token_required
def get_customers():
    """Récupérer tous les clients"""
    session = SessionLocal()
    try:
        customers = session.query(CustomerModel).all()
        
        return jsonify({
            'customers': [
                {
                    'id': customer.id,
                    'email': customer.email,
                    'first_name': customer.first_name,
                    'last_name': customer.last_name,
                    'role': customer.role,
                    'store_id': customer.store_id,
                    'is_active': customer.is_active
                }
                for customer in customers
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des clients: {str(e)}")
        return jsonify({'error': 'Erreur serveur'}), 500
    finally:
        session.close()

@app.route('/api/customers/role/<role>', methods=['GET'])
@token_required
def get_customers_by_role(role):
    """Récupérer les clients par rôle"""
    session = SessionLocal()
    try:
        customers = session.query(CustomerModel).filter_by(role=role).all()
        
        return jsonify({
            'customers': [
                {
                    'id': customer.id,
                    'email': customer.email,
                    'first_name': customer.first_name,
                    'last_name': customer.last_name,
                    'role': customer.role,
                    'store_id': customer.store_id,
                    'is_active': customer.is_active
                }
                for customer in customers
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des clients par rôle: {str(e)}")
        return jsonify({'error': 'Erreur serveur'}), 500
    finally:
        session.close()

@app.route('/health')
def health_check():
    return {"status": "healthy", "service": "customer-service"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
