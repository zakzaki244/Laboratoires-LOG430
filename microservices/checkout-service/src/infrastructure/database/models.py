from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()


class OrderModel(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    order_number = Column(String, unique=True, nullable=False, index=True)
    customer_id = Column(Integer, nullable=False)
    total_amount = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    shipping_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    final_amount = Column(Float, nullable=False)
    
    # Adresse de livraison
    shipping_address = Column(Text)
    shipping_city = Column(String)
    shipping_postal_code = Column(String)
    shipping_country = Column(String)
    
    # Adresse de facturation
    billing_address = Column(Text)
    billing_city = Column(String)
    billing_postal_code = Column(String)
    billing_country = Column(String)
    
    # Statuts
    status = Column(String, default="pending")
    payment_status = Column(String, default="pending")
    
    # Dates
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    shipped_at = Column(DateTime)
    delivered_at = Column(DateTime)
    
    # Notes
    notes = Column(Text)
    
    items = relationship("OrderItemModel", back_populates="order", cascade="all, delete-orphan")


class OrderItemModel(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    product_name = Column(String, nullable=False)
    
    order = relationship("OrderModel", back_populates="items")


def create_database_engine(database_url: str):
    """Créer le moteur de base de données"""
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    return engine


def create_session_factory(engine):
    """Créer une factory de sessions"""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
