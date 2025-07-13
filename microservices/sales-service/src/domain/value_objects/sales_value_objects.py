from dataclasses import dataclass
from typing import List, Dict, Any
from decimal import Decimal
from datetime import datetime

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
class Quantity:
    """Value object pour la quantité"""
    value: int
    
    def __post_init__(self):
        if self.value < 0:
            raise ValueError("La quantité ne peut pas être négative")
    
    def add(self, other: 'Quantity') -> 'Quantity':
        """Additionner deux quantités"""
        return Quantity(self.value + other.value)

@dataclass(frozen=True)
class ProductReference:
    """Value object pour la référence vers un produit"""
    product_id: int
    
    def __post_init__(self):
        if self.product_id <= 0:
            raise ValueError("L'ID du produit doit être positif")

@dataclass(frozen=True)
class StoreReference:
    """Value object pour la référence vers un magasin"""
    store_id: int
    
    def __post_init__(self):
        if self.store_id <= 0:
            raise ValueError("L'ID du magasin doit être positif")

@dataclass(frozen=True)
class SaleTimestamp:
    """Value object pour l'horodatage de la vente"""
    value: datetime
    
    def __post_init__(self):
        if not isinstance(self.value, datetime):
            raise ValueError("L'horodatage doit être un objet datetime")
    
    def to_iso_string(self) -> str:
        """Convertir en chaîne ISO"""
        return self.value.isoformat()
