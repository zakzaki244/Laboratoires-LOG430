from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class UserRole(enum.Enum):
    """Enumération des rôles utilisateurs"""
    ADMIN = "admin"
    GESTIONNAIRE = "gestionnaire"
    RESPONSABLE_PRODUIT = "responsable_produit"
    RESPONSABLE_LOGISTIQUE = "responsable_logistique"
    EMPLOYE_MAGASIN = "employe_magasin"
    CLIENT = "client"


class CustomerModel(Base):
    """Modèle SQLAlchemy pour les clients"""
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default='client')  # Utilisera l'enum côté application
    store_id = Column(Integer, nullable=True)  # ID du magasin pour les employés
    address = Column(JSON, nullable=False)  # {street, city, postal_code, country}
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Customer(id={self.id}, email='{self.email}', name='{self.first_name} {self.last_name}', role='{self.role}')>"
