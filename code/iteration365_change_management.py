#!/usr/bin/env python3
"""
Server Init - Iteration 365: Change Management Platform
Платформа управления изменениями

Функционал:
- Change Request Management - управление запросами на изменение
- Risk Assessment - оценка рисков
- Approval Workflows - workflow одобрения
- Change Calendar - календарь изменений
- Change Windows - окна изменений
- Rollback Planning - планирование отката
- Impact Analysis - анализ влияния
- Compliance Tracking - отслеживание соответствия
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid


class ChangeType(Enum):
    """Тип изменения"""
    STANDARD = "standard"
    NORMAL = "normal"
    EMERGENCY = "emergency"
    EXPEDITED = "expedited"


class ChangeCategory(Enum):
    """Категория изменения"""
    SOFTWARE = "software"
    HARDWARE = "hardware"
    NETWORK = "network"
    DATABASE = "database"
    SECURITY = "security"
    CONFIGURATION = "configuration"
    INFRASTRUCTURE = "infrastructure"


class ChangeStatus(Enum):
    """Статус изменения"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLED_BACK = "rolled_back"


class RiskLevel(Enum):
    """Уровень риска"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ImpactLevel(Enum):
    """Уровень влияния"""
    NONE = "none"
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


class WindowType(Enum):
    """Тип окна изменений"""
    STANDARD = "standard"
    MAINTENANCE = "maintenance"
    EMERGENCY = "emergency"
    FREEZE = "freeze"


@dataclass
class User:
    """Пользователь"""
    user_id: str
    name: str
    email: str
    role: str = ""  # requester, approver, implementer, cab_member
    department: str = ""
    is_cab_member: bool = False


@dataclass
class Service:
    """Сервис"""
    service_id: str
    name: str
    tier: int = 3
    owner_team: str = ""
    change_approvers: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class RiskAssessment:
    """Оценка риска"""
    assessment_id: str
    
    # Scores (1-5)
    complexity_score: int = 1
    impact_score: int = 1
    urgency_score: int = 1
    
    # Calculated
    risk_level: RiskLevel = RiskLevel.LOW
    risk_score: int = 0
    
    # Factors
    risk_factors: List[str] = field(default_factory=list)
    mitigation_steps: List[str] = field(default_factory=list)
    
    # Assessment
    assessed_by: str = ""
    assessed_at: datetime = field(default_factory=datetime.now)


@dataclass
class ImpactAnalysis:
    """Анализ влияния"""
    analysis_id: str
    
    # Affected items
    affected_services: List[str] = field(default_factory=list)
    affected_users: int = 0
    affected_regions: List[str] = field(default_factory=list)
    
    # Impact
    impact_level: ImpactLevel = ImpactLevel.LOW
    
    # Business impact
    business_impact: str = ""
    downtime_minutes: int = 0
    
    # Dependencies
    upstream_dependencies: List[str] = field(default_factory=list)
    downstream_dependencies: List[str] = field(default_factory=list)


@dataclass
class RollbackPlan:
    """План отката"""
    plan_id: str
    
    # Steps
    steps: List[str] = field(default_factory=list)
    
    # Prerequisites
    prerequisites: List[str] = field(default_factory=list)
    
    # Time
    estimated_duration_minutes: int = 30
    
    # Verification
    verification_steps: List[str] = field(default_factory=list)
    
    # Tested
    is_tested: bool = False
    tested_at: Optional[datetime] = None


@dataclass
class Approval:
    """Одобрение"""
    approval_id: str
    
    # Approver
    approver_id: str = ""
    approver_name: str = ""
    
    # Status
    status: ApprovalStatus = ApprovalStatus.PENDING
    
    # Comment
    comment: str = ""
    
    # Timestamps
    requested_at: datetime = field(default_factory=datetime.now)
    responded_at: Optional[datetime] = None


@dataclass
class ChangeWindow:
    """Окно изменений"""
    window_id: str
    
    # Identity
    name: str = ""
    description: str = ""
    
    # Type
    window_type: WindowType = WindowType.STANDARD
    
    # Time
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime = field(default_factory=datetime.now)
    
    # Recurrence
    is_recurring: bool = False
    recurrence_pattern: str = ""  # weekly, monthly
    
    # Restrictions
    allowed_change_types: List[ChangeType] = field(default_factory=list)
    max_concurrent_changes: int = 5
    
    # Status
    is_active: bool = True


@dataclass
class ImplementationTask:
    """Задача реализации"""
    task_id: str
    
    # Identity
    title: str = ""
    description: str = ""
    
    # Order
    order: int = 0
    
    # Assignment
    assignee_id: str = ""
    assignee_name: str = ""
    
    # Status
    status: str = "pending"  # pending, in_progress, completed, failed, skipped
    
    # Duration
    estimated_minutes: int = 30
    actual_minutes: int = 0
    
    # Result
    output: str = ""
    error: str = ""
    
    # Timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class ChangeRequest:
    """Запрос на изменение"""
    change_id: str
    
    # Identity
    change_number: int = 0
    title: str = ""
    description: str = ""
    
    # Classification
    change_type: ChangeType = ChangeType.NORMAL
    category: ChangeCategory = ChangeCategory.SOFTWARE
    
    # Status
    status: ChangeStatus = ChangeStatus.DRAFT
    
    # Requester
    requester_id: str = ""
    requester_name: str = ""
    
    # Implementer
    implementer_id: str = ""
    implementer_name: str = ""
    
    # Services
    affected_services: List[str] = field(default_factory=list)
    
    # Risk & Impact
    risk_assessment: Optional[RiskAssessment] = None
    impact_analysis: Optional[ImpactAnalysis] = None
    
    # Rollback
    rollback_plan: Optional[RollbackPlan] = None
    
    # Schedule
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    change_window_id: str = ""
    
    # Approvals
    approvals: List[Approval] = field(default_factory=list)
    requires_cab_approval: bool = False
    
    # Implementation
    implementation_tasks: List[ImplementationTask] = field(default_factory=list)
    
    # Testing
    test_plan: str = ""
    test_results: str = ""
    
    # Justification
    business_justification: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class CABMeeting:
    """Заседание CAB"""
    meeting_id: str
    
    # Schedule
    scheduled_at: datetime = field(default_factory=datetime.now)
    duration_minutes: int = 60
    
    # Attendees
    attendees: List[str] = field(default_factory=list)
    
    # Changes to review
    change_ids: List[str] = field(default_factory=list)
    
    # Status
    status: str = "scheduled"  # scheduled, in_progress, completed
    
    # Notes
    notes: str = ""
    
    # Decisions
    decisions: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ChangeMetrics:
    """Метрики изменений"""
    metrics_id: str
    
    # Counts
    total_changes: int = 0
    successful_changes: int = 0
    failed_changes: int = 0
    rolled_back_changes: int = 0
    
    # By type
    standard_changes: int = 0
    normal_changes: int = 0
    emergency_changes: int = 0
    
    # Performance
    avg_implementation_minutes: float = 0.0
    avg_approval_hours: float = 0.0
    
    # Success rate
    success_rate: float = 0.0
    
    # Timestamps
    collected_at: datetime = field(default_factory=datetime.now)


class ChangeManagementPlatform:
    """Платформа управления изменениями"""
    
    def __init__(self, platform_name: str = "change-management"):
        self.platform_name = platform_name
        self.changes: Dict[str, ChangeRequest] = {}
        self.users: Dict[str, User] = {}
        self.services: Dict[str, Service] = {}
        self.change_windows: Dict[str, ChangeWindow] = {}
        self.cab_meetings: Dict[str, CABMeeting] = {}
        self._change_counter = 0
        
    async def register_user(self, name: str,
                           email: str,
                           role: str = "requester",
                           department: str = "",
                           is_cab_member: bool = False) -> User:
        """Регистрация пользователя"""
        user = User(
            user_id=f"usr_{uuid.uuid4().hex[:8]}",
            name=name,
            email=email,
            role=role,
            department=department,
            is_cab_member=is_cab_member
        )
        
        self.users[user.user_id] = user
        return user
        
    async def register_service(self, name: str,
                              tier: int = 3,
                              owner_team: str = "",
                              change_approvers: List[str] = None,
                              dependencies: List[str] = None) -> Service:
        """Регистрация сервиса"""
        service = Service(
            service_id=f"svc_{uuid.uuid4().hex[:8]}",
            name=name,
            tier=tier,
            owner_team=owner_team,
            change_approvers=change_approvers or [],
            dependencies=dependencies or []
        )
        
        self.services[service.service_id] = service
        return service
        
    async def create_change_window(self, name: str,
                                   start_time: datetime,
                                   end_time: datetime,
                                   window_type: WindowType = WindowType.STANDARD,
                                   allowed_types: List[ChangeType] = None,
                                   is_recurring: bool = False,
                                   recurrence_pattern: str = "") -> ChangeWindow:
        """Создание окна изменений"""
        window = ChangeWindow(
            window_id=f"win_{uuid.uuid4().hex[:8]}",
            name=name,
            window_type=window_type,
            start_time=start_time,
            end_time=end_time,
            is_recurring=is_recurring,
            recurrence_pattern=recurrence_pattern,
            allowed_change_types=allowed_types or list(ChangeType)
        )
        
        self.change_windows[window.window_id] = window
        return window
        
    async def create_change_request(self, title: str,
                                    description: str,
                                    requester_id: str,
                                    change_type: ChangeType = ChangeType.NORMAL,
                                    category: ChangeCategory = ChangeCategory.SOFTWARE,
                                    affected_services: List[str] = None,
                                    business_justification: str = "") -> ChangeRequest:
        """Создание запроса на изменение"""
        self._change_counter += 1
        requester = self.users.get(requester_id)
        
        change = ChangeRequest(
            change_id=f"chg_{uuid.uuid4().hex[:8]}",
            change_number=self._change_counter,
            title=title,
            description=description,
            change_type=change_type,
            category=category,
            requester_id=requester_id,
            requester_name=requester.name if requester else "",
            affected_services=affected_services or [],
            business_justification=business_justification
        )
        
        # Determine if CAB approval required
        if change_type in [ChangeType.NORMAL, ChangeType.EMERGENCY]:
            change.requires_cab_approval = True
            
        self.changes[change.change_id] = change
        return change
        
    async def assess_risk(self, change_id: str,
                         complexity_score: int,
                         impact_score: int,
                         urgency_score: int,
                         risk_factors: List[str] = None,
                         mitigation_steps: List[str] = None,
                         assessor_id: str = "") -> Optional[RiskAssessment]:
        """Оценка риска"""
        change = self.changes.get(change_id)
        if not change:
            return None
            
        # Calculate risk score and level
        risk_score = complexity_score * impact_score * urgency_score
        
        if risk_score <= 8:
            risk_level = RiskLevel.LOW
        elif risk_score <= 27:
            risk_level = RiskLevel.MEDIUM
        elif risk_score <= 64:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.CRITICAL
            
        assessment = RiskAssessment(
            assessment_id=f"ra_{uuid.uuid4().hex[:8]}",
            complexity_score=complexity_score,
            impact_score=impact_score,
            urgency_score=urgency_score,
            risk_level=risk_level,
            risk_score=risk_score,
            risk_factors=risk_factors or [],
            mitigation_steps=mitigation_steps or [],
            assessed_by=assessor_id
        )
        
        change.risk_assessment = assessment
        return assessment
        
    async def analyze_impact(self, change_id: str,
                            affected_services: List[str] = None,
                            affected_users: int = 0,
                            downtime_minutes: int = 0,
                            business_impact: str = "") -> Optional[ImpactAnalysis]:
        """Анализ влияния"""
        change = self.changes.get(change_id)
        if not change:
            return None
            
        # Determine impact level
        if downtime_minutes == 0 and affected_users < 100:
            impact_level = ImpactLevel.LOW
        elif downtime_minutes <= 15 and affected_users < 1000:
            impact_level = ImpactLevel.MEDIUM
        elif downtime_minutes <= 60 or affected_users < 10000:
            impact_level = ImpactLevel.HIGH
        else:
            impact_level = ImpactLevel.CRITICAL
            
        analysis = ImpactAnalysis(
            analysis_id=f"ia_{uuid.uuid4().hex[:8]}",
            affected_services=affected_services or change.affected_services,
            affected_users=affected_users,
            impact_level=impact_level,
            business_impact=business_impact,
            downtime_minutes=downtime_minutes
        )
        
        change.impact_analysis = analysis
        return analysis
        
    async def create_rollback_plan(self, change_id: str,
                                   steps: List[str],
                                   prerequisites: List[str] = None,
                                   estimated_duration: int = 30,
                                   verification_steps: List[str] = None) -> Optional[RollbackPlan]:
        """Создание плана отката"""
        change = self.changes.get(change_id)
        if not change:
            return None
            
        plan = RollbackPlan(
            plan_id=f"rbp_{uuid.uuid4().hex[:8]}",
            steps=steps,
            prerequisites=prerequisites or [],
            estimated_duration_minutes=estimated_duration,
            verification_steps=verification_steps or []
        )
        
        change.rollback_plan = plan
        return plan
        
    async def add_implementation_task(self, change_id: str,
                                      title: str,
                                      description: str = "",
                                      assignee_id: str = "",
                                      estimated_minutes: int = 30) -> Optional[ImplementationTask]:
        """Добавление задачи реализации"""
        change = self.changes.get(change_id)
        if not change:
            return None
            
        user = self.users.get(assignee_id)
        
        task = ImplementationTask(
            task_id=f"tsk_{uuid.uuid4().hex[:8]}",
            title=title,
            description=description,
            order=len(change.implementation_tasks),
            assignee_id=assignee_id,
            assignee_name=user.name if user else "",
            estimated_minutes=estimated_minutes
        )
        
        change.implementation_tasks.append(task)
        return task
        
    async def submit_change(self, change_id: str) -> Optional[ChangeRequest]:
        """Отправка изменения на рассмотрение"""
        change = self.changes.get(change_id)
        if not change:
            return None
            
        if change.status != ChangeStatus.DRAFT:
            return change
            
        change.status = ChangeStatus.SUBMITTED
        change.submitted_at = datetime.now()
        
        # Auto-create approval requests for affected services
        for service_name in change.affected_services:
            for service in self.services.values():
                if service.name == service_name:
                    for approver_id in service.change_approvers:
                        await self._request_approval(change, approver_id)
                        
        return change
        
    async def _request_approval(self, change: ChangeRequest, approver_id: str):
        """Запрос одобрения"""
        user = self.users.get(approver_id)
        
        approval = Approval(
            approval_id=f"apr_{uuid.uuid4().hex[:8]}",
            approver_id=approver_id,
            approver_name=user.name if user else ""
        )
        
        change.approvals.append(approval)
        
    async def approve_change(self, change_id: str,
                            approver_id: str,
                            comment: str = "") -> Optional[ChangeRequest]:
        """Одобрение изменения"""
        change = self.changes.get(change_id)
        if not change:
            return None
            
        for approval in change.approvals:
            if approval.approver_id == approver_id:
                approval.status = ApprovalStatus.APPROVED
                approval.comment = comment
                approval.responded_at = datetime.now()
                break
                
        # Check if all approvals received
        all_approved = all(a.status == ApprovalStatus.APPROVED for a in change.approvals)
        if all_approved and change.approvals:
            change.status = ChangeStatus.APPROVED
            change.approved_at = datetime.now()
            
        return change
        
    async def reject_change(self, change_id: str,
                           approver_id: str,
                           reason: str = "") -> Optional[ChangeRequest]:
        """Отклонение изменения"""
        change = self.changes.get(change_id)
        if not change:
            return None
            
        for approval in change.approvals:
            if approval.approver_id == approver_id:
                approval.status = ApprovalStatus.REJECTED
                approval.comment = reason
                approval.responded_at = datetime.now()
                break
                
        return change
        
    async def schedule_change(self, change_id: str,
                             window_id: str,
                             start_time: datetime,
                             end_time: datetime,
                             implementer_id: str = "") -> Optional[ChangeRequest]:
        """Планирование изменения"""
        change = self.changes.get(change_id)
        if not change:
            return None
            
        user = self.users.get(implementer_id)
        
        change.scheduled_start = start_time
        change.scheduled_end = end_time
        change.change_window_id = window_id
        change.implementer_id = implementer_id
        change.implementer_name = user.name if user else ""
        change.status = ChangeStatus.SCHEDULED
        
        return change
        
    async def start_implementation(self, change_id: str) -> Optional[ChangeRequest]:
        """Начало реализации"""
        change = self.changes.get(change_id)
        if not change:
            return None
            
        change.status = ChangeStatus.IN_PROGRESS
        change.started_at = datetime.now()
        
        return change
        
    async def complete_task(self, change_id: str,
                           task_id: str,
                           output: str = "",
                           success: bool = True) -> Optional[ImplementationTask]:
        """Завершение задачи"""
        change = self.changes.get(change_id)
        if not change:
            return None
            
        for task in change.implementation_tasks:
            if task.task_id == task_id:
                task.status = "completed" if success else "failed"
                task.output = output
                task.completed_at = datetime.now()
                if task.started_at:
                    task.actual_minutes = int((task.completed_at - task.started_at).total_seconds() / 60)
                return task
                
        return None
        
    async def complete_change(self, change_id: str,
                             success: bool = True,
                             test_results: str = "") -> Optional[ChangeRequest]:
        """Завершение изменения"""
        change = self.changes.get(change_id)
        if not change:
            return None
            
        change.status = ChangeStatus.COMPLETED if success else ChangeStatus.FAILED
        change.completed_at = datetime.now()
        change.test_results = test_results
        
        return change
        
    async def rollback_change(self, change_id: str,
                             reason: str = "") -> Optional[ChangeRequest]:
        """Откат изменения"""
        change = self.changes.get(change_id)
        if not change:
            return None
            
        change.status = ChangeStatus.ROLLED_BACK
        change.completed_at = datetime.now()
        change.test_results = f"Rolled back: {reason}"
        
        return change
        
    async def schedule_cab_meeting(self, scheduled_at: datetime,
                                  duration_minutes: int = 60,
                                  attendees: List[str] = None) -> CABMeeting:
        """Планирование заседания CAB"""
        # Get CAB members
        cab_members = [u.user_id for u in self.users.values() if u.is_cab_member]
        
        meeting = CABMeeting(
            meeting_id=f"cab_{uuid.uuid4().hex[:8]}",
            scheduled_at=scheduled_at,
            duration_minutes=duration_minutes,
            attendees=attendees or cab_members
        )
        
        # Add pending changes to agenda
        for change in self.changes.values():
            if change.requires_cab_approval and change.status == ChangeStatus.SUBMITTED:
                meeting.change_ids.append(change.change_id)
                
        self.cab_meetings[meeting.meeting_id] = meeting
        return meeting
        
    async def collect_metrics(self) -> ChangeMetrics:
        """Сбор метрик"""
        completed = [c for c in self.changes.values() if c.status == ChangeStatus.COMPLETED]
        failed = [c for c in self.changes.values() if c.status == ChangeStatus.FAILED]
        rolled_back = [c for c in self.changes.values() if c.status == ChangeStatus.ROLLED_BACK]
        
        standard = sum(1 for c in self.changes.values() if c.change_type == ChangeType.STANDARD)
        normal = sum(1 for c in self.changes.values() if c.change_type == ChangeType.NORMAL)
        emergency = sum(1 for c in self.changes.values() if c.change_type == ChangeType.EMERGENCY)
        
        # Calculate averages
        impl_times = []
        for c in completed:
            if c.started_at and c.completed_at:
                impl_times.append((c.completed_at - c.started_at).total_seconds() / 60)
                
        avg_impl = sum(impl_times) / len(impl_times) if impl_times else 0.0
        
        approval_times = []
        for c in self.changes.values():
            if c.submitted_at and c.approved_at:
                approval_times.append((c.approved_at - c.submitted_at).total_seconds() / 3600)
                
        avg_approval = sum(approval_times) / len(approval_times) if approval_times else 0.0
        
        # Success rate
        total_finished = len(completed) + len(failed) + len(rolled_back)
        success_rate = (len(completed) / total_finished * 100) if total_finished > 0 else 0.0
        
        return ChangeMetrics(
            metrics_id=f"cm_{uuid.uuid4().hex[:8]}",
            total_changes=len(self.changes),
            successful_changes=len(completed),
            failed_changes=len(failed),
            rolled_back_changes=len(rolled_back),
            standard_changes=standard,
            normal_changes=normal,
            emergency_changes=emergency,
            avg_implementation_minutes=avg_impl,
            avg_approval_hours=avg_approval,
            success_rate=success_rate
        )
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        by_status = {}
        for status in ChangeStatus:
            by_status[status.value] = sum(1 for c in self.changes.values() if c.status == status)
            
        by_type = {}
        for change_type in ChangeType:
            by_type[change_type.value] = sum(1 for c in self.changes.values() if c.change_type == change_type)
            
        by_category = {}
        for category in ChangeCategory:
            by_category[category.value] = sum(1 for c in self.changes.values() if c.category == category)
            
        by_risk = {}
        for risk in RiskLevel:
            by_risk[risk.value] = sum(
                1 for c in self.changes.values()
                if c.risk_assessment and c.risk_assessment.risk_level == risk
            )
            
        pending_approvals = sum(
            1 for c in self.changes.values()
            for a in c.approvals if a.status == ApprovalStatus.PENDING
        )
        
        return {
            "total_changes": len(self.changes),
            "by_status": by_status,
            "by_type": by_type,
            "by_category": by_category,
            "by_risk": by_risk,
            "total_users": len(self.users),
            "total_services": len(self.services),
            "change_windows": len(self.change_windows),
            "cab_meetings": len(self.cab_meetings),
            "pending_approvals": pending_approvals
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 365: Change Management Platform")
    print("=" * 60)
    
    platform = ChangeManagementPlatform(platform_name="enterprise-cm")
    print("✓ Change Management Platform initialized")
    
    # Register Users
    print("\n👥 Registering Users...")
    
    users_data = [
        ("John Smith", "john@example.com", "approver", "Engineering", True),
        ("Jane Doe", "jane@example.com", "requester", "Backend", False),
        ("Bob Wilson", "bob@example.com", "implementer", "DevOps", True),
        ("Alice Brown", "alice@example.com", "approver", "Security", True),
        ("Charlie Davis", "charlie@example.com", "requester", "Platform", False),
        ("Eva Martinez", "eva@example.com", "cab_member", "IT Management", True)
    ]
    
    users = []
    for name, email, role, dept, is_cab in users_data:
        user = await platform.register_user(name, email, role, dept, is_cab)
        users.append(user)
        cab_status = " (CAB)" if is_cab else ""
        print(f"  👤 {name} ({role}){cab_status}")
        
    # Register Services
    print("\n🔧 Registering Services...")
    
    services_data = [
        ("api-gateway", 1, "Platform Team", [users[0].user_id, users[3].user_id]),
        ("payment-service", 1, "Backend Team", [users[0].user_id]),
        ("user-service", 2, "Backend Team", [users[0].user_id]),
        ("notification-service", 3, "Platform Team", [users[0].user_id]),
        ("analytics-service", 3, "Data Team", [users[0].user_id])
    ]
    
    services = []
    for name, tier, team, approvers in services_data:
        service = await platform.register_service(name, tier, team, approvers)
        services.append(service)
        print(f"  🔧 {name} (Tier {tier})")
        
    # Create Change Windows
    print("\n🕐 Creating Change Windows...")
    
    now = datetime.now()
    windows_data = [
        ("Weekly Maintenance", now + timedelta(days=1, hours=2), now + timedelta(days=1, hours=6), WindowType.MAINTENANCE, True, "weekly"),
        ("Emergency Window", now, now + timedelta(hours=24), WindowType.EMERGENCY, False, ""),
        ("Standard Changes", now + timedelta(hours=1), now + timedelta(days=7), WindowType.STANDARD, False, "")
    ]
    
    windows = []
    for name, start, end, w_type, recurring, pattern in windows_data:
        window = await platform.create_change_window(name, start, end, w_type, is_recurring=recurring, recurrence_pattern=pattern)
        windows.append(window)
        print(f"  🕐 {name} ({w_type.value})")
        
    # Create Change Requests
    print("\n📝 Creating Change Requests...")
    
    changes_data = [
        ("Upgrade API Gateway to v2.5", "Update nginx configuration and deploy new version", users[1].user_id, ChangeType.NORMAL, ChangeCategory.SOFTWARE, ["api-gateway"], "Improved performance and security patches"),
        ("Database Connection Pool Increase", "Increase max connections from 100 to 200", users[1].user_id, ChangeType.STANDARD, ChangeCategory.DATABASE, ["payment-service", "user-service"], "Handle increased traffic"),
        ("SSL Certificate Renewal", "Renew expiring SSL certificates", users[4].user_id, ChangeType.STANDARD, ChangeCategory.SECURITY, ["api-gateway"], "Certificate expires in 30 days"),
        ("Network Firewall Update", "Update firewall rules for new services", users[2].user_id, ChangeType.NORMAL, ChangeCategory.NETWORK, ["api-gateway", "payment-service"], "Security compliance requirement"),
        ("Emergency Hotfix - Memory Leak", "Deploy fix for memory leak in notification service", users[2].user_id, ChangeType.EMERGENCY, ChangeCategory.SOFTWARE, ["notification-service"], "Critical production issue")
    ]
    
    changes = []
    for title, desc, requester, c_type, category, services, justification in changes_data:
        change = await platform.create_change_request(title, desc, requester, c_type, category, services, justification)
        changes.append(change)
        print(f"  📝 CHG-{change.change_number}: {title} ({c_type.value})")
        
    # Assess Risks
    print("\n⚠️ Assessing Risks...")
    
    risk_data = [
        (changes[0].change_id, 3, 4, 2, ["Service downtime possible", "Configuration complexity"], ["Blue-green deployment", "Automated rollback"]),
        (changes[1].change_id, 2, 2, 3, ["Performance impact"], ["Gradual increase", "Monitor connections"]),
        (changes[2].change_id, 1, 1, 4, ["Certificate validation"], ["Pre-generate certificates", "DNS propagation"]),
        (changes[3].change_id, 4, 4, 2, ["Network disruption", "Service isolation"], ["Staged rollout", "Monitoring"]),
        (changes[4].change_id, 2, 3, 5, ["Incomplete fix possible"], ["Extended monitoring"])
    ]
    
    for change_id, complexity, impact, urgency, factors, mitigation in risk_data:
        assessment = await platform.assess_risk(change_id, complexity, impact, urgency, factors, mitigation, users[0].user_id)
        change = platform.changes[change_id]
        print(f"  ⚠️ CHG-{change.change_number}: {assessment.risk_level.value.upper()} (score: {assessment.risk_score})")
        
    # Analyze Impact
    print("\n📊 Analyzing Impact...")
    
    impact_data = [
        (changes[0].change_id, ["api-gateway"], 50000, 5, "Brief service interruption during deployment"),
        (changes[1].change_id, ["payment-service", "user-service"], 10000, 0, "No expected downtime"),
        (changes[2].change_id, ["api-gateway"], 50000, 0, "Certificate swap with no downtime"),
        (changes[3].change_id, ["api-gateway", "payment-service"], 50000, 15, "Brief connectivity issues"),
        (changes[4].change_id, ["notification-service"], 5000, 2, "Notification delays during restart")
    ]
    
    for change_id, services, users_affected, downtime, impact_desc in impact_data:
        analysis = await platform.analyze_impact(change_id, services, users_affected, downtime, impact_desc)
        change = platform.changes[change_id]
        print(f"  📊 CHG-{change.change_number}: {analysis.impact_level.value.upper()} ({users_affected} users, {downtime}m downtime)")
        
    # Create Rollback Plans
    print("\n🔙 Creating Rollback Plans...")
    
    rollback_data = [
        (changes[0].change_id, ["Revert to previous nginx config", "Redeploy v2.4", "Verify health checks"], ["Backup current config", "Document current state"], 15),
        (changes[1].change_id, ["Reduce connection pool to 100", "Restart services"], ["Database backup"], 10),
        (changes[3].change_id, ["Revert firewall rules", "Flush connection tracking", "Verify connectivity"], ["Export current rules"], 20)
    ]
    
    for change_id, steps, prereqs, duration in rollback_data:
        plan = await platform.create_rollback_plan(change_id, steps, prereqs, duration)
        change = platform.changes[change_id]
        print(f"  🔙 CHG-{change.change_number}: {len(steps)} steps, {duration}m estimated")
        
    # Add Implementation Tasks
    print("\n✅ Adding Implementation Tasks...")
    
    # Tasks for first change
    await platform.add_implementation_task(changes[0].change_id, "Backup current configuration", "Export nginx config", users[2].user_id, 5)
    await platform.add_implementation_task(changes[0].change_id, "Deploy new version", "Run deployment script", users[2].user_id, 15)
    await platform.add_implementation_task(changes[0].change_id, "Run smoke tests", "Verify basic functionality", users[2].user_id, 10)
    await platform.add_implementation_task(changes[0].change_id, "Enable production traffic", "Switch load balancer", users[2].user_id, 5)
    
    # Tasks for network change
    await platform.add_implementation_task(changes[3].change_id, "Export current rules", "Backup firewall config", users[2].user_id, 5)
    await platform.add_implementation_task(changes[3].change_id, "Apply new rules", "Run firewall update script", users[2].user_id, 10)
    await platform.add_implementation_task(changes[3].change_id, "Verify connectivity", "Run connectivity tests", users[2].user_id, 15)
    
    print(f"  ✅ Added implementation tasks")
    
    # Submit Changes
    print("\n📤 Submitting Changes...")
    
    for change in changes[:4]:
        await platform.submit_change(change.change_id)
        print(f"  📤 CHG-{change.change_number}: Submitted")
        
    # Approve Changes
    print("\n✔️ Processing Approvals...")
    
    # Approve first two changes
    await platform.approve_change(changes[0].change_id, users[0].user_id, "Approved - deployment plan looks good")
    await platform.approve_change(changes[0].change_id, users[3].user_id, "Security review passed")
    print(f"  ✔️ CHG-{changes[0].change_number}: Approved")
    
    await platform.approve_change(changes[1].change_id, users[0].user_id, "Standard change - approved")
    print(f"  ✔️ CHG-{changes[1].change_number}: Approved")
    
    # Reject one change
    await platform.reject_change(changes[3].change_id, users[3].user_id, "Need additional security review")
    print(f"  ✖️ CHG-{changes[3].change_number}: Rejected")
    
    # Schedule Changes
    print("\n📅 Scheduling Changes...")
    
    await platform.schedule_change(
        changes[0].change_id,
        windows[2].window_id,
        now + timedelta(hours=2),
        now + timedelta(hours=3),
        users[2].user_id
    )
    print(f"  📅 CHG-{changes[0].change_number}: Scheduled for {(now + timedelta(hours=2)).strftime('%H:%M')}")
    
    await platform.schedule_change(
        changes[1].change_id,
        windows[2].window_id,
        now + timedelta(hours=4),
        now + timedelta(hours=5),
        users[2].user_id
    )
    print(f"  📅 CHG-{changes[1].change_number}: Scheduled for {(now + timedelta(hours=4)).strftime('%H:%M')}")
    
    # Implement First Change
    print("\n🚀 Implementing CHG-1...")
    
    await platform.start_implementation(changes[0].change_id)
    
    for task in changes[0].implementation_tasks:
        task.started_at = datetime.now()
        await asyncio.sleep(0.01)
        await platform.complete_task(changes[0].change_id, task.task_id, "Task completed successfully", True)
        print(f"  ✓ {task.title}")
        
    await platform.complete_change(changes[0].change_id, True, "All tests passed")
    print(f"  🎉 CHG-{changes[0].change_number}: Completed successfully")
    
    # Schedule CAB Meeting
    print("\n📋 Scheduling CAB Meeting...")
    
    cab = await platform.schedule_cab_meeting(
        now + timedelta(days=1),
        60,
        [u.user_id for u in users if u.is_cab_member]
    )
    print(f"  📋 CAB Meeting scheduled with {len(cab.attendees)} attendees")
    print(f"  📋 {len(cab.change_ids)} changes on agenda")
    
    # Collect Metrics
    metrics = await platform.collect_metrics()
    
    # Changes Dashboard
    print("\n📝 Change Requests:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ ID      │ Type       │ Title                                   │ Status         │ Risk     │ Requester                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for change in changes:
        chg_id = f"CHG-{change.change_number}".ljust(7)
        c_type = change.change_type.value[:10].ljust(10)
        title = change.title[:39].ljust(39)
        status = change.status.value[:14].ljust(14)
        risk = change.risk_assessment.risk_level.value.upper() if change.risk_assessment else "N/A"
        risk = risk[:8].ljust(8)
        requester = change.requester_name[:75].ljust(75)
        
        print(f"  │ {chg_id} │ {c_type} │ {title} │ {status} │ {risk} │ {requester} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Approval Status
    print("\n✔️ Approval Status:")
    
    for change in changes:
        if change.approvals:
            approved = sum(1 for a in change.approvals if a.status == ApprovalStatus.APPROVED)
            rejected = sum(1 for a in change.approvals if a.status == ApprovalStatus.REJECTED)
            pending = sum(1 for a in change.approvals if a.status == ApprovalStatus.PENDING)
            print(f"  CHG-{change.change_number}: ✓{approved} ✗{rejected} ⏳{pending}")
            
    # Change Windows
    print("\n🕐 Change Windows:")
    
    for window in windows:
        status = "Active" if window.is_active else "Inactive"
        print(f"  - {window.name}: {window.start_time.strftime('%m/%d %H:%M')} - {window.end_time.strftime('%H:%M')} ({status})")
        
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Total Changes: {stats['total_changes']}")
    print(f"  Pending Approvals: {stats['pending_approvals']}")
    print(f"  Success Rate: {metrics.success_rate:.1f}%")
    
    # By Type
    print("\n  Changes by Type:")
    for c_type, count in stats["by_type"].items():
        if count > 0:
            bar = "█" * count
            print(f"    {c_type:12s} │ {bar} ({count})")
            
    # By Status
    print("\n  Changes by Status:")
    for status, count in stats["by_status"].items():
        if count > 0:
            bar = "█" * count
            print(f"    {status:14s} │ {bar} ({count})")
            
    # By Risk
    print("\n  Changes by Risk:")
    for risk, count in stats["by_risk"].items():
        if count > 0:
            bar = "█" * count
            print(f"    {risk:10s} │ {bar} ({count})")
            
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Change Management Platform                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Changes:                 {stats['total_changes']:>12}                      │")
    print(f"│ Successful Changes:            {metrics.successful_changes:>12}                      │")
    print(f"│ Failed Changes:                {metrics.failed_changes:>12}                      │")
    print(f"│ Rolled Back:                   {metrics.rolled_back_changes:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Standard Changes:              {metrics.standard_changes:>12}                      │")
    print(f"│ Normal Changes:                {metrics.normal_changes:>12}                      │")
    print(f"│ Emergency Changes:             {metrics.emergency_changes:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Avg Implementation (min):      {metrics.avg_implementation_minutes:>12.1f}                      │")
    print(f"│ Avg Approval (hours):          {metrics.avg_approval_hours:>12.2f}                      │")
    print(f"│ Success Rate:                  {metrics.success_rate:>11.1f}%                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Change Windows:                {stats['change_windows']:>12}                      │")
    print(f"│ Pending Approvals:             {stats['pending_approvals']:>12}                      │")
    print(f"│ CAB Meetings:                  {stats['cab_meetings']:>12}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Change Management Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
