#!/usr/bin/env python3
"""
Server Init - Iteration 120: Event Sourcing Platform
Платформа событийной архитектуры

Функционал:
- Event Store - хранилище событий
- Event Publishing - публикация событий
- Event Replay - воспроизведение событий
- Projections - проекции
- Snapshots - снапшоты
- Aggregates - агрегаты
- Event Handlers - обработчики событий
- CQRS Support - поддержка CQRS
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Type
from enum import Enum
from collections import defaultdict
import uuid
import random
import hashlib


class EventType(Enum):
    """Тип события"""
    DOMAIN = "domain"
    INTEGRATION = "integration"
    COMMAND = "command"
    NOTIFICATION = "notification"
    SYSTEM = "system"


class AggregateStatus(Enum):
    """Статус агрегата"""
    ACTIVE = "active"
    DELETED = "deleted"
    ARCHIVED = "archived"


class ProjectionStatus(Enum):
    """Статус проекции"""
    RUNNING = "running"
    STOPPED = "stopped"
    REBUILDING = "rebuilding"
    ERROR = "error"


@dataclass
class Event:
    """Событие"""
    event_id: str
    event_type: str = ""
    
    # Stream
    stream_id: str = ""
    stream_type: str = ""
    
    # Sequence
    sequence_number: int = 0
    global_position: int = 0
    
    # Payload
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Correlation
    correlation_id: str = ""
    causation_id: str = ""


@dataclass
class EventStream:
    """Поток событий"""
    stream_id: str
    stream_type: str = ""
    
    # Events
    events: List[Event] = field(default_factory=list)
    
    # Version
    version: int = 0
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Snapshot:
    """Снапшот"""
    snapshot_id: str
    stream_id: str = ""
    
    # State
    state: Dict[str, Any] = field(default_factory=dict)
    
    # Version
    version: int = 0
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Projection:
    """Проекция"""
    projection_id: str
    name: str = ""
    
    # Handler
    event_types: List[str] = field(default_factory=list)
    
    # State
    state: Dict[str, Any] = field(default_factory=dict)
    
    # Position
    last_position: int = 0
    
    # Status
    status: ProjectionStatus = ProjectionStatus.STOPPED
    
    # Stats
    events_processed: int = 0
    last_processed_at: Optional[datetime] = None


@dataclass
class Aggregate:
    """Агрегат"""
    aggregate_id: str
    aggregate_type: str = ""
    
    # State
    state: Dict[str, Any] = field(default_factory=dict)
    status: AggregateStatus = AggregateStatus.ACTIVE
    
    # Version
    version: int = 0
    
    # Events
    uncommitted_events: List[Event] = field(default_factory=list)


@dataclass
class Subscription:
    """Подписка"""
    subscription_id: str
    name: str = ""
    
    # Filter
    event_types: List[str] = field(default_factory=list)
    stream_types: List[str] = field(default_factory=list)
    
    # Position
    from_position: int = 0
    current_position: int = 0
    
    # Handler
    handler_name: str = ""
    
    # Status
    active: bool = True
    
    # Stats
    events_received: int = 0


class EventStore:
    """Хранилище событий"""
    
    def __init__(self):
        self.streams: Dict[str, EventStream] = {}
        self.all_events: List[Event] = []
        self.global_position: int = 0
        
    def append(self, stream_id: str, stream_type: str,
                event_type: str, data: Dict[str, Any],
                metadata: Dict[str, Any] = None) -> Event:
        """Добавление события"""
        # Get or create stream
        if stream_id not in self.streams:
            self.streams[stream_id] = EventStream(
                stream_id=stream_id,
                stream_type=stream_type
            )
            
        stream = self.streams[stream_id]
        stream.version += 1
        self.global_position += 1
        
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            event_type=event_type,
            stream_id=stream_id,
            stream_type=stream_type,
            sequence_number=stream.version,
            global_position=self.global_position,
            data=data,
            metadata=metadata or {},
            correlation_id=str(uuid.uuid4())
        )
        
        stream.events.append(event)
        stream.updated_at = datetime.now()
        
        self.all_events.append(event)
        
        return event
        
    def read_stream(self, stream_id: str,
                     from_version: int = 0,
                     to_version: int = None) -> List[Event]:
        """Чтение потока"""
        stream = self.streams.get(stream_id)
        if not stream:
            return []
            
        events = stream.events[from_version:]
        if to_version:
            events = events[:to_version - from_version]
            
        return events
        
    def read_all(self, from_position: int = 0,
                  count: int = 100) -> List[Event]:
        """Чтение всех событий"""
        return self.all_events[from_position:from_position + count]
        
    def get_stream_version(self, stream_id: str) -> int:
        """Версия потока"""
        stream = self.streams.get(stream_id)
        return stream.version if stream else 0


class SnapshotStore:
    """Хранилище снапшотов"""
    
    def __init__(self):
        self.snapshots: Dict[str, List[Snapshot]] = defaultdict(list)
        
    def save(self, stream_id: str, state: Dict[str, Any],
              version: int) -> Snapshot:
        """Сохранение снапшота"""
        snapshot = Snapshot(
            snapshot_id=f"snap_{uuid.uuid4().hex[:8]}",
            stream_id=stream_id,
            state=state,
            version=version
        )
        
        self.snapshots[stream_id].append(snapshot)
        return snapshot
        
    def get_latest(self, stream_id: str) -> Optional[Snapshot]:
        """Последний снапшот"""
        snapshots = self.snapshots.get(stream_id, [])
        return snapshots[-1] if snapshots else None


class AggregateRepository:
    """Репозиторий агрегатов"""
    
    def __init__(self, event_store: EventStore, snapshot_store: SnapshotStore):
        self.event_store = event_store
        self.snapshot_store = snapshot_store
        self.aggregates: Dict[str, Aggregate] = {}
        
    def load(self, aggregate_id: str, aggregate_type: str) -> Aggregate:
        """Загрузка агрегата"""
        # Try cache
        if aggregate_id in self.aggregates:
            return self.aggregates[aggregate_id]
            
        # Create aggregate
        aggregate = Aggregate(
            aggregate_id=aggregate_id,
            aggregate_type=aggregate_type
        )
        
        # Load from snapshot
        snapshot = self.snapshot_store.get_latest(aggregate_id)
        if snapshot:
            aggregate.state = snapshot.state.copy()
            aggregate.version = snapshot.version
            
        # Apply events since snapshot
        events = self.event_store.read_stream(
            aggregate_id,
            from_version=aggregate.version
        )
        
        for event in events:
            self._apply_event(aggregate, event)
            
        self.aggregates[aggregate_id] = aggregate
        return aggregate
        
    def save(self, aggregate: Aggregate):
        """Сохранение агрегата"""
        # Append uncommitted events
        for event in aggregate.uncommitted_events:
            self.event_store.append(
                aggregate.aggregate_id,
                aggregate.aggregate_type,
                event.event_type,
                event.data,
                event.metadata
            )
            
        aggregate.uncommitted_events.clear()
        
        # Create snapshot if needed
        if aggregate.version > 0 and aggregate.version % 10 == 0:
            self.snapshot_store.save(
                aggregate.aggregate_id,
                aggregate.state,
                aggregate.version
            )
            
    def _apply_event(self, aggregate: Aggregate, event: Event):
        """Применение события"""
        aggregate.version += 1
        # State would be updated based on event type
        aggregate.state["last_event"] = event.event_type
        aggregate.state["last_updated"] = datetime.now().isoformat()


class ProjectionManager:
    """Менеджер проекций"""
    
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        self.projections: Dict[str, Projection] = {}
        self.handlers: Dict[str, Callable] = {}
        
    def create_projection(self, name: str,
                           event_types: List[str]) -> Projection:
        """Создание проекции"""
        projection = Projection(
            projection_id=f"proj_{uuid.uuid4().hex[:8]}",
            name=name,
            event_types=event_types
        )
        
        self.projections[projection.projection_id] = projection
        return projection
        
    def register_handler(self, projection_id: str, handler: Callable):
        """Регистрация обработчика"""
        self.handlers[projection_id] = handler
        
    async def run_projection(self, projection_id: str,
                              batch_size: int = 100):
        """Запуск проекции"""
        projection = self.projections.get(projection_id)
        if not projection:
            return
            
        projection.status = ProjectionStatus.RUNNING
        handler = self.handlers.get(projection_id)
        
        while True:
            events = self.event_store.read_all(
                projection.last_position, batch_size
            )
            
            if not events:
                break
                
            for event in events:
                if event.event_type in projection.event_types or not projection.event_types:
                    if handler:
                        await handler(projection, event)
                    projection.events_processed += 1
                    
                projection.last_position = event.global_position
                
            projection.last_processed_at = datetime.now()
            
        projection.status = ProjectionStatus.STOPPED
        
    async def rebuild_projection(self, projection_id: str):
        """Перестроение проекции"""
        projection = self.projections.get(projection_id)
        if not projection:
            return
            
        projection.status = ProjectionStatus.REBUILDING
        projection.state = {}
        projection.last_position = 0
        projection.events_processed = 0
        
        await self.run_projection(projection_id)


class SubscriptionManager:
    """Менеджер подписок"""
    
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        self.subscriptions: Dict[str, Subscription] = {}
        self.handlers: Dict[str, Callable] = {}
        
    def subscribe(self, name: str, event_types: List[str] = None,
                   from_position: int = 0) -> Subscription:
        """Создание подписки"""
        subscription = Subscription(
            subscription_id=f"sub_{uuid.uuid4().hex[:8]}",
            name=name,
            event_types=event_types or [],
            from_position=from_position,
            current_position=from_position
        )
        
        self.subscriptions[subscription.subscription_id] = subscription
        return subscription
        
    def register_handler(self, subscription_id: str, handler: Callable):
        """Регистрация обработчика"""
        self.handlers[subscription_id] = handler
        
    async def process(self, subscription_id: str):
        """Обработка подписки"""
        subscription = self.subscriptions.get(subscription_id)
        if not subscription or not subscription.active:
            return
            
        handler = self.handlers.get(subscription_id)
        
        events = self.event_store.read_all(
            subscription.current_position, 100
        )
        
        for event in events:
            if subscription.event_types and event.event_type not in subscription.event_types:
                continue
                
            if handler:
                await handler(event)
                
            subscription.events_received += 1
            subscription.current_position = event.global_position


class EventSourcingPlatform:
    """Платформа событийной архитектуры"""
    
    def __init__(self):
        self.event_store = EventStore()
        self.snapshot_store = SnapshotStore()
        self.aggregate_repo = AggregateRepository(
            self.event_store, self.snapshot_store
        )
        self.projection_manager = ProjectionManager(self.event_store)
        self.subscription_manager = SubscriptionManager(self.event_store)
        
    def publish(self, stream_id: str, stream_type: str,
                 event_type: str, data: Dict[str, Any]) -> Event:
        """Публикация события"""
        return self.event_store.append(
            stream_id, stream_type, event_type, data
        )
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        return {
            "total_streams": len(self.event_store.streams),
            "total_events": len(self.event_store.all_events),
            "global_position": self.event_store.global_position,
            "snapshots": sum(len(s) for s in self.snapshot_store.snapshots.values()),
            "projections": len(self.projection_manager.projections),
            "subscriptions": len(self.subscription_manager.subscriptions)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 120: Event Sourcing Platform")
    print("=" * 60)
    
    async def demo():
        platform = EventSourcingPlatform()
        print("✓ Event Sourcing Platform created")
        
        # Generate events for different domains
        print("\n📝 Generating Domain Events...")
        
        # User domain events
        users = ["user_001", "user_002", "user_003"]
        user_events = [
            ("UserRegistered", {"email": "user@example.com", "name": "John"}),
            ("ProfileUpdated", {"field": "name", "value": "John Doe"}),
            ("PasswordChanged", {"changed_by": "user"}),
            ("EmailVerified", {"verified": True}),
            ("LoginSucceeded", {"ip": "192.168.1.1"}),
        ]
        
        for user_id in users:
            for event_type, data in random.sample(user_events, 3):
                platform.publish(
                    user_id, "User",
                    event_type, {**data, "timestamp": datetime.now().isoformat()}
                )
                
        print(f"  ✓ User events: {len(users) * 3}")
        
        # Order domain events
        orders = ["order_001", "order_002", "order_003", "order_004"]
        order_events = [
            ("OrderCreated", {"total": 99.99, "items": 3}),
            ("PaymentReceived", {"amount": 99.99, "method": "card"}),
            ("OrderConfirmed", {"confirmed_by": "system"}),
            ("OrderShipped", {"tracking": "TRACK123"}),
            ("OrderDelivered", {"signed_by": "recipient"}),
        ]
        
        for order_id in orders:
            for event_type, data in order_events[:random.randint(2, 5)]:
                platform.publish(
                    order_id, "Order",
                    event_type, {**data, "order_id": order_id}
                )
                
        print(f"  ✓ Order events: ~{len(orders) * 3}")
        
        # Product domain events
        products = ["prod_001", "prod_002"]
        product_events = [
            ("ProductCreated", {"name": "Widget", "price": 29.99}),
            ("PriceChanged", {"old": 29.99, "new": 24.99}),
            ("StockUpdated", {"quantity": 100}),
            ("ProductDiscontinued", {"reason": "obsolete"}),
        ]
        
        for product_id in products:
            for event_type, data in random.sample(product_events, 2):
                platform.publish(
                    product_id, "Product",
                    event_type, data
                )
                
        print(f"  ✓ Product events: {len(products) * 2}")
        
        # Show event streams
        print("\n📊 Event Streams:")
        
        streams_by_type = defaultdict(list)
        for stream in platform.event_store.streams.values():
            streams_by_type[stream.stream_type].append(stream)
            
        for stream_type, streams in streams_by_type.items():
            total_events = sum(s.version for s in streams)
            print(f"  {stream_type}: {len(streams)} streams, {total_events} events")
            
        # Event timeline
        print("\n📜 Recent Events:")
        
        for event in platform.event_store.all_events[-10:]:
            time_str = event.timestamp.strftime("%H:%M:%S.%f")[:-3]
            print(f"  [{time_str}] {event.stream_type}/{event.stream_id}: {event.event_type}")
            
        # Create projections
        print("\n🔮 Creating Projections...")
        
        # User count projection
        user_count_proj = platform.projection_manager.create_projection(
            "UserCountByStatus",
            ["UserRegistered", "UserDeleted", "EmailVerified"]
        )
        
        async def user_count_handler(projection: Projection, event: Event):
            if event.event_type == "UserRegistered":
                projection.state["total"] = projection.state.get("total", 0) + 1
                projection.state["unverified"] = projection.state.get("unverified", 0) + 1
            elif event.event_type == "EmailVerified":
                projection.state["unverified"] = projection.state.get("unverified", 0) - 1
                projection.state["verified"] = projection.state.get("verified", 0) + 1
                
        platform.projection_manager.register_handler(
            user_count_proj.projection_id, user_count_handler
        )
        print(f"  ✓ UserCountByStatus projection")
        
        # Order summary projection
        order_summary_proj = platform.projection_manager.create_projection(
            "OrderSummary",
            ["OrderCreated", "PaymentReceived", "OrderDelivered"]
        )
        
        async def order_summary_handler(projection: Projection, event: Event):
            if event.event_type == "OrderCreated":
                projection.state["total_orders"] = projection.state.get("total_orders", 0) + 1
                projection.state["total_amount"] = projection.state.get("total_amount", 0) + event.data.get("total", 0)
            elif event.event_type == "OrderDelivered":
                projection.state["delivered"] = projection.state.get("delivered", 0) + 1
                
        platform.projection_manager.register_handler(
            order_summary_proj.projection_id, order_summary_handler
        )
        print(f"  ✓ OrderSummary projection")
        
        # Run projections
        print("\n🔄 Running Projections...")
        
        await platform.projection_manager.run_projection(user_count_proj.projection_id)
        await platform.projection_manager.run_projection(order_summary_proj.projection_id)
        
        print(f"  ✓ UserCountByStatus: {user_count_proj.events_processed} events")
        print(f"    State: {user_count_proj.state}")
        
        print(f"  ✓ OrderSummary: {order_summary_proj.events_processed} events")
        print(f"    State: {order_summary_proj.state}")
        
        # Create subscriptions
        print("\n📬 Creating Subscriptions...")
        
        sub_orders = platform.subscription_manager.subscribe(
            "OrderNotifications",
            ["OrderCreated", "OrderShipped", "OrderDelivered"]
        )
        
        events_received = []
        async def order_handler(event: Event):
            events_received.append(event)
            
        platform.subscription_manager.register_handler(
            sub_orders.subscription_id, order_handler
        )
        
        await platform.subscription_manager.process(sub_orders.subscription_id)
        
        print(f"  ✓ OrderNotifications: {sub_orders.events_received} events received")
        
        # Load aggregates
        print("\n🏗️ Loading Aggregates...")
        
        for user_id in users[:2]:
            aggregate = platform.aggregate_repo.load(user_id, "User")
            print(f"  {user_id}: v{aggregate.version}, state={aggregate.state}")
            
        # Create snapshots
        print("\n📸 Creating Snapshots...")
        
        for user_id in users[:2]:
            aggregate = platform.aggregate_repo.load(user_id, "User")
            snapshot = platform.snapshot_store.save(
                user_id,
                aggregate.state,
                aggregate.version
            )
            print(f"  ✓ {user_id}: snapshot at v{snapshot.version}")
            
        # Read stream
        print("\n📖 Reading Stream (order_001):")
        
        events = platform.event_store.read_stream("order_001")
        for event in events[:5]:
            print(f"  v{event.sequence_number}: {event.event_type}")
            
        # Event type distribution
        print("\n📊 Event Type Distribution:")
        
        event_counts = defaultdict(int)
        for event in platform.event_store.all_events:
            event_counts[event.event_type] += 1
            
        for event_type, count in sorted(event_counts.items(), key=lambda x: -x[1])[:10]:
            bar = "█" * (count // 2 + 1)
            print(f"  {event_type:20}: {bar} ({count})")
            
        # Statistics
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Event Store:")
        print(f"    Streams: {stats['total_streams']}")
        print(f"    Events: {stats['total_events']}")
        print(f"    Global Position: {stats['global_position']}")
        
        print(f"\n  Snapshots: {stats['snapshots']}")
        print(f"  Projections: {stats['projections']}")
        print(f"  Subscriptions: {stats['subscriptions']}")
        
        # Stream details
        print("\n📋 Stream Details:")
        
        for stream_id, stream in list(platform.event_store.streams.items())[:5]:
            print(f"  {stream.stream_type}/{stream_id}: v{stream.version}")
            
        # Dashboard
        print("\n📋 Event Sourcing Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │               Event Sourcing Overview                       │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Event Streams:        {stats['total_streams']:>10}                      │")
        print(f"  │ Total Events:         {stats['total_events']:>10}                      │")
        print(f"  │ Global Position:      {stats['global_position']:>10}                      │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Snapshots:            {stats['snapshots']:>10}                      │")
        print(f"  │ Projections:          {stats['projections']:>10}                      │")
        print(f"  │ Subscriptions:        {stats['subscriptions']:>10}                      │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ User Streams:         {len([s for s in platform.event_store.streams.values() if s.stream_type == 'User']):>10}                      │")
        print(f"  │ Order Streams:        {len([s for s in platform.event_store.streams.values() if s.stream_type == 'Order']):>10}                      │")
        print(f"  │ Product Streams:      {len([s for s in platform.event_store.streams.values() if s.stream_type == 'Product']):>10}                      │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Event Sourcing Platform initialized!")
    print("=" * 60)
