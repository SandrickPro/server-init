#!/usr/bin/env python3
"""
Server Init - Iteration 74: Multi-Tenancy Management Platform
Платформа управления мультитенантностью

Функционал:
- Tenant Provisioning - создание тенантов
- Resource Isolation - изоляция ресурсов
- Quota Management - управление квотами
- Billing Integration - интеграция с биллингом
- Tenant Configuration - конфигурация тенантов
- Data Isolation - изоляция данных
- Access Control - контроль доступа
- Tenant Analytics - аналитика по тенантам
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


class TenantStatus(Enum):
    """Статус тенанта"""
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class TenantTier(Enum):
    """Уровень тенанта"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class IsolationLevel(Enum):
    """Уровень изоляции"""
    SHARED = "shared"          # Общие ресурсы
    POOL = "pool"              # Пул ресурсов
    DEDICATED = "dedicated"    # Выделенные ресурсы


class ResourceType(Enum):
    """Тип ресурса"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    BANDWIDTH = "bandwidth"
    API_CALLS = "api_calls"
    USERS = "users"
    PROJECTS = "projects"


@dataclass
class ResourceQuota:
    """Квота на ресурс"""
    resource_type: ResourceType
    limit: float
    used: float = 0.0
    unit: str = ""
    
    @property
    def available(self) -> float:
        return self.limit - self.used
        
    @property
    def usage_percent(self) -> float:
        if self.limit == 0:
            return 0
        return (self.used / self.limit) * 100


@dataclass
class Tenant:
    """Тенант"""
    tenant_id: str
    name: str
    
    # Идентификация
    slug: str = ""
    domain: str = ""
    
    # Статус
    status: TenantStatus = TenantStatus.PENDING
    tier: TenantTier = TenantTier.FREE
    
    # Изоляция
    isolation_level: IsolationLevel = IsolationLevel.SHARED
    
    # Квоты
    quotas: Dict[str, ResourceQuota] = field(default_factory=dict)
    
    # Настройки
    settings: Dict[str, Any] = field(default_factory=dict)
    
    # Метаданные
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    activated_at: Optional[datetime] = None
    
    # Биллинг
    billing_account_id: str = ""


@dataclass
class TenantUser:
    """Пользователь тенанта"""
    user_id: str
    tenant_id: str
    
    # Данные
    email: str = ""
    name: str = ""
    
    # Роль
    role: str = "member"  # owner, admin, member, viewer
    
    # Статус
    active: bool = True
    
    # Время
    joined_at: datetime = field(default_factory=datetime.now)
    last_active_at: Optional[datetime] = None


@dataclass
class TenantResource:
    """Ресурс тенанта"""
    resource_id: str
    tenant_id: str
    
    # Тип
    resource_type: str = ""
    resource_name: str = ""
    
    # Конфигурация
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Статус
    status: str = "active"
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class UsageRecord:
    """Запись использования"""
    record_id: str
    tenant_id: str
    
    # Ресурс
    resource_type: ResourceType = ResourceType.API_CALLS
    
    # Использование
    quantity: float = 0.0
    unit: str = ""
    
    # Время
    timestamp: datetime = field(default_factory=datetime.now)
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


@dataclass
class BillingPlan:
    """Биллинговый план"""
    plan_id: str
    name: str
    tier: TenantTier = TenantTier.FREE
    
    # Цены
    monthly_price: float = 0.0
    annual_price: float = 0.0
    
    # Лимиты
    included_quotas: Dict[str, float] = field(default_factory=dict)
    
    # Дополнительно
    overage_rates: Dict[str, float] = field(default_factory=dict)
    
    # Фичи
    features: List[str] = field(default_factory=list)


@dataclass
class Invoice:
    """Счёт"""
    invoice_id: str
    tenant_id: str
    
    # Период
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Суммы
    subtotal: float = 0.0
    tax: float = 0.0
    total: float = 0.0
    
    # Статус
    status: str = "draft"  # draft, sent, paid, overdue
    
    # Детали
    line_items: List[Dict[str, Any]] = field(default_factory=list)
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None


class QuotaManager:
    """Менеджер квот"""
    
    def __init__(self):
        self.tier_quotas: Dict[TenantTier, Dict[str, ResourceQuota]] = {}
        self._init_tier_quotas()
        
    def _init_tier_quotas(self):
        """Инициализация квот по уровням"""
        self.tier_quotas = {
            TenantTier.FREE: {
                ResourceType.CPU.value: ResourceQuota(ResourceType.CPU, 1, unit="cores"),
                ResourceType.MEMORY.value: ResourceQuota(ResourceType.MEMORY, 512, unit="MB"),
                ResourceType.STORAGE.value: ResourceQuota(ResourceType.STORAGE, 1, unit="GB"),
                ResourceType.API_CALLS.value: ResourceQuota(ResourceType.API_CALLS, 1000, unit="calls/day"),
                ResourceType.USERS.value: ResourceQuota(ResourceType.USERS, 5, unit="users"),
                ResourceType.PROJECTS.value: ResourceQuota(ResourceType.PROJECTS, 3, unit="projects")
            },
            TenantTier.STARTER: {
                ResourceType.CPU.value: ResourceQuota(ResourceType.CPU, 2, unit="cores"),
                ResourceType.MEMORY.value: ResourceQuota(ResourceType.MEMORY, 2048, unit="MB"),
                ResourceType.STORAGE.value: ResourceQuota(ResourceType.STORAGE, 10, unit="GB"),
                ResourceType.API_CALLS.value: ResourceQuota(ResourceType.API_CALLS, 10000, unit="calls/day"),
                ResourceType.USERS.value: ResourceQuota(ResourceType.USERS, 25, unit="users"),
                ResourceType.PROJECTS.value: ResourceQuota(ResourceType.PROJECTS, 10, unit="projects")
            },
            TenantTier.PROFESSIONAL: {
                ResourceType.CPU.value: ResourceQuota(ResourceType.CPU, 8, unit="cores"),
                ResourceType.MEMORY.value: ResourceQuota(ResourceType.MEMORY, 16384, unit="MB"),
                ResourceType.STORAGE.value: ResourceQuota(ResourceType.STORAGE, 100, unit="GB"),
                ResourceType.API_CALLS.value: ResourceQuota(ResourceType.API_CALLS, 100000, unit="calls/day"),
                ResourceType.USERS.value: ResourceQuota(ResourceType.USERS, 100, unit="users"),
                ResourceType.PROJECTS.value: ResourceQuota(ResourceType.PROJECTS, 50, unit="projects")
            },
            TenantTier.ENTERPRISE: {
                ResourceType.CPU.value: ResourceQuota(ResourceType.CPU, 32, unit="cores"),
                ResourceType.MEMORY.value: ResourceQuota(ResourceType.MEMORY, 65536, unit="MB"),
                ResourceType.STORAGE.value: ResourceQuota(ResourceType.STORAGE, 1000, unit="GB"),
                ResourceType.API_CALLS.value: ResourceQuota(ResourceType.API_CALLS, 1000000, unit="calls/day"),
                ResourceType.USERS.value: ResourceQuota(ResourceType.USERS, 1000, unit="users"),
                ResourceType.PROJECTS.value: ResourceQuota(ResourceType.PROJECTS, 500, unit="projects")
            }
        }
        
    def get_quotas_for_tier(self, tier: TenantTier) -> Dict[str, ResourceQuota]:
        """Получение квот для уровня"""
        return {k: ResourceQuota(v.resource_type, v.limit, unit=v.unit) 
                for k, v in self.tier_quotas.get(tier, {}).items()}
                
    def check_quota(self, tenant: Tenant, resource_type: ResourceType,
                     amount: float = 1) -> bool:
        """Проверка квоты"""
        quota = tenant.quotas.get(resource_type.value)
        if not quota:
            return False
            
        return quota.available >= amount
        
    def consume_quota(self, tenant: Tenant, resource_type: ResourceType,
                       amount: float = 1) -> bool:
        """Использование квоты"""
        if not self.check_quota(tenant, resource_type, amount):
            return False
            
        quota = tenant.quotas[resource_type.value]
        quota.used += amount
        return True
        
    def release_quota(self, tenant: Tenant, resource_type: ResourceType,
                       amount: float = 1):
        """Освобождение квоты"""
        quota = tenant.quotas.get(resource_type.value)
        if quota:
            quota.used = max(0, quota.used - amount)


class TenantProvisioner:
    """Провизионер тенантов"""
    
    def __init__(self, quota_manager: QuotaManager):
        self.quota_manager = quota_manager
        
    async def provision(self, tenant: Tenant) -> bool:
        """Провизионирование тенанта"""
        try:
            # 1. Создание namespace/схемы
            await self._create_namespace(tenant)
            
            # 2. Настройка квот
            await self._setup_quotas(tenant)
            
            # 3. Создание базовых ресурсов
            await self._create_base_resources(tenant)
            
            # 4. Активация
            tenant.status = TenantStatus.ACTIVE
            tenant.activated_at = datetime.now()
            
            return True
            
        except Exception as e:
            tenant.status = TenantStatus.PENDING
            return False
            
    async def _create_namespace(self, tenant: Tenant):
        """Создание namespace"""
        await asyncio.sleep(0.1)  # Симуляция
        
    async def _setup_quotas(self, tenant: Tenant):
        """Настройка квот"""
        tenant.quotas = self.quota_manager.get_quotas_for_tier(tenant.tier)
        
    async def _create_base_resources(self, tenant: Tenant):
        """Создание базовых ресурсов"""
        await asyncio.sleep(0.1)  # Симуляция
        
    async def deprovision(self, tenant: Tenant) -> bool:
        """Депровизионирование тенанта"""
        try:
            # 1. Архивирование данных
            await self._archive_data(tenant)
            
            # 2. Удаление ресурсов
            await self._delete_resources(tenant)
            
            # 3. Обновление статуса
            tenant.status = TenantStatus.ARCHIVED
            
            return True
            
        except Exception:
            return False
            
    async def _archive_data(self, tenant: Tenant):
        """Архивирование данных"""
        await asyncio.sleep(0.1)
        
    async def _delete_resources(self, tenant: Tenant):
        """Удаление ресурсов"""
        await asyncio.sleep(0.1)


class BillingManager:
    """Менеджер биллинга"""
    
    def __init__(self):
        self.plans: Dict[str, BillingPlan] = {}
        self.invoices: Dict[str, Invoice] = {}
        self.usage_records: List[UsageRecord] = []
        
        self._init_plans()
        
    def _init_plans(self):
        """Инициализация планов"""
        plans = [
            BillingPlan(
                plan_id="plan_free",
                name="Free",
                tier=TenantTier.FREE,
                monthly_price=0,
                features=["Basic support", "Community access"]
            ),
            BillingPlan(
                plan_id="plan_starter",
                name="Starter",
                tier=TenantTier.STARTER,
                monthly_price=29,
                annual_price=290,
                overage_rates={
                    ResourceType.API_CALLS.value: 0.001,
                    ResourceType.STORAGE.value: 0.1
                },
                features=["Email support", "API access", "Webhooks"]
            ),
            BillingPlan(
                plan_id="plan_professional",
                name="Professional",
                tier=TenantTier.PROFESSIONAL,
                monthly_price=99,
                annual_price=990,
                overage_rates={
                    ResourceType.API_CALLS.value: 0.0005,
                    ResourceType.STORAGE.value: 0.08
                },
                features=["Priority support", "SSO", "Advanced analytics", "Custom integrations"]
            ),
            BillingPlan(
                plan_id="plan_enterprise",
                name="Enterprise",
                tier=TenantTier.ENTERPRISE,
                monthly_price=499,
                annual_price=4990,
                overage_rates={
                    ResourceType.API_CALLS.value: 0.0003,
                    ResourceType.STORAGE.value: 0.05
                },
                features=["24/7 support", "Dedicated account manager", "Custom SLA", "On-premise option"]
            )
        ]
        
        for plan in plans:
            self.plans[plan.plan_id] = plan
            
    def record_usage(self, tenant_id: str, resource_type: ResourceType,
                      quantity: float, unit: str = "") -> UsageRecord:
        """Запись использования"""
        record = UsageRecord(
            record_id=f"usage_{uuid.uuid4().hex[:8]}",
            tenant_id=tenant_id,
            resource_type=resource_type,
            quantity=quantity,
            unit=unit
        )
        
        self.usage_records.append(record)
        return record
        
    def generate_invoice(self, tenant: Tenant,
                          period_start: datetime,
                          period_end: datetime) -> Invoice:
        """Генерация счёта"""
        plan = self.plans.get(f"plan_{tenant.tier.value}")
        
        line_items = []
        subtotal = 0.0
        
        # Базовая плата
        if plan and plan.monthly_price > 0:
            line_items.append({
                "description": f"{plan.name} Plan",
                "quantity": 1,
                "unit_price": plan.monthly_price,
                "amount": plan.monthly_price
            })
            subtotal += plan.monthly_price
            
        # Превышения
        tenant_usage = [u for u in self.usage_records 
                        if u.tenant_id == tenant.tenant_id
                        and period_start <= u.timestamp <= period_end]
                        
        usage_by_type = defaultdict(float)
        for u in tenant_usage:
            usage_by_type[u.resource_type.value] += u.quantity
            
        for res_type, used in usage_by_type.items():
            quota = tenant.quotas.get(res_type)
            if quota and used > quota.limit:
                overage = used - quota.limit
                rate = plan.overage_rates.get(res_type, 0) if plan else 0
                overage_cost = overage * rate
                
                if overage_cost > 0:
                    line_items.append({
                        "description": f"{res_type} overage",
                        "quantity": overage,
                        "unit_price": rate,
                        "amount": overage_cost
                    })
                    subtotal += overage_cost
                    
        tax = subtotal * 0.1  # 10% налог
        
        invoice = Invoice(
            invoice_id=f"inv_{uuid.uuid4().hex[:8]}",
            tenant_id=tenant.tenant_id,
            period_start=period_start,
            period_end=period_end,
            subtotal=subtotal,
            tax=tax,
            total=subtotal + tax,
            line_items=line_items,
            due_date=datetime.now() + timedelta(days=30)
        )
        
        self.invoices[invoice.invoice_id] = invoice
        return invoice


class TenantAnalytics:
    """Аналитика по тенантам"""
    
    def __init__(self):
        self.metrics: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
    def record_metric(self, tenant_id: str, metric_name: str, value: float):
        """Запись метрики"""
        self.metrics[tenant_id].append({
            "metric": metric_name,
            "value": value,
            "timestamp": datetime.now()
        })
        
    def get_tenant_stats(self, tenant: Tenant) -> Dict[str, Any]:
        """Статистика тенанта"""
        quota_usage = {}
        
        for res_type, quota in tenant.quotas.items():
            quota_usage[res_type] = {
                "limit": quota.limit,
                "used": quota.used,
                "available": quota.available,
                "usage_percent": quota.usage_percent
            }
            
        return {
            "tenant_id": tenant.tenant_id,
            "status": tenant.status.value,
            "tier": tenant.tier.value,
            "quota_usage": quota_usage,
            "days_since_creation": (datetime.now() - tenant.created_at).days
        }


class MultiTenancyPlatform:
    """Платформа мультитенантности"""
    
    def __init__(self):
        self.tenants: Dict[str, Tenant] = {}
        self.users: Dict[str, TenantUser] = {}
        self.resources: Dict[str, TenantResource] = {}
        
        self.quota_manager = QuotaManager()
        self.provisioner = TenantProvisioner(self.quota_manager)
        self.billing = BillingManager()
        self.analytics = TenantAnalytics()
        
    async def create_tenant(self, name: str, tier: TenantTier = TenantTier.FREE,
                             owner_email: str = "", **kwargs) -> Tenant:
        """Создание тенанта"""
        slug = name.lower().replace(" ", "-")
        
        tenant = Tenant(
            tenant_id=f"tenant_{uuid.uuid4().hex[:8]}",
            name=name,
            slug=slug,
            tier=tier,
            **kwargs
        )
        
        self.tenants[tenant.tenant_id] = tenant
        
        # Провизионирование
        success = await self.provisioner.provision(tenant)
        
        # Создание владельца
        if success and owner_email:
            await self.add_user(tenant.tenant_id, owner_email, role="owner")
            
        return tenant
        
    async def add_user(self, tenant_id: str, email: str,
                        name: str = "", role: str = "member") -> Optional[TenantUser]:
        """Добавление пользователя"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return None
            
        # Проверка квоты
        if not self.quota_manager.check_quota(tenant, ResourceType.USERS):
            return None
            
        user = TenantUser(
            user_id=f"user_{uuid.uuid4().hex[:8]}",
            tenant_id=tenant_id,
            email=email,
            name=name or email.split("@")[0],
            role=role
        )
        
        self.users[user.user_id] = user
        self.quota_manager.consume_quota(tenant, ResourceType.USERS)
        
        return user
        
    async def create_resource(self, tenant_id: str, resource_type: str,
                               resource_name: str, config: Dict[str, Any] = None) -> Optional[TenantResource]:
        """Создание ресурса"""
        tenant = self.tenants.get(tenant_id)
        if not tenant or tenant.status != TenantStatus.ACTIVE:
            return None
            
        resource = TenantResource(
            resource_id=f"res_{uuid.uuid4().hex[:8]}",
            tenant_id=tenant_id,
            resource_type=resource_type,
            resource_name=resource_name,
            config=config or {}
        )
        
        self.resources[resource.resource_id] = resource
        return resource
        
    async def upgrade_tenant(self, tenant_id: str, new_tier: TenantTier) -> bool:
        """Апгрейд тенанта"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
            
        # Обновляем tier и квоты
        tenant.tier = new_tier
        new_quotas = self.quota_manager.get_quotas_for_tier(new_tier)
        
        # Сохраняем использование
        for res_type, new_quota in new_quotas.items():
            old_quota = tenant.quotas.get(res_type)
            if old_quota:
                new_quota.used = min(old_quota.used, new_quota.limit)
                
        tenant.quotas = new_quotas
        return True
        
    async def suspend_tenant(self, tenant_id: str, reason: str = "") -> bool:
        """Приостановка тенанта"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
            
        tenant.status = TenantStatus.SUSPENDED
        tenant.metadata["suspension_reason"] = reason
        tenant.metadata["suspended_at"] = datetime.now().isoformat()
        
        return True
        
    def get_tenant_users(self, tenant_id: str) -> List[TenantUser]:
        """Получение пользователей тенанта"""
        return [u for u in self.users.values() if u.tenant_id == tenant_id]
        
    def get_tenant_resources(self, tenant_id: str) -> List[TenantResource]:
        """Получение ресурсов тенанта"""
        return [r for r in self.resources.values() if r.tenant_id == tenant_id]
        
    def generate_invoice(self, tenant_id: str) -> Optional[Invoice]:
        """Генерация счёта"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return None
            
        period_end = datetime.now()
        period_start = period_end - timedelta(days=30)
        
        return self.billing.generate_invoice(tenant, period_start, period_end)
        
    def get_stats(self) -> Dict[str, Any]:
        """Статистика платформы"""
        tenants_by_tier = defaultdict(int)
        tenants_by_status = defaultdict(int)
        
        for tenant in self.tenants.values():
            tenants_by_tier[tenant.tier.value] += 1
            tenants_by_status[tenant.status.value] += 1
            
        return {
            "total_tenants": len(self.tenants),
            "total_users": len(self.users),
            "total_resources": len(self.resources),
            "by_tier": dict(tenants_by_tier),
            "by_status": dict(tenants_by_status),
            "billing_plans": len(self.billing.plans),
            "invoices": len(self.billing.invoices)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 74: Multi-Tenancy Management")
    print("=" * 60)
    
    async def demo():
        platform = MultiTenancyPlatform()
        print("✓ Multi-Tenancy Platform created")
        
        # Создание тенантов
        print("\n🏢 Creating Tenants...")
        
        tenant1 = await platform.create_tenant(
            name="Acme Corp",
            tier=TenantTier.PROFESSIONAL,
            owner_email="admin@acme.com",
            domain="acme.example.com"
        )
        print(f"  ✓ Tenant: {tenant1.name} ({tenant1.tier.value})")
        print(f"    Status: {tenant1.status.value}")
        
        tenant2 = await platform.create_tenant(
            name="Startup Inc",
            tier=TenantTier.STARTER,
            owner_email="hello@startup.io"
        )
        print(f"  ✓ Tenant: {tenant2.name} ({tenant2.tier.value})")
        
        tenant3 = await platform.create_tenant(
            name="Free User",
            tier=TenantTier.FREE,
            owner_email="user@gmail.com"
        )
        print(f"  ✓ Tenant: {tenant3.name} ({tenant3.tier.value})")
        
        # Отображение квот
        print("\n📊 Tenant Quotas:")
        
        for tenant in [tenant1, tenant2, tenant3]:
            print(f"\n  {tenant.name} ({tenant.tier.value}):")
            for res_type, quota in list(tenant.quotas.items())[:4]:
                print(f"    {res_type}: {quota.limit} {quota.unit}")
                
        # Добавление пользователей
        print("\n👥 Adding Users...")
        
        users_to_add = [
            (tenant1.tenant_id, "dev1@acme.com", "Developer 1", "member"),
            (tenant1.tenant_id, "dev2@acme.com", "Developer 2", "member"),
            (tenant1.tenant_id, "lead@acme.com", "Team Lead", "admin"),
            (tenant2.tenant_id, "cto@startup.io", "CTO", "admin"),
        ]
        
        for tenant_id, email, name, role in users_to_add:
            user = await platform.add_user(tenant_id, email, name, role)
            if user:
                print(f"  ✓ {user.name} ({user.role}) → {platform.tenants[tenant_id].name}")
                
        # Проверка квот пользователей
        print("\n📈 User Quota Usage:")
        
        for tenant in [tenant1, tenant2]:
            users_quota = tenant.quotas.get(ResourceType.USERS.value)
            if users_quota:
                print(f"  {tenant.name}: {int(users_quota.used)}/{int(users_quota.limit)} users")
                
        # Создание ресурсов
        print("\n🔧 Creating Resources...")
        
        resources = [
            (tenant1.tenant_id, "database", "Production DB", {"engine": "postgres", "size": "100GB"}),
            (tenant1.tenant_id, "storage", "File Storage", {"type": "s3", "bucket": "acme-files"}),
            (tenant1.tenant_id, "api", "REST API", {"version": "v2", "rate_limit": 1000}),
            (tenant2.tenant_id, "database", "App Database", {"engine": "mysql"}),
        ]
        
        for tenant_id, res_type, name, config in resources:
            resource = await platform.create_resource(tenant_id, res_type, name, config)
            if resource:
                tenant = platform.tenants[tenant_id]
                print(f"  ✓ {name} ({res_type}) → {tenant.name}")
                
        # Апгрейд тенанта
        print("\n⬆️ Upgrading Tenant...")
        
        print(f"  Before: {tenant2.name} is {tenant2.tier.value}")
        success = await platform.upgrade_tenant(tenant2.tenant_id, TenantTier.PROFESSIONAL)
        if success:
            print(f"  After: {tenant2.name} is {tenant2.tier.value}")
            
        # Использование ресурсов
        print("\n📊 Recording Usage...")
        
        for tenant in [tenant1, tenant2]:
            # Симуляция использования API
            api_calls = random.randint(5000, 50000)
            platform.billing.record_usage(
                tenant.tenant_id,
                ResourceType.API_CALLS,
                api_calls,
                "calls"
            )
            print(f"  {tenant.name}: {api_calls} API calls")
            
            # Использование storage
            storage_gb = random.uniform(10, 50)
            platform.billing.record_usage(
                tenant.tenant_id,
                ResourceType.STORAGE,
                storage_gb,
                "GB"
            )
            print(f"  {tenant.name}: {storage_gb:.1f} GB storage")
            
        # Генерация счетов
        print("\n💳 Generating Invoices...")
        
        for tenant in [tenant1, tenant2]:
            invoice = platform.generate_invoice(tenant.tenant_id)
            if invoice:
                print(f"\n  Invoice for {tenant.name}:")
                print(f"    Subtotal: ${invoice.subtotal:.2f}")
                print(f"    Tax: ${invoice.tax:.2f}")
                print(f"    Total: ${invoice.total:.2f}")
                
                if invoice.line_items:
                    print(f"    Line items:")
                    for item in invoice.line_items[:3]:
                        print(f"      - {item['description']}: ${item['amount']:.2f}")
                        
        # Приостановка тенанта
        print("\n⏸️ Suspending Tenant...")
        
        await platform.suspend_tenant(tenant3.tenant_id, "Non-payment")
        print(f"  {tenant3.name} status: {tenant3.status.value}")
        
        # Аналитика
        print("\n📈 Tenant Analytics:")
        
        for tenant in [tenant1, tenant2]:
            stats = platform.analytics.get_tenant_stats(tenant)
            print(f"\n  {tenant.name}:")
            print(f"    Tier: {stats['tier']}")
            print(f"    Days since creation: {stats['days_since_creation']}")
            
            for res_type, usage in list(stats['quota_usage'].items())[:3]:
                print(f"    {res_type}: {usage['usage_percent']:.1f}% used")
                
        # Биллинговые планы
        print("\n💰 Billing Plans:")
        
        for plan in platform.billing.plans.values():
            print(f"\n  {plan.name} (${plan.monthly_price}/mo):")
            for feature in plan.features[:3]:
                print(f"    ✓ {feature}")
                
        # Статистика платформы
        print("\n📊 Platform Statistics:")
        stats = platform.get_stats()
        
        print(f"  Total Tenants: {stats['total_tenants']}")
        print(f"  Total Users: {stats['total_users']}")
        print(f"  Total Resources: {stats['total_resources']}")
        
        print(f"\n  By Tier:")
        for tier, count in stats['by_tier'].items():
            print(f"    {tier}: {count}")
            
        print(f"\n  By Status:")
        for status, count in stats['by_status'].items():
            print(f"    {status}: {count}")
            
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Multi-Tenancy Management Platform initialized!")
    print("=" * 60)
