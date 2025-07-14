from typing import List, Dict, Any

class IInventoryItemRepository:
    def get_inventory_item(self, item_id: int) -> Dict[str, Any]:
        pass

    def update_inventory_item(self, item_id: int, updates: Dict[str, Any]) -> None:
        pass

class IReapproRequestRepository:
    def create_reappro_request(self, request_data: Dict[str, Any]) -> int:
        pass

    def get_reappro_request_by_id(self, request_id: int) -> Dict[str, Any]:
        pass

    def update_reappro_request(self, request_id: int, updates: Dict[str, Any]) -> None:
        pass

class IProductServiceAdapter:
    def get_product_details(self, product_id: int) -> Dict[str, Any]:
        pass

class IStoreServiceAdapter:
    def get_store_details(self, store_id: int) -> Dict[str, Any]:
        pass

class INotificationService:
    def send_notification(self, notification_data: Dict[str, Any]) -> None:
        pass
