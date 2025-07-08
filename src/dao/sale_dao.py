from sqlalchemy.exc import NoResultFound
from db.db import SessionLocal, init_db
from db.db import Base
from models.sale import Sale
from models.sale_item import SaleItem
from models.product import Product

class SaleDAO:
    def __init__(self):
        self.session = SessionLocal()

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