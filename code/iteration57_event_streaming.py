#!/usr/bin/env python3
"""
Server Init - Iteration 57: Event Streaming & Message Queue Platform
Потоковая обработка событий и очереди сообщений

Функционал:
- Message Queue - очереди сообщений
- Event Streaming - потоковая передача событий
- Topic Management - управление топиками
- Consumer Groups - группы потребителей
- Dead Letter Queue - очередь недоставленных сообщений
- Message Routing - маршрутизация сообщений
- Stream Processing - обработка потоков
- Event Sourcing - событийное хранение
"""

import json
import asyncio
import hashlib
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
from collections import defaultdict
import random
import uuid


class MessageStatus(Enum):
    """Статус сообщения"""
    PENDING = "pending"
    DELIVERED = "delivered"
    PROCESSED = "processed"
    FAILED = "failed"
    DLQ = "dlq"  # Dead Letter Queue


class DeliveryMode(Enum):
    """Режим доставки"""
    AT_MOST_ONCE = "at_most_once"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"


class ConsumerState(Enum):
    """Состояние потребителя"""
    ACTIVE = "active"
    PAUSED = "paused"
    DISCONNECTED = "disconnected"


class PartitionStrategy(Enum):
    """Стратегия партиционирования"""
    ROUND_ROBIN = "round_robin"
    KEY_BASED = "key_based"
    RANDOM = "random"


@dataclass
class Message:
    """Сообщение"""
    message_id: str
    topic: str
    
    # Payload
    payload: Any = None
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Routing
    key: Optional[str] = None  # Partition key
    partition: int = 0
    
    # Статус
    status: MessageStatus = MessageStatus.PENDING
    
    # Метаданные
    timestamp: datetime = field(default_factory=datetime.now)
    producer_id: str = ""
    
    # Delivery
    delivery_attempts: int = 0
    max_retries: int = 3
    
    # Offset
    offset: int = 0


@dataclass
class Topic:
    """Топик"""
    topic_id: str
    name: str
    
    # Партиции
    partitions: int = 3
    replication_factor: int = 1
    
    # Retention
    retention_hours: int = 168  # 7 days
    retention_bytes: int = 1073741824  # 1 GB
    
    # Настройки
    delivery_mode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE
    partition_strategy: PartitionStrategy = PartitionStrategy.KEY_BASED
    
    # Компакция
    compaction_enabled: bool = False
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Partition:
    """Партиция"""
    partition_id: int
    topic: str
    
    # Сообщения
    messages: List[Message] = field(default_factory=list)
    
    # Offset
    high_watermark: int = 0  # Latest committed offset
    log_end_offset: int = 0  # Latest message offset
    
    # Размер
    size_bytes: int = 0


@dataclass
class ConsumerGroup:
    """Группа потребителей"""
    group_id: str
    name: str
    
    # Подписки
    subscriptions: List[str] = field(default_factory=list)  # Topic names
    
    # Потребители
    consumers: Dict[str, Any] = field(default_factory=dict)  # consumer_id -> Consumer
    
    # Offsets
    committed_offsets: Dict[str, Dict[int, int]] = field(default_factory=dict)  # topic -> partition -> offset
    
    # Балансировка
    partition_assignments: Dict[str, List[int]] = field(default_factory=dict)  # consumer_id -> partitions
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Consumer:
    """Потребитель"""
    consumer_id: str
    group_id: str
    
    # Состояние
    state: ConsumerState = ConsumerState.ACTIVE
    
    # Назначенные партиции
    assigned_partitions: Dict[str, List[int]] = field(default_factory=dict)  # topic -> partitions
    
    # Heartbeat
    last_heartbeat: datetime = field(default_factory=datetime.now)
    
    # Метрики
    messages_consumed: int = 0
    last_poll: Optional[datetime] = None


@dataclass
class Producer:
    """Производитель"""
    producer_id: str
    
    # Настройки
    acks: str = "all"  # 0, 1, all
    batch_size: int = 16384
    linger_ms: int = 0
    
    # Метрики
    messages_produced: int = 0
    bytes_produced: int = 0


@dataclass
class DeadLetterQueue:
    """Очередь недоставленных сообщений"""
    dlq_id: str
    source_topic: str
    
    # Сообщения
    messages: List[Message] = field(default_factory=list)
    
    # Настройки
    retention_days: int = 7
    
    # Статистика
    total_messages: int = 0


@dataclass
class StreamEvent:
    """Событие потока"""
    event_id: str
    stream: str
    
    # Данные
    event_type: str = ""
    data: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Время
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Position
    position: int = 0


class MessageBroker:
    """Брокер сообщений"""
    
    def __init__(self):
        self.topics: Dict[str, Topic] = {}
        self.partitions: Dict[str, Dict[int, Partition]] = {}  # topic -> partition_id -> Partition
        self.consumer_groups: Dict[str, ConsumerGroup] = {}
        self.producers: Dict[str, Producer] = {}
        self.dlqs: Dict[str, DeadLetterQueue] = {}
        
    def create_topic(self, name: str, partitions: int = 3, **kwargs) -> Topic:
        """Создание топика"""
        topic = Topic(
            topic_id=f"topic_{uuid.uuid4().hex[:8]}",
            name=name,
            partitions=partitions,
            **kwargs
        )
        
        self.topics[name] = topic
        
        # Создание партиций
        self.partitions[name] = {}
        for i in range(partitions):
            self.partitions[name][i] = Partition(
                partition_id=i,
                topic=name
            )
            
        # Создание DLQ
        dlq = DeadLetterQueue(
            dlq_id=f"dlq_{uuid.uuid4().hex[:8]}",
            source_topic=name
        )
        self.dlqs[name] = dlq
        
        return topic
        
    def create_producer(self, **kwargs) -> Producer:
        """Создание производителя"""
        producer = Producer(
            producer_id=f"producer_{uuid.uuid4().hex[:8]}",
            **kwargs
        )
        
        self.producers[producer.producer_id] = producer
        return producer
        
    def create_consumer_group(self, name: str, topics: List[str]) -> ConsumerGroup:
        """Создание группы потребителей"""
        group = ConsumerGroup(
            group_id=f"group_{uuid.uuid4().hex[:8]}",
            name=name,
            subscriptions=topics
        )
        
        # Инициализация offsets
        for topic in topics:
            group.committed_offsets[topic] = {}
            if topic in self.partitions:
                for partition_id in self.partitions[topic]:
                    group.committed_offsets[topic][partition_id] = 0
                    
        self.consumer_groups[group.group_id] = group
        return group
        
    def join_consumer_group(self, group_id: str) -> Consumer:
        """Присоединение к группе потребителей"""
        group = self.consumer_groups.get(group_id)
        if not group:
            raise ValueError("Consumer group not found")
            
        consumer = Consumer(
            consumer_id=f"consumer_{uuid.uuid4().hex[:8]}",
            group_id=group_id
        )
        
        group.consumers[consumer.consumer_id] = consumer
        
        # Перебалансировка
        self._rebalance_partitions(group)
        
        return consumer
        
    def _rebalance_partitions(self, group: ConsumerGroup):
        """Перебалансировка партиций"""
        active_consumers = [
            c for c in group.consumers.values()
            if c.state == ConsumerState.ACTIVE
        ]
        
        if not active_consumers:
            return
            
        # Собираем все партиции
        all_partitions = []
        for topic in group.subscriptions:
            if topic in self.partitions:
                for partition_id in self.partitions[topic]:
                    all_partitions.append((topic, partition_id))
                    
        # Распределяем round-robin
        group.partition_assignments.clear()
        
        for i, (topic, partition) in enumerate(all_partitions):
            consumer = active_consumers[i % len(active_consumers)]
            
            if consumer.consumer_id not in group.partition_assignments:
                group.partition_assignments[consumer.consumer_id] = []
                
            group.partition_assignments[consumer.consumer_id].append((topic, partition))
            
        # Обновляем consumers
        for consumer in active_consumers:
            consumer.assigned_partitions = {}
            assignments = group.partition_assignments.get(consumer.consumer_id, [])
            
            for topic, partition in assignments:
                if topic not in consumer.assigned_partitions:
                    consumer.assigned_partitions[topic] = []
                consumer.assigned_partitions[topic].append(partition)
                
    def _get_partition(self, topic: Topic, key: Optional[str] = None) -> int:
        """Выбор партиции"""
        if topic.partition_strategy == PartitionStrategy.KEY_BASED and key:
            return hash(key) % topic.partitions
        elif topic.partition_strategy == PartitionStrategy.ROUND_ROBIN:
            return random.randint(0, topic.partitions - 1)
        else:
            return random.randint(0, topic.partitions - 1)
            
    async def produce(self, producer_id: str, topic_name: str,
                       payload: Any, key: str = None,
                       headers: Dict[str, str] = None) -> Message:
        """Отправка сообщения"""
        producer = self.producers.get(producer_id)
        topic = self.topics.get(topic_name)
        
        if not producer or not topic:
            raise ValueError("Producer or topic not found")
            
        partition_id = self._get_partition(topic, key)
        partition = self.partitions[topic_name][partition_id]
        
        message = Message(
            message_id=f"msg_{uuid.uuid4().hex[:8]}",
            topic=topic_name,
            payload=payload,
            key=key,
            headers=headers or {},
            partition=partition_id,
            producer_id=producer_id,
            offset=partition.log_end_offset
        )
        
        partition.messages.append(message)
        partition.log_end_offset += 1
        partition.size_bytes += len(json.dumps(payload).encode())
        
        producer.messages_produced += 1
        
        return message
        
    async def consume(self, consumer_id: str, max_messages: int = 10) -> List[Message]:
        """Потребление сообщений"""
        # Находим consumer и group
        consumer = None
        group = None
        
        for g in self.consumer_groups.values():
            if consumer_id in g.consumers:
                consumer = g.consumers[consumer_id]
                group = g
                break
                
        if not consumer or not group:
            return []
            
        consumer.last_poll = datetime.now()
        consumer.last_heartbeat = datetime.now()
        
        messages = []
        
        for topic, partitions in consumer.assigned_partitions.items():
            for partition_id in partitions:
                partition = self.partitions.get(topic, {}).get(partition_id)
                if not partition:
                    continue
                    
                committed = group.committed_offsets.get(topic, {}).get(partition_id, 0)
                
                for msg in partition.messages[committed:]:
                    if len(messages) >= max_messages:
                        break
                        
                    if msg.status == MessageStatus.PENDING:
                        msg.status = MessageStatus.DELIVERED
                        msg.delivery_attempts += 1
                        messages.append(msg)
                        
        consumer.messages_consumed += len(messages)
        return messages
        
    async def commit(self, consumer_id: str, topic: str, partition: int, offset: int):
        """Коммит offset"""
        for group in self.consumer_groups.values():
            if consumer_id in group.consumers:
                if topic not in group.committed_offsets:
                    group.committed_offsets[topic] = {}
                    
                group.committed_offsets[topic][partition] = offset
                
                # Обновляем high watermark
                if topic in self.partitions and partition in self.partitions[topic]:
                    self.partitions[topic][partition].high_watermark = max(
                        self.partitions[topic][partition].high_watermark,
                        offset
                    )
                break
                
    async def process_message(self, message: Message, success: bool = True):
        """Обработка сообщения"""
        if success:
            message.status = MessageStatus.PROCESSED
        else:
            message.status = MessageStatus.FAILED
            
            if message.delivery_attempts >= message.max_retries:
                await self._send_to_dlq(message)
                
    async def _send_to_dlq(self, message: Message):
        """Отправка в DLQ"""
        dlq = self.dlqs.get(message.topic)
        if dlq:
            message.status = MessageStatus.DLQ
            dlq.messages.append(message)
            dlq.total_messages += 1


class StreamProcessor:
    """Процессор потоков"""
    
    def __init__(self):
        self.streams: Dict[str, List[StreamEvent]] = {}
        self.processors: Dict[str, List[Callable]] = {}  # stream -> processors
        self.aggregations: Dict[str, Dict[str, Any]] = {}  # stream -> aggregation results
        
    def create_stream(self, name: str) -> str:
        """Создание потока"""
        self.streams[name] = []
        self.processors[name] = []
        return name
        
    async def emit(self, stream: str, event_type: str, data: Any,
                    metadata: Dict[str, Any] = None) -> StreamEvent:
        """Эмитирование события"""
        if stream not in self.streams:
            self.create_stream(stream)
            
        event = StreamEvent(
            event_id=f"event_{uuid.uuid4().hex[:8]}",
            stream=stream,
            event_type=event_type,
            data=data,
            metadata=metadata or {},
            position=len(self.streams[stream])
        )
        
        self.streams[stream].append(event)
        
        # Выполнение процессоров
        for processor in self.processors.get(stream, []):
            try:
                await processor(event)
            except Exception as e:
                print(f"Processor error: {e}")
                
        return event
        
    def add_processor(self, stream: str, processor: Callable):
        """Добавление процессора"""
        if stream not in self.processors:
            self.processors[stream] = []
        self.processors[stream].append(processor)
        
    async def aggregate(self, stream: str, window_seconds: int,
                         aggregation_func: str = "count") -> Dict[str, Any]:
        """Агрегация событий"""
        cutoff = datetime.now() - timedelta(seconds=window_seconds)
        
        events = [
            e for e in self.streams.get(stream, [])
            if e.timestamp > cutoff
        ]
        
        result = {"stream": stream, "window_seconds": window_seconds}
        
        if aggregation_func == "count":
            result["count"] = len(events)
            
            # По типам
            by_type = defaultdict(int)
            for e in events:
                by_type[e.event_type] += 1
            result["by_type"] = dict(by_type)
            
        elif aggregation_func == "rate":
            result["events_per_second"] = len(events) / window_seconds if window_seconds > 0 else 0
            
        return result
        
    def get_stream(self, name: str, from_position: int = 0,
                    limit: int = 100) -> List[StreamEvent]:
        """Получение событий из потока"""
        stream = self.streams.get(name, [])
        return stream[from_position:from_position + limit]


class EventStore:
    """Хранилище событий (Event Sourcing)"""
    
    def __init__(self):
        self.events: Dict[str, List[StreamEvent]] = {}  # aggregate_id -> events
        self.snapshots: Dict[str, Dict[str, Any]] = {}  # aggregate_id -> snapshot
        
    async def append(self, aggregate_id: str, event_type: str,
                      data: Any, metadata: Dict[str, Any] = None) -> StreamEvent:
        """Добавление события"""
        if aggregate_id not in self.events:
            self.events[aggregate_id] = []
            
        event = StreamEvent(
            event_id=f"ev_{uuid.uuid4().hex[:8]}",
            stream=aggregate_id,
            event_type=event_type,
            data=data,
            metadata=metadata or {},
            position=len(self.events[aggregate_id])
        )
        
        self.events[aggregate_id].append(event)
        return event
        
    def get_events(self, aggregate_id: str, from_version: int = 0) -> List[StreamEvent]:
        """Получение событий"""
        return self.events.get(aggregate_id, [])[from_version:]
        
    async def create_snapshot(self, aggregate_id: str, state: Dict[str, Any]):
        """Создание снапшота"""
        self.snapshots[aggregate_id] = {
            "state": state,
            "version": len(self.events.get(aggregate_id, [])),
            "timestamp": datetime.now()
        }
        
    def get_snapshot(self, aggregate_id: str) -> Optional[Dict[str, Any]]:
        """Получение снапшота"""
        return self.snapshots.get(aggregate_id)
        
    async def replay(self, aggregate_id: str, apply_func: Callable) -> Any:
        """Воспроизведение событий"""
        state = {}
        
        # Проверяем снапшот
        snapshot = self.get_snapshot(aggregate_id)
        if snapshot:
            state = snapshot["state"].copy()
            events = self.get_events(aggregate_id, snapshot["version"])
        else:
            events = self.get_events(aggregate_id)
            
        # Применяем события
        for event in events:
            state = await apply_func(state, event)
            
        return state


class MessageRouter:
    """Маршрутизатор сообщений"""
    
    def __init__(self, broker: MessageBroker):
        self.broker = broker
        self.routes: Dict[str, List[Dict[str, Any]]] = {}  # source -> routes
        
    def add_route(self, source_topic: str, target_topic: str,
                   filter_func: Callable = None, transform_func: Callable = None):
        """Добавление маршрута"""
        if source_topic not in self.routes:
            self.routes[source_topic] = []
            
        self.routes[source_topic].append({
            "target": target_topic,
            "filter": filter_func,
            "transform": transform_func
        })
        
    async def route_message(self, producer_id: str, message: Message):
        """Маршрутизация сообщения"""
        routes = self.routes.get(message.topic, [])
        
        for route in routes:
            # Фильтрация
            if route["filter"] and not route["filter"](message):
                continue
                
            # Трансформация
            payload = message.payload
            if route["transform"]:
                payload = route["transform"](message)
                
            # Отправка в целевой топик
            await self.broker.produce(
                producer_id,
                route["target"],
                payload,
                key=message.key,
                headers=message.headers
            )


class MessagingPlatform:
    """Платформа сообщений"""
    
    def __init__(self):
        self.broker = MessageBroker()
        self.stream_processor = StreamProcessor()
        self.event_store = EventStore()
        self.router = MessageRouter(self.broker)
        
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики"""
        total_messages = 0
        total_partitions = 0
        
        for topic, partitions in self.broker.partitions.items():
            total_partitions += len(partitions)
            for partition in partitions.values():
                total_messages += len(partition.messages)
                
        dlq_messages = sum(dlq.total_messages for dlq in self.broker.dlqs.values())
        
        return {
            "topics": len(self.broker.topics),
            "partitions": total_partitions,
            "consumer_groups": len(self.broker.consumer_groups),
            "producers": len(self.broker.producers),
            "total_messages": total_messages,
            "dlq_messages": dlq_messages,
            "streams": len(self.stream_processor.streams),
            "aggregates": len(self.event_store.events)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 57: Event Streaming & Message Queue")
    print("=" * 60)
    
    async def demo():
        # Создание платформы
        platform = MessagingPlatform()
        print("✓ Messaging Platform created")
        
        # Создание топиков
        print("\n📦 Creating topics...")
        
        topics = [
            ("orders", 3),
            ("payments", 2),
            ("notifications", 1),
            ("order-completed", 2),
        ]
        
        for name, partitions in topics:
            topic = platform.broker.create_topic(name, partitions=partitions)
            print(f"  ✓ Topic: {name} ({partitions} partitions)")
            
        # Создание producer
        print("\n📤 Creating producer...")
        producer = platform.broker.create_producer(acks="all")
        print(f"  ✓ Producer: {producer.producer_id}")
        
        # Создание consumer group
        print("\n👥 Creating consumer groups...")
        
        order_group = platform.broker.create_consumer_group(
            "order-processors",
            ["orders"]
        )
        print(f"  ✓ Group: {order_group.name}")
        
        payment_group = platform.broker.create_consumer_group(
            "payment-processors",
            ["payments", "order-completed"]
        )
        print(f"  ✓ Group: {payment_group.name}")
        
        # Присоединение consumers
        print("\n🔌 Joining consumers...")
        
        consumers = []
        for i in range(3):
            consumer = platform.broker.join_consumer_group(order_group.group_id)
            consumers.append(consumer)
            assigned = sum(len(p) for p in consumer.assigned_partitions.values())
            print(f"  ✓ Consumer {i+1}: {assigned} partitions assigned")
            
        # Настройка маршрутизации
        print("\n🔀 Setting up routing...")
        
        # Маршрут: orders -> notifications (для определённых событий)
        platform.router.add_route(
            "orders",
            "notifications",
            filter_func=lambda m: m.payload.get("status") == "created",
            transform_func=lambda m: {
                "type": "order_notification",
                "order_id": m.payload.get("order_id"),
                "message": "New order created"
            }
        )
        print("  ✓ Route: orders -> notifications (filter: status=created)")
        
        # Отправка сообщений
        print("\n📨 Producing messages...")
        
        orders_data = [
            {"order_id": "ORD-001", "status": "created", "amount": 99.99, "customer": "user1"},
            {"order_id": "ORD-002", "status": "created", "amount": 149.99, "customer": "user2"},
            {"order_id": "ORD-003", "status": "processing", "amount": 299.99, "customer": "user3"},
            {"order_id": "ORD-004", "status": "created", "amount": 49.99, "customer": "user1"},
            {"order_id": "ORD-005", "status": "completed", "amount": 199.99, "customer": "user4"},
        ]
        
        for order in orders_data:
            msg = await platform.broker.produce(
                producer.producer_id,
                "orders",
                order,
                key=order["customer"]
            )
            print(f"  ✓ Produced: {order['order_id']} -> partition {msg.partition}")
            
            # Маршрутизация
            await platform.router.route_message(producer.producer_id, msg)
            
        # Потребление сообщений
        print("\n📥 Consuming messages...")
        
        for consumer in consumers[:2]:  # Первые 2 потребителя
            messages = await platform.broker.consume(consumer.consumer_id, max_messages=3)
            
            if messages:
                print(f"\n  Consumer {consumer.consumer_id[:12]}...")
                for msg in messages:
                    print(f"    ✓ {msg.payload['order_id']} ({msg.status.value})")
                    
                    # Обработка
                    success = random.random() > 0.1  # 90% успех
                    await platform.broker.process_message(msg, success)
                    
                    # Коммит
                    if success:
                        await platform.broker.commit(
                            consumer.consumer_id,
                            msg.topic,
                            msg.partition,
                            msg.offset + 1
                        )
                        
        # Stream Processing
        print("\n🌊 Stream Processing...")
        
        # Создание потока
        platform.stream_processor.create_stream("analytics")
        
        # Добавление процессора
        processed_events = []
        
        async def analytics_processor(event: StreamEvent):
            processed_events.append(event.event_type)
            
        platform.stream_processor.add_processor("analytics", analytics_processor)
        
        # Эмитирование событий
        events_data = [
            ("page_view", {"page": "/home", "user": "u1"}),
            ("page_view", {"page": "/products", "user": "u2"}),
            ("click", {"element": "buy_button", "user": "u1"}),
            ("page_view", {"page": "/checkout", "user": "u1"}),
            ("purchase", {"amount": 99.99, "user": "u1"}),
        ]
        
        for event_type, data in events_data:
            event = await platform.stream_processor.emit("analytics", event_type, data)
            print(f"  ✓ Emitted: {event_type}")
            
        print(f"  Processed: {len(processed_events)} events")
        
        # Агрегация
        print("\n📊 Stream Aggregation...")
        
        aggregation = await platform.stream_processor.aggregate(
            "analytics",
            window_seconds=60,
            aggregation_func="count"
        )
        
        print(f"  Total events (60s window): {aggregation['count']}")
        print(f"  By type: {aggregation['by_type']}")
        
        # Event Sourcing
        print("\n📚 Event Sourcing Demo...")
        
        # Создание агрегата Order
        order_id = "order-123"
        
        await platform.event_store.append(
            order_id,
            "OrderCreated",
            {"customer": "user1", "items": [{"product": "p1", "qty": 2}]}
        )
        
        await platform.event_store.append(
            order_id,
            "ItemAdded",
            {"product": "p2", "qty": 1}
        )
        
        await platform.event_store.append(
            order_id,
            "PaymentReceived",
            {"amount": 299.99, "method": "card"}
        )
        
        await platform.event_store.append(
            order_id,
            "OrderShipped",
            {"tracking": "TRK123456"}
        )
        
        # Получение событий
        events = platform.event_store.get_events(order_id)
        print(f"  Order events: {len(events)}")
        for e in events:
            print(f"    {e.position}. {e.event_type}")
            
        # Replay
        async def apply_order_event(state: Dict, event: StreamEvent) -> Dict:
            if event.event_type == "OrderCreated":
                state = {
                    "customer": event.data["customer"],
                    "items": event.data["items"],
                    "status": "created"
                }
            elif event.event_type == "ItemAdded":
                state["items"].append(event.data)
            elif event.event_type == "PaymentReceived":
                state["payment"] = event.data
                state["status"] = "paid"
            elif event.event_type == "OrderShipped":
                state["tracking"] = event.data["tracking"]
                state["status"] = "shipped"
            return state
            
        final_state = await platform.event_store.replay(order_id, apply_order_event)
        print(f"\n  Replayed state:")
        print(f"    Customer: {final_state['customer']}")
        print(f"    Items: {len(final_state['items'])}")
        print(f"    Status: {final_state['status']}")
        
        # Снапшот
        await platform.event_store.create_snapshot(order_id, final_state)
        snapshot = platform.event_store.get_snapshot(order_id)
        print(f"  ✓ Snapshot created at version {snapshot['version']}")
        
        # Dead Letter Queue
        print("\n💀 Dead Letter Queue...")
        
        # Симуляция failed messages
        for i in range(3):
            msg = await platform.broker.produce(
                producer.producer_id,
                "orders",
                {"order_id": f"FAIL-{i}", "status": "error"}
            )
            msg.delivery_attempts = msg.max_retries  # Исчерпаны попытки
            await platform.broker.process_message(msg, success=False)
            
        dlq = platform.broker.dlqs.get("orders")
        print(f"  Messages in DLQ: {dlq.total_messages}")
        
        # Статистика платформы
        print("\n📈 Platform Statistics:")
        stats = platform.get_stats()
        print(f"  Topics: {stats['topics']}")
        print(f"  Partitions: {stats['partitions']}")
        print(f"  Consumer Groups: {stats['consumer_groups']}")
        print(f"  Producers: {stats['producers']}")
        print(f"  Total Messages: {stats['total_messages']}")
        print(f"  DLQ Messages: {stats['dlq_messages']}")
        print(f"  Streams: {stats['streams']}")
        print(f"  Aggregates: {stats['aggregates']}")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Event Streaming & Message Queue Platform initialized!")
    print("=" * 60)
