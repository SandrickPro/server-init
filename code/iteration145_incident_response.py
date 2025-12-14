#!/usr/bin/env python3
"""
Server Init - Iteration 145: Incident Response Platform
Платформа реагирования на инциденты

Функционал:
- Incident Detection - обнаружение инцидентов
- Alert Management - управление алертами
- Escalation - эскалация
- Runbook Automation - автоматизация рунбуков
- On-Call Management - управление дежурствами
- Post-Mortem - пост-мортемы
- Communication - коммуникация
- Metrics & Analytics - метрики и аналитика
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
import uuid
import random


class IncidentSeverity(Enum):
    """Критичность инцидента"""
    SEV1 = "sev1"  # Critical - Full outage
    SEV2 = "sev2"  # Major - Partial outage
    SEV3 = "sev3"  # Minor - Degraded performance
    SEV4 = "sev4"  # Low - Minor issue
    SEV5 = "sev5"  # Informational


class IncidentStatus(Enum):
    """Статус инцидента"""
    TRIGGERED = "triggered"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"
    CLOSED = "closed"


class AlertStatus(Enum):
    """Статус алерта"""
    FIRING = "firing"
    ACKNOWLEDGED = "acknowledged"
    SILENCED = "silenced"
    RESOLVED = "resolved"


class EscalationLevel(Enum):
    """Уровень эскалации"""
    L1 = "l1"  # First responder
    L2 = "l2"  # Team lead
    L3 = "l3"  # Manager
    L4 = "l4"  # VP/Director
    EXECUTIVE = "executive"


@dataclass
class Alert:
    """Алерт"""
    alert_id: str
    name: str = ""
    
    # Source
    source: str = ""  # prometheus, datadog, etc.
    metric: str = ""
    
    # Status
    status: AlertStatus = AlertStatus.FIRING
    severity: IncidentSeverity = IncidentSeverity.SEV3
    
    # Details
    description: str = ""
    labels: Dict = field(default_factory=dict)
    annotations: Dict = field(default_factory=dict)
    
    # Value
    current_value: float = 0.0
    threshold: float = 0.0
    
    # Timestamps
    fired_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Assignment
    assigned_to: str = ""


@dataclass
class Incident:
    """Инцидент"""
    incident_id: str
    title: str = ""
    
    # Classification
    severity: IncidentSeverity = IncidentSeverity.SEV3
    status: IncidentStatus = IncidentStatus.TRIGGERED
    
    # Impact
    affected_services: List[str] = field(default_factory=list)
    affected_customers: int = 0
    business_impact: str = ""
    
    # Description
    summary: str = ""
    root_cause: str = ""
    
    # Related alerts
    alerts: List[str] = field(default_factory=list)
    
    # Timeline
    timeline: List[Dict] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Responders
    commander: str = ""
    responders: List[str] = field(default_factory=list)
    
    # Communication
    status_page_id: str = ""
    slack_channel: str = ""


@dataclass
class OnCallSchedule:
    """Расписание дежурств"""
    schedule_id: str
    name: str = ""
    
    # Team
    team: str = ""
    members: List[str] = field(default_factory=list)
    
    # Rotation
    rotation_type: str = "weekly"  # daily, weekly, custom
    current_oncall: str = ""
    
    # Escalation
    escalation_timeout_minutes: int = 15
    escalation_chain: List[str] = field(default_factory=list)


@dataclass
class Runbook:
    """Рунбук"""
    runbook_id: str
    name: str = ""
    
    # Target
    alert_type: str = ""
    service: str = ""
    
    # Steps
    steps: List[Dict] = field(default_factory=list)
    
    # Automation
    automated: bool = False
    automation_script: str = ""
    
    # Metrics
    execution_count: int = 0
    avg_resolution_time: float = 0.0


@dataclass
class PostMortem:
    """Пост-мортем"""
    postmortem_id: str
    incident_id: str = ""
    
    # Summary
    title: str = ""
    summary: str = ""
    
    # Timeline
    timeline: List[Dict] = field(default_factory=list)
    
    # Analysis
    root_cause: str = ""
    contributing_factors: List[str] = field(default_factory=list)
    
    # Impact
    duration_minutes: int = 0
    affected_customers: int = 0
    revenue_impact: float = 0.0
    
    # Action items
    action_items: List[Dict] = field(default_factory=list)
    
    # Status
    status: str = "draft"  # draft, review, published
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class StatusUpdate:
    """Обновление статуса"""
    update_id: str
    incident_id: str = ""
    
    # Content
    message: str = ""
    status: IncidentStatus = IncidentStatus.INVESTIGATING
    
    # Visibility
    public: bool = True
    
    # Author
    author: str = ""
    
    # Timestamp
    created_at: datetime = field(default_factory=datetime.now)


class AlertManager:
    """Менеджер алертов"""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.alert_rules: List[Dict] = []
        
    def create_alert(self, name: str, source: str, severity: IncidentSeverity,
                      description: str, **kwargs) -> Alert:
        """Создание алерта"""
        alert = Alert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            name=name,
            source=source,
            severity=severity,
            description=description,
            **kwargs
        )
        self.alerts[alert.alert_id] = alert
        return alert
        
    def acknowledge(self, alert_id: str, user: str) -> Alert:
        """Подтверждение алерта"""
        alert = self.alerts.get(alert_id)
        if alert:
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.now()
            alert.assigned_to = user
        return alert
        
    def resolve(self, alert_id: str) -> Alert:
        """Разрешение алерта"""
        alert = self.alerts.get(alert_id)
        if alert:
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
        return alert
        
    def get_firing_alerts(self) -> List[Alert]:
        """Получение активных алертов"""
        return [a for a in self.alerts.values() if a.status == AlertStatus.FIRING]
        
    def silence_alert(self, alert_id: str, duration_minutes: int = 60) -> Alert:
        """Заглушение алерта"""
        alert = self.alerts.get(alert_id)
        if alert:
            alert.status = AlertStatus.SILENCED
        return alert


class IncidentManager:
    """Менеджер инцидентов"""
    
    def __init__(self, alert_manager: AlertManager):
        self.alert_manager = alert_manager
        self.incidents: Dict[str, Incident] = {}
        
    def create_incident(self, title: str, severity: IncidentSeverity,
                         affected_services: List[str], **kwargs) -> Incident:
        """Создание инцидента"""
        incident = Incident(
            incident_id=f"INC-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}",
            title=title,
            severity=severity,
            affected_services=affected_services,
            **kwargs
        )
        
        # Add creation to timeline
        incident.timeline.append({
            "timestamp": datetime.now().isoformat(),
            "event": "incident_created",
            "details": f"Incident created: {title}"
        })
        
        self.incidents[incident.incident_id] = incident
        return incident
        
    def update_status(self, incident_id: str, status: IncidentStatus,
                       note: str = "") -> Incident:
        """Обновление статуса"""
        incident = self.incidents.get(incident_id)
        if incident:
            incident.status = status
            incident.timeline.append({
                "timestamp": datetime.now().isoformat(),
                "event": f"status_changed_{status.value}",
                "details": note
            })
            
            if status == IncidentStatus.ACKNOWLEDGED:
                incident.acknowledged_at = datetime.now()
            elif status == IncidentStatus.RESOLVED:
                incident.resolved_at = datetime.now()
                
        return incident
        
    def assign_commander(self, incident_id: str, commander: str) -> Incident:
        """Назначение командира инцидента"""
        incident = self.incidents.get(incident_id)
        if incident:
            incident.commander = commander
            incident.timeline.append({
                "timestamp": datetime.now().isoformat(),
                "event": "commander_assigned",
                "details": f"Incident commander: {commander}"
            })
        return incident
        
    def add_responder(self, incident_id: str, responder: str) -> Incident:
        """Добавление респондера"""
        incident = self.incidents.get(incident_id)
        if incident and responder not in incident.responders:
            incident.responders.append(responder)
        return incident
        
    def calculate_mttr(self) -> float:
        """Расчёт MTTR (Mean Time To Resolve)"""
        resolved = [
            i for i in self.incidents.values()
            if i.resolved_at and i.created_at
        ]
        
        if not resolved:
            return 0.0
            
        total_minutes = sum(
            (i.resolved_at - i.created_at).total_seconds() / 60
            for i in resolved
        )
        
        return total_minutes / len(resolved)


class OnCallManager:
    """Менеджер дежурств"""
    
    def __init__(self):
        self.schedules: Dict[str, OnCallSchedule] = {}
        
    def create_schedule(self, name: str, team: str, members: List[str],
                         rotation_type: str = "weekly") -> OnCallSchedule:
        """Создание расписания"""
        schedule = OnCallSchedule(
            schedule_id=f"sched_{uuid.uuid4().hex[:8]}",
            name=name,
            team=team,
            members=members,
            rotation_type=rotation_type,
            current_oncall=members[0] if members else "",
            escalation_chain=members
        )
        self.schedules[schedule.schedule_id] = schedule
        return schedule
        
    def get_current_oncall(self, schedule_id: str) -> str:
        """Получение текущего дежурного"""
        schedule = self.schedules.get(schedule_id)
        return schedule.current_oncall if schedule else ""
        
    def escalate(self, schedule_id: str, current_level: int = 0) -> Optional[str]:
        """Эскалация"""
        schedule = self.schedules.get(schedule_id)
        if not schedule or current_level >= len(schedule.escalation_chain) - 1:
            return None
            
        return schedule.escalation_chain[current_level + 1]
        
    def rotate(self, schedule_id: str):
        """Ротация дежурных"""
        schedule = self.schedules.get(schedule_id)
        if schedule and schedule.members:
            current_idx = schedule.members.index(schedule.current_oncall)
            next_idx = (current_idx + 1) % len(schedule.members)
            schedule.current_oncall = schedule.members[next_idx]


class RunbookEngine:
    """Движок рунбуков"""
    
    def __init__(self):
        self.runbooks: Dict[str, Runbook] = {}
        
    def create_runbook(self, name: str, alert_type: str, steps: List[Dict],
                        automated: bool = False) -> Runbook:
        """Создание рунбука"""
        runbook = Runbook(
            runbook_id=f"rb_{uuid.uuid4().hex[:8]}",
            name=name,
            alert_type=alert_type,
            steps=steps,
            automated=automated
        )
        self.runbooks[runbook.runbook_id] = runbook
        return runbook
        
    async def execute(self, runbook_id: str) -> Dict:
        """Выполнение рунбука"""
        runbook = self.runbooks.get(runbook_id)
        if not runbook:
            return {"success": False, "error": "Runbook not found"}
            
        results = []
        start_time = datetime.now()
        
        for i, step in enumerate(runbook.steps, 1):
            # Simulate step execution
            await asyncio.sleep(0.1)
            success = random.random() > 0.1  # 90% success rate
            
            results.append({
                "step": i,
                "name": step.get("name", f"Step {i}"),
                "success": success,
                "output": step.get("expected_output", "Completed")
            })
            
            if not success and not step.get("continue_on_failure", False):
                break
                
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        runbook.execution_count += 1
        runbook.avg_resolution_time = (
            (runbook.avg_resolution_time * (runbook.execution_count - 1) + duration) /
            runbook.execution_count
        )
        
        return {
            "success": all(r["success"] for r in results),
            "steps_executed": len(results),
            "duration_seconds": duration,
            "results": results
        }
        
    def get_runbook_for_alert(self, alert_type: str) -> Optional[Runbook]:
        """Получение рунбука для типа алерта"""
        for runbook in self.runbooks.values():
            if runbook.alert_type == alert_type:
                return runbook
        return None


class PostMortemManager:
    """Менеджер пост-мортемов"""
    
    def __init__(self, incident_manager: IncidentManager):
        self.incident_manager = incident_manager
        self.postmortems: Dict[str, PostMortem] = {}
        
    def create(self, incident_id: str) -> PostMortem:
        """Создание пост-мортема"""
        incident = self.incident_manager.incidents.get(incident_id)
        if not incident:
            return None
            
        duration = 0
        if incident.resolved_at and incident.created_at:
            duration = int((incident.resolved_at - incident.created_at).total_seconds() / 60)
            
        postmortem = PostMortem(
            postmortem_id=f"pm_{uuid.uuid4().hex[:8]}",
            incident_id=incident_id,
            title=f"Post-Mortem: {incident.title}",
            timeline=incident.timeline.copy(),
            duration_minutes=duration,
            affected_customers=incident.affected_customers
        )
        self.postmortems[postmortem.postmortem_id] = postmortem
        return postmortem
        
    def add_root_cause(self, postmortem_id: str, root_cause: str,
                        contributing_factors: List[str] = None):
        """Добавление корневой причины"""
        pm = self.postmortems.get(postmortem_id)
        if pm:
            pm.root_cause = root_cause
            pm.contributing_factors = contributing_factors or []
            
    def add_action_item(self, postmortem_id: str, action: str,
                         owner: str, due_date: datetime = None):
        """Добавление action item"""
        pm = self.postmortems.get(postmortem_id)
        if pm:
            pm.action_items.append({
                "action": action,
                "owner": owner,
                "due_date": due_date.isoformat() if due_date else None,
                "status": "open"
            })
            
    def publish(self, postmortem_id: str) -> PostMortem:
        """Публикация пост-мортема"""
        pm = self.postmortems.get(postmortem_id)
        if pm:
            pm.status = "published"
        return pm


class CommunicationHub:
    """Хаб коммуникаций"""
    
    def __init__(self):
        self.status_updates: List[StatusUpdate] = []
        self.channels: Dict[str, str] = {}
        
    def post_update(self, incident_id: str, message: str,
                     status: IncidentStatus, author: str,
                     public: bool = True) -> StatusUpdate:
        """Публикация обновления"""
        update = StatusUpdate(
            update_id=f"upd_{uuid.uuid4().hex[:8]}",
            incident_id=incident_id,
            message=message,
            status=status,
            author=author,
            public=public
        )
        self.status_updates.append(update)
        return update
        
    def get_updates_for_incident(self, incident_id: str) -> List[StatusUpdate]:
        """Получение обновлений для инцидента"""
        return [u for u in self.status_updates if u.incident_id == incident_id]
        
    def create_channel(self, incident_id: str, channel_type: str = "slack") -> str:
        """Создание канала"""
        channel_name = f"inc-{incident_id[-8:].lower()}"
        self.channels[incident_id] = channel_name
        return channel_name


class IncidentResponsePlatform:
    """Платформа реагирования на инциденты"""
    
    def __init__(self):
        self.alert_manager = AlertManager()
        self.incident_manager = IncidentManager(self.alert_manager)
        self.oncall_manager = OnCallManager()
        self.runbook_engine = RunbookEngine()
        self.postmortem_manager = PostMortemManager(self.incident_manager)
        self.communication_hub = CommunicationHub()
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        incidents = list(self.incident_manager.incidents.values())
        
        return {
            "total_alerts": len(self.alert_manager.alerts),
            "firing_alerts": len(self.alert_manager.get_firing_alerts()),
            "total_incidents": len(incidents),
            "open_incidents": len([i for i in incidents if i.status != IncidentStatus.CLOSED]),
            "mttr_minutes": self.incident_manager.calculate_mttr(),
            "oncall_schedules": len(self.oncall_manager.schedules),
            "runbooks": len(self.runbook_engine.runbooks),
            "postmortems": len(self.postmortem_manager.postmortems)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 145: Incident Response Platform")
    print("=" * 60)
    
    async def demo():
        platform = IncidentResponsePlatform()
        print("✓ Incident Response Platform created")
        
        # Create on-call schedules
        print("\n📅 Setting Up On-Call Schedules...")
        
        schedules = [
            ("Platform Team", "platform", ["alice", "bob", "charlie"]),
            ("Database Team", "database", ["dave", "eve"]),
            ("Network Team", "network", ["frank", "grace", "henry"])
        ]
        
        for name, team, members in schedules:
            schedule = platform.oncall_manager.create_schedule(name, team, members)
            print(f"  ✓ {name}: Current on-call: {schedule.current_oncall}")
            
        # Create runbooks
        print("\n📋 Creating Runbooks...")
        
        runbooks_data = [
            ("High CPU Runbook", "high_cpu", [
                {"name": "Check process list", "command": "top -bn1"},
                {"name": "Check resource hogs", "command": "ps aux --sort=-%cpu"},
                {"name": "Scale if needed", "command": "kubectl scale deployment"}
            ]),
            ("Database Connection Runbook", "db_connection", [
                {"name": "Check connection pool", "command": "show processlist"},
                {"name": "Kill idle connections", "command": "kill idle"},
                {"name": "Restart connection pooler", "command": "systemctl restart pgbouncer"}
            ]),
            ("Memory Leak Runbook", "memory_leak", [
                {"name": "Check memory usage", "command": "free -h"},
                {"name": "Identify leaking process", "command": "top -o %MEM"},
                {"name": "Trigger GC or restart", "command": "kill -SIGUSR1"}
            ])
        ]
        
        for name, alert_type, steps in runbooks_data:
            runbook = platform.runbook_engine.create_runbook(name, alert_type, steps, automated=True)
            print(f"  ✓ {name}: {len(steps)} steps")
            
        # Simulate alerts
        print("\n🚨 Simulating Alerts...")
        
        alerts_data = [
            ("High CPU Usage", "prometheus", IncidentSeverity.SEV2, "CPU usage above 90%"),
            ("Database Connection Pool Exhausted", "datadog", IncidentSeverity.SEV1, "No available connections"),
            ("Increased Error Rate", "prometheus", IncidentSeverity.SEV3, "Error rate > 5%"),
            ("Memory Usage Critical", "cloudwatch", IncidentSeverity.SEV2, "Memory > 95%")
        ]
        
        alerts = []
        for name, source, severity, desc in alerts_data:
            alert = platform.alert_manager.create_alert(name, source, severity, desc)
            alerts.append(alert)
            severity_icon = {"sev1": "🔴", "sev2": "🟠", "sev3": "🟡", "sev4": "🟢", "sev5": "🔵"}
            print(f"  {severity_icon[severity.value]} {name}: {desc}")
            
        # Create incident from alert
        print("\n🔥 Creating Incident...")
        
        incident = platform.incident_manager.create_incident(
            "Production Database Outage",
            IncidentSeverity.SEV1,
            affected_services=["api", "web", "mobile"],
            affected_customers=50000,
            summary="Database connection pool exhausted causing service disruption"
        )
        
        print(f"\n  Incident: {incident.incident_id}")
        print(f"  Title: {incident.title}")
        print(f"  Severity: {incident.severity.value}")
        print(f"  Affected Services: {', '.join(incident.affected_services)}")
        print(f"  Affected Customers: {incident.affected_customers:,}")
        
        # Create communication channel
        channel = platform.communication_hub.create_channel(incident.incident_id)
        incident.slack_channel = channel
        print(f"  Slack Channel: #{channel}")
        
        # Assign commander
        platform.incident_manager.assign_commander(incident.incident_id, "alice")
        platform.incident_manager.add_responder(incident.incident_id, "bob")
        platform.incident_manager.add_responder(incident.incident_id, "dave")
        
        print(f"\n  Commander: {incident.commander}")
        print(f"  Responders: {', '.join(incident.responders)}")
        
        # Incident progression
        print("\n📈 Incident Progression...")
        
        statuses = [
            (IncidentStatus.ACKNOWLEDGED, "Incident acknowledged by on-call"),
            (IncidentStatus.INVESTIGATING, "Investigating database connections"),
            (IncidentStatus.IDENTIFIED, "Root cause: Connection pool leak in API v2.5"),
            (IncidentStatus.MITIGATING, "Rolling back to API v2.4"),
            (IncidentStatus.RESOLVED, "Service restored, connections normalized")
        ]
        
        for status, note in statuses:
            platform.incident_manager.update_status(incident.incident_id, status, note)
            platform.communication_hub.post_update(
                incident.incident_id, note, status, "alice"
            )
            await asyncio.sleep(0.1)
            print(f"  [{status.value:15}] {note}")
            
        # Execute runbook
        print("\n🔧 Executing Runbook...")
        
        runbook = platform.runbook_engine.get_runbook_for_alert("db_connection")
        if runbook:
            result = await platform.runbook_engine.execute(runbook.runbook_id)
            print(f"  Runbook: {runbook.name}")
            print(f"  Success: {result['success']}")
            print(f"  Steps Executed: {result['steps_executed']}")
            print(f"  Duration: {result['duration_seconds']:.2f}s")
            
        # Create post-mortem
        print("\n📝 Creating Post-Mortem...")
        
        postmortem = platform.postmortem_manager.create(incident.incident_id)
        
        platform.postmortem_manager.add_root_cause(
            postmortem.postmortem_id,
            "Connection pool leak introduced in API v2.5 release",
            [
                "Insufficient testing of connection handling",
                "No connection pool monitoring alerts",
                "Missing circuit breaker for DB connections"
            ]
        )
        
        action_items = [
            ("Add connection pool monitoring", "bob", 7),
            ("Implement circuit breaker", "charlie", 14),
            ("Update deployment checklist", "alice", 3),
            ("Conduct load testing", "dave", 21)
        ]
        
        for action, owner, days in action_items:
            platform.postmortem_manager.add_action_item(
                postmortem.postmortem_id,
                action, owner,
                datetime.now() + timedelta(days=days)
            )
            
        platform.postmortem_manager.publish(postmortem.postmortem_id)
        
        print(f"\n  Post-Mortem: {postmortem.postmortem_id}")
        print(f"  Duration: {postmortem.duration_minutes} minutes")
        print(f"  Root Cause: {postmortem.root_cause}")
        print(f"  Action Items: {len(postmortem.action_items)}")
        
        # Show timeline
        print("\n⏱️ Incident Timeline:")
        
        for event in incident.timeline[-5:]:
            print(f"  • {event['event']}: {event['details']}")
            
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Alerts: {stats['total_alerts']}")
        print(f"  Firing Alerts: {stats['firing_alerts']}")
        print(f"  Total Incidents: {stats['total_incidents']}")
        print(f"  Open Incidents: {stats['open_incidents']}")
        print(f"  MTTR: {stats['mttr_minutes']:.1f} minutes")
        print(f"  On-Call Schedules: {stats['oncall_schedules']}")
        print(f"  Runbooks: {stats['runbooks']}")
        print(f"  Post-Mortems: {stats['postmortems']}")
        
        # Dashboard
        print("\n📋 Incident Response Dashboard:")
        print("  ┌────────────────────────────────────────────────────────────┐")
        print("  │                Incident Response Overview                  │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Alerts:        {stats['total_alerts']:>10}                    │")
        print(f"  │ Firing Alerts:       {stats['firing_alerts']:>10}                    │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Incidents:     {stats['total_incidents']:>10}                    │")
        print(f"  │ Open Incidents:      {stats['open_incidents']:>10}                    │")
        print(f"  │ MTTR (minutes):      {stats['mttr_minutes']:>10.1f}                    │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ On-Call Schedules:   {stats['oncall_schedules']:>10}                    │")
        print(f"  │ Runbooks:            {stats['runbooks']:>10}                    │")
        print(f"  │ Post-Mortems:        {stats['postmortems']:>10}                    │")
        print("  └────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Incident Response Platform initialized!")
    print("=" * 60)
