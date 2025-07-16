# from flask import Flask, request, jsonify, g
# from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime
# import jwt
# import os
# from functools import wraps

# # Configuration
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://logistics_user:logistics_pass@logistics-db:5432/logistics_db')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'logistics-secret-key')

# db = SQLAlchemy(app)

# # ===== DOMAIN MODELS =====

# class RestockRequest(db.Model):
#     """Modèle de domaine pour les demandes de réapprovisionnement"""
#     __tablename__ = 'restock_requests'
    
#     id = db.Column(db.Integer, primary_key=True)
#     store_id = db.Column(db.Integer, nullable=False)
#     product_id = db.Column(db.Integer, nullable=False)
#     quantity_requested = db.Column(db.Integer, nullable=False)
#     priority = db.Column(db.String(20), nullable=False, default='medium')  # low, medium, high
#     status = db.Column(db.String(20), nullable=False, default='pending')  # pending, approved, rejected, completed
#     request_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#     approved_date = db.Column(db.DateTime)
#     completed_date = db.Column(db.DateTime)
#     notes = db.Column(db.Text)
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'store_id': self.store_id,
#             'product_id': self.product_id,
#             'quantity_requested': self.quantity_requested,
#             'priority': self.priority,
#             'status': self.status,
#             'request_date': self.request_date.isoformat() if self.request_date else None,
#             'approved_date': self.approved_date.isoformat() if self.approved_date else None,
#             'completed_date': self.completed_date.isoformat() if self.completed_date else None,
#             'notes': self.notes
#         }

# class InventoryMovement(db.Model):
#     """Modèle de domaine pour les mouvements d'inventaire"""
#     __tablename__ = 'inventory_movements'
    
#     id = db.Column(db.Integer, primary_key=True)
#     product_id = db.Column(db.Integer, nullable=False)
#     from_store_id = db.Column(db.Integer)  # None si depuis le centre logistique
#     to_store_id = db.Column(db.Integer, nullable=False)
#     quantity = db.Column(db.Integer, nullable=False)
#     movement_type = db.Column(db.String(20), nullable=False)  # restock, transfer, return
#     movement_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#     reference_id = db.Column(db.Integer)  # ID de la demande de réapprovisionnement
#     notes = db.Column(db.Text)
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'product_id': self.product_id,
#             'from_store_id': self.from_store_id,
#             'to_store_id': self.to_store_id,
#             'quantity': self.quantity,
#             'movement_type': self.movement_type,
#             'movement_date': self.movement_date.isoformat() if self.movement_date else None,
#             'reference_id': self.reference_id,
#             'notes': self.notes
#         }

# class WarehouseInventory(db.Model):
#     """Modèle de domaine pour l'inventaire du centre logistique"""
#     __tablename__ = 'warehouse_inventory'
    
#     id = db.Column(db.Integer, primary_key=True)
#     product_id = db.Column(db.Integer, nullable=False, unique=True)
#     quantity_available = db.Column(db.Integer, nullable=False, default=0)
#     quantity_reserved = db.Column(db.Integer, nullable=False, default=0)
#     last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'product_id': self.product_id,
#             'quantity_available': self.quantity_available,
#             'quantity_reserved': self.quantity_reserved,
#             'total_quantity': self.quantity_available + self.quantity_reserved,
#             'last_updated': self.last_updated.isoformat() if self.last_updated else None
#         }

# class DeliverySchedule(db.Model):
#     """Modèle de domaine pour les plannings de livraison"""
#     __tablename__ = 'delivery_schedules'
    
#     id = db.Column(db.Integer, primary_key=True)
#     store_id = db.Column(db.Integer, nullable=False)
#     scheduled_date = db.Column(db.DateTime, nullable=False)
#     status = db.Column(db.String(20), nullable=False, default='scheduled')  # scheduled, in_progress, completed, cancelled
#     driver_name = db.Column(db.String(100))
#     vehicle_id = db.Column(db.String(50))
#     notes = db.Column(db.Text)
#     created_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'store_id': self.store_id,
#             'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
#             'status': self.status,
#             'driver_name': self.driver_name,
#             'vehicle_id': self.vehicle_id,
#             'notes': self.notes,
#             'created_date': self.created_date.isoformat() if self.created_date else None
#         }

# # ===== REPOSITORIES =====

# class RestockRequestRepository:
#     """Repository pour les demandes de réapprovisionnement"""
    
#     @staticmethod
#     def create(store_id, product_id, quantity_requested, priority='medium', notes=None):
#         request = RestockRequest()
#         request.store_id = store_id
#         request.product_id = product_id
#         request.quantity_requested = quantity_requested
#         request.priority = priority
#         request.notes = notes
#         db.session.add(request)
#         db.session.commit()
#         return request
    
#     @staticmethod
#     def get_by_id(request_id):
#         return RestockRequest.query.get(request_id)
    
#     @staticmethod
#     def get_all(status=None, store_id=None):
#         query = RestockRequest.query
#         if status:
#             query = query.filter(RestockRequest.status == status)
#         if store_id:
#             query = query.filter(RestockRequest.store_id == store_id)
#         return query.order_by(RestockRequest.request_date.desc()).all()
    
#     @staticmethod
#     def update_status(request_id, status, notes=None):
#         request = RestockRequest.query.get(request_id)
#         if request:
#             request.status = status
#             if status == 'approved':
#                 request.approved_date = datetime.utcnow()
#             elif status == 'completed':
#                 request.completed_date = datetime.utcnow()
#             if notes:
#                 request.notes = notes
#             db.session.commit()
#         return request

# class InventoryMovementRepository:
#     """Repository pour les mouvements d'inventaire"""
    
#     @staticmethod
#     def create(product_id, to_store_id, quantity, movement_type, from_store_id=None, reference_id=None, notes=None):
#         movement = InventoryMovement()
#         movement.product_id = product_id
#         movement.from_store_id = from_store_id
#         movement.to_store_id = to_store_id
#         movement.quantity = quantity
#         movement.movement_type = movement_type
#         movement.reference_id = reference_id
#         movement.notes = notes
#         db.session.add(movement)
#         db.session.commit()
#         return movement
    
#     @staticmethod
#     def get_by_id(movement_id):
#         return InventoryMovement.query.get(movement_id)
    
#     @staticmethod
#     def get_by_product(product_id):
#         return InventoryMovement.query.filter_by(product_id=product_id).order_by(InventoryMovement.movement_date.desc()).all()
    
#     @staticmethod
#     def get_by_store(store_id):
#         return InventoryMovement.query.filter(
#             (InventoryMovement.from_store_id == store_id) | 
#             (InventoryMovement.to_store_id == store_id)
#         ).order_by(InventoryMovement.movement_date.desc()).all()

# class WarehouseInventoryRepository:
#     """Repository pour l'inventaire du centre logistique"""
    
#     @staticmethod
#     def get_by_product(product_id):
#         return WarehouseInventory.query.filter_by(product_id=product_id).first()
    
#     @staticmethod
#     def get_all():
#         return WarehouseInventory.query.all()
    
#     @staticmethod
#     def update_quantity(product_id, quantity_available, quantity_reserved=0):
#         inventory = WarehouseInventory.query.filter_by(product_id=product_id).first()
#         if inventory:
#             inventory.quantity_available = quantity_available
#             inventory.quantity_reserved = quantity_reserved
#             inventory.last_updated = datetime.utcnow()
#         else:
#             inventory = WarehouseInventory()
#             inventory.product_id = product_id
#             inventory.quantity_available = quantity_available
#             inventory.quantity_reserved = quantity_reserved
#             db.session.add(inventory)
#         db.session.commit()
#         return inventory

# class DeliveryScheduleRepository:
#     """Repository pour les plannings de livraison"""
    
#     @staticmethod
#     def create(store_id, scheduled_date, driver_name=None, vehicle_id=None, notes=None):
#         schedule = DeliverySchedule()
#         schedule.store_id = store_id
#         schedule.scheduled_date = scheduled_date
#         schedule.driver_name = driver_name
#         schedule.vehicle_id = vehicle_id
#         schedule.notes = notes
#         db.session.add(schedule)
#         db.session.commit()
#         return schedule
    
#     @staticmethod
#     def get_by_id(schedule_id):
#         return DeliverySchedule.query.get(schedule_id)
    
#     @staticmethod
#     def get_all(status=None, store_id=None):
#         query = DeliverySchedule.query
#         if status:
#             query = query.filter(DeliverySchedule.status == status)
#         if store_id:
#             query = query.filter(DeliverySchedule.store_id == store_id)
#         return query.order_by(DeliverySchedule.scheduled_date).all()
    
#     @staticmethod
#     def update_status(schedule_id, status, notes=None):
#         schedule = DeliverySchedule.query.get(schedule_id)
#         if schedule:
#             schedule.status = status
#             if notes:
#                 schedule.notes = notes
#             db.session.commit()
#         return schedule

# # ===== SERVICES =====

# class LogisticsService:
#     """Service de logistique - logique métier"""
    
#     def __init__(self):
#         self.restock_repo = RestockRequestRepository()
#         self.movement_repo = InventoryMovementRepository()
#         self.warehouse_repo = WarehouseInventoryRepository()
#         self.delivery_repo = DeliveryScheduleRepository()
    
#     def create_restock_request(self, store_id, product_id, quantity_requested, priority='medium', notes=None):
#         """Créer une demande de réapprovisionnement"""
#         return self.restock_repo.create(store_id, product_id, quantity_requested, priority, notes)
    
#     def approve_restock_request(self, request_id, notes=None):
#         """Approuver une demande de réapprovisionnement"""
#         request = self.restock_repo.update_status(request_id, 'approved', notes)
#         if request:
#             # Créer un mouvement d'inventaire
#             self.movement_repo.create(
#                 product_id=request.product_id,
#                 to_store_id=request.store_id,
#                 quantity=request.quantity_requested,
#                 movement_type='restock',
#                 reference_id=request.id,
#                 notes=f"Réapprovisionnement approuvé - Demande #{request.id}"
#             )
#         return request
    
#     def reject_restock_request(self, request_id, notes=None):
#         """Rejeter une demande de réapprovisionnement"""
#         return self.restock_repo.update_status(request_id, 'rejected', notes)
    
#     def complete_restock_request(self, request_id, notes=None):
#         """Marquer une demande comme complétée"""
#         return self.restock_repo.update_status(request_id, 'completed', notes)
    
#     def get_pending_requests(self, store_id=None):
#         """Obtenir les demandes en attente"""
#         return self.restock_repo.get_all(status='pending', store_id=store_id)
    
#     def get_warehouse_inventory(self):
#         """Obtenir l'inventaire du centre logistique"""
#         return self.warehouse_repo.get_all()
    
#     def update_warehouse_inventory(self, product_id, quantity_available, quantity_reserved=0):
#         """Mettre à jour l'inventaire du centre logistique"""
#         return self.warehouse_repo.update_quantity(product_id, quantity_available, quantity_reserved)
    
#     def create_delivery_schedule(self, store_id, scheduled_date, driver_name=None, vehicle_id=None, notes=None):
#         """Créer un planning de livraison"""
#         return self.delivery_repo.create(store_id, scheduled_date, driver_name, vehicle_id, notes)
    
#     def get_delivery_schedules(self, status=None, store_id=None):
#         """Obtenir les plannings de livraison"""
#         return self.delivery_repo.get_all(status, store_id)
    
#     def update_delivery_status(self, schedule_id, status, notes=None):
#         """Mettre à jour le statut d'une livraison"""
#         return self.delivery_repo.update_status(schedule_id, status, notes)

# # ===== JWT UTILS =====

# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None
#         if 'Authorization' in request.headers:
#             token = request.headers['Authorization'].split(" ")[1]
        
#         if not token:
#             return jsonify({'message': 'Token manquant'}), 401
        
#         try:
#             data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
#             g.current_user = data
#         except:
#             return jsonify({'message': 'Token invalide'}), 401
        
#         return f(*args, **kwargs)
#     return decorated

# def role_required(required_role):
#     def decorator(f):
#         @wraps(f)
#         def decorated(*args, **kwargs):
#             if not hasattr(g, 'current_user'):
#                 return jsonify({'message': 'Utilisateur non authentifié'}), 401
            
#             user_role = g.current_user.get('role')
#             if user_role != required_role and user_role != 'admin':
#                 return jsonify({'message': 'Permissions insuffisantes'}), 403
            
#             return f(*args, **kwargs)
#         return decorated
#     return decorator

# # ===== ROUTES =====

# logistics_service = LogisticsService()

# @app.route('/health', methods=['GET'])
# def health_check():
#     return jsonify({'status': 'healthy', 'service': 'logistics'})

# # Routes pour les demandes de réapprovisionnement
# @app.route('/restock-requests', methods=['POST'])
# @token_required
# @role_required('logistics')
# def create_restock_request():
#     data = request.get_json()
    
#     required_fields = ['store_id', 'product_id', 'quantity_requested']
#     for field in required_fields:
#         if field not in data:
#             return jsonify({'message': f'Champ requis manquant: {field}'}), 400
    
#     try:
#         request_obj = logistics_service.create_restock_request(
#             store_id=data['store_id'],
#             product_id=data['product_id'],
#             quantity_requested=data['quantity_requested'],
#             priority=data.get('priority', 'medium'),
#             notes=data.get('notes')
#         )
#         return jsonify({
#             'message': 'Demande de réapprovisionnement créée avec succès',
#             'request': request_obj.to_dict()
#         }), 201
#     except Exception as e:
#         return jsonify({'message': f'Erreur lors de la création: {str(e)}'}), 500

# @app.route('/restock-requests', methods=['GET'])
# @token_required
# @role_required('logistics')
# def get_restock_requests():
#     status = request.args.get('status')
#     store_id = request.args.get('store_id', type=int)
    
#     requests = logistics_service.get_pending_requests(store_id) if status == 'pending' else logistics_service.restock_repo.get_all(status, store_id)
    
#     return jsonify({
#         'requests': [req.to_dict() for req in requests]
#     })

# @app.route('/restock-requests/<int:request_id>/approve', methods=['PUT'])
# @token_required
# @role_required('logistics')
# def approve_restock_request(request_id):
#     data = request.get_json()
#     notes = data.get('notes') if data else None
    
#     try:
#         request_obj = logistics_service.approve_restock_request(request_id, notes)
#         if request_obj:
#             return jsonify({
#                 'message': 'Demande de réapprovisionnement approuvée',
#                 'request': request_obj.to_dict()
#             })
#         else:
#             return jsonify({'message': 'Demande non trouvée'}), 404
#     except Exception as e:
#         return jsonify({'message': f'Erreur lors de l\'approbation: {str(e)}'}), 500

# @app.route('/restock-requests/<int:request_id>/reject', methods=['PUT'])
# @token_required
# @role_required('logistics')
# def reject_restock_request(request_id):
#     data = request.get_json()
#     notes = data.get('notes') if data else None
    
#     try:
#         request_obj = logistics_service.reject_restock_request(request_id, notes)
#         if request_obj:
#             return jsonify({
#                 'message': 'Demande de réapprovisionnement rejetée',
#                 'request': request_obj.to_dict()
#             })
#         else:
#             return jsonify({'message': 'Demande non trouvée'}), 404
#     except Exception as e:
#         return jsonify({'message': f'Erreur lors du rejet: {str(e)}'}), 500

# @app.route('/restock-requests/<int:request_id>/complete', methods=['PUT'])
# @token_required
# @role_required('logistics')
# def complete_restock_request(request_id):
#     data = request.get_json()
#     notes = data.get('notes') if data else None
    
#     try:
#         request_obj = logistics_service.complete_restock_request(request_id, notes)
#         if request_obj:
#             return jsonify({
#                 'message': 'Demande de réapprovisionnement complétée',
#                 'request': request_obj.to_dict()
#             })
#         else:
#             return jsonify({'message': 'Demande non trouvée'}), 404
#     except Exception as e:
#         return jsonify({'message': f'Erreur lors de la finalisation: {str(e)}'}), 500

# # Routes pour l'inventaire du centre logistique
# @app.route('/warehouse-inventory', methods=['GET'])
# @token_required
# @role_required('logistics')
# def get_warehouse_inventory():
#     inventory = logistics_service.get_warehouse_inventory()
#     return jsonify({
#         'inventory': [item.to_dict() for item in inventory]
#     })

# @app.route('/warehouse-inventory/<int:product_id>', methods=['PUT'])
# @token_required
# @role_required('logistics')
# def update_warehouse_inventory(product_id):
#     data = request.get_json()
    
#     if 'quantity_available' not in data:
#         return jsonify({'message': 'Champ requis manquant: quantity_available'}), 400
    
#     try:
#         inventory = logistics_service.update_warehouse_inventory(
#             product_id=product_id,
#             quantity_available=data['quantity_available'],
#             quantity_reserved=data.get('quantity_reserved', 0)
#         )
#         return jsonify({
#             'message': 'Inventaire mis à jour avec succès',
#             'inventory': inventory.to_dict()
#         })
#     except Exception as e:
#         return jsonify({'message': f'Erreur lors de la mise à jour: {str(e)}'}), 500

# # Routes pour les plannings de livraison
# @app.route('/delivery-schedules', methods=['POST'])
# @token_required
# @role_required('logistics')
# def create_delivery_schedule():
#     data = request.get_json()
    
#     required_fields = ['store_id', 'scheduled_date']
#     for field in required_fields:
#         if field not in data:
#             return jsonify({'message': f'Champ requis manquant: {field}'}), 400
    
#     try:
#         scheduled_date = datetime.fromisoformat(data['scheduled_date'].replace('Z', '+00:00'))
#         schedule = logistics_service.create_delivery_schedule(
#             store_id=data['store_id'],
#             scheduled_date=scheduled_date,
#             driver_name=data.get('driver_name'),
#             vehicle_id=data.get('vehicle_id'),
#             notes=data.get('notes')
#         )
#         return jsonify({
#             'message': 'Planning de livraison créé avec succès',
#             'schedule': schedule.to_dict()
#         }), 201
#     except Exception as e:
#         return jsonify({'message': f'Erreur lors de la création: {str(e)}'}), 500

# @app.route('/delivery-schedules', methods=['GET'])
# @token_required
# @role_required('logistics')
# def get_delivery_schedules():
#     status = request.args.get('status')
#     store_id = request.args.get('store_id', type=int)
    
#     schedules = logistics_service.get_delivery_schedules(status, store_id)
#     return jsonify({
#         'schedules': [schedule.to_dict() for schedule in schedules]
#     })

# @app.route('/delivery-schedules/<int:schedule_id>/status', methods=['PUT'])
# @token_required
# @role_required('logistics')
# def update_delivery_status(schedule_id):
#     data = request.get_json()
    
#     if 'status' not in data:
#         return jsonify({'message': 'Champ requis manquant: status'}), 400
    
#     try:
#         schedule = logistics_service.update_delivery_status(
#             schedule_id, 
#             data['status'], 
#             data.get('notes')
#         )
#         if schedule:
#             return jsonify({
#                 'message': 'Statut de livraison mis à jour',
#                 'schedule': schedule.to_dict()
#             })
#         else:
#             return jsonify({'message': 'Planning non trouvé'}), 404
#     except Exception as e:
#         return jsonify({'message': f'Erreur lors de la mise à jour: {str(e)}'}), 500

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(host='0.0.0.0', port=5007, debug=True) 