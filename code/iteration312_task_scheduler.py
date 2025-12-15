#!/usr/bin/env python3
"""
Server Init - Iteration 312: Task Scheduler Platform
Платформа планирования задач

Функционал:
- Job Scheduling - планирование задач
- Cron Expressions - cron выражения
- Dependencies - зависимости задач
- Retry Logic - логика повторов
- Job Queues - очереди задач
- Workers - воркеры
- History - история выполнения
- Monitoring - мониторинг
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid
import heapq


class JobStatus(Enum):
    """Статус задачи"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class JobPriority(Enum):
    """Приоритет задачи"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class RetryPolicy(Enum):
    """Политика повторов"""
    NONE = "none"
    IMMEDIATE = "immediate"
    FIXED_DELAY = "fixed_delay"
    EXPONENTIAL_BACKOFF = "exponential_backoff"


class WorkerStatus(Enum):
    """Статус воркера"""
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"


@dataclass
class Job:
    """Задача"""
    job_id: str
    name: str
    
    # Function
    function_name: str = ""
    arguments: Dict[str, Any] = field(default_factory=dict)
    
    # Scheduling
    cron_expression: str = ""  # e.g., "0 * * * *" for hourly
    scheduled_time: Optional[datetime] = None
    
    # Priority
    priority: JobPriority = JobPriority.NORMAL
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)  # job_ids
    
    # Retry
    retry_policy: RetryPolicy = RetryPolicy.NONE
    max_retries: int = 3
    retry_delay_seconds: int = 60
    
    # Timeout
    timeout_seconds: int = 3600
    
    # Queue
    queue: str = "default"
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Status
    status: JobStatus = JobStatus.PENDING
    retry_count: int = 0
    
    # Result
    result: Any = None
    error_message: str = ""
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0
    
    # Next execution
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None


@dataclass
class JobExecution:
    """Выполнение задачи"""
    execution_id: str
    job_id: str
    
    # Status
    status: JobStatus = JobStatus.PENDING
    
    # Worker
    worker_id: str = ""
    
    # Result
    result: Any = None
    error_message: str = ""
    
    # Retry
    retry_count: int = 0
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Worker:
    """Воркер"""
    worker_id: str
    name: str
    
    # Queues
    queues: List[str] = field(default_factory=lambda: ["default"])
    
    # Status
    status: WorkerStatus = WorkerStatus.IDLE
    current_job_id: str = ""
    
    # Stats
    jobs_processed: int = 0
    jobs_failed: int = 0
    total_runtime_seconds: float = 0
    
    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: datetime = field(default_factory=datetime.now)


@dataclass
class Queue:
    """Очередь задач"""
    queue_id: str
    name: str
    
    # Config
    max_concurrency: int = 10
    priority_weight: int = 1
    
    # Status
    is_paused: bool = False
    
    # Stats
    pending_jobs: int = 0
    running_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0


@dataclass
class Schedule:
    """Расписание"""
    schedule_id: str
    name: str
    
    # Job template
    job_template: Dict[str, Any] = field(default_factory=dict)
    
    # Cron
    cron_expression: str = ""
    
    # Status
    is_active: bool = True
    
    # Stats
    run_count: int = 0
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None


class TaskScheduler:
    """Планировщик задач"""
    
    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self.executions: Dict[str, JobExecution] = {}
        self.workers: Dict[str, Worker] = {}
        self.queues: Dict[str, Queue] = {}
        self.schedules: Dict[str, Schedule] = {}
        
        # Job queue (priority queue)
        self.job_queue: List[tuple] = []  # (priority, scheduled_time, job_id)
        
        # Handlers
        self.handlers: Dict[str, Callable] = {}
        
    async def create_queue(self, name: str,
                          max_concurrency: int = 10) -> Queue:
        """Создание очереди"""
        queue = Queue(
            queue_id=f"q_{uuid.uuid4().hex[:8]}",
            name=name,
            max_concurrency=max_concurrency
        )
        
        self.queues[queue.queue_id] = queue
        return queue
        
    async def create_worker(self, name: str,
                           queues: List[str] = None) -> Worker:
        """Создание воркера"""
        worker = Worker(
            worker_id=f"wrk_{uuid.uuid4().hex[:8]}",
            name=name,
            queues=queues or ["default"]
        )
        
        self.workers[worker.worker_id] = worker
        return worker
        
    def register_handler(self, function_name: str, handler: Callable):
        """Регистрация обработчика"""
        self.handlers[function_name] = handler
        
    async def schedule_job(self, name: str,
                          function_name: str,
                          arguments: Dict[str, Any] = None,
                          scheduled_time: datetime = None,
                          priority: JobPriority = JobPriority.NORMAL,
                          queue: str = "default",
                          retry_policy: RetryPolicy = RetryPolicy.NONE,
                          depends_on: List[str] = None) -> Job:
        """Планирование задачи"""
        job = Job(
            job_id=f"job_{uuid.uuid4().hex[:8]}",
            name=name,
            function_name=function_name,
            arguments=arguments or {},
            scheduled_time=scheduled_time or datetime.now(),
            priority=priority,
            queue=queue,
            retry_policy=retry_policy,
            depends_on=depends_on or [],
            status=JobStatus.SCHEDULED
        )
        
        self.jobs[job.job_id] = job
        
        # Add to queue
        heapq.heappush(
            self.job_queue,
            (-priority.value, job.scheduled_time, job.job_id)
        )
        
        # Update queue stats
        queue_obj = next(
            (q for q in self.queues.values() if q.name == queue),
            None
        )
        if queue_obj:
            queue_obj.pending_jobs += 1
            
        return job
        
    async def schedule_recurring(self, name: str,
                                function_name: str,
                                cron_expression: str,
                                arguments: Dict[str, Any] = None,
                                queue: str = "default") -> Schedule:
        """Создание периодической задачи"""
        schedule = Schedule(
            schedule_id=f"sch_{uuid.uuid4().hex[:8]}",
            name=name,
            job_template={
                "function_name": function_name,
                "arguments": arguments or {},
                "queue": queue
            },
            cron_expression=cron_expression
        )
        
        # Calculate next run
        schedule.next_run = self._calculate_next_run(cron_expression)
        
        self.schedules[schedule.schedule_id] = schedule
        return schedule
        
    def _calculate_next_run(self, cron_expression: str) -> datetime:
        """Расчет следующего запуска"""
        # Simplified cron parsing (for demo)
        now = datetime.now()
        
        parts = cron_expression.split()
        if len(parts) >= 1:
            minute = parts[0]
            if minute == "*":
                return now + timedelta(minutes=1)
            elif minute.startswith("*/"):
                interval = int(minute[2:])
                return now + timedelta(minutes=interval)
                
        return now + timedelta(hours=1)
        
    async def process_schedules(self):
        """Обработка расписаний"""
        now = datetime.now()
        
        for schedule in self.schedules.values():
            if not schedule.is_active:
                continue
                
            if schedule.next_run and schedule.next_run <= now:
                # Create job from template
                template = schedule.job_template
                
                job = await self.schedule_job(
                    f"{schedule.name}_{now.strftime('%Y%m%d_%H%M%S')}",
                    template.get("function_name", ""),
                    template.get("arguments", {}),
                    now,
                    JobPriority.NORMAL,
                    template.get("queue", "default")
                )
                
                schedule.run_count += 1
                schedule.last_run = now
                schedule.next_run = self._calculate_next_run(schedule.cron_expression)
                
    async def run_job(self, job_id: str, worker_id: str = "") -> Optional[JobExecution]:
        """Запуск задачи"""
        job = self.jobs.get(job_id)
        if not job or job.status not in [JobStatus.SCHEDULED, JobStatus.RETRYING]:
            return None
            
        # Check dependencies
        for dep_id in job.depends_on:
            dep_job = self.jobs.get(dep_id)
            if dep_job and dep_job.status != JobStatus.COMPLETED:
                return None  # Dependency not met
                
        # Create execution
        execution = JobExecution(
            execution_id=f"exec_{uuid.uuid4().hex[:8]}",
            job_id=job_id,
            worker_id=worker_id
        )
        
        self.executions[execution.execution_id] = execution
        
        # Update job and execution status
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now()
        execution.status = JobStatus.RUNNING
        execution.started_at = datetime.now()
        
        # Update worker
        worker = self.workers.get(worker_id)
        if worker:
            worker.status = WorkerStatus.BUSY
            worker.current_job_id = job_id
            
        # Update queue
        queue_obj = next(
            (q for q in self.queues.values() if q.name == job.queue),
            None
        )
        if queue_obj:
            queue_obj.pending_jobs = max(0, queue_obj.pending_jobs - 1)
            queue_obj.running_jobs += 1
            
        try:
            # Execute handler
            handler = self.handlers.get(job.function_name)
            if handler:
                result = await handler(**job.arguments)
                job.result = result
                execution.result = result
            else:
                # Simulate execution
                await asyncio.sleep(random.uniform(0.05, 0.2))
                job.result = {"status": "simulated"}
                execution.result = {"status": "simulated"}
                
            job.status = JobStatus.COMPLETED
            execution.status = JobStatus.COMPLETED
            
            if queue_obj:
                queue_obj.completed_jobs += 1
                
        except Exception as e:
            job.error_message = str(e)
            execution.error_message = str(e)
            
            # Retry logic
            if (job.retry_policy != RetryPolicy.NONE and
                job.retry_count < job.max_retries):
                job.retry_count += 1
                execution.retry_count = job.retry_count
                job.status = JobStatus.RETRYING
                
                # Re-schedule
                delay = self._calculate_retry_delay(job)
                job.scheduled_time = datetime.now() + timedelta(seconds=delay)
                heapq.heappush(
                    self.job_queue,
                    (-job.priority.value, job.scheduled_time, job.job_id)
                )
            else:
                job.status = JobStatus.FAILED
                execution.status = JobStatus.FAILED
                
                if queue_obj:
                    queue_obj.failed_jobs += 1
                    
        # Update timing
        job.completed_at = datetime.now()
        job.duration_seconds = (job.completed_at - job.started_at).total_seconds()
        job.last_run = job.completed_at
        
        execution.completed_at = datetime.now()
        execution.duration_seconds = (
            execution.completed_at - execution.started_at
        ).total_seconds()
        
        # Update worker
        if worker:
            worker.status = WorkerStatus.IDLE
            worker.current_job_id = ""
            worker.jobs_processed += 1
            worker.total_runtime_seconds += execution.duration_seconds
            
            if job.status == JobStatus.FAILED:
                worker.jobs_failed += 1
                
        # Update queue
        if queue_obj:
            queue_obj.running_jobs = max(0, queue_obj.running_jobs - 1)
            
        return execution
        
    def _calculate_retry_delay(self, job: Job) -> int:
        """Расчет задержки повтора"""
        if job.retry_policy == RetryPolicy.IMMEDIATE:
            return 0
        elif job.retry_policy == RetryPolicy.FIXED_DELAY:
            return job.retry_delay_seconds
        elif job.retry_policy == RetryPolicy.EXPONENTIAL_BACKOFF:
            return job.retry_delay_seconds * (2 ** job.retry_count)
        return job.retry_delay_seconds
        
    async def process_queue(self):
        """Обработка очереди"""
        # Process scheduled jobs
        await self.process_schedules()
        
        # Get available workers
        available_workers = [
            w for w in self.workers.values()
            if w.status == WorkerStatus.IDLE
        ]
        
        # Process jobs
        while self.job_queue and available_workers:
            _, scheduled_time, job_id = heapq.heappop(self.job_queue)
            
            job = self.jobs.get(job_id)
            if not job or job.status not in [JobStatus.SCHEDULED, JobStatus.RETRYING]:
                continue
                
            if scheduled_time > datetime.now():
                # Not yet time, put back
                heapq.heappush(self.job_queue, (-job.priority.value, scheduled_time, job_id))
                break
                
            # Find suitable worker
            worker = None
            for w in available_workers:
                if job.queue in w.queues or "default" in w.queues:
                    worker = w
                    available_workers.remove(w)
                    break
                    
            if worker:
                await self.run_job(job_id, worker.worker_id)
                
    async def cancel_job(self, job_id: str) -> bool:
        """Отмена задачи"""
        job = self.jobs.get(job_id)
        if not job:
            return False
            
        if job.status in [JobStatus.PENDING, JobStatus.SCHEDULED]:
            job.status = JobStatus.CANCELLED
            return True
            
        return False
        
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Статус задачи"""
        job = self.jobs.get(job_id)
        if not job:
            return {}
            
        executions = [
            e for e in self.executions.values()
            if e.job_id == job_id
        ]
        
        return {
            "job_id": job_id,
            "name": job.name,
            "status": job.status.value,
            "priority": job.priority.name,
            "queue": job.queue,
            "retry_count": job.retry_count,
            "executions": len(executions),
            "duration": job.duration_seconds,
            "scheduled_time": job.scheduled_time.isoformat() if job.scheduled_time else None,
            "last_run": job.last_run.isoformat() if job.last_run else None,
            "error": job.error_message
        }
        
    def get_queue_status(self, queue_name: str) -> Dict[str, Any]:
        """Статус очереди"""
        queue = next(
            (q for q in self.queues.values() if q.name == queue_name),
            None
        )
        if not queue:
            return {}
            
        return {
            "queue_id": queue.queue_id,
            "name": queue.name,
            "is_paused": queue.is_paused,
            "pending": queue.pending_jobs,
            "running": queue.running_jobs,
            "completed": queue.completed_jobs,
            "failed": queue.failed_jobs,
            "max_concurrency": queue.max_concurrency
        }
        
    def get_worker_status(self, worker_id: str) -> Dict[str, Any]:
        """Статус воркера"""
        worker = self.workers.get(worker_id)
        if not worker:
            return {}
            
        return {
            "worker_id": worker_id,
            "name": worker.name,
            "status": worker.status.value,
            "queues": worker.queues,
            "current_job": worker.current_job_id,
            "jobs_processed": worker.jobs_processed,
            "jobs_failed": worker.jobs_failed,
            "total_runtime": worker.total_runtime_seconds,
            "uptime_seconds": (datetime.now() - worker.started_at).total_seconds()
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        by_status = {}
        by_priority = {}
        by_queue = {}
        total_duration = 0
        
        for job in self.jobs.values():
            by_status[job.status.value] = by_status.get(job.status.value, 0) + 1
            by_priority[job.priority.name] = by_priority.get(job.priority.name, 0) + 1
            by_queue[job.queue] = by_queue.get(job.queue, 0) + 1
            total_duration += job.duration_seconds
            
        workers_idle = sum(1 for w in self.workers.values() if w.status == WorkerStatus.IDLE)
        workers_busy = sum(1 for w in self.workers.values() if w.status == WorkerStatus.BUSY)
        
        total_retries = sum(j.retry_count for j in self.jobs.values())
        
        return {
            "total_jobs": len(self.jobs),
            "by_status": by_status,
            "by_priority": by_priority,
            "by_queue": by_queue,
            "total_queues": len(self.queues),
            "total_workers": len(self.workers),
            "workers_idle": workers_idle,
            "workers_busy": workers_busy,
            "total_schedules": len(self.schedules),
            "total_executions": len(self.executions),
            "total_retries": total_retries,
            "queue_size": len(self.job_queue),
            "avg_duration": total_duration / max(len(self.jobs), 1),
            "total_duration": total_duration
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 312: Task Scheduler Platform")
    print("=" * 60)
    
    scheduler = TaskScheduler()
    print("✓ Task Scheduler created")
    
    # Create queues
    print("\n📋 Creating Queues...")
    
    queues_data = [
        ("default", 10),
        ("high-priority", 5),
        ("background", 20),
        ("reports", 3)
    ]
    
    queues = []
    for name, concurrency in queues_data:
        queue = await scheduler.create_queue(name, concurrency)
        queues.append(queue)
        print(f"  📋 {name} (concurrency: {concurrency})")
        
    # Create workers
    print("\n👷 Creating Workers...")
    
    workers_data = [
        ("Worker-1", ["default", "high-priority"]),
        ("Worker-2", ["default", "background"]),
        ("Worker-3", ["default"]),
        ("Worker-4", ["reports", "background"]),
        ("Worker-5", ["high-priority"])
    ]
    
    workers = []
    for name, q_list in workers_data:
        worker = await scheduler.create_worker(name, q_list)
        workers.append(worker)
        print(f"  👷 {name}: {', '.join(q_list)}")
        
    # Register handlers
    print("\n🔧 Registering Handlers...")
    
    async def process_data(**kwargs):
        await asyncio.sleep(random.uniform(0.05, 0.15))
        return {"processed": True, "items": random.randint(10, 100)}
        
    async def send_email(**kwargs):
        await asyncio.sleep(random.uniform(0.02, 0.1))
        return {"sent": True, "recipient": kwargs.get("to", "unknown")}
        
    async def generate_report(**kwargs):
        await asyncio.sleep(random.uniform(0.1, 0.3))
        return {"report_id": f"rpt_{random.randint(1000, 9999)}"}
        
    async def cleanup_task(**kwargs):
        await asyncio.sleep(random.uniform(0.05, 0.1))
        return {"cleaned": random.randint(5, 50)}
        
    scheduler.register_handler("process_data", process_data)
    scheduler.register_handler("send_email", send_email)
    scheduler.register_handler("generate_report", generate_report)
    scheduler.register_handler("cleanup", cleanup_task)
    
    print("  🔧 Registered 4 handlers")
    
    # Create recurring schedules
    print("\n⏰ Creating Schedules...")
    
    schedules_data = [
        ("Hourly Cleanup", "cleanup", "0 * * * *", {}),
        ("Daily Report", "generate_report", "0 9 * * *", {"type": "daily"}),
        ("Process Queue", "process_data", "*/5 * * * *", {"batch": True})
    ]
    
    for name, func, cron, args in schedules_data:
        schedule = await scheduler.schedule_recurring(name, func, cron, args)
        print(f"  ⏰ {name}: {cron}")
        
    # Schedule jobs
    print("\n📝 Scheduling Jobs...")
    
    jobs = []
    
    # High priority jobs
    for i in range(5):
        job = await scheduler.schedule_job(
            f"Critical Task {i+1}",
            "process_data",
            {"id": i, "urgent": True},
            datetime.now(),
            JobPriority.CRITICAL,
            "high-priority"
        )
        jobs.append(job)
        
    # Normal jobs
    for i in range(15):
        job = await scheduler.schedule_job(
            f"Regular Task {i+1}",
            random.choice(["process_data", "send_email", "cleanup"]),
            {"id": i},
            datetime.now() + timedelta(seconds=random.randint(0, 5)),
            JobPriority.NORMAL,
            random.choice(["default", "background"]),
            RetryPolicy.FIXED_DELAY if random.random() > 0.7 else RetryPolicy.NONE
        )
        jobs.append(job)
        
    # Report jobs
    for i in range(5):
        job = await scheduler.schedule_job(
            f"Report {i+1}",
            "generate_report",
            {"report_type": random.choice(["daily", "weekly", "monthly"])},
            datetime.now(),
            JobPriority.LOW,
            "reports"
        )
        jobs.append(job)
        
    print(f"  ✓ Scheduled {len(jobs)} jobs")
    
    # Process queue
    print("\n▶️ Processing Queue...")
    
    for _ in range(10):
        await scheduler.process_queue()
        await asyncio.sleep(0.1)
        
    # Check results
    completed = sum(1 for j in scheduler.jobs.values() if j.status == JobStatus.COMPLETED)
    failed = sum(1 for j in scheduler.jobs.values() if j.status == JobStatus.FAILED)
    pending = sum(1 for j in scheduler.jobs.values() if j.status in [JobStatus.PENDING, JobStatus.SCHEDULED])
    
    print(f"  ✓ Completed: {completed} | Failed: {failed} | Pending: {pending}")
    
    # Job list
    print("\n📋 Job List:")
    
    print("\n  ┌──────────────────────────────┬──────────────┬────────────┬────────────┬──────────┐")
    print("  │ Job                          │ Status       │ Priority   │ Queue      │ Duration │")
    print("  ├──────────────────────────────┼──────────────┼────────────┼────────────┼──────────┤")
    
    for job in list(scheduler.jobs.values())[:12]:
        name = job.name[:28].ljust(28)
        status = job.status.value[:12].ljust(12)
        priority = job.priority.name[:10].ljust(10)
        queue = job.queue[:10].ljust(10)
        duration = f"{job.duration_seconds:.3f}s" if job.duration_seconds > 0 else "N/A"
        duration = duration.ljust(8)
        
        print(f"  │ {name} │ {status} │ {priority} │ {queue} │ {duration} │")
        
    print("  └──────────────────────────────┴──────────────┴────────────┴────────────┴──────────┘")
    
    # Queue status
    print("\n📋 Queue Status:")
    
    print("\n  ┌────────────────────┬─────────┬─────────┬───────────┬────────┐")
    print("  │ Queue              │ Pending │ Running │ Completed │ Failed │")
    print("  ├────────────────────┼─────────┼─────────┼───────────┼────────┤")
    
    for queue in scheduler.queues.values():
        status = scheduler.get_queue_status(queue.name)
        
        name = status['name'][:18].ljust(18)
        pending = str(status['pending']).ljust(7)
        running = str(status['running']).ljust(7)
        completed_str = str(status['completed']).ljust(9)
        failed_str = str(status['failed']).ljust(6)
        
        print(f"  │ {name} │ {pending} │ {running} │ {completed_str} │ {failed_str} │")
        
    print("  └────────────────────┴─────────┴─────────┴───────────┴────────┘")
    
    # Worker status
    print("\n👷 Worker Status:")
    
    print("\n  ┌──────────────────┬──────────┬─────────────┬────────┬──────────────┐")
    print("  │ Worker           │ Status   │ Jobs Done   │ Failed │ Runtime      │")
    print("  ├──────────────────┼──────────┼─────────────┼────────┼──────────────┤")
    
    for worker in scheduler.workers.values():
        status = scheduler.get_worker_status(worker.worker_id)
        
        name = status['name'][:16].ljust(16)
        w_status = status['status'][:8].ljust(8)
        jobs_done = str(status['jobs_processed']).ljust(11)
        failed_str = str(status['jobs_failed']).ljust(6)
        runtime = f"{status['total_runtime']:.2f}s".ljust(12)
        
        print(f"  │ {name} │ {w_status} │ {jobs_done} │ {failed_str} │ {runtime} │")
        
    print("  └──────────────────┴──────────┴─────────────┴────────┴──────────────┘")
    
    # Schedule status
    print("\n⏰ Schedule Status:")
    
    for schedule in scheduler.schedules.values():
        next_run = schedule.next_run.strftime('%Y-%m-%d %H:%M') if schedule.next_run else "N/A"
        active = "✓" if schedule.is_active else "✗"
        
        print(f"  [{active}] {schedule.name}")
        print(f"      Cron: {schedule.cron_expression} | Runs: {schedule.run_count} | Next: {next_run}")
        
    # Job status distribution
    print("\n📊 Job Status Distribution:")
    
    stats = scheduler.get_statistics()
    
    for status_name, count in stats['by_status'].items():
        bar = "█" * min(count, 15) + "░" * (15 - min(count, 15))
        icon = "✓" if status_name == "completed" else "✗" if status_name == "failed" else "○"
        print(f"  {icon} {status_name:12} [{bar}] {count}")
        
    # Priority distribution
    print("\n📊 Priority Distribution:")
    
    for priority_name, count in stats['by_priority'].items():
        bar = "█" * min(count, 15) + "░" * (15 - min(count, 15))
        print(f"  {priority_name:10} [{bar}] {count}")
        
    # Statistics
    print("\n📊 Scheduler Statistics:")
    
    print(f"\n  Total Jobs: {stats['total_jobs']}")
    print("  By Queue:")
    for queue_name, count in stats['by_queue'].items():
        print(f"    {queue_name}: {count}")
        
    print(f"\n  Total Queues: {stats['total_queues']}")
    print(f"  Queue Size: {stats['queue_size']}")
    
    print(f"\n  Total Workers: {stats['total_workers']}")
    print(f"  Workers Idle: {stats['workers_idle']}")
    print(f"  Workers Busy: {stats['workers_busy']}")
    
    print(f"\n  Total Schedules: {stats['total_schedules']}")
    print(f"  Total Executions: {stats['total_executions']}")
    print(f"  Total Retries: {stats['total_retries']}")
    
    print(f"\n  Avg Job Duration: {stats['avg_duration']:.3f}s")
    print(f"  Total Runtime: {stats['total_duration']:.2f}s")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                      Task Scheduler Platform                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Jobs:                  {stats['total_jobs']:>12}                          │")
    print(f"│ Total Workers:               {stats['total_workers']:>12}                          │")
    print(f"│ Total Queues:                {stats['total_queues']:>12}                          │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Avg Job Duration:            {stats['avg_duration']:>10.3f}s                        │")
    print(f"│ Total Runtime:               {stats['total_duration']:>10.2f}s                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Task Scheduler Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
