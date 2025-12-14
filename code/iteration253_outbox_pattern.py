#!/usr/bin/env python3
"""
Server Init - Iteration 253: Outbox Pattern Platform
Платформа реализации паттерна Outbox для надёжной доставки событий

Функционал:
- Outbox Table Management - управление таблицей outbox
- Event Capture - захват событий
- Reliable Publishing - надёжная публикация
- Change Data Capture - захват изменений
- Deduplication - дедупликация
- Order Guarantee - гарантия порядка
- Cleanup & Archiving - очистка и архивирование
- Monitoring - мониторинг
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import json
import hashlib


class OutboxEntryState(Enum):
    """Состояние записи outbox"""
    PENDING = "pending"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
    ARCHIVED = "archived"


class AggregateType(Enum):
    """Тип агрегата"""
    ORDER = "order"
    USER = "user"
    PAYMENT = "payment"
    INVENTORY = "inventory"
    NOTIFICATION = "notification"


class PublishResult(Enum):
    """Результат публикации"""
    SUCCESS = "success"
    RETRY = "retry"
    FAILED = "failed"
    DUPLICATE = "duplicate"


@dataclass
class OutboxEntry:
    """Запись в outbox таблице"""
    entry_id: str
    
    # Aggregate
    aggregate_type: AggregateType = AggregateType.ORDER
    aggregate_id: str = ""
    
    # Event
    event_type: str = ""
    event_payload: Dict[str, Any] = field(default_factory=dict)
    
    # State
    state: OutboxEntryState = OutboxEntryState.PENDING
    
    # Publishing
    topic: str = ""
    partition_key: str = ""
    
    # Deduplication
    idempotency_key: str = ""
    payload_hash: str = ""
    
    # Ordering
    sequence_number: int = 0
    
    # Retry
    attempts: int = 0
    max_attempts: int = 5
    last_error: str = ""
    next_retry_at: Optional[datetime] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    published_at: Optional[datetime] = None


@dataclass
class OutboxBatch:
    """Batch для обработки"""
    batch_id: str
    
    # Entries
    entries: List[str] = field(default_factory=list)  # entry_ids
    
    # State
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    # Stats
    total: int = 0
    published: int = 0
    failed: int = 0


@dataclass
class DeduplicationRecord:
    """Запись дедупликации"""
    record_id: str
    idempotency_key: str
    payload_hash: str
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=7))


@dataclass
class PublishMetrics:
    """Метрики публикации"""
    topic: str
    
    # Counters
    total_published: int = 0
    total_failed: int = 0
    total_retried: int = 0
    total_duplicates: int = 0
    
    # Latency
    total_latency_ms: float = 0
    min_latency_ms: float = float('inf')
    max_latency_ms: float = 0
    
    # Time
    last_published_at: Optional[datetime] = None


@dataclass
class CleanupConfig:
    """Конфигурация очистки"""
    retention_days: int = 30
    archive_enabled: bool = True
    batch_size: int = 1000
    
    # Schedule
    schedule_cron: str = "0 0 * * *"  # Daily at midnight


class OutboxManager:
    """Менеджер Outbox паттерна"""
    
    def __init__(self):
        self.entries: Dict[str, OutboxEntry] = {}
        self.batches: Dict[str, OutboxBatch] = {}
        self.dedup_records: Dict[str, DeduplicationRecord] = {}
        self.metrics: Dict[str, PublishMetrics] = {}
        self.archived_entries: List[OutboxEntry] = []
        
        # Sequence counters per aggregate
        self._sequences: Dict[str, int] = {}
        
        # Processing lock
        self._processing_entries: Set[str] = set()
        
        # Config
        self.cleanup_config = CleanupConfig()
        
    def capture_event(self, aggregate_type: AggregateType,
                     aggregate_id: str, event_type: str,
                     payload: Dict[str, Any],
                     topic: str = "",
                     idempotency_key: str = "") -> OutboxEntry:
        """Захват события в outbox"""
        # Generate keys
        if not idempotency_key:
            idempotency_key = f"{aggregate_type.value}:{aggregate_id}:{event_type}:{uuid.uuid4().hex[:8]}"
            
        payload_hash = hashlib.md5(
            json.dumps(payload, sort_keys=True, default=str).encode()
        ).hexdigest()
        
        # Get sequence
        seq_key = f"{aggregate_type.value}:{aggregate_id}"
        self._sequences[seq_key] = self._sequences.get(seq_key, 0) + 1
        sequence = self._sequences[seq_key]
        
        # Create entry
        entry = OutboxEntry(
            entry_id=f"outbox_{uuid.uuid4().hex[:8]}",
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            event_type=event_type,
            event_payload=payload,
            topic=topic or f"{aggregate_type.value}-events",
            partition_key=aggregate_id,
            idempotency_key=idempotency_key,
            payload_hash=payload_hash,
            sequence_number=sequence
        )
        
        self.entries[entry.entry_id] = entry
        
        # Initialize topic metrics
        if entry.topic not in self.metrics:
            self.metrics[entry.topic] = PublishMetrics(topic=entry.topic)
            
        return entry
        
    async def publish_entry(self, entry_id: str) -> PublishResult:
        """Публикация записи"""
        entry = self.entries.get(entry_id)
        if not entry:
            return PublishResult.FAILED
            
        if entry_id in self._processing_entries:
            return PublishResult.RETRY
            
        # Check deduplication
        if entry.idempotency_key in self.dedup_records:
            entry.state = OutboxEntryState.PUBLISHED
            self.metrics[entry.topic].total_duplicates += 1
            return PublishResult.DUPLICATE
            
        # Mark as processing
        self._processing_entries.add(entry_id)
        entry.state = OutboxEntryState.PROCESSING
        entry.attempts += 1
        
        start_time = datetime.now()
        
        try:
            # Simulate publishing
            await asyncio.sleep(random.uniform(0.01, 0.1))
            
            if random.random() < 0.9:  # 90% success rate
                # Success
                entry.state = OutboxEntryState.PUBLISHED
                entry.published_at = datetime.now()
                entry.processed_at = datetime.now()
                
                # Record for deduplication
                self.dedup_records[entry.idempotency_key] = DeduplicationRecord(
                    record_id=f"dedup_{uuid.uuid4().hex[:8]}",
                    idempotency_key=entry.idempotency_key,
                    payload_hash=entry.payload_hash
                )
                
                # Update metrics
                metrics = self.metrics[entry.topic]
                latency = (datetime.now() - start_time).total_seconds() * 1000
                metrics.total_published += 1
                metrics.total_latency_ms += latency
                metrics.min_latency_ms = min(metrics.min_latency_ms, latency)
                metrics.max_latency_ms = max(metrics.max_latency_ms, latency)
                metrics.last_published_at = datetime.now()
                
                return PublishResult.SUCCESS
            else:
                raise Exception("Simulated publish failure")
                
        except Exception as e:
            entry.last_error = str(e)
            
            if entry.attempts >= entry.max_attempts:
                entry.state = OutboxEntryState.FAILED
                self.metrics[entry.topic].total_failed += 1
                return PublishResult.FAILED
            else:
                entry.state = OutboxEntryState.PENDING
                entry.next_retry_at = datetime.now() + timedelta(
                    seconds=2 ** entry.attempts  # Exponential backoff
                )
                self.metrics[entry.topic].total_retried += 1
                return PublishResult.RETRY
                
        finally:
            self._processing_entries.discard(entry_id)
            
    async def process_pending(self, batch_size: int = 100) -> OutboxBatch:
        """Обработка pending записей"""
        batch = OutboxBatch(
            batch_id=f"batch_{uuid.uuid4().hex[:8]}",
            started_at=datetime.now()
        )
        
        # Get pending entries
        pending = [
            e for e in self.entries.values()
            if e.state == OutboxEntryState.PENDING
            and e.entry_id not in self._processing_entries
            and (e.next_retry_at is None or e.next_retry_at <= datetime.now())
        ]
        
        # Sort by sequence for ordering guarantee
        pending.sort(key=lambda e: (e.aggregate_id, e.sequence_number))
        
        # Process batch
        for entry in pending[:batch_size]:
            batch.entries.append(entry.entry_id)
            batch.total += 1
            
            result = await self.publish_entry(entry.entry_id)
            
            if result == PublishResult.SUCCESS:
                batch.published += 1
            elif result == PublishResult.FAILED:
                batch.failed += 1
                
        batch.completed_at = datetime.now()
        self.batches[batch.batch_id] = batch
        
        return batch
        
    async def cleanup_old_entries(self) -> Dict[str, int]:
        """Очистка старых записей"""
        cutoff = datetime.now() - timedelta(days=self.cleanup_config.retention_days)
        
        archived = 0
        deleted = 0
        
        entries_to_process = [
            e for e in self.entries.values()
            if e.state == OutboxEntryState.PUBLISHED
            and e.published_at and e.published_at < cutoff
        ]
        
        for entry in entries_to_process:
            if self.cleanup_config.archive_enabled:
                entry.state = OutboxEntryState.ARCHIVED
                self.archived_entries.append(entry)
                archived += 1
            else:
                deleted += 1
                
            del self.entries[entry.entry_id]
            
        # Cleanup dedup records
        dedup_expired = [
            key for key, record in self.dedup_records.items()
            if record.expires_at < datetime.now()
        ]
        
        for key in dedup_expired:
            del self.dedup_records[key]
            
        return {
            "archived": archived,
            "deleted": deleted,
            "dedup_cleaned": len(dedup_expired)
        }
        
    def get_pending_count(self) -> int:
        """Количество pending записей"""
        return sum(1 for e in self.entries.values() if e.state == OutboxEntryState.PENDING)
        
    def get_failed_entries(self) -> List[OutboxEntry]:
        """Получение failed записей"""
        return [e for e in self.entries.values() if e.state == OutboxEntryState.FAILED]
        
    def get_entries_by_aggregate(self, aggregate_type: AggregateType,
                                aggregate_id: str) -> List[OutboxEntry]:
        """Получение записей по агрегату"""
        return [
            e for e in self.entries.values()
            if e.aggregate_type == aggregate_type
            and e.aggregate_id == aggregate_id
        ]
        
    def get_topic_metrics(self, topic: str) -> Optional[PublishMetrics]:
        """Метрики по топику"""
        return self.metrics.get(topic)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        state_counts: Dict[OutboxEntryState, int] = {}
        for entry in self.entries.values():
            state_counts[entry.state] = state_counts.get(entry.state, 0) + 1
            
        total_published = sum(m.total_published for m in self.metrics.values())
        total_failed = sum(m.total_failed for m in self.metrics.values())
        total_latency = sum(m.total_latency_ms for m in self.metrics.values())
        
        avg_latency = (total_latency / total_published) if total_published > 0 else 0
        
        return {
            "entries_total": len(self.entries),
            "entries_pending": state_counts.get(OutboxEntryState.PENDING, 0),
            "entries_processing": state_counts.get(OutboxEntryState.PROCESSING, 0),
            "entries_published": state_counts.get(OutboxEntryState.PUBLISHED, 0),
            "entries_failed": state_counts.get(OutboxEntryState.FAILED, 0),
            "batches_processed": len(self.batches),
            "dedup_records": len(self.dedup_records),
            "archived_entries": len(self.archived_entries),
            "total_published": total_published,
            "total_failed": total_failed,
            "avg_latency_ms": avg_latency,
            "topics_count": len(self.metrics)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 253: Outbox Pattern Platform")
    print("=" * 60)
    
    manager = OutboxManager()
    print("✓ Outbox Manager created")
    
    # Capture events
    print("\n📤 Capturing Events to Outbox...")
    
    events_to_capture = [
        (AggregateType.ORDER, "ORD-001", "order.created", {"amount": 99.99, "items": 3}),
        (AggregateType.ORDER, "ORD-001", "order.paid", {"payment_id": "PAY-001"}),
        (AggregateType.ORDER, "ORD-001", "order.shipped", {"tracking": "TRK123"}),
        (AggregateType.ORDER, "ORD-002", "order.created", {"amount": 149.99, "items": 5}),
        (AggregateType.USER, "USR-001", "user.created", {"email": "alice@example.com"}),
        (AggregateType.USER, "USR-001", "user.verified", {"verified": True}),
        (AggregateType.PAYMENT, "PAY-001", "payment.captured", {"amount": 99.99}),
        (AggregateType.INVENTORY, "INV-001", "inventory.reserved", {"product_id": "P001", "qty": 2}),
    ]
    
    entries = []
    for agg_type, agg_id, event_type, payload in events_to_capture:
        entry = manager.capture_event(agg_type, agg_id, event_type, payload)
        entries.append(entry)
        print(f"  📤 {event_type} -> {entry.topic} (seq: {entry.sequence_number})")
        
    # Process pending entries
    print("\n🔄 Processing Pending Entries...")
    
    batch = await manager.process_pending(batch_size=10)
    print(f"  📦 Batch {batch.batch_id[:12]}...")
    print(f"     Total: {batch.total}, Published: {batch.published}, Failed: {batch.failed}")
    
    # Process remaining
    while manager.get_pending_count() > 0:
        batch = await manager.process_pending(batch_size=10)
        if batch.total == 0:
            break
            
    # Display entries
    print("\n📋 Outbox Entries:")
    
    print("\n  ┌──────────────────┬───────────────┬─────────────────┬───────────┬──────────┐")
    print("  │ Entry            │ Aggregate     │ Event Type      │ State     │ Attempts │")
    print("  ├──────────────────┼───────────────┼─────────────────┼───────────┼──────────┤")
    
    for entry in list(manager.entries.values())[:8]:
        entry_id = entry.entry_id[:16].ljust(16)
        agg = f"{entry.aggregate_type.value[:4]}:{entry.aggregate_id[-4:]}"[:13].ljust(13)
        event = entry.event_type[:15].ljust(15)
        state = entry.state.value[:9].ljust(9)
        attempts = str(entry.attempts)[:8].ljust(8)
        
        print(f"  │ {entry_id} │ {agg} │ {event} │ {state} │ {attempts} │")
        
    print("  └──────────────────┴───────────────┴─────────────────┴───────────┴──────────┘")
    
    # Display by aggregate
    print("\n📊 Entries by Aggregate (ORD-001):")
    
    ord_entries = manager.get_entries_by_aggregate(AggregateType.ORDER, "ORD-001")
    for entry in ord_entries:
        status_icon = "✓" if entry.state == OutboxEntryState.PUBLISHED else "○"
        print(f"  {status_icon} [{entry.sequence_number}] {entry.event_type}: {entry.state.value}")
        
    # Topic metrics
    print("\n📊 Topic Metrics:")
    
    print("\n  ┌─────────────────────┬──────────┬──────────┬──────────┬──────────┐")
    print("  │ Topic               │ Published│ Failed   │ Retried  │ Avg(ms)  │")
    print("  ├─────────────────────┼──────────┼──────────┼──────────┼──────────┤")
    
    for topic, metrics in manager.metrics.items():
        topic_name = topic[:19].ljust(19)
        published = str(metrics.total_published)[:8].ljust(8)
        failed = str(metrics.total_failed)[:8].ljust(8)
        retried = str(metrics.total_retried)[:8].ljust(8)
        avg_lat = f"{metrics.total_latency_ms / max(1, metrics.total_published):.1f}"[:8].ljust(8)
        
        print(f"  │ {topic_name} │ {published} │ {failed} │ {retried} │ {avg_lat} │")
        
    print("  └─────────────────────┴──────────┴──────────┴──────────┴──────────┘")
    
    # Deduplication test
    print("\n🔒 Testing Deduplication...")
    
    # Try to capture same event again
    dup_entry = manager.capture_event(
        AggregateType.ORDER, "ORD-001", "order.created",
        {"amount": 99.99, "items": 3}
    )
    
    result = await manager.publish_entry(dup_entry.entry_id)
    if result == PublishResult.DUPLICATE:
        print(f"  🔒 Duplicate detected for {dup_entry.event_type}")
    else:
        print(f"  📤 Published (result: {result.value})")
        
    # Display dedup records
    print(f"\n🔐 Deduplication Records: {len(manager.dedup_records)}")
    
    for key, record in list(manager.dedup_records.items())[:3]:
        print(f"  🔐 {record.idempotency_key[:40]}...")
        
    # Failed entries
    print("\n❌ Failed Entries:")
    
    failed = manager.get_failed_entries()
    if failed:
        for entry in failed[:3]:
            print(f"  ❌ {entry.event_type}: {entry.last_error}")
    else:
        print("  No failed entries")
        
    # Cleanup simulation
    print("\n🧹 Cleanup Configuration:")
    
    config = manager.cleanup_config
    print(f"  Retention: {config.retention_days} days")
    print(f"  Archive: {'enabled' if config.archive_enabled else 'disabled'}")
    print(f"  Batch Size: {config.batch_size}")
    print(f"  Schedule: {config.schedule_cron}")
    
    # State distribution
    print("\n📊 Entry State Distribution:")
    
    state_counts: Dict[OutboxEntryState, int] = {}
    for entry in manager.entries.values():
        state_counts[entry.state] = state_counts.get(entry.state, 0) + 1
        
    for state in OutboxEntryState:
        count = state_counts.get(state, 0)
        bar = "█" * min(count, 10) + "░" * (10 - min(count, 10))
        icon = {
            OutboxEntryState.PENDING: "○",
            OutboxEntryState.PROCESSING: "◐",
            OutboxEntryState.PUBLISHED: "✓",
            OutboxEntryState.FAILED: "✗",
            OutboxEntryState.ARCHIVED: "📦"
        }.get(state, "?")
        print(f"  {icon} {state.value:12s} [{bar}] {count}")
        
    # Statistics
    print("\n📊 Outbox Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Entries Total: {stats['entries_total']}")
    print(f"  Pending: {stats['entries_pending']}")
    print(f"  Published: {stats['entries_published']}")
    print(f"  Failed: {stats['entries_failed']}")
    
    print(f"\n  Batches Processed: {stats['batches_processed']}")
    print(f"  Dedup Records: {stats['dedup_records']}")
    print(f"  Topics: {stats['topics_count']}")
    
    print(f"\n  Total Published: {stats['total_published']}")
    print(f"  Avg Latency: {stats['avg_latency_ms']:.1f}ms")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                     Outbox Pattern Dashboard                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Entries:                 {stats['entries_total']:>12}                        │")
    print(f"│ Pending:                       {stats['entries_pending']:>12}                        │")
    print(f"│ Published:                     {stats['entries_published']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Published:               {stats['total_published']:>12}                        │")
    print(f"│ Avg Latency:                   {stats['avg_latency_ms']:>10.1f}ms                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Outbox Pattern Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
