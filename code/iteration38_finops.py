#!/usr/bin/env python3
"""
Server Init - Iteration 38: FinOps & Cloud Cost Optimization
Финансовые операции и оптимизация облачных затрат

Функционал:
- Cost Allocation - распределение затрат
- Budget Management - управление бюджетами
- Reserved Instance Optimization - оптимизация зарезервированных инстансов
- Spot Instance Management - управление спот-инстансами
- Resource Right-sizing - правильный размер ресурсов
- Waste Detection - обнаружение потерь
- Cost Forecasting - прогнозирование затрат
- Chargeback/Showback - возврат/показ затрат
"""

import json
import asyncio
import hashlib
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Tuple
from enum import Enum
from abc import ABC, abstractmethod
import random
from collections import defaultdict
import uuid
import math
import statistics


class CloudProvider(Enum):
    """Облачный провайдер"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    MULTI = "multi"


class ResourceType(Enum):
    """Тип ресурса"""
    COMPUTE = "compute"
    STORAGE = "storage"
    DATABASE = "database"
    NETWORK = "network"
    CONTAINER = "container"
    SERVERLESS = "serverless"
    ML = "ml"
    OTHER = "other"


class PricingModel(Enum):
    """Модель ценообразования"""
    ON_DEMAND = "on_demand"
    RESERVED = "reserved"
    SPOT = "spot"
    SAVINGS_PLAN = "savings_plan"
    COMMITTED_USE = "committed_use"


class BudgetStatus(Enum):
    """Статус бюджета"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    EXCEEDED = "exceeded"


class OptimizationType(Enum):
    """Тип оптимизации"""
    RIGHTSIZING = "rightsizing"
    RESERVED_INSTANCES = "reserved_instances"
    SPOT_USAGE = "spot_usage"
    IDLE_RESOURCES = "idle_resources"
    STORAGE_TIER = "storage_tier"
    NETWORK = "network"
    LICENSE = "license"


@dataclass
class CloudResource:
    """Облачный ресурс"""
    resource_id: str
    name: str
    provider: CloudProvider
    resource_type: ResourceType
    region: str
    
    # Конфигурация
    instance_type: str = ""
    size: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Стоимость
    pricing_model: PricingModel = PricingModel.ON_DEMAND
    hourly_cost: float = 0.0
    monthly_cost: float = 0.0
    
    # Использование
    avg_cpu_utilization: float = 0.0
    avg_memory_utilization: float = 0.0
    avg_network_utilization: float = 0.0
    
    # Метаданные
    created_at: datetime = field(default_factory=datetime.now)
    owner: str = ""
    team: str = ""
    environment: str = ""
    project: str = ""


@dataclass
class CostRecord:
    """Запись о затратах"""
    record_id: str
    resource_id: str
    provider: CloudProvider
    
    # Период
    date: datetime
    
    # Стоимость
    cost: float
    currency: str = "USD"
    
    # Детали
    service: str = ""
    usage_type: str = ""
    usage_quantity: float = 0.0
    unit: str = ""
    
    # Аллокация
    team: str = ""
    project: str = ""
    environment: str = ""
    cost_center: str = ""


@dataclass
class Budget:
    """Бюджет"""
    budget_id: str
    name: str
    
    # Лимиты
    amount: float
    currency: str = "USD"
    period: str = "monthly"  # monthly, quarterly, yearly
    
    # Фильтры
    teams: List[str] = field(default_factory=list)
    projects: List[str] = field(default_factory=list)
    cost_centers: List[str] = field(default_factory=list)
    providers: List[CloudProvider] = field(default_factory=list)
    
    # Пороги алертов (проценты)
    alert_thresholds: List[int] = field(default_factory=lambda: [50, 80, 100])
    
    # Текущее состояние
    current_spend: float = 0.0
    forecasted_spend: float = 0.0
    status: BudgetStatus = BudgetStatus.HEALTHY


@dataclass
class ReservedInstance:
    """Зарезервированный инстанс"""
    ri_id: str
    provider: CloudProvider
    instance_type: str
    region: str
    
    # Контракт
    term_months: int = 12
    payment_option: str = "no_upfront"  # no_upfront, partial_upfront, all_upfront
    quantity: int = 1
    
    # Стоимость
    hourly_rate: float = 0.0
    upfront_cost: float = 0.0
    total_cost: float = 0.0
    
    # Использование
    utilized_hours: float = 0.0
    total_hours: float = 0.0
    utilization_percent: float = 0.0
    
    # Даты
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    
    # Savings
    on_demand_equivalent: float = 0.0
    savings: float = 0.0


@dataclass
class SpotInstance:
    """Спот-инстанс"""
    spot_id: str
    provider: CloudProvider
    instance_type: str
    region: str
    availability_zone: str
    
    # Ставка
    bid_price: float = 0.0
    current_price: float = 0.0
    max_price: float = 0.0
    
    # Состояние
    status: str = "running"
    interruption_probability: float = 0.0
    
    # Fallback
    fallback_instance_type: str = ""
    fallback_to_on_demand: bool = True
    
    # Время
    launch_time: datetime = field(default_factory=datetime.now)
    uptime_hours: float = 0.0


@dataclass
class OptimizationRecommendation:
    """Рекомендация по оптимизации"""
    recommendation_id: str
    optimization_type: OptimizationType
    title: str
    description: str
    
    # Ресурсы
    affected_resources: List[str] = field(default_factory=list)
    
    # Savings
    estimated_monthly_savings: float = 0.0
    estimated_annual_savings: float = 0.0
    confidence: float = 0.0
    
    # Риски
    risk_level: str = "low"  # low, medium, high
    implementation_effort: str = "easy"  # easy, medium, hard
    
    # Действия
    actions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Статус
    status: str = "pending"  # pending, accepted, rejected, implemented
    created_at: datetime = field(default_factory=datetime.now)


class CostAllocation:
    """Распределение затрат"""
    
    def __init__(self):
        self.cost_records: List[CostRecord] = []
        self.allocation_rules: List[Dict[str, Any]] = []
        self.cost_centers: Dict[str, Dict[str, Any]] = {}
        
    def add_cost_record(self, record: CostRecord):
        """Добавление записи о затратах"""
        self.cost_records.append(record)
        
    def add_allocation_rule(self, rule: Dict[str, Any]):
        """Добавление правила распределения"""
        self.allocation_rules.append({
            "id": f"rule_{uuid.uuid4().hex[:8]}",
            "name": rule.get("name", "Unnamed"),
            "condition": rule.get("condition", {}),
            "allocation": rule.get("allocation", {}),
            "priority": rule.get("priority", 100)
        })
        # Сортировка по приоритету
        self.allocation_rules.sort(key=lambda r: r["priority"])
        
    def register_cost_center(self, cost_center_id: str, info: Dict[str, Any]):
        """Регистрация центра затрат"""
        self.cost_centers[cost_center_id] = {
            "id": cost_center_id,
            "name": info.get("name", cost_center_id),
            "owner": info.get("owner", ""),
            "budget": info.get("budget", 0),
            "teams": info.get("teams", [])
        }
        
    def allocate_costs(self, start_date: datetime, 
                       end_date: datetime) -> Dict[str, Any]:
        """Распределение затрат"""
        # Фильтрация записей по дате
        records = [
            r for r in self.cost_records
            if start_date <= r.date <= end_date
        ]
        
        # Распределение по центрам затрат
        by_cost_center = defaultdict(float)
        by_team = defaultdict(float)
        by_project = defaultdict(float)
        by_environment = defaultdict(float)
        
        for record in records:
            # Применение правил распределения
            allocated = self._apply_allocation_rules(record)
            
            by_cost_center[allocated.get("cost_center", "unallocated")] += record.cost
            by_team[allocated.get("team", "unallocated")] += record.cost
            by_project[allocated.get("project", "unallocated")] += record.cost
            by_environment[allocated.get("environment", "unallocated")] += record.cost
            
        total_cost = sum(r.cost for r in records)
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_cost": total_cost,
            "by_cost_center": dict(by_cost_center),
            "by_team": dict(by_team),
            "by_project": dict(by_project),
            "by_environment": dict(by_environment),
            "record_count": len(records)
        }
        
    def _apply_allocation_rules(self, record: CostRecord) -> Dict[str, str]:
        """Применение правил распределения"""
        result = {
            "cost_center": record.cost_center or "unallocated",
            "team": record.team or "unallocated",
            "project": record.project or "unallocated",
            "environment": record.environment or "unallocated"
        }
        
        for rule in self.allocation_rules:
            condition = rule["condition"]
            allocation = rule["allocation"]
            
            # Проверка условия
            matches = True
            
            if "service" in condition:
                if record.service != condition["service"]:
                    matches = False
                    
            if "tags" in condition:
                # Требует дополнительной информации о тегах
                pass
                
            if matches:
                result.update(allocation)
                break
                
        return result
        
    def generate_chargeback_report(self, period: str = "monthly") -> Dict[str, Any]:
        """Генерация отчёта chargeback"""
        now = datetime.now()
        
        if period == "monthly":
            start_date = now.replace(day=1, hour=0, minute=0, second=0)
            end_date = now
        elif period == "quarterly":
            quarter_start_month = ((now.month - 1) // 3) * 3 + 1
            start_date = now.replace(month=quarter_start_month, day=1, hour=0, minute=0, second=0)
            end_date = now
        else:
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0)
            end_date = now
            
        allocation = self.allocate_costs(start_date, end_date)
        
        # Формирование отчёта по центрам затрат
        report = {
            "period": period,
            "generated_at": now.isoformat(),
            "total_cost": allocation["total_cost"],
            "cost_centers": []
        }
        
        for cc_id, amount in allocation["by_cost_center"].items():
            cc_info = self.cost_centers.get(cc_id, {"name": cc_id})
            budget = cc_info.get("budget", 0)
            
            report["cost_centers"].append({
                "id": cc_id,
                "name": cc_info.get("name", cc_id),
                "owner": cc_info.get("owner", "Unknown"),
                "cost": amount,
                "budget": budget,
                "variance": budget - amount if budget > 0 else 0,
                "utilization": (amount / budget * 100) if budget > 0 else 0
            })
            
        return report


class BudgetManager:
    """Менеджер бюджетов"""
    
    def __init__(self, cost_allocation: CostAllocation):
        self.cost_allocation = cost_allocation
        self.budgets: Dict[str, Budget] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.forecasts: Dict[str, float] = {}
        
    def create_budget(self, budget: Budget) -> str:
        """Создание бюджета"""
        self.budgets[budget.budget_id] = budget
        return budget.budget_id
        
    def update_budget_spend(self, budget_id: str):
        """Обновление расходов бюджета"""
        budget = self.budgets.get(budget_id)
        if not budget:
            return
            
        # Расчёт периода
        now = datetime.now()
        if budget.period == "monthly":
            start_date = now.replace(day=1, hour=0, minute=0, second=0)
        elif budget.period == "quarterly":
            quarter_start_month = ((now.month - 1) // 3) * 3 + 1
            start_date = now.replace(month=quarter_start_month, day=1, hour=0, minute=0, second=0)
        else:
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0)
            
        # Фильтрация записей
        records = [
            r for r in self.cost_allocation.cost_records
            if r.date >= start_date
        ]
        
        # Применение фильтров бюджета
        if budget.teams:
            records = [r for r in records if r.team in budget.teams]
        if budget.projects:
            records = [r for r in records if r.project in budget.projects]
        if budget.cost_centers:
            records = [r for r in records if r.cost_center in budget.cost_centers]
            
        budget.current_spend = sum(r.cost for r in records)
        
        # Прогноз
        days_elapsed = (now - start_date).days + 1
        if budget.period == "monthly":
            days_in_period = 30
        elif budget.period == "quarterly":
            days_in_period = 90
        else:
            days_in_period = 365
            
        daily_avg = budget.current_spend / days_elapsed if days_elapsed > 0 else 0
        budget.forecasted_spend = daily_avg * days_in_period
        self.forecasts[budget_id] = budget.forecasted_spend
        
        # Обновление статуса
        usage_percent = (budget.current_spend / budget.amount * 100) if budget.amount > 0 else 0
        
        if usage_percent >= 100:
            budget.status = BudgetStatus.EXCEEDED
        elif usage_percent >= 80:
            budget.status = BudgetStatus.CRITICAL
        elif usage_percent >= 50:
            budget.status = BudgetStatus.WARNING
        else:
            budget.status = BudgetStatus.HEALTHY
            
        # Проверка алертов
        self._check_alerts(budget)
        
    def _check_alerts(self, budget: Budget):
        """Проверка и создание алертов"""
        usage_percent = (budget.current_spend / budget.amount * 100) if budget.amount > 0 else 0
        
        for threshold in budget.alert_thresholds:
            if usage_percent >= threshold:
                # Проверка, был ли уже такой алерт
                existing = [
                    a for a in self.alerts
                    if a["budget_id"] == budget.budget_id 
                    and a["threshold"] == threshold
                    and a["period_start"] == datetime.now().replace(day=1).date().isoformat()
                ]
                
                if not existing:
                    self.alerts.append({
                        "id": f"alert_{uuid.uuid4().hex[:8]}",
                        "budget_id": budget.budget_id,
                        "budget_name": budget.name,
                        "threshold": threshold,
                        "current_usage": usage_percent,
                        "current_spend": budget.current_spend,
                        "budget_amount": budget.amount,
                        "period_start": datetime.now().replace(day=1).date().isoformat(),
                        "created_at": datetime.now().isoformat()
                    })
                    
    def get_budget_summary(self) -> Dict[str, Any]:
        """Получение сводки по бюджетам"""
        total_budget = sum(b.amount for b in self.budgets.values())
        total_spend = sum(b.current_spend for b in self.budgets.values())
        total_forecast = sum(b.forecasted_spend for b in self.budgets.values())
        
        by_status = defaultdict(int)
        for budget in self.budgets.values():
            by_status[budget.status.value] += 1
            
        return {
            "total_budgets": len(self.budgets),
            "total_budget_amount": total_budget,
            "total_current_spend": total_spend,
            "total_forecasted_spend": total_forecast,
            "overall_utilization": (total_spend / total_budget * 100) if total_budget > 0 else 0,
            "by_status": dict(by_status),
            "active_alerts": len([a for a in self.alerts 
                                 if datetime.fromisoformat(a["created_at"]).date() == datetime.now().date()])
        }


class ReservedInstanceOptimizer:
    """Оптимизатор зарезервированных инстансов"""
    
    def __init__(self):
        self.reserved_instances: Dict[str, ReservedInstance] = {}
        self.on_demand_usage: Dict[str, Dict[str, float]] = defaultdict(dict)  # instance_type -> region -> hours
        
    def add_reserved_instance(self, ri: ReservedInstance):
        """Добавление RI"""
        self.reserved_instances[ri.ri_id] = ri
        
        # Расчёт дат
        if not ri.end_date:
            ri.end_date = ri.start_date + timedelta(days=ri.term_months * 30)
            
    def record_on_demand_usage(self, instance_type: str, region: str, hours: float):
        """Запись использования on-demand"""
        key = f"{instance_type}:{region}"
        if key not in self.on_demand_usage:
            self.on_demand_usage[key] = {"total_hours": 0, "records": []}
            
        self.on_demand_usage[key]["total_hours"] += hours
        self.on_demand_usage[key]["records"].append({
            "hours": hours,
            "date": datetime.now().isoformat()
        })
        
    def analyze_ri_utilization(self) -> Dict[str, Any]:
        """Анализ использования RI"""
        analysis = {
            "total_ris": len(self.reserved_instances),
            "underutilized": [],
            "well_utilized": [],
            "expiring_soon": [],
            "total_savings": 0,
            "potential_additional_savings": 0
        }
        
        for ri_id, ri in self.reserved_instances.items():
            # Расчёт использования
            if ri.total_hours > 0:
                ri.utilization_percent = (ri.utilized_hours / ri.total_hours) * 100
                
            # Классификация
            if ri.utilization_percent < 70:
                analysis["underutilized"].append({
                    "ri_id": ri_id,
                    "instance_type": ri.instance_type,
                    "region": ri.region,
                    "utilization": ri.utilization_percent,
                    "waste": ri.total_cost * (1 - ri.utilization_percent / 100)
                })
            else:
                analysis["well_utilized"].append({
                    "ri_id": ri_id,
                    "instance_type": ri.instance_type,
                    "utilization": ri.utilization_percent
                })
                
            # Проверка истечения
            if ri.end_date:
                days_remaining = (ri.end_date - datetime.now()).days
                if 0 < days_remaining <= 30:
                    analysis["expiring_soon"].append({
                        "ri_id": ri_id,
                        "instance_type": ri.instance_type,
                        "days_remaining": days_remaining,
                        "end_date": ri.end_date.isoformat()
                    })
                    
            analysis["total_savings"] += ri.savings
            
        return analysis
        
    def recommend_ri_purchases(self) -> List[Dict[str, Any]]:
        """Рекомендации по покупке RI"""
        recommendations = []
        
        # Анализ on-demand использования
        for key, usage in self.on_demand_usage.items():
            instance_type, region = key.split(":")
            monthly_hours = usage["total_hours"]
            
            # Если используем более 70% времени - рекомендуем RI
            hours_in_month = 730  # ~24 * 30.4
            utilization_ratio = monthly_hours / hours_in_month
            
            if utilization_ratio > 0.7:
                # Расчёт savings (упрощённо)
                on_demand_rate = self._get_on_demand_rate(instance_type, region)
                ri_rate = on_demand_rate * 0.6  # ~40% скидка для 1-year RI
                
                monthly_on_demand = monthly_hours * on_demand_rate
                monthly_ri = hours_in_month * ri_rate
                monthly_savings = monthly_on_demand - monthly_ri
                
                if monthly_savings > 50:  # Минимальный порог
                    recommendations.append({
                        "instance_type": instance_type,
                        "region": region,
                        "current_usage_hours": monthly_hours,
                        "utilization_ratio": utilization_ratio,
                        "recommended_quantity": max(1, int(utilization_ratio)),
                        "term": "1 year",
                        "payment_option": "no_upfront",
                        "estimated_monthly_savings": monthly_savings,
                        "estimated_annual_savings": monthly_savings * 12,
                        "confidence": min(0.95, utilization_ratio)
                    })
                    
        return sorted(recommendations, 
                     key=lambda r: r["estimated_annual_savings"], 
                     reverse=True)
        
    def _get_on_demand_rate(self, instance_type: str, region: str) -> float:
        """Получение on-demand rate (упрощённо)"""
        # В реальности - запрос к API
        base_rates = {
            "t3.micro": 0.0104,
            "t3.small": 0.0208,
            "t3.medium": 0.0416,
            "m5.large": 0.096,
            "m5.xlarge": 0.192,
            "c5.large": 0.085,
            "r5.large": 0.126
        }
        return base_rates.get(instance_type, 0.1)


class SpotInstanceManager:
    """Менеджер спот-инстансов"""
    
    def __init__(self):
        self.spot_instances: Dict[str, SpotInstance] = {}
        self.price_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.interruption_history: List[Dict[str, Any]] = []
        
    def register_spot_instance(self, spot: SpotInstance):
        """Регистрация спот-инстанса"""
        self.spot_instances[spot.spot_id] = spot
        
    def record_price(self, instance_type: str, region: str, 
                     az: str, price: float):
        """Запись цены"""
        key = f"{instance_type}:{region}:{az}"
        self.price_history[key].append({
            "price": price,
            "timestamp": datetime.now().isoformat()
        })
        
        # Ограничение истории
        if len(self.price_history[key]) > 1000:
            self.price_history[key] = self.price_history[key][-500:]
            
    def record_interruption(self, spot_id: str, reason: str):
        """Запись прерывания"""
        spot = self.spot_instances.get(spot_id)
        if spot:
            spot.status = "interrupted"
            
        self.interruption_history.append({
            "spot_id": spot_id,
            "instance_type": spot.instance_type if spot else "unknown",
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        
    def analyze_spot_savings(self) -> Dict[str, Any]:
        """Анализ экономии от spot"""
        total_spot_cost = 0
        total_on_demand_equivalent = 0
        
        for spot in self.spot_instances.values():
            spot_cost = spot.current_price * spot.uptime_hours
            total_spot_cost += spot_cost
            
            # On-demand эквивалент
            on_demand_rate = self._get_on_demand_rate(spot.instance_type)
            on_demand_cost = on_demand_rate * spot.uptime_hours
            total_on_demand_equivalent += on_demand_cost
            
        savings = total_on_demand_equivalent - total_spot_cost
        savings_percent = (savings / total_on_demand_equivalent * 100) if total_on_demand_equivalent > 0 else 0
        
        return {
            "total_spot_instances": len(self.spot_instances),
            "running": len([s for s in self.spot_instances.values() if s.status == "running"]),
            "interrupted": len([s for s in self.spot_instances.values() if s.status == "interrupted"]),
            "total_spot_cost": total_spot_cost,
            "on_demand_equivalent": total_on_demand_equivalent,
            "total_savings": savings,
            "savings_percent": savings_percent,
            "interruption_count_24h": len([
                i for i in self.interruption_history
                if datetime.fromisoformat(i["timestamp"]) > datetime.now() - timedelta(days=1)
            ])
        }
        
    def get_optimal_bid_price(self, instance_type: str, region: str, az: str) -> Dict[str, Any]:
        """Получение оптимальной bid price"""
        key = f"{instance_type}:{region}:{az}"
        history = self.price_history.get(key, [])
        
        if not history:
            on_demand = self._get_on_demand_rate(instance_type)
            return {
                "recommended_bid": on_demand * 0.5,
                "confidence": 0.5,
                "note": "No price history, using conservative estimate"
            }
            
        prices = [h["price"] for h in history[-100:]]
        
        avg_price = statistics.mean(prices)
        max_price = max(prices)
        p90_price = sorted(prices)[int(len(prices) * 0.9)]
        
        # Рекомендация: чуть выше P90 для стабильности
        recommended = p90_price * 1.1
        
        on_demand = self._get_on_demand_rate(instance_type)
        
        return {
            "recommended_bid": min(recommended, on_demand * 0.7),
            "average_price": avg_price,
            "max_price": max_price,
            "p90_price": p90_price,
            "on_demand_price": on_demand,
            "potential_savings_percent": (1 - recommended / on_demand) * 100,
            "confidence": min(0.9, len(prices) / 100)
        }
        
    def _get_on_demand_rate(self, instance_type: str) -> float:
        """Получение on-demand rate"""
        base_rates = {
            "t3.micro": 0.0104,
            "t3.small": 0.0208,
            "t3.medium": 0.0416,
            "m5.large": 0.096,
            "m5.xlarge": 0.192,
            "c5.large": 0.085
        }
        return base_rates.get(instance_type, 0.1)


class ResourceRightsizer:
    """Оптимизатор размера ресурсов"""
    
    def __init__(self):
        self.resources: Dict[str, CloudResource] = {}
        self.utilization_history: Dict[str, List[Dict[str, float]]] = defaultdict(list)
        self.instance_catalog: Dict[str, Dict[str, Any]] = {}
        
    def register_resource(self, resource: CloudResource):
        """Регистрация ресурса"""
        self.resources[resource.resource_id] = resource
        
    def record_utilization(self, resource_id: str, cpu: float, memory: float):
        """Запись использования"""
        self.utilization_history[resource_id].append({
            "timestamp": datetime.now().isoformat(),
            "cpu": cpu,
            "memory": memory
        })
        
        # Обновление средних
        resource = self.resources.get(resource_id)
        if resource:
            recent = self.utilization_history[resource_id][-100:]
            resource.avg_cpu_utilization = statistics.mean([u["cpu"] for u in recent])
            resource.avg_memory_utilization = statistics.mean([u["memory"] for u in recent])
            
    def add_instance_type(self, instance_type: str, specs: Dict[str, Any]):
        """Добавление типа инстанса в каталог"""
        self.instance_catalog[instance_type] = specs
        
    def analyze_rightsizing(self) -> List[OptimizationRecommendation]:
        """Анализ rightsizing"""
        recommendations = []
        
        for resource_id, resource in self.resources.items():
            history = self.utilization_history.get(resource_id, [])
            
            if len(history) < 24:  # Минимум 24 точки данных
                continue
                
            # Анализ CPU
            cpu_values = [h["cpu"] for h in history]
            max_cpu = max(cpu_values)
            avg_cpu = statistics.mean(cpu_values)
            p95_cpu = sorted(cpu_values)[int(len(cpu_values) * 0.95)]
            
            # Анализ Memory
            mem_values = [h["memory"] for h in history]
            max_mem = max(mem_values)
            avg_mem = statistics.mean(mem_values)
            p95_mem = sorted(mem_values)[int(len(mem_values) * 0.95)]
            
            # Определение рекомендации
            if p95_cpu < 30 and p95_mem < 30:
                # Сильно oversized
                recommendation = self._create_downsize_recommendation(
                    resource, "aggressive", avg_cpu, avg_mem, p95_cpu, p95_mem
                )
                if recommendation:
                    recommendations.append(recommendation)
                    
            elif p95_cpu < 50 and p95_mem < 50:
                # Умеренно oversized
                recommendation = self._create_downsize_recommendation(
                    resource, "moderate", avg_cpu, avg_mem, p95_cpu, p95_mem
                )
                if recommendation:
                    recommendations.append(recommendation)
                    
            elif p95_cpu > 80 or p95_mem > 80:
                # Undersized
                recommendation = self._create_upsize_recommendation(
                    resource, avg_cpu, avg_mem, p95_cpu, p95_mem
                )
                if recommendation:
                    recommendations.append(recommendation)
                    
        return sorted(recommendations, 
                     key=lambda r: r.estimated_annual_savings,
                     reverse=True)
        
    def _create_downsize_recommendation(self, resource: CloudResource,
                                         aggressiveness: str,
                                         avg_cpu: float, avg_mem: float,
                                         p95_cpu: float, p95_mem: float
                                         ) -> Optional[OptimizationRecommendation]:
        """Создание рекомендации на уменьшение"""
        current_type = resource.instance_type
        
        # Поиск меньшего инстанса
        smaller_type = self._find_smaller_instance(current_type, p95_cpu, p95_mem)
        
        if not smaller_type:
            return None
            
        # Расчёт savings
        current_cost = resource.monthly_cost
        new_cost = self._estimate_cost(smaller_type)
        monthly_savings = current_cost - new_cost
        
        if monthly_savings <= 0:
            return None
            
        return OptimizationRecommendation(
            recommendation_id=f"rightsize_{uuid.uuid4().hex[:8]}",
            optimization_type=OptimizationType.RIGHTSIZING,
            title=f"Downsize {resource.name} from {current_type} to {smaller_type}",
            description=f"Resource is underutilized (avg CPU: {avg_cpu:.1f}%, avg Memory: {avg_mem:.1f}%)",
            affected_resources=[resource.resource_id],
            estimated_monthly_savings=monthly_savings,
            estimated_annual_savings=monthly_savings * 12,
            confidence=0.85 if aggressiveness == "moderate" else 0.75,
            risk_level="low" if aggressiveness == "moderate" else "medium",
            implementation_effort="easy",
            actions=[
                {"action": "resize", "from": current_type, "to": smaller_type}
            ]
        )
        
    def _create_upsize_recommendation(self, resource: CloudResource,
                                       avg_cpu: float, avg_mem: float,
                                       p95_cpu: float, p95_mem: float
                                       ) -> Optional[OptimizationRecommendation]:
        """Создание рекомендации на увеличение"""
        current_type = resource.instance_type
        larger_type = self._find_larger_instance(current_type)
        
        if not larger_type:
            return None
            
        return OptimizationRecommendation(
            recommendation_id=f"rightsize_{uuid.uuid4().hex[:8]}",
            optimization_type=OptimizationType.RIGHTSIZING,
            title=f"Upsize {resource.name} from {current_type} to {larger_type}",
            description=f"Resource is constrained (P95 CPU: {p95_cpu:.1f}%, P95 Memory: {p95_mem:.1f}%)",
            affected_resources=[resource.resource_id],
            estimated_monthly_savings=-50,  # Увеличение затрат
            estimated_annual_savings=-600,
            confidence=0.9,
            risk_level="low",
            implementation_effort="easy",
            actions=[
                {"action": "resize", "from": current_type, "to": larger_type}
            ]
        )
        
    def _find_smaller_instance(self, current_type: str, 
                                target_cpu: float, target_mem: float) -> Optional[str]:
        """Поиск меньшего инстанса"""
        # Упрощённая логика
        downsizing_map = {
            "m5.xlarge": "m5.large",
            "m5.large": "t3.large",
            "t3.large": "t3.medium",
            "t3.medium": "t3.small",
            "c5.xlarge": "c5.large",
            "c5.large": "t3.large"
        }
        return downsizing_map.get(current_type)
        
    def _find_larger_instance(self, current_type: str) -> Optional[str]:
        """Поиск большего инстанса"""
        upsizing_map = {
            "t3.small": "t3.medium",
            "t3.medium": "t3.large",
            "t3.large": "m5.large",
            "m5.large": "m5.xlarge",
            "c5.large": "c5.xlarge"
        }
        return upsizing_map.get(current_type)
        
    def _estimate_cost(self, instance_type: str) -> float:
        """Оценка стоимости"""
        monthly_costs = {
            "t3.micro": 7.5,
            "t3.small": 15,
            "t3.medium": 30,
            "t3.large": 60,
            "m5.large": 70,
            "m5.xlarge": 140,
            "c5.large": 62,
            "c5.xlarge": 124
        }
        return monthly_costs.get(instance_type, 100)


class WasteDetector:
    """Детектор потерь"""
    
    def __init__(self, resources: Dict[str, CloudResource]):
        self.resources = resources
        self.waste_findings: List[Dict[str, Any]] = []
        
    def detect_idle_resources(self) -> List[Dict[str, Any]]:
        """Обнаружение простаивающих ресурсов"""
        idle = []
        
        for resource_id, resource in self.resources.items():
            if resource.avg_cpu_utilization < 5 and resource.avg_memory_utilization < 10:
                idle.append({
                    "resource_id": resource_id,
                    "name": resource.name,
                    "type": resource.resource_type.value,
                    "instance_type": resource.instance_type,
                    "avg_cpu": resource.avg_cpu_utilization,
                    "avg_memory": resource.avg_memory_utilization,
                    "monthly_cost": resource.monthly_cost,
                    "recommendation": "Consider terminating or hibernating"
                })
                
        return idle
        
    def detect_unattached_volumes(self, volumes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Обнаружение неприсоединённых томов"""
        unattached = []
        
        for volume in volumes:
            if not volume.get("attached_to"):
                unattached.append({
                    "volume_id": volume["id"],
                    "name": volume.get("name", "unnamed"),
                    "size_gb": volume.get("size_gb", 0),
                    "created_at": volume.get("created_at"),
                    "monthly_cost": volume.get("size_gb", 0) * 0.10,  # ~$0.10/GB
                    "recommendation": "Delete or snapshot and remove"
                })
                
        return unattached
        
    def detect_unused_snapshots(self, snapshots: List[Dict[str, Any]],
                                 retention_days: int = 30) -> List[Dict[str, Any]]:
        """Обнаружение старых снапшотов"""
        unused = []
        cutoff = datetime.now() - timedelta(days=retention_days)
        
        for snapshot in snapshots:
            created_at = snapshot.get("created_at")
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at)
                
            if created_at and created_at < cutoff:
                unused.append({
                    "snapshot_id": snapshot["id"],
                    "name": snapshot.get("name", "unnamed"),
                    "size_gb": snapshot.get("size_gb", 0),
                    "created_at": created_at.isoformat(),
                    "age_days": (datetime.now() - created_at).days,
                    "monthly_cost": snapshot.get("size_gb", 0) * 0.05,
                    "recommendation": "Review and delete if not needed"
                })
                
        return unused
        
    def detect_unused_ips(self, elastic_ips: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Обнаружение неиспользуемых Elastic IP"""
        unused = []
        
        for ip in elastic_ips:
            if not ip.get("associated_with"):
                unused.append({
                    "ip_id": ip["id"],
                    "ip_address": ip.get("address", "unknown"),
                    "monthly_cost": 3.60,  # ~$0.005/hour when unassociated
                    "recommendation": "Release if not needed"
                })
                
        return unused
        
    def generate_waste_report(self) -> Dict[str, Any]:
        """Генерация отчёта о потерях"""
        idle_resources = self.detect_idle_resources()
        
        # Упрощённый пример - в реальности данные приходят из облака
        unattached_volumes = self.detect_unattached_volumes([])
        unused_snapshots = self.detect_unused_snapshots([])
        unused_ips = self.detect_unused_ips([])
        
        total_waste = (
            sum(r["monthly_cost"] for r in idle_resources) +
            sum(v["monthly_cost"] for v in unattached_volumes) +
            sum(s["monthly_cost"] for s in unused_snapshots) +
            sum(ip["monthly_cost"] for ip in unused_ips)
        )
        
        return {
            "generated_at": datetime.now().isoformat(),
            "total_monthly_waste": total_waste,
            "total_annual_waste": total_waste * 12,
            "categories": {
                "idle_resources": {
                    "count": len(idle_resources),
                    "monthly_cost": sum(r["monthly_cost"] for r in idle_resources),
                    "items": idle_resources
                },
                "unattached_volumes": {
                    "count": len(unattached_volumes),
                    "monthly_cost": sum(v["monthly_cost"] for v in unattached_volumes),
                    "items": unattached_volumes
                },
                "unused_snapshots": {
                    "count": len(unused_snapshots),
                    "monthly_cost": sum(s["monthly_cost"] for s in unused_snapshots),
                    "items": unused_snapshots
                },
                "unused_ips": {
                    "count": len(unused_ips),
                    "monthly_cost": sum(ip["monthly_cost"] for ip in unused_ips),
                    "items": unused_ips
                }
            }
        }


class FinOpsEngine:
    """FinOps движок"""
    
    def __init__(self):
        self.cost_allocation = CostAllocation()
        self.budget_manager = BudgetManager(self.cost_allocation)
        self.ri_optimizer = ReservedInstanceOptimizer()
        self.spot_manager = SpotInstanceManager()
        self.rightsizer = ResourceRightsizer()
        self.waste_detector: Optional[WasteDetector] = None
        
        self.recommendations: List[OptimizationRecommendation] = []
        
    def initialize(self):
        """Инициализация"""
        # Добавление правил распределения по умолчанию
        self.cost_allocation.add_allocation_rule({
            "name": "Production to Ops",
            "condition": {"tags": {"environment": "production"}},
            "allocation": {"cost_center": "operations"},
            "priority": 10
        })
        
        self.cost_allocation.add_allocation_rule({
            "name": "Development to Engineering",
            "condition": {"tags": {"environment": "development"}},
            "allocation": {"cost_center": "engineering"},
            "priority": 20
        })
        
        # Инициализация waste detector
        self.waste_detector = WasteDetector(self.rightsizer.resources)
        
    def ingest_cost_data(self, records: List[Dict[str, Any]]):
        """Приём данных о затратах"""
        for record_data in records:
            record = CostRecord(
                record_id=record_data.get("id", str(uuid.uuid4())),
                resource_id=record_data.get("resource_id", ""),
                provider=CloudProvider(record_data.get("provider", "aws")),
                date=datetime.fromisoformat(record_data["date"]) if isinstance(record_data["date"], str) else record_data["date"],
                cost=record_data.get("cost", 0),
                service=record_data.get("service", ""),
                team=record_data.get("team", ""),
                project=record_data.get("project", ""),
                cost_center=record_data.get("cost_center", "")
            )
            self.cost_allocation.add_cost_record(record)
            
    def generate_all_recommendations(self) -> List[OptimizationRecommendation]:
        """Генерация всех рекомендаций"""
        self.recommendations = []
        
        # RI рекомендации
        ri_recommendations = self.ri_optimizer.recommend_ri_purchases()
        for ri_rec in ri_recommendations:
            self.recommendations.append(OptimizationRecommendation(
                recommendation_id=f"ri_{uuid.uuid4().hex[:8]}",
                optimization_type=OptimizationType.RESERVED_INSTANCES,
                title=f"Purchase RI for {ri_rec['instance_type']}",
                description=f"High utilization ({ri_rec['utilization_ratio']:.0%}) suggests RI purchase",
                estimated_monthly_savings=ri_rec["estimated_monthly_savings"],
                estimated_annual_savings=ri_rec["estimated_annual_savings"],
                confidence=ri_rec["confidence"],
                risk_level="low",
                implementation_effort="easy",
                actions=[
                    {
                        "action": "purchase_ri",
                        "instance_type": ri_rec["instance_type"],
                        "region": ri_rec["region"],
                        "term": ri_rec["term"],
                        "quantity": ri_rec["recommended_quantity"]
                    }
                ]
            ))
            
        # Rightsizing рекомендации
        rightsizing_recs = self.rightsizer.analyze_rightsizing()
        self.recommendations.extend(rightsizing_recs)
        
        # Сортировка по экономии
        self.recommendations.sort(key=lambda r: r.estimated_annual_savings, reverse=True)
        
        return self.recommendations
        
    def get_cost_dashboard(self) -> Dict[str, Any]:
        """Получение финансового дашборда"""
        # Текущий месяц
        now = datetime.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0)
        
        allocation = self.cost_allocation.allocate_costs(start_of_month, now)
        budget_summary = self.budget_manager.get_budget_summary()
        ri_analysis = self.ri_optimizer.analyze_ri_utilization()
        spot_analysis = self.spot_manager.analyze_spot_savings()
        
        waste_report = self.waste_detector.generate_waste_report() if self.waste_detector else {}
        
        # Суммарные recommendations
        total_savings_potential = sum(r.estimated_annual_savings for r in self.recommendations if r.estimated_annual_savings > 0)
        
        return {
            "period": {
                "month": now.strftime("%B %Y"),
                "start": start_of_month.isoformat(),
                "end": now.isoformat()
            },
            "cost_summary": {
                "total_cost_mtd": allocation["total_cost"],
                "by_team": allocation["by_team"],
                "by_project": allocation["by_project"],
                "by_environment": allocation["by_environment"]
            },
            "budgets": budget_summary,
            "optimization": {
                "ri_utilization": ri_analysis.get("total_savings", 0),
                "spot_savings": spot_analysis.get("total_savings", 0),
                "waste_identified": waste_report.get("total_monthly_waste", 0),
                "recommendations_count": len(self.recommendations),
                "potential_annual_savings": total_savings_potential
            },
            "reserved_instances": {
                "total": ri_analysis.get("total_ris", 0),
                "underutilized": len(ri_analysis.get("underutilized", [])),
                "expiring_soon": len(ri_analysis.get("expiring_soon", []))
            },
            "spot_instances": {
                "running": spot_analysis.get("running", 0),
                "savings_percent": spot_analysis.get("savings_percent", 0),
                "interruptions_24h": spot_analysis.get("interruption_count_24h", 0)
            }
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 38: FinOps & Cloud Cost Optimization")
    print("=" * 60)
    
    # Создание FinOps движка
    finops = FinOpsEngine()
    finops.initialize()
    
    print("✓ FinOps Engine initialized")
    
    # Регистрация центров затрат
    finops.cost_allocation.register_cost_center("engineering", {
        "name": "Engineering",
        "owner": "CTO",
        "budget": 50000,
        "teams": ["backend", "frontend", "platform"]
    })
    
    finops.cost_allocation.register_cost_center("operations", {
        "name": "Operations",
        "owner": "VP Operations",
        "budget": 30000,
        "teams": ["devops", "sre"]
    })
    
    print("✓ Cost centers registered")
    
    # Создание бюджетов
    budget = Budget(
        budget_id="budget_eng_2024",
        name="Engineering Monthly Budget",
        amount=50000,
        period="monthly",
        teams=["backend", "frontend", "platform"],
        alert_thresholds=[50, 80, 100]
    )
    finops.budget_manager.create_budget(budget)
    print("✓ Budget created")
    
    # Симуляция данных о затратах
    now = datetime.now()
    for i in range(30):
        date = now - timedelta(days=i)
        
        finops.ingest_cost_data([
            {
                "date": date,
                "cost": random.uniform(500, 2000),
                "provider": "aws",
                "service": "EC2",
                "team": "backend",
                "project": "api-service",
                "cost_center": "engineering"
            },
            {
                "date": date,
                "cost": random.uniform(200, 800),
                "provider": "aws",
                "service": "RDS",
                "team": "backend",
                "project": "database",
                "cost_center": "engineering"
            }
        ])
        
    print(f"✓ Ingested cost data for 30 days")
    
    # Обновление бюджета
    finops.budget_manager.update_budget_spend("budget_eng_2024")
    
    # Регистрация ресурсов для rightsizing
    resource = CloudResource(
        resource_id="i-1234567890",
        name="api-server-1",
        provider=CloudProvider.AWS,
        resource_type=ResourceType.COMPUTE,
        region="us-east-1",
        instance_type="m5.xlarge",
        monthly_cost=140,
        avg_cpu_utilization=25,
        avg_memory_utilization=30,
        team="backend"
    )
    finops.rightsizer.register_resource(resource)
    
    # Запись истории использования
    for _ in range(100):
        finops.rightsizer.record_utilization(
            "i-1234567890",
            cpu=random.uniform(15, 35),
            memory=random.uniform(20, 40)
        )
        
    # Запись on-demand использования для RI рекомендаций
    for _ in range(30):
        finops.ri_optimizer.record_on_demand_usage("m5.large", "us-east-1", random.uniform(600, 730))
        
    print("✓ Resource utilization data recorded")
    
    # Генерация рекомендаций
    recommendations = finops.generate_all_recommendations()
    print(f"\n💡 Generated {len(recommendations)} optimization recommendations")
    
    for rec in recommendations[:3]:
        print(f"   - {rec.title}")
        print(f"     Potential Annual Savings: ${rec.estimated_annual_savings:,.0f}")
        
    # Получение дашборда
    dashboard = finops.get_cost_dashboard()
    
    print(f"\n📊 FinOps Dashboard:")
    print(f"   Period: {dashboard['period']['month']}")
    print(f"   Total Cost MTD: ${dashboard['cost_summary']['total_cost_mtd']:,.2f}")
    print(f"\n   Budget Status:")
    print(f"      Total Budgets: {dashboard['budgets']['total_budgets']}")
    print(f"      Overall Utilization: {dashboard['budgets']['overall_utilization']:.1f}%")
    
    print(f"\n   Optimization Opportunities:")
    print(f"      Potential Annual Savings: ${dashboard['optimization']['potential_annual_savings']:,.0f}")
    print(f"      Recommendations: {dashboard['optimization']['recommendations_count']}")
    
    # Chargeback отчёт
    chargeback = finops.cost_allocation.generate_chargeback_report("monthly")
    print(f"\n📋 Chargeback Report:")
    for cc in chargeback["cost_centers"]:
        print(f"   {cc['name']}: ${cc['cost']:,.2f} / ${cc['budget']:,.0f} ({cc['utilization']:.1f}%)")
        
    print("\n" + "=" * 60)
    print("FinOps Engine initialized successfully!")
    print("=" * 60)
