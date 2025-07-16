from infrastructure.db import db, CheckoutModel
from domain.checkout import Checkout

class CheckoutRepository:
    def add(self, checkout: Checkout):
        checkout_model = CheckoutModel(
            user_id=checkout.user_id,
            store_id=checkout.store_id,
            cart_id=checkout.cart_id,
            total_amount=checkout.total_amount,
            payment_method=checkout.payment_method,
            status=checkout.status,
            created_at=checkout.created_at
        )
        db.session.add(checkout_model)
        db.session.commit()
        return checkout_model.id

    def get_by_id(self, checkout_id):
        checkout_model = CheckoutModel.query.get(checkout_id)
        if checkout_model:
            return Checkout(
                id=checkout_model.id,
                user_id=checkout_model.user_id,
                store_id=checkout_model.store_id,
                cart_id=checkout_model.cart_id,
                total_amount=checkout_model.total_amount,
                payment_method=checkout_model.payment_method,
                status=checkout_model.status,
                created_at=checkout_model.created_at
            )
        return None

    def update_status(self, checkout_id, status):
        checkout_model = CheckoutModel.query.get(checkout_id)
        if not checkout_model:
            return None
        checkout_model.status = status
        db.session.commit()
        return checkout_model

    def get_by_user_id(self, user_id):
        checkouts = CheckoutModel.query.filter_by(user_id=user_id).all()
        return [
            Checkout(
                id=c.id,
                user_id=c.user_id,
                store_id=c.store_id,
                cart_id=c.cart_id,
                total_amount=c.total_amount,
                payment_method=c.payment_method,
                status=c.status,
                created_at=c.created_at
            ) for c in checkouts
        ]