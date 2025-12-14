#!/usr/bin/env python3
"""
Server Init - Iteration 138: Data Lake Platform
Платформа Data Lake

Функционал:
- Data Ingestion - загрузка данных
- Schema Management - управление схемами
- Data Catalog - каталог данных
- Partitioning - партиционирование
- Format Conversion - конвертация форматов
- Data Quality - качество данных
- Access Control - контроль доступа
- Lineage Tracking - отслеживание происхождения
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from collections import defaultdict
import uuid
import hashlib


class DataFormat(Enum):
    """Формат данных"""
    PARQUET = "parquet"
    JSON = "json"
    CSV = "csv"
    AVRO = "avro"
    ORC = "orc"
    DELTA = "delta"
    ICEBERG = "iceberg"


class DataType(Enum):
    """Тип данных"""
    STRING = "string"
    INTEGER = "integer"
    LONG = "long"
    FLOAT = "float"
    DOUBLE = "double"
    BOOLEAN = "boolean"
    TIMESTAMP = "timestamp"
    DATE = "date"
    BINARY = "binary"
    ARRAY = "array"
    MAP = "map"
    STRUCT = "struct"


class IngestionMode(Enum):
    """Режим загрузки"""
    BATCH = "batch"
    STREAMING = "streaming"
    INCREMENTAL = "incremental"
    FULL_REFRESH = "full_refresh"


class Zone(Enum):
    """Зона данных"""
    RAW = "raw"
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"


@dataclass
class Column:
    """Колонка"""
    name: str
    data_type: DataType
    nullable: bool = True
    description: str = ""
    metadata: Dict = field(default_factory=dict)


@dataclass
class Schema:
    """Схема"""
    schema_id: str
    name: str = ""
    version: int = 1
    
    # Columns
    columns: List[Column] = field(default_factory=list)
    
    # Metadata
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Partition:
    """Партиция"""
    partition_id: str
    table_id: str = ""
    
    # Partition key
    partition_key: str = ""
    partition_value: str = ""
    
    # Stats
    row_count: int = 0
    size_bytes: int = 0
    file_count: int = 0
    
    # Location
    path: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class Table:
    """Таблица"""
    table_id: str
    name: str = ""
    
    # Location
    zone: Zone = Zone.RAW
    database: str = "default"
    
    # Schema
    schema: Optional[Schema] = None
    
    # Format
    data_format: DataFormat = DataFormat.PARQUET
    
    # Partitioning
    partition_columns: List[str] = field(default_factory=list)
    partitions: List[Partition] = field(default_factory=list)
    
    # Stats
    total_rows: int = 0
    total_size_bytes: int = 0
    
    # Metadata
    description: str = ""
    tags: List[str] = field(default_factory=list)
    owner: str = ""
    
    # Path
    location: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class IngestionJob:
    """Задание загрузки"""
    job_id: str
    source: str = ""
    target_table_id: str = ""
    
    # Mode
    mode: IngestionMode = IngestionMode.BATCH
    
    # Status
    status: str = "pending"  # pending, running, completed, failed
    
    # Stats
    records_read: int = 0
    records_written: int = 0
    bytes_processed: int = 0
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class QualityCheck:
    """Проверка качества"""
    check_id: str
    table_id: str = ""
    
    # Check type
    check_type: str = ""  # null_check, unique_check, range_check, pattern_check
    column: str = ""
    
    # Config
    threshold: float = 0.0
    
    # Results
    passed: bool = True
    actual_value: float = 0
    
    # Timestamp
    executed_at: datetime = field(default_factory=datetime.now)


@dataclass
class LineageNode:
    """Узел происхождения"""
    node_id: str
    node_type: str = ""  # table, job, transformation
    name: str = ""
    
    # Connections
    upstream: List[str] = field(default_factory=list)
    downstream: List[str] = field(default_factory=list)


class SchemaManager:
    """Менеджер схем"""
    
    def __init__(self):
        self.schemas: Dict[str, Schema] = {}
        self.versions: Dict[str, List[Schema]] = defaultdict(list)
        
    def create(self, name: str, columns: List[Dict], **kwargs) -> Schema:
        """Создание схемы"""
        parsed_columns = [
            Column(
                name=col["name"],
                data_type=DataType(col["type"]),
                nullable=col.get("nullable", True),
                description=col.get("description", "")
            )
            for col in columns
        ]
        
        schema = Schema(
            schema_id=f"schema_{uuid.uuid4().hex[:8]}",
            name=name,
            columns=parsed_columns,
            **kwargs
        )
        
        self.schemas[schema.schema_id] = schema
        self.versions[name].append(schema)
        
        return schema
        
    def evolve(self, schema_id: str, changes: List[Dict]) -> Schema:
        """Эволюция схемы"""
        old_schema = self.schemas.get(schema_id)
        if not old_schema:
            return None
            
        # Copy columns
        new_columns = list(old_schema.columns)
        
        for change in changes:
            if change["action"] == "add":
                new_columns.append(Column(
                    name=change["name"],
                    data_type=DataType(change["type"]),
                    nullable=change.get("nullable", True)
                ))
            elif change["action"] == "drop":
                new_columns = [c for c in new_columns if c.name != change["name"]]
                
        new_schema = Schema(
            schema_id=f"schema_{uuid.uuid4().hex[:8]}",
            name=old_schema.name,
            version=old_schema.version + 1,
            columns=new_columns
        )
        
        self.schemas[new_schema.schema_id] = new_schema
        self.versions[old_schema.name].append(new_schema)
        
        return new_schema
        
    def get_version_history(self, name: str) -> List[Dict]:
        """История версий"""
        return [
            {"schema_id": s.schema_id, "version": s.version, "columns": len(s.columns)}
            for s in self.versions.get(name, [])
        ]


class TableManager:
    """Менеджер таблиц"""
    
    def __init__(self, schema_manager: SchemaManager):
        self.schema_manager = schema_manager
        self.tables: Dict[str, Table] = {}
        
    def create(self, name: str, zone: Zone, database: str,
                schema: Schema, data_format: DataFormat = DataFormat.PARQUET,
                partition_columns: List[str] = None, **kwargs) -> Table:
        """Создание таблицы"""
        table = Table(
            table_id=f"table_{uuid.uuid4().hex[:8]}",
            name=name,
            zone=zone,
            database=database,
            schema=schema,
            data_format=data_format,
            partition_columns=partition_columns or [],
            location=f"s3://data-lake/{zone.value}/{database}/{name}/",
            **kwargs
        )
        
        self.tables[table.table_id] = table
        return table
        
    def add_partition(self, table_id: str, partition_key: str,
                       partition_value: str, row_count: int = 0,
                       size_bytes: int = 0) -> Partition:
        """Добавление партиции"""
        table = self.tables.get(table_id)
        if not table:
            return None
            
        partition = Partition(
            partition_id=f"part_{uuid.uuid4().hex[:8]}",
            table_id=table_id,
            partition_key=partition_key,
            partition_value=partition_value,
            row_count=row_count,
            size_bytes=size_bytes,
            path=f"{table.location}{partition_key}={partition_value}/"
        )
        
        table.partitions.append(partition)
        table.total_rows += row_count
        table.total_size_bytes += size_bytes
        
        return partition
        
    def get_table_stats(self, table_id: str) -> Dict:
        """Статистика таблицы"""
        table = self.tables.get(table_id)
        if not table:
            return {}
            
        return {
            "table_id": table_id,
            "name": table.name,
            "zone": table.zone.value,
            "format": table.data_format.value,
            "partitions": len(table.partitions),
            "total_rows": table.total_rows,
            "total_size_gb": round(table.total_size_bytes / (1024 ** 3), 2),
            "columns": len(table.schema.columns) if table.schema else 0
        }


class IngestionEngine:
    """Движок загрузки"""
    
    def __init__(self, table_manager: TableManager):
        self.table_manager = table_manager
        self.jobs: Dict[str, IngestionJob] = {}
        
    async def ingest(self, source: str, target_table_id: str,
                      mode: IngestionMode = IngestionMode.BATCH,
                      records: int = 1000) -> IngestionJob:
        """Загрузка данных"""
        job = IngestionJob(
            job_id=f"job_{uuid.uuid4().hex[:8]}",
            source=source,
            target_table_id=target_table_id,
            mode=mode,
            status="running",
            started_at=datetime.now()
        )
        self.jobs[job.job_id] = job
        
        # Simulate ingestion
        await asyncio.sleep(0.1)
        
        job.records_read = records
        job.records_written = records
        job.bytes_processed = records * 256  # ~256 bytes per record
        
        # Update table
        table = self.table_manager.tables.get(target_table_id)
        if table:
            table.total_rows += records
            table.total_size_bytes += job.bytes_processed
            table.updated_at = datetime.now()
            
        job.status = "completed"
        job.completed_at = datetime.now()
        
        return job
        
    def get_job_history(self, table_id: str = None) -> List[Dict]:
        """История загрузок"""
        jobs = self.jobs.values()
        if table_id:
            jobs = [j for j in jobs if j.target_table_id == table_id]
            
        return [
            {
                "job_id": j.job_id,
                "source": j.source,
                "mode": j.mode.value,
                "status": j.status,
                "records": j.records_written
            }
            for j in jobs
        ]


class DataCatalog:
    """Каталог данных"""
    
    def __init__(self, table_manager: TableManager):
        self.table_manager = table_manager
        self.metadata: Dict[str, Dict] = {}
        
    def register(self, table_id: str, metadata: Dict):
        """Регистрация в каталоге"""
        self.metadata[table_id] = {
            **metadata,
            "registered_at": datetime.now().isoformat()
        }
        
    def search(self, query: str = None, tags: List[str] = None,
                zone: Zone = None) -> List[Dict]:
        """Поиск в каталоге"""
        results = []
        
        for table in self.table_manager.tables.values():
            # Filter by zone
            if zone and table.zone != zone:
                continue
                
            # Filter by tags
            if tags and not all(t in table.tags for t in tags):
                continue
                
            # Filter by query
            if query:
                if query.lower() not in table.name.lower() and \
                   query.lower() not in table.description.lower():
                    continue
                    
            results.append({
                "table_id": table.table_id,
                "name": table.name,
                "zone": table.zone.value,
                "database": table.database,
                "description": table.description,
                "tags": table.tags
            })
            
        return results
        
    def get_table_info(self, table_id: str) -> Dict:
        """Информация о таблице"""
        table = self.table_manager.tables.get(table_id)
        if not table:
            return {}
            
        return {
            "table_id": table.table_id,
            "name": table.name,
            "zone": table.zone.value,
            "database": table.database,
            "format": table.data_format.value,
            "location": table.location,
            "schema": {
                "columns": [
                    {"name": c.name, "type": c.data_type.value, "nullable": c.nullable}
                    for c in table.schema.columns
                ] if table.schema else []
            },
            "partitions": len(table.partitions),
            "rows": table.total_rows,
            "size_gb": round(table.total_size_bytes / (1024 ** 3), 2),
            "tags": table.tags,
            "owner": table.owner,
            "metadata": self.metadata.get(table_id, {})
        }


class QualityEngine:
    """Движок качества данных"""
    
    def __init__(self, table_manager: TableManager):
        self.table_manager = table_manager
        self.checks: List[QualityCheck] = []
        
    async def run_check(self, table_id: str, check_type: str,
                         column: str, threshold: float = 0.0) -> QualityCheck:
        """Выполнение проверки"""
        check = QualityCheck(
            check_id=f"check_{uuid.uuid4().hex[:8]}",
            table_id=table_id,
            check_type=check_type,
            column=column,
            threshold=threshold
        )
        
        # Simulate check
        await asyncio.sleep(0.05)
        
        import random
        
        if check_type == "null_check":
            check.actual_value = random.uniform(0, 0.1)  # 0-10% nulls
            check.passed = check.actual_value <= threshold
        elif check_type == "unique_check":
            check.actual_value = random.uniform(0.95, 1.0)  # 95-100% unique
            check.passed = check.actual_value >= threshold
        elif check_type == "range_check":
            check.actual_value = random.uniform(0.9, 1.0)  # 90-100% in range
            check.passed = check.actual_value >= threshold
            
        self.checks.append(check)
        return check
        
    async def run_suite(self, table_id: str, checks: List[Dict]) -> Dict:
        """Запуск набора проверок"""
        results = []
        
        for check_config in checks:
            check = await self.run_check(
                table_id,
                check_config["type"],
                check_config["column"],
                check_config.get("threshold", 0.0)
            )
            results.append({
                "check": check.check_type,
                "column": check.column,
                "passed": check.passed,
                "value": round(check.actual_value, 3)
            })
            
        passed = len([r for r in results if r["passed"]])
        
        return {
            "table_id": table_id,
            "total_checks": len(results),
            "passed": passed,
            "failed": len(results) - passed,
            "results": results
        }


class LineageTracker:
    """Трекер происхождения"""
    
    def __init__(self):
        self.nodes: Dict[str, LineageNode] = {}
        
    def add_node(self, node_id: str, node_type: str, name: str) -> LineageNode:
        """Добавление узла"""
        node = LineageNode(
            node_id=node_id,
            node_type=node_type,
            name=name
        )
        self.nodes[node_id] = node
        return node
        
    def add_edge(self, upstream_id: str, downstream_id: str):
        """Добавление связи"""
        upstream = self.nodes.get(upstream_id)
        downstream = self.nodes.get(downstream_id)
        
        if upstream and downstream:
            upstream.downstream.append(downstream_id)
            downstream.upstream.append(upstream_id)
            
    def get_upstream(self, node_id: str, depth: int = 1) -> List[Dict]:
        """Получение восходящего происхождения"""
        result = []
        visited = set()
        
        def traverse(nid: str, d: int):
            if d <= 0 or nid in visited:
                return
            visited.add(nid)
            
            node = self.nodes.get(nid)
            if node:
                for up_id in node.upstream:
                    up_node = self.nodes.get(up_id)
                    if up_node:
                        result.append({
                            "node_id": up_id,
                            "type": up_node.node_type,
                            "name": up_node.name,
                            "depth": depth - d + 1
                        })
                        traverse(up_id, d - 1)
                        
        traverse(node_id, depth)
        return result
        
    def get_downstream(self, node_id: str, depth: int = 1) -> List[Dict]:
        """Получение нисходящего влияния"""
        result = []
        visited = set()
        
        def traverse(nid: str, d: int):
            if d <= 0 or nid in visited:
                return
            visited.add(nid)
            
            node = self.nodes.get(nid)
            if node:
                for down_id in node.downstream:
                    down_node = self.nodes.get(down_id)
                    if down_node:
                        result.append({
                            "node_id": down_id,
                            "type": down_node.node_type,
                            "name": down_node.name,
                            "depth": depth - d + 1
                        })
                        traverse(down_id, d - 1)
                        
        traverse(node_id, depth)
        return result


class DataLakePlatform:
    """Платформа Data Lake"""
    
    def __init__(self):
        self.schema_manager = SchemaManager()
        self.table_manager = TableManager(self.schema_manager)
        self.ingestion_engine = IngestionEngine(self.table_manager)
        self.catalog = DataCatalog(self.table_manager)
        self.quality_engine = QualityEngine(self.table_manager)
        self.lineage_tracker = LineageTracker()
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        tables = list(self.table_manager.tables.values())
        
        return {
            "schemas": len(self.schema_manager.schemas),
            "tables": len(tables),
            "tables_by_zone": {
                zone.value: len([t for t in tables if t.zone == zone])
                for zone in Zone
            },
            "total_rows": sum(t.total_rows for t in tables),
            "total_size_gb": round(sum(t.total_size_bytes for t in tables) / (1024 ** 3), 2),
            "ingestion_jobs": len(self.ingestion_engine.jobs),
            "quality_checks": len(self.quality_engine.checks),
            "lineage_nodes": len(self.lineage_tracker.nodes)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 138: Data Lake Platform")
    print("=" * 60)
    
    async def demo():
        platform = DataLakePlatform()
        print("✓ Data Lake Platform created")
        
        # Create schemas
        print("\n📋 Creating Schemas...")
        
        # Orders schema
        orders_schema = platform.schema_manager.create(
            "orders_schema",
            columns=[
                {"name": "order_id", "type": "string", "nullable": False},
                {"name": "customer_id", "type": "string", "nullable": False},
                {"name": "order_date", "type": "timestamp"},
                {"name": "total_amount", "type": "double"},
                {"name": "status", "type": "string"}
            ],
            description="Schema for orders data"
        )
        
        # Customers schema
        customers_schema = platform.schema_manager.create(
            "customers_schema",
            columns=[
                {"name": "customer_id", "type": "string", "nullable": False},
                {"name": "name", "type": "string"},
                {"name": "email", "type": "string"},
                {"name": "created_at", "type": "timestamp"},
                {"name": "country", "type": "string"}
            ]
        )
        
        # Products schema
        products_schema = platform.schema_manager.create(
            "products_schema",
            columns=[
                {"name": "product_id", "type": "string", "nullable": False},
                {"name": "name", "type": "string"},
                {"name": "category", "type": "string"},
                {"name": "price", "type": "double"},
                {"name": "inventory", "type": "integer"}
            ]
        )
        
        print(f"  ✓ orders_schema: {len(orders_schema.columns)} columns")
        print(f"  ✓ customers_schema: {len(customers_schema.columns)} columns")
        print(f"  ✓ products_schema: {len(products_schema.columns)} columns")
        
        # Create tables in different zones
        print("\n📦 Creating Tables...")
        
        # Raw zone
        raw_orders = platform.table_manager.create(
            "raw_orders",
            Zone.RAW,
            "sales",
            orders_schema,
            DataFormat.JSON,
            partition_columns=["order_date"],
            tags=["orders", "raw"],
            owner="data-team"
        )
        
        # Bronze zone
        bronze_orders = platform.table_manager.create(
            "bronze_orders",
            Zone.BRONZE,
            "sales",
            orders_schema,
            DataFormat.PARQUET,
            partition_columns=["order_date"],
            tags=["orders", "bronze", "cleaned"]
        )
        
        # Silver zone
        silver_orders = platform.table_manager.create(
            "silver_orders",
            Zone.SILVER,
            "sales",
            orders_schema,
            DataFormat.DELTA,
            partition_columns=["order_date"],
            tags=["orders", "silver", "enriched"]
        )
        
        # Gold zone
        gold_sales_summary = platform.table_manager.create(
            "gold_sales_summary",
            Zone.GOLD,
            "analytics",
            platform.schema_manager.create(
                "sales_summary_schema",
                columns=[
                    {"name": "date", "type": "date"},
                    {"name": "total_orders", "type": "integer"},
                    {"name": "total_revenue", "type": "double"},
                    {"name": "avg_order_value", "type": "double"}
                ]
            ),
            DataFormat.DELTA,
            partition_columns=["date"],
            tags=["analytics", "gold", "aggregated"]
        )
        
        for table in [raw_orders, bronze_orders, silver_orders, gold_sales_summary]:
            print(f"  ✓ {table.name} ({table.zone.value}): {table.data_format.value}")
            
        # Add partitions
        print("\n📂 Adding Partitions...")
        
        for i in range(5):
            date = f"2024-01-{15 + i:02d}"
            platform.table_manager.add_partition(
                bronze_orders.table_id,
                "order_date",
                date,
                row_count=10000 + i * 1000,
                size_bytes=1024 * 1024 * (10 + i)
            )
            
        print(f"  ✓ Added {len(bronze_orders.partitions)} partitions to bronze_orders")
        
        # Ingest data
        print("\n📥 Ingesting Data...")
        
        ingest_jobs = [
            ("s3://source/orders/", raw_orders.table_id, IngestionMode.BATCH, 50000),
            ("kafka://orders-topic", raw_orders.table_id, IngestionMode.STREAMING, 10000),
            ("jdbc://mysql/orders", bronze_orders.table_id, IngestionMode.INCREMENTAL, 25000)
        ]
        
        for source, table_id, mode, records in ingest_jobs:
            job = await platform.ingestion_engine.ingest(source, table_id, mode, records)
            print(f"  ✓ {mode.value}: {job.records_written:,} records from {source.split('/')[0]}")
            
        # Register in catalog
        print("\n📚 Registering in Data Catalog...")
        
        for table in [raw_orders, bronze_orders, silver_orders, gold_sales_summary]:
            platform.catalog.register(table.table_id, {
                "business_owner": "analytics-team",
                "pii_flag": table.zone in [Zone.RAW, Zone.BRONZE],
                "retention_days": 365
            })
            
        print(f"  ✓ Registered {len(platform.catalog.metadata)} tables")
        
        # Search catalog
        print("\n🔍 Searching Catalog...")
        
        results = platform.catalog.search(tags=["orders"])
        print(f"  Tables with 'orders' tag: {len(results)}")
        
        silver_tables = platform.catalog.search(zone=Zone.SILVER)
        print(f"  Tables in Silver zone: {len(silver_tables)}")
        
        # Get table info
        print("\n📊 Table Information:")
        
        info = platform.catalog.get_table_info(bronze_orders.table_id)
        print(f"\n  {info['name']}:")
        print(f"    Zone: {info['zone']}")
        print(f"    Format: {info['format']}")
        print(f"    Rows: {info['rows']:,}")
        print(f"    Size: {info['size_gb']} GB")
        print(f"    Partitions: {info['partitions']}")
        print(f"    Columns: {len(info['schema']['columns'])}")
        
        # Data quality checks
        print("\n✅ Running Data Quality Checks...")
        
        quality_suite = await platform.quality_engine.run_suite(
            bronze_orders.table_id,
            [
                {"type": "null_check", "column": "order_id", "threshold": 0.0},
                {"type": "null_check", "column": "customer_id", "threshold": 0.05},
                {"type": "unique_check", "column": "order_id", "threshold": 0.99},
                {"type": "range_check", "column": "total_amount", "threshold": 0.95}
            ]
        )
        
        print(f"\n  Results: {quality_suite['passed']}/{quality_suite['total_checks']} passed")
        
        for result in quality_suite["results"]:
            icon = "✓" if result["passed"] else "✗"
            print(f"  {icon} {result['check']} on {result['column']}: {result['value']}")
            
        # Lineage tracking
        print("\n🔗 Setting Up Lineage...")
        
        # Add nodes
        platform.lineage_tracker.add_node("source_mysql", "source", "MySQL Orders DB")
        platform.lineage_tracker.add_node("ingest_job", "job", "Orders Ingestion")
        platform.lineage_tracker.add_node(raw_orders.table_id, "table", raw_orders.name)
        platform.lineage_tracker.add_node("clean_job", "job", "Data Cleaning")
        platform.lineage_tracker.add_node(bronze_orders.table_id, "table", bronze_orders.name)
        platform.lineage_tracker.add_node("enrich_job", "job", "Data Enrichment")
        platform.lineage_tracker.add_node(silver_orders.table_id, "table", silver_orders.name)
        platform.lineage_tracker.add_node("aggregate_job", "job", "Aggregation")
        platform.lineage_tracker.add_node(gold_sales_summary.table_id, "table", gold_sales_summary.name)
        
        # Add edges
        platform.lineage_tracker.add_edge("source_mysql", "ingest_job")
        platform.lineage_tracker.add_edge("ingest_job", raw_orders.table_id)
        platform.lineage_tracker.add_edge(raw_orders.table_id, "clean_job")
        platform.lineage_tracker.add_edge("clean_job", bronze_orders.table_id)
        platform.lineage_tracker.add_edge(bronze_orders.table_id, "enrich_job")
        platform.lineage_tracker.add_edge("enrich_job", silver_orders.table_id)
        platform.lineage_tracker.add_edge(silver_orders.table_id, "aggregate_job")
        platform.lineage_tracker.add_edge("aggregate_job", gold_sales_summary.table_id)
        
        print(f"  ✓ Created {len(platform.lineage_tracker.nodes)} lineage nodes")
        
        # Get lineage
        upstream = platform.lineage_tracker.get_upstream(silver_orders.table_id, depth=5)
        downstream = platform.lineage_tracker.get_downstream(bronze_orders.table_id, depth=5)
        
        print(f"\n  Upstream of silver_orders:")
        for node in upstream:
            print(f"    {'  ' * (node['depth'] - 1)}← [{node['type']}] {node['name']}")
            
        print(f"\n  Downstream of bronze_orders:")
        for node in downstream:
            print(f"    {'  ' * (node['depth'] - 1)}→ [{node['type']}] {node['name']}")
            
        # Schema evolution
        print("\n📈 Schema Evolution:")
        
        evolved_schema = platform.schema_manager.evolve(
            orders_schema.schema_id,
            [
                {"action": "add", "name": "discount", "type": "double"},
                {"action": "add", "name": "payment_method", "type": "string"}
            ]
        )
        
        history = platform.schema_manager.get_version_history("orders_schema")
        print(f"  orders_schema versions: {len(history)}")
        for v in history:
            print(f"    v{v['version']}: {v['columns']} columns")
            
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Schemas: {stats['schemas']}")
        print(f"  Tables: {stats['tables']}")
        print(f"  Tables by Zone:")
        for zone, count in stats["tables_by_zone"].items():
            print(f"    {zone}: {count}")
        print(f"  Total Rows: {stats['total_rows']:,}")
        print(f"  Total Size: {stats['total_size_gb']} GB")
        print(f"  Ingestion Jobs: {stats['ingestion_jobs']}")
        print(f"  Quality Checks: {stats['quality_checks']}")
        print(f"  Lineage Nodes: {stats['lineage_nodes']}")
        
        # Dashboard
        print("\n📋 Data Lake Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │                   Data Lake Overview                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Schemas:            {stats['schemas']:>10}                        │")
        print(f"  │ Tables:             {stats['tables']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Raw Zone:           {stats['tables_by_zone']['raw']:>10}                        │")
        print(f"  │ Bronze Zone:        {stats['tables_by_zone']['bronze']:>10}                        │")
        print(f"  │ Silver Zone:        {stats['tables_by_zone']['silver']:>10}                        │")
        print(f"  │ Gold Zone:          {stats['tables_by_zone']['gold']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Rows:     {stats['total_rows']:>14,}                    │")
        print(f"  │ Total Size:         {stats['total_size_gb']:>10} GB                   │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Ingestion Jobs:     {stats['ingestion_jobs']:>10}                        │")
        print(f"  │ Quality Checks:     {stats['quality_checks']:>10}                        │")
        print(f"  │ Lineage Nodes:      {stats['lineage_nodes']:>10}                        │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Data Lake Platform initialized!")
    print("=" * 60)
