from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class ProductModel(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Float, nullable=False)
    quantity_stock = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    store_id = db.Column(db.Integer, nullable=False)

    def __init__(self, name, description, price, quantity_stock, category, store_id):
        self.name = name
        self.description = description
        self.price = price
        self.quantity_stock = quantity_stock
        self.category = category
        self.store_id = store_id