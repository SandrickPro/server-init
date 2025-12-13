#!/usr/bin/env python3
"""
Server Init - Iteration 113: Capacity Planning Platform
Платформа планирования ёмкости

Функционал:
- Resource Forecasting - прогнозирование ресурсов
- Growth Analysis - анализ роста
- Capacity Modeling - моделирование ёмкости
- Bottleneck Detection - обнаружение узких мест
- Scaling Recommendations - рекомендации по масштабированию
- Cost Projection - прогноз затрат
- Workload Simulation - симуляция нагрузки
- Trend Analysis - анализ трендов
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
from collections import defaultdict
import uuid
import random
import math


class ResourceType(Enum):
    """Тип ресурса"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    IOPS = "iops"
    CONNECTIONS = "connections"


class GrowthPattern(Enum):
    """Паттерн роста"""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    LOGARITHMIC = "logarithmic"
    SEASONAL = "seasonal"
    STEP = "step"


class BottleneckSeverity(Enum):
    """Критичность узкого места"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class RecommendationType(Enum):
    """Тип рекомендации"""
    SCALE_UP = "scale_up"
    SCALE_OUT = "scale_out"
    OPTIMIZE = "optimize"
    RESERVE = "reserve"
    MIGRATE = "migrate"


@dataclass
class ResourceMetric:
    """Метрика ресурса"""
    timestamp: datetime
    resource_type: ResourceType
    current_value: float = 0.0
    capacity: float = 0.0
    utilization: float = 0.0


@dataclass
class CapacityModel:
    """Модель ёмкости"""
    model_id: str
    service_name: str = ""
    
    # Resources
    resources: Dict[ResourceType, float] = field(default_factory=dict)
    current_usage: Dict[ResourceType, float] = field(default_factory=dict)
    
    # Growth
    growth_pattern: GrowthPattern = GrowthPattern.LINEAR
    growth_rate_monthly: float = 0.05  # 5% monthly
    
    # Load characteristics
    peak_multiplier: float = 1.5
    base_users: int = 1000
    users_per_resource_unit: float = 100.0


@dataclass
class Bottleneck:
    """Узкое место"""
    bottleneck_id: str
    service: str = ""
    
    # Resource
    resource_type: ResourceType = ResourceType.CPU
    
    # Details
    severity: BottleneckSeverity = BottleneckSeverity.WARNING
    current_utilization: float = 0.0
    threshold: float = 80.0
    
    # Impact
    affected_services: List[str] = field(default_factory=list)
    estimated_impact: str = ""
    
    # Detection
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class Forecast:
    """Прогноз"""
    forecast_id: str
    service: str = ""
    resource_type: ResourceType = ResourceType.CPU
    
    # Timeline
    horizon_days: int = 90
    created_at: datetime = field(default_factory=datetime.now)
    
    # Predictions
    predictions: List[Tuple[datetime, float]] = field(default_factory=list)
    
    # Confidence
    confidence: float = 0.85
    
    # Capacity exhaustion
    exhaustion_date: Optional[datetime] = None


@dataclass
class ScalingRecommendation:
    """Рекомендация по масштабированию"""
    rec_id: str
    service: str = ""
    
    # Type
    recommendation_type: RecommendationType = RecommendationType.SCALE_UP
    
    # Details
    resource_type: ResourceType = ResourceType.CPU
    current_capacity: float = 0.0
    recommended_capacity: float = 0.0
    
    # Timeline
    implement_by: datetime = field(default_factory=datetime.now)
    
    # Cost
    estimated_cost_monthly: float = 0.0
    
    # Priority
    priority: int = 1  # 1-5, 1 is highest
    
    # Rationale
    rationale: str = ""


@dataclass
class CostProjection:
    """Прогноз затрат"""
    projection_id: str
    
    # Timeline
    start_date: datetime = field(default_factory=datetime.now)
    end_date: datetime = field(default_factory=datetime.now)
    
    # Current
    current_monthly_cost: float = 0.0
    
    # Projections
    monthly_projections: List[Tuple[datetime, float]] = field(default_factory=list)
    
    # Total
    total_projected_cost: float = 0.0


class CapacityModeler:
    """Моделирование ёмкости"""
    
    def __init__(self):
        self.models: Dict[str, CapacityModel] = {}
        
    def create(self, service_name: str, **kwargs) -> CapacityModel:
        """Создание модели"""
        model = CapacityModel(
            model_id=f"cap_{uuid.uuid4().hex[:8]}",
            service_name=service_name,
            **kwargs
        )
        self.models[model.model_id] = model
        return model
        
    def calculate_headroom(self, model_id: str, 
                            resource_type: ResourceType) -> Dict[str, float]:
        """Расчёт запаса"""
        model = self.models.get(model_id)
        if not model:
            return {}
            
        capacity = model.resources.get(resource_type, 0)
        usage = model.current_usage.get(resource_type, 0)
        
        headroom = capacity - usage
        headroom_percent = (headroom / capacity * 100) if capacity > 0 else 0
        
        return {
            "capacity": capacity,
            "current_usage": usage,
            "headroom": headroom,
            "headroom_percent": headroom_percent
        }


class ForecastEngine:
    """Движок прогнозирования"""
    
    def __init__(self, modeler: CapacityModeler):
        self.modeler = modeler
        self.forecasts: Dict[str, Forecast] = {}
        
    def forecast(self, model_id: str, resource_type: ResourceType,
                  horizon_days: int = 90) -> Forecast:
        """Прогнозирование"""
        model = self.modeler.models.get(model_id)
        if not model:
            return None
            
        forecast = Forecast(
            forecast_id=f"fc_{uuid.uuid4().hex[:8]}",
            service=model.service_name,
            resource_type=resource_type,
            horizon_days=horizon_days
        )
        
        # Generate predictions
        current_usage = model.current_usage.get(resource_type, 0)
        capacity = model.resources.get(resource_type, 100)
        growth_rate = model.growth_rate_monthly
        
        predictions = []
        usage = current_usage
        
        for day in range(0, horizon_days, 7):  # Weekly predictions
            date = datetime.now() + timedelta(days=day)
            
            if model.growth_pattern == GrowthPattern.LINEAR:
                usage = current_usage * (1 + growth_rate * day / 30)
            elif model.growth_pattern == GrowthPattern.EXPONENTIAL:
                usage = current_usage * math.exp(growth_rate * day / 30)
            elif model.growth_pattern == GrowthPattern.SEASONAL:
                base_growth = 1 + growth_rate * day / 30
                seasonal = 1 + 0.2 * math.sin(2 * math.pi * day / 365)
                usage = current_usage * base_growth * seasonal
            else:
                usage = current_usage * (1 + growth_rate * day / 30)
                
            # Add some noise
            usage *= random.uniform(0.95, 1.05)
            
            predictions.append((date, usage))
            
            # Check for capacity exhaustion
            if usage >= capacity and not forecast.exhaustion_date:
                forecast.exhaustion_date = date
                
        forecast.predictions = predictions
        self.forecasts[forecast.forecast_id] = forecast
        
        return forecast


class BottleneckDetector:
    """Детектор узких мест"""
    
    def __init__(self, modeler: CapacityModeler):
        self.modeler = modeler
        self.bottlenecks: List[Bottleneck] = []
        
    def detect(self, model_id: str) -> List[Bottleneck]:
        """Обнаружение узких мест"""
        model = self.modeler.models.get(model_id)
        if not model:
            return []
            
        bottlenecks = []
        
        for resource_type, capacity in model.resources.items():
            usage = model.current_usage.get(resource_type, 0)
            utilization = (usage / capacity * 100) if capacity > 0 else 0
            
            if utilization >= 90:
                severity = BottleneckSeverity.CRITICAL
            elif utilization >= 80:
                severity = BottleneckSeverity.WARNING
            elif utilization >= 70:
                severity = BottleneckSeverity.INFO
            else:
                continue
                
            bottleneck = Bottleneck(
                bottleneck_id=f"bn_{uuid.uuid4().hex[:8]}",
                service=model.service_name,
                resource_type=resource_type,
                severity=severity,
                current_utilization=utilization,
                threshold=80.0,
                estimated_impact=f"Service degradation risk at {utilization:.1f}% utilization"
            )
            bottlenecks.append(bottleneck)
            
        self.bottlenecks.extend(bottlenecks)
        return bottlenecks


class RecommendationEngine:
    """Движок рекомендаций"""
    
    def __init__(self, modeler: CapacityModeler, forecaster: ForecastEngine):
        self.modeler = modeler
        self.forecaster = forecaster
        self.recommendations: List[ScalingRecommendation] = []
        
    def generate(self, model_id: str) -> List[ScalingRecommendation]:
        """Генерация рекомендаций"""
        model = self.modeler.models.get(model_id)
        if not model:
            return []
            
        recommendations = []
        
        for resource_type, capacity in model.resources.items():
            usage = model.current_usage.get(resource_type, 0)
            utilization = (usage / capacity * 100) if capacity > 0 else 0
            
            if utilization >= 80:
                # Need to scale
                recommended = capacity * 1.5
                cost = self._estimate_cost(resource_type, recommended - capacity)
                
                rec = ScalingRecommendation(
                    rec_id=f"rec_{uuid.uuid4().hex[:8]}",
                    service=model.service_name,
                    recommendation_type=RecommendationType.SCALE_UP,
                    resource_type=resource_type,
                    current_capacity=capacity,
                    recommended_capacity=recommended,
                    implement_by=datetime.now() + timedelta(days=14),
                    estimated_cost_monthly=cost,
                    priority=1 if utilization >= 90 else 2,
                    rationale=f"Current utilization {utilization:.1f}% exceeds threshold"
                )
                recommendations.append(rec)
                
            elif utilization >= 60:
                # Reserve capacity
                recommended = capacity * 1.25
                cost = self._estimate_cost(resource_type, recommended - capacity)
                
                rec = ScalingRecommendation(
                    rec_id=f"rec_{uuid.uuid4().hex[:8]}",
                    service=model.service_name,
                    recommendation_type=RecommendationType.RESERVE,
                    resource_type=resource_type,
                    current_capacity=capacity,
                    recommended_capacity=recommended,
                    implement_by=datetime.now() + timedelta(days=30),
                    estimated_cost_monthly=cost,
                    priority=3,
                    rationale=f"Proactive capacity reservation based on {utilization:.1f}% utilization"
                )
                recommendations.append(rec)
                
        self.recommendations.extend(recommendations)
        return recommendations
        
    def _estimate_cost(self, resource_type: ResourceType, 
                        additional_capacity: float) -> float:
        """Оценка стоимости"""
        # Cost per unit per month
        costs = {
            ResourceType.CPU: 50.0,
            ResourceType.MEMORY: 10.0,
            ResourceType.STORAGE: 0.1,
            ResourceType.NETWORK: 0.05,
            ResourceType.IOPS: 0.01,
            ResourceType.CONNECTIONS: 0.5
        }
        return costs.get(resource_type, 1.0) * additional_capacity


class CostProjector:
    """Проектор затрат"""
    
    def __init__(self, modeler: CapacityModeler, recommender: RecommendationEngine):
        self.modeler = modeler
        self.recommender = recommender
        
    def project(self, months: int = 12) -> CostProjection:
        """Проекция затрат"""
        projection = CostProjection(
            projection_id=f"proj_{uuid.uuid4().hex[:8]}",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=months * 30)
        )
        
        # Calculate current cost
        current_cost = 0.0
        for model in self.modeler.models.values():
            for resource_type, capacity in model.resources.items():
                current_cost += self.recommender._estimate_cost(resource_type, capacity)
                
        projection.current_monthly_cost = current_cost
        
        # Project monthly costs
        monthly_cost = current_cost
        total = 0.0
        
        for month in range(months):
            date = datetime.now() + timedelta(days=month * 30)
            
            # Apply growth
            avg_growth = 0.05  # 5% monthly average
            monthly_cost *= (1 + avg_growth)
            
            projection.monthly_projections.append((date, monthly_cost))
            total += monthly_cost
            
        projection.total_projected_cost = total
        
        return projection


class CapacityPlanningPlatform:
    """Платформа планирования ёмкости"""
    
    def __init__(self):
        self.modeler = CapacityModeler()
        self.forecaster = ForecastEngine(self.modeler)
        self.bottleneck_detector = BottleneckDetector(self.modeler)
        self.recommender = RecommendationEngine(self.modeler, self.forecaster)
        self.cost_projector = CostProjector(self.modeler, self.recommender)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        models = list(self.modeler.models.values())
        
        total_capacity = defaultdict(float)
        total_usage = defaultdict(float)
        
        for model in models:
            for rt, cap in model.resources.items():
                total_capacity[rt.value] += cap
                total_usage[rt.value] += model.current_usage.get(rt, 0)
                
        return {
            "total_services": len(models),
            "total_forecasts": len(self.forecaster.forecasts),
            "active_bottlenecks": len(self.bottleneck_detector.bottlenecks),
            "recommendations": len(self.recommender.recommendations),
            "total_capacity": dict(total_capacity),
            "total_usage": dict(total_usage)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 113: Capacity Planning Platform")
    print("=" * 60)
    
    async def demo():
        platform = CapacityPlanningPlatform()
        print("✓ Capacity Planning Platform created")
        
        # Create capacity models
        print("\n📊 Creating Capacity Models...")
        
        services_data = [
            ("api-gateway", GrowthPattern.LINEAR, 0.08, {
                ResourceType.CPU: 100, ResourceType.MEMORY: 256, 
                ResourceType.CONNECTIONS: 10000
            }, {
                ResourceType.CPU: 75, ResourceType.MEMORY: 180,
                ResourceType.CONNECTIONS: 7500
            }),
            ("user-service", GrowthPattern.EXPONENTIAL, 0.12, {
                ResourceType.CPU: 50, ResourceType.MEMORY: 128,
                ResourceType.STORAGE: 500
            }, {
                ResourceType.CPU: 45, ResourceType.MEMORY: 100,
                ResourceType.STORAGE: 350
            }),
            ("payment-service", GrowthPattern.SEASONAL, 0.05, {
                ResourceType.CPU: 80, ResourceType.MEMORY: 192,
                ResourceType.CONNECTIONS: 5000
            }, {
                ResourceType.CPU: 55, ResourceType.MEMORY: 140,
                ResourceType.CONNECTIONS: 3200
            }),
            ("analytics-service", GrowthPattern.LINEAR, 0.15, {
                ResourceType.CPU: 200, ResourceType.MEMORY: 512,
                ResourceType.STORAGE: 2000, ResourceType.IOPS: 10000
            }, {
                ResourceType.CPU: 160, ResourceType.MEMORY: 400,
                ResourceType.STORAGE: 1600, ResourceType.IOPS: 7500
            }),
            ("cache-cluster", GrowthPattern.LINEAR, 0.03, {
                ResourceType.MEMORY: 1024, ResourceType.NETWORK: 10000
            }, {
                ResourceType.MEMORY: 820, ResourceType.NETWORK: 6000
            })
        ]
        
        models = []
        for name, pattern, growth, resources, usage in services_data:
            model = platform.modeler.create(
                name,
                growth_pattern=pattern,
                growth_rate_monthly=growth,
                resources=resources,
                current_usage=usage
            )
            models.append(model)
            
            print(f"  ✓ {name} ({pattern.value}, {growth*100:.0f}% monthly)")
            
        # Calculate headroom
        print("\n📈 Resource Headroom Analysis...")
        
        for model in models[:3]:
            print(f"\n  {model.service_name}:")
            for rt in model.resources.keys():
                headroom = platform.modeler.calculate_headroom(model.model_id, rt)
                bar_filled = int(20 * (100 - headroom['headroom_percent']) / 100)
                bar = "█" * bar_filled + "░" * (20 - bar_filled)
                print(f"    {rt.value:12}: [{bar}] {headroom['headroom_percent']:.1f}% free")
                
        # Detect bottlenecks
        print("\n🔍 Detecting Bottlenecks...")
        
        all_bottlenecks = []
        for model in models:
            bottlenecks = platform.bottleneck_detector.detect(model.model_id)
            all_bottlenecks.extend(bottlenecks)
            
        if all_bottlenecks:
            for bn in all_bottlenecks:
                icon = {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(bn.severity.value, "⚪")
                print(f"  {icon} {bn.service}/{bn.resource_type.value}: {bn.current_utilization:.1f}% ({bn.severity.value})")
        else:
            print("  ✓ No bottlenecks detected")
            
        # Generate forecasts
        print("\n🔮 Generating Forecasts...")
        
        for model in models[:3]:
            for rt in [ResourceType.CPU, ResourceType.MEMORY]:
                if rt in model.resources:
                    forecast = platform.forecaster.forecast(
                        model.model_id, rt, horizon_days=90
                    )
                    
                    if forecast.exhaustion_date:
                        days_until = (forecast.exhaustion_date - datetime.now()).days
                        print(f"  ⚠️ {model.service_name}/{rt.value}: exhaustion in {days_until} days")
                    else:
                        print(f"  ✓ {model.service_name}/{rt.value}: sufficient for 90 days")
                        
        # Generate recommendations
        print("\n💡 Scaling Recommendations...")
        
        all_recommendations = []
        for model in models:
            recs = platform.recommender.generate(model.model_id)
            all_recommendations.extend(recs)
            
        # Sort by priority
        all_recommendations.sort(key=lambda x: x.priority)
        
        for rec in all_recommendations[:5]:
            priority_icon = ["🔴", "🟠", "🟡", "🟢", "🔵"][rec.priority - 1]
            print(f"  {priority_icon} [{rec.recommendation_type.value}] {rec.service}/{rec.resource_type.value}")
            print(f"     Current: {rec.current_capacity:.0f} → Recommended: {rec.recommended_capacity:.0f}")
            print(f"     Cost: ${rec.estimated_cost_monthly:.2f}/month")
            
        # Cost projection
        print("\n💰 Cost Projection (12 months)...")
        
        projection = platform.cost_projector.project(months=12)
        
        print(f"\n  Current monthly cost: ${projection.current_monthly_cost:,.2f}")
        print(f"  12-month total projection: ${projection.total_projected_cost:,.2f}")
        
        print("\n  Monthly breakdown:")
        for i, (date, cost) in enumerate(projection.monthly_projections[::3]):  # Every 3 months
            print(f"    {date.strftime('%b %Y')}: ${cost:,.2f}")
            
        # Trend analysis
        print("\n📉 Growth Trend Analysis:")
        
        for model in models[:3]:
            trend = "↗️ exponential" if model.growth_pattern == GrowthPattern.EXPONENTIAL else \
                    "➡️ linear" if model.growth_pattern == GrowthPattern.LINEAR else \
                    "🔄 seasonal"
            print(f"  {model.service_name}: {trend} ({model.growth_rate_monthly*100:.0f}%/month)")
            
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Services Modeled: {stats['total_services']}")
        print(f"  Active Forecasts: {stats['total_forecasts']}")
        print(f"  Bottlenecks: {stats['active_bottlenecks']}")
        print(f"  Recommendations: {stats['recommendations']}")
        
        print("\n  Total Capacity:")
        for rt, cap in stats['total_capacity'].items():
            usage = stats['total_usage'].get(rt, 0)
            util = (usage / cap * 100) if cap > 0 else 0
            print(f"    {rt}: {usage:.0f}/{cap:.0f} ({util:.1f}%)")
            
        # Dashboard
        print("\n📋 Capacity Planning Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │              Capacity Planning Overview                     │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Services Modeled:   {stats['total_services']:>10}                        │")
        print(f"  │ Active Forecasts:   {stats['total_forecasts']:>10}                        │")
        print(f"  │ Bottlenecks:        {stats['active_bottlenecks']:>10}                        │")
        print(f"  │ Recommendations:    {stats['recommendations']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Current Cost:       ${projection.current_monthly_cost:>9,.2f}/month          │")
        print(f"  │ 12-month Forecast:  ${projection.total_projected_cost:>9,.2f} total          │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Capacity Planning Platform initialized!")
    print("=" * 60)
