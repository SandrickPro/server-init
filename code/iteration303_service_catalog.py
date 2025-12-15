#!/usr/bin/env python3
"""
Server Init - Iteration 303: Service Catalog Platform
Платформа каталога сервисов

Функционал:
- Service Registry - реестр сервисов
- Service Metadata - метаданные сервисов
- Ownership Management - управление владельцами
- Dependency Mapping - картирование зависимостей
- SLA Definitions - определения SLA
- Cost Management - управление стоимостью
- Request Management - управление запросами
- Service Discovery - обнаружение сервисов
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid


class ServiceStatus(Enum):
    """Статус сервиса"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    RETIRED = "retired"
    PLANNED = "planned"
    MAINTENANCE = "maintenance"


class ServiceTier(Enum):
    """Уровень сервиса"""
    PLATINUM = "platinum"
    GOLD = "gold"
    SILVER = "silver"
    BRONZE = "bronze"


class ServiceCategory(Enum):
    """Категория сервиса"""
    INFRASTRUCTURE = "infrastructure"
    PLATFORM = "platform"
    APPLICATION = "application"
    DATA = "data"
    SECURITY = "security"
    COMMUNICATION = "communication"


class RequestStatus(Enum):
    """Статус запроса"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROVISIONING = "provisioning"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RequestType(Enum):
    """Тип запроса"""
    PROVISION = "provision"
    MODIFY = "modify"
    DECOMMISSION = "decommission"
    ACCESS = "access"


@dataclass
class Owner:
    """Владелец сервиса"""
    owner_id: str
    name: str
    email: str
    team: str
    
    # Responsibilities
    is_technical: bool = True
    is_business: bool = False
    
    # Contact
    slack_channel: str = ""
    on_call: bool = False


@dataclass
class SLADefinition:
    """Определение SLA"""
    sla_id: str
    name: str
    
    # Availability
    availability_target: float = 99.9  # %
    
    # Response times
    response_time_p50: int = 100  # ms
    response_time_p95: int = 500
    response_time_p99: int = 1000
    
    # Support
    support_hours: str = "24x7"
    response_sla: int = 15  # minutes
    resolution_sla: int = 240  # minutes
    
    # Penalties
    penalty_per_violation: float = 0.0


@dataclass
class ServiceCost:
    """Стоимость сервиса"""
    cost_id: str
    service_id: str
    
    # Monthly costs
    compute_cost: float = 0.0
    storage_cost: float = 0.0
    network_cost: float = 0.0
    license_cost: float = 0.0
    support_cost: float = 0.0
    
    # Usage
    cost_per_unit: float = 0.0
    unit_type: str = "request"  # request, user, gb
    
    # Allocation
    allocated_budget: float = 0.0


@dataclass
class ServiceDependency:
    """Зависимость сервиса"""
    dependency_id: str
    from_service_id: str
    to_service_id: str
    
    # Type
    dependency_type: str = "runtime"  # runtime, build, optional
    
    # Criticality
    is_critical: bool = True
    
    # Version
    required_version: str = ""


@dataclass
class ServiceEndpoint:
    """Эндпоинт сервиса"""
    endpoint_id: str
    service_id: str
    
    # Endpoint
    url: str = ""
    protocol: str = "http"  # http, grpc, websocket
    
    # Environment
    environment: str = "production"
    
    # Health
    health_url: str = ""
    is_healthy: bool = True


@dataclass
class Service:
    """Сервис"""
    service_id: str
    name: str
    description: str
    
    # Classification
    category: ServiceCategory = ServiceCategory.APPLICATION
    tier: ServiceTier = ServiceTier.SILVER
    status: ServiceStatus = ServiceStatus.ACTIVE
    
    # Ownership
    owners: List[str] = field(default_factory=list)  # owner_ids
    team: str = ""
    
    # Technical
    version: str = "1.0.0"
    repository: str = ""
    documentation_url: str = ""
    
    # SLA
    sla_id: Optional[str] = None
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)  # dependency_ids
    dependents: List[str] = field(default_factory=list)
    
    # Endpoints
    endpoints: List[str] = field(default_factory=list)  # endpoint_ids
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ServiceRequest:
    """Запрос на сервис"""
    request_id: str
    service_id: str
    requester_id: str
    
    # Type
    request_type: RequestType = RequestType.PROVISION
    
    # Details
    details: Dict[str, Any] = field(default_factory=dict)
    justification: str = ""
    
    # Status
    status: RequestStatus = RequestStatus.PENDING
    
    # Approval
    approvers: List[str] = field(default_factory=list)
    approved_by: Optional[str] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class ServiceCatalogManager:
    """Менеджер Service Catalog"""
    
    def __init__(self):
        self.services: Dict[str, Service] = {}
        self.owners: Dict[str, Owner] = {}
        self.slas: Dict[str, SLADefinition] = {}
        self.costs: Dict[str, ServiceCost] = {}
        self.dependencies: Dict[str, ServiceDependency] = {}
        self.endpoints: Dict[str, ServiceEndpoint] = {}
        self.requests: Dict[str, ServiceRequest] = {}
        
    async def register_owner(self, name: str, email: str,
                            team: str) -> Owner:
        """Регистрация владельца"""
        owner = Owner(
            owner_id=f"own_{uuid.uuid4().hex[:8]}",
            name=name,
            email=email,
            team=team
        )
        
        self.owners[owner.owner_id] = owner
        return owner
        
    async def create_sla(self, name: str,
                        availability: float = 99.9,
                        response_time_p95: int = 500) -> SLADefinition:
        """Создание SLA"""
        sla = SLADefinition(
            sla_id=f"sla_{uuid.uuid4().hex[:8]}",
            name=name,
            availability_target=availability,
            response_time_p95=response_time_p95
        )
        
        self.slas[sla.sla_id] = sla
        return sla
        
    async def register_service(self, name: str, description: str,
                              category: ServiceCategory,
                              tier: ServiceTier = ServiceTier.SILVER,
                              team: str = "",
                              sla_id: Optional[str] = None) -> Service:
        """Регистрация сервиса"""
        service = Service(
            service_id=f"svc_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            category=category,
            tier=tier,
            team=team,
            sla_id=sla_id
        )
        
        self.services[service.service_id] = service
        return service
        
    async def set_service_owner(self, service_id: str,
                               owner_id: str) -> bool:
        """Установка владельца сервиса"""
        service = self.services.get(service_id)
        owner = self.owners.get(owner_id)
        
        if not service or not owner:
            return False
            
        if owner_id not in service.owners:
            service.owners.append(owner_id)
            service.updated_at = datetime.now()
            
        return True
        
    async def add_dependency(self, from_service_id: str,
                            to_service_id: str,
                            dependency_type: str = "runtime",
                            is_critical: bool = True) -> Optional[ServiceDependency]:
        """Добавление зависимости"""
        from_service = self.services.get(from_service_id)
        to_service = self.services.get(to_service_id)
        
        if not from_service or not to_service:
            return None
            
        dependency = ServiceDependency(
            dependency_id=f"dep_{uuid.uuid4().hex[:8]}",
            from_service_id=from_service_id,
            to_service_id=to_service_id,
            dependency_type=dependency_type,
            is_critical=is_critical
        )
        
        self.dependencies[dependency.dependency_id] = dependency
        from_service.dependencies.append(dependency.dependency_id)
        to_service.dependents.append(dependency.dependency_id)
        
        return dependency
        
    async def add_endpoint(self, service_id: str,
                          url: str,
                          protocol: str = "http",
                          environment: str = "production") -> Optional[ServiceEndpoint]:
        """Добавление эндпоинта"""
        service = self.services.get(service_id)
        if not service:
            return None
            
        endpoint = ServiceEndpoint(
            endpoint_id=f"ep_{uuid.uuid4().hex[:8]}",
            service_id=service_id,
            url=url,
            protocol=protocol,
            environment=environment
        )
        
        self.endpoints[endpoint.endpoint_id] = endpoint
        service.endpoints.append(endpoint.endpoint_id)
        
        return endpoint
        
    async def set_service_cost(self, service_id: str,
                              compute: float = 0.0,
                              storage: float = 0.0,
                              network: float = 0.0) -> Optional[ServiceCost]:
        """Установка стоимости сервиса"""
        service = self.services.get(service_id)
        if not service:
            return None
            
        cost = ServiceCost(
            cost_id=f"cost_{uuid.uuid4().hex[:8]}",
            service_id=service_id,
            compute_cost=compute,
            storage_cost=storage,
            network_cost=network
        )
        
        self.costs[service_id] = cost
        return cost
        
    async def create_request(self, service_id: str,
                            requester_id: str,
                            request_type: RequestType,
                            justification: str = "") -> Optional[ServiceRequest]:
        """Создание запроса на сервис"""
        service = self.services.get(service_id)
        if not service:
            return None
            
        request = ServiceRequest(
            request_id=f"req_{uuid.uuid4().hex[:8]}",
            service_id=service_id,
            requester_id=requester_id,
            request_type=request_type,
            justification=justification,
            approvers=service.owners.copy()
        )
        
        self.requests[request.request_id] = request
        return request
        
    async def approve_request(self, request_id: str,
                             approver_id: str) -> bool:
        """Одобрение запроса"""
        request = self.requests.get(request_id)
        if not request:
            return False
            
        if request.status != RequestStatus.PENDING:
            return False
            
        if approver_id not in request.approvers:
            return False
            
        request.status = RequestStatus.APPROVED
        request.approved_by = approver_id
        
        return True
        
    async def complete_request(self, request_id: str) -> bool:
        """Завершение запроса"""
        request = self.requests.get(request_id)
        if not request:
            return False
            
        if request.status != RequestStatus.APPROVED:
            return False
            
        request.status = RequestStatus.COMPLETED
        request.completed_at = datetime.now()
        
        return True
        
    async def search_services(self, query: str = "",
                             category: Optional[ServiceCategory] = None,
                             tier: Optional[ServiceTier] = None,
                             status: Optional[ServiceStatus] = None,
                             tags: List[str] = None) -> List[Service]:
        """Поиск сервисов"""
        results = []
        
        for service in self.services.values():
            # Filter by status
            if status and service.status != status:
                continue
                
            # Filter by category
            if category and service.category != category:
                continue
                
            # Filter by tier
            if tier and service.tier != tier:
                continue
                
            # Filter by query
            if query:
                query_lower = query.lower()
                if (query_lower not in service.name.lower() and
                    query_lower not in service.description.lower()):
                    continue
                    
            # Filter by tags
            if tags:
                if not any(t in service.tags for t in tags):
                    continue
                    
            results.append(service)
            
        return results
        
    def get_service_dependencies(self, service_id: str,
                                 depth: int = 3) -> Dict[str, Any]:
        """Получение дерева зависимостей"""
        service = self.services.get(service_id)
        if not service:
            return {}
            
        def build_tree(svc_id: str, current_depth: int, visited: Set[str]) -> Dict:
            if current_depth > depth or svc_id in visited:
                return {}
                
            visited.add(svc_id)
            svc = self.services.get(svc_id)
            if not svc:
                return {}
                
            deps = []
            for dep_id in svc.dependencies:
                dep = self.dependencies.get(dep_id)
                if dep:
                    child_tree = build_tree(dep.to_service_id, current_depth + 1, visited.copy())
                    dep_svc = self.services.get(dep.to_service_id)
                    deps.append({
                        "service_id": dep.to_service_id,
                        "name": dep_svc.name if dep_svc else "Unknown",
                        "type": dep.dependency_type,
                        "critical": dep.is_critical,
                        "dependencies": child_tree.get("dependencies", [])
                    })
                    
            return {
                "service_id": svc_id,
                "name": svc.name,
                "dependencies": deps
            }
            
        return build_tree(service_id, 0, set())
        
    def get_service_dependents(self, service_id: str) -> List[Service]:
        """Получение сервисов, зависящих от данного"""
        service = self.services.get(service_id)
        if not service:
            return []
            
        dependents = []
        for dep_id in service.dependents:
            dep = self.dependencies.get(dep_id)
            if dep:
                from_service = self.services.get(dep.from_service_id)
                if from_service:
                    dependents.append(from_service)
                    
        return dependents
        
    def calculate_service_cost(self, service_id: str) -> float:
        """Расчёт полной стоимости сервиса"""
        cost = self.costs.get(service_id)
        if not cost:
            return 0.0
            
        return (cost.compute_cost + cost.storage_cost + 
                cost.network_cost + cost.license_cost + cost.support_cost)
                
    def get_service_details(self, service_id: str) -> Dict[str, Any]:
        """Получение деталей сервиса"""
        service = self.services.get(service_id)
        if not service:
            return {}
            
        owners = [self.owners.get(o) for o in service.owners if self.owners.get(o)]
        sla = self.slas.get(service.sla_id) if service.sla_id else None
        cost = self.costs.get(service_id)
        endpoints = [self.endpoints.get(e) for e in service.endpoints if self.endpoints.get(e)]
        
        return {
            "service_id": service_id,
            "name": service.name,
            "description": service.description,
            "category": service.category.value,
            "tier": service.tier.value,
            "status": service.status.value,
            "version": service.version,
            "team": service.team,
            "owners": [{"name": o.name, "email": o.email, "team": o.team} for o in owners],
            "sla": {
                "name": sla.name,
                "availability": sla.availability_target,
                "response_time_p95": sla.response_time_p95
            } if sla else None,
            "monthly_cost": self.calculate_service_cost(service_id),
            "endpoints": [{"url": e.url, "protocol": e.protocol, "environment": e.environment} for e in endpoints],
            "dependency_count": len(service.dependencies),
            "dependent_count": len(service.dependents),
            "tags": service.tags
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика каталога"""
        by_category = {}
        by_tier = {}
        by_status = {}
        
        total_cost = 0.0
        
        for service in self.services.values():
            by_category[service.category.value] = by_category.get(service.category.value, 0) + 1
            by_tier[service.tier.value] = by_tier.get(service.tier.value, 0) + 1
            by_status[service.status.value] = by_status.get(service.status.value, 0) + 1
            total_cost += self.calculate_service_cost(service.service_id)
            
        pending_requests = sum(1 for r in self.requests.values() if r.status == RequestStatus.PENDING)
        
        return {
            "total_services": len(self.services),
            "by_category": by_category,
            "by_tier": by_tier,
            "by_status": by_status,
            "total_owners": len(self.owners),
            "total_slas": len(self.slas),
            "total_dependencies": len(self.dependencies),
            "total_endpoints": len(self.endpoints),
            "total_requests": len(self.requests),
            "pending_requests": pending_requests,
            "total_monthly_cost": total_cost
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 303: Service Catalog Platform")
    print("=" * 60)
    
    manager = ServiceCatalogManager()
    print("✓ Service Catalog Manager created")
    
    # Create SLAs
    print("\n📊 Creating SLA Definitions...")
    
    slas_data = [
        ("Platinum SLA", 99.99, 100),
        ("Gold SLA", 99.95, 250),
        ("Silver SLA", 99.9, 500),
        ("Bronze SLA", 99.5, 1000)
    ]
    
    slas = {}
    for name, availability, response_time in slas_data:
        sla = await manager.create_sla(name, availability, response_time)
        slas[name.split()[0].lower()] = sla
        print(f"  📊 {name}: {availability}% availability, p95 {response_time}ms")
        
    # Register owners
    print("\n👤 Registering Owners...")
    
    owners_data = [
        ("Alice Smith", "alice@company.com", "Platform Team"),
        ("Bob Johnson", "bob@company.com", "Infrastructure Team"),
        ("Carol Williams", "carol@company.com", "Application Team"),
        ("David Brown", "david@company.com", "Data Team"),
        ("Eve Davis", "eve@company.com", "Security Team")
    ]
    
    owners = []
    for name, email, team in owners_data:
        owner = await manager.register_owner(name, email, team)
        owners.append(owner)
        print(f"  👤 {name} ({team})")
        
    # Register services
    print("\n🔧 Registering Services...")
    
    services_data = [
        ("API Gateway", "Central API gateway for all services", ServiceCategory.INFRASTRUCTURE, ServiceTier.PLATINUM, "Platform Team"),
        ("User Service", "User management and authentication", ServiceCategory.APPLICATION, ServiceTier.GOLD, "Application Team"),
        ("Order Service", "Order processing and management", ServiceCategory.APPLICATION, ServiceTier.GOLD, "Application Team"),
        ("Payment Service", "Payment processing integration", ServiceCategory.APPLICATION, ServiceTier.PLATINUM, "Application Team"),
        ("Notification Service", "Email and push notifications", ServiceCategory.COMMUNICATION, ServiceTier.SILVER, "Platform Team"),
        ("Analytics Service", "Business analytics and reporting", ServiceCategory.DATA, ServiceTier.SILVER, "Data Team"),
        ("Cache Service", "Distributed caching layer", ServiceCategory.INFRASTRUCTURE, ServiceTier.GOLD, "Infrastructure Team"),
        ("Search Service", "Full-text search functionality", ServiceCategory.DATA, ServiceTier.SILVER, "Data Team"),
        ("Auth Service", "OAuth2/OIDC authentication", ServiceCategory.SECURITY, ServiceTier.PLATINUM, "Security Team"),
        ("File Storage", "Cloud file storage service", ServiceCategory.INFRASTRUCTURE, ServiceTier.GOLD, "Infrastructure Team"),
        ("Message Queue", "Async message broker", ServiceCategory.INFRASTRUCTURE, ServiceTier.GOLD, "Infrastructure Team"),
        ("Database Service", "Primary PostgreSQL database", ServiceCategory.DATA, ServiceTier.PLATINUM, "Data Team")
    ]
    
    services = []
    for name, desc, category, tier, team in services_data:
        sla = slas.get(tier.value.lower())
        service = await manager.register_service(name, desc, category, tier, team, sla.sla_id if sla else None)
        service.tags = [category.value, tier.value, "production"]
        services.append(service)
        print(f"  🔧 {name} [{category.value}] - {tier.value}")
        
    # Set owners
    print("\n👥 Assigning Owners...")
    
    for i, service in enumerate(services):
        owner = owners[i % len(owners)]
        await manager.set_service_owner(service.service_id, owner.owner_id)
        
    print(f"  ✓ Assigned owners to {len(services)} services")
    
    # Add dependencies
    print("\n🔗 Adding Dependencies...")
    
    # API Gateway depends on Auth
    await manager.add_dependency(services[0].service_id, services[8].service_id, "runtime", True)
    # User Service depends on Cache, Database
    await manager.add_dependency(services[1].service_id, services[6].service_id, "runtime", False)
    await manager.add_dependency(services[1].service_id, services[11].service_id, "runtime", True)
    # Order Service depends on User, Payment, Database
    await manager.add_dependency(services[2].service_id, services[1].service_id, "runtime", True)
    await manager.add_dependency(services[2].service_id, services[3].service_id, "runtime", True)
    await manager.add_dependency(services[2].service_id, services[11].service_id, "runtime", True)
    # Payment Service depends on Auth
    await manager.add_dependency(services[3].service_id, services[8].service_id, "runtime", True)
    # Notification Service depends on Message Queue
    await manager.add_dependency(services[4].service_id, services[10].service_id, "runtime", True)
    # Analytics depends on Database, Cache
    await manager.add_dependency(services[5].service_id, services[11].service_id, "runtime", True)
    await manager.add_dependency(services[5].service_id, services[6].service_id, "runtime", False)
    # Search depends on Database
    await manager.add_dependency(services[7].service_id, services[11].service_id, "runtime", True)
    
    print(f"  ✓ Added {len(manager.dependencies)} dependencies")
    
    # Add endpoints
    print("\n🌐 Adding Endpoints...")
    
    for service in services:
        # Production endpoint
        await manager.add_endpoint(
            service.service_id,
            f"https://{service.name.lower().replace(' ', '-')}.prod.company.com/api/v1",
            "http",
            "production"
        )
        # Staging endpoint
        await manager.add_endpoint(
            service.service_id,
            f"https://{service.name.lower().replace(' ', '-')}.staging.company.com/api/v1",
            "http",
            "staging"
        )
        
    print(f"  ✓ Added {len(manager.endpoints)} endpoints")
    
    # Set costs
    print("\n💰 Setting Service Costs...")
    
    for service in services:
        compute = random.uniform(500, 5000)
        storage = random.uniform(100, 1000)
        network = random.uniform(50, 500)
        await manager.set_service_cost(service.service_id, compute, storage, network)
        
    print(f"  ✓ Set costs for {len(services)} services")
    
    # Search services
    print("\n🔍 Searching Services...")
    
    # Search by category
    infra_services = await manager.search_services(category=ServiceCategory.INFRASTRUCTURE)
    print(f"  Infrastructure services: {len(infra_services)}")
    
    # Search by tier
    platinum_services = await manager.search_services(tier=ServiceTier.PLATINUM)
    print(f"  Platinum tier services: {len(platinum_services)}")
    
    # Search by query
    search_results = await manager.search_services(query="service")
    print(f"  Services matching 'service': {len(search_results)}")
    
    # Service details
    print("\n📋 Service Details:")
    
    for service in services[:4]:
        details = manager.get_service_details(service.service_id)
        
        print(f"\n  📋 {details['name']}")
        print(f"     Category: {details['category']} | Tier: {details['tier']}")
        print(f"     Status: {details['status']} | Team: {details['team']}")
        
        if details['sla']:
            print(f"     SLA: {details['sla']['name']} ({details['sla']['availability']}%)")
            
        print(f"     Cost: ${details['monthly_cost']:,.2f}/month")
        print(f"     Dependencies: {details['dependency_count']} | Dependents: {details['dependent_count']}")
        
    # Dependency tree
    print("\n🌳 Dependency Trees:")
    
    order_service = services[2]  # Order Service
    tree = manager.get_service_dependencies(order_service.service_id)
    
    def print_tree(node: Dict, indent: int = 2):
        prefix = "  " * indent
        print(f"{prefix}└─ {node['name']}")
        for dep in node.get('dependencies', []):
            critical = "🔴" if dep.get('critical') else "🟡"
            print(f"{prefix}   {critical} {dep['name']} ({dep['type']})")
            for sub_dep in dep.get('dependencies', []):
                print(f"{prefix}      └─ {sub_dep['name']}")
                
    print(f"\n  {tree['name']}")
    for dep in tree.get('dependencies', []):
        critical = "🔴" if dep.get('critical') else "🟡"
        print(f"    {critical} {dep['name']} ({dep['type']})")
        for sub_dep in dep.get('dependencies', []):
            print(f"       └─ {sub_dep['name']}")
            
    # Service dependents
    print("\n👥 Service Dependents (Database Service):")
    
    db_service = services[11]  # Database Service
    dependents = manager.get_service_dependents(db_service.service_id)
    
    for dep in dependents:
        print(f"  📦 {dep.name} ({dep.tier.value})")
        
    # Create service requests
    print("\n📝 Creating Service Requests...")
    
    requests_data = [
        (services[1], owners[2], RequestType.ACCESS, "Need access for new team member"),
        (services[3], owners[1], RequestType.MODIFY, "Increase rate limit for peak season"),
        (services[5], owners[3], RequestType.PROVISION, "New analytics dashboard"),
        (services[6], owners[0], RequestType.MODIFY, "Expand cache cluster")
    ]
    
    requests = []
    for service, requester, req_type, justification in requests_data:
        request = await manager.create_request(
            service.service_id,
            requester.owner_id,
            req_type,
            justification
        )
        requests.append(request)
        print(f"  📝 {service.name}: {req_type.value} - {requester.name}")
        
    # Approve and complete some requests
    print("\n✅ Processing Requests...")
    
    for i, request in enumerate(requests[:2]):
        if request.approvers:
            await manager.approve_request(request.request_id, request.approvers[0])
            await manager.complete_request(request.request_id)
            service = manager.services.get(request.service_id)
            print(f"  ✅ {service.name if service else 'Unknown'}: {request.request_type.value} completed")
            
    # Service catalog display
    print("\n📋 Service Catalog:")
    
    print("\n  ┌──────────────────────────┬──────────────────┬──────────┬──────────┬────────────┐")
    print("  │ Service                  │ Category         │ Tier     │ Status   │ Cost/mo    │")
    print("  ├──────────────────────────┼──────────────────┼──────────┼──────────┼────────────┤")
    
    for service in services:
        name = service.name[:24].ljust(24)
        category = service.category.value[:16].ljust(16)
        tier = service.tier.value[:8].ljust(8)
        
        status_icons = {"active": "🟢", "deprecated": "🟡", "retired": "🔴", "planned": "⚪", "maintenance": "🟠"}
        status = f"{status_icons.get(service.status.value, '⚪')} {service.status.value[:6]}".ljust(8)
        
        cost = manager.calculate_service_cost(service.service_id)
        cost_str = f"${cost:,.0f}".ljust(10)
        
        print(f"  │ {name} │ {category} │ {tier} │ {status} │ {cost_str} │")
        
    print("  └──────────────────────────┴──────────────────┴──────────┴──────────┴────────────┘")
    
    # Statistics
    print("\n📊 Catalog Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Total Services: {stats['total_services']}")
    
    print("\n  By Category:")
    for cat, count in stats['by_category'].items():
        print(f"    {cat}: {count}")
        
    print("\n  By Tier:")
    for tier, count in stats['by_tier'].items():
        bar = "█" * count + "░" * (6 - count)
        print(f"    {tier:12} [{bar}] {count}")
        
    print(f"\n  Total Owners: {stats['total_owners']}")
    print(f"  Total SLAs: {stats['total_slas']}")
    print(f"  Total Dependencies: {stats['total_dependencies']}")
    print(f"  Total Endpoints: {stats['total_endpoints']}")
    print(f"  Total Requests: {stats['total_requests']}")
    print(f"  Pending Requests: {stats['pending_requests']}")
    print(f"  Total Monthly Cost: ${stats['total_monthly_cost']:,.2f}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Service Catalog Dashboard                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Services:           {stats['total_services']:>12}                           │")
    print(f"│ Active Services:          {stats['by_status'].get('active', 0):>12}                           │")
    print(f"│ Total Endpoints:          {stats['total_endpoints']:>12}                           │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Monthly Cost:       ${stats['total_monthly_cost']:>11,.2f}                          │")
    print(f"│ Pending Requests:         {stats['pending_requests']:>12}                           │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Service Catalog Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
