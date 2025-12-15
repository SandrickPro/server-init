#!/usr/bin/env python3
"""
Server Init - Iteration 314: API Gateway Manager Platform
Платформа управления API шлюзом

Функционал:
- API Registration - регистрация API
- Rate Limiting - ограничение запросов
- Authentication - аутентификация
- Request Routing - маршрутизация запросов
- Load Balancing - балансировка нагрузки
- Caching - кэширование
- Monitoring - мониторинг
- Analytics - аналитика
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid
import hashlib


class AuthType(Enum):
    """Тип аутентификации"""
    NONE = "none"
    API_KEY = "api_key"
    JWT = "jwt"
    OAUTH2 = "oauth2"
    BASIC = "basic"


class RateLimitType(Enum):
    """Тип ограничения"""
    REQUESTS_PER_SECOND = "requests_per_second"
    REQUESTS_PER_MINUTE = "requests_per_minute"
    REQUESTS_PER_HOUR = "requests_per_hour"
    REQUESTS_PER_DAY = "requests_per_day"


class LoadBalanceStrategy(Enum):
    """Стратегия балансировки"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"
    WEIGHTED = "weighted"
    IP_HASH = "ip_hash"


class CachePolicy(Enum):
    """Политика кэширования"""
    NO_CACHE = "no_cache"
    PUBLIC = "public"
    PRIVATE = "private"
    MUST_REVALIDATE = "must_revalidate"


class APIStatus(Enum):
    """Статус API"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    MAINTENANCE = "maintenance"


@dataclass
class Upstream:
    """Апстрим сервер"""
    upstream_id: str
    name: str
    
    # Target
    host: str = ""
    port: int = 80
    protocol: str = "http"
    
    # Weight
    weight: int = 1
    
    # Health
    is_healthy: bool = True
    health_check_path: str = "/health"
    last_health_check: Optional[datetime] = None
    
    # Stats
    requests_count: int = 0
    errors_count: int = 0
    active_connections: int = 0
    avg_response_time_ms: float = 0


@dataclass
class Route:
    """Маршрут"""
    route_id: str
    path: str
    methods: List[str] = field(default_factory=lambda: ["GET"])
    
    # Target
    upstream_ids: List[str] = field(default_factory=list)
    
    # Rewrite
    strip_path: bool = False
    rewrite_path: str = ""
    
    # Headers
    request_headers: Dict[str, str] = field(default_factory=dict)
    response_headers: Dict[str, str] = field(default_factory=dict)
    
    # Priority
    priority: int = 0


@dataclass
class RateLimit:
    """Ограничение запросов"""
    limit_id: str
    name: str
    
    # Limits
    limit_type: RateLimitType = RateLimitType.REQUESTS_PER_MINUTE
    limit_value: int = 100
    
    # Scope
    scope: str = "api"  # api, consumer, ip
    
    # Response
    exceeded_status_code: int = 429
    exceeded_message: str = "Rate limit exceeded"


@dataclass
class CacheConfig:
    """Конфигурация кэша"""
    cache_id: str
    
    # Policy
    policy: CachePolicy = CachePolicy.NO_CACHE
    ttl_seconds: int = 300
    
    # Keys
    vary_headers: List[str] = field(default_factory=list)
    include_query_params: bool = True
    
    # Stats
    hits: int = 0
    misses: int = 0


@dataclass
class Consumer:
    """Потребитель API"""
    consumer_id: str
    name: str
    
    # Auth
    api_key: str = ""
    
    # Limits
    rate_limit_id: str = ""
    
    # Status
    is_active: bool = True
    
    # Stats
    requests_count: int = 0
    last_request: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class API:
    """API"""
    api_id: str
    name: str
    description: str
    version: str = "v1"
    
    # Base path
    base_path: str = ""
    
    # Routes
    routes: List[str] = field(default_factory=list)  # route_ids
    
    # Auth
    auth_type: AuthType = AuthType.API_KEY
    
    # Rate limiting
    rate_limit_id: str = ""
    
    # Caching
    cache_id: str = ""
    
    # Load balancing
    load_balance_strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN
    
    # Status
    status: APIStatus = APIStatus.ACTIVE
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Stats
    requests_count: int = 0
    errors_count: int = 0
    avg_latency_ms: float = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Request:
    """Запрос"""
    request_id: str
    api_id: str
    
    # Request
    method: str = "GET"
    path: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Consumer
    consumer_id: str = ""
    client_ip: str = ""
    
    # Response
    status_code: int = 0
    response_size_bytes: int = 0
    
    # Timing
    latency_ms: float = 0
    
    # Cache
    cache_hit: bool = False
    
    # Timestamps
    timestamp: datetime = field(default_factory=datetime.now)


class APIGatewayManager:
    """Менеджер API шлюза"""
    
    def __init__(self):
        self.upstreams: Dict[str, Upstream] = {}
        self.routes: Dict[str, Route] = {}
        self.rate_limits: Dict[str, RateLimit] = {}
        self.caches: Dict[str, CacheConfig] = {}
        self.consumers: Dict[str, Consumer] = {}
        self.apis: Dict[str, API] = {}
        self.requests: List[Request] = []
        
        # Cache storage
        self._cache_store: Dict[str, Any] = {}
        
        # Rate limit counters
        self._rate_counters: Dict[str, Dict[str, int]] = {}
        
    async def create_upstream(self, name: str,
                             host: str,
                             port: int = 80,
                             protocol: str = "http",
                             weight: int = 1) -> Upstream:
        """Создание апстрима"""
        upstream = Upstream(
            upstream_id=f"ups_{uuid.uuid4().hex[:8]}",
            name=name,
            host=host,
            port=port,
            protocol=protocol,
            weight=weight
        )
        
        self.upstreams[upstream.upstream_id] = upstream
        return upstream
        
    async def create_route(self, path: str,
                          methods: List[str] = None,
                          upstream_ids: List[str] = None,
                          strip_path: bool = False,
                          rewrite_path: str = "") -> Route:
        """Создание маршрута"""
        route = Route(
            route_id=f"rt_{uuid.uuid4().hex[:8]}",
            path=path,
            methods=methods or ["GET"],
            upstream_ids=upstream_ids or [],
            strip_path=strip_path,
            rewrite_path=rewrite_path
        )
        
        self.routes[route.route_id] = route
        return route
        
    async def create_rate_limit(self, name: str,
                               limit_type: RateLimitType,
                               limit_value: int,
                               scope: str = "api") -> RateLimit:
        """Создание ограничения"""
        rate_limit = RateLimit(
            limit_id=f"rl_{uuid.uuid4().hex[:8]}",
            name=name,
            limit_type=limit_type,
            limit_value=limit_value,
            scope=scope
        )
        
        self.rate_limits[rate_limit.limit_id] = rate_limit
        return rate_limit
        
    async def create_cache(self, policy: CachePolicy,
                          ttl_seconds: int = 300,
                          vary_headers: List[str] = None) -> CacheConfig:
        """Создание кэша"""
        cache = CacheConfig(
            cache_id=f"cache_{uuid.uuid4().hex[:8]}",
            policy=policy,
            ttl_seconds=ttl_seconds,
            vary_headers=vary_headers or []
        )
        
        self.caches[cache.cache_id] = cache
        return cache
        
    async def create_consumer(self, name: str,
                             rate_limit_id: str = "") -> Consumer:
        """Создание потребителя"""
        consumer = Consumer(
            consumer_id=f"con_{uuid.uuid4().hex[:8]}",
            name=name,
            api_key=hashlib.sha256(uuid.uuid4().bytes).hexdigest()[:32],
            rate_limit_id=rate_limit_id
        )
        
        self.consumers[consumer.consumer_id] = consumer
        return consumer
        
    async def create_api(self, name: str,
                        description: str = "",
                        version: str = "v1",
                        base_path: str = "",
                        auth_type: AuthType = AuthType.API_KEY,
                        load_balance_strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN) -> API:
        """Создание API"""
        api = API(
            api_id=f"api_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            version=version,
            base_path=base_path or f"/{name.lower().replace(' ', '-')}",
            auth_type=auth_type,
            load_balance_strategy=load_balance_strategy
        )
        
        self.apis[api.api_id] = api
        return api
        
    async def add_route_to_api(self, api_id: str, route_id: str) -> bool:
        """Добавление маршрута в API"""
        api = self.apis.get(api_id)
        route = self.routes.get(route_id)
        
        if not api or not route:
            return False
            
        if route_id not in api.routes:
            api.routes.append(route_id)
            
        return True
        
    async def set_rate_limit(self, api_id: str, rate_limit_id: str) -> bool:
        """Установка ограничения для API"""
        api = self.apis.get(api_id)
        rate_limit = self.rate_limits.get(rate_limit_id)
        
        if not api or not rate_limit:
            return False
            
        api.rate_limit_id = rate_limit_id
        return True
        
    async def set_cache(self, api_id: str, cache_id: str) -> bool:
        """Установка кэша для API"""
        api = self.apis.get(api_id)
        cache = self.caches.get(cache_id)
        
        if not api or not cache:
            return False
            
        api.cache_id = cache_id
        return True
        
    async def handle_request(self, api_id: str,
                            method: str,
                            path: str,
                            consumer_id: str = "",
                            client_ip: str = "") -> Request:
        """Обработка запроса"""
        api = self.apis.get(api_id)
        if not api:
            return self._create_error_request(api_id, method, path, 404)
            
        if api.status != APIStatus.ACTIVE:
            return self._create_error_request(api_id, method, path, 503)
            
        # Check rate limit
        if api.rate_limit_id:
            if not await self._check_rate_limit(api.rate_limit_id, consumer_id or client_ip):
                return self._create_error_request(api_id, method, path, 429)
                
        # Check cache
        cache_key = f"{api_id}:{method}:{path}"
        cache_hit = False
        
        if api.cache_id and method == "GET":
            cache = self.caches.get(api.cache_id)
            if cache and cache.policy != CachePolicy.NO_CACHE:
                if cache_key in self._cache_store:
                    cache.hits += 1
                    cache_hit = True
                else:
                    cache.misses += 1
                    self._cache_store[cache_key] = {"timestamp": datetime.now()}
                    
        # Find route
        route = self._find_route(api, path, method)
        if not route:
            return self._create_error_request(api_id, method, path, 404)
            
        # Select upstream
        upstream = await self._select_upstream(route, api.load_balance_strategy, client_ip)
        if not upstream:
            return self._create_error_request(api_id, method, path, 502)
            
        # Simulate request
        latency = random.uniform(10, 200) if not cache_hit else random.uniform(1, 10)
        await asyncio.sleep(latency / 1000)
        
        # Simulate response
        status_code = 200 if random.random() > 0.05 else random.choice([500, 502, 503])
        
        request = Request(
            request_id=f"req_{uuid.uuid4().hex[:8]}",
            api_id=api_id,
            method=method,
            path=path,
            consumer_id=consumer_id,
            client_ip=client_ip,
            status_code=status_code,
            response_size_bytes=random.randint(100, 10000),
            latency_ms=latency,
            cache_hit=cache_hit
        )
        
        self.requests.append(request)
        
        # Update stats
        api.requests_count += 1
        if status_code >= 400:
            api.errors_count += 1
            
        # Update average latency
        total_latency = api.avg_latency_ms * (api.requests_count - 1) + latency
        api.avg_latency_ms = total_latency / api.requests_count
        
        # Update upstream stats
        upstream.requests_count += 1
        if status_code >= 500:
            upstream.errors_count += 1
            
        # Update consumer stats
        if consumer_id:
            consumer = self.consumers.get(consumer_id)
            if consumer:
                consumer.requests_count += 1
                consumer.last_request = datetime.now()
                
        return request
        
    def _create_error_request(self, api_id: str, method: str,
                             path: str, status_code: int) -> Request:
        """Создание ошибочного запроса"""
        request = Request(
            request_id=f"req_{uuid.uuid4().hex[:8]}",
            api_id=api_id,
            method=method,
            path=path,
            status_code=status_code,
            latency_ms=random.uniform(1, 5)
        )
        
        self.requests.append(request)
        return request
        
    async def _check_rate_limit(self, rate_limit_id: str, key: str) -> bool:
        """Проверка ограничения"""
        rate_limit = self.rate_limits.get(rate_limit_id)
        if not rate_limit:
            return True
            
        counter_key = f"{rate_limit_id}:{key}"
        
        if counter_key not in self._rate_counters:
            self._rate_counters[counter_key] = {"count": 0, "reset": datetime.now()}
            
        counter = self._rate_counters[counter_key]
        
        # Check if reset needed
        now = datetime.now()
        reset_interval = timedelta(seconds=60)  # Simplified
        
        if (now - counter["reset"]) > reset_interval:
            counter["count"] = 0
            counter["reset"] = now
            
        counter["count"] += 1
        
        return counter["count"] <= rate_limit.limit_value
        
    def _find_route(self, api: API, path: str, method: str) -> Optional[Route]:
        """Поиск маршрута"""
        for route_id in api.routes:
            route = self.routes.get(route_id)
            if route and method in route.methods:
                # Simple path matching
                if path.startswith(route.path) or route.path == "*":
                    return route
                    
        return None
        
    async def _select_upstream(self, route: Route,
                              strategy: LoadBalanceStrategy,
                              client_ip: str = "") -> Optional[Upstream]:
        """Выбор апстрима"""
        healthy_upstreams = [
            self.upstreams[uid] for uid in route.upstream_ids
            if uid in self.upstreams and self.upstreams[uid].is_healthy
        ]
        
        if not healthy_upstreams:
            return None
            
        if strategy == LoadBalanceStrategy.ROUND_ROBIN:
            return healthy_upstreams[0]
        elif strategy == LoadBalanceStrategy.RANDOM:
            return random.choice(healthy_upstreams)
        elif strategy == LoadBalanceStrategy.LEAST_CONNECTIONS:
            return min(healthy_upstreams, key=lambda u: u.active_connections)
        elif strategy == LoadBalanceStrategy.WEIGHTED:
            total_weight = sum(u.weight for u in healthy_upstreams)
            r = random.uniform(0, total_weight)
            current = 0
            for upstream in healthy_upstreams:
                current += upstream.weight
                if r <= current:
                    return upstream
            return healthy_upstreams[-1]
        elif strategy == LoadBalanceStrategy.IP_HASH:
            if client_ip:
                idx = hash(client_ip) % len(healthy_upstreams)
                return healthy_upstreams[idx]
            return healthy_upstreams[0]
            
        return healthy_upstreams[0]
        
    async def health_check(self, upstream_id: str) -> bool:
        """Проверка здоровья апстрима"""
        upstream = self.upstreams.get(upstream_id)
        if not upstream:
            return False
            
        # Simulate health check
        await asyncio.sleep(random.uniform(0.01, 0.05))
        
        is_healthy = random.random() > 0.1  # 90% healthy
        upstream.is_healthy = is_healthy
        upstream.last_health_check = datetime.now()
        
        return is_healthy
        
    def get_api_stats(self, api_id: str) -> Dict[str, Any]:
        """Статистика API"""
        api = self.apis.get(api_id)
        if not api:
            return {}
            
        api_requests = [r for r in self.requests if r.api_id == api_id]
        
        error_rate = 0
        if api.requests_count > 0:
            error_rate = api.errors_count / api.requests_count * 100
            
        cache_hit_rate = 0
        cache_hits = sum(1 for r in api_requests if r.cache_hit)
        if api_requests:
            cache_hit_rate = cache_hits / len(api_requests) * 100
            
        status_codes = {}
        for r in api_requests:
            status_codes[r.status_code] = status_codes.get(r.status_code, 0) + 1
            
        return {
            "api_id": api_id,
            "name": api.name,
            "status": api.status.value,
            "requests": api.requests_count,
            "errors": api.errors_count,
            "error_rate": error_rate,
            "avg_latency_ms": api.avg_latency_ms,
            "cache_hit_rate": cache_hit_rate,
            "status_codes": status_codes,
            "routes_count": len(api.routes)
        }
        
    def get_consumer_stats(self, consumer_id: str) -> Dict[str, Any]:
        """Статистика потребителя"""
        consumer = self.consumers.get(consumer_id)
        if not consumer:
            return {}
            
        consumer_requests = [r for r in self.requests if r.consumer_id == consumer_id]
        
        return {
            "consumer_id": consumer_id,
            "name": consumer.name,
            "is_active": consumer.is_active,
            "requests": consumer.requests_count,
            "last_request": consumer.last_request.isoformat() if consumer.last_request else None
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        by_status = {}
        total_errors = 0
        total_latency = 0
        
        for api in self.apis.values():
            by_status[api.status.value] = by_status.get(api.status.value, 0) + 1
            total_errors += api.errors_count
            
        for r in self.requests:
            total_latency += r.latency_ms
            
        upstreams_healthy = sum(1 for u in self.upstreams.values() if u.is_healthy)
        consumers_active = sum(1 for c in self.consumers.values() if c.is_active)
        
        cache_hits = sum(c.hits for c in self.caches.values())
        cache_misses = sum(c.misses for c in self.caches.values())
        
        return {
            "total_apis": len(self.apis),
            "by_status": by_status,
            "total_upstreams": len(self.upstreams),
            "upstreams_healthy": upstreams_healthy,
            "total_routes": len(self.routes),
            "total_consumers": len(self.consumers),
            "consumers_active": consumers_active,
            "total_rate_limits": len(self.rate_limits),
            "total_requests": len(self.requests),
            "total_errors": total_errors,
            "avg_latency_ms": total_latency / max(len(self.requests), 1),
            "cache_hits": cache_hits,
            "cache_misses": cache_misses,
            "cache_hit_rate": (cache_hits / (cache_hits + cache_misses) * 100) if (cache_hits + cache_misses) > 0 else 0
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 314: API Gateway Manager Platform")
    print("=" * 60)
    
    gateway = APIGatewayManager()
    print("✓ API Gateway Manager created")
    
    # Create upstreams
    print("\n🖥️ Creating Upstreams...")
    
    upstreams_data = [
        ("User Service 1", "user-svc-1.local", 8080, 3),
        ("User Service 2", "user-svc-2.local", 8080, 2),
        ("Order Service 1", "order-svc-1.local", 8081, 1),
        ("Order Service 2", "order-svc-2.local", 8081, 1),
        ("Product Service", "product-svc.local", 8082, 2),
        ("Payment Service", "payment-svc.local", 8083, 1),
        ("Notification Service", "notify-svc.local", 8084, 1)
    ]
    
    upstreams = []
    for name, host, port, weight in upstreams_data:
        upstream = await gateway.create_upstream(name, host, port, "http", weight)
        upstreams.append(upstream)
        print(f"  🖥️ {name} ({host}:{port}) weight={weight}")
        
    # Create routes
    print("\n🔀 Creating Routes...")
    
    routes_data = [
        ("/users", ["GET", "POST"], [upstreams[0].upstream_id, upstreams[1].upstream_id]),
        ("/users/{id}", ["GET", "PUT", "DELETE"], [upstreams[0].upstream_id, upstreams[1].upstream_id]),
        ("/orders", ["GET", "POST"], [upstreams[2].upstream_id, upstreams[3].upstream_id]),
        ("/orders/{id}", ["GET", "PUT"], [upstreams[2].upstream_id, upstreams[3].upstream_id]),
        ("/products", ["GET"], [upstreams[4].upstream_id]),
        ("/products/{id}", ["GET"], [upstreams[4].upstream_id]),
        ("/payments", ["POST"], [upstreams[5].upstream_id]),
        ("/notifications", ["POST"], [upstreams[6].upstream_id])
    ]
    
    routes = []
    for path, methods, ups_ids in routes_data:
        route = await gateway.create_route(path, methods, ups_ids)
        routes.append(route)
        print(f"  🔀 {path} [{', '.join(methods)}]")
        
    # Create rate limits
    print("\n⏱️ Creating Rate Limits...")
    
    rate_limits_data = [
        ("Standard", RateLimitType.REQUESTS_PER_MINUTE, 100, "consumer"),
        ("Premium", RateLimitType.REQUESTS_PER_MINUTE, 1000, "consumer"),
        ("Free Tier", RateLimitType.REQUESTS_PER_HOUR, 100, "consumer"),
        ("Global", RateLimitType.REQUESTS_PER_SECOND, 10000, "api")
    ]
    
    rate_limits = []
    for name, r_type, value, scope in rate_limits_data:
        rate_limit = await gateway.create_rate_limit(name, r_type, value, scope)
        rate_limits.append(rate_limit)
        print(f"  ⏱️ {name}: {value} {r_type.value}")
        
    # Create caches
    print("\n💾 Creating Caches...")
    
    caches_data = [
        (CachePolicy.PUBLIC, 300, ["Accept", "Accept-Language"]),
        (CachePolicy.PRIVATE, 60, []),
        (CachePolicy.MUST_REVALIDATE, 120, [])
    ]
    
    caches = []
    for policy, ttl, vary in caches_data:
        cache = await gateway.create_cache(policy, ttl, vary)
        caches.append(cache)
        print(f"  💾 {policy.value} (TTL: {ttl}s)")
        
    # Create consumers
    print("\n👤 Creating Consumers...")
    
    consumers_data = [
        ("Mobile App", rate_limits[1].limit_id),  # Premium
        ("Web Frontend", rate_limits[0].limit_id),  # Standard
        ("Partner API", rate_limits[1].limit_id),  # Premium
        ("Free User", rate_limits[2].limit_id),  # Free
        ("Internal Service", rate_limits[0].limit_id)  # Standard
    ]
    
    consumers = []
    for name, rl_id in consumers_data:
        consumer = await gateway.create_consumer(name, rl_id)
        consumers.append(consumer)
        print(f"  👤 {name}: {consumer.api_key[:16]}...")
        
    # Create APIs
    print("\n🔌 Creating APIs...")
    
    apis_data = [
        ("User API", "User management", "v1", "/api/v1/users", AuthType.JWT, LoadBalanceStrategy.ROUND_ROBIN),
        ("Order API", "Order management", "v1", "/api/v1/orders", AuthType.API_KEY, LoadBalanceStrategy.LEAST_CONNECTIONS),
        ("Product API", "Product catalog", "v2", "/api/v2/products", AuthType.NONE, LoadBalanceStrategy.RANDOM),
        ("Payment API", "Payment processing", "v1", "/api/v1/payments", AuthType.OAUTH2, LoadBalanceStrategy.WEIGHTED),
        ("Notification API", "Send notifications", "v1", "/api/v1/notifications", AuthType.API_KEY, LoadBalanceStrategy.ROUND_ROBIN)
    ]
    
    apis = []
    for name, desc, version, base_path, auth, lb in apis_data:
        api = await gateway.create_api(name, desc, version, base_path, auth, lb)
        apis.append(api)
        print(f"  🔌 {name} ({version}) - {auth.value}")
        
    # Add routes to APIs
    await gateway.add_route_to_api(apis[0].api_id, routes[0].route_id)
    await gateway.add_route_to_api(apis[0].api_id, routes[1].route_id)
    await gateway.add_route_to_api(apis[1].api_id, routes[2].route_id)
    await gateway.add_route_to_api(apis[1].api_id, routes[3].route_id)
    await gateway.add_route_to_api(apis[2].api_id, routes[4].route_id)
    await gateway.add_route_to_api(apis[2].api_id, routes[5].route_id)
    await gateway.add_route_to_api(apis[3].api_id, routes[6].route_id)
    await gateway.add_route_to_api(apis[4].api_id, routes[7].route_id)
    
    # Set rate limits and caches
    for api in apis[:3]:
        await gateway.set_rate_limit(api.api_id, rate_limits[3].limit_id)
        await gateway.set_cache(api.api_id, caches[0].cache_id)
        
    # Health checks
    print("\n💚 Running Health Checks...")
    
    for upstream in upstreams:
        await gateway.health_check(upstream.upstream_id)
        
    healthy = sum(1 for u in upstreams if u.is_healthy)
    print(f"  ✓ Healthy: {healthy}/{len(upstreams)}")
    
    # Simulate requests
    print("\n📨 Simulating Requests...")
    
    for _ in range(100):
        api = random.choice(apis)
        consumer = random.choice(consumers)
        method = random.choice(["GET", "POST", "PUT"])
        path = f"/{random.choice(['users', 'orders', 'products'])}/{random.randint(1, 100)}"
        
        await gateway.handle_request(
            api.api_id,
            method,
            path,
            consumer.consumer_id,
            f"192.168.1.{random.randint(1, 255)}"
        )
        
    success = sum(1 for r in gateway.requests if r.status_code == 200)
    errors = sum(1 for r in gateway.requests if r.status_code >= 400)
    print(f"  ✓ Success: {success} | Errors: {errors}")
    
    # API stats
    print("\n📊 API Statistics:")
    
    print("\n  ┌────────────────────────┬──────────┬──────────┬───────────┬────────────────┐")
    print("  │ API                    │ Requests │ Errors   │ Error %   │ Avg Latency    │")
    print("  ├────────────────────────┼──────────┼──────────┼───────────┼────────────────┤")
    
    for api in apis:
        stats = gateway.get_api_stats(api.api_id)
        
        name = stats['name'][:22].ljust(22)
        requests = str(stats['requests']).ljust(8)
        errors = str(stats['errors']).ljust(8)
        error_rate = f"{stats['error_rate']:.1f}%".ljust(9)
        latency = f"{stats['avg_latency_ms']:.1f}ms".ljust(14)
        
        print(f"  │ {name} │ {requests} │ {errors} │ {error_rate} │ {latency} │")
        
    print("  └────────────────────────┴──────────┴──────────┴───────────┴────────────────┘")
    
    # Upstream health
    print("\n🖥️ Upstream Health:")
    
    print("\n  ┌──────────────────────────┬────────────┬──────────┬────────┬────────────────┐")
    print("  │ Upstream                 │ Status     │ Requests │ Errors │ Last Check     │")
    print("  ├──────────────────────────┼────────────┼──────────┼────────┼────────────────┤")
    
    for upstream in upstreams:
        name = upstream.name[:24].ljust(24)
        status = ("✓ Healthy" if upstream.is_healthy else "✗ Unhealthy").ljust(10)
        requests = str(upstream.requests_count).ljust(8)
        errors = str(upstream.errors_count).ljust(6)
        last_check = upstream.last_health_check.strftime('%H:%M:%S') if upstream.last_health_check else "N/A"
        last_check = last_check.ljust(14)
        
        print(f"  │ {name} │ {status} │ {requests} │ {errors} │ {last_check} │")
        
    print("  └──────────────────────────┴────────────┴──────────┴────────┴────────────────┘")
    
    # Consumer stats
    print("\n👤 Consumer Activity:")
    
    for consumer in consumers:
        stats = gateway.get_consumer_stats(consumer.consumer_id)
        
        active = "✓" if stats['is_active'] else "✗"
        last_req = stats['last_request'][:19] if stats['last_request'] else "Never"
        
        print(f"  [{active}] {stats['name']}")
        print(f"      Requests: {stats['requests']} | Last: {last_req}")
        
    # Cache stats
    print("\n💾 Cache Statistics:")
    
    for cache in caches:
        total = cache.hits + cache.misses
        hit_rate = (cache.hits / total * 100) if total > 0 else 0
        
        print(f"  {cache.policy.value}")
        print(f"      Hits: {cache.hits} | Misses: {cache.misses} | Rate: {hit_rate:.1f}%")
        
    # Rate limit status
    print("\n⏱️ Rate Limit Status:")
    
    for rate_limit in rate_limits:
        print(f"  {rate_limit.name}: {rate_limit.limit_value} {rate_limit.limit_type.value}")
        
    # Request distribution by status code
    print("\n📊 Response Status Distribution:")
    
    stats = gateway.get_statistics()
    status_counts = {}
    for r in gateway.requests:
        status_counts[r.status_code] = status_counts.get(r.status_code, 0) + 1
        
    for code, count in sorted(status_counts.items()):
        bar = "█" * min(count // 2, 20) + "░" * (20 - min(count // 2, 20))
        icon = "✓" if code < 400 else "✗"
        print(f"  {icon} {code:3} [{bar}] {count}")
        
    # Statistics
    print("\n📊 Gateway Statistics:")
    
    print(f"\n  Total APIs: {stats['total_apis']}")
    print("  By Status:")
    for status, count in stats['by_status'].items():
        print(f"    {status}: {count}")
        
    print(f"\n  Total Upstreams: {stats['total_upstreams']}")
    print(f"  Healthy: {stats['upstreams_healthy']}")
    
    print(f"\n  Total Routes: {stats['total_routes']}")
    print(f"  Total Consumers: {stats['total_consumers']}")
    print(f"  Active Consumers: {stats['consumers_active']}")
    
    print(f"\n  Total Requests: {stats['total_requests']}")
    print(f"  Avg Latency: {stats['avg_latency_ms']:.2f}ms")
    
    print(f"\n  Cache Hit Rate: {stats['cache_hit_rate']:.1f}%")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    API Gateway Manager Platform                     │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total APIs:                  {stats['total_apis']:>12}                          │")
    print(f"│ Total Upstreams:             {stats['total_upstreams']:>12}                          │")
    print(f"│ Total Requests:              {stats['total_requests']:>12}                          │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Avg Latency:                 {stats['avg_latency_ms']:>10.2f}ms                        │")
    print(f"│ Cache Hit Rate:              {stats['cache_hit_rate']:>10.1f}%                         │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("API Gateway Manager Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
