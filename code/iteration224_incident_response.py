#!/usr/bin/env python3
"""
Server Init - Iteration 224: Incident Response Platform
Платформа реагирования на инциденты

Функционал:
- Incident Creation - создание инцидентов
- Severity Classification - классификация по серьёзности
- Escalation Rules - правила эскалации
- On-Call Management - управление дежурствами
- Timeline Tracking - отслеживание таймлайна
- Postmortem Generation - генерация постмортемов
- Notification System - система уведомлений
- Metrics & Analytics - метрики и аналитика
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class IncidentSeverity(Enum):
    """Серьёзность инцидента"""
    SEV1 = "sev1"  # Critical - business impacting
    SEV2 = "sev2"  # High - partial outage
    SEV3 = "sev3"  # Medium - degraded performance
    SEV4 = "sev4"  # Low - minor issue


class IncidentStatus(Enum):
    """Статус инцидента"""
    TRIGGERED = "triggered"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MONITORING = "monitoring"
    RESOLVED = "resolved"


class EscalationLevel(Enum):
    """Уровень эскалации"""
    L1 = "l1"  # Primary on-call
    L2 = "l2"  # Secondary on-call
    L3 = "l3"  # Team lead
    L4 = "l4"  # Management


class NotificationType(Enum):
    """Тип уведомления"""
    EMAIL = "email"
    SLACK = "slack"
    SMS = "sms"
    PAGERDUTY = "pagerduty"
    PHONE = "phone"


@dataclass
class Responder:
    """Респондер"""
    responder_id: str
    name: str = ""
    email: str = ""
    phone: str = ""
    slack_id: str = ""
    team: str = ""
    is_oncall: bool = False


@dataclass
class OnCallSchedule:
    """Расписание дежурств"""
    schedule_id: str
    team: str = ""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime = field(default_factory=datetime.now)
    primary_responder: Optional[Responder] = None
    secondary_responder: Optional[Responder] = None


@dataclass
class EscalationPolicy:
    """Политика эскалации"""
    policy_id: str
    name: str = ""
    levels: List[EscalationLevel] = field(default_factory=list)
    timeout_minutes: int = 15
    repeat: bool = True


@dataclass
class TimelineEvent:
    """Событие таймлайна"""
    event_id: str
    incident_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    event_type: str = ""  # status_change, note, escalation, notification
    description: str = ""
    author: str = ""


@dataclass
class IncidentNotification:
    """Уведомление об инциденте"""
    notification_id: str
    incident_id: str = ""
    responder_id: str = ""
    notification_type: NotificationType = NotificationType.SLACK
    sent_at: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False


@dataclass
class Incident:
    """Инцидент"""
    incident_id: str
    title: str = ""
    description: str = ""
    
    # Classification
    severity: IncidentSeverity = IncidentSeverity.SEV3
    status: IncidentStatus = IncidentStatus.TRIGGERED
    
    # Affected
    affected_services: List[str] = field(default_factory=list)
    affected_customers: int = 0
    
    # Responders
    commander: Optional[Responder] = None
    responders: List[Responder] = field(default_factory=list)
    
    # Timeline
    timeline: List[TimelineEvent] = field(default_factory=list)
    
    # Escalation
    escalation_level: EscalationLevel = EscalationLevel.L1
    escalation_policy_id: str = ""
    
    # Times
    created_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Metrics
    time_to_acknowledge_mins: float = 0
    time_to_resolve_mins: float = 0
    
    # Root cause
    root_cause: str = ""
    resolution: str = ""


@dataclass
class Postmortem:
    """Постмортем"""
    postmortem_id: str
    incident_id: str = ""
    title: str = ""
    
    # Summary
    summary: str = ""
    impact: str = ""
    root_cause: str = ""
    
    # Timeline
    timeline_summary: List[str] = field(default_factory=list)
    
    # Actions
    action_items: List[str] = field(default_factory=list)
    
    # Lessons
    lessons_learned: List[str] = field(default_factory=list)
    
    # Status
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "draft"  # draft, review, published


class OnCallManager:
    """Менеджер дежурств"""
    
    def __init__(self):
        self.schedules: Dict[str, OnCallSchedule] = {}
        self.responders: Dict[str, Responder] = {}
        
    def register_responder(self, name: str, email: str, phone: str,
                          team: str, slack_id: str = "") -> Responder:
        """Регистрация респондера"""
        responder = Responder(
            responder_id=f"resp_{uuid.uuid4().hex[:8]}",
            name=name,
            email=email,
            phone=phone,
            team=team,
            slack_id=slack_id
        )
        self.responders[responder.responder_id] = responder
        return responder
        
    def create_schedule(self, team: str, primary: Responder,
                       secondary: Responder, hours: int = 24) -> OnCallSchedule:
        """Создание расписания"""
        now = datetime.now()
        schedule = OnCallSchedule(
            schedule_id=f"sch_{uuid.uuid4().hex[:8]}",
            team=team,
            start_time=now,
            end_time=now + timedelta(hours=hours),
            primary_responder=primary,
            secondary_responder=secondary
        )
        
        primary.is_oncall = True
        secondary.is_oncall = True
        
        self.schedules[schedule.schedule_id] = schedule
        return schedule
        
    def get_oncall(self, team: str) -> Optional[Responder]:
        """Получить дежурного"""
        for schedule in self.schedules.values():
            if schedule.team == team:
                now = datetime.now()
                if schedule.start_time <= now <= schedule.end_time:
                    return schedule.primary_responder
        return None


class EscalationManager:
    """Менеджер эскалации"""
    
    def __init__(self):
        self.policies: Dict[str, EscalationPolicy] = {}
        
    def create_policy(self, name: str, timeout: int = 15) -> EscalationPolicy:
        """Создание политики"""
        policy = EscalationPolicy(
            policy_id=f"pol_{uuid.uuid4().hex[:8]}",
            name=name,
            levels=[EscalationLevel.L1, EscalationLevel.L2, EscalationLevel.L3],
            timeout_minutes=timeout
        )
        self.policies[policy.policy_id] = policy
        return policy
        
    def should_escalate(self, incident: Incident, elapsed_mins: float) -> bool:
        """Проверка необходимости эскалации"""
        policy = self.policies.get(incident.escalation_policy_id)
        if not policy:
            return False
            
        if incident.status == IncidentStatus.TRIGGERED:
            return elapsed_mins >= policy.timeout_minutes
        return False
        
    def escalate(self, incident: Incident) -> EscalationLevel:
        """Эскалация инцидента"""
        levels = [EscalationLevel.L1, EscalationLevel.L2, 
                 EscalationLevel.L3, EscalationLevel.L4]
        
        current_idx = levels.index(incident.escalation_level)
        if current_idx < len(levels) - 1:
            incident.escalation_level = levels[current_idx + 1]
            
        return incident.escalation_level


class NotificationService:
    """Сервис уведомлений"""
    
    def __init__(self):
        self.notifications: List[IncidentNotification] = []
        
    async def notify(self, incident: Incident, responder: Responder,
                    notification_type: NotificationType) -> IncidentNotification:
        """Отправка уведомления"""
        notification = IncidentNotification(
            notification_id=f"notif_{uuid.uuid4().hex[:8]}",
            incident_id=incident.incident_id,
            responder_id=responder.responder_id,
            notification_type=notification_type
        )
        
        self.notifications.append(notification)
        return notification
        
    async def notify_all(self, incident: Incident,
                        responders: List[Responder]) -> List[IncidentNotification]:
        """Уведомление всех"""
        notifications = []
        for responder in responders:
            notif = await self.notify(incident, responder, NotificationType.SLACK)
            notifications.append(notif)
        return notifications


class IncidentResponsePlatform:
    """Платформа реагирования на инциденты"""
    
    def __init__(self):
        self.incidents: Dict[str, Incident] = {}
        self.postmortems: Dict[str, Postmortem] = {}
        self.oncall = OnCallManager()
        self.escalation = EscalationManager()
        self.notifications = NotificationService()
        
    def create_incident(self, title: str, description: str,
                       severity: IncidentSeverity,
                       affected_services: List[str] = None) -> Incident:
        """Создание инцидента"""
        incident = Incident(
            incident_id=f"inc_{uuid.uuid4().hex[:8]}",
            title=title,
            description=description,
            severity=severity,
            affected_services=affected_services or []
        )
        
        # Add initial timeline event
        event = TimelineEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            incident_id=incident.incident_id,
            event_type="created",
            description=f"Incident created: {title}",
            author="system"
        )
        incident.timeline.append(event)
        
        self.incidents[incident.incident_id] = incident
        return incident
        
    def acknowledge(self, incident_id: str, responder: Responder) -> bool:
        """Подтверждение инцидента"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return False
            
        incident.status = IncidentStatus.ACKNOWLEDGED
        incident.acknowledged_at = datetime.now()
        incident.commander = responder
        incident.responders.append(responder)
        
        # Calculate TTA
        incident.time_to_acknowledge_mins = (
            incident.acknowledged_at - incident.created_at
        ).total_seconds() / 60
        
        # Timeline event
        event = TimelineEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            incident_id=incident.incident_id,
            event_type="acknowledged",
            description=f"Acknowledged by {responder.name}",
            author=responder.name
        )
        incident.timeline.append(event)
        
        return True
        
    def update_status(self, incident_id: str, status: IncidentStatus,
                     note: str = "", author: str = "system") -> bool:
        """Обновление статуса"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return False
            
        old_status = incident.status
        incident.status = status
        
        event = TimelineEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            incident_id=incident.incident_id,
            event_type="status_change",
            description=f"Status: {old_status.value} -> {status.value}. {note}",
            author=author
        )
        incident.timeline.append(event)
        
        return True
        
    def resolve(self, incident_id: str, resolution: str,
               root_cause: str = "") -> bool:
        """Разрешение инцидента"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return False
            
        incident.status = IncidentStatus.RESOLVED
        incident.resolved_at = datetime.now()
        incident.resolution = resolution
        incident.root_cause = root_cause
        
        # Calculate TTR
        incident.time_to_resolve_mins = (
            incident.resolved_at - incident.created_at
        ).total_seconds() / 60
        
        event = TimelineEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            incident_id=incident.incident_id,
            event_type="resolved",
            description=f"Resolved: {resolution}",
            author="system"
        )
        incident.timeline.append(event)
        
        return True
        
    def add_note(self, incident_id: str, note: str, author: str) -> bool:
        """Добавление заметки"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return False
            
        event = TimelineEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            incident_id=incident.incident_id,
            event_type="note",
            description=note,
            author=author
        )
        incident.timeline.append(event)
        
        return True
        
    def create_postmortem(self, incident_id: str) -> Optional[Postmortem]:
        """Создание постмортема"""
        incident = self.incidents.get(incident_id)
        if not incident or incident.status != IncidentStatus.RESOLVED:
            return None
            
        postmortem = Postmortem(
            postmortem_id=f"pm_{uuid.uuid4().hex[:8]}",
            incident_id=incident_id,
            title=f"Postmortem: {incident.title}",
            summary=f"Incident {incident.incident_id} affecting {len(incident.affected_services)} services",
            impact=f"Duration: {incident.time_to_resolve_mins:.0f} minutes",
            root_cause=incident.root_cause,
            timeline_summary=[e.description for e in incident.timeline],
            action_items=[
                "Review monitoring gaps",
                "Update runbooks",
                "Improve alerting"
            ],
            lessons_learned=[
                "Earlier detection needed",
                "Communication could be improved"
            ]
        )
        
        self.postmortems[postmortem.postmortem_id] = postmortem
        return postmortem
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        incidents = list(self.incidents.values())
        resolved = [i for i in incidents if i.status == IncidentStatus.RESOLVED]
        
        by_severity = {}
        for i in incidents:
            s = i.severity.value
            if s not in by_severity:
                by_severity[s] = 0
            by_severity[s] += 1
            
        avg_tta = sum(i.time_to_acknowledge_mins for i in resolved) / len(resolved) if resolved else 0
        avg_ttr = sum(i.time_to_resolve_mins for i in resolved) / len(resolved) if resolved else 0
        
        return {
            "total_incidents": len(incidents),
            "active_incidents": len([i for i in incidents if i.status != IncidentStatus.RESOLVED]),
            "resolved_incidents": len(resolved),
            "by_severity": by_severity,
            "avg_time_to_acknowledge": avg_tta,
            "avg_time_to_resolve": avg_ttr,
            "postmortems_created": len(self.postmortems)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 224: Incident Response Platform")
    print("=" * 60)
    
    platform = IncidentResponsePlatform()
    print("✓ Incident Response Platform created")
    
    # Register responders
    print("\n👤 Registering Responders...")
    
    responders = [
        platform.oncall.register_responder("Alex Kim", "alex@company.com", "+1-555-0001", "Platform"),
        platform.oncall.register_responder("Maria Garcia", "maria@company.com", "+1-555-0002", "Platform"),
        platform.oncall.register_responder("John Smith", "john@company.com", "+1-555-0003", "Backend"),
        platform.oncall.register_responder("Sarah Lee", "sarah@company.com", "+1-555-0004", "Backend"),
    ]
    
    for r in responders:
        print(f"  ✓ {r.name} ({r.team})")
        
    # Create on-call schedules
    print("\n📅 Creating On-Call Schedules...")
    
    platform.oncall.create_schedule("Platform", responders[0], responders[1])
    platform.oncall.create_schedule("Backend", responders[2], responders[3])
    print(f"  ✓ Platform: {responders[0].name} (primary)")
    print(f"  ✓ Backend: {responders[2].name} (primary)")
    
    # Create escalation policies
    print("\n⚡ Creating Escalation Policies...")
    
    policy = platform.escalation.create_policy("Default", timeout=15)
    print(f"  ✓ {policy.name}: timeout {policy.timeout_minutes}min")
    
    # Create incidents
    print("\n🚨 Creating Incidents...")
    
    incidents_config = [
        ("API Gateway Down", "Complete outage of API gateway", IncidentSeverity.SEV1, ["api-gateway"]),
        ("Database Latency", "High latency on main database", IncidentSeverity.SEV2, ["postgres-main"]),
        ("Payment Errors", "Increased error rate in payments", IncidentSeverity.SEV2, ["payment-service"]),
        ("Cache Miss Rate", "High cache miss rate", IncidentSeverity.SEV3, ["redis-cache"]),
        ("Memory Leak", "Memory leak in user service", IncidentSeverity.SEV3, ["user-service"]),
    ]
    
    incidents = []
    for title, desc, severity, services in incidents_config:
        incident = platform.create_incident(title, desc, severity, services)
        incident.escalation_policy_id = policy.policy_id
        incidents.append(incident)
        
        sev_icons = {
            IncidentSeverity.SEV1: "🔴",
            IncidentSeverity.SEV2: "🟠",
            IncidentSeverity.SEV3: "🟡",
            IncidentSeverity.SEV4: "🟢"
        }
        print(f"  {sev_icons[severity]} {title} ({severity.value})")
        
    # Acknowledge incidents
    print("\n✅ Acknowledging Incidents...")
    
    for i, incident in enumerate(incidents):
        responder = responders[i % len(responders)]
        platform.acknowledge(incident.incident_id, responder)
        await asyncio.sleep(0.01)
        print(f"  ✓ {incident.title} -> {responder.name}")
        
    # Update statuses
    print("\n📝 Updating Incident Statuses...")
    
    status_flow = [
        IncidentStatus.INVESTIGATING,
        IncidentStatus.IDENTIFIED,
        IncidentStatus.MONITORING,
    ]
    
    for incident in incidents:
        for status in status_flow:
            platform.update_status(
                incident.incident_id,
                status,
                f"Moving to {status.value}",
                incident.commander.name if incident.commander else "system"
            )
            
    print(f"  ✓ Updated {len(incidents)} incidents through flow")
    
    # Add notes
    print("\n📋 Adding Investigation Notes...")
    
    notes = [
        "Investigating network connectivity",
        "Found potential root cause",
        "Implementing fix",
        "Monitoring recovery"
    ]
    
    for incident in incidents[:3]:
        for note in notes:
            platform.add_note(
                incident.incident_id,
                note,
                incident.commander.name if incident.commander else "system"
            )
            
    print(f"  ✓ Added notes to incidents")
    
    # Resolve incidents
    print("\n✔️ Resolving Incidents...")
    
    resolutions = [
        ("Restarted gateway pods", "Configuration drift"),
        ("Scaled database replicas", "Connection pool exhaustion"),
        ("Rolled back deployment", "Bug in new release"),
        ("Increased cache TTL", "Hot key issue"),
    ]
    
    for i, incident in enumerate(incidents[:-1]):
        resolution, root_cause = resolutions[i % len(resolutions)]
        platform.resolve(incident.incident_id, resolution, root_cause)
        print(f"  ✓ {incident.title}: {resolution}")
        
    # Create postmortems
    print("\n📄 Creating Postmortems...")
    
    for incident in incidents[:-1]:
        postmortem = platform.create_postmortem(incident.incident_id)
        if postmortem:
            print(f"  ✓ {postmortem.title}")
            
    # Display incidents
    print("\n📋 Incident List:")
    
    print("\n  ┌────────────────────────┬────────┬───────────────┬──────────┐")
    print("  │ Incident               │ Sev    │ Status        │ TTR      │")
    print("  ├────────────────────────┼────────┼───────────────┼──────────┤")
    
    sev_icons = {
        IncidentSeverity.SEV1: "🔴",
        IncidentSeverity.SEV2: "🟠",
        IncidentSeverity.SEV3: "🟡",
        IncidentSeverity.SEV4: "🟢"
    }
    
    for incident in platform.incidents.values():
        title = incident.title[:20].ljust(20)
        sev = f"{sev_icons.get(incident.severity, '⚪')} {incident.severity.value}"[:6].ljust(6)
        status = incident.status.value[:13].ljust(13)
        ttr = f"{incident.time_to_resolve_mins:.0f}m" if incident.time_to_resolve_mins > 0 else "active"
        ttr = ttr[:8].ljust(8)
        
        print(f"  │ {title} │ {sev} │ {status} │ {ttr} │")
        
    print("  └────────────────────────┴────────┴───────────────┴──────────┘")
    
    # Timeline for first incident
    print(f"\n📜 Timeline for: {incidents[0].title}")
    
    for event in incidents[0].timeline[:8]:
        time_str = event.timestamp.strftime("%H:%M")
        desc = event.description[:45]
        print(f"  [{time_str}] {desc}")
        
    # Incidents by severity
    print("\n📊 Incidents by Severity:")
    
    stats = platform.get_statistics()
    
    for sev in ["sev1", "sev2", "sev3", "sev4"]:
        count = stats["by_severity"].get(sev, 0)
        icon = {"sev1": "🔴", "sev2": "🟠", "sev3": "🟡", "sev4": "🟢"}.get(sev, "⚪")
        bar = "█" * count + "░" * (5 - count)
        print(f"  {icon} {sev.upper()} [{bar}] {count}")
        
    # MTTA/MTTR
    print("\n⏱ Response Metrics:")
    
    print(f"  Mean Time to Acknowledge (MTTA): {stats['avg_time_to_acknowledge']:.1f} minutes")
    print(f"  Mean Time to Resolve (MTTR):     {stats['avg_time_to_resolve']:.1f} minutes")
    
    # Postmortem summary
    print("\n📄 Postmortem Summary:")
    
    for pm in list(platform.postmortems.values())[:3]:
        print(f"\n  {pm.title}")
        print(f"    Root Cause: {pm.root_cause}")
        print(f"    Action Items: {len(pm.action_items)}")
        
    # On-call status
    print("\n👤 Current On-Call:")
    
    for team in ["Platform", "Backend"]:
        oncall = platform.oncall.get_oncall(team)
        if oncall:
            print(f"  {team}: {oncall.name} ({oncall.email})")
            
    # Statistics
    print("\n📈 Platform Statistics:")
    
    print(f"\n  Total Incidents: {stats['total_incidents']}")
    print(f"  Active: {stats['active_incidents']}")
    print(f"  Resolved: {stats['resolved_incidents']}")
    print(f"  Postmortems: {stats['postmortems_created']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Incident Response Dashboard                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Incidents:               {stats['total_incidents']:>12}                        │")
    print(f"│ Active Incidents:              {stats['active_incidents']:>12}                        │")
    print(f"│ Resolved Incidents:            {stats['resolved_incidents']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ MTTA (minutes):                  {stats['avg_time_to_acknowledge']:>10.1f}                        │")
    print(f"│ MTTR (minutes):                  {stats['avg_time_to_resolve']:>10.1f}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Incident Response Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
