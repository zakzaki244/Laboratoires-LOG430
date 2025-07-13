from typing import List, Optional
from ...infrastructure.database.models import CustomerModel
import logging

logger = logging.getLogger(__name__)


class CustomerService:
    """Service applicatif pour la gestion des clients"""
    
    def __init__(self, customer_repository):
        self._customer_repository = customer_repository
    
    def create_customer(self, customer_data: dict) -> CustomerModel:
        """Créer un nouveau client"""
        try:
            customer = self._customer_repository.create(customer_data)
            logger.info(f"Client créé avec succès: {customer.email}")
            return customer
        except Exception as e:
            logger.error(f"Erreur lors de la création du client: {str(e)}")
            raise
    
    def get_customer_by_email(self, email: str) -> Optional[CustomerModel]:
        """Récupérer un client par email"""
        try:
            return self._customer_repository.get_by_email(email)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du client par email: {str(e)}")
            return None
    
    def get_customer_by_id(self, customer_id: int) -> Optional[CustomerModel]:
        """Récupérer un client par ID"""
        try:
            return self._customer_repository.get_by_id(customer_id)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du client par ID: {str(e)}")
            return None
    
    def update_customer(self, customer_id: int, update_data: dict) -> Optional[CustomerModel]:
        """Mettre à jour un client"""
        try:
            customer = self._customer_repository.update(customer_id, update_data)
            if customer:
                logger.info(f"Client mis à jour avec succès: {customer.email}")
            return customer
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du client: {str(e)}")
            return None
    
    def delete_customer(self, customer_id: int) -> bool:
        """Supprimer un client"""
        try:
            success = self._customer_repository.delete(customer_id)
            if success:
                logger.info(f"Client supprimé avec succès: {customer_id}")
            return success
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du client: {str(e)}")
            return False
    
    def get_all_customers(self) -> List[CustomerModel]:
        """Récupérer tous les clients"""
        try:
            return self._customer_repository.get_all()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des clients: {str(e)}")
            return []
    
    def authenticate_customer(self, email: str, password: str) -> Optional[CustomerModel]:
        """Authentifier un client"""
        try:
            customer = self.get_customer_by_email(email)
            if customer and customer.is_active:
                # Note: La validation du mot de passe est faite au niveau du contrôleur
                return customer
            return None
        except Exception as e:
            logger.error(f"Erreur lors de l'authentification: {str(e)}")
            return None
    
    def activate_customer(self, customer_id: int) -> bool:
        """Activer un client"""
        try:
            return self.update_customer(customer_id, {'is_active': True}) is not None
        except Exception as e:
            logger.error(f"Erreur lors de l'activation du client: {str(e)}")
            return False
    
    def deactivate_customer(self, customer_id: int) -> bool:
        """Désactiver un client"""
        try:
            return self.update_customer(customer_id, {'is_active': False}) is not None
        except Exception as e:
            logger.error(f"Erreur lors de la désactivation du client: {str(e)}")
            return False
