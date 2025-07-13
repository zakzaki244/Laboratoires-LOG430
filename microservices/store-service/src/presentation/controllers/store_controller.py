from flask import Flask, request, jsonify
from sqlalchemy.orm import Session
from functools import wraps
import os

from ...application.services import StoreService
from ...application.dto import CreateStoreRequest, UpdateStoreRequest
from ...infrastructure.repositories import StoreRepository

class StoreController:
    """Contrôleur pour les endpoints des magasins"""
    
    def __init__(self, store_service: StoreService):
        self.store_service = store_service
    
    def get_stores(self):
        """Récupérer tous les magasins"""
        try:
            stores = self.store_service.get_all_stores()
            return jsonify([store.__dict__ for store in stores])
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def get_store(self, store_id: int):
        """Récupérer un magasin spécifique"""
        try:
            store = self.store_service.get_store_by_id(store_id)
            if not store:
                return jsonify({"error": "Magasin non trouvé"}), 404
            return jsonify(store.__dict__)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def create_store(self):
        """Créer un nouveau magasin"""
        try:
            data = request.json
            if not data or 'name' not in data:
                return jsonify({"error": "Nom du magasin requis"}), 400
            
            create_request = CreateStoreRequest(
                name=data['name'],
                address=data.get('address'),
                phone=data.get('phone')
            )
            
            store = self.store_service.create_store(create_request)
            return jsonify(store.__dict__), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def update_store(self, store_id: int):
        """Mettre à jour un magasin"""
        try:
            data = request.json
            if not data:
                return jsonify({"error": "Données manquantes"}), 400
            
            update_request = UpdateStoreRequest(
                name=data.get('name'),
                address=data.get('address'),
                phone=data.get('phone')
            )
            
            store = self.store_service.update_store(store_id, update_request)
            if not store:
                return jsonify({"error": "Magasin non trouvé"}), 404
            return jsonify(store.__dict__)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def delete_store(self, store_id: int):
        """Supprimer un magasin"""
        try:
            success = self.store_service.delete_store(store_id)
            if not success:
                return jsonify({"error": "Magasin non trouvé"}), 404
            return jsonify({"message": "Magasin supprimé avec succès"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

def create_store_controller(session_factory) -> StoreController:
    """Factory pour créer le contrôleur des magasins"""
    def get_session():
        return session_factory()
    
    store_repository = StoreRepository(get_session())
    store_service = StoreService(store_repository)
    
    return StoreController(store_service)
