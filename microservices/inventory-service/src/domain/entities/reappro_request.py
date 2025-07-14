from __future__ import annotations
from typing import Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass

from ..value_objects.inventory_value_objects import (
    StoreId, ProductId, Quantity, ReapproStatus, StockQuantity, MinimumThreshold, MaximumThreshold
)


@dataclass
class InventoryItem:
    id: Optional[int] = None
    store_id: Optional[StoreId] = None
    product_id: Optional[ProductId] = None
    current_stock: Optional[StockQuantity] = None
    reserved_stock: Optional[StockQuantity] = None
    minimum_stock: Optional[MinimumThreshold] = None
    maximum_stock: Optional[MaximumThreshold] = None
    last_updated: Optional[datetime] = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.utcnow()
        if self.reserved_stock is None:
            self.reserved_stock = StockQuantity(0)
    
    @property
    def available_stock(self) -> int:
        """Stock disponible (stock actuel - stock réservé)"""
        if self.current_stock is None or self.reserved_stock is None:
            return 0
        return self.current_stock.value - self.reserved_stock.value
    
    @property
    def is_low_stock(self) -> bool:
        """Vérifier si le stock est faible"""
        if self.minimum_stock is None:
            return False
        return self.available_stock <= self.minimum_stock.value
    
    def update_stock(self, quantity: int, movement_type: str) -> None:
        """Mettre à jour le stock"""
        if self.current_stock is None:
            self.current_stock = StockQuantity(0)
        
        if movement_type == 'IN':
            self.current_stock = StockQuantity(self.current_stock.value + quantity)
        elif movement_type == 'OUT':
            new_stock = self.current_stock.value - quantity
            if new_stock < 0:
                raise ValueError("Stock insuffisant")
            self.current_stock = StockQuantity(new_stock)
        elif movement_type == 'RESERVED':
            if self.reserved_stock is None:
                self.reserved_stock = StockQuantity(0)
            self.reserved_stock = StockQuantity(self.reserved_stock.value + quantity)
        elif movement_type == 'RELEASED':
            if self.reserved_stock is None:
                self.reserved_stock = StockQuantity(0)
            self.reserved_stock = StockQuantity(max(0, self.reserved_stock.value - quantity))
        
        self.last_updated = datetime.utcnow()
    
    def reserve_stock(self, quantity: int) -> bool:
        """Réserver du stock"""
        if self.available_stock >= quantity:
            self.update_stock(quantity, 'RESERVED')
            return True
        return False
    
    def release_stock(self, quantity: int) -> None:
        """Libérer du stock réservé"""
        self.update_stock(quantity, 'RELEASED')
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'store_id': self.store_id.value if self.store_id else None,
            'product_id': self.product_id.value if self.product_id else None,
            'current_stock': self.current_stock.value if self.current_stock else None,
            'reserved_stock': self.reserved_stock.value if self.reserved_stock else None,
            'minimum_stock': self.minimum_stock.value if self.minimum_stock else None,
            'maximum_stock': self.maximum_stock.value if self.maximum_stock else None,
            'available_stock': self.available_stock,
            'is_low_stock': self.is_low_stock,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }


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
