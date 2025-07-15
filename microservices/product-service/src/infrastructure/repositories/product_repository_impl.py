from typing import List, Optional
from sqlalchemy.orm import Session
from typing import Callable
from decimal import Decimal
import requests

from ..database import ProductModel
from ...domain.entities import Product
from ...domain.repositories import IProductRepository, IStoreServiceAdapter
from ...domain.value_objects import ProductName, Category, Money, Stock, StoreReference

class ProductRepository(IProductRepository):
    """Implémentation du repository des produits"""
    
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory
    
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Récupérer un produit par son ID"""
        session = self.session_factory()
        try:
            model = session.query(ProductModel).filter(ProductModel.id == product_id).first()
            return self._to_entity(model) if model else None
        finally:
            session.close()
    
    def get_all(self) -> List[Product]:
        """Récupérer tous les produits"""
        session = self.session_factory()
        try:
            models = session.query(ProductModel).all()
            return [self._to_entity(model) for model in models]
        finally:
            session.close()
    
    def search(self, term: str) -> List[Product]:
        """Rechercher des produits par nom ou catégorie"""
        session = self.session_factory()
        try:
            models = session.query(ProductModel).filter(
                ProductModel.name.ilike(f'%{term}%') |
                ProductModel.category.ilike(f'%{term}%')
            ).all()
            return [self._to_entity(model) for model in models]
        finally:
            session.close()
    
    def get_by_store(self, store_id: int) -> List[Product]:
        """Récupérer les produits d'un magasin"""
        session = self.session_factory()
        try:
            models = session.query(ProductModel).filter(ProductModel.store_id == store_id).all()
            return [self._to_entity(model) for model in models]
        finally:
            session.close()
    
    def save(self, product: Product) -> Product:
        """Sauvegarder un produit"""
        session = self.session_factory()
        model = ProductModel(
            name=product.name.value,
            category=product.category.name,
            price=product.price.amount,
            currency=product.price.currency,
            stock=product.stock.quantity,
            store_id=product.store_reference.store_id
        )
        session.add(model)
        session.commit()
        session.refresh(model)
        product_entity = self._to_entity(model)
        session.close()
        return product_entity
    
    def update(self, product: Product) -> Product:
        """Mettre à jour un produit"""
        session = self.session_factory()
        model = session.query(ProductModel).filter(ProductModel.id == product.id).first()
        if not model:
            raise ValueError("Produit non trouvé")
        
        model.name = product.name.value
        model.category = product.category.name
        model.price = product.price.amount
        model.currency = product.price.currency
        model.stock = product.stock.quantity
        model.store_id = product.store_reference.store_id
        
        session.commit()
        updated = self._to_entity(model)
        session.close()
        return updated
    
    def delete(self, product_id: int) -> bool:
        """Supprimer un produit"""
        session = self.session_factory()
        model = session.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not model:
            session.close()
            return False

        session.delete(model)
        session.commit()
        session.close()
        return True
    
    def _to_entity(self, model: ProductModel) -> Product:
        """Convertir un modèle en entité"""
        return Product(
            id=model.id,
            name=ProductName(model.name),
            category=Category(model.category),
            price=Money(Decimal(str(model.price)), model.currency),
            stock=Stock(model.stock),
            store_reference=StoreReference(model.store_id)
        )

class StoreServiceAdapter(IStoreServiceAdapter):
    """Adaptateur pour le service des magasins"""
    
    def __init__(self, store_service_url: str, api_token: str):
        self.store_service_url = store_service_url
        self.api_token = api_token
    
    def store_exists(self, store_id: int) -> bool:
        """Vérifier si un magasin existe"""
        try:
            headers = {'Authorization': f'Bearer {self.api_token}'}
            response = requests.get(
                f'{self.store_service_url}/stores/{store_id}',
                headers=headers,
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False
