#!/usr/bin/env python3
"""
Server Init - Iteration 156: Data Pipeline Platform
Платформа конвейеров данных

Функционал:
- Pipeline Definition - определение конвейеров
- DAG Management - управление DAG
- Task Scheduling - планирование задач
- Data Transformation - трансформация данных
- Backfill Support - поддержка бэкфилла
- Pipeline Monitoring - мониторинг конвейеров
- Data Quality Checks - проверки качества данных
- Retry Mechanism - механизм повторных попыток
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid


class TaskStatus(Enum):
    """Статус задачи"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"
    UPSTREAM_FAILED = "upstream_failed"


class PipelineStatus(Enum):
    """Статус конвейера"""
    INACTIVE = "inactive"
    ACTIVE = "active"
    PAUSED = "paused"
    RUNNING = "running"


class TriggerType(Enum):
    """Тип триггера"""
    SCHEDULE = "schedule"
    MANUAL = "manual"
    EVENT = "event"
    DEPENDENCY = "dependency"


class DataFormat(Enum):
    """Формат данных"""
    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"
    AVRO = "avro"
    ORC = "orc"


class QualityCheckType(Enum):
    """Тип проверки качества"""
    NOT_NULL = "not_null"
    UNIQUE = "unique"
    IN_RANGE = "in_range"
    REGEX_MATCH = "regex_match"
    CUSTOM = "custom"


@dataclass
class Task:
    """Задача конвейера"""
    task_id: str
    name: str = ""
    
    # Pipeline
    pipeline_id: str = ""
    
    # Dependencies
    upstream_tasks: List[str] = field(default_factory=list)
    downstream_tasks: List[str] = field(default_factory=list)
    
    # Execution
    operator: str = ""  # python, sql, bash, transfer
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Retry
    retries: int = 3
    retry_delay: int = 60  # seconds
    
    # Timeout
    timeout: int = 3600  # seconds
    
    # Status
    status: TaskStatus = TaskStatus.PENDING
    attempts: int = 0
    
    # Results
    output: Any = None
    error: str = ""
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Pool/Resources
    pool: str = "default"
    priority: int = 0


@dataclass
class Pipeline:
    """Конвейер данных"""
    pipeline_id: str
    name: str = ""
    
    # Tasks
    tasks: Dict[str, Task] = field(default_factory=dict)
    
    # Schedule
    schedule: str = ""  # cron expression
    trigger_type: TriggerType = TriggerType.SCHEDULE
    
    # Status
    status: PipelineStatus = PipelineStatus.INACTIVE
    
    # Config
    max_active_runs: int = 1
    catchup: bool = False
    
    # Defaults
    default_retries: int = 3
    default_timeout: int = 3600
    
    # Metadata
    description: str = ""
    owner: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Statistics
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_run: Optional[datetime] = None


@dataclass
class PipelineRun:
    """Запуск конвейера"""
    run_id: str
    pipeline_id: str = ""
    
    # Trigger
    trigger_type: TriggerType = TriggerType.MANUAL
    triggered_by: str = ""
    
    # Task instances
    task_instances: Dict[str, TaskInstance] = field(default_factory=dict)
    
    # Status
    status: TaskStatus = TaskStatus.PENDING
    
    # Timing
    scheduled_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Parameters
    conf: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskInstance:
    """Экземпляр задачи"""
    instance_id: str
    task_id: str = ""
    run_id: str = ""
    
    # Status
    status: TaskStatus = TaskStatus.PENDING
    attempts: int = 0
    
    # Results
    output: Any = None
    error: str = ""
    logs: List[str] = field(default_factory=list)
    
    # Timing
    queued_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class DataQualityCheck:
    """Проверка качества данных"""
    check_id: str
    name: str = ""
    
    # Type
    check_type: QualityCheckType = QualityCheckType.NOT_NULL
    
    # Parameters
    column: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Result
    passed: bool = False
    message: str = ""
    
    # Blocking
    blocking: bool = True


@dataclass
class DataSource:
    """Источник данных"""
    source_id: str
    name: str = ""
    
    # Type
    source_type: str = ""  # database, file, api, stream
    
    # Connection
    connection_string: str = ""
    credentials: Dict[str, str] = field(default_factory=dict)
    
    # Format
    data_format: DataFormat = DataFormat.JSON


@dataclass
class Transformation:
    """Трансформация данных"""
    transform_id: str
    name: str = ""
    
    # Type
    transform_type: str = ""  # map, filter, aggregate, join
    
    # Logic
    logic: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)


class DAGBuilder:
    """Построитель DAG"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.edges: List[tuple] = []
        
    def add_task(self, task: Task) -> 'DAGBuilder':
        """Добавление задачи"""
        self.tasks[task.task_id] = task
        return self
        
    def add_dependency(self, upstream: str, downstream: str) -> 'DAGBuilder':
        """Добавление зависимости"""
        self.edges.append((upstream, downstream))
        
        if upstream in self.tasks:
            self.tasks[upstream].downstream_tasks.append(downstream)
        if downstream in self.tasks:
            self.tasks[downstream].upstream_tasks.append(upstream)
            
        return self
        
    def build(self) -> Dict[str, Task]:
        """Построение DAG"""
        # Validate DAG (no cycles)
        if self._has_cycle():
            raise ValueError("DAG contains a cycle")
        return self.tasks
        
    def _has_cycle(self) -> bool:
        """Проверка на циклы"""
        visited = set()
        rec_stack = set()
        
        def dfs(task_id: str) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)
            
            task = self.tasks.get(task_id)
            if task:
                for downstream in task.downstream_tasks:
                    if downstream not in visited:
                        if dfs(downstream):
                            return True
                    elif downstream in rec_stack:
                        return True
                        
            rec_stack.remove(task_id)
            return False
            
        for task_id in self.tasks:
            if task_id not in visited:
                if dfs(task_id):
                    return True
        return False
        
    def get_execution_order(self) -> List[List[str]]:
        """Получение порядка выполнения"""
        # Topological sort with levels
        in_degree = {t: 0 for t in self.tasks}
        
        for task in self.tasks.values():
            for downstream in task.downstream_tasks:
                if downstream in in_degree:
                    in_degree[downstream] += 1
                    
        levels = []
        remaining = set(self.tasks.keys())
        
        while remaining:
            # Find tasks with no remaining dependencies
            level = [t for t in remaining if in_degree[t] == 0]
            
            if not level:
                break
                
            levels.append(level)
            
            for t in level:
                remaining.remove(t)
                task = self.tasks[t]
                for downstream in task.downstream_tasks:
                    if downstream in in_degree:
                        in_degree[downstream] -= 1
                        
        return levels


class PipelineManager:
    """Менеджер конвейеров"""
    
    def __init__(self):
        self.pipelines: Dict[str, Pipeline] = {}
        self.runs: Dict[str, PipelineRun] = {}
        
    def create_pipeline(self, name: str, **kwargs) -> Pipeline:
        """Создание конвейера"""
        pipeline = Pipeline(
            pipeline_id=f"pipe_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        self.pipelines[pipeline.pipeline_id] = pipeline
        return pipeline
        
    def add_task(self, pipeline_id: str, task: Task) -> Task:
        """Добавление задачи"""
        if pipeline_id in self.pipelines:
            task.pipeline_id = pipeline_id
            self.pipelines[pipeline_id].tasks[task.task_id] = task
        return task
        
    def trigger_run(self, pipeline_id: str, conf: Dict = None,
                     trigger_type: TriggerType = TriggerType.MANUAL,
                     triggered_by: str = "") -> Optional[PipelineRun]:
        """Запуск конвейера"""
        if pipeline_id not in self.pipelines:
            return None
            
        pipeline = self.pipelines[pipeline_id]
        
        run = PipelineRun(
            run_id=f"run_{uuid.uuid4().hex[:8]}",
            pipeline_id=pipeline_id,
            trigger_type=trigger_type,
            triggered_by=triggered_by,
            conf=conf or {}
        )
        
        # Create task instances
        for task_id, task in pipeline.tasks.items():
            instance = TaskInstance(
                instance_id=f"ti_{uuid.uuid4().hex[:8]}",
                task_id=task_id,
                run_id=run.run_id
            )
            run.task_instances[task_id] = instance
            
        self.runs[run.run_id] = run
        pipeline.total_runs += 1
        pipeline.last_run = datetime.now()
        
        return run
        
    def get_run_status(self, run_id: str) -> Dict:
        """Статус запуска"""
        if run_id not in self.runs:
            return {}
            
        run = self.runs[run_id]
        
        status_counts = {}
        for ti in run.task_instances.values():
            status = ti.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            
        return {
            "run_id": run_id,
            "status": run.status.value,
            "total_tasks": len(run.task_instances),
            "status_counts": status_counts
        }


class TaskExecutor:
    """Исполнитель задач"""
    
    def __init__(self):
        self.operators: Dict[str, Callable] = {}
        self._register_default_operators()
        
    def _register_default_operators(self):
        """Регистрация операторов"""
        self.operators["python"] = self._python_operator
        self.operators["sql"] = self._sql_operator
        self.operators["bash"] = self._bash_operator
        self.operators["transfer"] = self._transfer_operator
        self.operators["sensor"] = self._sensor_operator
        
    async def _python_operator(self, task: Task, params: Dict) -> Any:
        """Python оператор"""
        code = params.get("code", "")
        # Simulate execution
        await asyncio.sleep(0.1)
        return {"status": "executed", "code_length": len(code)}
        
    async def _sql_operator(self, task: Task, params: Dict) -> Any:
        """SQL оператор"""
        query = params.get("query", "")
        await asyncio.sleep(0.1)
        return {"rows_affected": 100, "query": query[:50]}
        
    async def _bash_operator(self, task: Task, params: Dict) -> Any:
        """Bash оператор"""
        command = params.get("command", "")
        await asyncio.sleep(0.1)
        return {"exit_code": 0, "command": command}
        
    async def _transfer_operator(self, task: Task, params: Dict) -> Any:
        """Transfer оператор"""
        source = params.get("source", "")
        destination = params.get("destination", "")
        await asyncio.sleep(0.2)
        return {"transferred": True, "records": 1000}
        
    async def _sensor_operator(self, task: Task, params: Dict) -> Any:
        """Sensor оператор"""
        condition = params.get("condition", "")
        await asyncio.sleep(0.1)
        return {"condition_met": True}
        
    async def execute(self, task: Task, instance: TaskInstance) -> bool:
        """Выполнение задачи"""
        instance.status = TaskStatus.RUNNING
        instance.started_at = datetime.now()
        instance.attempts += 1
        
        try:
            operator = self.operators.get(task.operator)
            
            if not operator:
                raise ValueError(f"Unknown operator: {task.operator}")
                
            result = await operator(task, task.parameters)
            
            instance.output = result
            instance.status = TaskStatus.SUCCESS
            instance.completed_at = datetime.now()
            
            return True
            
        except Exception as e:
            instance.error = str(e)
            
            if instance.attempts < task.retries:
                instance.status = TaskStatus.RETRYING
            else:
                instance.status = TaskStatus.FAILED
                
            instance.completed_at = datetime.now()
            
            return False


class DataQualityManager:
    """Менеджер качества данных"""
    
    def __init__(self):
        self.checks: Dict[str, DataQualityCheck] = {}
        
    def create_check(self, name: str, check_type: QualityCheckType,
                      column: str = "", **kwargs) -> DataQualityCheck:
        """Создание проверки"""
        check = DataQualityCheck(
            check_id=f"dq_{uuid.uuid4().hex[:8]}",
            name=name,
            check_type=check_type,
            column=column,
            **kwargs
        )
        self.checks[check.check_id] = check
        return check
        
    def run_check(self, check: DataQualityCheck, data: Any) -> bool:
        """Запуск проверки"""
        if check.check_type == QualityCheckType.NOT_NULL:
            return self._check_not_null(check, data)
        elif check.check_type == QualityCheckType.UNIQUE:
            return self._check_unique(check, data)
        elif check.check_type == QualityCheckType.IN_RANGE:
            return self._check_in_range(check, data)
        elif check.check_type == QualityCheckType.REGEX_MATCH:
            return self._check_regex(check, data)
        return True
        
    def _check_not_null(self, check: DataQualityCheck, data: List[Dict]) -> bool:
        """Проверка на NULL"""
        column = check.column
        null_count = sum(1 for row in data if row.get(column) is None)
        check.passed = null_count == 0
        check.message = f"Found {null_count} null values" if not check.passed else "Pass"
        return check.passed
        
    def _check_unique(self, check: DataQualityCheck, data: List[Dict]) -> bool:
        """Проверка уникальности"""
        column = check.column
        values = [row.get(column) for row in data]
        duplicates = len(values) - len(set(values))
        check.passed = duplicates == 0
        check.message = f"Found {duplicates} duplicates" if not check.passed else "Pass"
        return check.passed
        
    def _check_in_range(self, check: DataQualityCheck, data: List[Dict]) -> bool:
        """Проверка диапазона"""
        column = check.column
        min_val = check.parameters.get("min")
        max_val = check.parameters.get("max")
        
        out_of_range = 0
        for row in data:
            val = row.get(column)
            if val is not None:
                if min_val is not None and val < min_val:
                    out_of_range += 1
                if max_val is not None and val > max_val:
                    out_of_range += 1
                    
        check.passed = out_of_range == 0
        check.message = f"Found {out_of_range} out of range" if not check.passed else "Pass"
        return check.passed
        
    def _check_regex(self, check: DataQualityCheck, data: List[Dict]) -> bool:
        """Проверка regex"""
        import re
        column = check.column
        pattern = check.parameters.get("pattern", "")
        
        non_matching = 0
        for row in data:
            val = str(row.get(column, ""))
            if not re.match(pattern, val):
                non_matching += 1
                
        check.passed = non_matching == 0
        check.message = f"Found {non_matching} non-matching" if not check.passed else "Pass"
        return check.passed


class BackfillManager:
    """Менеджер бэкфилла"""
    
    def __init__(self, pipeline_manager: PipelineManager):
        self.manager = pipeline_manager
        
    def create_backfill(self, pipeline_id: str,
                         start_date: datetime,
                         end_date: datetime,
                         interval: timedelta) -> List[PipelineRun]:
        """Создание бэкфилла"""
        runs = []
        current = start_date
        
        while current <= end_date:
            run = self.manager.trigger_run(
                pipeline_id,
                conf={"execution_date": current.isoformat()},
                trigger_type=TriggerType.MANUAL,
                triggered_by="backfill"
            )
            
            if run:
                runs.append(run)
                
            current += interval
            
        return runs


class DataPipelinePlatform:
    """Платформа конвейеров данных"""
    
    def __init__(self):
        self.pipeline_manager = PipelineManager()
        self.executor = TaskExecutor()
        self.quality_manager = DataQualityManager()
        self.backfill_manager = BackfillManager(self.pipeline_manager)
        
    async def run_pipeline(self, run: PipelineRun) -> bool:
        """Запуск конвейера"""
        pipeline = self.pipeline_manager.pipelines.get(run.pipeline_id)
        
        if not pipeline:
            return False
            
        run.status = TaskStatus.RUNNING
        run.started_at = datetime.now()
        
        # Build execution order
        builder = DAGBuilder()
        for task in pipeline.tasks.values():
            builder.add_task(task)
            
        try:
            execution_order = builder.get_execution_order()
        except ValueError:
            run.status = TaskStatus.FAILED
            return False
            
        # Execute by levels
        all_success = True
        
        for level in execution_order:
            # Execute tasks in parallel
            tasks_to_run = []
            
            for task_id in level:
                task = pipeline.tasks[task_id]
                instance = run.task_instances[task_id]
                
                # Check upstream
                upstream_failed = False
                for upstream_id in task.upstream_tasks:
                    upstream_instance = run.task_instances.get(upstream_id)
                    if upstream_instance and upstream_instance.status == TaskStatus.FAILED:
                        upstream_failed = True
                        break
                        
                if upstream_failed:
                    instance.status = TaskStatus.UPSTREAM_FAILED
                    all_success = False
                else:
                    tasks_to_run.append((task, instance))
                    
            # Run in parallel
            if tasks_to_run:
                results = await asyncio.gather(
                    *[self.executor.execute(t, i) for t, i in tasks_to_run],
                    return_exceptions=True
                )
                
                for result in results:
                    if result is False or isinstance(result, Exception):
                        all_success = False
                        
        # Update run status
        run.completed_at = datetime.now()
        
        if all_success:
            run.status = TaskStatus.SUCCESS
            pipeline.successful_runs += 1
        else:
            run.status = TaskStatus.FAILED
            pipeline.failed_runs += 1
            
        return all_success
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        pipelines = list(self.pipeline_manager.pipelines.values())
        runs = list(self.pipeline_manager.runs.values())
        
        return {
            "total_pipelines": len(pipelines),
            "active_pipelines": len([p for p in pipelines if p.status == PipelineStatus.ACTIVE]),
            "total_runs": len(runs),
            "successful_runs": len([r for r in runs if r.status == TaskStatus.SUCCESS]),
            "failed_runs": len([r for r in runs if r.status == TaskStatus.FAILED]),
            "quality_checks": len(self.quality_manager.checks)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 156: Data Pipeline Platform")
    print("=" * 60)
    
    async def demo():
        platform = DataPipelinePlatform()
        print("✓ Data Pipeline Platform created")
        
        # Create pipeline
        print("\n📊 Creating Data Pipeline...")
        
        pipeline = platform.pipeline_manager.create_pipeline(
            name="etl_daily_sales",
            schedule="0 2 * * *",
            description="Daily sales ETL pipeline",
            owner="data-team",
            tags=["etl", "sales", "daily"]
        )
        print(f"  ✓ Pipeline: {pipeline.name}")
        
        # Create tasks
        print("\n📋 Adding Tasks...")
        
        # Extract task
        extract_task = Task(
            task_id="extract_sales",
            name="Extract Sales Data",
            operator="sql",
            parameters={
                "query": "SELECT * FROM sales WHERE date = '{{ ds }}'"
            },
            retries=3,
            retry_delay=60
        )
        platform.pipeline_manager.add_task(pipeline.pipeline_id, extract_task)
        print(f"  ✓ {extract_task.name} ({extract_task.operator})")
        
        # Transform task
        transform_task = Task(
            task_id="transform_sales",
            name="Transform Sales Data",
            operator="python",
            parameters={
                "code": "df = clean_and_transform(df)"
            },
            upstream_tasks=["extract_sales"]
        )
        platform.pipeline_manager.add_task(pipeline.pipeline_id, transform_task)
        print(f"  ✓ {transform_task.name} ({transform_task.operator})")
        
        # Quality check task
        quality_task = Task(
            task_id="quality_check",
            name="Data Quality Check",
            operator="python",
            parameters={
                "code": "run_quality_checks(df)"
            },
            upstream_tasks=["transform_sales"]
        )
        platform.pipeline_manager.add_task(pipeline.pipeline_id, quality_task)
        print(f"  ✓ {quality_task.name} ({quality_task.operator})")
        
        # Load task
        load_task = Task(
            task_id="load_warehouse",
            name="Load to Warehouse",
            operator="transfer",
            parameters={
                "source": "staging.sales",
                "destination": "warehouse.fact_sales"
            },
            upstream_tasks=["quality_check"]
        )
        platform.pipeline_manager.add_task(pipeline.pipeline_id, load_task)
        print(f"  ✓ {load_task.name} ({load_task.operator})")
        
        # Aggregation task
        aggregate_task = Task(
            task_id="aggregate_metrics",
            name="Aggregate Metrics",
            operator="sql",
            parameters={
                "query": "INSERT INTO metrics SELECT ... FROM warehouse.fact_sales"
            },
            upstream_tasks=["load_warehouse"]
        )
        platform.pipeline_manager.add_task(pipeline.pipeline_id, aggregate_task)
        print(f"  ✓ {aggregate_task.name} ({aggregate_task.operator})")
        
        # Notify task
        notify_task = Task(
            task_id="notify_complete",
            name="Send Notification",
            operator="python",
            parameters={
                "code": "send_slack_notification('ETL Complete')"
            },
            upstream_tasks=["aggregate_metrics"]
        )
        platform.pipeline_manager.add_task(pipeline.pipeline_id, notify_task)
        print(f"  ✓ {notify_task.name} ({notify_task.operator})")
        
        # Update dependencies
        extract_task.downstream_tasks = ["transform_sales"]
        transform_task.downstream_tasks = ["quality_check"]
        quality_task.downstream_tasks = ["load_warehouse"]
        load_task.downstream_tasks = ["aggregate_metrics"]
        aggregate_task.downstream_tasks = ["notify_complete"]
        
        # Build and validate DAG
        print("\n🔗 Building DAG...")
        
        builder = DAGBuilder()
        for task in pipeline.tasks.values():
            builder.add_task(task)
            
        execution_order = builder.get_execution_order()
        
        print("\n  Execution Order:")
        for i, level in enumerate(execution_order):
            tasks_str = ", ".join(level)
            print(f"    Level {i+1}: {tasks_str}")
            
        # Create quality checks
        print("\n✅ Creating Quality Checks...")
        
        not_null_check = platform.quality_manager.create_check(
            name="sales_amount_not_null",
            check_type=QualityCheckType.NOT_NULL,
            column="amount",
            blocking=True
        )
        print(f"  ✓ {not_null_check.name}")
        
        unique_check = platform.quality_manager.create_check(
            name="transaction_id_unique",
            check_type=QualityCheckType.UNIQUE,
            column="transaction_id",
            blocking=True
        )
        print(f"  ✓ {unique_check.name}")
        
        range_check = platform.quality_manager.create_check(
            name="amount_in_range",
            check_type=QualityCheckType.IN_RANGE,
            column="amount",
            parameters={"min": 0, "max": 1000000},
            blocking=False
        )
        print(f"  ✓ {range_check.name}")
        
        # Run quality checks on sample data
        print("\n🧪 Running Quality Checks...")
        
        sample_data = [
            {"transaction_id": "T001", "amount": 150.50, "product": "Widget"},
            {"transaction_id": "T002", "amount": 299.99, "product": "Gadget"},
            {"transaction_id": "T003", "amount": 75.00, "product": "Thing"},
            {"transaction_id": "T004", "amount": None, "product": "Item"},  # Will fail not_null
        ]
        
        for check in [not_null_check, unique_check, range_check]:
            platform.quality_manager.run_check(check, sample_data)
            status = "✓" if check.passed else "✗"
            print(f"  {status} {check.name}: {check.message}")
            
        # Trigger pipeline run
        print("\n🚀 Triggering Pipeline Run...")
        
        run = platform.pipeline_manager.trigger_run(
            pipeline.pipeline_id,
            conf={"ds": "2024-01-15"},
            trigger_type=TriggerType.MANUAL,
            triggered_by="data-engineer"
        )
        
        print(f"\n  Run ID: {run.run_id}")
        print(f"  Triggered by: {run.triggered_by}")
        print(f"  Trigger type: {run.trigger_type.value}")
        
        # Execute pipeline
        print("\n⚙️ Executing Pipeline...")
        
        success = await platform.run_pipeline(run)
        
        print(f"\n  Pipeline {'succeeded' if success else 'failed'}!")
        
        # Show task results
        print("\n📋 Task Results:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │ Task                    │ Status    │ Duration │ Attempts │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        
        for task_id, instance in run.task_instances.items():
            task = pipeline.tasks[task_id]
            name = task.name[:23].ljust(23)
            status = instance.status.value[:9].ljust(9)
            
            duration = ""
            if instance.started_at and instance.completed_at:
                dur = (instance.completed_at - instance.started_at).total_seconds()
                duration = f"{dur:.2f}s".ljust(8)
            else:
                duration = "-".ljust(8)
                
            print(f"  │ {name} │ {status} │ {duration} │ {instance.attempts:8} │")
            
        print("  └─────────────────────────────────────────────────────────────┘")
        
        # Backfill
        print("\n⏪ Creating Backfill...")
        
        start_date = datetime.now() - timedelta(days=3)
        end_date = datetime.now() - timedelta(days=1)
        
        backfill_runs = platform.backfill_manager.create_backfill(
            pipeline.pipeline_id,
            start_date,
            end_date,
            timedelta(days=1)
        )
        
        print(f"\n  Created {len(backfill_runs)} backfill runs:")
        for bf_run in backfill_runs:
            exec_date = bf_run.conf.get("execution_date", "")[:10]
            print(f"    - {bf_run.run_id}: {exec_date}")
            
        # Execute backfill runs
        print("\n  Executing backfill...")
        
        for bf_run in backfill_runs:
            await platform.run_pipeline(bf_run)
            
        # Run status
        print("\n📊 Run Statistics:")
        
        for bf_run in backfill_runs:
            status = platform.pipeline_manager.get_run_status(bf_run.run_id)
            exec_date = bf_run.conf.get("execution_date", "")[:10]
            print(f"  {exec_date}: {status['status']} ({status['status_counts']})")
            
        # Pipeline statistics
        print("\n📊 Pipeline Statistics:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │ Pipeline              │ Runs │ Success │ Failed │ Rate    │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        
        for p in platform.pipeline_manager.pipelines.values():
            name = p.name[:21].ljust(21)
            rate = (p.successful_runs / p.total_runs * 100) if p.total_runs > 0 else 0
            print(f"  │ {name} │ {p.total_runs:4} │ {p.successful_runs:7} │ {p.failed_runs:6} │ {rate:6.1f}% │")
            
        print("  └─────────────────────────────────────────────────────────────┘")
        
        # Platform statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Pipelines: {stats['total_pipelines']}")
        print(f"  Active Pipelines: {stats['active_pipelines']}")
        print(f"  Total Runs: {stats['total_runs']}")
        print(f"  Successful: {stats['successful_runs']}")
        print(f"  Failed: {stats['failed_runs']}")
        print(f"  Quality Checks: {stats['quality_checks']}")
        
        # Dashboard
        print("\n📋 Data Pipeline Dashboard:")
        print("  ┌────────────────────────────────────────────────────────────┐")
        print("  │                  Pipeline Platform Overview                │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Pipelines:         {stats['total_pipelines']:>10}                   │")
        print(f"  │ Active Pipelines:        {stats['active_pipelines']:>10}                   │")
        print(f"  │ Total Runs:              {stats['total_runs']:>10}                   │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Successful Runs:         {stats['successful_runs']:>10}                   │")
        print(f"  │ Failed Runs:             {stats['failed_runs']:>10}                   │")
        print(f"  │ Quality Checks:          {stats['quality_checks']:>10}                   │")
        print("  └────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Data Pipeline Platform initialized!")
    print("=" * 60)
