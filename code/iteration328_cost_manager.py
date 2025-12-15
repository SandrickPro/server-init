#!/usr/bin/env python3
"""
Server Init - Iteration 328: Cost Management Platform
Платформа управления затратами облачной инфраструктуры

Функционал:
- Cost Tracking - отслеживание затрат
- Budget Management - управление бюджетами
- Cost Allocation - распределение затрат
- Reserved Instances - резервные инстансы
- Savings Plans - планы экономии
- Cost Optimization - оптимизация затрат
- Billing Alerts - оповещения о расходах
- FinOps Reporting - финансовая отчетность
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class CloudProvider(Enum):
    """Облачный провайдер"""
    AWS = "AWS"
    AZURE = "Azure"
    GCP = "GCP"
    ALIBABA = "Alibaba"
    ORACLE = "Oracle"
    PRIVATE = "Private"


class ServiceCategory(Enum):
    """Категория сервиса"""
    COMPUTE = "compute"
    STORAGE = "storage"
    DATABASE = "database"
    NETWORKING = "networking"
    ANALYTICS = "analytics"
    AI_ML = "ai_ml"
    SECURITY = "security"
    MANAGEMENT = "management"
    OTHER = "other"


class BudgetPeriod(Enum):
    """Период бюджета"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class AlertSeverity(Enum):
    """Серьезность оповещения"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class RecommendationType(Enum):
    """Тип рекомендации"""
    RIGHTSIZE = "rightsize"
    RESERVED = "reserved"
    SAVINGS_PLAN = "savings_plan"
    SPOT = "spot"
    DELETE = "delete"
    SCHEDULE = "schedule"
    STORAGE_TIER = "storage_tier"
    COMMITMENT = "commitment"


class CostTrend(Enum):
    """Тренд затрат"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    SPIKE = "spike"


@dataclass
class CostItem:
    """Элемент затрат"""
    item_id: str
    
    # Provider
    provider: CloudProvider = CloudProvider.AWS
    
    # Service
    service_name: str = ""
    service_category: ServiceCategory = ServiceCategory.COMPUTE
    
    # Resource
    resource_id: str = ""
    resource_name: str = ""
    resource_type: str = ""
    
    # Region
    region: str = ""
    
    # Cost
    cost_amount: float = 0.0
    currency: str = "USD"
    
    # Usage
    usage_quantity: float = 0.0
    usage_unit: str = ""
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Allocation
    cost_center: str = ""
    project: str = ""
    environment: str = ""
    team: str = ""
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)


@dataclass
class Budget:
    """Бюджет"""
    budget_id: str
    name: str
    
    # Scope
    provider: Optional[CloudProvider] = None
    cost_center: str = ""
    project: str = ""
    team: str = ""
    
    # Amount
    amount: float = 0.0
    currency: str = "USD"
    
    # Period
    period: BudgetPeriod = BudgetPeriod.MONTHLY
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    
    # Thresholds
    alert_thresholds: List[int] = field(default_factory=lambda: [50, 80, 100])
    
    # Current
    current_spend: float = 0.0
    forecasted_spend: float = 0.0
    
    # Status
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CostAllocationRule:
    """Правило распределения затрат"""
    rule_id: str
    name: str
    
    # Source
    source_tags: Dict[str, str] = field(default_factory=dict)
    source_services: List[str] = field(default_factory=list)
    
    # Target
    target_cost_center: str = ""
    target_project: str = ""
    target_team: str = ""
    
    # Split
    split_type: str = "percentage"  # percentage, fixed, proportional
    split_percentage: float = 100.0
    
    # Priority
    priority: int = 0
    
    # Status
    is_active: bool = True


@dataclass
class ReservedInstance:
    """Зарезервированный инстанс"""
    ri_id: str
    
    # Provider
    provider: CloudProvider = CloudProvider.AWS
    
    # Type
    instance_type: str = ""
    platform: str = ""  # Linux, Windows, etc.
    region: str = ""
    
    # Term
    term_months: int = 12  # 12 or 36
    payment_option: str = "all_upfront"  # all_upfront, partial_upfront, no_upfront
    
    # Cost
    upfront_cost: float = 0.0
    hourly_cost: float = 0.0
    on_demand_hourly: float = 0.0  # For comparison
    
    # Savings
    savings_percentage: float = 0.0
    total_savings: float = 0.0
    
    # Utilization
    utilization_percentage: float = 0.0
    
    # Coverage
    covered_instances: List[str] = field(default_factory=list)
    
    # Dates
    start_date: datetime = field(default_factory=datetime.now)
    end_date: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=365))
    
    # Status
    status: str = "active"  # active, expired, scheduled


@dataclass
class SavingsPlan:
    """План экономии"""
    plan_id: str
    name: str
    
    # Provider
    provider: CloudProvider = CloudProvider.AWS
    
    # Type
    plan_type: str = "compute"  # compute, ec2_instance, sagemaker
    
    # Commitment
    hourly_commitment: float = 0.0
    
    # Term
    term_months: int = 12
    payment_option: str = "all_upfront"
    
    # Cost
    upfront_cost: float = 0.0
    
    # Savings
    savings_percentage: float = 0.0
    
    # Utilization
    utilization_percentage: float = 0.0
    
    # Coverage
    covered_usage: float = 0.0
    total_usage: float = 0.0
    
    # Dates
    start_date: datetime = field(default_factory=datetime.now)
    end_date: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=365))
    
    # Status
    status: str = "active"


@dataclass
class CostAlert:
    """Оповещение о затратах"""
    alert_id: str
    
    # Type
    alert_type: str = "budget_threshold"  # budget_threshold, anomaly, forecast
    severity: AlertSeverity = AlertSeverity.WARNING
    
    # Budget
    budget_id: str = ""
    
    # Message
    title: str = ""
    message: str = ""
    
    # Values
    threshold_value: float = 0.0
    actual_value: float = 0.0
    
    # Status
    is_acknowledged: bool = False
    acknowledged_by: str = ""
    acknowledged_at: Optional[datetime] = None
    
    # Timestamps
    triggered_at: datetime = field(default_factory=datetime.now)


@dataclass
class CostRecommendation:
    """Рекомендация по оптимизации"""
    recommendation_id: str
    
    # Type
    recommendation_type: RecommendationType = RecommendationType.RIGHTSIZE
    
    # Resource
    resource_id: str = ""
    resource_name: str = ""
    resource_type: str = ""
    
    # Provider
    provider: CloudProvider = CloudProvider.AWS
    region: str = ""
    
    # Current
    current_cost: float = 0.0
    current_config: str = ""
    
    # Recommended
    recommended_cost: float = 0.0
    recommended_config: str = ""
    
    # Savings
    estimated_savings: float = 0.0
    savings_percentage: float = 0.0
    
    # Effort
    implementation_effort: str = "low"  # low, medium, high
    
    # Risk
    risk_level: str = "low"
    
    # Status
    status: str = "open"  # open, implemented, dismissed, in_progress
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    implemented_at: Optional[datetime] = None


@dataclass
class CostReport:
    """Отчет о затратах"""
    report_id: str
    name: str
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Scope
    providers: List[CloudProvider] = field(default_factory=list)
    cost_centers: List[str] = field(default_factory=list)
    
    # Totals
    total_cost: float = 0.0
    previous_period_cost: float = 0.0
    cost_change_percentage: float = 0.0
    
    # Breakdown
    cost_by_provider: Dict[str, float] = field(default_factory=dict)
    cost_by_service: Dict[str, float] = field(default_factory=dict)
    cost_by_region: Dict[str, float] = field(default_factory=dict)
    cost_by_team: Dict[str, float] = field(default_factory=dict)
    
    # Trend
    trend: CostTrend = CostTrend.STABLE
    
    # Generated
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Anomaly:
    """Аномалия затрат"""
    anomaly_id: str
    
    # Type
    anomaly_type: str = "spike"  # spike, drop, unusual_pattern
    
    # Resource
    resource_id: str = ""
    service_name: str = ""
    
    # Provider
    provider: CloudProvider = CloudProvider.AWS
    
    # Values
    expected_cost: float = 0.0
    actual_cost: float = 0.0
    deviation_percentage: float = 0.0
    
    # Root cause
    root_cause: str = ""
    
    # Status
    status: str = "open"  # open, resolved, acknowledged
    
    # Timestamps
    detected_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


class CostManager:
    """Менеджер затрат"""
    
    def __init__(self):
        self.cost_items: Dict[str, CostItem] = {}
        self.budgets: Dict[str, Budget] = {}
        self.allocation_rules: Dict[str, CostAllocationRule] = {}
        self.reserved_instances: Dict[str, ReservedInstance] = {}
        self.savings_plans: Dict[str, SavingsPlan] = {}
        self.alerts: Dict[str, CostAlert] = {}
        self.recommendations: Dict[str, CostRecommendation] = {}
        self.reports: Dict[str, CostReport] = {}
        self.anomalies: Dict[str, Anomaly] = {}
        
    async def add_cost_item(self, provider: CloudProvider,
                           service_name: str,
                           service_category: ServiceCategory,
                           resource_id: str,
                           resource_name: str,
                           cost_amount: float,
                           region: str = "",
                           tags: Dict[str, str] = None) -> CostItem:
        """Добавление элемента затрат"""
        item = CostItem(
            item_id=f"cost_{uuid.uuid4().hex[:12]}",
            provider=provider,
            service_name=service_name,
            service_category=service_category,
            resource_id=resource_id,
            resource_name=resource_name,
            cost_amount=cost_amount,
            region=region,
            tags=tags or {}
        )
        
        # Apply allocation rules
        await self._apply_allocation_rules(item)
        
        self.cost_items[item.item_id] = item
        
        # Update budget tracking
        await self._update_budget_tracking(item)
        
        # Check for anomalies
        await self._check_anomalies(item)
        
        return item
        
    async def _apply_allocation_rules(self, item: CostItem):
        """Применение правил распределения"""
        for rule in sorted(self.allocation_rules.values(), key=lambda r: r.priority, reverse=True):
            if not rule.is_active:
                continue
                
            # Check tag match
            tag_match = all(item.tags.get(k) == v for k, v in rule.source_tags.items())
            service_match = not rule.source_services or item.service_name in rule.source_services
            
            if tag_match and service_match:
                if rule.target_cost_center:
                    item.cost_center = rule.target_cost_center
                if rule.target_project:
                    item.project = rule.target_project
                if rule.target_team:
                    item.team = rule.target_team
                break
                
    async def _update_budget_tracking(self, item: CostItem):
        """Обновление отслеживания бюджета"""
        for budget in self.budgets.values():
            if not budget.is_active:
                continue
                
            # Check scope match
            matches = True
            if budget.provider and item.provider != budget.provider:
                matches = False
            if budget.cost_center and item.cost_center != budget.cost_center:
                matches = False
            if budget.project and item.project != budget.project:
                matches = False
            if budget.team and item.team != budget.team:
                matches = False
                
            if matches:
                budget.current_spend += item.cost_amount
                
                # Check thresholds
                for threshold in budget.alert_thresholds:
                    percentage = (budget.current_spend / budget.amount) * 100
                    if percentage >= threshold:
                        await self._create_budget_alert(budget, threshold, percentage)
                        
    async def _check_anomalies(self, item: CostItem):
        """Проверка аномалий"""
        # Simplified anomaly detection - check if cost is significantly higher than average
        similar_items = [i for i in self.cost_items.values()
                        if i.service_name == item.service_name and i.region == item.region]
                        
        if len(similar_items) >= 5:
            avg_cost = sum(i.cost_amount for i in similar_items) / len(similar_items)
            if item.cost_amount > avg_cost * 2:
                anomaly = Anomaly(
                    anomaly_id=f"anom_{uuid.uuid4().hex[:8]}",
                    anomaly_type="spike",
                    resource_id=item.resource_id,
                    service_name=item.service_name,
                    provider=item.provider,
                    expected_cost=avg_cost,
                    actual_cost=item.cost_amount,
                    deviation_percentage=((item.cost_amount - avg_cost) / avg_cost) * 100
                )
                self.anomalies[anomaly.anomaly_id] = anomaly
                
    async def _create_budget_alert(self, budget: Budget,
                                   threshold: int,
                                   actual_percentage: float):
        """Создание оповещения бюджета"""
        # Check if alert already exists
        for alert in self.alerts.values():
            if alert.budget_id == budget.budget_id and alert.threshold_value == threshold:
                return
                
        severity = AlertSeverity.INFO
        if threshold >= 100:
            severity = AlertSeverity.CRITICAL
        elif threshold >= 80:
            severity = AlertSeverity.WARNING
            
        alert = CostAlert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            alert_type="budget_threshold",
            severity=severity,
            budget_id=budget.budget_id,
            title=f"Budget '{budget.name}' at {actual_percentage:.1f}%",
            message=f"Budget threshold of {threshold}% reached. Current spend: ${budget.current_spend:,.2f}",
            threshold_value=threshold,
            actual_value=actual_percentage
        )
        
        self.alerts[alert.alert_id] = alert
        
    async def create_budget(self, name: str,
                           amount: float,
                           period: BudgetPeriod = BudgetPeriod.MONTHLY,
                           provider: CloudProvider = None,
                           cost_center: str = "",
                           project: str = "",
                           team: str = "",
                           thresholds: List[int] = None) -> Budget:
        """Создание бюджета"""
        budget = Budget(
            budget_id=f"budget_{uuid.uuid4().hex[:8]}",
            name=name,
            amount=amount,
            period=period,
            provider=provider,
            cost_center=cost_center,
            project=project,
            team=team,
            alert_thresholds=thresholds or [50, 80, 100]
        )
        
        self.budgets[budget.budget_id] = budget
        return budget
        
    async def create_allocation_rule(self, name: str,
                                    source_tags: Dict[str, str] = None,
                                    source_services: List[str] = None,
                                    target_cost_center: str = "",
                                    target_project: str = "",
                                    target_team: str = "",
                                    priority: int = 0) -> CostAllocationRule:
        """Создание правила распределения"""
        rule = CostAllocationRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name=name,
            source_tags=source_tags or {},
            source_services=source_services or [],
            target_cost_center=target_cost_center,
            target_project=target_project,
            target_team=target_team,
            priority=priority
        )
        
        self.allocation_rules[rule.rule_id] = rule
        return rule
        
    async def add_reserved_instance(self, provider: CloudProvider,
                                   instance_type: str,
                                   platform: str,
                                   region: str,
                                   term_months: int = 12,
                                   payment_option: str = "all_upfront",
                                   upfront_cost: float = 0.0,
                                   hourly_cost: float = 0.0,
                                   on_demand_hourly: float = 0.0) -> ReservedInstance:
        """Добавление зарезервированного инстанса"""
        savings_pct = ((on_demand_hourly - hourly_cost) / on_demand_hourly * 100) if on_demand_hourly > 0 else 0
        total_hours = term_months * 30 * 24
        total_savings = (on_demand_hourly - hourly_cost) * total_hours - upfront_cost
        
        ri = ReservedInstance(
            ri_id=f"ri_{uuid.uuid4().hex[:8]}",
            provider=provider,
            instance_type=instance_type,
            platform=platform,
            region=region,
            term_months=term_months,
            payment_option=payment_option,
            upfront_cost=upfront_cost,
            hourly_cost=hourly_cost,
            on_demand_hourly=on_demand_hourly,
            savings_percentage=savings_pct,
            total_savings=total_savings,
            end_date=datetime.now() + timedelta(days=term_months * 30)
        )
        
        self.reserved_instances[ri.ri_id] = ri
        return ri
        
    async def add_savings_plan(self, name: str,
                              provider: CloudProvider,
                              plan_type: str,
                              hourly_commitment: float,
                              term_months: int = 12,
                              payment_option: str = "all_upfront",
                              upfront_cost: float = 0.0,
                              savings_percentage: float = 0.0) -> SavingsPlan:
        """Добавление плана экономии"""
        plan = SavingsPlan(
            plan_id=f"sp_{uuid.uuid4().hex[:8]}",
            name=name,
            provider=provider,
            plan_type=plan_type,
            hourly_commitment=hourly_commitment,
            term_months=term_months,
            payment_option=payment_option,
            upfront_cost=upfront_cost,
            savings_percentage=savings_percentage,
            end_date=datetime.now() + timedelta(days=term_months * 30)
        )
        
        self.savings_plans[plan.plan_id] = plan
        return plan
        
    async def create_recommendation(self, recommendation_type: RecommendationType,
                                   resource_id: str,
                                   resource_name: str,
                                   resource_type: str,
                                   provider: CloudProvider,
                                   current_cost: float,
                                   current_config: str,
                                   recommended_cost: float,
                                   recommended_config: str,
                                   effort: str = "low",
                                   risk: str = "low") -> CostRecommendation:
        """Создание рекомендации"""
        savings = current_cost - recommended_cost
        savings_pct = (savings / current_cost * 100) if current_cost > 0 else 0
        
        rec = CostRecommendation(
            recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
            recommendation_type=recommendation_type,
            resource_id=resource_id,
            resource_name=resource_name,
            resource_type=resource_type,
            provider=provider,
            current_cost=current_cost,
            current_config=current_config,
            recommended_cost=recommended_cost,
            recommended_config=recommended_config,
            estimated_savings=savings,
            savings_percentage=savings_pct,
            implementation_effort=effort,
            risk_level=risk
        )
        
        self.recommendations[rec.recommendation_id] = rec
        return rec
        
    async def implement_recommendation(self, recommendation_id: str) -> bool:
        """Применение рекомендации"""
        rec = self.recommendations.get(recommendation_id)
        if not rec or rec.status != "open":
            return False
            
        rec.status = "implemented"
        rec.implemented_at = datetime.now()
        return True
        
    async def dismiss_recommendation(self, recommendation_id: str) -> bool:
        """Отклонение рекомендации"""
        rec = self.recommendations.get(recommendation_id)
        if not rec:
            return False
            
        rec.status = "dismissed"
        return True
        
    async def generate_report(self, name: str,
                             period_start: datetime,
                             period_end: datetime,
                             providers: List[CloudProvider] = None,
                             cost_centers: List[str] = None) -> CostReport:
        """Генерация отчета"""
        report = CostReport(
            report_id=f"report_{uuid.uuid4().hex[:8]}",
            name=name,
            period_start=period_start,
            period_end=period_end,
            providers=providers or [],
            cost_centers=cost_centers or []
        )
        
        # Calculate totals
        for item in self.cost_items.values():
            if providers and item.provider not in providers:
                continue
            if cost_centers and item.cost_center not in cost_centers:
                continue
                
            report.total_cost += item.cost_amount
            
            # By provider
            provider_key = item.provider.value
            report.cost_by_provider[provider_key] = report.cost_by_provider.get(provider_key, 0) + item.cost_amount
            
            # By service
            report.cost_by_service[item.service_name] = report.cost_by_service.get(item.service_name, 0) + item.cost_amount
            
            # By region
            report.cost_by_region[item.region] = report.cost_by_region.get(item.region, 0) + item.cost_amount
            
            # By team
            if item.team:
                report.cost_by_team[item.team] = report.cost_by_team.get(item.team, 0) + item.cost_amount
                
        self.reports[report.report_id] = report
        return report
        
    async def acknowledge_alert(self, alert_id: str, user: str) -> bool:
        """Подтверждение оповещения"""
        alert = self.alerts.get(alert_id)
        if not alert:
            return False
            
        alert.is_acknowledged = True
        alert.acknowledged_by = user
        alert.acknowledged_at = datetime.now()
        return True
        
    def get_total_spend(self, provider: CloudProvider = None,
                       cost_center: str = "",
                       team: str = "") -> float:
        """Получение общих затрат"""
        total = 0.0
        for item in self.cost_items.values():
            if provider and item.provider != provider:
                continue
            if cost_center and item.cost_center != cost_center:
                continue
            if team and item.team != team:
                continue
            total += item.cost_amount
        return total
        
    def get_ri_utilization(self) -> Dict[str, Any]:
        """Получение утилизации RI"""
        total_ri = len(self.reserved_instances)
        active_ri = sum(1 for ri in self.reserved_instances.values() if ri.status == "active")
        
        total_savings = sum(ri.total_savings for ri in self.reserved_instances.values())
        avg_utilization = 0.0
        if self.reserved_instances:
            avg_utilization = sum(ri.utilization_percentage for ri in self.reserved_instances.values()) / len(self.reserved_instances)
            
        return {
            "total": total_ri,
            "active": active_ri,
            "total_savings": total_savings,
            "avg_utilization": avg_utilization
        }
        
    def get_savings_plan_coverage(self) -> Dict[str, Any]:
        """Получение покрытия Savings Plans"""
        total_plans = len(self.savings_plans)
        active_plans = sum(1 for sp in self.savings_plans.values() if sp.status == "active")
        
        total_commitment = sum(sp.hourly_commitment for sp in self.savings_plans.values())
        avg_savings = 0.0
        if self.savings_plans:
            avg_savings = sum(sp.savings_percentage for sp in self.savings_plans.values()) / len(self.savings_plans)
            
        return {
            "total": total_plans,
            "active": active_plans,
            "hourly_commitment": total_commitment,
            "avg_savings_percentage": avg_savings
        }
        
    def get_potential_savings(self) -> Dict[str, Any]:
        """Получение потенциальной экономии"""
        open_recs = [r for r in self.recommendations.values() if r.status == "open"]
        
        total_savings = sum(r.estimated_savings for r in open_recs)
        by_type = {}
        
        for rec in open_recs:
            rec_type = rec.recommendation_type.value
            by_type[rec_type] = by_type.get(rec_type, 0) + rec.estimated_savings
            
        return {
            "total_potential_savings": total_savings,
            "open_recommendations": len(open_recs),
            "savings_by_type": by_type
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_spend = sum(item.cost_amount for item in self.cost_items.values())
        
        by_provider = {}
        by_category = {}
        by_team = {}
        
        for item in self.cost_items.values():
            by_provider[item.provider.value] = by_provider.get(item.provider.value, 0) + item.cost_amount
            by_category[item.service_category.value] = by_category.get(item.service_category.value, 0) + item.cost_amount
            if item.team:
                by_team[item.team] = by_team.get(item.team, 0) + item.cost_amount
                
        active_budgets = sum(1 for b in self.budgets.values() if b.is_active)
        over_budget = sum(1 for b in self.budgets.values() if b.current_spend > b.amount)
        
        unacknowledged_alerts = sum(1 for a in self.alerts.values() if not a.is_acknowledged)
        
        return {
            "total_spend": total_spend,
            "cost_by_provider": by_provider,
            "cost_by_category": by_category,
            "cost_by_team": by_team,
            "total_budgets": len(self.budgets),
            "active_budgets": active_budgets,
            "over_budget": over_budget,
            "total_alerts": len(self.alerts),
            "unacknowledged_alerts": unacknowledged_alerts,
            "total_recommendations": len(self.recommendations),
            "open_recommendations": sum(1 for r in self.recommendations.values() if r.status == "open"),
            "total_anomalies": len(self.anomalies),
            "open_anomalies": sum(1 for a in self.anomalies.values() if a.status == "open")
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 328: Cost Management Platform")
    print("=" * 60)
    
    cost_mgr = CostManager()
    print("✓ Cost Manager created")
    
    # Create allocation rules
    print("\n📋 Creating Allocation Rules...")
    
    rules_data = [
        ("Production Environment", {"env": "production"}, [], "CC001", "PROD", "Platform"),
        ("Development Environment", {"env": "development"}, [], "CC002", "DEV", "Engineering"),
        ("Database Services", {}, ["RDS", "DynamoDB", "Aurora"], "CC003", "DATA", "Data"),
        ("ML Services", {"team": "ml"}, ["SageMaker", "Rekognition"], "CC004", "ML", "ML Team"),
        ("Analytics", {"project": "analytics"}, ["Redshift", "Athena"], "CC005", "ANALYTICS", "Analytics")
    ]
    
    for name, tags, services, cc, project, team in rules_data:
        await cost_mgr.create_allocation_rule(name, tags, services, cc, project, team)
        print(f"  📋 {name}")
        
    # Create budgets
    print("\n💰 Creating Budgets...")
    
    budgets_data = [
        ("AWS Monthly", 50000, BudgetPeriod.MONTHLY, CloudProvider.AWS, "", "", ""),
        ("Azure Monthly", 30000, BudgetPeriod.MONTHLY, CloudProvider.AZURE, "", "", ""),
        ("Platform Team", 25000, BudgetPeriod.MONTHLY, None, "", "", "Platform"),
        ("Engineering Team", 40000, BudgetPeriod.MONTHLY, None, "", "", "Engineering"),
        ("Data Team", 35000, BudgetPeriod.MONTHLY, None, "", "", "Data"),
        ("Production Workloads", 60000, BudgetPeriod.MONTHLY, None, "CC001", "PROD", ""),
        ("Development Workloads", 15000, BudgetPeriod.MONTHLY, None, "CC002", "DEV", "")
    ]
    
    budgets = []
    for name, amount, period, provider, cc, project, team in budgets_data:
        budget = await cost_mgr.create_budget(name, amount, period, provider, cc, project, team)
        budgets.append(budget)
        print(f"  💰 {name}: ${amount:,.0f}")
        
    # Add cost items
    print("\n📊 Adding Cost Items...")
    
    services = [
        (CloudProvider.AWS, "EC2", ServiceCategory.COMPUTE, "us-east-1", {"env": "production"}),
        (CloudProvider.AWS, "EC2", ServiceCategory.COMPUTE, "us-west-2", {"env": "development"}),
        (CloudProvider.AWS, "RDS", ServiceCategory.DATABASE, "us-east-1", {"env": "production"}),
        (CloudProvider.AWS, "S3", ServiceCategory.STORAGE, "us-east-1", {"env": "production"}),
        (CloudProvider.AWS, "Lambda", ServiceCategory.COMPUTE, "us-east-1", {"env": "production"}),
        (CloudProvider.AWS, "SageMaker", ServiceCategory.AI_ML, "us-east-1", {"team": "ml"}),
        (CloudProvider.AWS, "Redshift", ServiceCategory.ANALYTICS, "us-east-1", {"project": "analytics"}),
        (CloudProvider.AZURE, "Virtual Machines", ServiceCategory.COMPUTE, "eastus", {"env": "production"}),
        (CloudProvider.AZURE, "SQL Database", ServiceCategory.DATABASE, "eastus", {"env": "production"}),
        (CloudProvider.AZURE, "Blob Storage", ServiceCategory.STORAGE, "eastus", {"env": "production"}),
        (CloudProvider.GCP, "Compute Engine", ServiceCategory.COMPUTE, "us-central1", {"env": "production"}),
        (CloudProvider.GCP, "BigQuery", ServiceCategory.ANALYTICS, "us-central1", {"project": "analytics"})
    ]
    
    cost_items = []
    for provider, service, category, region, tags in services:
        for i in range(random.randint(3, 8)):
            cost = random.uniform(500, 5000)
            item = await cost_mgr.add_cost_item(
                provider=provider,
                service_name=service,
                service_category=category,
                resource_id=f"{service.lower()}-{uuid.uuid4().hex[:8]}",
                resource_name=f"{service} Instance {i+1}",
                cost_amount=cost,
                region=region,
                tags=tags
            )
            cost_items.append(item)
            
    print(f"  ✓ Added {len(cost_items)} cost items")
    
    # Add reserved instances
    print("\n🔒 Adding Reserved Instances...")
    
    ri_data = [
        (CloudProvider.AWS, "m5.xlarge", "Linux", "us-east-1", 12, "all_upfront", 2000, 0.08, 0.192),
        (CloudProvider.AWS, "c5.2xlarge", "Linux", "us-east-1", 36, "partial_upfront", 5000, 0.12, 0.34),
        (CloudProvider.AWS, "r5.large", "Linux", "us-west-2", 12, "no_upfront", 0, 0.10, 0.126),
        (CloudProvider.AZURE, "D4s_v3", "Windows", "eastus", 12, "all_upfront", 1800, 0.15, 0.38),
        (CloudProvider.GCP, "n1-standard-4", "Linux", "us-central1", 12, "all_upfront", 1500, 0.07, 0.19)
    ]
    
    reserved_instances = []
    for provider, itype, platform, region, term, payment, upfront, hourly, on_demand in ri_data:
        ri = await cost_mgr.add_reserved_instance(
            provider, itype, platform, region, term, payment, upfront, hourly, on_demand
        )
        ri.utilization_percentage = random.uniform(60, 95)
        reserved_instances.append(ri)
        print(f"  🔒 {provider.value} {itype}: {ri.savings_percentage:.1f}% savings")
        
    # Add savings plans
    print("\n📈 Adding Savings Plans...")
    
    sp_data = [
        ("Compute Savings Plan 1", CloudProvider.AWS, "compute", 10.0, 12, "all_upfront", 20000, 22),
        ("EC2 Instance Savings Plan", CloudProvider.AWS, "ec2_instance", 5.0, 36, "partial_upfront", 30000, 30),
        ("SageMaker Savings Plan", CloudProvider.AWS, "sagemaker", 2.0, 12, "no_upfront", 0, 15)
    ]
    
    savings_plans = []
    for name, provider, plan_type, commitment, term, payment, upfront, savings_pct in sp_data:
        plan = await cost_mgr.add_savings_plan(
            name, provider, plan_type, commitment, term, payment, upfront, savings_pct
        )
        plan.utilization_percentage = random.uniform(70, 95)
        savings_plans.append(plan)
        print(f"  📈 {name}: ${commitment:.2f}/hr commitment")
        
    # Create recommendations
    print("\n💡 Creating Optimization Recommendations...")
    
    rec_data = [
        (RecommendationType.RIGHTSIZE, "ec2-abc123", "Web Server 1", "EC2", CloudProvider.AWS, 500, "m5.xlarge", 250, "m5.large", "low", "low"),
        (RecommendationType.RIGHTSIZE, "ec2-def456", "App Server 1", "EC2", CloudProvider.AWS, 800, "c5.2xlarge", 400, "c5.xlarge", "low", "low"),
        (RecommendationType.RESERVED, "rds-ghi789", "Database", "RDS", CloudProvider.AWS, 1200, "On-Demand", 720, "1yr RI", "medium", "low"),
        (RecommendationType.DELETE, "ebs-jkl012", "Unused Volume", "EBS", CloudProvider.AWS, 100, "500GB gp2", 0, "Delete", "low", "low"),
        (RecommendationType.SPOT, "ec2-mno345", "Batch Server", "EC2", CloudProvider.AWS, 600, "On-Demand", 180, "Spot", "medium", "medium"),
        (RecommendationType.STORAGE_TIER, "s3-pqr678", "Archive Bucket", "S3", CloudProvider.AWS, 200, "Standard", 20, "Glacier", "low", "low"),
        (RecommendationType.SCHEDULE, "ec2-stu901", "Dev Server", "EC2", CloudProvider.AWS, 400, "24/7", 100, "10hr/day", "medium", "low")
    ]
    
    recommendations = []
    for rec_type, res_id, res_name, res_type, provider, curr_cost, curr_config, rec_cost, rec_config, effort, risk in rec_data:
        rec = await cost_mgr.create_recommendation(
            rec_type, res_id, res_name, res_type, provider, curr_cost, curr_config, rec_cost, rec_config, effort, risk
        )
        recommendations.append(rec)
        print(f"  💡 {rec_type.value}: {res_name} - Save ${rec.estimated_savings:.2f}")
        
    # Implement some recommendations
    for rec in recommendations[:2]:
        await cost_mgr.implement_recommendation(rec.recommendation_id)
        
    # Generate report
    print("\n📊 Generating Cost Report...")
    
    report = await cost_mgr.generate_report(
        "Monthly Cost Report",
        datetime.now() - timedelta(days=30),
        datetime.now()
    )
    print(f"  ✓ Report generated: ${report.total_cost:,.2f} total")
    
    # Budget status
    print("\n💰 Budget Status:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Budget                       │ Amount       │ Spent        │ Remaining    │ Usage    │ Status      │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for budget in budgets:
        name = budget.name[:28].ljust(28)
        amount = f"${budget.amount:,.0f}".ljust(12)
        spent = f"${budget.current_spend:,.0f}".ljust(12)
        remaining = f"${max(0, budget.amount - budget.current_spend):,.0f}".ljust(12)
        
        usage_pct = (budget.current_spend / budget.amount) * 100 if budget.amount > 0 else 0
        usage = f"{usage_pct:.1f}%".ljust(8)
        
        status = "✓ OK" if usage_pct < 80 else "⚠ Warning" if usage_pct < 100 else "✗ Over"
        status = status[:11].ljust(11)
        
        print(f"  │ {name} │ {amount} │ {spent} │ {remaining} │ {usage} │ {status} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Cost by provider
    print("\n☁️ Cost by Provider:")
    
    stats = cost_mgr.get_statistics()
    total = stats['total_spend']
    
    for provider, cost in sorted(stats['cost_by_provider'].items(), key=lambda x: x[1], reverse=True):
        pct = (cost / total * 100) if total > 0 else 0
        bar_len = int(pct / 2.5)
        bar = "█" * bar_len + "░" * (40 - bar_len)
        print(f"  {provider:10} [{bar}] ${cost:,.0f} ({pct:.1f}%)")
        
    # Cost by category
    print("\n📂 Cost by Category:")
    
    for category, cost in sorted(stats['cost_by_category'].items(), key=lambda x: x[1], reverse=True):
        pct = (cost / total * 100) if total > 0 else 0
        bar_len = int(pct / 2.5)
        bar = "█" * bar_len + "░" * (40 - bar_len)
        print(f"  {category:12} [{bar}] ${cost:,.0f} ({pct:.1f}%)")
        
    # Reserved Instances
    print("\n🔒 Reserved Instances:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Instance Type  │ Provider │ Term │ Payment    │ Utilization │ Savings   │ Status     │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────┤")
    
    for ri in reserved_instances:
        itype = ri.instance_type[:14].ljust(14)
        provider = ri.provider.value[:8].ljust(8)
        term = f"{ri.term_months}mo".ljust(4)
        payment = ri.payment_option[:10].ljust(10)
        util = f"{ri.utilization_percentage:.1f}%".ljust(11)
        savings = f"{ri.savings_percentage:.1f}%".ljust(9)
        status = ri.status[:10].ljust(10)
        
        print(f"  │ {itype} │ {provider} │ {term} │ {payment} │ {util} │ {savings} │ {status} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────┘")
    
    ri_stats = cost_mgr.get_ri_utilization()
    print(f"\n  Total RI Savings: ${ri_stats['total_savings']:,.2f}")
    print(f"  Average Utilization: {ri_stats['avg_utilization']:.1f}%")
    
    # Savings Plans
    print("\n📈 Savings Plans:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Plan Name                    │ Type     │ Commitment │ Utilization │ Savings        │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────┤")
    
    for plan in savings_plans:
        name = plan.name[:28].ljust(28)
        plan_type = plan.plan_type[:8].ljust(8)
        commitment = f"${plan.hourly_commitment:.2f}/hr".ljust(10)
        util = f"{plan.utilization_percentage:.1f}%".ljust(11)
        savings = f"{plan.savings_percentage:.1f}%".ljust(14)
        
        print(f"  │ {name} │ {plan_type} │ {commitment} │ {util} │ {savings} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Recommendations
    print("\n💡 Optimization Recommendations:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Type           │ Resource               │ Current     │ Recommended │ Savings     │ Status      │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for rec in recommendations:
        rec_type = rec.recommendation_type.value[:14].ljust(14)
        resource = rec.resource_name[:22].ljust(22)
        current = f"${rec.current_cost:.0f}".ljust(11)
        recommended = f"${rec.recommended_cost:.0f}".ljust(11)
        savings = f"${rec.estimated_savings:.0f}".ljust(11)
        
        status_icon = {"open": "○", "implemented": "✓", "dismissed": "✗", "in_progress": "◐"}.get(rec.status, "?")
        status = f"{status_icon} {rec.status}"[:11].ljust(11)
        
        print(f"  │ {rec_type} │ {resource} │ {current} │ {recommended} │ {savings} │ {status} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    potential = cost_mgr.get_potential_savings()
    print(f"\n  Total Potential Savings: ${potential['total_potential_savings']:,.2f}")
    print(f"  Open Recommendations: {potential['open_recommendations']}")
    
    # Alerts
    print("\n🔔 Active Alerts:")
    
    unack_alerts = [a for a in cost_mgr.alerts.values() if not a.is_acknowledged]
    if unack_alerts:
        for alert in unack_alerts[:5]:
            icon = {"info": "ℹ", "warning": "⚠", "critical": "🚨"}.get(alert.severity.value, "?")
            print(f"  {icon} {alert.title}")
    else:
        print("  ✓ No unacknowledged alerts")
        
    # Anomalies
    print("\n⚡ Cost Anomalies:")
    
    open_anomalies = [a for a in cost_mgr.anomalies.values() if a.status == "open"]
    if open_anomalies:
        for anomaly in open_anomalies[:5]:
            print(f"  ⚡ {anomaly.service_name}: {anomaly.deviation_percentage:.1f}% deviation")
    else:
        print("  ✓ No active anomalies")
        
    # Statistics
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Total Spend: ${stats['total_spend']:,.2f}")
    print(f"  Budgets: {stats['active_budgets']}/{stats['total_budgets']} active, {stats['over_budget']} over budget")
    print(f"  Alerts: {stats['unacknowledged_alerts']}/{stats['total_alerts']} unacknowledged")
    print(f"  Recommendations: {stats['open_recommendations']}/{stats['total_recommendations']} open")
    print(f"  Anomalies: {stats['open_anomalies']}/{stats['total_anomalies']} open")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                     Cost Management Platform                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Monthly Spend:          ${stats['total_spend']:>12,.2f}                  │")
    print(f"│ Potential Savings:            ${potential['total_potential_savings']:>12,.2f}                  │")
    print(f"│ RI Savings:                   ${ri_stats['total_savings']:>12,.2f}                  │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Active Budgets:               {stats['active_budgets']:>12}                      │")
    print(f"│ Over Budget:                  {stats['over_budget']:>12}                      │")
    print(f"│ Open Recommendations:         {stats['open_recommendations']:>12}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Cost Management Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
