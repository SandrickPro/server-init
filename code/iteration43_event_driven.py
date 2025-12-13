#!/usr/bin/env python3
"""
Server Init - Iteration 43: Event-Driven Architecture Platform
Событийно-ориентированная архитектура

Функционал:
- Event Bus - шина событий
- Event Sourcing - событийный sourcing
- CQRS Pattern - разделение команд и запросов
- Saga Orchestration - оркестрация саг
- Event Store - хранилище событий
- Event Schema Registry - реестр схем событий
- Dead Letter Queue - очередь недоставленных сообщений
- Event Replay - воспроизведение событий
"""

import json
import asyncio
import hashlib
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Tuple, Type
from enum import Enum
from abc import ABC, abstractmethod
import random
from collections import defaultdict
import uuid


class EventType(Enum):
    """Тип события"""
    DOMAIN = "domain"
    INTEGRATION = "integration"
    NOTIFICATION = "notification"
    SYSTEM = "system"


class EventPriority(Enum):
    """Приоритет события"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class DeliveryGuarantee(Enum):
    """Гарантия доставки"""
    AT_MOST_ONCE = "at_most_once"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"


class SagaStatus(Enum):
    """Статус саги"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"


@dataclass
class Event:
    """Базовое событие"""
    event_id: str
    event_type: str
    aggregate_type: str
    aggregate_id: str
    
    # Данные
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Версионирование
    version: int = 1
    schema_version: str = "1.0"
    
    # Время
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Корреляция
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    # Приоритет
    priority: EventPriority = EventPriority.NORMAL
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "aggregate_type": self.aggregate_type,
            "aggregate_id": self.aggregate_id,
            "payload": self.payload,
            "metadata": self.metadata,
            "version": self.version,
            "schema_version": self.schema_version,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "priority": self.priority.value
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Создание из словаря"""
        return cls(
            event_id=data["event_id"],
            event_type=data["event_type"],
            aggregate_type=data["aggregate_type"],
            aggregate_id=data["aggregate_id"],
            payload=data["payload"],
            metadata=data.get("metadata", {}),
            version=data.get("version", 1),
            schema_version=data.get("schema_version", "1.0"),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            correlation_id=data.get("correlation_id"),
            causation_id=data.get("causation_id"),
            priority=EventPriority(data.get("priority", 2))
        )


@dataclass
class EventEnvelope:
    """Конверт события"""
    event: Event
    delivery_attempt: int = 1
    max_attempts: int = 3
    first_delivery_at: datetime = field(default_factory=datetime.now)
    last_delivery_at: Optional[datetime] = None
    next_retry_at: Optional[datetime] = None


@dataclass
class Subscription:
    """Подписка на события"""
    subscription_id: str
    subscriber_id: str
    event_types: List[str]
    
    # Фильтры
    filters: Dict[str, Any] = field(default_factory=dict)
    
    # Обработчик
    handler: Optional[Callable] = None
    handler_url: Optional[str] = None  # Для webhook
    
    # Настройки
    delivery_guarantee: DeliveryGuarantee = DeliveryGuarantee.AT_LEAST_ONCE
    max_retries: int = 3
    retry_delay_ms: int = 1000
    
    # Состояние
    enabled: bool = True
    last_event_id: Optional[str] = None
    
    # Метаданные
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class EventSchema:
    """Схема события"""
    schema_id: str
    event_type: str
    version: str
    
    # Схема
    json_schema: Dict[str, Any] = field(default_factory=dict)
    
    # Совместимость
    compatibility: str = "BACKWARD"  # BACKWARD, FORWARD, FULL, NONE
    
    # Метаданные
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Aggregate:
    """Базовый агрегат"""
    aggregate_id: str
    aggregate_type: str
    version: int = 0
    
    # Состояние
    state: Dict[str, Any] = field(default_factory=dict)
    
    # События
    uncommitted_events: List[Event] = field(default_factory=list)
    
    def apply_event(self, event: Event):
        """Применение события"""
        # Переопределяется в наследниках
        pass
        
    def raise_event(self, event_type: str, payload: Dict[str, Any]):
        """Создание нового события"""
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            event_type=event_type,
            aggregate_type=self.aggregate_type,
            aggregate_id=self.aggregate_id,
            payload=payload,
            version=self.version + 1
        )
        
        self.uncommitted_events.append(event)
        self.apply_event(event)
        self.version += 1


@dataclass
class SagaStep:
    """Шаг саги"""
    step_id: str
    name: str
    
    # Команда
    command: str
    command_params: Dict[str, Any] = field(default_factory=dict)
    
    # Компенсация
    compensation_command: Optional[str] = None
    compensation_params: Dict[str, Any] = field(default_factory=dict)
    
    # Состояние
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    # Время
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class Saga:
    """Сага"""
    saga_id: str
    saga_type: str
    
    # Шаги
    steps: List[SagaStep] = field(default_factory=list)
    current_step: int = 0
    
    # Данные
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Статус
    status: SagaStatus = SagaStatus.PENDING
    
    # Время
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Корреляция
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class Command:
    """Команда"""
    command_id: str
    command_type: str
    aggregate_id: str
    
    # Данные
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # Корреляция
    correlation_id: Optional[str] = None
    
    # Метаданные
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Query:
    """Запрос"""
    query_id: str
    query_type: str
    
    # Параметры
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Метаданные
    metadata: Dict[str, Any] = field(default_factory=dict)


class EventStore:
    """Хранилище событий"""
    
    def __init__(self):
        self.events: List[Event] = []
        self.event_index: Dict[str, int] = {}  # event_id -> position
        self.aggregate_index: Dict[str, List[int]] = defaultdict(list)  # aggregate_id -> positions
        self.snapshots: Dict[str, Dict[str, Any]] = {}
        
    async def append(self, event: Event) -> int:
        """Добавление события"""
        position = len(self.events)
        self.events.append(event)
        self.event_index[event.event_id] = position
        self.aggregate_index[event.aggregate_id].append(position)
        
        return position
        
    async def append_batch(self, events: List[Event]) -> List[int]:
        """Добавление пакета событий"""
        positions = []
        for event in events:
            pos = await self.append(event)
            positions.append(pos)
        return positions
        
    async def get_events(self, aggregate_id: str, 
                          from_version: int = 0) -> List[Event]:
        """Получение событий агрегата"""
        positions = self.aggregate_index.get(aggregate_id, [])
        events = [self.events[pos] for pos in positions]
        return [e for e in events if e.version > from_version]
        
    async def get_events_by_type(self, event_type: str,
                                   limit: int = 100) -> List[Event]:
        """Получение событий по типу"""
        return [e for e in self.events if e.event_type == event_type][:limit]
        
    async def get_all_events(self, from_position: int = 0,
                              limit: int = 1000) -> List[Event]:
        """Получение всех событий"""
        return self.events[from_position:from_position + limit]
        
    async def save_snapshot(self, aggregate_id: str, 
                             state: Dict[str, Any], version: int):
        """Сохранение снапшота"""
        self.snapshots[aggregate_id] = {
            "state": state,
            "version": version,
            "timestamp": datetime.now().isoformat()
        }
        
    async def get_snapshot(self, aggregate_id: str) -> Optional[Dict[str, Any]]:
        """Получение снапшота"""
        return self.snapshots.get(aggregate_id)
        
    def get_stats(self) -> Dict[str, Any]:
        """Статистика"""
        return {
            "total_events": len(self.events),
            "aggregates": len(self.aggregate_index),
            "snapshots": len(self.snapshots)
        }


class EventBus:
    """Шина событий"""
    
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        self.subscriptions: Dict[str, Subscription] = {}
        self.handlers: Dict[str, List[Callable]] = defaultdict(list)
        self.dead_letter_queue: List[EventEnvelope] = []
        self.processing_queue: asyncio.Queue = asyncio.Queue()
        
    def subscribe(self, subscription: Subscription):
        """Подписка на события"""
        self.subscriptions[subscription.subscription_id] = subscription
        
        if subscription.handler:
            for event_type in subscription.event_types:
                self.handlers[event_type].append(subscription.handler)
                
    def unsubscribe(self, subscription_id: str):
        """Отписка"""
        subscription = self.subscriptions.pop(subscription_id, None)
        if subscription and subscription.handler:
            for event_type in subscription.event_types:
                if subscription.handler in self.handlers[event_type]:
                    self.handlers[event_type].remove(subscription.handler)
                    
    async def publish(self, event: Event):
        """Публикация события"""
        # Сохранение в event store
        await self.event_store.append(event)
        
        # Добавление в очередь обработки
        envelope = EventEnvelope(event=event)
        await self.processing_queue.put(envelope)
        
    async def publish_batch(self, events: List[Event]):
        """Публикация пакета событий"""
        await self.event_store.append_batch(events)
        
        for event in events:
            envelope = EventEnvelope(event=event)
            await self.processing_queue.put(envelope)
            
    async def process_events(self):
        """Обработка событий"""
        while True:
            envelope = await self.processing_queue.get()
            
            try:
                await self._dispatch_event(envelope)
            except Exception as e:
                await self._handle_delivery_failure(envelope, str(e))
                
            self.processing_queue.task_done()
            
    async def _dispatch_event(self, envelope: EventEnvelope):
        """Диспетчеризация события"""
        event = envelope.event
        handlers = self.handlers.get(event.event_type, [])
        
        # Также отправляем в wildcard handlers
        handlers.extend(self.handlers.get("*", []))
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                print(f"Handler error: {e}")
                
        envelope.last_delivery_at = datetime.now()
        
    async def _handle_delivery_failure(self, envelope: EventEnvelope, error: str):
        """Обработка ошибки доставки"""
        envelope.delivery_attempt += 1
        
        if envelope.delivery_attempt <= envelope.max_attempts:
            # Retry с exponential backoff
            delay = 2 ** envelope.delivery_attempt
            envelope.next_retry_at = datetime.now() + timedelta(seconds=delay)
            await self.processing_queue.put(envelope)
        else:
            # Dead Letter Queue
            self.dead_letter_queue.append(envelope)
            
    async def replay_events(self, aggregate_id: str, 
                             from_version: int = 0) -> List[Event]:
        """Воспроизведение событий"""
        return await self.event_store.get_events(aggregate_id, from_version)
        
    def get_dead_letter_count(self) -> int:
        """Количество в DLQ"""
        return len(self.dead_letter_queue)
        
    async def retry_dead_letter(self, event_id: str) -> bool:
        """Повтор из DLQ"""
        for i, envelope in enumerate(self.dead_letter_queue):
            if envelope.event.event_id == event_id:
                envelope.delivery_attempt = 1
                envelope.max_attempts = 3
                await self.processing_queue.put(envelope)
                del self.dead_letter_queue[i]
                return True
        return False


class CommandBus:
    """Шина команд"""
    
    def __init__(self):
        self.handlers: Dict[str, Callable] = {}
        
    def register_handler(self, command_type: str, handler: Callable):
        """Регистрация обработчика"""
        self.handlers[command_type] = handler
        
    async def dispatch(self, command: Command) -> Any:
        """Отправка команды"""
        handler = self.handlers.get(command.command_type)
        
        if not handler:
            raise ValueError(f"No handler for command: {command.command_type}")
            
        if asyncio.iscoroutinefunction(handler):
            return await handler(command)
        else:
            return handler(command)


class QueryBus:
    """Шина запросов"""
    
    def __init__(self):
        self.handlers: Dict[str, Callable] = {}
        
    def register_handler(self, query_type: str, handler: Callable):
        """Регистрация обработчика"""
        self.handlers[query_type] = handler
        
    async def query(self, query: Query) -> Any:
        """Выполнение запроса"""
        handler = self.handlers.get(query.query_type)
        
        if not handler:
            raise ValueError(f"No handler for query: {query.query_type}")
            
        if asyncio.iscoroutinefunction(handler):
            return await handler(query)
        else:
            return handler(query)


class EventSchemaRegistry:
    """Реестр схем событий"""
    
    def __init__(self):
        self.schemas: Dict[str, Dict[str, EventSchema]] = defaultdict(dict)  # event_type -> {version -> schema}
        
    def register_schema(self, schema: EventSchema) -> str:
        """Регистрация схемы"""
        # Проверка совместимости
        existing = self.schemas.get(schema.event_type, {})
        
        if existing and schema.compatibility != "NONE":
            latest = max(existing.values(), key=lambda s: s.version)
            if not self._check_compatibility(latest, schema):
                raise ValueError("Schema is not compatible with previous version")
                
        self.schemas[schema.event_type][schema.version] = schema
        return schema.schema_id
        
    def _check_compatibility(self, old_schema: EventSchema, 
                              new_schema: EventSchema) -> bool:
        """Проверка совместимости"""
        # Упрощённая проверка
        if new_schema.compatibility == "BACKWARD":
            # Новая схема может читать старые данные
            return True
        elif new_schema.compatibility == "FORWARD":
            # Старая схема может читать новые данные
            return True
        elif new_schema.compatibility == "FULL":
            # Полная совместимость
            return True
        return True
        
    def get_schema(self, event_type: str, 
                    version: Optional[str] = None) -> Optional[EventSchema]:
        """Получение схемы"""
        schemas = self.schemas.get(event_type, {})
        
        if not schemas:
            return None
            
        if version:
            return schemas.get(version)
        else:
            # Последняя версия
            return max(schemas.values(), key=lambda s: s.version)
            
    def validate_event(self, event: Event) -> Tuple[bool, List[str]]:
        """Валидация события"""
        schema = self.get_schema(event.event_type, event.schema_version)
        
        if not schema:
            return False, ["Schema not found"]
            
        # Упрощённая валидация
        errors = []
        required = schema.json_schema.get("required", [])
        
        for field in required:
            if field not in event.payload:
                errors.append(f"Missing required field: {field}")
                
        return len(errors) == 0, errors


class SagaOrchestrator:
    """Оркестратор саг"""
    
    def __init__(self, command_bus: CommandBus, event_bus: EventBus):
        self.command_bus = command_bus
        self.event_bus = event_bus
        self.sagas: Dict[str, Saga] = {}
        self.saga_definitions: Dict[str, List[Dict[str, Any]]] = {}
        
    def define_saga(self, saga_type: str, steps: List[Dict[str, Any]]):
        """Определение саги"""
        self.saga_definitions[saga_type] = steps
        
    async def start_saga(self, saga_type: str, 
                          context: Dict[str, Any]) -> Saga:
        """Запуск саги"""
        definition = self.saga_definitions.get(saga_type)
        if not definition:
            raise ValueError(f"Saga not defined: {saga_type}")
            
        saga = Saga(
            saga_id=f"saga_{uuid.uuid4().hex[:12]}",
            saga_type=saga_type,
            context=context
        )
        
        # Создание шагов
        for i, step_def in enumerate(definition):
            step = SagaStep(
                step_id=f"step_{i}",
                name=step_def["name"],
                command=step_def["command"],
                command_params=step_def.get("params", {}),
                compensation_command=step_def.get("compensation"),
                compensation_params=step_def.get("compensation_params", {})
            )
            saga.steps.append(step)
            
        self.sagas[saga.saga_id] = saga
        
        # Запуск первого шага
        saga.status = SagaStatus.RUNNING
        saga.started_at = datetime.now()
        
        await self._execute_current_step(saga)
        
        return saga
        
    async def _execute_current_step(self, saga: Saga):
        """Выполнение текущего шага"""
        if saga.current_step >= len(saga.steps):
            saga.status = SagaStatus.COMPLETED
            saga.completed_at = datetime.now()
            return
            
        step = saga.steps[saga.current_step]
        step.status = "running"
        step.started_at = datetime.now()
        
        try:
            # Подготовка параметров команды
            params = dict(step.command_params)
            params.update(saga.context)
            
            command = Command(
                command_id=f"cmd_{uuid.uuid4().hex[:8]}",
                command_type=step.command,
                aggregate_id=params.get("aggregate_id", ""),
                payload=params,
                correlation_id=saga.correlation_id
            )
            
            result = await self.command_bus.dispatch(command)
            
            step.result = result
            step.status = "completed"
            step.completed_at = datetime.now()
            
            # Обновление контекста
            if result:
                saga.context.update(result)
                
            # Переход к следующему шагу
            saga.current_step += 1
            await self._execute_current_step(saga)
            
        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            
            # Запуск компенсации
            await self._compensate(saga)
            
    async def _compensate(self, saga: Saga):
        """Компенсация саги"""
        saga.status = SagaStatus.COMPENSATING
        
        # Компенсируем все выполненные шаги в обратном порядке
        for i in range(saga.current_step - 1, -1, -1):
            step = saga.steps[i]
            
            if step.compensation_command:
                try:
                    params = dict(step.compensation_params)
                    params.update(saga.context)
                    
                    command = Command(
                        command_id=f"cmd_comp_{uuid.uuid4().hex[:8]}",
                        command_type=step.compensation_command,
                        aggregate_id=params.get("aggregate_id", ""),
                        payload=params,
                        correlation_id=saga.correlation_id
                    )
                    
                    await self.command_bus.dispatch(command)
                    
                except Exception as e:
                    print(f"Compensation failed for step {step.name}: {e}")
                    
        saga.status = SagaStatus.COMPENSATED
        saga.completed_at = datetime.now()
        
    def get_saga(self, saga_id: str) -> Optional[Saga]:
        """Получение саги"""
        return self.sagas.get(saga_id)
        
    def get_saga_status(self, saga_id: str) -> Dict[str, Any]:
        """Статус саги"""
        saga = self.sagas.get(saga_id)
        if not saga:
            return {"error": "Saga not found"}
            
        return {
            "saga_id": saga.saga_id,
            "type": saga.saga_type,
            "status": saga.status.value,
            "current_step": saga.current_step,
            "total_steps": len(saga.steps),
            "steps": [
                {
                    "name": s.name,
                    "status": s.status,
                    "error": s.error
                }
                for s in saga.steps
            ],
            "started_at": saga.started_at.isoformat() if saga.started_at else None,
            "completed_at": saga.completed_at.isoformat() if saga.completed_at else None
        }


class Projection:
    """Проекция для CQRS"""
    
    def __init__(self, name: str):
        self.name = name
        self.state: Dict[str, Any] = {}
        self.handlers: Dict[str, Callable] = {}
        self.last_processed_position: int = -1
        
    def register_handler(self, event_type: str, handler: Callable):
        """Регистрация обработчика события"""
        self.handlers[event_type] = handler
        
    async def apply(self, event: Event):
        """Применение события"""
        handler = self.handlers.get(event.event_type)
        
        if handler:
            if asyncio.iscoroutinefunction(handler):
                await handler(self.state, event)
            else:
                handler(self.state, event)
                
    def get_state(self) -> Dict[str, Any]:
        """Получение состояния"""
        return self.state.copy()


class ProjectionManager:
    """Менеджер проекций"""
    
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        self.projections: Dict[str, Projection] = {}
        
    def register_projection(self, projection: Projection):
        """Регистрация проекции"""
        self.projections[projection.name] = projection
        
    async def rebuild_projection(self, projection_name: str):
        """Пересборка проекции"""
        projection = self.projections.get(projection_name)
        if not projection:
            return
            
        projection.state = {}
        projection.last_processed_position = -1
        
        events = await self.event_store.get_all_events()
        
        for i, event in enumerate(events):
            await projection.apply(event)
            projection.last_processed_position = i
            
    async def update_projections(self, event: Event):
        """Обновление всех проекций"""
        for projection in self.projections.values():
            await projection.apply(event)
            
    def get_projection_state(self, projection_name: str) -> Optional[Dict[str, Any]]:
        """Получение состояния проекции"""
        projection = self.projections.get(projection_name)
        if projection:
            return projection.get_state()
        return None


class EventDrivenPlatform:
    """Платформа событийно-ориентированной архитектуры"""
    
    def __init__(self):
        self.event_store = EventStore()
        self.event_bus = EventBus(self.event_store)
        self.command_bus = CommandBus()
        self.query_bus = QueryBus()
        self.schema_registry = EventSchemaRegistry()
        self.saga_orchestrator = SagaOrchestrator(self.command_bus, self.event_bus)
        self.projection_manager = ProjectionManager(self.event_store)
        
    def create_event(self, event_type: str, aggregate_type: str,
                      aggregate_id: str, payload: Dict[str, Any],
                      correlation_id: Optional[str] = None) -> Event:
        """Создание события"""
        return Event(
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            payload=payload,
            correlation_id=correlation_id or str(uuid.uuid4())
        )
        
    async def publish_event(self, event: Event):
        """Публикация события"""
        # Валидация схемы
        valid, errors = self.schema_registry.validate_event(event)
        if not valid:
            print(f"Event validation warnings: {errors}")
            
        # Публикация
        await self.event_bus.publish(event)
        
        # Обновление проекций
        await self.projection_manager.update_projections(event)
        
    def get_platform_stats(self) -> Dict[str, Any]:
        """Статистика платформы"""
        return {
            "event_store": self.event_store.get_stats(),
            "subscriptions": len(self.event_bus.subscriptions),
            "dead_letter_queue": self.event_bus.get_dead_letter_count(),
            "schemas": sum(len(v) for v in self.schema_registry.schemas.values()),
            "sagas": len(self.saga_orchestrator.sagas),
            "projections": len(self.projection_manager.projections)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 43: Event-Driven Architecture")
    print("=" * 60)
    
    async def demo():
        # Создание платформы
        platform = EventDrivenPlatform()
        print("✓ Event-Driven Platform created")
        
        # Регистрация схем событий
        order_created_schema = EventSchema(
            schema_id="schema_order_created",
            event_type="OrderCreated",
            version="1.0",
            json_schema={
                "type": "object",
                "required": ["order_id", "customer_id", "items"],
                "properties": {
                    "order_id": {"type": "string"},
                    "customer_id": {"type": "string"},
                    "items": {"type": "array"},
                    "total": {"type": "number"}
                }
            }
        )
        platform.schema_registry.register_schema(order_created_schema)
        print(f"✓ Registered event schema: {order_created_schema.event_type}")
        
        # Регистрация обработчиков команд
        async def create_order_handler(command: Command) -> Dict[str, Any]:
            print(f"  📦 Creating order: {command.payload.get('order_id')}")
            return {"order_id": command.payload.get("order_id"), "status": "created"}
            
        async def reserve_inventory_handler(command: Command) -> Dict[str, Any]:
            print(f"  📦 Reserving inventory for: {command.payload.get('order_id')}")
            return {"reserved": True}
            
        async def process_payment_handler(command: Command) -> Dict[str, Any]:
            print(f"  💳 Processing payment for: {command.payload.get('order_id')}")
            # Симуляция успеха/неудачи
            if random.random() > 0.3:
                return {"payment_id": f"pay_{uuid.uuid4().hex[:8]}", "status": "completed"}
            else:
                raise Exception("Payment failed")
                
        async def release_inventory_handler(command: Command) -> Dict[str, Any]:
            print(f"  🔄 Releasing inventory for: {command.payload.get('order_id')}")
            return {"released": True}
            
        platform.command_bus.register_handler("CreateOrder", create_order_handler)
        platform.command_bus.register_handler("ReserveInventory", reserve_inventory_handler)
        platform.command_bus.register_handler("ProcessPayment", process_payment_handler)
        platform.command_bus.register_handler("ReleaseInventory", release_inventory_handler)
        print("✓ Registered command handlers")
        
        # Определение саги
        platform.saga_orchestrator.define_saga("OrderProcessing", [
            {
                "name": "Create Order",
                "command": "CreateOrder",
                "params": {}
            },
            {
                "name": "Reserve Inventory",
                "command": "ReserveInventory",
                "compensation": "ReleaseInventory"
            },
            {
                "name": "Process Payment",
                "command": "ProcessPayment"
            }
        ])
        print("✓ Defined OrderProcessing saga")
        
        # Создание проекции
        orders_projection = Projection("orders")
        
        def on_order_created(state: Dict, event: Event):
            order_id = event.payload.get("order_id")
            state[order_id] = {
                "status": "created",
                "customer_id": event.payload.get("customer_id"),
                "items": event.payload.get("items"),
                "total": event.payload.get("total")
            }
            
        orders_projection.register_handler("OrderCreated", on_order_created)
        platform.projection_manager.register_projection(orders_projection)
        print("✓ Created orders projection")
        
        # Подписка на события
        event_log = []
        
        def log_event(event: Event):
            event_log.append(event)
            print(f"  📩 Event received: {event.event_type}")
            
        subscription = Subscription(
            subscription_id="sub_logger",
            subscriber_id="event_logger",
            event_types=["*"],
            handler=log_event
        )
        platform.event_bus.subscribe(subscription)
        print("✓ Created event subscription")
        
        # Публикация событий
        print(f"\n📤 Publishing events...")
        
        order_event = platform.create_event(
            event_type="OrderCreated",
            aggregate_type="Order",
            aggregate_id="order_001",
            payload={
                "order_id": "order_001",
                "customer_id": "cust_123",
                "items": [{"sku": "SKU-001", "qty": 2}],
                "total": 99.99
            }
        )
        
        await platform.publish_event(order_event)
        
        # Запуск обработки событий в фоне
        processor_task = asyncio.create_task(platform.event_bus.process_events())
        await asyncio.sleep(0.1)  # Даём время на обработку
        
        print(f"  Events logged: {len(event_log)}")
        
        # Проверка проекции
        orders_state = platform.projection_manager.get_projection_state("orders")
        print(f"  Orders in projection: {len(orders_state)}")
        
        # Запуск саги
        print(f"\n🎭 Starting saga...")
        
        saga = await platform.saga_orchestrator.start_saga(
            "OrderProcessing",
            {"order_id": "order_002", "customer_id": "cust_456", "amount": 150.00}
        )
        
        status = platform.saga_orchestrator.get_saga_status(saga.saga_id)
        print(f"  Saga ID: {saga.saga_id}")
        print(f"  Status: {status['status']}")
        print(f"  Steps: {status['current_step']}/{status['total_steps']}")
        
        for step in status['steps']:
            status_emoji = "✓" if step['status'] == 'completed' else "✗" if step['status'] == 'failed' else "○"
            print(f"    {status_emoji} {step['name']}: {step['status']}")
            
        # Event Store stats
        store_stats = platform.event_store.get_stats()
        print(f"\n📊 Event Store:")
        print(f"  Total Events: {store_stats['total_events']}")
        print(f"  Aggregates: {store_stats['aggregates']}")
        
        # Platform stats
        platform_stats = platform.get_platform_stats()
        print(f"\n🎯 Platform Stats:")
        print(f"  Subscriptions: {platform_stats['subscriptions']}")
        print(f"  Schemas: {platform_stats['schemas']}")
        print(f"  Projections: {platform_stats['projections']}")
        print(f"  Dead Letter Queue: {platform_stats['dead_letter_queue']}")
        
        # Отмена фоновой задачи
        processor_task.cancel()
        try:
            await processor_task
        except asyncio.CancelledError:
            pass
            
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Event-Driven Architecture Platform initialized!")
    print("=" * 60)
