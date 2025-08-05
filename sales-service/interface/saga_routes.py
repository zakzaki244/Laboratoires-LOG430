from flask import Blueprint, request, jsonify
from flask import Blueprint, request, jsonify
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

bp = Blueprint('saga', __name__)

@bp.route('/api/process-payment', methods=['POST'])
def process_payment():
    """Traite le paiement pour une commande"""
    try:
        data = request.get_json()
        if not data or 'order_id' not in data or 'customer_id' not in data or 'amount' not in data:
            return jsonify({'error': 'Données manquantes'}), 400
        
        order_id = data['order_id']
        customer_id = data['customer_id']
        amount = data['amount']
        payment_id = f"pay_{order_id}"
        
        # Simuler le traitement du paiement
        # En production, cela appellerait un service de paiement externe
        payment_success = True  # Simulation - pourrait échouer pour tester
        
        if not payment_success:
            return jsonify({
                'success': False,
                'error': 'Paiement refusé par la banque'
            }), 400
        
        # Créer un enregistrement de paiement
        payment_record = {
            'payment_id': payment_id,
            'order_id': order_id,
            'customer_id': customer_id,
            'amount': amount,
            'status': 'completed',
            'processed_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Payment processed successfully for order {order_id}")
        return jsonify({
            'success': True,
            'payment_id': payment_id,
            'amount': amount,
            'status': 'completed',
            'message': 'Paiement traité avec succès'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in process_payment: {str(e)}")
        return jsonify({'error': f'Erreur interne: {str(e)}'}), 500

@bp.route('/api/confirm-order', methods=['POST'])
def confirm_order():
    """Confirme une commande après paiement réussi"""
    try:
        data = request.get_json()
        if not data or 'order_id' not in data or 'customer_id' not in data or 'items' not in data:
            return jsonify({'error': 'Données manquantes'}), 400
        
        order_id = data['order_id']
        customer_id = data['customer_id']
        items = data['items']
        payment_id = data.get('payment_id')
        
        # Créer la vente dans la base de données
        sale_data = {
            'customer_id': customer_id,
            'total_amount': sum(item.get('price', 0) * item.get('quantity', 1) for item in items),
            'payment_id': payment_id,
            'status': 'confirmed'
        }
        
        # Simuler la création de la vente
        sale_id = f"sale_{order_id}"
        
        # En production, cela créerait réellement la vente dans la base de données
        logger.info(f"Sale created: {sale_id} for order {order_id}")
        
        logger.info(f"Order confirmed successfully: {order_id}")
        return jsonify({
            'success': True,
            'sale_id': sale_id,
            'order_id': order_id,
            'message': 'Commande confirmée avec succès'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in confirm_order: {str(e)}")
        return jsonify({'error': f'Erreur interne: {str(e)}'}), 500

@bp.route('/api/refund-payment', methods=['POST'])
def refund_payment():
    """Rembourse un paiement (compensation)"""
    try:
        data = request.get_json()
        if not data or 'payment_id' not in data:
            return jsonify({'error': 'Données manquantes'}), 400
        
        payment_id = data['payment_id']
        amount = data.get('amount', 0)
        
        # Simuler le remboursement
        # En production, cela appellerait un service de paiement externe
        refund_success = True  # Simulation
        
        if not refund_success:
            return jsonify({
                'success': False,
                'error': 'Échec du remboursement'
            }), 400
        
        # Simuler l'annulation de la vente
        if 'sale_id' in data:
            sale_id = data['sale_id']
            logger.info(f"Sale cancelled: {sale_id}")
        
        logger.info(f"Payment refunded successfully: {payment_id}")
        return jsonify({
            'success': True,
            'payment_id': payment_id,
            'refunded_amount': amount,
            'status': 'refunded',
            'message': 'Paiement remboursé avec succès'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in refund_payment: {str(e)}")
        return jsonify({'error': f'Erreur interne: {str(e)}'}), 500 