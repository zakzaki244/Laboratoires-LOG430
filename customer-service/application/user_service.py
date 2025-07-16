from flask import jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from domain.user import User
from utils.jwt_utils import generate_jwt

class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def register(self, data):
        if self.user_repository.get_by_username(data['username']):
            return {'message': "Nom d'utilisateur déjà utilisé"}, 400
        password_hash = generate_password_hash(data['password'])
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=password_hash,
            role=data.get('role', 'client')
        )
        user_id = self.user_repository.add(user)
        return {'id': user_id, 'message': "Utilisateur enregistré avec succès"}, 201

    # def login(self, data):
    #     print("LOGIN DATA:", data)
    #     user = None
    #     if 'email' in data:
    #         user = self.user_repository.get_by_email(data['email'])
    #         print("USER BY EMAIL:", user)
    #     elif 'username' in data:
    #         user = self.user_repository.get_by_username(data['username'])
    #         print("USER BY USERNAME:", user)
    #     if not user or not check_password_hash(user.password_hash, data['password']):
    #         return {'message': "Identifiants invalides"}, 401
    #     token = generate_jwt({'user_id': user.id, 'role': user.role})
    #     return {'token': token}, 200

    def login(self, data):
        print("LOGIN DATA:", data)
        user = None
        if 'email' in data:
            user = self.user_repository.get_by_email(data['email'])
            print("USER BY EMAIL:", user)
        elif 'username' in data:
            user = self.user_repository.get_by_username(data['username'])
            print("USER BY USERNAME:", user)
            if not user or not check_password_hash(user.password_hash, data['password']):
                return {'message': "Identifiants invalides"}, 401
            token = generate_jwt({'user_id': user.id, 'role': user.role})
            # --- AJOUTE CETTE PARTIE ---
            user_dict = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
    }
            return jsonify({'token': token, 'user': user_dict}), 200
        

    def get_user(self, user_id):
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return {'message': "Utilisateur non trouvé"}, 404
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }, 200

    def update_user(self, user_id, data):
        user = self.user_repository.update(user_id, data)
        if not user:
            return {'message': "Utilisateur non trouvé"}, 404
        return {'message': "Utilisateur mis à jour avec succès"}, 200

    def delete_user(self, user_id):
        if not self.user_repository.delete(user_id):
            return {'message': "Utilisateur non trouvé"}, 404
        return {'message': "Utilisateur supprimé avec succès"}, 200

    def list_users(self):
        users = self.user_repository.list_all()
        return [
            {
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'role': u.role
            } for u in users
        ], 200