"""
Seed data for customer service
"""

from .models import CustomerModel, UserRole
from werkzeug.security import generate_password_hash

def seed_default_users(session):
    """Seed default users if they don't exist"""
    try:
        # Liste des utilisateurs par défaut avec leurs rôles
        default_users = [
            {
                'first_name': 'Admin',
                'last_name': 'System',
                'email': 'admin@supermarcher.com',
                'password': 'admin123',
                'role': UserRole.ADMIN.value,
                'store_id': None,
                'phone': '514-000-0001',
                'address': {
                    'street': '123 Admin St',
                    'city': 'Montreal',
                    'postal_code': 'H1A 1A1',
                    'country': 'Canada'
                }
            },
            {
                'first_name': 'Gestionnaire',
                'last_name': 'Maison Mère',
                'email': 'gestionnaire@supermarcher.com',
                'password': 'gestionnaire123',
                'role': UserRole.GESTIONNAIRE.value,
                'store_id': None,
                'phone': '514-000-0002',
                'address': {
                    'street': '456 Corporate Ave',
                    'city': 'Montreal',
                    'postal_code': 'H2B 2B2',
                    'country': 'Canada'
                }
            },
            {
                'first_name': 'Responsable',
                'last_name': 'Produit',
                'email': 'responsable.produit@supermarcher.com',
                'password': 'produit123',
                'role': UserRole.RESPONSABLE_PRODUIT.value,
                'store_id': None,
                'phone': '514-000-0003',
                'address': {
                    'street': '789 Product Blvd',
                    'city': 'Montreal',
                    'postal_code': 'H3C 3C3',
                    'country': 'Canada'
                }
            },
            {
                'first_name': 'Responsable',
                'last_name': 'Logistique',
                'email': 'responsable.logistique@supermarcher.com',
                'password': 'logistique123',
                'role': UserRole.RESPONSABLE_LOGISTIQUE.value,
                'store_id': None,
                'phone': '514-000-0004',
                'address': {
                    'street': '321 Logistics St',
                    'city': 'Montreal',
                    'postal_code': 'H4D 4D4',
                    'country': 'Canada'
                }
            },
            {
                'first_name': 'Employé',
                'last_name': 'Magasin',
                'email': 'employe.magasin@supermarcher.com',
                'password': 'employe123',
                'role': UserRole.EMPLOYE_MAGASIN.value,
                'store_id': 1,
                'phone': '514-000-0005',
                'address': {
                    'street': '654 Store Ave',
                    'city': 'Montreal',
                    'postal_code': 'H5E 5E5',
                    'country': 'Canada'
                }
            },
            {
                'first_name': 'Client',
                'last_name': 'Test',
                'email': 'client@supermarcher.com',
                'password': 'client123',
                'role': UserRole.CLIENT.value,
                'store_id': None,
                'phone': '514-000-0006',
                'address': {
                    'street': '987 Client St',
                    'city': 'Montreal',
                    'postal_code': 'H6F 6F6',
                    'country': 'Canada'
                }
            }
        ]

        for user_data in default_users:
            # Vérifier si l'utilisateur existe déjà
            existing_user = session.query(CustomerModel).filter_by(email=user_data['email']).first()
            if not existing_user:
                new_user = CustomerModel(
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    email=user_data['email'],
                    password_hash=generate_password_hash(user_data['password']),
                    role=user_data['role'],
                    store_id=user_data['store_id'],
                    phone=user_data['phone'],
                    address=user_data['address']
                )
                session.add(new_user)
                print(f"User created: {user_data['email']} (role: {user_data['role']})")
        
        session.commit()
        print("Default users seeded successfully")
        
    except Exception as e:
        print(f"Error seeding users: {e}")
        session.rollback()

def seed_stores():
    """Seed default stores if they don't exist"""
    try:
        # Note: In a real microservices architecture, stores would be managed by store-service
        # This is a simplified version for the customer service
        print("Store seeding would be handled by store-service in production")
        
    except Exception as e:
        print(f"Error seeding stores: {e}")
