from dataclasses import dataclass
from typing import Optional, Dict, Any
from decimal import Decimal

from ..value_objects import Money, Category, ProductName, Stock, StoreReference

@dataclass
class Product:
    """Entité produit représentant un produit dans le domaine"""
    id: Optional[int]
    name: ProductName
    category: Category
    price: Money
    stock: Stock
    store_reference: StoreReference
    
    def update_stock(self, quantity: int) -> None:
        """Mettre à jour le stock du produit"""
        self.stock = self.stock.add(quantity)
    
    def reduce_stock(self, quantity: int) -> None:
        """Réduire le stock du produit"""
        self.stock = self.stock.remove(quantity)
    
    def update_price(self, new_price: Money) -> None:
        """Mettre à jour le prix du produit"""
        self.price = new_price
    
    def change_category(self, new_category: Category) -> None:
        """Changer la catégorie du produit"""
        self.category = new_category
    
    def rename(self, new_name: ProductName) -> None:
        """Renommer le produit"""
        self.name = new_name
    
    def is_available(self, required_quantity: int) -> bool:
        """Vérifier la disponibilité du produit"""
        return self.stock.is_available(required_quantity)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire pour la sérialisation"""
        return {
            'id': self.id,
            'name': self.name.value,
            'category': self.category.name,
            'price': float(self.price.amount),
            'currency': self.price.currency,
            'stock': self.stock.quantity,
            'store_id': self.store_reference.store_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Product':
        """Créer un produit à partir d'un dictionnaire"""
        return cls(
            id=data.get('id'),
            name=ProductName(data['name']),
            category=Category(data['category']),
            price=Money(Decimal(str(data['price'])), data.get('currency', 'CAD')),
            stock=Stock(data['stock']),
            store_reference=StoreReference(data['store_id'])
        )
