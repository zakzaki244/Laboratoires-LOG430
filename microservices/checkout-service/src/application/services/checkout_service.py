from typing import List, Optional, Dict, Any
import requests
from datetime import datetime

from ..dto.checkout_dto import (
    CreateOrderRequest, UpdateOrderRequest, ProcessPaymentRequest,
    OrderResponse, OrderListResponse, AddressRequest
)
from ...domain.entities.order import Order, OrderItem
from ...domain.repositories.order_repository import OrderRepository
from ...domain.value_objects.checkout_value_objects import (
    CustomerId, ProductId, Quantity, Money, Address, OrderNumber, OrderStatus, PaymentStatus
)


class CheckoutService:
    def __init__(self, order_repository: OrderRepository, 
                 cart_service_url: str, product_service_url: str, 
                 customer_service_url: str, sales_service_url: str,
                 api_token: str):
        self.order_repository = order_repository
        self.cart_service_url = cart_service_url
        self.product_service_url = product_service_url
        self.customer_service_url = customer_service_url
        self.sales_service_url = sales_service_url
        self.api_token = api_token
        self.headers = {"Authorization": f"Bearer {api_token}"}
    
    def create_order(self, request: CreateOrderRequest) -> OrderResponse:
        """Créer une nouvelle commande"""
        try:
            # Vérifier que le client existe
            customer_response = requests.get(
                f"{self.customer_service_url}/customers/{request.customer_id}",
                headers=self.headers
            )
            if customer_response.status_code != 200:
                raise ValueError("Customer not found")
            
            # Créer l'entité Order
            order = Order(
                customer_id=CustomerId(request.customer_id),
                shipping_address=AddressRequest(**request.shipping_address).to_address(),
                billing_address=AddressRequest(**request.billing_address).to_address() if request.billing_address else None,
                notes=request.notes
            )
            
            # Ajouter les articles
            for item_data in request.items:
                # Récupérer les détails du produit
                product_response = requests.get(
                    f"{self.product_service_url}/products/{item_data['product_id']}",
                    headers=self.headers
                )
                if product_response.status_code != 200:
                    raise ValueError(f"Product {item_data['product_id']} not found")
                
                product = product_response.json()
                
                order_item = OrderItem(
                    product_id=ProductId(item_data['product_id']),
                    quantity=Quantity(item_data['quantity']),
                    unit_price=Money(product['price']),
                    product_name=product['name']
                )
                order.add_item(order_item)
            
            # Calculer les taxes et frais (exemple: 13% de taxes)
            subtotal = order.calculate_subtotal()
            tax_amount = Money(subtotal.amount * 0.13)  # 13% de taxes
            shipping_amount = Money(10.0)  # Frais de livraison fixes
            
            order.tax_amount = tax_amount
            order.shipping_amount = shipping_amount
            
            # Sauvegarder la commande
            saved_order = self.order_repository.save(order)
            
            return self._order_to_response(saved_order)
            
        except Exception as e:
            raise ValueError(f"Error creating order: {str(e)}")
    
    def get_order(self, order_id: int) -> Optional[OrderResponse]:
        """Récupérer une commande par ID"""
        order = self.order_repository.find_by_id(order_id)
        if not order:
            return None
        return self._order_to_response(order)
    
    def get_orders_by_customer(self, customer_id: int) -> List[OrderResponse]:
        """Récupérer toutes les commandes d'un client"""
        orders = self.order_repository.find_by_customer_id(CustomerId(customer_id))
        return [self._order_to_response(order) for order in orders]
    
    def get_all_orders(self) -> List[OrderResponse]:
        """Récupérer toutes les commandes"""
        orders = self.order_repository.find_all()
        return [self._order_to_response(order) for order in orders]
    
    def update_order(self, request: UpdateOrderRequest) -> Optional[OrderResponse]:
        """Mettre à jour une commande"""
        order = self.order_repository.find_by_id(request.order_id)
        if not order:
            return None
        
        # Seules les commandes en attente peuvent être modifiées
        if order.status != OrderStatus.PENDING:
            raise ValueError("Only pending orders can be updated")
        
        if request.items:
            order.items = []  
            for item_data in request.items:
                product_response = requests.get(
                    f"{self.product_service_url}/products/{item_data['product_id']}",
                    headers=self.headers
                )
                if product_response.status_code != 200:
                    raise ValueError(f"Product {item_data['product_id']} not found")
                
                product = product_response.json()
                order_item = OrderItem(
                    product_id=ProductId(item_data['product_id']),
                    quantity=Quantity(item_data['quantity']),
                    unit_price=Money(product['price']),
                    product_name=product['name']
                )
                order.add_item(order_item)
        
        if request.shipping_address:
            order.shipping_address = AddressRequest(**request.shipping_address).to_address()
        
        if request.billing_address:
            order.billing_address = AddressRequest(**request.billing_address).to_address()
        
        if request.notes is not None:
            order.notes = request.notes
        
        order.updated_at = datetime.utcnow()
        updated_order = self.order_repository.save(order)
        return self._order_to_response(updated_order)
    
    def confirm_order(self, order_id: int) -> Optional[OrderResponse]:
        """Confirmer une commande"""
        order = self.order_repository.find_by_id(order_id)
        if not order:
            return None
        
        order.confirm()
        confirmed_order = self.order_repository.save(order)
        return self._order_to_response(confirmed_order)
    
    def cancel_order(self, order_id: int) -> Optional[OrderResponse]:
        """Annuler une commande"""
        order = self.order_repository.find_by_id(order_id)
        if not order:
            return None
        
        order.cancel()
        cancelled_order = self.order_repository.save(order)
        return self._order_to_response(cancelled_order)
    
    def process_payment(self, request: ProcessPaymentRequest) -> Optional[OrderResponse]:
        """Traiter le paiement d'une commande"""
        order = self.order_repository.find_by_id(request.order_id)
        if not order:
            return None
        
        # Simuler le traitement du paiement
        try:
            # Autoriser le paiement
            order.authorize_payment()
            
            # Capturer le paiement
            order.capture_payment()
            
            # Créer la vente dans le service de ventes
            sale_data = {
                'order_id': order.id,
                'customer_id': order.customer_id.value,
                'total_amount': order.calculate_total().amount,
                'items': [
                    {
                        'product_id': item.product_id.value,
                        'quantity': item.quantity.value,
                        'unit_price': item.unit_price.amount
                    }
                    for item in order.items
                ]
            }
            
            sales_response = requests.post(
                f"{self.sales_service_url}/sales",
                json=sale_data,
                headers=self.headers
            )
            
            if sales_response.status_code != 201:
                order.payment_status = PaymentStatus.FAILED
                order.status = OrderStatus.PENDING
            
            processed_order = self.order_repository.save(order)
            return self._order_to_response(processed_order)
            
        except Exception as e:
            order.payment_status = PaymentStatus.FAILED
            self.order_repository.save(order)
            raise ValueError(f"Payment processing failed: {str(e)}")
    
    def ship_order(self, order_id: int) -> Optional[OrderResponse]:
        """Expédier une commande"""
        order = self.order_repository.find_by_id(order_id)
        if not order:
            return None
        
        order.ship()
        shipped_order = self.order_repository.save(order)
        return self._order_to_response(shipped_order)
    
    def deliver_order(self, order_id: int) -> Optional[OrderResponse]:
        """Livrer une commande"""
        order = self.order_repository.find_by_id(order_id)
        if not order:
            return None
        
        order.deliver()
        delivered_order = self.order_repository.save(order)
        return self._order_to_response(delivered_order)
    
    def checkout_from_cart(self, customer_id: int, shipping_address: Dict[str, str], 
                          billing_address: Optional[Dict[str, str]] = None, 
                          notes: Optional[str] = None) -> OrderResponse:
        """Créer une commande à partir du panier actif"""
        # Récupérer le panier actif
        cart_response = requests.get(
            f"{self.cart_service_url}/customers/{customer_id}/cart",
            headers=self.headers
        )
        
        if cart_response.status_code != 200:
            raise ValueError("No active cart found")
        
        cart_data = cart_response.json()
        
        # Convertir les articles du panier en articles de commande
        order_items = []
        for item in cart_data['items']:
            order_items.append({
                'product_id': item['product_id'],
                'quantity': item['quantity']
            })
        
        # Créer la commande
        create_request = CreateOrderRequest(
            customer_id=customer_id,
            items=order_items,
            shipping_address=shipping_address,
            billing_address=billing_address,
            notes=notes
        )
        
        order_response = self.create_order(create_request)
        
        # Vider le panier après création de commande
        requests.post(
            f"{self.cart_service_url}/customers/{customer_id}/cart/clear",
            headers=self.headers
        )
        
        return order_response
    
    def _order_to_response(self, order: Order) -> OrderResponse:
        """Convertir une entité Order en OrderResponse"""
        return OrderResponse(
            id=order.id,
            order_number=order.order_number.value,
            customer_id=order.customer_id.value,
            items=[item.to_dict() for item in order.items],
            shipping_address={
                'street': order.shipping_address.street,
                'city': order.shipping_address.city,
                'postal_code': order.shipping_address.postal_code,
                'country': order.shipping_address.country
            } if order.shipping_address else None,
            billing_address={
                'street': order.billing_address.street,
                'city': order.billing_address.city,
                'postal_code': order.billing_address.postal_code,
                'country': order.billing_address.country
            } if order.billing_address else None,
            subtotal=order.calculate_subtotal().amount,
            tax_amount=order.tax_amount.amount,
            shipping_amount=order.shipping_amount.amount,
            discount_amount=order.discount_amount.amount,
            total=order.calculate_total().amount,
            status=order.status.value,
            payment_status=order.payment_status.value,
            notes=order.notes,
            created_at=order.created_at.isoformat() if order.created_at else None,
            updated_at=order.updated_at.isoformat() if order.updated_at else None,
            shipped_at=order.shipped_at.isoformat() if order.shipped_at else None,
            delivered_at=order.delivered_at.isoformat() if order.delivered_at else None
        )
