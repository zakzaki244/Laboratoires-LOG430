from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities import Product

class IProductRepository(ABC):
    """Interface pour le repository des produits"""
    
    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Récupérer un produit par son ID"""
        pass
    
    @abstractmethod
    def get_all(self) -> List[Product]:
        """Récupérer tous les produits"""
        pass
    
    @abstractmethod
    def search(self, term: str) -> List[Product]:
        """Rechercher des produits par nom ou catégorie"""
        pass
    
    @abstractmethod
    def get_by_store(self, store_id: int) -> List[Product]:
        """Récupérer les produits d'un magasin"""
        pass
    
    @abstractmethod
    def save(self, product: Product) -> Product:
        """Sauvegarder un produit"""
        pass
    
    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """Supprimer un produit"""
        pass
    
    @abstractmethod
    def update(self, product: Product) -> Product:
        """Mettre à jour un produit"""
        pass

class IStoreServiceAdapter(ABC):
    """Interface pour adapter le service des magasins"""
    
    @abstractmethod
    def store_exists(self, store_id: int) -> bool:
        """Vérifier si un magasin existe"""
        pass
