#!/usr/bin/env python3
"""
Server Init - Iteration 247: CQRS Platform
Платформа CQRS (Command Query Responsibility Segregation)

Функционал:
- Command Bus - шина команд
- Query Bus - шина запросов
- Command Handlers - обработчики команд
- Query Handlers - обработчики запросов
- Read Models - модели чтения
- Write Models - модели записи
- Eventual Consistency - согласованность в конечном счете
- Command Validation - валидация команд
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Type
from enum import Enum
import uuid
import json


class CommandStatus(Enum):
    """Статус команды"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"


class QueryStatus(Enum):
    """Статус запроса"""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"


class ConsistencyLevel(Enum):
    """Уровень согласованности"""
    STRONG = "strong"
    EVENTUAL = "eventual"
    CAUSAL = "causal"


@dataclass
class Command:
    """Команда"""
    command_id: str
    command_type: str = ""
    
    # Payload
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    aggregate_id: str = ""
    
    # Status
    status: CommandStatus = CommandStatus.PENDING
    
    # Result
    result: Any = None
    error: str = ""
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    
    # Validation
    is_valid: bool = True
    validation_errors: List[str] = field(default_factory=list)


@dataclass
class Query:
    """Запрос"""
    query_id: str
    query_type: str = ""
    
    # Parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    status: QueryStatus = QueryStatus.PENDING
    
    # Result
    result: Any = None
    error: str = ""
    
    # Caching
    cache_key: str = ""
    from_cache: bool = False
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    executed_at: Optional[datetime] = None
    execution_time_ms: float = 0


@dataclass
class CommandHandler:
    """Обработчик команд"""
    handler_id: str
    command_type: str = ""
    
    # Handler function (simulated)
    handler_name: str = ""
    
    # Options
    is_async: bool = False
    timeout_ms: int = 5000
    retry_count: int = 3
    
    # Stats
    invocations: int = 0
    successes: int = 0
    failures: int = 0
    avg_duration_ms: float = 0


@dataclass
class QueryHandler:
    """Обработчик запросов"""
    handler_id: str
    query_type: str = ""
    
    # Handler function (simulated)
    handler_name: str = ""
    
    # Options
    cache_enabled: bool = True
    cache_ttl_seconds: int = 300
    
    # Stats
    invocations: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    avg_duration_ms: float = 0


@dataclass
class ReadModel:
    """Модель чтения"""
    model_id: str
    name: str = ""
    
    # Data
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Version
    version: int = 0
    last_event_id: str = ""
    
    # Sync
    is_synchronized: bool = True
    lag_events: int = 0
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class WriteModel:
    """Модель записи"""
    model_id: str
    name: str = ""
    aggregate_type: str = ""
    
    # State
    state: Dict[str, Any] = field(default_factory=dict)
    
    # Version
    version: int = 0
    
    # Pending changes
    pending_changes: List[Dict] = field(default_factory=list)
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)


class CQRSPlatform:
    """Платформа CQRS"""
    
    def __init__(self):
        self.commands: Dict[str, Command] = {}
        self.queries: Dict[str, Query] = {}
        self.command_handlers: Dict[str, CommandHandler] = {}
        self.query_handlers: Dict[str, QueryHandler] = {}
        self.read_models: Dict[str, ReadModel] = {}
        self.write_models: Dict[str, WriteModel] = {}
        
        # Query cache
        self.query_cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        
        # Command queue
        self.command_queue: List[str] = []
        
        # Stats
        self._command_durations: List[float] = []
        self._query_durations: List[float] = []
        
    def register_command_handler(self, command_type: str, handler_name: str,
                                 is_async: bool = False,
                                 timeout_ms: int = 5000) -> CommandHandler:
        """Регистрация обработчика команд"""
        handler = CommandHandler(
            handler_id=f"ch_{uuid.uuid4().hex[:8]}",
            command_type=command_type,
            handler_name=handler_name,
            is_async=is_async,
            timeout_ms=timeout_ms
        )
        
        self.command_handlers[command_type] = handler
        return handler
        
    def register_query_handler(self, query_type: str, handler_name: str,
                              cache_enabled: bool = True,
                              cache_ttl_seconds: int = 300) -> QueryHandler:
        """Регистрация обработчика запросов"""
        handler = QueryHandler(
            handler_id=f"qh_{uuid.uuid4().hex[:8]}",
            query_type=query_type,
            handler_name=handler_name,
            cache_enabled=cache_enabled,
            cache_ttl_seconds=cache_ttl_seconds
        )
        
        self.query_handlers[query_type] = handler
        return handler
        
    def validate_command(self, command: Command) -> bool:
        """Валидация команды"""
        errors = []
        
        if not command.command_type:
            errors.append("Command type is required")
            
        if not command.payload:
            errors.append("Command payload is required")
            
        # Type-specific validation
        if command.command_type == "CreateUser":
            if "email" not in command.payload:
                errors.append("Email is required for CreateUser")
            if "name" not in command.payload:
                errors.append("Name is required for CreateUser")
                
        elif command.command_type == "PlaceOrder":
            if "items" not in command.payload or not command.payload["items"]:
                errors.append("Items are required for PlaceOrder")
                
        command.validation_errors = errors
        command.is_valid = len(errors) == 0
        
        return command.is_valid
        
    async def dispatch_command(self, command_type: str,
                              payload: Dict[str, Any],
                              aggregate_id: str = "",
                              metadata: Dict[str, Any] = None) -> Command:
        """Отправка команды"""
        command = Command(
            command_id=f"cmd_{uuid.uuid4().hex[:8]}",
            command_type=command_type,
            payload=payload,
            aggregate_id=aggregate_id or str(uuid.uuid4()),
            metadata=metadata or {}
        )
        
        # Validate
        if not self.validate_command(command):
            command.status = CommandStatus.REJECTED
            self.commands[command.command_id] = command
            return command
            
        # Find handler
        handler = self.command_handlers.get(command_type)
        if not handler:
            command.status = CommandStatus.FAILED
            command.error = f"No handler for command type: {command_type}"
            self.commands[command.command_id] = command
            return command
            
        # Process command
        command.status = CommandStatus.PROCESSING
        start_time = datetime.now()
        
        try:
            # Simulate processing
            await asyncio.sleep(random.uniform(0.01, 0.1))
            
            # Simulate occasional failures
            if random.random() > 0.95:
                raise Exception("Random processing error")
                
            # Update write model
            self._update_write_model(command)
            
            command.status = CommandStatus.COMPLETED
            command.result = {"success": True, "aggregate_id": command.aggregate_id}
            
            handler.successes += 1
            
        except Exception as e:
            command.status = CommandStatus.FAILED
            command.error = str(e)
            handler.failures += 1
            
        finally:
            command.processed_at = datetime.now()
            duration = (command.processed_at - start_time).total_seconds() * 1000
            
            handler.invocations += 1
            handler.avg_duration_ms = (
                (handler.avg_duration_ms * (handler.invocations - 1) + duration)
                / handler.invocations
            )
            
            self._command_durations.append(duration)
            
        self.commands[command.command_id] = command
        
        # Sync read models (eventual consistency)
        self._sync_read_models(command)
        
        return command
        
    def _update_write_model(self, command: Command):
        """Обновление модели записи"""
        model_id = f"write_{command.aggregate_id}"
        
        if model_id not in self.write_models:
            self.write_models[model_id] = WriteModel(
                model_id=model_id,
                name=command.command_type,
                aggregate_type=command.command_type.replace("Create", "").replace("Update", "")
            )
            
        model = self.write_models[model_id]
        model.version += 1
        model.last_modified = datetime.now()
        
        # Apply changes
        for key, value in command.payload.items():
            model.state[key] = value
            
    def _sync_read_models(self, command: Command):
        """Синхронизация моделей чтения"""
        # Find or create read model
        model_id = f"read_{command.aggregate_id}"
        
        if model_id not in self.read_models:
            self.read_models[model_id] = ReadModel(
                model_id=model_id,
                name=command.command_type
            )
            
        model = self.read_models[model_id]
        model.version += 1
        model.last_event_id = command.command_id
        model.last_updated = datetime.now()
        
        # Copy data from command
        for key, value in command.payload.items():
            model.data[key] = value
            
        model.is_synchronized = True
        
    async def execute_query(self, query_type: str,
                           parameters: Dict[str, Any] = None,
                           metadata: Dict[str, Any] = None) -> Query:
        """Выполнение запроса"""
        query = Query(
            query_id=f"qry_{uuid.uuid4().hex[:8]}",
            query_type=query_type,
            parameters=parameters or {},
            metadata=metadata or {}
        )
        
        # Generate cache key
        query.cache_key = f"{query_type}:{json.dumps(parameters or {}, sort_keys=True)}"
        
        # Find handler
        handler = self.query_handlers.get(query_type)
        if not handler:
            query.status = QueryStatus.FAILED
            query.error = f"No handler for query type: {query_type}"
            self.queries[query.query_id] = query
            return query
            
        # Check cache
        if handler.cache_enabled:
            cached = self._get_from_cache(query.cache_key, handler.cache_ttl_seconds)
            if cached is not None:
                query.result = cached
                query.status = QueryStatus.CACHED
                query.from_cache = True
                query.executed_at = datetime.now()
                handler.cache_hits += 1
                self.queries[query.query_id] = query
                return query
                
            handler.cache_misses += 1
            
        # Execute query
        query.status = QueryStatus.EXECUTING
        start_time = datetime.now()
        
        try:
            # Simulate query execution
            await asyncio.sleep(random.uniform(0.005, 0.05))
            
            # Get data from read models
            result = self._execute_read_query(query)
            
            query.result = result
            query.status = QueryStatus.COMPLETED
            
            # Update cache
            if handler.cache_enabled:
                self._set_cache(query.cache_key, result)
                
        except Exception as e:
            query.status = QueryStatus.FAILED
            query.error = str(e)
            
        finally:
            query.executed_at = datetime.now()
            duration = (query.executed_at - start_time).total_seconds() * 1000
            query.execution_time_ms = duration
            
            handler.invocations += 1
            handler.avg_duration_ms = (
                (handler.avg_duration_ms * (handler.invocations - 1) + duration)
                / handler.invocations
            )
            
            self._query_durations.append(duration)
            
        self.queries[query.query_id] = query
        return query
        
    def _execute_read_query(self, query: Query) -> Any:
        """Выполнение запроса к моделям чтения"""
        if query.query_type == "GetUser":
            user_id = query.parameters.get("user_id")
            model = self.read_models.get(f"read_{user_id}")
            return model.data if model else None
            
        elif query.query_type == "ListUsers":
            users = []
            for model in self.read_models.values():
                if "email" in model.data:
                    users.append(model.data)
            return users
            
        elif query.query_type == "GetOrder":
            order_id = query.parameters.get("order_id")
            model = self.read_models.get(f"read_{order_id}")
            return model.data if model else None
            
        return None
        
    def _get_from_cache(self, key: str, ttl_seconds: int) -> Any:
        """Получение из кэша"""
        if key not in self.query_cache:
            return None
            
        timestamp = self.cache_timestamps.get(key)
        if timestamp and (datetime.now() - timestamp).total_seconds() > ttl_seconds:
            del self.query_cache[key]
            del self.cache_timestamps[key]
            return None
            
        return self.query_cache[key]
        
    def _set_cache(self, key: str, value: Any):
        """Сохранение в кэш"""
        self.query_cache[key] = value
        self.cache_timestamps[key] = datetime.now()
        
    def create_read_model(self, name: str) -> ReadModel:
        """Создание модели чтения"""
        model = ReadModel(
            model_id=f"rm_{uuid.uuid4().hex[:8]}",
            name=name
        )
        
        self.read_models[model.model_id] = model
        return model
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_commands = len(self.commands)
        completed_commands = sum(1 for c in self.commands.values() if c.status == CommandStatus.COMPLETED)
        failed_commands = sum(1 for c in self.commands.values() if c.status == CommandStatus.FAILED)
        
        total_queries = len(self.queries)
        cached_queries = sum(1 for q in self.queries.values() if q.from_cache)
        
        avg_command_time = sum(self._command_durations) / len(self._command_durations) if self._command_durations else 0
        avg_query_time = sum(self._query_durations) / len(self._query_durations) if self._query_durations else 0
        
        return {
            "total_commands": total_commands,
            "completed_commands": completed_commands,
            "failed_commands": failed_commands,
            "total_queries": total_queries,
            "cached_queries": cached_queries,
            "cache_hit_rate": cached_queries / total_queries * 100 if total_queries > 0 else 0,
            "command_handlers": len(self.command_handlers),
            "query_handlers": len(self.query_handlers),
            "read_models": len(self.read_models),
            "write_models": len(self.write_models),
            "avg_command_time_ms": avg_command_time,
            "avg_query_time_ms": avg_query_time
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 247: CQRS Platform")
    print("=" * 60)
    
    platform = CQRSPlatform()
    print("✓ CQRS Platform created")
    
    # Register command handlers
    print("\n📝 Registering Command Handlers...")
    
    command_handlers = [
        ("CreateUser", "UserCommandHandler.handleCreate"),
        ("UpdateUser", "UserCommandHandler.handleUpdate"),
        ("DeleteUser", "UserCommandHandler.handleDelete"),
        ("PlaceOrder", "OrderCommandHandler.handlePlace"),
        ("CancelOrder", "OrderCommandHandler.handleCancel"),
        ("ProcessPayment", "PaymentCommandHandler.handleProcess"),
    ]
    
    for cmd_type, handler_name in command_handlers:
        platform.register_command_handler(cmd_type, handler_name)
        print(f"  📝 {cmd_type} → {handler_name}")
        
    # Register query handlers
    print("\n🔍 Registering Query Handlers...")
    
    query_handlers = [
        ("GetUser", "UserQueryHandler.getById", True, 300),
        ("ListUsers", "UserQueryHandler.list", True, 60),
        ("GetOrder", "OrderQueryHandler.getById", True, 300),
        ("ListOrders", "OrderQueryHandler.list", True, 60),
        ("GetOrderStats", "OrderQueryHandler.getStats", True, 30),
    ]
    
    for query_type, handler_name, cache, ttl in query_handlers:
        platform.register_query_handler(query_type, handler_name, cache, ttl)
        cache_str = f"cache={ttl}s" if cache else "no cache"
        print(f"  🔍 {query_type} → {handler_name} ({cache_str})")
        
    # Dispatch commands
    print("\n⚡ Dispatching Commands...")
    
    # Create users
    users_data = [
        {"name": "Alice Johnson", "email": "alice@example.com", "role": "admin"},
        {"name": "Bob Smith", "email": "bob@example.com", "role": "user"},
        {"name": "Carol Davis", "email": "carol@example.com", "role": "user"},
    ]
    
    user_ids = []
    for data in users_data:
        cmd = await platform.dispatch_command("CreateUser", data)
        user_ids.append(cmd.aggregate_id)
        status = "✓" if cmd.status == CommandStatus.COMPLETED else "✗"
        print(f"  {status} CreateUser: {data['name']} (id: {cmd.aggregate_id[:8]}...)")
        
    # Place orders
    orders_data = [
        {"items": [{"product": "Widget", "qty": 2}], "total": 59.98, "user_id": user_ids[0]},
        {"items": [{"product": "Gadget", "qty": 1}], "total": 149.99, "user_id": user_ids[1]},
    ]
    
    order_ids = []
    for data in orders_data:
        cmd = await platform.dispatch_command("PlaceOrder", data)
        order_ids.append(cmd.aggregate_id)
        status = "✓" if cmd.status == CommandStatus.COMPLETED else "✗"
        print(f"  {status} PlaceOrder: ${data['total']} (id: {cmd.aggregate_id[:8]}...)")
        
    # Invalid command
    invalid_cmd = await platform.dispatch_command("CreateUser", {})
    status = "✓" if invalid_cmd.status == CommandStatus.REJECTED else "✗"
    print(f"  {status} CreateUser (invalid): {invalid_cmd.validation_errors}")
    
    # Execute queries
    print("\n🔍 Executing Queries...")
    
    # Get user
    query = await platform.execute_query("GetUser", {"user_id": user_ids[0]})
    cached = "(cached)" if query.from_cache else ""
    print(f"  ✓ GetUser: {query.result} {cached}")
    
    # Same query again (should be cached)
    query2 = await platform.execute_query("GetUser", {"user_id": user_ids[0]})
    cached = "(cached)" if query2.from_cache else ""
    print(f"  ✓ GetUser: {query2.result.get('name') if query2.result else None} {cached}")
    
    # List users
    query3 = await platform.execute_query("ListUsers", {})
    cached = "(cached)" if query3.from_cache else ""
    print(f"  ✓ ListUsers: {len(query3.result or [])} users {cached}")
    
    # Display command handlers
    print("\n📝 Command Handlers:")
    
    print("\n  ┌───────────────────┬───────────┬───────────┬───────────┬──────────┐")
    print("  │ Command Type      │ Calls     │ Success   │ Failures  │ Avg (ms) │")
    print("  ├───────────────────┼───────────┼───────────┼───────────┼──────────┤")
    
    for handler in platform.command_handlers.values():
        cmd_type = handler.command_type[:17].ljust(17)
        calls = str(handler.invocations)[:9].ljust(9)
        success = str(handler.successes)[:9].ljust(9)
        failures = str(handler.failures)[:9].ljust(9)
        avg_ms = f"{handler.avg_duration_ms:.1f}"[:8].ljust(8)
        
        print(f"  │ {cmd_type} │ {calls} │ {success} │ {failures} │ {avg_ms} │")
        
    print("  └───────────────────┴───────────┴───────────┴───────────┴──────────┘")
    
    # Display query handlers
    print("\n🔍 Query Handlers:")
    
    print("\n  ┌───────────────────┬───────────┬───────────┬───────────┬──────────┐")
    print("  │ Query Type        │ Calls     │ Hits      │ Misses    │ Avg (ms) │")
    print("  ├───────────────────┼───────────┼───────────┼───────────┼──────────┤")
    
    for handler in platform.query_handlers.values():
        query_type = handler.query_type[:17].ljust(17)
        calls = str(handler.invocations)[:9].ljust(9)
        hits = str(handler.cache_hits)[:9].ljust(9)
        misses = str(handler.cache_misses)[:9].ljust(9)
        avg_ms = f"{handler.avg_duration_ms:.1f}"[:8].ljust(8)
        
        print(f"  │ {query_type} │ {calls} │ {hits} │ {misses} │ {avg_ms} │")
        
    print("  └───────────────────┴───────────┴───────────┴───────────┴──────────┘")
    
    # Read/Write models
    print("\n📊 Read Models:")
    
    for model in list(platform.read_models.values())[:5]:
        sync = "🟢" if model.is_synchronized else "🟡"
        print(f"  {sync} {model.model_id[:20]}: v{model.version}, data={json.dumps(model.data)[:40]}...")
        
    print("\n📝 Write Models:")
    
    for model in list(platform.write_models.values())[:5]:
        print(f"  📝 {model.model_id[:20]}: v{model.version}, state={json.dumps(model.state)[:40]}...")
        
    # CQRS flow diagram
    print("\n📐 CQRS Flow:")
    
    print("""
    ┌─────────────────────────────────────────────────────────────┐
    │                        Client                                │
    └────────────┬───────────────────────────────────┬────────────┘
                 │                                   │
          ┌──────▼──────┐                    ┌───────▼──────┐
          │   Commands  │                    │    Queries   │
          └──────┬──────┘                    └───────┬──────┘
                 │                                   │
          ┌──────▼──────┐                    ┌───────▼──────┐
          │  Command    │                    │   Query      │
          │  Handlers   │                    │   Handlers   │
          └──────┬──────┘                    └───────┬──────┘
                 │                                   │
          ┌──────▼──────┐                    ┌───────▼──────┐
          │   Write     │═══ Events ═══════>│    Read      │
          │   Model     │                    │    Models    │
          └─────────────┘                    └──────────────┘
    """)
    
    # Statistics
    print("\n📊 Platform Statistics:")
    
    stats = platform.get_statistics()
    
    print(f"\n  Total Commands: {stats['total_commands']}")
    print(f"  Completed: {stats['completed_commands']}")
    print(f"  Failed: {stats['failed_commands']}")
    
    print(f"\n  Total Queries: {stats['total_queries']}")
    print(f"  Cache Hit Rate: {stats['cache_hit_rate']:.1f}%")
    
    print(f"\n  Command Handlers: {stats['command_handlers']}")
    print(f"  Query Handlers: {stats['query_handlers']}")
    print(f"  Read Models: {stats['read_models']}")
    print(f"  Write Models: {stats['write_models']}")
    
    print(f"\n  Avg Command Time: {stats['avg_command_time_ms']:.2f}ms")
    print(f"  Avg Query Time: {stats['avg_query_time_ms']:.2f}ms")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                        CQRS Dashboard                               │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Commands Processed:            {stats['completed_commands']:>12}                        │")
    print(f"│ Queries Executed:              {stats['total_queries']:>12}                        │")
    print(f"│ Cache Hit Rate:                   {stats['cache_hit_rate']:>7.1f}%                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Avg Command Time:                 {stats['avg_command_time_ms']:>7.2f}ms                      │")
    print(f"│ Avg Query Time:                   {stats['avg_query_time_ms']:>7.2f}ms                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("CQRS Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
