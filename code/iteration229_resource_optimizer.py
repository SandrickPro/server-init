#!/usr/bin/env python3
"""
Server Init - Iteration 229: Resource Optimizer Platform
Платформа оптимизации ресурсов

Функционал:
- Resource Analysis - анализ ресурсов
- Cost Optimization - оптимизация затрат
- Right-Sizing - правильный размер
- Idle Detection - обнаружение простоя
- Recommendation Engine - движок рекомендаций
- Budget Management - управление бюджетом
- Scheduling Optimization - оптимизация расписания
- Savings Tracking - отслеживание экономии
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class ResourceType(Enum):
    """Тип ресурса"""
    COMPUTE = "compute"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    CONTAINER = "container"


class RecommendationType(Enum):
    """Тип рекомендации"""
    DOWNSIZE = "downsize"
    UPSIZE = "upsize"
    TERMINATE = "terminate"
    RESERVED = "reserved"
    SPOT = "spot"
    SCHEDULE = "schedule"


class Severity(Enum):
    """Серьёзность"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResourceStatus(Enum):
    """Статус ресурса"""
    ACTIVE = "active"
    IDLE = "idle"
    UNDERUTILIZED = "underutilized"
    OVERUTILIZED = "overutilized"


@dataclass
class Resource:
    """Ресурс"""
    resource_id: str
    name: str = ""
    resource_type: ResourceType = ResourceType.COMPUTE
    
    # Provider info
    provider: str = ""  # aws, gcp, azure
    region: str = ""
    instance_type: str = ""
    
    # Specs
    cpu_cores: int = 0
    memory_gb: float = 0
    storage_gb: float = 0
    
    # Utilization
    cpu_avg_percent: float = 0
    memory_avg_percent: float = 0
    
    # Cost
    hourly_cost: float = 0
    monthly_cost: float = 0
    
    # Status
    status: ResourceStatus = ResourceStatus.ACTIVE
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Times
    created_at: datetime = field(default_factory=datetime.now)
    last_analyzed: Optional[datetime] = None


@dataclass
class Recommendation:
    """Рекомендация"""
    rec_id: str
    resource_id: str = ""
    
    # Type
    rec_type: RecommendationType = RecommendationType.DOWNSIZE
    severity: Severity = Severity.MEDIUM
    
    # Current vs recommended
    current_config: Dict[str, Any] = field(default_factory=dict)
    recommended_config: Dict[str, Any] = field(default_factory=dict)
    
    # Savings
    monthly_savings: float = 0
    savings_percent: float = 0
    
    # Justification
    reason: str = ""
    confidence: float = 0.8
    
    # Status
    is_applied: bool = False
    applied_at: Optional[datetime] = None
    
    # Created
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Budget:
    """Бюджет"""
    budget_id: str
    name: str = ""
    
    # Limits
    monthly_limit: float = 0
    current_spend: float = 0
    forecasted_spend: float = 0
    
    # Alerts
    alert_threshold_percent: float = 80
    is_alert_triggered: bool = False
    
    # Scope
    tags_filter: Dict[str, str] = field(default_factory=dict)
    
    # Period
    start_date: datetime = field(default_factory=datetime.now)
    end_date: datetime = field(default_factory=datetime.now)


@dataclass
class SavingsReport:
    """Отчёт об экономии"""
    report_id: str
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Savings
    total_savings: float = 0
    savings_by_type: Dict[str, float] = field(default_factory=dict)
    
    # Recommendations
    recommendations_applied: int = 0
    recommendations_pending: int = 0
    
    # Resources optimized
    resources_optimized: int = 0


class ResourceAnalyzer:
    """Анализатор ресурсов"""
    
    def __init__(self):
        self.thresholds = {
            "idle_cpu": 5,       # <5% = idle
            "low_cpu": 20,      # <20% = underutilized
            "high_cpu": 80,     # >80% = overutilized
            "idle_memory": 10,
            "low_memory": 30,
            "high_memory": 85
        }
        
    def analyze(self, resource: Resource) -> ResourceStatus:
        """Анализ ресурса"""
        if resource.cpu_avg_percent < self.thresholds["idle_cpu"] and \
           resource.memory_avg_percent < self.thresholds["idle_memory"]:
            return ResourceStatus.IDLE
            
        if resource.cpu_avg_percent < self.thresholds["low_cpu"] or \
           resource.memory_avg_percent < self.thresholds["low_memory"]:
            return ResourceStatus.UNDERUTILIZED
            
        if resource.cpu_avg_percent > self.thresholds["high_cpu"] or \
           resource.memory_avg_percent > self.thresholds["high_memory"]:
            return ResourceStatus.OVERUTILIZED
            
        return ResourceStatus.ACTIVE


class RecommendationEngine:
    """Движок рекомендаций"""
    
    def __init__(self):
        self.instance_types = {
            "small": {"cpu": 2, "memory": 4, "cost": 0.05},
            "medium": {"cpu": 4, "memory": 8, "cost": 0.10},
            "large": {"cpu": 8, "memory": 16, "cost": 0.20},
            "xlarge": {"cpu": 16, "memory": 32, "cost": 0.40}
        }
        
    def generate(self, resource: Resource) -> Optional[Recommendation]:
        """Генерация рекомендации"""
        if resource.status == ResourceStatus.IDLE:
            return self._recommend_terminate(resource)
        elif resource.status == ResourceStatus.UNDERUTILIZED:
            return self._recommend_downsize(resource)
        elif resource.status == ResourceStatus.OVERUTILIZED:
            return self._recommend_upsize(resource)
        return None
        
    def _recommend_terminate(self, resource: Resource) -> Recommendation:
        """Рекомендация на удаление"""
        return Recommendation(
            rec_id=f"rec_{uuid.uuid4().hex[:8]}",
            resource_id=resource.resource_id,
            rec_type=RecommendationType.TERMINATE,
            severity=Severity.HIGH,
            current_config={"instance_type": resource.instance_type},
            recommended_config={"action": "terminate"},
            monthly_savings=resource.monthly_cost,
            savings_percent=100,
            reason=f"Resource idle (CPU: {resource.cpu_avg_percent:.1f}%, Memory: {resource.memory_avg_percent:.1f}%)",
            confidence=0.95
        )
        
    def _recommend_downsize(self, resource: Resource) -> Recommendation:
        """Рекомендация на уменьшение"""
        # Find smaller instance
        smaller_cost = resource.hourly_cost * 0.5
        savings = resource.monthly_cost * 0.5
        
        return Recommendation(
            rec_id=f"rec_{uuid.uuid4().hex[:8]}",
            resource_id=resource.resource_id,
            rec_type=RecommendationType.DOWNSIZE,
            severity=Severity.MEDIUM,
            current_config={
                "instance_type": resource.instance_type,
                "cpu": resource.cpu_cores,
                "memory": resource.memory_gb
            },
            recommended_config={
                "cpu": resource.cpu_cores // 2,
                "memory": resource.memory_gb / 2
            },
            monthly_savings=savings,
            savings_percent=50,
            reason=f"Resource underutilized (CPU: {resource.cpu_avg_percent:.1f}%, Memory: {resource.memory_avg_percent:.1f}%)",
            confidence=0.85
        )
        
    def _recommend_upsize(self, resource: Resource) -> Recommendation:
        """Рекомендация на увеличение"""
        return Recommendation(
            rec_id=f"rec_{uuid.uuid4().hex[:8]}",
            resource_id=resource.resource_id,
            rec_type=RecommendationType.UPSIZE,
            severity=Severity.HIGH,
            current_config={
                "instance_type": resource.instance_type,
                "cpu": resource.cpu_cores,
                "memory": resource.memory_gb
            },
            recommended_config={
                "cpu": resource.cpu_cores * 2,
                "memory": resource.memory_gb * 2
            },
            monthly_savings=-resource.monthly_cost,  # Negative = increase
            savings_percent=0,
            reason=f"Resource overutilized (CPU: {resource.cpu_avg_percent:.1f}%, Memory: {resource.memory_avg_percent:.1f}%)",
            confidence=0.90
        )


class ResourceOptimizerPlatform:
    """Платформа оптимизации ресурсов"""
    
    def __init__(self):
        self.resources: Dict[str, Resource] = {}
        self.recommendations: Dict[str, Recommendation] = {}
        self.budgets: Dict[str, Budget] = {}
        self.savings_reports: List[SavingsReport] = []
        self.analyzer = ResourceAnalyzer()
        self.engine = RecommendationEngine()
        
    def add_resource(self, name: str, resource_type: ResourceType,
                    provider: str, region: str, instance_type: str,
                    cpu: int, memory: float, hourly_cost: float) -> Resource:
        """Добавление ресурса"""
        resource = Resource(
            resource_id=f"res_{uuid.uuid4().hex[:8]}",
            name=name,
            resource_type=resource_type,
            provider=provider,
            region=region,
            instance_type=instance_type,
            cpu_cores=cpu,
            memory_gb=memory,
            hourly_cost=hourly_cost,
            monthly_cost=hourly_cost * 720  # ~30 days
        )
        self.resources[resource.resource_id] = resource
        return resource
        
    def set_utilization(self, resource_id: str, cpu_pct: float, memory_pct: float):
        """Установка утилизации"""
        resource = self.resources.get(resource_id)
        if resource:
            resource.cpu_avg_percent = cpu_pct
            resource.memory_avg_percent = memory_pct
            
    def analyze_resource(self, resource_id: str) -> Optional[ResourceStatus]:
        """Анализ ресурса"""
        resource = self.resources.get(resource_id)
        if not resource:
            return None
            
        status = self.analyzer.analyze(resource)
        resource.status = status
        resource.last_analyzed = datetime.now()
        return status
        
    def generate_recommendation(self, resource_id: str) -> Optional[Recommendation]:
        """Генерация рекомендации"""
        resource = self.resources.get(resource_id)
        if not resource:
            return None
            
        rec = self.engine.generate(resource)
        if rec:
            self.recommendations[rec.rec_id] = rec
        return rec
        
    def analyze_all(self) -> List[Recommendation]:
        """Анализ всех ресурсов"""
        recs = []
        for resource_id in self.resources:
            self.analyze_resource(resource_id)
            rec = self.generate_recommendation(resource_id)
            if rec:
                recs.append(rec)
        return recs
        
    def apply_recommendation(self, rec_id: str) -> bool:
        """Применение рекомендации"""
        rec = self.recommendations.get(rec_id)
        if not rec:
            return False
            
        rec.is_applied = True
        rec.applied_at = datetime.now()
        return True
        
    def create_budget(self, name: str, monthly_limit: float,
                     alert_threshold: float = 80) -> Budget:
        """Создание бюджета"""
        budget = Budget(
            budget_id=f"bud_{uuid.uuid4().hex[:8]}",
            name=name,
            monthly_limit=monthly_limit,
            alert_threshold_percent=alert_threshold,
            end_date=datetime.now() + timedelta(days=30)
        )
        self.budgets[budget.budget_id] = budget
        return budget
        
    def update_budget_spend(self, budget_id: str):
        """Обновление траты бюджета"""
        budget = self.budgets.get(budget_id)
        if not budget:
            return
            
        total_spend = sum(r.monthly_cost for r in self.resources.values())
        budget.current_spend = total_spend
        budget.forecasted_spend = total_spend * 1.1  # +10% forecast
        
        if (budget.current_spend / budget.monthly_limit * 100) >= budget.alert_threshold_percent:
            budget.is_alert_triggered = True
            
    def generate_savings_report(self) -> SavingsReport:
        """Генерация отчёта об экономии"""
        applied = [r for r in self.recommendations.values() if r.is_applied]
        pending = [r for r in self.recommendations.values() if not r.is_applied]
        
        total_savings = sum(r.monthly_savings for r in applied if r.monthly_savings > 0)
        
        by_type = {}
        for r in applied:
            if r.monthly_savings > 0:
                t = r.rec_type.value
                if t not in by_type:
                    by_type[t] = 0
                by_type[t] += r.monthly_savings
                
        report = SavingsReport(
            report_id=f"rep_{uuid.uuid4().hex[:8]}",
            period_start=datetime.now() - timedelta(days=30),
            period_end=datetime.now(),
            total_savings=total_savings,
            savings_by_type=by_type,
            recommendations_applied=len(applied),
            recommendations_pending=len(pending),
            resources_optimized=len(set(r.resource_id for r in applied))
        )
        
        self.savings_reports.append(report)
        return report
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        resources = list(self.resources.values())
        recs = list(self.recommendations.values())
        
        by_status = {}
        for r in resources:
            s = r.status.value
            if s not in by_status:
                by_status[s] = 0
            by_status[s] += 1
            
        total_cost = sum(r.monthly_cost for r in resources)
        potential_savings = sum(r.monthly_savings for r in recs 
                               if not r.is_applied and r.monthly_savings > 0)
        
        return {
            "total_resources": len(resources),
            "by_status": by_status,
            "total_monthly_cost": total_cost,
            "potential_savings": potential_savings,
            "recommendations": len(recs),
            "recommendations_applied": len([r for r in recs if r.is_applied]),
            "budgets": len(self.budgets)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 229: Resource Optimizer Platform")
    print("=" * 60)
    
    platform = ResourceOptimizerPlatform()
    print("✓ Resource Optimizer Platform created")
    
    # Add resources
    print("\n💻 Adding Resources...")
    
    resources_config = [
        ("prod-api-1", ResourceType.COMPUTE, "aws", "us-east-1", "m5.xlarge", 4, 16, 0.192),
        ("prod-api-2", ResourceType.COMPUTE, "aws", "us-east-1", "m5.xlarge", 4, 16, 0.192),
        ("dev-server-1", ResourceType.COMPUTE, "aws", "us-west-2", "m5.large", 2, 8, 0.096),
        ("staging-db", ResourceType.DATABASE, "aws", "us-east-1", "db.r5.large", 2, 16, 0.24),
        ("analytics-node", ResourceType.COMPUTE, "gcp", "us-central1", "n1-standard-8", 8, 30, 0.38),
        ("cache-cluster", ResourceType.MEMORY, "aws", "us-east-1", "cache.r5.large", 2, 13, 0.166),
        ("test-env-1", ResourceType.COMPUTE, "aws", "us-west-2", "t3.medium", 2, 4, 0.0416),
        ("test-env-2", ResourceType.COMPUTE, "aws", "us-west-2", "t3.medium", 2, 4, 0.0416),
    ]
    
    resources = []
    for name, rtype, provider, region, instance, cpu, memory, cost in resources_config:
        resource = platform.add_resource(name, rtype, provider, region, instance, cpu, memory, cost)
        resources.append(resource)
        
        type_icons = {
            ResourceType.COMPUTE: "💻",
            ResourceType.MEMORY: "🧠",
            ResourceType.STORAGE: "💾",
            ResourceType.DATABASE: "🗄️",
            ResourceType.NETWORK: "🌐",
            ResourceType.CONTAINER: "📦"
        }
        print(f"  {type_icons[rtype]} {name}: {instance} (${cost:.3f}/hr)")
        
    # Set utilization
    print("\n📊 Setting Utilization Metrics...")
    
    utilizations = [
        (75, 60),   # prod-api-1: normal
        (85, 78),   # prod-api-2: high
        (8, 15),    # dev-server-1: underutilized
        (45, 55),   # staging-db: normal
        (92, 88),   # analytics-node: overutilized
        (35, 42),   # cache-cluster: normal
        (2, 5),     # test-env-1: idle
        (3, 8),     # test-env-2: idle
    ]
    
    for i, resource in enumerate(resources):
        cpu, mem = utilizations[i]
        platform.set_utilization(resource.resource_id, cpu, mem)
        
    print(f"  ✓ Set utilization for {len(resources)} resources")
    
    # Analyze resources
    print("\n🔍 Analyzing Resources...")
    
    recommendations = platform.analyze_all()
    
    status_icons = {
        ResourceStatus.ACTIVE: "🟢",
        ResourceStatus.IDLE: "⚫",
        ResourceStatus.UNDERUTILIZED: "🟡",
        ResourceStatus.OVERUTILIZED: "🔴"
    }
    
    for resource in resources:
        icon = status_icons.get(resource.status, "⚪")
        cpu = f"{resource.cpu_avg_percent:.0f}%"
        mem = f"{resource.memory_avg_percent:.0f}%"
        print(f"  {icon} {resource.name}: CPU {cpu}, Mem {mem} - {resource.status.value}")
        
    # Display recommendations
    print("\n💡 Recommendations Generated:")
    
    rec_icons = {
        RecommendationType.TERMINATE: "🗑️",
        RecommendationType.DOWNSIZE: "⬇️",
        RecommendationType.UPSIZE: "⬆️",
        RecommendationType.RESERVED: "📋",
        RecommendationType.SPOT: "💰",
        RecommendationType.SCHEDULE: "⏰"
    }
    
    for rec in recommendations:
        resource = platform.resources.get(rec.resource_id)
        name = resource.name if resource else "unknown"
        icon = rec_icons.get(rec.rec_type, "❓")
        savings = f"${rec.monthly_savings:.2f}/mo" if rec.monthly_savings > 0 else "cost increase"
        print(f"  {icon} {name}: {rec.rec_type.value} - {savings}")
        print(f"     Reason: {rec.reason[:60]}...")
        
    # Apply some recommendations
    print("\n✅ Applying Recommendations...")
    
    for rec in recommendations[:4]:
        platform.apply_recommendation(rec.rec_id)
        resource = platform.resources.get(rec.resource_id)
        name = resource.name if resource else "unknown"
        print(f"  ✓ Applied: {name} - {rec.rec_type.value}")
        
    # Create budgets
    print("\n💰 Creating Budgets...")
    
    budgets = [
        platform.create_budget("Production Budget", 5000, 80),
        platform.create_budget("Development Budget", 1000, 90),
        platform.create_budget("Total Cloud Budget", 8000, 75),
    ]
    
    for budget in budgets:
        platform.update_budget_spend(budget.budget_id)
        status = "⚠️" if budget.is_alert_triggered else "✓"
        pct = (budget.current_spend / budget.monthly_limit * 100)
        print(f"  {status} {budget.name}: ${budget.current_spend:.2f} / ${budget.monthly_limit:.2f} ({pct:.0f}%)")
        
    # Generate savings report
    print("\n📈 Generating Savings Report...")
    
    report = platform.generate_savings_report()
    print(f"  Total Savings: ${report.total_savings:.2f}")
    print(f"  Recommendations Applied: {report.recommendations_applied}")
    print(f"  Resources Optimized: {report.resources_optimized}")
    
    # Display resource table
    print("\n📋 Resource Overview:")
    
    print("\n  ┌────────────────────┬────────────┬──────────┬────────────┬──────────┐")
    print("  │ Resource           │ Type       │ Status   │ CPU Usage  │ Cost/Mo  │")
    print("  ├────────────────────┼────────────┼──────────┼────────────┼──────────┤")
    
    for resource in platform.resources.values():
        name = resource.name[:18].ljust(18)
        rtype = resource.resource_type.value[:10].ljust(10)
        
        status = f"{status_icons.get(resource.status, '⚪')}"[:8].ljust(8)
        cpu = f"{resource.cpu_avg_percent:.0f}%"[:10].ljust(10)
        cost = f"${resource.monthly_cost:.0f}"[:8].ljust(8)
        
        print(f"  │ {name} │ {rtype} │ {status} │ {cpu} │ {cost} │")
        
    print("  └────────────────────┴────────────┴──────────┴────────────┴──────────┘")
    
    # Resources by status
    print("\n📊 Resources by Status:")
    
    stats = platform.get_statistics()
    
    for status, count in stats["by_status"].items():
        icon = {
            "active": "🟢",
            "idle": "⚫",
            "underutilized": "🟡",
            "overutilized": "🔴"
        }.get(status, "⚪")
        bar = "█" * count + "░" * (5 - count)
        print(f"  {icon} {status:15s} [{bar}] {count}")
        
    # Cost breakdown
    print("\n💵 Cost Analysis:")
    
    print(f"  Total Monthly Cost: ${stats['total_monthly_cost']:.2f}")
    print(f"  Potential Savings:  ${stats['potential_savings']:.2f}")
    
    savings_pct = (stats['potential_savings'] / stats['total_monthly_cost'] * 100) if stats['total_monthly_cost'] > 0 else 0
    print(f"  Savings Potential:  {savings_pct:.1f}%")
    
    # Top savings opportunities
    print("\n🎯 Top Savings Opportunities:")
    
    pending_recs = [r for r in platform.recommendations.values() 
                   if not r.is_applied and r.monthly_savings > 0]
    pending_recs.sort(key=lambda x: x.monthly_savings, reverse=True)
    
    for i, rec in enumerate(pending_recs[:5], 1):
        resource = platform.resources.get(rec.resource_id)
        name = resource.name if resource else "unknown"
        print(f"  {i}. {name}: ${rec.monthly_savings:.2f}/mo ({rec.rec_type.value})")
        
    # Statistics
    print("\n📈 Platform Statistics:")
    
    print(f"\n  Resources: {stats['total_resources']}")
    print(f"  Recommendations: {stats['recommendations']}")
    print(f"  Applied: {stats['recommendations_applied']}")
    print(f"  Budgets: {stats['budgets']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Resource Optimizer Dashboard                     │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Resources:               {stats['total_resources']:>12}                        │")
    print(f"│ Monthly Cost:                  ${stats['total_monthly_cost']:>11.2f}                       │")
    print(f"│ Potential Savings:             ${stats['potential_savings']:>11.2f}                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Recommendations:               {stats['recommendations']:>12}                        │")
    print(f"│ Applied:                       {stats['recommendations_applied']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Resource Optimizer Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
