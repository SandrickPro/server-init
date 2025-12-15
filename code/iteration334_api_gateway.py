#!/usr/bin/env python3
"""
Server Init - Iteration 334: API Gateway Platform
Платформа управления API Gateway

Функционал:
- API Management - управление API
- Route Configuration - конфигурация маршрутов
- Rate Limiting - ограничение скорости
- Authentication - аутентификация (API Key, JWT, OAuth)
- Request/Response Transformation - трансформация запросов
- Caching - кеширование ответов
- Analytics & Monitoring - аналитика и мониторинг
- Plugin System - система плагинов
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import hashlib


class APIStatus(Enum):
    """Статус API"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    BETA = "beta"


class AuthType(Enum):
    """Тип аутентификации"""
    NONE = "none"
    API_KEY = "api_key"
    JWT = "jwt"
    OAUTH2 = "oauth2"
    BASIC = "basic"
    MTLS = "mtls"


class RouteMethod(Enum):
    """HTTP метод"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


class PluginType(Enum):
    """Тип плагина"""
    AUTHENTICATION = "authentication"
    RATE_LIMITING = "rate_limiting"
    TRANSFORMATION = "transformation"
    LOGGING = "logging"
    CACHING = "caching"
    CORS = "cors"
    SECURITY = "security"


class RateLimitStrategy(Enum):
    """Стратегия ограничения"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"


class UpstreamStrategy(Enum):
    """Стратегия upstream"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    LEAST_CONNECTIONS = "least_connections"
    IP_HASH = "ip_hash"
    RANDOM = "random"


@dataclass
class APIKey:
    """API ключ"""
    key_id: str
    key_hash: str
    
    # Owner
    consumer_id: str = ""
    consumer_name: str = ""
    
    # Permissions
    apis: List[str] = field(default_factory=list)
    scopes: List[str] = field(default_factory=list)
    
    # Rate limit
    rate_limit: int = 1000  # requests per minute
    
    # Status
    is_active: bool = True
    
    # Expiry
    expires_at: Optional[datetime] = None
    
    # Usage
    requests_count: int = 0
    last_used_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Consumer:
    """Consumer (потребитель API)"""
    consumer_id: str
    name: str
    
    # Contact
    email: str = ""
    organization: str = ""
    
    # API Keys
    api_key_ids: List[str] = field(default_factory=list)
    
    # Permissions
    allowed_apis: List[str] = field(default_factory=list)
    
    # Rate limit
    rate_limit: int = 10000
    
    # Status
    is_active: bool = True
    
    # Usage
    total_requests: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Upstream:
    """Upstream (backend сервис)"""
    upstream_id: str
    name: str
    
    # Targets
    targets: List[Dict[str, Any]] = field(default_factory=list)  # [{host, port, weight}]
    
    # Strategy
    strategy: UpstreamStrategy = UpstreamStrategy.ROUND_ROBIN
    
    # Health check
    health_check_path: str = "/health"
    health_check_interval: int = 30
    health_threshold: int = 3
    
    # Timeouts
    connect_timeout: int = 10000  # ms
    read_timeout: int = 60000
    write_timeout: int = 60000
    
    # Retries
    retries: int = 3
    
    # Status
    is_healthy: bool = True
    healthy_targets: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Route:
    """Маршрут API"""
    route_id: str
    name: str
    
    # Path
    path: str = ""
    methods: List[RouteMethod] = field(default_factory=list)
    
    # Service
    api_id: str = ""
    upstream_id: str = ""
    
    # Strip path
    strip_path: bool = True
    preserve_host: bool = False
    
    # Regex priority
    regex_priority: int = 0
    
    # Headers
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Query params
    query_params: Dict[str, str] = field(default_factory=dict)
    
    # Protocols
    protocols: List[str] = field(default_factory=lambda: ["https"])
    
    # Status
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class API:
    """API определение"""
    api_id: str
    name: str
    
    # Version
    version: str = "v1"
    
    # Description
    description: str = ""
    
    # Base path
    base_path: str = ""
    
    # Upstream
    upstream_id: str = ""
    
    # Routes
    route_ids: List[str] = field(default_factory=list)
    
    # Authentication
    auth_type: AuthType = AuthType.API_KEY
    
    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit: int = 1000  # per minute
    
    # Caching
    cache_enabled: bool = False
    cache_ttl: int = 300  # seconds
    
    # CORS
    cors_enabled: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    
    # Status
    status: APIStatus = APIStatus.ACTIVE
    
    # Plugins
    plugin_ids: List[str] = field(default_factory=list)
    
    # Documentation
    docs_url: str = ""
    openapi_spec: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Plugin:
    """Плагин"""
    plugin_id: str
    name: str
    
    # Type
    plugin_type: PluginType = PluginType.LOGGING
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Scope
    global_plugin: bool = False
    api_id: str = ""
    route_id: str = ""
    consumer_id: str = ""
    
    # Order
    priority: int = 0
    
    # Status
    is_enabled: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RateLimit:
    """Конфигурация rate limit"""
    limit_id: str
    name: str
    
    # Strategy
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    
    # Limits
    requests_per_second: int = 100
    requests_per_minute: int = 1000
    requests_per_hour: int = 10000
    
    # Burst
    burst_size: int = 200
    
    # Scope
    scope: str = "consumer"  # consumer, api, route, ip, global
    
    # Actions
    action_on_limit: str = "reject"  # reject, queue, throttle
    
    # Response
    limit_exceeded_status: int = 429
    limit_exceeded_message: str = "Rate limit exceeded"
    
    # Headers
    add_headers: bool = True
    
    # Status
    is_enabled: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CacheConfig:
    """Конфигурация кеширования"""
    cache_id: str
    name: str
    
    # TTL
    ttl: int = 300  # seconds
    
    # Scope
    api_id: str = ""
    route_id: str = ""
    
    # Cache key
    vary_by_query: bool = True
    vary_by_headers: List[str] = field(default_factory=list)
    vary_by_consumer: bool = False
    
    # Methods
    cache_methods: List[str] = field(default_factory=lambda: ["GET", "HEAD"])
    
    # Status codes
    cache_status_codes: List[int] = field(default_factory=lambda: [200, 301, 302])
    
    # Max size
    max_size_mb: int = 100
    
    # Status
    is_enabled: bool = True
    
    # Stats
    hits: int = 0
    misses: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RequestLog:
    """Лог запроса"""
    log_id: str
    
    # Request
    api_id: str = ""
    route_id: str = ""
    consumer_id: str = ""
    
    # HTTP
    method: str = ""
    path: str = ""
    query_string: str = ""
    
    # Response
    status_code: int = 0
    response_time_ms: float = 0.0
    response_size: int = 0
    
    # Client
    client_ip: str = ""
    user_agent: str = ""
    
    # Cache
    cache_status: str = ""  # HIT, MISS, BYPASS
    
    # Upstream
    upstream_latency_ms: float = 0.0
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class APIMetrics:
    """Метрики API"""
    metric_id: str
    
    # Target
    api_id: str = ""
    
    # Time
    timestamp: datetime = field(default_factory=datetime.now)
    interval_minutes: int = 5
    
    # Requests
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # By status code
    status_2xx: int = 0
    status_3xx: int = 0
    status_4xx: int = 0
    status_5xx: int = 0
    
    # Latency
    avg_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    
    # Throughput
    requests_per_second: float = 0.0
    bytes_in: int = 0
    bytes_out: int = 0
    
    # Cache
    cache_hits: int = 0
    cache_misses: int = 0
    
    # Rate limiting
    rate_limited_requests: int = 0


class APIGateway:
    """API Gateway"""
    
    def __init__(self):
        self.apis: Dict[str, API] = {}
        self.routes: Dict[str, Route] = {}
        self.upstreams: Dict[str, Upstream] = {}
        self.consumers: Dict[str, Consumer] = {}
        self.api_keys: Dict[str, APIKey] = {}
        self.plugins: Dict[str, Plugin] = {}
        self.rate_limits: Dict[str, RateLimit] = {}
        self.cache_configs: Dict[str, CacheConfig] = {}
        self.request_logs: Dict[str, RequestLog] = {}
        self.metrics: Dict[str, APIMetrics] = {}
        
    async def create_upstream(self, name: str,
                             targets: List[Dict[str, Any]],
                             strategy: UpstreamStrategy = UpstreamStrategy.ROUND_ROBIN,
                             health_check_path: str = "/health") -> Upstream:
        """Создание upstream"""
        upstream = Upstream(
            upstream_id=f"upstream_{uuid.uuid4().hex[:8]}",
            name=name,
            targets=targets,
            strategy=strategy,
            health_check_path=health_check_path,
            healthy_targets=len(targets)
        )
        
        self.upstreams[upstream.upstream_id] = upstream
        return upstream
        
    async def create_api(self, name: str,
                        version: str,
                        base_path: str,
                        upstream_id: str,
                        auth_type: AuthType = AuthType.API_KEY,
                        description: str = "") -> Optional[API]:
        """Создание API"""
        if upstream_id not in self.upstreams:
            return None
            
        api = API(
            api_id=f"api_{uuid.uuid4().hex[:8]}",
            name=name,
            version=version,
            base_path=base_path,
            upstream_id=upstream_id,
            auth_type=auth_type,
            description=description
        )
        
        self.apis[api.api_id] = api
        return api
        
    async def create_route(self, name: str,
                          api_id: str,
                          path: str,
                          methods: List[RouteMethod],
                          strip_path: bool = True) -> Optional[Route]:
        """Создание маршрута"""
        api = self.apis.get(api_id)
        if not api:
            return None
            
        route = Route(
            route_id=f"route_{uuid.uuid4().hex[:8]}",
            name=name,
            path=path,
            methods=methods,
            api_id=api_id,
            upstream_id=api.upstream_id,
            strip_path=strip_path
        )
        
        api.route_ids.append(route.route_id)
        self.routes[route.route_id] = route
        return route
        
    async def create_consumer(self, name: str,
                             email: str,
                             organization: str = "",
                             rate_limit: int = 10000) -> Consumer:
        """Создание consumer"""
        consumer = Consumer(
            consumer_id=f"consumer_{uuid.uuid4().hex[:8]}",
            name=name,
            email=email,
            organization=organization,
            rate_limit=rate_limit
        )
        
        self.consumers[consumer.consumer_id] = consumer
        return consumer
        
    async def create_api_key(self, consumer_id: str,
                            apis: List[str] = None,
                            scopes: List[str] = None,
                            rate_limit: int = 1000,
                            expires_days: int = 365) -> Optional[APIKey]:
        """Создание API ключа"""
        consumer = self.consumers.get(consumer_id)
        if not consumer:
            return None
            
        # Generate key
        raw_key = f"sk_{uuid.uuid4().hex}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        api_key = APIKey(
            key_id=f"key_{uuid.uuid4().hex[:8]}",
            key_hash=key_hash,
            consumer_id=consumer_id,
            consumer_name=consumer.name,
            apis=apis or [],
            scopes=scopes or ["read"],
            rate_limit=rate_limit,
            expires_at=datetime.now() + timedelta(days=expires_days)
        )
        
        consumer.api_key_ids.append(api_key.key_id)
        self.api_keys[api_key.key_id] = api_key
        
        return api_key
        
    async def create_plugin(self, name: str,
                           plugin_type: PluginType,
                           config: Dict[str, Any],
                           api_id: str = "",
                           route_id: str = "",
                           global_plugin: bool = False,
                           priority: int = 0) -> Plugin:
        """Создание плагина"""
        plugin = Plugin(
            plugin_id=f"plugin_{uuid.uuid4().hex[:8]}",
            name=name,
            plugin_type=plugin_type,
            config=config,
            api_id=api_id,
            route_id=route_id,
            global_plugin=global_plugin,
            priority=priority
        )
        
        # Add plugin to API
        if api_id and api_id in self.apis:
            self.apis[api_id].plugin_ids.append(plugin.plugin_id)
            
        self.plugins[plugin.plugin_id] = plugin
        return plugin
        
    async def create_rate_limit(self, name: str,
                               strategy: RateLimitStrategy,
                               rps: int = 100,
                               rpm: int = 1000,
                               scope: str = "consumer") -> RateLimit:
        """Создание rate limit"""
        rate_limit = RateLimit(
            limit_id=f"rl_{uuid.uuid4().hex[:8]}",
            name=name,
            strategy=strategy,
            requests_per_second=rps,
            requests_per_minute=rpm,
            requests_per_hour=rpm * 60,
            scope=scope
        )
        
        self.rate_limits[rate_limit.limit_id] = rate_limit
        return rate_limit
        
    async def create_cache_config(self, name: str,
                                 api_id: str,
                                 ttl: int = 300,
                                 vary_by_query: bool = True) -> Optional[CacheConfig]:
        """Создание конфигурации кеширования"""
        if api_id not in self.apis:
            return None
            
        cache = CacheConfig(
            cache_id=f"cache_{uuid.uuid4().hex[:8]}",
            name=name,
            api_id=api_id,
            ttl=ttl,
            vary_by_query=vary_by_query
        )
        
        self.apis[api_id].cache_enabled = True
        self.apis[api_id].cache_ttl = ttl
        
        self.cache_configs[cache.cache_id] = cache
        return cache
        
    async def log_request(self, api_id: str,
                         route_id: str,
                         consumer_id: str,
                         method: str,
                         path: str,
                         status_code: int,
                         response_time_ms: float,
                         client_ip: str) -> RequestLog:
        """Логирование запроса"""
        log = RequestLog(
            log_id=f"log_{uuid.uuid4().hex[:8]}",
            api_id=api_id,
            route_id=route_id,
            consumer_id=consumer_id,
            method=method,
            path=path,
            status_code=status_code,
            response_time_ms=response_time_ms,
            client_ip=client_ip,
            cache_status=random.choice(["HIT", "MISS", "BYPASS"])
        )
        
        self.request_logs[log.log_id] = log
        
        # Update API key usage
        for key in self.api_keys.values():
            if key.consumer_id == consumer_id:
                key.requests_count += 1
                key.last_used_at = datetime.now()
                
        # Update consumer usage
        consumer = self.consumers.get(consumer_id)
        if consumer:
            consumer.total_requests += 1
            
        return log
        
    async def collect_metrics(self, api_id: str) -> Optional[APIMetrics]:
        """Сбор метрик"""
        api = self.apis.get(api_id)
        if not api:
            return None
            
        # Simulate metrics
        total = random.randint(10000, 100000)
        success = int(total * random.uniform(0.95, 0.999))
        
        metrics = APIMetrics(
            metric_id=f"metrics_{uuid.uuid4().hex[:8]}",
            api_id=api_id,
            total_requests=total,
            successful_requests=success,
            failed_requests=total - success,
            status_2xx=int(total * 0.95),
            status_3xx=int(total * 0.02),
            status_4xx=int(total * 0.025),
            status_5xx=int(total * 0.005),
            avg_latency_ms=random.uniform(20, 100),
            p50_latency_ms=random.uniform(15, 50),
            p95_latency_ms=random.uniform(50, 200),
            p99_latency_ms=random.uniform(100, 500),
            requests_per_second=random.uniform(100, 1000),
            bytes_in=random.randint(1000000, 10000000),
            bytes_out=random.randint(10000000, 100000000),
            cache_hits=random.randint(1000, 10000),
            cache_misses=random.randint(100, 1000),
            rate_limited_requests=random.randint(10, 100)
        )
        
        self.metrics[metrics.metric_id] = metrics
        return metrics
        
    def get_routes_for_api(self, api_id: str) -> List[Route]:
        """Получение маршрутов для API"""
        api = self.apis.get(api_id)
        if not api:
            return []
            
        return [self.routes[rid] for rid in api.route_ids if rid in self.routes]
        
    def get_plugins_for_api(self, api_id: str) -> List[Plugin]:
        """Получение плагинов для API"""
        api = self.apis.get(api_id)
        if not api:
            return []
            
        return [self.plugins[pid] for pid in api.plugin_ids if pid in self.plugins]
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_apis = len(self.apis)
        active_apis = sum(1 for a in self.apis.values() if a.status == APIStatus.ACTIVE)
        
        total_routes = len(self.routes)
        active_routes = sum(1 for r in self.routes.values() if r.is_active)
        
        total_consumers = len(self.consumers)
        active_consumers = sum(1 for c in self.consumers.values() if c.is_active)
        
        total_api_keys = len(self.api_keys)
        active_keys = sum(1 for k in self.api_keys.values() if k.is_active)
        
        total_upstreams = len(self.upstreams)
        healthy_upstreams = sum(1 for u in self.upstreams.values() if u.is_healthy)
        
        total_plugins = len(self.plugins)
        enabled_plugins = sum(1 for p in self.plugins.values() if p.is_enabled)
        
        total_requests = sum(m.total_requests for m in self.metrics.values())
        
        return {
            "total_apis": total_apis,
            "active_apis": active_apis,
            "total_routes": total_routes,
            "active_routes": active_routes,
            "total_consumers": total_consumers,
            "active_consumers": active_consumers,
            "total_api_keys": total_api_keys,
            "active_keys": active_keys,
            "total_upstreams": total_upstreams,
            "healthy_upstreams": healthy_upstreams,
            "total_plugins": total_plugins,
            "enabled_plugins": enabled_plugins,
            "total_requests_logged": total_requests
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 334: API Gateway Platform")
    print("=" * 60)
    
    gateway = APIGateway()
    print("✓ API Gateway created")
    
    # Create upstreams
    print("\n🔗 Creating Upstreams...")
    
    upstreams_data = [
        ("users-service", [
            {"host": "10.0.1.10", "port": 8080, "weight": 100},
            {"host": "10.0.1.11", "port": 8080, "weight": 100},
            {"host": "10.0.1.12", "port": 8080, "weight": 50}
        ], UpstreamStrategy.WEIGHTED),
        ("products-service", [
            {"host": "10.0.2.10", "port": 8080, "weight": 100},
            {"host": "10.0.2.11", "port": 8080, "weight": 100}
        ], UpstreamStrategy.ROUND_ROBIN),
        ("orders-service", [
            {"host": "10.0.3.10", "port": 8080, "weight": 100},
            {"host": "10.0.3.11", "port": 8080, "weight": 100},
            {"host": "10.0.3.12", "port": 8080, "weight": 100}
        ], UpstreamStrategy.LEAST_CONNECTIONS),
        ("payments-service", [
            {"host": "10.0.4.10", "port": 8443, "weight": 100},
            {"host": "10.0.4.11", "port": 8443, "weight": 100}
        ], UpstreamStrategy.IP_HASH),
        ("notifications-service", [
            {"host": "10.0.5.10", "port": 8080, "weight": 100}
        ], UpstreamStrategy.ROUND_ROBIN),
        ("analytics-service", [
            {"host": "10.0.6.10", "port": 8080, "weight": 100},
            {"host": "10.0.6.11", "port": 8080, "weight": 100}
        ], UpstreamStrategy.RANDOM)
    ]
    
    upstreams = []
    for name, targets, strategy in upstreams_data:
        upstream = await gateway.create_upstream(name, targets, strategy)
        upstreams.append(upstream)
        print(f"  🔗 {name} ({len(targets)} targets, {strategy.value})")
        
    # Create APIs
    print("\n📚 Creating APIs...")
    
    apis_data = [
        ("Users API", "v1", "/api/v1/users", upstreams[0].upstream_id, AuthType.JWT, "User management API"),
        ("Products API", "v1", "/api/v1/products", upstreams[1].upstream_id, AuthType.API_KEY, "Product catalog API"),
        ("Orders API", "v1", "/api/v1/orders", upstreams[2].upstream_id, AuthType.JWT, "Order management API"),
        ("Payments API", "v1", "/api/v1/payments", upstreams[3].upstream_id, AuthType.OAUTH2, "Payment processing API"),
        ("Notifications API", "v1", "/api/v1/notifications", upstreams[4].upstream_id, AuthType.API_KEY, "Notification service API"),
        ("Analytics API", "v2", "/api/v2/analytics", upstreams[5].upstream_id, AuthType.JWT, "Analytics and reporting API")
    ]
    
    apis = []
    for name, version, path, upstream_id, auth, desc in apis_data:
        api = await gateway.create_api(name, version, path, upstream_id, auth, desc)
        if api:
            apis.append(api)
            print(f"  📚 {name} {version} ({auth.value})")
            
    # Create routes
    print("\n🛤️ Creating Routes...")
    
    routes_data = [
        # Users API
        (0, "Get Users", "/", [RouteMethod.GET]),
        (0, "Create User", "/", [RouteMethod.POST]),
        (0, "Get User", "/{id}", [RouteMethod.GET]),
        (0, "Update User", "/{id}", [RouteMethod.PUT, RouteMethod.PATCH]),
        (0, "Delete User", "/{id}", [RouteMethod.DELETE]),
        # Products API
        (1, "List Products", "/", [RouteMethod.GET]),
        (1, "Get Product", "/{id}", [RouteMethod.GET]),
        (1, "Create Product", "/", [RouteMethod.POST]),
        (1, "Update Product", "/{id}", [RouteMethod.PUT]),
        (1, "Search Products", "/search", [RouteMethod.GET, RouteMethod.POST]),
        # Orders API
        (2, "List Orders", "/", [RouteMethod.GET]),
        (2, "Create Order", "/", [RouteMethod.POST]),
        (2, "Get Order", "/{id}", [RouteMethod.GET]),
        (2, "Cancel Order", "/{id}/cancel", [RouteMethod.POST]),
        # Payments API
        (3, "Process Payment", "/process", [RouteMethod.POST]),
        (3, "Get Payment Status", "/{id}", [RouteMethod.GET]),
        (3, "Refund Payment", "/{id}/refund", [RouteMethod.POST]),
        # Notifications API
        (4, "Send Notification", "/send", [RouteMethod.POST]),
        (4, "Get Notification", "/{id}", [RouteMethod.GET]),
        # Analytics API
        (5, "Get Analytics", "/", [RouteMethod.GET]),
        (5, "Generate Report", "/report", [RouteMethod.POST])
    ]
    
    routes = []
    for api_idx, name, path, methods in routes_data:
        if api_idx < len(apis):
            route = await gateway.create_route(name, apis[api_idx].api_id, path, methods)
            if route:
                routes.append(route)
                
    print(f"  ✓ Created {len(routes)} routes")
    
    # Create consumers
    print("\n👥 Creating Consumers...")
    
    consumers_data = [
        ("Mobile App", "mobile@example.com", "Example Corp", 50000),
        ("Web Frontend", "web@example.com", "Example Corp", 100000),
        ("Partner Integration", "partner@partner.com", "Partner Inc", 10000),
        ("Internal Services", "internal@example.com", "Example Corp", 200000),
        ("Third Party", "thirdparty@external.com", "External Ltd", 5000),
        ("Analytics Dashboard", "analytics@example.com", "Example Corp", 30000)
    ]
    
    consumers = []
    for name, email, org, rate in consumers_data:
        consumer = await gateway.create_consumer(name, email, org, rate)
        consumers.append(consumer)
        print(f"  👥 {name} ({org})")
        
    # Create API keys
    print("\n🔑 Creating API Keys...")
    
    api_keys = []
    for consumer in consumers:
        # Create API key for each consumer
        key = await gateway.create_api_key(
            consumer.consumer_id,
            apis=[a.api_id for a in apis],
            scopes=["read", "write"],
            rate_limit=consumer.rate_limit
        )
        if key:
            api_keys.append(key)
            print(f"  🔑 Key for {consumer.name}")
            
    # Create plugins
    print("\n🔌 Creating Plugins...")
    
    plugins_data = [
        # Global plugins
        ("Request Logging", PluginType.LOGGING, {"level": "info", "format": "json"}, "", True),
        ("CORS Handler", PluginType.CORS, {"origins": ["*"], "methods": ["GET", "POST", "PUT", "DELETE"]}, "", True),
        # API-specific plugins
        ("JWT Auth", PluginType.AUTHENTICATION, {"issuer": "auth.example.com", "algorithm": "RS256"}, apis[0].api_id, False),
        ("Response Transform", PluginType.TRANSFORMATION, {"add_headers": {"X-API-Version": "v1"}}, apis[1].api_id, False),
        ("Security Headers", PluginType.SECURITY, {"hsts": True, "xss_protection": True}, apis[3].api_id, False),
        ("Response Cache", PluginType.CACHING, {"ttl": 300, "vary": ["Accept"]}, apis[5].api_id, False)
    ]
    
    plugins = []
    for name, ptype, config, api_id, is_global in plugins_data:
        plugin = await gateway.create_plugin(name, ptype, config, api_id, "", is_global)
        plugins.append(plugin)
        scope = "Global" if is_global else "API"
        print(f"  🔌 {name} ({ptype.value}, {scope})")
        
    # Create rate limits
    print("\n⏱️ Creating Rate Limits...")
    
    rate_limits_data = [
        ("Global Limit", RateLimitStrategy.SLIDING_WINDOW, 1000, 10000, "global"),
        ("Consumer Limit", RateLimitStrategy.TOKEN_BUCKET, 100, 1000, "consumer"),
        ("IP Limit", RateLimitStrategy.FIXED_WINDOW, 50, 500, "ip"),
        ("API Limit", RateLimitStrategy.LEAKY_BUCKET, 500, 5000, "api")
    ]
    
    rate_limits = []
    for name, strategy, rps, rpm, scope in rate_limits_data:
        rl = await gateway.create_rate_limit(name, strategy, rps, rpm, scope)
        rate_limits.append(rl)
        print(f"  ⏱️ {name} ({rps} RPS, {strategy.value})")
        
    # Create cache configs
    print("\n💾 Creating Cache Configurations...")
    
    cache_configs_data = [
        ("Products Cache", apis[1].api_id, 600, True),
        ("Analytics Cache", apis[5].api_id, 300, False)
    ]
    
    caches = []
    for name, api_id, ttl, vary in cache_configs_data:
        cache = await gateway.create_cache_config(name, api_id, ttl, vary)
        if cache:
            caches.append(cache)
            print(f"  💾 {name} (TTL: {ttl}s)")
            
    # Simulate request logging
    print("\n📝 Simulating Request Logging...")
    
    for _ in range(100):
        api = random.choice(apis)
        consumer = random.choice(consumers)
        route = random.choice(routes)
        
        await gateway.log_request(
            api.api_id,
            route.route_id,
            consumer.consumer_id,
            random.choice(["GET", "POST", "PUT", "DELETE"]),
            f"{api.base_path}{route.path}",
            random.choices([200, 201, 400, 401, 404, 500], weights=[80, 10, 3, 2, 3, 2])[0],
            random.uniform(10, 500),
            f"10.0.0.{random.randint(1, 255)}"
        )
        
    print(f"  ✓ Logged 100 requests")
    
    # Collect metrics
    print("\n📊 Collecting Metrics...")
    
    metrics = []
    for api in apis:
        metric = await gateway.collect_metrics(api.api_id)
        if metric:
            metrics.append(metric)
            
    print(f"  ✓ Collected metrics for {len(metrics)} APIs")
    
    # Upstreams
    print("\n🔗 Upstreams:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                     │ Strategy         │ Targets │ Healthy │ Connect Timeout │ Status            │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for upstream in upstreams:
        name = upstream.name[:24].ljust(24)
        strategy = upstream.strategy.value[:16].ljust(16)
        targets = str(len(upstream.targets)).ljust(7)
        healthy = str(upstream.healthy_targets).ljust(7)
        timeout = f"{upstream.connect_timeout}ms".ljust(15)
        
        status = "✓ Healthy" if upstream.is_healthy else "✗ Unhealthy"
        status = status[:17].ljust(17)
        
        print(f"  │ {name} │ {strategy} │ {targets} │ {healthy} │ {timeout} │ {status} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # APIs
    print("\n📚 APIs:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                │ Version │ Base Path               │ Auth       │ Rate Limit │ Cache │ Routes │ Plugins │ Status                             │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for api in apis:
        name = api.name[:19].ljust(19)
        version = api.version[:7].ljust(7)
        path = api.base_path[:23].ljust(23)
        auth = api.auth_type.value[:10].ljust(10)
        rate = f"{api.rate_limit}/min".ljust(10)
        cache = "✓" if api.cache_enabled else "✗"
        cache = cache.ljust(5)
        routes_count = str(len(api.route_ids)).ljust(6)
        plugins_count = str(len(api.plugin_ids)).ljust(7)
        
        status_icon = {"active": "✓", "inactive": "○", "deprecated": "⚠", "beta": "β"}.get(api.status.value, "?")
        status = f"{status_icon} {api.status.value}"[:35].ljust(35)
        
        print(f"  │ {name} │ {version} │ {path} │ {auth} │ {rate} │ {cache} │ {routes_count} │ {plugins_count} │ {status} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Routes
    print("\n🛤️ Routes (sample):")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Route Name            │ Path                    │ Methods              │ Strip │ Status              │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for route in routes[:10]:
        name = route.name[:21].ljust(21)
        path = route.path[:23].ljust(23)
        methods = ", ".join(m.value for m in route.methods[:3])[:20].ljust(20)
        strip = "✓" if route.strip_path else "✗"
        strip = strip.ljust(5)
        
        status = "✓ Active" if route.is_active else "○ Inactive"
        status = status[:19].ljust(19)
        
        print(f"  │ {name} │ {path} │ {methods} │ {strip} │ {status} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Consumers
    print("\n👥 Consumers:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                   │ Organization         │ Email                        │ Rate Limit │ Requests │ Status    │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for consumer in consumers:
        name = consumer.name[:22].ljust(22)
        org = consumer.organization[:20].ljust(20)
        email = consumer.email[:28].ljust(28)
        rate = f"{consumer.rate_limit:,}".ljust(10)
        requests = f"{consumer.total_requests:,}".ljust(8)
        
        status = "✓ Active" if consumer.is_active else "○ Inactive"
        status = status[:9].ljust(9)
        
        print(f"  │ {name} │ {org} │ {email} │ {rate} │ {requests} │ {status} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Plugins
    print("\n🔌 Plugins:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                   │ Type             │ Scope    │ Priority │ Status                                 │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for plugin in plugins:
        name = plugin.name[:22].ljust(22)
        ptype = plugin.plugin_type.value[:16].ljust(16)
        scope = "Global" if plugin.global_plugin else "API"
        scope = scope[:8].ljust(8)
        priority = str(plugin.priority).ljust(8)
        
        status = "✓ Enabled" if plugin.is_enabled else "○ Disabled"
        status = status[:38].ljust(38)
        
        print(f"  │ {name} │ {ptype} │ {scope} │ {priority} │ {status} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Rate Limits
    print("\n⏱️ Rate Limits:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                 │ Strategy         │ RPS    │ RPM     │ Scope      │ Status                       │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for rl in rate_limits:
        name = rl.name[:20].ljust(20)
        strategy = rl.strategy.value[:16].ljust(16)
        rps = str(rl.requests_per_second).ljust(6)
        rpm = f"{rl.requests_per_minute:,}".ljust(7)
        scope = rl.scope[:10].ljust(10)
        
        status = "✓ Enabled" if rl.is_enabled else "○ Disabled"
        status = status[:28].ljust(28)
        
        print(f"  │ {name} │ {strategy} │ {rps} │ {rpm} │ {scope} │ {status} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # API Metrics
    print("\n📊 API Metrics:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ API                  │ Requests     │ Success Rate │ Avg Latency │ P95 Latency │ RPS       │ Cache Hits │ Rate Limited                       │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for i, metric in enumerate(metrics):
        if i < len(apis):
            api_name = apis[i].name[:20].ljust(20)
        else:
            api_name = "Unknown"[:20].ljust(20)
            
        requests = f"{metric.total_requests:,}".ljust(12)
        success_rate = f"{(metric.successful_requests/metric.total_requests)*100:.1f}%".ljust(12)
        avg_lat = f"{metric.avg_latency_ms:.1f}ms".ljust(11)
        p95_lat = f"{metric.p95_latency_ms:.1f}ms".ljust(11)
        rps = f"{metric.requests_per_second:.0f}".ljust(9)
        cache = f"{metric.cache_hits:,}".ljust(10)
        limited = f"{metric.rate_limited_requests:,}".ljust(36)
        
        print(f"  │ {api_name} │ {requests} │ {success_rate} │ {avg_lat} │ {p95_lat} │ {rps} │ {cache} │ {limited} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Recent Requests
    print("\n📝 Recent Requests (sample):")
    
    recent_logs = list(gateway.request_logs.values())[-10:]
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Method │ Path                               │ Status │ Response Time │ Cache  │ Client IP                          │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for log in recent_logs:
        method = log.method[:6].ljust(6)
        path = log.path[:36].ljust(36)
        status = str(log.status_code).ljust(6)
        time = f"{log.response_time_ms:.0f}ms".ljust(13)
        cache = log.cache_status[:6].ljust(6)
        ip = log.client_ip[:36].ljust(36)
        
        print(f"  │ {method} │ {path} │ {status} │ {time} │ {cache} │ {ip} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Statistics
    stats = gateway.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  APIs: {stats['active_apis']}/{stats['total_apis']} active")
    print(f"  Routes: {stats['active_routes']}/{stats['total_routes']} active")
    print(f"  Consumers: {stats['active_consumers']}/{stats['total_consumers']} active")
    print(f"  API Keys: {stats['active_keys']}/{stats['total_api_keys']} active")
    print(f"  Upstreams: {stats['healthy_upstreams']}/{stats['total_upstreams']} healthy")
    print(f"  Plugins: {stats['enabled_plugins']}/{stats['total_plugins']} enabled")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                       API Gateway Platform                         │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Active APIs:                  {stats['active_apis']:>12}                      │")
    print(f"│ Active Routes:                {stats['active_routes']:>12}                      │")
    print(f"│ Consumers:                    {stats['active_consumers']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Healthy Upstreams:            {stats['healthy_upstreams']:>12}                      │")
    print(f"│ Active API Keys:              {stats['active_keys']:>12}                      │")
    print(f"│ Enabled Plugins:              {stats['enabled_plugins']:>12}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("API Gateway Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
