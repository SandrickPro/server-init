#!/usr/bin/env python3
"""
Server Init - Iteration 152: Alert Correlation Platform
Платформа корреляции алертов

Функционал:
- Alert Ingestion - приём алертов
- Pattern Detection - обнаружение паттернов
- Alert Correlation - корреляция алертов
- Root Cause Analysis - анализ первопричин
- Alert Suppression - подавление алертов
- Incident Grouping - группировка инцидентов
- Noise Reduction - уменьшение шума
- Escalation Management - управление эскалацией
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
import uuid
import random
from collections import defaultdict


class AlertSeverity(Enum):
    """Серьёзность алерта"""
    INFO = 0
    WARNING = 1
    MINOR = 2
    MAJOR = 3
    CRITICAL = 4


class AlertStatus(Enum):
    """Статус алерта"""
    FIRING = "firing"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ACKNOWLEDGED = "acknowledged"


class CorrelationType(Enum):
    """Тип корреляции"""
    TEMPORAL = "temporal"
    TOPOLOGICAL = "topological"
    CAUSAL = "causal"
    PATTERN = "pattern"
    SERVICE = "service"


class IncidentStatus(Enum):
    """Статус инцидента"""
    OPEN = "open"
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    RESOLVED = "resolved"


@dataclass
class Alert:
    """Алерт"""
    alert_id: str
    name: str = ""
    
    # Source
    source: str = ""
    service: str = ""
    host: str = ""
    
    # Severity
    severity: AlertSeverity = AlertSeverity.WARNING
    
    # Status
    status: AlertStatus = AlertStatus.FIRING
    
    # Content
    message: str = ""
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    
    # Timing
    fired_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    
    # Correlation
    fingerprint: str = ""
    correlation_id: str = ""
    parent_alert_id: str = ""
    
    # Metrics
    value: float = 0.0
    threshold: float = 0.0


@dataclass
class CorrelationRule:
    """Правило корреляции"""
    rule_id: str
    name: str = ""
    
    # Type
    correlation_type: CorrelationType = CorrelationType.TEMPORAL
    
    # Conditions
    conditions: List[Dict] = field(default_factory=list)
    
    # Time window
    time_window_seconds: int = 300
    
    # Priority
    priority: int = 0
    
    # Actions
    actions: List[str] = field(default_factory=list)
    
    # Statistics
    matches: int = 0
    
    # Status
    enabled: bool = True


@dataclass
class AlertPattern:
    """Паттерн алертов"""
    pattern_id: str
    name: str = ""
    
    # Pattern definition
    alert_sequence: List[str] = field(default_factory=list)  # Alert names in order
    time_window_seconds: int = 600
    
    # Detection
    detected_count: int = 0
    last_detected: Optional[datetime] = None
    
    # Root cause
    root_cause: str = ""
    remediation: str = ""


@dataclass
class CorrelatedGroup:
    """Группа коррелированных алертов"""
    group_id: str
    
    # Alerts
    alerts: List[Alert] = field(default_factory=list)
    
    # Correlation
    correlation_type: CorrelationType = CorrelationType.TEMPORAL
    correlation_reason: str = ""
    
    # Root cause
    root_cause_alert: str = ""
    
    # Severity (max of group)
    severity: AlertSeverity = AlertSeverity.WARNING
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    
    # Status
    status: str = "active"


@dataclass
class SuppressionRule:
    """Правило подавления"""
    rule_id: str
    name: str = ""
    
    # Conditions
    source_alert: str = ""  # Alert that triggers suppression
    suppressed_alerts: List[str] = field(default_factory=list)  # Alerts to suppress
    
    # Time
    duration_seconds: int = 300
    
    # Statistics
    suppressions_count: int = 0
    
    # Status
    enabled: bool = True
    expires_at: Optional[datetime] = None


@dataclass
class Incident:
    """Инцидент"""
    incident_id: str
    title: str = ""
    
    # Alerts
    related_alerts: List[str] = field(default_factory=list)
    alert_count: int = 0
    
    # Services
    affected_services: List[str] = field(default_factory=list)
    
    # Severity
    severity: AlertSeverity = AlertSeverity.WARNING
    
    # Status
    status: IncidentStatus = IncidentStatus.OPEN
    
    # Root cause
    root_cause: str = ""
    resolution: str = ""
    
    # Timeline
    created_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Assignees
    assignee: str = ""


@dataclass
class RootCauseAnalysis:
    """Анализ первопричин"""
    analysis_id: str
    incident_id: str = ""
    
    # Findings
    probable_cause: str = ""
    confidence: float = 0.0
    
    # Evidence
    supporting_alerts: List[str] = field(default_factory=list)
    timeline: List[Dict] = field(default_factory=list)
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    
    # Timestamp
    analyzed_at: datetime = field(default_factory=datetime.now)


class AlertIngester:
    """Приём алертов"""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.fingerprint_index: Dict[str, List[str]] = defaultdict(list)
        
    def ingest(self, alert_data: Dict) -> Alert:
        """Приём алерта"""
        alert = Alert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            name=alert_data.get("name", ""),
            source=alert_data.get("source", ""),
            service=alert_data.get("service", ""),
            host=alert_data.get("host", ""),
            severity=AlertSeverity[alert_data.get("severity", "WARNING").upper()],
            message=alert_data.get("message", ""),
            labels=alert_data.get("labels", {}),
            annotations=alert_data.get("annotations", {}),
            value=alert_data.get("value", 0.0),
            threshold=alert_data.get("threshold", 0.0)
        )
        
        # Generate fingerprint
        alert.fingerprint = self._generate_fingerprint(alert)
        
        # Deduplicate by fingerprint
        self.fingerprint_index[alert.fingerprint].append(alert.alert_id)
        
        self.alerts[alert.alert_id] = alert
        return alert
        
    def _generate_fingerprint(self, alert: Alert) -> str:
        """Генерация отпечатка"""
        components = [alert.name, alert.source, alert.service, alert.host]
        return uuid.uuid5(uuid.NAMESPACE_DNS, "|".join(components)).hex[:16]
        
    def resolve(self, alert_id: str) -> bool:
        """Разрешение алерта"""
        alert = self.alerts.get(alert_id)
        if alert:
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            return True
        return False
        
    def get_firing_alerts(self) -> List[Alert]:
        """Получение активных алертов"""
        return [a for a in self.alerts.values() if a.status == AlertStatus.FIRING]


class CorrelationEngine:
    """Движок корреляции"""
    
    def __init__(self):
        self.rules: Dict[str, CorrelationRule] = {}
        self.groups: Dict[str, CorrelatedGroup] = {}
        
    def add_rule(self, name: str, correlation_type: CorrelationType,
                  conditions: List[Dict], **kwargs) -> CorrelationRule:
        """Добавление правила"""
        rule = CorrelationRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name=name,
            correlation_type=correlation_type,
            conditions=conditions,
            **kwargs
        )
        self.rules[rule.rule_id] = rule
        return rule
        
    def correlate(self, alerts: List[Alert]) -> List[CorrelatedGroup]:
        """Корреляция алертов"""
        new_groups = []
        
        for rule in self.rules.values():
            if not rule.enabled:
                continue
                
            matching_alerts = self._match_rule(rule, alerts)
            
            if len(matching_alerts) >= 2:
                group = self._create_group(matching_alerts, rule)
                self.groups[group.group_id] = group
                new_groups.append(group)
                rule.matches += 1
                
        return new_groups
        
    def _match_rule(self, rule: CorrelationRule, alerts: List[Alert]) -> List[Alert]:
        """Проверка соответствия правилу"""
        matching = []
        
        for alert in alerts:
            for condition in rule.conditions:
                if self._check_condition(alert, condition):
                    matching.append(alert)
                    break
                    
        # Filter by time window
        if matching:
            now = datetime.now()
            window = timedelta(seconds=rule.time_window_seconds)
            matching = [a for a in matching if now - a.fired_at <= window]
            
        return matching
        
    def _check_condition(self, alert: Alert, condition: Dict) -> bool:
        """Проверка условия"""
        field = condition.get("field")
        operator = condition.get("operator", "equals")
        value = condition.get("value")
        
        alert_value = getattr(alert, field, None)
        if alert_value is None and field in alert.labels:
            alert_value = alert.labels[field]
            
        if alert_value is None:
            return False
            
        if hasattr(alert_value, 'name'):
            alert_value = alert_value.name
            
        if operator == "equals":
            return str(alert_value) == str(value)
        elif operator == "contains":
            return str(value) in str(alert_value)
        elif operator == "regex":
            import re
            return bool(re.match(value, str(alert_value)))
            
        return False
        
    def _create_group(self, alerts: List[Alert], rule: CorrelationRule) -> CorrelatedGroup:
        """Создание группы"""
        # Determine root cause (earliest alert)
        sorted_alerts = sorted(alerts, key=lambda a: a.fired_at)
        root_cause = sorted_alerts[0].alert_id if sorted_alerts else ""
        
        # Determine max severity
        max_severity = max(a.severity for a in alerts)
        
        group = CorrelatedGroup(
            group_id=f"grp_{uuid.uuid4().hex[:8]}",
            alerts=alerts,
            correlation_type=rule.correlation_type,
            correlation_reason=rule.name,
            root_cause_alert=root_cause,
            severity=max_severity
        )
        
        # Update alerts with correlation ID
        for alert in alerts:
            alert.correlation_id = group.group_id
            if alert.alert_id != root_cause:
                alert.parent_alert_id = root_cause
                
        return group


class PatternDetector:
    """Детектор паттернов"""
    
    def __init__(self):
        self.patterns: Dict[str, AlertPattern] = {}
        
    def add_pattern(self, name: str, alert_sequence: List[str],
                     **kwargs) -> AlertPattern:
        """Добавление паттерна"""
        pattern = AlertPattern(
            pattern_id=f"pat_{uuid.uuid4().hex[:8]}",
            name=name,
            alert_sequence=alert_sequence,
            **kwargs
        )
        self.patterns[pattern.pattern_id] = pattern
        return pattern
        
    def detect(self, alerts: List[Alert]) -> List[AlertPattern]:
        """Обнаружение паттернов"""
        detected = []
        
        # Sort by time
        sorted_alerts = sorted(alerts, key=lambda a: a.fired_at)
        alert_names = [a.name for a in sorted_alerts]
        
        for pattern in self.patterns.values():
            if self._match_sequence(alert_names, pattern.alert_sequence):
                pattern.detected_count += 1
                pattern.last_detected = datetime.now()
                detected.append(pattern)
                
        return detected
        
    def _match_sequence(self, alerts: List[str], sequence: List[str]) -> bool:
        """Проверка последовательности"""
        if len(sequence) > len(alerts):
            return False
            
        for i in range(len(alerts) - len(sequence) + 1):
            if alerts[i:i+len(sequence)] == sequence:
                return True
                
        return False


class SuppressionManager:
    """Менеджер подавления"""
    
    def __init__(self):
        self.rules: Dict[str, SuppressionRule] = {}
        self.active_suppressions: Dict[str, datetime] = {}
        
    def add_rule(self, name: str, source_alert: str,
                  suppressed_alerts: List[str], **kwargs) -> SuppressionRule:
        """Добавление правила"""
        rule = SuppressionRule(
            rule_id=f"sup_{uuid.uuid4().hex[:8]}",
            name=name,
            source_alert=source_alert,
            suppressed_alerts=suppressed_alerts,
            **kwargs
        )
        self.rules[rule.rule_id] = rule
        return rule
        
    def check_suppression(self, alert: Alert) -> bool:
        """Проверка подавления"""
        # Clean expired suppressions
        now = datetime.now()
        self.active_suppressions = {
            k: v for k, v in self.active_suppressions.items()
            if v > now
        }
        
        # Check if alert should be suppressed
        if alert.name in self.active_suppressions:
            alert.status = AlertStatus.SUPPRESSED
            return True
            
        return False
        
    def trigger_suppression(self, alert: Alert):
        """Активация подавления"""
        for rule in self.rules.values():
            if not rule.enabled:
                continue
                
            if alert.name == rule.source_alert:
                expires = datetime.now() + timedelta(seconds=rule.duration_seconds)
                
                for suppressed in rule.suppressed_alerts:
                    self.active_suppressions[suppressed] = expires
                    
                rule.suppressions_count += 1


class IncidentManager:
    """Менеджер инцидентов"""
    
    def __init__(self):
        self.incidents: Dict[str, Incident] = {}
        
    def create_incident(self, title: str, alerts: List[Alert],
                         **kwargs) -> Incident:
        """Создание инцидента"""
        services = list(set(a.service for a in alerts if a.service))
        max_severity = max(a.severity for a in alerts) if alerts else AlertSeverity.WARNING
        
        incident = Incident(
            incident_id=f"inc_{uuid.uuid4().hex[:8]}",
            title=title,
            related_alerts=[a.alert_id for a in alerts],
            alert_count=len(alerts),
            affected_services=services,
            severity=max_severity,
            **kwargs
        )
        self.incidents[incident.incident_id] = incident
        return incident
        
    def update_status(self, incident_id: str, status: IncidentStatus,
                       **kwargs) -> Optional[Incident]:
        """Обновление статуса"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return None
            
        incident.status = status
        
        if status == IncidentStatus.INVESTIGATING and not incident.acknowledged_at:
            incident.acknowledged_at = datetime.now()
            
        if status == IncidentStatus.RESOLVED:
            incident.resolved_at = datetime.now()
            
        for key, value in kwargs.items():
            if hasattr(incident, key):
                setattr(incident, key, value)
                
        return incident


class RootCauseAnalyzer:
    """Анализатор первопричин"""
    
    def __init__(self):
        self.knowledge_base: Dict[str, Dict] = {}
        
    def add_knowledge(self, pattern: str, cause: str,
                       recommendations: List[str]):
        """Добавление знаний"""
        self.knowledge_base[pattern] = {
            "cause": cause,
            "recommendations": recommendations
        }
        
    def analyze(self, group: CorrelatedGroup) -> RootCauseAnalysis:
        """Анализ группы алертов"""
        analysis = RootCauseAnalysis(
            analysis_id=f"rca_{uuid.uuid4().hex[:8]}"
        )
        
        # Find earliest alert
        if group.alerts:
            sorted_alerts = sorted(group.alerts, key=lambda a: a.fired_at)
            root_alert = sorted_alerts[0]
            
            # Build timeline
            for alert in sorted_alerts:
                analysis.timeline.append({
                    "time": alert.fired_at.isoformat(),
                    "alert": alert.name,
                    "service": alert.service,
                    "message": alert.message
                })
                
            # Check knowledge base
            for pattern, knowledge in self.knowledge_base.items():
                if pattern in root_alert.name:
                    analysis.probable_cause = knowledge["cause"]
                    analysis.recommendations = knowledge["recommendations"]
                    analysis.confidence = 0.8
                    break
                    
            if not analysis.probable_cause:
                analysis.probable_cause = f"Likely root cause: {root_alert.name}"
                analysis.confidence = 0.5
                analysis.recommendations = [
                    "Review alert timeline",
                    "Check related services",
                    "Examine logs around incident time"
                ]
                
            analysis.supporting_alerts = [a.alert_id for a in sorted_alerts]
            
        return analysis


class AlertCorrelationPlatform:
    """Платформа корреляции алертов"""
    
    def __init__(self):
        self.ingester = AlertIngester()
        self.correlation_engine = CorrelationEngine()
        self.pattern_detector = PatternDetector()
        self.suppression_manager = SuppressionManager()
        self.incident_manager = IncidentManager()
        self.rca_analyzer = RootCauseAnalyzer()
        
    async def process_alert(self, alert_data: Dict) -> Dict:
        """Обработка алерта"""
        result = {
            "alert": None,
            "suppressed": False,
            "correlated_group": None,
            "patterns_detected": [],
            "incident_created": None
        }
        
        # Ingest
        alert = self.ingester.ingest(alert_data)
        result["alert"] = alert
        
        # Check suppression
        if self.suppression_manager.check_suppression(alert):
            result["suppressed"] = True
            return result
            
        # Trigger suppression for others
        self.suppression_manager.trigger_suppression(alert)
        
        # Correlate
        firing = self.ingester.get_firing_alerts()
        groups = self.correlation_engine.correlate(firing)
        
        if groups:
            result["correlated_group"] = groups[-1]
            
        # Detect patterns
        patterns = self.pattern_detector.detect(firing)
        result["patterns_detected"] = patterns
        
        # Auto-create incident for critical alerts
        if alert.severity == AlertSeverity.CRITICAL and not alert.correlation_id:
            incident = self.incident_manager.create_incident(
                f"Critical Alert: {alert.name}",
                [alert]
            )
            result["incident_created"] = incident
            
        return result
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        alerts = list(self.ingester.alerts.values())
        
        return {
            "total_alerts": len(alerts),
            "firing_alerts": len([a for a in alerts if a.status == AlertStatus.FIRING]),
            "suppressed_alerts": len([a for a in alerts if a.status == AlertStatus.SUPPRESSED]),
            "resolved_alerts": len([a for a in alerts if a.status == AlertStatus.RESOLVED]),
            "correlation_rules": len(self.correlation_engine.rules),
            "correlated_groups": len(self.correlation_engine.groups),
            "patterns_defined": len(self.pattern_detector.patterns),
            "suppression_rules": len(self.suppression_manager.rules),
            "total_incidents": len(self.incident_manager.incidents),
            "open_incidents": len([i for i in self.incident_manager.incidents.values() 
                                   if i.status == IncidentStatus.OPEN])
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 152: Alert Correlation Platform")
    print("=" * 60)
    
    async def demo():
        platform = AlertCorrelationPlatform()
        print("✓ Alert Correlation Platform created")
        
        # Add knowledge base
        print("\n📚 Adding Knowledge Base...")
        
        platform.rca_analyzer.add_knowledge(
            "HighCPU",
            "CPU exhaustion due to runaway process or traffic spike",
            [
                "Check process list for high CPU consumers",
                "Review recent deployments",
                "Scale horizontally if traffic spike"
            ]
        )
        
        platform.rca_analyzer.add_knowledge(
            "HighMemory",
            "Memory leak or insufficient capacity",
            [
                "Check for memory leaks in application",
                "Review heap dumps",
                "Consider increasing memory limits"
            ]
        )
        
        platform.rca_analyzer.add_knowledge(
            "DatabaseConnection",
            "Database connection pool exhausted",
            [
                "Check connection pool settings",
                "Review slow queries",
                "Check database server health"
            ]
        )
        print("  ✓ Added 3 knowledge entries")
        
        # Add correlation rules
        print("\n📏 Adding Correlation Rules...")
        
        rules_data = [
            ("Same Service Rule", CorrelationType.SERVICE, 
             [{"field": "service", "operator": "equals", "value": "api-gateway"}]),
            ("Same Host Rule", CorrelationType.TOPOLOGICAL,
             [{"field": "host", "operator": "equals", "value": "host-1"}]),
            ("CPU Cascade", CorrelationType.CAUSAL,
             [{"field": "name", "operator": "contains", "value": "CPU"}])
        ]
        
        for name, ctype, conditions in rules_data:
            rule = platform.correlation_engine.add_rule(
                name, ctype, conditions,
                time_window_seconds=300
            )
            print(f"  ✓ {name}: {ctype.value}")
            
        # Add alert patterns
        print("\n🔍 Adding Alert Patterns...")
        
        pattern = platform.pattern_detector.add_pattern(
            "Database Cascade Failure",
            alert_sequence=["DatabaseConnectionError", "HighLatency", "ServiceUnavailable"],
            time_window_seconds=600,
            root_cause="Database connectivity issues",
            remediation="Check database cluster health and connection pools"
        )
        print(f"  ✓ {pattern.name}")
        
        # Add suppression rules
        print("\n🔇 Adding Suppression Rules...")
        
        supp_rule = platform.suppression_manager.add_rule(
            "Suppress Downstream on Primary Failure",
            source_alert="DatabaseConnectionError",
            suppressed_alerts=["HighLatency", "ServiceUnavailable", "TimeoutError"],
            duration_seconds=600
        )
        print(f"  ✓ {supp_rule.name}")
        
        # Simulate alerts
        print("\n📥 Processing Alerts...")
        
        alerts_data = [
            # First wave - database issues
            {"name": "DatabaseConnectionError", "service": "api-gateway", "host": "host-1",
             "severity": "CRITICAL", "message": "Cannot connect to database"},
            {"name": "HighLatency", "service": "api-gateway", "host": "host-1",
             "severity": "MAJOR", "message": "Response time > 5s"},
            {"name": "ServiceUnavailable", "service": "api-gateway", "host": "host-1",
             "severity": "CRITICAL", "message": "Service returning 503"},
             
            # Second wave - CPU issues on different service
            {"name": "HighCPU", "service": "worker-service", "host": "host-2",
             "severity": "WARNING", "message": "CPU usage > 90%"},
            {"name": "HighCPU", "service": "worker-service", "host": "host-3",
             "severity": "WARNING", "message": "CPU usage > 85%"},
            
            # Third wave - memory on another host
            {"name": "HighMemory", "service": "cache-service", "host": "host-4",
             "severity": "MINOR", "message": "Memory usage > 80%"},
            
            # Fourth wave - mixed
            {"name": "DiskSpaceLow", "service": "storage-service", "host": "host-5",
             "severity": "WARNING", "message": "Disk space < 20%"},
            {"name": "ErrorRateHigh", "service": "api-gateway", "host": "host-1",
             "severity": "MAJOR", "message": "Error rate > 5%"}
        ]
        
        results = []
        for alert_data in alerts_data:
            result = await platform.process_alert(alert_data)
            results.append(result)
            
            status = "SUPPRESSED" if result["suppressed"] else "PROCESSED"
            print(f"  {status}: {alert_data['name']} ({alert_data['service']})")
            
        # Show correlation groups
        print("\n🔗 Correlated Groups:")
        
        for group_id, group in platform.correlation_engine.groups.items():
            print(f"\n  Group: {group_id}")
            print(f"    Type: {group.correlation_type.value}")
            print(f"    Reason: {group.correlation_reason}")
            print(f"    Severity: {group.severity.name}")
            print(f"    Alerts: {len(group.alerts)}")
            
            for alert in group.alerts[:3]:
                is_root = "🎯" if alert.alert_id == group.root_cause_alert else "  "
                print(f"      {is_root} {alert.name} ({alert.service})")
                
        # Show detected patterns
        print("\n🎯 Detected Patterns:")
        
        for pattern in platform.pattern_detector.patterns.values():
            if pattern.detected_count > 0:
                print(f"  ✓ {pattern.name}: detected {pattern.detected_count}x")
                print(f"    Root cause: {pattern.root_cause}")
                
        # Show suppression stats
        print("\n🔇 Suppression Statistics:")
        
        for rule in platform.suppression_manager.rules.values():
            print(f"  {rule.name}: {rule.suppressions_count} suppressions")
            
        # Create incident from correlated group
        print("\n🚨 Creating Incident from Correlation...")
        
        if platform.correlation_engine.groups:
            first_group = list(platform.correlation_engine.groups.values())[0]
            incident = platform.incident_manager.create_incident(
                f"Correlated Alert Storm: {first_group.correlation_reason}",
                first_group.alerts
            )
            print(f"  ✓ Incident created: {incident.incident_id}")
            print(f"    Title: {incident.title}")
            print(f"    Alerts: {incident.alert_count}")
            print(f"    Services: {', '.join(incident.affected_services)}")
            
            # Run RCA
            print("\n🔬 Running Root Cause Analysis...")
            
            rca = platform.rca_analyzer.analyze(first_group)
            
            print(f"\n  Analysis ID: {rca.analysis_id}")
            print(f"  Probable Cause: {rca.probable_cause}")
            print(f"  Confidence: {rca.confidence * 100:.0f}%")
            print(f"  Recommendations:")
            for rec in rca.recommendations:
                print(f"    • {rec}")
                
            print(f"\n  Timeline:")
            for event in rca.timeline[:5]:
                print(f"    {event['time']}: {event['alert']} ({event['service']})")
                
        # Update incident
        print("\n📝 Updating Incident Status...")
        
        if platform.incident_manager.incidents:
            incident_id = list(platform.incident_manager.incidents.keys())[0]
            platform.incident_manager.update_status(
                incident_id,
                IncidentStatus.INVESTIGATING,
                assignee="oncall@company.com"
            )
            print(f"  ✓ Status updated to INVESTIGATING")
            
        # Alert overview
        print("\n📊 Alert Overview:")
        
        severity_counts = defaultdict(int)
        status_counts = defaultdict(int)
        
        for alert in platform.ingester.alerts.values():
            severity_counts[alert.severity.name] += 1
            status_counts[alert.status.value] += 1
            
        print("\n  By Severity:")
        for sev in ["CRITICAL", "MAJOR", "MINOR", "WARNING", "INFO"]:
            count = severity_counts.get(sev, 0)
            if count:
                bar = "█" * count
                print(f"    {sev:10}: {count:2} {bar}")
                
        print("\n  By Status:")
        for status, count in status_counts.items():
            print(f"    {status:12}: {count}")
            
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Alerts: {stats['total_alerts']}")
        print(f"  Firing: {stats['firing_alerts']}")
        print(f"  Suppressed: {stats['suppressed_alerts']}")
        print(f"  Resolved: {stats['resolved_alerts']}")
        print(f"  Correlation Rules: {stats['correlation_rules']}")
        print(f"  Correlated Groups: {stats['correlated_groups']}")
        print(f"  Total Incidents: {stats['total_incidents']}")
        print(f"  Open Incidents: {stats['open_incidents']}")
        
        # Dashboard
        print("\n📋 Alert Correlation Dashboard:")
        print("  ┌────────────────────────────────────────────────────────────┐")
        print("  │               Alert Correlation Overview                   │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Alerts:          {stats['total_alerts']:>10}                    │")
        print(f"  │ Firing:                {stats['firing_alerts']:>10}                    │")
        print(f"  │ Suppressed:            {stats['suppressed_alerts']:>10}                    │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Correlation Rules:     {stats['correlation_rules']:>10}                    │")
        print(f"  │ Correlated Groups:     {stats['correlated_groups']:>10}                    │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Incidents:       {stats['total_incidents']:>10}                    │")
        print(f"  │ Open Incidents:        {stats['open_incidents']:>10}                    │")
        print("  └────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Alert Correlation Platform initialized!")
    print("=" * 60)
