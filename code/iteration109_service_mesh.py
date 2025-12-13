#!/usr/bin/env python3
"""
Server Init - Iteration 109: Service Mesh Platform
Платформа сервисной сетки

Функционал:
- Traffic Management - управление трафиком
- Service Discovery - обнаружение сервисов
- Load Balancing - балансировка нагрузки
- Circuit Breaking - размыкание цепи
- Retry Policies - политики повторов
- mTLS - взаимная аутентификация
- Observability - наблюдаемость
- Rate Limiting - ограничение запросов
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
from collections import defaultdict
import uuid
import random


class LoadBalancerAlgorithm(Enum):
    """Алгоритм балансировки"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"
    WEIGHTED = "weighted"
    CONSISTENT_HASH = "consistent_hash"


class CircuitState(Enum):
    """Состояние circuit breaker"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class ProtocolType(Enum):
    """Тип протокола"""
    HTTP = "http"
    HTTPS = "https"
    GRPC = "grpc"
    TCP = "tcp"


class TrafficPolicy(Enum):
    """Политика трафика"""
    ALLOW = "allow"
    DENY = "deny"
    RATE_LIMIT = "rate_limit"


@dataclass
class ServiceEndpoint:
    """Эндпоинт сервиса"""
    endpoint_id: str
    
    # Address
    address: str = ""
    port: int = 80
    
    # Health
    healthy: bool = True
    last_health_check: datetime = field(default_factory=datetime.now)
    
    # Metadata
    labels: Dict[str, str] = field(default_factory=dict)
    weight: int = 100
    
    # Stats
    active_connections: int = 0
    total_requests: int = 0
    failed_requests: int = 0


@dataclass
class Service:
    """Сервис"""
    service_id: str
    name: str = ""
    namespace: str = "default"
    
    # Endpoints
    endpoints: List[ServiceEndpoint] = field(default_factory=list)
    
    # Protocol
    protocol: ProtocolType = ProtocolType.HTTP
    
    # Port
    port: int = 80
    target_port: int = 8080
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Status
    healthy_endpoints: int = 0


@dataclass
class VirtualService:
    """Виртуальный сервис"""
    vs_id: str
    name: str = ""
    
    # Hosts
    hosts: List[str] = field(default_factory=list)
    
    # Routes
    routes: List[Dict[str, Any]] = field(default_factory=list)
    
    # Traffic split
    traffic_split: Dict[str, int] = field(default_factory=dict)  # version -> percentage
    
    # Timeout
    timeout_seconds: int = 30
    
    # Retries
    retries: int = 3
    retry_on: List[str] = field(default_factory=lambda: ["5xx", "reset", "connect-failure"])


@dataclass
class DestinationRule:
    """Правило назначения"""
    rule_id: str
    
    # Host
    host: str = ""
    
    # Load balancing
    load_balancer: LoadBalancerAlgorithm = LoadBalancerAlgorithm.ROUND_ROBIN
    
    # Connection pool
    max_connections: int = 100
    max_requests_per_connection: int = 1000
    
    # Circuit breaker
    circuit_breaker_enabled: bool = True
    consecutive_errors: int = 5
    interval_seconds: int = 10
    base_ejection_time_seconds: int = 30
    
    # TLS
    tls_mode: str = "ISTIO_MUTUAL"  # DISABLE, SIMPLE, MUTUAL, ISTIO_MUTUAL
    
    # Subsets
    subsets: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class CircuitBreaker:
    """Circuit Breaker"""
    breaker_id: str
    service_name: str = ""
    
    # State
    state: CircuitState = CircuitState.CLOSED
    
    # Thresholds
    failure_threshold: int = 5
    success_threshold: int = 3
    
    # Counters
    failure_count: int = 0
    success_count: int = 0
    
    # Timing
    timeout_seconds: int = 30
    last_failure: Optional[datetime] = None
    opened_at: Optional[datetime] = None


@dataclass
class RateLimitRule:
    """Правило ограничения запросов"""
    rule_id: str
    
    # Target
    service: str = ""
    
    # Limits
    requests_per_second: int = 100
    burst_size: int = 200
    
    # Scope
    per_source: bool = False
    
    # Current state
    current_count: int = 0
    window_start: datetime = field(default_factory=datetime.now)


@dataclass
class MTLSConfig:
    """Конфигурация mTLS"""
    config_id: str
    
    # Mode
    mode: str = "STRICT"  # DISABLE, PERMISSIVE, STRICT
    
    # Namespaces
    namespaces: List[str] = field(default_factory=list)
    
    # Certificate
    cert_chain: str = ""
    private_key_ref: str = ""
    root_cert: str = ""
    
    # Rotation
    rotation_interval_hours: int = 24


@dataclass
class TrafficMetrics:
    """Метрики трафика"""
    service: str = ""
    
    # Request metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # Latency
    avg_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    
    # Throughput
    requests_per_second: float = 0.0
    bytes_in: int = 0
    bytes_out: int = 0
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)


class ServiceRegistry:
    """Реестр сервисов"""
    
    def __init__(self):
        self.services: Dict[str, Service] = {}
        
    def register(self, name: str, namespace: str = "default",
                  protocol: ProtocolType = ProtocolType.HTTP,
                  port: int = 80) -> Service:
        """Регистрация сервиса"""
        service = Service(
            service_id=f"svc_{uuid.uuid4().hex[:8]}",
            name=name,
            namespace=namespace,
            protocol=protocol,
            port=port
        )
        key = f"{namespace}/{name}"
        self.services[key] = service
        return service
        
    def add_endpoint(self, service_key: str, address: str,
                      port: int, weight: int = 100,
                      labels: Dict[str, str] = None) -> Optional[ServiceEndpoint]:
        """Добавление эндпоинта"""
        service = self.services.get(service_key)
        if not service:
            return None
            
        endpoint = ServiceEndpoint(
            endpoint_id=f"ep_{uuid.uuid4().hex[:8]}",
            address=address,
            port=port,
            weight=weight,
            labels=labels or {}
        )
        service.endpoints.append(endpoint)
        return endpoint
        
    def health_check(self, service_key: str) -> Dict[str, Any]:
        """Проверка здоровья"""
        service = self.services.get(service_key)
        if not service:
            return {"status": "not_found"}
            
        healthy = 0
        for endpoint in service.endpoints:
            # Simulate health check
            endpoint.healthy = random.random() > 0.1
            endpoint.last_health_check = datetime.now()
            if endpoint.healthy:
                healthy += 1
                
        service.healthy_endpoints = healthy
        
        return {
            "service": service_key,
            "total_endpoints": len(service.endpoints),
            "healthy_endpoints": healthy,
            "status": "healthy" if healthy > 0 else "unhealthy"
        }
        
    def discover(self, labels: Dict[str, str] = None) -> List[Service]:
        """Обнаружение сервисов"""
        if not labels:
            return list(self.services.values())
            
        result = []
        for service in self.services.values():
            if all(service.labels.get(k) == v for k, v in labels.items()):
                result.append(service)
                
        return result


class LoadBalancer:
    """Балансировщик нагрузки"""
    
    def __init__(self):
        self.counters: Dict[str, int] = defaultdict(int)
        
    def select_endpoint(self, endpoints: List[ServiceEndpoint],
                         algorithm: LoadBalancerAlgorithm) -> Optional[ServiceEndpoint]:
        """Выбор эндпоинта"""
        healthy = [e for e in endpoints if e.healthy]
        if not healthy:
            return None
            
        if algorithm == LoadBalancerAlgorithm.ROUND_ROBIN:
            return self._round_robin(healthy)
        elif algorithm == LoadBalancerAlgorithm.LEAST_CONNECTIONS:
            return self._least_connections(healthy)
        elif algorithm == LoadBalancerAlgorithm.RANDOM:
            return random.choice(healthy)
        elif algorithm == LoadBalancerAlgorithm.WEIGHTED:
            return self._weighted(healthy)
        else:
            return random.choice(healthy)
            
    def _round_robin(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Round Robin"""
        key = endpoints[0].endpoint_id[:4]
        idx = self.counters[key] % len(endpoints)
        self.counters[key] += 1
        return endpoints[idx]
        
    def _least_connections(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Least Connections"""
        return min(endpoints, key=lambda e: e.active_connections)
        
    def _weighted(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Weighted"""
        total_weight = sum(e.weight for e in endpoints)
        r = random.uniform(0, total_weight)
        
        current = 0
        for endpoint in endpoints:
            current += endpoint.weight
            if r <= current:
                return endpoint
                
        return endpoints[-1]


class CircuitBreakerManager:
    """Менеджер circuit breakers"""
    
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
        
    def get_or_create(self, service_name: str) -> CircuitBreaker:
        """Получение или создание"""
        if service_name not in self.breakers:
            self.breakers[service_name] = CircuitBreaker(
                breaker_id=f"cb_{uuid.uuid4().hex[:8]}",
                service_name=service_name
            )
        return self.breakers[service_name]
        
    def record_success(self, service_name: str) -> None:
        """Запись успеха"""
        breaker = self.get_or_create(service_name)
        
        if breaker.state == CircuitState.HALF_OPEN:
            breaker.success_count += 1
            if breaker.success_count >= breaker.success_threshold:
                breaker.state = CircuitState.CLOSED
                breaker.failure_count = 0
                breaker.success_count = 0
                
    def record_failure(self, service_name: str) -> None:
        """Запись ошибки"""
        breaker = self.get_or_create(service_name)
        breaker.failure_count += 1
        breaker.last_failure = datetime.now()
        
        if breaker.state == CircuitState.CLOSED:
            if breaker.failure_count >= breaker.failure_threshold:
                breaker.state = CircuitState.OPEN
                breaker.opened_at = datetime.now()
        elif breaker.state == CircuitState.HALF_OPEN:
            breaker.state = CircuitState.OPEN
            breaker.opened_at = datetime.now()
            
    def can_execute(self, service_name: str) -> bool:
        """Можно ли выполнить запрос"""
        breaker = self.get_or_create(service_name)
        
        if breaker.state == CircuitState.CLOSED:
            return True
        elif breaker.state == CircuitState.OPEN:
            # Check if timeout passed
            if breaker.opened_at:
                elapsed = (datetime.now() - breaker.opened_at).total_seconds()
                if elapsed >= breaker.timeout_seconds:
                    breaker.state = CircuitState.HALF_OPEN
                    breaker.success_count = 0
                    return True
            return False
        else:  # HALF_OPEN
            return True


class RateLimiter:
    """Ограничитель запросов"""
    
    def __init__(self):
        self.rules: Dict[str, RateLimitRule] = {}
        
    def add_rule(self, service: str, rps: int, burst: int = None) -> RateLimitRule:
        """Добавление правила"""
        rule = RateLimitRule(
            rule_id=f"rl_{uuid.uuid4().hex[:8]}",
            service=service,
            requests_per_second=rps,
            burst_size=burst or rps * 2
        )
        self.rules[service] = rule
        return rule
        
    def allow(self, service: str) -> bool:
        """Проверка разрешения"""
        rule = self.rules.get(service)
        if not rule:
            return True
            
        now = datetime.now()
        elapsed = (now - rule.window_start).total_seconds()
        
        if elapsed >= 1.0:
            # Reset window
            rule.window_start = now
            rule.current_count = 0
            
        if rule.current_count < rule.requests_per_second:
            rule.current_count += 1
            return True
        elif rule.current_count < rule.burst_size:
            rule.current_count += 1
            return True
        else:
            return False


class TrafficManager:
    """Менеджер трафика"""
    
    def __init__(self, registry: ServiceRegistry, load_balancer: LoadBalancer,
                  circuit_breaker_mgr: CircuitBreakerManager, rate_limiter: RateLimiter):
        self.registry = registry
        self.load_balancer = load_balancer
        self.circuit_breaker = circuit_breaker_mgr
        self.rate_limiter = rate_limiter
        
        self.virtual_services: Dict[str, VirtualService] = {}
        self.destination_rules: Dict[str, DestinationRule] = {}
        self.metrics: Dict[str, TrafficMetrics] = defaultdict(TrafficMetrics)
        
    def create_virtual_service(self, name: str, hosts: List[str],
                                traffic_split: Dict[str, int] = None) -> VirtualService:
        """Создание виртуального сервиса"""
        vs = VirtualService(
            vs_id=f"vs_{uuid.uuid4().hex[:8]}",
            name=name,
            hosts=hosts,
            traffic_split=traffic_split or {}
        )
        self.virtual_services[name] = vs
        return vs
        
    def create_destination_rule(self, host: str,
                                  lb_algorithm: LoadBalancerAlgorithm,
                                  **kwargs) -> DestinationRule:
        """Создание правила назначения"""
        rule = DestinationRule(
            rule_id=f"dr_{uuid.uuid4().hex[:8]}",
            host=host,
            load_balancer=lb_algorithm,
            **kwargs
        )
        self.destination_rules[host] = rule
        return rule
        
    async def route_request(self, service_key: str,
                             request: Dict[str, Any]) -> Dict[str, Any]:
        """Маршрутизация запроса"""
        # Check rate limit
        if not self.rate_limiter.allow(service_key):
            return {"status": 429, "error": "Rate limit exceeded"}
            
        # Check circuit breaker
        if not self.circuit_breaker.can_execute(service_key):
            return {"status": 503, "error": "Circuit breaker open"}
            
        # Get service
        service = self.registry.services.get(service_key)
        if not service:
            return {"status": 404, "error": "Service not found"}
            
        # Get destination rule
        rule = self.destination_rules.get(service_key)
        algorithm = rule.load_balancer if rule else LoadBalancerAlgorithm.ROUND_ROBIN
        
        # Select endpoint
        endpoint = self.load_balancer.select_endpoint(service.endpoints, algorithm)
        if not endpoint:
            return {"status": 503, "error": "No healthy endpoints"}
            
        # Simulate request
        await asyncio.sleep(0.01)
        success = random.random() > 0.05
        
        # Update metrics
        metrics = self.metrics[service_key]
        metrics.service = service_key
        metrics.total_requests += 1
        
        if success:
            metrics.successful_requests += 1
            self.circuit_breaker.record_success(service_key)
            endpoint.total_requests += 1
            return {
                "status": 200,
                "endpoint": f"{endpoint.address}:{endpoint.port}",
                "latency_ms": random.uniform(10, 100)
            }
        else:
            metrics.failed_requests += 1
            self.circuit_breaker.record_failure(service_key)
            endpoint.failed_requests += 1
            return {"status": 500, "error": "Request failed"}


class ServiceMeshPlatform:
    """Платформа сервисной сетки"""
    
    def __init__(self):
        self.registry = ServiceRegistry()
        self.load_balancer = LoadBalancer()
        self.circuit_breaker_mgr = CircuitBreakerManager()
        self.rate_limiter = RateLimiter()
        self.traffic_manager = TrafficManager(
            self.registry, self.load_balancer,
            self.circuit_breaker_mgr, self.rate_limiter
        )
        
        self.mtls_configs: Dict[str, MTLSConfig] = {}
        
    def configure_mtls(self, mode: str = "STRICT",
                        namespaces: List[str] = None) -> MTLSConfig:
        """Настройка mTLS"""
        config = MTLSConfig(
            config_id=f"mtls_{uuid.uuid4().hex[:8]}",
            mode=mode,
            namespaces=namespaces or ["default"]
        )
        self.mtls_configs[config.config_id] = config
        return config
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        services = list(self.registry.services.values())
        total_endpoints = sum(len(s.endpoints) for s in services)
        healthy_endpoints = sum(s.healthy_endpoints for s in services)
        
        breakers = self.circuit_breaker_mgr.breakers
        open_circuits = len([b for b in breakers.values() if b.state == CircuitState.OPEN])
        
        total_requests = sum(m.total_requests for m in self.traffic_manager.metrics.values())
        failed_requests = sum(m.failed_requests for m in self.traffic_manager.metrics.values())
        
        return {
            "services": len(services),
            "total_endpoints": total_endpoints,
            "healthy_endpoints": healthy_endpoints,
            "virtual_services": len(self.traffic_manager.virtual_services),
            "destination_rules": len(self.traffic_manager.destination_rules),
            "circuit_breakers": len(breakers),
            "open_circuits": open_circuits,
            "rate_limit_rules": len(self.rate_limiter.rules),
            "mtls_configs": len(self.mtls_configs),
            "total_requests": total_requests,
            "failed_requests": failed_requests,
            "success_rate": ((total_requests - failed_requests) / total_requests * 100) if total_requests else 100
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 109: Service Mesh Platform")
    print("=" * 60)
    
    async def demo():
        platform = ServiceMeshPlatform()
        print("✓ Service Mesh Platform created")
        
        # Register services
        print("\n📦 Registering Services...")
        
        services_data = [
            ("api-gateway", "production", ProtocolType.HTTP, 80),
            ("auth-service", "production", ProtocolType.GRPC, 9090),
            ("user-service", "production", ProtocolType.HTTP, 8080),
            ("order-service", "production", ProtocolType.HTTP, 8080),
            ("payment-service", "production", ProtocolType.HTTPS, 443),
            ("notification-service", "production", ProtocolType.HTTP, 8080)
        ]
        
        for name, ns, proto, port in services_data:
            svc = platform.registry.register(name, ns, proto, port)
            key = f"{ns}/{name}"
            
            # Add endpoints
            for i in range(3):
                platform.registry.add_endpoint(
                    key,
                    f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}",
                    8080 + i,
                    weight=100,
                    labels={"version": f"v{random.randint(1, 3)}"}
                )
                
            # Health check
            health = platform.registry.health_check(key)
            status_icon = "✅" if health["status"] == "healthy" else "❌"
            print(f"  {status_icon} {name}: {health['healthy_endpoints']}/{health['total_endpoints']} healthy")
            
        # Create virtual services
        print("\n🌐 Creating Virtual Services...")
        
        vs1 = platform.traffic_manager.create_virtual_service(
            "api-gateway-vs",
            ["api.company.com"],
            traffic_split={"v1": 90, "v2": 10}
        )
        print(f"  ✓ {vs1.name}: 90% v1, 10% v2")
        
        vs2 = platform.traffic_manager.create_virtual_service(
            "user-service-vs",
            ["users.internal"],
            traffic_split={"stable": 100}
        )
        print(f"  ✓ {vs2.name}: 100% stable")
        
        # Create destination rules
        print("\n⚙️ Creating Destination Rules...")
        
        rules_data = [
            ("production/api-gateway", LoadBalancerAlgorithm.ROUND_ROBIN),
            ("production/auth-service", LoadBalancerAlgorithm.LEAST_CONNECTIONS),
            ("production/user-service", LoadBalancerAlgorithm.WEIGHTED),
            ("production/order-service", LoadBalancerAlgorithm.ROUND_ROBIN),
            ("production/payment-service", LoadBalancerAlgorithm.LEAST_CONNECTIONS)
        ]
        
        for host, algorithm in rules_data:
            rule = platform.traffic_manager.create_destination_rule(
                host, algorithm,
                max_connections=100,
                circuit_breaker_enabled=True
            )
            print(f"  ✓ {host}: {algorithm.value}")
            
        # Configure rate limiting
        print("\n🚦 Configuring Rate Limiting...")
        
        platform.rate_limiter.add_rule("production/api-gateway", rps=1000, burst=2000)
        platform.rate_limiter.add_rule("production/auth-service", rps=500, burst=750)
        platform.rate_limiter.add_rule("production/payment-service", rps=100, burst=150)
        
        for rule in platform.rate_limiter.rules.values():
            print(f"  ✓ {rule.service}: {rule.requests_per_second} RPS (burst: {rule.burst_size})")
            
        # Configure mTLS
        print("\n🔐 Configuring mTLS...")
        
        mtls = platform.configure_mtls("STRICT", ["production", "staging"])
        print(f"  ✓ Mode: {mtls.mode}")
        print(f"  ✓ Namespaces: {', '.join(mtls.namespaces)}")
        
        # Simulate traffic
        print("\n📡 Simulating Traffic...")
        
        services_to_call = [
            "production/api-gateway",
            "production/user-service",
            "production/order-service",
            "production/payment-service"
        ]
        
        for service_key in services_to_call:
            print(f"\n  Calling {service_key}:")
            
            for i in range(10):
                result = await platform.traffic_manager.route_request(
                    service_key,
                    {"path": "/api/test", "method": "GET"}
                )
                
            metrics = platform.traffic_manager.metrics[service_key]
            success_rate = (metrics.successful_requests / metrics.total_requests * 100) if metrics.total_requests else 0
            print(f"    Requests: {metrics.total_requests}, Success: {success_rate:.1f}%")
            
        # Circuit breaker status
        print("\n⚡ Circuit Breaker Status:")
        
        for name, breaker in platform.circuit_breaker_mgr.breakers.items():
            state_icon = {
                "closed": "🟢",
                "open": "🔴",
                "half_open": "🟡"
            }.get(breaker.state.value, "⚪")
            print(f"  {state_icon} {name}: {breaker.state.value} (failures: {breaker.failure_count})")
            
        # Service discovery
        print("\n🔍 Service Discovery:")
        
        all_services = platform.registry.discover()
        print(f"  Found {len(all_services)} services")
        
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Services:")
        print(f"    Total: {stats['services']}")
        print(f"    Endpoints: {stats['total_endpoints']} ({stats['healthy_endpoints']} healthy)")
        
        print(f"\n  Traffic Management:")
        print(f"    Virtual Services: {stats['virtual_services']}")
        print(f"    Destination Rules: {stats['destination_rules']}")
        print(f"    Rate Limit Rules: {stats['rate_limit_rules']}")
        
        print(f"\n  Resilience:")
        print(f"    Circuit Breakers: {stats['circuit_breakers']}")
        print(f"    Open Circuits: {stats['open_circuits']}")
        
        print(f"\n  Traffic:")
        print(f"    Total Requests: {stats['total_requests']}")
        print(f"    Success Rate: {stats['success_rate']:.1f}%")
        
        print(f"\n  Security:")
        print(f"    mTLS Configs: {stats['mtls_configs']}")
        
        # Dashboard
        print("\n📋 Service Mesh Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │                Service Mesh Overview                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Services:           {stats['services']:>10}                        │")
        print(f"  │ Endpoints:          {stats['total_endpoints']:>10} ({stats['healthy_endpoints']} healthy)       │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Virtual Services:   {stats['virtual_services']:>10}                        │")
        print(f"  │ Destination Rules:  {stats['destination_rules']:>10}                        │")
        print(f"  │ Rate Limit Rules:   {stats['rate_limit_rules']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Requests:     {stats['total_requests']:>10}                        │")
        print(f"  │ Success Rate:       {stats['success_rate']:>10.1f}%                       │")
        print(f"  │ Open Circuits:      {stats['open_circuits']:>10}                        │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Service Mesh Platform initialized!")
    print("=" * 60)
