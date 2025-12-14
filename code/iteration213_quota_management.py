#!/usr/bin/env python3
"""
Server Init - Iteration 213: Quota Management Platform
Платформа управления квотами

Функционал:
- Resource Quotas - квоты ресурсов
- Rate Limits - лимиты частоты
- Usage Tracking - отслеживание использования
- Quota Enforcement - применение квот
- Quota Policies - политики квот
- Overage Handling - обработка превышения
- Quota Alerts - алерты по квотам
- Usage Reports - отчёты об использовании
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid


class ResourceType(Enum):
    """Тип ресурса"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    REQUESTS = "requests"
    CONNECTIONS = "connections"


class QuotaScope(Enum):
    """Область квоты"""
    TENANT = "tenant"
    PROJECT = "project"
    USER = "user"
    SERVICE = "service"


class QuotaStatus(Enum):
    """Статус квоты"""
    ACTIVE = "active"
    EXCEEDED = "exceeded"
    WARNING = "warning"
    DISABLED = "disabled"


class ActionOnExceed(Enum):
    """Действие при превышении"""
    BLOCK = "block"
    THROTTLE = "throttle"
    NOTIFY = "notify"
    ALLOW = "allow"


@dataclass
class QuotaLimit:
    """Лимит квоты"""
    resource_type: ResourceType = ResourceType.REQUESTS
    limit: float = 0
    unit: str = ""  # per second, per hour, total
    
    # Burst
    burst_limit: Optional[float] = None
    
    # Soft limit for warnings
    warning_threshold: float = 0.8  # 80%


@dataclass
class QuotaUsage:
    """Использование квоты"""
    usage_id: str
    quota_id: str = ""
    
    # Current usage
    current_value: float = 0
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: Optional[datetime] = None
    
    # Peak
    peak_value: float = 0
    peak_time: Optional[datetime] = None
    
    # History
    samples: List[tuple] = field(default_factory=list)  # (timestamp, value)


@dataclass
class Quota:
    """Квота"""
    quota_id: str
    name: str = ""
    
    # Scope
    scope: QuotaScope = QuotaScope.TENANT
    scope_id: str = ""  # tenant_id, project_id, etc.
    
    # Limits
    limits: List[QuotaLimit] = field(default_factory=list)
    
    # Status
    status: QuotaStatus = QuotaStatus.ACTIVE
    
    # Action on exceed
    action_on_exceed: ActionOnExceed = ActionOnExceed.THROTTLE
    
    # Usage
    usage: Dict[str, QuotaUsage] = field(default_factory=dict)
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


@dataclass
class QuotaRequest:
    """Запрос на ресурсы"""
    request_id: str
    quota_id: str = ""
    
    # Resource
    resource_type: ResourceType = ResourceType.REQUESTS
    requested_amount: float = 1
    
    # Requester
    requester_id: str = ""
    
    # Result
    granted: bool = False
    granted_amount: float = 0
    
    # Time
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Reason (if denied)
    denial_reason: str = ""


@dataclass
class QuotaAlert:
    """Алерт по квоте"""
    alert_id: str
    quota_id: str = ""
    
    # Type
    alert_type: str = "warning"  # warning, exceeded, restored
    
    # Resource
    resource_type: ResourceType = ResourceType.REQUESTS
    
    # Values
    current_usage: float = 0
    limit: float = 0
    usage_percentage: float = 0
    
    # Time
    triggered_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


@dataclass
class QuotaPolicy:
    """Политика квот"""
    policy_id: str
    name: str = ""
    
    # Default limits
    default_limits: List[QuotaLimit] = field(default_factory=list)
    
    # Scope
    applicable_scope: QuotaScope = QuotaScope.TENANT
    
    # Priority
    priority: int = 1
    
    # Active
    active: bool = True


class QuotaEnforcer:
    """Применитель квот"""
    
    def check_quota(self, quota: Quota, resource_type: ResourceType,
                   requested_amount: float) -> QuotaRequest:
        """Проверка квоты"""
        request = QuotaRequest(
            request_id=f"req_{uuid.uuid4().hex[:8]}",
            quota_id=quota.quota_id,
            resource_type=resource_type,
            requested_amount=requested_amount
        )
        
        # Find limit for resource type
        limit = None
        for l in quota.limits:
            if l.resource_type == resource_type:
                limit = l
                break
                
        if not limit:
            # No limit defined, allow
            request.granted = True
            request.granted_amount = requested_amount
            return request
            
        # Get current usage
        usage_key = resource_type.value
        usage = quota.usage.get(usage_key)
        current = usage.current_value if usage else 0
        
        # Check if within limit
        if current + requested_amount <= limit.limit:
            request.granted = True
            request.granted_amount = requested_amount
        elif quota.action_on_exceed == ActionOnExceed.ALLOW:
            request.granted = True
            request.granted_amount = requested_amount
        elif quota.action_on_exceed == ActionOnExceed.THROTTLE:
            # Grant partial
            available = max(0, limit.limit - current)
            request.granted = available > 0
            request.granted_amount = available
            request.denial_reason = "Throttled due to quota limit"
        else:
            request.granted = False
            request.denial_reason = "Quota exceeded"
            
        return request


class UsageTracker:
    """Трекер использования"""
    
    def __init__(self):
        self.usage_records: Dict[str, List[tuple]] = {}  # quota_id -> [(timestamp, resource, amount)]
        
    def record_usage(self, quota: Quota, resource_type: ResourceType, amount: float):
        """Запись использования"""
        usage_key = resource_type.value
        
        if usage_key not in quota.usage:
            quota.usage[usage_key] = QuotaUsage(
                usage_id=f"usage_{uuid.uuid4().hex[:8]}",
                quota_id=quota.quota_id
            )
            
        usage = quota.usage[usage_key]
        usage.current_value += amount
        
        # Update peak
        if usage.current_value > usage.peak_value:
            usage.peak_value = usage.current_value
            usage.peak_time = datetime.now()
            
        # Add sample
        usage.samples.append((datetime.now(), usage.current_value))
        
        # Keep only last 100 samples
        if len(usage.samples) > 100:
            usage.samples = usage.samples[-100:]
            
        # Track in records
        if quota.quota_id not in self.usage_records:
            self.usage_records[quota.quota_id] = []
        self.usage_records[quota.quota_id].append((datetime.now(), resource_type.value, amount))
        
    def get_usage_percentage(self, quota: Quota, resource_type: ResourceType) -> float:
        """Получение процента использования"""
        usage_key = resource_type.value
        usage = quota.usage.get(usage_key)
        
        if not usage:
            return 0
            
        # Find limit
        limit = None
        for l in quota.limits:
            if l.resource_type == resource_type:
                limit = l
                break
                
        if not limit or limit.limit == 0:
            return 0
            
        return (usage.current_value / limit.limit) * 100


class AlertManager:
    """Менеджер алертов"""
    
    def __init__(self):
        self.alerts: Dict[str, QuotaAlert] = {}
        
    def check_and_alert(self, quota: Quota, tracker: UsageTracker) -> List[QuotaAlert]:
        """Проверка и создание алертов"""
        new_alerts = []
        
        for limit in quota.limits:
            usage_pct = tracker.get_usage_percentage(quota, limit.resource_type)
            usage_key = limit.resource_type.value
            usage = quota.usage.get(usage_key)
            current = usage.current_value if usage else 0
            
            if usage_pct >= 100:
                alert = QuotaAlert(
                    alert_id=f"alert_{uuid.uuid4().hex[:8]}",
                    quota_id=quota.quota_id,
                    alert_type="exceeded",
                    resource_type=limit.resource_type,
                    current_usage=current,
                    limit=limit.limit,
                    usage_percentage=usage_pct
                )
                self.alerts[alert.alert_id] = alert
                new_alerts.append(alert)
                quota.status = QuotaStatus.EXCEEDED
                
            elif usage_pct >= limit.warning_threshold * 100:
                alert = QuotaAlert(
                    alert_id=f"alert_{uuid.uuid4().hex[:8]}",
                    quota_id=quota.quota_id,
                    alert_type="warning",
                    resource_type=limit.resource_type,
                    current_usage=current,
                    limit=limit.limit,
                    usage_percentage=usage_pct
                )
                self.alerts[alert.alert_id] = alert
                new_alerts.append(alert)
                if quota.status != QuotaStatus.EXCEEDED:
                    quota.status = QuotaStatus.WARNING
                    
        return new_alerts


class QuotaManagementPlatform:
    """Платформа управления квотами"""
    
    def __init__(self):
        self.quotas: Dict[str, Quota] = {}
        self.policies: Dict[str, QuotaPolicy] = {}
        self.enforcer = QuotaEnforcer()
        self.tracker = UsageTracker()
        self.alert_manager = AlertManager()
        self.requests: List[QuotaRequest] = []
        
    def create_quota(self, name: str, scope: QuotaScope, scope_id: str,
                    limits: List[tuple] = None,
                    action_on_exceed: ActionOnExceed = ActionOnExceed.THROTTLE) -> Quota:
        """Создание квоты"""
        quota_limits = []
        if limits:
            for resource_type, limit_value, unit in limits:
                quota_limits.append(QuotaLimit(
                    resource_type=resource_type,
                    limit=limit_value,
                    unit=unit
                ))
                
        quota = Quota(
            quota_id=f"quota_{uuid.uuid4().hex[:8]}",
            name=name,
            scope=scope,
            scope_id=scope_id,
            limits=quota_limits,
            action_on_exceed=action_on_exceed
        )
        self.quotas[quota.quota_id] = quota
        return quota
        
    def create_policy(self, name: str, scope: QuotaScope,
                     default_limits: List[tuple] = None) -> QuotaPolicy:
        """Создание политики"""
        limits = []
        if default_limits:
            for resource_type, limit_value, unit in default_limits:
                limits.append(QuotaLimit(
                    resource_type=resource_type,
                    limit=limit_value,
                    unit=unit
                ))
                
        policy = QuotaPolicy(
            policy_id=f"policy_{uuid.uuid4().hex[:8]}",
            name=name,
            default_limits=limits,
            applicable_scope=scope
        )
        self.policies[policy.policy_id] = policy
        return policy
        
    async def request_resource(self, quota_id: str, resource_type: ResourceType,
                              amount: float) -> QuotaRequest:
        """Запрос ресурса"""
        quota = self.quotas.get(quota_id)
        if not quota:
            return QuotaRequest(
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                denial_reason="Quota not found"
            )
            
        request = self.enforcer.check_quota(quota, resource_type, amount)
        
        if request.granted:
            self.tracker.record_usage(quota, resource_type, request.granted_amount)
            
        self.requests.append(request)
        
        # Check for alerts
        self.alert_manager.check_and_alert(quota, self.tracker)
        
        return request
        
    def reset_usage(self, quota_id: str, resource_type: Optional[ResourceType] = None):
        """Сброс использования"""
        quota = self.quotas.get(quota_id)
        if not quota:
            return
            
        if resource_type:
            usage_key = resource_type.value
            if usage_key in quota.usage:
                quota.usage[usage_key].current_value = 0
        else:
            for usage in quota.usage.values():
                usage.current_value = 0
                
        quota.status = QuotaStatus.ACTIVE
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_requests = len(self.requests)
        granted = len([r for r in self.requests if r.granted])
        denied = total_requests - granted
        
        return {
            "total_quotas": len(self.quotas),
            "active_quotas": len([q for q in self.quotas.values() if q.status == QuotaStatus.ACTIVE]),
            "exceeded_quotas": len([q for q in self.quotas.values() if q.status == QuotaStatus.EXCEEDED]),
            "total_policies": len(self.policies),
            "total_requests": total_requests,
            "granted_requests": granted,
            "denied_requests": denied,
            "grant_rate": (granted / total_requests * 100) if total_requests > 0 else 0,
            "active_alerts": len([a for a in self.alert_manager.alerts.values() if not a.resolved_at])
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 213: Quota Management Platform")
    print("=" * 60)
    
    platform = QuotaManagementPlatform()
    print("✓ Quota Management Platform created")
    
    # Create policies
    print("\n📋 Creating Quota Policies...")
    
    standard_policy = platform.create_policy(
        "Standard Tier",
        QuotaScope.TENANT,
        [
            (ResourceType.REQUESTS, 10000, "per hour"),
            (ResourceType.STORAGE, 100, "GB"),
            (ResourceType.CPU, 4, "cores"),
            (ResourceType.MEMORY, 8192, "MB"),
        ]
    )
    print(f"  ✓ {standard_policy.name}")
    
    premium_policy = platform.create_policy(
        "Premium Tier",
        QuotaScope.TENANT,
        [
            (ResourceType.REQUESTS, 100000, "per hour"),
            (ResourceType.STORAGE, 1000, "GB"),
            (ResourceType.CPU, 16, "cores"),
            (ResourceType.MEMORY, 32768, "MB"),
        ]
    )
    print(f"  ✓ {premium_policy.name}")
    
    # Create quotas
    print("\n📊 Creating Quotas...")
    
    quotas_config = [
        ("Tenant A - API", QuotaScope.TENANT, "tenant_a", 
         [(ResourceType.REQUESTS, 5000, "per hour"), (ResourceType.CONNECTIONS, 100, "total")],
         ActionOnExceed.THROTTLE),
        ("Tenant B - API", QuotaScope.TENANT, "tenant_b",
         [(ResourceType.REQUESTS, 10000, "per hour"), (ResourceType.CONNECTIONS, 200, "total")],
         ActionOnExceed.THROTTLE),
        ("Project Alpha - Storage", QuotaScope.PROJECT, "project_alpha",
         [(ResourceType.STORAGE, 50, "GB")],
         ActionOnExceed.BLOCK),
        ("Service Gateway - CPU", QuotaScope.SERVICE, "gateway",
         [(ResourceType.CPU, 2, "cores"), (ResourceType.MEMORY, 4096, "MB")],
         ActionOnExceed.NOTIFY),
    ]
    
    quotas = []
    for name, scope, scope_id, limits, action in quotas_config:
        quota = platform.create_quota(name, scope, scope_id, limits, action)
        quotas.append(quota)
        print(f"  ✓ {name} ({scope.value}: {scope_id})")
        
    # Simulate resource requests
    print("\n📨 Processing Resource Requests...")
    
    request_patterns = [
        (quotas[0].quota_id, ResourceType.REQUESTS, 100),  # Normal usage
        (quotas[0].quota_id, ResourceType.REQUESTS, 200),
        (quotas[0].quota_id, ResourceType.REQUESTS, 4000),  # High usage
        (quotas[0].quota_id, ResourceType.REQUESTS, 1000),  # Exceed
        (quotas[1].quota_id, ResourceType.REQUESTS, 500),
        (quotas[1].quota_id, ResourceType.CONNECTIONS, 50),
        (quotas[2].quota_id, ResourceType.STORAGE, 20),
        (quotas[2].quota_id, ResourceType.STORAGE, 35),  # Will exceed
        (quotas[3].quota_id, ResourceType.CPU, 1),
        (quotas[3].quota_id, ResourceType.MEMORY, 2048),
    ]
    
    for quota_id, resource_type, amount in request_patterns:
        request = await platform.request_resource(quota_id, resource_type, amount)
        quota = platform.quotas.get(quota_id)
        quota_name = quota.name[:20] if quota else "Unknown"
        status = "✓" if request.granted else "✗"
        print(f"  {status} {quota_name}: {resource_type.value} +{amount} (granted: {request.granted_amount})")
        
    # Display quota status
    print("\n📊 Quota Status:")
    
    print("\n  ┌────────────────────────────┬────────────┬──────────────┬────────────┐")
    print("  │ Quota                      │ Scope      │ Status       │ Action     │")
    print("  ├────────────────────────────┼────────────┼──────────────┼────────────┤")
    
    for quota in platform.quotas.values():
        name = quota.name[:26].ljust(26)
        scope = quota.scope.value[:10].ljust(10)
        
        status_icons = {
            QuotaStatus.ACTIVE: "🟢",
            QuotaStatus.WARNING: "🟡",
            QuotaStatus.EXCEEDED: "🔴",
            QuotaStatus.DISABLED: "⚪"
        }
        status = f"{status_icons.get(quota.status, '⚪')} {quota.status.value}"[:12].ljust(12)
        action = quota.action_on_exceed.value[:10].ljust(10)
        
        print(f"  │ {name} │ {scope} │ {status} │ {action} │")
        
    print("  └────────────────────────────┴────────────┴──────────────┴────────────┘")
    
    # Usage details
    print("\n📈 Usage Details:")
    
    for quota in platform.quotas.values():
        if quota.usage:
            print(f"\n  {quota.name}:")
            
            for limit in quota.limits:
                usage_key = limit.resource_type.value
                usage = quota.usage.get(usage_key)
                
                if usage:
                    pct = platform.tracker.get_usage_percentage(quota, limit.resource_type)
                    bar_len = min(20, int(pct / 5))
                    bar = "█" * bar_len + "░" * (20 - bar_len)
                    
                    print(f"    {limit.resource_type.value:12s} [{bar}] {usage.current_value:.0f}/{limit.limit:.0f} {limit.unit} ({pct:.0f}%)")
                    
    # Alerts
    print("\n🚨 Active Alerts:")
    
    active_alerts = [a for a in platform.alert_manager.alerts.values() if not a.resolved_at]
    
    if active_alerts:
        for alert in active_alerts:
            quota = platform.quotas.get(alert.quota_id)
            quota_name = quota.name if quota else "Unknown"
            
            icon = "⚠️" if alert.alert_type == "warning" else "🔴"
            print(f"  {icon} [{alert.alert_type.upper()}] {quota_name}")
            print(f"      Resource: {alert.resource_type.value}")
            print(f"      Usage: {alert.current_usage}/{alert.limit} ({alert.usage_percentage:.0f}%)")
    else:
        print("  ✓ No active alerts")
        
    # Request summary
    print("\n📊 Request Summary:")
    
    by_resource = {}
    for request in platform.requests:
        r = request.resource_type.value
        if r not in by_resource:
            by_resource[r] = {"total": 0, "granted": 0}
        by_resource[r]["total"] += 1
        if request.granted:
            by_resource[r]["granted"] += 1
            
    print("\n  ┌────────────────────┬──────────┬──────────┬────────────────┐")
    print("  │ Resource           │ Total    │ Granted  │ Grant Rate     │")
    print("  ├────────────────────┼──────────┼──────────┼────────────────┤")
    
    for resource, data in by_resource.items():
        name = resource[:18].ljust(18)
        total = str(data["total"]).center(8)
        granted = str(data["granted"]).center(8)
        rate = f"{data['granted']/data['total']*100:.0f}%".center(14) if data["total"] > 0 else "N/A".center(14)
        print(f"  │ {name} │ {total} │ {granted} │ {rate} │")
        
    print("  └────────────────────┴──────────┴──────────┴────────────────┘")
    
    # Quota by scope
    print("\n📁 Quotas by Scope:")
    
    by_scope = {}
    for quota in platform.quotas.values():
        s = quota.scope.value
        if s not in by_scope:
            by_scope[s] = []
        by_scope[s].append(quota)
        
    for scope, scope_quotas in by_scope.items():
        print(f"\n  {scope.upper()}:")
        for quota in scope_quotas:
            status_icon = "🟢" if quota.status == QuotaStatus.ACTIVE else "🔴"
            print(f"    {status_icon} {quota.name} ({quota.scope_id})")
            
    # Policy overview
    print("\n📋 Policy Overview:")
    
    for policy in platform.policies.values():
        print(f"\n  {policy.name}:")
        print(f"    Scope: {policy.applicable_scope.value}")
        print(f"    Default Limits:")
        for limit in policy.default_limits:
            print(f"      • {limit.resource_type.value}: {limit.limit} {limit.unit}")
            
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📈 Platform Statistics:")
    
    print(f"\n  Total Quotas: {stats['total_quotas']}")
    print(f"  Active: {stats['active_quotas']}")
    print(f"  Exceeded: {stats['exceeded_quotas']}")
    print(f"  Policies: {stats['total_policies']}")
    print(f"  Total Requests: {stats['total_requests']}")
    print(f"  Granted: {stats['granted_requests']}")
    print(f"  Denied: {stats['denied_requests']}")
    print(f"  Grant Rate: {stats['grant_rate']:.1f}%")
    print(f"  Active Alerts: {stats['active_alerts']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Quota Management Dashboard                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Quotas:                  {stats['total_quotas']:>12}                        │")
    print(f"│ Active Quotas:                 {stats['active_quotas']:>12}                        │")
    print(f"│ Exceeded Quotas:               {stats['exceeded_quotas']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Requests:                {stats['total_requests']:>12}                        │")
    print(f"│ Grant Rate:                      {stats['grant_rate']:>10.1f}%                   │")
    print(f"│ Active Alerts:                 {stats['active_alerts']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Quota Management Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
