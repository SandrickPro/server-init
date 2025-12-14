#!/usr/bin/env python3
"""
Server Init - Iteration 132: Cost Optimization Platform
Платформа оптимизации затрат

Функционал:
- Cost Tracking - отслеживание затрат
- Resource Right-sizing - оптимизация размеров ресурсов
- Reserved Instance Analysis - анализ зарезервированных инстансов
- Spot Instance Management - управление spot-инстансами
- Budget Alerts - бюджетные алерты
- Cost Allocation - распределение затрат
- Savings Recommendations - рекомендации по экономии
- Cloud Cost Comparison - сравнение затрат облаков
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from collections import defaultdict
import uuid
import random


class ResourceType(Enum):
    """Тип ресурса"""
    COMPUTE = "compute"
    STORAGE = "storage"
    DATABASE = "database"
    NETWORK = "network"
    CONTAINER = "container"
    SERVERLESS = "serverless"


class CloudProvider(Enum):
    """Облачный провайдер"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    ON_PREMISE = "on_premise"


class PricingModel(Enum):
    """Модель ценообразования"""
    ON_DEMAND = "on_demand"
    RESERVED_1Y = "reserved_1y"
    RESERVED_3Y = "reserved_3y"
    SPOT = "spot"
    SAVINGS_PLAN = "savings_plan"


class AlertSeverity(Enum):
    """Критичность алерта"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class CloudResource:
    """Облачный ресурс"""
    resource_id: str
    name: str = ""
    
    # Type
    resource_type: ResourceType = ResourceType.COMPUTE
    provider: CloudProvider = CloudProvider.AWS
    
    # Specs
    instance_type: str = ""
    region: str = ""
    
    # Pricing
    pricing_model: PricingModel = PricingModel.ON_DEMAND
    hourly_cost: float = 0.0
    
    # Usage
    avg_cpu_utilization: float = 0.0
    avg_memory_utilization: float = 0.0
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CostRecord:
    """Запись о затратах"""
    record_id: str
    resource_id: str = ""
    
    # Period
    date: datetime = field(default_factory=datetime.now)
    
    # Costs
    compute_cost: float = 0.0
    storage_cost: float = 0.0
    network_cost: float = 0.0
    other_cost: float = 0.0
    
    @property
    def total_cost(self) -> float:
        return self.compute_cost + self.storage_cost + self.network_cost + self.other_cost


@dataclass
class Budget:
    """Бюджет"""
    budget_id: str
    name: str = ""
    
    # Scope
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Amount
    monthly_budget: float = 0.0
    current_spend: float = 0.0
    forecasted_spend: float = 0.0
    
    # Thresholds
    warning_threshold: float = 0.8  # 80%
    critical_threshold: float = 0.95  # 95%
    
    # Status
    exceeded: bool = False


@dataclass
class RightsizingRecommendation:
    """Рекомендация по оптимизации размера"""
    recommendation_id: str
    resource_id: str = ""
    
    # Current
    current_type: str = ""
    current_cost: float = 0.0
    
    # Recommended
    recommended_type: str = ""
    recommended_cost: float = 0.0
    
    # Savings
    monthly_savings: float = 0.0
    annual_savings: float = 0.0
    
    # Reason
    reason: str = ""
    
    # Status
    implemented: bool = False


@dataclass
class ReservedInstanceAnalysis:
    """Анализ зарезервированных инстансов"""
    analysis_id: str
    
    # Current state
    current_ri_coverage: float = 0.0
    on_demand_spend: float = 0.0
    
    # Recommendation
    recommended_ri_coverage: float = 0.0
    break_even_months: int = 0
    
    # Savings
    monthly_savings: float = 0.0
    total_savings_3y: float = 0.0


@dataclass
class SpotInstance:
    """Spot инстанс"""
    spot_id: str
    resource_id: str = ""
    
    # Pricing
    on_demand_price: float = 0.0
    spot_price: float = 0.0
    savings_percent: float = 0.0
    
    # Status
    active: bool = True
    interruption_count: int = 0
    
    # Availability
    availability_zone: str = ""
    instance_type: str = ""


class CostTracker:
    """Трекер затрат"""
    
    def __init__(self):
        self.resources: Dict[str, CloudResource] = {}
        self.cost_records: List[CostRecord] = []
        
    def add_resource(self, name: str, resource_type: ResourceType,
                      provider: CloudProvider = CloudProvider.AWS,
                      instance_type: str = "", hourly_cost: float = 0.0,
                      **kwargs) -> CloudResource:
        """Добавление ресурса"""
        resource = CloudResource(
            resource_id=f"res_{uuid.uuid4().hex[:8]}",
            name=name,
            resource_type=resource_type,
            provider=provider,
            instance_type=instance_type,
            hourly_cost=hourly_cost,
            **kwargs
        )
        self.resources[resource.resource_id] = resource
        return resource
        
    def record_cost(self, resource_id: str, compute: float = 0.0,
                     storage: float = 0.0, network: float = 0.0,
                     other: float = 0.0) -> CostRecord:
        """Запись затрат"""
        record = CostRecord(
            record_id=f"cost_{uuid.uuid4().hex[:8]}",
            resource_id=resource_id,
            compute_cost=compute,
            storage_cost=storage,
            network_cost=network,
            other_cost=other
        )
        self.cost_records.append(record)
        return record
        
    def get_total_cost(self, days: int = 30) -> Dict[str, float]:
        """Получить общие затраты"""
        threshold = datetime.now() - timedelta(days=days)
        recent = [r for r in self.cost_records if r.date >= threshold]
        
        return {
            "compute": sum(r.compute_cost for r in recent),
            "storage": sum(r.storage_cost for r in recent),
            "network": sum(r.network_cost for r in recent),
            "other": sum(r.other_cost for r in recent),
            "total": sum(r.total_cost for r in recent)
        }
        
    def get_cost_by_tag(self, tag_key: str) -> Dict[str, float]:
        """Затраты по тегу"""
        costs_by_tag = defaultdict(float)
        
        for record in self.cost_records:
            resource = self.resources.get(record.resource_id)
            if resource:
                tag_value = resource.tags.get(tag_key, "untagged")
                costs_by_tag[tag_value] += record.total_cost
                
        return dict(costs_by_tag)


class BudgetManager:
    """Менеджер бюджетов"""
    
    def __init__(self, cost_tracker: CostTracker):
        self.cost_tracker = cost_tracker
        self.budgets: Dict[str, Budget] = {}
        self.alerts: List[Dict] = []
        
    def create(self, name: str, monthly_budget: float,
                tags: Dict[str, str] = None, **kwargs) -> Budget:
        """Создание бюджета"""
        budget = Budget(
            budget_id=f"budget_{uuid.uuid4().hex[:8]}",
            name=name,
            monthly_budget=monthly_budget,
            tags=tags or {},
            **kwargs
        )
        self.budgets[budget.budget_id] = budget
        return budget
        
    def update_spend(self, budget_id: str) -> Dict:
        """Обновление расходов"""
        budget = self.budgets.get(budget_id)
        if not budget:
            return {"error": "Budget not found"}
            
        # Calculate spend for tagged resources
        total_spend = 0.0
        
        for record in self.cost_tracker.cost_records:
            resource = self.cost_tracker.resources.get(record.resource_id)
            if resource:
                # Check if resource matches budget tags
                matches = all(
                    resource.tags.get(k) == v
                    for k, v in budget.tags.items()
                )
                if matches or not budget.tags:
                    total_spend += record.total_cost
                    
        budget.current_spend = total_spend
        budget.forecasted_spend = total_spend * 1.2  # Simple forecast
        
        # Check thresholds
        utilization = budget.current_spend / budget.monthly_budget if budget.monthly_budget > 0 else 0
        
        if utilization >= budget.critical_threshold:
            budget.exceeded = True
            self._create_alert(budget, AlertSeverity.CRITICAL, utilization)
        elif utilization >= budget.warning_threshold:
            self._create_alert(budget, AlertSeverity.WARNING, utilization)
            
        return {
            "budget_id": budget_id,
            "current_spend": budget.current_spend,
            "utilization": utilization * 100,
            "exceeded": budget.exceeded
        }
        
    def _create_alert(self, budget: Budget, severity: AlertSeverity, utilization: float):
        """Создание алерта"""
        self.alerts.append({
            "budget_id": budget.budget_id,
            "budget_name": budget.name,
            "severity": severity.value,
            "utilization": utilization * 100,
            "timestamp": datetime.now()
        })


class RightsizingAnalyzer:
    """Анализатор оптимизации размеров"""
    
    def __init__(self, cost_tracker: CostTracker):
        self.cost_tracker = cost_tracker
        self.recommendations: Dict[str, RightsizingRecommendation] = {}
        
        # Instance type pricing (simplified)
        self.instance_pricing = {
            "t3.micro": 0.0104,
            "t3.small": 0.0208,
            "t3.medium": 0.0416,
            "t3.large": 0.0832,
            "t3.xlarge": 0.1664,
            "m5.large": 0.096,
            "m5.xlarge": 0.192,
            "m5.2xlarge": 0.384,
            "c5.large": 0.085,
            "c5.xlarge": 0.170,
            "r5.large": 0.126,
            "r5.xlarge": 0.252
        }
        
    def analyze(self, resource_id: str) -> Optional[RightsizingRecommendation]:
        """Анализ ресурса"""
        resource = self.cost_tracker.resources.get(resource_id)
        if not resource or resource.resource_type != ResourceType.COMPUTE:
            return None
            
        # Check utilization
        if resource.avg_cpu_utilization < 20 and resource.avg_memory_utilization < 20:
            # Recommend downsizing
            current_type = resource.instance_type
            
            # Find smaller instance
            smaller_types = {
                "t3.xlarge": "t3.large",
                "t3.large": "t3.medium",
                "t3.medium": "t3.small",
                "t3.small": "t3.micro",
                "m5.2xlarge": "m5.xlarge",
                "m5.xlarge": "m5.large",
                "c5.xlarge": "c5.large",
                "r5.xlarge": "r5.large"
            }
            
            recommended = smaller_types.get(current_type)
            if recommended:
                current_cost = self.instance_pricing.get(current_type, 0) * 730  # Monthly
                recommended_cost = self.instance_pricing.get(recommended, 0) * 730
                
                rec = RightsizingRecommendation(
                    recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
                    resource_id=resource_id,
                    current_type=current_type,
                    current_cost=current_cost,
                    recommended_type=recommended,
                    recommended_cost=recommended_cost,
                    monthly_savings=current_cost - recommended_cost,
                    annual_savings=(current_cost - recommended_cost) * 12,
                    reason=f"Low utilization: CPU {resource.avg_cpu_utilization:.0f}%, Memory {resource.avg_memory_utilization:.0f}%"
                )
                self.recommendations[rec.recommendation_id] = rec
                return rec
                
        return None
        
    def analyze_all(self) -> List[RightsizingRecommendation]:
        """Анализ всех ресурсов"""
        recommendations = []
        
        for resource_id in self.cost_tracker.resources:
            rec = self.analyze(resource_id)
            if rec:
                recommendations.append(rec)
                
        return recommendations


class ReservedInstanceOptimizer:
    """Оптимизатор зарезервированных инстансов"""
    
    def __init__(self, cost_tracker: CostTracker):
        self.cost_tracker = cost_tracker
        self.analyses: Dict[str, ReservedInstanceAnalysis] = {}
        
    def analyze(self) -> ReservedInstanceAnalysis:
        """Анализ возможностей RI"""
        # Calculate current state
        resources = [r for r in self.cost_tracker.resources.values() 
                    if r.resource_type == ResourceType.COMPUTE]
        
        on_demand_resources = [r for r in resources 
                               if r.pricing_model == PricingModel.ON_DEMAND]
        reserved_resources = [r for r in resources 
                              if r.pricing_model in [PricingModel.RESERVED_1Y, PricingModel.RESERVED_3Y]]
        
        total_resources = len(resources)
        ri_coverage = len(reserved_resources) / total_resources * 100 if total_resources > 0 else 0
        
        on_demand_spend = sum(r.hourly_cost * 730 for r in on_demand_resources)
        
        # Calculate potential savings (30% for 1-year RI, 50% for 3-year)
        potential_savings = on_demand_spend * 0.4  # Average savings
        
        analysis = ReservedInstanceAnalysis(
            analysis_id=f"ri_{uuid.uuid4().hex[:8]}",
            current_ri_coverage=ri_coverage,
            on_demand_spend=on_demand_spend,
            recommended_ri_coverage=80.0,  # Target 80% coverage
            break_even_months=8,
            monthly_savings=potential_savings,
            total_savings_3y=potential_savings * 36
        )
        
        self.analyses[analysis.analysis_id] = analysis
        return analysis


class SpotInstanceManager:
    """Менеджер spot-инстансов"""
    
    def __init__(self):
        self.spot_instances: Dict[str, SpotInstance] = {}
        
    def create(self, resource_id: str, instance_type: str,
                on_demand_price: float, spot_price: float,
                availability_zone: str = "") -> SpotInstance:
        """Создание spot-инстанса"""
        savings = (on_demand_price - spot_price) / on_demand_price * 100 if on_demand_price > 0 else 0
        
        spot = SpotInstance(
            spot_id=f"spot_{uuid.uuid4().hex[:8]}",
            resource_id=resource_id,
            on_demand_price=on_demand_price,
            spot_price=spot_price,
            savings_percent=savings,
            instance_type=instance_type,
            availability_zone=availability_zone
        )
        self.spot_instances[spot.spot_id] = spot
        return spot
        
    def get_savings(self) -> Dict[str, float]:
        """Получить экономию от spot"""
        active = [s for s in self.spot_instances.values() if s.active]
        
        total_on_demand = sum(s.on_demand_price * 730 for s in active)
        total_spot = sum(s.spot_price * 730 for s in active)
        
        return {
            "on_demand_cost": total_on_demand,
            "spot_cost": total_spot,
            "monthly_savings": total_on_demand - total_spot,
            "savings_percent": ((total_on_demand - total_spot) / total_on_demand * 100) if total_on_demand > 0 else 0
        }


class CostOptimizationPlatform:
    """Платформа оптимизации затрат"""
    
    def __init__(self):
        self.cost_tracker = CostTracker()
        self.budget_manager = BudgetManager(self.cost_tracker)
        self.rightsizing = RightsizingAnalyzer(self.cost_tracker)
        self.ri_optimizer = ReservedInstanceOptimizer(self.cost_tracker)
        self.spot_manager = SpotInstanceManager()
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        costs = self.cost_tracker.get_total_cost(30)
        spot_savings = self.spot_manager.get_savings()
        
        return {
            "total_resources": len(self.cost_tracker.resources),
            "monthly_cost": costs["total"],
            "budgets": len(self.budget_manager.budgets),
            "budget_alerts": len(self.budget_manager.alerts),
            "recommendations": len(self.rightsizing.recommendations),
            "spot_instances": len(self.spot_manager.spot_instances),
            "spot_savings": spot_savings["monthly_savings"]
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 132: Cost Optimization Platform")
    print("=" * 60)
    
    async def demo():
        platform = CostOptimizationPlatform()
        print("✓ Cost Optimization Platform created")
        
        # Add resources
        print("\n☁️ Adding Cloud Resources...")
        
        resources_data = [
            ("web-server-1", ResourceType.COMPUTE, "t3.xlarge", 0.1664, {"team": "web", "env": "prod"}),
            ("web-server-2", ResourceType.COMPUTE, "t3.large", 0.0832, {"team": "web", "env": "prod"}),
            ("api-server-1", ResourceType.COMPUTE, "m5.xlarge", 0.192, {"team": "api", "env": "prod"}),
            ("api-server-2", ResourceType.COMPUTE, "m5.large", 0.096, {"team": "api", "env": "prod"}),
            ("db-primary", ResourceType.DATABASE, "r5.xlarge", 0.252, {"team": "data", "env": "prod"}),
            ("cache-server", ResourceType.COMPUTE, "r5.large", 0.126, {"team": "data", "env": "prod"}),
            ("dev-server", ResourceType.COMPUTE, "t3.medium", 0.0416, {"team": "dev", "env": "dev"}),
            ("staging-server", ResourceType.COMPUTE, "t3.large", 0.0832, {"team": "dev", "env": "staging"})
        ]
        
        created_resources = []
        for name, res_type, instance, cost, tags in resources_data:
            resource = platform.cost_tracker.add_resource(
                name, res_type,
                instance_type=instance,
                hourly_cost=cost,
                tags=tags,
                avg_cpu_utilization=random.uniform(10, 80),
                avg_memory_utilization=random.uniform(15, 70)
            )
            created_resources.append(resource)
            print(f"  ✓ {name} ({instance}): ${cost:.4f}/hr")
            
        # Record costs
        print("\n💰 Recording Daily Costs...")
        
        for resource in created_resources:
            daily_cost = resource.hourly_cost * 24
            
            # Simulate 30 days of costs
            for day in range(30):
                variation = random.uniform(0.9, 1.1)
                platform.cost_tracker.record_cost(
                    resource.resource_id,
                    compute=daily_cost * variation * 0.7,
                    storage=daily_cost * variation * 0.15,
                    network=daily_cost * variation * 0.10,
                    other=daily_cost * variation * 0.05
                )
                
        costs = platform.cost_tracker.get_total_cost(30)
        
        print(f"  Total (30 days): ${costs['total']:.2f}")
        print(f"    Compute: ${costs['compute']:.2f}")
        print(f"    Storage: ${costs['storage']:.2f}")
        print(f"    Network: ${costs['network']:.2f}")
        
        # Cost by team
        print("\n👥 Cost Allocation by Team:")
        
        team_costs = platform.cost_tracker.get_cost_by_tag("team")
        
        for team, cost in sorted(team_costs.items(), key=lambda x: -x[1]):
            bar = "█" * int(cost / 100)
            print(f"  {team}: ${cost:.2f} {bar}")
            
        # Create budgets
        print("\n📊 Creating Budgets...")
        
        budgets_data = [
            ("Production Budget", 5000, {"env": "prod"}),
            ("Development Budget", 1000, {"env": "dev"}),
            ("API Team Budget", 2000, {"team": "api"})
        ]
        
        created_budgets = []
        for name, amount, tags in budgets_data:
            budget = platform.budget_manager.create(name, amount, tags)
            created_budgets.append(budget)
            print(f"  ✓ {name}: ${amount}/month")
            
        # Update spend
        print("\n💵 Updating Budget Spend...")
        
        for budget in created_budgets:
            result = platform.budget_manager.update_spend(budget.budget_id)
            
            utilization = result.get("utilization", 0)
            icon = "🟢" if utilization < 80 else "🟡" if utilization < 95 else "🔴"
            
            print(f"  {icon} {budget.name}")
            print(f"     Spend: ${result['current_spend']:.2f} / ${budget.monthly_budget:.2f}")
            print(f"     Utilization: {utilization:.1f}%")
            
        # Budget alerts
        if platform.budget_manager.alerts:
            print(f"\n  ⚠️ {len(platform.budget_manager.alerts)} budget alerts!")
            
        # Rightsizing analysis
        print("\n📐 Rightsizing Analysis...")
        
        # Set low utilization for some resources
        for resource in created_resources[:3]:
            resource.avg_cpu_utilization = random.uniform(5, 15)
            resource.avg_memory_utilization = random.uniform(8, 18)
            
        recommendations = platform.rightsizing.analyze_all()
        
        print(f"  Found {len(recommendations)} rightsizing opportunities:")
        
        total_savings = 0
        for rec in recommendations:
            print(f"\n  📉 {platform.cost_tracker.resources[rec.resource_id].name}")
            print(f"     Current: {rec.current_type} (${rec.current_cost:.2f}/mo)")
            print(f"     Recommended: {rec.recommended_type} (${rec.recommended_cost:.2f}/mo)")
            print(f"     Monthly Savings: ${rec.monthly_savings:.2f}")
            print(f"     Reason: {rec.reason}")
            total_savings += rec.monthly_savings
            
        print(f"\n  💰 Total Potential Savings: ${total_savings:.2f}/month")
        
        # Reserved Instance analysis
        print("\n📅 Reserved Instance Analysis...")
        
        ri_analysis = platform.ri_optimizer.analyze()
        
        print(f"  Current RI Coverage: {ri_analysis.current_ri_coverage:.1f}%")
        print(f"  On-Demand Spend: ${ri_analysis.on_demand_spend:.2f}/mo")
        print(f"  Recommended Coverage: {ri_analysis.recommended_ri_coverage:.1f}%")
        print(f"  Break-even: {ri_analysis.break_even_months} months")
        print(f"  Monthly Savings: ${ri_analysis.monthly_savings:.2f}")
        print(f"  3-Year Savings: ${ri_analysis.total_savings_3y:.2f}")
        
        # Spot instances
        print("\n⚡ Spot Instance Management...")
        
        spot_data = [
            ("t3.large", 0.0832, 0.025),
            ("m5.large", 0.096, 0.029),
            ("c5.large", 0.085, 0.026)
        ]
        
        for instance_type, on_demand, spot_price in spot_data:
            spot = platform.spot_manager.create(
                f"res_{uuid.uuid4().hex[:8]}",
                instance_type,
                on_demand,
                spot_price,
                "us-east-1a"
            )
            print(f"  ✓ {instance_type}: ${on_demand:.4f} -> ${spot_price:.4f} ({spot.savings_percent:.1f}% savings)")
            
        spot_savings = platform.spot_manager.get_savings()
        
        print(f"\n  Spot Savings Summary:")
        print(f"    On-Demand would cost: ${spot_savings['on_demand_cost']:.2f}/mo")
        print(f"    Spot costs: ${spot_savings['spot_cost']:.2f}/mo")
        print(f"    Monthly Savings: ${spot_savings['monthly_savings']:.2f} ({spot_savings['savings_percent']:.1f}%)")
        
        # Cost comparison
        print("\n🔄 Cost Environment Comparison:")
        
        env_costs = platform.cost_tracker.get_cost_by_tag("env")
        
        for env, cost in sorted(env_costs.items()):
            print(f"  {env}: ${cost:.2f}")
            
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Resources: {stats['total_resources']}")
        print(f"  Monthly Cost: ${stats['monthly_cost']:.2f}")
        print(f"  Budgets: {stats['budgets']}")
        print(f"  Budget Alerts: {stats['budget_alerts']}")
        print(f"  Recommendations: {stats['recommendations']}")
        print(f"  Spot Instances: {stats['spot_instances']}")
        print(f"  Spot Savings: ${stats['spot_savings']:.2f}/mo")
        
        # Dashboard
        print("\n📋 Cost Optimization Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │               Cost Optimization Overview                    │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Resources:    {stats['total_resources']:>10}                        │")
        print(f"  │ Monthly Cost:       ${stats['monthly_cost']:>9.2f}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Budgets:            {stats['budgets']:>10}                        │")
        print(f"  │ Budget Alerts:      {stats['budget_alerts']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Recommendations:    {stats['recommendations']:>10}                        │")
        print(f"  │ Spot Instances:     {stats['spot_instances']:>10}                        │")
        print(f"  │ Spot Savings:       ${stats['spot_savings']:>9.2f}/mo                    │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Cost Optimization Platform initialized!")
    print("=" * 60)
