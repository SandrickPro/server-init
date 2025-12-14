#!/usr/bin/env python3
"""
Server Init - Iteration 117: Database Migration Platform
Платформа миграции баз данных

Функционал:
- Schema Migration - миграция схемы
- Data Migration - миграция данных
- Version Control - контроль версий
- Rollback Support - поддержка отката
- Multi-Database - поддержка разных СУБД
- Validation - валидация
- Dependency Management - управление зависимостями
- Dry Run - пробный запуск
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
import hashlib


class DatabaseType(Enum):
    """Тип базы данных"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    SQLITE = "sqlite"
    MSSQL = "mssql"
    ORACLE = "oracle"


class MigrationStatus(Enum):
    """Статус миграции"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class MigrationType(Enum):
    """Тип миграции"""
    SCHEMA = "schema"
    DATA = "data"
    SEED = "seed"
    INDEX = "index"
    CONSTRAINT = "constraint"


class OperationType(Enum):
    """Тип операции"""
    CREATE_TABLE = "create_table"
    ALTER_TABLE = "alter_table"
    DROP_TABLE = "drop_table"
    ADD_COLUMN = "add_column"
    DROP_COLUMN = "drop_column"
    MODIFY_COLUMN = "modify_column"
    ADD_INDEX = "add_index"
    DROP_INDEX = "drop_index"
    ADD_CONSTRAINT = "add_constraint"
    DROP_CONSTRAINT = "drop_constraint"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"


@dataclass
class DatabaseConnection:
    """Подключение к БД"""
    connection_id: str
    name: str = ""
    
    # Type
    db_type: DatabaseType = DatabaseType.POSTGRESQL
    
    # Connection
    host: str = "localhost"
    port: int = 5432
    database: str = ""
    username: str = ""
    
    # Status
    connected: bool = False
    
    # Version
    db_version: str = ""


@dataclass
class MigrationOperation:
    """Операция миграции"""
    operation_id: str
    operation_type: OperationType = OperationType.CREATE_TABLE
    
    # Target
    table_name: str = ""
    column_name: str = ""
    
    # SQL
    up_sql: str = ""
    down_sql: str = ""
    
    # Data
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    executed: bool = False
    execution_time_ms: float = 0.0


@dataclass
class Migration:
    """Миграция"""
    migration_id: str
    version: str = ""
    name: str = ""
    description: str = ""
    
    # Type
    migration_type: MigrationType = MigrationType.SCHEMA
    
    # Operations
    operations: List[MigrationOperation] = field(default_factory=list)
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)
    
    # Status
    status: MigrationStatus = MigrationStatus.PENDING
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    executed_at: Optional[datetime] = None
    rolled_back_at: Optional[datetime] = None
    
    # Metrics
    execution_time_ms: float = 0.0
    rows_affected: int = 0
    
    # Checksums
    checksum: str = ""


@dataclass
class MigrationPlan:
    """План миграции"""
    plan_id: str
    name: str = ""
    
    # Migrations
    migrations: List[str] = field(default_factory=list)
    
    # Order
    execution_order: List[str] = field(default_factory=list)
    
    # Status
    status: str = "draft"  # draft, approved, executing, completed
    
    # Validation
    validated: bool = False
    validation_errors: List[str] = field(default_factory=list)


@dataclass
class MigrationHistory:
    """История миграций"""
    history_id: str
    migration_id: str = ""
    version: str = ""
    
    # Action
    action: str = ""  # apply, rollback
    
    # Status
    success: bool = True
    error_message: str = ""
    
    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    duration_ms: float = 0.0
    
    # User
    executed_by: str = ""


class ConnectionManager:
    """Менеджер подключений"""
    
    def __init__(self):
        self.connections: Dict[str, DatabaseConnection] = {}
        
    def register(self, name: str, db_type: DatabaseType,
                  host: str, port: int, database: str,
                  **kwargs) -> DatabaseConnection:
        """Регистрация подключения"""
        conn = DatabaseConnection(
            connection_id=f"conn_{uuid.uuid4().hex[:8]}",
            name=name,
            db_type=db_type,
            host=host,
            port=port,
            database=database,
            **kwargs
        )
        self.connections[conn.connection_id] = conn
        return conn
        
    def connect(self, connection_id: str) -> bool:
        """Подключение"""
        conn = self.connections.get(connection_id)
        if not conn:
            return False
            
        # Simulate connection
        conn.connected = random.random() > 0.05
        if conn.connected:
            versions = {
                DatabaseType.POSTGRESQL: "15.3",
                DatabaseType.MYSQL: "8.0.33",
                DatabaseType.MONGODB: "6.0",
                DatabaseType.SQLITE: "3.42",
                DatabaseType.MSSQL: "2022",
                DatabaseType.ORACLE: "21c"
            }
            conn.db_version = versions.get(conn.db_type, "unknown")
            
        return conn.connected


class MigrationBuilder:
    """Построитель миграций"""
    
    def __init__(self):
        self.migrations: Dict[str, Migration] = {}
        
    def create(self, version: str, name: str,
                migration_type: MigrationType = MigrationType.SCHEMA,
                **kwargs) -> Migration:
        """Создание миграции"""
        migration = Migration(
            migration_id=f"mig_{uuid.uuid4().hex[:8]}",
            version=version,
            name=name,
            migration_type=migration_type,
            **kwargs
        )
        
        # Calculate checksum
        content = f"{version}:{name}:{migration_type.value}"
        migration.checksum = hashlib.md5(content.encode()).hexdigest()[:8]
        
        self.migrations[migration.migration_id] = migration
        return migration
        
    def add_operation(self, migration_id: str, 
                       operation_type: OperationType,
                       table_name: str = "",
                       up_sql: str = "",
                       down_sql: str = "",
                       **kwargs) -> Optional[MigrationOperation]:
        """Добавление операции"""
        migration = self.migrations.get(migration_id)
        if not migration:
            return None
            
        operation = MigrationOperation(
            operation_id=f"op_{uuid.uuid4().hex[:8]}",
            operation_type=operation_type,
            table_name=table_name,
            up_sql=up_sql,
            down_sql=down_sql,
            **kwargs
        )
        migration.operations.append(operation)
        return operation


class MigrationValidator:
    """Валидатор миграций"""
    
    def validate(self, migration: Migration) -> List[str]:
        """Валидация миграции"""
        errors = []
        
        # Check version
        if not migration.version:
            errors.append("Migration version is required")
            
        # Check name
        if not migration.name:
            errors.append("Migration name is required")
            
        # Check operations
        if not migration.operations:
            errors.append("Migration must have at least one operation")
            
        # Check SQL
        for op in migration.operations:
            if not op.up_sql and op.operation_type != OperationType.INSERT:
                errors.append(f"Operation {op.operation_id} missing up_sql")
                
        return errors
        
    def validate_plan(self, plan: MigrationPlan, 
                       migrations: Dict[str, Migration]) -> List[str]:
        """Валидация плана"""
        errors = []
        
        # Check dependencies
        for mig_id in plan.migrations:
            migration = migrations.get(mig_id)
            if not migration:
                errors.append(f"Migration {mig_id} not found")
                continue
                
            for dep in migration.depends_on:
                if dep not in plan.migrations:
                    errors.append(f"Dependency {dep} not in plan")
                    
        # Check circular dependencies
        visited = set()
        for mig_id in plan.migrations:
            if self._has_cycle(mig_id, migrations, visited, set()):
                errors.append(f"Circular dependency detected for {mig_id}")
                
        return errors
        
    def _has_cycle(self, mig_id: str, migrations: Dict[str, Migration],
                    visited: Set[str], path: Set[str]) -> bool:
        """Проверка циклов"""
        if mig_id in path:
            return True
        if mig_id in visited:
            return False
            
        visited.add(mig_id)
        path.add(mig_id)
        
        migration = migrations.get(mig_id)
        if migration:
            for dep in migration.depends_on:
                if self._has_cycle(dep, migrations, visited, path):
                    return True
                    
        path.remove(mig_id)
        return False


class MigrationExecutor:
    """Исполнитель миграций"""
    
    def __init__(self, builder: MigrationBuilder):
        self.builder = builder
        self.history: List[MigrationHistory] = []
        
    async def execute(self, migration_id: str, 
                       dry_run: bool = False) -> Dict[str, Any]:
        """Выполнение миграции"""
        migration = self.builder.migrations.get(migration_id)
        if not migration:
            return {"status": "error", "message": "Migration not found"}
            
        start_time = datetime.now()
        migration.status = MigrationStatus.RUNNING
        
        result = {
            "migration_id": migration_id,
            "version": migration.version,
            "dry_run": dry_run,
            "operations": []
        }
        
        try:
            for op in migration.operations:
                op_start = datetime.now()
                
                if not dry_run:
                    # Simulate execution
                    await asyncio.sleep(0.01)
                    
                    # Random failure (5% chance)
                    if random.random() < 0.05:
                        raise Exception(f"Operation {op.operation_type.value} failed")
                        
                op.executed = True
                op.execution_time_ms = (datetime.now() - op_start).total_seconds() * 1000
                
                result["operations"].append({
                    "operation": op.operation_type.value,
                    "table": op.table_name,
                    "time_ms": op.execution_time_ms
                })
                
            migration.status = MigrationStatus.COMPLETED
            migration.executed_at = datetime.now()
            migration.execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            migration.rows_affected = sum(random.randint(0, 100) for _ in migration.operations)
            
            result["status"] = "success"
            result["time_ms"] = migration.execution_time_ms
            result["rows_affected"] = migration.rows_affected
            
            # Record history
            if not dry_run:
                self._record_history(migration, "apply", True)
                
        except Exception as e:
            migration.status = MigrationStatus.FAILED
            result["status"] = "error"
            result["message"] = str(e)
            
            if not dry_run:
                self._record_history(migration, "apply", False, str(e))
                
        return result
        
    async def rollback(self, migration_id: str) -> Dict[str, Any]:
        """Откат миграции"""
        migration = self.builder.migrations.get(migration_id)
        if not migration:
            return {"status": "error", "message": "Migration not found"}
            
        if migration.status != MigrationStatus.COMPLETED:
            return {"status": "error", "message": "Can only rollback completed migrations"}
            
        start_time = datetime.now()
        
        try:
            # Execute down operations in reverse
            for op in reversed(migration.operations):
                if op.down_sql:
                    await asyncio.sleep(0.01)
                    
            migration.status = MigrationStatus.ROLLED_BACK
            migration.rolled_back_at = datetime.now()
            
            self._record_history(migration, "rollback", True)
            
            return {
                "status": "success",
                "migration_id": migration_id,
                "time_ms": (datetime.now() - start_time).total_seconds() * 1000
            }
            
        except Exception as e:
            self._record_history(migration, "rollback", False, str(e))
            return {"status": "error", "message": str(e)}
            
    def _record_history(self, migration: Migration, action: str,
                         success: bool, error: str = ""):
        """Запись истории"""
        history = MigrationHistory(
            history_id=f"hist_{uuid.uuid4().hex[:8]}",
            migration_id=migration.migration_id,
            version=migration.version,
            action=action,
            success=success,
            error_message=error,
            completed_at=datetime.now(),
            duration_ms=migration.execution_time_ms
        )
        self.history.append(history)


class MigrationPlanner:
    """Планировщик миграций"""
    
    def __init__(self, builder: MigrationBuilder, validator: MigrationValidator):
        self.builder = builder
        self.validator = validator
        self.plans: Dict[str, MigrationPlan] = {}
        
    def create_plan(self, name: str, migration_ids: List[str]) -> MigrationPlan:
        """Создание плана"""
        plan = MigrationPlan(
            plan_id=f"plan_{uuid.uuid4().hex[:8]}",
            name=name,
            migrations=migration_ids
        )
        
        # Determine execution order (topological sort)
        plan.execution_order = self._topological_sort(migration_ids)
        
        self.plans[plan.plan_id] = plan
        return plan
        
    def validate_plan(self, plan_id: str) -> MigrationPlan:
        """Валидация плана"""
        plan = self.plans.get(plan_id)
        if not plan:
            return None
            
        errors = self.validator.validate_plan(plan, self.builder.migrations)
        plan.validation_errors = errors
        plan.validated = len(errors) == 0
        
        return plan
        
    def _topological_sort(self, migration_ids: List[str]) -> List[str]:
        """Топологическая сортировка"""
        result = []
        visited = set()
        
        def visit(mig_id):
            if mig_id in visited:
                return
            visited.add(mig_id)
            
            migration = self.builder.migrations.get(mig_id)
            if migration:
                for dep in migration.depends_on:
                    if dep in migration_ids:
                        visit(dep)
                        
            result.append(mig_id)
            
        for mig_id in migration_ids:
            visit(mig_id)
            
        return result


class DatabaseMigrationPlatform:
    """Платформа миграции БД"""
    
    def __init__(self):
        self.connection_manager = ConnectionManager()
        self.builder = MigrationBuilder()
        self.validator = MigrationValidator()
        self.executor = MigrationExecutor(self.builder)
        self.planner = MigrationPlanner(self.builder, self.validator)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        migrations = list(self.builder.migrations.values())
        
        by_status = defaultdict(int)
        by_type = defaultdict(int)
        
        for m in migrations:
            by_status[m.status.value] += 1
            by_type[m.migration_type.value] += 1
            
        total_time = sum(m.execution_time_ms for m in migrations if m.executed_at)
        total_rows = sum(m.rows_affected for m in migrations if m.executed_at)
        
        return {
            "total_migrations": len(migrations),
            "migrations_by_status": dict(by_status),
            "migrations_by_type": dict(by_type),
            "total_connections": len(self.connection_manager.connections),
            "total_plans": len(self.planner.plans),
            "history_entries": len(self.executor.history),
            "total_execution_time_ms": total_time,
            "total_rows_affected": total_rows
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 117: Database Migration Platform")
    print("=" * 60)
    
    async def demo():
        platform = DatabaseMigrationPlatform()
        print("✓ Database Migration Platform created")
        
        # Register connections
        print("\n🔌 Registering Database Connections...")
        
        connections_data = [
            ("Production", DatabaseType.POSTGRESQL, "db.prod.example.com", 5432, "app_prod"),
            ("Staging", DatabaseType.POSTGRESQL, "db.stage.example.com", 5432, "app_stage"),
            ("Analytics", DatabaseType.MYSQL, "analytics.example.com", 3306, "analytics"),
            ("Cache", DatabaseType.MONGODB, "mongo.example.com", 27017, "cache")
        ]
        
        created_connections = []
        for name, db_type, host, port, database in connections_data:
            conn = platform.connection_manager.register(
                name, db_type, host, port, database
            )
            connected = platform.connection_manager.connect(conn.connection_id)
            created_connections.append(conn)
            
            status_icon = "✅" if connected else "❌"
            print(f"  {status_icon} {name} ({db_type.value}): {host}:{port}/{database}")
            if connected:
                print(f"     Version: {conn.db_version}")
                
        # Create migrations
        print("\n📝 Creating Migrations...")
        
        migrations_data = [
            ("20240101_001", "create_users_table", MigrationType.SCHEMA, [
                (OperationType.CREATE_TABLE, "users", 
                 "CREATE TABLE users (id SERIAL PRIMARY KEY, email VARCHAR(255), created_at TIMESTAMP)",
                 "DROP TABLE users")
            ]),
            ("20240101_002", "create_orders_table", MigrationType.SCHEMA, [
                (OperationType.CREATE_TABLE, "orders",
                 "CREATE TABLE orders (id SERIAL PRIMARY KEY, user_id INT, total DECIMAL(10,2))",
                 "DROP TABLE orders")
            ]),
            ("20240102_001", "add_user_name_column", MigrationType.SCHEMA, [
                (OperationType.ADD_COLUMN, "users",
                 "ALTER TABLE users ADD COLUMN name VARCHAR(255)",
                 "ALTER TABLE users DROP COLUMN name")
            ]),
            ("20240102_002", "add_users_index", MigrationType.INDEX, [
                (OperationType.ADD_INDEX, "users",
                 "CREATE INDEX idx_users_email ON users(email)",
                 "DROP INDEX idx_users_email")
            ]),
            ("20240103_001", "seed_initial_data", MigrationType.SEED, [
                (OperationType.INSERT, "users",
                 "INSERT INTO users (email, name) VALUES ('admin@example.com', 'Admin')",
                 "DELETE FROM users WHERE email = 'admin@example.com'")
            ])
        ]
        
        created_migrations = []
        for version, name, mtype, operations in migrations_data:
            migration = platform.builder.create(version, name, mtype)
            
            for op_type, table, up_sql, down_sql in operations:
                platform.builder.add_operation(
                    migration.migration_id,
                    op_type, table, up_sql, down_sql
                )
                
            created_migrations.append(migration)
            print(f"  ✓ {version}: {name} ({mtype.value})")
            
        # Set dependencies
        created_migrations[2].depends_on = [created_migrations[0].migration_id]
        created_migrations[3].depends_on = [created_migrations[0].migration_id]
        created_migrations[4].depends_on = [created_migrations[0].migration_id, created_migrations[2].migration_id]
        
        # Validate migrations
        print("\n✅ Validating Migrations...")
        
        for migration in created_migrations:
            errors = platform.validator.validate(migration)
            status = "✓" if not errors else "✗"
            print(f"  {status} {migration.version}: {migration.name}")
            for error in errors:
                print(f"     ⚠️ {error}")
                
        # Create migration plan
        print("\n📋 Creating Migration Plan...")
        
        plan = platform.planner.create_plan(
            "Initial Setup",
            [m.migration_id for m in created_migrations]
        )
        
        validated_plan = platform.planner.validate_plan(plan.plan_id)
        
        print(f"  Plan: {plan.name}")
        print(f"  Migrations: {len(plan.migrations)}")
        print(f"  Valid: {'✅' if validated_plan.validated else '❌'}")
        
        print("\n  Execution Order:")
        for i, mig_id in enumerate(plan.execution_order, 1):
            migration = platform.builder.migrations.get(mig_id)
            print(f"    {i}. {migration.version}: {migration.name}")
            
        # Dry run
        print("\n🔍 Dry Run...")
        
        for mig_id in plan.execution_order[:2]:
            migration = platform.builder.migrations.get(mig_id)
            result = await platform.executor.execute(mig_id, dry_run=True)
            
            print(f"  {migration.version}:")
            for op in result.get("operations", []):
                print(f"    → {op['operation']} {op['table']}")
                
        # Execute migrations
        print("\n🚀 Executing Migrations...")
        
        for mig_id in plan.execution_order:
            migration = platform.builder.migrations.get(mig_id)
            result = await platform.executor.execute(mig_id)
            
            status_icon = "✅" if result["status"] == "success" else "❌"
            print(f"  {status_icon} {migration.version}: {migration.name}")
            
            if result["status"] == "success":
                print(f"     Time: {result.get('time_ms', 0):.2f}ms, Rows: {result.get('rows_affected', 0)}")
            else:
                print(f"     Error: {result.get('message', 'Unknown error')}")
                
        # Rollback one migration
        print("\n⏪ Rolling Back Migration...")
        
        last_migration = created_migrations[-1]
        rollback_result = await platform.executor.rollback(last_migration.migration_id)
        
        if rollback_result["status"] == "success":
            print(f"  ✅ {last_migration.version} rolled back ({rollback_result.get('time_ms', 0):.2f}ms)")
        else:
            print(f"  ❌ Rollback failed: {rollback_result.get('message', 'Unknown')}")
            
        # Migration history
        print("\n📜 Migration History:")
        
        for entry in platform.executor.history[-5:]:
            migration = platform.builder.migrations.get(entry.migration_id)
            status = "✓" if entry.success else "✗"
            print(f"  {status} {entry.action}: {migration.version if migration else 'unknown'}")
            print(f"     Duration: {entry.duration_ms:.2f}ms")
            
        # Migration status overview
        print("\n📊 Migration Status Overview:")
        
        for migration in created_migrations:
            status_icons = {
                MigrationStatus.PENDING: "⏳",
                MigrationStatus.RUNNING: "🔄",
                MigrationStatus.COMPLETED: "✅",
                MigrationStatus.FAILED: "❌",
                MigrationStatus.ROLLED_BACK: "⏪"
            }
            icon = status_icons.get(migration.status, "❓")
            print(f"  {icon} {migration.version}: {migration.status.value}")
            
        # Statistics
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Migrations:")
        print(f"    Total: {stats['total_migrations']}")
        for status, count in stats['migrations_by_status'].items():
            print(f"    {status}: {count}")
            
        print(f"\n  By Type:")
        for mtype, count in stats['migrations_by_type'].items():
            print(f"    {mtype}: {count}")
            
        print(f"\n  Performance:")
        print(f"    Total Time: {stats['total_execution_time_ms']:.2f}ms")
        print(f"    Rows Affected: {stats['total_rows_affected']}")
        
        print(f"\n  Infrastructure:")
        print(f"    Connections: {stats['total_connections']}")
        print(f"    Plans: {stats['total_plans']}")
        print(f"    History: {stats['history_entries']}")
        
        # Dashboard
        print("\n📋 Database Migration Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │             Database Migration Overview                     │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Migrations:   {stats['total_migrations']:>10}                        │")
        print(f"  │ Completed:          {stats['migrations_by_status'].get('completed', 0):>10}                        │")
        print(f"  │ Pending:            {stats['migrations_by_status'].get('pending', 0):>10}                        │")
        print(f"  │ Failed:             {stats['migrations_by_status'].get('failed', 0):>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ DB Connections:     {stats['total_connections']:>10}                        │")
        print(f"  │ Migration Plans:    {stats['total_plans']:>10}                        │")
        print(f"  │ History Entries:    {stats['history_entries']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Execution Time:     {stats['total_execution_time_ms']:>10.2f}ms                  │")
        print(f"  │ Rows Affected:      {stats['total_rows_affected']:>10}                        │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Database Migration Platform initialized!")
    print("=" * 60)
