#!/usr/bin/env python3
"""
Server Init - Iteration 56: API Gateway & Management
Шлюз и управление API

Функционал:
- API Gateway - шлюз API
- Route Management - управление маршрутами
- Request/Response Transformation - трансформация запросов
- Authentication & Authorization - аутентификация и авторизация
- API Versioning - версионирование API
- Rate Limiting & Throttling - ограничение скорости
- API Analytics - аналитика API
- Developer Portal - портал разработчиков
"""

import json
import asyncio
import hashlib
import time
import re
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Pattern
from enum import Enum
from collections import defaultdict
import random
import uuid


class HTTPMethod(Enum):
    """HTTP методы"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


class AuthType(Enum):
    """Тип аутентификации"""
    NONE = "none"
    API_KEY = "api_key"
    JWT = "jwt"
    OAUTH2 = "oauth2"
    BASIC = "basic"
    MTLS = "mtls"


class RateLimitScope(Enum):
    """Область rate limiting"""
    GLOBAL = "global"
    PER_API = "per_api"
    PER_USER = "per_user"
    PER_IP = "per_ip"


class APIStatus(Enum):
    """Статус API"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    RETIRED = "retired"
    BETA = "beta"
    DRAFT = "draft"


@dataclass
class APIRoute:
    """Маршрут API"""
    route_id: str
    path: str
    methods: List[HTTPMethod]
    
    # Backend
    backend_url: str = ""
    backend_timeout_ms: int = 30000
    
    # Трансформации
    request_transform: Optional[Dict[str, Any]] = None
    response_transform: Optional[Dict[str, Any]] = None
    
    # Auth
    auth_type: AuthType = AuthType.NONE
    required_scopes: List[str] = field(default_factory=list)
    
    # Rate limiting
    rate_limit: Optional[int] = None  # requests per minute
    
    # Caching
    cache_enabled: bool = False
    cache_ttl_seconds: int = 300
    
    # Статус
    enabled: bool = True
    
    # Метрики
    total_requests: int = 0
    error_count: int = 0
    avg_latency_ms: float = 0.0


@dataclass
class API:
    """API"""
    api_id: str
    name: str
    version: str
    
    # Базовый путь
    base_path: str = ""
    
    # Маршруты
    routes: List[APIRoute] = field(default_factory=list)
    
    # Метаданные
    description: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Статус
    status: APIStatus = APIStatus.ACTIVE
    
    # Auth по умолчанию
    default_auth: AuthType = AuthType.API_KEY
    
    # Rate limiting по умолчанию
    default_rate_limit: int = 1000  # per minute
    
    # CORS
    cors_enabled: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class APIKey:
    """API ключ"""
    key_id: str
    key_hash: str  # Хранится хеш, не сам ключ
    name: str
    
    # Владелец
    owner_id: str = ""
    
    # Разрешения
    allowed_apis: List[str] = field(default_factory=list)
    scopes: List[str] = field(default_factory=list)
    
    # Лимиты
    rate_limit: Optional[int] = None
    daily_quota: Optional[int] = None
    
    # Статус
    enabled: bool = True
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    # Статистика
    total_requests: int = 0
    last_used: Optional[datetime] = None


@dataclass
class Consumer:
    """Потребитель API"""
    consumer_id: str
    name: str
    email: str
    
    # Организация
    organization: str = ""
    
    # Ключи
    api_keys: List[str] = field(default_factory=list)
    
    # Подписки
    subscriptions: List[str] = field(default_factory=list)  # API IDs
    
    # Лимиты
    tier: str = "free"  # free, basic, pro, enterprise
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class APIRequest:
    """Запрос API"""
    request_id: str
    
    # Request
    method: HTTPMethod = HTTPMethod.GET
    path: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    query_params: Dict[str, str] = field(default_factory=dict)
    body: Optional[Any] = None
    
    # Клиент
    client_ip: str = ""
    api_key: Optional[str] = None
    consumer_id: Optional[str] = None
    
    # Время
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class APIResponse:
    """Ответ API"""
    status_code: int = 200
    headers: Dict[str, str] = field(default_factory=dict)
    body: Any = None
    
    # Метрики
    latency_ms: float = 0.0
    
    # Ошибка
    error: Optional[str] = None


@dataclass
class APIMetrics:
    """Метрики API"""
    api_id: str
    
    # Временной диапазон
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Запросы
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # Статус коды
    status_codes: Dict[int, int] = field(default_factory=dict)
    
    # Latency
    avg_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    
    # По эндпоинтам
    by_endpoint: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # По потребителям
    by_consumer: Dict[str, int] = field(default_factory=dict)


class RouteRegistry:
    """Реестр маршрутов"""
    
    def __init__(self):
        self.apis: Dict[str, API] = {}
        self.routes: Dict[str, APIRoute] = {}
        self.route_patterns: List[tuple] = []  # (pattern, route_id)
        
    def register_api(self, name: str, version: str, base_path: str,
                      **kwargs) -> API:
        """Регистрация API"""
        api = API(
            api_id=f"api_{uuid.uuid4().hex[:8]}",
            name=name,
            version=version,
            base_path=base_path,
            **kwargs
        )
        
        self.apis[api.api_id] = api
        return api
        
    def add_route(self, api_id: str, path: str, methods: List[HTTPMethod],
                   backend_url: str, **kwargs) -> APIRoute:
        """Добавление маршрута"""
        api = self.apis.get(api_id)
        if not api:
            raise ValueError("API not found")
            
        full_path = f"{api.base_path}{path}"
        
        route = APIRoute(
            route_id=f"route_{uuid.uuid4().hex[:8]}",
            path=full_path,
            methods=methods,
            backend_url=backend_url,
            auth_type=kwargs.get("auth_type", api.default_auth),
            rate_limit=kwargs.get("rate_limit", api.default_rate_limit),
            **{k: v for k, v in kwargs.items() if k not in ["auth_type", "rate_limit"]}
        )
        
        self.routes[route.route_id] = route
        api.routes.append(route)
        
        # Компиляция паттерна
        pattern = self._compile_pattern(full_path)
        self.route_patterns.append((pattern, route.route_id))
        
        return route
        
    def _compile_pattern(self, path: str) -> Pattern:
        """Компиляция паттерна пути"""
        # Конвертация {param} в regex группы
        pattern = re.sub(r'\{(\w+)\}', r'(?P<\1>[^/]+)', path)
        return re.compile(f"^{pattern}$")
        
    def match_route(self, method: HTTPMethod, path: str) -> Optional[tuple]:
        """Поиск подходящего маршрута"""
        for pattern, route_id in self.route_patterns:
            match = pattern.match(path)
            if match:
                route = self.routes.get(route_id)
                if route and method in route.methods and route.enabled:
                    return route, match.groupdict()
        return None


class AuthManager:
    """Менеджер аутентификации"""
    
    def __init__(self):
        self.api_keys: Dict[str, APIKey] = {}
        self.consumers: Dict[str, Consumer] = {}
        
    def create_api_key(self, name: str, owner_id: str, **kwargs) -> tuple:
        """Создание API ключа"""
        # Генерация ключа
        raw_key = f"sk_{uuid.uuid4().hex}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        api_key = APIKey(
            key_id=f"key_{uuid.uuid4().hex[:8]}",
            key_hash=key_hash,
            name=name,
            owner_id=owner_id,
            **kwargs
        )
        
        self.api_keys[api_key.key_id] = api_key
        
        return raw_key, api_key
        
    def validate_api_key(self, raw_key: str) -> Optional[APIKey]:
        """Валидация API ключа"""
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        for api_key in self.api_keys.values():
            if api_key.key_hash == key_hash:
                if not api_key.enabled:
                    return None
                if api_key.expires_at and api_key.expires_at < datetime.now():
                    return None
                    
                api_key.total_requests += 1
                api_key.last_used = datetime.now()
                return api_key
                
        return None
        
    def create_consumer(self, name: str, email: str, **kwargs) -> Consumer:
        """Создание потребителя"""
        consumer = Consumer(
            consumer_id=f"consumer_{uuid.uuid4().hex[:8]}",
            name=name,
            email=email,
            **kwargs
        )
        
        self.consumers[consumer.consumer_id] = consumer
        return consumer
        
    def authenticate(self, request: APIRequest, route: APIRoute) -> tuple:
        """Аутентификация запроса"""
        if route.auth_type == AuthType.NONE:
            return True, None
            
        if route.auth_type == AuthType.API_KEY:
            key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
            if not key:
                return False, "API key required"
                
            api_key = self.validate_api_key(key)
            if not api_key:
                return False, "Invalid API key"
                
            # Проверка scopes
            if route.required_scopes:
                if not all(s in api_key.scopes for s in route.required_scopes):
                    return False, "Insufficient permissions"
                    
            return True, api_key
            
        # JWT, OAuth2 и другие - упрощённая симуляция
        auth_header = request.headers.get("Authorization", "")
        if not auth_header:
            return False, "Authorization header required"
            
        return True, None


class RateLimiter:
    """Ограничитель скорости"""
    
    def __init__(self):
        self.counters: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
    def check_limit(self, key: str, limit: int, window_seconds: int = 60) -> tuple:
        """Проверка лимита"""
        now = time.time()
        window_start = now - window_seconds
        
        if key not in self.counters:
            self.counters[key] = {"requests": [], "window": window_seconds}
            
        # Очистка старых запросов
        self.counters[key]["requests"] = [
            t for t in self.counters[key]["requests"]
            if t > window_start
        ]
        
        current_count = len(self.counters[key]["requests"])
        
        if current_count >= limit:
            retry_after = int(self.counters[key]["requests"][0] + window_seconds - now) + 1
            return False, retry_after
            
        self.counters[key]["requests"].append(now)
        return True, limit - current_count - 1
        
    def get_usage(self, key: str) -> Dict[str, Any]:
        """Получение использования"""
        if key not in self.counters:
            return {"requests": 0, "limit": 0}
            
        return {
            "requests": len(self.counters[key]["requests"]),
            "window_seconds": self.counters[key].get("window", 60)
        }


class RequestTransformer:
    """Трансформатор запросов"""
    
    def transform_request(self, request: APIRequest, 
                           transform: Dict[str, Any]) -> APIRequest:
        """Трансформация запроса"""
        if not transform:
            return request
            
        # Header transformations
        if "headers" in transform:
            for action in transform["headers"]:
                if action["type"] == "add":
                    request.headers[action["name"]] = action["value"]
                elif action["type"] == "remove":
                    request.headers.pop(action["name"], None)
                elif action["type"] == "rename":
                    if action["from"] in request.headers:
                        request.headers[action["to"]] = request.headers.pop(action["from"])
                        
        # Path rewrite
        if "path_rewrite" in transform:
            pattern = transform["path_rewrite"].get("pattern", "")
            replacement = transform["path_rewrite"].get("replacement", "")
            request.path = re.sub(pattern, replacement, request.path)
            
        return request
        
    def transform_response(self, response: APIResponse,
                            transform: Dict[str, Any]) -> APIResponse:
        """Трансформация ответа"""
        if not transform:
            return response
            
        # Header transformations
        if "headers" in transform:
            for action in transform["headers"]:
                if action["type"] == "add":
                    response.headers[action["name"]] = action["value"]
                elif action["type"] == "remove":
                    response.headers.pop(action["name"], None)
                    
        return response


class APICache:
    """Кэш API"""
    
    def __init__(self):
        self.cache: Dict[str, tuple] = {}  # key -> (response, expires_at)
        
    def _generate_key(self, request: APIRequest) -> str:
        """Генерация ключа кэша"""
        key_parts = [
            request.method.value,
            request.path,
            json.dumps(sorted(request.query_params.items()))
        ]
        return hashlib.md5(":".join(key_parts).encode()).hexdigest()
        
    def get(self, request: APIRequest) -> Optional[APIResponse]:
        """Получение из кэша"""
        key = self._generate_key(request)
        
        if key in self.cache:
            response, expires_at = self.cache[key]
            if expires_at > datetime.now():
                return response
            else:
                del self.cache[key]
                
        return None
        
    def set(self, request: APIRequest, response: APIResponse, ttl_seconds: int):
        """Сохранение в кэш"""
        key = self._generate_key(request)
        expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
        self.cache[key] = (response, expires_at)
        
    def invalidate(self, pattern: str = None):
        """Инвалидация кэша"""
        if pattern:
            keys_to_remove = [k for k in self.cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self.cache[key]
        else:
            self.cache.clear()


class APIAnalytics:
    """Аналитика API"""
    
    def __init__(self):
        self.requests: List[Dict[str, Any]] = []
        self.metrics_cache: Dict[str, APIMetrics] = {}
        
    def record_request(self, api_id: str, route_id: str,
                        request: APIRequest, response: APIResponse,
                        consumer_id: str = None):
        """Запись запроса"""
        self.requests.append({
            "api_id": api_id,
            "route_id": route_id,
            "method": request.method.value,
            "path": request.path,
            "status_code": response.status_code,
            "latency_ms": response.latency_ms,
            "consumer_id": consumer_id,
            "client_ip": request.client_ip,
            "timestamp": datetime.now()
        })
        
        # Ограничение размера
        if len(self.requests) > 100000:
            self.requests = self.requests[-50000:]
            
    def get_metrics(self, api_id: str, hours: int = 24) -> APIMetrics:
        """Получение метрик"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        relevant = [
            r for r in self.requests
            if r["api_id"] == api_id and r["timestamp"] > cutoff
        ]
        
        if not relevant:
            return APIMetrics(api_id=api_id)
            
        metrics = APIMetrics(
            api_id=api_id,
            period_start=cutoff,
            period_end=datetime.now(),
            total_requests=len(relevant),
            successful_requests=len([r for r in relevant if r["status_code"] < 400]),
            failed_requests=len([r for r in relevant if r["status_code"] >= 400])
        )
        
        # Status codes
        for r in relevant:
            status = r["status_code"]
            metrics.status_codes[status] = metrics.status_codes.get(status, 0) + 1
            
        # Latency
        latencies = sorted([r["latency_ms"] for r in relevant])
        n = len(latencies)
        
        metrics.avg_latency_ms = sum(latencies) / n
        metrics.p50_latency_ms = latencies[int(n * 0.5)]
        metrics.p95_latency_ms = latencies[int(n * 0.95)] if n > 20 else latencies[-1]
        metrics.p99_latency_ms = latencies[int(n * 0.99)] if n > 100 else latencies[-1]
        
        # By endpoint
        by_endpoint = defaultdict(lambda: {"requests": 0, "errors": 0, "latency": []})
        for r in relevant:
            path = r["path"]
            by_endpoint[path]["requests"] += 1
            if r["status_code"] >= 400:
                by_endpoint[path]["errors"] += 1
            by_endpoint[path]["latency"].append(r["latency_ms"])
            
        for path, data in by_endpoint.items():
            metrics.by_endpoint[path] = {
                "requests": data["requests"],
                "errors": data["errors"],
                "avg_latency": sum(data["latency"]) / len(data["latency"])
            }
            
        # By consumer
        for r in relevant:
            consumer = r.get("consumer_id", "anonymous")
            metrics.by_consumer[consumer] = metrics.by_consumer.get(consumer, 0) + 1
            
        return metrics
        
    def get_top_endpoints(self, api_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Топ эндпоинтов"""
        metrics = self.get_metrics(api_id)
        
        endpoints = [
            {"path": path, **data}
            for path, data in metrics.by_endpoint.items()
        ]
        
        return sorted(endpoints, key=lambda e: e["requests"], reverse=True)[:limit]


class APIGateway:
    """API Gateway"""
    
    def __init__(self):
        self.route_registry = RouteRegistry()
        self.auth_manager = AuthManager()
        self.rate_limiter = RateLimiter()
        self.transformer = RequestTransformer()
        self.cache = APICache()
        self.analytics = APIAnalytics()
        
    async def handle_request(self, request: APIRequest) -> APIResponse:
        """Обработка запроса"""
        start_time = time.time()
        
        # Поиск маршрута
        match_result = self.route_registry.match_route(request.method, request.path)
        
        if not match_result:
            return APIResponse(
                status_code=404,
                body={"error": "Not found"},
                latency_ms=(time.time() - start_time) * 1000
            )
            
        route, path_params = match_result
        
        # Получение API
        api = None
        for a in self.route_registry.apis.values():
            if route in a.routes:
                api = a
                break
                
        # Аутентификация
        auth_result, auth_data = self.auth_manager.authenticate(request, route)
        
        if not auth_result:
            return APIResponse(
                status_code=401,
                body={"error": auth_data},
                latency_ms=(time.time() - start_time) * 1000
            )
            
        # Rate limiting
        rate_key = f"{route.route_id}:{request.client_ip}"
        limit = route.rate_limit or 1000
        
        allowed, remaining = self.rate_limiter.check_limit(rate_key, limit)
        
        if not allowed:
            return APIResponse(
                status_code=429,
                headers={"Retry-After": str(remaining)},
                body={"error": "Rate limit exceeded"},
                latency_ms=(time.time() - start_time) * 1000
            )
            
        # Проверка кэша
        if route.cache_enabled and request.method == HTTPMethod.GET:
            cached = self.cache.get(request)
            if cached:
                cached.headers["X-Cache"] = "HIT"
                return cached
                
        # Трансформация запроса
        request = self.transformer.transform_request(request, route.request_transform)
        
        # Вызов backend (симуляция)
        response = await self._call_backend(route, request, path_params)
        
        # Трансформация ответа
        response = self.transformer.transform_response(response, route.response_transform)
        
        # Кэширование
        if route.cache_enabled and request.method == HTTPMethod.GET and response.status_code == 200:
            self.cache.set(request, response, route.cache_ttl_seconds)
            response.headers["X-Cache"] = "MISS"
            
        response.latency_ms = (time.time() - start_time) * 1000
        
        # Обновление метрик
        route.total_requests += 1
        route.avg_latency_ms = (route.avg_latency_ms * (route.total_requests - 1) + response.latency_ms) / route.total_requests
        
        if response.status_code >= 400:
            route.error_count += 1
            
        # Аналитика
        consumer_id = None
        if isinstance(auth_data, APIKey):
            consumer_id = auth_data.owner_id
            
        if api:
            self.analytics.record_request(api.api_id, route.route_id, request, response, consumer_id)
            
        return response
        
    async def _call_backend(self, route: APIRoute, request: APIRequest,
                             path_params: Dict[str, str]) -> APIResponse:
        """Вызов backend"""
        # Симуляция вызова
        await asyncio.sleep(random.uniform(0.01, 0.1))
        
        # 95% успех
        if random.random() > 0.05:
            return APIResponse(
                status_code=200,
                headers={"Content-Type": "application/json"},
                body={"success": True, "path_params": path_params}
            )
        else:
            return APIResponse(
                status_code=500,
                body={"error": "Backend error"}
            )
            
    def get_status(self) -> Dict[str, Any]:
        """Статус gateway"""
        return {
            "apis": len(self.route_registry.apis),
            "routes": len(self.route_registry.routes),
            "api_keys": len(self.auth_manager.api_keys),
            "consumers": len(self.auth_manager.consumers),
            "cache_entries": len(self.cache.cache),
            "total_requests_recorded": len(self.analytics.requests)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 56: API Gateway & Management")
    print("=" * 60)
    
    async def demo():
        # Создание gateway
        gateway = APIGateway()
        print("✓ API Gateway created")
        
        # Регистрация API
        print("\n📡 Registering APIs...")
        
        user_api = gateway.route_registry.register_api(
            name="User API",
            version="v1",
            base_path="/api/v1/users",
            description="User management API",
            tags=["users", "auth"]
        )
        print(f"  ✓ {user_api.name} ({user_api.version})")
        
        order_api = gateway.route_registry.register_api(
            name="Order API",
            version="v1",
            base_path="/api/v1/orders",
            description="Order management API",
            tags=["orders", "commerce"]
        )
        print(f"  ✓ {order_api.name} ({order_api.version})")
        
        # Добавление маршрутов
        print("\n🛤️ Adding routes...")
        
        routes = [
            (user_api.api_id, "", [HTTPMethod.GET, HTTPMethod.POST], "http://user-service:8080/users"),
            (user_api.api_id, "/{user_id}", [HTTPMethod.GET, HTTPMethod.PUT, HTTPMethod.DELETE], "http://user-service:8080/users/{user_id}"),
            (user_api.api_id, "/{user_id}/profile", [HTTPMethod.GET], "http://user-service:8080/users/{user_id}/profile"),
            (order_api.api_id, "", [HTTPMethod.GET, HTTPMethod.POST], "http://order-service:8080/orders"),
            (order_api.api_id, "/{order_id}", [HTTPMethod.GET], "http://order-service:8080/orders/{order_id}"),
        ]
        
        for api_id, path, methods, backend in routes:
            route = gateway.route_registry.add_route(
                api_id, path, methods, backend,
                cache_enabled=HTTPMethod.GET in methods,
                cache_ttl_seconds=60
            )
            method_names = ", ".join(m.value for m in methods)
            print(f"  ✓ {route.path} [{method_names}]")
            
        # Создание потребителей и ключей
        print("\n👤 Creating consumers and API keys...")
        
        consumer1 = gateway.auth_manager.create_consumer(
            name="Mobile App",
            email="mobile@example.com",
            organization="Example Corp",
            tier="pro"
        )
        print(f"  ✓ Consumer: {consumer1.name}")
        
        raw_key, api_key = gateway.auth_manager.create_api_key(
            name="mobile-app-key",
            owner_id=consumer1.consumer_id,
            scopes=["read", "write"],
            rate_limit=5000
        )
        print(f"  ✓ API Key: {raw_key[:20]}...")
        
        # Обработка запросов
        print("\n📤 Processing requests...")
        
        requests_to_test = [
            APIRequest(
                request_id="req_1",
                method=HTTPMethod.GET,
                path="/api/v1/users",
                headers={"X-API-Key": raw_key},
                client_ip="192.168.1.100"
            ),
            APIRequest(
                request_id="req_2",
                method=HTTPMethod.GET,
                path="/api/v1/users/123",
                headers={"X-API-Key": raw_key},
                client_ip="192.168.1.100"
            ),
            APIRequest(
                request_id="req_3",
                method=HTTPMethod.POST,
                path="/api/v1/orders",
                headers={"X-API-Key": raw_key},
                body={"items": [{"product_id": "p1", "quantity": 2}]},
                client_ip="192.168.1.101"
            ),
            APIRequest(
                request_id="req_4",
                method=HTTPMethod.GET,
                path="/api/v1/orders/456",
                headers={"X-API-Key": raw_key},
                client_ip="192.168.1.102"
            ),
            APIRequest(
                request_id="req_5",
                method=HTTPMethod.GET,
                path="/api/v1/nonexistent",
                headers={"X-API-Key": raw_key},
                client_ip="192.168.1.103"
            ),
        ]
        
        for req in requests_to_test:
            response = await gateway.handle_request(req)
            status = "✓" if response.status_code < 400 else "✗"
            cache = response.headers.get("X-Cache", "N/A")
            print(f"  {status} {req.method.value} {req.path} -> {response.status_code} ({response.latency_ms:.1f}ms) [Cache: {cache}]")
            
        # Тест кэша
        print("\n💾 Testing cache...")
        
        for i in range(3):
            req = APIRequest(
                request_id=f"cache_req_{i}",
                method=HTTPMethod.GET,
                path="/api/v1/users",
                headers={"X-API-Key": raw_key},
                client_ip="192.168.1.100"
            )
            response = await gateway.handle_request(req)
            cache = response.headers.get("X-Cache", "N/A")
            print(f"  Request {i+1}: Cache {cache}, Latency: {response.latency_ms:.1f}ms")
            
        # Тест rate limiting
        print("\n⏱️ Testing rate limiting...")
        
        # Создаём ключ с низким лимитом
        _, limited_key = gateway.auth_manager.create_api_key(
            name="limited-key",
            owner_id=consumer1.consumer_id,
            rate_limit=5
        )
        
        # Создаём route с низким лимитом
        gateway.route_registry.add_route(
            user_api.api_id,
            "/limited",
            [HTTPMethod.GET],
            "http://user-service:8080/limited",
            rate_limit=5
        )
        
        results = {"success": 0, "rate_limited": 0}
        for i in range(10):
            req = APIRequest(
                request_id=f"rl_req_{i}",
                method=HTTPMethod.GET,
                path="/api/v1/users/limited",
                headers={"X-API-Key": raw_key},
                client_ip="192.168.1.200"
            )
            response = await gateway.handle_request(req)
            
            if response.status_code == 429:
                results["rate_limited"] += 1
            else:
                results["success"] += 1
                
        print(f"  Success: {results['success']}, Rate limited: {results['rate_limited']}")
        
        # Тест без auth
        print("\n🔐 Testing authentication...")
        
        no_auth_req = APIRequest(
            request_id="no_auth",
            method=HTTPMethod.GET,
            path="/api/v1/users",
            client_ip="192.168.1.100"
        )
        response = await gateway.handle_request(no_auth_req)
        print(f"  No API key: {response.status_code} - {response.body.get('error', '')}")
        
        invalid_req = APIRequest(
            request_id="invalid_auth",
            method=HTTPMethod.GET,
            path="/api/v1/users",
            headers={"X-API-Key": "invalid_key"},
            client_ip="192.168.1.100"
        )
        response = await gateway.handle_request(invalid_req)
        print(f"  Invalid key: {response.status_code} - {response.body.get('error', '')}")
        
        # Массовые запросы для аналитики
        print("\n📊 Generating analytics data...")
        
        for i in range(100):
            req = APIRequest(
                request_id=f"bulk_{i}",
                method=random.choice([HTTPMethod.GET, HTTPMethod.POST]),
                path=random.choice(["/api/v1/users", "/api/v1/users/123", "/api/v1/orders"]),
                headers={"X-API-Key": raw_key},
                client_ip=f"192.168.1.{random.randint(1, 254)}"
            )
            await gateway.handle_request(req)
            
        print("  ✓ 100 requests generated")
        
        # Получение метрик
        print("\n📈 API Metrics:")
        
        metrics = gateway.analytics.get_metrics(user_api.api_id)
        print(f"\n  {user_api.name}:")
        print(f"    Total requests: {metrics.total_requests}")
        print(f"    Successful: {metrics.successful_requests}")
        print(f"    Failed: {metrics.failed_requests}")
        print(f"    Avg latency: {metrics.avg_latency_ms:.2f}ms")
        print(f"    P95 latency: {metrics.p95_latency_ms:.2f}ms")
        
        # Топ эндпоинтов
        print("\n  Top endpoints:")
        top = gateway.analytics.get_top_endpoints(user_api.api_id, 3)
        for ep in top:
            print(f"    {ep['path']}: {ep['requests']} requests, {ep['avg_latency']:.1f}ms avg")
            
        # Статус gateway
        print("\n📊 Gateway Status:")
        status = gateway.get_status()
        print(f"  APIs: {status['apis']}")
        print(f"  Routes: {status['routes']}")
        print(f"  API Keys: {status['api_keys']}")
        print(f"  Consumers: {status['consumers']}")
        print(f"  Cache entries: {status['cache_entries']}")
        print(f"  Requests recorded: {status['total_requests_recorded']}")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("API Gateway & Management Platform initialized!")
    print("=" * 60)
