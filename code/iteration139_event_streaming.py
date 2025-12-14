#!/usr/bin/env python3
"""
Server Init - Iteration 139: Event Streaming Platform
Платформа Event Streaming

Функционал:
- Event Production - производство событий
- Event Consumption - потребление событий
- Topic Management - управление топиками
- Partitioning - партиционирование
- Consumer Groups - группы потребителей
- Stream Processing - обработка потоков
- Schema Registry - реестр схем
- Dead Letter Queue - очередь недоставленных
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Awaitable
from enum import Enum
from collections import defaultdict
import uuid
import hashlib


class EventStatus(Enum):
    """Статус события"""
    PENDING = "pending"
    DELIVERED = "delivered"
    PROCESSED = "processed"
    FAILED = "failed"
    DEAD_LETTERED = "dead_lettered"


class OffsetReset(Enum):
    """Сброс оффсета"""
    EARLIEST = "earliest"
    LATEST = "latest"
    NONE = "none"


class CompressionType(Enum):
    """Тип сжатия"""
    NONE = "none"
    GZIP = "gzip"
    SNAPPY = "snappy"
    LZ4 = "lz4"
    ZSTD = "zstd"


class AckMode(Enum):
    """Режим подтверждения"""
    NONE = "none"
    LEADER = "leader"
    ALL = "all"


@dataclass
class Event:
    """Событие"""
    event_id: str
    topic: str = ""
    partition: int = 0
    
    # Content
    key: Optional[str] = None
    value: Any = None
    headers: Dict = field(default_factory=dict)
    
    # Schema
    schema_id: Optional[str] = None
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    offset: int = 0
    
    # Status
    status: EventStatus = EventStatus.PENDING


@dataclass
class Partition:
    """Партиция"""
    partition_id: int
    topic: str = ""
    
    # Offsets
    start_offset: int = 0
    end_offset: int = 0
    
    # Leader
    leader_broker: int = 0
    replicas: List[int] = field(default_factory=list)
    isr: List[int] = field(default_factory=list)  # In-Sync Replicas
    
    # Events
    events: List[Event] = field(default_factory=list)


@dataclass
class Topic:
    """Топик"""
    topic_id: str
    name: str = ""
    
    # Config
    partitions_count: int = 3
    replication_factor: int = 1
    retention_ms: int = 604800000  # 7 days
    
    # Partitions
    partitions: List[Partition] = field(default_factory=list)
    
    # Compression
    compression: CompressionType = CompressionType.NONE
    
    # Stats
    total_messages: int = 0
    bytes_in: int = 0
    bytes_out: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ConsumerGroup:
    """Группа потребителей"""
    group_id: str
    name: str = ""
    
    # Members
    members: List[str] = field(default_factory=list)
    
    # Offsets
    committed_offsets: Dict[str, Dict[int, int]] = field(default_factory=dict)  # topic -> partition -> offset
    
    # Config
    auto_commit: bool = True
    auto_commit_interval_ms: int = 5000
    offset_reset: OffsetReset = OffsetReset.LATEST
    
    # State
    state: str = "stable"  # stable, rebalancing, dead


@dataclass
class Consumer:
    """Потребитель"""
    consumer_id: str
    group_id: str = ""
    
    # Subscriptions
    subscriptions: List[str] = field(default_factory=list)
    assigned_partitions: Dict[str, List[int]] = field(default_factory=dict)
    
    # Position
    current_offsets: Dict[str, Dict[int, int]] = field(default_factory=dict)
    
    # Stats
    messages_consumed: int = 0
    last_poll: Optional[datetime] = None


@dataclass
class Producer:
    """Производитель"""
    producer_id: str
    client_id: str = ""
    
    # Config
    ack_mode: AckMode = AckMode.LEADER
    compression: CompressionType = CompressionType.NONE
    batch_size: int = 16384
    linger_ms: int = 0
    
    # Stats
    messages_sent: int = 0
    bytes_sent: int = 0
    errors: int = 0


@dataclass
class Schema:
    """Схема события"""
    schema_id: str
    subject: str = ""
    version: int = 1
    
    # Schema
    schema_type: str = "avro"  # avro, json, protobuf
    schema_definition: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DeadLetterEvent:
    """Событие в DLQ"""
    dlq_id: str
    original_event: Event = None
    
    # Error
    error_message: str = ""
    error_code: str = ""
    retry_count: int = 0
    
    # Timestamps
    failed_at: datetime = field(default_factory=datetime.now)


class TopicManager:
    """Менеджер топиков"""
    
    def __init__(self):
        self.topics: Dict[str, Topic] = {}
        
    def create(self, name: str, partitions_count: int = 3,
                replication_factor: int = 1, **kwargs) -> Topic:
        """Создание топика"""
        topic = Topic(
            topic_id=f"topic_{uuid.uuid4().hex[:8]}",
            name=name,
            partitions_count=partitions_count,
            replication_factor=replication_factor,
            **kwargs
        )
        
        # Create partitions
        for i in range(partitions_count):
            partition = Partition(
                partition_id=i,
                topic=name,
                leader_broker=i % 3,
                replicas=list(range(replication_factor)),
                isr=list(range(replication_factor))
            )
            topic.partitions.append(partition)
            
        self.topics[name] = topic
        return topic
        
    def delete(self, name: str) -> bool:
        """Удаление топика"""
        if name in self.topics:
            del self.topics[name]
            return True
        return False
        
    def get_partition(self, topic_name: str, key: str = None) -> int:
        """Получение партиции для ключа"""
        topic = self.topics.get(topic_name)
        if not topic:
            return 0
            
        if key:
            # Hash partitioning
            hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)
            return hash_value % topic.partitions_count
        else:
            # Round robin
            return topic.total_messages % topic.partitions_count


class SchemaRegistry:
    """Реестр схем"""
    
    def __init__(self):
        self.schemas: Dict[str, List[Schema]] = defaultdict(list)
        
    def register(self, subject: str, schema_type: str,
                  schema_definition: str) -> Schema:
        """Регистрация схемы"""
        versions = self.schemas.get(subject, [])
        version = len(versions) + 1
        
        schema = Schema(
            schema_id=f"schema_{uuid.uuid4().hex[:8]}",
            subject=subject,
            version=version,
            schema_type=schema_type,
            schema_definition=schema_definition
        )
        
        self.schemas[subject].append(schema)
        return schema
        
    def get_latest(self, subject: str) -> Optional[Schema]:
        """Получение последней версии"""
        versions = self.schemas.get(subject, [])
        return versions[-1] if versions else None
        
    def get_version(self, subject: str, version: int) -> Optional[Schema]:
        """Получение конкретной версии"""
        versions = self.schemas.get(subject, [])
        if 0 < version <= len(versions):
            return versions[version - 1]
        return None
        
    def check_compatibility(self, subject: str, new_schema: str) -> Dict:
        """Проверка совместимости"""
        latest = self.get_latest(subject)
        
        # Simplified compatibility check
        return {
            "compatible": True,
            "previous_version": latest.version if latest else 0
        }


class EventProducer:
    """Производитель событий"""
    
    def __init__(self, topic_manager: TopicManager, schema_registry: SchemaRegistry):
        self.topic_manager = topic_manager
        self.schema_registry = schema_registry
        self.producers: Dict[str, Producer] = {}
        
    def create_producer(self, client_id: str, **kwargs) -> Producer:
        """Создание производителя"""
        producer = Producer(
            producer_id=f"producer_{uuid.uuid4().hex[:8]}",
            client_id=client_id,
            **kwargs
        )
        self.producers[producer.producer_id] = producer
        return producer
        
    async def send(self, producer_id: str, topic_name: str,
                    value: Any, key: str = None, headers: Dict = None,
                    schema_id: str = None) -> Event:
        """Отправка события"""
        producer = self.producers.get(producer_id)
        topic = self.topic_manager.topics.get(topic_name)
        
        if not producer or not topic:
            return None
            
        # Get partition
        partition_id = self.topic_manager.get_partition(topic_name, key)
        partition = topic.partitions[partition_id]
        
        # Create event
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            topic=topic_name,
            partition=partition_id,
            key=key,
            value=value,
            headers=headers or {},
            schema_id=schema_id,
            offset=partition.end_offset,
            status=EventStatus.DELIVERED
        )
        
        # Add to partition
        partition.events.append(event)
        partition.end_offset += 1
        
        # Update stats
        topic.total_messages += 1
        topic.bytes_in += len(json.dumps(value)) if value else 0
        producer.messages_sent += 1
        
        return event
        
    async def send_batch(self, producer_id: str, topic_name: str,
                          events: List[Dict]) -> List[Event]:
        """Отправка пакета событий"""
        results = []
        
        for event_data in events:
            event = await self.send(
                producer_id,
                topic_name,
                event_data.get("value"),
                event_data.get("key"),
                event_data.get("headers")
            )
            if event:
                results.append(event)
                
        return results


class ConsumerGroupManager:
    """Менеджер групп потребителей"""
    
    def __init__(self, topic_manager: TopicManager):
        self.topic_manager = topic_manager
        self.groups: Dict[str, ConsumerGroup] = {}
        self.consumers: Dict[str, Consumer] = {}
        
    def create_group(self, name: str, **kwargs) -> ConsumerGroup:
        """Создание группы"""
        group = ConsumerGroup(
            group_id=f"group_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        self.groups[group.group_id] = group
        return group
        
    def join_group(self, group_id: str, subscriptions: List[str]) -> Consumer:
        """Присоединение к группе"""
        group = self.groups.get(group_id)
        if not group:
            return None
            
        consumer = Consumer(
            consumer_id=f"consumer_{uuid.uuid4().hex[:8]}",
            group_id=group_id,
            subscriptions=subscriptions
        )
        
        group.members.append(consumer.consumer_id)
        self.consumers[consumer.consumer_id] = consumer
        
        # Trigger rebalance
        self._rebalance(group_id)
        
        return consumer
        
    def leave_group(self, consumer_id: str) -> bool:
        """Покидание группы"""
        consumer = self.consumers.get(consumer_id)
        if not consumer:
            return False
            
        group = self.groups.get(consumer.group_id)
        if group:
            group.members.remove(consumer_id)
            self._rebalance(consumer.group_id)
            
        del self.consumers[consumer_id]
        return True
        
    def _rebalance(self, group_id: str):
        """Перебалансировка"""
        group = self.groups.get(group_id)
        if not group:
            return
            
        group.state = "rebalancing"
        
        # Get all partitions for subscribed topics
        all_partitions = []
        consumers = [self.consumers[cid] for cid in group.members]
        
        for consumer in consumers:
            consumer.assigned_partitions = {}
            for topic_name in consumer.subscriptions:
                topic = self.topic_manager.topics.get(topic_name)
                if topic:
                    for p in topic.partitions:
                        all_partitions.append((topic_name, p.partition_id))
                        
        # Round-robin assignment
        for i, (topic, partition) in enumerate(all_partitions):
            consumer = consumers[i % len(consumers)]
            if topic not in consumer.assigned_partitions:
                consumer.assigned_partitions[topic] = []
            consumer.assigned_partitions[topic].append(partition)
            
        group.state = "stable"
        
    async def poll(self, consumer_id: str, max_records: int = 100,
                    timeout_ms: int = 1000) -> List[Event]:
        """Получение событий"""
        consumer = self.consumers.get(consumer_id)
        if not consumer:
            return []
            
        events = []
        
        for topic_name, partitions in consumer.assigned_partitions.items():
            topic = self.topic_manager.topics.get(topic_name)
            if not topic:
                continue
                
            for partition_id in partitions:
                partition = topic.partitions[partition_id]
                
                # Get current offset
                if topic_name not in consumer.current_offsets:
                    consumer.current_offsets[topic_name] = {}
                current_offset = consumer.current_offsets[topic_name].get(partition_id, 0)
                
                # Get events from offset
                for event in partition.events[current_offset:current_offset + max_records]:
                    events.append(event)
                    consumer.current_offsets[topic_name][partition_id] = event.offset + 1
                    
                if len(events) >= max_records:
                    break
                    
        consumer.messages_consumed += len(events)
        consumer.last_poll = datetime.now()
        
        return events
        
    def commit(self, consumer_id: str, offsets: Dict[str, Dict[int, int]] = None):
        """Фиксация оффсетов"""
        consumer = self.consumers.get(consumer_id)
        if not consumer:
            return
            
        group = self.groups.get(consumer.group_id)
        if not group:
            return
            
        # Use provided offsets or current position
        commit_offsets = offsets or consumer.current_offsets
        
        for topic, partitions in commit_offsets.items():
            if topic not in group.committed_offsets:
                group.committed_offsets[topic] = {}
            for partition, offset in partitions.items():
                group.committed_offsets[topic][partition] = offset


class StreamProcessor:
    """Процессор потоков"""
    
    def __init__(self, consumer_manager: ConsumerGroupManager, producer: EventProducer):
        self.consumer_manager = consumer_manager
        self.producer = producer
        self.processors: Dict[str, Callable] = {}
        
    def add_processor(self, name: str, processor: Callable):
        """Добавление процессора"""
        self.processors[name] = processor
        
    async def process(self, consumer_id: str, processor_name: str,
                       output_topic: str = None) -> Dict:
        """Обработка потока"""
        processor = self.processors.get(processor_name)
        if not processor:
            return {"error": "Processor not found"}
            
        events = await self.consumer_manager.poll(consumer_id)
        processed = 0
        errors = 0
        
        for event in events:
            try:
                result = await processor(event)
                
                if output_topic and result:
                    # Get producer
                    producer_id = list(self.producer.producers.keys())[0]
                    await self.producer.send(producer_id, output_topic, result)
                    
                event.status = EventStatus.PROCESSED
                processed += 1
                
            except Exception as e:
                event.status = EventStatus.FAILED
                errors += 1
                
        # Commit offsets
        self.consumer_manager.commit(consumer_id)
        
        return {
            "processed": processed,
            "errors": errors,
            "total": len(events)
        }


class DeadLetterQueue:
    """Очередь недоставленных сообщений"""
    
    def __init__(self, topic_manager: TopicManager):
        self.topic_manager = topic_manager
        self.dlq_events: List[DeadLetterEvent] = []
        
    def send_to_dlq(self, event: Event, error_message: str,
                     error_code: str = "PROCESSING_ERROR") -> DeadLetterEvent:
        """Отправка в DLQ"""
        dlq_event = DeadLetterEvent(
            dlq_id=f"dlq_{uuid.uuid4().hex[:8]}",
            original_event=event,
            error_message=error_message,
            error_code=error_code,
            retry_count=0
        )
        
        event.status = EventStatus.DEAD_LETTERED
        self.dlq_events.append(dlq_event)
        
        return dlq_event
        
    def get_dlq_events(self, topic: str = None) -> List[DeadLetterEvent]:
        """Получение событий из DLQ"""
        if topic:
            return [e for e in self.dlq_events if e.original_event.topic == topic]
        return self.dlq_events
        
    async def retry(self, dlq_id: str, producer: EventProducer,
                     producer_id: str) -> Event:
        """Повтор отправки"""
        dlq_event = next((e for e in self.dlq_events if e.dlq_id == dlq_id), None)
        if not dlq_event:
            return None
            
        event = dlq_event.original_event
        
        # Retry
        new_event = await producer.send(
            producer_id,
            event.topic,
            event.value,
            event.key,
            event.headers
        )
        
        if new_event:
            dlq_event.retry_count += 1
            self.dlq_events.remove(dlq_event)
            
        return new_event


class EventStreamingPlatform:
    """Платформа Event Streaming"""
    
    def __init__(self):
        self.topic_manager = TopicManager()
        self.schema_registry = SchemaRegistry()
        self.producer = EventProducer(self.topic_manager, self.schema_registry)
        self.consumer_manager = ConsumerGroupManager(self.topic_manager)
        self.stream_processor = StreamProcessor(self.consumer_manager, self.producer)
        self.dlq = DeadLetterQueue(self.topic_manager)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        topics = list(self.topic_manager.topics.values())
        
        return {
            "topics": len(topics),
            "total_partitions": sum(t.partitions_count for t in topics),
            "total_messages": sum(t.total_messages for t in topics),
            "producers": len(self.producer.producers),
            "consumer_groups": len(self.consumer_manager.groups),
            "consumers": len(self.consumer_manager.consumers),
            "schemas": sum(len(v) for v in self.schema_registry.schemas.values()),
            "dlq_events": len(self.dlq.dlq_events)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 139: Event Streaming Platform")
    print("=" * 60)
    
    async def demo():
        platform = EventStreamingPlatform()
        print("✓ Event Streaming Platform created")
        
        # Create topics
        print("\n📋 Creating Topics...")
        
        topics_config = [
            ("orders", 6, 3),
            ("payments", 3, 3),
            ("notifications", 3, 2),
            ("user-events", 6, 3),
            ("audit-log", 1, 3)
        ]
        
        created_topics = []
        for name, partitions, replication in topics_config:
            topic = platform.topic_manager.create(
                name, partitions, replication,
                compression=CompressionType.SNAPPY
            )
            created_topics.append(topic)
            print(f"  ✓ {name}: {partitions} partitions, RF={replication}")
            
        # Register schemas
        print("\n📜 Registering Schemas...")
        
        schemas = [
            ("orders-value", "avro", '{"type":"record","name":"Order","fields":[{"name":"id","type":"string"},{"name":"amount","type":"double"}]}'),
            ("payments-value", "avro", '{"type":"record","name":"Payment","fields":[{"name":"id","type":"string"},{"name":"status","type":"string"}]}'),
            ("user-events-value", "json", '{"type":"object","properties":{"user_id":{"type":"string"},"action":{"type":"string"}}}')
        ]
        
        for subject, schema_type, definition in schemas:
            schema = platform.schema_registry.register(subject, schema_type, definition)
            print(f"  ✓ {subject} v{schema.version} ({schema_type})")
            
        # Create producers
        print("\n📤 Creating Producers...")
        
        producer1 = platform.producer.create_producer(
            "order-service",
            ack_mode=AckMode.ALL,
            compression=CompressionType.SNAPPY
        )
        
        producer2 = platform.producer.create_producer(
            "payment-service",
            ack_mode=AckMode.LEADER
        )
        
        print(f"  ✓ {producer1.client_id} (acks={producer1.ack_mode.value})")
        print(f"  ✓ {producer2.client_id} (acks={producer2.ack_mode.value})")
        
        # Send events
        print("\n📨 Sending Events...")
        
        # Single events
        for i in range(10):
            event = await platform.producer.send(
                producer1.producer_id,
                "orders",
                {"order_id": f"ORD-{i:04d}", "amount": 99.99 + i, "customer": f"CUST-{i:03d}"},
                key=f"customer-{i % 3}"
            )
            
        print(f"  ✓ Sent 10 order events")
        
        # Batch events
        payment_events = [
            {"key": f"order-{i}", "value": {"payment_id": f"PAY-{i:04d}", "status": "completed"}}
            for i in range(5)
        ]
        
        batch_results = await platform.producer.send_batch(
            producer2.producer_id,
            "payments",
            payment_events
        )
        
        print(f"  ✓ Sent {len(batch_results)} payment events (batch)")
        
        # Create consumer groups
        print("\n👥 Creating Consumer Groups...")
        
        group1 = platform.consumer_manager.create_group(
            "order-processors",
            auto_commit=True,
            offset_reset=OffsetReset.EARLIEST
        )
        
        group2 = platform.consumer_manager.create_group(
            "analytics-consumers",
            auto_commit=False,
            offset_reset=OffsetReset.LATEST
        )
        
        print(f"  ✓ {group1.name} (auto_commit={group1.auto_commit})")
        print(f"  ✓ {group2.name} (auto_commit={group2.auto_commit})")
        
        # Add consumers
        print("\n🔌 Adding Consumers...")
        
        consumer1 = platform.consumer_manager.join_group(group1.group_id, ["orders"])
        consumer2 = platform.consumer_manager.join_group(group1.group_id, ["orders"])
        consumer3 = platform.consumer_manager.join_group(group2.group_id, ["orders", "payments"])
        
        print(f"  ✓ Consumer 1 assigned: {consumer1.assigned_partitions}")
        print(f"  ✓ Consumer 2 assigned: {consumer2.assigned_partitions}")
        print(f"  ✓ Consumer 3 assigned: {consumer3.assigned_partitions}")
        
        # Poll events
        print("\n📥 Polling Events...")
        
        events1 = await platform.consumer_manager.poll(consumer1.consumer_id, max_records=5)
        events2 = await platform.consumer_manager.poll(consumer2.consumer_id, max_records=5)
        
        print(f"  Consumer 1 received: {len(events1)} events")
        print(f"  Consumer 2 received: {len(events2)} events")
        
        for event in events1[:2]:
            print(f"    - {event.event_id}: {event.value}")
            
        # Commit offsets
        print("\n✅ Committing Offsets...")
        
        platform.consumer_manager.commit(consumer1.consumer_id)
        platform.consumer_manager.commit(consumer2.consumer_id)
        
        print(f"  ✓ Committed offsets for {group1.name}")
        
        # Stream processing
        print("\n⚡ Stream Processing...")
        
        async def enrich_order(event: Event) -> Dict:
            """Обогащение заказа"""
            data = event.value
            data["enriched"] = True
            data["processed_at"] = datetime.now().isoformat()
            return data
            
        platform.stream_processor.add_processor("enrich", enrich_order)
        
        # Create output topic
        platform.topic_manager.create("enriched-orders", 3, 2)
        
        result = await platform.stream_processor.process(
            consumer3.consumer_id,
            "enrich",
            "enriched-orders"
        )
        
        print(f"  ✓ Processed: {result['processed']}/{result['total']}")
        
        # Dead Letter Queue
        print("\n💀 Dead Letter Queue Demo...")
        
        # Simulate failed event
        failed_event = Event(
            event_id="evt_failed123",
            topic="orders",
            value={"invalid": "data"},
            status=EventStatus.FAILED
        )
        
        dlq_event = platform.dlq.send_to_dlq(
            failed_event,
            "Schema validation failed",
            "SCHEMA_ERROR"
        )
        
        print(f"  ✓ Event sent to DLQ: {dlq_event.dlq_id}")
        print(f"    Error: {dlq_event.error_message}")
        
        # Topic stats
        print("\n📊 Topic Statistics:")
        
        for topic in created_topics:
            print(f"\n  {topic.name}:")
            print(f"    Partitions: {topic.partitions_count}")
            print(f"    Messages: {topic.total_messages}")
            print(f"    Compression: {topic.compression.value}")
            
            # Partition details
            for p in topic.partitions[:2]:
                print(f"    Partition {p.partition_id}: offset={p.end_offset}, leader={p.leader_broker}")
                
        # Consumer group status
        print("\n👥 Consumer Group Status:")
        
        for group in platform.consumer_manager.groups.values():
            print(f"\n  {group.name}:")
            print(f"    State: {group.state}")
            print(f"    Members: {len(group.members)}")
            print(f"    Committed Offsets: {group.committed_offsets}")
            
        # Schema versions
        print("\n📜 Schema Versions:")
        
        for subject, versions in platform.schema_registry.schemas.items():
            print(f"  {subject}: {len(versions)} version(s)")
            latest = versions[-1]
            print(f"    Latest: v{latest.version} ({latest.schema_type})")
            
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Topics: {stats['topics']}")
        print(f"  Total Partitions: {stats['total_partitions']}")
        print(f"  Total Messages: {stats['total_messages']}")
        print(f"  Producers: {stats['producers']}")
        print(f"  Consumer Groups: {stats['consumer_groups']}")
        print(f"  Consumers: {stats['consumers']}")
        print(f"  Schemas: {stats['schemas']}")
        print(f"  DLQ Events: {stats['dlq_events']}")
        
        # Dashboard
        print("\n📋 Event Streaming Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │              Event Streaming Overview                       │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Topics:             {stats['topics']:>10}                        │")
        print(f"  │ Partitions:         {stats['total_partitions']:>10}                        │")
        print(f"  │ Total Messages:     {stats['total_messages']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Producers:          {stats['producers']:>10}                        │")
        print(f"  │ Consumer Groups:    {stats['consumer_groups']:>10}                        │")
        print(f"  │ Consumers:          {stats['consumers']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Schemas:            {stats['schemas']:>10}                        │")
        print(f"  │ DLQ Events:         {stats['dlq_events']:>10}                        │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Event Streaming Platform initialized!")
    print("=" * 60)
