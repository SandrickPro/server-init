#!/usr/bin/env python3
"""
Server Init - Iteration 351: ETL Platform
Платформа ETL (Extract, Transform, Load)

Функционал:
- Data Sources - источники данных
- Data Extractors - экстракторы данных
- Data Transformers - трансформеры данных
- Data Loaders - загрузчики данных
- ETL Pipelines - конвейеры ETL
- Data Quality - качество данных
- Schema Management - управление схемами
- ETL Monitoring - мониторинг ETL
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import json


class SourceType(Enum):
    """Тип источника"""
    DATABASE = "database"
    FILE = "file"
    API = "api"
    STREAM = "stream"
    CLOUD_STORAGE = "cloud_storage"
    MESSAGE_QUEUE = "message_queue"


class DatabaseType(Enum):
    """Тип базы данных"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    ORACLE = "oracle"
    SQLSERVER = "sqlserver"
    MONGODB = "mongodb"
    ELASTICSEARCH = "elasticsearch"


class FileFormat(Enum):
    """Формат файла"""
    CSV = "csv"
    JSON = "json"
    PARQUET = "parquet"
    AVRO = "avro"
    ORC = "orc"
    XML = "xml"


class TransformationType(Enum):
    """Тип трансформации"""
    MAP = "map"
    FILTER = "filter"
    AGGREGATE = "aggregate"
    JOIN = "join"
    UNION = "union"
    PIVOT = "pivot"
    UNPIVOT = "unpivot"
    DEDUPLICATE = "deduplicate"


class PipelineStatus(Enum):
    """Статус конвейера"""
    DRAFT = "draft"
    ACTIVE = "active"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionStatus(Enum):
    """Статус выполнения"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class QualityRuleType(Enum):
    """Тип правила качества"""
    NOT_NULL = "not_null"
    UNIQUE = "unique"
    RANGE = "range"
    REGEX = "regex"
    CUSTOM = "custom"
    REFERENTIAL = "referential"


class LoadMode(Enum):
    """Режим загрузки"""
    APPEND = "append"
    OVERWRITE = "overwrite"
    UPSERT = "upsert"
    MERGE = "merge"


@dataclass
class DataSource:
    """Источник данных"""
    source_id: str
    name: str
    
    # Type
    source_type: SourceType = SourceType.DATABASE
    
    # Connection
    connection_string: str = ""
    credentials: Dict[str, str] = field(default_factory=dict)
    
    # Database
    database_type: DatabaseType = DatabaseType.POSTGRESQL
    database_name: str = ""
    schema_name: str = ""
    
    # File
    file_format: FileFormat = FileFormat.CSV
    file_path: str = ""
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    is_active: bool = True
    last_connected: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DataTarget:
    """Цель данных"""
    target_id: str
    name: str
    
    # Type
    target_type: SourceType = SourceType.DATABASE
    
    # Connection
    connection_string: str = ""
    credentials: Dict[str, str] = field(default_factory=dict)
    
    # Database
    database_type: DatabaseType = DatabaseType.POSTGRESQL
    database_name: str = ""
    schema_name: str = ""
    table_name: str = ""
    
    # File
    file_format: FileFormat = FileFormat.PARQUET
    file_path: str = ""
    
    # Load mode
    load_mode: LoadMode = LoadMode.APPEND
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Schema:
    """Схема данных"""
    schema_id: str
    name: str
    
    # Fields
    fields: List[Dict[str, Any]] = field(default_factory=list)
    
    # Primary key
    primary_key: List[str] = field(default_factory=list)
    
    # Version
    version: int = 1
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Extractor:
    """Экстрактор данных"""
    extractor_id: str
    name: str
    source_id: str
    
    # Query
    query: str = ""
    
    # Incremental
    is_incremental: bool = False
    incremental_column: str = ""
    last_value: Any = None
    
    # Batch
    batch_size: int = 10000
    
    # Schema
    schema_id: str = ""
    
    # Stats
    rows_extracted: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Transformer:
    """Трансформер данных"""
    transformer_id: str
    name: str
    
    # Type
    transform_type: TransformationType = TransformationType.MAP
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Expression
    expression: str = ""
    
    # Input/Output schema
    input_schema_id: str = ""
    output_schema_id: str = ""
    
    # Order
    order: int = 0
    
    # Stats
    rows_processed: int = 0
    rows_filtered: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Loader:
    """Загрузчик данных"""
    loader_id: str
    name: str
    target_id: str
    
    # Mode
    load_mode: LoadMode = LoadMode.APPEND
    
    # Batch
    batch_size: int = 10000
    commit_interval: int = 1000
    
    # Key columns for upsert/merge
    key_columns: List[str] = field(default_factory=list)
    
    # Schema
    schema_id: str = ""
    
    # Stats
    rows_loaded: int = 0
    rows_updated: int = 0
    rows_deleted: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Pipeline:
    """Конвейер ETL"""
    pipeline_id: str
    name: str
    description: str = ""
    
    # Components
    extractor_ids: List[str] = field(default_factory=list)
    transformer_ids: List[str] = field(default_factory=list)
    loader_ids: List[str] = field(default_factory=list)
    
    # Status
    status: PipelineStatus = PipelineStatus.DRAFT
    
    # Schedule
    cron_expression: str = ""
    is_scheduled: bool = False
    
    # Configuration
    parallelism: int = 1
    retry_count: int = 3
    timeout_seconds: int = 3600
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    last_run: Optional[datetime] = None


@dataclass
class PipelineExecution:
    """Выполнение конвейера"""
    execution_id: str
    pipeline_id: str
    
    # Status
    status: ExecutionStatus = ExecutionStatus.PENDING
    
    # Stats
    rows_extracted: int = 0
    rows_transformed: int = 0
    rows_loaded: int = 0
    rows_rejected: int = 0
    
    # Duration
    duration_seconds: float = 0.0
    
    # Error
    error_message: str = ""
    
    # Timestamps
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class QualityRule:
    """Правило качества"""
    rule_id: str
    name: str
    
    # Type
    rule_type: QualityRuleType = QualityRuleType.NOT_NULL
    
    # Target
    schema_id: str = ""
    field_name: str = ""
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Threshold
    threshold_percent: float = 100.0
    
    # Action
    fail_on_violation: bool = True
    
    # Status
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class QualityCheck:
    """Проверка качества"""
    check_id: str
    execution_id: str
    rule_id: str
    
    # Results
    total_rows: int = 0
    passed_rows: int = 0
    failed_rows: int = 0
    pass_rate: float = 0.0
    
    # Status
    is_passed: bool = True
    
    # Details
    failed_samples: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timestamps
    checked_at: datetime = field(default_factory=datetime.now)


@dataclass
class DataLineage:
    """Линия данных"""
    lineage_id: str
    
    # Source
    source_type: str = ""  # source, transformer, pipeline
    source_id: str = ""
    
    # Target
    target_type: str = ""
    target_id: str = ""
    
    # Fields
    field_mappings: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ETLMetrics:
    """Метрики ETL"""
    metrics_id: str
    pipeline_id: str
    
    # Executions
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    
    # Rows
    total_rows_extracted: int = 0
    total_rows_loaded: int = 0
    total_rows_rejected: int = 0
    
    # Duration
    avg_duration_seconds: float = 0.0
    
    # Throughput
    avg_rows_per_second: float = 0.0
    
    # Quality
    avg_quality_score: float = 0.0
    
    # Timestamps
    collected_at: datetime = field(default_factory=datetime.now)


class ETLPlatform:
    """Платформа ETL"""
    
    def __init__(self):
        self.sources: Dict[str, DataSource] = {}
        self.targets: Dict[str, DataTarget] = {}
        self.schemas: Dict[str, Schema] = {}
        self.extractors: Dict[str, Extractor] = {}
        self.transformers: Dict[str, Transformer] = {}
        self.loaders: Dict[str, Loader] = {}
        self.pipelines: Dict[str, Pipeline] = {}
        self.executions: Dict[str, PipelineExecution] = {}
        self.quality_rules: Dict[str, QualityRule] = {}
        self.quality_checks: Dict[str, QualityCheck] = {}
        self.lineages: Dict[str, DataLineage] = {}
        self.metrics: Dict[str, ETLMetrics] = {}
        
    async def create_source(self, name: str,
                           source_type: SourceType = SourceType.DATABASE,
                           connection_string: str = "",
                           database_type: DatabaseType = DatabaseType.POSTGRESQL,
                           database_name: str = "",
                           schema_name: str = "",
                           file_format: FileFormat = FileFormat.CSV,
                           file_path: str = "",
                           config: Dict[str, Any] = None) -> DataSource:
        """Создание источника данных"""
        source = DataSource(
            source_id=f"src_{uuid.uuid4().hex[:8]}",
            name=name,
            source_type=source_type,
            connection_string=connection_string,
            database_type=database_type,
            database_name=database_name,
            schema_name=schema_name,
            file_format=file_format,
            file_path=file_path,
            config=config or {}
        )
        
        self.sources[source.source_id] = source
        return source
        
    async def create_target(self, name: str,
                           target_type: SourceType = SourceType.DATABASE,
                           connection_string: str = "",
                           database_type: DatabaseType = DatabaseType.POSTGRESQL,
                           database_name: str = "",
                           schema_name: str = "",
                           table_name: str = "",
                           file_format: FileFormat = FileFormat.PARQUET,
                           file_path: str = "",
                           load_mode: LoadMode = LoadMode.APPEND,
                           config: Dict[str, Any] = None) -> DataTarget:
        """Создание цели данных"""
        target = DataTarget(
            target_id=f"tgt_{uuid.uuid4().hex[:8]}",
            name=name,
            target_type=target_type,
            connection_string=connection_string,
            database_type=database_type,
            database_name=database_name,
            schema_name=schema_name,
            table_name=table_name,
            file_format=file_format,
            file_path=file_path,
            load_mode=load_mode,
            config=config or {}
        )
        
        self.targets[target.target_id] = target
        return target
        
    async def create_schema(self, name: str,
                           fields: List[Dict[str, Any]],
                           primary_key: List[str] = None) -> Schema:
        """Создание схемы"""
        schema = Schema(
            schema_id=f"sch_{uuid.uuid4().hex[:8]}",
            name=name,
            fields=fields,
            primary_key=primary_key or []
        )
        
        self.schemas[schema.schema_id] = schema
        return schema
        
    async def create_extractor(self, name: str,
                              source_id: str,
                              query: str = "",
                              is_incremental: bool = False,
                              incremental_column: str = "",
                              batch_size: int = 10000,
                              schema_id: str = "") -> Optional[Extractor]:
        """Создание экстрактора"""
        source = self.sources.get(source_id)
        if not source:
            return None
            
        extractor = Extractor(
            extractor_id=f"ext_{uuid.uuid4().hex[:8]}",
            name=name,
            source_id=source_id,
            query=query,
            is_incremental=is_incremental,
            incremental_column=incremental_column,
            batch_size=batch_size,
            schema_id=schema_id
        )
        
        self.extractors[extractor.extractor_id] = extractor
        return extractor
        
    async def create_transformer(self, name: str,
                                transform_type: TransformationType = TransformationType.MAP,
                                config: Dict[str, Any] = None,
                                expression: str = "",
                                order: int = 0) -> Transformer:
        """Создание трансформера"""
        transformer = Transformer(
            transformer_id=f"trx_{uuid.uuid4().hex[:8]}",
            name=name,
            transform_type=transform_type,
            config=config or {},
            expression=expression,
            order=order
        )
        
        self.transformers[transformer.transformer_id] = transformer
        return transformer
        
    async def create_loader(self, name: str,
                           target_id: str,
                           load_mode: LoadMode = LoadMode.APPEND,
                           batch_size: int = 10000,
                           key_columns: List[str] = None,
                           schema_id: str = "") -> Optional[Loader]:
        """Создание загрузчика"""
        target = self.targets.get(target_id)
        if not target:
            return None
            
        loader = Loader(
            loader_id=f"ldr_{uuid.uuid4().hex[:8]}",
            name=name,
            target_id=target_id,
            load_mode=load_mode,
            batch_size=batch_size,
            key_columns=key_columns or [],
            schema_id=schema_id
        )
        
        self.loaders[loader.loader_id] = loader
        return loader
        
    async def create_pipeline(self, name: str,
                             description: str = "",
                             extractor_ids: List[str] = None,
                             transformer_ids: List[str] = None,
                             loader_ids: List[str] = None,
                             cron_expression: str = "",
                             parallelism: int = 1,
                             tags: List[str] = None) -> Pipeline:
        """Создание конвейера"""
        pipeline = Pipeline(
            pipeline_id=f"pipe_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            extractor_ids=extractor_ids or [],
            transformer_ids=transformer_ids or [],
            loader_ids=loader_ids or [],
            cron_expression=cron_expression,
            is_scheduled=bool(cron_expression),
            parallelism=parallelism,
            tags=tags or []
        )
        
        self.pipelines[pipeline.pipeline_id] = pipeline
        return pipeline
        
    async def add_quality_rule(self, name: str,
                              schema_id: str,
                              field_name: str,
                              rule_type: QualityRuleType = QualityRuleType.NOT_NULL,
                              config: Dict[str, Any] = None,
                              threshold_percent: float = 100.0,
                              fail_on_violation: bool = True) -> QualityRule:
        """Добавление правила качества"""
        rule = QualityRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name=name,
            rule_type=rule_type,
            schema_id=schema_id,
            field_name=field_name,
            config=config or {},
            threshold_percent=threshold_percent,
            fail_on_violation=fail_on_violation
        )
        
        self.quality_rules[rule.rule_id] = rule
        return rule
        
    async def run_pipeline(self, pipeline_id: str) -> Optional[PipelineExecution]:
        """Запуск конвейера"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            return None
            
        execution = PipelineExecution(
            execution_id=f"exec_{uuid.uuid4().hex[:12]}",
            pipeline_id=pipeline_id,
            status=ExecutionStatus.RUNNING
        )
        
        self.executions[execution.execution_id] = execution
        
        pipeline.status = PipelineStatus.RUNNING
        pipeline.last_run = datetime.now()
        
        # Execute pipeline
        await self._execute_pipeline(execution, pipeline)
        
        return execution
        
    async def _execute_pipeline(self, execution: PipelineExecution,
                               pipeline: Pipeline):
        """Выполнение конвейера"""
        start_time = datetime.now()
        
        try:
            # Extract
            for ext_id in pipeline.extractor_ids:
                extractor = self.extractors.get(ext_id)
                if extractor:
                    rows = await self._execute_extract(extractor)
                    execution.rows_extracted += rows
                    
            # Transform
            for trx_id in pipeline.transformer_ids:
                transformer = self.transformers.get(trx_id)
                if transformer:
                    rows = await self._execute_transform(transformer, execution.rows_extracted)
                    execution.rows_transformed = rows
                    
            # Load
            for ldr_id in pipeline.loader_ids:
                loader = self.loaders.get(ldr_id)
                if loader:
                    rows = await self._execute_load(loader, execution.rows_transformed or execution.rows_extracted)
                    execution.rows_loaded += rows
                    
            # Run quality checks
            await self._run_quality_checks(execution)
            
            execution.status = ExecutionStatus.SUCCESS
            pipeline.status = PipelineStatus.COMPLETED
            
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error_message = str(e)
            pipeline.status = PipelineStatus.FAILED
            
        execution.completed_at = datetime.now()
        execution.duration_seconds = (execution.completed_at - start_time).total_seconds()
        
        pipeline.updated_at = datetime.now()
        
    async def _execute_extract(self, extractor: Extractor) -> int:
        """Выполнение экстракции"""
        # Simulate extraction
        rows = random.randint(1000, 100000)
        extractor.rows_extracted += rows
        
        if extractor.is_incremental:
            extractor.last_value = datetime.now().isoformat()
            
        return rows
        
    async def _execute_transform(self, transformer: Transformer, input_rows: int) -> int:
        """Выполнение трансформации"""
        # Simulate transformation
        output_rows = input_rows
        
        if transformer.transform_type == TransformationType.FILTER:
            filter_rate = random.uniform(0.1, 0.3)
            output_rows = int(input_rows * (1 - filter_rate))
            transformer.rows_filtered += int(input_rows * filter_rate)
        elif transformer.transform_type == TransformationType.DEDUPLICATE:
            dedup_rate = random.uniform(0.01, 0.1)
            output_rows = int(input_rows * (1 - dedup_rate))
            
        transformer.rows_processed += output_rows
        return output_rows
        
    async def _execute_load(self, loader: Loader, input_rows: int) -> int:
        """Выполнение загрузки"""
        # Simulate loading
        if loader.load_mode == LoadMode.UPSERT:
            loader.rows_updated = random.randint(0, input_rows // 10)
            loader.rows_loaded = input_rows - loader.rows_updated
        elif loader.load_mode == LoadMode.MERGE:
            loader.rows_updated = random.randint(0, input_rows // 5)
            loader.rows_deleted = random.randint(0, input_rows // 20)
            loader.rows_loaded = input_rows - loader.rows_updated
        else:
            loader.rows_loaded = input_rows
            
        return input_rows
        
    async def _run_quality_checks(self, execution: PipelineExecution):
        """Выполнение проверок качества"""
        for rule in self.quality_rules.values():
            if not rule.is_active:
                continue
                
            check = QualityCheck(
                check_id=f"chk_{uuid.uuid4().hex[:8]}",
                execution_id=execution.execution_id,
                rule_id=rule.rule_id,
                total_rows=execution.rows_loaded
            )
            
            # Simulate check
            pass_rate = random.uniform(0.9, 1.0)
            check.passed_rows = int(check.total_rows * pass_rate)
            check.failed_rows = check.total_rows - check.passed_rows
            check.pass_rate = pass_rate * 100
            check.is_passed = check.pass_rate >= rule.threshold_percent
            
            if not check.is_passed:
                execution.rows_rejected += check.failed_rows
                
            self.quality_checks[check.check_id] = check
            
    async def add_lineage(self, source_type: str,
                         source_id: str,
                         target_type: str,
                         target_id: str,
                         field_mappings: Dict[str, str] = None) -> DataLineage:
        """Добавление линии данных"""
        lineage = DataLineage(
            lineage_id=f"lin_{uuid.uuid4().hex[:8]}",
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            target_id=target_id,
            field_mappings=field_mappings or {}
        )
        
        self.lineages[lineage.lineage_id] = lineage
        return lineage
        
    async def activate_pipeline(self, pipeline_id: str) -> bool:
        """Активация конвейера"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            return False
            
        pipeline.status = PipelineStatus.ACTIVE
        return True
        
    async def pause_pipeline(self, pipeline_id: str) -> bool:
        """Приостановка конвейера"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            return False
            
        pipeline.status = PipelineStatus.PAUSED
        return True
        
    async def collect_metrics(self, pipeline_id: str) -> Optional[ETLMetrics]:
        """Сбор метрик"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            return None
            
        executions = [e for e in self.executions.values() if e.pipeline_id == pipeline_id]
        
        metrics = ETLMetrics(
            metrics_id=f"met_{uuid.uuid4().hex[:8]}",
            pipeline_id=pipeline_id,
            total_executions=len(executions),
            successful_executions=sum(1 for e in executions if e.status == ExecutionStatus.SUCCESS),
            failed_executions=sum(1 for e in executions if e.status == ExecutionStatus.FAILED),
            total_rows_extracted=sum(e.rows_extracted for e in executions),
            total_rows_loaded=sum(e.rows_loaded for e in executions),
            total_rows_rejected=sum(e.rows_rejected for e in executions)
        )
        
        # Calculate averages
        completed = [e for e in executions if e.completed_at]
        if completed:
            metrics.avg_duration_seconds = sum(e.duration_seconds for e in completed) / len(completed)
            total_time = sum(e.duration_seconds for e in completed)
            if total_time > 0:
                metrics.avg_rows_per_second = metrics.total_rows_loaded / total_time
                
        # Quality score
        checks = [c for c in self.quality_checks.values() if c.execution_id in [e.execution_id for e in executions]]
        if checks:
            metrics.avg_quality_score = sum(c.pass_rate for c in checks) / len(checks)
            
        self.metrics[metrics.metrics_id] = metrics
        return metrics
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_sources = len(self.sources)
        active_sources = sum(1 for s in self.sources.values() if s.is_active)
        
        total_targets = len(self.targets)
        active_targets = sum(1 for t in self.targets.values() if t.is_active)
        
        total_pipelines = len(self.pipelines)
        active_pipelines = sum(1 for p in self.pipelines.values() if p.status == PipelineStatus.ACTIVE)
        running_pipelines = sum(1 for p in self.pipelines.values() if p.status == PipelineStatus.RUNNING)
        
        total_executions = len(self.executions)
        success_executions = sum(1 for e in self.executions.values() if e.status == ExecutionStatus.SUCCESS)
        failed_executions = sum(1 for e in self.executions.values() if e.status == ExecutionStatus.FAILED)
        
        total_rows_extracted = sum(e.rows_extracted for e in self.executions.values())
        total_rows_loaded = sum(e.rows_loaded for e in self.executions.values())
        
        total_quality_rules = len(self.quality_rules)
        active_quality_rules = sum(1 for r in self.quality_rules.values() if r.is_active)
        
        return {
            "total_sources": total_sources,
            "active_sources": active_sources,
            "total_targets": total_targets,
            "active_targets": active_targets,
            "total_pipelines": total_pipelines,
            "active_pipelines": active_pipelines,
            "running_pipelines": running_pipelines,
            "total_executions": total_executions,
            "success_executions": success_executions,
            "failed_executions": failed_executions,
            "total_rows_extracted": total_rows_extracted,
            "total_rows_loaded": total_rows_loaded,
            "total_quality_rules": total_quality_rules,
            "active_quality_rules": active_quality_rules
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 351: ETL Platform")
    print("=" * 60)
    
    platform = ETLPlatform()
    print("✓ ETL Platform initialized")
    
    # Create Data Sources
    print("\n📥 Creating Data Sources...")
    
    sources_data = [
        ("PostgreSQL Orders", SourceType.DATABASE, "postgresql://db:5432/orders", DatabaseType.POSTGRESQL, "orders_db", "public", FileFormat.CSV, ""),
        ("MySQL Users", SourceType.DATABASE, "mysql://db:3306/users", DatabaseType.MYSQL, "users_db", "main", FileFormat.CSV, ""),
        ("MongoDB Events", SourceType.DATABASE, "mongodb://db:27017/events", DatabaseType.MONGODB, "events_db", "", FileFormat.JSON, ""),
        ("CSV Products", SourceType.FILE, "", DatabaseType.POSTGRESQL, "", "", FileFormat.CSV, "/data/products.csv"),
        ("S3 Logs", SourceType.CLOUD_STORAGE, "s3://data-bucket/logs", DatabaseType.POSTGRESQL, "", "", FileFormat.JSON, "s3://bucket/logs/"),
        ("Kafka Stream", SourceType.STREAM, "kafka://broker:9092", DatabaseType.POSTGRESQL, "", "", FileFormat.AVRO, "")
    ]
    
    sources = []
    for name, stype, conn, dbtype, dbname, schema, fformat, fpath in sources_data:
        s = await platform.create_source(name, stype, conn, dbtype, dbname, schema, fformat, fpath)
        sources.append(s)
        print(f"  📥 {name} ({stype.value})")
        
    # Create Data Targets
    print("\n📤 Creating Data Targets...")
    
    targets_data = [
        ("Data Warehouse", SourceType.DATABASE, "postgresql://dw:5432/warehouse", DatabaseType.POSTGRESQL, "warehouse", "analytics", "fact_orders", FileFormat.PARQUET, "", LoadMode.UPSERT),
        ("Elasticsearch Index", SourceType.DATABASE, "http://es:9200", DatabaseType.ELASTICSEARCH, "analytics", "", "orders", FileFormat.JSON, "", LoadMode.APPEND),
        ("S3 Data Lake", SourceType.CLOUD_STORAGE, "s3://data-lake/processed", DatabaseType.POSTGRESQL, "", "", "", FileFormat.PARQUET, "s3://lake/data/", LoadMode.APPEND),
        ("Parquet Archive", SourceType.FILE, "", DatabaseType.POSTGRESQL, "", "", "", FileFormat.PARQUET, "/archive/data.parquet", LoadMode.OVERWRITE),
        ("Kafka Output", SourceType.MESSAGE_QUEUE, "kafka://broker:9092", DatabaseType.POSTGRESQL, "", "", "", FileFormat.AVRO, "", LoadMode.APPEND)
    ]
    
    targets = []
    for name, ttype, conn, dbtype, dbname, schema, table, fformat, fpath, mode in targets_data:
        t = await platform.create_target(name, ttype, conn, dbtype, dbname, schema, table, fformat, fpath, mode)
        targets.append(t)
        print(f"  📤 {name} ({mode.value})")
        
    # Create Schemas
    print("\n📋 Creating Schemas...")
    
    schemas_data = [
        ("orders_schema", [
            {"name": "id", "type": "integer", "nullable": False},
            {"name": "customer_id", "type": "integer", "nullable": False},
            {"name": "amount", "type": "decimal", "nullable": False},
            {"name": "status", "type": "string", "nullable": False},
            {"name": "created_at", "type": "timestamp", "nullable": False}
        ], ["id"]),
        ("users_schema", [
            {"name": "id", "type": "integer", "nullable": False},
            {"name": "email", "type": "string", "nullable": False},
            {"name": "name", "type": "string", "nullable": True},
            {"name": "created_at", "type": "timestamp", "nullable": False}
        ], ["id"]),
        ("events_schema", [
            {"name": "event_id", "type": "string", "nullable": False},
            {"name": "event_type", "type": "string", "nullable": False},
            {"name": "payload", "type": "json", "nullable": True},
            {"name": "timestamp", "type": "timestamp", "nullable": False}
        ], ["event_id"])
    ]
    
    schemas = []
    for name, fields, pk in schemas_data:
        s = await platform.create_schema(name, fields, pk)
        schemas.append(s)
        print(f"  📋 {name} ({len(fields)} fields)")
        
    # Create Extractors
    print("\n📖 Creating Extractors...")
    
    extractors_data = [
        ("orders_extractor", sources[0].source_id, "SELECT * FROM orders WHERE updated_at > :last_value", True, "updated_at", 10000),
        ("users_extractor", sources[1].source_id, "SELECT * FROM users", False, "", 5000),
        ("events_extractor", sources[2].source_id, "{'timestamp': {'$gte': ISODate(:last_value)}}", True, "timestamp", 20000),
        ("products_extractor", sources[3].source_id, "", False, "", 1000),
        ("logs_extractor", sources[4].source_id, "", True, "timestamp", 50000)
    ]
    
    extractors = []
    for name, src_id, query, incr, col, batch in extractors_data:
        e = await platform.create_extractor(name, src_id, query, incr, col, batch)
        if e:
            extractors.append(e)
            print(f"  📖 {name} (incremental: {incr})")
            
    # Create Transformers
    print("\n⚙️ Creating Transformers...")
    
    transformers_data = [
        ("clean_nulls", TransformationType.FILTER, {"remove_nulls": True}, "FILTER(NOT IS_NULL(id))", 1),
        ("map_fields", TransformationType.MAP, {"mappings": {"amount": "total", "customer_id": "user_id"}}, "MAP(amount -> total)", 2),
        ("aggregate_daily", TransformationType.AGGREGATE, {"group_by": ["date"], "sum": ["amount"]}, "GROUP BY date SUM(amount)", 3),
        ("deduplicate", TransformationType.DEDUPLICATE, {"key_columns": ["id"]}, "DISTINCT(id)", 4),
        ("join_users", TransformationType.JOIN, {"type": "left", "on": "customer_id = user_id"}, "LEFT JOIN users", 5),
        ("pivot_status", TransformationType.PIVOT, {"pivot_column": "status", "value_column": "count"}, "PIVOT(status)", 6)
    ]
    
    transformers = []
    for name, ttype, config, expr, order in transformers_data:
        t = await platform.create_transformer(name, ttype, config, expr, order)
        transformers.append(t)
        print(f"  ⚙️ {name} ({ttype.value})")
        
    # Create Loaders
    print("\n✍️ Creating Loaders...")
    
    loaders_data = [
        ("warehouse_loader", targets[0].target_id, LoadMode.UPSERT, 5000, ["id"]),
        ("elasticsearch_loader", targets[1].target_id, LoadMode.APPEND, 1000, []),
        ("datalake_loader", targets[2].target_id, LoadMode.APPEND, 10000, []),
        ("archive_loader", targets[3].target_id, LoadMode.OVERWRITE, 50000, [])
    ]
    
    loaders = []
    for name, tgt_id, mode, batch, keys in loaders_data:
        l = await platform.create_loader(name, tgt_id, mode, batch, keys)
        if l:
            loaders.append(l)
            print(f"  ✍️ {name} ({mode.value})")
            
    # Create Quality Rules
    print("\n✅ Creating Quality Rules...")
    
    rules_data = [
        ("orders_not_null_id", schemas[0].schema_id, "id", QualityRuleType.NOT_NULL, {}, 100.0, True),
        ("orders_positive_amount", schemas[0].schema_id, "amount", QualityRuleType.RANGE, {"min": 0}, 99.9, True),
        ("users_unique_email", schemas[1].schema_id, "email", QualityRuleType.UNIQUE, {}, 100.0, True),
        ("users_valid_email", schemas[1].schema_id, "email", QualityRuleType.REGEX, {"pattern": "^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$"}, 99.0, False),
        ("events_valid_type", schemas[2].schema_id, "event_type", QualityRuleType.NOT_NULL, {}, 100.0, True)
    ]
    
    rules = []
    for name, sch_id, field, rtype, config, threshold, fail in rules_data:
        r = await platform.add_quality_rule(name, sch_id, field, rtype, config, threshold, fail)
        rules.append(r)
        print(f"  ✅ {name} ({rtype.value})")
        
    # Create Pipelines
    print("\n🔄 Creating Pipelines...")
    
    pipelines_data = [
        ("orders_etl", "Daily orders ETL to warehouse", [extractors[0].extractor_id], [transformers[0].transformer_id, transformers[1].transformer_id], [loaders[0].loader_id], "0 2 * * *", 4, ["orders", "daily"]),
        ("users_sync", "User data synchronization", [extractors[1].extractor_id], [transformers[3].transformer_id], [loaders[0].loader_id], "0 */4 * * *", 2, ["users", "sync"]),
        ("events_streaming", "Real-time events to Elasticsearch", [extractors[2].extractor_id], [transformers[0].transformer_id], [loaders[1].loader_id], "", 8, ["events", "realtime"]),
        ("archive_pipeline", "Data archiving to S3", [extractors[0].extractor_id, extractors[1].extractor_id], [transformers[3].transformer_id], [loaders[2].loader_id], "0 0 * * 0", 2, ["archive", "weekly"]),
        ("analytics_pipeline", "Analytics aggregation", [extractors[0].extractor_id], [transformers[2].transformer_id, transformers[5].transformer_id], [loaders[0].loader_id], "0 3 * * *", 4, ["analytics"])
    ]
    
    pipelines = []
    for name, desc, ext_ids, trx_ids, ldr_ids, cron, parallel, tags in pipelines_data:
        p = await platform.create_pipeline(name, desc, ext_ids, trx_ids, ldr_ids, cron, parallel, tags)
        pipelines.append(p)
        print(f"  🔄 {name}")
        
    # Activate Pipelines
    for p in pipelines[:3]:
        await platform.activate_pipeline(p.pipeline_id)
        
    # Run Pipelines
    print("\n▶️ Running Pipelines...")
    
    executions = []
    
    for pipeline in pipelines[:4]:
        for _ in range(random.randint(2, 5)):
            execution = await platform.run_pipeline(pipeline.pipeline_id)
            if execution:
                executions.append(execution)
                
    print(f"  ▶️ Executed {len(executions)} pipeline runs")
    
    # Add Lineage
    print("\n🔗 Adding Data Lineage...")
    
    await platform.add_lineage("source", sources[0].source_id, "pipeline", pipelines[0].pipeline_id, {"id": "id", "amount": "total"})
    await platform.add_lineage("pipeline", pipelines[0].pipeline_id, "target", targets[0].target_id, {"total": "order_amount"})
    print(f"  🔗 Added lineage for orders pipeline")
    
    # Collect Metrics
    print("\n📊 Collecting Metrics...")
    
    metrics = []
    for pipeline in pipelines[:3]:
        m = await platform.collect_metrics(pipeline.pipeline_id)
        if m:
            metrics.append(m)
            
    print(f"  📊 Collected metrics for {len(metrics)} pipelines")
    
    # Data Sources Dashboard
    print("\n📥 Data Sources:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                      │ Type          │ DB Type      │ Database        │ Schema       │ Connection                                                                                                                                                                                                                                                                                                                                                         │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for s in sources:
        name = s.name[:25].ljust(25)
        stype = s.source_type.value[:13].ljust(13)
        dbtype = s.database_type.value[:12].ljust(12)
        dbname = s.database_name[:15] if s.database_name else "N/A"
        dbname = dbname.ljust(15)
        schema = s.schema_name[:12] if s.schema_name else "N/A"
        schema = schema.ljust(12)
        conn = s.connection_string[:168] if s.connection_string else s.file_path[:168]
        conn = conn.ljust(168)
        
        print(f"  │ {name} │ {stype} │ {dbtype} │ {dbname} │ {schema} │ {conn} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Pipelines Dashboard
    print("\n🔄 ETL Pipelines:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                      │ Status     │ Extractors │ Transformers │ Loaders │ Cron              │ Parallelism │ Tags                                                                                                                                                                                                                                                                                                                                                              │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for p in pipelines:
        name = p.name[:25].ljust(25)
        
        status_icons = {"draft": "📝", "active": "✅", "running": "🔄", "paused": "⏸️", "completed": "✅", "failed": "❌"}
        status_icon = status_icons.get(p.status.value, "?")
        status = f"{status_icon} {p.status.value}"[:10].ljust(10)
        
        extractors_count = str(len(p.extractor_ids)).ljust(10)
        transformers_count = str(len(p.transformer_ids)).ljust(12)
        loaders_count = str(len(p.loader_ids)).ljust(7)
        cron = p.cron_expression[:17] if p.cron_expression else "N/A"
        cron = cron.ljust(17)
        parallel = str(p.parallelism).ljust(11)
        tags = ", ".join(p.tags)[:190]
        tags = tags.ljust(190)
        
        print(f"  │ {name} │ {status} │ {extractors_count} │ {transformers_count} │ {loaders_count} │ {cron} │ {parallel} │ {tags} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Pipeline Executions
    print("\n▶️ Pipeline Executions:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Execution ID                │ Pipeline                  │ Status   │ Extracted │ Transformed │ Loaded   │ Rejected │ Duration                                                                                                                                                                                                                                                                                                                                                                                                                                              │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for e in list(executions)[:12]:
        exec_id = e.execution_id[:27].ljust(27)
        
        pipeline = platform.pipelines.get(e.pipeline_id)
        pipe_name = pipeline.name if pipeline else "Unknown"
        pipe_name = pipe_name[:25].ljust(25)
        
        status_icons = {"pending": "⏳", "running": "🔄", "success": "✅", "failed": "❌", "cancelled": "⚫"}
        status_icon = status_icons.get(e.status.value, "?")
        status = f"{status_icon}".ljust(8)
        
        extracted = str(e.rows_extracted).ljust(9)
        transformed = str(e.rows_transformed).ljust(11)
        loaded = str(e.rows_loaded).ljust(8)
        rejected = str(e.rows_rejected).ljust(8)
        duration = f"{e.duration_seconds:.1f}s".ljust(222)
        
        print(f"  │ {exec_id} │ {pipe_name} │ {status} │ {extracted} │ {transformed} │ {loaded} │ {rejected} │ {duration} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Quality Checks
    print("\n✅ Quality Checks:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Rule Name                      │ Type        │ Field          │ Total Rows │ Passed │ Failed │ Pass Rate │ Status                                                                                                                                                                                                                                                                                                                                                              │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for check in list(platform.quality_checks.values())[:10]:
        rule = platform.quality_rules.get(check.rule_id)
        rule_name = rule.name if rule else "Unknown"
        rule_name = rule_name[:30].ljust(30)
        
        rtype = rule.rule_type.value if rule else "unknown"
        rtype = rtype[:11].ljust(11)
        
        field = rule.field_name if rule else "N/A"
        field = field[:14].ljust(14)
        
        total = str(check.total_rows).ljust(10)
        passed = str(check.passed_rows).ljust(6)
        failed = str(check.failed_rows).ljust(6)
        pass_rate = f"{check.pass_rate:.1f}%".ljust(9)
        status = "✅ Passed" if check.is_passed else "❌ Failed"
        status = status[:158].ljust(158)
        
        print(f"  │ {rule_name} │ {rtype} │ {field} │ {total} │ {passed} │ {failed} │ {pass_rate} │ {status} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # ETL Metrics
    print("\n📊 ETL Metrics:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Pipeline                  │ Executions │ Success │ Failed │ Rows Extracted │ Rows Loaded │ Avg Duration │ Throughput/s │ Quality Score                                                                                                                                                                                                                                                                                                                                                                       │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for m in metrics:
        pipeline = platform.pipelines.get(m.pipeline_id)
        pipe_name = pipeline.name if pipeline else "Unknown"
        pipe_name = pipe_name[:25].ljust(25)
        
        total = str(m.total_executions).ljust(10)
        success = str(m.successful_executions).ljust(7)
        failed = str(m.failed_executions).ljust(6)
        extracted = str(m.total_rows_extracted).ljust(14)
        loaded = str(m.total_rows_loaded).ljust(11)
        duration = f"{m.avg_duration_seconds:.1f}s".ljust(12)
        throughput = f"{m.avg_rows_per_second:.0f}".ljust(12)
        quality = f"{m.avg_quality_score:.1f}%".ljust(183)
        
        print(f"  │ {pipe_name} │ {total} │ {success} │ {failed} │ {extracted} │ {loaded} │ {duration} │ {throughput} │ {quality} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Sources: {stats['active_sources']}/{stats['total_sources']} active")
    print(f"  Targets: {stats['active_targets']}/{stats['total_targets']} active")
    print(f"  Pipelines: {stats['active_pipelines']} active, {stats['running_pipelines']} running")
    print(f"  Executions: {stats['success_executions']} success, {stats['failed_executions']} failed")
    print(f"  Rows: {stats['total_rows_extracted']} extracted, {stats['total_rows_loaded']} loaded")
    print(f"  Quality Rules: {stats['active_quality_rules']}/{stats['total_quality_rules']} active")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                          ETL Platform                              │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Data Sources:                 {stats['active_sources']:>12}                      │")
    print(f"│ Data Targets:                 {stats['active_targets']:>12}                      │")
    print(f"│ Active Pipelines:             {stats['active_pipelines']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Executions:             {stats['total_executions']:>12}                      │")
    print(f"│ Success Executions:           {stats['success_executions']:>12}                      │")
    print(f"│ Failed Executions:            {stats['failed_executions']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Rows Extracted:         {stats['total_rows_extracted']:>12}                      │")
    print(f"│ Total Rows Loaded:            {stats['total_rows_loaded']:>12}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("ETL Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
