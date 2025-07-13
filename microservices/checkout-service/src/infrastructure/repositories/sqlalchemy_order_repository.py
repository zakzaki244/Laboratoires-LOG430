from typing import List, Optional
from sqlalchemy.orm import Session

from ...domain.entities.order import Order, OrderItem
from ...domain.repositories.order_repository import OrderRepository
from ...domain.value_objects.checkout_value_objects import (
    CustomerId, OrderNumber, ProductId, Quantity, Money, Address, OrderStatus, PaymentStatus
)
from ..database.models import OrderModel, OrderItemModel


class SQLAlchemyOrderRepository(OrderRepository):
    def __init__(self, session: Session):
        self.session = session
    
    def save(self, order: Order) -> Order:
        """Sauvegarder une commande"""
        if order.id is None:
            # Nouvelle commande
            order_model = self._order_to_model(order)
            self.session.add(order_model)
            self.session.commit()
            self.session.refresh(order_model)
            return self._model_to_order(order_model)
        else:
            # Commande existante
            order_model = self.session.query(OrderModel).filter_by(id=order.id).first()
            if not order_model:
                raise ValueError(f"Order with id {order.id} not found")
            
            self._update_model_from_order(order_model, order)
            self.session.commit()
            self.session.refresh(order_model)
            return self._model_to_order(order_model)
    
    def find_by_id(self, order_id: int) -> Optional[Order]:
        """Trouver une commande par ID"""
        order_model = self.session.query(OrderModel).filter_by(id=order_id).first()
        if not order_model:
            return None
        return self._model_to_order(order_model)
    
    def find_by_order_number(self, order_number: OrderNumber) -> Optional[Order]:
        """Trouver une commande par numéro"""
        order_model = self.session.query(OrderModel).filter_by(order_number=order_number.value).first()
        if not order_model:
            return None
        return self._model_to_order(order_model)
    
    def find_by_customer_id(self, customer_id: CustomerId) -> List[Order]:
        """Trouver toutes les commandes d'un client"""
        order_models = self.session.query(OrderModel).filter_by(customer_id=customer_id.value).all()
        return [self._model_to_order(model) for model in order_models]
    
    def find_all(self) -> List[Order]:
        """Trouver toutes les commandes"""
        order_models = self.session.query(OrderModel).all()
        return [self._model_to_order(model) for model in order_models]
    
    def delete(self, order_id: int) -> bool:
        """Supprimer une commande"""
        order_model = self.session.query(OrderModel).filter_by(id=order_id).first()
        if not order_model:
            return False
        
        self.session.delete(order_model)
        self.session.commit()
        return True
    
    def _order_to_model(self, order: Order) -> OrderModel:
        """Convertir une entité Order en OrderModel"""
        order_model = OrderModel(
            order_number=order.order_number.value,
            customer_id=order.customer_id.value,
            total_amount=order.calculate_subtotal().amount,
            tax_amount=order.tax_amount.amount,
            shipping_amount=order.shipping_amount.amount,
            discount_amount=order.discount_amount.amount,
            final_amount=order.calculate_total().amount,
            status=order.status.value,
            payment_status=order.payment_status.value,
            notes=order.notes,
            created_at=order.created_at,
            updated_at=order.updated_at,
            shipped_at=order.shipped_at,
            delivered_at=order.delivered_at
        )
        
        # Adresse de livraison
        if order.shipping_address:
            order_model.shipping_address = order.shipping_address.street
            order_model.shipping_city = order.shipping_address.city
            order_model.shipping_postal_code = order.shipping_address.postal_code
            order_model.shipping_country = order.shipping_address.country
        
        # Adresse de facturation
        if order.billing_address:
            order_model.billing_address = order.billing_address.street
            order_model.billing_city = order.billing_address.city
            order_model.billing_postal_code = order.billing_address.postal_code
            order_model.billing_country = order.billing_address.country
        
        # Articles
        for item in order.items:
            item_model = OrderItemModel(
                product_id=item.product_id.value,
                quantity=item.quantity.value,
                unit_price=item.unit_price.amount,
                product_name=item.product_name
            )
            order_model.items.append(item_model)
        
        return order_model
    
    def _update_model_from_order(self, order_model: OrderModel, order: Order):
        """Mettre à jour un OrderModel à partir d'une entité Order"""
        order_model.order_number = order.order_number.value
        order_model.customer_id = order.customer_id.value
        order_model.total_amount = order.calculate_subtotal().amount
        order_model.tax_amount = order.tax_amount.amount
        order_model.shipping_amount = order.shipping_amount.amount
        order_model.discount_amount = order.discount_amount.amount
        order_model.final_amount = order.calculate_total().amount
        order_model.status = order.status.value
        order_model.payment_status = order.payment_status.value
        order_model.notes = order.notes
        order_model.updated_at = order.updated_at
        order_model.shipped_at = order.shipped_at
        order_model.delivered_at = order.delivered_at
        
        # Adresse de livraison
        if order.shipping_address:
            order_model.shipping_address = order.shipping_address.street
            order_model.shipping_city = order.shipping_address.city
            order_model.shipping_postal_code = order.shipping_address.postal_code
            order_model.shipping_country = order.shipping_address.country
        
        # Adresse de facturation
        if order.billing_address:
            order_model.billing_address = order.billing_address.street
            order_model.billing_city = order.billing_address.city
            order_model.billing_postal_code = order.billing_address.postal_code
            order_model.billing_country = order.billing_address.country
        
        # Mettre à jour les articles
        # Supprimer tous les articles existants
        for item in order_model.items:
            self.session.delete(item)
        
        # Ajouter les nouveaux articles
        for item in order.items:
            item_model = OrderItemModel(
                product_id=item.product_id.value,
                quantity=item.quantity.value,
                unit_price=item.unit_price.amount,
                product_name=item.product_name,
                order_id=order_model.id
            )
            order_model.items.append(item_model)
    
    def _model_to_order(self, order_model: OrderModel) -> Order:
        """Convertir un OrderModel en entité Order"""
        shipping_address = None
        if order_model.shipping_address:
            shipping_address = Address(
                street=order_model.shipping_address,
                city=order_model.shipping_city,
                postal_code=order_model.shipping_postal_code,
                country=order_model.shipping_country
            )
        
        # Créer l'adresse de facturation
        billing_address = None
        if order_model.billing_address:
            billing_address = Address(
                street=order_model.billing_address,
                city=order_model.billing_city,
                postal_code=order_model.billing_postal_code,
                country=order_model.billing_country
            )
        
        # Créer les articles
        items = []
        for item_model in order_model.items:
            item = OrderItem(
                product_id=ProductId(item_model.product_id),
                quantity=Quantity(item_model.quantity),
                unit_price=Money(item_model.unit_price),
                product_name=item_model.product_name
            )
            items.append(item)
        
        # Créer la commande
        order = Order(
            id=order_model.id,
            order_number=OrderNumber(order_model.order_number),
            customer_id=CustomerId(order_model.customer_id),
            items=items,
            shipping_address=shipping_address,
            billing_address=billing_address,
            tax_amount=Money(order_model.tax_amount),
            shipping_amount=Money(order_model.shipping_amount),
            discount_amount=Money(order_model.discount_amount),
            status=OrderStatus(order_model.status),
            payment_status=PaymentStatus(order_model.payment_status),
            notes=order_model.notes,
            created_at=order_model.created_at,
            updated_at=order_model.updated_at,
            shipped_at=order_model.shipped_at,
            delivered_at=order_model.delivered_at
        )
        
        return order
