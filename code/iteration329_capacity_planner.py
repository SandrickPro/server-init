#!/usr/bin/env python3
"""
Server Init - Iteration 329: Capacity Planning Platform
Платформа планирования ёмкости инфраструктуры

Функционал:
- Resource Forecasting - прогнозирование ресурсов
- Capacity Modeling - моделирование ёмкости
- Demand Analysis - анализ спроса
- Growth Planning - планирование роста
- Bottleneck Detection - обнаружение узких мест
- Scaling Recommendations - рекомендации по масштабированию
- What-If Analysis - анализ сценариев
- Capacity Reporting - отчётность по ёмкости
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
    GPU = "gpu"
    IOPS = "iops"


class CapacityStatus(Enum):
    """Статус ёмкости"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    EXHAUSTED = "exhausted"


class TrendDirection(Enum):
    """Направление тренда"""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"
    VOLATILE = "volatile"


class ScalingStrategy(Enum):
    """Стратегия масштабирования"""
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    HYBRID = "hybrid"


class ForecastMethod(Enum):
    """Метод прогнозирования"""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    SEASONAL = "seasonal"
    ML_BASED = "ml_based"


@dataclass
class ResourceMetric:
    """Метрика ресурса"""
    metric_id: str
    resource_id: str
    
    # Type
    resource_type: ResourceType = ResourceType.CPU
    
    # Values
    current_value: float = 0.0
    max_capacity: float = 100.0
    unit: str = "%"
    
    # Utilization
    utilization_percent: float = 0.0
    
    # Thresholds
    warning_threshold: float = 70.0
    critical_threshold: float = 85.0
    
    # Timestamp
    collected_at: datetime = field(default_factory=datetime.now)


@dataclass
class CapacityPool:
    """Пул ёмкости"""
    pool_id: str
    name: str
    
    # Type
    resource_type: ResourceType = ResourceType.CPU
    
    # Capacity
    total_capacity: float = 0.0
    allocated_capacity: float = 0.0
    reserved_capacity: float = 0.0
    available_capacity: float = 0.0
    
    # Unit
    unit: str = "cores"
    
    # Members
    member_ids: List[str] = field(default_factory=list)
    
    # Thresholds
    warning_threshold: float = 70.0
    critical_threshold: float = 85.0
    
    # Status
    status: CapacityStatus = CapacityStatus.HEALTHY
    
    # Location
    region: str = ""
    availability_zone: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class UsageHistory:
    """История использования"""
    history_id: str
    resource_id: str
    
    # Type
    resource_type: ResourceType = ResourceType.CPU
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Values
    avg_value: float = 0.0
    max_value: float = 0.0
    min_value: float = 0.0
    p95_value: float = 0.0
    p99_value: float = 0.0
    
    # Data points
    data_points: List[Tuple[datetime, float]] = field(default_factory=list)


@dataclass
class Forecast:
    """Прогноз"""
    forecast_id: str
    
    # Target
    resource_id: str = ""
    pool_id: str = ""
    resource_type: ResourceType = ResourceType.CPU
    
    # Method
    method: ForecastMethod = ForecastMethod.LINEAR
    
    # Period
    forecast_start: datetime = field(default_factory=datetime.now)
    forecast_end: datetime = field(default_factory=datetime.now)
    
    # Predictions
    predicted_values: List[Tuple[datetime, float]] = field(default_factory=list)
    
    # Confidence
    confidence_level: float = 0.95
    upper_bound: List[float] = field(default_factory=list)
    lower_bound: List[float] = field(default_factory=list)
    
    # Accuracy
    mape: float = 0.0  # Mean Absolute Percentage Error
    
    # Capacity exhaustion
    exhaustion_date: Optional[datetime] = None
    
    # Timestamps
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class DemandPattern:
    """Паттерн спроса"""
    pattern_id: str
    name: str
    
    # Type
    pattern_type: str = "daily"  # daily, weekly, monthly, seasonal
    
    # Resource
    resource_type: ResourceType = ResourceType.CPU
    
    # Pattern data
    peak_hours: List[int] = field(default_factory=list)
    low_hours: List[int] = field(default_factory=list)
    peak_days: List[int] = field(default_factory=list)  # 0=Monday
    
    # Multipliers
    peak_multiplier: float = 1.5
    low_multiplier: float = 0.5
    
    # Seasonality
    seasonal_factors: Dict[str, float] = field(default_factory=dict)
    
    # Description
    description: str = ""


@dataclass
class Bottleneck:
    """Узкое место"""
    bottleneck_id: str
    
    # Resource
    resource_id: str = ""
    resource_type: ResourceType = ResourceType.CPU
    
    # Severity
    severity: CapacityStatus = CapacityStatus.WARNING
    
    # Details
    description: str = ""
    impact: str = ""
    
    # Utilization
    current_utilization: float = 0.0
    threshold: float = 0.0
    
    # Affected
    affected_services: List[str] = field(default_factory=list)
    
    # Recommendation
    recommendation: str = ""
    
    # Timestamps
    detected_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


@dataclass
class ScalingRecommendation:
    """Рекомендация по масштабированию"""
    recommendation_id: str
    
    # Target
    resource_id: str = ""
    pool_id: str = ""
    
    # Strategy
    strategy: ScalingStrategy = ScalingStrategy.HORIZONTAL
    
    # Current
    current_capacity: float = 0.0
    current_utilization: float = 0.0
    
    # Recommended
    recommended_capacity: float = 0.0
    scale_factor: float = 1.0
    
    # Timing
    urgency: str = "medium"  # low, medium, high, critical
    recommended_date: datetime = field(default_factory=datetime.now)
    
    # Cost
    estimated_cost: float = 0.0
    cost_per_unit: float = 0.0
    
    # Justification
    reason: str = ""
    
    # Status
    status: str = "open"  # open, approved, implemented, dismissed


@dataclass
class WhatIfScenario:
    """Сценарий What-If"""
    scenario_id: str
    name: str
    
    # Description
    description: str = ""
    
    # Parameters
    growth_rate: float = 0.0  # Monthly percentage
    new_workloads: List[Dict[str, Any]] = field(default_factory=list)
    removed_workloads: List[str] = field(default_factory=list)
    
    # Time horizon
    horizon_months: int = 12
    
    # Results
    capacity_projections: Dict[str, List[float]] = field(default_factory=dict)
    exhaustion_dates: Dict[str, Optional[datetime]] = field(default_factory=dict)
    
    # Requirements
    additional_capacity_needed: Dict[str, float] = field(default_factory=dict)
    estimated_cost: float = 0.0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CapacityReport:
    """Отчёт по ёмкости"""
    report_id: str
    name: str
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Summary
    total_pools: int = 0
    healthy_pools: int = 0
    warning_pools: int = 0
    critical_pools: int = 0
    
    # Utilization
    avg_utilization: Dict[str, float] = field(default_factory=dict)
    max_utilization: Dict[str, float] = field(default_factory=dict)
    
    # Trends
    trends: Dict[str, TrendDirection] = field(default_factory=dict)
    
    # Bottlenecks
    active_bottlenecks: int = 0
    
    # Recommendations
    open_recommendations: int = 0
    
    # Generated
    generated_at: datetime = field(default_factory=datetime.now)


class CapacityPlanner:
    """Планировщик ёмкости"""
    
    def __init__(self):
        self.pools: Dict[str, CapacityPool] = {}
        self.metrics: Dict[str, ResourceMetric] = {}
        self.history: Dict[str, List[UsageHistory]] = {}
        self.forecasts: Dict[str, Forecast] = {}
        self.patterns: Dict[str, DemandPattern] = {}
        self.bottlenecks: Dict[str, Bottleneck] = {}
        self.recommendations: Dict[str, ScalingRecommendation] = {}
        self.scenarios: Dict[str, WhatIfScenario] = {}
        self.reports: Dict[str, CapacityReport] = {}
        
    async def create_pool(self, name: str,
                         resource_type: ResourceType,
                         total_capacity: float,
                         unit: str,
                         region: str = "",
                         warning_threshold: float = 70.0,
                         critical_threshold: float = 85.0) -> CapacityPool:
        """Создание пула ёмкости"""
        pool = CapacityPool(
            pool_id=f"pool_{uuid.uuid4().hex[:8]}",
            name=name,
            resource_type=resource_type,
            total_capacity=total_capacity,
            available_capacity=total_capacity,
            unit=unit,
            region=region,
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold
        )
        
        self.pools[pool.pool_id] = pool
        return pool
        
    async def allocate_capacity(self, pool_id: str,
                               amount: float,
                               member_id: str = "") -> bool:
        """Выделение ёмкости"""
        pool = self.pools.get(pool_id)
        if not pool:
            return False
            
        if amount > pool.available_capacity:
            return False
            
        pool.allocated_capacity += amount
        pool.available_capacity = pool.total_capacity - pool.allocated_capacity - pool.reserved_capacity
        
        if member_id:
            pool.member_ids.append(member_id)
            
        await self._update_pool_status(pool)
        pool.last_updated = datetime.now()
        
        return True
        
    async def release_capacity(self, pool_id: str,
                              amount: float,
                              member_id: str = "") -> bool:
        """Освобождение ёмкости"""
        pool = self.pools.get(pool_id)
        if not pool:
            return False
            
        pool.allocated_capacity = max(0, pool.allocated_capacity - amount)
        pool.available_capacity = pool.total_capacity - pool.allocated_capacity - pool.reserved_capacity
        
        if member_id and member_id in pool.member_ids:
            pool.member_ids.remove(member_id)
            
        await self._update_pool_status(pool)
        pool.last_updated = datetime.now()
        
        return True
        
    async def reserve_capacity(self, pool_id: str,
                              amount: float) -> bool:
        """Резервирование ёмкости"""
        pool = self.pools.get(pool_id)
        if not pool:
            return False
            
        if amount > pool.available_capacity:
            return False
            
        pool.reserved_capacity += amount
        pool.available_capacity = pool.total_capacity - pool.allocated_capacity - pool.reserved_capacity
        
        await self._update_pool_status(pool)
        return True
        
    async def _update_pool_status(self, pool: CapacityPool):
        """Обновление статуса пула"""
        utilization = (pool.allocated_capacity / pool.total_capacity * 100) if pool.total_capacity > 0 else 0
        
        if utilization >= 95:
            pool.status = CapacityStatus.EXHAUSTED
        elif utilization >= pool.critical_threshold:
            pool.status = CapacityStatus.CRITICAL
        elif utilization >= pool.warning_threshold:
            pool.status = CapacityStatus.WARNING
        else:
            pool.status = CapacityStatus.HEALTHY
            
        # Check for bottlenecks
        if pool.status in [CapacityStatus.CRITICAL, CapacityStatus.EXHAUSTED]:
            await self._create_bottleneck(pool, utilization)
            
    async def _create_bottleneck(self, pool: CapacityPool,
                                utilization: float):
        """Создание записи об узком месте"""
        # Check if bottleneck already exists
        for b in self.bottlenecks.values():
            if b.resource_id == pool.pool_id and not b.resolved_at:
                return
                
        bottleneck = Bottleneck(
            bottleneck_id=f"bn_{uuid.uuid4().hex[:8]}",
            resource_id=pool.pool_id,
            resource_type=pool.resource_type,
            severity=pool.status,
            description=f"Pool '{pool.name}' at {utilization:.1f}% utilization",
            impact=f"May affect performance of {len(pool.member_ids)} resources",
            current_utilization=utilization,
            threshold=pool.critical_threshold,
            recommendation=f"Consider scaling {pool.resource_type.value} capacity"
        )
        
        self.bottlenecks[bottleneck.bottleneck_id] = bottleneck
        
    async def record_metric(self, pool_id: str,
                           current_value: float) -> Optional[ResourceMetric]:
        """Запись метрики"""
        pool = self.pools.get(pool_id)
        if not pool:
            return None
            
        metric = ResourceMetric(
            metric_id=f"metric_{uuid.uuid4().hex[:8]}",
            resource_id=pool_id,
            resource_type=pool.resource_type,
            current_value=current_value,
            max_capacity=pool.total_capacity,
            unit=pool.unit,
            utilization_percent=(current_value / pool.total_capacity * 100) if pool.total_capacity > 0 else 0,
            warning_threshold=pool.warning_threshold,
            critical_threshold=pool.critical_threshold
        )
        
        self.metrics[metric.metric_id] = metric
        
        # Update history
        if pool_id not in self.history:
            self.history[pool_id] = []
            
        return metric
        
    async def add_usage_history(self, pool_id: str,
                               period_hours: int = 24) -> Optional[UsageHistory]:
        """Добавление истории использования"""
        pool = self.pools.get(pool_id)
        if not pool:
            return None
            
        # Generate synthetic data points
        now = datetime.now()
        data_points = []
        values = []
        
        for i in range(period_hours):
            timestamp = now - timedelta(hours=period_hours - i)
            # Simulate usage pattern
            base_usage = pool.allocated_capacity / pool.total_capacity * 100
            variation = random.uniform(-10, 10)
            value = max(0, min(100, base_usage + variation))
            data_points.append((timestamp, value))
            values.append(value)
            
        history = UsageHistory(
            history_id=f"hist_{uuid.uuid4().hex[:8]}",
            resource_id=pool_id,
            resource_type=pool.resource_type,
            period_start=now - timedelta(hours=period_hours),
            period_end=now,
            avg_value=sum(values) / len(values) if values else 0,
            max_value=max(values) if values else 0,
            min_value=min(values) if values else 0,
            p95_value=sorted(values)[int(len(values) * 0.95)] if values else 0,
            p99_value=sorted(values)[int(len(values) * 0.99)] if values else 0,
            data_points=data_points
        )
        
        if pool_id not in self.history:
            self.history[pool_id] = []
        self.history[pool_id].append(history)
        
        return history
        
    async def generate_forecast(self, pool_id: str,
                               forecast_days: int = 30,
                               method: ForecastMethod = ForecastMethod.LINEAR) -> Optional[Forecast]:
        """Генерация прогноза"""
        pool = self.pools.get(pool_id)
        if not pool:
            return None
            
        now = datetime.now()
        current_utilization = (pool.allocated_capacity / pool.total_capacity * 100) if pool.total_capacity > 0 else 0
        
        # Generate predictions based on method
        predictions = []
        upper_bounds = []
        lower_bounds = []
        
        # Simulate growth rate
        daily_growth = random.uniform(0.1, 0.5)  # 0.1-0.5% daily growth
        
        for day in range(forecast_days):
            future_date = now + timedelta(days=day)
            
            if method == ForecastMethod.LINEAR:
                predicted = current_utilization + (daily_growth * day)
            elif method == ForecastMethod.EXPONENTIAL:
                predicted = current_utilization * (1 + daily_growth / 100) ** day
            else:
                predicted = current_utilization + (daily_growth * day)
                
            predicted = min(100, predicted)
            margin = predicted * 0.1  # 10% confidence interval
            
            predictions.append((future_date, predicted))
            upper_bounds.append(min(100, predicted + margin))
            lower_bounds.append(max(0, predicted - margin))
            
        # Calculate exhaustion date
        exhaustion_date = None
        for date, value in predictions:
            if value >= 95:
                exhaustion_date = date
                break
                
        forecast = Forecast(
            forecast_id=f"fc_{uuid.uuid4().hex[:8]}",
            pool_id=pool_id,
            resource_type=pool.resource_type,
            method=method,
            forecast_start=now,
            forecast_end=now + timedelta(days=forecast_days),
            predicted_values=predictions,
            upper_bound=upper_bounds,
            lower_bound=lower_bounds,
            exhaustion_date=exhaustion_date,
            mape=random.uniform(3, 8)  # Simulated error
        )
        
        self.forecasts[forecast.forecast_id] = forecast
        
        # Create scaling recommendation if needed
        if exhaustion_date and (exhaustion_date - now).days < 30:
            await self._create_scaling_recommendation(pool, forecast)
            
        return forecast
        
    async def _create_scaling_recommendation(self, pool: CapacityPool,
                                            forecast: Forecast):
        """Создание рекомендации по масштабированию"""
        current_utilization = (pool.allocated_capacity / pool.total_capacity * 100)
        
        # Calculate recommended capacity (20% buffer)
        recommended_capacity = pool.total_capacity * 1.2
        scale_factor = recommended_capacity / pool.total_capacity
        
        urgency = "low"
        if forecast.exhaustion_date:
            days_until = (forecast.exhaustion_date - datetime.now()).days
            if days_until < 7:
                urgency = "critical"
            elif days_until < 14:
                urgency = "high"
            elif days_until < 30:
                urgency = "medium"
                
        rec = ScalingRecommendation(
            recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
            pool_id=pool.pool_id,
            strategy=ScalingStrategy.HORIZONTAL if pool.resource_type == ResourceType.CPU else ScalingStrategy.VERTICAL,
            current_capacity=pool.total_capacity,
            current_utilization=current_utilization,
            recommended_capacity=recommended_capacity,
            scale_factor=scale_factor,
            urgency=urgency,
            recommended_date=datetime.now() + timedelta(days=7),
            estimated_cost=random.uniform(500, 5000),
            reason=f"Capacity exhaustion predicted in {(forecast.exhaustion_date - datetime.now()).days if forecast.exhaustion_date else 'N/A'} days"
        )
        
        self.recommendations[rec.recommendation_id] = rec
        
    async def define_demand_pattern(self, name: str,
                                   pattern_type: str,
                                   resource_type: ResourceType,
                                   peak_hours: List[int] = None,
                                   low_hours: List[int] = None,
                                   peak_days: List[int] = None,
                                   peak_multiplier: float = 1.5,
                                   low_multiplier: float = 0.5) -> DemandPattern:
        """Определение паттерна спроса"""
        pattern = DemandPattern(
            pattern_id=f"pat_{uuid.uuid4().hex[:8]}",
            name=name,
            pattern_type=pattern_type,
            resource_type=resource_type,
            peak_hours=peak_hours or [9, 10, 11, 14, 15, 16],
            low_hours=low_hours or [0, 1, 2, 3, 4, 5],
            peak_days=peak_days or [1, 2, 3],  # Tue, Wed, Thu
            peak_multiplier=peak_multiplier,
            low_multiplier=low_multiplier
        )
        
        self.patterns[pattern.pattern_id] = pattern
        return pattern
        
    async def create_scenario(self, name: str,
                             description: str,
                             growth_rate: float,
                             horizon_months: int = 12,
                             new_workloads: List[Dict[str, Any]] = None) -> WhatIfScenario:
        """Создание сценария What-If"""
        scenario = WhatIfScenario(
            scenario_id=f"sc_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            growth_rate=growth_rate,
            horizon_months=horizon_months,
            new_workloads=new_workloads or []
        )
        
        # Calculate projections
        await self._calculate_scenario_projections(scenario)
        
        self.scenarios[scenario.scenario_id] = scenario
        return scenario
        
    async def _calculate_scenario_projections(self, scenario: WhatIfScenario):
        """Расчёт проекций сценария"""
        for pool in self.pools.values():
            projections = []
            current = (pool.allocated_capacity / pool.total_capacity * 100)
            
            for month in range(scenario.horizon_months):
                growth = current * (1 + scenario.growth_rate / 100) ** month
                
                # Add workload impact
                for workload in scenario.new_workloads:
                    if workload.get('resource_type') == pool.resource_type.value:
                        growth += workload.get('capacity_impact', 0)
                        
                projections.append(min(100, growth))
                
            scenario.capacity_projections[pool.pool_id] = projections
            
            # Check exhaustion
            for i, value in enumerate(projections):
                if value >= 95:
                    scenario.exhaustion_dates[pool.pool_id] = datetime.now() + timedelta(days=i * 30)
                    break
                    
            # Calculate additional capacity needed
            if projections[-1] > 80:
                needed = (projections[-1] - 80) / 100 * pool.total_capacity
                scenario.additional_capacity_needed[pool.pool_id] = needed
                scenario.estimated_cost += needed * random.uniform(10, 50)
                
    async def resolve_bottleneck(self, bottleneck_id: str) -> bool:
        """Разрешение узкого места"""
        bottleneck = self.bottlenecks.get(bottleneck_id)
        if not bottleneck:
            return False
            
        bottleneck.resolved_at = datetime.now()
        return True
        
    async def approve_recommendation(self, recommendation_id: str) -> bool:
        """Утверждение рекомендации"""
        rec = self.recommendations.get(recommendation_id)
        if not rec:
            return False
            
        rec.status = "approved"
        return True
        
    async def implement_recommendation(self, recommendation_id: str) -> bool:
        """Применение рекомендации"""
        rec = self.recommendations.get(recommendation_id)
        if not rec:
            return False
            
        pool = self.pools.get(rec.pool_id)
        if pool:
            pool.total_capacity = rec.recommended_capacity
            pool.available_capacity = pool.total_capacity - pool.allocated_capacity - pool.reserved_capacity
            await self._update_pool_status(pool)
            
        rec.status = "implemented"
        return True
        
    async def generate_report(self, name: str,
                             period_days: int = 30) -> CapacityReport:
        """Генерация отчёта"""
        now = datetime.now()
        
        report = CapacityReport(
            report_id=f"rpt_{uuid.uuid4().hex[:8]}",
            name=name,
            period_start=now - timedelta(days=period_days),
            period_end=now,
            total_pools=len(self.pools)
        )
        
        # Count by status
        for pool in self.pools.values():
            if pool.status == CapacityStatus.HEALTHY:
                report.healthy_pools += 1
            elif pool.status == CapacityStatus.WARNING:
                report.warning_pools += 1
            elif pool.status in [CapacityStatus.CRITICAL, CapacityStatus.EXHAUSTED]:
                report.critical_pools += 1
                
            # Utilization
            resource_type = pool.resource_type.value
            utilization = (pool.allocated_capacity / pool.total_capacity * 100) if pool.total_capacity > 0 else 0
            
            if resource_type not in report.avg_utilization:
                report.avg_utilization[resource_type] = []
            report.avg_utilization[resource_type] = utilization
            
            report.max_utilization[resource_type] = max(
                report.max_utilization.get(resource_type, 0),
                utilization
            )
            
            # Trends
            report.trends[resource_type] = random.choice(list(TrendDirection))
            
        # Bottlenecks
        report.active_bottlenecks = sum(1 for b in self.bottlenecks.values() if not b.resolved_at)
        
        # Recommendations
        report.open_recommendations = sum(1 for r in self.recommendations.values() if r.status == "open")
        
        self.reports[report.report_id] = report
        return report
        
    def get_pool_utilization(self, pool_id: str) -> float:
        """Получение утилизации пула"""
        pool = self.pools.get(pool_id)
        if not pool or pool.total_capacity == 0:
            return 0.0
        return (pool.allocated_capacity / pool.total_capacity) * 100
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_pools = len(self.pools)
        
        by_status = {status.value: 0 for status in CapacityStatus}
        by_type = {rtype.value: 0 for rtype in ResourceType}
        
        total_capacity = {}
        used_capacity = {}
        
        for pool in self.pools.values():
            by_status[pool.status.value] += 1
            by_type[pool.resource_type.value] += 1
            
            rtype = pool.resource_type.value
            total_capacity[rtype] = total_capacity.get(rtype, 0) + pool.total_capacity
            used_capacity[rtype] = used_capacity.get(rtype, 0) + pool.allocated_capacity
            
        active_bottlenecks = sum(1 for b in self.bottlenecks.values() if not b.resolved_at)
        open_recommendations = sum(1 for r in self.recommendations.values() if r.status == "open")
        
        return {
            "total_pools": total_pools,
            "pools_by_status": by_status,
            "pools_by_type": by_type,
            "total_capacity": total_capacity,
            "used_capacity": used_capacity,
            "total_forecasts": len(self.forecasts),
            "total_patterns": len(self.patterns),
            "active_bottlenecks": active_bottlenecks,
            "open_recommendations": open_recommendations,
            "total_scenarios": len(self.scenarios)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 329: Capacity Planning Platform")
    print("=" * 60)
    
    planner = CapacityPlanner()
    print("✓ Capacity Planner created")
    
    # Create capacity pools
    print("\n📦 Creating Capacity Pools...")
    
    pools_data = [
        ("Production CPU Pool", ResourceType.CPU, 1000, "cores", "us-east-1"),
        ("Production Memory Pool", ResourceType.MEMORY, 4096, "GB", "us-east-1"),
        ("Production Storage Pool", ResourceType.STORAGE, 100000, "GB", "us-east-1"),
        ("Production Network Pool", ResourceType.NETWORK, 100, "Gbps", "us-east-1"),
        ("GPU Compute Pool", ResourceType.GPU, 64, "GPUs", "us-east-1"),
        ("Development CPU Pool", ResourceType.CPU, 500, "cores", "us-west-2"),
        ("Development Memory Pool", ResourceType.MEMORY, 2048, "GB", "us-west-2"),
        ("Staging CPU Pool", ResourceType.CPU, 200, "cores", "eu-west-1"),
        ("Analytics Storage Pool", ResourceType.STORAGE, 500000, "GB", "us-east-1"),
        ("IOPS Pool", ResourceType.IOPS, 100000, "IOPS", "us-east-1")
    ]
    
    pools = []
    for name, rtype, capacity, unit, region in pools_data:
        pool = await planner.create_pool(name, rtype, capacity, unit, region)
        pools.append(pool)
        print(f"  📦 {name}: {capacity} {unit}")
        
    # Allocate capacity
    print("\n⚡ Allocating Capacity...")
    
    allocations = [
        (0, 750, "web-cluster"),  # Production CPU - 75%
        (1, 3200, "app-servers"),  # Production Memory - 78%
        (2, 70000, "data-volumes"),  # Production Storage - 70%
        (3, 60, "load-balancers"),  # Network - 60%
        (4, 55, "ml-training"),  # GPU - 86%
        (5, 350, "dev-workloads"),  # Dev CPU - 70%
        (6, 1400, "dev-apps"),  # Dev Memory - 68%
        (7, 150, "staging-apps"),  # Staging CPU - 75%
        (8, 400000, "analytics-data"),  # Analytics Storage - 80%
        (9, 85000, "database-io")  # IOPS - 85%
    ]
    
    for pool_idx, amount, member in allocations:
        await planner.allocate_capacity(pools[pool_idx].pool_id, amount, member)
        
    print(f"  ✓ Allocated capacity across {len(pools)} pools")
    
    # Record metrics
    print("\n📊 Recording Metrics...")
    
    for pool in pools:
        await planner.record_metric(pool.pool_id, pool.allocated_capacity)
        
    print(f"  ✓ Recorded metrics for {len(pools)} pools")
    
    # Add usage history
    print("\n📈 Generating Usage History...")
    
    for pool in pools:
        await planner.add_usage_history(pool.pool_id, 24)
        
    print(f"  ✓ Generated 24-hour history for {len(pools)} pools")
    
    # Generate forecasts
    print("\n🔮 Generating Forecasts...")
    
    forecasts = []
    for pool in pools:
        forecast = await planner.generate_forecast(pool.pool_id, 30, ForecastMethod.LINEAR)
        if forecast:
            forecasts.append(forecast)
            
    print(f"  ✓ Generated {len(forecasts)} forecasts")
    
    # Define demand patterns
    print("\n📉 Defining Demand Patterns...")
    
    patterns_data = [
        ("Business Hours Pattern", "daily", ResourceType.CPU, [9, 10, 11, 14, 15, 16], [0, 1, 2, 3, 4, 5]),
        ("Weekly Peak", "weekly", ResourceType.CPU, None, None, [1, 2, 3]),
        ("Month-End Batch", "monthly", ResourceType.STORAGE, [22, 23], [8, 9, 10])
    ]
    
    patterns = []
    for name, ptype, rtype, peak_h, low_h, *rest in patterns_data:
        peak_d = rest[0] if rest else None
        pattern = await planner.define_demand_pattern(name, ptype, rtype, peak_h, low_h, peak_d)
        patterns.append(pattern)
        print(f"  📉 {name}")
        
    # Create what-if scenarios
    print("\n🎯 Creating What-If Scenarios...")
    
    scenarios_data = [
        ("Organic Growth 10%", "10% monthly growth projection", 10, 12, []),
        ("New Product Launch", "Launch of new product line", 5, 6, [
            {"resource_type": "cpu", "capacity_impact": 20},
            {"resource_type": "memory", "capacity_impact": 15}
        ]),
        ("ML Expansion", "Expansion of ML workloads", 8, 12, [
            {"resource_type": "gpu", "capacity_impact": 30}
        ]),
        ("Conservative Growth", "Conservative 3% growth", 3, 12, [])
    ]
    
    scenarios = []
    for name, desc, growth, horizon, workloads in scenarios_data:
        scenario = await planner.create_scenario(name, desc, growth, horizon, workloads)
        scenarios.append(scenario)
        print(f"  🎯 {name}: {growth}% growth")
        
    # Generate report
    print("\n📋 Generating Capacity Report...")
    
    report = await planner.generate_report("Monthly Capacity Report", 30)
    print(f"  ✓ Report generated")
    
    # Pool status
    print("\n📦 Capacity Pool Status:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Pool Name                    │ Type     │ Total      │ Allocated  │ Available  │ Util%   │ Status      │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for pool in pools:
        name = pool.name[:28].ljust(28)
        rtype = pool.resource_type.value[:8].ljust(8)
        total = f"{pool.total_capacity:,.0f}".ljust(10)
        allocated = f"{pool.allocated_capacity:,.0f}".ljust(10)
        available = f"{pool.available_capacity:,.0f}".ljust(10)
        
        util_pct = (pool.allocated_capacity / pool.total_capacity * 100)
        util = f"{util_pct:.1f}%".ljust(7)
        
        status_icons = {
            "healthy": "✓ OK",
            "warning": "⚠ Warn",
            "critical": "✗ Crit",
            "exhausted": "🚨 Full"
        }
        status = status_icons.get(pool.status.value, pool.status.value)[:11].ljust(11)
        
        print(f"  │ {name} │ {rtype} │ {total} │ {allocated} │ {available} │ {util} │ {status} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Utilization by type
    print("\n📊 Utilization by Resource Type:")
    
    stats = planner.get_statistics()
    
    for rtype in ResourceType:
        type_pools = [p for p in pools if p.resource_type == rtype]
        if type_pools:
            total = sum(p.total_capacity for p in type_pools)
            allocated = sum(p.allocated_capacity for p in type_pools)
            util_pct = (allocated / total * 100) if total > 0 else 0
            
            bar_len = int(util_pct / 2.5)
            bar = "█" * bar_len + "░" * (40 - bar_len)
            
            status = "✓" if util_pct < 70 else "⚠" if util_pct < 85 else "✗"
            print(f"  {status} {rtype.value:10} [{bar}] {util_pct:.1f}%")
            
    # Forecasts
    print("\n🔮 Capacity Forecasts (30-day):")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Pool Name                    │ Current  │ Predicted │ Exhaustion Date │ Confidence   │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for forecast in forecasts:
        pool = planner.pools.get(forecast.pool_id)
        if pool:
            name = pool.name[:28].ljust(28)
            current = f"{(pool.allocated_capacity / pool.total_capacity * 100):.1f}%".ljust(8)
            
            final_prediction = forecast.predicted_values[-1][1] if forecast.predicted_values else 0
            predicted = f"{final_prediction:.1f}%".ljust(9)
            
            if forecast.exhaustion_date:
                exhaustion = forecast.exhaustion_date.strftime("%Y-%m-%d").ljust(15)
            else:
                exhaustion = "N/A".ljust(15)
                
            confidence = f"±{forecast.mape:.1f}%".ljust(12)
            
            print(f"  │ {name} │ {current} │ {predicted} │ {exhaustion} │ {confidence} │")
            
    print("  └────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Bottlenecks
    print("\n🚨 Active Bottlenecks:")
    
    active_bottlenecks = [b for b in planner.bottlenecks.values() if not b.resolved_at]
    if active_bottlenecks:
        for bn in active_bottlenecks:
            severity_icon = {"warning": "⚠", "critical": "✗", "exhausted": "🚨"}.get(bn.severity.value, "?")
            print(f"  {severity_icon} {bn.description}")
            print(f"    Impact: {bn.impact}")
            print(f"    Recommendation: {bn.recommendation}")
    else:
        print("  ✓ No active bottlenecks")
        
    # Scaling recommendations
    print("\n💡 Scaling Recommendations:")
    
    open_recs = [r for r in planner.recommendations.values() if r.status == "open"]
    
    if open_recs:
        print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────┐")
        print("  │ Pool                         │ Strategy   │ Current    │ Recommended │ Urgency  │ Est. Cost    │")
        print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────┤")
        
        for rec in open_recs:
            pool = planner.pools.get(rec.pool_id)
            pool_name = pool.name[:28].ljust(28) if pool else "Unknown".ljust(28)
            strategy = rec.strategy.value[:10].ljust(10)
            current = f"{rec.current_capacity:,.0f}".ljust(10)
            recommended = f"{rec.recommended_capacity:,.0f}".ljust(11)
            
            urgency_icons = {"low": "○", "medium": "◐", "high": "⚠", "critical": "🚨"}
            urgency = f"{urgency_icons.get(rec.urgency, '?')} {rec.urgency}"[:8].ljust(8)
            
            cost = f"${rec.estimated_cost:,.0f}".ljust(12)
            
            print(f"  │ {pool_name} │ {strategy} │ {current} │ {recommended} │ {urgency} │ {cost} │")
            
        print("  └────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    else:
        print("  ✓ No pending recommendations")
        
    # What-If Scenarios
    print("\n🎯 What-If Scenarios:")
    
    for scenario in scenarios:
        print(f"\n  📌 {scenario.name}")
        print(f"     Growth Rate: {scenario.growth_rate}% monthly")
        print(f"     Horizon: {scenario.horizon_months} months")
        
        if scenario.exhaustion_dates:
            exhaustion_pools = [p for p, d in scenario.exhaustion_dates.items() if d]
            if exhaustion_pools:
                print(f"     ⚠ Pools reaching exhaustion: {len(exhaustion_pools)}")
                
        if scenario.additional_capacity_needed:
            print(f"     Additional capacity needed:")
            for pool_id, amount in list(scenario.additional_capacity_needed.items())[:3]:
                pool = planner.pools.get(pool_id)
                if pool:
                    print(f"       - {pool.name}: {amount:,.0f} {pool.unit}")
                    
        print(f"     Estimated Cost: ${scenario.estimated_cost:,.0f}")
        
    # Demand patterns
    print("\n📉 Demand Patterns:")
    
    for pattern in patterns:
        print(f"\n  📉 {pattern.name}")
        print(f"     Type: {pattern.pattern_type}")
        print(f"     Resource: {pattern.resource_type.value}")
        print(f"     Peak Hours: {pattern.peak_hours}")
        print(f"     Peak Multiplier: {pattern.peak_multiplier}x")
        
    # Report summary
    print("\n📋 Capacity Report Summary:")
    
    print(f"\n  Period: {report.period_start.strftime('%Y-%m-%d')} - {report.period_end.strftime('%Y-%m-%d')}")
    print(f"\n  Pool Status:")
    print(f"    ✓ Healthy: {report.healthy_pools}")
    print(f"    ⚠ Warning: {report.warning_pools}")
    print(f"    ✗ Critical: {report.critical_pools}")
    
    print(f"\n  Active Bottlenecks: {report.active_bottlenecks}")
    print(f"  Open Recommendations: {report.open_recommendations}")
    
    # Overall statistics
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Total Pools: {stats['total_pools']}")
    print(f"  Total Forecasts: {stats['total_forecasts']}")
    print(f"  Total Patterns: {stats['total_patterns']}")
    print(f"  Total Scenarios: {stats['total_scenarios']}")
    print(f"  Active Bottlenecks: {stats['active_bottlenecks']}")
    print(f"  Open Recommendations: {stats['open_recommendations']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Capacity Planning Platform                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Capacity Pools:         {stats['total_pools']:>12}                      │")
    print(f"│ Healthy Pools:                {stats['pools_by_status'].get('healthy', 0):>12}                      │")
    print(f"│ Warning/Critical Pools:       {stats['pools_by_status'].get('warning', 0) + stats['pools_by_status'].get('critical', 0):>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Active Bottlenecks:           {stats['active_bottlenecks']:>12}                      │")
    print(f"│ Open Recommendations:         {stats['open_recommendations']:>12}                      │")
    print(f"│ What-If Scenarios:            {stats['total_scenarios']:>12}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Capacity Planning Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
