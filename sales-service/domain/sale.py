from datetime import datetime

class Sale:
    def __init__(self, client_id, total, date=None, id=None):
        self.id = id
        self.client_id = client_id
        self.total = total
        self.date = date or datetime.now()