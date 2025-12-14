#!/usr/bin/env python3
"""
Server Init - Iteration 278: Alert Manager Platform
Платформа управления оповещениями

Функционал:
- Alert Rules - правила оповещений
- Alert Routing - маршрутизация оповещений
- Alert Grouping - группировка оповещений
- Alert Silencing - заглушение оповещений
- Alert Inhibition - подавление оповещений
- Notification Channels - каналы уведомлений
- Escalation Policies - политики эскалации
- On-Call Management - управление дежурствами
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid


class AlertSeverity(Enum):
    """Серьезность оповещения"""
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


class AlertState(Enum):
    """Состояние оповещения"""
    PENDING = "pending"
    FIRING = "firing"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


class NotificationType(Enum):
    """Тип уведомления"""
    EMAIL = "email"
    SLACK = "slack"
    PAGERDUTY = "pagerduty"
    WEBHOOK = "webhook"
    SMS = "sms"
    TELEGRAM = "telegram"


class EscalationAction(Enum):
    """Действие эскалации"""
    NOTIFY = "notify"
    PAGE = "page"
    CALL = "call"
    ESCALATE = "escalate"


@dataclass
class AlertLabel:
    """Метка оповещения"""
    name: str
    value: str


@dataclass
class AlertAnnotation:
    """Аннотация оповещения"""
    name: str
    value: str


@dataclass
class AlertRule:
    """Правило оповещения"""
    rule_id: str
    name: str
    
    # Condition
    expression: str = ""  # PromQL-like
    
    # Duration
    for_duration_seconds: int = 60
    
    # Severity
    severity: AlertSeverity = AlertSeverity.WARNING
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Annotations
    summary: str = ""
    description: str = ""
    runbook_url: str = ""
    
    # State
    active: bool = True
    last_evaluation: Optional[datetime] = None


@dataclass
class Alert:
    """Оповещение"""
    alert_id: str
    rule_id: str
    
    # Name
    name: str = ""
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Annotations
    annotations: Dict[str, str] = field(default_factory=dict)
    
    # Severity
    severity: AlertSeverity = AlertSeverity.WARNING
    
    # State
    state: AlertState = AlertState.PENDING
    
    # Timing
    starts_at: datetime = field(default_factory=datetime.now)
    ends_at: Optional[datetime] = None
    
    # Notifications
    notifications_sent: int = 0
    last_notification: Optional[datetime] = None
    
    # Fingerprint
    fingerprint: str = ""


@dataclass
class AlertGroup:
    """Группа оповещений"""
    group_id: str
    group_key: str
    
    # Alerts
    alerts: List[Alert] = field(default_factory=list)
    
    # Labels
    common_labels: Dict[str, str] = field(default_factory=dict)
    
    # State
    active: bool = True
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class NotificationChannel:
    """Канал уведомлений"""
    channel_id: str
    name: str
    
    # Type
    notification_type: NotificationType = NotificationType.EMAIL
    
    # Config
    config: Dict[str, Any] = field(default_factory=dict)
    
    # State
    active: bool = True
    notifications_sent: int = 0
    last_sent: Optional[datetime] = None


@dataclass
class RouteRule:
    """Правило маршрутизации"""
    route_id: str
    name: str
    
    # Match
    match_labels: Dict[str, str] = field(default_factory=dict)
    match_regex: Dict[str, str] = field(default_factory=dict)
    
    # Receiver
    receiver: str = ""
    
    # Group by
    group_by: List[str] = field(default_factory=list)
    
    # Timing
    group_wait_seconds: int = 30
    group_interval_seconds: int = 300
    repeat_interval_seconds: int = 3600
    
    # Continue
    continue_route: bool = False
    
    # Children
    child_routes: List['RouteRule'] = field(default_factory=list)


@dataclass
class Silence:
    """Заглушение оповещений"""
    silence_id: str
    
    # Matchers
    matchers: Dict[str, str] = field(default_factory=dict)
    
    # Creator
    created_by: str = ""
    comment: str = ""
    
    # Timing
    starts_at: datetime = field(default_factory=datetime.now)
    ends_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=1))
    
    # State
    active: bool = True


@dataclass
class InhibitRule:
    """Правило подавления"""
    rule_id: str
    name: str
    
    # Source match (inhibiting alert)
    source_match: Dict[str, str] = field(default_factory=dict)
    
    # Target match (inhibited alert)
    target_match: Dict[str, str] = field(default_factory=dict)
    
    # Equal labels
    equal_labels: List[str] = field(default_factory=list)
    
    # Active
    active: bool = True


@dataclass
class EscalationLevel:
    """Уровень эскалации"""
    level: int
    
    # Delay
    delay_minutes: int = 0
    
    # Action
    action: EscalationAction = EscalationAction.NOTIFY
    
    # Targets
    targets: List[str] = field(default_factory=list)


@dataclass
class EscalationPolicy:
    """Политика эскалации"""
    policy_id: str
    name: str
    
    # Levels
    levels: List[EscalationLevel] = field(default_factory=list)
    
    # Repeat
    repeat_after_minutes: int = 60
    
    # Active
    active: bool = True


@dataclass
class OnCallSchedule:
    """Расписание дежурств"""
    schedule_id: str
    name: str
    
    # Rotation
    rotation_type: str = "weekly"  # daily, weekly
    
    # Participants
    participants: List[str] = field(default_factory=list)
    
    # Current
    current_on_call: str = ""
    
    # Timing
    start_time: datetime = field(default_factory=datetime.now)
    handoff_time: str = "09:00"  # HH:MM


class AlertManager:
    """Менеджер оповещений"""
    
    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.alerts: Dict[str, Alert] = {}
        self.groups: Dict[str, AlertGroup] = {}
        self.channels: Dict[str, NotificationChannel] = {}
        self.routes: List[RouteRule] = []
        self.silences: Dict[str, Silence] = {}
        self.inhibit_rules: Dict[str, InhibitRule] = {}
        self.escalation_policies: Dict[str, EscalationPolicy] = {}
        self.schedules: Dict[str, OnCallSchedule] = {}
        
    def create_rule(self, name: str,
                   expression: str,
                   severity: AlertSeverity = AlertSeverity.WARNING,
                   for_duration: int = 60) -> AlertRule:
        """Создание правила"""
        rule = AlertRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name=name,
            expression=expression,
            severity=severity,
            for_duration_seconds=for_duration
        )
        
        self.rules[name] = rule
        return rule
        
    def add_channel(self, name: str,
                   notification_type: NotificationType,
                   config: Dict[str, Any] = None) -> NotificationChannel:
        """Добавление канала"""
        channel = NotificationChannel(
            channel_id=f"channel_{uuid.uuid4().hex[:8]}",
            name=name,
            notification_type=notification_type,
            config=config or {}
        )
        
        self.channels[name] = channel
        return channel
        
    def add_route(self, name: str,
                 receiver: str,
                 match_labels: Dict[str, str] = None,
                 group_by: List[str] = None) -> RouteRule:
        """Добавление маршрута"""
        route = RouteRule(
            route_id=f"route_{uuid.uuid4().hex[:8]}",
            name=name,
            receiver=receiver,
            match_labels=match_labels or {},
            group_by=group_by or ["alertname"]
        )
        
        self.routes.append(route)
        return route
        
    def fire_alert(self, rule_name: str,
                  labels: Dict[str, str] = None,
                  annotations: Dict[str, str] = None) -> Alert:
        """Срабатывание оповещения"""
        rule = self.rules.get(rule_name)
        if not rule:
            return None
            
        labels = labels or {}
        labels["alertname"] = rule_name
        
        # Generate fingerprint
        fingerprint = self._generate_fingerprint(labels)
        
        # Check if alert already exists
        if fingerprint in self.alerts:
            alert = self.alerts[fingerprint]
            if alert.state == AlertState.RESOLVED:
                alert.state = AlertState.FIRING
                alert.starts_at = datetime.now()
                alert.ends_at = None
            return alert
            
        alert = Alert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            rule_id=rule.rule_id,
            name=rule_name,
            labels=labels,
            annotations=annotations or {},
            severity=rule.severity,
            state=AlertState.FIRING,
            fingerprint=fingerprint
        )
        
        self.alerts[fingerprint] = alert
        
        # Check silences
        if self._is_silenced(alert):
            alert.state = AlertState.SUPPRESSED
            return alert
            
        # Check inhibitions
        if self._is_inhibited(alert):
            alert.state = AlertState.SUPPRESSED
            return alert
            
        # Group alert
        self._group_alert(alert)
        
        # Route and notify
        self._route_alert(alert)
        
        return alert
        
    def resolve_alert(self, fingerprint: str):
        """Разрешение оповещения"""
        alert = self.alerts.get(fingerprint)
        if alert:
            alert.state = AlertState.RESOLVED
            alert.ends_at = datetime.now()
            
    def _generate_fingerprint(self, labels: Dict[str, str]) -> str:
        """Генерация fingerprint"""
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return uuid.uuid5(uuid.NAMESPACE_DNS, label_str).hex[:16]
        
    def _is_silenced(self, alert: Alert) -> bool:
        """Проверка заглушения"""
        now = datetime.now()
        
        for silence in self.silences.values():
            if not silence.active:
                continue
            if silence.starts_at > now or silence.ends_at < now:
                continue
                
            match = all(
                alert.labels.get(k) == v 
                for k, v in silence.matchers.items()
            )
            
            if match:
                return True
                
        return False
        
    def _is_inhibited(self, alert: Alert) -> bool:
        """Проверка подавления"""
        for rule in self.inhibit_rules.values():
            if not rule.active:
                continue
                
            # Check if target matches
            target_match = all(
                alert.labels.get(k) == v 
                for k, v in rule.target_match.items()
            )
            
            if not target_match:
                continue
                
            # Check if source alert exists
            for other in self.alerts.values():
                if other.state != AlertState.FIRING:
                    continue
                    
                source_match = all(
                    other.labels.get(k) == v 
                    for k, v in rule.source_match.items()
                )
                
                if not source_match:
                    continue
                    
                # Check equal labels
                equal_match = all(
                    alert.labels.get(l) == other.labels.get(l)
                    for l in rule.equal_labels
                )
                
                if equal_match:
                    return True
                    
        return False
        
    def _group_alert(self, alert: Alert):
        """Группировка оповещения"""
        # Find matching route
        route = self._find_route(alert)
        if not route:
            return
            
        # Generate group key
        group_labels = {k: alert.labels.get(k, "") for k in route.group_by}
        group_key = ",".join(f"{k}={v}" for k, v in sorted(group_labels.items()))
        
        if group_key not in self.groups:
            self.groups[group_key] = AlertGroup(
                group_id=f"group_{uuid.uuid4().hex[:8]}",
                group_key=group_key,
                common_labels=group_labels
            )
            
        self.groups[group_key].alerts.append(alert)
        
    def _find_route(self, alert: Alert) -> Optional[RouteRule]:
        """Поиск маршрута"""
        for route in self.routes:
            if self._route_matches(route, alert):
                return route
        return self.routes[0] if self.routes else None
        
    def _route_matches(self, route: RouteRule, alert: Alert) -> bool:
        """Проверка соответствия маршруту"""
        for k, v in route.match_labels.items():
            if alert.labels.get(k) != v:
                return False
        return True
        
    def _route_alert(self, alert: Alert):
        """Маршрутизация оповещения"""
        route = self._find_route(alert)
        if not route:
            return
            
        channel = self.channels.get(route.receiver)
        if channel:
            self._send_notification(alert, channel)
            
    def _send_notification(self, alert: Alert, channel: NotificationChannel):
        """Отправка уведомления"""
        channel.notifications_sent += 1
        channel.last_sent = datetime.now()
        
        alert.notifications_sent += 1
        alert.last_notification = datetime.now()
        
    def create_silence(self, matchers: Dict[str, str],
                      duration_hours: int = 1,
                      created_by: str = "",
                      comment: str = "") -> Silence:
        """Создание заглушения"""
        silence = Silence(
            silence_id=f"silence_{uuid.uuid4().hex[:8]}",
            matchers=matchers,
            created_by=created_by,
            comment=comment,
            ends_at=datetime.now() + timedelta(hours=duration_hours)
        )
        
        self.silences[silence.silence_id] = silence
        
        # Update affected alerts
        for alert in self.alerts.values():
            if alert.state == AlertState.FIRING:
                if self._is_silenced(alert):
                    alert.state = AlertState.SUPPRESSED
                    
        return silence
        
    def expire_silence(self, silence_id: str):
        """Истечение заглушения"""
        silence = self.silences.get(silence_id)
        if silence:
            silence.active = False
            silence.ends_at = datetime.now()
            
    def add_inhibit_rule(self, name: str,
                        source_match: Dict[str, str],
                        target_match: Dict[str, str],
                        equal_labels: List[str] = None) -> InhibitRule:
        """Добавление правила подавления"""
        rule = InhibitRule(
            rule_id=f"inhibit_{uuid.uuid4().hex[:8]}",
            name=name,
            source_match=source_match,
            target_match=target_match,
            equal_labels=equal_labels or []
        )
        
        self.inhibit_rules[name] = rule
        return rule
        
    def create_escalation_policy(self, name: str,
                                levels: List[Dict[str, Any]] = None) -> EscalationPolicy:
        """Создание политики эскалации"""
        policy = EscalationPolicy(
            policy_id=f"escalation_{uuid.uuid4().hex[:8]}",
            name=name,
            levels=[
                EscalationLevel(
                    level=l.get("level", i),
                    delay_minutes=l.get("delay", 0),
                    action=EscalationAction(l.get("action", "notify")),
                    targets=l.get("targets", [])
                )
                for i, l in enumerate(levels or [])
            ]
        )
        
        self.escalation_policies[name] = policy
        return policy
        
    def create_schedule(self, name: str,
                       participants: List[str],
                       rotation_type: str = "weekly") -> OnCallSchedule:
        """Создание расписания"""
        schedule = OnCallSchedule(
            schedule_id=f"schedule_{uuid.uuid4().hex[:8]}",
            name=name,
            rotation_type=rotation_type,
            participants=participants,
            current_on_call=participants[0] if participants else ""
        )
        
        self.schedules[name] = schedule
        return schedule
        
    def get_on_call(self, schedule_name: str) -> Optional[str]:
        """Получение текущего дежурного"""
        schedule = self.schedules.get(schedule_name)
        if schedule:
            return schedule.current_on_call
        return None
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        firing = sum(1 for a in self.alerts.values() if a.state == AlertState.FIRING)
        suppressed = sum(1 for a in self.alerts.values() if a.state == AlertState.SUPPRESSED)
        resolved = sum(1 for a in self.alerts.values() if a.state == AlertState.RESOLVED)
        
        severity_counts = {}
        for alert in self.alerts.values():
            if alert.state == AlertState.FIRING:
                severity_counts[alert.severity.name] = severity_counts.get(alert.severity.name, 0) + 1
                
        return {
            "total_alerts": len(self.alerts),
            "firing": firing,
            "suppressed": suppressed,
            "resolved": resolved,
            "rules": len(self.rules),
            "channels": len(self.channels),
            "routes": len(self.routes),
            "silences": len([s for s in self.silences.values() if s.active]),
            "groups": len(self.groups),
            "severity_counts": severity_counts
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 278: Alert Manager Platform")
    print("=" * 60)
    
    manager = AlertManager()
    print("✓ Alert Manager created")
    
    # Add notification channels
    print("\n📢 Adding Notification Channels...")
    
    channels_config = [
        ("slack-ops", NotificationType.SLACK, {"channel": "#ops-alerts", "webhook_url": "https://..."}),
        ("pagerduty", NotificationType.PAGERDUTY, {"service_key": "xxx", "severity": "critical"}),
        ("email-team", NotificationType.EMAIL, {"to": "team@example.com", "smtp": "smtp.example.com"}),
        ("telegram-critical", NotificationType.TELEGRAM, {"chat_id": "-100123", "bot_token": "xxx"}),
    ]
    
    for name, ntype, config in channels_config:
        channel = manager.add_channel(name, ntype, config)
        print(f"  📢 {name}: {ntype.value}")
        
    # Add routes
    print("\n🔀 Adding Routes...")
    
    manager.add_route(
        "critical-alerts",
        "pagerduty",
        match_labels={"severity": "critical"},
        group_by=["alertname", "service"]
    )
    
    manager.add_route(
        "warning-alerts",
        "slack-ops",
        match_labels={"severity": "warning"},
        group_by=["alertname"]
    )
    
    manager.add_route(
        "default",
        "email-team",
        group_by=["alertname"]
    )
    
    print(f"  Added {len(manager.routes)} routes")
    
    # Create alert rules
    print("\n📋 Creating Alert Rules...")
    
    rules_config = [
        ("HighCPUUsage", "cpu_usage > 80", AlertSeverity.WARNING, 60),
        ("CriticalCPUUsage", "cpu_usage > 95", AlertSeverity.CRITICAL, 30),
        ("HighMemoryUsage", "memory_usage > 85", AlertSeverity.WARNING, 120),
        ("ServiceDown", "up == 0", AlertSeverity.CRITICAL, 60),
        ("HighLatency", "latency_p99 > 1000", AlertSeverity.WARNING, 300),
        ("HighErrorRate", "error_rate > 5", AlertSeverity.ERROR, 60),
        ("DiskSpaceLow", "disk_usage > 90", AlertSeverity.WARNING, 300),
        ("DiskSpaceCritical", "disk_usage > 95", AlertSeverity.CRITICAL, 60),
    ]
    
    for name, expr, severity, duration in rules_config:
        rule = manager.create_rule(name, expr, severity, duration)
        rule.summary = f"{name} alert"
        rule.description = f"Alert triggered by: {expr}"
        print(f"  📋 {name}: {severity.name}")
        
    # Add inhibit rules
    print("\n🚫 Adding Inhibit Rules...")
    
    manager.add_inhibit_rule(
        "critical-inhibits-warning",
        source_match={"severity": "critical"},
        target_match={"severity": "warning"},
        equal_labels=["service"]
    )
    
    manager.add_inhibit_rule(
        "service-down-inhibits-all",
        source_match={"alertname": "ServiceDown"},
        target_match={},
        equal_labels=["service"]
    )
    
    print(f"  Added {len(manager.inhibit_rules)} inhibit rules")
    
    # Create escalation policies
    print("\n📈 Creating Escalation Policies...")
    
    manager.create_escalation_policy("critical-escalation", [
        {"level": 1, "delay": 0, "action": "notify", "targets": ["slack-ops"]},
        {"level": 2, "delay": 15, "action": "page", "targets": ["pagerduty"]},
        {"level": 3, "delay": 30, "action": "call", "targets": ["phone-oncall"]},
    ])
    
    manager.create_escalation_policy("standard-escalation", [
        {"level": 1, "delay": 0, "action": "notify", "targets": ["email-team"]},
        {"level": 2, "delay": 60, "action": "notify", "targets": ["slack-ops"]},
    ])
    
    print(f"  Created {len(manager.escalation_policies)} policies")
    
    # Create on-call schedules
    print("\n📅 Creating On-Call Schedules...")
    
    manager.create_schedule(
        "primary-oncall",
        ["alice@example.com", "bob@example.com", "charlie@example.com"],
        "weekly"
    )
    
    manager.create_schedule(
        "secondary-oncall",
        ["dave@example.com", "eve@example.com"],
        "daily"
    )
    
    print(f"  Created {len(manager.schedules)} schedules")
    
    # Fire alerts
    print("\n🔥 Firing Alerts...")
    
    alerts_to_fire = [
        ("HighCPUUsage", {"service": "api-gateway", "instance": "node-1", "severity": "warning"}),
        ("CriticalCPUUsage", {"service": "api-gateway", "instance": "node-1", "severity": "critical"}),
        ("HighMemoryUsage", {"service": "user-service", "instance": "node-2", "severity": "warning"}),
        ("ServiceDown", {"service": "payment-service", "instance": "node-3", "severity": "critical"}),
        ("HighLatency", {"service": "order-service", "instance": "node-1", "severity": "warning"}),
        ("HighErrorRate", {"service": "inventory-service", "instance": "node-2", "severity": "error"}),
        ("DiskSpaceLow", {"service": "database", "instance": "db-1", "severity": "warning"}),
    ]
    
    for rule_name, labels in alerts_to_fire:
        alert = manager.fire_alert(rule_name, labels, {"dashboard": "http://grafana/..."})
        if alert:
            status = "🔥" if alert.state == AlertState.FIRING else "🚫"
            print(f"  {status} {alert.name}: {alert.state.value}")
            
    # Create silences
    print("\n🔇 Creating Silences...")
    
    silence = manager.create_silence(
        {"service": "database"},
        duration_hours=2,
        created_by="admin@example.com",
        comment="Planned maintenance"
    )
    print(f"  🔇 Silenced service=database for 2 hours")
    
    # Display alerts
    print("\n🚨 Active Alerts:")
    
    print("\n  ┌────────────────────────┬─────────────┬─────────────────┬─────────────┐")
    print("  │ Alert                  │ Severity    │ Service         │ State       │")
    print("  ├────────────────────────┼─────────────┼─────────────────┼─────────────┤")
    
    for alert in manager.alerts.values():
        name = alert.name[:22].ljust(22)
        severity = alert.severity.name[:11].ljust(11)
        service = alert.labels.get("service", "N/A")[:15].ljust(15)
        state = alert.state.value[:11].ljust(11)
        
        print(f"  │ {name} │ {severity} │ {service} │ {state} │")
        
    print("  └────────────────────────┴─────────────┴─────────────────┴─────────────┘")
    
    # Display alert groups
    print("\n📦 Alert Groups:")
    
    for group in manager.groups.values():
        labels_str = ", ".join(f"{k}={v}" for k, v in group.common_labels.items())
        print(f"\n  📦 {labels_str}")
        
        for alert in group.alerts[:3]:
            severity_icon = {
                AlertSeverity.INFO: "ℹ️",
                AlertSeverity.WARNING: "⚠️",
                AlertSeverity.ERROR: "❌",
                AlertSeverity.CRITICAL: "🚨"
            }.get(alert.severity, "❓")
            
            print(f"     {severity_icon} {alert.name} ({alert.state.value})")
            
    # Display notification channels status
    print("\n📢 Channel Statistics:")
    
    for channel in manager.channels.values():
        status = "🟢" if channel.active else "🔴"
        print(f"  {status} {channel.name}: {channel.notifications_sent} notifications")
        
    # Display silences
    print("\n🔇 Active Silences:")
    
    for silence in manager.silences.values():
        if silence.active:
            matchers_str = ", ".join(f"{k}={v}" for k, v in silence.matchers.items())
            remaining = (silence.ends_at - datetime.now()).total_seconds() / 3600
            print(f"  🔇 {matchers_str} - {remaining:.1f}h remaining")
            print(f"     Created by: {silence.created_by}")
            print(f"     Comment: {silence.comment}")
            
    # Display escalation policies
    print("\n📈 Escalation Policies:")
    
    for policy in manager.escalation_policies.values():
        print(f"\n  📈 {policy.name}:")
        for level in policy.levels:
            targets = ", ".join(level.targets)
            print(f"     Level {level.level}: +{level.delay_minutes}m -> {level.action.value} -> {targets}")
            
    # Display on-call schedules
    print("\n📅 On-Call Schedules:")
    
    for schedule in manager.schedules.values():
        print(f"\n  📅 {schedule.name} ({schedule.rotation_type}):")
        print(f"     Current: {schedule.current_on_call}")
        print(f"     Rotation: {', '.join(schedule.participants)}")
        
    # Display inhibit rules
    print("\n🚫 Inhibit Rules:")
    
    for rule in manager.inhibit_rules.values():
        source = ", ".join(f"{k}={v}" for k, v in rule.source_match.items())
        target = ", ".join(f"{k}={v}" for k, v in rule.target_match.items()) or "all"
        equal = ", ".join(rule.equal_labels) if rule.equal_labels else "none"
        print(f"  🚫 {rule.name}:")
        print(f"     Source: {source} inhibits Target: {target}")
        print(f"     Equal labels: {equal}")
        
    # Severity distribution
    print("\n📊 Severity Distribution:")
    
    stats = manager.get_statistics()
    severity_counts = stats.get("severity_counts", {})
    
    for severity in AlertSeverity:
        count = severity_counts.get(severity.name, 0)
        bar = "█" * count + "░" * (10 - count)
        
        severity_icon = {
            AlertSeverity.INFO: "ℹ️",
            AlertSeverity.WARNING: "⚠️",
            AlertSeverity.ERROR: "❌",
            AlertSeverity.CRITICAL: "🚨"
        }.get(severity, "❓")
        
        print(f"  {severity_icon} {severity.name:10s}: [{bar}] {count}")
        
    # Statistics
    print("\n📊 Alert Manager Statistics:")
    
    print(f"\n  Total Alerts: {stats['total_alerts']}")
    print(f"  Firing: {stats['firing']}")
    print(f"  Suppressed: {stats['suppressed']}")
    print(f"  Resolved: {stats['resolved']}")
    print(f"  Rules: {stats['rules']}")
    print(f"  Channels: {stats['channels']}")
    print(f"  Routes: {stats['routes']}")
    print(f"  Active Silences: {stats['silences']}")
    print(f"  Alert Groups: {stats['groups']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                     Alert Manager Dashboard                         │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Firing Alerts:                 {stats['firing']:>12}                        │")
    print(f"│ Suppressed:                    {stats['suppressed']:>12}                        │")
    print(f"│ Resolved:                      {stats['resolved']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Alert Rules:                   {stats['rules']:>12}                        │")
    print(f"│ Notification Channels:         {stats['channels']:>12}                        │")
    print(f"│ Active Silences:               {stats['silences']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Alert Manager Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
