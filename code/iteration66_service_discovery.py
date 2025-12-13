#!/usr/bin/env python3
"""
Server Init - Iteration 66: Service Discovery & Registry Platform
Обнаружение сервисов и реестр

Функционал:
- Service Registration - регистрация сервисов
- Service Discovery - обнаружение сервисов
- Health Checking - проверка здоровья
- Load Balancing - балансировка нагрузки
- DNS Integration - интеграция с DNS
- Service Mesh - сервисная сетка
- Configuration Distribution - распределение конфигурации
- Watch Mechanism - механизм наблюдения
"""

import json
import asyncio
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
from collections import defaultdict
import uuid
import random


class ServiceStatus(Enum):
    """Статус сервиса"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
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
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"
    WEIGHTED = "weighted"
    IP_HASH = "ip_hash"
    LEAST_LATENCY = "least_latency"


class WatchEventType(Enum):
    """Тип события наблюдения"""
    REGISTERED = "registered"
    DEREGISTERED = "deregistered"
    HEALTH_CHANGED = "health_changed"
    METADATA_UPDATED = "metadata_updated"


@dataclass
class ServiceInstance:
    """Экземпляр сервиса"""
    instance_id: str
    service_name: str
    
    # Адрес
    host: str = ""
    port: int = 0
    
    # Протокол
    protocol: str = "http"
    
    # Статус
    status: ServiceStatus = ServiceStatus.UNKNOWN
    
    # Метаданные
    metadata: Dict[str, str] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    # Здоровье
    last_health_check: Optional[datetime] = None
    health_check_failures: int = 0
    
    # Вес для балансировки
    weight: int = 100
    
    # Метрики
    active_connections: int = 0
    total_requests: int = 0
    avg_latency_ms: float = 0.0
    
    # Время
    registered_at: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)


@dataclass
class Service:
    """Сервис"""
    service_id: str
    name: str
    
    # Описание
    description: str = ""
    version: str = "1.0.0"
    
    # Экземпляры
    instances: Dict[str, ServiceInstance] = field(default_factory=dict)
    
    # Health Check конфигурация
    health_check: Dict[str, Any] = field(default_factory=dict)
    
    # Теги
    tags: List[str] = field(default_factory=list)
    
    # Маршрутизация
    load_balancer: LoadBalancerAlgorithm = LoadBalancerAlgorithm.ROUND_ROBIN
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class HealthCheck:
    """Проверка здоровья"""
    check_id: str
    service_name: str
    instance_id: str
    
    # Тип
    check_type: HealthCheckType = HealthCheckType.HTTP
    
    # Конфигурация
    endpoint: str = "/health"
    interval_seconds: int = 10
    timeout_seconds: int = 5
    
    # Пороги
    healthy_threshold: int = 2
    unhealthy_threshold: int = 3
    
    # Статус
    consecutive_successes: int = 0
    consecutive_failures: int = 0
    last_status: ServiceStatus = ServiceStatus.UNKNOWN


@dataclass
class WatchEvent:
    """Событие наблюдения"""
    event_id: str
    event_type: WatchEventType
    
    # Сервис
    service_name: str = ""
    instance_id: str = ""
    
    # Данные
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Время
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ConfigEntry:
    """Запись конфигурации"""
    key: str
    value: str
    
    # Версия
    version: int = 1
    
    # Метаданные
    content_type: str = "text/plain"
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)


class ServiceRegistry:
    """Реестр сервисов"""
    
    def __init__(self):
        self.services: Dict[str, Service] = {}
        self.instances: Dict[str, ServiceInstance] = {}  # instance_id -> instance
        self.health_checks: Dict[str, HealthCheck] = {}
        
    def register_service(self, name: str, **kwargs) -> Service:
        """Регистрация сервиса"""
        if name not in self.services:
            service = Service(
                service_id=f"svc_{uuid.uuid4().hex[:8]}",
                name=name,
                **kwargs
            )
            self.services[name] = service
            
        return self.services[name]
        
    def register_instance(self, service_name: str, host: str, port: int,
                           **kwargs) -> ServiceInstance:
        """Регистрация экземпляра"""
        # Убеждаемся, что сервис существует
        if service_name not in self.services:
            self.register_service(service_name)
            
        instance = ServiceInstance(
            instance_id=f"inst_{uuid.uuid4().hex[:8]}",
            service_name=service_name,
            host=host,
            port=port,
            status=ServiceStatus.HEALTHY,
            **kwargs
        )
        
        self.services[service_name].instances[instance.instance_id] = instance
        self.instances[instance.instance_id] = instance
        
        return instance
        
    def deregister_instance(self, instance_id: str) -> bool:
        """Отмена регистрации экземпляра"""
        instance = self.instances.get(instance_id)
        
        if not instance:
            return False
            
        service = self.services.get(instance.service_name)
        if service and instance_id in service.instances:
            del service.instances[instance_id]
            
        del self.instances[instance_id]
        
        # Удаляем health check
        check_id = f"hc_{instance_id}"
        if check_id in self.health_checks:
            del self.health_checks[check_id]
            
        return True
        
    def get_service(self, name: str) -> Optional[Service]:
        """Получение сервиса"""
        return self.services.get(name)
        
    def get_healthy_instances(self, service_name: str) -> List[ServiceInstance]:
        """Получение здоровых экземпляров"""
        service = self.services.get(service_name)
        
        if not service:
            return []
            
        return [
            inst for inst in service.instances.values()
            if inst.status == ServiceStatus.HEALTHY
        ]
        
    def update_instance_status(self, instance_id: str, status: ServiceStatus):
        """Обновление статуса экземпляра"""
        instance = self.instances.get(instance_id)
        if instance:
            instance.status = status
            instance.last_seen = datetime.now()


class HealthChecker:
    """Проверщик здоровья"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.running = False
        
    async def check_instance(self, instance: ServiceInstance,
                              check_config: Dict[str, Any]) -> bool:
        """Проверка экземпляра"""
        check_type = check_config.get("type", HealthCheckType.HTTP)
        
        # Симуляция проверки
        if check_type == HealthCheckType.HTTP:
            success = await self._http_check(instance, check_config)
        elif check_type == HealthCheckType.TCP:
            success = await self._tcp_check(instance, check_config)
        elif check_type == HealthCheckType.GRPC:
            success = await self._grpc_check(instance, check_config)
        else:
            success = random.random() > 0.1  # 90% успех
            
        return success
        
    async def _http_check(self, instance: ServiceInstance,
                           config: Dict[str, Any]) -> bool:
        """HTTP проверка"""
        endpoint = config.get("endpoint", "/health")
        timeout = config.get("timeout_seconds", 5)
        
        # Симуляция
        await asyncio.sleep(0.05)
        
        # 95% успех для симуляции
        return random.random() > 0.05
        
    async def _tcp_check(self, instance: ServiceInstance,
                          config: Dict[str, Any]) -> bool:
        """TCP проверка"""
        await asyncio.sleep(0.02)
        return random.random() > 0.02  # 98% успех
        
    async def _grpc_check(self, instance: ServiceInstance,
                           config: Dict[str, Any]) -> bool:
        """gRPC проверка"""
        await asyncio.sleep(0.03)
        return random.random() > 0.05
        
    async def run_health_checks(self):
        """Запуск проверок здоровья"""
        for service in self.registry.services.values():
            check_config = service.health_check or {"type": HealthCheckType.HTTP}
            
            for instance in service.instances.values():
                success = await self.check_instance(instance, check_config)
                
                # Получаем или создаём health check
                check_id = f"hc_{instance.instance_id}"
                
                if check_id not in self.registry.health_checks:
                    self.registry.health_checks[check_id] = HealthCheck(
                        check_id=check_id,
                        service_name=service.name,
                        instance_id=instance.instance_id
                    )
                    
                hc = self.registry.health_checks[check_id]
                
                if success:
                    hc.consecutive_successes += 1
                    hc.consecutive_failures = 0
                    
                    if hc.consecutive_successes >= hc.healthy_threshold:
                        instance.status = ServiceStatus.HEALTHY
                else:
                    hc.consecutive_failures += 1
                    hc.consecutive_successes = 0
                    instance.health_check_failures += 1
                    
                    if hc.consecutive_failures >= hc.unhealthy_threshold:
                        instance.status = ServiceStatus.UNHEALTHY
                        
                instance.last_health_check = datetime.now()


class LoadBalancer:
    """Балансировщик нагрузки"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.round_robin_index: Dict[str, int] = defaultdict(int)
        
    def select_instance(self, service_name: str,
                         algorithm: LoadBalancerAlgorithm = None,
                         client_ip: str = None) -> Optional[ServiceInstance]:
        """Выбор экземпляра"""
        instances = self.registry.get_healthy_instances(service_name)
        
        if not instances:
            return None
            
        service = self.registry.get_service(service_name)
        alg = algorithm or (service.load_balancer if service else LoadBalancerAlgorithm.ROUND_ROBIN)
        
        if alg == LoadBalancerAlgorithm.ROUND_ROBIN:
            return self._round_robin(service_name, instances)
        elif alg == LoadBalancerAlgorithm.LEAST_CONNECTIONS:
            return self._least_connections(instances)
        elif alg == LoadBalancerAlgorithm.RANDOM:
            return random.choice(instances)
        elif alg == LoadBalancerAlgorithm.WEIGHTED:
            return self._weighted(instances)
        elif alg == LoadBalancerAlgorithm.IP_HASH:
            return self._ip_hash(instances, client_ip or "")
        elif alg == LoadBalancerAlgorithm.LEAST_LATENCY:
            return self._least_latency(instances)
            
        return instances[0]
        
    def _round_robin(self, service_name: str,
                      instances: List[ServiceInstance]) -> ServiceInstance:
        """Round Robin"""
        index = self.round_robin_index[service_name] % len(instances)
        self.round_robin_index[service_name] += 1
        return instances[index]
        
    def _least_connections(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Least Connections"""
        return min(instances, key=lambda i: i.active_connections)
        
    def _weighted(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Weighted"""
        total_weight = sum(i.weight for i in instances)
        r = random.uniform(0, total_weight)
        
        cumulative = 0
        for instance in instances:
            cumulative += instance.weight
            if r <= cumulative:
                return instance
                
        return instances[0]
        
    def _ip_hash(self, instances: List[ServiceInstance], client_ip: str) -> ServiceInstance:
        """IP Hash"""
        hash_val = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        index = hash_val % len(instances)
        return instances[index]
        
    def _least_latency(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Least Latency"""
        return min(instances, key=lambda i: i.avg_latency_ms)


class WatchManager:
    """Менеджер наблюдения"""
    
    def __init__(self):
        self.watchers: Dict[str, List[Callable]] = defaultdict(list)
        self.events: List[WatchEvent] = []
        
    def watch(self, service_name: str, callback: Callable):
        """Подписка на изменения"""
        self.watchers[service_name].append(callback)
        
    def unwatch(self, service_name: str, callback: Callable):
        """Отписка от изменений"""
        if callback in self.watchers[service_name]:
            self.watchers[service_name].remove(callback)
            
    async def emit(self, event: WatchEvent):
        """Отправка события"""
        self.events.append(event)
        
        callbacks = self.watchers.get(event.service_name, [])
        callbacks.extend(self.watchers.get("*", []))  # Wildcard watchers
        
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                print(f"Watch callback error: {e}")


class ConfigStore:
    """Хранилище конфигурации"""
    
    def __init__(self):
        self.entries: Dict[str, ConfigEntry] = {}
        self.watchers: Dict[str, List[Callable]] = defaultdict(list)
        
    def put(self, key: str, value: str, content_type: str = "text/plain") -> ConfigEntry:
        """Сохранение конфигурации"""
        if key in self.entries:
            entry = self.entries[key]
            entry.value = value
            entry.version += 1
            entry.modified_at = datetime.now()
        else:
            entry = ConfigEntry(
                key=key,
                value=value,
                content_type=content_type
            )
            self.entries[key] = entry
            
        # Уведомляем watchers
        self._notify(key, entry)
        
        return entry
        
    def get(self, key: str) -> Optional[ConfigEntry]:
        """Получение конфигурации"""
        return self.entries.get(key)
        
    def get_prefix(self, prefix: str) -> List[ConfigEntry]:
        """Получение по префиксу"""
        return [e for k, e in self.entries.items() if k.startswith(prefix)]
        
    def delete(self, key: str) -> bool:
        """Удаление конфигурации"""
        if key in self.entries:
            del self.entries[key]
            return True
        return False
        
    def watch(self, key_pattern: str, callback: Callable):
        """Подписка на изменения"""
        self.watchers[key_pattern].append(callback)
        
    def _notify(self, key: str, entry: ConfigEntry):
        """Уведомление watchers"""
        for pattern, callbacks in self.watchers.items():
            if key.startswith(pattern) or pattern == "*":
                for callback in callbacks:
                    try:
                        callback(key, entry)
                    except Exception as e:
                        print(f"Config watcher error: {e}")


class DNSResolver:
    """DNS резолвер для сервисов"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.cache: Dict[str, tuple] = {}  # domain -> (instances, expires)
        self.ttl = 30  # секунд
        
    def resolve(self, domain: str) -> List[str]:
        """Резолв домена в адреса"""
        # Проверяем кэш
        if domain in self.cache:
            instances, expires = self.cache[domain]
            if datetime.now() < expires:
                return instances
                
        # Извлекаем имя сервиса из домена
        # Формат: service-name.service.local
        parts = domain.split(".")
        if len(parts) >= 2 and parts[1] == "service":
            service_name = parts[0]
            
            instances = self.registry.get_healthy_instances(service_name)
            addresses = [f"{i.host}:{i.port}" for i in instances]
            
            # Кэшируем
            self.cache[domain] = (addresses, datetime.now() + timedelta(seconds=self.ttl))
            
            return addresses
            
        return []
        
    def srv_lookup(self, service_name: str) -> List[Dict[str, Any]]:
        """SRV lookup"""
        instances = self.registry.get_healthy_instances(service_name)
        
        return [
            {
                "priority": 0,
                "weight": inst.weight,
                "port": inst.port,
                "target": inst.host
            }
            for inst in instances
        ]


class ServiceDiscoveryPlatform:
    """Платформа обнаружения сервисов"""
    
    def __init__(self):
        self.registry = ServiceRegistry()
        self.health_checker = HealthChecker(self.registry)
        self.load_balancer = LoadBalancer(self.registry)
        self.watch_manager = WatchManager()
        self.config_store = ConfigStore()
        self.dns_resolver = DNSResolver(self.registry)
        
    def register(self, service_name: str, host: str, port: int,
                  **kwargs) -> ServiceInstance:
        """Регистрация сервиса"""
        instance = self.registry.register_instance(service_name, host, port, **kwargs)
        
        # Событие
        event = WatchEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type=WatchEventType.REGISTERED,
            service_name=service_name,
            instance_id=instance.instance_id,
            data={"host": host, "port": port}
        )
        
        asyncio.create_task(self.watch_manager.emit(event))
        
        return instance
        
    def deregister(self, instance_id: str) -> bool:
        """Отмена регистрации"""
        instance = self.registry.instances.get(instance_id)
        
        if not instance:
            return False
            
        service_name = instance.service_name
        success = self.registry.deregister_instance(instance_id)
        
        if success:
            event = WatchEvent(
                event_id=f"evt_{uuid.uuid4().hex[:8]}",
                event_type=WatchEventType.DEREGISTERED,
                service_name=service_name,
                instance_id=instance_id
            )
            
            asyncio.create_task(self.watch_manager.emit(event))
            
        return success
        
    def discover(self, service_name: str,
                  algorithm: LoadBalancerAlgorithm = None) -> Optional[ServiceInstance]:
        """Обнаружение сервиса"""
        return self.load_balancer.select_instance(service_name, algorithm)
        
    def discover_all(self, service_name: str) -> List[ServiceInstance]:
        """Обнаружение всех экземпляров"""
        return self.registry.get_healthy_instances(service_name)
        
    def resolve(self, domain: str) -> List[str]:
        """DNS резолв"""
        return self.dns_resolver.resolve(domain)
        
    def watch(self, service_name: str, callback: Callable):
        """Подписка на изменения"""
        self.watch_manager.watch(service_name, callback)
        
    async def run_health_checks(self):
        """Запуск проверок здоровья"""
        await self.health_checker.run_health_checks()
        
    def set_config(self, key: str, value: str) -> ConfigEntry:
        """Установка конфигурации"""
        return self.config_store.put(key, value)
        
    def get_config(self, key: str) -> Optional[str]:
        """Получение конфигурации"""
        entry = self.config_store.get(key)
        return entry.value if entry else None
        
    def get_stats(self) -> Dict[str, Any]:
        """Статистика платформы"""
        total_instances = len(self.registry.instances)
        healthy = len([i for i in self.registry.instances.values() if i.status == ServiceStatus.HEALTHY])
        
        return {
            "services": len(self.registry.services),
            "instances": {
                "total": total_instances,
                "healthy": healthy,
                "unhealthy": total_instances - healthy
            },
            "health_checks": len(self.registry.health_checks),
            "config_entries": len(self.config_store.entries),
            "watchers": sum(len(w) for w in self.watch_manager.watchers.values()),
            "events": len(self.watch_manager.events)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 66: Service Discovery Platform")
    print("=" * 60)
    
    async def demo():
        platform = ServiceDiscoveryPlatform()
        print("✓ Service Discovery Platform created")
        
        # Watch callback
        events_received = []
        
        def on_service_change(event: WatchEvent):
            events_received.append(event)
            print(f"  📢 Event: {event.event_type.value} - {event.service_name}/{event.instance_id}")
            
        # Подписка на изменения
        platform.watch("*", on_service_change)
        
        # Регистрация сервисов
        print("\n📝 Registering services...")
        
        # API Gateway
        for i in range(3):
            instance = platform.register(
                service_name="api-gateway",
                host=f"10.0.1.{10 + i}",
                port=8080,
                tags=["production", "frontend"],
                metadata={"version": "2.1.0", "region": "us-east-1"},
                weight=100 if i < 2 else 50  # Третий с меньшим весом
            )
            print(f"  ✓ api-gateway: {instance.host}:{instance.port}")
            
        # User Service
        for i in range(2):
            instance = platform.register(
                service_name="user-service",
                host=f"10.0.2.{10 + i}",
                port=8081,
                tags=["production", "backend"],
                metadata={"version": "1.5.0"}
            )
            print(f"  ✓ user-service: {instance.host}:{instance.port}")
            
        # Payment Service
        instance = platform.register(
            service_name="payment-service",
            host="10.0.3.10",
            port=8082,
            tags=["production", "critical"],
            metadata={"version": "3.0.0"}
        )
        print(f"  ✓ payment-service: {instance.host}:{instance.port}")
        
        await asyncio.sleep(0.1)  # Даём время events
        
        # Конфигурация сервисов
        print("\n⚙️ Setting service configurations...")
        
        platform.set_config("services/api-gateway/timeout", "30s")
        platform.set_config("services/api-gateway/rate-limit", "1000")
        platform.set_config("services/user-service/cache-ttl", "60")
        platform.set_config("global/log-level", "info")
        
        print(f"  ✓ Timeout: {platform.get_config('services/api-gateway/timeout')}")
        print(f"  ✓ Rate limit: {platform.get_config('services/api-gateway/rate-limit')}")
        
        # Health Checks
        print("\n🏥 Running health checks...")
        await platform.run_health_checks()
        
        healthy_count = len([i for i in platform.registry.instances.values() 
                            if i.status == ServiceStatus.HEALTHY])
        print(f"  ✓ Healthy instances: {healthy_count}/{len(platform.registry.instances)}")
        
        # Service Discovery
        print("\n🔍 Service Discovery:")
        
        # Round Robin
        print("\n  Round Robin (api-gateway):")
        for i in range(5):
            instance = platform.discover("api-gateway", LoadBalancerAlgorithm.ROUND_ROBIN)
            if instance:
                print(f"    Request {i+1}: {instance.host}:{instance.port}")
                
        # Least Connections
        print("\n  Least Connections (user-service):")
        instances = platform.discover_all("user-service")
        
        # Симуляция нагрузки
        if instances:
            instances[0].active_connections = 10
            instances[1].active_connections = 5
            
        for i in range(3):
            instance = platform.discover("user-service", LoadBalancerAlgorithm.LEAST_CONNECTIONS)
            if instance:
                print(f"    Request {i+1}: {instance.host}:{instance.port} (connections: {instance.active_connections})")
                instance.active_connections += 1
                
        # Weighted
        print("\n  Weighted (api-gateway):")
        weight_distribution = defaultdict(int)
        for _ in range(100):
            instance = platform.discover("api-gateway", LoadBalancerAlgorithm.WEIGHTED)
            if instance:
                weight_distribution[instance.host] += 1
                
        for host, count in weight_distribution.items():
            print(f"    {host}: {count}%")
            
        # DNS Resolution
        print("\n🌐 DNS Resolution:")
        
        addresses = platform.resolve("api-gateway.service.local")
        print(f"  api-gateway.service.local -> {addresses}")
        
        srv_records = platform.dns_resolver.srv_lookup("user-service")
        print(f"  user-service SRV records: {len(srv_records)}")
        for srv in srv_records:
            print(f"    {srv['target']}:{srv['port']} (weight: {srv['weight']})")
            
        # Deregistration
        print("\n🗑️ Deregistering instance...")
        
        # Находим один экземпляр
        api_instances = platform.discover_all("api-gateway")
        if api_instances:
            instance_to_remove = api_instances[0]
            platform.deregister(instance_to_remove.instance_id)
            print(f"  ✓ Deregistered: {instance_to_remove.host}:{instance_to_remove.port}")
            
        await asyncio.sleep(0.1)
        
        # Service Info
        print("\n📊 Service Information:")
        
        for service_name in ["api-gateway", "user-service", "payment-service"]:
            service = platform.registry.get_service(service_name)
            if service:
                healthy = len([i for i in service.instances.values() 
                              if i.status == ServiceStatus.HEALTHY])
                print(f"  {service_name}:")
                print(f"    Instances: {len(service.instances)} (healthy: {healthy})")
                print(f"    Load Balancer: {service.load_balancer.value}")
                
        # Watch Events
        print(f"\n📢 Events received: {len(events_received)}")
        for event in events_received[-5:]:
            print(f"  [{event.event_type.value}] {event.service_name}")
            
        # Config entries
        print("\n⚙️ Configuration Entries:")
        for entry in platform.config_store.entries.values():
            print(f"  {entry.key} = {entry.value} (v{entry.version})")
            
        # Platform Statistics
        print("\n📈 Platform Statistics:")
        stats = platform.get_stats()
        print(f"  Services: {stats['services']}")
        print(f"  Instances: {stats['instances']['total']} (healthy: {stats['instances']['healthy']})")
        print(f"  Health Checks: {stats['health_checks']}")
        print(f"  Config Entries: {stats['config_entries']}")
        print(f"  Active Watchers: {stats['watchers']}")
        print(f"  Total Events: {stats['events']}")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Service Discovery Platform initialized!")
    print("=" * 60)
