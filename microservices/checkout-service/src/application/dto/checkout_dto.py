from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from ..value_objects.checkout_value_objects import Address


@dataclass
class CreateOrderRequest:
    customer_id: int
    items: List[Dict[str, Any]]  # [{"product_id": int, "quantity": int}]
    shipping_address: Dict[str, str]
    billing_address: Optional[Dict[str, str]] = None
    notes: Optional[str] = None


@dataclass
class UpdateOrderRequest:
    order_id: int
    items: Optional[List[Dict[str, Any]]] = None
    shipping_address: Optional[Dict[str, str]] = None
    billing_address: Optional[Dict[str, str]] = None
    notes: Optional[str] = None


@dataclass
class ProcessPaymentRequest:
    order_id: int
    payment_method: str
    payment_details: Dict[str, Any]


@dataclass
class OrderResponse:
    id: int
    order_number: str
    customer_id: int
    items: List[Dict[str, Any]]
    shipping_address: Optional[Dict[str, str]]
    billing_address: Optional[Dict[str, str]]
    subtotal: float
    tax_amount: float
    shipping_amount: float
    discount_amount: float
    total: float
    status: str
    payment_status: str
    notes: Optional[str]
    created_at: str
    updated_at: str
    shipped_at: Optional[str]
    delivered_at: Optional[str]


@dataclass
class OrderListResponse:
    orders: List[OrderResponse]
    total: int
    page: int
    per_page: int


@dataclass
class OrderItemRequest:
    product_id: int
    quantity: int


@dataclass
class AddressRequest:
    street: str
    city: str
    postal_code: str
    country: str
    
    def to_address(self) -> Address:
        return Address(
            street=self.street,
            city=self.city,
            postal_code=self.postal_code,
            country=self.country
        )
