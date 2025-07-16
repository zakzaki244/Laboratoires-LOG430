class User:
    def __init__(self, username, email, password_hash, role, id=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role

    def check_password(self, password, hasher):
        return hasher.check_password_hash(self.password_hash, password)