from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from typing import Dict, Any

Base = declarative_base()

class StoreModel(Base):
    """Modèle SQLAlchemy pour les magasins"""
    __tablename__ = "stores"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone
        }
