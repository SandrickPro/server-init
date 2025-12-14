#!/usr/bin/env python3
"""
Server Init - Iteration 282: GraphQL Federation Platform
Платформа GraphQL Federation

Функционал:
- Schema Stitching - объединение схем
- Federated Types - федеративные типы
- Query Planning - планирование запросов
- Entity Resolution - разрешение сущностей
- Service Routing - маршрутизация сервисов
- Schema Validation - валидация схем
- Type Extensions - расширение типов
- Query Execution - выполнение запросов
"""

import asyncio
import random
import time
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid


class ServiceStatus(Enum):
    """Статус сервиса"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class FieldType(Enum):
    """Тип поля"""
    STRING = "String"
    INT = "Int"
    FLOAT = "Float"
    BOOLEAN = "Boolean"
    ID = "ID"
    OBJECT = "Object"
    LIST = "List"
    NON_NULL = "NonNull"


class DirectiveType(Enum):
    """Тип директивы"""
    KEY = "key"
    EXTENDS = "extends"
    EXTERNAL = "external"
    REQUIRES = "requires"
    PROVIDES = "provides"


class QueryOperationType(Enum):
    """Тип операции"""
    QUERY = "query"
    MUTATION = "mutation"
    SUBSCRIPTION = "subscription"


@dataclass
class FieldDefinition:
    """Определение поля"""
    name: str
    field_type: FieldType
    type_name: str = ""  # For Object/List types
    
    # Nullable
    nullable: bool = True
    
    # List
    is_list: bool = False
    
    # Arguments
    arguments: Dict[str, Any] = field(default_factory=dict)
    
    # Directives
    directives: List[str] = field(default_factory=list)
    
    # External
    is_external: bool = False
    requires: List[str] = field(default_factory=list)
    provides: List[str] = field(default_factory=list)


@dataclass
class TypeDefinition:
    """Определение типа"""
    type_id: str
    name: str
    
    # Fields
    fields: Dict[str, FieldDefinition] = field(default_factory=dict)
    
    # Federation
    key_fields: List[str] = field(default_factory=list)
    is_extended: bool = False
    
    # Source service
    source_service: str = ""
    
    # Interfaces
    implements: List[str] = field(default_factory=list)


@dataclass
class SubgraphService:
    """Подграф-сервис"""
    service_id: str
    name: str
    url: str
    
    # Schema
    types: Dict[str, TypeDefinition] = field(default_factory=dict)
    queries: Dict[str, FieldDefinition] = field(default_factory=dict)
    mutations: Dict[str, FieldDefinition] = field(default_factory=dict)
    
    # Status
    status: ServiceStatus = ServiceStatus.HEALTHY
    last_check: datetime = field(default_factory=datetime.now)
    
    # Stats
    requests_count: int = 0
    errors_count: int = 0
    avg_latency_ms: float = 0


@dataclass
class FederatedType:
    """Федеративный тип"""
    name: str
    
    # Key fields
    key_fields: List[str] = field(default_factory=list)
    
    # Source services
    owner_service: str = ""
    extending_services: List[str] = field(default_factory=list)
    
    # Merged fields
    all_fields: Dict[str, FieldDefinition] = field(default_factory=dict)
    field_sources: Dict[str, str] = field(default_factory=dict)  # field -> service


@dataclass
class QueryPlan:
    """План запроса"""
    plan_id: str
    
    # Nodes
    fetch_nodes: List['FetchNode'] = field(default_factory=list)
    
    # Dependencies
    parallel_fetches: List[List[int]] = field(default_factory=list)
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    estimated_ms: float = 0


@dataclass
class FetchNode:
    """Узел выборки"""
    node_id: int
    service_name: str
    
    # Fields to fetch
    fields: List[str] = field(default_factory=list)
    
    # Dependencies
    depends_on: List[int] = field(default_factory=list)
    
    # Entity references
    requires_entities: bool = False
    entity_type: str = ""


@dataclass
class QueryRequest:
    """GraphQL запрос"""
    request_id: str
    
    # Operation
    operation_type: QueryOperationType = QueryOperationType.QUERY
    operation_name: str = ""
    
    # Query
    query: str = ""
    variables: Dict[str, Any] = field(default_factory=dict)
    
    # Parsed
    requested_fields: Dict[str, List[str]] = field(default_factory=dict)  # type -> fields
    
    # Timing
    received_at: datetime = field(default_factory=datetime.now)


@dataclass
class QueryResult:
    """Результат запроса"""
    result_id: str
    
    # Data
    data: Optional[Dict[str, Any]] = None
    errors: List[Dict[str, Any]] = field(default_factory=list)
    
    # Extensions
    extensions: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    latency_ms: float = 0


@dataclass
class EntityReference:
    """Ссылка на сущность"""
    typename: str
    key_values: Dict[str, Any] = field(default_factory=dict)


class GraphQLFederationManager:
    """Менеджер GraphQL Federation"""
    
    def __init__(self):
        self.services: Dict[str, SubgraphService] = {}
        self.federated_types: Dict[str, FederatedType] = {}
        self.supergraph_schema: Dict[str, TypeDefinition] = {}
        
        # Stats
        self.queries_total: int = 0
        self.queries_success: int = 0
        self.queries_failed: int = 0
        
    def register_service(self, name: str, url: str) -> SubgraphService:
        """Регистрация сервиса"""
        service = SubgraphService(
            service_id=f"svc_{uuid.uuid4().hex[:8]}",
            name=name,
            url=url
        )
        
        self.services[name] = service
        return service
        
    def add_type_to_service(self, service_name: str,
                           type_name: str,
                           fields: Dict[str, FieldDefinition],
                           key_fields: List[str] = None,
                           extends: bool = False) -> TypeDefinition:
        """Добавление типа в сервис"""
        service = self.services.get(service_name)
        if not service:
            return None
            
        type_def = TypeDefinition(
            type_id=f"type_{uuid.uuid4().hex[:8]}",
            name=type_name,
            fields=fields,
            key_fields=key_fields or [],
            is_extended=extends,
            source_service=service_name
        )
        
        service.types[type_name] = type_def
        return type_def
        
    def add_query_to_service(self, service_name: str,
                            query_name: str,
                            return_type: str,
                            arguments: Dict[str, Any] = None,
                            is_list: bool = False) -> FieldDefinition:
        """Добавление query в сервис"""
        service = self.services.get(service_name)
        if not service:
            return None
            
        query_def = FieldDefinition(
            name=query_name,
            field_type=FieldType.OBJECT,
            type_name=return_type,
            is_list=is_list,
            arguments=arguments or {}
        )
        
        service.queries[query_name] = query_def
        return query_def
        
    def compose_supergraph(self) -> Dict[str, TypeDefinition]:
        """Компоновка supergraph"""
        self.federated_types.clear()
        self.supergraph_schema.clear()
        
        # Collect all types
        for service in self.services.values():
            for type_name, type_def in service.types.items():
                if type_name not in self.federated_types:
                    self.federated_types[type_name] = FederatedType(
                        name=type_name,
                        key_fields=type_def.key_fields.copy()
                    )
                    
                fed_type = self.federated_types[type_name]
                
                if type_def.is_extended:
                    fed_type.extending_services.append(service.name)
                else:
                    fed_type.owner_service = service.name
                    
                # Merge fields
                for field_name, field_def in type_def.fields.items():
                    if field_name not in fed_type.all_fields:
                        fed_type.all_fields[field_name] = field_def
                        fed_type.field_sources[field_name] = service.name
                        
        # Build supergraph schema
        for type_name, fed_type in self.federated_types.items():
            merged_type = TypeDefinition(
                type_id=f"merged_{uuid.uuid4().hex[:8]}",
                name=type_name,
                fields=fed_type.all_fields,
                key_fields=fed_type.key_fields,
                source_service="federation"
            )
            self.supergraph_schema[type_name] = merged_type
            
        return self.supergraph_schema
        
    def create_query_plan(self, request: QueryRequest) -> QueryPlan:
        """Создание плана запроса"""
        plan = QueryPlan(
            plan_id=f"plan_{uuid.uuid4().hex[:8]}"
        )
        
        node_id = 0
        type_to_node: Dict[str, int] = {}
        
        # Determine which services to query
        for type_name, fields in request.requested_fields.items():
            if type_name not in self.federated_types:
                continue
                
            fed_type = self.federated_types[type_name]
            
            # Group fields by service
            service_fields: Dict[str, List[str]] = {}
            
            for field_name in fields:
                source_service = fed_type.field_sources.get(field_name)
                if source_service:
                    if source_service not in service_fields:
                        service_fields[source_service] = []
                    service_fields[source_service].append(field_name)
                    
            # Create fetch nodes
            first_node_id = None
            
            for service_name, svc_fields in service_fields.items():
                node = FetchNode(
                    node_id=node_id,
                    service_name=service_name,
                    fields=svc_fields
                )
                
                # Check dependencies
                if service_name != fed_type.owner_service and fed_type.owner_service:
                    node.requires_entities = True
                    node.entity_type = type_name
                    # Add dependency on owner service
                    owner_node = type_to_node.get(type_name)
                    if owner_node is not None:
                        node.depends_on.append(owner_node)
                        
                plan.fetch_nodes.append(node)
                
                if first_node_id is None:
                    first_node_id = node_id
                    type_to_node[type_name] = node_id
                    
                node_id += 1
                
        # Build parallel execution groups
        plan.parallel_fetches = self._build_parallel_groups(plan.fetch_nodes)
        
        return plan
        
    def _build_parallel_groups(self, nodes: List[FetchNode]) -> List[List[int]]:
        """Построение групп параллельного выполнения"""
        groups: List[List[int]] = []
        executed: Set[int] = set()
        
        while len(executed) < len(nodes):
            group = []
            
            for node in nodes:
                if node.node_id in executed:
                    continue
                    
                # Check if all dependencies are executed
                deps_met = all(dep in executed for dep in node.depends_on)
                
                if deps_met:
                    group.append(node.node_id)
                    
            if not group:
                # Deadlock prevention
                remaining = [n.node_id for n in nodes if n.node_id not in executed]
                groups.append(remaining)
                break
                
            executed.update(group)
            groups.append(group)
            
        return groups
        
    async def execute_query(self, request: QueryRequest) -> QueryResult:
        """Выполнение запроса"""
        self.queries_total += 1
        start_time = time.time()
        
        result = QueryResult(
            result_id=f"result_{uuid.uuid4().hex[:8]}"
        )
        
        # Create query plan
        plan = self.create_query_plan(request)
        
        # Execute plan
        data: Dict[str, Any] = {}
        entities: Dict[str, List[Dict[str, Any]]] = {}
        
        for group in plan.parallel_fetches:
            # Execute nodes in parallel
            fetch_tasks = []
            
            for node_id in group:
                node = plan.fetch_nodes[node_id]
                entity_refs = entities.get(node.entity_type) if node.requires_entities else None
                fetch_tasks.append(
                    self._fetch_from_service(node, entity_refs)
                )
                
            group_results = await asyncio.gather(*fetch_tasks, return_exceptions=True)
            
            # Process results
            for node_id, fetch_result in zip(group, group_results):
                node = plan.fetch_nodes[node_id]
                
                if isinstance(fetch_result, Exception):
                    result.errors.append({
                        "message": str(fetch_result),
                        "path": node.fields
                    })
                    continue
                    
                # Merge data
                for key, value in fetch_result.items():
                    if key not in data:
                        data[key] = value
                    elif isinstance(value, list):
                        # Merge entity data
                        if key not in entities:
                            entities[key] = []
                        entities[key].extend(value)
                        data[key] = entities[key]
                    elif isinstance(value, dict):
                        data[key].update(value)
                        
        result.data = data
        result.latency_ms = (time.time() - start_time) * 1000
        
        # Extensions
        result.extensions = {
            "queryPlan": {
                "nodes": len(plan.fetch_nodes),
                "parallelGroups": len(plan.parallel_fetches)
            },
            "services": list({n.service_name for n in plan.fetch_nodes})
        }
        
        if result.errors:
            self.queries_failed += 1
        else:
            self.queries_success += 1
            
        return result
        
    async def _fetch_from_service(self, node: FetchNode,
                                 entity_refs: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Выборка данных из сервиса"""
        service = self.services.get(node.service_name)
        if not service:
            raise Exception(f"Service not found: {node.service_name}")
            
        # Update service stats
        service.requests_count += 1
        
        # Simulate network latency
        latency = random.uniform(5, 50)
        await asyncio.sleep(latency / 1000)
        
        # Simulate response
        if random.random() < 0.98:  # 98% success rate
            # Generate mock data
            return self._generate_mock_data(node, entity_refs)
        else:
            service.errors_count += 1
            raise Exception(f"Service error: {node.service_name}")
            
    def _generate_mock_data(self, node: FetchNode,
                           entity_refs: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Генерация mock данных"""
        data = {}
        
        for field_name in node.fields:
            if entity_refs:
                # Entity resolution
                data[field_name] = [
                    {field_name: f"resolved_{field_name}_{i}"}
                    for i in range(len(entity_refs))
                ]
            else:
                # Root query
                data[field_name] = {
                    "id": f"id_{uuid.uuid4().hex[:8]}",
                    field_name: f"value_{field_name}"
                }
                
        return data
        
    async def resolve_entities(self, typename: str,
                              representations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Разрешение сущностей"""
        fed_type = self.federated_types.get(typename)
        if not fed_type:
            return []
            
        owner_service = self.services.get(fed_type.owner_service)
        if not owner_service:
            return []
            
        # Fetch entities from owner service
        resolved = []
        for rep in representations:
            entity = {
                "__typename": typename,
                **rep
            }
            # Add mock resolved fields
            for field_name in fed_type.all_fields:
                if field_name not in entity:
                    entity[field_name] = f"resolved_{field_name}"
            resolved.append(entity)
            
        return resolved
        
    def validate_schema(self) -> List[str]:
        """Валидация схемы"""
        errors = []
        
        for type_name, fed_type in self.federated_types.items():
            # Check for owner
            if not fed_type.owner_service and not fed_type.extending_services:
                errors.append(f"Type {type_name} has no owner service")
                
            # Check key fields
            if fed_type.key_fields:
                for key_field in fed_type.key_fields:
                    if key_field not in fed_type.all_fields:
                        errors.append(f"Key field {key_field} not found in type {type_name}")
                        
            # Check external fields have source
            for field_name, field_def in fed_type.all_fields.items():
                if field_def.is_external:
                    if field_name not in fed_type.field_sources:
                        errors.append(f"External field {field_name} has no source")
                        
        return errors
        
    def get_service_health(self) -> Dict[str, Dict[str, Any]]:
        """Здоровье сервисов"""
        health = {}
        
        for name, service in self.services.items():
            error_rate = service.errors_count / max(service.requests_count, 1) * 100
            
            if error_rate < 1:
                status = ServiceStatus.HEALTHY
            elif error_rate < 5:
                status = ServiceStatus.DEGRADED
            else:
                status = ServiceStatus.UNHEALTHY
                
            service.status = status
            
            health[name] = {
                "status": status.value,
                "requests": service.requests_count,
                "errors": service.errors_count,
                "error_rate": error_rate,
                "types": len(service.types),
                "queries": len(service.queries)
            }
            
        return health
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        return {
            "services": len(self.services),
            "federated_types": len(self.federated_types),
            "queries_total": self.queries_total,
            "queries_success": self.queries_success,
            "queries_failed": self.queries_failed,
            "success_rate": self.queries_success / max(self.queries_total, 1) * 100
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 282: GraphQL Federation Platform")
    print("=" * 60)
    
    manager = GraphQLFederationManager()
    print("✓ GraphQL Federation Manager created")
    
    # Register services
    print("\n🔧 Registering Subgraph Services...")
    
    services_config = [
        ("users", "http://users-service:4001/graphql"),
        ("products", "http://products-service:4002/graphql"),
        ("reviews", "http://reviews-service:4003/graphql"),
        ("orders", "http://orders-service:4004/graphql"),
        ("inventory", "http://inventory-service:4005/graphql"),
    ]
    
    for name, url in services_config:
        service = manager.register_service(name, url)
        print(f"  📡 {name}: {url}")
        
    # Define types for users service
    print("\n📋 Defining Types...")
    
    # User type (owner: users)
    user_fields = {
        "id": FieldDefinition("id", FieldType.ID, nullable=False),
        "username": FieldDefinition("username", FieldType.STRING),
        "email": FieldDefinition("email", FieldType.STRING),
        "createdAt": FieldDefinition("createdAt", FieldType.STRING),
    }
    manager.add_type_to_service("users", "User", user_fields, key_fields=["id"])
    manager.add_query_to_service("users", "user", "User", {"id": "ID!"})
    manager.add_query_to_service("users", "users", "User", is_list=True)
    print("  👤 User type (users service)")
    
    # Product type (owner: products)
    product_fields = {
        "id": FieldDefinition("id", FieldType.ID, nullable=False),
        "name": FieldDefinition("name", FieldType.STRING),
        "price": FieldDefinition("price", FieldType.FLOAT),
        "category": FieldDefinition("category", FieldType.STRING),
    }
    manager.add_type_to_service("products", "Product", product_fields, key_fields=["id"])
    manager.add_query_to_service("products", "product", "Product", {"id": "ID!"})
    manager.add_query_to_service("products", "products", "Product", is_list=True)
    print("  📦 Product type (products service)")
    
    # Review type (owner: reviews)
    review_fields = {
        "id": FieldDefinition("id", FieldType.ID, nullable=False),
        "rating": FieldDefinition("rating", FieldType.INT),
        "comment": FieldDefinition("comment", FieldType.STRING),
        "author": FieldDefinition("author", FieldType.OBJECT, type_name="User"),
        "product": FieldDefinition("product", FieldType.OBJECT, type_name="Product"),
    }
    manager.add_type_to_service("reviews", "Review", review_fields, key_fields=["id"])
    manager.add_query_to_service("reviews", "reviews", "Review", {"productId": "ID!"}, is_list=True)
    print("  ⭐ Review type (reviews service)")
    
    # Extend User with reviews
    user_extension = {
        "reviews": FieldDefinition("reviews", FieldType.OBJECT, type_name="Review", is_list=True),
    }
    manager.add_type_to_service("reviews", "User", user_extension, key_fields=["id"], extends=True)
    print("  👤 User extended with reviews")
    
    # Extend Product with reviews and inventory
    product_extension_reviews = {
        "reviews": FieldDefinition("reviews", FieldType.OBJECT, type_name="Review", is_list=True),
    }
    manager.add_type_to_service("reviews", "Product", product_extension_reviews, key_fields=["id"], extends=True)
    
    product_extension_inventory = {
        "inStock": FieldDefinition("inStock", FieldType.BOOLEAN),
        "quantity": FieldDefinition("quantity", FieldType.INT),
    }
    manager.add_type_to_service("inventory", "Product", product_extension_inventory, key_fields=["id"], extends=True)
    print("  📦 Product extended with reviews and inventory")
    
    # Order type
    order_fields = {
        "id": FieldDefinition("id", FieldType.ID, nullable=False),
        "customer": FieldDefinition("customer", FieldType.OBJECT, type_name="User"),
        "products": FieldDefinition("products", FieldType.OBJECT, type_name="Product", is_list=True),
        "total": FieldDefinition("total", FieldType.FLOAT),
        "status": FieldDefinition("status", FieldType.STRING),
    }
    manager.add_type_to_service("orders", "Order", order_fields, key_fields=["id"])
    manager.add_query_to_service("orders", "order", "Order", {"id": "ID!"})
    manager.add_query_to_service("orders", "orders", "Order", {"userId": "ID"}, is_list=True)
    print("  🛒 Order type (orders service)")
    
    # Compose supergraph
    print("\n🔗 Composing Supergraph...")
    supergraph = manager.compose_supergraph()
    print(f"  ✓ Composed {len(supergraph)} types")
    
    # Validate schema
    print("\n✅ Validating Schema...")
    errors = manager.validate_schema()
    if errors:
        for error in errors:
            print(f"  ❌ {error}")
    else:
        print("  ✓ Schema is valid")
        
    # Execute queries
    print("\n🚀 Executing Queries...")
    
    # Query 1: Simple user query
    query1 = QueryRequest(
        request_id="q1",
        operation_type=QueryOperationType.QUERY,
        operation_name="GetUser",
        query="query GetUser { user(id: 1) { id username email } }",
        requested_fields={"User": ["id", "username", "email"]}
    )
    
    result1 = await manager.execute_query(query1)
    print(f"\n  📊 Query: GetUser")
    print(f"    Status: {'✅' if not result1.errors else '❌'}")
    print(f"    Latency: {result1.latency_ms:.1f}ms")
    print(f"    Services: {result1.extensions.get('services', [])}")
    
    # Query 2: Federated query (product with reviews)
    query2 = QueryRequest(
        request_id="q2",
        operation_type=QueryOperationType.QUERY,
        operation_name="GetProductWithReviews",
        query="query GetProduct { product(id: 1) { id name reviews { rating comment } } }",
        requested_fields={
            "Product": ["id", "name", "reviews"],
            "Review": ["rating", "comment"]
        }
    )
    
    result2 = await manager.execute_query(query2)
    print(f"\n  📊 Query: GetProductWithReviews")
    print(f"    Status: {'✅' if not result2.errors else '❌'}")
    print(f"    Latency: {result2.latency_ms:.1f}ms")
    print(f"    Query Plan Nodes: {result2.extensions.get('queryPlan', {}).get('nodes', 0)}")
    print(f"    Services: {result2.extensions.get('services', [])}")
    
    # Query 3: Complex federated query
    query3 = QueryRequest(
        request_id="q3",
        operation_type=QueryOperationType.QUERY,
        operation_name="GetProductComplete",
        query="query { product(id: 1) { id name price inStock quantity reviews { rating author { username } } } }",
        requested_fields={
            "Product": ["id", "name", "price", "inStock", "quantity", "reviews"],
            "Review": ["rating", "author"],
            "User": ["username"]
        }
    )
    
    result3 = await manager.execute_query(query3)
    print(f"\n  📊 Query: GetProductComplete (federated)")
    print(f"    Status: {'✅' if not result3.errors else '❌'}")
    print(f"    Latency: {result3.latency_ms:.1f}ms")
    print(f"    Parallel Groups: {result3.extensions.get('queryPlan', {}).get('parallelGroups', 0)}")
    print(f"    Services: {result3.extensions.get('services', [])}")
    
    # Bulk queries
    print("\n📦 Executing bulk queries...")
    
    for i in range(30):
        query = QueryRequest(
            request_id=f"bulk_{i}",
            operation_type=QueryOperationType.QUERY,
            requested_fields={
                random.choice(["User", "Product", "Review", "Order"]): ["id", "name"]
            }
        )
        await manager.execute_query(query)
        
    print(f"  ✓ Processed 30 bulk queries")
    
    # Display federated types
    print("\n📋 Federated Types:")
    
    print("\n  ┌────────────────────┬─────────────────────┬─────────────────────────────────────┐")
    print("  │ Type               │ Owner               │ Extensions                          │")
    print("  ├────────────────────┼─────────────────────┼─────────────────────────────────────┤")
    
    for type_name, fed_type in manager.federated_types.items():
        owner = fed_type.owner_service[:19].ljust(19)
        extensions = ", ".join(fed_type.extending_services)[:35].ljust(35)
        type_display = type_name[:18].ljust(18)
        
        print(f"  │ {type_display} │ {owner} │ {extensions} │")
        
    print("  └────────────────────┴─────────────────────┴─────────────────────────────────────┘")
    
    # Display type fields
    print("\n📝 Type Fields Distribution:")
    
    for type_name, fed_type in manager.federated_types.items():
        print(f"\n  🏷️ {type_name}:")
        print(f"    Key: {fed_type.key_fields}")
        print(f"    Fields: {len(fed_type.all_fields)}")
        
        for field_name, source in fed_type.field_sources.items():
            print(f"      • {field_name} <- {source}")
            
    # Service health
    print("\n💚 Service Health:")
    
    health = manager.get_service_health()
    
    for name, info in health.items():
        status_icon = {
            "healthy": "🟢",
            "degraded": "🟡",
            "unhealthy": "🔴"
        }.get(info["status"], "⚪")
        
        print(f"\n  {status_icon} {name}:")
        print(f"    Requests: {info['requests']}")
        print(f"    Errors: {info['errors']} ({info['error_rate']:.1f}%)")
        print(f"    Types: {info['types']}, Queries: {info['queries']}")
        
    # Query plan visualization
    print("\n📊 Query Plan Example:")
    
    sample_request = QueryRequest(
        request_id="sample",
        requested_fields={
            "Product": ["id", "name", "inStock", "reviews"],
            "Review": ["rating"]
        }
    )
    
    plan = manager.create_query_plan(sample_request)
    
    print(f"\n  Plan ID: {plan.plan_id}")
    print(f"  Fetch Nodes: {len(plan.fetch_nodes)}")
    
    for node in plan.fetch_nodes:
        deps = f" (depends on: {node.depends_on})" if node.depends_on else ""
        entity = f" [entity: {node.entity_type}]" if node.requires_entities else ""
        print(f"    [{node.node_id}] {node.service_name}: {node.fields}{deps}{entity}")
        
    print(f"\n  Parallel Execution Groups:")
    for i, group in enumerate(plan.parallel_fetches):
        print(f"    Stage {i+1}: nodes {group}")
        
    # Statistics
    print("\n📈 Federation Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Services: {stats['services']}")
    print(f"  Federated Types: {stats['federated_types']}")
    print(f"\n  Queries Total: {stats['queries_total']}")
    print(f"  Queries Success: {stats['queries_success']}")
    print(f"  Queries Failed: {stats['queries_failed']}")
    print(f"  Success Rate: {stats['success_rate']:.1f}%")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   GraphQL Federation Dashboard                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Subgraph Services:             {stats['services']:>12}                        │")
    print(f"│ Federated Types:               {stats['federated_types']:>12}                        │")
    print(f"│ Total Queries:                 {stats['queries_total']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Query Success Rate:            {stats['success_rate']:>11.1f}%                        │")
    
    healthy_services = sum(1 for h in health.values() if h['status'] == 'healthy')
    print(f"│ Healthy Services:              {healthy_services:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("GraphQL Federation Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
