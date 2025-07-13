# Modèles SQLAlchemy pour Cart Service
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, DECIMAL, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from typing import Dict, Any
import datetime

Base = declarative_base()

class CartModel(Base):
    """Modèle SQLAlchemy pour les paniers"""
    __tablename__ = "carts"
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relation avec les articles
    items = relationship("CartItemModel", back_populates="cart", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire"""
        total_amount = sum(float(item.total_price) for item in self.items)
        total_items = sum(item.quantity for item in self.items)
        
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active,
            'total_amount': total_amount,
            'total_items': total_items,
            'items': [item.to_dict() for item in self.items]
        }

class CartItemModel(Base):
    """Modèle SQLAlchemy pour les articles du panier"""
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, nullable=False)
    product_name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    
    # Relation avec le panier
    cart = relationship("CartModel", back_populates="items")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'total_price': float(self.total_price)
        }
