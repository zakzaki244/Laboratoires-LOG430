from domain.store import Store

class StoreService:
    def __init__(self, store_repository):
        self.store_repository = store_repository

    def create_store(self, data):
        store = Store(
            name=data['name'],
            address=data['address'],
            phone=data['phone'],
            email=data['email']
        )
        store_id = self.store_repository.add(store)
        return {'id': store_id, 'message': "Magasin créé avec succès"}, 201

    def get_store(self, store_id):
        store = self.store_repository.get_by_id(store_id)
        if not store:
            return {'message': "Magasin non trouvé"}, 404
        return {
            'id': store.id,
            'name': store.name,
            'address': store.address,
            'phone': store.phone,
            'email': store.email
        }, 200

    def update_store(self, store_id, data):
        store = self.store_repository.update(store_id, data)
        if not store:
            return {'message': "Magasin non trouvé"}, 404
        return {'message': "Magasin mis à jour avec succès"}, 200

    def delete_store(self, store_id):
        if not self.store_repository.delete(store_id):
            return {'message': "Magasin non trouvé"}, 404
        return {'message': "Magasin supprimé avec succès"}, 200

    def list_stores(self):
        stores = self.store_repository.list_all()
        return [
            {
                'id': store.id,
                'name': store.name,
                'address': store.address,
                'phone': store.phone,
                'email': store.email
            } for store in stores
        ], 200

    def search_stores(self, query):
        stores = self.store_repository.search(query)
        return [
            {
                'id': store.id,
                'name': store.name,
                'address': store.address,
                'phone': store.phone,
                'email': store.email
            } for store in stores
        ], 200