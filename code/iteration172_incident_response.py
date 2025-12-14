#!/usr/bin/env python3
"""
Server Init - Iteration 172: Incident Response Platform
Платформа реагирования на инциденты

Функционал:
- Incident Detection - обнаружение инцидентов
- Incident Classification - классификация инцидентов
- Escalation Management - управление эскалацией
- Runbook Automation - автоматизация runbook
- Post-Mortem Management - управление post-mortem
- On-Call Scheduling - планирование дежурств
- Communication Hub - центр коммуникаций
- Metrics & Analytics - метрики и аналитика
"""

import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
import uuid
from collections import defaultdict


class IncidentSeverity(Enum):
    """Серьёзность инцидента"""
    SEV1 = "sev1"  # Critical - major customer impact
    SEV2 = "sev2"  # High - significant impact
    SEV3 = "sev3"  # Medium - moderate impact
    SEV4 = "sev4"  # Low - minor impact
    SEV5 = "sev5"  # Informational


class IncidentStatus(Enum):
    """Статус инцидента"""
    DETECTED = "detected"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"
    POST_MORTEM = "post_mortem"
    CLOSED = "closed"


class IncidentType(Enum):
    """Тип инцидента"""
    OUTAGE = "outage"
    DEGRADATION = "degradation"
    SECURITY = "security"
    DATA_LOSS = "data_loss"
    PERFORMANCE = "performance"
    CAPACITY = "capacity"
    NETWORK = "network"
    OTHER = "other"


class EscalationLevel(Enum):
    """Уровень эскалации"""
    L1 = "l1"  # First responders
    L2 = "l2"  # Senior engineers
    L3 = "l3"  # Leads/Managers
    L4 = "l4"  # Directors/VPs
    L5 = "l5"  # Executive


class NotificationChannel(Enum):
    """Канал уведомления"""
    EMAIL = "email"
    SLACK = "slack"
    PAGERDUTY = "pagerduty"
    SMS = "sms"
    PHONE = "phone"
    TEAMS = "teams"


@dataclass
class Responder:
    """Ответственный"""
    responder_id: str
    name: str = ""
    email: str = ""
    phone: str = ""
    
    # Role
    role: str = ""  # incident_commander, tech_lead, communications
    team: str = ""
    
    # Escalation level
    escalation_level: EscalationLevel = EscalationLevel.L1
    
    # Availability
    on_call: bool = False
    available: bool = True
    
    # Notification preferences
    preferred_channels: List[NotificationChannel] = field(default_factory=list)


@dataclass
class OnCallSchedule:
    """Расписание дежурств"""
    schedule_id: str
    team: str = ""
    
    # Current on-call
    primary_responder_id: str = ""
    secondary_responder_id: str = ""
    
    # Rotation
    rotation_period_hours: int = 168  # Weekly
    rotation_start: datetime = field(default_factory=datetime.now)
    
    # Members
    rotation_members: List[str] = field(default_factory=list)


@dataclass
class Timeline:
    """Запись временной шкалы"""
    entry_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Content
    event_type: str = ""  # status_change, action, note, escalation
    description: str = ""
    
    # Author
    author_id: str = ""
    author_name: str = ""
    
    # Metadata
    automated: bool = False
    visibility: str = "internal"  # internal, public


@dataclass
class Incident:
    """Инцидент"""
    incident_id: str
    title: str = ""
    description: str = ""
    
    # Classification
    severity: IncidentSeverity = IncidentSeverity.SEV3
    incident_type: IncidentType = IncidentType.OTHER
    status: IncidentStatus = IncidentStatus.DETECTED
    
    # Impact
    affected_services: List[str] = field(default_factory=list)
    affected_customers: int = 0
    
    # Team
    incident_commander_id: str = ""
    responders: List[str] = field(default_factory=list)
    
    # Timeline
    timeline: List[Timeline] = field(default_factory=list)
    
    # Escalation
    escalation_level: EscalationLevel = EscalationLevel.L1
    escalations: List[Dict] = field(default_factory=list)
    
    # Timestamps
    detected_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    # Root cause
    root_cause: str = ""
    
    # Related
    related_incidents: List[str] = field(default_factory=list)
    related_alerts: List[str] = field(default_factory=list)
    
    # Metrics
    time_to_acknowledge_sec: float = 0
    time_to_resolve_sec: float = 0
    
    # Tags
    tags: List[str] = field(default_factory=list)


@dataclass
class Runbook:
    """Runbook"""
    runbook_id: str
    name: str = ""
    description: str = ""
    
    # Trigger
    trigger_conditions: Dict[str, Any] = field(default_factory=dict)
    auto_trigger: bool = False
    
    # Steps
    steps: List[Dict] = field(default_factory=list)
    
    # Metadata
    owner: str = ""
    last_executed: Optional[datetime] = None
    execution_count: int = 0
    
    # Success rate
    success_count: int = 0
    failure_count: int = 0


@dataclass
class RunbookExecution:
    """Выполнение runbook"""
    execution_id: str
    runbook_id: str = ""
    incident_id: str = ""
    
    # Status
    status: str = "running"  # running, completed, failed
    current_step: int = 0
    total_steps: int = 0
    
    # Results
    step_results: List[Dict] = field(default_factory=list)
    
    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    # Executed by
    executed_by: str = ""


@dataclass
class PostMortem:
    """Post-mortem"""
    postmortem_id: str
    incident_id: str = ""
    
    # Content
    title: str = ""
    summary: str = ""
    
    # Analysis
    timeline_summary: str = ""
    root_cause_analysis: str = ""
    impact_analysis: str = ""
    
    # Actions
    action_items: List[Dict] = field(default_factory=list)
    lessons_learned: List[str] = field(default_factory=list)
    
    # Review
    status: str = "draft"  # draft, review, approved, published
    reviewers: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    published_at: Optional[datetime] = None


class ResponderManager:
    """Менеджер респондеров"""
    
    def __init__(self):
        self.responders: Dict[str, Responder] = {}
        self.schedules: Dict[str, OnCallSchedule] = {}
        
    def add_responder(self, responder: Responder):
        """Добавление респондера"""
        self.responders[responder.responder_id] = responder
        
    def get_on_call(self, team: str) -> List[Responder]:
        """Получение дежурных"""
        schedule = self.schedules.get(team)
        if not schedule:
            return []
            
        result = []
        if schedule.primary_responder_id in self.responders:
            result.append(self.responders[schedule.primary_responder_id])
        if schedule.secondary_responder_id in self.responders:
            result.append(self.responders[schedule.secondary_responder_id])
            
        return result
        
    def get_by_escalation_level(self, level: EscalationLevel, team: str = "") -> List[Responder]:
        """Получение по уровню эскалации"""
        responders = [r for r in self.responders.values() 
                     if r.escalation_level == level and r.available]
        if team:
            responders = [r for r in responders if r.team == team]
        return responders


class NotificationService:
    """Сервис уведомлений"""
    
    def __init__(self):
        self.sent_notifications: List[Dict] = []
        
    async def notify(self, responder: Responder, message: str, 
                    incident: Incident, channel: NotificationChannel = None):
        """Отправка уведомления"""
        channels = [channel] if channel else responder.preferred_channels
        
        for ch in channels:
            notification = {
                "id": f"notif_{uuid.uuid4().hex[:8]}",
                "responder_id": responder.responder_id,
                "channel": ch.value,
                "message": message,
                "incident_id": incident.incident_id,
                "sent_at": datetime.now()
            }
            self.sent_notifications.append(notification)
            
    async def notify_team(self, team: str, message: str, incident: Incident,
                         responder_manager: ResponderManager):
        """Уведомление команды"""
        on_call = responder_manager.get_on_call(team)
        for responder in on_call:
            await self.notify(responder, message, incident)


class EscalationEngine:
    """Движок эскалации"""
    
    def __init__(self, responder_manager: ResponderManager, notification_service: NotificationService):
        self.responder_manager = responder_manager
        self.notification = notification_service
        
        # Escalation timeouts by severity (minutes)
        self.escalation_timeouts = {
            IncidentSeverity.SEV1: [5, 15, 30, 60],
            IncidentSeverity.SEV2: [15, 30, 60, 120],
            IncidentSeverity.SEV3: [30, 60, 120, 240],
            IncidentSeverity.SEV4: [60, 120, 240, 480],
            IncidentSeverity.SEV5: [120, 240, 480, 960]
        }
        
    async def check_escalation(self, incident: Incident) -> bool:
        """Проверка необходимости эскалации"""
        if incident.status in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]:
            return False
            
        timeouts = self.escalation_timeouts.get(incident.severity, [])
        current_level_idx = list(EscalationLevel).index(incident.escalation_level)
        
        if current_level_idx >= len(timeouts):
            return False
            
        timeout_minutes = timeouts[current_level_idx]
        time_since_detection = (datetime.now() - incident.detected_at).total_seconds() / 60
        
        if time_since_detection > timeout_minutes:
            return True
            
        return False
        
    async def escalate(self, incident: Incident) -> EscalationLevel:
        """Эскалация инцидента"""
        current_idx = list(EscalationLevel).index(incident.escalation_level)
        next_level = list(EscalationLevel)[min(current_idx + 1, len(EscalationLevel) - 1)]
        
        incident.escalation_level = next_level
        
        # Record escalation
        escalation = {
            "from_level": list(EscalationLevel)[current_idx].value,
            "to_level": next_level.value,
            "timestamp": datetime.now(),
            "reason": "timeout"
        }
        incident.escalations.append(escalation)
        
        # Add timeline entry
        incident.timeline.append(Timeline(
            entry_id=f"tl_{uuid.uuid4().hex[:8]}",
            event_type="escalation",
            description=f"Escalated from {escalation['from_level']} to {next_level.value}",
            automated=True
        ))
        
        # Notify next level
        next_responders = self.responder_manager.get_by_escalation_level(next_level)
        for responder in next_responders:
            await self.notification.notify(
                responder,
                f"[ESCALATION] Incident {incident.incident_id}: {incident.title}",
                incident
            )
            
        return next_level


class RunbookExecutor:
    """Исполнитель runbook"""
    
    def __init__(self):
        self.runbooks: Dict[str, Runbook] = {}
        self.executions: Dict[str, RunbookExecution] = {}
        
    def register_runbook(self, runbook: Runbook):
        """Регистрация runbook"""
        self.runbooks[runbook.runbook_id] = runbook
        
    async def execute(self, runbook_id: str, incident: Incident, 
                     executor_id: str) -> RunbookExecution:
        """Выполнение runbook"""
        runbook = self.runbooks.get(runbook_id)
        if not runbook:
            return None
            
        execution = RunbookExecution(
            execution_id=f"exec_{uuid.uuid4().hex[:8]}",
            runbook_id=runbook_id,
            incident_id=incident.incident_id,
            total_steps=len(runbook.steps),
            executed_by=executor_id
        )
        
        self.executions[execution.execution_id] = execution
        
        # Execute steps
        for i, step in enumerate(runbook.steps):
            execution.current_step = i + 1
            
            try:
                # Simulate step execution
                await asyncio.sleep(0.1)
                
                result = {
                    "step": i + 1,
                    "name": step.get("name", ""),
                    "status": "success",
                    "output": f"Step {i+1} completed",
                    "timestamp": datetime.now()
                }
                execution.step_results.append(result)
                
            except Exception as e:
                result = {
                    "step": i + 1,
                    "name": step.get("name", ""),
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.now()
                }
                execution.step_results.append(result)
                execution.status = "failed"
                runbook.failure_count += 1
                break
                
        if execution.status != "failed":
            execution.status = "completed"
            runbook.success_count += 1
            
        execution.completed_at = datetime.now()
        runbook.last_executed = datetime.now()
        runbook.execution_count += 1
        
        return execution


class IncidentManager:
    """Менеджер инцидентов"""
    
    def __init__(self, responder_manager: ResponderManager):
        self.incidents: Dict[str, Incident] = {}
        self.responder_manager = responder_manager
        
    def create_incident(self, title: str, severity: IncidentSeverity,
                       incident_type: IncidentType, description: str = "",
                       affected_services: List[str] = None) -> Incident:
        """Создание инцидента"""
        incident = Incident(
            incident_id=f"INC-{uuid.uuid4().hex[:8].upper()}",
            title=title,
            description=description,
            severity=severity,
            incident_type=incident_type,
            affected_services=affected_services or []
        )
        
        # Add creation timeline entry
        incident.timeline.append(Timeline(
            entry_id=f"tl_{uuid.uuid4().hex[:8]}",
            event_type="created",
            description=f"Incident created: {title}",
            automated=True
        ))
        
        self.incidents[incident.incident_id] = incident
        return incident
        
    def acknowledge(self, incident_id: str, responder_id: str) -> bool:
        """Подтверждение инцидента"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return False
            
        if incident.status != IncidentStatus.DETECTED:
            return False
            
        incident.status = IncidentStatus.ACKNOWLEDGED
        incident.acknowledged_at = datetime.now()
        incident.time_to_acknowledge_sec = (incident.acknowledged_at - incident.detected_at).total_seconds()
        
        responder = self.responder_manager.responders.get(responder_id)
        responder_name = responder.name if responder else responder_id
        
        incident.timeline.append(Timeline(
            entry_id=f"tl_{uuid.uuid4().hex[:8]}",
            event_type="status_change",
            description=f"Incident acknowledged by {responder_name}",
            author_id=responder_id,
            author_name=responder_name
        ))
        
        return True
        
    def update_status(self, incident_id: str, new_status: IncidentStatus, 
                     responder_id: str, note: str = "") -> bool:
        """Обновление статуса"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return False
            
        old_status = incident.status
        incident.status = new_status
        
        if new_status == IncidentStatus.RESOLVED:
            incident.resolved_at = datetime.now()
            incident.time_to_resolve_sec = (incident.resolved_at - incident.detected_at).total_seconds()
        elif new_status == IncidentStatus.CLOSED:
            incident.closed_at = datetime.now()
            
        responder = self.responder_manager.responders.get(responder_id)
        responder_name = responder.name if responder else responder_id
        
        description = f"Status changed: {old_status.value} → {new_status.value}"
        if note:
            description += f"\nNote: {note}"
            
        incident.timeline.append(Timeline(
            entry_id=f"tl_{uuid.uuid4().hex[:8]}",
            event_type="status_change",
            description=description,
            author_id=responder_id,
            author_name=responder_name
        ))
        
        return True
        
    def add_responder(self, incident_id: str, responder_id: str) -> bool:
        """Добавление респондера"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return False
            
        if responder_id not in incident.responders:
            incident.responders.append(responder_id)
            
        return True
        
    def set_incident_commander(self, incident_id: str, responder_id: str) -> bool:
        """Назначение командира инцидента"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return False
            
        incident.incident_commander_id = responder_id
        
        responder = self.responder_manager.responders.get(responder_id)
        responder_name = responder.name if responder else responder_id
        
        incident.timeline.append(Timeline(
            entry_id=f"tl_{uuid.uuid4().hex[:8]}",
            event_type="assignment",
            description=f"Incident commander assigned: {responder_name}",
            automated=False
        ))
        
        return True


class PostMortemManager:
    """Менеджер post-mortem"""
    
    def __init__(self):
        self.postmortems: Dict[str, PostMortem] = {}
        
    def create_postmortem(self, incident: Incident) -> PostMortem:
        """Создание post-mortem"""
        postmortem = PostMortem(
            postmortem_id=f"PM-{uuid.uuid4().hex[:8].upper()}",
            incident_id=incident.incident_id,
            title=f"Post-Mortem: {incident.title}"
        )
        
        self.postmortems[postmortem.postmortem_id] = postmortem
        return postmortem
        
    def add_action_item(self, postmortem_id: str, action: Dict):
        """Добавление action item"""
        postmortem = self.postmortems.get(postmortem_id)
        if postmortem:
            postmortem.action_items.append(action)


class IncidentResponsePlatform:
    """Платформа реагирования на инциденты"""
    
    def __init__(self):
        self.responder_manager = ResponderManager()
        self.notification_service = NotificationService()
        self.escalation_engine = EscalationEngine(self.responder_manager, self.notification_service)
        self.runbook_executor = RunbookExecutor()
        self.incident_manager = IncidentManager(self.responder_manager)
        self.postmortem_manager = PostMortemManager()
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        incidents = list(self.incident_manager.incidents.values())
        
        open_incidents = [i for i in incidents if i.status not in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]]
        
        # Calculate MTTA and MTTR
        resolved = [i for i in incidents if i.resolved_at]
        mtta = sum(i.time_to_acknowledge_sec for i in incidents if i.acknowledged_at) / len(incidents) if incidents else 0
        mttr = sum(i.time_to_resolve_sec for i in resolved) / len(resolved) if resolved else 0
        
        return {
            "total_incidents": len(incidents),
            "open_incidents": len(open_incidents),
            "total_responders": len(self.responder_manager.responders),
            "total_runbooks": len(self.runbook_executor.runbooks),
            "total_postmortems": len(self.postmortem_manager.postmortems),
            "mtta_minutes": round(mtta / 60, 1),
            "mttr_minutes": round(mttr / 60, 1)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 172: Incident Response Platform")
    print("=" * 60)
    
    async def demo():
        platform = IncidentResponsePlatform()
        print("✓ Incident Response Platform created")
        
        # Add responders
        print("\n👥 Adding Responders...")
        
        responders = [
            Responder(
                responder_id="resp_001",
                name="Alice Smith",
                email="alice@example.com",
                role="incident_commander",
                team="platform",
                escalation_level=EscalationLevel.L1,
                on_call=True,
                preferred_channels=[NotificationChannel.SLACK, NotificationChannel.PAGERDUTY]
            ),
            Responder(
                responder_id="resp_002",
                name="Bob Johnson",
                email="bob@example.com",
                role="tech_lead",
                team="platform",
                escalation_level=EscalationLevel.L2,
                on_call=True,
                preferred_channels=[NotificationChannel.SLACK, NotificationChannel.SMS]
            ),
            Responder(
                responder_id="resp_003",
                name="Carol Williams",
                email="carol@example.com",
                role="engineering_manager",
                team="platform",
                escalation_level=EscalationLevel.L3,
                preferred_channels=[NotificationChannel.EMAIL, NotificationChannel.PHONE]
            ),
            Responder(
                responder_id="resp_004",
                name="David Brown",
                email="david@example.com",
                role="sre",
                team="infrastructure",
                escalation_level=EscalationLevel.L1,
                on_call=True,
                preferred_channels=[NotificationChannel.PAGERDUTY]
            ),
        ]
        
        for responder in responders:
            platform.responder_manager.add_responder(responder)
            print(f"  ✓ {responder.name} ({responder.role}, {responder.escalation_level.value})")
            
        # Setup on-call schedule
        platform.responder_manager.schedules["platform"] = OnCallSchedule(
            schedule_id="sched_001",
            team="platform",
            primary_responder_id="resp_001",
            secondary_responder_id="resp_002"
        )
        
        # Register runbooks
        print("\n📘 Registering Runbooks...")
        
        runbooks = [
            Runbook(
                runbook_id="rb_database_recovery",
                name="Database Recovery",
                description="Steps to recover from database issues",
                steps=[
                    {"name": "Check database connectivity", "command": "pg_isready"},
                    {"name": "Check replication status", "command": "SELECT * FROM pg_stat_replication"},
                    {"name": "Failover if needed", "command": "pg_ctl promote"},
                    {"name": "Verify data integrity", "command": "SELECT count(*) FROM critical_table"},
                ]
            ),
            Runbook(
                runbook_id="rb_service_restart",
                name="Service Restart Procedure",
                description="Standard service restart procedure",
                steps=[
                    {"name": "Drain connections", "command": "kubectl drain node"},
                    {"name": "Stop service", "command": "systemctl stop service"},
                    {"name": "Clear cache", "command": "redis-cli flushall"},
                    {"name": "Start service", "command": "systemctl start service"},
                    {"name": "Verify health", "command": "curl /health"},
                ]
            ),
            Runbook(
                runbook_id="rb_network_troubleshoot",
                name="Network Troubleshooting",
                description="Network connectivity troubleshooting steps",
                steps=[
                    {"name": "Check DNS", "command": "dig example.com"},
                    {"name": "Check connectivity", "command": "ping -c 5 gateway"},
                    {"name": "Check routes", "command": "ip route show"},
                    {"name": "Check firewall rules", "command": "iptables -L"},
                ]
            ),
        ]
        
        for runbook in runbooks:
            platform.runbook_executor.register_runbook(runbook)
            print(f"  ✓ {runbook.name} ({len(runbook.steps)} steps)")
            
        # Create incidents
        print("\n🚨 Creating Incidents...")
        
        # Incident 1: Critical outage
        incident1 = platform.incident_manager.create_incident(
            title="Production Database Unavailable",
            severity=IncidentSeverity.SEV1,
            incident_type=IncidentType.OUTAGE,
            description="Primary database cluster is not responding. All write operations failing.",
            affected_services=["api-gateway", "user-service", "order-service"]
        )
        print(f"\n  🔴 {incident1.incident_id}: {incident1.title}")
        print(f"     Severity: {incident1.severity.value}")
        print(f"     Affected: {', '.join(incident1.affected_services)}")
        
        # Notify on-call
        on_call = platform.responder_manager.get_on_call("platform")
        for responder in on_call:
            await platform.notification_service.notify(
                responder,
                f"[{incident1.severity.value.upper()}] {incident1.title}",
                incident1
            )
            
        # Incident 2: Performance degradation
        incident2 = platform.incident_manager.create_incident(
            title="High API Latency",
            severity=IncidentSeverity.SEV2,
            incident_type=IncidentType.PERFORMANCE,
            description="API response times exceeding 5 seconds for 30% of requests.",
            affected_services=["api-gateway"]
        )
        print(f"\n  🟠 {incident2.incident_id}: {incident2.title}")
        print(f"     Severity: {incident2.severity.value}")
        
        # Incident 3: Security incident
        incident3 = platform.incident_manager.create_incident(
            title="Suspicious Login Activity Detected",
            severity=IncidentSeverity.SEV3,
            incident_type=IncidentType.SECURITY,
            description="Multiple failed login attempts from unknown IP addresses.",
            affected_services=["auth-service"]
        )
        print(f"\n  🟡 {incident3.incident_id}: {incident3.title}")
        print(f"     Severity: {incident3.severity.value}")
        
        # Acknowledge incident
        print("\n✅ Acknowledging Incidents...")
        
        platform.incident_manager.acknowledge(incident1.incident_id, "resp_001")
        print(f"  ✓ {incident1.incident_id} acknowledged by Alice Smith")
        print(f"    Time to acknowledge: {incident1.time_to_acknowledge_sec:.1f}s")
        
        # Assign incident commander
        platform.incident_manager.set_incident_commander(incident1.incident_id, "resp_001")
        platform.incident_manager.add_responder(incident1.incident_id, "resp_002")
        platform.incident_manager.add_responder(incident1.incident_id, "resp_004")
        
        # Update status
        print("\n🔄 Updating Incident Status...")
        
        platform.incident_manager.update_status(
            incident1.incident_id,
            IncidentStatus.INVESTIGATING,
            "resp_001",
            "Starting investigation. Checking database cluster health."
        )
        
        # Execute runbook
        print("\n📋 Executing Runbook...")
        
        execution = await platform.runbook_executor.execute(
            "rb_database_recovery",
            incident1,
            "resp_001"
        )
        
        if execution:
            print(f"\n  Runbook: {platform.runbook_executor.runbooks[execution.runbook_id].name}")
            print(f"  Status: {execution.status}")
            print(f"  Steps completed: {len(execution.step_results)}/{execution.total_steps}")
            
            for result in execution.step_results:
                status_icon = "✓" if result["status"] == "success" else "✗"
                print(f"    {status_icon} Step {result['step']}: {result['name']}")
                
        # Identify root cause
        print("\n🔍 Root Cause Identified...")
        
        platform.incident_manager.update_status(
            incident1.incident_id,
            IncidentStatus.IDENTIFIED,
            "resp_001",
            "Root cause: Disk space exhausted on primary database node."
        )
        incident1.root_cause = "Disk space exhausted due to unrotated transaction logs"
        
        # Resolve incident
        print("\n✅ Resolving Incident...")
        
        # Add some delay to simulate time passing
        await asyncio.sleep(0.5)
        
        platform.incident_manager.update_status(
            incident1.incident_id,
            IncidentStatus.RESOLVED,
            "resp_001",
            "Disk space freed. Service restored. Monitoring for stability."
        )
        
        print(f"  {incident1.incident_id} resolved")
        print(f"  Time to resolve: {incident1.time_to_resolve_sec:.1f}s")
        
        # Timeline
        print("\n📜 Incident Timeline:")
        
        print(f"\n  Incident: {incident1.incident_id}")
        print("  ─" * 35)
        
        for entry in incident1.timeline:
            time_str = entry.timestamp.strftime("%H:%M:%S")
            event = entry.event_type[:12].ljust(12)
            auto = "🤖" if entry.automated else "👤"
            print(f"  {time_str} │ {event} │ {auto} {entry.description[:40]}")
            
        # Create post-mortem
        print("\n📝 Creating Post-Mortem...")
        
        postmortem = platform.postmortem_manager.create_postmortem(incident1)
        postmortem.summary = "Production database became unavailable due to disk space exhaustion."
        postmortem.root_cause_analysis = """
        The primary database node ran out of disk space due to transaction logs
        not being rotated properly. The log rotation cron job failed silently
        two weeks ago when the logrotate package was updated.
        """
        postmortem.lessons_learned = [
            "Implement disk space monitoring alerts",
            "Add health checks for cron jobs",
            "Review log rotation configuration quarterly"
        ]
        
        platform.postmortem_manager.add_action_item(postmortem.postmortem_id, {
            "action": "Implement disk space alerts at 80% threshold",
            "owner": "resp_004",
            "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "status": "pending"
        })
        
        platform.postmortem_manager.add_action_item(postmortem.postmortem_id, {
            "action": "Create cron job monitoring dashboard",
            "owner": "resp_002",
            "due_date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
            "status": "pending"
        })
        
        print(f"  ✓ Post-mortem created: {postmortem.postmortem_id}")
        print(f"  Action items: {len(postmortem.action_items)}")
        print(f"  Lessons learned: {len(postmortem.lessons_learned)}")
        
        # All incidents summary
        print("\n📊 Incident Summary:")
        
        all_incidents = list(platform.incident_manager.incidents.values())
        
        print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────┐")
        print("  │ ID              │ Severity │ Status         │ Title                               │")
        print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────┤")
        
        for inc in all_incidents:
            inc_id = inc.incident_id[:15].ljust(15)
            sev = inc.severity.value[:8].ljust(8)
            status = inc.status.value[:14].ljust(14)
            title = inc.title[:35].ljust(35)
            print(f"  │ {inc_id} │ {sev} │ {status} │ {title} │")
            
        print("  └────────────────────────────────────────────────────────────────────────────────────────────────────┘")
        
        # Notifications sent
        print("\n📧 Notifications Sent:")
        print(f"  Total: {len(platform.notification_service.sent_notifications)}")
        
        channel_counts = defaultdict(int)
        for notif in platform.notification_service.sent_notifications:
            channel_counts[notif["channel"]] += 1
            
        for channel, count in sorted(channel_counts.items()):
            print(f"    {channel}: {count}")
            
        # Platform statistics
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Incidents: {stats['total_incidents']}")
        print(f"  Open Incidents: {stats['open_incidents']}")
        print(f"  Responders: {stats['total_responders']}")
        print(f"  Runbooks: {stats['total_runbooks']}")
        print(f"  Post-Mortems: {stats['total_postmortems']}")
        print(f"  MTTA: {stats['mtta_minutes']} minutes")
        print(f"  MTTR: {stats['mttr_minutes']} minutes")
        
        # Severity distribution
        print("\n  Incidents by Severity:")
        
        sev_counts = defaultdict(int)
        for inc in all_incidents:
            sev_counts[inc.severity.value] += 1
            
        for sev in ["sev1", "sev2", "sev3", "sev4", "sev5"]:
            count = sev_counts.get(sev, 0)
            bar = "█" * count * 5
            print(f"    {sev}: {bar} {count}")
            
        # Dashboard
        print("\n┌────────────────────────────────────────────────────────────────────┐")
        print("│                 Incident Response Dashboard                        │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Open Incidents:              {stats['open_incidents']:>10}                       │")
        print(f"│ Total Incidents:             {stats['total_incidents']:>10}                       │")
        print(f"│ MTTA:                        {stats['mtta_minutes']:>8.1f} min                   │")
        print(f"│ MTTR:                        {stats['mttr_minutes']:>8.1f} min                   │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Available Responders:        {stats['total_responders']:>10}                       │")
        print(f"│ Runbooks Available:          {stats['total_runbooks']:>10}                       │")
        print(f"│ Post-Mortems:                {stats['total_postmortems']:>10}                       │")
        print("└────────────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Incident Response Platform initialized!")
    print("=" * 60)
