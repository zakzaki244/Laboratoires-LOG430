from datetime import datetime

class Checkout:
    def __init__(self, user_id, store_id, cart_id, total_amount, payment_method, status="pending", id=None, created_at=None):
        self.id = id
        self.user_id = user_id
        self.store_id = store_id
        self.cart_id = cart_id
        self.total_amount = total_amount
        self.payment_method = payment_method
        self.status = status
        self.created_at = created_at or datetime.now()