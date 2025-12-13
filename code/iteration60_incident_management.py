#!/usr/bin/env python3
"""
Server Init - Iteration 60: Incident Management & On-Call Platform
Управление инцидентами и дежурствами

Функционал:
- Incident Lifecycle - жизненный цикл инцидентов
- On-Call Schedules - расписания дежурств
- Escalation Policies - политики эскалации
- Alert Routing - маршрутизация оповещений
- War Room - комната координации
- Post-Mortem - анализ после инцидента
- Runbooks - рабочие инструкции
- SLA Tracking - отслеживание SLA
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from collections import defaultdict
import uuid
import random


class IncidentSeverity(Enum):
    """Критичность инцидента"""
    SEV1 = "sev1"  # Critical
    SEV2 = "sev2"  # High
    SEV3 = "sev3"  # Medium
    SEV4 = "sev4"  # Low
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
    """Статус оповещения"""
    PENDING = "pending"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    ESCALATED = "escalated"
    RESOLVED = "resolved"


class NotificationChannel(Enum):
    """Канал оповещения"""
    EMAIL = "email"
    SMS = "sms"
    PHONE = "phone"
    SLACK = "slack"
    TEAMS = "teams"
    PAGERDUTY = "pagerduty"
    WEBHOOK = "webhook"


class EscalationRuleType(Enum):
    """Тип правила эскалации"""
    TIMEOUT = "timeout"
    NO_ACK = "no_ack"
    SEVERITY_UPGRADE = "severity_upgrade"
    MANUAL = "manual"


@dataclass
class OnCallUser:
    """Дежурный пользователь"""
    user_id: str
    name: str
    email: str
    
    # Контакты
    phone: str = ""
    slack_id: str = ""
    
    # Настройки
    notification_preferences: Dict[str, List[NotificationChannel]] = field(default_factory=dict)
    
    # Временная зона
    timezone: str = "UTC"


@dataclass
class OnCallSchedule:
    """Расписание дежурств"""
    schedule_id: str
    name: str
    
    # Команда
    team_id: str = ""
    
    # Участники
    participants: List[str] = field(default_factory=list)  # User IDs
    
    # Ротация
    rotation_type: str = "weekly"  # daily, weekly, custom
    rotation_start: datetime = field(default_factory=datetime.now)
    
    # Переопределения
    overrides: List[Dict[str, Any]] = field(default_factory=list)
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class EscalationPolicy:
    """Политика эскалации"""
    policy_id: str
    name: str
    
    # Уровни эскалации
    levels: List[Dict[str, Any]] = field(default_factory=list)
    # Each level: {"timeout_minutes": 15, "targets": [user_ids/schedule_ids]}
    
    # Повтор
    repeat_enabled: bool = True
    repeat_limit: int = 3
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AlertRule:
    """Правило оповещения"""
    rule_id: str
    name: str
    
    # Условия
    conditions: Dict[str, Any] = field(default_factory=dict)
    # e.g., {"service": "api", "severity": ["sev1", "sev2"]}
    
    # Действия
    escalation_policy_id: str = ""
    notification_channels: List[NotificationChannel] = field(default_factory=list)
    
    # Трансформации
    transformations: Dict[str, Any] = field(default_factory=dict)
    
    # Статус
    enabled: bool = True


@dataclass
class Alert:
    """Оповещение"""
    alert_id: str
    
    # Источник
    source: str = ""
    source_id: str = ""
    
    # Детали
    title: str = ""
    description: str = ""
    severity: IncidentSeverity = IncidentSeverity.SEV3
    
    # Статус
    status: AlertStatus = AlertStatus.PENDING
    
    # Связи
    incident_id: Optional[str] = None
    
    # Время
    triggered_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


@dataclass
class Incident:
    """Инцидент"""
    incident_id: str
    title: str
    
    # Детали
    description: str = ""
    severity: IncidentSeverity = IncidentSeverity.SEV3
    
    # Статус
    status: IncidentStatus = IncidentStatus.TRIGGERED
    
    # Ответственные
    commander_id: str = ""  # Incident Commander
    assignees: List[str] = field(default_factory=list)
    
    # Связи
    alerts: List[str] = field(default_factory=list)  # Alert IDs
    services: List[str] = field(default_factory=list)  # Affected services
    
    # Timeline
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    # Метрики
    time_to_acknowledge: Optional[float] = None  # minutes
    time_to_resolve: Optional[float] = None  # minutes
    
    # Post-mortem
    postmortem_id: Optional[str] = None


@dataclass
class PostMortem:
    """Анализ после инцидента"""
    postmortem_id: str
    incident_id: str
    
    # Детали
    title: str = ""
    summary: str = ""
    
    # Timeline
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    
    # Root Cause Analysis
    root_cause: str = ""
    contributing_factors: List[str] = field(default_factory=list)
    
    # Impact
    impact: Dict[str, Any] = field(default_factory=dict)
    # e.g., {"users_affected": 1000, "revenue_loss": 5000}
    
    # Action Items
    action_items: List[Dict[str, Any]] = field(default_factory=list)
    # e.g., {"description": "...", "owner": "...", "due_date": "...", "status": "open"}
    
    # Статус
    status: str = "draft"  # draft, in_review, published
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    published_at: Optional[datetime] = None


@dataclass
class Runbook:
    """Рабочая инструкция"""
    runbook_id: str
    name: str
    
    # Категория
    category: str = ""
    
    # Связи
    services: List[str] = field(default_factory=list)
    alert_types: List[str] = field(default_factory=list)
    
    # Содержимое
    steps: List[Dict[str, Any]] = field(default_factory=list)
    # e.g., {"step": 1, "description": "...", "command": "...", "expected_result": "..."}
    
    # Версия
    version: str = "1.0"
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class SLA:
    """Соглашение об уровне обслуживания"""
    sla_id: str
    name: str
    
    # Цели по критичности
    targets: Dict[str, Dict[str, int]] = field(default_factory=dict)
    # e.g., {"sev1": {"acknowledge": 5, "resolve": 60}, ...}
    
    # Бизнес-часы
    business_hours_only: bool = False
    business_hours: Dict[str, Any] = field(default_factory=dict)


class OnCallManager:
    """Менеджер дежурств"""
    
    def __init__(self):
        self.users: Dict[str, OnCallUser] = {}
        self.schedules: Dict[str, OnCallSchedule] = {}
        
    def add_user(self, name: str, email: str, **kwargs) -> OnCallUser:
        """Добавление пользователя"""
        user = OnCallUser(
            user_id=f"user_{uuid.uuid4().hex[:8]}",
            name=name,
            email=email,
            **kwargs
        )
        
        self.users[user.user_id] = user
        return user
        
    def create_schedule(self, name: str, participants: List[str],
                         rotation_type: str = "weekly", **kwargs) -> OnCallSchedule:
        """Создание расписания"""
        schedule = OnCallSchedule(
            schedule_id=f"sched_{uuid.uuid4().hex[:8]}",
            name=name,
            participants=participants,
            rotation_type=rotation_type,
            **kwargs
        )
        
        self.schedules[schedule.schedule_id] = schedule
        return schedule
        
    def get_current_oncall(self, schedule_id: str) -> Optional[OnCallUser]:
        """Получение текущего дежурного"""
        schedule = self.schedules.get(schedule_id)
        
        if not schedule or not schedule.participants:
            return None
            
        # Проверяем overrides
        now = datetime.now()
        for override in schedule.overrides:
            if override["start"] <= now <= override["end"]:
                return self.users.get(override["user_id"])
                
        # Рассчитываем по ротации
        if schedule.rotation_type == "daily":
            days_since_start = (now - schedule.rotation_start).days
            index = days_since_start % len(schedule.participants)
        elif schedule.rotation_type == "weekly":
            weeks_since_start = (now - schedule.rotation_start).days // 7
            index = weeks_since_start % len(schedule.participants)
        else:
            index = 0
            
        user_id = schedule.participants[index]
        return self.users.get(user_id)
        
    def add_override(self, schedule_id: str, user_id: str,
                      start: datetime, end: datetime):
        """Добавление переопределения"""
        schedule = self.schedules.get(schedule_id)
        
        if schedule:
            schedule.overrides.append({
                "user_id": user_id,
                "start": start,
                "end": end
            })


class EscalationManager:
    """Менеджер эскалации"""
    
    def __init__(self, oncall_manager: OnCallManager):
        self.oncall_manager = oncall_manager
        self.policies: Dict[str, EscalationPolicy] = {}
        self.active_escalations: Dict[str, Dict[str, Any]] = {}
        
    def create_policy(self, name: str, levels: List[Dict[str, Any]],
                       **kwargs) -> EscalationPolicy:
        """Создание политики"""
        policy = EscalationPolicy(
            policy_id=f"policy_{uuid.uuid4().hex[:8]}",
            name=name,
            levels=levels,
            **kwargs
        )
        
        self.policies[policy.policy_id] = policy
        return policy
        
    async def start_escalation(self, policy_id: str, alert_id: str) -> List[str]:
        """Запуск эскалации"""
        policy = self.policies.get(policy_id)
        
        if not policy or not policy.levels:
            return []
            
        # Начинаем с первого уровня
        self.active_escalations[alert_id] = {
            "policy_id": policy_id,
            "current_level": 0,
            "repeat_count": 0,
            "started_at": datetime.now()
        }
        
        return await self._notify_level(policy, 0)
        
    async def escalate(self, alert_id: str) -> List[str]:
        """Эскалация на следующий уровень"""
        escalation = self.active_escalations.get(alert_id)
        
        if not escalation:
            return []
            
        policy = self.policies.get(escalation["policy_id"])
        
        if not policy:
            return []
            
        next_level = escalation["current_level"] + 1
        
        if next_level >= len(policy.levels):
            # Проверяем повтор
            if policy.repeat_enabled and escalation["repeat_count"] < policy.repeat_limit:
                escalation["current_level"] = 0
                escalation["repeat_count"] += 1
                return await self._notify_level(policy, 0)
            return []
            
        escalation["current_level"] = next_level
        return await self._notify_level(policy, next_level)
        
    async def _notify_level(self, policy: EscalationPolicy,
                             level: int) -> List[str]:
        """Оповещение уровня"""
        notified = []
        
        level_config = policy.levels[level]
        targets = level_config.get("targets", [])
        
        for target in targets:
            if target.startswith("sched_"):
                # Это расписание - получаем текущего дежурного
                user = self.oncall_manager.get_current_oncall(target)
                if user:
                    notified.append(user.user_id)
            else:
                # Это пользователь напрямую
                notified.append(target)
                
        return notified
        
    def stop_escalation(self, alert_id: str):
        """Остановка эскалации"""
        self.active_escalations.pop(alert_id, None)


class AlertRouter:
    """Маршрутизатор оповещений"""
    
    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        
    def add_rule(self, name: str, conditions: Dict[str, Any],
                  escalation_policy_id: str, **kwargs) -> AlertRule:
        """Добавление правила"""
        rule = AlertRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name=name,
            conditions=conditions,
            escalation_policy_id=escalation_policy_id,
            **kwargs
        )
        
        self.rules[rule.rule_id] = rule
        return rule
        
    def match_rules(self, alert: Alert) -> List[AlertRule]:
        """Поиск подходящих правил"""
        matching = []
        
        for rule in self.rules.values():
            if not rule.enabled:
                continue
                
            if self._matches_conditions(alert, rule.conditions):
                matching.append(rule)
                
        return matching
        
    def _matches_conditions(self, alert: Alert,
                             conditions: Dict[str, Any]) -> bool:
        """Проверка условий"""
        for key, value in conditions.items():
            if key == "source":
                if isinstance(value, list):
                    if alert.source not in value:
                        return False
                elif alert.source != value:
                    return False
                    
            elif key == "severity":
                if isinstance(value, list):
                    if alert.severity.value not in value:
                        return False
                elif alert.severity.value != value:
                    return False
                    
            elif key == "title_contains":
                if value.lower() not in alert.title.lower():
                    return False
                    
        return True


class NotificationService:
    """Сервис уведомлений"""
    
    def __init__(self):
        self.sent_notifications: List[Dict[str, Any]] = []
        
    async def notify(self, user: OnCallUser, alert: Alert,
                      channels: List[NotificationChannel] = None) -> List[str]:
        """Отправка уведомления"""
        channels = channels or [NotificationChannel.EMAIL, NotificationChannel.SLACK]
        sent = []
        
        for channel in channels:
            notification = {
                "id": f"notif_{uuid.uuid4().hex[:8]}",
                "user_id": user.user_id,
                "user_name": user.name,
                "alert_id": alert.alert_id,
                "channel": channel.value,
                "title": alert.title,
                "severity": alert.severity.value,
                "timestamp": datetime.now()
            }
            
            self.sent_notifications.append(notification)
            sent.append(notification["id"])
            
            # Симуляция отправки
            await asyncio.sleep(0.05)
            
        return sent


class IncidentManager:
    """Менеджер инцидентов"""
    
    def __init__(self, oncall_manager: OnCallManager,
                  escalation_manager: EscalationManager,
                  notification_service: NotificationService):
        self.oncall_manager = oncall_manager
        self.escalation_manager = escalation_manager
        self.notification_service = notification_service
        
        self.incidents: Dict[str, Incident] = {}
        self.alerts: Dict[str, Alert] = {}
        self.alert_router = AlertRouter()
        
    async def create_alert(self, source: str, title: str,
                            severity: IncidentSeverity,
                            **kwargs) -> Alert:
        """Создание оповещения"""
        alert = Alert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            source=source,
            title=title,
            severity=severity,
            **kwargs
        )
        
        self.alerts[alert.alert_id] = alert
        
        # Маршрутизация
        rules = self.alert_router.match_rules(alert)
        
        if rules:
            # Используем первое правило
            rule = rules[0]
            
            # Запуск эскалации
            notified = await self.escalation_manager.start_escalation(
                rule.escalation_policy_id,
                alert.alert_id
            )
            
            # Уведомления
            for user_id in notified:
                user = self.oncall_manager.users.get(user_id)
                if user:
                    await self.notification_service.notify(
                        user, alert, rule.notification_channels
                    )
                    
            alert.status = AlertStatus.SENT
            
        return alert
        
    async def create_incident(self, title: str, severity: IncidentSeverity,
                               alert_ids: List[str] = None,
                               **kwargs) -> Incident:
        """Создание инцидента"""
        incident = Incident(
            incident_id=f"inc_{uuid.uuid4().hex[:8]}",
            title=title,
            severity=severity,
            alerts=alert_ids or [],
            **kwargs
        )
        
        # Добавляем в timeline
        incident.timeline.append({
            "timestamp": datetime.now(),
            "event": "incident_created",
            "user": "system",
            "details": {"severity": severity.value}
        })
        
        # Связываем алерты
        for alert_id in incident.alerts:
            if alert_id in self.alerts:
                self.alerts[alert_id].incident_id = incident.incident_id
                
        self.incidents[incident.incident_id] = incident
        return incident
        
    async def acknowledge(self, incident_id: str, user_id: str) -> bool:
        """Подтверждение инцидента"""
        incident = self.incidents.get(incident_id)
        
        if not incident or incident.status not in [IncidentStatus.TRIGGERED]:
            return False
            
        now = datetime.now()
        
        incident.status = IncidentStatus.ACKNOWLEDGED
        incident.acknowledged_at = now
        incident.time_to_acknowledge = (now - incident.created_at).total_seconds() / 60
        
        if user_id not in incident.assignees:
            incident.assignees.append(user_id)
            
        incident.timeline.append({
            "timestamp": now,
            "event": "acknowledged",
            "user": user_id,
            "details": {}
        })
        
        # Останавливаем эскалацию для связанных алертов
        for alert_id in incident.alerts:
            self.escalation_manager.stop_escalation(alert_id)
            if alert_id in self.alerts:
                self.alerts[alert_id].status = AlertStatus.ACKNOWLEDGED
                
        return True
        
    async def update_status(self, incident_id: str, status: IncidentStatus,
                             user_id: str, note: str = "") -> bool:
        """Обновление статуса"""
        incident = self.incidents.get(incident_id)
        
        if not incident:
            return False
            
        old_status = incident.status
        incident.status = status
        
        now = datetime.now()
        
        incident.timeline.append({
            "timestamp": now,
            "event": "status_changed",
            "user": user_id,
            "details": {"from": old_status.value, "to": status.value, "note": note}
        })
        
        if status == IncidentStatus.RESOLVED:
            incident.resolved_at = now
            incident.time_to_resolve = (now - incident.created_at).total_seconds() / 60
            
            for alert_id in incident.alerts:
                if alert_id in self.alerts:
                    self.alerts[alert_id].status = AlertStatus.RESOLVED
                    self.alerts[alert_id].resolved_at = now
                    
        elif status == IncidentStatus.CLOSED:
            incident.closed_at = now
            
        return True
        
    def add_timeline_event(self, incident_id: str, event: str,
                            user_id: str, details: Dict[str, Any] = None):
        """Добавление события в timeline"""
        incident = self.incidents.get(incident_id)
        
        if incident:
            incident.timeline.append({
                "timestamp": datetime.now(),
                "event": event,
                "user": user_id,
                "details": details or {}
            })


class PostMortemManager:
    """Менеджер post-mortem"""
    
    def __init__(self, incident_manager: IncidentManager):
        self.incident_manager = incident_manager
        self.postmortems: Dict[str, PostMortem] = {}
        
    def create(self, incident_id: str, title: str = None) -> PostMortem:
        """Создание post-mortem"""
        incident = self.incident_manager.incidents.get(incident_id)
        
        if not incident:
            raise ValueError("Incident not found")
            
        postmortem = PostMortem(
            postmortem_id=f"pm_{uuid.uuid4().hex[:8]}",
            incident_id=incident_id,
            title=title or f"Post-Mortem: {incident.title}",
            timeline=incident.timeline.copy()
        )
        
        incident.postmortem_id = postmortem.postmortem_id
        self.postmortems[postmortem.postmortem_id] = postmortem
        
        return postmortem
        
    def add_action_item(self, postmortem_id: str, description: str,
                         owner: str, due_date: datetime):
        """Добавление action item"""
        postmortem = self.postmortems.get(postmortem_id)
        
        if postmortem:
            postmortem.action_items.append({
                "id": f"action_{uuid.uuid4().hex[:8]}",
                "description": description,
                "owner": owner,
                "due_date": due_date,
                "status": "open",
                "created_at": datetime.now()
            })
            
    def publish(self, postmortem_id: str) -> bool:
        """Публикация post-mortem"""
        postmortem = self.postmortems.get(postmortem_id)
        
        if postmortem and postmortem.status == "in_review":
            postmortem.status = "published"
            postmortem.published_at = datetime.now()
            return True
            
        return False


class RunbookManager:
    """Менеджер runbooks"""
    
    def __init__(self):
        self.runbooks: Dict[str, Runbook] = {}
        
    def create(self, name: str, category: str,
                steps: List[Dict[str, Any]], **kwargs) -> Runbook:
        """Создание runbook"""
        runbook = Runbook(
            runbook_id=f"rb_{uuid.uuid4().hex[:8]}",
            name=name,
            category=category,
            steps=steps,
            **kwargs
        )
        
        self.runbooks[runbook.runbook_id] = runbook
        return runbook
        
    def find_by_alert(self, alert_type: str) -> List[Runbook]:
        """Поиск по типу алерта"""
        return [
            rb for rb in self.runbooks.values()
            if alert_type in rb.alert_types
        ]
        
    def find_by_service(self, service: str) -> List[Runbook]:
        """Поиск по сервису"""
        return [
            rb for rb in self.runbooks.values()
            if service in rb.services
        ]


class SLATracker:
    """Отслеживание SLA"""
    
    def __init__(self):
        self.slas: Dict[str, SLA] = {}
        
    def create_sla(self, name: str, targets: Dict[str, Dict[str, int]]) -> SLA:
        """Создание SLA"""
        sla = SLA(
            sla_id=f"sla_{uuid.uuid4().hex[:8]}",
            name=name,
            targets=targets
        )
        
        self.slas[sla.sla_id] = sla
        return sla
        
    def check_compliance(self, incident: Incident, sla_id: str) -> Dict[str, Any]:
        """Проверка соответствия SLA"""
        sla = self.slas.get(sla_id)
        
        if not sla:
            return {"error": "SLA not found"}
            
        severity = incident.severity.value
        targets = sla.targets.get(severity, {})
        
        result = {
            "sla_id": sla_id,
            "severity": severity,
            "targets": targets,
            "metrics": {},
            "breaches": []
        }
        
        # Проверка acknowledge
        if "acknowledge" in targets and incident.time_to_acknowledge:
            result["metrics"]["acknowledge"] = incident.time_to_acknowledge
            if incident.time_to_acknowledge > targets["acknowledge"]:
                result["breaches"].append({
                    "metric": "acknowledge",
                    "target": targets["acknowledge"],
                    "actual": incident.time_to_acknowledge
                })
                
        # Проверка resolve
        if "resolve" in targets and incident.time_to_resolve:
            result["metrics"]["resolve"] = incident.time_to_resolve
            if incident.time_to_resolve > targets["resolve"]:
                result["breaches"].append({
                    "metric": "resolve",
                    "target": targets["resolve"],
                    "actual": incident.time_to_resolve
                })
                
        result["compliant"] = len(result["breaches"]) == 0
        
        return result


class IncidentPlatform:
    """Платформа управления инцидентами"""
    
    def __init__(self):
        self.oncall_manager = OnCallManager()
        self.notification_service = NotificationService()
        self.escalation_manager = EscalationManager(self.oncall_manager)
        self.incident_manager = IncidentManager(
            self.oncall_manager,
            self.escalation_manager,
            self.notification_service
        )
        self.postmortem_manager = PostMortemManager(self.incident_manager)
        self.runbook_manager = RunbookManager()
        self.sla_tracker = SLATracker()
        
    def get_stats(self) -> Dict[str, Any]:
        """Статистика"""
        incidents = list(self.incident_manager.incidents.values())
        
        open_incidents = len([i for i in incidents if i.status not in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]])
        
        by_severity = defaultdict(int)
        for inc in incidents:
            by_severity[inc.severity.value] += 1
            
        avg_tta = 0
        avg_ttr = 0
        with_tta = [i for i in incidents if i.time_to_acknowledge]
        with_ttr = [i for i in incidents if i.time_to_resolve]
        
        if with_tta:
            avg_tta = sum(i.time_to_acknowledge for i in with_tta) / len(with_tta)
        if with_ttr:
            avg_ttr = sum(i.time_to_resolve for i in with_ttr) / len(with_ttr)
            
        return {
            "total_incidents": len(incidents),
            "open_incidents": open_incidents,
            "by_severity": dict(by_severity),
            "avg_time_to_acknowledge_min": round(avg_tta, 1),
            "avg_time_to_resolve_min": round(avg_ttr, 1),
            "alerts": len(self.incident_manager.alerts),
            "notifications_sent": len(self.notification_service.sent_notifications),
            "postmortems": len(self.postmortem_manager.postmortems),
            "runbooks": len(self.runbook_manager.runbooks)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 60: Incident Management & On-Call")
    print("=" * 60)
    
    async def demo():
        # Создание платформы
        platform = IncidentPlatform()
        print("✓ Incident Platform created")
        
        # Создание on-call пользователей
        print("\n👤 Creating on-call users...")
        
        users = [
            platform.oncall_manager.add_user(
                name="Alice Engineer",
                email="alice@example.com",
                phone="+1234567890",
                slack_id="U12345"
            ),
            platform.oncall_manager.add_user(
                name="Bob DevOps",
                email="bob@example.com",
                phone="+0987654321",
                slack_id="U67890"
            ),
            platform.oncall_manager.add_user(
                name="Carol SRE",
                email="carol@example.com",
                phone="+1122334455",
                slack_id="U11223"
            ),
        ]
        
        for user in users:
            print(f"  ✓ {user.name} ({user.email})")
            
        # Создание расписания
        print("\n📅 Creating on-call schedule...")
        
        schedule = platform.oncall_manager.create_schedule(
            name="Primary On-Call",
            participants=[u.user_id for u in users],
            rotation_type="weekly"
        )
        print(f"  ✓ Schedule: {schedule.name}")
        
        current = platform.oncall_manager.get_current_oncall(schedule.schedule_id)
        print(f"  Current on-call: {current.name if current else 'None'}")
        
        # Создание политики эскалации
        print("\n🔼 Creating escalation policy...")
        
        policy = platform.escalation_manager.create_policy(
            name="Standard Escalation",
            levels=[
                {"timeout_minutes": 5, "targets": [schedule.schedule_id]},
                {"timeout_minutes": 10, "targets": [users[1].user_id]},
                {"timeout_minutes": 15, "targets": [users[2].user_id]},
            ]
        )
        print(f"  ✓ Policy: {policy.name} ({len(policy.levels)} levels)")
        
        # Создание правил маршрутизации
        print("\n📋 Creating alert routing rules...")
        
        rule = platform.incident_manager.alert_router.add_rule(
            name="Critical Alerts",
            conditions={"severity": ["sev1", "sev2"]},
            escalation_policy_id=policy.policy_id,
            notification_channels=[NotificationChannel.SLACK, NotificationChannel.SMS]
        )
        print(f"  ✓ Rule: {rule.name}")
        
        # Создание SLA
        print("\n⏱️ Creating SLA...")
        
        sla = platform.sla_tracker.create_sla(
            name="Standard SLA",
            targets={
                "sev1": {"acknowledge": 5, "resolve": 60},
                "sev2": {"acknowledge": 15, "resolve": 240},
                "sev3": {"acknowledge": 60, "resolve": 480},
            }
        )
        print(f"  ✓ SLA: {sla.name}")
        
        # Создание runbook
        print("\n📖 Creating runbooks...")
        
        runbook = platform.runbook_manager.create(
            name="Database Connection Issues",
            category="database",
            services=["api", "backend"],
            alert_types=["db_connection_failed"],
            steps=[
                {"step": 1, "description": "Check database server status", "command": "systemctl status postgresql"},
                {"step": 2, "description": "Check connection pool", "command": "pgbouncer show pools"},
                {"step": 3, "description": "Verify network connectivity", "command": "nc -zv db-server 5432"},
                {"step": 4, "description": "Check application logs", "command": "tail -100 /var/log/app/error.log"},
            ]
        )
        print(f"  ✓ Runbook: {runbook.name} ({len(runbook.steps)} steps)")
        
        # Симуляция инцидента
        print("\n🚨 Simulating incident...")
        
        # Создание алерта
        alert = await platform.incident_manager.create_alert(
            source="monitoring",
            title="High Error Rate on API Gateway",
            severity=IncidentSeverity.SEV1,
            description="Error rate exceeded 50% on api-gateway service"
        )
        print(f"  ✓ Alert created: {alert.alert_id}")
        print(f"    Severity: {alert.severity.value}")
        print(f"    Status: {alert.status.value}")
        
        # Создание инцидента
        incident = await platform.incident_manager.create_incident(
            title="API Gateway Outage",
            severity=IncidentSeverity.SEV1,
            alert_ids=[alert.alert_id],
            services=["api-gateway", "backend"],
            commander_id=users[0].user_id
        )
        print(f"\n  ✓ Incident created: {incident.incident_id}")
        print(f"    Status: {incident.status.value}")
        
        # Симуляция работы с инцидентом
        await asyncio.sleep(0.2)  # Симуляция времени
        
        # Acknowledge
        await platform.incident_manager.acknowledge(incident.incident_id, users[0].user_id)
        print(f"\n  ✓ Incident acknowledged by {users[0].name}")
        print(f"    Time to acknowledge: {incident.time_to_acknowledge:.1f} min")
        
        # Обновление статуса
        await platform.incident_manager.update_status(
            incident.incident_id,
            IncidentStatus.INVESTIGATING,
            users[0].user_id,
            "Starting investigation"
        )
        print("  ✓ Status -> investigating")
        
        # Добавление события
        platform.incident_manager.add_timeline_event(
            incident.incident_id,
            "found_root_cause",
            users[0].user_id,
            {"cause": "Memory leak in upstream service"}
        )
        print("  ✓ Root cause identified")
        
        await platform.incident_manager.update_status(
            incident.incident_id,
            IncidentStatus.MITIGATING,
            users[0].user_id,
            "Restarting affected services"
        )
        print("  ✓ Status -> mitigating")
        
        await asyncio.sleep(0.1)
        
        # Разрешение
        await platform.incident_manager.update_status(
            incident.incident_id,
            IncidentStatus.RESOLVED,
            users[0].user_id,
            "Services restored"
        )
        print(f"\n  ✓ Incident resolved")
        print(f"    Time to resolve: {incident.time_to_resolve:.1f} min")
        
        # Проверка SLA
        print("\n📊 SLA Compliance check...")
        
        compliance = platform.sla_tracker.check_compliance(incident, sla.sla_id)
        print(f"  Compliant: {compliance['compliant']}")
        print(f"  Metrics: {compliance['metrics']}")
        if compliance['breaches']:
            print(f"  Breaches: {len(compliance['breaches'])}")
            
        # Post-mortem
        print("\n📝 Creating post-mortem...")
        
        postmortem = platform.postmortem_manager.create(incident.incident_id)
        postmortem.root_cause = "Memory leak in upstream service caused connection pool exhaustion"
        postmortem.contributing_factors = [
            "No memory limits set on containers",
            "Missing connection timeout configuration"
        ]
        postmortem.impact = {
            "duration_minutes": incident.time_to_resolve,
            "affected_users": 5000,
            "revenue_impact": 2500
        }
        print(f"  ✓ Post-mortem created: {postmortem.postmortem_id}")
        
        # Action items
        platform.postmortem_manager.add_action_item(
            postmortem.postmortem_id,
            "Add memory limits to all containers",
            users[1].user_id,
            datetime.now() + timedelta(days=7)
        )
        platform.postmortem_manager.add_action_item(
            postmortem.postmortem_id,
            "Implement connection pool monitoring",
            users[2].user_id,
            datetime.now() + timedelta(days=14)
        )
        print(f"  ✓ Added {len(postmortem.action_items)} action items")
        
        # Timeline инцидента
        print("\n📋 Incident Timeline:")
        for event in incident.timeline[-5:]:
            ts = event["timestamp"].strftime("%H:%M:%S")
            print(f"  {ts} - {event['event']}: {event.get('details', {})}")
            
        # Статистика
        print("\n📈 Platform Statistics:")
        stats = platform.get_stats()
        print(f"  Total incidents: {stats['total_incidents']}")
        print(f"  Open incidents: {stats['open_incidents']}")
        print(f"  By severity: {stats['by_severity']}")
        print(f"  Avg TTA: {stats['avg_time_to_acknowledge_min']} min")
        print(f"  Avg TTR: {stats['avg_time_to_resolve_min']} min")
        print(f"  Alerts: {stats['alerts']}")
        print(f"  Notifications sent: {stats['notifications_sent']}")
        print(f"  Post-mortems: {stats['postmortems']}")
        print(f"  Runbooks: {stats['runbooks']}")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Incident Management & On-Call Platform initialized!")
    print("=" * 60)
