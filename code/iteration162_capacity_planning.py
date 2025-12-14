#!/usr/bin/env python3
"""
Server Init - Iteration 162: Capacity Planning Platform
Платформа планирования ёмкости

Функционал:
- Resource Forecasting - прогнозирование ресурсов
- Demand Analysis - анализ потребности
- Growth Planning - планирование роста
- Cost Projection - проекция затрат
- Performance Modeling - моделирование производительности
- Scaling Recommendations - рекомендации по масштабированию
- Bottleneck Detection - обнаружение узких мест
- Capacity Reports - отчёты о ёмкости
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


class ResourceCategory(Enum):
    """Категория ресурса"""
    COMPUTE = "compute"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"


class TimeGranularity(Enum):
    """Гранулярность времени"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TrendType(Enum):
    """Тип тренда"""
    STABLE = "stable"
    GROWING = "growing"
    DECLINING = "declining"
    SEASONAL = "seasonal"
    SPIKE = "spike"


class AlertLevel(Enum):
    """Уровень алерта"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


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
    resource_id: str = ""
    category: ResourceCategory = ResourceCategory.COMPUTE
    
    # Current values
    current_value: float = 0.0
    max_capacity: float = 100.0
    
    # Historical
    historical_data: List[Tuple[datetime, float]] = field(default_factory=list)
    
    # Metadata
    unit: str = ""
    name: str = ""


@dataclass
class UsagePattern:
    """Паттерн использования"""
    pattern_id: str
    resource_id: str = ""
    
    # Pattern info
    trend_type: TrendType = TrendType.STABLE
    
    # Statistics
    avg_usage: float = 0.0
    peak_usage: float = 0.0
    min_usage: float = 0.0
    std_deviation: float = 0.0
    
    # Growth
    growth_rate: float = 0.0  # percentage per period
    
    # Seasonality
    has_seasonality: bool = False
    seasonal_peaks: List[str] = field(default_factory=list)  # time periods


@dataclass
class CapacityForecast:
    """Прогноз ёмкости"""
    forecast_id: str
    resource_id: str = ""
    
    # Method
    method: ForecastMethod = ForecastMethod.LINEAR
    
    # Predictions
    predictions: List[Tuple[datetime, float]] = field(default_factory=list)
    
    # Confidence
    confidence_level: float = 0.95
    upper_bound: List[float] = field(default_factory=list)
    lower_bound: List[float] = field(default_factory=list)
    
    # Timeline
    forecast_horizon_days: int = 90
    
    # Exhaustion
    exhaustion_date: Optional[datetime] = None
    days_until_exhaustion: int = -1
    
    # Created
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ScalingRecommendation:
    """Рекомендация по масштабированию"""
    recommendation_id: str
    resource_id: str = ""
    
    # Action
    action: str = ""  # scale_up, scale_down, add_capacity, optimize
    priority: AlertLevel = AlertLevel.INFO
    
    # Details
    current_capacity: float = 0.0
    recommended_capacity: float = 0.0
    
    # Timing
    when: str = ""  # immediate, 7_days, 30_days, 90_days
    
    # Cost impact
    cost_delta: float = 0.0
    
    # Reason
    reason: str = ""


@dataclass
class Bottleneck:
    """Узкое место"""
    bottleneck_id: str
    resource_id: str = ""
    
    # Info
    category: ResourceCategory = ResourceCategory.COMPUTE
    component: str = ""
    
    # Severity
    severity: AlertLevel = AlertLevel.WARNING
    
    # Metrics
    current_utilization: float = 0.0
    threshold: float = 80.0
    
    # Impact
    affected_services: List[str] = field(default_factory=list)
    
    # Recommendation
    recommendation: str = ""
    
    # Detected
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class CostProjection:
    """Проекция затрат"""
    projection_id: str
    
    # Current
    current_monthly_cost: float = 0.0
    
    # Projections
    projections: Dict[str, float] = field(default_factory=dict)  # period: cost
    
    # Breakdown
    by_category: Dict[str, float] = field(default_factory=dict)
    by_resource: Dict[str, float] = field(default_factory=dict)
    
    # Growth
    cost_growth_rate: float = 0.0


@dataclass
class CapacityPlan:
    """План ёмкости"""
    plan_id: str
    name: str = ""
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Resources
    resources: Dict[str, Dict] = field(default_factory=dict)
    
    # Forecasts
    forecasts: List[CapacityForecast] = field(default_factory=list)
    
    # Recommendations
    recommendations: List[ScalingRecommendation] = field(default_factory=list)
    
    # Budget
    total_budget: float = 0.0
    projected_cost: float = 0.0
    
    # Status
    status: str = "draft"  # draft, approved, in_progress, completed


class MetricsCollector:
    """Сборщик метрик"""
    
    def __init__(self):
        self.metrics: Dict[str, ResourceMetric] = {}
        
    def register_resource(self, resource_id: str, name: str,
                          category: ResourceCategory,
                          max_capacity: float, unit: str) -> ResourceMetric:
        """Регистрация ресурса"""
        metric = ResourceMetric(
            metric_id=f"metric_{uuid.uuid4().hex[:8]}",
            resource_id=resource_id,
            category=category,
            max_capacity=max_capacity,
            unit=unit,
            name=name
        )
        self.metrics[resource_id] = metric
        return metric
        
    def record_metric(self, resource_id: str, value: float,
                       timestamp: Optional[datetime] = None):
        """Запись метрики"""
        if resource_id not in self.metrics:
            return
            
        metric = self.metrics[resource_id]
        metric.current_value = value
        
        ts = timestamp or datetime.now()
        metric.historical_data.append((ts, value))
        
        # Keep last 1000 points
        if len(metric.historical_data) > 1000:
            metric.historical_data = metric.historical_data[-1000:]
            
    def generate_sample_data(self, resource_id: str, days: int = 30,
                              trend: TrendType = TrendType.GROWING):
        """Генерация тестовых данных"""
        if resource_id not in self.metrics:
            return
            
        metric = self.metrics[resource_id]
        base_value = metric.max_capacity * 0.4  # 40% base utilization
        
        for day in range(days):
            for hour in range(24):
                ts = datetime.now() - timedelta(days=days-day, hours=24-hour)
                
                # Base value with trend
                if trend == TrendType.GROWING:
                    value = base_value * (1 + (day / days) * 0.3)
                elif trend == TrendType.DECLINING:
                    value = base_value * (1 - (day / days) * 0.2)
                elif trend == TrendType.SEASONAL:
                    value = base_value * (1 + 0.2 * math.sin(2 * math.pi * hour / 24))
                else:
                    value = base_value
                    
                # Add noise
                noise = random.gauss(0, base_value * 0.1)
                value = max(0, min(metric.max_capacity, value + noise))
                
                # Add daily pattern
                if 9 <= hour <= 18:  # Business hours
                    value *= 1.3
                    
                self.record_metric(resource_id, value, ts)


class PatternAnalyzer:
    """Анализатор паттернов"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        
    def analyze_pattern(self, resource_id: str) -> Optional[UsagePattern]:
        """Анализ паттерна использования"""
        metric = self.collector.metrics.get(resource_id)
        
        if not metric or not metric.historical_data:
            return None
            
        values = [v for _, v in metric.historical_data]
        
        pattern = UsagePattern(
            pattern_id=f"pattern_{uuid.uuid4().hex[:8]}",
            resource_id=resource_id
        )
        
        # Calculate statistics
        pattern.avg_usage = sum(values) / len(values)
        pattern.peak_usage = max(values)
        pattern.min_usage = min(values)
        
        # Standard deviation
        variance = sum((v - pattern.avg_usage) ** 2 for v in values) / len(values)
        pattern.std_deviation = math.sqrt(variance)
        
        # Determine trend
        if len(values) >= 2:
            first_half = values[:len(values)//2]
            second_half = values[len(values)//2:]
            
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            
            change = (second_avg - first_avg) / first_avg if first_avg > 0 else 0
            
            if change > 0.1:
                pattern.trend_type = TrendType.GROWING
                pattern.growth_rate = change * 100
            elif change < -0.1:
                pattern.trend_type = TrendType.DECLINING
                pattern.growth_rate = change * 100
            else:
                pattern.trend_type = TrendType.STABLE
                pattern.growth_rate = 0
                
        # Check seasonality
        if len(values) >= 48:  # At least 2 days
            hourly_avgs = {}
            for i, (ts, v) in enumerate(metric.historical_data):
                hour = ts.hour
                if hour not in hourly_avgs:
                    hourly_avgs[hour] = []
                hourly_avgs[hour].append(v)
                
            avg_by_hour = {h: sum(vs)/len(vs) for h, vs in hourly_avgs.items()}
            
            overall_avg = pattern.avg_usage
            max_deviation = max(abs(v - overall_avg) / overall_avg 
                              for v in avg_by_hour.values()) if overall_avg > 0 else 0
                              
            if max_deviation > 0.2:  # 20% deviation indicates seasonality
                pattern.has_seasonality = True
                peak_hours = [h for h, v in avg_by_hour.items() 
                            if v > overall_avg * 1.1]
                pattern.seasonal_peaks = [f"{h}:00" for h in sorted(peak_hours)]
                
        return pattern


class Forecaster:
    """Прогнозировщик"""
    
    def __init__(self, collector: MetricsCollector, analyzer: PatternAnalyzer):
        self.collector = collector
        self.analyzer = analyzer
        
    def forecast(self, resource_id: str, horizon_days: int = 90,
                  method: ForecastMethod = ForecastMethod.LINEAR) -> Optional[CapacityForecast]:
        """Прогнозирование"""
        metric = self.collector.metrics.get(resource_id)
        
        if not metric or len(metric.historical_data) < 24:
            return None
            
        pattern = self.analyzer.analyze_pattern(resource_id)
        
        forecast = CapacityForecast(
            forecast_id=f"forecast_{uuid.uuid4().hex[:8]}",
            resource_id=resource_id,
            method=method,
            forecast_horizon_days=horizon_days
        )
        
        values = [v for _, v in metric.historical_data]
        current_avg = sum(values[-24:]) / 24 if len(values) >= 24 else sum(values) / len(values)
        
        # Generate predictions
        for day in range(horizon_days):
            pred_date = datetime.now() + timedelta(days=day)
            
            if method == ForecastMethod.LINEAR:
                growth = pattern.growth_rate / 100 if pattern else 0
                pred_value = current_avg * (1 + growth * day / 30)
            elif method == ForecastMethod.EXPONENTIAL:
                growth = pattern.growth_rate / 100 if pattern else 0
                pred_value = current_avg * math.exp(growth * day / 30)
            else:
                pred_value = current_avg
                
            pred_value = min(pred_value, metric.max_capacity * 1.5)
            forecast.predictions.append((pred_date, pred_value))
            
            # Confidence bounds
            std = pattern.std_deviation if pattern else current_avg * 0.1
            forecast.upper_bound.append(pred_value + 2 * std)
            forecast.lower_bound.append(pred_value - 2 * std)
            
        # Calculate exhaustion date
        for pred_date, pred_value in forecast.predictions:
            if pred_value >= metric.max_capacity * 0.9:
                forecast.exhaustion_date = pred_date
                forecast.days_until_exhaustion = (pred_date - datetime.now()).days
                break
                
        return forecast


class BottleneckDetector:
    """Детектор узких мест"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self.thresholds = {
            ResourceCategory.COMPUTE: 80,
            ResourceCategory.MEMORY: 85,
            ResourceCategory.STORAGE: 90,
            ResourceCategory.NETWORK: 75,
            ResourceCategory.DATABASE: 80,
        }
        
    def detect_bottlenecks(self) -> List[Bottleneck]:
        """Обнаружение узких мест"""
        bottlenecks = []
        
        for resource_id, metric in self.collector.metrics.items():
            threshold = self.thresholds.get(metric.category, 80)
            utilization = (metric.current_value / metric.max_capacity * 100) \
                         if metric.max_capacity > 0 else 0
                         
            if utilization >= threshold:
                severity = AlertLevel.CRITICAL if utilization >= 95 else AlertLevel.WARNING
                
                bottleneck = Bottleneck(
                    bottleneck_id=f"bn_{uuid.uuid4().hex[:8]}",
                    resource_id=resource_id,
                    category=metric.category,
                    component=metric.name,
                    severity=severity,
                    current_utilization=utilization,
                    threshold=threshold,
                    recommendation=self._get_recommendation(metric.category, utilization)
                )
                bottlenecks.append(bottleneck)
                
        return bottlenecks
        
    def _get_recommendation(self, category: ResourceCategory, utilization: float) -> str:
        """Получение рекомендации"""
        if utilization >= 95:
            action = "Immediate scaling required"
        else:
            action = "Plan scaling within 7 days"
            
        recommendations = {
            ResourceCategory.COMPUTE: f"{action}. Consider adding more CPU cores or instances.",
            ResourceCategory.MEMORY: f"{action}. Increase RAM allocation or optimize memory usage.",
            ResourceCategory.STORAGE: f"{action}. Add storage capacity or implement data archiving.",
            ResourceCategory.NETWORK: f"{action}. Upgrade network bandwidth or add load balancers.",
            ResourceCategory.DATABASE: f"{action}. Scale database or implement read replicas.",
        }
        
        return recommendations.get(category, action)


class RecommendationEngine:
    """Движок рекомендаций"""
    
    def __init__(self, collector: MetricsCollector, forecaster: Forecaster,
                 detector: BottleneckDetector):
        self.collector = collector
        self.forecaster = forecaster
        self.detector = detector
        
        # Cost per unit by category
        self.costs = {
            ResourceCategory.COMPUTE: 50,   # $ per core per month
            ResourceCategory.MEMORY: 10,    # $ per GB per month
            ResourceCategory.STORAGE: 0.5,  # $ per GB per month
            ResourceCategory.NETWORK: 0.1,  # $ per GB transferred
            ResourceCategory.DATABASE: 100, # $ per instance per month
        }
        
    def generate_recommendations(self) -> List[ScalingRecommendation]:
        """Генерация рекомендаций"""
        recommendations = []
        
        for resource_id, metric in self.collector.metrics.items():
            forecast = self.forecaster.forecast(resource_id)
            
            if not forecast:
                continue
                
            # Check if scaling needed
            utilization = metric.current_value / metric.max_capacity * 100
            
            if utilization >= 90:
                rec = self._create_scale_recommendation(
                    metric, "immediate", AlertLevel.CRITICAL
                )
                recommendations.append(rec)
            elif forecast.exhaustion_date:
                days = forecast.days_until_exhaustion
                
                if days <= 7:
                    priority = AlertLevel.CRITICAL
                    when = "7_days"
                elif days <= 30:
                    priority = AlertLevel.WARNING
                    when = "30_days"
                else:
                    priority = AlertLevel.INFO
                    when = "90_days"
                    
                rec = self._create_scale_recommendation(metric, when, priority)
                recommendations.append(rec)
            elif utilization < 30:
                # Underutilized - can scale down
                rec = ScalingRecommendation(
                    recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
                    resource_id=resource_id,
                    action="scale_down",
                    priority=AlertLevel.INFO,
                    current_capacity=metric.max_capacity,
                    recommended_capacity=metric.max_capacity * 0.5,
                    when="30_days",
                    cost_delta=-self.costs.get(metric.category, 0) * 0.5,
                    reason=f"Resource underutilized at {utilization:.1f}%"
                )
                recommendations.append(rec)
                
        return recommendations
        
    def _create_scale_recommendation(self, metric: ResourceMetric,
                                      when: str, priority: AlertLevel) -> ScalingRecommendation:
        """Создание рекомендации по масштабированию"""
        scale_factor = 1.5 if priority == AlertLevel.CRITICAL else 1.3
        new_capacity = metric.max_capacity * scale_factor
        
        cost_delta = self.costs.get(metric.category, 0) * (scale_factor - 1)
        
        return ScalingRecommendation(
            recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
            resource_id=metric.resource_id,
            action="scale_up",
            priority=priority,
            current_capacity=metric.max_capacity,
            recommended_capacity=new_capacity,
            when=when,
            cost_delta=cost_delta,
            reason=f"Capacity exhaustion predicted. Scale up {metric.name}."
        )


class CostAnalyzer:
    """Анализатор затрат"""
    
    def __init__(self, collector: MetricsCollector,
                 recommendation_engine: RecommendationEngine):
        self.collector = collector
        self.engine = recommendation_engine
        
    def project_costs(self, months: int = 12) -> CostProjection:
        """Проекция затрат"""
        projection = CostProjection(
            projection_id=f"proj_{uuid.uuid4().hex[:8]}"
        )
        
        # Calculate current costs
        current_cost = 0
        by_category: Dict[str, float] = {}
        by_resource: Dict[str, float] = {}
        
        for resource_id, metric in self.collector.metrics.items():
            cost = self.engine.costs.get(metric.category, 0) * metric.max_capacity
            current_cost += cost
            
            cat = metric.category.value
            by_category[cat] = by_category.get(cat, 0) + cost
            by_resource[resource_id] = cost
            
        projection.current_monthly_cost = current_cost
        projection.by_category = by_category
        projection.by_resource = by_resource
        
        # Project future costs
        growth_rate = 0.05  # 5% monthly growth assumption
        
        for month in range(1, months + 1):
            future_cost = current_cost * (1 + growth_rate) ** month
            projection.projections[f"month_{month}"] = future_cost
            
        projection.cost_growth_rate = growth_rate * 100
        
        return projection


class PlanBuilder:
    """Строитель плана ёмкости"""
    
    def __init__(self, collector: MetricsCollector, forecaster: Forecaster,
                 recommendation_engine: RecommendationEngine, cost_analyzer: CostAnalyzer):
        self.collector = collector
        self.forecaster = forecaster
        self.recommendation_engine = recommendation_engine
        self.cost_analyzer = cost_analyzer
        
    def create_plan(self, name: str, period_days: int = 90,
                     budget: float = 0) -> CapacityPlan:
        """Создание плана ёмкости"""
        plan = CapacityPlan(
            plan_id=f"plan_{uuid.uuid4().hex[:8]}",
            name=name,
            period_start=datetime.now(),
            period_end=datetime.now() + timedelta(days=period_days),
            total_budget=budget
        )
        
        # Add resources
        for resource_id, metric in self.collector.metrics.items():
            plan.resources[resource_id] = {
                "name": metric.name,
                "category": metric.category.value,
                "current_capacity": metric.max_capacity,
                "current_utilization": metric.current_value / metric.max_capacity * 100
            }
            
        # Add forecasts
        for resource_id in self.collector.metrics:
            forecast = self.forecaster.forecast(resource_id, period_days)
            if forecast:
                plan.forecasts.append(forecast)
                
        # Add recommendations
        plan.recommendations = self.recommendation_engine.generate_recommendations()
        
        # Calculate projected cost
        cost_projection = self.cost_analyzer.project_costs(period_days // 30)
        plan.projected_cost = cost_projection.current_monthly_cost * (period_days / 30)
        
        return plan


class CapacityPlanningPlatform:
    """Платформа планирования ёмкости"""
    
    def __init__(self):
        self.collector = MetricsCollector()
        self.analyzer = PatternAnalyzer(self.collector)
        self.forecaster = Forecaster(self.collector, self.analyzer)
        self.bottleneck_detector = BottleneckDetector(self.collector)
        self.recommendation_engine = RecommendationEngine(
            self.collector, self.forecaster, self.bottleneck_detector
        )
        self.cost_analyzer = CostAnalyzer(self.collector, self.recommendation_engine)
        self.plan_builder = PlanBuilder(
            self.collector, self.forecaster,
            self.recommendation_engine, self.cost_analyzer
        )
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        resources = len(self.collector.metrics)
        bottlenecks = len(self.bottleneck_detector.detect_bottlenecks())
        recommendations = len(self.recommendation_engine.generate_recommendations())
        
        return {
            "total_resources": resources,
            "bottlenecks": bottlenecks,
            "recommendations": recommendations
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 162: Capacity Planning Platform")
    print("=" * 60)
    
    platform = CapacityPlanningPlatform()
    print("✓ Capacity Planning Platform created")
    
    # Register resources
    print("\n📊 Registering Resources...")
    
    resources = [
        ("cpu_cluster", "CPU Cluster", ResourceCategory.COMPUTE, 100, "cores", TrendType.GROWING),
        ("memory_pool", "Memory Pool", ResourceCategory.MEMORY, 512, "GB", TrendType.GROWING),
        ("storage_array", "Storage Array", ResourceCategory.STORAGE, 10000, "GB", TrendType.GROWING),
        ("network_bandwidth", "Network Bandwidth", ResourceCategory.NETWORK, 10, "Gbps", TrendType.STABLE),
        ("database_pool", "Database Pool", ResourceCategory.DATABASE, 10, "instances", TrendType.GROWING),
    ]
    
    for res_id, name, category, capacity, unit, trend in resources:
        platform.collector.register_resource(res_id, name, category, capacity, unit)
        platform.collector.generate_sample_data(res_id, days=30, trend=trend)
        
        # Set current value based on trend
        if trend == TrendType.GROWING:
            current = capacity * 0.75
        else:
            current = capacity * 0.5
        platform.collector.record_metric(res_id, current)
        
        print(f"  ✓ {name}: {capacity} {unit}")
        
    # Analyze patterns
    print("\n📈 Analyzing Usage Patterns...")
    
    print("\n  ┌────────────────────────────────────────────────────────────────┐")
    print("  │ Resource          │ Trend      │ Avg      │ Peak     │ Growth   │")
    print("  ├────────────────────────────────────────────────────────────────┤")
    
    for res_id, metric in platform.collector.metrics.items():
        pattern = platform.analyzer.analyze_pattern(res_id)
        
        if pattern:
            name = metric.name[:17].ljust(17)
            trend = pattern.trend_type.value[:10].ljust(10)
            avg = f"{pattern.avg_usage:.1f}".ljust(8)
            peak = f"{pattern.peak_usage:.1f}".ljust(8)
            growth = f"{pattern.growth_rate:+.1f}%".ljust(8)
            print(f"  │ {name} │ {trend} │ {avg} │ {peak} │ {growth} │")
            
    print("  └────────────────────────────────────────────────────────────────┘")
    
    # Generate forecasts
    print("\n🔮 Generating Forecasts (90 days)...")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────┐")
    print("  │ Resource          │ Current   │ 30 Days   │ 60 Days   │ 90 Days    │")
    print("  ├─────────────────────────────────────────────────────────────────────┤")
    
    for res_id, metric in platform.collector.metrics.items():
        forecast = platform.forecaster.forecast(res_id, 90)
        
        if forecast:
            name = metric.name[:17].ljust(17)
            current = f"{metric.current_value:.0f}".ljust(9)
            
            # Get predictions at 30, 60, 90 days
            pred_30 = forecast.predictions[29][1] if len(forecast.predictions) > 29 else 0
            pred_60 = forecast.predictions[59][1] if len(forecast.predictions) > 59 else 0
            pred_90 = forecast.predictions[89][1] if len(forecast.predictions) > 89 else 0
            
            d30 = f"{pred_30:.0f}".ljust(9)
            d60 = f"{pred_60:.0f}".ljust(9)
            d90 = f"{pred_90:.0f}".ljust(10)
            
            print(f"  │ {name} │ {current} │ {d30} │ {d60} │ {d90} │")
            
    print("  └─────────────────────────────────────────────────────────────────────┘")
    
    # Capacity exhaustion warnings
    print("\n⚠️ Capacity Exhaustion Warnings:")
    
    for res_id, metric in platform.collector.metrics.items():
        forecast = platform.forecaster.forecast(res_id, 90)
        
        if forecast and forecast.exhaustion_date:
            days = forecast.days_until_exhaustion
            status = "🔴 CRITICAL" if days <= 7 else "🟡 WARNING" if days <= 30 else "🟢 INFO"
            print(f"  {status} {metric.name}: Capacity exhaustion in {days} days")
            
    # Detect bottlenecks
    print("\n🚧 Current Bottlenecks:")
    
    bottlenecks = platform.bottleneck_detector.detect_bottlenecks()
    
    if bottlenecks:
        for bn in bottlenecks:
            status = "🔴" if bn.severity == AlertLevel.CRITICAL else "🟡"
            metric = platform.collector.metrics.get(bn.resource_id)
            print(f"  {status} {metric.name if metric else bn.component}: {bn.current_utilization:.1f}% utilization")
            print(f"     Recommendation: {bn.recommendation}")
    else:
        print("  ✓ No critical bottlenecks detected")
        
    # Generate recommendations
    print("\n💡 Scaling Recommendations:")
    
    recommendations = platform.recommendation_engine.generate_recommendations()
    
    if recommendations:
        print("\n  ┌────────────────────────────────────────────────────────────────────────┐")
        print("  │ Resource          │ Action    │ Priority │ When     │ Cost Impact   │")
        print("  ├────────────────────────────────────────────────────────────────────────┤")
        
        for rec in sorted(recommendations, key=lambda r: r.priority.value):
            metric = platform.collector.metrics.get(rec.resource_id)
            name = (metric.name if metric else rec.resource_id)[:17].ljust(17)
            action = rec.action[:9].ljust(9)
            priority = rec.priority.value[:8].ljust(8)
            when = rec.when[:8].ljust(8)
            cost = f"${rec.cost_delta:+.0f}/mo".ljust(13)
            print(f"  │ {name} │ {action} │ {priority} │ {when} │ {cost} │")
            
        print("  └────────────────────────────────────────────────────────────────────────┘")
    else:
        print("  ✓ No immediate scaling actions needed")
        
    # Cost projections
    print("\n💰 Cost Projections:")
    
    cost_projection = platform.cost_analyzer.project_costs(12)
    
    print(f"\n  Current Monthly Cost: ${cost_projection.current_monthly_cost:,.0f}")
    print(f"  Annual Growth Rate: {cost_projection.cost_growth_rate:.1f}%")
    
    print("\n  Cost by Category:")
    for cat, cost in sorted(cost_projection.by_category.items(), 
                           key=lambda x: x[1], reverse=True):
        bar = "█" * int(cost / cost_projection.current_monthly_cost * 20)
        print(f"    {cat.ljust(12)}: ${cost:>8,.0f} {bar}")
        
    print("\n  12-Month Projection:")
    print("  ┌────────────────────────────────────────────────────────────┐")
    
    for month in [1, 3, 6, 12]:
        cost = cost_projection.projections.get(f"month_{month}", 0)
        bar = "█" * int(cost / cost_projection.projections["month_12"] * 30)
        print(f"  │ Month {month:>2}: ${cost:>10,.0f} {bar.ljust(30)} │")
        
    print("  └────────────────────────────────────────────────────────────┘")
    
    # Create capacity plan
    print("\n📋 Creating Capacity Plan...")
    
    plan = platform.plan_builder.create_plan(
        name="Q4 2024 Capacity Plan",
        period_days=90,
        budget=50000
    )
    
    print(f"\n  Plan: {plan.name}")
    print(f"  Period: {plan.period_start.strftime('%Y-%m-%d')} to {plan.period_end.strftime('%Y-%m-%d')}")
    print(f"  Resources: {len(plan.resources)}")
    print(f"  Forecasts: {len(plan.forecasts)}")
    print(f"  Recommendations: {len(plan.recommendations)}")
    print(f"  Budget: ${plan.total_budget:,.0f}")
    print(f"  Projected Cost: ${plan.projected_cost:,.0f}")
    
    budget_status = "✓ Within Budget" if plan.projected_cost <= plan.total_budget else "⚠️ Over Budget"
    print(f"  Status: {budget_status}")
    
    # Resource utilization heatmap
    print("\n📊 Resource Utilization Heatmap:")
    print("  ┌────────────────────────────────────────────────────────────┐")
    
    for res_id, info in plan.resources.items():
        name = info["name"][:15].ljust(15)
        util = info["current_utilization"]
        
        # Create bar
        bar_len = int(util / 5)  # 20 chars max
        bar = "█" * bar_len + "░" * (20 - bar_len)
        
        # Color indicator
        if util >= 90:
            indicator = "🔴"
        elif util >= 75:
            indicator = "🟡"
        else:
            indicator = "🟢"
            
        print(f"  │ {name} {indicator} [{bar}] {util:>5.1f}% │")
        
    print("  └────────────────────────────────────────────────────────────┘")
    
    # Platform statistics
    print("\n📈 Platform Statistics:")
    
    stats = platform.get_statistics()
    
    print(f"\n  Total Resources Tracked: {stats['total_resources']}")
    print(f"  Active Bottlenecks: {stats['bottlenecks']}")
    print(f"  Pending Recommendations: {stats['recommendations']}")
    
    # Summary dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Capacity Planning Dashboard                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Resources Monitored:          {stats['total_resources']:>10}                       │")
    print(f"│ Bottlenecks Detected:         {stats['bottlenecks']:>10}                       │")
    print(f"│ Scaling Recommendations:      {stats['recommendations']:>10}                       │")
    print(f"│ Monthly Cost:                 ${cost_projection.current_monthly_cost:>9,.0f}                       │")
    print(f"│ Projected Annual Cost:        ${cost_projection.projections['month_12']:>9,.0f}                       │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Capacity Planning Platform initialized!")
    print("=" * 60)
