from flask import Flask, request, jsonify
from functools import wraps
from typing import Dict, Any

from ...application.services.checkout_service import CheckoutService
from ...application.dto.checkout_dto import (
    CreateOrderRequest, UpdateOrderRequest, ProcessPaymentRequest,
    AddressRequest
)


class CheckoutController:
    def __init__(self, checkout_service: CheckoutService, api_token: str):
        self.checkout_service = checkout_service
        self.api_token = api_token
    
    def create_order(self):
        """Créer une nouvelle commande"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            required_fields = ['customer_id', 'items', 'shipping_address']
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"Missing required field: {field}"}), 400
            
            create_request = CreateOrderRequest(
                customer_id=data['customer_id'],
                items=data['items'],
                shipping_address=data['shipping_address'],
                billing_address=data.get('billing_address'),
                notes=data.get('notes')
            )
            
            order_response = self.checkout_service.create_order(create_request)
            
            return jsonify(order_response.__dict__), 201
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    
    def get_order(self, order_id: int):
        """Récupérer une commande par ID"""
        try:
            order_response = self.checkout_service.get_order(order_id)
            if not order_response:
                return jsonify({"error": "Order not found"}), 404
            
            return jsonify(order_response.__dict__), 200
            
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    
    def get_customer_orders(self, customer_id: int):
        """Récupérer toutes les commandes d'un client"""
        try:
            orders = self.checkout_service.get_orders_by_customer(customer_id)
            return jsonify([order.__dict__ for order in orders]), 200
            
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    
    def get_all_orders(self):
        """Récupérer toutes les commandes"""
        try:
            orders = self.checkout_service.get_all_orders()
            return jsonify([order.__dict__ for order in orders]), 200
            
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    
    def update_order(self, order_id: int):
        """Mettre à jour une commande"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            update_request = UpdateOrderRequest(
                order_id=order_id,
                items=data.get('items'),
                shipping_address=data.get('shipping_address'),
                billing_address=data.get('billing_address'),
                notes=data.get('notes')
            )
            
            order_response = self.checkout_service.update_order(update_request)
            if not order_response:
                return jsonify({"error": "Order not found"}), 404
            
            return jsonify(order_response.__dict__), 200
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    
    def confirm_order(self, order_id: int):
        """Confirmer une commande"""
        try:
            order_response = self.checkout_service.confirm_order(order_id)
            if not order_response:
                return jsonify({"error": "Order not found"}), 404
            
            return jsonify(order_response.__dict__), 200
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    
    def cancel_order(self, order_id: int):
        """Annuler une commande"""
        try:
            order_response = self.checkout_service.cancel_order(order_id)
            if not order_response:
                return jsonify({"error": "Order not found"}), 404
            
            return jsonify(order_response.__dict__), 200
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    
    def process_payment(self, order_id: int):
        """Traiter le paiement d'une commande"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            payment_request = ProcessPaymentRequest(
                order_id=order_id,
                payment_method=data.get('payment_method', 'credit_card'),
                payment_details=data.get('payment_details', {})
            )
            
            order_response = self.checkout_service.process_payment(payment_request)
            if not order_response:
                return jsonify({"error": "Order not found"}), 404
            
            return jsonify(order_response.__dict__), 200
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    
    def ship_order(self, order_id: int):
        """Expédier une commande"""
        try:
            order_response = self.checkout_service.ship_order(order_id)
            if not order_response:
                return jsonify({"error": "Order not found"}), 404
            
            return jsonify(order_response.__dict__), 200
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    
    def deliver_order(self, order_id: int):
        """Livrer une commande"""
        try:
            order_response = self.checkout_service.deliver_order(order_id)
            if not order_response:
                return jsonify({"error": "Order not found"}), 404
            
            return jsonify(order_response.__dict__), 200
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    
    def checkout_from_cart(self, customer_id: int):
        """Créer une commande à partir du panier"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            if 'shipping_address' not in data:
                return jsonify({"error": "Shipping address is required"}), 400
            
            order_response = self.checkout_service.checkout_from_cart(
                customer_id=customer_id,
                shipping_address=data['shipping_address'],
                billing_address=data.get('billing_address'),
                notes=data.get('notes')
            )
            
            return jsonify(order_response.__dict__), 201
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500


def create_checkout_controller(session_factory, cart_service_url: str, 
                             product_service_url: str, customer_service_url: str,
                             sales_service_url: str, api_token: str) -> CheckoutController:
    """Factory pour créer un contrôleur de checkout"""
    from ...infrastructure.repositories.sqlalchemy_order_repository import SQLAlchemyOrderRepository
    
    def get_session():
        return session_factory()
    
    def get_repository():
        return SQLAlchemyOrderRepository(get_session())
    
    checkout_service = CheckoutService(
        order_repository=get_repository(),
        cart_service_url=cart_service_url,
        product_service_url=product_service_url,
        customer_service_url=customer_service_url,
        sales_service_url=sales_service_url,
        api_token=api_token
    )
    
    return CheckoutController(checkout_service, api_token)
