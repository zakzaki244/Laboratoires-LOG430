from flask import Blueprint, request, jsonify
from application.product_service import ProductService
from infrastructure.product_repository import ProductRepository
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('saga', __name__)
product_service = ProductService(ProductRepository())

@bp.route('/api/check-stock', methods=['POST'])
def check_stock():
    """Vérifie la disponibilité du stock pour les produits demandés"""
    try:
        data = request.get_json()
        if not data or 'items' not in data:
            return jsonify({'error': 'Données manquantes'}), 400
        
        items = data['items']
        unavailable_items = []
        available_items = []
        
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)
            
            if not product_id:
                continue
                
            # Vérifier le stock du produit
            success, result = product_service.get_product(product_id)
            if not success:
                unavailable_items.append({
                    'product_id': product_id,
                    'reason': 'Produit non trouvé'
                })
                continue
            
            product = result if isinstance(result, dict) else {}
            current_stock = product.get('quantity_stock', 0)
            
            if current_stock >= quantity:
                available_items.append({
                    'product_id': product_id,
                    'available_quantity': current_stock,
                    'requested_quantity': quantity
                })
            else:
                unavailable_items.append({
                    'product_id': product_id,
                    'available_quantity': current_stock,
                    'requested_quantity': quantity,
                    'reason': 'Stock insuffisant'
                })
        
        # Si tous les produits sont disponibles
        if not unavailable_items:
            return jsonify({
                'available': True,
                'available_items': available_items,
                'message': 'Tous les produits sont disponibles'
            }), 200
        else:
            return jsonify({
                'available': False,
                'available_items': available_items,
                'unavailable_items': unavailable_items,
                'message': 'Certains produits ne sont pas disponibles'
            }), 200
            
    except Exception as e:
        logger.error(f"Error in check_stock: {str(e)}")
        return jsonify({'error': f'Erreur interne: {str(e)}'}), 500

@bp.route('/api/reserve-stock', methods=['POST'])
def reserve_stock():
    """Réserve le stock pour une commande"""
    try:
        data = request.get_json()
        if not data or 'order_id' not in data or 'items' not in data:
            return jsonify({'error': 'Données manquantes'}), 400
        
        order_id = data['order_id']
        items = data['items']
        reservation_id = f"res_{order_id}"
        
        # Vérifier d'abord la disponibilité
        unavailable_items = []
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)
            
            if not product_id:
                continue
                
            # Vérifier le stock du produit
            success, result = product_service.get_product(product_id)
            if not success:
                unavailable_items.append({
                    'product_id': product_id,
                    'reason': 'Produit non trouvé'
                })
                continue
            
            product = result if isinstance(result, dict) else {}
            current_stock = product.get('quantity_stock', 0)
            
            if current_stock < quantity:
                unavailable_items.append({
                    'product_id': product_id,
                    'available_quantity': current_stock,
                    'requested_quantity': quantity,
                    'reason': 'Stock insuffisant'
                })
        
        if unavailable_items:
            return jsonify({
                'success': False,
                'error': 'Stock insuffisant pour la réservation'
            }), 400
        
        # Effectuer les réservations
        reservations = []
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)
            
            # Mettre à jour le stock (réduire la quantité)
            success, result = product_service.update_stock(product_id, -quantity)
            if not success:
                # Annuler les réservations déjà effectuées
                for reservation in reservations:
                    product_service.update_stock(reservation['product_id'], reservation['quantity'])
                
                return jsonify({
                    'success': False,
                    'error': f'Échec de la réservation pour le produit {product_id}'
                }), 400
            
            reservations.append({
                'product_id': product_id,
                'quantity': quantity,
                'reserved_at': '2025-07-16T18:00:00Z'  # Timestamp simulé
            })
        
        logger.info(f"Stock reserved successfully for order {order_id}")
        return jsonify({
            'success': True,
            'reservation_id': reservation_id,
            'reservations': reservations,
            'message': 'Stock réservé avec succès'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in reserve_stock: {str(e)}")
        return jsonify({'error': f'Erreur interne: {str(e)}'}), 500

@bp.route('/api/release-stock', methods=['POST'])
def release_stock():
    """Libère le stock réservé (compensation)"""
    try:
        data = request.get_json()
        if not data or 'items' not in data:
            return jsonify({'error': 'Données manquantes'}), 400
        
        items = data['items']
        released_items = []
        
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)
            
            # Restaurer le stock (augmenter la quantité)
            success, result = product_service.update_stock(product_id, quantity)
            if success:
                released_items.append({
                    'product_id': product_id,
                    'quantity': quantity,
                    'released_at': '2025-07-16T18:00:00Z'  # Timestamp simulé
                })
            else:
                logger.error(f"Failed to release stock for product {product_id}")
        
        logger.info(f"Stock released for {len(released_items)} items")
        return jsonify({
            'success': True,
            'released_items': released_items,
            'message': 'Stock libéré avec succès'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in release_stock: {str(e)}")
        return jsonify({'error': f'Erreur interne: {str(e)}'}), 500 