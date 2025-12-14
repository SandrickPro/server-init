#!/usr/bin/env python3
"""
Server Init - Iteration 184: Event Sourcing Platform
Платформа Event Sourcing

Функционал:
- Event Store - хранилище событий
- Event Streams - потоки событий
- Projections - проекции
- Snapshots - снапшоты
- Event Replay - воспроизведение событий
- Aggregate Management - управление агрегатами
- Subscriptions - подписки
- Event Versioning - версионирование событий
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, TypeVar, Generic
from enum import Enum
import uuid
import json


T = TypeVar('T')


class EventType(Enum):
    """Тип события"""
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    COMMAND = "command"
    DOMAIN = "domain"
    INTEGRATION = "integration"


class StreamState(Enum):
    """Состояние потока"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ProjectionState(Enum):
    """Состояние проекции"""
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    FAULTED = "faulted"


@dataclass
class Event:
    """Событие"""
    event_id: str
    event_type: str = ""
    
    # Stream
    stream_id: str = ""
    stream_name: str = ""
    
    # Position
    position: int = 0
    global_position: int = 0
    
    # Data
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Versioning
    schema_version: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "stream_id": self.stream_id,
            "position": self.position,
            "data": self.data,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "schema_version": self.schema_version
        }


@dataclass
class EventStream:
    """Поток событий"""
    stream_id: str
    stream_name: str = ""
    
    # Category
    category: str = ""  # e.g., "order", "user", "payment"
    
    # State
    state: StreamState = StreamState.ACTIVE
    version: int = 0
    
    # Events
    events: List[Event] = field(default_factory=list)
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    last_event_at: Optional[datetime] = None


@dataclass
class Snapshot:
    """Снапшот состояния"""
    snapshot_id: str
    stream_id: str = ""
    
    # State
    state: Dict[str, Any] = field(default_factory=dict)
    
    # Position
    version: int = 0
    event_position: int = 0
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Projection:
    """Проекция"""
    projection_id: str
    name: str = ""
    description: str = ""
    
    # State
    state: ProjectionState = ProjectionState.STOPPED
    current_position: int = 0
    
    # Filters
    event_types: List[str] = field(default_factory=list)
    stream_categories: List[str] = field(default_factory=list)
    
    # Stats
    events_processed: int = 0
    last_processed_at: Optional[datetime] = None
    
    # Handler
    handler_name: str = ""


@dataclass
class Subscription:
    """Подписка"""
    subscription_id: str
    name: str = ""
    
    # Target
    stream_id: Optional[str] = None
    category: Optional[str] = None
    
    # Position
    start_position: int = 0
    current_position: int = 0
    
    # State
    active: bool = True
    
    # Consumer
    consumer_group: str = ""


class EventStore:
    """Хранилище событий"""
    
    def __init__(self):
        self.streams: Dict[str, EventStream] = {}
        self.events: List[Event] = []
        self.global_position: int = 0
        
    async def append(self, stream_name: str, event_type: str, data: Dict, 
                    metadata: Dict = None, expected_version: int = None) -> Event:
        """Добавление события"""
        # Get or create stream
        stream_id = f"stream_{stream_name}"
        if stream_id not in self.streams:
            self.streams[stream_id] = EventStream(
                stream_id=stream_id,
                stream_name=stream_name,
                category=stream_name.split("-")[0] if "-" in stream_name else stream_name
            )
            
        stream = self.streams[stream_id]
        
        # Check expected version
        if expected_version is not None and stream.version != expected_version:
            raise ValueError(f"Expected version {expected_version}, got {stream.version}")
            
        # Create event
        self.global_position += 1
        stream.version += 1
        
        event = Event(
            event_id=f"event_{uuid.uuid4().hex[:12]}",
            event_type=event_type,
            stream_id=stream_id,
            stream_name=stream_name,
            position=stream.version,
            global_position=self.global_position,
            data=data,
            metadata=metadata or {},
            timestamp=datetime.now()
        )
        
        stream.events.append(event)
        stream.last_event_at = event.timestamp
        self.events.append(event)
        
        return event
        
    async def read_stream(self, stream_name: str, from_position: int = 0, 
                         count: int = 100) -> List[Event]:
        """Чтение потока"""
        stream_id = f"stream_{stream_name}"
        stream = self.streams.get(stream_id)
        
        if not stream:
            return []
            
        return stream.events[from_position:from_position + count]
        
    async def read_all(self, from_position: int = 0, count: int = 100) -> List[Event]:
        """Чтение всех событий"""
        return self.events[from_position:from_position + count]
        
    async def read_category(self, category: str, from_position: int = 0) -> List[Event]:
        """Чтение по категории"""
        return [
            e for e in self.events[from_position:]
            if e.stream_name.startswith(category)
        ]


class AggregateRoot(Generic[T]):
    """Корень агрегата"""
    
    def __init__(self, aggregate_id: str):
        self.aggregate_id = aggregate_id
        self.version = 0
        self._changes: List[Event] = []
        
    def apply_event(self, event: Event):
        """Применение события (override in subclass)"""
        pass
        
    def load_from_history(self, events: List[Event]):
        """Загрузка из истории"""
        for event in events:
            self.apply_event(event)
            self.version = event.position
            
    def get_uncommitted_changes(self) -> List[Event]:
        """Получение незафиксированных изменений"""
        return self._changes
        
    def mark_changes_committed(self):
        """Пометка изменений как зафиксированных"""
        self._changes.clear()


class ProjectionEngine:
    """Движок проекций"""
    
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        self.projections: Dict[str, Projection] = {}
        self.handlers: Dict[str, Callable] = {}
        self.projection_states: Dict[str, Dict[str, Any]] = {}
        
    def register_projection(self, projection: Projection, handler: Callable):
        """Регистрация проекции"""
        self.projections[projection.projection_id] = projection
        self.handlers[projection.projection_id] = handler
        self.projection_states[projection.projection_id] = {}
        
    async def run_projection(self, projection_id: str):
        """Запуск проекции"""
        projection = self.projections.get(projection_id)
        if not projection:
            return
            
        projection.state = ProjectionState.RUNNING
        handler = self.handlers.get(projection_id)
        
        events = await self.event_store.read_all(projection.current_position)
        
        for event in events:
            # Filter by event type
            if projection.event_types and event.event_type not in projection.event_types:
                continue
                
            # Filter by category
            if projection.stream_categories:
                category = event.stream_name.split("-")[0]
                if category not in projection.stream_categories:
                    continue
                    
            # Process event
            if handler:
                state = self.projection_states[projection_id]
                handler(event, state)
                
            projection.current_position = event.global_position
            projection.events_processed += 1
            projection.last_processed_at = datetime.now()
            
    def get_projection_state(self, projection_id: str) -> Dict[str, Any]:
        """Получение состояния проекции"""
        return self.projection_states.get(projection_id, {})


class SnapshotStore:
    """Хранилище снапшотов"""
    
    def __init__(self):
        self.snapshots: Dict[str, List[Snapshot]] = {}
        
    async def save(self, stream_id: str, state: Dict, version: int) -> Snapshot:
        """Сохранение снапшота"""
        snapshot = Snapshot(
            snapshot_id=f"snap_{uuid.uuid4().hex[:8]}",
            stream_id=stream_id,
            state=state,
            version=version,
            event_position=version
        )
        
        if stream_id not in self.snapshots:
            self.snapshots[stream_id] = []
        self.snapshots[stream_id].append(snapshot)
        
        return snapshot
        
    async def load(self, stream_id: str) -> Optional[Snapshot]:
        """Загрузка последнего снапшота"""
        snapshots = self.snapshots.get(stream_id, [])
        return snapshots[-1] if snapshots else None


class SubscriptionManager:
    """Менеджер подписок"""
    
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        self.subscriptions: Dict[str, Subscription] = {}
        self.handlers: Dict[str, Callable] = {}
        
    def subscribe(self, name: str, handler: Callable, stream_id: str = None,
                 category: str = None) -> Subscription:
        """Подписка на события"""
        subscription = Subscription(
            subscription_id=f"sub_{uuid.uuid4().hex[:8]}",
            name=name,
            stream_id=stream_id,
            category=category
        )
        
        self.subscriptions[subscription.subscription_id] = subscription
        self.handlers[subscription.subscription_id] = handler
        
        return subscription
        
    async def process_subscriptions(self):
        """Обработка подписок"""
        for sub_id, subscription in self.subscriptions.items():
            if not subscription.active:
                continue
                
            handler = self.handlers.get(sub_id)
            if not handler:
                continue
                
            # Get events
            if subscription.stream_id:
                events = await self.event_store.read_stream(
                    subscription.stream_id.replace("stream_", ""),
                    subscription.current_position
                )
            elif subscription.category:
                events = await self.event_store.read_category(
                    subscription.category,
                    subscription.current_position
                )
            else:
                events = await self.event_store.read_all(subscription.current_position)
                
            for event in events:
                await handler(event)
                subscription.current_position = event.global_position


class EventSourcingPlatform:
    """Платформа Event Sourcing"""
    
    def __init__(self):
        self.event_store = EventStore()
        self.snapshot_store = SnapshotStore()
        self.projection_engine = ProjectionEngine(self.event_store)
        self.subscription_manager = SubscriptionManager(self.event_store)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        return {
            "total_events": len(self.event_store.events),
            "total_streams": len(self.event_store.streams),
            "global_position": self.event_store.global_position,
            "projections": len(self.projection_engine.projections),
            "subscriptions": len(self.subscription_manager.subscriptions),
            "snapshots": sum(len(s) for s in self.snapshot_store.snapshots.values())
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 184: Event Sourcing Platform")
    print("=" * 60)
    
    async def demo():
        platform = EventSourcingPlatform()
        print("✓ Event Sourcing Platform created")
        
        # Append events
        print("\n📝 Appending Events...")
        
        # Order events
        order_id = "ORD-001"
        
        events_data = [
            ("OrderCreated", {"order_id": order_id, "customer_id": "CUST-001", "total": 150.00}),
            ("ItemAdded", {"order_id": order_id, "item_id": "ITEM-001", "quantity": 2, "price": 50.00}),
            ("ItemAdded", {"order_id": order_id, "item_id": "ITEM-002", "quantity": 1, "price": 50.00}),
            ("ShippingAddressSet", {"order_id": order_id, "address": "123 Main St", "city": "NYC"}),
            ("OrderSubmitted", {"order_id": order_id, "submitted_at": datetime.now().isoformat()}),
            ("PaymentReceived", {"order_id": order_id, "amount": 150.00, "method": "credit_card"}),
            ("OrderShipped", {"order_id": order_id, "tracking_number": "TRK-123456"}),
        ]
        
        for event_type, data in events_data:
            event = await platform.event_store.append(
                stream_name=f"order-{order_id}",
                event_type=event_type,
                data=data,
                metadata={"user_id": "admin", "correlation_id": str(uuid.uuid4())}
            )
            print(f"  ✓ {event.event_type} (position: {event.position})")
            
        # Add more orders
        for i in range(2, 5):
            order_id = f"ORD-00{i}"
            await platform.event_store.append(
                f"order-{order_id}", "OrderCreated",
                {"order_id": order_id, "customer_id": f"CUST-00{i}", "total": random.uniform(50, 500)}
            )
            await platform.event_store.append(
                f"order-{order_id}", "OrderSubmitted",
                {"order_id": order_id}
            )
            
        print(f"\n  Total events: {len(platform.event_store.events)}")
        
        # Read stream
        print("\n📖 Reading Order Stream...")
        
        events = await platform.event_store.read_stream("order-ORD-001")
        
        print(f"\n  Stream: order-ORD-001")
        print(f"  Events: {len(events)}")
        
        print("\n  ┌─────┬────────────────────────┬────────────────────────────────────────────────┐")
        print("  │ Pos │ Event Type             │ Data                                           │")
        print("  ├─────┼────────────────────────┼────────────────────────────────────────────────┤")
        
        for event in events:
            pos = str(event.position).rjust(3)
            etype = event.event_type[:22].ljust(22)
            data = str(event.data)[:46].ljust(46)
            print(f"  │ {pos} │ {etype} │ {data} │")
            
        print("  └─────┴────────────────────────┴────────────────────────────────────────────────┘")
        
        # Create projection
        print("\n📊 Creating Projections...")
        
        # Order summary projection
        def order_summary_handler(event: Event, state: Dict):
            if event.event_type == "OrderCreated":
                order_id = event.data.get("order_id")
                state[order_id] = {
                    "order_id": order_id,
                    "customer_id": event.data.get("customer_id"),
                    "total": event.data.get("total"),
                    "status": "created",
                    "items": []
                }
            elif event.event_type == "ItemAdded":
                order_id = event.data.get("order_id")
                if order_id in state:
                    state[order_id]["items"].append({
                        "item_id": event.data.get("item_id"),
                        "quantity": event.data.get("quantity")
                    })
            elif event.event_type == "OrderSubmitted":
                order_id = event.data.get("order_id")
                if order_id in state:
                    state[order_id]["status"] = "submitted"
            elif event.event_type == "OrderShipped":
                order_id = event.data.get("order_id")
                if order_id in state:
                    state[order_id]["status"] = "shipped"
                    state[order_id]["tracking"] = event.data.get("tracking_number")
                    
        order_projection = Projection(
            projection_id="order_summary",
            name="Order Summary",
            event_types=["OrderCreated", "ItemAdded", "OrderSubmitted", "OrderShipped"],
            stream_categories=["order"]
        )
        
        platform.projection_engine.register_projection(order_projection, order_summary_handler)
        print(f"  ✓ Registered: {order_projection.name}")
        
        # Run projection
        await platform.projection_engine.run_projection("order_summary")
        
        # Get projection state
        order_state = platform.projection_engine.get_projection_state("order_summary")
        
        print(f"\n  Projection State:")
        print(f"  Events processed: {order_projection.events_processed}")
        print(f"  Orders tracked: {len(order_state)}")
        
        print("\n  Order Status:")
        for order_id, order in order_state.items():
            print(f"    • {order_id}: {order['status']} (${order['total']:.2f})")
            
        # Create snapshot
        print("\n📸 Creating Snapshot...")
        
        snapshot = await platform.snapshot_store.save(
            "stream_order-ORD-001",
            order_state.get("ORD-001", {}),
            7  # version
        )
        
        print(f"  ✓ Snapshot created at version {snapshot.version}")
        print(f"  State: {snapshot.state}")
        
        # Create subscription
        print("\n🔔 Creating Subscriptions...")
        
        received_events = []
        
        async def order_handler(event: Event):
            received_events.append(event)
            
        subscription = platform.subscription_manager.subscribe(
            "order_notifications",
            order_handler,
            category="order"
        )
        
        print(f"  ✓ Subscription: {subscription.name}")
        
        # Process subscriptions
        await platform.subscription_manager.process_subscriptions()
        
        print(f"  Events received: {len(received_events)}")
        
        # Read all events
        print("\n📜 Global Event Log:")
        
        all_events = await platform.event_store.read_all()
        
        print(f"\n  Total events: {len(all_events)}")
        
        print("\n  ┌─────────┬────────────────────────┬─────────────────────────┬──────────────────────┐")
        print("  │ Global  │ Event Type             │ Stream                  │ Timestamp            │")
        print("  ├─────────┼────────────────────────┼─────────────────────────┼──────────────────────┤")
        
        for event in all_events[:10]:
            gpos = str(event.global_position).rjust(7)
            etype = event.event_type[:22].ljust(22)
            stream = event.stream_name[:23].ljust(23)
            ts = event.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            print(f"  │ {gpos} │ {etype} │ {stream} │ {ts} │")
            
        print("  └─────────┴────────────────────────┴─────────────────────────┴──────────────────────┘")
        
        # Event replay
        print("\n🔄 Event Replay (Rebuilding State)...")
        
        # Rebuild order state from events
        rebuilt_state = {}
        events = await platform.event_store.read_stream("order-ORD-001")
        
        for event in events:
            order_summary_handler(event, rebuilt_state)
            
        print(f"  Rebuilt state for ORD-001:")
        print(f"    Status: {rebuilt_state.get('ORD-001', {}).get('status')}")
        print(f"    Items: {len(rebuilt_state.get('ORD-001', {}).get('items', []))}")
        print(f"    Tracking: {rebuilt_state.get('ORD-001', {}).get('tracking')}")
        
        # Stream statistics
        print("\n📊 Stream Statistics:")
        
        print("\n  ┌─────────────────────────────┬──────────┬────────────────────────┐")
        print("  │ Stream                      │ Events   │ Last Event             │")
        print("  ├─────────────────────────────┼──────────┼────────────────────────┤")
        
        for stream_id, stream in platform.event_store.streams.items():
            name = stream.stream_name[:27].ljust(27)
            count = str(len(stream.events)).rjust(8)
            last = stream.last_event_at.strftime("%Y-%m-%d %H:%M") if stream.last_event_at else "N/A"
            print(f"  │ {name} │ {count} │ {last:>22} │")
            
        print("  └─────────────────────────────┴──────────┴────────────────────────┘")
        
        # Platform statistics
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Events: {stats['total_events']}")
        print(f"  Total Streams: {stats['total_streams']}")
        print(f"  Global Position: {stats['global_position']}")
        print(f"  Projections: {stats['projections']}")
        print(f"  Subscriptions: {stats['subscriptions']}")
        print(f"  Snapshots: {stats['snapshots']}")
        
        # Dashboard
        print("\n┌────────────────────────────────────────────────────────────────────┐")
        print("│                    Event Sourcing Dashboard                        │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Total Events:                  {stats['total_events']:>10}                     │")
        print(f"│ Total Streams:                 {stats['total_streams']:>10}                     │")
        print(f"│ Global Position:               {stats['global_position']:>10}                     │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Active Projections:            {stats['projections']:>10}                     │")
        print(f"│ Active Subscriptions:          {stats['subscriptions']:>10}                     │")
        print(f"│ Snapshots Stored:              {stats['snapshots']:>10}                     │")
        print("└────────────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Event Sourcing Platform initialized!")
    print("=" * 60)
