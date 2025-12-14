#!/usr/bin/env python3
"""
Server Init - Iteration 281: API Gateway Advanced Platform
Платформа продвинутого API Gateway

Функционал:
- Request Routing - маршрутизация запросов
- Rate Limiting - ограничение скорости
- Authentication - аутентификация
- Request/Response Transformation - трансформация
- Caching - кэширование
- Circuit Breaking - предохранители
- Load Balancing - балансировка нагрузки
- Request Validation - валидация запросов
"""

import asyncio
import random
import hashlib
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid


class AuthType(Enum):
    """Тип аутентификации"""
    NONE = "none"
    API_KEY = "api_key"
    JWT = "jwt"
    OAUTH2 = "oauth2"
    BASIC = "basic"
    MTLS = "mtls"


class RateLimitStrategy(Enum):
    """Стратегия rate limiting"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"


class LoadBalanceStrategy(Enum):
    """Стратегия балансировки"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"
    IP_HASH = "ip_hash"


class CircuitState(Enum):
    """Состояние предохранителя"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class TransformType(Enum):
    """Тип трансформации"""
    ADD_HEADER = "add_header"
    REMOVE_HEADER = "remove_header"
    MODIFY_BODY = "modify_body"
    REWRITE_PATH = "rewrite_path"
    REDIRECT = "redirect"


@dataclass
class Upstream:
    """Upstream сервис"""
    upstream_id: str
    name: str
    
    # Targets
    targets: List[str] = field(default_factory=list)  # host:port
    
    # Weights
    weights: Dict[str, int] = field(default_factory=dict)
    
    # Health
    healthy_targets: List[str] = field(default_factory=list)
    
    # Load balance
    lb_strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN
    
    # Stats
    current_index: int = 0
    connections: Dict[str, int] = field(default_factory=dict)


@dataclass
class Route:
    """Маршрут"""
    route_id: str
    name: str
    
    # Matching
    path_prefix: str = ""
    path_regex: str = ""
    methods: List[str] = field(default_factory=list)
    hosts: List[str] = field(default_factory=list)
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Upstream
    upstream_name: str = ""
    
    # Strip path
    strip_prefix: bool = False
    
    # Timeout
    timeout_ms: int = 30000
    
    # Priority
    priority: int = 0
    
    # Active
    active: bool = True


@dataclass
class RateLimitConfig:
    """Конфигурация rate limit"""
    config_id: str
    name: str
    
    # Strategy
    strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET
    
    # Limits
    requests_per_second: int = 100
    burst_size: int = 50
    
    # Key
    key_type: str = "ip"  # ip, api_key, user, global
    
    # State
    tokens: float = 0
    last_update: datetime = field(default_factory=datetime.now)
    
    # Per-key state
    key_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class AuthConfig:
    """Конфигурация аутентификации"""
    config_id: str
    name: str
    
    # Type
    auth_type: AuthType = AuthType.API_KEY
    
    # Config
    api_key_header: str = "X-API-Key"
    jwt_secret: str = ""
    jwt_audience: str = ""
    oauth2_introspection_url: str = ""
    
    # Valid keys/tokens
    valid_api_keys: List[str] = field(default_factory=list)
    
    # Active
    active: bool = True


@dataclass
class CacheConfig:
    """Конфигурация кэша"""
    config_id: str
    name: str
    
    # Enabled
    enabled: bool = True
    
    # TTL
    ttl_seconds: int = 300
    
    # Cache key
    vary_headers: List[str] = field(default_factory=list)
    
    # Methods
    cacheable_methods: List[str] = field(default_factory=lambda: ["GET"])
    
    # Status codes
    cacheable_statuses: List[int] = field(default_factory=lambda: [200, 301, 302])


@dataclass
class CacheEntry:
    """Запись кэша"""
    key: str
    response: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=datetime.now)
    hits: int = 0


@dataclass
class CircuitBreaker:
    """Предохранитель"""
    breaker_id: str
    name: str
    
    # State
    state: CircuitState = CircuitState.CLOSED
    
    # Thresholds
    failure_threshold: int = 5
    success_threshold: int = 3
    timeout_seconds: int = 30
    
    # Counters
    failure_count: int = 0
    success_count: int = 0
    
    # Timing
    last_failure: Optional[datetime] = None
    opened_at: Optional[datetime] = None


@dataclass
class Transform:
    """Трансформация"""
    transform_id: str
    name: str
    
    # Type
    transform_type: TransformType = TransformType.ADD_HEADER
    
    # Phase
    phase: str = "request"  # request, response
    
    # Config
    header_name: str = ""
    header_value: str = ""
    body_template: str = ""
    rewrite_pattern: str = ""
    rewrite_replacement: str = ""


@dataclass
class ValidationRule:
    """Правило валидации"""
    rule_id: str
    name: str
    
    # Target
    target: str = "body"  # body, header, query, path
    
    # Schema
    json_schema: Dict[str, Any] = field(default_factory=dict)
    
    # Required fields
    required_fields: List[str] = field(default_factory=list)
    
    # Active
    active: bool = True


@dataclass
class Request:
    """HTTP запрос"""
    request_id: str
    
    # Method and path
    method: str = "GET"
    path: str = "/"
    
    # Headers
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Body
    body: Optional[Any] = None
    
    # Client
    client_ip: str = ""
    
    # Timing
    received_at: datetime = field(default_factory=datetime.now)


@dataclass
class Response:
    """HTTP ответ"""
    response_id: str
    
    # Status
    status_code: int = 200
    
    # Headers
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Body
    body: Optional[Any] = None
    
    # Timing
    latency_ms: float = 0


class APIGatewayManager:
    """Менеджер API Gateway"""
    
    def __init__(self):
        self.upstreams: Dict[str, Upstream] = {}
        self.routes: Dict[str, Route] = {}
        self.rate_limits: Dict[str, RateLimitConfig] = {}
        self.auth_configs: Dict[str, AuthConfig] = {}
        self.cache_configs: Dict[str, CacheConfig] = {}
        self.cache: Dict[str, CacheEntry] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.transforms: Dict[str, List[Transform]] = {}
        self.validation_rules: Dict[str, List[ValidationRule]] = {}
        
        # Stats
        self.requests_total: int = 0
        self.requests_success: int = 0
        self.requests_failed: int = 0
        self.cache_hits: int = 0
        self.cache_misses: int = 0
        self.rate_limited: int = 0
        
    def add_upstream(self, name: str,
                    targets: List[str],
                    lb_strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN,
                    weights: Dict[str, int] = None) -> Upstream:
        """Добавление upstream"""
        upstream = Upstream(
            upstream_id=f"upstream_{uuid.uuid4().hex[:8]}",
            name=name,
            targets=targets,
            healthy_targets=targets.copy(),
            lb_strategy=lb_strategy,
            weights=weights or {t: 1 for t in targets}
        )
        
        self.upstreams[name] = upstream
        return upstream
        
    def add_route(self, name: str,
                 path_prefix: str,
                 upstream_name: str,
                 methods: List[str] = None,
                 strip_prefix: bool = False) -> Route:
        """Добавление маршрута"""
        route = Route(
            route_id=f"route_{uuid.uuid4().hex[:8]}",
            name=name,
            path_prefix=path_prefix,
            upstream_name=upstream_name,
            methods=methods or ["GET", "POST", "PUT", "DELETE"],
            strip_prefix=strip_prefix
        )
        
        self.routes[name] = route
        return route
        
    def configure_rate_limit(self, route_name: str,
                            requests_per_second: int,
                            burst_size: int = None,
                            strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET) -> RateLimitConfig:
        """Настройка rate limit"""
        config = RateLimitConfig(
            config_id=f"ratelimit_{uuid.uuid4().hex[:8]}",
            name=f"{route_name}_ratelimit",
            strategy=strategy,
            requests_per_second=requests_per_second,
            burst_size=burst_size or requests_per_second,
            tokens=float(burst_size or requests_per_second)
        )
        
        self.rate_limits[route_name] = config
        return config
        
    def configure_auth(self, route_name: str,
                      auth_type: AuthType,
                      **kwargs) -> AuthConfig:
        """Настройка аутентификации"""
        config = AuthConfig(
            config_id=f"auth_{uuid.uuid4().hex[:8]}",
            name=f"{route_name}_auth",
            auth_type=auth_type,
            **kwargs
        )
        
        self.auth_configs[route_name] = config
        return config
        
    def configure_cache(self, route_name: str,
                       ttl_seconds: int = 300,
                       vary_headers: List[str] = None) -> CacheConfig:
        """Настройка кэширования"""
        config = CacheConfig(
            config_id=f"cache_{uuid.uuid4().hex[:8]}",
            name=f"{route_name}_cache",
            ttl_seconds=ttl_seconds,
            vary_headers=vary_headers or []
        )
        
        self.cache_configs[route_name] = config
        return config
        
    def configure_circuit_breaker(self, upstream_name: str,
                                 failure_threshold: int = 5,
                                 timeout_seconds: int = 30) -> CircuitBreaker:
        """Настройка circuit breaker"""
        breaker = CircuitBreaker(
            breaker_id=f"breaker_{uuid.uuid4().hex[:8]}",
            name=f"{upstream_name}_breaker",
            failure_threshold=failure_threshold,
            timeout_seconds=timeout_seconds
        )
        
        self.circuit_breakers[upstream_name] = breaker
        return breaker
        
    def add_transform(self, route_name: str,
                     transform_type: TransformType,
                     phase: str = "request",
                     **kwargs) -> Transform:
        """Добавление трансформации"""
        transform = Transform(
            transform_id=f"transform_{uuid.uuid4().hex[:8]}",
            name=f"{route_name}_{transform_type.value}",
            transform_type=transform_type,
            phase=phase,
            **kwargs
        )
        
        if route_name not in self.transforms:
            self.transforms[route_name] = []
        self.transforms[route_name].append(transform)
        
        return transform
        
    def add_validation(self, route_name: str,
                      target: str = "body",
                      required_fields: List[str] = None,
                      json_schema: Dict[str, Any] = None) -> ValidationRule:
        """Добавление валидации"""
        rule = ValidationRule(
            rule_id=f"validation_{uuid.uuid4().hex[:8]}",
            name=f"{route_name}_validation",
            target=target,
            required_fields=required_fields or [],
            json_schema=json_schema or {}
        )
        
        if route_name not in self.validation_rules:
            self.validation_rules[route_name] = []
        self.validation_rules[route_name].append(rule)
        
        return rule
        
    async def handle_request(self, request: Request) -> Response:
        """Обработка запроса"""
        self.requests_total += 1
        start_time = time.time()
        
        # Find matching route
        route = self._find_route(request)
        if not route:
            return Response(
                response_id=f"resp_{uuid.uuid4().hex[:8]}",
                status_code=404,
                body={"error": "Route not found"}
            )
            
        # Check authentication
        if route.name in self.auth_configs:
            auth_result = await self._check_auth(request, self.auth_configs[route.name])
            if not auth_result:
                return Response(
                    response_id=f"resp_{uuid.uuid4().hex[:8]}",
                    status_code=401,
                    body={"error": "Unauthorized"}
                )
                
        # Check rate limit
        if route.name in self.rate_limits:
            allowed = self._check_rate_limit(request, self.rate_limits[route.name])
            if not allowed:
                self.rate_limited += 1
                return Response(
                    response_id=f"resp_{uuid.uuid4().hex[:8]}",
                    status_code=429,
                    body={"error": "Rate limit exceeded"}
                )
                
        # Validate request
        if route.name in self.validation_rules:
            valid = self._validate_request(request, self.validation_rules[route.name])
            if not valid:
                return Response(
                    response_id=f"resp_{uuid.uuid4().hex[:8]}",
                    status_code=400,
                    body={"error": "Validation failed"}
                )
                
        # Apply request transforms
        if route.name in self.transforms:
            request = self._apply_transforms(request, self.transforms[route.name], "request")
            
        # Check cache
        if route.name in self.cache_configs:
            cached = self._get_from_cache(request, route.name)
            if cached:
                self.cache_hits += 1
                cached.latency_ms = (time.time() - start_time) * 1000
                return cached
            self.cache_misses += 1
            
        # Check circuit breaker
        upstream = self.upstreams.get(route.upstream_name)
        if upstream and route.upstream_name in self.circuit_breakers:
            breaker = self.circuit_breakers[route.upstream_name]
            if breaker.state == CircuitState.OPEN:
                if not self._should_try_half_open(breaker):
                    return Response(
                        response_id=f"resp_{uuid.uuid4().hex[:8]}",
                        status_code=503,
                        body={"error": "Service unavailable"}
                    )
                breaker.state = CircuitState.HALF_OPEN
                
        # Forward to upstream
        response = await self._forward_request(request, route)
        
        # Update circuit breaker
        if upstream and route.upstream_name in self.circuit_breakers:
            self._update_circuit_breaker(
                self.circuit_breakers[route.upstream_name],
                response.status_code < 500
            )
            
        # Apply response transforms
        if route.name in self.transforms:
            response = self._apply_response_transforms(response, self.transforms[route.name])
            
        # Cache response
        if route.name in self.cache_configs and response.status_code == 200:
            self._store_in_cache(request, response, route.name)
            
        response.latency_ms = (time.time() - start_time) * 1000
        
        if response.status_code < 400:
            self.requests_success += 1
        else:
            self.requests_failed += 1
            
        return response
        
    def _find_route(self, request: Request) -> Optional[Route]:
        """Поиск маршрута"""
        for route in sorted(self.routes.values(), key=lambda r: -r.priority):
            if not route.active:
                continue
            if route.path_prefix and request.path.startswith(route.path_prefix):
                if not route.methods or request.method in route.methods:
                    return route
        return None
        
    async def _check_auth(self, request: Request, config: AuthConfig) -> bool:
        """Проверка аутентификации"""
        if config.auth_type == AuthType.NONE:
            return True
            
        if config.auth_type == AuthType.API_KEY:
            api_key = request.headers.get(config.api_key_header)
            return api_key in config.valid_api_keys
            
        if config.auth_type == AuthType.JWT:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                # Simplified JWT validation
                return len(auth_header) > 20
                
        return False
        
    def _check_rate_limit(self, request: Request,
                         config: RateLimitConfig) -> bool:
        """Проверка rate limit"""
        key = request.client_ip if config.key_type == "ip" else "global"
        
        if config.strategy == RateLimitStrategy.TOKEN_BUCKET:
            now = datetime.now()
            elapsed = (now - config.last_update).total_seconds()
            
            # Replenish tokens
            config.tokens = min(
                config.burst_size,
                config.tokens + elapsed * config.requests_per_second
            )
            config.last_update = now
            
            if config.tokens >= 1:
                config.tokens -= 1
                return True
            return False
            
        return True
        
    def _validate_request(self, request: Request,
                         rules: List[ValidationRule]) -> bool:
        """Валидация запроса"""
        for rule in rules:
            if not rule.active:
                continue
                
            if rule.target == "body" and request.body:
                if rule.required_fields:
                    if isinstance(request.body, dict):
                        for field in rule.required_fields:
                            if field not in request.body:
                                return False
                                
        return True
        
    def _apply_transforms(self, request: Request,
                         transforms: List[Transform],
                         phase: str) -> Request:
        """Применение трансформаций запроса"""
        for transform in transforms:
            if transform.phase != phase:
                continue
                
            if transform.transform_type == TransformType.ADD_HEADER:
                request.headers[transform.header_name] = transform.header_value
                
            elif transform.transform_type == TransformType.REMOVE_HEADER:
                request.headers.pop(transform.header_name, None)
                
        return request
        
    def _apply_response_transforms(self, response: Response,
                                  transforms: List[Transform]) -> Response:
        """Применение трансформаций ответа"""
        for transform in transforms:
            if transform.phase != "response":
                continue
                
            if transform.transform_type == TransformType.ADD_HEADER:
                response.headers[transform.header_name] = transform.header_value
                
        return response
        
    def _get_from_cache(self, request: Request, route_name: str) -> Optional[Response]:
        """Получение из кэша"""
        config = self.cache_configs.get(route_name)
        if not config or not config.enabled:
            return None
            
        if request.method not in config.cacheable_methods:
            return None
            
        cache_key = self._generate_cache_key(request, config)
        entry = self.cache.get(cache_key)
        
        if entry and entry.expires_at > datetime.now():
            entry.hits += 1
            return Response(
                response_id=f"resp_{uuid.uuid4().hex[:8]}",
                status_code=entry.response.get("status_code", 200),
                headers=entry.response.get("headers", {}),
                body=entry.response.get("body")
            )
            
        return None
        
    def _store_in_cache(self, request: Request, response: Response, route_name: str):
        """Сохранение в кэш"""
        config = self.cache_configs.get(route_name)
        if not config or not config.enabled:
            return
            
        cache_key = self._generate_cache_key(request, config)
        
        self.cache[cache_key] = CacheEntry(
            key=cache_key,
            response={
                "status_code": response.status_code,
                "headers": response.headers,
                "body": response.body
            },
            expires_at=datetime.now() + timedelta(seconds=config.ttl_seconds)
        )
        
    def _generate_cache_key(self, request: Request, config: CacheConfig) -> str:
        """Генерация ключа кэша"""
        parts = [request.method, request.path]
        
        for header in config.vary_headers:
            parts.append(request.headers.get(header, ""))
            
        return hashlib.md5(":".join(parts).encode()).hexdigest()
        
    def _should_try_half_open(self, breaker: CircuitBreaker) -> bool:
        """Проверка перехода в half-open"""
        if not breaker.opened_at:
            return True
            
        elapsed = (datetime.now() - breaker.opened_at).total_seconds()
        return elapsed >= breaker.timeout_seconds
        
    def _update_circuit_breaker(self, breaker: CircuitBreaker, success: bool):
        """Обновление circuit breaker"""
        if success:
            breaker.success_count += 1
            
            if breaker.state == CircuitState.HALF_OPEN:
                if breaker.success_count >= breaker.success_threshold:
                    breaker.state = CircuitState.CLOSED
                    breaker.failure_count = 0
                    breaker.success_count = 0
        else:
            breaker.failure_count += 1
            breaker.success_count = 0
            breaker.last_failure = datetime.now()
            
            if breaker.state == CircuitState.HALF_OPEN:
                breaker.state = CircuitState.OPEN
                breaker.opened_at = datetime.now()
            elif breaker.failure_count >= breaker.failure_threshold:
                breaker.state = CircuitState.OPEN
                breaker.opened_at = datetime.now()
                
    async def _forward_request(self, request: Request, route: Route) -> Response:
        """Пересылка запроса к upstream"""
        upstream = self.upstreams.get(route.upstream_name)
        if not upstream or not upstream.healthy_targets:
            return Response(
                response_id=f"resp_{uuid.uuid4().hex[:8]}",
                status_code=502,
                body={"error": "No healthy upstream"}
            )
            
        # Select target
        target = self._select_target(upstream)
        
        # Simulate request
        await asyncio.sleep(random.uniform(0.01, 0.1))
        
        # Random success/failure
        if random.random() < 0.95:
            return Response(
                response_id=f"resp_{uuid.uuid4().hex[:8]}",
                status_code=200,
                headers={"X-Upstream": target},
                body={"status": "ok", "target": target}
            )
        else:
            return Response(
                response_id=f"resp_{uuid.uuid4().hex[:8]}",
                status_code=500,
                body={"error": "Upstream error"}
            )
            
    def _select_target(self, upstream: Upstream) -> str:
        """Выбор target"""
        targets = upstream.healthy_targets
        if not targets:
            return ""
            
        if upstream.lb_strategy == LoadBalanceStrategy.ROUND_ROBIN:
            target = targets[upstream.current_index % len(targets)]
            upstream.current_index += 1
            return target
            
        elif upstream.lb_strategy == LoadBalanceStrategy.RANDOM:
            return random.choice(targets)
            
        elif upstream.lb_strategy == LoadBalanceStrategy.WEIGHTED:
            total = sum(upstream.weights.get(t, 1) for t in targets)
            r = random.randint(1, total)
            cumulative = 0
            for t in targets:
                cumulative += upstream.weights.get(t, 1)
                if r <= cumulative:
                    return t
            return targets[-1]
            
        return targets[0]
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        return {
            "requests_total": self.requests_total,
            "requests_success": self.requests_success,
            "requests_failed": self.requests_failed,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "rate_limited": self.rate_limited,
            "upstreams": len(self.upstreams),
            "routes": len(self.routes),
            "cache_entries": len(self.cache)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 281: API Gateway Advanced Platform")
    print("=" * 60)
    
    manager = APIGatewayManager()
    print("✓ API Gateway Manager created")
    
    # Add upstreams
    print("\n🎯 Adding Upstreams...")
    
    upstreams_config = [
        ("user-service", ["user-1:8080", "user-2:8080", "user-3:8080"], LoadBalanceStrategy.ROUND_ROBIN),
        ("order-service", ["order-1:8080", "order-2:8080"], LoadBalanceStrategy.LEAST_CONNECTIONS),
        ("product-service", ["product-1:8080", "product-2:8080", "product-3:8080"], LoadBalanceStrategy.WEIGHTED),
    ]
    
    for name, targets, strategy in upstreams_config:
        upstream = manager.add_upstream(name, targets, strategy)
        if strategy == LoadBalanceStrategy.WEIGHTED:
            upstream.weights = {targets[0]: 5, targets[1]: 3, targets[2]: 2}
        print(f"  🎯 {name}: {len(targets)} targets, {strategy.value}")
        
    # Add routes
    print("\n🛤️ Adding Routes...")
    
    routes_config = [
        ("users", "/api/v1/users", "user-service", ["GET", "POST"]),
        ("orders", "/api/v1/orders", "order-service", ["GET", "POST", "PUT"]),
        ("products", "/api/v1/products", "product-service", ["GET"]),
    ]
    
    for name, path, upstream, methods in routes_config:
        route = manager.add_route(name, path, upstream, methods)
        print(f"  🛤️ {path} -> {upstream}")
        
    # Configure rate limits
    print("\n⏱️ Configuring Rate Limits...")
    
    manager.configure_rate_limit("users", 100, 50)
    manager.configure_rate_limit("orders", 50, 25)
    manager.configure_rate_limit("products", 200, 100)
    print("  Rate limits configured")
    
    # Configure authentication
    print("\n🔐 Configuring Authentication...")
    
    auth = manager.configure_auth(
        "orders",
        AuthType.API_KEY,
        api_key_header="X-API-Key",
        valid_api_keys=["key-123", "key-456", "key-789"]
    )
    print(f"  {auth.name}: {auth.auth_type.value}")
    
    # Configure caching
    print("\n💾 Configuring Caching...")
    
    manager.configure_cache("products", ttl_seconds=600, vary_headers=["Accept-Language"])
    print("  Products cache: 600s TTL")
    
    # Configure circuit breakers
    print("\n⚡ Configuring Circuit Breakers...")
    
    for upstream_name in manager.upstreams:
        breaker = manager.configure_circuit_breaker(upstream_name, failure_threshold=3)
        print(f"  {upstream_name}: threshold={breaker.failure_threshold}")
        
    # Add transforms
    print("\n🔄 Adding Transforms...")
    
    manager.add_transform("users", TransformType.ADD_HEADER, "request",
                         header_name="X-Request-ID", header_value=str(uuid.uuid4()))
    manager.add_transform("users", TransformType.ADD_HEADER, "response",
                         header_name="X-Gateway-Version", header_value="1.0")
    print("  Transforms added")
    
    # Add validation
    print("\n✅ Adding Validation Rules...")
    
    manager.add_validation("orders", "body", required_fields=["user_id", "items"])
    print("  Orders validation: required fields")
    
    # Simulate requests
    print("\n🚀 Processing Requests...")
    
    test_requests = [
        Request(request_id="r1", method="GET", path="/api/v1/users", client_ip="192.168.1.1"),
        Request(request_id="r2", method="GET", path="/api/v1/products", client_ip="192.168.1.2"),
        Request(request_id="r3", method="POST", path="/api/v1/orders", client_ip="192.168.1.3",
               headers={"X-API-Key": "key-123"}, body={"user_id": 1, "items": []}),
        Request(request_id="r4", method="POST", path="/api/v1/orders", client_ip="192.168.1.4",
               headers={"X-API-Key": "invalid"}, body={"user_id": 2, "items": []}),
        Request(request_id="r5", method="GET", path="/api/v1/products", client_ip="192.168.1.5"),  # Cache hit
    ]
    
    for req in test_requests:
        response = await manager.handle_request(req)
        status_icon = "✅" if response.status_code < 400 else "❌"
        print(f"  {status_icon} {req.method} {req.path} -> {response.status_code} ({response.latency_ms:.1f}ms)")
        
    # Process more requests for stats
    print("\n📊 Processing bulk requests...")
    
    for i in range(50):
        req = Request(
            request_id=f"bulk_{i}",
            method=random.choice(["GET", "POST"]),
            path=random.choice(["/api/v1/users", "/api/v1/products", "/api/v1/orders"]),
            client_ip=f"192.168.{random.randint(1,255)}.{random.randint(1,255)}",
            headers={"X-API-Key": "key-123"},
            body={"user_id": i, "items": []} if random.random() > 0.5 else None
        )
        await manager.handle_request(req)
        
    print(f"  Processed 50 bulk requests")
    
    # Display routes
    print("\n🛤️ Routes Configuration:")
    
    print("\n  ┌────────────────────┬─────────────────────────┬─────────────────────┬─────────────┐")
    print("  │ Route              │ Path                    │ Upstream            │ Methods     │")
    print("  ├────────────────────┼─────────────────────────┼─────────────────────┼─────────────┤")
    
    for route in manager.routes.values():
        name = route.name[:18].ljust(18)
        path = route.path_prefix[:23].ljust(23)
        upstream = route.upstream_name[:19].ljust(19)
        methods = ",".join(route.methods)[:11].ljust(11)
        
        print(f"  │ {name} │ {path} │ {upstream} │ {methods} │")
        
    print("  └────────────────────┴─────────────────────────┴─────────────────────┴─────────────┘")
    
    # Display upstreams
    print("\n🎯 Upstreams Status:")
    
    for upstream in manager.upstreams.values():
        healthy = len(upstream.healthy_targets)
        total = len(upstream.targets)
        status = "🟢" if healthy == total else "🟡" if healthy > 0 else "🔴"
        
        print(f"\n  {status} {upstream.name}:")
        print(f"    Strategy: {upstream.lb_strategy.value}")
        print(f"    Targets: {healthy}/{total} healthy")
        
        for target in upstream.targets[:3]:
            health = "✅" if target in upstream.healthy_targets else "❌"
            weight = upstream.weights.get(target, 1)
            print(f"      {health} {target} (weight: {weight})")
            
    # Display circuit breakers
    print("\n⚡ Circuit Breakers:")
    
    for name, breaker in manager.circuit_breakers.items():
        state_icon = {
            CircuitState.CLOSED: "🟢",
            CircuitState.OPEN: "🔴",
            CircuitState.HALF_OPEN: "🟡"
        }.get(breaker.state, "⚪")
        
        print(f"  {state_icon} {name}: {breaker.state.value}")
        print(f"    Failures: {breaker.failure_count}/{breaker.failure_threshold}")
        
    # Display rate limits
    print("\n⏱️ Rate Limit Status:")
    
    for name, config in manager.rate_limits.items():
        tokens = int(config.tokens)
        max_tokens = config.burst_size
        bar = "█" * int(tokens / max_tokens * 10) + "░" * (10 - int(tokens / max_tokens * 10))
        
        print(f"  {name}: [{bar}] {tokens}/{max_tokens} tokens")
        
    # Display cache
    print("\n💾 Cache Status:")
    
    for name, config in manager.cache_configs.items():
        entries = sum(1 for e in manager.cache.values() if name in e.key)
        status = "🟢 Enabled" if config.enabled else "🔴 Disabled"
        
        print(f"  {name}: {status}, TTL={config.ttl_seconds}s, entries={entries}")
        
    # Statistics
    print("\n📊 Gateway Statistics:")
    
    stats = manager.get_statistics()
    
    success_rate = stats['requests_success'] / max(stats['requests_total'], 1) * 100
    cache_hit_rate = stats['cache_hits'] / max(stats['cache_hits'] + stats['cache_misses'], 1) * 100
    
    print(f"\n  Total Requests: {stats['requests_total']}")
    print(f"  Success: {stats['requests_success']} ({success_rate:.1f}%)")
    print(f"  Failed: {stats['requests_failed']}")
    print(f"  Rate Limited: {stats['rate_limited']}")
    print(f"\n  Cache Hits: {stats['cache_hits']}")
    print(f"  Cache Misses: {stats['cache_misses']}")
    print(f"  Hit Rate: {cache_hit_rate:.1f}%")
    print(f"\n  Upstreams: {stats['upstreams']}")
    print(f"  Routes: {stats['routes']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    API Gateway Dashboard                            │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Requests:                {stats['requests_total']:>12}                        │")
    print(f"│ Success Rate:                  {success_rate:>11.1f}%                        │")
    print(f"│ Rate Limited:                  {stats['rate_limited']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Cache Hit Rate:                {cache_hit_rate:>11.1f}%                        │")
    print(f"│ Active Routes:                 {stats['routes']:>12}                        │")
    print(f"│ Upstreams:                     {stats['upstreams']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("API Gateway Advanced Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
