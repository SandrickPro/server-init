#!/usr/bin/env python3
"""
Server Init - Iteration 134: Service Discovery Platform
Платформа Service Discovery

Функционал:
- Service Registration - регистрация сервисов
- Health Checking - проверка здоровья
- Service Catalog - каталог сервисов
- DNS Integration - интеграция с DNS
- Load Balancing - балансировка нагрузки
- Service Mesh Integration - интеграция с service mesh
- Endpoint Management - управление эндпоинтами
- Failover Handling - обработка отказов
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from collections import defaultdict
import uuid
import hashlib
import random


class ServiceStatus(Enum):
    """Статус сервиса"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class HealthCheckType(Enum):
    """Тип проверки здоровья"""
    HTTP = "http"
    TCP = "tcp"
    GRPC = "grpc"
    SCRIPT = "script"
    TTL = "ttl"


class LoadBalancerStrategy(Enum):
    """Стратегия балансировки"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"
    WEIGHTED = "weighted"
    CONSISTENT_HASH = "consistent_hash"


@dataclass
class ServiceInstance:
    """Инстанс сервиса"""
    instance_id: str
    service_id: str = ""
    
    # Network
    address: str = ""
    port: int = 80
    
    # Metadata
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    # Weight
    weight: int = 100
    
    # Status
    status: ServiceStatus = ServiceStatus.UNKNOWN
    healthy: bool = True
    
    # Timestamps
    registered_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: datetime = field(default_factory=datetime.now)


@dataclass
class HealthCheck:
    """Проверка здоровья"""
    check_id: str
    service_id: str = ""
    instance_id: str = ""
    
    # Type
    check_type: HealthCheckType = HealthCheckType.HTTP
    
    # HTTP Config
    http_path: str = "/health"
    http_method: str = "GET"
    expected_status: int = 200
    
    # TCP Config
    tcp_timeout_ms: int = 5000
    
    # Intervals
    interval_seconds: int = 30
    timeout_seconds: int = 10
    deregister_after_seconds: int = 300
    
    # Status
    last_check: Optional[datetime] = None
    passing: bool = True
    consecutive_failures: int = 0


@dataclass
class Service:
    """Сервис"""
    service_id: str
    name: str = ""
    
    # Config
    namespace: str = "default"
    
    # Endpoints
    instances: List[ServiceInstance] = field(default_factory=list)
    healthy_count: int = 0
    total_count: int = 0
    
    # Load Balancing
    lb_strategy: LoadBalancerStrategy = LoadBalancerStrategy.ROUND_ROBIN
    
    # DNS
    dns_name: str = ""
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DNSRecord:
    """DNS запись"""
    record_id: str
    service_id: str = ""
    
    # DNS
    name: str = ""
    record_type: str = "A"  # A, AAAA, SRV, CNAME
    ttl: int = 60
    
    # Values
    values: List[str] = field(default_factory=list)
    
    # Status
    active: bool = True


@dataclass
class ServiceEndpoint:
    """Эндпоинт сервиса"""
    endpoint_id: str
    service_id: str = ""
    
    # Network
    protocol: str = "http"
    host: str = ""
    port: int = 80
    path: str = "/"
    
    # Health
    healthy: bool = True
    
    # Stats
    connections: int = 0
    latency_ms: float = 0


class ServiceRegistry:
    """Реестр сервисов"""
    
    def __init__(self):
        self.services: Dict[str, Service] = {}
        self.instances: Dict[str, ServiceInstance] = {}
        
    def register_service(self, name: str, namespace: str = "default",
                          lb_strategy: LoadBalancerStrategy = LoadBalancerStrategy.ROUND_ROBIN,
                          **kwargs) -> Service:
        """Регистрация сервиса"""
        service = Service(
            service_id=f"svc_{uuid.uuid4().hex[:8]}",
            name=name,
            namespace=namespace,
            lb_strategy=lb_strategy,
            dns_name=f"{name}.{namespace}.svc.cluster.local",
            **kwargs
        )
        self.services[service.service_id] = service
        return service
        
    def register_instance(self, service_id: str, address: str, port: int,
                           version: str = "1.0.0", **kwargs) -> ServiceInstance:
        """Регистрация инстанса"""
        instance = ServiceInstance(
            instance_id=f"inst_{uuid.uuid4().hex[:8]}",
            service_id=service_id,
            address=address,
            port=port,
            version=version,
            status=ServiceStatus.HEALTHY,
            healthy=True,
            **kwargs
        )
        self.instances[instance.instance_id] = instance
        
        service = self.services.get(service_id)
        if service:
            service.instances.append(instance)
            service.total_count += 1
            service.healthy_count += 1
            
        return instance
        
    def deregister_instance(self, instance_id: str) -> bool:
        """Удаление инстанса"""
        instance = self.instances.pop(instance_id, None)
        if not instance:
            return False
            
        service = self.services.get(instance.service_id)
        if service:
            service.instances = [i for i in service.instances if i.instance_id != instance_id]
            service.total_count -= 1
            if instance.healthy:
                service.healthy_count -= 1
                
        return True
        
    def heartbeat(self, instance_id: str) -> bool:
        """Обновление heartbeat"""
        instance = self.instances.get(instance_id)
        if not instance:
            return False
            
        instance.last_heartbeat = datetime.now()
        return True


class HealthChecker:
    """Проверка здоровья"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.checks: Dict[str, HealthCheck] = {}
        
    def add_check(self, service_id: str, instance_id: str,
                   check_type: HealthCheckType = HealthCheckType.HTTP,
                   **kwargs) -> HealthCheck:
        """Добавление проверки"""
        check = HealthCheck(
            check_id=f"check_{uuid.uuid4().hex[:8]}",
            service_id=service_id,
            instance_id=instance_id,
            check_type=check_type,
            **kwargs
        )
        self.checks[check.check_id] = check
        return check
        
    async def run_check(self, check_id: str) -> Dict:
        """Выполнение проверки"""
        check = self.checks.get(check_id)
        if not check:
            return {"error": "Check not found"}
            
        # Simulate health check
        await asyncio.sleep(0.05)
        
        # Random result for demo
        passing = random.random() > 0.1  # 90% healthy
        
        check.last_check = datetime.now()
        check.passing = passing
        
        if not passing:
            check.consecutive_failures += 1
        else:
            check.consecutive_failures = 0
            
        # Update instance status
        instance = self.registry.instances.get(check.instance_id)
        if instance:
            if check.consecutive_failures >= 3:
                instance.healthy = False
                instance.status = ServiceStatus.UNHEALTHY
                
                service = self.registry.services.get(instance.service_id)
                if service:
                    service.healthy_count = len([i for i in service.instances if i.healthy])
            else:
                instance.healthy = True
                instance.status = ServiceStatus.HEALTHY
                
        return {
            "check_id": check_id,
            "passing": passing,
            "consecutive_failures": check.consecutive_failures
        }
        
    async def run_all_checks(self) -> Dict:
        """Выполнение всех проверок"""
        results = {"passed": 0, "failed": 0}
        
        for check_id in self.checks:
            result = await self.run_check(check_id)
            if result.get("passing"):
                results["passed"] += 1
            else:
                results["failed"] += 1
                
        return results


class LoadBalancer:
    """Балансировщик нагрузки"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.round_robin_index: Dict[str, int] = defaultdict(int)
        self.connection_counts: Dict[str, int] = defaultdict(int)
        
    def get_endpoint(self, service_id: str) -> Optional[ServiceInstance]:
        """Получение эндпоинта"""
        service = self.registry.services.get(service_id)
        if not service:
            return None
            
        healthy_instances = [i for i in service.instances if i.healthy]
        if not healthy_instances:
            return None
            
        if service.lb_strategy == LoadBalancerStrategy.ROUND_ROBIN:
            return self._round_robin(service_id, healthy_instances)
        elif service.lb_strategy == LoadBalancerStrategy.LEAST_CONNECTIONS:
            return self._least_connections(healthy_instances)
        elif service.lb_strategy == LoadBalancerStrategy.RANDOM:
            return self._random(healthy_instances)
        elif service.lb_strategy == LoadBalancerStrategy.WEIGHTED:
            return self._weighted(healthy_instances)
        else:
            return healthy_instances[0] if healthy_instances else None
            
    def _round_robin(self, service_id: str, instances: List[ServiceInstance]) -> ServiceInstance:
        """Round Robin"""
        index = self.round_robin_index[service_id] % len(instances)
        self.round_robin_index[service_id] += 1
        return instances[index]
        
    def _least_connections(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Least Connections"""
        return min(instances, key=lambda i: self.connection_counts.get(i.instance_id, 0))
        
    def _random(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Random"""
        return random.choice(instances)
        
    def _weighted(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Weighted"""
        total_weight = sum(i.weight for i in instances)
        r = random.uniform(0, total_weight)
        
        current = 0
        for instance in instances:
            current += instance.weight
            if r <= current:
                return instance
                
        return instances[-1]


class DNSManager:
    """Менеджер DNS"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.records: Dict[str, DNSRecord] = {}
        
    def create_record(self, service_id: str, record_type: str = "A",
                       ttl: int = 60) -> DNSRecord:
        """Создание DNS записи"""
        service = self.registry.services.get(service_id)
        if not service:
            return None
            
        values = [i.address for i in service.instances if i.healthy]
        
        record = DNSRecord(
            record_id=f"dns_{uuid.uuid4().hex[:8]}",
            service_id=service_id,
            name=service.dns_name,
            record_type=record_type,
            ttl=ttl,
            values=values
        )
        self.records[record.record_id] = record
        return record
        
    def resolve(self, name: str) -> List[str]:
        """Разрешение DNS имени"""
        for record in self.records.values():
            if record.name == name and record.active:
                return record.values
        return []
        
    def update_records(self):
        """Обновление записей"""
        for record in self.records.values():
            service = self.registry.services.get(record.service_id)
            if service:
                record.values = [i.address for i in service.instances if i.healthy]


class ServiceCatalog:
    """Каталог сервисов"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        
    def list_services(self, namespace: str = None) -> List[Dict]:
        """Список сервисов"""
        services = []
        
        for service in self.registry.services.values():
            if namespace and service.namespace != namespace:
                continue
                
            services.append({
                "service_id": service.service_id,
                "name": service.name,
                "namespace": service.namespace,
                "dns_name": service.dns_name,
                "healthy": service.healthy_count,
                "total": service.total_count
            })
            
        return services
        
    def get_service(self, service_id: str) -> Dict:
        """Получение сервиса"""
        service = self.registry.services.get(service_id)
        if not service:
            return {"error": "Service not found"}
            
        return {
            "service_id": service.service_id,
            "name": service.name,
            "namespace": service.namespace,
            "dns_name": service.dns_name,
            "lb_strategy": service.lb_strategy.value,
            "instances": [
                {
                    "instance_id": i.instance_id,
                    "address": i.address,
                    "port": i.port,
                    "healthy": i.healthy,
                    "version": i.version
                }
                for i in service.instances
            ]
        }
        
    def search(self, tags: List[str] = None, metadata: Dict = None) -> List[Dict]:
        """Поиск сервисов"""
        results = []
        
        for service in self.registry.services.values():
            if tags:
                if not all(t in service.tags for t in tags):
                    continue
                    
            if metadata:
                if not all(service.metadata.get(k) == v for k, v in metadata.items()):
                    continue
                    
            results.append(self.get_service(service.service_id))
            
        return results


class ServiceDiscoveryPlatform:
    """Платформа Service Discovery"""
    
    def __init__(self):
        self.registry = ServiceRegistry()
        self.health_checker = HealthChecker(self.registry)
        self.load_balancer = LoadBalancer(self.registry)
        self.dns_manager = DNSManager(self.registry)
        self.catalog = ServiceCatalog(self.registry)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        services = list(self.registry.services.values())
        instances = list(self.registry.instances.values())
        
        return {
            "services": len(services),
            "instances": len(instances),
            "healthy_instances": len([i for i in instances if i.healthy]),
            "unhealthy_instances": len([i for i in instances if not i.healthy]),
            "health_checks": len(self.health_checker.checks),
            "dns_records": len(self.dns_manager.records),
            "namespaces": len(set(s.namespace for s in services))
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 134: Service Discovery Platform")
    print("=" * 60)
    
    async def demo():
        platform = ServiceDiscoveryPlatform()
        print("✓ Service Discovery Platform created")
        
        # Register services
        print("\n📦 Registering Services...")
        
        services_data = [
            ("api-gateway", "production", LoadBalancerStrategy.ROUND_ROBIN, ["api", "gateway"]),
            ("user-service", "production", LoadBalancerStrategy.LEAST_CONNECTIONS, ["users", "auth"]),
            ("order-service", "production", LoadBalancerStrategy.WEIGHTED, ["orders", "commerce"]),
            ("notification-service", "production", LoadBalancerStrategy.RANDOM, ["notifications"]),
            ("cache-service", "infrastructure", LoadBalancerStrategy.CONSISTENT_HASH, ["cache", "redis"])
        ]
        
        created_services = []
        for name, namespace, strategy, tags in services_data:
            service = platform.registry.register_service(
                name, namespace, strategy, tags=tags
            )
            created_services.append(service)
            print(f"  ✓ {name} ({namespace}) - {strategy.value}")
            
        # Register instances
        print("\n🖥️ Registering Instances...")
        
        for service in created_services:
            # Register 3 instances per service
            for i in range(3):
                instance = platform.registry.register_instance(
                    service.service_id,
                    f"10.0.{created_services.index(service)}.{i + 1}",
                    8080 + i,
                    version=f"1.{i}.0",
                    weight=100 - i * 20
                )
                
            print(f"  ✓ {service.name}: {service.total_count} instances")
            
        # Add health checks
        print("\n❤️ Adding Health Checks...")
        
        for instance in platform.registry.instances.values():
            check = platform.health_checker.add_check(
                instance.service_id,
                instance.instance_id,
                HealthCheckType.HTTP,
                http_path="/health",
                interval_seconds=30
            )
            
        print(f"  ✓ {len(platform.health_checker.checks)} health checks configured")
        
        # Run health checks
        print("\n🔍 Running Health Checks...")
        
        results = await platform.health_checker.run_all_checks()
        print(f"  ✓ Passed: {results['passed']}")
        print(f"  ✗ Failed: {results['failed']}")
        
        # Create DNS records
        print("\n🌐 Creating DNS Records...")
        
        for service in created_services:
            record = platform.dns_manager.create_record(service.service_id)
            if record:
                print(f"  ✓ {record.name}: {len(record.values)} IPs")
                
        # Test DNS resolution
        print("\n🔎 DNS Resolution:")
        
        for service in created_services[:3]:
            ips = platform.dns_manager.resolve(service.dns_name)
            print(f"  {service.dns_name} -> {ips}")
            
        # Test load balancing
        print("\n⚖️ Load Balancing Test:")
        
        for service in created_services:
            print(f"\n  {service.name} ({service.lb_strategy.value}):")
            
            selections = defaultdict(int)
            for _ in range(10):
                instance = platform.load_balancer.get_endpoint(service.service_id)
                if instance:
                    selections[instance.address] += 1
                    
            for addr, count in selections.items():
                bar = "█" * count
                print(f"    {addr}: {bar} ({count})")
                
        # Service catalog
        print("\n📋 Service Catalog:")
        
        services_list = platform.catalog.list_services()
        for svc in services_list:
            status_icon = "🟢" if svc["healthy"] == svc["total"] else "🟡" if svc["healthy"] > 0 else "🔴"
            print(f"  {status_icon} {svc['name']}")
            print(f"     Namespace: {svc['namespace']}")
            print(f"     DNS: {svc['dns_name']}")
            print(f"     Health: {svc['healthy']}/{svc['total']}")
            
        # Search services
        print("\n🔍 Service Search:")
        
        api_services = platform.catalog.search(tags=["api"])
        print(f"  Services with 'api' tag: {len(api_services)}")
        
        # Heartbeat demo
        print("\n💓 Heartbeat Updates:")
        
        for instance_id in list(platform.registry.instances.keys())[:3]:
            result = platform.registry.heartbeat(instance_id)
            instance = platform.registry.instances.get(instance_id)
            print(f"  ✓ {instance.address}:{instance.port} - heartbeat updated")
            
        # Deregister instance
        print("\n🗑️ Deregistering Instance:")
        
        instance_to_remove = list(platform.registry.instances.keys())[0]
        instance = platform.registry.instances.get(instance_to_remove)
        print(f"  Removing: {instance.address}:{instance.port}")
        
        platform.registry.deregister_instance(instance_to_remove)
        print(f"  ✓ Instance deregistered")
        
        # Update DNS
        platform.dns_manager.update_records()
        print(f"  ✓ DNS records updated")
        
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Services: {stats['services']}")
        print(f"  Namespaces: {stats['namespaces']}")
        print(f"  Instances: {stats['instances']}")
        print(f"    Healthy: {stats['healthy_instances']}")
        print(f"    Unhealthy: {stats['unhealthy_instances']}")
        print(f"  Health Checks: {stats['health_checks']}")
        print(f"  DNS Records: {stats['dns_records']}")
        
        # Dashboard
        print("\n📋 Service Discovery Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │              Service Discovery Overview                     │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Services:           {stats['services']:>10}                        │")
        print(f"  │ Namespaces:         {stats['namespaces']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Instances:    {stats['instances']:>10}                        │")
        print(f"  │   Healthy:          {stats['healthy_instances']:>10}                        │")
        print(f"  │   Unhealthy:        {stats['unhealthy_instances']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Health Checks:      {stats['health_checks']:>10}                        │")
        print(f"  │ DNS Records:        {stats['dns_records']:>10}                        │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Service Discovery Platform initialized!")
    print("=" * 60)
