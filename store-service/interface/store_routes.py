from flask import Blueprint, request, jsonify
from application.store_service import StoreService
from infrastructure.store_repository import StoreRepository
from utils.jwt_utils import jwt_required, role_required

bp = Blueprint('stores', __name__)
store_service = StoreService(StoreRepository())

@bp.route('/stores', methods=['POST'])
@jwt_required
@role_required(['admin', 'gestionnaire'])
def create_store():
    return jsonify(*store_service.create_store(request.json or {}))

@bp.route('/stores/<int:store_id>', methods=['GET'])
@jwt_required
def get_store(store_id):
    return jsonify(*store_service.get_store(store_id))

@bp.route('/stores/<int:store_id>', methods=['PUT'])
@jwt_required
@role_required(['admin', 'gestionnaire'])
def update_store(store_id):
    return jsonify(*store_service.update_store(store_id, request.json or {}))

@bp.route('/stores/<int:store_id>', methods=['DELETE'])
@jwt_required
@role_required(['admin', 'gestionnaire'])
def delete_store(store_id):
    return jsonify(*store_service.delete_store(store_id))

@bp.route('/stores', methods=['GET'])
@jwt_required
def list_stores():
    query = request.args.get('q')
    if query:
        return jsonify(*store_service.search_stores(query))
    return jsonify(*store_service.list_stores())