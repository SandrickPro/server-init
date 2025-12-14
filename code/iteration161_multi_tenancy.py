#!/usr/bin/env python3
"""
Server Init - Iteration 161: Multi-Tenancy Platform
Платформа мультитенантности

Функционал:
- Tenant Management - управление тенантами
- Resource Isolation - изоляция ресурсов
- Quota Management - управление квотами
- Billing Integration - интеграция биллинга
- Tenant Provisioning - провизионинг тенантов
- Access Control - контроль доступа
- Data Partitioning - партиционирование данных
- Tenant Analytics - аналитика тенантов
"""

import json
import asyncio
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
    DELETED = "deleted"


class TenantTier(Enum):
    """Уровень тенанта"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class IsolationLevel(Enum):
    """Уровень изоляции"""
    SHARED = "shared"
    NAMESPACE = "namespace"
    DEDICATED = "dedicated"


class ResourceType(Enum):
    """Тип ресурса"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    API_CALLS = "api_calls"
    USERS = "users"
    PROJECTS = "projects"


class BillingPeriod(Enum):
    """Период биллинга"""
    MONTHLY = "monthly"
    YEARLY = "yearly"
    USAGE_BASED = "usage_based"


@dataclass
class ResourceQuota:
    """Квота ресурса"""
    quota_id: str
    resource_type: ResourceType = ResourceType.CPU
    
    # Limits
    limit: float = 0.0
    used: float = 0.0
    
    # Unit
    unit: str = ""
    
    # Alerts
    warning_threshold: float = 80.0  # percentage
    critical_threshold: float = 95.0
    
    # Enforcement
    hard_limit: bool = True


@dataclass
class QuotaSet:
    """Набор квот"""
    quotas: Dict[ResourceType, ResourceQuota] = field(default_factory=dict)
    
    def get_usage_percentage(self, resource_type: ResourceType) -> float:
        """Получение процента использования"""
        if resource_type in self.quotas:
            quota = self.quotas[resource_type]
            if quota.limit > 0:
                return (quota.used / quota.limit) * 100
        return 0.0


@dataclass
class TenantConfig:
    """Конфигурация тенанта"""
    config_id: str
    
    # Isolation
    isolation_level: IsolationLevel = IsolationLevel.SHARED
    
    # Features
    features: List[str] = field(default_factory=list)
    
    # Custom settings
    settings: Dict[str, Any] = field(default_factory=dict)
    
    # Limits
    max_users: int = 10
    max_projects: int = 5
    max_api_calls_per_day: int = 10000


@dataclass
class BillingInfo:
    """Информация о биллинге"""
    billing_id: str
    tenant_id: str = ""
    
    # Plan
    plan_name: str = ""
    billing_period: BillingPeriod = BillingPeriod.MONTHLY
    
    # Pricing
    base_price: float = 0.0
    current_charges: float = 0.0
    
    # Usage
    usage_records: List[Dict] = field(default_factory=list)
    
    # Payment
    payment_method: str = ""
    last_payment: Optional[datetime] = None
    next_billing_date: Optional[datetime] = None
    
    # Status
    paid: bool = True
    balance: float = 0.0


@dataclass
class TenantUser:
    """Пользователь тенанта"""
    user_id: str
    tenant_id: str = ""
    
    # Info
    email: str = ""
    name: str = ""
    
    # Role
    role: str = "member"  # owner, admin, member, viewer
    
    # Permissions
    permissions: List[str] = field(default_factory=list)
    
    # Status
    active: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None


@dataclass
class TenantProject:
    """Проект тенанта"""
    project_id: str
    tenant_id: str = ""
    
    # Info
    name: str = ""
    description: str = ""
    
    # Resources
    namespace: str = ""
    
    # Status
    active: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Tenant:
    """Тенант"""
    tenant_id: str
    name: str = ""
    
    # Organization
    organization: str = ""
    domain: str = ""
    
    # Tier
    tier: TenantTier = TenantTier.FREE
    
    # Status
    status: TenantStatus = TenantStatus.PENDING
    
    # Config
    config: Optional[TenantConfig] = None
    
    # Quotas
    quotas: Optional[QuotaSet] = None
    
    # Billing
    billing: Optional[BillingInfo] = None
    
    # Users
    users: Dict[str, TenantUser] = field(default_factory=dict)
    owner_id: str = ""
    
    # Projects
    projects: Dict[str, TenantProject] = field(default_factory=dict)
    
    # Data partition
    database_schema: str = ""
    storage_bucket: str = ""
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    activated_at: Optional[datetime] = None


@dataclass
class UsageMetric:
    """Метрика использования"""
    metric_id: str
    tenant_id: str = ""
    
    # Resource
    resource_type: ResourceType = ResourceType.API_CALLS
    
    # Value
    value: float = 0.0
    unit: str = ""
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)


@dataclass
class TenantEvent:
    """Событие тенанта"""
    event_id: str
    tenant_id: str = ""
    
    # Event
    event_type: str = ""  # created, activated, suspended, upgraded, etc.
    description: str = ""
    
    # Actor
    actor_id: str = ""
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)


class TenantManager:
    """Менеджер тенантов"""
    
    def __init__(self):
        self.tenants: Dict[str, Tenant] = {}
        self.events: List[TenantEvent] = []
        
    def create_tenant(self, name: str, organization: str,
                       tier: TenantTier = TenantTier.FREE,
                       owner_email: str = "") -> Tenant:
        """Создание тенанта"""
        tenant = Tenant(
            tenant_id=f"tenant_{uuid.uuid4().hex[:8]}",
            name=name,
            organization=organization,
            tier=tier,
            status=TenantStatus.PENDING
        )
        
        # Create config
        tenant.config = self._create_config(tier)
        
        # Create quotas
        tenant.quotas = self._create_quotas(tier)
        
        # Create billing
        tenant.billing = self._create_billing(tenant.tenant_id, tier)
        
        # Create owner user
        if owner_email:
            owner = self._create_user(tenant.tenant_id, owner_email, "owner")
            tenant.users[owner.user_id] = owner
            tenant.owner_id = owner.user_id
            
        # Set data partition
        tenant.database_schema = f"tenant_{tenant.tenant_id}"
        tenant.storage_bucket = f"bucket-{tenant.tenant_id}"
        
        self.tenants[tenant.tenant_id] = tenant
        
        # Log event
        self._log_event(tenant.tenant_id, "created", "Tenant created")
        
        return tenant
        
    def _create_config(self, tier: TenantTier) -> TenantConfig:
        """Создание конфигурации"""
        configs = {
            TenantTier.FREE: TenantConfig(
                config_id=f"cfg_{uuid.uuid4().hex[:8]}",
                isolation_level=IsolationLevel.SHARED,
                features=["basic_api"],
                max_users=3,
                max_projects=1,
                max_api_calls_per_day=1000
            ),
            TenantTier.STARTER: TenantConfig(
                config_id=f"cfg_{uuid.uuid4().hex[:8]}",
                isolation_level=IsolationLevel.SHARED,
                features=["basic_api", "analytics", "support"],
                max_users=10,
                max_projects=5,
                max_api_calls_per_day=10000
            ),
            TenantTier.PROFESSIONAL: TenantConfig(
                config_id=f"cfg_{uuid.uuid4().hex[:8]}",
                isolation_level=IsolationLevel.NAMESPACE,
                features=["basic_api", "analytics", "support", "sso", "audit_logs"],
                max_users=50,
                max_projects=20,
                max_api_calls_per_day=100000
            ),
            TenantTier.ENTERPRISE: TenantConfig(
                config_id=f"cfg_{uuid.uuid4().hex[:8]}",
                isolation_level=IsolationLevel.DEDICATED,
                features=["basic_api", "analytics", "support", "sso", "audit_logs", "custom_domain", "sla"],
                max_users=1000,
                max_projects=100,
                max_api_calls_per_day=1000000
            ),
        }
        return configs.get(tier, configs[TenantTier.FREE])
        
    def _create_quotas(self, tier: TenantTier) -> QuotaSet:
        """Создание квот"""
        quota_set = QuotaSet()
        
        limits = {
            TenantTier.FREE: {
                ResourceType.CPU: (1, "cores"),
                ResourceType.MEMORY: (2, "GB"),
                ResourceType.STORAGE: (5, "GB"),
                ResourceType.API_CALLS: (1000, "calls/day"),
                ResourceType.USERS: (3, "users"),
                ResourceType.PROJECTS: (1, "projects"),
            },
            TenantTier.STARTER: {
                ResourceType.CPU: (2, "cores"),
                ResourceType.MEMORY: (4, "GB"),
                ResourceType.STORAGE: (20, "GB"),
                ResourceType.API_CALLS: (10000, "calls/day"),
                ResourceType.USERS: (10, "users"),
                ResourceType.PROJECTS: (5, "projects"),
            },
            TenantTier.PROFESSIONAL: {
                ResourceType.CPU: (8, "cores"),
                ResourceType.MEMORY: (16, "GB"),
                ResourceType.STORAGE: (100, "GB"),
                ResourceType.API_CALLS: (100000, "calls/day"),
                ResourceType.USERS: (50, "users"),
                ResourceType.PROJECTS: (20, "projects"),
            },
            TenantTier.ENTERPRISE: {
                ResourceType.CPU: (32, "cores"),
                ResourceType.MEMORY: (64, "GB"),
                ResourceType.STORAGE: (1000, "GB"),
                ResourceType.API_CALLS: (1000000, "calls/day"),
                ResourceType.USERS: (1000, "users"),
                ResourceType.PROJECTS: (100, "projects"),
            },
        }
        
        tier_limits = limits.get(tier, limits[TenantTier.FREE])
        
        for resource_type, (limit, unit) in tier_limits.items():
            quota = ResourceQuota(
                quota_id=f"quota_{uuid.uuid4().hex[:8]}",
                resource_type=resource_type,
                limit=limit,
                unit=unit
            )
            quota_set.quotas[resource_type] = quota
            
        return quota_set
        
    def _create_billing(self, tenant_id: str, tier: TenantTier) -> BillingInfo:
        """Создание биллинга"""
        prices = {
            TenantTier.FREE: 0.0,
            TenantTier.STARTER: 49.0,
            TenantTier.PROFESSIONAL: 199.0,
            TenantTier.ENTERPRISE: 999.0,
        }
        
        plan_names = {
            TenantTier.FREE: "Free",
            TenantTier.STARTER: "Starter",
            TenantTier.PROFESSIONAL: "Professional",
            TenantTier.ENTERPRISE: "Enterprise",
        }
        
        return BillingInfo(
            billing_id=f"bill_{uuid.uuid4().hex[:8]}",
            tenant_id=tenant_id,
            plan_name=plan_names.get(tier, "Free"),
            base_price=prices.get(tier, 0.0),
            billing_period=BillingPeriod.MONTHLY,
            next_billing_date=datetime.now() + timedelta(days=30)
        )
        
    def _create_user(self, tenant_id: str, email: str, role: str) -> TenantUser:
        """Создание пользователя"""
        permissions = {
            "owner": ["all"],
            "admin": ["manage_users", "manage_projects", "view_billing"],
            "member": ["create_projects", "view_projects"],
            "viewer": ["view_projects"],
        }
        
        return TenantUser(
            user_id=f"user_{uuid.uuid4().hex[:8]}",
            tenant_id=tenant_id,
            email=email,
            role=role,
            permissions=permissions.get(role, [])
        )
        
    def _log_event(self, tenant_id: str, event_type: str, description: str):
        """Логирование события"""
        event = TenantEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            tenant_id=tenant_id,
            event_type=event_type,
            description=description
        )
        self.events.append(event)
        
    def activate_tenant(self, tenant_id: str) -> bool:
        """Активация тенанта"""
        if tenant_id not in self.tenants:
            return False
            
        tenant = self.tenants[tenant_id]
        tenant.status = TenantStatus.ACTIVE
        tenant.activated_at = datetime.now()
        
        self._log_event(tenant_id, "activated", "Tenant activated")
        return True
        
    def suspend_tenant(self, tenant_id: str, reason: str = "") -> bool:
        """Приостановка тенанта"""
        if tenant_id not in self.tenants:
            return False
            
        tenant = self.tenants[tenant_id]
        tenant.status = TenantStatus.SUSPENDED
        
        self._log_event(tenant_id, "suspended", f"Tenant suspended: {reason}")
        return True
        
    def upgrade_tier(self, tenant_id: str, new_tier: TenantTier) -> bool:
        """Обновление тарифа"""
        if tenant_id not in self.tenants:
            return False
            
        tenant = self.tenants[tenant_id]
        old_tier = tenant.tier
        
        tenant.tier = new_tier
        tenant.config = self._create_config(new_tier)
        tenant.quotas = self._create_quotas(new_tier)
        tenant.billing = self._create_billing(tenant_id, new_tier)
        
        self._log_event(
            tenant_id, "upgraded",
            f"Tenant upgraded from {old_tier.value} to {new_tier.value}"
        )
        return True


class QuotaManager:
    """Менеджер квот"""
    
    def __init__(self, tenant_manager: TenantManager):
        self.tenant_manager = tenant_manager
        self.usage_history: List[UsageMetric] = []
        
    def check_quota(self, tenant_id: str, resource_type: ResourceType,
                     amount: float = 1) -> tuple:
        """Проверка квоты"""
        tenant = self.tenant_manager.tenants.get(tenant_id)
        
        if not tenant or not tenant.quotas:
            return False, "Tenant not found"
            
        quota = tenant.quotas.quotas.get(resource_type)
        
        if not quota:
            return True, "No quota defined"
            
        if quota.used + amount > quota.limit:
            if quota.hard_limit:
                return False, f"Quota exceeded: {resource_type.value}"
            else:
                return True, f"Quota warning: {resource_type.value}"
                
        return True, "OK"
        
    def use_quota(self, tenant_id: str, resource_type: ResourceType,
                   amount: float) -> bool:
        """Использование квоты"""
        allowed, _ = self.check_quota(tenant_id, resource_type, amount)
        
        if not allowed:
            return False
            
        tenant = self.tenant_manager.tenants.get(tenant_id)
        
        if tenant and tenant.quotas:
            quota = tenant.quotas.quotas.get(resource_type)
            if quota:
                quota.used += amount
                
                # Record usage
                metric = UsageMetric(
                    metric_id=f"metric_{uuid.uuid4().hex[:8]}",
                    tenant_id=tenant_id,
                    resource_type=resource_type,
                    value=amount
                )
                self.usage_history.append(metric)
                
        return True
        
    def release_quota(self, tenant_id: str, resource_type: ResourceType,
                       amount: float):
        """Освобождение квоты"""
        tenant = self.tenant_manager.tenants.get(tenant_id)
        
        if tenant and tenant.quotas:
            quota = tenant.quotas.quotas.get(resource_type)
            if quota:
                quota.used = max(0, quota.used - amount)
                
    def get_quota_status(self, tenant_id: str) -> Dict[str, Any]:
        """Статус квот"""
        tenant = self.tenant_manager.tenants.get(tenant_id)
        
        if not tenant or not tenant.quotas:
            return {}
            
        status = {}
        
        for resource_type, quota in tenant.quotas.quotas.items():
            usage_pct = (quota.used / quota.limit * 100) if quota.limit > 0 else 0
            
            if usage_pct >= quota.critical_threshold:
                alert = "critical"
            elif usage_pct >= quota.warning_threshold:
                alert = "warning"
            else:
                alert = "normal"
                
            status[resource_type.value] = {
                "used": quota.used,
                "limit": quota.limit,
                "unit": quota.unit,
                "percentage": usage_pct,
                "alert": alert
            }
            
        return status


class BillingManager:
    """Менеджер биллинга"""
    
    def __init__(self, tenant_manager: TenantManager):
        self.tenant_manager = tenant_manager
        self.invoices: List[Dict] = []
        
    def calculate_charges(self, tenant_id: str) -> float:
        """Расчёт начислений"""
        tenant = self.tenant_manager.tenants.get(tenant_id)
        
        if not tenant or not tenant.billing:
            return 0.0
            
        charges = tenant.billing.base_price
        
        # Add usage-based charges
        for record in tenant.billing.usage_records:
            charges += record.get("amount", 0)
            
        tenant.billing.current_charges = charges
        return charges
        
    def generate_invoice(self, tenant_id: str) -> Dict:
        """Генерация счёта"""
        tenant = self.tenant_manager.tenants.get(tenant_id)
        
        if not tenant or not tenant.billing:
            return {}
            
        charges = self.calculate_charges(tenant_id)
        
        invoice = {
            "invoice_id": f"inv_{uuid.uuid4().hex[:8]}",
            "tenant_id": tenant_id,
            "tenant_name": tenant.name,
            "plan": tenant.billing.plan_name,
            "base_price": tenant.billing.base_price,
            "usage_charges": charges - tenant.billing.base_price,
            "total": charges,
            "period_start": (datetime.now() - timedelta(days=30)).isoformat(),
            "period_end": datetime.now().isoformat(),
            "due_date": (datetime.now() + timedelta(days=15)).isoformat(),
            "status": "pending"
        }
        
        self.invoices.append(invoice)
        return invoice
        
    def process_payment(self, tenant_id: str, amount: float) -> bool:
        """Обработка платежа"""
        tenant = self.tenant_manager.tenants.get(tenant_id)
        
        if not tenant or not tenant.billing:
            return False
            
        tenant.billing.balance += amount
        tenant.billing.last_payment = datetime.now()
        tenant.billing.paid = tenant.billing.balance >= 0
        
        return True


class TenantProvisioner:
    """Провизионер тенантов"""
    
    def __init__(self, tenant_manager: TenantManager):
        self.tenant_manager = tenant_manager
        
    async def provision(self, tenant: Tenant) -> bool:
        """Провизионинг тенанта"""
        try:
            # Create database schema
            await self._create_database_schema(tenant)
            
            # Create storage bucket
            await self._create_storage_bucket(tenant)
            
            # Create namespace (if dedicated)
            if tenant.config and tenant.config.isolation_level in [
                IsolationLevel.NAMESPACE, IsolationLevel.DEDICATED
            ]:
                await self._create_namespace(tenant)
                
            # Setup networking
            await self._setup_networking(tenant)
            
            # Activate tenant
            self.tenant_manager.activate_tenant(tenant.tenant_id)
            
            return True
            
        except Exception as e:
            print(f"Provisioning failed: {e}")
            return False
            
    async def _create_database_schema(self, tenant: Tenant):
        """Создание схемы БД"""
        await asyncio.sleep(0.1)  # Simulate
        print(f"    Created schema: {tenant.database_schema}")
        
    async def _create_storage_bucket(self, tenant: Tenant):
        """Создание бакета"""
        await asyncio.sleep(0.1)
        print(f"    Created bucket: {tenant.storage_bucket}")
        
    async def _create_namespace(self, tenant: Tenant):
        """Создание namespace"""
        await asyncio.sleep(0.1)
        namespace = f"ns-{tenant.tenant_id}"
        print(f"    Created namespace: {namespace}")
        
    async def _setup_networking(self, tenant: Tenant):
        """Настройка сети"""
        await asyncio.sleep(0.1)
        print(f"    Configured networking")
        
    async def deprovision(self, tenant: Tenant) -> bool:
        """Депровизионинг тенанта"""
        try:
            await asyncio.sleep(0.2)  # Simulate cleanup
            tenant.status = TenantStatus.DELETED
            return True
        except Exception:
            return False


class TenantAnalytics:
    """Аналитика тенантов"""
    
    def __init__(self, tenant_manager: TenantManager, quota_manager: QuotaManager):
        self.tenant_manager = tenant_manager
        self.quota_manager = quota_manager
        
    def get_tenant_metrics(self, tenant_id: str) -> Dict[str, Any]:
        """Метрики тенанта"""
        tenant = self.tenant_manager.tenants.get(tenant_id)
        
        if not tenant:
            return {}
            
        return {
            "tenant_id": tenant_id,
            "name": tenant.name,
            "tier": tenant.tier.value,
            "status": tenant.status.value,
            "users": len(tenant.users),
            "projects": len(tenant.projects),
            "quota_status": self.quota_manager.get_quota_status(tenant_id),
            "created_at": tenant.created_at.isoformat(),
            "days_active": (datetime.now() - tenant.created_at).days
        }
        
    def get_platform_metrics(self) -> Dict[str, Any]:
        """Метрики платформы"""
        tenants = list(self.tenant_manager.tenants.values())
        
        by_tier = {}
        by_status = {}
        total_users = 0
        total_projects = 0
        
        for tenant in tenants:
            tier = tenant.tier.value
            by_tier[tier] = by_tier.get(tier, 0) + 1
            
            status = tenant.status.value
            by_status[status] = by_status.get(status, 0) + 1
            
            total_users += len(tenant.users)
            total_projects += len(tenant.projects)
            
        return {
            "total_tenants": len(tenants),
            "by_tier": by_tier,
            "by_status": by_status,
            "total_users": total_users,
            "total_projects": total_projects
        }


class MultiTenancyPlatform:
    """Платформа мультитенантности"""
    
    def __init__(self):
        self.tenant_manager = TenantManager()
        self.quota_manager = QuotaManager(self.tenant_manager)
        self.billing_manager = BillingManager(self.tenant_manager)
        self.provisioner = TenantProvisioner(self.tenant_manager)
        self.analytics = TenantAnalytics(self.tenant_manager, self.quota_manager)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        return self.analytics.get_platform_metrics()


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 161: Multi-Tenancy Platform")
    print("=" * 60)
    
    async def demo():
        platform = MultiTenancyPlatform()
        print("✓ Multi-Tenancy Platform created")
        
        # Create tenants
        print("\n🏢 Creating Tenants...")
        
        # Free tier tenant
        free_tenant = platform.tenant_manager.create_tenant(
            name="StartupCo",
            organization="StartupCo Inc.",
            tier=TenantTier.FREE,
            owner_email="owner@startupco.com"
        )
        print(f"  ✓ {free_tenant.name} ({free_tenant.tier.value})")
        
        # Starter tier tenant
        starter_tenant = platform.tenant_manager.create_tenant(
            name="GrowingBiz",
            organization="Growing Business LLC",
            tier=TenantTier.STARTER,
            owner_email="admin@growingbiz.com"
        )
        print(f"  ✓ {starter_tenant.name} ({starter_tenant.tier.value})")
        
        # Professional tier tenant
        pro_tenant = platform.tenant_manager.create_tenant(
            name="TechCorp",
            organization="Technology Corporation",
            tier=TenantTier.PROFESSIONAL,
            owner_email="cto@techcorp.com"
        )
        print(f"  ✓ {pro_tenant.name} ({pro_tenant.tier.value})")
        
        # Enterprise tier tenant
        enterprise_tenant = platform.tenant_manager.create_tenant(
            name="MegaEnterprise",
            organization="Mega Enterprise Group",
            tier=TenantTier.ENTERPRISE,
            owner_email="admin@megaenterprise.com"
        )
        print(f"  ✓ {enterprise_tenant.name} ({enterprise_tenant.tier.value})")
        
        # Provision tenants
        print("\n⚙️ Provisioning Tenants...")
        
        for tenant in [free_tenant, starter_tenant, pro_tenant, enterprise_tenant]:
            print(f"\n  Provisioning {tenant.name}...")
            await platform.provisioner.provision(tenant)
            
        # Add users to tenants
        print("\n👥 Adding Users...")
        
        # Add users to pro tenant
        users = [
            ("dev1@techcorp.com", "member"),
            ("dev2@techcorp.com", "member"),
            ("manager@techcorp.com", "admin"),
        ]
        
        for email, role in users:
            user = platform.tenant_manager._create_user(
                pro_tenant.tenant_id, email, role
            )
            pro_tenant.users[user.user_id] = user
            
        print(f"  ✓ Added {len(users)} users to {pro_tenant.name}")
        
        # Create projects
        print("\n📁 Creating Projects...")
        
        projects = [
            ("api-backend", "Main API Backend"),
            ("web-frontend", "Web Application"),
            ("mobile-app", "Mobile Application"),
        ]
        
        for name, desc in projects:
            project = TenantProject(
                project_id=f"proj_{uuid.uuid4().hex[:8]}",
                tenant_id=pro_tenant.tenant_id,
                name=name,
                description=desc,
                namespace=f"ns-{pro_tenant.tenant_id}-{name}"
            )
            pro_tenant.projects[project.project_id] = project
            print(f"  ✓ {name}: {desc}")
            
        # Use quotas
        print("\n📊 Using Quotas...")
        
        # Simulate API calls
        for i in range(5):
            success = platform.quota_manager.use_quota(
                pro_tenant.tenant_id,
                ResourceType.API_CALLS,
                10000
            )
            
        # Simulate resource usage
        platform.quota_manager.use_quota(
            pro_tenant.tenant_id, ResourceType.CPU, 4
        )
        platform.quota_manager.use_quota(
            pro_tenant.tenant_id, ResourceType.MEMORY, 8
        )
        platform.quota_manager.use_quota(
            pro_tenant.tenant_id, ResourceType.STORAGE, 30
        )
        
        # Check quota status
        quota_status = platform.quota_manager.get_quota_status(pro_tenant.tenant_id)
        
        print(f"\n  Quota Status for {pro_tenant.name}:")
        print("  ┌───────────────────────────────────────────────────────────┐")
        print("  │ Resource      │ Used      │ Limit     │ Usage  │ Status  │")
        print("  ├───────────────────────────────────────────────────────────┤")
        
        for resource, status in quota_status.items():
            res = resource[:13].ljust(13)
            used = f"{status['used']:.0f}".ljust(9)
            limit = f"{status['limit']:.0f}".ljust(9)
            pct = f"{status['percentage']:.1f}%".ljust(6)
            alert = status['alert'][:7].ljust(7)
            print(f"  │ {res} │ {used} │ {limit} │ {pct} │ {alert} │")
            
        print("  └───────────────────────────────────────────────────────────┘")
        
        # Billing
        print("\n💰 Billing Information...")
        
        print("\n  Monthly Charges:")
        print("  ┌───────────────────────────────────────────────────────────┐")
        print("  │ Tenant             │ Plan           │ Base    │ Total    │")
        print("  ├───────────────────────────────────────────────────────────┤")
        
        for tenant in platform.tenant_manager.tenants.values():
            if tenant.billing:
                charges = platform.billing_manager.calculate_charges(tenant.tenant_id)
                name = tenant.name[:18].ljust(18)
                plan = tenant.billing.plan_name[:14].ljust(14)
                base = f"${tenant.billing.base_price:.0f}".ljust(7)
                total = f"${charges:.0f}".ljust(8)
                print(f"  │ {name} │ {plan} │ {base} │ {total} │")
                
        print("  └───────────────────────────────────────────────────────────┘")
        
        # Generate invoice
        print("\n📄 Sample Invoice:")
        
        invoice = platform.billing_manager.generate_invoice(pro_tenant.tenant_id)
        
        print(f"\n  Invoice #{invoice['invoice_id']}")
        print(f"  Tenant: {invoice['tenant_name']}")
        print(f"  Plan: {invoice['plan']}")
        print(f"  Base Price: ${invoice['base_price']:.2f}")
        print(f"  Usage Charges: ${invoice['usage_charges']:.2f}")
        print(f"  Total: ${invoice['total']:.2f}")
        print(f"  Due Date: {invoice['due_date'][:10]}")
        
        # Upgrade tenant
        print("\n⬆️ Upgrading Tenant...")
        
        platform.tenant_manager.upgrade_tier(
            starter_tenant.tenant_id,
            TenantTier.PROFESSIONAL
        )
        
        print(f"  ✓ Upgraded {starter_tenant.name} to Professional")
        
        # Tenant configuration comparison
        print("\n⚙️ Tenant Configurations:")
        print("  ┌────────────────────────────────────────────────────────────────────────┐")
        print("  │ Tenant             │ Tier         │ Isolation │ Users │ Projects │ API │")
        print("  ├────────────────────────────────────────────────────────────────────────┤")
        
        for tenant in platform.tenant_manager.tenants.values():
            name = tenant.name[:18].ljust(18)
            tier = tenant.tier.value[:12].ljust(12)
            iso = tenant.config.isolation_level.value[:9].ljust(9) if tenant.config else "-".ljust(9)
            users = str(tenant.config.max_users if tenant.config else 0).ljust(5)
            projects = str(tenant.config.max_projects if tenant.config else 0).ljust(8)
            api = str(tenant.config.max_api_calls_per_day if tenant.config else 0)
            print(f"  │ {name} │ {tier} │ {iso} │ {users} │ {projects} │ {api:>7} │")
            
        print("  └────────────────────────────────────────────────────────────────────────┘")
        
        # Feature comparison
        print("\n🎁 Feature Comparison:")
        
        all_features = set()
        for tenant in platform.tenant_manager.tenants.values():
            if tenant.config:
                all_features.update(tenant.config.features)
                
        print("\n  Feature Matrix:")
        for feature in sorted(all_features):
            line = f"  {feature.ljust(20)}"
            for tenant in platform.tenant_manager.tenants.values():
                has = "✓" if tenant.config and feature in tenant.config.features else "-"
                line += f" {has:^10}"
            print(line)
            
        # Events log
        print("\n📜 Recent Events:")
        
        for event in platform.tenant_manager.events[-5:]:
            tenant = platform.tenant_manager.tenants.get(event.tenant_id)
            tenant_name = tenant.name if tenant else "Unknown"
            print(f"  [{event.event_type}] {tenant_name}: {event.description}")
            
        # Platform statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Tenants: {stats['total_tenants']}")
        print(f"  Total Users: {stats['total_users']}")
        print(f"  Total Projects: {stats['total_projects']}")
        
        print("\n  By Tier:")
        for tier, count in stats["by_tier"].items():
            print(f"    {tier}: {count}")
            
        print("\n  By Status:")
        for status, count in stats["by_status"].items():
            print(f"    {status}: {count}")
            
        # Dashboard
        print("\n📋 Multi-Tenancy Dashboard:")
        print("  ┌────────────────────────────────────────────────────────────┐")
        print("  │                Multi-Tenancy Overview                      │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Tenants:           {stats['total_tenants']:>10}                   │")
        print(f"  │ Total Users:             {stats['total_users']:>10}                   │")
        print(f"  │ Total Projects:          {stats['total_projects']:>10}                   │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Active Tenants:          {stats['by_status'].get('active', 0):>10}                   │")
        print(f"  │ Enterprise Tier:         {stats['by_tier'].get('enterprise', 0):>10}                   │")
        print("  └────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Multi-Tenancy Platform initialized!")
    print("=" * 60)
