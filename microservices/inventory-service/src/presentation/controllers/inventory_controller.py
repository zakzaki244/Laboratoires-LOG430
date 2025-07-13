from flask import Flask, request, jsonify
from functools import wraps
from typing import Dict, Any

from ...application.services.inventory_service import InventoryService
from ...application.dto.inventory_dto import (
    CreateReapproRequest, UpdateReapproRequest, ProcessReapproRequest
)


class InventoryController:
    def __init__(self, inventory_service: InventoryService, api_token: str):
        self.inventory_service = inventory_service
        self.api_token = api_token
    
    def create_reappro_request(self):
        """Créer une nouvelle demande de réapprovisionnement"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            required_fields = ['store_id', 'product_id', 'quantity']
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"Missing required field: {field}"}), 400
            
            # Créer la requête
            create_request = CreateReapproRequest(
                store_id=data['store_id'],
                product_id=data['product_id'],
                quantity=data['quantity'],
                notes=data.get('notes')
            )
            
            # Créer la demande
            response = self.inventory_service.create_reappro_request(create_request)
            
            return jsonify(response.__dict__), 201
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    
    def get_reappro_request(self, request_id: int):
        """Récupérer une demande de réapprovisionnement par ID"""
        try:
            response = self.inventory_service.get_reappro_request(request_id)
            if not response:
                return jsonify({"error": "Request not found"}), 404
            
            return jsonify(response.__dict__), 200
            
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    
    def get_all_reappro_requests(self):
        """Récupérer toutes les demandes de réapprovisionnement"""
        try:
            responses = self.inventory_service.get_all_reappro_requests()
            return jsonify([response.__dict__ for response in responses]), 200
            
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    
    def get_reappro_requests_by_store(self, store_id: int):
        """Récupérer toutes les demandes d'un magasin"""
        try:
            responses = self.inventory_service.get_reappro_requests_by_store(store_id)
            return jsonify([response.__dict__ for response in responses]), 200
            
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    
    def get_reappro_requests_by_product(self, product_id: int):
        """Récupérer toutes les demandes pour un produit"""
        try:
            responses = self.inventory_service.get_reappro_requests_by_product(product_id)
            return jsonify([response.__dict__ for response in responses]), 200
            
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    
    def get_pending_reappro_requests(self):
        """Récupérer toutes les demandes en attente"""
        try:
            responses = self.inventory_service.get_pending_reappro_requests()
            return jsonify([response.__dict__ for response in responses]), 200
            
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    
    def get_reappro_requests_by_status(self, status: str):
        """Récupérer toutes les demandes avec un statut donné"""
        try:
            responses = self.inventory_service.get_reappro_requests_by_status(status)
            return jsonify([response.__dict__ for response in responses]), 200
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    
    def update_reappro_request(self, request_id: int):
        """Mettre à jour une demande de réapprovisionnement"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            update_request = UpdateReapproRequest(
                request_id=request_id,
                quantity=data.get('quantity'),
                notes=data.get('notes')
            )
            
            response = self.inventory_service.update_reappro_request(update_request)
            if not response:
                return jsonify({"error": "Request not found"}), 404
            
            return jsonify(response.__dict__), 200
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    
    def process_reappro_request(self, request_id: int):
        """Traiter une demande de réapprovisionnement (approuver ou rejeter)"""
        try:
            data = request.get_json()
            if not data or 'action' not in data:
                return jsonify({"error": "Action required (approve/reject)"}), 400
            
            if data['action'] not in ['approve', 'reject']:
                return jsonify({"error": "Invalid action. Use 'approve' or 'reject'"}), 400
            
            process_request = ProcessReapproRequest(
                request_id=request_id,
                action=data['action'],
                notes=data.get('notes')
            )
            
            response = self.inventory_service.process_reappro_request(process_request)
            if not response:
                return jsonify({"error": "Request not found"}), 404
            
            return jsonify(response.__dict__), 200
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    
    def complete_reappro_request(self, request_id: int):
        """Marquer une demande comme terminée"""
        try:
            response = self.inventory_service.complete_reappro_request(request_id)
            if not response:
                return jsonify({"error": "Request not found"}), 404
            
            return jsonify(response.__dict__), 200
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    
    def delete_reappro_request(self, request_id: int):
        """Supprimer une demande de réapprovisionnement"""
        try:
            success = self.inventory_service.delete_reappro_request(request_id)
            if not success:
                return jsonify({"error": "Request not found"}), 404
            
            return jsonify({"message": "Request deleted successfully"}), 200
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    
    def get_reappro_stats(self):
        """Récupérer les statistiques des demandes de réapprovisionnement"""
        try:
            stats = self.inventory_service.get_reappro_stats()
            return jsonify(stats.__dict__), 200
            
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500


def create_inventory_controller(session_factory, product_service_url: str, 
                              store_service_url: str, api_token: str) -> InventoryController:
    """Factory pour créer un contrôleur d'inventaire"""
    from ...infrastructure.repositories.sqlalchemy_reappro_request_repository import SQLAlchemyReapproRequestRepository
    
    def get_session():
        return session_factory()
    
    def get_repository():
        return SQLAlchemyReapproRequestRepository(get_session())
    
    inventory_service = InventoryService(
        reappro_repository=get_repository(),
        product_service_url=product_service_url,
        store_service_url=store_service_url,
        api_token=api_token
    )
    
    return InventoryController(inventory_service, api_token)
