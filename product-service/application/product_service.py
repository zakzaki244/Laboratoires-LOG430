from domain.product import Product

class ProductService:
    def __init__(self, product_repository):
        self.product_repository = product_repository

    def create_product(self, data):
        product = Product(
            name=data['name'],
            description=data.get('description', ''),
            price=data['price'],
            quantity_stock=data['quantity_stock'],
            category=data['category'],
            store_id=data['store_id']
        )
        product_id = self.product_repository.add(product)
        return {'id': product_id, 'message': "Produit créé avec succès"}, 201

    def get_product(self, product_id):
        product = self.product_repository.get_by_id(product_id)
        if not product:
            return {'message': "Produit non trouvé"}, 404
        return {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'quantity_stock': product.quantity_stock,
            'category': product.category,
            'store_id': product.store_id
        }, 200

    def update_product(self, product_id, data):
        product = self.product_repository.update(product_id, data)
        if not product:
            return {'message': "Produit non trouvé"}, 404
        return {'message': "Produit mis à jour avec succès"}, 200

    def delete_product(self, product_id):
        if not self.product_repository.delete(product_id):
            return {'message': "Produit non trouvé"}, 404
        return {'message': "Produit supprimé avec succès"}, 200

    def list_products(self, store_id=None):
        if store_id:
            products = self.product_repository.list_by_store(store_id)
        else:
            products = self.product_repository.list_all()
        return [
            {
                'id': p.id,
                'name': p.name,
                'description': p.description,
                'price': p.price,
                'quantity_stock': p.quantity_stock,
                'category': p.category,
                'store_id': p.store_id
            } for p in products
        ], 200

    def search_products(self, query, store_id=None):
        if store_id:
            products = self.product_repository.search_by_store(query, store_id)
        else:
            products = self.product_repository.search(query)
        return [
            {
                'id': p.id,
                'name': p.name,
                'description': p.description,
                'price': p.price,
                'quantity_stock': p.quantity_stock,
                'category': p.category,
                'store_id': p.store_id
            } for p in products
        ], 200

    def update_stock(self, product_id, quantity_stock):
        product = self.product_repository.update(product_id, {'quantity_stock': quantity_stock})
        if not product:
            return {'message': "Produit non trouvé"}, 404
        return {'message': "Stock mis à jour avec succès"}, 200