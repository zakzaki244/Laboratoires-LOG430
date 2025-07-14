from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class CustomerRepositorySimple:
    """Repository simple pour les clients utilisant un stockage en mémoire"""
    
    def __init__(self):
        self._customers: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1
    
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
                'is_active': customer_data.get('is_active', True),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
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
