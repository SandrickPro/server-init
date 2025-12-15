#!/usr/bin/env python3
"""
Server Init - Iteration 306: SLA Manager Platform
Платформа управления SLA (Service Level Agreements)

Функционал:
- SLA Definition - определение SLA
- SLO Tracking - отслеживание целей
- SLI Monitoring - мониторинг индикаторов
- Error Budget - бюджет ошибок
- Breach Detection - обнаружение нарушений
- Reporting - отчётность
- Alerting - оповещения
- Compliance Tracking - отслеживание соответствия
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class SLAType(Enum):
    """Тип SLA"""
    AVAILABILITY = "availability"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    RESPONSE_TIME = "response_time"
    RESOLUTION_TIME = "resolution_time"


class SLAStatus(Enum):
    """Статус SLA"""
    HEALTHY = "healthy"
    WARNING = "warning"
    BREACHED = "breached"
    CRITICAL = "critical"


class TimeWindow(Enum):
    """Временное окно"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


@dataclass
class SLI:
    """Service Level Indicator"""
    sli_id: str
    name: str
    
    # Measurement
    metric_name: str = ""
    measurement_type: str = "ratio"  # ratio, average, percentile
    
    # Current value
    current_value: float = 0.0
    
    # History
    measurements: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timestamps
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class SLO:
    """Service Level Objective"""
    slo_id: str
    name: str
    
    # Target
    target_value: float = 99.9
    comparison: str = "gte"  # gte, lte, eq
    
    # SLI
    sli_id: str = ""
    
    # Time window
    window: TimeWindow = TimeWindow.MONTHLY
    
    # Current status
    current_value: float = 0.0
    status: SLAStatus = SLAStatus.HEALTHY
    
    # Error budget
    error_budget_total: float = 0.0
    error_budget_remaining: float = 0.0
    error_budget_consumed: float = 0.0


@dataclass
class SLA:
    """Service Level Agreement"""
    sla_id: str
    name: str
    description: str
    
    # Service
    service_id: str = ""
    service_name: str = ""
    
    # Type
    sla_type: SLAType = SLAType.AVAILABILITY
    
    # SLOs
    slo_ids: List[str] = field(default_factory=list)
    
    # Contract
    customer: str = ""
    contract_start: Optional[datetime] = None
    contract_end: Optional[datetime] = None
    
    # Penalties
    penalty_per_breach: float = 0.0
    max_penalty: float = 0.0
    
    # Status
    status: SLAStatus = SLAStatus.HEALTHY
    
    # History
    breach_count: int = 0
    total_penalties: float = 0.0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Breach:
    """Нарушение SLA"""
    breach_id: str
    sla_id: str
    slo_id: str
    
    # Details
    target_value: float = 0.0
    actual_value: float = 0.0
    deviation: float = 0.0
    
    # Impact
    duration_minutes: int = 0
    affected_users: int = 0
    
    # Penalty
    penalty_amount: float = 0.0
    
    # Status
    acknowledged: bool = False
    root_cause: str = ""
    
    # Timestamps
    occurred_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


@dataclass
class ErrorBudget:
    """Бюджет ошибок"""
    budget_id: str
    slo_id: str
    
    # Budget
    total_minutes: float = 0.0
    consumed_minutes: float = 0.0
    remaining_minutes: float = 0.0
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Status
    burn_rate: float = 0.0  # consumption rate
    projected_exhaustion: Optional[datetime] = None


@dataclass
class Report:
    """Отчёт SLA"""
    report_id: str
    sla_id: str
    
    # Period
    period_start: datetime
    period_end: datetime
    
    # Metrics
    uptime_percentage: float = 0.0
    breaches_count: int = 0
    total_downtime_minutes: int = 0
    
    # Financial
    penalty_amount: float = 0.0
    credit_amount: float = 0.0
    
    # Trends
    trend: str = "stable"  # improving, stable, degrading
    
    # Generated
    generated_at: datetime = field(default_factory=datetime.now)


class SLAManager:
    """Менеджер SLA"""
    
    def __init__(self):
        self.slas: Dict[str, SLA] = {}
        self.slos: Dict[str, SLO] = {}
        self.slis: Dict[str, SLI] = {}
        self.breaches: Dict[str, Breach] = {}
        self.error_budgets: Dict[str, ErrorBudget] = {}
        self.reports: Dict[str, Report] = {}
        
    async def create_sli(self, name: str, metric_name: str,
                        measurement_type: str = "ratio") -> SLI:
        """Создание SLI"""
        sli = SLI(
            sli_id=f"sli_{uuid.uuid4().hex[:8]}",
            name=name,
            metric_name=metric_name,
            measurement_type=measurement_type
        )
        
        self.slis[sli.sli_id] = sli
        return sli
        
    async def create_slo(self, name: str, sli_id: str,
                        target_value: float,
                        comparison: str = "gte",
                        window: TimeWindow = TimeWindow.MONTHLY) -> Optional[SLO]:
        """Создание SLO"""
        sli = self.slis.get(sli_id)
        if not sli:
            return None
            
        slo = SLO(
            slo_id=f"slo_{uuid.uuid4().hex[:8]}",
            name=name,
            target_value=target_value,
            comparison=comparison,
            sli_id=sli_id,
            window=window
        )
        
        # Calculate error budget
        if target_value >= 99.0:
            error_budget_percent = 100.0 - target_value
            if window == TimeWindow.MONTHLY:
                total_minutes = 30 * 24 * 60
            elif window == TimeWindow.WEEKLY:
                total_minutes = 7 * 24 * 60
            else:
                total_minutes = 24 * 60
                
            slo.error_budget_total = total_minutes * (error_budget_percent / 100.0)
            slo.error_budget_remaining = slo.error_budget_total
            
        self.slos[slo.slo_id] = slo
        return slo
        
    async def create_sla(self, name: str, description: str,
                        service_name: str,
                        sla_type: SLAType,
                        slo_ids: List[str],
                        customer: str = "",
                        penalty_per_breach: float = 0.0) -> SLA:
        """Создание SLA"""
        sla = SLA(
            sla_id=f"sla_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            service_name=service_name,
            sla_type=sla_type,
            slo_ids=slo_ids,
            customer=customer,
            penalty_per_breach=penalty_per_breach,
            contract_start=datetime.now(),
            contract_end=datetime.now() + timedelta(days=365)
        )
        
        self.slas[sla.sla_id] = sla
        return sla
        
    async def record_measurement(self, sli_id: str, value: float) -> bool:
        """Запись измерения"""
        sli = self.slis.get(sli_id)
        if not sli:
            return False
            
        sli.current_value = value
        sli.measurements.append({
            "timestamp": datetime.now().isoformat(),
            "value": value
        })
        sli.last_updated = datetime.now()
        
        # Keep only last 1000 measurements
        if len(sli.measurements) > 1000:
            sli.measurements = sli.measurements[-1000:]
            
        # Update related SLOs
        await self._update_slos_for_sli(sli_id)
        
        return True
        
    async def _update_slos_for_sli(self, sli_id: str):
        """Обновление SLO для SLI"""
        sli = self.slis.get(sli_id)
        if not sli:
            return
            
        for slo in self.slos.values():
            if slo.sli_id != sli_id:
                continue
                
            slo.current_value = sli.current_value
            
            # Check status
            is_meeting = False
            if slo.comparison == "gte":
                is_meeting = slo.current_value >= slo.target_value
            elif slo.comparison == "lte":
                is_meeting = slo.current_value <= slo.target_value
            else:
                is_meeting = slo.current_value == slo.target_value
                
            # Update status
            if is_meeting:
                buffer = abs(slo.current_value - slo.target_value)
                if buffer < 0.1:
                    slo.status = SLAStatus.WARNING
                else:
                    slo.status = SLAStatus.HEALTHY
            else:
                slo.status = SLAStatus.BREACHED
                
                # Record breach for related SLAs
                for sla in self.slas.values():
                    if slo.slo_id in sla.slo_ids:
                        await self._record_breach(sla, slo)
                        
    async def _record_breach(self, sla: SLA, slo: SLO):
        """Запись нарушения"""
        breach = Breach(
            breach_id=f"br_{uuid.uuid4().hex[:8]}",
            sla_id=sla.sla_id,
            slo_id=slo.slo_id,
            target_value=slo.target_value,
            actual_value=slo.current_value,
            deviation=abs(slo.target_value - slo.current_value),
            penalty_amount=sla.penalty_per_breach
        )
        
        self.breaches[breach.breach_id] = breach
        sla.breach_count += 1
        sla.total_penalties += breach.penalty_amount
        sla.status = SLAStatus.BREACHED
        
        # Consume error budget
        if slo.error_budget_remaining > 0:
            consumption = 5.0  # 5 minutes per breach (example)
            slo.error_budget_consumed += consumption
            slo.error_budget_remaining = max(0, slo.error_budget_total - slo.error_budget_consumed)
            
    async def create_error_budget(self, slo_id: str,
                                 period_days: int = 30) -> Optional[ErrorBudget]:
        """Создание бюджета ошибок"""
        slo = self.slos.get(slo_id)
        if not slo:
            return None
            
        now = datetime.now()
        
        budget = ErrorBudget(
            budget_id=f"eb_{uuid.uuid4().hex[:8]}",
            slo_id=slo_id,
            total_minutes=slo.error_budget_total,
            remaining_minutes=slo.error_budget_remaining,
            consumed_minutes=slo.error_budget_consumed,
            period_start=now,
            period_end=now + timedelta(days=period_days)
        )
        
        # Calculate burn rate
        if slo.error_budget_total > 0:
            budget.burn_rate = slo.error_budget_consumed / slo.error_budget_total
            
            # Project exhaustion
            if budget.burn_rate > 0:
                days_remaining = period_days * (1 - budget.burn_rate)
                budget.projected_exhaustion = now + timedelta(days=days_remaining)
                
        self.error_budgets[budget.budget_id] = budget
        return budget
        
    async def acknowledge_breach(self, breach_id: str,
                                root_cause: str = "") -> bool:
        """Подтверждение нарушения"""
        breach = self.breaches.get(breach_id)
        if not breach:
            return False
            
        breach.acknowledged = True
        breach.root_cause = root_cause
        
        return True
        
    async def resolve_breach(self, breach_id: str) -> bool:
        """Разрешение нарушения"""
        breach = self.breaches.get(breach_id)
        if not breach:
            return False
            
        breach.resolved_at = datetime.now()
        
        if breach.occurred_at:
            breach.duration_minutes = int((breach.resolved_at - breach.occurred_at).total_seconds() / 60)
            
        return True
        
    async def generate_report(self, sla_id: str,
                             period_days: int = 30) -> Optional[Report]:
        """Генерация отчёта"""
        sla = self.slas.get(sla_id)
        if not sla:
            return None
            
        now = datetime.now()
        period_start = now - timedelta(days=period_days)
        
        # Count breaches in period
        period_breaches = [
            b for b in self.breaches.values()
            if b.sla_id == sla_id and b.occurred_at >= period_start
        ]
        
        # Calculate metrics
        total_downtime = sum(b.duration_minutes for b in period_breaches if b.duration_minutes)
        total_minutes = period_days * 24 * 60
        uptime = ((total_minutes - total_downtime) / total_minutes) * 100
        
        total_penalty = sum(b.penalty_amount for b in period_breaches)
        
        # Determine trend
        mid_point = period_start + timedelta(days=period_days // 2)
        first_half = sum(1 for b in period_breaches if b.occurred_at < mid_point)
        second_half = len(period_breaches) - first_half
        
        if second_half < first_half:
            trend = "improving"
        elif second_half > first_half:
            trend = "degrading"
        else:
            trend = "stable"
            
        report = Report(
            report_id=f"rpt_{uuid.uuid4().hex[:8]}",
            sla_id=sla_id,
            period_start=period_start,
            period_end=now,
            uptime_percentage=uptime,
            breaches_count=len(period_breaches),
            total_downtime_minutes=total_downtime,
            penalty_amount=total_penalty,
            trend=trend
        )
        
        self.reports[report.report_id] = report
        return report
        
    def get_sla_status(self, sla_id: str) -> Dict[str, Any]:
        """Получение статуса SLA"""
        sla = self.slas.get(sla_id)
        if not sla:
            return {}
            
        slos_status = []
        for slo_id in sla.slo_ids:
            slo = self.slos.get(slo_id)
            if slo:
                sli = self.slis.get(slo.sli_id)
                slos_status.append({
                    "name": slo.name,
                    "target": slo.target_value,
                    "current": slo.current_value,
                    "status": slo.status.value,
                    "error_budget_remaining": slo.error_budget_remaining,
                    "sli_name": sli.name if sli else "Unknown"
                })
                
        # Recent breaches
        recent_breaches = [
            b for b in self.breaches.values()
            if b.sla_id == sla_id
        ][-5:]
        
        return {
            "sla_id": sla_id,
            "name": sla.name,
            "service": sla.service_name,
            "type": sla.sla_type.value,
            "status": sla.status.value,
            "customer": sla.customer,
            "breach_count": sla.breach_count,
            "total_penalties": sla.total_penalties,
            "slos": slos_status,
            "recent_breaches": len(recent_breaches),
            "contract_end": sla.contract_end.isoformat() if sla.contract_end else None
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        healthy = sum(1 for s in self.slas.values() if s.status == SLAStatus.HEALTHY)
        warning = sum(1 for s in self.slas.values() if s.status == SLAStatus.WARNING)
        breached = sum(1 for s in self.slas.values() if s.status == SLAStatus.BREACHED)
        
        total_penalties = sum(s.total_penalties for s in self.slas.values())
        
        # Average SLO compliance
        meeting_target = sum(1 for slo in self.slos.values() if slo.current_value >= slo.target_value)
        compliance_rate = (meeting_target / max(len(self.slos), 1)) * 100
        
        # Error budget status
        budgets_exhausted = sum(
            1 for slo in self.slos.values() 
            if slo.error_budget_remaining <= 0 and slo.error_budget_total > 0
        )
        
        return {
            "total_slas": len(self.slas),
            "healthy_slas": healthy,
            "warning_slas": warning,
            "breached_slas": breached,
            "total_slos": len(self.slos),
            "total_slis": len(self.slis),
            "total_breaches": len(self.breaches),
            "unresolved_breaches": sum(1 for b in self.breaches.values() if not b.resolved_at),
            "total_penalties": total_penalties,
            "compliance_rate": compliance_rate,
            "error_budgets_exhausted": budgets_exhausted,
            "total_reports": len(self.reports)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 306: SLA Manager Platform")
    print("=" * 60)
    
    manager = SLAManager()
    print("✓ SLA Manager created")
    
    # Create SLIs
    print("\n📊 Creating Service Level Indicators...")
    
    slis_data = [
        ("API Availability", "api_uptime_ratio", "ratio"),
        ("API Latency P95", "api_latency_p95_ms", "percentile"),
        ("Error Rate", "error_rate_percent", "ratio"),
        ("Database Availability", "db_uptime_ratio", "ratio"),
        ("Request Throughput", "requests_per_second", "average")
    ]
    
    slis = []
    for name, metric, m_type in slis_data:
        sli = await manager.create_sli(name, metric, m_type)
        slis.append(sli)
        print(f"  📊 {name} ({metric})")
        
    # Create SLOs
    print("\n🎯 Creating Service Level Objectives...")
    
    slos_data = [
        ("API Availability Target", slis[0].sli_id, 99.95, "gte", TimeWindow.MONTHLY),
        ("API Latency Target", slis[1].sli_id, 200.0, "lte", TimeWindow.WEEKLY),
        ("Error Rate Target", slis[2].sli_id, 0.1, "lte", TimeWindow.DAILY),
        ("Database Availability", slis[3].sli_id, 99.99, "gte", TimeWindow.MONTHLY),
        ("Throughput Minimum", slis[4].sli_id, 1000.0, "gte", TimeWindow.HOURLY)
    ]
    
    slos = []
    for name, sli_id, target, comp, window in slos_data:
        slo = await manager.create_slo(name, sli_id, target, comp, window)
        slos.append(slo)
        print(f"  🎯 {name}: {target} ({window.value})")
        
    # Create SLAs
    print("\n📋 Creating Service Level Agreements...")
    
    slas_data = [
        ("Enterprise API SLA", "API availability and performance guarantee", "API Gateway",
         SLAType.AVAILABILITY, [slos[0].slo_id, slos[1].slo_id], "Acme Corp", 5000.0),
        ("Database SLA", "Database uptime commitment", "Primary Database",
         SLAType.AVAILABILITY, [slos[3].slo_id], "Internal", 0.0),
        ("Platform SLA", "Overall platform performance", "Platform Services",
         SLAType.RESPONSE_TIME, [slos[0].slo_id, slos[2].slo_id, slos[4].slo_id], "Beta Inc", 10000.0)
    ]
    
    slas = []
    for name, desc, service, sla_type, slo_ids, customer, penalty in slas_data:
        sla = await manager.create_sla(name, desc, service, sla_type, slo_ids, customer, penalty)
        slas.append(sla)
        print(f"  📋 {name} ({customer})")
        
    # Record measurements
    print("\n📈 Recording Measurements...")
    
    measurements = [
        (slis[0], 99.97),  # API Availability
        (slis[1], 185.0),  # API Latency
        (slis[2], 0.08),   # Error Rate
        (slis[3], 99.995), # DB Availability
        (slis[4], 1250.0)  # Throughput
    ]
    
    for sli, value in measurements:
        await manager.record_measurement(sli.sli_id, value)
        print(f"  📈 {sli.name}: {value}")
        
    # Simulate some breaches
    print("\n⚠️ Simulating SLA Breaches...")
    
    # Record a breach scenario
    await manager.record_measurement(slis[0].sli_id, 99.90)  # Below 99.95
    print(f"  ⚠️ API Availability dropped to 99.90%")
    
    await manager.record_measurement(slis[1].sli_id, 250.0)  # Above 200ms
    print(f"  ⚠️ API Latency increased to 250ms")
    
    # Acknowledge breaches
    print("\n✅ Acknowledging Breaches...")
    
    for breach in list(manager.breaches.values())[:2]:
        await manager.acknowledge_breach(
            breach.breach_id,
            "Infrastructure scaling issue during peak traffic"
        )
        await manager.resolve_breach(breach.breach_id)
        
        sla = manager.slas.get(breach.sla_id)
        print(f"  ✅ Breach acknowledged for {sla.name if sla else 'Unknown'}")
        
    # Create error budgets
    print("\n💰 Creating Error Budgets...")
    
    for slo in slos[:3]:
        budget = await manager.create_error_budget(slo.slo_id, 30)
        if budget:
            print(f"  💰 {slo.name}")
            print(f"     Total: {budget.total_minutes:.1f}min | Remaining: {budget.remaining_minutes:.1f}min")
            
    # Generate reports
    print("\n📊 Generating Reports...")
    
    for sla in slas:
        report = await manager.generate_report(sla.sla_id, 30)
        if report:
            print(f"\n  📊 {sla.name}")
            print(f"     Uptime: {report.uptime_percentage:.3f}%")
            print(f"     Breaches: {report.breaches_count}")
            print(f"     Downtime: {report.total_downtime_minutes}min")
            print(f"     Trend: {report.trend}")
            
    # SLA Status
    print("\n📋 SLA Status:")
    
    for sla in slas:
        status = manager.get_sla_status(sla.sla_id)
        
        status_icons = {"healthy": "🟢", "warning": "🟡", "breached": "🔴", "critical": "⚫"}
        
        print(f"\n  {status_icons.get(status['status'], '⚪')} {status['name']}")
        print(f"     Service: {status['service']} | Customer: {status['customer']}")
        print(f"     Breaches: {status['breach_count']} | Penalties: ${status['total_penalties']:,.2f}")
        
        if status['slos']:
            print(f"     SLOs:")
            for slo_status in status['slos']:
                slo_icon = status_icons.get(slo_status['status'], '⚪')
                print(f"       {slo_icon} {slo_status['name']}: {slo_status['current']:.2f} (target: {slo_status['target']})")
                
    # SLA Dashboard
    print("\n📊 SLA Dashboard:")
    
    print("\n  ┌─────────────────────────────┬────────────┬──────────┬──────────┬─────────────┐")
    print("  │ SLA                         │ Status     │ Breaches │ Penalty  │ Customer    │")
    print("  ├─────────────────────────────┼────────────┼──────────┼──────────┼─────────────┤")
    
    for sla in slas:
        name = sla.name[:27].ljust(27)
        
        status_icons = {"healthy": "🟢", "warning": "🟡", "breached": "🔴", "critical": "⚫"}
        status = f"{status_icons.get(sla.status.value, '⚪')} {sla.status.value[:8]}".ljust(10)
        
        breaches = str(sla.breach_count).ljust(8)
        penalty = f"${sla.total_penalties:,.0f}".ljust(8)
        customer = sla.customer[:11].ljust(11)
        
        print(f"  │ {name} │ {status} │ {breaches} │ {penalty} │ {customer} │")
        
    print("  └─────────────────────────────┴────────────┴──────────┴──────────┴─────────────┘")
    
    # SLO Performance
    print("\n📊 SLO Performance:")
    
    print("\n  ┌─────────────────────────────┬──────────┬──────────┬──────────────────────┐")
    print("  │ SLO                         │ Target   │ Current  │ Error Budget         │")
    print("  ├─────────────────────────────┼──────────┼──────────┼──────────────────────┤")
    
    for slo in slos:
        name = slo.name[:27].ljust(27)
        target = f"{slo.target_value}".ljust(8)
        current = f"{slo.current_value:.2f}".ljust(8)
        
        if slo.error_budget_total > 0:
            remaining_pct = (slo.error_budget_remaining / slo.error_budget_total) * 100
            budget_bar = "█" * int(remaining_pct / 10) + "░" * (10 - int(remaining_pct / 10))
            budget = f"[{budget_bar}] {remaining_pct:.0f}%"
        else:
            budget = "N/A".ljust(20)
            
        print(f"  │ {name} │ {target} │ {current} │ {budget} │")
        
    print("  └─────────────────────────────┴──────────┴──────────┴──────────────────────┘")
    
    # Statistics
    print("\n📊 SLA Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Total SLAs: {stats['total_slas']}")
    print(f"    Healthy: {stats['healthy_slas']}")
    print(f"    Warning: {stats['warning_slas']}")
    print(f"    Breached: {stats['breached_slas']}")
    
    print(f"\n  Total SLOs: {stats['total_slos']}")
    print(f"  Total SLIs: {stats['total_slis']}")
    print(f"\n  Total Breaches: {stats['total_breaches']}")
    print(f"  Unresolved: {stats['unresolved_breaches']}")
    print(f"\n  Total Penalties: ${stats['total_penalties']:,.2f}")
    print(f"  Compliance Rate: {stats['compliance_rate']:.1f}%")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                       SLA Manager Dashboard                         │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total SLAs:                  {stats['total_slas']:>12}                          │")
    print(f"│ Healthy SLAs:                {stats['healthy_slas']:>12}                          │")
    print(f"│ Total Breaches:              {stats['total_breaches']:>12}                          │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Compliance Rate:             {stats['compliance_rate']:>11.1f}%                          │")
    print(f"│ Total Penalties:             ${stats['total_penalties']:>11,.2f}                         │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("SLA Manager Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
