#!/usr/bin/env python3
"""
Server Init - Iteration 246: Event Sourcing Platform
Платформа Event Sourcing

Функционал:
- Event Store - хранилище событий
- Event Streams - потоки событий
- Aggregates - агрегаты
- Projections - проекции
- Snapshots - снапшоты состояния
- Event Replay - воспроизведение событий
- Causation/Correlation - связи событий
- Optimistic Concurrency - оптимистичный контроль
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


class EventType(Enum):
    """Тип события"""
    DOMAIN = "domain"
    INTEGRATION = "integration"
    SYSTEM = "system"


class StreamState(Enum):
    """Состояние потока"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ProjectionState(Enum):
    """Состояние проекции"""
    RUNNING = "running"
    STOPPED = "stopped"
    CATCHING_UP = "catching_up"
    ERROR = "error"


@dataclass
class Event:
    """Событие"""
    event_id: str
    
    # Type
    event_type: str = ""
    event_category: EventType = EventType.DOMAIN
    
    # Stream
    stream_id: str = ""
    stream_position: int = 0
    global_position: int = 0
    
    # Data
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Causation
    causation_id: str = ""
    correlation_id: str = ""
    
    # Time
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Hash
    data_hash: str = ""


@dataclass
class EventStream:
    """Поток событий"""
    stream_id: str
    stream_name: str = ""
    
    # Category
    category: str = ""
    aggregate_type: str = ""
    aggregate_id: str = ""
    
    # Events
    events: List[Event] = field(default_factory=list)
    current_version: int = 0
    
    # State
    state: StreamState = StreamState.ACTIVE
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)
    last_event_at: Optional[datetime] = None


@dataclass
class Snapshot:
    """Снапшот состояния"""
    snapshot_id: str
    
    # Stream
    stream_id: str = ""
    version: int = 0
    
    # State
    state: Dict[str, Any] = field(default_factory=dict)
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Projection:
    """Проекция"""
    projection_id: str
    name: str = ""
    
    # Handler
    event_types: List[str] = field(default_factory=list)
    
    # Position
    last_position: int = 0
    
    # State
    state: ProjectionState = ProjectionState.STOPPED
    current_state: Dict[str, Any] = field(default_factory=dict)
    
    # Checkpoints
    checkpoint_interval: int = 100
    last_checkpoint: int = 0
    
    # Stats
    events_processed: int = 0
    errors: int = 0
    
    # Time
    started_at: Optional[datetime] = None
    last_processed_at: Optional[datetime] = None


@dataclass
class Subscription:
    """Подписка на события"""
    subscription_id: str
    name: str = ""
    
    # Filter
    stream_pattern: str = "*"
    event_types: List[str] = field(default_factory=list)
    
    # Position
    start_from: int = 0
    current_position: int = 0
    
    # Consumer
    consumer_group: str = ""
    
    # Status
    is_active: bool = True
    
    # Stats
    messages_delivered: int = 0
    messages_acknowledged: int = 0


class EventSourcingPlatform:
    """Платформа Event Sourcing"""
    
    def __init__(self):
        self.streams: Dict[str, EventStream] = {}
        self.events: List[Event] = []
        self.snapshots: Dict[str, List[Snapshot]] = {}
        self.projections: Dict[str, Projection] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        
        self._global_position = 0
        self._projection_handlers: Dict[str, Callable] = {}
        
    def _compute_hash(self, data: Dict) -> str:
        """Вычисление хеша данных"""
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()[:16]
        
    def create_stream(self, category: str, aggregate_type: str,
                     aggregate_id: str, metadata: Dict[str, Any] = None) -> EventStream:
        """Создание потока событий"""
        stream_name = f"{category}-{aggregate_type}-{aggregate_id}"
        
        stream = EventStream(
            stream_id=f"str_{uuid.uuid4().hex[:8]}",
            stream_name=stream_name,
            category=category,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            metadata=metadata or {}
        )
        
        self.streams[stream.stream_id] = stream
        return stream
        
    def append_event(self, stream_id: str, event_type: str,
                    data: Dict[str, Any], metadata: Dict[str, Any] = None,
                    expected_version: int = None,
                    correlation_id: str = None,
                    causation_id: str = None) -> Optional[Event]:
        """Добавление события в поток"""
        stream = self.streams.get(stream_id)
        if not stream:
            return None
            
        # Optimistic concurrency check
        if expected_version is not None:
            if stream.current_version != expected_version:
                raise ValueError(
                    f"Concurrency conflict: expected {expected_version}, "
                    f"got {stream.current_version}"
                )
                
        self._global_position += 1
        stream.current_version += 1
        
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            stream_id=stream_id,
            stream_position=stream.current_version,
            global_position=self._global_position,
            data=data,
            metadata=metadata or {},
            correlation_id=correlation_id or str(uuid.uuid4()),
            causation_id=causation_id or "",
            data_hash=self._compute_hash(data)
        )
        
        stream.events.append(event)
        stream.last_event_at = event.timestamp
        self.events.append(event)
        
        # Process projections
        self._process_event_for_projections(event)
        
        return event
        
    def read_stream(self, stream_id: str, from_version: int = 0,
                   max_count: int = 100) -> List[Event]:
        """Чтение событий из потока"""
        stream = self.streams.get(stream_id)
        if not stream:
            return []
            
        events = [e for e in stream.events if e.stream_position > from_version]
        return events[:max_count]
        
    def read_all(self, from_position: int = 0, max_count: int = 100) -> List[Event]:
        """Чтение всех событий"""
        events = [e for e in self.events if e.global_position > from_position]
        return events[:max_count]
        
    def create_snapshot(self, stream_id: str, state: Dict[str, Any]) -> Optional[Snapshot]:
        """Создание снапшота"""
        stream = self.streams.get(stream_id)
        if not stream:
            return None
            
        snapshot = Snapshot(
            snapshot_id=f"snap_{uuid.uuid4().hex[:8]}",
            stream_id=stream_id,
            version=stream.current_version,
            state=state
        )
        
        if stream_id not in self.snapshots:
            self.snapshots[stream_id] = []
            
        self.snapshots[stream_id].append(snapshot)
        return snapshot
        
    def get_latest_snapshot(self, stream_id: str) -> Optional[Snapshot]:
        """Получение последнего снапшота"""
        snapshots = self.snapshots.get(stream_id, [])
        return snapshots[-1] if snapshots else None
        
    def rebuild_state(self, stream_id: str, 
                     reducer: Callable[[Dict, Event], Dict]) -> Dict[str, Any]:
        """Восстановление состояния из событий"""
        # Try to use snapshot
        snapshot = self.get_latest_snapshot(stream_id)
        
        if snapshot:
            state = snapshot.state.copy()
            from_version = snapshot.version
        else:
            state = {}
            from_version = 0
            
        # Apply events
        events = self.read_stream(stream_id, from_version)
        
        for event in events:
            state = reducer(state, event)
            
        return state
        
    def create_projection(self, name: str, event_types: List[str],
                         checkpoint_interval: int = 100) -> Projection:
        """Создание проекции"""
        projection = Projection(
            projection_id=f"proj_{uuid.uuid4().hex[:8]}",
            name=name,
            event_types=event_types,
            checkpoint_interval=checkpoint_interval
        )
        
        self.projections[projection.projection_id] = projection
        return projection
        
    def start_projection(self, projection_id: str):
        """Запуск проекции"""
        projection = self.projections.get(projection_id)
        if projection:
            projection.state = ProjectionState.RUNNING
            projection.started_at = datetime.now()
            
    def stop_projection(self, projection_id: str):
        """Остановка проекции"""
        projection = self.projections.get(projection_id)
        if projection:
            projection.state = ProjectionState.STOPPED
            
    def _process_event_for_projections(self, event: Event):
        """Обработка события для проекций"""
        for projection in self.projections.values():
            if projection.state != ProjectionState.RUNNING:
                continue
                
            if event.event_type in projection.event_types or "*" in projection.event_types:
                projection.events_processed += 1
                projection.last_position = event.global_position
                projection.last_processed_at = datetime.now()
                
                # Checkpoint
                if projection.events_processed % projection.checkpoint_interval == 0:
                    projection.last_checkpoint = event.global_position
                    
    def create_subscription(self, name: str, stream_pattern: str = "*",
                           event_types: List[str] = None,
                           start_from: int = 0) -> Subscription:
        """Создание подписки"""
        subscription = Subscription(
            subscription_id=f"sub_{uuid.uuid4().hex[:8]}",
            name=name,
            stream_pattern=stream_pattern,
            event_types=event_types or [],
            start_from=start_from,
            current_position=start_from
        )
        
        self.subscriptions[subscription.subscription_id] = subscription
        return subscription
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_snapshots = sum(len(s) for s in self.snapshots.values())
        
        running_projections = sum(
            1 for p in self.projections.values()
            if p.state == ProjectionState.RUNNING
        )
        
        return {
            "total_streams": len(self.streams),
            "total_events": len(self.events),
            "global_position": self._global_position,
            "total_snapshots": total_snapshots,
            "total_projections": len(self.projections),
            "running_projections": running_projections,
            "total_subscriptions": len(self.subscriptions)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 246: Event Sourcing Platform")
    print("=" * 60)
    
    platform = EventSourcingPlatform()
    print("✓ Event Sourcing Platform created")
    
    # Create streams for different aggregates
    print("\n📊 Creating Event Streams...")
    
    # User aggregate
    user_stream = platform.create_stream("users", "User", "user-123")
    print(f"  📊 {user_stream.stream_name}")
    
    # Order aggregate
    order_stream = platform.create_stream("orders", "Order", "order-456")
    print(f"  📊 {order_stream.stream_name}")
    
    # Account aggregate
    account_stream = platform.create_stream("accounts", "Account", "acc-789")
    print(f"  📊 {account_stream.stream_name}")
    
    # Append events
    print("\n📝 Appending Events...")
    
    correlation_id = str(uuid.uuid4())
    
    # User events
    events = [
        (user_stream.stream_id, "UserCreated", {"user_id": "user-123", "email": "alice@example.com", "name": "Alice"}),
        (user_stream.stream_id, "UserEmailVerified", {"user_id": "user-123", "verified_at": datetime.now().isoformat()}),
        (user_stream.stream_id, "UserProfileUpdated", {"user_id": "user-123", "phone": "+1234567890"}),
    ]
    
    for stream_id, event_type, data in events:
        evt = platform.append_event(stream_id, event_type, data, correlation_id=correlation_id)
        print(f"  📝 {event_type} (pos: {evt.global_position})")
        
    # Order events
    order_events = [
        (order_stream.stream_id, "OrderCreated", {"order_id": "order-456", "user_id": "user-123", "items": []}),
        (order_stream.stream_id, "ItemAdded", {"order_id": "order-456", "product_id": "prod-1", "quantity": 2, "price": 29.99}),
        (order_stream.stream_id, "ItemAdded", {"order_id": "order-456", "product_id": "prod-2", "quantity": 1, "price": 49.99}),
        (order_stream.stream_id, "OrderSubmitted", {"order_id": "order-456", "total": 109.97}),
        (order_stream.stream_id, "PaymentReceived", {"order_id": "order-456", "amount": 109.97, "method": "card"}),
        (order_stream.stream_id, "OrderShipped", {"order_id": "order-456", "tracking": "TRK123456"}),
    ]
    
    for stream_id, event_type, data in order_events:
        evt = platform.append_event(stream_id, event_type, data, correlation_id=correlation_id)
        print(f"  📝 {event_type} (pos: {evt.global_position})")
        
    # Account events
    account_events = [
        (account_stream.stream_id, "AccountOpened", {"account_id": "acc-789", "owner": "user-123", "balance": 0}),
        (account_stream.stream_id, "MoneyDeposited", {"account_id": "acc-789", "amount": 1000}),
        (account_stream.stream_id, "MoneyWithdrawn", {"account_id": "acc-789", "amount": 150}),
        (account_stream.stream_id, "MoneyDeposited", {"account_id": "acc-789", "amount": 500}),
    ]
    
    for stream_id, event_type, data in account_events:
        evt = platform.append_event(stream_id, event_type, data, correlation_id=correlation_id)
        print(f"  📝 {event_type} (pos: {evt.global_position})")
        
    # Create projections
    print("\n📺 Creating Projections...")
    
    order_projection = platform.create_projection(
        "OrderSummary",
        ["OrderCreated", "ItemAdded", "OrderSubmitted", "OrderShipped"]
    )
    platform.start_projection(order_projection.projection_id)
    print(f"  📺 {order_projection.name} (running)")
    
    account_projection = platform.create_projection(
        "AccountBalance",
        ["AccountOpened", "MoneyDeposited", "MoneyWithdrawn"]
    )
    platform.start_projection(account_projection.projection_id)
    print(f"  📺 {account_projection.name} (running)")
    
    # Read stream
    print("\n📖 Reading Order Stream:")
    
    order_events_read = platform.read_stream(order_stream.stream_id)
    for evt in order_events_read:
        print(f"  {evt.stream_position}. {evt.event_type}: {json.dumps(evt.data)[:50]}...")
        
    # Rebuild state
    print("\n🔄 Rebuilding Account State:")
    
    def account_reducer(state: Dict, event: Event) -> Dict:
        if event.event_type == "AccountOpened":
            return {"balance": event.data.get("balance", 0), "owner": event.data.get("owner")}
        elif event.event_type == "MoneyDeposited":
            state["balance"] = state.get("balance", 0) + event.data.get("amount", 0)
        elif event.event_type == "MoneyWithdrawn":
            state["balance"] = state.get("balance", 0) - event.data.get("amount", 0)
        return state
        
    account_state = platform.rebuild_state(account_stream.stream_id, account_reducer)
    print(f"  Account Owner: {account_state.get('owner')}")
    print(f"  Current Balance: ${account_state.get('balance', 0):.2f}")
    
    # Create snapshot
    print("\n📸 Creating Snapshot...")
    
    snapshot = platform.create_snapshot(account_stream.stream_id, account_state)
    print(f"  📸 Snapshot at version {snapshot.version}")
    
    # Display streams
    print("\n📊 Event Streams:")
    
    print("\n  ┌──────────────────────────────┬──────────┬───────────┬──────────┐")
    print("  │ Stream                       │ Events   │ Version   │ Status   │")
    print("  ├──────────────────────────────┼──────────┼───────────┼──────────┤")
    
    for stream in platform.streams.values():
        name = stream.stream_name[:28].ljust(28)
        events = str(len(stream.events))[:8].ljust(8)
        version = str(stream.current_version)[:9].ljust(9)
        status = "🟢" if stream.state == StreamState.ACTIVE else "🔴"
        
        print(f"  │ {name} │ {events} │ {version} │ {status:8s} │")
        
    print("  └──────────────────────────────┴──────────┴───────────┴──────────┘")
    
    # Event timeline
    print("\n📅 Event Timeline (Global):")
    
    all_events = platform.read_all(0, 15)
    
    for evt in all_events:
        stream = platform.streams.get(evt.stream_id)
        stream_name = stream.stream_name[:15] if stream else "unknown"
        
        print(f"  {evt.global_position:3d}. [{stream_name:15s}] {evt.event_type}")
        
    # Projection status
    print("\n📺 Projections:")
    
    print("\n  ┌─────────────────┬───────────┬───────────┬───────────┬──────────┐")
    print("  │ Projection      │ Position  │ Processed │ Checkpoint│ Status   │")
    print("  ├─────────────────┼───────────┼───────────┼───────────┼──────────┤")
    
    for proj in platform.projections.values():
        name = proj.name[:15].ljust(15)
        position = str(proj.last_position)[:9].ljust(9)
        processed = str(proj.events_processed)[:9].ljust(9)
        checkpoint = str(proj.last_checkpoint)[:9].ljust(9)
        
        status_icon = {
            ProjectionState.RUNNING: "🟢",
            ProjectionState.STOPPED: "🔴",
            ProjectionState.CATCHING_UP: "🟡",
            ProjectionState.ERROR: "❌"
        }.get(proj.state, "⚪")
        
        print(f"  │ {name} │ {position} │ {processed} │ {checkpoint} │ {status_icon:8s} │")
        
    print("  └─────────────────┴───────────┴───────────┴───────────┴──────────┘")
    
    # Event correlation
    print("\n🔗 Event Correlation:")
    
    print(f"\n  Correlation ID: {correlation_id[:8]}...")
    
    correlated = [e for e in platform.events if e.correlation_id == correlation_id]
    print(f"  Related Events: {len(correlated)}")
    
    # Statistics
    print("\n📊 Platform Statistics:")
    
    stats = platform.get_statistics()
    
    print(f"\n  Total Streams: {stats['total_streams']}")
    print(f"  Total Events: {stats['total_events']}")
    print(f"  Global Position: {stats['global_position']}")
    print(f"  Total Snapshots: {stats['total_snapshots']}")
    print(f"  Running Projections: {stats['running_projections']}/{stats['total_projections']}")
    
    # Events per stream
    print("\n  Events per Stream:")
    for stream in platform.streams.values():
        bar = "█" * len(stream.events) + "░" * (10 - len(stream.events))
        print(f"    {stream.stream_name[:20]:20s} [{bar}] {len(stream.events)}")
        
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Event Sourcing Dashboard                          │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Streams:                 {stats['total_streams']:>12}                        │")
    print(f"│ Total Events:                  {stats['total_events']:>12}                        │")
    print(f"│ Global Position:               {stats['global_position']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Active Projections:            {stats['running_projections']:>12}                        │")
    print(f"│ Total Snapshots:               {stats['total_snapshots']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Event Sourcing Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
