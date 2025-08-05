from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class OrderState(Enum):
    """États possibles d'une commande dans la Saga"""
    INITIATED = "initiated"
    STOCK_CHECKED = "stock_checked"
    STOCK_RESERVED = "stock_reserved"
    PAYMENT_PROCESSED = "payment_processed"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class SagaEvent(Enum):
    """Événements de la Saga"""
    SAGA_STARTED = "saga_started"
    STOCK_CHECK_SUCCESS = "stock_check_success"
    STOCK_CHECK_FAILED = "stock_check_failed"
    STOCK_RESERVATION_SUCCESS = "stock_reservation_success"
    STOCK_RESERVATION_FAILED = "stock_reservation_failed"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    ORDER_CONFIRMED = "order_confirmed"
    SAGA_FAILED = "saga_failed"
    COMPENSATION_STARTED = "compensation_started"
    COMPENSATION_COMPLETED = "compensation_completed"

class OrderStateMachine:
    """Machine d'état pour gérer l'évolution des commandes"""
    
    def __init__(self):
        self.transitions = {
            OrderState.INITIATED: [OrderState.STOCK_CHECKED, OrderState.FAILED],
            OrderState.STOCK_CHECKED: [OrderState.STOCK_RESERVED, OrderState.FAILED],
            OrderState.STOCK_RESERVED: [OrderState.PAYMENT_PROCESSED, OrderState.CANCELLED],
            OrderState.PAYMENT_PROCESSED: [OrderState.CONFIRMED, OrderState.CANCELLED],
            OrderState.CONFIRMED: [],  # État final
            OrderState.FAILED: [],     # État final
            OrderState.CANCELLED: []   # État final
        }
    
    def can_transition(self, from_state: OrderState, to_state: OrderState) -> bool:
        """Vérifie si une transition d'état est valide"""
        return to_state in self.transitions.get(from_state, [])
    
    def get_next_valid_states(self, current_state: OrderState) -> list[OrderState]:
        """Retourne les états valides suivants"""
        return self.transitions.get(current_state, [])
    
    def is_final_state(self, state: OrderState) -> bool:
        """Vérifie si un état est final"""
        return state in [OrderState.CONFIRMED, OrderState.FAILED, OrderState.CANCELLED]

class OrderSaga:
    """Représente une instance de Saga pour une commande"""
    
    def __init__(self, order_id: str, customer_id: str, items: list[Dict[str, Any]]):
        self.order_id = order_id
        self.customer_id = customer_id
        self.items = items
        self.current_state = OrderState.INITIATED
        self.state_machine = OrderStateMachine()
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.events = []
        self.error_message = None
        self.compensation_data = {}
        
        # Ajouter l'événement initial
        self.add_event(SagaEvent.SAGA_STARTED, {"order_id": order_id})
    
    def add_event(self, event: SagaEvent, data: Optional[Dict[str, Any]] = None):
        """Ajoute un événement à l'historique de la Saga"""
        event_record = {
            "event": event.value,
            "timestamp": datetime.utcnow(),
            "state": self.current_state.value,
            "data": data or {}
        }
        self.events.append(event_record)
        self.updated_at = datetime.utcnow()
        logger.info(f"Saga {self.order_id}: {event.value} -> {self.current_state.value}")
    
    def transition_to(self, new_state: OrderState, event: SagaEvent, data: Optional[Dict[str, Any]] = None):
        """Effectue une transition d'état"""
        if not self.state_machine.can_transition(self.current_state, new_state):
            raise ValueError(f"Transition invalide: {self.current_state} -> {new_state}")
        
        self.current_state = new_state
        self.add_event(event, data)
    
    def mark_failed(self, error_message: str):
        """Marque la Saga comme échouée"""
        self.current_state = OrderState.FAILED
        self.error_message = error_message
        self.add_event(SagaEvent.SAGA_FAILED, {"error": error_message})
    
    def mark_cancelled(self, reason: str):
        """Marque la Saga comme annulée (compensation)"""
        self.current_state = OrderState.CANCELLED
        self.add_event(SagaEvent.COMPENSATION_STARTED, {"reason": reason})
    
    def add_compensation_data(self, service: str, data: Dict[str, Any]):
        """Ajoute des données pour la compensation"""
        self.compensation_data[service] = data
    
    def get_compensation_data(self, service: str) -> Optional[Dict[str, Any]]:
        """Récupère les données de compensation pour un service"""
        return self.compensation_data.get(service)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit la Saga en dictionnaire pour la sérialisation"""
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "items": self.items,
            "current_state": self.current_state.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "events": self.events,
            "error_message": self.error_message,
            "compensation_data": self.compensation_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrderSaga':
        """Crée une Saga à partir d'un dictionnaire"""
        saga = cls(data["order_id"], data["customer_id"], data["items"])
        saga.current_state = OrderState(data["current_state"])
        saga.created_at = datetime.fromisoformat(data["created_at"])
        saga.updated_at = datetime.fromisoformat(data["updated_at"])
        saga.events = data["events"]
        saga.error_message = data.get("error_message")
        saga.compensation_data = data.get("compensation_data", {})
        return saga 