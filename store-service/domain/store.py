class Store:
    def __init__(self, name, address, phone, email, id=None):
        self.id = id
        self.name = name
        self.address = address
        self.phone = phone
        self.email = email