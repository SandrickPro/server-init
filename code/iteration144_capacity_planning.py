#!/usr/bin/env python3
"""
Server Init - Iteration 144: Capacity Planning Platform
Платформа планирования ёмкости

Функционал:
- Resource Forecasting - прогнозирование ресурсов
- Demand Modeling - моделирование спроса
- Capacity Analysis - анализ ёмкости
- Growth Planning - планирование роста
- What-If Scenarios - сценарии "что если"
- Bottleneck Detection - обнаружение узких мест
- Right-Sizing - оптимизация размеров
- Budget Planning - планирование бюджета
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
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    GPU = "gpu"
    DATABASE = "database"


class TimeGranularity(Enum):
    """Гранулярность времени"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class ScenarioType(Enum):
    """Тип сценария"""
    BASELINE = "baseline"
    GROWTH = "growth"
    PEAK = "peak"
    COST_OPTIMIZED = "cost_optimized"
    CUSTOM = "custom"


class BottleneckSeverity(Enum):
    """Серьёзность узкого места"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ResourceMetrics:
    """Метрики ресурса"""
    resource_id: str
    resource_type: ResourceType = ResourceType.CPU
    
    # Current state
    current_capacity: float = 0.0
    current_usage: float = 0.0
    utilization_percent: float = 0.0
    
    # Historical
    avg_usage_7d: float = 0.0
    avg_usage_30d: float = 0.0
    peak_usage: float = 0.0
    
    # Unit
    unit: str = ""  # cores, GB, IOPS, etc.
    
    # Timestamps
    measured_at: datetime = field(default_factory=datetime.now)


@dataclass
class DemandForecast:
    """Прогноз спроса"""
    forecast_id: str
    resource_type: ResourceType = ResourceType.CPU
    
    # Time horizon
    horizon_days: int = 90
    granularity: TimeGranularity = TimeGranularity.DAILY
    
    # Forecast data
    forecasted_values: List[float] = field(default_factory=list)
    confidence_lower: List[float] = field(default_factory=list)
    confidence_upper: List[float] = field(default_factory=list)
    
    # Model info
    model_type: str = "exponential_smoothing"
    accuracy_mae: float = 0.0
    
    # Generated
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class CapacityPlan:
    """План ёмкости"""
    plan_id: str
    name: str = ""
    
    # Time frame
    start_date: datetime = field(default_factory=datetime.now)
    end_date: datetime = field(default_factory=datetime.now)
    
    # Resource requirements
    requirements: Dict[str, float] = field(default_factory=dict)
    
    # Current vs needed
    current_capacity: Dict[str, float] = field(default_factory=dict)
    required_capacity: Dict[str, float] = field(default_factory=dict)
    gap: Dict[str, float] = field(default_factory=dict)
    
    # Cost
    estimated_cost: float = 0.0
    
    # Status
    status: str = "draft"  # draft, approved, in_progress, completed


@dataclass
class WhatIfScenario:
    """Сценарий "что если" """
    scenario_id: str
    name: str = ""
    scenario_type: ScenarioType = ScenarioType.BASELINE
    
    # Parameters
    growth_rate: float = 0.0  # percentage
    peak_multiplier: float = 1.0
    
    # Projections
    projected_demand: Dict[str, List[float]] = field(default_factory=dict)
    projected_cost: float = 0.0
    
    # Comparison
    baseline_difference: float = 0.0


@dataclass
class Bottleneck:
    """Узкое место"""
    bottleneck_id: str
    resource_type: ResourceType = ResourceType.CPU
    
    # Location
    component: str = ""
    region: str = ""
    
    # Metrics
    current_utilization: float = 0.0
    threshold: float = 80.0
    headroom_percent: float = 0.0
    
    # Severity
    severity: BottleneckSeverity = BottleneckSeverity.MEDIUM
    
    # Time to saturation
    days_to_saturation: int = 0
    
    # Recommendation
    recommendation: str = ""


@dataclass
class RightSizingRecommendation:
    """Рекомендация по оптимизации размера"""
    recommendation_id: str
    resource_id: str = ""
    resource_name: str = ""
    
    # Current
    current_size: str = ""
    current_cost: float = 0.0
    current_utilization: float = 0.0
    
    # Recommended
    recommended_size: str = ""
    recommended_cost: float = 0.0
    
    # Savings
    estimated_savings: float = 0.0
    savings_percent: float = 0.0
    
    # Action
    action: str = ""  # upsize, downsize, no_change


@dataclass
class BudgetProjection:
    """Проекция бюджета"""
    projection_id: str
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Current
    current_monthly_cost: float = 0.0
    
    # Projected
    projected_costs: List[float] = field(default_factory=list)
    total_projected: float = 0.0
    
    # By category
    by_resource_type: Dict[str, float] = field(default_factory=dict)


class MetricsCollector:
    """Коллектор метрик"""
    
    def __init__(self):
        self.metrics: Dict[str, List[ResourceMetrics]] = {}
        
    def collect(self, resource_id: str, resource_type: ResourceType,
                 capacity: float, usage: float, unit: str = "") -> ResourceMetrics:
        """Сбор метрик"""
        utilization = (usage / capacity * 100) if capacity > 0 else 0
        
        metrics = ResourceMetrics(
            resource_id=resource_id,
            resource_type=resource_type,
            current_capacity=capacity,
            current_usage=usage,
            utilization_percent=utilization,
            unit=unit
        )
        
        if resource_id not in self.metrics:
            self.metrics[resource_id] = []
        self.metrics[resource_id].append(metrics)
        
        return metrics
        
    def get_historical(self, resource_id: str, days: int = 30) -> List[ResourceMetrics]:
        """Получение исторических данных"""
        return self.metrics.get(resource_id, [])[-days:]
        
    def calculate_averages(self, resource_id: str) -> Dict[str, float]:
        """Расчёт средних значений"""
        history = self.metrics.get(resource_id, [])
        
        if not history:
            return {"avg_7d": 0, "avg_30d": 0, "peak": 0}
            
        usages = [m.current_usage for m in history]
        
        return {
            "avg_7d": sum(usages[-7:]) / len(usages[-7:]) if len(usages) >= 7 else sum(usages) / len(usages),
            "avg_30d": sum(usages[-30:]) / len(usages[-30:]) if len(usages) >= 30 else sum(usages) / len(usages),
            "peak": max(usages)
        }


class ForecastEngine:
    """Движок прогнозирования"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.forecasts: Dict[str, DemandForecast] = {}
        
    def forecast(self, resource_id: str, resource_type: ResourceType,
                  horizon_days: int = 90, growth_rate: float = 0.05) -> DemandForecast:
        """Прогнозирование"""
        history = self.metrics_collector.get_historical(resource_id)
        
        # Get base value
        if history:
            base_value = sum(m.current_usage for m in history[-7:]) / min(7, len(history))
        else:
            base_value = 100  # Default
            
        # Generate forecast with exponential growth
        forecasted = []
        confidence_lower = []
        confidence_upper = []
        
        daily_growth = (1 + growth_rate) ** (1/365)
        
        for day in range(horizon_days):
            value = base_value * (daily_growth ** day)
            # Add some randomness for realism
            noise = random.uniform(-0.05, 0.05) * value
            forecasted.append(value + noise)
            confidence_lower.append(value * 0.85)
            confidence_upper.append(value * 1.15)
            
        forecast = DemandForecast(
            forecast_id=f"fc_{uuid.uuid4().hex[:8]}",
            resource_type=resource_type,
            horizon_days=horizon_days,
            forecasted_values=forecasted,
            confidence_lower=confidence_lower,
            confidence_upper=confidence_upper,
            accuracy_mae=random.uniform(2, 8)
        )
        
        self.forecasts[resource_id] = forecast
        return forecast
        
    def get_peak_demand(self, forecast_id: str) -> float:
        """Получение пикового спроса"""
        for forecast in self.forecasts.values():
            if forecast.forecast_id == forecast_id:
                return max(forecast.forecasted_values) if forecast.forecasted_values else 0
        return 0


class CapacityPlanner:
    """Планировщик ёмкости"""
    
    def __init__(self, forecast_engine: ForecastEngine):
        self.forecast_engine = forecast_engine
        self.plans: Dict[str, CapacityPlan] = {}
        
    def create_plan(self, name: str, resources: Dict[str, Dict],
                     months_ahead: int = 6) -> CapacityPlan:
        """Создание плана"""
        plan = CapacityPlan(
            plan_id=f"plan_{uuid.uuid4().hex[:8]}",
            name=name,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=months_ahead * 30)
        )
        
        total_cost = 0
        
        for resource_id, resource_info in resources.items():
            current = resource_info.get("current_capacity", 0)
            growth_rate = resource_info.get("growth_rate", 0.1)
            unit_cost = resource_info.get("unit_cost", 100)
            
            # Forecast future requirement
            future = current * ((1 + growth_rate) ** (months_ahead / 12))
            gap = max(0, future - current)
            
            plan.current_capacity[resource_id] = current
            plan.required_capacity[resource_id] = future
            plan.gap[resource_id] = gap
            
            total_cost += gap * unit_cost
            
        plan.estimated_cost = total_cost
        self.plans[plan.plan_id] = plan
        
        return plan
        
    def approve_plan(self, plan_id: str) -> CapacityPlan:
        """Утверждение плана"""
        plan = self.plans.get(plan_id)
        if plan:
            plan.status = "approved"
        return plan


class ScenarioAnalyzer:
    """Анализатор сценариев"""
    
    def __init__(self, forecast_engine: ForecastEngine):
        self.forecast_engine = forecast_engine
        self.scenarios: Dict[str, WhatIfScenario] = {}
        
    def create_scenario(self, name: str, scenario_type: ScenarioType,
                         base_values: Dict[str, float],
                         **kwargs) -> WhatIfScenario:
        """Создание сценария"""
        scenario = WhatIfScenario(
            scenario_id=f"sc_{uuid.uuid4().hex[:8]}",
            name=name,
            scenario_type=scenario_type
        )
        
        # Set parameters based on type
        if scenario_type == ScenarioType.GROWTH:
            scenario.growth_rate = kwargs.get("growth_rate", 0.25)
        elif scenario_type == ScenarioType.PEAK:
            scenario.peak_multiplier = kwargs.get("peak_multiplier", 2.0)
        elif scenario_type == ScenarioType.COST_OPTIMIZED:
            scenario.growth_rate = kwargs.get("growth_rate", 0.05)
            
        # Generate projections
        for resource, base in base_values.items():
            projections = []
            for month in range(12):
                if scenario_type == ScenarioType.GROWTH:
                    value = base * ((1 + scenario.growth_rate) ** (month / 12))
                elif scenario_type == ScenarioType.PEAK:
                    value = base * scenario.peak_multiplier if month in [5, 6, 11] else base
                else:
                    value = base * ((1 + 0.05) ** (month / 12))
                projections.append(value)
            scenario.projected_demand[resource] = projections
            
        # Calculate cost
        scenario.projected_cost = sum(
            sum(vals) for vals in scenario.projected_demand.values()
        ) * 10  # $10 per unit
        
        self.scenarios[scenario.scenario_id] = scenario
        return scenario
        
    def compare_scenarios(self, scenario_ids: List[str]) -> Dict:
        """Сравнение сценариев"""
        results = []
        
        for sid in scenario_ids:
            scenario = self.scenarios.get(sid)
            if scenario:
                results.append({
                    "id": sid,
                    "name": scenario.name,
                    "type": scenario.scenario_type.value,
                    "cost": scenario.projected_cost
                })
                
        return {
            "scenarios": results,
            "lowest_cost": min(results, key=lambda x: x["cost"]) if results else None,
            "highest_cost": max(results, key=lambda x: x["cost"]) if results else None
        }


class BottleneckDetector:
    """Детектор узких мест"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.bottlenecks: List[Bottleneck] = []
        
    def detect(self, threshold: float = 80.0) -> List[Bottleneck]:
        """Обнаружение узких мест"""
        detected = []
        
        for resource_id, history in self.metrics_collector.metrics.items():
            if not history:
                continue
                
            latest = history[-1]
            
            if latest.utilization_percent >= threshold:
                # Calculate days to saturation
                growth_rate = 0.02  # Assume 2% daily growth
                headroom = 100 - latest.utilization_percent
                days_to_sat = int(headroom / (latest.utilization_percent * growth_rate)) if growth_rate > 0 else 999
                
                severity = BottleneckSeverity.CRITICAL if latest.utilization_percent >= 95 else \
                           BottleneckSeverity.HIGH if latest.utilization_percent >= 90 else \
                           BottleneckSeverity.MEDIUM
                           
                bottleneck = Bottleneck(
                    bottleneck_id=f"bn_{uuid.uuid4().hex[:8]}",
                    resource_type=latest.resource_type,
                    component=resource_id,
                    current_utilization=latest.utilization_percent,
                    threshold=threshold,
                    headroom_percent=100 - latest.utilization_percent,
                    severity=severity,
                    days_to_saturation=days_to_sat,
                    recommendation=f"Scale {latest.resource_type.value} capacity by {int(latest.utilization_percent - 60)}%"
                )
                detected.append(bottleneck)
                
        self.bottlenecks = detected
        return detected


class RightSizingAnalyzer:
    """Анализатор оптимизации размеров"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.recommendations: List[RightSizingRecommendation] = []
        
    def analyze(self) -> List[RightSizingRecommendation]:
        """Анализ и рекомендации"""
        recs = []
        
        sizes = ["small", "medium", "large", "xlarge", "2xlarge"]
        costs = {"small": 50, "medium": 100, "large": 200, "xlarge": 400, "2xlarge": 800}
        
        for resource_id, history in self.metrics_collector.metrics.items():
            if not history:
                continue
                
            avg_util = sum(m.utilization_percent for m in history[-7:]) / min(7, len(history))
            current_size = random.choice(sizes)
            current_cost = costs[current_size]
            
            # Determine action
            if avg_util < 30:
                action = "downsize"
                current_idx = sizes.index(current_size)
                recommended_size = sizes[max(0, current_idx - 1)]
            elif avg_util > 80:
                action = "upsize"
                current_idx = sizes.index(current_size)
                recommended_size = sizes[min(len(sizes) - 1, current_idx + 1)]
            else:
                action = "no_change"
                recommended_size = current_size
                
            recommended_cost = costs[recommended_size]
            savings = current_cost - recommended_cost
            
            rec = RightSizingRecommendation(
                recommendation_id=f"rs_{uuid.uuid4().hex[:8]}",
                resource_id=resource_id,
                resource_name=f"Instance-{resource_id[-6:]}",
                current_size=current_size,
                current_cost=current_cost,
                current_utilization=avg_util,
                recommended_size=recommended_size,
                recommended_cost=recommended_cost,
                estimated_savings=max(0, savings),
                savings_percent=(savings / current_cost * 100) if current_cost > 0 else 0,
                action=action
            )
            recs.append(rec)
            
        self.recommendations = recs
        return recs


class BudgetPlanner:
    """Планировщик бюджета"""
    
    def __init__(self, forecast_engine: ForecastEngine):
        self.forecast_engine = forecast_engine
        self.projections: List[BudgetProjection] = []
        
    def project(self, current_costs: Dict[str, float], months: int = 12,
                 growth_rate: float = 0.05) -> BudgetProjection:
        """Проекция бюджета"""
        projection = BudgetProjection(
            projection_id=f"bp_{uuid.uuid4().hex[:8]}",
            period_end=datetime.now() + timedelta(days=months * 30),
            current_monthly_cost=sum(current_costs.values())
        )
        
        total = 0
        monthly_values = []
        
        for month in range(months):
            monthly = sum(current_costs.values()) * ((1 + growth_rate) ** (month / 12))
            monthly_values.append(monthly)
            total += monthly
            
        projection.projected_costs = monthly_values
        projection.total_projected = total
        projection.by_resource_type = {k: v * months for k, v in current_costs.items()}
        
        self.projections.append(projection)
        return projection


class CapacityPlanningPlatform:
    """Платформа планирования ёмкости"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.forecast_engine = ForecastEngine(self.metrics_collector)
        self.capacity_planner = CapacityPlanner(self.forecast_engine)
        self.scenario_analyzer = ScenarioAnalyzer(self.forecast_engine)
        self.bottleneck_detector = BottleneckDetector(self.metrics_collector)
        self.rightsizing_analyzer = RightSizingAnalyzer(self.metrics_collector)
        self.budget_planner = BudgetPlanner(self.forecast_engine)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        return {
            "resources_monitored": len(self.metrics_collector.metrics),
            "forecasts": len(self.forecast_engine.forecasts),
            "capacity_plans": len(self.capacity_planner.plans),
            "scenarios": len(self.scenario_analyzer.scenarios),
            "bottlenecks": len(self.bottleneck_detector.bottlenecks),
            "rightsizing_recs": len(self.rightsizing_analyzer.recommendations),
            "budget_projections": len(self.budget_planner.projections)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 144: Capacity Planning Platform")
    print("=" * 60)
    
    async def demo():
        platform = CapacityPlanningPlatform()
        print("✓ Capacity Planning Platform created")
        
        # Collect metrics
        print("\n📊 Collecting Resource Metrics...")
        
        resources = [
            ("web-cluster-cpu", ResourceType.CPU, 100, 75, "cores"),
            ("web-cluster-mem", ResourceType.MEMORY, 512, 420, "GB"),
            ("db-primary-cpu", ResourceType.CPU, 64, 58, "cores"),
            ("db-primary-storage", ResourceType.STORAGE, 10000, 7500, "GB"),
            ("cache-cluster-mem", ResourceType.MEMORY, 256, 230, "GB"),
            ("api-gateway-network", ResourceType.NETWORK, 10000, 6500, "Mbps"),
            ("ml-cluster-gpu", ResourceType.GPU, 8, 7, "GPUs")
        ]
        
        for res_id, res_type, capacity, usage, unit in resources:
            # Collect multiple data points for history
            for i in range(30):
                noise = random.uniform(-0.1, 0.1) * usage
                platform.metrics_collector.collect(
                    res_id, res_type, capacity, usage + noise, unit
                )
                
        for res_id, res_type, capacity, usage, unit in resources:
            util = usage / capacity * 100
            status = "🔴" if util > 85 else "🟡" if util > 70 else "🟢"
            print(f"  {status} {res_id}: {usage}/{capacity} {unit} ({util:.1f}%)")
            
        # Generate forecasts
        print("\n🔮 Generating Demand Forecasts...")
        
        forecasts = {}
        for res_id, res_type, _, _, _ in resources[:3]:
            forecast = platform.forecast_engine.forecast(
                res_id, res_type, horizon_days=90, growth_rate=0.15
            )
            forecasts[res_id] = forecast
            peak = max(forecast.forecasted_values)
            print(f"  ✓ {res_id}: Peak demand in 90d = {peak:.1f}")
            
        # Create capacity plan
        print("\n📋 Creating Capacity Plan...")
        
        plan_resources = {
            "web-cluster": {"current_capacity": 100, "growth_rate": 0.20, "unit_cost": 500},
            "database": {"current_capacity": 64, "growth_rate": 0.15, "unit_cost": 1000},
            "storage": {"current_capacity": 10000, "growth_rate": 0.25, "unit_cost": 0.10}
        }
        
        plan = platform.capacity_planner.create_plan("Q1 2025 Expansion", plan_resources, months_ahead=6)
        
        print(f"\n  Plan: {plan.name}")
        print(f"  Period: {plan.start_date.strftime('%Y-%m-%d')} to {plan.end_date.strftime('%Y-%m-%d')}")
        print(f"\n  Resource Gaps:")
        for res, gap in plan.gap.items():
            print(f"    {res}: +{gap:.1f} units needed")
        print(f"\n  Estimated Cost: ${plan.estimated_cost:,.2f}")
        
        # What-if scenarios
        print("\n🎭 Running What-If Scenarios...")
        
        base_values = {"compute": 100, "storage": 10000, "network": 5000}
        
        scenarios = [
            ("Baseline Growth", ScenarioType.BASELINE, {}),
            ("Aggressive Growth", ScenarioType.GROWTH, {"growth_rate": 0.50}),
            ("Peak Season", ScenarioType.PEAK, {"peak_multiplier": 2.5}),
            ("Cost Optimized", ScenarioType.COST_OPTIMIZED, {"growth_rate": 0.03})
        ]
        
        scenario_ids = []
        for name, sc_type, params in scenarios:
            scenario = platform.scenario_analyzer.create_scenario(
                name, sc_type, base_values, **params
            )
            scenario_ids.append(scenario.scenario_id)
            print(f"  ✓ {name}: Projected cost ${scenario.projected_cost:,.2f}")
            
        comparison = platform.scenario_analyzer.compare_scenarios(scenario_ids)
        print(f"\n  Lowest Cost: {comparison['lowest_cost']['name']} (${comparison['lowest_cost']['cost']:,.2f})")
        print(f"  Highest Cost: {comparison['highest_cost']['name']} (${comparison['highest_cost']['cost']:,.2f})")
        
        # Detect bottlenecks
        print("\n⚠️ Detecting Bottlenecks...")
        
        bottlenecks = platform.bottleneck_detector.detect(threshold=80)
        
        for bn in bottlenecks:
            severity_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
            print(f"  {severity_icon[bn.severity.value]} {bn.component}")
            print(f"      Utilization: {bn.current_utilization:.1f}%")
            print(f"      Days to saturation: {bn.days_to_saturation}")
            print(f"      Recommendation: {bn.recommendation}")
            
        # Right-sizing analysis
        print("\n📐 Running Right-Sizing Analysis...")
        
        rightsizing_recs = platform.rightsizing_analyzer.analyze()
        
        downsize = [r for r in rightsizing_recs if r.action == "downsize"]
        upsize = [r for r in rightsizing_recs if r.action == "upsize"]
        no_change = [r for r in rightsizing_recs if r.action == "no_change"]
        
        print(f"\n  Summary:")
        print(f"    Downsize: {len(downsize)} resources")
        print(f"    Upsize: {len(upsize)} resources")
        print(f"    No change: {len(no_change)} resources")
        
        total_savings = sum(r.estimated_savings for r in rightsizing_recs)
        print(f"\n  Total Potential Savings: ${total_savings:,.2f}/month")
        
        if downsize:
            print(f"\n  Top Downsize Recommendations:")
            for rec in sorted(downsize, key=lambda x: x.estimated_savings, reverse=True)[:3]:
                print(f"    • {rec.resource_name}: {rec.current_size} → {rec.recommended_size} (Save ${rec.estimated_savings}/mo)")
                
        # Budget planning
        print("\n💰 Budget Projections...")
        
        current_costs = {
            "compute": 25000,
            "storage": 8000,
            "network": 5000,
            "database": 15000
        }
        
        budget = platform.budget_planner.project(current_costs, months=12, growth_rate=0.10)
        
        print(f"\n  Current Monthly: ${budget.current_monthly_cost:,.2f}")
        print(f"  12-Month Projection: ${budget.total_projected:,.2f}")
        print(f"\n  Monthly Trend:")
        for i, cost in enumerate(budget.projected_costs[:6], 1):
            bar = "█" * int(cost / 3000)
            print(f"    Month {i}: ${cost:,.2f} {bar}")
            
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Resources Monitored: {stats['resources_monitored']}")
        print(f"  Forecasts: {stats['forecasts']}")
        print(f"  Capacity Plans: {stats['capacity_plans']}")
        print(f"  Scenarios: {stats['scenarios']}")
        print(f"  Bottlenecks: {stats['bottlenecks']}")
        print(f"  Right-sizing Recs: {stats['rightsizing_recs']}")
        print(f"  Budget Projections: {stats['budget_projections']}")
        
        # Dashboard
        print("\n📋 Capacity Planning Dashboard:")
        print("  ┌────────────────────────────────────────────────────────────┐")
        print("  │                  Capacity Overview                         │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Resources Monitored:   {stats['resources_monitored']:>10}                    │")
        print(f"  │ Active Forecasts:      {stats['forecasts']:>10}                    │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Capacity Plans:        {stats['capacity_plans']:>10}                    │")
        print(f"  │ Scenarios Analyzed:    {stats['scenarios']:>10}                    │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Bottlenecks Detected:  {stats['bottlenecks']:>10}                    │")
        print(f"  │ Right-sizing Recs:     {stats['rightsizing_recs']:>10}                    │")
        print(f"  │ Potential Savings:     ${total_savings:>9,.0f}                    │")
        print("  └────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Capacity Planning Platform initialized!")
    print("=" * 60)
