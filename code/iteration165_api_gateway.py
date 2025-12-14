#!/usr/bin/env python3
"""
Server Init - Iteration 165: API Gateway Platform
Платформа API Gateway

Функционал:
- Route Management - управление маршрутами
- Rate Limiting - ограничение запросов
- Authentication - аутентификация
- Request/Response Transformation - трансформация
- Load Balancing - балансировка нагрузки
- Circuit Breaker - предохранитель
- API Versioning - версионирование API
- Analytics & Monitoring - аналитика и мониторинг
"""

import asyncio
import json
import re
import time
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum
import uuid


class HttpMethod(Enum):
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


class LoadBalanceStrategy(Enum):
    """Стратегия балансировки"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"
    WEIGHTED = "weighted"
    IP_HASH = "ip_hash"


class CircuitState(Enum):
    """Состояние circuit breaker"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class RateLimitConfig:
    """Конфигурация rate limiting"""
    requests_per_second: int = 100
    requests_per_minute: int = 1000
    requests_per_hour: int = 10000
    burst_size: int = 50
    
    # Per client
    per_client_rps: int = 10
    per_client_rpm: int = 100


@dataclass
class Backend:
    """Backend сервис"""
    backend_id: str
    name: str = ""
    url: str = ""
    
    # Health
    healthy: bool = True
    health_check_url: str = ""
    
    # Load balancing
    weight: int = 1
    active_connections: int = 0
    
    # Stats
    total_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0


@dataclass
class Route:
    """Маршрут API"""
    route_id: str
    path: str = ""
    path_regex: Optional[str] = None
    
    # Methods
    methods: List[HttpMethod] = field(default_factory=list)
    
    # Backend
    backends: List[Backend] = field(default_factory=list)
    load_balance_strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN
    
    # Auth
    auth_type: AuthType = AuthType.NONE
    auth_config: Dict[str, Any] = field(default_factory=dict)
    
    # Rate limiting
    rate_limit: Optional[RateLimitConfig] = None
    
    # Transformation
    request_transforms: List[Dict] = field(default_factory=list)
    response_transforms: List[Dict] = field(default_factory=list)
    
    # Headers
    add_headers: Dict[str, str] = field(default_factory=dict)
    remove_headers: List[str] = field(default_factory=list)
    
    # Timeout
    timeout_ms: int = 30000
    
    # Retry
    retry_count: int = 3
    retry_delay_ms: int = 100
    
    # Cache
    cache_enabled: bool = False
    cache_ttl_seconds: int = 60
    
    # Enabled
    enabled: bool = True
    
    # Version
    version: str = "v1"


@dataclass
class ApiKey:
    """API ключ"""
    key_id: str
    key_hash: str = ""
    name: str = ""
    
    # Owner
    owner_id: str = ""
    
    # Permissions
    allowed_routes: List[str] = field(default_factory=list)
    
    # Rate limit override
    rate_limit_override: Optional[RateLimitConfig] = None
    
    # Status
    active: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None


@dataclass
class Request:
    """HTTP запрос"""
    request_id: str
    method: HttpMethod = HttpMethod.GET
    path: str = ""
    
    # Headers
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Query params
    query_params: Dict[str, str] = field(default_factory=dict)
    
    # Body
    body: Optional[str] = None
    
    # Client
    client_ip: str = ""
    client_id: str = ""
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Response:
    """HTTP ответ"""
    status_code: int = 200
    
    # Headers
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Body
    body: Optional[str] = None
    
    # Timing
    response_time_ms: float = 0.0
    
    # Backend
    backend_id: str = ""


@dataclass
class CircuitBreaker:
    """Circuit breaker"""
    circuit_id: str
    backend_id: str = ""
    
    # State
    state: CircuitState = CircuitState.CLOSED
    
    # Thresholds
    failure_threshold: int = 5
    success_threshold: int = 3
    timeout_seconds: int = 30
    
    # Counters
    failure_count: int = 0
    success_count: int = 0
    
    # Timestamps
    last_failure: Optional[datetime] = None
    state_changed_at: datetime = field(default_factory=datetime.now)


@dataclass
class RequestMetrics:
    """Метрики запроса"""
    route_id: str
    
    # Counts
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # Latency
    total_latency_ms: float = 0.0
    min_latency_ms: float = float('inf')
    max_latency_ms: float = 0.0
    
    # Status codes
    status_codes: Dict[int, int] = field(default_factory=dict)
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)


class RateLimiter:
    """Rate limiter"""
    
    def __init__(self):
        self.buckets: Dict[str, Dict] = {}
        
    def check_limit(self, key: str, config: RateLimitConfig) -> Tuple[bool, int]:
        """Проверка лимита"""
        now = time.time()
        
        if key not in self.buckets:
            self.buckets[key] = {
                "tokens": config.burst_size,
                "last_update": now,
                "requests_this_second": 0,
                "second_start": int(now)
            }
            
        bucket = self.buckets[key]
        
        # Token bucket refill
        elapsed = now - bucket["last_update"]
        refill = elapsed * config.requests_per_second
        bucket["tokens"] = min(config.burst_size, bucket["tokens"] + refill)
        bucket["last_update"] = now
        
        # Check second window
        current_second = int(now)
        if current_second != bucket["second_start"]:
            bucket["requests_this_second"] = 0
            bucket["second_start"] = current_second
            
        # Check if allowed
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            bucket["requests_this_second"] += 1
            remaining = int(bucket["tokens"])
            return True, remaining
        else:
            return False, 0
            
    def get_retry_after(self, key: str, config: RateLimitConfig) -> int:
        """Время до сброса лимита"""
        return int(1.0 / config.requests_per_second) + 1


class AuthManager:
    """Менеджер аутентификации"""
    
    def __init__(self):
        self.api_keys: Dict[str, ApiKey] = {}
        self.jwt_secret = "super-secret-key"
        
    def create_api_key(self, name: str, owner_id: str,
                        allowed_routes: List[str] = None) -> Tuple[str, ApiKey]:
        """Создание API ключа"""
        raw_key = f"sk_{uuid.uuid4().hex}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        api_key = ApiKey(
            key_id=f"key_{uuid.uuid4().hex[:8]}",
            key_hash=key_hash,
            name=name,
            owner_id=owner_id,
            allowed_routes=allowed_routes or []
        )
        
        self.api_keys[key_hash] = api_key
        return raw_key, api_key
        
    def validate_api_key(self, raw_key: str) -> Optional[ApiKey]:
        """Валидация API ключа"""
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        api_key = self.api_keys.get(key_hash)
        
        if api_key and api_key.active:
            if api_key.expires_at and api_key.expires_at < datetime.now():
                return None
            api_key.last_used = datetime.now()
            return api_key
            
        return None
        
    def authenticate(self, request: Request, route: Route) -> Tuple[bool, str]:
        """Аутентификация запроса"""
        if route.auth_type == AuthType.NONE:
            return True, ""
            
        if route.auth_type == AuthType.API_KEY:
            api_key = request.headers.get("X-API-Key", "")
            
            if not api_key:
                return False, "Missing API key"
                
            key_obj = self.validate_api_key(api_key)
            
            if not key_obj:
                return False, "Invalid API key"
                
            if key_obj.allowed_routes and route.route_id not in key_obj.allowed_routes:
                return False, "API key not authorized for this route"
                
            return True, ""
            
        if route.auth_type == AuthType.JWT:
            auth_header = request.headers.get("Authorization", "")
            
            if not auth_header.startswith("Bearer "):
                return False, "Missing or invalid Authorization header"
                
            # Simplified JWT validation
            token = auth_header[7:]
            if len(token) < 10:
                return False, "Invalid JWT token"
                
            return True, ""
            
        return True, ""


class LoadBalancer:
    """Балансировщик нагрузки"""
    
    def __init__(self):
        self.round_robin_index: Dict[str, int] = {}
        
    def select_backend(self, route: Route, client_ip: str = "") -> Optional[Backend]:
        """Выбор backend"""
        healthy_backends = [b for b in route.backends if b.healthy]
        
        if not healthy_backends:
            return None
            
        strategy = route.load_balance_strategy
        
        if strategy == LoadBalanceStrategy.ROUND_ROBIN:
            if route.route_id not in self.round_robin_index:
                self.round_robin_index[route.route_id] = 0
                
            index = self.round_robin_index[route.route_id]
            backend = healthy_backends[index % len(healthy_backends)]
            self.round_robin_index[route.route_id] = index + 1
            return backend
            
        elif strategy == LoadBalanceStrategy.LEAST_CONNECTIONS:
            return min(healthy_backends, key=lambda b: b.active_connections)
            
        elif strategy == LoadBalanceStrategy.RANDOM:
            import random
            return random.choice(healthy_backends)
            
        elif strategy == LoadBalanceStrategy.WEIGHTED:
            import random
            total_weight = sum(b.weight for b in healthy_backends)
            r = random.uniform(0, total_weight)
            
            cumulative = 0
            for backend in healthy_backends:
                cumulative += backend.weight
                if r <= cumulative:
                    return backend
                    
            return healthy_backends[-1]
            
        elif strategy == LoadBalanceStrategy.IP_HASH:
            hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
            index = hash_value % len(healthy_backends)
            return healthy_backends[index]
            
        return healthy_backends[0]


class CircuitBreakerManager:
    """Менеджер circuit breakers"""
    
    def __init__(self):
        self.circuits: Dict[str, CircuitBreaker] = {}
        
    def get_circuit(self, backend_id: str) -> CircuitBreaker:
        """Получение circuit breaker"""
        if backend_id not in self.circuits:
            self.circuits[backend_id] = CircuitBreaker(
                circuit_id=f"cb_{uuid.uuid4().hex[:8]}",
                backend_id=backend_id
            )
        return self.circuits[backend_id]
        
    def is_available(self, backend_id: str) -> bool:
        """Проверка доступности"""
        circuit = self.get_circuit(backend_id)
        
        if circuit.state == CircuitState.CLOSED:
            return True
            
        if circuit.state == CircuitState.OPEN:
            # Check if timeout passed
            if circuit.state_changed_at:
                elapsed = (datetime.now() - circuit.state_changed_at).total_seconds()
                if elapsed >= circuit.timeout_seconds:
                    circuit.state = CircuitState.HALF_OPEN
                    circuit.state_changed_at = datetime.now()
                    return True
            return False
            
        # Half-open - allow one request
        return True
        
    def record_success(self, backend_id: str):
        """Запись успеха"""
        circuit = self.get_circuit(backend_id)
        
        if circuit.state == CircuitState.HALF_OPEN:
            circuit.success_count += 1
            if circuit.success_count >= circuit.success_threshold:
                circuit.state = CircuitState.CLOSED
                circuit.failure_count = 0
                circuit.success_count = 0
                circuit.state_changed_at = datetime.now()
        else:
            circuit.failure_count = max(0, circuit.failure_count - 1)
            
    def record_failure(self, backend_id: str):
        """Запись ошибки"""
        circuit = self.get_circuit(backend_id)
        circuit.failure_count += 1
        circuit.last_failure = datetime.now()
        
        if circuit.state == CircuitState.HALF_OPEN:
            circuit.state = CircuitState.OPEN
            circuit.state_changed_at = datetime.now()
            circuit.success_count = 0
        elif circuit.failure_count >= circuit.failure_threshold:
            circuit.state = CircuitState.OPEN
            circuit.state_changed_at = datetime.now()


class RequestTransformer:
    """Трансформер запросов"""
    
    def transform_request(self, request: Request, route: Route) -> Request:
        """Трансформация запроса"""
        # Add headers
        for key, value in route.add_headers.items():
            request.headers[key] = value
            
        # Remove headers
        for key in route.remove_headers:
            request.headers.pop(key, None)
            
        # Add request ID
        request.headers["X-Request-ID"] = request.request_id
        
        # Add forwarded headers
        request.headers["X-Forwarded-For"] = request.client_ip
        request.headers["X-Forwarded-Proto"] = "https"
        
        # Apply custom transforms
        for transform in route.request_transforms:
            transform_type = transform.get("type")
            
            if transform_type == "add_header":
                request.headers[transform["key"]] = transform["value"]
            elif transform_type == "rewrite_path":
                pattern = transform.get("pattern", "")
                replacement = transform.get("replacement", "")
                request.path = re.sub(pattern, replacement, request.path)
                
        return request
        
    def transform_response(self, response: Response, route: Route) -> Response:
        """Трансформация ответа"""
        # Apply custom transforms
        for transform in route.response_transforms:
            transform_type = transform.get("type")
            
            if transform_type == "add_header":
                response.headers[transform["key"]] = transform["value"]
            elif transform_type == "remove_header":
                response.headers.pop(transform.get("key", ""), None)
                
        return response


class AnalyticsCollector:
    """Сборщик аналитики"""
    
    def __init__(self):
        self.metrics: Dict[str, RequestMetrics] = {}
        self.request_log: List[Dict] = []
        
    def record_request(self, request: Request, response: Response, route: Route):
        """Запись запроса"""
        # Update route metrics
        if route.route_id not in self.metrics:
            self.metrics[route.route_id] = RequestMetrics(route_id=route.route_id)
            
        metrics = self.metrics[route.route_id]
        metrics.total_requests += 1
        
        if 200 <= response.status_code < 400:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1
            
        metrics.total_latency_ms += response.response_time_ms
        metrics.min_latency_ms = min(metrics.min_latency_ms, response.response_time_ms)
        metrics.max_latency_ms = max(metrics.max_latency_ms, response.response_time_ms)
        
        status = response.status_code
        metrics.status_codes[status] = metrics.status_codes.get(status, 0) + 1
        
        # Log request
        log_entry = {
            "request_id": request.request_id,
            "method": request.method.value,
            "path": request.path,
            "status_code": response.status_code,
            "response_time_ms": response.response_time_ms,
            "client_ip": request.client_ip,
            "timestamp": request.timestamp.isoformat()
        }
        self.request_log.append(log_entry)
        
        # Keep last 10000 entries
        if len(self.request_log) > 10000:
            self.request_log = self.request_log[-10000:]
            
    def get_route_stats(self, route_id: str) -> Dict[str, Any]:
        """Статистика маршрута"""
        metrics = self.metrics.get(route_id)
        
        if not metrics:
            return {}
            
        avg_latency = metrics.total_latency_ms / metrics.total_requests if metrics.total_requests > 0 else 0
        success_rate = metrics.successful_requests / metrics.total_requests * 100 if metrics.total_requests > 0 else 0
        
        return {
            "route_id": route_id,
            "total_requests": metrics.total_requests,
            "successful_requests": metrics.successful_requests,
            "failed_requests": metrics.failed_requests,
            "success_rate": success_rate,
            "avg_latency_ms": avg_latency,
            "min_latency_ms": metrics.min_latency_ms if metrics.min_latency_ms != float('inf') else 0,
            "max_latency_ms": metrics.max_latency_ms,
            "status_codes": metrics.status_codes
        }


class APIGateway:
    """API Gateway"""
    
    def __init__(self):
        self.routes: Dict[str, Route] = {}
        self.rate_limiter = RateLimiter()
        self.auth_manager = AuthManager()
        self.load_balancer = LoadBalancer()
        self.circuit_breaker = CircuitBreakerManager()
        self.transformer = RequestTransformer()
        self.analytics = AnalyticsCollector()
        self.cache: Dict[str, Tuple[Response, datetime]] = {}
        
    def add_route(self, route: Route):
        """Добавление маршрута"""
        self.routes[route.route_id] = route
        
    def find_route(self, method: HttpMethod, path: str) -> Optional[Route]:
        """Поиск маршрута"""
        for route in self.routes.values():
            if not route.enabled:
                continue
                
            if method not in route.methods:
                continue
                
            # Check path regex
            if route.path_regex:
                if re.match(route.path_regex, path):
                    return route
            elif route.path == path or path.startswith(route.path):
                return route
                
        return None
        
    async def handle_request(self, request: Request) -> Response:
        """Обработка запроса"""
        start_time = time.time()
        
        # Find route
        route = self.find_route(request.method, request.path)
        
        if not route:
            return Response(status_code=404, body='{"error": "Route not found"}')
            
        # Check rate limit
        if route.rate_limit:
            limit_key = f"{route.route_id}:{request.client_ip}"
            allowed, remaining = self.rate_limiter.check_limit(limit_key, route.rate_limit)
            
            if not allowed:
                retry_after = self.rate_limiter.get_retry_after(limit_key, route.rate_limit)
                return Response(
                    status_code=429,
                    headers={"Retry-After": str(retry_after)},
                    body='{"error": "Rate limit exceeded"}'
                )
                
        # Authenticate
        auth_ok, auth_error = self.auth_manager.authenticate(request, route)
        
        if not auth_ok:
            return Response(status_code=401, body=f'{{"error": "{auth_error}"}}')
            
        # Check cache
        if route.cache_enabled and request.method == HttpMethod.GET:
            cache_key = f"{request.path}:{json.dumps(request.query_params, sort_keys=True)}"
            
            if cache_key in self.cache:
                cached_response, cache_time = self.cache[cache_key]
                age = (datetime.now() - cache_time).total_seconds()
                
                if age < route.cache_ttl_seconds:
                    cached_response.headers["X-Cache"] = "HIT"
                    return cached_response
                    
        # Transform request
        request = self.transformer.transform_request(request, route)
        
        # Select backend
        backend = self.load_balancer.select_backend(route, request.client_ip)
        
        if not backend:
            return Response(status_code=503, body='{"error": "No available backends"}')
            
        # Check circuit breaker
        if not self.circuit_breaker.is_available(backend.backend_id):
            return Response(status_code=503, body='{"error": "Service temporarily unavailable"}')
            
        # Forward request (simulated)
        response = await self._forward_request(request, backend, route)
        
        # Record circuit breaker
        if response.status_code >= 500:
            self.circuit_breaker.record_failure(backend.backend_id)
        else:
            self.circuit_breaker.record_success(backend.backend_id)
            
        # Transform response
        response = self.transformer.transform_response(response, route)
        
        # Calculate response time
        response.response_time_ms = (time.time() - start_time) * 1000
        
        # Cache response
        if route.cache_enabled and request.method == HttpMethod.GET and 200 <= response.status_code < 300:
            cache_key = f"{request.path}:{json.dumps(request.query_params, sort_keys=True)}"
            self.cache[cache_key] = (response, datetime.now())
            response.headers["X-Cache"] = "MISS"
            
        # Record analytics
        self.analytics.record_request(request, response, route)
        
        return response
        
    async def _forward_request(self, request: Request, backend: Backend,
                                route: Route) -> Response:
        """Пересылка запроса на backend"""
        # Simulate backend response
        await asyncio.sleep(0.01)  # Simulate network latency
        
        backend.total_requests += 1
        
        # Simulate occasional errors
        import random
        if random.random() < 0.05:
            backend.failed_requests += 1
            return Response(
                status_code=500,
                backend_id=backend.backend_id,
                body='{"error": "Internal server error"}'
            )
            
        return Response(
            status_code=200,
            backend_id=backend.backend_id,
            headers={"Content-Type": "application/json"},
            body='{"status": "success", "data": {}}'
        )


class APIGatewayPlatform:
    """Платформа API Gateway"""
    
    def __init__(self):
        self.gateway = APIGateway()
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_requests = sum(m.total_requests for m in self.gateway.analytics.metrics.values())
        
        circuit_states = {}
        for circuit in self.gateway.circuit_breaker.circuits.values():
            circuit_states[circuit.backend_id] = circuit.state.value
            
        return {
            "routes": len(self.gateway.routes),
            "total_requests": total_requests,
            "api_keys": len(self.gateway.auth_manager.api_keys),
            "circuit_states": circuit_states
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 165: API Gateway Platform")
    print("=" * 60)
    
    async def demo():
        platform = APIGatewayPlatform()
        print("✓ API Gateway Platform created")
        
        # Create backends
        print("\n🖥️ Creating Backends...")
        
        user_backends = [
            Backend(backend_id="user-1", name="User Service 1", url="http://user-1:8080", weight=2),
            Backend(backend_id="user-2", name="User Service 2", url="http://user-2:8080", weight=1),
        ]
        
        order_backends = [
            Backend(backend_id="order-1", name="Order Service 1", url="http://order-1:8080"),
            Backend(backend_id="order-2", name="Order Service 2", url="http://order-2:8080"),
            Backend(backend_id="order-3", name="Order Service 3", url="http://order-3:8080"),
        ]
        
        print(f"  ✓ User service: {len(user_backends)} backends")
        print(f"  ✓ Order service: {len(order_backends)} backends")
        
        # Create routes
        print("\n🛤️ Creating Routes...")
        
        # Users API route
        users_route = Route(
            route_id="users-api",
            path="/api/v1/users",
            path_regex=r"^/api/v1/users.*",
            methods=[HttpMethod.GET, HttpMethod.POST, HttpMethod.PUT, HttpMethod.DELETE],
            backends=user_backends,
            load_balance_strategy=LoadBalanceStrategy.WEIGHTED,
            auth_type=AuthType.API_KEY,
            rate_limit=RateLimitConfig(
                requests_per_second=100,
                per_client_rps=10,
                burst_size=20
            ),
            cache_enabled=True,
            cache_ttl_seconds=30,
            add_headers={"X-Service": "users"},
            version="v1"
        )
        platform.gateway.add_route(users_route)
        
        # Orders API route
        orders_route = Route(
            route_id="orders-api",
            path="/api/v1/orders",
            path_regex=r"^/api/v1/orders.*",
            methods=[HttpMethod.GET, HttpMethod.POST],
            backends=order_backends,
            load_balance_strategy=LoadBalanceStrategy.ROUND_ROBIN,
            auth_type=AuthType.JWT,
            rate_limit=RateLimitConfig(
                requests_per_second=50,
                per_client_rps=5,
                burst_size=10
            ),
            timeout_ms=5000,
            retry_count=2,
            version="v1"
        )
        platform.gateway.add_route(orders_route)
        
        # Health check route (no auth)
        health_route = Route(
            route_id="health",
            path="/health",
            methods=[HttpMethod.GET],
            backends=[Backend(backend_id="health", url="http://localhost:8080/health")],
            auth_type=AuthType.NONE
        )
        platform.gateway.add_route(health_route)
        
        print(f"  ✓ Created {len(platform.gateway.routes)} routes")
        
        # Create API keys
        print("\n🔑 Creating API Keys...")
        
        raw_key1, key1 = platform.gateway.auth_manager.create_api_key(
            "Production Key",
            "user-123",
            ["users-api", "orders-api"]
        )
        
        raw_key2, key2 = platform.gateway.auth_manager.create_api_key(
            "Development Key",
            "user-456",
            ["users-api"]
        )
        
        print(f"  ✓ Production Key: {raw_key1[:20]}...")
        print(f"  ✓ Development Key: {raw_key2[:20]}...")
        
        # Process requests
        print("\n📨 Processing Requests...")
        
        requests_to_process = [
            Request(
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                method=HttpMethod.GET,
                path="/api/v1/users",
                headers={"X-API-Key": raw_key1},
                client_ip="192.168.1.100"
            ),
            Request(
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                method=HttpMethod.POST,
                path="/api/v1/users",
                headers={"X-API-Key": raw_key1, "Content-Type": "application/json"},
                body='{"name": "John"}',
                client_ip="192.168.1.100"
            ),
            Request(
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                method=HttpMethod.GET,
                path="/api/v1/orders",
                headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.test"},
                client_ip="192.168.1.101"
            ),
            Request(
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                method=HttpMethod.GET,
                path="/health",
                client_ip="192.168.1.102"
            ),
            # Request without auth (should fail)
            Request(
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                method=HttpMethod.GET,
                path="/api/v1/users",
                client_ip="192.168.1.103"
            ),
        ]
        
        print("\n  ┌───────────────────────────────────────────────────────────────────────┐")
        print("  │ Request ID      │ Method │ Path              │ Status │ Time (ms) │")
        print("  ├───────────────────────────────────────────────────────────────────────┤")
        
        for req in requests_to_process:
            response = await platform.gateway.handle_request(req)
            
            req_id = req.request_id[:15].ljust(15)
            method = req.method.value.ljust(6)
            path = req.path[:17].ljust(17)
            status = str(response.status_code).ljust(6)
            time_ms = f"{response.response_time_ms:.2f}".ljust(9)
            
            print(f"  │ {req_id} │ {method} │ {path} │ {status} │ {time_ms} │")
            
        print("  └───────────────────────────────────────────────────────────────────────┘")
        
        # Process many requests for load testing
        print("\n🔄 Load Testing (100 requests)...")
        
        for i in range(100):
            req = Request(
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                method=HttpMethod.GET,
                path="/api/v1/users",
                headers={"X-API-Key": raw_key1},
                client_ip=f"192.168.1.{i % 256}"
            )
            await platform.gateway.handle_request(req)
            
        print("  ✓ Completed 100 requests")
        
        # Route statistics
        print("\n📊 Route Statistics:")
        
        print("\n  ┌───────────────────────────────────────────────────────────────────────────┐")
        print("  │ Route          │ Requests │ Success │ Failed │ Success% │ Avg (ms) │")
        print("  ├───────────────────────────────────────────────────────────────────────────┤")
        
        for route_id in platform.gateway.routes:
            stats = platform.gateway.analytics.get_route_stats(route_id)
            
            if stats:
                name = route_id[:14].ljust(14)
                total = str(stats["total_requests"]).ljust(8)
                success = str(stats["successful_requests"]).ljust(7)
                failed = str(stats["failed_requests"]).ljust(6)
                rate = f"{stats['success_rate']:.1f}%".ljust(8)
                avg_ms = f"{stats['avg_latency_ms']:.2f}".ljust(8)
                print(f"  │ {name} │ {total} │ {success} │ {failed} │ {rate} │ {avg_ms} │")
                
        print("  └───────────────────────────────────────────────────────────────────────────┘")
        
        # Circuit breaker status
        print("\n⚡ Circuit Breaker Status:")
        
        for backend in user_backends + order_backends:
            circuit = platform.gateway.circuit_breaker.get_circuit(backend.backend_id)
            status_icon = "🟢" if circuit.state == CircuitState.CLOSED else "🔴" if circuit.state == CircuitState.OPEN else "🟡"
            print(f"  {status_icon} {backend.name}: {circuit.state.value} (failures: {circuit.failure_count})")
            
        # Rate limiter test
        print("\n🚦 Rate Limiting Test...")
        
        # Send many requests from same IP
        allowed = 0
        rejected = 0
        
        for i in range(30):
            req = Request(
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                method=HttpMethod.GET,
                path="/api/v1/users",
                headers={"X-API-Key": raw_key1},
                client_ip="10.0.0.1"  # Same IP
            )
            response = await platform.gateway.handle_request(req)
            
            if response.status_code == 429:
                rejected += 1
            else:
                allowed += 1
                
        print(f"  Allowed: {allowed}, Rejected (rate limited): {rejected}")
        
        # API Gateway Configuration
        print("\n⚙️ Gateway Configuration:")
        
        print("\n  Routes:")
        for route in platform.gateway.routes.values():
            backends_count = len(route.backends)
            auth = route.auth_type.value
            lb = route.load_balance_strategy.value
            cache = "Yes" if route.cache_enabled else "No"
            print(f"    • {route.path}")
            print(f"      Methods: {', '.join(m.value for m in route.methods)}")
            print(f"      Backends: {backends_count}, LB: {lb}")
            print(f"      Auth: {auth}, Cache: {cache}")
            
        # Platform statistics
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Active Routes: {stats['routes']}")
        print(f"  Total Requests: {stats['total_requests']}")
        print(f"  API Keys: {stats['api_keys']}")
        
        # Dashboard
        print("\n┌────────────────────────────────────────────────────────────────────┐")
        print("│                     API Gateway Dashboard                          │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Active Routes:                {stats['routes']:>10}                       │")
        print(f"│ Total Requests Processed:     {stats['total_requests']:>10}                       │")
        print(f"│ Active API Keys:              {stats['api_keys']:>10}                       │")
        print("├────────────────────────────────────────────────────────────────────┤")
        
        total_backends = len(user_backends) + len(order_backends) + 1
        healthy_backends = sum(1 for b in user_backends + order_backends if b.healthy) + 1
        
        print(f"│ Total Backends:               {total_backends:>10}                       │")
        print(f"│ Healthy Backends:             {healthy_backends:>10}                       │")
        print("└────────────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("API Gateway Platform initialized!")
    print("=" * 60)
