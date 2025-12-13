#!/usr/bin/env python3
"""
Server Init - Iteration 76: Resource Quota & Limits Management
Управление квотами и лимитами ресурсов

Функционал:
- Quota Definition - определение квот
- Limit Enforcement - применение лимитов
- Usage Tracking - отслеживание использования
- Quota Alerts - алерты по квотам
- Quota Inheritance - наследование квот
- Burst Handling - обработка пиков
- Quota Reports - отчёты по квотам
- Dynamic Adjustment - динамическая корректировка
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
from collections import defaultdict
import uuid
import time


class ResourceCategory(Enum):
    """Категория ресурса"""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    API = "api"
    DATABASE = "database"
    CUSTOM = "custom"


class QuotaScope(Enum):
    """Область применения квоты"""
    GLOBAL = "global"
    ORGANIZATION = "organization"
    PROJECT = "project"
    USER = "user"
    SERVICE = "service"


class EnforcementAction(Enum):
    """Действие при превышении"""
    BLOCK = "block"
    THROTTLE = "throttle"
    WARN = "warn"
    LOG = "log"
    QUEUE = "queue"


class QuotaPeriod(Enum):
    """Период квоты"""
    PER_SECOND = "per_second"
    PER_MINUTE = "per_minute"
    PER_HOUR = "per_hour"
    PER_DAY = "per_day"
    PER_MONTH = "per_month"
    ABSOLUTE = "absolute"  # Без периода


@dataclass
class ResourceQuota:
    """Квота на ресурс"""
    quota_id: str
    name: str
    
    # Ресурс
    resource_type: str = ""
    category: ResourceCategory = ResourceCategory.CUSTOM
    
    # Лимиты
    limit: float = 0.0
    soft_limit: float = 0.0  # Мягкий лимит для предупреждений
    burst_limit: float = 0.0  # Пиковый лимит
    
    # Период
    period: QuotaPeriod = QuotaPeriod.ABSOLUTE
    
    # Действие
    enforcement: EnforcementAction = EnforcementAction.BLOCK
    
    # Единица измерения
    unit: str = ""
    
    # Метаданные
    description: str = ""


@dataclass
class QuotaPolicy:
    """Политика квот"""
    policy_id: str
    name: str
    
    # Область
    scope: QuotaScope = QuotaScope.PROJECT
    scope_id: str = ""  # ID организации/проекта/пользователя
    
    # Квоты
    quotas: Dict[str, ResourceQuota] = field(default_factory=dict)
    
    # Наследование
    parent_policy_id: str = ""
    
    # Статус
    enabled: bool = True
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    
    # Приоритет
    priority: int = 0


@dataclass
class UsageRecord:
    """Запись использования"""
    record_id: str
    
    # Контекст
    scope: QuotaScope = QuotaScope.PROJECT
    scope_id: str = ""
    resource_type: str = ""
    
    # Использование
    amount: float = 0.0
    
    # Время
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Метаданные
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QuotaUsage:
    """Использование квоты"""
    quota_id: str
    scope_id: str
    
    # Текущее использование
    current: float = 0.0
    
    # Лимит
    limit: float = 0.0
    soft_limit: float = 0.0
    
    # Статус
    available: float = 0.0
    usage_percent: float = 0.0
    
    # Период
    period_start: datetime = field(default_factory=datetime.now)
    period_end: Optional[datetime] = None
    
    # История
    peak_usage: float = 0.0
    peak_time: Optional[datetime] = None


@dataclass
class QuotaAlert:
    """Алерт по квоте"""
    alert_id: str
    
    # Квота
    quota_id: str = ""
    scope_id: str = ""
    
    # Порог
    threshold_percent: float = 80.0
    
    # Статус
    triggered: bool = False
    triggered_at: Optional[datetime] = None
    
    # Уведомления
    notification_channels: List[str] = field(default_factory=list)
    
    # Cooldown
    cooldown_minutes: int = 60
    last_notified: Optional[datetime] = None


@dataclass
class QuotaRequest:
    """Запрос на использование ресурса"""
    request_id: str
    
    # Контекст
    scope: QuotaScope = QuotaScope.PROJECT
    scope_id: str = ""
    
    # Ресурс
    resource_type: str = ""
    amount: float = 1.0
    
    # Время
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class QuotaDecision:
    """Решение по квоте"""
    request_id: str
    
    # Результат
    allowed: bool = True
    
    # Причина
    reason: str = ""
    
    # Квота
    quota_id: str = ""
    current_usage: float = 0.0
    limit: float = 0.0
    
    # Рекомендации
    retry_after_seconds: int = 0
    suggested_amount: float = 0.0


class UsageTracker:
    """Трекер использования"""
    
    def __init__(self):
        self.records: List[UsageRecord] = []
        self.current_usage: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        # current_usage[scope_id][resource_type] = amount
        
        self.window_usage: Dict[str, Dict[str, Dict[str, List[tuple]]]] = defaultdict(
            lambda: defaultdict(lambda: defaultdict(list))
        )
        # window_usage[scope_id][resource_type][period] = [(timestamp, amount), ...]
        
    def record(self, scope_id: str, resource_type: str, amount: float):
        """Запись использования"""
        record = UsageRecord(
            record_id=f"usage_{uuid.uuid4().hex[:8]}",
            scope_id=scope_id,
            resource_type=resource_type,
            amount=amount
        )
        
        self.records.append(record)
        self.current_usage[scope_id][resource_type] += amount
        
        # Записываем в окна
        now = datetime.now()
        for period in [QuotaPeriod.PER_SECOND, QuotaPeriod.PER_MINUTE, 
                       QuotaPeriod.PER_HOUR, QuotaPeriod.PER_DAY]:
            self.window_usage[scope_id][resource_type][period.value].append(
                (now, amount)
            )
            
        # Очистка старых записей
        self._cleanup_windows(scope_id, resource_type)
        
    def _cleanup_windows(self, scope_id: str, resource_type: str):
        """Очистка устаревших записей в окнах"""
        now = datetime.now()
        
        cutoffs = {
            QuotaPeriod.PER_SECOND.value: now - timedelta(seconds=2),
            QuotaPeriod.PER_MINUTE.value: now - timedelta(minutes=2),
            QuotaPeriod.PER_HOUR.value: now - timedelta(hours=2),
            QuotaPeriod.PER_DAY.value: now - timedelta(days=2)
        }
        
        for period, cutoff in cutoffs.items():
            records = self.window_usage[scope_id][resource_type][period]
            self.window_usage[scope_id][resource_type][period] = [
                (ts, amt) for ts, amt in records if ts > cutoff
            ]
            
    def get_usage(self, scope_id: str, resource_type: str,
                   period: QuotaPeriod = QuotaPeriod.ABSOLUTE) -> float:
        """Получение использования"""
        if period == QuotaPeriod.ABSOLUTE:
            return self.current_usage[scope_id][resource_type]
            
        now = datetime.now()
        
        if period == QuotaPeriod.PER_SECOND:
            cutoff = now - timedelta(seconds=1)
        elif period == QuotaPeriod.PER_MINUTE:
            cutoff = now - timedelta(minutes=1)
        elif period == QuotaPeriod.PER_HOUR:
            cutoff = now - timedelta(hours=1)
        elif period == QuotaPeriod.PER_DAY:
            cutoff = now - timedelta(days=1)
        else:
            cutoff = now - timedelta(days=30)
            
        records = self.window_usage[scope_id][resource_type][period.value]
        return sum(amt for ts, amt in records if ts > cutoff)
        
    def release(self, scope_id: str, resource_type: str, amount: float):
        """Освобождение ресурса"""
        self.current_usage[scope_id][resource_type] = max(
            0, self.current_usage[scope_id][resource_type] - amount
        )


class QuotaEnforcer:
    """Применение квот"""
    
    def __init__(self, tracker: UsageTracker):
        self.tracker = tracker
        self.policies: Dict[str, QuotaPolicy] = {}
        self.alerts: Dict[str, QuotaAlert] = {}
        
        self.burst_tokens: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.last_burst_refill: Dict[str, datetime] = {}
        
    def add_policy(self, policy: QuotaPolicy):
        """Добавление политики"""
        self.policies[policy.policy_id] = policy
        
    def check(self, request: QuotaRequest) -> QuotaDecision:
        """Проверка квоты"""
        decision = QuotaDecision(request_id=request.request_id)
        
        # Находим применимые политики
        applicable_policies = self._get_applicable_policies(request.scope, request.scope_id)
        
        for policy in applicable_policies:
            quota = policy.quotas.get(request.resource_type)
            if not quota:
                continue
                
            # Получаем текущее использование
            current = self.tracker.get_usage(
                request.scope_id,
                request.resource_type,
                quota.period
            )
            
            # Проверяем burst
            burst_available = self._get_burst_tokens(
                request.scope_id, request.resource_type, quota
            )
            
            effective_limit = quota.limit + burst_available
            
            if current + request.amount > effective_limit:
                decision.allowed = False
                decision.reason = f"Quota exceeded for {request.resource_type}"
                decision.quota_id = quota.quota_id
                decision.current_usage = current
                decision.limit = quota.limit
                decision.suggested_amount = max(0, effective_limit - current)
                
                if quota.enforcement == EnforcementAction.THROTTLE:
                    decision.retry_after_seconds = self._calculate_retry(quota.period)
                    
                return decision
                
            # Проверяем soft limit для алертов
            if quota.soft_limit > 0 and current + request.amount > quota.soft_limit:
                self._trigger_alert(quota, request.scope_id, current)
                
        decision.allowed = True
        return decision
        
    def _get_applicable_policies(self, scope: QuotaScope,
                                   scope_id: str) -> List[QuotaPolicy]:
        """Получение применимых политик"""
        policies = []
        
        for policy in self.policies.values():
            if not policy.enabled:
                continue
                
            if policy.scope == scope and policy.scope_id == scope_id:
                policies.append(policy)
            elif policy.scope == QuotaScope.GLOBAL:
                policies.append(policy)
                
        # Сортируем по приоритету
        policies.sort(key=lambda p: -p.priority)
        return policies
        
    def _get_burst_tokens(self, scope_id: str, resource_type: str,
                           quota: ResourceQuota) -> float:
        """Получение burst токенов"""
        if quota.burst_limit <= 0:
            return 0
            
        key = f"{scope_id}:{resource_type}"
        
        # Пополнение токенов
        now = datetime.now()
        last_refill = self.last_burst_refill.get(key, now)
        elapsed = (now - last_refill).total_seconds()
        
        # Пополняем со скоростью 10% burst лимита в секунду
        refill_rate = quota.burst_limit * 0.1
        tokens_to_add = elapsed * refill_rate
        
        current_tokens = self.burst_tokens[scope_id][resource_type]
        new_tokens = min(quota.burst_limit, current_tokens + tokens_to_add)
        
        self.burst_tokens[scope_id][resource_type] = new_tokens
        self.last_burst_refill[key] = now
        
        return new_tokens
        
    def _calculate_retry(self, period: QuotaPeriod) -> int:
        """Расчёт времени до повтора"""
        if period == QuotaPeriod.PER_SECOND:
            return 1
        elif period == QuotaPeriod.PER_MINUTE:
            return 60
        elif period == QuotaPeriod.PER_HOUR:
            return 300
        elif period == QuotaPeriod.PER_DAY:
            return 3600
        return 60
        
    def _trigger_alert(self, quota: ResourceQuota, scope_id: str, current: float):
        """Срабатывание алерта"""
        alert_key = f"{quota.quota_id}:{scope_id}"
        
        if alert_key not in self.alerts:
            self.alerts[alert_key] = QuotaAlert(
                alert_id=f"alert_{uuid.uuid4().hex[:8]}",
                quota_id=quota.quota_id,
                scope_id=scope_id
            )
            
        alert = self.alerts[alert_key]
        
        # Проверяем cooldown
        now = datetime.now()
        if alert.last_notified:
            cooldown_end = alert.last_notified + timedelta(minutes=alert.cooldown_minutes)
            if now < cooldown_end:
                return
                
        alert.triggered = True
        alert.triggered_at = now
        alert.last_notified = now
        
    def consume(self, request: QuotaRequest, decision: QuotaDecision):
        """Потребление ресурса"""
        if decision.allowed:
            self.tracker.record(request.scope_id, request.resource_type, request.amount)
            
            # Уменьшаем burst токены если использовали
            applicable_policies = self._get_applicable_policies(request.scope, request.scope_id)
            for policy in applicable_policies:
                quota = policy.quotas.get(request.resource_type)
                if quota and quota.burst_limit > 0:
                    current = self.burst_tokens[request.scope_id][request.resource_type]
                    self.burst_tokens[request.scope_id][request.resource_type] = max(0, current - request.amount * 0.1)


class QuotaReporter:
    """Отчёты по квотам"""
    
    def __init__(self, tracker: UsageTracker, enforcer: QuotaEnforcer):
        self.tracker = tracker
        self.enforcer = enforcer
        
    def get_usage_report(self, scope_id: str) -> Dict[str, Any]:
        """Отчёт об использовании"""
        usage = {}
        
        for resource_type, amount in self.tracker.current_usage[scope_id].items():
            # Находим квоту
            limit = 0
            soft_limit = 0
            
            for policy in self.enforcer.policies.values():
                if policy.scope_id == scope_id or policy.scope == QuotaScope.GLOBAL:
                    quota = policy.quotas.get(resource_type)
                    if quota:
                        limit = quota.limit
                        soft_limit = quota.soft_limit
                        break
                        
            usage[resource_type] = {
                "current": amount,
                "limit": limit,
                "soft_limit": soft_limit,
                "available": max(0, limit - amount),
                "usage_percent": (amount / limit * 100) if limit > 0 else 0
            }
            
        return {
            "scope_id": scope_id,
            "timestamp": datetime.now().isoformat(),
            "resources": usage
        }
        
    def get_alerts_report(self) -> List[Dict[str, Any]]:
        """Отчёт по алертам"""
        return [
            {
                "alert_id": alert.alert_id,
                "quota_id": alert.quota_id,
                "scope_id": alert.scope_id,
                "triggered": alert.triggered,
                "triggered_at": alert.triggered_at.isoformat() if alert.triggered_at else None
            }
            for alert in self.enforcer.alerts.values()
            if alert.triggered
        ]


class ResourceQuotaPlatform:
    """Платформа управления квотами"""
    
    def __init__(self):
        self.tracker = UsageTracker()
        self.enforcer = QuotaEnforcer(self.tracker)
        self.reporter = QuotaReporter(self.tracker, self.enforcer)
        
    def create_quota(self, name: str, resource_type: str,
                      limit: float, **kwargs) -> ResourceQuota:
        """Создание квоты"""
        quota = ResourceQuota(
            quota_id=f"quota_{uuid.uuid4().hex[:8]}",
            name=name,
            resource_type=resource_type,
            limit=limit,
            **kwargs
        )
        return quota
        
    def create_policy(self, name: str, scope: QuotaScope,
                       scope_id: str, quotas: List[ResourceQuota],
                       **kwargs) -> QuotaPolicy:
        """Создание политики"""
        policy = QuotaPolicy(
            policy_id=f"policy_{uuid.uuid4().hex[:8]}",
            name=name,
            scope=scope,
            scope_id=scope_id,
            quotas={q.resource_type: q for q in quotas},
            **kwargs
        )
        
        self.enforcer.add_policy(policy)
        return policy
        
    def request_resource(self, scope_id: str, resource_type: str,
                          amount: float = 1.0) -> QuotaDecision:
        """Запрос ресурса"""
        request = QuotaRequest(
            request_id=f"req_{uuid.uuid4().hex[:8]}",
            scope_id=scope_id,
            resource_type=resource_type,
            amount=amount
        )
        
        decision = self.enforcer.check(request)
        
        if decision.allowed:
            self.enforcer.consume(request, decision)
            
        return decision
        
    def release_resource(self, scope_id: str, resource_type: str,
                          amount: float = 1.0):
        """Освобождение ресурса"""
        self.tracker.release(scope_id, resource_type, amount)
        
    def get_usage(self, scope_id: str, resource_type: str = None) -> Dict[str, Any]:
        """Получение использования"""
        if resource_type:
            return {
                resource_type: self.tracker.get_usage(scope_id, resource_type)
            }
        return dict(self.tracker.current_usage[scope_id])
        
    def get_usage_report(self, scope_id: str) -> Dict[str, Any]:
        """Отчёт об использовании"""
        return self.reporter.get_usage_report(scope_id)
        
    def get_stats(self) -> Dict[str, Any]:
        """Статистика платформы"""
        total_policies = len(self.enforcer.policies)
        total_quotas = sum(len(p.quotas) for p in self.enforcer.policies.values())
        active_alerts = len([a for a in self.enforcer.alerts.values() if a.triggered])
        
        return {
            "policies": total_policies,
            "quotas": total_quotas,
            "active_alerts": active_alerts,
            "tracked_scopes": len(self.tracker.current_usage),
            "usage_records": len(self.tracker.records)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 76: Resource Quota Management")
    print("=" * 60)
    
    async def demo():
        platform = ResourceQuotaPlatform()
        print("✓ Resource Quota Platform created")
        
        # Создание квот
        print("\n📊 Creating Quotas...")
        
        cpu_quota = platform.create_quota(
            name="CPU Cores",
            resource_type="cpu_cores",
            limit=8,
            soft_limit=6,
            category=ResourceCategory.COMPUTE,
            unit="cores",
            enforcement=EnforcementAction.BLOCK
        )
        print(f"  ✓ {cpu_quota.name}: {cpu_quota.limit} {cpu_quota.unit}")
        
        memory_quota = platform.create_quota(
            name="Memory",
            resource_type="memory_gb",
            limit=32,
            soft_limit=24,
            category=ResourceCategory.COMPUTE,
            unit="GB"
        )
        print(f"  ✓ {memory_quota.name}: {memory_quota.limit} {memory_quota.unit}")
        
        storage_quota = platform.create_quota(
            name="Storage",
            resource_type="storage_gb",
            limit=500,
            soft_limit=400,
            category=ResourceCategory.STORAGE,
            unit="GB"
        )
        print(f"  ✓ {storage_quota.name}: {storage_quota.limit} {storage_quota.unit}")
        
        api_quota = platform.create_quota(
            name="API Requests",
            resource_type="api_requests",
            limit=1000,
            soft_limit=800,
            burst_limit=200,
            period=QuotaPeriod.PER_MINUTE,
            category=ResourceCategory.API,
            unit="req/min",
            enforcement=EnforcementAction.THROTTLE
        )
        print(f"  ✓ {api_quota.name}: {api_quota.limit} {api_quota.unit}")
        
        db_conn_quota = platform.create_quota(
            name="DB Connections",
            resource_type="db_connections",
            limit=100,
            soft_limit=80,
            category=ResourceCategory.DATABASE,
            unit="connections"
        )
        print(f"  ✓ {db_conn_quota.name}: {db_conn_quota.limit} {db_conn_quota.unit}")
        
        # Создание политик
        print("\n📋 Creating Policies...")
        
        # Политика для проекта
        project_policy = platform.create_policy(
            name="Project Alpha Quota",
            scope=QuotaScope.PROJECT,
            scope_id="project-alpha",
            quotas=[cpu_quota, memory_quota, storage_quota, api_quota, db_conn_quota]
        )
        print(f"  ✓ Policy: {project_policy.name}")
        print(f"    Scope: {project_policy.scope.value}")
        print(f"    Quotas: {len(project_policy.quotas)}")
        
        # Глобальная политика
        global_cpu = platform.create_quota("Global CPU", "cpu_cores", 4, soft_limit=3)
        global_policy = platform.create_policy(
            name="Global Limits",
            scope=QuotaScope.GLOBAL,
            scope_id="",
            quotas=[global_cpu],
            priority=-1  # Низкий приоритет
        )
        print(f"  ✓ Policy: {global_policy.name} (Global)")
        
        # Запросы ресурсов
        print("\n🔄 Requesting Resources...")
        
        # CPU requests
        for i in range(3):
            decision = platform.request_resource("project-alpha", "cpu_cores", 2)
            status = "✓" if decision.allowed else "✗"
            print(f"  {status} CPU request (2 cores): {decision.reason or 'Allowed'}")
            
        # Еще один запрос - должен превысить лимит
        decision = platform.request_resource("project-alpha", "cpu_cores", 4)
        status = "✓" if decision.allowed else "✗"
        print(f"  {status} CPU request (4 cores): {decision.reason or 'Allowed'}")
        if not decision.allowed:
            print(f"      Current: {decision.current_usage}, Limit: {decision.limit}")
            print(f"      Available: {decision.suggested_amount} cores")
            
        # Memory requests
        decision = platform.request_resource("project-alpha", "memory_gb", 16)
        status = "✓" if decision.allowed else "✗"
        print(f"  {status} Memory request (16 GB): {decision.reason or 'Allowed'}")
        
        # Storage request
        decision = platform.request_resource("project-alpha", "storage_gb", 100)
        status = "✓" if decision.allowed else "✗"
        print(f"  {status} Storage request (100 GB): {decision.reason or 'Allowed'}")
        
        # API requests (с burst)
        print("\n🚀 Testing API Rate Limiting with Burst...")
        
        for i in range(12):
            decision = platform.request_resource("project-alpha", "api_requests", 100)
            status = "✓" if decision.allowed else "✗"
            if i < 5 or i > 9:
                print(f"  Batch {i+1}: {status} - 100 requests")
            elif i == 5:
                print(f"  ... (batches 6-10)")
                
        # DB connections
        print("\n🔌 DB Connection Pool...")
        
        for i in range(5):
            decision = platform.request_resource("project-alpha", "db_connections", 20)
            status = "✓" if decision.allowed else "✗"
            print(f"  {status} DB connections (+20): {'Allowed' if decision.allowed else decision.reason}")
            
        # Освобождение ресурсов
        print("\n♻️ Releasing Resources...")
        
        platform.release_resource("project-alpha", "cpu_cores", 2)
        print("  Released 2 CPU cores")
        
        platform.release_resource("project-alpha", "db_connections", 40)
        print("  Released 40 DB connections")
        
        # Повторный запрос после освобождения
        decision = platform.request_resource("project-alpha", "cpu_cores", 2)
        status = "✓" if decision.allowed else "✗"
        print(f"  {status} CPU request after release: {decision.reason or 'Allowed'}")
        
        # Отчёт об использовании
        print("\n📊 Usage Report for project-alpha:")
        
        report = platform.get_usage_report("project-alpha")
        
        for resource, usage in report["resources"].items():
            bar_length = 20
            filled = int(usage["usage_percent"] / 100 * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            print(f"\n  {resource}:")
            print(f"    [{bar}] {usage['usage_percent']:.1f}%")
            print(f"    Current: {usage['current']} / {usage['limit']}")
            print(f"    Available: {usage['available']}")
            
        # Алерты
        print("\n🚨 Active Alerts:")
        alerts = platform.reporter.get_alerts_report()
        
        if alerts:
            for alert in alerts:
                print(f"  ⚠️ Quota: {alert['quota_id']}")
                print(f"     Scope: {alert['scope_id']}")
                print(f"     Triggered: {alert['triggered_at']}")
        else:
            print("  No active alerts")
            
        # Статистика
        print("\n📊 Platform Statistics:")
        stats = platform.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Resource Quota Management Platform initialized!")
    print("=" * 60)
