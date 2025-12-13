#!/usr/bin/env python3
"""
Server Init - Iteration 62: Data Pipeline & ETL Platform
Платформа обработки данных и ETL

Функционал:
- Pipeline Orchestration - оркестрация пайплайнов
- Data Extraction - извлечение данных
- Data Transformation - трансформация данных
- Data Loading - загрузка данных
- Scheduling - планирование
- Data Quality - качество данных
- Lineage Tracking - отслеживание происхождения
- Incremental Processing - инкрементальная обработка
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from collections import defaultdict
import uuid
import hashlib


class PipelineStatus(Enum):
    """Статус пайплайна"""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStatus(Enum):
    """Статус задачи"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    UPSTREAM_FAILED = "upstream_failed"


class DataSourceType(Enum):
    """Тип источника данных"""
    DATABASE = "database"
    API = "api"
    FILE = "file"
    STREAM = "stream"
    S3 = "s3"
    KAFKA = "kafka"


class TransformType(Enum):
    """Тип трансформации"""
    MAP = "map"
    FILTER = "filter"
    AGGREGATE = "aggregate"
    JOIN = "join"
    PIVOT = "pivot"
    CUSTOM = "custom"


class ScheduleType(Enum):
    """Тип расписания"""
    CRON = "cron"
    INTERVAL = "interval"
    MANUAL = "manual"
    EVENT = "event"


@dataclass
class DataSource:
    """Источник данных"""
    source_id: str
    name: str
    source_type: DataSourceType
    
    # Подключение
    connection_config: Dict[str, Any] = field(default_factory=dict)
    
    # Схема
    schema: Dict[str, str] = field(default_factory=dict)
    
    # Метаданные
    description: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class DataDestination:
    """Назначение данных"""
    destination_id: str
    name: str
    destination_type: DataSourceType
    
    # Подключение
    connection_config: Dict[str, Any] = field(default_factory=dict)
    
    # Настройки записи
    write_mode: str = "append"  # append, overwrite, merge
    partition_by: List[str] = field(default_factory=list)


@dataclass
class Transform:
    """Трансформация"""
    transform_id: str
    name: str
    transform_type: TransformType
    
    # Конфигурация
    config: Dict[str, Any] = field(default_factory=dict)
    
    # SQL (если применимо)
    sql: str = ""
    
    # Функция (для custom)
    function_name: str = ""


@dataclass
class Task:
    """Задача в пайплайне"""
    task_id: str
    name: str
    
    # Тип задачи
    task_type: str = "transform"  # extract, transform, load, custom
    
    # Конфигурация
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Зависимости
    depends_on: List[str] = field(default_factory=list)
    
    # Статус
    status: TaskStatus = TaskStatus.PENDING
    
    # Время
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Результаты
    output: Any = None
    error: Optional[str] = None
    
    # Retry
    retries: int = 0
    max_retries: int = 3


@dataclass
class Pipeline:
    """Пайплайн данных"""
    pipeline_id: str
    name: str
    
    # Описание
    description: str = ""
    
    # Задачи
    tasks: List[Task] = field(default_factory=list)
    
    # Статус
    status: PipelineStatus = PipelineStatus.IDLE
    
    # Расписание
    schedule_type: ScheduleType = ScheduleType.MANUAL
    schedule_config: Dict[str, Any] = field(default_factory=dict)
    
    # Параметры
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    
    # Статистика
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0


@dataclass
class PipelineRun:
    """Запуск пайплайна"""
    run_id: str
    pipeline_id: str
    
    # Статус
    status: PipelineStatus = PipelineStatus.RUNNING
    
    # Задачи
    task_runs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Параметры
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Время
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    # Метрики
    records_processed: int = 0
    records_failed: int = 0


@dataclass
class DataQualityRule:
    """Правило качества данных"""
    rule_id: str
    name: str
    
    # Тип проверки
    check_type: str = ""  # not_null, unique, range, regex, custom
    
    # Конфигурация
    column: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Severity
    severity: str = "warning"  # warning, error
    
    # Статус
    enabled: bool = True


@dataclass
class DataQualityResult:
    """Результат проверки качества"""
    rule_id: str
    passed: bool
    
    # Детали
    total_records: int = 0
    failed_records: int = 0
    failure_rate: float = 0.0
    
    # Примеры ошибок
    sample_failures: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class LineageNode:
    """Узел lineage"""
    node_id: str
    node_type: str  # source, transform, destination
    name: str
    
    # Метаданные
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LineageEdge:
    """Ребро lineage"""
    source_id: str
    target_id: str
    
    # Тип связи
    relationship: str = "derived_from"
    
    # Метаданные
    metadata: Dict[str, Any] = field(default_factory=dict)


class DataExtractor:
    """Экстрактор данных"""
    
    def __init__(self):
        self.sources: Dict[str, DataSource] = {}
        
    def register_source(self, name: str, source_type: DataSourceType,
                         connection_config: Dict[str, Any], **kwargs) -> DataSource:
        """Регистрация источника"""
        source = DataSource(
            source_id=f"src_{uuid.uuid4().hex[:8]}",
            name=name,
            source_type=source_type,
            connection_config=connection_config,
            **kwargs
        )
        
        self.sources[name] = source
        return source
        
    async def extract(self, source_name: str, query: Dict[str, Any] = None) -> List[Dict]:
        """Извлечение данных"""
        source = self.sources.get(source_name)
        
        if not source:
            raise ValueError(f"Source {source_name} not found")
            
        # Симуляция извлечения
        await asyncio.sleep(0.1)
        
        # Генерация тестовых данных
        data = []
        for i in range(100):
            record = {
                "id": i + 1,
                "name": f"Record_{i + 1}",
                "value": (i + 1) * 10.5,
                "timestamp": datetime.now().isoformat(),
                "source": source_name
            }
            data.append(record)
            
        return data


class DataTransformer:
    """Трансформатор данных"""
    
    def __init__(self):
        self.transforms: Dict[str, Transform] = {}
        
    def register_transform(self, name: str, transform_type: TransformType,
                            config: Dict[str, Any] = None, **kwargs) -> Transform:
        """Регистрация трансформации"""
        transform = Transform(
            transform_id=f"tfm_{uuid.uuid4().hex[:8]}",
            name=name,
            transform_type=transform_type,
            config=config or {},
            **kwargs
        )
        
        self.transforms[name] = transform
        return transform
        
    async def transform(self, data: List[Dict], transform_name: str) -> List[Dict]:
        """Применение трансформации"""
        transform = self.transforms.get(transform_name)
        
        if not transform:
            raise ValueError(f"Transform {transform_name} not found")
            
        await asyncio.sleep(0.05)
        
        if transform.transform_type == TransformType.MAP:
            return self._apply_map(data, transform.config)
        elif transform.transform_type == TransformType.FILTER:
            return self._apply_filter(data, transform.config)
        elif transform.transform_type == TransformType.AGGREGATE:
            return self._apply_aggregate(data, transform.config)
            
        return data
        
    def _apply_map(self, data: List[Dict], config: Dict) -> List[Dict]:
        """Применение map"""
        mappings = config.get("mappings", {})
        
        result = []
        for record in data:
            new_record = {}
            for new_key, old_key in mappings.items():
                if old_key in record:
                    new_record[new_key] = record[old_key]
            result.append(new_record)
            
        return result
        
    def _apply_filter(self, data: List[Dict], config: Dict) -> List[Dict]:
        """Применение filter"""
        column = config.get("column", "")
        operator = config.get("operator", "eq")
        value = config.get("value")
        
        result = []
        for record in data:
            record_value = record.get(column)
            
            if operator == "eq" and record_value == value:
                result.append(record)
            elif operator == "gt" and record_value > value:
                result.append(record)
            elif operator == "lt" and record_value < value:
                result.append(record)
            elif operator == "contains" and value in str(record_value):
                result.append(record)
                
        return result
        
    def _apply_aggregate(self, data: List[Dict], config: Dict) -> List[Dict]:
        """Применение aggregate"""
        group_by = config.get("group_by", [])
        aggregations = config.get("aggregations", {})
        
        if not group_by:
            # Глобальная агрегация
            result = {}
            for agg_name, agg_config in aggregations.items():
                column = agg_config.get("column")
                func = agg_config.get("function", "sum")
                values = [r.get(column, 0) for r in data]
                
                if func == "sum":
                    result[agg_name] = sum(values)
                elif func == "avg":
                    result[agg_name] = sum(values) / len(values) if values else 0
                elif func == "count":
                    result[agg_name] = len(values)
                elif func == "min":
                    result[agg_name] = min(values) if values else 0
                elif func == "max":
                    result[agg_name] = max(values) if values else 0
                    
            return [result]
            
        # Группировка
        groups = defaultdict(list)
        for record in data:
            key = tuple(record.get(col) for col in group_by)
            groups[key].append(record)
            
        result = []
        for key, group_data in groups.items():
            row = dict(zip(group_by, key))
            
            for agg_name, agg_config in aggregations.items():
                column = agg_config.get("column")
                func = agg_config.get("function", "sum")
                values = [r.get(column, 0) for r in group_data]
                
                if func == "sum":
                    row[agg_name] = sum(values)
                elif func == "avg":
                    row[agg_name] = sum(values) / len(values) if values else 0
                elif func == "count":
                    row[agg_name] = len(values)
                    
            result.append(row)
            
        return result


class DataLoader:
    """Загрузчик данных"""
    
    def __init__(self):
        self.destinations: Dict[str, DataDestination] = {}
        self.loaded_data: Dict[str, List[Dict]] = {}  # Для демо
        
    def register_destination(self, name: str, destination_type: DataSourceType,
                               connection_config: Dict[str, Any], **kwargs) -> DataDestination:
        """Регистрация назначения"""
        destination = DataDestination(
            destination_id=f"dst_{uuid.uuid4().hex[:8]}",
            name=name,
            destination_type=destination_type,
            connection_config=connection_config,
            **kwargs
        )
        
        self.destinations[name] = destination
        return destination
        
    async def load(self, data: List[Dict], destination_name: str) -> Dict[str, Any]:
        """Загрузка данных"""
        destination = self.destinations.get(destination_name)
        
        if not destination:
            raise ValueError(f"Destination {destination_name} not found")
            
        await asyncio.sleep(0.05)
        
        # Симуляция загрузки
        if destination_name not in self.loaded_data:
            self.loaded_data[destination_name] = []
            
        if destination.write_mode == "overwrite":
            self.loaded_data[destination_name] = data
        else:
            self.loaded_data[destination_name].extend(data)
            
        return {
            "destination": destination_name,
            "records_loaded": len(data),
            "write_mode": destination.write_mode,
            "total_records": len(self.loaded_data[destination_name])
        }


class DataQualityEngine:
    """Движок качества данных"""
    
    def __init__(self):
        self.rules: Dict[str, DataQualityRule] = {}
        
    def add_rule(self, name: str, check_type: str, column: str,
                  config: Dict[str, Any] = None, **kwargs) -> DataQualityRule:
        """Добавление правила"""
        rule = DataQualityRule(
            rule_id=f"dq_{uuid.uuid4().hex[:8]}",
            name=name,
            check_type=check_type,
            column=column,
            config=config or {},
            **kwargs
        )
        
        self.rules[name] = rule
        return rule
        
    def validate(self, data: List[Dict], rule_names: List[str] = None) -> List[DataQualityResult]:
        """Валидация данных"""
        rules_to_check = []
        
        if rule_names:
            rules_to_check = [self.rules[n] for n in rule_names if n in self.rules]
        else:
            rules_to_check = [r for r in self.rules.values() if r.enabled]
            
        results = []
        
        for rule in rules_to_check:
            result = self._check_rule(data, rule)
            results.append(result)
            
        return results
        
    def _check_rule(self, data: List[Dict], rule: DataQualityRule) -> DataQualityResult:
        """Проверка одного правила"""
        failed_records = []
        
        for i, record in enumerate(data):
            value = record.get(rule.column)
            
            if not self._check_value(value, rule):
                failed_records.append({
                    "index": i,
                    "value": value,
                    "rule": rule.name
                })
                
        total = len(data)
        failed = len(failed_records)
        
        return DataQualityResult(
            rule_id=rule.rule_id,
            passed=failed == 0,
            total_records=total,
            failed_records=failed,
            failure_rate=failed / total if total > 0 else 0,
            sample_failures=failed_records[:5]
        )
        
    def _check_value(self, value: Any, rule: DataQualityRule) -> bool:
        """Проверка значения"""
        check_type = rule.check_type
        config = rule.config
        
        if check_type == "not_null":
            return value is not None
            
        elif check_type == "unique":
            # Упрощённо - для полной проверки нужен контекст всех данных
            return True
            
        elif check_type == "range":
            min_val = config.get("min")
            max_val = config.get("max")
            
            if min_val is not None and value < min_val:
                return False
            if max_val is not None and value > max_val:
                return False
            return True
            
        elif check_type == "in_set":
            valid_values = config.get("values", [])
            return value in valid_values
            
        elif check_type == "regex":
            import re
            pattern = config.get("pattern", "")
            return bool(re.match(pattern, str(value))) if value else False
            
        return True


class LineageTracker:
    """Отслеживание происхождения данных"""
    
    def __init__(self):
        self.nodes: Dict[str, LineageNode] = {}
        self.edges: List[LineageEdge] = []
        
    def add_node(self, node_id: str, node_type: str, name: str,
                  metadata: Dict[str, Any] = None) -> LineageNode:
        """Добавление узла"""
        node = LineageNode(
            node_id=node_id,
            node_type=node_type,
            name=name,
            metadata=metadata or {}
        )
        
        self.nodes[node_id] = node
        return node
        
    def add_edge(self, source_id: str, target_id: str,
                  relationship: str = "derived_from",
                  metadata: Dict[str, Any] = None):
        """Добавление связи"""
        edge = LineageEdge(
            source_id=source_id,
            target_id=target_id,
            relationship=relationship,
            metadata=metadata or {}
        )
        
        self.edges.append(edge)
        
    def get_upstream(self, node_id: str) -> List[str]:
        """Получение upstream узлов"""
        upstream = []
        
        for edge in self.edges:
            if edge.target_id == node_id:
                upstream.append(edge.source_id)
                upstream.extend(self.get_upstream(edge.source_id))
                
        return list(set(upstream))
        
    def get_downstream(self, node_id: str) -> List[str]:
        """Получение downstream узлов"""
        downstream = []
        
        for edge in self.edges:
            if edge.source_id == node_id:
                downstream.append(edge.target_id)
                downstream.extend(self.get_downstream(edge.target_id))
                
        return list(set(downstream))
        
    def get_lineage_graph(self) -> Dict[str, Any]:
        """Получение графа lineage"""
        return {
            "nodes": [
                {"id": n.node_id, "type": n.node_type, "name": n.name}
                for n in self.nodes.values()
            ],
            "edges": [
                {"source": e.source_id, "target": e.target_id, "relationship": e.relationship}
                for e in self.edges
            ]
        }


class PipelineOrchestrator:
    """Оркестратор пайплайнов"""
    
    def __init__(self):
        self.pipelines: Dict[str, Pipeline] = {}
        self.runs: Dict[str, PipelineRun] = {}
        
        self.extractor = DataExtractor()
        self.transformer = DataTransformer()
        self.loader = DataLoader()
        self.quality_engine = DataQualityEngine()
        self.lineage_tracker = LineageTracker()
        
    def create_pipeline(self, name: str, tasks: List[Dict[str, Any]],
                         **kwargs) -> Pipeline:
        """Создание пайплайна"""
        task_objects = []
        
        for task_config in tasks:
            task = Task(
                task_id=f"task_{uuid.uuid4().hex[:8]}",
                name=task_config.get("name", ""),
                task_type=task_config.get("type", "transform"),
                config=task_config.get("config", {}),
                depends_on=task_config.get("depends_on", [])
            )
            task_objects.append(task)
            
        pipeline = Pipeline(
            pipeline_id=f"pipe_{uuid.uuid4().hex[:8]}",
            name=name,
            tasks=task_objects,
            **kwargs
        )
        
        self.pipelines[name] = pipeline
        return pipeline
        
    async def run_pipeline(self, pipeline_name: str,
                            parameters: Dict[str, Any] = None) -> PipelineRun:
        """Запуск пайплайна"""
        pipeline = self.pipelines.get(pipeline_name)
        
        if not pipeline:
            raise ValueError(f"Pipeline {pipeline_name} not found")
            
        run = PipelineRun(
            run_id=f"run_{uuid.uuid4().hex[:8]}",
            pipeline_id=pipeline.pipeline_id,
            parameters=parameters or {}
        )
        
        pipeline.status = PipelineStatus.RUNNING
        self.runs[run.run_id] = run
        
        # Выполняем задачи в порядке зависимостей
        task_results: Dict[str, Any] = {}
        
        try:
            for task in self._get_execution_order(pipeline.tasks):
                # Проверяем зависимости
                deps_ok = all(
                    run.task_runs.get(dep, {}).get("status") == TaskStatus.SUCCESS.value
                    for dep in task.depends_on
                )
                
                if not deps_ok:
                    task.status = TaskStatus.UPSTREAM_FAILED
                    run.task_runs[task.task_id] = {
                        "status": TaskStatus.UPSTREAM_FAILED.value,
                        "error": "Upstream task failed"
                    }
                    continue
                    
                # Выполняем задачу
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.now()
                
                try:
                    result = await self._execute_task(task, task_results, parameters or {})
                    task_results[task.task_id] = result
                    
                    task.status = TaskStatus.SUCCESS
                    task.output = result
                    run.records_processed += len(result) if isinstance(result, list) else 1
                    
                    run.task_runs[task.task_id] = {
                        "status": TaskStatus.SUCCESS.value,
                        "records": len(result) if isinstance(result, list) else 1
                    }
                    
                except Exception as e:
                    task.status = TaskStatus.FAILED
                    task.error = str(e)
                    
                    run.task_runs[task.task_id] = {
                        "status": TaskStatus.FAILED.value,
                        "error": str(e)
                    }
                    
                task.completed_at = datetime.now()
                
            # Определяем итоговый статус
            failed_tasks = [t for t in pipeline.tasks if t.status == TaskStatus.FAILED]
            
            if failed_tasks:
                run.status = PipelineStatus.FAILED
                pipeline.status = PipelineStatus.FAILED
                pipeline.failed_runs += 1
            else:
                run.status = PipelineStatus.SUCCESS
                pipeline.status = PipelineStatus.SUCCESS
                pipeline.successful_runs += 1
                
        except Exception as e:
            run.status = PipelineStatus.FAILED
            pipeline.status = PipelineStatus.FAILED
            pipeline.failed_runs += 1
            
        run.completed_at = datetime.now()
        pipeline.total_runs += 1
        pipeline.last_run = datetime.now()
        
        return run
        
    def _get_execution_order(self, tasks: List[Task]) -> List[Task]:
        """Топологическая сортировка задач"""
        task_map = {t.task_id: t for t in tasks}
        task_name_map = {t.name: t.task_id for t in tasks}
        
        visited = set()
        order = []
        
        def visit(task_id: str):
            if task_id in visited:
                return
            visited.add(task_id)
            
            task = task_map.get(task_id)
            if task:
                for dep_name in task.depends_on:
                    dep_id = task_name_map.get(dep_name)
                    if dep_id:
                        visit(dep_id)
                order.append(task)
                
        for task in tasks:
            visit(task.task_id)
            
        return order
        
    async def _execute_task(self, task: Task, previous_results: Dict[str, Any],
                             parameters: Dict[str, Any]) -> Any:
        """Выполнение задачи"""
        task_type = task.task_type
        config = task.config
        
        if task_type == "extract":
            source = config.get("source")
            return await self.extractor.extract(source, config.get("query"))
            
        elif task_type == "transform":
            # Получаем данные из предыдущей задачи
            input_task = config.get("input")
            input_task_id = None
            
            for tid, t in previous_results.items():
                # Ищем по имени задачи
                pass
                
            # Берём последний результат если не указан input
            data = list(previous_results.values())[-1] if previous_results else []
            
            transform_name = config.get("transform")
            return await self.transformer.transform(data, transform_name)
            
        elif task_type == "load":
            data = list(previous_results.values())[-1] if previous_results else []
            destination = config.get("destination")
            result = await self.loader.load(data, destination)
            return [result]
            
        elif task_type == "quality_check":
            data = list(previous_results.values())[-1] if previous_results else []
            rules = config.get("rules", [])
            return self.quality_engine.validate(data, rules)
            
        return []
        
    def get_stats(self) -> Dict[str, Any]:
        """Статистика"""
        return {
            "pipelines": len(self.pipelines),
            "total_runs": sum(p.total_runs for p in self.pipelines.values()),
            "successful_runs": sum(p.successful_runs for p in self.pipelines.values()),
            "failed_runs": sum(p.failed_runs for p in self.pipelines.values()),
            "sources": len(self.extractor.sources),
            "destinations": len(self.loader.destinations),
            "transforms": len(self.transformer.transforms),
            "quality_rules": len(self.quality_engine.rules)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 62: Data Pipeline & ETL Platform")
    print("=" * 60)
    
    async def demo():
        # Создание оркестратора
        orchestrator = PipelineOrchestrator()
        print("✓ Pipeline Orchestrator created")
        
        # Регистрация источников
        print("\n📥 Registering data sources...")
        
        orchestrator.extractor.register_source(
            name="sales_db",
            source_type=DataSourceType.DATABASE,
            connection_config={
                "host": "localhost",
                "port": 5432,
                "database": "sales"
            },
            schema={
                "id": "integer",
                "product": "string",
                "amount": "decimal",
                "date": "timestamp"
            }
        )
        print("  ✓ Source: sales_db")
        
        orchestrator.extractor.register_source(
            name="user_api",
            source_type=DataSourceType.API,
            connection_config={
                "url": "https://api.example.com/users",
                "auth": "bearer"
            }
        )
        print("  ✓ Source: user_api")
        
        # Регистрация трансформаций
        print("\n🔄 Registering transforms...")
        
        orchestrator.transformer.register_transform(
            name="map_sales",
            transform_type=TransformType.MAP,
            config={
                "mappings": {
                    "record_id": "id",
                    "record_name": "name",
                    "amount": "value"
                }
            }
        )
        print("  ✓ Transform: map_sales")
        
        orchestrator.transformer.register_transform(
            name="filter_high_value",
            transform_type=TransformType.FILTER,
            config={
                "column": "value",
                "operator": "gt",
                "value": 500
            }
        )
        print("  ✓ Transform: filter_high_value")
        
        orchestrator.transformer.register_transform(
            name="aggregate_by_source",
            transform_type=TransformType.AGGREGATE,
            config={
                "group_by": ["source"],
                "aggregations": {
                    "total_amount": {"column": "amount", "function": "sum"},
                    "record_count": {"column": "id", "function": "count"}
                }
            }
        )
        print("  ✓ Transform: aggregate_by_source")
        
        # Регистрация назначений
        print("\n📤 Registering destinations...")
        
        orchestrator.loader.register_destination(
            name="data_warehouse",
            destination_type=DataSourceType.DATABASE,
            connection_config={
                "host": "dw.example.com",
                "port": 5432,
                "database": "warehouse"
            },
            write_mode="append"
        )
        print("  ✓ Destination: data_warehouse")
        
        # Правила качества данных
        print("\n✅ Adding data quality rules...")
        
        orchestrator.quality_engine.add_rule(
            name="id_not_null",
            check_type="not_null",
            column="id",
            severity="error"
        )
        print("  ✓ Rule: id_not_null")
        
        orchestrator.quality_engine.add_rule(
            name="value_in_range",
            check_type="range",
            column="value",
            config={"min": 0, "max": 10000},
            severity="warning"
        )
        print("  ✓ Rule: value_in_range")
        
        # Создание пайплайна
        print("\n📊 Creating pipeline...")
        
        pipeline = orchestrator.create_pipeline(
            name="sales_etl",
            description="Sales data ETL pipeline",
            tasks=[
                {
                    "name": "extract_sales",
                    "type": "extract",
                    "config": {"source": "sales_db"}
                },
                {
                    "name": "map_fields",
                    "type": "transform",
                    "config": {"transform": "map_sales"},
                    "depends_on": ["extract_sales"]
                },
                {
                    "name": "filter_data",
                    "type": "transform",
                    "config": {"transform": "filter_high_value"},
                    "depends_on": ["map_fields"]
                },
                {
                    "name": "quality_check",
                    "type": "quality_check",
                    "config": {"rules": ["id_not_null", "value_in_range"]},
                    "depends_on": ["filter_data"]
                },
                {
                    "name": "load_warehouse",
                    "type": "load",
                    "config": {"destination": "data_warehouse"},
                    "depends_on": ["quality_check"]
                }
            ]
        )
        print(f"  ✓ Pipeline: {pipeline.name}")
        print(f"  Tasks: {len(pipeline.tasks)}")
        
        # Запуск пайплайна
        print("\n🚀 Running pipeline...")
        
        run = await orchestrator.run_pipeline("sales_etl")
        
        print(f"  Run ID: {run.run_id}")
        print(f"  Status: {run.status.value}")
        print(f"  Records processed: {run.records_processed}")
        
        # Результаты задач
        print("\n  Task results:")
        for task_id, result in run.task_runs.items():
            status = result.get("status")
            records = result.get("records", "-")
            print(f"    {task_id[:12]}...: {status} ({records} records)")
            
        # Lineage tracking
        print("\n🔗 Data Lineage...")
        
        orchestrator.lineage_tracker.add_node("sales_db", "source", "Sales Database")
        orchestrator.lineage_tracker.add_node("map_sales", "transform", "Field Mapping")
        orchestrator.lineage_tracker.add_node("filter_high", "transform", "High Value Filter")
        orchestrator.lineage_tracker.add_node("data_warehouse", "destination", "Data Warehouse")
        
        orchestrator.lineage_tracker.add_edge("sales_db", "map_sales")
        orchestrator.lineage_tracker.add_edge("map_sales", "filter_high")
        orchestrator.lineage_tracker.add_edge("filter_high", "data_warehouse")
        
        lineage = orchestrator.lineage_tracker.get_lineage_graph()
        print(f"  Nodes: {len(lineage['nodes'])}")
        print(f"  Edges: {len(lineage['edges'])}")
        
        # Upstream/downstream
        upstream = orchestrator.lineage_tracker.get_upstream("data_warehouse")
        print(f"  Upstream of data_warehouse: {upstream}")
        
        # Второй запуск
        print("\n🔄 Running pipeline again...")
        
        run2 = await orchestrator.run_pipeline("sales_etl")
        print(f"  Run 2 Status: {run2.status.value}")
        
        # Статистика
        print("\n📈 Platform Statistics:")
        stats = orchestrator.get_stats()
        print(f"  Pipelines: {stats['pipelines']}")
        print(f"  Total runs: {stats['total_runs']}")
        print(f"  Successful: {stats['successful_runs']}")
        print(f"  Failed: {stats['failed_runs']}")
        print(f"  Sources: {stats['sources']}")
        print(f"  Destinations: {stats['destinations']}")
        print(f"  Transforms: {stats['transforms']}")
        print(f"  Quality rules: {stats['quality_rules']}")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Data Pipeline & ETL Platform initialized!")
    print("=" * 60)
