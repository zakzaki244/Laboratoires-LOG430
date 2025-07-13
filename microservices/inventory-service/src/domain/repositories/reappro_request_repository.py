from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.reappro_request import ReapproRequest
from ..value_objects.inventory_value_objects import StoreId, ProductId, ReapproStatus


class ReapproRequestRepository(ABC):
    """Interface pour la persistance des demandes de réapprovisionnement"""
    
    @abstractmethod
    def save(self, request: ReapproRequest) -> ReapproRequest:
        """Sauvegarder une demande de réapprovisionnement"""
        pass
    
    @abstractmethod
    def find_by_id(self, request_id: int) -> Optional[ReapproRequest]:
        """Trouver une demande par ID"""
        pass
    
    @abstractmethod
    def find_by_store_id(self, store_id: StoreId) -> List[ReapproRequest]:
        """Trouver toutes les demandes d'un magasin"""
        pass
    
    @abstractmethod
    def find_by_product_id(self, product_id: ProductId) -> List[ReapproRequest]:
        """Trouver toutes les demandes pour un produit"""
        pass
    
    @abstractmethod
    def find_by_status(self, status: ReapproStatus) -> List[ReapproRequest]:
        """Trouver toutes les demandes avec un statut donné"""
        pass
    
    @abstractmethod
    def find_pending_requests(self) -> List[ReapproRequest]:
        """Trouver toutes les demandes en attente"""
        pass
    
    @abstractmethod
    def find_all(self) -> List[ReapproRequest]:
        """Trouver toutes les demandes"""
        pass
    
    @abstractmethod
    def delete(self, request_id: int) -> bool:
        """Supprimer une demande"""
        pass
