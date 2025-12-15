#!/usr/bin/env python3
"""
Server Init - Iteration 344: Event-Driven Architecture Platform
Платформа событийно-ориентированной архитектуры

Функционал:
- Event Bus - шина событий
- Event Sourcing - источник событий
- CQRS Pattern - паттерн CQRS
- Saga Orchestration - оркестрация саг
- Event Schema Registry - реестр схем событий
- Dead Letter Queue - очередь недоставленных сообщений
- Event Replay - воспроизведение событий
- Event Analytics - аналитика событий
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Awaitable
from enum import Enum
import uuid
import json
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
    DEAD_LETTERED = "dead_lettered"
    REPLAYED = "replayed"


class SubscriptionType(Enum):
    """Тип подписки"""
    PUSH = "push"
    PULL = "pull"
    BROADCAST = "broadcast"


class DeliveryGuarantee(Enum):
    """Гарантия доставки"""
    AT_MOST_ONCE = "at_most_once"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"


class SagaStatus(Enum):
    """Статус саги"""
    STARTED = "started"
    RUNNING = "running"
    COMPLETED = "completed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"
    FAILED = "failed"


class SchemaFormat(Enum):
    """Формат схемы"""
    JSON_SCHEMA = "json_schema"
    AVRO = "avro"
    PROTOBUF = "protobuf"


class AggregateStatus(Enum):
    """Статус агрегата"""
    ACTIVE = "active"
    DELETED = "deleted"
    ARCHIVED = "archived"


@dataclass
class Event:
    """Событие"""
    event_id: str
    
    # Type
    event_type: str = ""
    
    # Source
    source_service: str = ""
    source_aggregate_id: str = ""
    
    # Payload
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    correlation_id: str = ""
    causation_id: str = ""
    
    # Priority
    priority: EventPriority = EventPriority.NORMAL
    
    # Status
    status: EventStatus = EventStatus.PENDING
    
    # Version
    version: int = 1
    schema_version: str = "1.0"
    
    # Timestamps
    timestamp: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    
    # Retry
    retry_count: int = 0
    max_retries: int = 3
    
    # Partition
    partition_key: str = ""


@dataclass
class EventTopic:
    """Топик событий"""
    topic_id: str
    name: str
    
    # Configuration
    partitions: int = 4
    replication_factor: int = 3
    retention_hours: int = 168  # 7 days
    
    # Schema
    schema_id: str = ""
    
    # Status
    is_active: bool = True
    
    # Stats
    total_events: int = 0
    events_per_second: float = 0.0
    
    # Description
    description: str = ""
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Subscription:
    """Подписка"""
    subscription_id: str
    name: str
    
    # Topic
    topic_id: str = ""
    
    # Subscriber
    subscriber_service: str = ""
    endpoint: str = ""
    
    # Type
    subscription_type: SubscriptionType = SubscriptionType.PUSH
    delivery_guarantee: DeliveryGuarantee = DeliveryGuarantee.AT_LEAST_ONCE
    
    # Filter
    filter_expression: str = ""
    
    # Configuration
    max_delivery_attempts: int = 5
    ack_deadline_seconds: int = 60
    batch_size: int = 100
    
    # Status
    is_active: bool = True
    
    # Stats
    pending_messages: int = 0
    delivered_messages: int = 0
    failed_messages: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class EventSchema:
    """Схема события"""
    schema_id: str
    name: str
    
    # Format
    schema_format: SchemaFormat = SchemaFormat.JSON_SCHEMA
    
    # Version
    version: int = 1
    
    # Definition
    schema_definition: Dict[str, Any] = field(default_factory=dict)
    
    # Compatibility
    compatibility: str = "backward"  # backward, forward, full, none
    
    # Event types
    event_types: List[str] = field(default_factory=list)
    
    # Status
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Aggregate:
    """Агрегат (Event Sourcing)"""
    aggregate_id: str
    aggregate_type: str = ""
    
    # Version
    version: int = 0
    
    # State
    current_state: Dict[str, Any] = field(default_factory=dict)
    status: AggregateStatus = AggregateStatus.ACTIVE
    
    # Events
    event_ids: List[str] = field(default_factory=list)
    
    # Snapshot
    snapshot_version: int = 0
    snapshot_state: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


@dataclass
class Command:
    """Команда (CQRS)"""
    command_id: str
    command_type: str = ""
    
    # Target
    target_aggregate_id: str = ""
    
    # Payload
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # User
    user_id: str = ""
    
    # Correlation
    correlation_id: str = ""
    
    # Status
    status: str = "pending"  # pending, processing, completed, failed
    
    # Result
    result: Dict[str, Any] = field(default_factory=dict)
    error: str = ""
    
    # Timestamps
    submitted_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None


@dataclass
class Query:
    """Запрос (CQRS)"""
    query_id: str
    query_type: str = ""
    
    # Parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # User
    user_id: str = ""
    
    # Result
    result: Any = None
    
    # Timing
    execution_time_ms: float = 0.0
    
    # Timestamps
    executed_at: datetime = field(default_factory=datetime.now)


@dataclass
class Saga:
    """Сага"""
    saga_id: str
    saga_type: str = ""
    
    # Status
    status: SagaStatus = SagaStatus.STARTED
    
    # Steps
    steps: List[Dict[str, Any]] = field(default_factory=list)
    current_step: int = 0
    
    # Context
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Compensation
    compensated_steps: List[int] = field(default_factory=list)
    
    # Events
    emitted_event_ids: List[str] = field(default_factory=list)
    
    # Correlation
    correlation_id: str = ""
    
    # Error
    error: str = ""
    
    # Timestamps
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class DeadLetterEntry:
    """Запись в очереди недоставленных"""
    entry_id: str
    
    # Original event
    event_id: str = ""
    event_type: str = ""
    
    # Subscription
    subscription_id: str = ""
    
    # Error
    error_message: str = ""
    error_count: int = 0
    
    # Payload
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    status: str = "pending"  # pending, reprocessing, resolved, discarded
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_retry: Optional[datetime] = None


@dataclass
class EventProjection:
    """Проекция событий"""
    projection_id: str
    name: str
    
    # Source
    source_topic_ids: List[str] = field(default_factory=list)
    
    # Target
    target_type: str = ""  # table, view, cache
    target_name: str = ""
    
    # Status
    status: str = "running"  # running, paused, error
    
    # Position
    last_processed_event_id: str = ""
    processed_events: int = 0
    
    # Lag
    lag_events: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: Optional[datetime] = None


@dataclass
class EventReplay:
    """Воспроизведение событий"""
    replay_id: str
    
    # Source
    source_topic_id: str = ""
    
    # Target
    target_subscription_id: str = ""
    
    # Range
    from_timestamp: Optional[datetime] = None
    to_timestamp: Optional[datetime] = None
    from_event_id: str = ""
    
    # Filter
    event_types: List[str] = field(default_factory=list)
    
    # Status
    status: str = "pending"  # pending, running, completed, failed
    
    # Progress
    total_events: int = 0
    replayed_events: int = 0
    
    # Timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class EventPlatform:
    """Платформа событийной архитектуры"""
    
    def __init__(self):
        self.events: Dict[str, Event] = {}
        self.topics: Dict[str, EventTopic] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        self.schemas: Dict[str, EventSchema] = {}
        self.aggregates: Dict[str, Aggregate] = {}
        self.commands: Dict[str, Command] = {}
        self.queries: Dict[str, Query] = {}
        self.sagas: Dict[str, Saga] = {}
        self.dead_letter_queue: Dict[str, DeadLetterEntry] = {}
        self.projections: Dict[str, EventProjection] = {}
        self.replays: Dict[str, EventReplay] = {}
        
        # Event handlers
        self.handlers: Dict[str, List[Callable]] = {}
        
        # Stats
        self.total_published = 0
        self.total_delivered = 0
        self.total_failed = 0
        
    async def create_topic(self, name: str,
                          partitions: int = 4,
                          replication_factor: int = 3,
                          retention_hours: int = 168,
                          schema_id: str = "",
                          description: str = "",
                          labels: Dict[str, str] = None) -> EventTopic:
        """Создание топика"""
        topic = EventTopic(
            topic_id=f"topic_{uuid.uuid4().hex[:8]}",
            name=name,
            partitions=partitions,
            replication_factor=replication_factor,
            retention_hours=retention_hours,
            schema_id=schema_id,
            description=description,
            labels=labels or {}
        )
        
        self.topics[topic.topic_id] = topic
        return topic
        
    async def register_schema(self, name: str,
                             schema_format: SchemaFormat,
                             schema_definition: Dict[str, Any],
                             event_types: List[str] = None,
                             compatibility: str = "backward") -> EventSchema:
        """Регистрация схемы"""
        schema = EventSchema(
            schema_id=f"schema_{uuid.uuid4().hex[:8]}",
            name=name,
            schema_format=schema_format,
            schema_definition=schema_definition,
            event_types=event_types or [],
            compatibility=compatibility
        )
        
        self.schemas[schema.schema_id] = schema
        return schema
        
    async def create_subscription(self, name: str,
                                 topic_id: str,
                                 subscriber_service: str,
                                 endpoint: str = "",
                                 subscription_type: SubscriptionType = SubscriptionType.PUSH,
                                 delivery_guarantee: DeliveryGuarantee = DeliveryGuarantee.AT_LEAST_ONCE,
                                 filter_expression: str = "",
                                 max_delivery_attempts: int = 5) -> Optional[Subscription]:
        """Создание подписки"""
        topic = self.topics.get(topic_id)
        if not topic:
            return None
            
        subscription = Subscription(
            subscription_id=f"sub_{uuid.uuid4().hex[:8]}",
            name=name,
            topic_id=topic_id,
            subscriber_service=subscriber_service,
            endpoint=endpoint,
            subscription_type=subscription_type,
            delivery_guarantee=delivery_guarantee,
            filter_expression=filter_expression,
            max_delivery_attempts=max_delivery_attempts
        )
        
        self.subscriptions[subscription.subscription_id] = subscription
        return subscription
        
    async def publish_event(self, topic_id: str,
                           event_type: str,
                           payload: Dict[str, Any],
                           source_service: str,
                           source_aggregate_id: str = "",
                           correlation_id: str = "",
                           causation_id: str = "",
                           priority: EventPriority = EventPriority.NORMAL,
                           partition_key: str = "") -> Optional[Event]:
        """Публикация события"""
        topic = self.topics.get(topic_id)
        if not topic or not topic.is_active:
            return None
            
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            event_type=event_type,
            source_service=source_service,
            source_aggregate_id=source_aggregate_id,
            payload=payload,
            correlation_id=correlation_id or str(uuid.uuid4()),
            causation_id=causation_id,
            priority=priority,
            partition_key=partition_key or source_aggregate_id
        )
        
        # Validate against schema if exists
        if topic.schema_id:
            schema = self.schemas.get(topic.schema_id)
            if schema and event_type not in schema.event_types:
                pass  # Could add validation logic
                
        self.events[event.event_id] = event
        topic.total_events += 1
        self.total_published += 1
        
        # Deliver to subscribers
        await self._deliver_to_subscribers(topic_id, event)
        
        return event
        
    async def _deliver_to_subscribers(self, topic_id: str, event: Event):
        """Доставка события подписчикам"""
        for subscription in self.subscriptions.values():
            if subscription.topic_id != topic_id or not subscription.is_active:
                continue
                
            # Check filter
            if subscription.filter_expression:
                if not self._match_filter(event, subscription.filter_expression):
                    continue
                    
            # Simulate delivery
            success = random.random() > 0.05  # 95% success rate
            
            if success:
                event.status = EventStatus.DELIVERED
                event.processed_at = datetime.now()
                subscription.delivered_messages += 1
                self.total_delivered += 1
            else:
                event.retry_count += 1
                
                if event.retry_count >= subscription.max_delivery_attempts:
                    event.status = EventStatus.DEAD_LETTERED
                    subscription.failed_messages += 1
                    self.total_failed += 1
                    
                    # Add to dead letter queue
                    await self._add_to_dead_letter(event, subscription.subscription_id, "Delivery failed")
                else:
                    event.status = EventStatus.FAILED
                    subscription.pending_messages += 1
                    
    def _match_filter(self, event: Event, filter_expression: str) -> bool:
        """Проверка фильтра"""
        # Simple filter matching (e.g., "event_type:order.created")
        if ":" in filter_expression:
            key, value = filter_expression.split(":", 1)
            if key == "event_type":
                return event.event_type == value
            elif key in event.payload:
                return str(event.payload[key]) == value
        return True
        
    async def _add_to_dead_letter(self, event: Event,
                                 subscription_id: str,
                                 error_message: str):
        """Добавление в очередь недоставленных"""
        entry = DeadLetterEntry(
            entry_id=f"dlq_{uuid.uuid4().hex[:8]}",
            event_id=event.event_id,
            event_type=event.event_type,
            subscription_id=subscription_id,
            error_message=error_message,
            error_count=event.retry_count,
            payload=event.payload
        )
        
        self.dead_letter_queue[entry.entry_id] = entry
        
    async def create_aggregate(self, aggregate_type: str,
                              initial_state: Dict[str, Any] = None) -> Aggregate:
        """Создание агрегата"""
        aggregate = Aggregate(
            aggregate_id=f"agg_{uuid.uuid4().hex[:12]}",
            aggregate_type=aggregate_type,
            current_state=initial_state or {}
        )
        
        self.aggregates[aggregate.aggregate_id] = aggregate
        return aggregate
        
    async def apply_event_to_aggregate(self, aggregate_id: str,
                                      event: Event) -> bool:
        """Применение события к агрегату"""
        aggregate = self.aggregates.get(aggregate_id)
        if not aggregate:
            return False
            
        # Apply event (simplified)
        aggregate.version += 1
        aggregate.event_ids.append(event.event_id)
        aggregate.updated_at = datetime.now()
        
        # Update state based on event type
        event_type = event.event_type.split(".")[-1]
        
        if event_type == "created":
            aggregate.current_state.update(event.payload)
        elif event_type == "updated":
            aggregate.current_state.update(event.payload)
        elif event_type == "deleted":
            aggregate.status = AggregateStatus.DELETED
            
        return True
        
    async def snapshot_aggregate(self, aggregate_id: str) -> bool:
        """Создание снапшота агрегата"""
        aggregate = self.aggregates.get(aggregate_id)
        if not aggregate:
            return False
            
        aggregate.snapshot_version = aggregate.version
        aggregate.snapshot_state = aggregate.current_state.copy()
        
        return True
        
    async def rebuild_aggregate(self, aggregate_id: str) -> Optional[Dict[str, Any]]:
        """Восстановление агрегата из событий"""
        aggregate = self.aggregates.get(aggregate_id)
        if not aggregate:
            return None
            
        # Start from snapshot if available
        if aggregate.snapshot_version > 0:
            state = aggregate.snapshot_state.copy()
            start_idx = aggregate.snapshot_version
        else:
            state = {}
            start_idx = 0
            
        # Apply events
        for event_id in aggregate.event_ids[start_idx:]:
            event = self.events.get(event_id)
            if event:
                event_type = event.event_type.split(".")[-1]
                if event_type in ["created", "updated"]:
                    state.update(event.payload)
                    
        return state
        
    async def submit_command(self, command_type: str,
                            target_aggregate_id: str,
                            payload: Dict[str, Any],
                            user_id: str = "") -> Command:
        """Отправка команды"""
        command = Command(
            command_id=f"cmd_{uuid.uuid4().hex[:12]}",
            command_type=command_type,
            target_aggregate_id=target_aggregate_id,
            payload=payload,
            user_id=user_id,
            correlation_id=str(uuid.uuid4())
        )
        
        self.commands[command.command_id] = command
        
        # Process command
        await self._process_command(command)
        
        return command
        
    async def _process_command(self, command: Command):
        """Обработка команды"""
        command.status = "processing"
        
        # Simulate processing
        success = random.random() > 0.1  # 90% success
        
        if success:
            command.status = "completed"
            command.result = {"success": True, "message": "Command processed"}
            
            # Generate event from command
            event_type = command.command_type.replace("Command", ".processed")
            
        else:
            command.status = "failed"
            command.error = "Processing failed"
            
        command.processed_at = datetime.now()
        
    async def execute_query(self, query_type: str,
                           parameters: Dict[str, Any],
                           user_id: str = "") -> Query:
        """Выполнение запроса"""
        query = Query(
            query_id=f"qry_{uuid.uuid4().hex[:8]}",
            query_type=query_type,
            parameters=parameters,
            user_id=user_id
        )
        
        start_time = datetime.now()
        
        # Simulate query execution
        await asyncio.sleep(0.01)  # Simulated latency
        
        # Generate mock result
        query.result = {
            "data": [{"id": f"item_{i}", "value": random.randint(1, 100)} for i in range(5)],
            "total": 5
        }
        
        query.execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        self.queries[query.query_id] = query
        return query
        
    async def start_saga(self, saga_type: str,
                        steps: List[Dict[str, Any]],
                        context: Dict[str, Any] = None,
                        correlation_id: str = "") -> Saga:
        """Запуск саги"""
        saga = Saga(
            saga_id=f"saga_{uuid.uuid4().hex[:12]}",
            saga_type=saga_type,
            steps=steps,
            context=context or {},
            correlation_id=correlation_id or str(uuid.uuid4())
        )
        
        self.sagas[saga.saga_id] = saga
        
        # Start executing saga
        await self._execute_saga(saga)
        
        return saga
        
    async def _execute_saga(self, saga: Saga):
        """Выполнение саги"""
        saga.status = SagaStatus.RUNNING
        
        for i, step in enumerate(saga.steps):
            saga.current_step = i
            
            # Simulate step execution
            success = random.random() > 0.15  # 85% success
            
            if success:
                step["status"] = "completed"
            else:
                step["status"] = "failed"
                saga.error = f"Step {i} failed: {step.get('name', 'Unknown')}"
                
                # Start compensation
                await self._compensate_saga(saga, i)
                return
                
        saga.status = SagaStatus.COMPLETED
        saga.completed_at = datetime.now()
        
    async def _compensate_saga(self, saga: Saga, failed_step: int):
        """Компенсация саги"""
        saga.status = SagaStatus.COMPENSATING
        
        # Compensate in reverse order
        for i in range(failed_step - 1, -1, -1):
            step = saga.steps[i]
            
            if step.get("compensate"):
                # Execute compensation
                step["status"] = "compensated"
                saga.compensated_steps.append(i)
                
        saga.status = SagaStatus.COMPENSATED
        saga.completed_at = datetime.now()
        
    async def create_projection(self, name: str,
                               source_topic_ids: List[str],
                               target_type: str,
                               target_name: str) -> EventProjection:
        """Создание проекции"""
        projection = EventProjection(
            projection_id=f"proj_{uuid.uuid4().hex[:8]}",
            name=name,
            source_topic_ids=source_topic_ids,
            target_type=target_type,
            target_name=target_name
        )
        
        self.projections[projection.projection_id] = projection
        return projection
        
    async def start_replay(self, source_topic_id: str,
                          target_subscription_id: str,
                          from_timestamp: datetime = None,
                          to_timestamp: datetime = None,
                          event_types: List[str] = None) -> EventReplay:
        """Запуск воспроизведения"""
        replay = EventReplay(
            replay_id=f"replay_{uuid.uuid4().hex[:8]}",
            source_topic_id=source_topic_id,
            target_subscription_id=target_subscription_id,
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp,
            event_types=event_types or []
        )
        
        self.replays[replay.replay_id] = replay
        
        # Start replay
        await self._execute_replay(replay)
        
        return replay
        
    async def _execute_replay(self, replay: EventReplay):
        """Выполнение воспроизведения"""
        replay.status = "running"
        replay.started_at = datetime.now()
        
        # Find matching events
        for event in self.events.values():
            # Check filters
            if replay.from_timestamp and event.timestamp < replay.from_timestamp:
                continue
            if replay.to_timestamp and event.timestamp > replay.to_timestamp:
                continue
            if replay.event_types and event.event_type not in replay.event_types:
                continue
                
            replay.total_events += 1
            
            # Replay event
            event.status = EventStatus.REPLAYED
            replay.replayed_events += 1
            
        replay.status = "completed"
        replay.completed_at = datetime.now()
        
    async def reprocess_dead_letter(self, entry_id: str) -> bool:
        """Повторная обработка из DLQ"""
        entry = self.dead_letter_queue.get(entry_id)
        if not entry or entry.status != "pending":
            return False
            
        entry.status = "reprocessing"
        entry.last_retry = datetime.now()
        
        # Simulate reprocessing
        success = random.random() > 0.3  # 70% success on retry
        
        if success:
            entry.status = "resolved"
            return True
        else:
            entry.error_count += 1
            entry.status = "pending"
            return False
            
    def get_topic_stats(self, topic_id: str) -> Dict[str, Any]:
        """Статистика топика"""
        topic = self.topics.get(topic_id)
        if not topic:
            return {}
            
        subscribers = [s for s in self.subscriptions.values() if s.topic_id == topic_id]
        
        return {
            "topic_name": topic.name,
            "total_events": topic.total_events,
            "partitions": topic.partitions,
            "subscribers": len(subscribers),
            "retention_hours": topic.retention_hours
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_topics = len(self.topics)
        active_topics = sum(1 for t in self.topics.values() if t.is_active)
        
        total_subscriptions = len(self.subscriptions)
        active_subscriptions = sum(1 for s in self.subscriptions.values() if s.is_active)
        
        total_schemas = len(self.schemas)
        
        total_events = len(self.events)
        delivered_events = sum(1 for e in self.events.values() if e.status == EventStatus.DELIVERED)
        failed_events = sum(1 for e in self.events.values() if e.status == EventStatus.FAILED)
        
        total_aggregates = len(self.aggregates)
        
        total_commands = len(self.commands)
        completed_commands = sum(1 for c in self.commands.values() if c.status == "completed")
        
        total_queries = len(self.queries)
        
        total_sagas = len(self.sagas)
        completed_sagas = sum(1 for s in self.sagas.values() if s.status == SagaStatus.COMPLETED)
        
        dlq_size = len(self.dead_letter_queue)
        pending_dlq = sum(1 for d in self.dead_letter_queue.values() if d.status == "pending")
        
        total_projections = len(self.projections)
        
        return {
            "total_topics": total_topics,
            "active_topics": active_topics,
            "total_subscriptions": total_subscriptions,
            "active_subscriptions": active_subscriptions,
            "total_schemas": total_schemas,
            "total_events": total_events,
            "delivered_events": delivered_events,
            "failed_events": failed_events,
            "total_aggregates": total_aggregates,
            "total_commands": total_commands,
            "completed_commands": completed_commands,
            "total_queries": total_queries,
            "total_sagas": total_sagas,
            "completed_sagas": completed_sagas,
            "dlq_size": dlq_size,
            "pending_dlq": pending_dlq,
            "total_projections": total_projections
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 344: Event-Driven Architecture")
    print("=" * 60)
    
    platform = EventPlatform()
    print("✓ Event Platform initialized")
    
    # Register Schemas
    print("\n📋 Registering Event Schemas...")
    
    schemas_data = [
        ("Order Events", SchemaFormat.JSON_SCHEMA, {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "customer_id": {"type": "string"},
                "total": {"type": "number"}
            }
        }, ["order.created", "order.updated", "order.cancelled", "order.completed"]),
        ("Payment Events", SchemaFormat.JSON_SCHEMA, {
            "type": "object",
            "properties": {
                "payment_id": {"type": "string"},
                "order_id": {"type": "string"},
                "amount": {"type": "number"}
            }
        }, ["payment.initiated", "payment.completed", "payment.failed"]),
        ("Inventory Events", SchemaFormat.AVRO, {
            "type": "record",
            "name": "InventoryEvent"
        }, ["inventory.reserved", "inventory.released", "inventory.updated"]),
        ("Shipping Events", SchemaFormat.JSON_SCHEMA, {
            "type": "object",
            "properties": {"shipment_id": {"type": "string"}}
        }, ["shipping.created", "shipping.dispatched", "shipping.delivered"])
    ]
    
    schemas = []
    for name, fmt, definition, events in schemas_data:
        schema = await platform.register_schema(name, fmt, definition, events)
        schemas.append(schema)
        print(f"  📋 {name} ({len(events)} event types)")
        
    # Create Topics
    print("\n📨 Creating Event Topics...")
    
    topics_data = [
        ("orders", 8, 3, 168, schemas[0].schema_id, "Order domain events"),
        ("payments", 4, 3, 336, schemas[1].schema_id, "Payment transactions"),
        ("inventory", 4, 3, 168, schemas[2].schema_id, "Inventory changes"),
        ("shipping", 4, 3, 720, schemas[3].schema_id, "Shipping updates"),
        ("notifications", 2, 3, 24, "", "User notifications"),
        ("analytics", 16, 3, 720, "", "Analytics events")
    ]
    
    topics = []
    for name, parts, repl, ret, schema_id, desc in topics_data:
        topic = await platform.create_topic(name, parts, repl, ret, schema_id, desc)
        topics.append(topic)
        print(f"  📨 {name} ({parts} partitions)")
        
    # Create Subscriptions
    print("\n📬 Creating Subscriptions...")
    
    subscriptions_data = [
        ("order-service-sub", topics[0].topic_id, "order-service", "http://order-service/events", SubscriptionType.PUSH, DeliveryGuarantee.EXACTLY_ONCE),
        ("payment-processor-sub", topics[1].topic_id, "payment-service", "http://payment-service/events", SubscriptionType.PUSH, DeliveryGuarantee.EXACTLY_ONCE),
        ("inventory-sub", topics[2].topic_id, "inventory-service", "http://inventory-service/events", SubscriptionType.PUSH, DeliveryGuarantee.AT_LEAST_ONCE),
        ("shipping-sub", topics[3].topic_id, "shipping-service", "http://shipping-service/events", SubscriptionType.PUSH, DeliveryGuarantee.AT_LEAST_ONCE),
        ("notification-sub", topics[4].topic_id, "notification-service", "http://notification-service/events", SubscriptionType.PUSH, DeliveryGuarantee.AT_MOST_ONCE),
        ("analytics-sub", topics[5].topic_id, "analytics-service", "", SubscriptionType.PULL, DeliveryGuarantee.AT_LEAST_ONCE),
        ("reporting-sub", topics[0].topic_id, "reporting-service", "http://reporting-service/events", SubscriptionType.PUSH, DeliveryGuarantee.AT_LEAST_ONCE),
        ("audit-sub", topics[0].topic_id, "audit-service", "http://audit-service/events", SubscriptionType.BROADCAST, DeliveryGuarantee.AT_LEAST_ONCE)
    ]
    
    subscriptions = []
    for name, topic_id, service, endpoint, stype, guarantee in subscriptions_data:
        sub = await platform.create_subscription(name, topic_id, service, endpoint, stype, guarantee)
        if sub:
            subscriptions.append(sub)
            print(f"  📬 {name} ({guarantee.value})")
            
    # Create Aggregates
    print("\n🎯 Creating Aggregates (Event Sourcing)...")
    
    aggregates = []
    for i in range(5):
        agg = await platform.create_aggregate("Order", {"status": "created", "items": []})
        aggregates.append(agg)
        
    print(f"  🎯 Created {len(aggregates)} Order aggregates")
    
    # Publish Events
    print("\n📤 Publishing Events...")
    
    events_data = [
        (topics[0].topic_id, "order.created", {"order_id": "ord-001", "customer_id": "cust-001", "total": 150.00}, "order-service"),
        (topics[0].topic_id, "order.created", {"order_id": "ord-002", "customer_id": "cust-002", "total": 299.99}, "order-service"),
        (topics[1].topic_id, "payment.initiated", {"payment_id": "pay-001", "order_id": "ord-001", "amount": 150.00}, "payment-service"),
        (topics[1].topic_id, "payment.completed", {"payment_id": "pay-001", "order_id": "ord-001", "status": "success"}, "payment-service"),
        (topics[2].topic_id, "inventory.reserved", {"product_id": "prod-001", "quantity": 2, "order_id": "ord-001"}, "inventory-service"),
        (topics[3].topic_id, "shipping.created", {"shipment_id": "ship-001", "order_id": "ord-001"}, "shipping-service"),
        (topics[3].topic_id, "shipping.dispatched", {"shipment_id": "ship-001", "carrier": "FedEx"}, "shipping-service"),
        (topics[4].topic_id, "notification.sent", {"user_id": "cust-001", "type": "order_confirmation"}, "notification-service"),
        (topics[5].topic_id, "page.viewed", {"page": "/products", "user_id": "cust-001"}, "web-app"),
        (topics[5].topic_id, "cart.updated", {"user_id": "cust-001", "items": 3}, "web-app")
    ]
    
    events = []
    for topic_id, event_type, payload, source in events_data:
        event = await platform.publish_event(topic_id, event_type, payload, source)
        if event:
            events.append(event)
            
    print(f"  📤 Published {len(events)} events")
    
    # Apply events to aggregates
    print("\n🔄 Applying Events to Aggregates...")
    
    for i, event in enumerate(events[:3]):
        if i < len(aggregates):
            await platform.apply_event_to_aggregate(aggregates[i].aggregate_id, event)
            
    print(f"  🔄 Applied events to {min(3, len(aggregates))} aggregates")
    
    # Create Snapshots
    for agg in aggregates[:2]:
        await platform.snapshot_aggregate(agg.aggregate_id)
        
    print(f"  📸 Created 2 aggregate snapshots")
    
    # Submit Commands (CQRS)
    print("\n⚡ Submitting Commands (CQRS)...")
    
    commands_data = [
        ("CreateOrderCommand", aggregates[0].aggregate_id, {"items": [{"product": "A", "qty": 1}], "customer": "cust-001"}, "user-001"),
        ("UpdateOrderCommand", aggregates[0].aggregate_id, {"status": "confirmed"}, "user-001"),
        ("CancelOrderCommand", aggregates[1].aggregate_id, {"reason": "Out of stock"}, "system"),
        ("ProcessPaymentCommand", "", {"order_id": "ord-001", "amount": 150.00}, "payment-system"),
        ("ShipOrderCommand", "", {"order_id": "ord-001", "carrier": "FedEx"}, "shipping-system")
    ]
    
    commands = []
    for cmd_type, target, payload, user in commands_data:
        cmd = await platform.submit_command(cmd_type, target, payload, user)
        commands.append(cmd)
        status_icon = "✓" if cmd.status == "completed" else "✗"
        print(f"  {status_icon} {cmd_type}")
        
    # Execute Queries (CQRS)
    print("\n🔍 Executing Queries (CQRS)...")
    
    queries_data = [
        ("GetOrderDetails", {"order_id": "ord-001"}, "user-001"),
        ("ListOrders", {"customer_id": "cust-001", "status": "active"}, "user-001"),
        ("GetOrderHistory", {"customer_id": "cust-001", "limit": 10}, "user-001"),
        ("GetInventoryStatus", {"product_id": "prod-001"}, "system"),
        ("GetShippingStatus", {"order_id": "ord-001"}, "user-001")
    ]
    
    queries = []
    for qry_type, params, user in queries_data:
        qry = await platform.execute_query(qry_type, params, user)
        queries.append(qry)
        print(f"  🔍 {qry_type} ({qry.execution_time_ms:.2f}ms)")
        
    # Start Sagas
    print("\n🎭 Starting Sagas (Orchestration)...")
    
    order_saga = await platform.start_saga(
        "OrderProcessingSaga",
        [
            {"name": "ValidateOrder", "service": "order-service", "compensate": "CancelOrder"},
            {"name": "ReserveInventory", "service": "inventory-service", "compensate": "ReleaseInventory"},
            {"name": "ProcessPayment", "service": "payment-service", "compensate": "RefundPayment"},
            {"name": "CreateShipment", "service": "shipping-service", "compensate": "CancelShipment"},
            {"name": "SendNotification", "service": "notification-service"}
        ],
        {"order_id": "ord-001", "customer_id": "cust-001"}
    )
    
    status_icon = "✓" if order_saga.status == SagaStatus.COMPLETED else "◐" if order_saga.status == SagaStatus.COMPENSATED else "✗"
    print(f"  {status_icon} OrderProcessingSaga: {order_saga.status.value}")
    
    payment_saga = await platform.start_saga(
        "PaymentSaga",
        [
            {"name": "ValidatePayment", "service": "payment-service", "compensate": "VoidPayment"},
            {"name": "ChargeCard", "service": "payment-gateway", "compensate": "RefundCharge"},
            {"name": "UpdateOrder", "service": "order-service"}
        ],
        {"payment_id": "pay-001", "amount": 150.00}
    )
    
    status_icon = "✓" if payment_saga.status == SagaStatus.COMPLETED else "◐" if payment_saga.status == SagaStatus.COMPENSATED else "✗"
    print(f"  {status_icon} PaymentSaga: {payment_saga.status.value}")
    
    # Create Projections
    print("\n📊 Creating Event Projections...")
    
    projections_data = [
        ("OrderSummary", [topics[0].topic_id], "table", "order_summary"),
        ("CustomerOrders", [topics[0].topic_id], "view", "customer_orders_view"),
        ("InventoryLevels", [topics[2].topic_id], "cache", "inventory_cache"),
        ("AnalyticsDashboard", [topics[5].topic_id], "table", "analytics_events")
    ]
    
    projections = []
    for name, source_ids, target_type, target_name in projections_data:
        proj = await platform.create_projection(name, source_ids, target_type, target_name)
        projections.append(proj)
        print(f"  📊 {name} → {target_type}:{target_name}")
        
    # Start Event Replay
    print("\n⏮️ Starting Event Replay...")
    
    replay = await platform.start_replay(
        topics[0].topic_id,
        subscriptions[0].subscription_id,
        datetime.now() - timedelta(hours=1),
        datetime.now()
    )
    
    print(f"  ⏮️ Replayed {replay.replayed_events} events")
    
    # Event Topics Dashboard
    print("\n📨 Event Topics:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                │ Partitions │ Replication │ Retention │ Events │ Subscribers │ Schema                  │ Description                                                                                                              │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for topic in topics:
        name = topic.name[:19].ljust(19)
        parts = str(topic.partitions).ljust(10)
        repl = str(topic.replication_factor).ljust(11)
        ret = f"{topic.retention_hours}h".ljust(9)
        events_count = str(topic.total_events).ljust(6)
        
        subs = [s for s in platform.subscriptions.values() if s.topic_id == topic.topic_id]
        sub_count = str(len(subs)).ljust(11)
        
        schema = platform.schemas.get(topic.schema_id)
        schema_name = schema.name[:23] if schema else "N/A"
        schema_name = schema_name.ljust(23)
        
        desc = topic.description[:122].ljust(122)
        
        print(f"  │ {name} │ {parts} │ {repl} │ {ret} │ {events_count} │ {sub_count} │ {schema_name} │ {desc} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Subscriptions
    print("\n📬 Subscriptions:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                      │ Topic         │ Service                │ Type      │ Guarantee        │ Delivered │ Failed │ Pending │ Status                                                                                     │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for sub in subscriptions:
        name = sub.name[:25].ljust(25)
        
        topic = platform.topics.get(sub.topic_id)
        topic_name = topic.name if topic else "N/A"
        topic_name = topic_name[:13].ljust(13)
        
        service = sub.subscriber_service[:22].ljust(22)
        stype = sub.subscription_type.value[:9].ljust(9)
        guarantee = sub.delivery_guarantee.value[:16].ljust(16)
        delivered = str(sub.delivered_messages).ljust(9)
        failed = str(sub.failed_messages).ljust(6)
        pending = str(sub.pending_messages).ljust(7)
        
        status = "🟢 Active" if sub.is_active else "⚫ Inactive"
        status = status[:92].ljust(92)
        
        print(f"  │ {name} │ {topic_name} │ {service} │ {stype} │ {guarantee} │ {delivered} │ {failed} │ {pending} │ {status} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Recent Events
    print("\n📤 Recent Events:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Event Type               │ Source Service      │ Priority │ Status     │ Retries │ Timestamp            │ Correlation ID                           │ Payload Summary                                                                          │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for event in events[:10]:
        etype = event.event_type[:24].ljust(24)
        source = event.source_service[:19].ljust(19)
        
        priority_icons = {"low": "⬇️", "normal": "➡️", "high": "⬆️", "critical": "🔴"}
        priority = priority_icons.get(event.priority.value, "➡️").ljust(8)
        
        status_icons = {"delivered": "✓", "failed": "✗", "pending": "⏳", "dead_lettered": "💀", "replayed": "⏮️"}
        status_icon = status_icons.get(event.status.value, "?")
        status = f"{status_icon} {event.status.value}"[:10].ljust(10)
        
        retries = str(event.retry_count).ljust(7)
        timestamp = event.timestamp.strftime("%Y-%m-%d %H:%M:%S")[:20].ljust(20)
        corr_id = event.correlation_id[:40].ljust(40)
        
        payload_str = str(event.payload)[:90]
        payload_str = payload_str.ljust(90)
        
        print(f"  │ {etype} │ {source} │ {priority} │ {status} │ {retries} │ {timestamp} │ {corr_id} │ {payload_str} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Commands (CQRS)
    print("\n⚡ Commands (CQRS):")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Command Type               │ Target Aggregate               │ User          │ Status     │ Submitted            │ Processed            │ Result                                                                                       │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for cmd in commands:
        cmd_type = cmd.command_type[:26].ljust(26)
        target = cmd.target_aggregate_id[:30].ljust(30) if cmd.target_aggregate_id else "N/A".ljust(30)
        user = cmd.user_id[:13].ljust(13)
        
        status_icons = {"completed": "✓", "failed": "✗", "pending": "⏳", "processing": "🔄"}
        status_icon = status_icons.get(cmd.status, "?")
        status = f"{status_icon} {cmd.status}"[:10].ljust(10)
        
        submitted = cmd.submitted_at.strftime("%Y-%m-%d %H:%M:%S")[:20].ljust(20)
        processed = cmd.processed_at.strftime("%Y-%m-%d %H:%M:%S") if cmd.processed_at else "N/A"
        processed = processed[:20].ljust(20)
        
        result = str(cmd.result) if cmd.status == "completed" else cmd.error if cmd.error else "N/A"
        result = result[:94].ljust(94)
        
        print(f"  │ {cmd_type} │ {target} │ {user} │ {status} │ {submitted} │ {processed} │ {result} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Sagas
    print("\n🎭 Sagas:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Saga Type                    │ Status       │ Steps │ Current │ Compensated │ Started              │ Completed            │ Context                                                                                                                                                              │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for saga in [order_saga, payment_saga]:
        saga_type = saga.saga_type[:28].ljust(28)
        
        status_icons = {
            "started": "⏳", "running": "🔄", "completed": "✓", 
            "compensating": "↩️", "compensated": "◐", "failed": "✗"
        }
        status_icon = status_icons.get(saga.status.value, "?")
        status = f"{status_icon} {saga.status.value}"[:12].ljust(12)
        
        steps = str(len(saga.steps)).ljust(5)
        current = str(saga.current_step).ljust(7)
        compensated = str(len(saga.compensated_steps)).ljust(11)
        
        started = saga.started_at.strftime("%Y-%m-%d %H:%M:%S")[:20].ljust(20)
        completed = saga.completed_at.strftime("%Y-%m-%d %H:%M:%S") if saga.completed_at else "N/A"
        completed = completed[:20].ljust(20)
        
        context = str(saga.context)[:162]
        context = context.ljust(162)
        
        print(f"  │ {saga_type} │ {status} │ {steps} │ {current} │ {compensated} │ {started} │ {completed} │ {context} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Dead Letter Queue
    print("\n💀 Dead Letter Queue:")
    
    dlq_entries = list(platform.dead_letter_queue.values())[:5]
    if dlq_entries:
        print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
        print("  │ Event Type               │ Subscription        │ Errors │ Status      │ Error Message                                             │")
        print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
        
        for entry in dlq_entries:
            etype = entry.event_type[:24].ljust(24)
            sub_id = entry.subscription_id[:19].ljust(19)
            errors = str(entry.error_count).ljust(6)
            status = entry.status[:11].ljust(11)
            error = entry.error_message[:57].ljust(57)
            
            print(f"  │ {etype} │ {sub_id} │ {errors} │ {status} │ {error} │")
            
        print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    else:
        print("  No entries in Dead Letter Queue")
        
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Topics: {stats['active_topics']}/{stats['total_topics']} active")
    print(f"  Subscriptions: {stats['active_subscriptions']}/{stats['total_subscriptions']} active")
    print(f"  Schemas: {stats['total_schemas']}")
    print(f"  Events: {stats['delivered_events']} delivered, {stats['failed_events']} failed")
    print(f"  Aggregates: {stats['total_aggregates']}")
    print(f"  Commands: {stats['completed_commands']}/{stats['total_commands']} completed")
    print(f"  Queries: {stats['total_queries']}")
    print(f"  Sagas: {stats['completed_sagas']}/{stats['total_sagas']} completed")
    print(f"  DLQ: {stats['pending_dlq']} pending entries")
    print(f"  Projections: {stats['total_projections']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│              Event-Driven Architecture Platform                   │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Active Topics:                {stats['active_topics']:>12}                      │")
    print(f"│ Active Subscriptions:         {stats['active_subscriptions']:>12}                      │")
    print(f"│ Event Schemas:                {stats['total_schemas']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Events Delivered:             {stats['delivered_events']:>12}                      │")
    print(f"│ Events Failed:                {stats['failed_events']:>12}                      │")
    print(f"│ Sagas Completed:              {stats['completed_sagas']:>12}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Event-Driven Architecture Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
