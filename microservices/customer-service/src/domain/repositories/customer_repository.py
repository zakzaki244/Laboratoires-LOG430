from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.customer import Customer
from ..value_objects.customer_value_objects import Email


class CustomerRepository(ABC):
    """Interface du repository pour les clients"""
    
    @abstractmethod
    async def save(self, customer: Customer) -> Customer:
        """Sauvegarder un client"""
        pass
    
    @abstractmethod
    async def get_by_id(self, customer_id: str) -> Optional[Customer]:
        """Récupérer un client par ID"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: Email) -> Optional[Customer]:
        """Récupérer un client par email"""
        pass
    
    @abstractmethod
    async def get_all_active(self) -> List[Customer]:
        """Récupérer tous les clients actifs"""
        pass
    
    @abstractmethod
    async def delete(self, customer_id: str) -> None:
        """Supprimer un client"""
        pass
    
    @abstractmethod
    async def email_exists(self, email: Email) -> bool:
        """Vérifier si un email existe déjà"""
        pass
