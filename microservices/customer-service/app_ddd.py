from flask import Flask, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics
from werkzeug.security import generate_password_hash, check_password_hash
from src.infrastructure.repositories.customer_repository_simple import CustomerRepositorySimple
import os

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Création du repository simple
customer_repository = CustomerRepositorySimple()

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
