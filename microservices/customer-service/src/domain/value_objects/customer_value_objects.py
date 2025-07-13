from dataclasses import dataclass
from typing import Optional
import re


@dataclass(frozen=True)
class Email:
    """Value Object pour l'email"""
    value: str
    
    def __post_init__(self):
        if not self._is_valid_email(self.value):
            raise ValueError(f"Email invalide: {self.value}")
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None


@dataclass(frozen=True)
class Phone:
    """Value Object pour le téléphone"""
    value: str
    
    def __post_init__(self):
        if not self._is_valid_phone(self.value):
            raise ValueError(f"Téléphone invalide: {self.value}")
    
    @staticmethod
    def _is_valid_phone(phone: str) -> bool:
        pattern = r'^\+?[1-9]\d{1,14}$'
        return re.match(pattern, phone.replace(' ', '').replace('-', '')) is not None


@dataclass(frozen=True)
class Address:
    """Value Object pour l'adresse"""
    street: str
    city: str
    postal_code: str
    country: str
    
    def __post_init__(self):
        if not self.street or not self.city or not self.postal_code or not self.country:
            raise ValueError("Tous les champs de l'adresse sont requis")
    
    def to_dict(self) -> dict:
        return {
            'street': self.street,
            'city': self.city,
            'postal_code': self.postal_code,
            'country': self.country
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Address':
        return cls(
            street=data['street'],
            city=data['city'],
            postal_code=data['postal_code'],
            country=data['country']
        )


@dataclass(frozen=True)
class Password:
    """Value Object pour le mot de passe"""
    hashed_value: str
    
    def __post_init__(self):
        if not self.hashed_value:
            raise ValueError("Le mot de passe haché ne peut pas être vide")
    
    @classmethod
    def create_from_plain(cls, plain_password: str) -> 'Password':
        """Créer un mot de passe à partir d'un texte en clair"""
        if len(plain_password) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
        
        # Ici vous pourriez utiliser bcrypt ou argon2
        import hashlib
        hashed = hashlib.sha256(plain_password.encode()).hexdigest()
        return cls(hashed_value=hashed)
    
    def verify(self, plain_password: str) -> bool:
        """Vérifier si le mot de passe en clair correspond"""
        import hashlib
        hashed = hashlib.sha256(plain_password.encode()).hexdigest()
        return hashed == self.hashed_value
