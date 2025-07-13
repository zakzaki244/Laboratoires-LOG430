from dataclasses import dataclass
from typing import Optional

@dataclass
class CreateStoreRequest:
    """DTO pour créer un magasin"""
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None

@dataclass
class UpdateStoreRequest:
    """DTO pour mettre à jour un magasin"""
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None

@dataclass
class StoreResponse:
    """DTO pour la réponse magasin"""
    id: int
    name: str
    address: Optional[str]
    phone: Optional[str]
