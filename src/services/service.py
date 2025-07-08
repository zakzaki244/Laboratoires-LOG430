# from dao import DAO
# from sqlalchemy.exc import NoResultFound

# class Service:
#     def __init__(self):
#         self.dao = DAO()


#     def search(self, term: str):
#         return self.dao.search_products(term)

#     def stock(self):
#         return self.dao.list_stock()

#     def sale(self, entries: list[tuple[int,int]]):
#         cart = []
#         for pid, qty in entries:
#             try:
#                 prod = self.dao.get_product(pid)
#             except NoResultFound:
#                 raise ValueError(f"Produit #{pid} introuvable")
#             cart.append((prod, qty))
#         return self.dao.create_sale(cart)

#     def refund(self, sale_id: int):
#         try:
#             return self.dao.delete_sale(sale_id)
#         except NoResultFound:
#             raise ValueError(f"Vente #{sale_id} introuvable")
