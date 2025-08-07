from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging
import os
import threading
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from collections import defaultdict
import json

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
EVENT_STORE_URL = os.getenv('EVENT_STORE_URL', 'http://event-bus-service:5000')

# Projections CQRS (vues de lecture optimisées)
class ProjectionStore:
    def __init__(self):
        # Projection 1: Stock Levels View
        self.stock_levels = {}
        
        # Projection 2: Restock Alerts View  
        self.restock_alerts = []
        
        # Projection 3: Supplier Performance View
        self.supplier_performance = defaultdict(lambda: {
            'total_orders': 0,
            'completed_deliveries': 0,
            'total_quantity_delivered': 0,
            'average_delivery_time': 0,
            'reliability_score': 0,
            'last_delivery': None
        })
        
        # Projection 4: Sales Analytics View
        self.sales_analytics = {
            'daily_sales': defaultdict(lambda: {'quantity': 0, 'revenue': 0}),
            'product_sales': defaultdict(lambda: {'total_quantity': 0, 'total_revenue': 0, 'sale_count': 0}),
            'customer_stats': defaultdict(lambda: {'total_purchases': 0, 'total_spent': 0})
        }
        
        # Projection 5: Inventory Movements View
        self.inventory_movements = []
        
        # Métadonnées des projections
        self.projection_metadata = {
            'last_updated': None,
            'last_event_processed': None,
            'events_processed_count': 0
        }

# Instance du store de projections
projection_store = ProjectionStore()

class AnalyticsEventService:
    """Service d'analytics basé sur les événements - Implémentation CQRS"""
    
    def __init__(self):
        self.event_store_url = EVENT_STORE_URL
        self.running = False
        self.projection_worker_thread = None
    
    def update_projections_from_event(self, event: Dict[str, Any]):
        """Met à jour toutes les projections basées sur un événement"""
        try:
            event_type = event['event_type']
            event_data = event['data']
            event_timestamp = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
            
            if event_type == 'ProductSold':
                self._handle_product_sold(event_data, event_timestamp)
            elif event_type == 'LowStockDetected':
                self._handle_low_stock_detected(event_data, event_timestamp)
            elif event_type == 'RestockRequested':
                self._handle_restock_requested(event_data, event_timestamp)
            elif event_type == 'StockReceived':
                self._handle_stock_received(event_data, event_timestamp)
            elif event_type == 'DeliveryScheduled':
                self._handle_delivery_scheduled(event_data, event_timestamp)
            
            # Mettre à jour les métadonnées
            projection_store.projection_metadata['last_updated'] = datetime.now(timezone.utc).isoformat()
            projection_store.projection_metadata['last_event_processed'] = event['event_id']
            projection_store.projection_metadata['events_processed_count'] += 1
            
        except Exception as e:
            logger.error(f"Error updating projections from event: {e}")
    
    def _handle_product_sold(self, event_data: Dict[str, Any], timestamp: datetime):
        """Met à jour les projections pour ProductSold"""
        product_id = event_data['product_id']
        quantity = event_data['quantity']
        total_amount = event_data['total_amount']
        customer_id = event_data['customer_id']
        
        # Mise à jour Stock Levels
        current_stock = projection_store.stock_levels.get(product_id, 0)
        projection_store.stock_levels[product_id] = max(0, current_stock - quantity)
        
        # Mise à jour Sales Analytics
        date_key = timestamp.date().isoformat()
        projection_store.sales_analytics['daily_sales'][date_key]['quantity'] += quantity
        projection_store.sales_analytics['daily_sales'][date_key]['revenue'] += total_amount
        
        projection_store.sales_analytics['product_sales'][product_id]['total_quantity'] += quantity
        projection_store.sales_analytics['product_sales'][product_id]['total_revenue'] += total_amount
        projection_store.sales_analytics['product_sales'][product_id]['sale_count'] += 1
        
        projection_store.sales_analytics['customer_stats'][customer_id]['total_purchases'] += 1
        projection_store.sales_analytics['customer_stats'][customer_id]['total_spent'] += total_amount
        
        # Mise à jour Inventory Movements
        projection_store.inventory_movements.append({
            'timestamp': timestamp.isoformat(),
            'product_id': product_id,
            'movement_type': 'sale',
            'quantity': -quantity,
            'reason': 'product_sold',
            'reference': f"sale_{customer_id}"
        })
        
        logger.debug(f"Updated projections for ProductSold: {product_id}")
    
    def _handle_low_stock_detected(self, event_data: Dict[str, Any], timestamp: datetime):
        """Met à jour les projections pour LowStockDetected"""
        product_id = event_data['product_id']
        current_stock = event_data['current_stock']
        threshold = event_data['minimum_threshold']
        
        # Mise à jour Restock Alerts
        alert = {
            'product_id': product_id,
            'current_stock': current_stock,
            'threshold': threshold,
            'severity': 'critical' if current_stock == 0 else 'warning',
            'detected_at': timestamp.isoformat(),
            'status': 'active'
        }
        
        # Éviter les doublons d'alertes actives
        existing_alert = None
        for i, existing in enumerate(projection_store.restock_alerts):
            if (existing['product_id'] == product_id and 
                existing['status'] == 'active'):
                existing_alert = i
                break
        
        if existing_alert is not None:
            projection_store.restock_alerts[existing_alert] = alert
        else:
            projection_store.restock_alerts.append(alert)
        
        logger.debug(f"Updated restock alert for product {product_id}")
    
    def _handle_restock_requested(self, event_data: Dict[str, Any], timestamp: datetime):
        """Met à jour les projections pour RestockRequested"""
        supplier_id = event_data['supplier_id']
        
        # Mise à jour Supplier Performance
        projection_store.supplier_performance[supplier_id]['total_orders'] += 1
        
        logger.debug(f"Updated supplier performance for RestockRequested: {supplier_id}")
    
    def _handle_stock_received(self, event_data: Dict[str, Any], timestamp: datetime):
        """Met à jour les projections pour StockReceived"""
        product_id = event_data['product_id']
        received_quantity = event_data['received_quantity']
        supplier_id = event_data['supplier_id']
        
        # Mise à jour Stock Levels
        current_stock = projection_store.stock_levels.get(product_id, 0)
        projection_store.stock_levels[product_id] = current_stock + received_quantity
        
        # Mise à jour Supplier Performance
        supplier_perf = projection_store.supplier_performance[supplier_id]
        supplier_perf['completed_deliveries'] += 1
        supplier_perf['total_quantity_delivered'] += received_quantity
        supplier_perf['last_delivery'] = timestamp.isoformat()
        
        # Calculer le score de fiabilité
        if supplier_perf['total_orders'] > 0:
            supplier_perf['reliability_score'] = (
                supplier_perf['completed_deliveries'] / supplier_perf['total_orders']
            ) * 100
        
        # Mise à jour Inventory Movements
        projection_store.inventory_movements.append({
            'timestamp': timestamp.isoformat(),
            'product_id': product_id,
            'movement_type': 'restock',
            'quantity': received_quantity,
            'reason': 'stock_received',
            'reference': f"supplier_{supplier_id}"
        })
        
        # Résoudre l'alerte de stock si elle existe
        for alert in projection_store.restock_alerts:
            if (alert['product_id'] == product_id and 
                alert['status'] == 'active'):
                new_stock = projection_store.stock_levels[product_id]
                if new_stock > alert['threshold']:
                    alert['status'] = 'resolved'
                    alert['resolved_at'] = timestamp.isoformat()
        
        logger.debug(f"Updated projections for StockReceived: {product_id}")
    
    def _handle_delivery_scheduled(self, event_data: Dict[str, Any], timestamp: datetime):
        """Met à jour les projections pour DeliveryScheduled"""
        supplier_id = event_data['supplier_id']
        
        # Pourrait être utilisé pour calculer les délais de livraison moyens
        logger.debug(f"Processed DeliveryScheduled for supplier {supplier_id}")
    
    def rebuild_projections_from_events(self) -> bool:
        """Reconstruit toutes les projections depuis l'Event Store"""
        try:
            logger.info("Starting projection rebuild from events...")
            
            # Réinitialiser les projections
            projection_store.stock_levels.clear()
            projection_store.restock_alerts.clear()
            projection_store.supplier_performance.clear()
            projection_store.sales_analytics = {
                'daily_sales': defaultdict(lambda: {'quantity': 0, 'revenue': 0}),
                'product_sales': defaultdict(lambda: {'total_quantity': 0, 'total_revenue': 0, 'sale_count': 0}),
                'customer_stats': defaultdict(lambda: {'total_purchases': 0, 'total_spent': 0})
            }
            projection_store.inventory_movements.clear()
            
            # Récupérer tous les événements
            response = requests.get(
                f"{self.event_store_url}/api/events/replay/all",
                params={'limit': 10000},
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch events: {response.status_code}")
                return False
            
            events_data = response.json()
            events = events_data.get('events', [])
            
            # Traiter les événements en ordre chronologique
            events.sort(key=lambda x: x['timestamp'])
            
            processed_count = 0
            for event in events:
                self.update_projections_from_event(event)
                processed_count += 1
            
            logger.info(f"Rebuilt projections from {processed_count} events")
            return True
            
        except Exception as e:
            logger.error(f"Error rebuilding projections: {e}")
            return False
    
    def start_projection_updates(self):
        """Démarre la mise à jour continue des projections"""
        self.running = True
        self.projection_worker_thread = threading.Thread(target=self._projection_worker)
        self.projection_worker_thread.daemon = True
        self.projection_worker_thread.start()
        logger.info("Started projection updates worker")
    
    def stop_projection_updates(self):
        """Arrête la mise à jour des projections"""
        self.running = False
        if self.projection_worker_thread:
            self.projection_worker_thread.join(timeout=5)
        logger.info("Stopped projection updates worker")
    
    def _projection_worker(self):
        """Worker pour mettre à jour les projections en continu"""
        last_check = datetime.now(timezone.utc) - timedelta(hours=1)
        
        while self.running:
            try:
                # Récupérer les nouveaux événements
                response = requests.get(
                    f"{self.event_store_url}/api/events/replay/all",
                    params={
                        'since': last_check.isoformat(),
                        'limit': 100
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    events_data = response.json()
                    events = events_data.get('events', [])
                    
                    if events:
                        # Traiter les nouveaux événements
                        events.sort(key=lambda x: x['timestamp'])
                        for event in events:
                            event_timestamp = datetime.fromisoformat(
                                event['timestamp'].replace('Z', '+00:00')
                            )
                            if event_timestamp > last_check:
                                self.update_projections_from_event(event)
                        
                        last_check = datetime.now(timezone.utc)
                        logger.debug(f"Processed {len(events)} new events for projections")
                
                time.sleep(30)  # Mettre à jour toutes les 30 secondes
                
            except Exception as e:
                logger.error(f"Error in projection worker: {e}")
                time.sleep(60)

# Instance du service
analytics_service = AnalyticsEventService()

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de santé"""
    return jsonify({
        'status': 'healthy',
        'service': 'analytics-service',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'projections_status': {
            'stock_levels_count': len(projection_store.stock_levels),
            'restock_alerts_count': len(projection_store.restock_alerts),
            'suppliers_tracked': len(projection_store.supplier_performance),
            'inventory_movements_count': len(projection_store.inventory_movements),
            'last_updated': projection_store.projection_metadata['last_updated'],
            'events_processed': projection_store.projection_metadata['events_processed_count']
        },
        'worker_running': analytics_service.running
    }), 200

@app.route('/api/projections/stock-levels', methods=['GET'])
def get_stock_levels():
    """Obtenir la vue des niveaux de stock (Projection CQRS)"""
    try:
        stock_data = []
        for product_id, stock_level in projection_store.stock_levels.items():
            stock_data.append({
                'product_id': product_id,
                'current_stock': stock_level,
                'is_low_stock': any(
                    alert['product_id'] == product_id and alert['status'] == 'active'
                    for alert in projection_store.restock_alerts
                )
            })
        
        return jsonify({
            'stock_levels': stock_data,
            'total_products': len(stock_data),
            'last_updated': projection_store.projection_metadata['last_updated']
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting stock levels: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/projections/restock-alerts', methods=['GET'])
def get_restock_alerts():
    """Obtenir la vue des alertes de réapprovisionnement (Projection CQRS)"""
    try:
        status_filter = request.args.get('status', 'active')
        
        filtered_alerts = [
            alert for alert in projection_store.restock_alerts
            if alert['status'] == status_filter
        ]
        
        # Trier par sévérité puis par date
        filtered_alerts.sort(key=lambda x: (
            0 if x['severity'] == 'critical' else 1,
            x['detected_at']
        ))
        
        return jsonify({
            'restock_alerts': filtered_alerts,
            'total_alerts': len(filtered_alerts),
            'last_updated': projection_store.projection_metadata['last_updated']
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting restock alerts: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/projections/supplier-performance', methods=['GET'])
def get_supplier_performance():
    """Obtenir la vue de performance des fournisseurs (Projection CQRS)"""
    try:
        performance_data = []
        for supplier_id, perf in projection_store.supplier_performance.items():
            performance_data.append({
                'supplier_id': supplier_id,
                **perf
            })
        
        # Trier par score de fiabilité
        performance_data.sort(key=lambda x: x['reliability_score'], reverse=True)
        
        return jsonify({
            'supplier_performance': performance_data,
            'total_suppliers': len(performance_data),
            'last_updated': projection_store.projection_metadata['last_updated']
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting supplier performance: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/projections/sales-analytics', methods=['GET'])
def get_sales_analytics():
    """Obtenir la vue d'analytics des ventes (Projection CQRS)"""
    try:
        period = request.args.get('period', 'week')  # week, month, all
        
        # Préparer les données selon la période
        if period == 'week':
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)
        elif period == 'month':
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
        else:
            cutoff_date = datetime.min.replace(tzinfo=timezone.utc)
        
        # Filtrer les données par période
        filtered_daily_sales = {}
        for date_str, sales_data in projection_store.sales_analytics['daily_sales'].items():
            date_obj = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
            if date_obj >= cutoff_date:
                filtered_daily_sales[date_str] = sales_data
        
        # Convertir les defaultdict en dict normaux pour JSON
        return jsonify({
            'sales_analytics': {
                'daily_sales': dict(filtered_daily_sales),
                'product_sales': dict(projection_store.sales_analytics['product_sales']),
                'customer_stats': dict(projection_store.sales_analytics['customer_stats'])
            },
            'period': period,
            'last_updated': projection_store.projection_metadata['last_updated']
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting sales analytics: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/projections/inventory-movements', methods=['GET'])
def get_inventory_movements():
    """Obtenir la vue des mouvements d'inventaire (Projection CQRS)"""
    try:
        limit = request.args.get('limit', 100, type=int)
        product_filter = request.args.get('product_id')
        
        movements = projection_store.inventory_movements
        
        # Filtrer par produit si spécifié
        if product_filter:
            movements = [m for m in movements if m['product_id'] == product_filter]
        
        # Trier par timestamp (plus récent en premier) et limiter
        movements.sort(key=lambda x: x['timestamp'], reverse=True)
        movements = movements[:limit]
        
        return jsonify({
            'inventory_movements': movements,
            'total_movements': len(movements),
            'last_updated': projection_store.projection_metadata['last_updated']
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting inventory movements: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/projections/rebuild', methods=['POST'])
def rebuild_projections():
    """Reconstruire toutes les projections depuis l'Event Store"""
    try:
        success = analytics_service.rebuild_projections_from_events()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Projections rebuilt successfully',
                'events_processed': projection_store.projection_metadata['events_processed_count'],
                'last_updated': projection_store.projection_metadata['last_updated']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to rebuild projections'
            }), 500
            
    except Exception as e:
        logger.error(f"Error rebuilding projections: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/events/start-updates', methods=['POST'])
def start_projection_updates():
    """Démarrer les mises à jour continues des projections"""
    try:
        if not analytics_service.running:
            analytics_service.start_projection_updates()
            return jsonify({
                'success': True,
                'message': 'Projection updates started'
            }), 200
        else:
            return jsonify({
                'success': True,
                'message': 'Projection updates already running'
            }), 200
            
    except Exception as e:
        logger.error(f"Error starting projection updates: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/events/stop-updates', methods=['POST'])
def stop_projection_updates():
    """Arrêter les mises à jour des projections"""
    try:
        analytics_service.stop_projection_updates()
        return jsonify({
            'success': True,
            'message': 'Projection updates stopped'
        }), 200
        
    except Exception as e:
        logger.error(f"Error stopping projection updates: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

if __name__ == '__main__':
    # Reconstruire les projections au démarrage
    logger.info("Rebuilding projections at startup...")
    analytics_service.rebuild_projections_from_events()
    
    # Démarrer les mises à jour continues
    analytics_service.start_projection_updates()
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
        # Arrêter les mises à jour lors de l'arrêt
        analytics_service.stop_projection_updates()
