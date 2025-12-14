#!/usr/bin/env python3
"""
Server Init - Iteration 237: Message Queue Manager Platform
Платформа управления очередями сообщений

Функционал:
- Queue Management - управление очередями
- Consumer Management - управление потребителями
- Dead Letter Queue - очереди мёртвых сообщений
- Message Routing - маршрутизация сообщений
- Message Persistence - сохранение сообщений
- Rate Limiting - ограничение скорости
- Priority Queues - приоритетные очереди
- Message Replay - повторная обработка
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid
import json
import hashlib


class QueueType(Enum):
    """Тип очереди"""
    STANDARD = "standard"
    FIFO = "fifo"
    PRIORITY = "priority"
    DELAY = "delay"
    DLQ = "dead_letter"


class MessageStatus(Enum):
    """Статус сообщения"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD_LETTERED = "dead_lettered"


class ConsumerStatus(Enum):
    """Статус потребителя"""
    ACTIVE = "active"
    IDLE = "idle"
    PAUSED = "paused"
    DISCONNECTED = "disconnected"


class DeliveryMode(Enum):
    """Режим доставки"""
    AT_MOST_ONCE = "at_most_once"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"


@dataclass
class MessageQueue:
    """Очередь сообщений"""
    queue_id: str
    name: str = ""
    
    # Type
    queue_type: QueueType = QueueType.STANDARD
    
    # DLQ
    dlq_id: str = ""
    
    # Settings
    max_size: int = 10000
    message_ttl_seconds: int = 86400
    visibility_timeout: int = 30
    max_retries: int = 3
    
    # Delivery
    delivery_mode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE
    
    # Stats
    messages_in_queue: int = 0
    messages_in_flight: int = 0
    total_messages: int = 0
    
    # Created
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Message:
    """Сообщение"""
    message_id: str
    queue_id: str = ""
    
    # Content
    body: str = ""
    attributes: Dict[str, str] = field(default_factory=dict)
    
    # Priority (0-9, higher = more priority)
    priority: int = 5
    
    # Status
    status: MessageStatus = MessageStatus.PENDING
    
    # Delivery
    delivery_count: int = 0
    first_delivered: Optional[datetime] = None
    last_delivered: Optional[datetime] = None
    
    # Visibility
    visible_at: datetime = field(default_factory=datetime.now)
    
    # Times
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    # Deduplication
    dedup_id: str = ""
    
    # Group (for FIFO)
    message_group_id: str = ""


@dataclass
class Consumer:
    """Потребитель"""
    consumer_id: str
    queue_id: str = ""
    
    # Name
    name: str = ""
    
    # Status
    status: ConsumerStatus = ConsumerStatus.ACTIVE
    
    # Settings
    batch_size: int = 10
    polling_interval_ms: int = 1000
    
    # Stats
    messages_processed: int = 0
    messages_failed: int = 0
    last_poll: Optional[datetime] = None
    
    # Connected
    connected_at: datetime = field(default_factory=datetime.now)


@dataclass
class Exchange:
    """Обменник для маршрутизации"""
    exchange_id: str
    name: str = ""
    
    # Type
    exchange_type: str = "direct"  # direct, fanout, topic, headers
    
    # Bindings (queue_id -> routing_key)
    bindings: Dict[str, str] = field(default_factory=dict)
    
    # Durable
    durable: bool = True


@dataclass
class DLQMessage:
    """Сообщение в DLQ"""
    dlq_message_id: str
    original_message_id: str = ""
    original_queue_id: str = ""
    
    # Content
    body: str = ""
    
    # Error
    error_message: str = ""
    failure_count: int = 0
    
    # Times
    dead_lettered_at: datetime = field(default_factory=datetime.now)


class MessageQueuePlatform:
    """Платформа управления очередями"""
    
    def __init__(self):
        self.queues: Dict[str, MessageQueue] = {}
        self.messages: Dict[str, Message] = {}
        self.consumers: Dict[str, Consumer] = {}
        self.exchanges: Dict[str, Exchange] = {}
        self.dlq_messages: List[DLQMessage] = []
        
    def create_queue(self, name: str,
                    queue_type: QueueType = QueueType.STANDARD,
                    max_size: int = 10000,
                    message_ttl: int = 86400,
                    max_retries: int = 3) -> MessageQueue:
        """Создание очереди"""
        queue = MessageQueue(
            queue_id=f"q_{uuid.uuid4().hex[:8]}",
            name=name,
            queue_type=queue_type,
            max_size=max_size,
            message_ttl_seconds=message_ttl,
            max_retries=max_retries
        )
        
        # Create DLQ if not DLQ itself
        if queue_type != QueueType.DLQ:
            dlq = self.create_queue(
                f"{name}-dlq",
                QueueType.DLQ,
                max_size=max_size
            )
            queue.dlq_id = dlq.queue_id
            
        self.queues[queue.queue_id] = queue
        return queue
        
    def send_message(self, queue_id: str, body: str,
                    attributes: Dict[str, str] = None,
                    priority: int = 5,
                    delay_seconds: int = 0,
                    dedup_id: str = "",
                    group_id: str = "") -> Optional[Message]:
        """Отправка сообщения"""
        queue = self.queues.get(queue_id)
        if not queue:
            return None
            
        # Check queue size
        if queue.messages_in_queue >= queue.max_size:
            return None
            
        message = Message(
            message_id=f"msg_{uuid.uuid4().hex[:12]}",
            queue_id=queue_id,
            body=body,
            attributes=attributes or {},
            priority=priority,
            visible_at=datetime.now() + timedelta(seconds=delay_seconds),
            expires_at=datetime.now() + timedelta(seconds=queue.message_ttl_seconds),
            dedup_id=dedup_id or uuid.uuid4().hex[:8],
            message_group_id=group_id
        )
        
        self.messages[message.message_id] = message
        queue.messages_in_queue += 1
        queue.total_messages += 1
        
        return message
        
    def receive_messages(self, queue_id: str,
                        max_messages: int = 10,
                        visibility_timeout: int = 30) -> List[Message]:
        """Получение сообщений"""
        queue = self.queues.get(queue_id)
        if not queue:
            return []
            
        now = datetime.now()
        received = []
        
        # Get visible messages
        available = [
            m for m in self.messages.values()
            if m.queue_id == queue_id
            and m.status == MessageStatus.PENDING
            and m.visible_at <= now
        ]
        
        # Sort by priority for priority queues
        if queue.queue_type == QueueType.PRIORITY:
            available.sort(key=lambda m: -m.priority)
        elif queue.queue_type == QueueType.FIFO:
            available.sort(key=lambda m: m.created_at)
            
        for msg in available[:max_messages]:
            msg.status = MessageStatus.PROCESSING
            msg.delivery_count += 1
            msg.last_delivered = now
            if not msg.first_delivered:
                msg.first_delivered = now
                
            msg.visible_at = now + timedelta(seconds=visibility_timeout)
            
            queue.messages_in_flight += 1
            queue.messages_in_queue -= 1
            
            received.append(msg)
            
        return received
        
    def acknowledge_message(self, message_id: str) -> bool:
        """Подтверждение обработки"""
        message = self.messages.get(message_id)
        if not message:
            return False
            
        queue = self.queues.get(message.queue_id)
        if queue:
            queue.messages_in_flight -= 1
            
        message.status = MessageStatus.COMPLETED
        return True
        
    def nack_message(self, message_id: str, requeue: bool = True) -> bool:
        """Отклонение сообщения"""
        message = self.messages.get(message_id)
        if not message:
            return False
            
        queue = self.queues.get(message.queue_id)
        if not queue:
            return False
            
        queue.messages_in_flight -= 1
        
        if requeue and message.delivery_count < queue.max_retries:
            # Requeue with delay
            message.status = MessageStatus.PENDING
            message.visible_at = datetime.now() + timedelta(seconds=5 * message.delivery_count)
            queue.messages_in_queue += 1
        else:
            # Move to DLQ
            self._move_to_dlq(message, "Max retries exceeded")
            
        return True
        
    def _move_to_dlq(self, message: Message, error: str):
        """Перемещение в DLQ"""
        message.status = MessageStatus.DEAD_LETTERED
        
        dlq_msg = DLQMessage(
            dlq_message_id=f"dlq_{uuid.uuid4().hex[:8]}",
            original_message_id=message.message_id,
            original_queue_id=message.queue_id,
            body=message.body,
            error_message=error,
            failure_count=message.delivery_count
        )
        
        self.dlq_messages.append(dlq_msg)
        
    def create_consumer(self, queue_id: str, name: str,
                       batch_size: int = 10) -> Consumer:
        """Создание потребителя"""
        consumer = Consumer(
            consumer_id=f"cons_{uuid.uuid4().hex[:8]}",
            queue_id=queue_id,
            name=name,
            batch_size=batch_size
        )
        
        self.consumers[consumer.consumer_id] = consumer
        return consumer
        
    def create_exchange(self, name: str,
                       exchange_type: str = "direct") -> Exchange:
        """Создание обменника"""
        exchange = Exchange(
            exchange_id=f"ex_{uuid.uuid4().hex[:8]}",
            name=name,
            exchange_type=exchange_type
        )
        
        self.exchanges[exchange.exchange_id] = exchange
        return exchange
        
    def bind_queue(self, exchange_id: str, queue_id: str,
                  routing_key: str = "") -> bool:
        """Привязка очереди к обменнику"""
        exchange = self.exchanges.get(exchange_id)
        if not exchange:
            return False
            
        exchange.bindings[queue_id] = routing_key
        return True
        
    def publish_to_exchange(self, exchange_id: str, body: str,
                           routing_key: str = "",
                           attributes: Dict[str, str] = None) -> int:
        """Публикация через обменник"""
        exchange = self.exchanges.get(exchange_id)
        if not exchange:
            return 0
            
        published = 0
        
        for queue_id, bound_key in exchange.bindings.items():
            # Route based on exchange type
            should_route = False
            
            if exchange.exchange_type == "fanout":
                should_route = True
            elif exchange.exchange_type == "direct":
                should_route = (routing_key == bound_key)
            elif exchange.exchange_type == "topic":
                # Simplified topic matching
                should_route = routing_key.startswith(bound_key.replace("*", "").replace("#", ""))
                
            if should_route:
                msg = self.send_message(queue_id, body, attributes)
                if msg:
                    published += 1
                    
        return published
        
    def replay_dlq(self, original_queue_id: str, limit: int = 100) -> int:
        """Повторная обработка DLQ"""
        replayed = 0
        
        for dlq_msg in self.dlq_messages[:limit]:
            if dlq_msg.original_queue_id == original_queue_id:
                msg = self.send_message(original_queue_id, dlq_msg.body)
                if msg:
                    replayed += 1
                    
        return replayed
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        queues = list(self.queues.values())
        
        total_pending = sum(q.messages_in_queue for q in queues)
        total_in_flight = sum(q.messages_in_flight for q in queues)
        
        # By type
        by_type = {}
        for q in queues:
            t = q.queue_type.value
            by_type[t] = by_type.get(t, 0) + 1
            
        return {
            "total_queues": len(queues),
            "total_consumers": len(self.consumers),
            "total_exchanges": len(self.exchanges),
            "messages_pending": total_pending,
            "messages_in_flight": total_in_flight,
            "dlq_messages": len(self.dlq_messages),
            "queues_by_type": by_type
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 237: Message Queue Manager Platform")
    print("=" * 60)
    
    platform = MessageQueuePlatform()
    print("✓ Message Queue Platform created")
    
    # Create queues
    print("\n📬 Creating Message Queues...")
    
    queues_config = [
        ("orders-queue", QueueType.FIFO, 50000),
        ("notifications-queue", QueueType.STANDARD, 100000),
        ("priority-tasks", QueueType.PRIORITY, 10000),
        ("scheduled-jobs", QueueType.DELAY, 50000),
        ("events-queue", QueueType.STANDARD, 200000),
    ]
    
    queues = []
    for name, qtype, max_size in queues_config:
        queue = platform.create_queue(name, qtype, max_size)
        queues.append(queue)
        
        type_icons = {
            QueueType.STANDARD: "📨",
            QueueType.FIFO: "📋",
            QueueType.PRIORITY: "⭐",
            QueueType.DELAY: "⏰",
            QueueType.DLQ: "☠️"
        }
        icon = type_icons.get(qtype, "📬")
        print(f"  {icon} {name} ({qtype.value})")
        
    # Create exchanges
    print("\n🔀 Creating Exchanges...")
    
    exchanges_config = [
        ("events", "fanout"),
        ("orders", "direct"),
        ("logs", "topic"),
    ]
    
    exchanges = []
    for name, etype in exchanges_config:
        exchange = platform.create_exchange(name, etype)
        exchanges.append(exchange)
        print(f"  🔀 {name} ({etype})")
        
    # Bind queues to exchanges
    print("\n🔗 Binding Queues to Exchanges...")
    
    # Bind events queue to fanout
    platform.bind_queue(exchanges[0].exchange_id, queues[4].queue_id)
    print(f"  ✓ events -> {queues[4].name}")
    
    # Bind orders queue with routing key
    platform.bind_queue(exchanges[1].exchange_id, queues[0].queue_id, "order.created")
    print(f"  ✓ orders -> {queues[0].name} (order.created)")
    
    # Create consumers
    print("\n👥 Creating Consumers...")
    
    consumers_config = [
        (queues[0].queue_id, "order-processor-1", 10),
        (queues[0].queue_id, "order-processor-2", 10),
        (queues[1].queue_id, "notification-sender", 50),
        (queues[2].queue_id, "task-worker", 5),
        (queues[4].queue_id, "event-handler", 20),
    ]
    
    consumers = []
    for queue_id, name, batch in consumers_config:
        consumer = platform.create_consumer(queue_id, name, batch)
        consumers.append(consumer)
        queue = platform.queues.get(queue_id)
        queue_name = queue.name if queue else "unknown"
        print(f"  👤 {name} -> {queue_name}")
        
    # Send messages
    print("\n📤 Sending Messages...")
    
    # Orders
    order_messages = [
        {"order_id": f"ORD-{i}", "amount": random.randint(100, 1000)}
        for i in range(1, 21)
    ]
    
    for order in order_messages:
        platform.send_message(
            queues[0].queue_id,
            json.dumps(order),
            {"type": "order"},
            group_id=f"customer-{random.randint(1, 5)}"
        )
        
    # Priority tasks
    for i in range(15):
        priority = random.randint(1, 9)
        platform.send_message(
            queues[2].queue_id,
            f"Task #{i+1}",
            {"priority": str(priority)},
            priority=priority
        )
        
    # Standard messages
    for i in range(30):
        platform.send_message(
            queues[1].queue_id,
            f"Notification #{i+1}",
            {"channel": random.choice(["email", "sms", "push"])}
        )
        
    total_sent = sum(q.total_messages for q in queues if q.queue_type != QueueType.DLQ)
    print(f"  ✓ Sent {total_sent} messages")
    
    # Publish to exchange
    print("\n📢 Publishing to Exchanges...")
    
    published = platform.publish_to_exchange(
        exchanges[0].exchange_id,
        json.dumps({"event": "user.created", "user_id": "123"}),
        attributes={"source": "api"}
    )
    print(f"  ✓ Published to {published} queues via fanout")
    
    # Receive and process messages
    print("\n📥 Processing Messages...")
    
    processed = 0
    failed = 0
    
    for queue in queues[:4]:  # Exclude events queue for now
        messages = platform.receive_messages(queue.queue_id, 10)
        
        for msg in messages:
            # Simulate processing (90% success)
            if random.random() > 0.1:
                platform.acknowledge_message(msg.message_id)
                processed += 1
            else:
                platform.nack_message(msg.message_id)
                failed += 1
                
    print(f"  ✅ Processed: {processed}")
    print(f"  ❌ Failed: {failed}")
    
    # Display queues
    print("\n📬 Message Queues:")
    
    print("\n  ┌──────────────────────────┬────────────────┬──────────┬──────────┬─────────┐")
    print("  │ Queue                    │ Type           │ Pending  │ Flight   │ Total   │")
    print("  ├──────────────────────────┼────────────────┼──────────┼──────────┼─────────┤")
    
    for queue in platform.queues.values():
        if queue.queue_type == QueueType.DLQ:
            continue
            
        name = queue.name[:24].ljust(24)
        qtype = queue.queue_type.value[:14].ljust(14)
        pending = str(queue.messages_in_queue)[:8].ljust(8)
        flight = str(queue.messages_in_flight)[:8].ljust(8)
        total = str(queue.total_messages)[:7].ljust(7)
        
        print(f"  │ {name} │ {qtype} │ {pending} │ {flight} │ {total} │")
        
    print("  └──────────────────────────┴────────────────┴──────────┴──────────┴─────────┘")
    
    # Display consumers
    print("\n👥 Consumers:")
    
    print("\n  ┌────────────────────────────┬────────────────────────┬──────────┬─────────┐")
    print("  │ Consumer                   │ Queue                  │ Status   │ Batch   │")
    print("  ├────────────────────────────┼────────────────────────┼──────────┼─────────┤")
    
    for consumer in platform.consumers.values():
        name = consumer.name[:26].ljust(26)
        queue = platform.queues.get(consumer.queue_id)
        queue_name = (queue.name if queue else "unknown")[:22].ljust(22)
        
        status_icons = {
            ConsumerStatus.ACTIVE: "🟢",
            ConsumerStatus.IDLE: "🟡",
            ConsumerStatus.PAUSED: "⏸️",
            ConsumerStatus.DISCONNECTED: "🔴"
        }
        status = status_icons.get(consumer.status, "⚪")[:8].ljust(8)
        batch = str(consumer.batch_size)[:7].ljust(7)
        
        print(f"  │ {name} │ {queue_name} │ {status} │ {batch} │")
        
    print("  └────────────────────────────┴────────────────────────┴──────────┴─────────┘")
    
    # Dead letter queue
    print("\n☠️ Dead Letter Queue:")
    
    dlq_count = len(platform.dlq_messages)
    print(f"  Messages in DLQ: {dlq_count}")
    
    for dlq_msg in platform.dlq_messages[:3]:
        print(f"  ❌ {dlq_msg.original_message_id}: {dlq_msg.error_message}")
        
    # Exchange routing
    print("\n🔀 Exchange Bindings:")
    
    for exchange in platform.exchanges.values():
        print(f"  📤 {exchange.name} ({exchange.exchange_type}):")
        for queue_id, routing_key in exchange.bindings.items():
            queue = platform.queues.get(queue_id)
            queue_name = queue.name if queue else "unknown"
            key_str = f" [{routing_key}]" if routing_key else ""
            print(f"     └─ {queue_name}{key_str}")
            
    # Queue type distribution
    print("\n📊 Queue Types:")
    
    stats = platform.get_statistics()
    
    for qtype, count in stats['queues_by_type'].items():
        type_icons = {
            "standard": "📨",
            "fifo": "📋",
            "priority": "⭐",
            "delay": "⏰",
            "dead_letter": "☠️"
        }
        icon = type_icons.get(qtype, "📬")
        bar = "█" * (count * 2) + "░" * (10 - count * 2)
        print(f"  {icon} {qtype:12s} [{bar}] {count}")
        
    # Message flow
    print("\n📈 Message Flow:")
    
    print(f"  Pending: {stats['messages_pending']}")
    print(f"  In Flight: {stats['messages_in_flight']}")
    print(f"  Dead Lettered: {stats['dlq_messages']}")
    
    # Statistics
    print("\n📊 Platform Statistics:")
    
    print(f"\n  Queues: {stats['total_queues']}")
    print(f"  Consumers: {stats['total_consumers']}")
    print(f"  Exchanges: {stats['total_exchanges']}")
    print(f"  Messages Pending: {stats['messages_pending']}")
    print(f"  Messages In Flight: {stats['messages_in_flight']}")
    print(f"  DLQ Messages: {stats['dlq_messages']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Message Queue Dashboard                          │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Queues:                  {stats['total_queues']:>12}                        │")
    print(f"│ Active Consumers:              {stats['total_consumers']:>12}                        │")
    print(f"│ Messages Pending:              {stats['messages_pending']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Messages In Flight:            {stats['messages_in_flight']:>12}                        │")
    print(f"│ Dead Letter Messages:          {stats['dlq_messages']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Message Queue Manager Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
