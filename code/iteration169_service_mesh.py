#!/usr/bin/env python3
"""
Server Init - Iteration 169: Service Mesh Platform
Платформа сервисной сетки (Service Mesh)

Функционал:
- Service Discovery - обнаружение сервисов
- Load Balancing - балансировка нагрузки
- Traffic Management - управление трафиком
- Circuit Breaker - автоматический выключатель
- Retry Policy - политики повторных попыток
- mTLS - взаимная TLS-аутентификация
- Observability - наблюдаемость
- Traffic Splitting - разделение трафика
"""

import asyncio
import hashlib
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
import uuid
from collections import defaultdict


class ServiceStatus(Enum):
    """Статус сервиса"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class LoadBalancingStrategy(Enum):
    """Стратегия балансировки"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"
    WEIGHTED = "weighted"
    CONSISTENT_HASH = "consistent_hash"


class CircuitState(Enum):
    """Состояние Circuit Breaker"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class TrafficPolicy(Enum):
    """Политика трафика"""
    ALLOW = "allow"
    DENY = "deny"
    RATE_LIMIT = "rate_limit"
    REDIRECT = "redirect"


class TLSMode(Enum):
    """Режим TLS"""
    DISABLE = "disable"
    PERMISSIVE = "permissive"
    STRICT = "strict"
    MUTUAL = "mutual"


@dataclass
class ServiceEndpoint:
    """Эндпоинт сервиса"""
    endpoint_id: str
    host: str = ""
    port: int = 80
    
    # Health
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_health_check: Optional[datetime] = None
    consecutive_failures: int = 0
    
    # Load info
    active_connections: int = 0
    weight: int = 100
    
    # TLS
    tls_enabled: bool = False
    certificate_cn: str = ""
    
    # Metadata
    labels: Dict[str, str] = field(default_factory=dict)
    region: str = ""
    zone: str = ""


@dataclass
class Service:
    """Сервис"""
    service_id: str
    name: str = ""
    namespace: str = "default"
    
    # Endpoints
    endpoints: List[ServiceEndpoint] = field(default_factory=list)
    
    # Port configuration
    service_port: int = 80
    target_port: int = 80
    protocol: str = "HTTP"
    
    # Metadata
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass 
class VirtualService:
    """Виртуальный сервис (для маршрутизации)"""
    vs_id: str
    name: str = ""
    
    # Host matching
    hosts: List[str] = field(default_factory=list)
    
    # Routes
    http_routes: List['HTTPRoute'] = field(default_factory=list)
    
    # Timeout
    timeout_sec: float = 30.0
    
    # Retry
    retries: Optional['RetryPolicy'] = None


@dataclass
class HTTPRoute:
    """HTTP маршрут"""
    route_id: str
    name: str = ""
    
    # Match conditions
    match_uri: str = ""  # prefix, exact, regex
    match_method: str = ""
    match_headers: Dict[str, str] = field(default_factory=dict)
    
    # Destinations
    destinations: List['RouteDestination'] = field(default_factory=list)
    
    # Rewrite
    rewrite_uri: str = ""
    
    # Redirect
    redirect_uri: str = ""
    redirect_code: int = 301
    
    # Timeout override
    timeout_sec: Optional[float] = None
    
    # Fault injection
    fault_delay_ms: int = 0
    fault_abort_percent: float = 0.0


@dataclass
class RouteDestination:
    """Назначение маршрута"""
    service_name: str = ""
    port: int = 80
    weight: int = 100
    
    # Subset (version)
    subset: str = ""


@dataclass
class RetryPolicy:
    """Политика повторных попыток"""
    max_retries: int = 3
    per_try_timeout_sec: float = 10.0
    retry_on: List[str] = field(default_factory=lambda: ["5xx", "connect-failure"])
    backoff_base_interval_ms: int = 25
    backoff_max_interval_ms: int = 250


@dataclass
class CircuitBreaker:
    """Circuit Breaker конфигурация"""
    cb_id: str
    service_name: str = ""
    
    # State
    state: CircuitState = CircuitState.CLOSED
    
    # Thresholds
    failure_threshold: int = 5
    success_threshold: int = 3
    timeout_sec: float = 30.0
    
    # Half-open settings
    half_open_requests: int = 3
    
    # Counters
    failure_count: int = 0
    success_count: int = 0
    
    # Timestamps
    state_changed_at: Optional[datetime] = None
    last_failure: Optional[datetime] = None


@dataclass
class RateLimitConfig:
    """Конфигурация rate limiting"""
    rl_id: str
    service_name: str = ""
    
    # Limits
    requests_per_second: int = 100
    burst_size: int = 200
    
    # Tokens (token bucket)
    tokens: float = 0
    last_update: datetime = field(default_factory=datetime.now)
    
    # Stats
    total_allowed: int = 0
    total_denied: int = 0


@dataclass
class TrafficMirror:
    """Зеркалирование трафика"""
    mirror_id: str
    source_service: str = ""
    mirror_service: str = ""
    percentage: float = 100.0
    
    # Stats
    mirrored_count: int = 0


@dataclass
class ServiceMeshMetrics:
    """Метрики сервисной сетки"""
    service_name: str = ""
    
    # Request metrics
    request_count: int = 0
    success_count: int = 0
    error_count: int = 0
    
    # Latency
    total_latency_ms: float = 0
    min_latency_ms: float = float('inf')
    max_latency_ms: float = 0
    
    # Traffic
    bytes_sent: int = 0
    bytes_received: int = 0
    
    # Circuit breaker
    circuit_open_count: int = 0
    
    # Retry
    retry_count: int = 0


class ServiceRegistry:
    """Реестр сервисов"""
    
    def __init__(self):
        self.services: Dict[str, Service] = {}
        self.endpoints_by_service: Dict[str, List[ServiceEndpoint]] = defaultdict(list)
        
    def register_service(self, service: Service):
        """Регистрация сервиса"""
        key = f"{service.namespace}/{service.name}"
        self.services[key] = service
        
        for endpoint in service.endpoints:
            self.endpoints_by_service[key].append(endpoint)
            
    def deregister_service(self, name: str, namespace: str = "default"):
        """Удаление сервиса"""
        key = f"{namespace}/{name}"
        if key in self.services:
            del self.services[key]
            del self.endpoints_by_service[key]
            
    def get_service(self, name: str, namespace: str = "default") -> Optional[Service]:
        """Получение сервиса"""
        key = f"{namespace}/{name}"
        return self.services.get(key)
        
    def get_healthy_endpoints(self, name: str, namespace: str = "default") -> List[ServiceEndpoint]:
        """Получение здоровых эндпоинтов"""
        key = f"{namespace}/{name}"
        return [
            ep for ep in self.endpoints_by_service.get(key, [])
            if ep.status == ServiceStatus.HEALTHY
        ]
        
    def list_services(self, namespace: str = "") -> List[Service]:
        """Список сервисов"""
        if namespace:
            return [s for s in self.services.values() if s.namespace == namespace]
        return list(self.services.values())


class LoadBalancer:
    """Балансировщик нагрузки"""
    
    def __init__(self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN):
        self.strategy = strategy
        self.round_robin_index: Dict[str, int] = defaultdict(int)
        
    def select_endpoint(self, service_name: str, endpoints: List[ServiceEndpoint], 
                       client_id: str = "") -> Optional[ServiceEndpoint]:
        """Выбор эндпоинта"""
        if not endpoints:
            return None
            
        healthy = [ep for ep in endpoints if ep.status == ServiceStatus.HEALTHY]
        if not healthy:
            return None
            
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin(service_name, healthy)
        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._least_connections(healthy)
        elif self.strategy == LoadBalancingStrategy.RANDOM:
            return random.choice(healthy)
        elif self.strategy == LoadBalancingStrategy.WEIGHTED:
            return self._weighted(healthy)
        elif self.strategy == LoadBalancingStrategy.CONSISTENT_HASH:
            return self._consistent_hash(healthy, client_id)
            
        return healthy[0]
        
    def _round_robin(self, service_name: str, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Round Robin"""
        idx = self.round_robin_index[service_name] % len(endpoints)
        self.round_robin_index[service_name] = idx + 1
        return endpoints[idx]
        
    def _least_connections(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Наименьшее количество соединений"""
        return min(endpoints, key=lambda ep: ep.active_connections)
        
    def _weighted(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Взвешенный выбор"""
        total_weight = sum(ep.weight for ep in endpoints)
        r = random.randint(0, total_weight - 1)
        
        current = 0
        for ep in endpoints:
            current += ep.weight
            if r < current:
                return ep
                
        return endpoints[-1]
        
    def _consistent_hash(self, endpoints: List[ServiceEndpoint], client_id: str) -> ServiceEndpoint:
        """Консистентное хеширование"""
        hash_val = int(hashlib.md5(client_id.encode()).hexdigest(), 16)
        idx = hash_val % len(endpoints)
        return endpoints[idx]


class CircuitBreakerManager:
    """Менеджер Circuit Breaker"""
    
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
        
    def get_or_create(self, service_name: str) -> CircuitBreaker:
        """Получение или создание CB"""
        if service_name not in self.breakers:
            self.breakers[service_name] = CircuitBreaker(
                cb_id=f"cb_{uuid.uuid4().hex[:8]}",
                service_name=service_name
            )
        return self.breakers[service_name]
        
    def can_execute(self, service_name: str) -> bool:
        """Можно ли выполнить запрос"""
        cb = self.get_or_create(service_name)
        
        if cb.state == CircuitState.CLOSED:
            return True
            
        if cb.state == CircuitState.OPEN:
            # Check if timeout passed
            if cb.state_changed_at:
                timeout_end = cb.state_changed_at + timedelta(seconds=cb.timeout_sec)
                if datetime.now() > timeout_end:
                    self._transition(cb, CircuitState.HALF_OPEN)
                    return True
            return False
            
        if cb.state == CircuitState.HALF_OPEN:
            return True
            
        return True
        
    def record_success(self, service_name: str):
        """Запись успеха"""
        cb = self.get_or_create(service_name)
        
        if cb.state == CircuitState.HALF_OPEN:
            cb.success_count += 1
            if cb.success_count >= cb.success_threshold:
                self._transition(cb, CircuitState.CLOSED)
                cb.failure_count = 0
                cb.success_count = 0
        elif cb.state == CircuitState.CLOSED:
            cb.failure_count = 0
            
    def record_failure(self, service_name: str):
        """Запись ошибки"""
        cb = self.get_or_create(service_name)
        cb.last_failure = datetime.now()
        
        if cb.state == CircuitState.HALF_OPEN:
            self._transition(cb, CircuitState.OPEN)
            cb.success_count = 0
        elif cb.state == CircuitState.CLOSED:
            cb.failure_count += 1
            if cb.failure_count >= cb.failure_threshold:
                self._transition(cb, CircuitState.OPEN)
                
    def _transition(self, cb: CircuitBreaker, new_state: CircuitState):
        """Переход состояния"""
        cb.state = new_state
        cb.state_changed_at = datetime.now()


class TrafficManager:
    """Менеджер трафика"""
    
    def __init__(self):
        self.virtual_services: Dict[str, VirtualService] = {}
        self.traffic_mirrors: List[TrafficMirror] = []
        
    def add_virtual_service(self, vs: VirtualService):
        """Добавление виртуального сервиса"""
        self.virtual_services[vs.name] = vs
        
    def add_mirror(self, mirror: TrafficMirror):
        """Добавление зеркалирования"""
        self.traffic_mirrors.append(mirror)
        
    def resolve_route(self, host: str, path: str, method: str = "GET",
                     headers: Dict[str, str] = None) -> Optional[RouteDestination]:
        """Разрешение маршрута"""
        headers = headers or {}
        
        for vs in self.virtual_services.values():
            if host not in vs.hosts and "*" not in vs.hosts:
                continue
                
            for route in vs.http_routes:
                if self._matches_route(route, path, method, headers):
                    return self._select_destination(route.destinations)
                    
        return None
        
    def _matches_route(self, route: HTTPRoute, path: str, method: str, 
                      headers: Dict[str, str]) -> bool:
        """Проверка соответствия маршруту"""
        # URI match
        if route.match_uri:
            if not path.startswith(route.match_uri):
                return False
                
        # Method match
        if route.match_method and route.match_method.upper() != method.upper():
            return False
            
        # Headers match
        for header_name, header_value in route.match_headers.items():
            if headers.get(header_name) != header_value:
                return False
                
        return True
        
    def _select_destination(self, destinations: List[RouteDestination]) -> RouteDestination:
        """Выбор назначения (weighted)"""
        if not destinations:
            return None
            
        if len(destinations) == 1:
            return destinations[0]
            
        total_weight = sum(d.weight for d in destinations)
        r = random.randint(0, total_weight - 1)
        
        current = 0
        for dest in destinations:
            current += dest.weight
            if r < current:
                return dest
                
        return destinations[-1]


class RateLimiter:
    """Rate Limiter"""
    
    def __init__(self):
        self.configs: Dict[str, RateLimitConfig] = {}
        
    def configure(self, service_name: str, rps: int = 100, burst: int = 200):
        """Настройка rate limit"""
        self.configs[service_name] = RateLimitConfig(
            rl_id=f"rl_{uuid.uuid4().hex[:8]}",
            service_name=service_name,
            requests_per_second=rps,
            burst_size=burst,
            tokens=float(burst)
        )
        
    def allow(self, service_name: str) -> bool:
        """Проверка разрешения"""
        if service_name not in self.configs:
            return True
            
        config = self.configs[service_name]
        
        # Token bucket refill
        now = datetime.now()
        elapsed = (now - config.last_update).total_seconds()
        config.tokens = min(
            config.burst_size,
            config.tokens + elapsed * config.requests_per_second
        )
        config.last_update = now
        
        # Check
        if config.tokens >= 1:
            config.tokens -= 1
            config.total_allowed += 1
            return True
        else:
            config.total_denied += 1
            return False


class MetricsCollector:
    """Сборщик метрик"""
    
    def __init__(self):
        self.metrics: Dict[str, ServiceMeshMetrics] = {}
        
    def get_or_create(self, service_name: str) -> ServiceMeshMetrics:
        """Получение или создание метрик"""
        if service_name not in self.metrics:
            self.metrics[service_name] = ServiceMeshMetrics(service_name=service_name)
        return self.metrics[service_name]
        
    def record_request(self, service_name: str, latency_ms: float, 
                      success: bool, bytes_sent: int = 0, bytes_received: int = 0):
        """Запись запроса"""
        m = self.get_or_create(service_name)
        
        m.request_count += 1
        m.total_latency_ms += latency_ms
        m.min_latency_ms = min(m.min_latency_ms, latency_ms)
        m.max_latency_ms = max(m.max_latency_ms, latency_ms)
        m.bytes_sent += bytes_sent
        m.bytes_received += bytes_received
        
        if success:
            m.success_count += 1
        else:
            m.error_count += 1
            
    def record_retry(self, service_name: str):
        """Запись retry"""
        m = self.get_or_create(service_name)
        m.retry_count += 1
        
    def record_circuit_open(self, service_name: str):
        """Запись открытия CB"""
        m = self.get_or_create(service_name)
        m.circuit_open_count += 1
        
    def get_avg_latency(self, service_name: str) -> float:
        """Средняя задержка"""
        m = self.metrics.get(service_name)
        if not m or m.request_count == 0:
            return 0
        return m.total_latency_ms / m.request_count


class ServiceMeshPlatform:
    """Платформа Service Mesh"""
    
    def __init__(self):
        self.registry = ServiceRegistry()
        self.load_balancer = LoadBalancer(LoadBalancingStrategy.ROUND_ROBIN)
        self.circuit_breaker = CircuitBreakerManager()
        self.traffic_manager = TrafficManager()
        self.rate_limiter = RateLimiter()
        self.metrics = MetricsCollector()
        
    async def proxy_request(self, service_name: str, path: str = "/", 
                           method: str = "GET", client_id: str = "") -> Dict:
        """Проксирование запроса"""
        start_time = datetime.now()
        
        # Rate limiting
        if not self.rate_limiter.allow(service_name):
            return {"status": 429, "error": "Rate limit exceeded"}
            
        # Circuit breaker check
        if not self.circuit_breaker.can_execute(service_name):
            self.metrics.record_circuit_open(service_name)
            return {"status": 503, "error": "Circuit breaker open"}
            
        # Get endpoints
        endpoints = self.registry.get_healthy_endpoints(service_name)
        
        if not endpoints:
            return {"status": 503, "error": "No healthy endpoints"}
            
        # Load balance
        endpoint = self.load_balancer.select_endpoint(service_name, endpoints, client_id)
        
        if not endpoint:
            return {"status": 503, "error": "No endpoint selected"}
            
        # Simulate request
        endpoint.active_connections += 1
        
        try:
            # Simulate latency
            latency_ms = random.uniform(10, 100)
            await asyncio.sleep(latency_ms / 1000)
            
            # Simulate success/failure (95% success rate)
            success = random.random() < 0.95
            
            if success:
                self.circuit_breaker.record_success(service_name)
                self.metrics.record_request(service_name, latency_ms, True)
                
                return {
                    "status": 200,
                    "endpoint": f"{endpoint.host}:{endpoint.port}",
                    "latency_ms": latency_ms
                }
            else:
                self.circuit_breaker.record_failure(service_name)
                self.metrics.record_request(service_name, latency_ms, False)
                
                return {"status": 500, "error": "Backend error"}
                
        finally:
            endpoint.active_connections -= 1
            
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        return {
            "total_services": len(self.registry.services),
            "total_endpoints": sum(len(eps) for eps in self.registry.endpoints_by_service.values()),
            "virtual_services": len(self.traffic_manager.virtual_services),
            "circuit_breakers": len(self.circuit_breaker.breakers),
            "rate_limit_configs": len(self.rate_limiter.configs)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 169: Service Mesh Platform")
    print("=" * 60)
    
    async def demo():
        mesh = ServiceMeshPlatform()
        print("✓ Service Mesh Platform created")
        
        # Register services
        print("\n📡 Registering Services...")
        
        # API Gateway service
        api_gateway = Service(
            service_id="svc_api_gw",
            name="api-gateway",
            namespace="default",
            service_port=8080,
            endpoints=[
                ServiceEndpoint(
                    endpoint_id="ep_1",
                    host="10.0.1.10",
                    port=8080,
                    status=ServiceStatus.HEALTHY,
                    weight=100,
                    labels={"version": "v1"}
                ),
                ServiceEndpoint(
                    endpoint_id="ep_2",
                    host="10.0.1.11",
                    port=8080,
                    status=ServiceStatus.HEALTHY,
                    weight=100,
                    labels={"version": "v1"}
                ),
            ],
            labels={"app": "api-gateway", "tier": "frontend"}
        )
        mesh.registry.register_service(api_gateway)
        print(f"  ✓ api-gateway ({len(api_gateway.endpoints)} endpoints)")
        
        # User service
        user_service = Service(
            service_id="svc_user",
            name="user-service",
            namespace="default",
            service_port=8081,
            endpoints=[
                ServiceEndpoint(
                    endpoint_id="ep_3",
                    host="10.0.2.10",
                    port=8081,
                    status=ServiceStatus.HEALTHY,
                    weight=100,
                    labels={"version": "v1"}
                ),
                ServiceEndpoint(
                    endpoint_id="ep_4",
                    host="10.0.2.11",
                    port=8081,
                    status=ServiceStatus.HEALTHY,
                    weight=50,  # Lower weight
                    labels={"version": "v2"}  # Canary
                ),
            ],
            labels={"app": "user-service", "tier": "backend"}
        )
        mesh.registry.register_service(user_service)
        print(f"  ✓ user-service ({len(user_service.endpoints)} endpoints)")
        
        # Order service
        order_service = Service(
            service_id="svc_order",
            name="order-service",
            namespace="default",
            service_port=8082,
            endpoints=[
                ServiceEndpoint(
                    endpoint_id="ep_5",
                    host="10.0.3.10",
                    port=8082,
                    status=ServiceStatus.HEALTHY
                ),
                ServiceEndpoint(
                    endpoint_id="ep_6",
                    host="10.0.3.11",
                    port=8082,
                    status=ServiceStatus.UNHEALTHY  # Will be excluded
                ),
                ServiceEndpoint(
                    endpoint_id="ep_7",
                    host="10.0.3.12",
                    port=8082,
                    status=ServiceStatus.HEALTHY
                ),
            ],
            labels={"app": "order-service", "tier": "backend"}
        )
        mesh.registry.register_service(order_service)
        print(f"  ✓ order-service ({len(order_service.endpoints)} endpoints, 1 unhealthy)")
        
        # Setup rate limiting
        print("\n⚡ Configuring Rate Limits...")
        
        mesh.rate_limiter.configure("api-gateway", rps=100, burst=200)
        mesh.rate_limiter.configure("user-service", rps=50, burst=100)
        mesh.rate_limiter.configure("order-service", rps=30, burst=60)
        
        print("  ✓ Rate limits configured")
        
        # Setup virtual services
        print("\n🔀 Configuring Virtual Services...")
        
        vs = VirtualService(
            vs_id="vs_main",
            name="main-routing",
            hosts=["api.example.com", "*"],
            http_routes=[
                HTTPRoute(
                    route_id="route_users",
                    name="user-routes",
                    match_uri="/api/users",
                    destinations=[
                        RouteDestination(service_name="user-service", weight=90, subset="v1"),
                        RouteDestination(service_name="user-service", weight=10, subset="v2"),  # Canary
                    ]
                ),
                HTTPRoute(
                    route_id="route_orders",
                    name="order-routes",
                    match_uri="/api/orders",
                    destinations=[
                        RouteDestination(service_name="order-service", weight=100)
                    ]
                ),
            ],
            retries=RetryPolicy(max_retries=3, retry_on=["5xx", "connect-failure"])
        )
        mesh.traffic_manager.add_virtual_service(vs)
        print(f"  ✓ Virtual service: {vs.name} ({len(vs.http_routes)} routes)")
        
        # Display registered services
        print("\n📋 Registered Services:")
        
        services = mesh.registry.list_services()
        
        print("\n  ┌──────────────────────────────────────────────────────────────────────────────────┐")
        print("  │ Service          │ Namespace │ Port │ Endpoints │ Healthy │")
        print("  ├──────────────────────────────────────────────────────────────────────────────────┤")
        
        for svc in services:
            name = svc.name[:16].ljust(16)
            ns = svc.namespace[:9].ljust(9)
            healthy = len(mesh.registry.get_healthy_endpoints(svc.name, svc.namespace))
            total = len(svc.endpoints)
            print(f"  │ {name} │ {ns} │ {svc.service_port:>4} │ {total:>9} │ {healthy:>7} │")
            
        print("  └──────────────────────────────────────────────────────────────────────────────────┘")
        
        # Send traffic
        print("\n🚀 Simulating Traffic...")
        
        services_to_test = ["api-gateway", "user-service", "order-service"]
        
        for service in services_to_test:
            print(f"\n  Testing {service}...")
            
            for i in range(10):
                result = await mesh.proxy_request(
                    service,
                    path=f"/api/test/{i}",
                    client_id=f"client_{i % 3}"
                )
                
                status = result.get("status")
                if status == 200:
                    endpoint = result.get("endpoint", "")
                    latency = result.get("latency_ms", 0)
                    print(f"    ✓ Request {i+1}: {endpoint} ({latency:.1f}ms)")
                else:
                    error = result.get("error", "Unknown")
                    print(f"    ✗ Request {i+1}: {status} - {error}")
                    
        # Circuit Breaker demonstration
        print("\n🔌 Circuit Breaker States:")
        
        print("\n  ┌────────────────────────────────────────────────────────────────┐")
        print("  │ Service          │ State      │ Failures │ Successes │")
        print("  ├────────────────────────────────────────────────────────────────┤")
        
        for service_name, cb in mesh.circuit_breaker.breakers.items():
            name = service_name[:16].ljust(16)
            state = cb.state.value[:10].ljust(10)
            print(f"  │ {name} │ {state} │ {cb.failure_count:>8} │ {cb.success_count:>9} │")
            
        print("  └────────────────────────────────────────────────────────────────┘")
        
        # Metrics
        print("\n📊 Service Metrics:")
        
        print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────┐")
        print("  │ Service          │ Requests │ Success │ Errors │ Avg Latency │ Retries │")
        print("  ├──────────────────────────────────────────────────────────────────────────────────────────┤")
        
        for service_name, m in mesh.metrics.metrics.items():
            name = service_name[:16].ljust(16)
            avg_lat = mesh.metrics.get_avg_latency(service_name)
            print(f"  │ {name} │ {m.request_count:>8} │ {m.success_count:>7} │ {m.error_count:>6} │ {avg_lat:>10.1f}ms │ {m.retry_count:>7} │")
            
        print("  └──────────────────────────────────────────────────────────────────────────────────────────┘")
        
        # Rate Limiter stats
        print("\n⚡ Rate Limiter Statistics:")
        
        print("\n  ┌────────────────────────────────────────────────────────────────────────┐")
        print("  │ Service          │ RPS Limit │ Allowed │ Denied │ Tokens │")
        print("  ├────────────────────────────────────────────────────────────────────────┤")
        
        for service_name, config in mesh.rate_limiter.configs.items():
            name = service_name[:16].ljust(16)
            tokens = f"{config.tokens:.1f}"
            print(f"  │ {name} │ {config.requests_per_second:>9} │ {config.total_allowed:>7} │ {config.total_denied:>6} │ {tokens:>6} │")
            
        print("  └────────────────────────────────────────────────────────────────────────┘")
        
        # Load balancing demonstration
        print("\n⚖️ Load Balancing (Round Robin):")
        
        user_endpoints = mesh.registry.get_healthy_endpoints("user-service")
        
        print(f"\n  User Service endpoints: {len(user_endpoints)}")
        
        distribution = defaultdict(int)
        for i in range(100):
            ep = mesh.load_balancer.select_endpoint("user-service", user_endpoints)
            distribution[f"{ep.host}:{ep.port}"] += 1
            
        for endpoint, count in sorted(distribution.items()):
            bar = "█" * (count // 5)
            print(f"    {endpoint}: {bar} {count}%")
            
        # Platform statistics
        print("\n📈 Platform Statistics:")
        
        stats = mesh.get_statistics()
        
        print(f"\n  Total Services: {stats['total_services']}")
        print(f"  Total Endpoints: {stats['total_endpoints']}")
        print(f"  Virtual Services: {stats['virtual_services']}")
        print(f"  Circuit Breakers: {stats['circuit_breakers']}")
        print(f"  Rate Limit Configs: {stats['rate_limit_configs']}")
        
        # Dashboard
        print("\n┌────────────────────────────────────────────────────────────────────┐")
        print("│                    Service Mesh Dashboard                          │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Registered Services:         {stats['total_services']:>10}                       │")
        print(f"│ Active Endpoints:            {stats['total_endpoints']:>10}                       │")
        print(f"│ Virtual Services:            {stats['virtual_services']:>10}                       │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Load Balancing:              Round Robin                          │")
        print(f"│ Circuit Breakers Active:     {stats['circuit_breakers']:>10}                       │")
        print(f"│ Rate Limiting Configs:       {stats['rate_limit_configs']:>10}                       │")
        print("└────────────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Service Mesh Platform initialized!")
    print("=" * 60)
