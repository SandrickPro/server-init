#!/usr/bin/env python3
"""
Server Init - Iteration 248: GraphQL Gateway Platform
Платформа GraphQL шлюза

Функционал:
- Schema Stitching - объединение схем
- Schema Federation - федерация схем
- Resolver Management - управление резолверами
- Query Complexity - сложность запросов
- Batching & Caching - батчинг и кэширование
- Subscriptions - подписки
- Introspection - интроспекция
- Persisted Queries - сохранённые запросы
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import json
import hashlib


class FieldType(Enum):
    """Тип поля"""
    SCALAR = "scalar"
    OBJECT = "object"
    LIST = "list"
    NON_NULL = "non_null"
    ENUM = "enum"
    UNION = "union"
    INTERFACE = "interface"


class OperationType(Enum):
    """Тип операции"""
    QUERY = "query"
    MUTATION = "mutation"
    SUBSCRIPTION = "subscription"


class ResolverStatus(Enum):
    """Статус резолвера"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    DISABLED = "disabled"


@dataclass
class GraphQLField:
    """Поле GraphQL"""
    field_id: str
    name: str = ""
    
    # Type
    field_type: FieldType = FieldType.SCALAR
    type_name: str = "String"
    is_nullable: bool = True
    is_list: bool = False
    
    # Arguments
    arguments: List[Dict[str, Any]] = field(default_factory=list)
    
    # Description
    description: str = ""
    
    # Deprecation
    is_deprecated: bool = False
    deprecation_reason: str = ""
    
    # Complexity
    complexity: int = 1


@dataclass
class GraphQLType:
    """Тип GraphQL"""
    type_id: str
    name: str = ""
    
    # Kind
    kind: FieldType = FieldType.OBJECT
    
    # Fields
    fields: List[GraphQLField] = field(default_factory=list)
    
    # Interfaces
    implements: List[str] = field(default_factory=list)
    
    # Description
    description: str = ""
    
    # Service (for federation)
    service: str = ""


@dataclass
class GraphQLSchema:
    """Схема GraphQL"""
    schema_id: str
    name: str = ""
    
    # Types
    types: Dict[str, GraphQLType] = field(default_factory=dict)
    
    # Root types
    query_type: str = "Query"
    mutation_type: str = "Mutation"
    subscription_type: str = "Subscription"
    
    # Directives
    directives: List[str] = field(default_factory=list)
    
    # Service
    service_name: str = ""
    service_url: str = ""
    
    # Version
    version: str = "1.0.0"


@dataclass
class Resolver:
    """Резолвер"""
    resolver_id: str
    
    # Target
    type_name: str = ""
    field_name: str = ""
    
    # Handler
    handler_name: str = ""
    
    # Status
    status: ResolverStatus = ResolverStatus.ACTIVE
    
    # Options
    is_batched: bool = False
    cache_ttl: int = 0
    
    # Stats
    invocations: int = 0
    errors: int = 0
    avg_duration_ms: float = 0
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class GraphQLQuery:
    """Запрос GraphQL"""
    query_id: str
    
    # Operation
    operation_type: OperationType = OperationType.QUERY
    operation_name: str = ""
    
    # Query
    query_string: str = ""
    variables: Dict[str, Any] = field(default_factory=dict)
    
    # Hash (for persisted queries)
    query_hash: str = ""
    
    # Complexity
    complexity_score: int = 0
    depth: int = 0
    
    # Result
    result: Any = None
    errors: List[Dict] = field(default_factory=list)
    
    # Stats
    execution_time_ms: float = 0
    from_cache: bool = False
    
    # Time
    received_at: datetime = field(default_factory=datetime.now)


@dataclass
class PersistedQuery:
    """Сохранённый запрос"""
    hash_id: str
    query_string: str = ""
    operation_name: str = ""
    
    # Stats
    usage_count: int = 0
    last_used: datetime = field(default_factory=datetime.now)
    
    # Allowed
    is_allowed: bool = True


@dataclass
class Subscription:
    """Подписка"""
    subscription_id: str
    
    # Query
    query_string: str = ""
    variables: Dict[str, Any] = field(default_factory=dict)
    
    # Connection
    connection_id: str = ""
    
    # Status
    is_active: bool = True
    
    # Stats
    messages_sent: int = 0
    
    # Time
    started_at: datetime = field(default_factory=datetime.now)


class GraphQLGateway:
    """GraphQL шлюз"""
    
    def __init__(self):
        self.schemas: Dict[str, GraphQLSchema] = {}
        self.resolvers: Dict[str, Resolver] = {}
        self.queries: List[GraphQLQuery] = []
        self.persisted_queries: Dict[str, PersistedQuery] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        
        # Merged schema
        self.merged_schema: Optional[GraphQLSchema] = None
        
        # Query cache
        self.query_cache: Dict[str, Any] = {}
        
        # Complexity limits
        self.max_complexity = 1000
        self.max_depth = 10
        
        # Stats
        self._durations: List[float] = []
        
    def _compute_hash(self, query: str) -> str:
        """Вычисление хеша запроса"""
        return hashlib.sha256(query.encode()).hexdigest()[:16]
        
    def register_schema(self, name: str, service_name: str,
                       service_url: str) -> GraphQLSchema:
        """Регистрация схемы сервиса"""
        schema = GraphQLSchema(
            schema_id=f"sch_{uuid.uuid4().hex[:8]}",
            name=name,
            service_name=service_name,
            service_url=service_url
        )
        
        self.schemas[schema.schema_id] = schema
        return schema
        
    def add_type(self, schema_id: str, name: str,
                kind: FieldType = FieldType.OBJECT,
                description: str = "") -> Optional[GraphQLType]:
        """Добавление типа в схему"""
        schema = self.schemas.get(schema_id)
        if not schema:
            return None
            
        gql_type = GraphQLType(
            type_id=f"type_{uuid.uuid4().hex[:8]}",
            name=name,
            kind=kind,
            description=description,
            service=schema.service_name
        )
        
        schema.types[name] = gql_type
        return gql_type
        
    def add_field(self, schema_id: str, type_name: str,
                 field_name: str, field_type: str,
                 is_nullable: bool = True, is_list: bool = False,
                 arguments: List[Dict] = None,
                 description: str = "",
                 complexity: int = 1) -> Optional[GraphQLField]:
        """Добавление поля в тип"""
        schema = self.schemas.get(schema_id)
        if not schema or type_name not in schema.types:
            return None
            
        gql_field = GraphQLField(
            field_id=f"fld_{uuid.uuid4().hex[:8]}",
            name=field_name,
            type_name=field_type,
            is_nullable=is_nullable,
            is_list=is_list,
            arguments=arguments or [],
            description=description,
            complexity=complexity
        )
        
        schema.types[type_name].fields.append(gql_field)
        return gql_field
        
    def register_resolver(self, type_name: str, field_name: str,
                         handler_name: str, is_batched: bool = False,
                         cache_ttl: int = 0) -> Resolver:
        """Регистрация резолвера"""
        resolver = Resolver(
            resolver_id=f"res_{uuid.uuid4().hex[:8]}",
            type_name=type_name,
            field_name=field_name,
            handler_name=handler_name,
            is_batched=is_batched,
            cache_ttl=cache_ttl
        )
        
        key = f"{type_name}.{field_name}"
        self.resolvers[key] = resolver
        return resolver
        
    def stitch_schemas(self) -> GraphQLSchema:
        """Объединение схем"""
        merged = GraphQLSchema(
            schema_id=f"merged_{uuid.uuid4().hex[:8]}",
            name="MergedSchema"
        )
        
        # Merge types from all schemas
        for schema in self.schemas.values():
            for type_name, gql_type in schema.types.items():
                if type_name in merged.types:
                    # Merge fields
                    existing = merged.types[type_name]
                    existing_fields = {f.name for f in existing.fields}
                    
                    for field in gql_type.fields:
                        if field.name not in existing_fields:
                            existing.fields.append(field)
                else:
                    merged.types[type_name] = gql_type
                    
        self.merged_schema = merged
        return merged
        
    def calculate_complexity(self, query_string: str) -> tuple:
        """Расчёт сложности запроса"""
        # Simplified complexity calculation
        depth = query_string.count('{')
        
        # Count fields
        field_count = 0
        for word in query_string.split():
            if word.isalpha() and word[0].islower():
                field_count += 1
                
        complexity = depth * field_count
        
        return complexity, depth
        
    async def execute_query(self, query_string: str,
                           variables: Dict[str, Any] = None,
                           operation_name: str = "") -> GraphQLQuery:
        """Выполнение запроса"""
        query_hash = self._compute_hash(query_string)
        
        query = GraphQLQuery(
            query_id=f"qry_{uuid.uuid4().hex[:8]}",
            operation_name=operation_name,
            query_string=query_string,
            variables=variables or {},
            query_hash=query_hash
        )
        
        # Calculate complexity
        complexity, depth = self.calculate_complexity(query_string)
        query.complexity_score = complexity
        query.depth = depth
        
        # Check limits
        if complexity > self.max_complexity:
            query.errors.append({
                "message": f"Query complexity {complexity} exceeds limit {self.max_complexity}"
            })
            self.queries.append(query)
            return query
            
        if depth > self.max_depth:
            query.errors.append({
                "message": f"Query depth {depth} exceeds limit {self.max_depth}"
            })
            self.queries.append(query)
            return query
            
        # Check cache
        cache_key = f"{query_hash}:{json.dumps(variables or {}, sort_keys=True)}"
        if cache_key in self.query_cache:
            query.result = self.query_cache[cache_key]
            query.from_cache = True
            self.queries.append(query)
            return query
            
        # Determine operation type
        if "mutation" in query_string.lower():
            query.operation_type = OperationType.MUTATION
        elif "subscription" in query_string.lower():
            query.operation_type = OperationType.SUBSCRIPTION
        else:
            query.operation_type = OperationType.QUERY
            
        # Execute
        start_time = datetime.now()
        
        try:
            # Simulate query execution
            await asyncio.sleep(random.uniform(0.01, 0.1))
            
            # Generate mock result
            query.result = self._generate_mock_result(query_string)
            
        except Exception as e:
            query.errors.append({"message": str(e)})
            
        finally:
            query.execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            self._durations.append(query.execution_time_ms)
            
        # Cache result
        if query.operation_type == OperationType.QUERY and not query.errors:
            self.query_cache[cache_key] = query.result
            
        # Update persisted query stats
        if query_hash in self.persisted_queries:
            pq = self.persisted_queries[query_hash]
            pq.usage_count += 1
            pq.last_used = datetime.now()
            
        self.queries.append(query)
        return query
        
    def _generate_mock_result(self, query_string: str) -> Dict[str, Any]:
        """Генерация мок-результата"""
        # Simplified mock generation
        if "users" in query_string.lower():
            return {
                "data": {
                    "users": [
                        {"id": "1", "name": "Alice", "email": "alice@example.com"},
                        {"id": "2", "name": "Bob", "email": "bob@example.com"}
                    ]
                }
            }
        elif "user" in query_string.lower():
            return {
                "data": {
                    "user": {"id": "1", "name": "Alice", "email": "alice@example.com"}
                }
            }
        elif "products" in query_string.lower():
            return {
                "data": {
                    "products": [
                        {"id": "1", "name": "Widget", "price": 29.99},
                        {"id": "2", "name": "Gadget", "price": 49.99}
                    ]
                }
            }
        return {"data": {}}
        
    def register_persisted_query(self, query_string: str,
                                operation_name: str = "") -> PersistedQuery:
        """Регистрация сохранённого запроса"""
        query_hash = self._compute_hash(query_string)
        
        pq = PersistedQuery(
            hash_id=query_hash,
            query_string=query_string,
            operation_name=operation_name
        )
        
        self.persisted_queries[query_hash] = pq
        return pq
        
    def create_subscription(self, query_string: str,
                           variables: Dict[str, Any] = None,
                           connection_id: str = "") -> Subscription:
        """Создание подписки"""
        subscription = Subscription(
            subscription_id=f"sub_{uuid.uuid4().hex[:8]}",
            query_string=query_string,
            variables=variables or {},
            connection_id=connection_id or str(uuid.uuid4())
        )
        
        self.subscriptions[subscription.subscription_id] = subscription
        return subscription
        
    def introspect(self) -> Dict[str, Any]:
        """Интроспекция схемы"""
        schema = self.merged_schema or list(self.schemas.values())[0] if self.schemas else None
        
        if not schema:
            return {}
            
        types = []
        for gql_type in schema.types.values():
            type_def = {
                "name": gql_type.name,
                "kind": gql_type.kind.value.upper(),
                "description": gql_type.description,
                "fields": [
                    {
                        "name": f.name,
                        "type": f.type_name,
                        "description": f.description
                    }
                    for f in gql_type.fields
                ]
            }
            types.append(type_def)
            
        return {
            "__schema": {
                "queryType": {"name": schema.query_type},
                "mutationType": {"name": schema.mutation_type},
                "subscriptionType": {"name": schema.subscription_type},
                "types": types
            }
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_queries = len(self.queries)
        cached = sum(1 for q in self.queries if q.from_cache)
        errors = sum(1 for q in self.queries if q.errors)
        
        avg_duration = sum(self._durations) / len(self._durations) if self._durations else 0
        avg_complexity = sum(q.complexity_score for q in self.queries) / total_queries if total_queries else 0
        
        total_fields = sum(
            len(t.fields)
            for s in self.schemas.values()
            for t in s.types.values()
        )
        
        return {
            "total_schemas": len(self.schemas),
            "total_types": sum(len(s.types) for s in self.schemas.values()),
            "total_fields": total_fields,
            "total_resolvers": len(self.resolvers),
            "total_queries": total_queries,
            "cached_queries": cached,
            "cache_hit_rate": cached / total_queries * 100 if total_queries else 0,
            "error_queries": errors,
            "avg_duration_ms": avg_duration,
            "avg_complexity": avg_complexity,
            "persisted_queries": len(self.persisted_queries),
            "active_subscriptions": sum(1 for s in self.subscriptions.values() if s.is_active)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 248: GraphQL Gateway Platform")
    print("=" * 60)
    
    gateway = GraphQLGateway()
    print("✓ GraphQL Gateway created")
    
    # Register service schemas
    print("\n📋 Registering Service Schemas...")
    
    # User service schema
    user_schema = gateway.register_schema(
        "UserService", "user-service", "http://user-service:4000/graphql"
    )
    
    gateway.add_type(user_schema.schema_id, "User", FieldType.OBJECT, "User entity")
    gateway.add_field(user_schema.schema_id, "User", "id", "ID", False)
    gateway.add_field(user_schema.schema_id, "User", "name", "String", False)
    gateway.add_field(user_schema.schema_id, "User", "email", "String", False)
    gateway.add_field(user_schema.schema_id, "User", "orders", "Order", True, True, complexity=5)
    
    gateway.add_type(user_schema.schema_id, "Query", FieldType.OBJECT)
    gateway.add_field(user_schema.schema_id, "Query", "user", "User",
                     arguments=[{"name": "id", "type": "ID!"}])
    gateway.add_field(user_schema.schema_id, "Query", "users", "User", True, True)
    
    print(f"  📋 {user_schema.name} - {len(user_schema.types)} types")
    
    # Product service schema
    product_schema = gateway.register_schema(
        "ProductService", "product-service", "http://product-service:4001/graphql"
    )
    
    gateway.add_type(product_schema.schema_id, "Product", FieldType.OBJECT, "Product entity")
    gateway.add_field(product_schema.schema_id, "Product", "id", "ID", False)
    gateway.add_field(product_schema.schema_id, "Product", "name", "String", False)
    gateway.add_field(product_schema.schema_id, "Product", "price", "Float", False)
    gateway.add_field(product_schema.schema_id, "Product", "category", "String")
    
    gateway.add_type(product_schema.schema_id, "Query", FieldType.OBJECT)
    gateway.add_field(product_schema.schema_id, "Query", "product", "Product",
                     arguments=[{"name": "id", "type": "ID!"}])
    gateway.add_field(product_schema.schema_id, "Query", "products", "Product", True, True)
    
    print(f"  📋 {product_schema.name} - {len(product_schema.types)} types")
    
    # Order service schema
    order_schema = gateway.register_schema(
        "OrderService", "order-service", "http://order-service:4002/graphql"
    )
    
    gateway.add_type(order_schema.schema_id, "Order", FieldType.OBJECT, "Order entity")
    gateway.add_field(order_schema.schema_id, "Order", "id", "ID", False)
    gateway.add_field(order_schema.schema_id, "Order", "userId", "ID", False)
    gateway.add_field(order_schema.schema_id, "Order", "products", "Product", True, True)
    gateway.add_field(order_schema.schema_id, "Order", "total", "Float", False)
    gateway.add_field(order_schema.schema_id, "Order", "status", "String", False)
    
    gateway.add_type(order_schema.schema_id, "Query", FieldType.OBJECT)
    gateway.add_field(order_schema.schema_id, "Query", "order", "Order",
                     arguments=[{"name": "id", "type": "ID!"}])
    gateway.add_field(order_schema.schema_id, "Query", "orders", "Order", True, True)
    
    print(f"  📋 {order_schema.name} - {len(order_schema.types)} types")
    
    # Stitch schemas
    print("\n🔗 Stitching Schemas...")
    
    merged = gateway.stitch_schemas()
    print(f"  ✓ Merged schema: {len(merged.types)} types")
    
    # Register resolvers
    print("\n⚡ Registering Resolvers...")
    
    resolvers = [
        ("Query", "user", "UserResolver.getUser", False, 60),
        ("Query", "users", "UserResolver.getUsers", True, 30),
        ("Query", "product", "ProductResolver.getProduct", False, 120),
        ("Query", "products", "ProductResolver.getProducts", True, 60),
        ("Query", "order", "OrderResolver.getOrder", False, 60),
        ("User", "orders", "UserResolver.getOrders", True, 0),
        ("Order", "products", "OrderResolver.getProducts", True, 0),
    ]
    
    for type_name, field_name, handler, batched, ttl in resolvers:
        gateway.register_resolver(type_name, field_name, handler, batched, ttl)
        batch = "(batched)" if batched else ""
        print(f"  ⚡ {type_name}.{field_name} → {handler} {batch}")
        
    # Register persisted queries
    print("\n📝 Registering Persisted Queries...")
    
    persisted = [
        ("query GetUser($id: ID!) { user(id: $id) { id name email } }", "GetUser"),
        ("query ListUsers { users { id name } }", "ListUsers"),
        ("query GetProducts { products { id name price } }", "GetProducts"),
    ]
    
    for query, name in persisted:
        pq = gateway.register_persisted_query(query, name)
        print(f"  📝 {name} (hash: {pq.hash_id})")
        
    # Execute queries
    print("\n🔍 Executing Queries...")
    
    queries = [
        ("query { users { id name email } }", None, "ListUsers"),
        ("query GetUser { user(id: \"1\") { id name email } }", None, "GetUser"),
        ("query { products { id name price } }", None, "GetProducts"),
        ("query { user(id: \"1\") { id name orders { id total } } }", None, "UserWithOrders"),
    ]
    
    for query_str, variables, name in queries:
        result = await gateway.execute_query(query_str, variables, name)
        
        cached = "(cached)" if result.from_cache else ""
        status = "✓" if not result.errors else "✗"
        
        print(f"  {status} {name}: complexity={result.complexity_score}, "
              f"depth={result.depth}, {result.execution_time_ms:.1f}ms {cached}")
              
    # Same query again (should be cached)
    result = await gateway.execute_query(queries[0][0], None, "ListUsers")
    cached = "(cached)" if result.from_cache else ""
    print(f"  ✓ ListUsers (repeat): {result.execution_time_ms:.1f}ms {cached}")
    
    # Query too complex
    complex_query = "{ " + "users { orders { products { " * 5 + "id } } } " * 5 + "}"
    result = await gateway.execute_query(complex_query, None, "ComplexQuery")
    if result.errors:
        print(f"  ✗ ComplexQuery: {result.errors[0]['message']}")
        
    # Create subscription
    print("\n📡 Creating Subscriptions...")
    
    sub = gateway.create_subscription(
        "subscription { orderCreated { id total } }",
        {},
        "conn_123"
    )
    print(f"  📡 orderCreated subscription (id: {sub.subscription_id})")
    
    # Introspection
    print("\n🔍 Schema Introspection:")
    
    intro = gateway.introspect()
    schema_info = intro.get("__schema", {})
    
    print(f"  Query Type: {schema_info.get('queryType', {}).get('name')}")
    print(f"  Mutation Type: {schema_info.get('mutationType', {}).get('name')}")
    print(f"  Types: {len(schema_info.get('types', []))}")
    
    # Display schema types
    print("\n📋 Schema Types:")
    
    for gql_type in merged.types.values():
        print(f"\n  type {gql_type.name} {{")
        for fld in gql_type.fields[:5]:
            nullable = "" if fld.is_nullable else "!"
            list_type = f"[{fld.type_name}]" if fld.is_list else fld.type_name
            print(f"    {fld.name}: {list_type}{nullable}")
        if len(gql_type.fields) > 5:
            print(f"    ... and {len(gql_type.fields) - 5} more fields")
        print("  }")
        
    # Resolver stats
    print("\n⚡ Resolver Statistics:")
    
    print("\n  ┌─────────────────────┬───────────┬───────────┬──────────┐")
    print("  │ Resolver            │ Calls     │ Errors    │ Avg (ms) │")
    print("  ├─────────────────────┼───────────┼───────────┼──────────┤")
    
    for key, resolver in gateway.resolvers.items():
        name = key[:19].ljust(19)
        calls = str(resolver.invocations)[:9].ljust(9)
        errors = str(resolver.errors)[:9].ljust(9)
        avg = f"{resolver.avg_duration_ms:.1f}"[:8].ljust(8)
        
        print(f"  │ {name} │ {calls} │ {errors} │ {avg} │")
        
    print("  └─────────────────────┴───────────┴───────────┴──────────┘")
    
    # Statistics
    print("\n📊 Gateway Statistics:")
    
    stats = gateway.get_statistics()
    
    print(f"\n  Total Schemas: {stats['total_schemas']}")
    print(f"  Total Types: {stats['total_types']}")
    print(f"  Total Fields: {stats['total_fields']}")
    print(f"  Total Resolvers: {stats['total_resolvers']}")
    
    print(f"\n  Total Queries: {stats['total_queries']}")
    print(f"  Cache Hit Rate: {stats['cache_hit_rate']:.1f}%")
    print(f"  Avg Duration: {stats['avg_duration_ms']:.2f}ms")
    print(f"  Avg Complexity: {stats['avg_complexity']:.1f}")
    
    print(f"\n  Persisted Queries: {stats['persisted_queries']}")
    print(f"  Active Subscriptions: {stats['active_subscriptions']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    GraphQL Gateway Dashboard                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Federated Schemas:             {stats['total_schemas']:>12}                        │")
    print(f"│ Total Types:                   {stats['total_types']:>12}                        │")
    print(f"│ Total Resolvers:               {stats['total_resolvers']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Queries Executed:              {stats['total_queries']:>12}                        │")
    print(f"│ Cache Hit Rate:                   {stats['cache_hit_rate']:>7.1f}%                       │")
    print(f"│ Avg Query Time:                   {stats['avg_duration_ms']:>7.2f}ms                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("GraphQL Gateway Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
