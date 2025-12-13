#!/usr/bin/env python3
"""
Server Init - Iteration 36: Distributed Systems Orchestration
Оркестрация распределённых систем

Функционал:
- Distributed Consensus - распределённый консенсус (Raft)
- Leader Election - выбор лидера
- Distributed Locks - распределённые блокировки
- Service Mesh Control - управление service mesh
- Circuit Breaker Pattern - паттерн Circuit Breaker
- Distributed Tracing - распределённая трассировка
- Event Sourcing - событийное журналирование
- CQRS Pattern - разделение команд и запросов
"""

import json
import asyncio
import hashlib
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Tuple
from enum import Enum
from abc import ABC, abstractmethod
import random
from collections import defaultdict
import uuid
import threading
import heapq


class NodeState(Enum):
    """Состояние узла Raft"""
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"


class CircuitState(Enum):
    """Состояние Circuit Breaker"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class EventType(Enum):
    """Тип события"""
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    STATE_CHANGED = "state_changed"
    COMMAND_EXECUTED = "command_executed"


class TraceStatus(Enum):
    """Статус трассировки"""
    OK = "ok"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class LogEntry:
    """Запись в логе Raft"""
    term: int
    index: int
    command: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RaftNode:
    """Узел Raft кластера"""
    node_id: str
    address: str
    state: NodeState = NodeState.FOLLOWER
    current_term: int = 0
    voted_for: Optional[str] = None
    
    # Log
    log: List[LogEntry] = field(default_factory=list)
    commit_index: int = 0
    last_applied: int = 0
    
    # Leader state
    next_index: Dict[str, int] = field(default_factory=dict)
    match_index: Dict[str, int] = field(default_factory=dict)
    
    # Timing
    last_heartbeat: datetime = field(default_factory=datetime.now)
    election_timeout_ms: int = field(default_factory=lambda: random.randint(150, 300))


@dataclass
class DistributedLock:
    """Распределённая блокировка"""
    lock_id: str
    resource: str
    holder: Optional[str] = None
    acquired_at: Optional[datetime] = None
    ttl_seconds: int = 30
    version: int = 0
    waiters: List[str] = field(default_factory=list)


@dataclass
class ServiceInstance:
    """Экземпляр сервиса"""
    instance_id: str
    service_name: str
    address: str
    port: int
    metadata: Dict[str, str] = field(default_factory=dict)
    health_status: str = "healthy"
    last_health_check: datetime = field(default_factory=datetime.now)
    weight: int = 100


@dataclass
class CircuitBreaker:
    """Circuit Breaker"""
    name: str
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    failure_threshold: int = 5
    success_threshold: int = 3
    timeout_seconds: int = 30
    last_failure_time: Optional[datetime] = None
    last_state_change: datetime = field(default_factory=datetime.now)
    
    # Stats
    total_requests: int = 0
    total_failures: int = 0
    total_successes: int = 0


@dataclass
class Span:
    """Span трассировки"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    service_name: str
    
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_ms: float = 0.0
    
    status: TraceStatus = TraceStatus.OK
    tags: Dict[str, str] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    
    # Baggage (context propagation)
    baggage: Dict[str, str] = field(default_factory=dict)


@dataclass
class Event:
    """Событие для Event Sourcing"""
    event_id: str
    aggregate_id: str
    aggregate_type: str
    event_type: EventType
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    version: int = 1


@dataclass
class Command:
    """Команда CQRS"""
    command_id: str
    command_type: str
    aggregate_id: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Query:
    """Запрос CQRS"""
    query_id: str
    query_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class RaftConsensus:
    """Реализация консенсуса Raft"""
    
    def __init__(self, node_id: str, address: str):
        self.node = RaftNode(node_id=node_id, address=address)
        self.cluster_nodes: Dict[str, str] = {}  # node_id -> address
        self.state_machine: Dict[str, Any] = {}
        self.running = False
        self._lock = threading.Lock()
        self.callbacks: Dict[str, Callable] = {}
        
    def add_node(self, node_id: str, address: str):
        """Добавление узла в кластер"""
        self.cluster_nodes[node_id] = address
        self.node.next_index[node_id] = len(self.node.log) + 1
        self.node.match_index[node_id] = 0
        
    def remove_node(self, node_id: str):
        """Удаление узла из кластера"""
        if node_id in self.cluster_nodes:
            del self.cluster_nodes[node_id]
            
    async def start(self):
        """Запуск узла"""
        self.running = True
        asyncio.create_task(self._election_timer())
        asyncio.create_task(self._heartbeat_timer())
        
    async def stop(self):
        """Остановка узла"""
        self.running = False
        
    async def _election_timer(self):
        """Таймер выборов"""
        while self.running:
            await asyncio.sleep(self.node.election_timeout_ms / 1000)
            
            if self.node.state != NodeState.LEADER:
                elapsed = (datetime.now() - self.node.last_heartbeat).total_seconds() * 1000
                if elapsed >= self.node.election_timeout_ms:
                    await self._start_election()
                    
    async def _heartbeat_timer(self):
        """Таймер heartbeat (для лидера)"""
        while self.running:
            await asyncio.sleep(0.05)  # 50ms
            
            if self.node.state == NodeState.LEADER:
                await self._send_heartbeats()
                
    async def _start_election(self):
        """Начало выборов"""
        with self._lock:
            self.node.state = NodeState.CANDIDATE
            self.node.current_term += 1
            self.node.voted_for = self.node.node_id
            
        votes = 1  # Голос за себя
        
        # Запрос голосов
        for node_id in self.cluster_nodes:
            vote = await self._request_vote(node_id)
            if vote:
                votes += 1
                
        # Проверка кворума
        total_nodes = len(self.cluster_nodes) + 1
        if votes > total_nodes // 2:
            self._become_leader()
        else:
            self.node.state = NodeState.FOLLOWER
            
    async def _request_vote(self, node_id: str) -> bool:
        """Запрос голоса"""
        # Симуляция RPC
        await asyncio.sleep(0.01)
        
        # В реальной реализации - отправка RequestVote RPC
        # Здесь упрощённая логика
        return random.random() > 0.3
        
    def _become_leader(self):
        """Становление лидером"""
        with self._lock:
            self.node.state = NodeState.LEADER
            
            # Инициализация next_index и match_index
            for node_id in self.cluster_nodes:
                self.node.next_index[node_id] = len(self.node.log) + 1
                self.node.match_index[node_id] = 0
                
        if "on_leader_elected" in self.callbacks:
            self.callbacks["on_leader_elected"](self.node.node_id)
            
    async def _send_heartbeats(self):
        """Отправка heartbeat всем followers"""
        for node_id in self.cluster_nodes:
            await self._append_entries(node_id)
            
    async def _append_entries(self, node_id: str) -> bool:
        """AppendEntries RPC"""
        # Симуляция RPC
        await asyncio.sleep(0.005)
        
        # В реальной реализации - отправка AppendEntries
        return True
        
    async def propose(self, command: Dict[str, Any]) -> bool:
        """Предложение команды"""
        if self.node.state != NodeState.LEADER:
            return False
            
        # Добавление в лог
        entry = LogEntry(
            term=self.node.current_term,
            index=len(self.node.log) + 1,
            command=command
        )
        
        with self._lock:
            self.node.log.append(entry)
            
        # Репликация
        successes = 1
        for node_id in self.cluster_nodes:
            if await self._append_entries(node_id):
                successes += 1
                
        # Проверка кворума
        total_nodes = len(self.cluster_nodes) + 1
        if successes > total_nodes // 2:
            self._commit_entry(entry)
            return True
            
        return False
        
    def _commit_entry(self, entry: LogEntry):
        """Коммит записи"""
        with self._lock:
            self.node.commit_index = entry.index
            
            # Применение к state machine
            self._apply_to_state_machine(entry.command)
            self.node.last_applied = entry.index
            
    def _apply_to_state_machine(self, command: Dict[str, Any]):
        """Применение команды к state machine"""
        op = command.get("op")
        key = command.get("key")
        value = command.get("value")
        
        if op == "set":
            self.state_machine[key] = value
        elif op == "delete":
            if key in self.state_machine:
                del self.state_machine[key]
                
    def get_state(self) -> Dict[str, Any]:
        """Получение состояния"""
        return {
            "node_id": self.node.node_id,
            "state": self.node.state.value,
            "term": self.node.current_term,
            "log_length": len(self.node.log),
            "commit_index": self.node.commit_index,
            "state_machine": dict(self.state_machine)
        }


class LeaderElection:
    """Выбор лидера"""
    
    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.current_leader: Optional[str] = None
        self.election_in_progress = False
        self.callbacks: Dict[str, Callable] = {}
        self._lock = threading.Lock()
        
    def register_node(self, node_id: str, priority: int = 100,
                      metadata: Optional[Dict[str, Any]] = None):
        """Регистрация узла"""
        with self._lock:
            self.nodes[node_id] = {
                "id": node_id,
                "priority": priority,
                "metadata": metadata or {},
                "last_heartbeat": datetime.now(),
                "is_healthy": True
            }
            
    def deregister_node(self, node_id: str):
        """Отмена регистрации узла"""
        with self._lock:
            if node_id in self.nodes:
                del self.nodes[node_id]
                
            if self.current_leader == node_id:
                self.current_leader = None
                
    def update_heartbeat(self, node_id: str):
        """Обновление heartbeat"""
        if node_id in self.nodes:
            self.nodes[node_id]["last_heartbeat"] = datetime.now()
            self.nodes[node_id]["is_healthy"] = True
            
    def check_leader_health(self) -> bool:
        """Проверка здоровья лидера"""
        if not self.current_leader:
            return False
            
        leader = self.nodes.get(self.current_leader)
        if not leader:
            return False
            
        elapsed = (datetime.now() - leader["last_heartbeat"]).seconds
        return elapsed < 10  # 10 секунд таймаут
        
    async def elect_leader(self) -> Optional[str]:
        """Выбор нового лидера"""
        with self._lock:
            if self.election_in_progress:
                return self.current_leader
                
            self.election_in_progress = True
            
        try:
            # Маркировка unhealthy узлов
            now = datetime.now()
            for node_id, node in self.nodes.items():
                elapsed = (now - node["last_heartbeat"]).seconds
                node["is_healthy"] = elapsed < 10
                
            # Выбор по приоритету среди здоровых
            healthy_nodes = [
                (node["priority"], node_id)
                for node_id, node in self.nodes.items()
                if node["is_healthy"]
            ]
            
            if not healthy_nodes:
                self.current_leader = None
                return None
                
            # Сортировка по приоритету (больше = лучше)
            healthy_nodes.sort(reverse=True)
            new_leader = healthy_nodes[0][1]
            
            # Смена лидера
            if new_leader != self.current_leader:
                old_leader = self.current_leader
                self.current_leader = new_leader
                
                if "on_leader_change" in self.callbacks:
                    self.callbacks["on_leader_change"](old_leader, new_leader)
                    
            return self.current_leader
            
        finally:
            with self._lock:
                self.election_in_progress = False
                
    def get_leader(self) -> Optional[str]:
        """Получение текущего лидера"""
        return self.current_leader
        
    def is_leader(self, node_id: str) -> bool:
        """Проверка, является ли узел лидером"""
        return self.current_leader == node_id


class DistributedLockManager:
    """Менеджер распределённых блокировок"""
    
    def __init__(self):
        self.locks: Dict[str, DistributedLock] = {}
        self._lock = threading.Lock()
        
    def acquire(self, resource: str, holder: str, 
                ttl_seconds: int = 30,
                wait: bool = True,
                timeout: float = 10.0) -> Optional[str]:
        """Получение блокировки"""
        lock_id = hashlib.md5(resource.encode()).hexdigest()[:16]
        
        start_time = time.time()
        
        while True:
            with self._lock:
                if lock_id not in self.locks:
                    # Создание новой блокировки
                    lock = DistributedLock(
                        lock_id=lock_id,
                        resource=resource,
                        holder=holder,
                        acquired_at=datetime.now(),
                        ttl_seconds=ttl_seconds
                    )
                    self.locks[lock_id] = lock
                    return lock_id
                    
                lock = self.locks[lock_id]
                
                # Проверка истечения
                if lock.acquired_at:
                    elapsed = (datetime.now() - lock.acquired_at).seconds
                    if elapsed >= lock.ttl_seconds:
                        # Блокировка истекла
                        lock.holder = holder
                        lock.acquired_at = datetime.now()
                        lock.ttl_seconds = ttl_seconds
                        lock.version += 1
                        return lock_id
                        
                # Блокировка занята
                if not wait:
                    return None
                    
                # Добавление в очередь ожидания
                if holder not in lock.waiters:
                    lock.waiters.append(holder)
                    
            # Проверка таймаута
            if time.time() - start_time >= timeout:
                return None
                
            time.sleep(0.1)
            
    def release(self, lock_id: str, holder: str) -> bool:
        """Освобождение блокировки"""
        with self._lock:
            if lock_id not in self.locks:
                return False
                
            lock = self.locks[lock_id]
            
            if lock.holder != holder:
                return False
                
            # Передача следующему в очереди
            if lock.waiters:
                next_holder = lock.waiters.pop(0)
                lock.holder = next_holder
                lock.acquired_at = datetime.now()
                lock.version += 1
            else:
                del self.locks[lock_id]
                
            return True
            
    def extend(self, lock_id: str, holder: str, 
               additional_seconds: int) -> bool:
        """Продление блокировки"""
        with self._lock:
            if lock_id not in self.locks:
                return False
                
            lock = self.locks[lock_id]
            
            if lock.holder != holder:
                return False
                
            lock.ttl_seconds += additional_seconds
            return True
            
    def is_locked(self, resource: str) -> bool:
        """Проверка, заблокирован ли ресурс"""
        lock_id = hashlib.md5(resource.encode()).hexdigest()[:16]
        
        with self._lock:
            if lock_id not in self.locks:
                return False
                
            lock = self.locks[lock_id]
            
            if lock.acquired_at:
                elapsed = (datetime.now() - lock.acquired_at).seconds
                if elapsed >= lock.ttl_seconds:
                    return False
                    
            return lock.holder is not None


class CircuitBreakerManager:
    """Менеджер Circuit Breakers"""
    
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
        
    def create_breaker(self, name: str, 
                       failure_threshold: int = 5,
                       success_threshold: int = 3,
                       timeout_seconds: int = 30) -> CircuitBreaker:
        """Создание Circuit Breaker"""
        breaker = CircuitBreaker(
            name=name,
            failure_threshold=failure_threshold,
            success_threshold=success_threshold,
            timeout_seconds=timeout_seconds
        )
        self.breakers[name] = breaker
        return breaker
        
    def get_breaker(self, name: str) -> Optional[CircuitBreaker]:
        """Получение Circuit Breaker"""
        return self.breakers.get(name)
        
    def can_execute(self, name: str) -> bool:
        """Проверка возможности выполнения"""
        breaker = self.breakers.get(name)
        if not breaker:
            return True
            
        if breaker.state == CircuitState.CLOSED:
            return True
            
        if breaker.state == CircuitState.OPEN:
            # Проверка таймаута
            if breaker.last_failure_time:
                elapsed = (datetime.now() - breaker.last_failure_time).seconds
                if elapsed >= breaker.timeout_seconds:
                    self._transition_to_half_open(breaker)
                    return True
            return False
            
        if breaker.state == CircuitState.HALF_OPEN:
            return True
            
        return True
        
    def record_success(self, name: str):
        """Запись успеха"""
        breaker = self.breakers.get(name)
        if not breaker:
            return
            
        breaker.total_requests += 1
        breaker.total_successes += 1
        
        if breaker.state == CircuitState.HALF_OPEN:
            breaker.success_count += 1
            
            if breaker.success_count >= breaker.success_threshold:
                self._transition_to_closed(breaker)
        else:
            breaker.failure_count = 0
            
    def record_failure(self, name: str):
        """Запись ошибки"""
        breaker = self.breakers.get(name)
        if not breaker:
            return
            
        breaker.total_requests += 1
        breaker.total_failures += 1
        breaker.last_failure_time = datetime.now()
        
        if breaker.state == CircuitState.HALF_OPEN:
            self._transition_to_open(breaker)
        else:
            breaker.failure_count += 1
            
            if breaker.failure_count >= breaker.failure_threshold:
                self._transition_to_open(breaker)
                
    def _transition_to_open(self, breaker: CircuitBreaker):
        """Переход в состояние OPEN"""
        breaker.state = CircuitState.OPEN
        breaker.last_state_change = datetime.now()
        breaker.success_count = 0
        
    def _transition_to_half_open(self, breaker: CircuitBreaker):
        """Переход в состояние HALF_OPEN"""
        breaker.state = CircuitState.HALF_OPEN
        breaker.last_state_change = datetime.now()
        breaker.failure_count = 0
        breaker.success_count = 0
        
    def _transition_to_closed(self, breaker: CircuitBreaker):
        """Переход в состояние CLOSED"""
        breaker.state = CircuitState.CLOSED
        breaker.last_state_change = datetime.now()
        breaker.failure_count = 0
        breaker.success_count = 0
        
    async def execute_with_breaker(self, name: str, 
                                    func: Callable,
                                    fallback: Optional[Callable] = None) -> Any:
        """Выполнение с Circuit Breaker"""
        if not self.can_execute(name):
            if fallback:
                return await fallback() if asyncio.iscoroutinefunction(fallback) else fallback()
            raise Exception(f"Circuit breaker {name} is open")
            
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func()
            else:
                result = func()
                
            self.record_success(name)
            return result
            
        except Exception as e:
            self.record_failure(name)
            
            if fallback:
                return await fallback() if asyncio.iscoroutinefunction(fallback) else fallback()
            raise


class DistributedTracer:
    """Распределённая трассировка"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.spans: Dict[str, Span] = {}
        self.traces: Dict[str, List[str]] = defaultdict(list)  # trace_id -> span_ids
        self.exporters: List[Callable] = []
        
    def start_span(self, operation_name: str,
                   parent_span: Optional[Span] = None,
                   trace_id: Optional[str] = None) -> Span:
        """Начало span"""
        if trace_id is None:
            if parent_span:
                trace_id = parent_span.trace_id
            else:
                trace_id = uuid.uuid4().hex
                
        span = Span(
            trace_id=trace_id,
            span_id=uuid.uuid4().hex[:16],
            parent_span_id=parent_span.span_id if parent_span else None,
            operation_name=operation_name,
            service_name=self.service_name
        )
        
        # Копирование baggage из родителя
        if parent_span:
            span.baggage = dict(parent_span.baggage)
            
        self.spans[span.span_id] = span
        self.traces[trace_id].append(span.span_id)
        
        return span
        
    def finish_span(self, span: Span, status: TraceStatus = TraceStatus.OK):
        """Завершение span"""
        span.end_time = datetime.now()
        span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
        span.status = status
        
        # Экспорт
        for exporter in self.exporters:
            try:
                exporter(span)
            except Exception:
                pass
                
    def add_tag(self, span: Span, key: str, value: str):
        """Добавление тега"""
        span.tags[key] = value
        
    def add_log(self, span: Span, message: str, 
                fields: Optional[Dict[str, Any]] = None):
        """Добавление лога"""
        span.logs.append({
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "fields": fields or {}
        })
        
    def set_baggage(self, span: Span, key: str, value: str):
        """Установка baggage (context propagation)"""
        span.baggage[key] = value
        
    def get_trace(self, trace_id: str) -> List[Span]:
        """Получение всех spans трейса"""
        span_ids = self.traces.get(trace_id, [])
        return [self.spans[sid] for sid in span_ids if sid in self.spans]
        
    def add_exporter(self, exporter: Callable):
        """Добавление экспортёра"""
        self.exporters.append(exporter)
        
    def inject_context(self, span: Span) -> Dict[str, str]:
        """Инъекция контекста для propagation"""
        return {
            "trace-id": span.trace_id,
            "span-id": span.span_id,
            "baggage": json.dumps(span.baggage)
        }
        
    def extract_context(self, headers: Dict[str, str]) -> Tuple[Optional[str], Optional[str], Dict[str, str]]:
        """Извлечение контекста"""
        trace_id = headers.get("trace-id")
        parent_span_id = headers.get("span-id")
        baggage = {}
        
        if "baggage" in headers:
            try:
                baggage = json.loads(headers["baggage"])
            except json.JSONDecodeError:
                pass
                
        return trace_id, parent_span_id, baggage


class EventStore:
    """Event Store для Event Sourcing"""
    
    def __init__(self):
        self.events: List[Event] = []
        self.streams: Dict[str, List[int]] = defaultdict(list)  # aggregate_id -> event indices
        self.projections: Dict[str, Callable] = {}
        self.snapshots: Dict[str, Dict[str, Any]] = {}
        
    def append(self, event: Event) -> int:
        """Добавление события"""
        event_index = len(self.events)
        self.events.append(event)
        self.streams[event.aggregate_id].append(event_index)
        
        # Обновление проекций
        for projection_name, projection in self.projections.items():
            try:
                projection(event)
            except Exception:
                pass
                
        return event_index
        
    def get_events(self, aggregate_id: str,
                   from_version: int = 0) -> List[Event]:
        """Получение событий агрегата"""
        indices = self.streams.get(aggregate_id, [])
        events = [self.events[i] for i in indices]
        return [e for e in events if e.version >= from_version]
        
    def get_all_events(self, from_position: int = 0,
                       limit: int = 100) -> List[Event]:
        """Получение всех событий"""
        return self.events[from_position:from_position + limit]
        
    def register_projection(self, name: str, handler: Callable):
        """Регистрация проекции"""
        self.projections[name] = handler
        
    def save_snapshot(self, aggregate_id: str, state: Dict[str, Any],
                      version: int):
        """Сохранение снапшота"""
        self.snapshots[aggregate_id] = {
            "state": state,
            "version": version,
            "timestamp": datetime.now().isoformat()
        }
        
    def get_snapshot(self, aggregate_id: str) -> Optional[Dict[str, Any]]:
        """Получение снапшота"""
        return self.snapshots.get(aggregate_id)
        
    def rebuild_state(self, aggregate_id: str) -> Dict[str, Any]:
        """Восстановление состояния из событий"""
        state = {}
        
        # Загрузка из снапшота если есть
        snapshot = self.get_snapshot(aggregate_id)
        if snapshot:
            state = snapshot["state"].copy()
            from_version = snapshot["version"] + 1
        else:
            from_version = 0
            
        # Применение событий
        events = self.get_events(aggregate_id, from_version)
        for event in events:
            state = self._apply_event(state, event)
            
        return state
        
    def _apply_event(self, state: Dict[str, Any], event: Event) -> Dict[str, Any]:
        """Применение события к состоянию"""
        new_state = state.copy()
        
        if event.event_type == EventType.CREATED:
            new_state.update(event.data)
        elif event.event_type == EventType.UPDATED:
            new_state.update(event.data)
        elif event.event_type == EventType.DELETED:
            new_state["deleted"] = True
        elif event.event_type == EventType.STATE_CHANGED:
            new_state["state"] = event.data.get("new_state")
            
        new_state["version"] = event.version
        
        return new_state


class CQRSHandler:
    """Обработчик CQRS"""
    
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        self.command_handlers: Dict[str, Callable] = {}
        self.query_handlers: Dict[str, Callable] = {}
        self.read_models: Dict[str, Dict[str, Any]] = {}
        
    def register_command_handler(self, command_type: str, handler: Callable):
        """Регистрация обработчика команды"""
        self.command_handlers[command_type] = handler
        
    def register_query_handler(self, query_type: str, handler: Callable):
        """Регистрация обработчика запроса"""
        self.query_handlers[query_type] = handler
        
    async def execute_command(self, command: Command) -> Dict[str, Any]:
        """Выполнение команды"""
        handler = self.command_handlers.get(command.command_type)
        if not handler:
            return {"error": f"Unknown command type: {command.command_type}"}
            
        try:
            # Выполнение обработчика
            events = await handler(command) if asyncio.iscoroutinefunction(handler) else handler(command)
            
            # Сохранение событий
            if isinstance(events, list):
                for event in events:
                    self.event_store.append(event)
            elif isinstance(events, Event):
                self.event_store.append(events)
                
            # Обновление read model
            self._update_read_models(events)
            
            return {
                "success": True,
                "command_id": command.command_id,
                "events_count": len(events) if isinstance(events, list) else 1
            }
            
        except Exception as e:
            return {"error": str(e)}
            
    async def execute_query(self, query: Query) -> Dict[str, Any]:
        """Выполнение запроса"""
        handler = self.query_handlers.get(query.query_type)
        if not handler:
            return {"error": f"Unknown query type: {query.query_type}"}
            
        try:
            result = await handler(query) if asyncio.iscoroutinefunction(handler) else handler(query)
            return {"success": True, "data": result}
            
        except Exception as e:
            return {"error": str(e)}
            
    def _update_read_models(self, events):
        """Обновление read models"""
        if isinstance(events, Event):
            events = [events]
            
        for event in events:
            aggregate_id = event.aggregate_id
            
            if aggregate_id not in self.read_models:
                self.read_models[aggregate_id] = {}
                
            if event.event_type == EventType.CREATED:
                self.read_models[aggregate_id] = event.data.copy()
            elif event.event_type == EventType.UPDATED:
                self.read_models[aggregate_id].update(event.data)
            elif event.event_type == EventType.DELETED:
                if aggregate_id in self.read_models:
                    del self.read_models[aggregate_id]
                    
    def get_read_model(self, aggregate_id: str) -> Optional[Dict[str, Any]]:
        """Получение read model"""
        return self.read_models.get(aggregate_id)


class ServiceMeshController:
    """Контроллер Service Mesh"""
    
    def __init__(self):
        self.services: Dict[str, List[ServiceInstance]] = defaultdict(list)
        self.load_balancing: Dict[str, str] = {}  # service -> strategy
        self.circuit_breakers = CircuitBreakerManager()
        self.retry_policies: Dict[str, Dict[str, Any]] = {}
        self.timeouts: Dict[str, int] = {}  # service -> timeout_ms
        
    def register_instance(self, instance: ServiceInstance):
        """Регистрация экземпляра сервиса"""
        self.services[instance.service_name].append(instance)
        
    def deregister_instance(self, service_name: str, instance_id: str):
        """Отмена регистрации"""
        if service_name in self.services:
            self.services[service_name] = [
                i for i in self.services[service_name]
                if i.instance_id != instance_id
            ]
            
    def configure_load_balancing(self, service_name: str, 
                                  strategy: str = "round_robin"):
        """Настройка load balancing"""
        self.load_balancing[service_name] = strategy
        
    def configure_retry_policy(self, service_name: str,
                                max_retries: int = 3,
                                retry_on: Optional[List[int]] = None):
        """Настройка политики retry"""
        self.retry_policies[service_name] = {
            "max_retries": max_retries,
            "retry_on": retry_on or [502, 503, 504]
        }
        
    def configure_timeout(self, service_name: str, timeout_ms: int):
        """Настройка таймаута"""
        self.timeouts[service_name] = timeout_ms
        
    def select_instance(self, service_name: str) -> Optional[ServiceInstance]:
        """Выбор экземпляра сервиса"""
        instances = self.services.get(service_name, [])
        healthy = [i for i in instances if i.health_status == "healthy"]
        
        if not healthy:
            return None
            
        strategy = self.load_balancing.get(service_name, "round_robin")
        
        if strategy == "round_robin":
            return healthy[int(time.time()) % len(healthy)]
        elif strategy == "random":
            return random.choice(healthy)
        elif strategy == "weighted":
            total_weight = sum(i.weight for i in healthy)
            r = random.randint(1, total_weight)
            for instance in healthy:
                r -= instance.weight
                if r <= 0:
                    return instance
                    
        return healthy[0]
        
    def update_health_status(self, service_name: str, instance_id: str,
                             status: str):
        """Обновление статуса здоровья"""
        for instance in self.services.get(service_name, []):
            if instance.instance_id == instance_id:
                instance.health_status = status
                instance.last_health_check = datetime.now()
                break
                
    def get_mesh_topology(self) -> Dict[str, Any]:
        """Получение топологии mesh"""
        topology = {}
        
        for service_name, instances in self.services.items():
            topology[service_name] = {
                "instances": len(instances),
                "healthy": len([i for i in instances if i.health_status == "healthy"]),
                "load_balancing": self.load_balancing.get(service_name, "round_robin"),
                "timeout_ms": self.timeouts.get(service_name, 5000),
                "retry_policy": self.retry_policies.get(service_name)
            }
            
        return topology


class DistributedOrchestrator:
    """Оркестратор распределённых систем"""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.raft = RaftConsensus(node_id, f"localhost:{5000 + hash(node_id) % 1000}")
        self.leader_election = LeaderElection()
        self.lock_manager = DistributedLockManager()
        self.circuit_breakers = CircuitBreakerManager()
        self.tracer = DistributedTracer(f"orchestrator-{node_id}")
        self.event_store = EventStore()
        self.cqrs = CQRSHandler(self.event_store)
        self.service_mesh = ServiceMeshController()
        
    async def initialize(self):
        """Инициализация оркестратора"""
        # Регистрация узла
        self.leader_election.register_node(self.node_id, priority=100)
        
        # Настройка circuit breakers
        self.circuit_breakers.create_breaker("default", 
                                              failure_threshold=5,
                                              timeout_seconds=30)
                                              
        # Настройка трассировки
        self.tracer.add_exporter(self._log_span)
        
        # Запуск Raft
        await self.raft.start()
        
    def _log_span(self, span: Span):
        """Логирование span"""
        print(f"[TRACE] {span.service_name}:{span.operation_name} "
              f"- {span.duration_ms:.2f}ms - {span.status.value}")
              
    async def execute_distributed_operation(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение распределённой операции"""
        span = self.tracer.start_span(f"execute_{operation.get('type', 'unknown')}")
        
        try:
            # Получение блокировки
            resource = operation.get("resource", "default")
            lock_id = self.lock_manager.acquire(resource, self.node_id)
            
            if not lock_id:
                self.tracer.add_tag(span, "error", "lock_failed")
                return {"error": "Failed to acquire lock"}
                
            try:
                # Выполнение с circuit breaker
                result = await self.circuit_breakers.execute_with_breaker(
                    "default",
                    lambda: self._process_operation(operation)
                )
                
                # Создание события
                event = Event(
                    event_id=uuid.uuid4().hex,
                    aggregate_id=operation.get("aggregate_id", "system"),
                    aggregate_type="operation",
                    event_type=EventType.COMMAND_EXECUTED,
                    data={"operation": operation, "result": result}
                )
                self.event_store.append(event)
                
                self.tracer.add_tag(span, "result", "success")
                return {"success": True, "result": result}
                
            finally:
                self.lock_manager.release(lock_id, self.node_id)
                
        except Exception as e:
            self.tracer.add_tag(span, "error", str(e))
            return {"error": str(e)}
            
        finally:
            self.tracer.finish_span(span)
            
    async def _process_operation(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка операции"""
        await asyncio.sleep(0.1)  # Симуляция
        return {"processed": True, "operation": operation["type"]}
        
    def get_status(self) -> Dict[str, Any]:
        """Получение статуса оркестратора"""
        return {
            "node_id": self.node_id,
            "raft": self.raft.get_state(),
            "is_leader": self.leader_election.is_leader(self.node_id),
            "current_leader": self.leader_election.get_leader(),
            "circuit_breakers": {
                name: {
                    "state": cb.state.value,
                    "failure_count": cb.failure_count,
                    "total_requests": cb.total_requests
                }
                for name, cb in self.circuit_breakers.breakers.items()
            },
            "active_locks": len(self.lock_manager.locks),
            "event_count": len(self.event_store.events),
            "mesh_topology": self.service_mesh.get_mesh_topology()
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 36: Distributed Systems Orchestration")
    print("=" * 60)
    
    async def demo():
        # Создание оркестратора
        orchestrator = DistributedOrchestrator("node_1")
        await orchestrator.initialize()
        
        print("✓ Orchestrator initialized")
        
        # Регистрация сервисов в mesh
        services = [
            ServiceInstance(
                instance_id="api_1",
                service_name="api-gateway",
                address="10.0.0.1",
                port=8080,
                weight=100
            ),
            ServiceInstance(
                instance_id="api_2",
                service_name="api-gateway",
                address="10.0.0.2",
                port=8080,
                weight=100
            ),
            ServiceInstance(
                instance_id="user_1",
                service_name="user-service",
                address="10.0.1.1",
                port=8081,
                weight=100
            )
        ]
        
        for service in services:
            orchestrator.service_mesh.register_instance(service)
            
        print(f"✓ Registered {len(services)} service instances")
        
        # Настройка mesh
        orchestrator.service_mesh.configure_load_balancing("api-gateway", "round_robin")
        orchestrator.service_mesh.configure_timeout("api-gateway", 5000)
        orchestrator.service_mesh.configure_retry_policy("api-gateway", max_retries=3)
        
        print("✓ Service mesh configured")
        
        # Выполнение распределённой операции
        result = await orchestrator.execute_distributed_operation({
            "type": "create_order",
            "resource": "orders",
            "aggregate_id": "order_123",
            "data": {"product": "widget", "quantity": 5}
        })
        print(f"✓ Operation result: {result['success']}")
        
        # Event Sourcing demo
        events = [
            Event(
                event_id=str(uuid.uuid4()),
                aggregate_id="user_1",
                aggregate_type="user",
                event_type=EventType.CREATED,
                data={"name": "John", "email": "john@example.com"},
                version=1
            ),
            Event(
                event_id=str(uuid.uuid4()),
                aggregate_id="user_1",
                aggregate_type="user",
                event_type=EventType.UPDATED,
                data={"email": "john.doe@example.com"},
                version=2
            )
        ]
        
        for event in events:
            orchestrator.event_store.append(event)
            
        state = orchestrator.event_store.rebuild_state("user_1")
        print(f"✓ Rebuilt state: {state}")
        
        # Статус
        status = orchestrator.get_status()
        print(f"\n📊 Orchestrator Status:")
        print(f"   Node ID: {status['node_id']}")
        print(f"   Is Leader: {status['is_leader']}")
        print(f"   Raft State: {status['raft']['state']}")
        print(f"   Event Count: {status['event_count']}")
        print(f"   Active Locks: {status['active_locks']}")
        
        mesh = status['mesh_topology']
        print(f"\n🕸️ Service Mesh:")
        for service, info in mesh.items():
            print(f"   {service}: {info['healthy']}/{info['instances']} healthy")
            
        # Cleanup
        await orchestrator.raft.stop()
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Distributed Systems Orchestration initialized successfully!")
    print("=" * 60)
