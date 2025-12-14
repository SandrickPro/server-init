#!/usr/bin/env python3
"""
Server Init - Iteration 284: Event Streaming Platform
Платформа Event Streaming

Функционал:
- Event Production - публикация событий
- Event Consumption - потребление событий
- Stream Processing - обработка потоков
- Partitioning - партиционирование
- Consumer Groups - группы потребителей
- Offset Management - управление смещениями
- Retention Policies - политики хранения
- Dead Letter Queue - очередь недоставленных
"""

import asyncio
import random
import time
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
import uuid


class EventState(Enum):
    """Состояние события"""
    PENDING = "pending"
    COMMITTED = "committed"
    ACKNOWLEDGED = "acknowledged"
    DEAD = "dead"


class AckMode(Enum):
    """Режим подтверждения"""
    AUTO = "auto"
    MANUAL = "manual"
    BATCH = "batch"


class PartitionStrategy(Enum):
    """Стратегия партиционирования"""
    ROUND_ROBIN = "round_robin"
    KEY_HASH = "key_hash"
    RANDOM = "random"
    STICKY = "sticky"


class OffsetReset(Enum):
    """Сброс смещения"""
    EARLIEST = "earliest"
    LATEST = "latest"
    NONE = "none"


class RetentionPolicy(Enum):
    """Политика хранения"""
    TIME = "time"
    SIZE = "size"
    COMPACT = "compact"


@dataclass
class Event:
    """Событие"""
    event_id: str
    
    # Metadata
    topic: str = ""
    partition: int = 0
    offset: int = 0
    
    # Key/Value
    key: Optional[str] = None
    value: Any = None
    
    # Headers
    headers: Dict[str, str] = field(default_factory=dict)
    
    # State
    state: EventState = EventState.PENDING
    
    # Timing
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Size
    size_bytes: int = 0


@dataclass
class Partition:
    """Партиция"""
    partition_id: int
    topic: str
    
    # Events
    events: List[Event] = field(default_factory=list)
    
    # Offsets
    high_watermark: int = 0  # Latest committed offset
    low_watermark: int = 0   # Earliest available offset
    
    # Stats
    bytes_in: int = 0
    bytes_out: int = 0
    
    # Leader
    leader_broker: str = ""


@dataclass
class Topic:
    """Топик"""
    topic_id: str
    name: str
    
    # Partitions
    partitions: Dict[int, Partition] = field(default_factory=dict)
    partition_count: int = 3
    
    # Replication
    replication_factor: int = 1
    
    # Retention
    retention_policy: RetentionPolicy = RetentionPolicy.TIME
    retention_ms: int = 604800000  # 7 days
    retention_bytes: int = -1
    
    # Config
    max_message_bytes: int = 1048576  # 1MB
    
    # Stats
    messages_in: int = 0
    messages_out: int = 0
    
    # Created
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ConsumerGroup:
    """Группа потребителей"""
    group_id: str
    name: str
    
    # Members
    members: Dict[str, 'Consumer'] = field(default_factory=dict)
    
    # Offsets per topic-partition
    committed_offsets: Dict[str, int] = field(default_factory=dict)  # "topic:partition" -> offset
    
    # Assignment
    partition_assignment: Dict[str, Set[str]] = field(default_factory=dict)  # member_id -> set of "topic:partition"
    
    # Config
    ack_mode: AckMode = AckMode.AUTO
    
    # Generation
    generation_id: int = 0


@dataclass
class Consumer:
    """Потребитель"""
    consumer_id: str
    
    # Group
    group_id: str = ""
    group_name: str = ""
    
    # Subscriptions
    subscribed_topics: Set[str] = field(default_factory=set)
    assigned_partitions: Set[str] = field(default_factory=set)  # "topic:partition"
    
    # Offsets
    current_offsets: Dict[str, int] = field(default_factory=dict)  # "topic:partition" -> offset
    
    # Config
    offset_reset: OffsetReset = OffsetReset.LATEST
    max_poll_records: int = 500
    
    # Session
    session_timeout_ms: int = 30000
    last_heartbeat: datetime = field(default_factory=datetime.now)
    
    # Stats
    messages_consumed: int = 0
    bytes_consumed: int = 0


@dataclass
class Producer:
    """Производитель"""
    producer_id: str
    
    # Config
    partition_strategy: PartitionStrategy = PartitionStrategy.ROUND_ROBIN
    
    # State
    current_partition: int = 0
    
    # Stats
    messages_produced: int = 0
    bytes_produced: int = 0
    
    # Acks
    acks: str = "all"  # 0, 1, all


@dataclass
class DeadLetterEntry:
    """Запись в DLQ"""
    entry_id: str
    original_event: Event
    
    # Error info
    error_message: str = ""
    error_timestamp: datetime = field(default_factory=datetime.now)
    
    # Retry info
    retry_count: int = 0
    max_retries: int = 3
    
    # Source
    source_consumer: str = ""
    source_group: str = ""


class EventStreamingManager:
    """Менеджер Event Streaming"""
    
    def __init__(self):
        self.topics: Dict[str, Topic] = {}
        self.consumer_groups: Dict[str, ConsumerGroup] = {}
        self.producers: Dict[str, Producer] = {}
        self.consumers: Dict[str, Consumer] = {}
        
        # DLQ
        self.dead_letter_queue: List[DeadLetterEntry] = []
        
        # Stats
        self.events_total: int = 0
        self.events_delivered: int = 0
        self.events_failed: int = 0
        
        # Stream processors
        self.processors: Dict[str, Callable] = {}
        
    def create_topic(self, name: str,
                    partitions: int = 3,
                    replication_factor: int = 1,
                    retention_ms: int = 604800000) -> Topic:
        """Создание топика"""
        topic = Topic(
            topic_id=f"topic_{uuid.uuid4().hex[:8]}",
            name=name,
            partition_count=partitions,
            replication_factor=replication_factor,
            retention_ms=retention_ms
        )
        
        # Create partitions
        for i in range(partitions):
            partition = Partition(
                partition_id=i,
                topic=name,
                leader_broker=f"broker_{i % 3}"
            )
            topic.partitions[i] = partition
            
        self.topics[name] = topic
        return topic
        
    def create_producer(self, strategy: PartitionStrategy = PartitionStrategy.ROUND_ROBIN) -> Producer:
        """Создание producer"""
        producer = Producer(
            producer_id=f"producer_{uuid.uuid4().hex[:8]}",
            partition_strategy=strategy
        )
        
        self.producers[producer.producer_id] = producer
        return producer
        
    def create_consumer(self, group_name: str,
                       offset_reset: OffsetReset = OffsetReset.LATEST) -> Consumer:
        """Создание consumer"""
        consumer = Consumer(
            consumer_id=f"consumer_{uuid.uuid4().hex[:8]}",
            group_name=group_name,
            offset_reset=offset_reset
        )
        
        # Join or create group
        if group_name not in self.consumer_groups:
            group = ConsumerGroup(
                group_id=f"group_{uuid.uuid4().hex[:8]}",
                name=group_name
            )
            self.consumer_groups[group_name] = group
            
        group = self.consumer_groups[group_name]
        consumer.group_id = group.group_id
        group.members[consumer.consumer_id] = consumer
        
        self.consumers[consumer.consumer_id] = consumer
        return consumer
        
    async def produce(self, producer: Producer,
                     topic_name: str,
                     value: Any,
                     key: str = None,
                     headers: Dict[str, str] = None) -> Event:
        """Публикация события"""
        topic = self.topics.get(topic_name)
        if not topic:
            raise Exception(f"Topic not found: {topic_name}")
            
        # Select partition
        partition_id = self._select_partition(producer, topic, key)
        partition = topic.partitions[partition_id]
        
        # Create event
        event = Event(
            event_id=f"event_{uuid.uuid4().hex[:12]}",
            topic=topic_name,
            partition=partition_id,
            offset=partition.high_watermark,
            key=key,
            value=value,
            headers=headers or {},
            state=EventState.COMMITTED,
            size_bytes=len(str(value))
        )
        
        # Add to partition
        partition.events.append(event)
        partition.high_watermark += 1
        partition.bytes_in += event.size_bytes
        
        # Update stats
        producer.messages_produced += 1
        producer.bytes_produced += event.size_bytes
        topic.messages_in += 1
        self.events_total += 1
        
        return event
        
    def _select_partition(self, producer: Producer,
                         topic: Topic,
                         key: str = None) -> int:
        """Выбор партиции"""
        if producer.partition_strategy == PartitionStrategy.ROUND_ROBIN:
            partition = producer.current_partition
            producer.current_partition = (partition + 1) % topic.partition_count
            return partition
            
        elif producer.partition_strategy == PartitionStrategy.KEY_HASH:
            if key:
                hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)
                return hash_value % topic.partition_count
            return random.randint(0, topic.partition_count - 1)
            
        elif producer.partition_strategy == PartitionStrategy.RANDOM:
            return random.randint(0, topic.partition_count - 1)
            
        return 0
        
    async def subscribe(self, consumer: Consumer, topics: List[str]):
        """Подписка consumer на топики"""
        consumer.subscribed_topics.update(topics)
        
        # Trigger rebalance
        await self._rebalance_group(consumer.group_name)
        
    async def _rebalance_group(self, group_name: str):
        """Ребалансировка группы"""
        group = self.consumer_groups.get(group_name)
        if not group:
            return
            
        group.generation_id += 1
        
        # Collect all partitions to assign
        all_partitions: List[str] = []
        
        for member in group.members.values():
            for topic_name in member.subscribed_topics:
                topic = self.topics.get(topic_name)
                if topic:
                    for p_id in topic.partitions:
                        all_partitions.append(f"{topic_name}:{p_id}")
                        
        # Clear current assignments
        for member in group.members.values():
            member.assigned_partitions.clear()
            
        group.partition_assignment.clear()
        
        # Round-robin assignment
        members = list(group.members.values())
        if not members:
            return
            
        for i, partition_key in enumerate(all_partitions):
            member = members[i % len(members)]
            member.assigned_partitions.add(partition_key)
            
            if member.consumer_id not in group.partition_assignment:
                group.partition_assignment[member.consumer_id] = set()
            group.partition_assignment[member.consumer_id].add(partition_key)
            
            # Initialize offset
            if partition_key not in member.current_offsets:
                committed = group.committed_offsets.get(partition_key, 0)
                if committed > 0:
                    member.current_offsets[partition_key] = committed
                elif member.offset_reset == OffsetReset.EARLIEST:
                    member.current_offsets[partition_key] = 0
                else:
                    # Latest
                    topic_name, p_id = partition_key.split(":")
                    topic = self.topics.get(topic_name)
                    if topic:
                        member.current_offsets[partition_key] = topic.partitions[int(p_id)].high_watermark
                        
    async def poll(self, consumer: Consumer,
                  timeout_ms: int = 1000) -> List[Event]:
        """Получение событий consumer"""
        events = []
        
        for partition_key in consumer.assigned_partitions:
            topic_name, p_id = partition_key.split(":")
            topic = self.topics.get(topic_name)
            
            if not topic:
                continue
                
            partition = topic.partitions.get(int(p_id))
            if not partition:
                continue
                
            # Get current offset
            current_offset = consumer.current_offsets.get(partition_key, 0)
            
            # Fetch events
            for event in partition.events[current_offset:]:
                if len(events) >= consumer.max_poll_records:
                    break
                    
                events.append(event)
                consumer.current_offsets[partition_key] = event.offset + 1
                
        # Update stats
        consumer.messages_consumed += len(events)
        consumer.bytes_consumed += sum(e.size_bytes for e in events)
        consumer.last_heartbeat = datetime.now()
        
        # Auto ack
        group = self.consumer_groups.get(consumer.group_name)
        if group and group.ack_mode == AckMode.AUTO:
            for partition_key, offset in consumer.current_offsets.items():
                group.committed_offsets[partition_key] = offset
                
        self.events_delivered += len(events)
        
        return events
        
    async def commit(self, consumer: Consumer, offsets: Dict[str, int] = None):
        """Коммит смещений"""
        group = self.consumer_groups.get(consumer.group_name)
        if not group:
            return
            
        if offsets:
            for partition_key, offset in offsets.items():
                group.committed_offsets[partition_key] = offset
        else:
            for partition_key, offset in consumer.current_offsets.items():
                group.committed_offsets[partition_key] = offset
                
    async def send_to_dlq(self, event: Event,
                        error_message: str,
                        consumer: Consumer):
        """Отправка в DLQ"""
        entry = DeadLetterEntry(
            entry_id=f"dlq_{uuid.uuid4().hex[:8]}",
            original_event=event,
            error_message=error_message,
            source_consumer=consumer.consumer_id,
            source_group=consumer.group_name
        )
        
        event.state = EventState.DEAD
        self.dead_letter_queue.append(entry)
        self.events_failed += 1
        
    async def retry_dlq(self, entry_id: str) -> bool:
        """Повторная обработка из DLQ"""
        for entry in self.dead_letter_queue:
            if entry.entry_id == entry_id:
                if entry.retry_count >= entry.max_retries:
                    return False
                    
                entry.retry_count += 1
                entry.original_event.state = EventState.PENDING
                
                # Re-publish event
                topic = self.topics.get(entry.original_event.topic)
                if topic:
                    partition = topic.partitions.get(entry.original_event.partition)
                    if partition:
                        partition.events.append(entry.original_event)
                        partition.high_watermark += 1
                        
                        self.dead_letter_queue.remove(entry)
                        return True
                        
        return False
        
    def register_processor(self, topic: str, processor: Callable):
        """Регистрация stream processor"""
        self.processors[topic] = processor
        
    async def process_stream(self, topic_name: str):
        """Обработка потока"""
        processor = self.processors.get(topic_name)
        if not processor:
            return []
            
        topic = self.topics.get(topic_name)
        if not topic:
            return []
            
        results = []
        
        for partition in topic.partitions.values():
            for event in partition.events:
                if event.state == EventState.COMMITTED:
                    try:
                        result = await processor(event)
                        results.append(result)
                        event.state = EventState.ACKNOWLEDGED
                    except Exception as e:
                        await self.send_to_dlq(event, str(e), Consumer(consumer_id="processor"))
                        
        return results
        
    def apply_retention(self):
        """Применение политик хранения"""
        now = datetime.now()
        
        for topic in self.topics.values():
            if topic.retention_policy == RetentionPolicy.TIME:
                retention_delta = timedelta(milliseconds=topic.retention_ms)
                cutoff = now - retention_delta
                
                for partition in topic.partitions.values():
                    # Remove old events
                    partition.events = [
                        e for e in partition.events
                        if e.timestamp > cutoff
                    ]
                    
                    if partition.events:
                        partition.low_watermark = partition.events[0].offset
                    else:
                        partition.low_watermark = partition.high_watermark
                        
    def get_topic_stats(self, topic_name: str) -> Dict[str, Any]:
        """Статистика топика"""
        topic = self.topics.get(topic_name)
        if not topic:
            return {}
            
        total_events = sum(len(p.events) for p in topic.partitions.values())
        total_bytes = sum(p.bytes_in for p in topic.partitions.values())
        
        return {
            "name": topic.name,
            "partitions": topic.partition_count,
            "total_events": total_events,
            "total_bytes": total_bytes,
            "messages_in": topic.messages_in,
            "messages_out": topic.messages_out
        }
        
    def get_consumer_lag(self, group_name: str) -> Dict[str, int]:
        """Лаг consumer group"""
        group = self.consumer_groups.get(group_name)
        if not group:
            return {}
            
        lag = {}
        
        for partition_key, committed in group.committed_offsets.items():
            topic_name, p_id = partition_key.split(":")
            topic = self.topics.get(topic_name)
            
            if topic:
                partition = topic.partitions.get(int(p_id))
                if partition:
                    lag[partition_key] = partition.high_watermark - committed
                    
        return lag
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        return {
            "topics": len(self.topics),
            "consumer_groups": len(self.consumer_groups),
            "producers": len(self.producers),
            "consumers": len(self.consumers),
            "events_total": self.events_total,
            "events_delivered": self.events_delivered,
            "events_failed": self.events_failed,
            "dlq_size": len(self.dead_letter_queue)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 284: Event Streaming Platform")
    print("=" * 60)
    
    manager = EventStreamingManager()
    print("✓ Event Streaming Manager created")
    
    # Create topics
    print("\n📋 Creating Topics...")
    
    topics_config = [
        ("orders", 4, 3),
        ("payments", 3, 3),
        ("notifications", 2, 2),
        ("analytics", 6, 2),
        ("logs", 8, 1),
    ]
    
    for name, partitions, replication in topics_config:
        topic = manager.create_topic(name, partitions, replication)
        print(f"  📋 {name}: {partitions} partitions, replication={replication}")
        
    # Create producers
    print("\n📤 Creating Producers...")
    
    producer1 = manager.create_producer(PartitionStrategy.ROUND_ROBIN)
    producer2 = manager.create_producer(PartitionStrategy.KEY_HASH)
    producer3 = manager.create_producer(PartitionStrategy.RANDOM)
    
    print(f"  📤 {producer1.producer_id} (round_robin)")
    print(f"  📤 {producer2.producer_id} (key_hash)")
    print(f"  📤 {producer3.producer_id} (random)")
    
    # Produce events
    print("\n✉️ Producing Events...")
    
    events_config = [
        (producer1, "orders", {"order_id": 1, "amount": 100}, "user_123"),
        (producer1, "orders", {"order_id": 2, "amount": 250}, "user_456"),
        (producer2, "payments", {"payment_id": 1, "status": "completed"}, "order_1"),
        (producer2, "payments", {"payment_id": 2, "status": "pending"}, "order_2"),
        (producer3, "notifications", {"type": "email", "to": "user@example.com"}, None),
    ]
    
    for producer, topic, value, key in events_config:
        event = await manager.produce(producer, topic, value, key)
        print(f"  ✉️ {topic}:{event.partition} offset={event.offset}")
        
    # Produce more events
    print("\n📦 Bulk producing events...")
    
    for i in range(100):
        producer = random.choice([producer1, producer2, producer3])
        topic = random.choice(["orders", "payments", "notifications", "analytics", "logs"])
        
        await manager.produce(
            producer,
            topic,
            {"event_id": i, "data": f"event_data_{i}"},
            f"key_{i % 10}"
        )
        
    print(f"  ✓ Produced 100 events")
    
    # Create consumers
    print("\n📥 Creating Consumer Groups...")
    
    consumers = []
    
    for group_name in ["order-processor", "analytics-service", "logger"]:
        for i in range(2):
            consumer = manager.create_consumer(group_name)
            consumers.append(consumer)
            
    print(f"  ✓ Created {len(consumers)} consumers in 3 groups")
    
    # Subscribe consumers
    print("\n📬 Subscribing Consumers...")
    
    # Order processors subscribe to orders and payments
    for consumer in consumers[:2]:
        await manager.subscribe(consumer, ["orders", "payments"])
        
    # Analytics service subscribes to analytics
    for consumer in consumers[2:4]:
        await manager.subscribe(consumer, ["analytics"])
        
    # Logger subscribes to logs
    for consumer in consumers[4:]:
        await manager.subscribe(consumer, ["logs"])
        
    # Display assignments
    for group_name, group in manager.consumer_groups.items():
        print(f"\n  📬 {group_name}:")
        for member_id, partitions in group.partition_assignment.items():
            print(f"    {member_id[:20]}: {len(partitions)} partitions")
            
    # Poll events
    print("\n🔄 Polling Events...")
    
    total_polled = 0
    
    for consumer in consumers:
        events = await manager.poll(consumer, timeout_ms=1000)
        total_polled += len(events)
        
    print(f"  ✓ Polled {total_polled} events")
    
    # Commit offsets
    print("\n💾 Committing Offsets...")
    
    for consumer in consumers:
        await manager.commit(consumer)
        
    print("  ✓ Offsets committed")
    
    # Simulate failures
    print("\n⚠️ Simulating Failures...")
    
    # Get some events and send to DLQ
    for consumer in consumers[:2]:
        events = await manager.poll(consumer)
        for event in events[:2]:
            await manager.send_to_dlq(event, "Processing error", consumer)
            
    print(f"  ⚠️ Sent {len(manager.dead_letter_queue)} events to DLQ")
    
    # Retry from DLQ
    if manager.dead_letter_queue:
        entry = manager.dead_letter_queue[0]
        success = await manager.retry_dlq(entry.entry_id)
        print(f"  🔄 Retry: {'success' if success else 'failed'}")
        
    # Stream processor
    print("\n🔄 Stream Processing...")
    
    async def order_processor(event: Event):
        # Simulate processing
        await asyncio.sleep(0.01)
        return {"processed": event.event_id}
        
    manager.register_processor("orders", order_processor)
    results = await manager.process_stream("orders")
    print(f"  ✓ Processed {len(results)} order events")
    
    # Display topics
    print("\n📋 Topic Statistics:")
    
    print("\n  ┌─────────────────────┬─────────────┬───────────────┬───────────────┐")
    print("  │ Topic               │ Partitions  │ Events        │ Bytes         │")
    print("  ├─────────────────────┼─────────────┼───────────────┼───────────────┤")
    
    for topic in manager.topics.values():
        stats = manager.get_topic_stats(topic.name)
        name = topic.name[:19].ljust(19)
        parts = str(stats['partitions']).ljust(11)
        events = str(stats['total_events']).ljust(13)
        bytes_str = str(stats['total_bytes']).ljust(13)
        
        print(f"  │ {name} │ {parts} │ {events} │ {bytes_str} │")
        
    print("  └─────────────────────┴─────────────┴───────────────┴───────────────┘")
    
    # Display partition distribution
    print("\n📊 Partition Distribution:")
    
    for topic_name, topic in list(manager.topics.items())[:3]:
        print(f"\n  📋 {topic_name}:")
        
        for p_id, partition in topic.partitions.items():
            events_count = len(partition.events)
            bar = "█" * min(events_count, 20) + "░" * max(0, 20 - events_count)
            
            print(f"    P{p_id}: [{bar}] {events_count} events (offset: {partition.low_watermark}-{partition.high_watermark})")
            
    # Consumer lag
    print("\n📈 Consumer Lag:")
    
    for group_name in manager.consumer_groups:
        lag = manager.get_consumer_lag(group_name)
        total_lag = sum(lag.values())
        
        print(f"\n  📊 {group_name}:")
        print(f"    Total lag: {total_lag} events")
        
        for partition_key, partition_lag in list(lag.items())[:3]:
            print(f"    {partition_key}: {partition_lag}")
            
    # DLQ status
    print("\n☠️ Dead Letter Queue:")
    
    print(f"\n  Total entries: {len(manager.dead_letter_queue)}")
    
    for entry in manager.dead_letter_queue[:3]:
        print(f"\n  Entry: {entry.entry_id}")
        print(f"    Topic: {entry.original_event.topic}")
        print(f"    Error: {entry.error_message}")
        print(f"    Retries: {entry.retry_count}/{entry.max_retries}")
        
    # Producer statistics
    print("\n📤 Producer Statistics:")
    
    for producer in manager.producers.values():
        print(f"\n  {producer.producer_id}:")
        print(f"    Strategy: {producer.partition_strategy.value}")
        print(f"    Messages: {producer.messages_produced}")
        print(f"    Bytes: {producer.bytes_produced}")
        
    # Consumer statistics
    print("\n📥 Consumer Statistics:")
    
    for group_name, group in manager.consumer_groups.items():
        print(f"\n  📊 {group_name} (gen: {group.generation_id}):")
        
        total_consumed = 0
        for member in group.members.values():
            total_consumed += member.messages_consumed
            
        print(f"    Members: {len(group.members)}")
        print(f"    Total consumed: {total_consumed}")
        print(f"    Committed offsets: {len(group.committed_offsets)}")
        
    # Statistics
    print("\n📈 Platform Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Topics: {stats['topics']}")
    print(f"  Consumer Groups: {stats['consumer_groups']}")
    print(f"  Producers: {stats['producers']}")
    print(f"  Consumers: {stats['consumers']}")
    print(f"\n  Events Total: {stats['events_total']}")
    print(f"  Events Delivered: {stats['events_delivered']}")
    print(f"  Events Failed: {stats['events_failed']}")
    print(f"  DLQ Size: {stats['dlq_size']}")
    
    delivery_rate = stats['events_delivered'] / max(stats['events_total'], 1) * 100
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Event Streaming Dashboard                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Topics:                        {stats['topics']:>12}                        │")
    print(f"│ Consumer Groups:               {stats['consumer_groups']:>12}                        │")
    print(f"│ Active Consumers:              {stats['consumers']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Events Total:                  {stats['events_total']:>12}                        │")
    print(f"│ Delivery Rate:                 {delivery_rate:>11.1f}%                        │")
    print(f"│ DLQ Size:                      {stats['dlq_size']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Event Streaming Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
