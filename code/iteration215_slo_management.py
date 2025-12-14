#!/usr/bin/env python3
"""
Server Init - Iteration 215: SLO Management Platform
Платформа управления SLO

Функционал:
- SLO Definition - определение SLO
- Error Budget - бюджет ошибок
- SLI Tracking - отслеживание SLI
- Burn Rate Alerts - алерты скорости сжигания
- Compliance Reports - отчёты о соответствии
- Budget Policies - политики бюджета
- Multi-window Alerting - многооконные алерты
- Historical Analysis - исторический анализ
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class SLOType(Enum):
    """Тип SLO"""
    AVAILABILITY = "availability"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    QUALITY = "quality"


class ComplianceStatus(Enum):
    """Статус соответствия"""
    COMPLIANT = "compliant"
    AT_RISK = "at_risk"
    VIOLATED = "violated"


class AlertSeverity(Enum):
    """Серьёзность алерта"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class WindowType(Enum):
    """Тип окна"""
    ROLLING = "rolling"
    CALENDAR = "calendar"


@dataclass
class SLI:
    """Service Level Indicator"""
    sli_id: str
    name: str = ""
    
    # Query
    good_query: str = ""  # Query for good events
    total_query: str = ""  # Query for total events
    
    # Current value
    current_value: float = 0  # 0-100%
    
    # Time
    last_measured: datetime = field(default_factory=datetime.now)


@dataclass
class SLO:
    """Service Level Objective"""
    slo_id: str
    name: str = ""
    description: str = ""
    
    # Type
    slo_type: SLOType = SLOType.AVAILABILITY
    
    # Target
    target_percentage: float = 99.9  # 99.9%
    
    # SLI
    sli_id: str = ""
    
    # Window
    window_type: WindowType = WindowType.ROLLING
    window_days: int = 30
    
    # Status
    status: ComplianceStatus = ComplianceStatus.COMPLIANT
    
    # Current
    current_value: float = 0
    
    # Service
    service_name: str = ""
    
    # Tags
    tags: List[str] = field(default_factory=list)


@dataclass
class ErrorBudget:
    """Бюджет ошибок"""
    budget_id: str
    slo_id: str = ""
    
    # Budget
    total_budget_minutes: float = 0
    consumed_minutes: float = 0
    remaining_minutes: float = 0
    
    # Percentage
    remaining_percentage: float = 100
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=30))
    
    # Burn rate
    current_burn_rate: float = 1.0  # 1x = normal, >1 = faster burn
    
    @property
    def is_exhausted(self) -> bool:
        return self.remaining_percentage <= 0


@dataclass
class BurnRateAlert:
    """Алерт скорости сжигания"""
    alert_id: str
    slo_id: str = ""
    
    # Windows
    short_window_hours: int = 1
    long_window_hours: int = 6
    
    # Thresholds
    short_window_burn_rate: float = 14.4  # Will exhaust budget in ~5 hours
    long_window_burn_rate: float = 6.0    # Will exhaust budget in ~24 hours
    
    # Current
    current_short_burn: float = 0
    current_long_burn: float = 0
    
    # Status
    triggered: bool = False
    severity: AlertSeverity = AlertSeverity.WARNING
    
    # Time
    triggered_at: Optional[datetime] = None


@dataclass
class SLOReport:
    """Отчёт по SLO"""
    report_id: str
    slo_id: str = ""
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Metrics
    average_sli: float = 0
    min_sli: float = 0
    max_sli: float = 0
    
    # Compliance
    compliance_percentage: float = 0  # % of time in compliance
    
    # Budget
    budget_consumed_percentage: float = 0
    
    # Incidents
    violation_count: int = 0
    total_downtime_minutes: float = 0
    
    # Generated
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class BudgetPolicy:
    """Политика бюджета"""
    policy_id: str
    name: str = ""
    
    # Thresholds
    warning_threshold: float = 50  # Warn when 50% consumed
    critical_threshold: float = 80  # Critical when 80% consumed
    
    # Actions
    freeze_deployments_on_exhaust: bool = True
    notify_stakeholders: bool = True
    
    # Active
    active: bool = True


class SLICollector:
    """Сборщик SLI"""
    
    def __init__(self):
        self.slis: Dict[str, SLI] = {}
        self.measurements: Dict[str, List[tuple]] = {}  # sli_id -> [(timestamp, value)]
        
    def create_sli(self, name: str, good_query: str = "",
                  total_query: str = "") -> SLI:
        """Создание SLI"""
        sli = SLI(
            sli_id=f"sli_{uuid.uuid4().hex[:8]}",
            name=name,
            good_query=good_query,
            total_query=total_query
        )
        self.slis[sli.sli_id] = sli
        self.measurements[sli.sli_id] = []
        return sli
        
    async def measure(self, sli_id: str) -> float:
        """Измерение SLI"""
        sli = self.slis.get(sli_id)
        if not sli:
            return 0
            
        # Simulate measurement
        await asyncio.sleep(0.01)
        
        # Generate realistic SLI value (usually high availability)
        value = random.gauss(99.5, 0.5)
        value = max(95, min(100, value))  # Clamp to realistic range
        
        sli.current_value = value
        sli.last_measured = datetime.now()
        
        self.measurements[sli_id].append((datetime.now(), value))
        
        # Keep only last 1000 measurements
        if len(self.measurements[sli_id]) > 1000:
            self.measurements[sli_id] = self.measurements[sli_id][-1000:]
            
        return value


class ErrorBudgetCalculator:
    """Калькулятор бюджета ошибок"""
    
    def calculate_budget(self, slo: SLO, window_days: int = 30) -> ErrorBudget:
        """Расчёт бюджета ошибок"""
        # Total minutes in window
        total_minutes = window_days * 24 * 60
        
        # Allowed downtime
        allowed_downtime_percentage = 100 - slo.target_percentage
        total_budget = total_minutes * (allowed_downtime_percentage / 100)
        
        # Calculate consumed (simulated)
        # In reality, would be based on actual SLI measurements
        actual_sli = slo.current_value if slo.current_value > 0 else 99.5
        
        # Calculate consumed based on actual vs target
        if actual_sli >= slo.target_percentage:
            consumed_ratio = 0.3  # Some normal consumption
        else:
            gap = slo.target_percentage - actual_sli
            consumed_ratio = min(1.0, gap / allowed_downtime_percentage)
            
        consumed = total_budget * consumed_ratio
        remaining = total_budget - consumed
        
        budget = ErrorBudget(
            budget_id=f"budget_{uuid.uuid4().hex[:8]}",
            slo_id=slo.slo_id,
            total_budget_minutes=total_budget,
            consumed_minutes=consumed,
            remaining_minutes=remaining,
            remaining_percentage=(remaining / total_budget * 100) if total_budget > 0 else 0,
            period_end=datetime.now() + timedelta(days=window_days)
        )
        
        # Calculate burn rate
        days_elapsed = random.uniform(5, 15)
        expected_consumed = (days_elapsed / window_days) * total_budget
        budget.current_burn_rate = consumed / expected_consumed if expected_consumed > 0 else 1.0
        
        return budget


class BurnRateAlertEngine:
    """Движок алертов скорости сжигания"""
    
    def __init__(self):
        self.alerts: Dict[str, BurnRateAlert] = {}
        
    def create_alert_config(self, slo_id: str,
                           short_window: int = 1,
                           long_window: int = 6) -> BurnRateAlert:
        """Создание конфигурации алерта"""
        alert = BurnRateAlert(
            alert_id=f"burnalert_{uuid.uuid4().hex[:8]}",
            slo_id=slo_id,
            short_window_hours=short_window,
            long_window_hours=long_window
        )
        self.alerts[alert.alert_id] = alert
        return alert
        
    def evaluate(self, alert: BurnRateAlert, budget: ErrorBudget) -> bool:
        """Оценка алерта"""
        # Simulate burn rates based on budget
        alert.current_short_burn = budget.current_burn_rate * random.uniform(0.8, 1.5)
        alert.current_long_burn = budget.current_burn_rate * random.uniform(0.9, 1.2)
        
        # Check thresholds
        short_triggered = alert.current_short_burn >= alert.short_window_burn_rate
        long_triggered = alert.current_long_burn >= alert.long_window_burn_rate
        
        if short_triggered and long_triggered:
            alert.triggered = True
            alert.severity = AlertSeverity.CRITICAL
            alert.triggered_at = datetime.now()
        elif short_triggered or long_triggered:
            alert.triggered = True
            alert.severity = AlertSeverity.WARNING
            alert.triggered_at = datetime.now()
        else:
            alert.triggered = False
            
        return alert.triggered


class SLOManagementPlatform:
    """Платформа управления SLO"""
    
    def __init__(self):
        self.slos: Dict[str, SLO] = {}
        self.sli_collector = SLICollector()
        self.budget_calculator = ErrorBudgetCalculator()
        self.alert_engine = BurnRateAlertEngine()
        self.policies: Dict[str, BudgetPolicy] = {}
        self.budgets: Dict[str, ErrorBudget] = {}
        self.reports: List[SLOReport] = []
        
    def create_slo(self, name: str, service_name: str,
                  slo_type: SLOType, target: float,
                  sli_name: str = "", window_days: int = 30) -> SLO:
        """Создание SLO"""
        # Create SLI
        sli = self.sli_collector.create_sli(
            sli_name or f"{service_name}_sli",
            good_query=f"sum(rate(http_requests_total{{service='{service_name}',status='success'}}[5m]))",
            total_query=f"sum(rate(http_requests_total{{service='{service_name}'}}[5m]))"
        )
        
        slo = SLO(
            slo_id=f"slo_{uuid.uuid4().hex[:8]}",
            name=name,
            slo_type=slo_type,
            target_percentage=target,
            sli_id=sli.sli_id,
            window_days=window_days,
            service_name=service_name
        )
        self.slos[slo.slo_id] = slo
        
        # Create burn rate alert
        self.alert_engine.create_alert_config(slo.slo_id)
        
        return slo
        
    def create_policy(self, name: str, warning: float = 50,
                     critical: float = 80) -> BudgetPolicy:
        """Создание политики"""
        policy = BudgetPolicy(
            policy_id=f"policy_{uuid.uuid4().hex[:8]}",
            name=name,
            warning_threshold=warning,
            critical_threshold=critical
        )
        self.policies[policy.policy_id] = policy
        return policy
        
    async def measure_all(self):
        """Измерение всех SLI"""
        for slo in self.slos.values():
            value = await self.sli_collector.measure(slo.sli_id)
            slo.current_value = value
            
            # Update status
            if value >= slo.target_percentage:
                slo.status = ComplianceStatus.COMPLIANT
            elif value >= slo.target_percentage - 0.5:
                slo.status = ComplianceStatus.AT_RISK
            else:
                slo.status = ComplianceStatus.VIOLATED
                
    def calculate_budgets(self):
        """Расчёт всех бюджетов"""
        for slo in self.slos.values():
            budget = self.budget_calculator.calculate_budget(slo, slo.window_days)
            self.budgets[slo.slo_id] = budget
            
    def evaluate_alerts(self) -> List[BurnRateAlert]:
        """Оценка всех алертов"""
        triggered = []
        
        for alert in self.alert_engine.alerts.values():
            budget = self.budgets.get(alert.slo_id)
            if budget and self.alert_engine.evaluate(alert, budget):
                triggered.append(alert)
                
        return triggered
        
    def generate_report(self, slo_id: str, days: int = 30) -> SLOReport:
        """Генерация отчёта"""
        slo = self.slos.get(slo_id)
        if not slo:
            return SLOReport(report_id=f"report_{uuid.uuid4().hex[:8]}")
            
        # Get measurements
        measurements = self.sli_collector.measurements.get(slo.sli_id, [])
        values = [v for _, v in measurements] if measurements else [slo.current_value]
        
        budget = self.budgets.get(slo_id)
        
        report = SLOReport(
            report_id=f"report_{uuid.uuid4().hex[:8]}",
            slo_id=slo_id,
            period_start=datetime.now() - timedelta(days=days),
            period_end=datetime.now(),
            average_sli=sum(values) / len(values) if values else 0,
            min_sli=min(values) if values else 0,
            max_sli=max(values) if values else 0,
            compliance_percentage=len([v for v in values if v >= slo.target_percentage]) / len(values) * 100 if values else 0,
            budget_consumed_percentage=100 - budget.remaining_percentage if budget else 0,
            violation_count=len([v for v in values if v < slo.target_percentage]),
            total_downtime_minutes=budget.consumed_minutes if budget else 0
        )
        
        self.reports.append(report)
        return report
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        return {
            "total_slos": len(self.slos),
            "compliant_slos": len([s for s in self.slos.values() if s.status == ComplianceStatus.COMPLIANT]),
            "at_risk_slos": len([s for s in self.slos.values() if s.status == ComplianceStatus.AT_RISK]),
            "violated_slos": len([s for s in self.slos.values() if s.status == ComplianceStatus.VIOLATED]),
            "total_slis": len(self.sli_collector.slis),
            "triggered_alerts": len([a for a in self.alert_engine.alerts.values() if a.triggered]),
            "exhausted_budgets": len([b for b in self.budgets.values() if b.is_exhausted]),
            "reports_generated": len(self.reports)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 215: SLO Management Platform")
    print("=" * 60)
    
    platform = SLOManagementPlatform()
    print("✓ SLO Management Platform created")
    
    # Create SLOs
    print("\n📊 Creating SLOs...")
    
    slos_config = [
        ("API Gateway Availability", "api-gateway", SLOType.AVAILABILITY, 99.9),
        ("User Service Latency P99", "user-service", SLOType.LATENCY, 99.5),
        ("Order Service Availability", "order-service", SLOType.AVAILABILITY, 99.95),
        ("Payment Service Error Rate", "payment-service", SLOType.ERROR_RATE, 99.99),
        ("Search Service Throughput", "search-service", SLOType.THROUGHPUT, 99.0),
    ]
    
    for name, service, slo_type, target in slos_config:
        slo = platform.create_slo(name, service, slo_type, target)
        print(f"  ✓ {name}: {target}% target")
        
    # Create policies
    print("\n📋 Creating Budget Policies...")
    
    standard_policy = platform.create_policy("Standard", 50, 80)
    print(f"  ✓ {standard_policy.name}: warn at {standard_policy.warning_threshold}%, critical at {standard_policy.critical_threshold}%")
    
    strict_policy = platform.create_policy("Strict", 30, 60)
    print(f"  ✓ {strict_policy.name}: warn at {strict_policy.warning_threshold}%, critical at {strict_policy.critical_threshold}%")
    
    # Measure SLIs
    print("\n📏 Measuring SLIs...")
    
    for _ in range(5):  # Multiple measurements
        await platform.measure_all()
        
    print(f"  ✓ Collected {sum(len(m) for m in platform.sli_collector.measurements.values())} measurements")
    
    # Calculate budgets
    print("\n💰 Calculating Error Budgets...")
    
    platform.calculate_budgets()
    print(f"  ✓ Calculated {len(platform.budgets)} budgets")
    
    # Evaluate alerts
    print("\n🚨 Evaluating Burn Rate Alerts...")
    
    triggered = platform.evaluate_alerts()
    print(f"  ✓ {len(triggered)} alerts triggered")
    
    # Display SLO status
    print("\n📊 SLO Status:")
    
    print("\n  ┌────────────────────────────┬────────────┬──────────┬──────────────┐")
    print("  │ SLO                        │ Target     │ Current  │ Status       │")
    print("  ├────────────────────────────┼────────────┼──────────┼──────────────┤")
    
    for slo in platform.slos.values():
        name = slo.name[:26].ljust(26)
        target = f"{slo.target_percentage}%".center(10)
        current = f"{slo.current_value:.2f}%".center(8)
        
        status_icons = {
            ComplianceStatus.COMPLIANT: "🟢",
            ComplianceStatus.AT_RISK: "🟡",
            ComplianceStatus.VIOLATED: "🔴"
        }
        status = f"{status_icons.get(slo.status, '⚪')} {slo.status.value}"[:12].ljust(12)
        
        print(f"  │ {name} │ {target} │ {current} │ {status} │")
        
    print("  └────────────────────────────┴────────────┴──────────┴──────────────┘")
    
    # Error budgets
    print("\n💰 Error Budgets:")
    
    print("\n  ┌────────────────────────────┬────────────┬────────────┬────────────┐")
    print("  │ SLO                        │ Remaining  │ Burn Rate  │ Status     │")
    print("  ├────────────────────────────┼────────────┼────────────┼────────────┤")
    
    for slo in platform.slos.values():
        budget = platform.budgets.get(slo.slo_id)
        if not budget:
            continue
            
        name = slo.name[:26].ljust(26)
        remaining = f"{budget.remaining_percentage:.1f}%".center(10)
        burn = f"{budget.current_burn_rate:.2f}x".center(10)
        
        if budget.remaining_percentage > 50:
            status_icon = "🟢"
        elif budget.remaining_percentage > 20:
            status_icon = "🟡"
        else:
            status_icon = "🔴"
            
        status = f"{status_icon} {'OK' if budget.remaining_percentage > 0 else 'Exhausted'}"[:10].ljust(10)
        
        print(f"  │ {name} │ {remaining} │ {burn} │ {status} │")
        
    print("  └────────────────────────────┴────────────┴────────────┴────────────┘")
    
    # Budget visualization
    print("\n📊 Budget Consumption:")
    
    for slo in platform.slos.values():
        budget = platform.budgets.get(slo.slo_id)
        if not budget:
            continue
            
        consumed_pct = 100 - budget.remaining_percentage
        bar_len = int(consumed_pct / 5)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        
        print(f"  {slo.service_name:15s} [{bar}] {consumed_pct:.1f}% consumed")
        
    # Burn rate alerts
    print("\n🔥 Burn Rate Alerts:")
    
    for alert in platform.alert_engine.alerts.values():
        slo = platform.slos.get(alert.slo_id)
        slo_name = slo.name if slo else "Unknown"
        
        status_icon = "🚨" if alert.triggered else "✓"
        severity = f"[{alert.severity.value.upper()}]" if alert.triggered else ""
        
        print(f"  {status_icon} {slo_name[:30]} {severity}")
        print(f"      Short window ({alert.short_window_hours}h): {alert.current_short_burn:.2f}x (threshold: {alert.short_window_burn_rate})")
        print(f"      Long window ({alert.long_window_hours}h): {alert.current_long_burn:.2f}x (threshold: {alert.long_window_burn_rate})")
        
    # Generate reports
    print("\n📋 Generating Reports...")
    
    for slo in list(platform.slos.values())[:3]:
        report = platform.generate_report(slo.slo_id)
        print(f"\n  {slo.name}:")
        print(f"    Average SLI: {report.average_sli:.2f}%")
        print(f"    Compliance: {report.compliance_percentage:.1f}%")
        print(f"    Budget Consumed: {report.budget_consumed_percentage:.1f}%")
        print(f"    Violations: {report.violation_count}")
        
    # SLO by type
    print("\n📊 SLOs by Type:")
    
    by_type = {}
    for slo in platform.slos.values():
        t = slo.slo_type.value
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(slo)
        
    for slo_type, slos in by_type.items():
        compliant = len([s for s in slos if s.status == ComplianceStatus.COMPLIANT])
        print(f"  {slo_type:15s}: {compliant}/{len(slos)} compliant")
        
    # SLI trends (simulated)
    print("\n📈 SLI Trends (Last 5 Measurements):")
    
    for slo in list(platform.slos.values())[:3]:
        measurements = platform.sli_collector.measurements.get(slo.sli_id, [])
        if measurements:
            recent = measurements[-5:]
            values = [f"{v:.1f}" for _, v in recent]
            print(f"  {slo.service_name:15s}: {' -> '.join(values)}")
            
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📈 Platform Statistics:")
    
    print(f"\n  Total SLOs: {stats['total_slos']}")
    print(f"  Compliant: {stats['compliant_slos']}")
    print(f"  At Risk: {stats['at_risk_slos']}")
    print(f"  Violated: {stats['violated_slos']}")
    print(f"  SLIs: {stats['total_slis']}")
    print(f"  Triggered Alerts: {stats['triggered_alerts']}")
    print(f"  Exhausted Budgets: {stats['exhausted_budgets']}")
    
    # Compliance score
    compliance_score = (stats['compliant_slos'] / stats['total_slos'] * 100) if stats['total_slos'] > 0 else 0
    
    print(f"\n  Overall Compliance: {compliance_score:.0f}%")
    score_bar = "█" * int(compliance_score / 10) + "░" * (10 - int(compliance_score / 10))
    print(f"  [{score_bar}]")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                      SLO Management Dashboard                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total SLOs:                    {stats['total_slos']:>12}                        │")
    print(f"│ Compliant:                     {stats['compliant_slos']:>12}                        │")
    print(f"│ Violated:                      {stats['violated_slos']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Triggered Alerts:              {stats['triggered_alerts']:>12}                        │")
    print(f"│ Overall Compliance:              {compliance_score:>10.0f}%                   │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("SLO Management Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
