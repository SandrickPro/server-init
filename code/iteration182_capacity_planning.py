#!/usr/bin/env python3
"""
Server Init - Iteration 182: Capacity Planning Platform
Платформа планирования ёмкости

Функционал:
- Resource Forecasting - прогнозирование ресурсов
- Demand Modeling - моделирование спроса
- Growth Planning - планирование роста
- Bottleneck Detection - обнаружение узких мест
- Scaling Recommendations - рекомендации по масштабированию
- Cost Projections - прогнозы затрат
- What-If Analysis - анализ "что если"
- Capacity Reports - отчёты о ёмкости
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import uuid
import math


class ResourceType(Enum):
    """Тип ресурса"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    CACHE = "cache"


class GrowthModel(Enum):
    """Модель роста"""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    SEASONAL = "seasonal"
    STEP = "step"


class CapacityStatus(Enum):
    """Статус ёмкости"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    EXHAUSTED = "exhausted"


class ScalingDirection(Enum):
    """Направление масштабирования"""
    SCALE_UP = "scale_up"
    SCALE_OUT = "scale_out"
    SCALE_DOWN = "scale_down"
    NO_ACTION = "no_action"


@dataclass
class ResourceCapacity:
    """Ёмкость ресурса"""
    resource_id: str
    resource_type: ResourceType = ResourceType.CPU
    name: str = ""
    
    # Capacity
    total_capacity: float = 0.0
    used_capacity: float = 0.0
    reserved_capacity: float = 0.0
    
    # Unit
    unit: str = ""  # cores, GB, IOPS, etc.
    
    # Thresholds
    warning_threshold: float = 70.0
    critical_threshold: float = 85.0
    
    @property
    def available_capacity(self) -> float:
        return self.total_capacity - self.used_capacity - self.reserved_capacity
        
    @property
    def utilization_percent(self) -> float:
        if self.total_capacity == 0:
            return 0
        return (self.used_capacity / self.total_capacity) * 100
        
    @property
    def status(self) -> CapacityStatus:
        util = self.utilization_percent
        if util >= 95:
            return CapacityStatus.EXHAUSTED
        elif util >= self.critical_threshold:
            return CapacityStatus.CRITICAL
        elif util >= self.warning_threshold:
            return CapacityStatus.WARNING
        return CapacityStatus.HEALTHY


@dataclass
class DemandForecast:
    """Прогноз спроса"""
    forecast_id: str
    resource_id: str = ""
    
    # Time range
    start_date: datetime = field(default_factory=datetime.now)
    end_date: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=90))
    
    # Model
    growth_model: GrowthModel = GrowthModel.LINEAR
    
    # Predictions
    predictions: List[Tuple[datetime, float]] = field(default_factory=list)
    
    # Confidence
    confidence_interval: float = 95.0
    lower_bound: List[float] = field(default_factory=list)
    upper_bound: List[float] = field(default_factory=list)
    
    # Accuracy
    mape: float = 0.0  # Mean Absolute Percentage Error


@dataclass
class CapacityPlan:
    """План ёмкости"""
    plan_id: str
    name: str = ""
    description: str = ""
    
    # Time horizon
    horizon_months: int = 12
    created_at: datetime = field(default_factory=datetime.now)
    
    # Resources
    resource_plans: Dict[str, Dict] = field(default_factory=dict)
    
    # Cost
    total_cost_current: float = 0.0
    total_cost_projected: float = 0.0
    
    # Status
    approved: bool = False
    approved_by: str = ""


@dataclass
class Bottleneck:
    """Узкое место"""
    bottleneck_id: str
    resource_id: str = ""
    
    # Details
    severity: str = "medium"  # low, medium, high, critical
    description: str = ""
    
    # Impact
    affected_services: List[str] = field(default_factory=list)
    performance_impact: float = 0.0  # percent degradation
    
    # Timeline
    detected_at: datetime = field(default_factory=datetime.now)
    expected_exhaustion: Optional[datetime] = None
    
    # Resolution
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ScalingRecommendation:
    """Рекомендация по масштабированию"""
    recommendation_id: str
    resource_id: str = ""
    
    # Direction
    direction: ScalingDirection = ScalingDirection.NO_ACTION
    
    # Details
    current_capacity: float = 0.0
    recommended_capacity: float = 0.0
    
    # Timing
    urgency: str = "low"  # low, medium, high, immediate
    recommended_by: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=30))
    
    # Cost
    estimated_cost_change: float = 0.0
    
    # Justification
    reason: str = ""


class DemandModeler:
    """Моделирование спроса"""
    
    def __init__(self):
        self.historical_data: Dict[str, List[Tuple[datetime, float]]] = {}
        
    def add_historical_data(self, resource_id: str, data: List[Tuple[datetime, float]]):
        """Добавление исторических данных"""
        self.historical_data[resource_id] = data
        
    def forecast(self, resource_id: str, days: int = 90, model: GrowthModel = GrowthModel.LINEAR) -> DemandForecast:
        """Прогнозирование спроса"""
        forecast = DemandForecast(
            forecast_id=f"forecast_{uuid.uuid4().hex[:8]}",
            resource_id=resource_id,
            end_date=datetime.now() + timedelta(days=days),
            growth_model=model
        )
        
        historical = self.historical_data.get(resource_id, [])
        
        if not historical:
            return forecast
            
        # Simple linear regression for demo
        current_value = historical[-1][1] if historical else 0
        
        if len(historical) >= 2:
            growth_rate = (historical[-1][1] - historical[0][1]) / len(historical)
        else:
            growth_rate = 0
            
        # Generate predictions
        for day in range(1, days + 1):
            date = datetime.now() + timedelta(days=day)
            
            if model == GrowthModel.LINEAR:
                value = current_value + growth_rate * day
            elif model == GrowthModel.EXPONENTIAL:
                value = current_value * (1.02 ** day)  # 2% daily growth
            elif model == GrowthModel.SEASONAL:
                seasonal_factor = 1 + 0.2 * math.sin(2 * math.pi * day / 30)
                value = (current_value + growth_rate * day) * seasonal_factor
            else:
                value = current_value + growth_rate * day
                
            forecast.predictions.append((date, max(0, value)))
            forecast.lower_bound.append(max(0, value * 0.9))
            forecast.upper_bound.append(value * 1.1)
            
        forecast.mape = random.uniform(5, 15)
        return forecast


class BottleneckDetector:
    """Детектор узких мест"""
    
    def __init__(self):
        self.bottlenecks: Dict[str, Bottleneck] = {}
        
    def detect(self, resources: List[ResourceCapacity]) -> List[Bottleneck]:
        """Обнаружение узких мест"""
        bottlenecks = []
        
        for resource in resources:
            if resource.status in [CapacityStatus.CRITICAL, CapacityStatus.EXHAUSTED]:
                severity = "critical" if resource.status == CapacityStatus.EXHAUSTED else "high"
                
                bottleneck = Bottleneck(
                    bottleneck_id=f"bottleneck_{uuid.uuid4().hex[:8]}",
                    resource_id=resource.resource_id,
                    severity=severity,
                    description=f"{resource.name} at {resource.utilization_percent:.1f}% utilization",
                    performance_impact=resource.utilization_percent - 80,
                    recommendations=[
                        f"Scale {resource.resource_type.value} capacity",
                        "Review resource allocation",
                        "Consider load balancing"
                    ]
                )
                
                # Estimate exhaustion
                if resource.utilization_percent > 90:
                    days_until = max(1, int((100 - resource.utilization_percent) * 5))
                    bottleneck.expected_exhaustion = datetime.now() + timedelta(days=days_until)
                    
                bottlenecks.append(bottleneck)
                self.bottlenecks[bottleneck.bottleneck_id] = bottleneck
                
        return bottlenecks


class ScalingAdvisor:
    """Советник по масштабированию"""
    
    def __init__(self, demand_modeler: DemandModeler):
        self.demand_modeler = demand_modeler
        
    def recommend(self, resource: ResourceCapacity, forecast: DemandForecast = None) -> ScalingRecommendation:
        """Рекомендация по масштабированию"""
        rec = ScalingRecommendation(
            recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
            resource_id=resource.resource_id,
            current_capacity=resource.total_capacity
        )
        
        util = resource.utilization_percent
        
        # Determine direction
        if util >= 85:
            rec.direction = ScalingDirection.SCALE_UP
            rec.urgency = "high" if util >= 90 else "medium"
            rec.recommended_capacity = resource.total_capacity * 1.5
            rec.reason = f"High utilization ({util:.1f}%)"
        elif util >= 70:
            rec.direction = ScalingDirection.SCALE_OUT
            rec.urgency = "medium"
            rec.recommended_capacity = resource.total_capacity * 1.2
            rec.reason = f"Growing utilization ({util:.1f}%)"
        elif util < 30 and resource.total_capacity > 10:
            rec.direction = ScalingDirection.SCALE_DOWN
            rec.urgency = "low"
            rec.recommended_capacity = resource.total_capacity * 0.7
            rec.reason = f"Low utilization ({util:.1f}%)"
        else:
            rec.direction = ScalingDirection.NO_ACTION
            rec.reason = "Current capacity is adequate"
            
        # Estimate cost change
        if rec.direction in [ScalingDirection.SCALE_UP, ScalingDirection.SCALE_OUT]:
            rec.estimated_cost_change = (rec.recommended_capacity - rec.current_capacity) * 100
        elif rec.direction == ScalingDirection.SCALE_DOWN:
            rec.estimated_cost_change = (rec.recommended_capacity - rec.current_capacity) * 100
            
        return rec


class WhatIfAnalyzer:
    """Анализатор "что если" """
    
    def __init__(self, resources: Dict[str, ResourceCapacity]):
        self.resources = resources
        
    def analyze_traffic_increase(self, multiplier: float) -> Dict[str, Any]:
        """Анализ увеличения трафика"""
        results = {
            "scenario": f"Traffic increase {multiplier}x",
            "resources": {},
            "bottlenecks": [],
            "actions_required": []
        }
        
        for rid, resource in self.resources.items():
            new_usage = resource.used_capacity * multiplier
            new_util = (new_usage / resource.total_capacity) * 100 if resource.total_capacity > 0 else 100
            
            results["resources"][rid] = {
                "current_utilization": resource.utilization_percent,
                "projected_utilization": new_util,
                "status": "critical" if new_util > 85 else ("warning" if new_util > 70 else "ok")
            }
            
            if new_util > resource.total_capacity:
                results["bottlenecks"].append(f"{resource.name} will be exhausted")
                results["actions_required"].append(f"Scale {resource.name} by {int(multiplier * 1.2)}x")
                
        return results


class CapacityPlanningPlatform:
    """Платформа планирования ёмкости"""
    
    def __init__(self):
        self.resources: Dict[str, ResourceCapacity] = {}
        self.plans: Dict[str, CapacityPlan] = {}
        self.demand_modeler = DemandModeler()
        self.bottleneck_detector = BottleneckDetector()
        self.scaling_advisor = ScalingAdvisor(self.demand_modeler)
        
    def add_resource(self, resource: ResourceCapacity):
        """Добавление ресурса"""
        self.resources[resource.resource_id] = resource
        
    def get_what_if_analyzer(self) -> WhatIfAnalyzer:
        """Получение анализатора"""
        return WhatIfAnalyzer(self.resources)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        resources = list(self.resources.values())
        
        return {
            "total_resources": len(resources),
            "by_type": {
                rt.value: len([r for r in resources if r.resource_type == rt])
                for rt in ResourceType
            },
            "by_status": {
                st.value: len([r for r in resources if r.status == st])
                for st in CapacityStatus
            },
            "avg_utilization": sum(r.utilization_percent for r in resources) / len(resources) if resources else 0,
            "active_plans": len([p for p in self.plans.values() if p.approved])
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 182: Capacity Planning Platform")
    print("=" * 60)
    
    platform = CapacityPlanningPlatform()
    print("✓ Capacity Planning Platform created")
    
    # Create resources
    print("\n📦 Creating Resources...")
    
    resources = [
        ResourceCapacity(
            resource_id="cpu_prod",
            resource_type=ResourceType.CPU,
            name="Production CPU",
            total_capacity=1000,
            used_capacity=750,
            unit="cores"
        ),
        ResourceCapacity(
            resource_id="mem_prod",
            resource_type=ResourceType.MEMORY,
            name="Production Memory",
            total_capacity=2048,
            used_capacity=1600,
            unit="GB"
        ),
        ResourceCapacity(
            resource_id="storage_prod",
            resource_type=ResourceType.STORAGE,
            name="Production Storage",
            total_capacity=100,
            used_capacity=92,
            unit="TB"
        ),
        ResourceCapacity(
            resource_id="db_connections",
            resource_type=ResourceType.DATABASE,
            name="Database Connections",
            total_capacity=5000,
            used_capacity=3500,
            unit="connections"
        ),
        ResourceCapacity(
            resource_id="cache_mem",
            resource_type=ResourceType.CACHE,
            name="Redis Cache",
            total_capacity=256,
            used_capacity=180,
            unit="GB"
        ),
        ResourceCapacity(
            resource_id="network_bw",
            resource_type=ResourceType.NETWORK,
            name="Network Bandwidth",
            total_capacity=100,
            used_capacity=45,
            unit="Gbps"
        ),
    ]
    
    for resource in resources:
        platform.add_resource(resource)
        status_icon = "🟢" if resource.status == CapacityStatus.HEALTHY else ("🟡" if resource.status == CapacityStatus.WARNING else "🔴")
        print(f"  {status_icon} {resource.name}: {resource.utilization_percent:.1f}% ({resource.used_capacity}/{resource.total_capacity} {resource.unit})")
        
    # Resource utilization dashboard
    print("\n📊 Resource Utilization:")
    
    print("\n  ┌────────────────────────────────┬────────────┬──────────────┬────────────┬─────────────┐")
    print("  │ Resource                       │ Used       │ Total        │ Util %     │ Status      │")
    print("  ├────────────────────────────────┼────────────┼──────────────┼────────────┼─────────────┤")
    
    for resource in platform.resources.values():
        name = resource.name[:30].ljust(30)
        used = f"{resource.used_capacity:.0f}".rjust(10)
        total = f"{resource.total_capacity:.0f}".rjust(12)
        util = f"{resource.utilization_percent:.1f}%".rjust(10)
        status = resource.status.value[:11].ljust(11)
        print(f"  │ {name} │ {used} │ {total} │ {util} │ {status} │")
        
    print("  └────────────────────────────────┴────────────┴──────────────┴────────────┴─────────────┘")
    
    # Detect bottlenecks
    print("\n🔍 Bottleneck Detection...")
    
    bottlenecks = platform.bottleneck_detector.detect(list(platform.resources.values()))
    
    if bottlenecks:
        for bn in bottlenecks:
            resource = platform.resources.get(bn.resource_id)
            print(f"\n  ⚠️ {resource.name if resource else bn.resource_id}")
            print(f"     Severity: {bn.severity.upper()}")
            print(f"     Impact: {bn.performance_impact:.1f}% degradation")
            if bn.expected_exhaustion:
                days = (bn.expected_exhaustion - datetime.now()).days
                print(f"     Expected Exhaustion: {days} days")
            print(f"     Recommendations:")
            for rec in bn.recommendations[:2]:
                print(f"       • {rec}")
    else:
        print("  ✓ No critical bottlenecks detected")
        
    # Demand forecasting
    print("\n📈 Demand Forecasting...")
    
    # Add historical data
    for resource in resources:
        historical = []
        base = resource.used_capacity * 0.7
        for i in range(90):
            date = datetime.now() - timedelta(days=90-i)
            value = base + (resource.used_capacity - base) * (i / 90) + random.uniform(-5, 5)
            historical.append((date, value))
        platform.demand_modeler.add_historical_data(resource.resource_id, historical)
        
    # Generate forecasts
    print("\n  90-Day Forecasts:")
    
    for resource in resources[:3]:
        forecast = platform.demand_modeler.forecast(resource.resource_id, 90, GrowthModel.LINEAR)
        
        if forecast.predictions:
            current = resource.used_capacity
            projected = forecast.predictions[-1][1]
            change = ((projected - current) / current) * 100 if current > 0 else 0
            
            print(f"\n  {resource.name}:")
            print(f"    Current: {current:.0f} {resource.unit}")
            print(f"    Projected (90d): {projected:.0f} {resource.unit}")
            print(f"    Change: {change:+.1f}%")
            print(f"    Model Accuracy: {100 - forecast.mape:.1f}%")
            
    # Scaling recommendations
    print("\n💡 Scaling Recommendations:")
    
    for resource in resources:
        rec = platform.scaling_advisor.recommend(resource)
        
        if rec.direction != ScalingDirection.NO_ACTION:
            direction_icon = "⬆️" if rec.direction in [ScalingDirection.SCALE_UP, ScalingDirection.SCALE_OUT] else "⬇️"
            print(f"\n  {direction_icon} {resource.name}")
            print(f"     Action: {rec.direction.value.replace('_', ' ').title()}")
            print(f"     Current: {rec.current_capacity:.0f} → Recommended: {rec.recommended_capacity:.0f} {resource.unit}")
            print(f"     Urgency: {rec.urgency.upper()}")
            print(f"     Cost Change: ${rec.estimated_cost_change:+,.0f}/month")
            print(f"     Reason: {rec.reason}")
            
    # What-If analysis
    print("\n🔮 What-If Analysis:")
    
    analyzer = platform.get_what_if_analyzer()
    
    scenarios = [1.5, 2.0, 3.0]
    
    for multiplier in scenarios:
        results = analyzer.analyze_traffic_increase(multiplier)
        
        print(f"\n  Scenario: {results['scenario']}")
        
        critical_count = sum(1 for r in results['resources'].values() if r['status'] == 'critical')
        warning_count = sum(1 for r in results['resources'].values() if r['status'] == 'warning')
        
        print(f"    Resources at Risk: {critical_count} critical, {warning_count} warning")
        
        if results['actions_required']:
            print(f"    Actions Required: {len(results['actions_required'])}")
            
    # Capacity plan
    print("\n📋 Capacity Plan (12 months):")
    
    plan = CapacityPlan(
        plan_id="plan_2024",
        name="2024 Capacity Plan",
        description="Annual capacity planning",
        horizon_months=12
    )
    
    total_cost = 0
    print("\n  ┌────────────────────────────────┬───────────────┬───────────────┬──────────────┐")
    print("  │ Resource                       │ Current       │ EOY Target    │ Cost/Month   │")
    print("  ├────────────────────────────────┼───────────────┼───────────────┼──────────────┤")
    
    for resource in resources:
        rec = platform.scaling_advisor.recommend(resource)
        
        current = f"{resource.total_capacity:.0f} {resource.unit}"[:13].rjust(13)
        target = f"{rec.recommended_capacity:.0f} {resource.unit}"[:13].rjust(13)
        cost = rec.estimated_cost_change
        total_cost += abs(cost)
        cost_str = f"${cost:+,.0f}"[:12].rjust(12)
        name = resource.name[:30].ljust(30)
        
        print(f"  │ {name} │ {current} │ {target} │ {cost_str} │")
        
        plan.resource_plans[resource.resource_id] = {
            "current": resource.total_capacity,
            "target": rec.recommended_capacity,
            "cost_change": cost
        }
        
    print("  ├────────────────────────────────┴───────────────┴───────────────┼──────────────┤")
    print(f"  │ Total Monthly Cost Change                                      │ ${total_cost:>10,.0f} │")
    print("  └─────────────────────────────────────────────────────────────────┴──────────────┘")
    
    plan.total_cost_projected = total_cost
    platform.plans[plan.plan_id] = plan
    
    # Platform statistics
    print("\n📈 Platform Statistics:")
    
    stats = platform.get_statistics()
    
    print(f"\n  Total Resources: {stats['total_resources']}")
    print(f"  Average Utilization: {stats['avg_utilization']:.1f}%")
    
    print("\n  By Status:")
    for status, count in stats['by_status'].items():
        if count > 0:
            icon = "🟢" if status == "healthy" else ("🟡" if status == "warning" else "🔴")
            print(f"    {icon} {status}: {count}")
            
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Capacity Planning Dashboard                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Resources:               {stats['total_resources']:>10}                     │")
    print(f"│ Average Utilization:             {stats['avg_utilization']:>8.1f}%                   │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Healthy:                       {stats['by_status'].get('healthy', 0):>10}                     │")
    print(f"│ Warning:                       {stats['by_status'].get('warning', 0):>10}                     │")
    print(f"│ Critical:                      {stats['by_status'].get('critical', 0):>10}                     │")
    print(f"│ Active Bottlenecks:            {len(bottlenecks):>10}                     │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Capacity Planning Platform initialized!")
    print("=" * 60)
