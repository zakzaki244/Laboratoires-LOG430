from dataclasses import dataclass
from typing import Optional
from decimal import Decimal

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

@dataclass(frozen=True)
class Category:
    """Value object pour la catégorie de produit"""
    name: str
    
    def __post_init__(self):
        if not self.name or len(self.name.strip()) < 2:
            raise ValueError("La catégorie doit contenir au moins 2 caractères")

@dataclass(frozen=True)
class ProductName:
    """Value object pour le nom du produit"""
    value: str
    
    def __post_init__(self):
        if not self.value or len(self.value.strip()) < 2:
            raise ValueError("Le nom du produit doit contenir au moins 2 caractères")
        if len(self.value) > 255:
            raise ValueError("Le nom du produit ne peut pas dépasser 255 caractères")

@dataclass(frozen=True)
class Stock:
    """Value object pour le stock"""
    quantity: int
    
    def __post_init__(self):
        if self.quantity < 0:
            raise ValueError("Le stock ne peut pas être négatif")
    
    def add(self, quantity: int) -> 'Stock':
        """Ajouter du stock"""
        return Stock(self.quantity + quantity)
    
    def remove(self, quantity: int) -> 'Stock':
        """Retirer du stock"""
        new_quantity = self.quantity - quantity
        if new_quantity < 0:
            raise ValueError("Stock insuffisant")
        return Stock(new_quantity)
    
    def is_available(self, required_quantity: int) -> bool:
        """Vérifier la disponibilité du stock"""
        return self.quantity >= required_quantity

@dataclass(frozen=True)
class StoreReference:
    """Value object pour la référence vers un magasin"""
    store_id: int
    
    def __post_init__(self):
        if self.store_id <= 0:
            raise ValueError("L'ID du magasin doit être positif")
