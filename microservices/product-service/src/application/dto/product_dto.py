from dataclasses import dataclass
from typing import Optional
from decimal import Decimal

@dataclass
class CreateProductRequest:
    """DTO pour créer un produit"""
    name: str
    category: str
    price: float
    store_id: int
    stock: int = 0
    currency: str = "CAD"

@dataclass
class UpdateProductRequest:
    """DTO pour mettre à jour un produit"""
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    store_id: Optional[int] = None
    currency: Optional[str] = None

@dataclass
class ProductResponse:
    """DTO pour la réponse produit"""
    id: int
    name: str
    category: str
    price: float
    currency: str
    stock: int
    store_id: int

@dataclass
class UpdateStockRequest:
    """DTO pour mettre à jour le stock"""
    quantity: int

@dataclass
class ProductSearchRequest:
    """DTO pour rechercher des produits"""
    term: str
