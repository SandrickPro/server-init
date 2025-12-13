#!/usr/bin/env python3
"""
Server Init - Iteration 78: Data Pipeline Management
Управление дата-пайплайнами

Функционал:
- Pipeline Definition - определение пайплайнов
- DAG Management - управление DAG
- Task Orchestration - оркестрация задач
- Data Lineage - отслеживание данных
- Pipeline Monitoring - мониторинг пайплайнов
- Scheduling - планирование запусков
- Error Handling - обработка ошибок
- Data Quality - качество данных
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Awaitable
from enum import Enum
from collections import defaultdict, deque
import uuid
import time
import hashlib


class TaskStatus(Enum):
    """Статус задачи"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    UPSTREAM_FAILED = "upstream_failed"
    RETRY = "retry"


class PipelineStatus(Enum):
    """Статус пайплайна"""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PAUSED = "paused"


class ScheduleType(Enum):
    """Тип расписания"""
    ONCE = "once"
    INTERVAL = "interval"
    CRON = "cron"
    EVENT = "event"


class TriggerType(Enum):
    """Тип триггера"""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    DATA_ARRIVAL = "data_arrival"
    API = "api"
    UPSTREAM = "upstream"


class DataFormat(Enum):
    """Формат данных"""
    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"
    AVRO = "avro"
    ORC = "orc"


@dataclass
class DataSource:
    """Источник данных"""
    source_id: str
    name: str = ""
    
    # Тип источника
    source_type: str = ""  # database, file, api, stream
    
    # Подключение
    connection_string: str = ""
    
    # Формат
    format: DataFormat = DataFormat.JSON
    
    # Схема
    schema: Dict[str, str] = field(default_factory=dict)
    
    # Метаданные
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataSink:
    """Приёмник данных"""
    sink_id: str
    name: str = ""
    
    # Тип
    sink_type: str = ""  # database, file, api, stream
    
    # Подключение
    connection_string: str = ""
    
    # Формат
    format: DataFormat = DataFormat.JSON
    
    # Партиционирование
    partition_by: List[str] = field(default_factory=list)
    
    # Метаданные
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskDefinition:
    """Определение задачи"""
    task_id: str
    name: str = ""
    
    # Тип задачи
    task_type: str = ""  # extract, transform, load, validate, custom
    
    # Зависимости
    dependencies: List[str] = field(default_factory=list)
    
    # Источники и приёмники
    sources: List[str] = field(default_factory=list)
    sinks: List[str] = field(default_factory=list)
    
    # Функция обработки
    handler: Optional[Callable] = None
    
    # Параметры
    params: Dict[str, Any] = field(default_factory=dict)
    
    # Retry
    retries: int = 3
    retry_delay_seconds: int = 60
    
    # Timeout
    timeout_seconds: int = 3600
    
    # Приоритет
    priority: int = 0


@dataclass
class TaskInstance:
    """Экземпляр задачи"""
    instance_id: str
    task_id: str
    run_id: str = ""
    
    # Статус
    status: TaskStatus = TaskStatus.PENDING
    
    # Время
    queued_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    
    # Retry
    try_number: int = 1
    
    # Результат
    result: Any = None
    error: str = ""
    
    # Метрики
    rows_processed: int = 0
    bytes_processed: int = 0
    
    # Контекст
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Schedule:
    """Расписание"""
    schedule_id: str
    
    # Тип
    schedule_type: ScheduleType = ScheduleType.INTERVAL
    
    # Интервал
    interval_seconds: int = 3600
    
    # Cron expression
    cron: str = ""  # "0 * * * *"
    
    # Start/End
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    # Следующий запуск
    next_run: Optional[datetime] = None
    
    # Статус
    enabled: bool = True


@dataclass
class PipelineDefinition:
    """Определение пайплайна"""
    pipeline_id: str
    name: str = ""
    description: str = ""
    
    # Задачи
    tasks: Dict[str, TaskDefinition] = field(default_factory=dict)
    
    # Расписание
    schedule: Optional[Schedule] = None
    
    # Параметры по умолчанию
    default_params: Dict[str, Any] = field(default_factory=dict)
    
    # Источники и приёмники
    sources: Dict[str, DataSource] = field(default_factory=dict)
    sinks: Dict[str, DataSink] = field(default_factory=dict)
    
    # Метаданные
    tags: List[str] = field(default_factory=list)
    owner: str = ""
    
    # Настройки
    max_parallel_tasks: int = 4
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PipelineRun:
    """Запуск пайплайна"""
    run_id: str
    pipeline_id: str = ""
    
    # Статус
    status: PipelineStatus = PipelineStatus.IDLE
    
    # Триггер
    trigger_type: TriggerType = TriggerType.MANUAL
    
    # Время
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    
    # Задачи
    task_instances: Dict[str, TaskInstance] = field(default_factory=dict)
    
    # Параметры запуска
    params: Dict[str, Any] = field(default_factory=dict)
    
    # Результат
    error: str = ""


@dataclass
class DataLineage:
    """Происхождение данных"""
    lineage_id: str
    
    # Источник
    source_dataset: str = ""
    source_task: str = ""
    
    # Назначение
    destination_dataset: str = ""
    destination_task: str = ""
    
    # Трансформации
    transformations: List[str] = field(default_factory=list)
    
    # Время
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DataQualityRule:
    """Правило качества данных"""
    rule_id: str
    name: str = ""
    
    # Правило
    rule_type: str = ""  # not_null, unique, range, regex, custom
    column: str = ""
    
    # Параметры
    params: Dict[str, Any] = field(default_factory=dict)
    
    # Серьёзность
    severity: str = "warning"  # warning, error, critical
    
    # Статус
    enabled: bool = True


@dataclass
class QualityCheckResult:
    """Результат проверки качества"""
    check_id: str
    rule_id: str = ""
    
    # Результат
    passed: bool = True
    
    # Статистика
    total_rows: int = 0
    failed_rows: int = 0
    pass_rate: float = 100.0
    
    # Примеры ошибок
    sample_failures: List[Dict[str, Any]] = field(default_factory=list)
    
    # Время
    checked_at: datetime = field(default_factory=datetime.now)


class DAGBuilder:
    """Построитель DAG"""
    
    def __init__(self):
        self.nodes: Dict[str, TaskDefinition] = {}
        self.edges: Dict[str, List[str]] = defaultdict(list)  # child -> parents
        
    def add_task(self, task: TaskDefinition):
        """Добавление задачи"""
        self.nodes[task.task_id] = task
        
        for dep in task.dependencies:
            self.edges[task.task_id].append(dep)
            
    def get_execution_order(self) -> List[List[str]]:
        """Получение порядка выполнения (по уровням)"""
        in_degree = defaultdict(int)
        
        for node in self.nodes:
            in_degree[node] = len(self.edges[node])
            
        levels = []
        processed = set()
        
        while len(processed) < len(self.nodes):
            # Задачи без зависимостей или с выполненными зависимостями
            level = []
            
            for node in self.nodes:
                if node in processed:
                    continue
                    
                all_deps_processed = all(
                    dep in processed for dep in self.edges[node]
                )
                
                if all_deps_processed:
                    level.append(node)
                    
            if not level:
                raise ValueError("Circular dependency detected!")
                
            levels.append(level)
            processed.update(level)
            
        return levels
        
    def validate(self) -> List[str]:
        """Валидация DAG"""
        errors = []
        
        # Проверка на циклы
        try:
            self.get_execution_order()
        except ValueError as e:
            errors.append(str(e))
            
        # Проверка зависимостей
        for task_id, deps in self.edges.items():
            for dep in deps:
                if dep not in self.nodes:
                    errors.append(f"Task {task_id} depends on unknown task {dep}")
                    
        return errors


class TaskExecutor:
    """Исполнитель задач"""
    
    def __init__(self):
        self.running_tasks: Dict[str, TaskInstance] = {}
        
    async def execute(self, task: TaskDefinition, instance: TaskInstance,
                       context: Dict[str, Any]) -> TaskInstance:
        """Выполнение задачи"""
        instance.status = TaskStatus.RUNNING
        instance.started_at = datetime.now()
        instance.context = context
        
        try:
            if task.handler:
                result = await asyncio.wait_for(
                    task.handler(context, task.params),
                    timeout=task.timeout_seconds
                )
                instance.result = result
                instance.status = TaskStatus.SUCCESS
            else:
                # Симуляция задачи
                await asyncio.sleep(0.1)
                instance.result = {"status": "completed"}
                instance.status = TaskStatus.SUCCESS
                instance.rows_processed = context.get("rows", 100)
                
        except asyncio.TimeoutError:
            instance.status = TaskStatus.FAILED
            instance.error = f"Timeout after {task.timeout_seconds}s"
            
        except Exception as e:
            instance.status = TaskStatus.FAILED
            instance.error = str(e)
            
        finally:
            instance.finished_at = datetime.now()
            
        return instance


class PipelineScheduler:
    """Планировщик пайплайнов"""
    
    def __init__(self):
        self.schedules: Dict[str, Schedule] = {}
        self.next_runs: Dict[str, datetime] = {}
        
    def add_schedule(self, pipeline_id: str, schedule: Schedule):
        """Добавление расписания"""
        self.schedules[pipeline_id] = schedule
        self._calculate_next_run(pipeline_id)
        
    def _calculate_next_run(self, pipeline_id: str):
        """Расчёт следующего запуска"""
        schedule = self.schedules.get(pipeline_id)
        if not schedule or not schedule.enabled:
            return
            
        now = datetime.now()
        
        if schedule.schedule_type == ScheduleType.INTERVAL:
            next_run = now + timedelta(seconds=schedule.interval_seconds)
        elif schedule.schedule_type == ScheduleType.ONCE:
            next_run = schedule.start_date
        else:
            # Для cron - упрощённая версия
            next_run = now + timedelta(hours=1)
            
        if schedule.end_date and next_run > schedule.end_date:
            next_run = None
            
        self.next_runs[pipeline_id] = next_run
        
    def get_due_pipelines(self) -> List[str]:
        """Получение пайплайнов для запуска"""
        now = datetime.now()
        due = []
        
        for pipeline_id, next_run in self.next_runs.items():
            if next_run and next_run <= now:
                due.append(pipeline_id)
                
        return due


class DataQualityChecker:
    """Проверка качества данных"""
    
    def __init__(self):
        self.rules: Dict[str, DataQualityRule] = {}
        self.results: List[QualityCheckResult] = []
        
    def add_rule(self, rule: DataQualityRule):
        """Добавление правила"""
        self.rules[rule.rule_id] = rule
        
    def check(self, data: List[Dict[str, Any]], dataset: str = "") -> List[QualityCheckResult]:
        """Проверка данных"""
        results = []
        
        for rule in self.rules.values():
            if not rule.enabled:
                continue
                
            result = self._check_rule(rule, data)
            results.append(result)
            self.results.append(result)
            
        return results
        
    def _check_rule(self, rule: DataQualityRule,
                     data: List[Dict[str, Any]]) -> QualityCheckResult:
        """Проверка одного правила"""
        total = len(data)
        failed = 0
        failures = []
        
        for row in data:
            value = row.get(rule.column)
            
            if rule.rule_type == "not_null":
                if value is None:
                    failed += 1
                    if len(failures) < 5:
                        failures.append({"row": row, "error": "NULL value"})
                        
            elif rule.rule_type == "unique":
                # Упрощённая проверка
                pass
                
            elif rule.rule_type == "range":
                min_val = rule.params.get("min", float("-inf"))
                max_val = rule.params.get("max", float("inf"))
                if value is not None and (value < min_val or value > max_val):
                    failed += 1
                    if len(failures) < 5:
                        failures.append({"row": row, "error": f"Out of range [{min_val}, {max_val}]"})
                        
        pass_rate = ((total - failed) / total * 100) if total > 0 else 100.0
        
        return QualityCheckResult(
            check_id=f"check_{uuid.uuid4().hex[:8]}",
            rule_id=rule.rule_id,
            passed=failed == 0,
            total_rows=total,
            failed_rows=failed,
            pass_rate=pass_rate,
            sample_failures=failures
        )


class DataPipelinePlatform:
    """Платформа управления пайплайнами"""
    
    def __init__(self):
        self.pipelines: Dict[str, PipelineDefinition] = {}
        self.runs: Dict[str, PipelineRun] = {}
        self.lineage: List[DataLineage] = []
        
        self.executor = TaskExecutor()
        self.scheduler = PipelineScheduler()
        self.quality_checker = DataQualityChecker()
        
    def create_pipeline(self, name: str, **kwargs) -> PipelineDefinition:
        """Создание пайплайна"""
        pipeline = PipelineDefinition(
            pipeline_id=f"pipe_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        self.pipelines[pipeline.pipeline_id] = pipeline
        return pipeline
        
    def add_task(self, pipeline_id: str, name: str, **kwargs) -> TaskDefinition:
        """Добавление задачи"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline {pipeline_id} not found")
            
        task = TaskDefinition(
            task_id=f"task_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        pipeline.tasks[task.task_id] = task
        return task
        
    def add_source(self, pipeline_id: str, name: str, **kwargs) -> DataSource:
        """Добавление источника"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline {pipeline_id} not found")
            
        source = DataSource(
            source_id=f"src_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        pipeline.sources[source.source_id] = source
        return source
        
    def add_sink(self, pipeline_id: str, name: str, **kwargs) -> DataSink:
        """Добавление приёмника"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline {pipeline_id} not found")
            
        sink = DataSink(
            sink_id=f"sink_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        pipeline.sinks[sink.sink_id] = sink
        return sink
        
    async def run_pipeline(self, pipeline_id: str,
                            params: Dict[str, Any] = None,
                            trigger: TriggerType = TriggerType.MANUAL) -> PipelineRun:
        """Запуск пайплайна"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline {pipeline_id} not found")
            
        run = PipelineRun(
            run_id=f"run_{uuid.uuid4().hex[:8]}",
            pipeline_id=pipeline_id,
            status=PipelineStatus.RUNNING,
            trigger_type=trigger,
            started_at=datetime.now(),
            params=params or {}
        )
        self.runs[run.run_id] = run
        
        # Построение DAG
        dag = DAGBuilder()
        for task in pipeline.tasks.values():
            dag.add_task(task)
            
        errors = dag.validate()
        if errors:
            run.status = PipelineStatus.FAILED
            run.error = "; ".join(errors)
            return run
            
        # Выполнение по уровням
        try:
            execution_order = dag.get_execution_order()
            
            for level in execution_order:
                # Параллельное выполнение задач на уровне
                tasks = []
                
                for task_id in level:
                    task = pipeline.tasks[task_id]
                    instance = TaskInstance(
                        instance_id=f"inst_{uuid.uuid4().hex[:8]}",
                        task_id=task_id,
                        run_id=run.run_id,
                        queued_at=datetime.now()
                    )
                    run.task_instances[task_id] = instance
                    
                    # Проверяем upstream failures
                    upstream_failed = False
                    for dep in task.dependencies:
                        dep_instance = run.task_instances.get(dep)
                        if dep_instance and dep_instance.status == TaskStatus.FAILED:
                            instance.status = TaskStatus.UPSTREAM_FAILED
                            upstream_failed = True
                            break
                            
                    if not upstream_failed:
                        context = {**pipeline.default_params, **run.params}
                        tasks.append(self.executor.execute(task, instance, context))
                        
                # Ждём выполнения уровня
                if tasks:
                    await asyncio.gather(*tasks)
                    
            # Проверяем итоговый статус
            all_success = all(
                inst.status == TaskStatus.SUCCESS
                for inst in run.task_instances.values()
            )
            run.status = PipelineStatus.SUCCESS if all_success else PipelineStatus.FAILED
            
        except Exception as e:
            run.status = PipelineStatus.FAILED
            run.error = str(e)
            
        finally:
            run.finished_at = datetime.now()
            
        return run
        
    def record_lineage(self, source_dataset: str, source_task: str,
                        dest_dataset: str, dest_task: str,
                        transformations: List[str] = None):
        """Запись lineage"""
        lineage = DataLineage(
            lineage_id=f"lin_{uuid.uuid4().hex[:8]}",
            source_dataset=source_dataset,
            source_task=source_task,
            destination_dataset=dest_dataset,
            destination_task=dest_task,
            transformations=transformations or []
        )
        self.lineage.append(lineage)
        
    def get_lineage(self, dataset: str) -> List[DataLineage]:
        """Получение lineage для датасета"""
        return [
            l for l in self.lineage
            if l.source_dataset == dataset or l.destination_dataset == dataset
        ]
        
    def add_quality_rule(self, **kwargs) -> DataQualityRule:
        """Добавление правила качества"""
        rule = DataQualityRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            **kwargs
        )
        self.quality_checker.add_rule(rule)
        return rule
        
    def get_stats(self) -> Dict[str, Any]:
        """Статистика"""
        total_runs = len(self.runs)
        success_runs = len([r for r in self.runs.values() if r.status == PipelineStatus.SUCCESS])
        
        return {
            "pipelines": len(self.pipelines),
            "total_runs": total_runs,
            "success_runs": success_runs,
            "failed_runs": total_runs - success_runs,
            "success_rate": f"{success_runs/total_runs*100:.1f}%" if total_runs > 0 else "N/A",
            "lineage_records": len(self.lineage),
            "quality_rules": len(self.quality_checker.rules)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 78: Data Pipeline Management")
    print("=" * 60)
    
    async def demo():
        platform = DataPipelinePlatform()
        print("✓ Data Pipeline Platform created")
        
        # Создание пайплайна ETL
        print("\n📊 Creating ETL Pipeline...")
        
        pipeline = platform.create_pipeline(
            name="Sales Data ETL",
            description="Extract, transform and load sales data",
            tags=["sales", "etl", "daily"],
            owner="data-team",
            max_parallel_tasks=4
        )
        print(f"  ✓ Pipeline: {pipeline.name}")
        
        # Добавление источников
        print("\n📥 Adding Data Sources...")
        
        sales_db = platform.add_source(
            pipeline.pipeline_id,
            "Sales Database",
            source_type="database",
            connection_string="postgresql://db.example.com:5432/sales",
            format=DataFormat.JSON,
            schema={"id": "int", "amount": "decimal", "date": "timestamp"}
        )
        print(f"  ✓ Source: {sales_db.name}")
        
        customers_api = platform.add_source(
            pipeline.pipeline_id,
            "Customers API",
            source_type="api",
            connection_string="https://api.example.com/customers",
            format=DataFormat.JSON
        )
        print(f"  ✓ Source: {customers_api.name}")
        
        # Добавление приёмников
        print("\n📤 Adding Data Sinks...")
        
        warehouse = platform.add_sink(
            pipeline.pipeline_id,
            "Data Warehouse",
            sink_type="database",
            connection_string="snowflake://warehouse.example.com/analytics",
            format=DataFormat.PARQUET,
            partition_by=["date", "region"]
        )
        print(f"  ✓ Sink: {warehouse.name}")
        
        # Добавление задач
        print("\n📋 Adding Pipeline Tasks...")
        
        extract_sales = platform.add_task(
            pipeline.pipeline_id,
            "Extract Sales",
            task_type="extract",
            sources=[sales_db.source_id],
            params={"query": "SELECT * FROM sales WHERE date >= :start_date"}
        )
        print(f"  ✓ Task: {extract_sales.name}")
        
        extract_customers = platform.add_task(
            pipeline.pipeline_id,
            "Extract Customers",
            task_type="extract",
            sources=[customers_api.source_id],
            params={"endpoint": "/v1/customers"}
        )
        print(f"  ✓ Task: {extract_customers.name}")
        
        transform_join = platform.add_task(
            pipeline.pipeline_id,
            "Join Data",
            task_type="transform",
            dependencies=[extract_sales.task_id, extract_customers.task_id],
            params={"join_key": "customer_id"}
        )
        print(f"  ✓ Task: {transform_join.name}")
        
        validate_data = platform.add_task(
            pipeline.pipeline_id,
            "Validate Data",
            task_type="validate",
            dependencies=[transform_join.task_id]
        )
        print(f"  ✓ Task: {validate_data.name}")
        
        load_warehouse = platform.add_task(
            pipeline.pipeline_id,
            "Load to Warehouse",
            task_type="load",
            dependencies=[validate_data.task_id],
            sinks=[warehouse.sink_id],
            retries=3,
            retry_delay_seconds=120
        )
        print(f"  ✓ Task: {load_warehouse.name}")
        
        # Визуализация DAG
        print("\n🔗 Pipeline DAG:")
        dag = DAGBuilder()
        for task in pipeline.tasks.values():
            dag.add_task(task)
            
        levels = dag.get_execution_order()
        for i, level in enumerate(levels):
            task_names = [pipeline.tasks[t].name for t in level]
            print(f"  Level {i}: {' | '.join(task_names)}")
            
        # Запуск пайплайна
        print("\n🚀 Running Pipeline...")
        
        run = await platform.run_pipeline(
            pipeline.pipeline_id,
            params={"start_date": "2024-01-01"},
            trigger=TriggerType.MANUAL
        )
        
        print(f"\n  Run ID: {run.run_id}")
        print(f"  Status: {run.status.value}")
        print(f"  Duration: {(run.finished_at - run.started_at).total_seconds():.2f}s")
        
        print("\n  Task Results:")
        for task_id, instance in run.task_instances.items():
            task = pipeline.tasks[task_id]
            status_icon = "✓" if instance.status == TaskStatus.SUCCESS else "✗"
            duration = ""
            if instance.started_at and instance.finished_at:
                duration = f" ({(instance.finished_at - instance.started_at).total_seconds():.2f}s)"
            print(f"    {status_icon} {task.name}: {instance.status.value}{duration}")
            
        # Data Lineage
        print("\n📈 Recording Data Lineage...")
        
        platform.record_lineage(
            source_dataset="sales_db.sales",
            source_task=extract_sales.task_id,
            dest_dataset="staging.sales_raw",
            dest_task=transform_join.task_id,
            transformations=["filter", "dedupe"]
        )
        
        platform.record_lineage(
            source_dataset="api.customers",
            source_task=extract_customers.task_id,
            dest_dataset="staging.customers_raw",
            dest_task=transform_join.task_id,
            transformations=["normalize"]
        )
        
        platform.record_lineage(
            source_dataset="staging.sales_raw",
            source_task=transform_join.task_id,
            dest_dataset="warehouse.sales_enriched",
            dest_task=load_warehouse.task_id,
            transformations=["join", "aggregate", "partition"]
        )
        
        print(f"  ✓ Recorded {len(platform.lineage)} lineage records")
        
        # Просмотр lineage
        lineage = platform.get_lineage("staging.sales_raw")
        print(f"\n  Lineage for 'staging.sales_raw':")
        for l in lineage:
            direction = "→" if l.source_dataset == "staging.sales_raw" else "←"
            other = l.destination_dataset if direction == "→" else l.source_dataset
            print(f"    {direction} {other}")
            if l.transformations:
                print(f"      Transforms: {', '.join(l.transformations)}")
                
        # Data Quality
        print("\n🔍 Data Quality Rules...")
        
        amount_rule = platform.add_quality_rule(
            name="Amount Not Null",
            rule_type="not_null",
            column="amount",
            severity="error"
        )
        print(f"  ✓ Rule: {amount_rule.name}")
        
        range_rule = platform.add_quality_rule(
            name="Amount Positive",
            rule_type="range",
            column="amount",
            params={"min": 0, "max": 1000000},
            severity="warning"
        )
        print(f"  ✓ Rule: {range_rule.name}")
        
        # Проверка качества
        print("\n  Running Quality Checks...")
        
        sample_data = [
            {"id": 1, "amount": 100.0, "customer_id": "C1"},
            {"id": 2, "amount": None, "customer_id": "C2"},
            {"id": 3, "amount": 250.0, "customer_id": "C3"},
            {"id": 4, "amount": -50.0, "customer_id": "C4"},
            {"id": 5, "amount": 1500000.0, "customer_id": "C5"},
        ]
        
        results = platform.quality_checker.check(sample_data)
        
        for result in results:
            rule = platform.quality_checker.rules[result.rule_id]
            status = "✓ PASSED" if result.passed else "✗ FAILED"
            print(f"\n    {status}: {rule.name}")
            print(f"      Pass rate: {result.pass_rate:.1f}%")
            print(f"      Failed rows: {result.failed_rows}/{result.total_rows}")
            
            if result.sample_failures:
                print("      Sample failures:")
                for failure in result.sample_failures[:2]:
                    print(f"        - {failure['error']}")
                    
        # Создание второго пайплайна
        print("\n📊 Creating Second Pipeline (Streaming)...")
        
        stream_pipeline = platform.create_pipeline(
            name="Real-time Events",
            description="Process streaming events",
            tags=["streaming", "real-time"],
            owner="data-team"
        )
        
        event_source = platform.add_source(
            stream_pipeline.pipeline_id,
            "Kafka Events",
            source_type="stream",
            connection_string="kafka://kafka.example.com:9092/events"
        )
        
        process_task = platform.add_task(
            stream_pipeline.pipeline_id,
            "Process Events",
            task_type="transform"
        )
        
        print(f"  ✓ Pipeline: {stream_pipeline.name}")
        
        # Запуск второго пайплайна
        run2 = await platform.run_pipeline(stream_pipeline.pipeline_id)
        print(f"  ✓ Run status: {run2.status.value}")
        
        # Статистика
        print("\n📊 Platform Statistics:")
        stats = platform.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
        # Список пайплайнов
        print("\n📋 All Pipelines:")
        for p in platform.pipelines.values():
            run_count = len([r for r in platform.runs.values() if r.pipeline_id == p.pipeline_id])
            print(f"  • {p.name}")
            print(f"    Tasks: {len(p.tasks)}, Sources: {len(p.sources)}, Sinks: {len(p.sinks)}")
            print(f"    Runs: {run_count}")
            
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Data Pipeline Management Platform initialized!")
    print("=" * 60)
