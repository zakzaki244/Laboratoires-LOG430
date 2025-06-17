from sqlalchemy.exc import NoResultFound
from db import SessionLocal, init_db
from src.db import Base
from models import Product, Sale, SaleItem

init_db()

class DAO:
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

# créer une vente avec un panier d'articles
    def create_sale(self, cart: list[tuple[Product, int]]):
        sale = Sale()
        self.session.add(sale)
        for prod, qty in cart:
            if prod.stock < qty:
                raise ValueError(f"Stock insuffisant pour {prod.name}")
            prod.stock -= qty
            item = SaleItem(sale=sale, product=prod, quantity=qty)
            self.session.add(item)
        self.session.commit()
        return sale.id

# supprimer une vente et remettre en stock les produits
    def delete_sale(self, sale_id: int):
        sale = self.session.query(Sale).filter_by(id=sale_id).one()
        # remise en stock
        for item in sale.items:
            item.product.stock += item.quantity
        self.session.delete(sale)
        self.session.commit()
