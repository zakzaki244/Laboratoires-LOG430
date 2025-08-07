from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging
import os
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import json

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
EVENT_STORE_URL = os.getenv('EVENT_STORE_URL', 'http://event-bus-service:5000')
LOW_STOCK_THRESHOLD = int(os.getenv('LOW_STOCK_THRESHOLD', '5'))

# État en mémoire pour les projections de stock (en production, utiliser Redis ou DB)
stock_projections = {}
product_info = {}

class InventoryEventService:
    """Service de gestion du stock basé sur les événements"""
    
    def __init__(self):
        self.event_store_url = EVENT_STORE_URL
    
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
    
    def get_current_stock(self, product_id: str) -> int:
        """Obtient le stock actuel d'un produit depuis la projection"""
        return stock_projections.get(product_id, 0)
    
    def update_stock_projection(self, product_id: str, quantity_change: int):
        """Met à jour la projection de stock"""
        current_stock = stock_projections.get(product_id, 0)
        new_stock = max(0, current_stock + quantity_change)  # Pas de stock négatif
        stock_projections[product_id] = new_stock
        
        logger.info(f"Updated stock projection for product {product_id}: {current_stock} -> {new_stock}")
        
        # Vérifier si le stock est faible
        if new_stock <= LOW_STOCK_THRESHOLD and quantity_change < 0:
            self.trigger_low_stock_event(product_id, new_stock)
    
    def trigger_low_stock_event(self, product_id: str, current_stock: int):
        """Déclenche un événement de stock faible"""
        event_data = {
            'product_id': product_id,
            'current_stock': current_stock,
            'minimum_threshold': LOW_STOCK_THRESHOLD,
            'detected_at': datetime.now(timezone.utc).isoformat()
        }
        
        self.publish_event(
            event_type='LowStockDetected',
            aggregate_id=product_id,
            aggregate_type='Product',
            data=event_data
        )
    
    def process_product_sold(self, product_id: str, quantity: int, 
                           price: float, customer_id: str) -> bool:
        """Traite une vente de produit"""
        try:
            # Vérifier le stock disponible
            current_stock = self.get_current_stock(product_id)
            if current_stock < quantity:
                logger.warning(f"Insufficient stock for product {product_id}: {current_stock} < {quantity}")
                return False
            
            # Publier l'événement ProductSold
            event_data = {
                'product_id': product_id,
                'quantity': quantity,
                'price': price,
                'customer_id': customer_id,
                'total_amount': quantity * price,
                'sale_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            success = self.publish_event(
                event_type='ProductSold',
                aggregate_id=product_id,
                aggregate_type='Product',
                data=event_data
            )
            
            if success:
                # Mettre à jour la projection de stock
                self.update_stock_projection(product_id, -quantity)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing product sale: {e}")
            return False
    
    def process_stock_received(self, product_id: str, received_quantity: int,
                             supplier_id: str, restock_request_id: str) -> bool:
        """Traite la réception de stock"""
        try:
            # Publier l'événement StockReceived
            event_data = {
                'product_id': product_id,
                'received_quantity': received_quantity,
                'supplier_id': supplier_id,
                'restock_request_id': restock_request_id,
                'delivery_date': datetime.now(timezone.utc).isoformat()
            }
            
            success = self.publish_event(
                event_type='StockReceived',
                aggregate_id=product_id,
                aggregate_type='Product',
                data=event_data
            )
            
            if success:
                # Mettre à jour la projection de stock
                self.update_stock_projection(product_id, received_quantity)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing stock received: {e}")
            return False
    
    def initialize_stock(self, product_id: str, initial_quantity: int):
        """Initialise le stock d'un produit"""
        stock_projections[product_id] = initial_quantity
        logger.info(f"Initialized stock for product {product_id}: {initial_quantity}")

# Instance du service
inventory_service = InventoryEventService()

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de santé"""
    return jsonify({
        'status': 'healthy',
        'service': 'inventory-event-service',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'stock_items_count': len(stock_projections)
    }), 200

@app.route('/api/products/<product_id>/sell', methods=['POST'])
def sell_product(product_id: str):
    """Vendre un produit (commande)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validation
        required_fields = ['quantity', 'price', 'customer_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        quantity = int(data['quantity'])
        price = float(data['price'])
        customer_id = data['customer_id']
        
        if quantity <= 0:
            return jsonify({'error': 'Quantity must be positive'}), 400
        
        # Traiter la vente
        success = inventory_service.process_product_sold(
            product_id=product_id,
            quantity=quantity,
            price=price,
            customer_id=customer_id
        )
        
        if success:
            current_stock = inventory_service.get_current_stock(product_id)
            return jsonify({
                'success': True,
                'message': 'Product sold successfully',
                'product_id': product_id,
                'quantity_sold': quantity,
                'remaining_stock': current_stock,
                'total_amount': quantity * price
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to process sale - insufficient stock'
            }), 400
            
    except Exception as e:
        logger.error(f"Error in sell_product: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/products/<product_id>/restock', methods=['POST'])
def receive_stock(product_id: str):
    """Recevoir du stock (événement de réapprovisionnement)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validation
        required_fields = ['received_quantity', 'supplier_id', 'restock_request_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        received_quantity = int(data['received_quantity'])
        supplier_id = data['supplier_id']
        restock_request_id = data['restock_request_id']
        
        if received_quantity <= 0:
            return jsonify({'error': 'Received quantity must be positive'}), 400
        
        # Traiter la réception
        success = inventory_service.process_stock_received(
            product_id=product_id,
            received_quantity=received_quantity,
            supplier_id=supplier_id,
            restock_request_id=restock_request_id
        )
        
        if success:
            current_stock = inventory_service.get_current_stock(product_id)
            return jsonify({
                'success': True,
                'message': 'Stock received successfully',
                'product_id': product_id,
                'received_quantity': received_quantity,
                'new_stock_level': current_stock
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to process stock reception'
            }), 500
            
    except Exception as e:
        logger.error(f"Error in receive_stock: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/products/<product_id>/stock', methods=['GET'])
def get_stock_level(product_id: str):
    """Obtenir le niveau de stock actuel"""
    try:
        current_stock = inventory_service.get_current_stock(product_id)
        
        return jsonify({
            'product_id': product_id,
            'current_stock': current_stock,
            'low_stock_threshold': LOW_STOCK_THRESHOLD,
            'is_low_stock': current_stock <= LOW_STOCK_THRESHOLD
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting stock level: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/products/stock/all', methods=['GET'])
def get_all_stock_levels():
    """Obtenir tous les niveaux de stock"""
    try:
        stock_data = []
        for product_id, stock_level in stock_projections.items():
            stock_data.append({
                'product_id': product_id,
                'current_stock': stock_level,
                'is_low_stock': stock_level <= LOW_STOCK_THRESHOLD
            })
        
        return jsonify({
            'stock_levels': stock_data,
            'total_products': len(stock_data),
            'low_stock_threshold': LOW_STOCK_THRESHOLD
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting all stock levels: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/products/<product_id>/initialize', methods=['POST'])
def initialize_product_stock(product_id: str):
    """Initialiser le stock d'un produit"""
    try:
        data = request.get_json()
        if not data or 'initial_quantity' not in data:
            return jsonify({'error': 'Missing initial_quantity'}), 400
        
        initial_quantity = int(data['initial_quantity'])
        if initial_quantity < 0:
            return jsonify({'error': 'Initial quantity cannot be negative'}), 400
        
        inventory_service.initialize_stock(product_id, initial_quantity)
        
        return jsonify({
            'success': True,
            'message': 'Product stock initialized',
            'product_id': product_id,
            'initial_quantity': initial_quantity
        }), 201
        
    except Exception as e:
        logger.error(f"Error initializing product stock: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/events/replay', methods=['POST'])
def replay_events():
    """Replay des événements pour reconstruire les projections"""
    try:
        # Récupérer tous les événements depuis l'Event Store
        response = requests.get(f"{EVENT_STORE_URL}/api/events/replay/inventory")
        
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch events from Event Store'}), 500
        
        events_data = response.json()
        events = events_data.get('events', [])
        
        # Réinitialiser les projections
        stock_projections.clear()
        
        # Rejouer les événements
        processed_count = 0
        for event in events:
            event_type = event['event_type']
            event_data = event['data']
            
            if event_type == 'ProductSold':
                product_id = event_data['product_id']
                quantity = event_data['quantity']
                inventory_service.update_stock_projection(product_id, -quantity)
                processed_count += 1
                
            elif event_type == 'StockReceived':
                product_id = event_data['product_id']
                received_quantity = event_data['received_quantity']
                inventory_service.update_stock_projection(product_id, received_quantity)
                processed_count += 1
        
        logger.info(f"Replayed {processed_count} events to rebuild stock projections")
        
        return jsonify({
            'success': True,
            'message': 'Events replayed successfully',
            'events_processed': processed_count,
            'current_stock_projections': stock_projections
        }), 200
        
    except Exception as e:
        logger.error(f"Error replaying events: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

if __name__ == '__main__':
    # Initialiser quelques produits pour les tests
    inventory_service.initialize_stock('1', 20)
    inventory_service.initialize_stock('2', 15)
    inventory_service.initialize_stock('3', 8)
    inventory_service.initialize_stock('4', 25)
    inventory_service.initialize_stock('5', 3)  # Stock faible pour tester les alertes
    
    app.run(host='0.0.0.0', port=5000, debug=False)
