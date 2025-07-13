from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import CustomerModel, Base

def create_database_engine(database_url: str):
    """Crée le moteur de base de données SQLAlchemy"""
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)
    return engine

def create_session_factory(engine):
    """Crée une factory de sessions SQLAlchemy"""
    return sessionmaker(bind=engine)

__all__ = ['CustomerModel', 'Base', 'create_database_engine', 'create_session_factory']
