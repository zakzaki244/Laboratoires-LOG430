from enum import Enum
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


class ReapproStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


@dataclass
class StockLevel:
    current_stock: int
    reserved_stock: int
    minimum_stock: int
    maximum_stock: int
    
    @property
    def available_stock(self) -> int:
        return self.current_stock - self.reserved_stock
    
    @property
    def is_low_stock(self) -> bool:
        return self.available_stock <= self.minimum_stock


@dataclass
class StockMovement:
    movement_type: str  # 'IN', 'OUT', 'RESERVED', 'RELEASED'
    quantity: int
    reference: Optional[str] = None
    timestamp: Optional[datetime] = None
