from dao.sale_dao import SaleDAO
from sqlalchemy.exc import NoResultFound

class RefundService:
    def __init__(self):
        self.sale_dao = SaleDAO()
    
    def refund(self, sale_id: int):
        try:
            return self.sale_dao.delete_sale(sale_id)
        except NoResultFound:
            raise ValueError(f"Vente #{sale_id} introuvable")