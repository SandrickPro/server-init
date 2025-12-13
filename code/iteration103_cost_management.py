#!/usr/bin/env python3
"""
Server Init - Iteration 103: Cost Management Platform
Платформа управления затратами

Функционал:
- Cost Tracking - отслеживание затрат
- Budget Management - управление бюджетами
- Cost Allocation - распределение затрат
- Cost Optimization - оптимизация
- Forecasting - прогнозирование
- Anomaly Detection - обнаружение аномалий
- Chargeback/Showback - возврат затрат
- Reports & Dashboards - отчёты и дашборды
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Union, Tuple
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
    KUBERNETES = "kubernetes"
    SERVERLESS = "serverless"
    SUPPORT = "support"
    OTHER = "other"


class ResourceType(Enum):
    """Тип ресурса"""
    VM = "vm"
    CONTAINER = "container"
    STORAGE_BLOCK = "storage_block"
    STORAGE_OBJECT = "storage_object"
    DATABASE_INSTANCE = "database_instance"
    LOAD_BALANCER = "load_balancer"
    NETWORK_TRAFFIC = "network_traffic"
    FUNCTION = "function"


class BudgetPeriod(Enum):
    """Период бюджета"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class AlertThresholdType(Enum):
    """Тип порога алерта"""
    PERCENTAGE = "percentage"
    ABSOLUTE = "absolute"


class OptimizationType(Enum):
    """Тип оптимизации"""
    RIGHTSIZING = "rightsizing"
    RESERVED_INSTANCES = "reserved_instances"
    SPOT_INSTANCES = "spot_instances"
    UNUSED_RESOURCES = "unused_resources"
    STORAGE_OPTIMIZATION = "storage_optimization"
    SCHEDULING = "scheduling"


@dataclass
class CostRecord:
    """Запись о затратах"""
    record_id: str
    
    # Resource
    resource_id: str = ""
    resource_name: str = ""
    resource_type: ResourceType = ResourceType.VM
    
    # Category
    category: CostCategory = CostCategory.COMPUTE
    
    # Cost
    amount: float = 0.0
    currency: str = "USD"
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Ownership
    project: str = ""
    team: str = ""
    environment: str = ""
    
    # Time
    timestamp: datetime = field(default_factory=datetime.now)
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)


@dataclass
class Budget:
    """Бюджет"""
    budget_id: str
    name: str = ""
    
    # Scope
    project: str = ""
    team: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Amount
    amount: float = 0.0
    currency: str = "USD"
    
    # Period
    period: BudgetPeriod = BudgetPeriod.MONTHLY
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    
    # Current spend
    current_spend: float = 0.0
    
    # Alerts
    alert_thresholds: List[float] = field(default_factory=lambda: [50, 80, 100])
    alerts_triggered: List[float] = field(default_factory=list)
    
    # Status
    active: bool = True


@dataclass
class CostAllocation:
    """Распределение затрат"""
    allocation_id: str
    
    # Source
    source_cost: float = 0.0
    
    # Targets
    allocations: Dict[str, float] = field(default_factory=dict)  # target -> percentage
    
    # Method
    allocation_method: str = "usage"  # usage, equal, custom
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)


@dataclass
class OptimizationRecommendation:
    """Рекомендация по оптимизации"""
    recommendation_id: str
    
    # Type
    optimization_type: OptimizationType = OptimizationType.RIGHTSIZING
    
    # Resource
    resource_id: str = ""
    resource_name: str = ""
    
    # Savings
    estimated_savings_monthly: float = 0.0
    estimated_savings_yearly: float = 0.0
    
    # Details
    current_state: Dict[str, Any] = field(default_factory=dict)
    recommended_state: Dict[str, Any] = field(default_factory=dict)
    
    # Confidence
    confidence_score: float = 0.0
    
    # Status
    status: str = "pending"  # pending, applied, dismissed
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CostAnomaly:
    """Аномалия затрат"""
    anomaly_id: str
    
    # Detection
    detected_at: datetime = field(default_factory=datetime.now)
    
    # Resource
    resource_id: str = ""
    category: CostCategory = CostCategory.COMPUTE
    
    # Anomaly details
    expected_cost: float = 0.0
    actual_cost: float = 0.0
    deviation_percent: float = 0.0
    
    # Root cause
    root_cause: str = ""
    
    # Status
    acknowledged: bool = False


@dataclass
class CostForecast:
    """Прогноз затрат"""
    forecast_id: str
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Forecast
    forecasted_amount: float = 0.0
    
    # Confidence interval
    lower_bound: float = 0.0
    upper_bound: float = 0.0
    
    # By category
    by_category: Dict[str, float] = field(default_factory=dict)
    
    # Created
    created_at: datetime = field(default_factory=datetime.now)


class CostTracker:
    """Трекер затрат"""
    
    def __init__(self):
        self.records: List[CostRecord] = []
        
    def record_cost(self, resource_id: str, amount: float,
                     category: CostCategory, **kwargs) -> CostRecord:
        """Запись затрат"""
        record = CostRecord(
            record_id=f"cost_{uuid.uuid4().hex[:8]}",
            resource_id=resource_id,
            amount=amount,
            category=category,
            **kwargs
        )
        self.records.append(record)
        return record
        
    def get_costs(self, start_date: datetime = None,
                   end_date: datetime = None,
                   category: CostCategory = None,
                   project: str = None,
                   team: str = None) -> List[CostRecord]:
        """Получение затрат с фильтрами"""
        filtered = self.records
        
        if start_date:
            filtered = [r for r in filtered if r.timestamp >= start_date]
        if end_date:
            filtered = [r for r in filtered if r.timestamp <= end_date]
        if category:
            filtered = [r for r in filtered if r.category == category]
        if project:
            filtered = [r for r in filtered if r.project == project]
        if team:
            filtered = [r for r in filtered if r.team == team]
            
        return filtered
        
    def get_total_cost(self, **filters) -> float:
        """Общие затраты"""
        records = self.get_costs(**filters)
        return sum(r.amount for r in records)
        
    def get_cost_by_category(self, **filters) -> Dict[str, float]:
        """Затраты по категориям"""
        records = self.get_costs(**filters)
        
        by_category = defaultdict(float)
        for record in records:
            by_category[record.category.value] += record.amount
            
        return dict(by_category)
        
    def get_cost_by_project(self, **filters) -> Dict[str, float]:
        """Затраты по проектам"""
        records = self.get_costs(**filters)
        
        by_project = defaultdict(float)
        for record in records:
            by_project[record.project or "unassigned"] += record.amount
            
        return dict(by_project)


class BudgetManager:
    """Менеджер бюджетов"""
    
    def __init__(self):
        self.budgets: Dict[str, Budget] = {}
        self.alerts: List[Dict[str, Any]] = []
        
    def create_budget(self, name: str, amount: float,
                       period: BudgetPeriod = BudgetPeriod.MONTHLY,
                       **kwargs) -> Budget:
        """Создание бюджета"""
        budget = Budget(
            budget_id=f"budget_{uuid.uuid4().hex[:8]}",
            name=name,
            amount=amount,
            period=period,
            **kwargs
        )
        self.budgets[budget.budget_id] = budget
        return budget
        
    def update_spend(self, budget_id: str, spend: float) -> List[Dict[str, Any]]:
        """Обновление расходов"""
        budget = self.budgets.get(budget_id)
        if not budget:
            return []
            
        budget.current_spend = spend
        triggered_alerts = []
        
        # Check thresholds
        spend_percent = (spend / budget.amount) * 100 if budget.amount > 0 else 0
        
        for threshold in budget.alert_thresholds:
            if spend_percent >= threshold and threshold not in budget.alerts_triggered:
                alert = {
                    "budget_id": budget_id,
                    "budget_name": budget.name,
                    "threshold": threshold,
                    "current_spend": spend,
                    "budget_amount": budget.amount,
                    "spend_percent": spend_percent,
                    "timestamp": datetime.now().isoformat()
                }
                triggered_alerts.append(alert)
                budget.alerts_triggered.append(threshold)
                self.alerts.append(alert)
                
        return triggered_alerts
        
    def get_budget_status(self, budget_id: str) -> Dict[str, Any]:
        """Статус бюджета"""
        budget = self.budgets.get(budget_id)
        if not budget:
            return {}
            
        spend_percent = (budget.current_spend / budget.amount) * 100 if budget.amount > 0 else 0
        remaining = budget.amount - budget.current_spend
        
        return {
            "budget_id": budget_id,
            "name": budget.name,
            "amount": budget.amount,
            "current_spend": budget.current_spend,
            "remaining": remaining,
            "spend_percent": spend_percent,
            "status": "over_budget" if spend_percent > 100 else "on_track"
        }


class CostOptimizer:
    """Оптимизатор затрат"""
    
    def __init__(self):
        self.recommendations: List[OptimizationRecommendation] = []
        
    def analyze(self, cost_records: List[CostRecord]) -> List[OptimizationRecommendation]:
        """Анализ и генерация рекомендаций"""
        recommendations = []
        
        # Group by resource
        by_resource = defaultdict(list)
        for record in cost_records:
            by_resource[record.resource_id].append(record)
            
        for resource_id, records in by_resource.items():
            total_cost = sum(r.amount for r in records)
            resource_type = records[0].resource_type if records else ResourceType.VM
            
            # Check for rightsizing opportunities
            if resource_type in [ResourceType.VM, ResourceType.CONTAINER]:
                if random.random() > 0.6:  # 40% chance of recommendation
                    rec = OptimizationRecommendation(
                        recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
                        optimization_type=OptimizationType.RIGHTSIZING,
                        resource_id=resource_id,
                        resource_name=records[0].resource_name,
                        estimated_savings_monthly=total_cost * random.uniform(0.1, 0.3),
                        current_state={"size": "large", "cpu_util": random.uniform(10, 40)},
                        recommended_state={"size": "medium", "expected_cpu_util": random.uniform(50, 70)},
                        confidence_score=random.uniform(0.7, 0.95)
                    )
                    rec.estimated_savings_yearly = rec.estimated_savings_monthly * 12
                    recommendations.append(rec)
                    
            # Check for unused resources
            if total_cost > 0 and random.random() > 0.8:
                rec = OptimizationRecommendation(
                    recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
                    optimization_type=OptimizationType.UNUSED_RESOURCES,
                    resource_id=resource_id,
                    resource_name=records[0].resource_name,
                    estimated_savings_monthly=total_cost,
                    current_state={"status": "running", "last_access": "30+ days ago"},
                    recommended_state={"status": "terminated"},
                    confidence_score=random.uniform(0.8, 0.98)
                )
                rec.estimated_savings_yearly = rec.estimated_savings_monthly * 12
                recommendations.append(rec)
                
        # Reserved instances recommendation
        if len(cost_records) > 10:
            total_compute = sum(r.amount for r in cost_records 
                               if r.category == CostCategory.COMPUTE)
            if total_compute > 1000:
                rec = OptimizationRecommendation(
                    recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
                    optimization_type=OptimizationType.RESERVED_INSTANCES,
                    resource_id="compute_cluster",
                    resource_name="Production Compute",
                    estimated_savings_monthly=total_compute * 0.35,
                    current_state={"pricing": "on_demand"},
                    recommended_state={"pricing": "1_year_reserved", "commitment": total_compute * 0.8},
                    confidence_score=0.9
                )
                rec.estimated_savings_yearly = rec.estimated_savings_monthly * 12
                recommendations.append(rec)
                
        self.recommendations.extend(recommendations)
        return recommendations
        
    def get_total_savings_potential(self) -> Dict[str, float]:
        """Потенциал экономии"""
        pending = [r for r in self.recommendations if r.status == "pending"]
        
        return {
            "monthly": sum(r.estimated_savings_monthly for r in pending),
            "yearly": sum(r.estimated_savings_yearly for r in pending),
            "recommendations_count": len(pending)
        }


class AnomalyDetector:
    """Детектор аномалий"""
    
    def __init__(self):
        self.anomalies: List[CostAnomaly] = []
        self.baselines: Dict[str, float] = {}
        
    def set_baseline(self, resource_id: str, baseline_cost: float) -> None:
        """Установка базовой линии"""
        self.baselines[resource_id] = baseline_cost
        
    def detect(self, cost_records: List[CostRecord],
                threshold_percent: float = 50) -> List[CostAnomaly]:
        """Обнаружение аномалий"""
        detected = []
        
        # Group by resource
        by_resource = defaultdict(float)
        for record in cost_records:
            by_resource[record.resource_id] += record.amount
            
        for resource_id, actual_cost in by_resource.items():
            expected = self.baselines.get(resource_id, actual_cost)
            
            if expected > 0:
                deviation = ((actual_cost - expected) / expected) * 100
                
                if abs(deviation) > threshold_percent:
                    anomaly = CostAnomaly(
                        anomaly_id=f"anomaly_{uuid.uuid4().hex[:8]}",
                        resource_id=resource_id,
                        expected_cost=expected,
                        actual_cost=actual_cost,
                        deviation_percent=deviation,
                        root_cause=self._determine_root_cause(deviation)
                    )
                    detected.append(anomaly)
                    self.anomalies.append(anomaly)
                    
        return detected
        
    def _determine_root_cause(self, deviation: float) -> str:
        """Определение причины"""
        causes = [
            "Unusual traffic spike",
            "New resource provisioned",
            "Configuration change",
            "Pricing tier change",
            "Unoptimized query",
            "Data transfer increase"
        ]
        return random.choice(causes)


class CostForecaster:
    """Прогнозировщик затрат"""
    
    def forecast(self, historical_costs: List[float],
                  periods_ahead: int = 3) -> CostForecast:
        """Прогнозирование"""
        if not historical_costs:
            return CostForecast(
                forecast_id=f"forecast_{uuid.uuid4().hex[:8]}"
            )
            
        # Simple moving average forecast
        avg = sum(historical_costs) / len(historical_costs)
        std = math.sqrt(sum((x - avg) ** 2 for x in historical_costs) / len(historical_costs))
        
        # Trend (simple linear)
        if len(historical_costs) >= 2:
            trend = (historical_costs[-1] - historical_costs[0]) / len(historical_costs)
        else:
            trend = 0
            
        forecasted = avg + (trend * periods_ahead)
        
        forecast = CostForecast(
            forecast_id=f"forecast_{uuid.uuid4().hex[:8]}",
            period_start=datetime.now(),
            period_end=datetime.now() + timedelta(days=30 * periods_ahead),
            forecasted_amount=max(0, forecasted),
            lower_bound=max(0, forecasted - 2 * std),
            upper_bound=forecasted + 2 * std
        )
        
        return forecast


class CostManagementPlatform:
    """Платформа управления затратами"""
    
    def __init__(self):
        self.cost_tracker = CostTracker()
        self.budget_manager = BudgetManager()
        self.optimizer = CostOptimizer()
        self.anomaly_detector = AnomalyDetector()
        self.forecaster = CostForecaster()
        
    def record_cost(self, **kwargs) -> CostRecord:
        """Запись затрат"""
        return self.cost_tracker.record_cost(**kwargs)
        
    def create_budget(self, **kwargs) -> Budget:
        """Создание бюджета"""
        return self.budget_manager.create_budget(**kwargs)
        
    def get_cost_summary(self, start_date: datetime = None,
                          end_date: datetime = None) -> Dict[str, Any]:
        """Сводка по затратам"""
        total = self.cost_tracker.get_total_cost(
            start_date=start_date, end_date=end_date
        )
        by_category = self.cost_tracker.get_cost_by_category(
            start_date=start_date, end_date=end_date
        )
        by_project = self.cost_tracker.get_cost_by_project(
            start_date=start_date, end_date=end_date
        )
        
        return {
            "total_cost": total,
            "by_category": by_category,
            "by_project": by_project,
            "record_count": len(self.cost_tracker.get_costs(
                start_date=start_date, end_date=end_date
            ))
        }
        
    def analyze_and_optimize(self) -> Dict[str, Any]:
        """Анализ и оптимизация"""
        recommendations = self.optimizer.analyze(self.cost_tracker.records)
        savings = self.optimizer.get_total_savings_potential()
        
        return {
            "new_recommendations": len(recommendations),
            "total_recommendations": len(self.optimizer.recommendations),
            "potential_savings": savings
        }
        
    def detect_anomalies(self, threshold: float = 50) -> List[CostAnomaly]:
        """Обнаружение аномалий"""
        return self.anomaly_detector.detect(
            self.cost_tracker.records,
            threshold
        )
        
    def forecast_costs(self, periods: int = 3) -> CostForecast:
        """Прогноз затрат"""
        # Get monthly totals
        monthly_costs = []
        for i in range(6):
            month_start = datetime.now() - timedelta(days=30 * (i + 1))
            month_end = datetime.now() - timedelta(days=30 * i)
            total = self.cost_tracker.get_total_cost(
                start_date=month_start, end_date=month_end
            )
            if total > 0:
                monthly_costs.append(total)
                
        return self.forecaster.forecast(monthly_costs, periods)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        return {
            "total_records": len(self.cost_tracker.records),
            "total_cost": self.cost_tracker.get_total_cost(),
            "budgets": len(self.budget_manager.budgets),
            "budget_alerts": len(self.budget_manager.alerts),
            "recommendations": len(self.optimizer.recommendations),
            "anomalies": len(self.anomaly_detector.anomalies)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 103: Cost Management Platform")
    print("=" * 60)
    
    async def demo():
        platform = CostManagementPlatform()
        print("✓ Cost Management Platform created")
        
        # Record costs
        print("\n💰 Recording Costs...")
        
        # Generate sample cost data
        projects = ["platform", "e-commerce", "analytics", "mobile-app"]
        teams = ["platform-team", "dev-team", "data-team", "mobile-team"]
        resources = [
            ("vm-web-1", ResourceType.VM, CostCategory.COMPUTE),
            ("vm-web-2", ResourceType.VM, CostCategory.COMPUTE),
            ("vm-api-1", ResourceType.VM, CostCategory.COMPUTE),
            ("db-primary", ResourceType.DATABASE_INSTANCE, CostCategory.DATABASE),
            ("db-replica", ResourceType.DATABASE_INSTANCE, CostCategory.DATABASE),
            ("s3-data", ResourceType.STORAGE_OBJECT, CostCategory.STORAGE),
            ("s3-backups", ResourceType.STORAGE_OBJECT, CostCategory.STORAGE),
            ("lb-main", ResourceType.LOAD_BALANCER, CostCategory.NETWORK),
            ("k8s-cluster", ResourceType.CONTAINER, CostCategory.KUBERNETES),
            ("lambda-funcs", ResourceType.FUNCTION, CostCategory.SERVERLESS)
        ]
        
        for resource_name, resource_type, category in resources:
            cost = random.uniform(50, 500)
            platform.record_cost(
                resource_id=resource_name,
                amount=cost,
                category=category,
                resource_name=resource_name,
                resource_type=resource_type,
                project=random.choice(projects),
                team=random.choice(teams),
                environment="production",
                tags={"managed_by": "terraform", "cost_center": "engineering"}
            )
            
        # Add more historical data
        for _ in range(100):
            resource = random.choice(resources)
            platform.record_cost(
                resource_id=resource[0],
                amount=random.uniform(10, 300),
                category=resource[2],
                resource_name=resource[0],
                resource_type=resource[1],
                project=random.choice(projects),
                team=random.choice(teams),
                environment=random.choice(["production", "staging", "development"])
            )
            
        print(f"  ✓ Recorded {len(platform.cost_tracker.records)} cost entries")
        
        # Cost summary
        print("\n📊 Cost Summary:")
        
        summary = platform.get_cost_summary()
        
        print(f"\n  Total Cost: ${summary['total_cost']:.2f}")
        print(f"  Records: {summary['record_count']}")
        
        print("\n  By Category:")
        for category, cost in sorted(summary['by_category'].items(), key=lambda x: -x[1]):
            bar = "█" * int(cost / summary['total_cost'] * 20)
            print(f"    {category:<15} ${cost:>10.2f} {bar}")
            
        print("\n  By Project:")
        for project, cost in sorted(summary['by_project'].items(), key=lambda x: -x[1]):
            pct = cost / summary['total_cost'] * 100
            print(f"    {project:<15} ${cost:>10.2f} ({pct:.1f}%)")
            
        # Create budgets
        print("\n💼 Creating Budgets...")
        
        budget1 = platform.create_budget(
            "Platform Infrastructure",
            amount=5000,
            period=BudgetPeriod.MONTHLY,
            project="platform",
            alert_thresholds=[50, 80, 90, 100]
        )
        print(f"  ✓ {budget1.name}: ${budget1.amount}/month")
        
        budget2 = platform.create_budget(
            "E-commerce Resources",
            amount=3000,
            period=BudgetPeriod.MONTHLY,
            project="e-commerce"
        )
        print(f"  ✓ {budget2.name}: ${budget2.amount}/month")
        
        budget3 = platform.create_budget(
            "Data Team Budget",
            amount=4000,
            period=BudgetPeriod.MONTHLY,
            team="data-team"
        )
        print(f"  ✓ {budget3.name}: ${budget3.amount}/month")
        
        # Update budget spend
        print("\n  Updating Budget Spend:")
        
        project_costs = summary['by_project']
        
        alerts = platform.budget_manager.update_spend(
            budget1.budget_id,
            project_costs.get("platform", 0)
        )
        for alert in alerts:
            print(f"    ⚠️ Alert: {alert['budget_name']} at {alert['spend_percent']:.1f}%")
            
        alerts = platform.budget_manager.update_spend(
            budget2.budget_id,
            project_costs.get("e-commerce", 0) * 1.5  # Simulate over budget
        )
        for alert in alerts:
            print(f"    ⚠️ Alert: {alert['budget_name']} at {alert['spend_percent']:.1f}%")
            
        # Budget status
        print("\n  Budget Status:")
        
        for budget_id in [budget1.budget_id, budget2.budget_id, budget3.budget_id]:
            status = platform.budget_manager.get_budget_status(budget_id)
            status_icon = "✅" if status['status'] == "on_track" else "🔴"
            print(f"    {status_icon} {status['name']}: ${status['current_spend']:.2f}/${status['amount']:.2f} ({status['spend_percent']:.1f}%)")
            
        # Set baselines for anomaly detection
        print("\n🔍 Setting up Anomaly Detection...")
        
        for resource in resources:
            platform.anomaly_detector.set_baseline(
                resource[0],
                random.uniform(100, 300)
            )
            
        # Detect anomalies
        anomalies = platform.detect_anomalies(threshold=50)
        
        print(f"  Detected {len(anomalies)} anomalies:")
        for anomaly in anomalies[:5]:
            deviation_icon = "📈" if anomaly.deviation_percent > 0 else "📉"
            print(f"    {deviation_icon} {anomaly.resource_id}: {anomaly.deviation_percent:+.1f}%")
            print(f"       Expected: ${anomaly.expected_cost:.2f}, Actual: ${anomaly.actual_cost:.2f}")
            print(f"       Cause: {anomaly.root_cause}")
            
        # Optimization recommendations
        print("\n💡 Analyzing for Optimization...")
        
        analysis = platform.analyze_and_optimize()
        
        print(f"\n  New Recommendations: {analysis['new_recommendations']}")
        print(f"  Potential Monthly Savings: ${analysis['potential_savings']['monthly']:.2f}")
        print(f"  Potential Yearly Savings: ${analysis['potential_savings']['yearly']:.2f}")
        
        print("\n  Top Recommendations:")
        sorted_recs = sorted(
            platform.optimizer.recommendations,
            key=lambda r: r.estimated_savings_monthly,
            reverse=True
        )
        
        for rec in sorted_recs[:5]:
            print(f"\n    [{rec.optimization_type.value}] {rec.resource_name}")
            print(f"      Savings: ${rec.estimated_savings_monthly:.2f}/month (${rec.estimated_savings_yearly:.2f}/year)")
            print(f"      Confidence: {rec.confidence_score*100:.0f}%")
            print(f"      Current: {rec.current_state}")
            print(f"      Recommended: {rec.recommended_state}")
            
        # Forecasting
        print("\n📈 Cost Forecasting...")
        
        forecast = platform.forecast_costs(periods=3)
        
        print(f"\n  3-Month Forecast:")
        print(f"    Predicted: ${forecast.forecasted_amount:.2f}")
        print(f"    Range: ${forecast.lower_bound:.2f} - ${forecast.upper_bound:.2f}")
        
        # Statistics
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Cost Records: {stats['total_records']}")
        print(f"  Total Cost: ${stats['total_cost']:.2f}")
        print(f"  Budgets: {stats['budgets']}")
        print(f"  Budget Alerts: {stats['budget_alerts']}")
        print(f"  Recommendations: {stats['recommendations']}")
        print(f"  Anomalies: {stats['anomalies']}")
        
        # Dashboard
        print("\n📋 Cost Management Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │              Cost Management Overview                       │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Cost:      ${stats['total_cost']:>10.2f}                        │")
        print(f"  │ Cost Records:    {stats['total_records']:>10}                        │")
        print(f"  │ Budgets:         {stats['budgets']:>10}                        │")
        print(f"  │ Budget Alerts:   {stats['budget_alerts']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        savings = analysis['potential_savings']['monthly']
        print(f"  │ Recommendations: {stats['recommendations']:>10}                        │")
        print(f"  │ Potential Save:  ${savings:>10.2f}/mo                     │")
        print(f"  │ Anomalies:       {stats['anomalies']:>10}                        │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Cost Management Platform initialized!")
    print("=" * 60)
