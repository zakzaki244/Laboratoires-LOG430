from flask import Blueprint, request, jsonify
from application.sale_service import SaleService
from infrastructure.sale_repository import SaleRepository, SaleItemRepository
from utils.jwt_utils import jwt_required, role_required

bp = Blueprint('sales', __name__)
sale_service = SaleService(SaleRepository(), SaleItemRepository())

@bp.route('/sales', methods=['POST'])
@jwt_required
@role_required(['gestionnaire', 'admin', 'responsable_logistique'])
def create_sale():
    return jsonify(*sale_service.create_sale(request.json or {}))

@bp.route('/sales/<int:sale_id>', methods=['GET'])
@jwt_required
@role_required(['gestionnaire', 'admin', 'responsable_logistique'])
def get_sale(sale_id):
    return jsonify(*sale_service.get_sale(sale_id))

@bp.route('/sales/<int:sale_id>', methods=['DELETE'])
@jwt_required
@role_required(['admin', 'gestionnaire'])
def delete_sale(sale_id):
    return jsonify(*sale_service.delete_sale(sale_id))

@bp.route('/sales', methods=['GET'])
@jwt_required
@role_required(['gestionnaire', 'admin', 'responsable_logistique'])
def list_sales():
    return jsonify(*sale_service.list_sales())

@bp.route('/sales/client/<int:client_id>', methods=['GET'])
@jwt_required
@role_required(['gestionnaire', 'admin', 'responsable_logistique'])
def get_sales_by_client(client_id):
    return jsonify(*sale_service.get_sales_by_client(client_id))

@bp.route('/sales/report', methods=['GET'])
@jwt_required
@role_required(['gestionnaire', 'admin', 'responsable_logistique'])
def generate_report():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    return jsonify(*sale_service.generate_report(start_date, end_date))