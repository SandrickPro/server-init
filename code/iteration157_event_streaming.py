#!/usr/bin/env python3
"""
Server Init - Iteration 157: Event Streaming Platform
Платформа потоковой обработки событий

Функционал:
- Event Production - генерация событий
- Event Consumption - потребление событий
- Stream Processing - потоковая обработка
- Partitioning - партиционирование
- Consumer Groups - группы потребителей
- Dead Letter Queue - очередь недоставленных сообщений
- Schema Registry - реестр схем
- Event Replay - воспроизведение событий
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid
import hashlib


class EventStatus(Enum):
    """Статус события"""
    PENDING = "pending"
    DELIVERED = "delivered"
    ACKNOWLEDGED = "acknowledged"
    FAILED = "failed"
    DEAD_LETTERED = "dead_lettered"


class ConsumerState(Enum):
    """Состояние потребителя"""
    IDLE = "idle"
    CONSUMING = "consuming"
    PAUSED = "paused"
    DISCONNECTED = "disconnected"


class SchemaType(Enum):
    """Тип схемы"""
    JSON = "json"
    AVRO = "avro"
    PROTOBUF = "protobuf"


class ProcessingStrategy(Enum):
    """Стратегия обработки"""
    AT_LEAST_ONCE = "at_least_once"
    AT_MOST_ONCE = "at_most_once"
    EXACTLY_ONCE = "exactly_once"


class PartitionStrategy(Enum):
    """Стратегия партиционирования"""
    ROUND_ROBIN = "round_robin"
    KEY_HASH = "key_hash"
    RANDOM = "random"


@dataclass
class Event:
    """Событие"""
    event_id: str
    topic: str = ""
    
    # Key and value
    key: str = ""
    value: Dict = field(default_factory=dict)
    
    # Headers
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Partition
    partition: int = 0
    offset: int = 0
    
    # Status
    status: EventStatus = EventStatus.PENDING
    
    # Retry
    attempts: int = 0
    max_attempts: int = 3
    
    # Timestamps
    timestamp: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None


@dataclass
class Topic:
    """Топик"""
    topic_id: str
    name: str = ""
    
    # Partitions
    partitions: int = 3
    replication_factor: int = 1
    
    # Retention
    retention_ms: int = 604800000  # 7 days
    retention_bytes: int = -1  # unlimited
    
    # Schema
    schema_id: Optional[str] = None
    
    # Settings
    cleanup_policy: str = "delete"  # delete, compact
    compression: str = "none"  # none, gzip, snappy, lz4
    
    # Statistics
    message_count: int = 0
    bytes_in: int = 0
    bytes_out: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Partition:
    """Партиция"""
    partition_id: int
    topic: str = ""
    
    # Offsets
    start_offset: int = 0
    end_offset: int = 0
    
    # Leader/Replicas
    leader: str = ""
    replicas: List[str] = field(default_factory=list)
    in_sync_replicas: List[str] = field(default_factory=list)
    
    # Events storage
    events: List[Event] = field(default_factory=list)


@dataclass
class Consumer:
    """Потребитель"""
    consumer_id: str
    group_id: str = ""
    
    # Subscriptions
    topics: List[str] = field(default_factory=list)
    assigned_partitions: Dict[str, List[int]] = field(default_factory=dict)
    
    # State
    state: ConsumerState = ConsumerState.IDLE
    
    # Offsets
    committed_offsets: Dict[str, Dict[int, int]] = field(default_factory=dict)
    
    # Processing
    strategy: ProcessingStrategy = ProcessingStrategy.AT_LEAST_ONCE
    
    # Handler
    handler: Optional[Callable] = None
    
    # Statistics
    events_consumed: int = 0
    events_failed: int = 0
    
    # Timing
    last_poll: Optional[datetime] = None
    last_commit: Optional[datetime] = None


@dataclass
class ConsumerGroup:
    """Группа потребителей"""
    group_id: str
    
    # Members
    consumers: Dict[str, Consumer] = field(default_factory=dict)
    
    # Subscriptions
    topics: List[str] = field(default_factory=list)
    
    # Partition assignment
    partition_assignment: Dict[str, Dict[str, List[int]]] = field(default_factory=dict)
    
    # Offsets
    committed_offsets: Dict[str, Dict[int, int]] = field(default_factory=dict)
    
    # Statistics
    lag: int = 0
    
    # Rebalance
    generation: int = 0
    last_rebalance: Optional[datetime] = None


@dataclass
class Schema:
    """Схема"""
    schema_id: str
    subject: str = ""
    
    # Version
    version: int = 1
    
    # Type
    schema_type: SchemaType = SchemaType.JSON
    
    # Definition
    schema_def: Dict = field(default_factory=dict)
    
    # Compatibility
    compatibility: str = "BACKWARD"  # BACKWARD, FORWARD, FULL, NONE
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DeadLetter:
    """Недоставленное сообщение"""
    dead_letter_id: str
    
    # Original event
    original_event: Event = None
    
    # Error
    error: str = ""
    error_type: str = ""
    
    # Source
    source_topic: str = ""
    consumer_group: str = ""
    
    # Retry
    retryable: bool = True
    retried: bool = False
    
    # Timestamp
    dead_at: datetime = field(default_factory=datetime.now)


class TopicManager:
    """Менеджер топиков"""
    
    def __init__(self):
        self.topics: Dict[str, Topic] = {}
        self.partitions: Dict[str, Dict[int, Partition]] = {}
        
    def create_topic(self, name: str, partitions: int = 3,
                      **kwargs) -> Topic:
        """Создание топика"""
        topic = Topic(
            topic_id=f"topic_{uuid.uuid4().hex[:8]}",
            name=name,
            partitions=partitions,
            **kwargs
        )
        
        self.topics[name] = topic
        self.partitions[name] = {}
        
        # Create partitions
        for i in range(partitions):
            partition = Partition(
                partition_id=i,
                topic=name
            )
            self.partitions[name][i] = partition
            
        return topic
        
    def get_partition(self, topic: str, key: str = None,
                       strategy: PartitionStrategy = PartitionStrategy.KEY_HASH) -> int:
        """Получение партиции"""
        if topic not in self.topics:
            return 0
            
        num_partitions = self.topics[topic].partitions
        
        if strategy == PartitionStrategy.ROUND_ROBIN:
            # Simple round-robin based on message count
            return self.topics[topic].message_count % num_partitions
        elif strategy == PartitionStrategy.KEY_HASH:
            if key:
                hash_val = int(hashlib.md5(key.encode()).hexdigest(), 16)
                return hash_val % num_partitions
            return 0
        else:
            import random
            return random.randint(0, num_partitions - 1)


class Producer:
    """Продюсер событий"""
    
    def __init__(self, topic_manager: TopicManager):
        self.topic_manager = topic_manager
        self.events_produced: int = 0
        
    async def send(self, topic: str, value: Dict, key: str = None,
                    headers: Dict = None,
                    partition: int = None) -> Event:
        """Отправка события"""
        if topic not in self.topic_manager.topics:
            raise ValueError(f"Topic {topic} not found")
            
        # Determine partition
        if partition is None:
            partition = self.topic_manager.get_partition(topic, key)
            
        # Get partition
        part = self.topic_manager.partitions[topic][partition]
        
        # Create event
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            topic=topic,
            key=key or "",
            value=value,
            headers=headers or {},
            partition=partition,
            offset=part.end_offset,
            status=EventStatus.DELIVERED
        )
        
        # Add to partition
        part.events.append(event)
        part.end_offset += 1
        
        # Update topic stats
        self.topic_manager.topics[topic].message_count += 1
        self.topic_manager.topics[topic].bytes_in += len(json.dumps(value))
        
        self.events_produced += 1
        
        return event
        
    async def send_batch(self, topic: str, events: List[Dict]) -> List[Event]:
        """Пакетная отправка"""
        results = []
        for evt_data in events:
            event = await self.send(
                topic,
                evt_data.get("value", {}),
                evt_data.get("key"),
                evt_data.get("headers")
            )
            results.append(event)
        return results


class ConsumerManager:
    """Менеджер потребителей"""
    
    def __init__(self, topic_manager: TopicManager):
        self.topic_manager = topic_manager
        self.groups: Dict[str, ConsumerGroup] = {}
        self.dead_letters: List[DeadLetter] = []
        
    def create_group(self, group_id: str) -> ConsumerGroup:
        """Создание группы"""
        group = ConsumerGroup(group_id=group_id)
        self.groups[group_id] = group
        return group
        
    def create_consumer(self, group_id: str, topics: List[str],
                         handler: Callable = None,
                         **kwargs) -> Consumer:
        """Создание потребителя"""
        if group_id not in self.groups:
            self.create_group(group_id)
            
        consumer = Consumer(
            consumer_id=f"con_{uuid.uuid4().hex[:8]}",
            group_id=group_id,
            topics=topics,
            handler=handler,
            **kwargs
        )
        
        group = self.groups[group_id]
        group.consumers[consumer.consumer_id] = consumer
        
        # Add topics to group
        for topic in topics:
            if topic not in group.topics:
                group.topics.append(topic)
                
        # Trigger rebalance
        self._rebalance(group_id)
        
        return consumer
        
    def _rebalance(self, group_id: str):
        """Ребалансировка партиций"""
        if group_id not in self.groups:
            return
            
        group = self.groups[group_id]
        group.generation += 1
        group.last_rebalance = datetime.now()
        
        # Clear assignments
        for consumer in group.consumers.values():
            consumer.assigned_partitions = {}
            
        # Round-robin assignment
        consumer_list = list(group.consumers.values())
        if not consumer_list:
            return
            
        for topic in group.topics:
            if topic not in self.topic_manager.topics:
                continue
                
            num_partitions = self.topic_manager.topics[topic].partitions
            
            for i in range(num_partitions):
                consumer = consumer_list[i % len(consumer_list)]
                
                if topic not in consumer.assigned_partitions:
                    consumer.assigned_partitions[topic] = []
                consumer.assigned_partitions[topic].append(i)
                
    async def poll(self, consumer: Consumer, max_events: int = 100,
                    timeout_ms: int = 1000) -> List[Event]:
        """Получение событий"""
        consumer.state = ConsumerState.CONSUMING
        consumer.last_poll = datetime.now()
        
        events = []
        
        for topic, partitions in consumer.assigned_partitions.items():
            for partition_id in partitions:
                if topic not in self.topic_manager.partitions:
                    continue
                    
                partition = self.topic_manager.partitions[topic][partition_id]
                
                # Get committed offset
                committed = consumer.committed_offsets.get(topic, {}).get(partition_id, 0)
                
                # Get events from offset
                for event in partition.events:
                    if event.offset >= committed:
                        events.append(event)
                        if len(events) >= max_events:
                            break
                            
        return events
        
    async def commit(self, consumer: Consumer, events: List[Event]):
        """Коммит оффсетов"""
        for event in events:
            topic = event.topic
            partition = event.partition
            offset = event.offset + 1
            
            if topic not in consumer.committed_offsets:
                consumer.committed_offsets[topic] = {}
            consumer.committed_offsets[topic][partition] = offset
            
            # Update group offsets
            group = self.groups.get(consumer.group_id)
            if group:
                if topic not in group.committed_offsets:
                    group.committed_offsets[topic] = {}
                group.committed_offsets[topic][partition] = offset
                
        consumer.last_commit = datetime.now()
        
    async def process_event(self, consumer: Consumer, event: Event) -> bool:
        """Обработка события"""
        try:
            if consumer.handler:
                await consumer.handler(event)
                
            event.status = EventStatus.ACKNOWLEDGED
            event.processed_at = datetime.now()
            consumer.events_consumed += 1
            
            return True
            
        except Exception as e:
            event.attempts += 1
            consumer.events_failed += 1
            
            if event.attempts >= event.max_attempts:
                self._send_to_dead_letter(event, str(e), consumer)
                event.status = EventStatus.DEAD_LETTERED
            else:
                event.status = EventStatus.FAILED
                
            return False
            
    def _send_to_dead_letter(self, event: Event, error: str, consumer: Consumer):
        """Отправка в DLQ"""
        dead_letter = DeadLetter(
            dead_letter_id=f"dlq_{uuid.uuid4().hex[:8]}",
            original_event=event,
            error=error,
            error_type=type(error).__name__,
            source_topic=event.topic,
            consumer_group=consumer.group_id
        )
        self.dead_letters.append(dead_letter)


class SchemaRegistry:
    """Реестр схем"""
    
    def __init__(self):
        self.schemas: Dict[str, Dict[int, Schema]] = {}
        self.latest_versions: Dict[str, int] = {}
        
    def register_schema(self, subject: str, schema_def: Dict,
                         schema_type: SchemaType = SchemaType.JSON) -> Schema:
        """Регистрация схемы"""
        if subject not in self.schemas:
            self.schemas[subject] = {}
            self.latest_versions[subject] = 0
            
        version = self.latest_versions[subject] + 1
        
        schema = Schema(
            schema_id=f"sch_{uuid.uuid4().hex[:8]}",
            subject=subject,
            version=version,
            schema_type=schema_type,
            schema_def=schema_def
        )
        
        self.schemas[subject][version] = schema
        self.latest_versions[subject] = version
        
        return schema
        
    def get_schema(self, subject: str, version: int = None) -> Optional[Schema]:
        """Получение схемы"""
        if subject not in self.schemas:
            return None
            
        if version is None:
            version = self.latest_versions[subject]
            
        return self.schemas[subject].get(version)
        
    def validate(self, subject: str, data: Dict) -> tuple:
        """Валидация данных"""
        schema = self.get_schema(subject)
        
        if not schema:
            return True, "No schema registered"
            
        # Simple JSON schema validation
        schema_def = schema.schema_def
        required = schema_def.get("required", [])
        properties = schema_def.get("properties", {})
        
        for field in required:
            if field not in data:
                return False, f"Missing required field: {field}"
                
        for field, value in data.items():
            if field in properties:
                expected_type = properties[field].get("type")
                if expected_type == "string" and not isinstance(value, str):
                    return False, f"Field {field} should be string"
                elif expected_type == "number" and not isinstance(value, (int, float)):
                    return False, f"Field {field} should be number"
                elif expected_type == "boolean" and not isinstance(value, bool):
                    return False, f"Field {field} should be boolean"
                    
        return True, "Valid"


class StreamProcessor:
    """Потоковый процессор"""
    
    def __init__(self, topic_manager: TopicManager, producer: Producer):
        self.topic_manager = topic_manager
        self.producer = producer
        self.processors: Dict[str, Callable] = {}
        
    def map(self, source_topic: str, target_topic: str,
             transform: Callable) -> str:
        """Map операция"""
        processor_id = f"map_{uuid.uuid4().hex[:8]}"
        
        async def processor(event: Event):
            result = transform(event.value)
            await self.producer.send(target_topic, result, event.key)
            
        self.processors[processor_id] = processor
        return processor_id
        
    def filter(self, source_topic: str, target_topic: str,
                predicate: Callable) -> str:
        """Filter операция"""
        processor_id = f"filter_{uuid.uuid4().hex[:8]}"
        
        async def processor(event: Event):
            if predicate(event.value):
                await self.producer.send(target_topic, event.value, event.key)
                
        self.processors[processor_id] = processor
        return processor_id
        
    def aggregate(self, source_topic: str, target_topic: str,
                   aggregator: Callable, window_size: int = 60) -> str:
        """Aggregate операция"""
        processor_id = f"agg_{uuid.uuid4().hex[:8]}"
        
        buffer = []
        last_flush = datetime.now()
        
        async def processor(event: Event):
            nonlocal buffer, last_flush
            
            buffer.append(event.value)
            
            if (datetime.now() - last_flush).seconds >= window_size:
                result = aggregator(buffer)
                await self.producer.send(target_topic, result)
                buffer = []
                last_flush = datetime.now()
                
        self.processors[processor_id] = processor
        return processor_id


class EventReplay:
    """Воспроизведение событий"""
    
    def __init__(self, topic_manager: TopicManager, producer: Producer):
        self.topic_manager = topic_manager
        self.producer = producer
        
    async def replay(self, source_topic: str, target_topic: str,
                      start_offset: int = 0, end_offset: int = None,
                      start_time: datetime = None,
                      end_time: datetime = None) -> int:
        """Воспроизведение событий"""
        if source_topic not in self.topic_manager.partitions:
            return 0
            
        replayed = 0
        
        for partition_id, partition in self.topic_manager.partitions[source_topic].items():
            for event in partition.events:
                # Filter by offset
                if event.offset < start_offset:
                    continue
                if end_offset and event.offset > end_offset:
                    continue
                    
                # Filter by time
                if start_time and event.timestamp < start_time:
                    continue
                if end_time and event.timestamp > end_time:
                    continue
                    
                # Replay to target
                await self.producer.send(
                    target_topic,
                    event.value,
                    event.key,
                    event.headers
                )
                replayed += 1
                
        return replayed


class EventStreamingPlatform:
    """Платформа потоковой обработки"""
    
    def __init__(self):
        self.topic_manager = TopicManager()
        self.producer = Producer(self.topic_manager)
        self.consumer_manager = ConsumerManager(self.topic_manager)
        self.schema_registry = SchemaRegistry()
        self.stream_processor = StreamProcessor(self.topic_manager, self.producer)
        self.event_replay = EventReplay(self.topic_manager, self.producer)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        topics = list(self.topic_manager.topics.values())
        groups = list(self.consumer_manager.groups.values())
        
        total_messages = sum(t.message_count for t in topics)
        total_consumers = sum(len(g.consumers) for g in groups)
        
        return {
            "topics": len(topics),
            "partitions": sum(t.partitions for t in topics),
            "consumer_groups": len(groups),
            "consumers": total_consumers,
            "total_messages": total_messages,
            "dead_letters": len(self.consumer_manager.dead_letters),
            "schemas": sum(len(s) for s in self.schema_registry.schemas.values()),
            "processors": len(self.stream_processor.processors)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 157: Event Streaming Platform")
    print("=" * 60)
    
    async def demo():
        platform = EventStreamingPlatform()
        print("✓ Event Streaming Platform created")
        
        # Create topics
        print("\n📋 Creating Topics...")
        
        orders_topic = platform.topic_manager.create_topic(
            name="orders",
            partitions=3,
            retention_ms=604800000  # 7 days
        )
        print(f"  ✓ {orders_topic.name} ({orders_topic.partitions} partitions)")
        
        payments_topic = platform.topic_manager.create_topic(
            name="payments",
            partitions=3
        )
        print(f"  ✓ {payments_topic.name} ({payments_topic.partitions} partitions)")
        
        notifications_topic = platform.topic_manager.create_topic(
            name="notifications",
            partitions=2
        )
        print(f"  ✓ {notifications_topic.name} ({notifications_topic.partitions} partitions)")
        
        processed_orders_topic = platform.topic_manager.create_topic(
            name="processed-orders",
            partitions=3
        )
        print(f"  ✓ {processed_orders_topic.name} ({processed_orders_topic.partitions} partitions)")
        
        # Register schemas
        print("\n📝 Registering Schemas...")
        
        order_schema = platform.schema_registry.register_schema(
            subject="orders-value",
            schema_def={
                "type": "object",
                "required": ["order_id", "customer_id", "amount"],
                "properties": {
                    "order_id": {"type": "string"},
                    "customer_id": {"type": "string"},
                    "amount": {"type": "number"},
                    "status": {"type": "string"}
                }
            }
        )
        print(f"  ✓ {order_schema.subject} v{order_schema.version}")
        
        payment_schema = platform.schema_registry.register_schema(
            subject="payments-value",
            schema_def={
                "type": "object",
                "required": ["payment_id", "order_id", "amount"],
                "properties": {
                    "payment_id": {"type": "string"},
                    "order_id": {"type": "string"},
                    "amount": {"type": "number"},
                    "method": {"type": "string"}
                }
            }
        )
        print(f"  ✓ {payment_schema.subject} v{payment_schema.version}")
        
        # Produce events
        print("\n📤 Producing Events...")
        
        orders = [
            {"order_id": "ORD001", "customer_id": "C100", "amount": 150.00, "status": "pending"},
            {"order_id": "ORD002", "customer_id": "C101", "amount": 299.99, "status": "pending"},
            {"order_id": "ORD003", "customer_id": "C100", "amount": 75.50, "status": "pending"},
            {"order_id": "ORD004", "customer_id": "C102", "amount": 500.00, "status": "pending"},
            {"order_id": "ORD005", "customer_id": "C103", "amount": 1200.00, "status": "pending"},
        ]
        
        for order in orders:
            # Validate schema
            valid, msg = platform.schema_registry.validate("orders-value", order)
            
            if valid:
                event = await platform.producer.send(
                    "orders",
                    order,
                    key=order["customer_id"],
                    headers={"source": "order-service"}
                )
                print(f"  ✓ {order['order_id']} → partition {event.partition}, offset {event.offset}")
            else:
                print(f"  ✗ {order['order_id']}: {msg}")
                
        # Create consumer group
        print("\n👥 Creating Consumer Group...")
        
        async def order_handler(event: Event):
            """Обработчик заказов"""
            await asyncio.sleep(0.05)  # Simulate processing
            
        consumer = platform.consumer_manager.create_consumer(
            group_id="order-processing",
            topics=["orders"],
            handler=order_handler,
            strategy=ProcessingStrategy.AT_LEAST_ONCE
        )
        
        print(f"\n  Consumer: {consumer.consumer_id}")
        print(f"  Group: {consumer.group_id}")
        print(f"  Strategy: {consumer.strategy.value}")
        print(f"  Assigned partitions: {consumer.assigned_partitions}")
        
        # Create another consumer for scaling
        consumer2 = platform.consumer_manager.create_consumer(
            group_id="order-processing",
            topics=["orders"],
            handler=order_handler
        )
        
        print(f"\n  Added consumer: {consumer2.consumer_id}")
        print(f"  Consumer 1 partitions: {consumer.assigned_partitions}")
        print(f"  Consumer 2 partitions: {consumer2.assigned_partitions}")
        
        # Poll and process events
        print("\n⚙️ Processing Events...")
        
        events = await platform.consumer_manager.poll(consumer, max_events=10)
        print(f"\n  Polled {len(events)} events")
        
        processed = 0
        for event in events:
            success = await platform.consumer_manager.process_event(consumer, event)
            if success:
                processed += 1
                
        print(f"  Processed: {processed}")
        print(f"  Consumer consumed: {consumer.events_consumed}")
        
        # Commit offsets
        await platform.consumer_manager.commit(consumer, events)
        print(f"  Committed offsets: {consumer.committed_offsets}")
        
        # Stream processing
        print("\n🔄 Stream Processing...")
        
        # Map: Add processing timestamp
        def add_timestamp(value: Dict) -> Dict:
            value["processed_at"] = datetime.now().isoformat()
            return value
            
        map_processor = platform.stream_processor.map(
            "orders",
            "processed-orders",
            add_timestamp
        )
        print(f"  ✓ Map processor: {map_processor}")
        
        # Filter: High value orders
        def is_high_value(value: Dict) -> bool:
            return value.get("amount", 0) > 200
            
        filter_processor = platform.stream_processor.filter(
            "orders",
            "high-value-orders",
            is_high_value
        )
        print(f"  ✓ Filter processor: {filter_processor}")
        
        # Aggregate: Sum amounts
        def sum_amounts(values: List[Dict]) -> Dict:
            total = sum(v.get("amount", 0) for v in values)
            return {"total_amount": total, "count": len(values)}
            
        agg_processor = platform.stream_processor.aggregate(
            "orders",
            "order-totals",
            sum_amounts,
            window_size=60
        )
        print(f"  ✓ Aggregate processor: {agg_processor}")
        
        # Simulate DLQ
        print("\n💀 Dead Letter Queue...")
        
        # Create a failing event
        failing_event = Event(
            event_id="evt_fail",
            topic="orders",
            value={"order_id": "BAD001"},
            max_attempts=3,
            attempts=3
        )
        
        platform.consumer_manager._send_to_dead_letter(
            failing_event,
            "Processing error: Invalid order data",
            consumer
        )
        
        print(f"\n  DLQ entries: {len(platform.consumer_manager.dead_letters)}")
        
        for dl in platform.consumer_manager.dead_letters:
            print(f"  - {dl.dead_letter_id}: {dl.error}")
            
        # Event replay
        print("\n⏪ Event Replay...")
        
        # Create replay topic
        platform.topic_manager.create_topic("orders-replay", partitions=3)
        
        replayed = await platform.event_replay.replay(
            source_topic="orders",
            target_topic="orders-replay",
            start_offset=0
        )
        
        print(f"\n  Replayed {replayed} events to orders-replay")
        
        # Topic statistics
        print("\n📊 Topic Statistics:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │ Topic              │ Partitions │ Messages │ Bytes In      │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        
        for topic in platform.topic_manager.topics.values():
            name = topic.name[:18].ljust(18)
            print(f"  │ {name} │ {topic.partitions:10} │ {topic.message_count:8} │ {topic.bytes_in:13} │")
            
        print("  └─────────────────────────────────────────────────────────────┘")
        
        # Consumer group stats
        print("\n👥 Consumer Group Statistics:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │ Group               │ Consumers │ Topics │ Generation      │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        
        for group in platform.consumer_manager.groups.values():
            name = group.group_id[:19].ljust(19)
            print(f"  │ {name} │ {len(group.consumers):9} │ {len(group.topics):6} │ {group.generation:15} │")
            
        print("  └─────────────────────────────────────────────────────────────┘")
        
        # Platform statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Topics: {stats['topics']}")
        print(f"  Partitions: {stats['partitions']}")
        print(f"  Consumer Groups: {stats['consumer_groups']}")
        print(f"  Consumers: {stats['consumers']}")
        print(f"  Total Messages: {stats['total_messages']}")
        print(f"  Dead Letters: {stats['dead_letters']}")
        print(f"  Schemas: {stats['schemas']}")
        print(f"  Processors: {stats['processors']}")
        
        # Dashboard
        print("\n📋 Event Streaming Dashboard:")
        print("  ┌────────────────────────────────────────────────────────────┐")
        print("  │                Event Streaming Overview                    │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Topics:                  {stats['topics']:>10}                   │")
        print(f"  │ Partitions:              {stats['partitions']:>10}                   │")
        print(f"  │ Consumer Groups:         {stats['consumer_groups']:>10}                   │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Messages:          {stats['total_messages']:>10}                   │")
        print(f"  │ Dead Letters:            {stats['dead_letters']:>10}                   │")
        print(f"  │ Stream Processors:       {stats['processors']:>10}                   │")
        print("  └────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Event Streaming Platform initialized!")
    print("=" * 60)
