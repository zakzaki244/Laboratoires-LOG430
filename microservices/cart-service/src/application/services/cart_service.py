from typing import Optional, List
from decimal import Decimal
from datetime import datetime

from ..dto import (
    CreateCartRequest, AddToCartRequest, UpdateCartItemRequest,
    CartResponse, CartItemResponse
)
from ...domain.entities import Cart, CartItem
from ...domain.repositories import (
    ICartRepository, IProductServiceAdapter, ICustomerServiceAdapter, ICacheAdapter
)
from ...domain.value_objects import CustomerReference, CartTimestamp

class CartService:
    """Service d'application pour la gestion des paniers"""
    
    def __init__(self, 
                 cart_repository: ICartRepository,
                 product_service: IProductServiceAdapter,
                 customer_service: ICustomerServiceAdapter,
                 cache_adapter: ICacheAdapter):
        self.cart_repository = cart_repository
        self.product_service = product_service
        self.customer_service = customer_service
        self.cache_adapter = cache_adapter
    
    def get_cart_by_id(self, cart_id: int) -> Optional[CartResponse]:
        """Récupérer un panier par son ID"""
        
        cache_key = f"cart:{cart_id}"
        cached_cart = self.cache_adapter.get(cache_key)
        if cached_cart:
            return CartResponse(**cached_cart)
        
        cart = self.cart_repository.get_by_id(cart_id)
        if not cart:
            return None
        
        response = self._to_response(cart)
        
        self.cache_adapter.set(cache_key, response.__dict__)
        return response
    
    def get_active_cart_by_customer(self, customer_id: int) -> Optional[CartResponse]:
        """Récupérer le panier actif d'un client"""
        
        cache_key = f"active_cart:customer:{customer_id}"
        cached_cart = self.cache_adapter.get(cache_key)
        if cached_cart:
            return CartResponse(**cached_cart)
        
        cart = self.cart_repository.get_active_by_customer(customer_id)
        if not cart:
            return None
        
        response = self._to_response(cart)
        
        self.cache_adapter.set(cache_key, response.__dict__)
        return response
    
    def create_cart(self, request: CreateCartRequest) -> CartResponse:
        """Créer un nouveau panier"""
        
        if not self.customer_service.customer_exists(request.customer_id):
            raise ValueError("Client non trouvé")
        
        # Désactiver le panier existant s'il y en a un
        existing_cart = self.cart_repository.get_active_by_customer(request.customer_id)
        if existing_cart:
            existing_cart.deactivate()
            self.cart_repository.update(existing_cart)
           
            self.cache_adapter.delete(f"active_cart:customer:{request.customer_id}")
        
        
        now = datetime.utcnow()
        cart = Cart(
            id=None,
            customer_reference=CustomerReference(request.customer_id),
            created_at=CartTimestamp(now),
            updated_at=CartTimestamp(now),
            is_active=True,
            items=[]
        )
        
        saved_cart = self.cart_repository.save(cart)
        response = self._to_response(saved_cart)
        
        
        self.cache_adapter.set(f"active_cart:customer:{request.customer_id}", response.__dict__)
        return response
    
    def add_to_cart(self, customer_id: int, request: AddToCartRequest) -> CartResponse:
        """Ajouter un article au panier"""
        # Récupérer ou créer le panier actif
        cart = self.cart_repository.get_active_by_customer(customer_id)
        if not cart:
            # Créer un nouveau panier
            create_request = CreateCartRequest(customer_id=customer_id)
            cart_response = self.create_cart(create_request)
            cart = self.cart_repository.get_by_id(cart_response.id)
        
        # Vérifier si le produit existe et est disponible
        product_info = self.product_service.get_product_info(request.product_id)
        if not product_info:
            raise ValueError("Produit non trouvé")
        
        if not self.product_service.check_product_availability(request.product_id, request.quantity):
            raise ValueError("Produit non disponible en quantité suffisante")
        
        # Ajouter l'article au panier
        cart.add_item(
            product_id=request.product_id,
            quantity=request.quantity,
            unit_price=Decimal(str(product_info['price'])),
            product_name=product_info['name']
        )
        
        # Sauvegarder
        updated_cart = self.cart_repository.update(cart)
        response = self._to_response(updated_cart)
        
       
        self._invalidate_cart_cache(customer_id, updated_cart.id)
        return response
    
    def update_cart_item(self, customer_id: int, request: UpdateCartItemRequest) -> CartResponse:
        """Mettre à jour un article du panier"""
        cart = self.cart_repository.get_active_by_customer(customer_id)
        if not cart:
            raise ValueError("Panier non trouvé")
        
        # Vérifier la disponibilité si on augmente la quantité
        if request.quantity > 0:
            current_quantity = 0
            for item in cart.items:
                if item.product_reference.product_id == request.product_id:
                    current_quantity = item.quantity.value
                    break
            
            if request.quantity > current_quantity:
                additional_quantity = request.quantity - current_quantity
                if not self.product_service.check_product_availability(request.product_id, additional_quantity):
                    raise ValueError("Produit non disponible en quantité suffisante")
        
        # Mettre à jour l'article
        if not cart.update_item_quantity(request.product_id, request.quantity):
            raise ValueError("Article non trouvé dans le panier")
        
        # Sauvegarder
        updated_cart = self.cart_repository.update(cart)
        response = self._to_response(updated_cart)
        
      
        self._invalidate_cart_cache(customer_id, updated_cart.id)
        return response
    
    def remove_from_cart(self, customer_id: int, product_id: int) -> CartResponse:
        """Supprimer un article du panier"""
        cart = self.cart_repository.get_active_by_customer(customer_id)
        if not cart:
            raise ValueError("Panier non trouvé")
        
        if not cart.remove_item(product_id):
            raise ValueError("Article non trouvé dans le panier")
        
        # Sauvegarder
        updated_cart = self.cart_repository.update(cart)
        response = self._to_response(updated_cart)
        
    
        self._invalidate_cart_cache(customer_id, updated_cart.id)
        return response
    
    def clear_cart(self, customer_id: int) -> CartResponse:
        """Vider le panier"""
        cart = self.cart_repository.get_active_by_customer(customer_id)
        if not cart:
            raise ValueError("Panier non trouvé")
        
        cart.clear()
        
        # Sauvegarder
        updated_cart = self.cart_repository.update(cart)
        response = self._to_response(updated_cart)
        
       
        self._invalidate_cart_cache(customer_id, updated_cart.id)
        return response
    
    def _to_response(self, cart: Cart) -> CartResponse:
        """Convertir une entité en DTO de réponse"""
        item_responses = [
            CartItemResponse(
                id=item.id,
                product_id=item.product_reference.product_id,
                product_name=item.product_name,
                quantity=item.quantity.value,
                unit_price=float(item.unit_price.amount),
                total_price=float(item.total_price.amount)
            )
            for item in cart.items
        ]
        
        return CartResponse(
            id=cart.id,
            customer_id=cart.customer_reference.customer_id,
            created_at=cart.created_at.to_iso_string(),
            updated_at=cart.updated_at.to_iso_string(),
            is_active=cart.is_active,
            total_amount=float(cart.total_amount.amount),
            total_items=cart.total_items,
            items=item_responses
        )
    
    def _invalidate_cart_cache(self, customer_id: int, cart_id: Optional[int] = None):
        """Invalider le cache du panier"""
        self.cache_adapter.delete(f"active_cart:customer:{customer_id}")
        if cart_id:
            self.cache_adapter.delete(f"cart:{cart_id}")
