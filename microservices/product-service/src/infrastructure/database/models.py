from sqlalchemy import Column, Integer, String, Float, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from typing import Dict, Any

Base = declarative_base()

class ProductModel(Base):
    """Modèle SQLAlchemy pour les produits"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(String(500), nullable=True)
    category = Column(String(100), nullable=False, index=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="CAD")
    stock = Column(Integer, nullable=False, default=0)
    store_id = Column(Integer, nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'price': float(self.price),
            'currency': self.currency,
            'stock': self.stock,
            'store_id': self.store_id
        }
