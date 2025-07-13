from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.order import Order
from ..value_objects.checkout_value_objects import CustomerId, OrderNumber


class OrderRepository(ABC):
    """Interface pour la persistance des commandes"""
    
    @abstractmethod
    def save(self, order: Order) -> Order:
        """Sauvegarder une commande"""
        pass
    
    @abstractmethod
    def find_by_id(self, order_id: int) -> Optional[Order]:
        """Trouver une commande par ID"""
        pass
    
    @abstractmethod
    def find_by_order_number(self, order_number: OrderNumber) -> Optional[Order]:
        """Trouver une commande par numéro"""
        pass
    
    @abstractmethod
    def find_by_customer_id(self, customer_id: CustomerId) -> List[Order]:
        """Trouver toutes les commandes d'un client"""
        pass
    
    @abstractmethod
    def find_all(self) -> List[Order]:
        """Trouver toutes les commandes"""
        pass
    
    @abstractmethod
    def delete(self, order_id: int) -> bool:
        """Supprimer une commande"""
        pass
