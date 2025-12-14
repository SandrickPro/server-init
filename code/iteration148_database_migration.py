#!/usr/bin/env python3
"""
Server Init - Iteration 148: Database Migration Platform
Платформа миграции баз данных

Функционал:
- Schema Migration - миграция схемы
- Data Migration - миграция данных
- Version Control - контроль версий
- Rollback Support - поддержка отката
- Multi-Database - множественные БД
- Zero-Downtime Migration - миграция без простоя
- Migration Validation - валидация миграций
- Dependency Management - управление зависимостями
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid
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
    SKIPPED = "skipped"


class MigrationType(Enum):
    """Тип миграции"""
    SCHEMA = "schema"
    DATA = "data"
    INDEX = "index"
    CONSTRAINT = "constraint"
    SEED = "seed"
    ROLLBACK = "rollback"


class ValidationResult(Enum):
    """Результат валидации"""
    VALID = "valid"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class Migration:
    """Миграция"""
    migration_id: str
    version: str = ""
    name: str = ""
    
    # Type
    migration_type: MigrationType = MigrationType.SCHEMA
    
    # SQL
    up_sql: str = ""
    down_sql: str = ""
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)
    
    # Metadata
    description: str = ""
    author: str = ""
    
    # Checksums
    checksum: str = ""
    
    # Status
    status: MigrationStatus = MigrationStatus.PENDING
    
    # Execution
    executed_at: Optional[datetime] = None
    execution_time_ms: float = 0.0
    error_message: str = ""
    
    # Flags
    reversible: bool = True
    transactional: bool = True


@dataclass
class DatabaseConnection:
    """Подключение к БД"""
    connection_id: str
    name: str = ""
    
    # Connection
    db_type: DatabaseType = DatabaseType.POSTGRESQL
    host: str = "localhost"
    port: int = 5432
    database: str = ""
    username: str = ""
    
    # Status
    connected: bool = False
    last_connected: Optional[datetime] = None
    
    # Migration table
    migration_table: str = "schema_migrations"


@dataclass
class MigrationPlan:
    """План миграции"""
    plan_id: str
    
    # Migrations
    migrations: List[str] = field(default_factory=list)  # Ordered list
    
    # Direction
    direction: str = "up"  # up, down
    target_version: str = ""
    
    # Status
    status: str = "pending"  # pending, executing, completed, failed
    
    # Results
    completed_migrations: List[str] = field(default_factory=list)
    failed_migration: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class ValidationReport:
    """Отчёт валидации"""
    report_id: str
    migration_id: str = ""
    
    # Results
    result: ValidationResult = ValidationResult.VALID
    
    # Issues
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Checks
    syntax_valid: bool = True
    dependencies_resolved: bool = True
    reversible: bool = True
    
    # Timestamp
    validated_at: datetime = field(default_factory=datetime.now)


@dataclass
class MigrationHistory:
    """История миграций"""
    history_id: str
    migration_id: str = ""
    version: str = ""
    
    # Execution
    direction: str = "up"
    status: MigrationStatus = MigrationStatus.COMPLETED
    
    # Timing
    executed_at: datetime = field(default_factory=datetime.now)
    execution_time_ms: float = 0.0
    
    # Actor
    executed_by: str = ""
    
    # Checksum
    checksum: str = ""


class MigrationRegistry:
    """Реестр миграций"""
    
    def __init__(self):
        self.migrations: Dict[str, Migration] = {}
        self.version_order: List[str] = []
        
    def register(self, version: str, name: str, up_sql: str,
                  down_sql: str = "", **kwargs) -> Migration:
        """Регистрация миграции"""
        migration = Migration(
            migration_id=f"mig_{uuid.uuid4().hex[:8]}",
            version=version,
            name=name,
            up_sql=up_sql,
            down_sql=down_sql,
            checksum=self._calculate_checksum(up_sql + down_sql),
            **kwargs
        )
        
        self.migrations[migration.migration_id] = migration
        
        # Insert in order
        insert_idx = 0
        for i, v in enumerate(self.version_order):
            if self._compare_versions(version, v) > 0:
                insert_idx = i + 1
                
        self.version_order.insert(insert_idx, migration.migration_id)
        
        return migration
        
    def _calculate_checksum(self, content: str) -> str:
        """Расчёт контрольной суммы"""
        return hashlib.md5(content.encode()).hexdigest()
        
    def _compare_versions(self, v1: str, v2: str) -> int:
        """Сравнение версий"""
        # Handle timestamps like 20241214120000
        try:
            return int(v1) - int(self.migrations[v2].version if v2 in self.migrations else v2)
        except:
            return 0
            
    def get_pending(self, applied: List[str]) -> List[Migration]:
        """Получение ожидающих миграций"""
        applied_versions = set(applied)
        return [
            self.migrations[mid] for mid in self.version_order
            if self.migrations[mid].version not in applied_versions
        ]
        
    def get_by_version(self, version: str) -> Optional[Migration]:
        """Получение по версии"""
        for migration in self.migrations.values():
            if migration.version == version:
                return migration
        return None


class MigrationValidator:
    """Валидатор миграций"""
    
    def __init__(self, registry: MigrationRegistry):
        self.registry = registry
        
    def validate(self, migration: Migration) -> ValidationReport:
        """Валидация миграции"""
        report = ValidationReport(
            report_id=f"val_{uuid.uuid4().hex[:8]}",
            migration_id=migration.migration_id
        )
        
        # Check syntax (simplified)
        if not migration.up_sql.strip():
            report.errors.append("Up migration SQL is empty")
            report.syntax_valid = False
            
        # Check reversibility
        if migration.reversible and not migration.down_sql.strip():
            report.warnings.append("Migration marked as reversible but has no down SQL")
            report.reversible = False
            
        # Check dependencies
        for dep in migration.depends_on:
            dep_migration = self.registry.get_by_version(dep)
            if not dep_migration:
                report.errors.append(f"Dependency not found: {dep}")
                report.dependencies_resolved = False
                
        # Check for dangerous operations
        dangerous_keywords = ["DROP TABLE", "TRUNCATE", "DELETE FROM"]
        for keyword in dangerous_keywords:
            if keyword in migration.up_sql.upper():
                report.warnings.append(f"Potentially dangerous operation: {keyword}")
                
        # Set result
        if report.errors:
            report.result = ValidationResult.ERROR
        elif report.warnings:
            report.result = ValidationResult.WARNING
        else:
            report.result = ValidationResult.VALID
            
        return report


class MigrationExecutor:
    """Исполнитель миграций"""
    
    def __init__(self, registry: MigrationRegistry):
        self.registry = registry
        self.history: List[MigrationHistory] = []
        
    async def execute(self, migration: Migration, direction: str = "up") -> MigrationHistory:
        """Выполнение миграции"""
        start_time = datetime.now()
        
        sql = migration.up_sql if direction == "up" else migration.down_sql
        
        history = MigrationHistory(
            history_id=f"hist_{uuid.uuid4().hex[:8]}",
            migration_id=migration.migration_id,
            version=migration.version,
            direction=direction,
            checksum=migration.checksum
        )
        
        try:
            # Simulate execution
            await asyncio.sleep(0.05)  # Simulate DB operation
            
            # Check for simulated errors
            if "FAIL" in sql:
                raise Exception("Simulated migration failure")
                
            migration.status = MigrationStatus.COMPLETED
            history.status = MigrationStatus.COMPLETED
            
        except Exception as e:
            migration.status = MigrationStatus.FAILED
            migration.error_message = str(e)
            history.status = MigrationStatus.FAILED
            
        end_time = datetime.now()
        history.execution_time_ms = (end_time - start_time).total_seconds() * 1000
        migration.execution_time_ms = history.execution_time_ms
        migration.executed_at = end_time
        
        self.history.append(history)
        return history
        
    async def execute_plan(self, plan: MigrationPlan) -> MigrationPlan:
        """Выполнение плана миграции"""
        plan.status = "executing"
        plan.started_at = datetime.now()
        
        for migration_id in plan.migrations:
            migration = self.registry.migrations.get(migration_id)
            if not migration:
                continue
                
            history = await self.execute(migration, plan.direction)
            
            if history.status == MigrationStatus.COMPLETED:
                plan.completed_migrations.append(migration_id)
            else:
                plan.failed_migration = migration_id
                plan.status = "failed"
                return plan
                
        plan.status = "completed"
        plan.completed_at = datetime.now()
        return plan
        
    def get_applied_versions(self) -> List[str]:
        """Получение применённых версий"""
        applied = set()
        for h in self.history:
            if h.direction == "up" and h.status == MigrationStatus.COMPLETED:
                applied.add(h.version)
            elif h.direction == "down" and h.status == MigrationStatus.COMPLETED:
                applied.discard(h.version)
        return list(applied)


class MigrationPlanner:
    """Планировщик миграций"""
    
    def __init__(self, registry: MigrationRegistry, executor: MigrationExecutor):
        self.registry = registry
        self.executor = executor
        
    def plan_upgrade(self, target_version: str = None) -> MigrationPlan:
        """Планирование апгрейда"""
        applied = self.executor.get_applied_versions()
        pending = self.registry.get_pending(applied)
        
        if target_version:
            pending = [m for m in pending if m.version <= target_version]
            
        # Resolve dependencies
        ordered = self._resolve_dependencies(pending)
        
        return MigrationPlan(
            plan_id=f"plan_{uuid.uuid4().hex[:8]}",
            migrations=[m.migration_id for m in ordered],
            direction="up",
            target_version=target_version or (ordered[-1].version if ordered else "")
        )
        
    def plan_rollback(self, steps: int = 1) -> MigrationPlan:
        """Планирование отката"""
        applied = self.executor.get_applied_versions()
        
        # Get migrations to rollback (in reverse order)
        to_rollback = []
        for history in reversed(self.executor.history):
            if history.direction == "up" and history.status == MigrationStatus.COMPLETED:
                migration = self.registry.get_by_version(history.version)
                if migration and migration.reversible:
                    to_rollback.append(migration)
                    if len(to_rollback) >= steps:
                        break
                        
        return MigrationPlan(
            plan_id=f"plan_{uuid.uuid4().hex[:8]}",
            migrations=[m.migration_id for m in to_rollback],
            direction="down",
            target_version=to_rollback[-1].version if to_rollback else ""
        )
        
    def _resolve_dependencies(self, migrations: List[Migration]) -> List[Migration]:
        """Разрешение зависимостей"""
        resolved = []
        pending = migrations.copy()
        resolved_versions = set(self.executor.get_applied_versions())
        
        while pending:
            for migration in pending:
                deps_met = all(
                    dep in resolved_versions
                    for dep in migration.depends_on
                )
                if deps_met:
                    resolved.append(migration)
                    resolved_versions.add(migration.version)
                    pending.remove(migration)
                    break
            else:
                # No progress - circular dependency or missing dep
                resolved.extend(pending)
                break
                
        return resolved


class DataMigrator:
    """Мигратор данных"""
    
    def __init__(self):
        self.batch_size: int = 1000
        self.progress: Dict[str, Dict] = {}
        
    async def migrate_table(self, source_table: str, target_table: str,
                             transform: Callable = None,
                             batch_size: int = None) -> Dict:
        """Миграция таблицы"""
        batch_size = batch_size or self.batch_size
        
        migration_id = f"dm_{uuid.uuid4().hex[:8]}"
        self.progress[migration_id] = {
            "source": source_table,
            "target": target_table,
            "status": "running",
            "total_rows": 0,
            "migrated_rows": 0,
            "failed_rows": 0,
            "started_at": datetime.now()
        }
        
        # Simulate data migration
        total_rows = 10000  # Simulated
        self.progress[migration_id]["total_rows"] = total_rows
        
        for batch_start in range(0, total_rows, batch_size):
            batch_end = min(batch_start + batch_size, total_rows)
            
            await asyncio.sleep(0.01)  # Simulate batch processing
            
            self.progress[migration_id]["migrated_rows"] = batch_end
            
        self.progress[migration_id]["status"] = "completed"
        self.progress[migration_id]["completed_at"] = datetime.now()
        
        return self.progress[migration_id]
        
    def get_progress(self, migration_id: str) -> Optional[Dict]:
        """Получение прогресса"""
        return self.progress.get(migration_id)


class ZeroDowntimeMigrator:
    """Мигратор без простоя"""
    
    def __init__(self, registry: MigrationRegistry):
        self.registry = registry
        self.phases: List[Dict] = []
        
    def plan_zero_downtime(self, migration: Migration) -> List[Dict]:
        """Планирование миграции без простоя"""
        phases = []
        
        # Analyze migration
        sql_upper = migration.up_sql.upper()
        
        if "ADD COLUMN" in sql_upper:
            phases.extend([
                {"phase": 1, "action": "Add column with NULL allowed", "blocking": False},
                {"phase": 2, "action": "Backfill data in batches", "blocking": False},
                {"phase": 3, "action": "Add constraints", "blocking": True, "window": "maintenance"}
            ])
            
        elif "DROP COLUMN" in sql_upper:
            phases.extend([
                {"phase": 1, "action": "Stop writing to column", "blocking": False},
                {"phase": 2, "action": "Deploy code without column usage", "blocking": False},
                {"phase": 3, "action": "Drop column", "blocking": True, "window": "maintenance"}
            ])
            
        elif "CREATE INDEX" in sql_upper:
            phases.extend([
                {"phase": 1, "action": "Create index CONCURRENTLY", "blocking": False}
            ])
            
        elif "ALTER TABLE" in sql_upper:
            phases.extend([
                {"phase": 1, "action": "Create new table with new schema", "blocking": False},
                {"phase": 2, "action": "Double-write to both tables", "blocking": False},
                {"phase": 3, "action": "Backfill new table", "blocking": False},
                {"phase": 4, "action": "Switch reads to new table", "blocking": False},
                {"phase": 5, "action": "Stop writes to old table", "blocking": False},
                {"phase": 6, "action": "Drop old table", "blocking": True, "window": "maintenance"}
            ])
        else:
            phases.append({"phase": 1, "action": "Execute migration", "blocking": True})
            
        self.phases = phases
        return phases


class DatabaseMigrationPlatform:
    """Платформа миграции БД"""
    
    def __init__(self):
        self.registry = MigrationRegistry()
        self.validator = MigrationValidator(self.registry)
        self.executor = MigrationExecutor(self.registry)
        self.planner = MigrationPlanner(self.registry, self.executor)
        self.data_migrator = DataMigrator()
        self.zero_downtime = ZeroDowntimeMigrator(self.registry)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        history = self.executor.history
        
        return {
            "total_migrations": len(self.registry.migrations),
            "applied_migrations": len(self.executor.get_applied_versions()),
            "pending_migrations": len(self.registry.get_pending(self.executor.get_applied_versions())),
            "total_executions": len(history),
            "successful_executions": len([h for h in history if h.status == MigrationStatus.COMPLETED]),
            "failed_executions": len([h for h in history if h.status == MigrationStatus.FAILED]),
            "total_execution_time_ms": sum(h.execution_time_ms for h in history)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 148: Database Migration Platform")
    print("=" * 60)
    
    async def demo():
        platform = DatabaseMigrationPlatform()
        print("✓ Database Migration Platform created")
        
        # Register migrations
        print("\n📝 Registering Migrations...")
        
        migrations_data = [
            ("20241201000001", "create_users_table", """
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """, "DROP TABLE users;"),
            
            ("20241201000002", "create_orders_table", """
                CREATE TABLE orders (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    total DECIMAL(10,2),
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """, "DROP TABLE orders;", ["20241201000001"]),
            
            ("20241202000001", "add_user_name", """
                ALTER TABLE users ADD COLUMN name VARCHAR(255);
            """, "ALTER TABLE users DROP COLUMN name;", ["20241201000001"]),
            
            ("20241202000002", "add_orders_status", """
                ALTER TABLE orders ADD COLUMN status VARCHAR(50) DEFAULT 'pending';
            """, "ALTER TABLE orders DROP COLUMN status;", ["20241201000002"]),
            
            ("20241203000001", "create_products_table", """
                CREATE TABLE products (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    price DECIMAL(10,2),
                    stock INTEGER DEFAULT 0
                );
            """, "DROP TABLE products;"),
            
            ("20241203000002", "add_user_index", """
                CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
            """, "DROP INDEX idx_users_email;", ["20241201000001"])
        ]
        
        for data in migrations_data:
            version, name, up_sql, down_sql = data[:4]
            deps = data[4] if len(data) > 4 else []
            
            migration = platform.registry.register(
                version, name, up_sql, down_sql,
                depends_on=deps,
                migration_type=MigrationType.SCHEMA,
                author="developer@company.com"
            )
            print(f"  ✓ {version}: {name}")
            
        # Validate migrations
        print("\n🔍 Validating Migrations...")
        
        for migration in platform.registry.migrations.values():
            report = platform.validator.validate(migration)
            
            result_icon = {"valid": "✓", "warning": "⚠", "error": "✗"}
            print(f"  {result_icon[report.result.value]} {migration.version}: {migration.name}")
            
            for warning in report.warnings:
                print(f"      ⚠️ {warning}")
            for error in report.errors:
                print(f"      ❌ {error}")
                
        # Plan migration
        print("\n📋 Planning Migration...")
        
        plan = platform.planner.plan_upgrade()
        
        print(f"\n  Plan ID: {plan.plan_id}")
        print(f"  Direction: {plan.direction}")
        print(f"  Target Version: {plan.target_version}")
        print(f"  Migrations to apply: {len(plan.migrations)}")
        
        print("\n  Migration Order:")
        for i, mid in enumerate(plan.migrations, 1):
            migration = platform.registry.migrations[mid]
            deps = f" (depends: {migration.depends_on})" if migration.depends_on else ""
            print(f"    {i}. {migration.version}: {migration.name}{deps}")
            
        # Execute plan
        print("\n🚀 Executing Migration Plan...")
        
        result_plan = await platform.executor.execute_plan(plan)
        
        print(f"\n  Status: {result_plan.status}")
        print(f"  Completed: {len(result_plan.completed_migrations)}/{len(result_plan.migrations)}")
        
        for mid in result_plan.completed_migrations:
            migration = platform.registry.migrations[mid]
            print(f"    ✓ {migration.version}: {migration.execution_time_ms:.1f}ms")
            
        # Show applied versions
        print("\n📊 Applied Versions:")
        
        applied = platform.executor.get_applied_versions()
        for version in sorted(applied):
            migration = platform.registry.get_by_version(version)
            if migration:
                print(f"  ✓ {version}: {migration.name}")
                
        # Plan rollback
        print("\n⏪ Planning Rollback (2 steps)...")
        
        rollback_plan = platform.planner.plan_rollback(steps=2)
        
        print(f"\n  Migrations to rollback: {len(rollback_plan.migrations)}")
        for mid in rollback_plan.migrations:
            migration = platform.registry.migrations[mid]
            print(f"    ↩️ {migration.version}: {migration.name}")
            
        # Zero-downtime planning
        print("\n🔄 Zero-Downtime Migration Planning...")
        
        alter_migration = platform.registry.get_by_version("20241202000001")
        if alter_migration:
            phases = platform.zero_downtime.plan_zero_downtime(alter_migration)
            
            print(f"\n  Migration: {alter_migration.name}")
            print(f"  Phases required: {len(phases)}")
            
            for phase in phases:
                blocking = "🔴 BLOCKING" if phase.get("blocking") else "🟢 Non-blocking"
                window = f" ({phase['window']})" if phase.get("window") else ""
                print(f"    Phase {phase['phase']}: {phase['action']} {blocking}{window}")
                
        # Data migration
        print("\n📦 Data Migration Simulation...")
        
        result = await platform.data_migrator.migrate_table(
            "old_users", "new_users",
            batch_size=2000
        )
        
        print(f"\n  Source: {result['source']}")
        print(f"  Target: {result['target']}")
        print(f"  Total rows: {result['total_rows']:,}")
        print(f"  Migrated: {result['migrated_rows']:,}")
        print(f"  Status: {result['status']}")
        
        # Migration history
        print("\n📜 Migration History:")
        
        for history in platform.executor.history[-5:]:
            direction_icon = "↑" if history.direction == "up" else "↓"
            status_icon = "✓" if history.status == MigrationStatus.COMPLETED else "✗"
            print(f"  {status_icon} {direction_icon} {history.version}: {history.execution_time_ms:.1f}ms")
            
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Migrations: {stats['total_migrations']}")
        print(f"  Applied: {stats['applied_migrations']}")
        print(f"  Pending: {stats['pending_migrations']}")
        print(f"  Total Executions: {stats['total_executions']}")
        print(f"  Successful: {stats['successful_executions']}")
        print(f"  Failed: {stats['failed_executions']}")
        print(f"  Total Time: {stats['total_execution_time_ms']:.1f}ms")
        
        # Dashboard
        print("\n📋 Migration Dashboard:")
        print("  ┌────────────────────────────────────────────────────────────┐")
        print("  │                  Migration Overview                        │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Migrations:      {stats['total_migrations']:>10}                    │")
        print(f"  │ Applied:               {stats['applied_migrations']:>10}                    │")
        print(f"  │ Pending:               {stats['pending_migrations']:>10}                    │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Successful Runs:       {stats['successful_executions']:>10}                    │")
        print(f"  │ Failed Runs:           {stats['failed_executions']:>10}                    │")
        print(f"  │ Total Time (ms):       {stats['total_execution_time_ms']:>10.1f}                    │")
        print("  └────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Database Migration Platform initialized!")
    print("=" * 60)
