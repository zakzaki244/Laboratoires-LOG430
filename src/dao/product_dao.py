from sqlalchemy.exc import NoResultFound
from db.db import SessionLocal, init_db
from db.db import Base
from models.product import Product

class ProductDAO:
    def __init__(self):
        self.session = SessionLocal()

#chercher des produits par nom, catégorie ou ID
    def search_products(self, term: str):
        q = self.session.query(Product)
        return q.filter(
            (Product.name.ilike(f"%{term}%")) |
            (Product.category.ilike(f"%{term}%")) |
            (Product.id == term if term.isdigit() else False)
        ).all()

# lister les produits en stock
    def list_stock(self):
        return self.session.query(Product).all()

# obtenir un produit par ID
    def get_product(self, pid: int) -> Product:
        return self.session.query(Product).filter_by(id=pid).one()
