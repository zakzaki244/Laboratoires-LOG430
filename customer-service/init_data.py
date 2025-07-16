from infrastructure.db import db, UserModel
from flask import Flask
from config import Config
from werkzeug.security import generate_password_hash

# Liste des utilisateurs à insérer
users = [
    {"username": "admin", "email": "admin@supermarche.com", "password": "admin123", "role": "admin"},
    {"username": "gestionnaire", "email": "gestion@supermarche.com", "password": "gest123", "role": "gestionnaire"},
    {"username": "resp_produit", "email": "produit@supermarche.com", "password": "prod123", "role": "responsable_produit"},
    {"username": "resp_log", "email": "logistique@supermarche.com", "password": "log123", "role": "responsable_logistique"},
    {"username": "employe", "email": "employe@supermarche.com", "password": "emp123", "role": "employe_magasin"},
    {"username": "client", "email": "client@supermarche.com", "password": "client123", "role": "client"},
]

def init_db_and_insert_users():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    with app.app_context():
        db.create_all()
        for u in users:
            if not UserModel.query.filter_by(username=u["username"]).first():
                user = UserModel(
                    username=u["username"],
                    email=u["email"],
                    password_hash=generate_password_hash(u["password"]),
                    role=u["role"]
                )
                db.session.add(user)
        db.session.commit()
        print("Utilisateurs de test insérés !")

if __name__ == "__main__":
    init_db_and_insert_users() 