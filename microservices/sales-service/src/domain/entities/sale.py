from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

from ..value_objects import Money, Quantity, ProductReference, StoreReference, SaleTimestamp

@dataclass
class SaleItem:
    """Entité représentant un article de vente"""
    id: Optional[int]
    product_reference: ProductReference
    quantity: Quantity
    unit_price: Money
    
    @property
    def total_price(self) -> Money:
        """Calculer le prix total de l'article"""
        return self.unit_price.multiply(self.quantity.value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'product_id': self.product_reference.product_id,
            'quantity': self.quantity.value,
            'unit_price': float(self.unit_price.amount),
            'total_price': float(self.total_price.amount)
        }

@dataclass
class Sale:
    """Entité représentant une vente"""
    id: Optional[int]
    timestamp: SaleTimestamp
    store_reference: StoreReference
    items: List[SaleItem] = field(default_factory=list)
    
    def add_item(self, item: SaleItem) -> None:
        """Ajouter un article à la vente"""
        for existing_item in self.items:
            if existing_item.product_reference.product_id == item.product_reference.product_id:
                new_quantity = existing_item.quantity.add(item.quantity)
                existing_item.quantity = new_quantity
                return
        
        self.items.append(item)
    
    def remove_item(self, product_id: int) -> bool:
        """Supprimer un article de la vente"""
        for i, item in enumerate(self.items):
            if item.product_reference.product_id == product_id:
                del self.items[i]
                return True
        return False
    
    def update_item_quantity(self, product_id: int, new_quantity: Quantity) -> bool:
        """Mettre à jour la quantité d'un article"""
        for item in self.items:
            if item.product_reference.product_id == product_id:
                item.quantity = new_quantity
                return True
        return False
    
    @property
    def total_amount(self) -> Money:
        """Calculer le montant total de la vente"""
        if not self.items:
            return Money(Decimal('0.00'))
        
        total = Money(Decimal('0.00'))
        for item in self.items:
            total = total.add(item.total_price)
        return total
    
    def validate(self) -> bool:
        """Valider la vente"""
        if not self.items:
            raise ValueError("Une vente doit contenir au moins un article")
        
        for item in self.items:
            if item.quantity.value <= 0:
                raise ValueError("La quantité de chaque article doit être positive")
            if item.unit_price.amount <= 0:
                raise ValueError("Le prix unitaire de chaque article doit être positif")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.to_iso_string(),
            'total_amount': float(self.total_amount.amount),
            'store_id': self.store_reference.store_id,
            'items': [item.to_dict() for item in self.items]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Sale':
        """Créer une vente à partir d'un dictionnaire"""
        items = []
        for item_data in data.get('items', []):
            item = SaleItem(
                id=item_data.get('id'),
                product_reference=ProductReference(item_data['product_id']),
                quantity=Quantity(item_data['quantity']),
                unit_price=Money(Decimal(str(item_data['unit_price'])))
            )
            items.append(item)
        
        return cls(
            id=data.get('id'),
            timestamp=SaleTimestamp(datetime.fromisoformat(data['timestamp'])),
            store_reference=StoreReference(data['store_id']),
            items=items
        )
