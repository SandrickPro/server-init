#!/usr/bin/env python3
"""
Server Init - Iteration 99: Event Bus Platform
Платформа шины событий

Функционал:
- Event Publishing - публикация событий
- Event Subscription - подписка на события
- Event Routing - маршрутизация событий
- Dead Letter Queue - очередь недоставленных
- Event Replay - воспроизведение событий
- Schema Registry - реестр схем
- Event Sourcing - event sourcing
- CQRS Support - поддержка CQRS
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Union, Tuple
from enum import Enum
from collections import defaultdict
import uuid
import random
import hashlib


class EventPriority(Enum):
    """Приоритет события"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class EventStatus(Enum):
    """Статус события"""
    PENDING = "pending"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


class DeliveryMode(Enum):
    """Режим доставки"""
    AT_MOST_ONCE = "at_most_once"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"


class RoutingStrategy(Enum):
    """Стратегия маршрутизации"""
    BROADCAST = "broadcast"  # All subscribers
    ROUND_ROBIN = "round_robin"  # One subscriber
    RANDOM = "random"  # Random subscriber
    CONTENT_BASED = "content_based"  # Based on content


@dataclass
class EventSchema:
    """Схема события"""
    schema_id: str
    event_type: str = ""
    version: str = "1.0.0"
    
    # Schema definition
    fields: Dict[str, str] = field(default_factory=dict)  # name -> type
    required_fields: List[str] = field(default_factory=list)
    
    # Metadata
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Event:
    """Событие"""
    event_id: str
    event_type: str = ""
    
    # Payload
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    source: str = ""
    correlation_id: str = ""
    causation_id: str = ""
    
    # Headers
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Priority & TTL
    priority: EventPriority = EventPriority.NORMAL
    ttl_seconds: int = 0  # 0 = no expiry
    
    # Timing
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Schema
    schema_version: str = "1.0.0"
    
    # Status
    status: EventStatus = EventStatus.PENDING
    
    # Delivery tracking
    delivery_attempts: int = 0
    last_delivery_attempt: Optional[datetime] = None
    delivered_to: List[str] = field(default_factory=list)


@dataclass
class Subscription:
    """Подписка"""
    subscription_id: str
    subscriber_id: str = ""
    
    # Topic/Event type
    event_types: List[str] = field(default_factory=list)  # empty = all
    
    # Filters
    filters: Dict[str, Any] = field(default_factory=dict)
    
    # Handler
    handler: Optional[Callable] = None
    handler_url: str = ""  # For webhook subscriptions
    
    # Settings
    delivery_mode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE
    max_retries: int = 3
    retry_delay_seconds: int = 5
    
    # Batch settings
    batch_size: int = 1
    batch_timeout_ms: int = 100
    
    # Status
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    
    # Stats
    events_received: int = 0
    events_processed: int = 0
    events_failed: int = 0


@dataclass
class Topic:
    """Топик"""
    topic_id: str
    name: str = ""
    
    # Settings
    routing_strategy: RoutingStrategy = RoutingStrategy.BROADCAST
    retention_hours: int = 24
    
    # Schema
    schema_id: str = ""
    
    # Partitions
    partition_count: int = 1
    
    # Stats
    total_events: int = 0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DeadLetterEntry:
    """Запись в dead letter queue"""
    entry_id: str
    event: Event = field(default_factory=Event)
    subscription_id: str = ""
    
    # Error info
    error_message: str = ""
    error_count: int = 0
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


@dataclass
class EventLog:
    """Лог событий для replay"""
    log_id: str
    topic: str = ""
    partition: int = 0
    
    # Events
    events: List[Event] = field(default_factory=list)
    
    # Offsets
    start_offset: int = 0
    end_offset: int = 0


class SchemaRegistry:
    """Реестр схем"""
    
    def __init__(self):
        self.schemas: Dict[str, Dict[str, EventSchema]] = defaultdict(dict)
        
    def register(self, event_type: str, fields: Dict[str, str],
                  required_fields: List[str] = None,
                  version: str = "1.0.0") -> EventSchema:
        """Регистрация схемы"""
        schema = EventSchema(
            schema_id=f"schema_{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            version=version,
            fields=fields,
            required_fields=required_fields or []
        )
        self.schemas[event_type][version] = schema
        return schema
        
    def get_schema(self, event_type: str,
                    version: str = None) -> Optional[EventSchema]:
        """Получение схемы"""
        type_schemas = self.schemas.get(event_type, {})
        
        if not type_schemas:
            return None
            
        if version:
            return type_schemas.get(version)
            
        # Return latest version
        latest_version = max(type_schemas.keys())
        return type_schemas.get(latest_version)
        
    def validate(self, event: Event) -> Tuple[bool, str]:
        """Валидация события по схеме"""
        schema = self.get_schema(event.event_type, event.schema_version)
        
        if not schema:
            return True, ""  # No schema = no validation
            
        # Check required fields
        for field_name in schema.required_fields:
            if field_name not in event.payload:
                return False, f"Missing required field: {field_name}"
                
        return True, ""


class EventRouter:
    """Маршрутизатор событий"""
    
    def __init__(self):
        self.counters: Dict[str, int] = defaultdict(int)
        
    def route(self, event: Event, subscriptions: List[Subscription],
               strategy: RoutingStrategy) -> List[Subscription]:
        """Маршрутизация события"""
        # Filter by event type
        matching = []
        for sub in subscriptions:
            if not sub.active:
                continue
                
            # Check event type match
            if sub.event_types and event.event_type not in sub.event_types:
                continue
                
            # Check filters
            if sub.filters and not self._match_filters(event, sub.filters):
                continue
                
            matching.append(sub)
            
        if not matching:
            return []
            
        if strategy == RoutingStrategy.BROADCAST:
            return matching
            
        if strategy == RoutingStrategy.ROUND_ROBIN:
            key = event.event_type
            idx = self.counters[key] % len(matching)
            self.counters[key] += 1
            return [matching[idx]]
            
        if strategy == RoutingStrategy.RANDOM:
            return [random.choice(matching)]
            
        return matching
        
    def _match_filters(self, event: Event,
                        filters: Dict[str, Any]) -> bool:
        """Проверка фильтров"""
        for key, value in filters.items():
            event_value = event.payload.get(key)
            
            if isinstance(value, dict):
                # Operators
                for op, op_value in value.items():
                    if op == "$eq" and event_value != op_value:
                        return False
                    elif op == "$ne" and event_value == op_value:
                        return False
                    elif op == "$gt" and not (event_value and event_value > op_value):
                        return False
                    elif op == "$lt" and not (event_value and event_value < op_value):
                        return False
                    elif op == "$in" and event_value not in op_value:
                        return False
            else:
                if event_value != value:
                    return False
                    
        return True


class DeadLetterQueue:
    """Dead Letter Queue"""
    
    def __init__(self, retention_hours: int = 168):  # 7 days
        self.entries: Dict[str, DeadLetterEntry] = {}
        self.retention_hours = retention_hours
        
    def add(self, event: Event, subscription_id: str,
             error_message: str) -> DeadLetterEntry:
        """Добавление в DLQ"""
        entry = DeadLetterEntry(
            entry_id=f"dlq_{uuid.uuid4().hex[:8]}",
            event=event,
            subscription_id=subscription_id,
            error_message=error_message,
            expires_at=datetime.now() + timedelta(hours=self.retention_hours)
        )
        self.entries[entry.entry_id] = entry
        return entry
        
    def get_entries(self, subscription_id: str = None,
                     event_type: str = None) -> List[DeadLetterEntry]:
        """Получение записей"""
        entries = list(self.entries.values())
        
        if subscription_id:
            entries = [e for e in entries if e.subscription_id == subscription_id]
            
        if event_type:
            entries = [e for e in entries if e.event.event_type == event_type]
            
        return entries
        
    def retry(self, entry_id: str) -> Optional[Event]:
        """Повторная попытка"""
        entry = self.entries.get(entry_id)
        if not entry:
            return None
            
        event = entry.event
        event.status = EventStatus.PENDING
        event.delivery_attempts = 0
        
        del self.entries[entry_id]
        return event
        
    def cleanup(self) -> int:
        """Очистка истекших записей"""
        now = datetime.now()
        expired = [
            eid for eid, entry in self.entries.items()
            if entry.expires_at and entry.expires_at < now
        ]
        
        for eid in expired:
            del self.entries[eid]
            
        return len(expired)


class EventStore:
    """Хранилище событий для event sourcing"""
    
    def __init__(self):
        self.streams: Dict[str, List[Event]] = defaultdict(list)
        self.snapshots: Dict[str, Tuple[int, Any]] = {}  # stream -> (version, state)
        
    def append(self, stream_id: str, event: Event) -> int:
        """Добавление события в поток"""
        self.streams[stream_id].append(event)
        return len(self.streams[stream_id]) - 1  # Return position
        
    def read(self, stream_id: str, from_position: int = 0,
              to_position: int = None) -> List[Event]:
        """Чтение событий из потока"""
        events = self.streams.get(stream_id, [])
        
        if to_position is None:
            return events[from_position:]
            
        return events[from_position:to_position + 1]
        
    def read_all(self, event_type: str = None,
                  from_time: datetime = None) -> List[Event]:
        """Чтение всех событий"""
        all_events = []
        
        for stream_events in self.streams.values():
            all_events.extend(stream_events)
            
        # Filter
        if event_type:
            all_events = [e for e in all_events if e.event_type == event_type]
            
        if from_time:
            all_events = [e for e in all_events if e.timestamp >= from_time]
            
        # Sort by timestamp
        all_events.sort(key=lambda e: e.timestamp)
        return all_events
        
    def save_snapshot(self, stream_id: str, version: int, state: Any) -> None:
        """Сохранение снапшота"""
        self.snapshots[stream_id] = (version, state)
        
    def get_snapshot(self, stream_id: str) -> Optional[Tuple[int, Any]]:
        """Получение снапшота"""
        return self.snapshots.get(stream_id)


class EventBusPlatform:
    """Платформа шины событий"""
    
    def __init__(self):
        self.topics: Dict[str, Topic] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        
        self.schema_registry = SchemaRegistry()
        self.router = EventRouter()
        self.dlq = DeadLetterQueue()
        self.event_store = EventStore()
        
        # Queues per topic
        self.queues: Dict[str, List[Event]] = defaultdict(list)
        
        # Metrics
        self.metrics = {
            "events_published": 0,
            "events_delivered": 0,
            "events_failed": 0,
            "dead_letter_count": 0,
            "total_subscriptions": 0
        }
        
    def create_topic(self, name: str, **kwargs) -> Topic:
        """Создание топика"""
        topic = Topic(
            topic_id=f"topic_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        self.topics[name] = topic
        return topic
        
    def subscribe(self, subscriber_id: str,
                   event_types: List[str] = None,
                   handler: Callable = None,
                   **kwargs) -> Subscription:
        """Подписка на события"""
        subscription = Subscription(
            subscription_id=f"sub_{uuid.uuid4().hex[:8]}",
            subscriber_id=subscriber_id,
            event_types=event_types or [],
            handler=handler,
            **kwargs
        )
        self.subscriptions[subscription.subscription_id] = subscription
        self.metrics["total_subscriptions"] = len(self.subscriptions)
        return subscription
        
    def unsubscribe(self, subscription_id: str) -> bool:
        """Отписка"""
        if subscription_id in self.subscriptions:
            del self.subscriptions[subscription_id]
            self.metrics["total_subscriptions"] = len(self.subscriptions)
            return True
        return False
        
    async def publish(self, event_type: str, payload: Dict[str, Any],
                       topic: str = None, **kwargs) -> Event:
        """Публикация события"""
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            payload=payload,
            **kwargs
        )
        
        # Validate schema
        valid, error = self.schema_registry.validate(event)
        if not valid:
            raise ValueError(f"Schema validation failed: {error}")
            
        # Store in event store
        stream_id = topic or event_type
        self.event_store.append(stream_id, event)
        
        # Add to topic queue
        if topic:
            self.queues[topic].append(event)
            topic_obj = self.topics.get(topic)
            if topic_obj:
                topic_obj.total_events += 1
                
        self.metrics["events_published"] += 1
        
        # Deliver
        await self._deliver_event(event, topic)
        
        return event
        
    async def _deliver_event(self, event: Event, topic: str = None) -> None:
        """Доставка события подписчикам"""
        topic_obj = self.topics.get(topic) if topic else None
        strategy = topic_obj.routing_strategy if topic_obj else RoutingStrategy.BROADCAST
        
        # Route to subscriptions
        targets = self.router.route(
            event,
            list(self.subscriptions.values()),
            strategy
        )
        
        for subscription in targets:
            await self._deliver_to_subscription(event, subscription)
            
    async def _deliver_to_subscription(self, event: Event,
                                         subscription: Subscription) -> bool:
        """Доставка события подписчику"""
        event.delivery_attempts += 1
        event.last_delivery_attempt = datetime.now()
        
        success = False
        error_message = ""
        
        try:
            if subscription.handler:
                # Call handler
                if asyncio.iscoroutinefunction(subscription.handler):
                    await subscription.handler(event)
                else:
                    subscription.handler(event)
                success = True
                
            elif subscription.handler_url:
                # Webhook delivery (simulated)
                await asyncio.sleep(0.01)
                success = random.random() > 0.05  # 95% success rate
                
                if not success:
                    error_message = "Webhook delivery failed"
            else:
                success = True  # No handler = success (fire and forget)
                
        except Exception as e:
            error_message = str(e)
            
        # Update stats
        subscription.events_received += 1
        
        if success:
            subscription.events_processed += 1
            event.status = EventStatus.DELIVERED
            event.delivered_to.append(subscription.subscription_id)
            self.metrics["events_delivered"] += 1
        else:
            subscription.events_failed += 1
            
            # Retry logic
            if event.delivery_attempts < subscription.max_retries:
                await asyncio.sleep(subscription.retry_delay_seconds * 0.01)  # Scaled for demo
                return await self._deliver_to_subscription(event, subscription)
            else:
                # Move to DLQ
                event.status = EventStatus.DEAD_LETTER
                self.dlq.add(event, subscription.subscription_id, error_message)
                self.metrics["events_failed"] += 1
                self.metrics["dead_letter_count"] += 1
                
        return success
        
    async def replay(self, event_type: str = None,
                      from_time: datetime = None,
                      subscription_id: str = None) -> int:
        """Воспроизведение событий"""
        events = self.event_store.read_all(event_type, from_time)
        
        replayed = 0
        for event in events:
            event.status = EventStatus.PENDING
            event.delivery_attempts = 0
            
            if subscription_id:
                subscription = self.subscriptions.get(subscription_id)
                if subscription:
                    await self._deliver_to_subscription(event, subscription)
                    replayed += 1
            else:
                await self._deliver_event(event)
                replayed += 1
                
        return replayed
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        return {
            **self.metrics,
            "topics": len(self.topics),
            "subscriptions": len(self.subscriptions),
            "schemas": sum(len(v) for v in self.schema_registry.schemas.values()),
            "event_streams": len(self.event_store.streams),
            "dlq_entries": len(self.dlq.entries)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 99: Event Bus Platform")
    print("=" * 60)
    
    async def demo():
        bus = EventBusPlatform()
        print("✓ Event Bus Platform created")
        
        # Register schemas
        print("\n📋 Registering Event Schemas...")
        
        bus.schema_registry.register(
            "user.created",
            fields={"user_id": "string", "email": "string", "name": "string"},
            required_fields=["user_id", "email"]
        )
        
        bus.schema_registry.register(
            "order.placed",
            fields={"order_id": "string", "user_id": "string", "total": "number", "items": "array"},
            required_fields=["order_id", "user_id", "total"]
        )
        
        bus.schema_registry.register(
            "payment.processed",
            fields={"payment_id": "string", "order_id": "string", "amount": "number", "status": "string"},
            required_fields=["payment_id", "order_id", "amount"]
        )
        
        print("  ✓ user.created")
        print("  ✓ order.placed")
        print("  ✓ payment.processed")
        
        # Create topics
        print("\n📍 Creating Topics...")
        
        bus.create_topic(
            "users",
            routing_strategy=RoutingStrategy.BROADCAST,
            retention_hours=72
        )
        
        bus.create_topic(
            "orders",
            routing_strategy=RoutingStrategy.BROADCAST,
            retention_hours=168
        )
        
        bus.create_topic(
            "payments",
            routing_strategy=RoutingStrategy.ROUND_ROBIN,
            retention_hours=168
        )
        
        print("  ✓ users (broadcast)")
        print("  ✓ orders (broadcast)")
        print("  ✓ payments (round-robin)")
        
        # Event handlers
        received_events = []
        
        async def user_handler(event: Event):
            received_events.append(("user_handler", event))
            
        async def order_handler(event: Event):
            received_events.append(("order_handler", event))
            
        async def notification_handler(event: Event):
            received_events.append(("notification_handler", event))
            
        async def analytics_handler(event: Event):
            received_events.append(("analytics_handler", event))
            
        # Subscribe
        print("\n📬 Creating Subscriptions...")
        
        sub_user = bus.subscribe(
            "user-service",
            event_types=["user.created", "user.updated"],
            handler=user_handler,
            delivery_mode=DeliveryMode.AT_LEAST_ONCE
        )
        print(f"  ✓ user-service: user events")
        
        sub_order = bus.subscribe(
            "order-service",
            event_types=["order.placed", "order.updated"],
            handler=order_handler
        )
        print(f"  ✓ order-service: order events")
        
        sub_notification = bus.subscribe(
            "notification-service",
            event_types=["user.created", "order.placed", "payment.processed"],
            handler=notification_handler
        )
        print(f"  ✓ notification-service: multiple events")
        
        sub_analytics = bus.subscribe(
            "analytics-service",
            handler=analytics_handler  # All events
        )
        print(f"  ✓ analytics-service: all events")
        
        # Content-based subscription
        sub_high_value = bus.subscribe(
            "vip-service",
            event_types=["order.placed"],
            filters={"total": {"$gt": 1000}},
            handler=lambda e: received_events.append(("vip_handler", e))
        )
        print(f"  ✓ vip-service: high-value orders (>$1000)")
        
        # Publish events
        print("\n📤 Publishing Events...")
        
        # User created
        user_event = await bus.publish(
            "user.created",
            {
                "user_id": "user_123",
                "email": "john@example.com",
                "name": "John Doe"
            },
            topic="users",
            source="user-service"
        )
        print(f"  ✓ user.created: {user_event.event_id}")
        
        # Order placed (regular)
        order_event1 = await bus.publish(
            "order.placed",
            {
                "order_id": "order_456",
                "user_id": "user_123",
                "total": 150.00,
                "items": [{"product": "Widget", "qty": 3}]
            },
            topic="orders",
            source="order-service",
            correlation_id=user_event.event_id
        )
        print(f"  ✓ order.placed: {order_event1.event_id} (total: $150)")
        
        # Order placed (high value - triggers VIP handler)
        order_event2 = await bus.publish(
            "order.placed",
            {
                "order_id": "order_789",
                "user_id": "user_456",
                "total": 2500.00,
                "items": [{"product": "Premium Package", "qty": 1}]
            },
            topic="orders",
            source="order-service"
        )
        print(f"  ✓ order.placed: {order_event2.event_id} (total: $2500 - VIP)")
        
        # Payment processed
        payment_event = await bus.publish(
            "payment.processed",
            {
                "payment_id": "pay_001",
                "order_id": "order_456",
                "amount": 150.00,
                "status": "completed"
            },
            topic="payments",
            source="payment-service",
            causation_id=order_event1.event_id
        )
        print(f"  ✓ payment.processed: {payment_event.event_id}")
        
        # Bulk events
        print("\n  Publishing bulk events...")
        for i in range(10):
            await bus.publish(
                random.choice(["user.created", "order.placed"]),
                {
                    "user_id": f"user_{1000+i}",
                    "email": f"user{i}@example.com",
                    "order_id": f"order_{2000+i}",
                    "total": random.uniform(50, 500)
                },
                source="bulk-import"
            )
            
        print(f"  ✓ Published 10 bulk events")
        
        # Event delivery summary
        print("\n📨 Event Delivery Summary:")
        
        handlers_count = defaultdict(int)
        for handler_name, event in received_events:
            handlers_count[handler_name] += 1
            
        for handler, count in handlers_count.items():
            print(f"  {handler}: {count} events received")
            
        # Subscription stats
        print("\n📊 Subscription Statistics:")
        
        for sub_id, sub in bus.subscriptions.items():
            print(f"\n  {sub.subscriber_id}:")
            print(f"    Events received: {sub.events_received}")
            print(f"    Events processed: {sub.events_processed}")
            print(f"    Events failed: {sub.events_failed}")
            
        # Event store
        print("\n💾 Event Store:")
        
        for stream_id, events in bus.event_store.streams.items():
            print(f"  Stream '{stream_id}': {len(events)} events")
            
        # Read events from store
        print("\n  Recent order events:")
        order_events = bus.event_store.read_all("order.placed")
        for event in order_events[-3:]:
            print(f"    • {event.event_id}: ${event.payload.get('total', 0):.2f}")
            
        # Dead Letter Queue
        print("\n☠️ Dead Letter Queue:")
        print(f"  Entries: {len(bus.dlq.entries)}")
        
        if bus.dlq.entries:
            for entry_id, entry in list(bus.dlq.entries.items())[:3]:
                print(f"    • {entry.event.event_type}: {entry.error_message}")
                
        # Event replay demo
        print("\n🔄 Event Replay Demo:")
        
        # Create new subscription
        replay_received = []
        replay_sub = bus.subscribe(
            "replay-consumer",
            event_types=["order.placed"],
            handler=lambda e: replay_received.append(e)
        )
        
        # Replay order events
        replayed = await bus.replay(
            event_type="order.placed",
            subscription_id=replay_sub.subscription_id
        )
        
        print(f"  Replayed {replayed} order events to replay-consumer")
        print(f"  Events received: {len(replay_received)}")
        
        # Topic statistics
        print("\n📍 Topic Statistics:")
        
        for topic_name, topic in bus.topics.items():
            print(f"\n  {topic_name}:")
            print(f"    Events: {topic.total_events}")
            print(f"    Strategy: {topic.routing_strategy.value}")
            print(f"    Retention: {topic.retention_hours}h")
            
        # Overall statistics
        print("\n📈 Platform Statistics:")
        
        stats = bus.get_statistics()
        
        print(f"\n  Topics: {stats['topics']}")
        print(f"  Subscriptions: {stats['subscriptions']}")
        print(f"  Schemas: {stats['schemas']}")
        print(f"\n  Events Published: {stats['events_published']}")
        print(f"  Events Delivered: {stats['events_delivered']}")
        print(f"  Events Failed: {stats['events_failed']}")
        print(f"\n  Event Streams: {stats['event_streams']}")
        print(f"  DLQ Entries: {stats['dlq_entries']}")
        
        # Dashboard
        print("\n📋 Event Bus Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │                  Event Bus Overview                         │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Topics:          {stats['topics']:>6}                                │")
        print(f"  │ Subscriptions:   {stats['subscriptions']:>6}                                │")
        print(f"  │ Schemas:         {stats['schemas']:>6}                                │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Published:       {stats['events_published']:>6}                                │")
        print(f"  │ Delivered:       {stats['events_delivered']:>6}                                │")
        print(f"  │ Failed:          {stats['events_failed']:>6}                                │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Event Streams:   {stats['event_streams']:>6}                                │")
        print(f"  │ DLQ Entries:     {stats['dlq_entries']:>6}                                │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Event Bus Platform initialized!")
    print("=" * 60)
