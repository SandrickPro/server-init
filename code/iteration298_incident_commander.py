#!/usr/bin/env python3
"""
Server Init - Iteration 298: Incident Commander Platform
Платформа управления инцидентами

Функционал:
- Incident Detection - обнаружение инцидентов
- Severity Classification - классификация серьёзности
- Escalation Management - управление эскалациями
- War Room Coordination - координация war room
- Communication Automation - автоматизация коммуникаций
- Post-Mortem Analysis - post-mortem анализ
- SLA Tracking - отслеживание SLA
- On-Call Management - управление дежурствами
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
    SEV1 = "sev1"  # Critical - system down
    SEV2 = "sev2"  # Major - significant impact
    SEV3 = "sev3"  # Minor - limited impact
    SEV4 = "sev4"  # Low - minimal impact


class IncidentStatus(Enum):
    """Статус инцидента"""
    DETECTED = "detected"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentCategory(Enum):
    """Категория инцидента"""
    INFRASTRUCTURE = "infrastructure"
    APPLICATION = "application"
    NETWORK = "network"
    DATABASE = "database"
    SECURITY = "security"
    PERFORMANCE = "performance"


class EscalationLevel(Enum):
    """Уровень эскалации"""
    L1 = "level_1"
    L2 = "level_2"
    L3 = "level_3"
    MANAGEMENT = "management"
    EXECUTIVE = "executive"


@dataclass
class OnCallSchedule:
    """Расписание дежурств"""
    schedule_id: str
    team: str
    
    # Current on-call
    primary: str = ""
    secondary: str = ""
    
    # Schedule
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    # Rotation
    rotation_hours: int = 24
    
    # Contact
    phone: str = ""
    email: str = ""


@dataclass
class Escalation:
    """Эскалация"""
    escalation_id: str
    incident_id: str
    
    # Level
    from_level: EscalationLevel = EscalationLevel.L1
    to_level: EscalationLevel = EscalationLevel.L2
    
    # Reason
    reason: str = ""
    
    # Target
    escalated_to: str = ""
    
    # Status
    acknowledged: bool = False
    
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TimelineEntry:
    """Запись таймлайна"""
    entry_id: str
    incident_id: str
    
    # Content
    timestamp: datetime = field(default_factory=datetime.now)
    action: str = ""
    description: str = ""
    
    # Actor
    user: str = ""
    automated: bool = False


@dataclass
class Communication:
    """Коммуникация"""
    comm_id: str
    incident_id: str
    
    # Type
    channel: str = ""  # slack, email, sms, pagerduty
    
    # Content
    message: str = ""
    
    # Recipients
    recipients: List[str] = field(default_factory=list)
    
    # Status
    sent: bool = False
    
    sent_at: Optional[datetime] = None


@dataclass
class PostMortem:
    """Post-Mortem"""
    postmortem_id: str
    incident_id: str
    
    # Summary
    title: str = ""
    summary: str = ""
    
    # Timeline
    detection_time: Optional[datetime] = None
    resolution_time: Optional[datetime] = None
    
    # Impact
    impact: str = ""
    affected_users: int = 0
    
    # Analysis
    root_cause: str = ""
    contributing_factors: List[str] = field(default_factory=list)
    
    # Actions
    action_items: List[str] = field(default_factory=list)
    
    # Status
    completed: bool = False
    
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Incident:
    """Инцидент"""
    incident_id: str
    title: str
    
    # Classification
    severity: IncidentSeverity = IncidentSeverity.SEV3
    status: IncidentStatus = IncidentStatus.DETECTED
    category: IncidentCategory = IncidentCategory.APPLICATION
    
    # Description
    description: str = ""
    
    # Impact
    impact: str = ""
    affected_services: List[str] = field(default_factory=list)
    affected_users: int = 0
    
    # Assignment
    commander: str = ""
    responders: List[str] = field(default_factory=list)
    
    # Escalation
    escalation_level: EscalationLevel = EscalationLevel.L1
    
    # Timeline
    timeline: List[str] = field(default_factory=list)
    
    # Communication
    communications: List[str] = field(default_factory=list)
    
    # Resolution
    resolution: str = ""
    
    # SLA
    sla_deadline: Optional[datetime] = None
    sla_breached: bool = False
    
    # Timestamps
    detected_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Post-mortem
    postmortem_id: Optional[str] = None


class IncidentCommanderManager:
    """Менеджер Incident Commander"""
    
    def __init__(self):
        self.incidents: Dict[str, Incident] = {}
        self.escalations: Dict[str, Escalation] = {}
        self.timeline_entries: Dict[str, TimelineEntry] = {}
        self.communications: Dict[str, Communication] = {}
        self.postmortems: Dict[str, PostMortem] = {}
        self.schedules: Dict[str, OnCallSchedule] = {}
        
        # Stats
        self.incidents_resolved: int = 0
        self.escalations_total: int = 0
        self.communications_sent: int = 0
        
        # SLA targets (minutes)
        self.sla_targets = {
            IncidentSeverity.SEV1: 15,
            IncidentSeverity.SEV2: 60,
            IncidentSeverity.SEV3: 240,
            IncidentSeverity.SEV4: 1440
        }
        
    async def create_incident(self, title: str,
                             severity: IncidentSeverity = IncidentSeverity.SEV3,
                             category: IncidentCategory = IncidentCategory.APPLICATION,
                             description: str = "",
                             affected_services: List[str] = None) -> Incident:
        """Создание инцидента"""
        incident = Incident(
            incident_id=f"INC-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}",
            title=title,
            severity=severity,
            category=category,
            description=description,
            affected_services=affected_services or []
        )
        
        # Set SLA deadline
        sla_minutes = self.sla_targets.get(severity, 240)
        incident.sla_deadline = datetime.now() + timedelta(minutes=sla_minutes)
        
        self.incidents[incident.incident_id] = incident
        
        # Add initial timeline entry
        await self._add_timeline_entry(incident.incident_id, "Incident created", f"Severity: {severity.value}", automated=True)
        
        return incident
        
    async def acknowledge_incident(self, incident_id: str, commander: str) -> bool:
        """Подтверждение инцидента"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return False
            
        incident.status = IncidentStatus.ACKNOWLEDGED
        incident.commander = commander
        incident.acknowledged_at = datetime.now()
        
        await self._add_timeline_entry(incident_id, "Incident acknowledged", f"Commander: {commander}", user=commander)
        
        return True
        
    async def update_status(self, incident_id: str, status: IncidentStatus, note: str = "") -> bool:
        """Обновление статуса"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return False
            
        old_status = incident.status
        incident.status = status
        
        if status == IncidentStatus.RESOLVED:
            incident.resolved_at = datetime.now()
            self.incidents_resolved += 1
            
        await self._add_timeline_entry(
            incident_id,
            f"Status changed: {old_status.value} → {status.value}",
            note,
            user=incident.commander
        )
        
        return True
        
    async def add_responder(self, incident_id: str, responder: str) -> bool:
        """Добавление респондера"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return False
            
        if responder not in incident.responders:
            incident.responders.append(responder)
            await self._add_timeline_entry(incident_id, "Responder joined", responder)
            
        return True
        
    async def escalate(self, incident_id: str, to_level: EscalationLevel, reason: str = "") -> Optional[Escalation]:
        """Эскалация"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return None
            
        escalation = Escalation(
            escalation_id=f"esc_{uuid.uuid4().hex[:8]}",
            incident_id=incident_id,
            from_level=incident.escalation_level,
            to_level=to_level,
            reason=reason
        )
        
        incident.escalation_level = to_level
        self.escalations[escalation.escalation_id] = escalation
        self.escalations_total += 1
        
        await self._add_timeline_entry(
            incident_id,
            f"Escalated to {to_level.value}",
            reason,
            automated=True
        )
        
        return escalation
        
    async def _add_timeline_entry(self, incident_id: str, action: str, 
                                 description: str = "", user: str = "",
                                 automated: bool = False) -> TimelineEntry:
        """Добавление записи в таймлайн"""
        entry = TimelineEntry(
            entry_id=f"tl_{uuid.uuid4().hex[:8]}",
            incident_id=incident_id,
            action=action,
            description=description,
            user=user,
            automated=automated
        )
        
        self.timeline_entries[entry.entry_id] = entry
        
        incident = self.incidents.get(incident_id)
        if incident:
            incident.timeline.append(entry.entry_id)
            
        return entry
        
    async def send_communication(self, incident_id: str, channel: str,
                                message: str, recipients: List[str]) -> Optional[Communication]:
        """Отправка коммуникации"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return None
            
        comm = Communication(
            comm_id=f"comm_{uuid.uuid4().hex[:8]}",
            incident_id=incident_id,
            channel=channel,
            message=message,
            recipients=recipients,
            sent=True,
            sent_at=datetime.now()
        )
        
        self.communications[comm.comm_id] = comm
        incident.communications.append(comm.comm_id)
        self.communications_sent += 1
        
        return comm
        
    async def create_postmortem(self, incident_id: str) -> Optional[PostMortem]:
        """Создание post-mortem"""
        incident = self.incidents.get(incident_id)
        if not incident or incident.status not in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]:
            return None
            
        pm = PostMortem(
            postmortem_id=f"pm_{uuid.uuid4().hex[:8]}",
            incident_id=incident_id,
            title=f"Post-Mortem: {incident.title}",
            detection_time=incident.detected_at,
            resolution_time=incident.resolved_at,
            affected_users=incident.affected_users
        )
        
        # Calculate duration
        if incident.resolved_at:
            duration = incident.resolved_at - incident.detected_at
            pm.summary = f"Incident lasted {duration.total_seconds() / 60:.0f} minutes"
            
        self.postmortems[pm.postmortem_id] = pm
        incident.postmortem_id = pm.postmortem_id
        
        return pm
        
    async def update_postmortem(self, postmortem_id: str,
                               root_cause: str = "",
                               contributing_factors: List[str] = None,
                               action_items: List[str] = None) -> bool:
        """Обновление post-mortem"""
        pm = self.postmortems.get(postmortem_id)
        if not pm:
            return False
            
        if root_cause:
            pm.root_cause = root_cause
        if contributing_factors:
            pm.contributing_factors.extend(contributing_factors)
        if action_items:
            pm.action_items.extend(action_items)
            
        return True
        
    async def create_oncall_schedule(self, team: str, primary: str,
                                    secondary: str, rotation_hours: int = 24) -> OnCallSchedule:
        """Создание расписания дежурств"""
        schedule = OnCallSchedule(
            schedule_id=f"sch_{uuid.uuid4().hex[:8]}",
            team=team,
            primary=primary,
            secondary=secondary,
            rotation_hours=rotation_hours,
            end_time=datetime.now() + timedelta(hours=rotation_hours)
        )
        
        self.schedules[schedule.schedule_id] = schedule
        return schedule
        
    async def get_oncall(self, team: str) -> Optional[OnCallSchedule]:
        """Получение текущего дежурного"""
        for schedule in self.schedules.values():
            if schedule.team == team:
                return schedule
        return None
        
    async def check_sla(self, incident_id: str) -> Dict[str, Any]:
        """Проверка SLA"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return {}
            
        now = datetime.now()
        sla_deadline = incident.sla_deadline
        
        if incident.resolved_at:
            # Incident resolved
            resolution_time = (incident.resolved_at - incident.detected_at).total_seconds() / 60
            sla_target = self.sla_targets.get(incident.severity, 240)
            
            met_sla = resolution_time <= sla_target
            
            return {
                "incident_id": incident_id,
                "severity": incident.severity.value,
                "sla_target_minutes": sla_target,
                "resolution_minutes": resolution_time,
                "met_sla": met_sla,
                "status": "resolved"
            }
        else:
            # Incident ongoing
            elapsed = (now - incident.detected_at).total_seconds() / 60
            remaining = (sla_deadline - now).total_seconds() / 60 if sla_deadline > now else 0
            breached = remaining <= 0
            
            if breached:
                incident.sla_breached = True
                
            return {
                "incident_id": incident_id,
                "severity": incident.severity.value,
                "elapsed_minutes": elapsed,
                "remaining_minutes": max(0, remaining),
                "breached": breached,
                "status": "ongoing"
            }
            
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        open_incidents = sum(1 for i in self.incidents.values() 
                            if i.status not in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED])
        resolved = sum(1 for i in self.incidents.values() if i.status == IncidentStatus.RESOLVED)
        
        sev_counts = {}
        for sev in IncidentSeverity:
            sev_counts[sev.value] = sum(1 for i in self.incidents.values() if i.severity == sev)
            
        sla_met = sum(1 for i in self.incidents.values() 
                     if i.status == IncidentStatus.RESOLVED and not i.sla_breached)
        sla_breached = sum(1 for i in self.incidents.values() if i.sla_breached)
        
        # Calculate MTTR (Mean Time To Resolve)
        resolution_times = []
        for incident in self.incidents.values():
            if incident.resolved_at:
                duration = (incident.resolved_at - incident.detected_at).total_seconds() / 60
                resolution_times.append(duration)
                
        mttr = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        
        return {
            "total_incidents": len(self.incidents),
            "open_incidents": open_incidents,
            "resolved_incidents": resolved,
            "severity_breakdown": sev_counts,
            "sla_met": sla_met,
            "sla_breached": sla_breached,
            "mttr_minutes": mttr,
            "escalations": self.escalations_total,
            "communications_sent": self.communications_sent,
            "postmortems": len(self.postmortems)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 298: Incident Commander Platform")
    print("=" * 60)
    
    manager = IncidentCommanderManager()
    print("✓ Incident Commander Manager created")
    
    # Create on-call schedules
    print("\n📅 Setting Up On-Call Schedules...")
    
    teams = [
        ("Platform Team", "alice@company.com", "bob@company.com"),
        ("Database Team", "charlie@company.com", "dave@company.com"),
        ("Network Team", "eve@company.com", "frank@company.com")
    ]
    
    for team, primary, secondary in teams:
        schedule = await manager.create_oncall_schedule(team, primary, secondary)
        print(f"  📅 {team}: {primary} (backup: {secondary})")
        
    # Create incidents
    print("\n🚨 Creating Incidents...")
    
    incidents_data = [
        ("Production Database Outage", IncidentSeverity.SEV1, IncidentCategory.DATABASE,
         "Primary database cluster is unresponsive", ["api", "web", "mobile"]),
        ("High API Latency", IncidentSeverity.SEV2, IncidentCategory.PERFORMANCE,
         "API response times increased 5x", ["api"]),
        ("Authentication Service Errors", IncidentSeverity.SEV2, IncidentCategory.APPLICATION,
         "Users unable to login intermittently", ["auth", "web"]),
        ("Network Packet Loss", IncidentSeverity.SEV3, IncidentCategory.NETWORK,
         "Increased packet loss in us-east region", ["cdn"]),
        ("Disk Space Warning", IncidentSeverity.SEV4, IncidentCategory.INFRASTRUCTURE,
         "Log server reaching 80% capacity", ["logging"])
    ]
    
    incidents = []
    for title, severity, category, desc, services in incidents_data:
        incident = await manager.create_incident(title, severity, category, desc, services)
        incidents.append(incident)
        
        severity_icons = {
            IncidentSeverity.SEV1: "🔴",
            IncidentSeverity.SEV2: "🟠",
            IncidentSeverity.SEV3: "🟡",
            IncidentSeverity.SEV4: "🟢"
        }
        icon = severity_icons.get(severity, "⚪")
        print(f"\n  {icon} [{incident.incident_id}] {title}")
        print(f"     Severity: {severity.value} | Category: {category.value}")
        print(f"     Affected: {', '.join(services)}")
        
    # Acknowledge incidents
    print("\n✅ Acknowledging Incidents...")
    
    commanders = ["alice@company.com", "bob@company.com", "charlie@company.com"]
    
    for i, incident in enumerate(incidents[:3]):
        await manager.acknowledge_incident(incident.incident_id, commanders[i])
        print(f"  ✅ {incident.incident_id} acknowledged by {commanders[i]}")
        
    # Add responders
    print("\n👥 Adding Responders...")
    
    responders = ["dev1@company.com", "dev2@company.com", "dba1@company.com", "sre1@company.com"]
    
    for incident in incidents[:2]:
        for responder in random.sample(responders, k=random.randint(2, 4)):
            await manager.add_responder(incident.incident_id, responder)
        print(f"  👥 {incident.incident_id}: {len(incident.responders)} responders")
        
    # Escalate SEV1 incident
    print("\n📈 Escalating Incidents...")
    
    sev1_incident = incidents[0]
    await manager.escalate(sev1_incident.incident_id, EscalationLevel.L2, "No progress after 10 minutes")
    await manager.escalate(sev1_incident.incident_id, EscalationLevel.L3, "Root cause not identified")
    await manager.escalate(sev1_incident.incident_id, EscalationLevel.MANAGEMENT, "Customer impact critical")
    
    print(f"  📈 {sev1_incident.incident_id} escalated to {sev1_incident.escalation_level.value}")
    
    # Send communications
    print("\n📧 Sending Communications...")
    
    for incident in incidents[:2]:
        # Initial notification
        await manager.send_communication(
            incident.incident_id,
            "slack",
            f"🚨 {incident.severity.value.upper()}: {incident.title}",
            ["#incidents", "#engineering"]
        )
        
        # Stakeholder update
        await manager.send_communication(
            incident.incident_id,
            "email",
            f"Incident Update: {incident.title} - Investigation in progress",
            ["stakeholders@company.com"]
        )
        
    print(f"  📧 Sent {manager.communications_sent} communications")
    
    # Update incident statuses
    print("\n🔄 Updating Incident Status...")
    
    status_progression = [
        (IncidentStatus.INVESTIGATING, "Team reviewing logs and metrics"),
        (IncidentStatus.IDENTIFIED, "Root cause identified: database connection pool exhausted"),
        (IncidentStatus.MITIGATING, "Applying fix: increasing connection pool size"),
        (IncidentStatus.RESOLVED, "Service restored, monitoring for stability")
    ]
    
    for status, note in status_progression:
        await manager.update_status(incidents[0].incident_id, status, note)
        print(f"  🔄 {incidents[0].incident_id}: {status.value}")
        
    # Resolve more incidents
    for incident in incidents[1:3]:
        await manager.update_status(incident.incident_id, IncidentStatus.INVESTIGATING)
        await manager.update_status(incident.incident_id, IncidentStatus.RESOLVED, "Issue resolved")
        
    # Check SLA
    print("\n⏱️ SLA Status:")
    
    for incident in incidents:
        sla_status = await manager.check_sla(incident.incident_id)
        
        if sla_status.get('status') == 'resolved':
            met = "✅ Met" if sla_status['met_sla'] else "❌ Breached"
            print(f"  {met} {incident.incident_id}: {sla_status['resolution_minutes']:.0f}min (target: {sla_status['sla_target_minutes']}min)")
        else:
            if sla_status.get('breached'):
                print(f"  ⚠️ {incident.incident_id}: SLA BREACHED ({sla_status['elapsed_minutes']:.0f}min elapsed)")
            else:
                print(f"  ⏳ {incident.incident_id}: {sla_status['remaining_minutes']:.0f}min remaining")
                
    # Create post-mortem
    print("\n📝 Creating Post-Mortem...")
    
    pm = await manager.create_postmortem(incidents[0].incident_id)
    
    if pm:
        await manager.update_postmortem(
            pm.postmortem_id,
            root_cause="Database connection pool exhausted due to leaked connections",
            contributing_factors=[
                "Recent deployment without connection pool changes",
                "Monitoring alert threshold too high",
                "Missing connection leak detection"
            ],
            action_items=[
                "Implement connection pool monitoring",
                "Add connection leak detection",
                "Review deployment checklist",
                "Lower alert thresholds"
            ]
        )
        
        print(f"  📝 Post-Mortem created: {pm.postmortem_id}")
        print(f"     Title: {pm.title}")
        print(f"     Root Cause: {pm.root_cause}")
        print(f"     Action Items: {len(pm.action_items)}")
        
    # Incident timeline
    print("\n📋 Incident Timeline (SEV1):")
    
    for entry_id in incidents[0].timeline[:8]:
        entry = manager.timeline_entries.get(entry_id)
        if entry:
            time_str = entry.timestamp.strftime("%H:%M:%S")
            actor = f"[{entry.user}]" if entry.user else "[automated]"
            print(f"  {time_str} {actor} {entry.action}")
            if entry.description:
                print(f"           └── {entry.description}")
                
    # Active incidents dashboard
    print("\n📊 Active Incidents:")
    
    print("\n  ┌──────────────────────┬──────────┬────────────────┬────────────┬──────────┐")
    print("  │ ID                   │ Severity │ Status         │ Commander  │ SLA      │")
    print("  ├──────────────────────┼──────────┼────────────────┼────────────┼──────────┤")
    
    for incident in incidents:
        inc_id = incident.incident_id[:20].ljust(20)
        severity = incident.severity.value.ljust(8)
        status = incident.status.value[:14].ljust(14)
        commander = (incident.commander[:10] if incident.commander else "unassigned").ljust(10)
        
        sla = await manager.check_sla(incident.incident_id)
        if sla.get('status') == 'resolved':
            sla_str = "✅ Met" if sla['met_sla'] else "❌ Miss"
        else:
            sla_str = "⚠️ Risk" if sla.get('remaining_minutes', 999) < 30 else "✅ OK"
        sla_str = sla_str.ljust(8)
        
        print(f"  │ {inc_id} │ {severity} │ {status} │ {commander} │ {sla_str} │")
        
    print("  └──────────────────────┴──────────┴────────────────┴────────────┴──────────┘")
    
    # Statistics
    print("\n📊 Incident Commander Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Total Incidents: {stats['total_incidents']}")
    print(f"  Open Incidents: {stats['open_incidents']}")
    print(f"  Resolved Incidents: {stats['resolved_incidents']}")
    
    print("\n  Severity Breakdown:")
    for sev, count in stats['severity_breakdown'].items():
        bar = "█" * count + "░" * (5 - count)
        print(f"    {sev.upper()}: [{bar}] {count}")
        
    print(f"\n  SLA Performance:")
    print(f"    Met: {stats['sla_met']}")
    print(f"    Breached: {stats['sla_breached']}")
    
    print(f"\n  MTTR: {stats['mttr_minutes']:.1f} minutes")
    print(f"  Escalations: {stats['escalations']}")
    print(f"  Communications: {stats['communications_sent']}")
    
    sla_rate = (stats['sla_met'] / max(stats['resolved_incidents'], 1)) * 100
    resolution_rate = (stats['resolved_incidents'] / max(stats['total_incidents'], 1)) * 100
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Incident Commander Dashboard                     │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Incidents:               {stats['total_incidents']:>12}                        │")
    print(f"│ Open Incidents:                {stats['open_incidents']:>12}                        │")
    print(f"│ Resolved Incidents:            {stats['resolved_incidents']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Resolution Rate:               {resolution_rate:>11.1f}%                        │")
    print(f"│ SLA Compliance Rate:           {sla_rate:>11.1f}%                        │")
    print(f"│ Mean Time To Resolve:          {stats['mttr_minutes']:>10.1f}m                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Incident Commander Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
