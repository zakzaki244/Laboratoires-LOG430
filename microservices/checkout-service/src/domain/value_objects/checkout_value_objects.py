from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentStatus(Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass(frozen=True)
class OrderNumber:
    value: str
    
    def __post_init__(self):
        if not self.value or len(self.value) < 8:
            raise ValueError("Le numéro de commande doit comporter au moins 8 caractères.")


@dataclass(frozen=True)
class Address:
    street: str
    city: str
    postal_code: str
    country: str
    
    def __post_init__(self):
        if not self.street or not self.city or not self.postal_code or not self.country:
            raise ValueError("Tous les champs d'adresse sont obligatoires.")


@dataclass(frozen=True)
class Money:
    amount: float
    currency: str = "CAD"
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Le montant ne peut pas être négatif.")
        if not self.currency:
            raise ValueError("Une devise est requise.")
    
    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Impossible d'ajouter différentes devises")
        return Money(self.amount + other.amount, self.currency)
    
    def subtract(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Impossible de soustraire des devises différentes")
        return Money(self.amount - other.amount, self.currency)
    
    def multiply(self, factor: float) -> 'Money':
        return Money(self.amount * factor, self.currency)


@dataclass(frozen=True)
class CustomerId:
    value: int
    
    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("L'identifiant client doit être positif.")


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
class CartId:
    value: int
    
    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("L'ID du panier doit être positif.")


@dataclass(frozen=True)
class CustomerReference:
    value: int
    
    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("La référence client doit être positive.")


@dataclass(frozen=True)
class PaymentMethod:
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Le mode de paiement est requis.")


@dataclass(frozen=True)
class OrderTimestamp:
    value: datetime
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("L'horodatage de la commande est requis.")
