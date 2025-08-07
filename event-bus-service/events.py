from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
import uuid
import logging

logger = logging.getLogger(__name__)

@dataclass
class Event:
    """Modèle de base pour tous les événements"""
    event_id: str
    event_type: str
    aggregate_id: str
    aggregate_type: str
    data: Dict[str, Any]
    timestamp: datetime
    version: int = 1
    correlation_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        if not self.correlation_id:
            self.correlation_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'événement en dictionnaire pour sérialisation"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Crée un événement à partir d'un dictionnaire"""
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        return cls(**data)

class EventPublisher(ABC):
    """Interface abstraite pour publier des événements"""
    
    @abstractmethod
    async def publish(self, event: Event, stream: str) -> bool:
        """Publie un événement sur un stream donné"""
        pass
    
    @abstractmethod
    async def publish_batch(self, events: List[Event], stream: str) -> bool:
        """Publie plusieurs événements en batch"""
        pass

class EventSubscriber(ABC):
    """Interface abstraite pour consommer des événements"""
    
    @abstractmethod
    async def subscribe(self, streams: List[str], handler: Callable[[Event], None], 
                       consumer_group: str = None) -> None:
        """S'abonne à un ou plusieurs streams"""
        pass
    
    @abstractmethod
    async def unsubscribe(self, streams: List[str]) -> None:
        """Se désabonne des streams"""
        pass

class EventHandler(ABC):
    """Interface pour les gestionnaires d'événements"""
    
    @abstractmethod
    def can_handle(self, event: Event) -> bool:
        """Détermine si ce handler peut traiter l'événement"""
        pass
    
    @abstractmethod
    async def handle(self, event: Event) -> None:
        """Traite l'événement"""
        pass

class EventBus(ABC):
    """Interface du bus d'événements"""
    
    @abstractmethod
    async def publish(self, event: Event, stream: str) -> bool:
        pass
    
    @abstractmethod
    async def subscribe(self, streams: List[str], handler: EventHandler, 
                       consumer_group: str = None) -> None:
        pass
    
    @abstractmethod
    async def get_events(self, stream: str, start_id: str = '0', 
                        count: int = 100) -> List[Event]:
        """Récupère les événements d'un stream (pour replay)"""
        pass

# Événements spécifiques pour Lab 7

@dataclass
class ProductSoldEvent(Event):
    """Événement : Produit vendu"""
    
    def __init__(self, product_id: str, quantity: int, price: float, 
                 customer_id: str, **kwargs):
        super().__init__(
            event_type="ProductSold",
            aggregate_id=product_id,
            aggregate_type="Product",
            data={
                "product_id": product_id,
                "quantity": quantity,
                "price": price,
                "customer_id": customer_id,
                "total_amount": quantity * price
            },
            **kwargs
        )

@dataclass
class LowStockDetectedEvent(Event):
    """Événement : Stock faible détecté"""
    
    def __init__(self, product_id: str, current_stock: int, minimum_threshold: int, **kwargs):
        super().__init__(
            event_type="LowStockDetected",
            aggregate_id=product_id,
            aggregate_type="Product",
            data={
                "product_id": product_id,
                "current_stock": current_stock,
                "minimum_threshold": minimum_threshold,
                "shortage": minimum_threshold - current_stock
            },
            **kwargs
        )

@dataclass
class RestockRequestedEvent(Event):
    """Événement : Demande de réapprovisionnement"""
    
    def __init__(self, product_id: str, requested_quantity: int, 
                 supplier_id: str, priority: str = "normal", **kwargs):
        super().__init__(
            event_type="RestockRequested",
            aggregate_id=f"restock_{product_id}_{uuid.uuid4().hex[:8]}",
            aggregate_type="RestockRequest",
            data={
                "product_id": product_id,
                "requested_quantity": requested_quantity,
                "supplier_id": supplier_id,
                "priority": priority,
                "estimated_delivery_days": 5 if priority == "normal" else 2
            },
            **kwargs
        )

@dataclass
class StockReceivedEvent(Event):
    """Événement : Stock reçu du fournisseur"""
    
    def __init__(self, product_id: str, received_quantity: int, 
                 supplier_id: str, restock_request_id: str, **kwargs):
        super().__init__(
            event_type="StockReceived",
            aggregate_id=product_id,
            aggregate_type="Product",
            data={
                "product_id": product_id,
                "received_quantity": received_quantity,
                "supplier_id": supplier_id,
                "restock_request_id": restock_request_id,
                "delivery_date": datetime.now(timezone.utc).isoformat()
            },
            **kwargs
        )

@dataclass
class RestockApprovedEvent(Event):
    """Événement : Demande de réapprovisionnement approuvée"""
    
    def __init__(self, restock_request_id: str, approved_by: str, 
                 approved_quantity: int, **kwargs):
        super().__init__(
            event_type="RestockApproved",
            aggregate_id=restock_request_id,
            aggregate_type="RestockRequest",
            data={
                "restock_request_id": restock_request_id,
                "approved_by": approved_by,
                "approved_quantity": approved_quantity,
                "approval_date": datetime.now(timezone.utc).isoformat()
            },
            **kwargs
        )

# Types d'événements disponibles
EVENT_TYPES = {
    "ProductSold": ProductSoldEvent,
    "LowStockDetected": LowStockDetectedEvent,
    "RestockRequested": RestockRequestedEvent,
    "StockReceived": StockReceivedEvent,
    "RestockApproved": RestockApprovedEvent,
}

def create_event(event_type: str, **kwargs) -> Event:
    """Factory pour créer des événements typés"""
    event_class = EVENT_TYPES.get(event_type)
    if not event_class:
        # Fallback vers Event générique
        return Event(event_type=event_type, **kwargs)
    return event_class(**kwargs)
