from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List
import threading
import time

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
EVENT_STORE_URL = os.getenv('EVENT_STORE_URL', 'http://event-bus-service:5000')
DEFAULT_RESTOCK_QUANTITY = int(os.getenv('DEFAULT_RESTOCK_QUANTITY', '50'))
AUTO_APPROVAL_THRESHOLD = int(os.getenv('AUTO_APPROVAL_THRESHOLD', '100'))

# État en mémoire pour les demandes de réapprovisionnement
restock_requests = {}
supplier_mappings = {
    '1': 'supplier_electronics',
    '2': 'supplier_clothing', 
    '3': 'supplier_books',
    '4': 'supplier_home',
    '5': 'supplier_sports',
    'default': 'supplier_general'
}

class ProcurementEventService:
    """Service de gestion des approvisionnements basé sur les événements"""
    
    def __init__(self):
        self.event_store_url = EVENT_STORE_URL
        self.running = False
        self.event_listener_thread = None
    
    def publish_event(self, event_type: str, aggregate_id: str, 
                     aggregate_type: str, data: Dict[str, Any]) -> bool:
        """Publie un événement vers l'Event Store"""
        try:
            event_data = {
                'event_type': event_type,
                'aggregate_id': aggregate_id,
                'aggregate_type': aggregate_type,
                'data': data
            }
            
            response = requests.post(
                f"{self.event_store_url}/api/events",
                json=event_data,
                timeout=10
            )
            
            if response.status_code == 201:
                logger.info(f"Published {event_type} event for {aggregate_id}")
                return True
            else:
                logger.error(f"Failed to publish event: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            return False
    
    def handle_low_stock_detected(self, event_data: Dict[str, Any]):
        """Gère l'événement LowStockDetected"""
        try:
            product_id = event_data['product_id']
            current_stock = event_data['current_stock']
            minimum_threshold = event_data['minimum_threshold']
            
            # Calculer la quantité à commander
            shortage = minimum_threshold - current_stock
            restock_quantity = max(DEFAULT_RESTOCK_QUANTITY, shortage * 2)
            
            # Déterminer le fournisseur
            supplier_id = supplier_mappings.get(product_id, supplier_mappings['default'])
            
            # Créer une demande de réapprovisionnement
            restock_request_id = f"restock_{product_id}_{uuid.uuid4().hex[:8]}"
            
            request_data = {
                'restock_request_id': restock_request_id,
                'product_id': product_id,
                'requested_quantity': restock_quantity,
                'supplier_id': supplier_id,
                'priority': 'high' if current_stock == 0 else 'normal',
                'reason': 'low_stock_detected',
                'current_stock': current_stock,
                'minimum_threshold': minimum_threshold,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Stocker la demande
            restock_requests[restock_request_id] = request_data
            
            # Publier l'événement RestockRequested
            success = self.publish_event(
                event_type='RestockRequested',
                aggregate_id=restock_request_id,
                aggregate_type='RestockRequest',
                data=request_data
            )
            
            if success:
                logger.info(f"Created restock request {restock_request_id} for product {product_id}")
                
                # Auto-approbation pour les petites quantités
                if restock_quantity <= AUTO_APPROVAL_THRESHOLD:
                    self.auto_approve_restock(restock_request_id, "system_auto_approval")
            
        except Exception as e:
            logger.error(f"Error handling LowStockDetected event: {e}")
    
    def auto_approve_restock(self, restock_request_id: str, approved_by: str):
        """Approuve automatiquement une demande de réapprovisionnement"""
        try:
            request_data = restock_requests.get(restock_request_id)
            if not request_data:
                logger.error(f"Restock request {restock_request_id} not found")
                return
            
            # Mettre à jour le statut
            request_data['status'] = 'approved'
            request_data['approved_by'] = approved_by
            request_data['approved_at'] = datetime.now(timezone.utc).isoformat()
            
            # Publier l'événement RestockApproved
            approval_data = {
                'restock_request_id': restock_request_id,
                'product_id': request_data['product_id'],
                'approved_quantity': request_data['requested_quantity'],
                'supplier_id': request_data['supplier_id'],
                'approved_by': approved_by,
                'approval_type': 'automatic',
                'approved_at': request_data['approved_at']
            }
            
            self.publish_event(
                event_type='RestockApproved',
                aggregate_id=restock_request_id,
                aggregate_type='RestockRequest',
                data=approval_data
            )
            
            logger.info(f"Auto-approved restock request {restock_request_id}")
            
        except Exception as e:
            logger.error(f"Error auto-approving restock request: {e}")
    
    def manual_approve_restock(self, restock_request_id: str, approved_by: str, 
                              approved_quantity: int = None) -> bool:
        """Approuve manuellement une demande de réapprovisionnement"""
        try:
            request_data = restock_requests.get(restock_request_id)
            if not request_data:
                return False
            
            # Utiliser la quantité demandée si pas spécifiée
            if approved_quantity is None:
                approved_quantity = request_data['requested_quantity']
            
            # Mettre à jour le statut
            request_data['status'] = 'approved'
            request_data['approved_by'] = approved_by
            request_data['approved_quantity'] = approved_quantity
            request_data['approved_at'] = datetime.now(timezone.utc).isoformat()
            
            # Publier l'événement RestockApproved
            approval_data = {
                'restock_request_id': restock_request_id,
                'product_id': request_data['product_id'],
                'approved_quantity': approved_quantity,
                'supplier_id': request_data['supplier_id'],
                'approved_by': approved_by,
                'approval_type': 'manual',
                'approved_at': request_data['approved_at']
            }
            
            success = self.publish_event(
                event_type='RestockApproved',
                aggregate_id=restock_request_id,
                aggregate_type='RestockRequest',
                data=approval_data
            )
            
            if success:
                logger.info(f"Manually approved restock request {restock_request_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error manually approving restock request: {e}")
            return False
    
    def start_event_listening(self):
        """Démarre l'écoute des événements (simulation)"""
        self.running = True
        self.event_listener_thread = threading.Thread(target=self._event_listener_worker)
        self.event_listener_thread.daemon = True
        self.event_listener_thread.start()
        logger.info("Started event listening for Procurement Service")
    
    def stop_event_listening(self):
        """Arrête l'écoute des événements"""
        self.running = False
        if self.event_listener_thread:
            self.event_listener_thread.join(timeout=5)
        logger.info("Stopped event listening for Procurement Service")
    
    def _event_listener_worker(self):
        """Worker pour écouter les événements (simulation polling)"""
        last_check = datetime.now(timezone.utc)
        
        while self.running:
            try:
                # Récupérer les nouveaux événements LowStockDetected
                response = requests.get(
                    f"{self.event_store_url}/api/events/types/LowStockDetected",
                    params={'limit': 10},
                    timeout=5
                )
                
                if response.status_code == 200:
                    events_data = response.json()
                    events = events_data.get('events', [])
                    
                    for event in events:
                        event_timestamp = datetime.fromisoformat(
                            event['timestamp'].replace('Z', '+00:00')
                        )
                        
                        # Traiter seulement les nouveaux événements
                        if event_timestamp > last_check:
                            self.handle_low_stock_detected(event['data'])
                    
                    if events:
                        last_check = datetime.now(timezone.utc)
                
                time.sleep(30)  # Vérifier toutes les 30 secondes
                
            except Exception as e:
                logger.error(f"Error in event listener: {e}")
                time.sleep(60)  # Attendre plus longtemps en cas d'erreur

# Instance du service
procurement_service = ProcurementEventService()

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de santé"""
    return jsonify({
        'status': 'healthy',
        'service': 'procurement-service',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'restock_requests_count': len(restock_requests),
        'event_listening': procurement_service.running
    }), 200

@app.route('/api/restock/requests', methods=['GET'])
def get_restock_requests():
    """Obtenir toutes les demandes de réapprovisionnement"""
    try:
        status_filter = request.args.get('status')
        
        filtered_requests = []
        for request_id, request_data in restock_requests.items():
            if not status_filter or request_data.get('status') == status_filter:
                filtered_requests.append({
                    'request_id': request_id,
                    **request_data
                })
        
        return jsonify({
            'restock_requests': filtered_requests,
            'total_count': len(filtered_requests)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting restock requests: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/restock/requests/<request_id>', methods=['GET'])
def get_restock_request(request_id: str):
    """Obtenir une demande de réapprovisionnement spécifique"""
    try:
        request_data = restock_requests.get(request_id)
        if not request_data:
            return jsonify({'error': 'Restock request not found'}), 404
        
        return jsonify({
            'request_id': request_id,
            **request_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting restock request: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/restock/requests/<request_id>/approve', methods=['POST'])
def approve_restock_request(request_id: str):
    """Approuver une demande de réapprovisionnement"""
    try:
        data = request.get_json()
        approved_by = data.get('approved_by', 'unknown_user')
        approved_quantity = data.get('approved_quantity')
        
        success = procurement_service.manual_approve_restock(
            restock_request_id=request_id,
            approved_by=approved_by,
            approved_quantity=approved_quantity
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Restock request approved',
                'request_id': request_id
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to approve restock request'
            }), 400
            
    except Exception as e:
        logger.error(f"Error approving restock request: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/restock/requests/create', methods=['POST'])
def create_manual_restock_request():
    """Créer manuellement une demande de réapprovisionnement"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validation
        required_fields = ['product_id', 'requested_quantity', 'supplier_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        product_id = data['product_id']
        requested_quantity = int(data['requested_quantity'])
        supplier_id = data['supplier_id']
        priority = data.get('priority', 'normal')
        reason = data.get('reason', 'manual_request')
        
        # Créer la demande
        restock_request_id = f"restock_{product_id}_{uuid.uuid4().hex[:8]}"
        
        request_data = {
            'restock_request_id': restock_request_id,
            'product_id': product_id,
            'requested_quantity': requested_quantity,
            'supplier_id': supplier_id,
            'priority': priority,
            'reason': reason,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'status': 'pending'
        }
        
        # Stocker la demande
        restock_requests[restock_request_id] = request_data
        
        # Publier l'événement
        success = procurement_service.publish_event(
            event_type='RestockRequested',
            aggregate_id=restock_request_id,
            aggregate_type='RestockRequest',
            data=request_data
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Restock request created',
                'request_id': restock_request_id,
                'request_data': request_data
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create restock request'
            }), 500
            
    except Exception as e:
        logger.error(f"Error creating manual restock request: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/events/start-listening', methods=['POST'])
def start_event_listening():
    """Démarrer l'écoute des événements"""
    try:
        if not procurement_service.running:
            procurement_service.start_event_listening()
            return jsonify({
                'success': True,
                'message': 'Event listening started'
            }), 200
        else:
            return jsonify({
                'success': True,
                'message': 'Event listening already running'
            }), 200
            
    except Exception as e:
        logger.error(f"Error starting event listening: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/events/stop-listening', methods=['POST'])
def stop_event_listening():
    """Arrêter l'écoute des événements"""
    try:
        procurement_service.stop_event_listening()
        return jsonify({
            'success': True,
            'message': 'Event listening stopped'
        }), 200
        
    except Exception as e:
        logger.error(f"Error stopping event listening: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/suppliers', methods=['GET'])
def get_suppliers():
    """Obtenir la liste des fournisseurs"""
    try:
        suppliers = []
        for product_id, supplier_id in supplier_mappings.items():
            if product_id != 'default':
                suppliers.append({
                    'product_id': product_id,
                    'supplier_id': supplier_id
                })
        
        return jsonify({
            'suppliers': suppliers,
            'default_supplier': supplier_mappings['default']
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting suppliers: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

if __name__ == '__main__':
    # Démarrer l'écoute des événements au lancement
    procurement_service.start_event_listening()
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
        # Arrêter l'écoute lors de l'arrêt
        procurement_service.stop_event_listening()
