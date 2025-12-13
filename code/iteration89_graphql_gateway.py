#!/usr/bin/env python3
"""
Server Init - Iteration 89: GraphQL Gateway Platform
Платформа GraphQL шлюза

Функционал:
- Schema Stitching - склеивание схем
- Federation Support - поддержка федерации
- Query Optimization - оптимизация запросов
- Caching Layer - слой кэширования
- Rate Limiting - ограничение запросов
- Query Complexity Analysis - анализ сложности запросов
- Introspection Control - контроль интроспекции
- Performance Monitoring - мониторинг производительности
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Tuple
from enum import Enum
from collections import defaultdict
import uuid
import random
import re
import hashlib


class OperationType(Enum):
    """Тип операции"""
    QUERY = "query"
    MUTATION = "mutation"
    SUBSCRIPTION = "subscription"


class CacheStrategy(Enum):
    """Стратегия кэширования"""
    NO_CACHE = "no_cache"
    PRIVATE = "private"
    PUBLIC = "public"
    MAX_AGE = "max_age"


class RateLimitScope(Enum):
    """Область ограничения запросов"""
    GLOBAL = "global"
    PER_USER = "per_user"
    PER_OPERATION = "per_operation"
    PER_FIELD = "per_field"


@dataclass
class GraphQLField:
    """Поле GraphQL"""
    name: str = ""
    field_type: str = ""  # String, Int, [User], etc.
    arguments: Dict[str, str] = field(default_factory=dict)
    description: str = ""
    
    # Директивы
    deprecated: bool = False
    deprecation_reason: str = ""
    
    # Резолвер
    resolver_service: str = ""  # Для федерации
    
    # Сложность
    complexity: int = 1
    
    # Кэширование
    cache_strategy: CacheStrategy = CacheStrategy.NO_CACHE
    cache_ttl_seconds: int = 0


@dataclass
class GraphQLType:
    """Тип GraphQL"""
    name: str = ""
    kind: str = "OBJECT"  # OBJECT, INTERFACE, UNION, ENUM, INPUT, SCALAR
    description: str = ""
    
    # Поля (для OBJECT, INTERFACE)
    fields: Dict[str, GraphQLField] = field(default_factory=dict)
    
    # Интерфейсы (для OBJECT)
    interfaces: List[str] = field(default_factory=list)
    
    # Возможные типы (для INTERFACE, UNION)
    possible_types: List[str] = field(default_factory=list)
    
    # Значения (для ENUM)
    enum_values: List[str] = field(default_factory=list)
    
    # Для федерации
    key_fields: List[str] = field(default_factory=list)  # @key директива
    service: str = ""  # Источник сервиса


@dataclass
class GraphQLSchema:
    """Схема GraphQL"""
    schema_id: str
    name: str = ""
    
    # Типы
    types: Dict[str, GraphQLType] = field(default_factory=dict)
    
    # Корневые типы
    query_type: str = "Query"
    mutation_type: str = "Mutation"
    subscription_type: str = "Subscription"
    
    # Директивы
    directives: List[str] = field(default_factory=list)
    
    # Версия
    version: str = "1.0"
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class GraphQLQuery:
    """GraphQL запрос"""
    query_id: str
    operation_type: OperationType = OperationType.QUERY
    operation_name: str = ""
    
    # Запрос
    query_string: str = ""
    variables: Dict[str, Any] = field(default_factory=dict)
    
    # Разобранные поля
    selected_fields: List[str] = field(default_factory=list)
    
    # Сложность
    complexity_score: int = 0
    depth: int = 0
    
    # Клиент
    client_id: str = ""
    user_id: str = ""
    
    # Время выполнения
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    duration_ms: float = 0
    
    # Результат
    success: bool = True
    errors: List[str] = field(default_factory=list)


@dataclass
class ServiceDefinition:
    """Определение сервиса для федерации"""
    service_id: str
    name: str = ""
    url: str = ""
    
    # Схема сервиса
    schema: Optional[GraphQLSchema] = None
    
    # Типы, которые предоставляет сервис
    provided_types: List[str] = field(default_factory=list)
    
    # Типы, которые расширяет
    extended_types: List[str] = field(default_factory=list)
    
    # Health
    is_healthy: bool = True
    last_health_check: datetime = field(default_factory=datetime.now)
    
    # Статистика
    requests_count: int = 0
    errors_count: int = 0


@dataclass
class CacheEntry:
    """Запись кэша"""
    key: str = ""
    value: Any = None
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    hits: int = 0


@dataclass
class RateLimitRule:
    """Правило ограничения запросов"""
    rule_id: str
    name: str = ""
    
    # Scope
    scope: RateLimitScope = RateLimitScope.GLOBAL
    
    # Лимиты
    requests_per_second: int = 100
    requests_per_minute: int = 1000
    max_complexity: int = 10000
    max_depth: int = 10
    
    # Применимость
    applies_to: List[str] = field(default_factory=list)  # ["Query.users", "*"]
    
    # Статус
    is_active: bool = True


class SchemaRegistry:
    """Реестр схем"""
    
    def __init__(self):
        self.schemas: Dict[str, GraphQLSchema] = {}
        
    def register(self, schema: GraphQLSchema):
        """Регистрация схемы"""
        self.schemas[schema.schema_id] = schema
        
    def get(self, schema_id: str) -> Optional[GraphQLSchema]:
        """Получение схемы"""
        return self.schemas.get(schema_id)
        
    def merge_schemas(self, schema_ids: List[str]) -> GraphQLSchema:
        """Слияние схем (Schema Stitching)"""
        merged = GraphQLSchema(
            schema_id=f"merged_{uuid.uuid4().hex[:8]}",
            name="Merged Schema"
        )
        
        for schema_id in schema_ids:
            schema = self.schemas.get(schema_id)
            if not schema:
                continue
                
            # Объединяем типы
            for type_name, gql_type in schema.types.items():
                if type_name in merged.types:
                    # Расширяем существующий тип
                    existing = merged.types[type_name]
                    existing.fields.update(gql_type.fields)
                else:
                    merged.types[type_name] = gql_type
                    
        return merged


class QueryParser:
    """Парсер запросов GraphQL"""
    
    def parse(self, query_string: str) -> Dict[str, Any]:
        """Разбор запроса"""
        result = {
            "operation_type": OperationType.QUERY,
            "operation_name": "",
            "fields": [],
            "depth": 0
        }
        
        # Упрощённый парсинг
        query_string = query_string.strip()
        
        # Определяем тип операции
        if query_string.startswith("mutation"):
            result["operation_type"] = OperationType.MUTATION
        elif query_string.startswith("subscription"):
            result["operation_type"] = OperationType.SUBSCRIPTION
            
        # Извлекаем имя операции
        match = re.match(r'(query|mutation|subscription)\s+(\w+)', query_string)
        if match:
            result["operation_name"] = match.group(2)
            
        # Подсчёт глубины (по количеству вложенных {})
        depth = 0
        max_depth = 0
        
        for char in query_string:
            if char == '{':
                depth += 1
                max_depth = max(max_depth, depth)
            elif char == '}':
                depth -= 1
                
        result["depth"] = max_depth
        
        # Извлечение полей (упрощённо)
        field_pattern = r'\b(\w+)\s*[{(]'
        result["fields"] = re.findall(field_pattern, query_string)
        
        return result


class ComplexityAnalyzer:
    """Анализатор сложности запросов"""
    
    def __init__(self, schema: GraphQLSchema, default_complexity: int = 1):
        self.schema = schema
        self.default_complexity = default_complexity
        
    def analyze(self, parsed_query: Dict[str, Any]) -> int:
        """Расчёт сложности запроса"""
        total = 0
        
        fields = parsed_query.get("fields", [])
        depth = parsed_query.get("depth", 1)
        
        for field_name in fields:
            # Ищем поле в схеме
            for gql_type in self.schema.types.values():
                if field_name in gql_type.fields:
                    field = gql_type.fields[field_name]
                    total += field.complexity
                    break
            else:
                total += self.default_complexity
                
        # Множитель глубины
        depth_multiplier = 1 + (depth - 1) * 0.5
        
        return int(total * depth_multiplier)


class QueryCache:
    """Кэш запросов"""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
        
    def _generate_key(self, query: str, variables: Dict[str, Any]) -> str:
        """Генерация ключа кэша"""
        data = f"{query}:{json.dumps(variables, sort_keys=True)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
        
    def get(self, query: str, variables: Dict[str, Any] = None) -> Optional[Any]:
        """Получение из кэша"""
        key = self._generate_key(query, variables or {})
        
        entry = self.cache.get(key)
        
        if entry:
            # Проверяем срок действия
            if entry.expires_at and entry.expires_at < datetime.now():
                del self.cache[key]
                self.misses += 1
                return None
                
            entry.hits += 1
            self.hits += 1
            return entry.value
            
        self.misses += 1
        return None
        
    def set(self, query: str, variables: Dict[str, Any], value: Any, 
             ttl_seconds: int = 60):
        """Сохранение в кэш"""
        key = self._generate_key(query, variables or {})
        
        # Очистка если превышен размер
        if len(self.cache) >= self.max_size:
            self._evict()
            
        self.cache[key] = CacheEntry(
            key=key,
            value=value,
            expires_at=datetime.now() + timedelta(seconds=ttl_seconds) if ttl_seconds > 0 else None
        )
        
    def _evict(self):
        """Удаление старых записей"""
        # Удаляем 10% самых старых
        sorted_entries = sorted(self.cache.items(), 
                                 key=lambda x: x[1].created_at)
        to_remove = len(sorted_entries) // 10 or 1
        
        for key, _ in sorted_entries[:to_remove]:
            del self.cache[key]
            
    def get_stats(self) -> Dict[str, Any]:
        """Статистика кэша"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            "entries": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate
        }


class RateLimiter:
    """Ограничитель запросов"""
    
    def __init__(self):
        self.rules: Dict[str, RateLimitRule] = {}
        self.counters: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.last_reset: Dict[str, datetime] = {}
        
    def add_rule(self, rule: RateLimitRule):
        """Добавление правила"""
        self.rules[rule.rule_id] = rule
        
    def check(self, query: GraphQLQuery) -> Tuple[bool, Optional[str]]:
        """Проверка лимитов"""
        for rule in self.rules.values():
            if not rule.is_active:
                continue
                
            # Определяем ключ счётчика
            if rule.scope == RateLimitScope.GLOBAL:
                counter_key = "global"
            elif rule.scope == RateLimitScope.PER_USER:
                counter_key = f"user:{query.user_id}"
            elif rule.scope == RateLimitScope.PER_OPERATION:
                counter_key = f"op:{query.operation_name}"
            else:
                counter_key = "global"
                
            # Сбрасываем счётчик если прошла минута
            now = datetime.now()
            last_reset = self.last_reset.get(counter_key)
            
            if not last_reset or (now - last_reset).total_seconds() >= 60:
                self.counters[rule.rule_id][counter_key] = 0
                self.last_reset[counter_key] = now
                
            # Проверяем лимит
            count = self.counters[rule.rule_id][counter_key]
            
            if count >= rule.requests_per_minute:
                return False, f"Rate limit exceeded: {rule.name}"
                
            # Проверяем сложность
            if query.complexity_score > rule.max_complexity:
                return False, f"Query complexity {query.complexity_score} exceeds limit {rule.max_complexity}"
                
            # Проверяем глубину
            if query.depth > rule.max_depth:
                return False, f"Query depth {query.depth} exceeds limit {rule.max_depth}"
                
            # Увеличиваем счётчик
            self.counters[rule.rule_id][counter_key] += 1
            
        return True, None


class Federation:
    """Поддержка федерации GraphQL"""
    
    def __init__(self):
        self.services: Dict[str, ServiceDefinition] = {}
        self.type_ownership: Dict[str, str] = {}  # type_name -> service_id
        
    def register_service(self, service: ServiceDefinition):
        """Регистрация сервиса"""
        self.services[service.service_id] = service
        
        # Регистрируем типы
        for type_name in service.provided_types:
            self.type_ownership[type_name] = service.service_id
            
    def get_service_for_type(self, type_name: str) -> Optional[ServiceDefinition]:
        """Получение сервиса для типа"""
        service_id = self.type_ownership.get(type_name)
        
        if service_id:
            return self.services.get(service_id)
        return None
        
    def plan_execution(self, fields: List[str]) -> List[Tuple[str, List[str]]]:
        """Планирование выполнения (какие поля из каких сервисов)"""
        plan = defaultdict(list)
        
        for field in fields:
            # Упрощённо: берём первую часть поля как тип
            parts = field.split(".")
            type_name = parts[0] if len(parts) > 1 else "Query"
            
            service = self.get_service_for_type(type_name)
            
            if service:
                plan[service.service_id].append(field)
            else:
                plan["default"].append(field)
                
        return list(plan.items())
        
    async def execute_federated(self, query: GraphQLQuery) -> Dict[str, Any]:
        """Федеративное выполнение"""
        execution_plan = self.plan_execution(query.selected_fields)
        
        results = {}
        
        for service_id, fields in execution_plan:
            service = self.services.get(service_id)
            
            if service and service.is_healthy:
                # Симуляция запроса к сервису
                service.requests_count += 1
                
                # В реальности здесь был бы HTTP запрос
                results[service_id] = {
                    "fields": fields,
                    "data": {"mock": "response"}
                }
            else:
                results[service_id] = {
                    "fields": fields,
                    "error": "Service unavailable"
                }
                if service:
                    service.errors_count += 1
                    
        return results


class GraphQLGatewayPlatform:
    """Платформа GraphQL шлюза"""
    
    def __init__(self):
        self.schema_registry = SchemaRegistry()
        self.query_parser = QueryParser()
        self.cache = QueryCache()
        self.rate_limiter = RateLimiter()
        self.federation = Federation()
        
        self.queries_log: List[GraphQLQuery] = []
        
        # Создаём базовую схему
        self._init_base_schema()
        
    def _init_base_schema(self):
        """Инициализация базовой схемы"""
        schema = GraphQLSchema(
            schema_id="base",
            name="Base Schema"
        )
        
        # Query тип
        query_type = GraphQLType(name="Query", kind="OBJECT")
        query_type.fields = {
            "users": GraphQLField(name="users", field_type="[User]", complexity=5,
                                   cache_strategy=CacheStrategy.MAX_AGE, cache_ttl_seconds=60),
            "user": GraphQLField(name="user", field_type="User", 
                                  arguments={"id": "ID!"}, complexity=1),
            "orders": GraphQLField(name="orders", field_type="[Order]", complexity=10),
            "order": GraphQLField(name="order", field_type="Order",
                                   arguments={"id": "ID!"}, complexity=2)
        }
        schema.types["Query"] = query_type
        
        # Mutation тип
        mutation_type = GraphQLType(name="Mutation", kind="OBJECT")
        mutation_type.fields = {
            "createUser": GraphQLField(name="createUser", field_type="User", complexity=5),
            "updateUser": GraphQLField(name="updateUser", field_type="User", complexity=3),
            "createOrder": GraphQLField(name="createOrder", field_type="Order", complexity=10)
        }
        schema.types["Mutation"] = mutation_type
        
        # User тип
        user_type = GraphQLType(name="User", kind="OBJECT", key_fields=["id"])
        user_type.fields = {
            "id": GraphQLField(name="id", field_type="ID!", complexity=1),
            "name": GraphQLField(name="name", field_type="String", complexity=1),
            "email": GraphQLField(name="email", field_type="String", complexity=1),
            "orders": GraphQLField(name="orders", field_type="[Order]", complexity=5,
                                    resolver_service="order-service")
        }
        schema.types["User"] = user_type
        
        # Order тип
        order_type = GraphQLType(name="Order", kind="OBJECT", key_fields=["id"])
        order_type.fields = {
            "id": GraphQLField(name="id", field_type="ID!", complexity=1),
            "user": GraphQLField(name="user", field_type="User", complexity=3,
                                  resolver_service="user-service"),
            "items": GraphQLField(name="items", field_type="[OrderItem]", complexity=5),
            "total": GraphQLField(name="total", field_type="Float", complexity=1),
            "status": GraphQLField(name="status", field_type="OrderStatus", complexity=1)
        }
        schema.types["Order"] = order_type
        
        # Enum
        status_enum = GraphQLType(name="OrderStatus", kind="ENUM")
        status_enum.enum_values = ["PENDING", "CONFIRMED", "SHIPPED", "DELIVERED", "CANCELLED"]
        schema.types["OrderStatus"] = status_enum
        
        self.schema_registry.register(schema)
        self.complexity_analyzer = ComplexityAnalyzer(schema)
        
    def register_service(self, name: str, url: str, 
                          provided_types: List[str]) -> ServiceDefinition:
        """Регистрация сервиса для федерации"""
        service = ServiceDefinition(
            service_id=f"svc_{uuid.uuid4().hex[:8]}",
            name=name,
            url=url,
            provided_types=provided_types
        )
        self.federation.register_service(service)
        return service
        
    def add_rate_limit_rule(self, name: str, scope: RateLimitScope,
                             requests_per_minute: int = 1000,
                             max_complexity: int = 10000,
                             max_depth: int = 10) -> RateLimitRule:
        """Добавление правила rate limiting"""
        rule = RateLimitRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name=name,
            scope=scope,
            requests_per_minute=requests_per_minute,
            max_complexity=max_complexity,
            max_depth=max_depth
        )
        self.rate_limiter.add_rule(rule)
        return rule
        
    async def execute(self, query_string: str, variables: Dict[str, Any] = None,
                       user_id: str = "", client_id: str = "") -> Dict[str, Any]:
        """Выполнение запроса"""
        variables = variables or {}
        
        # Парсим запрос
        parsed = self.query_parser.parse(query_string)
        
        # Создаём объект запроса
        query = GraphQLQuery(
            query_id=f"q_{uuid.uuid4().hex[:8]}",
            operation_type=parsed["operation_type"],
            operation_name=parsed["operation_name"],
            query_string=query_string,
            variables=variables,
            selected_fields=parsed["fields"],
            depth=parsed["depth"],
            user_id=user_id,
            client_id=client_id
        )
        
        # Анализируем сложность
        query.complexity_score = self.complexity_analyzer.analyze(parsed)
        
        # Проверяем rate limits
        allowed, error_message = self.rate_limiter.check(query)
        
        if not allowed:
            query.success = False
            query.errors.append(error_message)
            query.completed_at = datetime.now()
            self.queries_log.append(query)
            
            return {
                "data": None,
                "errors": [{"message": error_message}]
            }
            
        # Проверяем кэш (только для queries)
        if query.operation_type == OperationType.QUERY:
            cached = self.cache.get(query_string, variables)
            
            if cached:
                query.completed_at = datetime.now()
                query.duration_ms = (query.completed_at - query.started_at).total_seconds() * 1000
                self.queries_log.append(query)
                
                return {
                    "data": cached,
                    "extensions": {"cached": True}
                }
                
        # Выполняем федеративно
        result = await self.federation.execute_federated(query)
        
        # Симуляция результата
        response_data = self._mock_response(parsed["fields"])
        
        # Кэшируем результат
        if query.operation_type == OperationType.QUERY:
            self.cache.set(query_string, variables, response_data, ttl_seconds=60)
            
        query.completed_at = datetime.now()
        query.duration_ms = (query.completed_at - query.started_at).total_seconds() * 1000
        self.queries_log.append(query)
        
        return {
            "data": response_data,
            "extensions": {
                "complexity": query.complexity_score,
                "depth": query.depth,
                "duration_ms": query.duration_ms
            }
        }
        
    def _mock_response(self, fields: List[str]) -> Dict[str, Any]:
        """Генерация mock ответа"""
        data = {}
        
        for field in fields:
            if field in ["users", "orders"]:
                data[field] = [{"id": f"{field[:-1]}_1", "mock": True}]
            elif field in ["user", "order"]:
                data[field] = {"id": f"{field}_1", "mock": True}
            else:
                data[field] = None
                
        return data
        
    def get_schema_sdl(self) -> str:
        """Получение SDL схемы"""
        schema = self.schema_registry.get("base")
        if not schema:
            return ""
            
        sdl_lines = []
        
        for type_name, gql_type in schema.types.items():
            if gql_type.kind == "OBJECT":
                sdl_lines.append(f"type {type_name} {{")
                for field_name, field in gql_type.fields.items():
                    args = ""
                    if field.arguments:
                        args = f"({', '.join(f'{k}: {v}' for k, v in field.arguments.items())})"
                    sdl_lines.append(f"  {field_name}{args}: {field.field_type}")
                sdl_lines.append("}")
                sdl_lines.append("")
            elif gql_type.kind == "ENUM":
                sdl_lines.append(f"enum {type_name} {{")
                for value in gql_type.enum_values:
                    sdl_lines.append(f"  {value}")
                sdl_lines.append("}")
                sdl_lines.append("")
                
        return "\n".join(sdl_lines)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        successful = sum(1 for q in self.queries_log if q.success)
        failed = len(self.queries_log) - successful
        
        avg_duration = 0
        avg_complexity = 0
        
        if self.queries_log:
            avg_duration = sum(q.duration_ms for q in self.queries_log) / len(self.queries_log)
            avg_complexity = sum(q.complexity_score for q in self.queries_log) / len(self.queries_log)
            
        return {
            "total_queries": len(self.queries_log),
            "successful": successful,
            "failed": failed,
            "avg_duration_ms": avg_duration,
            "avg_complexity": avg_complexity,
            "cache": self.cache.get_stats(),
            "services": len(self.federation.services)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 89: GraphQL Gateway Platform")
    print("=" * 60)
    
    async def demo():
        platform = GraphQLGatewayPlatform()
        print("✓ GraphQL Gateway Platform created")
        
        # Отображение схемы
        print("\n📜 GraphQL Schema (SDL):")
        
        sdl = platform.get_schema_sdl()
        for line in sdl.split("\n")[:25]:
            print(f"  {line}")
        print("  ...")
        
        # Регистрация сервисов для федерации
        print("\n🔗 Registering Federated Services...")
        
        user_service = platform.register_service(
            "user-service",
            "http://user-service:4001/graphql",
            ["User"]
        )
        print(f"  ✓ {user_service.name}: {user_service.provided_types}")
        
        order_service = platform.register_service(
            "order-service",
            "http://order-service:4002/graphql",
            ["Order", "OrderItem"]
        )
        print(f"  ✓ {order_service.name}: {order_service.provided_types}")
        
        product_service = platform.register_service(
            "product-service",
            "http://product-service:4003/graphql",
            ["Product", "Category"]
        )
        print(f"  ✓ {product_service.name}: {product_service.provided_types}")
        
        # Rate Limiting
        print("\n🚦 Setting Up Rate Limiting...")
        
        global_rule = platform.add_rate_limit_rule(
            "Global Rate Limit",
            RateLimitScope.GLOBAL,
            requests_per_minute=10000,
            max_complexity=50000,
            max_depth=15
        )
        print(f"  ✓ {global_rule.name}: {global_rule.requests_per_minute} req/min")
        
        user_rule = platform.add_rate_limit_rule(
            "Per-User Rate Limit",
            RateLimitScope.PER_USER,
            requests_per_minute=100,
            max_complexity=10000,
            max_depth=10
        )
        print(f"  ✓ {user_rule.name}: {user_rule.requests_per_minute} req/min per user")
        
        # Выполнение запросов
        print("\n📤 Executing GraphQL Queries...")
        
        # Query 1: Простой запрос
        query1 = """
        query GetUsers {
            users {
                id
                name
                email
            }
        }
        """
        
        result1 = await platform.execute(query1, user_id="user_001")
        
        print(f"\n  Query: GetUsers")
        print(f"  Complexity: {result1['extensions']['complexity']}")
        print(f"  Depth: {result1['extensions']['depth']}")
        print(f"  Duration: {result1['extensions']['duration_ms']:.2f}ms")
        print(f"  Cached: {result1['extensions'].get('cached', False)}")
        
        # Query 2: Запрос с переменными
        query2 = """
        query GetUser($id: ID!) {
            user(id: $id) {
                id
                name
                orders {
                    id
                    total
                    status
                }
            }
        }
        """
        
        result2 = await platform.execute(query2, {"id": "user_123"}, user_id="user_001")
        
        print(f"\n  Query: GetUser (with variables)")
        print(f"  Complexity: {result2['extensions']['complexity']}")
        print(f"  Depth: {result2['extensions']['depth']}")
        print(f"  Duration: {result2['extensions']['duration_ms']:.2f}ms")
        
        # Query 3: Mutation
        mutation1 = """
        mutation CreateOrder($input: CreateOrderInput!) {
            createOrder(input: $input) {
                id
                total
                status
            }
        }
        """
        
        result3 = await platform.execute(
            mutation1,
            {"input": {"userId": "user_123", "items": [{"productId": "prod_1", "quantity": 2}]}},
            user_id="user_001"
        )
        
        print(f"\n  Mutation: CreateOrder")
        print(f"  Complexity: {result3['extensions']['complexity']}")
        print(f"  Duration: {result3['extensions']['duration_ms']:.2f}ms")
        
        # Query 4: Повторный запрос (должен быть закэширован)
        result4 = await platform.execute(query1, user_id="user_001")
        
        print(f"\n  Query: GetUsers (repeat)")
        print(f"  Cached: {result4['extensions'].get('cached', False)}")
        print(f"  Duration: {result4['extensions']['duration_ms']:.2f}ms")
        
        # Симуляция нагрузки
        print("\n🔄 Simulating Load...")
        
        for i in range(20):
            await platform.execute(
                f"query Test{i} {{ users {{ id }} }}",
                user_id=f"user_{i % 5}"
            )
            
        print(f"  ✓ Executed 20 additional queries")
        
        # Тест сложного запроса
        print("\n🔍 Complex Query Analysis:")
        
        complex_query = """
        query ComplexQuery {
            users {
                id
                name
                orders {
                    id
                    items {
                        product {
                            name
                            category {
                                name
                            }
                        }
                        quantity
                    }
                    total
                }
            }
        }
        """
        
        parsed = platform.query_parser.parse(complex_query)
        complexity = platform.complexity_analyzer.analyze(parsed)
        
        print(f"\n  Operation: {parsed['operation_type'].value}")
        print(f"  Depth: {parsed['depth']}")
        print(f"  Fields: {len(parsed['fields'])}")
        print(f"  Complexity Score: {complexity}")
        
        # Кэш статистика
        print("\n💾 Cache Statistics:")
        
        cache_stats = platform.cache.get_stats()
        
        print(f"\n  Entries: {cache_stats['entries']}")
        print(f"  Hits: {cache_stats['hits']}")
        print(f"  Misses: {cache_stats['misses']}")
        print(f"  Hit Rate: {cache_stats['hit_rate']:.1f}%")
        
        # Federation статистика
        print("\n🔗 Federation Statistics:")
        
        for service in platform.federation.services.values():
            health_icon = "🟢" if service.is_healthy else "🔴"
            print(f"\n  {health_icon} {service.name}")
            print(f"     URL: {service.url}")
            print(f"     Types: {service.provided_types}")
            print(f"     Requests: {service.requests_count}")
            print(f"     Errors: {service.errors_count}")
            
        # Общая статистика
        print("\n📊 Gateway Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Queries: {stats['total_queries']}")
        print(f"  Successful: {stats['successful']}")
        print(f"  Failed: {stats['failed']}")
        print(f"  Avg Duration: {stats['avg_duration_ms']:.2f}ms")
        print(f"  Avg Complexity: {stats['avg_complexity']:.1f}")
        print(f"  Federated Services: {stats['services']}")
        
        # Query Log
        print("\n📋 Recent Queries:")
        
        for query in platform.queries_log[-5:]:
            status_icon = "✅" if query.success else "❌"
            
            print(f"\n  {status_icon} {query.operation_name or 'Anonymous'}")
            print(f"     Type: {query.operation_type.value}")
            print(f"     Complexity: {query.complexity_score}")
            print(f"     Duration: {query.duration_ms:.2f}ms")
            print(f"     User: {query.user_id}")
            
        # Introspection Query
        print("\n🔎 Introspection:")
        
        schema = platform.schema_registry.get("base")
        
        print(f"\n  Types: {len(schema.types)}")
        
        for type_name, gql_type in list(schema.types.items())[:5]:
            fields_count = len(gql_type.fields) if gql_type.fields else 0
            print(f"    • {type_name} ({gql_type.kind}): {fields_count} fields")
            
        # Gateway Dashboard
        print("\n📊 GraphQL Gateway Dashboard:")
        print("  ┌─────────────────────────────────────────────────────┐")
        print(f"  │ Queries/min:    {stats['total_queries']:>8}                      │")
        print(f"  │ Success Rate:   {stats['successful']/max(1,stats['total_queries'])*100:>7.1f}%                      │")
        print(f"  │ Avg Latency:    {stats['avg_duration_ms']:>7.2f}ms                      │")
        print(f"  │ Cache Hit Rate: {cache_stats['hit_rate']:>7.1f}%                      │")
        print("  ├─────────────────────────────────────────────────────┤")
        
        for service in platform.federation.services.values():
            status = "●" if service.is_healthy else "○"
            print(f"  │ {status} {service.name:20} {service.requests_count:>6} reqs     │")
            
        print("  └─────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("GraphQL Gateway Platform initialized!")
    print("=" * 60)
