#!/usr/bin/env python3
"""
Server Init - Iteration 88: Event-Driven Architecture Platform
Платформа событийно-ориентированной архитектуры

Функционал:
- Event Bus - шина событий
- Event Sourcing - источники событий
- Event Schema Registry - реестр схем событий
- Event Routing - маршрутизация событий
- Event Replay - воспроизведение событий
- Dead Letter Queue - очередь недоставленных событий
- Event Monitoring - мониторинг событий
- CQRS Support - поддержка CQRS
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Tuple, Awaitable
from enum import Enum
from collections import defaultdict
import uuid
import random
import hashlib


class EventPriority(Enum):
    """Приоритет события"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class EventStatus(Enum):
    """Статус события"""
    PENDING = "pending"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


class DeliveryGuarantee(Enum):
    """Гарантия доставки"""
    AT_MOST_ONCE = "at_most_once"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"


@dataclass
class EventMetadata:
    """Метаданные события"""
    event_id: str = ""
    correlation_id: str = ""
    causation_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    version: str = "1.0"
    content_type: str = "application/json"
    priority: EventPriority = EventPriority.NORMAL
    ttl_seconds: int = 0  # 0 = no expiry
    trace_id: str = ""
    
    # Retry информация
    retry_count: int = 0
    max_retries: int = 3
    
    # Custom headers
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class Event:
    """Событие"""
    event_type: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: EventMetadata = field(default_factory=EventMetadata)
    
    # Статус
    status: EventStatus = EventStatus.PENDING
    
    # Время обработки
    processed_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.metadata.event_id:
            self.metadata.event_id = f"evt_{uuid.uuid4().hex}"
        if not self.metadata.timestamp:
            self.metadata.timestamp = datetime.now()


@dataclass
class EventSchema:
    """Схема события"""
    schema_id: str
    event_type: str = ""
    version: str = "1.0"
    
    # JSON Schema
    schema_definition: Dict[str, Any] = field(default_factory=dict)
    
    # Примеры
    examples: List[Dict[str, Any]] = field(default_factory=list)
    
    # Документация
    description: str = ""
    deprecated: bool = False
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Subscription:
    """Подписка на события"""
    subscription_id: str
    subscriber_name: str = ""
    
    # Фильтр событий
    event_types: List[str] = field(default_factory=list)  # ["order.*", "user.created"]
    filter_expression: str = ""  # JSONPath или подобное
    
    # Handler
    endpoint: str = ""  # URL или имя функции
    
    # Настройки
    delivery_guarantee: DeliveryGuarantee = DeliveryGuarantee.AT_LEAST_ONCE
    batch_size: int = 1
    timeout_ms: int = 5000
    
    # Статус
    is_active: bool = True
    
    # Статистика
    events_received: int = 0
    events_processed: int = 0
    events_failed: int = 0
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class EventStore:
    """Хранилище событий"""
    events: List[Event] = field(default_factory=list)
    streams: Dict[str, List[str]] = field(default_factory=dict)  # stream_id -> [event_ids]
    
    def append(self, stream_id: str, event: Event) -> int:
        """Добавление события в поток"""
        self.events.append(event)
        
        if stream_id not in self.streams:
            self.streams[stream_id] = []
        self.streams[stream_id].append(event.metadata.event_id)
        
        return len(self.streams[stream_id]) - 1  # Версия события
        
    def get_stream(self, stream_id: str, from_version: int = 0) -> List[Event]:
        """Получение событий потока"""
        event_ids = self.streams.get(stream_id, [])[from_version:]
        
        events_by_id = {e.metadata.event_id: e for e in self.events}
        return [events_by_id[eid] for eid in event_ids if eid in events_by_id]
        
    def get_all_events(self, from_position: int = 0) -> List[Event]:
        """Получение всех событий"""
        return self.events[from_position:]


@dataclass 
class DeadLetterEntry:
    """Запись в очереди недоставленных"""
    entry_id: str
    event: Event = None
    subscription_id: str = ""
    
    # Информация об ошибке
    error_message: str = ""
    error_type: str = ""
    
    # Количество попыток
    attempt_count: int = 0
    
    # Время
    failed_at: datetime = field(default_factory=datetime.now)
    
    # Статус обработки
    resolved: bool = False
    resolved_at: Optional[datetime] = None


# Тип хэндлера событий
EventHandler = Callable[[Event], Awaitable[bool]]


class EventRouter:
    """Маршрутизатор событий"""
    
    def __init__(self):
        self.routes: Dict[str, List[str]] = defaultdict(list)  # pattern -> [subscription_ids]
        
    def add_route(self, pattern: str, subscription_id: str):
        """Добавление маршрута"""
        self.routes[pattern].append(subscription_id)
        
    def remove_route(self, pattern: str, subscription_id: str):
        """Удаление маршрута"""
        if pattern in self.routes:
            self.routes[pattern] = [s for s in self.routes[pattern] if s != subscription_id]
            
    def match(self, event_type: str) -> List[str]:
        """Поиск подписок для типа события"""
        matched = []
        
        for pattern, subscription_ids in self.routes.items():
            if self._matches_pattern(event_type, pattern):
                matched.extend(subscription_ids)
                
        return list(set(matched))  # Уникальные
        
    def _matches_pattern(self, event_type: str, pattern: str) -> bool:
        """Проверка соответствия паттерну"""
        if pattern == "*":
            return True
        if pattern == event_type:
            return True
        if pattern.endswith(".*"):
            prefix = pattern[:-2]
            return event_type.startswith(prefix + ".")
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            return event_type.startswith(prefix)
        return False


class SchemaRegistry:
    """Реестр схем событий"""
    
    def __init__(self):
        self.schemas: Dict[str, Dict[str, EventSchema]] = {}  # event_type -> version -> schema
        
    def register(self, event_type: str, schema_def: Dict[str, Any], 
                  version: str = "1.0", **kwargs) -> EventSchema:
        """Регистрация схемы"""
        schema = EventSchema(
            schema_id=f"schema_{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            version=version,
            schema_definition=schema_def,
            **kwargs
        )
        
        if event_type not in self.schemas:
            self.schemas[event_type] = {}
        self.schemas[event_type][version] = schema
        
        return schema
        
    def get(self, event_type: str, version: str = None) -> Optional[EventSchema]:
        """Получение схемы"""
        if event_type not in self.schemas:
            return None
            
        versions = self.schemas[event_type]
        
        if version:
            return versions.get(version)
        else:
            # Возвращаем последнюю версию
            if versions:
                latest_version = max(versions.keys())
                return versions[latest_version]
        return None
        
    def validate(self, event: Event) -> Tuple[bool, List[str]]:
        """Валидация события по схеме"""
        schema = self.get(event.event_type, event.metadata.version)
        
        if not schema:
            return True, []  # Нет схемы - пропускаем валидацию
            
        errors = []
        schema_def = schema.schema_definition
        
        # Упрощённая валидация
        required = schema_def.get("required", [])
        properties = schema_def.get("properties", {})
        
        for field in required:
            if field not in event.payload:
                errors.append(f"Missing required field: {field}")
                
        for field, value in event.payload.items():
            if field in properties:
                expected_type = properties[field].get("type")
                actual_type = type(value).__name__
                
                type_map = {"string": "str", "integer": "int", "number": "float", "boolean": "bool", "object": "dict", "array": "list"}
                
                if expected_type and type_map.get(expected_type) != actual_type:
                    if not (expected_type == "number" and actual_type == "int"):
                        errors.append(f"Field {field}: expected {expected_type}, got {actual_type}")
                        
        return len(errors) == 0, errors


class DeadLetterQueue:
    """Очередь недоставленных событий"""
    
    def __init__(self):
        self.entries: List[DeadLetterEntry] = []
        
    def add(self, event: Event, subscription_id: str, error_message: str, error_type: str = "") -> DeadLetterEntry:
        """Добавление в DLQ"""
        entry = DeadLetterEntry(
            entry_id=f"dlq_{uuid.uuid4().hex[:8]}",
            event=event,
            subscription_id=subscription_id,
            error_message=error_message,
            error_type=error_type,
            attempt_count=event.metadata.retry_count
        )
        self.entries.append(entry)
        return entry
        
    def get_pending(self) -> List[DeadLetterEntry]:
        """Получение необработанных записей"""
        return [e for e in self.entries if not e.resolved]
        
    def resolve(self, entry_id: str):
        """Пометка как обработанная"""
        for entry in self.entries:
            if entry.entry_id == entry_id:
                entry.resolved = True
                entry.resolved_at = datetime.now()
                break


class EventBus:
    """Шина событий"""
    
    def __init__(self):
        self.subscriptions: Dict[str, Subscription] = {}
        self.handlers: Dict[str, EventHandler] = {}
        self.router = EventRouter()
        self.event_store = EventStore()
        self.schema_registry = SchemaRegistry()
        self.dlq = DeadLetterQueue()
        
        # Статистика
        self.stats = {
            "events_published": 0,
            "events_delivered": 0,
            "events_failed": 0
        }
        
    def subscribe(self, subscriber_name: str, event_types: List[str],
                   handler: EventHandler, **kwargs) -> Subscription:
        """Подписка на события"""
        subscription = Subscription(
            subscription_id=f"sub_{uuid.uuid4().hex[:8]}",
            subscriber_name=subscriber_name,
            event_types=event_types,
            **kwargs
        )
        
        self.subscriptions[subscription.subscription_id] = subscription
        self.handlers[subscription.subscription_id] = handler
        
        # Регистрируем маршруты
        for event_type in event_types:
            self.router.add_route(event_type, subscription.subscription_id)
            
        return subscription
        
    def unsubscribe(self, subscription_id: str):
        """Отмена подписки"""
        subscription = self.subscriptions.get(subscription_id)
        
        if subscription:
            for event_type in subscription.event_types:
                self.router.remove_route(event_type, subscription_id)
            del self.subscriptions[subscription_id]
            if subscription_id in self.handlers:
                del self.handlers[subscription_id]
                
    async def publish(self, event_type: str, payload: Dict[str, Any],
                       correlation_id: str = None, source: str = "",
                       stream_id: str = None, **kwargs) -> Event:
        """Публикация события"""
        metadata = EventMetadata(
            correlation_id=correlation_id or f"corr_{uuid.uuid4().hex[:8]}",
            source=source,
            **kwargs
        )
        
        event = Event(
            event_type=event_type,
            payload=payload,
            metadata=metadata
        )
        
        # Валидация по схеме
        valid, errors = self.schema_registry.validate(event)
        if not valid:
            raise ValueError(f"Schema validation failed: {errors}")
            
        # Сохраняем в event store
        if stream_id:
            self.event_store.append(stream_id, event)
        else:
            self.event_store.events.append(event)
            
        self.stats["events_published"] += 1
        
        # Находим подписчиков
        subscription_ids = self.router.match(event_type)
        
        # Доставляем
        for sub_id in subscription_ids:
            subscription = self.subscriptions.get(sub_id)
            handler = self.handlers.get(sub_id)
            
            if subscription and handler and subscription.is_active:
                await self._deliver(event, subscription, handler)
                
        return event
        
    async def _deliver(self, event: Event, subscription: Subscription, handler: EventHandler):
        """Доставка события подписчику"""
        subscription.events_received += 1
        
        try:
            event.status = EventStatus.PROCESSING
            
            success = await handler(event)
            
            if success:
                event.status = EventStatus.DELIVERED
                event.delivered_at = datetime.now()
                subscription.events_processed += 1
                self.stats["events_delivered"] += 1
            else:
                raise Exception("Handler returned False")
                
        except Exception as e:
            event.metadata.retry_count += 1
            subscription.events_failed += 1
            
            if event.metadata.retry_count >= event.metadata.max_retries:
                event.status = EventStatus.DEAD_LETTER
                self.dlq.add(event, subscription.subscription_id, str(e), type(e).__name__)
                self.stats["events_failed"] += 1
            else:
                event.status = EventStatus.FAILED
                # В реальной системе здесь был бы retry с backoff
                
    async def replay(self, stream_id: str, from_version: int = 0,
                      subscription_id: str = None) -> int:
        """Воспроизведение событий"""
        events = self.event_store.get_stream(stream_id, from_version)
        
        replayed = 0
        
        for event in events:
            if subscription_id:
                # Только для конкретной подписки
                subscription = self.subscriptions.get(subscription_id)
                handler = self.handlers.get(subscription_id)
                
                if subscription and handler:
                    await self._deliver(event, subscription, handler)
                    replayed += 1
            else:
                # Для всех подходящих подписок
                subscription_ids = self.router.match(event.event_type)
                
                for sub_id in subscription_ids:
                    subscription = self.subscriptions.get(sub_id)
                    handler = self.handlers.get(sub_id)
                    
                    if subscription and handler:
                        await self._deliver(event, subscription, handler)
                        
                replayed += 1
                
        return replayed


class Aggregate:
    """Базовый агрегат для Event Sourcing"""
    
    def __init__(self, aggregate_id: str):
        self.aggregate_id = aggregate_id
        self.version = 0
        self.changes: List[Event] = []  # Несохранённые изменения
        
    def apply_event(self, event: Event):
        """Применение события (переопределяется в наследниках)"""
        pass
        
    def load_from_history(self, events: List[Event]):
        """Загрузка из истории событий"""
        for event in events:
            self.apply_event(event)
            self.version += 1
            
    def raise_event(self, event_type: str, payload: Dict[str, Any]):
        """Создание нового события"""
        event = Event(
            event_type=event_type,
            payload=payload,
            metadata=EventMetadata(
                source=self.aggregate_id
            )
        )
        self.changes.append(event)
        self.apply_event(event)
        
    def get_uncommitted_changes(self) -> List[Event]:
        """Получение несохранённых изменений"""
        return self.changes
        
    def mark_changes_committed(self):
        """Пометка изменений как сохранённых"""
        self.version += len(self.changes)
        self.changes = []


class CQRSCommandBus:
    """Шина команд для CQRS"""
    
    def __init__(self):
        self.handlers: Dict[str, Callable] = {}
        
    def register(self, command_type: str, handler: Callable):
        """Регистрация обработчика команды"""
        self.handlers[command_type] = handler
        
    async def dispatch(self, command_type: str, payload: Dict[str, Any]) -> Any:
        """Отправка команды"""
        handler = self.handlers.get(command_type)
        
        if not handler:
            raise ValueError(f"No handler for command: {command_type}")
            
        return await handler(payload)


class EventDrivenPlatform:
    """Платформа событийно-ориентированной архитектуры"""
    
    def __init__(self):
        self.event_bus = EventBus()
        self.command_bus = CQRSCommandBus()
        self.aggregates: Dict[str, Aggregate] = {}
        
    def register_schema(self, event_type: str, schema: Dict[str, Any],
                         version: str = "1.0", **kwargs) -> EventSchema:
        """Регистрация схемы события"""
        return self.event_bus.schema_registry.register(event_type, schema, version, **kwargs)
        
    def subscribe(self, subscriber_name: str, event_types: List[str],
                   handler: EventHandler, **kwargs) -> Subscription:
        """Подписка на события"""
        return self.event_bus.subscribe(subscriber_name, event_types, handler, **kwargs)
        
    async def publish(self, event_type: str, payload: Dict[str, Any],
                       **kwargs) -> Event:
        """Публикация события"""
        return await self.event_bus.publish(event_type, payload, **kwargs)
        
    def register_command(self, command_type: str, handler: Callable):
        """Регистрация обработчика команды"""
        self.command_bus.register(command_type, handler)
        
    async def execute_command(self, command_type: str, payload: Dict[str, Any]) -> Any:
        """Выполнение команды"""
        return await self.command_bus.dispatch(command_type, payload)
        
    async def replay_stream(self, stream_id: str, from_version: int = 0) -> int:
        """Воспроизведение потока событий"""
        return await self.event_bus.replay(stream_id, from_version)
        
    def get_dead_letter_queue(self) -> List[DeadLetterEntry]:
        """Получение DLQ"""
        return self.event_bus.dlq.get_pending()
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        return {
            **self.event_bus.stats,
            "subscriptions": len(self.event_bus.subscriptions),
            "schemas": sum(len(v) for v in self.event_bus.schema_registry.schemas.values()),
            "streams": len(self.event_bus.event_store.streams),
            "total_events": len(self.event_bus.event_store.events),
            "dlq_pending": len(self.event_bus.dlq.get_pending())
        }


# Пример агрегата для демонстрации
class OrderAggregate(Aggregate):
    """Агрегат заказа"""
    
    def __init__(self, order_id: str):
        super().__init__(order_id)
        self.status = "created"
        self.items = []
        self.total = 0.0
        self.customer_id = ""
        
    def apply_event(self, event: Event):
        if event.event_type == "order.created":
            self.customer_id = event.payload.get("customer_id", "")
            self.items = event.payload.get("items", [])
            self.total = event.payload.get("total", 0)
            self.status = "created"
        elif event.event_type == "order.confirmed":
            self.status = "confirmed"
        elif event.event_type == "order.shipped":
            self.status = "shipped"
        elif event.event_type == "order.delivered":
            self.status = "delivered"
        elif event.event_type == "order.cancelled":
            self.status = "cancelled"
            
    def create(self, customer_id: str, items: List[Dict], total: float):
        self.raise_event("order.created", {
            "customer_id": customer_id,
            "items": items,
            "total": total
        })
        
    def confirm(self):
        if self.status != "created":
            raise ValueError("Can only confirm created orders")
        self.raise_event("order.confirmed", {})
        
    def ship(self):
        if self.status != "confirmed":
            raise ValueError("Can only ship confirmed orders")
        self.raise_event("order.shipped", {})
        
    def deliver(self):
        if self.status != "shipped":
            raise ValueError("Can only deliver shipped orders")
        self.raise_event("order.delivered", {})


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 88: Event-Driven Architecture Platform")
    print("=" * 60)
    
    async def demo():
        platform = EventDrivenPlatform()
        print("✓ Event-Driven Platform created")
        
        # Регистрация схем событий
        print("\n📋 Registering Event Schemas...")
        
        platform.register_schema(
            "order.created",
            {
                "type": "object",
                "required": ["customer_id", "items", "total"],
                "properties": {
                    "customer_id": {"type": "string"},
                    "items": {"type": "array"},
                    "total": {"type": "number"}
                }
            },
            description="Event fired when a new order is created"
        )
        print("  ✓ order.created schema registered")
        
        platform.register_schema(
            "user.registered",
            {
                "type": "object",
                "required": ["user_id", "email"],
                "properties": {
                    "user_id": {"type": "string"},
                    "email": {"type": "string"},
                    "name": {"type": "string"}
                }
            },
            description="Event fired when a new user registers"
        )
        print("  ✓ user.registered schema registered")
        
        platform.register_schema(
            "payment.completed",
            {
                "type": "object",
                "required": ["payment_id", "order_id", "amount"],
                "properties": {
                    "payment_id": {"type": "string"},
                    "order_id": {"type": "string"},
                    "amount": {"type": "number"}
                }
            },
            description="Event fired when payment is completed"
        )
        print("  ✓ payment.completed schema registered")
        
        # Создание подписчиков
        print("\n👥 Creating Subscriptions...")
        
        # Обработчики событий
        processed_events = []
        
        async def order_handler(event: Event) -> bool:
            processed_events.append(("order_service", event.event_type))
            return True
            
        async def notification_handler(event: Event) -> bool:
            processed_events.append(("notification_service", event.event_type))
            return True
            
        async def analytics_handler(event: Event) -> bool:
            processed_events.append(("analytics_service", event.event_type))
            # Симулируем случайную ошибку для демонстрации DLQ
            if random.random() < 0.1:
                raise Exception("Analytics processing failed")
            return True
            
        # Подписки
        order_sub = platform.subscribe(
            "order-service",
            ["order.*"],
            order_handler,
            delivery_guarantee=DeliveryGuarantee.EXACTLY_ONCE
        )
        print(f"  ✓ {order_sub.subscriber_name} subscribed to: {order_sub.event_types}")
        
        notification_sub = platform.subscribe(
            "notification-service",
            ["user.registered", "order.created", "payment.completed"],
            notification_handler,
            delivery_guarantee=DeliveryGuarantee.AT_LEAST_ONCE
        )
        print(f"  ✓ {notification_sub.subscriber_name} subscribed to: {notification_sub.event_types}")
        
        analytics_sub = platform.subscribe(
            "analytics-service",
            ["*"],  # Все события
            analytics_handler,
            delivery_guarantee=DeliveryGuarantee.AT_LEAST_ONCE
        )
        print(f"  ✓ {analytics_sub.subscriber_name} subscribed to: all events (*)")
        
        # Публикация событий
        print("\n📤 Publishing Events...")
        
        # User Registration
        user_event = await platform.publish(
            "user.registered",
            {
                "user_id": "usr_001",
                "email": "john@example.com",
                "name": "John Doe"
            },
            source="auth-service",
            correlation_id="corr_001"
        )
        print(f"\n  📧 Published: user.registered")
        print(f"     Event ID: {user_event.metadata.event_id}")
        print(f"     Correlation ID: {user_event.metadata.correlation_id}")
        
        # Order Creation
        order_event = await platform.publish(
            "order.created",
            {
                "customer_id": "usr_001",
                "items": [
                    {"product_id": "prod_001", "quantity": 2, "price": 29.99},
                    {"product_id": "prod_002", "quantity": 1, "price": 49.99}
                ],
                "total": 109.97
            },
            source="order-service",
            stream_id="orders"
        )
        print(f"\n  🛒 Published: order.created")
        print(f"     Stream: orders")
        
        # Payment
        payment_event = await platform.publish(
            "payment.completed",
            {
                "payment_id": "pay_001",
                "order_id": order_event.metadata.event_id,
                "amount": 109.97
            },
            source="payment-service",
            causation_id=order_event.metadata.event_id
        )
        print(f"\n  💳 Published: payment.completed")
        print(f"     Causation ID: {payment_event.metadata.causation_id}")
        
        # Публикуем ещё несколько событий
        for i in range(5):
            await platform.publish(
                f"order.updated",
                {"order_id": f"ord_{i}", "status": "processing"},
                source="order-service",
                stream_id="orders"
            )
            
        print(f"\n  ✓ Published 5 additional order.updated events")
        
        # Обработанные события
        print("\n📨 Processed Events:")
        
        events_by_service = defaultdict(list)
        for service, event_type in processed_events:
            events_by_service[service].append(event_type)
            
        for service, events in events_by_service.items():
            print(f"\n  {service}:")
            for event_type in events[:5]:  # Показываем первые 5
                print(f"    • {event_type}")
            if len(events) > 5:
                print(f"    ... and {len(events) - 5} more")
                
        # Event Sourcing демонстрация
        print("\n📚 Event Sourcing Demo:")
        
        # Создаём агрегат заказа
        order = OrderAggregate("order_123")
        
        # Создаём заказ через агрегат
        order.create(
            customer_id="cust_001",
            items=[{"product": "Widget", "qty": 2}],
            total=99.99
        )
        order.confirm()
        order.ship()
        
        print(f"\n  Order Aggregate: {order.aggregate_id}")
        print(f"  Current Status: {order.status}")
        print(f"  Version: {order.version}")
        print(f"  Uncommitted Changes: {len(order.get_uncommitted_changes())}")
        
        print("\n  Event History:")
        for event in order.get_uncommitted_changes():
            print(f"    → {event.event_type}")
            
        # Сохраняем события
        for event in order.get_uncommitted_changes():
            await platform.event_bus.publish(
                event.event_type,
                event.payload,
                stream_id=f"order-{order.aggregate_id}"
            )
        order.mark_changes_committed()
        
        print(f"\n  ✓ Events committed (new version: {order.version})")
        
        # Replay демонстрация
        print("\n🔄 Event Replay Demo:")
        
        # Создаём новый агрегат и восстанавливаем из истории
        restored_order = OrderAggregate("order_123")
        
        # Получаем события из хранилища
        events = platform.event_bus.event_store.get_stream(f"order-{order.aggregate_id}")
        
        print(f"\n  Loading {len(events)} events from stream...")
        
        restored_order.load_from_history(events)
        
        print(f"  Restored Status: {restored_order.status}")
        print(f"  Restored Version: {restored_order.version}")
        
        # CQRS демонстрация
        print("\n⚡ CQRS Demo:")
        
        # Регистрируем обработчик команды
        async def create_order_handler(payload: Dict[str, Any]) -> str:
            order_id = f"ord_{uuid.uuid4().hex[:8]}"
            
            # Публикуем событие
            await platform.publish(
                "order.created",
                {
                    "customer_id": payload["customer_id"],
                    "items": payload["items"],
                    "total": payload["total"]
                },
                stream_id=f"order-{order_id}"
            )
            
            return order_id
            
        platform.register_command("CreateOrder", create_order_handler)
        
        # Выполняем команду
        new_order_id = await platform.execute_command("CreateOrder", {
            "customer_id": "cust_002",
            "items": [{"product": "Gadget", "qty": 1}],
            "total": 149.99
        })
        
        print(f"\n  Command: CreateOrder")
        print(f"  Result: Order {new_order_id} created")
        
        # Dead Letter Queue
        print("\n☠️ Dead Letter Queue:")
        
        dlq_entries = platform.get_dead_letter_queue()
        
        if dlq_entries:
            print(f"\n  Entries: {len(dlq_entries)}")
            for entry in dlq_entries[:3]:
                print(f"\n    ID: {entry.entry_id}")
                print(f"    Event: {entry.event.event_type if entry.event else 'N/A'}")
                print(f"    Error: {entry.error_message[:50]}...")
                print(f"    Attempts: {entry.attempt_count}")
        else:
            print("  ✅ No failed events in DLQ")
            
        # Статистика
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Events Published: {stats['events_published']}")
        print(f"  Events Delivered: {stats['events_delivered']}")
        print(f"  Events Failed: {stats['events_failed']}")
        print(f"  Subscriptions: {stats['subscriptions']}")
        print(f"  Event Schemas: {stats['schemas']}")
        print(f"  Event Streams: {stats['streams']}")
        print(f"  Total Events Stored: {stats['total_events']}")
        print(f"  DLQ Pending: {stats['dlq_pending']}")
        
        # Subscription статистика
        print("\n📈 Subscription Statistics:")
        
        for sub in platform.event_bus.subscriptions.values():
            success_rate = (sub.events_processed / sub.events_received * 100) if sub.events_received > 0 else 100
            
            print(f"\n  {sub.subscriber_name}:")
            print(f"    Events Received: {sub.events_received}")
            print(f"    Events Processed: {sub.events_processed}")
            print(f"    Events Failed: {sub.events_failed}")
            print(f"    Success Rate: {success_rate:.1f}%")
            
        # Event Flow Visualization
        print("\n🔀 Event Flow:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │                      EVENT BUS                              │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print("  │  Publishers          Routing           Subscribers         │")
        print("  │  ───────────         ────────          ────────────         │")
        print("  │  auth-service    →   user.*        →   notification         │")
        print("  │  order-service   →   order.*       →   order-service        │")
        print("  │  payment-service →   payment.*     →   analytics            │")
        print("  │                                    →   (all events)         │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
        # Event Store
        print("\n💾 Event Store Summary:")
        print("  ┌───────────────────────────────────────┐")
        print(f"  │ Total Events:     {stats['total_events']:>8}            │")
        print(f"  │ Active Streams:   {stats['streams']:>8}            │")
        print("  ├───────────────────────────────────────┤")
        
        for stream_id, event_ids in list(platform.event_bus.event_store.streams.items())[:5]:
            print(f"  │ {stream_id[:20]:20} ({len(event_ids):>4} events) │")
            
        print("  └───────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Event-Driven Architecture Platform initialized!")
    print("=" * 60)
