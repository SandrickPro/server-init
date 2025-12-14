#!/usr/bin/env python3
"""
Server Init - Iteration 285: Message Queue Platform
Платформа Message Queue

Функционал:
- Queue Management - управление очередями
- Message Publishing - публикация сообщений
- Message Consuming - потребление сообщений
- Priority Queues - приоритетные очереди
- Delayed Messages - отложенные сообщения
- Message TTL - время жизни
- Routing - маршрутизация
- Acknowledgment - подтверждения
"""

import asyncio
import random
import time
import heapq
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
import uuid


class QueueType(Enum):
    """Тип очереди"""
    STANDARD = "standard"
    FIFO = "fifo"
    PRIORITY = "priority"
    DELAY = "delay"


class MessageState(Enum):
    """Состояние сообщения"""
    PENDING = "pending"
    DELIVERED = "delivered"
    ACKNOWLEDGED = "acknowledged"
    REJECTED = "rejected"
    EXPIRED = "expired"
    DEAD = "dead"


class ExchangeType(Enum):
    """Тип обменника"""
    DIRECT = "direct"
    FANOUT = "fanout"
    TOPIC = "topic"
    HEADERS = "headers"


class DeliveryMode(Enum):
    """Режим доставки"""
    AT_MOST_ONCE = "at_most_once"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"


@dataclass
class Message:
    """Сообщение"""
    message_id: str
    
    # Content
    body: Any = None
    content_type: str = "application/json"
    
    # Routing
    routing_key: str = ""
    headers: Dict[str, Any] = field(default_factory=dict)
    
    # Priority
    priority: int = 0  # 0-9, higher = more priority
    
    # TTL
    ttl_ms: int = 0  # 0 = no expiration
    expiration: Optional[datetime] = None
    
    # Delay
    delay_ms: int = 0
    available_at: Optional[datetime] = None
    
    # State
    state: MessageState = MessageState.PENDING
    
    # Delivery
    delivery_count: int = 0
    max_deliveries: int = 5
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    delivered_at: Optional[datetime] = None
    
    # Size
    size_bytes: int = 0
    
    def __lt__(self, other):
        # For priority queue
        return self.priority > other.priority


@dataclass
class Queue:
    """Очередь"""
    queue_id: str
    name: str
    
    # Type
    queue_type: QueueType = QueueType.STANDARD
    
    # Messages
    messages: List[Message] = field(default_factory=list)
    priority_heap: List[Message] = field(default_factory=list)
    
    # Config
    max_length: int = 0  # 0 = unlimited
    max_bytes: int = 0  # 0 = unlimited
    default_ttl_ms: int = 0
    
    # Bindings
    bindings: List['Binding'] = field(default_factory=list)
    
    # Consumers
    consumer_count: int = 0
    
    # Stats
    messages_total: int = 0
    messages_delivered: int = 0
    messages_acknowledged: int = 0
    messages_rejected: int = 0
    
    # Durable
    durable: bool = True
    
    # Created
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Exchange:
    """Обменник"""
    exchange_id: str
    name: str
    
    # Type
    exchange_type: ExchangeType = ExchangeType.DIRECT
    
    # Bindings
    bindings: List['Binding'] = field(default_factory=list)
    
    # Stats
    messages_in: int = 0
    messages_routed: int = 0
    
    # Durable
    durable: bool = True


@dataclass
class Binding:
    """Привязка"""
    binding_id: str
    
    # Source
    exchange_name: str = ""
    
    # Target
    queue_name: str = ""
    
    # Routing
    routing_key: str = ""
    arguments: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Consumer:
    """Потребитель"""
    consumer_id: str
    
    # Queue
    queue_name: str = ""
    
    # Config
    prefetch_count: int = 10
    exclusive: bool = False
    
    # Callback
    callback: Optional[Callable] = None
    
    # Stats
    messages_consumed: int = 0
    messages_acked: int = 0
    messages_rejected: int = 0
    
    # Active
    active: bool = True
    
    # Pending acks
    pending_acks: Set[str] = field(default_factory=set)


@dataclass
class Publisher:
    """Издатель"""
    publisher_id: str
    
    # Config
    delivery_mode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE
    confirm_mode: bool = False
    
    # Stats
    messages_published: int = 0
    messages_confirmed: int = 0
    messages_returned: int = 0


@dataclass
class DeadLetterConfig:
    """Конфигурация DLQ"""
    exchange: str = ""
    routing_key: str = ""
    enabled: bool = False


class MessageQueueManager:
    """Менеджер Message Queue"""
    
    def __init__(self):
        self.queues: Dict[str, Queue] = {}
        self.exchanges: Dict[str, Exchange] = {}
        self.consumers: Dict[str, Consumer] = {}
        self.publishers: Dict[str, Publisher] = {}
        
        # Default exchange
        self.exchanges[""] = Exchange(
            exchange_id="default",
            name="",
            exchange_type=ExchangeType.DIRECT
        )
        
        # Dead letter
        self.dlq_config: Dict[str, DeadLetterConfig] = {}
        
        # Stats
        self.messages_total: int = 0
        self.messages_delivered: int = 0
        self.messages_acked: int = 0
        
    def declare_queue(self, name: str,
                     queue_type: QueueType = QueueType.STANDARD,
                     durable: bool = True,
                     max_length: int = 0,
                     default_ttl_ms: int = 0) -> Queue:
        """Объявление очереди"""
        if name in self.queues:
            return self.queues[name]
            
        queue = Queue(
            queue_id=f"queue_{uuid.uuid4().hex[:8]}",
            name=name,
            queue_type=queue_type,
            durable=durable,
            max_length=max_length,
            default_ttl_ms=default_ttl_ms
        )
        
        self.queues[name] = queue
        
        # Create implicit binding to default exchange
        binding = Binding(
            binding_id=f"bind_{uuid.uuid4().hex[:8]}",
            exchange_name="",
            queue_name=name,
            routing_key=name
        )
        queue.bindings.append(binding)
        self.exchanges[""].bindings.append(binding)
        
        return queue
        
    def declare_exchange(self, name: str,
                        exchange_type: ExchangeType = ExchangeType.DIRECT,
                        durable: bool = True) -> Exchange:
        """Объявление обменника"""
        if name in self.exchanges:
            return self.exchanges[name]
            
        exchange = Exchange(
            exchange_id=f"exchange_{uuid.uuid4().hex[:8]}",
            name=name,
            exchange_type=exchange_type,
            durable=durable
        )
        
        self.exchanges[name] = exchange
        return exchange
        
    def bind_queue(self, queue_name: str,
                  exchange_name: str,
                  routing_key: str = "",
                  arguments: Dict[str, Any] = None) -> Binding:
        """Привязка очереди к обменнику"""
        queue = self.queues.get(queue_name)
        exchange = self.exchanges.get(exchange_name)
        
        if not queue or not exchange:
            return None
            
        binding = Binding(
            binding_id=f"bind_{uuid.uuid4().hex[:8]}",
            exchange_name=exchange_name,
            queue_name=queue_name,
            routing_key=routing_key,
            arguments=arguments or {}
        )
        
        queue.bindings.append(binding)
        exchange.bindings.append(binding)
        
        return binding
        
    def create_publisher(self, delivery_mode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE) -> Publisher:
        """Создание издателя"""
        publisher = Publisher(
            publisher_id=f"pub_{uuid.uuid4().hex[:8]}",
            delivery_mode=delivery_mode
        )
        
        self.publishers[publisher.publisher_id] = publisher
        return publisher
        
    def create_consumer(self, queue_name: str,
                       prefetch_count: int = 10,
                       callback: Callable = None) -> Consumer:
        """Создание потребителя"""
        queue = self.queues.get(queue_name)
        if not queue:
            return None
            
        consumer = Consumer(
            consumer_id=f"consumer_{uuid.uuid4().hex[:8]}",
            queue_name=queue_name,
            prefetch_count=prefetch_count,
            callback=callback
        )
        
        queue.consumer_count += 1
        self.consumers[consumer.consumer_id] = consumer
        
        return consumer
        
    async def publish(self, publisher: Publisher,
                     exchange_name: str,
                     routing_key: str,
                     body: Any,
                     priority: int = 0,
                     ttl_ms: int = 0,
                     delay_ms: int = 0,
                     headers: Dict[str, Any] = None) -> Message:
        """Публикация сообщения"""
        exchange = self.exchanges.get(exchange_name)
        if not exchange:
            raise Exception(f"Exchange not found: {exchange_name}")
            
        # Create message
        message = Message(
            message_id=f"msg_{uuid.uuid4().hex[:12]}",
            body=body,
            routing_key=routing_key,
            priority=priority,
            ttl_ms=ttl_ms,
            delay_ms=delay_ms,
            headers=headers or {},
            size_bytes=len(str(body))
        )
        
        # Set expiration
        if ttl_ms > 0:
            message.expiration = datetime.now() + timedelta(milliseconds=ttl_ms)
            
        # Set delay
        if delay_ms > 0:
            message.available_at = datetime.now() + timedelta(milliseconds=delay_ms)
            
        # Route message
        routed_count = await self._route_message(exchange, message)
        
        # Update stats
        exchange.messages_in += 1
        exchange.messages_routed += routed_count
        publisher.messages_published += 1
        self.messages_total += 1
        
        if routed_count == 0:
            publisher.messages_returned += 1
            
        return message
        
    async def _route_message(self, exchange: Exchange, message: Message) -> int:
        """Маршрутизация сообщения"""
        routed = 0
        
        for binding in exchange.bindings:
            match = False
            
            if exchange.exchange_type == ExchangeType.DIRECT:
                match = binding.routing_key == message.routing_key
                
            elif exchange.exchange_type == ExchangeType.FANOUT:
                match = True
                
            elif exchange.exchange_type == ExchangeType.TOPIC:
                match = self._match_topic(binding.routing_key, message.routing_key)
                
            elif exchange.exchange_type == ExchangeType.HEADERS:
                match = self._match_headers(binding.arguments, message.headers)
                
            if match:
                queue = self.queues.get(binding.queue_name)
                if queue:
                    await self._enqueue(queue, message)
                    routed += 1
                    
        return routed
        
    def _match_topic(self, pattern: str, routing_key: str) -> bool:
        """Сопоставление topic pattern"""
        pattern_parts = pattern.split(".")
        key_parts = routing_key.split(".")
        
        i = j = 0
        while i < len(pattern_parts) and j < len(key_parts):
            if pattern_parts[i] == "#":
                if i == len(pattern_parts) - 1:
                    return True
                i += 1
                while j < len(key_parts) and key_parts[j] != pattern_parts[i]:
                    j += 1
            elif pattern_parts[i] == "*":
                i += 1
                j += 1
            elif pattern_parts[i] == key_parts[j]:
                i += 1
                j += 1
            else:
                return False
                
        return i == len(pattern_parts) and j == len(key_parts)
        
    def _match_headers(self, binding_args: Dict, message_headers: Dict) -> bool:
        """Сопоставление заголовков"""
        match_type = binding_args.get("x-match", "all")
        
        matching = 0
        required = len([k for k in binding_args if not k.startswith("x-")])
        
        for key, value in binding_args.items():
            if key.startswith("x-"):
                continue
            if message_headers.get(key) == value:
                matching += 1
                
        if match_type == "all":
            return matching == required
        else:  # any
            return matching > 0
            
    async def _enqueue(self, queue: Queue, message: Message):
        """Добавление в очередь"""
        # Check limits
        if queue.max_length > 0 and len(queue.messages) >= queue.max_length:
            # Remove oldest
            if queue.messages:
                removed = queue.messages.pop(0)
                await self._send_to_dlq(queue, removed, "queue_overflow")
                
        # Apply queue TTL
        if queue.default_ttl_ms > 0 and message.ttl_ms == 0:
            message.ttl_ms = queue.default_ttl_ms
            message.expiration = datetime.now() + timedelta(milliseconds=queue.default_ttl_ms)
            
        # Add to appropriate structure
        if queue.queue_type == QueueType.PRIORITY:
            heapq.heappush(queue.priority_heap, message)
        else:
            queue.messages.append(message)
            
        queue.messages_total += 1
        
    async def consume(self, consumer: Consumer,
                     timeout_ms: int = 1000) -> List[Message]:
        """Получение сообщений"""
        queue = self.queues.get(consumer.queue_name)
        if not queue or not consumer.active:
            return []
            
        messages = []
        now = datetime.now()
        
        # Check pending acks limit
        available_slots = consumer.prefetch_count - len(consumer.pending_acks)
        if available_slots <= 0:
            return []
            
        # Get messages based on queue type
        if queue.queue_type == QueueType.PRIORITY:
            source = queue.priority_heap
            pop_func = lambda: heapq.heappop(queue.priority_heap) if queue.priority_heap else None
        else:
            source = queue.messages
            pop_func = lambda: queue.messages.pop(0) if queue.messages else None
            
        while len(messages) < available_slots and source:
            message = pop_func()
            if not message:
                break
                
            # Check expiration
            if message.expiration and message.expiration < now:
                message.state = MessageState.EXPIRED
                await self._send_to_dlq(queue, message, "expired")
                continue
                
            # Check delay
            if message.available_at and message.available_at > now:
                # Put back
                if queue.queue_type == QueueType.PRIORITY:
                    heapq.heappush(queue.priority_heap, message)
                else:
                    queue.messages.insert(0, message)
                break
                
            # Deliver
            message.state = MessageState.DELIVERED
            message.delivery_count += 1
            message.delivered_at = now
            
            messages.append(message)
            consumer.pending_acks.add(message.message_id)
            consumer.messages_consumed += 1
            
            queue.messages_delivered += 1
            self.messages_delivered += 1
            
        return messages
        
    async def ack(self, consumer: Consumer, message_id: str) -> bool:
        """Подтверждение сообщения"""
        if message_id not in consumer.pending_acks:
            return False
            
        consumer.pending_acks.remove(message_id)
        consumer.messages_acked += 1
        
        queue = self.queues.get(consumer.queue_name)
        if queue:
            queue.messages_acknowledged += 1
            
        self.messages_acked += 1
        return True
        
    async def reject(self, consumer: Consumer,
                    message_id: str,
                    requeue: bool = False) -> bool:
        """Отклонение сообщения"""
        if message_id not in consumer.pending_acks:
            return False
            
        consumer.pending_acks.remove(message_id)
        consumer.messages_rejected += 1
        
        queue = self.queues.get(consumer.queue_name)
        if queue:
            queue.messages_rejected += 1
            
            # Find message and handle
            # Note: In production, we'd track unacked messages separately
            if not requeue:
                # Send to DLQ
                pass
                
        return True
        
    async def _send_to_dlq(self, queue: Queue,
                         message: Message,
                         reason: str):
        """Отправка в DLQ"""
        config = self.dlq_config.get(queue.name)
        if not config or not config.enabled:
            return
            
        dlq = self.queues.get(config.routing_key)
        if dlq:
            message.state = MessageState.DEAD
            message.headers["x-death-reason"] = reason
            message.headers["x-original-queue"] = queue.name
            
            await self._enqueue(dlq, message)
            
    def setup_dlq(self, queue_name: str,
                 dlq_name: str):
        """Настройка DLQ"""
        self.dlq_config[queue_name] = DeadLetterConfig(
            routing_key=dlq_name,
            enabled=True
        )
        
        # Create DLQ if not exists
        if dlq_name not in self.queues:
            self.declare_queue(dlq_name)
            
    def purge_queue(self, queue_name: str) -> int:
        """Очистка очереди"""
        queue = self.queues.get(queue_name)
        if not queue:
            return 0
            
        count = len(queue.messages) + len(queue.priority_heap)
        queue.messages.clear()
        queue.priority_heap.clear()
        
        return count
        
    def delete_queue(self, queue_name: str) -> bool:
        """Удаление очереди"""
        queue = self.queues.get(queue_name)
        if not queue:
            return False
            
        # Remove bindings
        for binding in queue.bindings:
            exchange = self.exchanges.get(binding.exchange_name)
            if exchange:
                exchange.bindings = [b for b in exchange.bindings if b.queue_name != queue_name]
                
        del self.queues[queue_name]
        return True
        
    def get_queue_stats(self, queue_name: str) -> Dict[str, Any]:
        """Статистика очереди"""
        queue = self.queues.get(queue_name)
        if not queue:
            return {}
            
        ready = len(queue.messages) + len(queue.priority_heap)
        
        return {
            "name": queue.name,
            "type": queue.queue_type.value,
            "ready": ready,
            "consumers": queue.consumer_count,
            "total": queue.messages_total,
            "delivered": queue.messages_delivered,
            "acknowledged": queue.messages_acknowledged,
            "rejected": queue.messages_rejected
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_ready = sum(len(q.messages) + len(q.priority_heap) for q in self.queues.values())
        
        return {
            "queues": len(self.queues),
            "exchanges": len(self.exchanges),
            "consumers": len(self.consumers),
            "publishers": len(self.publishers),
            "messages_total": self.messages_total,
            "messages_ready": total_ready,
            "messages_delivered": self.messages_delivered,
            "messages_acked": self.messages_acked
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 285: Message Queue Platform")
    print("=" * 60)
    
    manager = MessageQueueManager()
    print("✓ Message Queue Manager created")
    
    # Declare exchanges
    print("\n📤 Declaring Exchanges...")
    
    exchanges_config = [
        ("orders", ExchangeType.DIRECT),
        ("events", ExchangeType.FANOUT),
        ("logs", ExchangeType.TOPIC),
        ("notifications", ExchangeType.HEADERS),
    ]
    
    for name, ex_type in exchanges_config:
        exchange = manager.declare_exchange(name, ex_type)
        print(f"  📤 {name} ({ex_type.value})")
        
    # Declare queues
    print("\n📬 Declaring Queues...")
    
    queues_config = [
        ("order.new", QueueType.STANDARD, 10000, 0),
        ("order.process", QueueType.FIFO, 5000, 300000),
        ("order.priority", QueueType.PRIORITY, 1000, 0),
        ("payment.process", QueueType.STANDARD, 5000, 0),
        ("notification.email", QueueType.DELAY, 10000, 0),
        ("notification.sms", QueueType.STANDARD, 5000, 0),
        ("log.error", QueueType.STANDARD, 0, 86400000),
        ("log.info", QueueType.STANDARD, 0, 3600000),
        ("dlq.orders", QueueType.STANDARD, 0, 0),
    ]
    
    for name, q_type, max_len, ttl in queues_config:
        queue = manager.declare_queue(name, q_type, max_length=max_len, default_ttl_ms=ttl)
        print(f"  📬 {name} ({q_type.value})")
        
    # Bind queues
    print("\n🔗 Binding Queues...")
    
    bindings_config = [
        ("order.new", "orders", "new"),
        ("order.process", "orders", "process"),
        ("order.priority", "orders", "priority"),
        ("payment.process", "orders", "payment"),
        ("notification.email", "events", ""),
        ("notification.sms", "events", ""),
        ("log.error", "logs", "*.error"),
        ("log.info", "logs", "*.info"),
    ]
    
    for queue_name, exchange_name, routing_key in bindings_config:
        binding = manager.bind_queue(queue_name, exchange_name, routing_key)
        if binding:
            print(f"  🔗 {queue_name} <- {exchange_name} ({routing_key or '*'})")
            
    # Setup DLQ
    print("\n☠️ Setting up Dead Letter Queues...")
    
    manager.setup_dlq("order.new", "dlq.orders")
    manager.setup_dlq("order.process", "dlq.orders")
    print("  ✓ DLQ configured for order queues")
    
    # Create publishers
    print("\n📤 Creating Publishers...")
    
    publisher1 = manager.create_publisher(DeliveryMode.AT_LEAST_ONCE)
    publisher2 = manager.create_publisher(DeliveryMode.EXACTLY_ONCE)
    
    print(f"  📤 {publisher1.publisher_id}")
    print(f"  📤 {publisher2.publisher_id}")
    
    # Publish messages
    print("\n✉️ Publishing Messages...")
    
    # Direct exchange
    for i in range(5):
        await manager.publish(
            publisher1,
            "orders",
            "new",
            {"order_id": i, "amount": random.randint(10, 1000)}
        )
        
    print("  ✉️ Published 5 new orders")
    
    # Priority messages
    for i in range(3):
        await manager.publish(
            publisher1,
            "orders",
            "priority",
            {"order_id": i, "urgent": True},
            priority=random.randint(5, 9)
        )
        
    print("  ✉️ Published 3 priority orders")
    
    # Fanout exchange
    await manager.publish(
        publisher2,
        "events",
        "",
        {"type": "user_registered", "user_id": 123}
    )
    print("  ✉️ Published event to fanout")
    
    # Topic exchange
    await manager.publish(
        publisher1,
        "logs",
        "app.error",
        {"message": "Error occurred", "level": "error"}
    )
    await manager.publish(
        publisher1,
        "logs",
        "db.info",
        {"message": "Query executed", "level": "info"}
    )
    print("  ✉️ Published logs")
    
    # Delayed message
    await manager.publish(
        publisher1,
        "",
        "notification.email",
        {"to": "user@example.com", "subject": "Welcome"},
        delay_ms=5000
    )
    print("  ✉️ Published delayed notification")
    
    # Bulk publish
    print("\n📦 Bulk publishing...")
    
    for i in range(50):
        await manager.publish(
            random.choice([publisher1, publisher2]),
            random.choice(["orders", "events", ""]),
            random.choice(["new", "process", ""]),
            {"bulk_id": i, "data": f"data_{i}"}
        )
        
    print("  ✓ Published 50 bulk messages")
    
    # Create consumers
    print("\n📥 Creating Consumers...")
    
    consumers = []
    consumer_queues = ["order.new", "order.process", "order.priority", "log.error"]
    
    for queue_name in consumer_queues:
        consumer = manager.create_consumer(queue_name, prefetch_count=10)
        consumers.append(consumer)
        print(f"  📥 {consumer.consumer_id} -> {queue_name}")
        
    # Consume messages
    print("\n🔄 Consuming Messages...")
    
    for consumer in consumers:
        messages = await manager.consume(consumer, timeout_ms=1000)
        print(f"\n  📥 {consumer.queue_name}: {len(messages)} messages")
        
        for msg in messages[:3]:
            # Acknowledge
            await manager.ack(consumer, msg.message_id)
            
        remaining = messages[3:]
        for msg in remaining:
            # Reject some
            await manager.reject(consumer, msg.message_id, requeue=True)
            
    # Display queues
    print("\n📬 Queue Status:")
    
    print("\n  ┌─────────────────────────┬─────────────┬─────────────┬─────────────┬─────────────┐")
    print("  │ Queue                   │ Type        │ Ready       │ Delivered   │ Acked       │")
    print("  ├─────────────────────────┼─────────────┼─────────────┼─────────────┼─────────────┤")
    
    for queue in manager.queues.values():
        stats = manager.get_queue_stats(queue.name)
        name = queue.name[:23].ljust(23)
        q_type = stats['type'][:11].ljust(11)
        ready = str(stats['ready']).ljust(11)
        delivered = str(stats['delivered']).ljust(11)
        acked = str(stats['acknowledged']).ljust(11)
        
        print(f"  │ {name} │ {q_type} │ {ready} │ {delivered} │ {acked} │")
        
    print("  └─────────────────────────┴─────────────┴─────────────┴─────────────┴─────────────┘")
    
    # Display exchanges
    print("\n📤 Exchange Statistics:")
    
    for exchange in manager.exchanges.values():
        if not exchange.name:
            continue
        print(f"\n  📤 {exchange.name}:")
        print(f"    Type: {exchange.exchange_type.value}")
        print(f"    Bindings: {len(exchange.bindings)}")
        print(f"    Messages In: {exchange.messages_in}")
        print(f"    Messages Routed: {exchange.messages_routed}")
        
    # Consumer statistics
    print("\n📥 Consumer Statistics:")
    
    for consumer in consumers:
        print(f"\n  📥 {consumer.consumer_id}:")
        print(f"    Queue: {consumer.queue_name}")
        print(f"    Consumed: {consumer.messages_consumed}")
        print(f"    Acked: {consumer.messages_acked}")
        print(f"    Pending: {len(consumer.pending_acks)}")
        
    # Publisher statistics
    print("\n📤 Publisher Statistics:")
    
    for publisher in manager.publishers.values():
        print(f"\n  📤 {publisher.publisher_id}:")
        print(f"    Mode: {publisher.delivery_mode.value}")
        print(f"    Published: {publisher.messages_published}")
        print(f"    Returned: {publisher.messages_returned}")
        
    # Message flow
    print("\n📊 Message Flow:")
    
    total_in = sum(e.messages_in for e in manager.exchanges.values())
    total_routed = sum(e.messages_routed for e in manager.exchanges.values())
    total_ready = sum(len(q.messages) + len(q.priority_heap) for q in manager.queues.values())
    
    print(f"\n  → Exchanges In: {total_in}")
    print(f"  → Routed: {total_routed}")
    print(f"  → Ready in Queues: {total_ready}")
    print(f"  → Delivered: {manager.messages_delivered}")
    print(f"  → Acknowledged: {manager.messages_acked}")
    
    # Statistics
    print("\n📈 Platform Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Queues: {stats['queues']}")
    print(f"  Exchanges: {stats['exchanges']}")
    print(f"  Consumers: {stats['consumers']}")
    print(f"  Publishers: {stats['publishers']}")
    print(f"\n  Messages Total: {stats['messages_total']}")
    print(f"  Messages Ready: {stats['messages_ready']}")
    print(f"  Messages Delivered: {stats['messages_delivered']}")
    print(f"  Messages Acked: {stats['messages_acked']}")
    
    ack_rate = stats['messages_acked'] / max(stats['messages_delivered'], 1) * 100
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                     Message Queue Dashboard                         │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Queues:                        {stats['queues']:>12}                        │")
    print(f"│ Exchanges:                     {stats['exchanges']:>12}                        │")
    print(f"│ Active Consumers:              {stats['consumers']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Messages Total:                {stats['messages_total']:>12}                        │")
    print(f"│ Messages Ready:                {stats['messages_ready']:>12}                        │")
    print(f"│ Acknowledgment Rate:           {ack_rate:>11.1f}%                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Message Queue Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
