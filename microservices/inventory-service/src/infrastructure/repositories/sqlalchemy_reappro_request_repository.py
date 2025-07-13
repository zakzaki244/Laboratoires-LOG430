from typing import List, Optional
from sqlalchemy.orm import Session

from ...domain.entities.reappro_request import ReapproRequest
from ...domain.repositories.reappro_request_repository import ReapproRequestRepository
from ...domain.value_objects.inventory_value_objects import (
    StoreId, ProductId, Quantity, ReapproStatus
)
from ..database.models import ReapproRequestModel


class SQLAlchemyReapproRequestRepository(ReapproRequestRepository):
    def __init__(self, session: Session):
        self.session = session
    
    def save(self, request: ReapproRequest) -> ReapproRequest:
        """Sauvegarder une demande de réapprovisionnement"""
        if request.id is None:
            request_model = self._request_to_model(request)
            self.session.add(request_model)
            self.session.commit()
            self.session.refresh(request_model)
            return self._model_to_request(request_model)
        else:
            request_model = self.session.query(ReapproRequestModel).filter_by(id=request.id).first()
            if not request_model:
                raise ValueError(f"Request with id {request.id} not found")
            
            self._update_model_from_request(request_model, request)
            self.session.commit()
            self.session.refresh(request_model)
            return self._model_to_request(request_model)
    
    def find_by_id(self, request_id: int) -> Optional[ReapproRequest]:
        """Trouver une demande par ID"""
        request_model = self.session.query(ReapproRequestModel).filter_by(id=request_id).first()
        if not request_model:
            return None
        return self._model_to_request(request_model)
    
    def find_by_store_id(self, store_id: StoreId) -> List[ReapproRequest]:
        """Trouver toutes les demandes d'un magasin"""
        request_models = self.session.query(ReapproRequestModel).filter_by(store_id=store_id.value).all()
        return [self._model_to_request(model) for model in request_models]
    
    def find_by_product_id(self, product_id: ProductId) -> List[ReapproRequest]:
        """Trouver toutes les demandes pour un produit"""
        request_models = self.session.query(ReapproRequestModel).filter_by(product_id=product_id.value).all()
        return [self._model_to_request(model) for model in request_models]
    
    def find_by_status(self, status: ReapproStatus) -> List[ReapproRequest]:
        """Trouver toutes les demandes avec un statut donné"""
        request_models = self.session.query(ReapproRequestModel).filter_by(status=status.value).all()
        return [self._model_to_request(model) for model in request_models]
    
    def find_pending_requests(self) -> List[ReapproRequest]:
        """Trouver toutes les demandes en attente"""
        return self.find_by_status(ReapproStatus.PENDING)
    
    def find_all(self) -> List[ReapproRequest]:
        """Trouver toutes les demandes"""
        request_models = self.session.query(ReapproRequestModel).all()
        return [self._model_to_request(model) for model in request_models]
    
    def delete(self, request_id: int) -> bool:
        """Supprimer une demande"""
        request_model = self.session.query(ReapproRequestModel).filter_by(id=request_id).first()
        if not request_model:
            return False
        
        self.session.delete(request_model)
        self.session.commit()
        return True
    
    def _request_to_model(self, request: ReapproRequest) -> ReapproRequestModel:
        """Convertir une entité ReapproRequest en ReapproRequestModel"""
        return ReapproRequestModel(
            store_id=request.store_id.value,
            product_id=request.product_id.value,
            quantity=request.quantity.value,
            status=request.status.value,
            requested_at=request.requested_at,
            processed_at=request.processed_at,
            notes=request.notes
        )
    
    def _update_model_from_request(self, request_model: ReapproRequestModel, request: ReapproRequest):
        """Mettre à jour un ReapproRequestModel à partir d'une entité ReapproRequest"""
        request_model.store_id = request.store_id.value
        request_model.product_id = request.product_id.value
        request_model.quantity = request.quantity.value
        request_model.status = request.status.value
        request_model.requested_at = request.requested_at
        request_model.processed_at = request.processed_at
        request_model.notes = request.notes
    
    def _model_to_request(self, request_model: ReapproRequestModel) -> ReapproRequest:
        """Convertir un ReapproRequestModel en entité ReapproRequest"""
        return ReapproRequest(
            id=request_model.id,
            store_id=StoreId(request_model.store_id),
            product_id=ProductId(request_model.product_id),
            quantity=Quantity(request_model.quantity),
            status=ReapproStatus(request_model.status),
            requested_at=request_model.requested_at,
            processed_at=request_model.processed_at,
            notes=request_model.notes
        )
