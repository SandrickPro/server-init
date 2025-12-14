#!/usr/bin/env python3
"""
Server Init - Iteration 189: Cost Optimization Platform
Платформа оптимизации затрат

Функционал:
- Cost Analysis - анализ затрат
- Resource Rightsizing - оптимизация размеров ресурсов
- Idle Resource Detection - обнаружение простаивающих ресурсов
- Reserved Instance Planning - планирование резервов
- Spot Instance Management - управление spot инстансами
- Cost Allocation - распределение затрат
- Budget Management - управление бюджетами
- Savings Recommendations - рекомендации по экономии
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
    COMPUTE = "compute"
    STORAGE = "storage"
    DATABASE = "database"
    NETWORK = "network"
    CONTAINER = "container"
    SERVERLESS = "serverless"
    CACHE = "cache"


class PricingModel(Enum):
    """Модель ценообразования"""
    ON_DEMAND = "on_demand"
    RESERVED = "reserved"
    SPOT = "spot"
    SAVINGS_PLAN = "savings_plan"


class CostCategory(Enum):
    """Категория затрат"""
    INFRASTRUCTURE = "infrastructure"
    DATA_TRANSFER = "data_transfer"
    STORAGE = "storage"
    SUPPORT = "support"
    LICENSING = "licensing"
    OTHER = "other"


class OptimizationType(Enum):
    """Тип оптимизации"""
    RIGHTSIZE = "rightsize"
    TERMINATE = "terminate"
    RESERVE = "reserve"
    SCHEDULE = "schedule"
    MIGRATE = "migrate"


@dataclass
class CostRecord:
    """Запись о затратах"""
    record_id: str
    
    # Resource
    resource_id: str = ""
    resource_name: str = ""
    resource_type: ResourceType = ResourceType.COMPUTE
    
    # Cost
    amount: float = 0.0
    currency: str = "USD"
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: Optional[datetime] = None
    
    # Allocation
    team: str = ""
    project: str = ""
    environment: str = ""
    
    # Pricing
    pricing_model: PricingModel = PricingModel.ON_DEMAND
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class Budget:
    """Бюджет"""
    budget_id: str
    name: str = ""
    
    # Amount
    total_amount: float = 0.0
    spent_amount: float = 0.0
    
    # Period
    period_type: str = "monthly"  # monthly, quarterly, yearly
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    
    # Alerts
    alert_thresholds: List[float] = field(default_factory=lambda: [50, 80, 100])
    
    # Scope
    team: str = ""
    project: str = ""
    
    @property
    def remaining(self) -> float:
        return max(0, self.total_amount - self.spent_amount)
        
    @property
    def utilization_percent(self) -> float:
        return (self.spent_amount / self.total_amount) * 100 if self.total_amount > 0 else 0


@dataclass
class ResourceMetrics:
    """Метрики использования ресурса"""
    resource_id: str
    
    # Utilization
    cpu_utilization: float = 0.0
    memory_utilization: float = 0.0
    storage_utilization: float = 0.0
    network_utilization: float = 0.0
    
    # Cost
    hourly_cost: float = 0.0
    monthly_cost: float = 0.0
    
    # Time
    measured_at: datetime = field(default_factory=datetime.now)


@dataclass
class Recommendation:
    """Рекомендация по оптимизации"""
    recommendation_id: str
    
    # Type
    optimization_type: OptimizationType = OptimizationType.RIGHTSIZE
    
    # Resource
    resource_id: str = ""
    resource_name: str = ""
    
    # Description
    title: str = ""
    description: str = ""
    
    # Impact
    current_cost: float = 0.0
    projected_cost: float = 0.0
    monthly_savings: float = 0.0
    annual_savings: float = 0.0
    
    # Confidence
    confidence: float = 0.0  # 0-100
    
    # Effort
    implementation_effort: str = "low"  # low, medium, high
    
    # Risk
    risk_level: str = "low"  # low, medium, high
    
    # Status
    status: str = "open"  # open, accepted, rejected, implemented
    
    # Created
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ReservedInstance:
    """Зарезервированный инстанс"""
    reservation_id: str
    
    # Instance
    instance_type: str = ""
    region: str = ""
    
    # Commitment
    term_months: int = 12
    payment_option: str = "no_upfront"  # no_upfront, partial_upfront, all_upfront
    
    # Cost
    hourly_rate: float = 0.0
    upfront_cost: float = 0.0
    
    # Coverage
    quantity: int = 1
    utilization_percent: float = 0.0
    
    # Timing
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None


class CostAnalyzer:
    """Анализатор затрат"""
    
    def __init__(self):
        self.cost_records: List[CostRecord] = []
        
    def add_record(self, record: CostRecord):
        """Добавление записи"""
        self.cost_records.append(record)
        
    def get_total_cost(self, start: datetime = None, end: datetime = None) -> float:
        """Получение общих затрат"""
        records = self.cost_records
        
        if start:
            records = [r for r in records if r.period_start >= start]
        if end:
            records = [r for r in records if r.period_end and r.period_end <= end]
            
        return sum(r.amount for r in records)
        
    def get_cost_by_team(self) -> Dict[str, float]:
        """Затраты по командам"""
        costs = {}
        for record in self.cost_records:
            team = record.team or "unallocated"
            costs[team] = costs.get(team, 0) + record.amount
        return costs
        
    def get_cost_by_type(self) -> Dict[str, float]:
        """Затраты по типам ресурсов"""
        costs = {}
        for record in self.cost_records:
            rtype = record.resource_type.value
            costs[rtype] = costs.get(rtype, 0) + record.amount
        return costs
        
    def get_cost_trend(self, days: int = 30) -> List[Dict[str, Any]]:
        """Тренд затрат"""
        trend = []
        for i in range(days):
            date = datetime.now() - timedelta(days=days - i)
            daily_records = [
                r for r in self.cost_records
                if r.period_start.date() == date.date()
            ]
            trend.append({
                "date": date.strftime("%Y-%m-%d"),
                "cost": sum(r.amount for r in daily_records)
            })
        return trend


class RightsizingEngine:
    """Движок оптимизации размеров"""
    
    def __init__(self):
        self.metrics: Dict[str, ResourceMetrics] = {}
        
    def add_metrics(self, metrics: ResourceMetrics):
        """Добавление метрик"""
        self.metrics[metrics.resource_id] = metrics
        
    def analyze(self) -> List[Recommendation]:
        """Анализ и рекомендации"""
        recommendations = []
        
        for resource_id, metrics in self.metrics.items():
            # Underutilized CPU
            if metrics.cpu_utilization < 20 and metrics.monthly_cost > 50:
                rec = Recommendation(
                    recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
                    optimization_type=OptimizationType.RIGHTSIZE,
                    resource_id=resource_id,
                    title=f"Rightsize underutilized instance",
                    description=f"CPU utilization is only {metrics.cpu_utilization:.1f}%",
                    current_cost=metrics.monthly_cost,
                    projected_cost=metrics.monthly_cost * 0.5,
                    monthly_savings=metrics.monthly_cost * 0.5,
                    annual_savings=metrics.monthly_cost * 0.5 * 12,
                    confidence=85,
                    implementation_effort="medium"
                )
                recommendations.append(rec)
                
            # Very low utilization - terminate
            if metrics.cpu_utilization < 5 and metrics.memory_utilization < 5:
                rec = Recommendation(
                    recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
                    optimization_type=OptimizationType.TERMINATE,
                    resource_id=resource_id,
                    title=f"Terminate idle resource",
                    description=f"Resource appears to be idle (CPU: {metrics.cpu_utilization:.1f}%)",
                    current_cost=metrics.monthly_cost,
                    projected_cost=0,
                    monthly_savings=metrics.monthly_cost,
                    annual_savings=metrics.monthly_cost * 12,
                    confidence=70,
                    implementation_effort="low",
                    risk_level="medium"
                )
                recommendations.append(rec)
                
        return recommendations


class BudgetManager:
    """Менеджер бюджетов"""
    
    def __init__(self, cost_analyzer: CostAnalyzer):
        self.cost_analyzer = cost_analyzer
        self.budgets: Dict[str, Budget] = {}
        self.alerts: List[Dict[str, Any]] = []
        
    def create_budget(self, name: str, amount: float, team: str = "", 
                     project: str = "") -> Budget:
        """Создание бюджета"""
        budget = Budget(
            budget_id=f"budget_{uuid.uuid4().hex[:8]}",
            name=name,
            total_amount=amount,
            team=team,
            project=project,
            end_date=datetime.now() + timedelta(days=30)
        )
        self.budgets[budget.budget_id] = budget
        return budget
        
    def update_spending(self):
        """Обновление трат"""
        for budget in self.budgets.values():
            # Calculate spent amount based on cost records
            relevant_costs = [
                r for r in self.cost_analyzer.cost_records
                if (not budget.team or r.team == budget.team) and
                   (not budget.project or r.project == budget.project)
            ]
            budget.spent_amount = sum(r.amount for r in relevant_costs)
            
            # Check alerts
            self._check_alerts(budget)
            
    def _check_alerts(self, budget: Budget):
        """Проверка алертов"""
        util = budget.utilization_percent
        
        for threshold in budget.alert_thresholds:
            if util >= threshold:
                alert = {
                    "budget_id": budget.budget_id,
                    "budget_name": budget.name,
                    "threshold": threshold,
                    "utilization": util,
                    "timestamp": datetime.now()
                }
                if alert not in self.alerts:
                    self.alerts.append(alert)


class ReservationPlanner:
    """Планировщик резервирования"""
    
    def __init__(self, cost_analyzer: CostAnalyzer):
        self.cost_analyzer = cost_analyzer
        self.reservations: Dict[str, ReservedInstance] = {}
        
    def analyze_reservation_opportunity(self) -> List[Recommendation]:
        """Анализ возможностей резервирования"""
        recommendations = []
        
        # Group on-demand costs by instance type
        on_demand_costs = {}
        
        for record in self.cost_analyzer.cost_records:
            if record.pricing_model == PricingModel.ON_DEMAND:
                key = record.resource_type.value
                if key not in on_demand_costs:
                    on_demand_costs[key] = {"cost": 0, "count": 0}
                on_demand_costs[key]["cost"] += record.amount
                on_demand_costs[key]["count"] += 1
                
        for resource_type, data in on_demand_costs.items():
            if data["cost"] > 1000:  # Significant spend
                # Reserved typically saves 30-40%
                savings_rate = 0.35
                
                rec = Recommendation(
                    recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
                    optimization_type=OptimizationType.RESERVE,
                    title=f"Purchase Reserved Instances for {resource_type}",
                    description=f"Consistent usage pattern detected for {data['count']} resources",
                    current_cost=data["cost"],
                    projected_cost=data["cost"] * (1 - savings_rate),
                    monthly_savings=data["cost"] * savings_rate,
                    annual_savings=data["cost"] * savings_rate * 12,
                    confidence=80,
                    implementation_effort="low"
                )
                recommendations.append(rec)
                
        return recommendations


class CostOptimizationPlatform:
    """Платформа оптимизации затрат"""
    
    def __init__(self):
        self.cost_analyzer = CostAnalyzer()
        self.rightsizing_engine = RightsizingEngine()
        self.budget_manager = BudgetManager(self.cost_analyzer)
        self.reservation_planner = ReservationPlanner(self.cost_analyzer)
        self.recommendations: List[Recommendation] = []
        
    def get_all_recommendations(self) -> List[Recommendation]:
        """Получение всех рекомендаций"""
        recs = []
        recs.extend(self.rightsizing_engine.analyze())
        recs.extend(self.reservation_planner.analyze_reservation_opportunity())
        self.recommendations = recs
        return recs
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_cost = self.cost_analyzer.get_total_cost()
        potential_savings = sum(r.monthly_savings for r in self.recommendations)
        
        return {
            "total_monthly_cost": total_cost,
            "potential_savings": potential_savings,
            "savings_percent": (potential_savings / total_cost * 100) if total_cost > 0 else 0,
            "total_recommendations": len(self.recommendations),
            "budgets": len(self.budget_manager.budgets),
            "cost_by_type": self.cost_analyzer.get_cost_by_type(),
            "cost_by_team": self.cost_analyzer.get_cost_by_team()
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 189: Cost Optimization Platform")
    print("=" * 60)
    
    platform = CostOptimizationPlatform()
    print("✓ Cost Optimization Platform created")
    
    # Add cost records
    print("\n💰 Adding Cost Records...")
    
    teams = ["platform", "data", "backend", "frontend", "ml"]
    projects = ["project-alpha", "project-beta", "project-gamma"]
    
    for i in range(50):
        record = CostRecord(
            record_id=f"cost_{uuid.uuid4().hex[:8]}",
            resource_id=f"resource_{i}",
            resource_name=f"resource-{i}",
            resource_type=random.choice(list(ResourceType)),
            amount=random.uniform(50, 2000),
            team=random.choice(teams),
            project=random.choice(projects),
            environment=random.choice(["production", "staging", "development"]),
            pricing_model=random.choice([PricingModel.ON_DEMAND] * 7 + [PricingModel.RESERVED] * 3),
            period_start=datetime.now() - timedelta(days=random.randint(0, 30))
        )
        platform.cost_analyzer.add_record(record)
        
    print(f"  Added {len(platform.cost_analyzer.cost_records)} cost records")
    
    # Cost breakdown
    print("\n📊 Cost Breakdown:")
    
    by_type = platform.cost_analyzer.get_cost_by_type()
    by_team = platform.cost_analyzer.get_cost_by_team()
    total = platform.cost_analyzer.get_total_cost()
    
    print(f"\n  Total Cost: ${total:,.2f}")
    
    print("\n  By Resource Type:")
    for rtype, cost in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
        percent = (cost / total * 100) if total > 0 else 0
        bar = "█" * int(percent / 5) + "░" * (20 - int(percent / 5))
        print(f"    {rtype:15} ${cost:>10,.2f} [{bar}] {percent:.1f}%")
        
    print("\n  By Team:")
    for team, cost in sorted(by_team.items(), key=lambda x: x[1], reverse=True):
        percent = (cost / total * 100) if total > 0 else 0
        print(f"    {team:15} ${cost:>10,.2f} ({percent:.1f}%)")
        
    # Add resource metrics
    print("\n📈 Adding Resource Metrics...")
    
    for i in range(30):
        metrics = ResourceMetrics(
            resource_id=f"resource_{i}",
            cpu_utilization=random.uniform(5, 80),
            memory_utilization=random.uniform(10, 90),
            hourly_cost=random.uniform(0.1, 5),
            monthly_cost=random.uniform(50, 2000)
        )
        platform.rightsizing_engine.add_metrics(metrics)
        
    print(f"  Added metrics for {len(platform.rightsizing_engine.metrics)} resources")
    
    # Create budgets
    print("\n📋 Creating Budgets...")
    
    budgets = [
        platform.budget_manager.create_budget("Platform Team Budget", 15000, team="platform"),
        platform.budget_manager.create_budget("Data Team Budget", 20000, team="data"),
        platform.budget_manager.create_budget("Project Alpha", 10000, project="project-alpha"),
    ]
    
    platform.budget_manager.update_spending()
    
    for budget in budgets:
        status = "🟢" if budget.utilization_percent < 80 else ("🟡" if budget.utilization_percent < 100 else "🔴")
        print(f"  {status} {budget.name}: ${budget.spent_amount:,.2f} / ${budget.total_amount:,.2f} ({budget.utilization_percent:.1f}%)")
        
    # Get recommendations
    print("\n💡 Cost Optimization Recommendations:")
    
    recommendations = platform.get_all_recommendations()
    
    print(f"\n  Found {len(recommendations)} recommendations")
    
    total_savings = sum(r.monthly_savings for r in recommendations)
    print(f"  Potential Monthly Savings: ${total_savings:,.2f}")
    
    print("\n  ┌─────────────────────────────────────────────┬─────────────┬─────────────┬────────────┐")
    print("  │ Recommendation                              │ Type        │ Monthly $   │ Confidence │")
    print("  ├─────────────────────────────────────────────┼─────────────┼─────────────┼────────────┤")
    
    for rec in recommendations[:10]:
        title = rec.title[:43].ljust(43)
        rtype = rec.optimization_type.value[:11].ljust(11)
        savings = f"${rec.monthly_savings:,.0f}".rjust(11)
        conf = f"{rec.confidence:.0f}%".rjust(10)
        print(f"  │ {title} │ {rtype} │ {savings} │ {conf} │")
        
    print("  └─────────────────────────────────────────────┴─────────────┴─────────────┴────────────┘")
    
    # Detailed recommendations
    print("\n📋 Top Recommendations:")
    
    top_recs = sorted(recommendations, key=lambda r: r.monthly_savings, reverse=True)[:3]
    
    for rec in top_recs:
        icon = "💰" if rec.optimization_type == OptimizationType.RESERVE else ("📉" if rec.optimization_type == OptimizationType.RIGHTSIZE else "🗑️")
        print(f"\n  {icon} {rec.title}")
        print(f"     Type: {rec.optimization_type.value}")
        print(f"     Description: {rec.description}")
        print(f"     Current Cost: ${rec.current_cost:,.2f}/month")
        print(f"     Projected Cost: ${rec.projected_cost:,.2f}/month")
        print(f"     Monthly Savings: ${rec.monthly_savings:,.2f}")
        print(f"     Annual Savings: ${rec.annual_savings:,.2f}")
        print(f"     Confidence: {rec.confidence}%")
        print(f"     Implementation Effort: {rec.implementation_effort}")
        
    # Budget alerts
    print("\n⚠️ Budget Alerts:")
    
    if platform.budget_manager.alerts:
        for alert in platform.budget_manager.alerts:
            print(f"  ⚠️ {alert['budget_name']}: {alert['utilization']:.1f}% (threshold: {alert['threshold']}%)")
    else:
        print("  ✓ No budget alerts")
        
    # Cost trend
    print("\n📈 Cost Trend (Last 7 Days):")
    
    trend = platform.cost_analyzer.get_cost_trend(7)
    
    max_cost = max(d['cost'] for d in trend) if trend else 0
    
    for day in trend:
        bar_len = int((day['cost'] / max_cost) * 30) if max_cost > 0 else 0
        bar = "█" * bar_len
        print(f"  {day['date']}: ${day['cost']:>8,.2f} {bar}")
        
    # Savings summary
    print("\n💵 Savings Summary:")
    
    by_type_savings = {}
    for rec in recommendations:
        rtype = rec.optimization_type.value
        if rtype not in by_type_savings:
            by_type_savings[rtype] = 0
        by_type_savings[rtype] += rec.monthly_savings
        
    print(f"\n  Total Potential Monthly Savings: ${total_savings:,.2f}")
    print(f"  Total Potential Annual Savings: ${total_savings * 12:,.2f}")
    
    print("\n  By Optimization Type:")
    for otype, savings in sorted(by_type_savings.items(), key=lambda x: x[1], reverse=True):
        print(f"    {otype}: ${savings:,.2f}/month")
        
    # Platform statistics
    print("\n📊 Platform Statistics:")
    
    stats = platform.get_statistics()
    
    print(f"\n  Total Monthly Cost: ${stats['total_monthly_cost']:,.2f}")
    print(f"  Potential Savings: ${stats['potential_savings']:,.2f} ({stats['savings_percent']:.1f}%)")
    print(f"  Recommendations: {stats['total_recommendations']}")
    print(f"  Active Budgets: {stats['budgets']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Cost Optimization Dashboard                     │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Monthly Cost:            ${stats['total_monthly_cost']:>12,.2f}                │")
    print(f"│ Potential Savings:             ${stats['potential_savings']:>12,.2f}                │")
    print(f"│ Savings Opportunity:             {stats['savings_percent']:>10.1f}%                  │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Recommendations:          {stats['total_recommendations']:>12}                │")
    print(f"│ Active Budgets:                 {stats['budgets']:>12}                │")
    print(f"│ Budget Alerts:                  {len(platform.budget_manager.alerts):>12}                │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Cost Optimization Platform initialized!")
    print("=" * 60)
