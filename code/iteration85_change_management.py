#!/usr/bin/env python3
"""
Server Init - Iteration 85: Change Management Platform
Платформа управления изменениями

Функционал:
- Change Request Management - управление запросами на изменение
- Change Advisory Board - консультационный совет по изменениям
- Impact Assessment - оценка влияния
- Change Calendar - календарь изменений
- Approval Workflows - workflow согласования
- Risk Analysis - анализ рисков
- Rollback Planning - планирование отката
- Change Audit - аудит изменений
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Tuple
from enum import Enum
from collections import defaultdict
import uuid
import random


class ChangeType(Enum):
    """Тип изменения"""
    STANDARD = "standard"  # Предварительно одобренное, низкий риск
    NORMAL = "normal"  # Требует одобрения CAB
    EMERGENCY = "emergency"  # Срочное, ускоренное одобрение
    MAJOR = "major"  # Крупное изменение


class ChangeCategory(Enum):
    """Категория изменения"""
    INFRASTRUCTURE = "infrastructure"
    APPLICATION = "application"
    DATABASE = "database"
    NETWORK = "network"
    SECURITY = "security"
    CONFIGURATION = "configuration"


class ChangeStatus(Enum):
    """Статус изменения"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"


class RiskLevel(Enum):
    """Уровень риска"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ApprovalStatus(Enum):
    """Статус одобрения"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ABSTAINED = "abstained"


@dataclass
class Approver:
    """Согласователь"""
    approver_id: str
    name: str = ""
    email: str = ""
    role: str = ""  # CAB member, Manager, Security, etc.
    
    # Статус
    status: ApprovalStatus = ApprovalStatus.PENDING
    decision_at: Optional[datetime] = None
    comments: str = ""


@dataclass
class ImpactAssessment:
    """Оценка влияния"""
    assessment_id: str
    
    # Затронутые системы
    affected_systems: List[str] = field(default_factory=list)
    affected_services: List[str] = field(default_factory=list)
    affected_users: int = 0
    
    # Влияние на бизнес
    business_impact: str = ""  # low, medium, high, critical
    
    # Время простоя
    expected_downtime_minutes: int = 0
    downtime_window: str = ""  # "02:00-04:00 UTC"
    
    # Зависимости
    dependencies: List[str] = field(default_factory=list)
    
    # Уведомления
    notification_required: bool = False
    notification_list: List[str] = field(default_factory=list)


@dataclass
class RollbackPlan:
    """План отката"""
    plan_id: str
    
    # Описание
    description: str = ""
    
    # Шаги отката
    steps: List[Dict[str, Any]] = field(default_factory=list)
    # [{"order": 1, "action": "...", "command": "...", "estimated_time": 5}]
    
    # Время на откат
    estimated_rollback_time_minutes: int = 0
    
    # Триггеры отката
    rollback_triggers: List[str] = field(default_factory=list)
    # ["Error rate > 5%", "Latency > 500ms", "Manual decision"]
    
    # Проверка отката
    verification_steps: List[str] = field(default_factory=list)


@dataclass
class ChangeRequest:
    """Запрос на изменение"""
    change_id: str
    title: str = ""
    description: str = ""
    
    # Тип и категория
    change_type: ChangeType = ChangeType.NORMAL
    category: ChangeCategory = ChangeCategory.APPLICATION
    
    # Статус
    status: ChangeStatus = ChangeStatus.DRAFT
    
    # Риск
    risk_level: RiskLevel = RiskLevel.MEDIUM
    
    # Расписание
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    
    # Фактическое время
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    
    # Владелец
    requestor: str = ""
    implementer: str = ""
    
    # Оценка влияния
    impact_assessment: Optional[ImpactAssessment] = None
    
    # План отката
    rollback_plan: Optional[RollbackPlan] = None
    
    # Согласователи
    approvers: List[Approver] = field(default_factory=list)
    
    # Связанные элементы
    related_incidents: List[str] = field(default_factory=list)
    related_changes: List[str] = field(default_factory=list)
    
    # Причина (для emergency)
    justification: str = ""
    
    # Результат
    implementation_notes: str = ""
    post_implementation_review: str = ""
    success: Optional[bool] = None
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Теги
    tags: List[str] = field(default_factory=list)


@dataclass
class ChangeWindow:
    """Окно изменений"""
    window_id: str
    name: str = ""
    
    # Расписание
    day_of_week: List[int] = field(default_factory=list)  # 0=Mon, 6=Sun
    start_time: str = ""  # "02:00"
    end_time: str = ""  # "06:00"
    timezone: str = "UTC"
    
    # Тип окна
    environment: str = "production"  # production, staging, all
    allowed_change_types: List[ChangeType] = field(default_factory=list)
    
    # Ограничения
    max_concurrent_changes: int = 3
    
    # Активность
    is_active: bool = True


@dataclass
class ChangeFreeze:
    """Заморозка изменений"""
    freeze_id: str
    name: str = ""
    reason: str = ""
    
    # Период
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    
    # Исключения
    exceptions: List[ChangeType] = field(default_factory=list)  # Emergency всегда разрешен
    
    # Статус
    is_active: bool = True


@dataclass
class AuditEntry:
    """Запись аудита"""
    entry_id: str
    change_id: str = ""
    
    # Действие
    action: str = ""  # created, submitted, approved, rejected, started, completed
    
    # Кто и когда
    actor: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Детали
    details: str = ""
    previous_status: str = ""
    new_status: str = ""


class RiskCalculator:
    """Калькулятор рисков"""
    
    def calculate(self, change: ChangeRequest) -> RiskLevel:
        """Расчёт уровня риска"""
        score = 0
        
        # Категория
        category_scores = {
            ChangeCategory.INFRASTRUCTURE: 3,
            ChangeCategory.DATABASE: 3,
            ChangeCategory.NETWORK: 3,
            ChangeCategory.SECURITY: 2,
            ChangeCategory.APPLICATION: 1,
            ChangeCategory.CONFIGURATION: 1
        }
        score += category_scores.get(change.category, 1)
        
        # Влияние
        if change.impact_assessment:
            impact = change.impact_assessment
            
            # Количество пользователей
            if impact.affected_users > 10000:
                score += 3
            elif impact.affected_users > 1000:
                score += 2
            elif impact.affected_users > 100:
                score += 1
                
            # Время простоя
            if impact.expected_downtime_minutes > 60:
                score += 3
            elif impact.expected_downtime_minutes > 15:
                score += 2
            elif impact.expected_downtime_minutes > 0:
                score += 1
                
            # Бизнес-влияние
            if impact.business_impact == "critical":
                score += 4
            elif impact.business_impact == "high":
                score += 2
            elif impact.business_impact == "medium":
                score += 1
                
        # План отката
        if not change.rollback_plan or not change.rollback_plan.steps:
            score += 2  # Нет плана отката = выше риск
            
        # Определение уровня
        if score >= 10:
            return RiskLevel.CRITICAL
        elif score >= 6:
            return RiskLevel.HIGH
        elif score >= 3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW


class ApprovalWorkflow:
    """Workflow согласования"""
    
    def __init__(self):
        # Правила: change_type -> list of required approvers
        self.rules: Dict[ChangeType, List[str]] = {
            ChangeType.STANDARD: [],  # Не требует согласования
            ChangeType.NORMAL: ["tech_lead", "cab_member"],
            ChangeType.EMERGENCY: ["on_call_manager"],
            ChangeType.MAJOR: ["tech_lead", "cab_member", "security", "director"]
        }
        
    def get_required_approvers(self, change: ChangeRequest) -> List[str]:
        """Получение списка требуемых согласователей"""
        roles = self.rules.get(change.change_type, ["tech_lead"])
        
        # Для высокого риска добавляем security
        if change.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            if "security" not in roles:
                roles = roles + ["security"]
                
        return roles
        
    def is_approved(self, change: ChangeRequest) -> bool:
        """Проверка, одобрено ли изменение"""
        if change.change_type == ChangeType.STANDARD:
            return True
            
        required = set(self.get_required_approvers(change))
        
        approved_roles = set()
        for approver in change.approvers:
            if approver.status == ApprovalStatus.APPROVED:
                approved_roles.add(approver.role)
                
        return required.issubset(approved_roles)
        
    def has_rejections(self, change: ChangeRequest) -> bool:
        """Проверка наличия отклонений"""
        return any(a.status == ApprovalStatus.REJECTED for a in change.approvers)


class ChangeCalendar:
    """Календарь изменений"""
    
    def __init__(self):
        self.windows: Dict[str, ChangeWindow] = {}
        self.freezes: Dict[str, ChangeFreeze] = {}
        self.scheduled_changes: Dict[str, ChangeRequest] = {}
        
    def add_window(self, name: str, days: List[int], start: str, end: str,
                    environment: str = "production") -> ChangeWindow:
        """Добавление окна изменений"""
        window = ChangeWindow(
            window_id=f"win_{uuid.uuid4().hex[:8]}",
            name=name,
            day_of_week=days,
            start_time=start,
            end_time=end,
            environment=environment
        )
        self.windows[window.window_id] = window
        return window
        
    def add_freeze(self, name: str, start: datetime, end: datetime, reason: str) -> ChangeFreeze:
        """Добавление заморозки"""
        freeze = ChangeFreeze(
            freeze_id=f"frz_{uuid.uuid4().hex[:8]}",
            name=name,
            reason=reason,
            start_date=start,
            end_date=end
        )
        self.freezes[freeze.freeze_id] = freeze
        return freeze
        
    def is_in_freeze(self, dt: datetime = None) -> Tuple[bool, Optional[ChangeFreeze]]:
        """Проверка заморозки"""
        dt = dt or datetime.now()
        
        for freeze in self.freezes.values():
            if not freeze.is_active:
                continue
            if freeze.start_date <= dt <= (freeze.end_date or datetime.max):
                return True, freeze
                
        return False, None
        
    def is_in_change_window(self, dt: datetime = None, 
                             change_type: ChangeType = ChangeType.NORMAL) -> bool:
        """Проверка окна изменений"""
        dt = dt or datetime.now()
        
        # Emergency всегда разрешён
        if change_type == ChangeType.EMERGENCY:
            return True
            
        # Проверяем заморозку
        in_freeze, freeze = self.is_in_freeze(dt)
        if in_freeze:
            if change_type not in (freeze.exceptions if freeze else []):
                return False
                
        # Проверяем окна
        day = dt.weekday()
        time_str = dt.strftime("%H:%M")
        
        for window in self.windows.values():
            if not window.is_active:
                continue
            if day not in window.day_of_week:
                continue
            if window.start_time <= time_str <= window.end_time:
                return True
                
        return False
        
    def get_next_window(self, from_dt: datetime = None) -> Optional[Tuple[datetime, ChangeWindow]]:
        """Получение следующего окна"""
        from_dt = from_dt or datetime.now()
        
        next_windows = []
        
        for window in self.windows.values():
            if not window.is_active:
                continue
                
            # Находим ближайший день недели из списка
            current_day = from_dt.weekday()
            
            for target_day in sorted(window.day_of_week):
                days_ahead = target_day - current_day
                if days_ahead <= 0:
                    days_ahead += 7
                    
                next_date = from_dt + timedelta(days=days_ahead)
                # Устанавливаем время начала окна
                h, m = map(int, window.start_time.split(":"))
                next_date = next_date.replace(hour=h, minute=m, second=0, microsecond=0)
                
                if next_date > from_dt:
                    next_windows.append((next_date, window))
                    break
                    
        if next_windows:
            return min(next_windows, key=lambda x: x[0])
            
        return None
        
    def check_conflicts(self, change: ChangeRequest) -> List[ChangeRequest]:
        """Проверка конфликтов"""
        conflicts = []
        
        if not change.scheduled_start or not change.scheduled_end:
            return conflicts
            
        for other in self.scheduled_changes.values():
            if other.change_id == change.change_id:
                continue
            if not other.scheduled_start or not other.scheduled_end:
                continue
                
            # Проверяем пересечение
            if (change.scheduled_start < other.scheduled_end and
                change.scheduled_end > other.scheduled_start):
                
                # Проверяем общие системы
                if change.impact_assessment and other.impact_assessment:
                    common_systems = set(change.impact_assessment.affected_systems) & \
                                     set(other.impact_assessment.affected_systems)
                    if common_systems:
                        conflicts.append(other)
                        
        return conflicts


class ChangeManagementPlatform:
    """Платформа управления изменениями"""
    
    def __init__(self):
        self.changes: Dict[str, ChangeRequest] = {}
        self.audit_log: List[AuditEntry] = []
        
        self.risk_calculator = RiskCalculator()
        self.approval_workflow = ApprovalWorkflow()
        self.calendar = ChangeCalendar()
        
    def create_change(self, title: str, description: str,
                       change_type: ChangeType = ChangeType.NORMAL,
                       category: ChangeCategory = ChangeCategory.APPLICATION,
                       requestor: str = "") -> ChangeRequest:
        """Создание запроса на изменение"""
        change = ChangeRequest(
            change_id=f"CHG{uuid.uuid4().hex[:8].upper()}",
            title=title,
            description=description,
            change_type=change_type,
            category=category,
            requestor=requestor
        )
        
        self.changes[change.change_id] = change
        self._audit(change.change_id, "created", requestor, "", "draft")
        
        return change
        
    def add_impact_assessment(self, change_id: str, 
                               affected_systems: List[str],
                               affected_services: List[str],
                               affected_users: int,
                               business_impact: str,
                               downtime_minutes: int = 0) -> ImpactAssessment:
        """Добавление оценки влияния"""
        change = self.changes.get(change_id)
        if not change:
            raise ValueError(f"Change {change_id} not found")
            
        assessment = ImpactAssessment(
            assessment_id=f"impact_{uuid.uuid4().hex[:8]}",
            affected_systems=affected_systems,
            affected_services=affected_services,
            affected_users=affected_users,
            business_impact=business_impact,
            expected_downtime_minutes=downtime_minutes,
            notification_required=affected_users > 100 or downtime_minutes > 0
        )
        
        change.impact_assessment = assessment
        
        # Пересчитываем риск
        change.risk_level = self.risk_calculator.calculate(change)
        
        return assessment
        
    def add_rollback_plan(self, change_id: str, description: str,
                           steps: List[Dict[str, Any]],
                           triggers: List[str]) -> RollbackPlan:
        """Добавление плана отката"""
        change = self.changes.get(change_id)
        if not change:
            raise ValueError(f"Change {change_id} not found")
            
        estimated_time = sum(s.get("estimated_time", 5) for s in steps)
        
        plan = RollbackPlan(
            plan_id=f"rb_{uuid.uuid4().hex[:8]}",
            description=description,
            steps=steps,
            estimated_rollback_time_minutes=estimated_time,
            rollback_triggers=triggers
        )
        
        change.rollback_plan = plan
        
        return plan
        
    def submit_for_approval(self, change_id: str) -> ChangeRequest:
        """Подача на согласование"""
        change = self.changes.get(change_id)
        if not change:
            raise ValueError(f"Change {change_id} not found")
            
        if change.status != ChangeStatus.DRAFT:
            raise ValueError(f"Change must be in draft status")
            
        # Проверяем обязательные поля
        if not change.impact_assessment:
            raise ValueError("Impact assessment required")
        if change.change_type != ChangeType.STANDARD and not change.rollback_plan:
            raise ValueError("Rollback plan required for non-standard changes")
            
        change.status = ChangeStatus.SUBMITTED
        change.updated_at = datetime.now()
        
        # Добавляем согласователей
        required_roles = self.approval_workflow.get_required_approvers(change)
        
        for role in required_roles:
            approver = Approver(
                approver_id=f"apr_{uuid.uuid4().hex[:8]}",
                role=role
            )
            change.approvers.append(approver)
            
        self._audit(change_id, "submitted", change.requestor, "draft", "submitted")
        
        return change
        
    def approve(self, change_id: str, approver_role: str, 
                 approver_name: str, comments: str = "") -> ChangeRequest:
        """Одобрение изменения"""
        change = self.changes.get(change_id)
        if not change:
            raise ValueError(f"Change {change_id} not found")
            
        # Находим согласователя
        for approver in change.approvers:
            if approver.role == approver_role and approver.status == ApprovalStatus.PENDING:
                approver.status = ApprovalStatus.APPROVED
                approver.name = approver_name
                approver.decision_at = datetime.now()
                approver.comments = comments
                break
                
        # Проверяем, все ли одобрили
        if self.approval_workflow.is_approved(change):
            change.status = ChangeStatus.APPROVED
            self._audit(change_id, "approved", approver_name, "submitted", "approved")
        else:
            change.status = ChangeStatus.UNDER_REVIEW
            self._audit(change_id, "partial_approval", approver_name, "", "", 
                        f"{approver_role} approved")
            
        change.updated_at = datetime.now()
        return change
        
    def reject(self, change_id: str, approver_role: str,
                approver_name: str, reason: str) -> ChangeRequest:
        """Отклонение изменения"""
        change = self.changes.get(change_id)
        if not change:
            raise ValueError(f"Change {change_id} not found")
            
        for approver in change.approvers:
            if approver.role == approver_role:
                approver.status = ApprovalStatus.REJECTED
                approver.name = approver_name
                approver.decision_at = datetime.now()
                approver.comments = reason
                break
                
        change.status = ChangeStatus.REJECTED
        change.updated_at = datetime.now()
        
        self._audit(change_id, "rejected", approver_name, "", "rejected", reason)
        
        return change
        
    def schedule(self, change_id: str, start: datetime, end: datetime) -> ChangeRequest:
        """Планирование изменения"""
        change = self.changes.get(change_id)
        if not change:
            raise ValueError(f"Change {change_id} not found")
            
        if change.status != ChangeStatus.APPROVED:
            raise ValueError("Change must be approved before scheduling")
            
        # Проверяем окно изменений
        if not self.calendar.is_in_change_window(start, change.change_type):
            raise ValueError("Start time is outside change window")
            
        # Проверяем конфликты
        change.scheduled_start = start
        change.scheduled_end = end
        
        conflicts = self.calendar.check_conflicts(change)
        if conflicts:
            conflict_ids = [c.change_id for c in conflicts]
            raise ValueError(f"Schedule conflicts with: {', '.join(conflict_ids)}")
            
        change.status = ChangeStatus.SCHEDULED
        change.updated_at = datetime.now()
        
        self.calendar.scheduled_changes[change_id] = change
        
        self._audit(change_id, "scheduled", change.requestor, "approved", "scheduled",
                    f"{start.isoformat()} - {end.isoformat()}")
        
        return change
        
    def start_implementation(self, change_id: str, implementer: str) -> ChangeRequest:
        """Начало реализации"""
        change = self.changes.get(change_id)
        if not change:
            raise ValueError(f"Change {change_id} not found")
            
        if change.status not in [ChangeStatus.SCHEDULED, ChangeStatus.APPROVED]:
            raise ValueError("Change must be scheduled or approved")
            
        change.status = ChangeStatus.IN_PROGRESS
        change.actual_start = datetime.now()
        change.implementer = implementer
        change.updated_at = datetime.now()
        
        self._audit(change_id, "started", implementer, "scheduled", "in_progress")
        
        return change
        
    def complete(self, change_id: str, success: bool, notes: str = "") -> ChangeRequest:
        """Завершение изменения"""
        change = self.changes.get(change_id)
        if not change:
            raise ValueError(f"Change {change_id} not found")
            
        change.status = ChangeStatus.COMPLETED if success else ChangeStatus.FAILED
        change.actual_end = datetime.now()
        change.success = success
        change.implementation_notes = notes
        change.updated_at = datetime.now()
        
        status = "completed" if success else "failed"
        self._audit(change_id, status, change.implementer, "in_progress", status, notes)
        
        return change
        
    def rollback(self, change_id: str, reason: str) -> ChangeRequest:
        """Откат изменения"""
        change = self.changes.get(change_id)
        if not change:
            raise ValueError(f"Change {change_id} not found")
            
        if change.status != ChangeStatus.IN_PROGRESS:
            raise ValueError("Can only rollback in-progress changes")
            
        change.status = ChangeStatus.ROLLED_BACK
        change.actual_end = datetime.now()
        change.success = False
        change.implementation_notes = f"ROLLED BACK: {reason}"
        change.updated_at = datetime.now()
        
        self._audit(change_id, "rolled_back", change.implementer, "in_progress", "rolled_back", reason)
        
        return change
        
    def _audit(self, change_id: str, action: str, actor: str, 
                prev_status: str, new_status: str, details: str = ""):
        """Запись в аудит"""
        entry = AuditEntry(
            entry_id=f"audit_{uuid.uuid4().hex[:8]}",
            change_id=change_id,
            action=action,
            actor=actor,
            previous_status=prev_status,
            new_status=new_status,
            details=details
        )
        self.audit_log.append(entry)
        
    def get_audit_log(self, change_id: str = None) -> List[AuditEntry]:
        """Получение журнала аудита"""
        if change_id:
            return [e for e in self.audit_log if e.change_id == change_id]
        return self.audit_log
        
    def get_stats(self) -> Dict[str, Any]:
        """Статистика"""
        by_status = defaultdict(int)
        by_type = defaultdict(int)
        by_risk = defaultdict(int)
        
        success_count = 0
        total_completed = 0
        
        for change in self.changes.values():
            by_status[change.status.value] += 1
            by_type[change.change_type.value] += 1
            by_risk[change.risk_level.value] += 1
            
            if change.status == ChangeStatus.COMPLETED:
                total_completed += 1
                if change.success:
                    success_count += 1
                    
        success_rate = (success_count / total_completed * 100) if total_completed > 0 else 0
        
        return {
            "total_changes": len(self.changes),
            "by_status": dict(by_status),
            "by_type": dict(by_type),
            "by_risk": dict(by_risk),
            "success_rate": success_rate,
            "audit_entries": len(self.audit_log)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 85: Change Management Platform")
    print("=" * 60)
    
    async def demo():
        platform = ChangeManagementPlatform()
        print("✓ Change Management Platform created")
        
        # Настройка окон изменений
        print("\n📅 Setting Up Change Windows...")
        
        # Будние дни ночью
        weekday_window = platform.calendar.add_window(
            "Weekday Maintenance Window",
            days=[0, 1, 2, 3, 4],  # Mon-Fri
            start="02:00",
            end="06:00",
            environment="production"
        )
        print(f"  ✓ {weekday_window.name}: {weekday_window.start_time}-{weekday_window.end_time} UTC")
        
        # Выходные
        weekend_window = platform.calendar.add_window(
            "Weekend Maintenance Window",
            days=[5, 6],  # Sat-Sun
            start="00:00",
            end="12:00",
            environment="production"
        )
        print(f"  ✓ {weekend_window.name}: {weekend_window.start_time}-{weekend_window.end_time} UTC")
        
        # Заморозка на праздники
        freeze_start = datetime.now() + timedelta(days=15)
        freeze_end = freeze_start + timedelta(days=5)
        
        holiday_freeze = platform.calendar.add_freeze(
            "Holiday Code Freeze",
            start=freeze_start,
            end=freeze_end,
            reason="Year-end code freeze period"
        )
        print(f"\n  ❄️ Code Freeze: {holiday_freeze.start_date.strftime('%Y-%m-%d')} to {holiday_freeze.end_date.strftime('%Y-%m-%d')}")
        print(f"     Reason: {holiday_freeze.reason}")
        
        # Создание запросов на изменение
        print("\n📝 Creating Change Requests...")
        
        # Change 1: Обновление базы данных
        change1 = platform.create_change(
            "Database Schema Migration v2.5",
            "Migrate database schema to support new features",
            change_type=ChangeType.NORMAL,
            category=ChangeCategory.DATABASE,
            requestor="db-team@company.com"
        )
        
        # Добавляем оценку влияния
        platform.add_impact_assessment(
            change1.change_id,
            affected_systems=["postgres-primary", "postgres-replica-1", "postgres-replica-2"],
            affected_services=["api-gateway", "user-service", "order-service"],
            affected_users=50000,
            business_impact="high",
            downtime_minutes=15
        )
        
        # Добавляем план отката
        platform.add_rollback_plan(
            change1.change_id,
            "Restore database from pre-migration snapshot",
            steps=[
                {"order": 1, "action": "Stop application services", "estimated_time": 2},
                {"order": 2, "action": "Restore database from snapshot", "estimated_time": 10},
                {"order": 3, "action": "Verify data integrity", "estimated_time": 5},
                {"order": 4, "action": "Start application services", "estimated_time": 2},
                {"order": 5, "action": "Verify service health", "estimated_time": 3}
            ],
            triggers=["Migration script fails", "Data corruption detected", "Error rate > 5%"]
        )
        
        print(f"\n  📋 {change1.change_id}: {change1.title}")
        print(f"     Type: {change1.change_type.value}")
        print(f"     Category: {change1.category.value}")
        print(f"     Risk: {change1.risk_level.value}")
        print(f"     Affected Users: {change1.impact_assessment.affected_users:,}")
        print(f"     Downtime: {change1.impact_assessment.expected_downtime_minutes} min")
        
        # Change 2: Обновление конфигурации
        change2 = platform.create_change(
            "Update Rate Limiter Configuration",
            "Increase rate limits for premium users",
            change_type=ChangeType.STANDARD,
            category=ChangeCategory.CONFIGURATION,
            requestor="platform-team@company.com"
        )
        
        platform.add_impact_assessment(
            change2.change_id,
            affected_systems=["api-gateway"],
            affected_services=["rate-limiter"],
            affected_users=1000,
            business_impact="low",
            downtime_minutes=0
        )
        
        print(f"\n  📋 {change2.change_id}: {change2.title}")
        print(f"     Type: {change2.change_type.value} (pre-approved)")
        print(f"     Risk: {change2.risk_level.value}")
        
        # Change 3: Emergency change
        change3 = platform.create_change(
            "Critical Security Patch CVE-2024-1234",
            "Apply critical security patch to address vulnerability",
            change_type=ChangeType.EMERGENCY,
            category=ChangeCategory.SECURITY,
            requestor="security-team@company.com"
        )
        change3.justification = "Critical vulnerability with active exploitation in the wild"
        
        platform.add_impact_assessment(
            change3.change_id,
            affected_systems=["all-web-servers"],
            affected_services=["nginx", "api-gateway"],
            affected_users=100000,
            business_impact="critical",
            downtime_minutes=5
        )
        
        platform.add_rollback_plan(
            change3.change_id,
            "Revert to previous package version",
            steps=[
                {"order": 1, "action": "Rollback package", "estimated_time": 2},
                {"order": 2, "action": "Restart services", "estimated_time": 3}
            ],
            triggers=["Service degradation", "Manual decision"]
        )
        
        print(f"\n  🚨 {change3.change_id}: {change3.title}")
        print(f"     Type: {change3.change_type.value.upper()}")
        print(f"     Risk: {change3.risk_level.value}")
        print(f"     Justification: {change3.justification}")
        
        # Подача на согласование
        print("\n📤 Submitting Changes for Approval...")
        
        platform.submit_for_approval(change1.change_id)
        print(f"\n  ✓ {change1.change_id} submitted")
        print(f"    Required approvers: {[a.role for a in change1.approvers]}")
        
        platform.submit_for_approval(change3.change_id)
        print(f"\n  ✓ {change3.change_id} submitted (emergency)")
        print(f"    Required approvers: {[a.role for a in change3.approvers]}")
        
        # Процесс согласования
        print("\n✅ Approval Process...")
        
        # Одобрение change1
        platform.approve(change1.change_id, "tech_lead", "John Smith", "Looks good, approve")
        print(f"\n  ✓ {change1.change_id}: tech_lead approved")
        print(f"    Status: {change1.status.value}")
        
        platform.approve(change1.change_id, "cab_member", "Jane Doe", "CAB review passed")
        print(f"  ✓ {change1.change_id}: cab_member approved")
        print(f"    Status: {change1.status.value}")
        
        # Security для высокого риска
        if "security" in [a.role for a in change1.approvers]:
            platform.approve(change1.change_id, "security", "Security Team", "Security review passed")
            print(f"  ✓ {change1.change_id}: security approved")
            
        print(f"    Final Status: {change1.status.value}")
        
        # Emergency change
        platform.approve(change3.change_id, "on_call_manager", "Emergency Manager", "Approved for immediate implementation")
        print(f"\n  🚨 {change3.change_id}: on_call_manager approved")
        print(f"    Status: {change3.status.value}")
        
        # Планирование
        print("\n📅 Scheduling Changes...")
        
        # Находим следующее окно
        next_window = platform.calendar.get_next_window()
        if next_window:
            window_time, window = next_window
            print(f"\n  Next maintenance window: {window_time.strftime('%Y-%m-%d %H:%M')} ({window.name})")
            
            # Планируем change1
            start_time = window_time
            end_time = start_time + timedelta(hours=2)
            
            platform.schedule(change1.change_id, start_time, end_time)
            print(f"\n  ✓ {change1.change_id} scheduled:")
            print(f"    Start: {change1.scheduled_start.strftime('%Y-%m-%d %H:%M')}")
            print(f"    End: {change1.scheduled_end.strftime('%Y-%m-%d %H:%M')}")
            
        # Emergency выполняется сразу
        now = datetime.now()
        platform.schedule(change3.change_id, now, now + timedelta(hours=1))
        print(f"\n  🚨 {change3.change_id} scheduled for immediate implementation")
        
        # Реализация Emergency change
        print("\n🔧 Implementing Emergency Change...")
        
        platform.start_implementation(change3.change_id, "ops-team@company.com")
        print(f"\n  ⏳ {change3.change_id} implementation started")
        print(f"    Started at: {change3.actual_start.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Симуляция успешного завершения
        await asyncio.sleep(0.1)
        
        platform.complete(change3.change_id, success=True, 
                           notes="Patch applied successfully to all servers")
        print(f"\n  ✅ {change3.change_id} completed successfully")
        print(f"    Duration: {(change3.actual_end - change3.actual_start).seconds} seconds")
        
        # Change Calendar View
        print("\n📅 Change Calendar (Next 7 Days):")
        
        scheduled = [c for c in platform.changes.values() 
                     if c.status == ChangeStatus.SCHEDULED and c.scheduled_start]
        
        print("  ┌─────────────────────────────────────────────────────┐")
        print("  │  Date       │ Time  │ Change ID   │ Title          │")
        print("  ├─────────────────────────────────────────────────────┤")
        
        for change in sorted(scheduled, key=lambda x: x.scheduled_start):
            date = change.scheduled_start.strftime("%Y-%m-%d")
            time = change.scheduled_start.strftime("%H:%M")
            title = change.title[:15] + "..." if len(change.title) > 15 else change.title.ljust(15)
            print(f"  │ {date} │ {time} │ {change.change_id} │ {title}│")
            
        print("  └─────────────────────────────────────────────────────┘")
        
        # Журнал аудита
        print("\n📜 Audit Log:")
        
        audit = platform.get_audit_log()[-10:]  # Последние 10 записей
        
        for entry in audit:
            timestamp = entry.timestamp.strftime("%H:%M:%S")
            print(f"  {timestamp} │ {entry.change_id} │ {entry.action:15} │ {entry.actor[:20]}")
            
        # Статистика
        print("\n📊 Change Management Statistics:")
        
        stats = platform.get_stats()
        
        print(f"\n  Total Changes: {stats['total_changes']}")
        print(f"  Success Rate: {stats['success_rate']:.1f}%")
        
        print("\n  By Status:")
        for status, count in stats['by_status'].items():
            print(f"    {status:15} {count}")
            
        print("\n  By Type:")
        for ctype, count in stats['by_type'].items():
            print(f"    {ctype:15} {count}")
            
        print("\n  By Risk Level:")
        for risk, count in stats['by_risk'].items():
            icon = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}.get(risk, "⚪")
            print(f"    {icon} {risk:10} {count}")
            
        # Отображение workflow
        print("\n🔄 Change Workflow Summary:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │  DRAFT → SUBMITTED → UNDER_REVIEW → APPROVED → SCHEDULED   │")
        print("  │                                                             │")
        print("  │  SCHEDULED → IN_PROGRESS → COMPLETED / FAILED / ROLLED_BACK│")
        print("  └─────────────────────────────────────────────────────────────┘")
        
        # Создаём ещё одно изменение и показываем отклонение
        print("\n❌ Demonstrating Rejection...")
        
        change4 = platform.create_change(
            "Upgrade Production DB to Beta Version",
            "Upgrade PostgreSQL to unreleased beta version",
            change_type=ChangeType.NORMAL,
            category=ChangeCategory.DATABASE,
            requestor="dev@company.com"
        )
        
        platform.add_impact_assessment(
            change4.change_id,
            affected_systems=["postgres-primary"],
            affected_services=["all"],
            affected_users=100000,
            business_impact="critical",
            downtime_minutes=60
        )
        
        platform.add_rollback_plan(
            change4.change_id,
            "Restore from backup",
            steps=[{"order": 1, "action": "Restore", "estimated_time": 120}],
            triggers=["Any issue"]
        )
        
        platform.submit_for_approval(change4.change_id)
        
        platform.reject(change4.change_id, "tech_lead", "John Smith",
                         "Cannot use beta software in production environment")
        
        print(f"\n  ❌ {change4.change_id}: REJECTED")
        print(f"     Reason: Cannot use beta software in production environment")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Change Management Platform initialized!")
    print("=" * 60)
