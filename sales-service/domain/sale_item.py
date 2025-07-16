class SaleItem:
    def __init__(self, sale_id, product_id, quantity, unit_price, id=None):
        self.id = id
        self.sale_id = sale_id
        self.product_id = product_id
        self.quantity = quantity
        self.unit_price = unit_price