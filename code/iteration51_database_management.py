#!/usr/bin/env python3
"""
Server Init - Iteration 51: Database Management Platform
Платформа управления базами данных

Функционал:
- Multi-Engine Support - поддержка нескольких СУБД
- Connection Pooling - пулинг соединений
- Query Optimization - оптимизация запросов
- Schema Management - управление схемами
- Migration Engine - движок миграций
- Replication Management - управление репликацией
- Performance Monitoring - мониторинг производительности
- Automated Scaling - автоматическое масштабирование
"""

import json
import asyncio
import hashlib
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Tuple
from enum import Enum
from abc import ABC, abstractmethod
import random
from collections import defaultdict
import uuid


class DatabaseEngine(Enum):
    """Движок базы данных"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MARIADB = "mariadb"
    MONGODB = "mongodb"
    REDIS = "redis"
    ELASTICSEARCH = "elasticsearch"
    CASSANDRA = "cassandra"
    CLICKHOUSE = "clickhouse"


class InstanceStatus(Enum):
    """Статус инстанса"""
    CREATING = "creating"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    MAINTENANCE = "maintenance"
    FAILED = "failed"
    DEGRADED = "degraded"


class ReplicaRole(Enum):
    """Роль реплики"""
    PRIMARY = "primary"
    REPLICA = "replica"
    STANDBY = "standby"
    ARBITER = "arbiter"


class MigrationStatus(Enum):
    """Статус миграции"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class QueryType(Enum):
    """Тип запроса"""
    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    DDL = "ddl"
    ADMIN = "admin"


@dataclass
class DatabaseInstance:
    """Инстанс базы данных"""
    instance_id: str
    name: str
    engine: DatabaseEngine
    
    # Конфигурация
    version: str = ""
    host: str = ""
    port: int = 0
    
    # Ресурсы
    cpu_cores: int = 2
    memory_gb: int = 4
    storage_gb: int = 100
    iops: int = 3000
    
    # Репликация
    role: ReplicaRole = ReplicaRole.PRIMARY
    primary_id: Optional[str] = None
    replicas: List[str] = field(default_factory=list)
    
    # Статус
    status: InstanceStatus = InstanceStatus.CREATING
    
    # Метрики
    connections_current: int = 0
    connections_max: int = 100
    storage_used_gb: float = 0.0
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    
    # Теги
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class ConnectionPool:
    """Пул соединений"""
    pool_id: str
    instance_id: str
    name: str
    
    # Конфигурация
    min_connections: int = 5
    max_connections: int = 50
    idle_timeout_seconds: int = 300
    
    # Статистика
    active_connections: int = 0
    idle_connections: int = 0
    waiting_requests: int = 0
    
    # Метрики
    total_connections_created: int = 0
    total_connections_closed: int = 0
    avg_wait_time_ms: float = 0.0


@dataclass
class DatabaseUser:
    """Пользователь базы данных"""
    user_id: str
    username: str
    instance_id: str
    
    # Права
    databases: List[str] = field(default_factory=list)
    privileges: List[str] = field(default_factory=list)
    
    # Лимиты
    max_connections: int = 10
    max_queries_per_hour: int = 0  # 0 = unlimited
    
    # Статус
    enabled: bool = True
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None


@dataclass
class Schema:
    """Схема базы данных"""
    schema_id: str
    name: str
    instance_id: str
    
    # Объекты
    tables_count: int = 0
    indexes_count: int = 0
    views_count: int = 0
    procedures_count: int = 0
    
    # Размер
    size_mb: float = 0.0
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Migration:
    """Миграция"""
    migration_id: str
    version: str
    name: str
    
    # Скрипты
    up_script: str = ""
    down_script: str = ""
    
    # Checksum
    checksum: str = ""
    
    # Статус
    status: MigrationStatus = MigrationStatus.PENDING
    
    # Время
    applied_at: Optional[datetime] = None
    execution_time_ms: int = 0
    
    # Ошибки
    error_message: Optional[str] = None


@dataclass
class QueryStats:
    """Статистика запроса"""
    query_id: str
    query_hash: str
    query_type: QueryType
    
    # Текст запроса (нормализованный)
    query_normalized: str = ""
    
    # Статистика
    calls_count: int = 0
    total_time_ms: float = 0.0
    mean_time_ms: float = 0.0
    min_time_ms: float = 0.0
    max_time_ms: float = 0.0
    
    # Ресурсы
    rows_returned: int = 0
    rows_affected: int = 0
    
    # Буферы
    shared_blks_hit: int = 0
    shared_blks_read: int = 0
    
    # Время последнего выполнения
    last_executed: Optional[datetime] = None


@dataclass
class SlowQuery:
    """Медленный запрос"""
    query_id: str
    instance_id: str
    
    # Запрос
    query_text: str = ""
    query_type: QueryType = QueryType.SELECT
    
    # Время
    execution_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Контекст
    database: str = ""
    user: str = ""
    
    # План выполнения
    execution_plan: Optional[Dict[str, Any]] = None
    
    # Рекомендации
    recommendations: List[str] = field(default_factory=list)


@dataclass
class Index:
    """Индекс"""
    index_id: str
    name: str
    table_name: str
    instance_id: str
    
    # Конфигурация
    columns: List[str] = field(default_factory=list)
    index_type: str = "btree"  # btree, hash, gin, gist
    unique: bool = False
    
    # Статистика
    size_mb: float = 0.0
    scans_count: int = 0
    tuples_read: int = 0
    tuples_fetched: int = 0
    
    # Bloat
    bloat_percent: float = 0.0


class DatabaseManager:
    """Менеджер баз данных"""
    
    def __init__(self):
        self.instances: Dict[str, DatabaseInstance] = {}
        self.pools: Dict[str, ConnectionPool] = {}
        self.users: Dict[str, DatabaseUser] = {}
        self.schemas: Dict[str, Schema] = {}
        
    async def create_instance(self, name: str, engine: DatabaseEngine,
                               **kwargs) -> DatabaseInstance:
        """Создание инстанса"""
        instance = DatabaseInstance(
            instance_id=f"db_{uuid.uuid4().hex[:8]}",
            name=name,
            engine=engine,
            **kwargs
        )
        
        # Настройка порта по умолчанию
        default_ports = {
            DatabaseEngine.POSTGRESQL: 5432,
            DatabaseEngine.MYSQL: 3306,
            DatabaseEngine.MARIADB: 3306,
            DatabaseEngine.MONGODB: 27017,
            DatabaseEngine.REDIS: 6379,
            DatabaseEngine.ELASTICSEARCH: 9200,
            DatabaseEngine.CASSANDRA: 9042,
            DatabaseEngine.CLICKHOUSE: 8123
        }
        
        if not instance.port:
            instance.port = default_ports.get(engine, 5432)
            
        # Симуляция создания
        await asyncio.sleep(0.1)
        
        instance.status = InstanceStatus.RUNNING
        instance.host = f"{name}.db.internal"
        
        self.instances[instance.instance_id] = instance
        return instance
        
    async def create_replica(self, primary_id: str) -> DatabaseInstance:
        """Создание реплики"""
        primary = self.instances.get(primary_id)
        if not primary:
            raise ValueError("Primary not found")
            
        replica_name = f"{primary.name}-replica-{len(primary.replicas) + 1}"
        
        replica = await self.create_instance(
            name=replica_name,
            engine=primary.engine,
            version=primary.version,
            cpu_cores=primary.cpu_cores,
            memory_gb=primary.memory_gb,
            storage_gb=primary.storage_gb
        )
        
        replica.role = ReplicaRole.REPLICA
        replica.primary_id = primary_id
        
        primary.replicas.append(replica.instance_id)
        
        return replica
        
    async def promote_replica(self, replica_id: str) -> DatabaseInstance:
        """Промоушен реплики"""
        replica = self.instances.get(replica_id)
        if not replica or replica.role != ReplicaRole.REPLICA:
            raise ValueError("Invalid replica")
            
        # Симуляция промоушена
        await asyncio.sleep(0.1)
        
        replica.role = ReplicaRole.PRIMARY
        old_primary_id = replica.primary_id
        replica.primary_id = None
        
        # Обновление старого primary
        if old_primary_id and old_primary_id in self.instances:
            old_primary = self.instances[old_primary_id]
            old_primary.replicas.remove(replica_id)
            old_primary.role = ReplicaRole.STANDBY
            
        return replica
        
    def create_pool(self, instance_id: str, name: str,
                     **kwargs) -> ConnectionPool:
        """Создание пула соединений"""
        pool = ConnectionPool(
            pool_id=f"pool_{uuid.uuid4().hex[:8]}",
            instance_id=instance_id,
            name=name,
            **kwargs
        )
        
        # Инициализация начальных соединений
        pool.idle_connections = pool.min_connections
        pool.total_connections_created = pool.min_connections
        
        self.pools[pool.pool_id] = pool
        return pool
        
    def get_connection(self, pool_id: str) -> Optional[Dict[str, Any]]:
        """Получение соединения из пула"""
        pool = self.pools.get(pool_id)
        if not pool:
            return None
            
        if pool.idle_connections > 0:
            pool.idle_connections -= 1
            pool.active_connections += 1
            return {"connection_id": f"conn_{uuid.uuid4().hex[:8]}", "pool_id": pool_id}
            
        if pool.active_connections < pool.max_connections:
            pool.active_connections += 1
            pool.total_connections_created += 1
            return {"connection_id": f"conn_{uuid.uuid4().hex[:8]}", "pool_id": pool_id}
            
        pool.waiting_requests += 1
        return None
        
    def release_connection(self, pool_id: str):
        """Возврат соединения в пул"""
        pool = self.pools.get(pool_id)
        if not pool:
            return
            
        pool.active_connections -= 1
        pool.idle_connections += 1
        
        if pool.waiting_requests > 0:
            pool.waiting_requests -= 1
            
    def create_user(self, instance_id: str, username: str,
                     **kwargs) -> DatabaseUser:
        """Создание пользователя"""
        user = DatabaseUser(
            user_id=f"user_{uuid.uuid4().hex[:8]}",
            username=username,
            instance_id=instance_id,
            **kwargs
        )
        
        self.users[user.user_id] = user
        return user
        
    def get_instance_stats(self, instance_id: str) -> Dict[str, Any]:
        """Статистика инстанса"""
        instance = self.instances.get(instance_id)
        if not instance:
            return {}
            
        # Симуляция метрик
        return {
            "instance_id": instance_id,
            "status": instance.status.value,
            "connections": {
                "current": random.randint(10, instance.connections_max),
                "max": instance.connections_max,
                "utilization": random.uniform(0.3, 0.8)
            },
            "storage": {
                "total_gb": instance.storage_gb,
                "used_gb": random.uniform(10, instance.storage_gb * 0.7),
                "utilization": random.uniform(0.2, 0.7)
            },
            "performance": {
                "queries_per_second": random.uniform(100, 5000),
                "transactions_per_second": random.uniform(50, 1000),
                "avg_query_time_ms": random.uniform(1, 50)
            },
            "replication": {
                "role": instance.role.value,
                "replicas": len(instance.replicas),
                "lag_bytes": random.randint(0, 10000) if instance.role == ReplicaRole.REPLICA else 0
            }
        }


class MigrationEngine:
    """Движок миграций"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.migrations: Dict[str, List[Migration]] = defaultdict(list)
        self.applied_versions: Dict[str, Set[str]] = defaultdict(set)
        
    def register_migration(self, instance_id: str, version: str,
                            name: str, up_script: str,
                            down_script: str = "") -> Migration:
        """Регистрация миграции"""
        migration = Migration(
            migration_id=f"mig_{uuid.uuid4().hex[:8]}",
            version=version,
            name=name,
            up_script=up_script,
            down_script=down_script,
            checksum=hashlib.md5(up_script.encode()).hexdigest()
        )
        
        self.migrations[instance_id].append(migration)
        return migration
        
    async def apply_migration(self, instance_id: str, version: str) -> Migration:
        """Применение миграции"""
        migrations = self.migrations.get(instance_id, [])
        migration = next((m for m in migrations if m.version == version), None)
        
        if not migration:
            raise ValueError("Migration not found")
            
        if version in self.applied_versions[instance_id]:
            raise ValueError("Migration already applied")
            
        migration.status = MigrationStatus.RUNNING
        
        try:
            # Симуляция выполнения
            start_time = time.time()
            await asyncio.sleep(0.1)
            
            migration.status = MigrationStatus.COMPLETED
            migration.applied_at = datetime.now()
            migration.execution_time_ms = int((time.time() - start_time) * 1000)
            
            self.applied_versions[instance_id].add(version)
            
        except Exception as e:
            migration.status = MigrationStatus.FAILED
            migration.error_message = str(e)
            
        return migration
        
    async def rollback_migration(self, instance_id: str, version: str) -> Migration:
        """Откат миграции"""
        migrations = self.migrations.get(instance_id, [])
        migration = next((m for m in migrations if m.version == version), None)
        
        if not migration:
            raise ValueError("Migration not found")
            
        if version not in self.applied_versions[instance_id]:
            raise ValueError("Migration not applied")
            
        if not migration.down_script:
            raise ValueError("No rollback script")
            
        # Симуляция отката
        await asyncio.sleep(0.1)
        
        migration.status = MigrationStatus.ROLLED_BACK
        self.applied_versions[instance_id].remove(version)
        
        return migration
        
    def get_pending_migrations(self, instance_id: str) -> List[Migration]:
        """Получение ожидающих миграций"""
        migrations = self.migrations.get(instance_id, [])
        applied = self.applied_versions.get(instance_id, set())
        
        return [m for m in migrations if m.version not in applied]


class QueryAnalyzer:
    """Анализатор запросов"""
    
    def __init__(self):
        self.query_stats: Dict[str, QueryStats] = {}
        self.slow_queries: List[SlowQuery] = []
        self.slow_query_threshold_ms: float = 1000.0
        
    def analyze_query(self, query: str, execution_time_ms: float,
                       **kwargs) -> Dict[str, Any]:
        """Анализ запроса"""
        # Нормализация запроса
        normalized = self._normalize_query(query)
        query_hash = hashlib.md5(normalized.encode()).hexdigest()
        
        # Определение типа
        query_type = self._detect_query_type(query)
        
        # Обновление статистики
        if query_hash not in self.query_stats:
            self.query_stats[query_hash] = QueryStats(
                query_id=f"query_{uuid.uuid4().hex[:8]}",
                query_hash=query_hash,
                query_type=query_type,
                query_normalized=normalized[:500]
            )
            
        stats = self.query_stats[query_hash]
        stats.calls_count += 1
        stats.total_time_ms += execution_time_ms
        stats.mean_time_ms = stats.total_time_ms / stats.calls_count
        stats.min_time_ms = min(stats.min_time_ms or execution_time_ms, execution_time_ms)
        stats.max_time_ms = max(stats.max_time_ms, execution_time_ms)
        stats.last_executed = datetime.now()
        
        # Проверка на медленный запрос
        recommendations = []
        if execution_time_ms > self.slow_query_threshold_ms:
            slow_query = SlowQuery(
                query_id=f"slow_{uuid.uuid4().hex[:8]}",
                instance_id=kwargs.get("instance_id", ""),
                query_text=query[:1000],
                query_type=query_type,
                execution_time_ms=execution_time_ms,
                database=kwargs.get("database", ""),
                user=kwargs.get("user", "")
            )
            
            recommendations = self._generate_recommendations(query, query_type)
            slow_query.recommendations = recommendations
            
            self.slow_queries.append(slow_query)
            
        return {
            "query_hash": query_hash,
            "query_type": query_type.value,
            "execution_time_ms": execution_time_ms,
            "is_slow": execution_time_ms > self.slow_query_threshold_ms,
            "recommendations": recommendations
        }
        
    def _normalize_query(self, query: str) -> str:
        """Нормализация запроса"""
        # Упрощённая нормализация
        import re
        query = query.strip().lower()
        query = re.sub(r'\s+', ' ', query)
        query = re.sub(r"'[^']*'", "'?'", query)
        query = re.sub(r'\d+', '?', query)
        return query
        
    def _detect_query_type(self, query: str) -> QueryType:
        """Определение типа запроса"""
        query_upper = query.strip().upper()
        
        if query_upper.startswith("SELECT"):
            return QueryType.SELECT
        elif query_upper.startswith("INSERT"):
            return QueryType.INSERT
        elif query_upper.startswith("UPDATE"):
            return QueryType.UPDATE
        elif query_upper.startswith("DELETE"):
            return QueryType.DELETE
        elif query_upper.startswith(("CREATE", "ALTER", "DROP")):
            return QueryType.DDL
        else:
            return QueryType.ADMIN
            
    def _generate_recommendations(self, query: str, query_type: QueryType) -> List[str]:
        """Генерация рекомендаций"""
        recommendations = []
        query_lower = query.lower()
        
        if "select *" in query_lower:
            recommendations.append("Избегайте SELECT *, укажите конкретные колонки")
            
        if query_type == QueryType.SELECT and "where" not in query_lower:
            recommendations.append("Добавьте WHERE для фильтрации данных")
            
        if "like '%'" in query_lower or "like '%" in query_lower:
            recommendations.append("LIKE с ведущим % не использует индекс")
            
        if query_lower.count("join") > 3:
            recommendations.append("Слишком много JOIN, рассмотрите денормализацию")
            
        if not recommendations:
            recommendations.append("Рассмотрите создание индекса")
            
        return recommendations
        
    def get_top_queries(self, limit: int = 10, sort_by: str = "total_time") -> List[QueryStats]:
        """Получение топ запросов"""
        stats = list(self.query_stats.values())
        
        if sort_by == "total_time":
            stats.sort(key=lambda x: x.total_time_ms, reverse=True)
        elif sort_by == "calls":
            stats.sort(key=lambda x: x.calls_count, reverse=True)
        elif sort_by == "mean_time":
            stats.sort(key=lambda x: x.mean_time_ms, reverse=True)
            
        return stats[:limit]


class IndexAdvisor:
    """Советник по индексам"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.indexes: Dict[str, List[Index]] = defaultdict(list)
        
    def create_index(self, instance_id: str, table_name: str,
                      columns: List[str], **kwargs) -> Index:
        """Создание индекса"""
        index_name = kwargs.get("name", f"idx_{table_name}_{'_'.join(columns)}")
        
        index = Index(
            index_id=f"idx_{uuid.uuid4().hex[:8]}",
            name=index_name,
            table_name=table_name,
            instance_id=instance_id,
            columns=columns,
            **kwargs
        )
        
        self.indexes[instance_id].append(index)
        return index
        
    def analyze_index_usage(self, instance_id: str) -> List[Dict[str, Any]]:
        """Анализ использования индексов"""
        indexes = self.indexes.get(instance_id, [])
        recommendations = []
        
        for index in indexes:
            # Симуляция метрик
            index.scans_count = random.randint(0, 10000)
            index.size_mb = random.uniform(0.1, 100)
            index.bloat_percent = random.uniform(0, 30)
            
            analysis = {
                "index_id": index.index_id,
                "name": index.name,
                "table": index.table_name,
                "scans": index.scans_count,
                "size_mb": round(index.size_mb, 2),
                "bloat_percent": round(index.bloat_percent, 1)
            }
            
            # Рекомендации
            if index.scans_count == 0:
                analysis["recommendation"] = "Индекс не используется, рассмотрите удаление"
                analysis["priority"] = "high"
            elif index.bloat_percent > 20:
                analysis["recommendation"] = "Высокий bloat, рекомендуется REINDEX"
                analysis["priority"] = "medium"
            else:
                analysis["recommendation"] = None
                analysis["priority"] = "low"
                
            recommendations.append(analysis)
            
        return sorted(recommendations, key=lambda x: x["scans"])
        
    def suggest_indexes(self, instance_id: str, query_analyzer: QueryAnalyzer) -> List[Dict[str, Any]]:
        """Предложение индексов"""
        suggestions = []
        
        slow_queries = query_analyzer.slow_queries
        
        for slow_query in slow_queries[-10:]:  # Последние 10 медленных запросов
            suggestion = {
                "query_id": slow_query.query_id,
                "query_preview": slow_query.query_text[:100],
                "suggested_index": {
                    "table": "detected_table",
                    "columns": ["detected_column"],
                    "type": "btree"
                },
                "estimated_improvement": f"{random.randint(20, 80)}%"
            }
            
            suggestions.append(suggestion)
            
        return suggestions


class DatabasePlatform:
    """Платформа управления базами данных"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.migration_engine = MigrationEngine(self.db_manager)
        self.query_analyzer = QueryAnalyzer()
        self.index_advisor = IndexAdvisor(self.db_manager)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика платформы"""
        instances = self.db_manager.instances
        
        by_engine = defaultdict(int)
        by_role = defaultdict(int)
        
        for instance in instances.values():
            by_engine[instance.engine.value] += 1
            by_role[instance.role.value] += 1
            
        return {
            "instances": {
                "total": len(instances),
                "by_engine": dict(by_engine),
                "by_role": dict(by_role),
                "running": len([i for i in instances.values() if i.status == InstanceStatus.RUNNING])
            },
            "connection_pools": len(self.db_manager.pools),
            "users": len(self.db_manager.users),
            "queries_analyzed": len(self.query_analyzer.query_stats),
            "slow_queries": len(self.query_analyzer.slow_queries)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 51: Database Management Platform")
    print("=" * 60)
    
    async def demo():
        # Создание платформы
        platform = DatabasePlatform()
        print("✓ Database Platform created")
        
        # Создание инстансов
        print("\n🗄️ Creating database instances...")
        
        pg_primary = await platform.db_manager.create_instance(
            name="postgres-prod",
            engine=DatabaseEngine.POSTGRESQL,
            version="15.4",
            cpu_cores=4,
            memory_gb=16,
            storage_gb=500
        )
        print(f"  ✓ PostgreSQL Primary: {pg_primary.name}")
        print(f"    Host: {pg_primary.host}:{pg_primary.port}")
        
        pg_replica = await platform.db_manager.create_replica(pg_primary.instance_id)
        print(f"  ✓ PostgreSQL Replica: {pg_replica.name}")
        
        mysql_instance = await platform.db_manager.create_instance(
            name="mysql-analytics",
            engine=DatabaseEngine.MYSQL,
            version="8.0",
            cpu_cores=8,
            memory_gb=32,
            storage_gb=1000
        )
        print(f"  ✓ MySQL: {mysql_instance.name}")
        
        redis_instance = await platform.db_manager.create_instance(
            name="redis-cache",
            engine=DatabaseEngine.REDIS,
            version="7.0",
            cpu_cores=2,
            memory_gb=8,
            storage_gb=50
        )
        print(f"  ✓ Redis: {redis_instance.name}")
        
        # Connection pools
        print("\n🔗 Creating connection pools...")
        
        pg_pool = platform.db_manager.create_pool(
            instance_id=pg_primary.instance_id,
            name="pg-pool-main",
            min_connections=10,
            max_connections=100
        )
        print(f"  ✓ Pool: {pg_pool.name}")
        print(f"    Min/Max: {pg_pool.min_connections}/{pg_pool.max_connections}")
        
        # Получение соединения
        conn = platform.db_manager.get_connection(pg_pool.pool_id)
        print(f"  ✓ Got connection: {conn['connection_id']}")
        
        # Users
        print("\n👤 Creating database users...")
        
        admin_user = platform.db_manager.create_user(
            instance_id=pg_primary.instance_id,
            username="admin",
            privileges=["ALL"],
            databases=["*"]
        )
        print(f"  ✓ User: {admin_user.username}")
        
        app_user = platform.db_manager.create_user(
            instance_id=pg_primary.instance_id,
            username="app_user",
            privileges=["SELECT", "INSERT", "UPDATE"],
            databases=["production"],
            max_connections=20
        )
        print(f"  ✓ User: {app_user.username}")
        
        # Migrations
        print("\n📦 Managing migrations...")
        
        mig1 = platform.migration_engine.register_migration(
            instance_id=pg_primary.instance_id,
            version="001",
            name="create_users_table",
            up_script="CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR(255));",
            down_script="DROP TABLE users;"
        )
        print(f"  ✓ Registered: {mig1.version} - {mig1.name}")
        
        mig2 = platform.migration_engine.register_migration(
            instance_id=pg_primary.instance_id,
            version="002",
            name="add_email_column",
            up_script="ALTER TABLE users ADD COLUMN email VARCHAR(255);",
            down_script="ALTER TABLE users DROP COLUMN email;"
        )
        print(f"  ✓ Registered: {mig2.version} - {mig2.name}")
        
        # Apply migrations
        await platform.migration_engine.apply_migration(pg_primary.instance_id, "001")
        print(f"  ✓ Applied migration 001")
        
        await platform.migration_engine.apply_migration(pg_primary.instance_id, "002")
        print(f"  ✓ Applied migration 002")
        
        # Query analysis
        print("\n🔍 Analyzing queries...")
        
        queries = [
            ("SELECT * FROM users WHERE id = 1", 5.2),
            ("SELECT name, email FROM users WHERE email LIKE '%@example.com'", 1500.0),
            ("SELECT u.*, o.* FROM users u JOIN orders o ON u.id = o.user_id WHERE u.status = 'active'", 2500.0),
            ("INSERT INTO users (name, email) VALUES ('Test', 'test@test.com')", 3.1),
            ("SELECT * FROM large_table", 5000.0)
        ]
        
        for query, exec_time in queries:
            result = platform.query_analyzer.analyze_query(
                query,
                exec_time,
                instance_id=pg_primary.instance_id,
                database="production"
            )
            
            if result["is_slow"]:
                print(f"  ⚠️ Slow query detected ({exec_time:.1f}ms)")
                for rec in result["recommendations"]:
                    print(f"     → {rec}")
                    
        # Top queries
        print("\n📊 Top queries by total time:")
        
        top_queries = platform.query_analyzer.get_top_queries(limit=3, sort_by="total_time")
        for i, q in enumerate(top_queries, 1):
            print(f"  {i}. {q.query_normalized[:50]}...")
            print(f"     Calls: {q.calls_count}, Total: {q.total_time_ms:.1f}ms")
            
        # Index management
        print("\n📇 Index management...")
        
        idx1 = platform.index_advisor.create_index(
            instance_id=pg_primary.instance_id,
            table_name="users",
            columns=["email"],
            unique=True
        )
        print(f"  ✓ Created index: {idx1.name}")
        
        idx2 = platform.index_advisor.create_index(
            instance_id=pg_primary.instance_id,
            table_name="orders",
            columns=["user_id", "status"]
        )
        print(f"  ✓ Created index: {idx2.name}")
        
        # Index analysis
        print("\n  Index usage analysis:")
        index_analysis = platform.index_advisor.analyze_index_usage(pg_primary.instance_id)
        
        for analysis in index_analysis:
            print(f"    {analysis['name']}: {analysis['scans']} scans, {analysis['size_mb']} MB")
            if analysis["recommendation"]:
                print(f"      → {analysis['recommendation']}")
                
        # Index suggestions
        print("\n  Index suggestions:")
        suggestions = platform.index_advisor.suggest_indexes(
            pg_primary.instance_id,
            platform.query_analyzer
        )
        
        for sug in suggestions[:3]:
            print(f"    {sug['suggested_index']['columns']} on {sug['suggested_index']['table']}")
            print(f"    Est. improvement: {sug['estimated_improvement']}")
            
        # Instance stats
        print("\n📈 Instance statistics:")
        
        stats = platform.db_manager.get_instance_stats(pg_primary.instance_id)
        print(f"\n  PostgreSQL Primary:")
        print(f"    Connections: {stats['connections']['current']}/{stats['connections']['max']}")
        print(f"    Storage: {stats['storage']['used_gb']:.1f}/{stats['storage']['total_gb']} GB")
        print(f"    QPS: {stats['performance']['queries_per_second']:.1f}")
        print(f"    Avg query time: {stats['performance']['avg_query_time_ms']:.1f}ms")
        
        # Platform statistics
        print("\n📊 Platform Statistics:")
        platform_stats = platform.get_statistics()
        
        print(f"  Instances: {platform_stats['instances']['total']}")
        print(f"    By engine: {platform_stats['instances']['by_engine']}")
        print(f"    By role: {platform_stats['instances']['by_role']}")
        print(f"  Connection pools: {platform_stats['connection_pools']}")
        print(f"  Users: {platform_stats['users']}")
        print(f"  Queries analyzed: {platform_stats['queries_analyzed']}")
        print(f"  Slow queries: {platform_stats['slow_queries']}")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Database Management Platform initialized!")
    print("=" * 60)
