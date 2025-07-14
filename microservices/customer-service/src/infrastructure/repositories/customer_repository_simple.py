from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
from werkzeug.security import generate_password_hash

logger = logging.getLogger(__name__)


class CustomerRepositorySimple:
    """Repository simple pour les clients utilisant un stockage en mémoire"""
    
    def __init__(self):
        self._customers: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1
        self._initialize_default_users()
    
    def create(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Créer un nouveau client"""
        try:
            # Vérifier si l'email existe déjà
            for customer in self._customers.values():
                if customer['email'] == customer_data['email']:
                    raise ValueError("Email déjà utilisé")
            
            # Créer le nouveau client
            customer = {
                'id': self._next_id,
                'email': customer_data['email'],
                'first_name': customer_data['first_name'],
                'last_name': customer_data['last_name'],
                'phone': customer_data['phone'],
                'password_hash': customer_data['password_hash'],
                'address': customer_data['address'],
                'role': customer_data.get('role', 'client'),
                'is_active': customer_data.get('is_active', True),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Ajouter store_id si présent
            if 'store_id' in customer_data:
                customer['store_id'] = customer_data['store_id']
            
            self._customers[self._next_id] = customer
            self._next_id += 1
            
            logger.info(f"Client créé avec succès: {customer['email']}")
            return customer
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du client: {str(e)}")
            raise
    
    def get_by_id(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Récupérer un client par son ID"""
        try:
            return self._customers.get(customer_id)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du client {customer_id}: {str(e)}")
            return None
    
    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Récupérer un client par son email"""
        try:
            for customer in self._customers.values():
                if customer['email'] == email:
                    return customer
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du client par email {email}: {str(e)}")
            return None
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Récupérer tous les clients"""
        try:
            return list(self._customers.values())
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de tous les clients: {str(e)}")
            return []
    
    def get_by_role(self, role: str) -> List[Dict[str, Any]]:
        """Récupérer tous les utilisateurs d'un rôle spécifique"""
        try:
            return [customer for customer in self._customers.values() if customer.get('role') == role]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des clients par rôle {role}: {str(e)}")
            return []
    
    def update(self, customer_id: int, customer_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Mettre à jour un client"""
        try:
            if customer_id not in self._customers:
                return None
            
            customer = self._customers[customer_id]
            
            # Mettre à jour les champs fournis
            for key, value in customer_data.items():
                if key != 'id':  # Ne pas permettre la modification de l'ID
                    customer[key] = value
            
            customer['updated_at'] = datetime.utcnow().isoformat()
            
            logger.info(f"Client mis à jour avec succès: {customer['email']}")
            return customer
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du client {customer_id}: {str(e)}")
            return None
    
    def delete(self, customer_id: int) -> bool:
        """Supprimer un client"""
        try:
            if customer_id in self._customers:
                del self._customers[customer_id]
                logger.info(f"Client supprimé avec succès: {customer_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du client {customer_id}: {str(e)}")
            return False
    
    def activate(self, customer_id: int) -> bool:
        """Activer un client"""
        try:
            if customer_id in self._customers:
                self._customers[customer_id]['is_active'] = True
                self._customers[customer_id]['updated_at'] = datetime.utcnow().isoformat()
                logger.info(f"Client activé avec succès: {customer_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erreur lors de l'activation du client {customer_id}: {str(e)}")
            return False
    
    def deactivate(self, customer_id: int) -> bool:
        """Désactiver un client"""
        try:
            if customer_id in self._customers:
                self._customers[customer_id]['is_active'] = False
                self._customers[customer_id]['updated_at'] = datetime.utcnow().isoformat()
                logger.info(f"Client désactivé avec succès: {customer_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la désactivation du client {customer_id}: {str(e)}")
            return False
    
    def _initialize_default_users(self):
        """Initialiser les utilisateurs par défaut selon les acteurs du système"""
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
        
        for user_data in default_users:
            try:
                # Hasher le mot de passe
                password_hash = generate_password_hash(user_data['password'])
                
                # Créer l'utilisateur avec un ID prédéfini
                user = {
                    'id': self._next_id,
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'phone': user_data['phone'],
                    'password_hash': password_hash,
                    'role': user_data['role'],
                    'address': user_data['address'],
                    'is_active': True,
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                # Ajouter store_id si présent
                if 'store_id' in user_data:
                    user['store_id'] = user_data['store_id']
                
                self._customers[self._next_id] = user
                self._next_id += 1
                
                logger.info(f"Utilisateur par défaut créé: {user_data['email']} ({user_data['role']})")
                
            except Exception as e:
                logger.error(f"Erreur lors de la création de l'utilisateur par défaut {user_data['email']}: {str(e)}")
