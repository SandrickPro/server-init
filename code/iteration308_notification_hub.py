#!/usr/bin/env python3
"""
Server Init - Iteration 308: Notification Hub Platform
Платформа центра уведомлений

Функционал:
- Multi-Channel Delivery - доставка по множеству каналов
- Template Management - управление шаблонами
- Routing Rules - правила маршрутизации
- Rate Limiting - ограничение частоты
- Delivery Tracking - отслеживание доставки
- Preferences Management - управление предпочтениями
- Batching - группировка уведомлений
- Analytics - аналитика
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import re


class Channel(Enum):
    """Канал доставки"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    SLACK = "slack"
    WEBHOOK = "webhook"
    IN_APP = "in_app"
    TEAMS = "teams"


class NotificationPriority(Enum):
    """Приоритет уведомления"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class DeliveryStatus(Enum):
    """Статус доставки"""
    PENDING = "pending"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    BOUNCED = "bounced"


class NotificationType(Enum):
    """Тип уведомления"""
    ALERT = "alert"
    INFO = "info"
    WARNING = "warning"
    MARKETING = "marketing"
    TRANSACTIONAL = "transactional"
    SYSTEM = "system"


@dataclass
class Template:
    """Шаблон уведомления"""
    template_id: str
    name: str
    
    # Content
    subject_template: str = ""
    body_template: str = ""
    
    # Channel-specific content
    channel_templates: Dict[Channel, Dict[str, str]] = field(default_factory=dict)
    
    # Metadata
    notification_type: NotificationType = NotificationType.INFO
    variables: List[str] = field(default_factory=list)
    
    # Status
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Recipient:
    """Получатель"""
    recipient_id: str
    user_id: str
    
    # Contacts
    email: str = ""
    phone: str = ""
    device_token: str = ""  # for push
    slack_id: str = ""
    webhook_url: str = ""
    
    # Preferences
    preferred_channels: List[Channel] = field(default_factory=list)
    do_not_disturb: bool = False
    dnd_start: Optional[str] = None  # HH:MM
    dnd_end: Optional[str] = None
    
    # Opt-outs
    unsubscribed_types: List[NotificationType] = field(default_factory=list)
    
    # Timezone
    timezone: str = "UTC"


@dataclass
class RoutingRule:
    """Правило маршрутизации"""
    rule_id: str
    name: str
    
    # Conditions
    conditions: Dict[str, Any] = field(default_factory=dict)
    # e.g., {"notification_type": "alert", "priority": "urgent"}
    
    # Actions
    channels: List[Channel] = field(default_factory=list)
    
    # Priority
    priority: int = 0
    
    # Status
    enabled: bool = True


@dataclass
class Notification:
    """Уведомление"""
    notification_id: str
    
    # Template
    template_id: str = ""
    
    # Content
    subject: str = ""
    body: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Type
    notification_type: NotificationType = NotificationType.INFO
    priority: NotificationPriority = NotificationPriority.NORMAL
    
    # Recipients
    recipient_ids: List[str] = field(default_factory=list)
    
    # Channels
    channels: List[Channel] = field(default_factory=list)
    
    # Scheduling
    scheduled_at: Optional[datetime] = None
    
    # Batching
    batch_id: Optional[str] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Delivery:
    """Запись о доставке"""
    delivery_id: str
    notification_id: str
    recipient_id: str
    
    # Channel
    channel: Channel = Channel.EMAIL
    
    # Status
    status: DeliveryStatus = DeliveryStatus.PENDING
    
    # Attempts
    attempts: int = 0
    max_attempts: int = 3
    
    # Response
    response_code: Optional[str] = None
    error_message: str = ""
    
    # Tracking
    opened: bool = False
    clicked: bool = False
    
    # Timestamps
    queued_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None


@dataclass
class RateLimit:
    """Ограничение частоты"""
    limit_id: str
    
    # Scope
    scope: str = "global"  # global, channel, recipient, notification_type
    scope_value: str = ""
    
    # Limits
    max_per_minute: int = 100
    max_per_hour: int = 1000
    max_per_day: int = 10000
    
    # Current usage
    current_minute: int = 0
    current_hour: int = 0
    current_day: int = 0
    
    # Reset times
    minute_reset: datetime = field(default_factory=datetime.now)
    hour_reset: datetime = field(default_factory=datetime.now)
    day_reset: datetime = field(default_factory=datetime.now)


class NotificationHub:
    """Центр уведомлений"""
    
    def __init__(self):
        self.templates: Dict[str, Template] = {}
        self.recipients: Dict[str, Recipient] = {}
        self.routing_rules: Dict[str, RoutingRule] = {}
        self.notifications: Dict[str, Notification] = {}
        self.deliveries: Dict[str, Delivery] = {}
        self.rate_limits: Dict[str, RateLimit] = {}
        
        # Stats
        self.total_sent: int = 0
        self.total_delivered: int = 0
        self.total_failed: int = 0
        
    async def create_template(self, name: str,
                             subject: str,
                             body: str,
                             notification_type: NotificationType = NotificationType.INFO,
                             channel_templates: Dict[Channel, Dict[str, str]] = None) -> Template:
        """Создание шаблона"""
        # Extract variables from templates
        variables = list(set(re.findall(r'\{\{(\w+)\}\}', subject + body)))
        
        template = Template(
            template_id=f"tpl_{uuid.uuid4().hex[:8]}",
            name=name,
            subject_template=subject,
            body_template=body,
            notification_type=notification_type,
            channel_templates=channel_templates or {},
            variables=variables
        )
        
        self.templates[template.template_id] = template
        return template
        
    async def register_recipient(self, user_id: str,
                                email: str = "",
                                phone: str = "",
                                preferred_channels: List[Channel] = None) -> Recipient:
        """Регистрация получателя"""
        recipient = Recipient(
            recipient_id=f"rcp_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            email=email,
            phone=phone,
            preferred_channels=preferred_channels or [Channel.EMAIL]
        )
        
        self.recipients[recipient.recipient_id] = recipient
        return recipient
        
    async def create_routing_rule(self, name: str,
                                 conditions: Dict[str, Any],
                                 channels: List[Channel],
                                 priority: int = 0) -> RoutingRule:
        """Создание правила маршрутизации"""
        rule = RoutingRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name=name,
            conditions=conditions,
            channels=channels,
            priority=priority
        )
        
        self.routing_rules[rule.rule_id] = rule
        return rule
        
    async def create_rate_limit(self, scope: str,
                               scope_value: str = "",
                               per_minute: int = 100,
                               per_hour: int = 1000,
                               per_day: int = 10000) -> RateLimit:
        """Создание ограничения частоты"""
        limit = RateLimit(
            limit_id=f"rl_{uuid.uuid4().hex[:8]}",
            scope=scope,
            scope_value=scope_value,
            max_per_minute=per_minute,
            max_per_hour=per_hour,
            max_per_day=per_day
        )
        
        self.rate_limits[limit.limit_id] = limit
        return limit
        
    def _render_template(self, template: str, data: Dict[str, Any]) -> str:
        """Рендеринг шаблона"""
        result = template
        for key, value in data.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result
        
    async def _find_matching_rules(self, notification: Notification) -> List[RoutingRule]:
        """Поиск подходящих правил"""
        matching = []
        
        for rule in self.routing_rules.values():
            if not rule.enabled:
                continue
                
            matches = True
            for key, value in rule.conditions.items():
                if key == "notification_type":
                    if notification.notification_type.value != value:
                        matches = False
                        break
                elif key == "priority":
                    if notification.priority.value != value:
                        matches = False
                        break
                        
            if matches:
                matching.append(rule)
                
        # Sort by priority
        matching.sort(key=lambda r: r.priority, reverse=True)
        return matching
        
    async def _check_rate_limit(self, channel: Channel, recipient_id: str) -> bool:
        """Проверка ограничения частоты"""
        now = datetime.now()
        
        for limit in self.rate_limits.values():
            # Reset counters if needed
            if (now - limit.minute_reset).total_seconds() >= 60:
                limit.current_minute = 0
                limit.minute_reset = now
            if (now - limit.hour_reset).total_seconds() >= 3600:
                limit.current_hour = 0
                limit.hour_reset = now
            if (now - limit.day_reset).total_seconds() >= 86400:
                limit.current_day = 0
                limit.day_reset = now
                
            # Check limits
            if limit.scope == "global":
                if (limit.current_minute >= limit.max_per_minute or
                    limit.current_hour >= limit.max_per_hour or
                    limit.current_day >= limit.max_per_day):
                    return False
            elif limit.scope == "channel" and limit.scope_value == channel.value:
                if limit.current_minute >= limit.max_per_minute:
                    return False
                    
        return True
        
    async def _update_rate_limit(self, channel: Channel):
        """Обновление счётчиков rate limit"""
        for limit in self.rate_limits.values():
            if limit.scope == "global" or (limit.scope == "channel" and limit.scope_value == channel.value):
                limit.current_minute += 1
                limit.current_hour += 1
                limit.current_day += 1
                
    async def send_notification(self, template_id: str,
                               recipient_ids: List[str],
                               data: Dict[str, Any] = None,
                               priority: NotificationPriority = NotificationPriority.NORMAL,
                               channels: List[Channel] = None) -> Notification:
        """Отправка уведомления"""
        template = self.templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
            
        # Render content
        data = data or {}
        subject = self._render_template(template.subject_template, data)
        body = self._render_template(template.body_template, data)
        
        notification = Notification(
            notification_id=f"notif_{uuid.uuid4().hex[:8]}",
            template_id=template_id,
            subject=subject,
            body=body,
            data=data,
            notification_type=template.notification_type,
            priority=priority,
            recipient_ids=recipient_ids,
            channels=channels or []
        )
        
        self.notifications[notification.notification_id] = notification
        
        # Determine channels if not specified
        if not notification.channels:
            rules = await self._find_matching_rules(notification)
            if rules:
                notification.channels = rules[0].channels
            else:
                notification.channels = [Channel.EMAIL]  # default
                
        # Create deliveries
        for recipient_id in recipient_ids:
            recipient = self.recipients.get(recipient_id)
            if not recipient:
                continue
                
            # Check opt-outs
            if template.notification_type in recipient.unsubscribed_types:
                continue
                
            # Check DND
            if recipient.do_not_disturb:
                continue
                
            # Create delivery for each channel
            for channel in notification.channels:
                # Check rate limit
                if not await self._check_rate_limit(channel, recipient_id):
                    continue
                    
                delivery = Delivery(
                    delivery_id=f"dlv_{uuid.uuid4().hex[:8]}",
                    notification_id=notification.notification_id,
                    recipient_id=recipient_id,
                    channel=channel
                )
                
                self.deliveries[delivery.delivery_id] = delivery
                
                # Process delivery
                await self._process_delivery(delivery)
                
        return notification
        
    async def _process_delivery(self, delivery: Delivery):
        """Обработка доставки"""
        delivery.attempts += 1
        delivery.queued_at = datetime.now()
        delivery.status = DeliveryStatus.QUEUED
        
        # Simulate sending
        await asyncio.sleep(0.01)
        
        success = random.random() > 0.05  # 95% success rate
        
        if success:
            delivery.status = DeliveryStatus.SENT
            delivery.sent_at = datetime.now()
            self.total_sent += 1
            
            await self._update_rate_limit(delivery.channel)
            
            # Simulate delivery
            delivered = random.random() > 0.02  # 98% delivery rate
            
            if delivered:
                delivery.status = DeliveryStatus.DELIVERED
                delivery.delivered_at = datetime.now()
                self.total_delivered += 1
                
                # Simulate read
                if random.random() > 0.6:  # 40% read rate
                    delivery.status = DeliveryStatus.READ
                    delivery.opened = True
                    delivery.read_at = datetime.now()
                    
                    # Simulate click
                    if random.random() > 0.7:  # 30% click rate of reads
                        delivery.clicked = True
        else:
            delivery.status = DeliveryStatus.FAILED
            delivery.error_message = "Delivery failed"
            self.total_failed += 1
            
    async def schedule_notification(self, template_id: str,
                                   recipient_ids: List[str],
                                   scheduled_at: datetime,
                                   data: Dict[str, Any] = None) -> Notification:
        """Планирование уведомления"""
        template = self.templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
            
        data = data or {}
        subject = self._render_template(template.subject_template, data)
        body = self._render_template(template.body_template, data)
        
        notification = Notification(
            notification_id=f"notif_{uuid.uuid4().hex[:8]}",
            template_id=template_id,
            subject=subject,
            body=body,
            data=data,
            notification_type=template.notification_type,
            recipient_ids=recipient_ids,
            scheduled_at=scheduled_at
        )
        
        self.notifications[notification.notification_id] = notification
        return notification
        
    async def update_preferences(self, recipient_id: str,
                                preferred_channels: List[Channel] = None,
                                unsubscribe_types: List[NotificationType] = None,
                                dnd: bool = None) -> bool:
        """Обновление предпочтений"""
        recipient = self.recipients.get(recipient_id)
        if not recipient:
            return False
            
        if preferred_channels is not None:
            recipient.preferred_channels = preferred_channels
        if unsubscribe_types is not None:
            recipient.unsubscribed_types = unsubscribe_types
        if dnd is not None:
            recipient.do_not_disturb = dnd
            
        return True
        
    def get_delivery_stats(self, notification_id: str) -> Dict[str, Any]:
        """Статистика доставки уведомления"""
        deliveries = [d for d in self.deliveries.values() if d.notification_id == notification_id]
        
        if not deliveries:
            return {}
            
        by_status = {}
        by_channel = {}
        
        total_opened = 0
        total_clicked = 0
        
        for d in deliveries:
            by_status[d.status.value] = by_status.get(d.status.value, 0) + 1
            by_channel[d.channel.value] = by_channel.get(d.channel.value, 0) + 1
            
            if d.opened:
                total_opened += 1
            if d.clicked:
                total_clicked += 1
                
        return {
            "notification_id": notification_id,
            "total_deliveries": len(deliveries),
            "by_status": by_status,
            "by_channel": by_channel,
            "open_rate": (total_opened / len(deliveries)) * 100 if deliveries else 0,
            "click_rate": (total_clicked / len(deliveries)) * 100 if deliveries else 0
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        by_status = {}
        by_channel = {}
        by_type = {}
        
        for d in self.deliveries.values():
            by_status[d.status.value] = by_status.get(d.status.value, 0) + 1
            by_channel[d.channel.value] = by_channel.get(d.channel.value, 0) + 1
            
        for n in self.notifications.values():
            by_type[n.notification_type.value] = by_type.get(n.notification_type.value, 0) + 1
            
        total_opened = sum(1 for d in self.deliveries.values() if d.opened)
        total_clicked = sum(1 for d in self.deliveries.values() if d.clicked)
        
        return {
            "total_templates": len(self.templates),
            "total_recipients": len(self.recipients),
            "total_rules": len(self.routing_rules),
            "total_notifications": len(self.notifications),
            "total_deliveries": len(self.deliveries),
            "by_status": by_status,
            "by_channel": by_channel,
            "by_type": by_type,
            "total_sent": self.total_sent,
            "total_delivered": self.total_delivered,
            "total_failed": self.total_failed,
            "total_opened": total_opened,
            "total_clicked": total_clicked,
            "delivery_rate": (self.total_delivered / max(self.total_sent, 1)) * 100,
            "open_rate": (total_opened / max(self.total_delivered, 1)) * 100,
            "click_rate": (total_clicked / max(total_opened, 1)) * 100
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 308: Notification Hub Platform")
    print("=" * 60)
    
    hub = NotificationHub()
    print("✓ Notification Hub created")
    
    # Create templates
    print("\n📝 Creating Templates...")
    
    templates_data = [
        ("Alert Template", "🚨 Alert: {{alert_name}}", 
         "An alert has been triggered:\n\nAlert: {{alert_name}}\nSeverity: {{severity}}\nMessage: {{message}}",
         NotificationType.ALERT),
        ("Welcome Email", "Welcome to {{app_name}}, {{user_name}}!",
         "Hi {{user_name}},\n\nWelcome to {{app_name}}! We're excited to have you.",
         NotificationType.TRANSACTIONAL),
        ("Password Reset", "Password Reset for {{app_name}}",
         "Click the link to reset your password: {{reset_link}}\n\nThis link expires in {{expiry}} minutes.",
         NotificationType.TRANSACTIONAL),
        ("Weekly Digest", "Your Weekly Summary - {{week}}",
         "Here's what happened this week:\n\n{{summary}}",
         NotificationType.INFO),
        ("System Maintenance", "Scheduled Maintenance: {{service_name}}",
         "{{service_name}} will undergo maintenance on {{date}} from {{start_time}} to {{end_time}}.",
         NotificationType.SYSTEM)
    ]
    
    templates = []
    for name, subject, body, n_type in templates_data:
        template = await hub.create_template(name, subject, body, n_type)
        templates.append(template)
        print(f"  📝 {name} ({n_type.value})")
        print(f"     Variables: {', '.join(template.variables)}")
        
    # Register recipients
    print("\n👥 Registering Recipients...")
    
    recipients_data = [
        ("user_001", "alice@example.com", "+1-555-0101", [Channel.EMAIL, Channel.SLACK]),
        ("user_002", "bob@example.com", "+1-555-0102", [Channel.EMAIL, Channel.PUSH]),
        ("user_003", "carol@example.com", "+1-555-0103", [Channel.SMS, Channel.EMAIL]),
        ("user_004", "david@example.com", "+1-555-0104", [Channel.EMAIL]),
        ("user_005", "eve@example.com", "+1-555-0105", [Channel.PUSH, Channel.IN_APP]),
        ("user_006", "frank@example.com", "+1-555-0106", [Channel.EMAIL, Channel.SLACK]),
        ("user_007", "grace@example.com", "+1-555-0107", [Channel.EMAIL]),
        ("user_008", "henry@example.com", "+1-555-0108", [Channel.SMS])
    ]
    
    recipients = []
    for user_id, email, phone, channels in recipients_data:
        recipient = await hub.register_recipient(user_id, email, phone, channels)
        recipients.append(recipient)
        channels_str = ", ".join([c.value for c in channels])
        print(f"  👤 {user_id}: {email} ({channels_str})")
        
    # Create routing rules
    print("\n📋 Creating Routing Rules...")
    
    rules_data = [
        ("Urgent Alerts", {"notification_type": "alert", "priority": "urgent"}, 
         [Channel.SMS, Channel.PUSH, Channel.EMAIL], 100),
        ("Normal Alerts", {"notification_type": "alert"}, 
         [Channel.EMAIL, Channel.SLACK], 50),
        ("System Notifications", {"notification_type": "system"},
         [Channel.EMAIL, Channel.IN_APP], 40),
        ("Transactional", {"notification_type": "transactional"},
         [Channel.EMAIL], 30)
    ]
    
    for name, conditions, channels, priority in rules_data:
        rule = await hub.create_routing_rule(name, conditions, channels, priority)
        channels_str = ", ".join([c.value for c in channels])
        print(f"  📋 {name} → {channels_str}")
        
    # Create rate limits
    print("\n⏱️ Creating Rate Limits...")
    
    await hub.create_rate_limit("global", "", 1000, 10000, 100000)
    await hub.create_rate_limit("channel", "email", 500, 5000, 50000)
    await hub.create_rate_limit("channel", "sms", 100, 1000, 10000)
    
    print("  ⏱️ Global: 1000/min, 10000/hr, 100000/day")
    print("  ⏱️ Email: 500/min, 5000/hr, 50000/day")
    print("  ⏱️ SMS: 100/min, 1000/hr, 10000/day")
    
    # Send notifications
    print("\n📤 Sending Notifications...")
    
    # Alert notification
    alert_notif = await hub.send_notification(
        templates[0].template_id,
        [r.recipient_id for r in recipients[:5]],
        {"alert_name": "High CPU Usage", "severity": "critical", "message": "CPU usage exceeded 90%"},
        NotificationPriority.URGENT
    )
    print(f"  📤 Alert sent to {len(alert_notif.recipient_ids)} recipients")
    
    # Welcome notification
    welcome_notif = await hub.send_notification(
        templates[1].template_id,
        [recipients[0].recipient_id],
        {"app_name": "Platform", "user_name": "Alice"},
        NotificationPriority.NORMAL
    )
    print(f"  📤 Welcome email sent")
    
    # System maintenance notification
    maintenance_notif = await hub.send_notification(
        templates[4].template_id,
        [r.recipient_id for r in recipients],
        {"service_name": "API Gateway", "date": "2024-01-15", 
         "start_time": "02:00 UTC", "end_time": "04:00 UTC"},
        NotificationPriority.HIGH
    )
    print(f"  📤 Maintenance notice sent to {len(maintenance_notif.recipient_ids)} recipients")
    
    # Weekly digest
    digest_notif = await hub.send_notification(
        templates[3].template_id,
        [r.recipient_id for r in recipients[:4]],
        {"week": "Dec 9-15", "summary": "5 deployments, 2 incidents resolved"},
        NotificationPriority.LOW
    )
    print(f"  📤 Weekly digest sent to {len(digest_notif.recipient_ids)} recipients")
    
    # Schedule notification
    print("\n⏰ Scheduling Notifications...")
    
    scheduled = await hub.schedule_notification(
        templates[3].template_id,
        [r.recipient_id for r in recipients],
        datetime.now() + timedelta(hours=24),
        {"week": "Dec 16-22", "summary": "Scheduled summary"}
    )
    print(f"  ⏰ Scheduled for {scheduled.scheduled_at}")
    
    # Update preferences
    print("\n⚙️ Updating Preferences...")
    
    await hub.update_preferences(
        recipients[0].recipient_id,
        preferred_channels=[Channel.SLACK],
        unsubscribe_types=[NotificationType.MARKETING]
    )
    print(f"  ⚙️ Updated preferences for {recipients[0].user_id}")
    
    await hub.update_preferences(
        recipients[1].recipient_id,
        dnd=True
    )
    print(f"  ⚙️ Enabled DND for {recipients[1].user_id}")
    
    # Delivery stats
    print("\n📊 Delivery Statistics:")
    
    for notif in [alert_notif, maintenance_notif]:
        stats = hub.get_delivery_stats(notif.notification_id)
        
        if stats:
            print(f"\n  📊 {notif.subject[:40]}...")
            print(f"     Total: {stats['total_deliveries']} | Open: {stats['open_rate']:.1f}% | Click: {stats['click_rate']:.1f}%")
            
            print(f"     By Status:")
            for status, count in stats['by_status'].items():
                print(f"       {status}: {count}")
                
    # Recent deliveries
    print("\n📬 Recent Deliveries:")
    
    print("\n  ┌──────────────────────┬──────────┬──────────────┬────────┬────────┐")
    print("  │ Recipient            │ Channel  │ Status       │ Opened │ Clicked│")
    print("  ├──────────────────────┼──────────┼──────────────┼────────┼────────┤")
    
    for delivery in list(hub.deliveries.values())[:12]:
        recipient = hub.recipients.get(delivery.recipient_id)
        user = recipient.user_id if recipient else "Unknown"
        user = user[:20].ljust(20)
        
        channel = delivery.channel.value[:8].ljust(8)
        
        status_icons = {
            "pending": "⏳", "queued": "📤", "sent": "✉️",
            "delivered": "📬", "read": "👁️", "failed": "❌", "bounced": "↩️"
        }
        status = f"{status_icons.get(delivery.status.value, '⚪')} {delivery.status.value[:10]}".ljust(12)
        
        opened = "✅" if delivery.opened else "❌"
        clicked = "✅" if delivery.clicked else "❌"
        
        print(f"  │ {user} │ {channel} │ {status} │ {opened:^6} │ {clicked:^6} │")
        
    print("  └──────────────────────┴──────────┴──────────────┴────────┴────────┘")
    
    # Channel performance
    print("\n📊 Channel Performance:")
    
    stats = hub.get_statistics()
    
    for channel, count in stats['by_channel'].items():
        channel_deliveries = [d for d in hub.deliveries.values() if d.channel.value == channel]
        delivered = sum(1 for d in channel_deliveries if d.status in [DeliveryStatus.DELIVERED, DeliveryStatus.READ])
        opened = sum(1 for d in channel_deliveries if d.opened)
        
        delivery_rate = (delivered / max(count, 1)) * 100
        open_rate = (opened / max(delivered, 1)) * 100
        
        bar_delivery = "█" * int(delivery_rate / 10) + "░" * (10 - int(delivery_rate / 10))
        bar_open = "█" * int(open_rate / 10) + "░" * (10 - int(open_rate / 10))
        
        print(f"\n  📧 {channel.upper()}")
        print(f"     Total: {count}")
        print(f"     Delivery: [{bar_delivery}] {delivery_rate:.1f}%")
        print(f"     Open:     [{bar_open}] {open_rate:.1f}%")
        
    # Statistics
    print("\n📊 Hub Statistics:")
    
    print(f"\n  Total Templates: {stats['total_templates']}")
    print(f"  Total Recipients: {stats['total_recipients']}")
    print(f"  Total Rules: {stats['total_rules']}")
    
    print(f"\n  Total Notifications: {stats['total_notifications']}")
    print(f"  Total Deliveries: {stats['total_deliveries']}")
    
    print("\n  By Status:")
    for status, count in stats['by_status'].items():
        print(f"    {status}: {count}")
        
    print(f"\n  Sent: {stats['total_sent']}")
    print(f"  Delivered: {stats['total_delivered']}")
    print(f"  Failed: {stats['total_failed']}")
    
    print(f"\n  Delivery Rate: {stats['delivery_rate']:.1f}%")
    print(f"  Open Rate: {stats['open_rate']:.1f}%")
    print(f"  Click Rate: {stats['click_rate']:.1f}%")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Notification Hub Dashboard                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Notifications:         {stats['total_notifications']:>12}                          │")
    print(f"│ Total Deliveries:            {stats['total_deliveries']:>12}                          │")
    print(f"│ Total Recipients:            {stats['total_recipients']:>12}                          │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Delivery Rate:               {stats['delivery_rate']:>11.1f}%                          │")
    print(f"│ Open Rate:                   {stats['open_rate']:>11.1f}%                          │")
    print(f"│ Click Rate:                  {stats['click_rate']:>11.1f}%                          │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Notification Hub Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
