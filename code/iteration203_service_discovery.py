#!/usr/bin/env python3
"""
Server Init - Iteration 203: Service Discovery Platform
Платформа обнаружения сервисов

Функционал:
- Service Registration - регистрация сервисов
- Service Discovery - обнаружение сервисов
- Health Checking - проверка здоровья
- Load Balancing - балансировка нагрузки
- DNS Integration - интеграция с DNS
- Service Catalog - каталог сервисов
- Watch/Notify - наблюдение и уведомления
- Metadata Management - управление метаданными
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
import uuid


class ServiceStatus(Enum):
    """Статус сервиса"""
    UNKNOWN = "unknown"
    PASSING = "passing"
    WARNING = "warning"
    CRITICAL = "critical"
    MAINTENANCE = "maintenance"


class HealthCheckType(Enum):
    """Тип проверки здоровья"""
    HTTP = "http"
    TCP = "tcp"
    GRPC = "grpc"
    SCRIPT = "script"
    TTL = "ttl"


class LoadBalancerAlgorithm(Enum):
    """Алгоритм балансировки"""
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED = "weighted"
    IP_HASH = "ip_hash"


@dataclass
class ServiceEndpoint:
    """Эндпоинт сервиса"""
    endpoint_id: str
    
    # Address
    address: str = ""
    port: int = 0
    
    # Protocol
    protocol: str = "http"
    
    # Health
    status: ServiceStatus = ServiceStatus.UNKNOWN
    
    # Weight
    weight: int = 100
    
    # Metadata
    metadata: Dict[str, str] = field(default_factory=dict)
    
    # Connections
    active_connections: int = 0
    
    # Time
    registered_at: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)


@dataclass
class HealthCheck:
    """Проверка здоровья"""
    check_id: str
    
    # Type
    check_type: HealthCheckType = HealthCheckType.HTTP
    
    # Config
    endpoint: str = ""
    interval_seconds: int = 10
    timeout_seconds: int = 5
    
    # Thresholds
    healthy_threshold: int = 2
    unhealthy_threshold: int = 3
    
    # State
    consecutive_successes: int = 0
    consecutive_failures: int = 0
    last_check: Optional[datetime] = None
    last_status: ServiceStatus = ServiceStatus.UNKNOWN


@dataclass
class Service:
    """Сервис"""
    service_id: str
    name: str = ""
    namespace: str = "default"
    
    # Version
    version: str = "1.0.0"
    
    # Endpoints
    endpoints: Dict[str, ServiceEndpoint] = field(default_factory=dict)
    
    # Health checks
    health_checks: List[HealthCheck] = field(default_factory=list)
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, str] = field(default_factory=dict)
    
    # Status
    status: ServiceStatus = ServiceStatus.UNKNOWN
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def healthy_endpoints(self) -> List[ServiceEndpoint]:
        return [e for e in self.endpoints.values() 
                if e.status == ServiceStatus.PASSING]


@dataclass
class DNSRecord:
    """DNS запись"""
    record_id: str
    
    # Record
    name: str = ""
    record_type: str = "A"  # A, AAAA, SRV, CNAME
    
    # Value
    value: str = ""
    
    # TTL
    ttl: int = 300
    
    # Linked service
    service_id: str = ""


@dataclass
class WatchSubscription:
    """Подписка на изменения"""
    subscription_id: str
    
    # Target
    service_name: str = ""
    namespace: str = ""
    
    # Callback
    callback_url: str = ""
    
    # Filter
    tags: List[str] = field(default_factory=list)
    
    # Created
    created_at: datetime = field(default_factory=datetime.now)


class ServiceRegistry:
    """Реестр сервисов"""
    
    def __init__(self):
        self.services: Dict[str, Service] = {}
        self.by_name: Dict[str, List[str]] = {}
        
    def register(self, service: Service) -> Service:
        """Регистрация сервиса"""
        self.services[service.service_id] = service
        
        key = f"{service.namespace}/{service.name}"
        if key not in self.by_name:
            self.by_name[key] = []
        self.by_name[key].append(service.service_id)
        
        return service
        
    def deregister(self, service_id: str) -> bool:
        """Снятие регистрации"""
        service = self.services.pop(service_id, None)
        if service:
            key = f"{service.namespace}/{service.name}"
            if key in self.by_name:
                self.by_name[key].remove(service_id)
            return True
        return False
        
    def find_by_name(self, name: str, namespace: str = "default") -> List[Service]:
        """Поиск по имени"""
        key = f"{namespace}/{name}"
        service_ids = self.by_name.get(key, [])
        return [self.services[sid] for sid in service_ids if sid in self.services]
        
    def find_by_tags(self, tags: List[str]) -> List[Service]:
        """Поиск по тегам"""
        return [s for s in self.services.values() 
                if all(tag in s.tags for tag in tags)]


class HealthChecker:
    """Проверщик здоровья"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.check_history: List[Dict[str, Any]] = []
        
    async def check_endpoint(self, endpoint: ServiceEndpoint,
                           health_check: HealthCheck) -> bool:
        """Проверка эндпоинта"""
        # Simulate health check
        await asyncio.sleep(0.01)
        
        # Random health status (90% healthy)
        healthy = random.random() > 0.1
        
        return healthy
        
    async def run_checks(self, service: Service):
        """Выполнение проверок для сервиса"""
        for endpoint in service.endpoints.values():
            for check in service.health_checks:
                healthy = await self.check_endpoint(endpoint, check)
                
                if healthy:
                    check.consecutive_successes += 1
                    check.consecutive_failures = 0
                    
                    if check.consecutive_successes >= check.healthy_threshold:
                        endpoint.status = ServiceStatus.PASSING
                else:
                    check.consecutive_failures += 1
                    check.consecutive_successes = 0
                    
                    if check.consecutive_failures >= check.unhealthy_threshold:
                        endpoint.status = ServiceStatus.CRITICAL
                        
                check.last_check = datetime.now()
                check.last_status = endpoint.status
                
                self.check_history.append({
                    "service_id": service.service_id,
                    "endpoint_id": endpoint.endpoint_id,
                    "healthy": healthy,
                    "timestamp": datetime.now()
                })
                
        # Update service status
        healthy_count = len(service.healthy_endpoints)
        total_count = len(service.endpoints)
        
        if healthy_count == 0:
            service.status = ServiceStatus.CRITICAL
        elif healthy_count < total_count:
            service.status = ServiceStatus.WARNING
        else:
            service.status = ServiceStatus.PASSING


class LoadBalancer:
    """Балансировщик нагрузки"""
    
    def __init__(self, algorithm: LoadBalancerAlgorithm = LoadBalancerAlgorithm.ROUND_ROBIN):
        self.algorithm = algorithm
        self.round_robin_index: Dict[str, int] = {}
        
    def select(self, service: Service) -> Optional[ServiceEndpoint]:
        """Выбор эндпоинта"""
        endpoints = service.healthy_endpoints
        
        if not endpoints:
            return None
            
        if self.algorithm == LoadBalancerAlgorithm.RANDOM:
            return random.choice(endpoints)
            
        elif self.algorithm == LoadBalancerAlgorithm.ROUND_ROBIN:
            index = self.round_robin_index.get(service.service_id, 0)
            endpoint = endpoints[index % len(endpoints)]
            self.round_robin_index[service.service_id] = index + 1
            return endpoint
            
        elif self.algorithm == LoadBalancerAlgorithm.LEAST_CONNECTIONS:
            return min(endpoints, key=lambda e: e.active_connections)
            
        elif self.algorithm == LoadBalancerAlgorithm.WEIGHTED:
            # Weighted random selection
            total_weight = sum(e.weight for e in endpoints)
            r = random.uniform(0, total_weight)
            cumulative = 0
            for endpoint in endpoints:
                cumulative += endpoint.weight
                if r <= cumulative:
                    return endpoint
            return endpoints[-1]
            
        return endpoints[0]


class DNSManager:
    """Менеджер DNS"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.records: Dict[str, DNSRecord] = {}
        self.domain_suffix = ".local"
        
    def create_record(self, service: Service) -> List[DNSRecord]:
        """Создание DNS записей"""
        records = []
        
        for endpoint in service.healthy_endpoints:
            record = DNSRecord(
                record_id=f"dns_{uuid.uuid4().hex[:8]}",
                name=f"{service.name}.{service.namespace}{self.domain_suffix}",
                record_type="A",
                value=endpoint.address,
                service_id=service.service_id
            )
            self.records[record.record_id] = record
            records.append(record)
            
        return records
        
    def resolve(self, name: str) -> List[str]:
        """Разрешение DNS"""
        return [r.value for r in self.records.values() if r.name == name]


class ServiceDiscoveryPlatform:
    """Платформа обнаружения сервисов"""
    
    def __init__(self):
        self.registry = ServiceRegistry()
        self.health_checker = HealthChecker(self.registry)
        self.load_balancer = LoadBalancer()
        self.dns = DNSManager(self.registry)
        self.subscriptions: Dict[str, WatchSubscription] = {}
        
    def register_service(self, name: str, namespace: str = "default",
                        endpoints: List[Dict[str, Any]] = None,
                        tags: List[str] = None) -> Service:
        """Регистрация сервиса"""
        service = Service(
            service_id=f"svc_{uuid.uuid4().hex[:8]}",
            name=name,
            namespace=namespace,
            tags=tags or []
        )
        
        # Add endpoints
        for ep_data in (endpoints or []):
            endpoint = ServiceEndpoint(
                endpoint_id=f"ep_{uuid.uuid4().hex[:8]}",
                address=ep_data.get("address", ""),
                port=ep_data.get("port", 80),
                protocol=ep_data.get("protocol", "http"),
                metadata=ep_data.get("metadata", {}),
                status=ServiceStatus.PASSING
            )
            service.endpoints[endpoint.endpoint_id] = endpoint
            
        # Add default health check
        health_check = HealthCheck(
            check_id=f"hc_{uuid.uuid4().hex[:8]}",
            check_type=HealthCheckType.HTTP,
            endpoint="/health"
        )
        service.health_checks.append(health_check)
        
        service.status = ServiceStatus.PASSING
        
        self.registry.register(service)
        self.dns.create_record(service)
        
        return service
        
    def discover(self, name: str, namespace: str = "default") -> List[Service]:
        """Обнаружение сервисов"""
        return self.registry.find_by_name(name, namespace)
        
    def get_endpoint(self, name: str, namespace: str = "default") -> Optional[ServiceEndpoint]:
        """Получение эндпоинта с балансировкой"""
        services = self.discover(name, namespace)
        
        for service in services:
            endpoint = self.load_balancer.select(service)
            if endpoint:
                return endpoint
                
        return None
        
    async def run_health_checks(self):
        """Запуск проверок здоровья"""
        for service in self.registry.services.values():
            await self.health_checker.run_checks(service)
            
    def subscribe(self, service_name: str, callback_url: str,
                 namespace: str = "default") -> WatchSubscription:
        """Подписка на изменения"""
        subscription = WatchSubscription(
            subscription_id=f"sub_{uuid.uuid4().hex[:8]}",
            service_name=service_name,
            namespace=namespace,
            callback_url=callback_url
        )
        self.subscriptions[subscription.subscription_id] = subscription
        return subscription
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        all_endpoints = []
        for service in self.registry.services.values():
            all_endpoints.extend(service.endpoints.values())
            
        healthy = len([e for e in all_endpoints if e.status == ServiceStatus.PASSING])
        
        return {
            "total_services": len(self.registry.services),
            "total_endpoints": len(all_endpoints),
            "healthy_endpoints": healthy,
            "dns_records": len(self.dns.records),
            "subscriptions": len(self.subscriptions),
            "health_checks": len(self.health_checker.check_history)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 203: Service Discovery Platform")
    print("=" * 60)
    
    platform = ServiceDiscoveryPlatform()
    print("✓ Service Discovery Platform created")
    
    # Register services
    print("\n📋 Registering Services...")
    
    services_config = [
        {
            "name": "api-gateway",
            "namespace": "production",
            "endpoints": [
                {"address": "10.0.1.10", "port": 8080},
                {"address": "10.0.1.11", "port": 8080},
                {"address": "10.0.1.12", "port": 8080},
            ],
            "tags": ["api", "gateway", "public"]
        },
        {
            "name": "user-service",
            "namespace": "production",
            "endpoints": [
                {"address": "10.0.2.10", "port": 8081},
                {"address": "10.0.2.11", "port": 8081},
            ],
            "tags": ["api", "users", "internal"]
        },
        {
            "name": "order-service",
            "namespace": "production",
            "endpoints": [
                {"address": "10.0.3.10", "port": 8082},
                {"address": "10.0.3.11", "port": 8082},
                {"address": "10.0.3.12", "port": 8082},
                {"address": "10.0.3.13", "port": 8082},
            ],
            "tags": ["api", "orders", "internal"]
        },
        {
            "name": "payment-service",
            "namespace": "production",
            "endpoints": [
                {"address": "10.0.4.10", "port": 8083},
            ],
            "tags": ["api", "payments", "critical"]
        },
        {
            "name": "notification-service",
            "namespace": "production",
            "endpoints": [
                {"address": "10.0.5.10", "port": 8084},
                {"address": "10.0.5.11", "port": 8084},
            ],
            "tags": ["api", "notifications"]
        },
    ]
    
    for config in services_config:
        service = platform.register_service(
            config["name"],
            config["namespace"],
            config["endpoints"],
            config["tags"]
        )
        print(f"  ✓ {service.name} ({len(service.endpoints)} endpoints)")
        
    # Run health checks
    print("\n🏥 Running Health Checks...")
    await platform.run_health_checks()
    print("  ✓ Health checks completed")
    
    # Discover services
    print("\n🔍 Service Discovery:")
    
    for name in ["api-gateway", "user-service", "order-service"]:
        services = platform.discover(name, "production")
        for svc in services:
            healthy = len(svc.healthy_endpoints)
            total = len(svc.endpoints)
            status_icon = "🟢" if healthy == total else ("🟡" if healthy > 0 else "🔴")
            print(f"  {status_icon} {svc.name}: {healthy}/{total} endpoints healthy")
            
    # Load balancing test
    print("\n⚖️ Load Balancing Test (10 requests):")
    
    endpoint_hits: Dict[str, int] = {}
    
    for _ in range(10):
        endpoint = platform.get_endpoint("order-service", "production")
        if endpoint:
            key = endpoint.address
            endpoint_hits[key] = endpoint_hits.get(key, 0) + 1
            
    for address, hits in endpoint_hits.items():
        bar = "█" * hits + "░" * (10 - hits)
        print(f"  {address} [{bar}] {hits}")
        
    # DNS resolution
    print("\n🌐 DNS Resolution:")
    
    dns_queries = [
        "api-gateway.production.local",
        "user-service.production.local",
        "order-service.production.local"
    ]
    
    for query in dns_queries:
        addresses = platform.dns.resolve(query)
        print(f"  {query} -> {', '.join(addresses) if addresses else 'NXDOMAIN'}")
        
    # Subscribe to changes
    print("\n👁️ Watch Subscriptions:")
    
    subs = [
        platform.subscribe("api-gateway", "http://watcher:8000/notify", "production"),
        platform.subscribe("user-service", "http://watcher:8000/notify", "production"),
    ]
    
    for sub in subs:
        print(f"  ✓ Watching {sub.service_name} -> {sub.callback_url}")
        
    # Display service catalog
    print("\n📚 Service Catalog:")
    
    print("\n  ┌──────────────────────┬─────────────┬──────────┬──────────┬──────────┐")
    print("  │ Service              │ Namespace   │ Endpoints│ Healthy  │ Status   │")
    print("  ├──────────────────────┼─────────────┼──────────┼──────────┼──────────┤")
    
    for service in platform.registry.services.values():
        name = service.name[:20].ljust(20)
        namespace = service.namespace[:11].ljust(11)
        endpoints = str(len(service.endpoints)).center(8)
        healthy = str(len(service.healthy_endpoints)).center(8)
        status = service.status.value[:8].ljust(8)
        print(f"  │ {name} │ {namespace} │ {endpoints} │ {healthy} │ {status} │")
        
    print("  └──────────────────────┴─────────────┴──────────┴──────────┴──────────┘")
    
    # Endpoint details
    print("\n📍 Endpoints Detail (order-service):")
    
    order_services = platform.discover("order-service", "production")
    if order_services:
        order_svc = order_services[0]
        
        print("\n  ┌─────────────────┬────────┬──────────┬──────────┐")
        print("  │ Address         │ Port   │ Weight   │ Status   │")
        print("  ├─────────────────┼────────┼──────────┼──────────┤")
        
        for endpoint in order_svc.endpoints.values():
            address = endpoint.address[:15].ljust(15)
            port = str(endpoint.port).center(6)
            weight = str(endpoint.weight).center(8)
            status = endpoint.status.value[:8].ljust(8)
            print(f"  │ {address} │ {port} │ {weight} │ {status} │")
            
        print("  └─────────────────┴────────┴──────────┴──────────┘")
        
    # Health check history
    print("\n🏥 Health Check Summary:")
    
    history = platform.health_checker.check_history
    healthy_checks = len([h for h in history if h["healthy"]])
    total_checks = len(history)
    
    if total_checks > 0:
        success_rate = healthy_checks / total_checks * 100
        print(f"\n  Total Checks: {total_checks}")
        print(f"  Healthy: {healthy_checks}")
        print(f"  Unhealthy: {total_checks - healthy_checks}")
        print(f"  Success Rate: {success_rate:.1f}%")
        
    # Tags search
    print("\n🏷️ Services by Tag:")
    
    tag_searches = [
        ["api", "internal"],
        ["critical"],
        ["public"]
    ]
    
    for tags in tag_searches:
        services = platform.registry.find_by_tags(tags)
        names = [s.name for s in services]
        print(f"  {tags}: {', '.join(names) if names else 'none'}")
        
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📊 Platform Statistics:")
    
    print(f"\n  Total Services: {stats['total_services']}")
    print(f"  Total Endpoints: {stats['total_endpoints']}")
    print(f"  Healthy Endpoints: {stats['healthy_endpoints']}")
    print(f"  DNS Records: {stats['dns_records']}")
    print(f"  Subscriptions: {stats['subscriptions']}")
    print(f"  Health Checks: {stats['health_checks']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                  Service Discovery Dashboard                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Services:                      {stats['total_services']:>12}                        │")
    print(f"│ Endpoints:                     {stats['total_endpoints']:>12}                        │")
    print(f"│ Healthy:                       {stats['healthy_endpoints']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    health_pct = (stats['healthy_endpoints'] / stats['total_endpoints'] * 100) if stats['total_endpoints'] > 0 else 0
    print(f"│ Health Rate:                     {health_pct:>10.1f}%                   │")
    print(f"│ DNS Records:                   {stats['dns_records']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Service Discovery Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
