from flask import Flask, request, jsonify
from sqlalchemy.orm import Session
from functools import wraps
import os

from ...application.services import ProductService
from ...application.dto import CreateProductRequest, UpdateProductRequest, UpdateStockRequest
from ...infrastructure.repositories import ProductRepository, StoreServiceAdapter

class ProductController:
    """Contrôleur pour les endpoints des produits"""
    
    def __init__(self, product_service: ProductService):
        self.product_service = product_service
    
    def get_products(self):
        """Récupérer tous les produits"""
        try:
            products = self.product_service.get_all_products()
            return jsonify([product.__dict__ for product in products])
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def get_product(self, product_id: int):
        """Récupérer un produit spécifique"""
        try:
            product = self.product_service.get_product_by_id(product_id)
            if not product:
                return jsonify({"error": "Produit non trouvé"}), 404
            return jsonify(product.__dict__)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def search_products(self):
        """Rechercher des produits"""
        try:
            term = request.args.get('q', '')
            products = self.product_service.search_products(term)
            return jsonify([product.__dict__ for product in products])
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def create_product(self):
        """Créer un nouveau produit"""
        try:
            data = request.json
            if not data or not all(key in data for key in ['name', 'category', 'price', 'store_id']):
                return jsonify({"error": "Données manquantes"}), 400
            
            create_request = CreateProductRequest(
                name=data['name'],
                category=data['category'],
                price=data['price'],
                store_id=data['store_id'],
                stock=data.get('stock', 0),
                currency=data.get('currency', 'CAD')
            )
            
            product = self.product_service.create_product(create_request)
            return jsonify(product.__dict__), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def update_product(self, product_id: int):
        """Mettre à jour un produit"""
        try:
            data = request.json
            if not data:
                return jsonify({"error": "Données manquantes"}), 400
            
            update_request = UpdateProductRequest(
                name=data.get('name'),
                category=data.get('category'),
                price=data.get('price'),
                stock=data.get('stock'),
                store_id=data.get('store_id'),
                currency=data.get('currency')
            )
            
            product = self.product_service.update_product(product_id, update_request)
            if not product:
                return jsonify({"error": "Produit non trouvé"}), 404
            return jsonify(product.__dict__)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def delete_product(self, product_id: int):
        """Supprimer un produit"""
        try:
            success = self.product_service.delete_product(product_id)
            if not success:
                return jsonify({"error": "Produit non trouvé"}), 404
            return jsonify({"message": "Produit supprimé avec succès"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def update_stock(self, product_id: int):
        """Mettre à jour le stock d'un produit"""
        try:
            data = request.json
            if not data or 'quantity' not in data:
                return jsonify({"error": "Quantité requise"}), 400
            
            stock_request = UpdateStockRequest(quantity=data['quantity'])
            product = self.product_service.update_stock(product_id, stock_request)
            if not product:
                return jsonify({"error": "Produit non trouvé"}), 404
            return jsonify(product.__dict__)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

def create_product_controller(session_factory, store_service_url: str, api_token: str) -> ProductController:
    """Factory pour créer le contrôleur des produits"""
    def get_session():
        return session_factory()
    
    product_repository = ProductRepository(get_session())
    store_service_adapter = StoreServiceAdapter(store_service_url, api_token)
    product_service = ProductService(product_repository, store_service_adapter)
    
    return ProductController(product_service)
