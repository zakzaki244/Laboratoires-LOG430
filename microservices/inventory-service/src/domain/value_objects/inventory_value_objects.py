from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ReapproStatus(Enum):
    PENDING = "en attente"
    APPROVED = "approuvée"
    REJECTED = "rejetée"
    COMPLETED = "terminée"


@dataclass(frozen=True)
class StoreId:
    value: int
    
    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("L'identifiant du magasin doit être positif.")


@dataclass(frozen=True)
class ProductId:
    value: int
    
    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("L'ID du produit doit être positif.")


@dataclass(frozen=True)
class Quantity:
    value: int
    
    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("La quantité doit être positive.")


@dataclass(frozen=True)
class RequestId:
    value: int
    
    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("L'ID de la demande doit être positif.")
