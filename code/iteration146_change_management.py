#!/usr/bin/env python3
"""
Server Init - Iteration 146: Change Management Platform
Платформа управления изменениями

Функционал:
- Change Requests - запросы на изменения
- Change Advisory Board (CAB) - совет по изменениям
- Risk Assessment - оценка рисков
- Approval Workflows - процессы утверждения
- Change Calendar - календарь изменений
- Impact Analysis - анализ влияния
- Rollback Planning - планирование отката
- Change Tracking - отслеживание изменений
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import random


class ChangeType(Enum):
    """Тип изменения"""
    STANDARD = "standard"  # Pre-approved, low risk
    NORMAL = "normal"  # Requires approval
    EMERGENCY = "emergency"  # Urgent, expedited approval
    MAJOR = "major"  # High impact, requires CAB


class ChangeStatus(Enum):
    """Статус изменения"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PENDING_APPROVAL = "pending_approval"
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
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class ApprovalStatus(Enum):
    """Статус утверждения"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ABSTAINED = "abstained"


@dataclass
class ChangeRequest:
    """Запрос на изменение"""
    change_id: str
    title: str = ""
    
    # Classification
    change_type: ChangeType = ChangeType.NORMAL
    status: ChangeStatus = ChangeStatus.DRAFT
    
    # Description
    description: str = ""
    justification: str = ""
    
    # Scope
    affected_systems: List[str] = field(default_factory=list)
    affected_services: List[str] = field(default_factory=list)
    
    # Risk
    risk_level: RiskLevel = RiskLevel.MEDIUM
    risk_assessment: Dict = field(default_factory=dict)
    
    # Schedule
    planned_start: Optional[datetime] = None
    planned_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    
    # Stakeholders
    requester: str = ""
    implementer: str = ""
    approvers: List[str] = field(default_factory=list)
    
    # Implementation
    implementation_plan: List[str] = field(default_factory=list)
    rollback_plan: List[str] = field(default_factory=list)
    test_plan: List[str] = field(default_factory=list)
    
    # History
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Approvals
    approvals: List[Dict] = field(default_factory=list)


@dataclass
class RiskAssessment:
    """Оценка риска"""
    assessment_id: str
    change_id: str = ""
    
    # Risk factors
    complexity: int = 3  # 1-5
    impact: int = 3  # 1-5
    likelihood: int = 3  # 1-5
    
    # Calculated
    risk_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.MEDIUM
    
    # Questions
    questions_answered: Dict = field(default_factory=dict)
    
    # Mitigations
    mitigations: List[str] = field(default_factory=list)


@dataclass
class Approval:
    """Утверждение"""
    approval_id: str
    change_id: str = ""
    
    # Approver
    approver: str = ""
    role: str = ""  # manager, cab_member, security, etc.
    
    # Decision
    status: ApprovalStatus = ApprovalStatus.PENDING
    comments: str = ""
    
    # Timestamps
    requested_at: datetime = field(default_factory=datetime.now)
    decided_at: Optional[datetime] = None


@dataclass
class CABMeeting:
    """Заседание CAB"""
    meeting_id: str
    
    # Schedule
    scheduled_at: datetime = field(default_factory=datetime.now)
    duration_minutes: int = 60
    
    # Attendees
    attendees: List[str] = field(default_factory=list)
    
    # Agenda
    changes_to_review: List[str] = field(default_factory=list)
    
    # Outcomes
    decisions: Dict[str, str] = field(default_factory=dict)
    minutes: str = ""
    
    # Status
    status: str = "scheduled"  # scheduled, in_progress, completed, cancelled


@dataclass
class ChangeWindow:
    """Окно изменений"""
    window_id: str
    name: str = ""
    
    # Schedule
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime = field(default_factory=datetime.now)
    
    # Recurrence
    recurring: bool = False
    recurrence_pattern: str = ""  # weekly, monthly
    
    # Restrictions
    allowed_types: List[ChangeType] = field(default_factory=list)
    max_changes: int = 5
    
    # Assigned changes
    scheduled_changes: List[str] = field(default_factory=list)


@dataclass
class Blackout:
    """Период запрета изменений"""
    blackout_id: str
    name: str = ""
    
    # Period
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime = field(default_factory=datetime.now)
    
    # Scope
    affected_systems: List[str] = field(default_factory=list)
    
    # Exceptions
    allowed_types: List[ChangeType] = field(default_factory=list)
    
    # Reason
    reason: str = ""


class ChangeRequestManager:
    """Менеджер запросов на изменение"""
    
    def __init__(self):
        self.changes: Dict[str, ChangeRequest] = {}
        
    def create(self, title: str, change_type: ChangeType,
                description: str, requester: str, **kwargs) -> ChangeRequest:
        """Создание запроса"""
        change = ChangeRequest(
            change_id=f"CHG-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}",
            title=title,
            change_type=change_type,
            description=description,
            requester=requester,
            **kwargs
        )
        self.changes[change.change_id] = change
        return change
        
    def submit(self, change_id: str) -> ChangeRequest:
        """Отправка на утверждение"""
        change = self.changes.get(change_id)
        if change and change.status == ChangeStatus.DRAFT:
            change.status = ChangeStatus.SUBMITTED
            change.updated_at = datetime.now()
        return change
        
    def update_status(self, change_id: str, status: ChangeStatus) -> ChangeRequest:
        """Обновление статуса"""
        change = self.changes.get(change_id)
        if change:
            change.status = status
            change.updated_at = datetime.now()
            
            if status == ChangeStatus.IN_PROGRESS:
                change.actual_start = datetime.now()
            elif status in [ChangeStatus.COMPLETED, ChangeStatus.FAILED, ChangeStatus.ROLLED_BACK]:
                change.actual_end = datetime.now()
                
        return change
        
    def get_by_status(self, status: ChangeStatus) -> List[ChangeRequest]:
        """Получение по статусу"""
        return [c for c in self.changes.values() if c.status == status]
        
    def get_pending_approval(self) -> List[ChangeRequest]:
        """Получение ожидающих утверждения"""
        return [
            c for c in self.changes.values()
            if c.status in [ChangeStatus.SUBMITTED, ChangeStatus.PENDING_APPROVAL]
        ]


class RiskAssessor:
    """Оценщик рисков"""
    
    def __init__(self):
        self.assessments: Dict[str, RiskAssessment] = {}
        
    def assess(self, change_id: str, complexity: int, impact: int,
                likelihood: int) -> RiskAssessment:
        """Оценка риска"""
        # Calculate risk score (1-25)
        risk_score = (complexity + impact + likelihood) / 3 * 5
        
        # Determine risk level
        if risk_score >= 20:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 15:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 10:
            risk_level = RiskLevel.MEDIUM
        elif risk_score >= 5:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.MINIMAL
            
        assessment = RiskAssessment(
            assessment_id=f"risk_{uuid.uuid4().hex[:8]}",
            change_id=change_id,
            complexity=complexity,
            impact=impact,
            likelihood=likelihood,
            risk_score=risk_score,
            risk_level=risk_level
        )
        self.assessments[change_id] = assessment
        return assessment
        
    def add_mitigation(self, change_id: str, mitigation: str):
        """Добавление меры снижения риска"""
        assessment = self.assessments.get(change_id)
        if assessment:
            assessment.mitigations.append(mitigation)
            
    def get_assessment(self, change_id: str) -> Optional[RiskAssessment]:
        """Получение оценки"""
        return self.assessments.get(change_id)


class ApprovalWorkflow:
    """Процесс утверждения"""
    
    def __init__(self, change_manager: ChangeRequestManager):
        self.change_manager = change_manager
        self.approvals: Dict[str, List[Approval]] = {}
        
    def request_approval(self, change_id: str, approvers: List[Dict]) -> List[Approval]:
        """Запрос утверждения"""
        change = self.change_manager.changes.get(change_id)
        if not change:
            return []
            
        approvals = []
        for approver_info in approvers:
            approval = Approval(
                approval_id=f"apr_{uuid.uuid4().hex[:8]}",
                change_id=change_id,
                approver=approver_info["name"],
                role=approver_info.get("role", "approver")
            )
            approvals.append(approval)
            
        self.approvals[change_id] = approvals
        change.status = ChangeStatus.PENDING_APPROVAL
        change.approvers = [a.approver for a in approvals]
        
        return approvals
        
    def approve(self, change_id: str, approver: str, comments: str = "") -> Approval:
        """Утверждение"""
        approvals = self.approvals.get(change_id, [])
        
        for approval in approvals:
            if approval.approver == approver and approval.status == ApprovalStatus.PENDING:
                approval.status = ApprovalStatus.APPROVED
                approval.comments = comments
                approval.decided_at = datetime.now()
                
                # Check if all approved
                self._check_all_approved(change_id)
                return approval
                
        return None
        
    def reject(self, change_id: str, approver: str, comments: str = "") -> Approval:
        """Отклонение"""
        approvals = self.approvals.get(change_id, [])
        
        for approval in approvals:
            if approval.approver == approver and approval.status == ApprovalStatus.PENDING:
                approval.status = ApprovalStatus.REJECTED
                approval.comments = comments
                approval.decided_at = datetime.now()
                
                # Reject change
                self.change_manager.update_status(change_id, ChangeStatus.REJECTED)
                return approval
                
        return None
        
    def _check_all_approved(self, change_id: str):
        """Проверка полного утверждения"""
        approvals = self.approvals.get(change_id, [])
        
        if all(a.status == ApprovalStatus.APPROVED for a in approvals):
            self.change_manager.update_status(change_id, ChangeStatus.APPROVED)


class CABManager:
    """Менеджер CAB"""
    
    def __init__(self, change_manager: ChangeRequestManager):
        self.change_manager = change_manager
        self.meetings: Dict[str, CABMeeting] = {}
        self.members: List[str] = []
        
    def add_member(self, member: str):
        """Добавление члена CAB"""
        if member not in self.members:
            self.members.append(member)
            
    def schedule_meeting(self, scheduled_at: datetime,
                          changes: List[str] = None) -> CABMeeting:
        """Планирование заседания"""
        meeting = CABMeeting(
            meeting_id=f"cab_{uuid.uuid4().hex[:8]}",
            scheduled_at=scheduled_at,
            attendees=self.members.copy(),
            changes_to_review=changes or []
        )
        self.meetings[meeting.meeting_id] = meeting
        return meeting
        
    def add_change_to_review(self, meeting_id: str, change_id: str):
        """Добавление изменения на рассмотрение"""
        meeting = self.meetings.get(meeting_id)
        if meeting and change_id not in meeting.changes_to_review:
            meeting.changes_to_review.append(change_id)
            
    def record_decision(self, meeting_id: str, change_id: str,
                         decision: str) -> CABMeeting:
        """Запись решения"""
        meeting = self.meetings.get(meeting_id)
        if meeting:
            meeting.decisions[change_id] = decision
            
            # Update change status
            if decision.lower() == "approved":
                self.change_manager.update_status(change_id, ChangeStatus.APPROVED)
            elif decision.lower() == "rejected":
                self.change_manager.update_status(change_id, ChangeStatus.REJECTED)
                
        return meeting


class ChangeCalendar:
    """Календарь изменений"""
    
    def __init__(self, change_manager: ChangeRequestManager):
        self.change_manager = change_manager
        self.windows: Dict[str, ChangeWindow] = {}
        self.blackouts: Dict[str, Blackout] = {}
        
    def create_window(self, name: str, start: datetime, end: datetime,
                       allowed_types: List[ChangeType] = None) -> ChangeWindow:
        """Создание окна изменений"""
        window = ChangeWindow(
            window_id=f"win_{uuid.uuid4().hex[:8]}",
            name=name,
            start_time=start,
            end_time=end,
            allowed_types=allowed_types or list(ChangeType)
        )
        self.windows[window.window_id] = window
        return window
        
    def create_blackout(self, name: str, start: datetime, end: datetime,
                         reason: str, affected_systems: List[str] = None) -> Blackout:
        """Создание периода запрета"""
        blackout = Blackout(
            blackout_id=f"bo_{uuid.uuid4().hex[:8]}",
            name=name,
            start_time=start,
            end_time=end,
            reason=reason,
            affected_systems=affected_systems or [],
            allowed_types=[ChangeType.EMERGENCY]
        )
        self.blackouts[blackout.blackout_id] = blackout
        return blackout
        
    def schedule_change(self, change_id: str, window_id: str) -> bool:
        """Планирование изменения в окно"""
        window = self.windows.get(window_id)
        change = self.change_manager.changes.get(change_id)
        
        if not window or not change:
            return False
            
        # Check if window allows this change type
        if change.change_type not in window.allowed_types:
            return False
            
        # Check capacity
        if len(window.scheduled_changes) >= window.max_changes:
            return False
            
        window.scheduled_changes.append(change_id)
        change.planned_start = window.start_time
        change.planned_end = window.end_time
        change.status = ChangeStatus.SCHEDULED
        
        return True
        
    def check_blackout(self, change: ChangeRequest) -> Optional[Blackout]:
        """Проверка на период запрета"""
        if not change.planned_start:
            return None
            
        for blackout in self.blackouts.values():
            if (blackout.start_time <= change.planned_start <= blackout.end_time):
                if change.change_type not in blackout.allowed_types:
                    return blackout
                    
        return None
        
    def get_upcoming_changes(self, days: int = 7) -> List[ChangeRequest]:
        """Получение предстоящих изменений"""
        cutoff = datetime.now() + timedelta(days=days)
        upcoming = []
        
        for change in self.change_manager.changes.values():
            if (change.planned_start and 
                datetime.now() <= change.planned_start <= cutoff and
                change.status == ChangeStatus.SCHEDULED):
                upcoming.append(change)
                
        return sorted(upcoming, key=lambda x: x.planned_start)


class ImpactAnalyzer:
    """Анализатор влияния"""
    
    def __init__(self):
        self.dependencies: Dict[str, List[str]] = {}
        
    def add_dependency(self, system: str, depends_on: List[str]):
        """Добавление зависимости"""
        self.dependencies[system] = depends_on
        
    def analyze_impact(self, affected_systems: List[str]) -> Dict:
        """Анализ влияния"""
        impacted = set(affected_systems)
        
        # Find cascading impacts
        for system, deps in self.dependencies.items():
            if any(s in affected_systems for s in deps):
                impacted.add(system)
                
        # Recursively find more impacts
        changed = True
        while changed:
            changed = False
            for system, deps in self.dependencies.items():
                if system not in impacted and any(d in impacted for d in deps):
                    impacted.add(system)
                    changed = True
                    
        return {
            "directly_affected": affected_systems,
            "total_impacted": list(impacted),
            "cascade_count": len(impacted) - len(affected_systems)
        }


class ChangeManagementPlatform:
    """Платформа управления изменениями"""
    
    def __init__(self):
        self.change_manager = ChangeRequestManager()
        self.risk_assessor = RiskAssessor()
        self.approval_workflow = ApprovalWorkflow(self.change_manager)
        self.cab_manager = CABManager(self.change_manager)
        self.calendar = ChangeCalendar(self.change_manager)
        self.impact_analyzer = ImpactAnalyzer()
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        changes = list(self.change_manager.changes.values())
        
        return {
            "total_changes": len(changes),
            "pending_approval": len(self.change_manager.get_pending_approval()),
            "scheduled": len(self.change_manager.get_by_status(ChangeStatus.SCHEDULED)),
            "in_progress": len(self.change_manager.get_by_status(ChangeStatus.IN_PROGRESS)),
            "completed": len(self.change_manager.get_by_status(ChangeStatus.COMPLETED)),
            "failed": len(self.change_manager.get_by_status(ChangeStatus.FAILED)),
            "cab_meetings": len(self.cab_manager.meetings),
            "change_windows": len(self.calendar.windows),
            "blackouts": len(self.calendar.blackouts)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 146: Change Management Platform")
    print("=" * 60)
    
    async def demo():
        platform = ChangeManagementPlatform()
        print("✓ Change Management Platform created")
        
        # Setup CAB members
        print("\n👥 Setting Up CAB...")
        
        cab_members = ["cto@company.com", "vp-eng@company.com", "security-lead@company.com",
                       "infra-lead@company.com", "qa-lead@company.com"]
        
        for member in cab_members:
            platform.cab_manager.add_member(member)
            
        print(f"  ✓ CAB Members: {len(cab_members)}")
        
        # Setup system dependencies
        print("\n🔗 Setting Up Dependencies...")
        
        dependencies = {
            "web-frontend": ["api-gateway"],
            "api-gateway": ["auth-service", "user-service"],
            "user-service": ["database-primary"],
            "order-service": ["database-primary", "payment-service"],
            "payment-service": ["database-primary", "external-gateway"]
        }
        
        for system, deps in dependencies.items():
            platform.impact_analyzer.add_dependency(system, deps)
            
        print(f"  ✓ Systems mapped: {len(dependencies)}")
        
        # Create change windows
        print("\n📅 Creating Change Windows...")
        
        windows = [
            ("Weekly Maintenance", 4, 6),  # Thursday 4-6am
            ("Weekend Deployment", 6, 10),  # Saturday 6-10am
        ]
        
        for name, start_hour, end_hour in windows:
            start = datetime.now().replace(hour=start_hour, minute=0, second=0) + timedelta(days=1)
            end = start.replace(hour=end_hour)
            platform.calendar.create_window(name, start, end)
            print(f"  ✓ {name}: {start.strftime('%a %H:%M')} - {end.strftime('%H:%M')}")
            
        # Create blackout period
        print("\n🚫 Creating Blackout Period...")
        
        blackout_start = datetime.now() + timedelta(days=10)
        blackout = platform.calendar.create_blackout(
            "Q4 Code Freeze",
            blackout_start,
            blackout_start + timedelta(days=14),
            "Year-end code freeze - only emergency changes allowed",
            affected_systems=["all"]
        )
        print(f"  ✓ {blackout.name}: {blackout_start.strftime('%Y-%m-%d')} ({blackout.reason})")
        
        # Create change requests
        print("\n📝 Creating Change Requests...")
        
        changes_data = [
            ("Database Schema Migration", ChangeType.MAJOR, "Add new columns for customer preferences",
             ["database-primary"], 4, 4, 3),
            ("API Gateway Update", ChangeType.NORMAL, "Update to v2.5 with new rate limiting",
             ["api-gateway"], 3, 3, 2),
            ("SSL Certificate Renewal", ChangeType.STANDARD, "Annual SSL certificate renewal",
             ["web-frontend"], 2, 2, 1),
            ("Emergency Security Patch", ChangeType.EMERGENCY, "Critical CVE patch for auth service",
             ["auth-service"], 3, 5, 4)
        ]
        
        changes = []
        for title, change_type, desc, systems, complexity, impact, likelihood in changes_data:
            change = platform.change_manager.create(
                title, change_type, desc, "engineer@company.com",
                affected_systems=systems,
                implementation_plan=["Backup", "Deploy", "Test", "Monitor"],
                rollback_plan=["Restore backup", "Revert code", "Verify"]
            )
            
            # Assess risk
            assessment = platform.risk_assessor.assess(
                change.change_id, complexity, impact, likelihood
            )
            change.risk_level = assessment.risk_level
            change.risk_assessment = {
                "score": assessment.risk_score,
                "complexity": complexity,
                "impact": impact,
                "likelihood": likelihood
            }
            
            changes.append(change)
            
            type_icon = {"standard": "🟢", "normal": "🟡", "emergency": "🔴", "major": "🟠"}
            risk_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢", "minimal": "⚪"}
            
            print(f"\n  {type_icon[change_type.value]} {title}")
            print(f"      Type: {change_type.value} | Risk: {risk_icon[assessment.risk_level.value]} {assessment.risk_level.value} ({assessment.risk_score:.1f})")
            print(f"      ID: {change.change_id}")
            
        # Analyze impact
        print("\n🎯 Impact Analysis...")
        
        for change in changes[:2]:
            impact = platform.impact_analyzer.analyze_impact(change.affected_systems)
            print(f"\n  {change.title}:")
            print(f"    Direct: {impact['directly_affected']}")
            print(f"    Total impacted: {len(impact['total_impacted'])} systems")
            print(f"    Cascade effect: +{impact['cascade_count']} systems")
            
        # Submit and approve
        print("\n✅ Approval Workflow...")
        
        normal_change = changes[1]  # API Gateway Update
        platform.change_manager.submit(normal_change.change_id)
        
        approvers = [
            {"name": "tech-lead@company.com", "role": "tech_lead"},
            {"name": "infra-lead@company.com", "role": "infrastructure"}
        ]
        
        approvals = platform.approval_workflow.request_approval(
            normal_change.change_id, approvers
        )
        
        print(f"\n  Change: {normal_change.title}")
        print(f"  Status: {normal_change.status.value}")
        
        for approver in approvers:
            platform.approval_workflow.approve(
                normal_change.change_id,
                approver["name"],
                "Approved - implementation plan looks good"
            )
            print(f"  ✓ Approved by: {approver['name']}")
            
        print(f"  Final Status: {normal_change.status.value}")
        
        # Schedule CAB meeting
        print("\n📋 Scheduling CAB Meeting...")
        
        major_change = changes[0]  # Database migration
        platform.change_manager.submit(major_change.change_id)
        
        cab_meeting = platform.cab_manager.schedule_meeting(
            datetime.now() + timedelta(days=3),
            changes=[major_change.change_id]
        )
        
        print(f"  Meeting: {cab_meeting.meeting_id}")
        print(f"  Scheduled: {cab_meeting.scheduled_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"  Attendees: {len(cab_meeting.attendees)}")
        print(f"  Changes to review: {len(cab_meeting.changes_to_review)}")
        
        # CAB decision
        platform.cab_manager.record_decision(
            cab_meeting.meeting_id,
            major_change.change_id,
            "approved"
        )
        print(f"  ✓ CAB Decision: {major_change.title} - APPROVED")
        
        # Schedule changes
        print("\n📆 Scheduling Changes...")
        
        window = list(platform.calendar.windows.values())[0]
        
        for change in changes[:2]:
            if change.status == ChangeStatus.APPROVED:
                if platform.calendar.schedule_change(change.change_id, window.window_id):
                    print(f"  ✓ Scheduled: {change.title}")
                    print(f"      Window: {window.name}")
                    
        # Upcoming changes
        print("\n📅 Upcoming Changes (7 days):")
        
        upcoming = platform.calendar.get_upcoming_changes(7)
        for change in upcoming:
            print(f"  • {change.planned_start.strftime('%Y-%m-%d %H:%M')} - {change.title}")
            
        # Execute change
        print("\n🚀 Executing Change...")
        
        executing_change = changes[1]
        platform.change_manager.update_status(executing_change.change_id, ChangeStatus.IN_PROGRESS)
        print(f"  Started: {executing_change.title}")
        
        await asyncio.sleep(0.5)
        
        platform.change_manager.update_status(executing_change.change_id, ChangeStatus.COMPLETED)
        print(f"  ✓ Completed: {executing_change.title}")
        print(f"    Duration: {(executing_change.actual_end - executing_change.actual_start).total_seconds():.1f}s")
        
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Changes: {stats['total_changes']}")
        print(f"  Pending Approval: {stats['pending_approval']}")
        print(f"  Scheduled: {stats['scheduled']}")
        print(f"  In Progress: {stats['in_progress']}")
        print(f"  Completed: {stats['completed']}")
        print(f"  Failed: {stats['failed']}")
        print(f"  CAB Meetings: {stats['cab_meetings']}")
        print(f"  Change Windows: {stats['change_windows']}")
        print(f"  Blackouts: {stats['blackouts']}")
        
        # Dashboard
        print("\n📋 Change Management Dashboard:")
        print("  ┌────────────────────────────────────────────────────────────┐")
        print("  │                Change Management Overview                  │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Changes:       {stats['total_changes']:>10}                    │")
        print(f"  │ Pending Approval:    {stats['pending_approval']:>10}                    │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Scheduled:           {stats['scheduled']:>10}                    │")
        print(f"  │ In Progress:         {stats['in_progress']:>10}                    │")
        print(f"  │ Completed:           {stats['completed']:>10}                    │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ CAB Meetings:        {stats['cab_meetings']:>10}                    │")
        print(f"  │ Change Windows:      {stats['change_windows']:>10}                    │")
        print(f"  │ Blackout Periods:    {stats['blackouts']:>10}                    │")
        print("  └────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Change Management Platform initialized!")
    print("=" * 60)
