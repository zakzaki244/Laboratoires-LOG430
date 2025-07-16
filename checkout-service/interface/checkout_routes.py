from flask import Blueprint, request, jsonify, g
from application.checkout_service import CheckoutService
from infrastructure.checkout_repository import CheckoutRepository
from utils.jwt_utils import jwt_required, role_required

bp = Blueprint('checkout', __name__)
checkout_service = CheckoutService(CheckoutRepository())

@bp.route('/checkout', methods=['POST'])
@jwt_required
def process_checkout():
    user_id = getattr(g, 'user', {}).get('user_id')
    data = request.json or {}
    store_id = data.get('store_id')
    payment_data = data.get('payment_data', {})
    
    if not store_id or not payment_data:
        return {'message': "ID du magasin et données de paiement requis"}, 400
    
    # Ajouter le token JWT aux données de paiement
    payment_data['token'] = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    return jsonify(*checkout_service.process_checkout(user_id, store_id, payment_data))

@bp.route('/checkout/<int:checkout_id>', methods=['GET'])
@jwt_required
def get_checkout(checkout_id):
    return jsonify(*checkout_service.get_checkout(checkout_id))

@bp.route('/checkout/history', methods=['GET'])
@jwt_required
def get_checkout_history():
    user_id = getattr(g, 'user', {}).get('user_id')
    return jsonify(*checkout_service.get_user_checkouts(user_id))