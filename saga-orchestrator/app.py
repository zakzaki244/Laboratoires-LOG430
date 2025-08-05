from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import logging
import uuid
from datetime import datetime
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from machine_etat import OrderSaga, OrderState, SagaEvent

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration de la base de données
app.config['SQLALchemy_DATABASE_URI'] = 'postgresql://log430:laboratoire@saga-db:5432/sagadb'
app.config['SQLALchemy_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configuration des services
SERVICES = {
    'product': 'http://product-service:5000',
    'sales': 'http://sales-service:5000',
    'customer': 'http://customer-service:5000'
}

# Métriques Prometheus
SAGA_COUNTER = Counter('saga_total', 'Total number of sagas', ['status'])
SAGA_DURATION = Histogram('saga_duration_seconds', 'Saga execution duration')
STEP_DURATION = Histogram('saga_step_duration_seconds', 'Saga step duration', ['step'])

# Stockage en mémoire des Sagas actives (en production, utiliser Redis ou DB)
active_sagas = {}

class SagaExecutionError(Exception):
    """Exception personnalisée pour les erreurs de Saga"""
    pass

class SagaOrchestrator:
    """Orchestrateur principal de la Saga"""
    
    def __init__(self):
        self.services = SERVICES
    
    def execute_order_saga(self, order_data: dict) -> dict:
        """Exécute la Saga complète pour une commande"""
        order_id = str(uuid.uuid4())
        customer_id = order_data.get('customer_id', '')
        items = order_data.get('items', [])
        
        # Créer une nouvelle instance de Saga
        saga = OrderSaga(order_id, customer_id, items)
        active_sagas[order_id] = saga
        
        try:
            with SAGA_DURATION.time():
                # Étape 1: Vérification du stock
                self._check_stock(saga)
                
                # Étape 2: Réservation du stock
                self._reserve_stock(saga)
                
                # Étape 3: Traitement du paiement
                self._process_payment(saga)
                
                # Étape 4: Confirmation de la commande
                self._confirm_order(saga)
                
                SAGA_COUNTER.labels(status='success').inc()
                return {
                    'success': True,
                    'order_id': order_id,
                    'state': saga.current_state.value,
                    'message': 'Commande confirmée avec succès'
                }
                
        except SagaExecutionError as e:
            logger.error(f"Saga {order_id} failed: {str(e)}")
            saga.mark_failed(str(e))
            SAGA_COUNTER.labels(status='failed').inc()
            
            # Exécuter les compensations
            self._execute_compensations(saga)
            
            return {
                'success': False,
                'order_id': order_id,
                'state': saga.current_state.value,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error in saga {order_id}: {str(e)}")
            saga.mark_failed(f"Erreur système: {str(e)}")
            SAGA_COUNTER.labels(status='failed').inc()
            
            return {
                'success': False,
                'order_id': order_id,
                'state': saga.current_state.value,
                'error': f"Erreur système: {str(e)}"
            }
    
    def _check_stock(self, saga: OrderSaga):
        """Étape 1: Vérification du stock"""
        with STEP_DURATION.labels(step='stock_check').time():
            try:
                # Préparer les données pour la vérification de stock
                stock_check_data = {
                    'items': saga.items
                }
                
                # Appel au service produit pour vérifier le stock
                response = requests.post(
                    f"{self.services['product']}/api/check-stock",
                    json=stock_check_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('available', False):
                        saga.transition_to(OrderState.STOCK_CHECKED, SagaEvent.STOCK_CHECK_SUCCESS, result)
                        logger.info(f"Stock check successful for order {saga.order_id}")
                    else:
                        raise SagaExecutionError("Stock insuffisant pour certains produits")
                else:
                    raise SagaExecutionError(f"Erreur lors de la vérification du stock: {response.status_code}")
                    
            except requests.RequestException as e:
                raise SagaExecutionError(f"Erreur de communication avec le service produit: {str(e)}")
    
    def _reserve_stock(self, saga: OrderSaga):
        """Étape 2: Réservation du stock"""
        with STEP_DURATION.labels(step='stock_reservation').time():
            try:
                # Préparer les données pour la réservation
                reservation_data = {
                    'order_id': saga.order_id,
                    'items': saga.items
                }
                
                # Appel au service produit pour réserver le stock
                response = requests.post(
                    f"{self.services['product']}/api/reserve-stock",
                    json=reservation_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success', False):
                        saga.transition_to(OrderState.STOCK_RESERVED, SagaEvent.STOCK_RESERVATION_SUCCESS, result)
                        # Stocker les données de compensation
                        saga.add_compensation_data('product', {
                            'reservation_id': result.get('reservation_id'),
                            'items': saga.items
                        })
                        logger.info(f"Stock reservation successful for order {saga.order_id}")
                    else:
                        raise SagaExecutionError("Échec de la réservation du stock")
                else:
                    raise SagaExecutionError(f"Erreur lors de la réservation du stock: {response.status_code}")
                    
            except requests.RequestException as e:
                raise SagaExecutionError(f"Erreur de communication avec le service produit: {str(e)}")
    
    def _process_payment(self, saga: OrderSaga):
        """Étape 3: Traitement du paiement"""
        with STEP_DURATION.labels(step='payment').time():
            try:
                # Préparer les données de paiement
                payment_data = {
                    'order_id': saga.order_id,
                    'customer_id': saga.customer_id,
                    'amount': self._calculate_total_amount(saga.items)
                }
                
                # Appel au service de vente pour le paiement
                response = requests.post(
                    f"{self.services['sales']}/api/process-payment",
                    json=payment_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success', False):
                        saga.transition_to(OrderState.PAYMENT_PROCESSED, SagaEvent.PAYMENT_SUCCESS, result)
                        # Stocker les données de compensation
                        saga.add_compensation_data('sales', {
                            'payment_id': result.get('payment_id'),
                            'amount': payment_data['amount']
                        })
                        logger.info(f"Payment processed successfully for order {saga.order_id}")
                    else:
                        raise SagaExecutionError("Échec du traitement du paiement")
                else:
                    raise SagaExecutionError(f"Erreur lors du traitement du paiement: {response.status_code}")
                    
            except requests.RequestException as e:
                raise SagaExecutionError(f"Erreur de communication avec le service de vente: {str(e)}")
    
    def _confirm_order(self, saga: OrderSaga):
        """Étape 4: Confirmation de la commande"""
        with STEP_DURATION.labels(step='order_confirmation').time():
            try:
                # Préparer les données de confirmation
                confirmation_data = {
                    'order_id': saga.order_id,
                    'customer_id': saga.customer_id,
                    'items': saga.items,
                    'payment_id': (saga.get_compensation_data('sales') or {}).get('payment_id')
                }
                
                # Appel au service de vente pour confirmer la commande
                response = requests.post(
                    f"{self.services['sales']}/api/confirm-order",
                    json=confirmation_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success', False):
                        saga.transition_to(OrderState.CONFIRMED, SagaEvent.ORDER_CONFIRMED, result)
                        logger.info(f"Order confirmed successfully: {saga.order_id}")
                    else:
                        raise SagaExecutionError("Échec de la confirmation de la commande")
                else:
                    raise SagaExecutionError(f"Erreur lors de la confirmation: {response.status_code}")
                    
            except requests.RequestException as e:
                raise SagaExecutionError(f"Erreur de communication avec le service de vente: {str(e)}")
    
    def _execute_compensations(self, saga: OrderSaga):
        """Exécute les compensations en cas d'échec"""
        logger.info(f"Executing compensations for order {saga.order_id}")
        
        # Compensation 1: Annuler la réservation de stock
        if saga.get_compensation_data('product'):
            try:
                self._compensate_stock_reservation(saga)
            except Exception as e:
                logger.error(f"Compensation stock failed: {str(e)}")
        
        # Compensation 2: Rembourser le paiement
        if saga.get_compensation_data('sales'):
            try:
                self._compensate_payment(saga)
            except Exception as e:
                logger.error(f"Compensation payment failed: {str(e)}")
        
        saga.add_event(SagaEvent.COMPENSATION_COMPLETED)
    
    def _compensate_stock_reservation(self, saga: OrderSaga):
        """Compensation: Annuler la réservation de stock"""
        try:
            compensation_data = saga.get_compensation_data('product')
            response = requests.post(
                f"{self.services['product']}/api/release-stock",
                json=compensation_data,
                timeout=10
            )
            if response.status_code == 200:
                logger.info(f"Stock reservation released for order {saga.order_id}")
            else:
                logger.error(f"Failed to release stock reservation: {response.status_code}")
        except Exception as e:
            logger.error(f"Error during stock compensation: {str(e)}")
    
    def _compensate_payment(self, saga: OrderSaga):
        """Compensation: Rembourser le paiement"""
        try:
            compensation_data = saga.get_compensation_data('sales')
            response = requests.post(
                f"{self.services['sales']}/api/refund-payment",
                json=compensation_data,
                timeout=10
            )
            if response.status_code == 200:
                logger.info(f"Payment refunded for order {saga.order_id}")
            else:
                logger.error(f"Failed to refund payment: {response.status_code}")
        except Exception as e:
            logger.error(f"Error during payment compensation: {str(e)}")
    
    def _calculate_total_amount(self, items: list) -> float:
        """Calcule le montant total de la commande"""
        total = 0.0
        for item in items:
            total += item.get('price', 0) * item.get('quantity', 1)
        return total

# Instance globale de l'orchestrateur
orchestrator = SagaOrchestrator()

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de santé"""
    return jsonify({'status': 'healthy', 'service': 'saga-orchestrator'})

@app.route('/api/saga/order', methods=['POST'])
def create_order_saga():
    """Endpoint pour créer et exécuter une Saga de commande"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Données manquantes'}), 400
        
        # Validation des données
        required_fields = ['customer_id', 'items']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Champ requis manquant: {field}'}), 400
        
        # Exécuter la Saga
        result = orchestrator.execute_order_saga(data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in create_order_saga: {str(e)}")
        return jsonify({'error': f'Erreur interne: {str(e)}'}), 500

@app.route('/api/saga/<order_id>/status', methods=['GET'])
def get_saga_status(order_id: str):
    """Endpoint pour obtenir le statut d'une Saga"""
    try:
        saga = active_sagas.get(order_id)
        if not saga:
            return jsonify({'error': 'Saga non trouvée'}), 404
        
        return jsonify(saga.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error in get_saga_status: {str(e)}")
        return jsonify({'error': f'Erreur interne: {str(e)}'}), 500

@app.route('/api/saga/<order_id>/compensate', methods=['POST'])
def compensate_saga(order_id: str):
    """Endpoint pour déclencher manuellement les compensations"""
    try:
        saga = active_sagas.get(order_id)
        if not saga:
            return jsonify({'error': 'Saga non trouvée'}), 404
        
        orchestrator._execute_compensations(saga)
        return jsonify({'message': 'Compensations exécutées'}), 200
        
    except Exception as e:
        logger.error(f"Error in compensate_saga: {str(e)}")
        return jsonify({'error': f'Erreur interne: {str(e)}'}), 500

@app.route('/metrics', methods=['GET'])
def metrics():
    """Endpoint pour les métriques Prometheus"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False) 