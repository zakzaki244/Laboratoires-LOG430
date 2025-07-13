from flask import Blueprint, request, jsonify
from typing import Optional
import asyncio

from ...application.services.customer_service import CustomerService
from ...application.dto.customer_dto import (
    CustomerRegistrationDTO, CustomerLoginDTO, CustomerUpdateDTO, PasswordChangeDTO
)


def create_customer_controller(customer_service: CustomerService) -> Blueprint:
    """Factory pour créer le contrôleur Customer"""
    
    customer_bp = Blueprint('customer', __name__)
    
    @customer_bp.route('/api/customers/register', methods=['POST'])
    def register_customer():
        """Inscrire un nouveau client"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'Données JSON requises'}), 400
            
            required_fields = ['email', 'first_name', 'last_name', 'phone', 'password', 'address']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({
                    'error': f'Champs manquants: {", ".join(missing_fields)}'
                }), 400
            
            address = data['address']
            required_address_fields = ['street', 'city', 'postal_code', 'country']
            missing_address_fields = [field for field in required_address_fields if field not in address]
            if missing_address_fields:
                return jsonify({
                    'error': f'Champs manquants dans l\'adresse: {", ".join(missing_address_fields)}'
                }), 400
            
            registration_dto = CustomerRegistrationDTO(
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone=data['phone'],
                password=data['password'],
                address=address
            )
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                customer_response = loop.run_until_complete(
                    customer_service.register_customer(registration_dto)
                )
                return jsonify(customer_response.__dict__), 201
            finally:
                loop.close()
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': f'Erreur interne: {str(e)}'}), 500
    
    @customer_bp.route('/api/customers/login', methods=['POST'])
    def login_customer():
        """Connecter un client"""
        try:
            data = request.get_json()
            
            if not data or 'email' not in data or 'password' not in data:
                return jsonify({'error': 'Email et mot de passe requis'}), 400
            
            login_dto = CustomerLoginDTO(
                email=data['email'],
                password=data['password']
            )
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                customer_response = loop.run_until_complete(
                    customer_service.login_customer(login_dto)
                )
                return jsonify(customer_response.__dict__), 200
            finally:
                loop.close()
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 401
        except Exception as e:
            return jsonify({'error': f'Erreur interne: {str(e)}'}), 500
    
    @customer_bp.route('/api/customers/<customer_id>', methods=['GET'])
    def get_customer(customer_id: str):
        """Récupérer un client par ID"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                customer = loop.run_until_complete(
                    customer_service.get_customer(customer_id)
                )
                
                if not customer:
                    return jsonify({'error': 'Client non trouvé'}), 404
                
                return jsonify(customer.__dict__), 200
            finally:
                loop.close()
            
        except Exception as e:
            return jsonify({'error': f'Erreur interne: {str(e)}'}), 500
    
    @customer_bp.route('/api/customers/<customer_id>', methods=['PUT'])
    def update_customer(customer_id: str):
        """Mettre à jour un client"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'Données JSON requises'}), 400
            
            update_dto = CustomerUpdateDTO(
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                phone=data.get('phone'),
                address=data.get('address')
            )
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                customer_response = loop.run_until_complete(
                    customer_service.update_customer(customer_id, update_dto)
                )
                return jsonify(customer_response.__dict__), 200
            finally:
                loop.close()
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': f'Erreur interne: {str(e)}'}), 500
    
    @customer_bp.route('/api/customers/<customer_id>/change-password', methods=['PUT'])
    def change_password(customer_id: str):
        """Changer le mot de passe d'un client"""
        try:
            data = request.get_json()
            
            if not data or 'current_password' not in data or 'new_password' not in data:
                return jsonify({'error': 'Mot de passe actuel et nouveau mot de passe requis'}), 400
            
            password_dto = PasswordChangeDTO(
                current_password=data['current_password'],
                new_password=data['new_password']
            )
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                customer_response = loop.run_until_complete(
                    customer_service.change_password(customer_id, password_dto)
                )
                return jsonify(customer_response.__dict__), 200
            finally:
                loop.close()
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': f'Erreur interne: {str(e)}'}), 500
    
    @customer_bp.route('/api/customers/<customer_id>/deactivate', methods=['PUT'])
    def deactivate_customer(customer_id: str):
        """Désactiver un client"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                customer_response = loop.run_until_complete(
                    customer_service.deactivate_customer(customer_id)
                )
                return jsonify(customer_response.__dict__), 200
            finally:
                loop.close()
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': f'Erreur interne: {str(e)}'}), 500
    
    @customer_bp.route('/api/customers', methods=['GET'])
    def get_all_customers():
        """Récupérer tous les clients actifs"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                customers = loop.run_until_complete(
                    customer_service.get_all_active_customers()
                )
                
                return jsonify({
                    'customers': [customer.__dict__ for customer in customers],
                    'total': len(customers)
                }), 200
            finally:
                loop.close()
            
        except Exception as e:
            return jsonify({'error': f'Erreur interne: {str(e)}'}), 500
    
    @customer_bp.route('/api/customers/health', methods=['GET'])
    def health_check():
        """Vérification de l'état du service"""
        return jsonify({
            'status': 'healthy',
            'service': 'customer-service',
            'version': '1.0.0'
        }), 200
    
    return customer_bp


class CustomerController:
    """Contrôleur principal pour le service Customer"""
    
    def __init__(self, customer_service: CustomerService):
        self.customer_service = customer_service
        self.blueprint = create_customer_controller(customer_service)
    
    def get_blueprint(self) -> Blueprint:
        """Retourner le Blueprint Flask"""
        return self.blueprint
