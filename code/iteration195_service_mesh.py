#!/usr/bin/env python3
"""
Server Init - Iteration 195: Service Mesh Platform
Платформа сервисной сетки

Функционал:
- Sidecar Management - управление sidecar прокси
- Traffic Routing - маршрутизация трафика
- Load Balancing - балансировка нагрузки
- Circuit Breaker - предохранители
- Retry Policies - политики повторов
- Rate Limiting - ограничение запросов
- mTLS - взаимный TLS
- Service Registry - реестр сервисов
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid


class ProxyStatus(Enum):
    """Статус прокси"""
    RUNNING = "running"
    STARTING = "starting"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class LoadBalancerType(Enum):
    """Тип балансировщика"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"
    WEIGHTED = "weighted"
    CONSISTENT_HASH = "consistent_hash"


class CircuitState(Enum):
    """Состояние предохранителя"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class TLSMode(Enum):
    """Режим TLS"""
    DISABLE = "disable"
    PERMISSIVE = "permissive"
    STRICT = "strict"


@dataclass
class ServiceEndpoint:
    """Эндпоинт сервиса"""
    endpoint_id: str
    service_name: str = ""
    host: str = ""
    port: int = 80
    
    # Health
    healthy: bool = True
    last_health_check: datetime = field(default_factory=datetime.now)
    
    # Weight
    weight: int = 100
    
    # Metadata
    labels: Dict[str, str] = field(default_factory=dict)
    zone: str = ""


@dataclass
class SidecarProxy:
    """Sidecar прокси"""
    proxy_id: str
    service_name: str = ""
    pod_name: str = ""
    
    # Status
    status: ProxyStatus = ProxyStatus.STOPPED
    
    # Version
    version: str = "1.0.0"
    
    # Config
    inbound_port: int = 15001
    outbound_port: int = 15002
    admin_port: int = 15000
    
    # Stats
    requests_total: int = 0
    requests_success: int = 0
    requests_failed: int = 0
    
    # Started
    started_at: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        return (self.requests_success / self.requests_total * 100) if self.requests_total > 0 else 100


@dataclass
class VirtualService:
    """Виртуальный сервис"""
    vs_id: str
    name: str = ""
    
    # Hosts
    hosts: List[str] = field(default_factory=list)
    
    # Routes
    routes: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timeout
    timeout_ms: int = 30000
    
    # Retries
    retries: int = 3
    retry_on: List[str] = field(default_factory=lambda: ["5xx", "reset", "connect-failure"])
    
    # Created
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DestinationRule:
    """Правило назначения"""
    rule_id: str
    host: str = ""
    
    # Load balancer
    lb_type: LoadBalancerType = LoadBalancerType.ROUND_ROBIN
    
    # Connection pool
    max_connections: int = 1000
    max_pending_requests: int = 100
    max_requests_per_connection: int = 100
    
    # TLS
    tls_mode: TLSMode = TLSMode.STRICT
    
    # Subsets
    subsets: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class CircuitBreaker:
    """Предохранитель"""
    cb_id: str
    service_name: str = ""
    
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
    
    def record_success(self):
        """Запись успеха"""
        self.success_count += 1
        self.failure_count = 0
        
        if self.state == CircuitState.HALF_OPEN:
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.success_count = 0
                
    def record_failure(self):
        """Запись отказа"""
        self.failure_count += 1
        self.success_count = 0
        self.last_failure = datetime.now()
        
        if self.state == CircuitState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                self.opened_at = datetime.now()
                
    def can_execute(self) -> bool:
        """Можно ли выполнить запрос"""
        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            if self.opened_at and (datetime.now() - self.opened_at).seconds >= self.timeout_seconds:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
        else:  # HALF_OPEN
            return True


@dataclass
class RateLimiter:
    """Ограничитель запросов"""
    rl_id: str
    service_name: str = ""
    
    # Limits
    requests_per_second: int = 100
    burst_size: int = 200
    
    # Current
    tokens: float = 0
    last_update: datetime = field(default_factory=datetime.now)
    
    def allow(self) -> bool:
        """Разрешить запрос"""
        now = datetime.now()
        elapsed = (now - self.last_update).total_seconds()
        
        # Add tokens
        self.tokens = min(self.burst_size, self.tokens + elapsed * self.requests_per_second)
        self.last_update = now
        
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


class ServiceRegistry:
    """Реестр сервисов"""
    
    def __init__(self):
        self.services: Dict[str, List[ServiceEndpoint]] = {}
        
    def register(self, endpoint: ServiceEndpoint):
        """Регистрация эндпоинта"""
        if endpoint.service_name not in self.services:
            self.services[endpoint.service_name] = []
        self.services[endpoint.service_name].append(endpoint)
        
    def deregister(self, endpoint_id: str):
        """Отмена регистрации"""
        for service_name, endpoints in self.services.items():
            self.services[service_name] = [e for e in endpoints if e.endpoint_id != endpoint_id]
            
    def get_endpoints(self, service_name: str) -> List[ServiceEndpoint]:
        """Получение эндпоинтов"""
        return [e for e in self.services.get(service_name, []) if e.healthy]
        
    def get_all_services(self) -> List[str]:
        """Все сервисы"""
        return list(self.services.keys())


class LoadBalancer:
    """Балансировщик нагрузки"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.counters: Dict[str, int] = {}
        self.connections: Dict[str, int] = {}
        
    def select(self, service_name: str, lb_type: LoadBalancerType) -> Optional[ServiceEndpoint]:
        """Выбор эндпоинта"""
        endpoints = self.registry.get_endpoints(service_name)
        if not endpoints:
            return None
            
        if lb_type == LoadBalancerType.ROUND_ROBIN:
            return self._round_robin(service_name, endpoints)
        elif lb_type == LoadBalancerType.LEAST_CONNECTIONS:
            return self._least_connections(endpoints)
        elif lb_type == LoadBalancerType.RANDOM:
            return random.choice(endpoints)
        elif lb_type == LoadBalancerType.WEIGHTED:
            return self._weighted(endpoints)
        else:
            return random.choice(endpoints)
            
    def _round_robin(self, service: str, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Round Robin"""
        idx = self.counters.get(service, 0)
        endpoint = endpoints[idx % len(endpoints)]
        self.counters[service] = idx + 1
        return endpoint
        
    def _least_connections(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Least Connections"""
        return min(endpoints, key=lambda e: self.connections.get(e.endpoint_id, 0))
        
    def _weighted(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Weighted"""
        total_weight = sum(e.weight for e in endpoints)
        r = random.randint(1, total_weight)
        
        for endpoint in endpoints:
            r -= endpoint.weight
            if r <= 0:
                return endpoint
        return endpoints[-1]


class ProxyManager:
    """Менеджер прокси"""
    
    def __init__(self):
        self.proxies: Dict[str, SidecarProxy] = {}
        
    def deploy(self, service_name: str, pod_name: str) -> SidecarProxy:
        """Развёртывание прокси"""
        proxy = SidecarProxy(
            proxy_id=f"proxy_{uuid.uuid4().hex[:8]}",
            service_name=service_name,
            pod_name=pod_name,
            status=ProxyStatus.STARTING
        )
        
        self.proxies[proxy.proxy_id] = proxy
        proxy.status = ProxyStatus.RUNNING
        proxy.started_at = datetime.now()
        
        return proxy
        
    def remove(self, proxy_id: str):
        """Удаление прокси"""
        if proxy_id in self.proxies:
            self.proxies[proxy_id].status = ProxyStatus.STOPPED
            del self.proxies[proxy_id]
            
    def get_by_service(self, service_name: str) -> List[SidecarProxy]:
        """Получение прокси по сервису"""
        return [p for p in self.proxies.values() if p.service_name == service_name]


class TrafficRouter:
    """Маршрутизатор трафика"""
    
    def __init__(self, lb: LoadBalancer):
        self.lb = lb
        self.virtual_services: Dict[str, VirtualService] = {}
        self.destination_rules: Dict[str, DestinationRule] = {}
        
    def add_virtual_service(self, vs: VirtualService):
        """Добавление виртуального сервиса"""
        self.virtual_services[vs.vs_id] = vs
        
    def add_destination_rule(self, rule: DestinationRule):
        """Добавление правила"""
        self.destination_rules[rule.rule_id] = rule
        
    def route(self, host: str, path: str = "/") -> Optional[ServiceEndpoint]:
        """Маршрутизация"""
        # Find virtual service
        vs = None
        for v in self.virtual_services.values():
            if host in v.hosts:
                vs = v
                break
                
        if not vs:
            return None
            
        # Find matching route
        for route in vs.routes:
            if self._match_route(route, path):
                destination = route.get("destination", {})
                service = destination.get("host", host)
                
                # Get destination rule
                rule = self._get_destination_rule(service)
                lb_type = rule.lb_type if rule else LoadBalancerType.ROUND_ROBIN
                
                return self.lb.select(service, lb_type)
                
        # Default route
        return self.lb.select(host, LoadBalancerType.ROUND_ROBIN)
        
    def _match_route(self, route: Dict[str, Any], path: str) -> bool:
        """Сопоставление маршрута"""
        match = route.get("match", {})
        uri = match.get("uri", {})
        
        if "prefix" in uri:
            return path.startswith(uri["prefix"])
        if "exact" in uri:
            return path == uri["exact"]
            
        return True
        
    def _get_destination_rule(self, host: str) -> Optional[DestinationRule]:
        """Получение правила"""
        for rule in self.destination_rules.values():
            if rule.host == host:
                return rule
        return None


class ServiceMeshPlatform:
    """Платформа сервисной сетки"""
    
    def __init__(self):
        self.registry = ServiceRegistry()
        self.lb = LoadBalancer(self.registry)
        self.proxy_manager = ProxyManager()
        self.router = TrafficRouter(self.lb)
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.rate_limiters: Dict[str, RateLimiter] = {}
        
    def get_circuit_breaker(self, service: str) -> CircuitBreaker:
        """Получение или создание CB"""
        if service not in self.circuit_breakers:
            self.circuit_breakers[service] = CircuitBreaker(
                cb_id=f"cb_{uuid.uuid4().hex[:8]}",
                service_name=service
            )
        return self.circuit_breakers[service]
        
    def get_rate_limiter(self, service: str) -> RateLimiter:
        """Получение или создание RL"""
        if service not in self.rate_limiters:
            self.rate_limiters[service] = RateLimiter(
                rl_id=f"rl_{uuid.uuid4().hex[:8]}",
                service_name=service
            )
        return self.rate_limiters[service]
        
    async def call_service(self, service: str, path: str = "/") -> Dict[str, Any]:
        """Вызов сервиса"""
        # Check rate limit
        rl = self.get_rate_limiter(service)
        if not rl.allow():
            return {"status": "rate_limited", "service": service}
            
        # Check circuit breaker
        cb = self.get_circuit_breaker(service)
        if not cb.can_execute():
            return {"status": "circuit_open", "service": service}
            
        # Route request
        endpoint = self.router.route(service, path)
        if not endpoint:
            cb.record_failure()
            return {"status": "no_endpoint", "service": service}
            
        # Simulate call
        success = random.random() > 0.1
        
        if success:
            cb.record_success()
            return {
                "status": "success",
                "service": service,
                "endpoint": endpoint.host,
                "port": endpoint.port
            }
        else:
            cb.record_failure()
            return {"status": "failed", "service": service}
            
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        proxies = list(self.proxy_manager.proxies.values())
        running = len([p for p in proxies if p.status == ProxyStatus.RUNNING])
        
        return {
            "total_services": len(self.registry.services),
            "total_endpoints": sum(len(e) for e in self.registry.services.values()),
            "total_proxies": len(proxies),
            "running_proxies": running,
            "virtual_services": len(self.router.virtual_services),
            "destination_rules": len(self.router.destination_rules),
            "circuit_breakers": len(self.circuit_breakers),
            "rate_limiters": len(self.rate_limiters)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 195: Service Mesh Platform")
    print("=" * 60)
    
    platform = ServiceMeshPlatform()
    print("✓ Service Mesh Platform created")
    
    # Register services
    print("\n🔧 Registering Services...")
    
    services = ["api-gateway", "user-service", "order-service", "payment-service", "notification-service"]
    
    for svc in services:
        for i in range(3):
            endpoint = ServiceEndpoint(
                endpoint_id=f"ep_{uuid.uuid4().hex[:8]}",
                service_name=svc,
                host=f"{svc}-{i}.default.svc.cluster.local",
                port=8080,
                weight=random.randint(50, 100),
                zone=random.choice(["us-east-1a", "us-east-1b", "us-east-1c"])
            )
            platform.registry.register(endpoint)
            
    print(f"  Registered {len(services)} services with {sum(len(e) for e in platform.registry.services.values())} endpoints")
    
    # Deploy sidecars
    print("\n📦 Deploying Sidecar Proxies...")
    
    for svc in services:
        for i in range(3):
            proxy = platform.proxy_manager.deploy(svc, f"{svc}-pod-{i}")
            
    print(f"  Deployed {len(platform.proxy_manager.proxies)} sidecar proxies")
    
    # Create virtual services
    print("\n🌐 Creating Virtual Services...")
    
    for svc in services:
        vs = VirtualService(
            vs_id=f"vs_{uuid.uuid4().hex[:8]}",
            name=f"{svc}-vs",
            hosts=[svc],
            routes=[
                {
                    "match": {"uri": {"prefix": "/api/v1"}},
                    "destination": {"host": svc}
                },
                {
                    "match": {"uri": {"prefix": "/api/v2"}},
                    "destination": {"host": svc}
                }
            ],
            timeout_ms=30000,
            retries=3
        )
        platform.router.add_virtual_service(vs)
        
    print(f"  Created {len(platform.router.virtual_services)} virtual services")
    
    # Create destination rules
    print("\n📋 Creating Destination Rules...")
    
    for svc in services:
        rule = DestinationRule(
            rule_id=f"dr_{uuid.uuid4().hex[:8]}",
            host=svc,
            lb_type=random.choice(list(LoadBalancerType)),
            tls_mode=TLSMode.STRICT,
            max_connections=1000
        )
        platform.router.add_destination_rule(rule)
        
    print(f"  Created {len(platform.router.destination_rules)} destination rules")
    
    # Simulate traffic
    print("\n🚀 Simulating Traffic...")
    
    results = {"success": 0, "failed": 0, "rate_limited": 0, "circuit_open": 0}
    
    for _ in range(200):
        svc = random.choice(services)
        path = random.choice(["/api/v1/data", "/api/v2/users", "/api/v1/orders"])
        
        result = await platform.call_service(svc, path)
        results[result["status"]] = results.get(result["status"], 0) + 1
        
    print(f"\n  Traffic Results:")
    for status, count in results.items():
        bar = "█" * (count // 5) + "░" * (40 - count // 5)
        print(f"    {status:15} [{bar}] {count}")
        
    # Service mesh status
    print("\n📊 Service Mesh Status:")
    
    print("\n  ┌─────────────────────────┬──────────┬───────────┬──────────────┐")
    print("  │ Service                 │ Proxies  │ Endpoints │ LB Type      │")
    print("  ├─────────────────────────┼──────────┼───────────┼──────────────┤")
    
    for svc in services:
        proxies = len(platform.proxy_manager.get_by_service(svc))
        endpoints = len(platform.registry.get_endpoints(svc))
        rule = platform.router._get_destination_rule(svc)
        lb = rule.lb_type.value if rule else "n/a"
        
        name = svc[:23].ljust(23)
        p = str(proxies).center(8)
        e = str(endpoints).center(9)
        l = lb[:12].ljust(12)
        print(f"  │ {name} │ {p} │ {e} │ {l} │")
        
    print("  └─────────────────────────┴──────────┴───────────┴──────────────┘")
    
    # Circuit breaker status
    print("\n⚡ Circuit Breaker Status:")
    
    for svc, cb in platform.circuit_breakers.items():
        state_icon = "🟢" if cb.state == CircuitState.CLOSED else ("🟡" if cb.state == CircuitState.HALF_OPEN else "🔴")
        print(f"  {state_icon} {svc}: {cb.state.value} (failures: {cb.failure_count})")
        
    # Rate limiter status
    print("\n🚦 Rate Limiter Status:")
    
    for svc, rl in platform.rate_limiters.items():
        tokens = f"{rl.tokens:.1f}/{rl.burst_size}"
        print(f"  📊 {svc}: {tokens} tokens, {rl.requests_per_second} req/s")
        
    # Proxy statistics
    print("\n📈 Proxy Statistics:")
    
    total_requests = sum(p.requests_total for p in platform.proxy_manager.proxies.values())
    total_success = sum(p.requests_success for p in platform.proxy_manager.proxies.values())
    
    print(f"\n  Total Requests: {total_requests}")
    print(f"  Total Success: {total_success}")
    
    running = [p for p in platform.proxy_manager.proxies.values() if p.status == ProxyStatus.RUNNING]
    print(f"  Running Proxies: {len(running)}")
    
    # Statistics
    stats = platform.get_statistics()
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                      Service Mesh Dashboard                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Services:                {stats['total_services']:>12}                        │")
    print(f"│ Total Endpoints:               {stats['total_endpoints']:>12}                        │")
    print(f"│ Running Proxies:               {stats['running_proxies']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Virtual Services:              {stats['virtual_services']:>12}                        │")
    print(f"│ Destination Rules:             {stats['destination_rules']:>12}                        │")
    print(f"│ Circuit Breakers:              {stats['circuit_breakers']:>12}                        │")
    print(f"│ Rate Limiters:                 {stats['rate_limiters']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Service Mesh Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
