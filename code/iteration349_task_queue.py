#!/usr/bin/env python3
"""
Server Init - Iteration 349: Task Queue Platform
Платформа очередей задач

Функционал:
- Task Definitions - определения задач
- Task Queues - очереди задач
- Worker Pools - пулы воркеров
- Task Routing - маршрутизация задач
- Task Results - результаты задач
- Dead Letter Queues - очереди ошибок
- Rate Limiting - ограничение скорости
- Task Chaining - цепочки задач
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
import uuid
import json


class TaskState(Enum):
    """Состояние задачи"""
    PENDING = "pending"
    RECEIVED = "received"
    STARTED = "started"
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"
    REVOKED = "revoked"


class QueueType(Enum):
    """Тип очереди"""
    DEFAULT = "default"
    PRIORITY = "priority"
    DELAY = "delay"
    DEAD_LETTER = "dead_letter"


class WorkerState(Enum):
    """Состояние воркера"""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    HEARTBEAT_MISS = "heartbeat_miss"


class RouteType(Enum):
    """Тип маршрутизации"""
    DIRECT = "direct"
    ROUND_ROBIN = "round_robin"
    BROADCAST = "broadcast"
    CONTENT_BASED = "content_based"


class ResultBackend(Enum):
    """Бэкенд результатов"""
    MEMORY = "memory"
    REDIS = "redis"
    DATABASE = "database"
    AMQP = "amqp"


class RateLimitAlgorithm(Enum):
    """Алгоритм ограничения скорости"""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"


@dataclass
class TaskDefinition:
    """Определение задачи"""
    task_id: str
    name: str
    
    # Function
    func_name: str = ""
    module: str = ""
    
    # Queue
    queue_name: str = "default"
    
    # Routing
    routing_key: str = ""
    
    # Timing
    soft_time_limit: int = 300
    hard_time_limit: int = 600
    
    # Retry
    max_retries: int = 3
    retry_delay: int = 60
    retry_backoff: bool = True
    
    # Rate Limit
    rate_limit: str = ""  # e.g., "100/m", "1000/h"
    
    # Acks
    acks_late: bool = False
    reject_on_worker_lost: bool = True
    
    # Result
    ignore_result: bool = False
    result_expires: int = 3600
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Active
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Task:
    """Задача"""
    task_instance_id: str
    task_def_id: str
    
    # State
    state: TaskState = TaskState.PENDING
    
    # Arguments
    args: List[Any] = field(default_factory=list)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    
    # Worker
    worker_id: str = ""
    
    # Retry
    retries: int = 0
    
    # Priority
    priority: int = 5
    
    # ETA
    eta: Optional[datetime] = None
    
    # Expiration
    expires: Optional[datetime] = None
    
    # Parent
    parent_id: str = ""
    root_id: str = ""
    
    # Correlation
    correlation_id: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    received_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class TaskResult:
    """Результат задачи"""
    result_id: str
    task_instance_id: str
    
    # State
    state: TaskState = TaskState.PENDING
    
    # Result
    result: Any = None
    
    # Error
    exception: str = ""
    traceback: str = ""
    
    # Timing
    runtime: float = 0.0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


@dataclass
class Queue:
    """Очередь"""
    queue_id: str
    name: str
    
    # Type
    queue_type: QueueType = QueueType.DEFAULT
    
    # Exchange
    exchange: str = ""
    routing_key: str = ""
    
    # Messages
    message_count: int = 0
    consumer_count: int = 0
    
    # Configuration
    durable: bool = True
    auto_delete: bool = False
    max_length: int = 0
    max_priority: int = 10
    
    # Dead Letter
    dead_letter_exchange: str = ""
    dead_letter_routing_key: str = ""
    
    # TTL
    message_ttl: int = 0
    
    # Stats
    messages_delivered: int = 0
    messages_acknowledged: int = 0
    messages_rejected: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Worker:
    """Воркер"""
    worker_id: str
    hostname: str
    
    # State
    state: WorkerState = WorkerState.ONLINE
    
    # Queues
    queues: List[str] = field(default_factory=list)
    
    # Concurrency
    concurrency: int = 4
    active_tasks: int = 0
    
    # Prefetch
    prefetch_count: int = 4
    
    # Pool
    pool_type: str = "prefork"  # prefork, eventlet, gevent, solo
    
    # Stats
    tasks_processed: int = 0
    tasks_succeeded: int = 0
    tasks_failed: int = 0
    
    # Resources
    cpu_load: float = 0.0
    memory_mb: int = 0
    
    # Heartbeat
    last_heartbeat: datetime = field(default_factory=datetime.now)
    heartbeat_interval: int = 30
    
    # Timestamps
    registered_at: datetime = field(default_factory=datetime.now)


@dataclass
class WorkerPool:
    """Пул воркеров"""
    pool_id: str
    name: str
    
    # Workers
    worker_ids: List[str] = field(default_factory=list)
    
    # Configuration
    min_workers: int = 1
    max_workers: int = 10
    
    # Auto-scaling
    autoscale_enabled: bool = False
    scale_up_threshold: float = 0.8
    scale_down_threshold: float = 0.2
    
    # Queues
    queues: List[str] = field(default_factory=list)
    
    # Stats
    current_workers: int = 0
    active_tasks: int = 0
    pending_tasks: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Route:
    """Маршрут"""
    route_id: str
    name: str
    
    # Type
    route_type: RouteType = RouteType.DIRECT
    
    # Pattern
    task_pattern: str = ""  # e.g., "myapp.tasks.*"
    
    # Queue
    queue_name: str = "default"
    
    # Exchange
    exchange: str = ""
    routing_key: str = ""
    
    # Priority
    priority: int = 0
    
    # Options
    options: Dict[str, Any] = field(default_factory=dict)
    
    # Active
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RateLimit:
    """Ограничение скорости"""
    limit_id: str
    
    # Target
    task_def_id: str = ""
    queue_name: str = ""
    
    # Limit
    algorithm: RateLimitAlgorithm = RateLimitAlgorithm.TOKEN_BUCKET
    requests_per_second: float = 100.0
    burst_size: int = 100
    
    # Window
    window_size_seconds: int = 60
    
    # Current
    current_tokens: float = 100.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    # Stats
    allowed_count: int = 0
    rejected_count: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TaskChain:
    """Цепочка задач"""
    chain_id: str
    name: str
    
    # Tasks
    task_ids: List[str] = field(default_factory=list)
    
    # State
    current_index: int = 0
    is_completed: bool = False
    
    # Options
    options: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class DeadLetterEntry:
    """Запись в dead letter"""
    entry_id: str
    task_instance_id: str
    
    # Original
    original_queue: str = ""
    
    # Reason
    reason: str = ""
    exception: str = ""
    
    # Retry
    retries_exhausted: bool = False
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class QueueMetrics:
    """Метрики очереди"""
    metrics_id: str
    queue_name: str
    
    # Messages
    messages_enqueued: int = 0
    messages_dequeued: int = 0
    messages_rejected: int = 0
    
    # Latency
    avg_wait_time_ms: float = 0.0
    max_wait_time_ms: float = 0.0
    
    # Throughput
    throughput_per_second: float = 0.0
    
    # Queue depth
    current_depth: int = 0
    max_depth: int = 0
    
    # Timestamps
    collected_at: datetime = field(default_factory=datetime.now)


class TaskQueuePlatform:
    """Платформа очередей задач"""
    
    def __init__(self, result_backend: ResultBackend = ResultBackend.MEMORY):
        self.task_definitions: Dict[str, TaskDefinition] = {}
        self.tasks: Dict[str, Task] = {}
        self.results: Dict[str, TaskResult] = {}
        self.queues: Dict[str, Queue] = {}
        self.workers: Dict[str, Worker] = {}
        self.worker_pools: Dict[str, WorkerPool] = {}
        self.routes: Dict[str, Route] = {}
        self.rate_limits: Dict[str, RateLimit] = {}
        self.chains: Dict[str, TaskChain] = {}
        self.dead_letters: Dict[str, DeadLetterEntry] = {}
        self.metrics: Dict[str, QueueMetrics] = {}
        
        self.result_backend = result_backend
        
        # Queue buffers
        self.queue_buffers: Dict[str, List[str]] = {}
        
    async def create_queue(self, name: str,
                          queue_type: QueueType = QueueType.DEFAULT,
                          exchange: str = "",
                          routing_key: str = "",
                          durable: bool = True,
                          max_length: int = 0,
                          max_priority: int = 10,
                          message_ttl: int = 0) -> Queue:
        """Создание очереди"""
        queue = Queue(
            queue_id=f"q_{uuid.uuid4().hex[:8]}",
            name=name,
            queue_type=queue_type,
            exchange=exchange,
            routing_key=routing_key or name,
            durable=durable,
            max_length=max_length,
            max_priority=max_priority,
            message_ttl=message_ttl
        )
        
        self.queues[queue.queue_id] = queue
        self.queue_buffers[name] = []
        
        return queue
        
    async def register_worker(self, hostname: str,
                             queues: List[str],
                             concurrency: int = 4,
                             prefetch_count: int = 4,
                             pool_type: str = "prefork") -> Worker:
        """Регистрация воркера"""
        worker = Worker(
            worker_id=f"w_{uuid.uuid4().hex[:8]}",
            hostname=hostname,
            queues=queues,
            concurrency=concurrency,
            prefetch_count=prefetch_count,
            pool_type=pool_type
        )
        
        self.workers[worker.worker_id] = worker
        
        # Update queue consumer count
        for q_name in queues:
            queue = self._find_queue_by_name(q_name)
            if queue:
                queue.consumer_count += 1
                
        return worker
        
    def _find_queue_by_name(self, name: str) -> Optional[Queue]:
        """Поиск очереди по имени"""
        for q in self.queues.values():
            if q.name == name:
                return q
        return None
        
    async def create_worker_pool(self, name: str,
                                queues: List[str],
                                min_workers: int = 1,
                                max_workers: int = 10,
                                autoscale_enabled: bool = False) -> WorkerPool:
        """Создание пула воркеров"""
        pool = WorkerPool(
            pool_id=f"pool_{uuid.uuid4().hex[:8]}",
            name=name,
            queues=queues,
            min_workers=min_workers,
            max_workers=max_workers,
            autoscale_enabled=autoscale_enabled
        )
        
        self.worker_pools[pool.pool_id] = pool
        return pool
        
    async def define_task(self, name: str,
                         func_name: str,
                         module: str = "",
                         queue_name: str = "default",
                         soft_time_limit: int = 300,
                         hard_time_limit: int = 600,
                         max_retries: int = 3,
                         retry_delay: int = 60,
                         rate_limit: str = "",
                         ignore_result: bool = False,
                         tags: List[str] = None) -> TaskDefinition:
        """Определение задачи"""
        task_def = TaskDefinition(
            task_id=f"task_{uuid.uuid4().hex[:8]}",
            name=name,
            func_name=func_name,
            module=module,
            queue_name=queue_name,
            soft_time_limit=soft_time_limit,
            hard_time_limit=hard_time_limit,
            max_retries=max_retries,
            retry_delay=retry_delay,
            rate_limit=rate_limit,
            ignore_result=ignore_result,
            tags=tags or []
        )
        
        self.task_definitions[task_def.task_id] = task_def
        
        # Set up rate limit if specified
        if rate_limit:
            await self._setup_rate_limit(task_def)
            
        return task_def
        
    async def _setup_rate_limit(self, task_def: TaskDefinition):
        """Настройка ограничения скорости"""
        # Parse rate limit string (e.g., "100/m")
        parts = task_def.rate_limit.split("/")
        if len(parts) == 2:
            count = int(parts[0])
            period = parts[1]
            
            if period == "s":
                rps = float(count)
            elif period == "m":
                rps = count / 60.0
            elif period == "h":
                rps = count / 3600.0
            else:
                rps = 100.0
                
            limit = RateLimit(
                limit_id=f"rl_{uuid.uuid4().hex[:8]}",
                task_def_id=task_def.task_id,
                requests_per_second=rps,
                burst_size=count
            )
            
            self.rate_limits[limit.limit_id] = limit
            
    async def add_route(self, name: str,
                       task_pattern: str,
                       queue_name: str,
                       route_type: RouteType = RouteType.DIRECT,
                       priority: int = 0) -> Route:
        """Добавление маршрута"""
        route = Route(
            route_id=f"route_{uuid.uuid4().hex[:8]}",
            name=name,
            route_type=route_type,
            task_pattern=task_pattern,
            queue_name=queue_name,
            priority=priority
        )
        
        self.routes[route.route_id] = route
        return route
        
    async def send_task(self, task_def_id: str,
                       args: List[Any] = None,
                       kwargs: Dict[str, Any] = None,
                       priority: int = 5,
                       eta: datetime = None,
                       expires: datetime = None,
                       correlation_id: str = "") -> Optional[Task]:
        """Отправка задачи"""
        task_def = self.task_definitions.get(task_def_id)
        if not task_def or not task_def.is_active:
            return None
            
        # Check rate limit
        if not await self._check_rate_limit(task_def_id):
            return None
            
        task = Task(
            task_instance_id=f"ti_{uuid.uuid4().hex[:12]}",
            task_def_id=task_def_id,
            args=args or [],
            kwargs=kwargs or {},
            priority=priority,
            eta=eta,
            expires=expires,
            correlation_id=correlation_id or str(uuid.uuid4())
        )
        
        self.tasks[task.task_instance_id] = task
        
        # Find queue
        queue_name = self._route_task(task_def)
        
        # Add to queue
        if queue_name in self.queue_buffers:
            self.queue_buffers[queue_name].append(task.task_instance_id)
            
            queue = self._find_queue_by_name(queue_name)
            if queue:
                queue.message_count += 1
                
        # Dispatch to worker
        await self._dispatch_task(task, queue_name)
        
        return task
        
    def _route_task(self, task_def: TaskDefinition) -> str:
        """Маршрутизация задачи"""
        # Check routes
        for route in sorted(self.routes.values(), key=lambda r: -r.priority):
            if route.is_active and self._match_pattern(task_def.name, route.task_pattern):
                return route.queue_name
                
        return task_def.queue_name
        
    def _match_pattern(self, task_name: str, pattern: str) -> bool:
        """Проверка соответствия паттерну"""
        if pattern.endswith("*"):
            return task_name.startswith(pattern[:-1])
        return task_name == pattern
        
    async def _check_rate_limit(self, task_def_id: str) -> bool:
        """Проверка ограничения скорости"""
        for rl in self.rate_limits.values():
            if rl.task_def_id == task_def_id:
                # Token bucket algorithm
                now = datetime.now()
                elapsed = (now - rl.last_updated).total_seconds()
                
                # Add tokens
                rl.current_tokens = min(
                    rl.burst_size,
                    rl.current_tokens + elapsed * rl.requests_per_second
                )
                rl.last_updated = now
                
                if rl.current_tokens >= 1:
                    rl.current_tokens -= 1
                    rl.allowed_count += 1
                    return True
                else:
                    rl.rejected_count += 1
                    return False
                    
        return True
        
    async def _dispatch_task(self, task: Task, queue_name: str):
        """Отправка задачи воркеру"""
        # Find available worker
        worker = await self._find_available_worker(queue_name)
        if not worker:
            return
            
        # Update task
        task.state = TaskState.RECEIVED
        task.received_at = datetime.now()
        task.worker_id = worker.worker_id
        
        # Update worker
        worker.active_tasks += 1
        worker.state = WorkerState.BUSY
        
        # Execute
        await self._execute_task(task, worker)
        
    async def _find_available_worker(self, queue_name: str) -> Optional[Worker]:
        """Поиск доступного воркера"""
        for worker in self.workers.values():
            if worker.state == WorkerState.OFFLINE:
                continue
            if queue_name not in worker.queues:
                continue
            if worker.active_tasks >= worker.concurrency:
                continue
            return worker
        return None
        
    async def _execute_task(self, task: Task, worker: Worker):
        """Выполнение задачи"""
        task_def = self.task_definitions.get(task.task_def_id)
        if not task_def:
            return
            
        # Update state
        task.state = TaskState.STARTED
        task.started_at = datetime.now()
        
        # Simulate execution
        success = random.random() > 0.15  # 85% success
        runtime = random.uniform(0.1, 30.0)
        
        # Create result
        result = TaskResult(
            result_id=f"res_{uuid.uuid4().hex[:8]}",
            task_instance_id=task.task_instance_id,
            runtime=runtime
        )
        
        if success:
            task.state = TaskState.SUCCESS
            result.state = TaskState.SUCCESS
            result.result = f"Task {task_def.name} completed"
            
            worker.tasks_succeeded += 1
        else:
            if task.retries < task_def.max_retries:
                task.state = TaskState.RETRY
                task.retries += 1
                result.state = TaskState.RETRY
            else:
                task.state = TaskState.FAILURE
                result.state = TaskState.FAILURE
                result.exception = "MaxRetriesExceededError"
                result.traceback = "Task exceeded max retries"
                
                # Add to dead letter
                await self._add_to_dead_letter(task, "Max retries exceeded")
                
                worker.tasks_failed += 1
                
        task.completed_at = datetime.now()
        result.expires_at = datetime.now() + timedelta(seconds=task_def.result_expires)
        
        # Update worker
        worker.active_tasks = max(0, worker.active_tasks - 1)
        worker.tasks_processed += 1
        if worker.active_tasks == 0:
            worker.state = WorkerState.ONLINE
            
        # Update queue
        queue = self._find_queue_by_name(task_def.queue_name)
        if queue:
            queue.message_count = max(0, queue.message_count - 1)
            queue.messages_delivered += 1
            if success:
                queue.messages_acknowledged += 1
            else:
                queue.messages_rejected += 1
                
        # Store result
        if not task_def.ignore_result:
            self.results[result.result_id] = result
            
        # Handle retry
        if task.state == TaskState.RETRY:
            await asyncio.sleep(0.01)  # Simulated delay
            await self._dispatch_task(task, task_def.queue_name)
            
    async def _add_to_dead_letter(self, task: Task, reason: str):
        """Добавление в dead letter"""
        task_def = self.task_definitions.get(task.task_def_id)
        
        entry = DeadLetterEntry(
            entry_id=f"dl_{uuid.uuid4().hex[:8]}",
            task_instance_id=task.task_instance_id,
            original_queue=task_def.queue_name if task_def else "",
            reason=reason,
            retries_exhausted=True
        )
        
        self.dead_letters[entry.entry_id] = entry
        
    async def create_chain(self, name: str, task_def_ids: List[str]) -> TaskChain:
        """Создание цепочки задач"""
        chain = TaskChain(
            chain_id=f"chain_{uuid.uuid4().hex[:8]}",
            name=name,
            task_ids=task_def_ids
        )
        
        self.chains[chain.chain_id] = chain
        return chain
        
    async def execute_chain(self, chain_id: str,
                           initial_args: List[Any] = None) -> Optional[List[Task]]:
        """Выполнение цепочки"""
        chain = self.chains.get(chain_id)
        if not chain:
            return None
            
        tasks = []
        current_args = initial_args or []
        
        for task_def_id in chain.task_ids:
            task = await self.send_task(task_def_id, args=current_args)
            if task:
                tasks.append(task)
                chain.current_index += 1
                
        chain.is_completed = True
        chain.completed_at = datetime.now()
        
        return tasks
        
    async def revoke_task(self, task_instance_id: str) -> bool:
        """Отмена задачи"""
        task = self.tasks.get(task_instance_id)
        if not task or task.state not in [TaskState.PENDING, TaskState.RECEIVED]:
            return False
            
        task.state = TaskState.REVOKED
        task.completed_at = datetime.now()
        
        return True
        
    async def worker_heartbeat(self, worker_id: str) -> bool:
        """Heartbeat воркера"""
        worker = self.workers.get(worker_id)
        if not worker:
            return False
            
        worker.last_heartbeat = datetime.now()
        return True
        
    async def get_task_result(self, task_instance_id: str) -> Optional[TaskResult]:
        """Получение результата задачи"""
        for result in self.results.values():
            if result.task_instance_id == task_instance_id:
                return result
        return None
        
    async def collect_metrics(self, queue_name: str) -> Optional[QueueMetrics]:
        """Сбор метрик"""
        queue = self._find_queue_by_name(queue_name)
        if not queue:
            return None
            
        metrics = QueueMetrics(
            metrics_id=f"met_{uuid.uuid4().hex[:8]}",
            queue_name=queue_name,
            messages_enqueued=queue.messages_delivered,
            messages_dequeued=queue.messages_acknowledged,
            messages_rejected=queue.messages_rejected,
            current_depth=queue.message_count,
            max_depth=max(queue.message_count, queue.messages_delivered // 10)
        )
        
        # Calculate throughput
        metrics.throughput_per_second = random.uniform(10, 100)
        metrics.avg_wait_time_ms = random.uniform(1, 100)
        metrics.max_wait_time_ms = random.uniform(100, 1000)
        
        self.metrics[metrics.metrics_id] = metrics
        return metrics
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_tasks_def = len(self.task_definitions)
        active_tasks_def = sum(1 for t in self.task_definitions.values() if t.is_active)
        
        total_tasks = len(self.tasks)
        pending_tasks = sum(1 for t in self.tasks.values() if t.state == TaskState.PENDING)
        running_tasks = sum(1 for t in self.tasks.values() if t.state == TaskState.STARTED)
        success_tasks = sum(1 for t in self.tasks.values() if t.state == TaskState.SUCCESS)
        failed_tasks = sum(1 for t in self.tasks.values() if t.state == TaskState.FAILURE)
        
        total_workers = len(self.workers)
        online_workers = sum(1 for w in self.workers.values() if w.state == WorkerState.ONLINE)
        busy_workers = sum(1 for w in self.workers.values() if w.state == WorkerState.BUSY)
        
        total_queues = len(self.queues)
        total_messages = sum(q.message_count for q in self.queues.values())
        
        dead_letters = len(self.dead_letters)
        
        return {
            "total_task_definitions": total_tasks_def,
            "active_task_definitions": active_tasks_def,
            "total_tasks": total_tasks,
            "pending_tasks": pending_tasks,
            "running_tasks": running_tasks,
            "success_tasks": success_tasks,
            "failed_tasks": failed_tasks,
            "total_workers": total_workers,
            "online_workers": online_workers,
            "busy_workers": busy_workers,
            "total_queues": total_queues,
            "total_messages": total_messages,
            "dead_letters": dead_letters
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 349: Task Queue Platform")
    print("=" * 60)
    
    platform = TaskQueuePlatform(result_backend=ResultBackend.MEMORY)
    print("✓ Task Queue Platform initialized")
    
    # Create Queues
    print("\n📦 Creating Queues...")
    
    queues_data = [
        ("celery", QueueType.DEFAULT, "celery", True, 0, 10),
        ("priority", QueueType.PRIORITY, "priority", True, 0, 10),
        ("email", QueueType.DEFAULT, "email", True, 10000, 5),
        ("reports", QueueType.DEFAULT, "reports", True, 1000, 5),
        ("notifications", QueueType.DEFAULT, "notifications", True, 50000, 3),
        ("analytics", QueueType.DEFAULT, "analytics", True, 0, 5),
        ("dead-letter", QueueType.DEAD_LETTER, "dead-letter", True, 0, 1)
    ]
    
    queues = []
    for name, qtype, exchange, durable, max_len, max_prio in queues_data:
        q = await platform.create_queue(name, qtype, exchange, "", durable, max_len, max_prio)
        queues.append(q)
        print(f"  📦 {name} ({qtype.value})")
        
    # Create Worker Pools
    print("\n👷 Creating Worker Pools...")
    
    pools_data = [
        ("default-pool", ["celery", "priority"], 2, 8, True),
        ("email-pool", ["email"], 1, 4, False),
        ("reports-pool", ["reports"], 1, 2, False),
        ("analytics-pool", ["analytics"], 2, 6, True)
    ]
    
    pools = []
    for name, q_list, min_w, max_w, auto in pools_data:
        p = await platform.create_worker_pool(name, q_list, min_w, max_w, auto)
        pools.append(p)
        print(f"  👷 {name} (min: {min_w}, max: {max_w})")
        
    # Register Workers
    print("\n🖥️ Registering Workers...")
    
    workers_data = [
        ("worker-001@host1", ["celery", "priority"], 8, 8, "prefork"),
        ("worker-002@host1", ["celery"], 8, 8, "prefork"),
        ("worker-003@host2", ["celery", "email"], 4, 4, "prefork"),
        ("worker-004@host2", ["email", "notifications"], 4, 4, "prefork"),
        ("worker-005@host3", ["reports"], 2, 2, "prefork"),
        ("worker-006@host3", ["analytics"], 8, 8, "gevent"),
        ("worker-007@host4", ["celery", "priority"], 16, 16, "eventlet"),
        ("worker-008@host4", ["notifications"], 8, 8, "gevent")
    ]
    
    workers = []
    for hostname, q_list, conc, prefetch, pool in workers_data:
        w = await platform.register_worker(hostname, q_list, conc, prefetch, pool)
        workers.append(w)
        print(f"  🖥️ {hostname} ({conc} workers, {pool})")
        
    # Define Tasks
    print("\n📋 Defining Tasks...")
    
    tasks_data = [
        ("send_email", "send_email", "app.tasks.email", "email", 60, 120, 5, 30, "100/m", False, ["email", "notification"]),
        ("generate_report", "generate_report", "app.tasks.reports", "reports", 300, 600, 3, 60, "", False, ["reports"]),
        ("process_payment", "process_payment", "app.tasks.payments", "priority", 30, 60, 3, 10, "50/s", False, ["payments", "critical"]),
        ("send_notification", "send_notification", "app.tasks.notifications", "notifications", 10, 30, 5, 5, "1000/s", True, ["notifications"]),
        ("update_analytics", "update_analytics", "app.tasks.analytics", "analytics", 120, 300, 2, 30, "", False, ["analytics"]),
        ("process_webhook", "process_webhook", "app.tasks.webhooks", "celery", 30, 60, 3, 10, "200/s", False, ["webhooks"]),
        ("cleanup_temp", "cleanup_temp", "app.tasks.maintenance", "celery", 60, 120, 1, 60, "", True, ["maintenance"]),
        ("sync_data", "sync_data", "app.tasks.sync", "celery", 600, 1200, 2, 120, "10/m", False, ["sync", "data"]),
        ("send_sms", "send_sms", "app.tasks.sms", "priority", 30, 60, 5, 10, "50/s", False, ["sms", "notification"]),
        ("generate_invoice", "generate_invoice", "app.tasks.billing", "reports", 120, 300, 3, 30, "", False, ["billing", "reports"])
    ]
    
    task_defs = []
    for name, func, mod, queue, soft, hard, retries, delay, rate, ignore, tags in tasks_data:
        t = await platform.define_task(name, func, mod, queue, soft, hard, retries, delay, rate, ignore, tags)
        task_defs.append(t)
        print(f"  📋 {name} ({queue})")
        
    # Add Routes
    print("\n🔀 Adding Routes...")
    
    routes_data = [
        ("email-route", "app.tasks.email.*", "email", RouteType.DIRECT, 10),
        ("report-route", "app.tasks.reports.*", "reports", RouteType.DIRECT, 10),
        ("payment-route", "app.tasks.payments.*", "priority", RouteType.DIRECT, 20),
        ("analytics-route", "app.tasks.analytics.*", "analytics", RouteType.ROUND_ROBIN, 5)
    ]
    
    routes = []
    for name, pattern, queue, rtype, prio in routes_data:
        r = await platform.add_route(name, pattern, queue, rtype, prio)
        routes.append(r)
        print(f"  🔀 {name} -> {queue}")
        
    # Create Task Chains
    print("\n⛓️ Creating Task Chains...")
    
    # Payment flow chain
    chain1 = await platform.create_chain("payment-flow", [
        task_defs[2].task_id,  # process_payment
        task_defs[0].task_id,  # send_email
        task_defs[3].task_id   # send_notification
    ])
    print(f"  ⛓️ payment-flow (3 tasks)")
    
    # Report generation chain
    chain2 = await platform.create_chain("report-generation", [
        task_defs[4].task_id,  # update_analytics
        task_defs[1].task_id,  # generate_report
        task_defs[0].task_id   # send_email
    ])
    print(f"  ⛓️ report-generation (3 tasks)")
    
    # Send Tasks
    print("\n📤 Sending Tasks...")
    
    tasks = []
    
    # Send multiple tasks
    for task_def in task_defs:
        for _ in range(random.randint(3, 8)):
            args = [f"arg{random.randint(1, 100)}"]
            kwargs = {"user_id": random.randint(1000, 9999)}
            priority = random.randint(1, 10)
            
            t = await platform.send_task(
                task_def.task_id,
                args=args,
                kwargs=kwargs,
                priority=priority
            )
            if t:
                tasks.append(t)
                
    print(f"  📤 Sent {len(tasks)} tasks")
    
    # Execute Chain
    print("\n⛓️ Executing Chains...")
    
    chain_tasks = await platform.execute_chain(chain1.chain_id, ["payment_123"])
    print(f"  ⛓️ Executed payment-flow ({len(chain_tasks) if chain_tasks else 0} tasks)")
    
    # Collect Metrics
    print("\n📊 Collecting Metrics...")
    
    metrics = []
    for q in queues[:5]:
        m = await platform.collect_metrics(q.name)
        if m:
            metrics.append(m)
            
    print(f"  📊 Collected metrics for {len(metrics)} queues")
    
    # Task Definitions Dashboard
    print("\n📋 Task Definitions:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                    │ Queue          │ Module                     │ Soft TL │ Hard TL │ Retries │ Rate Limit │ Ignore │ Tags                                                                                                                                          │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for td in task_defs:
        name = td.name[:23].ljust(23)
        queue = td.queue_name[:14].ljust(14)
        module = td.module[:26].ljust(26)
        soft = f"{td.soft_time_limit}s".ljust(7)
        hard = f"{td.hard_time_limit}s".ljust(7)
        retries = str(td.max_retries).ljust(7)
        rate = td.rate_limit[:10] if td.rate_limit else "N/A"
        rate = rate.ljust(10)
        ignore = "Yes" if td.ignore_result else "No"
        ignore = ignore.ljust(6)
        tags = ", ".join(td.tags)[:134]
        tags = tags.ljust(134)
        
        print(f"  │ {name} │ {queue} │ {module} │ {soft} │ {hard} │ {retries} │ {rate} │ {ignore} │ {tags} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Queues Dashboard
    print("\n📦 Queues:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                │ Type         │ Messages │ Consumers │ Delivered │ Acknowledged │ Rejected │ Durable │ Max Length │ Max Priority                                                                                                                                    │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for q in queues:
        name = q.name[:19].ljust(19)
        qtype = q.queue_type.value[:12].ljust(12)
        msgs = str(q.message_count).ljust(8)
        consumers = str(q.consumer_count).ljust(9)
        delivered = str(q.messages_delivered).ljust(9)
        acked = str(q.messages_acknowledged).ljust(12)
        rejected = str(q.messages_rejected).ljust(8)
        durable = "Yes" if q.durable else "No"
        durable = durable.ljust(7)
        max_len = str(q.max_length) if q.max_length > 0 else "∞"
        max_len = max_len[:10].ljust(10)
        max_prio = str(q.max_priority).ljust(132)
        
        print(f"  │ {name} │ {qtype} │ {msgs} │ {consumers} │ {delivered} │ {acked} │ {rejected} │ {durable} │ {max_len} │ {max_prio} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Workers Dashboard
    print("\n🖥️ Workers:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Hostname                    │ State   │ Pool      │ Concur │ Active │ Prefetch │ Processed │ Success │ Failed │ Last Heartbeat                                                                                                                                                                                                │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for w in workers:
        hostname = w.hostname[:27].ljust(27)
        
        state_icons = {"online": "🟢", "offline": "⚫", "busy": "🟡", "heartbeat_miss": "🟠"}
        state_icon = state_icons.get(w.state.value, "?")
        state = f"{state_icon}".ljust(7)
        
        pool = w.pool_type[:9].ljust(9)
        conc = str(w.concurrency).ljust(6)
        active = str(w.active_tasks).ljust(6)
        prefetch = str(w.prefetch_count).ljust(8)
        processed = str(w.tasks_processed).ljust(9)
        success = str(w.tasks_succeeded).ljust(7)
        failed = str(w.tasks_failed).ljust(6)
        hb = w.last_heartbeat.strftime("%Y-%m-%d %H:%M:%S")[:176].ljust(176)
        
        print(f"  │ {hostname} │ {state} │ {pool} │ {conc} │ {active} │ {prefetch} │ {processed} │ {success} │ {failed} │ {hb} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Recent Tasks Dashboard
    print("\n📤 Recent Tasks:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Task ID                 │ Name                    │ State    │ Worker                      │ Retries │ Priority │ Created              │ Started              │ Completed                                                                                                                                                                  │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for t in list(tasks)[:12]:
        task_id = t.task_instance_id[:23].ljust(23)
        
        task_def = platform.task_definitions.get(t.task_def_id)
        name = task_def.name if task_def else "Unknown"
        name = name[:23].ljust(23)
        
        state_icons = {"pending": "⏳", "received": "📥", "started": "🔄", "success": "✅", "failure": "❌", "retry": "🔁", "revoked": "⚫"}
        state_icon = state_icons.get(t.state.value, "?")
        state = f"{state_icon} {t.state.value}"[:8].ljust(8)
        
        worker = platform.workers.get(t.worker_id)
        worker_name = worker.hostname if worker else "N/A"
        worker_name = worker_name[:27].ljust(27)
        
        retries = str(t.retries).ljust(7)
        prio = str(t.priority).ljust(8)
        created = t.created_at.strftime("%Y-%m-%d %H:%M:%S")[:20].ljust(20)
        started = t.started_at.strftime("%Y-%m-%d %H:%M:%S") if t.started_at else "N/A"
        started = started[:20].ljust(20)
        completed = t.completed_at.strftime("%Y-%m-%d %H:%M:%S") if t.completed_at else "N/A"
        completed = completed[:164].ljust(164)
        
        print(f"  │ {task_id} │ {name} │ {state} │ {worker_name} │ {retries} │ {prio} │ {created} │ {started} │ {completed} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Queue Metrics
    print("\n📊 Queue Metrics:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Queue               │ Enqueued │ Dequeued │ Rejected │ Depth │ Max Depth │ Throughput/s │ Avg Wait (ms) │ Max Wait (ms)                                                                                                                             │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for m in metrics:
        queue = m.queue_name[:19].ljust(19)
        enqueued = str(m.messages_enqueued).ljust(8)
        dequeued = str(m.messages_dequeued).ljust(8)
        rejected = str(m.messages_rejected).ljust(8)
        depth = str(m.current_depth).ljust(5)
        max_depth = str(m.max_depth).ljust(9)
        throughput = f"{m.throughput_per_second:.1f}".ljust(12)
        avg_wait = f"{m.avg_wait_time_ms:.1f}".ljust(13)
        max_wait = f"{m.max_wait_time_ms:.1f}".ljust(125)
        
        print(f"  │ {queue} │ {enqueued} │ {dequeued} │ {rejected} │ {depth} │ {max_depth} │ {throughput} │ {avg_wait} │ {max_wait} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Rate Limits
    print("\n⏱️ Rate Limits:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Task                    │ Algorithm      │ RPS       │ Burst │ Tokens │ Allowed │ Rejected                                                                                                              │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for rl in platform.rate_limits.values():
        task_def = platform.task_definitions.get(rl.task_def_id)
        task_name = task_def.name if task_def else "Unknown"
        task_name = task_name[:23].ljust(23)
        
        algo = rl.algorithm.value[:14].ljust(14)
        rps = f"{rl.requests_per_second:.1f}".ljust(9)
        burst = str(rl.burst_size).ljust(5)
        tokens = f"{rl.current_tokens:.1f}".ljust(6)
        allowed = str(rl.allowed_count).ljust(7)
        rejected = str(rl.rejected_count).ljust(116)
        
        print(f"  │ {task_name} │ {algo} │ {rps} │ {burst} │ {tokens} │ {allowed} │ {rejected} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Dead Letters
    dead_letters = list(platform.dead_letters.values())[:5]
    
    print("\n💀 Dead Letter Queue:")
    
    if dead_letters:
        print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
        print("  │ Entry ID              │ Task ID                 │ Original Queue   │ Reason                              │ Retries Exhausted │ Created                                                                                             │")
        print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
        
        for dl in dead_letters:
            entry_id = dl.entry_id[:21].ljust(21)
            task_id = dl.task_instance_id[:23].ljust(23)
            orig_queue = dl.original_queue[:16].ljust(16)
            reason = dl.reason[:35].ljust(35)
            exhausted = "Yes" if dl.retries_exhausted else "No"
            exhausted = exhausted.ljust(17)
            created = dl.created_at.strftime("%Y-%m-%d %H:%M:%S")[:101].ljust(101)
            
            print(f"  │ {entry_id} │ {task_id} │ {orig_queue} │ {reason} │ {exhausted} │ {created} │")
            
        print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    else:
        print("  No dead letter entries")
        
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Task Definitions: {stats['active_task_definitions']}/{stats['total_task_definitions']} active")
    print(f"  Tasks: {stats['pending_tasks']} pending, {stats['running_tasks']} running, {stats['success_tasks']} success, {stats['failed_tasks']} failed")
    print(f"  Workers: {stats['online_workers']} online, {stats['busy_workers']} busy")
    print(f"  Queues: {stats['total_queues']} ({stats['total_messages']} messages)")
    print(f"  Dead Letters: {stats['dead_letters']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                       Task Queue Platform                          │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Task Definitions:             {stats['active_task_definitions']:>12}                      │")
    print(f"│ Total Tasks:                  {stats['total_tasks']:>12}                      │")
    print(f"│ Total Workers:                {stats['total_workers']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Pending Tasks:                {stats['pending_tasks']:>12}                      │")
    print(f"│ Success Tasks:                {stats['success_tasks']:>12}                      │")
    print(f"│ Failed Tasks:                 {stats['failed_tasks']:>12}                      │")
    print(f"│ Dead Letters:                 {stats['dead_letters']:>12}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Task Queue Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
