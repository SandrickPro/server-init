#!/usr/bin/env python3
"""
Server Init - Iteration 261: Dependency Injection Container Platform
Платформа контейнера внедрения зависимостей

Функционал:
- Service Registration - регистрация сервисов
- Lifetime Management - управление временем жизни
- Constructor Injection - внедрение через конструктор
- Property Injection - внедрение через свойства
- Factory Support - поддержка фабрик
- Scoped Services - сервисы с областью видимости
- Circular Dependency Detection - обнаружение циклических зависимостей
- Lazy Loading - отложенная загрузка
"""

import asyncio
import random
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Type, Callable, Set
from enum import Enum
import uuid
import inspect


class ServiceLifetime(Enum):
    """Время жизни сервиса"""
    TRANSIENT = "transient"  # New instance every time
    SCOPED = "scoped"  # One instance per scope
    SINGLETON = "singleton"  # One instance for entire app


class InjectionType(Enum):
    """Тип внедрения"""
    CONSTRUCTOR = "constructor"
    PROPERTY = "property"
    METHOD = "method"


class RegistrationType(Enum):
    """Тип регистрации"""
    TYPE = "type"
    INSTANCE = "instance"
    FACTORY = "factory"


@dataclass
class ServiceDescriptor:
    """Дескриптор сервиса"""
    descriptor_id: str
    service_type: str  # Interface/abstract type name
    implementation_type: str  # Concrete type name
    
    # Lifetime
    lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT
    
    # Registration
    registration_type: RegistrationType = RegistrationType.TYPE
    
    # Factory
    factory: Optional[Callable] = None
    
    # Instance (for singleton with instance registration)
    instance: Any = None
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    
    # Metadata
    registered_at: datetime = field(default_factory=datetime.now)


@dataclass
class Scope:
    """Область видимости"""
    scope_id: str
    name: str
    
    # Instances
    instances: Dict[str, Any] = field(default_factory=dict)
    
    # Parent scope
    parent_scope_id: Optional[str] = None
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    disposed: bool = False


@dataclass
class ResolveResult:
    """Результат разрешения зависимости"""
    result_id: str
    service_type: str
    
    # Instance
    instance: Any = None
    
    # Info
    from_cache: bool = False
    lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT
    
    # Resolution chain
    resolution_chain: List[str] = field(default_factory=list)
    
    # Timing
    resolved_at: datetime = field(default_factory=datetime.now)
    resolution_time_ms: float = 0


@dataclass
class ContainerMetrics:
    """Метрики контейнера"""
    # Registrations
    services_registered: int = 0
    transient_count: int = 0
    scoped_count: int = 0
    singleton_count: int = 0
    
    # Resolutions
    total_resolutions: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    
    # Scopes
    active_scopes: int = 0
    total_scopes_created: int = 0


# Sample service interfaces and implementations for demo
class ILogger:
    def log(self, message: str): pass


class IDatabase:
    def query(self, sql: str): pass


class ICache:
    def get(self, key: str): pass
    def set(self, key: str, value: Any): pass


class ConsoleLogger(ILogger):
    def __init__(self):
        self.instance_id = uuid.uuid4().hex[:8]
        
    def log(self, message: str):
        return f"[{self.instance_id}] {message}"


class PostgresDatabase(IDatabase):
    def __init__(self, logger: ILogger = None):
        self.instance_id = uuid.uuid4().hex[:8]
        self.logger = logger
        
    def query(self, sql: str):
        return f"[{self.instance_id}] Executing: {sql}"


class RedisCache(ICache):
    def __init__(self, logger: ILogger = None):
        self.instance_id = uuid.uuid4().hex[:8]
        self.logger = logger
        self.data = {}
        
    def get(self, key: str):
        return self.data.get(key)
        
    def set(self, key: str, value: Any):
        self.data[key] = value


class UserService:
    def __init__(self, database: IDatabase, cache: ICache, logger: ILogger):
        self.instance_id = uuid.uuid4().hex[:8]
        self.database = database
        self.cache = cache
        self.logger = logger
        
    def get_user(self, user_id: str):
        return f"[{self.instance_id}] Getting user {user_id}"


class DIContainer:
    """Контейнер внедрения зависимостей"""
    
    def __init__(self):
        self.descriptors: Dict[str, ServiceDescriptor] = {}
        self.singletons: Dict[str, Any] = {}
        self.scopes: Dict[str, Scope] = {}
        self.metrics = ContainerMetrics()
        self._resolution_stack: Set[str] = set()
        
    def register(self, service_type: str, implementation: Any,
                lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
                dependencies: List[str] = None) -> ServiceDescriptor:
        """Регистрация сервиса"""
        # Determine registration type
        if callable(implementation) and not isinstance(implementation, type):
            reg_type = RegistrationType.FACTORY
        elif isinstance(implementation, type):
            reg_type = RegistrationType.TYPE
        else:
            reg_type = RegistrationType.INSTANCE
            
        impl_name = implementation.__name__ if isinstance(implementation, type) else type(implementation).__name__
        
        descriptor = ServiceDescriptor(
            descriptor_id=f"desc_{uuid.uuid4().hex[:8]}",
            service_type=service_type,
            implementation_type=impl_name,
            lifetime=lifetime,
            registration_type=reg_type,
            factory=implementation if reg_type == RegistrationType.FACTORY else None,
            instance=implementation if reg_type == RegistrationType.INSTANCE else None,
            dependencies=dependencies or []
        )
        
        # Auto-detect dependencies from constructor
        if reg_type == RegistrationType.TYPE:
            try:
                sig = inspect.signature(implementation.__init__)
                for param_name, param in sig.parameters.items():
                    if param_name != 'self' and param.annotation != inspect.Parameter.empty:
                        dep_type = param.annotation.__name__
                        if dep_type not in descriptor.dependencies:
                            descriptor.dependencies.append(dep_type)
            except (ValueError, TypeError):
                pass
                
        self.descriptors[service_type] = descriptor
        
        # Update metrics
        self.metrics.services_registered += 1
        if lifetime == ServiceLifetime.TRANSIENT:
            self.metrics.transient_count += 1
        elif lifetime == ServiceLifetime.SCOPED:
            self.metrics.scoped_count += 1
        elif lifetime == ServiceLifetime.SINGLETON:
            self.metrics.singleton_count += 1
            
        return descriptor
        
    def register_singleton(self, service_type: str, implementation: Any,
                          dependencies: List[str] = None) -> ServiceDescriptor:
        """Регистрация singleton"""
        return self.register(service_type, implementation, ServiceLifetime.SINGLETON, dependencies)
        
    def register_scoped(self, service_type: str, implementation: Any,
                       dependencies: List[str] = None) -> ServiceDescriptor:
        """Регистрация scoped"""
        return self.register(service_type, implementation, ServiceLifetime.SCOPED, dependencies)
        
    def register_transient(self, service_type: str, implementation: Any,
                          dependencies: List[str] = None) -> ServiceDescriptor:
        """Регистрация transient"""
        return self.register(service_type, implementation, ServiceLifetime.TRANSIENT, dependencies)
        
    def create_scope(self, name: str = None, parent_scope_id: str = None) -> Scope:
        """Создание области видимости"""
        scope = Scope(
            scope_id=f"scope_{uuid.uuid4().hex[:8]}",
            name=name or f"scope_{uuid.uuid4().hex[:4]}",
            parent_scope_id=parent_scope_id
        )
        
        self.scopes[scope.scope_id] = scope
        self.metrics.active_scopes += 1
        self.metrics.total_scopes_created += 1
        
        return scope
        
    def dispose_scope(self, scope_id: str):
        """Освобождение области видимости"""
        scope = self.scopes.get(scope_id)
        if scope:
            scope.disposed = True
            scope.instances.clear()
            self.metrics.active_scopes -= 1
            
    def _check_circular_dependency(self, service_type: str) -> bool:
        """Проверка циклической зависимости"""
        if service_type in self._resolution_stack:
            return True
        return False
        
    def _create_instance(self, descriptor: ServiceDescriptor,
                        scope: Scope = None) -> Any:
        """Создание экземпляра"""
        # Resolve dependencies first
        resolved_deps = {}
        for dep_type in descriptor.dependencies:
            dep_instance = self.resolve(dep_type, scope)
            if dep_instance:
                resolved_deps[dep_type] = dep_instance.instance
                
        # Create instance based on registration type
        if descriptor.registration_type == RegistrationType.INSTANCE:
            return descriptor.instance
            
        elif descriptor.registration_type == RegistrationType.FACTORY:
            return descriptor.factory(**resolved_deps)
            
        else:
            # TYPE registration
            # Get the actual type to instantiate
            impl_type = None
            for name, obj in globals().items():
                if name == descriptor.implementation_type and isinstance(obj, type):
                    impl_type = obj
                    break
                    
            if impl_type:
                # Map dependencies to constructor parameters
                sig = inspect.signature(impl_type.__init__)
                kwargs = {}
                for param_name, param in sig.parameters.items():
                    if param_name == 'self':
                        continue
                    if param.annotation != inspect.Parameter.empty:
                        dep_type = param.annotation.__name__
                        if dep_type in resolved_deps:
                            kwargs[param_name] = resolved_deps[dep_type]
                            
                return impl_type(**kwargs)
                
        return None
        
    def resolve(self, service_type: str, scope: Scope = None) -> ResolveResult:
        """Разрешение зависимости"""
        start_time = datetime.now()
        
        result = ResolveResult(
            result_id=f"res_{uuid.uuid4().hex[:8]}",
            service_type=service_type
        )
        
        descriptor = self.descriptors.get(service_type)
        if not descriptor:
            return result
            
        result.lifetime = descriptor.lifetime
        result.resolution_chain = list(self._resolution_stack) + [service_type]
        
        # Check for circular dependency
        if self._check_circular_dependency(service_type):
            raise Exception(f"Circular dependency detected: {' -> '.join(result.resolution_chain)}")
            
        self._resolution_stack.add(service_type)
        
        try:
            self.metrics.total_resolutions += 1
            
            # Check caches based on lifetime
            if descriptor.lifetime == ServiceLifetime.SINGLETON:
                if service_type in self.singletons:
                    result.instance = self.singletons[service_type]
                    result.from_cache = True
                    self.metrics.cache_hits += 1
                else:
                    result.instance = self._create_instance(descriptor, scope)
                    self.singletons[service_type] = result.instance
                    self.metrics.cache_misses += 1
                    
            elif descriptor.lifetime == ServiceLifetime.SCOPED:
                if scope and service_type in scope.instances:
                    result.instance = scope.instances[service_type]
                    result.from_cache = True
                    self.metrics.cache_hits += 1
                else:
                    result.instance = self._create_instance(descriptor, scope)
                    if scope:
                        scope.instances[service_type] = result.instance
                    self.metrics.cache_misses += 1
                    
            else:  # TRANSIENT
                result.instance = self._create_instance(descriptor, scope)
                self.metrics.cache_misses += 1
                
        finally:
            self._resolution_stack.discard(service_type)
            
        result.resolution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        return result
        
    def get_all_registered(self) -> List[ServiceDescriptor]:
        """Получение всех зарегистрированных сервисов"""
        return list(self.descriptors.values())
        
    def is_registered(self, service_type: str) -> bool:
        """Проверка регистрации"""
        return service_type in self.descriptors
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика контейнера"""
        return {
            "services_registered": self.metrics.services_registered,
            "transient_count": self.metrics.transient_count,
            "scoped_count": self.metrics.scoped_count,
            "singleton_count": self.metrics.singleton_count,
            "total_resolutions": self.metrics.total_resolutions,
            "cache_hits": self.metrics.cache_hits,
            "cache_misses": self.metrics.cache_misses,
            "cache_hit_rate": (self.metrics.cache_hits / max(1, self.metrics.total_resolutions)) * 100,
            "active_scopes": self.metrics.active_scopes
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 261: Dependency Injection Container")
    print("=" * 60)
    
    container = DIContainer()
    print("✓ DI Container created")
    
    # Register services
    print("\n📦 Registering Services...")
    
    # Register Logger as Singleton
    container.register_singleton("ILogger", ConsoleLogger)
    print("  📦 ILogger -> ConsoleLogger (Singleton)")
    
    # Register Database as Scoped
    container.register_scoped("IDatabase", PostgresDatabase, ["ILogger"])
    print("  📦 IDatabase -> PostgresDatabase (Scoped)")
    
    # Register Cache as Singleton
    container.register_singleton("ICache", RedisCache, ["ILogger"])
    print("  📦 ICache -> RedisCache (Singleton)")
    
    # Register UserService as Transient
    container.register_transient("UserService", UserService, ["IDatabase", "ICache", "ILogger"])
    print("  📦 UserService -> UserService (Transient)")
    
    # Display registrations
    print("\n📋 Registered Services:")
    
    print("\n  ┌─────────────────────┬─────────────────────┬─────────────┬───────────────────┐")
    print("  │ Service Type        │ Implementation      │ Lifetime    │ Dependencies      │")
    print("  ├─────────────────────┼─────────────────────┼─────────────┼───────────────────┤")
    
    for desc in container.get_all_registered():
        svc_type = desc.service_type[:19].ljust(19)
        impl = desc.implementation_type[:19].ljust(19)
        lifetime = desc.lifetime.value[:11].ljust(11)
        deps = ", ".join(desc.dependencies[:2]) if desc.dependencies else "none"
        deps = deps[:17].ljust(17)
        
        print(f"  │ {svc_type} │ {impl} │ {lifetime} │ {deps} │")
        
    print("  └─────────────────────┴─────────────────────┴─────────────┴───────────────────┘")
    
    # Resolve services
    print("\n🔧 Resolving Services...")
    
    # Resolve Logger (singleton)
    logger1 = container.resolve("ILogger")
    logger2 = container.resolve("ILogger")
    print(f"\n  ILogger (1st): instance_id={logger1.instance.instance_id}, from_cache={logger1.from_cache}")
    print(f"  ILogger (2nd): instance_id={logger2.instance.instance_id}, from_cache={logger2.from_cache}")
    print(f"  Same instance: {logger1.instance.instance_id == logger2.instance.instance_id}")
    
    # Create scope and resolve scoped services
    print("\n📦 Creating Scope...")
    
    scope1 = container.create_scope("request-1")
    print(f"  Created scope: {scope1.name}")
    
    # Resolve Database in scope
    db1 = container.resolve("IDatabase", scope1)
    db2 = container.resolve("IDatabase", scope1)
    print(f"\n  IDatabase (scope1, 1st): instance_id={db1.instance.instance_id}")
    print(f"  IDatabase (scope1, 2nd): instance_id={db2.instance.instance_id}")
    print(f"  Same instance: {db1.instance.instance_id == db2.instance.instance_id}")
    
    # Create another scope
    scope2 = container.create_scope("request-2")
    db3 = container.resolve("IDatabase", scope2)
    print(f"\n  IDatabase (scope2): instance_id={db3.instance.instance_id}")
    print(f"  Different from scope1: {db1.instance.instance_id != db3.instance.instance_id}")
    
    # Resolve transient
    print("\n🔧 Transient Resolution:")
    
    user1 = container.resolve("UserService", scope1)
    user2 = container.resolve("UserService", scope1)
    print(f"  UserService (1st): instance_id={user1.instance.instance_id}")
    print(f"  UserService (2nd): instance_id={user2.instance.instance_id}")
    print(f"  Different instances: {user1.instance.instance_id != user2.instance.instance_id}")
    
    # Resolution chain
    print("\n🔗 Resolution Chain:")
    
    for svc_type in ["ILogger", "ICache", "UserService"]:
        result = container.resolve(svc_type, scope1)
        print(f"  {svc_type}: {' -> '.join(result.resolution_chain)}")
        
    # Lifetime distribution
    print("\n📊 Lifetime Distribution:")
    
    for lifetime in ServiceLifetime:
        count = sum(1 for d in container.descriptors.values() if d.lifetime == lifetime)
        bar = "█" * count + "░" * (5 - count)
        print(f"  {lifetime.value:12s} [{bar}] {count}")
        
    # Scope management
    print("\n📦 Scope Management:")
    
    for scope_id, scope in container.scopes.items():
        print(f"  {scope.name}:")
        print(f"    Instances: {len(scope.instances)}")
        print(f"    Disposed: {scope.disposed}")
        
    # Dispose scope
    print("\n🗑️ Disposing Scope...")
    
    container.dispose_scope(scope1.scope_id)
    print(f"  {scope1.name} disposed")
    
    # Statistics
    print("\n📊 Container Statistics:")
    
    stats = container.get_statistics()
    
    print(f"\n  Services Registered: {stats['services_registered']}")
    print(f"    Transient: {stats['transient_count']}")
    print(f"    Scoped: {stats['scoped_count']}")
    print(f"    Singleton: {stats['singleton_count']}")
    
    print(f"\n  Total Resolutions: {stats['total_resolutions']}")
    print(f"    Cache Hits: {stats['cache_hits']}")
    print(f"    Cache Misses: {stats['cache_misses']}")
    print(f"    Cache Hit Rate: {stats['cache_hit_rate']:.1f}%")
    
    print(f"\n  Active Scopes: {stats['active_scopes']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│              Dependency Injection Container Dashboard               │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Services Registered:           {stats['services_registered']:>12}                        │")
    print(f"│ Total Resolutions:             {stats['total_resolutions']:>12}                        │")
    print(f"│ Cache Hit Rate:                {stats['cache_hit_rate']:>11.1f}%                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Singletons:                    {stats['singleton_count']:>12}                        │")
    print(f"│ Scoped:                        {stats['scoped_count']:>12}                        │")
    print(f"│ Transient:                     {stats['transient_count']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Active Scopes:                 {stats['active_scopes']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Dependency Injection Container Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
