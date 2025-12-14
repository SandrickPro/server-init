#!/usr/bin/env python3
"""
Server Init - Iteration 265: Service Discovery Platform
Платформа обнаружения сервисов

Функционал:
- Service Registration - регистрация сервисов
- Service Discovery - обнаружение сервисов
- Health Checking - проверка здоровья
- Load Balancing - балансировка нагрузки
- Service Metadata - метаданные сервисов
- DNS Integration - интеграция DNS
- Failover Support - поддержка отказоустойчивости
- Watch Mechanism - механизм наблюдения
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
import uuid


class ServiceStatus(Enum):
    """Статус сервиса"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DRAINING = "draining"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"


class LoadBalanceStrategy(Enum):
    """Стратегия балансировки"""
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED = "weighted"
    IP_HASH = "ip_hash"


class HealthCheckType(Enum):
    """Тип проверки здоровья"""
    HTTP = "http"
    TCP = "tcp"
    GRPC = "grpc"
    SCRIPT = "script"


@dataclass
class HealthCheckConfig:
    """Конфигурация проверки здоровья"""
    check_id: str
    
    # Type
    check_type: HealthCheckType = HealthCheckType.HTTP
    
    # Endpoint
    endpoint: str = "/health"
    port: int = 80
    
    # Timing
    interval_seconds: int = 10
    timeout_seconds: int = 5
    
    # Thresholds
    healthy_threshold: int = 2
    unhealthy_threshold: int = 3


@dataclass
class ServiceEndpoint:
    """Эндпоинт сервиса"""
    endpoint_id: str
    
    # Address
    host: str = ""
    port: int = 80
    
    # Weight for load balancing
    weight: int = 100
    
    # Status
    status: ServiceStatus = ServiceStatus.UNKNOWN
    
    # Stats
    active_connections: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    
    # Health check
    last_health_check: datetime = field(default_factory=datetime.now)
    consecutive_successes: int = 0
    consecutive_failures: int = 0


@dataclass
class ServiceInstance:
    """Экземпляр сервиса"""
    instance_id: str
    service_name: str
    
    # Endpoint
    endpoint: ServiceEndpoint = field(default_factory=lambda: ServiceEndpoint(
        endpoint_id=f"ep_{uuid.uuid4().hex[:8]}"
    ))
    
    # Metadata
    metadata: Dict[str, str] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    # Version
    version: str = "1.0.0"
    
    # Health check
    health_check: HealthCheckConfig = field(default_factory=lambda: HealthCheckConfig(
        check_id=f"hc_{uuid.uuid4().hex[:8]}"
    ))
    
    # Timing
    registered_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    
    # TTL
    ttl_seconds: int = 30


@dataclass
class ServiceDefinition:
    """Определение сервиса"""
    service_id: str
    name: str
    
    # Instances
    instances: List[ServiceInstance] = field(default_factory=list)
    
    # Load balancing
    lb_strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN
    
    # Current index for round robin
    current_index: int = 0
    
    # Metadata
    description: str = ""
    domain: str = ""  # DNS domain
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ServiceQuery:
    """Запрос на поиск сервиса"""
    service_name: str
    
    # Filters
    tags: List[str] = field(default_factory=list)
    version: Optional[str] = None
    status: Optional[ServiceStatus] = None
    
    # Options
    healthy_only: bool = True


@dataclass
class ServiceWatch:
    """Наблюдение за сервисом"""
    watch_id: str
    service_name: str
    
    # Callback
    callback: Optional[Callable[[str, List[ServiceInstance]], None]] = None
    
    # Status
    active: bool = True
    
    # Last known instances
    last_instances: List[str] = field(default_factory=list)


class ServiceDiscoveryManager:
    """Менеджер обнаружения сервисов"""
    
    def __init__(self):
        self.services: Dict[str, ServiceDefinition] = {}
        self.watches: List[ServiceWatch] = []
        self._cleanup_task: Optional[asyncio.Task] = None
        
    def register_service(self, name: str,
                        lb_strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN,
                        description: str = "") -> ServiceDefinition:
        """Регистрация сервиса"""
        if name not in self.services:
            service = ServiceDefinition(
                service_id=f"svc_{uuid.uuid4().hex[:8]}",
                name=name,
                lb_strategy=lb_strategy,
                description=description,
                domain=f"{name}.service.local"
            )
            self.services[name] = service
            
        return self.services[name]
        
    def register_instance(self, service_name: str,
                         host: str, port: int,
                         metadata: Dict[str, str] = None,
                         tags: List[str] = None,
                         version: str = "1.0.0",
                         weight: int = 100) -> ServiceInstance:
        """Регистрация экземпляра"""
        service = self.register_service(service_name)
        
        # Check for existing instance
        for inst in service.instances:
            if inst.endpoint.host == host and inst.endpoint.port == port:
                inst.last_heartbeat = datetime.now()
                return inst
                
        instance = ServiceInstance(
            instance_id=f"inst_{uuid.uuid4().hex[:8]}",
            service_name=service_name,
            endpoint=ServiceEndpoint(
                endpoint_id=f"ep_{uuid.uuid4().hex[:8]}",
                host=host,
                port=port,
                weight=weight,
                status=ServiceStatus.UNKNOWN
            ),
            metadata=metadata or {},
            tags=tags or [],
            version=version
        )
        
        service.instances.append(instance)
        
        # Notify watches
        self._notify_watches(service_name)
        
        return instance
        
    def deregister_instance(self, service_name: str, instance_id: str) -> bool:
        """Отмена регистрации экземпляра"""
        service = self.services.get(service_name)
        if not service:
            return False
            
        for i, inst in enumerate(service.instances):
            if inst.instance_id == instance_id:
                service.instances.pop(i)
                self._notify_watches(service_name)
                return True
                
        return False
        
    def heartbeat(self, service_name: str, instance_id: str) -> bool:
        """Обновление heartbeat"""
        service = self.services.get(service_name)
        if not service:
            return False
            
        for inst in service.instances:
            if inst.instance_id == instance_id:
                inst.last_heartbeat = datetime.now()
                return True
                
        return False
        
    async def health_check(self, instance: ServiceInstance) -> bool:
        """Проверка здоровья экземпляра"""
        # Simulate health check
        await asyncio.sleep(random.uniform(0.01, 0.05))
        
        healthy = random.random() > 0.1  # 90% healthy
        
        endpoint = instance.endpoint
        
        if healthy:
            endpoint.consecutive_successes += 1
            endpoint.consecutive_failures = 0
            
            if endpoint.consecutive_successes >= instance.health_check.healthy_threshold:
                endpoint.status = ServiceStatus.HEALTHY
        else:
            endpoint.consecutive_failures += 1
            endpoint.consecutive_successes = 0
            
            if endpoint.consecutive_failures >= instance.health_check.unhealthy_threshold:
                endpoint.status = ServiceStatus.UNHEALTHY
                
        endpoint.last_health_check = datetime.now()
        
        return healthy
        
    def _notify_watches(self, service_name: str):
        """Уведомление наблюдателей"""
        service = self.services.get(service_name)
        if not service:
            return
            
        for watch in self.watches:
            if not watch.active:
                continue
                
            if watch.service_name != service_name:
                continue
                
            current_ids = [i.instance_id for i in service.instances]
            
            if set(current_ids) != set(watch.last_instances):
                watch.last_instances = current_ids
                if watch.callback:
                    try:
                        watch.callback(service_name, service.instances)
                    except Exception:
                        pass
                        
    def discover(self, query: ServiceQuery) -> List[ServiceInstance]:
        """Обнаружение сервисов"""
        service = self.services.get(query.service_name)
        if not service:
            return []
            
        results = []
        
        for instance in service.instances:
            # Filter by health
            if query.healthy_only and instance.endpoint.status != ServiceStatus.HEALTHY:
                continue
                
            # Filter by status
            if query.status and instance.endpoint.status != query.status:
                continue
                
            # Filter by version
            if query.version and instance.version != query.version:
                continue
                
            # Filter by tags
            if query.tags:
                if not all(tag in instance.tags for tag in query.tags):
                    continue
                    
            results.append(instance)
            
        return results
        
    def get_endpoint(self, service_name: str, client_ip: str = None) -> Optional[ServiceEndpoint]:
        """Получение эндпоинта по стратегии балансировки"""
        service = self.services.get(service_name)
        if not service:
            return None
            
        # Get healthy instances
        healthy = [i for i in service.instances 
                  if i.endpoint.status == ServiceStatus.HEALTHY]
        
        if not healthy:
            return None
            
        if service.lb_strategy == LoadBalanceStrategy.ROUND_ROBIN:
            service.current_index = (service.current_index + 1) % len(healthy)
            return healthy[service.current_index].endpoint
            
        elif service.lb_strategy == LoadBalanceStrategy.RANDOM:
            return random.choice(healthy).endpoint
            
        elif service.lb_strategy == LoadBalanceStrategy.LEAST_CONNECTIONS:
            return min(healthy, key=lambda i: i.endpoint.active_connections).endpoint
            
        elif service.lb_strategy == LoadBalanceStrategy.WEIGHTED:
            total_weight = sum(i.endpoint.weight for i in healthy)
            r = random.randint(0, total_weight - 1)
            cumulative = 0
            for inst in healthy:
                cumulative += inst.endpoint.weight
                if r < cumulative:
                    return inst.endpoint
            return healthy[-1].endpoint
            
        elif service.lb_strategy == LoadBalanceStrategy.IP_HASH:
            if client_ip:
                hash_value = hash(client_ip)
                index = hash_value % len(healthy)
                return healthy[index].endpoint
            return random.choice(healthy).endpoint
            
        return None
        
    def watch(self, service_name: str,
             callback: Callable[[str, List[ServiceInstance]], None]) -> ServiceWatch:
        """Наблюдение за сервисом"""
        watch = ServiceWatch(
            watch_id=f"watch_{uuid.uuid4().hex[:8]}",
            service_name=service_name,
            callback=callback
        )
        
        self.watches.append(watch)
        
        # Initial notification
        service = self.services.get(service_name)
        if service:
            watch.last_instances = [i.instance_id for i in service.instances]
            callback(service_name, service.instances)
            
        return watch
        
    def unwatch(self, watch_id: str):
        """Отмена наблюдения"""
        self.watches = [w for w in self.watches if w.watch_id != watch_id]
        
    def set_instance_status(self, service_name: str, instance_id: str,
                           status: ServiceStatus):
        """Установка статуса экземпляра"""
        service = self.services.get(service_name)
        if not service:
            return
            
        for inst in service.instances:
            if inst.instance_id == instance_id:
                inst.endpoint.status = status
                self._notify_watches(service_name)
                break
                
    def get_dns_record(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Получение DNS записи для сервиса"""
        service = self.services.get(service_name)
        if not service:
            return None
            
        healthy = [i for i in service.instances 
                  if i.endpoint.status == ServiceStatus.HEALTHY]
        
        return {
            "domain": service.domain,
            "type": "SRV",
            "records": [
                {
                    "priority": 0,
                    "weight": i.endpoint.weight,
                    "port": i.endpoint.port,
                    "target": i.endpoint.host
                }
                for i in healthy
            ]
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_instances = sum(len(s.instances) for s in self.services.values())
        healthy_instances = sum(
            sum(1 for i in s.instances if i.endpoint.status == ServiceStatus.HEALTHY)
            for s in self.services.values()
        )
        
        statuses = {status: 0 for status in ServiceStatus}
        for service in self.services.values():
            for inst in service.instances:
                statuses[inst.endpoint.status] += 1
                
        return {
            "services_total": len(self.services),
            "instances_total": total_instances,
            "instances_healthy": healthy_instances,
            "watches_active": sum(1 for w in self.watches if w.active),
            "statuses": {s.value: c for s, c in statuses.items()}
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 265: Service Discovery Platform")
    print("=" * 60)
    
    manager = ServiceDiscoveryManager()
    print("✓ Service Discovery Manager created")
    
    # Register services
    print("\n📦 Registering Services...")
    
    services_data = [
        ("api-gateway", LoadBalanceStrategy.ROUND_ROBIN, "API Gateway Service"),
        ("user-service", LoadBalanceStrategy.LEAST_CONNECTIONS, "User Management"),
        ("order-service", LoadBalanceStrategy.WEIGHTED, "Order Processing"),
        ("payment-service", LoadBalanceStrategy.IP_HASH, "Payment Processing"),
    ]
    
    for name, strategy, desc in services_data:
        service = manager.register_service(name, strategy, desc)
        print(f"  📦 {name}: {strategy.value}")
        
    # Register instances
    print("\n🖥️ Registering Instances...")
    
    instances_data = [
        ("api-gateway", "10.0.0.1", 8080, {"region": "us-east"}, ["primary"], 100),
        ("api-gateway", "10.0.0.2", 8080, {"region": "us-west"}, ["secondary"], 100),
        ("user-service", "10.0.1.1", 8081, {"region": "us-east"}, ["primary"], 100),
        ("user-service", "10.0.1.2", 8081, {"region": "us-east"}, ["backup"], 50),
        ("order-service", "10.0.2.1", 8082, {"region": "us-east"}, ["primary"], 80),
        ("order-service", "10.0.2.2", 8082, {"region": "us-west"}, ["primary"], 100),
        ("payment-service", "10.0.3.1", 8083, {"region": "us-east"}, ["secure"], 100),
    ]
    
    for service_name, host, port, metadata, tags, weight in instances_data:
        instance = manager.register_instance(
            service_name, host, port, metadata, tags, "1.0.0", weight
        )
        print(f"  🖥️ {service_name}: {host}:{port}")
        
    # Health checks
    print("\n🏥 Running Health Checks...")
    
    for service in manager.services.values():
        for instance in service.instances:
            await manager.health_check(instance)
            
    # Set some instances healthy
    for service in manager.services.values():
        for instance in service.instances:
            # Force healthy for demo
            instance.endpoint.status = ServiceStatus.HEALTHY
            instance.endpoint.consecutive_successes = 3
            
    # Display services
    print("\n📦 Services:")
    
    print("\n  ┌─────────────────────┬───────────────────────┬──────────┬──────────┬──────────┐")
    print("  │ Service             │ Strategy              │ Instances│ Healthy  │ Domain   │")
    print("  ├─────────────────────┼───────────────────────┼──────────┼──────────┼──────────┤")
    
    for service in manager.services.values():
        name = service.name[:19].ljust(19)
        strategy = service.lb_strategy.value[:21].ljust(21)
        instances = str(len(service.instances))[:8].ljust(8)
        healthy = str(sum(1 for i in service.instances if i.endpoint.status == ServiceStatus.HEALTHY))[:8].ljust(8)
        domain = service.domain[:8].ljust(8)
        
        print(f"  │ {name} │ {strategy} │ {instances} │ {healthy} │ {domain} │")
        
    print("  └─────────────────────┴───────────────────────┴──────────┴──────────┴──────────┘")
    
    # Display instances
    print("\n🖥️ Service Instances:")
    
    print("\n  ┌─────────────────────┬───────────────────┬───────────┬──────────┬──────────┐")
    print("  │ Service             │ Address           │ Status    │ Weight   │ Conn     │")
    print("  ├─────────────────────┼───────────────────┼───────────┼──────────┼──────────┤")
    
    for service in manager.services.values():
        for inst in service.instances:
            svc_name = service.name[:19].ljust(19)
            address = f"{inst.endpoint.host}:{inst.endpoint.port}"[:17].ljust(17)
            status = inst.endpoint.status.value[:9].ljust(9)
            weight = str(inst.endpoint.weight)[:8].ljust(8)
            conns = str(inst.endpoint.active_connections)[:8].ljust(8)
            
            print(f"  │ {svc_name} │ {address} │ {status} │ {weight} │ {conns} │")
            
    print("  └─────────────────────┴───────────────────┴───────────┴──────────┴──────────┘")
    
    # Service discovery
    print("\n🔍 Service Discovery:")
    
    for service_name in ["api-gateway", "user-service"]:
        query = ServiceQuery(service_name=service_name, healthy_only=True)
        results = manager.discover(query)
        print(f"\n  {service_name}: {len(results)} healthy instances")
        for inst in results:
            print(f"    - {inst.endpoint.host}:{inst.endpoint.port} (v{inst.version})")
            
    # Load balancing
    print("\n⚖️ Load Balancing Test:")
    
    for service_name in ["api-gateway", "order-service"]:
        print(f"\n  {service_name} (10 requests):")
        endpoints = []
        for _ in range(10):
            ep = manager.get_endpoint(service_name, f"192.168.1.{random.randint(1, 255)}")
            if ep:
                endpoints.append(f"{ep.host}:{ep.port}")
                
        # Count distribution
        from collections import Counter
        dist = Counter(endpoints)
        for addr, count in dist.items():
            bar = "█" * count + "░" * (10 - count)
            print(f"    {addr}: [{bar}] {count}")
            
    # Setup watch
    print("\n👁️ Setting Up Watch:")
    
    watch_events = []
    
    def on_service_change(service_name: str, instances: List[ServiceInstance]):
        watch_events.append({
            "service": service_name,
            "count": len(instances),
            "time": datetime.now()
        })
        
    watch = manager.watch("api-gateway", on_service_change)
    print(f"  👁️ Watching api-gateway")
    
    # Add new instance
    manager.register_instance("api-gateway", "10.0.0.3", 8080)
    print(f"  📬 Watch events received: {len(watch_events)}")
    
    # DNS records
    print("\n🌐 DNS Records:")
    
    for service_name in ["api-gateway", "user-service"]:
        dns = manager.get_dns_record(service_name)
        if dns:
            print(f"\n  {dns['domain']}:")
            for record in dns['records'][:3]:
                print(f"    SRV {record['priority']} {record['weight']} {record['port']} {record['target']}")
                
    # Status distribution
    print("\n📊 Status Distribution:")
    
    for status in ServiceStatus:
        count = sum(
            1 for s in manager.services.values()
            for i in s.instances
            if i.endpoint.status == status
        )
        if count > 0:
            bar = "█" * count + "░" * (10 - count)
            icon = {
                ServiceStatus.HEALTHY: "🟢",
                ServiceStatus.UNHEALTHY: "🔴",
                ServiceStatus.DRAINING: "🟡",
                ServiceStatus.MAINTENANCE: "🔧",
                ServiceStatus.UNKNOWN: "⚪"
            }.get(status, "⚪")
            print(f"  {icon} {status.value:12s} [{bar}] {count}")
            
    # Statistics
    print("\n📊 Manager Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Services: {stats['services_total']}")
    print(f"  Instances: {stats['instances_total']}")
    print(f"  Healthy: {stats['instances_healthy']}")
    print(f"  Watches: {stats['watches_active']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Service Discovery Dashboard                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Services:                      {stats['services_total']:>12}                        │")
    print(f"│ Instances:                     {stats['instances_total']:>12}                        │")
    print(f"│ Healthy:                       {stats['instances_healthy']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Active Watches:                {stats['watches_active']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Service Discovery Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
