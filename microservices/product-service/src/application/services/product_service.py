from typing import List, Optional
from decimal import Decimal

from ..dto import CreateProductRequest, UpdateProductRequest, ProductResponse, UpdateStockRequest
from ...domain.entities import Product
from ...domain.repositories import IProductRepository, IStoreServiceAdapter
from ...domain.value_objects import ProductName, Category, Money, Stock, StoreReference

class ProductService:
    """Service d'application pour la gestion des produits"""
    
    def __init__(self, product_repository: IProductRepository, store_service: IStoreServiceAdapter):
        self.product_repository = product_repository
        self.store_service = store_service
    
    def get_all_products(self) -> List[ProductResponse]:
        """Récupérer tous les produits"""
        products = self.product_repository.get_all()
        return [self._to_response(product) for product in products]
    
    def get_product_by_id(self, product_id: int) -> Optional[ProductResponse]:
        """Récupérer un produit par son ID"""
        product = self.product_repository.get_by_id(product_id)
        return self._to_response(product) if product else None
    
    def search_products(self, term: str) -> List[ProductResponse]:
        """Rechercher des produits"""
        products = self.product_repository.search(term)
        return [self._to_response(product) for product in products]
    
    def create_product(self, request: CreateProductRequest) -> ProductResponse:
        """Créer un nouveau produit"""
        if not self.store_service.store_exists(request.store_id):
            raise ValueError("Magasin non trouvé")
        
        product = Product(
            id=None,
            name=ProductName(request.name),
            category=Category(request.category),
            price=Money(Decimal(str(request.price)), request.currency),
            stock=Stock(request.stock),
            store_reference=StoreReference(request.store_id)
        )
        
        saved_product = self.product_repository.save(product)
        return self._to_response(saved_product)
    
    def update_product(self, product_id: int, request: UpdateProductRequest) -> Optional[ProductResponse]:
        """Mettre à jour un produit"""
        product = self.product_repository.get_by_id(product_id)
        if not product:
            return None
        
        if request.name is not None:
            product.rename(ProductName(request.name))
        
        if request.category is not None:
            product.change_category(Category(request.category))
        
        if request.price is not None:
            currency = request.currency or product.price.currency
            product.update_price(Money(Decimal(str(request.price)), currency))
        
        if request.stock is not None:
            difference = request.stock - product.stock.quantity
            if difference != 0:
                product.update_stock(difference)
        
        if request.store_id is not None:
            if not self.store_service.store_exists(request.store_id):
                raise ValueError("Magasin non trouvé")
            product.store_reference = StoreReference(request.store_id)
        
        updated_product = self.product_repository.update(product)
        return self._to_response(updated_product)
    
    def delete_product(self, product_id: int) -> bool:
        """Supprimer un produit"""
        return self.product_repository.delete(product_id)
    
    def update_stock(self, product_id: int, request: UpdateStockRequest) -> Optional[ProductResponse]:
        """Mettre à jour le stock d'un produit"""
        product = self.product_repository.get_by_id(product_id)
        if not product:
            return None
        
        if request.quantity >= 0:
            product.update_stock(request.quantity)
        else:
            product.reduce_stock(abs(request.quantity))
        
        updated_product = self.product_repository.update(product)
        return self._to_response(updated_product)
    
    def _to_response(self, product: Product) -> ProductResponse:
        """Convertir une entité en DTO de réponse"""
        return ProductResponse(
            id=product.id,
            name=product.name.value,
            description=product.description,
            category=product.category.name,
            price=float(product.price.amount),
            currency=product.price.currency,
            stock=product.stock.quantity,
            store_id=product.store_reference.store_id
        )
