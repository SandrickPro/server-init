#!/usr/bin/env python3
"""
Server Init - Iteration 97: Service Discovery Platform
Платформа обнаружения сервисов

Функционал:
- Service Registration - регистрация сервисов
- Health Checking - проверка здоровья
- DNS Resolution - DNS разрешение
- Load Balancing - балансировка нагрузки
- Service Mesh Integration - интеграция с service mesh
- Multi-Datacenter - мультидатацентр
- Watch Notifications - уведомления об изменениях
- Catalog Management - управление каталогом
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Union, Tuple
from enum import Enum
from collections import defaultdict
import uuid
import random
import hashlib


class ServiceStatus(Enum):
    """Статус сервиса"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    CRITICAL = "critical"
    MAINTENANCE = "maintenance"


class HealthCheckType(Enum):
    """Тип проверки здоровья"""
    HTTP = "http"
    TCP = "tcp"
    GRPC = "grpc"
    SCRIPT = "script"
    TTL = "ttl"


class LoadBalanceStrategy(Enum):
    """Стратегия балансировки"""
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED = "weighted"
    CONSISTENT_HASH = "consistent_hash"


class RegistrationSource(Enum):
    """Источник регистрации"""
    SELF = "self"
    CONSUL = "consul"
    KUBERNETES = "kubernetes"
    EXTERNAL = "external"


@dataclass
class ServiceInstance:
    """Экземпляр сервиса"""
    instance_id: str
    service_name: str = ""
    
    # Сеть
    address: str = ""
    port: int = 0
    
    # Метаданные
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)
    
    # Статус
    status: ServiceStatus = ServiceStatus.UNKNOWN
    
    # Источник
    source: RegistrationSource = RegistrationSource.SELF
    
    # Датацентр
    datacenter: str = "dc1"
    
    # Вес для балансировки
    weight: int = 100
    
    # Время
    registered_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    
    # Статистика
    active_connections: int = 0
    total_requests: int = 0


@dataclass
class HealthCheck:
    """Проверка здоровья"""
    check_id: str
    instance_id: str = ""
    service_name: str = ""
    
    # Тип проверки
    check_type: HealthCheckType = HealthCheckType.HTTP
    
    # Конфигурация
    endpoint: str = ""  # URL или адрес
    interval_seconds: int = 10
    timeout_seconds: int = 5
    
    # HTTP специфика
    http_method: str = "GET"
    expected_status: int = 200
    
    # TCP специфика
    tcp_port: int = 0
    
    # Script специфика
    script: str = ""
    
    # TTL специфика
    ttl_seconds: int = 60
    
    # Пороги
    deregister_critical_service_after: int = 300  # seconds
    success_threshold: int = 2
    failure_threshold: int = 3
    
    # Состояние
    consecutive_successes: int = 0
    consecutive_failures: int = 0
    last_check: Optional[datetime] = None
    last_status: ServiceStatus = ServiceStatus.UNKNOWN
    last_output: str = ""


@dataclass
class ServiceDefinition:
    """Определение сервиса"""
    service_name: str
    
    # Описание
    description: str = ""
    version: str = "1.0.0"
    
    # Настройки
    protocol: str = "http"
    
    # Health check defaults
    default_health_check: Optional[HealthCheck] = None
    
    # Теги
    tags: List[str] = field(default_factory=list)
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Endpoint:
    """Конечная точка для разрешения"""
    instance_id: str
    address: str = ""
    port: int = 0
    weight: int = 100
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class WatchEvent:
    """Событие изменения"""
    event_id: str
    event_type: str = ""  # register, deregister, health_change
    service_name: str = ""
    instance_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)


class HealthChecker:
    """Проверщик здоровья"""
    
    async def check(self, health_check: HealthCheck) -> Tuple[ServiceStatus, str]:
        """Выполнение проверки"""
        # Симуляция проверки
        await asyncio.sleep(0.02)
        
        if health_check.check_type == HealthCheckType.HTTP:
            return await self._check_http(health_check)
        elif health_check.check_type == HealthCheckType.TCP:
            return await self._check_tcp(health_check)
        elif health_check.check_type == HealthCheckType.TTL:
            return await self._check_ttl(health_check)
        else:
            return ServiceStatus.UNKNOWN, "Unknown check type"
            
    async def _check_http(self, check: HealthCheck) -> Tuple[ServiceStatus, str]:
        """HTTP проверка"""
        # Симуляция: 95% успеха
        if random.random() > 0.05:
            return ServiceStatus.HEALTHY, f"HTTP {check.expected_status} OK"
        else:
            return ServiceStatus.UNHEALTHY, "Connection timeout"
            
    async def _check_tcp(self, check: HealthCheck) -> Tuple[ServiceStatus, str]:
        """TCP проверка"""
        # Симуляция
        if random.random() > 0.03:
            return ServiceStatus.HEALTHY, "TCP connection successful"
        else:
            return ServiceStatus.UNHEALTHY, "TCP connection refused"
            
    async def _check_ttl(self, check: HealthCheck) -> Tuple[ServiceStatus, str]:
        """TTL проверка"""
        if check.last_check:
            elapsed = (datetime.now() - check.last_check).total_seconds()
            if elapsed < check.ttl_seconds:
                return ServiceStatus.HEALTHY, f"TTL OK ({int(elapsed)}s elapsed)"
            else:
                return ServiceStatus.CRITICAL, f"TTL expired ({int(elapsed)}s > {check.ttl_seconds}s)"
        return ServiceStatus.UNKNOWN, "No heartbeat received"


class LoadBalancer:
    """Балансировщик нагрузки"""
    
    def __init__(self, strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN):
        self.strategy = strategy
        self.counters: Dict[str, int] = defaultdict(int)
        
    def select(self, endpoints: List[Endpoint],
                key: str = None) -> Optional[Endpoint]:
        """Выбор endpoint"""
        if not endpoints:
            return None
            
        # Фильтруем только healthy
        healthy = [e for e in endpoints if e.weight > 0]
        if not healthy:
            return None
            
        if self.strategy == LoadBalanceStrategy.ROUND_ROBIN:
            return self._round_robin(healthy)
        elif self.strategy == LoadBalanceStrategy.RANDOM:
            return self._random(healthy)
        elif self.strategy == LoadBalanceStrategy.WEIGHTED:
            return self._weighted(healthy)
        elif self.strategy == LoadBalanceStrategy.CONSISTENT_HASH:
            return self._consistent_hash(healthy, key or "default")
        else:
            return healthy[0]
            
    def _round_robin(self, endpoints: List[Endpoint]) -> Endpoint:
        """Round robin выбор"""
        key = ",".join(e.instance_id for e in endpoints)
        idx = self.counters[key] % len(endpoints)
        self.counters[key] += 1
        return endpoints[idx]
        
    def _random(self, endpoints: List[Endpoint]) -> Endpoint:
        """Случайный выбор"""
        return random.choice(endpoints)
        
    def _weighted(self, endpoints: List[Endpoint]) -> Endpoint:
        """Взвешенный выбор"""
        total_weight = sum(e.weight for e in endpoints)
        r = random.randint(0, total_weight - 1)
        
        current = 0
        for endpoint in endpoints:
            current += endpoint.weight
            if r < current:
                return endpoint
                
        return endpoints[-1]
        
    def _consistent_hash(self, endpoints: List[Endpoint],
                          key: str) -> Endpoint:
        """Consistent hashing"""
        hash_val = int(hashlib.md5(key.encode()).hexdigest(), 16)
        idx = hash_val % len(endpoints)
        return endpoints[idx]


class DNSResolver:
    """DNS резолвер для сервисов"""
    
    def __init__(self, domain: str = "service.local"):
        self.domain = domain
        
    def get_srv_record(self, service_name: str,
                        instances: List[ServiceInstance]) -> List[Dict[str, Any]]:
        """SRV записи"""
        records = []
        for inst in instances:
            if inst.status == ServiceStatus.HEALTHY:
                records.append({
                    "name": f"{service_name}.{self.domain}",
                    "type": "SRV",
                    "priority": 0,
                    "weight": inst.weight,
                    "port": inst.port,
                    "target": inst.address
                })
        return records
        
    def get_a_record(self, service_name: str,
                      instances: List[ServiceInstance]) -> List[Dict[str, Any]]:
        """A записи"""
        records = []
        seen = set()
        
        for inst in instances:
            if inst.status == ServiceStatus.HEALTHY and inst.address not in seen:
                records.append({
                    "name": f"{service_name}.{self.domain}",
                    "type": "A",
                    "address": inst.address,
                    "ttl": 60
                })
                seen.add(inst.address)
                
        return records


class ServiceCatalog:
    """Каталог сервисов"""
    
    def __init__(self):
        self.services: Dict[str, ServiceDefinition] = {}
        self.instances: Dict[str, ServiceInstance] = {}
        self.health_checks: Dict[str, HealthCheck] = {}
        
        # Индексы
        self.by_service: Dict[str, Set[str]] = defaultdict(set)
        self.by_datacenter: Dict[str, Set[str]] = defaultdict(set)
        self.by_tag: Dict[str, Set[str]] = defaultdict(set)
        
    def define_service(self, name: str, **kwargs) -> ServiceDefinition:
        """Определение сервиса"""
        definition = ServiceDefinition(
            service_name=name,
            **kwargs
        )
        self.services[name] = definition
        return definition
        
    def register(self, instance: ServiceInstance,
                  health_check: HealthCheck = None) -> None:
        """Регистрация экземпляра"""
        self.instances[instance.instance_id] = instance
        
        # Обновляем индексы
        self.by_service[instance.service_name].add(instance.instance_id)
        self.by_datacenter[instance.datacenter].add(instance.instance_id)
        
        for tag in instance.tags:
            self.by_tag[tag].add(instance.instance_id)
            
        # Регистрируем health check
        if health_check:
            health_check.instance_id = instance.instance_id
            health_check.service_name = instance.service_name
            self.health_checks[health_check.check_id] = health_check
            
    def deregister(self, instance_id: str) -> bool:
        """Дерегистрация экземпляра"""
        instance = self.instances.get(instance_id)
        if not instance:
            return False
            
        # Удаляем из индексов
        self.by_service[instance.service_name].discard(instance_id)
        self.by_datacenter[instance.datacenter].discard(instance_id)
        
        for tag in instance.tags:
            self.by_tag[tag].discard(instance_id)
            
        # Удаляем health checks
        checks_to_remove = [
            cid for cid, check in self.health_checks.items()
            if check.instance_id == instance_id
        ]
        for cid in checks_to_remove:
            del self.health_checks[cid]
            
        del self.instances[instance_id]
        return True
        
    def get_instances(self, service_name: str,
                       tags: List[str] = None,
                       datacenter: str = None,
                       healthy_only: bool = True) -> List[ServiceInstance]:
        """Получение экземпляров"""
        instance_ids = self.by_service.get(service_name, set())
        
        # Фильтр по тегам
        if tags:
            for tag in tags:
                instance_ids = instance_ids & self.by_tag.get(tag, set())
                
        # Фильтр по датацентру
        if datacenter:
            instance_ids = instance_ids & self.by_datacenter.get(datacenter, set())
            
        instances = [self.instances[iid] for iid in instance_ids]
        
        # Фильтр по здоровью
        if healthy_only:
            instances = [i for i in instances if i.status == ServiceStatus.HEALTHY]
            
        return instances


class WatchManager:
    """Менеджер наблюдения за изменениями"""
    
    def __init__(self):
        self.watchers: Dict[str, List[Callable]] = defaultdict(list)
        self.events: List[WatchEvent] = []
        
    def watch(self, service_name: str, callback: Callable) -> str:
        """Подписка на изменения"""
        watch_id = f"watch_{uuid.uuid4().hex[:8]}"
        self.watchers[service_name].append(callback)
        return watch_id
        
    async def notify(self, event: WatchEvent) -> None:
        """Уведомление о событии"""
        self.events.append(event)
        
        # Уведомляем подписчиков
        callbacks = self.watchers.get(event.service_name, [])
        callbacks.extend(self.watchers.get("*", []))  # wildcard
        
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                print(f"Watch callback error: {e}")


class ServiceDiscoveryPlatform:
    """Платформа обнаружения сервисов"""
    
    def __init__(self, datacenter: str = "dc1"):
        self.datacenter = datacenter
        
        self.catalog = ServiceCatalog()
        self.health_checker = HealthChecker()
        self.load_balancer = LoadBalancer()
        self.dns_resolver = DNSResolver()
        self.watch_manager = WatchManager()
        
        # Состояние
        self.running = False
        self.check_task: Optional[asyncio.Task] = None
        
    def define_service(self, name: str, **kwargs) -> ServiceDefinition:
        """Определение сервиса"""
        return self.catalog.define_service(name, **kwargs)
        
    async def register(self, service_name: str,
                        address: str, port: int,
                        tags: List[str] = None,
                        metadata: Dict[str, str] = None,
                        health_check_endpoint: str = None) -> ServiceInstance:
        """Регистрация экземпляра"""
        instance = ServiceInstance(
            instance_id=f"{service_name}-{uuid.uuid4().hex[:8]}",
            service_name=service_name,
            address=address,
            port=port,
            tags=tags or [],
            metadata=metadata or {},
            status=ServiceStatus.UNKNOWN,
            datacenter=self.datacenter
        )
        
        # Создаём health check
        health_check = None
        if health_check_endpoint:
            health_check = HealthCheck(
                check_id=f"check_{instance.instance_id}",
                check_type=HealthCheckType.HTTP,
                endpoint=health_check_endpoint,
                interval_seconds=10
            )
            
        self.catalog.register(instance, health_check)
        
        # Уведомляем
        event = WatchEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type="register",
            service_name=service_name,
            instance_id=instance.instance_id,
            details={"address": address, "port": port}
        )
        await self.watch_manager.notify(event)
        
        return instance
        
    async def deregister(self, instance_id: str) -> bool:
        """Дерегистрация экземпляра"""
        instance = self.catalog.instances.get(instance_id)
        if not instance:
            return False
            
        service_name = instance.service_name
        result = self.catalog.deregister(instance_id)
        
        if result:
            event = WatchEvent(
                event_id=f"evt_{uuid.uuid4().hex[:8]}",
                event_type="deregister",
                service_name=service_name,
                instance_id=instance_id
            )
            await self.watch_manager.notify(event)
            
        return result
        
    def resolve(self, service_name: str,
                 tags: List[str] = None,
                 datacenter: str = None) -> List[Endpoint]:
        """Разрешение сервиса"""
        instances = self.catalog.get_instances(
            service_name,
            tags=tags,
            datacenter=datacenter,
            healthy_only=True
        )
        
        return [
            Endpoint(
                instance_id=i.instance_id,
                address=i.address,
                port=i.port,
                weight=i.weight,
                metadata=i.metadata
            )
            for i in instances
        ]
        
    def resolve_one(self, service_name: str,
                     key: str = None,
                     strategy: LoadBalanceStrategy = None) -> Optional[Endpoint]:
        """Разрешение одного endpoint"""
        endpoints = self.resolve(service_name)
        
        if strategy:
            lb = LoadBalancer(strategy)
            return lb.select(endpoints, key)
        else:
            return self.load_balancer.select(endpoints, key)
            
    def get_dns_records(self, service_name: str,
                         record_type: str = "SRV") -> List[Dict[str, Any]]:
        """DNS записи для сервиса"""
        instances = self.catalog.get_instances(service_name, healthy_only=True)
        
        if record_type == "SRV":
            return self.dns_resolver.get_srv_record(service_name, instances)
        else:
            return self.dns_resolver.get_a_record(service_name, instances)
            
    async def pass_ttl(self, check_id: str) -> bool:
        """Обновление TTL check"""
        check = self.catalog.health_checks.get(check_id)
        if not check:
            return False
            
        check.last_check = datetime.now()
        check.last_status = ServiceStatus.HEALTHY
        
        # Обновляем статус instance
        instance = self.catalog.instances.get(check.instance_id)
        if instance:
            instance.status = ServiceStatus.HEALTHY
            instance.last_heartbeat = datetime.now()
            
        return True
        
    async def run_health_checks(self) -> Dict[str, ServiceStatus]:
        """Запуск проверок здоровья"""
        results = {}
        
        for check_id, check in self.catalog.health_checks.items():
            if check.check_type == HealthCheckType.TTL:
                continue  # TTL проверяется пассивно
                
            status, output = await self.health_checker.check(check)
            
            check.last_check = datetime.now()
            check.last_output = output
            check.last_status = status
            
            # Обновляем счётчики
            if status == ServiceStatus.HEALTHY:
                check.consecutive_successes += 1
                check.consecutive_failures = 0
            else:
                check.consecutive_failures += 1
                check.consecutive_successes = 0
                
            # Обновляем статус instance если порог достигнут
            instance = self.catalog.instances.get(check.instance_id)
            if instance:
                if check.consecutive_successes >= check.success_threshold:
                    old_status = instance.status
                    instance.status = ServiceStatus.HEALTHY
                    
                    if old_status != ServiceStatus.HEALTHY:
                        event = WatchEvent(
                            event_id=f"evt_{uuid.uuid4().hex[:8]}",
                            event_type="health_change",
                            service_name=instance.service_name,
                            instance_id=instance.instance_id,
                            details={
                                "old_status": old_status.value,
                                "new_status": ServiceStatus.HEALTHY.value
                            }
                        )
                        await self.watch_manager.notify(event)
                        
                elif check.consecutive_failures >= check.failure_threshold:
                    old_status = instance.status
                    instance.status = ServiceStatus.UNHEALTHY
                    
                    if old_status == ServiceStatus.HEALTHY:
                        event = WatchEvent(
                            event_id=f"evt_{uuid.uuid4().hex[:8]}",
                            event_type="health_change",
                            service_name=instance.service_name,
                            instance_id=instance.instance_id,
                            details={
                                "old_status": old_status.value,
                                "new_status": ServiceStatus.UNHEALTHY.value
                            }
                        )
                        await self.watch_manager.notify(event)
                        
            results[check_id] = status
            
        return results
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        healthy = sum(1 for i in self.catalog.instances.values()
                      if i.status == ServiceStatus.HEALTHY)
        unhealthy = sum(1 for i in self.catalog.instances.values()
                        if i.status == ServiceStatus.UNHEALTHY)
                        
        return {
            "services": len(self.catalog.services),
            "instances": len(self.catalog.instances),
            "healthy": healthy,
            "unhealthy": unhealthy,
            "health_checks": len(self.catalog.health_checks),
            "datacenters": len(self.catalog.by_datacenter),
            "watch_events": len(self.watch_manager.events)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 97: Service Discovery Platform")
    print("=" * 60)
    
    async def demo():
        platform = ServiceDiscoveryPlatform(datacenter="dc1")
        print("✓ Service Discovery Platform created")
        print(f"  Datacenter: {platform.datacenter}")
        
        # События для наблюдения
        events_received = []
        
        async def on_service_change(event: WatchEvent):
            events_received.append(event)
            
        # Определение сервисов
        print("\n📋 Defining Services...")
        
        services = [
            ("api-gateway", "API Gateway service", ["http", "gateway"]),
            ("user-service", "User management service", ["http", "users"]),
            ("order-service", "Order processing service", ["http", "orders"]),
            ("notification-service", "Notification service", ["http", "notifications"]),
            ("auth-service", "Authentication service", ["http", "auth"])
        ]
        
        for name, desc, tags in services:
            platform.define_service(name, description=desc, tags=tags)
            print(f"  ✓ {name}")
            
            # Подписка на изменения
            platform.watch_manager.watch(name, on_service_change)
            
        # Регистрация экземпляров
        print("\n🔧 Registering Service Instances...")
        
        registered_instances = []
        
        # API Gateway (3 instances)
        for i in range(3):
            inst = await platform.register(
                "api-gateway",
                address=f"10.0.1.{10+i}",
                port=8080,
                tags=["production", "v2"],
                metadata={"version": "2.1.0", "region": "us-east"},
                health_check_endpoint=f"http://10.0.1.{10+i}:8080/health"
            )
            registered_instances.append(inst)
            
        print(f"  ✓ api-gateway: 3 instances")
        
        # User Service (2 instances)
        for i in range(2):
            inst = await platform.register(
                "user-service",
                address=f"10.0.2.{10+i}",
                port=8081,
                tags=["production"],
                metadata={"version": "1.5.0"},
                health_check_endpoint=f"http://10.0.2.{10+i}:8081/health"
            )
            registered_instances.append(inst)
            
        print(f"  ✓ user-service: 2 instances")
        
        # Order Service (3 instances)
        for i in range(3):
            inst = await platform.register(
                "order-service",
                address=f"10.0.3.{10+i}",
                port=8082,
                tags=["production", "critical"],
                metadata={"version": "3.0.0"},
                health_check_endpoint=f"http://10.0.3.{10+i}:8082/health"
            )
            registered_instances.append(inst)
            
        print(f"  ✓ order-service: 3 instances")
        
        # Notification Service (2 instances)
        for i in range(2):
            inst = await platform.register(
                "notification-service",
                address=f"10.0.4.{10+i}",
                port=8083,
                tags=["production"],
                metadata={"version": "1.2.0"}
            )
            registered_instances.append(inst)
            
        print(f"  ✓ notification-service: 2 instances")
        
        # Auth Service (2 instances)
        for i in range(2):
            inst = await platform.register(
                "auth-service",
                address=f"10.0.5.{10+i}",
                port=8084,
                tags=["production", "security"],
                metadata={"version": "2.0.0"},
                health_check_endpoint=f"http://10.0.5.{10+i}:8084/health"
            )
            registered_instances.append(inst)
            
        print(f"  ✓ auth-service: 2 instances")
        
        # Health checks
        print("\n🏥 Running Health Checks...")
        
        for _ in range(3):  # Run multiple rounds
            results = await platform.run_health_checks()
            
        healthy = sum(1 for r in results.values() if r == ServiceStatus.HEALTHY)
        unhealthy = sum(1 for r in results.values() if r != ServiceStatus.HEALTHY)
        
        print(f"  ✓ Completed health checks")
        print(f"    Healthy: {healthy}")
        print(f"    Unhealthy: {unhealthy}")
        
        # Service Resolution
        print("\n🔍 Service Resolution...")
        
        # Resolve all endpoints for a service
        endpoints = platform.resolve("api-gateway")
        print(f"\n  api-gateway endpoints ({len(endpoints)}):")
        for ep in endpoints:
            print(f"    • {ep.address}:{ep.port}")
            
        # Resolve with load balancing
        print("\n  Load Balanced Resolution (Round Robin):")
        for i in range(5):
            ep = platform.resolve_one("api-gateway")
            if ep:
                print(f"    Request {i+1}: {ep.address}:{ep.port}")
                
        # Consistent hash resolution
        print("\n  Consistent Hash Resolution:")
        for user_id in ["user_100", "user_200", "user_100", "user_300", "user_200"]:
            ep = platform.resolve_one(
                "user-service",
                key=user_id,
                strategy=LoadBalanceStrategy.CONSISTENT_HASH
            )
            if ep:
                print(f"    {user_id} → {ep.address}:{ep.port}")
                
        # Filter by tags
        print("\n  Filter by Tags:")
        
        critical_endpoints = platform.resolve("order-service")
        print(f"    order-service (critical): {len(critical_endpoints)} endpoints")
        
        # DNS Resolution
        print("\n📡 DNS Resolution...")
        
        srv_records = platform.get_dns_records("api-gateway", "SRV")
        print(f"\n  SRV Records for api-gateway:")
        for record in srv_records[:3]:
            print(f"    {record['name']} → {record['target']}:{record['port']} (weight: {record['weight']})")
            
        a_records = platform.get_dns_records("user-service", "A")
        print(f"\n  A Records for user-service:")
        for record in a_records[:3]:
            print(f"    {record['name']} → {record['address']} (TTL: {record['ttl']})")
            
        # Deregister an instance
        print("\n🔄 Instance Lifecycle...")
        
        if registered_instances:
            instance_to_remove = registered_instances[0]
            print(f"\n  Deregistering: {instance_to_remove.instance_id}")
            
            await platform.deregister(instance_to_remove.instance_id)
            
            endpoints_after = platform.resolve("api-gateway")
            print(f"  api-gateway endpoints after: {len(endpoints_after)}")
            
        # Watch Events
        print("\n👁 Watch Events:")
        
        print(f"  Total events received: {len(events_received)}")
        
        for event in events_received[:5]:
            print(f"    • [{event.event_type}] {event.service_name}")
            if event.instance_id:
                print(f"      Instance: {event.instance_id[:20]}...")
                
        # Service Catalog
        print("\n📚 Service Catalog:")
        
        for service_name in platform.catalog.services:
            instances = platform.catalog.get_instances(service_name, healthy_only=False)
            healthy = sum(1 for i in instances if i.status == ServiceStatus.HEALTHY)
            
            print(f"\n  {service_name}:")
            print(f"    Instances: {len(instances)} (healthy: {healthy})")
            
            for inst in instances[:2]:
                status_icon = "✅" if inst.status == ServiceStatus.HEALTHY else "❌"
                print(f"    {status_icon} {inst.address}:{inst.port}")
                
        # Statistics
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Services: {stats['services']}")
        print(f"  Instances: {stats['instances']}")
        print(f"  Healthy: {stats['healthy']}")
        print(f"  Unhealthy: {stats['unhealthy']}")
        print(f"  Health Checks: {stats['health_checks']}")
        print(f"  Datacenters: {stats['datacenters']}")
        print(f"  Watch Events: {stats['watch_events']}")
        
        # Dashboard
        print("\n📋 Service Discovery Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │              Service Discovery Overview                     │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Datacenter:    {platform.datacenter:<8}                            │")
        print(f"  │ Services:      {stats['services']:>6}                                │")
        print(f"  │ Instances:     {stats['instances']:>6}                                │")
        print(f"  │ Healthy:       {stats['healthy']:>6}                                │")
        print(f"  │ Unhealthy:     {stats['unhealthy']:>6}                                │")
        print(f"  │ Health Checks: {stats['health_checks']:>6}                                │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Service Discovery Platform initialized!")
    print("=" * 60)
