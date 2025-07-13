from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from .customer_value_objects import Email, Phone, Address, Password


@dataclass
class Customer:
    """Entité Customer du domaine"""
    id: Optional[str]
    email: Email
    first_name: str
    last_name: str
    phone: Phone
    address: Address
    password: Password
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def get_full_name(self) -> str:
        """Retourner le nom complet du client"""
        return f"{self.first_name} {self.last_name}"
    
    def update_contact_info(self, phone: Phone, address: Address) -> None:
        """Mettre à jour les informations de contact"""
        self.phone = phone
        self.address = address
        self.updated_at = datetime.utcnow()
    
    def change_password(self, new_password: Password) -> None:
        """Changer le mot de passe"""
        self.password = new_password
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Désactiver le compte client"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """Activer le compte client"""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def validate_for_registration(self) -> None:
        """Valider les données pour l'inscription"""
        if not self.first_name or len(self.first_name.strip()) < 2:
            raise ValueError("Le prénom doit contenir au moins 2 caractères")
        
        if not self.last_name or len(self.last_name.strip()) < 2:
            raise ValueError("Le nom doit contenir au moins 2 caractères")
    
    def to_dict(self) -> dict:
        """Convertir en dictionnaire pour la serialization"""
        return {
            'id': self.id,
            'email': self.email.value,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone.value,
            'address': self.address.to_dict(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def create_new_customer(
        cls,
        email: str,
        first_name: str,
        last_name: str,
        phone: str,
        address_data: dict,
        plain_password: str
    ) -> 'Customer':
        """Factory method pour créer un nouveau client"""
        customer = cls(
            id=None,
            email=Email(email),
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            phone=Phone(phone),
            address=Address.from_dict(address_data),
            password=Password.create_from_plain(plain_password)
        )
        
        customer.validate_for_registration()
        return customer
