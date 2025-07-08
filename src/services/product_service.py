from dao.product_dao import ProductDAO
from sqlalchemy.exc import NoResultFound

class ProductService:
    def __init__(self):
        self.dao = ProductDAO()
    
    def search(self, term: str):
        return self.dao.search_products(term)

    def stock(self):
        return self.dao.list_stock()

