#!/usr/bin/env python3
"""
Server Init - Iteration 164: Cost Optimization Platform
Платформа оптимизации затрат

Функционал:
- Cost Analysis - анализ затрат
- Resource Optimization - оптимизация ресурсов
- Rightsizing Recommendations - рекомендации по правильному размеру
- Reserved Instance Planning - планирование резервных инстансов
- Spot Instance Management - управление спот-инстансами
- Budget Management - управление бюджетом
- Cost Allocation - распределение затрат
- Savings Tracking - отслеживание экономии
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import uuid
import random
import math


class ResourceType(Enum):
    """Тип ресурса"""
    COMPUTE = "compute"
    STORAGE = "storage"
    DATABASE = "database"
    NETWORK = "network"
    CONTAINER = "container"
    SERVERLESS = "serverless"


class PricingModel(Enum):
    """Модель ценообразования"""
    ON_DEMAND = "on_demand"
    RESERVED = "reserved"
    SPOT = "spot"
    SAVINGS_PLAN = "savings_plan"


class OptimizationType(Enum):
    """Тип оптимизации"""
    RIGHTSIZING = "rightsizing"
    SCHEDULING = "scheduling"
    RESERVED_PURCHASE = "reserved_purchase"
    SPOT_USAGE = "spot_usage"
    STORAGE_TIERING = "storage_tiering"
    TERMINATION = "termination"


class AlertSeverity(Enum):
    """Серьёзность алерта"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BudgetPeriod(Enum):
    """Период бюджета"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


@dataclass
class CloudResource:
    """Облачный ресурс"""
    resource_id: str
    name: str = ""
    resource_type: ResourceType = ResourceType.COMPUTE
    
    # Configuration
    instance_type: str = ""
    region: str = ""
    
    # Pricing
    pricing_model: PricingModel = PricingModel.ON_DEMAND
    hourly_cost: float = 0.0
    monthly_cost: float = 0.0
    
    # Utilization
    cpu_utilization: float = 0.0
    memory_utilization: float = 0.0
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Owner
    owner: str = ""
    team: str = ""
    project: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None


@dataclass
class CostRecord:
    """Запись о затратах"""
    record_id: str
    resource_id: str = ""
    
    # Cost
    amount: float = 0.0
    currency: str = "USD"
    
    # Period
    date: datetime = field(default_factory=datetime.now)
    
    # Breakdown
    compute_cost: float = 0.0
    storage_cost: float = 0.0
    network_cost: float = 0.0
    other_cost: float = 0.0
    
    # Allocation
    team: str = ""
    project: str = ""
    environment: str = ""


@dataclass
class OptimizationRecommendation:
    """Рекомендация по оптимизации"""
    recommendation_id: str
    resource_id: str = ""
    
    # Type
    optimization_type: OptimizationType = OptimizationType.RIGHTSIZING
    
    # Details
    title: str = ""
    description: str = ""
    
    # Savings
    current_cost: float = 0.0
    projected_cost: float = 0.0
    monthly_savings: float = 0.0
    annual_savings: float = 0.0
    
    # Risk
    risk_level: AlertSeverity = AlertSeverity.LOW
    
    # Action
    action: str = ""
    effort: str = ""  # low, medium, high
    
    # Status
    status: str = "pending"  # pending, accepted, rejected, implemented
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Budget:
    """Бюджет"""
    budget_id: str
    name: str = ""
    
    # Amount
    amount: float = 0.0
    currency: str = "USD"
    
    # Period
    period: BudgetPeriod = BudgetPeriod.MONTHLY
    start_date: datetime = field(default_factory=datetime.now)
    
    # Actual
    actual_spend: float = 0.0
    forecasted_spend: float = 0.0
    
    # Thresholds
    warning_threshold: float = 80.0  # percentage
    critical_threshold: float = 100.0
    
    # Scope
    team: str = ""
    project: str = ""
    
    # Alerts
    alert_emails: List[str] = field(default_factory=list)


@dataclass
class CostAllocation:
    """Распределение затрат"""
    allocation_id: str
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Totals
    total_cost: float = 0.0
    
    # Breakdowns
    by_team: Dict[str, float] = field(default_factory=dict)
    by_project: Dict[str, float] = field(default_factory=dict)
    by_environment: Dict[str, float] = field(default_factory=dict)
    by_resource_type: Dict[str, float] = field(default_factory=dict)
    by_region: Dict[str, float] = field(default_factory=dict)


@dataclass
class ReservedInstance:
    """Резервный инстанс"""
    reservation_id: str
    instance_type: str = ""
    
    # Term
    term_months: int = 12
    payment_option: str = "no_upfront"  # no_upfront, partial_upfront, all_upfront
    
    # Quantity
    quantity: int = 1
    
    # Pricing
    upfront_cost: float = 0.0
    hourly_cost: float = 0.0
    effective_hourly_cost: float = 0.0
    
    # Savings
    on_demand_hourly: float = 0.0
    savings_percentage: float = 0.0
    
    # Coverage
    covered_instances: List[str] = field(default_factory=list)
    utilization_percentage: float = 0.0
    
    # Dates
    start_date: datetime = field(default_factory=datetime.now)
    end_date: datetime = field(default_factory=datetime.now)


@dataclass
class SavingsRecord:
    """Запись об экономии"""
    record_id: str
    
    # Source
    optimization_type: OptimizationType = OptimizationType.RIGHTSIZING
    recommendation_id: str = ""
    
    # Amount
    savings_amount: float = 0.0
    currency: str = "USD"
    
    # Period
    date: datetime = field(default_factory=datetime.now)
    
    # Details
    description: str = ""


class CostAnalyzer:
    """Анализатор затрат"""
    
    def __init__(self):
        self.resources: Dict[str, CloudResource] = {}
        self.cost_records: List[CostRecord] = []
        
    def add_resource(self, resource: CloudResource):
        """Добавление ресурса"""
        self.resources[resource.resource_id] = resource
        
    def record_cost(self, record: CostRecord):
        """Запись затрат"""
        self.cost_records.append(record)
        
    def get_total_cost(self, days: int = 30) -> float:
        """Общие затраты"""
        cutoff = datetime.now() - timedelta(days=days)
        
        total = 0.0
        for record in self.cost_records:
            if record.date >= cutoff:
                total += record.amount
                
        return total
        
    def get_cost_trend(self, days: int = 30) -> List[Tuple[datetime, float]]:
        """Тренд затрат"""
        cutoff = datetime.now() - timedelta(days=days)
        
        daily_costs: Dict[str, float] = {}
        
        for record in self.cost_records:
            if record.date >= cutoff:
                day_key = record.date.strftime("%Y-%m-%d")
                daily_costs[day_key] = daily_costs.get(day_key, 0) + record.amount
                
        trend = [(datetime.strptime(k, "%Y-%m-%d"), v) 
                 for k, v in sorted(daily_costs.items())]
                 
        return trend
        
    def get_cost_by_dimension(self, dimension: str) -> Dict[str, float]:
        """Затраты по измерению"""
        costs: Dict[str, float] = {}
        
        for record in self.cost_records:
            key = getattr(record, dimension, "unknown")
            costs[key] = costs.get(key, 0) + record.amount
            
        return costs


class ResourceOptimizer:
    """Оптимизатор ресурсов"""
    
    def __init__(self, analyzer: CostAnalyzer):
        self.analyzer = analyzer
        self.recommendations: List[OptimizationRecommendation] = []
        
    def analyze_rightsizing(self) -> List[OptimizationRecommendation]:
        """Анализ правильного размера"""
        recommendations = []
        
        for resource_id, resource in self.analyzer.resources.items():
            if resource.resource_type != ResourceType.COMPUTE:
                continue
                
            # Check utilization
            if resource.cpu_utilization < 20 and resource.memory_utilization < 20:
                # Severely underutilized
                savings = resource.monthly_cost * 0.5
                
                rec = OptimizationRecommendation(
                    recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
                    resource_id=resource_id,
                    optimization_type=OptimizationType.RIGHTSIZING,
                    title=f"Downsize {resource.name}",
                    description=f"Resource is severely underutilized (CPU: {resource.cpu_utilization:.1f}%, Memory: {resource.memory_utilization:.1f}%)",
                    current_cost=resource.monthly_cost,
                    projected_cost=resource.monthly_cost * 0.5,
                    monthly_savings=savings,
                    annual_savings=savings * 12,
                    risk_level=AlertSeverity.LOW,
                    action=f"Resize from {resource.instance_type} to smaller instance",
                    effort="low"
                )
                recommendations.append(rec)
                
            elif resource.cpu_utilization < 40 and resource.memory_utilization < 40:
                # Underutilized
                savings = resource.monthly_cost * 0.3
                
                rec = OptimizationRecommendation(
                    recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
                    resource_id=resource_id,
                    optimization_type=OptimizationType.RIGHTSIZING,
                    title=f"Consider downsizing {resource.name}",
                    description=f"Resource is underutilized (CPU: {resource.cpu_utilization:.1f}%, Memory: {resource.memory_utilization:.1f}%)",
                    current_cost=resource.monthly_cost,
                    projected_cost=resource.monthly_cost * 0.7,
                    monthly_savings=savings,
                    annual_savings=savings * 12,
                    risk_level=AlertSeverity.MEDIUM,
                    action=f"Review and potentially resize {resource.instance_type}",
                    effort="medium"
                )
                recommendations.append(rec)
                
        return recommendations
        
    def analyze_idle_resources(self) -> List[OptimizationRecommendation]:
        """Анализ простаивающих ресурсов"""
        recommendations = []
        
        for resource_id, resource in self.analyzer.resources.items():
            # Check if not used recently
            if resource.last_used:
                days_idle = (datetime.now() - resource.last_used).days
                
                if days_idle > 30:
                    rec = OptimizationRecommendation(
                        recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
                        resource_id=resource_id,
                        optimization_type=OptimizationType.TERMINATION,
                        title=f"Terminate idle resource {resource.name}",
                        description=f"Resource has been idle for {days_idle} days",
                        current_cost=resource.monthly_cost,
                        projected_cost=0,
                        monthly_savings=resource.monthly_cost,
                        annual_savings=resource.monthly_cost * 12,
                        risk_level=AlertSeverity.LOW,
                        action="Terminate or delete resource",
                        effort="low"
                    )
                    recommendations.append(rec)
                    
        return recommendations
        
    def analyze_reserved_opportunity(self) -> List[OptimizationRecommendation]:
        """Анализ возможностей резервирования"""
        recommendations = []
        
        # Group by instance type
        by_type: Dict[str, List[CloudResource]] = {}
        
        for resource in self.analyzer.resources.values():
            if resource.pricing_model == PricingModel.ON_DEMAND:
                if resource.instance_type not in by_type:
                    by_type[resource.instance_type] = []
                by_type[resource.instance_type].append(resource)
                
        for instance_type, resources in by_type.items():
            if len(resources) >= 3:  # At least 3 instances
                total_cost = sum(r.monthly_cost for r in resources)
                savings = total_cost * 0.30  # 30% typical RI savings
                
                rec = OptimizationRecommendation(
                    recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
                    resource_id="multiple",
                    optimization_type=OptimizationType.RESERVED_PURCHASE,
                    title=f"Purchase Reserved Instances for {instance_type}",
                    description=f"You have {len(resources)} on-demand instances of {instance_type}",
                    current_cost=total_cost,
                    projected_cost=total_cost * 0.7,
                    monthly_savings=savings,
                    annual_savings=savings * 12,
                    risk_level=AlertSeverity.MEDIUM,
                    action=f"Purchase {len(resources)} Reserved Instances",
                    effort="medium"
                )
                recommendations.append(rec)
                
        return recommendations
        
    def generate_all_recommendations(self) -> List[OptimizationRecommendation]:
        """Генерация всех рекомендаций"""
        self.recommendations = []
        
        self.recommendations.extend(self.analyze_rightsizing())
        self.recommendations.extend(self.analyze_idle_resources())
        self.recommendations.extend(self.analyze_reserved_opportunity())
        
        # Sort by savings
        self.recommendations.sort(key=lambda r: r.monthly_savings, reverse=True)
        
        return self.recommendations


class BudgetManager:
    """Менеджер бюджета"""
    
    def __init__(self, analyzer: CostAnalyzer):
        self.analyzer = analyzer
        self.budgets: Dict[str, Budget] = {}
        self.alerts: List[Dict] = []
        
    def create_budget(self, name: str, amount: float, period: BudgetPeriod,
                       team: str = "", project: str = "") -> Budget:
        """Создание бюджета"""
        budget = Budget(
            budget_id=f"budget_{uuid.uuid4().hex[:8]}",
            name=name,
            amount=amount,
            period=period,
            team=team,
            project=project
        )
        self.budgets[budget.budget_id] = budget
        return budget
        
    def update_budget_spend(self, budget_id: str):
        """Обновление расходов бюджета"""
        if budget_id not in self.budgets:
            return
            
        budget = self.budgets[budget_id]
        
        # Calculate period days
        period_days = {
            BudgetPeriod.DAILY: 1,
            BudgetPeriod.WEEKLY: 7,
            BudgetPeriod.MONTHLY: 30,
            BudgetPeriod.QUARTERLY: 90,
            BudgetPeriod.YEARLY: 365,
        }.get(budget.period, 30)
        
        # Get actual spend
        cutoff = datetime.now() - timedelta(days=period_days)
        
        actual = 0.0
        for record in self.analyzer.cost_records:
            if record.date >= cutoff:
                if budget.team and record.team != budget.team:
                    continue
                if budget.project and record.project != budget.project:
                    continue
                actual += record.amount
                
        budget.actual_spend = actual
        
        # Calculate forecast
        days_elapsed = (datetime.now() - budget.start_date).days or 1
        daily_rate = actual / days_elapsed
        budget.forecasted_spend = daily_rate * period_days
        
        # Check thresholds
        spend_percentage = (actual / budget.amount * 100) if budget.amount > 0 else 0
        
        if spend_percentage >= budget.critical_threshold:
            self._create_alert(budget, "critical", spend_percentage)
        elif spend_percentage >= budget.warning_threshold:
            self._create_alert(budget, "warning", spend_percentage)
            
    def _create_alert(self, budget: Budget, severity: str, percentage: float):
        """Создание алерта"""
        alert = {
            "alert_id": f"alert_{uuid.uuid4().hex[:8]}",
            "budget_id": budget.budget_id,
            "budget_name": budget.name,
            "severity": severity,
            "percentage": percentage,
            "actual": budget.actual_spend,
            "limit": budget.amount,
            "timestamp": datetime.now().isoformat()
        }
        self.alerts.append(alert)
        
    def get_budget_status(self) -> List[Dict]:
        """Статус бюджетов"""
        status = []
        
        for budget in self.budgets.values():
            self.update_budget_spend(budget.budget_id)
            
            spend_pct = (budget.actual_spend / budget.amount * 100) if budget.amount > 0 else 0
            forecast_pct = (budget.forecasted_spend / budget.amount * 100) if budget.amount > 0 else 0
            
            status.append({
                "budget_id": budget.budget_id,
                "name": budget.name,
                "amount": budget.amount,
                "actual_spend": budget.actual_spend,
                "forecasted_spend": budget.forecasted_spend,
                "spend_percentage": spend_pct,
                "forecast_percentage": forecast_pct,
                "status": "critical" if spend_pct >= budget.critical_threshold else
                         "warning" if spend_pct >= budget.warning_threshold else "healthy"
            })
            
        return status


class CostAllocator:
    """Распределитель затрат"""
    
    def __init__(self, analyzer: CostAnalyzer):
        self.analyzer = analyzer
        
    def allocate_costs(self, start_date: datetime,
                        end_date: datetime) -> CostAllocation:
        """Распределение затрат"""
        allocation = CostAllocation(
            allocation_id=f"alloc_{uuid.uuid4().hex[:8]}",
            period_start=start_date,
            period_end=end_date
        )
        
        for record in self.analyzer.cost_records:
            if start_date <= record.date <= end_date:
                allocation.total_cost += record.amount
                
                # By team
                team = record.team or "untagged"
                allocation.by_team[team] = allocation.by_team.get(team, 0) + record.amount
                
                # By project
                project = record.project or "untagged"
                allocation.by_project[project] = allocation.by_project.get(project, 0) + record.amount
                
                # By environment
                env = record.environment or "untagged"
                allocation.by_environment[env] = allocation.by_environment.get(env, 0) + record.amount
                
        # By resource type
        for resource in self.analyzer.resources.values():
            res_type = resource.resource_type.value
            allocation.by_resource_type[res_type] = allocation.by_resource_type.get(res_type, 0) + resource.monthly_cost
            
            region = resource.region or "unknown"
            allocation.by_region[region] = allocation.by_region.get(region, 0) + resource.monthly_cost
            
        return allocation


class ReservedInstancePlanner:
    """Планировщик резервных инстансов"""
    
    def __init__(self, analyzer: CostAnalyzer):
        self.analyzer = analyzer
        self.reservations: Dict[str, ReservedInstance] = {}
        
    def analyze_coverage(self) -> Dict[str, Any]:
        """Анализ покрытия"""
        on_demand_cost = 0.0
        reserved_cost = 0.0
        
        for resource in self.analyzer.resources.values():
            if resource.pricing_model == PricingModel.ON_DEMAND:
                on_demand_cost += resource.monthly_cost
            elif resource.pricing_model == PricingModel.RESERVED:
                reserved_cost += resource.monthly_cost
                
        total = on_demand_cost + reserved_cost
        coverage = (reserved_cost / total * 100) if total > 0 else 0
        
        return {
            "on_demand_cost": on_demand_cost,
            "reserved_cost": reserved_cost,
            "total_cost": total,
            "coverage_percentage": coverage,
            "target_coverage": 70,  # Target 70% coverage
            "gap": max(0, 70 - coverage)
        }
        
    def recommend_reservations(self) -> List[Dict]:
        """Рекомендации по резервированию"""
        recommendations = []
        
        # Group stable workloads by instance type
        by_type: Dict[str, List[CloudResource]] = {}
        
        for resource in self.analyzer.resources.values():
            if resource.pricing_model == PricingModel.ON_DEMAND:
                if resource.cpu_utilization > 40:  # Stable utilization
                    if resource.instance_type not in by_type:
                        by_type[resource.instance_type] = []
                    by_type[resource.instance_type].append(resource)
                    
        for instance_type, resources in by_type.items():
            on_demand_hourly = resources[0].hourly_cost if resources else 0
            reserved_hourly = on_demand_hourly * 0.6  # 40% discount
            
            monthly_savings = (on_demand_hourly - reserved_hourly) * 730 * len(resources)
            
            recommendations.append({
                "instance_type": instance_type,
                "quantity": len(resources),
                "on_demand_hourly": on_demand_hourly,
                "reserved_hourly": reserved_hourly,
                "monthly_savings": monthly_savings,
                "annual_savings": monthly_savings * 12,
                "recommended_term": "1 year",
                "payment_option": "no_upfront"
            })
            
        return sorted(recommendations, key=lambda r: r["annual_savings"], reverse=True)


class SavingsTracker:
    """Трекер экономии"""
    
    def __init__(self):
        self.savings_records: List[SavingsRecord] = []
        
    def record_savings(self, optimization_type: OptimizationType,
                        amount: float, description: str,
                        recommendation_id: str = ""):
        """Запись экономии"""
        record = SavingsRecord(
            record_id=f"save_{uuid.uuid4().hex[:8]}",
            optimization_type=optimization_type,
            recommendation_id=recommendation_id,
            savings_amount=amount,
            description=description
        )
        self.savings_records.append(record)
        
    def get_total_savings(self, days: int = 30) -> float:
        """Общая экономия"""
        cutoff = datetime.now() - timedelta(days=days)
        
        total = 0.0
        for record in self.savings_records:
            if record.date >= cutoff:
                total += record.savings_amount
                
        return total
        
    def get_savings_by_type(self) -> Dict[str, float]:
        """Экономия по типу"""
        by_type: Dict[str, float] = {}
        
        for record in self.savings_records:
            opt_type = record.optimization_type.value
            by_type[opt_type] = by_type.get(opt_type, 0) + record.savings_amount
            
        return by_type


class CostOptimizationPlatform:
    """Платформа оптимизации затрат"""
    
    def __init__(self):
        self.analyzer = CostAnalyzer()
        self.optimizer = ResourceOptimizer(self.analyzer)
        self.budget_manager = BudgetManager(self.analyzer)
        self.allocator = CostAllocator(self.analyzer)
        self.ri_planner = ReservedInstancePlanner(self.analyzer)
        self.savings_tracker = SavingsTracker()
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_cost = self.analyzer.get_total_cost(30)
        recommendations = self.optimizer.generate_all_recommendations()
        potential_savings = sum(r.monthly_savings for r in recommendations)
        realized_savings = self.savings_tracker.get_total_savings(30)
        
        return {
            "monthly_cost": total_cost,
            "resources": len(self.analyzer.resources),
            "recommendations": len(recommendations),
            "potential_savings": potential_savings,
            "realized_savings": realized_savings
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 164: Cost Optimization Platform")
    print("=" * 60)
    
    platform = CostOptimizationPlatform()
    print("✓ Cost Optimization Platform created")
    
    # Add sample resources
    print("\n📦 Adding Resources...")
    
    resources = [
        ("web-server-1", "Web Server 1", ResourceType.COMPUTE, "m5.xlarge", "us-east-1", 0.192, 140, 15, 20),
        ("web-server-2", "Web Server 2", ResourceType.COMPUTE, "m5.xlarge", "us-east-1", 0.192, 140, 65, 70),
        ("web-server-3", "Web Server 3", ResourceType.COMPUTE, "m5.xlarge", "us-east-1", 0.192, 140, 70, 75),
        ("api-server-1", "API Server 1", ResourceType.COMPUTE, "c5.2xlarge", "us-east-1", 0.34, 248, 45, 50),
        ("api-server-2", "API Server 2", ResourceType.COMPUTE, "c5.2xlarge", "us-east-1", 0.34, 248, 50, 55),
        ("db-primary", "Database Primary", ResourceType.DATABASE, "r5.2xlarge", "us-east-1", 0.504, 368, 60, 80),
        ("db-replica", "Database Replica", ResourceType.DATABASE, "r5.xlarge", "us-east-1", 0.252, 184, 25, 30),
        ("cache-1", "Redis Cache", ResourceType.COMPUTE, "r5.large", "us-east-1", 0.126, 92, 10, 15),
        ("storage-1", "Object Storage", ResourceType.STORAGE, "s3-standard", "us-east-1", 0.023, 500, 0, 0),
        ("cdn-1", "CDN Distribution", ResourceType.NETWORK, "cloudfront", "global", 0.085, 200, 0, 0),
    ]
    
    teams = ["platform", "backend", "frontend", "data"]
    projects = ["main-app", "api-gateway", "analytics", "ml-pipeline"]
    environments = ["production", "staging", "development"]
    
    for res_id, name, res_type, instance, region, hourly, monthly, cpu, mem in resources:
        resource = CloudResource(
            resource_id=res_id,
            name=name,
            resource_type=res_type,
            instance_type=instance,
            region=region,
            pricing_model=PricingModel.ON_DEMAND,
            hourly_cost=hourly,
            monthly_cost=monthly,
            cpu_utilization=cpu,
            memory_utilization=mem,
            team=random.choice(teams),
            project=random.choice(projects),
            last_used=datetime.now() - timedelta(days=random.randint(1, 45))
        )
        platform.analyzer.add_resource(resource)
        
    print(f"  ✓ Added {len(resources)} resources")
    
    # Generate cost records
    print("\n💰 Generating Cost Records...")
    
    for day in range(30):
        date = datetime.now() - timedelta(days=day)
        
        for resource in platform.analyzer.resources.values():
            daily_cost = resource.monthly_cost / 30 * random.uniform(0.9, 1.1)
            
            record = CostRecord(
                record_id=f"cost_{uuid.uuid4().hex[:8]}",
                resource_id=resource.resource_id,
                amount=daily_cost,
                date=date,
                team=resource.team,
                project=resource.project,
                environment=random.choice(environments)
            )
            platform.analyzer.record_cost(record)
            
    print(f"  ✓ Generated 30 days of cost records")
    
    # Cost overview
    print("\n📊 Cost Overview (Last 30 Days):")
    
    total_cost = platform.analyzer.get_total_cost(30)
    
    print(f"\n  Total Cost: ${total_cost:,.2f}")
    
    # Cost by team
    cost_by_team = platform.analyzer.get_cost_by_dimension("team")
    print("\n  By Team:")
    print("  ┌─────────────────────────────────────────────────────────────┐")
    
    for team, cost in sorted(cost_by_team.items(), key=lambda x: x[1], reverse=True):
        pct = cost / total_cost * 100 if total_cost > 0 else 0
        bar = "█" * int(pct / 5)
        print(f"  │ {team.ljust(15)} ${cost:>10,.2f} ({pct:>5.1f}%) {bar.ljust(20)} │")
        
    print("  └─────────────────────────────────────────────────────────────┘")
    
    # Generate recommendations
    print("\n💡 Optimization Recommendations:")
    
    recommendations = platform.optimizer.generate_all_recommendations()
    
    total_potential_savings = sum(r.monthly_savings for r in recommendations)
    
    print(f"\n  Found {len(recommendations)} recommendations")
    print(f"  Total Potential Monthly Savings: ${total_potential_savings:,.2f}")
    print(f"  Annual Savings Potential: ${total_potential_savings * 12:,.2f}")
    
    print("\n  Top Recommendations:")
    print("  ┌───────────────────────────────────────────────────────────────────────────┐")
    print("  │ Resource          │ Type           │ Monthly Save │ Annual Save │ Risk   │")
    print("  ├───────────────────────────────────────────────────────────────────────────┤")
    
    for rec in recommendations[:7]:
        resource = platform.analyzer.resources.get(rec.resource_id)
        name = (resource.name if resource else rec.resource_id)[:17].ljust(17)
        opt_type = rec.optimization_type.value[:14].ljust(14)
        monthly = f"${rec.monthly_savings:,.0f}".ljust(12)
        annual = f"${rec.annual_savings:,.0f}".ljust(11)
        risk = rec.risk_level.value[:6].ljust(6)
        print(f"  │ {name} │ {opt_type} │ {monthly} │ {annual} │ {risk} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────┘")
    
    # Budget management
    print("\n📋 Budget Management:")
    
    # Create budgets
    platform.budget_manager.create_budget(
        "Platform Team", 1500, BudgetPeriod.MONTHLY, team="platform"
    )
    platform.budget_manager.create_budget(
        "Backend Team", 2000, BudgetPeriod.MONTHLY, team="backend"
    )
    platform.budget_manager.create_budget(
        "Total Monthly", 5000, BudgetPeriod.MONTHLY
    )
    
    budget_status = platform.budget_manager.get_budget_status()
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────┐")
    print("  │ Budget            │ Limit      │ Actual     │ Forecast   │ Status    │")
    print("  ├───────────────────────────────────────────────────────────────────────┤")
    
    for status in budget_status:
        name = status["name"][:17].ljust(17)
        limit = f"${status['amount']:,.0f}".ljust(10)
        actual = f"${status['actual_spend']:,.0f}".ljust(10)
        forecast = f"${status['forecasted_spend']:,.0f}".ljust(10)
        st = status["status"][:9].ljust(9)
        print(f"  │ {name} │ {limit} │ {actual} │ {forecast} │ {st} │")
        
    print("  └───────────────────────────────────────────────────────────────────────┘")
    
    # Cost allocation
    print("\n📈 Cost Allocation:")
    
    allocation = platform.allocator.allocate_costs(
        datetime.now() - timedelta(days=30),
        datetime.now()
    )
    
    print(f"\n  Total Allocated: ${allocation.total_cost:,.2f}")
    
    print("\n  By Resource Type:")
    for res_type, cost in sorted(allocation.by_resource_type.items(),
                                  key=lambda x: x[1], reverse=True):
        pct = cost / allocation.total_cost * 100 if allocation.total_cost > 0 else 0
        print(f"    {res_type.ljust(12)}: ${cost:>10,.2f} ({pct:>5.1f}%)")
        
    print("\n  By Environment:")
    for env, cost in sorted(allocation.by_environment.items(),
                            key=lambda x: x[1], reverse=True):
        pct = cost / allocation.total_cost * 100 if allocation.total_cost > 0 else 0
        print(f"    {env.ljust(12)}: ${cost:>10,.2f} ({pct:>5.1f}%)")
        
    # Reserved Instance Analysis
    print("\n🔒 Reserved Instance Analysis:")
    
    coverage = platform.ri_planner.analyze_coverage()
    
    print(f"\n  On-Demand Cost: ${coverage['on_demand_cost']:,.2f}/month")
    print(f"  Reserved Cost: ${coverage['reserved_cost']:,.2f}/month")
    print(f"  Current Coverage: {coverage['coverage_percentage']:.1f}%")
    print(f"  Target Coverage: {coverage['target_coverage']}%")
    
    ri_recommendations = platform.ri_planner.recommend_reservations()
    
    if ri_recommendations:
        print("\n  Recommended Reservations:")
        print("  ┌─────────────────────────────────────────────────────────────────────┐")
        print("  │ Instance Type   │ Qty │ On-Demand   │ Reserved    │ Annual Save  │")
        print("  ├─────────────────────────────────────────────────────────────────────┤")
        
        for rec in ri_recommendations[:5]:
            inst = rec["instance_type"][:15].ljust(15)
            qty = str(rec["quantity"]).ljust(3)
            od = f"${rec['on_demand_hourly']:.3f}/hr".ljust(11)
            ri = f"${rec['reserved_hourly']:.3f}/hr".ljust(11)
            save = f"${rec['annual_savings']:,.0f}".ljust(12)
            print(f"  │ {inst} │ {qty} │ {od} │ {ri} │ {save} │")
            
        print("  └─────────────────────────────────────────────────────────────────────┘")
        
    # Record some savings
    print("\n✅ Recording Savings...")
    
    # Simulate implemented recommendations
    for rec in recommendations[:3]:
        platform.savings_tracker.record_savings(
            rec.optimization_type,
            rec.monthly_savings * 0.5,  # 50% of potential realized
            f"Implemented: {rec.title}",
            rec.recommendation_id
        )
        
    realized_savings = platform.savings_tracker.get_total_savings(30)
    savings_by_type = platform.savings_tracker.get_savings_by_type()
    
    print(f"\n  Realized Savings: ${realized_savings:,.2f}")
    
    print("\n  By Optimization Type:")
    for opt_type, savings in sorted(savings_by_type.items(),
                                     key=lambda x: x[1], reverse=True):
        print(f"    {opt_type.ljust(20)}: ${savings:,.2f}")
        
    # Platform statistics
    print("\n📊 Platform Statistics:")
    
    stats = platform.get_statistics()
    
    print(f"\n  Resources Tracked: {stats['resources']}")
    print(f"  Monthly Cost: ${stats['monthly_cost']:,.2f}")
    print(f"  Recommendations: {stats['recommendations']}")
    print(f"  Potential Savings: ${stats['potential_savings']:,.2f}/month")
    print(f"  Realized Savings: ${stats['realized_savings']:,.2f}")
    
    # ROI
    if stats['monthly_cost'] > 0:
        savings_rate = stats['potential_savings'] / stats['monthly_cost'] * 100
        print(f"  Savings Opportunity: {savings_rate:.1f}% of spend")
        
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Cost Optimization Dashboard                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Monthly Cloud Cost:           ${stats['monthly_cost']:>10,.2f}                   │")
    print(f"│ Resources Tracked:            {stats['resources']:>10}                       │")
    print(f"│ Active Recommendations:       {stats['recommendations']:>10}                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Potential Monthly Savings:    ${stats['potential_savings']:>10,.2f}                   │")
    print(f"│ Potential Annual Savings:     ${stats['potential_savings'] * 12:>10,.2f}                   │")
    print(f"│ Realized Savings (MTD):       ${stats['realized_savings']:>10,.2f}                   │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ RI Coverage:                  {coverage['coverage_percentage']:>9.1f}%                       │")
    print(f"│ Target Coverage:              {coverage['target_coverage']:>9}%                       │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Cost Optimization Platform initialized!")
    print("=" * 60)
