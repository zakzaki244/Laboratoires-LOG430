from flask import Blueprint, request, jsonify
from application.product_service import ProductService
from infrastructure.product_repository import ProductRepository
from utils.jwt_utils import jwt_required, role_required

bp = Blueprint('products', __name__)
product_service = ProductService(ProductRepository())

@bp.route('/products', methods=['POST'])
@jwt_required
@role_required(['admin', 'gestionnaire', 'responsable_produit'])
def create_product():
    return jsonify(*product_service.create_product(request.json or {}))

@bp.route('/products/<int:product_id>', methods=['GET'])
@jwt_required
def get_product(product_id):
    return jsonify(*product_service.get_product(product_id))

@bp.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required
@role_required(['admin', 'gestionnaire', 'responsable_produit'])
def update_product(product_id):
    return jsonify(*product_service.update_product(product_id, request.json or {}))

@bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required
@role_required(['admin', 'gestionnaire', 'responsable_produit'])
def delete_product(product_id):
    return jsonify(*product_service.delete_product(product_id))

@bp.route('/products', methods=['GET'])
@jwt_required
def list_products():
    query = request.args.get('q')
    store_id = request.args.get('store_id')
    if store_id:
        store_id = int(store_id)
    
    if query:
        return jsonify(*product_service.search_products(query, store_id))
    return jsonify(*product_service.list_products(store_id))

@bp.route('/products/<int:product_id>/stock', methods=['PATCH'])
@jwt_required
@role_required(['admin', 'gestionnaire', 'responsable_logistique'])
def update_stock(product_id):
    data = request.json or {}
    return jsonify(*product_service.update_stock(product_id, data.get('quantity_stock')))