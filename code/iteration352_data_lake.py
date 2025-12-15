#!/usr/bin/env python3
"""
Server Init - Iteration 352: Data Lake Platform
Платформа озера данных

Функционал:
- Data Zones - зоны данных (raw, curated, consumption)
- Data Catalog - каталог данных
- Schema Registry - реестр схем
- Data Partitioning - партиционирование данных
- Data Lifecycle - жизненный цикл данных
- Access Control - контроль доступа
- Data Discovery - обнаружение данных
- Data Governance - управление данными
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import json


class DataZone(Enum):
    """Зона данных"""
    RAW = "raw"
    STAGING = "staging"
    CURATED = "curated"
    CONSUMPTION = "consumption"
    ARCHIVE = "archive"


class DataFormat(Enum):
    """Формат данных"""
    PARQUET = "parquet"
    AVRO = "avro"
    ORC = "orc"
    JSON = "json"
    CSV = "csv"
    DELTA = "delta"
    ICEBERG = "iceberg"


class CompressionType(Enum):
    """Тип сжатия"""
    NONE = "none"
    GZIP = "gzip"
    SNAPPY = "snappy"
    LZ4 = "lz4"
    ZSTD = "zstd"


class PartitionStrategy(Enum):
    """Стратегия партиционирования"""
    DATE = "date"
    HASH = "hash"
    RANGE = "range"
    LIST = "list"


class DataClassification(Enum):
    """Классификация данных"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class LifecycleAction(Enum):
    """Действие жизненного цикла"""
    TRANSITION = "transition"
    DELETE = "delete"
    ARCHIVE = "archive"
    COMPRESS = "compress"


class CatalogStatus(Enum):
    """Статус каталога"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    DELETED = "deleted"


@dataclass
class Dataset:
    """Набор данных"""
    dataset_id: str
    name: str
    
    # Zone
    zone: DataZone = DataZone.RAW
    
    # Location
    path: str = ""
    bucket: str = ""
    
    # Format
    data_format: DataFormat = DataFormat.PARQUET
    compression: CompressionType = CompressionType.SNAPPY
    
    # Schema
    schema_id: str = ""
    
    # Partitioning
    partition_columns: List[str] = field(default_factory=list)
    partition_strategy: PartitionStrategy = PartitionStrategy.DATE
    
    # Classification
    classification: DataClassification = DataClassification.INTERNAL
    
    # Owner
    owner: str = ""
    team: str = ""
    
    # Description
    description: str = ""
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Stats
    size_bytes: int = 0
    row_count: int = 0
    file_count: int = 0
    partition_count: int = 0
    
    # Status
    status: CatalogStatus = CatalogStatus.ACTIVE
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None


@dataclass
class Schema:
    """Схема данных"""
    schema_id: str
    name: str
    dataset_id: str
    
    # Fields
    fields: List[Dict[str, Any]] = field(default_factory=list)
    
    # Primary key
    primary_key: List[str] = field(default_factory=list)
    
    # Version
    version: int = 1
    is_latest: bool = True
    
    # Compatibility
    compatibility_mode: str = "backward"  # backward, forward, full, none
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Partition:
    """Партиция"""
    partition_id: str
    dataset_id: str
    
    # Partition values
    partition_values: Dict[str, str] = field(default_factory=dict)
    
    # Location
    path: str = ""
    
    # Stats
    size_bytes: int = 0
    row_count: int = 0
    file_count: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


@dataclass
class DataFile:
    """Файл данных"""
    file_id: str
    dataset_id: str
    partition_id: str = ""
    
    # File info
    file_name: str = ""
    file_path: str = ""
    
    # Format
    data_format: DataFormat = DataFormat.PARQUET
    compression: CompressionType = CompressionType.SNAPPY
    
    # Stats
    size_bytes: int = 0
    row_count: int = 0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CatalogEntry:
    """Запись каталога"""
    entry_id: str
    dataset_id: str
    
    # Database/Table
    database_name: str = ""
    table_name: str = ""
    
    # Type
    entry_type: str = "table"  # table, view, external
    
    # Location
    location: str = ""
    
    # Properties
    properties: Dict[str, str] = field(default_factory=dict)
    
    # Status
    status: CatalogStatus = CatalogStatus.ACTIVE
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


@dataclass
class LifecycleRule:
    """Правило жизненного цикла"""
    rule_id: str
    name: str
    
    # Target
    zone: DataZone = DataZone.RAW
    dataset_pattern: str = "*"
    
    # Condition
    age_days: int = 30
    
    # Action
    action: LifecycleAction = LifecycleAction.TRANSITION
    target_zone: DataZone = DataZone.ARCHIVE
    
    # Status
    is_enabled: bool = True
    
    # Stats
    executions: int = 0
    bytes_processed: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_executed: Optional[datetime] = None


@dataclass
class AccessPolicy:
    """Политика доступа"""
    policy_id: str
    name: str
    
    # Target
    dataset_id: str = ""
    zone: DataZone = DataZone.RAW
    
    # Principal
    principal_type: str = "user"  # user, group, role
    principal_id: str = ""
    
    # Permissions
    permissions: List[str] = field(default_factory=list)  # read, write, delete, admin
    
    # Conditions
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


@dataclass
class DataLineage:
    """Линия данных"""
    lineage_id: str
    
    # Source
    source_dataset_id: str = ""
    source_type: str = ""  # dataset, external, stream
    
    # Target
    target_dataset_id: str = ""
    
    # Transformation
    transformation_type: str = ""  # etl, copy, aggregate
    transformation_id: str = ""
    
    # Field mappings
    field_mappings: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DataQualityRule:
    """Правило качества данных"""
    rule_id: str
    name: str
    dataset_id: str
    
    # Rule type
    rule_type: str = ""  # completeness, uniqueness, validity, consistency
    
    # Field
    field_name: str = ""
    
    # Expectation
    expectation: str = ""
    threshold: float = 100.0
    
    # Status
    is_enabled: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class QualityCheckResult:
    """Результат проверки качества"""
    check_id: str
    rule_id: str
    dataset_id: str
    
    # Results
    total_rows: int = 0
    passed_rows: int = 0
    failed_rows: int = 0
    pass_rate: float = 0.0
    
    # Status
    is_passed: bool = True
    
    # Timestamps
    checked_at: datetime = field(default_factory=datetime.now)


@dataclass
class SearchResult:
    """Результат поиска"""
    dataset_id: str
    name: str
    zone: DataZone
    score: float = 0.0
    highlights: List[str] = field(default_factory=list)


@dataclass
class DataLakeMetrics:
    """Метрики озера данных"""
    metrics_id: str
    zone: DataZone
    
    # Storage
    total_size_bytes: int = 0
    total_files: int = 0
    total_datasets: int = 0
    
    # Activity
    reads_today: int = 0
    writes_today: int = 0
    
    # Growth
    size_growth_percent: float = 0.0
    
    # Timestamps
    collected_at: datetime = field(default_factory=datetime.now)


class DataLakePlatform:
    """Платформа озера данных"""
    
    def __init__(self, bucket: str = "data-lake"):
        self.bucket = bucket
        self.datasets: Dict[str, Dataset] = {}
        self.schemas: Dict[str, Schema] = {}
        self.partitions: Dict[str, Partition] = {}
        self.files: Dict[str, DataFile] = {}
        self.catalog_entries: Dict[str, CatalogEntry] = {}
        self.lifecycle_rules: Dict[str, LifecycleRule] = {}
        self.access_policies: Dict[str, AccessPolicy] = {}
        self.lineages: Dict[str, DataLineage] = {}
        self.quality_rules: Dict[str, DataQualityRule] = {}
        self.quality_results: Dict[str, QualityCheckResult] = {}
        self.metrics: Dict[str, DataLakeMetrics] = {}
        
    async def create_dataset(self, name: str,
                            zone: DataZone = DataZone.RAW,
                            data_format: DataFormat = DataFormat.PARQUET,
                            compression: CompressionType = CompressionType.SNAPPY,
                            partition_columns: List[str] = None,
                            partition_strategy: PartitionStrategy = PartitionStrategy.DATE,
                            classification: DataClassification = DataClassification.INTERNAL,
                            owner: str = "",
                            team: str = "",
                            description: str = "",
                            tags: List[str] = None) -> Dataset:
        """Создание набора данных"""
        dataset = Dataset(
            dataset_id=f"ds_{uuid.uuid4().hex[:12]}",
            name=name,
            zone=zone,
            path=f"s3://{self.bucket}/{zone.value}/{name}",
            bucket=self.bucket,
            data_format=data_format,
            compression=compression,
            partition_columns=partition_columns or [],
            partition_strategy=partition_strategy,
            classification=classification,
            owner=owner,
            team=team,
            description=description,
            tags=tags or []
        )
        
        self.datasets[dataset.dataset_id] = dataset
        
        # Create catalog entry
        await self._create_catalog_entry(dataset)
        
        return dataset
        
    async def _create_catalog_entry(self, dataset: Dataset) -> CatalogEntry:
        """Создание записи каталога"""
        entry = CatalogEntry(
            entry_id=f"cat_{uuid.uuid4().hex[:8]}",
            dataset_id=dataset.dataset_id,
            database_name=dataset.zone.value,
            table_name=dataset.name,
            location=dataset.path,
            properties={
                "format": dataset.data_format.value,
                "compression": dataset.compression.value,
                "classification": dataset.classification.value
            }
        )
        
        self.catalog_entries[entry.entry_id] = entry
        return entry
        
    async def register_schema(self, dataset_id: str,
                             name: str,
                             fields: List[Dict[str, Any]],
                             primary_key: List[str] = None,
                             compatibility_mode: str = "backward") -> Optional[Schema]:
        """Регистрация схемы"""
        dataset = self.datasets.get(dataset_id)
        if not dataset:
            return None
            
        # Check for existing schemas and update version
        existing = [s for s in self.schemas.values() if s.dataset_id == dataset_id]
        version = max([s.version for s in existing], default=0) + 1
        
        # Mark old schemas as not latest
        for s in existing:
            s.is_latest = False
            
        schema = Schema(
            schema_id=f"sch_{uuid.uuid4().hex[:8]}",
            name=name,
            dataset_id=dataset_id,
            fields=fields,
            primary_key=primary_key or [],
            version=version,
            compatibility_mode=compatibility_mode
        )
        
        self.schemas[schema.schema_id] = schema
        dataset.schema_id = schema.schema_id
        
        return schema
        
    async def add_partition(self, dataset_id: str,
                           partition_values: Dict[str, str]) -> Optional[Partition]:
        """Добавление партиции"""
        dataset = self.datasets.get(dataset_id)
        if not dataset:
            return None
            
        # Build partition path
        partition_path = "/".join([f"{k}={v}" for k, v in partition_values.items()])
        
        partition = Partition(
            partition_id=f"part_{uuid.uuid4().hex[:8]}",
            dataset_id=dataset_id,
            partition_values=partition_values,
            path=f"{dataset.path}/{partition_path}"
        )
        
        self.partitions[partition.partition_id] = partition
        dataset.partition_count += 1
        
        return partition
        
    async def add_file(self, dataset_id: str,
                      file_name: str,
                      partition_id: str = "",
                      size_bytes: int = 0,
                      row_count: int = 0,
                      metadata: Dict[str, Any] = None) -> Optional[DataFile]:
        """Добавление файла"""
        dataset = self.datasets.get(dataset_id)
        if not dataset:
            return None
            
        partition = self.partitions.get(partition_id) if partition_id else None
        base_path = partition.path if partition else dataset.path
        
        file = DataFile(
            file_id=f"file_{uuid.uuid4().hex[:8]}",
            dataset_id=dataset_id,
            partition_id=partition_id,
            file_name=file_name,
            file_path=f"{base_path}/{file_name}",
            data_format=dataset.data_format,
            compression=dataset.compression,
            size_bytes=size_bytes,
            row_count=row_count,
            metadata=metadata or {}
        )
        
        self.files[file.file_id] = file
        
        # Update stats
        dataset.file_count += 1
        dataset.size_bytes += size_bytes
        dataset.row_count += row_count
        
        if partition:
            partition.file_count += 1
            partition.size_bytes += size_bytes
            partition.row_count += row_count
            
        return file
        
    async def create_lifecycle_rule(self, name: str,
                                   zone: DataZone,
                                   age_days: int,
                                   action: LifecycleAction,
                                   target_zone: DataZone = DataZone.ARCHIVE,
                                   dataset_pattern: str = "*") -> LifecycleRule:
        """Создание правила жизненного цикла"""
        rule = LifecycleRule(
            rule_id=f"lcr_{uuid.uuid4().hex[:8]}",
            name=name,
            zone=zone,
            dataset_pattern=dataset_pattern,
            age_days=age_days,
            action=action,
            target_zone=target_zone
        )
        
        self.lifecycle_rules[rule.rule_id] = rule
        return rule
        
    async def execute_lifecycle_rules(self):
        """Выполнение правил жизненного цикла"""
        for rule in self.lifecycle_rules.values():
            if not rule.is_enabled:
                continue
                
            # Find matching datasets
            datasets = [d for d in self.datasets.values() 
                       if d.zone == rule.zone and d.status == CatalogStatus.ACTIVE]
            
            for dataset in datasets:
                # Check age
                if dataset.created_at < datetime.now() - timedelta(days=rule.age_days):
                    await self._apply_lifecycle_action(dataset, rule)
                    
            rule.last_executed = datetime.now()
            rule.executions += 1
            
    async def _apply_lifecycle_action(self, dataset: Dataset, rule: LifecycleRule):
        """Применение действия жизненного цикла"""
        if rule.action == LifecycleAction.TRANSITION:
            dataset.zone = rule.target_zone
            dataset.path = f"s3://{self.bucket}/{rule.target_zone.value}/{dataset.name}"
        elif rule.action == LifecycleAction.DELETE:
            dataset.status = CatalogStatus.DELETED
        elif rule.action == LifecycleAction.ARCHIVE:
            dataset.zone = DataZone.ARCHIVE
            
        rule.bytes_processed += dataset.size_bytes
        dataset.updated_at = datetime.now()
        
    async def grant_access(self, name: str,
                          dataset_id: str,
                          principal_type: str,
                          principal_id: str,
                          permissions: List[str],
                          expires_at: datetime = None) -> AccessPolicy:
        """Предоставление доступа"""
        policy = AccessPolicy(
            policy_id=f"pol_{uuid.uuid4().hex[:8]}",
            name=name,
            dataset_id=dataset_id,
            principal_type=principal_type,
            principal_id=principal_id,
            permissions=permissions,
            expires_at=expires_at
        )
        
        self.access_policies[policy.policy_id] = policy
        return policy
        
    async def revoke_access(self, policy_id: str) -> bool:
        """Отзыв доступа"""
        policy = self.access_policies.get(policy_id)
        if not policy:
            return False
            
        policy.is_active = False
        return True
        
    async def add_lineage(self, source_dataset_id: str,
                         target_dataset_id: str,
                         transformation_type: str,
                         field_mappings: Dict[str, str] = None) -> DataLineage:
        """Добавление линии данных"""
        lineage = DataLineage(
            lineage_id=f"lin_{uuid.uuid4().hex[:8]}",
            source_dataset_id=source_dataset_id,
            source_type="dataset",
            target_dataset_id=target_dataset_id,
            transformation_type=transformation_type,
            field_mappings=field_mappings or {}
        )
        
        self.lineages[lineage.lineage_id] = lineage
        return lineage
        
    async def add_quality_rule(self, name: str,
                              dataset_id: str,
                              rule_type: str,
                              field_name: str,
                              expectation: str,
                              threshold: float = 100.0) -> DataQualityRule:
        """Добавление правила качества"""
        rule = DataQualityRule(
            rule_id=f"qr_{uuid.uuid4().hex[:8]}",
            name=name,
            dataset_id=dataset_id,
            rule_type=rule_type,
            field_name=field_name,
            expectation=expectation,
            threshold=threshold
        )
        
        self.quality_rules[rule.rule_id] = rule
        return rule
        
    async def run_quality_checks(self, dataset_id: str) -> List[QualityCheckResult]:
        """Выполнение проверок качества"""
        dataset = self.datasets.get(dataset_id)
        if not dataset:
            return []
            
        results = []
        rules = [r for r in self.quality_rules.values() if r.dataset_id == dataset_id and r.is_enabled]
        
        for rule in rules:
            # Simulate quality check
            total_rows = dataset.row_count
            pass_rate = random.uniform(0.9, 1.0)
            passed_rows = int(total_rows * pass_rate)
            
            result = QualityCheckResult(
                check_id=f"qc_{uuid.uuid4().hex[:8]}",
                rule_id=rule.rule_id,
                dataset_id=dataset_id,
                total_rows=total_rows,
                passed_rows=passed_rows,
                failed_rows=total_rows - passed_rows,
                pass_rate=pass_rate * 100,
                is_passed=pass_rate * 100 >= rule.threshold
            )
            
            self.quality_results[result.check_id] = result
            results.append(result)
            
        return results
        
    async def search_datasets(self, query: str,
                             zone: DataZone = None,
                             classification: DataClassification = None,
                             tags: List[str] = None,
                             limit: int = 10) -> List[SearchResult]:
        """Поиск наборов данных"""
        results = []
        
        for dataset in self.datasets.values():
            if dataset.status != CatalogStatus.ACTIVE:
                continue
                
            # Filter by zone
            if zone and dataset.zone != zone:
                continue
                
            # Filter by classification
            if classification and dataset.classification != classification:
                continue
                
            # Filter by tags
            if tags and not any(t in dataset.tags for t in tags):
                continue
                
            # Score by query match
            score = 0.0
            highlights = []
            
            if query.lower() in dataset.name.lower():
                score += 1.0
                highlights.append(f"name: {dataset.name}")
                
            if query.lower() in dataset.description.lower():
                score += 0.5
                highlights.append(f"description match")
                
            for tag in dataset.tags:
                if query.lower() in tag.lower():
                    score += 0.3
                    highlights.append(f"tag: {tag}")
                    
            if score > 0:
                results.append(SearchResult(
                    dataset_id=dataset.dataset_id,
                    name=dataset.name,
                    zone=dataset.zone,
                    score=score,
                    highlights=highlights
                ))
                
        # Sort by score
        results.sort(key=lambda r: -r.score)
        return results[:limit]
        
    async def collect_metrics(self, zone: DataZone) -> DataLakeMetrics:
        """Сбор метрик"""
        datasets = [d for d in self.datasets.values() if d.zone == zone]
        
        metrics = DataLakeMetrics(
            metrics_id=f"met_{uuid.uuid4().hex[:8]}",
            zone=zone,
            total_size_bytes=sum(d.size_bytes for d in datasets),
            total_files=sum(d.file_count for d in datasets),
            total_datasets=len(datasets),
            reads_today=random.randint(100, 10000),
            writes_today=random.randint(10, 1000),
            size_growth_percent=random.uniform(-5, 15)
        )
        
        self.metrics[metrics.metrics_id] = metrics
        return metrics
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_datasets = len(self.datasets)
        active_datasets = sum(1 for d in self.datasets.values() if d.status == CatalogStatus.ACTIVE)
        
        total_size = sum(d.size_bytes for d in self.datasets.values())
        total_files = sum(d.file_count for d in self.datasets.values())
        total_rows = sum(d.row_count for d in self.datasets.values())
        
        datasets_by_zone = {}
        for zone in DataZone:
            datasets_by_zone[zone.value] = sum(1 for d in self.datasets.values() if d.zone == zone)
            
        total_schemas = len(self.schemas)
        total_partitions = len(self.partitions)
        
        total_policies = len(self.access_policies)
        active_policies = sum(1 for p in self.access_policies.values() if p.is_active)
        
        total_quality_rules = len(self.quality_rules)
        
        return {
            "total_datasets": total_datasets,
            "active_datasets": active_datasets,
            "total_size_bytes": total_size,
            "total_size_gb": total_size / (1024**3),
            "total_files": total_files,
            "total_rows": total_rows,
            "datasets_by_zone": datasets_by_zone,
            "total_schemas": total_schemas,
            "total_partitions": total_partitions,
            "total_policies": total_policies,
            "active_policies": active_policies,
            "total_quality_rules": total_quality_rules
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 352: Data Lake Platform")
    print("=" * 60)
    
    platform = DataLakePlatform(bucket="enterprise-data-lake")
    print("✓ Data Lake Platform initialized")
    
    # Create Datasets
    print("\n📦 Creating Datasets...")
    
    datasets_data = [
        ("raw_orders", DataZone.RAW, DataFormat.JSON, CompressionType.GZIP, ["year", "month", "day"], PartitionStrategy.DATE, DataClassification.CONFIDENTIAL, "data-eng", "platform", "Raw orders from transactional DB", ["orders", "raw", "transactional"]),
        ("raw_users", DataZone.RAW, DataFormat.JSON, CompressionType.GZIP, ["region"], PartitionStrategy.LIST, DataClassification.RESTRICTED, "data-eng", "platform", "Raw user data", ["users", "raw", "pii"]),
        ("raw_events", DataZone.RAW, DataFormat.AVRO, CompressionType.SNAPPY, ["date", "event_type"], PartitionStrategy.DATE, DataClassification.INTERNAL, "analytics", "events", "Raw event stream", ["events", "clickstream"]),
        ("curated_orders", DataZone.CURATED, DataFormat.PARQUET, CompressionType.SNAPPY, ["year", "month"], PartitionStrategy.DATE, DataClassification.CONFIDENTIAL, "data-eng", "platform", "Curated orders with enrichment", ["orders", "curated"]),
        ("curated_users", DataZone.CURATED, DataFormat.PARQUET, CompressionType.SNAPPY, ["country"], PartitionStrategy.LIST, DataClassification.RESTRICTED, "data-eng", "platform", "Curated user profiles", ["users", "curated"]),
        ("fact_sales", DataZone.CONSUMPTION, DataFormat.DELTA, CompressionType.ZSTD, ["year", "quarter"], PartitionStrategy.DATE, DataClassification.CONFIDENTIAL, "bi-team", "analytics", "Sales fact table for BI", ["sales", "fact", "bi"]),
        ("dim_products", DataZone.CONSUMPTION, DataFormat.DELTA, CompressionType.ZSTD, [], PartitionStrategy.HASH, DataClassification.INTERNAL, "bi-team", "analytics", "Product dimension", ["products", "dimension"]),
        ("ml_features", DataZone.CONSUMPTION, DataFormat.PARQUET, CompressionType.SNAPPY, ["model_version"], PartitionStrategy.LIST, DataClassification.INTERNAL, "ml-team", "ml", "ML feature store", ["ml", "features"]),
        ("archive_logs", DataZone.ARCHIVE, DataFormat.ORC, CompressionType.ZSTD, ["year", "month"], PartitionStrategy.DATE, DataClassification.INTERNAL, "ops", "infrastructure", "Archived application logs", ["logs", "archive"]),
        ("staging_imports", DataZone.STAGING, DataFormat.CSV, CompressionType.GZIP, [], PartitionStrategy.DATE, DataClassification.INTERNAL, "data-eng", "integration", "Staging area for imports", ["staging", "imports"])
    ]
    
    datasets = []
    for name, zone, fmt, comp, parts, strat, cls, owner, team, desc, tags in datasets_data:
        d = await platform.create_dataset(name, zone, fmt, comp, parts, strat, cls, owner, team, desc, tags)
        datasets.append(d)
        print(f"  📦 {name} ({zone.value})")
        
    # Register Schemas
    print("\n📋 Registering Schemas...")
    
    schemas_data = [
        (datasets[0].dataset_id, "orders_schema_v1", [
            {"name": "order_id", "type": "string", "nullable": False},
            {"name": "customer_id", "type": "string", "nullable": False},
            {"name": "amount", "type": "decimal(18,2)", "nullable": False},
            {"name": "status", "type": "string", "nullable": False},
            {"name": "created_at", "type": "timestamp", "nullable": False}
        ], ["order_id"]),
        (datasets[1].dataset_id, "users_schema_v1", [
            {"name": "user_id", "type": "string", "nullable": False},
            {"name": "email", "type": "string", "nullable": False},
            {"name": "name", "type": "string", "nullable": True},
            {"name": "country", "type": "string", "nullable": True},
            {"name": "created_at", "type": "timestamp", "nullable": False}
        ], ["user_id"]),
        (datasets[5].dataset_id, "fact_sales_schema_v1", [
            {"name": "sale_id", "type": "bigint", "nullable": False},
            {"name": "product_id", "type": "string", "nullable": False},
            {"name": "customer_id", "type": "string", "nullable": False},
            {"name": "quantity", "type": "integer", "nullable": False},
            {"name": "amount", "type": "decimal(18,2)", "nullable": False},
            {"name": "sale_date", "type": "date", "nullable": False}
        ], ["sale_id"])
    ]
    
    schemas = []
    for ds_id, name, fields, pk in schemas_data:
        s = await platform.register_schema(ds_id, name, fields, pk)
        if s:
            schemas.append(s)
            print(f"  📋 {name} (v{s.version})")
            
    # Add Partitions and Files
    print("\n📁 Adding Partitions and Files...")
    
    for dataset in datasets[:5]:
        # Add partitions
        for i in range(random.randint(3, 10)):
            if dataset.partition_columns:
                if "year" in dataset.partition_columns:
                    values = {"year": "2024", "month": str(random.randint(1, 12)).zfill(2)}
                    if "day" in dataset.partition_columns:
                        values["day"] = str(random.randint(1, 28)).zfill(2)
                elif "region" in dataset.partition_columns:
                    values = {"region": random.choice(["us-east", "us-west", "eu-west", "ap-east"])}
                elif "country" in dataset.partition_columns:
                    values = {"country": random.choice(["US", "UK", "DE", "FR", "JP"])}
                else:
                    values = {"partition": str(i)}
                    
                partition = await platform.add_partition(dataset.dataset_id, values)
                
                # Add files to partition
                for j in range(random.randint(1, 5)):
                    await platform.add_file(
                        dataset.dataset_id,
                        f"part-{j:05d}.{dataset.data_format.value}",
                        partition.partition_id,
                        random.randint(1024*1024, 1024*1024*100),
                        random.randint(10000, 1000000)
                    )
                    
    print(f"  📁 Added {len(platform.partitions)} partitions and {len(platform.files)} files")
    
    # Create Lifecycle Rules
    print("\n🔄 Creating Lifecycle Rules...")
    
    lifecycle_data = [
        ("raw_to_archive_90d", DataZone.RAW, 90, LifecycleAction.TRANSITION, DataZone.ARCHIVE),
        ("staging_cleanup_7d", DataZone.STAGING, 7, LifecycleAction.DELETE, DataZone.STAGING),
        ("archive_compress_30d", DataZone.ARCHIVE, 30, LifecycleAction.COMPRESS, DataZone.ARCHIVE),
        ("curated_to_archive_365d", DataZone.CURATED, 365, LifecycleAction.TRANSITION, DataZone.ARCHIVE)
    ]
    
    lifecycle_rules = []
    for name, zone, days, action, target in lifecycle_data:
        r = await platform.create_lifecycle_rule(name, zone, days, action, target)
        lifecycle_rules.append(r)
        print(f"  🔄 {name} ({action.value} after {days} days)")
        
    # Grant Access
    print("\n🔐 Granting Access Policies...")
    
    access_data = [
        ("bi_team_sales_read", datasets[5].dataset_id, "group", "bi-analysts", ["read"]),
        ("ml_team_features_full", datasets[7].dataset_id, "group", "ml-engineers", ["read", "write"]),
        ("data_eng_all_admin", datasets[0].dataset_id, "group", "data-engineers", ["read", "write", "delete", "admin"]),
        ("analyst_curated_read", datasets[3].dataset_id, "role", "analyst", ["read"]),
        ("etl_raw_write", datasets[0].dataset_id, "role", "etl-service", ["read", "write"])
    ]
    
    policies = []
    for name, ds_id, ptype, pid, perms in access_data:
        p = await platform.grant_access(name, ds_id, ptype, pid, perms)
        policies.append(p)
        print(f"  🔐 {name} ({', '.join(perms)})")
        
    # Add Data Lineage
    print("\n🔗 Adding Data Lineage...")
    
    lineage_data = [
        (datasets[0].dataset_id, datasets[3].dataset_id, "etl", {"order_id": "order_id", "amount": "total_amount"}),
        (datasets[1].dataset_id, datasets[4].dataset_id, "etl", {"user_id": "user_id", "email": "email"}),
        (datasets[3].dataset_id, datasets[5].dataset_id, "aggregate", {"total_amount": "amount"}),
        (datasets[4].dataset_id, datasets[7].dataset_id, "transform", {"user_id": "customer_id"})
    ]
    
    lineages = []
    for src, tgt, ttype, mappings in lineage_data:
        l = await platform.add_lineage(src, tgt, ttype, mappings)
        lineages.append(l)
        
    print(f"  🔗 Added {len(lineages)} lineage records")
    
    # Add Quality Rules
    print("\n✅ Adding Quality Rules...")
    
    quality_data = [
        ("orders_id_not_null", datasets[0].dataset_id, "completeness", "order_id", "is_not_null", 100.0),
        ("orders_amount_positive", datasets[0].dataset_id, "validity", "amount", "value > 0", 99.9),
        ("users_email_unique", datasets[1].dataset_id, "uniqueness", "email", "is_unique", 100.0),
        ("users_email_valid", datasets[1].dataset_id, "validity", "email", "matches_pattern", 99.0),
        ("sales_amount_range", datasets[5].dataset_id, "validity", "amount", "between 0 and 1000000", 99.9)
    ]
    
    quality_rules = []
    for name, ds_id, rtype, field, expect, threshold in quality_data:
        r = await platform.add_quality_rule(name, ds_id, rtype, field, expect, threshold)
        quality_rules.append(r)
        print(f"  ✅ {name} ({rtype})")
        
    # Run Quality Checks
    print("\n🔍 Running Quality Checks...")
    
    all_results = []
    for dataset in datasets[:3]:
        results = await platform.run_quality_checks(dataset.dataset_id)
        all_results.extend(results)
        
    print(f"  🔍 Completed {len(all_results)} quality checks")
    
    # Collect Metrics
    print("\n📊 Collecting Metrics...")
    
    zone_metrics = []
    for zone in [DataZone.RAW, DataZone.CURATED, DataZone.CONSUMPTION]:
        m = await platform.collect_metrics(zone)
        zone_metrics.append(m)
        
    print(f"  📊 Collected metrics for {len(zone_metrics)} zones")
    
    # Search Datasets
    print("\n🔎 Searching Datasets...")
    
    search_results = await platform.search_datasets("orders", zone=DataZone.RAW)
    print(f"  🔎 Found {len(search_results)} datasets matching 'orders'")
    
    # Datasets Dashboard
    print("\n📦 Datasets:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                      │ Zone        │ Format   │ Classification │ Owner     │ Size        │ Files  │ Rows       │ Partitions │ Tags                                                                                                                                                                                                                                                                                                                                                                                                                                         │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for d in datasets:
        name = d.name[:25].ljust(25)
        zone = d.zone.value[:11].ljust(11)
        fmt = d.data_format.value[:8].ljust(8)
        cls = d.classification.value[:14].ljust(14)
        owner = d.owner[:9].ljust(9)
        
        size_mb = d.size_bytes / (1024*1024)
        if size_mb >= 1024:
            size = f"{size_mb/1024:.1f} GB"
        else:
            size = f"{size_mb:.1f} MB"
        size = size[:11].ljust(11)
        
        files = str(d.file_count).ljust(6)
        rows = f"{d.row_count:,}".ljust(10)
        parts = str(d.partition_count).ljust(10)
        tags = ", ".join(d.tags[:3])[:199]
        tags = tags.ljust(199)
        
        print(f"  │ {name} │ {zone} │ {fmt} │ {cls} │ {owner} │ {size} │ {files} │ {rows} │ {parts} │ {tags} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Schemas Dashboard
    print("\n📋 Schemas:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Schema Name                    │ Dataset                   │ Version │ Fields │ Primary Key │ Compatibility │ Latest                                                                                                                                                                                                                                                                                          │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for s in schemas:
        name = s.name[:30].ljust(30)
        dataset = platform.datasets.get(s.dataset_id)
        ds_name = dataset.name if dataset else "Unknown"
        ds_name = ds_name[:25].ljust(25)
        version = f"v{s.version}".ljust(7)
        fields = str(len(s.fields)).ljust(6)
        pk = ", ".join(s.primary_key)[:11] if s.primary_key else "N/A"
        pk = pk.ljust(11)
        compat = s.compatibility_mode[:13].ljust(13)
        latest = "✓" if s.is_latest else "✗"
        latest = latest.ljust(166)
        
        print(f"  │ {name} │ {ds_name} │ {version} │ {fields} │ {pk} │ {compat} │ {latest} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Zone Metrics
    print("\n📊 Zone Metrics:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Zone             │ Datasets │ Total Size   │ Total Files │ Reads Today │ Writes Today │ Growth %                                                                                                                                                                                                                                                                                                                                  │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for m in zone_metrics:
        zone = m.zone.value[:16].ljust(16)
        ds_count = str(m.total_datasets).ljust(8)
        
        size_gb = m.total_size_bytes / (1024**3)
        size = f"{size_gb:.2f} GB".ljust(12)
        
        files = str(m.total_files).ljust(11)
        reads = str(m.reads_today).ljust(11)
        writes = str(m.writes_today).ljust(12)
        growth = f"{m.size_growth_percent:+.1f}%".ljust(194)
        
        print(f"  │ {zone} │ {ds_count} │ {size} │ {files} │ {reads} │ {writes} │ {growth} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Quality Results
    print("\n✅ Quality Check Results:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Rule Name                           │ Dataset                   │ Total Rows │ Passed    │ Failed  │ Pass Rate │ Status                                                                                                                                                                                                                                                                                                                                                  │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for qr in all_results:
        rule = platform.quality_rules.get(qr.rule_id)
        rule_name = rule.name if rule else "Unknown"
        rule_name = rule_name[:37].ljust(37)
        
        dataset = platform.datasets.get(qr.dataset_id)
        ds_name = dataset.name if dataset else "Unknown"
        ds_name = ds_name[:25].ljust(25)
        
        total = f"{qr.total_rows:,}".ljust(10)
        passed = f"{qr.passed_rows:,}".ljust(9)
        failed = f"{qr.failed_rows:,}".ljust(7)
        rate = f"{qr.pass_rate:.2f}%".ljust(9)
        status = "✅ Passed" if qr.is_passed else "❌ Failed"
        status = status[:194].ljust(194)
        
        print(f"  │ {rule_name} │ {ds_name} │ {total} │ {passed} │ {failed} │ {rate} │ {status} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Datasets: {stats['active_datasets']}/{stats['total_datasets']} active")
    print(f"  Total Size: {stats['total_size_gb']:.2f} GB")
    print(f"  Total Files: {stats['total_files']:,}")
    print(f"  Total Rows: {stats['total_rows']:,}")
    print(f"  Schemas: {stats['total_schemas']}, Partitions: {stats['total_partitions']}")
    print(f"  Access Policies: {stats['active_policies']}/{stats['total_policies']} active")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                       Data Lake Platform                           │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Active Datasets:              {stats['active_datasets']:>12}                      │")
    print(f"│ Total Size (GB):              {stats['total_size_gb']:>12.2f}                      │")
    print(f"│ Total Files:                  {stats['total_files']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Raw Zone:                     {stats['datasets_by_zone'].get('raw', 0):>12}                      │")
    print(f"│ Curated Zone:                 {stats['datasets_by_zone'].get('curated', 0):>12}                      │")
    print(f"│ Consumption Zone:             {stats['datasets_by_zone'].get('consumption', 0):>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Schemas:                {stats['total_schemas']:>12}                      │")
    print(f"│ Total Partitions:             {stats['total_partitions']:>12}                      │")
    print(f"│ Quality Rules:                {stats['total_quality_rules']:>12}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Data Lake Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
