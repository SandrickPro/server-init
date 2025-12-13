#!/usr/bin/env python3
"""
Server Init - Iteration 90: Data Pipeline Orchestration Platform
Платформа оркестрации конвейеров данных

Функционал:
- Pipeline Definition - определение конвейеров
- DAG Orchestration - оркестрация DAG
- Task Scheduling - планирование задач
- Data Lineage - происхождение данных
- Quality Gates - контроль качества
- Pipeline Monitoring - мониторинг конвейеров
- Retry & Recovery - повторы и восстановление
- Multi-Environment - поддержка сред
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Tuple, Awaitable
from enum import Enum
from collections import defaultdict
import uuid
import random


class TaskStatus(Enum):
    """Статус задачи"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    UPSTREAM_FAILED = "upstream_failed"
    RETRYING = "retrying"


class PipelineStatus(Enum):
    """Статус конвейера"""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PAUSED = "paused"


class TriggerType(Enum):
    """Тип триггера"""
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    EVENT = "event"
    DEPENDENCY = "dependency"


class QualityCheckType(Enum):
    """Тип проверки качества"""
    ROW_COUNT = "row_count"
    NULL_CHECK = "null_check"
    UNIQUE_CHECK = "unique_check"
    RANGE_CHECK = "range_check"
    CUSTOM = "custom"


@dataclass
class TaskConfig:
    """Конфигурация задачи"""
    retries: int = 3
    retry_delay_seconds: int = 60
    timeout_seconds: int = 3600
    pool: str = "default"
    priority: int = 1
    queue: str = "default"


@dataclass
class Task:
    """Задача"""
    task_id: str
    name: str = ""
    description: str = ""
    
    # Тип задачи
    task_type: str = "python"  # python, sql, spark, shell
    
    # Конфигурация выполнения
    config: TaskConfig = field(default_factory=TaskConfig)
    
    # Код/команда
    callable: Optional[Callable] = None
    command: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Зависимости (task_ids)
    upstream: List[str] = field(default_factory=list)
    downstream: List[str] = field(default_factory=list)
    
    # Статус
    status: TaskStatus = TaskStatus.PENDING
    
    # Время выполнения
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0
    
    # Результат
    result: Any = None
    error_message: str = ""
    
    # Попытки
    attempt: int = 0


@dataclass
class QualityCheck:
    """Проверка качества"""
    check_id: str
    name: str = ""
    
    # Тип проверки
    check_type: QualityCheckType = QualityCheckType.ROW_COUNT
    
    # Параметры
    table: str = ""
    column: str = ""
    threshold: float = 0
    min_value: float = 0
    max_value: float = 0
    custom_sql: str = ""
    
    # Результат
    passed: bool = False
    actual_value: float = 0
    error_message: str = ""
    
    # Время
    executed_at: Optional[datetime] = None


@dataclass
class DataLineageNode:
    """Узел происхождения данных"""
    node_id: str
    name: str = ""
    node_type: str = ""  # table, file, api
    
    # Местоположение
    location: str = ""  # database.schema.table или path
    
    # Связи
    sources: List[str] = field(default_factory=list)  # node_ids
    targets: List[str] = field(default_factory=list)
    
    # Метаданные
    columns: List[str] = field(default_factory=list)
    row_count: int = 0
    
    # Последнее обновление
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class PipelineRun:
    """Запуск конвейера"""
    run_id: str
    pipeline_id: str = ""
    
    # Триггер
    trigger_type: TriggerType = TriggerType.MANUAL
    triggered_by: str = ""
    
    # Статус
    status: PipelineStatus = PipelineStatus.IDLE
    
    # Время
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0
    
    # Задачи
    task_runs: Dict[str, Task] = field(default_factory=dict)
    
    # Параметры запуска
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Окружение
    environment: str = "production"
    
    # Качество
    quality_checks: List[QualityCheck] = field(default_factory=list)


@dataclass
class Pipeline:
    """Конвейер данных"""
    pipeline_id: str
    name: str = ""
    description: str = ""
    
    # DAG задач
    tasks: Dict[str, Task] = field(default_factory=dict)
    
    # Расписание (cron)
    schedule: str = ""  # "0 2 * * *" - каждый день в 2:00
    
    # Настройки
    max_active_runs: int = 1
    catchup: bool = False
    
    # Параметры по умолчанию
    default_parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Владелец
    owner: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Качество
    quality_checks: List[QualityCheck] = field(default_factory=list)
    
    # История запусков
    runs: List[PipelineRun] = field(default_factory=list)
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_run_at: Optional[datetime] = None


class DAGValidator:
    """Валидатор DAG"""
    
    def validate(self, tasks: Dict[str, Task]) -> Tuple[bool, List[str]]:
        """Проверка корректности DAG"""
        errors = []
        
        # Проверяем на циклы
        if self._has_cycles(tasks):
            errors.append("DAG contains cycles")
            
        # Проверяем что все зависимости существуют
        for task_id, task in tasks.items():
            for upstream_id in task.upstream:
                if upstream_id not in tasks:
                    errors.append(f"Task {task_id} depends on non-existent task {upstream_id}")
                    
        return len(errors) == 0, errors
        
    def _has_cycles(self, tasks: Dict[str, Task]) -> bool:
        """Проверка на циклы"""
        visited = set()
        rec_stack = set()
        
        def dfs(task_id: str) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)
            
            task = tasks.get(task_id)
            if task:
                for upstream_id in task.upstream:
                    if upstream_id not in visited:
                        if dfs(upstream_id):
                            return True
                    elif upstream_id in rec_stack:
                        return True
                        
            rec_stack.remove(task_id)
            return False
            
        for task_id in tasks:
            if task_id not in visited:
                if dfs(task_id):
                    return True
                    
        return False
        
    def get_execution_order(self, tasks: Dict[str, Task]) -> List[List[str]]:
        """Получение порядка выполнения (по уровням)"""
        # Подсчёт входящих рёбер
        in_degree = {task_id: len(task.upstream) for task_id, task in tasks.items()}
        
        # Задачи без зависимостей
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        
        levels = []
        
        while queue:
            levels.append(queue.copy())
            next_queue = []
            
            for task_id in queue:
                task = tasks[task_id]
                for downstream_id in task.downstream:
                    in_degree[downstream_id] -= 1
                    if in_degree[downstream_id] == 0:
                        next_queue.append(downstream_id)
                        
            queue = next_queue
            
        return levels


class TaskExecutor:
    """Исполнитель задач"""
    
    def __init__(self):
        self.running_tasks: Dict[str, Task] = {}
        
    async def execute(self, task: Task, parameters: Dict[str, Any] = None) -> bool:
        """Выполнение задачи"""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        task.attempt += 1
        
        self.running_tasks[task.task_id] = task
        
        try:
            if task.callable:
                # Выполняем Python callable
                params = {**task.parameters, **(parameters or {})}
                
                if asyncio.iscoroutinefunction(task.callable):
                    task.result = await task.callable(**params)
                else:
                    task.result = task.callable(**params)
                    
            else:
                # Симуляция выполнения
                await asyncio.sleep(random.uniform(0.1, 0.5))
                
                # Случайная ошибка для демонстрации
                if random.random() < 0.1:
                    raise Exception("Simulated task failure")
                    
                task.result = {"status": "completed", "task": task.name}
                
            task.status = TaskStatus.SUCCESS
            
        except Exception as e:
            task.error_message = str(e)
            
            # Проверяем возможность retry
            if task.attempt < task.config.retries:
                task.status = TaskStatus.RETRYING
                return False
            else:
                task.status = TaskStatus.FAILED
                return False
                
        finally:
            task.completed_at = datetime.now()
            task.duration_seconds = (task.completed_at - task.started_at).total_seconds()
            del self.running_tasks[task.task_id]
            
        return True


class QualityGate:
    """Контроль качества"""
    
    async def run_checks(self, checks: List[QualityCheck]) -> Tuple[bool, List[QualityCheck]]:
        """Выполнение проверок"""
        all_passed = True
        results = []
        
        for check in checks:
            result = await self._run_check(check)
            results.append(result)
            
            if not result.passed:
                all_passed = False
                
        return all_passed, results
        
    async def _run_check(self, check: QualityCheck) -> QualityCheck:
        """Выполнение одной проверки"""
        check.executed_at = datetime.now()
        
        # Симуляция проверки
        if check.check_type == QualityCheckType.ROW_COUNT:
            check.actual_value = random.randint(1000, 100000)
            check.passed = check.actual_value >= check.threshold
            
        elif check.check_type == QualityCheckType.NULL_CHECK:
            check.actual_value = random.uniform(0, 10)  # % nulls
            check.passed = check.actual_value <= check.threshold
            
        elif check.check_type == QualityCheckType.UNIQUE_CHECK:
            check.actual_value = random.uniform(95, 100)  # % unique
            check.passed = check.actual_value >= check.threshold
            
        elif check.check_type == QualityCheckType.RANGE_CHECK:
            check.actual_value = random.uniform(check.min_value, check.max_value)
            check.passed = check.min_value <= check.actual_value <= check.max_value
            
        else:
            check.passed = random.random() > 0.1
            
        if not check.passed:
            check.error_message = f"Check failed: expected {check.threshold}, got {check.actual_value}"
            
        return check


class DataLineageTracker:
    """Отслеживание происхождения данных"""
    
    def __init__(self):
        self.nodes: Dict[str, DataLineageNode] = {}
        
    def register_node(self, name: str, node_type: str, location: str) -> DataLineageNode:
        """Регистрация узла"""
        node = DataLineageNode(
            node_id=f"node_{uuid.uuid4().hex[:8]}",
            name=name,
            node_type=node_type,
            location=location
        )
        self.nodes[node.node_id] = node
        return node
        
    def add_edge(self, source_id: str, target_id: str):
        """Добавление связи"""
        source = self.nodes.get(source_id)
        target = self.nodes.get(target_id)
        
        if source and target:
            if target_id not in source.targets:
                source.targets.append(target_id)
            if source_id not in target.sources:
                target.sources.append(source_id)
                
    def get_upstream(self, node_id: str, depth: int = 10) -> List[DataLineageNode]:
        """Получение upstream узлов"""
        result = []
        visited = set()
        
        def traverse(nid: str, d: int):
            if d <= 0 or nid in visited:
                return
            visited.add(nid)
            
            node = self.nodes.get(nid)
            if node:
                for source_id in node.sources:
                    source = self.nodes.get(source_id)
                    if source:
                        result.append(source)
                        traverse(source_id, d - 1)
                        
        traverse(node_id, depth)
        return result
        
    def get_downstream(self, node_id: str, depth: int = 10) -> List[DataLineageNode]:
        """Получение downstream узлов"""
        result = []
        visited = set()
        
        def traverse(nid: str, d: int):
            if d <= 0 or nid in visited:
                return
            visited.add(nid)
            
            node = self.nodes.get(nid)
            if node:
                for target_id in node.targets:
                    target = self.nodes.get(target_id)
                    if target:
                        result.append(target)
                        traverse(target_id, d - 1)
                        
        traverse(node_id, depth)
        return result


class PipelineOrchestrator:
    """Оркестратор конвейеров"""
    
    def __init__(self):
        self.pipelines: Dict[str, Pipeline] = {}
        self.dag_validator = DAGValidator()
        self.task_executor = TaskExecutor()
        self.quality_gate = QualityGate()
        self.lineage_tracker = DataLineageTracker()
        
        self.active_runs: Dict[str, PipelineRun] = {}
        
    def create_pipeline(self, name: str, description: str = "",
                         schedule: str = "", **kwargs) -> Pipeline:
        """Создание конвейера"""
        pipeline = Pipeline(
            pipeline_id=f"pipe_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            schedule=schedule,
            **kwargs
        )
        self.pipelines[pipeline.pipeline_id] = pipeline
        return pipeline
        
    def add_task(self, pipeline_id: str, name: str, task_type: str = "python",
                  upstream: List[str] = None, callable: Callable = None,
                  **kwargs) -> Task:
        """Добавление задачи"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline {pipeline_id} not found")
            
        task = Task(
            task_id=f"task_{uuid.uuid4().hex[:8]}",
            name=name,
            task_type=task_type,
            upstream=upstream or [],
            callable=callable,
            **kwargs
        )
        
        pipeline.tasks[task.task_id] = task
        
        # Обновляем downstream для upstream задач
        for upstream_id in task.upstream:
            upstream_task = pipeline.tasks.get(upstream_id)
            if upstream_task:
                upstream_task.downstream.append(task.task_id)
                
        return task
        
    def add_quality_check(self, pipeline_id: str, name: str,
                           check_type: QualityCheckType, **kwargs) -> QualityCheck:
        """Добавление проверки качества"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline {pipeline_id} not found")
            
        check = QualityCheck(
            check_id=f"qc_{uuid.uuid4().hex[:8]}",
            name=name,
            check_type=check_type,
            **kwargs
        )
        pipeline.quality_checks.append(check)
        return check
        
    async def run(self, pipeline_id: str, parameters: Dict[str, Any] = None,
                   trigger: TriggerType = TriggerType.MANUAL,
                   triggered_by: str = "") -> PipelineRun:
        """Запуск конвейера"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline {pipeline_id} not found")
            
        # Валидация DAG
        valid, errors = self.dag_validator.validate(pipeline.tasks)
        if not valid:
            raise ValueError(f"Invalid DAG: {errors}")
            
        # Создаём run
        run = PipelineRun(
            run_id=f"run_{uuid.uuid4().hex[:8]}",
            pipeline_id=pipeline_id,
            trigger_type=trigger,
            triggered_by=triggered_by,
            parameters={**pipeline.default_parameters, **(parameters or {})},
            status=PipelineStatus.RUNNING
        )
        
        # Копируем задачи для этого запуска
        for task_id, task in pipeline.tasks.items():
            run.task_runs[task_id] = Task(
                task_id=task.task_id,
                name=task.name,
                task_type=task.task_type,
                config=task.config,
                callable=task.callable,
                command=task.command,
                parameters=task.parameters,
                upstream=task.upstream.copy(),
                downstream=task.downstream.copy()
            )
            
        self.active_runs[run.run_id] = run
        
        # Получаем порядок выполнения
        execution_order = self.dag_validator.get_execution_order(run.task_runs)
        
        # Выполняем задачи по уровням
        for level in execution_order:
            # Проверяем upstream статусы
            tasks_to_run = []
            
            for task_id in level:
                task = run.task_runs[task_id]
                
                # Проверяем все upstream
                all_upstream_success = all(
                    run.task_runs[up_id].status == TaskStatus.SUCCESS
                    for up_id in task.upstream
                )
                
                any_upstream_failed = any(
                    run.task_runs[up_id].status in [TaskStatus.FAILED, TaskStatus.UPSTREAM_FAILED]
                    for up_id in task.upstream
                )
                
                if any_upstream_failed:
                    task.status = TaskStatus.UPSTREAM_FAILED
                elif all_upstream_success or not task.upstream:
                    tasks_to_run.append(task)
                    
            # Выполняем задачи этого уровня параллельно
            if tasks_to_run:
                await asyncio.gather(*[
                    self.task_executor.execute(task, run.parameters)
                    for task in tasks_to_run
                ])
                
        # Выполняем проверки качества
        if pipeline.quality_checks:
            passed, results = await self.quality_gate.run_checks(pipeline.quality_checks)
            run.quality_checks = results
            
        # Определяем статус run
        all_success = all(
            task.status == TaskStatus.SUCCESS
            for task in run.task_runs.values()
        )
        
        any_failed = any(
            task.status in [TaskStatus.FAILED, TaskStatus.UPSTREAM_FAILED]
            for task in run.task_runs.values()
        )
        
        if all_success:
            run.status = PipelineStatus.SUCCESS
        elif any_failed:
            run.status = PipelineStatus.FAILED
        else:
            run.status = PipelineStatus.SUCCESS
            
        run.completed_at = datetime.now()
        run.duration_seconds = (run.completed_at - run.started_at).total_seconds()
        
        # Сохраняем в историю
        pipeline.runs.append(run)
        pipeline.last_run_at = run.completed_at
        
        del self.active_runs[run.run_id]
        
        return run
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_runs = sum(len(p.runs) for p in self.pipelines.values())
        successful_runs = sum(
            1 for p in self.pipelines.values()
            for r in p.runs if r.status == PipelineStatus.SUCCESS
        )
        
        return {
            "total_pipelines": len(self.pipelines),
            "active_runs": len(self.active_runs),
            "total_runs": total_runs,
            "successful_runs": successful_runs,
            "success_rate": (successful_runs / total_runs * 100) if total_runs > 0 else 0
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 90: Data Pipeline Orchestration Platform")
    print("=" * 60)
    
    async def demo():
        orchestrator = PipelineOrchestrator()
        print("✓ Pipeline Orchestration Platform created")
        
        # Создание конвейера ETL
        print("\n📦 Creating ETL Pipeline...")
        
        etl_pipeline = orchestrator.create_pipeline(
            "daily_etl_pipeline",
            description="Daily ETL process for analytics",
            schedule="0 2 * * *",
            owner="data-team@company.com",
            tags=["etl", "analytics", "daily"]
        )
        
        print(f"\n  Pipeline: {etl_pipeline.name}")
        print(f"  Schedule: {etl_pipeline.schedule}")
        print(f"  ID: {etl_pipeline.pipeline_id}")
        
        # Добавление задач
        print("\n📝 Adding Tasks...")
        
        # Extract задачи
        async def extract_users():
            await asyncio.sleep(0.1)
            return {"rows": 10000, "table": "users"}
            
        async def extract_orders():
            await asyncio.sleep(0.1)
            return {"rows": 50000, "table": "orders"}
            
        async def extract_products():
            await asyncio.sleep(0.1)
            return {"rows": 5000, "table": "products"}
            
        extract_users_task = orchestrator.add_task(
            etl_pipeline.pipeline_id,
            "extract_users",
            task_type="python",
            callable=extract_users,
            description="Extract user data from source database"
        )
        print(f"  ✓ {extract_users_task.name}")
        
        extract_orders_task = orchestrator.add_task(
            etl_pipeline.pipeline_id,
            "extract_orders",
            task_type="python",
            callable=extract_orders,
            description="Extract order data from source database"
        )
        print(f"  ✓ {extract_orders_task.name}")
        
        extract_products_task = orchestrator.add_task(
            etl_pipeline.pipeline_id,
            "extract_products",
            task_type="python",
            callable=extract_products,
            description="Extract product data from source database"
        )
        print(f"  ✓ {extract_products_task.name}")
        
        # Transform задачи
        async def transform_users():
            await asyncio.sleep(0.1)
            return {"rows": 9500, "cleaned": True}
            
        async def transform_orders():
            await asyncio.sleep(0.1)
            return {"rows": 48000, "enriched": True}
            
        transform_users_task = orchestrator.add_task(
            etl_pipeline.pipeline_id,
            "transform_users",
            task_type="python",
            callable=transform_users,
            upstream=[extract_users_task.task_id],
            description="Clean and transform user data"
        )
        print(f"  ✓ {transform_users_task.name} (depends on: extract_users)")
        
        transform_orders_task = orchestrator.add_task(
            etl_pipeline.pipeline_id,
            "transform_orders",
            task_type="python",
            callable=transform_orders,
            upstream=[extract_orders_task.task_id, extract_products_task.task_id],
            description="Transform and enrich order data"
        )
        print(f"  ✓ {transform_orders_task.name} (depends on: extract_orders, extract_products)")
        
        # Load задачи
        async def load_to_warehouse():
            await asyncio.sleep(0.1)
            return {"loaded": True, "tables": ["dim_users", "fact_orders"]}
            
        load_task = orchestrator.add_task(
            etl_pipeline.pipeline_id,
            "load_to_warehouse",
            task_type="python",
            callable=load_to_warehouse,
            upstream=[transform_users_task.task_id, transform_orders_task.task_id],
            description="Load transformed data to data warehouse"
        )
        print(f"  ✓ {load_task.name} (depends on: transform_users, transform_orders)")
        
        # Aggregation
        async def build_aggregations():
            await asyncio.sleep(0.1)
            return {"aggregations": ["daily_sales", "user_stats"]}
            
        agg_task = orchestrator.add_task(
            etl_pipeline.pipeline_id,
            "build_aggregations",
            task_type="python",
            callable=build_aggregations,
            upstream=[load_task.task_id],
            description="Build analytics aggregations"
        )
        print(f"  ✓ {agg_task.name} (depends on: load_to_warehouse)")
        
        # Проверки качества
        print("\n✅ Adding Quality Checks...")
        
        orchestrator.add_quality_check(
            etl_pipeline.pipeline_id,
            "Users row count check",
            QualityCheckType.ROW_COUNT,
            table="dim_users",
            threshold=1000
        )
        
        orchestrator.add_quality_check(
            etl_pipeline.pipeline_id,
            "Orders null check",
            QualityCheckType.NULL_CHECK,
            table="fact_orders",
            column="order_id",
            threshold=0  # 0% nulls allowed
        )
        
        orchestrator.add_quality_check(
            etl_pipeline.pipeline_id,
            "User ID uniqueness",
            QualityCheckType.UNIQUE_CHECK,
            table="dim_users",
            column="user_id",
            threshold=99.99  # 99.99% unique required
        )
        
        print(f"  ✓ Added {len(etl_pipeline.quality_checks)} quality checks")
        
        # Отображение DAG
        print("\n🔀 Pipeline DAG:")
        
        execution_order = orchestrator.dag_validator.get_execution_order(etl_pipeline.tasks)
        
        for level, task_ids in enumerate(execution_order):
            tasks = [etl_pipeline.tasks[tid].name for tid in task_ids]
            print(f"  Level {level}: {' | '.join(tasks)}")
            
        # Визуализация DAG
        print("\n  DAG Visualization:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │ extract_users ─────┐                                        │")
        print("  │                    ├──> transform_users ──┐                 │")
        print("  │ extract_orders ────┤                      │                 │")
        print("  │                    ├──> transform_orders ─┼─> load ─> agg   │")
        print("  │ extract_products ──┘                      │                 │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
        # Запуск конвейера
        print("\n🚀 Running Pipeline...")
        
        run = await orchestrator.run(
            etl_pipeline.pipeline_id,
            parameters={"date": "2024-01-15"},
            trigger=TriggerType.MANUAL,
            triggered_by="data-engineer@company.com"
        )
        
        print(f"\n  Run ID: {run.run_id}")
        print(f"  Status: {run.status.value}")
        print(f"  Duration: {run.duration_seconds:.2f}s")
        
        # Статус задач
        print("\n📊 Task Status:")
        
        for task_id, task in run.task_runs.items():
            status_icon = {
                TaskStatus.SUCCESS: "✅",
                TaskStatus.FAILED: "❌",
                TaskStatus.SKIPPED: "⏭️",
                TaskStatus.UPSTREAM_FAILED: "⬆️❌"
            }.get(task.status, "⚪")
            
            print(f"  {status_icon} {task.name}: {task.status.value}")
            if task.duration_seconds > 0:
                print(f"      Duration: {task.duration_seconds:.3f}s")
            if task.result:
                print(f"      Result: {task.result}")
            if task.error_message:
                print(f"      Error: {task.error_message}")
                
        # Результаты проверок качества
        print("\n✅ Quality Check Results:")
        
        for check in run.quality_checks:
            status_icon = "✅" if check.passed else "❌"
            print(f"  {status_icon} {check.name}")
            print(f"      Type: {check.check_type.value}")
            print(f"      Actual: {check.actual_value:.2f}")
            if not check.passed:
                print(f"      Error: {check.error_message}")
                
        # Data Lineage
        print("\n🔗 Data Lineage:")
        
        # Регистрируем узлы
        source_users = orchestrator.lineage_tracker.register_node(
            "source_users", "table", "source_db.public.users"
        )
        source_orders = orchestrator.lineage_tracker.register_node(
            "source_orders", "table", "source_db.public.orders"
        )
        source_products = orchestrator.lineage_tracker.register_node(
            "source_products", "table", "source_db.public.products"
        )
        
        dim_users = orchestrator.lineage_tracker.register_node(
            "dim_users", "table", "warehouse.analytics.dim_users"
        )
        fact_orders = orchestrator.lineage_tracker.register_node(
            "fact_orders", "table", "warehouse.analytics.fact_orders"
        )
        
        daily_sales = orchestrator.lineage_tracker.register_node(
            "daily_sales", "table", "warehouse.analytics.daily_sales"
        )
        
        # Связи
        orchestrator.lineage_tracker.add_edge(source_users.node_id, dim_users.node_id)
        orchestrator.lineage_tracker.add_edge(source_orders.node_id, fact_orders.node_id)
        orchestrator.lineage_tracker.add_edge(source_products.node_id, fact_orders.node_id)
        orchestrator.lineage_tracker.add_edge(dim_users.node_id, daily_sales.node_id)
        orchestrator.lineage_tracker.add_edge(fact_orders.node_id, daily_sales.node_id)
        
        print("\n  Lineage Graph:")
        print("  source_users ────> dim_users ────┐")
        print("                                    ├──> daily_sales")
        print("  source_orders ──┬─> fact_orders ─┘")
        print("  source_products ┘")
        
        # Upstream для daily_sales
        upstream = orchestrator.lineage_tracker.get_upstream(daily_sales.node_id)
        print(f"\n  Upstream of daily_sales:")
        for node in upstream:
            print(f"    ← {node.name} ({node.location})")
            
        # Запускаем ещё несколько раз для статистики
        print("\n🔄 Running Additional Pipeline Executions...")
        
        for i in range(3):
            await orchestrator.run(
                etl_pipeline.pipeline_id,
                parameters={"date": f"2024-01-{16+i}"},
                trigger=TriggerType.SCHEDULED
            )
            
        print(f"  ✓ Completed 3 additional runs")
        
        # Статистика
        print("\n📊 Orchestration Statistics:")
        
        stats = orchestrator.get_statistics()
        
        print(f"\n  Total Pipelines: {stats['total_pipelines']}")
        print(f"  Total Runs: {stats['total_runs']}")
        print(f"  Successful Runs: {stats['successful_runs']}")
        print(f"  Success Rate: {stats['success_rate']:.1f}%")
        print(f"  Active Runs: {stats['active_runs']}")
        
        # История запусков
        print("\n📜 Run History:")
        
        for run in etl_pipeline.runs[-5:]:
            status_icon = "✅" if run.status == PipelineStatus.SUCCESS else "❌"
            print(f"\n  {status_icon} {run.run_id}")
            print(f"     Started: {run.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"     Duration: {run.duration_seconds:.2f}s")
            print(f"     Trigger: {run.trigger_type.value}")
            
        # Dashboard
        print("\n📋 Pipeline Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print(f"  │ Pipeline: {etl_pipeline.name:40} │")
        print(f"  │ Schedule: {etl_pipeline.schedule:40} │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Runs:     {len(etl_pipeline.runs):>6}                               │")
        print(f"  │ Success Rate:   {stats['success_rate']:>5.1f}%                               │")
        print(f"  │ Tasks:          {len(etl_pipeline.tasks):>6}                               │")
        print(f"  │ Quality Checks: {len(etl_pipeline.quality_checks):>6}                               │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Data Pipeline Orchestration Platform initialized!")
    print("=" * 60)
