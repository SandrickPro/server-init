#!/usr/bin/env python3
"""
Server Init - Iteration 299: Change Management Platform
Платформа управления изменениями

Функционал:
- Change Request Management - управление запросами на изменения
- Impact Assessment - оценка влияния
- Approval Workflow - workflow одобрений
- Change Calendar - календарь изменений
- Risk Analysis - анализ рисков
- Rollback Planning - планирование откатов
- Compliance Tracking - отслеживание compliance
- Audit Trail - аудит действий
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class ChangeType(Enum):
    """Тип изменения"""
    STANDARD = "standard"
    NORMAL = "normal"
    EMERGENCY = "emergency"
    MAJOR = "major"


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


@dataclass
class Approval:
    """Одобрение"""
    approval_id: str
    change_id: str
    
    # Approver
    approver: str = ""
    role: str = ""
    
    # Status
    status: ApprovalStatus = ApprovalStatus.PENDING
    
    # Comment
    comment: str = ""
    
    # Timestamps
    requested_at: datetime = field(default_factory=datetime.now)
    responded_at: Optional[datetime] = None


@dataclass
class ImpactAssessment:
    """Оценка влияния"""
    assessment_id: str
    change_id: str
    
    # Systems
    affected_systems: List[str] = field(default_factory=list)
    affected_services: List[str] = field(default_factory=list)
    
    # Users
    affected_users: int = 0
    user_impact: str = ""
    
    # Downtime
    expected_downtime: int = 0  # minutes
    maintenance_window: bool = False
    
    # Risk
    risk_level: RiskLevel = RiskLevel.MEDIUM
    risk_factors: List[str] = field(default_factory=list)
    
    # Mitigation
    mitigation_steps: List[str] = field(default_factory=list)


@dataclass
class RollbackPlan:
    """План отката"""
    plan_id: str
    change_id: str
    
    # Steps
    steps: List[str] = field(default_factory=list)
    
    # Requirements
    estimated_time: int = 0  # minutes
    required_resources: List[str] = field(default_factory=list)
    
    # Triggers
    rollback_triggers: List[str] = field(default_factory=list)
    
    # Validation
    validation_steps: List[str] = field(default_factory=list)


@dataclass
class ChangeWindow:
    """Окно изменений"""
    window_id: str
    name: str
    
    # Schedule
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    # Type
    window_type: str = "maintenance"  # maintenance, emergency, freeze
    
    # Restrictions
    allowed_categories: List[ChangeCategory] = field(default_factory=list)
    max_risk: RiskLevel = RiskLevel.HIGH
    
    # Status
    active: bool = True


@dataclass
class AuditEntry:
    """Запись аудита"""
    entry_id: str
    change_id: str
    
    # Action
    action: str = ""
    description: str = ""
    
    # Actor
    user: str = ""
    
    # Metadata
    old_value: str = ""
    new_value: str = ""
    
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ChangeRequest:
    """Запрос на изменение"""
    change_id: str
    title: str
    
    # Classification
    change_type: ChangeType = ChangeType.NORMAL
    category: ChangeCategory = ChangeCategory.APPLICATION
    
    # Description
    description: str = ""
    justification: str = ""
    
    # Status
    status: ChangeStatus = ChangeStatus.DRAFT
    
    # Requester
    requester: str = ""
    assignee: str = ""
    
    # Impact
    impact_assessment_id: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.MEDIUM
    
    # Schedule
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    
    # Approvals
    approvals: List[str] = field(default_factory=list)
    required_approvals: int = 1
    
    # Rollback
    rollback_plan_id: Optional[str] = None
    
    # Implementation
    implementation_steps: List[str] = field(default_factory=list)
    
    # Audit
    audit_trail: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class ChangeManagementManager:
    """Менеджер Change Management"""
    
    def __init__(self):
        self.changes: Dict[str, ChangeRequest] = {}
        self.approvals: Dict[str, Approval] = {}
        self.assessments: Dict[str, ImpactAssessment] = {}
        self.rollback_plans: Dict[str, RollbackPlan] = {}
        self.windows: Dict[str, ChangeWindow] = {}
        self.audit_entries: Dict[str, AuditEntry] = {}
        
        # Stats
        self.changes_completed: int = 0
        self.changes_failed: int = 0
        self.rollbacks_executed: int = 0
        
    async def create_change(self, title: str,
                           change_type: ChangeType = ChangeType.NORMAL,
                           category: ChangeCategory = ChangeCategory.APPLICATION,
                           description: str = "",
                           requester: str = "") -> ChangeRequest:
        """Создание запроса на изменение"""
        change = ChangeRequest(
            change_id=f"CHG-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}",
            title=title,
            change_type=change_type,
            category=category,
            description=description,
            requester=requester
        )
        
        # Set required approvals based on type
        approvals_map = {
            ChangeType.STANDARD: 1,
            ChangeType.NORMAL: 2,
            ChangeType.EMERGENCY: 1,
            ChangeType.MAJOR: 3
        }
        change.required_approvals = approvals_map.get(change_type, 2)
        
        self.changes[change.change_id] = change
        
        await self._add_audit(change.change_id, "created", "Change request created", requester)
        
        return change
        
    async def submit_change(self, change_id: str) -> bool:
        """Отправка изменения на рассмотрение"""
        change = self.changes.get(change_id)
        if not change or change.status != ChangeStatus.DRAFT:
            return False
            
        change.status = ChangeStatus.SUBMITTED
        
        await self._add_audit(change_id, "submitted", "Change submitted for review", change.requester)
        
        return True
        
    async def create_impact_assessment(self, change_id: str,
                                       affected_systems: List[str],
                                       affected_services: List[str],
                                       affected_users: int = 0,
                                       expected_downtime: int = 0) -> Optional[ImpactAssessment]:
        """Создание оценки влияния"""
        change = self.changes.get(change_id)
        if not change:
            return None
            
        assessment = ImpactAssessment(
            assessment_id=f"imp_{uuid.uuid4().hex[:8]}",
            change_id=change_id,
            affected_systems=affected_systems,
            affected_services=affected_services,
            affected_users=affected_users,
            expected_downtime=expected_downtime
        )
        
        # Calculate risk level
        assessment.risk_level = self._calculate_risk(
            len(affected_systems),
            len(affected_services),
            affected_users,
            expected_downtime
        )
        
        self.assessments[assessment.assessment_id] = assessment
        change.impact_assessment_id = assessment.assessment_id
        change.risk_level = assessment.risk_level
        
        return assessment
        
    def _calculate_risk(self, systems: int, services: int, 
                       users: int, downtime: int) -> RiskLevel:
        """Расчёт уровня риска"""
        score = 0
        
        score += min(systems * 10, 30)
        score += min(services * 5, 20)
        score += min(users // 100, 25)
        score += min(downtime // 5, 25)
        
        if score >= 80:
            return RiskLevel.CRITICAL
        elif score >= 50:
            return RiskLevel.HIGH
        elif score >= 25:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
            
    async def create_rollback_plan(self, change_id: str,
                                  steps: List[str],
                                  estimated_time: int = 30,
                                  triggers: List[str] = None) -> Optional[RollbackPlan]:
        """Создание плана отката"""
        change = self.changes.get(change_id)
        if not change:
            return None
            
        plan = RollbackPlan(
            plan_id=f"rb_{uuid.uuid4().hex[:8]}",
            change_id=change_id,
            steps=steps,
            estimated_time=estimated_time,
            rollback_triggers=triggers or []
        )
        
        self.rollback_plans[plan.plan_id] = plan
        change.rollback_plan_id = plan.plan_id
        
        return plan
        
    async def request_approval(self, change_id: str, approver: str, role: str) -> Optional[Approval]:
        """Запрос одобрения"""
        change = self.changes.get(change_id)
        if not change:
            return None
            
        approval = Approval(
            approval_id=f"apr_{uuid.uuid4().hex[:8]}",
            change_id=change_id,
            approver=approver,
            role=role
        )
        
        self.approvals[approval.approval_id] = approval
        change.approvals.append(approval.approval_id)
        change.status = ChangeStatus.UNDER_REVIEW
        
        await self._add_audit(change_id, "approval_requested", f"Approval requested from {approver}", change.requester)
        
        return approval
        
    async def approve_change(self, approval_id: str, comment: str = "") -> bool:
        """Одобрение изменения"""
        approval = self.approvals.get(approval_id)
        if not approval:
            return False
            
        approval.status = ApprovalStatus.APPROVED
        approval.comment = comment
        approval.responded_at = datetime.now()
        
        change = self.changes.get(approval.change_id)
        if change:
            await self._add_audit(change.change_id, "approved", f"Approved by {approval.approver}", approval.approver)
            
            # Check if all required approvals received
            approved_count = sum(
                1 for a_id in change.approvals
                if self.approvals.get(a_id, Approval(approval_id="", change_id="")).status == ApprovalStatus.APPROVED
            )
            
            if approved_count >= change.required_approvals:
                change.status = ChangeStatus.APPROVED
                
        return True
        
    async def reject_change(self, approval_id: str, reason: str) -> bool:
        """Отклонение изменения"""
        approval = self.approvals.get(approval_id)
        if not approval:
            return False
            
        approval.status = ApprovalStatus.REJECTED
        approval.comment = reason
        approval.responded_at = datetime.now()
        
        change = self.changes.get(approval.change_id)
        if change:
            change.status = ChangeStatus.REJECTED
            await self._add_audit(change.change_id, "rejected", f"Rejected by {approval.approver}: {reason}", approval.approver)
            
        return True
        
    async def schedule_change(self, change_id: str,
                             start_time: datetime,
                             end_time: datetime) -> bool:
        """Планирование изменения"""
        change = self.changes.get(change_id)
        if not change or change.status != ChangeStatus.APPROVED:
            return False
            
        change.scheduled_start = start_time
        change.scheduled_end = end_time
        change.status = ChangeStatus.SCHEDULED
        
        await self._add_audit(change_id, "scheduled", f"Scheduled for {start_time}", change.assignee or change.requester)
        
        return True
        
    async def start_change(self, change_id: str) -> bool:
        """Начало выполнения изменения"""
        change = self.changes.get(change_id)
        if not change or change.status != ChangeStatus.SCHEDULED:
            return False
            
        change.status = ChangeStatus.IN_PROGRESS
        
        await self._add_audit(change_id, "started", "Implementation started", change.assignee or change.requester)
        
        return True
        
    async def complete_change(self, change_id: str, success: bool = True) -> bool:
        """Завершение изменения"""
        change = self.changes.get(change_id)
        if not change:
            return False
            
        if success:
            change.status = ChangeStatus.COMPLETED
            change.completed_at = datetime.now()
            self.changes_completed += 1
            await self._add_audit(change_id, "completed", "Implementation completed successfully", change.assignee)
        else:
            change.status = ChangeStatus.FAILED
            self.changes_failed += 1
            await self._add_audit(change_id, "failed", "Implementation failed", change.assignee)
            
        return True
        
    async def execute_rollback(self, change_id: str) -> bool:
        """Выполнение отката"""
        change = self.changes.get(change_id)
        if not change:
            return False
            
        change.status = ChangeStatus.ROLLED_BACK
        self.rollbacks_executed += 1
        
        await self._add_audit(change_id, "rolled_back", "Rollback executed", change.assignee)
        
        return True
        
    async def create_change_window(self, name: str,
                                  start_time: datetime,
                                  end_time: datetime,
                                  window_type: str = "maintenance") -> ChangeWindow:
        """Создание окна изменений"""
        window = ChangeWindow(
            window_id=f"win_{uuid.uuid4().hex[:8]}",
            name=name,
            start_time=start_time,
            end_time=end_time,
            window_type=window_type
        )
        
        self.windows[window.window_id] = window
        return window
        
    async def _add_audit(self, change_id: str, action: str, 
                        description: str, user: str = "") -> AuditEntry:
        """Добавление записи аудита"""
        entry = AuditEntry(
            entry_id=f"aud_{uuid.uuid4().hex[:8]}",
            change_id=change_id,
            action=action,
            description=description,
            user=user
        )
        
        self.audit_entries[entry.entry_id] = entry
        
        change = self.changes.get(change_id)
        if change:
            change.audit_trail.append(entry.entry_id)
            
        return entry
        
    def get_change_summary(self, change_id: str) -> Dict[str, Any]:
        """Сводка по изменению"""
        change = self.changes.get(change_id)
        if not change:
            return {}
            
        approved = sum(1 for a_id in change.approvals
                      if self.approvals.get(a_id, Approval(approval_id="", change_id="")).status == ApprovalStatus.APPROVED)
                      
        return {
            "change_id": change_id,
            "title": change.title,
            "type": change.change_type.value,
            "category": change.category.value,
            "status": change.status.value,
            "risk": change.risk_level.value,
            "approvals": f"{approved}/{change.required_approvals}",
            "requester": change.requester,
            "assignee": change.assignee
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        pending = sum(1 for c in self.changes.values() 
                     if c.status in [ChangeStatus.DRAFT, ChangeStatus.SUBMITTED, ChangeStatus.UNDER_REVIEW])
        approved = sum(1 for c in self.changes.values() if c.status == ChangeStatus.APPROVED)
        scheduled = sum(1 for c in self.changes.values() if c.status == ChangeStatus.SCHEDULED)
        in_progress = sum(1 for c in self.changes.values() if c.status == ChangeStatus.IN_PROGRESS)
        
        risk_counts = {}
        for risk in RiskLevel:
            risk_counts[risk.value] = sum(1 for c in self.changes.values() if c.risk_level == risk)
            
        category_counts = {}
        for cat in ChangeCategory:
            category_counts[cat.value] = sum(1 for c in self.changes.values() if c.category == cat)
            
        return {
            "total_changes": len(self.changes),
            "pending": pending,
            "approved": approved,
            "scheduled": scheduled,
            "in_progress": in_progress,
            "completed": self.changes_completed,
            "failed": self.changes_failed,
            "rolled_back": self.rollbacks_executed,
            "risk_breakdown": risk_counts,
            "category_breakdown": category_counts,
            "total_approvals": len(self.approvals),
            "audit_entries": len(self.audit_entries)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 299: Change Management Platform")
    print("=" * 60)
    
    manager = ChangeManagementManager()
    print("✓ Change Management Manager created")
    
    # Create change windows
    print("\n📅 Creating Change Windows...")
    
    now = datetime.now()
    
    windows_data = [
        ("Weekly Maintenance", now + timedelta(days=3), now + timedelta(days=3, hours=4), "maintenance"),
        ("Emergency Window", now, now + timedelta(hours=2), "emergency"),
        ("Change Freeze", now + timedelta(days=7), now + timedelta(days=14), "freeze")
    ]
    
    for name, start, end, w_type in windows_data:
        window = await manager.create_change_window(name, start, end, w_type)
        print(f"  📅 {name} ({w_type}): {start.strftime('%Y-%m-%d %H:%M')} - {end.strftime('%Y-%m-%d %H:%M')}")
        
    # Create change requests
    print("\n📝 Creating Change Requests...")
    
    changes_data = [
        ("Database Server Upgrade", ChangeType.MAJOR, ChangeCategory.DATABASE,
         "Upgrade PostgreSQL from 13 to 15", "dba@company.com"),
        ("API Gateway Configuration", ChangeType.NORMAL, ChangeCategory.CONFIGURATION,
         "Update rate limiting rules", "devops@company.com"),
        ("Network Security Update", ChangeType.NORMAL, ChangeCategory.SECURITY,
         "Apply firewall rule changes", "security@company.com"),
        ("Application Deployment", ChangeType.STANDARD, ChangeCategory.APPLICATION,
         "Deploy version 2.5.0", "dev@company.com"),
        ("Emergency Hotfix", ChangeType.EMERGENCY, ChangeCategory.APPLICATION,
         "Critical security patch", "security@company.com")
    ]
    
    changes = []
    for title, c_type, category, desc, requester in changes_data:
        change = await manager.create_change(title, c_type, category, desc, requester)
        changes.append(change)
        
        type_icons = {
            ChangeType.STANDARD: "🟢",
            ChangeType.NORMAL: "🟡",
            ChangeType.EMERGENCY: "🔴",
            ChangeType.MAJOR: "🟠"
        }
        icon = type_icons.get(c_type, "⚪")
        
        print(f"\n  {icon} [{change.change_id}] {title}")
        print(f"     Type: {c_type.value} | Category: {category.value}")
        print(f"     Required Approvals: {change.required_approvals}")
        
    # Create impact assessments
    print("\n📊 Creating Impact Assessments...")
    
    for change in changes[:3]:
        assessment = await manager.create_impact_assessment(
            change.change_id,
            affected_systems=[f"system-{i}" for i in range(random.randint(1, 5))],
            affected_services=[f"service-{i}" for i in range(random.randint(2, 6))],
            affected_users=random.randint(100, 10000),
            expected_downtime=random.randint(0, 60)
        )
        
        risk_icons = {
            RiskLevel.LOW: "🟢",
            RiskLevel.MEDIUM: "🟡",
            RiskLevel.HIGH: "🟠",
            RiskLevel.CRITICAL: "🔴"
        }
        icon = risk_icons.get(assessment.risk_level, "⚪")
        
        print(f"\n  📊 {change.title[:30]}")
        print(f"     Risk: {icon} {assessment.risk_level.value}")
        print(f"     Systems: {len(assessment.affected_systems)} | Services: {len(assessment.affected_services)}")
        print(f"     Users: {assessment.affected_users} | Downtime: {assessment.expected_downtime}min")
        
    # Create rollback plans
    print("\n⏪ Creating Rollback Plans...")
    
    for change in changes[:2]:
        plan = await manager.create_rollback_plan(
            change.change_id,
            steps=[
                "Stop service traffic",
                "Revert configuration",
                "Restart services",
                "Verify functionality",
                "Resume traffic"
            ],
            estimated_time=random.randint(15, 45),
            triggers=[
                "Error rate > 5%",
                "Response time > 5s",
                "Health check failures"
            ]
        )
        
        print(f"  ⏪ {change.title[:30]}: {plan.estimated_time}min rollback time")
        
    # Submit changes
    print("\n📤 Submitting Changes...")
    
    for change in changes:
        await manager.submit_change(change.change_id)
        
    print(f"  📤 Submitted {len(changes)} changes for review")
    
    # Request approvals
    print("\n✍️ Requesting Approvals...")
    
    approvers = [
        ("manager@company.com", "Change Manager"),
        ("tech-lead@company.com", "Technical Lead"),
        ("security@company.com", "Security Officer")
    ]
    
    for change in changes:
        for approver, role in approvers[:change.required_approvals]:
            approval = await manager.request_approval(change.change_id, approver, role)
            
    print(f"  ✍️ Requested {len(manager.approvals)} approvals")
    
    # Approve changes
    print("\n✅ Processing Approvals...")
    
    approved_count = 0
    for approval in list(manager.approvals.values()):
        if random.random() > 0.15:  # 85% approval rate
            await manager.approve_change(approval.approval_id, "Looks good to proceed")
            approved_count += 1
        else:
            await manager.reject_change(approval.approval_id, "Needs more testing")
            
    print(f"  ✅ Approved: {approved_count} | ❌ Rejected: {len(manager.approvals) - approved_count}")
    
    # Schedule approved changes
    print("\n📅 Scheduling Changes...")
    
    scheduled_count = 0
    for change in changes:
        if change.status == ChangeStatus.APPROVED:
            start = now + timedelta(hours=random.randint(1, 48))
            end = start + timedelta(hours=random.randint(1, 4))
            await manager.schedule_change(change.change_id, start, end)
            scheduled_count += 1
            
    print(f"  📅 Scheduled {scheduled_count} changes")
    
    # Execute some changes
    print("\n🚀 Executing Changes...")
    
    for change in changes:
        if change.status == ChangeStatus.SCHEDULED:
            await manager.start_change(change.change_id)
            
            # Simulate execution
            success = random.random() > 0.1  # 90% success rate
            await manager.complete_change(change.change_id, success)
            
            status = "✅" if success else "❌"
            print(f"  {status} {change.title[:40]}")
            
    # Execute rollback for failed change
    for change in changes:
        if change.status == ChangeStatus.FAILED and change.rollback_plan_id:
            await manager.execute_rollback(change.change_id)
            print(f"  ⏪ Rolled back: {change.title[:40]}")
            
    # Change summary table
    print("\n📊 Change Request Summary:")
    
    print("\n  ┌──────────────────────┬──────────┬──────────────┬────────────┬──────────┐")
    print("  │ Change ID            │ Type     │ Status       │ Risk       │ Approvals│")
    print("  ├──────────────────────┼──────────┼──────────────┼────────────┼──────────┤")
    
    for change in changes:
        summary = manager.get_change_summary(change.change_id)
        
        c_id = change.change_id[:20].ljust(20)
        c_type = summary['type'][:8].ljust(8)
        
        status_icons = {
            "draft": "📝",
            "submitted": "📤",
            "under_review": "🔍",
            "approved": "✅",
            "rejected": "❌",
            "scheduled": "📅",
            "in_progress": "🔄",
            "completed": "✅",
            "failed": "❌",
            "rolled_back": "⏪"
        }
        status = f"{status_icons.get(summary['status'], '⚪')} {summary['status'][:10]}".ljust(12)
        
        risk_icons = {
            "low": "🟢",
            "medium": "🟡",
            "high": "🟠",
            "critical": "🔴"
        }
        risk = f"{risk_icons.get(summary['risk'], '⚪')} {summary['risk'][:6]}".ljust(10)
        
        approvals = summary['approvals'].ljust(8)
        
        print(f"  │ {c_id} │ {c_type} │ {status} │ {risk} │ {approvals} │")
        
    print("  └──────────────────────┴──────────┴──────────────┴────────────┴──────────┘")
    
    # Audit trail for first change
    print("\n📋 Audit Trail (First Change):")
    
    for entry_id in changes[0].audit_trail[:6]:
        entry = manager.audit_entries.get(entry_id)
        if entry:
            time_str = entry.timestamp.strftime("%H:%M:%S")
            user = f"[{entry.user}]" if entry.user else "[system]"
            print(f"  {time_str} {user:25} {entry.action}: {entry.description[:40]}")
            
    # Risk distribution
    print("\n📊 Risk Distribution:")
    
    stats = manager.get_statistics()
    
    for risk, count in stats['risk_breakdown'].items():
        bar = "█" * count + "░" * (5 - count)
        risk_icons = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}
        icon = risk_icons.get(risk, "⚪")
        print(f"  {icon} {risk.upper():10} [{bar}] {count}")
        
    # Category distribution
    print("\n📊 Category Distribution:")
    
    for cat, count in stats['category_breakdown'].items():
        if count > 0:
            bar = "█" * count + "░" * (5 - count)
            print(f"  {cat:15} [{bar}] {count}")
            
    # Statistics
    print("\n📊 Change Management Statistics:")
    
    print(f"\n  Total Changes: {stats['total_changes']}")
    print(f"    Pending: {stats['pending']}")
    print(f"    Approved: {stats['approved']}")
    print(f"    Scheduled: {stats['scheduled']}")
    print(f"    In Progress: {stats['in_progress']}")
    print(f"\n  Completed: {stats['completed']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Rolled Back: {stats['rolled_back']}")
    print(f"\n  Total Approvals: {stats['total_approvals']}")
    print(f"  Audit Entries: {stats['audit_entries']}")
    
    success_rate = (stats['completed'] / max(stats['completed'] + stats['failed'], 1)) * 100
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Change Management Dashboard                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Changes:                 {stats['total_changes']:>12}                        │")
    print(f"│ Pending Review:                {stats['pending']:>12}                        │")
    print(f"│ Completed:                     {stats['completed']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Success Rate:                  {success_rate:>11.1f}%                        │")
    print(f"│ Rollbacks:                     {stats['rolled_back']:>12}                        │")
    print(f"│ Audit Trail Entries:           {stats['audit_entries']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Change Management Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
