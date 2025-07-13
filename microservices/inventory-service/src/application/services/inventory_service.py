from typing import List, Optional, Dict, Any
import requests
from datetime import datetime

from ..dto.inventory_dto import (
    CreateReapproRequest, UpdateReapproRequest, ProcessReapproRequest,
    ReapproRequestResponse, ReapproRequestListResponse, ReapproStatsResponse
)
from ...domain.entities.reappro_request import ReapproRequest
from ...domain.repositories.reappro_request_repository import ReapproRequestRepository
from ...domain.value_objects.inventory_value_objects import (
    StoreId, ProductId, Quantity, ReapproStatus
)


class InventoryService:
    def __init__(self, reappro_repository: ReapproRequestRepository,
                 product_service_url: str, store_service_url: str,
                 api_token: str):
        self.reappro_repository = reappro_repository
        self.product_service_url = product_service_url
        self.store_service_url = store_service_url
        self.api_token = api_token
        self.headers = {"Authorization": f"Bearer {api_token}"}
    
    def create_reappro_request(self, request: CreateReapproRequest) -> ReapproRequestResponse:
        """Créer une nouvelle demande de réapprovisionnement"""
        try:
            # Vérifier que le magasin existe
            store_response = requests.get(
                f"{self.store_service_url}/stores/{request.store_id}",
                headers=self.headers
            )
            if store_response.status_code != 200:
                raise ValueError("Magasin introuvable")
            
            # Vérifier que le produit existe
            product_response = requests.get(
                f"{self.product_service_url}/products/{request.product_id}",
                headers=self.headers
            )
            if product_response.status_code != 200:
                raise ValueError("Produit introuvable")
            
            # Créer l'entité ReapproRequest
            reappro_request = ReapproRequest(
                store_id=StoreId(request.store_id),
                product_id=ProductId(request.product_id),
                quantity=Quantity(request.quantity),
                notes=request.notes
            )
            
            saved_request = self.reappro_repository.save(reappro_request)
            
            return self._request_to_response(saved_request)
            
        except Exception as e:
            raise ValueError(f"Error creating reappro request: {str(e)}")
    
    def get_reappro_request(self, request_id: int) -> Optional[ReapproRequestResponse]:
        """Récupérer une demande de réapprovisionnement par ID"""
        request = self.reappro_repository.find_by_id(request_id)
        if not request:
            return None
        return self._request_to_response(request)
    
    def get_all_reappro_requests(self) -> List[ReapproRequestResponse]:
        """Récupérer toutes les demandes de réapprovisionnement"""
        requests = self.reappro_repository.find_all()
        return [self._request_to_response(request) for request in requests]
    
    def get_reappro_requests_by_store(self, store_id: int) -> List[ReapproRequestResponse]:
        """Récupérer toutes les demandes d'un magasin"""
        requests = self.reappro_repository.find_by_store_id(StoreId(store_id))
        return [self._request_to_response(request) for request in requests]
    
    def get_reappro_requests_by_product(self, product_id: int) -> List[ReapproRequestResponse]:
        """Récupérer toutes les demandes pour un produit"""
        requests = self.reappro_repository.find_by_product_id(ProductId(product_id))
        return [self._request_to_response(request) for request in requests]
    
    def get_pending_reappro_requests(self) -> List[ReapproRequestResponse]:
        """Récupérer toutes les demandes en attente"""
        requests = self.reappro_repository.find_pending_requests()
        return [self._request_to_response(request) for request in requests]
    
    def get_reappro_requests_by_status(self, status: str) -> List[ReapproRequestResponse]:
        """Récupérer toutes les demandes avec un statut donné"""
        try:
            status_enum = ReapproStatus(status)
            requests = self.reappro_repository.find_by_status(status_enum)
            return [self._request_to_response(request) for request in requests]
        except ValueError:
            raise ValueError(f"Invalid status: {status}")
    
    def update_reappro_request(self, request: UpdateReapproRequest) -> Optional[ReapproRequestResponse]:
        """Mettre à jour une demande de réapprovisionnement"""
        reappro_request = self.reappro_repository.find_by_id(request.request_id)
        if not reappro_request:
            return None
        
        if not reappro_request.can_be_processed():
            raise ValueError("Seules les demandes en attente peuvent être modifiées")
        
        # Mettre à jour les champs
        if request.quantity is not None:
            reappro_request.quantity = Quantity(request.quantity)
        
        if request.notes is not None:
            reappro_request.notes = request.notes
        
        updated_request = self.reappro_repository.save(reappro_request)
        return self._request_to_response(updated_request)
    
    def process_reappro_request(self, request: ProcessReapproRequest) -> Optional[ReapproRequestResponse]:
        """Traiter une demande de réapprovisionnement (approuver ou rejeter)"""
        reappro_request = self.reappro_repository.find_by_id(request.request_id)
        if not reappro_request:
            return None
        
        if request.action == "approve":
            reappro_request.approve(request.notes)
        elif request.action == "reject":
            reappro_request.reject(request.notes)
        else:
            raise ValueError("Action non valide. Utilisez « approuver » ou « rejeter ».")
        
        processed_request = self.reappro_repository.save(reappro_request)
        return self._request_to_response(processed_request)
    
    def complete_reappro_request(self, request_id: int) -> Optional[ReapproRequestResponse]:
        """Marquer une demande comme terminée"""
        reappro_request = self.reappro_repository.find_by_id(request_id)
        if not reappro_request:
            return None
        
        reappro_request.complete()
        completed_request = self.reappro_repository.save(reappro_request)
        return self._request_to_response(completed_request)
    
    def delete_reappro_request(self, request_id: int) -> bool:
        """Supprimer une demande de réapprovisionnement"""
        reappro_request = self.reappro_repository.find_by_id(request_id)
        if not reappro_request:
            return False
        
        if not reappro_request.can_be_processed():
            raise ValueError("Seules les demandes en attente peuvent être supprimées")
        
        return self.reappro_repository.delete(request_id)
    
    def get_reappro_stats(self) -> ReapproStatsResponse:
        """Récupérer les statistiques des demandes de réapprovisionnement"""
        all_requests = self.reappro_repository.find_all()
        
        # Calculer les statistiques
        total_requests = len(all_requests)
        pending_requests = len([r for r in all_requests if r.status == ReapproStatus.PENDING])
        approved_requests = len([r for r in all_requests if r.status == ReapproStatus.APPROVED])
        rejected_requests = len([r for r in all_requests if r.status == ReapproStatus.REJECTED])
        completed_requests = len([r for r in all_requests if r.status == ReapproStatus.COMPLETED])
        
        # Statistiques par magasin
        requests_by_store = {}
        for request in all_requests:
            store_id = request.store_id.value
            requests_by_store[store_id] = requests_by_store.get(store_id, 0) + 1
        
        # Statistiques par produit
        requests_by_product = {}
        for request in all_requests:
            product_id = request.product_id.value
            requests_by_product[product_id] = requests_by_product.get(product_id, 0) + 1
        
        return ReapproStatsResponse(
            total_requests=total_requests,
            pending_requests=pending_requests,
            approved_requests=approved_requests,
            rejected_requests=rejected_requests,
            completed_requests=completed_requests,
            requests_by_store=requests_by_store,
            requests_by_product=requests_by_product
        )
    
    def _request_to_response(self, request: ReapproRequest) -> ReapproRequestResponse:
        """Convertir une entité ReapproRequest en ReapproRequestResponse"""
        store_name = None
        try:
            store_response = requests.get(
                f"{self.store_service_url}/stores/{request.store_id.value}",
                headers=self.headers
            )
            if store_response.status_code == 200:
                store_data = store_response.json()
                store_name = store_data.get('name')
        except:
            pass
        
        product_name = None
        try:
            product_response = requests.get(
                f"{self.product_service_url}/products/{request.product_id.value}",
                headers=self.headers
            )
            if product_response.status_code == 200:
                product_data = product_response.json()
                product_name = product_data.get('name')
        except:
            pass
        
        return ReapproRequestResponse(
            id=request.id,
            store_id=request.store_id.value,
            product_id=request.product_id.value,
            quantity=request.quantity.value,
            status=request.status.value,
            requested_at=request.requested_at.isoformat() if request.requested_at else None,
            processed_at=request.processed_at.isoformat() if request.processed_at else None,
            notes=request.notes,
            store_name=store_name,
            product_name=product_name
        )
