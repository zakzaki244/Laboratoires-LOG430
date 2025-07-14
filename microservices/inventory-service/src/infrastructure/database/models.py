from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class InventoryItemModel(Base):
    """Modèle pour les éléments d'inventaire"""
    __tablename__ = "inventory_items"
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, nullable=False)
    store_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    min_threshold = Column(Integer, nullable=False, default=10)
    max_threshold = Column(Integer, nullable=False, default=100)
    last_updated = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class StockMovementModel(Base):
    """Modèle pour les mouvements de stock"""
    __tablename__ = "stock_movements"
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, nullable=False)
    store_id = Column(Integer, nullable=False)
    movement_type = Column(String, nullable=False)  # 'IN', 'OUT', 'TRANSFER'
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float)
    reference = Column(String)  # Référence de commande, vente, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(String)


class ReapproRequestModel(Base):
    """Modèle pour les demandes de réapprovisionnement"""
    __tablename__ = "reappro_requests"
    
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(String, default="en attente")
    requested_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    notes = Column(String)


def create_database_engine(database_url: str):
    """Créer le moteur de base de données"""
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    return engine


def create_session_factory(engine):
    """Créer une factory de sessions"""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
