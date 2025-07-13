# Interfaces de repository pour Sales Service
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..entities import Sale, SaleItem

class ISaleRepository(ABC):
    """Interface pour le repository des ventes"""
    
    @abstractmethod
    def get_by_id(self, sale_id: int) -> Optional[Sale]:
        """Récupérer une vente par son ID"""
        pass
    
    @abstractmethod
    def get_all(self) -> List[Sale]:
        """Récupérer toutes les ventes"""
        pass
    
    @abstractmethod
    def get_by_store(self, store_id: int) -> List[Sale]:
        """Récupérer les ventes d'un magasin"""
        pass
    
    @abstractmethod
    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Sale]:
        """Récupérer les ventes dans une plage de dates"""
        pass
    
    @abstractmethod
    def save(self, sale: Sale) -> Sale:
        """Sauvegarder une vente"""
        pass
    
    @abstractmethod
    def update(self, sale: Sale) -> Sale:
        """Mettre à jour une vente"""
        pass
    
    @abstractmethod
    def delete(self, sale_id: int) -> bool:
        """Supprimer une vente"""
        pass

class IProductServiceAdapter(ABC):
    """Interface pour adapter le service des produits"""
    
    @abstractmethod
    def get_product_info(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Récupérer les informations d'un produit"""
        pass
    
    @abstractmethod
    def update_product_stock(self, product_id: int, quantity_change: int) -> bool:
        """Mettre à jour le stock d'un produit"""
        pass
    
    @abstractmethod
    def check_product_availability(self, product_id: int, required_quantity: int) -> bool:
        """Vérifier la disponibilité d'un produit"""
        pass
