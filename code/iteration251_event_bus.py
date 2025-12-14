#!/usr/bin/env python3
"""
Server Init - Iteration 251: Event Bus Platform
Платформа распределённой шины событий

Функционал:
- Topic Management - управление топиками
- Event Publishing - публикация событий
- Event Subscription - подписка на события
- Message Routing - маршрутизация сообщений
- Dead Letter Queue - очередь недоставленных
- Event Replay - воспроизведение событий
- Partitioning - партиционирование
- Consumer Groups - группы потребителей
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
import uuid
import json


class TopicState(Enum):
    """Состояние топика"""
    ACTIVE = "active"
    PAUSED = "paused"
    DELETED = "deleted"
    CREATING = "creating"


class SubscriptionState(Enum):
    """Состояние подписки"""
    ACTIVE = "active"
    PAUSED = "paused"
    EXPIRED = "expired"
    ERROR = "error"


class DeliveryMode(Enum):
    """Режим доставки"""
    AT_MOST_ONCE = "at_most_once"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"


class AckMode(Enum):
    """Режим подтверждения"""
    AUTO = "auto"
    MANUAL = "manual"
    BATCH = "batch"


class EventPriority(Enum):
    """Приоритет события"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class Topic:
    """Топик событий"""
    topic_id: str
    name: str
    
    # State
    state: TopicState = TopicState.ACTIVE
    
    # Configuration
    partitions: int = 1
    replication_factor: int = 1
    retention_hours: int = 168  # 7 days
    
    # Options
    compaction: bool = False
    ordered: bool = True
    
    # Stats
    message_count: int = 0
    bytes_total: int = 0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Partition:
    """Партиция топика"""
    partition_id: str
    topic_id: str
    partition_number: int
    
    # State
    leader_broker: str = ""
    replicas: List[str] = field(default_factory=list)
    
    # Offsets
    low_watermark: int = 0
    high_watermark: int = 0
    
    # Stats
    message_count: int = 0
    bytes_total: int = 0


@dataclass
class Event:
    """Событие"""
    event_id: str
    
    # Topic
    topic_id: str = ""
    partition: int = 0
    offset: int = 0
    
    # Event data
    event_type: str = ""
    key: str = ""
    value: Any = None
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Priority
    priority: EventPriority = EventPriority.NORMAL
    
    # Metadata
    source: str = ""
    correlation_id: str = ""
    causation_id: str = ""
    
    # Size
    size_bytes: int = 0
    
    # Time
    timestamp: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


@dataclass
class Subscription:
    """Подписка на топик"""
    subscription_id: str
    name: str
    
    # Topic
    topic_id: str = ""
    
    # State
    state: SubscriptionState = SubscriptionState.ACTIVE
    
    # Consumer group
    consumer_group: str = ""
    
    # Configuration
    delivery_mode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE
    ack_mode: AckMode = AckMode.MANUAL
    max_retries: int = 3
    retry_delay_ms: int = 1000
    
    # Filter
    event_type_filter: List[str] = field(default_factory=list)
    key_filter: str = ""
    
    # Offsets (per partition)
    committed_offsets: Dict[int, int] = field(default_factory=dict)
    
    # Stats
    messages_received: int = 0
    messages_acknowledged: int = 0
    messages_rejected: int = 0
    
    # Handler
    handler: Optional[Callable] = None
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ConsumerGroup:
    """Группа потребителей"""
    group_id: str
    name: str
    
    # Members
    members: Set[str] = field(default_factory=set)  # subscription_ids
    
    # Partition assignment
    assignments: Dict[str, List[int]] = field(default_factory=dict)  # subscription_id -> partitions
    
    # State
    coordinator: str = ""
    generation: int = 0
    
    # Stats
    lag: int = 0
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DeadLetterEntry:
    """Запись в Dead Letter Queue"""
    entry_id: str
    
    # Original event
    original_event: Event = field(default_factory=lambda: Event(event_id=""))
    
    # Error info
    error_message: str = ""
    error_count: int = 0
    
    # Subscription
    subscription_id: str = ""
    
    # Time
    failed_at: datetime = field(default_factory=datetime.now)
    last_retry_at: Optional[datetime] = None


class EventBus:
    """Распределённая шина событий"""
    
    def __init__(self):
        self.topics: Dict[str, Topic] = {}
        self.partitions: Dict[str, Partition] = {}
        self.events: Dict[str, List[Event]] = {}  # topic_id -> events
        self.subscriptions: Dict[str, Subscription] = {}
        self.consumer_groups: Dict[str, ConsumerGroup] = {}
        self.dead_letter_queue: List[DeadLetterEntry] = []
        
        # Counters
        self._total_published = 0
        self._total_delivered = 0
        
    def create_topic(self, name: str, partitions: int = 1,
                    retention_hours: int = 168,
                    compaction: bool = False) -> Topic:
        """Создание топика"""
        topic = Topic(
            topic_id=f"topic_{uuid.uuid4().hex[:8]}",
            name=name,
            partitions=partitions,
            retention_hours=retention_hours,
            compaction=compaction
        )
        
        self.topics[topic.topic_id] = topic
        self.events[topic.topic_id] = []
        
        # Create partitions
        for i in range(partitions):
            partition = Partition(
                partition_id=f"part_{uuid.uuid4().hex[:8]}",
                topic_id=topic.topic_id,
                partition_number=i,
                leader_broker=f"broker-{i % 3}"
            )
            self.partitions[partition.partition_id] = partition
            
        return topic
        
    async def publish(self, topic_name: str, event_type: str,
                     value: Any, key: str = "",
                     headers: Dict[str, str] = None,
                     priority: EventPriority = EventPriority.NORMAL) -> Optional[Event]:
        """Публикация события"""
        # Find topic
        topic = None
        for t in self.topics.values():
            if t.name == topic_name and t.state == TopicState.ACTIVE:
                topic = t
                break
                
        if not topic:
            return None
            
        # Calculate partition
        partition_num = 0
        if key:
            partition_num = hash(key) % topic.partitions
            
        # Get partition
        partition = None
        for p in self.partitions.values():
            if p.topic_id == topic.topic_id and p.partition_number == partition_num:
                partition = p
                break
                
        if not partition:
            return None
            
        # Create event
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            topic_id=topic.topic_id,
            partition=partition_num,
            offset=partition.high_watermark,
            event_type=event_type,
            key=key,
            value=value,
            headers=headers or {},
            priority=priority,
            size_bytes=len(json.dumps(value, default=str))
        )
        
        # Update partition
        partition.high_watermark += 1
        partition.message_count += 1
        partition.bytes_total += event.size_bytes
        
        # Update topic
        topic.message_count += 1
        topic.bytes_total += event.size_bytes
        
        # Store event
        self.events[topic.topic_id].append(event)
        self._total_published += 1
        
        # Deliver to subscribers
        await self._deliver_event(event)
        
        return event
        
    async def _deliver_event(self, event: Event):
        """Доставка события подписчикам"""
        for sub in self.subscriptions.values():
            if sub.topic_id != event.topic_id:
                continue
                
            if sub.state != SubscriptionState.ACTIVE:
                continue
                
            # Check filter
            if sub.event_type_filter and event.event_type not in sub.event_type_filter:
                continue
                
            if sub.key_filter and sub.key_filter not in event.key:
                continue
                
            # Check consumer group partition assignment
            if sub.consumer_group:
                group = self.consumer_groups.get(sub.consumer_group)
                if group:
                    assigned_partitions = group.assignments.get(sub.subscription_id, [])
                    if event.partition not in assigned_partitions:
                        continue
                        
            # Deliver
            try:
                if sub.handler:
                    await sub.handler(event)
                    
                sub.messages_received += 1
                self._total_delivered += 1
                
                # Auto ack
                if sub.ack_mode == AckMode.AUTO:
                    await self.acknowledge(sub.subscription_id, event.partition, event.offset)
                    
            except Exception as e:
                sub.messages_rejected += 1
                await self._send_to_dlq(event, sub.subscription_id, str(e))
                
    def subscribe(self, topic_name: str, name: str,
                 consumer_group: str = "",
                 delivery_mode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE,
                 event_type_filter: List[str] = None,
                 handler: Callable = None) -> Optional[Subscription]:
        """Подписка на топик"""
        # Find topic
        topic = None
        for t in self.topics.values():
            if t.name == topic_name:
                topic = t
                break
                
        if not topic:
            return None
            
        subscription = Subscription(
            subscription_id=f"sub_{uuid.uuid4().hex[:8]}",
            name=name,
            topic_id=topic.topic_id,
            consumer_group=consumer_group,
            delivery_mode=delivery_mode,
            event_type_filter=event_type_filter or [],
            handler=handler
        )
        
        # Initialize offsets for all partitions
        for p in self.partitions.values():
            if p.topic_id == topic.topic_id:
                subscription.committed_offsets[p.partition_number] = p.high_watermark
                
        self.subscriptions[subscription.subscription_id] = subscription
        
        # Add to consumer group
        if consumer_group:
            if consumer_group not in self.consumer_groups:
                self.consumer_groups[consumer_group] = ConsumerGroup(
                    group_id=consumer_group,
                    name=consumer_group
                )
            group = self.consumer_groups[consumer_group]
            group.members.add(subscription.subscription_id)
            
            # Rebalance partitions
            self._rebalance_group(group, topic.topic_id)
            
        return subscription
        
    def _rebalance_group(self, group: ConsumerGroup, topic_id: str):
        """Ребалансировка партиций в группе"""
        partitions = [
            p.partition_number for p in self.partitions.values()
            if p.topic_id == topic_id
        ]
        
        members = list(group.members)
        if not members:
            return
            
        # Simple round-robin assignment
        group.assignments = {}
        for member in members:
            group.assignments[member] = []
            
        for i, partition in enumerate(partitions):
            member = members[i % len(members)]
            group.assignments[member].append(partition)
            
        group.generation += 1
        
    async def acknowledge(self, subscription_id: str,
                         partition: int, offset: int):
        """Подтверждение получения события"""
        sub = self.subscriptions.get(subscription_id)
        if not sub:
            return
            
        current = sub.committed_offsets.get(partition, 0)
        if offset >= current:
            sub.committed_offsets[partition] = offset + 1
            sub.messages_acknowledged += 1
            
    async def reject(self, subscription_id: str, event: Event, error: str = ""):
        """Отклонение события"""
        sub = self.subscriptions.get(subscription_id)
        if not sub:
            return
            
        sub.messages_rejected += 1
        await self._send_to_dlq(event, subscription_id, error)
        
    async def _send_to_dlq(self, event: Event, subscription_id: str, error: str):
        """Отправка в Dead Letter Queue"""
        entry = DeadLetterEntry(
            entry_id=f"dlq_{uuid.uuid4().hex[:8]}",
            original_event=event,
            error_message=error,
            error_count=1,
            subscription_id=subscription_id
        )
        
        self.dead_letter_queue.append(entry)
        
    async def replay(self, topic_name: str, from_offset: int,
                    to_offset: Optional[int] = None,
                    partition: int = 0) -> List[Event]:
        """Воспроизведение событий из топика"""
        topic = None
        for t in self.topics.values():
            if t.name == topic_name:
                topic = t
                break
                
        if not topic:
            return []
            
        events = self.events.get(topic.topic_id, [])
        
        return [
            e for e in events
            if e.partition == partition
            and e.offset >= from_offset
            and (to_offset is None or e.offset <= to_offset)
        ]
        
    def get_topic_stats(self, topic_id: str) -> Dict[str, Any]:
        """Статистика топика"""
        topic = self.topics.get(topic_id)
        if not topic:
            return {}
            
        subscriptions = [
            s for s in self.subscriptions.values()
            if s.topic_id == topic_id
        ]
        
        partitions = [
            p for p in self.partitions.values()
            if p.topic_id == topic_id
        ]
        
        return {
            "topic_id": topic_id,
            "name": topic.name,
            "state": topic.state.value,
            "partitions": len(partitions),
            "subscriptions": len(subscriptions),
            "message_count": topic.message_count,
            "bytes_total": topic.bytes_total,
            "retention_hours": topic.retention_hours
        }
        
    def get_consumer_lag(self, group_id: str) -> Dict[str, int]:
        """Получение lag для consumer group"""
        group = self.consumer_groups.get(group_id)
        if not group:
            return {}
            
        lag_by_partition = {}
        
        for sub_id in group.members:
            sub = self.subscriptions.get(sub_id)
            if not sub:
                continue
                
            for partition, committed in sub.committed_offsets.items():
                # Get partition high watermark
                for p in self.partitions.values():
                    if p.topic_id == sub.topic_id and p.partition_number == partition:
                        lag = p.high_watermark - committed
                        lag_by_partition[f"p{partition}"] = lag
                        break
                        
        return lag_by_partition
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        active_topics = sum(1 for t in self.topics.values() if t.state == TopicState.ACTIVE)
        active_subs = sum(1 for s in self.subscriptions.values() if s.state == SubscriptionState.ACTIVE)
        total_messages = sum(t.message_count for t in self.topics.values())
        total_bytes = sum(t.bytes_total for t in self.topics.values())
        
        return {
            "topics_total": len(self.topics),
            "topics_active": active_topics,
            "partitions_total": len(self.partitions),
            "subscriptions_total": len(self.subscriptions),
            "subscriptions_active": active_subs,
            "consumer_groups": len(self.consumer_groups),
            "total_published": self._total_published,
            "total_delivered": self._total_delivered,
            "total_messages": total_messages,
            "total_bytes": total_bytes,
            "dlq_size": len(self.dead_letter_queue)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 251: Event Bus Platform")
    print("=" * 60)
    
    bus = EventBus()
    print("✓ Event Bus created")
    
    # Create topics
    print("\n📁 Creating Topics...")
    
    topics_data = [
        ("user-events", 3, 168, False),
        ("order-events", 4, 720, False),
        ("notifications", 2, 24, False),
        ("audit-log", 1, 8760, True),  # 1 year, compacted
    ]
    
    topics = []
    for name, partitions, retention, compaction in topics_data:
        topic = bus.create_topic(name, partitions, retention, compaction)
        topics.append(topic)
        print(f"  📁 {name} ({partitions} partitions, {retention}h retention)")
        
    # Create event handlers
    received_events = []
    
    async def user_handler(event: Event):
        received_events.append(event)
        
    async def order_handler(event: Event):
        received_events.append(event)
        
    # Subscribe to topics
    print("\n🔔 Creating Subscriptions...")
    
    subs_data = [
        ("user-events", "user-service-1", "user-consumers", DeliveryMode.AT_LEAST_ONCE, ["user.created", "user.updated"]),
        ("user-events", "user-service-2", "user-consumers", DeliveryMode.AT_LEAST_ONCE, ["user.deleted"]),
        ("order-events", "order-processor", "order-processors", DeliveryMode.EXACTLY_ONCE, []),
        ("notifications", "email-sender", "", DeliveryMode.AT_MOST_ONCE, ["notification.email"]),
    ]
    
    subscriptions = []
    for topic_name, name, group, mode, filters in subs_data:
        handler = user_handler if "user" in topic_name else order_handler
        sub = bus.subscribe(topic_name, name, group, mode, filters, handler)
        if sub:
            subscriptions.append(sub)
            print(f"  🔔 {name} -> {topic_name} (group: {group or 'none'})")
            
    # Publish events
    print("\n📤 Publishing Events...")
    
    events_to_publish = [
        ("user-events", "user.created", {"user_id": "u1", "email": "alice@example.com"}, "u1"),
        ("user-events", "user.updated", {"user_id": "u1", "name": "Alice"}, "u1"),
        ("user-events", "user.created", {"user_id": "u2", "email": "bob@example.com"}, "u2"),
        ("order-events", "order.created", {"order_id": "o1", "amount": 99.99}, "o1"),
        ("order-events", "order.paid", {"order_id": "o1", "method": "card"}, "o1"),
        ("order-events", "order.shipped", {"order_id": "o1", "tracking": "TRK123"}, "o1"),
        ("notifications", "notification.email", {"to": "alice@example.com", "subject": "Welcome"}, ""),
        ("audit-log", "audit.login", {"user_id": "u1", "ip": "192.168.1.1"}, "u1"),
    ]
    
    published_events = []
    for topic_name, event_type, value, key in events_to_publish:
        event = await bus.publish(topic_name, event_type, value, key)
        if event:
            published_events.append(event)
            print(f"  📤 {event_type} -> {topic_name} (partition: {event.partition}, offset: {event.offset})")
            
    # Display topics
    print("\n📊 Topics:")
    
    print("\n  ┌─────────────────┬───────────┬──────────┬──────────┬──────────┐")
    print("  │ Topic           │ Partitions│ Messages │ Subs     │ State    │")
    print("  ├─────────────────┼───────────┼──────────┼──────────┼──────────┤")
    
    for topic in bus.topics.values():
        stats = bus.get_topic_stats(topic.topic_id)
        name = topic.name[:15].ljust(15)
        parts = str(stats['partitions'])[:9].ljust(9)
        msgs = str(stats['message_count'])[:8].ljust(8)
        subs = str(stats['subscriptions'])[:8].ljust(8)
        state = topic.state.value[:8].ljust(8)
        
        print(f"  │ {name} │ {parts} │ {msgs} │ {subs} │ {state} │")
        
    print("  └─────────────────┴───────────┴──────────┴──────────┴──────────┘")
    
    # Display partitions
    print("\n📊 Partitions (user-events):")
    
    print("\n  ┌──────────┬──────────┬──────────┬──────────┬──────────┐")
    print("  │ Partition│ Leader   │ Low WM   │ High WM  │ Messages │")
    print("  ├──────────┼──────────┼──────────┼──────────┼──────────┤")
    
    for p in bus.partitions.values():
        if p.topic_id == topics[0].topic_id:
            pnum = str(p.partition_number)[:8].ljust(8)
            leader = p.leader_broker[:8].ljust(8)
            low = str(p.low_watermark)[:8].ljust(8)
            high = str(p.high_watermark)[:8].ljust(8)
            msgs = str(p.message_count)[:8].ljust(8)
            
            print(f"  │ {pnum} │ {leader} │ {low} │ {high} │ {msgs} │")
            
    print("  └──────────┴──────────┴──────────┴──────────┴──────────┘")
    
    # Display subscriptions
    print("\n🔔 Subscriptions:")
    
    print("\n  ┌─────────────────┬─────────────────┬──────────┬──────────┬──────────┐")
    print("  │ Subscription    │ Consumer Group  │ Received │ Acked    │ State    │")
    print("  ├─────────────────┼─────────────────┼──────────┼──────────┼──────────┤")
    
    for sub in bus.subscriptions.values():
        name = sub.name[:15].ljust(15)
        group = (sub.consumer_group or "-")[:15].ljust(15)
        received = str(sub.messages_received)[:8].ljust(8)
        acked = str(sub.messages_acknowledged)[:8].ljust(8)
        state = sub.state.value[:8].ljust(8)
        
        print(f"  │ {name} │ {group} │ {received} │ {acked} │ {state} │")
        
    print("  └─────────────────┴─────────────────┴──────────┴──────────┴──────────┘")
    
    # Display consumer groups
    print("\n👥 Consumer Groups:")
    
    for group_id, group in bus.consumer_groups.items():
        print(f"\n  Group: {group_id}")
        print(f"    Members: {len(group.members)}")
        print(f"    Generation: {group.generation}")
        
        lag = bus.get_consumer_lag(group_id)
        if lag:
            print(f"    Lag by partition: {lag}")
            
        print("    Assignments:")
        for sub_id, partitions in group.assignments.items():
            sub = bus.subscriptions.get(sub_id)
            if sub:
                print(f"      {sub.name}: partitions {partitions}")
                
    # Replay events
    print("\n🔄 Replaying Events (user-events, partition 0)...")
    
    replayed = await bus.replay("user-events", 0, 10, 0)
    for event in replayed[:3]:
        print(f"  🔄 [{event.offset}] {event.event_type}: {event.key}")
        
    # Recent events
    print("\n📋 Recent Events (user-events):")
    
    topic_events = bus.events.get(topics[0].topic_id, [])
    for event in topic_events[-5:]:
        print(f"  [{event.partition}:{event.offset}] {event.event_type} | key={event.key}")
        
    # Dead Letter Queue
    print(f"\n💀 Dead Letter Queue: {len(bus.dead_letter_queue)} entries")
    
    # Statistics
    print("\n📊 Event Bus Statistics:")
    
    stats = bus.get_statistics()
    
    print(f"\n  Topics: {stats['topics_total']} (active: {stats['topics_active']})")
    print(f"  Partitions: {stats['partitions_total']}")
    print(f"  Subscriptions: {stats['subscriptions_total']} (active: {stats['subscriptions_active']})")
    print(f"  Consumer Groups: {stats['consumer_groups']}")
    
    print(f"\n  Published: {stats['total_published']}")
    print(f"  Delivered: {stats['total_delivered']}")
    print(f"  Total Messages: {stats['total_messages']}")
    print(f"  Total Size: {stats['total_bytes'] / 1024:.1f} KB")
    
    # Event type distribution
    print("\n📊 Event Types Distribution:")
    
    event_types: Dict[str, int] = {}
    for topic_id, events in bus.events.items():
        for event in events:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
            
    for etype, count in sorted(event_types.items(), key=lambda x: -x[1])[:5]:
        bar = "█" * min(count, 10)
        print(f"  {etype:25s} [{bar:10s}] {count}")
        
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                     Event Bus Dashboard                             │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Topics:                        {stats['topics_total']:>12}                        │")
    print(f"│ Partitions:                    {stats['partitions_total']:>12}                        │")
    print(f"│ Subscriptions:                 {stats['subscriptions_total']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Events Published:              {stats['total_published']:>12}                        │")
    print(f"│ Events Delivered:              {stats['total_delivered']:>12}                        │")
    print(f"│ DLQ Size:                      {stats['dlq_size']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Event Bus Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
