#!/usr/bin/env python3
"""
Server Init - Iteration 160: Service Catalog Platform
Платформа каталога сервисов

Функционал:
- Service Registration - регистрация сервисов
- Service Discovery - обнаружение сервисов
- Dependency Mapping - маппинг зависимостей
- API Documentation - документация API
- Service Ownership - владение сервисами
- Health Dashboard - дашборд здоровья
- SLA Management - управление SLA
- Service Scoring - оценка сервисов
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid


class ServiceStatus(Enum):
    """Статус сервиса"""
    ACTIVE = "active"
    DEGRADED = "degraded"
    DOWN = "down"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"


class ServiceTier(Enum):
    """Уровень сервиса"""
    TIER1 = "tier1"  # Mission critical
    TIER2 = "tier2"  # Business critical
    TIER3 = "tier3"  # Standard
    TIER4 = "tier4"  # Best effort


class ServiceType(Enum):
    """Тип сервиса"""
    API = "api"
    BACKEND = "backend"
    FRONTEND = "frontend"
    DATABASE = "database"
    QUEUE = "queue"
    CACHE = "cache"
    GATEWAY = "gateway"
    WORKER = "worker"


class HealthStatus(Enum):
    """Статус здоровья"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class Owner:
    """Владелец сервиса"""
    owner_id: str
    name: str = ""
    team: str = ""
    email: str = ""
    slack_channel: str = ""
    pagerduty_service: str = ""


@dataclass
class Endpoint:
    """Эндпоинт сервиса"""
    endpoint_id: str
    url: str = ""
    method: str = "GET"
    description: str = ""
    auth_required: bool = True
    rate_limit: int = 1000
    timeout_ms: int = 5000


@dataclass
class APISpec:
    """Спецификация API"""
    spec_id: str
    version: str = "1.0.0"
    format: str = "openapi"  # openapi, graphql, grpc
    spec_url: str = ""
    endpoints: List[Endpoint] = field(default_factory=list)


@dataclass
class Dependency:
    """Зависимость"""
    dependency_id: str
    source_service: str = ""
    target_service: str = ""
    dependency_type: str = "sync"  # sync, async, optional
    criticality: str = "high"  # high, medium, low
    description: str = ""


@dataclass
class SLA:
    """SLA сервиса"""
    sla_id: str
    availability_target: float = 99.9  # percentage
    latency_p50_ms: int = 100
    latency_p95_ms: int = 500
    latency_p99_ms: int = 1000
    error_rate_threshold: float = 0.1  # percentage
    
    # Actual metrics
    current_availability: float = 100.0
    current_latency_p50: int = 0
    current_latency_p95: int = 0
    current_latency_p99: int = 0
    current_error_rate: float = 0.0
    
    # Compliance
    sla_met: bool = True


@dataclass
class HealthCheck:
    """Проверка здоровья"""
    check_id: str
    service_id: str = ""
    
    # Config
    endpoint: str = "/health"
    interval_seconds: int = 30
    timeout_seconds: int = 5
    
    # Status
    status: HealthStatus = HealthStatus.UNKNOWN
    last_check: Optional[datetime] = None
    consecutive_failures: int = 0
    
    # Response
    response_time_ms: int = 0
    last_error: str = ""


@dataclass
class Service:
    """Сервис"""
    service_id: str
    name: str = ""
    
    # Classification
    service_type: ServiceType = ServiceType.API
    tier: ServiceTier = ServiceTier.TIER3
    
    # Status
    status: ServiceStatus = ServiceStatus.ACTIVE
    
    # Ownership
    owner: Optional[Owner] = None
    
    # Technical details
    repository: str = ""
    documentation_url: str = ""
    runbook_url: str = ""
    
    # API
    api_spec: Optional[APISpec] = None
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    
    # SLA
    sla: Optional[SLA] = None
    
    # Health
    health_status: HealthStatus = HealthStatus.UNKNOWN
    health_checks: List[HealthCheck] = field(default_factory=list)
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Scoring
    maturity_score: float = 0.0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ServiceScore:
    """Оценка сервиса"""
    score_id: str
    service_id: str = ""
    
    # Scores (0-100)
    documentation_score: int = 0
    testing_score: int = 0
    monitoring_score: int = 0
    security_score: int = 0
    reliability_score: int = 0
    
    # Overall
    overall_score: int = 0
    grade: str = "F"  # A, B, C, D, F
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    
    # Timestamp
    scored_at: datetime = field(default_factory=datetime.now)


class ServiceRegistry:
    """Реестр сервисов"""
    
    def __init__(self):
        self.services: Dict[str, Service] = {}
        self.owners: Dict[str, Owner] = {}
        self.dependencies: Dict[str, Dependency] = {}
        
    def register_service(self, name: str, service_type: ServiceType,
                          tier: ServiceTier, **kwargs) -> Service:
        """Регистрация сервиса"""
        service = Service(
            service_id=f"svc_{uuid.uuid4().hex[:8]}",
            name=name,
            service_type=service_type,
            tier=tier,
            **kwargs
        )
        self.services[service.service_id] = service
        return service
        
    def register_owner(self, name: str, team: str, email: str,
                        **kwargs) -> Owner:
        """Регистрация владельца"""
        owner = Owner(
            owner_id=f"own_{uuid.uuid4().hex[:8]}",
            name=name,
            team=team,
            email=email,
            **kwargs
        )
        self.owners[owner.owner_id] = owner
        return owner
        
    def assign_owner(self, service_id: str, owner_id: str):
        """Назначение владельца"""
        if service_id in self.services and owner_id in self.owners:
            self.services[service_id].owner = self.owners[owner_id]
            
    def add_dependency(self, source_id: str, target_id: str,
                        dependency_type: str = "sync",
                        criticality: str = "high") -> Optional[Dependency]:
        """Добавление зависимости"""
        if source_id not in self.services or target_id not in self.services:
            return None
            
        dep = Dependency(
            dependency_id=f"dep_{uuid.uuid4().hex[:8]}",
            source_service=source_id,
            target_service=target_id,
            dependency_type=dependency_type,
            criticality=criticality
        )
        
        self.dependencies[dep.dependency_id] = dep
        self.services[source_id].dependencies.append(target_id)
        self.services[target_id].dependents.append(source_id)
        
        return dep
        
    def get_service_by_name(self, name: str) -> Optional[Service]:
        """Получение сервиса по имени"""
        for service in self.services.values():
            if service.name == name:
                return service
        return None
        
    def search_services(self, query: str = "", service_type: ServiceType = None,
                         tier: ServiceTier = None, tags: List[str] = None) -> List[Service]:
        """Поиск сервисов"""
        results = list(self.services.values())
        
        if query:
            results = [s for s in results if query.lower() in s.name.lower()]
            
        if service_type:
            results = [s for s in results if s.service_type == service_type]
            
        if tier:
            results = [s for s in results if s.tier == tier]
            
        if tags:
            results = [s for s in results if any(t in s.tags for t in tags)]
            
        return results


class DependencyMapper:
    """Маппер зависимостей"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        
    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """Получение графа зависимостей"""
        graph = {}
        
        for service in self.registry.services.values():
            graph[service.service_id] = service.dependencies
            
        return graph
        
    def get_upstream_services(self, service_id: str,
                               max_depth: int = 10) -> Set[str]:
        """Получение upstream сервисов"""
        if service_id not in self.registry.services:
            return set()
            
        upstream = set()
        queue = [(service_id, 0)]
        visited = set()
        
        while queue:
            current, depth = queue.pop(0)
            
            if current in visited or depth > max_depth:
                continue
                
            visited.add(current)
            service = self.registry.services.get(current)
            
            if service:
                for dep in service.dependencies:
                    if dep not in visited:
                        upstream.add(dep)
                        queue.append((dep, depth + 1))
                        
        return upstream
        
    def get_downstream_services(self, service_id: str,
                                  max_depth: int = 10) -> Set[str]:
        """Получение downstream сервисов"""
        if service_id not in self.registry.services:
            return set()
            
        downstream = set()
        queue = [(service_id, 0)]
        visited = set()
        
        while queue:
            current, depth = queue.pop(0)
            
            if current in visited or depth > max_depth:
                continue
                
            visited.add(current)
            service = self.registry.services.get(current)
            
            if service:
                for dep in service.dependents:
                    if dep not in visited:
                        downstream.add(dep)
                        queue.append((dep, depth + 1))
                        
        return downstream
        
    def get_critical_path(self, service_id: str) -> List[str]:
        """Получение критического пути"""
        critical = []
        
        service = self.registry.services.get(service_id)
        if not service:
            return critical
            
        for dep_id in service.dependencies:
            dep = None
            for d in self.registry.dependencies.values():
                if d.source_service == service_id and d.target_service == dep_id:
                    dep = d
                    break
                    
            if dep and dep.criticality == "high":
                critical.append(dep_id)
                critical.extend(self.get_critical_path(dep_id))
                
        return critical
        
    def detect_circular_dependencies(self) -> List[List[str]]:
        """Обнаружение циклических зависимостей"""
        cycles = []
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(service_id: str) -> bool:
            visited.add(service_id)
            rec_stack.add(service_id)
            path.append(service_id)
            
            service = self.registry.services.get(service_id)
            if service:
                for dep in service.dependencies:
                    if dep not in visited:
                        if dfs(dep):
                            return True
                    elif dep in rec_stack:
                        # Found cycle
                        cycle_start = path.index(dep)
                        cycles.append(path[cycle_start:] + [dep])
                        
            path.pop()
            rec_stack.remove(service_id)
            return False
            
        for service_id in self.registry.services:
            if service_id not in visited:
                dfs(service_id)
                
        return cycles


class HealthMonitor:
    """Монитор здоровья"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        
    async def check_service(self, service: Service) -> HealthCheck:
        """Проверка здоровья сервиса"""
        check = HealthCheck(
            check_id=f"chk_{uuid.uuid4().hex[:8]}",
            service_id=service.service_id
        )
        
        # Simulate health check
        await asyncio.sleep(0.05)
        
        import random
        is_healthy = random.random() > 0.1  # 90% healthy
        
        check.last_check = datetime.now()
        
        if is_healthy:
            check.status = HealthStatus.HEALTHY
            check.response_time_ms = random.randint(10, 200)
            check.consecutive_failures = 0
        else:
            check.status = HealthStatus.UNHEALTHY
            check.consecutive_failures += 1
            check.last_error = "Connection timeout"
            
        service.health_status = check.status
        service.health_checks.append(check)
        
        return check
        
    async def check_all_services(self) -> Dict[str, HealthStatus]:
        """Проверка всех сервисов"""
        results = {}
        
        for service in self.registry.services.values():
            check = await self.check_service(service)
            results[service.service_id] = check.status
            
        return results


class SLAManager:
    """Менеджер SLA"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        
    def create_sla(self, service_id: str, availability: float = 99.9,
                    **kwargs) -> Optional[SLA]:
        """Создание SLA"""
        if service_id not in self.registry.services:
            return None
            
        sla = SLA(
            sla_id=f"sla_{uuid.uuid4().hex[:8]}",
            availability_target=availability,
            **kwargs
        )
        
        self.registry.services[service_id].sla = sla
        return sla
        
    def update_metrics(self, service_id: str, availability: float,
                        latency_p50: int, latency_p95: int, latency_p99: int,
                        error_rate: float):
        """Обновление метрик"""
        service = self.registry.services.get(service_id)
        
        if not service or not service.sla:
            return
            
        sla = service.sla
        sla.current_availability = availability
        sla.current_latency_p50 = latency_p50
        sla.current_latency_p95 = latency_p95
        sla.current_latency_p99 = latency_p99
        sla.current_error_rate = error_rate
        
        # Check SLA compliance
        sla.sla_met = (
            availability >= sla.availability_target and
            latency_p50 <= sla.latency_p50_ms and
            latency_p95 <= sla.latency_p95_ms and
            latency_p99 <= sla.latency_p99_ms and
            error_rate <= sla.error_rate_threshold
        )
        
    def get_sla_report(self) -> Dict[str, Any]:
        """Отчёт по SLA"""
        report = {
            "total_services": 0,
            "with_sla": 0,
            "sla_met": 0,
            "sla_violated": 0,
            "services": []
        }
        
        for service in self.registry.services.values():
            report["total_services"] += 1
            
            if service.sla:
                report["with_sla"] += 1
                
                if service.sla.sla_met:
                    report["sla_met"] += 1
                else:
                    report["sla_violated"] += 1
                    
                report["services"].append({
                    "name": service.name,
                    "availability": service.sla.current_availability,
                    "target": service.sla.availability_target,
                    "met": service.sla.sla_met
                })
                
        return report


class ServiceScorer:
    """Оценщик сервисов"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        
    def score_service(self, service: Service) -> ServiceScore:
        """Оценка сервиса"""
        score = ServiceScore(
            score_id=f"scr_{uuid.uuid4().hex[:8]}",
            service_id=service.service_id
        )
        
        # Documentation score
        score.documentation_score = self._score_documentation(service)
        
        # Testing score
        score.testing_score = self._score_testing(service)
        
        # Monitoring score
        score.monitoring_score = self._score_monitoring(service)
        
        # Security score
        score.security_score = self._score_security(service)
        
        # Reliability score
        score.reliability_score = self._score_reliability(service)
        
        # Calculate overall
        score.overall_score = (
            score.documentation_score * 0.2 +
            score.testing_score * 0.2 +
            score.monitoring_score * 0.2 +
            score.security_score * 0.2 +
            score.reliability_score * 0.2
        )
        
        # Assign grade
        if score.overall_score >= 90:
            score.grade = "A"
        elif score.overall_score >= 80:
            score.grade = "B"
        elif score.overall_score >= 70:
            score.grade = "C"
        elif score.overall_score >= 60:
            score.grade = "D"
        else:
            score.grade = "F"
            
        # Generate recommendations
        score.recommendations = self._generate_recommendations(service, score)
        
        service.maturity_score = score.overall_score
        
        return score
        
    def _score_documentation(self, service: Service) -> int:
        """Оценка документации"""
        score = 0
        
        if service.documentation_url:
            score += 30
        if service.runbook_url:
            score += 30
        if service.api_spec:
            score += 40
            
        return min(score, 100)
        
    def _score_testing(self, service: Service) -> int:
        """Оценка тестирования"""
        # Simplified - would check actual test coverage
        return 70 if service.repository else 30
        
    def _score_monitoring(self, service: Service) -> int:
        """Оценка мониторинга"""
        score = 0
        
        if service.health_checks:
            score += 50
        if service.sla:
            score += 50
            
        return min(score, 100)
        
    def _score_security(self, service: Service) -> int:
        """Оценка безопасности"""
        score = 50  # Base score
        
        if service.api_spec and service.api_spec.endpoints:
            auth_endpoints = [e for e in service.api_spec.endpoints if e.auth_required]
            if len(auth_endpoints) == len(service.api_spec.endpoints):
                score += 50
                
        return min(score, 100)
        
    def _score_reliability(self, service: Service) -> int:
        """Оценка надёжности"""
        score = 50
        
        if service.sla and service.sla.sla_met:
            score += 30
        if service.tier in [ServiceTier.TIER1, ServiceTier.TIER2]:
            score += 20
            
        return min(score, 100)
        
    def _generate_recommendations(self, service: Service,
                                    score: ServiceScore) -> List[str]:
        """Генерация рекомендаций"""
        recommendations = []
        
        if score.documentation_score < 70:
            recommendations.append("Add or improve API documentation")
        if score.testing_score < 70:
            recommendations.append("Increase test coverage")
        if score.monitoring_score < 70:
            recommendations.append("Add health checks and define SLA")
        if score.security_score < 70:
            recommendations.append("Review authentication on all endpoints")
        if score.reliability_score < 70:
            recommendations.append("Review and improve SLA compliance")
            
        return recommendations


class ServiceCatalogPlatform:
    """Платформа каталога сервисов"""
    
    def __init__(self):
        self.registry = ServiceRegistry()
        self.dependency_mapper = DependencyMapper(self.registry)
        self.health_monitor = HealthMonitor(self.registry)
        self.sla_manager = SLAManager(self.registry)
        self.scorer = ServiceScorer(self.registry)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        services = list(self.registry.services.values())
        
        by_type = {}
        for service in services:
            t = service.service_type.value
            by_type[t] = by_type.get(t, 0) + 1
            
        by_tier = {}
        for service in services:
            t = service.tier.value
            by_tier[t] = by_tier.get(t, 0) + 1
            
        healthy = len([s for s in services if s.health_status == HealthStatus.HEALTHY])
        
        return {
            "total_services": len(services),
            "by_type": by_type,
            "by_tier": by_tier,
            "healthy_services": healthy,
            "total_owners": len(self.registry.owners),
            "total_dependencies": len(self.registry.dependencies)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 160: Service Catalog Platform")
    print("=" * 60)
    
    async def demo():
        platform = ServiceCatalogPlatform()
        print("✓ Service Catalog Platform created")
        
        # Register owners
        print("\n👥 Registering Owners...")
        
        owners = [
            ("Platform Team", "platform", "platform@example.com", "#platform-team"),
            ("Backend Team", "backend", "backend@example.com", "#backend-team"),
            ("Data Team", "data", "data@example.com", "#data-team"),
        ]
        
        registered_owners = []
        for name, team, email, slack in owners:
            owner = platform.registry.register_owner(
                name=name, team=team, email=email, slack_channel=slack
            )
            registered_owners.append(owner)
            print(f"  ✓ {name} ({team})")
            
        # Register services
        print("\n📦 Registering Services...")
        
        # API Gateway
        gateway = platform.registry.register_service(
            name="api-gateway",
            service_type=ServiceType.GATEWAY,
            tier=ServiceTier.TIER1,
            repository="github.com/company/api-gateway",
            documentation_url="https://docs.example.com/gateway",
            runbook_url="https://runbooks.example.com/gateway",
            tags=["api", "gateway", "public"]
        )
        platform.registry.assign_owner(gateway.service_id, registered_owners[0].owner_id)
        print(f"  ✓ {gateway.name} ({gateway.service_type.value}, {gateway.tier.value})")
        
        # User Service
        user_svc = platform.registry.register_service(
            name="user-service",
            service_type=ServiceType.API,
            tier=ServiceTier.TIER1,
            repository="github.com/company/user-service",
            documentation_url="https://docs.example.com/user-service",
            tags=["api", "users", "auth"]
        )
        platform.registry.assign_owner(user_svc.service_id, registered_owners[1].owner_id)
        print(f"  ✓ {user_svc.name} ({user_svc.service_type.value}, {user_svc.tier.value})")
        
        # Order Service
        order_svc = platform.registry.register_service(
            name="order-service",
            service_type=ServiceType.API,
            tier=ServiceTier.TIER2,
            repository="github.com/company/order-service",
            tags=["api", "orders", "commerce"]
        )
        platform.registry.assign_owner(order_svc.service_id, registered_owners[1].owner_id)
        print(f"  ✓ {order_svc.name} ({order_svc.service_type.value}, {order_svc.tier.value})")
        
        # Payment Service
        payment_svc = platform.registry.register_service(
            name="payment-service",
            service_type=ServiceType.API,
            tier=ServiceTier.TIER1,
            repository="github.com/company/payment-service",
            runbook_url="https://runbooks.example.com/payment",
            tags=["api", "payments", "critical"]
        )
        print(f"  ✓ {payment_svc.name} ({payment_svc.service_type.value}, {payment_svc.tier.value})")
        
        # Database
        db = platform.registry.register_service(
            name="postgres-primary",
            service_type=ServiceType.DATABASE,
            tier=ServiceTier.TIER1,
            tags=["database", "postgres", "primary"]
        )
        platform.registry.assign_owner(db.service_id, registered_owners[2].owner_id)
        print(f"  ✓ {db.name} ({db.service_type.value}, {db.tier.value})")
        
        # Cache
        cache = platform.registry.register_service(
            name="redis-cache",
            service_type=ServiceType.CACHE,
            tier=ServiceTier.TIER2,
            tags=["cache", "redis"]
        )
        print(f"  ✓ {cache.name} ({cache.service_type.value}, {cache.tier.value})")
        
        # Message Queue
        queue = platform.registry.register_service(
            name="rabbitmq",
            service_type=ServiceType.QUEUE,
            tier=ServiceTier.TIER2,
            tags=["queue", "rabbitmq", "messaging"]
        )
        print(f"  ✓ {queue.name} ({queue.service_type.value}, {queue.tier.value})")
        
        # Add API specs
        print("\n📋 Adding API Specifications...")
        
        user_api = APISpec(
            spec_id=f"spec_{uuid.uuid4().hex[:8]}",
            version="2.1.0",
            format="openapi",
            spec_url="https://api.example.com/user-service/openapi.json",
            endpoints=[
                Endpoint(endpoint_id="e1", url="/users", method="GET", description="List users"),
                Endpoint(endpoint_id="e2", url="/users/{id}", method="GET", description="Get user"),
                Endpoint(endpoint_id="e3", url="/users", method="POST", description="Create user"),
            ]
        )
        user_svc.api_spec = user_api
        print(f"  ✓ {user_svc.name}: OpenAPI v{user_api.version} ({len(user_api.endpoints)} endpoints)")
        
        # Add dependencies
        print("\n🔗 Adding Dependencies...")
        
        deps = [
            (gateway.service_id, user_svc.service_id, "sync", "high"),
            (gateway.service_id, order_svc.service_id, "sync", "high"),
            (gateway.service_id, payment_svc.service_id, "sync", "high"),
            (user_svc.service_id, db.service_id, "sync", "high"),
            (user_svc.service_id, cache.service_id, "sync", "medium"),
            (order_svc.service_id, db.service_id, "sync", "high"),
            (order_svc.service_id, user_svc.service_id, "sync", "high"),
            (order_svc.service_id, queue.service_id, "async", "medium"),
            (payment_svc.service_id, db.service_id, "sync", "high"),
            (payment_svc.service_id, order_svc.service_id, "sync", "high"),
        ]
        
        for source, target, dtype, crit in deps:
            dep = platform.registry.add_dependency(source, target, dtype, crit)
            src_name = platform.registry.services[source].name
            tgt_name = platform.registry.services[target].name
            print(f"  ✓ {src_name} → {tgt_name} ({dtype}, {crit})")
            
        # Create SLAs
        print("\n📊 Creating SLAs...")
        
        sla_configs = [
            (gateway.service_id, 99.99, 50, 200, 500),
            (user_svc.service_id, 99.9, 100, 300, 800),
            (order_svc.service_id, 99.9, 150, 400, 1000),
            (payment_svc.service_id, 99.99, 100, 300, 700),
        ]
        
        for svc_id, avail, p50, p95, p99 in sla_configs:
            sla = platform.sla_manager.create_sla(
                svc_id,
                availability=avail,
                latency_p50_ms=p50,
                latency_p95_ms=p95,
                latency_p99_ms=p99
            )
            svc_name = platform.registry.services[svc_id].name
            print(f"  ✓ {svc_name}: {avail}% availability, P95 < {p95}ms")
            
        # Update metrics
        import random
        for svc_id, _, _, _, _ in sla_configs:
            platform.sla_manager.update_metrics(
                svc_id,
                availability=random.uniform(99.5, 100),
                latency_p50=random.randint(30, 150),
                latency_p95=random.randint(100, 500),
                latency_p99=random.randint(300, 1200),
                error_rate=random.uniform(0, 0.5)
            )
            
        # Health checks
        print("\n🏥 Running Health Checks...")
        
        health_results = await platform.health_monitor.check_all_services()
        
        healthy = sum(1 for s in health_results.values() if s == HealthStatus.HEALTHY)
        print(f"\n  Healthy: {healthy}/{len(health_results)}")
        
        for svc_id, status in health_results.items():
            svc = platform.registry.services[svc_id]
            icon = "✓" if status == HealthStatus.HEALTHY else "✗"
            print(f"  {icon} {svc.name}: {status.value}")
            
        # Dependency analysis
        print("\n🔍 Dependency Analysis...")
        
        # Upstream/Downstream for order service
        upstream = platform.dependency_mapper.get_upstream_services(order_svc.service_id)
        downstream = platform.dependency_mapper.get_downstream_services(order_svc.service_id)
        
        print(f"\n  Order Service Dependencies:")
        print(f"    Upstream: {len(upstream)}")
        for up in upstream:
            print(f"      - {platform.registry.services[up].name}")
        print(f"    Downstream: {len(downstream)}")
        for down in downstream:
            print(f"      - {platform.registry.services[down].name}")
            
        # Critical path
        critical_path = platform.dependency_mapper.get_critical_path(gateway.service_id)
        print(f"\n  Critical Path from API Gateway:")
        for cp in critical_path[:5]:
            svc = platform.registry.services.get(cp)
            if svc:
                print(f"    → {svc.name}")
                
        # Check for circular dependencies
        cycles = platform.dependency_mapper.detect_circular_dependencies()
        print(f"\n  Circular Dependencies: {len(cycles)}")
        
        # Score services
        print("\n📊 Service Scoring...")
        
        scores = []
        for service in platform.registry.services.values():
            score = platform.scorer.score_service(service)
            scores.append((service, score))
            
        print("\n  Service Maturity Scores:")
        print("  ┌─────────────────────────────────────────────────────────────────────┐")
        print("  │ Service              │ Grade │ Overall │ Doc │ Test │ Mon │ Sec │ Rel │")
        print("  ├─────────────────────────────────────────────────────────────────────┤")
        
        for service, score in sorted(scores, key=lambda x: -x[1].overall_score):
            name = service.name[:20].ljust(20)
            print(f"  │ {name} │   {score.grade}   │ {score.overall_score:7.0f} │ {score.documentation_score:3} │ {score.testing_score:4} │ {score.monitoring_score:3} │ {score.security_score:3} │ {score.reliability_score:3} │")
            
        print("  └─────────────────────────────────────────────────────────────────────┘")
        
        # Recommendations
        print("\n💡 Improvement Recommendations:")
        
        for service, score in scores:
            if score.recommendations:
                print(f"\n  {service.name} (Grade: {score.grade}):")
                for rec in score.recommendations[:3]:
                    print(f"    - {rec}")
                    
        # SLA Report
        print("\n📈 SLA Report:")
        
        sla_report = platform.sla_manager.get_sla_report()
        
        print(f"\n  Services with SLA: {sla_report['with_sla']}/{sla_report['total_services']}")
        print(f"  SLA Met: {sla_report['sla_met']}")
        print(f"  SLA Violated: {sla_report['sla_violated']}")
        
        print("\n  ┌───────────────────────────────────────────────────────┐")
        print("  │ Service              │ Availability │ Target │ Status │")
        print("  ├───────────────────────────────────────────────────────┤")
        
        for svc_data in sla_report["services"]:
            name = svc_data["name"][:20].ljust(20)
            avail = f"{svc_data['availability']:.2f}%"
            target = f"{svc_data['target']:.2f}%"
            status = "✓ Met" if svc_data["met"] else "✗ Violated"
            print(f"  │ {name} │ {avail:>12} │ {target:>6} │ {status:>6} │")
            
        print("  └───────────────────────────────────────────────────────┘")
        
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Services: {stats['total_services']}")
        print(f"  Healthy Services: {stats['healthy_services']}")
        print(f"  Total Owners: {stats['total_owners']}")
        print(f"  Total Dependencies: {stats['total_dependencies']}")
        
        print("\n  By Type:")
        for t, count in stats["by_type"].items():
            print(f"    {t}: {count}")
            
        print("\n  By Tier:")
        for t, count in stats["by_tier"].items():
            print(f"    {t}: {count}")
            
        # Dashboard
        print("\n📋 Service Catalog Dashboard:")
        print("  ┌────────────────────────────────────────────────────────────┐")
        print("  │                 Service Catalog Overview                   │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Services:          {stats['total_services']:>10}                   │")
        print(f"  │ Healthy Services:        {stats['healthy_services']:>10}                   │")
        print(f"  │ Total Owners:            {stats['total_owners']:>10}                   │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Dependencies:            {stats['total_dependencies']:>10}                   │")
        print(f"  │ SLA Compliance:          {sla_report['sla_met']:>10}                   │")
        print("  └────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Service Catalog Platform initialized!")
    print("=" * 60)
