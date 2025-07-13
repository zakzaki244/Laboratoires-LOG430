from __future__ import annotations
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from dataclasses import dataclass, field

from ..value_objects.checkout_value_objects import (
    OrderNumber, Address, Money, CustomerId, ProductId, Quantity, OrderStatus, PaymentStatus
)


@dataclass
class OrderItem:
    product_id: ProductId
    quantity: Quantity
    unit_price: Money
    product_name: str
    
    def total_price(self) -> Money:
        return self.unit_price.multiply(self.quantity.value)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'product_id': self.product_id.value,
            'quantity': self.quantity.value,
            'unit_price': self.unit_price.amount,
            'product_name': self.product_name,
            'total_price': self.total_price().amount
        }


@dataclass
class Order:
    id: Optional[int] = None
    order_number: Optional[OrderNumber] = None
    customer_id: Optional[CustomerId] = None
    items: List[OrderItem] = field(default_factory=list)
    shipping_address: Optional[Address] = None
    billing_address: Optional[Address] = None
    tax_amount: Money = Money(0.0)
    shipping_amount: Money = Money(0.0)
    discount_amount: Money = Money(0.0)
    status: OrderStatus = OrderStatus.PENDING
    payment_status: PaymentStatus = PaymentStatus.PENDING
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.order_number is None:
            self.order_number = OrderNumber(self._generate_order_number())
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def _generate_order_number(self) -> str:
        return f"ORD-{uuid.uuid4().hex[:8].upper()}"
    
    def add_item(self, item: OrderItem) -> None:
        for existing_item in self.items:
            if existing_item.product_id.value == item.product_id.value:
                new_quantity = Quantity(existing_item.quantity.value + item.quantity.value)
                existing_item.quantity = new_quantity
                return
        self.items.append(item)
    
    def remove_item(self, product_id: ProductId) -> None:
        self.items = [item for item in self.items if item.product_id.value != product_id.value]
    
    def update_item_quantity(self, product_id: ProductId, quantity: Quantity) -> None:
        for item in self.items:
            if item.product_id.value == product_id.value:
                item.quantity = quantity
                return
        raise ValueError(f"Produit {product_id.value} non trouvé dans la commande")
    
    def calculate_subtotal(self) -> Money:
        total = Money(0.0)
        for item in self.items:
            total = total.add(item.total_price())
        return total
    
    def calculate_total(self) -> Money:
        subtotal = self.calculate_subtotal()
        total = subtotal.add(self.tax_amount).add(self.shipping_amount)
        return total.subtract(self.discount_amount)
    
    def confirm(self) -> None:
        if self.status != OrderStatus.PENDING:
            raise ValueError("Seules les commandes en attente peuvent être confirmées.")
        if not self.items:
            raise ValueError("Impossible de confirmer la commande vide")
        if not self.shipping_address:
            raise ValueError("L'adresse de livraison est obligatoire.")
        self.status = OrderStatus.CONFIRMED
        self.updated_at = datetime.utcnow()
    
    def cancel(self) -> None:
        if self.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            raise ValueError("Les commandes expédiées ou livrées ne peuvent pas être annulées.")
        self.status = OrderStatus.CANCELLED
        self.updated_at = datetime.utcnow()
    
    def ship(self) -> None:
        if self.status != OrderStatus.PROCESSING:
            raise ValueError("Seules les commandes en cours de traitement peuvent être expédiées.")
        self.status = OrderStatus.SHIPPED
        self.shipped_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def deliver(self) -> None:
        if self.status != OrderStatus.SHIPPED:
            raise ValueError("Seules les commandes expédiées peuvent être livrées.")
        self.status = OrderStatus.DELIVERED
        self.delivered_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def authorize_payment(self) -> None:
        if self.payment_status != PaymentStatus.PENDING:
            raise ValueError("Seuls les paiements en attente peuvent être autorisés.")
        self.payment_status = PaymentStatus.AUTHORIZED
        self.updated_at = datetime.utcnow()
    
    def capture_payment(self) -> None:
        if self.payment_status != PaymentStatus.AUTHORIZED:
            raise ValueError("Seuls les paiements autorisés peuvent être enregistrés.")
        self.payment_status = PaymentStatus.CAPTURED
        self.status = OrderStatus.PROCESSING
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'order_number': self.order_number.value if self.order_number else None,
            'customer_id': self.customer_id.value if self.customer_id else None,
            'items': [item.to_dict() for item in self.items],
            'shipping_address': {
                'street': self.shipping_address.street,
                'city': self.shipping_address.city,
                'postal_code': self.shipping_address.postal_code,
                'country': self.shipping_address.country
            } if self.shipping_address else None,
            'billing_address': {
                'street': self.billing_address.street,
                'city': self.billing_address.city,
                'postal_code': self.billing_address.postal_code,
                'country': self.billing_address.country
            } if self.billing_address else None,
            'subtotal': self.calculate_subtotal().amount,
            'tax_amount': self.tax_amount.amount,
            'shipping_amount': self.shipping_amount.amount,
            'discount_amount': self.discount_amount.amount,
            'total': self.calculate_total().amount,
            'status': self.status.value,
            'payment_status': self.payment_status.value,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'shipped_at': self.shipped_at.isoformat() if self.shipped_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None
        }
