import redis.asyncio as redis
import json
import asyncio
from typing import List, Dict, Any, Callable, Optional
import logging
from datetime import datetime

from .events import Event, EventBus, EventHandler

logger = logging.getLogger(__name__)

class RedisEventBus(EventBus):
    """Implémentation du bus d'événements avec Redis Streams"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        self.running = False
        self.subscriptions = {}
    
    async def connect(self):
        """Établit la connexion à Redis"""
        try:
            self.redis = redis.from_url(self.redis_url, decode_responses=True)
            await self.redis.ping()
            logger.info("Connected to Redis Event Bus")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Ferme la connexion Redis"""
        self.running = False
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis Event Bus")
    
    async def publish(self, event: Event, stream: str) -> bool:
        """Publie un événement sur un stream Redis"""
        try:
            if not self.redis:
                await self.connect()
            
            # Sérialiser l'événement
            event_data = {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "aggregate_id": event.aggregate_id,
                "aggregate_type": event.aggregate_type,
                "data": json.dumps(event.data),
                "timestamp": event.timestamp.isoformat(),
                "version": str(event.version),
                "correlation_id": event.correlation_id or ""
            }
            
            # Publier sur le stream
            message_id = await self.redis.xadd(stream, event_data)
            
            logger.info(f"Published event {event.event_id} to stream {stream} with ID {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish event to stream {stream}: {e}")
            return False
    
    async def publish_batch(self, events: List[Event], stream: str) -> bool:
        """Publie plusieurs événements en batch"""
        try:
            async with self.redis.pipeline(transaction=True) as pipe:
                for event in events:
                    event_data = {
                        "event_id": event.event_id,
                        "event_type": event.event_type,
                        "aggregate_id": event.aggregate_id,
                        "aggregate_type": event.aggregate_type,
                        "data": json.dumps(event.data),
                        "timestamp": event.timestamp.isoformat(),
                        "version": str(event.version),
                        "correlation_id": event.correlation_id or ""
                    }
                    pipe.xadd(stream, event_data)
                
                await pipe.execute()
                logger.info(f"Published batch of {len(events)} events to stream {stream}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to publish batch to stream {stream}: {e}")
            return False
    
    async def subscribe(self, streams: List[str], handler: EventHandler, 
                       consumer_group: str = None) -> None:
        """S'abonne à des streams avec un handler"""
        if not self.redis:
            await self.connect()
        
        consumer_group = consumer_group or f"group_{handler.__class__.__name__}"
        consumer_name = f"consumer_{handler.__class__.__name__}_{id(handler)}"
        
        # Créer les groupes de consommateurs
        for stream in streams:
            try:
                await self.redis.xgroup_create(stream, consumer_group, id='0', mkstream=True)
                logger.info(f"Created consumer group {consumer_group} for stream {stream}")
            except redis.exceptions.ResponseError as e:
                if "BUSYGROUP" not in str(e):
                    logger.error(f"Failed to create consumer group: {e}")
        
        # Stocker la subscription
        self.subscriptions[f"{consumer_group}_{consumer_name}"] = {
            'streams': streams,
            'handler': handler,
            'consumer_group': consumer_group,
            'consumer_name': consumer_name,
            'running': True
        }
        
        # Démarrer la tâche de consommation
        asyncio.create_task(self._consume_events(streams, handler, consumer_group, consumer_name))
    
    async def _consume_events(self, streams: List[str], handler: EventHandler, 
                             consumer_group: str, consumer_name: str):
        """Tâche de consommation d'événements"""
        logger.info(f"Starting event consumption for {consumer_name} on streams {streams}")
        
        subscription_key = f"{consumer_group}_{consumer_name}"
        
        while self.subscriptions.get(subscription_key, {}).get('running', False):
            try:
                # Lire les messages en attente d'abord
                pending_messages = await self.redis.xreadgroup(
                    consumer_group, consumer_name, 
                    {stream: '0' for stream in streams},
                    count=10, block=100
                )
                
                if pending_messages:
                    await self._process_messages(pending_messages, handler)
                
                # Lire les nouveaux messages
                new_messages = await self.redis.xreadgroup(
                    consumer_group, consumer_name,
                    {stream: '>' for stream in streams},
                    count=10, block=1000
                )
                
                if new_messages:
                    await self._process_messages(new_messages, handler)
                
            except Exception as e:
                if "timeout" not in str(e).lower():
                    logger.error(f"Error consuming events for {consumer_name}: {e}")
                await asyncio.sleep(1)
        
        logger.info(f"Stopped event consumption for {consumer_name}")
    
    async def _process_messages(self, messages: List, handler: EventHandler):
        """Traite les messages reçus"""
        for stream, stream_messages in messages:
            for message_id, fields in stream_messages:
                try:
                    # Reconstruire l'événement
                    event = Event(
                        event_id=fields['event_id'],
                        event_type=fields['event_type'],
                        aggregate_id=fields['aggregate_id'],
                        aggregate_type=fields['aggregate_type'],
                        data=json.loads(fields['data']),
                        timestamp=datetime.fromisoformat(fields['timestamp']),
                        version=int(fields['version']),
                        correlation_id=fields.get('correlation_id')
                    )
                    
                    # Vérifier si le handler peut traiter l'événement
                    if handler.can_handle(event):
                        await handler.handle(event)
                        logger.debug(f"Processed event {event.event_id} with {handler.__class__.__name__}")
                    
                    # Acquitter le message
                    # Note: Dans une implémentation production, on ferait ça après traitement réussi
                    await self.redis.xack(stream, 
                                         f"group_{handler.__class__.__name__}", 
                                         message_id)
                    
                except Exception as e:
                    logger.error(f"Failed to process message {message_id}: {e}")
    
    async def get_events(self, stream: str, start_id: str = '0', 
                        count: int = 100) -> List[Event]:
        """Récupère les événements d'un stream pour replay"""
        try:
            if not self.redis:
                await self.connect()
            
            messages = await self.redis.xrange(stream, min=start_id, count=count)
            events = []
            
            for message_id, fields in messages:
                event = Event(
                    event_id=fields['event_id'],
                    event_type=fields['event_type'],
                    aggregate_id=fields['aggregate_id'],
                    aggregate_type=fields['aggregate_type'],
                    data=json.loads(fields['data']),
                    timestamp=datetime.fromisoformat(fields['timestamp']),
                    version=int(fields['version']),
                    correlation_id=fields.get('correlation_id')
                )
                events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to get events from stream {stream}: {e}")
            return []
    
    async def get_stream_info(self, stream: str) -> Dict[str, Any]:
        """Obtient les informations d'un stream"""
        try:
            if not self.redis:
                await self.connect()
            
            info = await self.redis.xinfo_stream(stream)
            return {
                'length': info['length'],
                'first_entry': info.get('first-entry'),
                'last_entry': info.get('last-entry'),
                'groups': info.get('groups', 0)
            }
        except Exception as e:
            logger.error(f"Failed to get info for stream {stream}: {e}")
            return {}

# Streams prédéfinis pour Lab 7
STREAMS = {
    'INVENTORY_EVENTS': 'inventory.events',
    'SALES_EVENTS': 'sales.events', 
    'PROCUREMENT_EVENTS': 'procurement.events',
    'SUPPLIER_EVENTS': 'supplier.events',
    'ANALYTICS_EVENTS': 'analytics.events'
}

class StreamTopics:
    """Topics/Streams pour l'architecture événementielle"""
    PRODUCT_SOLD = "inventory.products.sold"
    LOW_STOCK_DETECTED = "inventory.stock.low"
    RESTOCK_REQUESTED = "procurement.restock.requested"
    RESTOCK_APPROVED = "procurement.restock.approved"
    STOCK_RECEIVED = "supplier.stock.received"
    DELIVERY_SCHEDULED = "supplier.delivery.scheduled"
