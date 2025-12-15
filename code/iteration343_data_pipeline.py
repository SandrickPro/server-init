#!/usr/bin/env python3
"""
Server Init - Iteration 343: Data Pipeline Orchestrator
Платформа оркестрации потоков данных

Функционал:
- Pipeline Definition - определение пайплайнов
- DAG Management - управление направленными ациклическими графами
- Task Scheduling - планирование задач
- Data Lineage - происхождение данных
- Error Handling - обработка ошибок
- Monitoring & Alerting - мониторинг и оповещения
- Backfill Support - поддержка исторических запусков
- Plugin Architecture - архитектура плагинов
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
import uuid


class TaskState(Enum):
    """Состояние задачи"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    UPSTREAM_FAILED = "upstream_failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class PipelineState(Enum):
    """Состояние пайплайна"""
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


class RunState(Enum):
    """Состояние запуска"""
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    CANCELLED = "cancelled"


class TriggerType(Enum):
    """Тип триггера"""
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    DEPENDENCY = "dependency"
    EVENT = "event"
    BACKFILL = "backfill"


class OperatorType(Enum):
    """Тип оператора"""
    PYTHON = "python"
    BASH = "bash"
    SQL = "sql"
    SPARK = "spark"
    HTTP = "http"
    BRANCH = "branch"
    SENSOR = "sensor"
    DUMMY = "dummy"


class ScheduleInterval(Enum):
    """Интервал расписания"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class RetryPolicy(Enum):
    """Политика повторов"""
    NONE = "none"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"


class DataQualityCheckType(Enum):
    """Тип проверки качества данных"""
    NOT_NULL = "not_null"
    UNIQUE = "unique"
    RANGE = "range"
    REGEX = "regex"
    CUSTOM = "custom"


@dataclass
class TaskDefinition:
    """Определение задачи"""
    task_id: str
    name: str
    
    # Operator
    operator_type: OperatorType = OperatorType.PYTHON
    
    # Dependencies
    upstream_task_ids: List[str] = field(default_factory=list)
    downstream_task_ids: List[str] = field(default_factory=list)
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Execution
    timeout_seconds: int = 3600
    max_retries: int = 3
    retry_policy: RetryPolicy = RetryPolicy.EXPONENTIAL
    retry_delay_seconds: int = 60
    
    # Resources
    pool: str = "default"
    priority: int = 0
    
    # Quality checks
    quality_checks: List[Dict[str, Any]] = field(default_factory=list)
    
    # Owner
    owner: str = ""
    
    # Description
    description: str = ""
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Pipeline:
    """Пайплайн данных"""
    pipeline_id: str
    name: str
    
    # State
    state: PipelineState = PipelineState.ACTIVE
    
    # Schedule
    schedule_interval: ScheduleInterval = ScheduleInterval.DAILY
    cron_expression: str = "0 0 * * *"
    
    # Start/End
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    # Tasks
    task_ids: List[str] = field(default_factory=list)
    
    # Default configuration
    default_timeout: int = 3600
    default_retries: int = 3
    default_pool: str = "default"
    
    # Catchup
    catchup: bool = False
    max_active_runs: int = 1
    
    # Concurrency
    concurrency: int = 16
    
    # Owner
    owner: str = ""
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Description
    description: str = ""
    
    # SLA
    sla_miss_callback: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None


@dataclass
class PipelineRun:
    """Запуск пайплайна"""
    run_id: str
    
    # Pipeline
    pipeline_id: str = ""
    pipeline_name: str = ""
    
    # State
    state: RunState = RunState.RUNNING
    
    # Trigger
    trigger_type: TriggerType = TriggerType.SCHEDULED
    triggered_by: str = ""
    
    # Logical date
    logical_date: datetime = field(default_factory=datetime.now)
    data_interval_start: Optional[datetime] = None
    data_interval_end: Optional[datetime] = None
    
    # Execution
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    
    # Task instances
    task_instance_ids: List[str] = field(default_factory=list)
    
    # Metrics
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    skipped_tasks: int = 0
    
    # Configuration override
    config_override: Dict[str, Any] = field(default_factory=dict)
    
    # External trigger
    external_trigger_id: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TaskInstance:
    """Экземпляр задачи"""
    instance_id: str
    
    # Task
    task_id: str = ""
    task_name: str = ""
    
    # Run
    run_id: str = ""
    pipeline_id: str = ""
    
    # State
    state: TaskState = TaskState.PENDING
    
    # Execution
    try_number: int = 1
    max_tries: int = 3
    
    # Time
    queued_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    
    # Duration
    duration_seconds: float = 0.0
    
    # Result
    return_value: Any = None
    exception: str = ""
    
    # Worker
    worker_id: str = ""
    worker_host: str = ""
    
    # Logs
    log_url: str = ""
    
    # XCom (cross-communication)
    xcom_data: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DataLineage:
    """Происхождение данных"""
    lineage_id: str
    
    # Run
    run_id: str = ""
    task_id: str = ""
    
    # Source
    source_type: str = ""  # table, file, api
    source_name: str = ""
    source_schema: str = ""
    
    # Target
    target_type: str = ""
    target_name: str = ""
    target_schema: str = ""
    
    # Transformation
    transformation_type: str = ""  # read, write, transform
    
    # Stats
    rows_read: int = 0
    rows_written: int = 0
    
    # Timestamps
    recorded_at: datetime = field(default_factory=datetime.now)


@dataclass
class DataQualityResult:
    """Результат проверки качества"""
    result_id: str
    
    # Instance
    task_instance_id: str = ""
    
    # Check
    check_type: DataQualityCheckType = DataQualityCheckType.NOT_NULL
    check_name: str = ""
    
    # Target
    dataset: str = ""
    column: str = ""
    
    # Result
    passed: bool = True
    actual_value: Any = None
    expected_value: Any = None
    
    # Threshold
    threshold: float = 0.0
    
    # Timestamps
    executed_at: datetime = field(default_factory=datetime.now)


@dataclass
class ResourcePool:
    """Пул ресурсов"""
    pool_id: str
    name: str
    
    # Slots
    total_slots: int = 10
    used_slots: int = 0
    
    # Queue
    queued_tasks: int = 0
    
    # Description
    description: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SensorState:
    """Состояние сенсора"""
    sensor_id: str
    
    # Task
    task_id: str = ""
    run_id: str = ""
    
    # Poke
    poke_count: int = 0
    poke_interval_seconds: int = 60
    last_poke: Optional[datetime] = None
    
    # Condition
    condition_met: bool = False
    
    # Timeout
    timeout_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PipelineAlert:
    """Алерт пайплайна"""
    alert_id: str
    
    # Source
    pipeline_id: str = ""
    run_id: str = ""
    task_id: str = ""
    
    # Type
    alert_type: str = ""  # task_failed, sla_miss, pipeline_failed
    
    # Severity
    severity: str = "warning"  # info, warning, error, critical
    
    # Message
    message: str = ""
    
    # Recipients
    recipients: List[str] = field(default_factory=list)
    
    # Status
    acknowledged: bool = False
    acknowledged_by: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None


@dataclass
class Plugin:
    """Плагин"""
    plugin_id: str
    name: str
    
    # Type
    plugin_type: str = ""  # operator, hook, sensor
    
    # Version
    version: str = "1.0.0"
    
    # Module
    module_path: str = ""
    
    # Status
    is_enabled: bool = True
    
    # Description
    description: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


class PipelineOrchestrator:
    """Оркестратор пайплайнов"""
    
    def __init__(self):
        self.pipelines: Dict[str, Pipeline] = {}
        self.tasks: Dict[str, TaskDefinition] = {}
        self.runs: Dict[str, PipelineRun] = {}
        self.task_instances: Dict[str, TaskInstance] = {}
        self.lineage: Dict[str, DataLineage] = {}
        self.quality_results: Dict[str, DataQualityResult] = {}
        self.pools: Dict[str, ResourcePool] = {}
        self.sensors: Dict[str, SensorState] = {}
        self.alerts: List[PipelineAlert] = []
        self.plugins: Dict[str, Plugin] = {}
        
        # Initialize default pool
        self.pools["default"] = ResourcePool(
            pool_id="pool_default",
            name="default",
            total_slots=128,
            description="Default execution pool"
        )
        
    async def create_task(self, name: str,
                         operator_type: OperatorType = OperatorType.PYTHON,
                         config: Dict[str, Any] = None,
                         upstream_task_ids: List[str] = None,
                         timeout_seconds: int = 3600,
                         max_retries: int = 3,
                         retry_policy: RetryPolicy = RetryPolicy.EXPONENTIAL,
                         pool: str = "default",
                         priority: int = 0,
                         owner: str = "",
                         description: str = "") -> TaskDefinition:
        """Создание задачи"""
        task = TaskDefinition(
            task_id=f"task_{uuid.uuid4().hex[:8]}",
            name=name,
            operator_type=operator_type,
            config=config or {},
            upstream_task_ids=upstream_task_ids or [],
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            retry_policy=retry_policy,
            pool=pool,
            priority=priority,
            owner=owner,
            description=description
        )
        
        # Update downstream tasks
        for upstream_id in task.upstream_task_ids:
            upstream = self.tasks.get(upstream_id)
            if upstream:
                upstream.downstream_task_ids.append(task.task_id)
                
        self.tasks[task.task_id] = task
        return task
        
    async def create_pipeline(self, name: str,
                             task_ids: List[str],
                             schedule_interval: ScheduleInterval = ScheduleInterval.DAILY,
                             cron_expression: str = "0 0 * * *",
                             start_date: datetime = None,
                             catchup: bool = False,
                             max_active_runs: int = 1,
                             concurrency: int = 16,
                             owner: str = "",
                             tags: List[str] = None,
                             description: str = "") -> Pipeline:
        """Создание пайплайна"""
        pipeline = Pipeline(
            pipeline_id=f"pipe_{uuid.uuid4().hex[:8]}",
            name=name,
            task_ids=task_ids,
            schedule_interval=schedule_interval,
            cron_expression=cron_expression,
            start_date=start_date or datetime.now(),
            catchup=catchup,
            max_active_runs=max_active_runs,
            concurrency=concurrency,
            owner=owner,
            tags=tags or [],
            description=description
        )
        
        # Calculate next run
        pipeline.next_run = self._calculate_next_run(pipeline)
        
        self.pipelines[pipeline.pipeline_id] = pipeline
        return pipeline
        
    def _calculate_next_run(self, pipeline: Pipeline) -> datetime:
        """Расчет следующего запуска"""
        now = datetime.now()
        
        if pipeline.schedule_interval == ScheduleInterval.HOURLY:
            next_run = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        elif pipeline.schedule_interval == ScheduleInterval.DAILY:
            next_run = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        elif pipeline.schedule_interval == ScheduleInterval.WEEKLY:
            days_ahead = 7 - now.weekday()
            next_run = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=days_ahead)
        elif pipeline.schedule_interval == ScheduleInterval.MONTHLY:
            if now.month == 12:
                next_run = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                next_run = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            next_run = now + timedelta(days=1)
            
        return next_run
        
    async def trigger_pipeline(self, pipeline_id: str,
                              trigger_type: TriggerType = TriggerType.MANUAL,
                              triggered_by: str = "",
                              logical_date: datetime = None,
                              config_override: Dict[str, Any] = None) -> Optional[PipelineRun]:
        """Запуск пайплайна"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline or pipeline.state != PipelineState.ACTIVE:
            return None
            
        # Check max active runs
        active_runs = [r for r in self.runs.values() 
                      if r.pipeline_id == pipeline_id and r.state == RunState.RUNNING]
        if len(active_runs) >= pipeline.max_active_runs:
            return None
            
        run = PipelineRun(
            run_id=f"run_{uuid.uuid4().hex[:12]}",
            pipeline_id=pipeline_id,
            pipeline_name=pipeline.name,
            trigger_type=trigger_type,
            triggered_by=triggered_by,
            logical_date=logical_date or datetime.now(),
            started_at=datetime.now(),
            config_override=config_override or {},
            total_tasks=len(pipeline.task_ids)
        )
        
        # Create task instances
        for task_id in pipeline.task_ids:
            task = self.tasks.get(task_id)
            if not task:
                continue
                
            instance = TaskInstance(
                instance_id=f"ti_{uuid.uuid4().hex[:12]}",
                task_id=task_id,
                task_name=task.name,
                run_id=run.run_id,
                pipeline_id=pipeline_id,
                max_tries=task.max_retries
            )
            
            run.task_instance_ids.append(instance.instance_id)
            self.task_instances[instance.instance_id] = instance
            
        self.runs[run.run_id] = run
        
        # Update pipeline
        pipeline.last_run = datetime.now()
        pipeline.next_run = self._calculate_next_run(pipeline)
        
        return run
        
    async def execute_task_instance(self, instance_id: str) -> bool:
        """Выполнение экземпляра задачи"""
        instance = self.task_instances.get(instance_id)
        if not instance or instance.state not in [TaskState.PENDING, TaskState.QUEUED, TaskState.RETRYING]:
            return False
            
        task = self.tasks.get(instance.task_id)
        if not task:
            return False
            
        # Check pool availability
        pool = self.pools.get(task.pool, self.pools["default"])
        if pool.used_slots >= pool.total_slots:
            instance.state = TaskState.QUEUED
            pool.queued_tasks += 1
            return False
            
        # Mark as running
        instance.state = TaskState.RUNNING
        instance.started_at = datetime.now()
        pool.used_slots += 1
        
        # Simulate execution
        success = random.random() > 0.1  # 90% success rate
        
        if success:
            instance.state = TaskState.SUCCESS
            instance.return_value = {"status": "completed", "records": random.randint(100, 10000)}
            
            # Record lineage
            await self._record_lineage(instance, task)
        else:
            if instance.try_number < instance.max_tries:
                instance.state = TaskState.RETRYING
                instance.try_number += 1
            else:
                instance.state = TaskState.FAILED
                instance.exception = "Simulated execution failure"
                
                # Create alert
                await self._create_alert(instance, "task_failed", "error", f"Task {task.name} failed after {instance.try_number} attempts")
                
        instance.ended_at = datetime.now()
        if instance.started_at:
            instance.duration_seconds = (instance.ended_at - instance.started_at).total_seconds()
            
        pool.used_slots -= 1
        
        # Update run
        await self._update_run_state(instance.run_id)
        
        return instance.state == TaskState.SUCCESS
        
    async def _record_lineage(self, instance: TaskInstance, task: TaskDefinition):
        """Запись происхождения данных"""
        # Simulated lineage data
        lineage = DataLineage(
            lineage_id=f"lin_{uuid.uuid4().hex[:8]}",
            run_id=instance.run_id,
            task_id=task.task_id,
            source_type="table",
            source_name=task.config.get("source_table", "source_data"),
            target_type="table",
            target_name=task.config.get("target_table", "target_data"),
            transformation_type=task.operator_type.value,
            rows_read=random.randint(1000, 50000),
            rows_written=random.randint(500, 40000)
        )
        
        self.lineage[lineage.lineage_id] = lineage
        
    async def _create_alert(self, instance: TaskInstance,
                           alert_type: str,
                           severity: str,
                           message: str):
        """Создание алерта"""
        task = self.tasks.get(instance.task_id)
        
        alert = PipelineAlert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            pipeline_id=instance.pipeline_id,
            run_id=instance.run_id,
            task_id=instance.task_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            recipients=[task.owner] if task else []
        )
        
        self.alerts.append(alert)
        
    async def _update_run_state(self, run_id: str):
        """Обновление состояния запуска"""
        run = self.runs.get(run_id)
        if not run:
            return
            
        completed = 0
        failed = 0
        skipped = 0
        
        all_done = True
        
        for instance_id in run.task_instance_ids:
            instance = self.task_instances.get(instance_id)
            if not instance:
                continue
                
            if instance.state == TaskState.SUCCESS:
                completed += 1
            elif instance.state == TaskState.FAILED:
                failed += 1
            elif instance.state == TaskState.SKIPPED:
                skipped += 1
            elif instance.state in [TaskState.PENDING, TaskState.RUNNING, TaskState.QUEUED, TaskState.RETRYING]:
                all_done = False
                
        run.completed_tasks = completed
        run.failed_tasks = failed
        run.skipped_tasks = skipped
        
        if all_done:
            run.ended_at = datetime.now()
            if failed == 0:
                run.state = RunState.SUCCESS
            elif completed == 0:
                run.state = RunState.FAILED
            else:
                run.state = RunState.PARTIAL
                
    async def pause_pipeline(self, pipeline_id: str) -> bool:
        """Пауза пайплайна"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            return False
            
        pipeline.state = PipelineState.PAUSED
        return True
        
    async def resume_pipeline(self, pipeline_id: str) -> bool:
        """Возобновление пайплайна"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            return False
            
        pipeline.state = PipelineState.ACTIVE
        pipeline.next_run = self._calculate_next_run(pipeline)
        return True
        
    async def cancel_run(self, run_id: str) -> bool:
        """Отмена запуска"""
        run = self.runs.get(run_id)
        if not run or run.state != RunState.RUNNING:
            return False
            
        run.state = RunState.CANCELLED
        run.ended_at = datetime.now()
        
        # Cancel all pending instances
        for instance_id in run.task_instance_ids:
            instance = self.task_instances.get(instance_id)
            if instance and instance.state in [TaskState.PENDING, TaskState.QUEUED]:
                instance.state = TaskState.CANCELLED
                
        return True
        
    async def backfill(self, pipeline_id: str,
                      start_date: datetime,
                      end_date: datetime,
                      triggered_by: str = "") -> List[PipelineRun]:
        """Запуск исторических запусков"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            return []
            
        runs = []
        current_date = start_date
        
        while current_date <= end_date:
            run = await self.trigger_pipeline(
                pipeline_id,
                TriggerType.BACKFILL,
                triggered_by,
                current_date
            )
            
            if run:
                runs.append(run)
                
            # Increment by schedule interval
            if pipeline.schedule_interval == ScheduleInterval.HOURLY:
                current_date += timedelta(hours=1)
            elif pipeline.schedule_interval == ScheduleInterval.DAILY:
                current_date += timedelta(days=1)
            elif pipeline.schedule_interval == ScheduleInterval.WEEKLY:
                current_date += timedelta(weeks=1)
            else:
                current_date += timedelta(days=1)
                
        return runs
        
    async def add_quality_check(self, task_id: str,
                               check_type: DataQualityCheckType,
                               check_name: str,
                               dataset: str,
                               column: str = "",
                               expected_value: Any = None,
                               threshold: float = 0.0) -> bool:
        """Добавление проверки качества"""
        task = self.tasks.get(task_id)
        if not task:
            return False
            
        check = {
            "check_type": check_type.value,
            "check_name": check_name,
            "dataset": dataset,
            "column": column,
            "expected_value": expected_value,
            "threshold": threshold
        }
        
        task.quality_checks.append(check)
        return True
        
    async def run_quality_check(self, task_instance_id: str,
                               check: Dict[str, Any]) -> DataQualityResult:
        """Выполнение проверки качества"""
        result = DataQualityResult(
            result_id=f"qc_{uuid.uuid4().hex[:8]}",
            task_instance_id=task_instance_id,
            check_type=DataQualityCheckType(check.get("check_type", "custom")),
            check_name=check.get("check_name", ""),
            dataset=check.get("dataset", ""),
            column=check.get("column", ""),
            expected_value=check.get("expected_value"),
            threshold=check.get("threshold", 0.0),
            passed=random.random() > 0.05,  # 95% pass rate
            actual_value=random.randint(95, 100)
        )
        
        self.quality_results[result.result_id] = result
        return result
        
    async def create_pool(self, name: str,
                         total_slots: int,
                         description: str = "") -> ResourcePool:
        """Создание пула ресурсов"""
        pool = ResourcePool(
            pool_id=f"pool_{uuid.uuid4().hex[:8]}",
            name=name,
            total_slots=total_slots,
            description=description
        )
        
        self.pools[pool.name] = pool
        return pool
        
    async def register_plugin(self, name: str,
                             plugin_type: str,
                             module_path: str,
                             version: str = "1.0.0",
                             description: str = "") -> Plugin:
        """Регистрация плагина"""
        plugin = Plugin(
            plugin_id=f"plug_{uuid.uuid4().hex[:8]}",
            name=name,
            plugin_type=plugin_type,
            version=version,
            module_path=module_path,
            description=description
        )
        
        self.plugins[plugin.plugin_id] = plugin
        return plugin
        
    def get_task_dependencies(self, task_id: str) -> Dict[str, List[str]]:
        """Получение зависимостей задачи"""
        task = self.tasks.get(task_id)
        if not task:
            return {"upstream": [], "downstream": []}
            
        return {
            "upstream": task.upstream_task_ids,
            "downstream": task.downstream_task_ids
        }
        
    def get_lineage_for_run(self, run_id: str) -> List[DataLineage]:
        """Получение происхождения данных для запуска"""
        return [lin for lin in self.lineage.values() if lin.run_id == run_id]
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_pipelines = len(self.pipelines)
        active_pipelines = sum(1 for p in self.pipelines.values() if p.state == PipelineState.ACTIVE)
        
        total_tasks = len(self.tasks)
        
        total_runs = len(self.runs)
        running_runs = sum(1 for r in self.runs.values() if r.state == RunState.RUNNING)
        successful_runs = sum(1 for r in self.runs.values() if r.state == RunState.SUCCESS)
        failed_runs = sum(1 for r in self.runs.values() if r.state == RunState.FAILED)
        
        total_instances = len(self.task_instances)
        successful_instances = sum(1 for i in self.task_instances.values() if i.state == TaskState.SUCCESS)
        failed_instances = sum(1 for i in self.task_instances.values() if i.state == TaskState.FAILED)
        
        # Pool usage
        pool_usage = {}
        for name, pool in self.pools.items():
            pool_usage[name] = {
                "used": pool.used_slots,
                "total": pool.total_slots,
                "queued": pool.queued_tasks
            }
            
        total_lineage = len(self.lineage)
        total_quality_checks = len(self.quality_results)
        passed_checks = sum(1 for q in self.quality_results.values() if q.passed)
        
        total_alerts = len(self.alerts)
        unacknowledged = sum(1 for a in self.alerts if not a.acknowledged)
        
        total_plugins = len(self.plugins)
        enabled_plugins = sum(1 for p in self.plugins.values() if p.is_enabled)
        
        return {
            "total_pipelines": total_pipelines,
            "active_pipelines": active_pipelines,
            "total_tasks": total_tasks,
            "total_runs": total_runs,
            "running_runs": running_runs,
            "successful_runs": successful_runs,
            "failed_runs": failed_runs,
            "total_task_instances": total_instances,
            "successful_instances": successful_instances,
            "failed_instances": failed_instances,
            "pool_usage": pool_usage,
            "total_lineage_records": total_lineage,
            "total_quality_checks": total_quality_checks,
            "passed_quality_checks": passed_checks,
            "total_alerts": total_alerts,
            "unacknowledged_alerts": unacknowledged,
            "total_plugins": total_plugins,
            "enabled_plugins": enabled_plugins
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 343: Data Pipeline Orchestrator")
    print("=" * 60)
    
    orchestrator = PipelineOrchestrator()
    print("✓ Pipeline Orchestrator initialized")
    
    # Create Resource Pools
    print("\n🏊 Creating Resource Pools...")
    
    pools_data = [
        ("spark_pool", 32, "Pool for Spark jobs"),
        ("sql_pool", 64, "Pool for SQL queries"),
        ("api_pool", 16, "Pool for API calls"),
        ("heavy_pool", 8, "Pool for resource-intensive tasks")
    ]
    
    for name, slots, desc in pools_data:
        pool = await orchestrator.create_pool(name, slots, desc)
        print(f"  🏊 {name} ({slots} slots)")
        
    # Register Plugins
    print("\n🔌 Registering Plugins...")
    
    plugins_data = [
        ("SparkOperator", "operator", "plugins.spark.SparkOperator", "Spark job operator"),
        ("S3Hook", "hook", "plugins.aws.S3Hook", "AWS S3 connection hook"),
        ("FileSensor", "sensor", "plugins.sensors.FileSensor", "File availability sensor"),
        ("SlackHook", "hook", "plugins.slack.SlackHook", "Slack notification hook"),
        ("BigQueryOperator", "operator", "plugins.gcp.BigQueryOperator", "BigQuery operator")
    ]
    
    for name, ptype, path, desc in plugins_data:
        plugin = await orchestrator.register_plugin(name, ptype, path, "1.0.0", desc)
        print(f"  🔌 {name} ({ptype})")
        
    # Create Tasks
    print("\n📝 Creating Tasks...")
    
    # ETL Pipeline tasks
    extract_task = await orchestrator.create_task(
        "Extract Source Data",
        OperatorType.SQL,
        {"source_table": "raw_events", "query": "SELECT * FROM raw_events"},
        [],
        3600, 3, RetryPolicy.EXPONENTIAL, "sql_pool", 1,
        "data-team", "Extract data from source database"
    )
    
    transform_task = await orchestrator.create_task(
        "Transform Data",
        OperatorType.SPARK,
        {"transformation": "aggregate_events", "target_table": "agg_events"},
        [extract_task.task_id],
        7200, 2, RetryPolicy.EXPONENTIAL, "spark_pool", 2,
        "data-team", "Transform and aggregate event data"
    )
    
    quality_task = await orchestrator.create_task(
        "Data Quality Checks",
        OperatorType.PYTHON,
        {"checks": ["null_check", "range_check"]},
        [transform_task.task_id],
        1800, 3, RetryPolicy.LINEAR, "default", 3,
        "data-team", "Run data quality validations"
    )
    
    load_task = await orchestrator.create_task(
        "Load to Data Warehouse",
        OperatorType.SQL,
        {"target_table": "dwh.events_fact", "mode": "append"},
        [quality_task.task_id],
        3600, 3, RetryPolicy.EXPONENTIAL, "sql_pool", 4,
        "data-team", "Load data to warehouse"
    )
    
    notify_task = await orchestrator.create_task(
        "Send Notification",
        OperatorType.HTTP,
        {"webhook_url": "https://slack.com/webhook", "message": "Pipeline complete"},
        [load_task.task_id],
        300, 2, RetryPolicy.LINEAR, "api_pool", 5,
        "data-team", "Send completion notification"
    )
    
    tasks = [extract_task, transform_task, quality_task, load_task, notify_task]
    
    for task in tasks:
        print(f"  📝 {task.name} ({task.operator_type.value})")
        
    # Add quality checks to task
    await orchestrator.add_quality_check(
        quality_task.task_id, DataQualityCheckType.NOT_NULL, "Null Check",
        "agg_events", "event_id"
    )
    await orchestrator.add_quality_check(
        quality_task.task_id, DataQualityCheckType.RANGE, "Value Range",
        "agg_events", "event_count", {"min": 0, "max": 1000000}, 99.0
    )
    
    # Create more tasks for ML Pipeline
    feature_extract = await orchestrator.create_task(
        "Feature Extraction",
        OperatorType.SPARK,
        {"features": ["user_features", "item_features"]},
        [],
        5400, 2, RetryPolicy.EXPONENTIAL, "spark_pool", 1,
        "ml-team", "Extract ML features"
    )
    
    model_train = await orchestrator.create_task(
        "Model Training",
        OperatorType.PYTHON,
        {"model": "recommendation_model", "epochs": 10},
        [feature_extract.task_id],
        14400, 1, RetryPolicy.NONE, "heavy_pool", 2,
        "ml-team", "Train ML model"
    )
    
    model_evaluate = await orchestrator.create_task(
        "Model Evaluation",
        OperatorType.PYTHON,
        {"metrics": ["accuracy", "precision", "recall"]},
        [model_train.task_id],
        1800, 3, RetryPolicy.LINEAR, "default", 3,
        "ml-team", "Evaluate model performance"
    )
    
    model_deploy = await orchestrator.create_task(
        "Model Deployment",
        OperatorType.HTTP,
        {"endpoint": "model-server", "version": "v1"},
        [model_evaluate.task_id],
        600, 3, RetryPolicy.EXPONENTIAL, "api_pool", 4,
        "ml-team", "Deploy model to production"
    )
    
    ml_tasks = [feature_extract, model_train, model_evaluate, model_deploy]
    
    # Create Pipelines
    print("\n📊 Creating Pipelines...")
    
    etl_pipeline = await orchestrator.create_pipeline(
        "Daily ETL Pipeline",
        [t.task_id for t in tasks],
        ScheduleInterval.DAILY,
        "0 2 * * *",
        datetime.now() - timedelta(days=7),
        False, 1, 16,
        "data-team",
        ["etl", "production", "daily"],
        "Daily data pipeline for event processing"
    )
    
    ml_pipeline = await orchestrator.create_pipeline(
        "ML Training Pipeline",
        [t.task_id for t in ml_tasks],
        ScheduleInterval.WEEKLY,
        "0 3 * * 0",
        datetime.now() - timedelta(days=30),
        False, 1, 8,
        "ml-team",
        ["ml", "training", "weekly"],
        "Weekly ML model training pipeline"
    )
    
    hourly_pipeline = await orchestrator.create_pipeline(
        "Hourly Metrics Pipeline",
        [extract_task.task_id, transform_task.task_id],
        ScheduleInterval.HOURLY,
        "0 * * * *",
        datetime.now() - timedelta(hours=12),
        False, 2, 8,
        "analytics-team",
        ["metrics", "hourly"],
        "Hourly metrics aggregation"
    )
    
    pipelines = [etl_pipeline, ml_pipeline, hourly_pipeline]
    
    for pipeline in pipelines:
        print(f"  📊 {pipeline.name} ({pipeline.schedule_interval.value})")
        
    # Trigger Pipeline Runs
    print("\n🚀 Triggering Pipeline Runs...")
    
    runs = []
    
    # Manual trigger
    run1 = await orchestrator.trigger_pipeline(
        etl_pipeline.pipeline_id,
        TriggerType.MANUAL,
        "admin"
    )
    if run1:
        runs.append(run1)
        print(f"  🚀 {etl_pipeline.name} - Manual trigger")
        
    # Scheduled trigger
    run2 = await orchestrator.trigger_pipeline(
        ml_pipeline.pipeline_id,
        TriggerType.SCHEDULED
    )
    if run2:
        runs.append(run2)
        print(f"  🚀 {ml_pipeline.name} - Scheduled trigger")
        
    # Multiple hourly runs
    for i in range(3):
        run = await orchestrator.trigger_pipeline(
            hourly_pipeline.pipeline_id,
            TriggerType.SCHEDULED,
            "",
            datetime.now() - timedelta(hours=i)
        )
        if run:
            runs.append(run)
            print(f"  🚀 {hourly_pipeline.name} - Hour -{i}")
            
    # Execute Task Instances
    print("\n⚡ Executing Task Instances...")
    
    executed = 0
    for run in runs:
        for instance_id in run.task_instance_ids:
            success = await orchestrator.execute_task_instance(instance_id)
            executed += 1
            
    print(f"  ⚡ Executed {executed} task instances")
    
    # Run Backfill
    print("\n📅 Running Backfill...")
    
    backfill_runs = await orchestrator.backfill(
        etl_pipeline.pipeline_id,
        datetime.now() - timedelta(days=3),
        datetime.now() - timedelta(days=1),
        "admin"
    )
    
    print(f"  📅 Created {len(backfill_runs)} backfill runs")
    
    # Execute backfill tasks
    for run in backfill_runs[:1]:  # Execute first backfill
        for instance_id in run.task_instance_ids:
            await orchestrator.execute_task_instance(instance_id)
            
    # Run Quality Checks
    print("\n✅ Running Quality Checks...")
    
    qc_count = 0
    for instance in orchestrator.task_instances.values():
        if instance.state == TaskState.SUCCESS:
            task = orchestrator.tasks.get(instance.task_id)
            if task and task.quality_checks:
                for check in task.quality_checks:
                    result = await orchestrator.run_quality_check(instance.instance_id, check)
                    qc_count += 1
                    
    print(f"  ✅ Ran {qc_count} quality checks")
    
    # Pipelines Dashboard
    print("\n📊 Pipelines:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                         │ Schedule │ Tasks │ State  │ Last Run             │ Next Run             │ Owner               │ Tags                                                                  │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for pipeline in pipelines:
        name = pipeline.name[:28].ljust(28)
        schedule = pipeline.schedule_interval.value[:8].ljust(8)
        tasks_count = str(len(pipeline.task_ids)).ljust(5)
        
        state_icons = {"active": "🟢", "paused": "🟡", "disabled": "⚫"}
        state_icon = state_icons.get(pipeline.state.value, "⚪")
        state = f"{state_icon}".ljust(6)
        
        last_run = pipeline.last_run.strftime("%Y-%m-%d %H:%M") if pipeline.last_run else "Never"
        last_run = last_run[:20].ljust(20)
        
        next_run = pipeline.next_run.strftime("%Y-%m-%d %H:%M") if pipeline.next_run else "N/A"
        next_run = next_run[:20].ljust(20)
        
        owner = pipeline.owner[:19].ljust(19)
        tags = ", ".join(pipeline.tags[:3])[:69].ljust(69)
        
        print(f"  │ {name} │ {schedule} │ {tasks_count} │ {state} │ {last_run} │ {next_run} │ {owner} │ {tags} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Task Definitions
    print("\n📝 Task Definitions:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                         │ Operator    │ Pool         │ Priority │ Timeout │ Retries │ Upstream Tasks │ Description                                                                     │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    all_tasks = tasks + ml_tasks
    for task in all_tasks:
        name = task.name[:28].ljust(28)
        op = task.operator_type.value[:11].ljust(11)
        pool = task.pool[:12].ljust(12)
        priority = str(task.priority).ljust(8)
        timeout = f"{task.timeout_seconds}s".ljust(7)
        retries = str(task.max_retries).ljust(7)
        upstream = str(len(task.upstream_task_ids)).ljust(14)
        desc = task.description[:81].ljust(81)
        
        print(f"  │ {name} │ {op} │ {pool} │ {priority} │ {timeout} │ {retries} │ {upstream} │ {desc} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Pipeline Runs
    print("\n🚀 Pipeline Runs:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Pipeline                     │ Trigger    │ State     │ Started              │ Tasks │ Completed │ Failed │ Logical Date         │ Triggered By          │ Status                                                          │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    all_runs = list(orchestrator.runs.values())[:10]
    for run in all_runs:
        pipeline = run.pipeline_name[:28].ljust(28)
        trigger = run.trigger_type.value[:10].ljust(10)
        
        state_icons = {"running": "🔄", "success": "✓", "failed": "✗", "partial": "◐", "cancelled": "⊘"}
        state_icon = state_icons.get(run.state.value, "?")
        state = f"{state_icon} {run.state.value}"[:9].ljust(9)
        
        started = run.started_at.strftime("%Y-%m-%d %H:%M") if run.started_at else "N/A"
        started = started[:20].ljust(20)
        
        tasks_total = str(run.total_tasks).ljust(5)
        completed = str(run.completed_tasks).ljust(9)
        failed = str(run.failed_tasks).ljust(6)
        
        logical = run.logical_date.strftime("%Y-%m-%d %H:%M")[:20].ljust(20)
        triggered = run.triggered_by[:21].ljust(21) if run.triggered_by else "scheduler".ljust(21)
        
        status = "Running" if run.state == RunState.RUNNING else run.state.value.capitalize()
        status = status[:65].ljust(65)
        
        print(f"  │ {pipeline} │ {trigger} │ {state} │ {started} │ {tasks_total} │ {completed} │ {failed} │ {logical} │ {triggered} │ {status} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Task Instances
    print("\n⚡ Recent Task Instances:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Task                         │ Pipeline                     │ State     │ Try │ Started              │ Duration │ Worker        │ Return Value                                                                                              │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    instances = list(orchestrator.task_instances.values())[:12]
    for inst in instances:
        task_name = inst.task_name[:28].ljust(28)
        
        run = orchestrator.runs.get(inst.run_id)
        pipeline = run.pipeline_name if run else "N/A"
        pipeline = pipeline[:28].ljust(28)
        
        state_icons = {"success": "✓", "failed": "✗", "running": "🔄", "pending": "⏳", "queued": "📋", "skipped": "⊘", "retrying": "↻"}
        state_icon = state_icons.get(inst.state.value, "?")
        state = f"{state_icon} {inst.state.value}"[:9].ljust(9)
        
        try_num = str(inst.try_number).ljust(3)
        
        started = inst.started_at.strftime("%H:%M:%S") if inst.started_at else "N/A"
        started = started[:20].ljust(20)
        
        duration = f"{inst.duration_seconds:.1f}s" if inst.duration_seconds > 0 else "N/A"
        duration = duration[:8].ljust(8)
        
        worker = inst.worker_id[:13].ljust(13) if inst.worker_id else "N/A".ljust(13)
        
        ret_val = str(inst.return_value)[:106] if inst.return_value else "N/A"
        ret_val = ret_val.ljust(106)
        
        print(f"  │ {task_name} │ {pipeline} │ {state} │ {try_num} │ {started} │ {duration} │ {worker} │ {ret_val} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Data Lineage
    print("\n🔗 Data Lineage Records:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Source                       │ Target                       │ Transform   │ Rows Read  │ Rows Written │ Task                         │ Recorded At          │ Status                                       │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    lineage_records = list(orchestrator.lineage.values())[:8]
    for lin in lineage_records:
        source = lin.source_name[:28].ljust(28)
        target = lin.target_name[:28].ljust(28)
        transform = lin.transformation_type[:11].ljust(11)
        rows_r = str(lin.rows_read).ljust(10)
        rows_w = str(lin.rows_written).ljust(12)
        
        task = orchestrator.tasks.get(lin.task_id)
        task_name = task.name if task else lin.task_id
        task_name = task_name[:28].ljust(28)
        
        recorded = lin.recorded_at.strftime("%Y-%m-%d %H:%M")[:20].ljust(20)
        status = "✓ Recorded".ljust(46)
        
        print(f"  │ {source} │ {target} │ {transform} │ {rows_r} │ {rows_w} │ {task_name} │ {recorded} │ {status} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Resource Pools
    print("\n🏊 Resource Pools:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Pool Name         │ Total Slots │ Used Slots │ Queued │ Utilization │ Description                                                      │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for pool in orchestrator.pools.values():
        name = pool.name[:17].ljust(17)
        total = str(pool.total_slots).ljust(11)
        used = str(pool.used_slots).ljust(10)
        queued = str(pool.queued_tasks).ljust(6)
        util = f"{(pool.used_slots / pool.total_slots * 100):.1f}%".ljust(11)
        desc = pool.description[:66].ljust(66)
        
        print(f"  │ {name} │ {total} │ {used} │ {queued} │ {util} │ {desc} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Statistics
    stats = orchestrator.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Pipelines: {stats['active_pipelines']}/{stats['total_pipelines']} active")
    print(f"  Tasks: {stats['total_tasks']}")
    print(f"  Pipeline Runs: {stats['running_runs']} running, {stats['successful_runs']} successful, {stats['failed_runs']} failed")
    print(f"  Task Instances: {stats['successful_instances']} successful, {stats['failed_instances']} failed")
    print(f"  Lineage Records: {stats['total_lineage_records']}")
    print(f"  Quality Checks: {stats['passed_quality_checks']}/{stats['total_quality_checks']} passed")
    print(f"  Alerts: {stats['unacknowledged_alerts']} unacknowledged")
    print(f"  Plugins: {stats['enabled_plugins']}/{stats['total_plugins']} enabled")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Data Pipeline Orchestrator                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Active Pipelines:             {stats['active_pipelines']:>12}                      │")
    print(f"│ Total Tasks:                  {stats['total_tasks']:>12}                      │")
    print(f"│ Running Runs:                 {stats['running_runs']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Successful Runs:              {stats['successful_runs']:>12}                      │")
    print(f"│ Failed Runs:                  {stats['failed_runs']:>12}                      │")
    print(f"│ Quality Checks Passed:   {stats['passed_quality_checks']:>5} / {stats['total_quality_checks']:<5}                          │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Data Pipeline Orchestrator initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
