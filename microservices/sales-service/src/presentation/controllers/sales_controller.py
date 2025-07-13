from flask import Flask, request, jsonify
from sqlalchemy.orm import Session
from functools import wraps
from typing import List
import os

from ...application.services import SalesService
from ...application.dto import CreateSaleRequest, UpdateSaleRequest, SaleItemRequest
from ...infrastructure.repositories import SaleRepository, ProductServiceAdapter

class SalesController:
    """Contrôleur pour les endpoints des ventes"""
    
    def __init__(self, sales_service: SalesService):
        self.sales_service = sales_service
    
    def get_sales(self):
        """Récupérer toutes les ventes"""
        try:
            sales = self.sales_service.get_all_sales()
            return jsonify([sale.__dict__ for sale in sales])
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def get_sale(self, sale_id: int):
        """Récupérer une vente spécifique"""
        try:
            sale = self.sales_service.get_sale_by_id(sale_id)
            if not sale:
                return jsonify({"error": "Vente non trouvée"}), 404
            return jsonify(sale.__dict__)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def get_sales_by_store(self, store_id: int):
        """Récupérer les ventes d'un magasin"""
        try:
            sales = self.sales_service.get_sales_by_store(store_id)
            return jsonify([sale.__dict__ for sale in sales])
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def create_sale(self):
        """Créer une nouvelle vente"""
        try:
            data = request.json
            if not data or not all(key in data for key in ['store_id', 'items']):
                return jsonify({"error": "Données manquantes"}), 400
            
            items = []
            for item_data in data['items']:
                if not all(key in item_data for key in ['product_id', 'quantity']):
                    return jsonify({"error": "Données d'article manquantes"}), 400
                
                item = SaleItemRequest(
                    product_id=item_data['product_id'],
                    quantity=item_data['quantity'],
                    unit_price=item_data.get('unit_price', 0.0)
                )
                items.append(item)
            
            create_request = CreateSaleRequest(
                store_id=data['store_id'],
                items=items
            )
            
            sale = self.sales_service.create_sale(create_request)
            return jsonify(sale.__dict__), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def update_sale(self, sale_id: int):
        """Mettre à jour une vente"""
        try:
            data = request.json
            if not data:
                return jsonify({"error": "Données manquantes"}), 400
            
            items = None
            if 'items' in data:
                items = []
                for item_data in data['items']:
                    if not all(key in item_data for key in ['product_id', 'quantity']):
                        return jsonify({"error": "Données d'article manquantes"}), 400
                    
                    item = SaleItemRequest(
                        product_id=item_data['product_id'],
                        quantity=item_data['quantity'],
                        unit_price=item_data.get('unit_price', 0.0)
                    )
                    items.append(item)
            
            update_request = UpdateSaleRequest(items=items)
            
            sale = self.sales_service.update_sale(sale_id, update_request)
            if not sale:
                return jsonify({"error": "Vente non trouvée"}), 404
            return jsonify(sale.__dict__)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def delete_sale(self, sale_id: int):
        """Supprimer une vente"""
        try:
            success = self.sales_service.delete_sale(sale_id)
            if not success:
                return jsonify({"error": "Vente non trouvée"}), 404
            return jsonify({"message": "Vente supprimée avec succès"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

def create_sales_controller(session_factory, product_service_url: str, api_token: str) -> SalesController:
    """Factory pour créer le contrôleur des ventes"""
    def get_session():
        return session_factory()
    
    sale_repository = SaleRepository(get_session())
    product_service_adapter = ProductServiceAdapter(product_service_url, api_token)
    sales_service = SalesService(sale_repository, product_service_adapter)
    
    return SalesController(sales_service)
