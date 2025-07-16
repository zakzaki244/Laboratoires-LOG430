from infrastructure.db import db, SaleModel, SaleItemModel
from domain.sale import Sale
from domain.sale_item import SaleItem

class SaleRepository:
    def add(self, sale: Sale):
        sale_model = SaleModel(
            client_id=sale.client_id,
            total=sale.total,
            date=sale.date
        )
        db.session.add(sale_model)
        db.session.commit()
        return sale_model.id

    def get_by_id(self, sale_id):
        sale_model = SaleModel.query.get(sale_id)
        if sale_model:
            return Sale(
                id=sale_model.id,
                client_id=sale_model.client_id,
                total=sale_model.total,
                date=sale_model.date
            )
        return None

    def update(self, sale_id, data):
        sale_model = SaleModel.query.get(sale_id)
        if not sale_model:
            return None
        for key, value in data.items():
            if hasattr(sale_model, key):
                setattr(sale_model, key, value)
        db.session.commit()
        return sale_model

    def delete(self, sale_id):
        sale_model = SaleModel.query.get(sale_id)
        if not sale_model:
            return False
        db.session.delete(sale_model)
        db.session.commit()
        return True

    def list_all(self):
        return SaleModel.query.all()

    def get_by_client(self, client_id):
        return SaleModel.query.filter_by(client_id=client_id).all()

    def get_sales_by_date_range(self, start_date, end_date):
        return SaleModel.query.filter(
            SaleModel.date >= start_date,
            SaleModel.date <= end_date
        ).all()

class SaleItemRepository:
    def add(self, sale_item: SaleItem):
        sale_item_model = SaleItemModel(
            sale_id=sale_item.sale_id,
            product_id=sale_item.product_id,
            quantity=sale_item.quantity,
            unit_price=sale_item.unit_price
        )
        db.session.add(sale_item_model)
        db.session.commit()
        return sale_item_model.id

    def get_by_sale_id(self, sale_id):
        sale_items = SaleItemModel.query.filter_by(sale_id=sale_id).all()
        return [
            SaleItem(
                id=item.id,
                sale_id=item.sale_id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price
            ) for item in sale_items
        ]