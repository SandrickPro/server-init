#!/usr/bin/env python3
"""
Server Init - Iteration 185: Multi-Tenancy Platform
Платформа мультитенантности

Функционал:
- Tenant Management - управление тенантами
- Isolation Strategies - стратегии изоляции
- Resource Quotas - квоты ресурсов
- Data Partitioning - партиционирование данных
- Tenant Routing - маршрутизация тенантов
- Billing Integration - интеграция биллинга
- Feature Toggles - переключатели функций
- Onboarding Workflows - процессы онбординга
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid


class TenantStatus(Enum):
    """Статус тенанта"""
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"
    DELETED = "deleted"


class IsolationLevel(Enum):
    """Уровень изоляции"""
    SHARED = "shared"  # Shared schema
    SCHEMA = "schema"  # Schema per tenant
    DATABASE = "database"  # Database per tenant
    CLUSTER = "cluster"  # Cluster per tenant


class PlanTier(Enum):
    """Уровень плана"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class FeatureFlag(Enum):
    """Флаги функций"""
    ADVANCED_ANALYTICS = "advanced_analytics"
    CUSTOM_BRANDING = "custom_branding"
    API_ACCESS = "api_access"
    SSO = "sso"
    DEDICATED_SUPPORT = "dedicated_support"
    CUSTOM_DOMAINS = "custom_domains"
    AUDIT_LOGS = "audit_logs"
    DATA_EXPORT = "data_export"


@dataclass
class ResourceQuota:
    """Квоты ресурсов"""
    quota_id: str
    tenant_id: str = ""
    
    # Storage
    storage_gb: int = 10
    storage_used_gb: float = 0.0
    
    # Users
    max_users: int = 5
    current_users: int = 0
    
    # API
    api_calls_per_month: int = 10000
    api_calls_used: int = 0
    
    # Projects
    max_projects: int = 3
    current_projects: int = 0
    
    @property
    def storage_percent(self) -> float:
        return (self.storage_used_gb / self.storage_gb) * 100 if self.storage_gb > 0 else 0
        
    @property
    def users_percent(self) -> float:
        return (self.current_users / self.max_users) * 100 if self.max_users > 0 else 0


@dataclass
class Tenant:
    """Тенант"""
    tenant_id: str
    name: str = ""
    slug: str = ""  # URL-friendly identifier
    
    # Contact
    admin_email: str = ""
    company_name: str = ""
    
    # Status
    status: TenantStatus = TenantStatus.PENDING
    
    # Plan
    plan_tier: PlanTier = PlanTier.FREE
    
    # Isolation
    isolation_level: IsolationLevel = IsolationLevel.SHARED
    
    # Features
    enabled_features: Set[FeatureFlag] = field(default_factory=set)
    
    # Quotas
    quotas: Optional[ResourceQuota] = None
    
    # Customization
    settings: Dict[str, Any] = field(default_factory=dict)
    branding: Dict[str, str] = field(default_factory=dict)
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    activated_at: Optional[datetime] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TenantUser:
    """Пользователь тенанта"""
    user_id: str
    tenant_id: str = ""
    
    # Info
    email: str = ""
    name: str = ""
    
    # Role
    role: str = "member"  # admin, member, viewer
    
    # Status
    active: bool = True
    
    # Timing
    joined_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None


@dataclass
class BillingInfo:
    """Биллинг информация"""
    billing_id: str
    tenant_id: str = ""
    
    # Plan
    plan_tier: PlanTier = PlanTier.FREE
    monthly_price: float = 0.0
    
    # Period
    billing_cycle_start: datetime = field(default_factory=datetime.now)
    billing_cycle_end: Optional[datetime] = None
    
    # Usage
    usage_charges: float = 0.0
    
    # Payment
    payment_method: str = ""
    last_payment: Optional[datetime] = None


@dataclass
class OnboardingStep:
    """Шаг онбординга"""
    step_id: str
    tenant_id: str = ""
    
    # Step info
    step_name: str = ""
    step_order: int = 0
    
    # Status
    completed: bool = False
    completed_at: Optional[datetime] = None
    
    # Metadata
    data: Dict[str, Any] = field(default_factory=dict)


class TenantManager:
    """Менеджер тенантов"""
    
    def __init__(self):
        self.tenants: Dict[str, Tenant] = {}
        self.users: Dict[str, List[TenantUser]] = {}
        
    async def create_tenant(self, name: str, admin_email: str, 
                           plan: PlanTier = PlanTier.FREE) -> Tenant:
        """Создание тенанта"""
        tenant_id = f"tenant_{uuid.uuid4().hex[:8]}"
        slug = name.lower().replace(" ", "-").replace("_", "-")
        
        # Define quotas based on plan
        quota_limits = {
            PlanTier.FREE: {"storage": 5, "users": 3, "api": 5000, "projects": 2},
            PlanTier.STARTER: {"storage": 25, "users": 10, "api": 50000, "projects": 10},
            PlanTier.PROFESSIONAL: {"storage": 100, "users": 50, "api": 500000, "projects": 50},
            PlanTier.ENTERPRISE: {"storage": 1000, "users": 500, "api": 5000000, "projects": -1},
        }
        
        limits = quota_limits[plan]
        
        quotas = ResourceQuota(
            quota_id=f"quota_{tenant_id}",
            tenant_id=tenant_id,
            storage_gb=limits["storage"],
            max_users=limits["users"],
            api_calls_per_month=limits["api"],
            max_projects=limits["projects"] if limits["projects"] > 0 else 999999
        )
        
        # Define features based on plan
        features = {FeatureFlag.DATA_EXPORT}
        if plan in [PlanTier.STARTER, PlanTier.PROFESSIONAL, PlanTier.ENTERPRISE]:
            features.add(FeatureFlag.API_ACCESS)
            features.add(FeatureFlag.CUSTOM_BRANDING)
        if plan in [PlanTier.PROFESSIONAL, PlanTier.ENTERPRISE]:
            features.add(FeatureFlag.ADVANCED_ANALYTICS)
            features.add(FeatureFlag.AUDIT_LOGS)
        if plan == PlanTier.ENTERPRISE:
            features.add(FeatureFlag.SSO)
            features.add(FeatureFlag.DEDICATED_SUPPORT)
            features.add(FeatureFlag.CUSTOM_DOMAINS)
            
        tenant = Tenant(
            tenant_id=tenant_id,
            name=name,
            slug=slug,
            admin_email=admin_email,
            plan_tier=plan,
            enabled_features=features,
            quotas=quotas,
            isolation_level=IsolationLevel.DATABASE if plan == PlanTier.ENTERPRISE else IsolationLevel.SHARED
        )
        
        self.tenants[tenant_id] = tenant
        self.users[tenant_id] = []
        
        return tenant
        
    async def activate_tenant(self, tenant_id: str) -> bool:
        """Активация тенанта"""
        tenant = self.tenants.get(tenant_id)
        if tenant and tenant.status == TenantStatus.PENDING:
            tenant.status = TenantStatus.ACTIVE
            tenant.activated_at = datetime.now()
            return True
        return False
        
    async def suspend_tenant(self, tenant_id: str, reason: str = "") -> bool:
        """Приостановка тенанта"""
        tenant = self.tenants.get(tenant_id)
        if tenant and tenant.status == TenantStatus.ACTIVE:
            tenant.status = TenantStatus.SUSPENDED
            tenant.metadata["suspension_reason"] = reason
            tenant.metadata["suspended_at"] = datetime.now().isoformat()
            return True
        return False
        
    def get_tenant_by_slug(self, slug: str) -> Optional[Tenant]:
        """Поиск по slug"""
        for tenant in self.tenants.values():
            if tenant.slug == slug:
                return tenant
        return None


class UserManager:
    """Менеджер пользователей"""
    
    def __init__(self, tenant_manager: TenantManager):
        self.tenant_manager = tenant_manager
        
    async def add_user(self, tenant_id: str, email: str, name: str, 
                      role: str = "member") -> Optional[TenantUser]:
        """Добавление пользователя"""
        tenant = self.tenant_manager.tenants.get(tenant_id)
        if not tenant or not tenant.quotas:
            return None
            
        # Check quota
        if tenant.quotas.current_users >= tenant.quotas.max_users:
            return None
            
        user = TenantUser(
            user_id=f"user_{uuid.uuid4().hex[:8]}",
            tenant_id=tenant_id,
            email=email,
            name=name,
            role=role
        )
        
        self.tenant_manager.users[tenant_id].append(user)
        tenant.quotas.current_users += 1
        
        return user
        
    def get_tenant_users(self, tenant_id: str) -> List[TenantUser]:
        """Получение пользователей"""
        return self.tenant_manager.users.get(tenant_id, [])


class TenantRouter:
    """Маршрутизатор тенантов"""
    
    def __init__(self, tenant_manager: TenantManager):
        self.tenant_manager = tenant_manager
        self.domain_mapping: Dict[str, str] = {}  # domain -> tenant_id
        
    def add_custom_domain(self, tenant_id: str, domain: str):
        """Добавление кастомного домена"""
        self.domain_mapping[domain] = tenant_id
        
    def resolve_tenant(self, request_host: str, request_path: str = "") -> Optional[str]:
        """Определение тенанта из запроса"""
        # Check custom domain
        if request_host in self.domain_mapping:
            return self.domain_mapping[request_host]
            
        # Check subdomain
        if "." in request_host:
            subdomain = request_host.split(".")[0]
            tenant = self.tenant_manager.get_tenant_by_slug(subdomain)
            if tenant:
                return tenant.tenant_id
                
        # Check path
        if request_path.startswith("/t/"):
            slug = request_path.split("/")[2] if len(request_path.split("/")) > 2 else ""
            tenant = self.tenant_manager.get_tenant_by_slug(slug)
            if tenant:
                return tenant.tenant_id
                
        return None


class BillingManager:
    """Менеджер биллинга"""
    
    PLAN_PRICES = {
        PlanTier.FREE: 0,
        PlanTier.STARTER: 29,
        PlanTier.PROFESSIONAL: 99,
        PlanTier.ENTERPRISE: 499,
    }
    
    def __init__(self):
        self.billing_info: Dict[str, BillingInfo] = {}
        
    def create_billing(self, tenant_id: str, plan: PlanTier) -> BillingInfo:
        """Создание биллинга"""
        billing = BillingInfo(
            billing_id=f"bill_{uuid.uuid4().hex[:8]}",
            tenant_id=tenant_id,
            plan_tier=plan,
            monthly_price=self.PLAN_PRICES[plan],
            billing_cycle_end=datetime.now() + timedelta(days=30)
        )
        self.billing_info[tenant_id] = billing
        return billing
        
    def calculate_invoice(self, tenant_id: str) -> Dict[str, Any]:
        """Расчёт счёта"""
        billing = self.billing_info.get(tenant_id)
        if not billing:
            return {}
            
        return {
            "tenant_id": tenant_id,
            "plan_tier": billing.plan_tier.value,
            "base_price": billing.monthly_price,
            "usage_charges": billing.usage_charges,
            "total": billing.monthly_price + billing.usage_charges,
            "period_end": billing.billing_cycle_end
        }


class OnboardingManager:
    """Менеджер онбординга"""
    
    ONBOARDING_STEPS = [
        "verify_email",
        "complete_profile",
        "invite_team",
        "create_project",
        "integrate_api",
        "setup_billing"
    ]
    
    def __init__(self):
        self.steps: Dict[str, List[OnboardingStep]] = {}
        
    def initialize_onboarding(self, tenant_id: str):
        """Инициализация онбординга"""
        steps = []
        for i, step_name in enumerate(self.ONBOARDING_STEPS):
            step = OnboardingStep(
                step_id=f"step_{uuid.uuid4().hex[:8]}",
                tenant_id=tenant_id,
                step_name=step_name,
                step_order=i + 1
            )
            steps.append(step)
        self.steps[tenant_id] = steps
        
    def complete_step(self, tenant_id: str, step_name: str) -> bool:
        """Завершение шага"""
        steps = self.steps.get(tenant_id, [])
        for step in steps:
            if step.step_name == step_name and not step.completed:
                step.completed = True
                step.completed_at = datetime.now()
                return True
        return False
        
    def get_progress(self, tenant_id: str) -> Dict[str, Any]:
        """Получение прогресса"""
        steps = self.steps.get(tenant_id, [])
        completed = len([s for s in steps if s.completed])
        return {
            "total_steps": len(steps),
            "completed_steps": completed,
            "progress_percent": (completed / len(steps)) * 100 if steps else 0,
            "current_step": next((s.step_name for s in steps if not s.completed), None)
        }


class MultiTenancyPlatform:
    """Платформа мультитенантности"""
    
    def __init__(self):
        self.tenant_manager = TenantManager()
        self.user_manager = UserManager(self.tenant_manager)
        self.router = TenantRouter(self.tenant_manager)
        self.billing = BillingManager()
        self.onboarding = OnboardingManager()
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        tenants = list(self.tenant_manager.tenants.values())
        
        return {
            "total_tenants": len(tenants),
            "by_status": {
                status.value: len([t for t in tenants if t.status == status])
                for status in TenantStatus
            },
            "by_plan": {
                plan.value: len([t for t in tenants if t.plan_tier == plan])
                for plan in PlanTier
            },
            "total_users": sum(len(users) for users in self.tenant_manager.users.values()),
            "custom_domains": len(self.router.domain_mapping)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 185: Multi-Tenancy Platform")
    print("=" * 60)
    
    async def demo():
        platform = MultiTenancyPlatform()
        print("✓ Multi-Tenancy Platform created")
        
        # Create tenants
        print("\n🏢 Creating Tenants...")
        
        tenant_configs = [
            ("Acme Corporation", "admin@acme.com", PlanTier.ENTERPRISE),
            ("StartupXYZ", "founder@startupxyz.io", PlanTier.PROFESSIONAL),
            ("SmallBiz Inc", "owner@smallbiz.com", PlanTier.STARTER),
            ("FreeUser", "user@gmail.com", PlanTier.FREE),
        ]
        
        tenants = []
        for name, email, plan in tenant_configs:
            tenant = await platform.tenant_manager.create_tenant(name, email, plan)
            await platform.tenant_manager.activate_tenant(tenant.tenant_id)
            platform.billing.create_billing(tenant.tenant_id, plan)
            platform.onboarding.initialize_onboarding(tenant.tenant_id)
            tenants.append(tenant)
            
            print(f"  ✓ {tenant.name} ({tenant.plan_tier.value})")
            print(f"    Slug: {tenant.slug}")
            print(f"    Isolation: {tenant.isolation_level.value}")
            
        # Show tenant details
        print("\n📋 Tenant Details:")
        
        print("\n  ┌─────────────────────┬────────────────┬────────────────┬────────────────┐")
        print("  │ Tenant              │ Plan           │ Status         │ Isolation      │")
        print("  ├─────────────────────┼────────────────┼────────────────┼────────────────┤")
        
        for tenant in tenants:
            name = tenant.name[:19].ljust(19)
            plan = tenant.plan_tier.value[:14].ljust(14)
            status = tenant.status.value[:14].ljust(14)
            isolation = tenant.isolation_level.value[:14].ljust(14)
            print(f"  │ {name} │ {plan} │ {status} │ {isolation} │")
            
        print("  └─────────────────────┴────────────────┴────────────────┴────────────────┘")
        
        # Add users
        print("\n👥 Adding Users...")
        
        for tenant in tenants:
            # Add admin
            await platform.user_manager.add_user(
                tenant.tenant_id,
                tenant.admin_email,
                f"Admin of {tenant.name}",
                "admin"
            )
            
            # Add additional users
            user_count = random.randint(1, min(5, tenant.quotas.max_users - 1))
            for i in range(user_count):
                await platform.user_manager.add_user(
                    tenant.tenant_id,
                    f"user{i}@{tenant.slug}.com",
                    f"User {i}",
                    "member"
                )
                
            print(f"  {tenant.name}: {tenant.quotas.current_users}/{tenant.quotas.max_users} users")
            
        # Show quotas
        print("\n📊 Resource Quotas:")
        
        print("\n  ┌─────────────────────┬────────────┬────────────┬──────────────┬────────────┐")
        print("  │ Tenant              │ Storage    │ Users      │ API Calls    │ Projects   │")
        print("  ├─────────────────────┼────────────┼────────────┼──────────────┼────────────┤")
        
        for tenant in tenants:
            q = tenant.quotas
            name = tenant.name[:19].ljust(19)
            storage = f"{q.storage_used_gb:.1f}/{q.storage_gb}GB".rjust(10)
            users = f"{q.current_users}/{q.max_users}".rjust(10)
            api = f"{q.api_calls_used}/{q.api_calls_per_month}".rjust(12)
            projects = f"{q.current_projects}/{q.max_projects}".rjust(10)
            print(f"  │ {name} │ {storage} │ {users} │ {api} │ {projects} │")
            
        print("  └─────────────────────┴────────────┴────────────┴──────────────┴────────────┘")
        
        # Show features
        print("\n✨ Feature Availability:")
        
        print("\n  ┌─────────────────────┬──────┬────────┬────────┬───────┬─────────┬───────┐")
        print("  │ Tenant              │ API  │ Brand  │ SSO    │ Audit │ Support │ CDN   │")
        print("  ├─────────────────────┼──────┼────────┼────────┼───────┼─────────┼───────┤")
        
        for tenant in tenants:
            name = tenant.name[:19].ljust(19)
            api = "✓" if FeatureFlag.API_ACCESS in tenant.enabled_features else "✗"
            brand = "✓" if FeatureFlag.CUSTOM_BRANDING in tenant.enabled_features else "✗"
            sso = "✓" if FeatureFlag.SSO in tenant.enabled_features else "✗"
            audit = "✓" if FeatureFlag.AUDIT_LOGS in tenant.enabled_features else "✗"
            support = "✓" if FeatureFlag.DEDICATED_SUPPORT in tenant.enabled_features else "✗"
            cdn = "✓" if FeatureFlag.CUSTOM_DOMAINS in tenant.enabled_features else "✗"
            print(f"  │ {name} │  {api}   │   {brand}    │   {sso}    │   {audit}   │    {support}    │   {cdn}   │")
            
        print("  └─────────────────────┴──────┴────────┴────────┴───────┴─────────┴───────┘")
        
        # Setup routing
        print("\n🔀 Tenant Routing:")
        
        # Add custom domains for enterprise
        enterprise_tenant = tenants[0]
        platform.router.add_custom_domain(enterprise_tenant.tenant_id, "app.acme.com")
        platform.router.add_custom_domain(enterprise_tenant.tenant_id, "portal.acme.com")
        
        print(f"\n  Custom domains for {enterprise_tenant.name}:")
        for domain, tid in platform.router.domain_mapping.items():
            if tid == enterprise_tenant.tenant_id:
                print(f"    • {domain}")
                
        # Test routing
        print("\n  Routing Tests:")
        
        test_cases = [
            ("app.acme.com", "/dashboard"),
            ("startupxyz.platform.com", "/projects"),
            ("platform.com", "/t/smallbiz-inc/home"),
        ]
        
        for host, path in test_cases:
            tenant_id = platform.router.resolve_tenant(host, path)
            tenant = platform.tenant_manager.tenants.get(tenant_id) if tenant_id else None
            result = tenant.name if tenant else "Not Found"
            print(f"    {host}{path} → {result}")
            
        # Billing
        print("\n💰 Billing Information:")
        
        total_mrr = 0
        for tenant in tenants:
            invoice = platform.billing.calculate_invoice(tenant.tenant_id)
            if invoice:
                total_mrr += invoice['total']
                print(f"\n  {tenant.name}:")
                print(f"    Plan: {invoice['plan_tier'].title()}")
                print(f"    Monthly: ${invoice['base_price']:.2f}")
                
        print(f"\n  Total MRR: ${total_mrr:.2f}")
        
        # Onboarding
        print("\n🎯 Onboarding Progress:")
        
        # Complete some steps
        for tenant in tenants:
            platform.onboarding.complete_step(tenant.tenant_id, "verify_email")
            platform.onboarding.complete_step(tenant.tenant_id, "complete_profile")
            if tenant.plan_tier != PlanTier.FREE:
                platform.onboarding.complete_step(tenant.tenant_id, "invite_team")
                platform.onboarding.complete_step(tenant.tenant_id, "create_project")
                
        for tenant in tenants:
            progress = platform.onboarding.get_progress(tenant.tenant_id)
            bar_width = 20
            filled = int(progress['progress_percent'] / 100 * bar_width)
            bar = "█" * filled + "░" * (bar_width - filled)
            
            print(f"\n  {tenant.name}:")
            print(f"    [{bar}] {progress['progress_percent']:.0f}%")
            print(f"    {progress['completed_steps']}/{progress['total_steps']} steps")
            if progress['current_step']:
                print(f"    Next: {progress['current_step'].replace('_', ' ').title()}")
                
        # Suspend a tenant
        print("\n⚠️ Tenant Management:")
        
        await platform.tenant_manager.suspend_tenant(tenants[3].tenant_id, "Payment overdue")
        print(f"  Suspended: {tenants[3].name} (Payment overdue)")
        
        # Platform statistics
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Tenants: {stats['total_tenants']}")
        print(f"  Total Users: {stats['total_users']}")
        print(f"  Custom Domains: {stats['custom_domains']}")
        
        print("\n  By Plan:")
        for plan, count in stats['by_plan'].items():
            if count > 0:
                print(f"    • {plan}: {count}")
                
        print("\n  By Status:")
        for status, count in stats['by_status'].items():
            if count > 0:
                print(f"    • {status}: {count}")
                
        # Dashboard
        print("\n┌────────────────────────────────────────────────────────────────────┐")
        print("│                    Multi-Tenancy Dashboard                         │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Total Tenants:                 {stats['total_tenants']:>10}                     │")
        print(f"│ Total Users:                   {stats['total_users']:>10}                     │")
        print(f"│ Monthly Revenue:               ${total_mrr:>9.2f}                     │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Active Tenants:                {stats['by_status'].get('active', 0):>10}                     │")
        print(f"│ Enterprise:                    {stats['by_plan'].get('enterprise', 0):>10}                     │")
        print(f"│ Professional:                  {stats['by_plan'].get('professional', 0):>10}                     │")
        print(f"│ Starter:                       {stats['by_plan'].get('starter', 0):>10}                     │")
        print(f"│ Free:                          {stats['by_plan'].get('free', 0):>10}                     │")
        print("└────────────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Multi-Tenancy Platform initialized!")
    print("=" * 60)
