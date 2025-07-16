from domain.cart import Cart
from domain.cart_item import CartItem

class CartService:
    def __init__(self, cart_repository, cart_item_repository):
        self.cart_repository = cart_repository
        self.cart_item_repository = cart_item_repository

    def get_cart(self, user_id, store_id):
        cart = self.cart_repository.get_or_create_cart(user_id, store_id)
        items = self.cart_item_repository.get_items_by_cart_id(cart.id)
        
        total = sum(item.quantity * item.unit_price for item in items)
        
        return {
            'id': cart.id,
            'user_id': cart.user_id,
            'store_id': cart.store_id,
            'created_at': cart.created_at.isoformat(),
            'items': [
                {
                    'id': item.id,
                    'product_id': item.product_id,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'subtotal': item.quantity * item.unit_price
                } for item in items
            ],
            'total': total
        }, 200

    def add_item(self, user_id, store_id, data):
        cart = self.cart_repository.get_or_create_cart(user_id, store_id)
        
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=data['product_id'],
            quantity=data['quantity'],
            unit_price=data['unit_price']
        )
        
        item_id = self.cart_item_repository.add_item(cart_item)
        return {'id': item_id, 'message': "Produit ajouté au panier avec succès"}, 201

    def update_item_quantity(self, user_id, store_id, product_id, quantity):
        cart = self.cart_repository.get_or_create_cart(user_id, store_id)
        
        if self.cart_item_repository.update_item_quantity(cart.id, product_id, quantity):
            return {'message': "Quantité mise à jour avec succès"}, 200
        return {'message': "Produit non trouvé dans le panier"}, 404

    def remove_item(self, user_id, store_id, product_id):
        cart = self.cart_repository.get_or_create_cart(user_id, store_id)
        
        if self.cart_item_repository.remove_item(cart.id, product_id):
            return {'message': "Produit supprimé du panier avec succès"}, 200
        return {'message': "Produit non trouvé dans le panier"}, 404

    def clear_cart(self, user_id, store_id):
        cart = self.cart_repository.get_or_create_cart(user_id, store_id)
        self.cart_item_repository.clear_cart(cart.id)
        return {'message': "Panier vidé avec succès"}, 200

    def delete_cart(self, user_id, store_id):
        cart = self.cart_repository.get_or_create_cart(user_id, store_id)
        if self.cart_repository.delete_cart(cart.id):
            return {'message': "Panier supprimé avec succès"}, 200
        return {'message': "Panier non trouvé"}, 404