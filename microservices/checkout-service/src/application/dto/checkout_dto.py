from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from ...domain.value_objects.checkout_value_objects import Address


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
class UpdateOrderStatusRequest:
    order_id: int
    status: str
    notes: Optional[str] = None


@dataclass
class ProcessPaymentRequest:
    order_id: int
    payment_method: str
    payment_details: Dict[str, Any]


@dataclass
class PaymentRequest:
    order_id: int
    payment_method: str
    amount: float
    payment_details: Dict[str, Any]


@dataclass
class PaymentResponse:
    id: int
    order_id: int
    payment_method: str
    amount: float
    status: str
    transaction_id: Optional[str]
    created_at: str
    processed_at: Optional[str]


@dataclass
class OrderItemResponse:
    id: int
    product_id: int
    quantity: int
    unit_price: float
    total_price: float
    product_name: Optional[str] = None
    product_sku: Optional[str] = None


@dataclass
class OrderResponse:
    id: int
    order_number: str
    customer_id: int
    items: List[OrderItemResponse]
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
