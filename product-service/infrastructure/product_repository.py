from infrastructure.db import db, ProductModel
from domain.product import Product

class ProductRepository:
    def add(self, product: Product):
        product_model = ProductModel(
            name=product.name,
            description=product.description,
            price=product.price,
            quantity_stock=product.quantity_stock,
            category=product.category,
            store_id=product.store_id
        )
        db.session.add(product_model)
        db.session.commit()
        return product_model.id

    def get_by_id(self, product_id):
        product_model = ProductModel.query.get(product_id)
        if product_model:
            return Product(
                id=product_model.id,
                name=product_model.name,
                description=product_model.description,
                price=product_model.price,
                quantity_stock=product_model.quantity_stock,
                category=product_model.category,
                store_id=product_model.store_id
            )
        return None

    def update(self, product_id, data):
        product_model = ProductModel.query.get(product_id)
        if not product_model:
            return None
        for key, value in data.items():
            if hasattr(product_model, key):
                setattr(product_model, key, value)
        db.session.commit()
        return product_model

    def delete(self, product_id):
        product_model = ProductModel.query.get(product_id)
        if not product_model:
            return False
        db.session.delete(product_model)
        db.session.commit()
        return True

    def list_all(self):
        return ProductModel.query.all()

    def list_by_store(self, store_id):
        return ProductModel.query.filter_by(store_id=store_id).all()

    def search(self, query):
        return ProductModel.query.filter(getattr(ProductModel, 'name').ilike(f'%{query}%')).all()

    def search_by_store(self, query, store_id):
        return ProductModel.query.filter(
            getattr(ProductModel, 'store_id') == store_id,
            getattr(ProductModel, 'name').ilike(f'%{query}%')
        ).all()