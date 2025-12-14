#!/usr/bin/env python3
"""
Server Init - Iteration 244: Platform Gateway
Платформа API шлюза

Функционал:
- Request Routing - маршрутизация запросов
- Rate Limiting - ограничение скорости
- Authentication - аутентификация
- Load Balancing - балансировка нагрузки
- Request/Response Transformation - трансформация
- Caching - кэширование
- Circuit Breaker - прерыватель цепи
- API Versioning - версионирование API
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import json


class RouteMethod(Enum):
    """HTTP метод"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    ANY = "*"


class LoadBalanceAlgorithm(Enum):
    """Алгоритм балансировки"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"
    WEIGHTED = "weighted"
    IP_HASH = "ip_hash"


class CircuitState(Enum):
    """Состояние прерывателя"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class AuthType(Enum):
    """Тип аутентификации"""
    NONE = "none"
    API_KEY = "api_key"
    JWT = "jwt"
    OAUTH2 = "oauth2"
    BASIC = "basic"


class RateLimitType(Enum):
    """Тип лимита"""
    REQUESTS_PER_SECOND = "rps"
    REQUESTS_PER_MINUTE = "rpm"
    REQUESTS_PER_HOUR = "rph"
    CONCURRENT = "concurrent"


@dataclass
class Backend:
    """Бэкенд сервис"""
    backend_id: str
    name: str = ""
    
    # Endpoint
    host: str = ""
    port: int = 80
    protocol: str = "http"
    
    # Health
    is_healthy: bool = True
    last_health_check: datetime = field(default_factory=datetime.now)
    
    # Load
    active_connections: int = 0
    weight: int = 1
    
    # Stats
    total_requests: int = 0
    failed_requests: int = 0


@dataclass
class Route:
    """Маршрут"""
    route_id: str
    name: str = ""
    
    # Match
    path_pattern: str = ""
    methods: List[RouteMethod] = field(default_factory=list)
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Target
    backends: List[str] = field(default_factory=list)
    load_balance: LoadBalanceAlgorithm = LoadBalanceAlgorithm.ROUND_ROBIN
    
    # Transformations
    path_rewrite: str = ""
    add_headers: Dict[str, str] = field(default_factory=dict)
    remove_headers: List[str] = field(default_factory=list)
    
    # Options
    timeout_ms: int = 30000
    retry_count: int = 3
    
    # Status
    is_active: bool = True
    priority: int = 0
    
    # Version
    api_version: str = ""


@dataclass
class RateLimitRule:
    """Правило лимита"""
    rule_id: str
    name: str = ""
    
    # Limit
    limit_type: RateLimitType = RateLimitType.REQUESTS_PER_MINUTE
    limit_value: int = 100
    
    # Scope
    scope: str = "global"  # global, ip, user, api_key
    
    # Match
    path_pattern: str = "*"
    
    # Burst
    burst_size: int = 10
    
    # Response
    rejection_code: int = 429
    rejection_message: str = "Rate limit exceeded"


@dataclass
class RateLimitState:
    """Состояние лимита"""
    key: str
    rule_id: str = ""
    
    # Counters
    request_count: int = 0
    window_start: datetime = field(default_factory=datetime.now)
    
    # Concurrent
    active_requests: int = 0


@dataclass
class CircuitBreaker:
    """Прерыватель цепи"""
    breaker_id: str
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
    
    # Time
    last_failure: Optional[datetime] = None
    opened_at: Optional[datetime] = None


@dataclass
class CacheEntry:
    """Запись кэша"""
    cache_key: str
    
    # Content
    response_body: str = ""
    response_headers: Dict[str, str] = field(default_factory=dict)
    status_code: int = 200
    
    # TTL
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=datetime.now)
    
    # Stats
    hit_count: int = 0


@dataclass
class Request:
    """Входящий запрос"""
    request_id: str
    
    # HTTP
    method: RouteMethod = RouteMethod.GET
    path: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    body: str = ""
    
    # Client
    client_ip: str = ""
    user_agent: str = ""
    
    # Auth
    api_key: str = ""
    auth_token: str = ""
    
    # Time
    received_at: datetime = field(default_factory=datetime.now)


@dataclass
class Response:
    """Исходящий ответ"""
    request_id: str
    
    # HTTP
    status_code: int = 200
    headers: Dict[str, str] = field(default_factory=dict)
    body: str = ""
    
    # Meta
    backend_id: str = ""
    cached: bool = False
    
    # Time
    latency_ms: float = 0


@dataclass
class GatewayStats:
    """Статистика шлюза"""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Requests
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # Rate limiting
    rate_limited: int = 0
    
    # Cache
    cache_hits: int = 0
    cache_misses: int = 0
    
    # Circuit breaker
    circuit_breaks: int = 0
    
    # Latency
    avg_latency_ms: float = 0
    p95_latency_ms: float = 0
    p99_latency_ms: float = 0


class PlatformGateway:
    """API шлюз платформы"""
    
    def __init__(self):
        self.backends: Dict[str, Backend] = {}
        self.routes: Dict[str, Route] = {}
        self.rate_limits: Dict[str, RateLimitRule] = {}
        self.rate_limit_states: Dict[str, RateLimitState] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.cache: Dict[str, CacheEntry] = {}
        
        # Round robin counters
        self._rr_counters: Dict[str, int] = {}
        
        # Stats
        self.stats = GatewayStats()
        self._latencies: List[float] = []
        
    def register_backend(self, name: str, host: str, port: int = 80,
                        protocol: str = "http", weight: int = 1) -> Backend:
        """Регистрация бэкенда"""
        backend = Backend(
            backend_id=f"be_{uuid.uuid4().hex[:8]}",
            name=name,
            host=host,
            port=port,
            protocol=protocol,
            weight=weight
        )
        
        self.backends[backend.backend_id] = backend
        
        # Create circuit breaker
        breaker = CircuitBreaker(
            breaker_id=f"cb_{backend.backend_id}",
            backend_id=backend.backend_id
        )
        self.circuit_breakers[backend.backend_id] = breaker
        
        return backend
        
    def create_route(self, name: str, path_pattern: str,
                    backends: List[str],
                    methods: List[RouteMethod] = None,
                    load_balance: LoadBalanceAlgorithm = LoadBalanceAlgorithm.ROUND_ROBIN,
                    api_version: str = "") -> Route:
        """Создание маршрута"""
        route = Route(
            route_id=f"rt_{uuid.uuid4().hex[:8]}",
            name=name,
            path_pattern=path_pattern,
            methods=methods or [RouteMethod.ANY],
            backends=backends,
            load_balance=load_balance,
            api_version=api_version
        )
        
        self.routes[route.route_id] = route
        return route
        
    def create_rate_limit(self, name: str, limit_value: int,
                         limit_type: RateLimitType = RateLimitType.REQUESTS_PER_MINUTE,
                         scope: str = "global",
                         path_pattern: str = "*") -> RateLimitRule:
        """Создание правила лимита"""
        rule = RateLimitRule(
            rule_id=f"rl_{uuid.uuid4().hex[:8]}",
            name=name,
            limit_type=limit_type,
            limit_value=limit_value,
            scope=scope,
            path_pattern=path_pattern
        )
        
        self.rate_limits[rule.rule_id] = rule
        return rule
        
    def _match_route(self, request: Request) -> Optional[Route]:
        """Поиск маршрута"""
        matched_routes = []
        
        for route in self.routes.values():
            if not route.is_active:
                continue
                
            # Check method
            if RouteMethod.ANY not in route.methods:
                if request.method not in route.methods:
                    continue
                    
            # Check path (simple prefix match)
            if route.path_pattern.endswith("*"):
                prefix = route.path_pattern[:-1]
                if not request.path.startswith(prefix):
                    continue
            elif route.path_pattern != request.path:
                continue
                
            matched_routes.append(route)
            
        if not matched_routes:
            return None
            
        # Return highest priority
        return max(matched_routes, key=lambda r: r.priority)
        
    def _check_rate_limit(self, request: Request) -> Optional[RateLimitRule]:
        """Проверка лимита"""
        for rule in self.rate_limits.values():
            # Check path
            if rule.path_pattern != "*":
                if not request.path.startswith(rule.path_pattern.rstrip("*")):
                    continue
                    
            # Get key
            if rule.scope == "global":
                key = f"global:{rule.rule_id}"
            elif rule.scope == "ip":
                key = f"ip:{request.client_ip}:{rule.rule_id}"
            elif rule.scope == "api_key":
                key = f"key:{request.api_key}:{rule.rule_id}"
            else:
                key = f"global:{rule.rule_id}"
                
            # Get/create state
            if key not in self.rate_limit_states:
                self.rate_limit_states[key] = RateLimitState(
                    key=key, rule_id=rule.rule_id
                )
                
            state = self.rate_limit_states[key]
            
            # Check window
            now = datetime.now()
            
            if rule.limit_type == RateLimitType.REQUESTS_PER_SECOND:
                window = timedelta(seconds=1)
            elif rule.limit_type == RateLimitType.REQUESTS_PER_MINUTE:
                window = timedelta(minutes=1)
            elif rule.limit_type == RateLimitType.REQUESTS_PER_HOUR:
                window = timedelta(hours=1)
            else:
                window = timedelta(minutes=1)
                
            if now - state.window_start > window:
                state.request_count = 0
                state.window_start = now
                
            # Check limit
            if state.request_count >= rule.limit_value:
                return rule
                
            state.request_count += 1
            
        return None
        
    def _select_backend(self, route: Route) -> Optional[Backend]:
        """Выбор бэкенда"""
        healthy_backends = [
            self.backends[bid] for bid in route.backends
            if bid in self.backends 
            and self.backends[bid].is_healthy
            and self._is_circuit_closed(bid)
        ]
        
        if not healthy_backends:
            return None
            
        if route.load_balance == LoadBalanceAlgorithm.ROUND_ROBIN:
            idx = self._rr_counters.get(route.route_id, 0)
            backend = healthy_backends[idx % len(healthy_backends)]
            self._rr_counters[route.route_id] = idx + 1
            return backend
            
        elif route.load_balance == LoadBalanceAlgorithm.RANDOM:
            return random.choice(healthy_backends)
            
        elif route.load_balance == LoadBalanceAlgorithm.LEAST_CONNECTIONS:
            return min(healthy_backends, key=lambda b: b.active_connections)
            
        elif route.load_balance == LoadBalanceAlgorithm.WEIGHTED:
            total_weight = sum(b.weight for b in healthy_backends)
            r = random.randint(1, total_weight)
            cumulative = 0
            for backend in healthy_backends:
                cumulative += backend.weight
                if r <= cumulative:
                    return backend
                    
        return healthy_backends[0]
        
    def _is_circuit_closed(self, backend_id: str) -> bool:
        """Проверка состояния прерывателя"""
        breaker = self.circuit_breakers.get(backend_id)
        if not breaker:
            return True
            
        if breaker.state == CircuitState.CLOSED:
            return True
            
        if breaker.state == CircuitState.OPEN:
            # Check timeout
            if breaker.opened_at:
                elapsed = (datetime.now() - breaker.opened_at).total_seconds()
                if elapsed > breaker.timeout_seconds:
                    breaker.state = CircuitState.HALF_OPEN
                    return True
            return False
            
        return True  # HALF_OPEN allows requests
        
    def _record_success(self, backend_id: str):
        """Запись успеха"""
        breaker = self.circuit_breakers.get(backend_id)
        if not breaker:
            return
            
        if breaker.state == CircuitState.HALF_OPEN:
            breaker.success_count += 1
            if breaker.success_count >= breaker.success_threshold:
                breaker.state = CircuitState.CLOSED
                breaker.failure_count = 0
                breaker.success_count = 0
                
    def _record_failure(self, backend_id: str):
        """Запись ошибки"""
        breaker = self.circuit_breakers.get(backend_id)
        if not breaker:
            return
            
        breaker.failure_count += 1
        breaker.last_failure = datetime.now()
        
        if breaker.state == CircuitState.HALF_OPEN:
            breaker.state = CircuitState.OPEN
            breaker.opened_at = datetime.now()
            self.stats.circuit_breaks += 1
        elif breaker.failure_count >= breaker.failure_threshold:
            breaker.state = CircuitState.OPEN
            breaker.opened_at = datetime.now()
            self.stats.circuit_breaks += 1
            
    def _get_cache_key(self, request: Request) -> str:
        """Ключ кэша"""
        return f"{request.method.value}:{request.path}"
        
    def _check_cache(self, request: Request) -> Optional[CacheEntry]:
        """Проверка кэша"""
        if request.method != RouteMethod.GET:
            return None
            
        key = self._get_cache_key(request)
        entry = self.cache.get(key)
        
        if entry and entry.expires_at > datetime.now():
            entry.hit_count += 1
            return entry
            
        return None
        
    async def handle_request(self, request: Request) -> Response:
        """Обработка запроса"""
        self.stats.total_requests += 1
        start_time = datetime.now()
        
        response = Response(request_id=request.request_id)
        
        # Check rate limit
        violated_rule = self._check_rate_limit(request)
        if violated_rule:
            self.stats.rate_limited += 1
            response.status_code = violated_rule.rejection_code
            response.body = json.dumps({"error": violated_rule.rejection_message})
            return response
            
        # Check cache
        cached = self._check_cache(request)
        if cached:
            self.stats.cache_hits += 1
            response.status_code = cached.status_code
            response.body = cached.response_body
            response.headers = cached.response_headers.copy()
            response.cached = True
            return response
            
        self.stats.cache_misses += 1
        
        # Find route
        route = self._match_route(request)
        if not route:
            response.status_code = 404
            response.body = json.dumps({"error": "Route not found"})
            return response
            
        # Select backend
        backend = self._select_backend(route)
        if not backend:
            response.status_code = 503
            response.body = json.dumps({"error": "No available backend"})
            return response
            
        # Simulate request to backend
        backend.active_connections += 1
        backend.total_requests += 1
        
        try:
            # Simulate latency
            await asyncio.sleep(random.uniform(0.01, 0.1))
            
            # Simulate occasional failures
            if random.random() > 0.95:
                raise Exception("Backend error")
                
            response.status_code = 200
            response.body = json.dumps({
                "message": "Success",
                "backend": backend.name,
                "path": request.path
            })
            response.backend_id = backend.backend_id
            
            self._record_success(backend.backend_id)
            self.stats.successful_requests += 1
            
        except Exception as e:
            backend.failed_requests += 1
            self._record_failure(backend.backend_id)
            
            response.status_code = 500
            response.body = json.dumps({"error": str(e)})
            self.stats.failed_requests += 1
            
        finally:
            backend.active_connections -= 1
            
        # Calculate latency
        latency = (datetime.now() - start_time).total_seconds() * 1000
        response.latency_ms = latency
        self._latencies.append(latency)
        
        # Keep only last 1000
        if len(self._latencies) > 1000:
            self._latencies = self._latencies[-1000:]
            
        return response
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        # Calculate percentiles
        if self._latencies:
            sorted_lat = sorted(self._latencies)
            avg = sum(sorted_lat) / len(sorted_lat)
            p95 = sorted_lat[int(len(sorted_lat) * 0.95)]
            p99 = sorted_lat[int(len(sorted_lat) * 0.99)]
        else:
            avg = p95 = p99 = 0
            
        # Circuit breakers
        open_breakers = sum(
            1 for cb in self.circuit_breakers.values()
            if cb.state == CircuitState.OPEN
        )
        
        return {
            "total_requests": self.stats.total_requests,
            "successful_requests": self.stats.successful_requests,
            "failed_requests": self.stats.failed_requests,
            "rate_limited": self.stats.rate_limited,
            "cache_hits": self.stats.cache_hits,
            "cache_misses": self.stats.cache_misses,
            "circuit_breaks": self.stats.circuit_breaks,
            "avg_latency_ms": avg,
            "p95_latency_ms": p95,
            "p99_latency_ms": p99,
            "backends": len(self.backends),
            "routes": len(self.routes),
            "open_circuit_breakers": open_breakers
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 244: Platform Gateway")
    print("=" * 60)
    
    gateway = PlatformGateway()
    print("✓ Platform Gateway created")
    
    # Register backends
    print("\n🖥️ Registering Backends...")
    
    backends_data = [
        ("user-service-1", "10.0.1.1", 8080, 2),
        ("user-service-2", "10.0.1.2", 8080, 2),
        ("order-service-1", "10.0.2.1", 8080, 1),
        ("order-service-2", "10.0.2.2", 8080, 1),
        ("payment-service-1", "10.0.3.1", 8080, 1),
        ("inventory-service-1", "10.0.4.1", 8080, 1),
    ]
    
    backends = []
    for name, host, port, weight in backends_data:
        be = gateway.register_backend(name, host, port, "http", weight)
        backends.append(be)
        print(f"  🖥️ {name} ({host}:{port}) weight={weight}")
        
    # Create routes
    print("\n🔀 Creating Routes...")
    
    user_route = gateway.create_route(
        "Users API",
        "/api/v1/users*",
        backends=[backends[0].backend_id, backends[1].backend_id],
        methods=[RouteMethod.GET, RouteMethod.POST, RouteMethod.PUT],
        load_balance=LoadBalanceAlgorithm.ROUND_ROBIN,
        api_version="v1"
    )
    print(f"  🔀 {user_route.name}: {user_route.path_pattern}")
    
    order_route = gateway.create_route(
        "Orders API",
        "/api/v1/orders*",
        backends=[backends[2].backend_id, backends[3].backend_id],
        methods=[RouteMethod.GET, RouteMethod.POST],
        load_balance=LoadBalanceAlgorithm.LEAST_CONNECTIONS,
        api_version="v1"
    )
    print(f"  🔀 {order_route.name}: {order_route.path_pattern}")
    
    payment_route = gateway.create_route(
        "Payments API",
        "/api/v1/payments*",
        backends=[backends[4].backend_id],
        methods=[RouteMethod.POST],
        load_balance=LoadBalanceAlgorithm.ROUND_ROBIN,
        api_version="v1"
    )
    print(f"  🔀 {payment_route.name}: {payment_route.path_pattern}")
    
    inventory_route = gateway.create_route(
        "Inventory API",
        "/api/v1/inventory*",
        backends=[backends[5].backend_id],
        load_balance=LoadBalanceAlgorithm.ROUND_ROBIN,
        api_version="v1"
    )
    print(f"  🔀 {inventory_route.name}: {inventory_route.path_pattern}")
    
    # Create rate limits
    print("\n⏱️ Creating Rate Limits...")
    
    global_limit = gateway.create_rate_limit(
        "Global Limit",
        1000,
        RateLimitType.REQUESTS_PER_MINUTE,
        "global"
    )
    print(f"  ⏱️ {global_limit.name}: {global_limit.limit_value} rpm")
    
    ip_limit = gateway.create_rate_limit(
        "Per-IP Limit",
        100,
        RateLimitType.REQUESTS_PER_MINUTE,
        "ip"
    )
    print(f"  ⏱️ {ip_limit.name}: {ip_limit.limit_value} rpm")
    
    # Simulate requests
    print("\n📨 Processing Requests...")
    
    test_requests = [
        (RouteMethod.GET, "/api/v1/users/123", "192.168.1.1"),
        (RouteMethod.POST, "/api/v1/orders", "192.168.1.2"),
        (RouteMethod.GET, "/api/v1/users", "192.168.1.1"),
        (RouteMethod.POST, "/api/v1/payments", "192.168.1.3"),
        (RouteMethod.GET, "/api/v1/inventory/items", "192.168.1.4"),
        (RouteMethod.GET, "/api/v2/unknown", "192.168.1.5"),
    ]
    
    responses = []
    
    for method, path, ip in test_requests:
        request = Request(
            request_id=f"req_{uuid.uuid4().hex[:8]}",
            method=method,
            path=path,
            client_ip=ip
        )
        
        response = await gateway.handle_request(request)
        responses.append((request, response))
        
        status_icon = "✅" if response.status_code == 200 else "❌"
        cached = " (cached)" if response.cached else ""
        print(f"  {status_icon} {method.value} {path} → {response.status_code}{cached}")
        
    # Simulate load
    print("\n🔄 Simulating Load (50 requests)...")
    
    paths = [
        "/api/v1/users",
        "/api/v1/users/123",
        "/api/v1/orders",
        "/api/v1/payments",
        "/api/v1/inventory/items"
    ]
    
    for i in range(50):
        request = Request(
            request_id=f"load_{i}",
            method=RouteMethod.GET,
            path=random.choice(paths),
            client_ip=f"192.168.{random.randint(1, 10)}.{random.randint(1, 254)}"
        )
        
        response = await gateway.handle_request(request)
        
    print("  ✓ Load simulation complete")
    
    # Display routes
    print("\n📊 Route Summary:")
    
    print("\n  ┌─────────────────────┬──────────────────────┬────────────────┬──────────┐")
    print("  │ Route               │ Pattern              │ Load Balance   │ Backends │")
    print("  ├─────────────────────┼──────────────────────┼────────────────┼──────────┤")
    
    for route in gateway.routes.values():
        name = route.name[:19].ljust(19)
        pattern = route.path_pattern[:20].ljust(20)
        lb = route.load_balance.value[:14].ljust(14)
        backends_count = str(len(route.backends))[:8].ljust(8)
        
        print(f"  │ {name} │ {pattern} │ {lb} │ {backends_count} │")
        
    print("  └─────────────────────┴──────────────────────┴────────────────┴──────────┘")
    
    # Display backends
    print("\n🖥️ Backend Status:")
    
    print("\n  ┌─────────────────────┬────────────────┬──────────┬──────────┬──────────┐")
    print("  │ Backend             │ Endpoint       │ Requests │ Failures │ Health   │")
    print("  ├─────────────────────┼────────────────┼──────────┼──────────┼──────────┤")
    
    for backend in gateway.backends.values():
        name = backend.name[:19].ljust(19)
        endpoint = f"{backend.host}:{backend.port}"[:14].ljust(14)
        requests = str(backend.total_requests)[:8].ljust(8)
        failures = str(backend.failed_requests)[:8].ljust(8)
        health = "🟢" if backend.is_healthy else "🔴"
        
        print(f"  │ {name} │ {endpoint} │ {requests} │ {failures} │ {health:8s} │")
        
    print("  └─────────────────────┴────────────────┴──────────┴──────────┴──────────┘")
    
    # Display circuit breakers
    print("\n⚡ Circuit Breakers:")
    
    for backend_id, breaker in gateway.circuit_breakers.items():
        backend = gateway.backends.get(backend_id)
        if not backend:
            continue
            
        state_icon = {
            CircuitState.CLOSED: "🟢",
            CircuitState.OPEN: "🔴",
            CircuitState.HALF_OPEN: "🟡"
        }.get(breaker.state, "⚪")
        
        print(f"  {state_icon} {backend.name}: {breaker.state.value} "
              f"(failures: {breaker.failure_count}/{breaker.failure_threshold})")
              
    # Rate limit status
    print("\n⏱️ Rate Limit Status:")
    
    for key, state in list(gateway.rate_limit_states.items())[:5]:
        rule = gateway.rate_limits.get(state.rule_id)
        if rule:
            usage = (state.request_count / rule.limit_value * 100) if rule.limit_value > 0 else 0
            bar = "█" * int(usage / 10) + "░" * (10 - int(usage / 10))
            print(f"  {key[:30]:30s} [{bar}] {state.request_count}/{rule.limit_value}")
            
    # Statistics
    print("\n📊 Gateway Statistics:")
    
    stats = gateway.get_statistics()
    
    print(f"\n  Total Requests: {stats['total_requests']}")
    print(f"  Successful: {stats['successful_requests']}")
    print(f"  Failed: {stats['failed_requests']}")
    print(f"  Rate Limited: {stats['rate_limited']}")
    
    print(f"\n  Cache Hits: {stats['cache_hits']}")
    print(f"  Cache Misses: {stats['cache_misses']}")
    
    hit_rate = (stats['cache_hits'] / (stats['cache_hits'] + stats['cache_misses']) * 100) \
        if (stats['cache_hits'] + stats['cache_misses']) > 0 else 0
    print(f"  Hit Rate: {hit_rate:.1f}%")
    
    print(f"\n  Avg Latency: {stats['avg_latency_ms']:.2f}ms")
    print(f"  P95 Latency: {stats['p95_latency_ms']:.2f}ms")
    print(f"  P99 Latency: {stats['p99_latency_ms']:.2f}ms")
    
    print(f"\n  Circuit Breaks: {stats['circuit_breaks']}")
    print(f"  Open Breakers: {stats['open_circuit_breakers']}")
    
    # Latency histogram
    print("\n📈 Latency Distribution:")
    
    if gateway._latencies:
        buckets = [0, 20, 40, 60, 80, 100]
        counts = [0] * (len(buckets) - 1)
        
        for lat in gateway._latencies:
            for i in range(len(buckets) - 1):
                if buckets[i] <= lat < buckets[i + 1]:
                    counts[i] += 1
                    break
                    
        max_count = max(counts) if counts else 1
        
        for i in range(len(buckets) - 1):
            bar_len = int(counts[i] / max_count * 20) if max_count > 0 else 0
            bar = "█" * bar_len
            print(f"  {buckets[i]:3d}-{buckets[i+1]:3d}ms │{bar:20s}│ {counts[i]}")
            
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                      Platform Gateway Dashboard                     │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Requests:                {stats['total_requests']:>12}                        │")
    print(f"│ Success Rate:                     {(stats['successful_requests']/stats['total_requests']*100 if stats['total_requests'] > 0 else 0):>6.1f}%                       │")
    print(f"│ Backends:                      {stats['backends']:>12}                        │")
    print(f"│ Routes:                        {stats['routes']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Avg Latency:                      {stats['avg_latency_ms']:>7.2f}ms                      │")
    print(f"│ P99 Latency:                      {stats['p99_latency_ms']:>7.2f}ms                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Platform Gateway initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
