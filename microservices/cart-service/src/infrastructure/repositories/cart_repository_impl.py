from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime
import requests
import redis
import json

from ..database import CartModel, CartItemModel
from ...domain.entities import Cart, CartItem
from ...domain.repositories import ICartRepository, IProductServiceAdapter, ICustomerServiceAdapter, ICacheAdapter
from ...domain.value_objects import (
    CustomerReference, CartTimestamp, ProductReference, 
    CartQuantity, Money
)

class CartRepository(ICartRepository):
    """Implémentation du repository des paniers"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, cart_id: int) -> Optional[Cart]:
        """Récupérer un panier par son ID"""
        model = self.session.query(CartModel).filter(CartModel.id == cart_id).first()
        return self._to_entity(model) if model else None
    
    def get_active_by_customer(self, customer_id: int) -> Optional[Cart]:
        """Récupérer le panier actif d'un client"""
        model = self.session.query(CartModel).filter(
            CartModel.customer_id == customer_id,
            CartModel.is_active == True
        ).first()
        return self._to_entity(model) if model else None
    
    def get_by_customer(self, customer_id: int) -> List[Cart]:
        """Récupérer tous les paniers d'un client"""
        models = self.session.query(CartModel).filter(
            CartModel.customer_id == customer_id
        ).all()
        return [self._to_entity(model) for model in models]
    
    def save(self, cart: Cart) -> Cart:
        """Sauvegarder un panier"""
        model = CartModel(
            customer_id=cart.customer_reference.customer_id,
            created_at=cart.created_at.value,
            updated_at=cart.updated_at.value,
            is_active=cart.is_active
        )
        self.session.add(model)
        self.session.flush()  # Pour obtenir l'ID
        
        # Sauvegarder les articles
        for item in cart.items:
            item_model = CartItemModel(
                cart_id=model.id,
                product_id=item.product_reference.product_id,
                product_name=item.product_name,
                quantity=item.quantity.value,
                unit_price=item.unit_price.amount,
                total_price=item.total_price.amount
            )
            self.session.add(item_model)
        
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)
    
    def update(self, cart: Cart) -> Cart:
        """Mettre à jour un panier"""
        model = self.session.query(CartModel).filter(CartModel.id == cart.id).first()
        if not model:
            raise ValueError("Panier non trouvé")
        
        # Mettre à jour le panier
        model.updated_at = cart.updated_at.value
        model.is_active = cart.is_active
        
        # Supprimer les anciens articles
        self.session.query(CartItemModel).filter(CartItemModel.cart_id == cart.id).delete()
        
        # Ajouter les nouveaux articles
        for item in cart.items:
            item_model = CartItemModel(
                cart_id=model.id,
                product_id=item.product_reference.product_id,
                product_name=item.product_name,
                quantity=item.quantity.value,
                unit_price=item.unit_price.amount,
                total_price=item.total_price.amount
            )
            self.session.add(item_model)
        
        self.session.commit()
        return self._to_entity(model)
    
    def delete(self, cart_id: int) -> bool:
        """Supprimer un panier"""
        model = self.session.query(CartModel).filter(CartModel.id == cart_id).first()
        if not model:
            return False
        
        self.session.delete(model)
        self.session.commit()
        return True
    
    def _to_entity(self, model: CartModel) -> Cart:
        """Convertir un modèle en entité"""
        items = []
        for item_model in model.items:
            item = CartItem(
                id=item_model.id,
                product_reference=ProductReference(item_model.product_id),
                quantity=CartQuantity(item_model.quantity),
                unit_price=Money(Decimal(str(item_model.unit_price))),
                product_name=item_model.product_name
            )
            items.append(item)
        
        return Cart(
            id=model.id,
            customer_reference=CustomerReference(model.customer_id),
            created_at=CartTimestamp(model.created_at),
            updated_at=CartTimestamp(model.updated_at),
            is_active=model.is_active,
            items=items
        )

class ProductServiceAdapter(IProductServiceAdapter):
    """Adaptateur pour le service des produits"""
    
    def __init__(self, product_service_url: str, api_token: str):
        self.product_service_url = product_service_url
        self.api_token = api_token
    
    def get_product_info(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Récupérer les informations d'un produit"""
        try:
            headers = {'Authorization': f'Bearer {self.api_token}'}
            response = requests.get(
                f'{self.product_service_url}/products/{product_id}',
                headers=headers,
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None
    
    def check_product_availability(self, product_id: int, required_quantity: int) -> bool:
        """Vérifier la disponibilité d'un produit"""
        product_info = self.get_product_info(product_id)
        if not product_info:
            return False
        
        return product_info.get('stock', 0) >= required_quantity

class CustomerServiceAdapter(ICustomerServiceAdapter):
    """Adaptateur pour le service des clients"""
    
    def __init__(self, customer_service_url: str, api_token: str):
        self.customer_service_url = customer_service_url
        self.api_token = api_token
    
    def customer_exists(self, customer_id: int) -> bool:
        """Vérifier si un client existe"""
        try:
            headers = {'Authorization': f'Bearer {self.api_token}'}
            response = requests.get(
                f'{self.customer_service_url}/customers/{customer_id}',
                headers=headers,
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False

class RedisCacheAdapter(ICacheAdapter):
    """Adaptateur pour le cache Redis"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Récupérer une valeur du cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception:
            return None
    
    def set(self, key: str, value: Dict[str, Any], ttl: int = 3600) -> bool:
        """Stocker une valeur dans le cache"""
        try:
            self.redis_client.setex(key, ttl, json.dumps(value, default=str))
            return True
        except Exception:
            return False
    
    def delete(self, key: str) -> bool:
        """Supprimer une valeur du cache"""
        try:
            self.redis_client.delete(key)
            return True
        except Exception:
            return False
