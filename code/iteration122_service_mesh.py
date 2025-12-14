#!/usr/bin/env python3
"""
Server Init - Iteration 122: Service Mesh Platform
Платформа сервисной сетки

Функционал:
- Sidecar Management - управление sidecar
- Traffic Management - управление трафиком
- Load Balancing - балансировка нагрузки
- Service Discovery - обнаружение сервисов
- Circuit Breaker - автоматический выключатель
- Retry Policies - политики повторов
- mTLS - взаимный TLS
- Observability - наблюдаемость
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
import hashlib


class ServiceStatus(Enum):
    """Статус сервиса"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class LoadBalancerType(Enum):
    """Тип балансировщика"""
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


class TrafficPolicy(Enum):
    """Политика трафика"""
    ALL = "all"
    CANARY = "canary"
    BLUE_GREEN = "blue_green"
    MIRROR = "mirror"


class mTLSMode(Enum):
    """Режим mTLS"""
    DISABLED = "disabled"
    PERMISSIVE = "permissive"
    STRICT = "strict"


@dataclass
class ServiceEndpoint:
    """Эндпоинт сервиса"""
    endpoint_id: str
    address: str = ""
    port: int = 80
    
    # Metadata
    version: str = "v1"
    weight: int = 100
    
    # Status
    status: ServiceStatus = ServiceStatus.HEALTHY
    last_health_check: Optional[datetime] = None
    
    # Stats
    request_count: int = 0
    error_count: int = 0
    active_connections: int = 0


@dataclass
class Service:
    """Сервис"""
    service_id: str
    name: str = ""
    namespace: str = "default"
    
    # Endpoints
    endpoints: List[ServiceEndpoint] = field(default_factory=list)
    
    # Config
    load_balancer: LoadBalancerType = LoadBalancerType.ROUND_ROBIN
    
    # mTLS
    mtls_mode: mTLSMode = mTLSMode.PERMISSIVE
    
    # Metadata
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Stats
    total_requests: int = 0


@dataclass
class Sidecar:
    """Sidecar прокси"""
    sidecar_id: str
    service_id: str = ""
    
    # Config
    inbound_port: int = 15006
    outbound_port: int = 15001
    admin_port: int = 15000
    
    # Status
    status: ServiceStatus = ServiceStatus.HEALTHY
    version: str = "1.0.0"
    
    # Stats
    requests_processed: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0


@dataclass
class VirtualService:
    """Виртуальный сервис"""
    virtual_service_id: str
    name: str = ""
    
    # Hosts
    hosts: List[str] = field(default_factory=list)
    
    # Routes
    routes: List[Dict[str, Any]] = field(default_factory=list)
    
    # Traffic policy
    traffic_policy: TrafficPolicy = TrafficPolicy.ALL


@dataclass
class DestinationRule:
    """Правило назначения"""
    rule_id: str
    service_name: str = ""
    
    # Traffic policy
    load_balancer: LoadBalancerType = LoadBalancerType.ROUND_ROBIN
    
    # Connection pool
    max_connections: int = 100
    max_pending_requests: int = 1000
    
    # Outlier detection
    consecutive_errors: int = 5
    interval_seconds: int = 10
    base_ejection_time_seconds: int = 30


@dataclass
class CircuitBreaker:
    """Автоматический выключатель"""
    breaker_id: str
    service_name: str = ""
    
    # Config
    failure_threshold: int = 5
    success_threshold: int = 3
    timeout_seconds: int = 30
    
    # State
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure: Optional[datetime] = None
    opened_at: Optional[datetime] = None


@dataclass
class RetryPolicy:
    """Политика повторов"""
    policy_id: str
    service_name: str = ""
    
    # Config
    max_retries: int = 3
    retry_on: List[str] = field(default_factory=lambda: ["5xx", "reset", "connect-failure"])
    per_try_timeout_ms: int = 2000
    
    # Backoff
    base_interval_ms: int = 25
    max_interval_ms: int = 250


@dataclass
class TrafficMirror:
    """Зеркалирование трафика"""
    mirror_id: str
    source_service: str = ""
    target_service: str = ""
    
    # Config
    percentage: float = 100.0
    
    # Status
    active: bool = True
    
    # Stats
    requests_mirrored: int = 0


class ServiceRegistry:
    """Реестр сервисов"""
    
    def __init__(self):
        self.services: Dict[str, Service] = {}
        
    def register(self, name: str, namespace: str = "default",
                  **kwargs) -> Service:
        """Регистрация сервиса"""
        service = Service(
            service_id=f"svc_{uuid.uuid4().hex[:8]}",
            name=name,
            namespace=namespace,
            **kwargs
        )
        self.services[service.service_id] = service
        return service
        
    def add_endpoint(self, service_id: str, address: str, port: int,
                      **kwargs) -> ServiceEndpoint:
        """Добавление эндпоинта"""
        service = self.services.get(service_id)
        if not service:
            return None
            
        endpoint = ServiceEndpoint(
            endpoint_id=f"ep_{uuid.uuid4().hex[:8]}",
            address=address,
            port=port,
            **kwargs
        )
        
        service.endpoints.append(endpoint)
        return endpoint
        
    def discover(self, name: str, namespace: str = "default") -> Optional[Service]:
        """Обнаружение сервиса"""
        for service in self.services.values():
            if service.name == name and service.namespace == namespace:
                return service
        return None
        
    def get_healthy_endpoints(self, service_id: str) -> List[ServiceEndpoint]:
        """Здоровые эндпоинты"""
        service = self.services.get(service_id)
        if not service:
            return []
            
        return [ep for ep in service.endpoints if ep.status == ServiceStatus.HEALTHY]


class SidecarManager:
    """Менеджер sidecar"""
    
    def __init__(self):
        self.sidecars: Dict[str, Sidecar] = {}
        
    def inject(self, service_id: str) -> Sidecar:
        """Инъекция sidecar"""
        sidecar = Sidecar(
            sidecar_id=f"proxy_{uuid.uuid4().hex[:8]}",
            service_id=service_id
        )
        
        self.sidecars[sidecar.sidecar_id] = sidecar
        return sidecar
        
    def configure(self, sidecar_id: str, **kwargs):
        """Настройка sidecar"""
        sidecar = self.sidecars.get(sidecar_id)
        if sidecar:
            for key, value in kwargs.items():
                if hasattr(sidecar, key):
                    setattr(sidecar, key, value)


class LoadBalancer:
    """Балансировщик нагрузки"""
    
    def __init__(self):
        self.round_robin_index: Dict[str, int] = defaultdict(int)
        
    def select(self, endpoints: List[ServiceEndpoint],
                lb_type: LoadBalancerType = LoadBalancerType.ROUND_ROBIN,
                key: str = None) -> Optional[ServiceEndpoint]:
        """Выбор эндпоинта"""
        if not endpoints:
            return None
            
        healthy = [ep for ep in endpoints if ep.status == ServiceStatus.HEALTHY]
        if not healthy:
            return None
            
        if lb_type == LoadBalancerType.ROUND_ROBIN:
            idx = self.round_robin_index[key or "default"]
            self.round_robin_index[key or "default"] = (idx + 1) % len(healthy)
            return healthy[idx % len(healthy)]
            
        elif lb_type == LoadBalancerType.RANDOM:
            return random.choice(healthy)
            
        elif lb_type == LoadBalancerType.LEAST_CONNECTIONS:
            return min(healthy, key=lambda ep: ep.active_connections)
            
        elif lb_type == LoadBalancerType.WEIGHTED:
            total_weight = sum(ep.weight for ep in healthy)
            r = random.randint(1, total_weight)
            for ep in healthy:
                r -= ep.weight
                if r <= 0:
                    return ep
            return healthy[0]
            
        elif lb_type == LoadBalancerType.CONSISTENT_HASH:
            if key:
                h = int(hashlib.md5(key.encode()).hexdigest(), 16)
                return healthy[h % len(healthy)]
            return healthy[0]
            
        return healthy[0]


class CircuitBreakerManager:
    """Менеджер circuit breaker"""
    
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
        
    def create(self, service_name: str, **kwargs) -> CircuitBreaker:
        """Создание breaker"""
        breaker = CircuitBreaker(
            breaker_id=f"cb_{uuid.uuid4().hex[:8]}",
            service_name=service_name,
            **kwargs
        )
        self.breakers[service_name] = breaker
        return breaker
        
    def allow_request(self, service_name: str) -> bool:
        """Разрешить запрос?"""
        breaker = self.breakers.get(service_name)
        if not breaker:
            return True
            
        if breaker.state == CircuitState.CLOSED:
            return True
            
        if breaker.state == CircuitState.OPEN:
            # Check if timeout passed
            if breaker.opened_at:
                elapsed = (datetime.now() - breaker.opened_at).total_seconds()
                if elapsed >= breaker.timeout_seconds:
                    breaker.state = CircuitState.HALF_OPEN
                    return True
            return False
            
        if breaker.state == CircuitState.HALF_OPEN:
            return True
            
        return True
        
    def record_success(self, service_name: str):
        """Записать успех"""
        breaker = self.breakers.get(service_name)
        if not breaker:
            return
            
        if breaker.state == CircuitState.HALF_OPEN:
            breaker.success_count += 1
            if breaker.success_count >= breaker.success_threshold:
                breaker.state = CircuitState.CLOSED
                breaker.failure_count = 0
                breaker.success_count = 0
                
    def record_failure(self, service_name: str):
        """Записать ошибку"""
        breaker = self.breakers.get(service_name)
        if not breaker:
            return
            
        breaker.failure_count += 1
        breaker.last_failure = datetime.now()
        
        if breaker.state == CircuitState.HALF_OPEN:
            breaker.state = CircuitState.OPEN
            breaker.opened_at = datetime.now()
        elif breaker.failure_count >= breaker.failure_threshold:
            breaker.state = CircuitState.OPEN
            breaker.opened_at = datetime.now()


class TrafficManager:
    """Менеджер трафика"""
    
    def __init__(self):
        self.virtual_services: Dict[str, VirtualService] = {}
        self.destination_rules: Dict[str, DestinationRule] = {}
        self.mirrors: Dict[str, TrafficMirror] = {}
        
    def create_virtual_service(self, name: str, hosts: List[str],
                                 **kwargs) -> VirtualService:
        """Создание виртуального сервиса"""
        vs = VirtualService(
            virtual_service_id=f"vs_{uuid.uuid4().hex[:8]}",
            name=name,
            hosts=hosts,
            **kwargs
        )
        self.virtual_services[vs.virtual_service_id] = vs
        return vs
        
    def create_destination_rule(self, service_name: str,
                                  **kwargs) -> DestinationRule:
        """Создание правила назначения"""
        rule = DestinationRule(
            rule_id=f"dr_{uuid.uuid4().hex[:8]}",
            service_name=service_name,
            **kwargs
        )
        self.destination_rules[service_name] = rule
        return rule
        
    def create_mirror(self, source: str, target: str,
                       percentage: float = 100.0) -> TrafficMirror:
        """Создание зеркала"""
        mirror = TrafficMirror(
            mirror_id=f"mir_{uuid.uuid4().hex[:8]}",
            source_service=source,
            target_service=target,
            percentage=percentage
        )
        self.mirrors[mirror.mirror_id] = mirror
        return mirror


class HealthChecker:
    """Проверка здоровья"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        
    async def check_all(self) -> Dict[str, Any]:
        """Проверка всех сервисов"""
        results = {}
        
        for service in self.registry.services.values():
            healthy = 0
            unhealthy = 0
            
            for endpoint in service.endpoints:
                # Simulate health check
                is_healthy = random.random() > 0.1
                
                if is_healthy:
                    endpoint.status = ServiceStatus.HEALTHY
                    healthy += 1
                else:
                    endpoint.status = ServiceStatus.UNHEALTHY
                    unhealthy += 1
                    
                endpoint.last_health_check = datetime.now()
                
            results[service.name] = {
                "healthy": healthy,
                "unhealthy": unhealthy,
                "total": len(service.endpoints)
            }
            
        return results


class ServiceMeshPlatform:
    """Платформа сервисной сетки"""
    
    def __init__(self):
        self.registry = ServiceRegistry()
        self.sidecar_manager = SidecarManager()
        self.load_balancer = LoadBalancer()
        self.circuit_breaker_manager = CircuitBreakerManager()
        self.traffic_manager = TrafficManager()
        self.health_checker = HealthChecker(self.registry)
        
    async def route_request(self, source: str, destination: str,
                             path: str = "/") -> Dict[str, Any]:
        """Маршрутизация запроса"""
        # Find destination service
        service = self.registry.discover(destination)
        if not service:
            return {"error": "Service not found", "status": 503}
            
        # Check circuit breaker
        if not self.circuit_breaker_manager.allow_request(destination):
            return {"error": "Circuit open", "status": 503}
            
        # Get healthy endpoints
        endpoints = self.registry.get_healthy_endpoints(service.service_id)
        if not endpoints:
            return {"error": "No healthy endpoints", "status": 503}
            
        # Load balance
        endpoint = self.load_balancer.select(endpoints, service.load_balancer)
        if not endpoint:
            return {"error": "No endpoint selected", "status": 503}
            
        # Simulate request
        await asyncio.sleep(random.uniform(0.001, 0.01))
        
        success = random.random() > 0.05
        
        # Update stats
        endpoint.request_count += 1
        service.total_requests += 1
        
        if success:
            self.circuit_breaker_manager.record_success(destination)
            return {
                "status": 200,
                "endpoint": f"{endpoint.address}:{endpoint.port}",
                "service": destination
            }
        else:
            endpoint.error_count += 1
            self.circuit_breaker_manager.record_failure(destination)
            return {"error": "Request failed", "status": 500}
            
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_endpoints = sum(
            len(s.endpoints) for s in self.registry.services.values()
        )
        
        healthy_endpoints = sum(
            len([ep for ep in s.endpoints if ep.status == ServiceStatus.HEALTHY])
            for s in self.registry.services.values()
        )
        
        total_requests = sum(
            s.total_requests for s in self.registry.services.values()
        )
        
        return {
            "total_services": len(self.registry.services),
            "total_endpoints": total_endpoints,
            "healthy_endpoints": healthy_endpoints,
            "total_sidecars": len(self.sidecar_manager.sidecars),
            "total_requests": total_requests,
            "virtual_services": len(self.traffic_manager.virtual_services),
            "circuit_breakers": len(self.circuit_breaker_manager.breakers)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 122: Service Mesh Platform")
    print("=" * 60)
    
    async def demo():
        platform = ServiceMeshPlatform()
        print("✓ Service Mesh Platform created")
        
        # Register services
        print("\n🏗️ Registering Services...")
        
        services_data = [
            ("api-gateway", "production", LoadBalancerType.ROUND_ROBIN),
            ("user-service", "production", LoadBalancerType.LEAST_CONNECTIONS),
            ("order-service", "production", LoadBalancerType.WEIGHTED),
            ("product-service", "production", LoadBalancerType.RANDOM),
            ("payment-service", "production", LoadBalancerType.CONSISTENT_HASH),
            ("notification-service", "production", LoadBalancerType.ROUND_ROBIN),
        ]
        
        created_services = []
        for name, ns, lb_type in services_data:
            service = platform.registry.register(name, ns, load_balancer=lb_type)
            created_services.append(service)
            
            # Add endpoints
            for i in range(random.randint(2, 4)):
                platform.registry.add_endpoint(
                    service.service_id,
                    f"10.0.{random.randint(1,10)}.{random.randint(1,254)}",
                    8080 + i,
                    version=random.choice(["v1", "v1.1", "v2"]),
                    weight=random.randint(50, 100)
                )
                
            print(f"  ✓ {name}: {len(service.endpoints)} endpoints ({lb_type.value})")
            
        # Inject sidecars
        print("\n🔧 Injecting Sidecars...")
        
        for service in created_services:
            sidecar = platform.sidecar_manager.inject(service.service_id)
            print(f"  ✓ {service.name}: {sidecar.sidecar_id}")
            
        # Create circuit breakers
        print("\n⚡ Creating Circuit Breakers...")
        
        for service in created_services:
            cb = platform.circuit_breaker_manager.create(
                service.name,
                failure_threshold=5,
                success_threshold=3,
                timeout_seconds=30
            )
            print(f"  ✓ {service.name}: {cb.state.value}")
            
        # Create virtual services
        print("\n🌐 Creating Virtual Services...")
        
        # Canary deployment
        canary_vs = platform.traffic_manager.create_virtual_service(
            "user-service-canary",
            ["user-service.production.svc.cluster.local"],
            traffic_policy=TrafficPolicy.CANARY,
            routes=[
                {"destination": "user-service", "version": "v1", "weight": 90},
                {"destination": "user-service", "version": "v2", "weight": 10}
            ]
        )
        print(f"  ✓ Canary: user-service (90% v1, 10% v2)")
        
        # Blue-green deployment
        bg_vs = platform.traffic_manager.create_virtual_service(
            "order-service-bg",
            ["order-service.production.svc.cluster.local"],
            traffic_policy=TrafficPolicy.BLUE_GREEN
        )
        print(f"  ✓ Blue-Green: order-service")
        
        # Create destination rules
        print("\n📋 Creating Destination Rules...")
        
        for service in created_services[:3]:
            rule = platform.traffic_manager.create_destination_rule(
                service.name,
                max_connections=100,
                max_pending_requests=1000,
                consecutive_errors=5
            )
            print(f"  ✓ {service.name}: max_conn={rule.max_connections}")
            
        # Create traffic mirror
        mirror = platform.traffic_manager.create_mirror(
            "api-gateway", "api-gateway-shadow", 100.0
        )
        print(f"\n🪞 Traffic Mirror: api-gateway → shadow (100%)")
        
        # Health check
        print("\n🏥 Running Health Checks...")
        
        health_results = await platform.health_checker.check_all()
        
        for service_name, result in health_results.items():
            status = "🟢" if result["healthy"] == result["total"] else "🟡"
            print(f"  {status} {service_name}: {result['healthy']}/{result['total']} healthy")
            
        # Route requests
        print("\n🚀 Routing Requests...")
        
        request_results = defaultdict(int)
        
        for _ in range(100):
            source = "api-gateway"
            destination = random.choice([s.name for s in created_services[1:]])
            
            result = await platform.route_request(source, destination, "/api/resource")
            
            if result.get("status") == 200:
                request_results["success"] += 1
            else:
                request_results["failed"] += 1
                
        print(f"  ✓ Success: {request_results['success']}")
        print(f"  ✗ Failed: {request_results['failed']}")
        
        # Circuit breaker status
        print("\n⚡ Circuit Breaker Status:")
        
        for name, cb in platform.circuit_breaker_manager.breakers.items():
            state_icon = {"closed": "🟢", "open": "🔴", "half_open": "🟡"}.get(cb.state.value, "⚪")
            print(f"  {state_icon} {name}: {cb.state.value} (failures: {cb.failure_count})")
            
        # Service statistics
        print("\n📊 Service Statistics:")
        
        for service in created_services:
            errors = sum(ep.error_count for ep in service.endpoints)
            error_rate = (errors / service.total_requests * 100) if service.total_requests > 0 else 0
            print(f"  {service.name}: {service.total_requests} requests ({error_rate:.1f}% errors)")
            
        # Load balancer distribution
        print("\n⚖️ Load Balancer Distribution:")
        
        for service in created_services[:3]:
            print(f"  {service.name} ({service.load_balancer.value}):")
            for ep in service.endpoints:
                pct = (ep.request_count / service.total_requests * 100) if service.total_requests > 0 else 0
                bar = "█" * int(pct / 5)
                print(f"    {ep.address}:{ep.port}: {bar} {pct:.1f}%")
                
        # Sidecar statistics
        print("\n🔧 Sidecar Statistics:")
        
        total_sidecars = len(platform.sidecar_manager.sidecars)
        healthy_sidecars = sum(1 for s in platform.sidecar_manager.sidecars.values() 
                              if s.status == ServiceStatus.HEALTHY)
        print(f"  Total: {total_sidecars}")
        print(f"  Healthy: {healthy_sidecars}")
        
        # Platform statistics
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Services:")
        print(f"    Total: {stats['total_services']}")
        print(f"    Endpoints: {stats['total_endpoints']}")
        print(f"    Healthy: {stats['healthy_endpoints']}")
        
        print(f"\n  Sidecars: {stats['total_sidecars']}")
        print(f"  Virtual Services: {stats['virtual_services']}")
        print(f"  Circuit Breakers: {stats['circuit_breakers']}")
        
        print(f"\n  Traffic:")
        print(f"    Total Requests: {stats['total_requests']}")
        
        # Dashboard
        print("\n📋 Service Mesh Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │                Service Mesh Overview                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Services:             {stats['total_services']:>10}                      │")
        print(f"  │ Endpoints:            {stats['total_endpoints']:>10}                      │")
        print(f"  │ Healthy Endpoints:    {stats['healthy_endpoints']:>10}                      │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Sidecars:             {stats['total_sidecars']:>10}                      │")
        print(f"  │ Virtual Services:     {stats['virtual_services']:>10}                      │")
        print(f"  │ Circuit Breakers:     {stats['circuit_breakers']:>10}                      │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Requests:       {stats['total_requests']:>10}                      │")
        print(f"  │ Success Rate:         {request_results['success']}%                        │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Service Mesh Platform initialized!")
    print("=" * 60)
