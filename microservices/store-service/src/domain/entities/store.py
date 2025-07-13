from dataclasses import dataclass
from typing import Optional, Dict, Any

from ..value_objects import StoreName, Address, Phone

@dataclass
class Store:
    """Entité magasin représentant un magasin dans le domaine"""
    id: Optional[int]
    name: StoreName
    address: Optional[Address]
    phone: Optional[Phone]
    
    def update_name(self, new_name: StoreName) -> None:
        """Mettre à jour le nom du magasin"""
        self.name = new_name
    
    def update_address(self, new_address: Address) -> None:
        """Mettre à jour l'adresse du magasin"""
        self.address = new_address
    
    def update_phone(self, new_phone: Phone) -> None:
        """Mettre à jour le téléphone du magasin"""
        self.phone = new_phone
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire pour la sérialisation"""
        result = {
            'id': self.id,
            'name': self.name.value,
        }
        
        if self.address:
            result['address'] = self.address.full_address()
        else:
            result['address'] = None
            
        if self.phone:
            result['phone'] = self.phone.formatted()
        else:
            result['phone'] = None
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Store':
        """Créer un magasin à partir d'un dictionnaire"""
        address = None
        if data.get('address'):
            address_parts = data['address'].split(', ')
            if len(address_parts) >= 3:
                street = address_parts[0]
                city = address_parts[1]
                province_postal = address_parts[2].split(' ')
                if len(province_postal) >= 2:
                    province = province_postal[0]
                    postal_code = ' '.join(province_postal[1:3])
                    country = address_parts[3] if len(address_parts) > 3 else "Canada"
                    address = Address(street, city, postal_code, province, country)
        
        phone = None
        if data.get('phone'):
            phone = Phone(data['phone'])
        
        return cls(
            id=data.get('id'),
            name=StoreName(data['name']),
            address=address,
            phone=phone
        )
