from datetime import datetime

class Cart:
    def __init__(self, user_id, store_id, id=None, created_at=None):
        self.id = id
        self.user_id = user_id
        self.store_id = store_id
        self.created_at = created_at or datetime.now()