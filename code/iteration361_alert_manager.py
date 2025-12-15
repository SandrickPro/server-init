#!/usr/bin/env python3
"""
Server Init - Iteration 361: Alert Manager Platform
Платформа управления алертами

Функционал:
- Alert Routing - маршрутизация алертов
- Alert Grouping - группировка алертов
- Silencing - подавление алертов
- Inhibition - ингибирование алертов
- Notification Channels - каналы уведомлений
- Escalation Policies - политики эскалации
- On-Call Management - управление дежурствами
- Incident Management - управление инцидентами
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
import uuid
import json
import re


class AlertSeverity(Enum):
    """Критичность алерта"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertState(Enum):
    """Состояние алерта"""
    PENDING = "pending"
    FIRING = "firing"
    RESOLVED = "resolved"


class NotificationChannel(Enum):
    """Канал уведомлений"""
    EMAIL = "email"
    SLACK = "slack"
    PAGERDUTY = "pagerduty"
    WEBHOOK = "webhook"
    SMS = "sms"
    TEAMS = "teams"
    OPSGENIE = "opsgenie"
    TELEGRAM = "telegram"


class IncidentStatus(Enum):
    """Статус инцидента"""
    TRIGGERED = "triggered"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class IncidentPriority(Enum):
    """Приоритет инцидента"""
    P1 = "p1"  # Critical
    P2 = "p2"  # High
    P3 = "p3"  # Medium
    P4 = "p4"  # Low
    P5 = "p5"  # Informational


class EscalationState(Enum):
    """Состояние эскалации"""
    NOT_ESCALATED = "not_escalated"
    ESCALATING = "escalating"
    ESCALATED = "escalated"


@dataclass
class Alert:
    """Алерт"""
    alert_id: str
    
    # Identity
    fingerprint: str = ""
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Annotations
    annotations: Dict[str, str] = field(default_factory=dict)
    
    # State
    state: AlertState = AlertState.FIRING
    
    # Severity
    severity: AlertSeverity = AlertSeverity.WARNING
    
    # Timestamps
    starts_at: datetime = field(default_factory=datetime.now)
    ends_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Generator URL
    generator_url: str = ""


@dataclass
class AlertGroup:
    """Группа алертов"""
    group_id: str
    
    # Group key
    group_key: str = ""
    
    # Labels
    group_labels: Dict[str, str] = field(default_factory=dict)
    common_labels: Dict[str, str] = field(default_factory=dict)
    common_annotations: Dict[str, str] = field(default_factory=dict)
    
    # Alerts
    alerts: List[str] = field(default_factory=list)
    
    # Status
    status: str = "firing"  # firing, resolved
    
    # Receiver
    receiver: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Route:
    """Маршрут алертов"""
    route_id: str
    
    # Receiver
    receiver: str = ""
    
    # Match conditions
    match: Dict[str, str] = field(default_factory=dict)
    match_re: Dict[str, str] = field(default_factory=dict)
    
    # Grouping
    group_by: List[str] = field(default_factory=list)
    group_wait: str = "30s"
    group_interval: str = "5m"
    repeat_interval: str = "4h"
    
    # Continue routing
    continue_routing: bool = False
    
    # Mute time
    mute_time_intervals: List[str] = field(default_factory=list)
    
    # Child routes
    routes: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Receiver:
    """Получатель уведомлений"""
    receiver_id: str
    name: str
    
    # Configurations
    email_configs: List[Dict[str, Any]] = field(default_factory=list)
    slack_configs: List[Dict[str, Any]] = field(default_factory=list)
    pagerduty_configs: List[Dict[str, Any]] = field(default_factory=list)
    webhook_configs: List[Dict[str, Any]] = field(default_factory=list)
    opsgenie_configs: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Silence:
    """Подавление алертов"""
    silence_id: str
    
    # Matchers
    matchers: List[Dict[str, str]] = field(default_factory=list)
    
    # Time range
    starts_at: datetime = field(default_factory=datetime.now)
    ends_at: datetime = field(default_factory=datetime.now)
    
    # Comment
    comment: str = ""
    created_by: str = ""
    
    # Status
    status: str = "active"  # active, expired, pending
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


@dataclass
class InhibitionRule:
    """Правило ингибирования"""
    rule_id: str
    
    # Source matchers (inhibiting alert)
    source_match: Dict[str, str] = field(default_factory=dict)
    source_match_re: Dict[str, str] = field(default_factory=dict)
    
    # Target matchers (inhibited alert)
    target_match: Dict[str, str] = field(default_factory=dict)
    target_match_re: Dict[str, str] = field(default_factory=dict)
    
    # Equal labels (must match between source and target)
    equal: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Notification:
    """Уведомление"""
    notification_id: str
    
    # Alert group
    group_id: str = ""
    
    # Receiver
    receiver: str = ""
    channel: NotificationChannel = NotificationChannel.EMAIL
    
    # Status
    status: str = "pending"  # pending, sent, failed
    
    # Retry
    retry_count: int = 0
    max_retries: int = 3
    
    # Error
    error: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    sent_at: Optional[datetime] = None


@dataclass
class EscalationPolicy:
    """Политика эскалации"""
    policy_id: str
    name: str
    
    # Levels
    levels: List[Dict[str, Any]] = field(default_factory=list)
    
    # Repeat
    repeat_enabled: bool = False
    repeat_after_level: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class EscalationLevel:
    """Уровень эскалации"""
    level_id: str
    level_number: int
    
    # Targets
    targets: List[Dict[str, str]] = field(default_factory=list)
    
    # Delay
    delay_minutes: int = 0
    
    # Notification channels
    channels: List[NotificationChannel] = field(default_factory=list)


@dataclass
class OnCallSchedule:
    """Расписание дежурств"""
    schedule_id: str
    name: str
    
    # Time zone
    timezone: str = "UTC"
    
    # Rotation
    rotation_type: str = "weekly"  # daily, weekly, custom
    
    # Users
    users: List[str] = field(default_factory=list)
    
    # Current on-call
    current_user: str = ""
    
    # Handoff time
    handoff_time: str = "09:00"
    handoff_day: int = 1  # Monday
    
    # Overrides
    overrides: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Incident:
    """Инцидент"""
    incident_id: str
    
    # Title
    title: str = ""
    description: str = ""
    
    # Status
    status: IncidentStatus = IncidentStatus.TRIGGERED
    
    # Priority
    priority: IncidentPriority = IncidentPriority.P3
    
    # Service
    service: str = ""
    
    # Assignee
    assignee: str = ""
    
    # Alerts
    alert_ids: List[str] = field(default_factory=list)
    
    # Escalation
    escalation_policy_id: str = ""
    escalation_state: EscalationState = EscalationState.NOT_ESCALATED
    current_escalation_level: int = 0
    
    # Timeline
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    
    # Resolution
    resolution_note: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


@dataclass
class User:
    """Пользователь"""
    user_id: str
    name: str
    email: str
    
    # Contact methods
    phone: str = ""
    slack_id: str = ""
    
    # Role
    role: str = "responder"  # admin, responder, stakeholder
    
    # Teams
    teams: List[str] = field(default_factory=list)
    
    # Notifications
    notification_preferences: Dict[str, bool] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Team:
    """Команда"""
    team_id: str
    name: str
    
    # Members
    members: List[str] = field(default_factory=list)
    
    # Escalation policy
    escalation_policy_id: str = ""
    
    # On-call schedule
    schedule_id: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AlertManagerMetrics:
    """Метрики Alert Manager"""
    metrics_id: str
    
    # Alerts
    total_alerts: int = 0
    firing_alerts: int = 0
    
    # Groups
    total_groups: int = 0
    
    # Silences
    active_silences: int = 0
    
    # Notifications
    total_notifications: int = 0
    successful_notifications: int = 0
    failed_notifications: int = 0
    
    # Incidents
    total_incidents: int = 0
    open_incidents: int = 0
    
    # MTTR
    avg_resolution_time_minutes: float = 0.0
    
    # Timestamps
    collected_at: datetime = field(default_factory=datetime.now)


class AlertManagerPlatform:
    """Платформа управления алертами"""
    
    def __init__(self, platform_name: str = "alert-manager"):
        self.platform_name = platform_name
        self.alerts: Dict[str, Alert] = {}
        self.alert_groups: Dict[str, AlertGroup] = {}
        self.routes: Dict[str, Route] = {}
        self.receivers: Dict[str, Receiver] = {}
        self.silences: Dict[str, Silence] = {}
        self.inhibition_rules: Dict[str, InhibitionRule] = {}
        self.notifications: Dict[str, Notification] = {}
        self.escalation_policies: Dict[str, EscalationPolicy] = {}
        self.schedules: Dict[str, OnCallSchedule] = {}
        self.incidents: Dict[str, Incident] = {}
        self.users: Dict[str, User] = {}
        self.teams: Dict[str, Team] = {}
        
    async def create_alert(self, labels: Dict[str, str],
                          annotations: Dict[str, str] = None,
                          severity: AlertSeverity = AlertSeverity.WARNING,
                          generator_url: str = "") -> Alert:
        """Создание алерта"""
        # Generate fingerprint from labels
        fingerprint = str(hash(json.dumps(labels, sort_keys=True)))
        
        alert = Alert(
            alert_id=f"alt_{uuid.uuid4().hex[:8]}",
            fingerprint=fingerprint,
            labels=labels,
            annotations=annotations or {},
            severity=severity,
            generator_url=generator_url
        )
        
        self.alerts[alert.alert_id] = alert
        
        # Route alert
        await self._route_alert(alert)
        
        return alert
        
    async def _route_alert(self, alert: Alert):
        """Маршрутизация алерта"""
        for route in self.routes.values():
            if await self._match_route(alert, route):
                # Add to group
                await self._add_to_group(alert, route)
                
                if not route.continue_routing:
                    break
                    
    async def _match_route(self, alert: Alert, route: Route) -> bool:
        """Проверка соответствия алерта маршруту"""
        # Check exact match
        for key, value in route.match.items():
            if alert.labels.get(key) != value:
                return False
                
        # Check regex match
        for key, pattern in route.match_re.items():
            label_value = alert.labels.get(key, "")
            if not re.match(pattern, label_value):
                return False
                
        return True
        
    async def _add_to_group(self, alert: Alert, route: Route):
        """Добавление алерта в группу"""
        # Generate group key
        group_labels = {k: alert.labels.get(k, "") for k in route.group_by}
        group_key = json.dumps(group_labels, sort_keys=True)
        
        if group_key not in self.alert_groups:
            self.alert_groups[group_key] = AlertGroup(
                group_id=f"grp_{uuid.uuid4().hex[:8]}",
                group_key=group_key,
                group_labels=group_labels,
                receiver=route.receiver
            )
            
        group = self.alert_groups[group_key]
        group.alerts.append(alert.alert_id)
        
    async def resolve_alert(self, alert_id: str) -> Optional[Alert]:
        """Разрешение алерта"""
        alert = self.alerts.get(alert_id)
        if not alert:
            return None
            
        alert.state = AlertState.RESOLVED
        alert.ends_at = datetime.now()
        
        return alert
        
    async def create_route(self, receiver: str,
                          match: Dict[str, str] = None,
                          match_re: Dict[str, str] = None,
                          group_by: List[str] = None,
                          group_wait: str = "30s",
                          group_interval: str = "5m",
                          repeat_interval: str = "4h") -> Route:
        """Создание маршрута"""
        route = Route(
            route_id=f"rt_{uuid.uuid4().hex[:8]}",
            receiver=receiver,
            match=match or {},
            match_re=match_re or {},
            group_by=group_by or ["alertname"],
            group_wait=group_wait,
            group_interval=group_interval,
            repeat_interval=repeat_interval
        )
        
        self.routes[route.route_id] = route
        return route
        
    async def create_receiver(self, name: str,
                             email_configs: List[Dict[str, Any]] = None,
                             slack_configs: List[Dict[str, Any]] = None,
                             pagerduty_configs: List[Dict[str, Any]] = None,
                             webhook_configs: List[Dict[str, Any]] = None) -> Receiver:
        """Создание получателя"""
        receiver = Receiver(
            receiver_id=f"rcv_{uuid.uuid4().hex[:8]}",
            name=name,
            email_configs=email_configs or [],
            slack_configs=slack_configs or [],
            pagerduty_configs=pagerduty_configs or [],
            webhook_configs=webhook_configs or []
        )
        
        self.receivers[receiver.receiver_id] = receiver
        return receiver
        
    async def create_silence(self, matchers: List[Dict[str, str]],
                            starts_at: datetime,
                            ends_at: datetime,
                            comment: str = "",
                            created_by: str = "") -> Silence:
        """Создание подавления"""
        silence = Silence(
            silence_id=f"sil_{uuid.uuid4().hex[:8]}",
            matchers=matchers,
            starts_at=starts_at,
            ends_at=ends_at,
            comment=comment,
            created_by=created_by
        )
        
        self.silences[silence.silence_id] = silence
        return silence
        
    async def is_silenced(self, alert: Alert) -> bool:
        """Проверка подавления алерта"""
        now = datetime.now()
        
        for silence in self.silences.values():
            if silence.status != "active":
                continue
            if now < silence.starts_at or now > silence.ends_at:
                continue
                
            # Check matchers
            matches = True
            for matcher in silence.matchers:
                name = matcher.get("name", "")
                value = matcher.get("value", "")
                is_regex = matcher.get("isRegex", False)
                
                label_value = alert.labels.get(name, "")
                
                if is_regex:
                    if not re.match(value, label_value):
                        matches = False
                        break
                else:
                    if label_value != value:
                        matches = False
                        break
                        
            if matches:
                return True
                
        return False
        
    async def create_inhibition_rule(self, source_match: Dict[str, str],
                                    target_match: Dict[str, str],
                                    equal: List[str] = None) -> InhibitionRule:
        """Создание правила ингибирования"""
        rule = InhibitionRule(
            rule_id=f"inh_{uuid.uuid4().hex[:8]}",
            source_match=source_match,
            target_match=target_match,
            equal=equal or []
        )
        
        self.inhibition_rules[rule.rule_id] = rule
        return rule
        
    async def is_inhibited(self, alert: Alert) -> bool:
        """Проверка ингибирования алерта"""
        for rule in self.inhibition_rules.values():
            # Check if alert matches target
            target_matches = all(
                alert.labels.get(k) == v
                for k, v in rule.target_match.items()
            )
            
            if not target_matches:
                continue
                
            # Look for inhibiting source alert
            for source_alert in self.alerts.values():
                if source_alert.state != AlertState.FIRING:
                    continue
                    
                # Check source match
                source_matches = all(
                    source_alert.labels.get(k) == v
                    for k, v in rule.source_match.items()
                )
                
                if not source_matches:
                    continue
                    
                # Check equal labels
                equal_matches = all(
                    alert.labels.get(k) == source_alert.labels.get(k)
                    for k in rule.equal
                )
                
                if equal_matches:
                    return True
                    
        return False
        
    async def send_notification(self, group_id: str,
                               receiver_name: str,
                               channel: NotificationChannel) -> Notification:
        """Отправка уведомления"""
        notification = Notification(
            notification_id=f"ntf_{uuid.uuid4().hex[:8]}",
            group_id=group_id,
            receiver=receiver_name,
            channel=channel
        )
        
        # Simulate sending
        await asyncio.sleep(0.01)
        
        if random.random() < 0.95:  # 95% success rate
            notification.status = "sent"
            notification.sent_at = datetime.now()
        else:
            notification.status = "failed"
            notification.error = "Connection timeout"
            
        self.notifications[notification.notification_id] = notification
        return notification
        
    async def create_escalation_policy(self, name: str,
                                       levels: List[Dict[str, Any]],
                                       repeat_enabled: bool = False) -> EscalationPolicy:
        """Создание политики эскалации"""
        policy = EscalationPolicy(
            policy_id=f"esc_{uuid.uuid4().hex[:8]}",
            name=name,
            levels=levels,
            repeat_enabled=repeat_enabled
        )
        
        self.escalation_policies[policy.policy_id] = policy
        return policy
        
    async def create_schedule(self, name: str,
                             users: List[str],
                             rotation_type: str = "weekly",
                             handoff_time: str = "09:00",
                             timezone: str = "UTC") -> OnCallSchedule:
        """Создание расписания дежурств"""
        schedule = OnCallSchedule(
            schedule_id=f"sch_{uuid.uuid4().hex[:8]}",
            name=name,
            users=users,
            rotation_type=rotation_type,
            handoff_time=handoff_time,
            timezone=timezone,
            current_user=users[0] if users else ""
        )
        
        self.schedules[schedule.schedule_id] = schedule
        return schedule
        
    async def get_current_oncall(self, schedule_id: str) -> Optional[str]:
        """Получение текущего дежурного"""
        schedule = self.schedules.get(schedule_id)
        if not schedule:
            return None
        return schedule.current_user
        
    async def create_incident(self, title: str,
                             description: str = "",
                             priority: IncidentPriority = IncidentPriority.P3,
                             service: str = "",
                             alert_ids: List[str] = None,
                             escalation_policy_id: str = "") -> Incident:
        """Создание инцидента"""
        incident = Incident(
            incident_id=f"inc_{uuid.uuid4().hex[:8]}",
            title=title,
            description=description,
            priority=priority,
            service=service,
            alert_ids=alert_ids or [],
            escalation_policy_id=escalation_policy_id
        )
        
        # Add to timeline
        incident.timeline.append({
            "event": "incident_created",
            "timestamp": datetime.now().isoformat(),
            "description": f"Incident created: {title}"
        })
        
        self.incidents[incident.incident_id] = incident
        return incident
        
    async def acknowledge_incident(self, incident_id: str,
                                  user_id: str) -> Optional[Incident]:
        """Подтверждение инцидента"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return None
            
        incident.status = IncidentStatus.ACKNOWLEDGED
        incident.acknowledged_at = datetime.now()
        incident.assignee = user_id
        
        incident.timeline.append({
            "event": "incident_acknowledged",
            "timestamp": datetime.now().isoformat(),
            "user": user_id,
            "description": f"Incident acknowledged by {user_id}"
        })
        
        return incident
        
    async def resolve_incident(self, incident_id: str,
                              resolution_note: str = "") -> Optional[Incident]:
        """Разрешение инцидента"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return None
            
        incident.status = IncidentStatus.RESOLVED
        incident.resolved_at = datetime.now()
        incident.resolution_note = resolution_note
        
        incident.timeline.append({
            "event": "incident_resolved",
            "timestamp": datetime.now().isoformat(),
            "description": f"Incident resolved: {resolution_note}"
        })
        
        return incident
        
    async def escalate_incident(self, incident_id: str) -> Optional[Incident]:
        """Эскалация инцидента"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return None
            
        policy = self.escalation_policies.get(incident.escalation_policy_id)
        if not policy:
            return incident
            
        incident.escalation_state = EscalationState.ESCALATING
        incident.current_escalation_level += 1
        
        if incident.current_escalation_level <= len(policy.levels):
            level = policy.levels[incident.current_escalation_level - 1]
            incident.timeline.append({
                "event": "incident_escalated",
                "timestamp": datetime.now().isoformat(),
                "level": incident.current_escalation_level,
                "description": f"Escalated to level {incident.current_escalation_level}"
            })
            
        return incident
        
    async def create_user(self, name: str,
                         email: str,
                         phone: str = "",
                         role: str = "responder",
                         teams: List[str] = None) -> User:
        """Создание пользователя"""
        user = User(
            user_id=f"usr_{uuid.uuid4().hex[:8]}",
            name=name,
            email=email,
            phone=phone,
            role=role,
            teams=teams or []
        )
        
        self.users[user.user_id] = user
        return user
        
    async def create_team(self, name: str,
                         members: List[str] = None,
                         escalation_policy_id: str = "",
                         schedule_id: str = "") -> Team:
        """Создание команды"""
        team = Team(
            team_id=f"team_{uuid.uuid4().hex[:8]}",
            name=name,
            members=members or [],
            escalation_policy_id=escalation_policy_id,
            schedule_id=schedule_id
        )
        
        self.teams[team.team_id] = team
        return team
        
    async def collect_metrics(self) -> AlertManagerMetrics:
        """Сбор метрик"""
        firing_alerts = sum(1 for a in self.alerts.values() if a.state == AlertState.FIRING)
        active_silences = sum(1 for s in self.silences.values() if s.status == "active")
        
        successful_notifications = sum(1 for n in self.notifications.values() if n.status == "sent")
        failed_notifications = sum(1 for n in self.notifications.values() if n.status == "failed")
        
        open_incidents = sum(1 for i in self.incidents.values() if i.status != IncidentStatus.RESOLVED)
        
        # Calculate MTTR
        resolved_incidents = [i for i in self.incidents.values() if i.resolved_at]
        if resolved_incidents:
            resolution_times = [
                (i.resolved_at - i.created_at).total_seconds() / 60
                for i in resolved_incidents
            ]
            avg_resolution_time = sum(resolution_times) / len(resolution_times)
        else:
            avg_resolution_time = 0.0
            
        return AlertManagerMetrics(
            metrics_id=f"amm_{uuid.uuid4().hex[:8]}",
            total_alerts=len(self.alerts),
            firing_alerts=firing_alerts,
            total_groups=len(self.alert_groups),
            active_silences=active_silences,
            total_notifications=len(self.notifications),
            successful_notifications=successful_notifications,
            failed_notifications=failed_notifications,
            total_incidents=len(self.incidents),
            open_incidents=open_incidents,
            avg_resolution_time_minutes=avg_resolution_time
        )
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        firing_alerts = sum(1 for a in self.alerts.values() if a.state == AlertState.FIRING)
        active_silences = sum(1 for s in self.silences.values() if s.status == "active")
        open_incidents = sum(1 for i in self.incidents.values() if i.status != IncidentStatus.RESOLVED)
        
        alerts_by_severity = {}
        for severity in AlertSeverity:
            alerts_by_severity[severity.value] = sum(
                1 for a in self.alerts.values()
                if a.severity == severity and a.state == AlertState.FIRING
            )
            
        return {
            "total_alerts": len(self.alerts),
            "firing_alerts": firing_alerts,
            "alerts_by_severity": alerts_by_severity,
            "total_groups": len(self.alert_groups),
            "total_routes": len(self.routes),
            "total_receivers": len(self.receivers),
            "total_silences": len(self.silences),
            "active_silences": active_silences,
            "inhibition_rules": len(self.inhibition_rules),
            "total_notifications": len(self.notifications),
            "escalation_policies": len(self.escalation_policies),
            "total_schedules": len(self.schedules),
            "total_incidents": len(self.incidents),
            "open_incidents": open_incidents,
            "total_users": len(self.users),
            "total_teams": len(self.teams)
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 361: Alert Manager Platform")
    print("=" * 60)
    
    platform = AlertManagerPlatform(platform_name="enterprise-alertmanager")
    print("✓ Alert Manager Platform initialized")
    
    # Create Users
    print("\n👥 Creating Users...")
    
    users_data = [
        ("John Smith", "john@example.com", "+1-555-0101", "admin"),
        ("Jane Doe", "jane@example.com", "+1-555-0102", "responder"),
        ("Bob Wilson", "bob@example.com", "+1-555-0103", "responder"),
        ("Alice Brown", "alice@example.com", "+1-555-0104", "responder"),
        ("Charlie Davis", "charlie@example.com", "+1-555-0105", "responder"),
        ("Eva Martinez", "eva@example.com", "+1-555-0106", "stakeholder")
    ]
    
    users = []
    for name, email, phone, role in users_data:
        user = await platform.create_user(name, email, phone, role)
        users.append(user)
        print(f"  👤 {name} ({role})")
        
    # Create Teams
    print("\n👥 Creating Teams...")
    
    teams_data = [
        ("Platform Team", [users[0].user_id, users[1].user_id]),
        ("Backend Team", [users[2].user_id, users[3].user_id]),
        ("Infrastructure Team", [users[4].user_id])
    ]
    
    teams = []
    for name, members in teams_data:
        team = await platform.create_team(name, members)
        teams.append(team)
        print(f"  👥 {name} ({len(members)} members)")
        
    # Create On-Call Schedules
    print("\n📅 Creating On-Call Schedules...")
    
    schedules_data = [
        ("Platform On-Call", [users[0].user_id, users[1].user_id], "weekly"),
        ("Backend On-Call", [users[2].user_id, users[3].user_id], "weekly"),
        ("Infrastructure On-Call", [users[4].user_id], "daily")
    ]
    
    schedules = []
    for name, schedule_users, rotation in schedules_data:
        schedule = await platform.create_schedule(name, schedule_users, rotation)
        schedules.append(schedule)
        print(f"  📅 {name} ({rotation} rotation)")
        
    # Create Escalation Policies
    print("\n📈 Creating Escalation Policies...")
    
    policies_data = [
        ("Critical Escalation", [
            {"level": 1, "targets": [users[0].user_id], "delay_minutes": 0, "channels": ["slack", "pagerduty"]},
            {"level": 2, "targets": [users[1].user_id, users[2].user_id], "delay_minutes": 15, "channels": ["slack", "phone"]},
            {"level": 3, "targets": [users[5].user_id], "delay_minutes": 30, "channels": ["phone", "sms"]}
        ]),
        ("Standard Escalation", [
            {"level": 1, "targets": [users[1].user_id], "delay_minutes": 0, "channels": ["slack"]},
            {"level": 2, "targets": [users[0].user_id], "delay_minutes": 30, "channels": ["slack", "email"]}
        ])
    ]
    
    policies = []
    for name, levels in policies_data:
        policy = await platform.create_escalation_policy(name, levels)
        policies.append(policy)
        print(f"  📈 {name} ({len(levels)} levels)")
        
    # Create Receivers
    print("\n📫 Creating Receivers...")
    
    receivers_data = [
        ("critical-alerts", 
         [{"to": "oncall@example.com"}],
         [{"channel": "#alerts-critical", "webhook_url": "https://hooks.slack.com/..."}],
         [{"service_key": "abc123"}]),
        ("warning-alerts",
         [{"to": "team@example.com"}],
         [{"channel": "#alerts-warning"}],
         []),
        ("info-alerts",
         [{"to": "info@example.com"}],
         [],
         [])
    ]
    
    receivers = []
    for name, email_cfg, slack_cfg, pd_cfg in receivers_data:
        receiver = await platform.create_receiver(name, email_cfg, slack_cfg, pd_cfg)
        receivers.append(receiver)
        print(f"  📫 {name}")
        
    # Create Routes
    print("\n🛤️ Creating Routes...")
    
    routes_data = [
        ("critical-alerts", {"severity": "critical"}, ["alertname", "service"]),
        ("critical-alerts", {"severity": "error"}, ["alertname", "service"]),
        ("warning-alerts", {"severity": "warning"}, ["alertname"]),
        ("info-alerts", {"severity": "info"}, ["alertname"])
    ]
    
    for receiver, match, group_by in routes_data:
        await platform.create_route(receiver, match, group_by=group_by)
        severity = match.get("severity", "any")
        print(f"  🛤️ {severity} → {receiver}")
        
    # Create Inhibition Rules
    print("\n🚫 Creating Inhibition Rules...")
    
    inhibition_data = [
        ({"severity": "critical"}, {"severity": "warning"}, ["alertname", "service"]),
        ({"alertname": "ServiceDown"}, {"alertname": "HighLatency"}, ["service"])
    ]
    
    for source, target, equal in inhibition_data:
        await platform.create_inhibition_rule(source, target, equal)
        
    print(f"  🚫 Created {len(platform.inhibition_rules)} inhibition rules")
    
    # Create Silences
    print("\n🔇 Creating Silences...")
    
    now = datetime.now()
    silences_data = [
        ([{"name": "alertname", "value": "HighCPU"}, {"name": "service", "value": "test-service"}],
         now, now + timedelta(hours=2), "Planned maintenance", users[0].user_id),
        ([{"name": "environment", "value": "staging"}],
         now, now + timedelta(hours=4), "Staging environment issues", users[1].user_id)
    ]
    
    for matchers, start, end, comment, user in silences_data:
        silence = await platform.create_silence(matchers, start, end, comment, user)
        print(f"  🔇 {comment[:30]}... (until {end.strftime('%H:%M')})")
        
    # Generate Alerts
    print("\n🚨 Generating Alerts...")
    
    alerts_data = [
        ({"alertname": "HighCPU", "service": "api-gateway", "severity": "critical", "instance": "api-gateway-1"}, AlertSeverity.CRITICAL),
        ({"alertname": "HighCPU", "service": "order-service", "severity": "warning", "instance": "order-service-1"}, AlertSeverity.WARNING),
        ({"alertname": "HighMemory", "service": "payment-service", "severity": "warning", "instance": "payment-service-1"}, AlertSeverity.WARNING),
        ({"alertname": "ServiceDown", "service": "inventory-service", "severity": "critical", "instance": "inventory-service-1"}, AlertSeverity.CRITICAL),
        ({"alertname": "HighLatency", "service": "api-gateway", "severity": "error", "instance": "api-gateway-2"}, AlertSeverity.ERROR),
        ({"alertname": "DatabaseConnectionError", "service": "user-service", "severity": "critical", "instance": "postgres-1"}, AlertSeverity.CRITICAL),
        ({"alertname": "DiskSpaceLow", "service": "analytics-service", "severity": "warning", "instance": "analytics-1"}, AlertSeverity.WARNING),
        ({"alertname": "CertificateExpiring", "service": "api-gateway", "severity": "info", "instance": "api-gateway-1"}, AlertSeverity.INFO),
        ({"alertname": "HighErrorRate", "service": "payment-service", "severity": "error", "instance": "payment-service-2"}, AlertSeverity.ERROR),
        ({"alertname": "KafkaLag", "service": "notification-service", "severity": "warning", "instance": "kafka-1"}, AlertSeverity.WARNING)
    ]
    
    alerts = []
    for labels, severity in alerts_data:
        alert = await platform.create_alert(
            labels,
            {"summary": f"{labels['alertname']} on {labels['service']}", "description": f"Alert triggered for {labels['instance']}"},
            severity
        )
        alerts.append(alert)
        
    print(f"  🚨 Generated {len(alerts)} alerts")
    
    # Send Notifications
    print("\n📤 Sending Notifications...")
    
    for group in list(platform.alert_groups.values())[:5]:
        for channel in [NotificationChannel.SLACK, NotificationChannel.EMAIL]:
            await platform.send_notification(group.group_id, group.receiver, channel)
            
    successful = sum(1 for n in platform.notifications.values() if n.status == "sent")
    print(f"  📤 Sent {successful}/{len(platform.notifications)} notifications")
    
    # Create Incidents
    print("\n🔥 Creating Incidents...")
    
    incidents_data = [
        ("High CPU on API Gateway", "Multiple instances showing high CPU utilization", IncidentPriority.P2, "api-gateway", [alerts[0].alert_id]),
        ("Inventory Service Down", "Service is unreachable", IncidentPriority.P1, "inventory-service", [alerts[3].alert_id]),
        ("Database Connection Issues", "Multiple connection errors reported", IncidentPriority.P1, "user-service", [alerts[5].alert_id]),
        ("Payment Processing Errors", "High error rate in payment service", IncidentPriority.P2, "payment-service", [alerts[8].alert_id])
    ]
    
    incidents = []
    for title, desc, priority, service, alert_ids in incidents_data:
        incident = await platform.create_incident(title, desc, priority, service, alert_ids, policies[0].policy_id)
        incidents.append(incident)
        print(f"  🔥 {priority.value.upper()}: {title}")
        
    # Acknowledge and Resolve Some Incidents
    print("\n✅ Processing Incidents...")
    
    # Acknowledge first incident
    await platform.acknowledge_incident(incidents[0].incident_id, users[0].user_id)
    print(f"  ✓ Acknowledged: {incidents[0].title}")
    
    # Escalate second incident
    await platform.escalate_incident(incidents[1].incident_id)
    print(f"  ⬆️ Escalated: {incidents[1].title}")
    
    # Resolve third incident
    await platform.acknowledge_incident(incidents[2].incident_id, users[1].user_id)
    await platform.resolve_incident(incidents[2].incident_id, "Database connection pool increased")
    print(f"  ✅ Resolved: {incidents[2].title}")
    
    # Resolve some alerts
    for alert in alerts[:3]:
        await platform.resolve_alert(alert.alert_id)
        
    # Collect Metrics
    metrics = await platform.collect_metrics()
    
    # Alerts Dashboard
    print("\n🚨 Active Alerts:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Alert Name                   │ Service              │ Severity    │ State      │ Started At                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for alert in sorted(alerts, key=lambda x: x.severity.value, reverse=True):
        name = alert.labels.get("alertname", "")[:28].ljust(28)
        service = alert.labels.get("service", "")[:20].ljust(20)
        severity = alert.severity.value[:11].ljust(11)
        state = alert.state.value[:10].ljust(10)
        started = alert.starts_at.strftime("%H:%M:%S")
        started = started.ljust(221)
        
        print(f"  │ {name} │ {service} │ {severity} │ {state} │ {started} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Incidents Dashboard
    print("\n🔥 Incidents:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ ID          │ Priority │ Title                                   │ Service              │ Status         │ Assignee                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for inc in incidents:
        inc_id = inc.incident_id[:11].ljust(11)
        priority = inc.priority.value.upper().ljust(8)
        title = inc.title[:39].ljust(39)
        service = inc.service[:20].ljust(20)
        status = inc.status.value[:14].ljust(14)
        assignee = inc.assignee[:10] if inc.assignee else "Unassigned"
        assignee = assignee.ljust(179)
        
        print(f"  │ {inc_id} │ {priority} │ {title} │ {service} │ {status} │ {assignee} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # On-Call Dashboard
    print("\n📅 On-Call Status:")
    
    for schedule in schedules:
        print(f"  - {schedule.name}: {schedule.current_user[:20] if schedule.current_user else 'None'}")
        
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Total Alerts: {stats['total_alerts']} ({stats['firing_alerts']} firing)")
    print(f"  Alert Groups: {stats['total_groups']}")
    print(f"  Active Silences: {stats['active_silences']}/{stats['total_silences']}")
    print(f"  Notifications: {stats['total_notifications']}")
    print(f"  Open Incidents: {stats['open_incidents']}/{stats['total_incidents']}")
    print(f"  Users: {stats['total_users']}")
    print(f"  Teams: {stats['total_teams']}")
    
    # Alert Severity Distribution
    print("\n  Alerts by Severity:")
    for severity, count in stats["alerts_by_severity"].items():
        if count > 0:
            bar = "█" * count
            print(f"    {severity.upper():10s} │ {bar} ({count})")
            
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                       Alert Manager Platform                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Alerts:                  {stats['total_alerts']:>12}                      │")
    print(f"│ Firing Alerts:                 {stats['firing_alerts']:>12}                      │")
    print(f"│ Alert Groups:                  {stats['total_groups']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Routes:                        {stats['total_routes']:>12}                      │")
    print(f"│ Receivers:                     {stats['total_receivers']:>12}                      │")
    print(f"│ Active Silences:               {stats['active_silences']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Notifications:           {stats['total_notifications']:>12}                      │")
    print(f"│ Escalation Policies:           {stats['escalation_policies']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Incidents:               {stats['total_incidents']:>12}                      │")
    print(f"│ Open Incidents:                {stats['open_incidents']:>12}                      │")
    print(f"│ Avg Resolution (min):          {metrics.avg_resolution_time_minutes:>12.1f}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Alert Manager Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
