from dataclasses import dataclass
from typing import List, Optional

@dataclass
class AddToCartRequest:
    """DTO pour ajouter un article au panier"""
    product_id: int
    quantity: int

@dataclass
class UpdateCartItemRequest:
    """DTO pour mettre à jour un article du panier"""
    product_id: int
    quantity: int

@dataclass
class CartItemResponse:
    """DTO de réponse pour un article du panier"""
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    total_price: float

@dataclass
class CartResponse:
    """DTO de réponse pour un panier"""
    id: int
    customer_id: int
    created_at: str
    updated_at: str
    is_active: bool
    total_amount: float
    total_items: int
    items: List[CartItemResponse]

@dataclass
class CreateCartRequest:
    """DTO pour créer un panier"""
    customer_id: int
