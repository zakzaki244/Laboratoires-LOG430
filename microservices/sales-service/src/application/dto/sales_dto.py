from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class SaleItemRequest:
    """DTO pour un article de vente"""
    product_id: int
    quantity: int
    unit_price: float

@dataclass
class CreateSaleRequest:
    """DTO pour créer une vente"""
    store_id: int
    items: List[SaleItemRequest]

@dataclass
class UpdateSaleRequest:
    """DTO pour mettre à jour une vente"""
    items: Optional[List[SaleItemRequest]] = None

@dataclass
class SaleItemResponse:
    """DTO de réponse pour un article de vente"""
    id: int
    product_id: int
    quantity: int
    unit_price: float
    total_price: float

@dataclass
class SaleResponse:
    """DTO de réponse pour une vente"""
    id: int
    timestamp: str
    total_amount: float
    store_id: int
    items: List[SaleItemResponse]

@dataclass
class SalesSummaryRequest:
    """DTO pour demander un résumé des ventes"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    store_id: Optional[int] = None

@dataclass
class SalesSummaryResponse:
    """DTO de réponse pour un résumé des ventes"""
    total_sales: int
    total_amount: float
    average_sale_amount: float
    best_selling_products: List[dict]
