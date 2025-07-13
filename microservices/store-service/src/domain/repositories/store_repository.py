from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities import Store

class IStoreRepository(ABC):
    """Interface pour le repository des magasins"""
    
    @abstractmethod
    def get_by_id(self, store_id: int) -> Optional[Store]:
        """Récupérer un magasin par son ID"""
        pass
    
    @abstractmethod
    def get_all(self) -> List[Store]:
        """Récupérer tous les magasins"""
        pass
    
    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Store]:
        """Récupérer un magasin par son nom"""
        pass
    
    @abstractmethod
    def save(self, store: Store) -> Store:
        """Sauvegarder un magasin"""
        pass
    
    @abstractmethod
    def update(self, store: Store) -> Store:
        """Mettre à jour un magasin"""
        pass
    
    @abstractmethod
    def delete(self, store_id: int) -> bool:
        """Supprimer un magasin"""
        pass
    
    @abstractmethod
    def name_exists(self, name: str, exclude_id: Optional[int] = None) -> bool:
        """Vérifier si un nom de magasin existe déjà"""
        pass
