from infrastructure.db import db, StoreModel
from domain.store import Store

class StoreRepository:
    def add(self, store: Store):
        store_model = StoreModel(
            name=store.name,
            address=store.address,
            phone=store.phone,
            email=store.email
        )
        db.session.add(store_model)
        db.session.commit()
        return store_model.id

    def get_by_id(self, store_id):
        store_model = StoreModel.query.get(store_id)
        if store_model:
            return Store(
                id=store_model.id,
                name=store_model.name,
                address=store_model.address,
                phone=store_model.phone,
                email=store_model.email
            )
        return None

    def update(self, store_id, data):
        store_model = StoreModel.query.get(store_id)
        if not store_model:
            return None
        for key, value in data.items():
            if hasattr(store_model, key):
                setattr(store_model, key, value)
        db.session.commit()
        return store_model

    def delete(self, store_id):
        store_model = StoreModel.query.get(store_id)
        if not store_model:
            return False
        db.session.delete(store_model)
        db.session.commit()
        return True

    def list_all(self):
        return StoreModel.query.all()

    def search(self, query):
        return StoreModel.query.filter(getattr(StoreModel, 'name').ilike(f'%{query}%')).all()