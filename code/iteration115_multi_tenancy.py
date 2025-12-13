#!/usr/bin/env python3
"""
Server Init - Iteration 115: Multi-Tenancy Platform
Платформа мультитенантности

Функционал:
- Tenant Management - управление арендаторами
- Resource Isolation - изоляция ресурсов
- Quota Management - управление квотами
- Billing & Metering - биллинг и учёт
- Access Control - контроль доступа
- Tenant Provisioning - провизионинг
- Data Segregation - разделение данных
- Tenant Analytics - аналитика по арендаторам
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from collections import defaultdict
import uuid
import random


class TenantTier(Enum):
    """Уровень арендатора"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class TenantStatus(Enum):
    """Статус арендатора"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    PENDING = "pending"
    ARCHIVED = "archived"


class IsolationLevel(Enum):
    """Уровень изоляции"""
    SHARED = "shared"
    NAMESPACE = "namespace"
    DEDICATED = "dedicated"
    ISOLATED = "isolated"


class ResourceType(Enum):
    """Тип ресурса"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    API_CALLS = "api_calls"
    USERS = "users"
    PROJECTS = "projects"


class BillingPeriod(Enum):
    """Период биллинга"""
    MONTHLY = "monthly"
    ANNUAL = "annual"
    PAY_AS_YOU_GO = "pay_as_you_go"


@dataclass
class ResourceQuota:
    """Квота ресурса"""
    resource_type: ResourceType
    limit: float = 0.0
    used: float = 0.0
    reserved: float = 0.0
    
    @property
    def available(self) -> float:
        return max(0, self.limit - self.used - self.reserved)
    
    @property
    def utilization(self) -> float:
        return (self.used / self.limit * 100) if self.limit > 0 else 0


@dataclass
class TierLimits:
    """Лимиты уровня"""
    tier: TenantTier
    cpu_cores: int = 2
    memory_gb: int = 4
    storage_gb: int = 10
    api_calls_monthly: int = 10000
    users: int = 5
    projects: int = 3
    price_monthly: float = 0.0


@dataclass
class Tenant:
    """Арендатор"""
    tenant_id: str
    name: str = ""
    
    # Organization
    organization: str = ""
    domain: str = ""
    
    # Status
    status: TenantStatus = TenantStatus.PENDING
    tier: TenantTier = TenantTier.FREE
    
    # Isolation
    isolation_level: IsolationLevel = IsolationLevel.SHARED
    namespace: str = ""
    
    # Quotas
    quotas: Dict[ResourceType, ResourceQuota] = field(default_factory=dict)
    
    # Billing
    billing_period: BillingPeriod = BillingPeriod.MONTHLY
    billing_email: str = ""
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Settings
    settings: Dict[str, Any] = field(default_factory=dict)
    
    # Stats
    users_count: int = 0
    projects_count: int = 0


@dataclass
class TenantUser:
    """Пользователь арендатора"""
    user_id: str
    tenant_id: str = ""
    
    # Identity
    email: str = ""
    name: str = ""
    
    # Role
    role: str = "member"  # owner, admin, member, viewer
    
    # Status
    active: bool = True
    
    # Timestamps
    joined_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None


@dataclass
class UsageRecord:
    """Запись использования"""
    record_id: str
    tenant_id: str = ""
    
    # Resource
    resource_type: ResourceType = ResourceType.API_CALLS
    
    # Amount
    amount: float = 0.0
    unit: str = ""
    
    # Time
    timestamp: datetime = field(default_factory=datetime.now)
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)


@dataclass
class Invoice:
    """Счёт"""
    invoice_id: str
    tenant_id: str = ""
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Items
    line_items: List[Dict[str, Any]] = field(default_factory=list)
    
    # Totals
    subtotal: float = 0.0
    tax: float = 0.0
    total: float = 0.0
    
    # Status
    status: str = "draft"  # draft, sent, paid, overdue
    due_date: datetime = field(default_factory=datetime.now)
    paid_at: Optional[datetime] = None


class TierManager:
    """Менеджер уровней"""
    
    def __init__(self):
        self.tiers: Dict[TenantTier, TierLimits] = {
            TenantTier.FREE: TierLimits(TenantTier.FREE, 1, 1, 5, 5000, 3, 1, 0),
            TenantTier.STARTER: TierLimits(TenantTier.STARTER, 2, 4, 20, 50000, 10, 5, 29),
            TenantTier.PROFESSIONAL: TierLimits(TenantTier.PROFESSIONAL, 8, 16, 100, 500000, 50, 20, 99),
            TenantTier.ENTERPRISE: TierLimits(TenantTier.ENTERPRISE, 32, 64, 1000, 5000000, 500, 100, 499),
            TenantTier.CUSTOM: TierLimits(TenantTier.CUSTOM, 0, 0, 0, 0, 0, 0, 0)
        }
        
    def get_limits(self, tier: TenantTier) -> TierLimits:
        """Получить лимиты уровня"""
        return self.tiers.get(tier, self.tiers[TenantTier.FREE])


class TenantManager:
    """Менеджер арендаторов"""
    
    def __init__(self, tier_manager: TierManager):
        self.tier_manager = tier_manager
        self.tenants: Dict[str, Tenant] = {}
        
    def create(self, name: str, organization: str,
                tier: TenantTier = TenantTier.FREE,
                **kwargs) -> Tenant:
        """Создание арендатора"""
        tenant = Tenant(
            tenant_id=f"tenant_{uuid.uuid4().hex[:8]}",
            name=name,
            organization=organization,
            tier=tier,
            namespace=f"ns-{name.lower().replace(' ', '-')}-{uuid.uuid4().hex[:4]}",
            status=TenantStatus.ACTIVE,
            **kwargs
        )
        
        # Initialize quotas from tier
        limits = self.tier_manager.get_limits(tier)
        tenant.quotas = {
            ResourceType.CPU: ResourceQuota(ResourceType.CPU, limits.cpu_cores),
            ResourceType.MEMORY: ResourceQuota(ResourceType.MEMORY, limits.memory_gb),
            ResourceType.STORAGE: ResourceQuota(ResourceType.STORAGE, limits.storage_gb),
            ResourceType.API_CALLS: ResourceQuota(ResourceType.API_CALLS, limits.api_calls_monthly),
            ResourceType.USERS: ResourceQuota(ResourceType.USERS, limits.users),
            ResourceType.PROJECTS: ResourceQuota(ResourceType.PROJECTS, limits.projects)
        }
        
        self.tenants[tenant.tenant_id] = tenant
        return tenant
        
    def upgrade_tier(self, tenant_id: str, new_tier: TenantTier) -> Dict[str, Any]:
        """Обновление уровня"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return {"status": "error", "message": "Tenant not found"}
            
        old_tier = tenant.tier
        tenant.tier = new_tier
        
        # Update quotas
        limits = self.tier_manager.get_limits(new_tier)
        tenant.quotas[ResourceType.CPU].limit = limits.cpu_cores
        tenant.quotas[ResourceType.MEMORY].limit = limits.memory_gb
        tenant.quotas[ResourceType.STORAGE].limit = limits.storage_gb
        tenant.quotas[ResourceType.API_CALLS].limit = limits.api_calls_monthly
        tenant.quotas[ResourceType.USERS].limit = limits.users
        tenant.quotas[ResourceType.PROJECTS].limit = limits.projects
        
        tenant.updated_at = datetime.now()
        
        return {
            "status": "success",
            "old_tier": old_tier.value,
            "new_tier": new_tier.value
        }
        
    def suspend(self, tenant_id: str, reason: str = "") -> bool:
        """Приостановка арендатора"""
        tenant = self.tenants.get(tenant_id)
        if tenant:
            tenant.status = TenantStatus.SUSPENDED
            tenant.updated_at = datetime.now()
            return True
        return False


class QuotaManager:
    """Менеджер квот"""
    
    def __init__(self, tenant_manager: TenantManager):
        self.tenant_manager = tenant_manager
        
    def check_quota(self, tenant_id: str, 
                     resource_type: ResourceType,
                     amount: float = 1) -> Dict[str, Any]:
        """Проверка квоты"""
        tenant = self.tenant_manager.tenants.get(tenant_id)
        if not tenant:
            return {"allowed": False, "reason": "Tenant not found"}
            
        quota = tenant.quotas.get(resource_type)
        if not quota:
            return {"allowed": False, "reason": "Quota not configured"}
            
        if quota.available >= amount:
            return {
                "allowed": True,
                "available": quota.available,
                "limit": quota.limit
            }
        else:
            return {
                "allowed": False,
                "reason": "Quota exceeded",
                "available": quota.available,
                "requested": amount
            }
            
    def consume(self, tenant_id: str, resource_type: ResourceType,
                 amount: float) -> bool:
        """Потребление ресурса"""
        tenant = self.tenant_manager.tenants.get(tenant_id)
        if not tenant:
            return False
            
        quota = tenant.quotas.get(resource_type)
        if not quota or quota.available < amount:
            return False
            
        quota.used += amount
        return True
        
    def release(self, tenant_id: str, resource_type: ResourceType,
                 amount: float) -> bool:
        """Освобождение ресурса"""
        tenant = self.tenant_manager.tenants.get(tenant_id)
        if not tenant:
            return False
            
        quota = tenant.quotas.get(resource_type)
        if not quota:
            return False
            
        quota.used = max(0, quota.used - amount)
        return True


class BillingManager:
    """Менеджер биллинга"""
    
    def __init__(self, tenant_manager: TenantManager, tier_manager: TierManager):
        self.tenant_manager = tenant_manager
        self.tier_manager = tier_manager
        self.usage_records: List[UsageRecord] = []
        self.invoices: Dict[str, Invoice] = {}
        
    def record_usage(self, tenant_id: str, resource_type: ResourceType,
                      amount: float, unit: str = "") -> UsageRecord:
        """Запись использования"""
        record = UsageRecord(
            record_id=f"usage_{uuid.uuid4().hex[:8]}",
            tenant_id=tenant_id,
            resource_type=resource_type,
            amount=amount,
            unit=unit
        )
        self.usage_records.append(record)
        return record
        
    def generate_invoice(self, tenant_id: str) -> Invoice:
        """Генерация счёта"""
        tenant = self.tenant_manager.tenants.get(tenant_id)
        if not tenant:
            return None
            
        limits = self.tier_manager.get_limits(tenant.tier)
        
        invoice = Invoice(
            invoice_id=f"inv_{uuid.uuid4().hex[:8]}",
            tenant_id=tenant_id,
            period_start=datetime.now() - timedelta(days=30),
            period_end=datetime.now(),
            due_date=datetime.now() + timedelta(days=30)
        )
        
        # Base subscription
        invoice.line_items.append({
            "description": f"{tenant.tier.value.title()} Plan",
            "amount": limits.price_monthly
        })
        
        # Calculate overage
        for rt, quota in tenant.quotas.items():
            if quota.used > quota.limit:
                overage = quota.used - quota.limit
                overage_cost = overage * self._get_overage_rate(rt)
                if overage_cost > 0:
                    invoice.line_items.append({
                        "description": f"{rt.value} overage ({overage:.0f} units)",
                        "amount": overage_cost
                    })
                    
        invoice.subtotal = sum(item["amount"] for item in invoice.line_items)
        invoice.tax = invoice.subtotal * 0.1  # 10% tax
        invoice.total = invoice.subtotal + invoice.tax
        
        self.invoices[invoice.invoice_id] = invoice
        return invoice
        
    def _get_overage_rate(self, resource_type: ResourceType) -> float:
        """Ставка за превышение"""
        rates = {
            ResourceType.CPU: 10.0,
            ResourceType.MEMORY: 5.0,
            ResourceType.STORAGE: 0.1,
            ResourceType.API_CALLS: 0.001,
            ResourceType.USERS: 5.0,
            ResourceType.PROJECTS: 2.0
        }
        return rates.get(resource_type, 1.0)


class UserManager:
    """Менеджер пользователей"""
    
    def __init__(self, tenant_manager: TenantManager, quota_manager: QuotaManager):
        self.tenant_manager = tenant_manager
        self.quota_manager = quota_manager
        self.users: Dict[str, TenantUser] = {}
        
    def add_user(self, tenant_id: str, email: str, name: str,
                  role: str = "member") -> Optional[TenantUser]:
        """Добавление пользователя"""
        # Check quota
        check = self.quota_manager.check_quota(tenant_id, ResourceType.USERS)
        if not check.get("allowed"):
            return None
            
        user = TenantUser(
            user_id=f"user_{uuid.uuid4().hex[:8]}",
            tenant_id=tenant_id,
            email=email,
            name=name,
            role=role
        )
        
        self.quota_manager.consume(tenant_id, ResourceType.USERS, 1)
        self.users[user.user_id] = user
        
        tenant = self.tenant_manager.tenants.get(tenant_id)
        if tenant:
            tenant.users_count += 1
            
        return user
        
    def get_tenant_users(self, tenant_id: str) -> List[TenantUser]:
        """Пользователи арендатора"""
        return [u for u in self.users.values() if u.tenant_id == tenant_id]


class MultiTenancyPlatform:
    """Платформа мультитенантности"""
    
    def __init__(self):
        self.tier_manager = TierManager()
        self.tenant_manager = TenantManager(self.tier_manager)
        self.quota_manager = QuotaManager(self.tenant_manager)
        self.billing_manager = BillingManager(self.tenant_manager, self.tier_manager)
        self.user_manager = UserManager(self.tenant_manager, self.quota_manager)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        tenants = list(self.tenant_manager.tenants.values())
        users = list(self.user_manager.users.values())
        
        by_tier = defaultdict(int)
        by_status = defaultdict(int)
        
        for t in tenants:
            by_tier[t.tier.value] += 1
            by_status[t.status.value] += 1
            
        total_mrr = sum(
            self.tier_manager.get_limits(t.tier).price_monthly
            for t in tenants if t.status == TenantStatus.ACTIVE
        )
        
        return {
            "total_tenants": len(tenants),
            "total_users": len(users),
            "tenants_by_tier": dict(by_tier),
            "tenants_by_status": dict(by_status),
            "total_invoices": len(self.billing_manager.invoices),
            "monthly_recurring_revenue": total_mrr
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 115: Multi-Tenancy Platform")
    print("=" * 60)
    
    async def demo():
        platform = MultiTenancyPlatform()
        print("✓ Multi-Tenancy Platform created")
        
        # Show tier pricing
        print("\n💰 Tier Pricing:")
        
        for tier in TenantTier:
            limits = platform.tier_manager.get_limits(tier)
            print(f"  {tier.value.upper():15} ${limits.price_monthly:>6.0f}/mo")
            print(f"    CPU: {limits.cpu_cores} cores, Memory: {limits.memory_gb} GB, Storage: {limits.storage_gb} GB")
            print(f"    Users: {limits.users}, Projects: {limits.projects}, API: {limits.api_calls_monthly:,}")
            
        # Create tenants
        print("\n🏢 Creating Tenants...")
        
        tenants_data = [
            ("Acme Corp", "Acme Corporation", TenantTier.ENTERPRISE),
            ("Startup Inc", "Startup Inc", TenantTier.PROFESSIONAL),
            ("Small Biz", "Small Business LLC", TenantTier.STARTER),
            ("Dev Team", "Developer Team", TenantTier.STARTER),
            ("Free User", "Individual", TenantTier.FREE),
            ("Trial Co", "Trial Company", TenantTier.FREE)
        ]
        
        created_tenants = []
        for name, org, tier in tenants_data:
            tenant = platform.tenant_manager.create(
                name, org, tier,
                domain=f"{name.lower().replace(' ', '')}.example.com"
            )
            created_tenants.append(tenant)
            
            limits = platform.tier_manager.get_limits(tier)
            print(f"  ✓ {name} ({tier.value}) - ${limits.price_monthly}/mo")
            print(f"    Namespace: {tenant.namespace}")
            
        # Add users to tenants
        print("\n👥 Adding Users...")
        
        for tenant in created_tenants[:3]:
            limits = platform.tier_manager.get_limits(tenant.tier)
            num_users = min(limits.users, random.randint(2, 10))
            
            for i in range(num_users):
                role = "owner" if i == 0 else "admin" if i == 1 else "member"
                user = platform.user_manager.add_user(
                    tenant.tenant_id,
                    f"user{i}@{tenant.domain}",
                    f"User {i}",
                    role
                )
                
            users = platform.user_manager.get_tenant_users(tenant.tenant_id)
            print(f"  {tenant.name}: {len(users)} users added")
            
        # Simulate resource usage
        print("\n📊 Simulating Resource Usage...")
        
        for tenant in created_tenants:
            for rt, quota in tenant.quotas.items():
                # Random usage
                usage = random.uniform(0.3, 1.1) * quota.limit
                quota.used = usage
                
                # Record usage
                platform.billing_manager.record_usage(
                    tenant.tenant_id, rt, usage
                )
                
        # Show quota status
        print("\n📈 Quota Status:")
        
        for tenant in created_tenants[:3]:
            print(f"\n  {tenant.name} ({tenant.tier.value}):")
            for rt, quota in tenant.quotas.items():
                bar_len = 20
                filled = int(bar_len * min(quota.utilization / 100, 1))
                bar = "█" * filled + "░" * (bar_len - filled)
                warn = "⚠️" if quota.utilization > 100 else "✓" if quota.utilization < 80 else "!"
                print(f"    {rt.value:12}: [{bar}] {quota.utilization:5.1f}% {warn}")
                
        # Check quota
        print("\n🔍 Quota Checks:")
        
        checks = [
            (created_tenants[0], ResourceType.API_CALLS, 1000),
            (created_tenants[4], ResourceType.USERS, 1),
            (created_tenants[2], ResourceType.STORAGE, 50)
        ]
        
        for tenant, rt, amount in checks:
            result = platform.quota_manager.check_quota(tenant.tenant_id, rt, amount)
            status = "✅ Allowed" if result.get("allowed") else "❌ Denied"
            print(f"  {tenant.name} - {rt.value} ({amount}): {status}")
            
        # Upgrade tier
        print("\n⬆️ Tier Upgrades:")
        
        upgrade_tenant = created_tenants[3]  # Dev Team
        old_tier = upgrade_tenant.tier
        result = platform.tenant_manager.upgrade_tier(
            upgrade_tenant.tenant_id, 
            TenantTier.PROFESSIONAL
        )
        
        print(f"  {upgrade_tenant.name}: {result['old_tier']} → {result['new_tier']}")
        print(f"    New limits: CPU={upgrade_tenant.quotas[ResourceType.CPU].limit}, Memory={upgrade_tenant.quotas[ResourceType.MEMORY].limit}GB")
        
        # Generate invoices
        print("\n💳 Generating Invoices...")
        
        for tenant in created_tenants[:4]:
            invoice = platform.billing_manager.generate_invoice(tenant.tenant_id)
            if invoice:
                print(f"\n  {tenant.name}:")
                for item in invoice.line_items:
                    print(f"    {item['description']}: ${item['amount']:.2f}")
                print(f"    Subtotal: ${invoice.subtotal:.2f}")
                print(f"    Tax: ${invoice.tax:.2f}")
                print(f"    Total: ${invoice.total:.2f}")
                
        # Suspend tenant
        print("\n⏸️ Suspending Tenant...")
        
        suspend_tenant = created_tenants[-1]
        platform.tenant_manager.suspend(suspend_tenant.tenant_id, "Non-payment")
        print(f"  {suspend_tenant.name}: {suspend_tenant.status.value}")
        
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Tenants: {stats['total_tenants']}")
        for tier, count in stats['tenants_by_tier'].items():
            print(f"    {tier}: {count}")
            
        print(f"\n  Status:")
        for status, count in stats['tenants_by_status'].items():
            print(f"    {status}: {count}")
            
        print(f"\n  Users: {stats['total_users']}")
        print(f"  Invoices: {stats['total_invoices']}")
        print(f"  MRR: ${stats['monthly_recurring_revenue']:.2f}")
        
        # Dashboard
        print("\n📋 Multi-Tenancy Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │              Multi-Tenancy Overview                         │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Tenants:      {stats['total_tenants']:>10}                        │")
        print(f"  │ Total Users:        {stats['total_users']:>10}                        │")
        print(f"  │ Total Invoices:     {stats['total_invoices']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Monthly Revenue:    ${stats['monthly_recurring_revenue']:>9.2f}                   │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Enterprise:         {stats['tenants_by_tier'].get('enterprise', 0):>10}                        │")
        print(f"  │ Professional:       {stats['tenants_by_tier'].get('professional', 0):>10}                        │")
        print(f"  │ Starter:            {stats['tenants_by_tier'].get('starter', 0):>10}                        │")
        print(f"  │ Free:               {stats['tenants_by_tier'].get('free', 0):>10}                        │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Multi-Tenancy Platform initialized!")
    print("=" * 60)
