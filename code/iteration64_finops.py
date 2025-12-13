#!/usr/bin/env python3
"""
Server Init - Iteration 64: FinOps & Cost Management Platform
Финансовые операции и управление затратами

Функционал:
- Cost Tracking - отслеживание затрат
- Budget Management - управление бюджетами
- Resource Optimization - оптимизация ресурсов
- Cost Allocation - распределение затрат
- Anomaly Detection - обнаружение аномалий
- Forecasting - прогнозирование
- Savings Plans - планы экономии
- Chargeback/Showback - распределение расходов
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from collections import defaultdict
import uuid
import random
import math


class CostCategory(Enum):
    """Категория затрат"""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    SERVERLESS = "serverless"
    SUPPORT = "support"
    OTHER = "other"


class ResourceType(Enum):
    """Тип ресурса"""
    VIRTUAL_MACHINE = "virtual_machine"
    CONTAINER = "container"
    DATABASE = "database"
    STORAGE = "storage"
    LOAD_BALANCER = "load_balancer"
    CDN = "cdn"
    FUNCTION = "function"
    KUBERNETES = "kubernetes"


class BudgetPeriod(Enum):
    """Период бюджета"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class AlertSeverity(Enum):
    """Серьёзность алерта"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class OptimizationType(Enum):
    """Тип оптимизации"""
    RIGHTSIZING = "rightsizing"
    RESERVED_INSTANCE = "reserved_instance"
    SPOT_INSTANCE = "spot_instance"
    IDLE_RESOURCE = "idle_resource"
    UNUSED_STORAGE = "unused_storage"


@dataclass
class CostRecord:
    """Запись о затратах"""
    record_id: str
    
    # Ресурс
    resource_id: str = ""
    resource_name: str = ""
    resource_type: ResourceType = ResourceType.VIRTUAL_MACHINE
    
    # Категория
    category: CostCategory = CostCategory.COMPUTE
    
    # Затраты
    amount: float = 0.0
    currency: str = "USD"
    
    # Период
    start_date: datetime = field(default_factory=datetime.now)
    end_date: datetime = field(default_factory=datetime.now)
    
    # Метаданные
    tags: Dict[str, str] = field(default_factory=dict)
    account_id: str = ""
    region: str = ""
    
    # Распределение
    cost_center: str = ""
    project: str = ""
    team: str = ""


@dataclass
class Budget:
    """Бюджет"""
    budget_id: str
    name: str
    
    # Сумма
    amount: float = 0.0
    currency: str = "USD"
    
    # Период
    period: BudgetPeriod = BudgetPeriod.MONTHLY
    start_date: datetime = field(default_factory=datetime.now)
    
    # Фильтры
    cost_centers: List[str] = field(default_factory=list)
    projects: List[str] = field(default_factory=list)
    categories: List[CostCategory] = field(default_factory=list)
    
    # Пороги алертов (в процентах)
    alert_thresholds: List[int] = field(default_factory=lambda: [50, 80, 100])
    
    # Статус
    current_spend: float = 0.0
    forecasted_spend: float = 0.0


@dataclass
class CostAllocation:
    """Распределение затрат"""
    allocation_id: str
    name: str
    
    # Правила
    rules: List[Dict[str, Any]] = field(default_factory=list)
    
    # Распределение по умолчанию
    default_cost_center: str = ""
    
    # Статус
    enabled: bool = True
    
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Recommendation:
    """Рекомендация по оптимизации"""
    recommendation_id: str
    
    # Тип
    optimization_type: OptimizationType = OptimizationType.RIGHTSIZING
    
    # Ресурс
    resource_id: str = ""
    resource_name: str = ""
    resource_type: ResourceType = ResourceType.VIRTUAL_MACHINE
    
    # Описание
    title: str = ""
    description: str = ""
    
    # Потенциальная экономия
    estimated_savings: float = 0.0
    savings_period: str = "monthly"
    
    # Усилия
    implementation_effort: str = "low"  # low, medium, high
    
    # Статус
    status: str = "open"  # open, in_progress, implemented, dismissed
    
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SavingsPlan:
    """План экономии"""
    plan_id: str
    name: str
    
    # Тип
    plan_type: str = "compute"  # compute, ec2, sagemaker
    
    # Обязательства
    commitment_amount: float = 0.0
    commitment_term: int = 12  # месяцев
    
    # Экономия
    estimated_savings: float = 0.0
    savings_percentage: float = 0.0
    
    # Период
    start_date: datetime = field(default_factory=datetime.now)
    end_date: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=365))
    
    # Использование
    utilization_percentage: float = 0.0


@dataclass 
class CostAnomaly:
    """Аномалия затрат"""
    anomaly_id: str
    
    # Детали
    resource_id: str = ""
    resource_name: str = ""
    
    # Аномалия
    expected_cost: float = 0.0
    actual_cost: float = 0.0
    deviation_percentage: float = 0.0
    
    # Период
    detected_at: datetime = field(default_factory=datetime.now)
    anomaly_period: str = ""
    
    # Серьёзность
    severity: AlertSeverity = AlertSeverity.WARNING
    
    # Статус
    status: str = "new"  # new, acknowledged, resolved
    root_cause: str = ""


class CostTracker:
    """Отслеживатель затрат"""
    
    def __init__(self):
        self.records: List[CostRecord] = []
        
    def record_cost(self, **kwargs) -> CostRecord:
        """Запись затрат"""
        record = CostRecord(
            record_id=f"cost_{uuid.uuid4().hex[:8]}",
            **kwargs
        )
        
        self.records.append(record)
        return record
        
    def get_costs(self, start_date: datetime = None,
                   end_date: datetime = None,
                   filters: Dict[str, Any] = None) -> List[CostRecord]:
        """Получение затрат"""
        result = self.records
        
        if start_date:
            result = [r for r in result if r.start_date >= start_date]
            
        if end_date:
            result = [r for r in result if r.end_date <= end_date]
            
        if filters:
            if "category" in filters:
                result = [r for r in result if r.category == filters["category"]]
            if "cost_center" in filters:
                result = [r for r in result if r.cost_center == filters["cost_center"]]
            if "project" in filters:
                result = [r for r in result if r.project == filters["project"]]
            if "resource_type" in filters:
                result = [r for r in result if r.resource_type == filters["resource_type"]]
                
        return result
        
    def aggregate_by(self, records: List[CostRecord],
                      group_by: str) -> Dict[str, float]:
        """Агрегация по полю"""
        result = defaultdict(float)
        
        for record in records:
            key = getattr(record, group_by, "unknown")
            if isinstance(key, Enum):
                key = key.value
            result[key] += record.amount
            
        return dict(result)
        
    def get_total(self, records: List[CostRecord] = None) -> float:
        """Общая сумма затрат"""
        records = records or self.records
        return sum(r.amount for r in records)


class BudgetManager:
    """Менеджер бюджетов"""
    
    def __init__(self, cost_tracker: CostTracker):
        self.budgets: Dict[str, Budget] = {}
        self.cost_tracker = cost_tracker
        self.alerts: List[Dict[str, Any]] = []
        
    def create_budget(self, name: str, amount: float, **kwargs) -> Budget:
        """Создание бюджета"""
        budget = Budget(
            budget_id=f"budget_{uuid.uuid4().hex[:8]}",
            name=name,
            amount=amount,
            **kwargs
        )
        
        self.budgets[budget.budget_id] = budget
        return budget
        
    def update_budget_spend(self, budget_id: str) -> Dict[str, Any]:
        """Обновление расходов по бюджету"""
        budget = self.budgets.get(budget_id)
        
        if not budget:
            return {"error": "Budget not found"}
            
        # Определяем период
        now = datetime.now()
        
        if budget.period == BudgetPeriod.MONTHLY:
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif budget.period == BudgetPeriod.QUARTERLY:
            quarter_start_month = ((now.month - 1) // 3) * 3 + 1
            start = now.replace(month=quarter_start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:  # YEARLY
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            
        # Фильтры
        filters = {}
        if budget.cost_centers:
            filters["cost_center"] = budget.cost_centers[0]  # Упрощённо
        if budget.projects:
            filters["project"] = budget.projects[0]
            
        # Получаем затраты
        records = self.cost_tracker.get_costs(start_date=start, filters=filters if filters else None)
        
        budget.current_spend = self.cost_tracker.get_total(records)
        
        # Прогноз
        days_passed = (now - start).days + 1
        if budget.period == BudgetPeriod.MONTHLY:
            total_days = 30
        elif budget.period == BudgetPeriod.QUARTERLY:
            total_days = 90
        else:
            total_days = 365
            
        budget.forecasted_spend = (budget.current_spend / days_passed) * total_days if days_passed > 0 else 0
        
        # Проверяем пороги
        spend_percentage = (budget.current_spend / budget.amount * 100) if budget.amount > 0 else 0
        
        for threshold in budget.alert_thresholds:
            if spend_percentage >= threshold:
                self._create_alert(budget, threshold, spend_percentage)
                
        return {
            "budget_id": budget.budget_id,
            "current_spend": round(budget.current_spend, 2),
            "budget_amount": budget.amount,
            "spend_percentage": round(spend_percentage, 1),
            "forecasted_spend": round(budget.forecasted_spend, 2)
        }
        
    def _create_alert(self, budget: Budget, threshold: int, current: float):
        """Создание алерта"""
        alert = {
            "alert_id": f"alert_{uuid.uuid4().hex[:8]}",
            "budget_id": budget.budget_id,
            "budget_name": budget.name,
            "threshold": threshold,
            "current_percentage": round(current, 1),
            "severity": AlertSeverity.CRITICAL if threshold >= 100 else AlertSeverity.WARNING,
            "created_at": datetime.now()
        }
        
        self.alerts.append(alert)


class OptimizationEngine:
    """Движок оптимизации"""
    
    def __init__(self, cost_tracker: CostTracker):
        self.cost_tracker = cost_tracker
        self.recommendations: Dict[str, Recommendation] = {}
        
    def analyze_resources(self, resources: List[Dict[str, Any]]) -> List[Recommendation]:
        """Анализ ресурсов"""
        new_recommendations = []
        
        for resource in resources:
            # Rightsizing
            if resource.get("avg_cpu", 100) < 20 and resource.get("avg_memory", 100) < 30:
                rec = self._create_recommendation(
                    resource,
                    OptimizationType.RIGHTSIZING,
                    "Downsize underutilized resource",
                    f"Resource {resource['name']} is significantly underutilized. "
                    f"Average CPU: {resource.get('avg_cpu', 0)}%, Memory: {resource.get('avg_memory', 0)}%",
                    resource.get("monthly_cost", 0) * 0.4  # 40% экономия
                )
                new_recommendations.append(rec)
                
            # Idle resources
            if resource.get("last_used_days", 0) > 30:
                rec = self._create_recommendation(
                    resource,
                    OptimizationType.IDLE_RESOURCE,
                    "Remove idle resource",
                    f"Resource {resource['name']} hasn't been used in {resource.get('last_used_days', 0)} days",
                    resource.get("monthly_cost", 0)  # 100% экономия
                )
                new_recommendations.append(rec)
                
            # Reserved Instance
            if resource.get("running_hours_month", 0) > 600:  # > 80% времени
                potential_savings = resource.get("monthly_cost", 0) * 0.3  # 30% экономия с RI
                rec = self._create_recommendation(
                    resource,
                    OptimizationType.RESERVED_INSTANCE,
                    "Convert to Reserved Instance",
                    f"Resource {resource['name']} runs consistently and could benefit from Reserved pricing",
                    potential_savings
                )
                new_recommendations.append(rec)
                
            # Spot Instance (для interruptible workloads)
            if resource.get("interruptible", False):
                potential_savings = resource.get("monthly_cost", 0) * 0.6  # 60% экономия со Spot
                rec = self._create_recommendation(
                    resource,
                    OptimizationType.SPOT_INSTANCE,
                    "Use Spot Instances",
                    f"Resource {resource['name']} can be migrated to Spot instances",
                    potential_savings
                )
                new_recommendations.append(rec)
                
        return new_recommendations
        
    def _create_recommendation(self, resource: Dict[str, Any],
                                opt_type: OptimizationType,
                                title: str, description: str,
                                savings: float) -> Recommendation:
        """Создание рекомендации"""
        rec = Recommendation(
            recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
            optimization_type=opt_type,
            resource_id=resource.get("id", ""),
            resource_name=resource.get("name", ""),
            resource_type=resource.get("type", ResourceType.VIRTUAL_MACHINE),
            title=title,
            description=description,
            estimated_savings=round(savings, 2),
            implementation_effort="medium" if opt_type in [OptimizationType.RESERVED_INSTANCE, OptimizationType.SPOT_INSTANCE] else "low"
        )
        
        self.recommendations[rec.recommendation_id] = rec
        return rec
        
    def get_total_savings_potential(self) -> Dict[str, Any]:
        """Общий потенциал экономии"""
        open_recs = [r for r in self.recommendations.values() if r.status == "open"]
        
        total = sum(r.estimated_savings for r in open_recs)
        by_type = defaultdict(float)
        
        for rec in open_recs:
            by_type[rec.optimization_type.value] += rec.estimated_savings
            
        return {
            "total_potential_savings": round(total, 2),
            "recommendations_count": len(open_recs),
            "by_type": dict(by_type)
        }


class ForecastingEngine:
    """Движок прогнозирования"""
    
    def __init__(self, cost_tracker: CostTracker):
        self.cost_tracker = cost_tracker
        
    def forecast_costs(self, days_ahead: int = 30,
                        filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Прогнозирование затрат"""
        # Получаем исторические данные (последние 90 дней)
        now = datetime.now()
        historical_start = now - timedelta(days=90)
        
        records = self.cost_tracker.get_costs(start_date=historical_start, filters=filters)
        
        if not records:
            return {
                "forecast": [],
                "total_forecasted": 0,
                "confidence": "low"
            }
            
        # Агрегируем по дням
        daily_costs = defaultdict(float)
        for record in records:
            day_key = record.start_date.strftime("%Y-%m-%d")
            daily_costs[day_key] += record.amount
            
        if not daily_costs:
            return {
                "forecast": [],
                "total_forecasted": 0,
                "confidence": "low"
            }
            
        # Простая линейная регрессия
        values = list(daily_costs.values())
        avg = sum(values) / len(values)
        
        # Тренд
        trend = 0
        if len(values) > 7:
            first_week = sum(values[:7]) / 7
            last_week = sum(values[-7:]) / 7
            trend = (last_week - first_week) / len(values)
            
        # Прогноз
        forecast = []
        total = 0
        
        for i in range(days_ahead):
            date = now + timedelta(days=i+1)
            predicted = avg + (trend * (len(values) + i))
            predicted = max(0, predicted)  # Не отрицательные
            
            forecast.append({
                "date": date.strftime("%Y-%m-%d"),
                "predicted_cost": round(predicted, 2)
            })
            total += predicted
            
        return {
            "forecast": forecast,
            "total_forecasted": round(total, 2),
            "daily_average": round(avg, 2),
            "trend": "increasing" if trend > 0 else "decreasing" if trend < 0 else "stable",
            "confidence": "high" if len(values) > 60 else "medium" if len(values) > 30 else "low"
        }


class AnomalyDetector:
    """Детектор аномалий"""
    
    def __init__(self, cost_tracker: CostTracker):
        self.cost_tracker = cost_tracker
        self.anomalies: Dict[str, CostAnomaly] = {}
        
    def detect_anomalies(self, sensitivity: float = 2.0) -> List[CostAnomaly]:
        """Обнаружение аномалий"""
        now = datetime.now()
        
        # Получаем данные за последние 30 дней
        records = self.cost_tracker.get_costs(
            start_date=now - timedelta(days=30)
        )
        
        if not records:
            return []
            
        # Группируем по ресурсам
        by_resource = defaultdict(list)
        for record in records:
            by_resource[record.resource_id].append(record.amount)
            
        new_anomalies = []
        
        for resource_id, costs in by_resource.items():
            if len(costs) < 7:  # Недостаточно данных
                continue
                
            # Вычисляем статистики
            avg = sum(costs) / len(costs)
            variance = sum((c - avg) ** 2 for c in costs) / len(costs)
            std = variance ** 0.5
            
            # Проверяем последние значения
            recent = costs[-3:]
            
            for cost in recent:
                deviation = abs(cost - avg)
                
                if std > 0 and deviation > sensitivity * std:
                    anomaly = CostAnomaly(
                        anomaly_id=f"anomaly_{uuid.uuid4().hex[:8]}",
                        resource_id=resource_id,
                        expected_cost=round(avg, 2),
                        actual_cost=round(cost, 2),
                        deviation_percentage=round((cost - avg) / avg * 100, 1) if avg > 0 else 0,
                        severity=AlertSeverity.CRITICAL if deviation > 3 * std else AlertSeverity.WARNING,
                        anomaly_period="daily"
                    )
                    
                    self.anomalies[anomaly.anomaly_id] = anomaly
                    new_anomalies.append(anomaly)
                    break  # Один раз на ресурс
                    
        return new_anomalies


class ChargebackManager:
    """Менеджер распределения расходов"""
    
    def __init__(self, cost_tracker: CostTracker):
        self.cost_tracker = cost_tracker
        self.allocations: Dict[str, CostAllocation] = {}
        
    def create_allocation(self, name: str, rules: List[Dict[str, Any]],
                           **kwargs) -> CostAllocation:
        """Создание правила распределения"""
        allocation = CostAllocation(
            allocation_id=f"alloc_{uuid.uuid4().hex[:8]}",
            name=name,
            rules=rules,
            **kwargs
        )
        
        self.allocations[allocation.allocation_id] = allocation
        return allocation
        
    def generate_chargeback_report(self, start_date: datetime,
                                    end_date: datetime) -> Dict[str, Any]:
        """Генерация отчёта chargeback"""
        records = self.cost_tracker.get_costs(start_date=start_date, end_date=end_date)
        
        # По cost centers
        by_cost_center = self.cost_tracker.aggregate_by(records, "cost_center")
        
        # По проектам
        by_project = self.cost_tracker.aggregate_by(records, "project")
        
        # По командам
        by_team = self.cost_tracker.aggregate_by(records, "team")
        
        total = self.cost_tracker.get_total(records)
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_cost": round(total, 2),
            "by_cost_center": {k: round(v, 2) for k, v in by_cost_center.items()},
            "by_project": {k: round(v, 2) for k, v in by_project.items()},
            "by_team": {k: round(v, 2) for k, v in by_team.items()},
            "record_count": len(records)
        }


class FinOpsPlatform:
    """Платформа FinOps"""
    
    def __init__(self):
        self.cost_tracker = CostTracker()
        self.budget_manager = BudgetManager(self.cost_tracker)
        self.optimization = OptimizationEngine(self.cost_tracker)
        self.forecasting = ForecastingEngine(self.cost_tracker)
        self.anomaly_detector = AnomalyDetector(self.cost_tracker)
        self.chargeback = ChargebackManager(self.cost_tracker)
        
        self.savings_plans: Dict[str, SavingsPlan] = {}
        
    def import_costs(self, costs: List[Dict[str, Any]]) -> int:
        """Импорт затрат"""
        imported = 0
        
        for cost in costs:
            self.cost_tracker.record_cost(**cost)
            imported += 1
            
        return imported
        
    def create_savings_plan(self, name: str, plan_type: str,
                             commitment_amount: float,
                             commitment_term: int = 12,
                             **kwargs) -> SavingsPlan:
        """Создание Savings Plan"""
        plan = SavingsPlan(
            plan_id=f"sp_{uuid.uuid4().hex[:8]}",
            name=name,
            plan_type=plan_type,
            commitment_amount=commitment_amount,
            commitment_term=commitment_term,
            estimated_savings=commitment_amount * 0.3,  # ~30% экономия
            savings_percentage=30.0,
            **kwargs
        )
        
        self.savings_plans[plan.plan_id] = plan
        return plan
        
    def get_cost_summary(self, days: int = 30) -> Dict[str, Any]:
        """Сводка по затратам"""
        start = datetime.now() - timedelta(days=days)
        records = self.cost_tracker.get_costs(start_date=start)
        
        total = self.cost_tracker.get_total(records)
        by_category = self.cost_tracker.aggregate_by(records, "category")
        by_region = self.cost_tracker.aggregate_by(records, "region")
        by_resource_type = self.cost_tracker.aggregate_by(records, "resource_type")
        
        return {
            "period_days": days,
            "total_cost": round(total, 2),
            "daily_average": round(total / days, 2),
            "by_category": {k: round(v, 2) for k, v in by_category.items()},
            "by_region": {k: round(v, 2) for k, v in by_region.items()},
            "by_resource_type": {k: round(v, 2) for k, v in by_resource_type.items()},
            "record_count": len(records)
        }
        
    def get_dashboard(self) -> Dict[str, Any]:
        """Дашборд FinOps"""
        # Текущие затраты
        cost_summary = self.get_cost_summary(30)
        
        # Бюджеты
        budgets = []
        for budget in self.budget_manager.budgets.values():
            status = self.budget_manager.update_budget_spend(budget.budget_id)
            budgets.append({
                "name": budget.name,
                "amount": budget.amount,
                "spent": status["current_spend"],
                "percentage": status["spend_percentage"]
            })
            
        # Рекомендации
        savings = self.optimization.get_total_savings_potential()
        
        # Прогноз
        forecast = self.forecasting.forecast_costs(30)
        
        # Аномалии
        anomalies = list(self.anomaly_detector.anomalies.values())
        active_anomalies = [a for a in anomalies if a.status == "new"]
        
        return {
            "costs": {
                "current_month": cost_summary["total_cost"],
                "daily_average": cost_summary["daily_average"],
                "by_category": cost_summary["by_category"]
            },
            "budgets": budgets,
            "optimization": {
                "potential_savings": savings["total_potential_savings"],
                "recommendations": savings["recommendations_count"]
            },
            "forecast": {
                "next_30_days": forecast["total_forecasted"],
                "trend": forecast.get("trend", "stable")
            },
            "anomalies": {
                "active": len(active_anomalies),
                "total": len(anomalies)
            },
            "savings_plans": {
                "count": len(self.savings_plans),
                "total_commitment": sum(sp.commitment_amount for sp in self.savings_plans.values())
            }
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 64: FinOps & Cost Management")
    print("=" * 60)
    
    async def demo():
        platform = FinOpsPlatform()
        print("✓ FinOps Platform created")
        
        # Генерация тестовых затрат
        print("\n💰 Generating cost data...")
        
        cost_centers = ["engineering", "marketing", "operations"]
        projects = ["project-alpha", "project-beta", "project-gamma"]
        teams = ["team-a", "team-b", "team-c"]
        regions = ["us-east-1", "eu-west-1", "ap-south-1"]
        
        costs = []
        now = datetime.now()
        
        for day in range(90):
            date = now - timedelta(days=day)
            
            # Compute costs
            for i in range(5):
                costs.append({
                    "resource_id": f"vm_{i}",
                    "resource_name": f"vm-instance-{i}",
                    "resource_type": ResourceType.VIRTUAL_MACHINE,
                    "category": CostCategory.COMPUTE,
                    "amount": random.uniform(10, 50) * (1 + day * 0.002),  # Небольшой рост
                    "start_date": date,
                    "end_date": date,
                    "cost_center": random.choice(cost_centers),
                    "project": random.choice(projects),
                    "team": random.choice(teams),
                    "region": random.choice(regions)
                })
                
            # Storage costs
            for i in range(3):
                costs.append({
                    "resource_id": f"storage_{i}",
                    "resource_name": f"storage-bucket-{i}",
                    "resource_type": ResourceType.STORAGE,
                    "category": CostCategory.STORAGE,
                    "amount": random.uniform(5, 20),
                    "start_date": date,
                    "end_date": date,
                    "cost_center": random.choice(cost_centers),
                    "project": random.choice(projects),
                    "team": random.choice(teams),
                    "region": random.choice(regions)
                })
                
            # Database costs
            costs.append({
                "resource_id": "db_main",
                "resource_name": "main-database",
                "resource_type": ResourceType.DATABASE,
                "category": CostCategory.DATABASE,
                "amount": random.uniform(30, 60),
                "start_date": date,
                "end_date": date,
                "cost_center": "engineering",
                "project": "project-alpha",
                "team": "team-a",
                "region": "us-east-1"
            })
            
        imported = platform.import_costs(costs)
        print(f"  ✓ Imported {imported} cost records")
        
        # Cost Summary
        print("\n📊 Cost Summary (30 days):")
        summary = platform.get_cost_summary(30)
        print(f"  Total: ${summary['total_cost']:,.2f}")
        print(f"  Daily average: ${summary['daily_average']:,.2f}")
        print(f"  By category:")
        for cat, amount in summary["by_category"].items():
            print(f"    {cat}: ${amount:,.2f}")
            
        # Бюджеты
        print("\n💵 Creating budgets...")
        
        budget1 = platform.budget_manager.create_budget(
            name="Monthly Engineering",
            amount=5000,
            period=BudgetPeriod.MONTHLY,
            cost_centers=["engineering"],
            alert_thresholds=[50, 80, 100]
        )
        print(f"  ✓ Budget: {budget1.name} (${budget1.amount})")
        
        budget2 = platform.budget_manager.create_budget(
            name="Monthly Total",
            amount=15000,
            period=BudgetPeriod.MONTHLY,
            alert_thresholds=[75, 90, 100]
        )
        print(f"  ✓ Budget: {budget2.name} (${budget2.amount})")
        
        # Обновление бюджетов
        print("\n📈 Budget Status:")
        for budget_id in platform.budget_manager.budgets:
            status = platform.budget_manager.update_budget_spend(budget_id)
            budget = platform.budget_manager.budgets[budget_id]
            print(f"  {budget.name}:")
            print(f"    Spent: ${status['current_spend']:,.2f} / ${status['budget_amount']:,.2f}")
            print(f"    Usage: {status['spend_percentage']}%")
            print(f"    Forecast: ${status['forecasted_spend']:,.2f}")
            
        # Рекомендации по оптимизации
        print("\n🔧 Optimization Analysis...")
        
        resources = [
            {"id": "vm_0", "name": "vm-instance-0", "type": ResourceType.VIRTUAL_MACHINE,
             "avg_cpu": 15, "avg_memory": 25, "monthly_cost": 300, "running_hours_month": 720},
            {"id": "vm_1", "name": "vm-instance-1", "type": ResourceType.VIRTUAL_MACHINE,
             "avg_cpu": 5, "avg_memory": 10, "monthly_cost": 200, "last_used_days": 45},
            {"id": "vm_2", "name": "vm-instance-2", "type": ResourceType.VIRTUAL_MACHINE,
             "avg_cpu": 60, "avg_memory": 70, "monthly_cost": 400, "running_hours_month": 650},
            {"id": "vm_3", "name": "vm-instance-3", "type": ResourceType.VIRTUAL_MACHINE,
             "avg_cpu": 30, "avg_memory": 40, "monthly_cost": 250, "interruptible": True},
        ]
        
        recommendations = platform.optimization.analyze_resources(resources)
        print(f"  Found {len(recommendations)} recommendations:")
        
        for rec in recommendations:
            print(f"    [{rec.optimization_type.value}] {rec.title}")
            print(f"      Resource: {rec.resource_name}")
            print(f"      Potential savings: ${rec.estimated_savings}/month")
            
        savings_potential = platform.optimization.get_total_savings_potential()
        print(f"\n  Total savings potential: ${savings_potential['total_potential_savings']}/month")
        
        # Прогнозирование
        print("\n🔮 Cost Forecasting:")
        forecast = platform.forecasting.forecast_costs(30)
        print(f"  Next 30 days forecast: ${forecast['total_forecasted']:,.2f}")
        print(f"  Daily average: ${forecast['daily_average']:,.2f}")
        print(f"  Trend: {forecast['trend']}")
        print(f"  Confidence: {forecast['confidence']}")
        
        # Anomaly Detection
        print("\n🚨 Anomaly Detection...")
        
        # Добавляем аномальные затраты
        platform.cost_tracker.record_cost(
            resource_id="vm_0",
            resource_name="vm-instance-0",
            resource_type=ResourceType.VIRTUAL_MACHINE,
            category=CostCategory.COMPUTE,
            amount=500,  # Аномально высокая
            start_date=now,
            end_date=now,
            cost_center="engineering"
        )
        
        anomalies = platform.anomaly_detector.detect_anomalies(sensitivity=1.5)
        print(f"  Detected {len(anomalies)} anomalies")
        
        for anomaly in anomalies[:3]:
            print(f"    Resource: {anomaly.resource_id}")
            print(f"      Expected: ${anomaly.expected_cost}, Actual: ${anomaly.actual_cost}")
            print(f"      Deviation: {anomaly.deviation_percentage}%")
            print(f"      Severity: {anomaly.severity.value}")
            
        # Savings Plans
        print("\n💎 Creating Savings Plan...")
        
        savings_plan = platform.create_savings_plan(
            name="Compute Savings Plan",
            plan_type="compute",
            commitment_amount=3000,
            commitment_term=12
        )
        print(f"  ✓ {savings_plan.name}")
        print(f"    Commitment: ${savings_plan.commitment_amount}/month for {savings_plan.commitment_term} months")
        print(f"    Estimated savings: ${savings_plan.estimated_savings}/month ({savings_plan.savings_percentage}%)")
        
        # Chargeback Report
        print("\n📋 Chargeback Report:")
        
        chargeback_report = platform.chargeback.generate_chargeback_report(
            start_date=now - timedelta(days=30),
            end_date=now
        )
        print(f"  Total cost: ${chargeback_report['total_cost']:,.2f}")
        print(f"  By Cost Center:")
        for cc, amount in chargeback_report["by_cost_center"].items():
            if cc:
                print(f"    {cc}: ${amount:,.2f}")
        print(f"  By Project:")
        for proj, amount in chargeback_report["by_project"].items():
            if proj:
                print(f"    {proj}: ${amount:,.2f}")
                
        # Dashboard
        print("\n📊 FinOps Dashboard:")
        dashboard = platform.get_dashboard()
        print(f"  Current month spend: ${dashboard['costs']['current_month']:,.2f}")
        print(f"  Daily average: ${dashboard['costs']['daily_average']:,.2f}")
        print(f"  Active budgets: {len(dashboard['budgets'])}")
        print(f"  Optimization potential: ${dashboard['optimization']['potential_savings']:,.2f}")
        print(f"  Active recommendations: {dashboard['optimization']['recommendations']}")
        print(f"  Next 30 days forecast: ${dashboard['forecast']['next_30_days']:,.2f}")
        print(f"  Cost trend: {dashboard['forecast']['trend']}")
        print(f"  Active anomalies: {dashboard['anomalies']['active']}")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("FinOps & Cost Management Platform initialized!")
    print("=" * 60)
