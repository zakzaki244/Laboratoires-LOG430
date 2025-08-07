from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging
import os
import uuid
import threading
import time
import random
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
EVENT_STORE_URL = os.getenv('EVENT_STORE_URL', 'http://event-bus-service:5000')
INVENTORY_SERVICE_URL = os.getenv('INVENTORY_SERVICE_URL', 'http://inventory-event-service:5000')
MIN_DELIVERY_DAYS = int(os.getenv('MIN_DELIVERY_DAYS', '1'))
MAX_DELIVERY_DAYS = int(os.getenv('MAX_DELIVERY_DAYS', '7'))

# État en mémoire pour les livraisons
pending_deliveries = {}
delivery_history = {}

# Catalogue des fournisseurs
suppliers_catalog = {
    'supplier_electronics': {
        'name': 'ElectroSupply Co.',
        'specialties': ['electronics', 'gadgets'],
        'reliability': 0.95,
        'delivery_speed': 'fast'
    },
    'supplier_clothing': {
        'name': 'Fashion Wholesale Ltd.',
        'specialties': ['clothing', 'accessories'],
        'reliability': 0.88,
        'delivery_speed': 'medium'
    },
    'supplier_books': {
        'name': 'Academic Books Supply',
        'specialties': ['books', 'educational'],
        'reliability': 0.92,
        'delivery_speed': 'medium'
    },
    'supplier_home': {
        'name': 'Home & Garden Suppliers',
        'specialties': ['home', 'garden', 'furniture'],
        'reliability': 0.85,
        'delivery_speed': 'slow'
    },
    'supplier_sports': {
        'name': 'SportsPro Distributors',
        'specialties': ['sports', 'fitness'],
        'reliability': 0.90,
        'delivery_speed': 'fast'
    },
    'supplier_general': {
        'name': 'General Goods Inc.',
        'specialties': ['general', 'miscellaneous'],
        'reliability': 0.80,
        'delivery_speed': 'medium'
    }
}

class SupplierEventService:
    """Service de gestion des fournisseurs basé sur les événements"""
    
    def __init__(self):
        self.event_store_url = EVENT_STORE_URL
        self.inventory_service_url = INVENTORY_SERVICE_URL
        self.running = False
        self.event_listener_thread = None
        self.delivery_worker_thread = None
    
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
    
    def handle_restock_approved(self, event_data: Dict[str, Any]):
        """Gère l'événement RestockApproved"""
        try:
            restock_request_id = event_data['restock_request_id']
            product_id = event_data['product_id']
            approved_quantity = event_data['approved_quantity']
            supplier_id = event_data['supplier_id']
            
            # Vérifier si ce fournisseur peut traiter la demande
            if supplier_id not in suppliers_catalog:
                logger.warning(f"Unknown supplier {supplier_id}, using default")
                supplier_id = 'supplier_general'
            
            supplier_info = suppliers_catalog[supplier_id]
            
            # Simuler la disponibilité du fournisseur
            reliability = supplier_info['reliability']
            is_available = random.random() < reliability
            
            if not is_available:
                logger.warning(f"Supplier {supplier_id} is not available for request {restock_request_id}")
                # En production, on publierait un événement SupplierUnavailable
                return
            
            # Calculer le délai de livraison
            delivery_speed = supplier_info['delivery_speed']
            if delivery_speed == 'fast':
                delivery_days = random.randint(MIN_DELIVERY_DAYS, MIN_DELIVERY_DAYS + 2)
            elif delivery_speed == 'medium':
                delivery_days = random.randint(MIN_DELIVERY_DAYS + 1, MAX_DELIVERY_DAYS - 1)
            else:  # slow
                delivery_days = random.randint(MAX_DELIVERY_DAYS - 2, MAX_DELIVERY_DAYS)
            
            # Programmer la livraison
            delivery_id = f"delivery_{restock_request_id}_{uuid.uuid4().hex[:8]}"
            delivery_date = datetime.now(timezone.utc) + timedelta(days=delivery_days)
            
            delivery_info = {
                'delivery_id': delivery_id,
                'restock_request_id': restock_request_id,
                'product_id': product_id,
                'quantity': approved_quantity,
                'supplier_id': supplier_id,
                'supplier_name': supplier_info['name'],
                'scheduled_delivery_date': delivery_date.isoformat(),
                'status': 'scheduled',
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Stocker la livraison programmée
            pending_deliveries[delivery_id] = delivery_info
            
            # Publier l'événement DeliveryScheduled
            self.publish_event(
                event_type='DeliveryScheduled',
                aggregate_id=delivery_id,
                aggregate_type='Delivery',
                data=delivery_info
            )
            
            logger.info(f"Scheduled delivery {delivery_id} for {delivery_days} days from now")
            
        except Exception as e:
            logger.error(f"Error handling RestockApproved event: {e}")
    
    def process_delivery(self, delivery_id: str) -> bool:
        """Traite une livraison (simule la réception de stock)"""
        try:
            delivery_info = pending_deliveries.get(delivery_id)
            if not delivery_info:
                logger.error(f"Delivery {delivery_id} not found")
                return False
            
            # Simuler des variations de quantité (défauts, bonus, etc.)
            expected_quantity = delivery_info['quantity']
            delivery_variance = random.uniform(0.9, 1.1)  # +/-10%
            actual_quantity = max(1, int(expected_quantity * delivery_variance))
            
            # Mettre à jour le statut
            delivery_info['status'] = 'delivered'
            delivery_info['actual_quantity'] = actual_quantity
            delivery_info['delivered_at'] = datetime.now(timezone.utc).isoformat()
            
            # Publier l'événement StockReceived
            stock_received_data = {
                'product_id': delivery_info['product_id'],
                'received_quantity': actual_quantity,
                'supplier_id': delivery_info['supplier_id'],
                'restock_request_id': delivery_info['restock_request_id'],
                'delivery_id': delivery_id,
                'delivery_date': delivery_info['delivered_at'],
                'expected_quantity': expected_quantity,
                'variance': actual_quantity - expected_quantity
            }
            
            success = self.publish_event(
                event_type='StockReceived',
                aggregate_id=delivery_info['product_id'],
                aggregate_type='Product',
                data=stock_received_data
            )
            
            if success:
                # Notifier le service d'inventaire
                self.notify_inventory_service(stock_received_data)
                
                # Déplacer vers l'historique
                delivery_history[delivery_id] = delivery_info
                del pending_deliveries[delivery_id]
                
                logger.info(f"Processed delivery {delivery_id}: {actual_quantity} units delivered")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing delivery {delivery_id}: {e}")
            return False
    
    def notify_inventory_service(self, stock_data: Dict[str, Any]):
        """Notifie le service d'inventaire de la réception de stock"""
        try:
            response = requests.post(
                f"{self.inventory_service_url}/api/products/{stock_data['product_id']}/restock",
                json={
                    'received_quantity': stock_data['received_quantity'],
                    'supplier_id': stock_data['supplier_id'],
                    'restock_request_id': stock_data['restock_request_id']
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Notified inventory service of stock reception for product {stock_data['product_id']}")
            else:
                logger.error(f"Failed to notify inventory service: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error notifying inventory service: {e}")
    
    def start_services(self):
        """Démarre les services d'écoute et de livraison"""
        self.running = True
        
        # Démarrer l'écoute des événements
        self.event_listener_thread = threading.Thread(target=self._event_listener_worker)
        self.event_listener_thread.daemon = True
        self.event_listener_thread.start()
        
        # Démarrer le worker de livraison
        self.delivery_worker_thread = threading.Thread(target=self._delivery_worker)
        self.delivery_worker_thread.daemon = True
        self.delivery_worker_thread.start()
        
        logger.info("Started Supplier Service workers")
    
    def stop_services(self):
        """Arrête les services"""
        self.running = False
        if self.event_listener_thread:
            self.event_listener_thread.join(timeout=5)
        if self.delivery_worker_thread:
            self.delivery_worker_thread.join(timeout=5)
        logger.info("Stopped Supplier Service workers")
    
    def _event_listener_worker(self):
        """Worker pour écouter les événements RestockApproved"""
        last_check = datetime.now(timezone.utc)
        
        while self.running:
            try:
                # Récupérer les nouveaux événements RestockApproved
                response = requests.get(
                    f"{self.event_store_url}/api/events/types/RestockApproved",
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
                            self.handle_restock_approved(event['data'])
                    
                    if events:
                        last_check = datetime.now(timezone.utc)
                
                time.sleep(20)  # Vérifier toutes les 20 secondes
                
            except Exception as e:
                logger.error(f"Error in event listener: {e}")
                time.sleep(60)
    
    def _delivery_worker(self):
        """Worker pour traiter les livraisons programmées"""
        while self.running:
            try:
                current_time = datetime.now(timezone.utc)
                deliveries_to_process = []
                
                # Chercher les livraisons prêtes
                for delivery_id, delivery_info in pending_deliveries.items():
                    scheduled_time = datetime.fromisoformat(
                        delivery_info['scheduled_delivery_date'].replace('Z', '+00:00')
                    )
                    
                    if current_time >= scheduled_time:
                        deliveries_to_process.append(delivery_id)
                
                # Traiter les livraisons
                for delivery_id in deliveries_to_process:
                    self.process_delivery(delivery_id)
                
                time.sleep(60)  # Vérifier toutes les minutes
                
            except Exception as e:
                logger.error(f"Error in delivery worker: {e}")
                time.sleep(120)

# Instance du service
supplier_service = SupplierEventService()

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de santé"""
    return jsonify({
        'status': 'healthy',
        'service': 'supplier-service',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'pending_deliveries': len(pending_deliveries),
        'completed_deliveries': len(delivery_history),
        'workers_running': supplier_service.running
    }), 200

@app.route('/api/suppliers', methods=['GET'])
def get_suppliers():
    """Obtenir la liste des fournisseurs"""
    try:
        return jsonify({
            'suppliers': suppliers_catalog
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting suppliers: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/deliveries/pending', methods=['GET'])
def get_pending_deliveries():
    """Obtenir les livraisons en attente"""
    try:
        deliveries = []
        for delivery_id, delivery_info in pending_deliveries.items():
            deliveries.append({
                'delivery_id': delivery_id,
                **delivery_info
            })
        
        return jsonify({
            'pending_deliveries': deliveries,
            'count': len(deliveries)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting pending deliveries: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/deliveries/history', methods=['GET'])
def get_delivery_history():
    """Obtenir l'historique des livraisons"""
    try:
        deliveries = []
        for delivery_id, delivery_info in delivery_history.items():
            deliveries.append({
                'delivery_id': delivery_id,
                **delivery_info
            })
        
        # Trier par date de livraison (plus récent en premier)
        deliveries.sort(key=lambda x: x.get('delivered_at', ''), reverse=True)
        
        return jsonify({
            'delivery_history': deliveries,
            'count': len(deliveries)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting delivery history: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/deliveries/<delivery_id>/process', methods=['POST'])
def force_process_delivery(delivery_id: str):
    """Forcer le traitement d'une livraison (pour les tests)"""
    try:
        success = supplier_service.process_delivery(delivery_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Delivery processed successfully',
                'delivery_id': delivery_id
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to process delivery'
            }), 400
            
    except Exception as e:
        logger.error(f"Error forcing delivery processing: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/events/start-services', methods=['POST'])
def start_services():
    """Démarrer les services d'événements"""
    try:
        if not supplier_service.running:
            supplier_service.start_services()
            return jsonify({
                'success': True,
                'message': 'Supplier services started'
            }), 200
        else:
            return jsonify({
                'success': True,
                'message': 'Supplier services already running'
            }), 200
            
    except Exception as e:
        logger.error(f"Error starting services: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/events/stop-services', methods=['POST'])
def stop_services():
    """Arrêter les services d'événements"""
    try:
        supplier_service.stop_services()
        return jsonify({
            'success': True,
            'message': 'Supplier services stopped'
        }), 200
        
    except Exception as e:
        logger.error(f"Error stopping services: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

if __name__ == '__main__':
    # Démarrer les services au lancement
    supplier_service.start_services()
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
        # Arrêter les services lors de l'arrêt
        supplier_service.stop_services()
