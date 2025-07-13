from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime
import requests

from ..database import SaleModel, SaleItemModel
from ...domain.entities import Sale, SaleItem
from ...domain.repositories import ISaleRepository, IProductServiceAdapter
from ...domain.value_objects import Money, Quantity, ProductReference, StoreReference, SaleTimestamp

class SaleRepository(ISaleRepository):
    """Implémentation du repository des ventes"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, sale_id: int) -> Optional[Sale]:
        """Récupérer une vente par son ID"""
        model = self.session.query(SaleModel).filter(SaleModel.id == sale_id).first()
        return self._to_entity(model) if model else None
    
    def get_all(self) -> List[Sale]:
        """Récupérer toutes les ventes"""
        models = self.session.query(SaleModel).all()
        return [self._to_entity(model) for model in models]
    
    def get_by_store(self, store_id: int) -> List[Sale]:
        """Récupérer les ventes d'un magasin"""
        models = self.session.query(SaleModel).filter(SaleModel.store_id == store_id).all()
        return [self._to_entity(model) for model in models]
    
    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Sale]:
        """Récupérer les ventes dans une plage de dates"""
        models = self.session.query(SaleModel).filter(
            SaleModel.timestamp >= start_date,
            SaleModel.timestamp <= end_date
        ).all()
        return [self._to_entity(model) for model in models]
    
    def save(self, sale: Sale) -> Sale:
        """Sauvegarder une vente"""
        model = SaleModel(
            timestamp=sale.timestamp.value,
            total_amount=sale.total_amount.amount,
            store_id=sale.store_reference.store_id
        )
        self.session.add(model)
        self.session.flush()  # Pour obtenir l'ID
        
        for item in sale.items:
            item_model = SaleItemModel(
                sale_id=model.id,
                product_id=item.product_reference.product_id,
                quantity=item.quantity.value,
                unit_price=item.unit_price.amount,
                total_price=item.total_price.amount
            )
            self.session.add(item_model)
        
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)
    
    def update(self, sale: Sale) -> Sale:
        """Mettre à jour une vente"""
        model = self.session.query(SaleModel).filter(SaleModel.id == sale.id).first()
        if not model:
            raise ValueError("Vente non trouvée")
        
        self.session.query(SaleItemModel).filter(SaleItemModel.sale_id == sale.id).delete()
        
        model.total_amount = sale.total_amount.amount
        model.store_id = sale.store_reference.store_id
        
        for item in sale.items:
            item_model = SaleItemModel(
                sale_id=model.id,
                product_id=item.product_reference.product_id,
                quantity=item.quantity.value,
                unit_price=item.unit_price.amount,
                total_price=item.total_price.amount
            )
            self.session.add(item_model)
        
        self.session.commit()
        return self._to_entity(model)
    
    def delete(self, sale_id: int) -> bool:
        """Supprimer une vente"""
        model = self.session.query(SaleModel).filter(SaleModel.id == sale_id).first()
        if not model:
            return False
        
        self.session.delete(model)
        self.session.commit()
        return True
    
    def _to_entity(self, model: SaleModel) -> Sale:
        """Convertir un modèle en entité"""
        items = []
        for item_model in model.items:
            item = SaleItem(
                id=item_model.id,
                product_reference=ProductReference(item_model.product_id),
                quantity=Quantity(item_model.quantity),
                unit_price=Money(Decimal(str(item_model.unit_price)))
            )
            items.append(item)
        
        return Sale(
            id=model.id,
            timestamp=SaleTimestamp(model.timestamp),
            store_reference=StoreReference(model.store_id),
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
    
    def update_product_stock(self, product_id: int, quantity_change: int) -> bool:
        """Mettre à jour le stock d'un produit"""
        try:
            headers = {'Authorization': f'Bearer {self.api_token}'}
            data = {'quantity': quantity_change}
            response = requests.put(
                f'{self.product_service_url}/products/{product_id}/stock',
                headers=headers,
                json=data,
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def check_product_availability(self, product_id: int, required_quantity: int) -> bool:
        """Vérifier la disponibilité d'un produit"""
        product_info = self.get_product_info(product_id)
        if not product_info:
            return False
        
        return product_info.get('stock', 0) >= required_quantity
