#!/usr/bin/env python3
"""
Server Init - Iteration 83: Capacity Planning Platform
Платформа планирования ёмкости

Функционал:
- Resource Forecasting - прогнозирование ресурсов
- Capacity Modeling - моделирование ёмкости
- Growth Analysis - анализ роста
- Bottleneck Detection - обнаружение узких мест
- Scaling Recommendations - рекомендации по масштабированию
- Cost Projection - проекция затрат
- What-If Analysis - анализ "что если"
- Capacity Alerts - алерты ёмкости
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Tuple
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
    DATABASE = "database"
    CUSTOM = "custom"


class TrendType(Enum):
    """Тип тренда"""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    SEASONAL = "seasonal"
    STABLE = "stable"


class AlertSeverity(Enum):
    """Серьёзность алерта"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ScalingAction(Enum):
    """Действие масштабирования"""
    SCALE_UP = "scale_up"
    SCALE_OUT = "scale_out"
    SCALE_DOWN = "scale_down"
    SCALE_IN = "scale_in"
    NO_ACTION = "no_action"


@dataclass
class ResourceMetric:
    """Метрика ресурса"""
    timestamp: datetime
    value: float
    unit: str = ""


@dataclass
class Resource:
    """Ресурс"""
    resource_id: str
    name: str = ""
    
    # Тип
    resource_type: ResourceType = ResourceType.CPU
    
    # Ёмкость
    total_capacity: float = 0.0
    current_usage: float = 0.0
    
    # Единица измерения
    unit: str = ""
    
    # Пороги
    warning_threshold: float = 70.0
    critical_threshold: float = 85.0
    
    # История
    metrics: List[ResourceMetric] = field(default_factory=list)
    
    # Метаданные
    service: str = ""
    environment: str = ""
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class GrowthModel:
    """Модель роста"""
    model_id: str
    resource_id: str = ""
    
    # Тип тренда
    trend_type: TrendType = TrendType.LINEAR
    
    # Параметры модели
    growth_rate: float = 0.0  # % в месяц
    seasonality_factor: float = 1.0
    
    # Статистика
    r_squared: float = 0.0  # Качество модели
    mape: float = 0.0  # Mean Absolute Percentage Error
    
    # Прогноз
    forecast_days: int = 90
    forecast_values: List[Tuple[datetime, float]] = field(default_factory=list)


@dataclass
class Forecast:
    """Прогноз"""
    forecast_id: str
    resource_id: str = ""
    
    # Время прогноза
    forecast_date: datetime = field(default_factory=datetime.now)
    horizon_days: int = 90
    
    # Прогнозируемые значения
    predicted_usage: float = 0.0
    confidence_lower: float = 0.0
    confidence_upper: float = 0.0
    
    # Дата исчерпания
    exhaustion_date: Optional[datetime] = None
    days_until_exhaustion: int = -1
    
    # Рекомендация
    recommendation: str = ""


@dataclass
class CapacityPlan:
    """План ёмкости"""
    plan_id: str
    name: str = ""
    
    # Период планирования
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    
    # Ресурсы
    resources: List[str] = field(default_factory=list)
    
    # Прогнозы
    forecasts: Dict[str, Forecast] = field(default_factory=dict)
    
    # Рекомендации
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Стоимость
    current_cost: float = 0.0
    projected_cost: float = 0.0
    
    # Статус
    status: str = "draft"  # draft, active, approved
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ScalingRecommendation:
    """Рекомендация по масштабированию"""
    recommendation_id: str
    resource_id: str = ""
    
    # Действие
    action: ScalingAction = ScalingAction.NO_ACTION
    
    # Детали
    current_capacity: float = 0.0
    recommended_capacity: float = 0.0
    change_percent: float = 0.0
    
    # Обоснование
    reason: str = ""
    urgency: AlertSeverity = AlertSeverity.INFO
    
    # Стоимость
    estimated_cost_change: float = 0.0
    
    # Время
    recommended_by: datetime = field(default_factory=datetime.now)
    
    # Статус
    status: str = "pending"  # pending, approved, implemented, rejected


@dataclass
class Bottleneck:
    """Узкое место"""
    bottleneck_id: str
    resource_id: str = ""
    
    # Характеристики
    severity: AlertSeverity = AlertSeverity.WARNING
    utilization_percent: float = 0.0
    
    # Влияние
    affected_services: List[str] = field(default_factory=list)
    impact_description: str = ""
    
    # Рекомендация
    resolution: str = ""
    
    # Время обнаружения
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class WhatIfScenario:
    """Сценарий "что если" """
    scenario_id: str
    name: str = ""
    description: str = ""
    
    # Изменения
    changes: Dict[str, Any] = field(default_factory=dict)
    # {"user_growth": 50, "traffic_increase": 100, ...}
    
    # Результаты
    resource_impact: Dict[str, Dict[str, float]] = field(default_factory=dict)
    # {resource_id: {"current": x, "projected": y, "change": z}}
    
    # Стоимость
    cost_impact: float = 0.0
    
    # Риски
    risks: List[str] = field(default_factory=list)
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)


class ForecastEngine:
    """Движок прогнозирования"""
    
    def __init__(self):
        self.models: Dict[str, GrowthModel] = {}
        
    def fit_model(self, resource: Resource) -> GrowthModel:
        """Обучение модели"""
        metrics = resource.metrics
        if len(metrics) < 2:
            return GrowthModel(
                model_id=f"model_{uuid.uuid4().hex[:8]}",
                resource_id=resource.resource_id,
                trend_type=TrendType.STABLE
            )
            
        # Простой линейный анализ
        values = [m.value for m in metrics]
        n = len(values)
        
        # Вычисляем средний темп роста
        if values[0] > 0:
            total_growth = (values[-1] - values[0]) / values[0] * 100
            growth_rate = total_growth / max(1, n - 1)  # % на период
        else:
            growth_rate = 0
            
        # Определяем тип тренда
        if abs(growth_rate) < 1:
            trend_type = TrendType.STABLE
        elif growth_rate > 5:
            trend_type = TrendType.EXPONENTIAL
        else:
            trend_type = TrendType.LINEAR
            
        # Вычисляем R^2 (упрощённо)
        mean_val = sum(values) / len(values)
        ss_tot = sum((v - mean_val) ** 2 for v in values)
        
        # Предсказанные значения (линейная модель)
        predicted = [values[0] + i * (values[-1] - values[0]) / (n - 1) for i in range(n)]
        ss_res = sum((values[i] - predicted[i]) ** 2 for i in range(n))
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        model = GrowthModel(
            model_id=f"model_{uuid.uuid4().hex[:8]}",
            resource_id=resource.resource_id,
            trend_type=trend_type,
            growth_rate=growth_rate * 30,  # В месяц
            r_squared=max(0, r_squared)
        )
        
        self.models[resource.resource_id] = model
        return model
        
    def forecast(self, resource: Resource, days: int = 90) -> Forecast:
        """Прогнозирование"""
        model = self.models.get(resource.resource_id)
        if not model:
            model = self.fit_model(resource)
            
        current = resource.current_usage
        capacity = resource.total_capacity
        
        # Расчёт прогноза
        daily_growth = model.growth_rate / 30 / 100
        predicted = current * (1 + daily_growth * days)
        
        # Доверительный интервал (±10%)
        confidence = predicted * 0.1
        
        # Дата исчерпания
        exhaustion_date = None
        days_until = -1
        
        if daily_growth > 0 and current < capacity:
            # Сколько дней до критического уровня (85%)
            target = capacity * 0.85
            if current < target:
                days_until = int((target - current) / (current * daily_growth)) if daily_growth > 0 else -1
                if days_until > 0:
                    exhaustion_date = datetime.now() + timedelta(days=days_until)
                    
        # Рекомендация
        utilization = (predicted / capacity * 100) if capacity > 0 else 0
        
        if utilization > 85:
            recommendation = f"CRITICAL: Capacity will exceed 85% in {days} days. Scale up immediately."
        elif utilization > 70:
            recommendation = f"WARNING: Capacity will reach {utilization:.0f}% in {days} days. Plan scaling."
        else:
            recommendation = f"OK: Capacity projected at {utilization:.0f}% in {days} days."
            
        return Forecast(
            forecast_id=f"fc_{uuid.uuid4().hex[:8]}",
            resource_id=resource.resource_id,
            horizon_days=days,
            predicted_usage=predicted,
            confidence_lower=predicted - confidence,
            confidence_upper=predicted + confidence,
            exhaustion_date=exhaustion_date,
            days_until_exhaustion=days_until,
            recommendation=recommendation
        )


class BottleneckDetector:
    """Детектор узких мест"""
    
    def detect(self, resources: List[Resource]) -> List[Bottleneck]:
        """Обнаружение узких мест"""
        bottlenecks = []
        
        for resource in resources:
            utilization = (resource.current_usage / resource.total_capacity * 100) if resource.total_capacity > 0 else 0
            
            if utilization >= resource.critical_threshold:
                severity = AlertSeverity.CRITICAL
            elif utilization >= resource.warning_threshold:
                severity = AlertSeverity.WARNING
            else:
                continue
                
            bottleneck = Bottleneck(
                bottleneck_id=f"bn_{uuid.uuid4().hex[:8]}",
                resource_id=resource.resource_id,
                severity=severity,
                utilization_percent=utilization,
                affected_services=[resource.service] if resource.service else [],
                impact_description=f"{resource.name} at {utilization:.1f}% utilization",
                resolution=self._get_resolution(resource, utilization)
            )
            bottlenecks.append(bottleneck)
            
        return bottlenecks
        
    def _get_resolution(self, resource: Resource, utilization: float) -> str:
        """Получение рекомендации по устранению"""
        if resource.resource_type == ResourceType.CPU:
            return "Consider scaling up CPU or adding more instances"
        elif resource.resource_type == ResourceType.MEMORY:
            return "Increase memory allocation or optimize memory usage"
        elif resource.resource_type == ResourceType.STORAGE:
            return "Expand storage capacity or implement data archival"
        elif resource.resource_type == ResourceType.DATABASE:
            return "Scale database or implement read replicas"
        else:
            return "Review resource allocation and consider scaling"


class RecommendationEngine:
    """Движок рекомендаций"""
    
    def __init__(self, cost_per_unit: Dict[ResourceType, float] = None):
        self.cost_per_unit = cost_per_unit or {
            ResourceType.CPU: 50.0,  # $/core/month
            ResourceType.MEMORY: 10.0,  # $/GB/month
            ResourceType.STORAGE: 0.1,  # $/GB/month
            ResourceType.NETWORK: 0.05,  # $/GB
            ResourceType.DATABASE: 100.0,  # $/instance/month
        }
        
    def generate(self, resource: Resource, forecast: Forecast) -> ScalingRecommendation:
        """Генерация рекомендации"""
        current_cap = resource.total_capacity
        current_usage = resource.current_usage
        predicted = forecast.predicted_usage
        
        utilization = (predicted / current_cap * 100) if current_cap > 0 else 0
        
        # Определяем действие
        if utilization > 85:
            action = ScalingAction.SCALE_UP
            # Целевая ёмкость: predicted / 0.7 (70% утилизация)
            recommended_cap = predicted / 0.7
            urgency = AlertSeverity.CRITICAL
            reason = f"Predicted utilization {utilization:.0f}% exceeds critical threshold"
        elif utilization > 70:
            action = ScalingAction.SCALE_UP
            recommended_cap = predicted / 0.6
            urgency = AlertSeverity.WARNING
            reason = f"Predicted utilization {utilization:.0f}% exceeds warning threshold"
        elif utilization < 30:
            action = ScalingAction.SCALE_DOWN
            recommended_cap = max(current_usage * 1.5, predicted * 1.5)
            urgency = AlertSeverity.INFO
            reason = f"Low utilization {utilization:.0f}% - cost optimization opportunity"
        else:
            action = ScalingAction.NO_ACTION
            recommended_cap = current_cap
            urgency = AlertSeverity.INFO
            reason = f"Utilization {utilization:.0f}% is within optimal range"
            
        # Расчёт изменения стоимости
        capacity_change = recommended_cap - current_cap
        unit_cost = self.cost_per_unit.get(resource.resource_type, 0)
        cost_change = capacity_change * unit_cost
        
        return ScalingRecommendation(
            recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
            resource_id=resource.resource_id,
            action=action,
            current_capacity=current_cap,
            recommended_capacity=recommended_cap,
            change_percent=((recommended_cap - current_cap) / current_cap * 100) if current_cap > 0 else 0,
            reason=reason,
            urgency=urgency,
            estimated_cost_change=cost_change
        )


class WhatIfAnalyzer:
    """Анализатор "что если" """
    
    def __init__(self, forecast_engine: ForecastEngine):
        self.forecast_engine = forecast_engine
        
    def analyze(self, resources: List[Resource], scenario_name: str,
                 changes: Dict[str, Any]) -> WhatIfScenario:
        """Анализ сценария"""
        scenario = WhatIfScenario(
            scenario_id=f"scenario_{uuid.uuid4().hex[:8]}",
            name=scenario_name,
            changes=changes
        )
        
        # Применяем изменения
        user_growth = changes.get("user_growth", 0) / 100  # %
        traffic_increase = changes.get("traffic_increase", 0) / 100
        
        multiplier = 1 + max(user_growth, traffic_increase)
        
        total_cost_impact = 0
        
        for resource in resources:
            current = resource.current_usage
            projected = current * multiplier
            capacity = resource.total_capacity
            
            utilization = (projected / capacity * 100) if capacity > 0 else 0
            
            scenario.resource_impact[resource.resource_id] = {
                "name": resource.name,
                "current_usage": current,
                "projected_usage": projected,
                "capacity": capacity,
                "utilization_percent": utilization,
                "change_percent": (multiplier - 1) * 100
            }
            
            # Если нужно масштабирование
            if utilization > 85:
                additional_capacity = projected / 0.7 - capacity
                # Упрощённый расчёт стоимости
                total_cost_impact += additional_capacity * 10  # $10/unit
                
                scenario.risks.append(
                    f"{resource.name} will exceed capacity ({utilization:.0f}%)"
                )
                
        scenario.cost_impact = total_cost_impact
        
        return scenario


class CapacityPlanningPlatform:
    """Платформа планирования ёмкости"""
    
    def __init__(self):
        self.resources: Dict[str, Resource] = {}
        self.plans: Dict[str, CapacityPlan] = {}
        
        self.forecast_engine = ForecastEngine()
        self.bottleneck_detector = BottleneckDetector()
        self.recommendation_engine = RecommendationEngine()
        self.what_if_analyzer = WhatIfAnalyzer(self.forecast_engine)
        
    def add_resource(self, name: str, resource_type: ResourceType,
                      total_capacity: float, current_usage: float,
                      **kwargs) -> Resource:
        """Добавление ресурса"""
        resource = Resource(
            resource_id=f"res_{uuid.uuid4().hex[:8]}",
            name=name,
            resource_type=resource_type,
            total_capacity=total_capacity,
            current_usage=current_usage,
            **kwargs
        )
        self.resources[resource.resource_id] = resource
        return resource
        
    def record_metric(self, resource_id: str, value: float):
        """Запись метрики"""
        resource = self.resources.get(resource_id)
        if resource:
            resource.metrics.append(ResourceMetric(
                timestamp=datetime.now(),
                value=value,
                unit=resource.unit
            ))
            resource.current_usage = value
            
    def simulate_history(self, resource_id: str, days: int = 30,
                          growth_rate: float = 0.05):
        """Симуляция исторических данных"""
        resource = self.resources.get(resource_id)
        if not resource:
            return
            
        base_value = resource.current_usage * 0.7  # Начальное значение
        daily_growth = growth_rate / 30
        
        for i in range(days):
            timestamp = datetime.now() - timedelta(days=days-i)
            # Добавляем немного шума
            noise = random.uniform(-0.05, 0.05)
            value = base_value * (1 + daily_growth * i) * (1 + noise)
            
            resource.metrics.append(ResourceMetric(
                timestamp=timestamp,
                value=value,
                unit=resource.unit
            ))
            
    def get_forecast(self, resource_id: str, days: int = 90) -> Forecast:
        """Получение прогноза"""
        resource = self.resources.get(resource_id)
        if not resource:
            raise ValueError(f"Resource {resource_id} not found")
            
        return self.forecast_engine.forecast(resource, days)
        
    def detect_bottlenecks(self) -> List[Bottleneck]:
        """Обнаружение узких мест"""
        return self.bottleneck_detector.detect(list(self.resources.values()))
        
    def get_recommendation(self, resource_id: str) -> ScalingRecommendation:
        """Получение рекомендации"""
        resource = self.resources.get(resource_id)
        if not resource:
            raise ValueError(f"Resource {resource_id} not found")
            
        forecast = self.forecast_engine.forecast(resource)
        return self.recommendation_engine.generate(resource, forecast)
        
    def create_capacity_plan(self, name: str, resource_ids: List[str] = None,
                              horizon_days: int = 90) -> CapacityPlan:
        """Создание плана ёмкости"""
        resource_ids = resource_ids or list(self.resources.keys())
        
        plan = CapacityPlan(
            plan_id=f"plan_{uuid.uuid4().hex[:8]}",
            name=name,
            resources=resource_ids,
            end_date=datetime.now() + timedelta(days=horizon_days)
        )
        
        total_current_cost = 0
        total_projected_cost = 0
        
        for res_id in resource_ids:
            resource = self.resources.get(res_id)
            if not resource:
                continue
                
            # Прогноз
            forecast = self.forecast_engine.forecast(resource, horizon_days)
            plan.forecasts[res_id] = forecast
            
            # Рекомендация
            recommendation = self.recommendation_engine.generate(resource, forecast)
            
            if recommendation.action != ScalingAction.NO_ACTION:
                plan.recommendations.append({
                    "resource": resource.name,
                    "action": recommendation.action.value,
                    "reason": recommendation.reason,
                    "cost_change": recommendation.estimated_cost_change,
                    "urgency": recommendation.urgency.value
                })
                
            # Стоимость
            unit_cost = self.recommendation_engine.cost_per_unit.get(resource.resource_type, 0)
            total_current_cost += resource.total_capacity * unit_cost
            total_projected_cost += recommendation.recommended_capacity * unit_cost
            
        plan.current_cost = total_current_cost
        plan.projected_cost = total_projected_cost
        
        self.plans[plan.plan_id] = plan
        return plan
        
    def run_what_if(self, scenario_name: str, changes: Dict[str, Any]) -> WhatIfScenario:
        """Запуск what-if анализа"""
        return self.what_if_analyzer.analyze(
            list(self.resources.values()),
            scenario_name,
            changes
        )
        
    def get_stats(self) -> Dict[str, Any]:
        """Статистика"""
        total_resources = len(self.resources)
        
        # Утилизация
        high_utilization = 0
        for resource in self.resources.values():
            util = (resource.current_usage / resource.total_capacity * 100) if resource.total_capacity > 0 else 0
            if util > 70:
                high_utilization += 1
                
        return {
            "total_resources": total_resources,
            "high_utilization_resources": high_utilization,
            "capacity_plans": len(self.plans),
            "forecast_models": len(self.forecast_engine.models)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 83: Capacity Planning Platform")
    print("=" * 60)
    
    async def demo():
        platform = CapacityPlanningPlatform()
        print("✓ Capacity Planning Platform created")
        
        # Добавление ресурсов
        print("\n📊 Adding Resources...")
        
        api_cpu = platform.add_resource(
            "API Server CPU",
            ResourceType.CPU,
            total_capacity=32,  # cores
            current_usage=22,
            unit="cores",
            service="api-gateway",
            environment="production",
            warning_threshold=70,
            critical_threshold=85
        )
        print(f"  ✓ {api_cpu.name}: {api_cpu.current_usage}/{api_cpu.total_capacity} {api_cpu.unit}")
        
        api_memory = platform.add_resource(
            "API Server Memory",
            ResourceType.MEMORY,
            total_capacity=128,  # GB
            current_usage=95,
            unit="GB",
            service="api-gateway",
            environment="production"
        )
        print(f"  ✓ {api_memory.name}: {api_memory.current_usage}/{api_memory.total_capacity} {api_memory.unit}")
        
        db_storage = platform.add_resource(
            "Database Storage",
            ResourceType.STORAGE,
            total_capacity=2000,  # GB
            current_usage=1650,
            unit="GB",
            service="postgres-primary",
            environment="production"
        )
        print(f"  ✓ {db_storage.name}: {db_storage.current_usage}/{db_storage.total_capacity} {db_storage.unit}")
        
        cache_memory = platform.add_resource(
            "Redis Cache Memory",
            ResourceType.MEMORY,
            total_capacity=64,  # GB
            current_usage=28,
            unit="GB",
            service="redis-cluster",
            environment="production"
        )
        print(f"  ✓ {cache_memory.name}: {cache_memory.current_usage}/{cache_memory.total_capacity} {cache_memory.unit}")
        
        db_connections = platform.add_resource(
            "Database Connections",
            ResourceType.DATABASE,
            total_capacity=500,
            current_usage=380,
            unit="connections",
            service="postgres-primary",
            environment="production"
        )
        print(f"  ✓ {db_connections.name}: {db_connections.current_usage}/{db_connections.total_capacity} {db_connections.unit}")
        
        # Симуляция истории
        print("\n📈 Simulating Historical Data...")
        
        for res_id in platform.resources:
            growth = random.uniform(0.03, 0.08)  # 3-8% рост в месяц
            platform.simulate_history(res_id, days=30, growth_rate=growth)
            
        print(f"  ✓ Simulated 30 days of metrics for {len(platform.resources)} resources")
        
        # Текущая утилизация
        print("\n📊 Current Resource Utilization:")
        
        for resource in platform.resources.values():
            utilization = (resource.current_usage / resource.total_capacity * 100)
            
            # Визуализация бара
            bar_length = 30
            filled = int(utilization / 100 * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            # Цвет/статус
            if utilization >= 85:
                status = "🔴 CRITICAL"
            elif utilization >= 70:
                status = "🟡 WARNING"
            else:
                status = "🟢 OK"
                
            print(f"\n  {resource.name}:")
            print(f"    [{bar}] {utilization:.1f}% {status}")
            print(f"    Usage: {resource.current_usage:.1f} / {resource.total_capacity} {resource.unit}")
            
        # Обнаружение узких мест
        print("\n🔍 Bottleneck Detection:")
        
        bottlenecks = platform.detect_bottlenecks()
        
        if bottlenecks:
            for bn in bottlenecks:
                resource = platform.resources.get(bn.resource_id)
                severity_icon = "🔴" if bn.severity == AlertSeverity.CRITICAL else "🟡"
                print(f"\n  {severity_icon} {resource.name if resource else bn.resource_id}")
                print(f"     Utilization: {bn.utilization_percent:.1f}%")
                print(f"     Resolution: {bn.resolution}")
        else:
            print("  ✅ No bottlenecks detected")
            
        # Прогнозирование
        print("\n🔮 Resource Forecasting (90 days):")
        
        for resource in platform.resources.values():
            forecast = platform.get_forecast(resource.resource_id, days=90)
            
            current_util = (resource.current_usage / resource.total_capacity * 100)
            predicted_util = (forecast.predicted_usage / resource.total_capacity * 100)
            
            print(f"\n  {resource.name}:")
            print(f"    Current: {resource.current_usage:.1f} {resource.unit} ({current_util:.1f}%)")
            print(f"    Predicted: {forecast.predicted_usage:.1f} {resource.unit} ({predicted_util:.1f}%)")
            
            if forecast.exhaustion_date:
                print(f"    ⚠️ Critical capacity in: {forecast.days_until_exhaustion} days")
                print(f"       Date: {forecast.exhaustion_date.strftime('%Y-%m-%d')}")
                
        # Рекомендации по масштабированию
        print("\n📋 Scaling Recommendations:")
        
        for resource in platform.resources.values():
            rec = platform.get_recommendation(resource.resource_id)
            
            if rec.action != ScalingAction.NO_ACTION:
                action_icon = "⬆️" if rec.action in [ScalingAction.SCALE_UP, ScalingAction.SCALE_OUT] else "⬇️"
                
                print(f"\n  {action_icon} {resource.name}")
                print(f"     Action: {rec.action.value.upper()}")
                print(f"     Current: {rec.current_capacity:.0f} → Recommended: {rec.recommended_capacity:.0f}")
                print(f"     Change: {rec.change_percent:+.1f}%")
                print(f"     Cost Impact: ${rec.estimated_cost_change:+,.0f}/month")
                print(f"     Reason: {rec.reason}")
                print(f"     Urgency: {rec.urgency.value.upper()}")
                
        # Создание плана ёмкости
        print("\n📝 Creating Capacity Plan...")
        
        plan = platform.create_capacity_plan(
            "Q1 2025 Capacity Plan",
            horizon_days=90
        )
        
        print(f"\n  Plan: {plan.name}")
        print(f"  ID: {plan.plan_id}")
        print(f"  Period: {plan.start_date.strftime('%Y-%m-%d')} to {plan.end_date.strftime('%Y-%m-%d')}")
        print(f"  Resources: {len(plan.resources)}")
        
        print(f"\n  💰 Cost Analysis:")
        print(f"     Current Monthly Cost: ${plan.current_cost:,.0f}")
        print(f"     Projected Monthly Cost: ${plan.projected_cost:,.0f}")
        print(f"     Change: ${plan.projected_cost - plan.current_cost:+,.0f}")
        
        if plan.recommendations:
            print(f"\n  📋 Action Items ({len(plan.recommendations)}):")
            for i, rec in enumerate(plan.recommendations, 1):
                urgency_icon = "🔴" if rec["urgency"] == "critical" else "🟡" if rec["urgency"] == "warning" else "🔵"
                print(f"     {i}. {urgency_icon} {rec['resource']}")
                print(f"        {rec['action'].upper()}: {rec['reason']}")
                
        # What-If Analysis
        print("\n🔬 What-If Analysis:")
        
        # Сценарий 1: Рост пользователей
        scenario1 = platform.run_what_if(
            "User Growth 50%",
            {"user_growth": 50, "traffic_increase": 50}
        )
        
        print(f"\n  📊 Scenario: {scenario1.name}")
        print(f"     Changes: {scenario1.changes}")
        
        print("\n     Resource Impact:")
        for res_id, impact in scenario1.resource_impact.items():
            util = impact["utilization_percent"]
            status = "🔴" if util > 85 else "🟡" if util > 70 else "🟢"
            print(f"       {status} {impact['name']}: {impact['current_usage']:.0f} → {impact['projected_usage']:.0f} ({util:.0f}%)")
            
        if scenario1.risks:
            print("\n     ⚠️ Risks:")
            for risk in scenario1.risks:
                print(f"       • {risk}")
                
        print(f"\n     💰 Additional Cost: ${scenario1.cost_impact:,.0f}/month")
        
        # Сценарий 2: Агрессивный рост
        scenario2 = platform.run_what_if(
            "Aggressive Growth 100%",
            {"user_growth": 100, "traffic_increase": 150}
        )
        
        print(f"\n  📊 Scenario: {scenario2.name}")
        
        at_risk = sum(1 for impact in scenario2.resource_impact.values() if impact["utilization_percent"] > 70)
        critical = sum(1 for impact in scenario2.resource_impact.values() if impact["utilization_percent"] > 85)
        
        print(f"     Resources at risk: {at_risk}")
        print(f"     Resources critical: {critical}")
        print(f"     Additional Cost: ${scenario2.cost_impact:,.0f}/month")
        
        # Статистика
        print("\n📈 Platform Statistics:")
        stats = platform.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
        # Summary
        print("\n📊 Capacity Summary Dashboard:")
        print("  ┌─────────────────────────────────────────┐")
        
        for resource in platform.resources.values():
            util = (resource.current_usage / resource.total_capacity * 100)
            bar = "█" * int(util/10) + "░" * (10 - int(util/10))
            status = "🔴" if util > 85 else "🟡" if util > 70 else "🟢"
            name = resource.name[:25].ljust(25)
            print(f"  │ {status} {name} [{bar}] {util:5.1f}% │")
            
        print("  └─────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Capacity Planning Platform initialized!")
    print("=" * 60)
