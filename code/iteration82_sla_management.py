#!/usr/bin/env python3
"""
Server Init - Iteration 82: SLA Management Platform
Платформа управления SLA

Функционал:
- SLA Definition - определение SLA
- SLO/SLI Tracking - отслеживание SLO/SLI
- Error Budgets - бюджеты ошибок
- SLA Reporting - отчётность SLA
- Breach Detection - обнаружение нарушений
- Alerting - алертинг SLA
- Customer SLAs - клиентские SLA
- Compliance Tracking - отслеживание соответствия
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
from collections import defaultdict
import uuid
import random


class SLIType(Enum):
    """Тип SLI"""
    AVAILABILITY = "availability"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    SATURATION = "saturation"
    CUSTOM = "custom"


class SLOStatus(Enum):
    """Статус SLO"""
    MET = "met"
    AT_RISK = "at_risk"
    BREACHED = "breached"


class TimeWindow(Enum):
    """Временное окно"""
    ROLLING_7_DAYS = "rolling_7_days"
    ROLLING_30_DAYS = "rolling_30_days"
    CALENDAR_MONTH = "calendar_month"
    CALENDAR_QUARTER = "calendar_quarter"


class SeverityLevel(Enum):
    """Уровень серьёзности"""
    WARNING = "warning"
    CRITICAL = "critical"
    BREACH = "breach"


@dataclass
class SLI:
    """Service Level Indicator"""
    sli_id: str
    name: str = ""
    description: str = ""
    
    # Тип
    sli_type: SLIType = SLIType.AVAILABILITY
    
    # Формула расчёта
    good_events_query: str = ""
    total_events_query: str = ""
    
    # Единица измерения
    unit: str = "%"
    
    # Источник данных
    data_source: str = ""
    
    # Текущее значение
    current_value: float = 100.0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class SLO:
    """Service Level Objective"""
    slo_id: str
    name: str = ""
    description: str = ""
    
    # SLI
    sli_id: str = ""
    
    # Цель
    target: float = 99.9  # 99.9%
    
    # Окно
    window: TimeWindow = TimeWindow.ROLLING_30_DAYS
    
    # Статус
    status: SLOStatus = SLOStatus.MET
    current_value: float = 100.0
    
    # Error budget
    error_budget_total: float = 0.0  # В минутах или процентах
    error_budget_remaining: float = 0.0
    error_budget_consumed_percent: float = 0.0
    
    # Пороги алертов
    warning_threshold_percent: float = 50.0  # 50% бюджета использовано
    critical_threshold_percent: float = 80.0
    
    # Время
    window_start: datetime = field(default_factory=datetime.now)
    window_end: Optional[datetime] = None
    
    # Метаданные
    owner: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class SLA:
    """Service Level Agreement"""
    sla_id: str
    name: str = ""
    description: str = ""
    
    # SLOs включённые в SLA
    slo_ids: List[str] = field(default_factory=list)
    
    # Клиент/контракт
    customer_id: str = ""
    contract_id: str = ""
    
    # Период действия
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    
    # Компенсации
    compensation_tiers: List[Dict[str, Any]] = field(default_factory=list)
    # [{"threshold": 99.0, "compensation_percent": 10}, ...]
    
    # Статус
    active: bool = True
    
    # Отчётность
    reporting_frequency: str = "monthly"  # daily, weekly, monthly
    
    # Метаданные
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SLAReport:
    """Отчёт по SLA"""
    report_id: str
    sla_id: str = ""
    
    # Период
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Результаты по SLO
    slo_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Общий статус
    overall_compliance: bool = True
    overall_score: float = 100.0
    
    # Нарушения
    breaches: List[Dict[str, Any]] = field(default_factory=list)
    
    # Компенсации
    compensation_due: float = 0.0
    
    # Время генерации
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Breach:
    """Нарушение SLA/SLO"""
    breach_id: str
    
    # Что нарушено
    slo_id: str = ""
    sla_id: str = ""
    
    # Детали
    target: float = 0.0
    actual: float = 0.0
    
    # Время
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    duration_minutes: int = 0
    
    # Причина
    reason: str = ""
    
    # Инцидент
    incident_id: str = ""
    
    # Статус
    acknowledged: bool = False
    resolved: bool = False


@dataclass
class ErrorBudget:
    """Error Budget"""
    budget_id: str
    slo_id: str = ""
    
    # Бюджет
    total_budget_minutes: float = 0.0
    consumed_minutes: float = 0.0
    remaining_minutes: float = 0.0
    
    # Процент
    consumed_percent: float = 0.0
    
    # Burn rate
    current_burn_rate: float = 0.0  # x быстрее нормы
    projected_exhaustion: Optional[datetime] = None
    
    # Период
    window_start: datetime = field(default_factory=datetime.now)
    window_end: Optional[datetime] = None


@dataclass 
class Measurement:
    """Измерение метрики"""
    measurement_id: str
    sli_id: str = ""
    
    # Значения
    good_events: int = 0
    total_events: int = 0
    value: float = 100.0
    
    # Время
    timestamp: datetime = field(default_factory=datetime.now)
    period_seconds: int = 60


class SLICollector:
    """Сборщик SLI"""
    
    def __init__(self):
        self.slis: Dict[str, SLI] = {}
        self.measurements: Dict[str, List[Measurement]] = defaultdict(list)
        
    def add_sli(self, sli: SLI):
        """Добавление SLI"""
        self.slis[sli.sli_id] = sli
        
    def record(self, sli_id: str, good_events: int, total_events: int):
        """Запись измерения"""
        sli = self.slis.get(sli_id)
        if not sli:
            return
            
        value = (good_events / total_events * 100) if total_events > 0 else 100.0
        
        measurement = Measurement(
            measurement_id=f"meas_{uuid.uuid4().hex[:8]}",
            sli_id=sli_id,
            good_events=good_events,
            total_events=total_events,
            value=value
        )
        
        self.measurements[sli_id].append(measurement)
        
        # Обновляем текущее значение SLI
        sli.current_value = value
        sli.last_updated = datetime.now()
        
    def get_sli_value(self, sli_id: str, window: TimeWindow) -> float:
        """Получение значения SLI за период"""
        measurements = self.measurements.get(sli_id, [])
        if not measurements:
            return 100.0
            
        # Определяем начало окна
        now = datetime.now()
        if window == TimeWindow.ROLLING_7_DAYS:
            start = now - timedelta(days=7)
        elif window == TimeWindow.ROLLING_30_DAYS:
            start = now - timedelta(days=30)
        else:
            start = now - timedelta(days=30)
            
        # Фильтруем измерения
        window_measurements = [m for m in measurements if m.timestamp >= start]
        
        if not window_measurements:
            return 100.0
            
        # Агрегируем
        total_good = sum(m.good_events for m in window_measurements)
        total_all = sum(m.total_events for m in window_measurements)
        
        return (total_good / total_all * 100) if total_all > 0 else 100.0


class SLOManager:
    """Менеджер SLO"""
    
    def __init__(self, collector: SLICollector):
        self.collector = collector
        self.slos: Dict[str, SLO] = {}
        self.error_budgets: Dict[str, ErrorBudget] = {}
        
    def add_slo(self, slo: SLO):
        """Добавление SLO"""
        self.slos[slo.slo_id] = slo
        self._init_error_budget(slo)
        
    def _init_error_budget(self, slo: SLO):
        """Инициализация error budget"""
        # Вычисляем бюджет в минутах
        window_minutes = self._get_window_minutes(slo.window)
        error_budget_minutes = window_minutes * (100 - slo.target) / 100
        
        budget = ErrorBudget(
            budget_id=f"budget_{uuid.uuid4().hex[:8]}",
            slo_id=slo.slo_id,
            total_budget_minutes=error_budget_minutes,
            remaining_minutes=error_budget_minutes,
            window_start=slo.window_start
        )
        
        self.error_budgets[slo.slo_id] = budget
        
    def _get_window_minutes(self, window: TimeWindow) -> float:
        """Получение длины окна в минутах"""
        if window == TimeWindow.ROLLING_7_DAYS:
            return 7 * 24 * 60
        elif window == TimeWindow.ROLLING_30_DAYS:
            return 30 * 24 * 60
        elif window == TimeWindow.CALENDAR_MONTH:
            return 30 * 24 * 60
        else:
            return 90 * 24 * 60
            
    def update_slo(self, slo_id: str):
        """Обновление статуса SLO"""
        slo = self.slos.get(slo_id)
        if not slo:
            return
            
        # Получаем текущее значение SLI
        current_value = self.collector.get_sli_value(slo.sli_id, slo.window)
        slo.current_value = current_value
        
        # Обновляем error budget
        budget = self.error_budgets.get(slo_id)
        if budget:
            # Вычисляем consumed
            window_minutes = self._get_window_minutes(slo.window)
            actual_uptime_minutes = window_minutes * current_value / 100
            downtime_minutes = window_minutes - actual_uptime_minutes
            
            budget.consumed_minutes = downtime_minutes
            budget.remaining_minutes = budget.total_budget_minutes - downtime_minutes
            budget.consumed_percent = (downtime_minutes / budget.total_budget_minutes * 100) if budget.total_budget_minutes > 0 else 0
            
            slo.error_budget_remaining = budget.remaining_minutes
            slo.error_budget_consumed_percent = budget.consumed_percent
            
        # Определяем статус
        if current_value >= slo.target:
            slo.status = SLOStatus.MET
        elif budget and budget.consumed_percent >= 100:
            slo.status = SLOStatus.BREACHED
        else:
            slo.status = SLOStatus.AT_RISK
            
    def get_burn_rate(self, slo_id: str) -> float:
        """Расчёт burn rate"""
        budget = self.error_budgets.get(slo_id)
        slo = self.slos.get(slo_id)
        
        if not budget or not slo:
            return 0.0
            
        # Сколько дней прошло
        elapsed = datetime.now() - slo.window_start
        elapsed_days = max(1, elapsed.days)
        
        # Нормальный burn rate = 100% / window_days
        window_days = self._get_window_minutes(slo.window) / (24 * 60)
        normal_rate = 100 / window_days  # % в день
        
        # Актуальный burn rate
        actual_rate = budget.consumed_percent / elapsed_days if elapsed_days > 0 else 0
        
        # Отношение
        return actual_rate / normal_rate if normal_rate > 0 else 0


class SLAManager:
    """Менеджер SLA"""
    
    def __init__(self, slo_manager: SLOManager):
        self.slo_manager = slo_manager
        self.slas: Dict[str, SLA] = {}
        self.reports: List[SLAReport] = []
        self.breaches: Dict[str, Breach] = {}
        
    def add_sla(self, sla: SLA):
        """Добавление SLA"""
        self.slas[sla.sla_id] = sla
        
    def check_compliance(self, sla_id: str) -> Dict[str, Any]:
        """Проверка соответствия SLA"""
        sla = self.slas.get(sla_id)
        if not sla:
            return {}
            
        results = {
            "sla_id": sla_id,
            "compliant": True,
            "slo_statuses": {}
        }
        
        for slo_id in sla.slo_ids:
            slo = self.slo_manager.slos.get(slo_id)
            if slo:
                self.slo_manager.update_slo(slo_id)
                
                results["slo_statuses"][slo_id] = {
                    "name": slo.name,
                    "target": slo.target,
                    "current": slo.current_value,
                    "status": slo.status.value,
                    "error_budget_consumed": slo.error_budget_consumed_percent
                }
                
                if slo.status == SLOStatus.BREACHED:
                    results["compliant"] = False
                    
        return results
        
    def calculate_compensation(self, sla_id: str, score: float) -> float:
        """Расчёт компенсации"""
        sla = self.slas.get(sla_id)
        if not sla or not sla.compensation_tiers:
            return 0.0
            
        for tier in sorted(sla.compensation_tiers, key=lambda x: x["threshold"], reverse=True):
            if score < tier["threshold"]:
                return tier["compensation_percent"]
                
        return 0.0
        
    def generate_report(self, sla_id: str, start: datetime, end: datetime) -> SLAReport:
        """Генерация отчёта"""
        sla = self.slas.get(sla_id)
        if not sla:
            raise ValueError(f"SLA {sla_id} not found")
            
        report = SLAReport(
            report_id=f"report_{uuid.uuid4().hex[:8]}",
            sla_id=sla_id,
            period_start=start,
            period_end=end
        )
        
        scores = []
        
        for slo_id in sla.slo_ids:
            slo = self.slo_manager.slos.get(slo_id)
            if slo:
                self.slo_manager.update_slo(slo_id)
                
                report.slo_results[slo_id] = {
                    "name": slo.name,
                    "target": slo.target,
                    "actual": slo.current_value,
                    "met": slo.current_value >= slo.target
                }
                
                scores.append(slo.current_value)
                
                if slo.status == SLOStatus.BREACHED:
                    report.overall_compliance = False
                    report.breaches.append({
                        "slo_id": slo_id,
                        "target": slo.target,
                        "actual": slo.current_value
                    })
                    
        report.overall_score = sum(scores) / len(scores) if scores else 100.0
        report.compensation_due = self.calculate_compensation(sla_id, report.overall_score)
        
        self.reports.append(report)
        return report
        
    def record_breach(self, slo_id: str, actual: float, reason: str = "") -> Breach:
        """Запись нарушения"""
        slo = self.slo_manager.slos.get(slo_id)
        if not slo:
            raise ValueError(f"SLO {slo_id} not found")
            
        breach = Breach(
            breach_id=f"breach_{uuid.uuid4().hex[:8]}",
            slo_id=slo_id,
            target=slo.target,
            actual=actual,
            reason=reason
        )
        
        self.breaches[breach.breach_id] = breach
        return breach


class SLAPlatform:
    """Платформа управления SLA"""
    
    def __init__(self):
        self.collector = SLICollector()
        self.slo_manager = SLOManager(self.collector)
        self.sla_manager = SLAManager(self.slo_manager)
        
    def create_sli(self, name: str, sli_type: SLIType = SLIType.AVAILABILITY,
                    **kwargs) -> SLI:
        """Создание SLI"""
        sli = SLI(
            sli_id=f"sli_{uuid.uuid4().hex[:8]}",
            name=name,
            sli_type=sli_type,
            **kwargs
        )
        self.collector.add_sli(sli)
        return sli
        
    def create_slo(self, name: str, sli_id: str, target: float = 99.9,
                    **kwargs) -> SLO:
        """Создание SLO"""
        slo = SLO(
            slo_id=f"slo_{uuid.uuid4().hex[:8]}",
            name=name,
            sli_id=sli_id,
            target=target,
            **kwargs
        )
        self.slo_manager.add_slo(slo)
        return slo
        
    def create_sla(self, name: str, slo_ids: List[str], **kwargs) -> SLA:
        """Создание SLA"""
        sla = SLA(
            sla_id=f"sla_{uuid.uuid4().hex[:8]}",
            name=name,
            slo_ids=slo_ids,
            **kwargs
        )
        self.sla_manager.add_sla(sla)
        return sla
        
    def record_measurement(self, sli_id: str, good_events: int, total_events: int):
        """Запись измерения"""
        self.collector.record(sli_id, good_events, total_events)
        
    def get_slo_status(self, slo_id: str) -> Dict[str, Any]:
        """Получение статуса SLO"""
        slo = self.slo_manager.slos.get(slo_id)
        if not slo:
            return {}
            
        self.slo_manager.update_slo(slo_id)
        budget = self.slo_manager.error_budgets.get(slo_id)
        
        return {
            "slo_id": slo_id,
            "name": slo.name,
            "target": slo.target,
            "current": slo.current_value,
            "status": slo.status.value,
            "error_budget": {
                "total_minutes": budget.total_budget_minutes if budget else 0,
                "consumed_minutes": budget.consumed_minutes if budget else 0,
                "remaining_minutes": budget.remaining_minutes if budget else 0,
                "consumed_percent": slo.error_budget_consumed_percent
            },
            "burn_rate": self.slo_manager.get_burn_rate(slo_id)
        }
        
    def generate_sla_report(self, sla_id: str, start: datetime = None,
                             end: datetime = None) -> SLAReport:
        """Генерация отчёта SLA"""
        start = start or datetime.now() - timedelta(days=30)
        end = end or datetime.now()
        return self.sla_manager.generate_report(sla_id, start, end)
        
    def get_stats(self) -> Dict[str, Any]:
        """Статистика"""
        slos_met = len([s for s in self.slo_manager.slos.values() if s.status == SLOStatus.MET])
        slos_at_risk = len([s for s in self.slo_manager.slos.values() if s.status == SLOStatus.AT_RISK])
        slos_breached = len([s for s in self.slo_manager.slos.values() if s.status == SLOStatus.BREACHED])
        
        return {
            "slis": len(self.collector.slis),
            "slos": len(self.slo_manager.slos),
            "slas": len(self.sla_manager.slas),
            "slos_met": slos_met,
            "slos_at_risk": slos_at_risk,
            "slos_breached": slos_breached,
            "reports_generated": len(self.sla_manager.reports),
            "total_breaches": len(self.sla_manager.breaches)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 82: SLA Management Platform")
    print("=" * 60)
    
    async def demo():
        platform = SLAPlatform()
        print("✓ SLA Management Platform created")
        
        # Создание SLI
        print("\n📊 Creating Service Level Indicators (SLIs)...")
        
        availability_sli = platform.create_sli(
            "API Availability",
            sli_type=SLIType.AVAILABILITY,
            description="Percentage of successful API requests",
            good_events_query="sum(http_requests_total{status!~'5..'})",
            total_events_query="sum(http_requests_total)",
            data_source="prometheus"
        )
        print(f"  ✓ {availability_sli.name}")
        
        latency_sli = platform.create_sli(
            "API Latency P99",
            sli_type=SLIType.LATENCY,
            description="99th percentile of API response time",
            unit="ms",
            data_source="prometheus"
        )
        print(f"  ✓ {latency_sli.name}")
        
        error_rate_sli = platform.create_sli(
            "Error Rate",
            sli_type=SLIType.ERROR_RATE,
            description="Percentage of failed requests",
            data_source="prometheus"
        )
        print(f"  ✓ {error_rate_sli.name}")
        
        # Создание SLO
        print("\n🎯 Creating Service Level Objectives (SLOs)...")
        
        availability_slo = platform.create_slo(
            "API Availability SLO",
            sli_id=availability_sli.sli_id,
            target=99.9,
            window=TimeWindow.ROLLING_30_DAYS,
            warning_threshold_percent=50,
            critical_threshold_percent=80,
            owner="platform-team",
            tags=["api", "availability", "critical"]
        )
        print(f"  ✓ {availability_slo.name}: {availability_slo.target}%")
        
        latency_slo = platform.create_slo(
            "API Latency SLO",
            sli_id=latency_sli.sli_id,
            target=99.0,  # 99% запросов < 200ms
            window=TimeWindow.ROLLING_30_DAYS,
            owner="platform-team",
            tags=["api", "latency"]
        )
        print(f"  ✓ {latency_slo.name}: {latency_slo.target}%")
        
        error_slo = platform.create_slo(
            "Error Rate SLO",
            sli_id=error_rate_sli.sli_id,
            target=99.5,  # < 0.5% errors
            window=TimeWindow.ROLLING_7_DAYS,
            owner="platform-team",
            tags=["api", "errors"]
        )
        print(f"  ✓ {error_slo.name}: {error_slo.target}%")
        
        # Создание SLA
        print("\n📋 Creating Service Level Agreements (SLAs)...")
        
        enterprise_sla = platform.create_sla(
            "Enterprise SLA",
            slo_ids=[availability_slo.slo_id, latency_slo.slo_id],
            customer_id="enterprise-corp",
            contract_id="ENT-2024-001",
            compensation_tiers=[
                {"threshold": 99.0, "compensation_percent": 10},
                {"threshold": 95.0, "compensation_percent": 25},
                {"threshold": 90.0, "compensation_percent": 50},
            ],
            reporting_frequency="monthly",
            metadata={"contract_value": 100000, "currency": "USD"}
        )
        print(f"  ✓ {enterprise_sla.name}")
        print(f"    Customer: {enterprise_sla.customer_id}")
        print(f"    SLOs: {len(enterprise_sla.slo_ids)}")
        
        standard_sla = platform.create_sla(
            "Standard SLA",
            slo_ids=[availability_slo.slo_id],
            customer_id="standard-customers",
            compensation_tiers=[
                {"threshold": 99.0, "compensation_percent": 5},
                {"threshold": 95.0, "compensation_percent": 15},
            ]
        )
        print(f"  ✓ {standard_sla.name}")
        
        # Симуляция измерений
        print("\n📈 Recording Measurements...")
        
        # Availability - хорошие результаты
        for _ in range(30):  # 30 дней
            good = random.randint(9980, 10000)
            total = 10000
            platform.record_measurement(availability_sli.sli_id, good, total)
            
        print(f"  ✓ Recorded 30 days of availability data")
        
        # Latency - в основном хорошие
        for _ in range(30):
            good = random.randint(9850, 9950)
            total = 10000
            platform.record_measurement(latency_sli.sli_id, good, total)
            
        print(f"  ✓ Recorded 30 days of latency data")
        
        # Error rate - некоторые проблемы
        for _ in range(7):
            good = random.randint(9900, 9980)
            total = 10000
            platform.record_measurement(error_rate_sli.sli_id, good, total)
            
        print(f"  ✓ Recorded 7 days of error rate data")
        
        # Проверка статуса SLO
        print("\n📊 SLO Status Dashboard:")
        
        for slo_id in [availability_slo.slo_id, latency_slo.slo_id, error_slo.slo_id]:
            status = platform.get_slo_status(slo_id)
            
            # Статус индикатор
            if status["status"] == "met":
                icon = "✅"
            elif status["status"] == "at_risk":
                icon = "⚠️"
            else:
                icon = "❌"
                
            print(f"\n  {icon} {status['name']}")
            print(f"     Target: {status['target']}%")
            print(f"     Current: {status['current']:.2f}%")
            print(f"     Status: {status['status'].upper()}")
            
            budget = status['error_budget']
            bar_length = 20
            consumed = int(budget['consumed_percent'] / 100 * bar_length)
            bar = "█" * consumed + "░" * (bar_length - consumed)
            
            print(f"     Error Budget: [{bar}] {budget['consumed_percent']:.1f}%")
            print(f"     Remaining: {budget['remaining_minutes']:.1f} minutes")
            print(f"     Burn Rate: {status['burn_rate']:.2f}x")
            
        # SLA Compliance
        print("\n📋 SLA Compliance Check:")
        
        compliance = platform.sla_manager.check_compliance(enterprise_sla.sla_id)
        
        status_icon = "✅" if compliance["compliant"] else "❌"
        print(f"\n  {status_icon} {enterprise_sla.name}")
        print(f"     Compliant: {compliance['compliant']}")
        
        print("     SLO Results:")
        for slo_id, result in compliance["slo_statuses"].items():
            met_icon = "✓" if result["current"] >= result["target"] else "✗"
            print(f"       {met_icon} {result['name']}: {result['current']:.2f}% (target: {result['target']}%)")
            
        # Генерация отчёта
        print("\n📄 Generating SLA Report...")
        
        report = platform.generate_sla_report(enterprise_sla.sla_id)
        
        print(f"\n  Report ID: {report.report_id}")
        print(f"  Period: {report.period_start.strftime('%Y-%m-%d')} to {report.period_end.strftime('%Y-%m-%d')}")
        print(f"  Overall Score: {report.overall_score:.2f}%")
        print(f"  Compliant: {report.overall_compliance}")
        
        if report.compensation_due > 0:
            print(f"  ⚠️ Compensation Due: {report.compensation_due}%")
        else:
            print(f"  ✓ No compensation due")
            
        print("\n  SLO Results:")
        for slo_id, result in report.slo_results.items():
            met = "✓" if result["met"] else "✗"
            print(f"    {met} {result['name']}: {result['actual']:.2f}% / {result['target']}%")
            
        # Симуляция breach
        print("\n⚠️ Simulating SLO Breach...")
        
        # Записываем плохие данные
        for _ in range(5):
            platform.record_measurement(availability_sli.sli_id, 9500, 10000)  # 95%
            
        status = platform.get_slo_status(availability_slo.slo_id)
        print(f"  Availability dropped to: {status['current']:.2f}%")
        print(f"  Status: {status['status'].upper()}")
        
        if status['status'] == 'breached':
            breach = platform.sla_manager.record_breach(
                availability_slo.slo_id,
                status['current'],
                reason="Infrastructure issues causing increased error rates"
            )
            print(f"  ❌ Breach recorded: {breach.breach_id}")
            
        # Повторная проверка compliance
        print("\n📋 Updated SLA Compliance:")
        
        compliance = platform.sla_manager.check_compliance(enterprise_sla.sla_id)
        status_icon = "✅" if compliance["compliant"] else "❌"
        print(f"  {status_icon} {enterprise_sla.name}: {'Compliant' if compliance['compliant'] else 'NOT Compliant'}")
        
        # Error Budget визуализация
        print("\n📊 Error Budget Summary:")
        
        for slo in platform.slo_manager.slos.values():
            budget = platform.slo_manager.error_budgets.get(slo.slo_id)
            if budget:
                remaining_pct = 100 - budget.consumed_percent
                
                # Цвет на основе remaining
                if remaining_pct > 50:
                    color = "🟢"
                elif remaining_pct > 20:
                    color = "🟡"
                else:
                    color = "🔴"
                    
                print(f"  {color} {slo.name}")
                print(f"     Total: {budget.total_budget_minutes:.0f} min")
                print(f"     Consumed: {budget.consumed_minutes:.0f} min ({budget.consumed_percent:.1f}%)")
                print(f"     Remaining: {budget.remaining_minutes:.0f} min ({remaining_pct:.1f}%)")
                
        # Platform Statistics
        print("\n📈 Platform Statistics:")
        stats = platform.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
        # Все SLA
        print("\n📋 All SLAs:")
        for sla in platform.sla_manager.slas.values():
            status = "Active" if sla.active else "Inactive"
            print(f"  • {sla.name} ({status})")
            print(f"    Customer: {sla.customer_id}")
            print(f"    SLOs: {len(sla.slo_ids)}")
            
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("SLA Management Platform initialized!")
    print("=" * 60)
