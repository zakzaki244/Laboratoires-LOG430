from flask import Blueprint, request, jsonify
from application.user_service import UserService
from infrastructure.user_repository import UserRepository
from utils.jwt_utils import jwt_required, role_required

bp = Blueprint('users', __name__)
user_service = UserService(UserRepository())

@bp.route('/register', methods=['POST'])
def register():
    return jsonify(*user_service.register(request.json))

@bp.route('/login', methods=['POST'])
def login():
    result, status = user_service.login(request.json)
    return jsonify(result), status

@bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required
def get_user(user_id):
    return jsonify(*user_service.get_user(user_id))

@bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required
def update_user(user_id):
    return jsonify(*user_service.update_user(user_id, request.json))

@bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required
@role_required(['admin'])
def delete_user(user_id):
    return jsonify(*user_service.delete_user(user_id))

@bp.route('/users', methods=['GET'])
@jwt_required
@role_required(['admin'])
def list_users():
    return jsonify(*user_service.list_users())