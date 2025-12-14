#!/usr/bin/env python3
"""
Server Init - Iteration 173: SLA Management Platform
Платформа управления SLA

Функционал:
- SLA Definition - определение SLA
- SLO/SLI Tracking - отслеживание SLO/SLI
- Error Budget - бюджет ошибок
- Compliance Monitoring - мониторинг соответствия
- Reporting - отчётность
- Alerting - оповещения
- Burn Rate Analysis - анализ сжигания бюджета
- Business Impact Mapping - связь с бизнес-влиянием
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid
from collections import defaultdict


class SLAStatus(Enum):
    """Статус SLA"""
    HEALTHY = "healthy"
    AT_RISK = "at_risk"
    BREACHED = "breached"
    UNKNOWN = "unknown"


class SLOType(Enum):
    """Тип SLO"""
    AVAILABILITY = "availability"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    SATURATION = "saturation"


class ComparisonOperator(Enum):
    """Оператор сравнения"""
    LESS_THAN = "<"
    LESS_EQUAL = "<="
    GREATER_THAN = ">"
    GREATER_EQUAL = ">="
    EQUAL = "=="


class TimeWindow(Enum):
    """Временное окно"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class AlertSeverity(Enum):
    """Серьёзность алерта"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class SLI:
    """Service Level Indicator"""
    sli_id: str
    name: str = ""
    description: str = ""
    
    # Measurement
    metric_name: str = ""  # e.g., request_latency_seconds
    metric_query: str = ""  # PromQL or similar
    
    # Type
    sli_type: SLOType = SLOType.AVAILABILITY
    
    # Unit
    unit: str = ""  # ms, %, count
    
    # Current value
    current_value: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    # History
    history: List[Dict] = field(default_factory=list)


@dataclass
class SLO:
    """Service Level Objective"""
    slo_id: str
    name: str = ""
    description: str = ""
    
    # Target
    target_value: float = 99.9  # e.g., 99.9%
    comparison: ComparisonOperator = ComparisonOperator.GREATER_EQUAL
    
    # SLI
    sli_id: str = ""
    
    # Time window
    window: TimeWindow = TimeWindow.MONTHLY
    window_days: int = 30
    
    # Current status
    current_value: float = 0.0
    status: SLAStatus = SLAStatus.UNKNOWN
    
    # Error budget
    error_budget_total: float = 0.0  # Total allowed errors
    error_budget_remaining: float = 0.0
    error_budget_consumed_percent: float = 0.0
    
    # Burn rate
    burn_rate_1h: float = 0.0
    burn_rate_6h: float = 0.0
    burn_rate_24h: float = 0.0


@dataclass
class SLA:
    """Service Level Agreement"""
    sla_id: str
    name: str = ""
    description: str = ""
    
    # Parties
    service_name: str = ""
    customer: str = ""
    
    # SLOs
    slos: List[str] = field(default_factory=list)  # SLO IDs
    
    # Period
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    
    # Status
    status: SLAStatus = SLAStatus.UNKNOWN
    compliance_percentage: float = 100.0
    
    # Consequences
    penalty_per_breach: float = 0.0  # $ per breach
    credit_percentage: float = 0.0  # % credit per breach
    
    # Metadata
    tier: str = ""  # gold, silver, bronze
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SLABreach:
    """Нарушение SLA"""
    breach_id: str
    sla_id: str = ""
    slo_id: str = ""
    
    # Details
    breach_type: str = ""  # target_missed, error_budget_exhausted
    severity: AlertSeverity = AlertSeverity.ERROR
    
    # Values
    target_value: float = 0.0
    actual_value: float = 0.0
    deviation: float = 0.0  # How far from target
    
    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    duration_minutes: float = 0.0
    
    # Impact
    affected_customers: int = 0
    financial_impact: float = 0.0
    
    # Resolution
    resolved: bool = False
    root_cause: str = ""
    incident_id: str = ""


@dataclass
class ErrorBudgetReport:
    """Отчёт по error budget"""
    report_id: str
    slo_id: str = ""
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Budget
    total_budget_minutes: float = 0.0
    consumed_minutes: float = 0.0
    remaining_minutes: float = 0.0
    
    # Percentage
    consumed_percent: float = 0.0
    
    # Projection
    projected_end_date: Optional[datetime] = None
    burn_rate: float = 0.0
    
    # Status
    on_track: bool = True


@dataclass
class SLAReport:
    """Отчёт по SLA"""
    report_id: str
    sla_id: str = ""
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Compliance
    overall_compliance: float = 0.0
    slo_compliance: Dict[str, float] = field(default_factory=dict)
    
    # Breaches
    total_breaches: int = 0
    breach_summary: List[Dict] = field(default_factory=list)
    
    # Financial
    credits_issued: float = 0.0
    penalties_incurred: float = 0.0
    
    # Generated
    generated_at: datetime = field(default_factory=datetime.now)


class SLICollector:
    """Сборщик SLI"""
    
    def __init__(self):
        self.slis: Dict[str, SLI] = {}
        
    def register_sli(self, sli: SLI):
        """Регистрация SLI"""
        self.slis[sli.sli_id] = sli
        
    async def collect(self, sli_id: str) -> float:
        """Сбор значения SLI"""
        sli = self.slis.get(sli_id)
        if not sli:
            return 0.0
            
        # Simulate metric collection
        if sli.sli_type == SLOType.AVAILABILITY:
            # Simulate availability between 99.5% and 100%
            value = random.uniform(99.5, 100.0)
        elif sli.sli_type == SLOType.LATENCY:
            # Simulate latency between 50ms and 500ms
            value = random.uniform(50, 500)
        elif sli.sli_type == SLOType.ERROR_RATE:
            # Simulate error rate between 0% and 2%
            value = random.uniform(0, 2)
        else:
            value = random.uniform(0, 100)
            
        sli.current_value = value
        sli.last_updated = datetime.now()
        
        # Store in history
        sli.history.append({
            "timestamp": datetime.now(),
            "value": value
        })
        
        # Keep only last 1000 points
        if len(sli.history) > 1000:
            sli.history = sli.history[-1000:]
            
        return value
        
    def get_average(self, sli_id: str, hours: int = 1) -> float:
        """Получение среднего значения"""
        sli = self.slis.get(sli_id)
        if not sli or not sli.history:
            return 0.0
            
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [h["value"] for h in sli.history if h["timestamp"] > cutoff]
        
        return sum(recent) / len(recent) if recent else 0.0


class SLOEvaluator:
    """Оценщик SLO"""
    
    def __init__(self, sli_collector: SLICollector):
        self.sli_collector = sli_collector
        self.slos: Dict[str, SLO] = {}
        
    def register_slo(self, slo: SLO):
        """Регистрация SLO"""
        self.slos[slo.slo_id] = slo
        self._calculate_error_budget(slo)
        
    def _calculate_error_budget(self, slo: SLO):
        """Расчёт error budget"""
        # Total minutes in window
        total_minutes = slo.window_days * 24 * 60
        
        # Error budget = (100 - target) * total time
        # e.g., for 99.9% target: 0.1% * 43200 min = 43.2 minutes
        error_percent = 100 - slo.target_value
        slo.error_budget_total = (error_percent / 100) * total_minutes
        slo.error_budget_remaining = slo.error_budget_total
        
    async def evaluate(self, slo_id: str) -> SLO:
        """Оценка SLO"""
        slo = self.slos.get(slo_id)
        if not slo:
            return None
            
        # Get current SLI value
        current_value = await self.sli_collector.collect(slo.sli_id)
        slo.current_value = current_value
        
        # Evaluate compliance
        if slo.comparison == ComparisonOperator.GREATER_EQUAL:
            compliant = current_value >= slo.target_value
        elif slo.comparison == ComparisonOperator.GREATER_THAN:
            compliant = current_value > slo.target_value
        elif slo.comparison == ComparisonOperator.LESS_EQUAL:
            compliant = current_value <= slo.target_value
        elif slo.comparison == ComparisonOperator.LESS_THAN:
            compliant = current_value < slo.target_value
        else:
            compliant = current_value == slo.target_value
            
        # Update status
        if not compliant:
            # Consume error budget
            consumed = abs(current_value - slo.target_value) / 100 * 1  # 1 minute sample
            slo.error_budget_remaining = max(0, slo.error_budget_remaining - consumed)
            
        slo.error_budget_consumed_percent = (
            (slo.error_budget_total - slo.error_budget_remaining) / slo.error_budget_total * 100
            if slo.error_budget_total > 0 else 0
        )
        
        # Determine status
        if slo.error_budget_consumed_percent >= 100:
            slo.status = SLAStatus.BREACHED
        elif slo.error_budget_consumed_percent >= 80:
            slo.status = SLAStatus.AT_RISK
        else:
            slo.status = SLAStatus.HEALTHY
            
        # Calculate burn rates
        self._calculate_burn_rates(slo)
        
        return slo
        
    def _calculate_burn_rates(self, slo: SLO):
        """Расчёт burn rate"""
        # Expected burn rate = 100% / window_days
        expected_daily = 100 / slo.window_days
        
        # Simulated actual burn rates
        slo.burn_rate_1h = random.uniform(0.5, 2.0) * expected_daily / 24
        slo.burn_rate_6h = random.uniform(0.7, 1.5) * expected_daily / 4
        slo.burn_rate_24h = random.uniform(0.8, 1.3) * expected_daily


class SLAManager:
    """Менеджер SLA"""
    
    def __init__(self, slo_evaluator: SLOEvaluator):
        self.slo_evaluator = slo_evaluator
        self.slas: Dict[str, SLA] = {}
        self.breaches: List[SLABreach] = []
        
    def register_sla(self, sla: SLA):
        """Регистрация SLA"""
        self.slas[sla.sla_id] = sla
        
    async def evaluate_sla(self, sla_id: str) -> SLA:
        """Оценка SLA"""
        sla = self.slas.get(sla_id)
        if not sla:
            return None
            
        # Evaluate all SLOs
        slo_statuses = []
        compliance_values = []
        
        for slo_id in sla.slos:
            slo = await self.slo_evaluator.evaluate(slo_id)
            if slo:
                slo_statuses.append(slo.status)
                
                # Calculate compliance based on error budget
                compliance = max(0, 100 - slo.error_budget_consumed_percent)
                compliance_values.append(compliance)
                
        # Overall SLA status
        if SLAStatus.BREACHED in slo_statuses:
            sla.status = SLAStatus.BREACHED
        elif SLAStatus.AT_RISK in slo_statuses:
            sla.status = SLAStatus.AT_RISK
        else:
            sla.status = SLAStatus.HEALTHY
            
        # Overall compliance
        sla.compliance_percentage = sum(compliance_values) / len(compliance_values) if compliance_values else 100
        
        # Check for breach
        if sla.status == SLAStatus.BREACHED:
            self._record_breach(sla)
            
        return sla
        
    def _record_breach(self, sla: SLA):
        """Запись нарушения"""
        breach = SLABreach(
            breach_id=f"breach_{uuid.uuid4().hex[:8]}",
            sla_id=sla.sla_id,
            breach_type="error_budget_exhausted",
            severity=AlertSeverity.CRITICAL,
            target_value=100,
            actual_value=sla.compliance_percentage,
            deviation=100 - sla.compliance_percentage,
            financial_impact=sla.penalty_per_breach
        )
        self.breaches.append(breach)


class ErrorBudgetTracker:
    """Трекер error budget"""
    
    def __init__(self, slo_evaluator: SLOEvaluator):
        self.slo_evaluator = slo_evaluator
        
    def get_budget_status(self, slo_id: str) -> ErrorBudgetReport:
        """Получение статуса бюджета"""
        slo = self.slo_evaluator.slos.get(slo_id)
        if not slo:
            return None
            
        report = ErrorBudgetReport(
            report_id=f"ebr_{uuid.uuid4().hex[:8]}",
            slo_id=slo_id,
            period_start=datetime.now() - timedelta(days=slo.window_days),
            period_end=datetime.now(),
            total_budget_minutes=slo.error_budget_total,
            consumed_minutes=slo.error_budget_total - slo.error_budget_remaining,
            remaining_minutes=slo.error_budget_remaining,
            consumed_percent=slo.error_budget_consumed_percent,
            burn_rate=slo.burn_rate_24h
        )
        
        # Project when budget will be exhausted
        if slo.burn_rate_24h > 0 and slo.error_budget_remaining > 0:
            days_remaining = slo.error_budget_remaining / (slo.burn_rate_24h * slo.error_budget_total / 100)
            report.projected_end_date = datetime.now() + timedelta(days=days_remaining)
            
        report.on_track = slo.error_budget_consumed_percent <= (
            (datetime.now() - report.period_start).days / slo.window_days * 100
        )
        
        return report


class SLAReporter:
    """Генератор отчётов SLA"""
    
    def __init__(self, sla_manager: SLAManager, slo_evaluator: SLOEvaluator):
        self.sla_manager = sla_manager
        self.slo_evaluator = slo_evaluator
        
    def generate_report(self, sla_id: str, days: int = 30) -> SLAReport:
        """Генерация отчёта"""
        sla = self.sla_manager.slas.get(sla_id)
        if not sla:
            return None
            
        report = SLAReport(
            report_id=f"rpt_{uuid.uuid4().hex[:8]}",
            sla_id=sla_id,
            period_start=datetime.now() - timedelta(days=days),
            period_end=datetime.now(),
            overall_compliance=sla.compliance_percentage
        )
        
        # SLO compliance
        for slo_id in sla.slos:
            slo = self.slo_evaluator.slos.get(slo_id)
            if slo:
                compliance = 100 - slo.error_budget_consumed_percent
                report.slo_compliance[slo.name] = round(compliance, 2)
                
        # Breaches
        sla_breaches = [b for b in self.sla_manager.breaches if b.sla_id == sla_id]
        report.total_breaches = len(sla_breaches)
        
        for breach in sla_breaches:
            report.breach_summary.append({
                "breach_id": breach.breach_id,
                "severity": breach.severity.value,
                "deviation": breach.deviation,
                "timestamp": breach.started_at
            })
            
        # Financial impact
        report.credits_issued = sum(b.financial_impact for b in sla_breaches)
        report.penalties_incurred = report.credits_issued * (sla.credit_percentage / 100)
        
        return report


class SLAManagementPlatform:
    """Платформа управления SLA"""
    
    def __init__(self):
        self.sli_collector = SLICollector()
        self.slo_evaluator = SLOEvaluator(self.sli_collector)
        self.sla_manager = SLAManager(self.slo_evaluator)
        self.error_budget_tracker = ErrorBudgetTracker(self.slo_evaluator)
        self.reporter = SLAReporter(self.sla_manager, self.slo_evaluator)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_slas = len(self.sla_manager.slas)
        healthy = len([s for s in self.sla_manager.slas.values() if s.status == SLAStatus.HEALTHY])
        at_risk = len([s for s in self.sla_manager.slas.values() if s.status == SLAStatus.AT_RISK])
        breached = len([s for s in self.sla_manager.slas.values() if s.status == SLAStatus.BREACHED])
        
        return {
            "total_slis": len(self.sli_collector.slis),
            "total_slos": len(self.slo_evaluator.slos),
            "total_slas": total_slas,
            "slas_healthy": healthy,
            "slas_at_risk": at_risk,
            "slas_breached": breached,
            "total_breaches": len(self.sla_manager.breaches)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 173: SLA Management Platform")
    print("=" * 60)
    
    async def demo():
        platform = SLAManagementPlatform()
        print("✓ SLA Management Platform created")
        
        # Define SLIs
        print("\n📊 Defining Service Level Indicators (SLIs)...")
        
        slis = [
            SLI(
                sli_id="sli_availability",
                name="API Availability",
                description="Percentage of successful requests",
                metric_name="http_request_success_rate",
                sli_type=SLOType.AVAILABILITY,
                unit="%"
            ),
            SLI(
                sli_id="sli_latency_p99",
                name="API Latency (P99)",
                description="99th percentile response time",
                metric_name="http_request_duration_seconds_p99",
                sli_type=SLOType.LATENCY,
                unit="ms"
            ),
            SLI(
                sli_id="sli_error_rate",
                name="Error Rate",
                description="Percentage of failed requests",
                metric_name="http_request_error_rate",
                sli_type=SLOType.ERROR_RATE,
                unit="%"
            ),
            SLI(
                sli_id="sli_throughput",
                name="Request Throughput",
                description="Requests per second",
                metric_name="http_requests_total_rate",
                sli_type=SLOType.THROUGHPUT,
                unit="req/s"
            ),
        ]
        
        for sli in slis:
            platform.sli_collector.register_sli(sli)
            print(f"  ✓ {sli.name} ({sli.sli_type.value})")
            
        # Define SLOs
        print("\n🎯 Defining Service Level Objectives (SLOs)...")
        
        slos = [
            SLO(
                slo_id="slo_availability",
                name="Availability SLO",
                description="99.9% availability target",
                target_value=99.9,
                comparison=ComparisonOperator.GREATER_EQUAL,
                sli_id="sli_availability",
                window=TimeWindow.MONTHLY,
                window_days=30
            ),
            SLO(
                slo_id="slo_latency",
                name="Latency SLO",
                description="P99 latency under 200ms",
                target_value=200,
                comparison=ComparisonOperator.LESS_EQUAL,
                sli_id="sli_latency_p99",
                window=TimeWindow.MONTHLY,
                window_days=30
            ),
            SLO(
                slo_id="slo_error_rate",
                name="Error Rate SLO",
                description="Error rate under 0.1%",
                target_value=0.1,
                comparison=ComparisonOperator.LESS_EQUAL,
                sli_id="sli_error_rate",
                window=TimeWindow.WEEKLY,
                window_days=7
            ),
        ]
        
        for slo in slos:
            platform.slo_evaluator.register_slo(slo)
            print(f"  ✓ {slo.name}: {slo.target_value}{platform.sli_collector.slis.get(slo.sli_id, SLI(sli_id='')).unit}")
            print(f"    Error Budget: {slo.error_budget_total:.1f} minutes")
            
        # Define SLAs
        print("\n📋 Defining Service Level Agreements (SLAs)...")
        
        slas = [
            SLA(
                sla_id="sla_enterprise",
                name="Enterprise API SLA",
                description="Enterprise tier service agreement",
                service_name="api-gateway",
                customer="Enterprise Customers",
                slos=["slo_availability", "slo_latency", "slo_error_rate"],
                tier="gold",
                penalty_per_breach=10000,
                credit_percentage=25
            ),
            SLA(
                sla_id="sla_standard",
                name="Standard API SLA",
                description="Standard tier service agreement",
                service_name="api-gateway",
                customer="Standard Customers",
                slos=["slo_availability", "slo_latency"],
                tier="silver",
                penalty_per_breach=1000,
                credit_percentage=10
            ),
        ]
        
        for sla in slas:
            platform.sla_manager.register_sla(sla)
            print(f"  ✓ {sla.name}")
            print(f"    Customer: {sla.customer}")
            print(f"    Tier: {sla.tier}")
            print(f"    SLOs: {len(sla.slos)}")
            
        # Collect SLI data
        print("\n📈 Collecting SLI Data...")
        
        for sli_id in platform.sli_collector.slis:
            for _ in range(10):  # Collect 10 samples
                await platform.sli_collector.collect(sli_id)
                await asyncio.sleep(0.01)
                
        print("  ✓ Data collection completed")
        
        # Show current SLI values
        print("\n  Current SLI Values:")
        
        print("\n  ┌──────────────────────────────────────────────────────────────────────┐")
        print("  │ SLI                    │ Current      │ Unit      │")
        print("  ├──────────────────────────────────────────────────────────────────────┤")
        
        for sli in platform.sli_collector.slis.values():
            name = sli.name[:22].ljust(22)
            value = f"{sli.current_value:.2f}".rjust(12)
            unit = sli.unit[:9].ljust(9)
            print(f"  │ {name} │ {value} │ {unit} │")
            
        print("  └──────────────────────────────────────────────────────────────────────┘")
        
        # Evaluate SLOs
        print("\n🔍 Evaluating SLOs...")
        
        for slo_id in platform.slo_evaluator.slos:
            slo = await platform.slo_evaluator.evaluate(slo_id)
            
        print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────┐")
        print("  │ SLO                    │ Target   │ Current  │ Status    │ Error Budget  │")
        print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────┤")
        
        for slo in platform.slo_evaluator.slos.values():
            name = slo.name[:22].ljust(22)
            target = f"{slo.target_value:.1f}".rjust(8)
            current = f"{slo.current_value:.2f}".rjust(8)
            
            status_icons = {
                SLAStatus.HEALTHY: "🟢",
                SLAStatus.AT_RISK: "🟡",
                SLAStatus.BREACHED: "🔴",
                SLAStatus.UNKNOWN: "⚪"
            }
            status = f"{status_icons.get(slo.status, '⚪')} {slo.status.value[:7]}".ljust(10)
            
            budget = f"{100 - slo.error_budget_consumed_percent:.1f}%".rjust(13)
            print(f"  │ {name} │ {target} │ {current} │ {status} │ {budget} │")
            
        print("  └────────────────────────────────────────────────────────────────────────────────────────────────────┘")
        
        # Evaluate SLAs
        print("\n📋 Evaluating SLAs...")
        
        for sla_id in platform.sla_manager.slas:
            sla = await platform.sla_manager.evaluate_sla(sla_id)
            
        print("\n  ┌────────────────────────────────────────────────────────────────────────────────┐")
        print("  │ SLA                         │ Tier   │ Compliance │ Status    │")
        print("  ├────────────────────────────────────────────────────────────────────────────────┤")
        
        for sla in platform.sla_manager.slas.values():
            name = sla.name[:27].ljust(27)
            tier = sla.tier[:6].ljust(6)
            compliance = f"{sla.compliance_percentage:.1f}%".rjust(10)
            
            status_icons = {
                SLAStatus.HEALTHY: "🟢",
                SLAStatus.AT_RISK: "🟡",
                SLAStatus.BREACHED: "🔴",
                SLAStatus.UNKNOWN: "⚪"
            }
            status = f"{status_icons.get(sla.status, '⚪')} {sla.status.value[:7]}".ljust(10)
            print(f"  │ {name} │ {tier} │ {compliance} │ {status} │")
            
        print("  └────────────────────────────────────────────────────────────────────────────────┘")
        
        # Error Budget Reports
        print("\n💰 Error Budget Status:")
        
        for slo_id in platform.slo_evaluator.slos:
            report = platform.error_budget_tracker.get_budget_status(slo_id)
            if report:
                slo = platform.slo_evaluator.slos.get(slo_id)
                print(f"\n  {slo.name}:")
                print(f"    Total Budget: {report.total_budget_minutes:.1f} minutes")
                print(f"    Consumed: {report.consumed_minutes:.1f} minutes ({report.consumed_percent:.1f}%)")
                print(f"    Remaining: {report.remaining_minutes:.1f} minutes")
                
                if report.projected_end_date:
                    print(f"    Projected Exhaustion: {report.projected_end_date.strftime('%Y-%m-%d')}")
                    
                status_icon = "✓" if report.on_track else "⚠"
                status_text = "On Track" if report.on_track else "At Risk"
                print(f"    Status: {status_icon} {status_text}")
                
        # Burn Rate Analysis
        print("\n🔥 Burn Rate Analysis:")
        
        print("\n  ┌──────────────────────────────────────────────────────────────────────────┐")
        print("  │ SLO                    │ 1h Rate  │ 6h Rate  │ 24h Rate │")
        print("  ├──────────────────────────────────────────────────────────────────────────┤")
        
        for slo in platform.slo_evaluator.slos.values():
            name = slo.name[:22].ljust(22)
            r1h = f"{slo.burn_rate_1h:.2f}x".rjust(8)
            r6h = f"{slo.burn_rate_6h:.2f}x".rjust(8)
            r24h = f"{slo.burn_rate_24h:.2f}x".rjust(8)
            print(f"  │ {name} │ {r1h} │ {r6h} │ {r24h} │")
            
        print("  └──────────────────────────────────────────────────────────────────────────┘")
        print("  (1x = expected rate, >1x = consuming faster than expected)")
        
        # Generate SLA Report
        print("\n📄 Generating SLA Report...")
        
        report = platform.reporter.generate_report("sla_enterprise", days=30)
        
        if report:
            print(f"\n  Report ID: {report.report_id}")
            print(f"  Period: {report.period_start.strftime('%Y-%m-%d')} to {report.period_end.strftime('%Y-%m-%d')}")
            print(f"\n  Overall Compliance: {report.overall_compliance:.1f}%")
            
            print("\n  SLO Compliance:")
            for slo_name, compliance in report.slo_compliance.items():
                bar_len = int(compliance / 5)
                bar = "█" * bar_len + "░" * (20 - bar_len)
                print(f"    {slo_name[:20].ljust(20)}: {bar} {compliance:.1f}%")
                
            print(f"\n  Total Breaches: {report.total_breaches}")
            if report.credits_issued > 0:
                print(f"  Credits Issued: ${report.credits_issued:,.2f}")
                
        # Platform statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total SLIs: {stats['total_slis']}")
        print(f"  Total SLOs: {stats['total_slos']}")
        print(f"  Total SLAs: {stats['total_slas']}")
        print(f"  SLAs Healthy: {stats['slas_healthy']}")
        print(f"  SLAs At Risk: {stats['slas_at_risk']}")
        print(f"  SLAs Breached: {stats['slas_breached']}")
        print(f"  Total Breaches: {stats['total_breaches']}")
        
        # Dashboard
        print("\n┌────────────────────────────────────────────────────────────────────┐")
        print("│                    SLA Management Dashboard                        │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ SLIs Tracked:                {stats['total_slis']:>10}                       │")
        print(f"│ SLOs Defined:                {stats['total_slos']:>10}                       │")
        print(f"│ SLAs Active:                 {stats['total_slas']:>10}                       │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ 🟢 Healthy:                  {stats['slas_healthy']:>10}                       │")
        print(f"│ 🟡 At Risk:                  {stats['slas_at_risk']:>10}                       │")
        print(f"│ 🔴 Breached:                 {stats['slas_breached']:>10}                       │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Total Breaches:              {stats['total_breaches']:>10}                       │")
        print("└────────────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("SLA Management Platform initialized!")
    print("=" * 60)
