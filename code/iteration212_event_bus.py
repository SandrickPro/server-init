#!/usr/bin/env python3
"""
Server Init - Iteration 212: Event Bus Platform
Платформа шины событий

Функционал:
- Event Publishing - публикация событий
- Event Subscription - подписка на события
- Topic Management - управление топиками
- Event Routing - маршрутизация событий
- Dead Letter Queue - очередь недоставленных сообщений
- Event Replay - повтор событий
- Schema Registry - реестр схем
- Event Analytics - аналитика событий
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
import uuid
import json


class EventPriority(Enum):
    """Приоритет события"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class EventStatus(Enum):
    """Статус события"""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    DEAD_LETTERED = "dead_lettered"
    REPLAYED = "replayed"


class SubscriptionStatus(Enum):
    """Статус подписки"""
    ACTIVE = "active"
    PAUSED = "paused"
    INACTIVE = "inactive"


class DeliveryGuarantee(Enum):
    """Гарантия доставки"""
    AT_MOST_ONCE = "at_most_once"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"


@dataclass
class Event:
    """Событие"""
    event_id: str
    event_type: str = ""
    
    # Topic
    topic: str = ""
    
    # Payload
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    source: str = ""
    correlation_id: str = ""
    
    # Priority
    priority: EventPriority = EventPriority.NORMAL
    
    # Status
    status: EventStatus = EventStatus.PENDING
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)
    delivered_at: Optional[datetime] = None
    
    # Delivery
    delivery_attempts: int = 0
    max_attempts: int = 3
    
    # Headers
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class Topic:
    """Топик"""
    topic_id: str
    name: str = ""
    
    # Config
    partitions: int = 1
    replication_factor: int = 1
    
    # Retention
    retention_hours: int = 168  # 7 days
    
    # Schema
    schema_id: Optional[str] = None
    
    # Stats
    message_count: int = 0
    bytes_in: int = 0


@dataclass
class Subscription:
    """Подписка"""
    subscription_id: str
    name: str = ""
    
    # Topic
    topic_id: str = ""
    
    # Subscriber
    subscriber_id: str = ""
    
    # Config
    delivery_guarantee: DeliveryGuarantee = DeliveryGuarantee.AT_LEAST_ONCE
    
    # Filter
    filter_expression: Optional[str] = None
    
    # Status
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    
    # Stats
    messages_received: int = 0
    messages_acknowledged: int = 0
    
    # Position
    offset: int = 0


@dataclass
class DeadLetterEntry:
    """Запись в DLQ"""
    entry_id: str
    event_id: str = ""
    
    # Reason
    reason: str = ""
    
    # Original
    original_topic: str = ""
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)
    
    # Retry
    retry_count: int = 0
    last_retry: Optional[datetime] = None


@dataclass
class EventSchema:
    """Схема события"""
    schema_id: str
    name: str = ""
    
    # Version
    version: int = 1
    
    # Schema
    schema_definition: Dict[str, Any] = field(default_factory=dict)
    
    # Compatibility
    compatibility: str = "backward"  # backward, forward, full
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)


class TopicManager:
    """Менеджер топиков"""
    
    def __init__(self):
        self.topics: Dict[str, Topic] = {}
        
    def create_topic(self, name: str, partitions: int = 1,
                    retention_hours: int = 168) -> Topic:
        """Создание топика"""
        topic = Topic(
            topic_id=f"topic_{uuid.uuid4().hex[:8]}",
            name=name,
            partitions=partitions,
            retention_hours=retention_hours
        )
        self.topics[topic.topic_id] = topic
        return topic
        
    def get_by_name(self, name: str) -> Optional[Topic]:
        """Получение топика по имени"""
        for topic in self.topics.values():
            if topic.name == name:
                return topic
        return None


class EventPublisher:
    """Издатель событий"""
    
    def __init__(self, topic_manager: TopicManager):
        self.topic_manager = topic_manager
        self.events: Dict[str, Event] = {}
        
    async def publish(self, topic_name: str, event_type: str,
                     payload: Dict[str, Any], source: str = "",
                     priority: EventPriority = EventPriority.NORMAL,
                     correlation_id: str = "") -> Event:
        """Публикация события"""
        topic = self.topic_manager.get_by_name(topic_name)
        
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            topic=topic_name,
            payload=payload,
            source=source,
            priority=priority,
            correlation_id=correlation_id or f"corr_{uuid.uuid4().hex[:8]}"
        )
        
        self.events[event.event_id] = event
        
        if topic:
            topic.message_count += 1
            topic.bytes_in += len(json.dumps(payload))
            
        return event


class SubscriptionManager:
    """Менеджер подписок"""
    
    def __init__(self):
        self.subscriptions: Dict[str, Subscription] = {}
        
    def subscribe(self, topic_id: str, subscriber_id: str,
                 name: str = "", delivery_guarantee: DeliveryGuarantee = DeliveryGuarantee.AT_LEAST_ONCE,
                 filter_expression: Optional[str] = None) -> Subscription:
        """Создание подписки"""
        subscription = Subscription(
            subscription_id=f"sub_{uuid.uuid4().hex[:8]}",
            name=name or f"subscription_{subscriber_id}",
            topic_id=topic_id,
            subscriber_id=subscriber_id,
            delivery_guarantee=delivery_guarantee,
            filter_expression=filter_expression
        )
        self.subscriptions[subscription.subscription_id] = subscription
        return subscription
        
    def pause(self, subscription_id: str) -> bool:
        """Приостановка подписки"""
        sub = self.subscriptions.get(subscription_id)
        if not sub:
            return False
        sub.status = SubscriptionStatus.PAUSED
        return True
        
    def resume(self, subscription_id: str) -> bool:
        """Возобновление подписки"""
        sub = self.subscriptions.get(subscription_id)
        if not sub:
            return False
        sub.status = SubscriptionStatus.ACTIVE
        return True


class DeadLetterQueue:
    """Очередь недоставленных сообщений"""
    
    def __init__(self):
        self.entries: Dict[str, DeadLetterEntry] = {}
        
    def add(self, event: Event, reason: str) -> DeadLetterEntry:
        """Добавление в DLQ"""
        entry = DeadLetterEntry(
            entry_id=f"dlq_{uuid.uuid4().hex[:8]}",
            event_id=event.event_id,
            reason=reason,
            original_topic=event.topic
        )
        self.entries[entry.entry_id] = entry
        event.status = EventStatus.DEAD_LETTERED
        return entry
        
    async def retry(self, entry_id: str) -> bool:
        """Повторная попытка"""
        entry = self.entries.get(entry_id)
        if not entry:
            return False
            
        entry.retry_count += 1
        entry.last_retry = datetime.now()
        
        await asyncio.sleep(0.05)
        
        success = random.random() > 0.3
        if success:
            del self.entries[entry_id]
            
        return success


class SchemaRegistry:
    """Реестр схем"""
    
    def __init__(self):
        self.schemas: Dict[str, EventSchema] = {}
        
    def register_schema(self, name: str, schema_definition: Dict[str, Any],
                       compatibility: str = "backward") -> EventSchema:
        """Регистрация схемы"""
        # Get next version
        existing = [s for s in self.schemas.values() if s.name == name]
        version = max((s.version for s in existing), default=0) + 1
        
        schema = EventSchema(
            schema_id=f"schema_{uuid.uuid4().hex[:8]}",
            name=name,
            version=version,
            schema_definition=schema_definition,
            compatibility=compatibility
        )
        self.schemas[schema.schema_id] = schema
        return schema
        
    def validate(self, schema_id: str, payload: Dict[str, Any]) -> bool:
        """Валидация данных по схеме"""
        schema = self.schemas.get(schema_id)
        if not schema:
            return True  # No schema, allow all
            
        # Simplified validation
        required = schema.schema_definition.get("required", [])
        return all(field in payload for field in required)


class EventBusPlatform:
    """Платформа шины событий"""
    
    def __init__(self):
        self.topic_manager = TopicManager()
        self.publisher = EventPublisher(self.topic_manager)
        self.subscriptions = SubscriptionManager()
        self.dlq = DeadLetterQueue()
        self.schema_registry = SchemaRegistry()
        self.delivered_events: List[Event] = []
        
    async def deliver_events(self, topic_name: str) -> int:
        """Доставка событий подписчикам"""
        topic = self.topic_manager.get_by_name(topic_name)
        if not topic:
            return 0
            
        # Get events for topic
        events = [e for e in self.publisher.events.values()
                 if e.topic == topic_name and e.status == EventStatus.PENDING]
        
        # Get active subscriptions
        subs = [s for s in self.subscriptions.subscriptions.values()
               if s.topic_id == topic.topic_id and s.status == SubscriptionStatus.ACTIVE]
        
        delivered = 0
        
        for event in events:
            for sub in subs:
                # Simulate delivery
                await asyncio.sleep(0.01)
                
                event.delivery_attempts += 1
                success = random.random() > 0.1
                
                if success:
                    event.status = EventStatus.DELIVERED
                    event.delivered_at = datetime.now()
                    sub.messages_received += 1
                    sub.messages_acknowledged += 1
                    delivered += 1
                    self.delivered_events.append(event)
                elif event.delivery_attempts >= event.max_attempts:
                    self.dlq.add(event, "Max delivery attempts exceeded")
                    
        return delivered
        
    async def replay_events(self, topic_name: str, from_time: datetime,
                           to_time: datetime) -> List[Event]:
        """Повтор событий за период"""
        events = [e for e in self.publisher.events.values()
                 if e.topic == topic_name and from_time <= e.created_at <= to_time]
        
        replayed = []
        for event in events:
            event.status = EventStatus.REPLAYED
            replayed.append(event)
            
        return replayed
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        all_events = list(self.publisher.events.values())
        
        return {
            "total_topics": len(self.topic_manager.topics),
            "total_subscriptions": len(self.subscriptions.subscriptions),
            "active_subscriptions": len([s for s in self.subscriptions.subscriptions.values()
                                        if s.status == SubscriptionStatus.ACTIVE]),
            "total_events": len(all_events),
            "delivered_events": len([e for e in all_events if e.status == EventStatus.DELIVERED]),
            "failed_events": len([e for e in all_events if e.status == EventStatus.FAILED]),
            "dlq_entries": len(self.dlq.entries),
            "schemas_registered": len(self.schema_registry.schemas)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 212: Event Bus Platform")
    print("=" * 60)
    
    platform = EventBusPlatform()
    print("✓ Event Bus Platform created")
    
    # Create topics
    print("\n📬 Creating Topics...")
    
    topics_config = [
        ("user.events", 4, 168),
        ("order.events", 8, 336),
        ("payment.events", 4, 720),
        ("notification.events", 2, 24),
        ("analytics.events", 16, 168),
    ]
    
    for name, partitions, retention in topics_config:
        topic = platform.topic_manager.create_topic(name, partitions, retention)
        print(f"  ✓ {name} ({partitions} partitions, {retention}h retention)")
        
    # Register schemas
    print("\n📋 Registering Event Schemas...")
    
    schemas_config = [
        ("UserCreated", {"required": ["user_id", "email", "timestamp"]}),
        ("OrderPlaced", {"required": ["order_id", "user_id", "items", "total"]}),
        ("PaymentProcessed", {"required": ["payment_id", "order_id", "amount", "status"]}),
    ]
    
    for name, definition in schemas_config:
        schema = platform.schema_registry.register_schema(name, definition)
        print(f"  ✓ {name} v{schema.version}")
        
    # Create subscriptions
    print("\n📥 Creating Subscriptions...")
    
    user_topic = platform.topic_manager.get_by_name("user.events")
    order_topic = platform.topic_manager.get_by_name("order.events")
    payment_topic = platform.topic_manager.get_by_name("payment.events")
    
    subs_config = [
        (user_topic.topic_id, "email-service", "Email notifications"),
        (user_topic.topic_id, "analytics-service", "User analytics"),
        (order_topic.topic_id, "inventory-service", "Inventory updates"),
        (order_topic.topic_id, "notification-service", "Order notifications"),
        (payment_topic.topic_id, "accounting-service", "Payment accounting"),
    ]
    
    for topic_id, subscriber, name in subs_config:
        sub = platform.subscriptions.subscribe(topic_id, subscriber, name)
        print(f"  ✓ {subscriber} -> {name}")
        
    # Publish events
    print("\n📤 Publishing Events...")
    
    event_types = [
        ("user.events", "UserCreated", {"user_id": "u123", "email": "user@example.com", "timestamp": datetime.now().isoformat()}),
        ("user.events", "UserUpdated", {"user_id": "u123", "changes": ["email"], "timestamp": datetime.now().isoformat()}),
        ("order.events", "OrderPlaced", {"order_id": "o456", "user_id": "u123", "items": 3, "total": 150.00}),
        ("order.events", "OrderShipped", {"order_id": "o456", "tracking": "TRACK123"}),
        ("payment.events", "PaymentProcessed", {"payment_id": "p789", "order_id": "o456", "amount": 150.00, "status": "success"}),
    ]
    
    published_events = []
    for topic, event_type, payload in event_types:
        priority = EventPriority.HIGH if "Payment" in event_type else EventPriority.NORMAL
        event = await platform.publisher.publish(topic, event_type, payload, "demo-service", priority)
        published_events.append(event)
        print(f"  ✓ {event_type} -> {topic}")
        
    # Publish more events for analytics
    print("\n📊 Publishing Bulk Events...")
    
    for i in range(20):
        topic = random.choice(["user.events", "order.events", "payment.events"])
        event_type = random.choice(["Created", "Updated", "Processed"])
        payload = {"id": f"item_{i}", "timestamp": datetime.now().isoformat()}
        await platform.publisher.publish(topic, event_type, payload, "bulk-producer")
        
    print(f"  ✓ Published 20 additional events")
    
    # Deliver events
    print("\n📬 Delivering Events...")
    
    for topic_name in ["user.events", "order.events", "payment.events"]:
        delivered = await platform.deliver_events(topic_name)
        print(f"  ✓ {topic_name}: {delivered} events delivered")
        
    # Display topic statistics
    print("\n📊 Topic Statistics:")
    
    print("\n  ┌────────────────────────┬────────────┬────────────┬────────────┐")
    print("  │ Topic                  │ Partitions │ Messages   │ Bytes In   │")
    print("  ├────────────────────────┼────────────┼────────────┼────────────┤")
    
    for topic in platform.topic_manager.topics.values():
        name = topic.name[:22].ljust(22)
        partitions = str(topic.partitions).center(10)
        messages = str(topic.message_count).center(10)
        bytes_in = f"{topic.bytes_in}B".center(10)
        print(f"  │ {name} │ {partitions} │ {messages} │ {bytes_in} │")
        
    print("  └────────────────────────┴────────────┴────────────┴────────────┘")
    
    # Subscription status
    print("\n📥 Subscription Status:")
    
    print("\n  ┌────────────────────────┬────────────────────┬────────────┬────────────┐")
    print("  │ Subscription           │ Subscriber         │ Received   │ Status     │")
    print("  ├────────────────────────┼────────────────────┼────────────┼────────────┤")
    
    for sub in platform.subscriptions.subscriptions.values():
        name = sub.name[:22].ljust(22)
        subscriber = sub.subscriber_id[:18].ljust(18)
        received = str(sub.messages_received).center(10)
        status = f"🟢 {sub.status.value}" if sub.status == SubscriptionStatus.ACTIVE else f"🟡 {sub.status.value}"
        print(f"  │ {name} │ {subscriber} │ {received} │ {status:10s} │")
        
    print("  └────────────────────────┴────────────────────┴────────────┴────────────┘")
    
    # Event status distribution
    print("\n📈 Event Status Distribution:")
    
    status_counts = {}
    for event in platform.publisher.events.values():
        s = event.status.value
        status_counts[s] = status_counts.get(s, 0) + 1
        
    for status, count in status_counts.items():
        pct = count / len(platform.publisher.events) * 100
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"  {status:15s} [{bar}] {count} ({pct:.0f}%)")
        
    # Event priority distribution
    print("\n⚡ Event Priority Distribution:")
    
    priority_counts = {}
    for event in platform.publisher.events.values():
        p = event.priority.value
        priority_counts[p] = priority_counts.get(p, 0) + 1
        
    for priority, count in priority_counts.items():
        bar = "█" * count
        print(f"  {priority:10s} {bar} ({count})")
        
    # Dead Letter Queue
    print("\n☠️ Dead Letter Queue:")
    
    if platform.dlq.entries:
        print(f"\n  Entries: {len(platform.dlq.entries)}")
        for entry in list(platform.dlq.entries.values())[:3]:
            print(f"    • Event {entry.event_id}: {entry.reason}")
    else:
        print("  ✓ DLQ is empty")
        
    # Event flow visualization
    print("\n🔄 Event Flow (Last 5 Events):")
    
    for event in published_events[:5]:
        status_icon = "✅" if event.status == EventStatus.DELIVERED else "⏳"
        print(f"  {status_icon} {event.source} -> [{event.topic}] -> {event.event_type}")
        
    # Schema registry
    print("\n📋 Registered Schemas:")
    
    for schema in platform.schema_registry.schemas.values():
        required = schema.schema_definition.get("required", [])
        print(f"  • {schema.name} v{schema.version}: {', '.join(required)}")
        
    # Throughput simulation
    print("\n📊 Throughput Metrics:")
    
    events_per_topic = {}
    for event in platform.publisher.events.values():
        t = event.topic
        events_per_topic[t] = events_per_topic.get(t, 0) + 1
        
    print("\n  Events per Topic:")
    for topic, count in sorted(events_per_topic.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * (count * 2)
        print(f"    {topic:20s} {bar} ({count})")
        
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📈 Platform Statistics:")
    
    print(f"\n  Total Topics: {stats['total_topics']}")
    print(f"  Subscriptions: {stats['active_subscriptions']}/{stats['total_subscriptions']} active")
    print(f"  Total Events: {stats['total_events']}")
    print(f"  Delivered: {stats['delivered_events']}")
    print(f"  Failed: {stats['failed_events']}")
    print(f"  DLQ Entries: {stats['dlq_entries']}")
    print(f"  Schemas: {stats['schemas_registered']}")
    
    # Delivery rate
    delivery_rate = (stats['delivered_events'] / stats['total_events'] * 100) if stats['total_events'] > 0 else 0
    
    print(f"\n  Delivery Rate: {delivery_rate:.1f}%")
    rate_bar = "█" * int(delivery_rate / 10) + "░" * (10 - int(delivery_rate / 10))
    print(f"  [{rate_bar}]")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                      Event Bus Dashboard                            │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Topics:                  {stats['total_topics']:>12}                        │")
    print(f"│ Active Subscriptions:          {stats['active_subscriptions']:>12}                        │")
    print(f"│ Total Events:                  {stats['total_events']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Delivered Events:              {stats['delivered_events']:>12}                        │")
    print(f"│ DLQ Entries:                   {stats['dlq_entries']:>12}                        │")
    print(f"│ Delivery Rate:                   {delivery_rate:>10.1f}%                   │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Event Bus Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
