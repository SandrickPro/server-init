#!/usr/bin/env python3
"""
Server Init - Iteration 200: Cloud Cost Platform
Платформа облачных затрат

Функционал:
- Cost Tracking - отслеживание затрат
- Budget Management - управление бюджетами
- Cost Allocation - распределение затрат
- Resource Optimization - оптимизация ресурсов
- Anomaly Detection - обнаружение аномалий
- Forecasting - прогнозирование
- Tagging Strategy - стратегия тегирования
- Reports & Dashboards - отчёты и дашборды
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class CloudProvider(Enum):
    """Облачный провайдер"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    MULTI = "multi"


class ResourceType(Enum):
    """Тип ресурса"""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    CONTAINER = "container"
    SERVERLESS = "serverless"
    OTHER = "other"


class BudgetStatus(Enum):
    """Статус бюджета"""
    ON_TRACK = "on_track"
    WARNING = "warning"
    EXCEEDED = "exceeded"


class OptimizationType(Enum):
    """Тип оптимизации"""
    RIGHTSIZING = "rightsizing"
    RESERVED = "reserved"
    SPOT = "spot"
    UNUSED = "unused"
    SCHEDULING = "scheduling"


@dataclass
class CostRecord:
    """Запись о затратах"""
    record_id: str
    
    # Resource
    resource_id: str = ""
    resource_name: str = ""
    resource_type: ResourceType = ResourceType.COMPUTE
    
    # Provider
    provider: CloudProvider = CloudProvider.AWS
    region: str = ""
    
    # Cost
    cost: float = 0.0
    currency: str = "USD"
    
    # Time
    date: datetime = field(default_factory=datetime.now)
    usage_hours: float = 0
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class CostAllocation:
    """Распределение затрат"""
    allocation_id: str
    
    # Entity
    entity_type: str = ""  # project, team, environment
    entity_id: str = ""
    entity_name: str = ""
    
    # Cost
    total_cost: float = 0.0
    
    # Breakdown
    by_resource_type: Dict[str, float] = field(default_factory=dict)
    by_provider: Dict[str, float] = field(default_factory=dict)
    
    # Time
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)


@dataclass
class Budget:
    """Бюджет"""
    budget_id: str
    name: str = ""
    
    # Amount
    amount: float = 0.0
    currency: str = "USD"
    
    # Period
    period: str = "monthly"  # daily, weekly, monthly, yearly
    
    # Scope
    scope_type: str = ""  # project, team, tag
    scope_value: str = ""
    
    # Current
    current_spend: float = 0.0
    forecasted_spend: float = 0.0
    
    # Thresholds
    warning_threshold: float = 0.8  # 80%
    critical_threshold: float = 1.0  # 100%
    
    # State
    status: BudgetStatus = BudgetStatus.ON_TRACK
    
    # Alerts
    alert_emails: List[str] = field(default_factory=list)
    
    @property
    def utilization(self) -> float:
        if self.amount <= 0:
            return 0
        return self.current_spend / self.amount * 100


@dataclass
class OptimizationRecommendation:
    """Рекомендация по оптимизации"""
    recommendation_id: str
    
    # Type
    optimization_type: OptimizationType = OptimizationType.RIGHTSIZING
    
    # Resource
    resource_id: str = ""
    resource_name: str = ""
    
    # Savings
    estimated_monthly_savings: float = 0.0
    savings_percentage: float = 0.0
    
    # Current vs Recommended
    current_config: Dict[str, Any] = field(default_factory=dict)
    recommended_config: Dict[str, Any] = field(default_factory=dict)
    
    # Risk
    risk_level: str = "low"  # low, medium, high
    
    # Status
    status: str = "pending"  # pending, applied, dismissed
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CostAnomaly:
    """Аномалия затрат"""
    anomaly_id: str
    
    # Resource
    resource_id: str = ""
    resource_name: str = ""
    
    # Cost
    expected_cost: float = 0.0
    actual_cost: float = 0.0
    deviation_percentage: float = 0.0
    
    # Time
    detected_at: datetime = field(default_factory=datetime.now)
    
    # Status
    status: str = "new"  # new, acknowledged, resolved


@dataclass
class CostForecast:
    """Прогноз затрат"""
    forecast_id: str
    
    # Scope
    scope_type: str = ""
    scope_value: str = ""
    
    # Forecast
    forecasted_cost: float = 0.0
    confidence_level: float = 0.0
    
    # Period
    forecast_date: datetime = field(default_factory=datetime.now)
    
    # Historical
    historical_avg: float = 0.0


class CostTracker:
    """Трекер затрат"""
    
    def __init__(self):
        self.records: List[CostRecord] = []
        
    def add_record(self, record: CostRecord):
        """Добавление записи"""
        self.records.append(record)
        
    def get_total_cost(self, start: datetime = None, end: datetime = None) -> float:
        """Общие затраты"""
        total = 0
        for record in self.records:
            if start and record.date < start:
                continue
            if end and record.date > end:
                continue
            total += record.cost
        return total
        
    def get_cost_by_tag(self, tag_key: str) -> Dict[str, float]:
        """Затраты по тегу"""
        by_tag = {}
        for record in self.records:
            tag_value = record.tags.get(tag_key, "untagged")
            by_tag[tag_value] = by_tag.get(tag_value, 0) + record.cost
        return by_tag
        
    def get_cost_by_type(self) -> Dict[str, float]:
        """Затраты по типу"""
        by_type = {}
        for record in self.records:
            rtype = record.resource_type.value
            by_type[rtype] = by_type.get(rtype, 0) + record.cost
        return by_type


class BudgetManager:
    """Менеджер бюджетов"""
    
    def __init__(self, cost_tracker: CostTracker):
        self.cost_tracker = cost_tracker
        self.budgets: Dict[str, Budget] = {}
        
    def create_budget(self, name: str, amount: float, 
                     scope_type: str, scope_value: str) -> Budget:
        """Создание бюджета"""
        budget = Budget(
            budget_id=f"budget_{uuid.uuid4().hex[:8]}",
            name=name,
            amount=amount,
            scope_type=scope_type,
            scope_value=scope_value
        )
        self.budgets[budget.budget_id] = budget
        return budget
        
    def update_spend(self):
        """Обновление текущих расходов"""
        for budget in self.budgets.values():
            # Calculate current spend based on scope
            spend = 0
            for record in self.cost_tracker.records:
                if budget.scope_type == "project":
                    if record.tags.get("project") == budget.scope_value:
                        spend += record.cost
                elif budget.scope_type == "team":
                    if record.tags.get("team") == budget.scope_value:
                        spend += record.cost
                        
            budget.current_spend = spend
            
            # Update status
            utilization = budget.utilization / 100
            if utilization >= budget.critical_threshold:
                budget.status = BudgetStatus.EXCEEDED
            elif utilization >= budget.warning_threshold:
                budget.status = BudgetStatus.WARNING
            else:
                budget.status = BudgetStatus.ON_TRACK


class OptimizationEngine:
    """Движок оптимизации"""
    
    def __init__(self, cost_tracker: CostTracker):
        self.cost_tracker = cost_tracker
        self.recommendations: List[OptimizationRecommendation] = []
        
    def analyze(self):
        """Анализ и генерация рекомендаций"""
        # Group by resource
        by_resource = {}
        for record in self.cost_tracker.records:
            rid = record.resource_id
            if rid not in by_resource:
                by_resource[rid] = {
                    "name": record.resource_name,
                    "type": record.resource_type,
                    "total_cost": 0,
                    "usage_hours": 0
                }
            by_resource[rid]["total_cost"] += record.cost
            by_resource[rid]["usage_hours"] += record.usage_hours
            
        # Generate recommendations
        for rid, data in by_resource.items():
            # Rightsizing for underutilized
            if data["usage_hours"] < 100:
                self.recommendations.append(OptimizationRecommendation(
                    recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
                    optimization_type=OptimizationType.RIGHTSIZING,
                    resource_id=rid,
                    resource_name=data["name"],
                    estimated_monthly_savings=data["total_cost"] * 0.3,
                    savings_percentage=30,
                    current_config={"size": "large"},
                    recommended_config={"size": "medium"},
                    risk_level="low"
                ))
                
            # Reserved instances for consistent usage
            if data["usage_hours"] > 600 and data["total_cost"] > 100:
                self.recommendations.append(OptimizationRecommendation(
                    recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
                    optimization_type=OptimizationType.RESERVED,
                    resource_id=rid,
                    resource_name=data["name"],
                    estimated_monthly_savings=data["total_cost"] * 0.4,
                    savings_percentage=40,
                    risk_level="medium"
                ))
                
    def get_total_savings(self) -> float:
        """Общая потенциальная экономия"""
        return sum(r.estimated_monthly_savings for r in self.recommendations
                  if r.status == "pending")


class AnomalyDetector:
    """Детектор аномалий"""
    
    def __init__(self, cost_tracker: CostTracker):
        self.cost_tracker = cost_tracker
        self.anomalies: List[CostAnomaly] = []
        
    def detect(self, threshold: float = 0.5):
        """Обнаружение аномалий"""
        # Group by resource and calculate average
        by_resource = {}
        for record in self.cost_tracker.records:
            rid = record.resource_id
            if rid not in by_resource:
                by_resource[rid] = {"name": record.resource_name, "costs": []}
            by_resource[rid]["costs"].append(record.cost)
            
        # Detect anomalies
        for rid, data in by_resource.items():
            if len(data["costs"]) < 3:
                continue
                
            avg_cost = sum(data["costs"]) / len(data["costs"])
            latest_cost = data["costs"][-1]
            
            if avg_cost > 0:
                deviation = abs(latest_cost - avg_cost) / avg_cost
                
                if deviation > threshold:
                    self.anomalies.append(CostAnomaly(
                        anomaly_id=f"anomaly_{uuid.uuid4().hex[:8]}",
                        resource_id=rid,
                        resource_name=data["name"],
                        expected_cost=avg_cost,
                        actual_cost=latest_cost,
                        deviation_percentage=deviation * 100
                    ))


class CloudCostPlatform:
    """Платформа облачных затрат"""
    
    def __init__(self):
        self.cost_tracker = CostTracker()
        self.budget_manager = BudgetManager(self.cost_tracker)
        self.optimization = OptimizationEngine(self.cost_tracker)
        self.anomaly_detector = AnomalyDetector(self.cost_tracker)
        
    def add_cost_record(self, resource_id: str, resource_name: str,
                       resource_type: ResourceType, cost: float,
                       provider: CloudProvider = CloudProvider.AWS,
                       tags: Dict[str, str] = None) -> CostRecord:
        """Добавление записи о затратах"""
        record = CostRecord(
            record_id=f"cost_{uuid.uuid4().hex[:8]}",
            resource_id=resource_id,
            resource_name=resource_name,
            resource_type=resource_type,
            cost=cost,
            provider=provider,
            tags=tags or {},
            usage_hours=random.uniform(50, 700)
        )
        self.cost_tracker.add_record(record)
        return record
        
    def run_analysis(self):
        """Запуск анализа"""
        self.budget_manager.update_spend()
        self.optimization.analyze()
        self.anomaly_detector.detect()
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        return {
            "total_cost": self.cost_tracker.get_total_cost(),
            "cost_records": len(self.cost_tracker.records),
            "budgets": len(self.budget_manager.budgets),
            "recommendations": len(self.optimization.recommendations),
            "potential_savings": self.optimization.get_total_savings(),
            "anomalies": len(self.anomaly_detector.anomalies)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 200: Cloud Cost Platform")
    print("=" * 60)
    
    platform = CloudCostPlatform()
    print("✓ Cloud Cost Platform created")
    
    # Generate cost records
    print("\n💰 Generating Cost Records...")
    
    resources = [
        ("i-123abc", "web-server-1", ResourceType.COMPUTE, CloudProvider.AWS),
        ("i-456def", "web-server-2", ResourceType.COMPUTE, CloudProvider.AWS),
        ("i-789ghi", "api-server", ResourceType.COMPUTE, CloudProvider.AWS),
        ("s3-bucket-main", "main-storage", ResourceType.STORAGE, CloudProvider.AWS),
        ("rds-prod", "production-db", ResourceType.DATABASE, CloudProvider.AWS),
        ("vm-001", "azure-web", ResourceType.COMPUTE, CloudProvider.AZURE),
        ("storage-001", "azure-storage", ResourceType.STORAGE, CloudProvider.AZURE),
        ("gce-001", "gcp-compute", ResourceType.COMPUTE, CloudProvider.GCP),
        ("gcs-001", "gcp-storage", ResourceType.STORAGE, CloudProvider.GCP),
        ("eks-cluster", "k8s-cluster", ResourceType.CONTAINER, CloudProvider.AWS),
    ]
    
    projects = ["frontend", "backend", "data", "infrastructure"]
    teams = ["engineering", "data-science", "devops", "platform"]
    environments = ["production", "staging", "development"]
    
    for _ in range(50):
        rid, rname, rtype, provider = random.choice(resources)
        
        # Vary cost by resource type
        base_cost = {
            ResourceType.COMPUTE: 50,
            ResourceType.STORAGE: 20,
            ResourceType.DATABASE: 100,
            ResourceType.CONTAINER: 80,
            ResourceType.NETWORK: 15,
        }.get(rtype, 30)
        
        cost = base_cost * random.uniform(0.5, 3.0)
        
        tags = {
            "project": random.choice(projects),
            "team": random.choice(teams),
            "environment": random.choice(environments)
        }
        
        platform.add_cost_record(rid, rname, rtype, cost, provider, tags)
        
    print(f"  ✓ Generated {len(platform.cost_tracker.records)} cost records")
    
    # Create budgets
    print("\n📊 Creating Budgets...")
    
    budgets_config = [
        ("Frontend Budget", 2000, "project", "frontend"),
        ("Backend Budget", 3000, "project", "backend"),
        ("Engineering Team", 5000, "team", "engineering"),
        ("DevOps Team", 4000, "team", "devops"),
    ]
    
    for name, amount, scope_type, scope_value in budgets_config:
        budget = platform.budget_manager.create_budget(name, amount, scope_type, scope_value)
        print(f"  ✓ {name}: ${amount}")
        
    # Run analysis
    print("\n🔍 Running Analysis...")
    platform.run_analysis()
    print("  ✓ Analysis complete")
    
    # Display cost breakdown
    print("\n💵 Cost Breakdown:")
    
    cost_by_type = platform.cost_tracker.get_cost_by_type()
    total_cost = platform.cost_tracker.get_total_cost()
    
    print("\n  By Resource Type:")
    print("\n  ┌─────────────────────┬──────────────┬──────────┐")
    print("  │ Type                │ Cost         │ %        │")
    print("  ├─────────────────────┼──────────────┼──────────┤")
    
    for rtype, cost in sorted(cost_by_type.items(), key=lambda x: x[1], reverse=True):
        pct = (cost / total_cost * 100) if total_cost > 0 else 0
        type_name = rtype[:19].ljust(19)
        cost_str = f"${cost:,.2f}".rjust(12)
        pct_str = f"{pct:.1f}%".rjust(8)
        print(f"  │ {type_name} │ {cost_str} │ {pct_str} │")
        
    print("  └─────────────────────┴──────────────┴──────────┘")
    
    # Cost by project
    cost_by_project = platform.cost_tracker.get_cost_by_tag("project")
    
    print("\n  By Project:")
    print("\n  ┌─────────────────────┬──────────────┬──────────┐")
    print("  │ Project             │ Cost         │ %        │")
    print("  ├─────────────────────┼──────────────┼──────────┤")
    
    for project, cost in sorted(cost_by_project.items(), key=lambda x: x[1], reverse=True):
        pct = (cost / total_cost * 100) if total_cost > 0 else 0
        proj_name = project[:19].ljust(19)
        cost_str = f"${cost:,.2f}".rjust(12)
        pct_str = f"{pct:.1f}%".rjust(8)
        print(f"  │ {proj_name} │ {cost_str} │ {pct_str} │")
        
    print("  └─────────────────────┴──────────────┴──────────┘")
    
    # Budget status
    print("\n📈 Budget Status:")
    
    print("\n  ┌──────────────────────┬──────────────┬──────────────┬──────────┬──────────┐")
    print("  │ Budget               │ Allocated    │ Spent        │ Util %   │ Status   │")
    print("  ├──────────────────────┼──────────────┼──────────────┼──────────┼──────────┤")
    
    for budget in platform.budget_manager.budgets.values():
        name = budget.name[:20].ljust(20)
        allocated = f"${budget.amount:,.0f}".rjust(12)
        spent = f"${budget.current_spend:,.0f}".rjust(12)
        util = f"{budget.utilization:.1f}%".rjust(8)
        status = budget.status.value[:8].ljust(8)
        print(f"  │ {name} │ {allocated} │ {spent} │ {util} │ {status} │")
        
    print("  └──────────────────────┴──────────────┴──────────────┴──────────┴──────────┘")
    
    # Optimization recommendations
    print("\n💡 Optimization Recommendations:")
    
    print("\n  ┌──────────────────────┬──────────────┬──────────────┬──────────┐")
    print("  │ Resource             │ Type         │ Savings      │ Risk     │")
    print("  ├──────────────────────┼──────────────┼──────────────┼──────────┤")
    
    for rec in platform.optimization.recommendations[:8]:
        name = rec.resource_name[:20].ljust(20)
        opt_type = rec.optimization_type.value[:12].ljust(12)
        savings = f"${rec.estimated_monthly_savings:,.0f}/mo".rjust(12)
        risk = rec.risk_level[:8].ljust(8)
        print(f"  │ {name} │ {opt_type} │ {savings} │ {risk} │")
        
    print("  └──────────────────────┴──────────────┴──────────────┴──────────┘")
    
    potential_savings = platform.optimization.get_total_savings()
    print(f"\n  💰 Total Potential Savings: ${potential_savings:,.2f}/month")
    
    # Anomalies
    print("\n⚠️ Cost Anomalies:")
    
    if platform.anomaly_detector.anomalies:
        for anomaly in platform.anomaly_detector.anomalies[:5]:
            deviation_icon = "📈" if anomaly.actual_cost > anomaly.expected_cost else "📉"
            print(f"  {deviation_icon} {anomaly.resource_name}: "
                  f"${anomaly.actual_cost:.2f} (expected ${anomaly.expected_cost:.2f}, "
                  f"{anomaly.deviation_percentage:.1f}% deviation)")
    else:
        print("  ✓ No anomalies detected")
        
    # Cost by provider
    print("\n☁️ Cost by Cloud Provider:")
    
    by_provider = {}
    for record in platform.cost_tracker.records:
        p = record.provider.value
        by_provider[p] = by_provider.get(p, 0) + record.cost
        
    for provider, cost in sorted(by_provider.items(), key=lambda x: x[1], reverse=True):
        pct = (cost / total_cost * 100) if total_cost > 0 else 0
        bar = "█" * int(pct / 2) + "░" * (50 - int(pct / 2))
        print(f"  {provider.upper():6} [{bar}] ${cost:,.0f} ({pct:.1f}%)")
        
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📊 Platform Statistics:")
    
    print(f"\n  Total Cost: ${stats['total_cost']:,.2f}")
    print(f"  Cost Records: {stats['cost_records']}")
    print(f"  Budgets: {stats['budgets']}")
    print(f"  Recommendations: {stats['recommendations']}")
    print(f"  Potential Savings: ${stats['potential_savings']:,.2f}")
    print(f"  Anomalies: {stats['anomalies']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                      Cloud Cost Dashboard                          │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Spend:                    ${stats['total_cost']:>10,.2f}                   │")
    print(f"│ Cost Records:                  {stats['cost_records']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Potential Savings:              ${stats['potential_savings']:>10,.2f}                   │")
    print(f"│ Active Anomalies:              {stats['anomalies']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Cloud Cost Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
