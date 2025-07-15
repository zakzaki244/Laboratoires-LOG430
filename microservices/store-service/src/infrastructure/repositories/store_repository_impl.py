from typing import List, Optional
from sqlalchemy.orm import Session
from typing import Callable

from ..database import StoreModel
from ...domain.entities import Store
from ...domain.repositories import IStoreRepository
from ...domain.value_objects import StoreName, Address, Phone

class StoreRepository(IStoreRepository):
    """Implémentation du repository des magasins"""
    
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory
    
    def get_by_id(self, store_id: int) -> Optional[Store]:
        """Récupérer un magasin par son ID"""
        session = self.session_factory()
        try:
            model = session.query(StoreModel).filter(StoreModel.id == store_id).first()
            return self._to_entity(model) if model else None
        finally:
            session.close()
    
    def get_all(self) -> List[Store]:
        """Récupérer tous les magasins"""
        session = self.session_factory()
        try:
            models = session.query(StoreModel).all()
            return [self._to_entity(model) for model in models]
        finally:
            session.close()
    
    def get_by_name(self, name: str) -> Optional[Store]:
        """Récupérer un magasin par son nom"""
        session = self.session_factory()
        try:
            model = session.query(StoreModel).filter(StoreModel.name == name).first()
            return self._to_entity(model) if model else None
        finally:
            session.close()
    
    def save(self, store: Store) -> Store:
        """Sauvegarder un magasin"""
        session = self.session_factory()
        model = StoreModel(
            name=store.name.value,
            address=store.address.full_address() if store.address else None,
            phone=store.phone.formatted() if store.phone else None
        )
        session.add(model)
        session.commit()
        session.refresh(model)
        store_entity = self._to_entity(model)
        session.close()
        return store_entity
    
    def update(self, store: Store) -> Store:
        """Mettre à jour un magasin"""
        session = self.session_factory()
        model = session.query(StoreModel).filter(StoreModel.id == store.id).first()
        if not model:
            raise ValueError("Magasin non trouvé")
        
        model.name = store.name.value
        model.address = store.address.full_address() if store.address else None
        model.phone = store.phone.formatted() if store.phone else None
        
        session.commit()
        updated = self._to_entity(model)
        session.close()
        return updated
    
    def delete(self, store_id: int) -> bool:
        """Supprimer un magasin"""
        session = self.session_factory()
        model = session.query(StoreModel).filter(StoreModel.id == store_id).first()
        if not model:
            session.close()
            return False

        session.delete(model)
        session.commit()
        session.close()
        return True
    
    def name_exists(self, name: str, exclude_id: Optional[int] = None) -> bool:
        """Vérifier si un nom de magasin existe déjà"""
        session = self.session_factory()
        query = session.query(StoreModel).filter(StoreModel.name == name)
        if exclude_id:
            query = query.filter(StoreModel.id != exclude_id)
        exists = query.first() is not None
        session.close()
        return exists
    
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
