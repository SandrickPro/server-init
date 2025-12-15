#!/usr/bin/env python3
"""
Server Init - Iteration 348: Job Scheduler Platform
Платформа планировщика заданий

Функционал:
- Cron Jobs - задания по расписанию
- Job Dependencies - зависимости заданий
- Job Queues - очереди заданий
- Worker Management - управление воркерами
- Job Retries - повторные попытки
- Job Priorities - приоритеты заданий
- Resource Allocation - распределение ресурсов
- Job Monitoring - мониторинг заданий
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import json


class JobStatus(Enum):
    """Статус задания"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    RETRY = "retry"


class JobType(Enum):
    """Тип задания"""
    SCHEDULED = "scheduled"
    TRIGGERED = "triggered"
    DEPENDENT = "dependent"
    RECURRING = "recurring"
    IMMEDIATE = "immediate"


class TriggerType(Enum):
    """Тип триггера"""
    CRON = "cron"
    INTERVAL = "interval"
    DATE = "date"
    EVENT = "event"
    MANUAL = "manual"


class WorkerStatus(Enum):
    """Статус воркера"""
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"
    DRAINING = "draining"


class QueueStatus(Enum):
    """Статус очереди"""
    ACTIVE = "active"
    PAUSED = "paused"
    DRAINING = "draining"


class Priority(Enum):
    """Приоритет"""
    LOW = 1
    NORMAL = 5
    HIGH = 7
    CRITICAL = 10


@dataclass
class JobDefinition:
    """Определение задания"""
    job_def_id: str
    name: str
    
    # Type
    job_type: JobType = JobType.SCHEDULED
    
    # Command
    command: str = ""
    arguments: List[str] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)
    
    # Trigger
    trigger_type: TriggerType = TriggerType.CRON
    trigger_config: Dict[str, Any] = field(default_factory=dict)
    cron_expression: str = ""
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)
    
    # Queue
    queue_name: str = "default"
    
    # Priority
    priority: Priority = Priority.NORMAL
    
    # Timeout
    timeout_seconds: int = 3600
    
    # Retry
    max_retries: int = 3
    retry_delay_seconds: int = 60
    
    # Resources
    cpu_limit: float = 1.0
    memory_limit_mb: int = 512
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Status
    is_enabled: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


@dataclass
class JobInstance:
    """Экземпляр задания"""
    job_instance_id: str
    job_def_id: str
    
    # Status
    status: JobStatus = JobStatus.PENDING
    
    # Worker
    worker_id: str = ""
    
    # Execution
    exit_code: int = 0
    output: str = ""
    error: str = ""
    
    # Retry
    attempt: int = 1
    
    # Resources used
    cpu_used: float = 0.0
    memory_used_mb: int = 0
    
    # Duration
    duration_seconds: float = 0.0
    
    # Timestamps
    scheduled_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class Schedule:
    """Расписание"""
    schedule_id: str
    job_def_id: str
    
    # Trigger
    trigger_type: TriggerType = TriggerType.CRON
    cron_expression: str = ""
    interval_seconds: int = 0
    run_at: Optional[datetime] = None
    
    # Next run
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None
    
    # Status
    is_active: bool = True
    
    # Runs
    run_count: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class JobQueue:
    """Очередь заданий"""
    queue_id: str
    name: str
    
    # Status
    status: QueueStatus = QueueStatus.ACTIVE
    
    # Configuration
    max_concurrent: int = 10
    priority_enabled: bool = True
    
    # Stats
    pending_jobs: int = 0
    running_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    
    # Workers
    worker_ids: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Worker:
    """Воркер"""
    worker_id: str
    name: str
    
    # Status
    status: WorkerStatus = WorkerStatus.IDLE
    
    # Host
    hostname: str = ""
    ip_address: str = ""
    
    # Queues
    queue_names: List[str] = field(default_factory=list)
    
    # Capacity
    max_concurrent_jobs: int = 4
    current_jobs: int = 0
    
    # Resources
    cpu_total: float = 4.0
    cpu_available: float = 4.0
    memory_total_mb: int = 8192
    memory_available_mb: int = 8192
    
    # Stats
    jobs_processed: int = 0
    jobs_failed: int = 0
    
    # Heartbeat
    last_heartbeat: datetime = field(default_factory=datetime.now)
    
    # Timestamps
    registered_at: datetime = field(default_factory=datetime.now)


@dataclass
class JobDependency:
    """Зависимость задания"""
    dependency_id: str
    job_def_id: str
    depends_on_job_def_id: str
    
    # Type
    dependency_type: str = "success"  # success, completion, failure
    
    # Condition
    condition: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class JobExecution:
    """Выполнение задания"""
    execution_id: str
    job_instance_id: str
    
    # Output
    stdout: str = ""
    stderr: str = ""
    
    # Exit
    exit_code: int = 0
    
    # Resources
    peak_cpu: float = 0.0
    peak_memory_mb: int = 0
    
    # Timestamps
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None


@dataclass
class ResourcePool:
    """Пул ресурсов"""
    pool_id: str
    name: str
    
    # Capacity
    total_cpu: float = 100.0
    available_cpu: float = 100.0
    total_memory_mb: int = 102400
    available_memory_mb: int = 102400
    
    # Workers
    worker_ids: List[str] = field(default_factory=list)
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class JobMetrics:
    """Метрики задания"""
    metrics_id: str
    job_def_id: str
    
    # Counts
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    
    # Duration
    avg_duration_seconds: float = 0.0
    min_duration_seconds: float = 0.0
    max_duration_seconds: float = 0.0
    
    # Resources
    avg_cpu_used: float = 0.0
    avg_memory_mb: int = 0
    
    # Success rate
    success_rate: float = 0.0
    
    # Timestamp
    collected_at: datetime = field(default_factory=datetime.now)


@dataclass
class Alert:
    """Оповещение"""
    alert_id: str
    
    # Type
    alert_type: str = ""  # job_failed, job_timeout, worker_offline, queue_full
    
    # Source
    job_def_id: str = ""
    job_instance_id: str = ""
    worker_id: str = ""
    queue_id: str = ""
    
    # Message
    message: str = ""
    severity: str = "warning"  # info, warning, error, critical
    
    # Status
    is_resolved: bool = False
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


class JobScheduler:
    """Планировщик заданий"""
    
    def __init__(self):
        self.job_definitions: Dict[str, JobDefinition] = {}
        self.job_instances: Dict[str, JobInstance] = {}
        self.schedules: Dict[str, Schedule] = {}
        self.queues: Dict[str, JobQueue] = {}
        self.workers: Dict[str, Worker] = {}
        self.dependencies: Dict[str, JobDependency] = {}
        self.executions: Dict[str, JobExecution] = {}
        self.resource_pools: Dict[str, ResourcePool] = {}
        self.metrics: Dict[str, JobMetrics] = {}
        self.alerts: Dict[str, Alert] = {}
        
        # Job queue buffers
        self.pending_jobs: Dict[str, List[str]] = {}  # queue_name -> job_instance_ids
        
    async def create_queue(self, name: str,
                          max_concurrent: int = 10,
                          priority_enabled: bool = True) -> JobQueue:
        """Создание очереди"""
        queue = JobQueue(
            queue_id=f"queue_{uuid.uuid4().hex[:8]}",
            name=name,
            max_concurrent=max_concurrent,
            priority_enabled=priority_enabled
        )
        
        self.queues[queue.queue_id] = queue
        self.pending_jobs[name] = []
        return queue
        
    async def register_worker(self, name: str,
                             hostname: str,
                             ip_address: str,
                             queue_names: List[str],
                             max_concurrent_jobs: int = 4,
                             cpu_total: float = 4.0,
                             memory_total_mb: int = 8192) -> Worker:
        """Регистрация воркера"""
        worker = Worker(
            worker_id=f"worker_{uuid.uuid4().hex[:8]}",
            name=name,
            hostname=hostname,
            ip_address=ip_address,
            queue_names=queue_names,
            max_concurrent_jobs=max_concurrent_jobs,
            cpu_total=cpu_total,
            cpu_available=cpu_total,
            memory_total_mb=memory_total_mb,
            memory_available_mb=memory_total_mb
        )
        
        self.workers[worker.worker_id] = worker
        
        # Add worker to queues
        for q_name in queue_names:
            queue = self._find_queue_by_name(q_name)
            if queue:
                queue.worker_ids.append(worker.worker_id)
                
        return worker
        
    def _find_queue_by_name(self, name: str) -> Optional[JobQueue]:
        """Поиск очереди по имени"""
        for q in self.queues.values():
            if q.name == name:
                return q
        return None
        
    async def create_resource_pool(self, name: str,
                                  total_cpu: float = 100.0,
                                  total_memory_mb: int = 102400,
                                  labels: Dict[str, str] = None) -> ResourcePool:
        """Создание пула ресурсов"""
        pool = ResourcePool(
            pool_id=f"pool_{uuid.uuid4().hex[:8]}",
            name=name,
            total_cpu=total_cpu,
            available_cpu=total_cpu,
            total_memory_mb=total_memory_mb,
            available_memory_mb=total_memory_mb,
            labels=labels or {}
        )
        
        self.resource_pools[pool.pool_id] = pool
        return pool
        
    async def create_job(self, name: str,
                        command: str,
                        arguments: List[str] = None,
                        job_type: JobType = JobType.SCHEDULED,
                        trigger_type: TriggerType = TriggerType.CRON,
                        cron_expression: str = "",
                        queue_name: str = "default",
                        priority: Priority = Priority.NORMAL,
                        timeout_seconds: int = 3600,
                        max_retries: int = 3,
                        cpu_limit: float = 1.0,
                        memory_limit_mb: int = 512,
                        depends_on: List[str] = None,
                        tags: List[str] = None,
                        environment: Dict[str, str] = None) -> JobDefinition:
        """Создание задания"""
        job = JobDefinition(
            job_def_id=f"job_{uuid.uuid4().hex[:12]}",
            name=name,
            command=command,
            arguments=arguments or [],
            job_type=job_type,
            trigger_type=trigger_type,
            cron_expression=cron_expression,
            queue_name=queue_name,
            priority=priority,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            cpu_limit=cpu_limit,
            memory_limit_mb=memory_limit_mb,
            depends_on=depends_on or [],
            tags=tags or [],
            environment=environment or {}
        )
        
        self.job_definitions[job.job_def_id] = job
        
        # Create schedule if cron
        if trigger_type == TriggerType.CRON and cron_expression:
            await self._create_schedule(job)
            
        # Create dependencies
        if depends_on:
            for dep_job_id in depends_on:
                await self.add_dependency(job.job_def_id, dep_job_id)
                
        return job
        
    async def _create_schedule(self, job: JobDefinition) -> Schedule:
        """Создание расписания"""
        schedule = Schedule(
            schedule_id=f"sched_{uuid.uuid4().hex[:8]}",
            job_def_id=job.job_def_id,
            trigger_type=job.trigger_type,
            cron_expression=job.cron_expression,
            next_run=datetime.now() + timedelta(minutes=random.randint(1, 60))  # Simplified
        )
        
        self.schedules[schedule.schedule_id] = schedule
        return schedule
        
    async def add_dependency(self, job_def_id: str,
                            depends_on_job_def_id: str,
                            dependency_type: str = "success") -> Optional[JobDependency]:
        """Добавление зависимости"""
        dep = JobDependency(
            dependency_id=f"dep_{uuid.uuid4().hex[:8]}",
            job_def_id=job_def_id,
            depends_on_job_def_id=depends_on_job_def_id,
            dependency_type=dependency_type
        )
        
        self.dependencies[dep.dependency_id] = dep
        return dep
        
    async def trigger_job(self, job_def_id: str) -> Optional[JobInstance]:
        """Запуск задания"""
        job_def = self.job_definitions.get(job_def_id)
        if not job_def or not job_def.is_enabled:
            return None
            
        # Check dependencies
        if not await self._check_dependencies(job_def_id):
            return None
            
        instance = JobInstance(
            job_instance_id=f"inst_{uuid.uuid4().hex[:12]}",
            job_def_id=job_def_id,
            status=JobStatus.QUEUED
        )
        
        self.job_instances[instance.job_instance_id] = instance
        
        # Add to queue
        if job_def.queue_name in self.pending_jobs:
            self.pending_jobs[job_def.queue_name].append(instance.job_instance_id)
            
        queue = self._find_queue_by_name(job_def.queue_name)
        if queue:
            queue.pending_jobs += 1
            
        # Try to dispatch
        await self._dispatch_job(instance)
        
        return instance
        
    async def _check_dependencies(self, job_def_id: str) -> bool:
        """Проверка зависимостей"""
        deps = [d for d in self.dependencies.values() if d.job_def_id == job_def_id]
        
        for dep in deps:
            # Find latest instance of dependency
            dep_instances = [i for i in self.job_instances.values() 
                           if i.job_def_id == dep.depends_on_job_def_id]
            
            if not dep_instances:
                return False
                
            latest = max(dep_instances, key=lambda x: x.scheduled_at)
            
            if dep.dependency_type == "success" and latest.status != JobStatus.COMPLETED:
                return False
            elif dep.dependency_type == "completion" and latest.status not in [JobStatus.COMPLETED, JobStatus.FAILED]:
                return False
                
        return True
        
    async def _dispatch_job(self, instance: JobInstance):
        """Распределение задания на воркер"""
        job_def = self.job_definitions.get(instance.job_def_id)
        if not job_def:
            return
            
        # Find available worker
        worker = await self._find_available_worker(job_def)
        if not worker:
            return
            
        # Allocate resources
        worker.cpu_available -= job_def.cpu_limit
        worker.memory_available_mb -= job_def.memory_limit_mb
        worker.current_jobs += 1
        worker.status = WorkerStatus.BUSY
        
        # Update instance
        instance.worker_id = worker.worker_id
        instance.status = JobStatus.RUNNING
        instance.started_at = datetime.now()
        
        # Update queue
        queue = self._find_queue_by_name(job_def.queue_name)
        if queue:
            queue.pending_jobs = max(0, queue.pending_jobs - 1)
            queue.running_jobs += 1
            
        # Remove from pending
        if job_def.queue_name in self.pending_jobs:
            if instance.job_instance_id in self.pending_jobs[job_def.queue_name]:
                self.pending_jobs[job_def.queue_name].remove(instance.job_instance_id)
                
        # Simulate execution
        await self._execute_job(instance, job_def, worker)
        
    async def _find_available_worker(self, job_def: JobDefinition) -> Optional[Worker]:
        """Поиск доступного воркера"""
        for worker in self.workers.values():
            if worker.status == WorkerStatus.OFFLINE:
                continue
            if job_def.queue_name not in worker.queue_names:
                continue
            if worker.current_jobs >= worker.max_concurrent_jobs:
                continue
            if worker.cpu_available < job_def.cpu_limit:
                continue
            if worker.memory_available_mb < job_def.memory_limit_mb:
                continue
            return worker
        return None
        
    async def _execute_job(self, instance: JobInstance,
                          job_def: JobDefinition,
                          worker: Worker):
        """Выполнение задания"""
        # Create execution record
        execution = JobExecution(
            execution_id=f"exec_{uuid.uuid4().hex[:8]}",
            job_instance_id=instance.job_instance_id
        )
        
        # Simulate execution
        success = random.random() > 0.1  # 90% success
        duration = random.uniform(10, 300)
        
        instance.duration_seconds = duration
        instance.cpu_used = random.uniform(0.1, job_def.cpu_limit)
        instance.memory_used_mb = random.randint(100, job_def.memory_limit_mb)
        
        execution.peak_cpu = instance.cpu_used
        execution.peak_memory_mb = instance.memory_used_mb
        execution.ended_at = datetime.now()
        
        if success:
            instance.status = JobStatus.COMPLETED
            instance.exit_code = 0
            execution.exit_code = 0
            execution.stdout = f"Job {job_def.name} completed successfully"
        else:
            if instance.attempt < job_def.max_retries:
                instance.status = JobStatus.RETRY
                instance.attempt += 1
            else:
                instance.status = JobStatus.FAILED
                instance.exit_code = 1
                instance.error = "Job execution failed"
                execution.exit_code = 1
                execution.stderr = "Error during execution"
                
                # Create alert
                await self._create_alert("job_failed", instance, worker)
                
        instance.completed_at = datetime.now()
        
        # Release resources
        worker.cpu_available += job_def.cpu_limit
        worker.memory_available_mb += job_def.memory_limit_mb
        worker.current_jobs -= 1
        if worker.current_jobs == 0:
            worker.status = WorkerStatus.IDLE
        worker.jobs_processed += 1
        if instance.status == JobStatus.FAILED:
            worker.jobs_failed += 1
            
        # Update queue
        queue = self._find_queue_by_name(job_def.queue_name)
        if queue:
            queue.running_jobs = max(0, queue.running_jobs - 1)
            if instance.status == JobStatus.COMPLETED:
                queue.completed_jobs += 1
            elif instance.status == JobStatus.FAILED:
                queue.failed_jobs += 1
                
        self.executions[execution.execution_id] = execution
        
        # Handle retry
        if instance.status == JobStatus.RETRY:
            await asyncio.sleep(0.01)  # Simulated delay
            await self._dispatch_job(instance)
            
    async def _create_alert(self, alert_type: str,
                           instance: JobInstance = None,
                           worker: Worker = None):
        """Создание оповещения"""
        alert = Alert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            alert_type=alert_type,
            job_instance_id=instance.job_instance_id if instance else "",
            job_def_id=instance.job_def_id if instance else "",
            worker_id=worker.worker_id if worker else "",
            message=f"Alert: {alert_type}",
            severity="error" if "failed" in alert_type else "warning"
        )
        
        self.alerts[alert.alert_id] = alert
        
    async def cancel_job(self, job_instance_id: str) -> bool:
        """Отмена задания"""
        instance = self.job_instances.get(job_instance_id)
        if not instance or instance.status not in [JobStatus.PENDING, JobStatus.QUEUED, JobStatus.RUNNING]:
            return False
            
        instance.status = JobStatus.CANCELLED
        instance.completed_at = datetime.now()
        
        # Release resources if running
        if instance.worker_id:
            worker = self.workers.get(instance.worker_id)
            job_def = self.job_definitions.get(instance.job_def_id)
            
            if worker and job_def:
                worker.cpu_available += job_def.cpu_limit
                worker.memory_available_mb += job_def.memory_limit_mb
                worker.current_jobs = max(0, worker.current_jobs - 1)
                if worker.current_jobs == 0:
                    worker.status = WorkerStatus.IDLE
                    
        return True
        
    async def pause_queue(self, queue_name: str) -> bool:
        """Приостановка очереди"""
        queue = self._find_queue_by_name(queue_name)
        if not queue:
            return False
            
        queue.status = QueueStatus.PAUSED
        return True
        
    async def resume_queue(self, queue_name: str) -> bool:
        """Возобновление очереди"""
        queue = self._find_queue_by_name(queue_name)
        if not queue:
            return False
            
        queue.status = QueueStatus.ACTIVE
        return True
        
    async def worker_heartbeat(self, worker_id: str) -> bool:
        """Heartbeat воркера"""
        worker = self.workers.get(worker_id)
        if not worker:
            return False
            
        worker.last_heartbeat = datetime.now()
        return True
        
    async def collect_metrics(self, job_def_id: str) -> Optional[JobMetrics]:
        """Сбор метрик"""
        job_def = self.job_definitions.get(job_def_id)
        if not job_def:
            return None
            
        instances = [i for i in self.job_instances.values() if i.job_def_id == job_def_id]
        
        metrics = JobMetrics(
            metrics_id=f"met_{uuid.uuid4().hex[:8]}",
            job_def_id=job_def_id,
            total_runs=len(instances),
            successful_runs=sum(1 for i in instances if i.status == JobStatus.COMPLETED),
            failed_runs=sum(1 for i in instances if i.status == JobStatus.FAILED)
        )
        
        # Calculate durations
        completed = [i for i in instances if i.completed_at and i.started_at]
        if completed:
            durations = [i.duration_seconds for i in completed]
            metrics.avg_duration_seconds = sum(durations) / len(durations)
            metrics.min_duration_seconds = min(durations)
            metrics.max_duration_seconds = max(durations)
            
            metrics.avg_cpu_used = sum(i.cpu_used for i in completed) / len(completed)
            metrics.avg_memory_mb = int(sum(i.memory_used_mb for i in completed) / len(completed))
            
        if metrics.total_runs > 0:
            metrics.success_rate = metrics.successful_runs / metrics.total_runs * 100
            
        self.metrics[metrics.metrics_id] = metrics
        return metrics
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_jobs = len(self.job_definitions)
        enabled_jobs = sum(1 for j in self.job_definitions.values() if j.is_enabled)
        
        total_instances = len(self.job_instances)
        running_instances = sum(1 for i in self.job_instances.values() if i.status == JobStatus.RUNNING)
        completed_instances = sum(1 for i in self.job_instances.values() if i.status == JobStatus.COMPLETED)
        failed_instances = sum(1 for i in self.job_instances.values() if i.status == JobStatus.FAILED)
        
        total_queues = len(self.queues)
        active_queues = sum(1 for q in self.queues.values() if q.status == QueueStatus.ACTIVE)
        
        total_workers = len(self.workers)
        idle_workers = sum(1 for w in self.workers.values() if w.status == WorkerStatus.IDLE)
        busy_workers = sum(1 for w in self.workers.values() if w.status == WorkerStatus.BUSY)
        
        total_schedules = len(self.schedules)
        active_schedules = sum(1 for s in self.schedules.values() if s.is_active)
        
        pending_alerts = sum(1 for a in self.alerts.values() if not a.is_resolved)
        
        return {
            "total_jobs": total_jobs,
            "enabled_jobs": enabled_jobs,
            "total_instances": total_instances,
            "running_instances": running_instances,
            "completed_instances": completed_instances,
            "failed_instances": failed_instances,
            "total_queues": total_queues,
            "active_queues": active_queues,
            "total_workers": total_workers,
            "idle_workers": idle_workers,
            "busy_workers": busy_workers,
            "total_schedules": total_schedules,
            "active_schedules": active_schedules,
            "pending_alerts": pending_alerts
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 348: Job Scheduler Platform")
    print("=" * 60)
    
    scheduler = JobScheduler()
    print("✓ Job Scheduler initialized")
    
    # Create Queues
    print("\n📦 Creating Job Queues...")
    
    queues_data = [
        ("default", 20, True),
        ("high-priority", 10, True),
        ("batch", 50, False),
        ("maintenance", 5, True),
        ("analytics", 30, False)
    ]
    
    queues = []
    for name, max_conc, priority in queues_data:
        q = await scheduler.create_queue(name, max_conc, priority)
        queues.append(q)
        print(f"  📦 {name} (max: {max_conc})")
        
    # Create Resource Pools
    print("\n🖥️ Creating Resource Pools...")
    
    pools_data = [
        ("production", 200.0, 409600, {"env": "prod"}),
        ("staging", 100.0, 204800, {"env": "staging"}),
        ("batch-processing", 500.0, 1024000, {"type": "batch"})
    ]
    
    pools = []
    for name, cpu, mem, labels in pools_data:
        p = await scheduler.create_resource_pool(name, cpu, mem, labels)
        pools.append(p)
        print(f"  🖥️ {name} ({cpu} CPU, {mem // 1024} GB)")
        
    # Register Workers
    print("\n👷 Registering Workers...")
    
    workers_data = [
        ("worker-01", "worker-01.local", "10.0.1.1", ["default", "high-priority"], 8, 16.0, 32768),
        ("worker-02", "worker-02.local", "10.0.1.2", ["default", "batch"], 16, 32.0, 65536),
        ("worker-03", "worker-03.local", "10.0.1.3", ["default", "analytics"], 8, 16.0, 32768),
        ("worker-04", "worker-04.local", "10.0.1.4", ["batch"], 32, 64.0, 131072),
        ("worker-05", "worker-05.local", "10.0.1.5", ["default", "maintenance"], 4, 8.0, 16384),
        ("worker-06", "worker-06.local", "10.0.1.6", ["high-priority"], 4, 8.0, 16384)
    ]
    
    workers = []
    for name, host, ip, queues_list, max_jobs, cpu, mem in workers_data:
        w = await scheduler.register_worker(name, host, ip, queues_list, max_jobs, cpu, mem)
        workers.append(w)
        print(f"  👷 {name} ({ip}, {max_jobs} jobs, {cpu} CPU)")
        
    # Create Job Definitions
    print("\n📋 Creating Job Definitions...")
    
    jobs_data = [
        ("Database Backup", "pg_dump", ["-h", "db.local", "-d", "main"], JobType.SCHEDULED, TriggerType.CRON, "0 2 * * *", "default", Priority.HIGH, 7200, 3, 2.0, 4096, [], ["backup", "database"]),
        ("Log Rotation", "logrotate", ["/etc/logrotate.conf"], JobType.SCHEDULED, TriggerType.CRON, "0 0 * * *", "maintenance", Priority.NORMAL, 1800, 3, 0.5, 512, [], ["logs", "maintenance"]),
        ("Data ETL", "python", ["etl_pipeline.py"], JobType.SCHEDULED, TriggerType.CRON, "0 */4 * * *", "batch", Priority.NORMAL, 14400, 2, 4.0, 8192, [], ["etl", "data"]),
        ("Report Generation", "python", ["generate_reports.py"], JobType.DEPENDENT, TriggerType.MANUAL, "", "analytics", Priority.NORMAL, 3600, 3, 2.0, 4096, [], ["reports"]),
        ("Cache Warmup", "python", ["warmup_cache.py"], JobType.SCHEDULED, TriggerType.CRON, "*/15 * * * *", "default", Priority.LOW, 900, 2, 1.0, 2048, [], ["cache"]),
        ("Health Check", "python", ["health_check.py"], JobType.RECURRING, TriggerType.INTERVAL, "", "high-priority", Priority.CRITICAL, 300, 1, 0.5, 256, [], ["monitoring"]),
        ("Index Rebuild", "python", ["rebuild_indexes.py"], JobType.SCHEDULED, TriggerType.CRON, "0 3 * * 0", "maintenance", Priority.HIGH, 7200, 2, 4.0, 8192, [], ["database", "index"]),
        ("Email Queue", "python", ["process_emails.py"], JobType.RECURRING, TriggerType.INTERVAL, "", "default", Priority.NORMAL, 600, 5, 1.0, 1024, [], ["email"]),
        ("Cleanup Temp", "bash", ["-c", "rm -rf /tmp/old/*"], JobType.SCHEDULED, TriggerType.CRON, "0 4 * * *", "maintenance", Priority.LOW, 1800, 1, 0.5, 256, [], ["cleanup"]),
        ("Analytics Aggregation", "python", ["aggregate_stats.py"], JobType.SCHEDULED, TriggerType.CRON, "0 1 * * *", "analytics", Priority.NORMAL, 10800, 2, 8.0, 16384, [], ["analytics"])
    ]
    
    jobs = []
    for name, cmd, args, jtype, trig, cron, queue, prio, timeout, retries, cpu, mem, deps, tags in jobs_data:
        j = await scheduler.create_job(name, cmd, args, jtype, trig, cron, queue, prio, timeout, retries, cpu, mem, deps, tags)
        jobs.append(j)
        print(f"  📋 {name} ({queue}, {prio.name})")
        
    # Add Dependencies
    print("\n🔗 Adding Dependencies...")
    
    # Report depends on ETL
    await scheduler.add_dependency(jobs[3].job_def_id, jobs[2].job_def_id, "success")
    print(f"  🔗 Report Generation depends on Data ETL")
    
    # Analytics depends on Database Backup
    await scheduler.add_dependency(jobs[9].job_def_id, jobs[0].job_def_id, "success")
    print(f"  🔗 Analytics Aggregation depends on Database Backup")
    
    # Trigger Jobs
    print("\n▶️ Triggering Jobs...")
    
    instances = []
    
    # Trigger multiple instances
    for job in jobs[:6]:
        for _ in range(random.randint(1, 3)):
            inst = await scheduler.trigger_job(job.job_def_id)
            if inst:
                instances.append(inst)
                
    print(f"  ▶️ Triggered {len(instances)} job instances")
    
    # Update heartbeats
    for worker in workers:
        await scheduler.worker_heartbeat(worker.worker_id)
        
    # Collect Metrics
    print("\n📊 Collecting Metrics...")
    
    metrics = []
    for job in jobs[:5]:
        m = await scheduler.collect_metrics(job.job_def_id)
        if m:
            metrics.append(m)
            
    print(f"  📊 Collected metrics for {len(metrics)} jobs")
    
    # Job Definitions Dashboard
    print("\n📋 Job Definitions:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                       │ Type       │ Queue            │ Priority │ Cron              │ Timeout │ Retries │ CPU  │ Memory │ Enabled │ Tags                                                                                                                    │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for job in jobs:
        name = job.name[:26].ljust(26)
        jtype = job.job_type.value[:10].ljust(10)
        queue = job.queue_name[:16].ljust(16)
        
        prio_colors = {Priority.LOW: "⬇️", Priority.NORMAL: "➡️", Priority.HIGH: "⬆️", Priority.CRITICAL: "🔴"}
        prio_icon = prio_colors.get(job.priority, "➡️")
        prio = f"{prio_icon} {job.priority.name}"[:8].ljust(8)
        
        cron = job.cron_expression[:17] if job.cron_expression else "N/A"
        cron = cron.ljust(17)
        
        timeout = f"{job.timeout_seconds // 60}m".ljust(7)
        retries = str(job.max_retries).ljust(7)
        cpu = f"{job.cpu_limit}".ljust(4)
        mem = f"{job.memory_limit_mb}MB".ljust(6)
        enabled = "✓" if job.is_enabled else "✗"
        enabled = enabled.ljust(7)
        tags = ", ".join(job.tags)[:117]
        tags = tags.ljust(117)
        
        print(f"  │ {name} │ {jtype} │ {queue} │ {prio} │ {cron} │ {timeout} │ {retries} │ {cpu} │ {mem} │ {enabled} │ {tags} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Job Queues
    print("\n📦 Job Queues:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                │ Status    │ Max Concurrent │ Priority │ Pending │ Running │ Completed │ Failed │ Workers                                                                                                                                                   │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for q in queues:
        name = q.name[:19].ljust(19)
        
        status_icons = {"active": "🟢", "paused": "🟡", "draining": "🔵"}
        status_icon = status_icons.get(q.status.value, "?")
        status = f"{status_icon} {q.status.value}"[:9].ljust(9)
        
        max_conc = str(q.max_concurrent).ljust(14)
        prio = "Yes" if q.priority_enabled else "No"
        prio = prio.ljust(8)
        pending = str(q.pending_jobs).ljust(7)
        running = str(q.running_jobs).ljust(7)
        completed = str(q.completed_jobs).ljust(9)
        failed = str(q.failed_jobs).ljust(6)
        worker_count = str(len(q.worker_ids)).ljust(147)
        
        print(f"  │ {name} │ {status} │ {max_conc} │ {prio} │ {pending} │ {running} │ {completed} │ {failed} │ {worker_count} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Workers
    print("\n👷 Workers:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name           │ Host                 │ IP             │ Status │ Jobs │ CPU Avail │ Mem Avail │ Processed │ Failed │ Last Heartbeat                                                                                                                          │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for w in workers:
        name = w.name[:14].ljust(14)
        host = w.hostname[:20].ljust(20)
        ip = w.ip_address[:14].ljust(14)
        
        status_icons = {"idle": "🟢", "busy": "🟡", "offline": "⚫", "draining": "🔵"}
        status_icon = status_icons.get(w.status.value, "?")
        status = f"{status_icon}"[:6].ljust(6)
        
        jobs_cur = f"{w.current_jobs}/{w.max_concurrent_jobs}".ljust(4)
        cpu = f"{w.cpu_available:.1f}/{w.cpu_total:.1f}".ljust(9)
        mem = f"{w.memory_available_mb // 1024}/{w.memory_total_mb // 1024}GB".ljust(9)
        processed = str(w.jobs_processed).ljust(9)
        failed = str(w.jobs_failed).ljust(6)
        hb = w.last_heartbeat.strftime("%Y-%m-%d %H:%M:%S")[:133].ljust(133)
        
        print(f"  │ {name} │ {host} │ {ip} │ {status} │ {jobs_cur} │ {cpu} │ {mem} │ {processed} │ {failed} │ {hb} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Recent Job Instances
    print("\n▶️ Recent Job Instances:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Instance ID               │ Job Name                    │ Status     │ Worker         │ Attempt │ Duration │ Exit │ Scheduled            │ Started              │ Completed                                                                                                       │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for inst in list(instances)[:10]:
        inst_id = inst.job_instance_id[:25].ljust(25)
        
        job_def = scheduler.job_definitions.get(inst.job_def_id)
        job_name = job_def.name if job_def else "Unknown"
        job_name = job_name[:27].ljust(27)
        
        status_icons = {"pending": "⏳", "queued": "📥", "running": "🔄", "completed": "✅", "failed": "❌", "cancelled": "⚫", "retry": "🔁"}
        status_icon = status_icons.get(inst.status.value, "?")
        status = f"{status_icon} {inst.status.value}"[:10].ljust(10)
        
        worker = scheduler.workers.get(inst.worker_id)
        worker_name = worker.name if worker else "N/A"
        worker_name = worker_name[:14].ljust(14)
        
        attempt = str(inst.attempt).ljust(7)
        duration = f"{inst.duration_seconds:.0f}s" if inst.duration_seconds > 0 else "N/A"
        duration = duration[:8].ljust(8)
        exit_code = str(inst.exit_code) if inst.status in [JobStatus.COMPLETED, JobStatus.FAILED] else "N/A"
        exit_code = exit_code[:4].ljust(4)
        
        scheduled = inst.scheduled_at.strftime("%Y-%m-%d %H:%M:%S")[:20].ljust(20)
        started = inst.started_at.strftime("%Y-%m-%d %H:%M:%S") if inst.started_at else "N/A"
        started = started[:20].ljust(20)
        completed = inst.completed_at.strftime("%Y-%m-%d %H:%M:%S") if inst.completed_at else "N/A"
        completed = completed[:113].ljust(113)
        
        print(f"  │ {inst_id} │ {job_name} │ {status} │ {worker_name} │ {attempt} │ {duration} │ {exit_code} │ {scheduled} │ {started} │ {completed} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Job Metrics
    print("\n📊 Job Metrics:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Job Name                    │ Total Runs │ Success │ Failed │ Success Rate │ Avg Duration │ Min Duration │ Max Duration │ Avg CPU │ Avg Memory                                                                                                                                               │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for m in metrics:
        job_def = scheduler.job_definitions.get(m.job_def_id)
        job_name = job_def.name if job_def else "Unknown"
        job_name = job_name[:27].ljust(27)
        
        total = str(m.total_runs).ljust(10)
        success = str(m.successful_runs).ljust(7)
        failed = str(m.failed_runs).ljust(6)
        rate = f"{m.success_rate:.1f}%".ljust(12)
        avg_dur = f"{m.avg_duration_seconds:.0f}s".ljust(12)
        min_dur = f"{m.min_duration_seconds:.0f}s".ljust(12)
        max_dur = f"{m.max_duration_seconds:.0f}s".ljust(12)
        avg_cpu = f"{m.avg_cpu_used:.2f}".ljust(7)
        avg_mem = f"{m.avg_memory_mb} MB".ljust(147)
        
        print(f"  │ {job_name} │ {total} │ {success} │ {failed} │ {rate} │ {avg_dur} │ {min_dur} │ {max_dur} │ {avg_cpu} │ {avg_mem} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Alerts
    alerts = [a for a in scheduler.alerts.values() if not a.is_resolved][:5]
    
    print("\n🚨 Active Alerts:")
    
    if alerts:
        print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
        print("  │ Type           │ Severity   │ Job                         │ Worker         │ Created              │ Message                                       │")
        print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
        
        for a in alerts:
            atype = a.alert_type[:14].ljust(14)
            
            sev_colors = {"info": "🔵", "warning": "🟡", "error": "🔴", "critical": "⛔"}
            sev_icon = sev_colors.get(a.severity, "?")
            sev = f"{sev_icon} {a.severity}"[:10].ljust(10)
            
            job_def = scheduler.job_definitions.get(a.job_def_id) if a.job_def_id else None
            job_name = job_def.name if job_def else "N/A"
            job_name = job_name[:27].ljust(27)
            
            worker = scheduler.workers.get(a.worker_id) if a.worker_id else None
            worker_name = worker.name if worker else "N/A"
            worker_name = worker_name[:14].ljust(14)
            
            created = a.created_at.strftime("%Y-%m-%d %H:%M:%S")[:20].ljust(20)
            msg = a.message[:47].ljust(47)
            
            print(f"  │ {atype} │ {sev} │ {job_name} │ {worker_name} │ {created} │ {msg} │")
            
        print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    else:
        print("  No active alerts")
        
    # Statistics
    stats = scheduler.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Jobs: {stats['enabled_jobs']}/{stats['total_jobs']} enabled")
    print(f"  Instances: {stats['running_instances']} running, {stats['completed_instances']} completed, {stats['failed_instances']} failed")
    print(f"  Queues: {stats['active_queues']}/{stats['total_queues']} active")
    print(f"  Workers: {stats['idle_workers']} idle, {stats['busy_workers']} busy")
    print(f"  Schedules: {stats['active_schedules']}/{stats['total_schedules']} active")
    print(f"  Pending Alerts: {stats['pending_alerts']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                      Job Scheduler Platform                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Enabled Jobs:                 {stats['enabled_jobs']:>12}                      │")
    print(f"│ Active Queues:                {stats['active_queues']:>12}                      │")
    print(f"│ Total Workers:                {stats['total_workers']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Running Instances:            {stats['running_instances']:>12}                      │")
    print(f"│ Completed Instances:          {stats['completed_instances']:>12}                      │")
    print(f"│ Failed Instances:             {stats['failed_instances']:>12}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Job Scheduler Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
