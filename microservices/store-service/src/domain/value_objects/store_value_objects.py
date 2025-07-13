from dataclasses import dataclass
import re
from typing import Optional

@dataclass(frozen=True)
class StoreName:
    """Value object pour le nom du magasin"""
    value: str
    
    def __post_init__(self):
        if not self.value or len(self.value.strip()) < 2:
            raise ValueError("Le nom du magasin doit contenir au moins 2 caractères")
        if len(self.value) > 100:
            raise ValueError("Le nom du magasin ne peut pas dépasser 100 caractères")

@dataclass(frozen=True)
class Address:
    """Value object pour l'adresse"""
    street: str
    city: str
    postal_code: str
    province: str = "QC"
    country: str = "Canada"
    
    def __post_init__(self):
        if not self.street or len(self.street.strip()) < 5:
            raise ValueError("L'adresse doit contenir au moins 5 caractères")
        if not self.city or len(self.city.strip()) < 2:
            raise ValueError("La ville doit contenir au moins 2 caractères")
        if not self.postal_code or not re.match(r'^[A-Za-z]\d[A-Za-z] \d[A-Za-z]\d$', self.postal_code):
            raise ValueError("Code postal invalide (format: A1A 1A1)")
    
    def full_address(self) -> str:
        """Retourner l'adresse complète"""
        return f"{self.street}, {self.city}, {self.province} {self.postal_code}, {self.country}"

@dataclass(frozen=True)
class Phone:
    """Value object pour le numéro de téléphone"""
    number: str
    
    def __post_init__(self):
        clean_number = re.sub(r'[^\d]', '', self.number)
        if len(clean_number) != 10:
            raise ValueError("Le numéro de téléphone doit contenir 10 chiffres")
        if not clean_number.startswith(('438', '514', '450', '819', '418')):
            raise ValueError("Code régional du Québec requis")
    
    def formatted(self) -> str:
        """Retourner le numéro formaté"""
        clean = re.sub(r'[^\d]', '', self.number)
        return f"({clean[:3]}) {clean[3:6]}-{clean[6:]}"
