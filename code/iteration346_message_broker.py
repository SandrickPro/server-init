#!/usr/bin/env python3
"""
Server Init - Iteration 346: Message Broker Platform
Платформа брокера сообщений

Функционал:
- Message Queues - очереди сообщений
- Topic Exchange - обмен по топикам
- Direct Exchange - прямой обмен
- Fanout Exchange - широковещательный обмен
- Dead Letter Handling - обработка недоставленных
- Message Retry - повторные попытки
- Queue Metrics - метрики очередей
- Consumer Groups - группы потребителей
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
import uuid
import json
import hashlib


class ExchangeType(Enum):
    """Тип обмена"""
    DIRECT = "direct"
    FANOUT = "fanout"
    TOPIC = "topic"
    HEADERS = "headers"


class MessageStatus(Enum):
    """Статус сообщения"""
    PENDING = "pending"
    DELIVERED = "delivered"
    ACKNOWLEDGED = "acknowledged"
    REJECTED = "rejected"
    DEAD_LETTERED = "dead_lettered"
    EXPIRED = "expired"


class QueueType(Enum):
    """Тип очереди"""
    STANDARD = "standard"
    PRIORITY = "priority"
    DELAY = "delay"
    DEAD_LETTER = "dead_letter"


class DeliveryMode(Enum):
    """Режим доставки"""
    TRANSIENT = "transient"
    PERSISTENT = "persistent"


class AcknowledgeMode(Enum):
    """Режим подтверждения"""
    AUTO = "auto"
    MANUAL = "manual"
    NONE = "none"


class ConsumerState(Enum):
    """Состояние потребителя"""
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class ConnectionState(Enum):
    """Состояние соединения"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    BLOCKED = "blocked"


@dataclass
class Message:
    """Сообщение"""
    message_id: str
    
    # Content
    body: bytes = b""
    content_type: str = "application/json"
    content_encoding: str = "utf-8"
    
    # Routing
    routing_key: str = ""
    exchange: str = ""
    
    # Properties
    headers: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    correlation_id: str = ""
    reply_to: str = ""
    
    # Delivery
    delivery_mode: DeliveryMode = DeliveryMode.PERSISTENT
    expiration: int = 0  # TTL in ms
    
    # Status
    status: MessageStatus = MessageStatus.PENDING
    
    # Retry
    retry_count: int = 0
    max_retries: int = 3
    
    # Timestamps
    timestamp: datetime = field(default_factory=datetime.now)
    delivered_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None


@dataclass
class Queue:
    """Очередь"""
    queue_id: str
    name: str
    
    # Type
    queue_type: QueueType = QueueType.STANDARD
    
    # Configuration
    durable: bool = True
    exclusive: bool = False
    auto_delete: bool = False
    
    # Limits
    max_length: int = 0  # 0 = unlimited
    max_length_bytes: int = 0
    max_priority: int = 10
    
    # TTL
    message_ttl: int = 0
    expires: int = 0
    
    # Dead Letter
    dead_letter_exchange: str = ""
    dead_letter_routing_key: str = ""
    
    # Arguments
    arguments: Dict[str, Any] = field(default_factory=dict)
    
    # Stats
    message_count: int = 0
    consumer_count: int = 0
    ready_messages: int = 0
    unacked_messages: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Exchange:
    """Обмен"""
    exchange_id: str
    name: str
    
    # Type
    exchange_type: ExchangeType = ExchangeType.DIRECT
    
    # Configuration
    durable: bool = True
    auto_delete: bool = False
    internal: bool = False
    
    # Arguments
    arguments: Dict[str, Any] = field(default_factory=dict)
    
    # Alternate exchange
    alternate_exchange: str = ""
    
    # Stats
    messages_in: int = 0
    messages_out: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Binding:
    """Привязка"""
    binding_id: str
    
    # Source/Destination
    source: str = ""  # Exchange name
    destination: str = ""  # Queue or Exchange name
    destination_type: str = "queue"  # queue or exchange
    
    # Routing
    routing_key: str = ""
    
    # Arguments
    arguments: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Consumer:
    """Потребитель"""
    consumer_id: str
    consumer_tag: str = ""
    
    # Queue
    queue_name: str = ""
    
    # Configuration
    prefetch_count: int = 10
    acknowledge_mode: AcknowledgeMode = AcknowledgeMode.MANUAL
    exclusive: bool = False
    
    # State
    state: ConsumerState = ConsumerState.ACTIVE
    
    # Consumer group
    consumer_group: str = ""
    
    # Stats
    messages_consumed: int = 0
    messages_acknowledged: int = 0
    messages_rejected: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: Optional[datetime] = None


@dataclass
class ConsumerGroup:
    """Группа потребителей"""
    group_id: str
    name: str
    
    # Members
    consumer_ids: List[str] = field(default_factory=list)
    
    # Strategy
    load_balancing: str = "round_robin"  # round_robin, least_conn, random
    
    # Stats
    total_consumed: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Connection:
    """Соединение"""
    connection_id: str
    name: str = ""
    
    # Client
    client_id: str = ""
    client_host: str = ""
    client_port: int = 0
    
    # Protocol
    protocol: str = "AMQP 0-9-1"
    
    # State
    state: ConnectionState = ConnectionState.CONNECTED
    
    # Channels
    channel_count: int = 0
    channel_max: int = 0
    
    # Stats
    messages_sent: int = 0
    messages_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    
    # Timestamps
    connected_at: datetime = field(default_factory=datetime.now)


@dataclass
class Channel:
    """Канал"""
    channel_id: str
    channel_number: int = 0
    
    # Connection
    connection_id: str = ""
    
    # State
    is_open: bool = True
    is_flow: bool = True
    
    # Prefetch
    prefetch_count: int = 0
    prefetch_size: int = 0
    
    # Stats
    messages_published: int = 0
    messages_delivered: int = 0
    messages_acknowledged: int = 0
    
    # Timestamps
    opened_at: datetime = field(default_factory=datetime.now)


@dataclass
class DeadLetterEntry:
    """Запись недоставленного сообщения"""
    entry_id: str
    
    # Original message
    message_id: str = ""
    original_queue: str = ""
    original_exchange: str = ""
    original_routing_key: str = ""
    
    # Reason
    reason: str = ""  # rejected, expired, max_length
    
    # Body
    body: bytes = b""
    headers: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    dead_lettered_at: datetime = field(default_factory=datetime.now)


@dataclass
class QueueMetrics:
    """Метрики очереди"""
    metrics_id: str
    queue_name: str
    
    # Messages
    message_count: int = 0
    ready_count: int = 0
    unacked_count: int = 0
    
    # Rates
    publish_rate: float = 0.0
    deliver_rate: float = 0.0
    ack_rate: float = 0.0
    
    # Memory
    memory_bytes: int = 0
    
    # Consumers
    consumer_count: int = 0
    
    # Timestamp
    collected_at: datetime = field(default_factory=datetime.now)


@dataclass
class VirtualHost:
    """Виртуальный хост"""
    vhost_id: str
    name: str
    
    # Description
    description: str = ""
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Limits
    max_queues: int = 0
    max_connections: int = 0
    
    # Stats
    queue_count: int = 0
    exchange_count: int = 0
    connection_count: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


class MessageBroker:
    """Брокер сообщений"""
    
    def __init__(self):
        self.messages: Dict[str, Message] = {}
        self.queues: Dict[str, Queue] = {}
        self.exchanges: Dict[str, Exchange] = {}
        self.bindings: Dict[str, Binding] = {}
        self.consumers: Dict[str, Consumer] = {}
        self.consumer_groups: Dict[str, ConsumerGroup] = {}
        self.connections: Dict[str, Connection] = {}
        self.channels: Dict[str, Channel] = {}
        self.dead_letters: Dict[str, DeadLetterEntry] = {}
        self.queue_metrics: Dict[str, QueueMetrics] = {}
        self.vhosts: Dict[str, VirtualHost] = {}
        
        # Queue message buffers
        self.queue_messages: Dict[str, List[str]] = {}
        
        # Stats
        self.total_published = 0
        self.total_delivered = 0
        self.total_acknowledged = 0
        
    async def create_vhost(self, name: str,
                          description: str = "",
                          tags: List[str] = None,
                          max_queues: int = 0,
                          max_connections: int = 0) -> VirtualHost:
        """Создание виртуального хоста"""
        vhost = VirtualHost(
            vhost_id=f"vhost_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            tags=tags or [],
            max_queues=max_queues,
            max_connections=max_connections
        )
        
        self.vhosts[vhost.vhost_id] = vhost
        return vhost
        
    async def declare_exchange(self, name: str,
                              exchange_type: ExchangeType = ExchangeType.DIRECT,
                              durable: bool = True,
                              auto_delete: bool = False,
                              internal: bool = False,
                              alternate_exchange: str = "",
                              arguments: Dict[str, Any] = None) -> Exchange:
        """Объявление обмена"""
        exchange = Exchange(
            exchange_id=f"ex_{uuid.uuid4().hex[:8]}",
            name=name,
            exchange_type=exchange_type,
            durable=durable,
            auto_delete=auto_delete,
            internal=internal,
            alternate_exchange=alternate_exchange,
            arguments=arguments or {}
        )
        
        self.exchanges[exchange.exchange_id] = exchange
        return exchange
        
    async def declare_queue(self, name: str,
                           queue_type: QueueType = QueueType.STANDARD,
                           durable: bool = True,
                           exclusive: bool = False,
                           auto_delete: bool = False,
                           max_length: int = 0,
                           max_priority: int = 10,
                           message_ttl: int = 0,
                           dead_letter_exchange: str = "",
                           dead_letter_routing_key: str = "",
                           arguments: Dict[str, Any] = None) -> Queue:
        """Объявление очереди"""
        queue = Queue(
            queue_id=f"q_{uuid.uuid4().hex[:8]}",
            name=name,
            queue_type=queue_type,
            durable=durable,
            exclusive=exclusive,
            auto_delete=auto_delete,
            max_length=max_length,
            max_priority=max_priority,
            message_ttl=message_ttl,
            dead_letter_exchange=dead_letter_exchange,
            dead_letter_routing_key=dead_letter_routing_key,
            arguments=arguments or {}
        )
        
        self.queues[queue.queue_id] = queue
        self.queue_messages[name] = []
        return queue
        
    async def bind_queue(self, exchange_name: str,
                        queue_name: str,
                        routing_key: str = "",
                        arguments: Dict[str, Any] = None) -> Binding:
        """Привязка очереди к обмену"""
        binding = Binding(
            binding_id=f"bind_{uuid.uuid4().hex[:8]}",
            source=exchange_name,
            destination=queue_name,
            destination_type="queue",
            routing_key=routing_key,
            arguments=arguments or {}
        )
        
        self.bindings[binding.binding_id] = binding
        return binding
        
    async def publish_message(self, exchange_name: str,
                             routing_key: str,
                             body: bytes,
                             content_type: str = "application/json",
                             headers: Dict[str, Any] = None,
                             priority: int = 0,
                             delivery_mode: DeliveryMode = DeliveryMode.PERSISTENT,
                             expiration: int = 0,
                             correlation_id: str = "",
                             reply_to: str = "") -> Message:
        """Публикация сообщения"""
        message = Message(
            message_id=f"msg_{uuid.uuid4().hex[:12]}",
            body=body,
            content_type=content_type,
            routing_key=routing_key,
            exchange=exchange_name,
            headers=headers or {},
            priority=priority,
            delivery_mode=delivery_mode,
            expiration=expiration,
            correlation_id=correlation_id,
            reply_to=reply_to
        )
        
        self.messages[message.message_id] = message
        self.total_published += 1
        
        # Route message to queues
        await self._route_message(message)
        
        # Update exchange stats
        exchange = self._find_exchange_by_name(exchange_name)
        if exchange:
            exchange.messages_in += 1
            
        return message
        
    def _find_exchange_by_name(self, name: str) -> Optional[Exchange]:
        """Поиск обмена по имени"""
        for ex in self.exchanges.values():
            if ex.name == name:
                return ex
        return None
        
    def _find_queue_by_name(self, name: str) -> Optional[Queue]:
        """Поиск очереди по имени"""
        for q in self.queues.values():
            if q.name == name:
                return q
        return None
        
    async def _route_message(self, message: Message):
        """Маршрутизация сообщения"""
        exchange = self._find_exchange_by_name(message.exchange)
        if not exchange:
            return
            
        # Find matching bindings
        for binding in self.bindings.values():
            if binding.source != message.exchange:
                continue
                
            if binding.destination_type != "queue":
                continue
                
            # Check routing based on exchange type
            if exchange.exchange_type == ExchangeType.FANOUT:
                await self._deliver_to_queue(binding.destination, message)
            elif exchange.exchange_type == ExchangeType.DIRECT:
                if binding.routing_key == message.routing_key:
                    await self._deliver_to_queue(binding.destination, message)
            elif exchange.exchange_type == ExchangeType.TOPIC:
                if self._match_topic(binding.routing_key, message.routing_key):
                    await self._deliver_to_queue(binding.destination, message)
            elif exchange.exchange_type == ExchangeType.HEADERS:
                if self._match_headers(binding.arguments, message.headers):
                    await self._deliver_to_queue(binding.destination, message)
                    
        exchange.messages_out += 1
        
    def _match_topic(self, pattern: str, routing_key: str) -> bool:
        """Сопоставление топика"""
        pattern_parts = pattern.split(".")
        key_parts = routing_key.split(".")
        
        i, j = 0, 0
        while i < len(pattern_parts) and j < len(key_parts):
            if pattern_parts[i] == "#":
                return True
            elif pattern_parts[i] == "*":
                i += 1
                j += 1
            elif pattern_parts[i] == key_parts[j]:
                i += 1
                j += 1
            else:
                return False
                
        return i == len(pattern_parts) and j == len(key_parts)
        
    def _match_headers(self, binding_headers: Dict[str, Any],
                      message_headers: Dict[str, Any]) -> bool:
        """Сопоставление заголовков"""
        x_match = binding_headers.get("x-match", "all")
        
        matches = 0
        for key, value in binding_headers.items():
            if key.startswith("x-"):
                continue
            if message_headers.get(key) == value:
                matches += 1
                
        if x_match == "all":
            return matches == len([k for k in binding_headers if not k.startswith("x-")])
        else:  # any
            return matches > 0
            
    async def _deliver_to_queue(self, queue_name: str, message: Message):
        """Доставка сообщения в очередь"""
        queue = self._find_queue_by_name(queue_name)
        if not queue:
            return
            
        # Check queue limits
        if queue.max_length > 0 and queue.message_count >= queue.max_length:
            await self._dead_letter_message(message, queue, "max_length")
            return
            
        # Add to queue
        if queue_name in self.queue_messages:
            self.queue_messages[queue_name].append(message.message_id)
            
        queue.message_count += 1
        queue.ready_messages += 1
        message.status = MessageStatus.DELIVERED
        message.delivered_at = datetime.now()
        self.total_delivered += 1
        
    async def _dead_letter_message(self, message: Message, queue: Queue, reason: str):
        """Перемещение сообщения в очередь недоставленных"""
        entry = DeadLetterEntry(
            entry_id=f"dlq_{uuid.uuid4().hex[:8]}",
            message_id=message.message_id,
            original_queue=queue.name,
            original_exchange=message.exchange,
            original_routing_key=message.routing_key,
            reason=reason,
            body=message.body,
            headers=message.headers
        )
        
        self.dead_letters[entry.entry_id] = entry
        message.status = MessageStatus.DEAD_LETTERED
        
        # Republish to DLX if configured
        if queue.dead_letter_exchange:
            dlx_routing_key = queue.dead_letter_routing_key or message.routing_key
            await self.publish_message(
                queue.dead_letter_exchange,
                dlx_routing_key,
                message.body,
                message.content_type,
                message.headers
            )
            
    async def consume_message(self, consumer_id: str) -> Optional[Message]:
        """Получение сообщения потребителем"""
        consumer = self.consumers.get(consumer_id)
        if not consumer or consumer.state != ConsumerState.ACTIVE:
            return None
            
        queue = self._find_queue_by_name(consumer.queue_name)
        if not queue:
            return None
            
        # Get message from queue
        if consumer.queue_name not in self.queue_messages:
            return None
            
        queue_msgs = self.queue_messages[consumer.queue_name]
        if not queue_msgs:
            return None
            
        message_id = queue_msgs.pop(0)
        message = self.messages.get(message_id)
        
        if message:
            queue.ready_messages -= 1
            queue.unacked_messages += 1
            consumer.messages_consumed += 1
            consumer.last_activity = datetime.now()
            
            # Auto-acknowledge if configured
            if consumer.acknowledge_mode == AcknowledgeMode.AUTO:
                await self.acknowledge_message(message_id, consumer_id)
                
        return message
        
    async def acknowledge_message(self, message_id: str,
                                 consumer_id: str) -> bool:
        """Подтверждение сообщения"""
        message = self.messages.get(message_id)
        consumer = self.consumers.get(consumer_id)
        
        if not message or not consumer:
            return False
            
        queue = self._find_queue_by_name(consumer.queue_name)
        if queue:
            queue.unacked_messages = max(0, queue.unacked_messages - 1)
            queue.message_count = max(0, queue.message_count - 1)
            
        message.status = MessageStatus.ACKNOWLEDGED
        message.acknowledged_at = datetime.now()
        consumer.messages_acknowledged += 1
        self.total_acknowledged += 1
        
        return True
        
    async def reject_message(self, message_id: str,
                            consumer_id: str,
                            requeue: bool = False) -> bool:
        """Отклонение сообщения"""
        message = self.messages.get(message_id)
        consumer = self.consumers.get(consumer_id)
        
        if not message or not consumer:
            return False
            
        queue = self._find_queue_by_name(consumer.queue_name)
        
        if requeue and queue:
            # Requeue the message
            if consumer.queue_name in self.queue_messages:
                self.queue_messages[consumer.queue_name].append(message_id)
            queue.ready_messages += 1
            queue.unacked_messages = max(0, queue.unacked_messages - 1)
        else:
            message.status = MessageStatus.REJECTED
            message.retry_count += 1
            
            if message.retry_count >= message.max_retries and queue:
                await self._dead_letter_message(message, queue, "rejected")
            elif queue:
                queue.unacked_messages = max(0, queue.unacked_messages - 1)
                queue.message_count = max(0, queue.message_count - 1)
                
        consumer.messages_rejected += 1
        return True
        
    async def create_consumer(self, queue_name: str,
                             consumer_tag: str = "",
                             prefetch_count: int = 10,
                             acknowledge_mode: AcknowledgeMode = AcknowledgeMode.MANUAL,
                             exclusive: bool = False,
                             consumer_group: str = "") -> Optional[Consumer]:
        """Создание потребителя"""
        queue = self._find_queue_by_name(queue_name)
        if not queue:
            return None
            
        consumer = Consumer(
            consumer_id=f"cons_{uuid.uuid4().hex[:8]}",
            consumer_tag=consumer_tag or f"ctag_{uuid.uuid4().hex[:8]}",
            queue_name=queue_name,
            prefetch_count=prefetch_count,
            acknowledge_mode=acknowledge_mode,
            exclusive=exclusive,
            consumer_group=consumer_group
        )
        
        self.consumers[consumer.consumer_id] = consumer
        queue.consumer_count += 1
        
        # Add to consumer group if specified
        if consumer_group:
            group = self._find_consumer_group_by_name(consumer_group)
            if group:
                group.consumer_ids.append(consumer.consumer_id)
                
        return consumer
        
    def _find_consumer_group_by_name(self, name: str) -> Optional[ConsumerGroup]:
        """Поиск группы потребителей"""
        for group in self.consumer_groups.values():
            if group.name == name:
                return group
        return None
        
    async def create_consumer_group(self, name: str,
                                   load_balancing: str = "round_robin") -> ConsumerGroup:
        """Создание группы потребителей"""
        group = ConsumerGroup(
            group_id=f"cg_{uuid.uuid4().hex[:8]}",
            name=name,
            load_balancing=load_balancing
        )
        
        self.consumer_groups[group.group_id] = group
        return group
        
    async def create_connection(self, name: str = "",
                               client_id: str = "",
                               client_host: str = "",
                               channel_max: int = 0) -> Connection:
        """Создание соединения"""
        connection = Connection(
            connection_id=f"conn_{uuid.uuid4().hex[:8]}",
            name=name,
            client_id=client_id,
            client_host=client_host,
            channel_max=channel_max
        )
        
        self.connections[connection.connection_id] = connection
        return connection
        
    async def create_channel(self, connection_id: str,
                            prefetch_count: int = 0) -> Optional[Channel]:
        """Создание канала"""
        connection = self.connections.get(connection_id)
        if not connection:
            return None
            
        channel = Channel(
            channel_id=f"ch_{uuid.uuid4().hex[:8]}",
            channel_number=connection.channel_count + 1,
            connection_id=connection_id,
            prefetch_count=prefetch_count
        )
        
        self.channels[channel.channel_id] = channel
        connection.channel_count += 1
        
        return channel
        
    async def collect_queue_metrics(self, queue_name: str) -> Optional[QueueMetrics]:
        """Сбор метрик очереди"""
        queue = self._find_queue_by_name(queue_name)
        if not queue:
            return None
            
        metrics = QueueMetrics(
            metrics_id=f"qm_{uuid.uuid4().hex[:8]}",
            queue_name=queue_name,
            message_count=queue.message_count,
            ready_count=queue.ready_messages,
            unacked_count=queue.unacked_messages,
            publish_rate=random.uniform(10, 1000),
            deliver_rate=random.uniform(10, 1000),
            ack_rate=random.uniform(10, 1000),
            memory_bytes=random.randint(1000000, 100000000),
            consumer_count=queue.consumer_count
        )
        
        self.queue_metrics[metrics.metrics_id] = metrics
        return metrics
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_exchanges = len(self.exchanges)
        total_queues = len(self.queues)
        total_bindings = len(self.bindings)
        total_consumers = len(self.consumers)
        active_consumers = sum(1 for c in self.consumers.values() if c.state == ConsumerState.ACTIVE)
        total_connections = len(self.connections)
        connected = sum(1 for c in self.connections.values() if c.state == ConnectionState.CONNECTED)
        total_channels = len(self.channels)
        total_messages = len(self.messages)
        pending_messages = sum(1 for m in self.messages.values() if m.status == MessageStatus.PENDING)
        dead_letters = len(self.dead_letters)
        
        return {
            "total_exchanges": total_exchanges,
            "total_queues": total_queues,
            "total_bindings": total_bindings,
            "total_consumers": total_consumers,
            "active_consumers": active_consumers,
            "total_connections": total_connections,
            "connected": connected,
            "total_channels": total_channels,
            "total_messages": total_messages,
            "pending_messages": pending_messages,
            "dead_letters": dead_letters,
            "total_published": self.total_published,
            "total_delivered": self.total_delivered,
            "total_acknowledged": self.total_acknowledged
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 346: Message Broker Platform")
    print("=" * 60)
    
    broker = MessageBroker()
    print("✓ Message Broker initialized")
    
    # Create Virtual Hosts
    print("\n🏠 Creating Virtual Hosts...")
    
    vhosts_data = [
        ("/", "Default virtual host", ["production"], 0, 0),
        ("/staging", "Staging environment", ["staging"], 100, 50),
        ("/development", "Development environment", ["dev"], 50, 20),
        ("/test", "Test environment", ["test"], 20, 10)
    ]
    
    vhosts = []
    for name, desc, tags, max_q, max_c in vhosts_data:
        vh = await broker.create_vhost(name, desc, tags, max_q, max_c)
        vhosts.append(vh)
        print(f"  🏠 {name}")
        
    # Create Exchanges
    print("\n📬 Creating Exchanges...")
    
    exchanges_data = [
        ("orders", ExchangeType.TOPIC, True, False),
        ("notifications", ExchangeType.FANOUT, True, False),
        ("payments", ExchangeType.DIRECT, True, False),
        ("events", ExchangeType.TOPIC, True, False),
        ("logs", ExchangeType.FANOUT, True, True),
        ("dlx", ExchangeType.DIRECT, True, False),
        ("headers.exchange", ExchangeType.HEADERS, True, False)
    ]
    
    exchanges = []
    for name, etype, durable, internal in exchanges_data:
        ex = await broker.declare_exchange(name, etype, durable, False, internal)
        exchanges.append(ex)
        print(f"  📬 {name} ({etype.value})")
        
    # Create Queues
    print("\n📥 Creating Queues...")
    
    queues_data = [
        ("orders.created", QueueType.STANDARD, True, 10000, 10, 86400000, "dlx", "orders.dead"),
        ("orders.processing", QueueType.PRIORITY, True, 5000, 10, 3600000, "dlx", "orders.dead"),
        ("orders.completed", QueueType.STANDARD, True, 10000, 10, 86400000, "", ""),
        ("notifications.email", QueueType.STANDARD, True, 50000, 5, 300000, "dlx", "notifications.dead"),
        ("notifications.sms", QueueType.STANDARD, True, 10000, 5, 60000, "dlx", "notifications.dead"),
        ("notifications.push", QueueType.STANDARD, True, 100000, 5, 60000, "", ""),
        ("payments.pending", QueueType.PRIORITY, True, 1000, 10, 3600000, "dlx", "payments.dead"),
        ("payments.completed", QueueType.STANDARD, True, 10000, 10, 86400000, "", ""),
        ("events.analytics", QueueType.STANDARD, True, 0, 10, 0, "", ""),
        ("dlq.orders", QueueType.DEAD_LETTER, True, 0, 10, 604800000, "", ""),
        ("dlq.notifications", QueueType.DEAD_LETTER, True, 0, 10, 604800000, "", ""),
        ("dlq.payments", QueueType.DEAD_LETTER, True, 0, 10, 604800000, "", "")
    ]
    
    queues = []
    for name, qtype, durable, max_len, max_pri, ttl, dlx, dlrk in queues_data:
        q = await broker.declare_queue(name, qtype, durable, False, False, max_len, max_pri, ttl, dlx, dlrk)
        queues.append(q)
        print(f"  📥 {name} ({qtype.value})")
        
    # Create Bindings
    print("\n🔗 Creating Bindings...")
    
    bindings_data = [
        ("orders", "orders.created", "order.created"),
        ("orders", "orders.processing", "order.#"),
        ("orders", "orders.completed", "order.completed"),
        ("notifications", "notifications.email", ""),
        ("notifications", "notifications.sms", ""),
        ("notifications", "notifications.push", ""),
        ("payments", "payments.pending", "payment.pending"),
        ("payments", "payments.completed", "payment.completed"),
        ("events", "events.analytics", "event.#"),
        ("dlx", "dlq.orders", "orders.dead"),
        ("dlx", "dlq.notifications", "notifications.dead"),
        ("dlx", "dlq.payments", "payments.dead")
    ]
    
    bindings = []
    for ex_name, q_name, rk in bindings_data:
        b = await broker.bind_queue(ex_name, q_name, rk)
        bindings.append(b)
        print(f"  🔗 {ex_name} → {q_name} ({rk or '*'})")
        
    # Create Connections
    print("\n🔌 Creating Connections...")
    
    connections_data = [
        ("order-service", "order-svc-001", "10.0.0.10", 2047),
        ("notification-service", "notif-svc-001", "10.0.0.11", 2047),
        ("payment-service", "pay-svc-001", "10.0.0.12", 2047),
        ("analytics-service", "analytics-001", "10.0.0.13", 1023),
        ("web-backend", "web-001", "10.0.0.20", 511)
    ]
    
    connections = []
    for name, client, host, max_ch in connections_data:
        conn = await broker.create_connection(name, client, host, max_ch)
        connections.append(conn)
        print(f"  🔌 {name} ({host})")
        
    # Create Channels
    print("\n📡 Creating Channels...")
    
    channels = []
    for conn in connections:
        for _ in range(random.randint(1, 5)):
            ch = await broker.create_channel(conn.connection_id, random.randint(10, 100))
            if ch:
                channels.append(ch)
                
    print(f"  📡 Created {len(channels)} channels")
    
    # Create Consumer Groups
    print("\n👥 Creating Consumer Groups...")
    
    groups_data = [
        ("order-processors", "round_robin"),
        ("notification-workers", "least_conn"),
        ("payment-handlers", "round_robin"),
        ("analytics-consumers", "random")
    ]
    
    groups = []
    for name, lb in groups_data:
        g = await broker.create_consumer_group(name, lb)
        groups.append(g)
        print(f"  👥 {name} ({lb})")
        
    # Create Consumers
    print("\n🤖 Creating Consumers...")
    
    consumers_data = [
        ("orders.created", "order-consumer-1", 10, AcknowledgeMode.MANUAL, "order-processors"),
        ("orders.created", "order-consumer-2", 10, AcknowledgeMode.MANUAL, "order-processors"),
        ("orders.processing", "order-processor-1", 5, AcknowledgeMode.MANUAL, "order-processors"),
        ("notifications.email", "email-worker-1", 20, AcknowledgeMode.AUTO, "notification-workers"),
        ("notifications.email", "email-worker-2", 20, AcknowledgeMode.AUTO, "notification-workers"),
        ("notifications.sms", "sms-worker-1", 10, AcknowledgeMode.AUTO, "notification-workers"),
        ("notifications.push", "push-worker-1", 50, AcknowledgeMode.AUTO, "notification-workers"),
        ("payments.pending", "payment-handler-1", 5, AcknowledgeMode.MANUAL, "payment-handlers"),
        ("events.analytics", "analytics-consumer-1", 100, AcknowledgeMode.AUTO, "analytics-consumers")
    ]
    
    consumers = []
    for q_name, tag, prefetch, ack_mode, group in consumers_data:
        c = await broker.create_consumer(q_name, tag, prefetch, ack_mode, False, group)
        if c:
            consumers.append(c)
            print(f"  🤖 {tag} → {q_name}")
            
    # Publish Messages
    print("\n📤 Publishing Messages...")
    
    messages = []
    
    # Order messages
    for i in range(10):
        body = json.dumps({"order_id": f"ord_{i:05d}", "status": "created", "amount": random.uniform(10, 1000)}).encode()
        msg = await broker.publish_message("orders", "order.created", body, priority=random.randint(0, 9))
        messages.append(msg)
        
    # Notification messages
    for i in range(20):
        body = json.dumps({"user_id": f"user_{i:05d}", "type": random.choice(["email", "sms", "push"])}).encode()
        msg = await broker.publish_message("notifications", "", body)
        messages.append(msg)
        
    # Payment messages
    for i in range(5):
        body = json.dumps({"payment_id": f"pay_{i:05d}", "amount": random.uniform(50, 500)}).encode()
        msg = await broker.publish_message("payments", "payment.pending", body, priority=random.randint(5, 10))
        messages.append(msg)
        
    # Event messages
    for i in range(30):
        body = json.dumps({"event_type": random.choice(["click", "view", "purchase"]), "timestamp": datetime.now().isoformat()}).encode()
        msg = await broker.publish_message("events", f"event.{random.choice(['web', 'mobile', 'api'])}", body)
        messages.append(msg)
        
    print(f"  📤 Published {len(messages)} messages")
    
    # Consume and acknowledge messages
    print("\n📬 Consuming Messages...")
    
    consumed = 0
    acknowledged = 0
    
    for consumer in consumers[:5]:
        for _ in range(3):
            msg = await broker.consume_message(consumer.consumer_id)
            if msg:
                consumed += 1
                if consumer.acknowledge_mode == AcknowledgeMode.MANUAL:
                    if random.random() > 0.1:  # 90% acknowledge
                        await broker.acknowledge_message(msg.message_id, consumer.consumer_id)
                        acknowledged += 1
                    else:
                        await broker.reject_message(msg.message_id, consumer.consumer_id, requeue=random.random() > 0.5)
                        
    print(f"  📬 Consumed {consumed} messages, acknowledged {acknowledged}")
    
    # Collect Queue Metrics
    print("\n📊 Collecting Queue Metrics...")
    
    queue_metrics = []
    for q in queues[:6]:
        m = await broker.collect_queue_metrics(q.name)
        if m:
            queue_metrics.append(m)
            
    print(f"  📊 Collected metrics for {len(queue_metrics)} queues")
    
    # Exchanges Dashboard
    print("\n📬 Exchanges:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                    │ Type      │ Durable │ Internal │ Messages In │ Messages Out │ Alternate Exchange                              │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for ex in exchanges:
        name = ex.name[:23].ljust(23)
        etype = ex.exchange_type.value[:9].ljust(9)
        durable = "Yes" if ex.durable else "No"
        durable = durable.ljust(7)
        internal = "Yes" if ex.internal else "No"
        internal = internal.ljust(8)
        msg_in = str(ex.messages_in).ljust(11)
        msg_out = str(ex.messages_out).ljust(12)
        alt = ex.alternate_exchange if ex.alternate_exchange else "N/A"
        alt = alt[:49].ljust(49)
        
        print(f"  │ {name} │ {etype} │ {durable} │ {internal} │ {msg_in} │ {msg_out} │ {alt} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Queues
    print("\n📥 Queues:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                    │ Type        │ Messages │ Ready │ Unacked │ Consumers │ Max Length │ TTL (s)   │ DLX                 │ State                                                                                                    │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for q in queues:
        name = q.name[:23].ljust(23)
        qtype = q.queue_type.value[:11].ljust(11)
        msgs = str(q.message_count).ljust(8)
        ready = str(q.ready_messages).ljust(5)
        unacked = str(q.unacked_messages).ljust(7)
        cons = str(q.consumer_count).ljust(9)
        max_len = str(q.max_length) if q.max_length > 0 else "∞"
        max_len = max_len[:10].ljust(10)
        ttl = str(q.message_ttl // 1000) if q.message_ttl > 0 else "∞"
        ttl = ttl[:9].ljust(9)
        dlx = q.dead_letter_exchange if q.dead_letter_exchange else "N/A"
        dlx = dlx[:19].ljust(19)
        state = "🟢 Active" if q.durable else "⚫ Transient"
        state = state[:106].ljust(106)
        
        print(f"  │ {name} │ {qtype} │ {msgs} │ {ready} │ {unacked} │ {cons} │ {max_len} │ {ttl} │ {dlx} │ {state} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Connections
    print("\n🔌 Connections:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                    │ Client ID            │ Host           │ State      │ Channels │ Messages Sent │ Messages Recv │ Connected                             │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for conn in connections:
        name = conn.name[:23].ljust(23)
        client = conn.client_id[:20].ljust(20)
        host = conn.client_host[:14].ljust(14)
        
        state_icons = {"connected": "🟢", "disconnected": "⚫", "blocked": "🟡"}
        state_icon = state_icons.get(conn.state.value, "?")
        state = f"{state_icon} {conn.state.value}"[:10].ljust(10)
        
        channels_cnt = str(conn.channel_count).ljust(8)
        sent = str(conn.messages_sent).ljust(13)
        recv = str(conn.messages_received).ljust(13)
        connected = conn.connected_at.strftime("%Y-%m-%d %H:%M:%S")[:39].ljust(39)
        
        print(f"  │ {name} │ {client} │ {host} │ {state} │ {channels_cnt} │ {sent} │ {recv} │ {connected} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Consumers
    print("\n🤖 Consumers:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Tag                      │ Queue                   │ Prefetch │ Ack Mode │ State  │ Group                │ Consumed │ Acknowledged │ Rejected │ Last Activity                                                              │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for cons in consumers:
        tag = cons.consumer_tag[:24].ljust(24)
        queue = cons.queue_name[:23].ljust(23)
        prefetch = str(cons.prefetch_count).ljust(8)
        ack = cons.acknowledge_mode.value[:8].ljust(8)
        
        state_icons = {"active": "🟢", "paused": "🟡", "cancelled": "⚫"}
        state_icon = state_icons.get(cons.state.value, "?")
        state = f"{state_icon}"[:6].ljust(6)
        
        group = cons.consumer_group[:20] if cons.consumer_group else "N/A"
        group = group.ljust(20)
        consumed = str(cons.messages_consumed).ljust(8)
        acked = str(cons.messages_acknowledged).ljust(12)
        rejected = str(cons.messages_rejected).ljust(8)
        
        last = cons.last_activity.strftime("%Y-%m-%d %H:%M:%S") if cons.last_activity else "N/A"
        last = last[:76].ljust(76)
        
        print(f"  │ {tag} │ {queue} │ {prefetch} │ {ack} │ {state} │ {group} │ {consumed} │ {acked} │ {rejected} │ {last} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Queue Metrics
    print("\n📊 Queue Metrics:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Queue                   │ Messages │ Ready │ Unacked │ Pub Rate │ Deliver Rate │ Ack Rate │ Memory     │ Consumers                                                       │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for met in queue_metrics:
        queue = met.queue_name[:23].ljust(23)
        msgs = str(met.message_count).ljust(8)
        ready = str(met.ready_count).ljust(5)
        unacked = str(met.unacked_count).ljust(7)
        pub_rate = f"{met.publish_rate:.0f}/s".ljust(8)
        del_rate = f"{met.deliver_rate:.0f}/s".ljust(12)
        ack_rate = f"{met.ack_rate:.0f}/s".ljust(8)
        memory = f"{met.memory_bytes // 1024 // 1024} MB".ljust(10)
        cons = str(met.consumer_count).ljust(65)
        
        print(f"  │ {queue} │ {msgs} │ {ready} │ {unacked} │ {pub_rate} │ {del_rate} │ {ack_rate} │ {memory} │ {cons} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Dead Letter Queue
    print("\n💀 Dead Letter Queue:")
    
    dlq_entries = list(broker.dead_letters.values())[:5]
    if dlq_entries:
        print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
        print("  │ Message ID                │ Original Queue          │ Reason      │ Dead Lettered                                              │")
        print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
        
        for entry in dlq_entries:
            msg_id = entry.message_id[:25].ljust(25)
            orig_q = entry.original_queue[:23].ljust(23)
            reason = entry.reason[:11].ljust(11)
            dl_at = entry.dead_lettered_at.strftime("%Y-%m-%d %H:%M:%S")[:58].ljust(58)
            
            print(f"  │ {msg_id} │ {orig_q} │ {reason} │ {dl_at} │")
            
        print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    else:
        print("  No entries in Dead Letter Queue")
        
    # Statistics
    stats = broker.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Exchanges: {stats['total_exchanges']}")
    print(f"  Queues: {stats['total_queues']}")
    print(f"  Bindings: {stats['total_bindings']}")
    print(f"  Consumers: {stats['active_consumers']}/{stats['total_consumers']} active")
    print(f"  Connections: {stats['connected']}/{stats['total_connections']} connected")
    print(f"  Channels: {stats['total_channels']}")
    print(f"  Messages: {stats['total_messages']} (pending: {stats['pending_messages']})")
    print(f"  Dead Letters: {stats['dead_letters']}")
    print(f"  Published: {stats['total_published']}, Delivered: {stats['total_delivered']}, Acknowledged: {stats['total_acknowledged']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                     Message Broker Platform                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Exchanges:                    {stats['total_exchanges']:>12}                      │")
    print(f"│ Queues:                       {stats['total_queues']:>12}                      │")
    print(f"│ Bindings:                     {stats['total_bindings']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Published:                    {stats['total_published']:>12}                      │")
    print(f"│ Delivered:                    {stats['total_delivered']:>12}                      │")
    print(f"│ Acknowledged:                 {stats['total_acknowledged']:>12}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Message Broker Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
