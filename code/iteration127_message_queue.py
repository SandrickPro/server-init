#!/usr/bin/env python3
"""
Server Init - Iteration 127: Message Queue Platform
Платформа управления очередями сообщений

Функционал:
- Queue Management - управление очередями
- Topic/Exchange Management - управление топиками/обменниками
- Message Routing - маршрутизация сообщений
- Dead Letter Queue - очереди недоставленных сообщений
- Consumer Groups - группы потребителей
- Message Retention - хранение сообщений
- Rate Limiting - ограничение скорости
- Monitoring & Metrics - мониторинг и метрики
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from collections import defaultdict
import uuid
import random


class QueueType(Enum):
    """Тип очереди"""
    STANDARD = "standard"
    FIFO = "fifo"
    PRIORITY = "priority"
    DELAY = "delay"


class ExchangeType(Enum):
    """Тип обменника"""
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
    DEAD_LETTER = "dead_letter"


class ConsumerStatus(Enum):
    """Статус потребителя"""
    ACTIVE = "active"
    IDLE = "idle"
    BLOCKED = "blocked"
    DISCONNECTED = "disconnected"


@dataclass
class Message:
    """Сообщение"""
    message_id: str
    queue_id: str = ""
    
    # Content
    payload: Dict = field(default_factory=dict)
    headers: Dict = field(default_factory=dict)
    
    # Routing
    routing_key: str = ""
    
    # Status
    status: MessageStatus = MessageStatus.PENDING
    
    # Priority
    priority: int = 0
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    delivered_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    
    # Retry
    delivery_attempts: int = 0
    max_delivery_attempts: int = 3
    
    # Delay
    delay_until: Optional[datetime] = None


@dataclass
class Queue:
    """Очередь"""
    queue_id: str
    name: str = ""
    
    # Type
    queue_type: QueueType = QueueType.STANDARD
    
    # Configuration
    max_size: int = 100000
    max_message_size: int = 256 * 1024  # 256KB
    
    # Retention
    retention_period: timedelta = field(default_factory=lambda: timedelta(days=7))
    
    # Dead letter
    dead_letter_queue_id: Optional[str] = None
    
    # Rate limiting
    rate_limit_per_second: int = 1000
    
    # Metrics
    message_count: int = 0
    unacked_count: int = 0
    consumer_count: int = 0
    
    # Status
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Exchange:
    """Обменник"""
    exchange_id: str
    name: str = ""
    
    # Type
    exchange_type: ExchangeType = ExchangeType.DIRECT
    
    # Durability
    durable: bool = True
    auto_delete: bool = False
    
    # Bindings
    bindings: List[Dict] = field(default_factory=list)
    
    # Metrics
    message_count: int = 0


@dataclass
class Consumer:
    """Потребитель"""
    consumer_id: str
    queue_id: str = ""
    
    # Group
    consumer_group: str = ""
    
    # Status
    status: ConsumerStatus = ConsumerStatus.IDLE
    
    # Metrics
    messages_consumed: int = 0
    messages_acknowledged: int = 0
    messages_rejected: int = 0
    
    # Prefetch
    prefetch_count: int = 10
    
    # Connection
    connected_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)


@dataclass
class ConsumerGroup:
    """Группа потребителей"""
    group_id: str
    name: str = ""
    queue_id: str = ""
    
    # Members
    consumer_ids: List[str] = field(default_factory=list)
    
    # Offset
    committed_offset: int = 0
    
    # Rebalancing
    rebalancing: bool = False
    
    # Metrics
    lag: int = 0


class QueueManager:
    """Менеджер очередей"""
    
    def __init__(self):
        self.queues: Dict[str, Queue] = {}
        self.messages: Dict[str, List[Message]] = defaultdict(list)
        
    def create(self, name: str, queue_type: QueueType = QueueType.STANDARD,
                **kwargs) -> Queue:
        """Создание очереди"""
        queue = Queue(
            queue_id=f"queue_{uuid.uuid4().hex[:8]}",
            name=name,
            queue_type=queue_type,
            **kwargs
        )
        self.queues[queue.queue_id] = queue
        return queue
        
    def publish(self, queue_id: str, payload: Dict,
                 routing_key: str = "", priority: int = 0,
                 delay_seconds: int = 0) -> Message:
        """Публикация сообщения"""
        queue = self.queues.get(queue_id)
        if not queue:
            return None
            
        message = Message(
            message_id=f"msg_{uuid.uuid4().hex[:12]}",
            queue_id=queue_id,
            payload=payload,
            routing_key=routing_key,
            priority=priority
        )
        
        if delay_seconds > 0:
            message.delay_until = datetime.now() + timedelta(seconds=delay_seconds)
            
        # Sort by priority if priority queue
        if queue.queue_type == QueueType.PRIORITY:
            self.messages[queue_id].append(message)
            self.messages[queue_id].sort(key=lambda m: -m.priority)
        else:
            self.messages[queue_id].append(message)
            
        queue.message_count += 1
        
        return message
        
    def consume(self, queue_id: str, consumer_id: str) -> Optional[Message]:
        """Получение сообщения"""
        queue = self.queues.get(queue_id)
        if not queue:
            return None
            
        messages = self.messages.get(queue_id, [])
        
        for msg in messages:
            # Skip delayed messages
            if msg.delay_until and msg.delay_until > datetime.now():
                continue
                
            if msg.status == MessageStatus.PENDING:
                msg.status = MessageStatus.DELIVERED
                msg.delivered_at = datetime.now()
                msg.delivery_attempts += 1
                queue.unacked_count += 1
                return msg
                
        return None
        
    def acknowledge(self, message_id: str) -> bool:
        """Подтверждение сообщения"""
        for queue_id, messages in self.messages.items():
            for msg in messages:
                if msg.message_id == message_id:
                    msg.status = MessageStatus.ACKNOWLEDGED
                    msg.acknowledged_at = datetime.now()
                    
                    queue = self.queues.get(queue_id)
                    if queue:
                        queue.unacked_count -= 1
                        queue.message_count -= 1
                        
                    # Remove message
                    self.messages[queue_id].remove(msg)
                    return True
                    
        return False
        
    def reject(self, message_id: str, requeue: bool = True) -> bool:
        """Отклонение сообщения"""
        for queue_id, messages in self.messages.items():
            for msg in messages:
                if msg.message_id == message_id:
                    queue = self.queues.get(queue_id)
                    
                    if msg.delivery_attempts >= msg.max_delivery_attempts:
                        # Move to dead letter queue
                        msg.status = MessageStatus.DEAD_LETTER
                        if queue and queue.dead_letter_queue_id:
                            self.messages[queue.dead_letter_queue_id].append(msg)
                        self.messages[queue_id].remove(msg)
                    elif requeue:
                        msg.status = MessageStatus.PENDING
                    else:
                        msg.status = MessageStatus.REJECTED
                        self.messages[queue_id].remove(msg)
                        
                    if queue:
                        queue.unacked_count -= 1
                        
                    return True
                    
        return False


class ExchangeManager:
    """Менеджер обменников"""
    
    def __init__(self, queue_manager: QueueManager):
        self.queue_manager = queue_manager
        self.exchanges: Dict[str, Exchange] = {}
        
    def create(self, name: str, exchange_type: ExchangeType = ExchangeType.DIRECT,
                **kwargs) -> Exchange:
        """Создание обменника"""
        exchange = Exchange(
            exchange_id=f"exchange_{uuid.uuid4().hex[:8]}",
            name=name,
            exchange_type=exchange_type,
            **kwargs
        )
        self.exchanges[exchange.exchange_id] = exchange
        return exchange
        
    def bind(self, exchange_id: str, queue_id: str, routing_key: str = "") -> Dict:
        """Привязка очереди"""
        exchange = self.exchanges.get(exchange_id)
        if not exchange:
            return {"error": "Exchange not found"}
            
        binding = {
            "queue_id": queue_id,
            "routing_key": routing_key,
            "created_at": datetime.now().isoformat()
        }
        exchange.bindings.append(binding)
        
        return {"exchange_id": exchange_id, "binding": binding}
        
    def publish(self, exchange_id: str, payload: Dict,
                 routing_key: str = "", **kwargs) -> List[Message]:
        """Публикация через обменник"""
        exchange = self.exchanges.get(exchange_id)
        if not exchange:
            return []
            
        messages = []
        
        if exchange.exchange_type == ExchangeType.FANOUT:
            # Broadcast to all bound queues
            for binding in exchange.bindings:
                msg = self.queue_manager.publish(
                    binding["queue_id"], payload,
                    routing_key=routing_key, **kwargs
                )
                if msg:
                    messages.append(msg)
                    
        elif exchange.exchange_type == ExchangeType.DIRECT:
            # Route to queues with matching routing key
            for binding in exchange.bindings:
                if binding["routing_key"] == routing_key:
                    msg = self.queue_manager.publish(
                        binding["queue_id"], payload,
                        routing_key=routing_key, **kwargs
                    )
                    if msg:
                        messages.append(msg)
                        
        elif exchange.exchange_type == ExchangeType.TOPIC:
            # Route with pattern matching
            for binding in exchange.bindings:
                if self._match_topic(binding["routing_key"], routing_key):
                    msg = self.queue_manager.publish(
                        binding["queue_id"], payload,
                        routing_key=routing_key, **kwargs
                    )
                    if msg:
                        messages.append(msg)
                        
        exchange.message_count += len(messages)
        return messages
        
    def _match_topic(self, pattern: str, routing_key: str) -> bool:
        """Сопоставление топика"""
        pattern_parts = pattern.split('.')
        key_parts = routing_key.split('.')
        
        p_idx = k_idx = 0
        
        while p_idx < len(pattern_parts) and k_idx < len(key_parts):
            if pattern_parts[p_idx] == '#':
                return True
            elif pattern_parts[p_idx] == '*' or pattern_parts[p_idx] == key_parts[k_idx]:
                p_idx += 1
                k_idx += 1
            else:
                return False
                
        return p_idx == len(pattern_parts) and k_idx == len(key_parts)


class ConsumerManager:
    """Менеджер потребителей"""
    
    def __init__(self, queue_manager: QueueManager):
        self.queue_manager = queue_manager
        self.consumers: Dict[str, Consumer] = {}
        self.groups: Dict[str, ConsumerGroup] = {}
        
    def register(self, queue_id: str, consumer_group: str = "",
                  prefetch_count: int = 10) -> Consumer:
        """Регистрация потребителя"""
        consumer = Consumer(
            consumer_id=f"consumer_{uuid.uuid4().hex[:8]}",
            queue_id=queue_id,
            consumer_group=consumer_group,
            prefetch_count=prefetch_count,
            status=ConsumerStatus.ACTIVE
        )
        
        self.consumers[consumer.consumer_id] = consumer
        
        # Update queue
        queue = self.queue_manager.queues.get(queue_id)
        if queue:
            queue.consumer_count += 1
            
        # Add to group
        if consumer_group:
            self._add_to_group(consumer_group, queue_id, consumer.consumer_id)
            
        return consumer
        
    def _add_to_group(self, group_name: str, queue_id: str, consumer_id: str):
        """Добавление в группу"""
        group_key = f"{group_name}_{queue_id}"
        
        if group_key not in self.groups:
            self.groups[group_key] = ConsumerGroup(
                group_id=f"group_{uuid.uuid4().hex[:8]}",
                name=group_name,
                queue_id=queue_id
            )
            
        self.groups[group_key].consumer_ids.append(consumer_id)
        
    def unregister(self, consumer_id: str) -> bool:
        """Отмена регистрации"""
        consumer = self.consumers.get(consumer_id)
        if not consumer:
            return False
            
        # Update queue
        queue = self.queue_manager.queues.get(consumer.queue_id)
        if queue:
            queue.consumer_count -= 1
            
        # Remove from group
        if consumer.consumer_group:
            group_key = f"{consumer.consumer_group}_{consumer.queue_id}"
            group = self.groups.get(group_key)
            if group and consumer_id in group.consumer_ids:
                group.consumer_ids.remove(consumer_id)
                
        consumer.status = ConsumerStatus.DISCONNECTED
        del self.consumers[consumer_id]
        return True
        
    def update_metrics(self, consumer_id: str, consumed: int = 0,
                        acked: int = 0, rejected: int = 0):
        """Обновление метрик"""
        consumer = self.consumers.get(consumer_id)
        if not consumer:
            return
            
        consumer.messages_consumed += consumed
        consumer.messages_acknowledged += acked
        consumer.messages_rejected += rejected
        consumer.last_activity = datetime.now()


class RateLimiter:
    """Ограничитель скорости"""
    
    def __init__(self):
        self.windows: Dict[str, List[datetime]] = defaultdict(list)
        
    def check(self, key: str, limit: int, window_seconds: int = 1) -> bool:
        """Проверка лимита"""
        now = datetime.now()
        window_start = now - timedelta(seconds=window_seconds)
        
        # Clean old entries
        self.windows[key] = [t for t in self.windows[key] if t > window_start]
        
        if len(self.windows[key]) >= limit:
            return False
            
        self.windows[key].append(now)
        return True


class MessageQueuePlatform:
    """Платформа очередей сообщений"""
    
    def __init__(self):
        self.queue_manager = QueueManager()
        self.exchange_manager = ExchangeManager(self.queue_manager)
        self.consumer_manager = ConsumerManager(self.queue_manager)
        self.rate_limiter = RateLimiter()
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        queues = list(self.queue_manager.queues.values())
        exchanges = list(self.exchange_manager.exchanges.values())
        consumers = list(self.consumer_manager.consumers.values())
        
        total_messages = sum(q.message_count for q in queues)
        unacked = sum(q.unacked_count for q in queues)
        active_consumers = len([c for c in consumers if c.status == ConsumerStatus.ACTIVE])
        
        return {
            "total_queues": len(queues),
            "total_exchanges": len(exchanges),
            "total_consumers": len(consumers),
            "active_consumers": active_consumers,
            "total_messages": total_messages,
            "unacked_messages": unacked,
            "consumer_groups": len(self.consumer_manager.groups)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 127: Message Queue Platform")
    print("=" * 60)
    
    async def demo():
        platform = MessageQueuePlatform()
        print("✓ Message Queue Platform created")
        
        # Create queues
        print("\n📬 Creating Queues...")
        
        queues_data = [
            ("orders", QueueType.FIFO),
            ("notifications", QueueType.STANDARD),
            ("analytics", QueueType.STANDARD),
            ("priority-tasks", QueueType.PRIORITY),
            ("scheduled-jobs", QueueType.DELAY)
        ]
        
        created_queues = []
        for name, q_type in queues_data:
            queue = platform.queue_manager.create(name, q_type)
            created_queues.append(queue)
            print(f"  ✓ {name} ({q_type.value})")
            
        # Create DLQ
        dlq = platform.queue_manager.create("dead-letter-queue", QueueType.STANDARD)
        print(f"  ✓ dead-letter-queue (dead letter)")
        
        # Link DLQ
        for queue in created_queues:
            queue.dead_letter_queue_id = dlq.queue_id
            
        # Create exchanges
        print("\n🔄 Creating Exchanges...")
        
        exchanges_data = [
            ("events", ExchangeType.FANOUT),
            ("orders-direct", ExchangeType.DIRECT),
            ("logs-topic", ExchangeType.TOPIC)
        ]
        
        created_exchanges = []
        for name, ex_type in exchanges_data:
            exchange = platform.exchange_manager.create(name, ex_type)
            created_exchanges.append(exchange)
            print(f"  ✓ {name} ({ex_type.value})")
            
        # Create bindings
        print("\n🔗 Creating Bindings...")
        
        # Fanout - bind all queues
        for queue in created_queues[:3]:
            platform.exchange_manager.bind(created_exchanges[0].exchange_id, queue.queue_id)
            print(f"  ✓ {created_exchanges[0].name} -> {queue.name}")
            
        # Direct - bind with routing keys
        platform.exchange_manager.bind(
            created_exchanges[1].exchange_id,
            created_queues[0].queue_id,
            "order.created"
        )
        platform.exchange_manager.bind(
            created_exchanges[1].exchange_id,
            created_queues[1].queue_id,
            "order.shipped"
        )
        print(f"  ✓ {created_exchanges[1].name} -> orders (order.created)")
        print(f"  ✓ {created_exchanges[1].name} -> notifications (order.shipped)")
        
        # Topic - bind with patterns
        platform.exchange_manager.bind(
            created_exchanges[2].exchange_id,
            created_queues[2].queue_id,
            "logs.*.error"
        )
        platform.exchange_manager.bind(
            created_exchanges[2].exchange_id,
            created_queues[2].queue_id,
            "logs.#"
        )
        print(f"  ✓ {created_exchanges[2].name} -> analytics (logs.*.error)")
        print(f"  ✓ {created_exchanges[2].name} -> analytics (logs.#)")
        
        # Register consumers
        print("\n👥 Registering Consumers...")
        
        consumers = []
        for queue in created_queues[:3]:
            for i in range(3):
                consumer = platform.consumer_manager.register(
                    queue.queue_id,
                    consumer_group=f"{queue.name}-consumers",
                    prefetch_count=10
                )
                consumers.append(consumer)
                
            print(f"  ✓ {queue.name}: 3 consumers")
            
        # Publish messages
        print("\n📤 Publishing Messages...")
        
        # Direct to queue
        for i in range(10):
            platform.queue_manager.publish(
                created_queues[0].queue_id,
                {"order_id": f"ORD-{1000 + i}", "amount": random.randint(10, 500)},
                routing_key="order"
            )
        print(f"  ✓ Published 10 orders to {created_queues[0].name}")
        
        # Through fanout exchange
        for i in range(5):
            platform.exchange_manager.publish(
                created_exchanges[0].exchange_id,
                {"event": "user_signup", "user_id": f"USR-{i}"}
            )
        print(f"  ✓ Published 5 events through fanout (15 total routed)")
        
        # Through direct exchange
        platform.exchange_manager.publish(
            created_exchanges[1].exchange_id,
            {"order_id": "ORD-9999", "status": "shipped"},
            routing_key="order.shipped"
        )
        print(f"  ✓ Published 1 order.shipped through direct")
        
        # Through topic exchange
        platform.exchange_manager.publish(
            created_exchanges[2].exchange_id,
            {"level": "error", "message": "Database connection failed"},
            routing_key="logs.db.error"
        )
        print(f"  ✓ Published 1 log through topic")
        
        # Priority messages
        for priority in [1, 5, 10, 3, 8]:
            platform.queue_manager.publish(
                created_queues[3].queue_id,
                {"task": f"Task with priority {priority}"},
                priority=priority
            )
        print(f"  ✓ Published 5 priority tasks")
        
        # Delayed messages
        for delay in [5, 10, 30, 60]:
            platform.queue_manager.publish(
                created_queues[4].queue_id,
                {"job": f"Job delayed by {delay}s"},
                delay_seconds=delay
            )
        print(f"  ✓ Published 4 delayed jobs")
        
        # Consume messages
        print("\n📥 Consuming Messages...")
        
        for queue in created_queues[:3]:
            consumed = 0
            while True:
                msg = platform.queue_manager.consume(queue.queue_id, "consumer-1")
                if not msg:
                    break
                    
                # Acknowledge
                platform.queue_manager.acknowledge(msg.message_id)
                consumed += 1
                
            print(f"  ✓ {queue.name}: consumed {consumed} messages")
            
        # Queue status
        print("\n📊 Queue Status:")
        
        for queue in platform.queue_manager.queues.values():
            status_icon = "🟢" if queue.message_count == 0 else "🟡" if queue.message_count < 100 else "🔴"
            print(f"  {status_icon} {queue.name}")
            print(f"     Type: {queue.queue_type.value}")
            print(f"     Messages: {queue.message_count}")
            print(f"     Unacked: {queue.unacked_count}")
            print(f"     Consumers: {queue.consumer_count}")
            
        # Consumer groups
        print("\n👥 Consumer Groups:")
        
        for group in platform.consumer_manager.groups.values():
            print(f"  📋 {group.name}")
            print(f"     Queue: {platform.queue_manager.queues.get(group.queue_id, Queue('')).name}")
            print(f"     Members: {len(group.consumer_ids)}")
            print(f"     Lag: {group.lag}")
            
        # Rate limiting demo
        print("\n⏱️ Rate Limiting Demo:")
        
        allowed = 0
        blocked = 0
        
        for i in range(20):
            if platform.rate_limiter.check("test-producer", limit=10, window_seconds=1):
                allowed += 1
            else:
                blocked += 1
                
        print(f"  Limit: 10/second")
        print(f"  Attempts: 20")
        print(f"  Allowed: {allowed}")
        print(f"  Blocked: {blocked}")
        
        # Exchange statistics
        print("\n🔄 Exchange Statistics:")
        
        for exchange in platform.exchange_manager.exchanges.values():
            print(f"  📌 {exchange.name}")
            print(f"     Type: {exchange.exchange_type.value}")
            print(f"     Bindings: {len(exchange.bindings)}")
            print(f"     Messages routed: {exchange.message_count}")
            
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Queues: {stats['total_queues']}")
        print(f"  Exchanges: {stats['total_exchanges']}")
        print(f"  Consumers: {stats['total_consumers']} ({stats['active_consumers']} active)")
        print(f"  Consumer Groups: {stats['consumer_groups']}")
        print(f"  Total Messages: {stats['total_messages']}")
        print(f"  Unacked Messages: {stats['unacked_messages']}")
        
        # Dashboard
        print("\n📋 Message Queue Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │               Message Queue Overview                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Queues:       {stats['total_queues']:>10}                        │")
        print(f"  │ Total Exchanges:    {stats['total_exchanges']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Consumers:    {stats['total_consumers']:>10}                        │")
        print(f"  │ Active Consumers:   {stats['active_consumers']:>10}                        │")
        print(f"  │ Consumer Groups:    {stats['consumer_groups']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Messages:     {stats['total_messages']:>10}                        │")
        print(f"  │ Unacked Messages:   {stats['unacked_messages']:>10}                        │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Message Queue Platform initialized!")
    print("=" * 60)
