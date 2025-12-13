#!/usr/bin/env python3
"""
Server Init - Iteration 104: Incident Management Platform
Платформа управления инцидентами

Функционал:
- Incident Detection - обнаружение инцидентов
- Alert Management - управление алертами
- On-Call Scheduling - расписание дежурств
- Escalation Policies - политики эскалации
- Incident Response - реагирование
- Post-Mortem Analysis - анализ постмортемов
- Runbook Integration - интеграция ранбуков
- Metrics & Analytics - метрики
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
from collections import defaultdict
import uuid
import random


class IncidentSeverity(Enum):
    """Критичность инцидента"""
    SEV1 = "sev1"  # Critical - service down
    SEV2 = "sev2"  # Major - significant degradation
    SEV3 = "sev3"  # Minor - partial degradation
    SEV4 = "sev4"  # Low - cosmetic issues
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


class EscalationAction(Enum):
    """Действие эскалации"""
    NOTIFY = "notify"
    PAGE = "page"
    CALL = "call"
    ESCALATE = "escalate"


@dataclass
class Alert:
    """Алерт"""
    alert_id: str
    
    # Source
    source: str = ""
    alert_name: str = ""
    
    # Details
    message: str = ""
    severity: IncidentSeverity = IncidentSeverity.SEV3
    
    # Labels & Annotations
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    
    # Status
    status: AlertStatus = AlertStatus.FIRING
    
    # Timestamps
    started_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Assignment
    assigned_to: Optional[str] = None


@dataclass
class Responder:
    """Дежурный"""
    responder_id: str
    name: str = ""
    email: str = ""
    phone: str = ""
    
    # Contact methods
    contact_methods: List[str] = field(default_factory=lambda: ["email", "sms", "push"])
    
    # Availability
    available: bool = True
    
    # Teams
    teams: List[str] = field(default_factory=list)


@dataclass
class OnCallSchedule:
    """Расписание дежурств"""
    schedule_id: str
    name: str = ""
    
    # Team
    team: str = ""
    
    # Schedule
    rotation_type: str = "weekly"  # daily, weekly, custom
    start_date: datetime = field(default_factory=datetime.now)
    
    # Responders
    responders: List[str] = field(default_factory=list)  # responder_ids
    current_on_call: Optional[str] = None
    
    # Settings
    handoff_time: str = "09:00"
    timezone: str = "UTC"


@dataclass
class EscalationPolicy:
    """Политика эскалации"""
    policy_id: str
    name: str = ""
    
    # Levels
    levels: List[Dict[str, Any]] = field(default_factory=list)
    # Each level: { "delay_minutes": int, "targets": List[str], "action": EscalationAction }
    
    # Settings
    repeat_enabled: bool = True
    repeat_after_minutes: int = 30


@dataclass
class Incident:
    """Инцидент"""
    incident_id: str
    
    # Basic info
    title: str = ""
    description: str = ""
    severity: IncidentSeverity = IncidentSeverity.SEV3
    status: IncidentStatus = IncidentStatus.TRIGGERED
    
    # Assignment
    commander: Optional[str] = None
    responders: List[str] = field(default_factory=list)
    
    # Related
    related_alerts: List[str] = field(default_factory=list)
    affected_services: List[str] = field(default_factory=list)
    
    # Timeline
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Metrics
    time_to_acknowledge: Optional[float] = None  # seconds
    time_to_resolve: Optional[float] = None  # seconds
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class PostMortem:
    """Постмортем"""
    postmortem_id: str
    incident_id: str
    
    # Summary
    title: str = ""
    summary: str = ""
    
    # Analysis
    impact: str = ""
    root_cause: str = ""
    contributing_factors: List[str] = field(default_factory=list)
    
    # Timeline
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    
    # Action items
    action_items: List[Dict[str, Any]] = field(default_factory=list)
    
    # Lessons learned
    lessons_learned: List[str] = field(default_factory=list)
    
    # Status
    status: str = "draft"  # draft, in_review, published
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    published_at: Optional[datetime] = None


class AlertManager:
    """Менеджер алертов"""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.silence_rules: List[Dict[str, Any]] = []
        
    def create_alert(self, source: str, alert_name: str,
                      message: str, severity: IncidentSeverity,
                      labels: Dict[str, str] = None) -> Alert:
        """Создание алерта"""
        # Check silence rules
        if self._is_silenced(labels or {}):
            return None
            
        alert = Alert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            source=source,
            alert_name=alert_name,
            message=message,
            severity=severity,
            labels=labels or {}
        )
        self.alerts[alert.alert_id] = alert
        return alert
        
    def acknowledge_alert(self, alert_id: str, responder: str) -> bool:
        """Подтверждение алерта"""
        alert = self.alerts.get(alert_id)
        if alert and alert.status == AlertStatus.FIRING:
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.now()
            alert.assigned_to = responder
            return True
        return False
        
    def resolve_alert(self, alert_id: str) -> bool:
        """Разрешение алерта"""
        alert = self.alerts.get(alert_id)
        if alert and alert.status != AlertStatus.RESOLVED:
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            return True
        return False
        
    def add_silence(self, labels: Dict[str, str],
                     duration_minutes: int) -> str:
        """Добавление правила тишины"""
        silence_id = f"silence_{uuid.uuid4().hex[:8]}"
        self.silence_rules.append({
            "silence_id": silence_id,
            "labels": labels,
            "expires_at": datetime.now() + timedelta(minutes=duration_minutes)
        })
        return silence_id
        
    def _is_silenced(self, labels: Dict[str, str]) -> bool:
        """Проверка тишины"""
        now = datetime.now()
        for rule in self.silence_rules:
            if rule["expires_at"] > now:
                if all(labels.get(k) == v for k, v in rule["labels"].items()):
                    return True
        return False
        
    def get_firing_alerts(self) -> List[Alert]:
        """Активные алерты"""
        return [a for a in self.alerts.values() if a.status == AlertStatus.FIRING]


class OnCallManager:
    """Менеджер дежурств"""
    
    def __init__(self):
        self.schedules: Dict[str, OnCallSchedule] = {}
        self.responders: Dict[str, Responder] = {}
        
    def add_responder(self, name: str, email: str,
                       phone: str = "", teams: List[str] = None) -> Responder:
        """Добавление дежурного"""
        responder = Responder(
            responder_id=f"resp_{uuid.uuid4().hex[:8]}",
            name=name,
            email=email,
            phone=phone,
            teams=teams or []
        )
        self.responders[responder.responder_id] = responder
        return responder
        
    def create_schedule(self, name: str, team: str,
                         responders: List[str],
                         rotation_type: str = "weekly") -> OnCallSchedule:
        """Создание расписания"""
        schedule = OnCallSchedule(
            schedule_id=f"sched_{uuid.uuid4().hex[:8]}",
            name=name,
            team=team,
            rotation_type=rotation_type,
            responders=responders
        )
        
        if responders:
            schedule.current_on_call = responders[0]
            
        self.schedules[schedule.schedule_id] = schedule
        return schedule
        
    def get_current_on_call(self, schedule_id: str) -> Optional[Responder]:
        """Текущий дежурный"""
        schedule = self.schedules.get(schedule_id)
        if schedule and schedule.current_on_call:
            return self.responders.get(schedule.current_on_call)
        return None
        
    def rotate(self, schedule_id: str) -> Optional[str]:
        """Ротация"""
        schedule = self.schedules.get(schedule_id)
        if not schedule or not schedule.responders:
            return None
            
        current_idx = 0
        if schedule.current_on_call in schedule.responders:
            current_idx = schedule.responders.index(schedule.current_on_call)
            
        next_idx = (current_idx + 1) % len(schedule.responders)
        schedule.current_on_call = schedule.responders[next_idx]
        
        return schedule.current_on_call


class EscalationManager:
    """Менеджер эскалации"""
    
    def __init__(self, oncall_manager: OnCallManager):
        self.policies: Dict[str, EscalationPolicy] = {}
        self.oncall_manager = oncall_manager
        self.escalation_history: List[Dict[str, Any]] = []
        
    def create_policy(self, name: str,
                       levels: List[Dict[str, Any]]) -> EscalationPolicy:
        """Создание политики"""
        policy = EscalationPolicy(
            policy_id=f"pol_{uuid.uuid4().hex[:8]}",
            name=name,
            levels=levels
        )
        self.policies[policy.policy_id] = policy
        return policy
        
    def escalate(self, incident_id: str, policy_id: str,
                  current_level: int = 0) -> Dict[str, Any]:
        """Эскалация"""
        policy = self.policies.get(policy_id)
        if not policy or current_level >= len(policy.levels):
            return {"status": "no_more_levels"}
            
        level = policy.levels[current_level]
        targets = level.get("targets", [])
        action = level.get("action", EscalationAction.NOTIFY)
        
        notified = []
        for target in targets:
            if target.startswith("schedule:"):
                schedule_id = target.replace("schedule:", "")
                responder = self.oncall_manager.get_current_on_call(schedule_id)
                if responder:
                    notified.append(responder.name)
            else:
                responder = self.oncall_manager.responders.get(target)
                if responder:
                    notified.append(responder.name)
                    
        result = {
            "incident_id": incident_id,
            "level": current_level,
            "action": action.value if isinstance(action, EscalationAction) else action,
            "notified": notified,
            "next_escalation_minutes": level.get("delay_minutes", 10)
        }
        
        self.escalation_history.append({
            **result,
            "timestamp": datetime.now().isoformat()
        })
        
        return result


class IncidentManager:
    """Менеджер инцидентов"""
    
    def __init__(self):
        self.incidents: Dict[str, Incident] = {}
        
    def create_incident(self, title: str, severity: IncidentSeverity,
                         description: str = "",
                         related_alerts: List[str] = None) -> Incident:
        """Создание инцидента"""
        incident = Incident(
            incident_id=f"inc_{uuid.uuid4().hex[:8]}",
            title=title,
            description=description,
            severity=severity,
            related_alerts=related_alerts or []
        )
        
        # Add timeline entry
        incident.timeline.append({
            "event": "incident_created",
            "timestamp": datetime.now().isoformat(),
            "details": f"Incident created with severity {severity.value}"
        })
        
        self.incidents[incident.incident_id] = incident
        return incident
        
    def acknowledge(self, incident_id: str, responder: str) -> bool:
        """Подтверждение"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return False
            
        if incident.status == IncidentStatus.TRIGGERED:
            incident.status = IncidentStatus.ACKNOWLEDGED
            incident.acknowledged_at = datetime.now()
            incident.time_to_acknowledge = (
                incident.acknowledged_at - incident.created_at
            ).total_seconds()
            
            incident.responders.append(responder)
            incident.timeline.append({
                "event": "acknowledged",
                "timestamp": datetime.now().isoformat(),
                "by": responder
            })
            return True
        return False
        
    def update_status(self, incident_id: str, status: IncidentStatus,
                       message: str = "", by: str = "") -> bool:
        """Обновление статуса"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return False
            
        old_status = incident.status
        incident.status = status
        
        incident.timeline.append({
            "event": "status_changed",
            "timestamp": datetime.now().isoformat(),
            "from": old_status.value,
            "to": status.value,
            "message": message,
            "by": by
        })
        
        if status == IncidentStatus.RESOLVED:
            incident.resolved_at = datetime.now()
            incident.time_to_resolve = (
                incident.resolved_at - incident.created_at
            ).total_seconds()
            
        return True
        
    def add_commander(self, incident_id: str, commander: str) -> bool:
        """Назначение командира"""
        incident = self.incidents.get(incident_id)
        if incident:
            incident.commander = commander
            incident.timeline.append({
                "event": "commander_assigned",
                "timestamp": datetime.now().isoformat(),
                "commander": commander
            })
            return True
        return False
        
    def get_active_incidents(self) -> List[Incident]:
        """Активные инциденты"""
        return [
            i for i in self.incidents.values()
            if i.status not in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]
        ]


class PostMortemManager:
    """Менеджер постмортемов"""
    
    def __init__(self):
        self.postmortems: Dict[str, PostMortem] = {}
        
    def create(self, incident: Incident) -> PostMortem:
        """Создание постмортема"""
        pm = PostMortem(
            postmortem_id=f"pm_{uuid.uuid4().hex[:8]}",
            incident_id=incident.incident_id,
            title=f"Post-Mortem: {incident.title}",
            timeline=incident.timeline.copy()
        )
        self.postmortems[pm.postmortem_id] = pm
        return pm
        
    def add_root_cause(self, pm_id: str, root_cause: str) -> bool:
        """Добавление root cause"""
        pm = self.postmortems.get(pm_id)
        if pm:
            pm.root_cause = root_cause
            return True
        return False
        
    def add_action_item(self, pm_id: str, title: str,
                         owner: str, priority: str = "medium") -> bool:
        """Добавление action item"""
        pm = self.postmortems.get(pm_id)
        if pm:
            pm.action_items.append({
                "title": title,
                "owner": owner,
                "priority": priority,
                "status": "open",
                "created_at": datetime.now().isoformat()
            })
            return True
        return False
        
    def publish(self, pm_id: str) -> bool:
        """Публикация"""
        pm = self.postmortems.get(pm_id)
        if pm and pm.status == "draft":
            pm.status = "published"
            pm.published_at = datetime.now()
            return True
        return False


class IncidentManagementPlatform:
    """Платформа управления инцидентами"""
    
    def __init__(self):
        self.alert_manager = AlertManager()
        self.oncall_manager = OnCallManager()
        self.escalation_manager = EscalationManager(self.oncall_manager)
        self.incident_manager = IncidentManager()
        self.postmortem_manager = PostMortemManager()
        
    def process_alert(self, source: str, alert_name: str,
                       message: str, severity: IncidentSeverity,
                       labels: Dict[str, str] = None,
                       auto_create_incident: bool = True) -> Dict[str, Any]:
        """Обработка алерта"""
        # Create alert
        alert = self.alert_manager.create_alert(
            source, alert_name, message, severity, labels
        )
        
        if not alert:
            return {"status": "silenced"}
            
        result = {
            "alert_id": alert.alert_id,
            "alert_name": alert_name,
            "severity": severity.value
        }
        
        # Auto-create incident for high severity
        if auto_create_incident and severity in [IncidentSeverity.SEV1, IncidentSeverity.SEV2]:
            incident = self.incident_manager.create_incident(
                title=f"[{severity.value.upper()}] {alert_name}",
                severity=severity,
                description=message,
                related_alerts=[alert.alert_id]
            )
            result["incident_id"] = incident.incident_id
            
        return result
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        incidents = list(self.incident_manager.incidents.values())
        
        # Calculate MTTR
        resolved_incidents = [i for i in incidents if i.time_to_resolve]
        avg_ttr = (
            sum(i.time_to_resolve for i in resolved_incidents) / len(resolved_incidents)
            if resolved_incidents else 0
        )
        
        # Calculate MTTA
        acked_incidents = [i for i in incidents if i.time_to_acknowledge]
        avg_tta = (
            sum(i.time_to_acknowledge for i in acked_incidents) / len(acked_incidents)
            if acked_incidents else 0
        )
        
        return {
            "total_alerts": len(self.alert_manager.alerts),
            "firing_alerts": len(self.alert_manager.get_firing_alerts()),
            "total_incidents": len(incidents),
            "active_incidents": len(self.incident_manager.get_active_incidents()),
            "responders": len(self.oncall_manager.responders),
            "schedules": len(self.oncall_manager.schedules),
            "policies": len(self.escalation_manager.policies),
            "postmortems": len(self.postmortem_manager.postmortems),
            "mttr_seconds": avg_ttr,
            "mtta_seconds": avg_tta
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 104: Incident Management Platform")
    print("=" * 60)
    
    async def demo():
        platform = IncidentManagementPlatform()
        print("✓ Incident Management Platform created")
        
        # Setup responders
        print("\n👥 Setting up Responders...")
        
        responders = []
        team_members = [
            ("Alice Smith", "alice@company.com", "+1-555-0101", ["platform", "oncall"]),
            ("Bob Johnson", "bob@company.com", "+1-555-0102", ["platform", "oncall"]),
            ("Carol Williams", "carol@company.com", "+1-555-0103", ["platform"]),
            ("David Brown", "david@company.com", "+1-555-0104", ["database"]),
            ("Eva Davis", "eva@company.com", "+1-555-0105", ["database", "oncall"])
        ]
        
        for name, email, phone, teams in team_members:
            resp = platform.oncall_manager.add_responder(name, email, phone, teams)
            responders.append(resp)
            print(f"  ✓ {name} ({', '.join(teams)})")
            
        # Create on-call schedules
        print("\n📅 Creating On-Call Schedules...")
        
        oncall_ids = [r.responder_id for r in responders if "oncall" in r.teams]
        
        schedule1 = platform.oncall_manager.create_schedule(
            "Platform Primary",
            "platform",
            oncall_ids,
            "weekly"
        )
        print(f"  ✓ {schedule1.name}: {len(schedule1.responders)} responders")
        
        schedule2 = platform.oncall_manager.create_schedule(
            "Database Primary",
            "database",
            [r.responder_id for r in responders if "database" in r.teams],
            "weekly"
        )
        print(f"  ✓ {schedule2.name}: {len(schedule2.responders)} responders")
        
        # Show current on-call
        current = platform.oncall_manager.get_current_on_call(schedule1.schedule_id)
        if current:
            print(f"\n  📞 Current on-call (Platform): {current.name}")
            
        # Create escalation policies
        print("\n📈 Creating Escalation Policies...")
        
        policy1 = platform.escalation_manager.create_policy(
            "Platform Critical",
            levels=[
                {
                    "delay_minutes": 0,
                    "targets": [f"schedule:{schedule1.schedule_id}"],
                    "action": EscalationAction.PAGE
                },
                {
                    "delay_minutes": 15,
                    "targets": [responders[2].responder_id],
                    "action": EscalationAction.PAGE
                },
                {
                    "delay_minutes": 30,
                    "targets": [r.responder_id for r in responders[:3]],
                    "action": EscalationAction.CALL
                }
            ]
        )
        print(f"  ✓ {policy1.name}: {len(policy1.levels)} levels")
        
        # Process alerts
        print("\n🚨 Processing Alerts...")
        
        alerts_data = [
            ("prometheus", "HighCPUUsage", "CPU usage above 90% on web-server-1", IncidentSeverity.SEV3, {"service": "web", "env": "prod"}),
            ("prometheus", "DatabaseConnectionsHigh", "DB connections at 95%", IncidentSeverity.SEV2, {"service": "database", "env": "prod"}),
            ("cloudwatch", "APILatencyHigh", "P99 latency > 5s", IncidentSeverity.SEV2, {"service": "api", "env": "prod"}),
            ("pagerduty", "ServiceDown", "Payment service unreachable", IncidentSeverity.SEV1, {"service": "payments", "env": "prod"}),
            ("datadog", "MemoryLeak", "Memory growing in worker-3", IncidentSeverity.SEV3, {"service": "worker", "env": "prod"})
        ]
        
        for source, name, message, severity, labels in alerts_data:
            result = platform.process_alert(source, name, message, severity, labels)
            
            severity_icon = {"sev1": "🔴", "sev2": "🟠", "sev3": "🟡", "sev4": "🔵", "sev5": "⚪"}.get(severity.value, "⚪")
            print(f"  {severity_icon} [{severity.value.upper()}] {name}")
            
            if "incident_id" in result:
                print(f"     → Auto-created incident: {result['incident_id']}")
                
        # Silence a rule
        print("\n🔇 Adding Silence Rule...")
        
        silence_id = platform.alert_manager.add_silence(
            {"service": "staging"},
            duration_minutes=60
        )
        print(f"  ✓ Silenced staging alerts for 60 minutes")
        
        # Manage an incident
        print("\n🔧 Managing Incident...")
        
        active_incidents = platform.incident_manager.get_active_incidents()
        if active_incidents:
            incident = active_incidents[0]
            print(f"\n  Incident: {incident.title}")
            print(f"  Severity: {incident.severity.value}")
            print(f"  Status: {incident.status.value}")
            
            # Escalate
            print("\n  Triggering escalation...")
            esc_result = platform.escalation_manager.escalate(
                incident.incident_id,
                policy1.policy_id,
                0
            )
            print(f"    ✓ Level 0: Notified {', '.join(esc_result['notified'])}")
            print(f"    → Next escalation in {esc_result['next_escalation_minutes']} minutes")
            
            # Acknowledge
            print("\n  Acknowledging incident...")
            platform.incident_manager.acknowledge(
                incident.incident_id,
                responders[0].name
            )
            print(f"    ✓ Acknowledged by {responders[0].name}")
            
            # Assign commander
            platform.incident_manager.add_commander(
                incident.incident_id,
                responders[0].name
            )
            print(f"    ✓ Commander: {responders[0].name}")
            
            # Update status
            platform.incident_manager.update_status(
                incident.incident_id,
                IncidentStatus.INVESTIGATING,
                "Analyzing logs and metrics",
                responders[0].name
            )
            print(f"    ✓ Status: investigating")
            
            platform.incident_manager.update_status(
                incident.incident_id,
                IncidentStatus.IDENTIFIED,
                "Root cause: database connection pool exhaustion",
                responders[0].name
            )
            print(f"    ✓ Status: identified")
            
            platform.incident_manager.update_status(
                incident.incident_id,
                IncidentStatus.RESOLVED,
                "Increased connection pool size and restarted service",
                responders[0].name
            )
            print(f"    ✓ Status: resolved")
            
            # Timeline
            print("\n  📜 Incident Timeline:")
            for entry in incident.timeline[-5:]:
                print(f"    • {entry['event']}: {entry.get('message', '')[:50]}")
                
            # Metrics
            print(f"\n  ⏱️ Metrics:")
            print(f"    Time to Acknowledge: {incident.time_to_acknowledge:.1f}s")
            print(f"    Time to Resolve: {incident.time_to_resolve:.1f}s")
            
            # Create post-mortem
            print("\n📝 Creating Post-Mortem...")
            
            pm = platform.postmortem_manager.create(incident)
            
            platform.postmortem_manager.add_root_cause(
                pm.postmortem_id,
                "Database connection pool was undersized for traffic surge"
            )
            
            platform.postmortem_manager.add_action_item(
                pm.postmortem_id,
                "Increase default connection pool size",
                responders[3].name,
                "high"
            )
            
            platform.postmortem_manager.add_action_item(
                pm.postmortem_id,
                "Add monitoring for connection pool utilization",
                responders[0].name,
                "medium"
            )
            
            platform.postmortem_manager.add_action_item(
                pm.postmortem_id,
                "Document connection pool sizing guidelines",
                responders[2].name,
                "low"
            )
            
            pm.impact = "5 minutes of degraded service for payment processing"
            pm.lessons_learned = [
                "Connection pool sizing should be based on load testing",
                "Need better alerting on resource exhaustion",
                "Runbook for database issues needs updating"
            ]
            
            platform.postmortem_manager.publish(pm.postmortem_id)
            
            print(f"  ✓ Post-mortem created and published")
            print(f"  ✓ Root cause: {pm.root_cause[:50]}...")
            print(f"  ✓ Action items: {len(pm.action_items)}")
            print(f"  ✓ Lessons learned: {len(pm.lessons_learned)}")
            
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Alerts:")
        print(f"    Total: {stats['total_alerts']}")
        print(f"    Firing: {stats['firing_alerts']}")
        
        print(f"\n  Incidents:")
        print(f"    Total: {stats['total_incidents']}")
        print(f"    Active: {stats['active_incidents']}")
        
        print(f"\n  Response:")
        print(f"    Responders: {stats['responders']}")
        print(f"    Schedules: {stats['schedules']}")
        print(f"    Policies: {stats['policies']}")
        
        print(f"\n  Metrics:")
        print(f"    MTTA: {stats['mtta_seconds']:.1f}s")
        print(f"    MTTR: {stats['mttr_seconds']:.1f}s")
        
        print(f"\n  Learning:")
        print(f"    Post-mortems: {stats['postmortems']}")
        
        # Dashboard
        print("\n📋 Incident Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │              Incident Management Overview                   │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ 🚨 Firing Alerts:     {stats['firing_alerts']:>5}                             │")
        print(f"  │ 📋 Active Incidents:  {stats['active_incidents']:>5}                             │")
        print(f"  │ 👥 On-Call:           {stats['responders']:>5} responders                   │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ ⏱️  MTTA:              {stats['mtta_seconds']:>5.1f}s                           │")
        print(f"  │ ⏱️  MTTR:              {stats['mttr_seconds']:>5.1f}s                           │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Incident Management Platform initialized!")
    print("=" * 60)
