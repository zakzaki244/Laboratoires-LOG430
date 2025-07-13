from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from datetime import datetime

@dataclass(frozen=True)
class CartQuantity:
    """Value object pour la quantité dans le panier"""
    value: int
    
    def __post_init__(self):
        if self.value < 0:
            raise ValueError("La quantité ne peut pas être négative")
        if self.value > 100:
            raise ValueError("La quantité ne peut pas dépasser 100")
    
    def add(self, quantity: int) -> 'CartQuantity':
        """Ajouter une quantité"""
        return CartQuantity(self.value + quantity)
    
    def subtract(self, quantity: int) -> 'CartQuantity':
        """Retirer une quantité"""
        new_value = self.value - quantity
        if new_value < 0:
            raise ValueError("La quantité ne peut pas être négative")
        return CartQuantity(new_value)

@dataclass(frozen=True)
class Money:
    """Value object pour représenter l'argent"""
    amount: Decimal
    currency: str = "CAD"
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Le montant ne peut pas être négatif")
        if not self.currency:
            raise ValueError("La devise est requise")
    
    def add(self, other: 'Money') -> 'Money':
        """Additionner deux montants"""
        if self.currency != other.currency:
            raise ValueError("Les devises doivent être identiques")
        return Money(self.amount + other.amount, self.currency)
    
    def multiply(self, factor: int) -> 'Money':
        """Multiplier un montant"""
        return Money(self.amount * factor, self.currency)

@dataclass(frozen=True)
class ProductReference:
    """Value object pour la référence produit"""
    product_id: int
    
    def __post_init__(self):
        if self.product_id <= 0:
            raise ValueError("L'ID du produit doit être positif")

@dataclass(frozen=True)
class CustomerReference:
    """Value object pour la référence client"""
    customer_id: int
    
    def __post_init__(self):
        if self.customer_id <= 0:
            raise ValueError("L'ID du client doit être positif")

@dataclass(frozen=True)
class CartTimestamp:
    """Value object pour l'horodatage du panier"""
    value: datetime
    
    def __post_init__(self):
        if not isinstance(self.value, datetime):
            raise ValueError("L'horodatage doit être un objet datetime")
    
    def to_iso_string(self) -> str:
        """Convertir en chaîne ISO"""
        return self.value.isoformat()
