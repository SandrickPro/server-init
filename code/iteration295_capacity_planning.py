#!/usr/bin/env python3
"""
Server Init - Iteration 295: Capacity Planning Platform
Платформа Capacity Planning

Функционал:
- Resource Forecasting - прогнозирование ресурсов
- Capacity Analysis - анализ ёмкости
- Demand Prediction - предсказание спроса
- Scaling Recommendations - рекомендации по масштабированию
- Trend Analysis - анализ трендов
- Bottleneck Detection - обнаружение узких мест
- Growth Planning - планирование роста
- SLA Management - управление SLA
"""

import asyncio
import random
import math
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import uuid


class ResourceCategory(Enum):
    """Категория ресурса"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    CONNECTIONS = "connections"
    IOPS = "iops"


class TrendDirection(Enum):
    """Направление тренда"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"


class ScalingType(Enum):
    """Тип масштабирования"""
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    BOTH = "both"


class AlertPriority(Enum):
    """Приоритет алерта"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ResourceMetric:
    """Метрика ресурса"""
    timestamp: datetime
    value: float
    capacity: float
    utilization: float


@dataclass
class Resource:
    """Ресурс"""
    resource_id: str
    name: str
    category: ResourceCategory
    
    # Capacity
    current_capacity: float = 0.0
    max_capacity: float = 0.0
    unit: str = ""
    
    # Usage
    current_usage: float = 0.0
    peak_usage: float = 0.0
    avg_usage: float = 0.0
    
    # History
    metrics: List[ResourceMetric] = field(default_factory=list)
    
    # Thresholds
    warning_threshold: float = 70.0
    critical_threshold: float = 85.0


@dataclass
class CapacityForecast:
    """Прогноз ёмкости"""
    forecast_id: str
    resource_id: str
    
    # Predictions
    days_7: float = 0.0
    days_14: float = 0.0
    days_30: float = 0.0
    days_90: float = 0.0
    
    # Exhaustion
    exhaustion_date: Optional[datetime] = None
    
    # Trend
    trend: TrendDirection = TrendDirection.STABLE
    growth_rate: float = 0.0
    
    # Confidence
    confidence: float = 0.0
    
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ScalingRecommendation:
    """Рекомендация по масштабированию"""
    rec_id: str
    resource_id: str
    
    # Type
    scaling_type: ScalingType = ScalingType.HORIZONTAL
    
    # Recommendation
    action: str = ""
    reason: str = ""
    
    # Target
    current_value: float = 0.0
    recommended_value: float = 0.0
    
    # Impact
    cost_impact: float = 0.0
    performance_impact: str = ""
    
    # Priority
    priority: AlertPriority = AlertPriority.MEDIUM
    
    # Status
    applied: bool = False


@dataclass
class Bottleneck:
    """Узкое место"""
    bottleneck_id: str
    
    # Resource
    resource_id: str
    resource_name: str
    category: ResourceCategory
    
    # Details
    severity: AlertPriority = AlertPriority.MEDIUM
    utilization: float = 0.0
    
    # Impact
    affected_services: List[str] = field(default_factory=list)
    impact_description: str = ""
    
    # Resolution
    resolution: str = ""
    estimated_fix_time: str = ""
    
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class GrowthPlan:
    """План роста"""
    plan_id: str
    name: str
    
    # Timeline
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    
    # Growth targets
    cpu_growth: float = 0.0
    memory_growth: float = 0.0
    storage_growth: float = 0.0
    
    # Resources needed
    additional_resources: Dict[str, float] = field(default_factory=dict)
    
    # Cost
    estimated_cost: float = 0.0
    
    # Status
    status: str = "draft"


@dataclass
class SLATarget:
    """SLA цель"""
    sla_id: str
    name: str
    
    # Target
    metric: str = ""
    target_value: float = 0.0
    unit: str = ""
    
    # Current
    current_value: float = 0.0
    
    # Period
    period_days: int = 30
    
    # Status
    meeting_sla: bool = True
    
    # Risk
    at_risk: bool = False


class CapacityPlanningManager:
    """Менеджер Capacity Planning"""
    
    def __init__(self):
        self.resources: Dict[str, Resource] = {}
        self.forecasts: Dict[str, CapacityForecast] = {}
        self.recommendations: Dict[str, ScalingRecommendation] = {}
        self.bottlenecks: Dict[str, Bottleneck] = {}
        self.growth_plans: Dict[str, GrowthPlan] = {}
        self.sla_targets: Dict[str, SLATarget] = {}
        
        # Stats
        self.forecasts_generated: int = 0
        self.recommendations_generated: int = 0
        
    async def add_resource(self, name: str,
                          category: ResourceCategory,
                          current_capacity: float,
                          max_capacity: float,
                          unit: str = "",
                          warning_threshold: float = 70.0,
                          critical_threshold: float = 85.0) -> Resource:
        """Добавление ресурса"""
        resource = Resource(
            resource_id=f"res_{uuid.uuid4().hex[:8]}",
            name=name,
            category=category,
            current_capacity=current_capacity,
            max_capacity=max_capacity,
            unit=unit,
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold
        )
        
        self.resources[resource.resource_id] = resource
        return resource
        
    async def record_metric(self, resource_id: str, value: float) -> Optional[ResourceMetric]:
        """Запись метрики"""
        resource = self.resources.get(resource_id)
        if not resource:
            return None
            
        utilization = (value / resource.current_capacity * 100) if resource.current_capacity > 0 else 0
        
        metric = ResourceMetric(
            timestamp=datetime.now(),
            value=value,
            capacity=resource.current_capacity,
            utilization=utilization
        )
        
        resource.metrics.append(metric)
        resource.current_usage = value
        
        # Update peak
        if value > resource.peak_usage:
            resource.peak_usage = value
            
        # Update average
        if resource.metrics:
            resource.avg_usage = sum(m.value for m in resource.metrics) / len(resource.metrics)
            
        # Keep only last 1000 metrics
        if len(resource.metrics) > 1000:
            resource.metrics = resource.metrics[-1000:]
            
        return metric
        
    async def generate_forecast(self, resource_id: str) -> Optional[CapacityForecast]:
        """Генерация прогноза"""
        resource = self.resources.get(resource_id)
        if not resource or len(resource.metrics) < 10:
            return None
            
        self.forecasts_generated += 1
        
        # Calculate trend
        recent = resource.metrics[-min(100, len(resource.metrics)):]
        
        if len(recent) >= 2:
            first_half = recent[:len(recent)//2]
            second_half = recent[len(recent)//2:]
            
            avg_first = sum(m.value for m in first_half) / len(first_half)
            avg_second = sum(m.value for m in second_half) / len(second_half)
            
            change = (avg_second - avg_first) / avg_first * 100 if avg_first > 0 else 0
            
            if change > 5:
                trend = TrendDirection.INCREASING
            elif change < -5:
                trend = TrendDirection.DECREASING
            else:
                trend = TrendDirection.STABLE
        else:
            trend = TrendDirection.STABLE
            change = 0
            
        # Predict future values
        current = resource.current_usage
        daily_growth = current * (change / 100 / 30)  # Daily growth rate
        
        forecast = CapacityForecast(
            forecast_id=f"forecast_{uuid.uuid4().hex[:8]}",
            resource_id=resource_id,
            days_7=current + daily_growth * 7,
            days_14=current + daily_growth * 14,
            days_30=current + daily_growth * 30,
            days_90=current + daily_growth * 90,
            trend=trend,
            growth_rate=change,
            confidence=random.uniform(70, 95)
        )
        
        # Calculate exhaustion date
        if daily_growth > 0:
            remaining = resource.current_capacity - current
            days_to_exhaust = remaining / daily_growth if daily_growth > 0 else float('inf')
            
            if days_to_exhaust < 365:
                forecast.exhaustion_date = datetime.now() + timedelta(days=int(days_to_exhaust))
                
        self.forecasts[forecast.forecast_id] = forecast
        return forecast
        
    async def analyze_capacity(self, resource_id: str) -> Dict[str, Any]:
        """Анализ ёмкости"""
        resource = self.resources.get(resource_id)
        if not resource:
            return {}
            
        utilization = (resource.current_usage / resource.current_capacity * 100) if resource.current_capacity > 0 else 0
        headroom = resource.current_capacity - resource.current_usage
        
        # Status
        if utilization >= resource.critical_threshold:
            status = "critical"
        elif utilization >= resource.warning_threshold:
            status = "warning"
        else:
            status = "healthy"
            
        # Peak analysis
        peak_util = (resource.peak_usage / resource.current_capacity * 100) if resource.current_capacity > 0 else 0
        
        return {
            "resource_id": resource_id,
            "name": resource.name,
            "category": resource.category.value,
            "current_usage": resource.current_usage,
            "capacity": resource.current_capacity,
            "utilization": utilization,
            "headroom": headroom,
            "peak_usage": resource.peak_usage,
            "peak_utilization": peak_util,
            "avg_usage": resource.avg_usage,
            "status": status
        }
        
    async def generate_recommendations(self) -> List[ScalingRecommendation]:
        """Генерация рекомендаций"""
        recommendations = []
        
        for resource in self.resources.values():
            utilization = (resource.current_usage / resource.current_capacity * 100) if resource.current_capacity > 0 else 0
            
            if utilization >= resource.critical_threshold:
                # Need immediate scaling
                rec = await self._create_scaling_recommendation(
                    resource,
                    "Urgent capacity increase required",
                    AlertPriority.CRITICAL,
                    increase_percent=50
                )
                recommendations.append(rec)
                
            elif utilization >= resource.warning_threshold:
                # Proactive scaling
                rec = await self._create_scaling_recommendation(
                    resource,
                    "Proactive capacity increase recommended",
                    AlertPriority.HIGH,
                    increase_percent=30
                )
                recommendations.append(rec)
                
            elif utilization < 30 and resource.current_capacity > resource.max_capacity * 0.5:
                # Possible over-provisioning
                rec = await self._create_scaling_recommendation(
                    resource,
                    "Resource appears over-provisioned",
                    AlertPriority.LOW,
                    increase_percent=-20
                )
                recommendations.append(rec)
                
        return recommendations
        
    async def _create_scaling_recommendation(self, resource: Resource,
                                            reason: str,
                                            priority: AlertPriority,
                                            increase_percent: float) -> ScalingRecommendation:
        """Создание рекомендации"""
        self.recommendations_generated += 1
        
        new_capacity = resource.current_capacity * (1 + increase_percent / 100)
        
        # Determine scaling type
        if resource.category == ResourceCategory.CPU:
            scaling_type = ScalingType.BOTH
        elif resource.category == ResourceCategory.STORAGE:
            scaling_type = ScalingType.VERTICAL
        else:
            scaling_type = ScalingType.HORIZONTAL
            
        rec = ScalingRecommendation(
            rec_id=f"rec_{uuid.uuid4().hex[:8]}",
            resource_id=resource.resource_id,
            scaling_type=scaling_type,
            action=f"Scale {'up' if increase_percent > 0 else 'down'} {resource.name}",
            reason=reason,
            current_value=resource.current_capacity,
            recommended_value=new_capacity,
            cost_impact=abs(new_capacity - resource.current_capacity) * random.uniform(0.01, 0.1),
            performance_impact="Improved" if increase_percent > 0 else "Maintained",
            priority=priority
        )
        
        self.recommendations[rec.rec_id] = rec
        return rec
        
    async def detect_bottlenecks(self) -> List[Bottleneck]:
        """Обнаружение узких мест"""
        bottlenecks = []
        
        for resource in self.resources.values():
            utilization = (resource.current_usage / resource.current_capacity * 100) if resource.current_capacity > 0 else 0
            
            if utilization >= resource.critical_threshold:
                severity = AlertPriority.CRITICAL
            elif utilization >= resource.warning_threshold:
                severity = AlertPriority.HIGH
            else:
                continue
                
            bottleneck = Bottleneck(
                bottleneck_id=f"bn_{uuid.uuid4().hex[:8]}",
                resource_id=resource.resource_id,
                resource_name=resource.name,
                category=resource.category,
                severity=severity,
                utilization=utilization,
                affected_services=[f"service-{i}" for i in range(random.randint(1, 5))],
                impact_description=f"{resource.category.value} constraint affecting performance",
                resolution=f"Increase {resource.category.value} capacity",
                estimated_fix_time="1-2 hours"
            )
            
            self.bottlenecks[bottleneck.bottleneck_id] = bottleneck
            bottlenecks.append(bottleneck)
            
        return bottlenecks
        
    async def create_growth_plan(self, name: str,
                                duration_days: int,
                                cpu_growth: float = 0.0,
                                memory_growth: float = 0.0,
                                storage_growth: float = 0.0) -> GrowthPlan:
        """Создание плана роста"""
        plan = GrowthPlan(
            plan_id=f"plan_{uuid.uuid4().hex[:8]}",
            name=name,
            end_date=datetime.now() + timedelta(days=duration_days),
            cpu_growth=cpu_growth,
            memory_growth=memory_growth,
            storage_growth=storage_growth
        )
        
        # Calculate additional resources
        for resource in self.resources.values():
            if resource.category == ResourceCategory.CPU and cpu_growth > 0:
                additional = resource.current_capacity * (cpu_growth / 100)
                plan.additional_resources[resource.name] = additional
                plan.estimated_cost += additional * random.uniform(10, 50)
                
            elif resource.category == ResourceCategory.MEMORY and memory_growth > 0:
                additional = resource.current_capacity * (memory_growth / 100)
                plan.additional_resources[resource.name] = additional
                plan.estimated_cost += additional * random.uniform(0.001, 0.01)
                
            elif resource.category == ResourceCategory.STORAGE and storage_growth > 0:
                additional = resource.current_capacity * (storage_growth / 100)
                plan.additional_resources[resource.name] = additional
                plan.estimated_cost += additional * random.uniform(0.0001, 0.001)
                
        self.growth_plans[plan.plan_id] = plan
        return plan
        
    async def add_sla_target(self, name: str,
                            metric: str,
                            target_value: float,
                            unit: str = "",
                            period_days: int = 30) -> SLATarget:
        """Добавление SLA цели"""
        sla = SLATarget(
            sla_id=f"sla_{uuid.uuid4().hex[:8]}",
            name=name,
            metric=metric,
            target_value=target_value,
            unit=unit,
            period_days=period_days,
            current_value=target_value * random.uniform(0.9, 1.1)
        )
        
        sla.meeting_sla = sla.current_value >= sla.target_value
        sla.at_risk = not sla.meeting_sla or sla.current_value < sla.target_value * 1.05
        
        self.sla_targets[sla.sla_id] = sla
        return sla
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        critical_resources = sum(1 for r in self.resources.values()
                                if (r.current_usage / r.current_capacity * 100) >= r.critical_threshold
                                if r.current_capacity > 0)
        warning_resources = sum(1 for r in self.resources.values()
                               if r.critical_threshold > (r.current_usage / r.current_capacity * 100) >= r.warning_threshold
                               if r.current_capacity > 0)
                               
        sla_met = sum(1 for s in self.sla_targets.values() if s.meeting_sla)
        
        return {
            "total_resources": len(self.resources),
            "critical_resources": critical_resources,
            "warning_resources": warning_resources,
            "bottlenecks": len(self.bottlenecks),
            "forecasts": len(self.forecasts),
            "recommendations": len(self.recommendations),
            "growth_plans": len(self.growth_plans),
            "sla_targets": len(self.sla_targets),
            "sla_met": sla_met,
            "forecasts_generated": self.forecasts_generated,
            "recommendations_generated": self.recommendations_generated
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 295: Capacity Planning Platform")
    print("=" * 60)
    
    manager = CapacityPlanningManager()
    print("✓ Capacity Planning Manager created")
    
    # Add resources
    print("\n📊 Adding Resources...")
    
    resources_data = [
        ("CPU Cluster A", ResourceCategory.CPU, 64, 128, "cores"),
        ("CPU Cluster B", ResourceCategory.CPU, 48, 96, "cores"),
        ("Memory Pool A", ResourceCategory.MEMORY, 256, 512, "GB"),
        ("Memory Pool B", ResourceCategory.MEMORY, 128, 256, "GB"),
        ("Storage SSD", ResourceCategory.STORAGE, 5000, 10000, "GB"),
        ("Storage HDD", ResourceCategory.STORAGE, 20000, 50000, "GB"),
        ("Network Bandwidth", ResourceCategory.NETWORK, 10, 40, "Gbps"),
        ("Database Connections", ResourceCategory.CONNECTIONS, 500, 1000, "conn"),
        ("Storage IOPS", ResourceCategory.IOPS, 50000, 100000, "IOPS")
    ]
    
    resources = []
    for name, category, capacity, max_cap, unit in resources_data:
        resource = await manager.add_resource(name, category, capacity, max_cap, unit)
        resources.append(resource)
        print(f"  📊 {name}: {capacity}/{max_cap} {unit}")
        
    # Record metrics (simulate usage)
    print("\n📈 Recording Metrics...")
    
    usage_patterns = {
        ResourceCategory.CPU: (0.6, 0.9),
        ResourceCategory.MEMORY: (0.5, 0.85),
        ResourceCategory.STORAGE: (0.4, 0.7),
        ResourceCategory.NETWORK: (0.3, 0.8),
        ResourceCategory.CONNECTIONS: (0.5, 0.9),
        ResourceCategory.IOPS: (0.4, 0.85)
    }
    
    for resource in resources:
        low, high = usage_patterns.get(resource.category, (0.3, 0.7))
        
        # Generate historical data
        for i in range(50):
            usage = resource.current_capacity * random.uniform(low, high)
            await manager.record_metric(resource.resource_id, usage)
            
    print(f"  📈 Recorded metrics for {len(resources)} resources")
    
    # Generate forecasts
    print("\n🔮 Generating Forecasts...")
    
    for resource in resources[:5]:
        forecast = await manager.generate_forecast(resource.resource_id)
        if forecast:
            trend_icon = {"increasing": "📈", "decreasing": "📉", "stable": "➡️"}.get(forecast.trend.value, "❓")
            print(f"\n  🔮 {resource.name}:")
            print(f"     Trend: {trend_icon} {forecast.trend.value} ({forecast.growth_rate:+.1f}%)")
            print(f"     7-day: {forecast.days_7:.1f} {resource.unit}")
            print(f"     30-day: {forecast.days_30:.1f} {resource.unit}")
            
            if forecast.exhaustion_date:
                days_left = (forecast.exhaustion_date - datetime.now()).days
                print(f"     ⚠️ Exhaustion in {days_left} days")
                
    # Analyze capacity
    print("\n📊 Capacity Analysis:")
    
    print("\n  ┌────────────────────────┬────────────┬────────────┬────────────┬────────────┐")
    print("  │ Resource               │ Usage      │ Capacity   │ Utiliz.    │ Status     │")
    print("  ├────────────────────────┼────────────┼────────────┼────────────┼────────────┤")
    
    for resource in resources:
        analysis = await manager.analyze_capacity(resource.resource_id)
        
        name = resource.name[:22].ljust(22)
        usage = f"{analysis['current_usage']:.1f}".ljust(10)
        capacity = f"{analysis['capacity']:.1f}".ljust(10)
        util = f"{analysis['utilization']:.1f}%".ljust(10)
        
        status_icons = {"healthy": "🟢", "warning": "🟡", "critical": "🔴"}
        status = f"{status_icons.get(analysis['status'], '⚪')} {analysis['status']}".ljust(10)
        
        print(f"  │ {name} │ {usage} │ {capacity} │ {util} │ {status} │")
        
    print("  └────────────────────────┴────────────┴────────────┴────────────┴────────────┘")
    
    # Detect bottlenecks
    print("\n🚧 Detecting Bottlenecks...")
    
    bottlenecks = await manager.detect_bottlenecks()
    
    if bottlenecks:
        for bn in bottlenecks[:5]:
            severity_icons = {
                AlertPriority.LOW: "🟢",
                AlertPriority.MEDIUM: "🟡",
                AlertPriority.HIGH: "🟠",
                AlertPriority.CRITICAL: "🔴"
            }
            icon = severity_icons.get(bn.severity, "⚪")
            print(f"\n  {icon} {bn.resource_name} ({bn.utilization:.1f}%)")
            print(f"     Impact: {bn.impact_description}")
            print(f"     Resolution: {bn.resolution}")
    else:
        print("  ✅ No bottlenecks detected")
        
    # Generate recommendations
    print("\n💡 Scaling Recommendations:")
    
    recommendations = await manager.generate_recommendations()
    
    if recommendations:
        for rec in sorted(recommendations, key=lambda x: x.priority.value, reverse=True)[:5]:
            priority_icons = {
                AlertPriority.LOW: "🟢",
                AlertPriority.MEDIUM: "🟡",
                AlertPriority.HIGH: "🟠",
                AlertPriority.CRITICAL: "🔴"
            }
            icon = priority_icons.get(rec.priority, "⚪")
            resource = manager.resources.get(rec.resource_id)
            
            print(f"\n  {icon} [{rec.priority.value.upper()}] {rec.action}")
            print(f"     Reason: {rec.reason}")
            print(f"     Current: {rec.current_value:.1f} → Recommended: {rec.recommended_value:.1f}")
            print(f"     Type: {rec.scaling_type.value}")
            print(f"     Cost Impact: ${rec.cost_impact:.2f}/month")
    else:
        print("  ✅ No immediate scaling needed")
        
    # Create growth plan
    print("\n📈 Creating Growth Plan...")
    
    plan = await manager.create_growth_plan(
        "Q1 Growth Plan",
        duration_days=90,
        cpu_growth=30,
        memory_growth=25,
        storage_growth=50
    )
    
    print(f"\n  📈 {plan.name}")
    print(f"     Duration: 90 days")
    print(f"     CPU Growth: {plan.cpu_growth}%")
    print(f"     Memory Growth: {plan.memory_growth}%")
    print(f"     Storage Growth: {plan.storage_growth}%")
    print(f"     Estimated Cost: ${plan.estimated_cost:.2f}")
    
    if plan.additional_resources:
        print("     Additional Resources:")
        for name, amount in list(plan.additional_resources.items())[:5]:
            print(f"       - {name}: +{amount:.1f}")
            
    # Add SLA targets
    print("\n🎯 SLA Targets...")
    
    sla_data = [
        ("CPU Availability", "availability", 99.9, "%"),
        ("Memory Response Time", "response_time", 100, "ms"),
        ("Storage Latency", "latency", 10, "ms"),
        ("Network Uptime", "uptime", 99.95, "%")
    ]
    
    for name, metric, target, unit in sla_data:
        sla = await manager.add_sla_target(name, metric, target, unit)
        status = "✅" if sla.meeting_sla else "❌"
        risk = "⚠️" if sla.at_risk else ""
        print(f"  {status} {name}: {sla.current_value:.2f}/{sla.target_value} {unit} {risk}")
        
    # Resource utilization chart
    print("\n📊 Resource Utilization:")
    
    for resource in resources[:6]:
        util = (resource.current_usage / resource.current_capacity * 100) if resource.current_capacity > 0 else 0
        bar_len = 30
        filled = int(util / 100 * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        
        color = "🟢" if util < 70 else "🟡" if util < 85 else "🔴"
        
        name = resource.name[:15].ljust(15)
        print(f"  {name} [{bar}] {util:5.1f}% {color}")
        
    # Statistics
    print("\n📊 Capacity Planning Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Total Resources: {stats['total_resources']}")
    print(f"  Critical Resources: {stats['critical_resources']}")
    print(f"  Warning Resources: {stats['warning_resources']}")
    print(f"\n  Active Bottlenecks: {stats['bottlenecks']}")
    print(f"  Forecasts Generated: {stats['forecasts_generated']}")
    print(f"  Recommendations: {stats['recommendations']}")
    print(f"\n  SLA Targets: {stats['sla_targets']}")
    print(f"  SLA Met: {stats['sla_met']}/{stats['sla_targets']}")
    
    health_rate = (stats['total_resources'] - stats['critical_resources'] - stats['warning_resources']) / max(stats['total_resources'], 1) * 100
    sla_rate = stats['sla_met'] / max(stats['sla_targets'], 1) * 100
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Capacity Planning Dashboard                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Resources:               {stats['total_resources']:>12}                        │")
    print(f"│ Critical Resources:            {stats['critical_resources']:>12}                        │")
    print(f"│ Active Bottlenecks:            {stats['bottlenecks']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Resource Health Rate:          {health_rate:>11.1f}%                        │")
    print(f"│ SLA Compliance Rate:           {sla_rate:>11.1f}%                        │")
    print(f"│ Open Recommendations:          {stats['recommendations']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Capacity Planning Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
