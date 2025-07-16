from flask import Blueprint, request, jsonify, g
from services.service_discovery import ServiceDiscovery
from utils.jwt_utils import jwt_required, role_required

bp = Blueprint('gateway', __name__)

# Routes publiques (pas d'authentification)
@bp.route('/auth/register', methods=['POST'])
def register():
    service_url = ServiceDiscovery.get_service_url('customer')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'POST', '/register',
        headers={'Content-Type': 'application/json'},
        json_data=request.json
    )
    return jsonify(response_json), status_code

@bp.route('/auth/login', methods=['POST'])
def login():
    service_url = ServiceDiscovery.get_service_url('customer')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'POST', '/login',
        headers={'Content-Type': 'application/json'},
        json_data=request.json
    )
    return jsonify(response_json), status_code

# Routes protégées - Customer Service
@bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required
def get_user(user_id):
    service_url = ServiceDiscovery.get_service_url('customer')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'GET', f'/users/{user_id}',
        headers=dict(request.headers)
    )
    return jsonify(response_json), status_code

@bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required
def update_user(user_id):
    service_url = ServiceDiscovery.get_service_url('customer')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'PUT', f'/users/{user_id}',
        headers=dict(request.headers),
        json_data=request.json
    )
    return jsonify(response_json), status_code

@bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required
@role_required(['admin'])
def delete_user(user_id):
    service_url = ServiceDiscovery.get_service_url('customer')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'DELETE', f'/users/{user_id}',
        headers=dict(request.headers)
    )
    return jsonify(response_json), status_code

@bp.route('/users', methods=['GET'])
@jwt_required
@role_required(['admin'])
def list_users():
    service_url = ServiceDiscovery.get_service_url('customer')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'GET', '/users',
        headers=dict(request.headers)
    )
    return jsonify(response_json), status_code

# Routes protégées - Product Service
@bp.route('/products', methods=['POST'])
@jwt_required
@role_required(['admin', 'gestionnaire', 'responsable_produit'])
def create_product():

    service_url = ServiceDiscovery.get_service_url('product')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'POST', '/products',
        headers=dict(request.headers),
        json_data=request.json
    )
    return jsonify(response_json), status_code

@bp.route('/products/<int:product_id>', methods=['GET'])
@jwt_required
def get_product(product_id):

    service_url = ServiceDiscovery.get_service_url('product')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'GET', f'/products/{product_id}',
        headers=dict(request.headers)
    )
    return jsonify(response_json), status_code

@bp.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required
@role_required(['admin', 'gestionnaire', 'responsable_produit'])
def update_product(product_id):
    service_url = ServiceDiscovery.get_service_url('product')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'PUT', f'/products/{product_id}',
        headers=dict(request.headers),
        json_data=request.json
    )
    return jsonify(response_json), status_code

@bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required
@role_required(['admin', 'gestionnaire', 'responsable_produit'])
def delete_product(product_id):
    service_url = ServiceDiscovery.get_service_url('product')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'DELETE', f'/products/{product_id}',
        headers=dict(request.headers)
    )
    return jsonify(response_json), status_code

@bp.route('/products', methods=['GET'])
@jwt_required
def list_products():
    service_url = ServiceDiscovery.get_service_url('product')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'GET', '/products',
        headers=dict(request.headers),
        params=dict(request.args)
    )
    return jsonify(response_json), status_code

@bp.route('/products/<int:product_id>/stock', methods=['PATCH'])
@jwt_required
@role_required(['admin', 'gestionnaire', 'responsable_logistique'])
def update_stock(product_id):
    service_url = ServiceDiscovery.get_service_url('product')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'PATCH', f'/products/{product_id}/stock',
        headers=dict(request.headers),
        json_data=request.json
    )
    return jsonify(response_json), status_code

# Routes protégées - Store Service
@bp.route('/stores', methods=['POST'])
@jwt_required
@role_required(['admin', 'gestionnaire'])
def create_store():
    service_url = ServiceDiscovery.get_service_url('store')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'POST', '/stores',
        headers=dict(request.headers),
        json_data=request.json
    )
    return jsonify(response_json), status_code

@bp.route('/stores/<int:store_id>', methods=['GET'])
@jwt_required
def get_store(store_id):
    service_url = ServiceDiscovery.get_service_url('store')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'GET', f'/stores/{store_id}',
        headers=dict(request.headers)
    )
    return jsonify(response_json), status_code

@bp.route('/stores/<int:store_id>', methods=['PUT'])
@jwt_required
@role_required(['admin', 'gestionnaire'])
def update_store(store_id):
    service_url = ServiceDiscovery.get_service_url('store')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'PUT', f'/stores/{store_id}',
        headers=dict(request.headers),
        json_data=request.json
    )
    return jsonify(response_json), status_code

@bp.route('/stores/<int:store_id>', methods=['DELETE'])
@jwt_required
@role_required(['admin', 'gestionnaire'])
def delete_store(store_id):
    service_url = ServiceDiscovery.get_service_url('store')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'DELETE', f'/stores/{store_id}',
        headers=dict(request.headers)
    )
    return jsonify(response_json), status_code

@bp.route('/stores', methods=['GET'])
@jwt_required
def list_stores():
    service_url = ServiceDiscovery.get_service_url('store')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'GET', '/stores',
        headers=dict(request.headers),
        params=dict(request.args)
    )
    return jsonify(response_json), status_code

# Routes protégées - Sales Service
@bp.route('/sales', methods=['POST'])
@jwt_required
@role_required(['gestionnaire', 'admin', 'responsable_logistique'])
def create_sale():
    service_url = ServiceDiscovery.get_service_url('sales')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'POST', '/sales',
        headers=dict(request.headers),
        json_data=request.json
    )
    return jsonify(response_json), status_code

@bp.route('/sales/<int:sale_id>', methods=['GET'])
@jwt_required
@role_required(['gestionnaire', 'admin', 'responsable_logistique'])
def get_sale(sale_id):
    service_url = ServiceDiscovery.get_service_url('sales')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'GET', f'/sales/{sale_id}',
        headers=dict(request.headers)
    )
    return jsonify(response_json), status_code

@bp.route('/sales/<int:sale_id>', methods=['DELETE'])
@jwt_required
@role_required(['admin', 'gestionnaire'])
def delete_sale(sale_id):
    service_url = ServiceDiscovery.get_service_url('sales')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'DELETE', f'/sales/{sale_id}',
        headers=dict(request.headers)
    )
    return jsonify(response_json), status_code

@bp.route('/sales', methods=['GET'])
@jwt_required
@role_required(['gestionnaire', 'admin', 'responsable_logistique'])
def list_sales():
    service_url = ServiceDiscovery.get_service_url('sales')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'GET', '/sales',
        headers=dict(request.headers)
    )
    return jsonify(response_json), status_code

@bp.route('/sales/report', methods=['GET'])
@jwt_required
@role_required(['gestionnaire', 'admin', 'responsable_logistique'])
def generate_sales_report():
    service_url = ServiceDiscovery.get_service_url('sales')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'GET', '/sales/report',
        headers=dict(request.headers),
        params=dict(request.args)
    )
    return jsonify(response_json), status_code

# Routes protégées - Cart Service
@bp.route('/cart', methods=['GET'])
@jwt_required
def get_cart():
    service_url = ServiceDiscovery.get_service_url('cart')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'GET', '/cart',
        headers=dict(request.headers),
        params=dict(request.args)
    )
    return jsonify(response_json), status_code

@bp.route('/cart/items', methods=['POST'])
@jwt_required
def add_cart_item():
    service_url = ServiceDiscovery.get_service_url('cart')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'POST', '/cart/items',
        headers=dict(request.headers),
        json_data=request.json
    )
    return jsonify(response_json), status_code

@bp.route('/cart/items/<int:product_id>', methods=['PUT'])
@jwt_required
def update_cart_item(product_id):
    service_url = ServiceDiscovery.get_service_url('cart')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'PUT', f'/cart/items/{product_id}',
        headers=dict(request.headers),
        json_data=request.json
    )
    return jsonify(response_json), status_code

@bp.route('/cart/items/<int:product_id>', methods=['DELETE'])
@jwt_required
def remove_cart_item(product_id):
    service_url = ServiceDiscovery.get_service_url('cart')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'DELETE', f'/cart/items/{product_id}',
        headers=dict(request.headers),
        params=dict(request.args)
    )
    return jsonify(response_json), status_code

@bp.route('/cart', methods=['DELETE'])
@jwt_required
def clear_cart():
    service_url = ServiceDiscovery.get_service_url('cart')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'DELETE', '/cart',
        headers=dict(request.headers),
        params=dict(request.args)
    )
    return jsonify(response_json), status_code

# Routes protégées - Checkout Service
@bp.route('/checkout', methods=['POST'])
@jwt_required
def process_checkout():
    service_url = ServiceDiscovery.get_service_url('checkout')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'POST', '/checkout',
        headers=dict(request.headers),
        json_data=request.json
    )
    return jsonify(response_json), status_code

@bp.route('/checkout/<int:checkout_id>', methods=['GET'])
@jwt_required
def get_checkout(checkout_id):
    service_url = ServiceDiscovery.get_service_url('checkout')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'GET', f'/checkout/{checkout_id}',
        headers=dict(request.headers)
    )
    return jsonify(response_json), status_code

@bp.route('/checkout/history', methods=['GET'])
@jwt_required
def get_checkout_history():
    service_url = ServiceDiscovery.get_service_url('checkout')
    response_json, status_code = ServiceDiscovery.forward_request(
        service_url, 'GET', '/checkout/history',
        headers=dict(request.headers)
    )
    return jsonify(response_json), status_code