from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from ..entities import Cart

class ICartRepository(ABC):
    """Interface pour le repository des paniers"""
    
    @abstractmethod
    def get_by_id(self, cart_id: int) -> Optional[Cart]:
        """Récupérer un panier par son ID"""
        pass
    
    @abstractmethod
    def get_active_by_customer(self, customer_id: int) -> Optional[Cart]:
        """Récupérer le panier actif d'un client"""
        pass
    
    @abstractmethod
    def get_by_customer(self, customer_id: int) -> List[Cart]:
        """Récupérer tous les paniers d'un client"""
        pass
    
    @abstractmethod
    def save(self, cart: Cart) -> Cart:
        """Sauvegarder un panier"""
        pass
    
    @abstractmethod
    def update(self, cart: Cart) -> Cart:
        """Mettre à jour un panier"""
        pass
    
    @abstractmethod
    def delete(self, cart_id: int) -> bool:
        """Supprimer un panier"""
        pass

class IProductServiceAdapter(ABC):
    """Interface pour adapter le service des produits"""
    
    @abstractmethod
    def get_product_info(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Récupérer les informations d'un produit"""
        pass
    
    @abstractmethod
    def check_product_availability(self, product_id: int, required_quantity: int) -> bool:
        """Vérifier la disponibilité d'un produit"""
        pass

class ICustomerServiceAdapter(ABC):
    """Interface pour adapter le service des clients"""
    
    @abstractmethod
    def customer_exists(self, customer_id: int) -> bool:
        """Vérifier si un client existe"""
        pass

class ICacheAdapter(ABC):
    """Interface pour adapter le cache"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Récupérer une valeur du cache"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Dict[str, Any], ttl: int = 3600) -> bool:
        """Stocker une valeur dans le cache"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Supprimer une valeur du cache"""
        pass
