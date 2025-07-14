from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..entities.order import Order
from ..value_objects.checkout_value_objects import CustomerId, OrderNumber


class IOrderRepository(ABC):
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


class ICartServiceAdapter(ABC):
    """Adaptateur pour le service de panier"""
    
    @abstractmethod
    def get_cart_items(self, customer_id: int) -> List[Dict[str, Any]]:
        """Récupérer les articles du panier"""
        pass
    
    @abstractmethod
    def clear_cart(self, customer_id: int) -> bool:
        """Vider le panier"""
        pass


class ICustomerServiceAdapter(ABC):
    """Adaptateur pour le service client"""
    
    @abstractmethod
    def get_customer(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Récupérer un client"""
        pass
    
    @abstractmethod
    def validate_customer(self, customer_id: int) -> bool:
        """Valider un client"""
        pass


class ISalesServiceAdapter(ABC):
    """Adaptateur pour le service de vente"""
    
    @abstractmethod
    def create_sale(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Créer une vente"""
        pass
    
    @abstractmethod
    def get_sale_by_order_id(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Récupérer une vente par ID de commande"""
        pass


class IPaymentServiceAdapter(ABC):
    """Adaptateur pour le service de paiement"""
    
    @abstractmethod
    def process_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Traiter un paiement"""
        pass
    
    @abstractmethod
    def get_payment_status(self, payment_id: str) -> str:
        """Récupérer le statut d'un paiement"""
        pass


class IInventoryServiceAdapter(ABC):
    """Adaptateur pour le service d'inventaire"""
    
    @abstractmethod
    def reserve_stock(self, items: List[Dict[str, Any]]) -> bool:
        """Réserver du stock"""
        pass
    
    @abstractmethod
    def release_stock(self, items: List[Dict[str, Any]]) -> bool:
        """Libérer du stock"""
        pass
    
    @abstractmethod
    def check_stock_availability(self, items: List[Dict[str, Any]]) -> bool:
        """Vérifier la disponibilité du stock"""
        pass


# Alias pour compatibilité
OrderRepository = IOrderRepository
