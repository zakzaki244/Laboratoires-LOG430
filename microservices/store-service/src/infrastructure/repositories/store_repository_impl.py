from typing import List, Optional
from sqlalchemy.orm import Session

from ..database import StoreModel
from ...domain.entities import Store
from ...domain.repositories import IStoreRepository
from ...domain.value_objects import StoreName, Address, Phone

class StoreRepository(IStoreRepository):
    """Implémentation du repository des magasins"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, store_id: int) -> Optional[Store]:
        """Récupérer un magasin par son ID"""
        model = self.session.query(StoreModel).filter(StoreModel.id == store_id).first()
        return self._to_entity(model) if model else None
    
    def get_all(self) -> List[Store]:
        """Récupérer tous les magasins"""
        models = self.session.query(StoreModel).all()
        return [self._to_entity(model) for model in models]
    
    def get_by_name(self, name: str) -> Optional[Store]:
        """Récupérer un magasin par son nom"""
        model = self.session.query(StoreModel).filter(StoreModel.name == name).first()
        return self._to_entity(model) if model else None
    
    def save(self, store: Store) -> Store:
        """Sauvegarder un magasin"""
        model = StoreModel(
            name=store.name.value,
            address=store.address.full_address() if store.address else None,
            phone=store.phone.formatted() if store.phone else None
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)
    
    def update(self, store: Store) -> Store:
        """Mettre à jour un magasin"""
        model = self.session.query(StoreModel).filter(StoreModel.id == store.id).first()
        if not model:
            raise ValueError("Magasin non trouvé")
        
        model.name = store.name.value
        model.address = store.address.full_address() if store.address else None
        model.phone = store.phone.formatted() if store.phone else None
        
        self.session.commit()
        return self._to_entity(model)
    
    def delete(self, store_id: int) -> bool:
        """Supprimer un magasin"""
        model = self.session.query(StoreModel).filter(StoreModel.id == store_id).first()
        if not model:
            return False
        
        self.session.delete(model)
        self.session.commit()
        return True
    
    def name_exists(self, name: str, exclude_id: Optional[int] = None) -> bool:
        """Vérifier si un nom de magasin existe déjà"""
        query = self.session.query(StoreModel).filter(StoreModel.name == name)
        if exclude_id:
            query = query.filter(StoreModel.id != exclude_id)
        return query.first() is not None
    
    def _to_entity(self, model: StoreModel) -> Store:
        """Convertir un modèle en entité"""
        address = None
        if model.address:
            address_parts = model.address.split(', ')
            if len(address_parts) >= 3:
                street = address_parts[0]
                city = address_parts[1]
                province_postal = address_parts[2].split(' ')
                if len(province_postal) >= 2:
                    province = province_postal[0]
                    postal_code = ' '.join(province_postal[1:3])
                    country = address_parts[3] if len(address_parts) > 3 else "Canada"
                    try:
                        address = Address(street, city, postal_code, province, country)
                    except ValueError:
                        pass
        
        phone = None
        if model.phone:
            try:
                phone = Phone(model.phone)
            except ValueError:
                pass
        
        return Store(
            id=model.id,
            name=StoreName(model.name),
            address=address,
            phone=phone
        )
