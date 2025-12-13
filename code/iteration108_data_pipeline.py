#!/usr/bin/env python3
"""
Server Init - Iteration 108: Data Pipeline Platform
Платформа управления данными

Функционал:
- Pipeline Definition - определение пайплайнов
- ETL/ELT Operations - операции ETL/ELT
- Data Orchestration - оркестрация данных
- Data Quality - качество данных
- Lineage Tracking - отслеживание происхождения
- Scheduling - планирование
- Monitoring - мониторинг
- Connectors - коннекторы к источникам
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
from collections import defaultdict
import uuid
import random


class PipelineStatus(Enum):
    """Статус пайплайна"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    FAILED = "failed"
    ARCHIVED = "archived"


class TaskStatus(Enum):
    """Статус задачи"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"
    UPSTREAM_FAILED = "upstream_failed"


class ConnectorType(Enum):
    """Тип коннектора"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    S3 = "s3"
    GCS = "gcs"
    KAFKA = "kafka"
    REST_API = "rest_api"
    SFTP = "sftp"
    SNOWFLAKE = "snowflake"
    BIGQUERY = "bigquery"
    REDSHIFT = "redshift"


class TaskType(Enum):
    """Тип задачи"""
    EXTRACT = "extract"
    TRANSFORM = "transform"
    LOAD = "load"
    VALIDATE = "validate"
    AGGREGATE = "aggregate"
    JOIN = "join"
    FILTER = "filter"
    CUSTOM = "custom"


class QualityCheckType(Enum):
    """Тип проверки качества"""
    NOT_NULL = "not_null"
    UNIQUE = "unique"
    RANGE = "range"
    REGEX = "regex"
    REFERENTIAL = "referential"
    FRESHNESS = "freshness"
    VOLUME = "volume"
    CUSTOM = "custom"


@dataclass
class Connector:
    """Коннектор"""
    connector_id: str
    
    # Basic info
    name: str = ""
    connector_type: ConnectorType = ConnectorType.POSTGRESQL
    
    # Connection
    host: str = ""
    port: int = 5432
    database: str = ""
    
    # Credentials
    username: str = ""
    password_ref: str = ""  # Secret reference
    
    # Additional config
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    connected: bool = False
    last_tested: Optional[datetime] = None


@dataclass
class Task:
    """Задача пайплайна"""
    task_id: str
    name: str = ""
    
    # Type
    task_type: TaskType = TaskType.EXTRACT
    
    # Source/Target
    source_connector: Optional[str] = None
    target_connector: Optional[str] = None
    
    # Query/Transform
    query: str = ""
    transform_code: str = ""
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)
    
    # Config
    retries: int = 3
    retry_delay_seconds: int = 60
    timeout_seconds: int = 3600
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class QualityCheck:
    """Проверка качества"""
    check_id: str
    name: str = ""
    
    # Type
    check_type: QualityCheckType = QualityCheckType.NOT_NULL
    
    # Target
    table: str = ""
    column: str = ""
    
    # Parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Severity
    warn_threshold: float = 0.0
    error_threshold: float = 0.0
    
    # Status
    enabled: bool = True


@dataclass
class Pipeline:
    """Пайплайн данных"""
    pipeline_id: str
    
    # Basic info
    name: str = ""
    description: str = ""
    
    # Status
    status: PipelineStatus = PipelineStatus.DRAFT
    
    # Tasks
    tasks: List[Task] = field(default_factory=list)
    
    # Quality checks
    quality_checks: List[QualityCheck] = field(default_factory=list)
    
    # Schedule
    schedule: str = ""  # Cron expression
    
    # Owner
    owner: str = ""
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class TaskRun:
    """Выполнение задачи"""
    run_id: str
    task_id: str
    task_name: str = ""
    
    # Status
    status: TaskStatus = TaskStatus.PENDING
    
    # Timestamps
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    
    # Metrics
    rows_read: int = 0
    rows_written: int = 0
    bytes_processed: int = 0
    
    # Output
    output: str = ""
    error: str = ""
    
    # Attempt
    attempt: int = 1


@dataclass
class PipelineRun:
    """Выполнение пайплайна"""
    run_id: str
    pipeline_id: str
    pipeline_name: str = ""
    
    # Status
    status: TaskStatus = TaskStatus.PENDING
    
    # Task runs
    task_runs: Dict[str, TaskRun] = field(default_factory=dict)
    
    # Timestamps
    started_at: datetime = field(default_factory=datetime.now)
    finished_at: Optional[datetime] = None
    
    # Trigger
    trigger: str = "manual"  # manual, scheduled, event
    triggered_by: str = ""
    
    # Quality results
    quality_results: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class LineageNode:
    """Узел происхождения"""
    node_id: str
    node_type: str = ""  # table, column, pipeline, task
    name: str = ""
    
    # Upstream/Downstream
    upstream: List[str] = field(default_factory=list)
    downstream: List[str] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConnectorManager:
    """Менеджер коннекторов"""
    
    def __init__(self):
        self.connectors: Dict[str, Connector] = {}
        
    def register(self, name: str, connector_type: ConnectorType,
                  **kwargs) -> Connector:
        """Регистрация коннектора"""
        connector = Connector(
            connector_id=f"conn_{uuid.uuid4().hex[:8]}",
            name=name,
            connector_type=connector_type,
            **kwargs
        )
        self.connectors[connector.connector_id] = connector
        return connector
        
    def test_connection(self, connector_id: str) -> bool:
        """Тест соединения"""
        connector = self.connectors.get(connector_id)
        if not connector:
            return False
            
        # Simulate connection test
        connector.connected = random.random() > 0.1
        connector.last_tested = datetime.now()
        return connector.connected


class QualityEngine:
    """Движок качества данных"""
    
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        
    def run_checks(self, checks: List[QualityCheck],
                    data_sample: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Запуск проверок"""
        results = []
        
        for check in checks:
            if not check.enabled:
                continue
                
            # Simulate quality check
            passed = random.random() > 0.2
            value = random.uniform(0, 100) if not passed else 0
            
            result = {
                "check_id": check.check_id,
                "check_name": check.name,
                "check_type": check.check_type.value,
                "table": check.table,
                "column": check.column,
                "passed": passed,
                "value": value,
                "timestamp": datetime.now().isoformat()
            }
            
            if not passed:
                if value > check.error_threshold:
                    result["severity"] = "error"
                elif value > check.warn_threshold:
                    result["severity"] = "warning"
                else:
                    result["severity"] = "info"
                    
            results.append(result)
            self.results.append(result)
            
        return results


class TaskExecutor:
    """Исполнитель задач"""
    
    def __init__(self, connector_manager: ConnectorManager):
        self.connector_manager = connector_manager
        
    async def execute(self, task: Task) -> TaskRun:
        """Выполнение задачи"""
        run = TaskRun(
            run_id=f"taskrun_{uuid.uuid4().hex[:8]}",
            task_id=task.task_id,
            task_name=task.name,
            status=TaskStatus.RUNNING,
            started_at=datetime.now()
        )
        
        try:
            # Simulate task execution
            await asyncio.sleep(0.1)
            
            if random.random() > 0.1:  # 90% success
                run.status = TaskStatus.SUCCEEDED
                run.rows_read = random.randint(1000, 100000)
                run.rows_written = random.randint(1000, run.rows_read)
                run.bytes_processed = run.rows_read * random.randint(100, 500)
                run.output = f"Processed {run.rows_read} rows"
            else:
                run.status = TaskStatus.FAILED
                run.error = "Task execution failed"
                
        except Exception as e:
            run.status = TaskStatus.FAILED
            run.error = str(e)
            
        run.finished_at = datetime.now()
        return run


class PipelineOrchestrator:
    """Оркестратор пайплайнов"""
    
    def __init__(self, task_executor: TaskExecutor, quality_engine: QualityEngine):
        self.task_executor = task_executor
        self.quality_engine = quality_engine
        
    async def run(self, pipeline: Pipeline, triggered_by: str = "",
                   trigger: str = "manual") -> PipelineRun:
        """Запуск пайплайна"""
        run = PipelineRun(
            run_id=f"piperun_{uuid.uuid4().hex[:8]}",
            pipeline_id=pipeline.pipeline_id,
            pipeline_name=pipeline.name,
            status=TaskStatus.RUNNING,
            trigger=trigger,
            triggered_by=triggered_by
        )
        
        # Build task order (topological sort)
        task_order = self._resolve_dependencies(pipeline.tasks)
        
        # Execute tasks
        for task in task_order:
            # Check upstream failures
            upstream_failed = False
            for dep in task.depends_on:
                if dep in run.task_runs:
                    if run.task_runs[dep].status == TaskStatus.FAILED:
                        upstream_failed = True
                        break
                        
            if upstream_failed:
                task_run = TaskRun(
                    run_id=f"taskrun_{uuid.uuid4().hex[:8]}",
                    task_id=task.task_id,
                    task_name=task.name,
                    status=TaskStatus.UPSTREAM_FAILED
                )
            else:
                task_run = await self.task_executor.execute(task)
                
            run.task_runs[task.task_id] = task_run
            
            # Stop on failure
            if task_run.status == TaskStatus.FAILED:
                break
                
        # Run quality checks
        if pipeline.quality_checks:
            run.quality_results = self.quality_engine.run_checks(pipeline.quality_checks)
            
        # Determine final status
        failed_tasks = [t for t in run.task_runs.values() if t.status == TaskStatus.FAILED]
        if failed_tasks:
            run.status = TaskStatus.FAILED
        else:
            run.status = TaskStatus.SUCCEEDED
            
        run.finished_at = datetime.now()
        return run
        
    def _resolve_dependencies(self, tasks: List[Task]) -> List[Task]:
        """Разрешение зависимостей"""
        # Simple topological sort
        result = []
        visited = set()
        
        def visit(task):
            if task.task_id in visited:
                return
            visited.add(task.task_id)
            
            for dep_id in task.depends_on:
                dep_task = next((t for t in tasks if t.task_id == dep_id), None)
                if dep_task:
                    visit(dep_task)
                    
            result.append(task)
            
        for task in tasks:
            visit(task)
            
        return result


class LineageTracker:
    """Трекер происхождения"""
    
    def __init__(self):
        self.nodes: Dict[str, LineageNode] = {}
        
    def add_node(self, node_type: str, name: str,
                  metadata: Dict[str, Any] = None) -> LineageNode:
        """Добавление узла"""
        node = LineageNode(
            node_id=f"node_{uuid.uuid4().hex[:8]}",
            node_type=node_type,
            name=name,
            metadata=metadata or {}
        )
        self.nodes[node.node_id] = node
        return node
        
    def add_edge(self, from_node: str, to_node: str) -> bool:
        """Добавление связи"""
        if from_node in self.nodes and to_node in self.nodes:
            self.nodes[from_node].downstream.append(to_node)
            self.nodes[to_node].upstream.append(from_node)
            return True
        return False
        
    def get_upstream(self, node_id: str) -> List[LineageNode]:
        """Получение upstream узлов"""
        node = self.nodes.get(node_id)
        if not node:
            return []
            
        result = []
        for upstream_id in node.upstream:
            if upstream_id in self.nodes:
                result.append(self.nodes[upstream_id])
                result.extend(self.get_upstream(upstream_id))
                
        return result


class PipelineManager:
    """Менеджер пайплайнов"""
    
    def __init__(self, orchestrator: PipelineOrchestrator):
        self.pipelines: Dict[str, Pipeline] = {}
        self.orchestrator = orchestrator
        self.runs: List[PipelineRun] = []
        
    def create(self, name: str, description: str = "",
                owner: str = "", **kwargs) -> Pipeline:
        """Создание пайплайна"""
        pipeline = Pipeline(
            pipeline_id=f"pipe_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            owner=owner,
            **kwargs
        )
        self.pipelines[pipeline.pipeline_id] = pipeline
        return pipeline
        
    def add_task(self, pipeline_id: str, name: str,
                  task_type: TaskType, **kwargs) -> Optional[Task]:
        """Добавление задачи"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            return None
            
        task = Task(
            task_id=f"task_{uuid.uuid4().hex[:8]}",
            name=name,
            task_type=task_type,
            **kwargs
        )
        pipeline.tasks.append(task)
        return task
        
    def add_quality_check(self, pipeline_id: str, name: str,
                           check_type: QualityCheckType,
                           table: str, column: str = "",
                           **kwargs) -> Optional[QualityCheck]:
        """Добавление проверки качества"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            return None
            
        check = QualityCheck(
            check_id=f"check_{uuid.uuid4().hex[:8]}",
            name=name,
            check_type=check_type,
            table=table,
            column=column,
            **kwargs
        )
        pipeline.quality_checks.append(check)
        return check
        
    async def run(self, pipeline_id: str, **kwargs) -> Optional[PipelineRun]:
        """Запуск пайплайна"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            return None
            
        run = await self.orchestrator.run(pipeline, **kwargs)
        self.runs.append(run)
        return run


class DataPipelinePlatform:
    """Платформа управления данными"""
    
    def __init__(self):
        self.connector_manager = ConnectorManager()
        self.quality_engine = QualityEngine()
        self.task_executor = TaskExecutor(self.connector_manager)
        self.orchestrator = PipelineOrchestrator(self.task_executor, self.quality_engine)
        self.pipeline_manager = PipelineManager(self.orchestrator)
        self.lineage_tracker = LineageTracker()
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        runs = self.pipeline_manager.runs
        
        total_rows = sum(
            sum(t.rows_read for t in r.task_runs.values())
            for r in runs
        )
        
        total_bytes = sum(
            sum(t.bytes_processed for t in r.task_runs.values())
            for r in runs
        )
        
        success_runs = len([r for r in runs if r.status == TaskStatus.SUCCEEDED])
        failed_runs = len([r for r in runs if r.status == TaskStatus.FAILED])
        
        quality_passed = len([
            q for r in runs for q in r.quality_results if q.get("passed", False)
        ])
        quality_failed = len([
            q for r in runs for q in r.quality_results if not q.get("passed", True)
        ])
        
        return {
            "connectors": len(self.connector_manager.connectors),
            "pipelines": len(self.pipeline_manager.pipelines),
            "total_runs": len(runs),
            "successful_runs": success_runs,
            "failed_runs": failed_runs,
            "success_rate": (success_runs / len(runs) * 100) if runs else 0,
            "total_rows_processed": total_rows,
            "total_bytes_processed": total_bytes,
            "quality_checks_passed": quality_passed,
            "quality_checks_failed": quality_failed,
            "lineage_nodes": len(self.lineage_tracker.nodes)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 108: Data Pipeline Platform")
    print("=" * 60)
    
    async def demo():
        platform = DataPipelinePlatform()
        print("✓ Data Pipeline Platform created")
        
        # Register connectors
        print("\n🔌 Registering Connectors...")
        
        connectors_data = [
            ("PostgreSQL Production", ConnectorType.POSTGRESQL, "pg-prod.company.com", 5432, "production"),
            ("PostgreSQL Analytics", ConnectorType.POSTGRESQL, "pg-analytics.company.com", 5432, "analytics"),
            ("MongoDB Events", ConnectorType.MONGODB, "mongo.company.com", 27017, "events"),
            ("S3 Data Lake", ConnectorType.S3, "s3.amazonaws.com", 443, "data-lake"),
            ("Kafka Streams", ConnectorType.KAFKA, "kafka.company.com", 9092, ""),
            ("Snowflake DWH", ConnectorType.SNOWFLAKE, "account.snowflakecomputing.com", 443, "warehouse")
        ]
        
        for name, conn_type, host, port, db in connectors_data:
            conn = platform.connector_manager.register(
                name, conn_type, host=host, port=port, database=db
            )
            connected = platform.connector_manager.test_connection(conn.connector_id)
            status = "✓" if connected else "✗"
            print(f"  {status} {name} ({conn_type.value})")
            
        # Create pipelines
        print("\n📊 Creating Pipelines...")
        
        # Pipeline 1: ETL Users
        pipe1 = platform.pipeline_manager.create(
            "ETL Users Pipeline",
            "Extract users from production, transform and load to analytics",
            "data-team@company.com",
            schedule="0 2 * * *",
            status=PipelineStatus.ACTIVE
        )
        
        platform.pipeline_manager.add_task(
            pipe1.pipeline_id, "Extract Users",
            TaskType.EXTRACT,
            query="SELECT * FROM users WHERE updated_at > :last_run"
        )
        
        task2 = platform.pipeline_manager.add_task(
            pipe1.pipeline_id, "Transform Users",
            TaskType.TRANSFORM,
            transform_code="clean_pii(data)"
        )
        task2.depends_on = [pipe1.tasks[0].task_id]
        
        task3 = platform.pipeline_manager.add_task(
            pipe1.pipeline_id, "Load to Analytics",
            TaskType.LOAD
        )
        task3.depends_on = [task2.task_id]
        
        platform.pipeline_manager.add_quality_check(
            pipe1.pipeline_id, "Users Not Null Email",
            QualityCheckType.NOT_NULL, "users", "email"
        )
        
        platform.pipeline_manager.add_quality_check(
            pipe1.pipeline_id, "Users Unique ID",
            QualityCheckType.UNIQUE, "users", "user_id"
        )
        
        print(f"  ✓ {pipe1.name} ({len(pipe1.tasks)} tasks, {len(pipe1.quality_checks)} checks)")
        
        # Pipeline 2: Events Processing
        pipe2 = platform.pipeline_manager.create(
            "Events Processing",
            "Process event stream from MongoDB to Snowflake",
            "analytics@company.com",
            schedule="*/15 * * * *"
        )
        
        platform.pipeline_manager.add_task(
            pipe2.pipeline_id, "Extract Events",
            TaskType.EXTRACT
        )
        
        t2 = platform.pipeline_manager.add_task(
            pipe2.pipeline_id, "Filter Valid Events",
            TaskType.FILTER
        )
        t2.depends_on = [pipe2.tasks[0].task_id]
        
        t3 = platform.pipeline_manager.add_task(
            pipe2.pipeline_id, "Aggregate by Hour",
            TaskType.AGGREGATE
        )
        t3.depends_on = [t2.task_id]
        
        t4 = platform.pipeline_manager.add_task(
            pipe2.pipeline_id, "Load to Snowflake",
            TaskType.LOAD
        )
        t4.depends_on = [t3.task_id]
        
        platform.pipeline_manager.add_quality_check(
            pipe2.pipeline_id, "Events Volume",
            QualityCheckType.VOLUME, "events",
            parameters={"min_rows": 1000}
        )
        
        print(f"  ✓ {pipe2.name} ({len(pipe2.tasks)} tasks)")
        
        # Pipeline 3: Data Mart
        pipe3 = platform.pipeline_manager.create(
            "Sales Data Mart",
            "Build sales data mart",
            "bi@company.com"
        )
        
        platform.pipeline_manager.add_task(
            pipe3.pipeline_id, "Extract Orders",
            TaskType.EXTRACT
        )
        
        platform.pipeline_manager.add_task(
            pipe3.pipeline_id, "Extract Products",
            TaskType.EXTRACT
        )
        
        j1 = platform.pipeline_manager.add_task(
            pipe3.pipeline_id, "Join Orders Products",
            TaskType.JOIN
        )
        j1.depends_on = [pipe3.tasks[0].task_id, pipe3.tasks[1].task_id]
        
        agg = platform.pipeline_manager.add_task(
            pipe3.pipeline_id, "Calculate Metrics",
            TaskType.AGGREGATE
        )
        agg.depends_on = [j1.task_id]
        
        platform.pipeline_manager.add_quality_check(
            pipe3.pipeline_id, "Sales Total Range",
            QualityCheckType.RANGE, "sales_mart", "total_amount",
            parameters={"min": 0, "max": 1000000}
        )
        
        print(f"  ✓ {pipe3.name} ({len(pipe3.tasks)} tasks)")
        
        # Build lineage
        print("\n🔗 Building Data Lineage...")
        
        # Add lineage nodes
        src_users = platform.lineage_tracker.add_node("table", "production.users")
        dst_users = platform.lineage_tracker.add_node("table", "analytics.users_cleaned")
        task_node = platform.lineage_tracker.add_node("task", "Transform Users")
        
        platform.lineage_tracker.add_edge(src_users.node_id, task_node.node_id)
        platform.lineage_tracker.add_edge(task_node.node_id, dst_users.node_id)
        
        print(f"  ✓ Tracked {len(platform.lineage_tracker.nodes)} nodes")
        
        # Run pipelines
        print("\n⚡ Running Pipelines...")
        
        for pipeline in [pipe1, pipe2, pipe3]:
            print(f"\n  Running: {pipeline.name}")
            run = await platform.pipeline_manager.run(
                pipeline.pipeline_id,
                triggered_by="admin@company.com"
            )
            
            status_icon = "✅" if run.status == TaskStatus.SUCCEEDED else "❌"
            print(f"    {status_icon} Status: {run.status.value}")
            
            # Show task results
            for task_id, task_run in run.task_runs.items():
                task_icon = {
                    "succeeded": "✅",
                    "failed": "❌",
                    "skipped": "⏭️",
                    "upstream_failed": "⬆️❌"
                }.get(task_run.status.value, "⚪")
                
                metrics = ""
                if task_run.rows_read > 0:
                    metrics = f" ({task_run.rows_read:,} rows, {task_run.bytes_processed/1024:.1f} KB)"
                    
                print(f"      {task_icon} {task_run.task_name}{metrics}")
                
            # Show quality results
            if run.quality_results:
                print("    Quality Checks:")
                for qr in run.quality_results:
                    q_icon = "✅" if qr["passed"] else "❌"
                    print(f"      {q_icon} {qr['check_name']}: {qr['check_type']}")
                    
        # Run history
        print("\n📜 Run History:")
        
        for run in platform.pipeline_manager.runs:
            status_icon = "✅" if run.status == TaskStatus.SUCCEEDED else "❌"
            duration = ""
            if run.finished_at:
                dur = (run.finished_at - run.started_at).total_seconds()
                duration = f" ({dur:.1f}s)"
                
            print(f"  {status_icon} {run.pipeline_name} [{run.trigger}]{duration}")
            
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Infrastructure:")
        print(f"    Connectors: {stats['connectors']}")
        print(f"    Pipelines: {stats['pipelines']}")
        print(f"    Lineage Nodes: {stats['lineage_nodes']}")
        
        print(f"\n  Runs:")
        print(f"    Total: {stats['total_runs']}")
        print(f"    Successful: {stats['successful_runs']}")
        print(f"    Failed: {stats['failed_runs']}")
        print(f"    Success Rate: {stats['success_rate']:.1f}%")
        
        print(f"\n  Data Processed:")
        print(f"    Rows: {stats['total_rows_processed']:,}")
        print(f"    Bytes: {stats['total_bytes_processed']/1024/1024:.2f} MB")
        
        print(f"\n  Quality:")
        print(f"    Checks Passed: {stats['quality_checks_passed']}")
        print(f"    Checks Failed: {stats['quality_checks_failed']}")
        
        # Dashboard
        print("\n📋 Data Pipeline Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │              Data Pipeline Overview                         │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Connectors:         {stats['connectors']:>10}                        │")
        print(f"  │ Pipelines:          {stats['pipelines']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Runs:         {stats['total_runs']:>10}                        │")
        print(f"  │ Success Rate:       {stats['success_rate']:>10.1f}%                       │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        mb = stats['total_bytes_processed']/1024/1024
        print(f"  │ Rows Processed:     {stats['total_rows_processed']:>10,}                        │")
        print(f"  │ Data Processed:     {mb:>10.1f} MB                       │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Data Pipeline Platform initialized!")
    print("=" * 60)
