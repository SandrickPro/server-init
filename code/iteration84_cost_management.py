#!/usr/bin/env python3
"""
Server Init - Iteration 84: Cost Management / FinOps Platform
Платформа управления затратами / FinOps

Функционал:
- Cost Tracking - отслеживание затрат
- Budget Management - управление бюджетами
- Cost Allocation - распределение затрат
- Anomaly Detection - обнаружение аномалий
- Optimization Recommendations - рекомендации по оптимизации
- Chargeback/Showback - возврат/отображение затрат
- Cost Forecasting - прогнозирование затрат
- Savings Plans - планы экономии
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


class CloudProvider(Enum):
    """Облачный провайдер"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    ON_PREMISE = "on_premise"
    MULTI_CLOUD = "multi_cloud"


class CostCategory(Enum):
    """Категория затрат"""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    ANALYTICS = "analytics"
    SECURITY = "security"
    SUPPORT = "support"
    OTHER = "other"


class BudgetPeriod(Enum):
    """Период бюджета"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class AlertType(Enum):
    """Тип алерта"""
    BUDGET_THRESHOLD = "budget_threshold"
    ANOMALY = "anomaly"
    OPTIMIZATION = "optimization"
    FORECAST_OVERRUN = "forecast_overrun"


class OptimizationType(Enum):
    """Тип оптимизации"""
    RIGHTSIZING = "rightsizing"
    RESERVED_INSTANCES = "reserved_instances"
    SPOT_INSTANCES = "spot_instances"
    UNUSED_RESOURCES = "unused_resources"
    SCHEDULING = "scheduling"


@dataclass
class CostEntry:
    """Запись о затратах"""
    entry_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Сумма
    amount: float = 0.0
    currency: str = "USD"
    
    # Категоризация
    provider: CloudProvider = CloudProvider.AWS
    category: CostCategory = CostCategory.COMPUTE
    service: str = ""
    
    # Теги
    project: str = ""
    team: str = ""
    environment: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Ресурс
    resource_id: str = ""
    resource_name: str = ""


@dataclass
class Budget:
    """Бюджет"""
    budget_id: str
    name: str = ""
    
    # Лимит
    limit: float = 0.0
    currency: str = "USD"
    period: BudgetPeriod = BudgetPeriod.MONTHLY
    
    # Текущее состояние
    spent: float = 0.0
    remaining: float = 0.0
    
    # Пороги алертов (% от бюджета)
    alert_thresholds: List[float] = field(default_factory=lambda: [50, 80, 90, 100])
    triggered_thresholds: Set[float] = field(default_factory=set)
    
    # Фильтры
    filters: Dict[str, Any] = field(default_factory=dict)
    # {"project": "api-gateway", "team": "platform", ...}
    
    # Владелец
    owner: str = ""
    
    # Период
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    
    # Статус
    is_active: bool = True


@dataclass
class CostAllocation:
    """Распределение затрат"""
    allocation_id: str
    
    # Период
    period_start: datetime = field(default_factory=datetime.now)
    period_end: Optional[datetime] = None
    
    # Распределение по измерениям
    by_team: Dict[str, float] = field(default_factory=dict)
    by_project: Dict[str, float] = field(default_factory=dict)
    by_environment: Dict[str, float] = field(default_factory=dict)
    by_category: Dict[str, float] = field(default_factory=dict)
    by_provider: Dict[str, float] = field(default_factory=dict)
    
    # Общая сумма
    total: float = 0.0


@dataclass
class CostAnomaly:
    """Аномалия затрат"""
    anomaly_id: str
    
    # Время обнаружения
    detected_at: datetime = field(default_factory=datetime.now)
    
    # Детали
    dimension: str = ""  # team, project, service
    dimension_value: str = ""
    
    # Значения
    expected_cost: float = 0.0
    actual_cost: float = 0.0
    deviation_percent: float = 0.0
    
    # Причина (если известна)
    root_cause: str = ""
    
    # Статус
    status: str = "open"  # open, investigating, resolved, ignored
    
    # Влияние
    impact_amount: float = 0.0


@dataclass
class OptimizationRecommendation:
    """Рекомендация по оптимизации"""
    recommendation_id: str
    
    # Тип
    optimization_type: OptimizationType = OptimizationType.RIGHTSIZING
    
    # Ресурс
    resource_id: str = ""
    resource_name: str = ""
    
    # Потенциальная экономия
    monthly_savings: float = 0.0
    annual_savings: float = 0.0
    
    # Детали
    current_state: str = ""
    recommended_state: str = ""
    description: str = ""
    
    # Сложность реализации
    effort: str = "low"  # low, medium, high
    
    # Риск
    risk: str = "low"
    
    # Статус
    status: str = "pending"  # pending, approved, implemented, rejected
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SavingsPlan:
    """План экономии"""
    plan_id: str
    name: str = ""
    
    # Тип
    plan_type: str = "savings_plan"  # savings_plan, reserved_instance, spot
    
    # Коммитмент
    commitment_amount: float = 0.0  # $/hour
    term_months: int = 12
    
    # Покрытие
    coverage_percent: float = 0.0
    
    # Экономия
    estimated_savings: float = 0.0
    actual_savings: float = 0.0
    
    # Утилизация
    utilization_percent: float = 0.0
    
    # Период
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    
    # Статус
    status: str = "active"


@dataclass
class ChargebackReport:
    """Отчёт о возврате затрат"""
    report_id: str
    
    # Период
    period_start: datetime = field(default_factory=datetime.now)
    period_end: Optional[datetime] = None
    
    # Распределение по командам
    team_charges: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    # {"team_name": {"total": x, "compute": y, "storage": z, ...}}
    
    # Общая сумма
    total_charges: float = 0.0
    
    # Shared costs
    shared_cost_allocation: Dict[str, float] = field(default_factory=dict)
    
    # Статус
    status: str = "draft"  # draft, pending_approval, approved, sent


class CostTracker:
    """Трекер затрат"""
    
    def __init__(self):
        self.entries: List[CostEntry] = []
        
    def record(self, amount: float, category: CostCategory, service: str,
               provider: CloudProvider = CloudProvider.AWS, **kwargs) -> CostEntry:
        """Запись затрат"""
        entry = CostEntry(
            entry_id=f"cost_{uuid.uuid4().hex[:8]}",
            amount=amount,
            category=category,
            service=service,
            provider=provider,
            **kwargs
        )
        self.entries.append(entry)
        return entry
        
    def get_total(self, start_date: datetime = None, end_date: datetime = None,
                   filters: Dict[str, Any] = None) -> float:
        """Получение общей суммы"""
        total = 0
        
        for entry in self.entries:
            # Фильтр по дате
            if start_date and entry.timestamp < start_date:
                continue
            if end_date and entry.timestamp > end_date:
                continue
                
            # Фильтры
            if filters:
                match = True
                if "project" in filters and entry.project != filters["project"]:
                    match = False
                if "team" in filters and entry.team != filters["team"]:
                    match = False
                if "category" in filters and entry.category.value != filters["category"]:
                    match = False
                if not match:
                    continue
                    
            total += entry.amount
            
        return total
        
    def get_by_dimension(self, dimension: str, start_date: datetime = None,
                          end_date: datetime = None) -> Dict[str, float]:
        """Группировка по измерению"""
        result = defaultdict(float)
        
        for entry in self.entries:
            if start_date and entry.timestamp < start_date:
                continue
            if end_date and entry.timestamp > end_date:
                continue
                
            if dimension == "team":
                key = entry.team or "unknown"
            elif dimension == "project":
                key = entry.project or "unknown"
            elif dimension == "category":
                key = entry.category.value
            elif dimension == "provider":
                key = entry.provider.value
            elif dimension == "service":
                key = entry.service or "unknown"
            elif dimension == "environment":
                key = entry.environment or "unknown"
            else:
                key = "unknown"
                
            result[key] += entry.amount
            
        return dict(result)


class BudgetManager:
    """Менеджер бюджетов"""
    
    def __init__(self, cost_tracker: CostTracker):
        self.budgets: Dict[str, Budget] = {}
        self.cost_tracker = cost_tracker
        self.alerts: List[Dict[str, Any]] = []
        
    def create_budget(self, name: str, limit: float, period: BudgetPeriod,
                       filters: Dict[str, Any] = None, **kwargs) -> Budget:
        """Создание бюджета"""
        budget = Budget(
            budget_id=f"budget_{uuid.uuid4().hex[:8]}",
            name=name,
            limit=limit,
            period=period,
            remaining=limit,
            filters=filters or {},
            **kwargs
        )
        self.budgets[budget.budget_id] = budget
        return budget
        
    def update_spending(self, budget_id: str) -> Budget:
        """Обновление расходов"""
        budget = self.budgets.get(budget_id)
        if not budget:
            raise ValueError(f"Budget {budget_id} not found")
            
        # Определяем период
        now = datetime.now()
        if budget.period == BudgetPeriod.DAILY:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif budget.period == BudgetPeriod.MONTHLY:
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start = budget.start_date
            
        # Считаем затраты
        spent = self.cost_tracker.get_total(start_date=start, filters=budget.filters)
        budget.spent = spent
        budget.remaining = budget.limit - spent
        
        # Проверяем пороги
        spent_percent = (spent / budget.limit * 100) if budget.limit > 0 else 0
        
        for threshold in budget.alert_thresholds:
            if spent_percent >= threshold and threshold not in budget.triggered_thresholds:
                budget.triggered_thresholds.add(threshold)
                self.alerts.append({
                    "type": AlertType.BUDGET_THRESHOLD.value,
                    "budget_id": budget_id,
                    "budget_name": budget.name,
                    "threshold": threshold,
                    "spent_percent": spent_percent,
                    "timestamp": datetime.now()
                })
                
        return budget


class AnomalyDetector:
    """Детектор аномалий"""
    
    def __init__(self, cost_tracker: CostTracker, threshold_percent: float = 30):
        self.cost_tracker = cost_tracker
        self.threshold_percent = threshold_percent
        self.anomalies: List[CostAnomaly] = []
        
    def detect(self, dimension: str = "service", lookback_days: int = 30) -> List[CostAnomaly]:
        """Обнаружение аномалий"""
        now = datetime.now()
        
        # Текущий период (последние 24 часа)
        current_start = now - timedelta(days=1)
        current_costs = self.cost_tracker.get_by_dimension(dimension, start_date=current_start)
        
        # Исторический период
        history_start = now - timedelta(days=lookback_days)
        history_end = current_start
        history_costs = self.cost_tracker.get_by_dimension(dimension, start_date=history_start, end_date=history_end)
        
        # Средние затраты за день
        days = lookback_days - 1
        avg_costs = {k: v / days for k, v in history_costs.items()}
        
        detected = []
        
        for dim_value, current in current_costs.items():
            expected = avg_costs.get(dim_value, 0)
            
            if expected > 0:
                deviation = ((current - expected) / expected) * 100
                
                if abs(deviation) > self.threshold_percent:
                    anomaly = CostAnomaly(
                        anomaly_id=f"anomaly_{uuid.uuid4().hex[:8]}",
                        dimension=dimension,
                        dimension_value=dim_value,
                        expected_cost=expected,
                        actual_cost=current,
                        deviation_percent=deviation,
                        impact_amount=current - expected
                    )
                    detected.append(anomaly)
                    self.anomalies.append(anomaly)
                    
        return detected


class OptimizationEngine:
    """Движок оптимизации"""
    
    def __init__(self):
        self.recommendations: List[OptimizationRecommendation] = []
        
    def analyze_rightsizing(self, resources: List[Dict[str, Any]]) -> List[OptimizationRecommendation]:
        """Анализ оптимизации размера"""
        recs = []
        
        for resource in resources:
            utilization = resource.get("cpu_utilization", 100)
            current_type = resource.get("instance_type", "unknown")
            cost = resource.get("monthly_cost", 0)
            
            if utilization < 30:
                # Рекомендуем уменьшить
                potential_savings = cost * 0.4
                
                rec = OptimizationRecommendation(
                    recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
                    optimization_type=OptimizationType.RIGHTSIZING,
                    resource_id=resource.get("id", ""),
                    resource_name=resource.get("name", ""),
                    monthly_savings=potential_savings,
                    annual_savings=potential_savings * 12,
                    current_state=f"{current_type} ({utilization:.0f}% utilized)",
                    recommended_state="Smaller instance type",
                    description=f"Low CPU utilization ({utilization:.0f}%). Consider downsizing.",
                    effort="low"
                )
                recs.append(rec)
                self.recommendations.append(rec)
                
        return recs
        
    def analyze_unused_resources(self, resources: List[Dict[str, Any]]) -> List[OptimizationRecommendation]:
        """Анализ неиспользуемых ресурсов"""
        recs = []
        
        for resource in resources:
            last_activity = resource.get("last_activity_days", 0)
            cost = resource.get("monthly_cost", 0)
            
            if last_activity > 30:
                rec = OptimizationRecommendation(
                    recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
                    optimization_type=OptimizationType.UNUSED_RESOURCES,
                    resource_id=resource.get("id", ""),
                    resource_name=resource.get("name", ""),
                    monthly_savings=cost,
                    annual_savings=cost * 12,
                    current_state=f"Idle for {last_activity} days",
                    recommended_state="Delete or archive",
                    description=f"Resource has been idle for {last_activity} days.",
                    effort="low"
                )
                recs.append(rec)
                self.recommendations.append(rec)
                
        return recs
        
    def analyze_reserved_instances(self, on_demand_spend: float, 
                                     usage_hours: Dict[str, float]) -> List[OptimizationRecommendation]:
        """Анализ Reserved Instances"""
        recs = []
        
        # Находим стабильное использование
        stable_hours = sum(h for h in usage_hours.values() if h > 700)  # ~730 часов в месяц
        stable_spend = stable_hours / sum(usage_hours.values()) * on_demand_spend if usage_hours else 0
        
        if stable_spend > 1000:  # Минимум $1000 в месяц для RI
            # RI даёт ~30% экономии
            savings = stable_spend * 0.3
            
            rec = OptimizationRecommendation(
                recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
                optimization_type=OptimizationType.RESERVED_INSTANCES,
                resource_id="compute-pool",
                resource_name="Compute instances",
                monthly_savings=savings,
                annual_savings=savings * 12,
                current_state=f"On-demand spend: ${on_demand_spend:,.0f}/month",
                recommended_state=f"Reserved Instances commitment: ${stable_spend:,.0f}/month",
                description="Stable workloads identified. Consider Reserved Instances.",
                effort="medium"
            )
            recs.append(rec)
            self.recommendations.append(rec)
            
        return recs
        
    def get_total_savings(self) -> Dict[str, float]:
        """Общая потенциальная экономия"""
        pending = [r for r in self.recommendations if r.status == "pending"]
        
        return {
            "monthly": sum(r.monthly_savings for r in pending),
            "annual": sum(r.annual_savings for r in pending),
            "count": len(pending)
        }


class CostAllocator:
    """Аллокатор затрат"""
    
    def __init__(self, cost_tracker: CostTracker):
        self.cost_tracker = cost_tracker
        
    def allocate(self, start_date: datetime = None, end_date: datetime = None) -> CostAllocation:
        """Распределение затрат"""
        allocation = CostAllocation(
            allocation_id=f"alloc_{uuid.uuid4().hex[:8]}",
            period_start=start_date or datetime.now().replace(day=1),
            period_end=end_date
        )
        
        allocation.by_team = self.cost_tracker.get_by_dimension("team", start_date, end_date)
        allocation.by_project = self.cost_tracker.get_by_dimension("project", start_date, end_date)
        allocation.by_environment = self.cost_tracker.get_by_dimension("environment", start_date, end_date)
        allocation.by_category = self.cost_tracker.get_by_dimension("category", start_date, end_date)
        allocation.by_provider = self.cost_tracker.get_by_dimension("provider", start_date, end_date)
        
        allocation.total = self.cost_tracker.get_total(start_date, end_date)
        
        return allocation
        
    def generate_chargeback(self, start_date: datetime = None, 
                             end_date: datetime = None,
                             shared_cost_method: str = "proportional") -> ChargebackReport:
        """Генерация отчёта chargeback"""
        report = ChargebackReport(
            report_id=f"cb_{uuid.uuid4().hex[:8]}",
            period_start=start_date or datetime.now().replace(day=1),
            period_end=end_date
        )
        
        # Затраты по командам
        team_costs = self.cost_tracker.get_by_dimension("team", start_date, end_date)
        total = sum(team_costs.values())
        
        # Shared costs (например, 20% от общих затрат)
        shared_percent = 0.2
        shared_total = total * shared_percent
        direct_total = total - shared_total
        
        # Распределяем shared costs
        if shared_cost_method == "proportional":
            # Пропорционально прямым затратам
            for team, direct_cost in team_costs.items():
                proportion = direct_cost / direct_total if direct_total > 0 else 0
                shared_allocation = shared_total * proportion
                
                report.team_charges[team] = {
                    "direct_cost": direct_cost * (1 - shared_percent),
                    "shared_cost": shared_allocation,
                    "total": direct_cost * (1 - shared_percent) + shared_allocation
                }
                report.shared_cost_allocation[team] = shared_allocation
        else:
            # Равномерно
            team_count = len(team_costs)
            shared_per_team = shared_total / team_count if team_count > 0 else 0
            
            for team, direct_cost in team_costs.items():
                report.team_charges[team] = {
                    "direct_cost": direct_cost * (1 - shared_percent),
                    "shared_cost": shared_per_team,
                    "total": direct_cost * (1 - shared_percent) + shared_per_team
                }
                report.shared_cost_allocation[team] = shared_per_team
                
        report.total_charges = total
        
        return report


class CostForecaster:
    """Прогнозирование затрат"""
    
    def __init__(self, cost_tracker: CostTracker):
        self.cost_tracker = cost_tracker
        
    def forecast(self, days: int = 30, growth_rate: float = None) -> Dict[str, Any]:
        """Прогноз затрат"""
        # Исторические данные
        now = datetime.now()
        history_start = now - timedelta(days=30)
        
        historical = self.cost_tracker.get_total(start_date=history_start)
        daily_avg = historical / 30
        
        # Определяем темп роста
        if growth_rate is None:
            # Упрощённый расчёт: используем последние 30 дней vs предыдущие 30
            prev_start = now - timedelta(days=60)
            prev_end = now - timedelta(days=30)
            previous = self.cost_tracker.get_total(start_date=prev_start, end_date=prev_end)
            
            if previous > 0:
                growth_rate = (historical - previous) / previous
            else:
                growth_rate = 0.05  # По умолчанию 5%
                
        # Прогноз
        projected_daily = daily_avg * (1 + growth_rate / 30)
        projected_total = projected_daily * days
        
        # Доверительный интервал (±15%)
        confidence = projected_total * 0.15
        
        return {
            "forecast_days": days,
            "historical_daily_avg": daily_avg,
            "projected_daily_avg": projected_daily,
            "projected_total": projected_total,
            "confidence_lower": projected_total - confidence,
            "confidence_upper": projected_total + confidence,
            "growth_rate": growth_rate * 100,  # %
            "forecast_date": (now + timedelta(days=days)).isoformat()
        }
        
    def forecast_by_dimension(self, dimension: str, days: int = 30) -> Dict[str, Dict[str, float]]:
        """Прогноз по измерению"""
        now = datetime.now()
        history_start = now - timedelta(days=30)
        
        historical = self.cost_tracker.get_by_dimension(dimension, start_date=history_start)
        
        result = {}
        for key, total in historical.items():
            daily_avg = total / 30
            projected = daily_avg * days
            
            result[key] = {
                "historical_monthly": total,
                "daily_avg": daily_avg,
                "projected": projected
            }
            
        return result


class CostManagementPlatform:
    """Платформа управления затратами"""
    
    def __init__(self):
        self.cost_tracker = CostTracker()
        self.budget_manager = BudgetManager(self.cost_tracker)
        self.anomaly_detector = AnomalyDetector(self.cost_tracker)
        self.optimization_engine = OptimizationEngine()
        self.cost_allocator = CostAllocator(self.cost_tracker)
        self.cost_forecaster = CostForecaster(self.cost_tracker)
        
        self.savings_plans: Dict[str, SavingsPlan] = {}
        
    def record_cost(self, amount: float, category: CostCategory, service: str,
                     **kwargs) -> CostEntry:
        """Запись затрат"""
        return self.cost_tracker.record(amount, category, service, **kwargs)
        
    def create_budget(self, name: str, limit: float, period: BudgetPeriod = BudgetPeriod.MONTHLY,
                       **kwargs) -> Budget:
        """Создание бюджета"""
        return self.budget_manager.create_budget(name, limit, period, **kwargs)
        
    def check_budgets(self) -> List[Budget]:
        """Проверка всех бюджетов"""
        results = []
        for budget_id in self.budget_manager.budgets:
            budget = self.budget_manager.update_spending(budget_id)
            results.append(budget)
        return results
        
    def detect_anomalies(self, dimension: str = "service") -> List[CostAnomaly]:
        """Обнаружение аномалий"""
        return self.anomaly_detector.detect(dimension)
        
    def get_optimization_recommendations(self, resources: List[Dict[str, Any]]) -> List[OptimizationRecommendation]:
        """Получение рекомендаций по оптимизации"""
        recs = []
        recs.extend(self.optimization_engine.analyze_rightsizing(resources))
        recs.extend(self.optimization_engine.analyze_unused_resources(resources))
        return recs
        
    def get_cost_allocation(self) -> CostAllocation:
        """Получение распределения затрат"""
        return self.cost_allocator.allocate()
        
    def get_chargeback_report(self) -> ChargebackReport:
        """Получение отчёта chargeback"""
        return self.cost_allocator.generate_chargeback()
        
    def get_forecast(self, days: int = 30) -> Dict[str, Any]:
        """Прогноз затрат"""
        return self.cost_forecaster.forecast(days)
        
    def add_savings_plan(self, name: str, commitment: float, 
                          term_months: int = 12, **kwargs) -> SavingsPlan:
        """Добавление плана экономии"""
        plan = SavingsPlan(
            plan_id=f"sp_{uuid.uuid4().hex[:8]}",
            name=name,
            commitment_amount=commitment,
            term_months=term_months,
            end_date=datetime.now() + timedelta(days=term_months * 30),
            **kwargs
        )
        self.savings_plans[plan.plan_id] = plan
        return plan
        
    def get_summary(self) -> Dict[str, Any]:
        """Сводка по затратам"""
        # Текущий месяц
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        mtd_spend = self.cost_tracker.get_total(start_date=month_start)
        by_category = self.cost_tracker.get_by_dimension("category", start_date=month_start)
        
        # Прогноз
        forecast = self.cost_forecaster.forecast(days=30)
        
        # Оптимизация
        savings = self.optimization_engine.get_total_savings()
        
        # Бюджеты
        budgets_at_risk = sum(1 for b in self.budget_manager.budgets.values() 
                              if b.spent / b.limit > 0.8)
        
        return {
            "mtd_spend": mtd_spend,
            "projected_month_end": forecast["projected_total"],
            "spend_by_category": by_category,
            "potential_savings": savings["monthly"],
            "optimization_recommendations": savings["count"],
            "budgets_total": len(self.budget_manager.budgets),
            "budgets_at_risk": budgets_at_risk,
            "savings_plans": len(self.savings_plans)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 84: Cost Management / FinOps Platform")
    print("=" * 60)
    
    async def demo():
        platform = CostManagementPlatform()
        print("✓ Cost Management Platform created")
        
        # Генерация исторических данных
        print("\n📊 Generating Historical Cost Data...")
        
        services = [
            ("EC2", CostCategory.COMPUTE, "platform", "production", 5000),
            ("RDS", CostCategory.DATABASE, "platform", "production", 2500),
            ("S3", CostCategory.STORAGE, "data", "production", 800),
            ("Lambda", CostCategory.COMPUTE, "api", "production", 600),
            ("ELB", CostCategory.NETWORK, "platform", "production", 400),
            ("CloudWatch", CostCategory.ANALYTICS, "ops", "production", 300),
            ("Route53", CostCategory.NETWORK, "platform", "production", 50),
            ("EC2", CostCategory.COMPUTE, "platform", "staging", 1200),
            ("RDS", CostCategory.DATABASE, "platform", "staging", 600),
            ("EKS", CostCategory.COMPUTE, "platform", "production", 3000),
        ]
        
        now = datetime.now()
        
        for day in range(60):
            date = now - timedelta(days=day)
            # Добавляем небольшой рост со временем
            growth_factor = 1 + (60 - day) * 0.001  # ~6% рост за 2 месяца
            
            for service, category, team, env, base_cost in services:
                daily_cost = base_cost / 30 * growth_factor
                # Добавляем случайную вариацию
                daily_cost *= random.uniform(0.85, 1.15)
                
                platform.record_cost(
                    daily_cost,
                    category,
                    service,
                    team=team,
                    environment=env,
                    provider=CloudProvider.AWS,
                    project=f"{team}-main"
                )
                
        total_costs = len(platform.cost_tracker.entries)
        print(f"  ✓ Generated {total_costs} cost entries over 60 days")
        
        # Текущий месяц
        print("\n💰 Current Month-to-Date Spend:")
        
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        mtd_total = platform.cost_tracker.get_total(start_date=month_start)
        
        by_category = platform.cost_tracker.get_by_dimension("category", start_date=month_start)
        
        print(f"\n  Total MTD: ${mtd_total:,.2f}")
        print("\n  By Category:")
        for cat, amount in sorted(by_category.items(), key=lambda x: -x[1]):
            bar = "█" * int(amount / mtd_total * 30)
            pct = amount / mtd_total * 100
            print(f"    {cat:12} ${amount:>10,.2f} ({pct:5.1f}%) {bar}")
            
        by_team = platform.cost_tracker.get_by_dimension("team", start_date=month_start)
        print("\n  By Team:")
        for team, amount in sorted(by_team.items(), key=lambda x: -x[1]):
            pct = amount / mtd_total * 100
            print(f"    {team:12} ${amount:>10,.2f} ({pct:5.1f}%)")
            
        # Создание бюджетов
        print("\n📋 Creating Budgets...")
        
        platform_budget = platform.create_budget(
            "Platform Team Budget",
            limit=10000,
            period=BudgetPeriod.MONTHLY,
            filters={"team": "platform"},
            owner="platform-lead@company.com"
        )
        print(f"  ✓ {platform_budget.name}: ${platform_budget.limit:,.0f}/month")
        
        overall_budget = platform.create_budget(
            "Overall Cloud Budget",
            limit=20000,
            period=BudgetPeriod.MONTHLY,
            owner="finance@company.com"
        )
        print(f"  ✓ {overall_budget.name}: ${overall_budget.limit:,.0f}/month")
        
        # Проверка бюджетов
        print("\n📊 Budget Status:")
        
        budgets = platform.check_budgets()
        
        for budget in budgets:
            spent_pct = (budget.spent / budget.limit * 100) if budget.limit > 0 else 0
            remaining_pct = 100 - spent_pct
            
            bar_length = 30
            filled = int(spent_pct / 100 * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            status = "🔴" if spent_pct >= 90 else "🟡" if spent_pct >= 80 else "🟢"
            
            print(f"\n  {status} {budget.name}")
            print(f"     [{bar}] {spent_pct:.1f}%")
            print(f"     Spent: ${budget.spent:,.2f} / ${budget.limit:,.2f}")
            print(f"     Remaining: ${budget.remaining:,.2f}")
            
        # Алерты бюджета
        if platform.budget_manager.alerts:
            print(f"\n  ⚠️ Budget Alerts ({len(platform.budget_manager.alerts)}):")
            for alert in platform.budget_manager.alerts[-3:]:
                print(f"     • {alert['budget_name']}: {alert['threshold']}% threshold exceeded")
                
        # Обнаружение аномалий
        print("\n🔍 Anomaly Detection:")
        
        anomalies = platform.detect_anomalies("service")
        
        if anomalies:
            print(f"\n  Found {len(anomalies)} anomalies:")
            for anomaly in anomalies[:5]:
                direction = "⬆️" if anomaly.deviation_percent > 0 else "⬇️"
                print(f"\n  {direction} {anomaly.dimension_value}")
                print(f"     Expected: ${anomaly.expected_cost:,.2f}")
                print(f"     Actual: ${anomaly.actual_cost:,.2f}")
                print(f"     Deviation: {anomaly.deviation_percent:+.1f}%")
                print(f"     Impact: ${anomaly.impact_amount:+,.2f}")
        else:
            print("  ✅ No significant anomalies detected")
            
        # Рекомендации по оптимизации
        print("\n💡 Optimization Recommendations:")
        
        # Симулируем ресурсы
        simulated_resources = [
            {"id": "i-001", "name": "api-server-1", "instance_type": "m5.xlarge", 
             "cpu_utilization": 15, "monthly_cost": 150},
            {"id": "i-002", "name": "api-server-2", "instance_type": "m5.xlarge",
             "cpu_utilization": 85, "monthly_cost": 150},
            {"id": "i-003", "name": "cache-server", "instance_type": "r5.large",
             "cpu_utilization": 22, "monthly_cost": 100},
            {"id": "i-004", "name": "test-server", "instance_type": "t3.medium",
             "cpu_utilization": 5, "monthly_cost": 50, "last_activity_days": 45},
            {"id": "i-005", "name": "old-backup", "instance_type": "t3.large",
             "cpu_utilization": 0, "monthly_cost": 80, "last_activity_days": 90},
        ]
        
        recommendations = platform.get_optimization_recommendations(simulated_resources)
        
        # Reserved Instances
        platform.optimization_engine.analyze_reserved_instances(
            on_demand_spend=8000,
            usage_hours={"m5.xlarge": 730, "r5.large": 710, "t3.medium": 500}
        )
        
        all_recs = platform.optimization_engine.recommendations
        
        print(f"\n  Found {len(all_recs)} optimization opportunities:")
        
        total_monthly_savings = 0
        
        for rec in all_recs:
            icon = {
                OptimizationType.RIGHTSIZING: "📦",
                OptimizationType.UNUSED_RESOURCES: "🗑️",
                OptimizationType.RESERVED_INSTANCES: "📋",
                OptimizationType.SPOT_INSTANCES: "⚡",
                OptimizationType.SCHEDULING: "⏰"
            }.get(rec.optimization_type, "💡")
            
            print(f"\n  {icon} {rec.optimization_type.value.upper()}: {rec.resource_name}")
            print(f"     Current: {rec.current_state}")
            print(f"     Recommended: {rec.recommended_state}")
            print(f"     Monthly Savings: ${rec.monthly_savings:,.2f}")
            print(f"     Annual Savings: ${rec.annual_savings:,.2f}")
            print(f"     Effort: {rec.effort}")
            
            total_monthly_savings += rec.monthly_savings
            
        print(f"\n  📊 Total Potential Savings:")
        print(f"     Monthly: ${total_monthly_savings:,.2f}")
        print(f"     Annual: ${total_monthly_savings * 12:,.2f}")
        
        # Cost Allocation
        print("\n📊 Cost Allocation Report:")
        
        allocation = platform.get_cost_allocation()
        
        print(f"\n  Total: ${allocation.total:,.2f}")
        
        print("\n  By Environment:")
        for env, amount in sorted(allocation.by_environment.items(), key=lambda x: -x[1]):
            pct = amount / allocation.total * 100 if allocation.total > 0 else 0
            print(f"    {env:15} ${amount:>10,.2f} ({pct:5.1f}%)")
            
        # Chargeback Report
        print("\n📋 Chargeback Report:")
        
        chargeback = platform.get_chargeback_report()
        
        print(f"\n  Period: {chargeback.period_start.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}")
        print(f"  Total Charges: ${chargeback.total_charges:,.2f}")
        
        print("\n  Team Charges:")
        print("  " + "-" * 50)
        print(f"  {'Team':12} {'Direct':>12} {'Shared':>12} {'Total':>12}")
        print("  " + "-" * 50)
        
        for team, charges in sorted(chargeback.team_charges.items(), key=lambda x: -x[1]["total"]):
            print(f"  {team:12} ${charges['direct_cost']:>10,.2f} ${charges['shared_cost']:>10,.2f} ${charges['total']:>10,.2f}")
            
        # Прогноз затрат
        print("\n🔮 Cost Forecast:")
        
        forecast = platform.get_forecast(days=30)
        
        print(f"\n  Next 30 Days:")
        print(f"    Projected Total: ${forecast['projected_total']:,.2f}")
        print(f"    Confidence Range: ${forecast['confidence_lower']:,.2f} - ${forecast['confidence_upper']:,.2f}")
        print(f"    Daily Average: ${forecast['projected_daily_avg']:,.2f}")
        print(f"    Growth Rate: {forecast['growth_rate']:+.1f}%")
        
        # Прогноз по категориям
        forecast_by_cat = platform.cost_forecaster.forecast_by_dimension("category", days=30)
        
        print("\n  By Category (30-day projection):")
        for cat, data in sorted(forecast_by_cat.items(), key=lambda x: -x[1]["projected"]):
            print(f"    {cat:12} ${data['projected']:>10,.2f}")
            
        # Savings Plans
        print("\n💰 Savings Plans:")
        
        sp1 = platform.add_savings_plan(
            "Compute Savings Plan",
            commitment=5.0,  # $5/hour
            term_months=12,
            coverage_percent=65,
            estimated_savings=2400,  # $/month
            utilization_percent=78
        )
        
        sp2 = platform.add_savings_plan(
            "EC2 Instance Savings Plan",
            commitment=3.0,  # $3/hour
            term_months=36,
            coverage_percent=45,
            estimated_savings=1800,
            utilization_percent=92
        )
        
        for plan in platform.savings_plans.values():
            print(f"\n  📋 {plan.name}")
            print(f"     Commitment: ${plan.commitment_amount}/hour (${plan.commitment_amount * 730:,.0f}/month)")
            print(f"     Term: {plan.term_months} months")
            print(f"     Coverage: {plan.coverage_percent}%")
            print(f"     Utilization: {plan.utilization_percent}%")
            print(f"     Est. Savings: ${plan.estimated_savings:,.0f}/month")
            
        # Summary Dashboard
        print("\n📊 Cost Management Dashboard:")
        
        summary = platform.get_summary()
        
        print("  ┌─────────────────────────────────────────────┐")
        print(f"  │ MTD Spend:        ${summary['mtd_spend']:>15,.2f}  │")
        print(f"  │ Projected Month:  ${summary['projected_month_end']:>15,.2f}  │")
        print(f"  │ Potential Savings: ${summary['potential_savings']:>14,.2f}  │")
        print(f"  │ Recommendations:  {summary['optimization_recommendations']:>17}   │")
        print(f"  │ Budgets at Risk:  {summary['budgets_at_risk']:>17}   │")
        print("  └─────────────────────────────────────────────┘")
        
        # Trend visualization
        print("\n📈 Cost Trend (Daily):")
        
        days_to_show = 7
        for i in range(days_to_show, 0, -1):
            date = now - timedelta(days=i)
            day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            daily_cost = platform.cost_tracker.get_total(start_date=day_start, end_date=day_end)
            
            bar_scale = 500  # $500 per bar unit
            bar_length = int(daily_cost / bar_scale)
            bar = "█" * min(bar_length, 40)
            
            print(f"  {date.strftime('%m/%d')} │ {bar} ${daily_cost:,.0f}")
            
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Cost Management / FinOps Platform initialized!")
    print("=" * 60)
