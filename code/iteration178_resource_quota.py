#!/usr/bin/env python3
"""
Server Init - Iteration 178: Resource Quota Platform
Платформа управления квотами ресурсов

Функционал:
- Quota Definition - определение квот
- Resource Tracking - отслеживание ресурсов
- Usage Monitoring - мониторинг использования
- Quota Enforcement - применение квот
- Cost Management - управление затратами
- Alerting - оповещения
- Reporting - отчётность
- Hierarchical Quotas - иерархические квоты
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class ResourceType(Enum):
    """Тип ресурса"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    GPU = "gpu"
    NETWORK = "network"
    PODS = "pods"
    SERVICES = "services"
    SECRETS = "secrets"
    CONFIGMAPS = "configmaps"
    PVC = "persistent_volume_claims"
    LOADBALANCERS = "loadbalancers"
    REQUESTS = "requests"  # API requests
    BANDWIDTH = "bandwidth"


class QuotaScope(Enum):
    """Область применения квоты"""
    ORGANIZATION = "organization"
    TEAM = "team"
    PROJECT = "project"
    NAMESPACE = "namespace"
    USER = "user"


class QuotaStatus(Enum):
    """Статус квоты"""
    ACTIVE = "active"
    EXCEEDED = "exceeded"
    WARNING = "warning"
    DISABLED = "disabled"


class AlertLevel(Enum):
    """Уровень алерта"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class ResourceUnit:
    """Единица измерения ресурса"""
    resource_type: ResourceType
    unit: str = ""  # cores, GB, count
    value: float = 0.0
    
    def __str__(self) -> str:
        return f"{self.value} {self.unit}"


@dataclass
class QuotaLimit:
    """Лимит квоты"""
    resource_type: ResourceType
    
    # Limits
    hard_limit: float = 0.0  # Maximum allowed
    soft_limit: float = 0.0  # Warning threshold
    
    # Current usage
    current_usage: float = 0.0
    
    # Unit
    unit: str = ""
    
    @property
    def usage_percent(self) -> float:
        """Процент использования"""
        if self.hard_limit == 0:
            return 0.0
        return (self.current_usage / self.hard_limit) * 100


@dataclass
class Quota:
    """Квота"""
    quota_id: str
    name: str = ""
    description: str = ""
    
    # Scope
    scope: QuotaScope = QuotaScope.PROJECT
    scope_id: str = ""  # Project ID, Team ID, etc.
    
    # Limits
    limits: Dict[ResourceType, QuotaLimit] = field(default_factory=dict)
    
    # Status
    status: QuotaStatus = QuotaStatus.ACTIVE
    
    # Inheritance
    parent_quota_id: str = ""  # For hierarchical quotas
    inherit_limits: bool = False
    
    # Period
    period: str = "monthly"  # hourly, daily, monthly, unlimited
    period_start: datetime = field(default_factory=datetime.now)
    period_end: Optional[datetime] = None
    
    # Metadata
    labels: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ResourceUsage:
    """Использование ресурсов"""
    usage_id: str
    quota_id: str = ""
    
    # Resource
    resource_type: ResourceType = ResourceType.CPU
    
    # Usage
    amount: float = 0.0
    unit: str = ""
    
    # Source
    source_id: str = ""  # Pod ID, Service ID, etc.
    source_type: str = ""
    
    # Timing
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class QuotaAlert:
    """Алерт квоты"""
    alert_id: str
    quota_id: str = ""
    
    # Alert details
    level: AlertLevel = AlertLevel.WARNING
    resource_type: ResourceType = ResourceType.CPU
    
    # Values
    threshold: float = 0.0
    current_value: float = 0.0
    
    # Message
    message: str = ""
    
    # Timing
    triggered_at: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    acknowledged_by: str = ""


@dataclass
class CostAllocation:
    """Распределение затрат"""
    allocation_id: str
    quota_id: str = ""
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Costs
    costs_by_resource: Dict[str, float] = field(default_factory=dict)
    total_cost: float = 0.0
    
    # Currency
    currency: str = "USD"
    
    # Budget
    budget: float = 0.0
    budget_remaining: float = 0.0


@dataclass
class QuotaReport:
    """Отчёт по квотам"""
    report_id: str
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Summary
    total_quotas: int = 0
    quotas_exceeded: int = 0
    quotas_warning: int = 0
    
    # Usage by resource
    usage_summary: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Cost summary
    total_cost: float = 0.0
    cost_by_scope: Dict[str, float] = field(default_factory=dict)
    
    # Generated
    generated_at: datetime = field(default_factory=datetime.now)


class QuotaStore:
    """Хранилище квот"""
    
    def __init__(self):
        self.quotas: Dict[str, Quota] = {}
        
    def add(self, quota: Quota):
        """Добавление квоты"""
        self.quotas[quota.quota_id] = quota
        
    def get(self, quota_id: str) -> Optional[Quota]:
        """Получение квоты"""
        return self.quotas.get(quota_id)
        
    def list_by_scope(self, scope: QuotaScope) -> List[Quota]:
        """Получение квот по scope"""
        return [q for q in self.quotas.values() if q.scope == scope]
        
    def get_children(self, parent_id: str) -> List[Quota]:
        """Получение дочерних квот"""
        return [q for q in self.quotas.values() if q.parent_quota_id == parent_id]


class UsageTracker:
    """Трекер использования"""
    
    def __init__(self, quota_store: QuotaStore):
        self.quota_store = quota_store
        self.usage_history: List[ResourceUsage] = []
        
    def record_usage(self, quota_id: str, resource_type: ResourceType, amount: float, unit: str = ""):
        """Запись использования"""
        quota = self.quota_store.get(quota_id)
        if not quota:
            return
            
        # Update quota limit
        if resource_type in quota.limits:
            quota.limits[resource_type].current_usage += amount
            
        # Record history
        usage = ResourceUsage(
            usage_id=f"usage_{uuid.uuid4().hex[:8]}",
            quota_id=quota_id,
            resource_type=resource_type,
            amount=amount,
            unit=unit
        )
        self.usage_history.append(usage)
        
        # Keep only last 10000
        if len(self.usage_history) > 10000:
            self.usage_history = self.usage_history[-10000:]
            
    def get_usage(self, quota_id: str, resource_type: ResourceType, hours: int = 24) -> float:
        """Получение использования за период"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return sum(
            u.amount for u in self.usage_history
            if u.quota_id == quota_id
            and u.resource_type == resource_type
            and u.timestamp > cutoff
        )


class QuotaEnforcer:
    """Применитель квот"""
    
    def __init__(self, quota_store: QuotaStore):
        self.quota_store = quota_store
        
    def check_quota(self, quota_id: str, resource_type: ResourceType, requested: float) -> Dict[str, Any]:
        """Проверка квоты"""
        quota = self.quota_store.get(quota_id)
        if not quota:
            return {"allowed": True, "reason": "No quota defined"}
            
        if resource_type not in quota.limits:
            return {"allowed": True, "reason": "Resource not limited"}
            
        limit = quota.limits[resource_type]
        new_usage = limit.current_usage + requested
        
        if new_usage > limit.hard_limit:
            return {
                "allowed": False,
                "reason": f"Would exceed hard limit ({new_usage:.2f} > {limit.hard_limit:.2f})",
                "available": max(0, limit.hard_limit - limit.current_usage)
            }
            
        warning = new_usage > limit.soft_limit
        
        return {
            "allowed": True,
            "warning": warning,
            "available": limit.hard_limit - limit.current_usage,
            "usage_after": new_usage,
            "usage_percent": (new_usage / limit.hard_limit * 100) if limit.hard_limit > 0 else 0
        }
        
    def enforce(self, quota_id: str, resource_type: ResourceType, requested: float) -> bool:
        """Применение квоты"""
        result = self.check_quota(quota_id, resource_type, requested)
        return result.get("allowed", False)


class AlertManager:
    """Менеджер алертов"""
    
    def __init__(self, quota_store: QuotaStore):
        self.quota_store = quota_store
        self.alerts: List[QuotaAlert] = []
        self.alert_thresholds = {
            AlertLevel.WARNING: 80,
            AlertLevel.CRITICAL: 95
        }
        
    def check_alerts(self, quota_id: str) -> List[QuotaAlert]:
        """Проверка алертов"""
        quota = self.quota_store.get(quota_id)
        if not quota:
            return []
            
        new_alerts = []
        
        for resource_type, limit in quota.limits.items():
            usage_pct = limit.usage_percent
            
            if usage_pct >= self.alert_thresholds[AlertLevel.CRITICAL]:
                alert = QuotaAlert(
                    alert_id=f"alert_{uuid.uuid4().hex[:8]}",
                    quota_id=quota_id,
                    level=AlertLevel.CRITICAL,
                    resource_type=resource_type,
                    threshold=self.alert_thresholds[AlertLevel.CRITICAL],
                    current_value=usage_pct,
                    message=f"{resource_type.value} usage at {usage_pct:.1f}% - CRITICAL"
                )
                new_alerts.append(alert)
                quota.status = QuotaStatus.EXCEEDED
                
            elif usage_pct >= self.alert_thresholds[AlertLevel.WARNING]:
                alert = QuotaAlert(
                    alert_id=f"alert_{uuid.uuid4().hex[:8]}",
                    quota_id=quota_id,
                    level=AlertLevel.WARNING,
                    resource_type=resource_type,
                    threshold=self.alert_thresholds[AlertLevel.WARNING],
                    current_value=usage_pct,
                    message=f"{resource_type.value} usage at {usage_pct:.1f}% - WARNING"
                )
                new_alerts.append(alert)
                if quota.status != QuotaStatus.EXCEEDED:
                    quota.status = QuotaStatus.WARNING
                    
        self.alerts.extend(new_alerts)
        return new_alerts


class CostManager:
    """Менеджер затрат"""
    
    def __init__(self, quota_store: QuotaStore):
        self.quota_store = quota_store
        self.cost_per_unit: Dict[ResourceType, float] = {
            ResourceType.CPU: 0.05,  # per core-hour
            ResourceType.MEMORY: 0.01,  # per GB-hour
            ResourceType.STORAGE: 0.001,  # per GB-hour
            ResourceType.GPU: 1.0,  # per GPU-hour
            ResourceType.NETWORK: 0.02,  # per GB
        }
        self.allocations: Dict[str, CostAllocation] = {}
        
    def calculate_cost(self, quota_id: str) -> CostAllocation:
        """Расчёт затрат"""
        quota = self.quota_store.get(quota_id)
        if not quota:
            return None
            
        allocation = CostAllocation(
            allocation_id=f"cost_{uuid.uuid4().hex[:8]}",
            quota_id=quota_id,
            period_end=datetime.now()
        )
        
        for resource_type, limit in quota.limits.items():
            unit_cost = self.cost_per_unit.get(resource_type, 0)
            resource_cost = limit.current_usage * unit_cost
            allocation.costs_by_resource[resource_type.value] = resource_cost
            allocation.total_cost += resource_cost
            
        self.allocations[allocation.allocation_id] = allocation
        return allocation


class QuotaReporter:
    """Генератор отчётов по квотам"""
    
    def __init__(self, quota_store: QuotaStore, cost_manager: CostManager):
        self.quota_store = quota_store
        self.cost_manager = cost_manager
        
    def generate_report(self) -> QuotaReport:
        """Генерация отчёта"""
        quotas = list(self.quota_store.quotas.values())
        
        report = QuotaReport(
            report_id=f"report_{uuid.uuid4().hex[:8]}",
            total_quotas=len(quotas),
            quotas_exceeded=len([q for q in quotas if q.status == QuotaStatus.EXCEEDED]),
            quotas_warning=len([q for q in quotas if q.status == QuotaStatus.WARNING])
        )
        
        # Usage summary
        for resource_type in ResourceType:
            total_limit = 0
            total_usage = 0
            
            for quota in quotas:
                if resource_type in quota.limits:
                    total_limit += quota.limits[resource_type].hard_limit
                    total_usage += quota.limits[resource_type].current_usage
                    
            if total_limit > 0:
                report.usage_summary[resource_type.value] = {
                    "limit": total_limit,
                    "usage": total_usage,
                    "percent": (total_usage / total_limit * 100)
                }
                
        # Cost by scope
        for quota in quotas:
            allocation = self.cost_manager.calculate_cost(quota.quota_id)
            if allocation:
                scope_key = f"{quota.scope.value}:{quota.scope_id}"
                report.cost_by_scope[scope_key] = report.cost_by_scope.get(scope_key, 0) + allocation.total_cost
                report.total_cost += allocation.total_cost
                
        return report


class ResourceQuotaPlatform:
    """Платформа управления квотами ресурсов"""
    
    def __init__(self):
        self.quota_store = QuotaStore()
        self.usage_tracker = UsageTracker(self.quota_store)
        self.enforcer = QuotaEnforcer(self.quota_store)
        self.alert_manager = AlertManager(self.quota_store)
        self.cost_manager = CostManager(self.quota_store)
        self.reporter = QuotaReporter(self.quota_store, self.cost_manager)
        
    def create_quota(
        self,
        name: str,
        scope: QuotaScope,
        scope_id: str,
        limits: Dict[ResourceType, tuple]  # (hard_limit, soft_limit, unit)
    ) -> Quota:
        """Создание квоты"""
        quota = Quota(
            quota_id=f"quota_{uuid.uuid4().hex[:8]}",
            name=name,
            scope=scope,
            scope_id=scope_id
        )
        
        for resource_type, (hard, soft, unit) in limits.items():
            quota.limits[resource_type] = QuotaLimit(
                resource_type=resource_type,
                hard_limit=hard,
                soft_limit=soft,
                unit=unit
            )
            
        self.quota_store.add(quota)
        return quota
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        quotas = list(self.quota_store.quotas.values())
        
        return {
            "total_quotas": len(quotas),
            "by_status": {
                status.value: len([q for q in quotas if q.status == status])
                for status in QuotaStatus
            },
            "by_scope": {
                scope.value: len([q for q in quotas if q.scope == scope])
                for scope in QuotaScope
            },
            "total_alerts": len(self.alert_manager.alerts),
            "active_alerts": len([a for a in self.alert_manager.alerts if not a.acknowledged])
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 178: Resource Quota Platform")
    print("=" * 60)
    
    async def demo():
        platform = ResourceQuotaPlatform()
        print("✓ Resource Quota Platform created")
        
        # Create organization quota (top level)
        print("\n📊 Creating Hierarchical Quotas...")
        
        org_quota = platform.create_quota(
            name="Organization Quota",
            scope=QuotaScope.ORGANIZATION,
            scope_id="org_acme",
            limits={
                ResourceType.CPU: (1000, 800, "cores"),
                ResourceType.MEMORY: (2000, 1600, "GB"),
                ResourceType.STORAGE: (10000, 8000, "GB"),
                ResourceType.GPU: (100, 80, "units"),
            }
        )
        print(f"\n  Organization Quota: {org_quota.name}")
        
        for rt, limit in org_quota.limits.items():
            print(f"    {rt.value}: {limit.hard_limit} {limit.unit} (soft: {limit.soft_limit})")
            
        # Create team quotas
        teams = [
            ("Team Alpha", "team_alpha", {
                ResourceType.CPU: (200, 160, "cores"),
                ResourceType.MEMORY: (400, 320, "GB"),
                ResourceType.STORAGE: (2000, 1600, "GB"),
                ResourceType.PODS: (500, 400, "count"),
            }),
            ("Team Beta", "team_beta", {
                ResourceType.CPU: (150, 120, "cores"),
                ResourceType.MEMORY: (300, 240, "GB"),
                ResourceType.STORAGE: (1500, 1200, "GB"),
                ResourceType.PODS: (300, 240, "count"),
            }),
            ("Team Gamma", "team_gamma", {
                ResourceType.CPU: (100, 80, "cores"),
                ResourceType.MEMORY: (200, 160, "GB"),
                ResourceType.STORAGE: (1000, 800, "GB"),
                ResourceType.PODS: (200, 160, "count"),
            }),
        ]
        
        print("\n  Team Quotas:")
        team_quotas = []
        for name, scope_id, limits in teams:
            quota = platform.create_quota(name, QuotaScope.TEAM, scope_id, limits)
            quota.parent_quota_id = org_quota.quota_id
            team_quotas.append(quota)
            print(f"    • {name} (CPU: {limits[ResourceType.CPU][0]} cores)")
            
        # Create project quotas
        print("\n  Project Quotas:")
        project_quotas = []
        
        projects = [
            ("Production API", "proj_api", team_quotas[0].quota_id),
            ("Data Pipeline", "proj_data", team_quotas[0].quota_id),
            ("ML Training", "proj_ml", team_quotas[1].quota_id),
            ("Analytics", "proj_analytics", team_quotas[2].quota_id),
        ]
        
        for name, scope_id, parent_id in projects:
            quota = platform.create_quota(
                name=name,
                scope=QuotaScope.PROJECT,
                scope_id=scope_id,
                limits={
                    ResourceType.CPU: (50, 40, "cores"),
                    ResourceType.MEMORY: (100, 80, "GB"),
                    ResourceType.STORAGE: (500, 400, "GB"),
                    ResourceType.PODS: (100, 80, "count"),
                }
            )
            quota.parent_quota_id = parent_id
            project_quotas.append(quota)
            print(f"    • {name} (CPU: 50 cores)")
            
        # Simulate resource usage
        print("\n📈 Simulating Resource Usage...")
        
        for quota in project_quotas:
            # Simulate various usage levels
            usage_percent = random.uniform(0.3, 1.1)  # Some may exceed
            
            for resource_type, limit in quota.limits.items():
                usage = limit.hard_limit * usage_percent * random.uniform(0.8, 1.2)
                usage = max(0, usage)
                
                platform.usage_tracker.record_usage(
                    quota.quota_id,
                    resource_type,
                    usage,
                    limit.unit
                )
                
            print(f"  • {quota.name}: ~{usage_percent*100:.0f}% usage")
            
        # Show quota status
        print("\n📋 Quota Status:")
        
        print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
        print("  │ Quota                    │ Scope         │ CPU Usage        │ Memory Usage     │ Status      │")
        print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
        
        for quota in platform.quota_store.quotas.values():
            name = quota.name[:24].ljust(24)
            scope = quota.scope.value[:13].ljust(13)
            
            cpu_limit = quota.limits.get(ResourceType.CPU)
            mem_limit = quota.limits.get(ResourceType.MEMORY)
            
            if cpu_limit:
                cpu_pct = cpu_limit.usage_percent
                cpu = f"{cpu_limit.current_usage:.0f}/{cpu_limit.hard_limit:.0f} ({cpu_pct:.0f}%)".ljust(16)
            else:
                cpu = "N/A".ljust(16)
                
            if mem_limit:
                mem_pct = mem_limit.usage_percent
                mem = f"{mem_limit.current_usage:.0f}/{mem_limit.hard_limit:.0f} ({mem_pct:.0f}%)".ljust(16)
            else:
                mem = "N/A".ljust(16)
                
            status_icons = {
                QuotaStatus.ACTIVE: "🟢",
                QuotaStatus.WARNING: "🟡",
                QuotaStatus.EXCEEDED: "🔴",
                QuotaStatus.DISABLED: "⚪"
            }
            status = f"{status_icons.get(quota.status, '⚪')} {quota.status.value}".ljust(12)
            
            print(f"  │ {name} │ {scope} │ {cpu} │ {mem} │ {status} │")
            
        print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
        
        # Check quota enforcement
        print("\n🔒 Quota Enforcement:")
        
        test_requests = [
            (project_quotas[0].quota_id, ResourceType.CPU, 20),
            (project_quotas[1].quota_id, ResourceType.MEMORY, 50),
            (project_quotas[2].quota_id, ResourceType.CPU, 100),  # Should fail
        ]
        
        for quota_id, resource_type, amount in test_requests:
            quota = platform.quota_store.get(quota_id)
            result = platform.enforcer.check_quota(quota_id, resource_type, amount)
            
            status = "✓ Allowed" if result["allowed"] else "✗ Denied"
            print(f"\n  Request: {amount} {resource_type.value} for {quota.name}")
            print(f"    Result: {status}")
            if "available" in result:
                print(f"    Available: {result['available']:.2f}")
            if result.get("warning"):
                print(f"    ⚠ Warning: Would exceed soft limit")
            if "reason" in result and not result["allowed"]:
                print(f"    Reason: {result['reason']}")
                
        # Check alerts
        print("\n🔔 Checking Alerts...")
        
        all_alerts = []
        for quota in platform.quota_store.quotas.values():
            alerts = platform.alert_manager.check_alerts(quota.quota_id)
            all_alerts.extend(alerts)
            
        if all_alerts:
            print("\n  Active Alerts:")
            for alert in all_alerts[:10]:
                quota = platform.quota_store.get(alert.quota_id)
                icon = "🔴" if alert.level == AlertLevel.CRITICAL else "🟡"
                print(f"    {icon} {quota.name}: {alert.message}")
        else:
            print("  No alerts triggered")
            
        # Cost analysis
        print("\n💰 Cost Analysis:")
        
        print("\n  ┌──────────────────────────────────────────────────────────────────────────┐")
        print("  │ Quota                    │ CPU ($)  │ Memory ($)│ Storage ($)│ Total ($) │")
        print("  ├──────────────────────────────────────────────────────────────────────────┤")
        
        total_cost = 0
        for quota in project_quotas:
            allocation = platform.cost_manager.calculate_cost(quota.quota_id)
            if allocation:
                name = quota.name[:24].ljust(24)
                cpu_cost = f"${allocation.costs_by_resource.get('cpu', 0):.2f}".rjust(8)
                mem_cost = f"${allocation.costs_by_resource.get('memory', 0):.2f}".rjust(9)
                stor_cost = f"${allocation.costs_by_resource.get('storage', 0):.2f}".rjust(10)
                total = f"${allocation.total_cost:.2f}".rjust(9)
                total_cost += allocation.total_cost
                print(f"  │ {name} │ {cpu_cost} │ {mem_cost} │ {stor_cost} │ {total} │")
                
        print("  ├──────────────────────────────────────────────────────────────────────────┤")
        print(f"  │ {'Total'.ljust(24)} │          │           │            │ ${total_cost:>7.2f} │")
        print("  └──────────────────────────────────────────────────────────────────────────┘")
        
        # Generate report
        print("\n📄 Quota Report:")
        
        report = platform.reporter.generate_report()
        
        print(f"\n  Report ID: {report.report_id}")
        print(f"  Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M')}")
        
        print(f"\n  Summary:")
        print(f"    Total Quotas: {report.total_quotas}")
        print(f"    Exceeded: {report.quotas_exceeded}")
        print(f"    Warning: {report.quotas_warning}")
        print(f"    Total Cost: ${report.total_cost:.2f}")
        
        print("\n  Resource Usage Summary:")
        for resource, data in list(report.usage_summary.items())[:5]:
            bar_len = int(data['percent'] / 5)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            print(f"    {resource.ljust(12)}: {bar} {data['percent']:.1f}%")
            
        # Platform statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Quotas: {stats['total_quotas']}")
        print(f"  Total Alerts: {stats['total_alerts']}")
        print(f"  Active Alerts: {stats['active_alerts']}")
        
        print("\n  By Status:")
        for status, count in stats['by_status'].items():
            if count > 0:
                print(f"    • {status}: {count}")
                
        print("\n  By Scope:")
        for scope, count in stats['by_scope'].items():
            if count > 0:
                print(f"    • {scope}: {count}")
                
        # Dashboard
        print("\n┌────────────────────────────────────────────────────────────────────┐")
        print("│                   Resource Quota Dashboard                         │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Total Quotas:                {stats['total_quotas']:>10}                       │")
        print(f"│ Total Alerts:                {stats['total_alerts']:>10}                       │")
        print(f"│ Active Alerts:               {stats['active_alerts']:>10}                       │")
        print("├────────────────────────────────────────────────────────────────────┤")
        active = stats['by_status'].get('active', 0)
        warning = stats['by_status'].get('warning', 0)
        exceeded = stats['by_status'].get('exceeded', 0)
        print(f"│ 🟢 Active:                   {active:>10}                       │")
        print(f"│ 🟡 Warning:                  {warning:>10}                       │")
        print(f"│ 🔴 Exceeded:                 {exceeded:>10}                       │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Monthly Cost:                ${total_cost:>9.2f}                       │")
        print("└────────────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Resource Quota Platform initialized!")
    print("=" * 60)
