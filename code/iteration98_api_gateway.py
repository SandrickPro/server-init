#!/usr/bin/env python3
"""
Server Init - Iteration 98: API Gateway Platform
Платформа API Gateway

Функционал:
- Request Routing - маршрутизация запросов
- Rate Limiting - ограничение скорости
- Authentication - аутентификация
- Load Balancing - балансировка нагрузки
- Request/Response Transformation - трансформация
- Circuit Breaker - circuit breaker
- Caching - кэширование
- Monitoring & Metrics - мониторинг
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Union, Tuple
from enum import Enum
from collections import defaultdict
import uuid
import random
import hashlib
import re


class HTTPMethod(Enum):
    """HTTP метод"""
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
    BASIC = "basic"
    OAUTH2 = "oauth2"


class RateLimitStrategy(Enum):
    """Стратегия rate limiting"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"


class CircuitState(Enum):
    """Состояние circuit breaker"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class LoadBalanceAlgorithm(Enum):
    """Алгоритм балансировки"""
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED = "weighted"


@dataclass
class Request:
    """HTTP запрос"""
    request_id: str
    method: HTTPMethod = HTTPMethod.GET
    path: str = ""
    
    # Headers
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Body
    body: Optional[str] = None
    
    # Query params
    query_params: Dict[str, str] = field(default_factory=dict)
    
    # Client info
    client_ip: str = ""
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Response:
    """HTTP ответ"""
    status_code: int = 200
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[str] = None
    
    # Timing
    latency_ms: float = 0


@dataclass
class Route:
    """Маршрут"""
    route_id: str
    name: str = ""
    
    # Matching
    path_pattern: str = ""  # /api/users/{id}
    methods: List[HTTPMethod] = field(default_factory=lambda: [HTTPMethod.GET])
    
    # Target
    upstream: str = ""  # service name or URL
    
    # Transformations
    strip_prefix: str = ""
    add_prefix: str = ""
    rewrite_path: str = ""
    
    # Headers
    add_headers: Dict[str, str] = field(default_factory=dict)
    remove_headers: List[str] = field(default_factory=list)
    
    # Features
    auth_required: bool = False
    auth_type: AuthType = AuthType.NONE
    rate_limit: Optional[int] = None  # requests per minute
    cache_ttl: int = 0  # seconds, 0 = no cache
    
    # Circuit breaker
    circuit_breaker_enabled: bool = False
    
    # Priority (higher = first)
    priority: int = 0
    
    # Status
    enabled: bool = True


@dataclass
class Upstream:
    """Upstream сервис"""
    upstream_id: str
    name: str = ""
    
    # Targets
    targets: List[Dict[str, Any]] = field(default_factory=list)
    
    # Health check
    health_check_path: str = "/health"
    health_check_interval: int = 10
    
    # Load balancing
    algorithm: LoadBalanceAlgorithm = LoadBalanceAlgorithm.ROUND_ROBIN
    
    # Timeouts
    connect_timeout: int = 5000  # ms
    read_timeout: int = 30000  # ms


@dataclass
class Consumer:
    """API Consumer"""
    consumer_id: str
    name: str = ""
    
    # Credentials
    api_key: str = ""
    
    # Limits
    rate_limit: int = 1000  # requests per minute
    
    # Allowed routes
    allowed_routes: List[str] = field(default_factory=list)  # empty = all
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RateLimitState:
    """Состояние rate limiter"""
    key: str
    count: int = 0
    window_start: datetime = field(default_factory=datetime.now)
    tokens: float = 0


@dataclass 
class CircuitBreakerState:
    """Состояние circuit breaker"""
    upstream: str
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure: Optional[datetime] = None
    state_changed_at: datetime = field(default_factory=datetime.now)


@dataclass
class CacheEntry:
    """Запись кэша"""
    key: str
    value: Response = field(default_factory=Response)
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=datetime.now)
    hits: int = 0


class PathMatcher:
    """Сопоставление путей"""
    
    @staticmethod
    def match(pattern: str, path: str) -> Tuple[bool, Dict[str, str]]:
        """Сопоставление пути с паттерном"""
        # Преобразуем паттерн в regex
        # /api/users/{id} -> /api/users/(?P<id>[^/]+)
        regex_pattern = pattern
        params = {}
        
        # Находим параметры {param}
        param_matches = re.findall(r'\{(\w+)\}', pattern)
        for param in param_matches:
            regex_pattern = regex_pattern.replace(
                f'{{{param}}}',
                f'(?P<{param}>[^/]+)'
            )
            
        # Wildcard support
        regex_pattern = regex_pattern.replace('*', '.*')
        
        # Match
        match = re.fullmatch(regex_pattern, path)
        if match:
            params = match.groupdict()
            return True, params
            
        return False, {}


class RateLimiter:
    """Rate limiter"""
    
    def __init__(self, strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW):
        self.strategy = strategy
        self.states: Dict[str, RateLimitState] = {}
        
    def check(self, key: str, limit: int, window_seconds: int = 60) -> Tuple[bool, int]:
        """Проверка лимита"""
        now = datetime.now()
        state = self.states.get(key)
        
        if not state:
            state = RateLimitState(key=key, window_start=now)
            self.states[key] = state
            
        if self.strategy == RateLimitStrategy.FIXED_WINDOW:
            return self._fixed_window(state, limit, window_seconds, now)
        elif self.strategy == RateLimitStrategy.SLIDING_WINDOW:
            return self._sliding_window(state, limit, window_seconds, now)
        else:
            return self._token_bucket(state, limit, window_seconds, now)
            
    def _fixed_window(self, state: RateLimitState, limit: int,
                       window_seconds: int, now: datetime) -> Tuple[bool, int]:
        """Fixed window algorithm"""
        window_start = state.window_start
        elapsed = (now - window_start).total_seconds()
        
        if elapsed >= window_seconds:
            # New window
            state.window_start = now
            state.count = 1
            return True, limit - 1
            
        if state.count >= limit:
            return False, 0
            
        state.count += 1
        return True, limit - state.count
        
    def _sliding_window(self, state: RateLimitState, limit: int,
                         window_seconds: int, now: datetime) -> Tuple[bool, int]:
        """Sliding window algorithm"""
        # Simplified sliding window
        elapsed = (now - state.window_start).total_seconds()
        
        if elapsed >= window_seconds:
            state.window_start = now
            state.count = 1
            return True, limit - 1
            
        # Weight previous window
        weight = 1 - (elapsed / window_seconds)
        effective_count = int(state.count * weight)
        
        if effective_count >= limit:
            return False, 0
            
        state.count = effective_count + 1
        return True, limit - state.count
        
    def _token_bucket(self, state: RateLimitState, limit: int,
                       window_seconds: int, now: datetime) -> Tuple[bool, int]:
        """Token bucket algorithm"""
        elapsed = (now - state.window_start).total_seconds()
        
        # Refill tokens
        refill_rate = limit / window_seconds
        state.tokens = min(limit, state.tokens + elapsed * refill_rate)
        state.window_start = now
        
        if state.tokens < 1:
            return False, 0
            
        state.tokens -= 1
        return True, int(state.tokens)


class CircuitBreaker:
    """Circuit breaker"""
    
    def __init__(self, failure_threshold: int = 5,
                  recovery_timeout: int = 30,
                  half_open_requests: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_requests = half_open_requests
        self.states: Dict[str, CircuitBreakerState] = {}
        
    def get_state(self, upstream: str) -> CircuitBreakerState:
        """Получение состояния"""
        if upstream not in self.states:
            self.states[upstream] = CircuitBreakerState(upstream=upstream)
        return self.states[upstream]
        
    def allow_request(self, upstream: str) -> bool:
        """Разрешить запрос?"""
        state = self.get_state(upstream)
        now = datetime.now()
        
        if state.state == CircuitState.CLOSED:
            return True
            
        if state.state == CircuitState.OPEN:
            # Check if recovery timeout passed
            elapsed = (now - state.state_changed_at).total_seconds()
            if elapsed >= self.recovery_timeout:
                state.state = CircuitState.HALF_OPEN
                state.state_changed_at = now
                state.success_count = 0
                return True
            return False
            
        # HALF_OPEN - allow limited requests
        return state.success_count < self.half_open_requests
        
    def record_success(self, upstream: str) -> None:
        """Записать успех"""
        state = self.get_state(upstream)
        
        if state.state == CircuitState.HALF_OPEN:
            state.success_count += 1
            if state.success_count >= self.half_open_requests:
                state.state = CircuitState.CLOSED
                state.failure_count = 0
                state.state_changed_at = datetime.now()
        else:
            state.failure_count = max(0, state.failure_count - 1)
            
    def record_failure(self, upstream: str) -> None:
        """Записать неудачу"""
        state = self.get_state(upstream)
        now = datetime.now()
        
        state.failure_count += 1
        state.last_failure = now
        
        if state.state == CircuitState.HALF_OPEN:
            state.state = CircuitState.OPEN
            state.state_changed_at = now
        elif state.failure_count >= self.failure_threshold:
            state.state = CircuitState.OPEN
            state.state_changed_at = now


class ResponseCache:
    """Кэш ответов"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: Dict[str, CacheEntry] = {}
        
    def get(self, key: str) -> Optional[Response]:
        """Получение из кэша"""
        entry = self.cache.get(key)
        if not entry:
            return None
            
        if datetime.now() > entry.expires_at:
            del self.cache[key]
            return None
            
        entry.hits += 1
        return entry.value
        
    def set(self, key: str, response: Response, ttl: int) -> None:
        """Сохранение в кэш"""
        if len(self.cache) >= self.max_size:
            # Evict oldest
            oldest_key = min(self.cache.keys(),
                            key=lambda k: self.cache[k].created_at)
            del self.cache[oldest_key]
            
        now = datetime.now()
        self.cache[key] = CacheEntry(
            key=key,
            value=response,
            created_at=now,
            expires_at=now + timedelta(seconds=ttl)
        )
        
    def invalidate(self, pattern: str = None) -> int:
        """Инвалидация кэша"""
        if pattern is None:
            count = len(self.cache)
            self.cache.clear()
            return count
            
        # Pattern matching
        keys_to_remove = [
            k for k in self.cache.keys()
            if re.match(pattern, k)
        ]
        for key in keys_to_remove:
            del self.cache[key]
        return len(keys_to_remove)


class LoadBalancer:
    """Балансировщик нагрузки"""
    
    def __init__(self):
        self.counters: Dict[str, int] = defaultdict(int)
        
    def select(self, upstream: Upstream) -> Optional[Dict[str, Any]]:
        """Выбор target"""
        healthy_targets = [t for t in upstream.targets if t.get('healthy', True)]
        
        if not healthy_targets:
            return None
            
        if upstream.algorithm == LoadBalanceAlgorithm.ROUND_ROBIN:
            idx = self.counters[upstream.name] % len(healthy_targets)
            self.counters[upstream.name] += 1
            return healthy_targets[idx]
            
        elif upstream.algorithm == LoadBalanceAlgorithm.RANDOM:
            return random.choice(healthy_targets)
            
        elif upstream.algorithm == LoadBalanceAlgorithm.WEIGHTED:
            total_weight = sum(t.get('weight', 100) for t in healthy_targets)
            r = random.randint(0, total_weight - 1)
            current = 0
            for target in healthy_targets:
                current += target.get('weight', 100)
                if r < current:
                    return target
                    
        return healthy_targets[0]


class AuthManager:
    """Менеджер аутентификации"""
    
    def __init__(self):
        self.api_keys: Dict[str, Consumer] = {}
        
    def register_consumer(self, consumer: Consumer) -> None:
        """Регистрация consumer"""
        if consumer.api_key:
            self.api_keys[consumer.api_key] = consumer
            
    def authenticate(self, request: Request,
                      auth_type: AuthType) -> Tuple[bool, Optional[Consumer]]:
        """Аутентификация"""
        if auth_type == AuthType.NONE:
            return True, None
            
        if auth_type == AuthType.API_KEY:
            return self._auth_api_key(request)
            
        if auth_type == AuthType.JWT:
            return self._auth_jwt(request)
            
        if auth_type == AuthType.BASIC:
            return self._auth_basic(request)
            
        return False, None
        
    def _auth_api_key(self, request: Request) -> Tuple[bool, Optional[Consumer]]:
        """API Key аутентификация"""
        api_key = request.headers.get('X-API-Key') or request.query_params.get('api_key')
        
        if not api_key:
            return False, None
            
        consumer = self.api_keys.get(api_key)
        return consumer is not None, consumer
        
    def _auth_jwt(self, request: Request) -> Tuple[bool, Optional[Consumer]]:
        """JWT аутентификация"""
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return False, None
            
        # Simplified JWT validation
        token = auth_header[7:]
        # In real implementation, validate JWT signature and claims
        return len(token) > 10, None
        
    def _auth_basic(self, request: Request) -> Tuple[bool, Optional[Consumer]]:
        """Basic аутентификация"""
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Basic '):
            return False, None
            
        # In real implementation, decode and validate credentials
        return True, None


class APIGatewayPlatform:
    """API Gateway платформа"""
    
    def __init__(self):
        self.routes: Dict[str, Route] = {}
        self.upstreams: Dict[str, Upstream] = {}
        self.consumers: Dict[str, Consumer] = {}
        
        self.rate_limiter = RateLimiter()
        self.circuit_breaker = CircuitBreaker()
        self.cache = ResponseCache()
        self.load_balancer = LoadBalancer()
        self.auth_manager = AuthManager()
        
        # Metrics
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "rate_limited": 0,
            "circuit_broken": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_latency_ms": 0
        }
        
    def add_route(self, path_pattern: str, upstream: str,
                   methods: List[HTTPMethod] = None,
                   **kwargs) -> Route:
        """Добавление маршрута"""
        route = Route(
            route_id=f"route_{uuid.uuid4().hex[:8]}",
            path_pattern=path_pattern,
            upstream=upstream,
            methods=methods or [HTTPMethod.GET],
            **kwargs
        )
        self.routes[route.route_id] = route
        return route
        
    def add_upstream(self, name: str, targets: List[Dict[str, Any]],
                      **kwargs) -> Upstream:
        """Добавление upstream"""
        upstream = Upstream(
            upstream_id=f"upstream_{uuid.uuid4().hex[:8]}",
            name=name,
            targets=targets,
            **kwargs
        )
        self.upstreams[name] = upstream
        return upstream
        
    def add_consumer(self, name: str, api_key: str = None,
                      rate_limit: int = 1000) -> Consumer:
        """Добавление consumer"""
        consumer = Consumer(
            consumer_id=f"consumer_{uuid.uuid4().hex[:8]}",
            name=name,
            api_key=api_key or f"key_{uuid.uuid4().hex}",
            rate_limit=rate_limit
        )
        self.consumers[consumer.consumer_id] = consumer
        self.auth_manager.register_consumer(consumer)
        return consumer
        
    def _find_route(self, request: Request) -> Tuple[Optional[Route], Dict[str, str]]:
        """Поиск маршрута"""
        # Sort by priority
        sorted_routes = sorted(
            self.routes.values(),
            key=lambda r: r.priority,
            reverse=True
        )
        
        for route in sorted_routes:
            if not route.enabled:
                continue
                
            if request.method not in route.methods:
                continue
                
            matched, params = PathMatcher.match(route.path_pattern, request.path)
            if matched:
                return route, params
                
        return None, {}
        
    async def handle_request(self, request: Request) -> Response:
        """Обработка запроса"""
        start_time = datetime.now()
        self.metrics["total_requests"] += 1
        
        # Find route
        route, path_params = self._find_route(request)
        
        if not route:
            return Response(status_code=404, body='{"error": "Not Found"}')
            
        # Authentication
        if route.auth_required:
            auth_ok, consumer = self.auth_manager.authenticate(request, route.auth_type)
            if not auth_ok:
                return Response(status_code=401, body='{"error": "Unauthorized"}')
                
        # Rate limiting
        if route.rate_limit:
            rate_key = f"{request.client_ip}:{route.route_id}"
            allowed, remaining = self.rate_limiter.check(rate_key, route.rate_limit)
            
            if not allowed:
                self.metrics["rate_limited"] += 1
                return Response(
                    status_code=429,
                    headers={"X-RateLimit-Remaining": "0"},
                    body='{"error": "Rate limit exceeded"}'
                )
                
        # Check circuit breaker
        if route.circuit_breaker_enabled:
            if not self.circuit_breaker.allow_request(route.upstream):
                self.metrics["circuit_broken"] += 1
                return Response(
                    status_code=503,
                    body='{"error": "Service temporarily unavailable"}'
                )
                
        # Check cache
        if route.cache_ttl > 0 and request.method == HTTPMethod.GET:
            cache_key = f"{route.route_id}:{request.path}:{json.dumps(request.query_params, sort_keys=True)}"
            cached = self.cache.get(cache_key)
            
            if cached:
                self.metrics["cache_hits"] += 1
                cached.headers["X-Cache"] = "HIT"
                return cached
            else:
                self.metrics["cache_misses"] += 1
                
        # Forward to upstream
        response = await self._forward_request(request, route, path_params)
        
        # Record circuit breaker result
        if route.circuit_breaker_enabled:
            if response.status_code >= 500:
                self.circuit_breaker.record_failure(route.upstream)
            else:
                self.circuit_breaker.record_success(route.upstream)
                
        # Cache response
        if route.cache_ttl > 0 and request.method == HTTPMethod.GET:
            if 200 <= response.status_code < 300:
                cache_key = f"{route.route_id}:{request.path}:{json.dumps(request.query_params, sort_keys=True)}"
                self.cache.set(cache_key, response, route.cache_ttl)
                response.headers["X-Cache"] = "MISS"
                
        # Update metrics
        latency = (datetime.now() - start_time).total_seconds() * 1000
        response.latency_ms = latency
        self.metrics["total_latency_ms"] += latency
        
        if 200 <= response.status_code < 400:
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["failed_requests"] += 1
            
        return response
        
    async def _forward_request(self, request: Request, route: Route,
                                path_params: Dict[str, str]) -> Response:
        """Пересылка запроса на upstream"""
        upstream = self.upstreams.get(route.upstream)
        if not upstream:
            return Response(status_code=502, body='{"error": "Bad Gateway"}')
            
        # Select target
        target = self.load_balancer.select(upstream)
        if not target:
            return Response(status_code=503, body='{"error": "No healthy targets"}')
            
        # Transform path
        target_path = request.path
        if route.strip_prefix:
            target_path = target_path.replace(route.strip_prefix, '', 1)
        if route.add_prefix:
            target_path = route.add_prefix + target_path
        if route.rewrite_path:
            # Simple rewrite
            for param, value in path_params.items():
                route.rewrite_path = route.rewrite_path.replace(f'${param}', value)
            target_path = route.rewrite_path
            
        # Simulate upstream call
        await asyncio.sleep(random.uniform(0.01, 0.05))
        
        # Simulate response
        if random.random() > 0.02:  # 98% success rate
            return Response(
                status_code=200,
                headers={
                    "Content-Type": "application/json",
                    "X-Upstream-Target": f"{target.get('host')}:{target.get('port')}"
                },
                body=json.dumps({
                    "message": "Success",
                    "path": target_path,
                    "upstream": route.upstream
                })
            )
        else:
            return Response(status_code=500, body='{"error": "Internal Server Error"}')
            
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total = self.metrics["total_requests"]
        avg_latency = (self.metrics["total_latency_ms"] / total) if total > 0 else 0
        
        cache_total = self.metrics["cache_hits"] + self.metrics["cache_misses"]
        cache_hit_rate = (self.metrics["cache_hits"] / cache_total * 100) if cache_total > 0 else 0
        
        return {
            **self.metrics,
            "routes": len(self.routes),
            "upstreams": len(self.upstreams),
            "consumers": len(self.consumers),
            "avg_latency_ms": round(avg_latency, 2),
            "cache_hit_rate": round(cache_hit_rate, 2),
            "cache_entries": len(self.cache.cache)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 98: API Gateway Platform")
    print("=" * 60)
    
    async def demo():
        gateway = APIGatewayPlatform()
        print("✓ API Gateway Platform created")
        
        # Upstreams
        print("\n🔧 Adding Upstreams...")
        
        gateway.add_upstream(
            "user-service",
            targets=[
                {"host": "10.0.1.1", "port": 8080, "weight": 100, "healthy": True},
                {"host": "10.0.1.2", "port": 8080, "weight": 100, "healthy": True},
                {"host": "10.0.1.3", "port": 8080, "weight": 50, "healthy": True}
            ],
            algorithm=LoadBalanceAlgorithm.WEIGHTED
        )
        print("  ✓ user-service: 3 targets")
        
        gateway.add_upstream(
            "order-service",
            targets=[
                {"host": "10.0.2.1", "port": 8081, "weight": 100, "healthy": True},
                {"host": "10.0.2.2", "port": 8081, "weight": 100, "healthy": True}
            ],
            algorithm=LoadBalanceAlgorithm.ROUND_ROBIN
        )
        print("  ✓ order-service: 2 targets")
        
        gateway.add_upstream(
            "product-service",
            targets=[
                {"host": "10.0.3.1", "port": 8082, "weight": 100, "healthy": True}
            ]
        )
        print("  ✓ product-service: 1 target")
        
        # Routes
        print("\n📍 Adding Routes...")
        
        # Users API
        gateway.add_route(
            "/api/v1/users",
            "user-service",
            methods=[HTTPMethod.GET, HTTPMethod.POST],
            name="users-list",
            rate_limit=100,
            auth_required=True,
            auth_type=AuthType.API_KEY
        )
        
        gateway.add_route(
            "/api/v1/users/{id}",
            "user-service",
            methods=[HTTPMethod.GET, HTTPMethod.PUT, HTTPMethod.DELETE],
            name="users-detail",
            rate_limit=100,
            cache_ttl=60,
            auth_required=True,
            auth_type=AuthType.API_KEY
        )
        
        print("  ✓ /api/v1/users (list, detail)")
        
        # Orders API
        gateway.add_route(
            "/api/v1/orders",
            "order-service",
            methods=[HTTPMethod.GET, HTTPMethod.POST],
            name="orders-list",
            circuit_breaker_enabled=True
        )
        
        gateway.add_route(
            "/api/v1/orders/{id}",
            "order-service",
            methods=[HTTPMethod.GET],
            name="orders-detail",
            circuit_breaker_enabled=True
        )
        
        print("  ✓ /api/v1/orders (list, detail)")
        
        # Products API
        gateway.add_route(
            "/api/v1/products",
            "product-service",
            methods=[HTTPMethod.GET],
            name="products-list",
            cache_ttl=300  # 5 min cache
        )
        
        gateway.add_route(
            "/api/v1/products/{id}",
            "product-service",
            methods=[HTTPMethod.GET],
            name="products-detail",
            cache_ttl=300
        )
        
        print("  ✓ /api/v1/products (list, detail)")
        
        # Consumers
        print("\n👤 Adding Consumers...")
        
        consumer1 = gateway.add_consumer("mobile-app", rate_limit=1000)
        print(f"  ✓ {consumer1.name}: {consumer1.api_key[:16]}...")
        
        consumer2 = gateway.add_consumer("web-frontend", rate_limit=2000)
        print(f"  ✓ {consumer2.name}: {consumer2.api_key[:16]}...")
        
        consumer3 = gateway.add_consumer("partner-api", rate_limit=500)
        print(f"  ✓ {consumer3.name}: {consumer3.api_key[:16]}...")
        
        # Process requests
        print("\n📨 Processing Requests...")
        
        test_requests = [
            # Users API (with auth)
            Request(
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                method=HTTPMethod.GET,
                path="/api/v1/users",
                headers={"X-API-Key": consumer1.api_key},
                client_ip="192.168.1.100"
            ),
            Request(
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                method=HTTPMethod.GET,
                path="/api/v1/users/123",
                headers={"X-API-Key": consumer1.api_key},
                client_ip="192.168.1.100"
            ),
            # Products API (cached)
            Request(
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                method=HTTPMethod.GET,
                path="/api/v1/products",
                client_ip="192.168.1.101"
            ),
            Request(
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                method=HTTPMethod.GET,
                path="/api/v1/products",  # Should hit cache
                client_ip="192.168.1.102"
            ),
            # Orders API (circuit breaker)
            Request(
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                method=HTTPMethod.GET,
                path="/api/v1/orders",
                client_ip="192.168.1.103"
            ),
            # Not found
            Request(
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                method=HTTPMethod.GET,
                path="/api/v1/unknown",
                client_ip="192.168.1.104"
            ),
            # Unauthorized
            Request(
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                method=HTTPMethod.GET,
                path="/api/v1/users",
                client_ip="192.168.1.105"
            )
        ]
        
        print("\n  Request Results:")
        for req in test_requests:
            response = await gateway.handle_request(req)
            
            status_icon = "✅" if response.status_code < 400 else "❌"
            cache_status = response.headers.get("X-Cache", "-")
            
            print(f"    {status_icon} {req.method.value} {req.path}")
            print(f"       Status: {response.status_code}, Latency: {response.latency_ms:.1f}ms, Cache: {cache_status}")
            
        # Bulk requests
        print("\n  Bulk Request Processing...")
        
        for i in range(50):
            req = Request(
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                method=HTTPMethod.GET,
                path=random.choice(["/api/v1/products", "/api/v1/orders", "/api/v1/products/42"]),
                client_ip=f"192.168.1.{random.randint(1, 254)}"
            )
            await gateway.handle_request(req)
            
        print(f"    Processed 50 additional requests")
        
        # Rate limiting demo
        print("\n⏱ Rate Limiting Demo...")
        
        rate_limited_count = 0
        for i in range(10):
            req = Request(
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                method=HTTPMethod.GET,
                path="/api/v1/users",
                headers={"X-API-Key": consumer3.api_key},  # Low rate limit
                client_ip="192.168.100.1"  # Same IP
            )
            response = await gateway.handle_request(req)
            if response.status_code == 429:
                rate_limited_count += 1
                
        print(f"  Rate limited: {rate_limited_count}/10 requests")
        
        # Circuit breaker demo
        print("\n🔌 Circuit Breaker Status:")
        
        for upstream_name, upstream in gateway.upstreams.items():
            state = gateway.circuit_breaker.get_state(upstream_name)
            print(f"  {upstream_name}: {state.state.value}")
            print(f"    Failures: {state.failure_count}")
            
        # Cache statistics
        print("\n📦 Cache Status:")
        
        print(f"  Entries: {len(gateway.cache.cache)}")
        for key, entry in list(gateway.cache.cache.items())[:3]:
            print(f"    • {key[:40]}...")
            print(f"      Hits: {entry.hits}, Expires: {entry.expires_at.strftime('%H:%M:%S')}")
            
        # Statistics
        print("\n📈 Gateway Statistics:")
        
        stats = gateway.get_statistics()
        
        print(f"\n  Routes: {stats['routes']}")
        print(f"  Upstreams: {stats['upstreams']}")
        print(f"  Consumers: {stats['consumers']}")
        print(f"\n  Total Requests: {stats['total_requests']}")
        print(f"  Successful: {stats['successful_requests']}")
        print(f"  Failed: {stats['failed_requests']}")
        print(f"  Rate Limited: {stats['rate_limited']}")
        print(f"  Circuit Broken: {stats['circuit_broken']}")
        print(f"\n  Avg Latency: {stats['avg_latency_ms']}ms")
        print(f"  Cache Hit Rate: {stats['cache_hit_rate']}%")
        print(f"  Cache Entries: {stats['cache_entries']}")
        
        # Dashboard
        print("\n📋 API Gateway Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │                 API Gateway Overview                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Routes:         {stats['routes']:>6}                                │")
        print(f"  │ Upstreams:      {stats['upstreams']:>6}                                │")
        print(f"  │ Consumers:      {stats['consumers']:>6}                                │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Requests: {stats['total_requests']:>6}                                │")
        print(f"  │ Successful:     {stats['successful_requests']:>6}                                │")
        print(f"  │ Failed:         {stats['failed_requests']:>6}                                │")
        print(f"  │ Rate Limited:   {stats['rate_limited']:>6}                                │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Avg Latency:    {stats['avg_latency_ms']:>6}ms                             │")
        print(f"  │ Cache Hit Rate: {stats['cache_hit_rate']:>6}%                              │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("API Gateway Platform initialized!")
    print("=" * 60)
