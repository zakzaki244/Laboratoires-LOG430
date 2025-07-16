
class Product:
    def __init__(self, name, description, price, quantity_stock, category, store_id, id=None):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.quantity_stock = quantity_stock
        self.category = category
        self.store_id = store_id