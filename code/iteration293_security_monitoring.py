#!/usr/bin/env python3
"""
Server Init - Iteration 293: Security Monitoring Platform
Платформа Security Monitoring

Функционал:
- Threat Detection - обнаружение угроз
- Intrusion Detection - обнаружение вторжений
- Vulnerability Scanning - сканирование уязвимостей
- Security Events - события безопасности
- Compliance Monitoring - мониторинг соответствия
- Access Audit - аудит доступа
- Incident Management - управление инцидентами
- Risk Assessment - оценка рисков
"""

import asyncio
import random
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import hashlib


class ThreatLevel(Enum):
    """Уровень угрозы"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(Enum):
    """Тип угрозы"""
    MALWARE = "malware"
    INTRUSION = "intrusion"
    DOS = "dos"
    BRUTE_FORCE = "brute_force"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"


class VulnerabilitySeverity(Enum):
    """Серьёзность уязвимости"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventType(Enum):
    """Тип события безопасности"""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    PERMISSION_CHANGE = "permission_change"
    FILE_ACCESS = "file_access"
    NETWORK_CONNECTION = "network_connection"
    PROCESS_EXECUTION = "process_execution"
    CONFIG_CHANGE = "config_change"
    FIREWALL_BLOCK = "firewall_block"


class IncidentStatus(Enum):
    """Статус инцидента"""
    NEW = "new"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    CLOSED = "closed"


class ComplianceStatus(Enum):
    """Статус соответствия"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL = "partial"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class Threat:
    """Угроза"""
    threat_id: str
    
    # Type
    threat_type: ThreatType = ThreatType.SUSPICIOUS_ACTIVITY
    level: ThreatLevel = ThreatLevel.MEDIUM
    
    # Source
    source_ip: str = ""
    source_host: str = ""
    
    # Target
    target_ip: str = ""
    target_host: str = ""
    target_port: int = 0
    
    # Details
    description: str = ""
    signature: str = ""
    payload: str = ""
    
    # Status
    blocked: bool = False
    acknowledged: bool = False
    
    # Timing
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class Vulnerability:
    """Уязвимость"""
    vuln_id: str
    cve_id: str = ""
    
    # Severity
    severity: VulnerabilitySeverity = VulnerabilitySeverity.MEDIUM
    cvss_score: float = 0.0
    
    # Affected
    affected_host: str = ""
    affected_software: str = ""
    affected_version: str = ""
    
    # Details
    title: str = ""
    description: str = ""
    solution: str = ""
    
    # Status
    fixed: bool = False
    
    # Timing
    discovered_at: datetime = field(default_factory=datetime.now)
    published_at: Optional[datetime] = None


@dataclass
class SecurityEvent:
    """Событие безопасности"""
    event_id: str
    
    # Type
    event_type: EventType = EventType.NETWORK_CONNECTION
    
    # Source
    source_ip: str = ""
    source_user: str = ""
    source_host: str = ""
    
    # Target
    target_resource: str = ""
    target_host: str = ""
    
    # Details
    action: str = ""
    result: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Risk
    risk_score: float = 0.0
    
    # Timing
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SecurityIncident:
    """Инцидент безопасности"""
    incident_id: str
    
    # Type
    title: str = ""
    severity: ThreatLevel = ThreatLevel.MEDIUM
    
    # Status
    status: IncidentStatus = IncidentStatus.NEW
    
    # Related
    threats: List[str] = field(default_factory=list)
    events: List[str] = field(default_factory=list)
    affected_hosts: List[str] = field(default_factory=list)
    
    # Assignment
    assigned_to: str = ""
    
    # Notes
    notes: List[str] = field(default_factory=list)
    
    # Timeline
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


@dataclass
class ComplianceRule:
    """Правило соответствия"""
    rule_id: str
    framework: str  # e.g., PCI-DSS, HIPAA, SOC2
    
    # Rule
    control_id: str = ""
    title: str = ""
    description: str = ""
    
    # Status
    status: ComplianceStatus = ComplianceStatus.NOT_APPLICABLE
    
    # Evidence
    evidence: List[str] = field(default_factory=list)
    
    # Last check
    last_checked: Optional[datetime] = None


@dataclass
class AccessLog:
    """Лог доступа"""
    log_id: str
    
    # User
    user: str = ""
    user_role: str = ""
    
    # Resource
    resource: str = ""
    action: str = ""
    
    # Result
    allowed: bool = True
    reason: str = ""
    
    # Context
    ip_address: str = ""
    user_agent: str = ""
    
    # Timing
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RiskAssessment:
    """Оценка риска"""
    host: str
    
    # Scores
    overall_score: float = 0.0
    threat_score: float = 0.0
    vulnerability_score: float = 0.0
    compliance_score: float = 0.0
    
    # Counts
    critical_vulns: int = 0
    high_vulns: int = 0
    active_threats: int = 0
    compliance_failures: int = 0


class SecurityMonitoringManager:
    """Менеджер Security Monitoring"""
    
    def __init__(self):
        self.threats: Dict[str, Threat] = {}
        self.vulnerabilities: Dict[str, Vulnerability] = {}
        self.events: List[SecurityEvent] = []
        self.incidents: Dict[str, SecurityIncident] = {}
        self.compliance_rules: Dict[str, ComplianceRule] = {}
        self.access_logs: List[AccessLog] = []
        
        # Known signatures
        self.threat_signatures: Dict[str, ThreatType] = {
            "SYN_FLOOD": ThreatType.DOS,
            "BRUTE_FORCE_SSH": ThreatType.BRUTE_FORCE,
            "SQL_INJECTION": ThreatType.INTRUSION,
            "XSS_ATTACK": ThreatType.INTRUSION,
            "RANSOMWARE_BEHAVIOR": ThreatType.MALWARE
        }
        
        # Stats
        self.total_threats_detected: int = 0
        self.total_threats_blocked: int = 0
        self.total_scans: int = 0
        
    async def detect_threat(self, source_ip: str,
                           target_ip: str,
                           threat_type: ThreatType,
                           level: ThreatLevel,
                           description: str = "",
                           signature: str = "") -> Threat:
        """Обнаружение угрозы"""
        threat = Threat(
            threat_id=f"thr_{uuid.uuid4().hex[:8]}",
            threat_type=threat_type,
            level=level,
            source_ip=source_ip,
            target_ip=target_ip,
            description=description,
            signature=signature
        )
        
        self.threats[threat.threat_id] = threat
        self.total_threats_detected += 1
        
        # Auto-block critical threats
        if level == ThreatLevel.CRITICAL:
            threat.blocked = True
            self.total_threats_blocked += 1
            
        # Create incident for high/critical
        if level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            await self._create_incident_from_threat(threat)
            
        return threat
        
    async def scan_vulnerabilities(self, host: str) -> List[Vulnerability]:
        """Сканирование уязвимостей"""
        self.total_scans += 1
        
        # Simulate vulnerability scan
        vuln_samples = [
            ("CVE-2023-1234", VulnerabilitySeverity.CRITICAL, 9.8, "Remote Code Execution", "nginx"),
            ("CVE-2023-5678", VulnerabilitySeverity.HIGH, 7.5, "SQL Injection", "postgresql"),
            ("CVE-2022-9012", VulnerabilitySeverity.MEDIUM, 5.3, "Information Disclosure", "openssl"),
            ("CVE-2023-3456", VulnerabilitySeverity.LOW, 3.1, "Denial of Service", "redis"),
            ("CVE-2023-7890", VulnerabilitySeverity.HIGH, 8.1, "Authentication Bypass", "nodejs")
        ]
        
        found = []
        num_vulns = random.randint(0, 3)
        
        for _ in range(num_vulns):
            sample = random.choice(vuln_samples)
            
            vuln = Vulnerability(
                vuln_id=f"vuln_{uuid.uuid4().hex[:8]}",
                cve_id=sample[0],
                severity=sample[1],
                cvss_score=sample[2],
                title=sample[3],
                affected_host=host,
                affected_software=sample[4],
                description=f"Vulnerability in {sample[4]}",
                solution="Update to latest version"
            )
            
            self.vulnerabilities[vuln.vuln_id] = vuln
            found.append(vuln)
            
        return found
        
    async def record_event(self, event_type: EventType,
                          source_ip: str = "",
                          source_user: str = "",
                          target_resource: str = "",
                          action: str = "",
                          result: str = "success",
                          details: Dict[str, Any] = None) -> SecurityEvent:
        """Запись события безопасности"""
        # Calculate risk score
        risk_score = self._calculate_event_risk(event_type, result)
        
        event = SecurityEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            source_ip=source_ip,
            source_user=source_user,
            target_resource=target_resource,
            action=action,
            result=result,
            details=details or {},
            risk_score=risk_score
        )
        
        self.events.append(event)
        
        # Keep only last 10000 events
        if len(self.events) > 10000:
            self.events = self.events[-10000:]
            
        # Check for anomalies
        if risk_score > 70:
            await self.detect_threat(
                source_ip,
                "",
                ThreatType.SUSPICIOUS_ACTIVITY,
                ThreatLevel.HIGH if risk_score > 85 else ThreatLevel.MEDIUM,
                f"High risk event: {event_type.value}"
            )
            
        return event
        
    async def log_access(self, user: str,
                        resource: str,
                        action: str,
                        allowed: bool = True,
                        ip_address: str = "",
                        reason: str = "") -> AccessLog:
        """Логирование доступа"""
        log = AccessLog(
            log_id=f"log_{uuid.uuid4().hex[:8]}",
            user=user,
            resource=resource,
            action=action,
            allowed=allowed,
            reason=reason,
            ip_address=ip_address
        )
        
        self.access_logs.append(log)
        
        if len(self.access_logs) > 10000:
            self.access_logs = self.access_logs[-10000:]
            
        # Record as security event
        await self.record_event(
            EventType.FILE_ACCESS if "file" in resource.lower() else EventType.PERMISSION_CHANGE,
            source_ip=ip_address,
            source_user=user,
            target_resource=resource,
            action=action,
            result="success" if allowed else "denied"
        )
        
        return log
        
    async def add_compliance_rule(self, framework: str,
                                 control_id: str,
                                 title: str,
                                 description: str = "") -> ComplianceRule:
        """Добавление правила соответствия"""
        rule = ComplianceRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            framework=framework,
            control_id=control_id,
            title=title,
            description=description
        )
        
        self.compliance_rules[rule.rule_id] = rule
        return rule
        
    async def check_compliance(self, rule_id: str) -> ComplianceStatus:
        """Проверка соответствия"""
        rule = self.compliance_rules.get(rule_id)
        if not rule:
            return ComplianceStatus.NOT_APPLICABLE
            
        # Simulate compliance check
        await asyncio.sleep(0.01)
        
        result = random.choices(
            [ComplianceStatus.COMPLIANT, ComplianceStatus.NON_COMPLIANT, ComplianceStatus.PARTIAL],
            weights=[0.7, 0.15, 0.15]
        )[0]
        
        rule.status = result
        rule.last_checked = datetime.now()
        
        if result == ComplianceStatus.COMPLIANT:
            rule.evidence.append(f"Check passed at {datetime.now()}")
            
        return result
        
    async def _create_incident_from_threat(self, threat: Threat) -> SecurityIncident:
        """Создание инцидента из угрозы"""
        incident = SecurityIncident(
            incident_id=f"inc_{uuid.uuid4().hex[:8]}",
            title=f"Detected {threat.threat_type.value}: {threat.description[:50]}",
            severity=threat.level,
            threats=[threat.threat_id],
            affected_hosts=[threat.target_ip] if threat.target_ip else []
        )
        
        self.incidents[incident.incident_id] = incident
        return incident
        
    async def create_incident(self, title: str,
                             severity: ThreatLevel,
                             description: str = "") -> SecurityIncident:
        """Создание инцидента"""
        incident = SecurityIncident(
            incident_id=f"inc_{uuid.uuid4().hex[:8]}",
            title=title,
            severity=severity,
            notes=[description] if description else []
        )
        
        self.incidents[incident.incident_id] = incident
        return incident
        
    async def update_incident(self, incident_id: str,
                             status: IncidentStatus = None,
                             assigned_to: str = None,
                             note: str = None):
        """Обновление инцидента"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return
            
        if status:
            incident.status = status
            if status == IncidentStatus.RESOLVED:
                incident.resolved_at = datetime.now()
                
        if assigned_to:
            incident.assigned_to = assigned_to
            
        if note:
            incident.notes.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {note}")
            
    def _calculate_event_risk(self, event_type: EventType, result: str) -> float:
        """Расчёт риска события"""
        base_risk = {
            EventType.LOGIN_SUCCESS: 10,
            EventType.LOGIN_FAILURE: 40,
            EventType.PERMISSION_CHANGE: 50,
            EventType.FILE_ACCESS: 20,
            EventType.NETWORK_CONNECTION: 15,
            EventType.PROCESS_EXECUTION: 30,
            EventType.CONFIG_CHANGE: 60,
            EventType.FIREWALL_BLOCK: 70
        }
        
        risk = base_risk.get(event_type, 25)
        
        if result != "success":
            risk += 20
            
        # Add some randomness
        risk += random.uniform(-10, 10)
        
        return max(0, min(100, risk))
        
    def assess_risk(self, host: str) -> RiskAssessment:
        """Оценка риска хоста"""
        assessment = RiskAssessment(host=host)
        
        # Count vulnerabilities
        for vuln in self.vulnerabilities.values():
            if vuln.affected_host == host and not vuln.fixed:
                if vuln.severity == VulnerabilitySeverity.CRITICAL:
                    assessment.critical_vulns += 1
                elif vuln.severity == VulnerabilitySeverity.HIGH:
                    assessment.high_vulns += 1
                    
        # Count active threats
        for threat in self.threats.values():
            if threat.target_ip == host and not threat.blocked:
                assessment.active_threats += 1
                
        # Count compliance failures
        for rule in self.compliance_rules.values():
            if rule.status == ComplianceStatus.NON_COMPLIANT:
                assessment.compliance_failures += 1
                
        # Calculate scores
        assessment.vulnerability_score = min(100, assessment.critical_vulns * 30 + assessment.high_vulns * 15)
        assessment.threat_score = min(100, assessment.active_threats * 25)
        assessment.compliance_score = min(100, assessment.compliance_failures * 20)
        
        assessment.overall_score = (
            assessment.vulnerability_score * 0.4 +
            assessment.threat_score * 0.35 +
            assessment.compliance_score * 0.25
        )
        
        return assessment
        
    def get_active_threats(self) -> List[Threat]:
        """Активные угрозы"""
        return [t for t in self.threats.values() if not t.blocked and not t.acknowledged]
        
    def get_open_incidents(self) -> List[SecurityIncident]:
        """Открытые инциденты"""
        return [i for i in self.incidents.values() 
                if i.status not in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]]
                
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        active_threats = len(self.get_active_threats())
        open_incidents = len(self.get_open_incidents())
        
        critical_vulns = sum(1 for v in self.vulnerabilities.values()
                           if v.severity == VulnerabilitySeverity.CRITICAL and not v.fixed)
        high_vulns = sum(1 for v in self.vulnerabilities.values()
                        if v.severity == VulnerabilitySeverity.HIGH and not v.fixed)
                        
        compliant = sum(1 for r in self.compliance_rules.values()
                       if r.status == ComplianceStatus.COMPLIANT)
        total_rules = len(self.compliance_rules)
        
        return {
            "total_threats": len(self.threats),
            "active_threats": active_threats,
            "blocked_threats": self.total_threats_blocked,
            "total_vulnerabilities": len(self.vulnerabilities),
            "critical_vulns": critical_vulns,
            "high_vulns": high_vulns,
            "total_events": len(self.events),
            "open_incidents": open_incidents,
            "compliance_rate": compliant / total_rules * 100 if total_rules else 0,
            "total_scans": self.total_scans
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 293: Security Monitoring Platform")
    print("=" * 60)
    
    manager = SecurityMonitoringManager()
    print("✓ Security Monitoring Manager created")
    
    # Detect threats
    print("\n🛡️ Detecting Threats...")
    
    threats_data = [
        ("192.168.1.100", "10.0.1.10", ThreatType.BRUTE_FORCE, ThreatLevel.HIGH, "SSH brute force attempt"),
        ("45.33.32.156", "10.0.1.10", ThreatType.INTRUSION, ThreatLevel.CRITICAL, "SQL injection detected"),
        ("89.248.172.16", "10.0.2.10", ThreatType.DOS, ThreatLevel.MEDIUM, "SYN flood attack"),
        ("185.220.101.35", "10.0.1.11", ThreatType.MALWARE, ThreatLevel.HIGH, "Ransomware behavior detected"),
        ("10.0.100.50", "10.0.3.10", ThreatType.DATA_EXFILTRATION, ThreatLevel.CRITICAL, "Large data transfer to external IP")
    ]
    
    for src, tgt, ttype, level, desc in threats_data:
        threat = await manager.detect_threat(src, tgt, ttype, level, desc)
        status = "BLOCKED" if threat.blocked else "ACTIVE"
        print(f"  🚨 {ttype.value}: {desc} [{status}]")
        
    # Scan vulnerabilities
    print("\n🔍 Scanning Vulnerabilities...")
    
    hosts_to_scan = ["web-server-01", "app-server-01", "db-server-01", "cache-server-01"]
    
    all_vulns = []
    for host in hosts_to_scan:
        vulns = await manager.scan_vulnerabilities(host)
        all_vulns.extend(vulns)
        print(f"  🔍 {host}: {len(vulns)} vulnerabilities found")
        
    # Record security events
    print("\n📋 Recording Security Events...")
    
    events_data = [
        (EventType.LOGIN_SUCCESS, "10.0.1.100", "admin", "/admin", "login"),
        (EventType.LOGIN_FAILURE, "192.168.1.50", "root", "/ssh", "login"),
        (EventType.LOGIN_FAILURE, "192.168.1.50", "root", "/ssh", "login"),
        (EventType.PERMISSION_CHANGE, "10.0.1.10", "admin", "/etc/passwd", "modify"),
        (EventType.FILE_ACCESS, "10.0.2.10", "app_user", "/data/secrets", "read"),
        (EventType.CONFIG_CHANGE, "10.0.1.10", "admin", "/nginx.conf", "update"),
        (EventType.FIREWALL_BLOCK, "89.248.172.16", "", "port 22", "blocked")
    ]
    
    for etype, ip, user, resource, action in events_data:
        event = await manager.record_event(etype, ip, user, resource, action)
        print(f"  📋 {etype.value}: {user or ip} -> {resource}")
        
    # Log access
    print("\n🔐 Logging Access...")
    
    access_data = [
        ("admin", "/admin/users", "read", True, "10.0.1.100"),
        ("user1", "/api/data", "read", True, "10.0.2.50"),
        ("guest", "/admin/settings", "write", False, "192.168.1.200"),
        ("app_service", "/database/backup", "read", True, "10.0.3.10")
    ]
    
    for user, resource, action, allowed, ip in access_data:
        log = await manager.log_access(user, resource, action, allowed, ip)
        status = "✅" if allowed else "❌"
        print(f"  {status} {user} -> {resource} ({action})")
        
    # Add compliance rules
    print("\n📜 Adding Compliance Rules...")
    
    compliance_data = [
        ("PCI-DSS", "1.1", "Install and maintain firewall"),
        ("PCI-DSS", "2.1", "Change default passwords"),
        ("PCI-DSS", "3.4", "Encrypt stored cardholder data"),
        ("SOC2", "CC6.1", "Access control policies"),
        ("SOC2", "CC7.2", "System monitoring"),
        ("HIPAA", "164.312", "Access controls for PHI")
    ]
    
    for framework, control_id, title in compliance_data:
        rule = await manager.add_compliance_rule(framework, control_id, title)
        await manager.check_compliance(rule.rule_id)
        print(f"  📜 {framework} {control_id}: {rule.status.value}")
        
    # Create incident
    print("\n🚨 Managing Incidents...")
    
    incident = await manager.create_incident(
        "Multiple login failures detected",
        ThreatLevel.HIGH,
        "Potential brute force attack on SSH"
    )
    await manager.update_incident(
        incident.incident_id,
        status=IncidentStatus.INVESTIGATING,
        assigned_to="security_team",
        note="Investigating source IPs"
    )
    print(f"  🚨 Incident created: {incident.incident_id}")
    print(f"     Status: {incident.status.value}")
    print(f"     Assigned: {incident.assigned_to}")
    
    # Active threats
    print("\n🛡️ Active Threats:")
    
    active_threats = manager.get_active_threats()
    
    print("\n  ┌────────────────────────┬────────────────────┬────────────┬─────────────────────────────────┐")
    print("  │ Type                   │ Source IP          │ Level      │ Description                     │")
    print("  ├────────────────────────┼────────────────────┼────────────┼─────────────────────────────────┤")
    
    for threat in active_threats[:5]:
        ttype = threat.threat_type.value[:22].ljust(22)
        src = threat.source_ip[:18].ljust(18)
        level_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
        level_icon = level_icons.get(threat.level.value, "⚪")
        level = threat.level.value[:10].ljust(10)
        desc = threat.description[:31].ljust(31)
        
        print(f"  │ {ttype} │ {src} │ {level_icon}{level[:9]} │ {desc} │")
        
    print("  └────────────────────────┴────────────────────┴────────────┴─────────────────────────────────┘")
    
    # Vulnerabilities
    print("\n🔍 Vulnerabilities:")
    
    print("\n  ┌────────────────────┬────────────────────────┬────────────┬─────────┬─────────────────────────┐")
    print("  │ CVE ID             │ Host                   │ Severity   │ CVSS    │ Software                │")
    print("  ├────────────────────┼────────────────────────┼────────────┼─────────┼─────────────────────────┤")
    
    for vuln in list(manager.vulnerabilities.values())[:5]:
        cve = vuln.cve_id[:18].ljust(18)
        host = vuln.affected_host[:22].ljust(22)
        sev_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢", "info": "ℹ️"}
        sev_icon = sev_icons.get(vuln.severity.value, "⚪")
        sev = vuln.severity.value[:10].ljust(10)
        cvss = f"{vuln.cvss_score:.1f}".ljust(7)
        soft = vuln.affected_software[:23].ljust(23)
        
        print(f"  │ {cve} │ {host} │ {sev_icon}{sev[:9]} │ {cvss} │ {soft} │")
        
    print("  └────────────────────┴────────────────────────┴────────────┴─────────┴─────────────────────────┘")
    
    # Recent events
    print("\n📋 Recent Security Events:")
    
    for event in manager.events[-5:]:
        risk_icon = "🔴" if event.risk_score > 70 else "🟡" if event.risk_score > 40 else "🟢"
        print(f"  {risk_icon} {event.event_type.value}: {event.source_user or event.source_ip} -> {event.target_resource}")
        
    # Compliance status
    print("\n📜 Compliance Status:")
    
    frameworks = {}
    for rule in manager.compliance_rules.values():
        if rule.framework not in frameworks:
            frameworks[rule.framework] = {"compliant": 0, "total": 0}
        frameworks[rule.framework]["total"] += 1
        if rule.status == ComplianceStatus.COMPLIANT:
            frameworks[rule.framework]["compliant"] += 1
            
    for fw, counts in frameworks.items():
        rate = counts['compliant'] / counts['total'] * 100
        bar_len = 20
        filled = int(rate / 100 * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"  {fw}: [{bar}] {rate:.0f}% ({counts['compliant']}/{counts['total']})")
        
    # Open incidents
    print("\n🚨 Open Incidents:")
    
    open_incidents = manager.get_open_incidents()
    
    for incident in open_incidents[:5]:
        sev_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
        icon = sev_icons.get(incident.severity.value, "⚪")
        print(f"  {icon} [{incident.status.value}] {incident.title}")
        if incident.assigned_to:
            print(f"     Assigned to: {incident.assigned_to}")
            
    # Risk assessment
    print("\n📊 Risk Assessment:")
    
    for host in hosts_to_scan[:3]:
        assessment = manager.assess_risk(host)
        risk_icon = "🔴" if assessment.overall_score > 70 else "🟡" if assessment.overall_score > 40 else "🟢"
        print(f"\n  {risk_icon} {host}:")
        print(f"    Overall Risk: {assessment.overall_score:.1f}")
        print(f"    Vulnerabilities: {assessment.critical_vulns} critical, {assessment.high_vulns} high")
        print(f"    Active Threats: {assessment.active_threats}")
        
    # Statistics
    print("\n📊 Security Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Threats Detected: {stats['total_threats']}")
    print(f"  Active Threats: {stats['active_threats']}")
    print(f"  Blocked Threats: {stats['blocked_threats']}")
    print(f"\n  Total Vulnerabilities: {stats['total_vulnerabilities']}")
    print(f"  Critical: {stats['critical_vulns']}, High: {stats['high_vulns']}")
    print(f"\n  Security Events: {stats['total_events']}")
    print(f"  Open Incidents: {stats['open_incidents']}")
    print(f"  Compliance Rate: {stats['compliance_rate']:.1f}%")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Security Monitoring Dashboard                     │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Active Threats:                {stats['active_threats']:>12}                        │")
    print(f"│ Critical Vulnerabilities:      {stats['critical_vulns']:>12}                        │")
    print(f"│ Open Incidents:                {stats['open_incidents']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Blocked Threats:               {stats['blocked_threats']:>12}                        │")
    print(f"│ Security Events:               {stats['total_events']:>12}                        │")
    print(f"│ Compliance Rate:               {stats['compliance_rate']:>11.1f}%                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Security Monitoring Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
