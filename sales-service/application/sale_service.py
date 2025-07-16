from domain.sale import Sale
from domain.sale_item import SaleItem
from datetime import datetime

class SaleService:
    def __init__(self, sale_repository, sale_item_repository):
        self.sale_repository = sale_repository
        self.sale_item_repository = sale_item_repository

    def create_sale(self, data):
        # Calculer le total à partir des items
        items_data = data.get('items', [])
        total = sum(item['quantity'] * item['unit_price'] for item in items_data)
        
        # Créer la vente
        sale = Sale(
            client_id=data['client_id'],
            total=total
        )
        sale_id = self.sale_repository.add(sale)
        
        # Créer les items de vente
        for item_data in items_data:
            sale_item = SaleItem(
                sale_id=sale_id,
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price']
            )
            self.sale_item_repository.add(sale_item)
        
        return {'id': sale_id, 'message': "Vente créée avec succès"}, 201

    def get_sale(self, sale_id):
        sale = self.sale_repository.get_by_id(sale_id)
        if not sale:
            return {'message': "Vente non trouvée"}, 404
        
        # Récupérer les items de la vente
        items = self.sale_item_repository.get_by_sale_id(sale_id)
        
        return {
            'id': sale.id,
            'client_id': sale.client_id,
            'total': sale.total,
            'date': sale.date.isoformat(),
            'items': [
                {
                    'id': item.id,
                    'product_id': item.product_id,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price
                } for item in items
            ]
        }, 200

    def delete_sale(self, sale_id):
        if not self.sale_repository.delete(sale_id):
            return {'message': "Vente non trouvée"}, 404
        return {'message': "Vente supprimée avec succès"}, 200

    def list_sales(self):
        sales = self.sale_repository.list_all()
        return [
            {
                'id': sale.id,
                'client_id': sale.client_id,
                'total': sale.total,
                'date': sale.date.isoformat()
            } for sale in sales
        ], 200

    def get_sales_by_client(self, client_id):
        sales = self.sale_repository.get_by_client(client_id)
        return [
            {
                'id': sale.id,
                'client_id': sale.client_id,
                'total': sale.total,
                'date': sale.date.isoformat()
            } for sale in sales
        ], 200

    def generate_report(self, start_date=None, end_date=None):
        if start_date:
            start_date = datetime.fromisoformat(start_date)
        if end_date:
            end_date = datetime.fromisoformat(end_date)
        
        sales = self.sale_repository.get_sales_by_date_range(start_date, end_date)
        
        total_sales = len(sales)
        total_revenue = sum(sale.total for sale in sales)
        
        return {
            'total_sales': total_sales,
            'total_revenue': total_revenue,
            'period': {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None
            }
        }, 200