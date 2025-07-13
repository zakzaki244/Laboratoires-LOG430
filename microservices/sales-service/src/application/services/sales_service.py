from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

from ..dto import (
    CreateSaleRequest, UpdateSaleRequest, SaleResponse, SaleItemResponse,
    SalesSummaryRequest, SalesSummaryResponse
)
from ...domain.entities import Sale, SaleItem
from ...domain.repositories import ISaleRepository, IProductServiceAdapter
from ...domain.value_objects import Money, Quantity, ProductReference, StoreReference, SaleTimestamp

class SalesService:
    """Service d'application pour la gestion des ventes"""
    
    def __init__(self, sale_repository: ISaleRepository, product_service: IProductServiceAdapter):
        self.sale_repository = sale_repository
        self.product_service = product_service
    
    def get_all_sales(self) -> List[SaleResponse]:
        """Récupérer toutes les ventes"""
        sales = self.sale_repository.get_all()
        return [self._to_response(sale) for sale in sales]
    
    def get_sale_by_id(self, sale_id: int) -> Optional[SaleResponse]:
        """Récupérer une vente par son ID"""
        sale = self.sale_repository.get_by_id(sale_id)
        return self._to_response(sale) if sale else None
    
    def get_sales_by_store(self, store_id: int) -> List[SaleResponse]:
        """Récupérer les ventes d'un magasin"""
        sales = self.sale_repository.get_by_store(store_id)
        return [self._to_response(sale) for sale in sales]
    
    def create_sale(self, request: CreateSaleRequest) -> SaleResponse:
        """Créer une nouvelle vente"""
        for item_request in request.items:
            if not self.product_service.check_product_availability(
                item_request.product_id, item_request.quantity
            ):
                raise ValueError(f"Produit {item_request.product_id} non disponible en quantité suffisante")
        
        sale_items = []
        for item_request in request.items:
            product_info = self.product_service.get_product_info(item_request.product_id)
            if not product_info:
                raise ValueError(f"Produit {item_request.product_id} non trouvé")
            
            unit_price = item_request.unit_price if item_request.unit_price > 0 else product_info['price']
            
            sale_item = SaleItem(
                id=None,
                product_reference=ProductReference(item_request.product_id),
                quantity=Quantity(item_request.quantity),
                unit_price=Money(Decimal(str(unit_price)))
            )
            sale_items.append(sale_item)
        
        sale = Sale(
            id=None,
            timestamp=SaleTimestamp(datetime.utcnow()),
            store_reference=StoreReference(request.store_id),
            items=sale_items
        )
        
        sale.validate()
        
        for item in sale.items:
            if not self.product_service.update_product_stock(
                item.product_reference.product_id, -item.quantity.value
            ):
                raise ValueError(f"Impossible de mettre à jour le stock du produit {item.product_reference.product_id}")
        
        saved_sale = self.sale_repository.save(sale)
        return self._to_response(saved_sale)
    
    def update_sale(self, sale_id: int, request: UpdateSaleRequest) -> Optional[SaleResponse]:
        """Mettre à jour une vente"""
        sale = self.sale_repository.get_by_id(sale_id)
        if not sale:
            return None
        
        if request.items is not None:
            for item in sale.items:
                self.product_service.update_product_stock(
                    item.product_reference.product_id, item.quantity.value
                )
            
            new_items = []
            for item_request in request.items:
                if not self.product_service.check_product_availability(
                    item_request.product_id, item_request.quantity
                ):
                    raise ValueError(f"Produit {item_request.product_id} non disponible en quantité suffisante")
                
                product_info = self.product_service.get_product_info(item_request.product_id)
                if not product_info:
                    raise ValueError(f"Produit {item_request.product_id} non trouvé")
                
                unit_price = item_request.unit_price if item_request.unit_price > 0 else product_info['price']
                
                sale_item = SaleItem(
                    id=None,
                    product_reference=ProductReference(item_request.product_id),
                    quantity=Quantity(item_request.quantity),
                    unit_price=Money(Decimal(str(unit_price)))
                )
                new_items.append(sale_item)
            
            sale.items = new_items
            
            sale.validate()
            for item in sale.items:
                if not self.product_service.update_product_stock(
                    item.product_reference.product_id, -item.quantity.value
                ):
                    raise ValueError(f"Impossible de mettre à jour le stock du produit {item.product_reference.product_id}")
        
        updated_sale = self.sale_repository.update(sale)
        return self._to_response(updated_sale)
    
    def delete_sale(self, sale_id: int) -> bool:
        """Supprimer une vente"""
        sale = self.sale_repository.get_by_id(sale_id)
        if not sale:
            return False
        
        for item in sale.items:
            self.product_service.update_product_stock(
                item.product_reference.product_id, item.quantity.value
            )
        
        return self.sale_repository.delete(sale_id)
    
    def get_sales_summary(self, request: SalesSummaryRequest) -> SalesSummaryResponse:
        """Obtenir un résumé des ventes"""
        if request.start_date and request.end_date:
            sales = self.sale_repository.get_by_date_range(request.start_date, request.end_date)
        elif request.store_id:
            sales = self.sale_repository.get_by_store(request.store_id)
        else:
            sales = self.sale_repository.get_all()
        
        # Calculer les statistiques
        total_sales = len(sales)
        total_amount = sum(float(sale.total_amount.amount) for sale in sales)
        average_sale_amount = total_amount / total_sales if total_sales > 0 else 0
        
        # Calculer les produits les plus vendus
        product_sales = {}
        for sale in sales:
            for item in sale.items:
                product_id = item.product_reference.product_id
                if product_id not in product_sales:
                    product_sales[product_id] = 0
                product_sales[product_id] += item.quantity.value
        
        best_selling_products = [
            {"product_id": product_id, "quantity_sold": quantity}
            for product_id, quantity in sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        return SalesSummaryResponse(
            total_sales=total_sales,
            total_amount=total_amount,
            average_sale_amount=average_sale_amount,
            best_selling_products=best_selling_products
        )
    
    def _to_response(self, sale: Sale) -> SaleResponse:
        """Convertir une entité en DTO de réponse"""
        item_responses = [
            SaleItemResponse(
                id=item.id,
                product_id=item.product_reference.product_id,
                quantity=item.quantity.value,
                unit_price=float(item.unit_price.amount),
                total_price=float(item.total_price.amount)
            )
            for item in sale.items
        ]
        
        return SaleResponse(
            id=sale.id,
            timestamp=sale.timestamp.to_iso_string(),
            total_amount=float(sale.total_amount.amount),
            store_id=sale.store_reference.store_id,
            items=item_responses
        )
