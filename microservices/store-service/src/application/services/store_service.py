from typing import List, Optional

from ..dto import CreateStoreRequest, UpdateStoreRequest, StoreResponse
from ...domain.entities import Store
from ...domain.repositories import IStoreRepository
from ...domain.value_objects import StoreName, Address, Phone

class StoreService:
    """Service d'application pour la gestion des magasins"""
    
    def __init__(self, store_repository: IStoreRepository):
        self.store_repository = store_repository
    
    def get_all_stores(self) -> List[StoreResponse]:
        """Récupérer tous les magasins"""
        stores = self.store_repository.get_all()
        return [self._to_response(store) for store in stores]
    
    def get_store_by_id(self, store_id: int) -> Optional[StoreResponse]:
        """Récupérer un magasin par son ID"""
        store = self.store_repository.get_by_id(store_id)
        return self._to_response(store) if store else None
    
    def create_store(self, request: CreateStoreRequest) -> StoreResponse:
        """Créer un nouveau magasin"""
        if self.store_repository.name_exists(request.name):
            raise ValueError("Un magasin avec ce nom existe déjà")
        
        name = StoreName(request.name)
        
        address = None
        if request.address:
            address_parts = request.address.split(', ')
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
        if request.phone:
            phone = Phone(request.phone)
        
        store = Store(
            id=None,
            name=name,
            address=address,
            phone=phone
        )
        
        saved_store = self.store_repository.save(store)
        return self._to_response(saved_store)
    
    def update_store(self, store_id: int, request: UpdateStoreRequest) -> Optional[StoreResponse]:
        """Mettre à jour un magasin"""
        store = self.store_repository.get_by_id(store_id)
        if not store:
            return None
        
        if request.name is not None:
            if self.store_repository.name_exists(request.name, store_id):
                raise ValueError("Un magasin avec ce nom existe déjà")
            store.update_name(StoreName(request.name))
        
        if request.address is not None:
            if request.address.strip():
                address_parts = request.address.split(', ')
                if len(address_parts) >= 3:
                    street = address_parts[0]
                    city = address_parts[1]
                    province_postal = address_parts[2].split(' ')
                    if len(province_postal) >= 2:
                        province = province_postal[0]
                        postal_code = ' '.join(province_postal[1:3])
                        country = address_parts[3] if len(address_parts) > 3 else "Canada"
                        address = Address(street, city, postal_code, province, country)
                        store.update_address(address)
            else:
                store.address = None
        
        if request.phone is not None:
            if request.phone.strip():
                store.update_phone(Phone(request.phone))
            else:
                store.phone = None
        
        updated_store = self.store_repository.update(store)
        return self._to_response(updated_store)
    
    def delete_store(self, store_id: int) -> bool:
        """Supprimer un magasin"""
        return self.store_repository.delete(store_id)
    
    def _to_response(self, store: Store) -> StoreResponse:
        """Convertir une entité en DTO de réponse"""
        return StoreResponse(
            id=store.id,
            name=store.name.value,
            address=store.address.full_address() if store.address else None,
            phone=store.phone.formatted() if store.phone else None
        )
