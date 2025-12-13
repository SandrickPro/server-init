#!/usr/bin/env python3
"""
Server Init - Iteration 53: Capacity Planning & Resource Forecasting
Планирование ёмкости и прогнозирование ресурсов

Функционал:
- Resource Utilization Analysis - анализ использования ресурсов
- Trend Analysis - анализ трендов
- Demand Forecasting - прогнозирование спроса
- Capacity Modeling - моделирование ёмкости
- Bottleneck Detection - обнаружение узких мест
- Cost Projection - прогнозирование затрат
- Scaling Recommendations - рекомендации по масштабированию
- What-If Analysis - анализ сценариев
"""

import json
import asyncio
import math
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from collections import defaultdict
import random
import uuid


class ResourceType(Enum):
    """Тип ресурса"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    IOPS = "iops"
    GPU = "gpu"


class TrendDirection(Enum):
    """Направление тренда"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    FLUCTUATING = "fluctuating"


class AlertSeverity(Enum):
    """Серьёзность алерта"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class ScaleAction(Enum):
    """Действие масштабирования"""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    SCALE_OUT = "scale_out"
    SCALE_IN = "scale_in"
    NO_ACTION = "no_action"


@dataclass
class ResourceMetric:
    """Метрика ресурса"""
    timestamp: datetime
    resource_type: ResourceType
    resource_id: str
    
    # Значения
    value: float = 0.0
    capacity: float = 0.0
    utilization: float = 0.0
    
    # Дополнительно
    unit: str = ""


@dataclass
class ResourceProfile:
    """Профиль ресурса"""
    profile_id: str
    resource_id: str
    name: str
    resource_type: ResourceType
    
    # Ёмкость
    total_capacity: float = 0.0
    allocated_capacity: float = 0.0
    reserved_capacity: float = 0.0
    
    # Текущее использование
    current_utilization: float = 0.0
    peak_utilization: float = 0.0
    avg_utilization: float = 0.0
    
    # Пороги
    warning_threshold: float = 75.0
    critical_threshold: float = 90.0
    
    # Единица измерения
    unit: str = ""


@dataclass
class TrendAnalysis:
    """Анализ тренда"""
    analysis_id: str
    resource_id: str
    resource_type: ResourceType
    
    # Период
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Тренд
    direction: TrendDirection = TrendDirection.STABLE
    slope: float = 0.0  # Изменение в единицу времени
    
    # Прогноз
    current_value: float = 0.0
    projected_value: float = 0.0
    projection_date: Optional[datetime] = None
    
    # Надёжность
    confidence: float = 0.0
    r_squared: float = 0.0


@dataclass
class CapacityForecast:
    """Прогноз ёмкости"""
    forecast_id: str
    resource_id: str
    resource_type: ResourceType
    
    # Горизонт прогноза
    forecast_horizon_days: int = 30
    
    # Прогнозы
    forecasts: List[Dict[str, Any]] = field(default_factory=list)
    
    # Время исчерпания
    exhaustion_date: Optional[datetime] = None
    days_until_exhaustion: Optional[int] = None
    
    # Уверенность
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    
    # Время создания
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Bottleneck:
    """Узкое место"""
    bottleneck_id: str
    resource_id: str
    resource_type: ResourceType
    
    # Серьёзность
    severity: AlertSeverity = AlertSeverity.WARNING
    
    # Описание
    description: str = ""
    
    # Метрики
    utilization: float = 0.0
    impact_score: float = 0.0
    
    # Затронутые сервисы
    affected_services: List[str] = field(default_factory=list)
    
    # Рекомендации
    recommendations: List[str] = field(default_factory=list)
    
    # Время
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class ScalingRecommendation:
    """Рекомендация по масштабированию"""
    recommendation_id: str
    resource_id: str
    resource_type: ResourceType
    
    # Действие
    action: ScaleAction = ScaleAction.NO_ACTION
    
    # Текущее и рекомендуемое
    current_capacity: float = 0.0
    recommended_capacity: float = 0.0
    change_percent: float = 0.0
    
    # Причина
    reason: str = ""
    
    # Стоимость
    estimated_cost_change: float = 0.0
    
    # Приоритет
    priority: int = 0  # 1-10
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CostProjection:
    """Прогноз затрат"""
    projection_id: str
    
    # Период
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Затраты
    current_monthly_cost: float = 0.0
    projected_monthly_cost: float = 0.0
    
    # По категориям
    cost_by_resource: Dict[str, float] = field(default_factory=dict)
    
    # Тренд
    cost_trend: TrendDirection = TrendDirection.STABLE
    growth_rate: float = 0.0  # Процент роста
    
    # Рекомендации по оптимизации
    savings_opportunities: List[Dict[str, Any]] = field(default_factory=list)


@dataclass 
class WhatIfScenario:
    """Сценарий What-If"""
    scenario_id: str
    name: str
    description: str = ""
    
    # Изменения
    changes: List[Dict[str, Any]] = field(default_factory=list)
    
    # Результаты
    impact_analysis: Dict[str, Any] = field(default_factory=dict)
    
    # Стоимость
    cost_impact: float = 0.0
    
    # Создано
    created_at: datetime = field(default_factory=datetime.now)


class MetricsCollector:
    """Коллектор метрик"""
    
    def __init__(self):
        self.metrics: Dict[str, List[ResourceMetric]] = defaultdict(list)
        self.profiles: Dict[str, ResourceProfile] = {}
        
    def add_metric(self, resource_id: str, resource_type: ResourceType,
                    value: float, capacity: float, **kwargs) -> ResourceMetric:
        """Добавление метрики"""
        metric = ResourceMetric(
            timestamp=datetime.now(),
            resource_type=resource_type,
            resource_id=resource_id,
            value=value,
            capacity=capacity,
            utilization=(value / capacity * 100) if capacity > 0 else 0,
            **kwargs
        )
        
        self.metrics[resource_id].append(metric)
        
        # Обновление профиля
        self._update_profile(resource_id, metric)
        
        return metric
        
    def _update_profile(self, resource_id: str, metric: ResourceMetric):
        """Обновление профиля ресурса"""
        if resource_id not in self.profiles:
            self.profiles[resource_id] = ResourceProfile(
                profile_id=f"profile_{uuid.uuid4().hex[:8]}",
                resource_id=resource_id,
                name=resource_id,
                resource_type=metric.resource_type,
                total_capacity=metric.capacity
            )
            
        profile = self.profiles[resource_id]
        profile.current_utilization = metric.utilization
        profile.peak_utilization = max(profile.peak_utilization, metric.utilization)
        
        # Расчёт среднего
        metrics = self.metrics[resource_id]
        if metrics:
            profile.avg_utilization = sum(m.utilization for m in metrics) / len(metrics)
            
    def get_metrics(self, resource_id: str, 
                     hours: int = 24) -> List[ResourceMetric]:
        """Получение метрик за период"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [
            m for m in self.metrics.get(resource_id, [])
            if m.timestamp > cutoff
        ]
        
    def generate_sample_data(self, resource_id: str, 
                              resource_type: ResourceType,
                              days: int = 30):
        """Генерация тестовых данных"""
        base_value = random.uniform(30, 50)
        capacity = 100.0
        
        for day in range(days):
            for hour in range(24):
                timestamp = datetime.now() - timedelta(days=days-day, hours=24-hour)
                
                # Добавляем тренд и сезонность
                trend = day * 0.3  # Растущий тренд
                daily_pattern = 10 * math.sin(hour * math.pi / 12)  # Дневной паттерн
                noise = random.uniform(-5, 5)
                
                value = min(capacity, max(0, base_value + trend + daily_pattern + noise))
                
                metric = ResourceMetric(
                    timestamp=timestamp,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    value=value,
                    capacity=capacity,
                    utilization=value
                )
                
                self.metrics[resource_id].append(metric)
                
        self._update_profile(resource_id, self.metrics[resource_id][-1])


class TrendAnalyzer:
    """Анализатор трендов"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.collector = metrics_collector
        
    def analyze_trend(self, resource_id: str, 
                       days: int = 7) -> TrendAnalysis:
        """Анализ тренда"""
        metrics = self.collector.get_metrics(resource_id, hours=days*24)
        
        if len(metrics) < 2:
            return TrendAnalysis(
                analysis_id=f"trend_{uuid.uuid4().hex[:8]}",
                resource_id=resource_id,
                resource_type=metrics[0].resource_type if metrics else ResourceType.CPU,
                direction=TrendDirection.STABLE,
                confidence=0.0
            )
            
        # Линейная регрессия
        n = len(metrics)
        x = list(range(n))
        y = [m.utilization for m in metrics]
        
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        
        # Определение направления
        if slope > 0.5:
            direction = TrendDirection.INCREASING
        elif slope < -0.5:
            direction = TrendDirection.DECREASING
        else:
            # Проверка на флуктуации
            variance = sum((yi - y_mean) ** 2 for yi in y) / n
            if variance > 100:
                direction = TrendDirection.FLUCTUATING
            else:
                direction = TrendDirection.STABLE
                
        # R-squared
        ss_tot = sum((yi - y_mean) ** 2 for yi in y)
        y_pred = [slope * xi + (y_mean - slope * x_mean) for xi in x]
        ss_res = sum((y[i] - y_pred[i]) ** 2 for i in range(n))
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # Прогноз на 30 дней
        projection_days = 30
        projected_value = y[-1] + slope * projection_days * 24  # hours
        
        return TrendAnalysis(
            analysis_id=f"trend_{uuid.uuid4().hex[:8]}",
            resource_id=resource_id,
            resource_type=metrics[0].resource_type,
            period_start=metrics[0].timestamp,
            period_end=metrics[-1].timestamp,
            direction=direction,
            slope=slope,
            current_value=y[-1],
            projected_value=min(100, max(0, projected_value)),
            projection_date=datetime.now() + timedelta(days=projection_days),
            confidence=r_squared * 100,
            r_squared=r_squared
        )


class CapacityForecaster:
    """Прогнозировщик ёмкости"""
    
    def __init__(self, metrics_collector: MetricsCollector,
                  trend_analyzer: TrendAnalyzer):
        self.collector = metrics_collector
        self.analyzer = trend_analyzer
        
    def forecast_capacity(self, resource_id: str,
                           horizon_days: int = 30) -> CapacityForecast:
        """Прогноз ёмкости"""
        profile = self.collector.profiles.get(resource_id)
        trend = self.analyzer.analyze_trend(resource_id)
        
        forecasts = []
        current_value = trend.current_value
        
        for day in range(1, horizon_days + 1):
            date = datetime.now() + timedelta(days=day)
            projected = current_value + trend.slope * day * 24
            
            # Добавляем неопределённость
            uncertainty = day * 0.5
            low = max(0, projected - uncertainty)
            high = min(100, projected + uncertainty)
            
            forecasts.append({
                "date": date.isoformat(),
                "day": day,
                "projected_utilization": round(projected, 1),
                "low": round(low, 1),
                "high": round(high, 1)
            })
            
        # Расчёт времени исчерпания
        exhaustion_date = None
        days_until_exhaustion = None
        
        if trend.direction == TrendDirection.INCREASING and trend.slope > 0:
            threshold = profile.critical_threshold if profile else 90
            remaining = threshold - current_value
            
            if remaining > 0 and trend.slope > 0:
                hours_to_exhaustion = remaining / trend.slope
                days_until_exhaustion = int(hours_to_exhaustion / 24)
                
                if days_until_exhaustion <= horizon_days:
                    exhaustion_date = datetime.now() + timedelta(hours=hours_to_exhaustion)
                    
        return CapacityForecast(
            forecast_id=f"forecast_{uuid.uuid4().hex[:8]}",
            resource_id=resource_id,
            resource_type=trend.resource_type,
            forecast_horizon_days=horizon_days,
            forecasts=forecasts,
            exhaustion_date=exhaustion_date,
            days_until_exhaustion=days_until_exhaustion,
            confidence_interval=(trend.confidence - 10, trend.confidence + 10)
        )


class BottleneckDetector:
    """Детектор узких мест"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.collector = metrics_collector
        
    def detect_bottlenecks(self) -> List[Bottleneck]:
        """Обнаружение узких мест"""
        bottlenecks = []
        
        for resource_id, profile in self.collector.profiles.items():
            if profile.current_utilization >= profile.critical_threshold:
                severity = AlertSeverity.CRITICAL
            elif profile.current_utilization >= profile.warning_threshold:
                severity = AlertSeverity.WARNING
            else:
                continue
                
            bottleneck = Bottleneck(
                bottleneck_id=f"btn_{uuid.uuid4().hex[:8]}",
                resource_id=resource_id,
                resource_type=profile.resource_type,
                severity=severity,
                description=f"{profile.resource_type.value.upper()} utilization at {profile.current_utilization:.1f}%",
                utilization=profile.current_utilization,
                impact_score=self._calculate_impact(profile),
                recommendations=self._generate_recommendations(profile)
            )
            
            bottlenecks.append(bottleneck)
            
        return sorted(bottlenecks, key=lambda b: b.impact_score, reverse=True)
        
    def _calculate_impact(self, profile: ResourceProfile) -> float:
        """Расчёт влияния"""
        base_impact = profile.current_utilization / 100
        
        # Увеличиваем для критических ресурсов
        critical_types = [ResourceType.CPU, ResourceType.MEMORY]
        if profile.resource_type in critical_types:
            base_impact *= 1.5
            
        return min(1.0, base_impact)
        
    def _generate_recommendations(self, profile: ResourceProfile) -> List[str]:
        """Генерация рекомендаций"""
        recommendations = []
        
        if profile.resource_type == ResourceType.CPU:
            recommendations.append("Рассмотрите вертикальное масштабирование (увеличение CPU)")
            recommendations.append("Оптимизируйте ресурсоёмкие процессы")
            
        elif profile.resource_type == ResourceType.MEMORY:
            recommendations.append("Увеличьте объём RAM")
            recommendations.append("Проверьте утечки памяти в приложениях")
            
        elif profile.resource_type == ResourceType.STORAGE:
            recommendations.append("Очистите неиспользуемые данные")
            recommendations.append("Расширьте хранилище")
            
        recommendations.append("Настройте горизонтальное масштабирование")
        
        return recommendations


class ScalingAdvisor:
    """Советник по масштабированию"""
    
    def __init__(self, metrics_collector: MetricsCollector,
                  forecaster: CapacityForecaster):
        self.collector = metrics_collector
        self.forecaster = forecaster
        
    def get_recommendations(self) -> List[ScalingRecommendation]:
        """Получение рекомендаций"""
        recommendations = []
        
        for resource_id, profile in self.collector.profiles.items():
            forecast = self.forecaster.forecast_capacity(resource_id, 30)
            
            recommendation = self._analyze_resource(profile, forecast)
            if recommendation:
                recommendations.append(recommendation)
                
        return sorted(recommendations, key=lambda r: r.priority, reverse=True)
        
    def _analyze_resource(self, profile: ResourceProfile,
                          forecast: CapacityForecast) -> Optional[ScalingRecommendation]:
        """Анализ ресурса"""
        action = ScaleAction.NO_ACTION
        recommended_capacity = profile.total_capacity
        reason = ""
        priority = 0
        
        # Проверка текущей утилизации
        if profile.current_utilization >= profile.critical_threshold:
            action = ScaleAction.SCALE_UP
            recommended_capacity = profile.total_capacity * 1.5
            reason = f"Критическая утилизация: {profile.current_utilization:.1f}%"
            priority = 10
            
        elif profile.current_utilization >= profile.warning_threshold:
            action = ScaleAction.SCALE_UP
            recommended_capacity = profile.total_capacity * 1.25
            reason = f"Высокая утилизация: {profile.current_utilization:.1f}%"
            priority = 7
            
        # Проверка прогноза
        elif forecast.exhaustion_date and forecast.days_until_exhaustion:
            if forecast.days_until_exhaustion <= 7:
                action = ScaleAction.SCALE_UP
                recommended_capacity = profile.total_capacity * 1.5
                reason = f"Исчерпание ёмкости через {forecast.days_until_exhaustion} дней"
                priority = 9
            elif forecast.days_until_exhaustion <= 30:
                action = ScaleAction.SCALE_UP
                recommended_capacity = profile.total_capacity * 1.25
                reason = f"Прогнозируемое исчерпание через {forecast.days_until_exhaustion} дней"
                priority = 5
                
        # Проверка на избыточную ёмкость
        elif profile.avg_utilization < 20 and profile.peak_utilization < 40:
            action = ScaleAction.SCALE_DOWN
            recommended_capacity = profile.total_capacity * 0.7
            reason = f"Низкая утилизация: avg={profile.avg_utilization:.1f}%, peak={profile.peak_utilization:.1f}%"
            priority = 3
            
        if action == ScaleAction.NO_ACTION:
            return None
            
        change_percent = ((recommended_capacity - profile.total_capacity) / profile.total_capacity) * 100
        
        # Оценка изменения стоимости
        cost_per_unit = 10.0  # Условная стоимость за единицу
        cost_change = (recommended_capacity - profile.total_capacity) * cost_per_unit
        
        return ScalingRecommendation(
            recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
            resource_id=profile.resource_id,
            resource_type=profile.resource_type,
            action=action,
            current_capacity=profile.total_capacity,
            recommended_capacity=recommended_capacity,
            change_percent=change_percent,
            reason=reason,
            estimated_cost_change=cost_change,
            priority=priority
        )


class CostProjector:
    """Прогнозировщик затрат"""
    
    def __init__(self, metrics_collector: MetricsCollector,
                  scaling_advisor: ScalingAdvisor):
        self.collector = metrics_collector
        self.advisor = scaling_advisor
        
    def project_costs(self, months: int = 3) -> CostProjection:
        """Прогноз затрат"""
        cost_per_unit = {
            ResourceType.CPU: 50.0,
            ResourceType.MEMORY: 20.0,
            ResourceType.STORAGE: 5.0,
            ResourceType.NETWORK: 10.0,
            ResourceType.IOPS: 2.0,
            ResourceType.GPU: 200.0
        }
        
        current_cost = 0.0
        cost_by_resource = {}
        
        for resource_id, profile in self.collector.profiles.items():
            unit_cost = cost_per_unit.get(profile.resource_type, 10.0)
            resource_cost = profile.total_capacity * unit_cost
            
            cost_by_resource[resource_id] = resource_cost
            current_cost += resource_cost
            
        # Учёт рекомендаций
        recommendations = self.advisor.get_recommendations()
        projected_cost = current_cost
        
        for rec in recommendations:
            projected_cost += rec.estimated_cost_change
            
        growth_rate = ((projected_cost - current_cost) / current_cost * 100) if current_cost > 0 else 0
        
        # Определение тренда
        if growth_rate > 10:
            trend = TrendDirection.INCREASING
        elif growth_rate < -10:
            trend = TrendDirection.DECREASING
        else:
            trend = TrendDirection.STABLE
            
        # Возможности экономии
        savings = []
        
        for rec in recommendations:
            if rec.action == ScaleAction.SCALE_DOWN:
                savings.append({
                    "resource_id": rec.resource_id,
                    "potential_savings": abs(rec.estimated_cost_change),
                    "action": "Reduce capacity"
                })
                
        return CostProjection(
            projection_id=f"cost_{uuid.uuid4().hex[:8]}",
            period_start=datetime.now(),
            period_end=datetime.now() + timedelta(days=months*30),
            current_monthly_cost=current_cost,
            projected_monthly_cost=projected_cost,
            cost_by_resource=cost_by_resource,
            cost_trend=trend,
            growth_rate=growth_rate,
            savings_opportunities=savings
        )


class WhatIfAnalyzer:
    """Анализатор What-If сценариев"""
    
    def __init__(self, metrics_collector: MetricsCollector,
                  cost_projector: CostProjector):
        self.collector = metrics_collector
        self.projector = cost_projector
        self.scenarios: Dict[str, WhatIfScenario] = {}
        
    def create_scenario(self, name: str, 
                         changes: List[Dict[str, Any]]) -> WhatIfScenario:
        """Создание сценария"""
        scenario = WhatIfScenario(
            scenario_id=f"scenario_{uuid.uuid4().hex[:8]}",
            name=name,
            changes=changes
        )
        
        self.scenarios[scenario.scenario_id] = scenario
        return scenario
        
    def analyze_scenario(self, scenario_id: str) -> Dict[str, Any]:
        """Анализ сценария"""
        scenario = self.scenarios.get(scenario_id)
        if not scenario:
            return {"error": "Scenario not found"}
            
        # Базовая проекция
        base_projection = self.projector.project_costs()
        
        # Применение изменений
        modified_cost = base_projection.current_monthly_cost
        resource_impacts = []
        
        for change in scenario.changes:
            change_type = change.get("type")
            resource_id = change.get("resource_id")
            factor = change.get("factor", 1.0)
            
            profile = self.collector.profiles.get(resource_id)
            if not profile:
                continue
                
            if change_type == "scale":
                old_capacity = profile.total_capacity
                new_capacity = old_capacity * factor
                cost_diff = (new_capacity - old_capacity) * 10  # Условная стоимость
                
                modified_cost += cost_diff
                
                resource_impacts.append({
                    "resource_id": resource_id,
                    "change": f"Capacity {old_capacity:.1f} -> {new_capacity:.1f}",
                    "cost_impact": cost_diff
                })
                
            elif change_type == "add":
                count = change.get("count", 1)
                unit_cost = change.get("unit_cost", 100)
                
                modified_cost += count * unit_cost
                
                resource_impacts.append({
                    "resource_id": resource_id,
                    "change": f"Add {count} instances",
                    "cost_impact": count * unit_cost
                })
                
        scenario.cost_impact = modified_cost - base_projection.current_monthly_cost
        scenario.impact_analysis = {
            "base_cost": base_projection.current_monthly_cost,
            "modified_cost": modified_cost,
            "cost_difference": scenario.cost_impact,
            "cost_change_percent": (scenario.cost_impact / base_projection.current_monthly_cost * 100) if base_projection.current_monthly_cost > 0 else 0,
            "resource_impacts": resource_impacts
        }
        
        return scenario.impact_analysis


class CapacityPlanningPlatform:
    """Платформа планирования ёмкости"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.trend_analyzer = TrendAnalyzer(self.metrics_collector)
        self.forecaster = CapacityForecaster(self.metrics_collector, self.trend_analyzer)
        self.bottleneck_detector = BottleneckDetector(self.metrics_collector)
        self.scaling_advisor = ScalingAdvisor(self.metrics_collector, self.forecaster)
        self.cost_projector = CostProjector(self.metrics_collector, self.scaling_advisor)
        self.whatif_analyzer = WhatIfAnalyzer(self.metrics_collector, self.cost_projector)
        
    def get_status(self) -> Dict[str, Any]:
        """Статус платформы"""
        profiles = self.metrics_collector.profiles
        
        return {
            "resources_monitored": len(profiles),
            "total_metrics": sum(len(m) for m in self.metrics_collector.metrics.values()),
            "bottlenecks": len(self.bottleneck_detector.detect_bottlenecks()),
            "recommendations": len(self.scaling_advisor.get_recommendations())
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 53: Capacity Planning & Forecasting")
    print("=" * 60)
    
    async def demo():
        # Создание платформы
        platform = CapacityPlanningPlatform()
        print("✓ Capacity Planning Platform created")
        
        # Генерация тестовых данных
        print("\n📊 Generating sample metrics...")
        
        resources = [
            ("web-server-cpu", ResourceType.CPU),
            ("web-server-memory", ResourceType.MEMORY),
            ("db-server-storage", ResourceType.STORAGE),
            ("cache-server-memory", ResourceType.MEMORY)
        ]
        
        for resource_id, resource_type in resources:
            platform.metrics_collector.generate_sample_data(
                resource_id, resource_type, days=30
            )
            print(f"  ✓ Generated metrics for {resource_id}")
            
        # Симуляция высокой нагрузки для одного ресурса
        platform.metrics_collector.add_metric(
            "web-server-cpu",
            ResourceType.CPU,
            value=92,
            capacity=100
        )
        
        # Профили ресурсов
        print("\n📋 Resource Profiles:")
        
        for resource_id, profile in platform.metrics_collector.profiles.items():
            print(f"\n  {resource_id}:")
            print(f"    Type: {profile.resource_type.value}")
            print(f"    Current: {profile.current_utilization:.1f}%")
            print(f"    Average: {profile.avg_utilization:.1f}%")
            print(f"    Peak: {profile.peak_utilization:.1f}%")
            
        # Анализ трендов
        print("\n📈 Trend Analysis:")
        
        for resource_id in resources[:2]:
            trend = platform.trend_analyzer.analyze_trend(resource_id[0])
            print(f"\n  {resource_id[0]}:")
            print(f"    Direction: {trend.direction.value}")
            print(f"    Slope: {trend.slope:.4f}")
            print(f"    Current: {trend.current_value:.1f}%")
            print(f"    Projected (30d): {trend.projected_value:.1f}%")
            print(f"    Confidence: {trend.confidence:.1f}%")
            
        # Прогноз ёмкости
        print("\n🔮 Capacity Forecasts:")
        
        for resource_id, _ in resources[:2]:
            forecast = platform.forecaster.forecast_capacity(resource_id, 30)
            print(f"\n  {resource_id}:")
            
            # Показываем прогноз на 7, 14, 30 дней
            for day in [7, 14, 30]:
                f = forecast.forecasts[day-1]
                print(f"    Day {day}: {f['projected_utilization']:.1f}% ({f['low']:.1f}-{f['high']:.1f})")
                
            if forecast.exhaustion_date:
                print(f"    ⚠️ Exhaustion in {forecast.days_until_exhaustion} days!")
                
        # Обнаружение узких мест
        print("\n🔍 Bottleneck Detection:")
        
        bottlenecks = platform.bottleneck_detector.detect_bottlenecks()
        
        if bottlenecks:
            for btn in bottlenecks:
                print(f"\n  ⚠️ {btn.severity.value.upper()}: {btn.description}")
                print(f"    Impact score: {btn.impact_score:.2f}")
                print(f"    Recommendations:")
                for rec in btn.recommendations[:2]:
                    print(f"      → {rec}")
        else:
            print("  ✓ No bottlenecks detected")
            
        # Рекомендации по масштабированию
        print("\n📝 Scaling Recommendations:")
        
        recommendations = platform.scaling_advisor.get_recommendations()
        
        if recommendations:
            for rec in recommendations[:3]:
                print(f"\n  {rec.resource_id}:")
                print(f"    Action: {rec.action.value}")
                print(f"    Current: {rec.current_capacity:.1f} → Recommended: {rec.recommended_capacity:.1f}")
                print(f"    Change: {rec.change_percent:+.1f}%")
                print(f"    Reason: {rec.reason}")
                print(f"    Priority: {rec.priority}/10")
                print(f"    Est. cost change: ${rec.estimated_cost_change:+.2f}/mo")
        else:
            print("  ✓ No scaling recommendations")
            
        # Прогноз затрат
        print("\n💰 Cost Projection:")
        
        cost_proj = platform.cost_projector.project_costs(3)
        print(f"  Current monthly: ${cost_proj.current_monthly_cost:.2f}")
        print(f"  Projected monthly: ${cost_proj.projected_monthly_cost:.2f}")
        print(f"  Trend: {cost_proj.cost_trend.value}")
        print(f"  Growth rate: {cost_proj.growth_rate:+.1f}%")
        
        if cost_proj.savings_opportunities:
            print(f"\n  Savings opportunities:")
            for sav in cost_proj.savings_opportunities[:3]:
                print(f"    {sav['resource_id']}: ${sav['potential_savings']:.2f}")
                
        # What-If анализ
        print("\n🤔 What-If Analysis:")
        
        scenario = platform.whatif_analyzer.create_scenario(
            name="Scale up web servers",
            changes=[
                {"type": "scale", "resource_id": "web-server-cpu", "factor": 1.5},
                {"type": "scale", "resource_id": "web-server-memory", "factor": 1.5}
            ]
        )
        print(f"  Scenario: {scenario.name}")
        
        analysis = platform.whatif_analyzer.analyze_scenario(scenario.scenario_id)
        print(f"  Base cost: ${analysis['base_cost']:.2f}")
        print(f"  Modified cost: ${analysis['modified_cost']:.2f}")
        print(f"  Difference: ${analysis['cost_difference']:+.2f} ({analysis['cost_change_percent']:+.1f}%)")
        
        # Статус платформы
        print("\n📊 Platform Status:")
        status = platform.get_status()
        print(f"  Resources monitored: {status['resources_monitored']}")
        print(f"  Total metrics: {status['total_metrics']}")
        print(f"  Active bottlenecks: {status['bottlenecks']}")
        print(f"  Recommendations: {status['recommendations']}")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Capacity Planning & Forecasting Platform initialized!")
    print("=" * 60)
