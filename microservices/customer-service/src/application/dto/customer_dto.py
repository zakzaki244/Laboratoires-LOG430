from dataclasses import dataclass
from typing import Optional


@dataclass
class CustomerRegistrationDTO:
    """DTO pour l'inscription d'un client"""
    email: str
    first_name: str
    last_name: str
    phone: str
    password: str
    address: dict  # {street, city, postal_code, country}


@dataclass
class CustomerLoginDTO:
    """DTO pour la connexion d'un client"""
    email: str
    password: str


@dataclass
class CustomerUpdateDTO:
    """DTO pour la mise à jour d'un client"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[dict] = None


@dataclass
class PasswordChangeDTO:
    """DTO pour le changement de mot de passe"""
    current_password: str
    new_password: str


@dataclass
class CustomerResponseDTO:
    """DTO de réponse pour un client"""
    id: str
    email: str
    first_name: str
    last_name: str
    full_name: str
    phone: str
    address: dict
    is_active: bool
    created_at: str
    updated_at: str
    
    @classmethod
    def from_entity(cls, customer):
        """Créer un DTO à partir d'une entité Customer"""
        return cls(
            id=customer.id,
            email=customer.email.value,
            first_name=customer.first_name,
            last_name=customer.last_name,
            full_name=customer.get_full_name(),
            phone=customer.phone.value,
            address=customer.address.to_dict(),
            is_active=customer.is_active,
            created_at=customer.created_at.isoformat() if customer.created_at else None,
            updated_at=customer.updated_at.isoformat() if customer.updated_at else None
        )
