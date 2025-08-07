from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime, timezone
import json
import os
from typing import List, Dict, Any

# Import des modules event bus
import sys
sys.path.append('/app')

from events import Event, create_event
from event_store import MongoEventStore
from redis_event_bus import RedisEventBus, StreamTopics

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://log430:laboratoire@mongodb-eventstore:27017/eventstore')
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis-events:6379')

# Initialisation de l'Event Store et Event Bus
event_store = MongoEventStore(MONGODB_URL)
event_bus = RedisEventBus(REDIS_URL)

def initialize_services():
    """Initialise les services au démarrage"""
    try:
        event_store.connect()
        logger.info("Event Store initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Event Store: {e}")

# Initialisation immédiate des services
initialize_services()

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de santé du service"""
    try:
        stats = event_store.get_stats()
        return jsonify({
            'status': 'healthy',
            'service': 'event-store',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event_store_stats': stats
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 503

@app.route('/api/events', methods=['POST'])
def publish_event():
    """Publier un événement dans l'Event Store et le bus d'événements"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validation des champs requis
        required_fields = ['event_type', 'aggregate_id', 'aggregate_type', 'data']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Créer l'événement
        event = create_event(
            event_type=data['event_type'],
            aggregate_id=data['aggregate_id'],
            aggregate_type=data['aggregate_type'],
            data=data['data'],
            version=data.get('version', 1),
            correlation_id=data.get('correlation_id')
        )
        
        # Stocker dans l'Event Store
        if not event_store.store_event(event):
            return jsonify({'error': 'Failed to store event'}), 500
        
        # Publier sur le bus d'événements
        stream = _get_stream_for_event_type(event.event_type)
        
        
        logger.info(f"Published event {event.event_id} of type {event.event_type}")
        
        return jsonify({
            'success': True,
            'event_id': event.event_id,
            'timestamp': event.timestamp.isoformat(),
            'stream': stream
        }), 201
        
    except Exception as e:
        logger.error(f"Error publishing event: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/events/batch', methods=['POST'])
def publish_events_batch():
    """Publier plusieurs événements en batch"""
    try:
        data = request.get_json()
        if not data or 'events' not in data:
            return jsonify({'error': 'No events provided'}), 400
        
        events = []
        for event_data in data['events']:
            # Validation
            required_fields = ['event_type', 'aggregate_id', 'aggregate_type', 'data']
            for field in required_fields:
                if field not in event_data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            # Créer l'événement
            event = create_event(
                event_type=event_data['event_type'],
                aggregate_id=event_data['aggregate_id'],
                aggregate_type=event_data['aggregate_type'],
                data=event_data['data'],
                version=event_data.get('version', 1),
                correlation_id=event_data.get('correlation_id')
            )
            events.append(event)
        
        # Stocker en batch
        if not event_store.store_events_batch(events):
            return jsonify({'error': 'Failed to store events batch'}), 500
        
        logger.info(f"Published batch of {len(events)} events")
        
        return jsonify({
            'success': True,
            'events_count': len(events),
            'event_ids': [event.event_id for event in events]
        }), 201
        
    except Exception as e:
        logger.error(f"Error publishing events batch: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/events/<aggregate_id>', methods=['GET'])
def get_events_by_aggregate(aggregate_id: str):
    """Récupérer les événements d'un agrégat (Event Sourcing)"""
    try:
        from_version = request.args.get('from_version', 0, type=int)
        
        events = event_store.get_events_by_aggregate(aggregate_id, from_version)
        
        return jsonify({
            'aggregate_id': aggregate_id,
            'events_count': len(events),
            'events': [event.to_dict() for event in events]
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving events for aggregate {aggregate_id}: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/events/replay/<stream>', methods=['GET'])
def replay_events(stream: str):
    """Replay des événements d'un stream depuis une date"""
    try:
        since_param = request.args.get('since')
        limit = request.args.get('limit', 1000, type=int)
        
        if since_param:
            try:
                since = datetime.fromisoformat(since_param.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use ISO format.'}), 400
        else:
            # Par défaut, dernières 24h
            since = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        events = event_store.get_events_since(since, limit)
        
        # Filtrer par type d'événement selon le stream
        if stream != 'all':
            event_types = _get_event_types_for_stream(stream)
            events = [e for e in events if e.event_type in event_types]
        
        return jsonify({
            'stream': stream,
            'since': since.isoformat(),
            'events_count': len(events),
            'events': [event.to_dict() for event in events]
        }), 200
        
    except Exception as e:
        logger.error(f"Error replaying events for stream {stream}: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/events/types/<event_type>', methods=['GET'])
def get_events_by_type(event_type: str):
    """Récupérer les événements par type"""
    try:
        limit = request.args.get('limit', 100, type=int)
        
        events = event_store.get_events_by_type(event_type, limit)
        
        return jsonify({
            'event_type': event_type,
            'events_count': len(events),
            'events': [event.to_dict() for event in events]
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving events by type {event_type}: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/events/stats', methods=['GET'])
def get_event_store_stats():
    """Obtenir les statistiques de l'Event Store"""
    try:
        stats = event_store.get_stats()
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error getting Event Store stats: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/snapshots/<aggregate_id>', methods=['POST'])
def create_snapshot(aggregate_id: str):
    """Créer un snapshot d'un agrégat"""
    try:
        data = request.get_json()
        if not data or 'version' not in data or 'data' not in data:
            return jsonify({'error': 'Missing version or data'}), 400
        
        success = event_store.create_snapshot(
            aggregate_id=aggregate_id,
            version=data['version'],
            data=data['data']
        )
        
        if success:
            return jsonify({
                'success': True,
                'aggregate_id': aggregate_id,
                'version': data['version']
            }), 201
        else:
            return jsonify({'error': 'Failed to create snapshot'}), 500
            
    except Exception as e:
        logger.error(f"Error creating snapshot for {aggregate_id}: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/snapshots/<aggregate_id>', methods=['GET'])
def get_snapshot(aggregate_id: str):
    """Récupérer le snapshot d'un agrégat"""
    try:
        snapshot = event_store.get_snapshot(aggregate_id)
        
        if snapshot:
            return jsonify({
                'aggregate_id': aggregate_id,
                'snapshot': snapshot
            }), 200
        else:
            return jsonify({'error': 'Snapshot not found'}), 404
            
    except Exception as e:
        logger.error(f"Error retrieving snapshot for {aggregate_id}: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

def _get_stream_for_event_type(event_type: str) -> str:
    """Détermine le stream Redis pour un type d'événement"""
    event_stream_mapping = {
        'ProductSold': StreamTopics.PRODUCT_SOLD,
        'LowStockDetected': StreamTopics.LOW_STOCK_DETECTED,
        'RestockRequested': StreamTopics.RESTOCK_REQUESTED,
        'RestockApproved': StreamTopics.RESTOCK_APPROVED,
        'StockReceived': StreamTopics.STOCK_RECEIVED,
        'DeliveryScheduled': StreamTopics.DELIVERY_SCHEDULED
    }
    return event_stream_mapping.get(event_type, 'misc.events')

def _get_event_types_for_stream(stream: str) -> List[str]:
    """Retourne les types d'événements pour un stream donné"""
    stream_event_mapping = {
        'inventory': ['ProductSold', 'LowStockDetected', 'StockReceived'],
        'procurement': ['RestockRequested', 'RestockApproved'],
        'supplier': ['StockReceived', 'DeliveryScheduled'],
        'sales': ['ProductSold']
    }
    return stream_event_mapping.get(stream, [])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
