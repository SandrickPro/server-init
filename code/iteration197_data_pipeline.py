#!/usr/bin/env python3
"""
Server Init - Iteration 197: Data Pipeline Platform
Платформа конвейеров данных

Функционал:
- Pipeline Definition - определение пайплайнов
- Task Orchestration - оркестрация задач
- Data Transformation - трансформация данных
- Scheduling - планирование
- Dependency Management - управление зависимостями
- Monitoring - мониторинг
- Error Handling - обработка ошибок
- Backfill Support - поддержка бэкфиллов
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
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


class TriggerType(Enum):
    """Тип триггера"""
    SCHEDULE = "schedule"
    MANUAL = "manual"
    EXTERNAL = "external"
    DEPENDENCY = "dependency"


class DataFormat(Enum):
    """Формат данных"""
    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"
    AVRO = "avro"
    ORC = "orc"


@dataclass
class TaskDefinition:
    """Определение задачи"""
    task_id: str
    name: str = ""
    
    # Dependencies
    upstream_tasks: List[str] = field(default_factory=list)
    
    # Handler
    handler: str = ""
    
    # Config
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Retry
    retries: int = 3
    retry_delay_seconds: int = 60
    
    # Timeout
    timeout_seconds: int = 3600
    
    # Pool
    pool: str = "default"


@dataclass
class TaskInstance:
    """Экземпляр задачи"""
    instance_id: str
    task_id: str
    pipeline_run_id: str
    
    # State
    state: TaskState = TaskState.PENDING
    
    # Execution
    execution_date: datetime = field(default_factory=datetime.now)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    # Retries
    try_number: int = 0
    max_tries: int = 3
    
    # Output
    xcom: Dict[str, Any] = field(default_factory=dict)
    
    # Error
    error: str = ""
    
    @property
    def duration_seconds(self) -> float:
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).total_seconds()
        return 0


@dataclass
class Pipeline:
    """Пайплайн"""
    pipeline_id: str
    name: str = ""
    description: str = ""
    
    # Tasks
    tasks: Dict[str, TaskDefinition] = field(default_factory=dict)
    
    # Schedule
    schedule: str = ""  # cron expression
    
    # Config
    default_args: Dict[str, Any] = field(default_factory=dict)
    
    # Time
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    
    # Metadata
    owner: str = ""
    tags: List[str] = field(default_factory=list)
    
    # State
    is_paused: bool = False
    
    # Created
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PipelineRun:
    """Запуск пайплайна"""
    run_id: str
    pipeline_id: str
    
    # State
    state: str = "running"  # running, success, failed
    
    # Execution
    execution_date: datetime = field(default_factory=datetime.now)
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    
    # Trigger
    trigger_type: TriggerType = TriggerType.MANUAL
    
    # Tasks
    task_instances: Dict[str, TaskInstance] = field(default_factory=dict)
    
    # Config
    config: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_seconds(self) -> float:
        if self.end_date:
            return (self.end_date - self.start_date).total_seconds()
        return 0
        
    @property
    def progress(self) -> float:
        if not self.task_instances:
            return 0
        completed = len([t for t in self.task_instances.values() 
                        if t.state in [TaskState.SUCCESS, TaskState.SKIPPED]])
        return completed / len(self.task_instances) * 100


@dataclass
class DataSource:
    """Источник данных"""
    source_id: str
    name: str = ""
    source_type: str = ""  # database, file, api, stream
    
    # Connection
    connection_string: str = ""
    
    # Schema
    schema: Dict[str, Any] = field(default_factory=dict)
    
    # Format
    data_format: DataFormat = DataFormat.JSON


class TaskExecutor:
    """Исполнитель задач"""
    
    def __init__(self):
        self.handlers: Dict[str, Callable] = {}
        
    def register_handler(self, name: str, handler: Callable):
        """Регистрация обработчика"""
        self.handlers[name] = handler
        
    async def execute(self, task_instance: TaskInstance,
                     task_def: TaskDefinition) -> bool:
        """Выполнение задачи"""
        task_instance.state = TaskState.RUNNING
        task_instance.start_date = datetime.now()
        task_instance.try_number += 1
        
        try:
            handler = self.handlers.get(task_def.handler)
            
            if handler:
                result = await asyncio.wait_for(
                    handler(task_instance, task_def.config),
                    timeout=task_def.timeout_seconds
                )
                task_instance.xcom = result or {}
            else:
                # Simulate execution
                await asyncio.sleep(random.uniform(0.05, 0.2))
                task_instance.xcom = {"status": "completed"}
                
            task_instance.state = TaskState.SUCCESS
            task_instance.end_date = datetime.now()
            return True
            
        except asyncio.TimeoutError:
            task_instance.state = TaskState.FAILED
            task_instance.error = "Task timeout"
            task_instance.end_date = datetime.now()
            return False
            
        except Exception as e:
            task_instance.state = TaskState.FAILED
            task_instance.error = str(e)
            task_instance.end_date = datetime.now()
            return False


class PipelineScheduler:
    """Планировщик пайплайнов"""
    
    def __init__(self):
        self.scheduled_runs: List[Dict[str, Any]] = []
        
    def schedule(self, pipeline: Pipeline, execution_date: datetime):
        """Планирование запуска"""
        self.scheduled_runs.append({
            "pipeline_id": pipeline.pipeline_id,
            "execution_date": execution_date,
            "status": "scheduled"
        })
        
    def get_pending_runs(self) -> List[Dict[str, Any]]:
        """Получение ожидающих запусков"""
        now = datetime.now()
        return [r for r in self.scheduled_runs 
                if r["execution_date"] <= now and r["status"] == "scheduled"]


class PipelineEngine:
    """Движок пайплайнов"""
    
    def __init__(self):
        self.pipelines: Dict[str, Pipeline] = {}
        self.runs: Dict[str, PipelineRun] = {}
        self.executor = TaskExecutor()
        self.scheduler = PipelineScheduler()
        
    def register_pipeline(self, pipeline: Pipeline):
        """Регистрация пайплайна"""
        self.pipelines[pipeline.pipeline_id] = pipeline
        
    async def run_pipeline(self, pipeline_id: str,
                          trigger_type: TriggerType = TriggerType.MANUAL,
                          config: Dict[str, Any] = None) -> PipelineRun:
        """Запуск пайплайна"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline {pipeline_id} not found")
            
        run = PipelineRun(
            run_id=f"run_{uuid.uuid4().hex[:8]}",
            pipeline_id=pipeline_id,
            trigger_type=trigger_type,
            config=config or {}
        )
        
        # Create task instances
        for task_id, task_def in pipeline.tasks.items():
            task_instance = TaskInstance(
                instance_id=f"ti_{uuid.uuid4().hex[:8]}",
                task_id=task_id,
                pipeline_run_id=run.run_id,
                execution_date=run.execution_date,
                max_tries=task_def.retries
            )
            run.task_instances[task_id] = task_instance
            
        self.runs[run.run_id] = run
        
        # Execute pipeline
        await self._execute_pipeline(run, pipeline)
        
        return run
        
    async def _execute_pipeline(self, run: PipelineRun, pipeline: Pipeline):
        """Выполнение пайплайна"""
        # Build execution order (topological sort)
        execution_order = self._get_execution_order(pipeline)
        
        for task_id in execution_order:
            task_def = pipeline.tasks[task_id]
            task_instance = run.task_instances[task_id]
            
            # Check upstream
            upstream_failed = False
            for upstream_id in task_def.upstream_tasks:
                upstream = run.task_instances.get(upstream_id)
                if upstream and upstream.state == TaskState.FAILED:
                    upstream_failed = True
                    break
                    
            if upstream_failed:
                task_instance.state = TaskState.UPSTREAM_FAILED
                continue
                
            # Execute
            success = await self.executor.execute(task_instance, task_def)
            
            # Retry if needed
            while not success and task_instance.try_number < task_instance.max_tries:
                task_instance.state = TaskState.RETRYING
                await asyncio.sleep(0.1)  # Retry delay
                success = await self.executor.execute(task_instance, task_def)
                
        # Update run state
        failed_tasks = [t for t in run.task_instances.values() 
                       if t.state in [TaskState.FAILED, TaskState.UPSTREAM_FAILED]]
        
        run.state = "failed" if failed_tasks else "success"
        run.end_date = datetime.now()
        
    def _get_execution_order(self, pipeline: Pipeline) -> List[str]:
        """Топологическая сортировка"""
        visited = set()
        order = []
        
        def visit(task_id: str):
            if task_id in visited:
                return
            visited.add(task_id)
            
            task_def = pipeline.tasks.get(task_id)
            if task_def:
                for upstream in task_def.upstream_tasks:
                    visit(upstream)
            order.append(task_id)
            
        for task_id in pipeline.tasks:
            visit(task_id)
            
        return order


class DataPipelinePlatform:
    """Платформа конвейеров данных"""
    
    def __init__(self):
        self.engine = PipelineEngine()
        self.data_sources: Dict[str, DataSource] = {}
        
    def add_data_source(self, name: str, source_type: str,
                       connection: str) -> DataSource:
        """Добавление источника данных"""
        source = DataSource(
            source_id=f"src_{uuid.uuid4().hex[:8]}",
            name=name,
            source_type=source_type,
            connection_string=connection
        )
        self.data_sources[source.source_id] = source
        return source
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        runs = list(self.engine.runs.values())
        
        success_runs = len([r for r in runs if r.state == "success"])
        failed_runs = len([r for r in runs if r.state == "failed"])
        
        return {
            "total_pipelines": len(self.engine.pipelines),
            "total_runs": len(runs),
            "success_runs": success_runs,
            "failed_runs": failed_runs,
            "success_rate": (success_runs / len(runs) * 100) if runs else 0,
            "data_sources": len(self.data_sources)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 197: Data Pipeline Platform")
    print("=" * 60)
    
    platform = DataPipelinePlatform()
    print("✓ Data Pipeline Platform created")
    
    # Add data sources
    print("\n📊 Adding Data Sources...")
    
    sources = [
        ("postgres_main", "database", "postgresql://localhost:5432/main"),
        ("s3_raw", "file", "s3://data-lake/raw/"),
        ("kafka_events", "stream", "kafka://localhost:9092/events"),
        ("api_external", "api", "https://api.example.com/data"),
    ]
    
    for name, stype, conn in sources:
        source = platform.add_data_source(name, stype, conn)
        print(f"  ✓ {name} ({stype})")
        
    # Create pipelines
    print("\n📋 Creating Pipelines...")
    
    # ETL Pipeline
    etl_pipeline = Pipeline(
        pipeline_id=f"pipe_{uuid.uuid4().hex[:8]}",
        name="ETL Daily Pipeline",
        description="Daily ETL process",
        schedule="0 0 * * *",
        owner="data-team",
        tags=["etl", "daily"]
    )
    
    etl_tasks = [
        TaskDefinition(task_id="extract_users", name="Extract Users", upstream_tasks=[]),
        TaskDefinition(task_id="extract_orders", name="Extract Orders", upstream_tasks=[]),
        TaskDefinition(task_id="transform_users", name="Transform Users", upstream_tasks=["extract_users"]),
        TaskDefinition(task_id="transform_orders", name="Transform Orders", upstream_tasks=["extract_orders"]),
        TaskDefinition(task_id="join_data", name="Join Data", upstream_tasks=["transform_users", "transform_orders"]),
        TaskDefinition(task_id="load_warehouse", name="Load to Warehouse", upstream_tasks=["join_data"]),
        TaskDefinition(task_id="update_metrics", name="Update Metrics", upstream_tasks=["load_warehouse"]),
    ]
    
    for task in etl_tasks:
        etl_pipeline.tasks[task.task_id] = task
        
    platform.engine.register_pipeline(etl_pipeline)
    print(f"  ✓ {etl_pipeline.name} ({len(etl_pipeline.tasks)} tasks)")
    
    # ML Pipeline
    ml_pipeline = Pipeline(
        pipeline_id=f"pipe_{uuid.uuid4().hex[:8]}",
        name="ML Training Pipeline",
        description="Weekly ML model training",
        schedule="0 2 * * 0",
        owner="ml-team",
        tags=["ml", "training"]
    )
    
    ml_tasks = [
        TaskDefinition(task_id="fetch_data", name="Fetch Training Data", upstream_tasks=[]),
        TaskDefinition(task_id="preprocess", name="Preprocess Data", upstream_tasks=["fetch_data"]),
        TaskDefinition(task_id="feature_eng", name="Feature Engineering", upstream_tasks=["preprocess"]),
        TaskDefinition(task_id="train_model", name="Train Model", upstream_tasks=["feature_eng"]),
        TaskDefinition(task_id="evaluate", name="Evaluate Model", upstream_tasks=["train_model"]),
        TaskDefinition(task_id="deploy", name="Deploy Model", upstream_tasks=["evaluate"]),
    ]
    
    for task in ml_tasks:
        ml_pipeline.tasks[task.task_id] = task
        
    platform.engine.register_pipeline(ml_pipeline)
    print(f"  ✓ {ml_pipeline.name} ({len(ml_pipeline.tasks)} tasks)")
    
    # Data Quality Pipeline
    dq_pipeline = Pipeline(
        pipeline_id=f"pipe_{uuid.uuid4().hex[:8]}",
        name="Data Quality Check",
        schedule="0 */6 * * *",
        owner="data-team",
        tags=["quality", "monitoring"]
    )
    
    dq_tasks = [
        TaskDefinition(task_id="check_freshness", name="Check Freshness", upstream_tasks=[]),
        TaskDefinition(task_id="check_completeness", name="Check Completeness", upstream_tasks=[]),
        TaskDefinition(task_id="check_accuracy", name="Check Accuracy", upstream_tasks=[]),
        TaskDefinition(task_id="generate_report", name="Generate Report", 
                      upstream_tasks=["check_freshness", "check_completeness", "check_accuracy"]),
        TaskDefinition(task_id="send_alerts", name="Send Alerts", upstream_tasks=["generate_report"]),
    ]
    
    for task in dq_tasks:
        dq_pipeline.tasks[task.task_id] = task
        
    platform.engine.register_pipeline(dq_pipeline)
    print(f"  ✓ {dq_pipeline.name} ({len(dq_pipeline.tasks)} tasks)")
    
    # Run pipelines
    print("\n🚀 Running Pipelines...")
    
    for pipeline in platform.engine.pipelines.values():
        run = await platform.engine.run_pipeline(pipeline.pipeline_id)
        status_icon = "✅" if run.state == "success" else "❌"
        print(f"  {status_icon} {pipeline.name}: {run.state} ({run.duration_seconds:.2f}s)")
        
    # Pipeline runs summary
    print("\n📊 Pipeline Runs Summary:")
    
    print("\n  ┌─────────────────────────────┬──────────┬──────────┬──────────┬──────────┐")
    print("  │ Pipeline                    │ Status   │ Tasks    │ Progress │ Duration │")
    print("  ├─────────────────────────────┼──────────┼──────────┼──────────┼──────────┤")
    
    for run in platform.engine.runs.values():
        pipeline = platform.engine.pipelines.get(run.pipeline_id)
        name = pipeline.name[:27].ljust(27) if pipeline else "Unknown".ljust(27)
        status = run.state[:8].ljust(8)
        tasks = str(len(run.task_instances)).center(8)
        progress = f"{run.progress:.0f}%".center(8)
        duration = f"{run.duration_seconds:.2f}s".rjust(8)
        print(f"  │ {name} │ {status} │ {tasks} │ {progress} │ {duration} │")
        
    print("  └─────────────────────────────┴──────────┴──────────┴──────────┴──────────┘")
    
    # Task instances detail
    print("\n📋 Task Instances (ETL Pipeline):")
    
    etl_run = [r for r in platform.engine.runs.values() 
               if platform.engine.pipelines.get(r.pipeline_id, Pipeline("")).name == "ETL Daily Pipeline"][0]
    
    for task_id, task_inst in etl_run.task_instances.items():
        status_icon = "✅" if task_inst.state == TaskState.SUCCESS else ("❌" if task_inst.state == TaskState.FAILED else "⏳")
        task_def = etl_pipeline.tasks.get(task_id)
        name = task_def.name if task_def else task_id
        print(f"  {status_icon} {name}: {task_inst.state.value} ({task_inst.duration_seconds:.3f}s)")
        
    # Run multiple times
    print("\n🔄 Running Additional Pipeline Executions...")
    
    for _ in range(5):
        pipeline = random.choice(list(platform.engine.pipelines.values()))
        run = await platform.engine.run_pipeline(pipeline.pipeline_id)
        
    total_runs = len(platform.engine.runs)
    print(f"  Total runs: {total_runs}")
    
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📈 Platform Statistics:")
    
    print(f"\n  Total Pipelines: {stats['total_pipelines']}")
    print(f"  Total Runs: {stats['total_runs']}")
    print(f"  Success Runs: {stats['success_runs']}")
    print(f"  Failed Runs: {stats['failed_runs']}")
    print(f"  Success Rate: {stats['success_rate']:.1f}%")
    print(f"  Data Sources: {stats['data_sources']}")
    
    # Task state distribution
    print("\n📊 Task State Distribution:")
    
    all_tasks = []
    for run in platform.engine.runs.values():
        all_tasks.extend(run.task_instances.values())
        
    state_counts = {}
    for task in all_tasks:
        s = task.state.value
        state_counts[s] = state_counts.get(s, 0) + 1
        
    for state, count in sorted(state_counts.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * min(count, 30) + "░" * max(0, 30 - count)
        print(f"  {state:15} [{bar}] {count}")
        
    # Pipeline health
    print("\n💚 Pipeline Health:")
    
    for pipeline in platform.engine.pipelines.values():
        pipeline_runs = [r for r in platform.engine.runs.values() if r.pipeline_id == pipeline.pipeline_id]
        success_count = len([r for r in pipeline_runs if r.state == "success"])
        total_count = len(pipeline_runs)
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        
        health_icon = "🟢" if success_rate >= 90 else ("🟡" if success_rate >= 70 else "🔴")
        print(f"  {health_icon} {pipeline.name}: {success_rate:.0f}% ({success_count}/{total_count})")
        
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                     Data Pipeline Dashboard                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Pipelines:               {stats['total_pipelines']:>12}                        │")
    print(f"│ Total Runs:                    {stats['total_runs']:>12}                        │")
    print(f"│ Success Rate:                    {stats['success_rate']:>10.1f}%                   │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Data Sources:                  {stats['data_sources']:>12}                        │")
    print(f"│ Total Tasks:                   {len(all_tasks):>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Data Pipeline Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
