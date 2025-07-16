from infrastructure.db import db, UserModel
from domain.user import User

class UserRepository:
    def add(self, user: User):
        user_model = UserModel(
            username=user.username,
            email=user.email,
            password_hash=user.password_hash,
            role=user.role
        )
        db.session.add(user_model)
        db.session.commit()
        return user_model.id

    def get_by_username(self, username):
        user_model = UserModel.query.filter_by(username=username).first()
        if user_model:
            return User(
                id=user_model.id,
                username=user_model.username,
                email=user_model.email,
                password_hash=user_model.password_hash,
                role=user_model.role
            )
        return None

    def get_by_id(self, user_id):
        user_model = UserModel.query.get(user_id)
        if user_model:
            return User(
                id=user_model.id,
                username=user_model.username,
                email=user_model.email,
                password_hash=user_model.password_hash,
                role=user_model.role
            )
        return None

    def update(self, user_id, data):
        user_model = UserModel.query.get(user_id)
        if not user_model:
            return None
        for key, value in data.items():
            setattr(user_model, key, value)
        db.session.commit()
        return user_model

    def delete(self, user_id):
        user_model = UserModel.query.get(user_id)
        if not user_model:
            return False
        db.session.delete(user_model)
        db.session.commit()
        return True

    def list_all(self):
        return UserModel.query.all()
    
    def get_by_email(self, email):
        user_model = UserModel.query.filter_by(email=email).first()
        if user_model:
            return User(
                id=user_model.id,
                username=user_model.username,
                email=user_model.email,
                password_hash=user_model.password_hash,
                role=user_model.role
            )
        return None