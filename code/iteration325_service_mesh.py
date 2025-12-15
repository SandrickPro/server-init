#!/usr/bin/env python3
"""
Server Init - Iteration 325: Service Mesh Platform
Платформа Service Mesh

Функционал:
- Service Discovery - обнаружение сервисов
- Traffic Management - управление трафиком
- Load Balancing - балансировка нагрузки
- Circuit Breaking - защита от каскадных сбоев
- Retry Policies - политики повторов
- mTLS Security - взаимная TLS аутентификация
- Observability - наблюдаемость
- Rate Limiting - ограничение частоты
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class ServiceStatus(Enum):
    """Статус сервиса"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class LoadBalancerAlgorithm(Enum):
    """Алгоритм балансировки"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"
    CONSISTENT_HASH = "consistent_hash"
    WEIGHTED = "weighted"


class TrafficPolicy(Enum):
    """Политика трафика"""
    ALLOW_ALL = "allow_all"
    DENY_ALL = "deny_all"
    MTLS_STRICT = "mtls_strict"
    MTLS_PERMISSIVE = "mtls_permissive"


class CircuitState(Enum):
    """Состояние Circuit Breaker"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class RetryPolicy(Enum):
    """Политика повторов"""
    NONE = "none"
    FIXED = "fixed"
    EXPONENTIAL = "exponential"


@dataclass
class ServiceEndpoint:
    """Эндпоинт сервиса"""
    endpoint_id: str
    service_id: str
    
    # Address
    ip_address: str = ""
    port: int = 80
    
    # Health
    status: ServiceStatus = ServiceStatus.HEALTHY
    last_health_check: datetime = field(default_factory=datetime.now)
    
    # Weight
    weight: int = 100
    
    # Zone
    zone: str = ""
    
    # Metrics
    request_count: int = 0
    error_count: int = 0
    latency_ms: float = 0


@dataclass
class Service:
    """Сервис"""
    service_id: str
    name: str
    
    # Namespace
    namespace: str = "default"
    
    # Ports
    port: int = 80
    target_port: int = 8080
    protocol: str = "http"
    
    # Endpoints
    endpoint_ids: List[str] = field(default_factory=list)
    
    # Version
    version: str = "v1"
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Status
    status: ServiceStatus = ServiceStatus.HEALTHY
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class VirtualService:
    """Виртуальный сервис для маршрутизации"""
    vs_id: str
    name: str
    
    # Hosts
    hosts: List[str] = field(default_factory=list)
    
    # Routes
    http_routes: List[Dict[str, Any]] = field(default_factory=list)
    # Format: {"match": {...}, "route": [...], "timeout": "30s", "retries": {...}}
    
    # Gateways
    gateways: List[str] = field(default_factory=list)
    
    # Status
    is_active: bool = True


@dataclass
class DestinationRule:
    """Правило назначения"""
    dr_id: str
    name: str
    
    # Host
    host: str = ""
    
    # Traffic policy
    traffic_policy: Dict[str, Any] = field(default_factory=dict)
    
    # Subsets (versions)
    subsets: List[Dict[str, Any]] = field(default_factory=list)
    # Format: {"name": "v1", "labels": {"version": "v1"}}


@dataclass
class CircuitBreaker:
    """Circuit Breaker"""
    cb_id: str
    service_id: str
    
    # State
    state: CircuitState = CircuitState.CLOSED
    
    # Thresholds
    failure_threshold: int = 5
    success_threshold: int = 3
    timeout_seconds: int = 30
    
    # Counters
    failure_count: int = 0
    success_count: int = 0
    
    # Timestamps
    last_failure: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    
    # Request tracking
    requests_in_half_open: int = 0
    max_requests_half_open: int = 3


@dataclass
class RetryConfig:
    """Конфигурация повторов"""
    config_id: str
    service_id: str
    
    # Policy
    policy: RetryPolicy = RetryPolicy.EXPONENTIAL
    
    # Attempts
    max_attempts: int = 3
    
    # Delays
    initial_delay_ms: int = 100
    max_delay_ms: int = 1000
    
    # Retry on
    retry_on: List[str] = field(default_factory=lambda: ["5xx", "reset", "connect-failure"])
    
    # Stats
    retry_count: int = 0
    success_after_retry: int = 0


@dataclass
class RateLimitRule:
    """Правило ограничения частоты"""
    rule_id: str
    name: str
    
    # Target
    service_id: str = ""
    
    # Limits
    requests_per_second: int = 100
    requests_per_minute: int = 1000
    burst_size: int = 50
    
    # Current
    current_count: int = 0
    last_reset: datetime = field(default_factory=datetime.now)
    
    # Stats
    allowed_count: int = 0
    denied_count: int = 0


@dataclass
class MTLSConfig:
    """Конфигурация mTLS"""
    config_id: str
    
    # Namespace
    namespace: str = "default"
    
    # Mode
    mode: str = "STRICT"  # STRICT, PERMISSIVE, DISABLE
    
    # Certificate
    certificate_chain: str = ""
    private_key: str = ""
    root_ca: str = ""
    
    # Rotation
    rotation_interval_hours: int = 24
    last_rotation: Optional[datetime] = None


@dataclass
class ServiceEntry:
    """Внешний сервис"""
    entry_id: str
    name: str
    
    # Hosts
    hosts: List[str] = field(default_factory=list)
    
    # Ports
    ports: List[Dict[str, Any]] = field(default_factory=list)
    # Format: {"number": 443, "name": "https", "protocol": "HTTPS"}
    
    # Location
    location: str = "MESH_EXTERNAL"  # MESH_INTERNAL, MESH_EXTERNAL
    
    # Resolution
    resolution: str = "DNS"  # NONE, STATIC, DNS


@dataclass
class RequestMetrics:
    """Метрики запросов"""
    source_service: str
    dest_service: str
    
    # Counts
    request_count: int = 0
    success_count: int = 0
    error_count: int = 0
    
    # Latency (ms)
    avg_latency: float = 0
    p50_latency: float = 0
    p95_latency: float = 0
    p99_latency: float = 0
    
    # Bytes
    bytes_sent: int = 0
    bytes_received: int = 0
    
    # Window
    window_start: datetime = field(default_factory=datetime.now)


@dataclass
class TrafficSplit:
    """Разделение трафика"""
    split_id: str
    service_id: str
    
    # Splits
    splits: List[Dict[str, Any]] = field(default_factory=list)
    # Format: {"version": "v1", "weight": 90}, {"version": "v2", "weight": 10}
    
    # A/B testing
    is_ab_test: bool = False
    
    # Canary
    is_canary: bool = False
    canary_version: str = ""


class ServiceMeshManager:
    """Менеджер Service Mesh"""
    
    def __init__(self):
        self.services: Dict[str, Service] = {}
        self.endpoints: Dict[str, ServiceEndpoint] = {}
        self.virtual_services: Dict[str, VirtualService] = {}
        self.destination_rules: Dict[str, DestinationRule] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_configs: Dict[str, RetryConfig] = {}
        self.rate_limits: Dict[str, RateLimitRule] = {}
        self.mtls_configs: Dict[str, MTLSConfig] = {}
        self.service_entries: Dict[str, ServiceEntry] = {}
        self.traffic_splits: Dict[str, TrafficSplit] = {}
        self.metrics: Dict[str, RequestMetrics] = {}
        
    async def register_service(self, name: str,
                              namespace: str = "default",
                              port: int = 80,
                              protocol: str = "http",
                              version: str = "v1",
                              labels: Dict[str, str] = None) -> Service:
        """Регистрация сервиса"""
        service = Service(
            service_id=f"svc_{uuid.uuid4().hex[:8]}",
            name=name,
            namespace=namespace,
            port=port,
            protocol=protocol,
            version=version,
            labels=labels or {"app": name, "version": version}
        )
        
        self.services[service.service_id] = service
        
        # Create circuit breaker
        cb = CircuitBreaker(
            cb_id=f"cb_{uuid.uuid4().hex[:8]}",
            service_id=service.service_id
        )
        self.circuit_breakers[cb.cb_id] = cb
        
        return service
        
    async def add_endpoint(self, service_id: str,
                          ip_address: str,
                          port: int,
                          zone: str = "",
                          weight: int = 100) -> Optional[ServiceEndpoint]:
        """Добавление эндпоинта"""
        service = self.services.get(service_id)
        if not service:
            return None
            
        endpoint = ServiceEndpoint(
            endpoint_id=f"ep_{uuid.uuid4().hex[:8]}",
            service_id=service_id,
            ip_address=ip_address,
            port=port,
            zone=zone,
            weight=weight
        )
        
        self.endpoints[endpoint.endpoint_id] = endpoint
        service.endpoint_ids.append(endpoint.endpoint_id)
        
        return endpoint
        
    async def create_virtual_service(self, name: str,
                                    hosts: List[str],
                                    routes: List[Dict[str, Any]],
                                    gateways: List[str] = None) -> VirtualService:
        """Создание виртуального сервиса"""
        vs = VirtualService(
            vs_id=f"vs_{uuid.uuid4().hex[:8]}",
            name=name,
            hosts=hosts,
            http_routes=routes,
            gateways=gateways or []
        )
        
        self.virtual_services[vs.vs_id] = vs
        return vs
        
    async def create_destination_rule(self, name: str,
                                     host: str,
                                     traffic_policy: Dict[str, Any] = None,
                                     subsets: List[Dict[str, Any]] = None) -> DestinationRule:
        """Создание правила назначения"""
        dr = DestinationRule(
            dr_id=f"dr_{uuid.uuid4().hex[:8]}",
            name=name,
            host=host,
            traffic_policy=traffic_policy or {},
            subsets=subsets or []
        )
        
        self.destination_rules[dr.dr_id] = dr
        return dr
        
    async def configure_retry(self, service_id: str,
                             policy: RetryPolicy = RetryPolicy.EXPONENTIAL,
                             max_attempts: int = 3,
                             retry_on: List[str] = None) -> RetryConfig:
        """Конфигурация повторов"""
        config = RetryConfig(
            config_id=f"retry_{uuid.uuid4().hex[:8]}",
            service_id=service_id,
            policy=policy,
            max_attempts=max_attempts,
            retry_on=retry_on or ["5xx", "reset", "connect-failure"]
        )
        
        self.retry_configs[config.config_id] = config
        return config
        
    async def configure_rate_limit(self, service_id: str,
                                  name: str,
                                  rps: int = 100,
                                  rpm: int = 1000,
                                  burst: int = 50) -> RateLimitRule:
        """Конфигурация ограничения частоты"""
        rule = RateLimitRule(
            rule_id=f"rl_{uuid.uuid4().hex[:8]}",
            name=name,
            service_id=service_id,
            requests_per_second=rps,
            requests_per_minute=rpm,
            burst_size=burst
        )
        
        self.rate_limits[rule.rule_id] = rule
        return rule
        
    async def configure_mtls(self, namespace: str = "default",
                            mode: str = "STRICT") -> MTLSConfig:
        """Конфигурация mTLS"""
        config = MTLSConfig(
            config_id=f"mtls_{uuid.uuid4().hex[:8]}",
            namespace=namespace,
            mode=mode,
            certificate_chain=f"cert_{uuid.uuid4().hex[:8]}",
            private_key=f"key_{uuid.uuid4().hex[:8]}",
            root_ca=f"ca_{uuid.uuid4().hex[:8]}"
        )
        
        self.mtls_configs[config.config_id] = config
        return config
        
    async def add_service_entry(self, name: str,
                               hosts: List[str],
                               ports: List[Dict[str, Any]],
                               location: str = "MESH_EXTERNAL") -> ServiceEntry:
        """Добавление внешнего сервиса"""
        entry = ServiceEntry(
            entry_id=f"se_{uuid.uuid4().hex[:8]}",
            name=name,
            hosts=hosts,
            ports=ports,
            location=location
        )
        
        self.service_entries[entry.entry_id] = entry
        return entry
        
    async def configure_traffic_split(self, service_id: str,
                                     splits: List[Dict[str, Any]],
                                     is_canary: bool = False) -> TrafficSplit:
        """Конфигурация разделения трафика"""
        split = TrafficSplit(
            split_id=f"split_{uuid.uuid4().hex[:8]}",
            service_id=service_id,
            splits=splits,
            is_canary=is_canary
        )
        
        if is_canary and splits:
            for s in splits:
                if s.get("weight", 0) < 50:
                    split.canary_version = s.get("version", "")
                    break
                    
        self.traffic_splits[split.split_id] = split
        return split
        
    async def health_check(self, service_id: str) -> ServiceStatus:
        """Проверка здоровья сервиса"""
        service = self.services.get(service_id)
        if not service:
            return ServiceStatus.UNKNOWN
            
        healthy_count = 0
        total_count = 0
        
        for ep_id in service.endpoint_ids:
            ep = self.endpoints.get(ep_id)
            if ep:
                total_count += 1
                # Simulate health check
                ep.status = random.choice([ServiceStatus.HEALTHY] * 9 + [ServiceStatus.UNHEALTHY])
                ep.last_health_check = datetime.now()
                
                if ep.status == ServiceStatus.HEALTHY:
                    healthy_count += 1
                    
        if total_count == 0:
            service.status = ServiceStatus.UNKNOWN
        elif healthy_count == total_count:
            service.status = ServiceStatus.HEALTHY
        elif healthy_count > 0:
            service.status = ServiceStatus.DEGRADED
        else:
            service.status = ServiceStatus.UNHEALTHY
            
        return service.status
        
    async def route_request(self, source_service: str,
                           dest_host: str) -> Optional[ServiceEndpoint]:
        """Маршрутизация запроса"""
        # Find service by host
        service = None
        for svc in self.services.values():
            if svc.name == dest_host or dest_host in [f"{svc.name}.{svc.namespace}"]:
                service = svc
                break
                
        if not service:
            return None
            
        # Check circuit breaker
        for cb in self.circuit_breakers.values():
            if cb.service_id == service.service_id:
                if cb.state == CircuitState.OPEN:
                    # Check if timeout expired
                    if cb.opened_at and (datetime.now() - cb.opened_at).total_seconds() > cb.timeout_seconds:
                        cb.state = CircuitState.HALF_OPEN
                        cb.requests_in_half_open = 0
                    else:
                        return None  # Circuit is open
                        
        # Check rate limit
        for rl in self.rate_limits.values():
            if rl.service_id == service.service_id:
                if rl.current_count >= rl.requests_per_second:
                    rl.denied_count += 1
                    return None  # Rate limited
                rl.current_count += 1
                rl.allowed_count += 1
                
        # Check traffic split
        target_version = service.version
        for split in self.traffic_splits.values():
            if split.service_id == service.service_id:
                total_weight = sum(s.get("weight", 0) for s in split.splits)
                if total_weight > 0:
                    rand = random.randint(1, total_weight)
                    cumulative = 0
                    for s in split.splits:
                        cumulative += s.get("weight", 0)
                        if rand <= cumulative:
                            target_version = s.get("version", service.version)
                            break
                            
        # Select endpoint (load balancing)
        healthy_endpoints = []
        for ep_id in service.endpoint_ids:
            ep = self.endpoints.get(ep_id)
            if ep and ep.status == ServiceStatus.HEALTHY:
                healthy_endpoints.append(ep)
                
        if not healthy_endpoints:
            return None
            
        # Round-robin selection (simplified)
        endpoint = random.choice(healthy_endpoints)
        
        # Update metrics
        metric_key = f"{source_service}_{service.name}"
        if metric_key not in self.metrics:
            self.metrics[metric_key] = RequestMetrics(
                source_service=source_service,
                dest_service=service.name
            )
            
        self.metrics[metric_key].request_count += 1
        endpoint.request_count += 1
        
        return endpoint
        
    async def record_response(self, source: str, dest: str,
                             success: bool, latency_ms: float):
        """Запись ответа"""
        metric_key = f"{source}_{dest}"
        
        if metric_key in self.metrics:
            metric = self.metrics[metric_key]
            
            if success:
                metric.success_count += 1
            else:
                metric.error_count += 1
                
            # Update latency (simplified moving average)
            n = metric.request_count
            metric.avg_latency = ((n - 1) * metric.avg_latency + latency_ms) / n
            
        # Update circuit breaker
        for svc in self.services.values():
            if svc.name == dest:
                for cb in self.circuit_breakers.values():
                    if cb.service_id == svc.service_id:
                        if success:
                            cb.success_count += 1
                            if cb.state == CircuitState.HALF_OPEN:
                                if cb.success_count >= cb.success_threshold:
                                    cb.state = CircuitState.CLOSED
                                    cb.failure_count = 0
                        else:
                            cb.failure_count += 1
                            cb.last_failure = datetime.now()
                            
                            if cb.state == CircuitState.CLOSED:
                                if cb.failure_count >= cb.failure_threshold:
                                    cb.state = CircuitState.OPEN
                                    cb.opened_at = datetime.now()
                            elif cb.state == CircuitState.HALF_OPEN:
                                cb.state = CircuitState.OPEN
                                cb.opened_at = datetime.now()
                        break
                break
                
    async def simulate_traffic(self, requests: int = 100):
        """Симуляция трафика"""
        service_names = [s.name for s in self.services.values()]
        
        for _ in range(requests):
            if len(service_names) < 2:
                continue
                
            source = random.choice(service_names)
            dest = random.choice([n for n in service_names if n != source])
            
            endpoint = await self.route_request(source, dest)
            
            if endpoint:
                # Simulate response
                success = random.random() > 0.05  # 95% success rate
                latency = random.uniform(1, 100)
                
                await self.record_response(source, dest, success, latency)
                
                endpoint.latency_ms = latency
                if not success:
                    endpoint.error_count += 1
                    
    def get_service_graph(self) -> Dict[str, Any]:
        """Получение графа сервисов"""
        nodes = []
        edges = []
        
        for svc in self.services.values():
            healthy_eps = sum(1 for ep_id in svc.endpoint_ids 
                            if self.endpoints.get(ep_id, ServiceEndpoint("", "")).status == ServiceStatus.HEALTHY)
            total_eps = len(svc.endpoint_ids)
            
            nodes.append({
                "id": svc.service_id,
                "name": svc.name,
                "namespace": svc.namespace,
                "version": svc.version,
                "status": svc.status.value,
                "endpoints": f"{healthy_eps}/{total_eps}"
            })
            
        for metric in self.metrics.values():
            edges.append({
                "source": metric.source_service,
                "target": metric.dest_service,
                "requests": metric.request_count,
                "success_rate": (metric.success_count / metric.request_count * 100) if metric.request_count > 0 else 0,
                "avg_latency": metric.avg_latency
            })
            
        return {
            "nodes": nodes,
            "edges": edges
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_services = len(self.services)
        healthy_services = sum(1 for s in self.services.values() if s.status == ServiceStatus.HEALTHY)
        
        total_endpoints = len(self.endpoints)
        healthy_endpoints = sum(1 for e in self.endpoints.values() if e.status == ServiceStatus.HEALTHY)
        
        total_requests = sum(m.request_count for m in self.metrics.values())
        total_errors = sum(m.error_count for m in self.metrics.values())
        
        avg_latency = 0
        if self.metrics:
            avg_latency = sum(m.avg_latency for m in self.metrics.values()) / len(self.metrics)
            
        open_circuits = sum(1 for cb in self.circuit_breakers.values() if cb.state == CircuitState.OPEN)
        
        total_rate_limited = sum(rl.denied_count for rl in self.rate_limits.values())
        
        return {
            "total_services": total_services,
            "healthy_services": healthy_services,
            "total_endpoints": total_endpoints,
            "healthy_endpoints": healthy_endpoints,
            "virtual_services": len(self.virtual_services),
            "destination_rules": len(self.destination_rules),
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": (total_errors / total_requests * 100) if total_requests > 0 else 0,
            "avg_latency_ms": avg_latency,
            "circuit_breakers": len(self.circuit_breakers),
            "open_circuits": open_circuits,
            "rate_limit_rules": len(self.rate_limits),
            "rate_limited_requests": total_rate_limited,
            "mtls_configs": len(self.mtls_configs),
            "service_entries": len(self.service_entries),
            "traffic_splits": len(self.traffic_splits)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 325: Service Mesh Platform")
    print("=" * 60)
    
    mesh = ServiceMeshManager()
    print("✓ Service Mesh Manager created")
    
    # Register services
    print("\n📦 Registering Services...")
    
    services_data = [
        ("api-gateway", "production", 80, "http", "v1"),
        ("user-service", "production", 8080, "grpc", "v1"),
        ("user-service", "production", 8080, "grpc", "v2"),
        ("order-service", "production", 8080, "http", "v1"),
        ("payment-service", "production", 8080, "http", "v1"),
        ("notification-service", "production", 8080, "http", "v1"),
        ("inventory-service", "production", 8080, "grpc", "v1"),
        ("cart-service", "production", 8080, "http", "v1"),
        ("search-service", "production", 9200, "http", "v1"),
        ("recommendation-service", "production", 8080, "grpc", "v1")
    ]
    
    services = []
    for name, ns, port, proto, version in services_data:
        svc = await mesh.register_service(name, ns, port, proto, version)
        services.append(svc)
        print(f"  📦 {name}.{ns} ({proto}:{port}) [{version}]")
        
    # Add endpoints for each service
    print("\n🔌 Adding Service Endpoints...")
    
    for svc in services:
        num_endpoints = random.randint(2, 5)
        for i in range(num_endpoints):
            ip = f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}"
            zone = random.choice(["us-east-1a", "us-east-1b", "us-east-1c"])
            await mesh.add_endpoint(svc.service_id, ip, svc.target_port, zone)
            
    total_endpoints = len(mesh.endpoints)
    print(f"  ✓ Added {total_endpoints} endpoints across {len(services)} services")
    
    # Create virtual services
    print("\n🌐 Creating Virtual Services...")
    
    vs_data = [
        ("api-gateway-vs", ["api.company.com"], [
            {
                "match": [{"uri": {"prefix": "/api/v1"}}],
                "route": [{"destination": {"host": "api-gateway", "port": 80}}],
                "timeout": "30s"
            }
        ]),
        ("user-service-vs", ["user-service"], [
            {
                "match": [{"headers": {"version": "v2"}}],
                "route": [{"destination": {"host": "user-service", "subset": "v2"}}]
            },
            {
                "route": [{"destination": {"host": "user-service", "subset": "v1"}}]
            }
        ])
    ]
    
    virtual_services = []
    for name, hosts, routes in vs_data:
        vs = await mesh.create_virtual_service(name, hosts, routes)
        virtual_services.append(vs)
        print(f"  🌐 {name} -> {', '.join(hosts)}")
        
    # Create destination rules
    print("\n📋 Creating Destination Rules...")
    
    dr_data = [
        ("user-service-dr", "user-service", 
         {"connectionPool": {"tcp": {"maxConnections": 100}}},
         [{"name": "v1", "labels": {"version": "v1"}}, {"name": "v2", "labels": {"version": "v2"}}]),
        ("order-service-dr", "order-service",
         {"loadBalancer": {"simple": "LEAST_CONN"}},
         [{"name": "v1", "labels": {"version": "v1"}}])
    ]
    
    dest_rules = []
    for name, host, policy, subsets in dr_data:
        dr = await mesh.create_destination_rule(name, host, policy, subsets)
        dest_rules.append(dr)
        print(f"  📋 {name} -> {host}")
        
    # Configure retry policies
    print("\n🔄 Configuring Retry Policies...")
    
    for svc in services[:5]:
        config = await mesh.configure_retry(
            svc.service_id,
            RetryPolicy.EXPONENTIAL,
            max_attempts=3,
            retry_on=["5xx", "reset", "connect-failure", "retriable-4xx"]
        )
        print(f"  🔄 Retry policy for {svc.name}")
        
    # Configure rate limits
    print("\n⏱️ Configuring Rate Limits...")
    
    rate_limits_data = [
        ("api-gateway", "API Gateway Limit", 1000, 10000, 100),
        ("user-service", "User Service Limit", 500, 5000, 50),
        ("order-service", "Order Service Limit", 200, 2000, 20)
    ]
    
    for svc_name, name, rps, rpm, burst in rate_limits_data:
        for svc in services:
            if svc.name == svc_name:
                await mesh.configure_rate_limit(svc.service_id, name, rps, rpm, burst)
                print(f"  ⏱️ {name}: {rps} RPS")
                break
                
    # Configure mTLS
    print("\n🔐 Configuring mTLS...")
    
    mtls = await mesh.configure_mtls("production", "STRICT")
    print(f"  🔐 mTLS enabled for production namespace (STRICT mode)")
    
    # Add external services
    print("\n🌍 Adding External Services...")
    
    external_services = [
        ("external-api", ["api.external-provider.com"],
         [{"number": 443, "name": "https", "protocol": "HTTPS"}]),
        ("mongodb-atlas", ["cluster0.mongodb.net"],
         [{"number": 27017, "name": "mongo", "protocol": "MONGO"}])
    ]
    
    for name, hosts, ports in external_services:
        await mesh.add_service_entry(name, hosts, ports)
        print(f"  🌍 {name} -> {hosts[0]}")
        
    # Configure traffic splits (canary deployment)
    print("\n🎯 Configuring Traffic Splits...")
    
    # Find user-service v1 and v2
    user_svc_v1 = None
    for svc in services:
        if svc.name == "user-service" and svc.version == "v1":
            user_svc_v1 = svc
            break
            
    if user_svc_v1:
        split = await mesh.configure_traffic_split(
            user_svc_v1.service_id,
            [{"version": "v1", "weight": 90}, {"version": "v2", "weight": 10}],
            is_canary=True
        )
        print(f"  🎯 Canary deployment: v1=90%, v2=10%")
        
    # Run health checks
    print("\n💓 Running Health Checks...")
    
    for svc in services:
        status = await mesh.health_check(svc.service_id)
        status_icon = {"healthy": "✓", "unhealthy": "✗", "degraded": "⚠"}.get(status.value, "?")
        print(f"  {status_icon} {svc.name}: {status.value}")
        
    # Simulate traffic
    print("\n📊 Simulating Traffic...")
    
    await mesh.simulate_traffic(500)
    print(f"  ✓ Simulated 500 requests")
    
    # Service status
    print("\n📦 Service Status:")
    
    print("\n  ┌───────────────────────────────┬──────────────────┬──────────────┬───────────────────┬──────────────┐")
    print("  │ Service                       │ Version          │ Endpoints    │ Status            │ Protocol     │")
    print("  ├───────────────────────────────┼──────────────────┼──────────────┼───────────────────┼──────────────┤")
    
    for svc in services:
        name = svc.name[:29].ljust(29)
        version = svc.version[:16].ljust(16)
        
        healthy = sum(1 for ep_id in svc.endpoint_ids
                     if mesh.endpoints.get(ep_id, ServiceEndpoint("", "")).status == ServiceStatus.HEALTHY)
        endpoints = f"{healthy}/{len(svc.endpoint_ids)}"[:12].ljust(12)
        
        status = svc.status.value[:17].ljust(17)
        protocol = svc.protocol[:12].ljust(12)
        
        print(f"  │ {name} │ {version} │ {endpoints} │ {status} │ {protocol} │")
        
    print("  └───────────────────────────────┴──────────────────┴──────────────┴───────────────────┴──────────────┘")
    
    # Circuit breaker status
    print("\n⚡ Circuit Breaker Status:")
    
    for cb in mesh.circuit_breakers.values():
        svc = mesh.services.get(cb.service_id)
        svc_name = svc.name if svc else "unknown"
        
        state_icon = {"closed": "🟢", "open": "🔴", "half_open": "🟡"}.get(cb.state.value, "⚪")
        
        print(f"  {state_icon} {svc_name}: {cb.state.value} (failures: {cb.failure_count}, successes: {cb.success_count})")
        
    # Rate limit status
    print("\n⏱️ Rate Limit Status:")
    
    for rl in mesh.rate_limits.values():
        svc = mesh.services.get(rl.service_id)
        svc_name = svc.name if svc else "unknown"
        
        print(f"\n  ⏱️ {rl.name}")
        print(f"     Service: {svc_name}")
        print(f"     Limit: {rl.requests_per_second} RPS / {rl.requests_per_minute} RPM")
        print(f"     Allowed: {rl.allowed_count} | Denied: {rl.denied_count}")
        
    # Traffic metrics
    print("\n📊 Traffic Metrics:")
    
    print("\n  ┌───────────────────────────────┬───────────────────────────────┬──────────────┬──────────────┬──────────────┐")
    print("  │ Source                        │ Destination                   │ Requests     │ Success Rate │ Avg Latency  │")
    print("  ├───────────────────────────────┼───────────────────────────────┼──────────────┼──────────────┼──────────────┤")
    
    for metric in sorted(mesh.metrics.values(), key=lambda m: m.request_count, reverse=True)[:10]:
        source = metric.source_service[:29].ljust(29)
        dest = metric.dest_service[:29].ljust(29)
        requests = str(metric.request_count)[:12].ljust(12)
        success_rate = f"{(metric.success_count / metric.request_count * 100):.1f}%"[:12].ljust(12) if metric.request_count > 0 else "N/A".ljust(12)
        latency = f"{metric.avg_latency:.1f}ms"[:12].ljust(12)
        
        print(f"  │ {source} │ {dest} │ {requests} │ {success_rate} │ {latency} │")
        
    print("  └───────────────────────────────┴───────────────────────────────┴──────────────┴──────────────┴──────────────┘")
    
    # Service graph
    print("\n🔗 Service Graph:")
    
    graph = mesh.get_service_graph()
    
    print(f"\n  Nodes: {len(graph['nodes'])}")
    print(f"  Edges: {len(graph['edges'])}")
    
    print("\n  Service Dependencies:")
    for edge in sorted(graph['edges'], key=lambda e: e['requests'], reverse=True)[:5]:
        print(f"    {edge['source']} -> {edge['target']}: {edge['requests']} requests ({edge['success_rate']:.1f}% success)")
        
    # mTLS status
    print("\n🔐 mTLS Configuration:")
    
    for config in mesh.mtls_configs.values():
        print(f"\n  🔐 Namespace: {config.namespace}")
        print(f"     Mode: {config.mode}")
        print(f"     Certificate: {config.certificate_chain[:20]}...")
        print(f"     Rotation: Every {config.rotation_interval_hours} hours")
        
    # Traffic splits
    print("\n🎯 Active Traffic Splits:")
    
    for split in mesh.traffic_splits.values():
        svc = mesh.services.get(split.service_id)
        svc_name = svc.name if svc else "unknown"
        
        split_type = "Canary" if split.is_canary else "A/B" if split.is_ab_test else "Split"
        
        print(f"\n  🎯 {svc_name} ({split_type})")
        for s in split.splits:
            print(f"     {s.get('version', 'default')}: {s.get('weight', 0)}%")
            
    # Statistics
    print("\n📊 Overall Statistics:")
    
    stats = mesh.get_statistics()
    
    print(f"\n  Services: {stats['healthy_services']}/{stats['total_services']} healthy")
    print(f"  Endpoints: {stats['healthy_endpoints']}/{stats['total_endpoints']} healthy")
    print(f"  Virtual Services: {stats['virtual_services']}")
    print(f"  Destination Rules: {stats['destination_rules']}")
    
    print(f"\n  Traffic:")
    print(f"    Total Requests: {stats['total_requests']}")
    print(f"    Error Rate: {stats['error_rate']:.2f}%")
    print(f"    Avg Latency: {stats['avg_latency_ms']:.2f}ms")
    
    print(f"\n  Resilience:")
    print(f"    Circuit Breakers: {stats['circuit_breakers']} ({stats['open_circuits']} open)")
    print(f"    Rate Limited: {stats['rate_limited_requests']} requests")
    
    print(f"\n  Security:")
    print(f"    mTLS Configs: {stats['mtls_configs']}")
    print(f"    External Services: {stats['service_entries']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                        Service Mesh Platform                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Services:              {stats['total_services']:>12}                          │")
    print(f"│ Healthy Services:            {stats['healthy_services']:>12}                          │")
    print(f"│ Total Endpoints:             {stats['total_endpoints']:>12}                          │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Requests:              {stats['total_requests']:>12}                          │")
    print(f"│ Error Rate:                  {stats['error_rate']:>10.2f}%                          │")
    print(f"│ Avg Latency:                 {stats['avg_latency_ms']:>10.2f}ms                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Service Mesh Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
