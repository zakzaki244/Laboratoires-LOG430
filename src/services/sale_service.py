from dao.sale_dao import SaleDAO, ProductDAO
from sqlalchemy.exc import NoResultFound

class SaleService:
    def __init__(self):
        self.sale_dao = SaleDAO()
        self.product_dao = ProductDAO()
    
    def sale(self, entries: list[tuple[int, int]]):
        cart = []
        for pid, qty in entries:
            try:
                prod = self.product_dao.get_product(pid)
            except NoResultFound:
                raise ValueError(f"Produit #{pid} introuvable")
            cart.append((prod, qty))
        return self.sale_dao.create_sale(cart)