from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from src.application.services.customer_service import CustomerService
from src.infrastructure.repositories.customer_repository_simple import SqlCustomerRepository
import logging

logger = logging.getLogger(__name__)

customer_bp = Blueprint('customer', __name__)


def create_customer_controller(session_factory):
    """Factory pour créer le contrôleur customer avec les dépendances"""
    repository = SqlCustomerRepository(session_factory)
    service = CustomerService(repository)
    
    @customer_bp.route('/api/customers/register', methods=['POST'])
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
            existing_customer = service.get_customer_by_email(data['email'])
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
            
            customer = service.create_customer(customer_data)
            
            return jsonify({
                'message': 'Client créé avec succès',
                'customer': {
                    'id': customer.id,
                    'email': customer.email,
                    'first_name': customer.first_name,
                    'last_name': customer.last_name,
                    'phone': customer.phone,
                    'address': customer.address,
                    'is_active': customer.is_active
                }
            }), 201
            
        except Exception as e:
            logger.error(f"Erreur lors de l'inscription: {str(e)}")
            return jsonify({'error': 'Erreur interne du serveur'}), 500
    
    @customer_bp.route('/api/customers/login', methods=['POST'])
    def login():
        """Endpoint de connexion d'un client"""
        try:
            data = request.get_json()
            
            # Validation des données requises
            if not data or 'email' not in data or 'password' not in data:
                return jsonify({'error': 'Email et mot de passe requis'}), 400
            
            # Récupérer le client
            customer = service.get_customer_by_email(data['email'])
            if not customer:
                return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
            
            # Vérifier le mot de passe
            if not check_password_hash(customer.password_hash, data['password']):
                return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
            
            # Vérifier si le compte est actif
            if not customer.is_active:
                return jsonify({'error': 'Compte désactivé'}), 401
            
            return jsonify({
                'message': 'Connexion réussie',
                'customer': {
                    'id': customer.id,
                    'email': customer.email,
                    'first_name': customer.first_name,
                    'last_name': customer.last_name,
                    'phone': customer.phone,
                    'address': customer.address,
                    'is_active': customer.is_active
                }
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la connexion: {str(e)}")
            return jsonify({'error': 'Erreur interne du serveur'}), 500
    
    @customer_bp.route('/api/customers/health', methods=['GET'])
    def health():
        """Endpoint de santé du service"""
        return jsonify({'status': 'healthy', 'service': 'customer-service'}), 200
    
    @customer_bp.route('/api/customers/<int:customer_id>', methods=['GET'])
    def get_customer(customer_id):
        """Endpoint pour récupérer un client par ID"""
        try:
            customer = service.get_customer_by_id(customer_id)
            if not customer:
                return jsonify({'error': 'Client non trouvé'}), 404
            
            return jsonify({
                'customer': {
                    'id': customer.id,
                    'email': customer.email,
                    'first_name': customer.first_name,
                    'last_name': customer.last_name,
                    'phone': customer.phone,
                    'address': customer.address,
                    'is_active': customer.is_active
                }
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du client: {str(e)}")
            return jsonify({'error': 'Erreur interne du serveur'}), 500
    
    return customer_bp
