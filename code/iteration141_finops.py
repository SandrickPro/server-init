#!/usr/bin/env python3
"""
Server Init - Iteration 141: FinOps Platform
Платформа FinOps

Функционал:
- Cloud Cost Management - управление облачными затратами
- Budget Tracking - отслеживание бюджета
- Cost Allocation - распределение затрат
- Anomaly Detection - обнаружение аномалий
- Forecasting - прогнозирование
- Showback/Chargeback - возврат/начисление затрат
- Optimization Recommendations - рекомендации по оптимизации
- RI/Savings Plans Management - управление RI/планами экономии
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


class CloudProvider(Enum):
    """Облачный провайдер"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    OCI = "oci"
    MULTI = "multi"


class CostCategory(Enum):
    """Категория затрат"""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    ANALYTICS = "analytics"
    CONTAINERS = "containers"
    SERVERLESS = "serverless"
    OTHER = "other"


class BudgetStatus(Enum):
    """Статус бюджета"""
    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    EXCEEDED = "exceeded"


class AnomalyType(Enum):
    """Тип аномалии"""
    SPIKE = "spike"
    SUSTAINED_INCREASE = "sustained_increase"
    UNUSUAL_PATTERN = "unusual_pattern"
    NEW_SERVICE = "new_service"


class RecommendationType(Enum):
    """Тип рекомендации"""
    RIGHTSIZING = "rightsizing"
    RESERVED_INSTANCE = "reserved_instance"
    SAVINGS_PLAN = "savings_plan"
    SPOT_INSTANCE = "spot_instance"
    UNUSED_RESOURCE = "unused_resource"
    STORAGE_TIER = "storage_tier"


@dataclass
class CostEntry:
    """Запись о затратах"""
    entry_id: str
    date: datetime = field(default_factory=datetime.now)
    
    # Source
    provider: CloudProvider = CloudProvider.AWS
    account_id: str = ""
    region: str = ""
    
    # Resource
    service: str = ""
    resource_id: str = ""
    resource_name: str = ""
    category: CostCategory = CostCategory.COMPUTE
    
    # Cost
    cost: float = 0.0
    currency: str = "USD"
    usage_quantity: float = 0.0
    usage_unit: str = ""
    
    # Tags
    tags: Dict = field(default_factory=dict)


@dataclass
class Budget:
    """Бюджет"""
    budget_id: str
    name: str = ""
    
    # Period
    period: str = "monthly"  # daily, weekly, monthly, quarterly, yearly
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    
    # Amount
    amount: float = 0.0
    currency: str = "USD"
    
    # Spent
    spent: float = 0.0
    forecasted: float = 0.0
    
    # Status
    status: BudgetStatus = BudgetStatus.ON_TRACK
    
    # Alerts
    alert_thresholds: List[int] = field(default_factory=lambda: [50, 80, 100])
    alerts_triggered: List[int] = field(default_factory=list)
    
    # Filters
    filters: Dict = field(default_factory=dict)  # provider, account, tags, etc.


@dataclass
class CostAllocation:
    """Распределение затрат"""
    allocation_id: str
    
    # Target
    cost_center: str = ""
    team: str = ""
    project: str = ""
    environment: str = ""
    
    # Costs
    allocated_cost: float = 0.0
    shared_cost: float = 0.0
    total_cost: float = 0.0
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)


@dataclass
class CostAnomaly:
    """Аномалия затрат"""
    anomaly_id: str
    
    # Detection
    detected_at: datetime = field(default_factory=datetime.now)
    anomaly_type: AnomalyType = AnomalyType.SPIKE
    
    # Impact
    service: str = ""
    account_id: str = ""
    expected_cost: float = 0.0
    actual_cost: float = 0.0
    impact: float = 0.0  # actual - expected
    
    # Status
    status: str = "open"  # open, investigating, resolved, false_positive
    root_cause: str = ""


@dataclass
class Recommendation:
    """Рекомендация"""
    recommendation_id: str
    
    # Type
    rec_type: RecommendationType = RecommendationType.RIGHTSIZING
    
    # Resource
    resource_id: str = ""
    resource_name: str = ""
    service: str = ""
    
    # Savings
    current_cost: float = 0.0
    recommended_cost: float = 0.0
    estimated_savings: float = 0.0
    savings_percentage: float = 0.0
    
    # Details
    description: str = ""
    action: str = ""
    
    # Status
    status: str = "open"  # open, accepted, rejected, implemented
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ReservedInstance:
    """Зарезервированный инстанс"""
    ri_id: str
    
    # Provider
    provider: CloudProvider = CloudProvider.AWS
    
    # Instance
    instance_type: str = ""
    region: str = ""
    
    # Term
    term_months: int = 12
    payment_option: str = "no_upfront"  # all_upfront, partial_upfront, no_upfront
    
    # Utilization
    quantity: int = 1
    utilization_percent: float = 0.0
    
    # Cost
    hourly_rate: float = 0.0
    total_cost: float = 0.0
    savings: float = 0.0
    
    # Dates
    start_date: datetime = field(default_factory=datetime.now)
    end_date: datetime = field(default_factory=datetime.now)


@dataclass
class SavingsPlan:
    """План экономии"""
    plan_id: str
    
    # Type
    plan_type: str = "compute"  # compute, ec2, sagemaker
    
    # Commitment
    commitment_hourly: float = 0.0
    term_months: int = 12
    
    # Utilization
    utilization_percent: float = 0.0
    
    # Savings
    on_demand_equivalent: float = 0.0
    actual_cost: float = 0.0
    net_savings: float = 0.0


class CostCollector:
    """Коллектор затрат"""
    
    def __init__(self):
        self.costs: List[CostEntry] = []
        
    def add_entry(self, provider: CloudProvider, account_id: str,
                   service: str, cost: float, category: CostCategory,
                   **kwargs) -> CostEntry:
        """Добавление записи"""
        entry = CostEntry(
            entry_id=f"cost_{uuid.uuid4().hex[:8]}",
            provider=provider,
            account_id=account_id,
            service=service,
            cost=cost,
            category=category,
            **kwargs
        )
        self.costs.append(entry)
        return entry
        
    def get_costs_by_period(self, start_date: datetime, end_date: datetime) -> List[CostEntry]:
        """Получение затрат за период"""
        return [c for c in self.costs if start_date <= c.date <= end_date]
        
    def get_costs_by_service(self, service: str) -> List[CostEntry]:
        """Получение затрат по сервису"""
        return [c for c in self.costs if c.service == service]
        
    def aggregate_by_category(self) -> Dict[str, float]:
        """Агрегация по категориям"""
        result = defaultdict(float)
        for cost in self.costs:
            result[cost.category.value] += cost.cost
        return dict(result)
        
    def aggregate_by_service(self) -> Dict[str, float]:
        """Агрегация по сервисам"""
        result = defaultdict(float)
        for cost in self.costs:
            result[cost.service] += cost.cost
        return dict(result)


class BudgetManager:
    """Менеджер бюджетов"""
    
    def __init__(self, cost_collector: CostCollector):
        self.cost_collector = cost_collector
        self.budgets: Dict[str, Budget] = {}
        
    def create(self, name: str, amount: float, period: str = "monthly",
                filters: Dict = None, **kwargs) -> Budget:
        """Создание бюджета"""
        budget = Budget(
            budget_id=f"budget_{uuid.uuid4().hex[:8]}",
            name=name,
            amount=amount,
            period=period,
            filters=filters or {},
            **kwargs
        )
        self.budgets[budget.budget_id] = budget
        return budget
        
    def update_spending(self, budget_id: str) -> Budget:
        """Обновление расходов"""
        budget = self.budgets.get(budget_id)
        if not budget:
            return None
            
        # Calculate spent based on filters
        costs = self.cost_collector.costs
        
        if budget.filters:
            if "provider" in budget.filters:
                costs = [c for c in costs if c.provider.value == budget.filters["provider"]]
            if "account_id" in budget.filters:
                costs = [c for c in costs if c.account_id == budget.filters["account_id"]]
            if "service" in budget.filters:
                costs = [c for c in costs if c.service == budget.filters["service"]]
                
        budget.spent = sum(c.cost for c in costs)
        
        # Calculate status
        usage_percent = (budget.spent / budget.amount * 100) if budget.amount > 0 else 0
        
        if usage_percent >= 100:
            budget.status = BudgetStatus.EXCEEDED
        elif usage_percent >= 80:
            budget.status = BudgetStatus.AT_RISK
        else:
            budget.status = BudgetStatus.ON_TRACK
            
        # Check alerts
        for threshold in budget.alert_thresholds:
            if usage_percent >= threshold and threshold not in budget.alerts_triggered:
                budget.alerts_triggered.append(threshold)
                
        return budget
        
    def forecast(self, budget_id: str, days_remaining: int = 15) -> float:
        """Прогноз расходов"""
        budget = self.budgets.get(budget_id)
        if not budget:
            return 0.0
            
        # Simple linear forecast
        days_passed = 15  # Assume mid-month
        daily_rate = budget.spent / days_passed if days_passed > 0 else 0
        budget.forecasted = budget.spent + (daily_rate * days_remaining)
        
        return budget.forecasted


class AllocationEngine:
    """Движок распределения затрат"""
    
    def __init__(self, cost_collector: CostCollector):
        self.cost_collector = cost_collector
        self.allocations: List[CostAllocation] = []
        
    def allocate_by_tags(self, tag_key: str) -> Dict[str, CostAllocation]:
        """Распределение по тегам"""
        allocations = {}
        
        for cost in self.cost_collector.costs:
            tag_value = cost.tags.get(tag_key, "untagged")
            
            if tag_value not in allocations:
                allocations[tag_value] = CostAllocation(
                    allocation_id=f"alloc_{uuid.uuid4().hex[:8]}",
                    **{tag_key: tag_value}
                )
                
            allocations[tag_value].allocated_cost += cost.cost
            allocations[tag_value].total_cost += cost.cost
            
        self.allocations.extend(allocations.values())
        return allocations
        
    def showback_report(self, group_by: str = "team") -> List[Dict]:
        """Отчёт showback"""
        grouped = defaultdict(float)
        
        for cost in self.cost_collector.costs:
            key = cost.tags.get(group_by, "unallocated")
            grouped[key] += cost.cost
            
        total = sum(grouped.values())
        
        return [
            {
                "group": k,
                "cost": round(v, 2),
                "percentage": round(v / total * 100, 2) if total > 0 else 0
            }
            for k, v in sorted(grouped.items(), key=lambda x: x[1], reverse=True)
        ]


class AnomalyDetector:
    """Детектор аномалий"""
    
    def __init__(self, cost_collector: CostCollector):
        self.cost_collector = cost_collector
        self.anomalies: List[CostAnomaly] = []
        self.baselines: Dict[str, float] = {}
        
    def set_baseline(self, service: str, expected_daily_cost: float):
        """Установка базовой линии"""
        self.baselines[service] = expected_daily_cost
        
    def detect(self, threshold_percent: float = 50) -> List[CostAnomaly]:
        """Обнаружение аномалий"""
        detected = []
        
        # Group costs by service
        by_service = defaultdict(float)
        for cost in self.cost_collector.costs:
            by_service[cost.service] += cost.cost
            
        for service, actual in by_service.items():
            expected = self.baselines.get(service, actual * 0.8)  # Default: 80% of actual
            
            if expected > 0:
                deviation = (actual - expected) / expected * 100
                
                if deviation > threshold_percent:
                    anomaly = CostAnomaly(
                        anomaly_id=f"anomaly_{uuid.uuid4().hex[:8]}",
                        anomaly_type=AnomalyType.SPIKE if deviation > 100 else AnomalyType.SUSTAINED_INCREASE,
                        service=service,
                        expected_cost=expected,
                        actual_cost=actual,
                        impact=actual - expected
                    )
                    self.anomalies.append(anomaly)
                    detected.append(anomaly)
                    
        return detected


class RecommendationEngine:
    """Движок рекомендаций"""
    
    def __init__(self, cost_collector: CostCollector):
        self.cost_collector = cost_collector
        self.recommendations: List[Recommendation] = []
        
    def analyze_rightsizing(self) -> List[Recommendation]:
        """Анализ rightsizing"""
        recs = []
        
        # Simulate analysis
        compute_costs = [c for c in self.cost_collector.costs if c.category == CostCategory.COMPUTE]
        
        for cost in compute_costs[:5]:  # Top 5
            savings_percent = random.uniform(10, 40)
            savings = cost.cost * savings_percent / 100
            
            rec = Recommendation(
                recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
                rec_type=RecommendationType.RIGHTSIZING,
                resource_id=cost.resource_id,
                resource_name=cost.resource_name,
                service=cost.service,
                current_cost=cost.cost,
                recommended_cost=cost.cost - savings,
                estimated_savings=savings,
                savings_percentage=savings_percent,
                description=f"Downsize instance based on utilization",
                action=f"Change to smaller instance type"
            )
            recs.append(rec)
            
        self.recommendations.extend(recs)
        return recs
        
    def analyze_unused_resources(self) -> List[Recommendation]:
        """Анализ неиспользуемых ресурсов"""
        recs = []
        
        # Simulate finding unused resources
        services = ["EBS Volumes", "Elastic IPs", "Load Balancers", "RDS Snapshots"]
        
        for service in services:
            cost = random.uniform(50, 500)
            
            rec = Recommendation(
                recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
                rec_type=RecommendationType.UNUSED_RESOURCE,
                service=service,
                current_cost=cost,
                recommended_cost=0,
                estimated_savings=cost,
                savings_percentage=100,
                description=f"Unused {service} detected",
                action=f"Delete unused {service}"
            )
            recs.append(rec)
            
        self.recommendations.extend(recs)
        return recs
        
    def get_total_savings(self) -> float:
        """Общая потенциальная экономия"""
        return sum(r.estimated_savings for r in self.recommendations if r.status == "open")


class RIManager:
    """Менеджер Reserved Instances"""
    
    def __init__(self):
        self.reserved_instances: List[ReservedInstance] = []
        self.savings_plans: List[SavingsPlan] = []
        
    def add_ri(self, instance_type: str, region: str, term_months: int = 12,
                quantity: int = 1, **kwargs) -> ReservedInstance:
        """Добавление RI"""
        ri = ReservedInstance(
            ri_id=f"ri_{uuid.uuid4().hex[:8]}",
            instance_type=instance_type,
            region=region,
            term_months=term_months,
            quantity=quantity,
            **kwargs
        )
        self.reserved_instances.append(ri)
        return ri
        
    def add_savings_plan(self, plan_type: str, commitment_hourly: float,
                          term_months: int = 12) -> SavingsPlan:
        """Добавление плана экономии"""
        plan = SavingsPlan(
            plan_id=f"sp_{uuid.uuid4().hex[:8]}",
            plan_type=plan_type,
            commitment_hourly=commitment_hourly,
            term_months=term_months
        )
        self.savings_plans.append(plan)
        return plan
        
    def calculate_utilization(self) -> Dict:
        """Расчёт утилизации"""
        ri_util = sum(ri.utilization_percent for ri in self.reserved_instances) / len(self.reserved_instances) if self.reserved_instances else 0
        sp_util = sum(sp.utilization_percent for sp in self.savings_plans) / len(self.savings_plans) if self.savings_plans else 0
        
        return {
            "ri_utilization": ri_util,
            "sp_utilization": sp_util,
            "ri_count": len(self.reserved_instances),
            "sp_count": len(self.savings_plans)
        }


class Forecaster:
    """Прогнозирование"""
    
    def __init__(self, cost_collector: CostCollector):
        self.cost_collector = cost_collector
        
    def forecast_monthly(self, months_ahead: int = 3) -> List[Dict]:
        """Месячный прогноз"""
        # Get current month total
        current_total = sum(c.cost for c in self.cost_collector.costs)
        
        forecasts = []
        growth_rate = 0.05  # 5% monthly growth assumption
        
        for i in range(1, months_ahead + 1):
            forecasted = current_total * ((1 + growth_rate) ** i)
            forecasts.append({
                "month": i,
                "forecasted_cost": round(forecasted, 2),
                "growth_rate": growth_rate * 100
            })
            
        return forecasts
        
    def forecast_by_service(self, service: str, days_ahead: int = 30) -> float:
        """Прогноз по сервису"""
        service_costs = [c for c in self.cost_collector.costs if c.service == service]
        
        if not service_costs:
            return 0.0
            
        daily_avg = sum(c.cost for c in service_costs) / max(1, len(service_costs))
        return daily_avg * days_ahead


class FinOpsPlatform:
    """Платформа FinOps"""
    
    def __init__(self):
        self.cost_collector = CostCollector()
        self.budget_manager = BudgetManager(self.cost_collector)
        self.allocation_engine = AllocationEngine(self.cost_collector)
        self.anomaly_detector = AnomalyDetector(self.cost_collector)
        self.recommendation_engine = RecommendationEngine(self.cost_collector)
        self.ri_manager = RIManager()
        self.forecaster = Forecaster(self.cost_collector)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        return {
            "total_cost": sum(c.cost for c in self.cost_collector.costs),
            "cost_entries": len(self.cost_collector.costs),
            "budgets": len(self.budget_manager.budgets),
            "anomalies": len(self.anomaly_detector.anomalies),
            "recommendations": len(self.recommendation_engine.recommendations),
            "potential_savings": self.recommendation_engine.get_total_savings(),
            "reserved_instances": len(self.ri_manager.reserved_instances),
            "savings_plans": len(self.ri_manager.savings_plans)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 141: FinOps Platform")
    print("=" * 60)
    
    async def demo():
        platform = FinOpsPlatform()
        print("✓ FinOps Platform created")
        
        # Add cost entries
        print("\n💰 Collecting Cost Data...")
        
        cost_data = [
            (CloudProvider.AWS, "123456789", "EC2", 15000, CostCategory.COMPUTE, {"team": "platform", "environment": "production"}),
            (CloudProvider.AWS, "123456789", "RDS", 8000, CostCategory.DATABASE, {"team": "platform", "environment": "production"}),
            (CloudProvider.AWS, "123456789", "S3", 3000, CostCategory.STORAGE, {"team": "data", "environment": "production"}),
            (CloudProvider.AWS, "123456789", "Lambda", 2000, CostCategory.SERVERLESS, {"team": "backend", "environment": "production"}),
            (CloudProvider.AWS, "123456789", "EKS", 5000, CostCategory.CONTAINERS, {"team": "platform", "environment": "production"}),
            (CloudProvider.AWS, "987654321", "EC2", 8000, CostCategory.COMPUTE, {"team": "frontend", "environment": "staging"}),
            (CloudProvider.AZURE, "azure-sub-1", "Virtual Machines", 10000, CostCategory.COMPUTE, {"team": "legacy", "environment": "production"}),
            (CloudProvider.GCP, "gcp-proj-1", "Compute Engine", 6000, CostCategory.COMPUTE, {"team": "ml", "environment": "development"}),
            (CloudProvider.GCP, "gcp-proj-1", "BigQuery", 4000, CostCategory.ANALYTICS, {"team": "data", "environment": "production"}),
            (CloudProvider.AWS, "123456789", "CloudFront", 1500, CostCategory.NETWORK, {"team": "frontend", "environment": "production"})
        ]
        
        for provider, account, service, cost, category, tags in cost_data:
            platform.cost_collector.add_entry(
                provider, account, service, cost, category,
                resource_id=f"res_{uuid.uuid4().hex[:6]}",
                resource_name=f"{service}-resource",
                tags=tags
            )
            
        total = sum(c.cost for c in platform.cost_collector.costs)
        print(f"  ✓ Collected {len(platform.cost_collector.costs)} cost entries")
        print(f"  ✓ Total cost: ${total:,.2f}")
        
        # Cost breakdown
        print("\n📊 Cost Breakdown by Category:")
        
        by_category = platform.cost_collector.aggregate_by_category()
        for category, cost in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
            percent = cost / total * 100
            bar = "█" * int(percent / 5)
            print(f"  {category:15s} ${cost:>10,.2f} ({percent:5.1f}%) {bar}")
            
        print("\n📊 Cost Breakdown by Service:")
        
        by_service = platform.cost_collector.aggregate_by_service()
        for service, cost in sorted(by_service.items(), key=lambda x: x[1], reverse=True)[:5]:
            percent = cost / total * 100
            print(f"  {service:20s} ${cost:>10,.2f} ({percent:5.1f}%)")
            
        # Create budgets
        print("\n📋 Creating Budgets...")
        
        budgets = [
            ("AWS Total", 45000, {"provider": "aws"}),
            ("Production Compute", 25000, {"service": "EC2"}),
            ("Data Team", 10000, None)
        ]
        
        created_budgets = []
        for name, amount, filters in budgets:
            budget = platform.budget_manager.create(name, amount, filters=filters)
            platform.budget_manager.update_spending(budget.budget_id)
            created_budgets.append(budget)
            
            status_icon = {"on_track": "🟢", "at_risk": "🟡", "exceeded": "🔴"}[budget.status.value]
            print(f"  {status_icon} {name}: ${budget.spent:,.2f} / ${budget.amount:,.2f} ({budget.spent/budget.amount*100:.1f}%)")
            
        # Forecast
        print("\n🔮 Budget Forecasts:")
        
        for budget in created_budgets:
            forecast = platform.budget_manager.forecast(budget.budget_id)
            status = "⚠️ Over budget" if forecast > budget.amount else "✓"
            print(f"  {budget.name}: Forecasted ${forecast:,.2f} {status}")
            
        # Cost allocation
        print("\n👥 Cost Allocation by Team:")
        
        showback = platform.allocation_engine.showback_report("team")
        for item in showback:
            bar = "█" * int(item["percentage"] / 5)
            print(f"  {item['group']:15s} ${item['cost']:>10,.2f} ({item['percentage']:5.1f}%) {bar}")
            
        # Anomaly detection
        print("\n🚨 Anomaly Detection...")
        
        # Set baselines
        for service, cost in by_service.items():
            platform.anomaly_detector.set_baseline(service, cost * 0.7)  # 70% of actual as baseline
            
        anomalies = platform.anomaly_detector.detect(threshold_percent=30)
        
        print(f"  Detected {len(anomalies)} anomalies:")
        for anomaly in anomalies[:3]:
            print(f"  🔴 {anomaly.service}: Expected ${anomaly.expected_cost:,.2f}, Actual ${anomaly.actual_cost:,.2f}")
            print(f"      Impact: +${anomaly.impact:,.2f} ({anomaly.anomaly_type.value})")
            
        # Recommendations
        print("\n💡 Optimization Recommendations...")
        
        rightsizing_recs = platform.recommendation_engine.analyze_rightsizing()
        unused_recs = platform.recommendation_engine.analyze_unused_resources()
        
        print(f"\n  Rightsizing Opportunities ({len(rightsizing_recs)}):")
        for rec in rightsizing_recs[:3]:
            print(f"    • {rec.service}: Save ${rec.estimated_savings:,.2f}/mo ({rec.savings_percentage:.1f}%)")
            
        print(f"\n  Unused Resources ({len(unused_recs)}):")
        for rec in unused_recs[:3]:
            print(f"    • {rec.service}: Save ${rec.estimated_savings:,.2f}/mo")
            
        total_savings = platform.recommendation_engine.get_total_savings()
        print(f"\n  💰 Total Potential Savings: ${total_savings:,.2f}/mo")
        
        # RI/Savings Plans
        print("\n📦 Reserved Instances & Savings Plans...")
        
        # Add RIs
        ri1 = platform.ri_manager.add_ri("m5.xlarge", "us-east-1", 12, 10, utilization_percent=85)
        ri2 = platform.ri_manager.add_ri("r5.2xlarge", "us-west-2", 36, 5, utilization_percent=72)
        
        # Add Savings Plans
        sp1 = platform.ri_manager.add_savings_plan("compute", 50, 12)
        sp1.utilization_percent = 92
        
        util = platform.ri_manager.calculate_utilization()
        print(f"  Reserved Instances: {util['ri_count']} (Avg Utilization: {util['ri_utilization']:.1f}%)")
        print(f"  Savings Plans: {util['sp_count']} (Avg Utilization: {util['sp_utilization']:.1f}%)")
        
        # Forecasting
        print("\n📈 Cost Forecasting...")
        
        monthly_forecast = platform.forecaster.forecast_monthly(3)
        print("  Monthly Forecast:")
        for forecast in monthly_forecast:
            print(f"    Month +{forecast['month']}: ${forecast['forecasted_cost']:,.2f} (+{forecast['growth_rate']:.1f}%)")
            
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Cost: ${stats['total_cost']:,.2f}")
        print(f"  Cost Entries: {stats['cost_entries']}")
        print(f"  Budgets: {stats['budgets']}")
        print(f"  Anomalies Detected: {stats['anomalies']}")
        print(f"  Recommendations: {stats['recommendations']}")
        print(f"  Potential Savings: ${stats['potential_savings']:,.2f}")
        print(f"  Reserved Instances: {stats['reserved_instances']}")
        print(f"  Savings Plans: {stats['savings_plans']}")
        
        # Dashboard
        print("\n📋 FinOps Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │                    FinOps Overview                          │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Cloud Cost:  ${stats['total_cost']:>12,.2f}                   │")
        print(f"  │ Cost Entries:      {stats['cost_entries']:>13}                   │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Budgets:           {stats['budgets']:>13}                   │")
        print(f"  │ Anomalies:         {stats['anomalies']:>13}                   │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Recommendations:   {stats['recommendations']:>13}                   │")
        print(f"  │ Potential Savings: ${stats['potential_savings']:>12,.2f}                   │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Reserved Instances:{stats['reserved_instances']:>13}                   │")
        print(f"  │ Savings Plans:     {stats['savings_plans']:>13}                   │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("FinOps Platform initialized!")
    print("=" * 60)
