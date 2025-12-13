#!/usr/bin/env python3
"""
Server Init - Iteration 81: Incident Management Platform
Платформа управления инцидентами

Функционал:
- Incident Creation - создание инцидентов
- Severity Management - управление серьёзностью
- Escalation Policies - политики эскалации
- On-Call Management - управление дежурствами
- Status Page - страница статуса
- Post-Mortem - пост-мортемы
- Communication - коммуникация
- Timeline Tracking - отслеживание timeline
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
from collections import defaultdict
import uuid


class IncidentSeverity(Enum):
    """Серьёзность инцидента"""
    SEV1 = "sev1"  # Critical - полный outage
    SEV2 = "sev2"  # Major - значительное влияние
    SEV3 = "sev3"  # Minor - частичное влияние
    SEV4 = "sev4"  # Low - минимальное влияние
    SEV5 = "sev5"  # Informational


class IncidentStatus(Enum):
    """Статус инцидента"""
    TRIGGERED = "triggered"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MONITORING = "monitoring"
    RESOLVED = "resolved"
    CLOSED = "closed"


class ComponentStatus(Enum):
    """Статус компонента"""
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    PARTIAL_OUTAGE = "partial_outage"
    MAJOR_OUTAGE = "major_outage"
    MAINTENANCE = "maintenance"


class NotificationType(Enum):
    """Тип уведомления"""
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    PAGERDUTY = "pagerduty"
    WEBHOOK = "webhook"


class EscalationLevel(Enum):
    """Уровень эскалации"""
    L1 = "l1"  # First responders
    L2 = "l2"  # Senior engineers
    L3 = "l3"  # Team leads
    L4 = "l4"  # Management
    L5 = "l5"  # Executive


@dataclass
class TeamMember:
    """Член команды"""
    member_id: str
    name: str = ""
    email: str = ""
    phone: str = ""
    
    # Роль
    role: str = ""
    team: str = ""
    
    # Уровень эскалации
    escalation_level: EscalationLevel = EscalationLevel.L1
    
    # Каналы уведомлений
    notification_channels: List[NotificationType] = field(default_factory=list)
    
    # Статус
    on_call: bool = False


@dataclass
class OnCallSchedule:
    """Расписание дежурств"""
    schedule_id: str
    name: str = ""
    
    # Команда
    team: str = ""
    
    # Текущий дежурный
    current_on_call: str = ""
    
    # Ротация
    rotation_members: List[str] = field(default_factory=list)
    rotation_interval_hours: int = 168  # 1 неделя
    
    # Следующая ротация
    next_rotation: Optional[datetime] = None
    
    # Backups
    backup_members: List[str] = field(default_factory=list)


@dataclass
class EscalationPolicy:
    """Политика эскалации"""
    policy_id: str
    name: str = ""
    
    # Уровни эскалации
    # level -> (delay_minutes, member_ids or team)
    escalation_levels: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    
    # Повторение
    repeat_enabled: bool = True
    repeat_interval_minutes: int = 30
    max_repeats: int = 3


@dataclass
class TimelineEvent:
    """Событие timeline"""
    event_id: str
    
    # Время
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Тип
    event_type: str = ""  # status_change, note, action, escalation
    
    # Детали
    title: str = ""
    description: str = ""
    
    # Автор
    author: str = ""
    
    # Метаданные
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Incident:
    """Инцидент"""
    incident_id: str
    number: int = 0  # INC-001
    title: str = ""
    description: str = ""
    
    # Статус и серьёзность
    status: IncidentStatus = IncidentStatus.TRIGGERED
    severity: IncidentSeverity = IncidentSeverity.SEV3
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    # Ответственные
    commander: str = ""
    assignees: List[str] = field(default_factory=list)
    
    # Компоненты
    affected_components: List[str] = field(default_factory=list)
    
    # Timeline
    timeline: List[TimelineEvent] = field(default_factory=list)
    
    # Communication
    customer_facing: bool = True
    status_page_message: str = ""
    
    # Эскалация
    escalation_level: int = 0
    escalation_policy_id: str = ""
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Root cause
    root_cause: str = ""
    resolution: str = ""
    
    # Post-mortem
    postmortem_id: str = ""


@dataclass
class StatusComponent:
    """Компонент на странице статуса"""
    component_id: str
    name: str = ""
    description: str = ""
    
    # Статус
    status: ComponentStatus = ComponentStatus.OPERATIONAL
    
    # Группа
    group: str = ""
    
    # Порядок
    order: int = 0
    
    # Показывать на странице
    visible: bool = True


@dataclass
class StatusUpdate:
    """Обновление статуса"""
    update_id: str
    incident_id: str = ""
    
    # Статус
    status: IncidentStatus = IncidentStatus.INVESTIGATING
    
    # Сообщение
    message: str = ""
    
    # Время
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Автор
    author: str = ""


@dataclass
class PostMortem:
    """Пост-мортем"""
    postmortem_id: str
    incident_id: str = ""
    
    # Заголовок
    title: str = ""
    
    # Summary
    summary: str = ""
    
    # Impact
    impact: str = ""
    duration_minutes: int = 0
    affected_users: int = 0
    
    # Timeline
    timeline_summary: str = ""
    
    # Root Cause
    root_cause: str = ""
    
    # Contributing Factors
    contributing_factors: List[str] = field(default_factory=list)
    
    # Action Items
    action_items: List[Dict[str, Any]] = field(default_factory=list)
    
    # Lessons Learned
    lessons_learned: List[str] = field(default_factory=list)
    
    # Статус
    status: str = "draft"  # draft, review, published
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Alert:
    """Алерт"""
    alert_id: str
    
    # Источник
    source: str = ""  # monitoring, user, automated
    
    # Детали
    title: str = ""
    description: str = ""
    
    # Серьёзность
    severity: IncidentSeverity = IncidentSeverity.SEV3
    
    # Статус
    acknowledged: bool = False
    incident_id: str = ""  # Привязанный инцидент
    
    # Время
    triggered_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None


class NotificationService:
    """Сервис уведомлений"""
    
    def __init__(self):
        self.sent_notifications: List[Dict[str, Any]] = []
        
    async def send(self, member: TeamMember, message: str,
                    channels: List[NotificationType] = None):
        """Отправка уведомления"""
        channels = channels or member.notification_channels
        
        for channel in channels:
            notification = {
                "id": f"notif_{uuid.uuid4().hex[:8]}",
                "member_id": member.member_id,
                "channel": channel.value,
                "message": message,
                "sent_at": datetime.now()
            }
            self.sent_notifications.append(notification)
            
        return True


class EscalationEngine:
    """Движок эскалации"""
    
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service
        self.policies: Dict[str, EscalationPolicy] = {}
        self.members: Dict[str, TeamMember] = {}
        
        self.escalation_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
    def add_policy(self, policy: EscalationPolicy):
        """Добавление политики"""
        self.policies[policy.policy_id] = policy
        
    def add_member(self, member: TeamMember):
        """Добавление члена команды"""
        self.members[member.member_id] = member
        
    async def escalate(self, incident: Incident):
        """Эскалация инцидента"""
        policy = self.policies.get(incident.escalation_policy_id)
        if not policy:
            return
            
        current_level = incident.escalation_level
        next_level = current_level + 1
        
        if next_level not in policy.escalation_levels:
            return  # Достигнут максимальный уровень
            
        level_config = policy.escalation_levels[next_level]
        member_ids = level_config.get("members", [])
        
        for member_id in member_ids:
            member = self.members.get(member_id)
            if member:
                message = f"ESCALATION: {incident.title} (INC-{incident.number:03d})"
                await self.notification_service.send(member, message)
                
        incident.escalation_level = next_level
        
        self.escalation_history[incident.incident_id].append({
            "level": next_level,
            "timestamp": datetime.now(),
            "notified": member_ids
        })


class OnCallManager:
    """Менеджер дежурств"""
    
    def __init__(self):
        self.schedules: Dict[str, OnCallSchedule] = {}
        self.members: Dict[str, TeamMember] = {}
        
    def add_schedule(self, schedule: OnCallSchedule):
        """Добавление расписания"""
        self.schedules[schedule.schedule_id] = schedule
        
    def get_on_call(self, team: str) -> Optional[TeamMember]:
        """Получение текущего дежурного"""
        for schedule in self.schedules.values():
            if schedule.team == team:
                return self.members.get(schedule.current_on_call)
        return None
        
    def rotate(self, schedule_id: str):
        """Ротация дежурств"""
        schedule = self.schedules.get(schedule_id)
        if not schedule or not schedule.rotation_members:
            return
            
        current_idx = 0
        if schedule.current_on_call in schedule.rotation_members:
            current_idx = schedule.rotation_members.index(schedule.current_on_call)
            
        next_idx = (current_idx + 1) % len(schedule.rotation_members)
        
        # Обновляем статус on_call
        if schedule.current_on_call:
            old_member = self.members.get(schedule.current_on_call)
            if old_member:
                old_member.on_call = False
                
        schedule.current_on_call = schedule.rotation_members[next_idx]
        
        new_member = self.members.get(schedule.current_on_call)
        if new_member:
            new_member.on_call = True
            
        schedule.next_rotation = datetime.now() + timedelta(hours=schedule.rotation_interval_hours)


class StatusPageManager:
    """Менеджер страницы статуса"""
    
    def __init__(self):
        self.components: Dict[str, StatusComponent] = {}
        self.updates: List[StatusUpdate] = []
        
    def add_component(self, component: StatusComponent):
        """Добавление компонента"""
        self.components[component.component_id] = component
        
    def update_component_status(self, component_id: str, status: ComponentStatus):
        """Обновление статуса компонента"""
        component = self.components.get(component_id)
        if component:
            component.status = status
            
    def add_update(self, incident_id: str, status: IncidentStatus,
                    message: str, author: str = "") -> StatusUpdate:
        """Добавление обновления"""
        update = StatusUpdate(
            update_id=f"upd_{uuid.uuid4().hex[:8]}",
            incident_id=incident_id,
            status=status,
            message=message,
            author=author
        )
        self.updates.append(update)
        return update
        
    def get_overall_status(self) -> ComponentStatus:
        """Получение общего статуса"""
        if not self.components:
            return ComponentStatus.OPERATIONAL
            
        statuses = [c.status for c in self.components.values() if c.visible]
        
        if ComponentStatus.MAJOR_OUTAGE in statuses:
            return ComponentStatus.MAJOR_OUTAGE
        elif ComponentStatus.PARTIAL_OUTAGE in statuses:
            return ComponentStatus.PARTIAL_OUTAGE
        elif ComponentStatus.DEGRADED in statuses:
            return ComponentStatus.DEGRADED
        elif ComponentStatus.MAINTENANCE in statuses:
            return ComponentStatus.MAINTENANCE
            
        return ComponentStatus.OPERATIONAL


class IncidentManagementPlatform:
    """Платформа управления инцидентами"""
    
    def __init__(self):
        self.incidents: Dict[str, Incident] = {}
        self.alerts: Dict[str, Alert] = {}
        self.postmortems: Dict[str, PostMortem] = {}
        
        self.incident_counter = 0
        
        self.notification_service = NotificationService()
        self.escalation_engine = EscalationEngine(self.notification_service)
        self.on_call_manager = OnCallManager()
        self.status_page = StatusPageManager()
        
    def add_team_member(self, name: str, **kwargs) -> TeamMember:
        """Добавление члена команды"""
        member = TeamMember(
            member_id=f"member_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        self.escalation_engine.add_member(member)
        self.on_call_manager.members[member.member_id] = member
        return member
        
    def create_escalation_policy(self, name: str, **kwargs) -> EscalationPolicy:
        """Создание политики эскалации"""
        policy = EscalationPolicy(
            policy_id=f"policy_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        self.escalation_engine.add_policy(policy)
        return policy
        
    def create_on_call_schedule(self, name: str, team: str,
                                 members: List[str]) -> OnCallSchedule:
        """Создание расписания дежурств"""
        schedule = OnCallSchedule(
            schedule_id=f"sched_{uuid.uuid4().hex[:8]}",
            name=name,
            team=team,
            rotation_members=members,
            current_on_call=members[0] if members else ""
        )
        
        # Устанавливаем первого дежурного
        if schedule.current_on_call:
            member = self.on_call_manager.members.get(schedule.current_on_call)
            if member:
                member.on_call = True
                
        self.on_call_manager.add_schedule(schedule)
        return schedule
        
    def add_status_component(self, name: str, **kwargs) -> StatusComponent:
        """Добавление компонента статуса"""
        component = StatusComponent(
            component_id=f"comp_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        self.status_page.add_component(component)
        return component
        
    def create_alert(self, title: str, severity: IncidentSeverity = IncidentSeverity.SEV3,
                      **kwargs) -> Alert:
        """Создание алерта"""
        alert = Alert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            title=title,
            severity=severity,
            **kwargs
        )
        self.alerts[alert.alert_id] = alert
        return alert
        
    async def create_incident(self, title: str, severity: IncidentSeverity = IncidentSeverity.SEV3,
                               description: str = "", **kwargs) -> Incident:
        """Создание инцидента"""
        self.incident_counter += 1
        
        incident = Incident(
            incident_id=f"inc_{uuid.uuid4().hex[:8]}",
            number=self.incident_counter,
            title=title,
            description=description,
            severity=severity,
            **kwargs
        )
        
        # Добавляем начальное событие в timeline
        incident.timeline.append(TimelineEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type="created",
            title="Incident Created",
            description=f"Incident INC-{incident.number:03d} was created"
        ))
        
        self.incidents[incident.incident_id] = incident
        
        # Уведомляем дежурного
        on_call = self._get_on_call_for_severity(severity)
        if on_call:
            message = f"🚨 NEW INCIDENT: {title} (INC-{incident.number:03d}) - {severity.value.upper()}"
            await self.notification_service.send(on_call, message)
            
        return incident
        
    def _get_on_call_for_severity(self, severity: IncidentSeverity) -> Optional[TeamMember]:
        """Получение дежурного по серьёзности"""
        # Для SEV1/SEV2 - platform team
        # Для остальных - general team
        team = "platform" if severity in [IncidentSeverity.SEV1, IncidentSeverity.SEV2] else "general"
        return self.on_call_manager.get_on_call(team)
        
    async def acknowledge_incident(self, incident_id: str, responder: str):
        """Подтверждение инцидента"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return
            
        incident.status = IncidentStatus.ACKNOWLEDGED
        incident.acknowledged_at = datetime.now()
        incident.assignees.append(responder)
        
        incident.timeline.append(TimelineEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type="status_change",
            title="Incident Acknowledged",
            description=f"Acknowledged by {responder}",
            author=responder
        ))
        
    async def update_incident_status(self, incident_id: str, status: IncidentStatus,
                                       message: str = "", author: str = ""):
        """Обновление статуса инцидента"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return
            
        old_status = incident.status
        incident.status = status
        
        if status == IncidentStatus.RESOLVED:
            incident.resolved_at = datetime.now()
        elif status == IncidentStatus.CLOSED:
            incident.closed_at = datetime.now()
            
        incident.timeline.append(TimelineEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type="status_change",
            title=f"Status changed to {status.value}",
            description=message,
            author=author
        ))
        
        # Обновляем страницу статуса
        if incident.customer_facing:
            self.status_page.add_update(incident_id, status, message, author)
            
    def add_timeline_note(self, incident_id: str, note: str, author: str = ""):
        """Добавление заметки в timeline"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return
            
        incident.timeline.append(TimelineEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type="note",
            title="Note added",
            description=note,
            author=author
        ))
        
    def create_postmortem(self, incident_id: str) -> PostMortem:
        """Создание пост-мортема"""
        incident = self.incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")
            
        # Вычисляем duration
        duration = 0
        if incident.resolved_at and incident.created_at:
            duration = int((incident.resolved_at - incident.created_at).total_seconds() / 60)
            
        postmortem = PostMortem(
            postmortem_id=f"pm_{uuid.uuid4().hex[:8]}",
            incident_id=incident_id,
            title=f"Post-Mortem: {incident.title}",
            duration_minutes=duration,
            root_cause=incident.root_cause,
            summary=incident.description
        )
        
        self.postmortems[postmortem.postmortem_id] = postmortem
        incident.postmortem_id = postmortem.postmortem_id
        
        return postmortem
        
    def get_active_incidents(self) -> List[Incident]:
        """Получение активных инцидентов"""
        return [
            inc for inc in self.incidents.values()
            if inc.status not in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]
        ]
        
    def get_stats(self) -> Dict[str, Any]:
        """Статистика"""
        total = len(self.incidents)
        active = len(self.get_active_incidents())
        
        by_severity = defaultdict(int)
        for inc in self.incidents.values():
            by_severity[inc.severity.value] += 1
            
        avg_ttac = 0
        acknowledged = [inc for inc in self.incidents.values() if inc.acknowledged_at]
        if acknowledged:
            ttacs = [(inc.acknowledged_at - inc.created_at).total_seconds() / 60 
                     for inc in acknowledged]
            avg_ttac = sum(ttacs) / len(ttacs)
            
        return {
            "total_incidents": total,
            "active_incidents": active,
            "by_severity": dict(by_severity),
            "avg_time_to_acknowledge_minutes": round(avg_ttac, 2),
            "postmortems": len(self.postmortems),
            "alerts": len(self.alerts)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 81: Incident Management Platform")
    print("=" * 60)
    
    async def demo():
        platform = IncidentManagementPlatform()
        print("✓ Incident Management Platform created")
        
        # Добавление членов команды
        print("\n👥 Adding Team Members...")
        
        alice = platform.add_team_member(
            "Alice Johnson",
            email="alice@example.com",
            phone="+1234567890",
            role="SRE Lead",
            team="platform",
            escalation_level=EscalationLevel.L2,
            notification_channels=[NotificationType.EMAIL, NotificationType.SLACK, NotificationType.SMS]
        )
        print(f"  ✓ {alice.name} ({alice.role})")
        
        bob = platform.add_team_member(
            "Bob Smith",
            email="bob@example.com",
            role="Senior SRE",
            team="platform",
            escalation_level=EscalationLevel.L1,
            notification_channels=[NotificationType.EMAIL, NotificationType.SLACK]
        )
        print(f"  ✓ {bob.name} ({bob.role})")
        
        charlie = platform.add_team_member(
            "Charlie Brown",
            email="charlie@example.com",
            role="Engineering Manager",
            team="platform",
            escalation_level=EscalationLevel.L3,
            notification_channels=[NotificationType.EMAIL, NotificationType.SMS]
        )
        print(f"  ✓ {charlie.name} ({charlie.role})")
        
        # Создание расписания дежурств
        print("\n📅 Creating On-Call Schedule...")
        
        schedule = platform.create_on_call_schedule(
            "Platform On-Call",
            team="platform",
            members=[bob.member_id, alice.member_id]
        )
        print(f"  ✓ Schedule: {schedule.name}")
        print(f"    Current on-call: {bob.name}")
        print(f"    Rotation: weekly")
        
        # Создание политики эскалации
        print("\n📈 Creating Escalation Policy...")
        
        policy = platform.create_escalation_policy(
            "Platform Escalation",
            escalation_levels={
                1: {"delay_minutes": 0, "members": [bob.member_id]},
                2: {"delay_minutes": 15, "members": [alice.member_id]},
                3: {"delay_minutes": 30, "members": [charlie.member_id]},
            }
        )
        print(f"  ✓ Policy: {policy.name}")
        print(f"    Levels: {len(policy.escalation_levels)}")
        
        # Добавление компонентов статуса
        print("\n🔧 Adding Status Page Components...")
        
        api = platform.add_status_component(
            "API Gateway",
            description="Core API services",
            group="Core Services"
        )
        print(f"  ✓ {api.name}")
        
        database = platform.add_status_component(
            "Database Cluster",
            description="PostgreSQL database",
            group="Core Services"
        )
        print(f"  ✓ {database.name}")
        
        cdn = platform.add_status_component(
            "CDN",
            description="Content delivery",
            group="Edge Services"
        )
        print(f"  ✓ {cdn.name}")
        
        auth = platform.add_status_component(
            "Authentication",
            description="User authentication",
            group="Security"
        )
        print(f"  ✓ {auth.name}")
        
        # Создание алерта
        print("\n🚨 Creating Alert...")
        
        alert = platform.create_alert(
            "High Error Rate on API Gateway",
            severity=IncidentSeverity.SEV2,
            source="prometheus",
            description="Error rate exceeded 5% threshold"
        )
        print(f"  ✓ Alert: {alert.title}")
        print(f"    Severity: {alert.severity.value}")
        
        # Создание инцидента из алерта
        print("\n🔥 Creating Incident...")
        
        incident = await platform.create_incident(
            "API Gateway Performance Degradation",
            severity=IncidentSeverity.SEV2,
            description="Multiple customers reporting slow API response times",
            affected_components=[api.component_id],
            escalation_policy_id=policy.policy_id,
            customer_facing=True,
            tags=["api", "performance", "customer-impact"]
        )
        print(f"\n  ✓ Incident: INC-{incident.number:03d}")
        print(f"    Title: {incident.title}")
        print(f"    Severity: {incident.severity.value}")
        print(f"    Status: {incident.status.value}")
        
        # Привязываем алерт к инциденту
        alert.incident_id = incident.incident_id
        alert.acknowledged = True
        
        # Обновляем статус компонента
        platform.status_page.update_component_status(api.component_id, ComponentStatus.DEGRADED)
        
        # Подтверждение инцидента
        print("\n✋ Acknowledging Incident...")
        
        await asyncio.sleep(0.1)  # Симуляция задержки
        await platform.acknowledge_incident(incident.incident_id, bob.name)
        print(f"  ✓ Acknowledged by {bob.name}")
        print(f"    Time to acknowledge: {(incident.acknowledged_at - incident.created_at).total_seconds():.1f}s")
        
        # Обновления статуса
        print("\n📝 Incident Updates...")
        
        await platform.update_incident_status(
            incident.incident_id,
            IncidentStatus.INVESTIGATING,
            "Investigating high error rates. Initial analysis shows database connection issues.",
            bob.name
        )
        print(f"  ✓ Status: {IncidentStatus.INVESTIGATING.value}")
        
        platform.add_timeline_note(
            incident.incident_id,
            "Identified slow queries on users table. Working on optimizing.",
            bob.name
        )
        print("  ✓ Added timeline note")
        
        await platform.update_incident_status(
            incident.incident_id,
            IncidentStatus.IDENTIFIED,
            "Root cause identified: Missing index on users.email column causing full table scans.",
            alice.name
        )
        print(f"  ✓ Status: {IncidentStatus.IDENTIFIED.value}")
        
        platform.add_timeline_note(
            incident.incident_id,
            "Adding missing index on users.email column.",
            alice.name
        )
        
        await platform.update_incident_status(
            incident.incident_id,
            IncidentStatus.MONITORING,
            "Fix deployed. Monitoring for stability.",
            alice.name
        )
        print(f"  ✓ Status: {IncidentStatus.MONITORING.value}")
        
        await asyncio.sleep(0.1)  # Симуляция мониторинга
        
        await platform.update_incident_status(
            incident.incident_id,
            IncidentStatus.RESOLVED,
            "Error rates returned to normal. Incident resolved.",
            alice.name
        )
        print(f"  ✓ Status: {IncidentStatus.RESOLVED.value}")
        
        # Обновляем root cause
        incident.root_cause = "Missing database index on users.email column"
        incident.resolution = "Added index on users.email column"
        
        # Восстанавливаем статус компонента
        platform.status_page.update_component_status(api.component_id, ComponentStatus.OPERATIONAL)
        
        # Просмотр timeline
        print("\n📜 Incident Timeline:")
        for event in incident.timeline:
            time_str = event.timestamp.strftime("%H:%M:%S")
            print(f"  [{time_str}] {event.title}")
            if event.description:
                print(f"           {event.description[:60]}...")
                
        # Создание пост-мортема
        print("\n📋 Creating Post-Mortem...")
        
        postmortem = platform.create_postmortem(incident.incident_id)
        postmortem.impact = "50% of API requests experienced increased latency (>2s response time)"
        postmortem.affected_users = 5000
        postmortem.contributing_factors = [
            "Rapid user growth not anticipated in capacity planning",
            "Missing database index went unnoticed in code review",
            "No slow query alerting configured"
        ]
        postmortem.action_items = [
            {"task": "Implement slow query alerting", "owner": "Bob", "due": "Next sprint"},
            {"task": "Review all tables for missing indexes", "owner": "Alice", "due": "2 weeks"},
            {"task": "Add index review to PR checklist", "owner": "Charlie", "due": "1 week"},
        ]
        postmortem.lessons_learned = [
            "Need better database monitoring for query performance",
            "Code review should include database schema checks",
            "Capacity planning should include database growth projections"
        ]
        postmortem.status = "review"
        
        print(f"  ✓ Post-mortem: {postmortem.postmortem_id}")
        print(f"    Duration: {postmortem.duration_minutes} minutes")
        print(f"    Affected users: {postmortem.affected_users}")
        print(f"    Action items: {len(postmortem.action_items)}")
        
        # Status Page
        print("\n📊 Status Page:")
        overall = platform.status_page.get_overall_status()
        print(f"  Overall Status: {overall.value}")
        
        print("\n  Components:")
        for comp in platform.status_page.components.values():
            icon = "✓" if comp.status == ComponentStatus.OPERATIONAL else "⚠"
            print(f"    {icon} {comp.name}: {comp.status.value}")
            
        # Создание ещё одного инцидента
        print("\n🔥 Creating SEV1 Incident...")
        
        sev1_incident = await platform.create_incident(
            "Complete Database Outage",
            severity=IncidentSeverity.SEV1,
            description="Database cluster is completely unavailable",
            affected_components=[database.component_id],
            escalation_policy_id=policy.policy_id,
            customer_facing=True,
            tags=["database", "outage", "critical"]
        )
        print(f"  ✓ Incident: INC-{sev1_incident.number:03d}")
        print(f"    Severity: {sev1_incident.severity.value}")
        
        platform.status_page.update_component_status(database.component_id, ComponentStatus.MAJOR_OUTAGE)
        
        # Проверяем общий статус
        overall = platform.status_page.get_overall_status()
        print(f"  Status Page: {overall.value}")
        
        # Быстро решаем
        await platform.acknowledge_incident(sev1_incident.incident_id, alice.name)
        await platform.update_incident_status(
            sev1_incident.incident_id,
            IncidentStatus.RESOLVED,
            "Database cluster restarted successfully.",
            alice.name
        )
        platform.status_page.update_component_status(database.component_id, ComponentStatus.OPERATIONAL)
        
        # Статистика
        print("\n📈 Platform Statistics:")
        stats = platform.get_stats()
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    {k}: {v}")
            else:
                print(f"  {key}: {value}")
                
        # Активные инциденты
        print("\n🔴 Active Incidents:")
        active = platform.get_active_incidents()
        if active:
            for inc in active:
                print(f"  • INC-{inc.number:03d}: {inc.title}")
        else:
            print("  No active incidents")
            
        # Уведомления
        print("\n📧 Notifications Sent:")
        for notif in platform.notification_service.sent_notifications[:5]:
            member = platform.escalation_engine.members.get(notif["member_id"])
            name = member.name if member else "Unknown"
            print(f"  • {notif['channel']}: {name}")
            
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Incident Management Platform initialized!")
    print("=" * 60)
