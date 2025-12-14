#!/usr/bin/env python3
"""
Server Init - Iteration 149: Service Mesh Platform
Платформа сервисной сетки

Функционал:
- Traffic Management - управление трафиком
- Service Discovery - обнаружение сервисов
- Load Balancing - балансировка нагрузки
- Circuit Breaking - предохранители
- Retry Policies - политики повторов
- Timeout Configuration - конфигурация таймаутов
- mTLS - взаимный TLS
- Observability - наблюдаемость
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid
import random


class ServiceStatus(Enum):
    """Статус сервиса"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class LoadBalanceAlgorithm(Enum):
    """Алгоритм балансировки"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"
    CONSISTENT_HASH = "consistent_hash"
    WEIGHTED = "weighted"


class CircuitState(Enum):
    """Состояние circuit breaker"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class RetryPolicy(Enum):
    """Политика повторов"""
    NONE = "none"
    SIMPLE = "simple"
    EXPONENTIAL_BACKOFF = "exponential_backoff"


class TrafficPolicy(Enum):
    """Политика трафика"""
    ALLOW_ALL = "allow_all"
    DENY_ALL = "deny_all"
    MUTUAL_TLS = "mutual_tls"
    PERMISSIVE = "permissive"


@dataclass
class ServiceEndpoint:
    """Эндпоинт сервиса"""
    endpoint_id: str
    host: str = ""
    port: int = 8080
    
    # Metadata
    zone: str = ""
    weight: int = 100
    
    # Status
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_health_check: Optional[datetime] = None
    
    # Metrics
    active_connections: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    avg_latency_ms: float = 0.0


@dataclass
class ServiceEntry:
    """Запись сервиса"""
    service_id: str
    name: str = ""
    namespace: str = "default"
    
    # Endpoints
    endpoints: List[ServiceEndpoint] = field(default_factory=list)
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Discovery
    protocol: str = "http"
    version: str = "v1"
    
    # Registration
    registered_at: datetime = field(default_factory=datetime.now)


@dataclass
class VirtualService:
    """Виртуальный сервис"""
    vs_id: str
    name: str = ""
    
    # Host matching
    hosts: List[str] = field(default_factory=list)
    
    # Routes
    routes: List[Dict] = field(default_factory=list)
    
    # Traffic policy
    traffic_policy: Dict = field(default_factory=dict)
    
    # Metadata
    namespace: str = "default"


@dataclass
class DestinationRule:
    """Правило назначения"""
    rule_id: str
    name: str = ""
    host: str = ""
    
    # Traffic policy
    connection_pool: Dict = field(default_factory=dict)
    load_balancer: LoadBalanceAlgorithm = LoadBalanceAlgorithm.ROUND_ROBIN
    
    # Circuit breaker
    circuit_breaker: Dict = field(default_factory=dict)
    
    # Subsets
    subsets: List[Dict] = field(default_factory=list)


@dataclass
class RetryConfig:
    """Конфигурация повторов"""
    config_id: str
    service: str = ""
    
    # Retry settings
    max_retries: int = 3
    per_try_timeout_ms: int = 2000
    retry_on: List[str] = field(default_factory=lambda: ["5xx", "reset", "connect-failure"])
    
    # Backoff
    policy: RetryPolicy = RetryPolicy.EXPONENTIAL_BACKOFF
    initial_interval_ms: int = 100
    max_interval_ms: int = 10000


@dataclass
class CircuitBreakerConfig:
    """Конфигурация circuit breaker"""
    config_id: str
    service: str = ""
    
    # Thresholds
    failure_threshold: int = 5
    success_threshold: int = 3
    
    # Timing
    timeout_ms: int = 30000
    half_open_requests: int = 3
    
    # State
    state: CircuitState = CircuitState.CLOSED
    failures: int = 0
    successes: int = 0
    last_failure: Optional[datetime] = None


@dataclass
class MTLSConfig:
    """Конфигурация mTLS"""
    config_id: str
    namespace: str = "default"
    
    # Mode
    mode: str = "STRICT"  # STRICT, PERMISSIVE, DISABLE
    
    # Certificates
    client_certificate: str = ""
    private_key: str = ""
    ca_certificates: str = ""
    
    # Peer auth
    peer_auth: Dict = field(default_factory=dict)


@dataclass
class TrafficShift:
    """Сдвиг трафика"""
    shift_id: str
    service: str = ""
    
    # Weights
    v1_weight: int = 100
    v2_weight: int = 0
    
    # Strategy
    strategy: str = "gradual"  # immediate, gradual, canary
    
    # Progress
    started_at: Optional[datetime] = None
    target_weight: int = 0


@dataclass
class ServiceMeshMetrics:
    """Метрики сервисной сетки"""
    service: str = ""
    
    # Request metrics
    requests_total: int = 0
    requests_success: int = 0
    requests_failed: int = 0
    
    # Latency
    latency_p50_ms: float = 0.0
    latency_p90_ms: float = 0.0
    latency_p99_ms: float = 0.0
    
    # Circuit breaker
    circuit_opens: int = 0
    
    # Retries
    retry_attempts: int = 0


class ServiceRegistry:
    """Реестр сервисов"""
    
    def __init__(self):
        self.services: Dict[str, ServiceEntry] = {}
        
    def register(self, name: str, endpoints: List[Dict], **kwargs) -> ServiceEntry:
        """Регистрация сервиса"""
        service = ServiceEntry(
            service_id=f"svc_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        
        for ep_data in endpoints:
            endpoint = ServiceEndpoint(
                endpoint_id=f"ep_{uuid.uuid4().hex[:8]}",
                **ep_data
            )
            service.endpoints.append(endpoint)
            
        self.services[service.service_id] = service
        return service
        
    def deregister(self, service_id: str) -> bool:
        """Дерегистрация сервиса"""
        if service_id in self.services:
            del self.services[service_id]
            return True
        return False
        
    def discover(self, name: str, namespace: str = "default") -> List[ServiceEntry]:
        """Обнаружение сервисов"""
        return [
            s for s in self.services.values()
            if s.name == name and s.namespace == namespace
        ]
        
    def get_healthy_endpoints(self, service_id: str) -> List[ServiceEndpoint]:
        """Получение здоровых эндпоинтов"""
        service = self.services.get(service_id)
        if not service:
            return []
        return [ep for ep in service.endpoints if ep.status == ServiceStatus.HEALTHY]


class LoadBalancer:
    """Балансировщик нагрузки"""
    
    def __init__(self):
        self.round_robin_indices: Dict[str, int] = {}
        
    def select(self, endpoints: List[ServiceEndpoint],
               algorithm: LoadBalanceAlgorithm = LoadBalanceAlgorithm.ROUND_ROBIN,
               hash_key: str = None) -> Optional[ServiceEndpoint]:
        """Выбор эндпоинта"""
        if not endpoints:
            return None
            
        healthy = [ep for ep in endpoints if ep.status == ServiceStatus.HEALTHY]
        if not healthy:
            healthy = endpoints
            
        if algorithm == LoadBalanceAlgorithm.ROUND_ROBIN:
            return self._round_robin(healthy)
        elif algorithm == LoadBalanceAlgorithm.LEAST_CONNECTIONS:
            return self._least_connections(healthy)
        elif algorithm == LoadBalanceAlgorithm.RANDOM:
            return random.choice(healthy)
        elif algorithm == LoadBalanceAlgorithm.CONSISTENT_HASH:
            return self._consistent_hash(healthy, hash_key or "")
        elif algorithm == LoadBalanceAlgorithm.WEIGHTED:
            return self._weighted(healthy)
            
        return healthy[0] if healthy else None
        
    def _round_robin(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Round Robin"""
        key = "|".join(ep.endpoint_id for ep in endpoints)
        idx = self.round_robin_indices.get(key, 0)
        
        endpoint = endpoints[idx % len(endpoints)]
        self.round_robin_indices[key] = idx + 1
        
        return endpoint
        
    def _least_connections(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Least connections"""
        return min(endpoints, key=lambda ep: ep.active_connections)
        
    def _consistent_hash(self, endpoints: List[ServiceEndpoint], key: str) -> ServiceEndpoint:
        """Consistent hashing"""
        hash_val = hash(key) % len(endpoints)
        return endpoints[hash_val]
        
    def _weighted(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Weighted selection"""
        total_weight = sum(ep.weight for ep in endpoints)
        r = random.randint(1, total_weight)
        
        cumulative = 0
        for ep in endpoints:
            cumulative += ep.weight
            if r <= cumulative:
                return ep
                
        return endpoints[-1]


class CircuitBreakerManager:
    """Менеджер circuit breaker"""
    
    def __init__(self):
        self.configs: Dict[str, CircuitBreakerConfig] = {}
        
    def configure(self, service: str, **kwargs) -> CircuitBreakerConfig:
        """Конфигурация circuit breaker"""
        config = CircuitBreakerConfig(
            config_id=f"cb_{uuid.uuid4().hex[:8]}",
            service=service,
            **kwargs
        )
        self.configs[service] = config
        return config
        
    def record_success(self, service: str):
        """Запись успеха"""
        config = self.configs.get(service)
        if not config:
            return
            
        config.successes += 1
        
        if config.state == CircuitState.HALF_OPEN:
            if config.successes >= config.success_threshold:
                config.state = CircuitState.CLOSED
                config.failures = 0
                config.successes = 0
                
    def record_failure(self, service: str):
        """Запись неудачи"""
        config = self.configs.get(service)
        if not config:
            return
            
        config.failures += 1
        config.last_failure = datetime.now()
        
        if config.state == CircuitState.CLOSED:
            if config.failures >= config.failure_threshold:
                config.state = CircuitState.OPEN
                
        elif config.state == CircuitState.HALF_OPEN:
            config.state = CircuitState.OPEN
            config.successes = 0
            
    def is_allowed(self, service: str) -> bool:
        """Проверка разрешения запроса"""
        config = self.configs.get(service)
        if not config:
            return True
            
        if config.state == CircuitState.CLOSED:
            return True
            
        if config.state == CircuitState.OPEN:
            # Check if timeout expired
            if config.last_failure:
                elapsed = (datetime.now() - config.last_failure).total_seconds() * 1000
                if elapsed >= config.timeout_ms:
                    config.state = CircuitState.HALF_OPEN
                    return True
            return False
            
        if config.state == CircuitState.HALF_OPEN:
            return True
            
        return False
        
    def get_state(self, service: str) -> CircuitState:
        """Получение состояния"""
        config = self.configs.get(service)
        return config.state if config else CircuitState.CLOSED


class RetryManager:
    """Менеджер повторов"""
    
    def __init__(self):
        self.configs: Dict[str, RetryConfig] = {}
        
    def configure(self, service: str, **kwargs) -> RetryConfig:
        """Конфигурация повторов"""
        config = RetryConfig(
            config_id=f"retry_{uuid.uuid4().hex[:8]}",
            service=service,
            **kwargs
        )
        self.configs[service] = config
        return config
        
    async def execute_with_retry(self, service: str,
                                   operation: Callable) -> Any:
        """Выполнение с повторами"""
        config = self.configs.get(service)
        if not config or config.policy == RetryPolicy.NONE:
            return await operation()
            
        last_error = None
        interval = config.initial_interval_ms
        
        for attempt in range(config.max_retries + 1):
            try:
                return await asyncio.wait_for(
                    operation(),
                    timeout=config.per_try_timeout_ms / 1000
                )
            except Exception as e:
                last_error = e
                
                if attempt < config.max_retries:
                    await asyncio.sleep(interval / 1000)
                    
                    if config.policy == RetryPolicy.EXPONENTIAL_BACKOFF:
                        interval = min(interval * 2, config.max_interval_ms)
                        
        raise last_error


class TrafficManager:
    """Менеджер трафика"""
    
    def __init__(self):
        self.virtual_services: Dict[str, VirtualService] = {}
        self.destination_rules: Dict[str, DestinationRule] = {}
        self.traffic_shifts: Dict[str, TrafficShift] = {}
        
    def create_virtual_service(self, name: str, hosts: List[str],
                                 routes: List[Dict]) -> VirtualService:
        """Создание виртуального сервиса"""
        vs = VirtualService(
            vs_id=f"vs_{uuid.uuid4().hex[:8]}",
            name=name,
            hosts=hosts,
            routes=routes
        )
        self.virtual_services[vs.vs_id] = vs
        return vs
        
    def create_destination_rule(self, name: str, host: str,
                                   **kwargs) -> DestinationRule:
        """Создание правила назначения"""
        rule = DestinationRule(
            rule_id=f"dr_{uuid.uuid4().hex[:8]}",
            name=name,
            host=host,
            **kwargs
        )
        self.destination_rules[rule.rule_id] = rule
        return rule
        
    def shift_traffic(self, service: str, v1_weight: int,
                       v2_weight: int) -> TrafficShift:
        """Сдвиг трафика"""
        shift = TrafficShift(
            shift_id=f"shift_{uuid.uuid4().hex[:8]}",
            service=service,
            v1_weight=v1_weight,
            v2_weight=v2_weight,
            started_at=datetime.now()
        )
        self.traffic_shifts[service] = shift
        return shift
        
    def get_route_weight(self, service: str, version: str) -> int:
        """Получение веса маршрута"""
        shift = self.traffic_shifts.get(service)
        if not shift:
            return 100 if version == "v1" else 0
            
        return shift.v1_weight if version == "v1" else shift.v2_weight


class MTLSManager:
    """Менеджер mTLS"""
    
    def __init__(self):
        self.configs: Dict[str, MTLSConfig] = {}
        
    def configure(self, namespace: str, mode: str = "STRICT") -> MTLSConfig:
        """Конфигурация mTLS"""
        config = MTLSConfig(
            config_id=f"mtls_{uuid.uuid4().hex[:8]}",
            namespace=namespace,
            mode=mode
        )
        self.configs[namespace] = config
        return config
        
    def is_tls_required(self, namespace: str) -> bool:
        """Требуется ли TLS"""
        config = self.configs.get(namespace)
        return config and config.mode in ["STRICT", "PERMISSIVE"]
        
    def is_strict_mode(self, namespace: str) -> bool:
        """Строгий режим"""
        config = self.configs.get(namespace)
        return config and config.mode == "STRICT"


class HealthChecker:
    """Проверка здоровья"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.check_interval: int = 30
        
    async def check_endpoint(self, endpoint: ServiceEndpoint) -> ServiceStatus:
        """Проверка эндпоинта"""
        # Simulate health check
        await asyncio.sleep(0.01)
        
        # Random health status for demo
        if random.random() > 0.1:
            endpoint.status = ServiceStatus.HEALTHY
        else:
            endpoint.status = ServiceStatus.UNHEALTHY
            
        endpoint.last_health_check = datetime.now()
        return endpoint.status
        
    async def check_all(self):
        """Проверка всех эндпоинтов"""
        for service in self.registry.services.values():
            for endpoint in service.endpoints:
                await self.check_endpoint(endpoint)


class ServiceMeshPlatform:
    """Платформа сервисной сетки"""
    
    def __init__(self):
        self.registry = ServiceRegistry()
        self.load_balancer = LoadBalancer()
        self.circuit_breaker = CircuitBreakerManager()
        self.retry_manager = RetryManager()
        self.traffic_manager = TrafficManager()
        self.mtls_manager = MTLSManager()
        self.health_checker = HealthChecker(self.registry)
        self.metrics: Dict[str, ServiceMeshMetrics] = {}
        
    async def call_service(self, service_name: str, request: Dict,
                            lb_algorithm: LoadBalanceAlgorithm = LoadBalanceAlgorithm.ROUND_ROBIN) -> Dict:
        """Вызов сервиса через mesh"""
        # Find service
        services = self.registry.discover(service_name)
        if not services:
            raise Exception(f"Service not found: {service_name}")
            
        service = services[0]
        
        # Check circuit breaker
        if not self.circuit_breaker.is_allowed(service_name):
            raise Exception(f"Circuit breaker open for {service_name}")
            
        # Select endpoint
        endpoint = self.load_balancer.select(service.endpoints, lb_algorithm)
        if not endpoint:
            raise Exception(f"No healthy endpoints for {service_name}")
            
        # Record metrics
        if service_name not in self.metrics:
            self.metrics[service_name] = ServiceMeshMetrics(service=service_name)
            
        metrics = self.metrics[service_name]
        metrics.requests_total += 1
        endpoint.total_requests += 1
        endpoint.active_connections += 1
        
        try:
            # Execute with retry
            result = await self.retry_manager.execute_with_retry(
                service_name,
                lambda: self._make_request(endpoint, request)
            )
            
            self.circuit_breaker.record_success(service_name)
            metrics.requests_success += 1
            
            return result
            
        except Exception as e:
            self.circuit_breaker.record_failure(service_name)
            metrics.requests_failed += 1
            endpoint.failed_requests += 1
            raise
            
        finally:
            endpoint.active_connections -= 1
            
    async def _make_request(self, endpoint: ServiceEndpoint,
                             request: Dict) -> Dict:
        """Выполнение запроса"""
        # Simulate request
        await asyncio.sleep(random.uniform(0.01, 0.05))
        
        # Random failures for demo
        if random.random() < 0.05:
            raise Exception("Simulated request failure")
            
        return {
            "status": "success",
            "endpoint": f"{endpoint.host}:{endpoint.port}",
            "response_time_ms": random.uniform(10, 100)
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_requests = sum(m.requests_total for m in self.metrics.values())
        total_success = sum(m.requests_success for m in self.metrics.values())
        
        return {
            "registered_services": len(self.registry.services),
            "total_endpoints": sum(len(s.endpoints) for s in self.registry.services.values()),
            "virtual_services": len(self.traffic_manager.virtual_services),
            "destination_rules": len(self.traffic_manager.destination_rules),
            "circuit_breakers": len(self.circuit_breaker.configs),
            "total_requests": total_requests,
            "success_rate": (total_success / total_requests * 100) if total_requests > 0 else 0
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 149: Service Mesh Platform")
    print("=" * 60)
    
    async def demo():
        platform = ServiceMeshPlatform()
        print("✓ Service Mesh Platform created")
        
        # Register services
        print("\n📡 Registering Services...")
        
        services_data = [
            ("api-gateway", [
                {"host": "10.0.1.1", "port": 8080, "zone": "us-east-1a"},
                {"host": "10.0.1.2", "port": 8080, "zone": "us-east-1b"},
                {"host": "10.0.1.3", "port": 8080, "zone": "us-east-1c"}
            ]),
            ("user-service", [
                {"host": "10.0.2.1", "port": 8081, "zone": "us-east-1a"},
                {"host": "10.0.2.2", "port": 8081, "zone": "us-east-1b"}
            ]),
            ("order-service", [
                {"host": "10.0.3.1", "port": 8082, "zone": "us-east-1a"},
                {"host": "10.0.3.2", "port": 8082, "zone": "us-east-1b"}
            ]),
            ("payment-service", [
                {"host": "10.0.4.1", "port": 8083, "zone": "us-east-1a"}
            ]),
            ("notification-service", [
                {"host": "10.0.5.1", "port": 8084, "zone": "us-east-1a"},
                {"host": "10.0.5.2", "port": 8084, "zone": "us-east-1b"}
            ])
        ]
        
        for name, endpoints in services_data:
            service = platform.registry.register(name, endpoints, protocol="http")
            print(f"  ✓ {name}: {len(endpoints)} endpoints")
            
        # Health checks
        print("\n🏥 Running Health Checks...")
        
        await platform.health_checker.check_all()
        
        for service in platform.registry.services.values():
            healthy = len([ep for ep in service.endpoints if ep.status == ServiceStatus.HEALTHY])
            total = len(service.endpoints)
            print(f"  {service.name}: {healthy}/{total} healthy")
            
        # Configure circuit breakers
        print("\n⚡ Configuring Circuit Breakers...")
        
        for service in ["user-service", "order-service", "payment-service"]:
            config = platform.circuit_breaker.configure(
                service,
                failure_threshold=5,
                success_threshold=3,
                timeout_ms=30000
            )
            print(f"  ✓ {service}: threshold={config.failure_threshold}")
            
        # Configure retries
        print("\n🔄 Configuring Retry Policies...")
        
        platform.retry_manager.configure(
            "payment-service",
            max_retries=3,
            per_try_timeout_ms=5000,
            policy=RetryPolicy.EXPONENTIAL_BACKOFF
        )
        print("  ✓ payment-service: 3 retries, exponential backoff")
        
        platform.retry_manager.configure(
            "notification-service",
            max_retries=5,
            per_try_timeout_ms=2000,
            policy=RetryPolicy.SIMPLE
        )
        print("  ✓ notification-service: 5 retries, simple")
        
        # Create virtual services
        print("\n🔀 Creating Virtual Services...")
        
        vs = platform.traffic_manager.create_virtual_service(
            "order-routing",
            hosts=["orders.default.svc.cluster.local"],
            routes=[
                {"match": {"uri": "/v2/*"}, "route": {"destination": "order-service-v2"}},
                {"match": {"uri": "/*"}, "route": {"destination": "order-service-v1"}}
            ]
        )
        print(f"  ✓ {vs.name}: {len(vs.routes)} routes")
        
        # Create destination rules
        print("\n🎯 Creating Destination Rules...")
        
        rule = platform.traffic_manager.create_destination_rule(
            "order-lb",
            host="order-service",
            load_balancer=LoadBalanceAlgorithm.LEAST_CONNECTIONS,
            circuit_breaker={"consecutive_errors": 5},
            subsets=[
                {"name": "v1", "labels": {"version": "v1"}},
                {"name": "v2", "labels": {"version": "v2"}}
            ]
        )
        print(f"  ✓ {rule.name}: {rule.load_balancer.value}")
        
        # Traffic shifting (canary)
        print("\n🐤 Traffic Shifting (Canary Deployment)...")
        
        shift = platform.traffic_manager.shift_traffic(
            "order-service",
            v1_weight=90,
            v2_weight=10
        )
        print(f"  ✓ order-service: v1={shift.v1_weight}%, v2={shift.v2_weight}%")
        
        # Configure mTLS
        print("\n🔐 Configuring mTLS...")
        
        platform.mtls_manager.configure("default", mode="STRICT")
        print("  ✓ default namespace: STRICT mode")
        
        platform.mtls_manager.configure("monitoring", mode="PERMISSIVE")
        print("  ✓ monitoring namespace: PERMISSIVE mode")
        
        # Make service calls
        print("\n📞 Making Service Calls...")
        
        call_results = {"success": 0, "failed": 0}
        
        for i in range(20):
            for service in ["user-service", "order-service"]:
                try:
                    result = await platform.call_service(
                        service,
                        {"action": "test", "id": i},
                        LoadBalanceAlgorithm.ROUND_ROBIN
                    )
                    call_results["success"] += 1
                except Exception as e:
                    call_results["failed"] += 1
                    
        print(f"\n  Success: {call_results['success']}")
        print(f"  Failed: {call_results['failed']}")
        
        # Show metrics
        print("\n📊 Service Metrics:")
        
        for service_name, metrics in platform.metrics.items():
            success_rate = (metrics.requests_success / metrics.requests_total * 100) if metrics.requests_total > 0 else 0
            print(f"\n  {service_name}:")
            print(f"    Requests: {metrics.requests_total}")
            print(f"    Success Rate: {success_rate:.1f}%")
            print(f"    Failed: {metrics.requests_failed}")
            
        # Show circuit breaker states
        print("\n⚡ Circuit Breaker States:")
        
        for service, config in platform.circuit_breaker.configs.items():
            state_icon = {"closed": "🟢", "open": "🔴", "half_open": "🟡"}
            print(f"  {state_icon[config.state.value]} {service}: {config.state.value} (failures: {config.failures})")
            
        # Load balancing demo
        print("\n⚖️ Load Balancing Distribution:")
        
        services = platform.registry.discover("user-service")
        if services:
            service = services[0]
            for ep in service.endpoints:
                print(f"  {ep.host}:{ep.port}: {ep.total_requests} requests")
                
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Registered Services: {stats['registered_services']}")
        print(f"  Total Endpoints: {stats['total_endpoints']}")
        print(f"  Virtual Services: {stats['virtual_services']}")
        print(f"  Destination Rules: {stats['destination_rules']}")
        print(f"  Circuit Breakers: {stats['circuit_breakers']}")
        print(f"  Total Requests: {stats['total_requests']}")
        print(f"  Success Rate: {stats['success_rate']:.1f}%")
        
        # Dashboard
        print("\n📋 Service Mesh Dashboard:")
        print("  ┌────────────────────────────────────────────────────────────┐")
        print("  │                  Service Mesh Overview                     │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Registered Services:   {stats['registered_services']:>10}                    │")
        print(f"  │ Total Endpoints:       {stats['total_endpoints']:>10}                    │")
        print(f"  │ Virtual Services:      {stats['virtual_services']:>10}                    │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Requests:        {stats['total_requests']:>10}                    │")
        print(f"  │ Success Rate:          {stats['success_rate']:>10.1f}%                   │")
        print("  └────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Service Mesh Platform initialized!")
    print("=" * 60)
