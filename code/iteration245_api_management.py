#!/usr/bin/env python3
"""
Server Init - Iteration 245: API Management Platform
Платформа управления API

Функционал:
- API Lifecycle - жизненный цикл API
- API Documentation - документация API
- API Versioning - версионирование
- API Analytics - аналитика использования
- Developer Portal - портал разработчиков
- API Keys Management - управление ключами
- Usage Plans - планы использования
- API Monetization - монетизация
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import json


class APIStatus(Enum):
    """Статус API"""
    DRAFT = "draft"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


class APIType(Enum):
    """Тип API"""
    REST = "rest"
    GRAPHQL = "graphql"
    GRPC = "grpc"
    WEBSOCKET = "websocket"
    SOAP = "soap"


class PlanTier(Enum):
    """Уровень плана"""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class AuthMethod(Enum):
    """Метод аутентификации"""
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    JWT = "jwt"
    BASIC = "basic"
    NONE = "none"


@dataclass
class APIEndpoint:
    """Эндпоинт API"""
    endpoint_id: str
    path: str = ""
    method: str = "GET"
    
    # Description
    summary: str = ""
    description: str = ""
    
    # Parameters
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    request_body: Dict[str, Any] = field(default_factory=dict)
    responses: Dict[str, Dict] = field(default_factory=dict)
    
    # Options
    is_deprecated: bool = False
    tags: List[str] = field(default_factory=list)


@dataclass
class APIVersion:
    """Версия API"""
    version_id: str
    version: str = "1.0.0"
    
    # Endpoints
    endpoints: List[APIEndpoint] = field(default_factory=list)
    
    # Status
    status: APIStatus = APIStatus.DRAFT
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)
    published_at: Optional[datetime] = None
    deprecated_at: Optional[datetime] = None
    
    # Changelog
    changelog: str = ""


@dataclass
class API:
    """API"""
    api_id: str
    name: str = ""
    
    # Type
    api_type: APIType = APIType.REST
    
    # Auth
    auth_method: AuthMethod = AuthMethod.API_KEY
    
    # Versions
    versions: Dict[str, APIVersion] = field(default_factory=dict)
    current_version: str = ""
    
    # Metadata
    description: str = ""
    owner: str = ""
    team: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Base URL
    base_url: str = ""
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class UsagePlan:
    """План использования"""
    plan_id: str
    name: str = ""
    
    # Tier
    tier: PlanTier = PlanTier.FREE
    
    # Limits
    requests_per_second: int = 10
    requests_per_day: int = 1000
    requests_per_month: int = 30000
    
    # Quota
    burst_limit: int = 20
    
    # Features
    features: List[str] = field(default_factory=list)
    
    # Pricing
    price_monthly: float = 0.0
    price_per_request: float = 0.0
    
    # APIs included
    apis: List[str] = field(default_factory=list)


@dataclass
class APIKey:
    """API ключ"""
    key_id: str
    key_value: str = ""
    
    # Owner
    developer_id: str = ""
    application_name: str = ""
    
    # Plan
    plan_id: str = ""
    
    # Limits
    rate_limit: int = 100
    
    # Status
    is_active: bool = True
    
    # Usage
    total_requests: int = 0
    last_used: Optional[datetime] = None
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


@dataclass
class Developer:
    """Разработчик"""
    developer_id: str
    name: str = ""
    email: str = ""
    company: str = ""
    
    # API Keys
    api_keys: List[str] = field(default_factory=list)
    
    # Applications
    applications: List[str] = field(default_factory=list)
    
    # Plan
    plan_id: str = ""
    
    # Status
    is_verified: bool = False
    is_active: bool = True
    
    # Time
    registered_at: datetime = field(default_factory=datetime.now)


@dataclass
class APIUsageRecord:
    """Запись использования"""
    record_id: str
    
    # What
    api_id: str = ""
    endpoint_path: str = ""
    method: str = ""
    
    # Who
    api_key_id: str = ""
    developer_id: str = ""
    
    # Result
    status_code: int = 200
    latency_ms: float = 0
    
    # Time
    timestamp: datetime = field(default_factory=datetime.now)


class APIManagementPlatform:
    """Платформа управления API"""
    
    def __init__(self):
        self.apis: Dict[str, API] = {}
        self.usage_plans: Dict[str, UsagePlan] = {}
        self.api_keys: Dict[str, APIKey] = {}
        self.developers: Dict[str, Developer] = {}
        self.usage_records: List[APIUsageRecord] = []
        
        self._init_default_plans()
        
    def _init_default_plans(self):
        """Инициализация планов по умолчанию"""
        plans = [
            UsagePlan(
                plan_id="plan_free",
                name="Free",
                tier=PlanTier.FREE,
                requests_per_second=5,
                requests_per_day=500,
                requests_per_month=10000,
                features=["Basic support", "API documentation"]
            ),
            UsagePlan(
                plan_id="plan_basic",
                name="Basic",
                tier=PlanTier.BASIC,
                requests_per_second=20,
                requests_per_day=5000,
                requests_per_month=100000,
                price_monthly=29.99,
                features=["Email support", "API documentation", "Analytics"]
            ),
            UsagePlan(
                plan_id="plan_pro",
                name="Professional",
                tier=PlanTier.PROFESSIONAL,
                requests_per_second=100,
                requests_per_day=50000,
                requests_per_month=1000000,
                price_monthly=99.99,
                features=["Priority support", "Advanced analytics", "Webhooks"]
            ),
            UsagePlan(
                plan_id="plan_enterprise",
                name="Enterprise",
                tier=PlanTier.ENTERPRISE,
                requests_per_second=1000,
                requests_per_day=500000,
                requests_per_month=10000000,
                price_monthly=499.99,
                features=["Dedicated support", "SLA", "Custom limits", "SSO"]
            )
        ]
        
        for plan in plans:
            self.usage_plans[plan.plan_id] = plan
            
    def create_api(self, name: str, api_type: APIType = APIType.REST,
                  auth_method: AuthMethod = AuthMethod.API_KEY,
                  description: str = "", owner: str = "",
                  base_url: str = "") -> API:
        """Создание API"""
        api = API(
            api_id=f"api_{uuid.uuid4().hex[:8]}",
            name=name,
            api_type=api_type,
            auth_method=auth_method,
            description=description,
            owner=owner,
            base_url=base_url or f"https://api.example.com/{name.lower()}"
        )
        
        self.apis[api.api_id] = api
        return api
        
    def create_version(self, api_id: str, version: str,
                      changelog: str = "") -> Optional[APIVersion]:
        """Создание версии API"""
        api = self.apis.get(api_id)
        if not api:
            return None
            
        ver = APIVersion(
            version_id=f"ver_{uuid.uuid4().hex[:8]}",
            version=version,
            changelog=changelog
        )
        
        api.versions[version] = ver
        
        if not api.current_version:
            api.current_version = version
            
        return ver
        
    def add_endpoint(self, api_id: str, version: str,
                    path: str, method: str = "GET",
                    summary: str = "", description: str = "",
                    tags: List[str] = None) -> Optional[APIEndpoint]:
        """Добавление эндпоинта"""
        api = self.apis.get(api_id)
        if not api or version not in api.versions:
            return None
            
        endpoint = APIEndpoint(
            endpoint_id=f"ep_{uuid.uuid4().hex[:8]}",
            path=path,
            method=method,
            summary=summary,
            description=description,
            tags=tags or []
        )
        
        api.versions[version].endpoints.append(endpoint)
        return endpoint
        
    def publish_version(self, api_id: str, version: str) -> bool:
        """Публикация версии"""
        api = self.apis.get(api_id)
        if not api or version not in api.versions:
            return False
            
        ver = api.versions[version]
        ver.status = APIStatus.PUBLISHED
        ver.published_at = datetime.now()
        api.current_version = version
        
        return True
        
    def deprecate_version(self, api_id: str, version: str) -> bool:
        """Депрекация версии"""
        api = self.apis.get(api_id)
        if not api or version not in api.versions:
            return False
            
        ver = api.versions[version]
        ver.status = APIStatus.DEPRECATED
        ver.deprecated_at = datetime.now()
        
        return True
        
    def register_developer(self, name: str, email: str,
                          company: str = "") -> Developer:
        """Регистрация разработчика"""
        developer = Developer(
            developer_id=f"dev_{uuid.uuid4().hex[:8]}",
            name=name,
            email=email,
            company=company,
            plan_id="plan_free"
        )
        
        self.developers[developer.developer_id] = developer
        return developer
        
    def create_api_key(self, developer_id: str, application_name: str,
                      plan_id: str = None) -> Optional[APIKey]:
        """Создание API ключа"""
        developer = self.developers.get(developer_id)
        if not developer:
            return None
            
        plan = self.usage_plans.get(plan_id or developer.plan_id)
        
        key = APIKey(
            key_id=f"key_{uuid.uuid4().hex[:8]}",
            key_value=f"sk_{uuid.uuid4().hex}",
            developer_id=developer_id,
            application_name=application_name,
            plan_id=plan.plan_id if plan else "plan_free",
            rate_limit=plan.requests_per_second if plan else 10
        )
        
        self.api_keys[key.key_id] = key
        developer.api_keys.append(key.key_id)
        
        return key
        
    def record_usage(self, api_id: str, endpoint_path: str,
                    method: str, api_key_id: str,
                    status_code: int = 200, latency_ms: float = 0):
        """Запись использования"""
        key = self.api_keys.get(api_key_id)
        
        record = APIUsageRecord(
            record_id=f"rec_{uuid.uuid4().hex[:8]}",
            api_id=api_id,
            endpoint_path=endpoint_path,
            method=method,
            api_key_id=api_key_id,
            developer_id=key.developer_id if key else "",
            status_code=status_code,
            latency_ms=latency_ms
        )
        
        self.usage_records.append(record)
        
        if key:
            key.total_requests += 1
            key.last_used = datetime.now()
            
    def get_api_analytics(self, api_id: str,
                         days: int = 7) -> Dict[str, Any]:
        """Аналитика API"""
        cutoff = datetime.now() - timedelta(days=days)
        
        records = [r for r in self.usage_records
                  if r.api_id == api_id and r.timestamp > cutoff]
                  
        if not records:
            return {"total_requests": 0}
            
        # Calculate metrics
        total = len(records)
        successful = sum(1 for r in records if 200 <= r.status_code < 300)
        errors = sum(1 for r in records if r.status_code >= 400)
        avg_latency = sum(r.latency_ms for r in records) / total
        
        # By endpoint
        by_endpoint: Dict[str, int] = {}
        for r in records:
            key = f"{r.method} {r.endpoint_path}"
            by_endpoint[key] = by_endpoint.get(key, 0) + 1
            
        # By status
        by_status: Dict[int, int] = {}
        for r in records:
            by_status[r.status_code] = by_status.get(r.status_code, 0) + 1
            
        return {
            "total_requests": total,
            "successful_requests": successful,
            "error_requests": errors,
            "success_rate": successful / total * 100 if total > 0 else 0,
            "avg_latency_ms": avg_latency,
            "by_endpoint": by_endpoint,
            "by_status": by_status
        }
        
    def generate_openapi_spec(self, api_id: str, version: str = None) -> Dict[str, Any]:
        """Генерация OpenAPI спецификации"""
        api = self.apis.get(api_id)
        if not api:
            return {}
            
        ver = api.versions.get(version or api.current_version)
        if not ver:
            return {}
            
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": api.name,
                "description": api.description,
                "version": ver.version
            },
            "servers": [{"url": api.base_url}],
            "paths": {}
        }
        
        for endpoint in ver.endpoints:
            if endpoint.path not in spec["paths"]:
                spec["paths"][endpoint.path] = {}
                
            spec["paths"][endpoint.path][endpoint.method.lower()] = {
                "summary": endpoint.summary,
                "description": endpoint.description,
                "tags": endpoint.tags,
                "responses": endpoint.responses or {"200": {"description": "Success"}}
            }
            
        return spec
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_endpoints = sum(
            len(ver.endpoints)
            for api in self.apis.values()
            for ver in api.versions.values()
        )
        
        published_apis = sum(
            1 for api in self.apis.values()
            if any(v.status == APIStatus.PUBLISHED for v in api.versions.values())
        )
        
        active_keys = sum(1 for k in self.api_keys.values() if k.is_active)
        
        return {
            "total_apis": len(self.apis),
            "published_apis": published_apis,
            "total_endpoints": total_endpoints,
            "total_developers": len(self.developers),
            "total_api_keys": len(self.api_keys),
            "active_api_keys": active_keys,
            "usage_plans": len(self.usage_plans),
            "total_requests": len(self.usage_records)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 245: API Management Platform")
    print("=" * 60)
    
    platform = APIManagementPlatform()
    print("✓ API Management Platform created")
    
    # Create APIs
    print("\n🔌 Creating APIs...")
    
    apis_data = [
        ("Users API", APIType.REST, "User management and authentication"),
        ("Orders API", APIType.REST, "Order processing and management"),
        ("Products API", APIType.REST, "Product catalog"),
        ("Analytics API", APIType.REST, "Business analytics and reporting"),
        ("Notifications API", APIType.WEBSOCKET, "Real-time notifications"),
    ]
    
    apis = []
    for name, api_type, desc in apis_data:
        api = platform.create_api(name, api_type, AuthMethod.API_KEY, desc, "platform-team")
        apis.append(api)
        print(f"  🔌 {name} ({api_type.value})")
        
    # Create versions and endpoints
    print("\n📋 Adding Versions and Endpoints...")
    
    for api in apis:
        # Create v1
        v1 = platform.create_version(api.api_id, "1.0.0", "Initial release")
        
        # Add endpoints
        endpoints = [
            (f"/{api.name.split()[0].lower()}", "GET", f"List all {api.name.split()[0].lower()}"),
            (f"/{api.name.split()[0].lower()}/{{id}}", "GET", f"Get {api.name.split()[0].lower()} by ID"),
            (f"/{api.name.split()[0].lower()}", "POST", f"Create new {api.name.split()[0].lower()}"),
            (f"/{api.name.split()[0].lower()}/{{id}}", "PUT", f"Update {api.name.split()[0].lower()}"),
            (f"/{api.name.split()[0].lower()}/{{id}}", "DELETE", f"Delete {api.name.split()[0].lower()}"),
        ]
        
        for path, method, summary in endpoints:
            platform.add_endpoint(api.api_id, "1.0.0", path, method, summary)
            
        # Publish
        platform.publish_version(api.api_id, "1.0.0")
        
        print(f"  ✓ {api.name} v1.0.0 - {len(endpoints)} endpoints")
        
    # Register developers
    print("\n👨‍💻 Registering Developers...")
    
    devs_data = [
        ("Alice Developer", "alice@example.com", "TechCorp"),
        ("Bob Builder", "bob@example.com", "BuildInc"),
        ("Carol Coder", "carol@example.com", "CodeCo"),
        ("Dave Designer", "dave@example.com", "DesignStudio"),
    ]
    
    developers = []
    for name, email, company in devs_data:
        dev = platform.register_developer(name, email, company)
        developers.append(dev)
        print(f"  👨‍💻 {name} ({company})")
        
    # Create API keys
    print("\n🔑 Creating API Keys...")
    
    keys = []
    for dev in developers:
        key = platform.create_api_key(dev.developer_id, f"{dev.name}'s App")
        keys.append(key)
        print(f"  🔑 {key.key_value[:20]}... → {dev.name}")
        
    # Simulate usage
    print("\n📊 Simulating API Usage...")
    
    for _ in range(100):
        api = random.choice(apis)
        key = random.choice(keys)
        
        endpoints = ["/users", "/users/123", "/orders", "/products"]
        methods = ["GET", "POST", "PUT", "DELETE"]
        
        platform.record_usage(
            api.api_id,
            random.choice(endpoints),
            random.choice(methods),
            key.key_id,
            random.choice([200, 200, 200, 201, 400, 404, 500]),
            random.uniform(10, 200)
        )
        
    print("  ✓ Simulated 100 API calls")
    
    # Display APIs
    print("\n📊 API Summary:")
    
    print("\n  ┌───────────────────┬──────────┬──────────┬───────────┬──────────┐")
    print("  │ API               │ Type     │ Version  │ Endpoints │ Status   │")
    print("  ├───────────────────┼──────────┼──────────┼───────────┼──────────┤")
    
    for api in apis:
        name = api.name[:17].ljust(17)
        api_type = api.api_type.value[:8].ljust(8)
        version = api.current_version[:8].ljust(8)
        
        ver = api.versions.get(api.current_version)
        endpoints = str(len(ver.endpoints) if ver else 0)[:9].ljust(9)
        
        status = "🟢" if ver and ver.status == APIStatus.PUBLISHED else "🟡"
        
        print(f"  │ {name} │ {api_type} │ {version} │ {endpoints} │ {status:8s} │")
        
    print("  └───────────────────┴──────────┴──────────┴───────────┴──────────┘")
    
    # Display usage plans
    print("\n💰 Usage Plans:")
    
    print("\n  ┌────────────────┬──────────┬────────────┬───────────┬──────────┐")
    print("  │ Plan           │ RPS      │ Daily      │ Monthly   │ Price    │")
    print("  ├────────────────┼──────────┼────────────┼───────────┼──────────┤")
    
    for plan in platform.usage_plans.values():
        name = plan.name[:14].ljust(14)
        rps = str(plan.requests_per_second)[:8].ljust(8)
        daily = str(plan.requests_per_day)[:10].ljust(10)
        monthly = str(plan.requests_per_month)[:9].ljust(9)
        price = f"${plan.price_monthly:.0f}" if plan.price_monthly > 0 else "Free"
        price = price[:8].ljust(8)
        
        print(f"  │ {name} │ {rps} │ {daily} │ {monthly} │ {price} │")
        
    print("  └────────────────┴──────────┴────────────┴───────────┴──────────┘")
    
    # Analytics for first API
    print("\n📈 API Analytics (Users API):")
    
    analytics = platform.get_api_analytics(apis[0].api_id)
    
    print(f"\n  Total Requests: {analytics.get('total_requests', 0)}")
    print(f"  Success Rate: {analytics.get('success_rate', 0):.1f}%")
    print(f"  Avg Latency: {analytics.get('avg_latency_ms', 0):.1f}ms")
    
    # Top endpoints
    by_endpoint = analytics.get('by_endpoint', {})
    if by_endpoint:
        print("\n  Top Endpoints:")
        for ep, count in sorted(by_endpoint.items(), key=lambda x: -x[1])[:5]:
            print(f"    {ep}: {count} requests")
            
    # OpenAPI spec
    print("\n📄 OpenAPI Specification (preview):")
    
    spec = platform.generate_openapi_spec(apis[0].api_id)
    if spec:
        print(f"\n  Title: {spec['info']['title']}")
        print(f"  Version: {spec['info']['version']}")
        print(f"  Paths: {len(spec['paths'])}")
        
    # Statistics
    print("\n📊 Platform Statistics:")
    
    stats = platform.get_statistics()
    
    print(f"\n  Total APIs: {stats['total_apis']}")
    print(f"  Published APIs: {stats['published_apis']}")
    print(f"  Total Endpoints: {stats['total_endpoints']}")
    print(f"  Total Developers: {stats['total_developers']}")
    print(f"  Active API Keys: {stats['active_api_keys']}")
    print(f"  Total Requests: {stats['total_requests']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   API Management Dashboard                          │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total APIs:                    {stats['total_apis']:>12}                        │")
    print(f"│ Total Endpoints:               {stats['total_endpoints']:>12}                        │")
    print(f"│ Registered Developers:         {stats['total_developers']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Active API Keys:               {stats['active_api_keys']:>12}                        │")
    print(f"│ Total API Calls:               {stats['total_requests']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("API Management Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
