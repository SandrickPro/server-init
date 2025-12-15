#!/usr/bin/env python3
"""
Server Init - Iteration 364: Incident Management Platform
Платформа управления инцидентами

Функционал:
- Incident Lifecycle - жизненный цикл инцидента
- Severity Classification - классификация критичности
- On-Call Integration - интеграция с дежурствами
- Communication Channels - каналы коммуникации
- Timeline Tracking - отслеживание таймлайна
- Post-Mortem Management - управление post-mortem
- SLA Tracking - отслеживание SLA
- War Room Coordination - координация war room
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid


class IncidentSeverity(Enum):
    """Критичность инцидента"""
    SEV1 = "sev1"  # Critical - System down
    SEV2 = "sev2"  # Major - Major feature impacted
    SEV3 = "sev3"  # Minor - Minor feature impacted
    SEV4 = "sev4"  # Low - Minimal impact
    SEV5 = "sev5"  # Informational


class IncidentStatus(Enum):
    """Статус инцидента"""
    DETECTED = "detected"
    TRIAGED = "triaged"
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentType(Enum):
    """Тип инцидента"""
    OUTAGE = "outage"
    DEGRADATION = "degradation"
    SECURITY = "security"
    DATA_LOSS = "data_loss"
    INFRASTRUCTURE = "infrastructure"
    APPLICATION = "application"


class RoleType(Enum):
    """Роль в инциденте"""
    INCIDENT_COMMANDER = "incident_commander"
    OPERATIONS_LEAD = "operations_lead"
    COMMUNICATIONS_LEAD = "communications_lead"
    TECHNICAL_LEAD = "technical_lead"
    SUBJECT_MATTER_EXPERT = "subject_matter_expert"
    SCRIBE = "scribe"


class TimelineEventType(Enum):
    """Тип события таймлайна"""
    DETECTION = "detection"
    ASSIGNMENT = "assignment"
    STATUS_CHANGE = "status_change"
    SEVERITY_CHANGE = "severity_change"
    COMMUNICATION = "communication"
    ACTION = "action"
    NOTE = "note"
    ESCALATION = "escalation"
    MITIGATION = "mitigation"
    RESOLUTION = "resolution"


class CommunicationType(Enum):
    """Тип коммуникации"""
    INTERNAL = "internal"
    EXTERNAL = "external"
    STATUS_PAGE = "status_page"
    EXECUTIVE = "executive"


class PostMortemStatus(Enum):
    """Статус post-mortem"""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    PUBLISHED = "published"


@dataclass
class User:
    """Пользователь"""
    user_id: str
    name: str
    email: str
    phone: str = ""
    team: str = ""
    is_oncall: bool = False
    skills: List[str] = field(default_factory=list)


@dataclass
class Service:
    """Сервис"""
    service_id: str
    name: str
    tier: int = 3  # 1-3, 1 is most critical
    team: str = ""
    oncall_schedule_id: str = ""
    dependencies: List[str] = field(default_factory=list)
    sla_uptime: float = 99.9


@dataclass
class TimelineEvent:
    """Событие таймлайна"""
    event_id: str
    
    # Type
    event_type: TimelineEventType = TimelineEventType.NOTE
    
    # Content
    title: str = ""
    description: str = ""
    
    # Actor
    actor_id: str = ""
    actor_name: str = ""
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CommunicationUpdate:
    """Обновление коммуникации"""
    update_id: str
    
    # Type
    comm_type: CommunicationType = CommunicationType.INTERNAL
    
    # Content
    title: str = ""
    message: str = ""
    
    # Channels
    channels: List[str] = field(default_factory=list)
    
    # Author
    author_id: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    sent_at: Optional[datetime] = None


@dataclass
class IncidentRole:
    """Роль в инциденте"""
    role_id: str
    
    # Role
    role_type: RoleType = RoleType.TECHNICAL_LEAD
    
    # User
    user_id: str = ""
    user_name: str = ""
    
    # Status
    is_active: bool = True
    
    # Timestamps
    assigned_at: datetime = field(default_factory=datetime.now)


@dataclass
class ActionItem:
    """Элемент действия"""
    action_id: str
    
    # Content
    title: str = ""
    description: str = ""
    
    # Assignment
    assignee_id: str = ""
    assignee_name: str = ""
    
    # Status
    status: str = "open"  # open, in_progress, done, blocked
    
    # Priority
    priority: str = "medium"  # low, medium, high, critical
    
    # Due date
    due_date: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class RootCause:
    """Корневая причина"""
    cause_id: str
    
    # Category
    category: str = ""  # code, config, infrastructure, human, external
    
    # Description
    title: str = ""
    description: str = ""
    
    # Contributing factors
    factors: List[str] = field(default_factory=list)
    
    # Verified
    is_verified: bool = False


@dataclass
class PostMortem:
    """Post-Mortem"""
    postmortem_id: str
    
    # References
    incident_id: str = ""
    
    # Status
    status: PostMortemStatus = PostMortemStatus.DRAFT
    
    # Content
    summary: str = ""
    impact_summary: str = ""
    
    # Timeline
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    
    # Root cause
    root_causes: List[RootCause] = field(default_factory=list)
    
    # Lessons learned
    lessons_learned: List[str] = field(default_factory=list)
    
    # Action items
    action_items: List[ActionItem] = field(default_factory=list)
    
    # What went well
    what_went_well: List[str] = field(default_factory=list)
    
    # What could be improved
    improvements: List[str] = field(default_factory=list)
    
    # Author
    author_id: str = ""
    
    # Reviewers
    reviewers: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    published_at: Optional[datetime] = None


@dataclass
class SLAMetrics:
    """Метрики SLA"""
    metrics_id: str
    
    # Incident reference
    incident_id: str = ""
    
    # Times
    time_to_detect_minutes: float = 0.0
    time_to_acknowledge_minutes: float = 0.0
    time_to_mitigate_minutes: float = 0.0
    time_to_resolve_minutes: float = 0.0
    
    # Targets
    sla_acknowledge_minutes: int = 15
    sla_mitigate_minutes: int = 60
    sla_resolve_minutes: int = 240
    
    # Compliance
    acknowledge_sla_met: bool = True
    mitigate_sla_met: bool = True
    resolve_sla_met: bool = True


@dataclass
class Incident:
    """Инцидент"""
    incident_id: str
    
    # Identity
    incident_number: int = 0
    title: str = ""
    description: str = ""
    
    # Classification
    severity: IncidentSeverity = IncidentSeverity.SEV3
    incident_type: IncidentType = IncidentType.APPLICATION
    
    # Status
    status: IncidentStatus = IncidentStatus.DETECTED
    
    # Services
    affected_services: List[str] = field(default_factory=list)
    
    # Roles
    roles: List[IncidentRole] = field(default_factory=list)
    
    # Timeline
    timeline: List[TimelineEvent] = field(default_factory=list)
    
    # Communications
    communications: List[CommunicationUpdate] = field(default_factory=list)
    
    # Action items
    action_items: List[ActionItem] = field(default_factory=list)
    
    # War room
    war_room_link: str = ""
    
    # Impact
    customer_impact: str = ""
    business_impact: str = ""
    
    # SLA
    sla_metrics: Optional[SLAMetrics] = None
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    
    # Timestamps
    detected_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    mitigated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None


@dataclass
class IncidentMetrics:
    """Метрики инцидентов"""
    metrics_id: str
    
    # Counts
    total_incidents: int = 0
    open_incidents: int = 0
    resolved_incidents: int = 0
    
    # By severity
    sev1_count: int = 0
    sev2_count: int = 0
    sev3_count: int = 0
    
    # Performance
    mttr_minutes: float = 0.0  # Mean Time To Resolve
    mtta_minutes: float = 0.0  # Mean Time To Acknowledge
    mttm_minutes: float = 0.0  # Mean Time To Mitigate
    
    # SLA
    sla_compliance_rate: float = 0.0
    
    # Timestamps
    collected_at: datetime = field(default_factory=datetime.now)


class IncidentManagementPlatform:
    """Платформа управления инцидентами"""
    
    def __init__(self, platform_name: str = "incident-management"):
        self.platform_name = platform_name
        self.incidents: Dict[str, Incident] = {}
        self.users: Dict[str, User] = {}
        self.services: Dict[str, Service] = {}
        self.postmortems: Dict[str, PostMortem] = {}
        self._incident_counter = 0
        
    async def register_user(self, name: str,
                           email: str,
                           phone: str = "",
                           team: str = "",
                           skills: List[str] = None) -> User:
        """Регистрация пользователя"""
        user = User(
            user_id=f"usr_{uuid.uuid4().hex[:8]}",
            name=name,
            email=email,
            phone=phone,
            team=team,
            skills=skills or []
        )
        
        self.users[user.user_id] = user
        return user
        
    async def register_service(self, name: str,
                              tier: int = 3,
                              team: str = "",
                              sla_uptime: float = 99.9,
                              dependencies: List[str] = None) -> Service:
        """Регистрация сервиса"""
        service = Service(
            service_id=f"svc_{uuid.uuid4().hex[:8]}",
            name=name,
            tier=tier,
            team=team,
            sla_uptime=sla_uptime,
            dependencies=dependencies or []
        )
        
        self.services[service.service_id] = service
        return service
        
    async def create_incident(self, title: str,
                             description: str = "",
                             severity: IncidentSeverity = IncidentSeverity.SEV3,
                             incident_type: IncidentType = IncidentType.APPLICATION,
                             affected_services: List[str] = None,
                             detected_by: str = "") -> Incident:
        """Создание инцидента"""
        self._incident_counter += 1
        
        incident = Incident(
            incident_id=f"inc_{uuid.uuid4().hex[:8]}",
            incident_number=self._incident_counter,
            title=title,
            description=description,
            severity=severity,
            incident_type=incident_type,
            affected_services=affected_services or []
        )
        
        # Add detection event to timeline
        await self._add_timeline_event(
            incident,
            TimelineEventType.DETECTION,
            "Incident Detected",
            description,
            detected_by
        )
        
        # Initialize SLA metrics
        incident.sla_metrics = SLAMetrics(
            metrics_id=f"sla_{uuid.uuid4().hex[:8]}",
            incident_id=incident.incident_id
        )
        
        self.incidents[incident.incident_id] = incident
        return incident
        
    async def assign_role(self, incident_id: str,
                         user_id: str,
                         role_type: RoleType) -> Optional[IncidentRole]:
        """Назначение роли"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return None
            
        user = self.users.get(user_id)
        
        role = IncidentRole(
            role_id=f"role_{uuid.uuid4().hex[:8]}",
            role_type=role_type,
            user_id=user_id,
            user_name=user.name if user else ""
        )
        
        incident.roles.append(role)
        
        await self._add_timeline_event(
            incident,
            TimelineEventType.ASSIGNMENT,
            f"{role_type.value} Assigned",
            f"{user.name if user else 'Unknown'} assigned as {role_type.value}",
            user_id
        )
        
        return role
        
    async def update_status(self, incident_id: str,
                           new_status: IncidentStatus,
                           updated_by: str = "",
                           note: str = "") -> Optional[Incident]:
        """Обновление статуса"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return None
            
        old_status = incident.status
        incident.status = new_status
        
        # Update timestamps
        now = datetime.now()
        if new_status == IncidentStatus.TRIAGED and not incident.acknowledged_at:
            incident.acknowledged_at = now
            if incident.sla_metrics:
                incident.sla_metrics.time_to_acknowledge_minutes = (now - incident.detected_at).total_seconds() / 60
                
        elif new_status == IncidentStatus.MITIGATING and not incident.mitigated_at:
            incident.mitigated_at = now
            if incident.sla_metrics:
                incident.sla_metrics.time_to_mitigate_minutes = (now - incident.detected_at).total_seconds() / 60
                
        elif new_status == IncidentStatus.RESOLVED and not incident.resolved_at:
            incident.resolved_at = now
            if incident.sla_metrics:
                incident.sla_metrics.time_to_resolve_minutes = (now - incident.detected_at).total_seconds() / 60
                
        elif new_status == IncidentStatus.CLOSED:
            incident.closed_at = now
            
        await self._add_timeline_event(
            incident,
            TimelineEventType.STATUS_CHANGE,
            f"Status Changed",
            f"Status changed from {old_status.value} to {new_status.value}. {note}",
            updated_by
        )
        
        return incident
        
    async def update_severity(self, incident_id: str,
                             new_severity: IncidentSeverity,
                             updated_by: str = "",
                             reason: str = "") -> Optional[Incident]:
        """Обновление критичности"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return None
            
        old_severity = incident.severity
        incident.severity = new_severity
        
        await self._add_timeline_event(
            incident,
            TimelineEventType.SEVERITY_CHANGE,
            "Severity Changed",
            f"Severity changed from {old_severity.value} to {new_severity.value}. {reason}",
            updated_by
        )
        
        return incident
        
    async def add_communication(self, incident_id: str,
                               comm_type: CommunicationType,
                               title: str,
                               message: str,
                               author_id: str = "",
                               channels: List[str] = None) -> Optional[CommunicationUpdate]:
        """Добавление коммуникации"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return None
            
        update = CommunicationUpdate(
            update_id=f"com_{uuid.uuid4().hex[:8]}",
            comm_type=comm_type,
            title=title,
            message=message,
            channels=channels or [],
            author_id=author_id,
            sent_at=datetime.now()
        )
        
        incident.communications.append(update)
        
        await self._add_timeline_event(
            incident,
            TimelineEventType.COMMUNICATION,
            f"{comm_type.value} Update",
            title,
            author_id
        )
        
        return update
        
    async def add_action_item(self, incident_id: str,
                             title: str,
                             description: str = "",
                             assignee_id: str = "",
                             priority: str = "medium",
                             due_date: datetime = None) -> Optional[ActionItem]:
        """Добавление элемента действия"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return None
            
        user = self.users.get(assignee_id)
        
        action = ActionItem(
            action_id=f"act_{uuid.uuid4().hex[:8]}",
            title=title,
            description=description,
            assignee_id=assignee_id,
            assignee_name=user.name if user else "",
            priority=priority,
            due_date=due_date
        )
        
        incident.action_items.append(action)
        
        await self._add_timeline_event(
            incident,
            TimelineEventType.ACTION,
            "Action Item Created",
            f"{title} - assigned to {user.name if user else 'unassigned'}",
            assignee_id
        )
        
        return action
        
    async def _add_timeline_event(self, incident: Incident,
                                 event_type: TimelineEventType,
                                 title: str,
                                 description: str,
                                 actor_id: str = ""):
        """Добавление события в таймлайн"""
        user = self.users.get(actor_id)
        
        event = TimelineEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            title=title,
            description=description,
            actor_id=actor_id,
            actor_name=user.name if user else ""
        )
        
        incident.timeline.append(event)
        
    async def create_war_room(self, incident_id: str) -> Optional[str]:
        """Создание war room"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return None
            
        war_room_link = f"https://meet.example.com/incident-{incident.incident_number}"
        incident.war_room_link = war_room_link
        
        await self._add_timeline_event(
            incident,
            TimelineEventType.NOTE,
            "War Room Created",
            f"War room available at {war_room_link}",
            ""
        )
        
        return war_room_link
        
    async def create_postmortem(self, incident_id: str,
                               author_id: str = "") -> Optional[PostMortem]:
        """Создание post-mortem"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return None
            
        postmortem = PostMortem(
            postmortem_id=f"pm_{uuid.uuid4().hex[:8]}",
            incident_id=incident_id,
            author_id=author_id,
            summary=f"Post-mortem for incident #{incident.incident_number}: {incident.title}",
            timeline=[{
                "time": event.timestamp.isoformat(),
                "type": event.event_type.value,
                "title": event.title,
                "description": event.description
            } for event in incident.timeline]
        )
        
        self.postmortems[postmortem.postmortem_id] = postmortem
        return postmortem
        
    async def add_root_cause(self, postmortem_id: str,
                            category: str,
                            title: str,
                            description: str = "",
                            factors: List[str] = None) -> Optional[RootCause]:
        """Добавление корневой причины"""
        postmortem = self.postmortems.get(postmortem_id)
        if not postmortem:
            return None
            
        root_cause = RootCause(
            cause_id=f"rc_{uuid.uuid4().hex[:8]}",
            category=category,
            title=title,
            description=description,
            factors=factors or []
        )
        
        postmortem.root_causes.append(root_cause)
        return root_cause
        
    async def publish_postmortem(self, postmortem_id: str) -> Optional[PostMortem]:
        """Публикация post-mortem"""
        postmortem = self.postmortems.get(postmortem_id)
        if not postmortem:
            return None
            
        postmortem.status = PostMortemStatus.PUBLISHED
        postmortem.published_at = datetime.now()
        
        return postmortem
        
    async def collect_metrics(self) -> IncidentMetrics:
        """Сбор метрик"""
        open_incidents = sum(1 for i in self.incidents.values() if i.status not in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED])
        resolved_incidents = sum(1 for i in self.incidents.values() if i.status in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED])
        
        sev1_count = sum(1 for i in self.incidents.values() if i.severity == IncidentSeverity.SEV1)
        sev2_count = sum(1 for i in self.incidents.values() if i.severity == IncidentSeverity.SEV2)
        sev3_count = sum(1 for i in self.incidents.values() if i.severity == IncidentSeverity.SEV3)
        
        # Calculate MTTR, MTTA, MTTM
        resolved_with_metrics = [
            i for i in self.incidents.values()
            if i.sla_metrics and i.sla_metrics.time_to_resolve_minutes > 0
        ]
        
        mttr = sum(i.sla_metrics.time_to_resolve_minutes for i in resolved_with_metrics) / len(resolved_with_metrics) if resolved_with_metrics else 0.0
        mtta = sum(i.sla_metrics.time_to_acknowledge_minutes for i in resolved_with_metrics) / len(resolved_with_metrics) if resolved_with_metrics else 0.0
        mttm = sum(i.sla_metrics.time_to_mitigate_minutes for i in resolved_with_metrics) / len(resolved_with_metrics) if resolved_with_metrics else 0.0
        
        # SLA compliance
        total_sla = len(resolved_with_metrics)
        met_sla = sum(1 for i in resolved_with_metrics if i.sla_metrics.acknowledge_sla_met and i.sla_metrics.resolve_sla_met)
        sla_rate = (met_sla / total_sla * 100) if total_sla > 0 else 100.0
        
        return IncidentMetrics(
            metrics_id=f"im_{uuid.uuid4().hex[:8]}",
            total_incidents=len(self.incidents),
            open_incidents=open_incidents,
            resolved_incidents=resolved_incidents,
            sev1_count=sev1_count,
            sev2_count=sev2_count,
            sev3_count=sev3_count,
            mttr_minutes=mttr,
            mtta_minutes=mtta,
            mttm_minutes=mttm,
            sla_compliance_rate=sla_rate
        )
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        open_incidents = sum(1 for i in self.incidents.values() if i.status not in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED])
        resolved_incidents = sum(1 for i in self.incidents.values() if i.status in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED])
        
        by_severity = {}
        for severity in IncidentSeverity:
            by_severity[severity.value] = sum(1 for i in self.incidents.values() if i.severity == severity)
            
        by_type = {}
        for inc_type in IncidentType:
            by_type[inc_type.value] = sum(1 for i in self.incidents.values() if i.incident_type == inc_type)
            
        by_status = {}
        for status in IncidentStatus:
            by_status[status.value] = sum(1 for i in self.incidents.values() if i.status == status)
            
        total_action_items = sum(len(i.action_items) for i in self.incidents.values())
        open_action_items = sum(
            1 for i in self.incidents.values()
            for a in i.action_items if a.status in ["open", "in_progress"]
        )
        
        return {
            "total_incidents": len(self.incidents),
            "open_incidents": open_incidents,
            "resolved_incidents": resolved_incidents,
            "by_severity": by_severity,
            "by_type": by_type,
            "by_status": by_status,
            "total_users": len(self.users),
            "total_services": len(self.services),
            "total_postmortems": len(self.postmortems),
            "total_action_items": total_action_items,
            "open_action_items": open_action_items
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 364: Incident Management Platform")
    print("=" * 60)
    
    platform = IncidentManagementPlatform(platform_name="enterprise-incidents")
    print("✓ Incident Management Platform initialized")
    
    # Register Users
    print("\n👥 Registering Users...")
    
    users_data = [
        ("John Smith", "john@example.com", "+1-555-0101", "SRE Team", ["kubernetes", "aws", "networking"]),
        ("Jane Doe", "jane@example.com", "+1-555-0102", "Platform Team", ["databases", "java", "microservices"]),
        ("Bob Wilson", "bob@example.com", "+1-555-0103", "Backend Team", ["python", "api", "performance"]),
        ("Alice Brown", "alice@example.com", "+1-555-0104", "Security Team", ["security", "compliance", "audit"]),
        ("Charlie Davis", "charlie@example.com", "+1-555-0105", "SRE Team", ["monitoring", "incident-response"]),
        ("Eva Martinez", "eva@example.com", "+1-555-0106", "Communications", ["comms", "status-page"])
    ]
    
    users = []
    for name, email, phone, team, skills in users_data:
        user = await platform.register_user(name, email, phone, team, skills)
        users.append(user)
        print(f"  👤 {name} ({team})")
        
    # Register Services
    print("\n🔧 Registering Services...")
    
    services_data = [
        ("api-gateway", 1, "Platform Team", 99.99, []),
        ("payment-service", 1, "Backend Team", 99.99, ["api-gateway", "database"]),
        ("user-service", 2, "Backend Team", 99.9, ["api-gateway", "database"]),
        ("order-service", 2, "Backend Team", 99.9, ["api-gateway", "payment-service"]),
        ("notification-service", 3, "Platform Team", 99.5, ["api-gateway"]),
        ("analytics-service", 3, "Data Team", 99.0, ["database"]),
        ("database", 1, "DBA Team", 99.99, [])
    ]
    
    services = []
    for name, tier, team, sla, deps in services_data:
        service = await platform.register_service(name, tier, team, sla, deps)
        services.append(service)
        print(f"  🔧 {name} (Tier {tier}, SLA {sla}%)")
        
    # Create Incidents
    print("\n🔥 Creating Incidents...")
    
    incidents_data = [
        ("Database Connection Pool Exhausted", "All database connections are in use, causing timeouts", IncidentSeverity.SEV1, IncidentType.OUTAGE, ["database", "api-gateway", "payment-service"]),
        ("Payment Gateway Timeout", "External payment provider returning 504 errors", IncidentSeverity.SEV2, IncidentType.DEGRADATION, ["payment-service"]),
        ("High Latency on User Service", "P99 latency increased to 5s", IncidentSeverity.SEV3, IncidentType.DEGRADATION, ["user-service"]),
        ("SSL Certificate Expiring", "Certificate expires in 7 days", IncidentSeverity.SEV4, IncidentType.INFRASTRUCTURE, ["api-gateway"]),
        ("Memory Leak in Analytics", "Gradual memory increase detected", IncidentSeverity.SEV3, IncidentType.APPLICATION, ["analytics-service"])
    ]
    
    incidents = []
    for title, desc, severity, inc_type, affected in incidents_data:
        incident = await platform.create_incident(title, desc, severity, inc_type, affected, users[0].user_id)
        incidents.append(incident)
        print(f"  🔥 {severity.value.upper()}: {title}")
        
    # Assign Roles
    print("\n👔 Assigning Roles...")
    
    # First incident (SEV1) - full incident response team
    await platform.assign_role(incidents[0].incident_id, users[0].user_id, RoleType.INCIDENT_COMMANDER)
    await platform.assign_role(incidents[0].incident_id, users[1].user_id, RoleType.TECHNICAL_LEAD)
    await platform.assign_role(incidents[0].incident_id, users[4].user_id, RoleType.OPERATIONS_LEAD)
    await platform.assign_role(incidents[0].incident_id, users[5].user_id, RoleType.COMMUNICATIONS_LEAD)
    print(f"  👔 INC-{incidents[0].incident_number}: Full response team assigned")
    
    # Second incident
    await platform.assign_role(incidents[1].incident_id, users[2].user_id, RoleType.INCIDENT_COMMANDER)
    await platform.assign_role(incidents[1].incident_id, users[1].user_id, RoleType.TECHNICAL_LEAD)
    print(f"  👔 INC-{incidents[1].incident_number}: Response team assigned")
    
    # Create War Rooms
    print("\n🎯 Creating War Rooms...")
    
    for incident in incidents[:2]:
        link = await platform.create_war_room(incident.incident_id)
        print(f"  🎯 INC-{incident.incident_number}: {link}")
        
    # Update Statuses
    print("\n📊 Updating Statuses...")
    
    # Simulate incident lifecycle for first incident
    await asyncio.sleep(0.01)  # Simulate time passing
    await platform.update_status(incidents[0].incident_id, IncidentStatus.TRIAGED, users[0].user_id, "Initial triage complete")
    await asyncio.sleep(0.01)
    await platform.update_status(incidents[0].incident_id, IncidentStatus.INVESTIGATING, users[1].user_id, "Investigating database connections")
    await asyncio.sleep(0.01)
    await platform.update_status(incidents[0].incident_id, IncidentStatus.IDENTIFIED, users[1].user_id, "Root cause identified - connection leak in new release")
    await asyncio.sleep(0.01)
    await platform.update_status(incidents[0].incident_id, IncidentStatus.MITIGATING, users[1].user_id, "Rolling back to previous version")
    await asyncio.sleep(0.01)
    await platform.update_status(incidents[0].incident_id, IncidentStatus.RESOLVED, users[0].user_id, "Service restored after rollback")
    
    print(f"  📊 INC-{incidents[0].incident_number}: {incidents[0].status.value}")
    
    # Update second incident
    await platform.update_status(incidents[1].incident_id, IncidentStatus.TRIAGED, users[2].user_id)
    await platform.update_status(incidents[1].incident_id, IncidentStatus.INVESTIGATING, users[2].user_id)
    print(f"  📊 INC-{incidents[1].incident_number}: {incidents[1].status.value}")
    
    # Third incident - escalate severity
    await platform.update_status(incidents[2].incident_id, IncidentStatus.INVESTIGATING, users[2].user_id)
    await platform.update_severity(incidents[2].incident_id, IncidentSeverity.SEV2, users[2].user_id, "Impact wider than initially assessed")
    print(f"  📊 INC-{incidents[2].incident_number}: Escalated to {incidents[2].severity.value}")
    
    # Add Communications
    print("\n📢 Adding Communications...")
    
    comms_data = [
        (incidents[0].incident_id, CommunicationType.INTERNAL, "Initial Assessment", "Database connection pool exhausted. All hands on deck.", users[0].user_id),
        (incidents[0].incident_id, CommunicationType.STATUS_PAGE, "Service Degradation", "We are experiencing issues with our platform. Our team is investigating.", users[5].user_id),
        (incidents[0].incident_id, CommunicationType.EXTERNAL, "Customer Update", "Services have been restored. Thank you for your patience.", users[5].user_id),
        (incidents[1].incident_id, CommunicationType.INTERNAL, "Payment Issues", "Payment provider experiencing issues. Monitoring closely.", users[2].user_id)
    ]
    
    for inc_id, comm_type, title, message, author in comms_data:
        await platform.add_communication(inc_id, comm_type, title, message, author, ["#incidents", "#ops"])
        
    print(f"  📢 Added {len(comms_data)} communications")
    
    # Add Action Items
    print("\n✅ Adding Action Items...")
    
    actions_data = [
        (incidents[0].incident_id, "Review database connection pooling config", "Analyze current settings and recommend improvements", users[1].user_id, "high"),
        (incidents[0].incident_id, "Add connection leak detection", "Implement monitoring for connection leaks", users[4].user_id, "medium"),
        (incidents[0].incident_id, "Update runbook", "Document the incident response procedure", users[0].user_id, "low"),
        (incidents[1].incident_id, "Implement circuit breaker", "Add circuit breaker for payment provider", users[2].user_id, "high")
    ]
    
    for inc_id, title, desc, assignee, priority in actions_data:
        await platform.add_action_item(inc_id, title, desc, assignee, priority)
        
    print(f"  ✅ Added {len(actions_data)} action items")
    
    # Create Post-Mortems
    print("\n📝 Creating Post-Mortems...")
    
    pm = await platform.create_postmortem(incidents[0].incident_id, users[0].user_id)
    
    await platform.add_root_cause(
        pm.postmortem_id,
        "code",
        "Connection leak in new release",
        "The new release introduced a code path that didn't properly close database connections",
        ["Insufficient testing", "Missing connection pool monitoring", "Rapid deployment"]
    )
    
    pm.lessons_learned = [
        "Need better testing for database connections",
        "Connection pool monitoring alerts should be in place",
        "Canary deployments could have caught this earlier"
    ]
    
    pm.what_went_well = [
        "Quick detection through customer reports",
        "Effective war room coordination",
        "Fast rollback procedure"
    ]
    
    pm.improvements = [
        "Implement connection pool monitoring",
        "Add integration tests for database connections",
        "Improve canary deployment coverage"
    ]
    
    await platform.publish_postmortem(pm.postmortem_id)
    print(f"  📝 Post-mortem created and published for INC-{incidents[0].incident_number}")
    
    # Collect Metrics
    metrics = await platform.collect_metrics()
    
    # Incidents Dashboard
    print("\n🔥 Active Incidents:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ ID      │ Severity │ Title                                   │ Status         │ Commander            │ Duration                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for inc in incidents:
        inc_num = f"INC-{inc.incident_number}".ljust(7)
        severity = inc.severity.value.upper().ljust(8)
        title = inc.title[:39].ljust(39)
        status = inc.status.value[:14].ljust(14)
        
        commander = next((r.user_name for r in inc.roles if r.role_type == RoleType.INCIDENT_COMMANDER), "Unassigned")
        commander = commander[:20].ljust(20)
        
        if inc.resolved_at:
            duration = f"{(inc.resolved_at - inc.detected_at).total_seconds() / 60:.1f}m"
        else:
            duration = f"{(datetime.now() - inc.detected_at).total_seconds() / 60:.1f}m*"
        duration = duration.ljust(157)
        
        print(f"  │ {inc_num} │ {severity} │ {title} │ {status} │ {commander} │ {duration} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Timeline for First Incident
    print(f"\n📅 Timeline (INC-{incidents[0].incident_number}):")
    
    for event in incidents[0].timeline[-8:]:
        time_str = event.timestamp.strftime("%H:%M:%S")
        print(f"  {time_str} │ {event.event_type.value:15s} │ {event.title}")
        
    # Action Items
    print("\n✅ Open Action Items:")
    
    for inc in incidents:
        for action in inc.action_items:
            if action.status in ["open", "in_progress"]:
                status_icon = "🔄" if action.status == "in_progress" else "⬜"
                print(f"  {status_icon} [{action.priority.upper()[:1]}] {action.title[:50]} - {action.assignee_name}")
                
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Total Incidents: {stats['total_incidents']} ({stats['open_incidents']} open)")
    print(f"  Total Users: {stats['total_users']}")
    print(f"  Total Services: {stats['total_services']}")
    print(f"  Post-Mortems: {stats['total_postmortems']}")
    print(f"  Action Items: {stats['open_action_items']}/{stats['total_action_items']} open")
    
    # By Severity
    print("\n  Incidents by Severity:")
    for severity, count in stats["by_severity"].items():
        if count > 0:
            bar = "█" * count
            print(f"    {severity.upper():6s} │ {bar} ({count})")
            
    # By Status
    print("\n  Incidents by Status:")
    for status, count in stats["by_status"].items():
        if count > 0:
            bar = "█" * count
            print(f"    {status:14s} │ {bar} ({count})")
            
    # Metrics
    print("\n📈 Performance Metrics:")
    print(f"  MTTA (Mean Time To Acknowledge): {metrics.mtta_minutes:.1f} minutes")
    print(f"  MTTM (Mean Time To Mitigate): {metrics.mttm_minutes:.1f} minutes")
    print(f"  MTTR (Mean Time To Resolve): {metrics.mttr_minutes:.1f} minutes")
    print(f"  SLA Compliance: {metrics.sla_compliance_rate:.1f}%")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Incident Management Platform                     │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Incidents:               {stats['total_incidents']:>12}                      │")
    print(f"│ Open Incidents:                {stats['open_incidents']:>12}                      │")
    print(f"│ Resolved Incidents:            {stats['resolved_incidents']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ SEV1 Incidents:                {metrics.sev1_count:>12}                      │")
    print(f"│ SEV2 Incidents:                {metrics.sev2_count:>12}                      │")
    print(f"│ SEV3 Incidents:                {metrics.sev3_count:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ MTTA (minutes):                {metrics.mtta_minutes:>12.1f}                      │")
    print(f"│ MTTM (minutes):                {metrics.mttm_minutes:>12.1f}                      │")
    print(f"│ MTTR (minutes):                {metrics.mttr_minutes:>12.1f}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ SLA Compliance:                {metrics.sla_compliance_rate:>11.1f}%                      │")
    print(f"│ Post-Mortems:                  {stats['total_postmortems']:>12}                      │")
    print(f"│ Open Action Items:             {stats['open_action_items']:>12}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Incident Management Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
