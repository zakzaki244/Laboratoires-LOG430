from flask import Flask, request, jsonify
from sqlalchemy.orm import Session
from functools import wraps
import os
import redis

from ...application.services import CartService
from ...application.dto import CreateCartRequest, AddToCartRequest, UpdateCartItemRequest
from ...infrastructure.repositories import (
    CartRepository, ProductServiceAdapter, CustomerServiceAdapter, RedisCacheAdapter
)

class CartController:
    """Contrôleur pour les endpoints des paniers"""
    
    def __init__(self, cart_service: CartService):
        self.cart_service = cart_service
    
    def get_cart(self, cart_id: int):
        """Récupérer un panier par son ID"""
        try:
            cart = self.cart_service.get_cart_by_id(cart_id)
            if not cart:
                return jsonify({"error": "Panier non trouvé"}), 404
            return jsonify(cart.__dict__)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def get_active_cart(self, customer_id: int):
        """Récupérer le panier actif d'un client"""
        try:
            cart = self.cart_service.get_active_cart_by_customer(customer_id)
            if not cart:
                return jsonify({"error": "Panier non trouvé"}), 404
            return jsonify(cart.__dict__)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def create_cart(self):
        """Créer un nouveau panier"""
        try:
            data = request.json
            if not data or 'customer_id' not in data:
                return jsonify({"error": "ID client requis"}), 400
            
            create_request = CreateCartRequest(customer_id=data['customer_id'])
            cart = self.cart_service.create_cart(create_request)
            return jsonify(cart.__dict__), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def add_to_cart(self, customer_id: int):
        """Ajouter un article au panier"""
        try:
            data = request.json
            if not data or not all(key in data for key in ['product_id', 'quantity']):
                return jsonify({"error": "Données manquantes"}), 400
            
            add_request = AddToCartRequest(
                product_id=data['product_id'],
                quantity=data['quantity']
            )
            
            cart = self.cart_service.add_to_cart(customer_id, add_request)
            return jsonify(cart.__dict__)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def update_cart_item(self, customer_id: int):
        """Mettre à jour un article du panier"""
        try:
            data = request.json
            if not data or not all(key in data for key in ['product_id', 'quantity']):
                return jsonify({"error": "Données manquantes"}), 400
            
            update_request = UpdateCartItemRequest(
                product_id=data['product_id'],
                quantity=data['quantity']
            )
            
            cart = self.cart_service.update_cart_item(customer_id, update_request)
            return jsonify(cart.__dict__)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def remove_from_cart(self, customer_id: int, product_id: int):
        """Supprimer un article du panier"""
        try:
            cart = self.cart_service.remove_from_cart(customer_id, product_id)
            return jsonify(cart.__dict__)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def clear_cart(self, customer_id: int):
        """Vider le panier"""
        try:
            cart = self.cart_service.clear_cart(customer_id)
            return jsonify(cart.__dict__)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

def create_cart_controller(session_factory, 
                          product_service_url: str, 
                          customer_service_url: str,
                          redis_client: redis.Redis,
                          api_token: str) -> CartController:
    """Factory pour créer le contrôleur des paniers"""
    def get_session():
        return session_factory()
    
    cart_repository = CartRepository(get_session())
    product_service_adapter = ProductServiceAdapter(product_service_url, api_token)
    customer_service_adapter = CustomerServiceAdapter(customer_service_url, api_token)
    cache_adapter = RedisCacheAdapter(redis_client)
    
    cart_service = CartService(
        cart_repository, 
        product_service_adapter, 
        customer_service_adapter,
        cache_adapter
    )
    
    return CartController(cart_service)
