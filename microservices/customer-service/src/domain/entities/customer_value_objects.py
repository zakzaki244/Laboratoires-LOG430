from dataclasses import dataclass
from typing import Dict, Any
import re
import hashlib


@dataclass
class Email:
    """Value object pour l'email"""
    value: str
    
    def __post_init__(self):
        if not self.is_valid():
            raise ValueError(f"Email invalide: {self.value}")
    
    def is_valid(self) -> bool:
        """Valide le format de l'email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, self.value) is not None
    
    def __str__(self) -> str:
        return self.value


@dataclass
class Phone:
    """Value object pour le téléphone"""
    value: str
    
    def __post_init__(self):
        if not self.is_valid():
            raise ValueError(f"Numéro de téléphone invalide: {self.value}")
    
    def is_valid(self) -> bool:
        """Valide le format du téléphone"""
        # Permet différents formats de téléphone
        pattern = r'^\+?[\d\s\-\(\)]{8,20}$'
        return re.match(pattern, self.value) is not None
    
    def __str__(self) -> str:
        return self.value


@dataclass
class Address:
    """Value object pour l'adresse"""
    street: str
    city: str
    postal_code: str
    country: str
    
    def __post_init__(self):
        if not all([self.street, self.city, self.postal_code, self.country]):
            raise ValueError("Tous les champs de l'adresse sont requis")
    
    def to_dict(self) -> Dict[str, str]:
        """Convertit l'adresse en dictionnaire"""
        return {
            'street': self.street,
            'city': self.city,
            'postal_code': self.postal_code,
            'country': self.country
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'Address':
        """Crée une adresse à partir d'un dictionnaire"""
        return cls(
            street=data['street'],
            city=data['city'],
            postal_code=data['postal_code'],
            country=data['country']
        )
    
    def __str__(self) -> str:
        return f"{self.street}, {self.city}, {self.postal_code}, {self.country}"


@dataclass
class Password:
    """Value object pour le mot de passe"""
    value: str
    
    def __post_init__(self):
        if not self.is_valid():
            raise ValueError("Le mot de passe ne respecte pas les critères de sécurité")
    
    def is_valid(self) -> bool:
        """Valide la force du mot de passe"""
        # Au moins 8 caractères avec au moins une lettre et un chiffre
        if len(self.value) < 8:
            return False
        
        has_letter = re.search(r'[a-zA-Z]', self.value)
        has_digit = re.search(r'\d', self.value)
        
        return has_letter is not None and has_digit is not None
    
    def hash(self) -> str:
        """Hache le mot de passe"""
        return hashlib.sha256(self.value.encode()).hexdigest()
    
    def __str__(self) -> str:
        return "*" * len(self.value)  # Masque le mot de passe lors de l'affichage
