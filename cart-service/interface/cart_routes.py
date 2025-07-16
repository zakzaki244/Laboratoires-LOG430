from flask import Blueprint, request, jsonify, g
from application.cart_service import CartService
from infrastructure.cart_repository import CartRepository, CartItemRepository
from utils.jwt_utils import jwt_required, role_required

bp = Blueprint('cart', __name__)
cart_service = CartService(CartRepository(), CartItemRepository())

@bp.route('/cart', methods=['GET'])
@jwt_required
def get_cart():
    user_id = getattr(g, 'user', {}).get('user_id')
    store_id = request.args.get('store_id')
    if not store_id:
        return {'message': "ID du magasin requis"}, 400
    return jsonify(*cart_service.get_cart(user_id, int(store_id)))

@bp.route('/cart/items', methods=['POST'])
@jwt_required
def add_item():
    user_id = getattr(g, 'user', {}).get('user_id')
    data = request.json or {}
    store_id = data.get('store_id')
    if not store_id:
        return {'message': "ID du magasin requis"}, 400
    return jsonify(*cart_service.add_item(user_id, store_id, data))

@bp.route('/cart/items/<int:product_id>', methods=['PUT'])
@jwt_required
def update_item_quantity(product_id):
    user_id = getattr(g, 'user', {}).get('user_id')
    data = request.json or {}
    store_id = data.get('store_id')
    quantity = data.get('quantity')
    if not store_id or quantity is None:
        return {'message': "ID du magasin et quantité requis"}, 400
    return jsonify(*cart_service.update_item_quantity(user_id, store_id, product_id, quantity))

@bp.route('/cart/items/<int:product_id>', methods=['DELETE'])
@jwt_required
def remove_item(product_id):
    user_id = getattr(g, 'user', {}).get('user_id')
    store_id = request.args.get('store_id')
    if not store_id:
        return {'message': "ID du magasin requis"}, 400
    return jsonify(*cart_service.remove_item(user_id, int(store_id), product_id))

@bp.route('/cart', methods=['DELETE'])
@jwt_required
def clear_cart():
    user_id = getattr(g, 'user', {}).get('user_id')
    store_id = request.args.get('store_id')
    if not store_id:
        return {'message': "ID du magasin requis"}, 400
    return jsonify(*cart_service.clear_cart(user_id, int(store_id)))