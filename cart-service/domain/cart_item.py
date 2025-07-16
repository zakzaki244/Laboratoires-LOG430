class CartItem:
    def __init__(self, cart_id, product_id, quantity, unit_price, id=None):
        self.id = id
        self.cart_id = cart_id
        self.product_id = product_id
        self.quantity = quantity
        self.unit_price = unit_price