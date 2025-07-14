"""
Script d'initialisation des utilisateurs par défaut selon les acteurs du système
"""
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash
from .models import CustomerModel, Customer
from .database import session
import logging

logger = logging.getLogger(__name__)


def seed_default_users(session: Session):
    """Initialiser les utilisateurs par défaut selon les acteurs du système"""
    
    # Vérifier si les utilisateurs existent déjà
    if session.query(CustomerModel).filter_by(email="gestionnaire@maisonmere.com").first():
        logger.info("Utilisateurs par défaut déjà créés")
        return
    
    default_users = [
        # 1. Gestionnaire Maison Mère (UC1, UC3, UC8)
        {
            "email": "gestionnaire@maisonmere.com",
            "password": "gestionnaire123",
            "first_name": "Marie",
            "last_name": "Dupont",
            "phone": "514-123-4567",
            "role": "gestionnaire_maison_mere",
            "address": {
                "street": "100 Boulevard Principal",
                "city": "Montréal",
                "postal_code": "H1A 1A1",
                "country": "Canada"
            }
        },
        # 2. Employé Magasin (UC2)
        {
            "email": "employe@magasin1.com",
            "password": "employe123",
            "first_name": "Jean",
            "last_name": "Martin",
            "phone": "514-234-5678",
            "role": "employe_magasin",
            "store_id": 1,
            "address": {
                "street": "50 Rue du Commerce",
                "city": "Montréal",
                "postal_code": "H2B 2B2",
                "country": "Canada"
            }
        },
        # 3. Responsable Logistique (UC6)
        {
            "email": "logistique@centre.com",
            "password": "logistique123",
            "first_name": "Pierre",
            "last_name": "Tremblay",
            "phone": "514-345-6789",
            "role": "responsable_logistique",
            "address": {
                "street": "200 Avenue Industrielle",
                "city": "Laval",
                "postal_code": "H3C 3C3",
                "country": "Canada"
            }
        },
        # 4. Responsable Produit (UC4)
        {
            "email": "produit@maisonmere.com",
            "password": "produit123",
            "first_name": "Sophie",
            "last_name": "Leblanc",
            "phone": "514-456-7890",
            "role": "responsable_produit",
            "address": {
                "street": "100 Boulevard Principal",
                "city": "Montréal",
                "postal_code": "H1A 1A1",
                "country": "Canada"
            }
        },
        # 5. Clients exemples (UC9-UC15)
        {
            "email": "client1@test.com",
            "password": "client123",
            "first_name": "Alice",
            "last_name": "Johnson",
            "phone": "514-567-8901",
            "role": "client",
            "address": {
                "street": "123 Rue Résidentielle",
                "city": "Montréal",
                "postal_code": "H4D 4D4",
                "country": "Canada"
            }
        },
        {
            "email": "client2@test.com",
            "password": "client123",
            "first_name": "Bob",
            "last_name": "Smith",
            "phone": "514-678-9012",
            "role": "client",
            "address": {
                "street": "456 Avenue des Clients",
                "city": "Québec",
                "postal_code": "G1E 5E5",
                "country": "Canada"
            }
        }
    ]
    
    try:
        for user_data in default_users:
            # Hasher le mot de passe
            password_hash = generate_password_hash(user_data['password'])
            
            # Créer le modèle utilisateur
            user_model = CustomerModel(
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                phone=user_data['phone'],
                password_hash=password_hash,
                role=user_data['role'],
                store_id=user_data.get('store_id'),
                address=user_data['address'],
                is_active=True
            )
            
            session.add(user_model)
            logger.info(f"Utilisateur créé: {user_data['email']} ({user_data['role']})")
        
        session.commit()
        logger.info("Tous les utilisateurs par défaut ont été créés avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors de la création des utilisateurs par défaut: {str(e)}")
        session.rollback()
        raise

# Ajout des utilisateurs
users = [
    Customer(
        email="gestionnaire@maisonmere.com",
        first_name="Gestionnaire",
        last_name="MaisonMere",
        phone="123456789",
        password_hash="hashed_password",
        role="admin",
        store_id=None,
        address="123 Main Street",
        is_active=True
    ),
    Customer(
        email="employe@magasin1.com",
        first_name="Employe",
        last_name="Magasin1",
        phone="987654321",
        password_hash="hashed_password",
        role="employee",
        store_id=1,
        address="456 Elm Street",
        is_active=True
    )
]

# Insertion dans la base de données
for user in users:
    session.add(user)
session.commit()
