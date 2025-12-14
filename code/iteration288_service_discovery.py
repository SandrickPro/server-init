#!/usr/bin/env python3
"""
Server Init - Iteration 288: Service Discovery Platform
Платформа Service Discovery

Функционал:
- Service Registration - регистрация сервисов
- Service Discovery - обнаружение сервисов
- Health Checking - проверка здоровья
- DNS Resolution - DNS разрешение
- Load Balancing - балансировка нагрузки
- Service Catalog - каталог сервисов
- Watch/Subscribe - подписка на изменения
- TTL Management - управление временем жизни
"""

import asyncio
import random
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
import uuid
import hashlib


class ServiceStatus(Enum):
    """Статус сервиса"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
    DEREGISTERING = "deregistering"


class HealthCheckType(Enum):
    """Тип проверки здоровья"""
    HTTP = "http"
    TCP = "tcp"
    GRPC = "grpc"
    TTL = "ttl"
    SCRIPT = "script"


class LoadBalanceStrategy(Enum):
    """Стратегия балансировки"""
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED = "weighted"
    CONSISTENT_HASH = "consistent_hash"


@dataclass
class HealthCheck:
    """Конфигурация проверки здоровья"""
    check_id: str
    
    # Type
    check_type: HealthCheckType = HealthCheckType.HTTP
    
    # HTTP check
    http_url: str = ""
    http_method: str = "GET"
    expected_status: int = 200
    
    # TCP check
    tcp_address: str = ""
    
    # Intervals
    interval_seconds: int = 10
    timeout_seconds: int = 5
    
    # Thresholds
    healthy_threshold: int = 2
    unhealthy_threshold: int = 3
    
    # Current state
    consecutive_successes: int = 0
    consecutive_failures: int = 0
    last_check: Optional[datetime] = None
    last_status: ServiceStatus = ServiceStatus.UNKNOWN


@dataclass
class ServiceInstance:
    """Экземпляр сервиса"""
    instance_id: str
    service_name: str
    
    # Address
    address: str = ""
    port: int = 0
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    meta: Dict[str, str] = field(default_factory=dict)
    
    # Health
    status: ServiceStatus = ServiceStatus.UNKNOWN
    health_check: Optional[HealthCheck] = None
    
    # Weight for load balancing
    weight: int = 100
    
    # TTL
    ttl_seconds: int = 0
    last_heartbeat: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    # Stats
    requests_count: int = 0
    active_connections: int = 0
    
    # Registration
    registered_at: datetime = field(default_factory=datetime.now)


@dataclass
class Service:
    """Сервис"""
    service_id: str
    name: str
    
    # Instances
    instances: Dict[str, ServiceInstance] = field(default_factory=dict)
    
    # Default settings
    default_tags: List[str] = field(default_factory=list)
    default_meta: Dict[str, str] = field(default_factory=dict)
    
    # Stats
    total_instances: int = 0
    healthy_instances: int = 0
    
    # Created
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ServiceQuery:
    """Запрос сервиса"""
    service_name: str
    
    # Filters
    tags: List[str] = field(default_factory=list)
    meta: Dict[str, str] = field(default_factory=dict)
    status: Optional[ServiceStatus] = None
    
    # Options
    healthy_only: bool = True
    near: str = ""  # Prefer instances near this datacenter


@dataclass
class Watcher:
    """Наблюдатель изменений"""
    watcher_id: str
    service_name: str
    
    # Callback
    callback: Optional[Callable] = None
    
    # Current version
    last_index: int = 0
    
    # Active
    active: bool = True


class ServiceDiscoveryManager:
    """Менеджер Service Discovery"""
    
    def __init__(self):
        self.services: Dict[str, Service] = {}
        self.instances: Dict[str, ServiceInstance] = {}
        self.watchers: Dict[str, List[Watcher]] = {}
        
        # Index for changes
        self.current_index: int = 0
        
        # DNS cache
        self.dns_cache: Dict[str, List[str]] = {}
        
        # Load balancer state
        self.lb_counters: Dict[str, int] = {}
        
        # Stats
        self.registrations: int = 0
        self.deregistrations: int = 0
        self.queries: int = 0
        
    async def register(self, service_name: str,
                      address: str,
                      port: int,
                      tags: List[str] = None,
                      meta: Dict[str, str] = None,
                      health_check: HealthCheck = None,
                      ttl_seconds: int = 0,
                      weight: int = 100) -> ServiceInstance:
        """Регистрация экземпляра сервиса"""
        # Get or create service
        if service_name not in self.services:
            service = Service(
                service_id=f"svc_{uuid.uuid4().hex[:8]}",
                name=service_name
            )
            self.services[service_name] = service
        else:
            service = self.services[service_name]
            
        # Create instance
        instance = ServiceInstance(
            instance_id=f"inst_{uuid.uuid4().hex[:12]}",
            service_name=service_name,
            address=address,
            port=port,
            tags=tags or [],
            meta=meta or {},
            weight=weight,
            ttl_seconds=ttl_seconds,
            health_check=health_check
        )
        
        if ttl_seconds > 0:
            instance.expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
            
        # Initial health check
        if health_check:
            await self._perform_health_check(instance)
        else:
            instance.status = ServiceStatus.HEALTHY
            
        # Register
        service.instances[instance.instance_id] = instance
        service.total_instances += 1
        
        if instance.status == ServiceStatus.HEALTHY:
            service.healthy_instances += 1
            
        self.instances[instance.instance_id] = instance
        self.registrations += 1
        
        # Update index and notify
        self._update_index()
        await self._notify_watchers(service_name)
        
        # Update DNS
        self._update_dns(service_name)
        
        return instance
        
    async def deregister(self, instance_id: str) -> bool:
        """Отмена регистрации"""
        instance = self.instances.get(instance_id)
        if not instance:
            return False
            
        instance.status = ServiceStatus.DEREGISTERING
        
        service = self.services.get(instance.service_name)
        if service:
            if instance_id in service.instances:
                del service.instances[instance_id]
                service.total_instances -= 1
                
        del self.instances[instance_id]
        self.deregistrations += 1
        
        # Update index and notify
        self._update_index()
        await self._notify_watchers(instance.service_name)
        
        # Update DNS
        self._update_dns(instance.service_name)
        
        return True
        
    async def heartbeat(self, instance_id: str) -> bool:
        """Обновление heartbeat"""
        instance = self.instances.get(instance_id)
        if not instance:
            return False
            
        instance.last_heartbeat = datetime.now()
        
        if instance.ttl_seconds > 0:
            instance.expires_at = datetime.now() + timedelta(seconds=instance.ttl_seconds)
            
        return True
        
    async def discover(self, query: ServiceQuery) -> List[ServiceInstance]:
        """Обнаружение сервисов"""
        self.queries += 1
        
        service = self.services.get(query.service_name)
        if not service:
            return []
            
        results = []
        
        for instance in service.instances.values():
            # Filter by status
            if query.healthy_only and instance.status != ServiceStatus.HEALTHY:
                continue
                
            if query.status and instance.status != query.status:
                continue
                
            # Filter by tags
            if query.tags:
                if not all(tag in instance.tags for tag in query.tags):
                    continue
                    
            # Filter by meta
            if query.meta:
                if not all(instance.meta.get(k) == v for k, v in query.meta.items()):
                    continue
                    
            results.append(instance)
            
        return results
        
    async def get_instance(self, service_name: str,
                          strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN) -> Optional[ServiceInstance]:
        """Получение экземпляра с балансировкой"""
        query = ServiceQuery(service_name=service_name, healthy_only=True)
        instances = await self.discover(query)
        
        if not instances:
            return None
            
        return self._select_instance(service_name, instances, strategy)
        
    def _select_instance(self, service_name: str,
                        instances: List[ServiceInstance],
                        strategy: LoadBalanceStrategy) -> ServiceInstance:
        """Выбор экземпляра"""
        if strategy == LoadBalanceStrategy.ROUND_ROBIN:
            counter = self.lb_counters.get(service_name, 0)
            instance = instances[counter % len(instances)]
            self.lb_counters[service_name] = counter + 1
            return instance
            
        elif strategy == LoadBalanceStrategy.RANDOM:
            return random.choice(instances)
            
        elif strategy == LoadBalanceStrategy.LEAST_CONNECTIONS:
            return min(instances, key=lambda x: x.active_connections)
            
        elif strategy == LoadBalanceStrategy.WEIGHTED:
            total_weight = sum(i.weight for i in instances)
            r = random.randint(1, total_weight)
            cumulative = 0
            
            for instance in instances:
                cumulative += instance.weight
                if r <= cumulative:
                    return instance
                    
            return instances[-1]
            
        elif strategy == LoadBalanceStrategy.CONSISTENT_HASH:
            # Simple consistent hash
            key = f"{service_name}_{datetime.now().minute}"
            hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)
            return instances[hash_value % len(instances)]
            
        return instances[0]
        
    async def watch(self, service_name: str,
                   callback: Callable) -> Watcher:
        """Подписка на изменения"""
        watcher = Watcher(
            watcher_id=f"watch_{uuid.uuid4().hex[:8]}",
            service_name=service_name,
            callback=callback,
            last_index=self.current_index
        )
        
        if service_name not in self.watchers:
            self.watchers[service_name] = []
            
        self.watchers[service_name].append(watcher)
        return watcher
        
    def unwatch(self, watcher_id: str):
        """Отписка от изменений"""
        for service_name, watchers in self.watchers.items():
            self.watchers[service_name] = [
                w for w in watchers if w.watcher_id != watcher_id
            ]
            
    async def _notify_watchers(self, service_name: str):
        """Уведомление наблюдателей"""
        if service_name not in self.watchers:
            return
            
        service = self.services.get(service_name)
        instances = list(service.instances.values()) if service else []
        
        for watcher in self.watchers[service_name]:
            if watcher.active and watcher.callback:
                try:
                    await watcher.callback(service_name, instances)
                    watcher.last_index = self.current_index
                except Exception:
                    pass
                    
    def _update_index(self):
        """Обновление индекса"""
        self.current_index += 1
        
    def _update_dns(self, service_name: str):
        """Обновление DNS кэша"""
        service = self.services.get(service_name)
        if not service:
            self.dns_cache.pop(service_name, None)
            return
            
        addresses = []
        for instance in service.instances.values():
            if instance.status == ServiceStatus.HEALTHY:
                addresses.append(f"{instance.address}:{instance.port}")
                
        self.dns_cache[service_name] = addresses
        
    def dns_lookup(self, service_name: str) -> List[str]:
        """DNS lookup"""
        return self.dns_cache.get(service_name, [])
        
    async def _perform_health_check(self, instance: ServiceInstance) -> bool:
        """Выполнение проверки здоровья"""
        check = instance.health_check
        if not check:
            return True
            
        check.last_check = datetime.now()
        
        # Simulate health check
        await asyncio.sleep(random.uniform(0.01, 0.05))
        success = random.random() < 0.95  # 95% success rate
        
        if success:
            check.consecutive_successes += 1
            check.consecutive_failures = 0
            
            if check.consecutive_successes >= check.healthy_threshold:
                old_status = instance.status
                instance.status = ServiceStatus.HEALTHY
                check.last_status = ServiceStatus.HEALTHY
                
                if old_status != ServiceStatus.HEALTHY:
                    service = self.services.get(instance.service_name)
                    if service:
                        service.healthy_instances += 1
        else:
            check.consecutive_failures += 1
            check.consecutive_successes = 0
            
            if check.consecutive_failures >= check.unhealthy_threshold:
                old_status = instance.status
                instance.status = ServiceStatus.UNHEALTHY
                check.last_status = ServiceStatus.UNHEALTHY
                
                if old_status == ServiceStatus.HEALTHY:
                    service = self.services.get(instance.service_name)
                    if service:
                        service.healthy_instances = max(0, service.healthy_instances - 1)
                        
        return success
        
    async def run_health_checks(self):
        """Запуск проверок здоровья"""
        for instance in self.instances.values():
            if instance.health_check:
                now = datetime.now()
                last = instance.health_check.last_check
                interval = instance.health_check.interval_seconds
                
                if not last or (now - last).total_seconds() >= interval:
                    await self._perform_health_check(instance)
                    
            # Check TTL expiration
            if instance.expires_at and instance.expires_at < datetime.now():
                instance.status = ServiceStatus.CRITICAL
                
    async def cleanup_expired(self) -> int:
        """Очистка истёкших экземпляров"""
        expired = []
        now = datetime.now()
        
        for instance_id, instance in self.instances.items():
            if instance.expires_at and instance.expires_at < now:
                expired.append(instance_id)
                
        for instance_id in expired:
            await self.deregister(instance_id)
            
        return len(expired)
        
    def get_catalog(self) -> Dict[str, Any]:
        """Каталог сервисов"""
        catalog = {}
        
        for name, service in self.services.items():
            catalog[name] = {
                "total_instances": service.total_instances,
                "healthy_instances": service.healthy_instances,
                "tags": list(set(
                    tag for inst in service.instances.values()
                    for tag in inst.tags
                ))
            }
            
        return catalog
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_instances = len(self.instances)
        healthy_instances = sum(
            1 for i in self.instances.values()
            if i.status == ServiceStatus.HEALTHY
        )
        
        return {
            "services": len(self.services),
            "total_instances": total_instances,
            "healthy_instances": healthy_instances,
            "registrations": self.registrations,
            "deregistrations": self.deregistrations,
            "queries": self.queries,
            "watchers": sum(len(w) for w in self.watchers.values()),
            "current_index": self.current_index
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 288: Service Discovery Platform")
    print("=" * 60)
    
    manager = ServiceDiscoveryManager()
    print("✓ Service Discovery Manager created")
    
    # Register services
    print("\n📝 Registering Services...")
    
    # User service
    for i in range(3):
        health_check = HealthCheck(
            check_id=f"check_user_{i}",
            check_type=HealthCheckType.HTTP,
            http_url=f"http://user-{i}:8080/health",
            interval_seconds=10
        )
        
        instance = await manager.register(
            "user-service",
            f"10.0.1.{10+i}",
            8080,
            tags=["api", "users", f"zone-{i % 2}"],
            meta={"version": "1.2.0", "environment": "production"},
            health_check=health_check,
            weight=100 if i == 0 else 80
        )
        print(f"  📝 user-service: {instance.address}:{instance.port}")
        
    # Order service
    for i in range(2):
        instance = await manager.register(
            "order-service",
            f"10.0.2.{10+i}",
            8080,
            tags=["api", "orders"],
            meta={"version": "2.0.0"},
            ttl_seconds=60
        )
        print(f"  📝 order-service: {instance.address}:{instance.port}")
        
    # Payment service
    instance = await manager.register(
        "payment-service",
        "10.0.3.10",
        8080,
        tags=["api", "payments", "critical"],
        meta={"version": "1.0.5"}
    )
    print(f"  📝 payment-service: {instance.address}:{instance.port}")
    
    # Notification service
    for i in range(2):
        instance = await manager.register(
            "notification-service",
            f"10.0.4.{10+i}",
            8080,
            tags=["api", "notifications"],
            meta={"version": "1.1.0"}
        )
        print(f"  📝 notification-service: {instance.address}:{instance.port}")
        
    # Watch for changes
    print("\n👁️ Setting up Watchers...")
    
    async def on_service_change(service_name: str, instances: List[ServiceInstance]):
        print(f"  🔔 Change in {service_name}: {len(instances)} instances")
        
    watcher = await manager.watch("user-service", on_service_change)
    print(f"  👁️ Watching user-service: {watcher.watcher_id}")
    
    # Service discovery
    print("\n🔍 Discovering Services...")
    
    # Find all user-service instances
    query = ServiceQuery(service_name="user-service")
    instances = await manager.discover(query)
    print(f"\n  🔍 user-service: {len(instances)} instances")
    
    for inst in instances:
        print(f"    • {inst.address}:{inst.port} ({inst.status.value})")
        
    # Find by tags
    query = ServiceQuery(service_name="user-service", tags=["zone-0"])
    instances = await manager.discover(query)
    print(f"\n  🔍 user-service (zone-0): {len(instances)} instances")
    
    # Get instance with load balancing
    print("\n⚖️ Load Balanced Discovery...")
    
    for strategy in LoadBalanceStrategy:
        instance = await manager.get_instance("user-service", strategy)
        if instance:
            print(f"  {strategy.value}: {instance.address}:{instance.port}")
            
    # DNS lookup
    print("\n🌐 DNS Lookup...")
    
    for service_name in manager.services:
        addresses = manager.dns_lookup(service_name)
        print(f"  {service_name}: {addresses}")
        
    # Run health checks
    print("\n💚 Running Health Checks...")
    
    await manager.run_health_checks()
    
    for name, service in manager.services.items():
        healthy = service.healthy_instances
        total = service.total_instances
        print(f"  {name}: {healthy}/{total} healthy")
        
    # Heartbeat
    print("\n💓 Sending Heartbeats...")
    
    for instance in list(manager.instances.values())[:3]:
        await manager.heartbeat(instance.instance_id)
        print(f"  💓 {instance.service_name}: heartbeat sent")
        
    # Simulate changes
    print("\n📝 Registering new instance...")
    
    new_instance = await manager.register(
        "user-service",
        "10.0.1.100",
        8080,
        tags=["api", "users", "new"]
    )
    
    # Deregister
    print("\n🗑️ Deregistering instance...")
    
    await manager.deregister(new_instance.instance_id)
    
    # Service catalog
    print("\n📚 Service Catalog:")
    
    catalog = manager.get_catalog()
    
    print("\n  ┌────────────────────────┬─────────────┬─────────────┬─────────────────────────┐")
    print("  │ Service                │ Total       │ Healthy     │ Tags                    │")
    print("  ├────────────────────────┼─────────────┼─────────────┼─────────────────────────┤")
    
    for name, info in catalog.items():
        name_display = name[:22].ljust(22)
        total = str(info['total_instances']).ljust(11)
        healthy = str(info['healthy_instances']).ljust(11)
        tags = ", ".join(info['tags'][:3])[:23].ljust(23)
        
        print(f"  │ {name_display} │ {total} │ {healthy} │ {tags} │")
        
    print("  └────────────────────────┴─────────────┴─────────────┴─────────────────────────┘")
    
    # Instance details
    print("\n📋 Instance Details:")
    
    for name, service in list(manager.services.items())[:2]:
        print(f"\n  📦 {name}:")
        
        for inst in list(service.instances.values())[:3]:
            status_icon = "🟢" if inst.status == ServiceStatus.HEALTHY else "🔴"
            
            print(f"    {status_icon} {inst.instance_id[:16]}:")
            print(f"      Address: {inst.address}:{inst.port}")
            print(f"      Tags: {inst.tags}")
            print(f"      Weight: {inst.weight}")
            
            if inst.health_check:
                hc = inst.health_check
                print(f"      Health: {hc.check_type.value}, interval={hc.interval_seconds}s")
                
    # Health check status
    print("\n💚 Health Check Status:")
    
    for inst in manager.instances.values():
        if inst.health_check:
            hc = inst.health_check
            status_icon = "🟢" if inst.status == ServiceStatus.HEALTHY else "🔴"
            
            print(f"  {status_icon} {inst.service_name}/{inst.address}:")
            print(f"    Consecutive Success: {hc.consecutive_successes}")
            print(f"    Consecutive Failures: {hc.consecutive_failures}")
            
    # Watchers
    print("\n👁️ Active Watchers:")
    
    for service_name, watchers in manager.watchers.items():
        print(f"\n  {service_name}: {len(watchers)} watchers")
        for w in watchers:
            print(f"    • {w.watcher_id} (index: {w.last_index})")
            
    # Statistics
    print("\n📊 Discovery Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Services: {stats['services']}")
    print(f"  Total Instances: {stats['total_instances']}")
    print(f"  Healthy Instances: {stats['healthy_instances']}")
    print(f"\n  Registrations: {stats['registrations']}")
    print(f"  Deregistrations: {stats['deregistrations']}")
    print(f"  Queries: {stats['queries']}")
    print(f"  Active Watchers: {stats['watchers']}")
    print(f"  Current Index: {stats['current_index']}")
    
    health_rate = stats['healthy_instances'] / max(stats['total_instances'], 1) * 100
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Service Discovery Dashboard                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Registered Services:           {stats['services']:>12}                        │")
    print(f"│ Total Instances:               {stats['total_instances']:>12}                        │")
    print(f"│ Healthy Instances:             {stats['healthy_instances']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Health Rate:                   {health_rate:>11.1f}%                        │")
    print(f"│ Discovery Queries:             {stats['queries']:>12}                        │")
    print(f"│ Active Watchers:               {stats['watchers']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Service Discovery Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
