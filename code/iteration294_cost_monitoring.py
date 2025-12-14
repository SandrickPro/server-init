#!/usr/bin/env python3
"""
Server Init - Iteration 294: Cost Monitoring Platform
Платформа Cost Monitoring

Функционал:
- Cost Tracking - отслеживание затрат
- Budget Management - управление бюджетами
- Resource Cost Analysis - анализ стоимости ресурсов
- Cost Allocation - распределение затрат
- Billing Integration - интеграция с биллингом
- Cost Forecasting - прогнозирование затрат
- Cost Optimization - оптимизация затрат
- Alert Management - управление алертами
"""

import asyncio
import random
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid


class ResourceType(Enum):
    """Тип ресурса"""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    KUBERNETES = "kubernetes"
    SERVERLESS = "serverless"
    SUPPORT = "support"
    OTHER = "other"


class CostUnit(Enum):
    """Единица затрат"""
    HOUR = "hour"
    DAY = "day"
    MONTH = "month"
    GB = "gb"
    REQUEST = "request"
    UNIT = "unit"


class BudgetPeriod(Enum):
    """Период бюджета"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class AlertType(Enum):
    """Тип алерта"""
    BUDGET_THRESHOLD = "budget_threshold"
    ANOMALY = "anomaly"
    FORECAST = "forecast"
    OPTIMIZATION = "optimization"


class AlertSeverity(Enum):
    """Серьёзность алерта"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class CostEntry:
    """Запись о затратах"""
    entry_id: str
    
    # Resource
    resource_id: str = ""
    resource_name: str = ""
    resource_type: ResourceType = ResourceType.COMPUTE
    
    # Cost
    amount: float = 0.0
    currency: str = "USD"
    
    # Unit
    unit: CostUnit = CostUnit.HOUR
    quantity: float = 0.0
    unit_price: float = 0.0
    
    # Allocation
    project: str = ""
    team: str = ""
    environment: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Period
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None


@dataclass
class Budget:
    """Бюджет"""
    budget_id: str
    name: str
    
    # Amount
    amount: float = 0.0
    currency: str = "USD"
    
    # Period
    period: BudgetPeriod = BudgetPeriod.MONTHLY
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    
    # Scope
    project: str = ""
    team: str = ""
    resource_types: List[ResourceType] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Current spending
    current_spend: float = 0.0
    forecasted_spend: float = 0.0
    
    # Thresholds (%)
    warning_threshold: float = 80.0
    critical_threshold: float = 100.0


@dataclass
class ResourceCost:
    """Стоимость ресурса"""
    resource_id: str
    resource_name: str
    resource_type: ResourceType
    
    # Current cost
    hourly_cost: float = 0.0
    daily_cost: float = 0.0
    monthly_cost: float = 0.0
    
    # History
    cost_history: List[CostEntry] = field(default_factory=list)
    
    # Metadata
    project: str = ""
    team: str = ""
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class CostAllocation:
    """Распределение затрат"""
    allocation_id: str
    
    # Target
    target_type: str = ""  # project, team, environment
    target_name: str = ""
    
    # Costs
    total_cost: float = 0.0
    
    # Breakdown by resource type
    breakdown: Dict[str, float] = field(default_factory=dict)
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: Optional[datetime] = None


@dataclass
class CostForecast:
    """Прогноз затрат"""
    forecast_id: str
    
    # Target
    scope: str = ""  # project, team, or "total"
    
    # Predictions
    current_month: float = 0.0
    next_month: float = 0.0
    next_quarter: float = 0.0
    
    # Trend
    trend_percent: float = 0.0  # Month-over-month change
    
    # Confidence
    confidence: float = 0.0
    
    # Generated
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class OptimizationRecommendation:
    """Рекомендация по оптимизации"""
    rec_id: str
    
    # Resource
    resource_id: str = ""
    resource_name: str = ""
    resource_type: ResourceType = ResourceType.COMPUTE
    
    # Recommendation
    title: str = ""
    description: str = ""
    
    # Savings
    estimated_savings: float = 0.0
    savings_percent: float = 0.0
    
    # Implementation
    difficulty: str = "easy"  # easy, medium, hard
    impact: str = "low"  # low, medium, high
    
    # Status
    implemented: bool = False


@dataclass
class CostAlert:
    """Алерт о затратах"""
    alert_id: str
    
    # Type
    alert_type: AlertType = AlertType.BUDGET_THRESHOLD
    severity: AlertSeverity = AlertSeverity.WARNING
    
    # Target
    budget_id: str = ""
    resource_id: str = ""
    
    # Details
    message: str = ""
    current_value: float = 0.0
    threshold: float = 0.0
    
    # Status
    acknowledged: bool = False
    resolved: bool = False
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)


class CostMonitoringManager:
    """Менеджер Cost Monitoring"""
    
    def __init__(self, default_currency: str = "USD"):
        self.cost_entries: List[CostEntry] = []
        self.budgets: Dict[str, Budget] = {}
        self.resource_costs: Dict[str, ResourceCost] = {}
        self.allocations: Dict[str, CostAllocation] = {}
        self.forecasts: Dict[str, CostForecast] = {}
        self.recommendations: Dict[str, OptimizationRecommendation] = {}
        self.alerts: List[CostAlert] = []
        
        self.default_currency = default_currency
        
        # Pricing (simulated)
        self.pricing = {
            ResourceType.COMPUTE: {"unit": CostUnit.HOUR, "price": 0.05},
            ResourceType.STORAGE: {"unit": CostUnit.GB, "price": 0.023},
            ResourceType.NETWORK: {"unit": CostUnit.GB, "price": 0.01},
            ResourceType.DATABASE: {"unit": CostUnit.HOUR, "price": 0.10},
            ResourceType.KUBERNETES: {"unit": CostUnit.HOUR, "price": 0.08},
            ResourceType.SERVERLESS: {"unit": CostUnit.REQUEST, "price": 0.0000002}
        }
        
    async def record_cost(self, resource_id: str,
                         resource_name: str,
                         resource_type: ResourceType,
                         quantity: float,
                         project: str = "",
                         team: str = "",
                         environment: str = "",
                         tags: Dict[str, str] = None) -> CostEntry:
        """Запись затрат"""
        pricing = self.pricing.get(resource_type, {"unit": CostUnit.UNIT, "price": 0.01})
        
        amount = quantity * pricing["price"]
        
        entry = CostEntry(
            entry_id=f"cost_{uuid.uuid4().hex[:8]}",
            resource_id=resource_id,
            resource_name=resource_name,
            resource_type=resource_type,
            amount=amount,
            unit=pricing["unit"],
            quantity=quantity,
            unit_price=pricing["price"],
            project=project,
            team=team,
            environment=environment,
            tags=tags or {}
        )
        
        self.cost_entries.append(entry)
        
        # Update resource cost
        await self._update_resource_cost(entry)
        
        # Update budget spending
        await self._update_budget_spending(entry)
        
        return entry
        
    async def create_budget(self, name: str,
                           amount: float,
                           period: BudgetPeriod = BudgetPeriod.MONTHLY,
                           project: str = "",
                           team: str = "",
                           resource_types: List[ResourceType] = None,
                           warning_threshold: float = 80.0,
                           critical_threshold: float = 100.0) -> Budget:
        """Создание бюджета"""
        budget = Budget(
            budget_id=f"budget_{uuid.uuid4().hex[:8]}",
            name=name,
            amount=amount,
            period=period,
            project=project,
            team=team,
            resource_types=resource_types or [],
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold
        )
        
        # Set end date based on period
        now = datetime.now()
        if period == BudgetPeriod.DAILY:
            budget.end_date = now + timedelta(days=1)
        elif period == BudgetPeriod.WEEKLY:
            budget.end_date = now + timedelta(weeks=1)
        elif period == BudgetPeriod.MONTHLY:
            budget.end_date = now + timedelta(days=30)
        elif period == BudgetPeriod.QUARTERLY:
            budget.end_date = now + timedelta(days=90)
        elif period == BudgetPeriod.YEARLY:
            budget.end_date = now + timedelta(days=365)
            
        self.budgets[budget.budget_id] = budget
        return budget
        
    async def _update_resource_cost(self, entry: CostEntry):
        """Обновление стоимости ресурса"""
        if entry.resource_id not in self.resource_costs:
            self.resource_costs[entry.resource_id] = ResourceCost(
                resource_id=entry.resource_id,
                resource_name=entry.resource_name,
                resource_type=entry.resource_type,
                project=entry.project,
                team=entry.team,
                tags=entry.tags
            )
            
        resource = self.resource_costs[entry.resource_id]
        resource.cost_history.append(entry)
        
        # Update current costs
        resource.hourly_cost = entry.amount
        resource.daily_cost = entry.amount * 24
        resource.monthly_cost = entry.amount * 24 * 30
        
        # Keep only last 1000 entries
        if len(resource.cost_history) > 1000:
            resource.cost_history = resource.cost_history[-1000:]
            
    async def _update_budget_spending(self, entry: CostEntry):
        """Обновление расходов бюджета"""
        for budget in self.budgets.values():
            # Check scope match
            if budget.project and budget.project != entry.project:
                continue
            if budget.team and budget.team != entry.team:
                continue
            if budget.resource_types and entry.resource_type not in budget.resource_types:
                continue
                
            # Update spending
            budget.current_spend += entry.amount
            
            # Check thresholds
            await self._check_budget_thresholds(budget)
            
    async def _check_budget_thresholds(self, budget: Budget):
        """Проверка порогов бюджета"""
        percent = (budget.current_spend / budget.amount * 100) if budget.amount > 0 else 0
        
        if percent >= budget.critical_threshold:
            await self._create_alert(
                AlertType.BUDGET_THRESHOLD,
                AlertSeverity.CRITICAL,
                budget_id=budget.budget_id,
                message=f"Budget '{budget.name}' exceeded: {percent:.1f}%",
                current_value=budget.current_spend,
                threshold=budget.amount
            )
        elif percent >= budget.warning_threshold:
            await self._create_alert(
                AlertType.BUDGET_THRESHOLD,
                AlertSeverity.WARNING,
                budget_id=budget.budget_id,
                message=f"Budget '{budget.name}' at {percent:.1f}%",
                current_value=budget.current_spend,
                threshold=budget.amount
            )
            
    async def _create_alert(self, alert_type: AlertType,
                           severity: AlertSeverity,
                           budget_id: str = "",
                           resource_id: str = "",
                           message: str = "",
                           current_value: float = 0.0,
                           threshold: float = 0.0):
        """Создание алерта"""
        # Check duplicate
        for alert in self.alerts:
            if (alert.budget_id == budget_id and
                alert.alert_type == alert_type and
                not alert.resolved):
                return
                
        alert = CostAlert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            alert_type=alert_type,
            severity=severity,
            budget_id=budget_id,
            resource_id=resource_id,
            message=message,
            current_value=current_value,
            threshold=threshold
        )
        
        self.alerts.append(alert)
        
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
            
    async def allocate_costs(self, target_type: str,
                            target_name: str,
                            period_days: int = 30) -> CostAllocation:
        """Распределение затрат"""
        period_start = datetime.now() - timedelta(days=period_days)
        
        total = 0.0
        breakdown = {}
        
        for entry in self.cost_entries:
            if entry.start_time < period_start:
                continue
                
            # Match target
            if target_type == "project" and entry.project != target_name:
                continue
            if target_type == "team" and entry.team != target_name:
                continue
            if target_type == "environment" and entry.environment != target_name:
                continue
                
            total += entry.amount
            
            rtype = entry.resource_type.value
            if rtype not in breakdown:
                breakdown[rtype] = 0
            breakdown[rtype] += entry.amount
            
        allocation = CostAllocation(
            allocation_id=f"alloc_{uuid.uuid4().hex[:8]}",
            target_type=target_type,
            target_name=target_name,
            total_cost=total,
            breakdown=breakdown,
            period_start=period_start
        )
        
        self.allocations[allocation.allocation_id] = allocation
        return allocation
        
    async def generate_forecast(self, scope: str = "total") -> CostForecast:
        """Генерация прогноза"""
        # Calculate current monthly spend
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        current_spend = 0.0
        for entry in self.cost_entries:
            if entry.start_time >= thirty_days_ago:
                if scope == "total" or entry.project == scope or entry.team == scope:
                    current_spend += entry.amount
                    
        # Project forward
        days_elapsed = min(30, (datetime.now() - thirty_days_ago).days)
        daily_rate = current_spend / max(days_elapsed, 1)
        
        forecast = CostForecast(
            forecast_id=f"forecast_{uuid.uuid4().hex[:8]}",
            scope=scope,
            current_month=current_spend + (daily_rate * (30 - days_elapsed)),
            next_month=daily_rate * 30 * 1.05,  # Assume 5% growth
            next_quarter=daily_rate * 90 * 1.1,  # Assume 10% growth
            trend_percent=random.uniform(-5, 15),
            confidence=random.uniform(70, 95)
        )
        
        self.forecasts[forecast.forecast_id] = forecast
        return forecast
        
    async def generate_recommendations(self) -> List[OptimizationRecommendation]:
        """Генерация рекомендаций"""
        recommendations = []
        
        # Analyze resource costs
        for resource in self.resource_costs.values():
            if resource.monthly_cost > 100:
                # Simulate recommendations
                rec_types = [
                    ("Downsize instance", "Consider downsizing to smaller instance type", 20, "easy"),
                    ("Use reserved capacity", "Switch to reserved pricing", 30, "medium"),
                    ("Enable auto-scaling", "Implement auto-scaling to match demand", 25, "medium"),
                    ("Remove unused resources", "Resource appears underutilized", 100, "easy"),
                    ("Use spot instances", "Consider using spot/preemptible instances", 40, "hard")
                ]
                
                rec_type = random.choice(rec_types)
                savings = resource.monthly_cost * rec_type[2] / 100
                
                rec = OptimizationRecommendation(
                    rec_id=f"rec_{uuid.uuid4().hex[:8]}",
                    resource_id=resource.resource_id,
                    resource_name=resource.resource_name,
                    resource_type=resource.resource_type,
                    title=rec_type[0],
                    description=rec_type[1],
                    estimated_savings=savings,
                    savings_percent=rec_type[2],
                    difficulty=rec_type[3]
                )
                
                self.recommendations[rec.rec_id] = rec
                recommendations.append(rec)
                
        return recommendations
        
    def get_total_cost(self, period_days: int = 30) -> float:
        """Общие затраты за период"""
        cutoff = datetime.now() - timedelta(days=period_days)
        return sum(e.amount for e in self.cost_entries if e.start_time >= cutoff)
        
    def get_cost_by_type(self, period_days: int = 30) -> Dict[str, float]:
        """Затраты по типам ресурсов"""
        cutoff = datetime.now() - timedelta(days=period_days)
        breakdown = {}
        
        for entry in self.cost_entries:
            if entry.start_time >= cutoff:
                rtype = entry.resource_type.value
                if rtype not in breakdown:
                    breakdown[rtype] = 0
                breakdown[rtype] += entry.amount
                
        return breakdown
        
    def get_active_alerts(self) -> List[CostAlert]:
        """Активные алерты"""
        return [a for a in self.alerts if not a.resolved]
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_30d = self.get_total_cost(30)
        total_7d = self.get_total_cost(7)
        
        potential_savings = sum(r.estimated_savings for r in self.recommendations.values()
                               if not r.implemented)
        
        over_budget = sum(1 for b in self.budgets.values()
                        if b.current_spend > b.amount)
                        
        return {
            "total_cost_30d": total_30d,
            "total_cost_7d": total_7d,
            "daily_average": total_30d / 30,
            "budgets": len(self.budgets),
            "over_budget": over_budget,
            "resources_tracked": len(self.resource_costs),
            "potential_savings": potential_savings,
            "active_alerts": len(self.get_active_alerts()),
            "recommendations": len(self.recommendations)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 294: Cost Monitoring Platform")
    print("=" * 60)
    
    manager = CostMonitoringManager()
    print("✓ Cost Monitoring Manager created")
    
    # Record costs
    print("\n💰 Recording Costs...")
    
    costs_data = [
        # Compute
        ("vm-web-01", "Web Server 1", ResourceType.COMPUTE, 720, "web-app", "platform"),
        ("vm-web-02", "Web Server 2", ResourceType.COMPUTE, 720, "web-app", "platform"),
        ("vm-api-01", "API Server 1", ResourceType.COMPUTE, 720, "api", "backend"),
        ("vm-api-02", "API Server 2", ResourceType.COMPUTE, 720, "api", "backend"),
        # Database
        ("db-postgres-01", "PostgreSQL Primary", ResourceType.DATABASE, 720, "api", "backend"),
        ("db-postgres-02", "PostgreSQL Replica", ResourceType.DATABASE, 720, "api", "backend"),
        ("db-redis-01", "Redis Cache", ResourceType.DATABASE, 720, "api", "backend"),
        # Storage
        ("storage-01", "Object Storage", ResourceType.STORAGE, 5000, "web-app", "platform"),
        ("storage-02", "Backup Storage", ResourceType.STORAGE, 10000, "infra", "platform"),
        # Network
        ("network-egress", "Network Egress", ResourceType.NETWORK, 2000, "web-app", "platform"),
        # Kubernetes
        ("k8s-cluster-01", "K8s Cluster", ResourceType.KUBERNETES, 720, "microservices", "platform"),
        # Serverless
        ("lambda-auth", "Auth Function", ResourceType.SERVERLESS, 10000000, "api", "backend")
    ]
    
    for res_id, res_name, res_type, qty, project, team in costs_data:
        entry = await manager.record_cost(
            res_id, res_name, res_type, qty,
            project=project, team=team, environment="production"
        )
        print(f"  💰 {res_name}: ${entry.amount:.2f}")
        
    # Create budgets
    print("\n📊 Creating Budgets...")
    
    budgets_data = [
        ("Platform Team Monthly", 500, BudgetPeriod.MONTHLY, "", "platform"),
        ("Backend Team Monthly", 300, BudgetPeriod.MONTHLY, "", "backend"),
        ("Web App Project", 200, BudgetPeriod.MONTHLY, "web-app", ""),
        ("API Project", 250, BudgetPeriod.MONTHLY, "api", ""),
        ("Compute Resources", 400, BudgetPeriod.MONTHLY, "", "", [ResourceType.COMPUTE])
    ]
    
    for name, amount, period, project, team, *rest in budgets_data:
        res_types = rest[0] if rest else []
        budget = await manager.create_budget(
            name, amount, period, project, team, res_types
        )
        percent = budget.current_spend / budget.amount * 100 if budget.amount > 0 else 0
        status = "⚠️" if percent > 80 else "✅"
        print(f"  {status} {name}: ${budget.current_spend:.2f}/${budget.amount:.2f} ({percent:.1f}%)")
        
    # Cost allocation
    print("\n📈 Cost Allocation...")
    
    for target_type, target_name in [("team", "platform"), ("team", "backend"), ("project", "api")]:
        allocation = await manager.allocate_costs(target_type, target_name)
        print(f"\n  📊 {target_type.capitalize()}: {target_name}")
        print(f"     Total: ${allocation.total_cost:.2f}")
        
        for rtype, cost in sorted(allocation.breakdown.items(), key=lambda x: -x[1])[:3]:
            print(f"       {rtype}: ${cost:.2f}")
            
    # Generate forecasts
    print("\n🔮 Cost Forecasts...")
    
    for scope in ["total", "api", "web-app"]:
        forecast = await manager.generate_forecast(scope)
        trend_icon = "📈" if forecast.trend_percent > 0 else "📉"
        print(f"\n  🔮 {scope.upper()}:")
        print(f"     Current Month: ${forecast.current_month:.2f}")
        print(f"     Next Month: ${forecast.next_month:.2f}")
        print(f"     Trend: {trend_icon} {forecast.trend_percent:+.1f}%")
        print(f"     Confidence: {forecast.confidence:.0f}%")
        
    # Generate recommendations
    print("\n💡 Optimization Recommendations...")
    
    recommendations = await manager.generate_recommendations()
    
    total_savings = sum(r.estimated_savings for r in recommendations)
    print(f"\n  Total Potential Savings: ${total_savings:.2f}")
    
    for rec in sorted(recommendations, key=lambda x: -x.estimated_savings)[:5]:
        print(f"\n  💡 {rec.title}")
        print(f"     Resource: {rec.resource_name}")
        print(f"     Savings: ${rec.estimated_savings:.2f}/month ({rec.savings_percent:.0f}%)")
        print(f"     Difficulty: {rec.difficulty}")
        
    # Budget status
    print("\n📊 Budget Status:")
    
    print("\n  ┌────────────────────────────┬────────────────┬────────────────┬────────────┬─────────────┐")
    print("  │ Budget                     │ Spent          │ Total          │ Used       │ Status      │")
    print("  ├────────────────────────────┼────────────────┼────────────────┼────────────┼─────────────┤")
    
    for budget in manager.budgets.values():
        name = budget.name[:26].ljust(26)
        spent = f"${budget.current_spend:.2f}".ljust(14)
        total = f"${budget.amount:.2f}".ljust(14)
        percent = budget.current_spend / budget.amount * 100 if budget.amount > 0 else 0
        used = f"{percent:.1f}%".ljust(10)
        
        if percent >= 100:
            status = "🔴 Over"
        elif percent >= 80:
            status = "🟡 Warning"
        else:
            status = "🟢 OK"
        status = status.ljust(11)
        
        print(f"  │ {name} │ {spent} │ {total} │ {used} │ {status} │")
        
    print("  └────────────────────────────┴────────────────┴────────────────┴────────────┴─────────────┘")
    
    # Cost by resource type
    print("\n📊 Cost by Resource Type:")
    
    cost_by_type = manager.get_cost_by_type()
    total_cost = sum(cost_by_type.values())
    
    for rtype, cost in sorted(cost_by_type.items(), key=lambda x: -x[1]):
        percent = cost / total_cost * 100 if total_cost > 0 else 0
        bar_len = 30
        filled = int(percent / 100 * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"  {rtype:15} [{bar}] ${cost:>8.2f} ({percent:>5.1f}%)")
        
    # Top cost resources
    print("\n💰 Top Cost Resources:")
    
    sorted_resources = sorted(
        manager.resource_costs.values(),
        key=lambda x: x.monthly_cost,
        reverse=True
    )[:5]
    
    print("\n  ┌────────────────────────────┬────────────────┬────────────────┬────────────────────┐")
    print("  │ Resource                   │ Hourly         │ Monthly        │ Type               │")
    print("  ├────────────────────────────┼────────────────┼────────────────┼────────────────────┤")
    
    for resource in sorted_resources:
        name = resource.resource_name[:26].ljust(26)
        hourly = f"${resource.hourly_cost:.4f}".ljust(14)
        monthly = f"${resource.monthly_cost:.2f}".ljust(14)
        rtype = resource.resource_type.value[:18].ljust(18)
        
        print(f"  │ {name} │ {hourly} │ {monthly} │ {rtype} │")
        
    print("  └────────────────────────────┴────────────────┴────────────────┴────────────────────┘")
    
    # Alerts
    print("\n🚨 Cost Alerts:")
    
    alerts = manager.get_active_alerts()
    
    if alerts:
        for alert in alerts[:5]:
            severity_icons = {
                AlertSeverity.INFO: "ℹ️",
                AlertSeverity.WARNING: "⚠️",
                AlertSeverity.ERROR: "❌",
                AlertSeverity.CRITICAL: "🔴"
            }
            icon = severity_icons.get(alert.severity, "❓")
            print(f"  {icon} [{alert.severity.value}] {alert.message}")
    else:
        print("  ✅ No active alerts")
        
    # Statistics
    print("\n📊 Cost Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Cost (30 days): ${stats['total_cost_30d']:.2f}")
    print(f"  Cost (7 days): ${stats['total_cost_7d']:.2f}")
    print(f"  Daily Average: ${stats['daily_average']:.2f}")
    print(f"\n  Budgets: {stats['budgets']}")
    print(f"  Over Budget: {stats['over_budget']}")
    print(f"  Resources Tracked: {stats['resources_tracked']}")
    print(f"\n  Potential Savings: ${stats['potential_savings']:.2f}")
    print(f"  Recommendations: {stats['recommendations']}")
    print(f"  Active Alerts: {stats['active_alerts']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Cost Monitoring Dashboard                         │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Monthly Cost (30d):            ${stats['total_cost_30d']:>11.2f}                       │")
    print(f"│ Weekly Cost (7d):              ${stats['total_cost_7d']:>11.2f}                       │")
    print(f"│ Daily Average:                 ${stats['daily_average']:>11.2f}                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Potential Savings:             ${stats['potential_savings']:>11.2f}                       │")
    print(f"│ Budgets Over Limit:            {stats['over_budget']:>12}                        │")
    print(f"│ Active Alerts:                 {stats['active_alerts']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Cost Monitoring Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
