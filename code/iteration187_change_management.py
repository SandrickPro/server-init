#!/usr/bin/env python3
"""
Server Init - Iteration 187: Change Management Platform
Платформа управления изменениями

Функционал:
- Change Requests - запросы на изменение
- Approval Workflows - процессы согласования
- Impact Assessment - оценка влияния
- Change Calendar - календарь изменений
- Rollback Planning - планирование отката
- Risk Assessment - оценка рисков
- Change Windows - окна изменений
- Post-Implementation Review - обзор после внедрения
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


class ImpactLevel(Enum):
    """Уровень влияния"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    SEVERE = "severe"


class Priority(Enum):
    """Приоритет"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class ApprovalStep:
    """Шаг согласования"""
    step_id: str
    step_name: str = ""
    step_order: int = 0
    
    # Approver
    approver_role: str = ""
    approver_id: Optional[str] = None
    
    # Status
    approved: Optional[bool] = None
    decision_at: Optional[datetime] = None
    comments: str = ""
    
    # Required
    required: bool = True


@dataclass
class ChangeRequest:
    """Запрос на изменение"""
    change_id: str
    title: str = ""
    description: str = ""
    
    # Type
    change_type: ChangeType = ChangeType.NORMAL
    
    # Status
    status: ChangeStatus = ChangeStatus.DRAFT
    
    # Risk & Impact
    risk_level: RiskLevel = RiskLevel.MEDIUM
    impact_level: ImpactLevel = ImpactLevel.MEDIUM
    priority: Priority = Priority.MEDIUM
    
    # Requester
    requester_id: str = ""
    requester_name: str = ""
    team: str = ""
    
    # Affected
    affected_systems: List[str] = field(default_factory=list)
    affected_services: List[str] = field(default_factory=list)
    affected_users: int = 0
    
    # Schedule
    requested_date: Optional[datetime] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    
    # Implementation
    implementation_plan: str = ""
    rollback_plan: str = ""
    test_plan: str = ""
    
    # Approvals
    approvals: List[ApprovalStep] = field(default_factory=list)
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    # Metadata
    tags: List[str] = field(default_factory=list)


@dataclass
class ChangeWindow:
    """Окно изменений"""
    window_id: str
    name: str = ""
    description: str = ""
    
    # Time
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    # Recurrence
    recurring: bool = False
    recurrence_pattern: str = ""  # weekly, monthly, etc.
    day_of_week: Optional[int] = None
    
    # Restrictions
    max_changes: int = 0
    allowed_types: List[ChangeType] = field(default_factory=list)
    
    # Status
    active: bool = True


@dataclass
class ImpactAssessment:
    """Оценка влияния"""
    assessment_id: str
    change_id: str = ""
    
    # Impact areas
    service_impact: ImpactLevel = ImpactLevel.NONE
    user_impact: ImpactLevel = ImpactLevel.NONE
    business_impact: ImpactLevel = ImpactLevel.NONE
    security_impact: ImpactLevel = ImpactLevel.NONE
    
    # Duration
    estimated_downtime: int = 0  # minutes
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    
    # Mitigation
    mitigation_steps: List[str] = field(default_factory=list)


@dataclass
class PostImplementationReview:
    """Обзор после внедрения"""
    review_id: str
    change_id: str = ""
    
    # Outcome
    success: bool = True
    
    # Metrics
    actual_duration: int = 0  # minutes
    planned_duration: int = 0
    
    # Issues
    issues_encountered: List[str] = field(default_factory=list)
    
    # Lessons
    lessons_learned: List[str] = field(default_factory=list)
    
    # Ratings
    execution_rating: int = 0  # 1-5
    planning_rating: int = 0
    communication_rating: int = 0
    
    # Timing
    review_date: datetime = field(default_factory=datetime.now)


class ApprovalWorkflow:
    """Процесс согласования"""
    
    def __init__(self):
        self.workflows: Dict[ChangeType, List[str]] = {
            ChangeType.STANDARD: ["tech_lead"],
            ChangeType.NORMAL: ["tech_lead", "change_manager", "service_owner"],
            ChangeType.EMERGENCY: ["on_call_manager"],
            ChangeType.EXPEDITED: ["change_manager", "director"],
        }
        
    def create_approval_steps(self, change: ChangeRequest) -> List[ApprovalStep]:
        """Создание шагов согласования"""
        roles = self.workflows.get(change.change_type, ["change_manager"])
        
        steps = []
        for i, role in enumerate(roles):
            step = ApprovalStep(
                step_id=f"step_{uuid.uuid4().hex[:8]}",
                step_name=f"Approval by {role.replace('_', ' ').title()}",
                step_order=i + 1,
                approver_role=role,
                required=True
            )
            steps.append(step)
            
        return steps
        
    def process_approval(self, change: ChangeRequest, step_id: str, 
                        approved: bool, approver_id: str, comments: str = "") -> bool:
        """Обработка согласования"""
        for step in change.approvals:
            if step.step_id == step_id:
                step.approved = approved
                step.approver_id = approver_id
                step.decision_at = datetime.now()
                step.comments = comments
                
                # Update change status
                if not approved:
                    change.status = ChangeStatus.REJECTED
                elif all(s.approved for s in change.approvals if s.required):
                    change.status = ChangeStatus.APPROVED
                    
                return True
        return False


class RiskAssessor:
    """Оценка рисков"""
    
    def assess(self, change: ChangeRequest) -> Dict[str, Any]:
        """Оценка риска изменения"""
        score = 0
        factors = []
        
        # Change type risk
        type_scores = {
            ChangeType.STANDARD: 1,
            ChangeType.NORMAL: 2,
            ChangeType.EXPEDITED: 3,
            ChangeType.EMERGENCY: 4,
        }
        score += type_scores.get(change.change_type, 2)
        
        # Affected systems
        if len(change.affected_systems) > 5:
            score += 3
            factors.append("Many affected systems")
        elif len(change.affected_systems) > 2:
            score += 2
            factors.append("Multiple affected systems")
            
        # Affected users
        if change.affected_users > 10000:
            score += 3
            factors.append("Large user base affected")
        elif change.affected_users > 1000:
            score += 2
            factors.append("Significant user impact")
            
        # Rollback plan
        if not change.rollback_plan:
            score += 2
            factors.append("No rollback plan")
            
        # Test plan
        if not change.test_plan:
            score += 1
            factors.append("No test plan")
            
        # Determine risk level
        if score >= 10:
            risk_level = RiskLevel.CRITICAL
        elif score >= 7:
            risk_level = RiskLevel.HIGH
        elif score >= 4:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
            
        return {
            "risk_level": risk_level,
            "risk_score": score,
            "factors": factors,
            "recommendations": self._get_recommendations(risk_level, factors)
        }
        
    def _get_recommendations(self, risk_level: RiskLevel, factors: List[str]) -> List[str]:
        """Получение рекомендаций"""
        recommendations = []
        
        if "No rollback plan" in factors:
            recommendations.append("Create detailed rollback plan")
        if "No test plan" in factors:
            recommendations.append("Develop comprehensive test plan")
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append("Schedule during maintenance window")
            recommendations.append("Have additional support on standby")
            
        return recommendations


class ChangeCalendar:
    """Календарь изменений"""
    
    def __init__(self):
        self.scheduled_changes: Dict[str, ChangeRequest] = {}
        self.windows: Dict[str, ChangeWindow] = {}
        self.blackout_dates: List[datetime] = []
        
    def schedule_change(self, change: ChangeRequest, start: datetime, end: datetime) -> bool:
        """Планирование изменения"""
        # Check blackout dates
        for blackout in self.blackout_dates:
            if blackout.date() == start.date():
                return False
                
        # Check conflicts
        conflicts = self.get_conflicts(start, end)
        if conflicts:
            return False
            
        change.scheduled_start = start
        change.scheduled_end = end
        change.status = ChangeStatus.SCHEDULED
        self.scheduled_changes[change.change_id] = change
        
        return True
        
    def get_conflicts(self, start: datetime, end: datetime) -> List[ChangeRequest]:
        """Поиск конфликтов"""
        conflicts = []
        
        for change in self.scheduled_changes.values():
            if change.scheduled_start and change.scheduled_end:
                if start < change.scheduled_end and end > change.scheduled_start:
                    conflicts.append(change)
                    
        return conflicts
        
    def get_changes_for_date(self, date: datetime) -> List[ChangeRequest]:
        """Получение изменений на дату"""
        return [
            c for c in self.scheduled_changes.values()
            if c.scheduled_start and c.scheduled_start.date() == date.date()
        ]
        
    def add_blackout(self, date: datetime):
        """Добавление blackout даты"""
        self.blackout_dates.append(date)


class ChangeManagementPlatform:
    """Платформа управления изменениями"""
    
    def __init__(self):
        self.changes: Dict[str, ChangeRequest] = {}
        self.approval_workflow = ApprovalWorkflow()
        self.risk_assessor = RiskAssessor()
        self.calendar = ChangeCalendar()
        self.reviews: Dict[str, PostImplementationReview] = {}
        
    async def create_change(self, title: str, description: str, 
                           change_type: ChangeType, requester_id: str) -> ChangeRequest:
        """Создание изменения"""
        change = ChangeRequest(
            change_id=f"CHG-{uuid.uuid4().hex[:8].upper()}",
            title=title,
            description=description,
            change_type=change_type,
            requester_id=requester_id
        )
        
        # Create approval steps
        change.approvals = self.approval_workflow.create_approval_steps(change)
        
        self.changes[change.change_id] = change
        return change
        
    async def submit_change(self, change_id: str) -> bool:
        """Отправка на согласование"""
        change = self.changes.get(change_id)
        if change and change.status == ChangeStatus.DRAFT:
            # Assess risk
            risk = self.risk_assessor.assess(change)
            change.risk_level = risk["risk_level"]
            
            change.status = ChangeStatus.SUBMITTED
            return True
        return False
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        changes = list(self.changes.values())
        
        return {
            "total_changes": len(changes),
            "by_status": {
                status.value: len([c for c in changes if c.status == status])
                for status in ChangeStatus
            },
            "by_type": {
                ctype.value: len([c for c in changes if c.change_type == ctype])
                for ctype in ChangeType
            },
            "by_risk": {
                risk.value: len([c for c in changes if c.risk_level == risk])
                for risk in RiskLevel
            },
            "total_reviews": len(self.reviews),
            "scheduled_count": len(self.calendar.scheduled_changes)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 187: Change Management Platform")
    print("=" * 60)
    
    async def demo():
        platform = ChangeManagementPlatform()
        print("✓ Change Management Platform created")
        
        # Create changes
        print("\n📝 Creating Change Requests...")
        
        changes_data = [
            ("Database Schema Migration", "Migrate user table to new schema with additional columns", ChangeType.NORMAL, "user123"),
            ("Security Patch Deployment", "Deploy critical security patch to all production servers", ChangeType.EMERGENCY, "secops"),
            ("API Version Upgrade", "Upgrade REST API from v2 to v3", ChangeType.NORMAL, "api-team"),
            ("Infrastructure Scaling", "Add 5 new application servers to handle increased load", ChangeType.STANDARD, "infra-team"),
            ("SSL Certificate Renewal", "Renew and deploy SSL certificates before expiration", ChangeType.EXPEDITED, "ops-team"),
        ]
        
        changes = []
        for title, desc, ctype, requester in changes_data:
            change = await platform.create_change(title, desc, ctype, requester)
            
            # Add details
            change.affected_systems = random.sample(["app-server", "db-server", "cache", "lb", "api-gateway", "cdn"], random.randint(1, 4))
            change.affected_users = random.randint(100, 50000)
            change.implementation_plan = "Step-by-step implementation plan..."
            change.rollback_plan = "Rollback to previous version..." if random.random() > 0.3 else ""
            change.test_plan = "Test plan with validation steps..."
            
            changes.append(change)
            print(f"  ✓ {change.change_id}: {change.title}")
            
        # Show change requests
        print("\n📋 Change Requests:")
        
        print("\n  ┌─────────────────┬─────────────────────────────────────────┬────────────┬──────────┐")
        print("  │ Change ID       │ Title                                   │ Type       │ Status   │")
        print("  ├─────────────────┼─────────────────────────────────────────┼────────────┼──────────┤")
        
        for change in changes:
            cid = change.change_id[:15].ljust(15)
            title = change.title[:39].ljust(39)
            ctype = change.change_type.value[:10].ljust(10)
            status = change.status.value[:8].ljust(8)
            print(f"  │ {cid} │ {title} │ {ctype} │ {status} │")
            
        print("  └─────────────────┴─────────────────────────────────────────┴────────────┴──────────┘")
        
        # Submit changes
        print("\n📤 Submitting Changes for Approval...")
        
        for change in changes:
            await platform.submit_change(change.change_id)
            print(f"  ✓ {change.change_id} submitted (Risk: {change.risk_level.value})")
            
        # Risk assessment
        print("\n⚠️ Risk Assessment:")
        
        for change in changes:
            risk = platform.risk_assessor.assess(change)
            
            icon = "🟢" if risk['risk_level'] == RiskLevel.LOW else ("🟡" if risk['risk_level'] == RiskLevel.MEDIUM else "🔴")
            print(f"\n  {icon} {change.change_id}: {change.title}")
            print(f"     Risk Level: {risk['risk_level'].value.upper()}")
            print(f"     Risk Score: {risk['risk_score']}")
            
            if risk['factors']:
                print(f"     Factors: {', '.join(risk['factors'])}")
            if risk['recommendations']:
                print(f"     Recommendations:")
                for rec in risk['recommendations'][:2]:
                    print(f"       • {rec}")
                    
        # Approval workflow
        print("\n✅ Processing Approvals...")
        
        for change in changes[:3]:
            change.status = ChangeStatus.UNDER_REVIEW
            
            for step in change.approvals:
                approved = random.random() > 0.2
                platform.approval_workflow.process_approval(
                    change, step.step_id, approved, 
                    f"approver_{step.approver_role}",
                    "Approved after review" if approved else "Needs more details"
                )
                
                status = "✓" if step.approved else "✗"
                print(f"  {status} {change.change_id}: {step.step_name}")
                
                if not approved:
                    break
                    
        # Show approval status
        print("\n📊 Approval Status:")
        
        for change in changes[:3]:
            approved_count = len([s for s in change.approvals if s.approved])
            total = len(change.approvals)
            
            print(f"\n  {change.change_id}:")
            print(f"    Status: {change.status.value.replace('_', ' ').title()}")
            print(f"    Approvals: {approved_count}/{total}")
            
            for step in change.approvals:
                icon = "✓" if step.approved else ("✗" if step.approved == False else "○")
                print(f"      {icon} {step.step_name}")
                
        # Schedule changes
        print("\n📅 Scheduling Changes...")
        
        # Add maintenance windows
        platform.calendar.windows["mw1"] = ChangeWindow(
            window_id="mw1",
            name="Weekly Maintenance Window",
            start_time=datetime.now().replace(hour=2, minute=0),
            end_time=datetime.now().replace(hour=6, minute=0),
            recurring=True,
            recurrence_pattern="weekly",
            day_of_week=6  # Sunday
        )
        
        # Add blackout dates
        platform.calendar.add_blackout(datetime.now() + timedelta(days=30))  # Month end
        
        # Schedule approved changes
        for change in changes:
            if change.status == ChangeStatus.APPROVED:
                start = datetime.now() + timedelta(days=random.randint(1, 7))
                end = start + timedelta(hours=2)
                
                if platform.calendar.schedule_change(change, start, end):
                    print(f"  ✓ {change.change_id}: {start.strftime('%Y-%m-%d %H:%M')}")
                    
        # Change calendar view
        print("\n📆 Change Calendar (Next 7 Days):")
        
        for day_offset in range(7):
            date = datetime.now() + timedelta(days=day_offset)
            changes_on_day = platform.calendar.get_changes_for_date(date)
            
            if changes_on_day:
                print(f"\n  {date.strftime('%Y-%m-%d (%A)')}:")
                for c in changes_on_day:
                    print(f"    • {c.scheduled_start.strftime('%H:%M')}: {c.title[:40]}")
                    
        # Execute and complete changes
        print("\n🚀 Executing Changes...")
        
        for change in platform.calendar.scheduled_changes.values():
            change.status = ChangeStatus.IN_PROGRESS
            await asyncio.sleep(0.01)
            
            success = random.random() > 0.1
            change.status = ChangeStatus.COMPLETED if success else ChangeStatus.FAILED
            change.completed_at = datetime.now()
            
            icon = "✓" if success else "✗"
            print(f"  {icon} {change.change_id}: {change.status.value}")
            
            # Create PIR
            review = PostImplementationReview(
                review_id=f"PIR-{uuid.uuid4().hex[:8]}",
                change_id=change.change_id,
                success=success,
                actual_duration=random.randint(30, 180),
                planned_duration=120,
                execution_rating=random.randint(3, 5) if success else random.randint(1, 3),
                planning_rating=random.randint(3, 5),
                communication_rating=random.randint(3, 5)
            )
            
            if not success:
                review.issues_encountered = ["Unexpected database lock", "Timeout during migration"]
                
            review.lessons_learned = ["Start migration earlier", "Add more validation steps"]
            platform.reviews[review.review_id] = review
            
        # Post-Implementation Review
        print("\n📝 Post-Implementation Reviews:")
        
        for review in platform.reviews.values():
            change = platform.changes.get(review.change_id)
            if change:
                icon = "✓" if review.success else "✗"
                print(f"\n  {icon} {change.change_id}: {change.title}")
                print(f"     Success: {'Yes' if review.success else 'No'}")
                print(f"     Duration: {review.actual_duration}min (planned: {review.planned_duration}min)")
                print(f"     Execution Rating: {'⭐' * review.execution_rating}")
                
                if review.issues_encountered:
                    print(f"     Issues: {', '.join(review.issues_encountered[:2])}")
                    
        # Platform statistics
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Changes: {stats['total_changes']}")
        print(f"  Scheduled: {stats['scheduled_count']}")
        print(f"  Reviews: {stats['total_reviews']}")
        
        print("\n  By Status:")
        for status, count in stats['by_status'].items():
            if count > 0:
                print(f"    • {status}: {count}")
                
        print("\n  By Risk Level:")
        for risk, count in stats['by_risk'].items():
            if count > 0:
                icon = "🟢" if risk == "low" else ("🟡" if risk == "medium" else "🔴")
                print(f"    {icon} {risk}: {count}")
                
        # Dashboard
        print("\n┌────────────────────────────────────────────────────────────────────┐")
        print("│                   Change Management Dashboard                      │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Total Changes:                 {stats['total_changes']:>10}                     │")
        print(f"│ Scheduled:                     {stats['scheduled_count']:>10}                     │")
        print(f"│ Reviews Completed:             {stats['total_reviews']:>10}                     │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Completed:                     {stats['by_status'].get('completed', 0):>10}                     │")
        print(f"│ In Progress:                   {stats['by_status'].get('in_progress', 0):>10}                     │")
        print(f"│ Pending Approval:              {stats['by_status'].get('submitted', 0):>10}                     │")
        print(f"│ Failed:                        {stats['by_status'].get('failed', 0):>10}                     │")
        print("└────────────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Change Management Platform initialized!")
    print("=" * 60)
