from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class ReapproRequestModel(Base):
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
