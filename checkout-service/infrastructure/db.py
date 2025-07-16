from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

class CheckoutModel(db.Model):
    __tablename__ = 'checkouts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    store_id = db.Column(db.Integer, nullable=False)
    cart_id = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, user_id, store_id, cart_id, total_amount, payment_method, status="pending", created_at=None):
        self.user_id = user_id
        self.store_id = store_id
        self.cart_id = cart_id
        self.total_amount = total_amount
        self.payment_method = payment_method
        self.status = status
        self.created_at = created_at or datetime.utcnow()