#!/usr/bin/env python3
"""
Server Init - Iteration 147: API Gateway Platform
Платформа API Gateway

Функционал:
- Request Routing - маршрутизация запросов
- Rate Limiting - ограничение скорости
- Authentication - аутентификация
- Load Balancing - балансировка нагрузки
- Request/Response Transformation - трансформация
- Caching - кэширование
- Circuit Breaker - предохранитель
- API Versioning - версионирование API
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid
import random
import hashlib
import time


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
    MTLS = "mtls"


class LoadBalanceStrategy(Enum):
    """Стратегия балансировки"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"
    WEIGHTED = "weighted"
    IP_HASH = "ip_hash"


class CircuitState(Enum):
    """Состояние предохранителя"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CacheStrategy(Enum):
    """Стратегия кэширования"""
    NO_CACHE = "no_cache"
    CACHE_FIRST = "cache_first"
    NETWORK_FIRST = "network_first"
    STALE_WHILE_REVALIDATE = "stale_while_revalidate"


@dataclass
class Route:
    """Маршрут"""
    route_id: str
    path: str = ""
    
    # Methods
    methods: List[HttpMethod] = field(default_factory=list)
    
    # Backend
    upstream_url: str = ""
    upstream_timeout_ms: int = 30000
    
    # Rewrite
    strip_prefix: bool = False
    path_rewrite: str = ""
    
    # Auth
    auth_type: AuthType = AuthType.NONE
    auth_config: Dict = field(default_factory=dict)
    
    # Rate limiting
    rate_limit_enabled: bool = False
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60
    
    # Caching
    cache_enabled: bool = False
    cache_ttl_seconds: int = 300
    cache_strategy: CacheStrategy = CacheStrategy.NO_CACHE
    
    # Status
    enabled: bool = True
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class Upstream:
    """Upstream сервер"""
    upstream_id: str
    name: str = ""
    
    # Targets
    targets: List[Dict] = field(default_factory=list)  # {host, port, weight}
    
    # Health check
    health_check_enabled: bool = True
    health_check_path: str = "/health"
    health_check_interval_seconds: int = 10
    
    # Load balancing
    load_balance_strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN
    
    # Circuit breaker
    circuit_breaker_enabled: bool = True
    failure_threshold: int = 5
    recovery_timeout_seconds: int = 30
    
    # Connection
    max_connections: int = 100
    connection_timeout_ms: int = 5000


@dataclass
class RateLimitRule:
    """Правило ограничения скорости"""
    rule_id: str
    name: str = ""
    
    # Scope
    scope: str = "global"  # global, route, consumer, ip
    
    # Limits
    requests_per_second: int = 10
    requests_per_minute: int = 100
    requests_per_hour: int = 1000
    
    # Burst
    burst_size: int = 20
    
    # Response
    retry_after_seconds: int = 60
    
    # Status
    enabled: bool = True


@dataclass
class Consumer:
    """Потребитель API"""
    consumer_id: str
    name: str = ""
    
    # Credentials
    api_key: str = ""
    jwt_secret: str = ""
    
    # Rate limit override
    custom_rate_limit: Optional[int] = None
    
    # Permissions
    allowed_routes: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    enabled: bool = True


@dataclass
class Request:
    """Запрос"""
    request_id: str
    
    # HTTP
    method: HttpMethod = HttpMethod.GET
    path: str = ""
    headers: Dict = field(default_factory=dict)
    query_params: Dict = field(default_factory=dict)
    body: Any = None
    
    # Client
    client_ip: str = ""
    consumer_id: str = ""
    
    # Timing
    received_at: datetime = field(default_factory=datetime.now)


@dataclass
class Response:
    """Ответ"""
    request_id: str
    
    # HTTP
    status_code: int = 200
    headers: Dict = field(default_factory=dict)
    body: Any = None
    
    # Timing
    latency_ms: float = 0.0
    
    # Source
    from_cache: bool = False
    upstream_used: str = ""


@dataclass
class CircuitBreaker:
    """Предохранитель"""
    breaker_id: str
    upstream_id: str = ""
    
    # State
    state: CircuitState = CircuitState.CLOSED
    
    # Counters
    failure_count: int = 0
    success_count: int = 0
    
    # Thresholds
    failure_threshold: int = 5
    success_threshold: int = 3
    
    # Timing
    last_failure: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    recovery_timeout_seconds: int = 30


class RouteManager:
    """Менеджер маршрутов"""
    
    def __init__(self):
        self.routes: Dict[str, Route] = {}
        
    def add_route(self, path: str, methods: List[HttpMethod],
                   upstream_url: str, **kwargs) -> Route:
        """Добавление маршрута"""
        route = Route(
            route_id=f"route_{uuid.uuid4().hex[:8]}",
            path=path,
            methods=methods,
            upstream_url=upstream_url,
            **kwargs
        )
        self.routes[route.route_id] = route
        return route
        
    def match_route(self, path: str, method: HttpMethod) -> Optional[Route]:
        """Поиск маршрута"""
        for route in self.routes.values():
            if not route.enabled:
                continue
                
            # Simple path matching
            if self._path_matches(route.path, path) and method in route.methods:
                return route
                
        return None
        
    def _path_matches(self, pattern: str, path: str) -> bool:
        """Проверка соответствия пути"""
        if pattern.endswith("/*"):
            return path.startswith(pattern[:-2])
        elif pattern.endswith("/**"):
            return path.startswith(pattern[:-3])
        else:
            return pattern == path
            
    def get_routes_by_tag(self, tag: str) -> List[Route]:
        """Получение маршрутов по тегу"""
        return [r for r in self.routes.values() if tag in r.tags]


class UpstreamManager:
    """Менеджер upstream"""
    
    def __init__(self):
        self.upstreams: Dict[str, Upstream] = {}
        self.target_index: Dict[str, int] = {}  # For round-robin
        self.target_health: Dict[str, Dict[str, bool]] = {}
        
    def add_upstream(self, name: str, targets: List[Dict],
                      **kwargs) -> Upstream:
        """Добавление upstream"""
        upstream = Upstream(
            upstream_id=f"ups_{uuid.uuid4().hex[:8]}",
            name=name,
            targets=targets,
            **kwargs
        )
        self.upstreams[upstream.upstream_id] = upstream
        self.target_index[upstream.upstream_id] = 0
        self.target_health[upstream.upstream_id] = {
            f"{t['host']}:{t['port']}": True for t in targets
        }
        return upstream
        
    def get_target(self, upstream_id: str) -> Optional[Dict]:
        """Получение target"""
        upstream = self.upstreams.get(upstream_id)
        if not upstream or not upstream.targets:
            return None
            
        healthy_targets = [
            t for t in upstream.targets
            if self.target_health[upstream_id].get(f"{t['host']}:{t['port']}", False)
        ]
        
        if not healthy_targets:
            healthy_targets = upstream.targets  # Fallback
            
        if upstream.load_balance_strategy == LoadBalanceStrategy.ROUND_ROBIN:
            idx = self.target_index[upstream_id]
            target = healthy_targets[idx % len(healthy_targets)]
            self.target_index[upstream_id] = idx + 1
            return target
            
        elif upstream.load_balance_strategy == LoadBalanceStrategy.RANDOM:
            return random.choice(healthy_targets)
            
        elif upstream.load_balance_strategy == LoadBalanceStrategy.WEIGHTED:
            weights = [t.get("weight", 1) for t in healthy_targets]
            return random.choices(healthy_targets, weights=weights)[0]
            
        return healthy_targets[0]
        
    def mark_unhealthy(self, upstream_id: str, host: str, port: int):
        """Пометка target как нездоровый"""
        key = f"{host}:{port}"
        if upstream_id in self.target_health:
            self.target_health[upstream_id][key] = False
            
    def mark_healthy(self, upstream_id: str, host: str, port: int):
        """Пометка target как здоровый"""
        key = f"{host}:{port}"
        if upstream_id in self.target_health:
            self.target_health[upstream_id][key] = True


class RateLimiter:
    """Ограничитель скорости"""
    
    def __init__(self):
        self.rules: Dict[str, RateLimitRule] = {}
        self.counters: Dict[str, Dict] = {}  # {key: {count, window_start}}
        
    def add_rule(self, name: str, requests_per_minute: int,
                  scope: str = "global", **kwargs) -> RateLimitRule:
        """Добавление правила"""
        rule = RateLimitRule(
            rule_id=f"rl_{uuid.uuid4().hex[:8]}",
            name=name,
            requests_per_minute=requests_per_minute,
            scope=scope,
            **kwargs
        )
        self.rules[rule.rule_id] = rule
        return rule
        
    def check_limit(self, rule_id: str, key: str) -> tuple[bool, int]:
        """Проверка лимита"""
        rule = self.rules.get(rule_id)
        if not rule or not rule.enabled:
            return True, 0
            
        now = time.time()
        counter_key = f"{rule_id}:{key}"
        
        if counter_key not in self.counters:
            self.counters[counter_key] = {"count": 0, "window_start": now}
            
        counter = self.counters[counter_key]
        
        # Reset window if expired
        if now - counter["window_start"] > 60:
            counter["count"] = 0
            counter["window_start"] = now
            
        # Check limit
        if counter["count"] >= rule.requests_per_minute:
            remaining = int(60 - (now - counter["window_start"]))
            return False, remaining
            
        counter["count"] += 1
        return True, 0
        
    def get_usage(self, rule_id: str, key: str) -> Dict:
        """Получение использования"""
        counter_key = f"{rule_id}:{key}"
        counter = self.counters.get(counter_key, {"count": 0})
        rule = self.rules.get(rule_id)
        
        return {
            "current": counter.get("count", 0),
            "limit": rule.requests_per_minute if rule else 0,
            "remaining": max(0, (rule.requests_per_minute if rule else 0) - counter.get("count", 0))
        }


class AuthManager:
    """Менеджер аутентификации"""
    
    def __init__(self):
        self.consumers: Dict[str, Consumer] = {}
        self.api_keys: Dict[str, str] = {}  # key -> consumer_id
        
    def create_consumer(self, name: str, **kwargs) -> Consumer:
        """Создание потребителя"""
        consumer = Consumer(
            consumer_id=f"cons_{uuid.uuid4().hex[:8]}",
            name=name,
            api_key=f"ak_{uuid.uuid4().hex}",
            jwt_secret=uuid.uuid4().hex,
            **kwargs
        )
        self.consumers[consumer.consumer_id] = consumer
        self.api_keys[consumer.api_key] = consumer.consumer_id
        return consumer
        
    def authenticate(self, auth_type: AuthType, credentials: Dict) -> Optional[Consumer]:
        """Аутентификация"""
        if auth_type == AuthType.NONE:
            return None
            
        if auth_type == AuthType.API_KEY:
            api_key = credentials.get("api_key", "")
            consumer_id = self.api_keys.get(api_key)
            if consumer_id:
                consumer = self.consumers.get(consumer_id)
                if consumer and consumer.enabled:
                    return consumer
                    
        elif auth_type == AuthType.JWT:
            # Simplified JWT validation
            token = credentials.get("token", "")
            # In real implementation, decode and verify JWT
            return None
            
        return None
        
    def check_permission(self, consumer: Consumer, route_id: str) -> bool:
        """Проверка разрешения"""
        if not consumer.allowed_routes:  # Empty means all allowed
            return True
        return route_id in consumer.allowed_routes


class CacheManager:
    """Менеджер кэша"""
    
    def __init__(self):
        self.cache: Dict[str, Dict] = {}
        
    def get(self, key: str) -> Optional[Dict]:
        """Получение из кэша"""
        entry = self.cache.get(key)
        if not entry:
            return None
            
        if datetime.now() > entry["expires_at"]:
            del self.cache[key]
            return None
            
        return entry["data"]
        
    def set(self, key: str, data: Dict, ttl_seconds: int = 300):
        """Сохранение в кэш"""
        self.cache[key] = {
            "data": data,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(seconds=ttl_seconds)
        }
        
    def invalidate(self, key: str):
        """Инвалидация"""
        if key in self.cache:
            del self.cache[key]
            
    def clear(self):
        """Очистка кэша"""
        self.cache.clear()
        
    def generate_key(self, request: Request) -> str:
        """Генерация ключа кэша"""
        key_parts = [request.method.value, request.path]
        if request.query_params:
            key_parts.append(json.dumps(request.query_params, sort_keys=True))
        return hashlib.md5(":".join(key_parts).encode()).hexdigest()


class CircuitBreakerManager:
    """Менеджер предохранителей"""
    
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
        
    def get_or_create(self, upstream_id: str, **kwargs) -> CircuitBreaker:
        """Получение или создание"""
        if upstream_id not in self.breakers:
            self.breakers[upstream_id] = CircuitBreaker(
                breaker_id=f"cb_{uuid.uuid4().hex[:8]}",
                upstream_id=upstream_id,
                **kwargs
            )
        return self.breakers[upstream_id]
        
    def can_execute(self, upstream_id: str) -> bool:
        """Проверка возможности выполнения"""
        breaker = self.breakers.get(upstream_id)
        if not breaker:
            return True
            
        if breaker.state == CircuitState.CLOSED:
            return True
            
        if breaker.state == CircuitState.OPEN:
            # Check if recovery timeout passed
            if breaker.opened_at:
                elapsed = (datetime.now() - breaker.opened_at).total_seconds()
                if elapsed >= breaker.recovery_timeout_seconds:
                    breaker.state = CircuitState.HALF_OPEN
                    return True
            return False
            
        # Half-open: allow limited requests
        return True
        
    def record_success(self, upstream_id: str):
        """Запись успеха"""
        breaker = self.breakers.get(upstream_id)
        if not breaker:
            return
            
        breaker.success_count += 1
        
        if breaker.state == CircuitState.HALF_OPEN:
            if breaker.success_count >= breaker.success_threshold:
                breaker.state = CircuitState.CLOSED
                breaker.failure_count = 0
                breaker.success_count = 0
                
    def record_failure(self, upstream_id: str):
        """Запись ошибки"""
        breaker = self.breakers.get(upstream_id)
        if not breaker:
            return
            
        breaker.failure_count += 1
        breaker.last_failure = datetime.now()
        
        if breaker.state == CircuitState.CLOSED:
            if breaker.failure_count >= breaker.failure_threshold:
                breaker.state = CircuitState.OPEN
                breaker.opened_at = datetime.now()
                
        elif breaker.state == CircuitState.HALF_OPEN:
            breaker.state = CircuitState.OPEN
            breaker.opened_at = datetime.now()


class RequestProcessor:
    """Обработчик запросов"""
    
    def __init__(self, route_manager: RouteManager, upstream_manager: UpstreamManager,
                  rate_limiter: RateLimiter, auth_manager: AuthManager,
                  cache_manager: CacheManager, circuit_breaker_manager: CircuitBreakerManager):
        self.route_manager = route_manager
        self.upstream_manager = upstream_manager
        self.rate_limiter = rate_limiter
        self.auth_manager = auth_manager
        self.cache_manager = cache_manager
        self.circuit_breaker = circuit_breaker_manager
        self.metrics: Dict = {"requests": 0, "errors": 0, "cache_hits": 0}
        
    async def process(self, request: Request) -> Response:
        """Обработка запроса"""
        start_time = time.time()
        self.metrics["requests"] += 1
        
        # Find route
        route = self.route_manager.match_route(request.path, request.method)
        if not route:
            return Response(
                request_id=request.request_id,
                status_code=404,
                body={"error": "Route not found"}
            )
            
        # Authentication
        if route.auth_type != AuthType.NONE:
            consumer = self.auth_manager.authenticate(
                route.auth_type,
                {"api_key": request.headers.get("X-API-Key", "")}
            )
            if not consumer:
                return Response(
                    request_id=request.request_id,
                    status_code=401,
                    body={"error": "Unauthorized"}
                )
            request.consumer_id = consumer.consumer_id
            
        # Rate limiting
        if route.rate_limit_enabled:
            key = request.consumer_id or request.client_ip
            allowed, retry_after = self.rate_limiter.check_limit(route.route_id, key)
            if not allowed:
                return Response(
                    request_id=request.request_id,
                    status_code=429,
                    headers={"Retry-After": str(retry_after)},
                    body={"error": "Rate limit exceeded"}
                )
                
        # Check cache
        if route.cache_enabled and request.method == HttpMethod.GET:
            cache_key = self.cache_manager.generate_key(request)
            cached = self.cache_manager.get(cache_key)
            if cached:
                self.metrics["cache_hits"] += 1
                return Response(
                    request_id=request.request_id,
                    status_code=200,
                    body=cached,
                    from_cache=True,
                    latency_ms=(time.time() - start_time) * 1000
                )
                
        # Circuit breaker check
        if not self.circuit_breaker.can_execute(route.upstream_url):
            self.metrics["errors"] += 1
            return Response(
                request_id=request.request_id,
                status_code=503,
                body={"error": "Service unavailable (circuit open)"}
            )
            
        # Forward to upstream (simulated)
        try:
            await asyncio.sleep(random.uniform(0.01, 0.1))  # Simulate latency
            
            response_body = {
                "message": "Success",
                "path": request.path,
                "method": request.method.value
            }
            
            # Cache response
            if route.cache_enabled and request.method == HttpMethod.GET:
                cache_key = self.cache_manager.generate_key(request)
                self.cache_manager.set(cache_key, response_body, route.cache_ttl_seconds)
                
            self.circuit_breaker.record_success(route.upstream_url)
            
            return Response(
                request_id=request.request_id,
                status_code=200,
                body=response_body,
                upstream_used=route.upstream_url,
                latency_ms=(time.time() - start_time) * 1000
            )
            
        except Exception as e:
            self.metrics["errors"] += 1
            self.circuit_breaker.record_failure(route.upstream_url)
            return Response(
                request_id=request.request_id,
                status_code=502,
                body={"error": str(e)}
            )


class APIGatewayPlatform:
    """Платформа API Gateway"""
    
    def __init__(self):
        self.route_manager = RouteManager()
        self.upstream_manager = UpstreamManager()
        self.rate_limiter = RateLimiter()
        self.auth_manager = AuthManager()
        self.cache_manager = CacheManager()
        self.circuit_breaker_manager = CircuitBreakerManager()
        self.processor = RequestProcessor(
            self.route_manager, self.upstream_manager,
            self.rate_limiter, self.auth_manager,
            self.cache_manager, self.circuit_breaker_manager
        )
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        return {
            "routes": len(self.route_manager.routes),
            "upstreams": len(self.upstream_manager.upstreams),
            "consumers": len(self.auth_manager.consumers),
            "rate_limit_rules": len(self.rate_limiter.rules),
            "cache_entries": len(self.cache_manager.cache),
            "circuit_breakers": len(self.circuit_breaker_manager.breakers),
            "total_requests": self.processor.metrics["requests"],
            "errors": self.processor.metrics["errors"],
            "cache_hits": self.processor.metrics["cache_hits"]
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 147: API Gateway Platform")
    print("=" * 60)
    
    async def demo():
        gateway = APIGatewayPlatform()
        print("✓ API Gateway Platform created")
        
        # Add upstreams
        print("\n🔗 Configuring Upstreams...")
        
        upstreams_data = [
            ("user-service", [
                {"host": "user-1.internal", "port": 8080, "weight": 3},
                {"host": "user-2.internal", "port": 8080, "weight": 2},
                {"host": "user-3.internal", "port": 8080, "weight": 1}
            ]),
            ("order-service", [
                {"host": "order-1.internal", "port": 8081, "weight": 1},
                {"host": "order-2.internal", "port": 8081, "weight": 1}
            ]),
            ("product-service", [
                {"host": "product-1.internal", "port": 8082, "weight": 1}
            ])
        ]
        
        for name, targets in upstreams_data:
            upstream = gateway.upstream_manager.add_upstream(
                name, targets,
                load_balance_strategy=LoadBalanceStrategy.WEIGHTED
            )
            print(f"  ✓ {name}: {len(targets)} targets")
            
        # Add routes
        print("\n🛣️ Configuring Routes...")
        
        routes_data = [
            ("/api/v1/users/*", [HttpMethod.GET, HttpMethod.POST], "http://user-service", True, True, 60),
            ("/api/v1/orders/*", [HttpMethod.GET, HttpMethod.POST, HttpMethod.PUT], "http://order-service", True, False, 0),
            ("/api/v1/products/*", [HttpMethod.GET], "http://product-service", False, True, 300),
            ("/api/v1/auth/login", [HttpMethod.POST], "http://user-service", False, False, 0),
            ("/health", [HttpMethod.GET], "http://localhost", False, False, 0)
        ]
        
        for path, methods, upstream, auth, cache, ttl in routes_data:
            route = gateway.route_manager.add_route(
                path, methods, upstream,
                auth_type=AuthType.API_KEY if auth else AuthType.NONE,
                cache_enabled=cache,
                cache_ttl_seconds=ttl,
                rate_limit_enabled=True,
                rate_limit_requests=100
            )
            methods_str = ", ".join(m.value for m in methods)
            auth_str = "🔒" if auth else "🔓"
            cache_str = f"💾{ttl}s" if cache else ""
            print(f"  {auth_str} {path}: [{methods_str}] {cache_str}")
            
        # Add rate limit rules
        print("\n⏱️ Configuring Rate Limiting...")
        
        rate_rules = [
            ("global-limit", 1000, "global"),
            ("api-consumer-limit", 100, "consumer"),
            ("ip-limit", 60, "ip")
        ]
        
        for name, rpm, scope in rate_rules:
            rule = gateway.rate_limiter.add_rule(name, rpm, scope)
            print(f"  ✓ {name}: {rpm} req/min ({scope})")
            
        # Create consumers
        print("\n👤 Creating API Consumers...")
        
        consumers_data = [
            ("mobile-app", None),
            ("web-frontend", None),
            ("partner-api", 500),  # Custom rate limit
            ("internal-service", None)
        ]
        
        consumers = []
        for name, custom_limit in consumers_data:
            consumer = gateway.auth_manager.create_consumer(
                name, custom_rate_limit=custom_limit
            )
            consumers.append(consumer)
            limit_str = f" (custom: {custom_limit}/min)" if custom_limit else ""
            print(f"  ✓ {name}: {consumer.api_key[:16]}...{limit_str}")
            
        # Process requests
        print("\n📨 Processing Requests...")
        
        test_requests = [
            (HttpMethod.GET, "/api/v1/users/123", consumers[0].api_key),
            (HttpMethod.GET, "/api/v1/products/456", ""),
            (HttpMethod.POST, "/api/v1/orders/new", consumers[1].api_key),
            (HttpMethod.GET, "/api/v1/users/789", consumers[0].api_key),  # Should hit cache
            (HttpMethod.GET, "/health", ""),
            (HttpMethod.GET, "/api/v1/unknown", ""),
            (HttpMethod.POST, "/api/v1/users/new", ""),  # No API key
        ]
        
        for method, path, api_key in test_requests:
            request = Request(
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                method=method,
                path=path,
                headers={"X-API-Key": api_key} if api_key else {},
                client_ip="192.168.1.100"
            )
            
            response = await gateway.processor.process(request)
            
            status_icon = "✓" if response.status_code < 400 else "✗"
            cache_str = " (cached)" if response.from_cache else ""
            print(f"  {status_icon} {method.value} {path}: {response.status_code} ({response.latency_ms:.1f}ms){cache_str}")
            
        # Test rate limiting
        print("\n⚡ Testing Rate Limiting...")
        
        route = list(gateway.route_manager.routes.values())[0]
        rule = gateway.rate_limiter.add_rule("test-limit", 5, "ip")
        
        for i in range(8):
            allowed, retry_after = gateway.rate_limiter.check_limit(rule.rule_id, "test-ip")
            status = "✓" if allowed else f"✗ (retry after {retry_after}s)"
            print(f"  Request {i+1}: {status}")
            
        # Circuit breaker simulation
        print("\n🔌 Circuit Breaker Status:")
        
        for upstream_id in gateway.upstream_manager.upstreams:
            breaker = gateway.circuit_breaker_manager.get_or_create(upstream_id)
            
            # Simulate some failures
            for _ in range(3):
                gateway.circuit_breaker_manager.record_failure(upstream_id)
                
            state_icon = {"closed": "🟢", "open": "🔴", "half_open": "🟡"}
            print(f"  {gateway.upstream_manager.upstreams[upstream_id].name}: {state_icon[breaker.state.value]} {breaker.state.value}")
            print(f"      Failures: {breaker.failure_count}, Threshold: {breaker.failure_threshold}")
            
        # Load balancing demo
        print("\n⚖️ Load Balancing Distribution:")
        
        upstream = list(gateway.upstream_manager.upstreams.values())[0]
        target_counts = {}
        
        for _ in range(100):
            target = gateway.upstream_manager.get_target(upstream.upstream_id)
            key = f"{target['host']}:{target['port']}"
            target_counts[key] = target_counts.get(key, 0) + 1
            
        for target, count in sorted(target_counts.items()):
            bar = "█" * (count // 5)
            print(f"  {target}: {count}% {bar}")
            
        # Statistics
        print("\n📊 Gateway Statistics:")
        
        stats = gateway.get_statistics()
        
        print(f"\n  Routes: {stats['routes']}")
        print(f"  Upstreams: {stats['upstreams']}")
        print(f"  Consumers: {stats['consumers']}")
        print(f"  Rate Limit Rules: {stats['rate_limit_rules']}")
        print(f"  Cache Entries: {stats['cache_entries']}")
        print(f"  Circuit Breakers: {stats['circuit_breakers']}")
        print(f"  Total Requests: {stats['total_requests']}")
        print(f"  Errors: {stats['errors']}")
        print(f"  Cache Hits: {stats['cache_hits']}")
        
        # Dashboard
        print("\n📋 API Gateway Dashboard:")
        print("  ┌────────────────────────────────────────────────────────────┐")
        print("  │                  API Gateway Overview                      │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Routes:              {stats['routes']:>10}                    │")
        print(f"  │ Upstreams:           {stats['upstreams']:>10}                    │")
        print(f"  │ Consumers:           {stats['consumers']:>10}                    │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Requests:      {stats['total_requests']:>10}                    │")
        print(f"  │ Errors:              {stats['errors']:>10}                    │")
        print(f"  │ Cache Hits:          {stats['cache_hits']:>10}                    │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Rate Limit Rules:    {stats['rate_limit_rules']:>10}                    │")
        print(f"  │ Circuit Breakers:    {stats['circuit_breakers']:>10}                    │")
        print("  └────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("API Gateway Platform initialized!")
    print("=" * 60)
