from __future__ import annotations
from typing import Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass

from ..value_objects.inventory_value_objects import (
    StoreId, ProductId, Quantity, ReapproStatus
)


@dataclass
class ReapproRequest:
    id: Optional[int] = None
    store_id: Optional[StoreId] = None
    product_id: Optional[ProductId] = None
    quantity: Optional[Quantity] = None
    status: ReapproStatus = ReapproStatus.PENDING
    requested_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        if self.requested_at is None:
            self.requested_at = datetime.utcnow()
    
    def approve(self, notes: Optional[str] = None) -> None:
        """Approuver la demande de réapprovisionnement"""
        if self.status != ReapproStatus.PENDING:
            raise ValueError("Seules les demandes en attente peuvent être approuvées.")
        
        self.status = ReapproStatus.APPROVED
        self.processed_at = datetime.utcnow()
        if notes:
            self.notes = notes
    
    def reject(self, notes: Optional[str] = None) -> None:
        """Rejeter la demande de réapprovisionnement"""
        if self.status != ReapproStatus.PENDING:
            raise ValueError("Seules les demandes en attente peuvent être rejetées.")
        
        self.status = ReapproStatus.REJECTED
        self.processed_at = datetime.utcnow()
        if notes:
            self.notes = notes
    
    def complete(self) -> None:
        """Marquer la demande comme terminée"""
        if self.status != ReapproStatus.APPROVED:
            raise ValueError("Seules les demandes approuvées peuvent être traitées.")
        
        self.status = ReapproStatus.COMPLETED
        self.processed_at = datetime.utcnow()
    
    def can_be_processed(self) -> bool:
        """Vérifier si la demande peut être traitée"""
        return self.status == ReapproStatus.PENDING
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'store_id': self.store_id.value if self.store_id else None,
            'product_id': self.product_id.value if self.product_id else None,
            'quantity': self.quantity.value if self.quantity else None,
            'status': self.status.value,
            'requested_at': self.requested_at.isoformat() if self.requested_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'notes': self.notes
        }
