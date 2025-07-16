import requests
from domain.checkout import Checkout
from flask import current_app

class CheckoutService:
    def __init__(self, checkout_repository):
        self.checkout_repository = checkout_repository

    def process_checkout(self, user_id, store_id, payment_data):
        try:
            # 1. Récupérer le panier depuis cart-service
            cart_response = requests.get(
                f"{current_app.config['CART_SERVICE_URL']}/cart",
                params={'store_id': store_id},
                headers={'Authorization': f"Bearer {payment_data.get('token')}"}
            )
            
            if cart_response.status_code != 200:
                return {'message': "Impossible de récupérer le panier"}, 400
            
            cart_data = cart_response.json()
            
            if not cart_data.get('items'):
                return {'message': "Le panier est vide"}, 400
            
            # 2. Valider le paiement (simulation)
            if not self._validate_payment(payment_data):
                return {'message': "Paiement refusé"}, 400
            
            # 3. Créer le checkout
            checkout = Checkout(
                user_id=user_id,
                store_id=store_id,
                cart_id=cart_data['id'],
                total_amount=cart_data['total'],
                payment_method=payment_data.get('payment_method', 'card'),
                status='completed'
            )
            
            checkout_id = self.checkout_repository.add(checkout)
            
            # 4. Créer la vente dans sales-service
            sale_data = {
                'client_id': user_id,
                'store_id': store_id,
                'items': cart_data['items']
            }
            
            sale_response = requests.post(
                f"{current_app.config['SALES_SERVICE_URL']}/sales",
                json=sale_data,
                headers={'Authorization': f"Bearer {payment_data.get('token')}"}
            )
            
            if sale_response.status_code != 201:
                # Annuler le checkout si la vente échoue
                self.checkout_repository.update_status(checkout_id, 'failed')
                return {'message': "Erreur lors de la création de la vente"}, 500
            
            # 5. Vider le panier
            requests.delete(
                f"{current_app.config['CART_SERVICE_URL']}/cart",
                params={'store_id': store_id},
                headers={'Authorization': f"Bearer {payment_data.get('token')}"}
            )
            
            return {
                'checkout_id': checkout_id,
                'sale_id': sale_response.json().get('id'),
                'total_amount': cart_data['total'],
                'message': "Commande finalisée avec succès"
            }, 201
            
        except requests.RequestException as e:
            return {'message': f"Erreur de communication avec les services: {str(e)}"}, 500
        except Exception as e:
            return {'message': f"Erreur lors du checkout: {str(e)}"}, 500

    def get_checkout(self, checkout_id):
        checkout = self.checkout_repository.get_by_id(checkout_id)
        if not checkout:
            return {'message': "Checkout non trouvé"}, 404
        return {
            'id': checkout.id,
            'user_id': checkout.user_id,
            'store_id': checkout.store_id,
            'cart_id': checkout.cart_id,
            'total_amount': checkout.total_amount,
            'payment_method': checkout.payment_method,
            'status': checkout.status,
            'created_at': checkout.created_at.isoformat()
        }, 200

    def get_user_checkouts(self, user_id):
        checkouts = self.checkout_repository.get_by_user_id(user_id)
        return [
            {
                'id': c.id,
                'user_id': c.user_id,
                'store_id': c.store_id,
                'cart_id': c.cart_id,
                'total_amount': c.total_amount,
                'payment_method': c.payment_method,
                'status': c.status,
                'created_at': c.created_at.isoformat()
            } for c in checkouts
        ], 200

    def _validate_payment(self, payment_data):
        # Simulation de validation de paiement
        # En production, intégrer avec un vrai système de paiement
        payment_method = payment_data.get('payment_method')
        if payment_method not in ['card', 'cash', 'paypal']:
            return False
        return True