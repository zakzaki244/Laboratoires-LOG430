from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

from ..value_objects import Money, CartQuantity, ProductReference, CustomerReference, CartTimestamp

@dataclass
class CartItem:
    """Entité représentant un article dans le panier"""
    id: Optional[int]
    product_reference: ProductReference
    quantity: CartQuantity
    unit_price: Money
    product_name: str
    
    @property
    def total_price(self) -> Money:
        """Calculer le prix total de l'article"""
        return self.unit_price.multiply(self.quantity.value)
    
    def update_quantity(self, new_quantity: CartQuantity) -> None:
        """Mettre à jour la quantité"""
        self.quantity = new_quantity
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'product_id': self.product_reference.product_id,
            'product_name': self.product_name,
            'quantity': self.quantity.value,
            'unit_price': float(self.unit_price.amount),
            'total_price': float(self.total_price.amount)
        }

@dataclass
class Cart:
    """Entité représentant un panier"""
    id: Optional[int]
    customer_reference: CustomerReference
    created_at: CartTimestamp
    updated_at: CartTimestamp
    is_active: bool
    items: List[CartItem] = field(default_factory=list)
    
    def add_item(self, product_id: int, quantity: int, unit_price: Decimal, product_name: str) -> None:
        """Ajouter un article au panier"""
        # Vérifier si l'article existe déjà
        for item in self.items:
            if item.product_reference.product_id == product_id:
                # Mettre à jour la quantité
                new_quantity = item.quantity.add(quantity)
                item.update_quantity(new_quantity)
                self.updated_at = CartTimestamp(datetime.utcnow())
                return
        
        # Ajouter un nouvel article
        new_item = CartItem(
            id=None,
            product_reference=ProductReference(product_id),
            quantity=CartQuantity(quantity),
            unit_price=Money(unit_price),
            product_name=product_name
        )
        self.items.append(new_item)
        self.updated_at = CartTimestamp(datetime.utcnow())
    
    def remove_item(self, product_id: int) -> bool:
        """Supprimer un article du panier"""
        for i, item in enumerate(self.items):
            if item.product_reference.product_id == product_id:
                del self.items[i]
                self.updated_at = CartTimestamp(datetime.utcnow())
                return True
        return False
    
    def update_item_quantity(self, product_id: int, new_quantity: int) -> bool:
        """Mettre à jour la quantité d'un article"""
        for item in self.items:
            if item.product_reference.product_id == product_id:
                if new_quantity == 0:
                    return self.remove_item(product_id)
                else:
                    item.update_quantity(CartQuantity(new_quantity))
                    self.updated_at = CartTimestamp(datetime.utcnow())
                    return True
        return False
    
    def clear(self) -> None:
        """Vider le panier"""
        self.items.clear()
        self.updated_at = CartTimestamp(datetime.utcnow())
    
    def deactivate(self) -> None:
        """Désactiver le panier"""
        self.is_active = False
        self.updated_at = CartTimestamp(datetime.utcnow())
    
    @property
    def total_amount(self) -> Money:
        """Calculer le montant total du panier"""
        if not self.items:
            return Money(Decimal('0.00'))
        
        total = Money(Decimal('0.00'))
        for item in self.items:
            total = total.add(item.total_price)
        return total
    
    @property
    def total_items(self) -> int:
        """Compter le nombre total d'articles"""
        return sum(item.quantity.value for item in self.items)
    
    def is_empty(self) -> bool:
        """Vérifier si le panier est vide"""
        return len(self.items) == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'customer_id': self.customer_reference.customer_id,
            'created_at': self.created_at.to_iso_string(),
            'updated_at': self.updated_at.to_iso_string(),
            'is_active': self.is_active,
            'total_amount': float(self.total_amount.amount),
            'total_items': self.total_items,
            'items': [item.to_dict() for item in self.items]
        }
