from infrastructure.db import db, CartModel, CartItemModel
from domain.cart import Cart
from domain.cart_item import CartItem

class CartRepository:
    def get_or_create_cart(self, user_id, store_id):
        cart_model = CartModel.query.filter_by(user_id=user_id, store_id=store_id).first()
        if not cart_model:
            cart_model = CartModel(user_id=user_id, store_id=store_id)
            db.session.add(cart_model)
            db.session.commit()
        
        return Cart(
            id=cart_model.id,
            user_id=cart_model.user_id,
            store_id=cart_model.store_id,
            created_at=cart_model.created_at
        )

    def get_cart_by_id(self, cart_id):
        cart_model = CartModel.query.get(cart_id)
        if cart_model:
            return Cart(
                id=cart_model.id,
                user_id=cart_model.user_id,
                store_id=cart_model.store_id,
                created_at=cart_model.created_at
            )
        return None

    def delete_cart(self, cart_id):
        cart_model = CartModel.query.get(cart_id)
        if not cart_model:
            return False
        db.session.delete(cart_model)
        db.session.commit()
        return True

class CartItemRepository:
    def add_item(self, cart_item: CartItem):
        cart_item_model = CartItemModel(
            cart_id=cart_item.cart_id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            unit_price=cart_item.unit_price
        )
        db.session.add(cart_item_model)
        db.session.commit()
        return cart_item_model.id

    def get_items_by_cart_id(self, cart_id):
        cart_items = CartItemModel.query.filter_by(cart_id=cart_id).all()
        return [
            CartItem(
                id=item.id,
                cart_id=item.cart_id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price
            ) for item in cart_items
        ]

    def update_item_quantity(self, cart_id, product_id, quantity):
        cart_item = CartItemModel.query.filter_by(
            cart_id=cart_id, 
            product_id=product_id
        ).first()
        if cart_item:
            cart_item.quantity = quantity
            db.session.commit()
            return True
        return False

    def remove_item(self, cart_id, product_id):
        cart_item = CartItemModel.query.filter_by(
            cart_id=cart_id, 
            product_id=product_id
        ).first()
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
            return True
        return False

    def clear_cart(self, cart_id):
        CartItemModel.query.filter_by(cart_id=cart_id).delete()
        db.session.commit()
        return True