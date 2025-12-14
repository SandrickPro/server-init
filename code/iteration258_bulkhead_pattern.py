#!/usr/bin/env python3
"""
Server Init - Iteration 258: Bulkhead Pattern Platform
Платформа изоляции ресурсов по паттерну Bulkhead

Функционал:
- Thread Pool Isolation - изоляция пулов потоков
- Semaphore Isolation - семафорная изоляция
- Resource Partitioning - разделение ресурсов
- Priority Queues - приоритетные очереди
- Fairness Policies - политики справедливости
- Metrics & Monitoring - метрики и мониторинг
- Load Shedding - сброс нагрузки
- Graceful Degradation - постепенная деградация
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Awaitable
from enum import Enum
import uuid


class BulkheadType(Enum):
    """Тип bulkhead"""
    SEMAPHORE = "semaphore"
    THREAD_POOL = "thread_pool"
    QUEUE = "queue"


class BulkheadState(Enum):
    """Состояние bulkhead"""
    NORMAL = "normal"
    DEGRADED = "degraded"
    OVERLOADED = "overloaded"
    CRITICAL = "critical"


class RejectionPolicy(Enum):
    """Политика отклонения"""
    REJECT = "reject"
    QUEUE = "queue"
    DISCARD_OLDEST = "discard_oldest"
    CALLER_RUNS = "caller_runs"


class FairnessPolicy(Enum):
    """Политика справедливости"""
    FIFO = "fifo"
    LIFO = "lifo"
    PRIORITY = "priority"
    WEIGHTED = "weighted"


@dataclass
class BulkheadConfig:
    """Конфигурация bulkhead"""
    config_id: str
    name: str
    
    # Type
    bulkhead_type: BulkheadType = BulkheadType.SEMAPHORE
    
    # Limits
    max_concurrent: int = 10
    max_wait_duration_ms: int = 5000
    queue_size: int = 100
    
    # Policies
    rejection_policy: RejectionPolicy = RejectionPolicy.REJECT
    fairness_policy: FairnessPolicy = FairnessPolicy.FIFO
    
    # Thresholds
    degradation_threshold: float = 70.0  # %
    overload_threshold: float = 90.0  # %
    critical_threshold: float = 98.0  # %
    
    # Priorities
    priority_levels: int = 3
    
    # Timeout
    execution_timeout_ms: int = 30000


@dataclass
class BulkheadMetrics:
    """Метрики bulkhead"""
    # Concurrent
    current_concurrent: int = 0
    max_concurrent_reached: int = 0
    
    # Queue
    queue_size: int = 0
    max_queue_reached: int = 0
    
    # Calls
    total_accepted: int = 0
    total_rejected: int = 0
    total_timed_out: int = 0
    total_completed: int = 0
    
    # Durations
    total_wait_time_ms: float = 0
    total_execution_time_ms: float = 0
    
    # State tracking
    state_changes: int = 0


@dataclass
class QueuedTask:
    """Задача в очереди"""
    task_id: str
    priority: int = 0
    
    # Timing
    queued_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    
    # State
    started: bool = False
    completed: bool = False
    
    # Result
    result: Any = None
    error: Optional[str] = None


@dataclass
class Bulkhead:
    """Bulkhead"""
    bulkhead_id: str
    name: str
    
    # Config
    config: BulkheadConfig = field(default_factory=lambda: BulkheadConfig(
        config_id="default",
        name="default"
    ))
    
    # State
    state: BulkheadState = BulkheadState.NORMAL
    
    # Semaphore (real asyncio semaphore created in manager)
    semaphore: Optional[asyncio.Semaphore] = None
    
    # Current state
    current_concurrent: int = 0
    
    # Queue
    queue: List[QueuedTask] = field(default_factory=list)
    
    # Metrics
    metrics: BulkheadMetrics = field(default_factory=BulkheadMetrics)
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    last_state_change: datetime = field(default_factory=datetime.now)


@dataclass
class ExecutionResult:
    """Результат выполнения"""
    result_id: str
    bulkhead_name: str
    
    # Timing
    wait_time_ms: float = 0
    execution_time_ms: float = 0
    
    # Result
    success: bool = True
    result: Any = None
    error: Optional[str] = None
    
    # State
    was_queued: bool = False
    was_rejected: bool = False


class BulkheadManager:
    """Менеджер bulkhead"""
    
    def __init__(self):
        self.bulkheads: Dict[str, Bulkhead] = {}
        self.configs: Dict[str, BulkheadConfig] = {}
        
    def create_config(self, name: str,
                     bulkhead_type: BulkheadType = BulkheadType.SEMAPHORE,
                     max_concurrent: int = 10,
                     max_wait_duration_ms: int = 5000,
                     queue_size: int = 100) -> BulkheadConfig:
        """Создание конфигурации"""
        config = BulkheadConfig(
            config_id=f"cfg_{uuid.uuid4().hex[:8]}",
            name=name,
            bulkhead_type=bulkhead_type,
            max_concurrent=max_concurrent,
            max_wait_duration_ms=max_wait_duration_ms,
            queue_size=queue_size
        )
        
        self.configs[name] = config
        return config
        
    def create_bulkhead(self, name: str, config_name: str = None) -> Bulkhead:
        """Создание bulkhead"""
        config = self.configs.get(config_name or name)
        if not config:
            config = BulkheadConfig(
                config_id=f"cfg_{uuid.uuid4().hex[:8]}",
                name=name
            )
            
        bulkhead = Bulkhead(
            bulkhead_id=f"bh_{uuid.uuid4().hex[:8]}",
            name=name,
            config=config,
            semaphore=asyncio.Semaphore(config.max_concurrent)
        )
        
        self.bulkheads[name] = bulkhead
        return bulkhead
        
    def _update_state(self, bulkhead: Bulkhead):
        """Обновление состояния"""
        config = bulkhead.config
        utilization = (bulkhead.current_concurrent / config.max_concurrent) * 100
        
        old_state = bulkhead.state
        
        if utilization >= config.critical_threshold:
            bulkhead.state = BulkheadState.CRITICAL
        elif utilization >= config.overload_threshold:
            bulkhead.state = BulkheadState.OVERLOADED
        elif utilization >= config.degradation_threshold:
            bulkhead.state = BulkheadState.DEGRADED
        else:
            bulkhead.state = BulkheadState.NORMAL
            
        if old_state != bulkhead.state:
            bulkhead.last_state_change = datetime.now()
            bulkhead.metrics.state_changes += 1
            
    def _can_accept(self, bulkhead: Bulkhead) -> bool:
        """Проверка возможности принятия"""
        config = bulkhead.config
        
        # Check concurrent limit
        if bulkhead.current_concurrent < config.max_concurrent:
            return True
            
        # Check queue if policy allows
        if config.rejection_policy in [RejectionPolicy.QUEUE, RejectionPolicy.DISCARD_OLDEST]:
            if len(bulkhead.queue) < config.queue_size:
                return True
                
        return False
        
    async def execute(self, bulkhead_name: str,
                     operation: Callable[..., Awaitable[Any]],
                     priority: int = 0,
                     *args, **kwargs) -> ExecutionResult:
        """Выполнение операции через bulkhead"""
        bulkhead = self.bulkheads.get(bulkhead_name)
        if not bulkhead:
            bulkhead = self.create_bulkhead(bulkhead_name)
            
        config = bulkhead.config
        result = ExecutionResult(
            result_id=f"res_{uuid.uuid4().hex[:8]}",
            bulkhead_name=bulkhead_name
        )
        
        start_time = datetime.now()
        
        # Check if we can accept
        if bulkhead.current_concurrent >= config.max_concurrent:
            if config.rejection_policy == RejectionPolicy.REJECT:
                result.was_rejected = True
                result.success = False
                result.error = "Bulkhead limit exceeded"
                bulkhead.metrics.total_rejected += 1
                return result
                
            elif config.rejection_policy == RejectionPolicy.QUEUE:
                if len(bulkhead.queue) >= config.queue_size:
                    result.was_rejected = True
                    result.success = False
                    result.error = "Queue full"
                    bulkhead.metrics.total_rejected += 1
                    return result
                    
                # Queue the task
                task = QueuedTask(
                    task_id=f"task_{uuid.uuid4().hex[:8]}",
                    priority=priority,
                    deadline=datetime.now() + timedelta(milliseconds=config.max_wait_duration_ms)
                )
                bulkhead.queue.append(task)
                result.was_queued = True
                
                # Wait for slot
                waited = 0
                while bulkhead.current_concurrent >= config.max_concurrent:
                    if waited >= config.max_wait_duration_ms:
                        bulkhead.queue.remove(task)
                        result.success = False
                        result.error = "Wait timeout"
                        bulkhead.metrics.total_timed_out += 1
                        return result
                    await asyncio.sleep(0.01)
                    waited += 10
                    
                bulkhead.queue.remove(task)
                
        # Acquire slot
        wait_end = datetime.now()
        result.wait_time_ms = (wait_end - start_time).total_seconds() * 1000
        bulkhead.metrics.total_wait_time_ms += result.wait_time_ms
        
        bulkhead.current_concurrent += 1
        bulkhead.metrics.total_accepted += 1
        
        if bulkhead.current_concurrent > bulkhead.metrics.max_concurrent_reached:
            bulkhead.metrics.max_concurrent_reached = bulkhead.current_concurrent
            
        bulkhead.metrics.current_concurrent = bulkhead.current_concurrent
        bulkhead.metrics.queue_size = len(bulkhead.queue)
        
        self._update_state(bulkhead)
        
        try:
            exec_start = datetime.now()
            
            # Execute with timeout
            operation_result = await asyncio.wait_for(
                operation(*args, **kwargs),
                timeout=config.execution_timeout_ms / 1000
            )
            
            result.result = operation_result
            result.success = True
            
        except asyncio.TimeoutError:
            result.success = False
            result.error = "Execution timeout"
            bulkhead.metrics.total_timed_out += 1
            
        except Exception as e:
            result.success = False
            result.error = str(e)
            
        finally:
            bulkhead.current_concurrent -= 1
            bulkhead.metrics.current_concurrent = bulkhead.current_concurrent
            bulkhead.metrics.total_completed += 1
            
            exec_end = datetime.now()
            result.execution_time_ms = (exec_end - wait_end).total_seconds() * 1000
            bulkhead.metrics.total_execution_time_ms += result.execution_time_ms
            
            self._update_state(bulkhead)
            
        return result
        
    def get_utilization(self, bulkhead_name: str) -> float:
        """Получение утилизации"""
        bulkhead = self.bulkheads.get(bulkhead_name)
        if not bulkhead:
            return 0.0
        return (bulkhead.current_concurrent / bulkhead.config.max_concurrent) * 100
        
    def get_metrics(self, bulkhead_name: str) -> Optional[BulkheadMetrics]:
        """Получение метрик"""
        bulkhead = self.bulkheads.get(bulkhead_name)
        return bulkhead.metrics if bulkhead else None
        
    def resize(self, bulkhead_name: str, new_max_concurrent: int):
        """Изменение размера"""
        bulkhead = self.bulkheads.get(bulkhead_name)
        if bulkhead:
            bulkhead.config.max_concurrent = new_max_concurrent
            bulkhead.semaphore = asyncio.Semaphore(new_max_concurrent)
            
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_accepted = 0
        total_rejected = 0
        total_queued = 0
        states = {state: 0 for state in BulkheadState}
        
        for bulkhead in self.bulkheads.values():
            total_accepted += bulkhead.metrics.total_accepted
            total_rejected += bulkhead.metrics.total_rejected
            total_queued += len(bulkhead.queue)
            states[bulkhead.state] += 1
            
        return {
            "bulkheads_total": len(self.bulkheads),
            "total_accepted": total_accepted,
            "total_rejected": total_rejected,
            "total_queued": total_queued,
            "states": {s.value: c for s, c in states.items()}
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 258: Bulkhead Pattern Platform")
    print("=" * 60)
    
    manager = BulkheadManager()
    print("✓ Bulkhead Manager created")
    
    # Create configurations
    print("\n⚙️ Creating Configurations...")
    
    configs_data = [
        ("api-gateway", BulkheadType.SEMAPHORE, 5, 3000, 20),
        ("database-pool", BulkheadType.THREAD_POOL, 10, 5000, 50),
        ("external-service", BulkheadType.QUEUE, 3, 10000, 100),
    ]
    
    for name, bh_type, max_conc, max_wait, queue_size in configs_data:
        config = manager.create_config(name, bh_type, max_conc, max_wait, queue_size)
        print(f"  ⚙️ {name}: type={bh_type.value}, max={max_conc}, queue={queue_size}")
        
    # Create bulkheads
    print("\n🛡️ Creating Bulkheads...")
    
    for config_name in ["api-gateway", "database-pool", "external-service"]:
        bulkhead = manager.create_bulkhead(config_name, config_name)
        print(f"  🛡️ {bulkhead.name}: state={bulkhead.state.value}")
        
    # Test operations
    async def api_request(request_id: int):
        await asyncio.sleep(random.uniform(0.1, 0.3))
        if random.random() < 0.1:
            raise Exception("Request failed")
        return {"request_id": request_id, "status": "success"}
        
    async def db_query(query_id: int):
        await asyncio.sleep(random.uniform(0.05, 0.15))
        return {"query_id": query_id, "rows": random.randint(1, 100)}
        
    # Execute concurrent operations
    print("\n🔄 Executing Operations...")
    
    # API Gateway test - many concurrent requests
    print("\n  API Gateway (5 max concurrent):")
    
    api_tasks = []
    for i in range(15):
        task = asyncio.create_task(
            manager.execute("api-gateway", api_request, i % 3, i)
        )
        api_tasks.append(task)
        
    api_results = await asyncio.gather(*api_tasks)
    
    accepted = sum(1 for r in api_results if not r.was_rejected and r.success)
    rejected = sum(1 for r in api_results if r.was_rejected)
    print(f"    Accepted: {accepted}, Rejected: {rejected}")
    
    # Database pool test
    print("\n  Database Pool (10 max concurrent):")
    
    db_tasks = []
    for i in range(20):
        task = asyncio.create_task(
            manager.execute("database-pool", db_query, 0, i)
        )
        db_tasks.append(task)
        
    db_results = await asyncio.gather(*db_tasks)
    
    accepted = sum(1 for r in db_results if not r.was_rejected and r.success)
    avg_exec = sum(r.execution_time_ms for r in db_results) / len(db_results)
    print(f"    Completed: {accepted}, Avg Execution: {avg_exec:.1f}ms")
    
    # Display bulkheads
    print("\n🛡️ Bulkhead Status:")
    
    print("\n  ┌─────────────────┬─────────────┬──────────┬──────────┬──────────┬──────────┐")
    print("  │ Bulkhead        │ Type        │ Current  │ Max      │ Queue    │ State    │")
    print("  ├─────────────────┼─────────────┼──────────┼──────────┼──────────┼──────────┤")
    
    for bulkhead in manager.bulkheads.values():
        name = bulkhead.name[:15].ljust(15)
        bh_type = bulkhead.config.bulkhead_type.value[:11].ljust(11)
        current = str(bulkhead.current_concurrent)[:8].ljust(8)
        max_conc = str(bulkhead.config.max_concurrent)[:8].ljust(8)
        queue = str(len(bulkhead.queue))[:8].ljust(8)
        state = bulkhead.state.value[:8].ljust(8)
        
        print(f"  │ {name} │ {bh_type} │ {current} │ {max_conc} │ {queue} │ {state} │")
        
    print("  └─────────────────┴─────────────┴──────────┴──────────┴──────────┴──────────┘")
    
    # Metrics
    print("\n📊 Bulkhead Metrics:")
    
    print("\n  ┌─────────────────┬──────────┬──────────┬──────────┬────────────┬────────────┐")
    print("  │ Bulkhead        │ Accepted │ Rejected │ Timeout  │ Wait(ms)   │ Exec(ms)   │")
    print("  ├─────────────────┼──────────┼──────────┼──────────┼────────────┼────────────┤")
    
    for bulkhead in manager.bulkheads.values():
        metrics = bulkhead.metrics
        name = bulkhead.name[:15].ljust(15)
        accepted = str(metrics.total_accepted)[:8].ljust(8)
        rejected = str(metrics.total_rejected)[:8].ljust(8)
        timeout = str(metrics.total_timed_out)[:8].ljust(8)
        avg_wait = f"{metrics.total_wait_time_ms / max(1, metrics.total_accepted):.1f}"[:10].ljust(10)
        avg_exec = f"{metrics.total_execution_time_ms / max(1, metrics.total_completed):.1f}"[:10].ljust(10)
        
        print(f"  │ {name} │ {accepted} │ {rejected} │ {timeout} │ {avg_wait} │ {avg_exec} │")
        
    print("  └─────────────────┴──────────┴──────────┴──────────┴────────────┴────────────┘")
    
    # Utilization
    print("\n📊 Utilization:")
    
    for name, bulkhead in manager.bulkheads.items():
        utilization = manager.get_utilization(name)
        bar_filled = int(utilization / 10)
        bar = "█" * bar_filled + "░" * (10 - bar_filled)
        
        state_icon = {
            BulkheadState.NORMAL: "🟢",
            BulkheadState.DEGRADED: "🟡",
            BulkheadState.OVERLOADED: "🟠",
            BulkheadState.CRITICAL: "🔴"
        }.get(bulkhead.state, "⚪")
        
        print(f"  {state_icon} {name:20s} [{bar}] {utilization:.1f}%")
        
    # State distribution
    print("\n📊 State Distribution:")
    
    for state in BulkheadState:
        count = sum(1 for b in manager.bulkheads.values() if b.state == state)
        bar = "█" * count + "░" * (5 - count)
        print(f"  {state.value:12s} [{bar}] {count}")
        
    # Configuration summary
    print("\n⚙️ Configurations:")
    
    print("\n  ┌─────────────────┬─────────────┬──────────┬──────────┬───────────────┐")
    print("  │ Config          │ Type        │ Max Conc │ Queue    │ Reject Policy │")
    print("  ├─────────────────┼─────────────┼──────────┼──────────┼───────────────┤")
    
    for config in manager.configs.values():
        name = config.name[:15].ljust(15)
        bh_type = config.bulkhead_type.value[:11].ljust(11)
        max_conc = str(config.max_concurrent)[:8].ljust(8)
        queue = str(config.queue_size)[:8].ljust(8)
        policy = config.rejection_policy.value[:13].ljust(13)
        
        print(f"  │ {name} │ {bh_type} │ {max_conc} │ {queue} │ {policy} │")
        
    print("  └─────────────────┴─────────────┴──────────┴──────────┴───────────────┘")
    
    # Statistics
    print("\n📊 Manager Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Bulkheads Total: {stats['bulkheads_total']}")
    print(f"  Total Accepted: {stats['total_accepted']}")
    print(f"  Total Rejected: {stats['total_rejected']}")
    print(f"  Currently Queued: {stats['total_queued']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Bulkhead Pattern Dashboard                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Bulkheads:                     {stats['bulkheads_total']:>12}                        │")
    print(f"│ Total Accepted:                {stats['total_accepted']:>12}                        │")
    print(f"│ Total Rejected:                {stats['total_rejected']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    
    for state, count in stats['states'].items():
        state_str = f"│ {state.title()}: {count:>3}                                                       │"
        print(state_str[:69] + "│")
        
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Bulkhead Pattern Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
