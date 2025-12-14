#!/usr/bin/env python3
"""
Server Init - Iteration 254: Dead Letter Queue Platform
Платформа управления очередями недоставленных сообщений

Функционал:
- DLQ Management - управление DLQ очередями
- Message Capture - захват failed сообщений
- Retry Processing - повторная обработка
- Error Analysis - анализ ошибок
- Message Inspection - инспекция сообщений
- Bulk Operations - массовые операции
- Alerting - алертинг
- Metrics & Reporting - метрики и отчёты
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
import uuid
import json


class DLQState(Enum):
    """Состояние DLQ"""
    ACTIVE = "active"
    PAUSED = "paused"
    DRAINING = "draining"
    DISABLED = "disabled"


class MessageState(Enum):
    """Состояние сообщения в DLQ"""
    PENDING = "pending"
    PROCESSING = "processing"
    REPROCESSED = "reprocessed"
    DISCARDED = "discarded"
    EXPIRED = "expired"


class ErrorCategory(Enum):
    """Категория ошибки"""
    TRANSIENT = "transient"
    PERMANENT = "permanent"
    UNKNOWN = "unknown"
    VALIDATION = "validation"
    TIMEOUT = "timeout"
    CAPACITY = "capacity"


class RetryStrategy(Enum):
    """Стратегия повторов"""
    IMMEDIATE = "immediate"
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    CUSTOM = "custom"


@dataclass
class DeadLetterMessage:
    """Сообщение в DLQ"""
    message_id: str
    
    # Original message
    original_topic: str = ""
    original_partition: int = 0
    original_offset: int = 0
    original_key: str = ""
    payload: Any = None
    headers: Dict[str, str] = field(default_factory=dict)
    
    # State
    state: MessageState = MessageState.PENDING
    
    # Error info
    error_message: str = ""
    error_code: str = ""
    error_category: ErrorCategory = ErrorCategory.UNKNOWN
    stack_trace: str = ""
    
    # Processing
    source_service: str = ""
    consumer_group: str = ""
    
    # Retry
    retry_count: int = 0
    max_retries: int = 3
    last_retry_at: Optional[datetime] = None
    next_retry_at: Optional[datetime] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Time
    failed_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None


@dataclass
class DeadLetterQueue:
    """Dead Letter Queue"""
    queue_id: str
    name: str
    
    # Source
    source_topic: str = ""
    source_consumer_group: str = ""
    
    # State
    state: DLQState = DLQState.ACTIVE
    
    # Configuration
    max_size: int = 10000
    retention_hours: int = 168  # 7 days
    retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    
    # Messages
    message_count: int = 0
    
    # Stats
    total_received: int = 0
    total_reprocessed: int = 0
    total_discarded: int = 0
    
    # Alerts
    alert_threshold: int = 100
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)


@dataclass
class ErrorPattern:
    """Паттерн ошибки"""
    pattern_id: str
    
    # Pattern
    error_code: str = ""
    error_message_pattern: str = ""
    
    # Category
    category: ErrorCategory = ErrorCategory.UNKNOWN
    
    # Stats
    occurrence_count: int = 0
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    
    # Affected
    affected_services: Set[str] = field(default_factory=set)
    affected_topics: Set[str] = field(default_factory=set)


@dataclass
class AlertRule:
    """Правило алертинга"""
    rule_id: str
    name: str
    
    # Condition
    queue_id: str = ""
    threshold: int = 100
    time_window_minutes: int = 5
    
    # Notification
    notification_channels: List[str] = field(default_factory=list)
    
    # State
    enabled: bool = True
    triggered: bool = False
    last_triggered: Optional[datetime] = None
    
    # Cooldown
    cooldown_minutes: int = 15


class DeadLetterQueueManager:
    """Менеджер Dead Letter Queue"""
    
    def __init__(self):
        self.queues: Dict[str, DeadLetterQueue] = {}
        self.messages: Dict[str, DeadLetterMessage] = {}
        self.queue_messages: Dict[str, List[str]] = {}  # queue_id -> message_ids
        self.error_patterns: Dict[str, ErrorPattern] = {}
        self.alert_rules: Dict[str, AlertRule] = {}
        
        # Processing
        self._processing: Set[str] = set()
        
    def create_queue(self, name: str, source_topic: str,
                    source_consumer_group: str = "",
                    max_size: int = 10000,
                    retention_hours: int = 168) -> DeadLetterQueue:
        """Создание DLQ"""
        queue = DeadLetterQueue(
            queue_id=f"dlq_{uuid.uuid4().hex[:8]}",
            name=name,
            source_topic=source_topic,
            source_consumer_group=source_consumer_group,
            max_size=max_size,
            retention_hours=retention_hours
        )
        
        self.queues[queue.queue_id] = queue
        self.queue_messages[queue.queue_id] = []
        
        return queue
        
    def capture_message(self, queue_name: str, payload: Any,
                       original_topic: str, error_message: str,
                       error_code: str = "", source_service: str = "",
                       original_key: str = "",
                       headers: Dict[str, str] = None) -> Optional[DeadLetterMessage]:
        """Захват сообщения в DLQ"""
        # Find queue
        queue = None
        for q in self.queues.values():
            if q.name == queue_name and q.state == DLQState.ACTIVE:
                queue = q
                break
                
        if not queue:
            return None
            
        # Check capacity
        if queue.message_count >= queue.max_size:
            return None
            
        # Detect error category
        category = self._detect_error_category(error_message, error_code)
        
        # Create message
        message = DeadLetterMessage(
            message_id=f"dlm_{uuid.uuid4().hex[:8]}",
            original_topic=original_topic,
            original_key=original_key,
            payload=payload,
            headers=headers or {},
            error_message=error_message,
            error_code=error_code,
            error_category=category,
            source_service=source_service,
            expires_at=datetime.now() + timedelta(hours=queue.retention_hours)
        )
        
        self.messages[message.message_id] = message
        self.queue_messages[queue.queue_id].append(message.message_id)
        
        queue.message_count += 1
        queue.total_received += 1
        queue.last_activity = datetime.now()
        
        # Track error pattern
        self._track_error_pattern(message)
        
        # Check alerts
        self._check_alerts(queue)
        
        return message
        
    def _detect_error_category(self, error_message: str,
                              error_code: str) -> ErrorCategory:
        """Определение категории ошибки"""
        error_lower = error_message.lower()
        
        if any(x in error_lower for x in ["timeout", "timed out"]):
            return ErrorCategory.TIMEOUT
        elif any(x in error_lower for x in ["capacity", "full", "limit"]):
            return ErrorCategory.CAPACITY
        elif any(x in error_lower for x in ["validation", "invalid", "required"]):
            return ErrorCategory.VALIDATION
        elif any(x in error_lower for x in ["connection", "unavailable", "retry"]):
            return ErrorCategory.TRANSIENT
        elif any(x in error_lower for x in ["permission", "forbidden", "unauthorized"]):
            return ErrorCategory.PERMANENT
        else:
            return ErrorCategory.UNKNOWN
            
    def _track_error_pattern(self, message: DeadLetterMessage):
        """Трекинг паттерна ошибки"""
        pattern_key = f"{message.error_code}:{message.error_category.value}"
        
        if pattern_key not in self.error_patterns:
            self.error_patterns[pattern_key] = ErrorPattern(
                pattern_id=f"pat_{uuid.uuid4().hex[:8]}",
                error_code=message.error_code,
                category=message.error_category
            )
            
        pattern = self.error_patterns[pattern_key]
        pattern.occurrence_count += 1
        pattern.last_seen = datetime.now()
        pattern.affected_services.add(message.source_service)
        pattern.affected_topics.add(message.original_topic)
        
    def _check_alerts(self, queue: DeadLetterQueue):
        """Проверка алертов"""
        for rule in self.alert_rules.values():
            if rule.queue_id != queue.queue_id or not rule.enabled:
                continue
                
            if queue.message_count >= rule.threshold:
                if not rule.triggered or (
                    rule.last_triggered and 
                    datetime.now() - rule.last_triggered > timedelta(minutes=rule.cooldown_minutes)
                ):
                    rule.triggered = True
                    rule.last_triggered = datetime.now()
                    
    async def retry_message(self, message_id: str) -> bool:
        """Повторная обработка сообщения"""
        message = self.messages.get(message_id)
        if not message:
            return False
            
        if message_id in self._processing:
            return False
            
        if message.state not in [MessageState.PENDING, MessageState.PROCESSING]:
            return False
            
        if message.retry_count >= message.max_retries:
            return False
            
        self._processing.add(message_id)
        message.state = MessageState.PROCESSING
        message.retry_count += 1
        message.last_retry_at = datetime.now()
        
        try:
            # Simulate retry
            await asyncio.sleep(random.uniform(0.01, 0.1))
            
            if random.random() < 0.7:  # 70% success
                message.state = MessageState.REPROCESSED
                message.processed_at = datetime.now()
                
                # Update queue stats
                for qid, msg_ids in self.queue_messages.items():
                    if message_id in msg_ids:
                        queue = self.queues.get(qid)
                        if queue:
                            queue.total_reprocessed += 1
                            queue.message_count -= 1
                        break
                        
                return True
            else:
                message.state = MessageState.PENDING
                
                # Calculate next retry time
                queue = self._get_message_queue(message_id)
                if queue:
                    delay = self._calculate_retry_delay(queue.retry_strategy, message.retry_count)
                    message.next_retry_at = datetime.now() + timedelta(seconds=delay)
                    
                return False
                
        finally:
            self._processing.discard(message_id)
            
    def _get_message_queue(self, message_id: str) -> Optional[DeadLetterQueue]:
        """Получение очереди для сообщения"""
        for qid, msg_ids in self.queue_messages.items():
            if message_id in msg_ids:
                return self.queues.get(qid)
        return None
        
    def _calculate_retry_delay(self, strategy: RetryStrategy,
                              retry_count: int) -> float:
        """Расчёт задержки для повтора"""
        if strategy == RetryStrategy.IMMEDIATE:
            return 0
        elif strategy == RetryStrategy.LINEAR:
            return retry_count * 10  # 10, 20, 30 seconds
        elif strategy == RetryStrategy.EXPONENTIAL:
            return min(2 ** retry_count * 5, 300)  # Max 5 minutes
        else:
            return 30
            
    async def retry_all_pending(self, queue_id: str,
                               batch_size: int = 100) -> Dict[str, int]:
        """Повторная обработка всех pending"""
        queue = self.queues.get(queue_id)
        if not queue:
            return {"success": 0, "failed": 0}
            
        msg_ids = self.queue_messages.get(queue_id, [])
        pending = [
            mid for mid in msg_ids
            if self.messages.get(mid) and 
            self.messages[mid].state == MessageState.PENDING
        ]
        
        success = 0
        failed = 0
        
        for msg_id in pending[:batch_size]:
            result = await self.retry_message(msg_id)
            if result:
                success += 1
            else:
                failed += 1
                
        return {"success": success, "failed": failed}
        
    def discard_message(self, message_id: str, reason: str = "") -> bool:
        """Отбрасывание сообщения"""
        message = self.messages.get(message_id)
        if not message:
            return False
            
        message.state = MessageState.DISCARDED
        message.processed_at = datetime.now()
        message.metadata["discard_reason"] = reason
        
        # Update queue
        for qid, msg_ids in self.queue_messages.items():
            if message_id in msg_ids:
                queue = self.queues.get(qid)
                if queue:
                    queue.total_discarded += 1
                    queue.message_count -= 1
                break
                
        return True
        
    def create_alert_rule(self, name: str, queue_id: str,
                         threshold: int, channels: List[str]) -> AlertRule:
        """Создание правила алертинга"""
        rule = AlertRule(
            rule_id=f"alert_{uuid.uuid4().hex[:8]}",
            name=name,
            queue_id=queue_id,
            threshold=threshold,
            notification_channels=channels
        )
        
        self.alert_rules[rule.rule_id] = rule
        return rule
        
    def get_queue_messages(self, queue_id: str, state: MessageState = None,
                          limit: int = 100) -> List[DeadLetterMessage]:
        """Получение сообщений очереди"""
        msg_ids = self.queue_messages.get(queue_id, [])
        
        messages = [
            self.messages[mid] for mid in msg_ids
            if mid in self.messages
        ]
        
        if state:
            messages = [m for m in messages if m.state == state]
            
        return messages[:limit]
        
    def get_error_analysis(self) -> Dict[str, Any]:
        """Анализ ошибок"""
        category_counts: Dict[ErrorCategory, int] = {}
        service_counts: Dict[str, int] = {}
        
        for message in self.messages.values():
            category_counts[message.error_category] = category_counts.get(message.error_category, 0) + 1
            if message.source_service:
                service_counts[message.source_service] = service_counts.get(message.source_service, 0) + 1
                
        return {
            "total_messages": len(self.messages),
            "by_category": {c.value: cnt for c, cnt in category_counts.items()},
            "by_service": service_counts,
            "patterns_count": len(self.error_patterns),
            "top_patterns": sorted(
                self.error_patterns.values(),
                key=lambda p: -p.occurrence_count
            )[:5]
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        state_counts: Dict[MessageState, int] = {}
        for msg in self.messages.values():
            state_counts[msg.state] = state_counts.get(msg.state, 0) + 1
            
        active_queues = sum(1 for q in self.queues.values() if q.state == DLQState.ACTIVE)
        total_received = sum(q.total_received for q in self.queues.values())
        total_reprocessed = sum(q.total_reprocessed for q in self.queues.values())
        
        return {
            "queues_total": len(self.queues),
            "queues_active": active_queues,
            "messages_total": len(self.messages),
            "messages_pending": state_counts.get(MessageState.PENDING, 0),
            "messages_reprocessed": state_counts.get(MessageState.REPROCESSED, 0),
            "messages_discarded": state_counts.get(MessageState.DISCARDED, 0),
            "total_received": total_received,
            "total_reprocessed": total_reprocessed,
            "reprocess_rate": (total_reprocessed / total_received * 100) if total_received > 0 else 0,
            "alert_rules": len(self.alert_rules),
            "error_patterns": len(self.error_patterns)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 254: Dead Letter Queue Platform")
    print("=" * 60)
    
    manager = DeadLetterQueueManager()
    print("✓ DLQ Manager created")
    
    # Create queues
    print("\n📬 Creating Dead Letter Queues...")
    
    queues_data = [
        ("order-events-dlq", "order-events", "order-processor"),
        ("payment-events-dlq", "payment-events", "payment-service"),
        ("notification-dlq", "notifications", "email-sender"),
        ("inventory-dlq", "inventory-events", "inventory-service"),
    ]
    
    queues = []
    for name, source_topic, consumer_group in queues_data:
        queue = manager.create_queue(name, source_topic, consumer_group)
        queues.append(queue)
        print(f"  📬 {name} (source: {source_topic})")
        
    # Create alert rules
    print("\n🔔 Creating Alert Rules...")
    
    for queue in queues[:2]:
        rule = manager.create_alert_rule(
            f"{queue.name}-alert",
            queue.queue_id,
            threshold=50,
            channels=["slack", "email"]
        )
        print(f"  🔔 {rule.name} (threshold: {rule.threshold})")
        
    # Capture messages
    print("\n📥 Capturing Failed Messages...")
    
    errors = [
        ("order-events-dlq", {"order_id": "ORD-001"}, "order-events", "Connection timeout to database", "CONN_TIMEOUT", "order-service"),
        ("order-events-dlq", {"order_id": "ORD-002"}, "order-events", "Invalid order status transition", "VALIDATION_ERROR", "order-service"),
        ("payment-events-dlq", {"payment_id": "PAY-001"}, "payment-events", "Payment gateway unavailable", "GATEWAY_DOWN", "payment-service"),
        ("payment-events-dlq", {"payment_id": "PAY-002"}, "payment-events", "Insufficient funds", "INSUFFICIENT_FUNDS", "payment-service"),
        ("notification-dlq", {"email": "test@example.com"}, "notifications", "SMTP connection refused", "SMTP_ERROR", "email-service"),
        ("notification-dlq", {"email": "invalid"}, "notifications", "Invalid email format", "VALIDATION_ERROR", "email-service"),
        ("inventory-dlq", {"product_id": "P001"}, "inventory-events", "Capacity limit exceeded", "CAPACITY_EXCEEDED", "inventory-service"),
    ]
    
    messages = []
    for queue_name, payload, topic, error_msg, error_code, service in errors:
        msg = manager.capture_message(
            queue_name, payload, topic,
            error_msg, error_code, service
        )
        if msg:
            messages.append(msg)
            cat_icon = {
                ErrorCategory.TIMEOUT: "⏱",
                ErrorCategory.VALIDATION: "⚠",
                ErrorCategory.TRANSIENT: "↻",
                ErrorCategory.CAPACITY: "📊",
                ErrorCategory.PERMANENT: "🚫"
            }.get(msg.error_category, "?")
            print(f"  {cat_icon} {error_code}: {error_msg[:40]}...")
            
    # Display queues
    print("\n📬 Dead Letter Queues:")
    
    print("\n  ┌─────────────────────┬─────────────────┬──────────┬──────────┬──────────┐")
    print("  │ Queue               │ Source Topic    │ Messages │ Received │ State    │")
    print("  ├─────────────────────┼─────────────────┼──────────┼──────────┼──────────┤")
    
    for queue in manager.queues.values():
        name = queue.name[:19].ljust(19)
        source = queue.source_topic[:15].ljust(15)
        msgs = str(queue.message_count)[:8].ljust(8)
        received = str(queue.total_received)[:8].ljust(8)
        state = queue.state.value[:8].ljust(8)
        
        print(f"  │ {name} │ {source} │ {msgs} │ {received} │ {state} │")
        
    print("  └─────────────────────┴─────────────────┴──────────┴──────────┴──────────┘")
    
    # Display messages
    print("\n📨 Messages in order-events-dlq:")
    
    print("\n  ┌──────────────────┬─────────────────┬───────────────┬───────────┬──────────┐")
    print("  │ Message          │ Error Code      │ Category      │ Retries   │ State    │")
    print("  ├──────────────────┼─────────────────┼───────────────┼───────────┼──────────┤")
    
    queue_msgs = manager.get_queue_messages(queues[0].queue_id)
    for msg in queue_msgs:
        msg_id = msg.message_id[:16].ljust(16)
        error_code = msg.error_code[:15].ljust(15)
        category = msg.error_category.value[:13].ljust(13)
        retries = f"{msg.retry_count}/{msg.max_retries}"[:9].ljust(9)
        state = msg.state.value[:8].ljust(8)
        
        print(f"  │ {msg_id} │ {error_code} │ {category} │ {retries} │ {state} │")
        
    print("  └──────────────────┴─────────────────┴───────────────┴───────────┴──────────┘")
    
    # Retry messages
    print("\n🔄 Retrying Messages...")
    
    for queue in queues[:2]:
        result = await manager.retry_all_pending(queue.queue_id)
        print(f"  🔄 {queue.name}: success={result['success']}, failed={result['failed']}")
        
    # Error analysis
    print("\n📊 Error Analysis:")
    
    analysis = manager.get_error_analysis()
    
    print("\n  By Category:")
    for category, count in analysis['by_category'].items():
        bar = "█" * min(count, 10)
        print(f"    {category:12s} [{bar:10s}] {count}")
        
    print("\n  By Service:")
    for service, count in analysis['by_service'].items():
        print(f"    {service}: {count}")
        
    # Error patterns
    print("\n🔍 Error Patterns:")
    
    for pattern in list(manager.error_patterns.values())[:5]:
        print(f"  [{pattern.error_code}] {pattern.category.value}")
        print(f"    Occurrences: {pattern.occurrence_count}")
        print(f"    Services: {', '.join(pattern.affected_services)}")
        
    # Alert rules
    print("\n🔔 Alert Rules:")
    
    for rule in manager.alert_rules.values():
        status = "🔴 TRIGGERED" if rule.triggered else "🟢 OK"
        queue = manager.queues.get(rule.queue_id)
        queue_name = queue.name if queue else "?"
        print(f"  {status} {rule.name}")
        print(f"    Queue: {queue_name}, Threshold: {rule.threshold}")
        
    # Discard test
    print("\n🗑 Discarding Invalid Message...")
    
    if messages:
        validation_msg = next((m for m in messages if m.error_category == ErrorCategory.VALIDATION), None)
        if validation_msg:
            manager.discard_message(validation_msg.message_id, "Invalid data - cannot reprocess")
            print(f"  🗑 Discarded {validation_msg.message_id}")
            
    # Message state distribution
    print("\n📊 Message State Distribution:")
    
    state_counts: Dict[MessageState, int] = {}
    for msg in manager.messages.values():
        state_counts[msg.state] = state_counts.get(msg.state, 0) + 1
        
    for state in MessageState:
        count = state_counts.get(state, 0)
        bar = "█" * count + "░" * (10 - count)
        icon = {
            MessageState.PENDING: "○",
            MessageState.PROCESSING: "◐",
            MessageState.REPROCESSED: "✓",
            MessageState.DISCARDED: "🗑",
            MessageState.EXPIRED: "⏰"
        }.get(state, "?")
        print(f"  {icon} {state.value:12s} [{bar}] {count}")
        
    # Statistics
    print("\n📊 DLQ Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Queues: {stats['queues_total']} (active: {stats['queues_active']})")
    print(f"  Messages: {stats['messages_total']} (pending: {stats['messages_pending']})")
    
    print(f"\n  Total Received: {stats['total_received']}")
    print(f"  Total Reprocessed: {stats['total_reprocessed']}")
    print(f"  Reprocess Rate: {stats['reprocess_rate']:.1f}%")
    
    print(f"\n  Alert Rules: {stats['alert_rules']}")
    print(f"  Error Patterns: {stats['error_patterns']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Dead Letter Queue Dashboard                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Queues:                        {stats['queues_total']:>12}                        │")
    print(f"│ Messages:                      {stats['messages_total']:>12}                        │")
    print(f"│ Pending:                       {stats['messages_pending']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Received:                {stats['total_received']:>12}                        │")
    print(f"│ Reprocess Rate:                {stats['reprocess_rate']:>11.1f}%                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Dead Letter Queue Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
