#!/usr/bin/env python3
"""
Server Init - Iteration 222: Multi-Tenancy Platform
Платформа мультитенантности

Функционал:
- Tenant Management - управление тенантами
- Resource Isolation - изоляция ресурсов
- Quota Management - управление квотами
- Data Partitioning - партиционирование данных
- Billing Integration - интеграция биллинга
- Access Control - контроль доступа
- Tenant Metrics - метрики тенантов
- Configuration Override - переопределение конфигурации
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class TenantStatus(Enum):
    """Статус тенанта"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    TERMINATED = "terminated"


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
    API_CALLS = "api_calls"
    USERS = "users"
    PROJECTS = "projects"


@dataclass
class ResourceQuota:
    """Квота ресурсов"""
    resource_type: ResourceType
    limit: int = 0
    used: int = 0
    
    @property
    def available(self) -> int:
        return max(0, self.limit - self.used)
        
    @property
    def utilization(self) -> float:
        return (self.used / self.limit * 100) if self.limit > 0 else 0


@dataclass
class TenantConfig:
    """Конфигурация тенанта"""
    config_id: str
    
    # Features
    features: Dict[str, bool] = field(default_factory=dict)
    
    # Limits
    rate_limit_per_minute: int = 1000
    max_concurrent_connections: int = 100
    
    # Branding
    custom_domain: Optional[str] = None
    logo_url: Optional[str] = None
    theme: str = "default"
    
    # Integration
    webhook_url: Optional[str] = None
    api_key_prefix: str = ""


@dataclass
class Tenant:
    """Тенант"""
    tenant_id: str
    name: str = ""
    slug: str = ""
    
    # Status
    status: TenantStatus = TenantStatus.PENDING
    tier: TenantTier = TenantTier.FREE
    
    # Isolation
    isolation_level: IsolationLevel = IsolationLevel.SHARED
    namespace: str = ""
    
    # Owner
    owner_id: str = ""
    owner_email: str = ""
    
    # Config
    config: Optional[TenantConfig] = None
    
    # Quotas
    quotas: Dict[ResourceType, ResourceQuota] = field(default_factory=dict)
    
    # Dates
    created_at: datetime = field(default_factory=datetime.now)
    activated_at: Optional[datetime] = None
    suspended_at: Optional[datetime] = None
    
    # Billing
    billing_email: str = ""
    payment_method_id: Optional[str] = None
    
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
    role: str = "member"  # owner, admin, member, viewer
    
    # Status
    active: bool = True
    
    # Dates
    joined_at: datetime = field(default_factory=datetime.now)
    last_active: Optional[datetime] = None


@dataclass
class TenantUsage:
    """Использование тенанта"""
    usage_id: str
    tenant_id: str = ""
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Metrics
    api_calls: int = 0
    storage_bytes: int = 0
    compute_seconds: int = 0
    bandwidth_bytes: int = 0
    
    # Cost
    estimated_cost: float = 0


@dataclass
class TenantInvoice:
    """Счёт тенанта"""
    invoice_id: str
    tenant_id: str = ""
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Amount
    subtotal: float = 0
    tax: float = 0
    total: float = 0
    
    # Status
    status: str = "pending"  # pending, paid, overdue
    
    # Dates
    due_date: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=30))
    paid_at: Optional[datetime] = None


class QuotaManager:
    """Менеджер квот"""
    
    TIER_LIMITS = {
        TenantTier.FREE: {
            ResourceType.CPU: 1,
            ResourceType.MEMORY: 1024,  # MB
            ResourceType.STORAGE: 5120,  # MB
            ResourceType.API_CALLS: 10000,
            ResourceType.USERS: 3,
            ResourceType.PROJECTS: 2,
        },
        TenantTier.STARTER: {
            ResourceType.CPU: 2,
            ResourceType.MEMORY: 4096,
            ResourceType.STORAGE: 20480,
            ResourceType.API_CALLS: 100000,
            ResourceType.USERS: 10,
            ResourceType.PROJECTS: 10,
        },
        TenantTier.PROFESSIONAL: {
            ResourceType.CPU: 8,
            ResourceType.MEMORY: 16384,
            ResourceType.STORAGE: 102400,
            ResourceType.API_CALLS: 1000000,
            ResourceType.USERS: 50,
            ResourceType.PROJECTS: 50,
        },
        TenantTier.ENTERPRISE: {
            ResourceType.CPU: 32,
            ResourceType.MEMORY: 65536,
            ResourceType.STORAGE: 1048576,
            ResourceType.API_CALLS: 10000000,
            ResourceType.USERS: 500,
            ResourceType.PROJECTS: 500,
        },
    }
    
    def get_limits(self, tier: TenantTier) -> Dict[ResourceType, int]:
        """Получение лимитов уровня"""
        return self.TIER_LIMITS.get(tier, self.TIER_LIMITS[TenantTier.FREE])
        
    def create_quotas(self, tier: TenantTier) -> Dict[ResourceType, ResourceQuota]:
        """Создание квот для уровня"""
        limits = self.get_limits(tier)
        return {
            rt: ResourceQuota(resource_type=rt, limit=limit)
            for rt, limit in limits.items()
        }
        
    def check_quota(self, quota: ResourceQuota, requested: int) -> bool:
        """Проверка квоты"""
        return quota.available >= requested
        
    def consume_quota(self, quota: ResourceQuota, amount: int) -> bool:
        """Потребление квоты"""
        if self.check_quota(quota, amount):
            quota.used += amount
            return True
        return False


class BillingCalculator:
    """Калькулятор биллинга"""
    
    TIER_PRICES = {
        TenantTier.FREE: 0,
        TenantTier.STARTER: 29.99,
        TenantTier.PROFESSIONAL: 99.99,
        TenantTier.ENTERPRISE: 499.99,
    }
    
    OVERAGE_PRICES = {
        ResourceType.API_CALLS: 0.0001,  # per call
        ResourceType.STORAGE: 0.05,  # per GB
        ResourceType.CPU: 0.10,  # per core-hour
    }
    
    def calculate_base_cost(self, tier: TenantTier) -> float:
        """Расчёт базовой стоимости"""
        return self.TIER_PRICES.get(tier, 0)
        
    def calculate_overage(self, quotas: Dict[ResourceType, ResourceQuota]) -> float:
        """Расчёт перерасхода"""
        overage = 0
        
        for rt, quota in quotas.items():
            if quota.used > quota.limit:
                excess = quota.used - quota.limit
                rate = self.OVERAGE_PRICES.get(rt, 0)
                overage += excess * rate
                
        return overage


class MultiTenancyPlatform:
    """Платформа мультитенантности"""
    
    def __init__(self):
        self.tenants: Dict[str, Tenant] = {}
        self.users: Dict[str, List[TenantUser]] = {}  # tenant_id -> users
        self.usage: Dict[str, List[TenantUsage]] = {}  # tenant_id -> usage
        self.invoices: Dict[str, List[TenantInvoice]] = {}  # tenant_id -> invoices
        
        self.quota_manager = QuotaManager()
        self.billing = BillingCalculator()
        
    def create_tenant(self, name: str, owner_email: str,
                     tier: TenantTier = TenantTier.FREE,
                     isolation: IsolationLevel = IsolationLevel.SHARED) -> Tenant:
        """Создание тенанта"""
        slug = name.lower().replace(" ", "-").replace("_", "-")
        
        tenant = Tenant(
            tenant_id=f"tenant_{uuid.uuid4().hex[:8]}",
            name=name,
            slug=slug,
            tier=tier,
            isolation_level=isolation,
            owner_email=owner_email,
            namespace=f"ns-{slug}",
            quotas=self.quota_manager.create_quotas(tier),
            config=TenantConfig(
                config_id=f"config_{uuid.uuid4().hex[:8]}",
                api_key_prefix=f"{slug}_"
            )
        )
        
        self.tenants[tenant.tenant_id] = tenant
        self.users[tenant.tenant_id] = []
        self.usage[tenant.tenant_id] = []
        self.invoices[tenant.tenant_id] = []
        
        return tenant
        
    def activate_tenant(self, tenant_id: str) -> bool:
        """Активация тенанта"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
            
        tenant.status = TenantStatus.ACTIVE
        tenant.activated_at = datetime.now()
        return True
        
    def suspend_tenant(self, tenant_id: str, reason: str = "") -> bool:
        """Приостановка тенанта"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
            
        tenant.status = TenantStatus.SUSPENDED
        tenant.suspended_at = datetime.now()
        tenant.metadata["suspension_reason"] = reason
        return True
        
    def upgrade_tier(self, tenant_id: str, new_tier: TenantTier) -> bool:
        """Повышение уровня"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
            
        old_tier = tenant.tier
        tenant.tier = new_tier
        
        # Update quotas
        new_limits = self.quota_manager.get_limits(new_tier)
        for rt, limit in new_limits.items():
            if rt in tenant.quotas:
                tenant.quotas[rt].limit = limit
            else:
                tenant.quotas[rt] = ResourceQuota(resource_type=rt, limit=limit)
                
        tenant.metadata["tier_history"] = tenant.metadata.get("tier_history", [])
        tenant.metadata["tier_history"].append({
            "from": old_tier.value,
            "to": new_tier.value,
            "date": datetime.now().isoformat()
        })
        
        return True
        
    def add_user(self, tenant_id: str, email: str, name: str,
                role: str = "member") -> Optional[TenantUser]:
        """Добавление пользователя"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return None
            
        # Check quota
        users_quota = tenant.quotas.get(ResourceType.USERS)
        if users_quota and not self.quota_manager.check_quota(users_quota, 1):
            return None
            
        user = TenantUser(
            user_id=f"user_{uuid.uuid4().hex[:8]}",
            tenant_id=tenant_id,
            email=email,
            name=name,
            role=role
        )
        
        self.users[tenant_id].append(user)
        
        if users_quota:
            self.quota_manager.consume_quota(users_quota, 1)
            
        return user
        
    def record_usage(self, tenant_id: str, api_calls: int = 0,
                    storage_bytes: int = 0, compute_seconds: int = 0) -> Optional[TenantUsage]:
        """Запись использования"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return None
            
        usage = TenantUsage(
            usage_id=f"usage_{uuid.uuid4().hex[:8]}",
            tenant_id=tenant_id,
            period_end=datetime.now(),
            api_calls=api_calls,
            storage_bytes=storage_bytes,
            compute_seconds=compute_seconds
        )
        
        # Update quotas
        if ResourceType.API_CALLS in tenant.quotas:
            tenant.quotas[ResourceType.API_CALLS].used += api_calls
            
        self.usage[tenant_id].append(usage)
        return usage
        
    def generate_invoice(self, tenant_id: str) -> Optional[TenantInvoice]:
        """Генерация счёта"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return None
            
        base_cost = self.billing.calculate_base_cost(tenant.tier)
        overage = self.billing.calculate_overage(tenant.quotas)
        
        subtotal = base_cost + overage
        tax = subtotal * 0.1  # 10% tax
        
        invoice = TenantInvoice(
            invoice_id=f"inv_{uuid.uuid4().hex[:8]}",
            tenant_id=tenant_id,
            period_start=datetime.now() - timedelta(days=30),
            period_end=datetime.now(),
            subtotal=subtotal,
            tax=tax,
            total=subtotal + tax
        )
        
        self.invoices[tenant_id].append(invoice)
        return invoice
        
    def get_tenant_metrics(self, tenant_id: str) -> Dict[str, Any]:
        """Метрики тенанта"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return {}
            
        users = self.users.get(tenant_id, [])
        usages = self.usage.get(tenant_id, [])
        
        return {
            "tenant_id": tenant_id,
            "name": tenant.name,
            "tier": tenant.tier.value,
            "status": tenant.status.value,
            "users_count": len(users),
            "api_calls_total": sum(u.api_calls for u in usages),
            "storage_used": sum(u.storage_bytes for u in usages),
            "quota_utilization": {
                rt.value: q.utilization for rt, q in tenant.quotas.items()
            }
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика платформы"""
        active = [t for t in self.tenants.values() if t.status == TenantStatus.ACTIVE]
        
        by_tier = {}
        for tenant in self.tenants.values():
            tier = tenant.tier.value
            if tier not in by_tier:
                by_tier[tier] = 0
            by_tier[tier] += 1
            
        return {
            "total_tenants": len(self.tenants),
            "active_tenants": len(active),
            "suspended_tenants": len([t for t in self.tenants.values() if t.status == TenantStatus.SUSPENDED]),
            "tenants_by_tier": by_tier,
            "total_users": sum(len(u) for u in self.users.values()),
            "total_invoices": sum(len(i) for i in self.invoices.values()),
            "total_revenue": sum(
                inv.total for invs in self.invoices.values() for inv in invs if inv.status == "paid"
            )
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 222: Multi-Tenancy Platform")
    print("=" * 60)
    
    platform = MultiTenancyPlatform()
    print("✓ Multi-Tenancy Platform created")
    
    # Create tenants
    print("\n🏢 Creating Tenants...")
    
    tenants_config = [
        ("Acme Corp", "admin@acme.com", TenantTier.ENTERPRISE, IsolationLevel.DEDICATED),
        ("StartupXYZ", "ceo@startupxyz.io", TenantTier.PROFESSIONAL, IsolationLevel.NAMESPACE),
        ("SmallBiz", "owner@smallbiz.com", TenantTier.STARTER, IsolationLevel.SHARED),
        ("FreeTier User", "user@free.com", TenantTier.FREE, IsolationLevel.SHARED),
        ("GrowthCo", "team@growth.co", TenantTier.PROFESSIONAL, IsolationLevel.NAMESPACE),
    ]
    
    tenants = []
    for name, email, tier, isolation in tenants_config:
        tenant = platform.create_tenant(name, email, tier, isolation)
        platform.activate_tenant(tenant.tenant_id)
        tenants.append(tenant)
        print(f"  ✓ {name}: {tier.value} ({isolation.value})")
        
    # Add users
    print("\n👥 Adding Users...")
    
    for tenant in tenants:
        num_users = random.randint(2, 10)
        for i in range(num_users):
            role = "admin" if i == 0 else "member"
            platform.add_user(
                tenant.tenant_id,
                f"user{i+1}@{tenant.slug}.com",
                f"User {i+1}",
                role
            )
        print(f"  ✓ {tenant.name}: {num_users} users")
        
    # Record usage
    print("\n📊 Recording Usage...")
    
    for tenant in tenants:
        api_calls = random.randint(1000, 500000)
        storage = random.randint(100000000, 5000000000)  # bytes
        compute = random.randint(1000, 100000)  # seconds
        
        platform.record_usage(tenant.tenant_id, api_calls, storage, compute)
        print(f"  ✓ {tenant.name}: {api_calls:,} API calls")
        
    # Upgrade a tenant
    print("\n⬆️ Upgrading Tenant...")
    platform.upgrade_tier(tenants[2].tenant_id, TenantTier.PROFESSIONAL)
    print(f"  ✓ {tenants[2].name}: starter -> professional")
    
    # Suspend a tenant
    print("\n⏸ Suspending Tenant...")
    platform.suspend_tenant(tenants[3].tenant_id, "Payment overdue")
    print(f"  ✓ {tenants[3].name}: suspended")
    
    # Generate invoices
    print("\n💰 Generating Invoices...")
    
    for tenant in tenants:
        invoice = platform.generate_invoice(tenant.tenant_id)
        if invoice and invoice.total > 0:
            print(f"  ✓ {tenant.name}: ${invoice.total:.2f}")
            
    # Display tenants
    print("\n🏢 Tenant Inventory:")
    
    print("\n  ┌────────────────────┬──────────────┬────────────┬──────────┬─────────┐")
    print("  │ Tenant             │ Tier         │ Isolation  │ Users    │ Status  │")
    print("  ├────────────────────┼──────────────┼────────────┼──────────┼─────────┤")
    
    for tenant in platform.tenants.values():
        name = tenant.name[:18].ljust(18)
        tier = tenant.tier.value[:12].ljust(12)
        isolation = tenant.isolation_level.value[:10].ljust(10)
        users = str(len(platform.users.get(tenant.tenant_id, []))).center(8)
        
        status_icons = {
            TenantStatus.ACTIVE: "🟢",
            TenantStatus.SUSPENDED: "🟡",
            TenantStatus.PENDING: "⚪",
            TenantStatus.TERMINATED: "🔴"
        }
        status = f"{status_icons.get(tenant.status, '⚪')}"[:7].ljust(7)
        
        print(f"  │ {name} │ {tier} │ {isolation} │ {users} │ {status} │")
        
    print("  └────────────────────┴──────────────┴────────────┴──────────┴─────────┘")
    
    # Quota utilization
    print("\n📊 Quota Utilization:")
    
    for tenant in list(platform.tenants.values())[:3]:
        print(f"\n  {tenant.name} ({tenant.tier.value}):")
        
        for rt, quota in tenant.quotas.items():
            if quota.limit > 0:
                util = quota.utilization
                bar_len = int(util / 5)
                bar = "█" * bar_len + "░" * (20 - bar_len)
                status = "🔴" if util > 90 else "🟡" if util > 70 else "🟢"
                print(f"    {status} {rt.value:12s} [{bar}] {util:5.1f}%")
                
    # Tenants by tier
    print("\n📈 Tenants by Tier:")
    
    stats = platform.get_statistics()
    
    for tier, count in stats["tenants_by_tier"].items():
        bar = "█" * count + "░" * (5 - count)
        print(f"  {tier:15s} [{bar}] {count}")
        
    # Revenue
    print("\n💵 Revenue by Tenant:")
    
    for tenant in platform.tenants.values():
        invoices = platform.invoices.get(tenant.tenant_id, [])
        total = sum(inv.total for inv in invoices)
        
        if total > 0:
            bar_len = min(20, int(total / 50))
            bar = "█" * bar_len + "░" * (20 - bar_len)
            print(f"  {tenant.name:15s} [{bar}] ${total:.2f}")
            
    # Tenant metrics
    print("\n📊 Tenant Metrics:")
    
    for tenant in list(platform.tenants.values())[:3]:
        metrics = platform.get_tenant_metrics(tenant.tenant_id)
        print(f"\n  {metrics['name']}:")
        print(f"    Users: {metrics['users_count']}")
        print(f"    API Calls: {metrics['api_calls_total']:,}")
        print(f"    Storage: {metrics['storage_used'] / (1024**3):.2f} GB")
        
    # Isolation breakdown
    print("\n🔒 Isolation Levels:")
    
    by_isolation = {}
    for tenant in platform.tenants.values():
        level = tenant.isolation_level.value
        if level not in by_isolation:
            by_isolation[level] = 0
        by_isolation[level] += 1
        
    for level, count in by_isolation.items():
        icon = "🔐" if level == "dedicated" else "🔒" if level == "namespace" else "🔓"
        print(f"  {icon} {level:12s}: {count} tenants")
        
    # Statistics
    print("\n📈 Platform Statistics:")
    
    print(f"\n  Total Tenants: {stats['total_tenants']}")
    print(f"  Active: {stats['active_tenants']}")
    print(f"  Suspended: {stats['suspended_tenants']}")
    print(f"  Total Users: {stats['total_users']}")
    print(f"  Total Invoices: {stats['total_invoices']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                     Multi-Tenancy Dashboard                         │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Tenants:                 {stats['total_tenants']:>12}                        │")
    print(f"│ Active Tenants:                {stats['active_tenants']:>12}                        │")
    print(f"│ Total Users:                   {stats['total_users']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Invoices:                {stats['total_invoices']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Multi-Tenancy Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
