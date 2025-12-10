#!/usr/bin/env python3
"""
Real-Time Event Streaming Platform v13.0
Distributed event streaming with Kafka/RabbitMQ, WebSocket, event replay
Production-grade event-driven architecture
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
import sqlite3
from pathlib import Path
import time

# Async frameworks
import websockets
import aiohttp
from aiohttp import web

# Message brokers
try:
    from kafka import KafkaProducer, KafkaConsumer
    from kafka.admin import KafkaAdminClient, NewTopic
    import pika  # RabbitMQ
except ImportError:
    print("Warning: kafka-python or pika not installed")

# Event serialization
import msgpack
import pickle

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
EVENT_DB = '/var/lib/events/streaming.db'
EVENT_STORE = '/var/lib/events/store/'
KAFKA_BROKERS = os.getenv('KAFKA_BROKERS', 'localhost:9092').split(',')
RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost/')
WEBSOCKET_PORT = int(os.getenv('WEBSOCKET_PORT', '8765'))

# Event retention
EVENT_RETENTION_DAYS = 30
MAX_REPLAY_EVENTS = 100000

for directory in [os.path.dirname(EVENT_DB), EVENT_STORE]:
    Path(directory).mkdir(parents=True, exist_ok=True)

################################################################################
# Data Models
################################################################################

class EventType(Enum):
    """Event types"""
    SYSTEM = "system"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    SECURITY = "security"
    COST = "cost"
    USER_ACTION = "user_action"
    ALERT = "alert"
    AUDIT = "audit"

class EventPriority(Enum):
    """Event priority"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Event:
    """Event model"""
    event_id: str
    event_type: EventType
    source: str
    payload: Dict[str, Any]
    priority: EventPriority = EventPriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'source': self.source,
            'payload': self.payload,
            'priority': self.priority.value,
            'timestamp': self.timestamp.isoformat(),
            'correlation_id': self.correlation_id,
            'causation_id': self.causation_id,
            'metadata': self.metadata
        }

@dataclass
class Subscription:
    """Event subscription"""
    subscription_id: str
    consumer_id: str
    event_types: List[EventType]
    filter_expr: Optional[str] = None
    callback: Optional[Callable] = None
    active: bool = True

################################################################################
# Event Store (Persistent Storage)
################################################################################

class EventStore:
    """Persistent event storage with replay capability"""
    
    def __init__(self, db_path: str = EVENT_DB):
        self.db_path = db_path
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """Initialize database"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.conn.cursor()
        
        # Events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                source TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                priority INTEGER NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                correlation_id TEXT,
                causation_id TEXT,
                metadata_json TEXT,
                processed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Event streams (topics)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_streams (
                stream_id TEXT PRIMARY KEY,
                stream_name TEXT NOT NULL UNIQUE,
                description TEXT,
                partition_count INTEGER DEFAULT 3,
                replication_factor INTEGER DEFAULT 2,
                retention_days INTEGER DEFAULT 30,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Subscriptions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                subscription_id TEXT PRIMARY KEY,
                consumer_id TEXT NOT NULL,
                event_types_json TEXT NOT NULL,
                filter_expr TEXT,
                offset_position INTEGER DEFAULT 0,
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Consumer offsets (for event replay)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consumer_offsets (
                consumer_id TEXT NOT NULL,
                stream_name TEXT NOT NULL,
                partition INTEGER NOT NULL,
                offset INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (consumer_id, stream_name, partition)
            )
        ''')
        
        # Dead letter queue
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dead_letter_queue (
                dlq_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL,
                event_json TEXT NOT NULL,
                error_message TEXT NOT NULL,
                retry_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_retry TIMESTAMP
            )
        ''')
        
        # Indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type, timestamp DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_correlation ON events(correlation_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_offsets ON consumer_offsets(consumer_id, stream_name)')
        
        self.conn.commit()
        logger.info(f"Event store initialized: {db_path}")
    
    def append_event(self, event: Event):
        """Append event to store"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO events 
            (event_id, event_type, source, payload_json, priority, timestamp,
             correlation_id, causation_id, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event.event_id,
            event.event_type.value,
            event.source,
            json.dumps(event.payload),
            event.priority.value,
            event.timestamp.isoformat(),
            event.correlation_id,
            event.causation_id,
            json.dumps(event.metadata)
        ))
        self.conn.commit()
    
    def get_events(self, start_time: datetime, end_time: datetime,
                   event_types: Optional[List[EventType]] = None,
                   limit: int = 1000) -> List[Event]:
        """Get events for replay"""
        cursor = self.conn.cursor()
        
        query = '''
            SELECT event_id, event_type, source, payload_json, priority,
                   timestamp, correlation_id, causation_id, metadata_json
            FROM events
            WHERE timestamp BETWEEN ? AND ?
        '''
        params = [start_time.isoformat(), end_time.isoformat()]
        
        if event_types:
            placeholders = ','.join('?' * len(event_types))
            query += f' AND event_type IN ({placeholders})'
            params.extend([et.value for et in event_types])
        
        query += ' ORDER BY timestamp ASC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        
        events = []
        for row in cursor.fetchall():
            event = Event(
                event_id=row[0],
                event_type=EventType(row[1]),
                source=row[2],
                payload=json.loads(row[3]),
                priority=EventPriority(row[4]),
                timestamp=datetime.fromisoformat(row[5]),
                correlation_id=row[6],
                causation_id=row[7],
                metadata=json.loads(row[8]) if row[8] else {}
            )
            events.append(event)
        
        return events
    
    def save_offset(self, consumer_id: str, stream_name: str, 
                   partition: int, offset: int):
        """Save consumer offset"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO consumer_offsets 
            (consumer_id, stream_name, partition, offset, timestamp)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (consumer_id, stream_name, partition, offset))
        self.conn.commit()
    
    def get_offset(self, consumer_id: str, stream_name: str, 
                   partition: int) -> int:
        """Get consumer offset"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT offset FROM consumer_offsets
            WHERE consumer_id = ? AND stream_name = ? AND partition = ?
        ''', (consumer_id, stream_name, partition))
        
        result = cursor.fetchone()
        return result[0] if result else 0

################################################################################
# Kafka Event Bus
################################################################################

class KafkaEventBus:
    """Kafka-based event bus for high-throughput streaming"""
    
    def __init__(self, brokers: List[str]):
        self.brokers = brokers
        self.producer = None
        self.consumers: Dict[str, KafkaConsumer] = {}
        self.admin = None
        
        self._init_kafka()
    
    def _init_kafka(self):
        """Initialize Kafka"""
        try:
            self.admin = KafkaAdminClient(bootstrap_servers=self.brokers)
            
            self.producer = KafkaProducer(
                bootstrap_servers=self.brokers,
                value_serializer=lambda v: msgpack.packb(v, use_bin_type=True),
                compression_type='gzip',
                acks='all',
                retries=3
            )
            
            logger.info(f"Kafka initialized: {self.brokers}")
        except Exception as e:
            logger.error(f"Kafka initialization failed: {e}")
    
    def create_topic(self, topic_name: str, num_partitions: int = 3,
                    replication_factor: int = 2):
        """Create Kafka topic"""
        try:
            topic = NewTopic(
                name=topic_name,
                num_partitions=num_partitions,
                replication_factor=replication_factor
            )
            self.admin.create_topics([topic])
            logger.info(f"Topic created: {topic_name}")
        except Exception as e:
            logger.warning(f"Topic creation failed: {e}")
    
    async def publish(self, topic: str, event: Event):
        """Publish event to Kafka"""
        if not self.producer:
            return
        
        try:
            future = self.producer.send(
                topic,
                value=event.to_dict(),
                key=event.event_id.encode('utf-8')
            )
            
            # Wait for confirmation
            record_metadata = future.get(timeout=10)
            
            logger.debug(f"Published to {topic}: {event.event_id} "
                        f"(partition {record_metadata.partition}, offset {record_metadata.offset})")
        except Exception as e:
            logger.error(f"Kafka publish error: {e}")
    
    async def subscribe(self, topic: str, consumer_group: str,
                       callback: Callable):
        """Subscribe to Kafka topic"""
        try:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=self.brokers,
                group_id=consumer_group,
                value_deserializer=lambda v: msgpack.unpackb(v, raw=False),
                auto_offset_reset='earliest',
                enable_auto_commit=False
            )
            
            self.consumers[consumer_group] = consumer
            
            # Consume messages
            for message in consumer:
                event_dict = message.value
                event = Event(
                    event_id=event_dict['event_id'],
                    event_type=EventType(event_dict['event_type']),
                    source=event_dict['source'],
                    payload=event_dict['payload'],
                    priority=EventPriority(event_dict['priority']),
                    timestamp=datetime.fromisoformat(event_dict['timestamp']),
                    correlation_id=event_dict.get('correlation_id'),
                    causation_id=event_dict.get('causation_id'),
                    metadata=event_dict.get('metadata', {})
                )
                
                await callback(event)
                consumer.commit()
        
        except Exception as e:
            logger.error(f"Kafka subscription error: {e}")

################################################################################
# RabbitMQ Event Bus
################################################################################

class RabbitMQEventBus:
    """RabbitMQ-based event bus for reliable messaging"""
    
    def __init__(self, url: str):
        self.url = url
        self.connection = None
        self.channel = None
        self.exchanges: Dict[str, str] = {}
        
        self._init_rabbitmq()
    
    def _init_rabbitmq(self):
        """Initialize RabbitMQ"""
        try:
            self.connection = pika.BlockingConnection(
                pika.URLParameters(self.url)
            )
            self.channel = self.connection.channel()
            
            # Declare default exchange
            self.channel.exchange_declare(
                exchange='events',
                exchange_type='topic',
                durable=True
            )
            
            logger.info("RabbitMQ initialized")
        except Exception as e:
            logger.error(f"RabbitMQ initialization failed: {e}")
    
    async def publish(self, routing_key: str, event: Event):
        """Publish event to RabbitMQ"""
        if not self.channel:
            return
        
        try:
            self.channel.basic_publish(
                exchange='events',
                routing_key=routing_key,
                body=json.dumps(event.to_dict()),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent
                    priority=event.priority.value,
                    content_type='application/json',
                    timestamp=int(event.timestamp.timestamp())
                )
            )
            
            logger.debug(f"Published to RabbitMQ: {routing_key} - {event.event_id}")
        except Exception as e:
            logger.error(f"RabbitMQ publish error: {e}")
    
    async def subscribe(self, routing_pattern: str, callback: Callable):
        """Subscribe to RabbitMQ exchange"""
        if not self.channel:
            return
        
        try:
            # Declare queue
            queue_name = f"consumer_{uuid.uuid4().hex[:8]}"
            self.channel.queue_declare(queue=queue_name, durable=True)
            
            # Bind queue to exchange
            self.channel.queue_bind(
                exchange='events',
                queue=queue_name,
                routing_key=routing_pattern
            )
            
            # Consume messages
            def on_message(ch, method, properties, body):
                event_dict = json.loads(body)
                event = Event(
                    event_id=event_dict['event_id'],
                    event_type=EventType(event_dict['event_type']),
                    source=event_dict['source'],
                    payload=event_dict['payload'],
                    priority=EventPriority(event_dict['priority']),
                    timestamp=datetime.fromisoformat(event_dict['timestamp']),
                    correlation_id=event_dict.get('correlation_id'),
                    causation_id=event_dict.get('causation_id'),
                    metadata=event_dict.get('metadata', {})
                )
                
                asyncio.create_task(callback(event))
                ch.basic_ack(delivery_tag=method.delivery_tag)
            
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=on_message
            )
            
            self.channel.start_consuming()
        
        except Exception as e:
            logger.error(f"RabbitMQ subscription error: {e}")

################################################################################
# WebSocket Real-Time Streaming
################################################################################

class WebSocketServer:
    """WebSocket server for real-time event streaming to clients"""
    
    def __init__(self, port: int = WEBSOCKET_PORT):
        self.port = port
        self.clients: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.subscriptions: Dict[str, List[EventType]] = {}
    
    async def register(self, websocket: websockets.WebSocketServerProtocol):
        """Register new WebSocket client"""
        client_id = str(uuid.uuid4())
        self.clients[client_id] = websocket
        self.subscriptions[client_id] = []
        
        logger.info(f"WebSocket client registered: {client_id}")
        return client_id
    
    async def unregister(self, client_id: str):
        """Unregister WebSocket client"""
        if client_id in self.clients:
            del self.clients[client_id]
            del self.subscriptions[client_id]
            logger.info(f"WebSocket client unregistered: {client_id}")
    
    async def handle_client(self, websocket: websockets.WebSocketServerProtocol,
                          path: str):
        """Handle WebSocket client connection"""
        client_id = await self.register(websocket)
        
        try:
            # Send welcome message
            await websocket.send(json.dumps({
                'type': 'connection',
                'client_id': client_id,
                'message': 'Connected to Event Streaming Platform'
            }))
            
            # Handle incoming messages
            async for message in websocket:
                data = json.loads(message)
                
                if data['type'] == 'subscribe':
                    event_types = [EventType(et) for et in data['event_types']]
                    self.subscriptions[client_id] = event_types
                    
                    await websocket.send(json.dumps({
                        'type': 'subscribed',
                        'event_types': [et.value for et in event_types]
                    }))
                
                elif data['type'] == 'unsubscribe':
                    self.subscriptions[client_id] = []
                    await websocket.send(json.dumps({'type': 'unsubscribed'}))
        
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister(client_id)
    
    async def broadcast_event(self, event: Event):
        """Broadcast event to subscribed clients"""
        message = json.dumps({
            'type': 'event',
            'event': event.to_dict()
        })
        
        disconnected = []
        
        for client_id, websocket in self.clients.items():
            # Check if client subscribed to this event type
            if not self.subscriptions[client_id] or \
               event.event_type in self.subscriptions[client_id]:
                
                try:
                    await websocket.send(message)
                except:
                    disconnected.append(client_id)
        
        # Remove disconnected clients
        for client_id in disconnected:
            await self.unregister(client_id)
    
    async def start(self):
        """Start WebSocket server"""
        logger.info(f"Starting WebSocket server on port {self.port}")
        
        async with websockets.serve(self.handle_client, "0.0.0.0", self.port):
            await asyncio.Future()  # Run forever

################################################################################
# Event Streaming Platform
################################################################################

class EventStreamingPlatform:
    """Main event streaming orchestrator"""
    
    def __init__(self):
        self.event_store = EventStore()
        self.kafka_bus = KafkaEventBus(KAFKA_BROKERS)
        self.rabbitmq_bus = RabbitMQEventBus(RABBITMQ_URL)
        self.websocket_server = WebSocketServer()
        self.running = False
    
    async def publish_event(self, event: Event, targets: List[str] = ['kafka', 'rabbitmq', 'websocket']):
        """Publish event to multiple targets"""
        
        # Store event for replay
        self.event_store.append_event(event)
        
        # Publish to Kafka
        if 'kafka' in targets and self.kafka_bus.producer:
            topic = f"events.{event.event_type.value}"
            await self.kafka_bus.publish(topic, event)
        
        # Publish to RabbitMQ
        if 'rabbitmq' in targets and self.rabbitmq_bus.channel:
            routing_key = f"{event.event_type.value}.{event.source}"
            await self.rabbitmq_bus.publish(routing_key, event)
        
        # Broadcast to WebSocket clients
        if 'websocket' in targets:
            await self.websocket_server.broadcast_event(event)
        
        logger.info(f"Event published: {event.event_id} ({event.event_type.value})")
    
    async def replay_events(self, consumer_id: str, start_time: datetime,
                          end_time: datetime, event_types: Optional[List[EventType]] = None):
        """Replay historical events"""
        events = self.event_store.get_events(start_time, end_time, event_types, MAX_REPLAY_EVENTS)
        
        logger.info(f"Replaying {len(events)} events for {consumer_id}")
        
        for event in events:
            await self.publish_event(event, targets=['websocket'])
            await asyncio.sleep(0.01)  # Throttle replay
        
        logger.info(f"Replay completed: {len(events)} events")
    
    async def start(self):
        """Start event streaming platform"""
        logger.info("🌊 Starting Real-Time Event Streaming Platform v13.0")
        self.running = True
        
        # Create default Kafka topics
        topics = ['events.system', 'events.deployment', 'events.monitoring',
                 'events.security', 'events.cost', 'events.alert']
        
        for topic in topics:
            self.kafka_bus.create_topic(topic)
        
        # Start WebSocket server
        await self.websocket_server.start()
    
    def stop(self):
        """Stop platform"""
        logger.info("Stopping event streaming platform")
        self.running = False

################################################################################
# CLI Interface
################################################################################

def main():
    """Main entry point"""
    logger.info("Real-Time Event Streaming Platform v13.0")
    
    if '--test-publish' in sys.argv:
        # Test event publishing
        platform = EventStreamingPlatform()
        
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=EventType.SYSTEM,
            source='test',
            payload={'message': 'Test event', 'value': 42},
            priority=EventPriority.HIGH,
            correlation_id=str(uuid.uuid4())
        )
        
        asyncio.run(platform.publish_event(event))
        print(f"✅ Event published: {event.event_id}")
    
    elif '--replay' in sys.argv:
        # Replay events
        platform = EventStreamingPlatform()
        
        start = datetime.now() - timedelta(hours=24)
        end = datetime.now()
        
        asyncio.run(platform.replay_events('test-consumer', start, end))
    
    elif '--server' in sys.argv:
        # Start streaming server
        platform = EventStreamingPlatform()
        
        try:
            asyncio.run(platform.start())
        except KeyboardInterrupt:
            platform.stop()
    
    else:
        print("""
Real-Time Event Streaming Platform v13.0

Usage:
  --test-publish    Publish test event
  --replay          Replay last 24h events
  --server          Start streaming server

Examples:
  python3 realtime_event_streaming.py --test-publish
  python3 realtime_event_streaming.py --server
        """)

if __name__ == '__main__':
    main()
