#!/usr/bin/env python3
"""
Server Init - Iteration 167: Database Migration Platform
Платформа миграции баз данных

Функционал:
- Migration Management - управление миграциями
- Schema Versioning - версионирование схемы
- Rollback Support - поддержка отката
- Data Migration - миграция данных
- Seed Data Management - управление сид-данными
- Migration History - история миграций
- Dry Run Support - поддержка тестового запуска
- Multi-Database Support - поддержка нескольких БД
"""

import asyncio
import hashlib
import re
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid


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
    FULL = "full"


class DatabaseType(Enum):
    """Тип базы данных"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"
    REDIS = "redis"


class OperationType(Enum):
    """Тип операции"""
    CREATE_TABLE = "create_table"
    DROP_TABLE = "drop_table"
    ALTER_TABLE = "alter_table"
    ADD_COLUMN = "add_column"
    DROP_COLUMN = "drop_column"
    RENAME_COLUMN = "rename_column"
    ADD_INDEX = "add_index"
    DROP_INDEX = "drop_index"
    ADD_CONSTRAINT = "add_constraint"
    DROP_CONSTRAINT = "drop_constraint"
    INSERT_DATA = "insert_data"
    UPDATE_DATA = "update_data"
    DELETE_DATA = "delete_data"
    RAW_SQL = "raw_sql"


@dataclass
class Column:
    """Колонка таблицы"""
    name: str
    data_type: str  # varchar, integer, text, boolean, timestamp, etc.
    nullable: bool = True
    default: Any = None
    primary_key: bool = False
    auto_increment: bool = False
    unique: bool = False
    references: Optional[str] = None  # table.column for FK


@dataclass
class Index:
    """Индекс"""
    name: str
    table: str = ""
    columns: List[str] = field(default_factory=list)
    unique: bool = False
    where: Optional[str] = None  # partial index condition


@dataclass
class Constraint:
    """Ограничение"""
    name: str
    constraint_type: str = ""  # primary_key, foreign_key, unique, check
    table: str = ""
    columns: List[str] = field(default_factory=list)
    references_table: str = ""
    references_columns: List[str] = field(default_factory=list)
    on_delete: str = "CASCADE"
    on_update: str = "CASCADE"
    check_expression: str = ""


@dataclass
class MigrationOperation:
    """Операция миграции"""
    operation_id: str
    operation_type: OperationType = OperationType.RAW_SQL
    
    # Target
    table_name: str = ""
    
    # For columns
    column: Optional[Column] = None
    old_column_name: str = ""
    
    # For indexes
    index: Optional[Index] = None
    
    # For constraints
    constraint: Optional[Constraint] = None
    
    # For data operations
    data: List[Dict] = field(default_factory=list)
    condition: str = ""
    
    # Raw SQL
    sql_up: str = ""
    sql_down: str = ""


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
    
    # Flags
    reversible: bool = True
    transactional: bool = True
    
    # Checksum
    checksum: str = ""
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    executed_at: Optional[datetime] = None
    execution_time_ms: float = 0.0
    
    # Error
    error_message: str = ""


@dataclass
class MigrationHistory:
    """Запись истории миграции"""
    history_id: str
    migration_id: str = ""
    version: str = ""
    name: str = ""
    
    # Action
    action: str = ""  # up, down
    
    # Status
    status: MigrationStatus = MigrationStatus.COMPLETED
    
    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    finished_at: Optional[datetime] = None
    duration_ms: float = 0.0
    
    # Context
    executed_by: str = ""
    environment: str = ""
    
    # Error
    error: str = ""


@dataclass
class DatabaseSchema:
    """Схема базы данных"""
    schema_id: str
    name: str = ""
    version: str = ""
    
    # Tables
    tables: Dict[str, List[Column]] = field(default_factory=dict)
    
    # Indexes
    indexes: List[Index] = field(default_factory=list)
    
    # Constraints
    constraints: List[Constraint] = field(default_factory=list)
    
    # Snapshot time
    snapshot_at: datetime = field(default_factory=datetime.now)


class SQLGenerator:
    """Генератор SQL"""
    
    def __init__(self, db_type: DatabaseType = DatabaseType.POSTGRESQL):
        self.db_type = db_type
        
    def generate_up(self, operation: MigrationOperation) -> str:
        """Генерация SQL для применения"""
        if operation.sql_up:
            return operation.sql_up
            
        op_type = operation.operation_type
        
        if op_type == OperationType.CREATE_TABLE:
            return self._create_table(operation)
        elif op_type == OperationType.DROP_TABLE:
            return f"DROP TABLE IF EXISTS {operation.table_name};"
        elif op_type == OperationType.ADD_COLUMN:
            return self._add_column(operation)
        elif op_type == OperationType.DROP_COLUMN:
            return f"ALTER TABLE {operation.table_name} DROP COLUMN {operation.column.name};"
        elif op_type == OperationType.RENAME_COLUMN:
            return f"ALTER TABLE {operation.table_name} RENAME COLUMN {operation.old_column_name} TO {operation.column.name};"
        elif op_type == OperationType.ADD_INDEX:
            return self._add_index(operation)
        elif op_type == OperationType.DROP_INDEX:
            return f"DROP INDEX IF EXISTS {operation.index.name};"
        elif op_type == OperationType.ADD_CONSTRAINT:
            return self._add_constraint(operation)
        elif op_type == OperationType.DROP_CONSTRAINT:
            return f"ALTER TABLE {operation.table_name} DROP CONSTRAINT {operation.constraint.name};"
        elif op_type == OperationType.INSERT_DATA:
            return self._insert_data(operation)
        elif op_type == OperationType.UPDATE_DATA:
            return self._update_data(operation)
        elif op_type == OperationType.DELETE_DATA:
            return f"DELETE FROM {operation.table_name} WHERE {operation.condition};"
            
        return ""
        
    def generate_down(self, operation: MigrationOperation) -> str:
        """Генерация SQL для отката"""
        if operation.sql_down:
            return operation.sql_down
            
        op_type = operation.operation_type
        
        if op_type == OperationType.CREATE_TABLE:
            return f"DROP TABLE IF EXISTS {operation.table_name};"
        elif op_type == OperationType.DROP_TABLE:
            # Need stored schema to recreate
            return f"-- Cannot auto-generate: table {operation.table_name} recreation required"
        elif op_type == OperationType.ADD_COLUMN:
            return f"ALTER TABLE {operation.table_name} DROP COLUMN {operation.column.name};"
        elif op_type == OperationType.DROP_COLUMN:
            return f"-- Cannot auto-generate: column {operation.column.name} recreation required"
        elif op_type == OperationType.ADD_INDEX:
            return f"DROP INDEX IF EXISTS {operation.index.name};"
        elif op_type == OperationType.DROP_INDEX:
            return f"-- Cannot auto-generate: index recreation required"
            
        return ""
        
    def _create_table(self, operation: MigrationOperation) -> str:
        """Создание таблицы"""
        columns = []
        
        for col in operation.data:
            col_def = self._column_definition(Column(**col))
            columns.append(col_def)
            
        columns_sql = ",\n  ".join(columns)
        return f"CREATE TABLE IF NOT EXISTS {operation.table_name} (\n  {columns_sql}\n);"
        
    def _column_definition(self, col: Column) -> str:
        """Определение колонки"""
        parts = [col.name, col.data_type.upper()]
        
        if col.primary_key:
            parts.append("PRIMARY KEY")
        if col.auto_increment:
            if self.db_type == DatabaseType.POSTGRESQL:
                parts[1] = "SERIAL"
            else:
                parts.append("AUTO_INCREMENT")
        if not col.nullable:
            parts.append("NOT NULL")
        if col.unique:
            parts.append("UNIQUE")
        if col.default is not None:
            parts.append(f"DEFAULT {col.default}")
        if col.references:
            parts.append(f"REFERENCES {col.references}")
            
        return " ".join(parts)
        
    def _add_column(self, operation: MigrationOperation) -> str:
        """Добавление колонки"""
        col = operation.column
        col_def = self._column_definition(col)
        return f"ALTER TABLE {operation.table_name} ADD COLUMN {col_def};"
        
    def _add_index(self, operation: MigrationOperation) -> str:
        """Создание индекса"""
        idx = operation.index
        unique = "UNIQUE " if idx.unique else ""
        columns = ", ".join(idx.columns)
        
        sql = f"CREATE {unique}INDEX {idx.name} ON {idx.table} ({columns})"
        
        if idx.where:
            sql += f" WHERE {idx.where}"
            
        return sql + ";"
        
    def _add_constraint(self, operation: MigrationOperation) -> str:
        """Добавление ограничения"""
        con = operation.constraint
        
        if con.constraint_type == "foreign_key":
            cols = ", ".join(con.columns)
            ref_cols = ", ".join(con.references_columns)
            return f"""ALTER TABLE {con.table} ADD CONSTRAINT {con.name}
  FOREIGN KEY ({cols}) REFERENCES {con.references_table} ({ref_cols})
  ON DELETE {con.on_delete} ON UPDATE {con.on_update};"""
        elif con.constraint_type == "unique":
            cols = ", ".join(con.columns)
            return f"ALTER TABLE {con.table} ADD CONSTRAINT {con.name} UNIQUE ({cols});"
        elif con.constraint_type == "check":
            return f"ALTER TABLE {con.table} ADD CONSTRAINT {con.name} CHECK ({con.check_expression});"
            
        return ""
        
    def _insert_data(self, operation: MigrationOperation) -> str:
        """Вставка данных"""
        if not operation.data:
            return ""
            
        columns = list(operation.data[0].keys())
        cols_sql = ", ".join(columns)
        
        values = []
        for row in operation.data:
            row_values = []
            for col in columns:
                val = row.get(col)
                if val is None:
                    row_values.append("NULL")
                elif isinstance(val, str):
                    row_values.append(f"'{val}'")
                else:
                    row_values.append(str(val))
            values.append(f"({', '.join(row_values)})")
            
        values_sql = ",\n  ".join(values)
        return f"INSERT INTO {operation.table_name} ({cols_sql})\nVALUES\n  {values_sql};"
        
    def _update_data(self, operation: MigrationOperation) -> str:
        """Обновление данных"""
        if not operation.data:
            return ""
            
        updates = operation.data[0]
        set_parts = [f"{k} = {repr(v)}" for k, v in updates.items()]
        set_sql = ", ".join(set_parts)
        
        return f"UPDATE {operation.table_name} SET {set_sql} WHERE {operation.condition};"


class MigrationExecutor:
    """Исполнитель миграций"""
    
    def __init__(self, sql_generator: SQLGenerator):
        self.sql_generator = sql_generator
        self.executed_statements: List[str] = []
        
    async def execute_migration(self, migration: Migration, dry_run: bool = False) -> bool:
        """Выполнение миграции"""
        migration.status = MigrationStatus.RUNNING
        start_time = datetime.now()
        
        try:
            statements = []
            
            for operation in migration.operations:
                sql = self.sql_generator.generate_up(operation)
                if sql:
                    statements.append(sql)
                    
            if dry_run:
                print(f"  [DRY RUN] Would execute {len(statements)} statements")
                for stmt in statements:
                    print(f"    {stmt[:100]}...")
            else:
                # Simulate execution
                for stmt in statements:
                    await asyncio.sleep(0.01)  # Simulate DB latency
                    self.executed_statements.append(stmt)
                    
            migration.status = MigrationStatus.COMPLETED
            migration.executed_at = datetime.now()
            migration.execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return True
            
        except Exception as e:
            migration.status = MigrationStatus.FAILED
            migration.error_message = str(e)
            return False
            
    async def rollback_migration(self, migration: Migration, dry_run: bool = False) -> bool:
        """Откат миграции"""
        if not migration.reversible:
            return False
            
        try:
            statements = []
            
            # Reverse order for rollback
            for operation in reversed(migration.operations):
                sql = self.sql_generator.generate_down(operation)
                if sql and not sql.startswith("--"):
                    statements.append(sql)
                    
            if dry_run:
                print(f"  [DRY RUN] Would rollback {len(statements)} statements")
            else:
                for stmt in statements:
                    await asyncio.sleep(0.01)
                    self.executed_statements.append(stmt)
                    
            migration.status = MigrationStatus.ROLLED_BACK
            return True
            
        except Exception as e:
            migration.error_message = str(e)
            return False


class MigrationManager:
    """Менеджер миграций"""
    
    def __init__(self, db_type: DatabaseType = DatabaseType.POSTGRESQL):
        self.db_type = db_type
        self.migrations: Dict[str, Migration] = {}
        self.history: List[MigrationHistory] = []
        self.current_version: str = "0"
        
        self.sql_generator = SQLGenerator(db_type)
        self.executor = MigrationExecutor(self.sql_generator)
        
    def create_migration(self, name: str, migration_type: MigrationType = MigrationType.SCHEMA) -> Migration:
        """Создание миграции"""
        # Generate version based on timestamp
        version = datetime.now().strftime("%Y%m%d%H%M%S")
        
        migration = Migration(
            migration_id=f"mig_{uuid.uuid4().hex[:8]}",
            version=version,
            name=name,
            migration_type=migration_type
        )
        
        self.migrations[migration.migration_id] = migration
        return migration
        
    def add_operation(self, migration_id: str, operation: MigrationOperation):
        """Добавление операции"""
        if migration_id in self.migrations:
            self.migrations[migration_id].operations.append(operation)
            self._update_checksum(migration_id)
            
    def _update_checksum(self, migration_id: str):
        """Обновление контрольной суммы"""
        migration = self.migrations[migration_id]
        
        content = json.dumps({
            "version": migration.version,
            "name": migration.name,
            "operations": [op.operation_id for op in migration.operations]
        }, sort_keys=True)
        
        migration.checksum = hashlib.md5(content.encode()).hexdigest()
        
    def get_pending_migrations(self) -> List[Migration]:
        """Получение ожидающих миграций"""
        pending = []
        
        for migration in sorted(self.migrations.values(), key=lambda m: m.version):
            if migration.status == MigrationStatus.PENDING:
                pending.append(migration)
                
        return pending
        
    def get_applied_migrations(self) -> List[Migration]:
        """Получение применённых миграций"""
        return [m for m in self.migrations.values() 
                if m.status == MigrationStatus.COMPLETED]
        
    async def migrate(self, target_version: Optional[str] = None, dry_run: bool = False) -> List[Migration]:
        """Выполнение миграций"""
        pending = self.get_pending_migrations()
        applied = []
        
        for migration in pending:
            if target_version and migration.version > target_version:
                break
                
            # Check dependencies
            deps_met = all(
                self.migrations.get(dep_id, Migration(migration_id="")).status == MigrationStatus.COMPLETED
                for dep_id in migration.depends_on
            )
            
            if not deps_met:
                print(f"  Skipping {migration.name}: dependencies not met")
                continue
                
            print(f"  Applying: {migration.version}_{migration.name}")
            
            success = await self.executor.execute_migration(migration, dry_run)
            
            if success:
                applied.append(migration)
                self.current_version = migration.version
                
                # Record history
                history = MigrationHistory(
                    history_id=f"hist_{uuid.uuid4().hex[:8]}",
                    migration_id=migration.migration_id,
                    version=migration.version,
                    name=migration.name,
                    action="up",
                    status=migration.status,
                    duration_ms=migration.execution_time_ms
                )
                self.history.append(history)
            else:
                print(f"  Failed: {migration.error_message}")
                break
                
        return applied
        
    async def rollback(self, steps: int = 1, dry_run: bool = False) -> List[Migration]:
        """Откат миграций"""
        applied = sorted(self.get_applied_migrations(), key=lambda m: m.version, reverse=True)
        rolled_back = []
        
        for i, migration in enumerate(applied):
            if i >= steps:
                break
                
            print(f"  Rolling back: {migration.version}_{migration.name}")
            
            success = await self.executor.rollback_migration(migration, dry_run)
            
            if success:
                rolled_back.append(migration)
                
                history = MigrationHistory(
                    history_id=f"hist_{uuid.uuid4().hex[:8]}",
                    migration_id=migration.migration_id,
                    version=migration.version,
                    name=migration.name,
                    action="down",
                    status=migration.status
                )
                self.history.append(history)
            else:
                print(f"  Rollback failed: {migration.error_message}")
                break
                
        return rolled_back


class SchemaBuilder:
    """Строитель схемы"""
    
    def __init__(self, migration_manager: MigrationManager):
        self.manager = migration_manager
        self.current_migration: Optional[Migration] = None
        
    def create_migration(self, name: str) -> 'SchemaBuilder':
        """Создание миграции"""
        self.current_migration = self.manager.create_migration(name)
        return self
        
    def create_table(self, table_name: str, columns: List[Dict]) -> 'SchemaBuilder':
        """Создание таблицы"""
        if self.current_migration:
            operation = MigrationOperation(
                operation_id=f"op_{uuid.uuid4().hex[:8]}",
                operation_type=OperationType.CREATE_TABLE,
                table_name=table_name,
                data=columns
            )
            self.manager.add_operation(self.current_migration.migration_id, operation)
        return self
        
    def drop_table(self, table_name: str) -> 'SchemaBuilder':
        """Удаление таблицы"""
        if self.current_migration:
            operation = MigrationOperation(
                operation_id=f"op_{uuid.uuid4().hex[:8]}",
                operation_type=OperationType.DROP_TABLE,
                table_name=table_name
            )
            self.manager.add_operation(self.current_migration.migration_id, operation)
        return self
        
    def add_column(self, table_name: str, column: Column) -> 'SchemaBuilder':
        """Добавление колонки"""
        if self.current_migration:
            operation = MigrationOperation(
                operation_id=f"op_{uuid.uuid4().hex[:8]}",
                operation_type=OperationType.ADD_COLUMN,
                table_name=table_name,
                column=column
            )
            self.manager.add_operation(self.current_migration.migration_id, operation)
        return self
        
    def add_index(self, index: Index) -> 'SchemaBuilder':
        """Добавление индекса"""
        if self.current_migration:
            operation = MigrationOperation(
                operation_id=f"op_{uuid.uuid4().hex[:8]}",
                operation_type=OperationType.ADD_INDEX,
                index=index
            )
            self.manager.add_operation(self.current_migration.migration_id, operation)
        return self
        
    def add_foreign_key(self, constraint: Constraint) -> 'SchemaBuilder':
        """Добавление внешнего ключа"""
        if self.current_migration:
            constraint.constraint_type = "foreign_key"
            operation = MigrationOperation(
                operation_id=f"op_{uuid.uuid4().hex[:8]}",
                operation_type=OperationType.ADD_CONSTRAINT,
                table_name=constraint.table,
                constraint=constraint
            )
            self.manager.add_operation(self.current_migration.migration_id, operation)
        return self
        
    def seed_data(self, table_name: str, data: List[Dict]) -> 'SchemaBuilder':
        """Вставка seed-данных"""
        if self.current_migration:
            operation = MigrationOperation(
                operation_id=f"op_{uuid.uuid4().hex[:8]}",
                operation_type=OperationType.INSERT_DATA,
                table_name=table_name,
                data=data
            )
            self.manager.add_operation(self.current_migration.migration_id, operation)
        return self
        
    def raw_sql(self, sql_up: str, sql_down: str = "") -> 'SchemaBuilder':
        """Сырой SQL"""
        if self.current_migration:
            operation = MigrationOperation(
                operation_id=f"op_{uuid.uuid4().hex[:8]}",
                operation_type=OperationType.RAW_SQL,
                sql_up=sql_up,
                sql_down=sql_down
            )
            self.manager.add_operation(self.current_migration.migration_id, operation)
        return self
        
    def build(self) -> Optional[Migration]:
        """Завершение построения"""
        migration = self.current_migration
        self.current_migration = None
        return migration


class DatabaseMigrationPlatform:
    """Платформа миграции БД"""
    
    def __init__(self, db_type: DatabaseType = DatabaseType.POSTGRESQL):
        self.manager = MigrationManager(db_type)
        self.builder = SchemaBuilder(self.manager)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        pending = len(self.manager.get_pending_migrations())
        applied = len(self.manager.get_applied_migrations())
        
        return {
            "total_migrations": len(self.manager.migrations),
            "pending_migrations": pending,
            "applied_migrations": applied,
            "current_version": self.manager.current_version,
            "history_entries": len(self.manager.history)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 167: Database Migration Platform")
    print("=" * 60)
    
    async def demo():
        platform = DatabaseMigrationPlatform(DatabaseType.POSTGRESQL)
        print("✓ Database Migration Platform created")
        
        # Create migrations using builder
        print("\n📝 Creating Migrations...")
        
        # Migration 1: Create users table
        platform.builder.create_migration("create_users_table")
        platform.builder.create_table("users", [
            {"name": "id", "data_type": "serial", "primary_key": True},
            {"name": "email", "data_type": "varchar(255)", "nullable": False, "unique": True},
            {"name": "password_hash", "data_type": "varchar(255)", "nullable": False},
            {"name": "name", "data_type": "varchar(100)"},
            {"name": "created_at", "data_type": "timestamp", "default": "CURRENT_TIMESTAMP"},
            {"name": "updated_at", "data_type": "timestamp"},
        ])
        platform.builder.add_index(Index(
            name="idx_users_email",
            table="users",
            columns=["email"],
            unique=True
        ))
        m1 = platform.builder.build()
        print(f"  ✓ {m1.version}_{m1.name}")
        
        # Add small delay for version uniqueness
        await asyncio.sleep(0.1)
        
        # Migration 2: Create posts table
        platform.builder.create_migration("create_posts_table")
        platform.builder.create_table("posts", [
            {"name": "id", "data_type": "serial", "primary_key": True},
            {"name": "user_id", "data_type": "integer", "nullable": False},
            {"name": "title", "data_type": "varchar(255)", "nullable": False},
            {"name": "content", "data_type": "text"},
            {"name": "status", "data_type": "varchar(20)", "default": "'draft'"},
            {"name": "published_at", "data_type": "timestamp"},
            {"name": "created_at", "data_type": "timestamp", "default": "CURRENT_TIMESTAMP"},
        ])
        platform.builder.add_foreign_key(Constraint(
            name="fk_posts_user",
            table="posts",
            columns=["user_id"],
            references_table="users",
            references_columns=["id"]
        ))
        platform.builder.add_index(Index(
            name="idx_posts_user_id",
            table="posts",
            columns=["user_id"]
        ))
        platform.builder.add_index(Index(
            name="idx_posts_status",
            table="posts",
            columns=["status"]
        ))
        m2 = platform.builder.build()
        print(f"  ✓ {m2.version}_{m2.name}")
        
        await asyncio.sleep(0.1)
        
        # Migration 3: Create comments table
        platform.builder.create_migration("create_comments_table")
        platform.builder.create_table("comments", [
            {"name": "id", "data_type": "serial", "primary_key": True},
            {"name": "post_id", "data_type": "integer", "nullable": False},
            {"name": "user_id", "data_type": "integer", "nullable": False},
            {"name": "content", "data_type": "text", "nullable": False},
            {"name": "created_at", "data_type": "timestamp", "default": "CURRENT_TIMESTAMP"},
        ])
        platform.builder.add_foreign_key(Constraint(
            name="fk_comments_post",
            table="comments",
            columns=["post_id"],
            references_table="posts",
            references_columns=["id"]
        ))
        platform.builder.add_foreign_key(Constraint(
            name="fk_comments_user",
            table="comments",
            columns=["user_id"],
            references_table="users",
            references_columns=["id"]
        ))
        m3 = platform.builder.build()
        print(f"  ✓ {m3.version}_{m3.name}")
        
        await asyncio.sleep(0.1)
        
        # Migration 4: Add column to users
        platform.builder.create_migration("add_avatar_to_users")
        platform.builder.add_column("users", Column(
            name="avatar_url",
            data_type="varchar(500)",
            nullable=True
        ))
        m4 = platform.builder.build()
        print(f"  ✓ {m4.version}_{m4.name}")
        
        await asyncio.sleep(0.1)
        
        # Migration 5: Seed data
        platform.builder.create_migration("seed_initial_data")
        platform.builder.seed_data("users", [
            {"email": "admin@example.com", "password_hash": "hashed_password", "name": "Admin User"},
            {"email": "user@example.com", "password_hash": "hashed_password", "name": "Regular User"},
        ])
        m5 = platform.builder.build()
        m5.migration_type = MigrationType.SEED
        print(f"  ✓ {m5.version}_{m5.name}")
        
        # Show pending migrations
        print("\n📋 Pending Migrations:")
        
        pending = platform.manager.get_pending_migrations()
        
        print("\n  ┌─────────────────────────────────────────────────────────────────────┐")
        print("  │ Version          │ Name                      │ Type    │ Ops │")
        print("  ├─────────────────────────────────────────────────────────────────────┤")
        
        for mig in pending:
            version = mig.version[:16].ljust(16)
            name = mig.name[:25].ljust(25)
            mtype = mig.migration_type.value[:7].ljust(7)
            ops = str(len(mig.operations)).ljust(3)
            print(f"  │ {version} │ {name} │ {mtype} │ {ops} │")
            
        print("  └─────────────────────────────────────────────────────────────────────┘")
        
        # Dry run
        print("\n🔍 Dry Run Preview:")
        print("\n  First migration SQL:")
        
        for op in m1.operations[:2]:
            sql = platform.manager.sql_generator.generate_up(op)
            # Show truncated SQL
            lines = sql.split("\n")
            for line in lines[:5]:
                print(f"    {line}")
            if len(lines) > 5:
                print(f"    ... ({len(lines) - 5} more lines)")
                
        # Execute migrations
        print("\n🚀 Executing Migrations...")
        
        applied = await platform.manager.migrate()
        
        print(f"\n  ✓ Applied {len(applied)} migrations")
        
        # Show applied migrations
        print("\n📊 Applied Migrations:")
        
        print("\n  ┌────────────────────────────────────────────────────────────────────────────┐")
        print("  │ Version          │ Name                      │ Status    │ Time (ms) │")
        print("  ├────────────────────────────────────────────────────────────────────────────┤")
        
        for mig in applied:
            version = mig.version[:16].ljust(16)
            name = mig.name[:25].ljust(25)
            status = mig.status.value[:9].ljust(9)
            time_ms = f"{mig.execution_time_ms:.2f}".ljust(9)
            print(f"  │ {version} │ {name} │ {status} │ {time_ms} │")
            
        print("  └────────────────────────────────────────────────────────────────────────────┘")
        
        # Migration history
        print("\n📜 Migration History:")
        
        for entry in platform.manager.history[-5:]:
            action_icon = "⬆️" if entry.action == "up" else "⬇️"
            print(f"  {action_icon} {entry.version}_{entry.name} - {entry.status.value}")
            
        # Test rollback
        print("\n⏪ Testing Rollback (1 step)...")
        
        rolled_back = await platform.manager.rollback(steps=1)
        
        if rolled_back:
            print(f"  ✓ Rolled back: {rolled_back[0].name}")
            
        # Re-apply
        print("\n🔄 Re-applying rolled back migration...")
        
        reapplied = await platform.manager.migrate()
        print(f"  ✓ Re-applied {len(reapplied)} migrations")
        
        # Executed SQL statements
        print("\n💾 Executed SQL Statements:")
        print(f"  Total statements executed: {len(platform.manager.executor.executed_statements)}")
        
        # Show some statements
        for stmt in platform.manager.executor.executed_statements[:3]:
            truncated = stmt[:80] + "..." if len(stmt) > 80 else stmt
            print(f"    • {truncated}")
            
        # Platform statistics
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Migrations: {stats['total_migrations']}")
        print(f"  Pending: {stats['pending_migrations']}")
        print(f"  Applied: {stats['applied_migrations']}")
        print(f"  Current Version: {stats['current_version']}")
        print(f"  History Entries: {stats['history_entries']}")
        
        # Dashboard
        print("\n┌────────────────────────────────────────────────────────────────────┐")
        print("│                 Database Migration Dashboard                        │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Database Type:                PostgreSQL                           │")
        print(f"│ Total Migrations:             {stats['total_migrations']:>10}                       │")
        print(f"│ Applied Migrations:           {stats['applied_migrations']:>10}                       │")
        print(f"│ Pending Migrations:           {stats['pending_migrations']:>10}                       │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Current Schema Version:       {stats['current_version'][:18].ljust(18)}              │")
        print(f"│ History Entries:              {stats['history_entries']:>10}                       │")
        print("└────────────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Database Migration Platform initialized!")
    print("=" * 60)
