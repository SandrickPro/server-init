#!/usr/bin/env python3
"""
Server Init - Iteration 121: GraphQL Gateway Platform
Платформа GraphQL шлюза

Функционал:
- Schema Definition - определение схемы
- Resolvers - резолверы
- Query Execution - выполнение запросов
- Mutations - мутации
- Subscriptions - подписки
- Federation - федерация
- Caching - кэширование
- Rate Limiting - ограничение запросов
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Union
from enum import Enum
from collections import defaultdict
import uuid
import random
import hashlib


class GraphQLType(Enum):
    """Тип GraphQL"""
    SCALAR = "scalar"
    OBJECT = "object"
    INPUT = "input"
    ENUM = "enum"
    INTERFACE = "interface"
    UNION = "union"


class OperationType(Enum):
    """Тип операции"""
    QUERY = "query"
    MUTATION = "mutation"
    SUBSCRIPTION = "subscription"


class CacheStrategy(Enum):
    """Стратегия кэширования"""
    NONE = "none"
    TTL = "ttl"
    LRU = "lru"
    PER_USER = "per_user"


@dataclass
class FieldDefinition:
    """Определение поля"""
    name: str
    type_name: str = "String"
    
    # Modifiers
    is_list: bool = False
    is_non_null: bool = False
    is_list_item_non_null: bool = False
    
    # Arguments
    arguments: Dict[str, str] = field(default_factory=dict)
    
    # Directives
    deprecated: bool = False
    deprecation_reason: str = ""
    
    # Resolver
    resolver_name: str = ""


@dataclass
class TypeDefinition:
    """Определение типа"""
    name: str
    type_kind: GraphQLType = GraphQLType.OBJECT
    
    # Fields
    fields: Dict[str, FieldDefinition] = field(default_factory=dict)
    
    # For enum
    enum_values: List[str] = field(default_factory=list)
    
    # For interface/union
    implements: List[str] = field(default_factory=list)
    possible_types: List[str] = field(default_factory=list)
    
    # Description
    description: str = ""


@dataclass
class Operation:
    """Операция GraphQL"""
    operation_id: str
    operation_type: OperationType = OperationType.QUERY
    
    # Query
    query: str = ""
    operation_name: str = ""
    
    # Variables
    variables: Dict[str, Any] = field(default_factory=dict)
    
    # Result
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timing
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    
    # Stats
    resolver_calls: int = 0


@dataclass
class Resolver:
    """Резолвер"""
    resolver_id: str
    type_name: str = ""
    field_name: str = ""
    
    # Handler
    handler: Optional[Callable] = None
    
    # Stats
    call_count: int = 0
    total_time_ms: float = 0.0
    error_count: int = 0


@dataclass
class Subscription:
    """Подписка GraphQL"""
    subscription_id: str
    query: str = ""
    
    # Client
    client_id: str = ""
    
    # Status
    active: bool = True
    
    # Events
    events_sent: int = 0
    last_event_at: Optional[datetime] = None


@dataclass
class FederatedService:
    """Федеративный сервис"""
    service_id: str
    name: str = ""
    url: str = ""
    
    # Schema
    types_provided: List[str] = field(default_factory=list)
    
    # Status
    healthy: bool = True
    last_check: Optional[datetime] = None


@dataclass
class CacheEntry:
    """Запись кэша"""
    key: str
    value: Any = None
    
    # TTL
    expires_at: Optional[datetime] = None
    
    # Stats
    hits: int = 0


class SchemaBuilder:
    """Построитель схемы"""
    
    def __init__(self):
        self.types: Dict[str, TypeDefinition] = {}
        self._init_scalars()
        
    def _init_scalars(self):
        """Инициализация скаляров"""
        scalars = ["String", "Int", "Float", "Boolean", "ID", "DateTime", "JSON"]
        for scalar in scalars:
            self.types[scalar] = TypeDefinition(
                name=scalar,
                type_kind=GraphQLType.SCALAR
            )
            
    def add_type(self, name: str, type_kind: GraphQLType = GraphQLType.OBJECT,
                  description: str = "") -> TypeDefinition:
        """Добавление типа"""
        type_def = TypeDefinition(
            name=name,
            type_kind=type_kind,
            description=description
        )
        self.types[name] = type_def
        return type_def
        
    def add_field(self, type_name: str, field_name: str,
                   field_type: str, **kwargs) -> FieldDefinition:
        """Добавление поля"""
        type_def = self.types.get(type_name)
        if not type_def:
            return None
            
        field_def = FieldDefinition(
            name=field_name,
            type_name=field_type,
            **kwargs
        )
        
        type_def.fields[field_name] = field_def
        return field_def
        
    def add_enum(self, name: str, values: List[str]) -> TypeDefinition:
        """Добавление enum"""
        type_def = TypeDefinition(
            name=name,
            type_kind=GraphQLType.ENUM,
            enum_values=values
        )
        self.types[name] = type_def
        return type_def
        
    def get_schema_sdl(self) -> str:
        """Получение SDL схемы"""
        lines = []
        
        for type_def in self.types.values():
            if type_def.type_kind == GraphQLType.SCALAR:
                continue
                
            if type_def.type_kind == GraphQLType.ENUM:
                lines.append(f"enum {type_def.name} {{")
                for val in type_def.enum_values:
                    lines.append(f"  {val}")
                lines.append("}")
            else:
                implements = f" implements {', '.join(type_def.implements)}" if type_def.implements else ""
                lines.append(f"type {type_def.name}{implements} {{")
                for field in type_def.fields.values():
                    type_str = field.type_name
                    if field.is_list:
                        item_null = "!" if field.is_list_item_non_null else ""
                        type_str = f"[{type_str}{item_null}]"
                    if field.is_non_null:
                        type_str += "!"
                    lines.append(f"  {field.name}: {type_str}")
                lines.append("}")
                
            lines.append("")
            
        return "\n".join(lines)


class ResolverRegistry:
    """Реестр резолверов"""
    
    def __init__(self):
        self.resolvers: Dict[str, Resolver] = {}
        
    def register(self, type_name: str, field_name: str,
                  handler: Callable) -> Resolver:
        """Регистрация резолвера"""
        key = f"{type_name}.{field_name}"
        
        resolver = Resolver(
            resolver_id=f"res_{uuid.uuid4().hex[:8]}",
            type_name=type_name,
            field_name=field_name,
            handler=handler
        )
        
        self.resolvers[key] = resolver
        return resolver
        
    def get(self, type_name: str, field_name: str) -> Optional[Resolver]:
        """Получение резолвера"""
        key = f"{type_name}.{field_name}"
        return self.resolvers.get(key)
        
    async def execute(self, type_name: str, field_name: str,
                       parent: Any, args: Dict[str, Any],
                       context: Dict[str, Any]) -> Any:
        """Выполнение резолвера"""
        resolver = self.get(type_name, field_name)
        if not resolver or not resolver.handler:
            # Default resolver - get attribute from parent
            if isinstance(parent, dict):
                return parent.get(field_name)
            return getattr(parent, field_name, None)
            
        start = datetime.now()
        
        try:
            result = await resolver.handler(parent, args, context)
            resolver.call_count += 1
            resolver.total_time_ms += (datetime.now() - start).total_seconds() * 1000
            return result
        except Exception as e:
            resolver.error_count += 1
            raise


class QueryCache:
    """Кэш запросов"""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        
    def get(self, key: str) -> Optional[Any]:
        """Получение из кэша"""
        entry = self.cache.get(key)
        if not entry:
            return None
            
        # Check expiry
        if entry.expires_at and entry.expires_at < datetime.now():
            del self.cache[key]
            return None
            
        entry.hits += 1
        return entry.value
        
    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """Запись в кэш"""
        # Evict if full
        if len(self.cache) >= self.max_size:
            oldest = min(self.cache.keys())
            del self.cache[oldest]
            
        self.cache[key] = CacheEntry(
            key=key,
            value=value,
            expires_at=datetime.now() + timedelta(seconds=ttl_seconds)
        )
        
    def invalidate(self, key: str):
        """Инвалидация"""
        if key in self.cache:
            del self.cache[key]
            
    def clear(self):
        """Очистка"""
        self.cache.clear()
        
    def stats(self) -> Dict[str, Any]:
        """Статистика"""
        total_hits = sum(e.hits for e in self.cache.values())
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "total_hits": total_hits
        }


class GraphQLExecutor:
    """Исполнитель GraphQL"""
    
    def __init__(self, schema: SchemaBuilder, resolvers: ResolverRegistry):
        self.schema = schema
        self.resolvers = resolvers
        self.cache = QueryCache()
        self.operations: List[Operation] = []
        
    async def execute(self, query: str,
                       variables: Dict[str, Any] = None,
                       operation_name: str = None,
                       context: Dict[str, Any] = None) -> Operation:
        """Выполнение запроса"""
        operation = Operation(
            operation_id=f"op_{uuid.uuid4().hex[:8]}",
            query=query,
            operation_name=operation_name or "",
            variables=variables or {},
            started_at=datetime.now()
        )
        
        # Check cache
        cache_key = hashlib.md5(f"{query}{json.dumps(variables or {})}".encode()).hexdigest()
        cached = self.cache.get(cache_key)
        if cached:
            operation.data = cached
            operation.finished_at = datetime.now()
            self.operations.append(operation)
            return operation
            
        # Parse and execute (simplified)
        try:
            # Simulate execution
            await asyncio.sleep(random.uniform(0.01, 0.05))
            
            # Generate mock result based on query
            operation.data = await self._execute_selection(query, context or {})
            operation.resolver_calls = random.randint(1, 10)
            
            # Cache result
            self.cache.set(cache_key, operation.data)
            
        except Exception as e:
            operation.errors.append({
                "message": str(e),
                "locations": [],
                "path": []
            })
            
        operation.finished_at = datetime.now()
        self.operations.append(operation)
        return operation
        
    async def _execute_selection(self, query: str,
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение выборки"""
        # Simplified mock execution
        result = {}
        
        if "users" in query.lower():
            result["users"] = [
                {"id": "1", "name": "User 1", "email": "user1@example.com"},
                {"id": "2", "name": "User 2", "email": "user2@example.com"}
            ]
            
        if "products" in query.lower():
            result["products"] = [
                {"id": "1", "name": "Product A", "price": 29.99},
                {"id": "2", "name": "Product B", "price": 49.99}
            ]
            
        if "orders" in query.lower():
            result["orders"] = [
                {"id": "1", "status": "PENDING", "total": 79.98}
            ]
            
        return result


class SubscriptionManager:
    """Менеджер подписок"""
    
    def __init__(self):
        self.subscriptions: Dict[str, Subscription] = {}
        self.handlers: Dict[str, Callable] = {}
        
    def subscribe(self, client_id: str, query: str) -> Subscription:
        """Создание подписки"""
        subscription = Subscription(
            subscription_id=f"sub_{uuid.uuid4().hex[:8]}",
            client_id=client_id,
            query=query
        )
        
        self.subscriptions[subscription.subscription_id] = subscription
        return subscription
        
    def unsubscribe(self, subscription_id: str):
        """Отмена подписки"""
        if subscription_id in self.subscriptions:
            self.subscriptions[subscription_id].active = False
            del self.subscriptions[subscription_id]
            
    async def publish(self, event_type: str, data: Dict[str, Any]):
        """Публикация события"""
        for sub in self.subscriptions.values():
            if sub.active and event_type.lower() in sub.query.lower():
                sub.events_sent += 1
                sub.last_event_at = datetime.now()


class FederationManager:
    """Менеджер федерации"""
    
    def __init__(self):
        self.services: Dict[str, FederatedService] = {}
        
    def register_service(self, name: str, url: str,
                          types: List[str]) -> FederatedService:
        """Регистрация сервиса"""
        service = FederatedService(
            service_id=f"fed_{uuid.uuid4().hex[:8]}",
            name=name,
            url=url,
            types_provided=types
        )
        
        self.services[service.service_id] = service
        return service
        
    async def health_check(self):
        """Проверка здоровья"""
        for service in self.services.values():
            # Simulate health check
            service.healthy = random.random() > 0.1
            service.last_check = datetime.now()


class RateLimiter:
    """Ограничитель запросов"""
    
    def __init__(self, requests_per_minute: int = 100):
        self.limit = requests_per_minute
        self.requests: Dict[str, List[datetime]] = defaultdict(list)
        
    def check(self, client_id: str) -> bool:
        """Проверка лимита"""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old requests
        self.requests[client_id] = [
            t for t in self.requests[client_id] if t > minute_ago
        ]
        
        if len(self.requests[client_id]) >= self.limit:
            return False
            
        self.requests[client_id].append(now)
        return True


class GraphQLGatewayPlatform:
    """Платформа GraphQL шлюза"""
    
    def __init__(self):
        self.schema = SchemaBuilder()
        self.resolvers = ResolverRegistry()
        self.executor = GraphQLExecutor(self.schema, self.resolvers)
        self.subscriptions = SubscriptionManager()
        self.federation = FederationManager()
        self.rate_limiter = RateLimiter()
        
    async def query(self, query: str, variables: Dict[str, Any] = None,
                     client_id: str = "anonymous") -> Operation:
        """Выполнение запроса"""
        if not self.rate_limiter.check(client_id):
            op = Operation(
                operation_id=f"op_{uuid.uuid4().hex[:8]}",
                query=query
            )
            op.errors.append({"message": "Rate limit exceeded"})
            return op
            
        return await self.executor.execute(query, variables)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        operations = self.executor.operations
        
        total_time = sum(
            (op.finished_at - op.started_at).total_seconds() * 1000
            for op in operations if op.finished_at
        )
        
        return {
            "total_types": len(self.schema.types),
            "total_resolvers": len(self.resolvers.resolvers),
            "total_operations": len(operations),
            "successful_operations": len([op for op in operations if not op.errors]),
            "failed_operations": len([op for op in operations if op.errors]),
            "avg_execution_time_ms": total_time / len(operations) if operations else 0,
            "cache_stats": self.executor.cache.stats(),
            "active_subscriptions": len([s for s in self.subscriptions.subscriptions.values() if s.active]),
            "federated_services": len(self.federation.services)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 121: GraphQL Gateway Platform")
    print("=" * 60)
    
    async def demo():
        platform = GraphQLGatewayPlatform()
        print("✓ GraphQL Gateway Platform created")
        
        # Build schema
        print("\n📐 Building GraphQL Schema...")
        
        # Add enums
        platform.schema.add_enum("UserStatus", ["ACTIVE", "INACTIVE", "PENDING"])
        platform.schema.add_enum("OrderStatus", ["PENDING", "CONFIRMED", "SHIPPED", "DELIVERED"])
        print("  ✓ Enums: UserStatus, OrderStatus")
        
        # Add types
        user_type = platform.schema.add_type("User", description="User account")
        platform.schema.add_field("User", "id", "ID", is_non_null=True)
        platform.schema.add_field("User", "name", "String", is_non_null=True)
        platform.schema.add_field("User", "email", "String", is_non_null=True)
        platform.schema.add_field("User", "status", "UserStatus")
        platform.schema.add_field("User", "orders", "Order", is_list=True)
        print("  ✓ Type: User (5 fields)")
        
        product_type = platform.schema.add_type("Product", description="Product in catalog")
        platform.schema.add_field("Product", "id", "ID", is_non_null=True)
        platform.schema.add_field("Product", "name", "String", is_non_null=True)
        platform.schema.add_field("Product", "price", "Float", is_non_null=True)
        platform.schema.add_field("Product", "inStock", "Boolean")
        print("  ✓ Type: Product (4 fields)")
        
        order_type = platform.schema.add_type("Order", description="Customer order")
        platform.schema.add_field("Order", "id", "ID", is_non_null=True)
        platform.schema.add_field("Order", "status", "OrderStatus")
        platform.schema.add_field("Order", "total", "Float")
        platform.schema.add_field("Order", "user", "User")
        platform.schema.add_field("Order", "items", "OrderItem", is_list=True)
        print("  ✓ Type: Order (5 fields)")
        
        # Add Query type
        query_type = platform.schema.add_type("Query", description="Root query type")
        platform.schema.add_field("Query", "users", "User", is_list=True, 
                                    arguments={"limit": "Int", "offset": "Int"})
        platform.schema.add_field("Query", "user", "User",
                                    arguments={"id": "ID!"})
        platform.schema.add_field("Query", "products", "Product", is_list=True)
        platform.schema.add_field("Query", "orders", "Order", is_list=True)
        print("  ✓ Type: Query (4 fields)")
        
        # Add Mutation type
        mutation_type = platform.schema.add_type("Mutation", description="Root mutation type")
        platform.schema.add_field("Mutation", "createUser", "User",
                                    arguments={"input": "CreateUserInput!"})
        platform.schema.add_field("Mutation", "createOrder", "Order",
                                    arguments={"input": "CreateOrderInput!"})
        print("  ✓ Type: Mutation (2 fields)")
        
        # Register resolvers
        print("\n🔧 Registering Resolvers...")
        
        async def resolve_users(parent, args, context):
            return [
                {"id": "1", "name": "Alice", "email": "alice@example.com", "status": "ACTIVE"},
                {"id": "2", "name": "Bob", "email": "bob@example.com", "status": "ACTIVE"}
            ]
            
        async def resolve_products(parent, args, context):
            return [
                {"id": "1", "name": "Widget", "price": 29.99, "inStock": True},
                {"id": "2", "name": "Gadget", "price": 49.99, "inStock": False}
            ]
            
        platform.resolvers.register("Query", "users", resolve_users)
        platform.resolvers.register("Query", "products", resolve_products)
        
        print(f"  ✓ Query.users resolver")
        print(f"  ✓ Query.products resolver")
        
        # Execute queries
        print("\n🚀 Executing GraphQL Queries...")
        
        queries = [
            ("GetUsers", "query GetUsers { users { id name email } }"),
            ("GetProducts", "query GetProducts { products { id name price } }"),
            ("GetOrders", "query GetOrders { orders { id status total } }"),
            ("GetUserById", "query GetUserById($id: ID!) { user(id: $id) { id name } }", {"id": "1"}),
        ]
        
        for name, query, *vars in queries:
            variables = vars[0] if vars else {}
            result = await platform.query(query, variables, "client_001")
            
            status = "✓" if not result.errors else "✗"
            duration = (result.finished_at - result.started_at).total_seconds() * 1000 if result.finished_at else 0
            
            print(f"  {status} {name}: {duration:.2f}ms")
            
        # Test caching
        print("\n📦 Testing Query Cache...")
        
        # Execute same query multiple times
        cache_query = "query { users { id name } }"
        
        times = []
        for i in range(5):
            result = await platform.query(cache_query, None, "client_001")
            duration = (result.finished_at - result.started_at).total_seconds() * 1000
            times.append(duration)
            
        print(f"  Query executions: {[f'{t:.2f}ms' for t in times]}")
        print(f"  Cache stats: {platform.executor.cache.stats()}")
        
        # Test subscriptions
        print("\n📬 Creating Subscriptions...")
        
        sub1 = platform.subscriptions.subscribe(
            "client_001",
            "subscription { orderCreated { id status } }"
        )
        
        sub2 = platform.subscriptions.subscribe(
            "client_002",
            "subscription { productUpdated { id price } }"
        )
        
        print(f"  ✓ Subscription: orderCreated ({sub1.subscription_id})")
        print(f"  ✓ Subscription: productUpdated ({sub2.subscription_id})")
        
        # Publish events
        await platform.subscriptions.publish("orderCreated", {"id": "1", "status": "CONFIRMED"})
        await platform.subscriptions.publish("productUpdated", {"id": "1", "price": 24.99})
        
        print(f"  Events sent to orderCreated: {sub1.events_sent}")
        print(f"  Events sent to productUpdated: {sub2.events_sent}")
        
        # Register federated services
        print("\n🌐 Registering Federated Services...")
        
        services_data = [
            ("user-service", "http://users:4001/graphql", ["User", "UserInput"]),
            ("product-service", "http://products:4002/graphql", ["Product", "ProductInput"]),
            ("order-service", "http://orders:4003/graphql", ["Order", "OrderItem"]),
            ("inventory-service", "http://inventory:4004/graphql", ["Inventory", "Stock"]),
        ]
        
        for name, url, types in services_data:
            service = platform.federation.register_service(name, url, types)
            print(f"  ✓ {name}: {', '.join(types)}")
            
        # Health check
        await platform.federation.health_check()
        
        healthy = sum(1 for s in platform.federation.services.values() if s.healthy)
        print(f"  Health: {healthy}/{len(platform.federation.services)} services healthy")
        
        # Rate limiting test
        print("\n⚡ Testing Rate Limiting...")
        
        # Send many requests
        allowed = 0
        denied = 0
        
        for i in range(120):
            result = await platform.query("{ users { id } }", None, "rate_test_client")
            if result.errors and "Rate limit" in str(result.errors):
                denied += 1
            else:
                allowed += 1
                
        print(f"  Allowed: {allowed}, Denied: {denied}")
        
        # Schema SDL
        print("\n📜 Schema SDL (excerpt):")
        
        sdl = platform.schema.get_schema_sdl()
        lines = sdl.split("\n")[:20]
        for line in lines:
            print(f"  {line}")
        print("  ...")
        
        # Resolver statistics
        print("\n📊 Resolver Statistics:")
        
        for key, resolver in platform.resolvers.resolvers.items():
            avg_time = resolver.total_time_ms / resolver.call_count if resolver.call_count > 0 else 0
            print(f"  {key}: {resolver.call_count} calls, {avg_time:.2f}ms avg")
            
        # Platform statistics
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Schema:")
        print(f"    Types: {stats['total_types']}")
        print(f"    Resolvers: {stats['total_resolvers']}")
        
        print(f"\n  Operations:")
        print(f"    Total: {stats['total_operations']}")
        print(f"    Successful: {stats['successful_operations']}")
        print(f"    Failed: {stats['failed_operations']}")
        print(f"    Avg Time: {stats['avg_execution_time_ms']:.2f}ms")
        
        print(f"\n  Cache:")
        print(f"    Size: {stats['cache_stats']['size']}")
        print(f"    Hits: {stats['cache_stats']['total_hits']}")
        
        print(f"\n  Subscriptions: {stats['active_subscriptions']}")
        print(f"  Federated Services: {stats['federated_services']}")
        
        # Dashboard
        print("\n📋 GraphQL Gateway Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │                GraphQL Gateway Overview                     │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Schema Types:         {stats['total_types']:>10}                      │")
        print(f"  │ Resolvers:            {stats['total_resolvers']:>10}                      │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Operations:     {stats['total_operations']:>10}                      │")
        print(f"  │ Successful:           {stats['successful_operations']:>10}                      │")
        print(f"  │ Failed:               {stats['failed_operations']:>10}                      │")
        print(f"  │ Avg Execution Time:   {stats['avg_execution_time_ms']:>10.2f} ms                │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Cache Size:           {stats['cache_stats']['size']:>10}                      │")
        print(f"  │ Cache Hits:           {stats['cache_stats']['total_hits']:>10}                      │")
        print(f"  │ Subscriptions:        {stats['active_subscriptions']:>10}                      │")
        print(f"  │ Fed. Services:        {stats['federated_services']:>10}                      │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("GraphQL Gateway Platform initialized!")
    print("=" * 60)
