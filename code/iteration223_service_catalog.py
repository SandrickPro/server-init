#!/usr/bin/env python3
"""
Server Init - Iteration 223: Service Catalog Platform
Платформа каталога сервисов

Функционал:
- Service Registration - регистрация сервисов
- Metadata Management - управление метаданными
- Dependency Mapping - маппинг зависимостей
- Owner Assignment - назначение владельцев
- Documentation Linking - связывание документации
- Health Integration - интеграция здоровья
- Search & Discovery - поиск и обнаружение
- Service Scoring - оценка сервисов
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid


class ServiceType(Enum):
    """Тип сервиса"""
    API = "api"
    BACKEND = "backend"
    FRONTEND = "frontend"
    DATABASE = "database"
    QUEUE = "queue"
    CACHE = "cache"
    WORKER = "worker"
    GATEWAY = "gateway"


class ServiceTier(Enum):
    """Уровень критичности"""
    TIER_0 = "tier_0"  # Mission critical
    TIER_1 = "tier_1"  # Business critical
    TIER_2 = "tier_2"  # Important
    TIER_3 = "tier_3"  # Non-critical


class LifecycleStatus(Enum):
    """Статус жизненного цикла"""
    PLANNING = "planning"
    DEVELOPMENT = "development"
    BETA = "beta"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


class HealthStatus(Enum):
    """Статус здоровья"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceOwner:
    """Владелец сервиса"""
    owner_id: str
    name: str = ""
    email: str = ""
    team: str = ""
    slack_channel: str = ""
    pagerduty_id: str = ""


@dataclass
class ServiceLink:
    """Ссылка сервиса"""
    link_id: str
    title: str = ""
    url: str = ""
    link_type: str = ""  # docs, repo, dashboard, runbook


@dataclass
class ServiceDependency:
    """Зависимость сервиса"""
    dep_id: str
    service_id: str = ""
    dependency_service_id: str = ""
    dependency_type: str = "runtime"  # runtime, build, optional
    is_critical: bool = True


@dataclass
class ServiceEndpoint:
    """Эндпоинт сервиса"""
    endpoint_id: str
    name: str = ""
    url: str = ""
    protocol: str = "http"  # http, grpc, graphql
    port: int = 80
    is_public: bool = False


@dataclass
class ServiceMetrics:
    """Метрики сервиса"""
    requests_per_second: float = 0
    latency_p50_ms: float = 0
    latency_p99_ms: float = 0
    error_rate: float = 0
    uptime_percent: float = 99.9


@dataclass
class Service:
    """Сервис"""
    service_id: str
    name: str = ""
    display_name: str = ""
    description: str = ""
    
    # Type and tier
    service_type: ServiceType = ServiceType.API
    tier: ServiceTier = ServiceTier.TIER_2
    
    # Lifecycle
    lifecycle_status: LifecycleStatus = LifecycleStatus.DEVELOPMENT
    
    # Owner
    owner: Optional[ServiceOwner] = None
    
    # Technical
    language: str = ""
    framework: str = ""
    repository: str = ""
    
    # Endpoints
    endpoints: List[ServiceEndpoint] = field(default_factory=list)
    
    # Links
    links: List[ServiceLink] = field(default_factory=list)
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Health
    health_status: HealthStatus = HealthStatus.UNKNOWN
    health_check_url: str = ""
    
    # Metrics
    metrics: Optional[ServiceMetrics] = None
    
    # Dates
    created_at: datetime = field(default_factory=datetime.now)
    last_deployed: Optional[datetime] = None
    
    # Score
    maturity_score: float = 0  # 0-100


@dataclass
class ServiceScore:
    """Оценка сервиса"""
    score_id: str
    service_id: str = ""
    
    # Categories
    documentation_score: float = 0
    monitoring_score: float = 0
    security_score: float = 0
    reliability_score: float = 0
    
    # Total
    total_score: float = 0
    
    # Last evaluated
    evaluated_at: datetime = field(default_factory=datetime.now)


class ServiceRegistry:
    """Реестр сервисов"""
    
    def __init__(self):
        self.services: Dict[str, Service] = {}
        self.dependencies: Dict[str, List[ServiceDependency]] = {}
        
    def register(self, service: Service) -> str:
        """Регистрация сервиса"""
        self.services[service.service_id] = service
        self.dependencies[service.service_id] = []
        return service.service_id
        
    def get(self, service_id: str) -> Optional[Service]:
        """Получение сервиса"""
        return self.services.get(service_id)
        
    def find_by_name(self, name: str) -> Optional[Service]:
        """Поиск по имени"""
        for service in self.services.values():
            if service.name == name:
                return service
        return None
        
    def add_dependency(self, from_id: str, to_id: str,
                      dep_type: str = "runtime", critical: bool = True):
        """Добавление зависимости"""
        dep = ServiceDependency(
            dep_id=f"dep_{uuid.uuid4().hex[:8]}",
            service_id=from_id,
            dependency_service_id=to_id,
            dependency_type=dep_type,
            is_critical=critical
        )
        
        if from_id not in self.dependencies:
            self.dependencies[from_id] = []
        self.dependencies[from_id].append(dep)
        
    def get_dependencies(self, service_id: str) -> List[Service]:
        """Получение зависимостей"""
        deps = self.dependencies.get(service_id, [])
        return [self.services[d.dependency_service_id] 
                for d in deps if d.dependency_service_id in self.services]
        
    def get_dependents(self, service_id: str) -> List[Service]:
        """Получение зависимых сервисов"""
        dependents = []
        for sid, deps in self.dependencies.items():
            for dep in deps:
                if dep.dependency_service_id == service_id:
                    if sid in self.services:
                        dependents.append(self.services[sid])
        return dependents


class ServiceScorer:
    """Оценщик сервисов"""
    
    def score(self, service: Service, deps_count: int = 0,
             dependents_count: int = 0) -> ServiceScore:
        """Оценка сервиса"""
        # Documentation score
        doc_score = 0
        if service.description:
            doc_score += 20
        if any(l.link_type == "docs" for l in service.links):
            doc_score += 30
        if any(l.link_type == "runbook" for l in service.links):
            doc_score += 25
        if any(l.link_type == "repo" for l in service.links):
            doc_score += 25
            
        # Monitoring score
        mon_score = 0
        if service.health_check_url:
            mon_score += 30
        if any(l.link_type == "dashboard" for l in service.links):
            mon_score += 30
        if service.metrics:
            mon_score += 40
            
        # Security score
        sec_score = 50  # Base score
        if service.owner:
            sec_score += 25
        if service.tier in [ServiceTier.TIER_0, ServiceTier.TIER_1]:
            sec_score += 25
            
        # Reliability score
        rel_score = 0
        if service.metrics and service.metrics.uptime_percent > 99.9:
            rel_score += 50
        elif service.metrics and service.metrics.uptime_percent > 99:
            rel_score += 30
        if service.lifecycle_status == LifecycleStatus.PRODUCTION:
            rel_score += 25
        if dependents_count > 0:
            rel_score += 25  # Has dependents = important
            
        total = (doc_score + mon_score + sec_score + rel_score) / 4
        
        return ServiceScore(
            score_id=f"score_{uuid.uuid4().hex[:8]}",
            service_id=service.service_id,
            documentation_score=doc_score,
            monitoring_score=mon_score,
            security_score=sec_score,
            reliability_score=rel_score,
            total_score=total
        )


class ServiceCatalogPlatform:
    """Платформа каталога сервисов"""
    
    def __init__(self):
        self.registry = ServiceRegistry()
        self.scorer = ServiceScorer()
        self.scores: Dict[str, ServiceScore] = {}
        self.owners: Dict[str, ServiceOwner] = {}
        
    def register_owner(self, name: str, email: str, team: str,
                      slack: str = "") -> ServiceOwner:
        """Регистрация владельца"""
        owner = ServiceOwner(
            owner_id=f"owner_{uuid.uuid4().hex[:8]}",
            name=name,
            email=email,
            team=team,
            slack_channel=slack
        )
        self.owners[owner.owner_id] = owner
        return owner
        
    def create_service(self, name: str, display_name: str,
                      service_type: ServiceType, tier: ServiceTier,
                      owner_id: str = "", language: str = "",
                      framework: str = "", description: str = "") -> Service:
        """Создание сервиса"""
        owner = self.owners.get(owner_id)
        
        service = Service(
            service_id=f"svc_{uuid.uuid4().hex[:8]}",
            name=name,
            display_name=display_name,
            description=description,
            service_type=service_type,
            tier=tier,
            owner=owner,
            language=language,
            framework=framework
        )
        
        self.registry.register(service)
        return service
        
    def add_endpoint(self, service_id: str, name: str, url: str,
                    protocol: str = "http", port: int = 80,
                    is_public: bool = False) -> Optional[ServiceEndpoint]:
        """Добавление эндпоинта"""
        service = self.registry.get(service_id)
        if not service:
            return None
            
        endpoint = ServiceEndpoint(
            endpoint_id=f"ep_{uuid.uuid4().hex[:8]}",
            name=name,
            url=url,
            protocol=protocol,
            port=port,
            is_public=is_public
        )
        
        service.endpoints.append(endpoint)
        return endpoint
        
    def add_link(self, service_id: str, title: str, url: str,
                link_type: str) -> Optional[ServiceLink]:
        """Добавление ссылки"""
        service = self.registry.get(service_id)
        if not service:
            return None
            
        link = ServiceLink(
            link_id=f"link_{uuid.uuid4().hex[:8]}",
            title=title,
            url=url,
            link_type=link_type
        )
        
        service.links.append(link)
        return link
        
    def add_dependency(self, from_service: str, to_service: str,
                      critical: bool = True):
        """Добавление зависимости"""
        self.registry.add_dependency(from_service, to_service, "runtime", critical)
        
    def set_health(self, service_id: str, status: HealthStatus,
                  health_url: str = ""):
        """Установка здоровья"""
        service = self.registry.get(service_id)
        if service:
            service.health_status = status
            if health_url:
                service.health_check_url = health_url
                
    def set_metrics(self, service_id: str, rps: float, p50: float,
                   p99: float, error_rate: float, uptime: float):
        """Установка метрик"""
        service = self.registry.get(service_id)
        if service:
            service.metrics = ServiceMetrics(
                requests_per_second=rps,
                latency_p50_ms=p50,
                latency_p99_ms=p99,
                error_rate=error_rate,
                uptime_percent=uptime
            )
            
    def score_service(self, service_id: str) -> Optional[ServiceScore]:
        """Оценка сервиса"""
        service = self.registry.get(service_id)
        if not service:
            return None
            
        deps = self.registry.get_dependencies(service_id)
        dependents = self.registry.get_dependents(service_id)
        
        score = self.scorer.score(service, len(deps), len(dependents))
        service.maturity_score = score.total_score
        self.scores[service_id] = score
        
        return score
        
    def search(self, query: str = "", service_type: ServiceType = None,
              tier: ServiceTier = None, tags: List[str] = None) -> List[Service]:
        """Поиск сервисов"""
        results = []
        
        for service in self.registry.services.values():
            match = True
            
            if query and query.lower() not in service.name.lower() and \
               query.lower() not in service.display_name.lower():
                match = False
                
            if service_type and service.service_type != service_type:
                match = False
                
            if tier and service.tier != tier:
                match = False
                
            if tags and not any(t in service.tags for t in tags):
                match = False
                
            if match:
                results.append(service)
                
        return results
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        services = list(self.registry.services.values())
        
        by_type = {}
        for s in services:
            t = s.service_type.value
            if t not in by_type:
                by_type[t] = 0
            by_type[t] += 1
            
        by_tier = {}
        for s in services:
            t = s.tier.value
            if t not in by_tier:
                by_tier[t] = 0
            by_tier[t] += 1
            
        healthy = len([s for s in services if s.health_status == HealthStatus.HEALTHY])
        
        return {
            "total_services": len(services),
            "by_type": by_type,
            "by_tier": by_tier,
            "healthy_services": healthy,
            "owners_registered": len(self.owners),
            "total_dependencies": sum(len(d) for d in self.registry.dependencies.values()),
            "avg_maturity_score": sum(s.maturity_score for s in services) / len(services) if services else 0
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 223: Service Catalog Platform")
    print("=" * 60)
    
    platform = ServiceCatalogPlatform()
    print("✓ Service Catalog Platform created")
    
    # Register owners
    print("\n👤 Registering Service Owners...")
    
    owners = [
        platform.register_owner("Platform Team", "platform@company.com", "Platform", "#platform"),
        platform.register_owner("Backend Team", "backend@company.com", "Backend", "#backend"),
        platform.register_owner("Frontend Team", "frontend@company.com", "Frontend", "#frontend"),
        platform.register_owner("Data Team", "data@company.com", "Data", "#data"),
    ]
    
    for owner in owners:
        print(f"  ✓ {owner.name} ({owner.team})")
        
    # Create services
    print("\n🔧 Creating Services...")
    
    services_config = [
        ("api-gateway", "API Gateway", ServiceType.GATEWAY, ServiceTier.TIER_0, owners[0].owner_id, "Go", "Gin"),
        ("user-service", "User Service", ServiceType.API, ServiceTier.TIER_1, owners[1].owner_id, "Python", "FastAPI"),
        ("order-service", "Order Service", ServiceType.API, ServiceTier.TIER_1, owners[1].owner_id, "Java", "Spring"),
        ("payment-service", "Payment Service", ServiceType.API, ServiceTier.TIER_0, owners[1].owner_id, "Go", "gRPC"),
        ("web-frontend", "Web Frontend", ServiceType.FRONTEND, ServiceTier.TIER_1, owners[2].owner_id, "TypeScript", "React"),
        ("postgres-main", "Main Database", ServiceType.DATABASE, ServiceTier.TIER_0, owners[3].owner_id, "SQL", "PostgreSQL"),
        ("redis-cache", "Redis Cache", ServiceType.CACHE, ServiceTier.TIER_1, owners[0].owner_id, "", "Redis"),
        ("kafka-events", "Event Bus", ServiceType.QUEUE, ServiceTier.TIER_1, owners[0].owner_id, "", "Kafka"),
    ]
    
    services = []
    for name, display, stype, tier, owner_id, lang, fw in services_config:
        service = platform.create_service(
            name, display, stype, tier, owner_id, lang, fw,
            f"{display} - Core platform service"
        )
        services.append(service)
        service.lifecycle_status = LifecycleStatus.PRODUCTION
        service.tags = [stype.value, tier.value]
        print(f"  ✓ {display}: {stype.value} ({tier.value})")
        
    # Add endpoints
    print("\n🔗 Adding Endpoints...")
    
    platform.add_endpoint(services[0].service_id, "HTTP", "https://api.example.com", "http", 443, True)
    platform.add_endpoint(services[1].service_id, "REST API", "http://user-service:8080", "http", 8080)
    platform.add_endpoint(services[2].service_id, "REST API", "http://order-service:8080", "http", 8080)
    platform.add_endpoint(services[3].service_id, "gRPC", "grpc://payment-service:9090", "grpc", 9090)
    print(f"  ✓ Added endpoints to services")
    
    # Add links
    print("\n📚 Adding Documentation Links...")
    
    for service in services:
        platform.add_link(service.service_id, "Repository", f"https://github.com/company/{service.name}", "repo")
        platform.add_link(service.service_id, "Documentation", f"https://docs.example.com/{service.name}", "docs")
        platform.add_link(service.service_id, "Dashboard", f"https://grafana.example.com/d/{service.name}", "dashboard")
        
    print(f"  ✓ Added links to {len(services)} services")
    
    # Add dependencies
    print("\n🔀 Adding Dependencies...")
    
    dependencies = [
        (services[0], services[1]),  # Gateway -> User
        (services[0], services[2]),  # Gateway -> Order
        (services[0], services[3]),  # Gateway -> Payment
        (services[1], services[5]),  # User -> Postgres
        (services[1], services[6]),  # User -> Redis
        (services[2], services[5]),  # Order -> Postgres
        (services[2], services[7]),  # Order -> Kafka
        (services[3], services[5]),  # Payment -> Postgres
        (services[4], services[0]),  # Frontend -> Gateway
    ]
    
    for from_svc, to_svc in dependencies:
        platform.add_dependency(from_svc.service_id, to_svc.service_id)
        print(f"  ✓ {from_svc.name} -> {to_svc.name}")
        
    # Set health
    print("\n💚 Setting Health Status...")
    
    health_statuses = [
        (HealthStatus.HEALTHY, 5),
        (HealthStatus.DEGRADED, 2),
        (HealthStatus.UNHEALTHY, 1),
    ]
    
    idx = 0
    for status, count in health_statuses:
        for _ in range(min(count, len(services) - idx)):
            platform.set_health(
                services[idx].service_id,
                status,
                f"http://{services[idx].name}:8080/health"
            )
            idx += 1
            
    print(f"  ✓ Set health for {len(services)} services")
    
    # Set metrics
    print("\n📊 Setting Metrics...")
    
    for service in services:
        platform.set_metrics(
            service.service_id,
            rps=random.uniform(100, 10000),
            p50=random.uniform(5, 50),
            p99=random.uniform(50, 500),
            error_rate=random.uniform(0, 2),
            uptime=random.uniform(99, 100)
        )
        
    print(f"  ✓ Set metrics for {len(services)} services")
    
    # Score services
    print("\n⭐ Scoring Services...")
    
    for service in services:
        score = platform.score_service(service.service_id)
        if score:
            stars = "★" * int(score.total_score / 20) + "☆" * (5 - int(score.total_score / 20))
            print(f"  {stars} {service.display_name}: {score.total_score:.0f}/100")
            
    # Display catalog
    print("\n📋 Service Catalog:")
    
    print("\n  ┌────────────────────┬────────────┬──────────┬──────────┬─────────┐")
    print("  │ Service            │ Type       │ Tier     │ Health   │ Score   │")
    print("  ├────────────────────┼────────────┼──────────┼──────────┼─────────┤")
    
    for service in platform.registry.services.values():
        name = service.display_name[:18].ljust(18)
        stype = service.service_type.value[:10].ljust(10)
        tier = service.tier.value[:8].ljust(8)
        
        health_icons = {
            HealthStatus.HEALTHY: "🟢",
            HealthStatus.DEGRADED: "🟡",
            HealthStatus.UNHEALTHY: "🔴",
            HealthStatus.UNKNOWN: "⚪"
        }
        health = f"{health_icons.get(service.health_status, '⚪')}"[:8].ljust(8)
        score = f"{service.maturity_score:.0f}"[:7].ljust(7)
        
        print(f"  │ {name} │ {stype} │ {tier} │ {health} │ {score} │")
        
    print("  └────────────────────┴────────────┴──────────┴──────────┴─────────┘")
    
    # Dependency graph
    print("\n🔀 Dependency Graph:")
    
    for service in services[:5]:
        deps = platform.registry.get_dependencies(service.service_id)
        if deps:
            dep_names = ", ".join(d.name for d in deps[:3])
            print(f"  {service.name} -> [{dep_names}]")
            
    # Services by type
    print("\n📊 Services by Type:")
    
    stats = platform.get_statistics()
    
    for stype, count in stats["by_type"].items():
        bar = "█" * count + "░" * (5 - count)
        print(f"  {stype:10s} [{bar}] {count}")
        
    # Services by tier
    print("\n🏷 Services by Tier:")
    
    tier_icons = {
        "tier_0": "🔴",
        "tier_1": "🟠",
        "tier_2": "🟡",
        "tier_3": "🟢"
    }
    
    for tier, count in stats["by_tier"].items():
        icon = tier_icons.get(tier, "⚪")
        bar = "█" * count + "░" * (5 - count)
        print(f"  {icon} {tier:8s} [{bar}] {count}")
        
    # Top scored services
    print("\n🏆 Top Scored Services:")
    
    sorted_services = sorted(
        platform.registry.services.values(),
        key=lambda s: s.maturity_score,
        reverse=True
    )
    
    for i, service in enumerate(sorted_services[:5], 1):
        score = service.maturity_score
        bar_len = int(score / 5)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        print(f"  {i}. {service.display_name:18s} [{bar}] {score:.0f}")
        
    # Owner statistics
    print("\n👤 Services by Owner:")
    
    by_owner = {}
    for service in platform.registry.services.values():
        owner = service.owner.team if service.owner else "Unassigned"
        if owner not in by_owner:
            by_owner[owner] = 0
        by_owner[owner] += 1
        
    for owner, count in sorted(by_owner.items(), key=lambda x: -x[1]):
        print(f"  {owner:15s}: {count} services")
        
    # Statistics
    print("\n📈 Catalog Statistics:")
    
    print(f"\n  Total Services: {stats['total_services']}")
    print(f"  Healthy: {stats['healthy_services']}")
    print(f"  Owners: {stats['owners_registered']}")
    print(f"  Dependencies: {stats['total_dependencies']}")
    print(f"  Avg Maturity: {stats['avg_maturity_score']:.1f}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                     Service Catalog Dashboard                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Services:                {stats['total_services']:>12}                        │")
    print(f"│ Healthy Services:              {stats['healthy_services']:>12}                        │")
    print(f"│ Dependencies Mapped:           {stats['total_dependencies']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Avg Maturity Score:              {stats['avg_maturity_score']:>10.1f}                   │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Service Catalog Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
