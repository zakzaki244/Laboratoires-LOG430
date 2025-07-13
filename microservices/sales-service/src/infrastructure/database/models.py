from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from typing import Dict, Any
import datetime

Base = declarative_base()

class SaleModel(Base):
    """Modèle SQLAlchemy pour les ventes"""
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    total_amount = Column(DECIMAL(10, 2), nullable=False, default=0.0)
    store_id = Column(Integer, nullable=False)
    
    items = relationship("SaleItemModel", back_populates="sale", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'total_amount': float(self.total_amount),
            'store_id': self.store_id,
            'items': [item.to_dict() for item in self.items]
        }

class SaleItemModel(Base):
    """Modèle SQLAlchemy pour les articles de vente"""
    __tablename__ = "sale_items"
    
    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    
    sale = relationship("SaleModel", back_populates="items")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'total_price': float(self.total_price)
        }
