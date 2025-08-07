from pymongo import MongoClient
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import json
import logging

from events import Event

logger = logging.getLogger(__name__)

class MongoEventStore:
    """Event Store utilisant MongoDB pour la persistance des événements"""
    
    def __init__(self, connection_string: str = "mongodb://log430:laboratoire@localhost:27017/eventstore"):
        self.connection_string = connection_string
        self.client = None
        self.db = None
        self.events_collection = None
        self.snapshots_collection = None
    
    def connect(self):
        """Établit la connexion à MongoDB"""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client.eventstore
            self.events_collection = self.db.events
            self.snapshots_collection = self.db.snapshots
            
            # Créer les index pour les performances
            self.events_collection.create_index("aggregate_id")
            self.events_collection.create_index("event_type")
            self.events_collection.create_index("timestamp")
            self.events_collection.create_index([("aggregate_id", 1), ("version", 1)], unique=True)
            
            logger.info("Connected to MongoDB Event Store")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def disconnect(self):
        """Ferme la connexion MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB Event Store")
    
    def store_event(self, event: Event) -> bool:
        """Stocke un événement dans l'Event Store"""
        try:
            if self.events_collection is None:
                self.connect()
            
            # Convertir l'événement en document MongoDB
            event_doc = {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "aggregate_id": event.aggregate_id,
                "aggregate_type": event.aggregate_type,
                "data": event.data,
                "timestamp": event.timestamp,
                "version": event.version,
                "correlation_id": event.correlation_id
            }
            
            # Insérer l'événement
            result = self.events_collection.insert_one(event_doc)
            
            if result.inserted_id:
                logger.debug(f"Stored event {event.event_id} in Event Store")
                return True
            else:
                logger.error(f"Failed to store event {event.event_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error storing event {event.event_id}: {e}")
            return False
    
    def store_events_batch(self, events: List[Event]) -> bool:
        """Stocke plusieurs événements en batch"""
        try:
            if self.events_collection is None:
                self.connect()
            
            # Convertir tous les événements
            event_docs = []
            for event in events:
                event_doc = {
                    "event_id": event.event_id,
                    "event_type": event.event_type,
                    "aggregate_id": event.aggregate_id,
                    "aggregate_type": event.aggregate_type,
                    "data": event.data,
                    "timestamp": event.timestamp,
                    "version": event.version,
                    "correlation_id": event.correlation_id
                }
                event_docs.append(event_doc)
            
            # Insérer en batch
            result = self.events_collection.insert_many(event_docs)
            
            if len(result.inserted_ids) == len(events):
                logger.info(f"Stored batch of {len(events)} events in Event Store")
                return True
            else:
                logger.error(f"Failed to store some events in batch")
                return False
                
        except Exception as e:
            logger.error(f"Error storing events batch: {e}")
            return False
    
    def get_events_by_aggregate(self, aggregate_id: str, from_version: int = 0) -> List[Event]:
        """Récupère tous les événements pour un agrégat donné"""
        try:
            if self.events_collection is None:
                self.connect()
            
            # Requête MongoDB
            query = {
                "aggregate_id": aggregate_id,
                "version": {"$gte": from_version}
            }
            
            cursor = self.events_collection.find(query).sort("version", 1)
            events = []
            
            for doc in cursor:
                event = Event(
                    event_id=doc["event_id"],
                    event_type=doc["event_type"],
                    aggregate_id=doc["aggregate_id"],
                    aggregate_type=doc["aggregate_type"],
                    data=doc["data"],
                    timestamp=doc["timestamp"],
                    version=doc["version"],
                    correlation_id=doc.get("correlation_id")
                )
                events.append(event)
            
            logger.debug(f"Retrieved {len(events)} events for aggregate {aggregate_id}")
            return events
            
        except Exception as e:
            logger.error(f"Error retrieving events for aggregate {aggregate_id}: {e}")
            return []
    
    def get_events_by_type(self, event_type: str, limit: int = 100) -> List[Event]:
        """Récupère les événements par type"""
        try:
            if self.events_collection is None:
                self.connect()
            
            cursor = self.events_collection.find(
                {"event_type": event_type}
            ).sort("timestamp", -1).limit(limit)
            
            events = []
            for doc in cursor:
                event = Event(
                    event_id=doc["event_id"],
                    event_type=doc["event_type"],
                    aggregate_id=doc["aggregate_id"],
                    aggregate_type=doc["aggregate_type"],
                    data=doc["data"],
                    timestamp=doc["timestamp"],
                    version=doc["version"],
                    correlation_id=doc.get("correlation_id")
                )
                events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Error retrieving events by type {event_type}: {e}")
            return []
    
    def get_events_since(self, since: datetime, limit: int = 1000) -> List[Event]:
        """Récupère les événements depuis une date donnée"""
        try:
            if self.events_collection is None:
                self.connect()
            
            cursor = self.events_collection.find(
                {"timestamp": {"$gte": since}}
            ).sort("timestamp", 1).limit(limit)
            
            events = []
            for doc in cursor:
                event = Event(
                    event_id=doc["event_id"],
                    event_type=doc["event_type"],
                    aggregate_id=doc["aggregate_id"],
                    aggregate_type=doc["aggregate_type"],
                    data=doc["data"],
                    timestamp=doc["timestamp"],
                    version=doc["version"],
                    correlation_id=doc.get("correlation_id")
                )
                events.append(event)
            
            logger.info(f"Retrieved {len(events)} events since {since}")
            return events
            
        except Exception as e:
            logger.error(f"Error retrieving events since {since}: {e}")
            return []
    
    def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """Récupère un événement par son ID"""
        try:
            if self.events_collection is None:
                self.connect()
            
            doc = self.events_collection.find_one({"event_id": event_id})
            
            if doc:
                return Event(
                    event_id=doc["event_id"],
                    event_type=doc["event_type"],
                    aggregate_id=doc["aggregate_id"],
                    aggregate_type=doc["aggregate_type"],
                    data=doc["data"],
                    timestamp=doc["timestamp"],
                    version=doc["version"],
                    correlation_id=doc.get("correlation_id")
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving event {event_id}: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtient les statistiques de l'Event Store"""
        try:
            if self.events_collection is None:
                self.connect()
            
            total_events = self.events_collection.count_documents({})
            
            # Statistiques par type d'événement
            pipeline = [
                {"$group": {"_id": "$event_type", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            event_types_stats = list(self.events_collection.aggregate(pipeline))
            
            # Statistiques par agrégat
            pipeline = [
                {"$group": {"_id": "$aggregate_type", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            aggregate_types_stats = list(self.events_collection.aggregate(pipeline))
            
            # Dernier événement
            last_event = self.events_collection.find_one(sort=[("timestamp", -1)])
            
            return {
                "total_events": total_events,
                "event_types": {stat["_id"]: stat["count"] for stat in event_types_stats},
                "aggregate_types": {stat["_id"]: stat["count"] for stat in aggregate_types_stats},
                "last_event_timestamp": last_event["timestamp"] if last_event else None
            }
            
        except Exception as e:
            logger.error(f"Error getting Event Store stats: {e}")
            return {}
    
    def create_snapshot(self, aggregate_id: str, version: int, data: Dict[str, Any]) -> bool:
        """Crée un snapshot d'un agrégat pour optimiser la reconstruction"""
        try:
            if self.snapshots_collection is None:
                self.connect()
            
            snapshot_doc = {
                "aggregate_id": aggregate_id,
                "version": version,
                "data": data,
                "timestamp": datetime.now(timezone.utc)
            }
            
            # Remplacer le snapshot existant
            result = self.snapshots_collection.replace_one(
                {"aggregate_id": aggregate_id},
                snapshot_doc,
                upsert=True
            )
            
            logger.debug(f"Created snapshot for aggregate {aggregate_id} at version {version}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating snapshot for {aggregate_id}: {e}")
            return False
    
    def get_snapshot(self, aggregate_id: str) -> Optional[Dict[str, Any]]:
        """Récupère le snapshot le plus récent d'un agrégat"""
        try:
            if self.snapshots_collection is None:
                self.connect()
            
            snapshot = self.snapshots_collection.find_one({"aggregate_id": aggregate_id})
            
            if snapshot:
                return {
                    "version": snapshot["version"],
                    "data": snapshot["data"],
                    "timestamp": snapshot["timestamp"]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving snapshot for {aggregate_id}: {e}")
            return None
