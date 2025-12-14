#!/usr/bin/env python3
"""
Server Init - Iteration 125: SLO Management Platform
Платформа управления SLO

Функционал:
- SLO Definition - определение SLO
- SLI Collection - сбор SLI
- Error Budget - бюджет ошибок
- Burn Rate Alerting - алертинг скорости сжигания
- SLO Reporting - отчётность SLO
- Multi-Window Alerts - многооконные алерты
- Service Dependencies - зависимости сервисов
- Compliance Tracking - отслеживание соответствия
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from collections import defaultdict
import uuid
import random
import math


class SLIType(Enum):
    """Тип SLI"""
    AVAILABILITY = "availability"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CORRECTNESS = "correctness"


class TimeWindow(Enum):
    """Временное окно"""
    ROLLING_1H = "1h"
    ROLLING_6H = "6h"
    ROLLING_1D = "1d"
    ROLLING_7D = "7d"
    ROLLING_30D = "30d"
    CALENDAR_MONTH = "calendar_month"


class AlertSeverity(Enum):
    """Критичность алерта"""
    PAGE = "page"
    TICKET = "ticket"
    LOG = "log"


@dataclass
class SLI:
    """Service Level Indicator"""
    sli_id: str
    name: str = ""
    
    # Type
    sli_type: SLIType = SLIType.AVAILABILITY
    
    # Query
    good_events_query: str = ""
    total_events_query: str = ""
    
    # Current values
    good_events: int = 0
    total_events: int = 0
    
    @property
    def value(self) -> float:
        """Текущее значение SLI"""
        if self.total_events == 0:
            return 100.0
        return (self.good_events / self.total_events) * 100


@dataclass
class SLO:
    """Service Level Objective"""
    slo_id: str
    name: str = ""
    description: str = ""
    
    # Service
    service_name: str = ""
    
    # SLI
    sli_id: str = ""
    
    # Target
    target_percent: float = 99.9
    
    # Window
    window: TimeWindow = TimeWindow.ROLLING_30D
    
    # Current status
    current_sli: float = 100.0
    
    # Error budget
    error_budget_remaining: float = 100.0
    error_budget_consumed: float = 0.0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    window_start: datetime = field(default_factory=datetime.now)


@dataclass
class ErrorBudget:
    """Бюджет ошибок"""
    budget_id: str
    slo_id: str = ""
    
    # Window
    window_start: datetime = field(default_factory=datetime.now)
    window_end: datetime = field(default_factory=datetime.now)
    
    # Budget
    total_budget_minutes: float = 0.0
    consumed_minutes: float = 0.0
    remaining_minutes: float = 0.0
    
    # Burn rate
    current_burn_rate: float = 1.0  # 1.0 = normal
    projected_exhaustion: Optional[datetime] = None


@dataclass
class BurnRateAlert:
    """Алерт скорости сжигания"""
    alert_id: str
    slo_id: str = ""
    
    # Windows
    short_window: str = "5m"
    long_window: str = "1h"
    
    # Thresholds
    burn_rate_threshold: float = 14.4  # For 30d window
    
    # Severity
    severity: AlertSeverity = AlertSeverity.PAGE
    
    # Status
    triggered: bool = False
    triggered_at: Optional[datetime] = None


@dataclass
class SLOReport:
    """Отчёт SLO"""
    report_id: str
    slo_id: str = ""
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Metrics
    average_sli: float = 0.0
    min_sli: float = 0.0
    max_sli: float = 0.0
    
    # Compliance
    target_met: bool = True
    time_in_compliance_percent: float = 100.0
    
    # Budget
    error_budget_consumed_percent: float = 0.0
    
    # Incidents
    incidents_count: int = 0


@dataclass
class SLIDatapoint:
    """Точка данных SLI"""
    timestamp: datetime
    good_events: int = 0
    total_events: int = 0
    sli_value: float = 100.0


class SLICollector:
    """Сборщик SLI"""
    
    def __init__(self):
        self.slis: Dict[str, SLI] = {}
        self.datapoints: Dict[str, List[SLIDatapoint]] = defaultdict(list)
        
    def create(self, name: str, sli_type: SLIType,
                good_query: str = "", total_query: str = "") -> SLI:
        """Создание SLI"""
        sli = SLI(
            sli_id=f"sli_{uuid.uuid4().hex[:8]}",
            name=name,
            sli_type=sli_type,
            good_events_query=good_query,
            total_events_query=total_query
        )
        self.slis[sli.sli_id] = sli
        return sli
        
    def collect(self, sli_id: str, good_events: int, total_events: int) -> SLIDatapoint:
        """Сбор данных SLI"""
        sli = self.slis.get(sli_id)
        if not sli:
            return None
            
        sli.good_events += good_events
        sli.total_events += total_events
        
        datapoint = SLIDatapoint(
            timestamp=datetime.now(),
            good_events=good_events,
            total_events=total_events,
            sli_value=sli.value
        )
        
        self.datapoints[sli_id].append(datapoint)
        
        # Keep only recent data
        if len(self.datapoints[sli_id]) > 43200:  # 30 days at 1-minute intervals
            self.datapoints[sli_id] = self.datapoints[sli_id][-21600:]
            
        return datapoint
        
    def get_history(self, sli_id: str, hours: int = 24) -> List[SLIDatapoint]:
        """История SLI"""
        threshold = datetime.now() - timedelta(hours=hours)
        return [dp for dp in self.datapoints.get(sli_id, []) if dp.timestamp >= threshold]


class SLOManager:
    """Менеджер SLO"""
    
    def __init__(self, sli_collector: SLICollector):
        self.sli_collector = sli_collector
        self.slos: Dict[str, SLO] = {}
        
    def create(self, name: str, service_name: str, sli_id: str,
                target_percent: float = 99.9,
                window: TimeWindow = TimeWindow.ROLLING_30D,
                **kwargs) -> SLO:
        """Создание SLO"""
        slo = SLO(
            slo_id=f"slo_{uuid.uuid4().hex[:8]}",
            name=name,
            service_name=service_name,
            sli_id=sli_id,
            target_percent=target_percent,
            window=window,
            **kwargs
        )
        self.slos[slo.slo_id] = slo
        return slo
        
    def update(self, slo_id: str) -> Dict[str, Any]:
        """Обновление статуса SLO"""
        slo = self.slos.get(slo_id)
        if not slo:
            return {"error": "SLO not found"}
            
        sli = self.sli_collector.slis.get(slo.sli_id)
        if not sli:
            return {"error": "SLI not found"}
            
        # Update current SLI
        slo.current_sli = sli.value
        
        # Calculate error budget
        allowed_errors = 100 - slo.target_percent
        actual_errors = 100 - slo.current_sli
        
        if allowed_errors > 0:
            slo.error_budget_consumed = (actual_errors / allowed_errors) * 100
            slo.error_budget_remaining = max(0, 100 - slo.error_budget_consumed)
        else:
            slo.error_budget_consumed = 100 if actual_errors > 0 else 0
            slo.error_budget_remaining = 100 - slo.error_budget_consumed
            
        return {
            "slo_id": slo_id,
            "current_sli": slo.current_sli,
            "target": slo.target_percent,
            "error_budget_remaining": slo.error_budget_remaining,
            "in_compliance": slo.current_sli >= slo.target_percent
        }
        
    def get_status(self, slo_id: str) -> Dict[str, Any]:
        """Получить статус SLO"""
        slo = self.slos.get(slo_id)
        if not slo:
            return {}
            
        return {
            "name": slo.name,
            "service": slo.service_name,
            "target": slo.target_percent,
            "current": slo.current_sli,
            "window": slo.window.value,
            "error_budget_remaining": slo.error_budget_remaining,
            "in_compliance": slo.current_sli >= slo.target_percent
        }


class ErrorBudgetTracker:
    """Трекер бюджета ошибок"""
    
    def __init__(self, slo_manager: SLOManager):
        self.slo_manager = slo_manager
        self.budgets: Dict[str, ErrorBudget] = {}
        
    def calculate(self, slo_id: str) -> ErrorBudget:
        """Расчёт бюджета ошибок"""
        slo = self.slo_manager.slos.get(slo_id)
        if not slo:
            return None
            
        # Get window duration
        window_minutes = {
            TimeWindow.ROLLING_1H: 60,
            TimeWindow.ROLLING_6H: 360,
            TimeWindow.ROLLING_1D: 1440,
            TimeWindow.ROLLING_7D: 10080,
            TimeWindow.ROLLING_30D: 43200,
            TimeWindow.CALENDAR_MONTH: 43200
        }.get(slo.window, 43200)
        
        # Calculate budget
        allowed_error_percent = 100 - slo.target_percent
        total_budget_minutes = window_minutes * (allowed_error_percent / 100)
        consumed_minutes = total_budget_minutes * (slo.error_budget_consumed / 100)
        remaining_minutes = total_budget_minutes - consumed_minutes
        
        budget = ErrorBudget(
            budget_id=f"budget_{uuid.uuid4().hex[:8]}",
            slo_id=slo_id,
            window_end=datetime.now() + timedelta(days=30),
            total_budget_minutes=total_budget_minutes,
            consumed_minutes=consumed_minutes,
            remaining_minutes=remaining_minutes
        )
        
        # Calculate burn rate
        if total_budget_minutes > 0:
            elapsed_fraction = 0.5  # Assume halfway through window
            expected_consumed = total_budget_minutes * elapsed_fraction
            if expected_consumed > 0:
                budget.current_burn_rate = consumed_minutes / expected_consumed
            else:
                budget.current_burn_rate = 1.0
                
        # Project exhaustion
        if budget.current_burn_rate > 1.0 and remaining_minutes > 0:
            days_until_exhaustion = remaining_minutes / (budget.current_burn_rate * (total_budget_minutes / 30))
            budget.projected_exhaustion = datetime.now() + timedelta(days=days_until_exhaustion)
            
        self.budgets[slo_id] = budget
        return budget


class BurnRateAlerter:
    """Алертер скорости сжигания"""
    
    def __init__(self, slo_manager: SLOManager, budget_tracker: ErrorBudgetTracker):
        self.slo_manager = slo_manager
        self.budget_tracker = budget_tracker
        self.alerts: Dict[str, List[BurnRateAlert]] = defaultdict(list)
        
    def setup_alerts(self, slo_id: str) -> List[BurnRateAlert]:
        """Настройка алертов"""
        # Multi-window, multi-burn-rate alerts
        alert_configs = [
            # Short window, high burn rate - page immediately
            ("5m", "1h", 14.4, AlertSeverity.PAGE),
            # Medium window, medium burn rate - page soon
            ("30m", "6h", 6.0, AlertSeverity.PAGE),
            # Long window, low burn rate - create ticket
            ("2h", "1d", 3.0, AlertSeverity.TICKET),
            # Very long window, slow burn - log
            ("6h", "3d", 1.0, AlertSeverity.LOG)
        ]
        
        alerts = []
        for short, long, threshold, severity in alert_configs:
            alert = BurnRateAlert(
                alert_id=f"alert_{uuid.uuid4().hex[:8]}",
                slo_id=slo_id,
                short_window=short,
                long_window=long,
                burn_rate_threshold=threshold,
                severity=severity
            )
            alerts.append(alert)
            
        self.alerts[slo_id] = alerts
        return alerts
        
    def evaluate(self, slo_id: str) -> List[BurnRateAlert]:
        """Оценка алертов"""
        budget = self.budget_tracker.budgets.get(slo_id)
        if not budget:
            return []
            
        triggered = []
        
        for alert in self.alerts.get(slo_id, []):
            # Check if burn rate exceeds threshold
            if budget.current_burn_rate >= alert.burn_rate_threshold:
                if not alert.triggered:
                    alert.triggered = True
                    alert.triggered_at = datetime.now()
                triggered.append(alert)
            else:
                alert.triggered = False
                alert.triggered_at = None
                
        return triggered


class SLOReporter:
    """Генератор отчётов SLO"""
    
    def __init__(self, slo_manager: SLOManager, sli_collector: SLICollector):
        self.slo_manager = slo_manager
        self.sli_collector = sli_collector
        
    def generate(self, slo_id: str, days: int = 30) -> SLOReport:
        """Генерация отчёта"""
        slo = self.slo_manager.slos.get(slo_id)
        if not slo:
            return None
            
        # Get SLI history
        history = self.sli_collector.get_history(slo.sli_id, hours=days * 24)
        
        if not history:
            return None
            
        sli_values = [dp.sli_value for dp in history]
        
        report = SLOReport(
            report_id=f"report_{uuid.uuid4().hex[:8]}",
            slo_id=slo_id,
            period_start=datetime.now() - timedelta(days=days),
            period_end=datetime.now(),
            average_sli=sum(sli_values) / len(sli_values),
            min_sli=min(sli_values),
            max_sli=max(sli_values),
            target_met=slo.current_sli >= slo.target_percent,
            time_in_compliance_percent=len([v for v in sli_values if v >= slo.target_percent]) / len(sli_values) * 100,
            error_budget_consumed_percent=slo.error_budget_consumed
        )
        
        return report


class SLOManagementPlatform:
    """Платформа управления SLO"""
    
    def __init__(self):
        self.sli_collector = SLICollector()
        self.slo_manager = SLOManager(self.sli_collector)
        self.budget_tracker = ErrorBudgetTracker(self.slo_manager)
        self.alerter = BurnRateAlerter(self.slo_manager, self.budget_tracker)
        self.reporter = SLOReporter(self.slo_manager, self.sli_collector)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        slos = list(self.slo_manager.slos.values())
        
        in_compliance = len([s for s in slos if s.current_sli >= s.target_percent])
        low_budget = len([s for s in slos if s.error_budget_remaining < 20])
        
        triggered_alerts = sum(
            len([a for a in alerts if a.triggered])
            for alerts in self.alerter.alerts.values()
        )
        
        return {
            "total_slis": len(self.sli_collector.slis),
            "total_slos": len(slos),
            "slos_in_compliance": in_compliance,
            "slos_out_of_compliance": len(slos) - in_compliance,
            "slos_low_budget": low_budget,
            "triggered_alerts": triggered_alerts
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 125: SLO Management Platform")
    print("=" * 60)
    
    async def demo():
        platform = SLOManagementPlatform()
        print("✓ SLO Management Platform created")
        
        # Create SLIs
        print("\n📏 Creating SLIs...")
        
        slis_data = [
            ("API Availability", SLIType.AVAILABILITY, "successful_requests", "total_requests"),
            ("API Latency P99", SLIType.LATENCY, "requests_under_300ms", "total_requests"),
            ("Error Rate", SLIType.ERROR_RATE, "non_error_requests", "total_requests"),
            ("Database Availability", SLIType.AVAILABILITY, "db_successful_queries", "db_total_queries"),
            ("Throughput", SLIType.THROUGHPUT, "successful_ops", "total_ops")
        ]
        
        created_slis = []
        for name, sli_type, good_query, total_query in slis_data:
            sli = platform.sli_collector.create(name, sli_type, good_query, total_query)
            created_slis.append(sli)
            print(f"  ✓ {name} ({sli_type.value})")
            
        # Create SLOs
        print("\n🎯 Creating SLOs...")
        
        slos_data = [
            ("API Availability SLO", "api-service", created_slis[0].sli_id, 99.9),
            ("API Latency SLO", "api-service", created_slis[1].sli_id, 99.0),
            ("Error Rate SLO", "api-service", created_slis[2].sli_id, 99.5),
            ("Database Availability SLO", "db-service", created_slis[3].sli_id, 99.99),
            ("Throughput SLO", "batch-service", created_slis[4].sli_id, 95.0)
        ]
        
        created_slos = []
        for name, service, sli_id, target in slos_data:
            slo = platform.slo_manager.create(
                name, service, sli_id,
                target_percent=target,
                window=TimeWindow.ROLLING_30D
            )
            created_slos.append(slo)
            
            # Setup alerts
            platform.alerter.setup_alerts(slo.slo_id)
            
            print(f"  ✓ {name}: {target}% target")
            
        # Simulate SLI data collection
        print("\n📊 Collecting SLI Data...")
        
        for i in range(100):
            for sli in created_slis:
                # Simulate varying performance
                if sli.sli_type == SLIType.AVAILABILITY:
                    total = random.randint(1000, 5000)
                    good = int(total * random.uniform(0.995, 1.0))
                elif sli.sli_type == SLIType.LATENCY:
                    total = random.randint(1000, 5000)
                    good = int(total * random.uniform(0.98, 1.0))
                else:
                    total = random.randint(1000, 5000)
                    good = int(total * random.uniform(0.99, 1.0))
                    
                platform.sli_collector.collect(sli.sli_id, good, total)
                
        print(f"  Collected {100 * len(created_slis)} datapoints")
        
        # Update SLOs
        print("\n🔄 Updating SLO Status...")
        
        for slo in created_slos:
            result = platform.slo_manager.update(slo.slo_id)
            
            status_icon = "🟢" if result.get("in_compliance") else "🔴"
            budget_icon = "✅" if result.get("error_budget_remaining", 0) > 50 else "⚠️" if result.get("error_budget_remaining", 0) > 20 else "🚨"
            
            print(f"  {status_icon} {slo.name}")
            print(f"     Current: {result['current_sli']:.3f}% (target: {result['target']}%)")
            print(f"     {budget_icon} Error budget: {result['error_budget_remaining']:.1f}% remaining")
            
        # Calculate error budgets
        print("\n💰 Error Budget Analysis...")
        
        for slo in created_slos[:3]:
            budget = platform.budget_tracker.calculate(slo.slo_id)
            
            print(f"\n  {slo.name}:")
            print(f"    Total budget: {budget.total_budget_minutes:.1f} minutes")
            print(f"    Consumed: {budget.consumed_minutes:.1f} minutes")
            print(f"    Remaining: {budget.remaining_minutes:.1f} minutes")
            print(f"    Burn rate: {budget.current_burn_rate:.2f}x")
            
            if budget.projected_exhaustion:
                days_until = (budget.projected_exhaustion - datetime.now()).days
                print(f"    ⚠️ Projected exhaustion in {days_until} days")
                
        # Evaluate alerts
        print("\n🚨 Burn Rate Alerts...")
        
        for slo in created_slos:
            triggered = platform.alerter.evaluate(slo.slo_id)
            
            if triggered:
                for alert in triggered:
                    icon = {"page": "🔴", "ticket": "🟡", "log": "🔵"}.get(alert.severity.value, "⚪")
                    print(f"  {icon} {slo.name}: {alert.severity.value} - burn rate {platform.budget_tracker.budgets[slo.slo_id].current_burn_rate:.1f}x > {alert.burn_rate_threshold}x")
                    
        # Generate reports
        print("\n📋 SLO Reports (30 days):")
        
        for slo in created_slos[:3]:
            report = platform.reporter.generate(slo.slo_id, days=30)
            
            if report:
                status = "✅ Met" if report.target_met else "❌ Missed"
                print(f"\n  {slo.name}:")
                print(f"    Average SLI: {report.average_sli:.3f}%")
                print(f"    Min/Max: {report.min_sli:.3f}% / {report.max_sli:.3f}%")
                print(f"    Time in compliance: {report.time_in_compliance_percent:.1f}%")
                print(f"    Target: {status}")
                
        # Service overview
        print("\n🔍 Service SLO Overview:")
        
        services = defaultdict(list)
        for slo in created_slos:
            services[slo.service_name].append(slo)
            
        for service, slos in services.items():
            all_compliant = all(s.current_sli >= s.target_percent for s in slos)
            icon = "🟢" if all_compliant else "🔴"
            print(f"\n  {icon} {service}:")
            for slo in slos:
                status = "✓" if slo.current_sli >= slo.target_percent else "✗"
                print(f"    {status} {slo.name}: {slo.current_sli:.3f}%")
                
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  SLIs: {stats['total_slis']}")
        print(f"  SLOs: {stats['total_slos']}")
        print(f"  In Compliance: {stats['slos_in_compliance']}")
        print(f"  Out of Compliance: {stats['slos_out_of_compliance']}")
        print(f"  Low Budget (<20%): {stats['slos_low_budget']}")
        print(f"  Triggered Alerts: {stats['triggered_alerts']}")
        
        # Dashboard
        compliance_pct = (stats['slos_in_compliance'] / stats['total_slos'] * 100) if stats['total_slos'] > 0 else 0
        
        print("\n📋 SLO Management Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │               SLO Management Overview                       │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total SLIs:         {stats['total_slis']:>10}                        │")
        print(f"  │ Total SLOs:         {stats['total_slos']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ In Compliance:      {stats['slos_in_compliance']:>10}                        │")
        print(f"  │ Out of Compliance:  {stats['slos_out_of_compliance']:>10}                        │")
        print(f"  │ Compliance Rate:    {compliance_pct:>10.1f}%                       │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Low Budget SLOs:    {stats['slos_low_budget']:>10}                        │")
        print(f"  │ Triggered Alerts:   {stats['triggered_alerts']:>10}                        │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("SLO Management Platform initialized!")
    print("=" * 60)
