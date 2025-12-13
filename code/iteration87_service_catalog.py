#!/usr/bin/env python3
"""
Server Init - Iteration 87: Service Catalog Platform
Платформа каталога сервисов

Функционал:
- Service Registry - реестр сервисов
- Service Templates - шаблоны сервисов
- Self-Service Provisioning - самообслуживание
- Service Dependencies - зависимости сервисов
- Service Health - здоровье сервисов
- Service Documentation - документация сервисов
- Service Versioning - версионирование
- Service Metrics - метрики сервисов
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Tuple
from enum import Enum
from collections import defaultdict
import uuid
import random


class ServiceType(Enum):
    """Тип сервиса"""
    API = "api"
    WEB = "web"
    WORKER = "worker"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    GATEWAY = "gateway"
    SCHEDULER = "scheduler"
    MONITORING = "monitoring"
    CUSTOM = "custom"


class ServiceStatus(Enum):
    """Статус сервиса"""
    ACTIVE = "active"
    DEGRADED = "degraded"
    DOWN = "down"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"
    DEVELOPMENT = "development"


class HealthStatus(Enum):
    """Статус здоровья"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class ProvisioningStatus(Enum):
    """Статус провизионирования"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ServiceOwner:
    """Владелец сервиса"""
    team: str = ""
    email: str = ""
    slack_channel: str = ""
    on_call_schedule: str = ""
    escalation_policy: str = ""


@dataclass
class ServiceEndpoint:
    """Эндпоинт сервиса"""
    endpoint_id: str
    name: str = ""
    url: str = ""
    environment: str = ""  # production, staging, dev
    protocol: str = "https"
    port: int = 443
    path: str = "/"
    health_check_path: str = "/health"
    is_public: bool = False


@dataclass
class ServiceDependency:
    """Зависимость сервиса"""
    dependency_id: str
    service_id: str = ""  # Зависимый сервис
    dependency_type: str = "runtime"  # runtime, build, optional
    description: str = ""
    is_critical: bool = True


@dataclass 
class ServiceSLA:
    """SLA сервиса"""
    availability_target: float = 99.9  # %
    latency_p50_ms: int = 100
    latency_p99_ms: int = 500
    error_rate_threshold: float = 0.1  # %
    support_hours: str = "24x7"


@dataclass
class ServiceMetrics:
    """Метрики сервиса"""
    requests_per_second: float = 0.0
    latency_p50_ms: float = 0.0
    latency_p99_ms: float = 0.0
    error_rate: float = 0.0
    availability: float = 100.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    instance_count: int = 0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class ServiceVersion:
    """Версия сервиса"""
    version: str = ""
    release_date: datetime = field(default_factory=datetime.now)
    changelog: str = ""
    git_commit: str = ""
    docker_image: str = ""
    is_current: bool = False


@dataclass
class Service:
    """Сервис"""
    service_id: str
    name: str = ""
    display_name: str = ""
    description: str = ""
    
    # Тип и статус
    service_type: ServiceType = ServiceType.API
    status: ServiceStatus = ServiceStatus.ACTIVE
    
    # Владелец
    owner: Optional[ServiceOwner] = None
    
    # Эндпоинты
    endpoints: List[ServiceEndpoint] = field(default_factory=list)
    
    # Зависимости
    dependencies: List[ServiceDependency] = field(default_factory=list)
    
    # SLA
    sla: Optional[ServiceSLA] = None
    
    # Метрики
    metrics: Optional[ServiceMetrics] = None
    health: HealthStatus = HealthStatus.UNKNOWN
    
    # Версионирование
    current_version: str = ""
    versions: List[ServiceVersion] = field(default_factory=list)
    
    # Документация
    documentation_url: str = ""
    runbook_url: str = ""
    api_spec_url: str = ""
    
    # Технический стек
    language: str = ""
    framework: str = ""
    infrastructure: str = ""  # kubernetes, ecs, lambda
    
    # Теги
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Критичность
    tier: int = 3  # 1=critical, 2=important, 3=standard


@dataclass
class ServiceTemplate:
    """Шаблон сервиса"""
    template_id: str
    name: str = ""
    description: str = ""
    
    # Тип создаваемого сервиса
    service_type: ServiceType = ServiceType.API
    
    # Конфигурация по умолчанию
    default_config: Dict[str, Any] = field(default_factory=dict)
    
    # Требуемые параметры
    required_params: List[str] = field(default_factory=list)
    
    # Ресурсы
    default_resources: Dict[str, Any] = field(default_factory=dict)
    # {"cpu": "500m", "memory": "512Mi", "replicas": 2}
    
    # Инфраструктура
    infrastructure_template: str = ""  # Terraform, CloudFormation, etc.
    
    # Теги по умолчанию
    default_tags: Dict[str, str] = field(default_factory=dict)
    
    # Время создания
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ProvisioningRequest:
    """Запрос на провизионирование"""
    request_id: str
    
    # Шаблон
    template_id: str = ""
    
    # Параметры
    service_name: str = ""
    environment: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Статус
    status: ProvisioningStatus = ProvisioningStatus.PENDING
    
    # Созданный сервис
    created_service_id: Optional[str] = None
    
    # Requestor
    requestor: str = ""
    
    # Логи
    logs: List[str] = field(default_factory=list)
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class ServiceRegistry:
    """Реестр сервисов"""
    
    def __init__(self):
        self.services: Dict[str, Service] = {}
        
    def register(self, service: Service):
        """Регистрация сервиса"""
        self.services[service.service_id] = service
        
    def unregister(self, service_id: str):
        """Отмена регистрации"""
        if service_id in self.services:
            del self.services[service_id]
            
    def get(self, service_id: str) -> Optional[Service]:
        """Получение сервиса"""
        return self.services.get(service_id)
        
    def find_by_name(self, name: str) -> Optional[Service]:
        """Поиск по имени"""
        for service in self.services.values():
            if service.name == name or service.display_name == name:
                return service
        return None
        
    def find_by_type(self, service_type: ServiceType) -> List[Service]:
        """Поиск по типу"""
        return [s for s in self.services.values() if s.service_type == service_type]
        
    def find_by_tag(self, tag_key: str, tag_value: str = None) -> List[Service]:
        """Поиск по тегу"""
        results = []
        for service in self.services.values():
            if tag_key in service.tags:
                if tag_value is None or service.tags[tag_key] == tag_value:
                    results.append(service)
        return results
        
    def search(self, query: str) -> List[Service]:
        """Полнотекстовый поиск"""
        query = query.lower()
        results = []
        
        for service in self.services.values():
            if (query in service.name.lower() or
                query in service.display_name.lower() or
                query in service.description.lower()):
                results.append(service)
                
        return results


class DependencyManager:
    """Менеджер зависимостей"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        
    def get_dependencies(self, service_id: str) -> List[Service]:
        """Получение зависимостей сервиса"""
        service = self.registry.get(service_id)
        if not service:
            return []
            
        deps = []
        for dep in service.dependencies:
            dep_service = self.registry.get(dep.service_id)
            if dep_service:
                deps.append(dep_service)
                
        return deps
        
    def get_dependents(self, service_id: str) -> List[Service]:
        """Кто зависит от этого сервиса"""
        dependents = []
        
        for service in self.registry.services.values():
            for dep in service.dependencies:
                if dep.service_id == service_id:
                    dependents.append(service)
                    break
                    
        return dependents
        
    def get_dependency_tree(self, service_id: str, depth: int = 5, 
                             visited: Set[str] = None) -> Dict[str, Any]:
        """Дерево зависимостей"""
        if visited is None:
            visited = set()
            
        if service_id in visited or depth <= 0:
            return {"circular": True}
            
        visited.add(service_id)
        
        service = self.registry.get(service_id)
        if not service:
            return {}
            
        tree = {
            "service_id": service_id,
            "name": service.name,
            "status": service.status.value,
            "health": service.health.value,
            "dependencies": []
        }
        
        for dep in service.dependencies:
            subtree = self.get_dependency_tree(dep.service_id, depth - 1, visited.copy())
            if subtree:
                subtree["dependency_type"] = dep.dependency_type
                subtree["is_critical"] = dep.is_critical
                tree["dependencies"].append(subtree)
                
        return tree
        
    def check_circular(self, service_id: str, new_dep_id: str) -> bool:
        """Проверка на циклические зависимости"""
        visited = set()
        
        def dfs(current_id: str) -> bool:
            if current_id == service_id:
                return True
            if current_id in visited:
                return False
                
            visited.add(current_id)
            service = self.registry.get(current_id)
            
            if service:
                for dep in service.dependencies:
                    if dfs(dep.service_id):
                        return True
                        
            return False
            
        return dfs(new_dep_id)
        
    def impact_analysis(self, service_id: str) -> Dict[str, Any]:
        """Анализ влияния (что затронет если сервис упадёт)"""
        service = self.registry.get(service_id)
        if not service:
            return {}
            
        # Все зависимые сервисы (рекурсивно)
        affected = set()
        to_check = [service_id]
        
        while to_check:
            current = to_check.pop()
            dependents = self.get_dependents(current)
            
            for dep in dependents:
                if dep.service_id not in affected:
                    affected.add(dep.service_id)
                    to_check.append(dep.service_id)
                    
        # Категоризация по критичности
        critical = []
        important = []
        standard = []
        
        for affected_id in affected:
            affected_service = self.registry.get(affected_id)
            if affected_service:
                if affected_service.tier == 1:
                    critical.append(affected_service)
                elif affected_service.tier == 2:
                    important.append(affected_service)
                else:
                    standard.append(affected_service)
                    
        return {
            "source_service": service.name,
            "total_affected": len(affected),
            "critical_services": [s.name for s in critical],
            "important_services": [s.name for s in important],
            "standard_services": [s.name for s in standard]
        }


class HealthChecker:
    """Проверка здоровья сервисов"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        
    async def check_service(self, service_id: str) -> HealthStatus:
        """Проверка здоровья сервиса"""
        service = self.registry.get(service_id)
        if not service:
            return HealthStatus.UNKNOWN
            
        # Симуляция проверки
        health_check_result = random.random()
        
        if health_check_result > 0.9:
            health = HealthStatus.UNHEALTHY
        elif health_check_result > 0.8:
            health = HealthStatus.DEGRADED
        else:
            health = HealthStatus.HEALTHY
            
        service.health = health
        service.updated_at = datetime.now()
        
        return health
        
    async def check_all(self) -> Dict[str, HealthStatus]:
        """Проверка всех сервисов"""
        results = {}
        
        for service_id in self.registry.services:
            results[service_id] = await self.check_service(service_id)
            
        return results
        
    def update_metrics(self, service_id: str, metrics: ServiceMetrics):
        """Обновление метрик"""
        service = self.registry.get(service_id)
        if service:
            service.metrics = metrics
            service.updated_at = datetime.now()
            
            # Обновляем health на основе метрик
            if metrics.error_rate > 5:
                service.health = HealthStatus.UNHEALTHY
            elif metrics.error_rate > 1 or metrics.availability < 99:
                service.health = HealthStatus.DEGRADED
            else:
                service.health = HealthStatus.HEALTHY


class ProvisioningEngine:
    """Движок провизионирования"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.templates: Dict[str, ServiceTemplate] = {}
        self.requests: List[ProvisioningRequest] = []
        
    def register_template(self, template: ServiceTemplate):
        """Регистрация шаблона"""
        self.templates[template.template_id] = template
        
    async def provision(self, request: ProvisioningRequest) -> Service:
        """Провизионирование сервиса"""
        request.status = ProvisioningStatus.IN_PROGRESS
        request.logs.append(f"{datetime.now().isoformat()}: Starting provisioning")
        
        template = self.templates.get(request.template_id)
        if not template:
            request.status = ProvisioningStatus.FAILED
            request.logs.append("Error: Template not found")
            raise ValueError(f"Template {request.template_id} not found")
            
        # Проверяем обязательные параметры
        for param in template.required_params:
            if param not in request.parameters:
                request.status = ProvisioningStatus.FAILED
                request.logs.append(f"Error: Missing required parameter: {param}")
                raise ValueError(f"Missing required parameter: {param}")
                
        request.logs.append(f"{datetime.now().isoformat()}: Creating service from template")
        
        # Создаём сервис
        service = Service(
            service_id=f"svc_{uuid.uuid4().hex[:8]}",
            name=request.service_name,
            display_name=request.parameters.get("display_name", request.service_name),
            description=request.parameters.get("description", ""),
            service_type=template.service_type,
            status=ServiceStatus.DEVELOPMENT,
            language=template.default_config.get("language", ""),
            framework=template.default_config.get("framework", ""),
            infrastructure=template.default_config.get("infrastructure", "kubernetes"),
            tags={**template.default_tags, "environment": request.environment}
        )
        
        # Добавляем эндпоинт
        endpoint = ServiceEndpoint(
            endpoint_id=f"ep_{uuid.uuid4().hex[:8]}",
            name=f"{request.service_name}-{request.environment}",
            url=f"https://{request.service_name}.{request.environment}.internal",
            environment=request.environment,
            health_check_path="/health"
        )
        service.endpoints.append(endpoint)
        
        # Добавляем SLA по умолчанию
        service.sla = ServiceSLA()
        
        # Инициализируем метрики
        service.metrics = ServiceMetrics(instance_count=template.default_resources.get("replicas", 1))
        
        # Регистрируем
        self.registry.register(service)
        
        request.logs.append(f"{datetime.now().isoformat()}: Service created successfully")
        request.status = ProvisioningStatus.COMPLETED
        request.created_service_id = service.service_id
        request.completed_at = datetime.now()
        
        self.requests.append(request)
        
        return service


class ServiceCatalogPlatform:
    """Платформа каталога сервисов"""
    
    def __init__(self):
        self.registry = ServiceRegistry()
        self.dependency_manager = DependencyManager(self.registry)
        self.health_checker = HealthChecker(self.registry)
        self.provisioning_engine = ProvisioningEngine(self.registry)
        
    def create_service(self, name: str, service_type: ServiceType,
                        **kwargs) -> Service:
        """Создание сервиса"""
        service = Service(
            service_id=f"svc_{uuid.uuid4().hex[:8]}",
            name=name,
            service_type=service_type,
            **kwargs
        )
        self.registry.register(service)
        return service
        
    def add_endpoint(self, service_id: str, name: str, url: str,
                      environment: str, **kwargs) -> ServiceEndpoint:
        """Добавление эндпоинта"""
        service = self.registry.get(service_id)
        if not service:
            raise ValueError(f"Service {service_id} not found")
            
        endpoint = ServiceEndpoint(
            endpoint_id=f"ep_{uuid.uuid4().hex[:8]}",
            name=name,
            url=url,
            environment=environment,
            **kwargs
        )
        service.endpoints.append(endpoint)
        return endpoint
        
    def add_dependency(self, service_id: str, depends_on_id: str,
                        dependency_type: str = "runtime",
                        is_critical: bool = True) -> ServiceDependency:
        """Добавление зависимости"""
        service = self.registry.get(service_id)
        dep_service = self.registry.get(depends_on_id)
        
        if not service:
            raise ValueError(f"Service {service_id} not found")
        if not dep_service:
            raise ValueError(f"Dependency service {depends_on_id} not found")
            
        # Проверяем циклы
        if self.dependency_manager.check_circular(service_id, depends_on_id):
            raise ValueError("Circular dependency detected")
            
        dependency = ServiceDependency(
            dependency_id=f"dep_{uuid.uuid4().hex[:8]}",
            service_id=depends_on_id,
            dependency_type=dependency_type,
            is_critical=is_critical,
            description=f"{service.name} depends on {dep_service.name}"
        )
        service.dependencies.append(dependency)
        return dependency
        
    def add_version(self, service_id: str, version: str,
                     changelog: str = "", git_commit: str = "",
                     docker_image: str = "") -> ServiceVersion:
        """Добавление версии"""
        service = self.registry.get(service_id)
        if not service:
            raise ValueError(f"Service {service_id} not found")
            
        # Сбрасываем is_current для всех версий
        for v in service.versions:
            v.is_current = False
            
        version_obj = ServiceVersion(
            version=version,
            changelog=changelog,
            git_commit=git_commit,
            docker_image=docker_image,
            is_current=True
        )
        
        service.versions.append(version_obj)
        service.current_version = version
        service.updated_at = datetime.now()
        
        return version_obj
        
    def register_template(self, name: str, service_type: ServiceType,
                           default_config: Dict[str, Any] = None,
                           required_params: List[str] = None,
                           **kwargs) -> ServiceTemplate:
        """Регистрация шаблона"""
        template = ServiceTemplate(
            template_id=f"tmpl_{uuid.uuid4().hex[:8]}",
            name=name,
            service_type=service_type,
            default_config=default_config or {},
            required_params=required_params or [],
            **kwargs
        )
        self.provisioning_engine.register_template(template)
        return template
        
    async def provision_service(self, template_id: str, service_name: str,
                                  environment: str, parameters: Dict[str, Any] = None,
                                  requestor: str = "") -> Service:
        """Провизионирование сервиса"""
        request = ProvisioningRequest(
            request_id=f"prov_{uuid.uuid4().hex[:8]}",
            template_id=template_id,
            service_name=service_name,
            environment=environment,
            parameters=parameters or {},
            requestor=requestor
        )
        
        return await self.provisioning_engine.provision(request)
        
    async def check_health(self, service_id: str = None) -> Dict[str, HealthStatus]:
        """Проверка здоровья"""
        if service_id:
            result = await self.health_checker.check_service(service_id)
            return {service_id: result}
        return await self.health_checker.check_all()
        
    def get_dependency_tree(self, service_id: str) -> Dict[str, Any]:
        """Дерево зависимостей"""
        return self.dependency_manager.get_dependency_tree(service_id)
        
    def impact_analysis(self, service_id: str) -> Dict[str, Any]:
        """Анализ влияния"""
        return self.dependency_manager.impact_analysis(service_id)
        
    def search(self, query: str) -> List[Service]:
        """Поиск сервисов"""
        return self.registry.search(query)
        
    def get_catalog_summary(self) -> Dict[str, Any]:
        """Сводка каталога"""
        by_type = defaultdict(int)
        by_status = defaultdict(int)
        by_health = defaultdict(int)
        by_tier = defaultdict(int)
        
        for service in self.registry.services.values():
            by_type[service.service_type.value] += 1
            by_status[service.status.value] += 1
            by_health[service.health.value] += 1
            by_tier[f"tier_{service.tier}"] += 1
            
        return {
            "total_services": len(self.registry.services),
            "templates": len(self.provisioning_engine.templates),
            "by_type": dict(by_type),
            "by_status": dict(by_status),
            "by_health": dict(by_health),
            "by_tier": dict(by_tier)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 87: Service Catalog Platform")
    print("=" * 60)
    
    async def demo():
        platform = ServiceCatalogPlatform()
        print("✓ Service Catalog Platform created")
        
        # Создание сервисов
        print("\n📦 Creating Services...")
        
        # API Gateway
        gateway = platform.create_service(
            "api-gateway",
            ServiceType.GATEWAY,
            display_name="API Gateway",
            description="Main API gateway for all external traffic",
            owner=ServiceOwner(
                team="platform",
                email="platform-team@company.com",
                slack_channel="#platform-alerts"
            ),
            language="Go",
            framework="Kong",
            infrastructure="kubernetes",
            tier=1,  # Critical
            documentation_url="https://docs.company.com/api-gateway",
            runbook_url="https://runbooks.company.com/api-gateway"
        )
        
        platform.add_endpoint(
            gateway.service_id,
            "production",
            "https://api.company.com",
            "production",
            is_public=True
        )
        
        platform.add_version(gateway.service_id, "2.5.0",
                              changelog="Performance improvements",
                              docker_image="company/api-gateway:2.5.0")
        
        print(f"\n  🚀 {gateway.display_name}")
        print(f"     Type: {gateway.service_type.value}")
        print(f"     Tier: {gateway.tier} (Critical)")
        print(f"     Version: {gateway.current_version}")
        
        # User Service
        user_svc = platform.create_service(
            "user-service",
            ServiceType.API,
            display_name="User Service",
            description="Manages user accounts and authentication",
            owner=ServiceOwner(
                team="identity",
                email="identity-team@company.com"
            ),
            language="Python",
            framework="FastAPI",
            infrastructure="kubernetes",
            tier=1,
            sla=ServiceSLA(
                availability_target=99.99,
                latency_p99_ms=200
            )
        )
        
        platform.add_endpoint(user_svc.service_id, "production",
                               "https://user.internal.company.com", "production")
        platform.add_endpoint(user_svc.service_id, "staging",
                               "https://user.staging.company.com", "staging")
        
        print(f"\n  👤 {user_svc.display_name}")
        print(f"     SLA: {user_svc.sla.availability_target}% availability")
        
        # Order Service
        order_svc = platform.create_service(
            "order-service",
            ServiceType.API,
            display_name="Order Service",
            description="Handles order creation and management",
            owner=ServiceOwner(team="commerce"),
            language="Java",
            framework="Spring Boot",
            tier=1
        )
        
        print(f"\n  🛒 {order_svc.display_name}")
        
        # PostgreSQL
        postgres = platform.create_service(
            "postgres-primary",
            ServiceType.DATABASE,
            display_name="PostgreSQL Primary",
            description="Primary PostgreSQL database cluster",
            owner=ServiceOwner(team="dba"),
            tier=1
        )
        
        print(f"\n  🗄️ {postgres.display_name}")
        
        # Redis Cache
        redis = platform.create_service(
            "redis-cluster",
            ServiceType.CACHE,
            display_name="Redis Cache Cluster",
            description="Distributed Redis cache",
            owner=ServiceOwner(team="platform"),
            tier=2
        )
        
        print(f"\n  💾 {redis.display_name}")
        
        # Notification Service
        notify_svc = platform.create_service(
            "notification-service",
            ServiceType.WORKER,
            display_name="Notification Service",
            description="Sends emails, SMS, push notifications",
            owner=ServiceOwner(team="platform"),
            tier=2
        )
        
        print(f"\n  📬 {notify_svc.display_name}")
        
        # RabbitMQ
        rabbitmq = platform.create_service(
            "rabbitmq",
            ServiceType.QUEUE,
            display_name="RabbitMQ Message Broker",
            description="Message queue for async communication",
            owner=ServiceOwner(team="platform"),
            tier=2
        )
        
        print(f"\n  📨 {rabbitmq.display_name}")
        
        # Добавление зависимостей
        print("\n🔗 Setting Up Dependencies...")
        
        # Gateway -> User Service
        platform.add_dependency(gateway.service_id, user_svc.service_id,
                                 "runtime", is_critical=True)
        print(f"  ✓ {gateway.name} → {user_svc.name}")
        
        # Gateway -> Order Service
        platform.add_dependency(gateway.service_id, order_svc.service_id,
                                 "runtime", is_critical=True)
        print(f"  ✓ {gateway.name} → {order_svc.name}")
        
        # User Service -> PostgreSQL
        platform.add_dependency(user_svc.service_id, postgres.service_id,
                                 "runtime", is_critical=True)
        print(f"  ✓ {user_svc.name} → {postgres.name}")
        
        # User Service -> Redis
        platform.add_dependency(user_svc.service_id, redis.service_id,
                                 "runtime", is_critical=False)
        print(f"  ✓ {user_svc.name} → {redis.name} (optional)")
        
        # Order Service -> PostgreSQL
        platform.add_dependency(order_svc.service_id, postgres.service_id,
                                 "runtime", is_critical=True)
        print(f"  ✓ {order_svc.name} → {postgres.name}")
        
        # Order Service -> RabbitMQ
        platform.add_dependency(order_svc.service_id, rabbitmq.service_id,
                                 "runtime", is_critical=True)
        print(f"  ✓ {order_svc.name} → {rabbitmq.name}")
        
        # Notification Service -> RabbitMQ
        platform.add_dependency(notify_svc.service_id, rabbitmq.service_id,
                                 "runtime", is_critical=True)
        print(f"  ✓ {notify_svc.name} → {rabbitmq.name}")
        
        # Дерево зависимостей
        print("\n🌳 Dependency Tree (API Gateway):")
        
        tree = platform.get_dependency_tree(gateway.service_id)
        
        def print_tree(node, indent=0, is_last=True):
            prefix = "  " * indent
            connector = "└── " if is_last else "├── "
            
            if indent > 0:
                print(f"{prefix}{connector}{node['name']} [{node['health']}]")
            else:
                print(f"  {node['name']} [{node['health']}]")
                
            deps = node.get("dependencies", [])
            for i, dep in enumerate(deps):
                print_tree(dep, indent + 1, i == len(deps) - 1)
                
        print_tree(tree)
        
        # Анализ влияния
        print("\n💥 Impact Analysis (if PostgreSQL fails):")
        
        impact = platform.impact_analysis(postgres.service_id)
        
        print(f"\n  Source: {impact['source_service']}")
        print(f"  Total Affected: {impact['total_affected']} services")
        
        if impact['critical_services']:
            print(f"\n  🔴 Critical Services Affected:")
            for svc in impact['critical_services']:
                print(f"     • {svc}")
                
        if impact['important_services']:
            print(f"\n  🟡 Important Services Affected:")
            for svc in impact['important_services']:
                print(f"     • {svc}")
                
        # Проверка здоровья
        print("\n💚 Health Check:")
        
        health_results = await platform.check_health()
        
        for service_id, health in health_results.items():
            service = platform.registry.get(service_id)
            
            icon = {
                HealthStatus.HEALTHY: "🟢",
                HealthStatus.DEGRADED: "🟡",
                HealthStatus.UNHEALTHY: "🔴",
                HealthStatus.UNKNOWN: "⚪"
            }.get(health, "⚪")
            
            print(f"  {icon} {service.name if service else service_id}: {health.value}")
            
        # Обновляем метрики
        print("\n📊 Updating Service Metrics...")
        
        for service in platform.registry.services.values():
            metrics = ServiceMetrics(
                requests_per_second=random.uniform(100, 1000),
                latency_p50_ms=random.uniform(10, 50),
                latency_p99_ms=random.uniform(100, 300),
                error_rate=random.uniform(0, 2),
                availability=random.uniform(99, 100),
                cpu_usage=random.uniform(20, 80),
                memory_usage=random.uniform(30, 70),
                instance_count=random.randint(2, 10)
            )
            platform.health_checker.update_metrics(service.service_id, metrics)
            
        print("  ✓ Metrics updated for all services")
        
        # Шаблоны сервисов
        print("\n📋 Registering Service Templates...")
        
        api_template = platform.register_template(
            "Python API Service",
            ServiceType.API,
            default_config={
                "language": "Python",
                "framework": "FastAPI",
                "infrastructure": "kubernetes"
            },
            required_params=["display_name", "description"],
            default_resources={"cpu": "500m", "memory": "512Mi", "replicas": 2},
            default_tags={"team": "platform", "managed": "true"},
            description="Standard Python API service template"
        )
        print(f"  ✓ {api_template.name}")
        
        worker_template = platform.register_template(
            "Worker Service",
            ServiceType.WORKER,
            default_config={
                "language": "Python",
                "framework": "Celery",
                "infrastructure": "kubernetes"
            },
            required_params=["display_name"],
            default_resources={"cpu": "250m", "memory": "256Mi", "replicas": 3},
            description="Standard background worker template"
        )
        print(f"  ✓ {worker_template.name}")
        
        # Self-Service Provisioning
        print("\n🚀 Self-Service Provisioning:")
        
        new_service = await platform.provision_service(
            api_template.template_id,
            "payment-service",
            "staging",
            parameters={
                "display_name": "Payment Service",
                "description": "Handles payment processing"
            },
            requestor="dev@company.com"
        )
        
        print(f"\n  ✓ Service Provisioned: {new_service.display_name}")
        print(f"    ID: {new_service.service_id}")
        print(f"    Environment: staging")
        print(f"    Status: {new_service.status.value}")
        
        if new_service.endpoints:
            print(f"    Endpoint: {new_service.endpoints[0].url}")
            
        # Поиск сервисов
        print("\n🔍 Service Search:")
        
        results = platform.search("service")
        print(f"\n  Query: 'service'")
        print(f"  Found: {len(results)} services")
        
        for svc in results[:5]:
            print(f"    • {svc.display_name or svc.name}")
            
        # Каталог по типам
        print("\n📂 Services by Type:")
        
        for svc_type in ServiceType:
            services = platform.registry.find_by_type(svc_type)
            if services:
                print(f"\n  {svc_type.value.upper()}: ({len(services)})")
                for svc in services:
                    status_icon = "🟢" if svc.status == ServiceStatus.ACTIVE else "🔵"
                    print(f"    {status_icon} {svc.display_name or svc.name}")
                    
        # Сводка каталога
        print("\n📊 Service Catalog Summary:")
        
        summary = platform.get_catalog_summary()
        
        print(f"\n  Total Services: {summary['total_services']}")
        print(f"  Templates: {summary['templates']}")
        
        print("\n  By Tier:")
        for tier, count in sorted(summary['by_tier'].items()):
            tier_icon = {"tier_1": "🔴", "tier_2": "🟡", "tier_3": "🟢"}.get(tier, "⚪")
            tier_name = {"tier_1": "Critical", "tier_2": "Important", "tier_3": "Standard"}.get(tier, tier)
            print(f"    {tier_icon} {tier_name}: {count}")
            
        print("\n  By Health:")
        for health, count in summary['by_health'].items():
            health_icon = {"healthy": "🟢", "degraded": "🟡", "unhealthy": "🔴", "unknown": "⚪"}.get(health, "⚪")
            print(f"    {health_icon} {health}: {count}")
            
        # Service Dashboard
        print("\n📋 Service Catalog Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────┐")
        print(f"  │ Total Services: {summary['total_services']:>4}    Templates: {summary['templates']:>4}             │")
        print("  ├─────────────────────────────────────────────────────────┤")
        
        for service in list(platform.registry.services.values())[:7]:
            health_icon = {
                HealthStatus.HEALTHY: "🟢",
                HealthStatus.DEGRADED: "🟡",
                HealthStatus.UNHEALTHY: "🔴"
            }.get(service.health, "⚪")
            
            name = (service.display_name or service.name)[:20].ljust(20)
            stype = service.service_type.value[:10].ljust(10)
            
            print(f"  │ {health_icon} {name} {stype}        │")
            
        print("  └─────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Service Catalog Platform initialized!")
    print("=" * 60)
