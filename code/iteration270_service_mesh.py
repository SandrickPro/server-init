#!/usr/bin/env python3
"""
Server Init - Iteration 270: Service Mesh Platform
Платформа сервисной сетки

Функционал:
- Service Registration - регистрация сервисов
- Traffic Management - управление трафиком
- mTLS Security - безопасность mTLS
- Observability - наблюдаемость
- Policy Enforcement - применение политик
- Load Balancing - балансировка нагрузки
- Circuit Breaking - прерывание цепи
- Service Discovery - обнаружение сервисов
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import hashlib


class ServiceStatus(Enum):
    """Статус сервиса"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class ProxyStatus(Enum):
    """Статус прокси"""
    ACTIVE = "active"
    SYNCING = "syncing"
    DISCONNECTED = "disconnected"


class TrafficPolicy(Enum):
    """Политика трафика"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONN = "least_conn"
    RANDOM = "random"
    PASSTHROUGH = "passthrough"


class TLSMode(Enum):
    """Режим TLS"""
    DISABLED = "disabled"
    PERMISSIVE = "permissive"
    STRICT = "strict"
    MUTUAL = "mutual"


class RateLimitAction(Enum):
    """Действие при превышении лимита"""
    DENY = "deny"
    LOG = "log"
    THROTTLE = "throttle"


@dataclass
class Certificate:
    """Сертификат"""
    cert_id: str
    
    # Subject
    common_name: str = ""
    organization: str = ""
    
    # Validity
    not_before: datetime = field(default_factory=datetime.now)
    not_after: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=365))
    
    # Type
    is_ca: bool = False
    
    # Fingerprint
    fingerprint: str = ""


@dataclass
class SidecarProxy:
    """Sidecar прокси"""
    proxy_id: str
    
    # Service
    service_name: str = ""
    instance_id: str = ""
    
    # Status
    status: ProxyStatus = ProxyStatus.ACTIVE
    
    # Ports
    inbound_port: int = 15006
    outbound_port: int = 15001
    admin_port: int = 15000
    
    # Config version
    config_version: str = ""
    last_sync: datetime = field(default_factory=datetime.now)
    
    # Stats
    requests_in: int = 0
    requests_out: int = 0
    
    # Certificate
    certificate: Optional[Certificate] = None


@dataclass
class ServiceEndpoint:
    """Эндпоинт сервиса"""
    endpoint_id: str
    
    # Address
    address: str = ""
    port: int = 80
    
    # Health
    healthy: bool = True
    
    # Weight
    weight: int = 100
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class MeshService:
    """Сервис в сетке"""
    service_id: str
    name: str
    namespace: str = "default"
    
    # Endpoints
    endpoints: List[ServiceEndpoint] = field(default_factory=list)
    
    # Proxies
    proxies: List[SidecarProxy] = field(default_factory=list)
    
    # Status
    status: ServiceStatus = ServiceStatus.HEALTHY
    
    # Config
    traffic_policy: TrafficPolicy = TrafficPolicy.ROUND_ROBIN
    tls_mode: TLSMode = TLSMode.STRICT
    
    # Ports
    ports: Dict[str, int] = field(default_factory=dict)
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Stats
    total_requests: int = 0
    error_count: int = 0
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TrafficRule:
    """Правило трафика"""
    rule_id: str
    name: str
    
    # Match
    source_service: str = "*"
    destination_service: str = ""
    
    # Action
    action: str = "allow"  # allow, deny, redirect
    
    # Routing
    weight_distribution: Dict[str, int] = field(default_factory=dict)  # version -> weight
    
    # Headers
    match_headers: Dict[str, str] = field(default_factory=dict)
    add_headers: Dict[str, str] = field(default_factory=dict)
    
    # Timeout
    timeout_seconds: int = 30
    
    # Retry
    retries: int = 3
    
    # Priority
    priority: int = 100


@dataclass
class RateLimitRule:
    """Правило ограничения скорости"""
    rule_id: str
    name: str
    
    # Target
    service_name: str = ""
    path: str = "*"
    
    # Limits
    requests_per_second: int = 100
    burst_size: int = 200
    
    # Action
    action: RateLimitAction = RateLimitAction.DENY
    
    # Scope
    per_source: bool = True


@dataclass
class CircuitBreakerConfig:
    """Конфигурация circuit breaker"""
    config_id: str
    service_name: str
    
    # Thresholds
    consecutive_errors: int = 5
    interval_seconds: int = 10
    
    # Ejection
    base_ejection_time_seconds: int = 30
    max_ejection_percent: int = 50
    
    # Detection
    consecutive_gateway_errors: int = 5
    consecutive_5xx_errors: int = 5


@dataclass
class MeshPolicy:
    """Политика сетки"""
    policy_id: str
    name: str
    
    # Scope
    namespace: str = "*"
    
    # mTLS
    mtls_mode: TLSMode = TLSMode.STRICT
    
    # Authorization
    allowed_services: List[str] = field(default_factory=list)
    
    # Active
    active: bool = True


@dataclass
class TrafficMetrics:
    """Метрики трафика"""
    metrics_id: str
    
    # Service
    source_service: str = ""
    destination_service: str = ""
    
    # Counts
    request_count: int = 0
    success_count: int = 0
    error_count: int = 0
    
    # Latency
    latency_p50_ms: float = 0
    latency_p95_ms: float = 0
    latency_p99_ms: float = 0
    
    # Time window
    window_start: datetime = field(default_factory=datetime.now)
    window_end: datetime = field(default_factory=datetime.now)


class ServiceMeshManager:
    """Менеджер сервисной сетки"""
    
    def __init__(self, mesh_name: str = "default-mesh"):
        self.mesh_name = mesh_name
        self.services: Dict[str, MeshService] = {}
        self.traffic_rules: Dict[str, TrafficRule] = {}
        self.rate_limits: Dict[str, RateLimitRule] = {}
        self.circuit_breakers: Dict[str, CircuitBreakerConfig] = {}
        self.policies: Dict[str, MeshPolicy] = {}
        self.metrics: List[TrafficMetrics] = []
        self._root_ca: Optional[Certificate] = None
        
    def _init_pki(self):
        """Инициализация PKI"""
        self._root_ca = Certificate(
            cert_id=f"ca_{uuid.uuid4().hex[:8]}",
            common_name=f"{self.mesh_name}-ca",
            organization="Service Mesh",
            is_ca=True,
            fingerprint=hashlib.sha256(self.mesh_name.encode()).hexdigest()[:40]
        )
        
    def _issue_certificate(self, service_name: str) -> Certificate:
        """Выдача сертификата"""
        if not self._root_ca:
            self._init_pki()
            
        return Certificate(
            cert_id=f"cert_{uuid.uuid4().hex[:8]}",
            common_name=f"{service_name}.{self.mesh_name}.local",
            organization=self.mesh_name,
            fingerprint=hashlib.sha256(f"{service_name}-{datetime.now()}".encode()).hexdigest()[:40]
        )
        
    def register_service(self, name: str, namespace: str = "default",
                        ports: Dict[str, int] = None,
                        replicas: int = 1) -> MeshService:
        """Регистрация сервиса"""
        service = MeshService(
            service_id=f"svc_{uuid.uuid4().hex[:8]}",
            name=name,
            namespace=namespace,
            ports=ports or {"http": 8080}
        )
        
        # Create endpoints and proxies
        for i in range(replicas):
            endpoint = ServiceEndpoint(
                endpoint_id=f"ep_{uuid.uuid4().hex[:8]}",
                address=f"10.0.{random.randint(1, 255)}.{i+1}",
                port=list(service.ports.values())[0] if service.ports else 8080
            )
            service.endpoints.append(endpoint)
            
            # Create sidecar proxy
            proxy = SidecarProxy(
                proxy_id=f"proxy_{uuid.uuid4().hex[:8]}",
                service_name=name,
                instance_id=endpoint.endpoint_id,
                certificate=self._issue_certificate(name)
            )
            service.proxies.append(proxy)
            
        self.services[name] = service
        return service
        
    def create_traffic_rule(self, name: str,
                           destination: str,
                           source: str = "*",
                           timeout: int = 30,
                           retries: int = 3) -> TrafficRule:
        """Создание правила трафика"""
        rule = TrafficRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name=name,
            source_service=source,
            destination_service=destination,
            timeout_seconds=timeout,
            retries=retries
        )
        
        self.traffic_rules[name] = rule
        return rule
        
    def set_weight_distribution(self, rule_name: str,
                               distribution: Dict[str, int]):
        """Установка распределения весов"""
        rule = self.traffic_rules.get(rule_name)
        if rule:
            rule.weight_distribution = distribution
            
    def create_rate_limit(self, name: str,
                         service_name: str,
                         rps: int = 100,
                         burst: int = 200) -> RateLimitRule:
        """Создание ограничения скорости"""
        rule = RateLimitRule(
            rule_id=f"rl_{uuid.uuid4().hex[:8]}",
            name=name,
            service_name=service_name,
            requests_per_second=rps,
            burst_size=burst
        )
        
        self.rate_limits[name] = rule
        return rule
        
    def configure_circuit_breaker(self, service_name: str,
                                  consecutive_errors: int = 5,
                                  ejection_time: int = 30) -> CircuitBreakerConfig:
        """Конфигурация circuit breaker"""
        config = CircuitBreakerConfig(
            config_id=f"cb_{uuid.uuid4().hex[:8]}",
            service_name=service_name,
            consecutive_errors=consecutive_errors,
            base_ejection_time_seconds=ejection_time
        )
        
        self.circuit_breakers[service_name] = config
        return config
        
    def create_policy(self, name: str,
                     namespace: str = "*",
                     mtls_mode: TLSMode = TLSMode.STRICT) -> MeshPolicy:
        """Создание политики"""
        policy = MeshPolicy(
            policy_id=f"policy_{uuid.uuid4().hex[:8]}",
            name=name,
            namespace=namespace,
            mtls_mode=mtls_mode
        )
        
        self.policies[name] = policy
        return policy
        
    def add_service_authorization(self, policy_name: str,
                                 allowed_services: List[str]):
        """Добавление авторизации сервисов"""
        policy = self.policies.get(policy_name)
        if policy:
            policy.allowed_services.extend(allowed_services)
            
    async def route_request(self, source: str, destination: str,
                           path: str = "/",
                           headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Маршрутизация запроса"""
        result = {
            "allowed": False,
            "destination": None,
            "endpoint": None,
            "latency_ms": 0
        }
        
        # Check service exists
        dest_service = self.services.get(destination)
        if not dest_service:
            return result
            
        # Check policies
        for policy in self.policies.values():
            if policy.active and policy.namespace in ["*", dest_service.namespace]:
                if policy.allowed_services and source not in policy.allowed_services:
                    return result
                    
        # Check rate limits
        for rate_limit in self.rate_limits.values():
            if rate_limit.service_name == destination:
                # Simulate rate limit check
                if random.random() < 0.05:  # 5% rejection
                    result["rate_limited"] = True
                    return result
                    
        # Select endpoint
        healthy_endpoints = [e for e in dest_service.endpoints if e.healthy]
        if not healthy_endpoints:
            return result
            
        # Apply traffic policy
        if dest_service.traffic_policy == TrafficPolicy.ROUND_ROBIN:
            endpoint = healthy_endpoints[dest_service.total_requests % len(healthy_endpoints)]
        elif dest_service.traffic_policy == TrafficPolicy.LEAST_CONN:
            endpoint = random.choice(healthy_endpoints)
        else:
            endpoint = random.choice(healthy_endpoints)
            
        # Simulate request
        await asyncio.sleep(random.uniform(0.001, 0.01))
        
        # Update stats
        dest_service.total_requests += 1
        
        result["allowed"] = True
        result["destination"] = destination
        result["endpoint"] = f"{endpoint.address}:{endpoint.port}"
        result["latency_ms"] = random.uniform(5, 50)
        
        # Record metrics
        self._record_metrics(source, destination, result["latency_ms"])
        
        return result
        
    def _record_metrics(self, source: str, destination: str,
                       latency_ms: float):
        """Запись метрик"""
        # Find or create metrics
        existing = next(
            (m for m in self.metrics
             if m.source_service == source and m.destination_service == destination),
            None
        )
        
        if existing:
            existing.request_count += 1
            existing.success_count += 1
            existing.latency_p50_ms = (existing.latency_p50_ms + latency_ms) / 2
        else:
            metrics = TrafficMetrics(
                metrics_id=f"metrics_{uuid.uuid4().hex[:8]}",
                source_service=source,
                destination_service=destination,
                request_count=1,
                success_count=1,
                latency_p50_ms=latency_ms
            )
            self.metrics.append(metrics)
            
    def get_service_graph(self) -> Dict[str, List[str]]:
        """Получение графа сервисов"""
        graph = {}
        
        for metrics in self.metrics:
            if metrics.source_service not in graph:
                graph[metrics.source_service] = []
            if metrics.destination_service not in graph[metrics.source_service]:
                graph[metrics.source_service].append(metrics.destination_service)
                
        return graph
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_proxies = sum(len(s.proxies) for s in self.services.values())
        total_endpoints = sum(len(s.endpoints) for s in self.services.values())
        healthy_endpoints = sum(
            sum(1 for e in s.endpoints if e.healthy)
            for s in self.services.values()
        )
        
        return {
            "services_total": len(self.services),
            "proxies_total": total_proxies,
            "endpoints_total": total_endpoints,
            "healthy_endpoints": healthy_endpoints,
            "traffic_rules": len(self.traffic_rules),
            "rate_limits": len(self.rate_limits),
            "circuit_breakers": len(self.circuit_breakers),
            "policies": len(self.policies),
            "metrics_count": len(self.metrics)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 270: Service Mesh Platform")
    print("=" * 60)
    
    manager = ServiceMeshManager("production-mesh")
    print("✓ Service Mesh Manager created")
    
    # Register services
    print("\n📦 Registering Services...")
    
    services_config = [
        ("api-gateway", "ingress", {"http": 8080, "grpc": 9090}, 3),
        ("user-service", "default", {"http": 8081}, 2),
        ("order-service", "default", {"http": 8082}, 3),
        ("payment-service", "default", {"http": 8083}, 2),
        ("notification-service", "default", {"http": 8084}, 1),
        ("inventory-service", "default", {"http": 8085}, 2),
    ]
    
    for name, ns, ports, replicas in services_config:
        service = manager.register_service(name, ns, ports, replicas)
        print(f"  📦 {name} ({ns}): {replicas} replicas, ports={list(ports.keys())}")
        
    # Create traffic rules
    print("\n🛤️ Creating Traffic Rules...")
    
    rules = [
        ("gateway-to-users", "user-service", "api-gateway", 10, 3),
        ("gateway-to-orders", "order-service", "api-gateway", 15, 3),
        ("orders-to-payment", "payment-service", "order-service", 30, 5),
        ("orders-to-inventory", "inventory-service", "order-service", 10, 3),
    ]
    
    for name, dest, src, timeout, retries in rules:
        rule = manager.create_traffic_rule(name, dest, src, timeout, retries)
        print(f"  🛤️ {name}: {src} -> {dest} (timeout={timeout}s, retries={retries})")
        
    # Set canary weights
    manager.set_weight_distribution("gateway-to-users", {"v1": 90, "v2": 10})
    print(f"  ⚖️ gateway-to-users: v1=90%, v2=10%")
    
    # Create rate limits
    print("\n⏱️ Creating Rate Limits...")
    
    rate_limits = [
        ("api-gateway-limit", "api-gateway", 1000, 2000),
        ("payment-limit", "payment-service", 100, 150),
    ]
    
    for name, service, rps, burst in rate_limits:
        rl = manager.create_rate_limit(name, service, rps, burst)
        print(f"  ⏱️ {name}: {rps} RPS, burst={burst}")
        
    # Configure circuit breakers
    print("\n🔌 Configuring Circuit Breakers...")
    
    for service_name in ["payment-service", "inventory-service"]:
        cb = manager.configure_circuit_breaker(service_name, 5, 30)
        print(f"  🔌 {service_name}: 5 errors, 30s ejection")
        
    # Create policies
    print("\n📜 Creating Policies...")
    
    # Strict mTLS for default namespace
    policy = manager.create_policy("default-mtls", "default", TLSMode.STRICT)
    manager.add_service_authorization("default-mtls", ["api-gateway", "user-service", "order-service"])
    print(f"  📜 default-mtls: STRICT mTLS")
    
    # Permissive for ingress
    manager.create_policy("ingress-mtls", "ingress", TLSMode.PERMISSIVE)
    print(f"  📜 ingress-mtls: PERMISSIVE mTLS")
    
    # Simulate traffic
    print("\n🔄 Simulating Traffic...")
    
    traffic_patterns = [
        ("api-gateway", "user-service", 20),
        ("api-gateway", "order-service", 15),
        ("order-service", "payment-service", 10),
        ("order-service", "inventory-service", 10),
        ("order-service", "notification-service", 5),
    ]
    
    for source, dest, count in traffic_patterns:
        success = 0
        for _ in range(count):
            result = await manager.route_request(source, dest)
            if result["allowed"]:
                success += 1
                
        print(f"  {source} -> {dest}: {success}/{count} requests")
        
    # Display services
    print("\n📦 Mesh Services:")
    
    print("\n  ┌─────────────────────┬───────────┬──────────┬──────────┬─────────────┐")
    print("  │ Service             │ Namespace │ Replicas │ Status   │ Requests    │")
    print("  ├─────────────────────┼───────────┼──────────┼──────────┼─────────────┤")
    
    for service in manager.services.values():
        name = service.name[:19].ljust(19)
        ns = service.namespace[:9].ljust(9)
        replicas = str(len(service.endpoints))[:8].ljust(8)
        status = service.status.value[:8].ljust(8)
        requests = str(service.total_requests)[:11].ljust(11)
        
        print(f"  │ {name} │ {ns} │ {replicas} │ {status} │ {requests} │")
        
    print("  └─────────────────────┴───────────┴──────────┴──────────┴─────────────┘")
    
    # Display proxies
    print("\n🔲 Sidecar Proxies:")
    
    print("\n  ┌─────────────────────┬────────────────────┬──────────┬─────────────────────┐")
    print("  │ Service             │ Proxy ID           │ Status   │ Certificate         │")
    print("  ├─────────────────────┼────────────────────┼──────────┼─────────────────────┤")
    
    for service in list(manager.services.values())[:3]:
        for proxy in service.proxies[:1]:
            svc = service.name[:19].ljust(19)
            pid = proxy.proxy_id[:18].ljust(18)
            status = proxy.status.value[:8].ljust(8)
            cert = (proxy.certificate.fingerprint[:19] if proxy.certificate else "N/A").ljust(19)
            
            print(f"  │ {svc} │ {pid} │ {status} │ {cert} │")
            
    print("  └─────────────────────┴────────────────────┴──────────┴─────────────────────┘")
    
    # Traffic rules
    print("\n🛤️ Traffic Rules:")
    
    for rule in manager.traffic_rules.values():
        print(f"\n  {rule.name}:")
        print(f"    Source: {rule.source_service} -> Dest: {rule.destination_service}")
        print(f"    Timeout: {rule.timeout_seconds}s, Retries: {rule.retries}")
        if rule.weight_distribution:
            print(f"    Weights: {rule.weight_distribution}")
            
    # Service graph
    print("\n🕸️ Service Graph:")
    
    graph = manager.get_service_graph()
    
    for source, destinations in graph.items():
        for dest in destinations:
            print(f"  {source} ──────> {dest}")
            
    # Traffic metrics
    print("\n📊 Traffic Metrics:")
    
    print("\n  ┌─────────────────────┬─────────────────────┬──────────┬──────────┬──────────┐")
    print("  │ Source              │ Destination         │ Requests │ Success  │ P50 (ms) │")
    print("  ├─────────────────────┼─────────────────────┼──────────┼──────────┼──────────┤")
    
    for metrics in manager.metrics:
        src = metrics.source_service[:19].ljust(19)
        dst = metrics.destination_service[:19].ljust(19)
        reqs = str(metrics.request_count)[:8].ljust(8)
        success = str(metrics.success_count)[:8].ljust(8)
        p50 = f"{metrics.latency_p50_ms:.1f}"[:8].ljust(8)
        
        print(f"  │ {src} │ {dst} │ {reqs} │ {success} │ {p50} │")
        
    print("  └─────────────────────┴─────────────────────┴──────────┴──────────┴──────────┘")
    
    # TLS modes
    print("\n🔐 TLS Configuration:")
    
    for policy in manager.policies.values():
        icon = {
            TLSMode.DISABLED: "🔓",
            TLSMode.PERMISSIVE: "🔐",
            TLSMode.STRICT: "🔒",
            TLSMode.MUTUAL: "🔏"
        }.get(policy.mtls_mode, "❓")
        
        print(f"  {icon} {policy.name} ({policy.namespace}): {policy.mtls_mode.value}")
        
    # Rate limits
    print("\n⏱️ Rate Limits:")
    
    for rl in manager.rate_limits.values():
        bar = "█" * (rl.requests_per_second // 100) + "░" * (10 - rl.requests_per_second // 100)
        print(f"  {rl.service_name}: [{bar}] {rl.requests_per_second} RPS")
        
    # Statistics
    print("\n📊 Mesh Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Services: {stats['services_total']}")
    print(f"  Proxies: {stats['proxies_total']}")
    print(f"  Endpoints: {stats['endpoints_total']} ({stats['healthy_endpoints']} healthy)")
    print(f"  Traffic Rules: {stats['traffic_rules']}")
    print(f"  Rate Limits: {stats['rate_limits']}")
    print(f"  Circuit Breakers: {stats['circuit_breakers']}")
    print(f"  Policies: {stats['policies']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                      Service Mesh Dashboard                         │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Services:                      {stats['services_total']:>12}                        │")
    print(f"│ Sidecar Proxies:               {stats['proxies_total']:>12}                        │")
    print(f"│ Healthy Endpoints:             {stats['healthy_endpoints']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Traffic Rules:                 {stats['traffic_rules']:>12}                        │")
    print(f"│ Rate Limits:                   {stats['rate_limits']:>12}                        │")
    print(f"│ Circuit Breakers:              {stats['circuit_breakers']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Service Mesh Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
