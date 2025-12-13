#!/usr/bin/env python3
"""
Server Init - Iteration 105: Compliance Automation Platform
Платформа автоматизации комплаенса

Функционал:
- Policy as Code - политики как код
- Compliance Frameworks - фреймворки (SOC2, HIPAA, PCI-DSS, GDPR)
- Continuous Compliance - непрерывная проверка
- Evidence Collection - сбор доказательств
- Audit Trail - аудит действий
- Risk Assessment - оценка рисков
- Remediation - автоматическое исправление
- Reporting - отчётность
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


class ComplianceFramework(Enum):
    """Фреймворк комплаенса"""
    SOC2 = "soc2"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    GDPR = "gdpr"
    ISO27001 = "iso27001"
    NIST = "nist"
    CIS = "cis"
    CUSTOM = "custom"


class ControlStatus(Enum):
    """Статус контроля"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_APPLICABLE = "not_applicable"
    PENDING = "pending"


class Severity(Enum):
    """Критичность"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ResourceType(Enum):
    """Тип ресурса"""
    COMPUTE = "compute"
    STORAGE = "storage"
    DATABASE = "database"
    NETWORK = "network"
    IAM = "iam"
    SECRETS = "secrets"
    LOGGING = "logging"
    ENCRYPTION = "encryption"


@dataclass
class Policy:
    """Политика комплаенса"""
    policy_id: str
    
    # Basic info
    name: str = ""
    description: str = ""
    
    # Classification
    framework: ComplianceFramework = ComplianceFramework.CUSTOM
    control_id: str = ""  # e.g., "CC6.1" for SOC2
    
    # Severity
    severity: Severity = Severity.MEDIUM
    
    # Check
    resource_type: ResourceType = ResourceType.COMPUTE
    check_function: Optional[Callable] = None
    check_query: str = ""  # for OPA/Rego
    
    # Remediation
    remediation_steps: List[str] = field(default_factory=list)
    auto_remediate: bool = False
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Status
    enabled: bool = True


@dataclass
class Control:
    """Контроль"""
    control_id: str
    
    # Basic info
    name: str = ""
    description: str = ""
    
    # Framework
    framework: ComplianceFramework = ComplianceFramework.CUSTOM
    
    # Category
    category: str = ""
    
    # Requirements
    requirements: List[str] = field(default_factory=list)
    
    # Related policies
    policies: List[str] = field(default_factory=list)
    
    # Status
    status: ControlStatus = ControlStatus.PENDING
    compliance_percentage: float = 0.0


@dataclass
class Finding:
    """Находка (нарушение)"""
    finding_id: str
    
    # Policy
    policy_id: str = ""
    policy_name: str = ""
    
    # Resource
    resource_id: str = ""
    resource_type: ResourceType = ResourceType.COMPUTE
    
    # Details
    title: str = ""
    description: str = ""
    severity: Severity = Severity.MEDIUM
    
    # Evidence
    evidence: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    status: str = "open"  # open, remediated, suppressed, accepted_risk
    
    # Timestamps
    detected_at: datetime = field(default_factory=datetime.now)
    remediated_at: Optional[datetime] = None
    
    # Remediation
    remediation_steps: List[str] = field(default_factory=list)


@dataclass
class Evidence:
    """Доказательство"""
    evidence_id: str
    
    # Control
    control_id: str = ""
    
    # Type
    evidence_type: str = ""  # screenshot, log, config, report
    
    # Content
    title: str = ""
    description: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Attachments
    attachments: List[str] = field(default_factory=list)
    
    # Timestamps
    collected_at: datetime = field(default_factory=datetime.now)
    valid_until: Optional[datetime] = None
    
    # Collector
    collected_by: str = ""


@dataclass
class AuditEntry:
    """Запись аудита"""
    entry_id: str
    
    # Action
    action: str = ""
    actor: str = ""
    
    # Target
    resource_type: str = ""
    resource_id: str = ""
    
    # Details
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Result
    success: bool = True
    error: Optional[str] = None


@dataclass
class RiskAssessment:
    """Оценка рисков"""
    assessment_id: str
    
    # Resource
    resource_id: str = ""
    resource_type: ResourceType = ResourceType.COMPUTE
    
    # Risk scores
    likelihood: float = 0.0  # 0-1
    impact: float = 0.0  # 0-1
    risk_score: float = 0.0  # calculated
    
    # Classification
    risk_level: str = ""  # critical, high, medium, low
    
    # Findings
    findings_count: int = 0
    critical_findings: int = 0
    
    # Mitigations
    mitigations: List[str] = field(default_factory=list)
    
    # Timestamp
    assessed_at: datetime = field(default_factory=datetime.now)


class PolicyEngine:
    """Движок политик"""
    
    def __init__(self):
        self.policies: Dict[str, Policy] = {}
        
    def register_policy(self, name: str, framework: ComplianceFramework,
                         control_id: str, resource_type: ResourceType,
                         severity: Severity,
                         check_function: Callable = None,
                         **kwargs) -> Policy:
        """Регистрация политики"""
        policy = Policy(
            policy_id=f"pol_{uuid.uuid4().hex[:8]}",
            name=name,
            framework=framework,
            control_id=control_id,
            resource_type=resource_type,
            severity=severity,
            check_function=check_function,
            **kwargs
        )
        self.policies[policy.policy_id] = policy
        return policy
        
    def evaluate(self, resource: Dict[str, Any],
                  policy_ids: List[str] = None) -> List[Finding]:
        """Оценка ресурса"""
        findings = []
        
        policies_to_check = (
            [self.policies[pid] for pid in policy_ids if pid in self.policies]
            if policy_ids
            else list(self.policies.values())
        )
        
        for policy in policies_to_check:
            if not policy.enabled:
                continue
                
            # Simulate check
            if policy.check_function:
                is_compliant = policy.check_function(resource)
            else:
                # Random for demo
                is_compliant = random.random() > 0.3
                
            if not is_compliant:
                finding = Finding(
                    finding_id=f"find_{uuid.uuid4().hex[:8]}",
                    policy_id=policy.policy_id,
                    policy_name=policy.name,
                    resource_id=resource.get("id", "unknown"),
                    resource_type=policy.resource_type,
                    title=f"Non-compliant: {policy.name}",
                    description=policy.description,
                    severity=policy.severity,
                    evidence={"resource": resource, "checked_at": datetime.now().isoformat()},
                    remediation_steps=policy.remediation_steps
                )
                findings.append(finding)
                
        return findings


class ControlManager:
    """Менеджер контролей"""
    
    def __init__(self):
        self.controls: Dict[str, Control] = {}
        
    def load_framework(self, framework: ComplianceFramework) -> List[Control]:
        """Загрузка фреймворка"""
        controls = []
        
        if framework == ComplianceFramework.SOC2:
            soc2_controls = [
                ("CC1", "Control Environment", "security"),
                ("CC2", "Communication and Information", "security"),
                ("CC3", "Risk Assessment", "security"),
                ("CC4", "Monitoring Activities", "security"),
                ("CC5", "Control Activities", "security"),
                ("CC6", "Logical and Physical Access", "access"),
                ("CC7", "System Operations", "operations"),
                ("CC8", "Change Management", "change"),
                ("CC9", "Risk Mitigation", "security")
            ]
            
            for ctrl_id, name, category in soc2_controls:
                control = Control(
                    control_id=ctrl_id,
                    name=name,
                    framework=framework,
                    category=category
                )
                self.controls[ctrl_id] = control
                controls.append(control)
                
        elif framework == ComplianceFramework.PCI_DSS:
            pci_controls = [
                ("1", "Install and maintain a firewall", "network"),
                ("2", "Do not use vendor-supplied defaults", "config"),
                ("3", "Protect stored cardholder data", "data"),
                ("4", "Encrypt transmission of data", "encryption"),
                ("5", "Protect all systems against malware", "security"),
                ("6", "Develop secure systems", "development"),
                ("7", "Restrict access by need to know", "access"),
                ("8", "Identify and authenticate access", "access"),
                ("9", "Restrict physical access", "physical"),
                ("10", "Track and monitor access", "logging"),
                ("11", "Test security systems", "testing"),
                ("12", "Maintain security policy", "policy")
            ]
            
            for ctrl_id, name, category in pci_controls:
                control = Control(
                    control_id=f"PCI-{ctrl_id}",
                    name=name,
                    framework=framework,
                    category=category
                )
                self.controls[control.control_id] = control
                controls.append(control)
                
        return controls
        
    def update_status(self, control_id: str, status: ControlStatus,
                       compliance_pct: float = 0.0) -> bool:
        """Обновление статуса"""
        control = self.controls.get(control_id)
        if control:
            control.status = status
            control.compliance_percentage = compliance_pct
            return True
        return False


class EvidenceCollector:
    """Сборщик доказательств"""
    
    def __init__(self):
        self.evidence: Dict[str, Evidence] = {}
        
    def collect(self, control_id: str, evidence_type: str,
                 title: str, data: Dict[str, Any],
                 collector: str = "automated") -> Evidence:
        """Сбор доказательства"""
        ev = Evidence(
            evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
            control_id=control_id,
            evidence_type=evidence_type,
            title=title,
            data=data,
            collected_by=collector,
            valid_until=datetime.now() + timedelta(days=90)
        )
        self.evidence[ev.evidence_id] = ev
        return ev
        
    def get_by_control(self, control_id: str) -> List[Evidence]:
        """Доказательства по контролю"""
        return [e for e in self.evidence.values() if e.control_id == control_id]


class AuditTrail:
    """Журнал аудита"""
    
    def __init__(self):
        self.entries: List[AuditEntry] = []
        
    def log(self, action: str, actor: str,
             resource_type: str, resource_id: str,
             details: Dict[str, Any] = None,
             success: bool = True) -> AuditEntry:
        """Запись в журнал"""
        entry = AuditEntry(
            entry_id=f"audit_{uuid.uuid4().hex[:8]}",
            action=action,
            actor=actor,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            success=success
        )
        self.entries.append(entry)
        return entry
        
    def query(self, action: str = None, actor: str = None,
               start_time: datetime = None,
               end_time: datetime = None) -> List[AuditEntry]:
        """Запрос журнала"""
        filtered = self.entries
        
        if action:
            filtered = [e for e in filtered if e.action == action]
        if actor:
            filtered = [e for e in filtered if e.actor == actor]
        if start_time:
            filtered = [e for e in filtered if e.timestamp >= start_time]
        if end_time:
            filtered = [e for e in filtered if e.timestamp <= end_time]
            
        return filtered


class RiskEngine:
    """Движок оценки рисков"""
    
    def assess(self, resource_id: str, resource_type: ResourceType,
                findings: List[Finding]) -> RiskAssessment:
        """Оценка риска"""
        # Count findings by severity
        critical = len([f for f in findings if f.severity == Severity.CRITICAL])
        high = len([f for f in findings if f.severity == Severity.HIGH])
        medium = len([f for f in findings if f.severity == Severity.MEDIUM])
        
        # Calculate likelihood
        likelihood = min(1.0, (critical * 0.4 + high * 0.2 + medium * 0.1))
        
        # Calculate impact based on resource type
        impact_map = {
            ResourceType.IAM: 0.9,
            ResourceType.SECRETS: 0.9,
            ResourceType.DATABASE: 0.8,
            ResourceType.ENCRYPTION: 0.7,
            ResourceType.NETWORK: 0.6,
            ResourceType.COMPUTE: 0.5,
            ResourceType.STORAGE: 0.5,
            ResourceType.LOGGING: 0.4
        }
        impact = impact_map.get(resource_type, 0.5)
        
        # Calculate risk score
        risk_score = likelihood * impact
        
        # Determine risk level
        if risk_score >= 0.7:
            risk_level = "critical"
        elif risk_score >= 0.5:
            risk_level = "high"
        elif risk_score >= 0.3:
            risk_level = "medium"
        else:
            risk_level = "low"
            
        return RiskAssessment(
            assessment_id=f"risk_{uuid.uuid4().hex[:8]}",
            resource_id=resource_id,
            resource_type=resource_type,
            likelihood=likelihood,
            impact=impact,
            risk_score=risk_score,
            risk_level=risk_level,
            findings_count=len(findings),
            critical_findings=critical
        )


class RemediationEngine:
    """Движок исправлений"""
    
    def __init__(self, audit_trail: AuditTrail):
        self.audit = audit_trail
        self.remediated: List[str] = []
        
    def remediate(self, finding: Finding, actor: str = "automation") -> bool:
        """Исправление"""
        # Log attempt
        self.audit.log(
            action="remediation_started",
            actor=actor,
            resource_type=finding.resource_type.value,
            resource_id=finding.resource_id,
            details={"finding_id": finding.finding_id, "policy": finding.policy_name}
        )
        
        # Simulate remediation
        success = random.random() > 0.1  # 90% success rate
        
        if success:
            finding.status = "remediated"
            finding.remediated_at = datetime.now()
            self.remediated.append(finding.finding_id)
            
        self.audit.log(
            action="remediation_completed",
            actor=actor,
            resource_type=finding.resource_type.value,
            resource_id=finding.resource_id,
            details={"finding_id": finding.finding_id, "success": success},
            success=success
        )
        
        return success


class ComplianceAutomationPlatform:
    """Платформа автоматизации комплаенса"""
    
    def __init__(self):
        self.policy_engine = PolicyEngine()
        self.control_manager = ControlManager()
        self.evidence_collector = EvidenceCollector()
        self.audit_trail = AuditTrail()
        self.risk_engine = RiskEngine()
        self.remediation_engine = RemediationEngine(self.audit_trail)
        
        self.findings: List[Finding] = []
        self.assessments: List[RiskAssessment] = []
        
    def load_framework(self, framework: ComplianceFramework) -> int:
        """Загрузка фреймворка"""
        controls = self.control_manager.load_framework(framework)
        return len(controls)
        
    def register_policy(self, **kwargs) -> Policy:
        """Регистрация политики"""
        return self.policy_engine.register_policy(**kwargs)
        
    def scan_resource(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Сканирование ресурса"""
        # Find violations
        findings = self.policy_engine.evaluate(resource)
        self.findings.extend(findings)
        
        # Assess risk
        resource_type = ResourceType(resource.get("type", "compute"))
        assessment = self.risk_engine.assess(
            resource.get("id", "unknown"),
            resource_type,
            findings
        )
        self.assessments.append(assessment)
        
        # Auto-remediate if enabled
        auto_remediated = 0
        for finding in findings:
            policy = self.policy_engine.policies.get(finding.policy_id)
            if policy and policy.auto_remediate:
                if self.remediation_engine.remediate(finding):
                    auto_remediated += 1
                    
        return {
            "resource_id": resource.get("id"),
            "findings_count": len(findings),
            "risk_level": assessment.risk_level,
            "risk_score": assessment.risk_score,
            "auto_remediated": auto_remediated
        }
        
    def get_compliance_summary(self) -> Dict[str, Any]:
        """Сводка по комплаенсу"""
        total_controls = len(self.control_manager.controls)
        compliant = len([c for c in self.control_manager.controls.values() 
                         if c.status == ControlStatus.COMPLIANT])
        
        open_findings = len([f for f in self.findings if f.status == "open"])
        critical_findings = len([f for f in self.findings 
                                  if f.status == "open" and f.severity == Severity.CRITICAL])
        
        return {
            "total_controls": total_controls,
            "compliant_controls": compliant,
            "compliance_percentage": (compliant / total_controls * 100) if total_controls else 0,
            "total_findings": len(self.findings),
            "open_findings": open_findings,
            "critical_findings": critical_findings,
            "remediated_findings": len(self.remediation_engine.remediated),
            "evidence_collected": len(self.evidence_collector.evidence),
            "audit_entries": len(self.audit_trail.entries)
        }
        
    def generate_report(self, framework: ComplianceFramework = None) -> Dict[str, Any]:
        """Генерация отчёта"""
        controls = list(self.control_manager.controls.values())
        if framework:
            controls = [c for c in controls if c.framework == framework]
            
        findings = self.findings
        if framework:
            framework_policies = [
                p.policy_id for p in self.policy_engine.policies.values()
                if p.framework == framework
            ]
            findings = [f for f in findings if f.policy_id in framework_policies]
            
        return {
            "generated_at": datetime.now().isoformat(),
            "framework": framework.value if framework else "all",
            "controls": len(controls),
            "findings": len(findings),
            "by_severity": {
                "critical": len([f for f in findings if f.severity == Severity.CRITICAL]),
                "high": len([f for f in findings if f.severity == Severity.HIGH]),
                "medium": len([f for f in findings if f.severity == Severity.MEDIUM]),
                "low": len([f for f in findings if f.severity == Severity.LOW])
            },
            "by_status": {
                "open": len([f for f in findings if f.status == "open"]),
                "remediated": len([f for f in findings if f.status == "remediated"]),
                "suppressed": len([f for f in findings if f.status == "suppressed"])
            }
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 105: Compliance Automation Platform")
    print("=" * 60)
    
    async def demo():
        platform = ComplianceAutomationPlatform()
        print("✓ Compliance Automation Platform created")
        
        # Load frameworks
        print("\n📚 Loading Compliance Frameworks...")
        
        soc2_count = platform.load_framework(ComplianceFramework.SOC2)
        print(f"  ✓ SOC2: {soc2_count} controls loaded")
        
        pci_count = platform.load_framework(ComplianceFramework.PCI_DSS)
        print(f"  ✓ PCI-DSS: {pci_count} controls loaded")
        
        # Register policies
        print("\n📋 Registering Policies...")
        
        policies_data = [
            ("Encryption at Rest", ComplianceFramework.SOC2, "CC6.1", ResourceType.STORAGE, Severity.HIGH,
             "All storage must be encrypted", ["Enable encryption", "Use KMS key"]),
            ("MFA Required", ComplianceFramework.SOC2, "CC6.1", ResourceType.IAM, Severity.CRITICAL,
             "MFA must be enabled for all users", ["Enable MFA", "Enforce MFA policy"]),
            ("Logging Enabled", ComplianceFramework.SOC2, "CC7.2", ResourceType.LOGGING, Severity.HIGH,
             "Audit logging must be enabled", ["Enable CloudTrail", "Configure retention"]),
            ("Network Segmentation", ComplianceFramework.PCI_DSS, "PCI-1", ResourceType.NETWORK, Severity.HIGH,
             "Cardholder data must be segmented", ["Create security groups", "Configure NACLs"]),
            ("No Default Passwords", ComplianceFramework.PCI_DSS, "PCI-2", ResourceType.COMPUTE, Severity.CRITICAL,
             "Default passwords must be changed", ["Change default credentials"]),
            ("Data Encryption", ComplianceFramework.PCI_DSS, "PCI-3", ResourceType.DATABASE, Severity.CRITICAL,
             "Cardholder data must be encrypted", ["Enable TDE", "Use strong encryption"]),
            ("TLS Required", ComplianceFramework.PCI_DSS, "PCI-4", ResourceType.NETWORK, Severity.HIGH,
             "All transmissions must use TLS", ["Enable TLS 1.2+", "Disable weak ciphers"]),
            ("Access Logging", ComplianceFramework.PCI_DSS, "PCI-10", ResourceType.LOGGING, Severity.HIGH,
             "All access must be logged", ["Enable access logs", "Configure SIEM"])
        ]
        
        for name, framework, control, resource_type, severity, desc, remediation in policies_data:
            policy = platform.register_policy(
                name=name,
                framework=framework,
                control_id=control,
                resource_type=resource_type,
                severity=severity,
                description=desc,
                remediation_steps=remediation,
                auto_remediate=(severity != Severity.CRITICAL)
            )
            print(f"  ✓ [{framework.value}] {name}")
            
        # Scan resources
        print("\n🔍 Scanning Resources...")
        
        resources = [
            {"id": "s3-data-bucket", "type": "storage", "name": "Data Bucket", "encrypted": True},
            {"id": "s3-logs-bucket", "type": "storage", "name": "Logs Bucket", "encrypted": False},
            {"id": "rds-primary", "type": "database", "name": "Primary DB", "encrypted": True},
            {"id": "ec2-web-1", "type": "compute", "name": "Web Server 1"},
            {"id": "ec2-web-2", "type": "compute", "name": "Web Server 2"},
            {"id": "vpc-main", "type": "network", "name": "Main VPC"},
            {"id": "iam-admin", "type": "iam", "name": "Admin Role"},
            {"id": "iam-developer", "type": "iam", "name": "Developer Role"},
            {"id": "cloudtrail-main", "type": "logging", "name": "Main Trail"},
            {"id": "secrets-db", "type": "secrets", "name": "DB Credentials"}
        ]
        
        for resource in resources:
            result = platform.scan_resource(resource)
            risk_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(result["risk_level"], "⚪")
            print(f"  {risk_icon} {resource['name']}: {result['findings_count']} findings, risk={result['risk_level']}")
            if result["auto_remediated"] > 0:
                print(f"     → Auto-remediated {result['auto_remediated']} issues")
                
        # Collect evidence
        print("\n📎 Collecting Evidence...")
        
        evidence_items = [
            ("CC6.1", "config", "Encryption Configuration", {"service": "S3", "encryption": "AES-256"}),
            ("CC6.1", "screenshot", "MFA Settings", {"users_with_mfa": 45, "total_users": 50}),
            ("CC7.2", "log", "Audit Log Sample", {"entries": 1000, "retention_days": 365}),
            ("PCI-1", "config", "Firewall Rules", {"rules_count": 25, "default_deny": True}),
            ("PCI-10", "report", "Access Report", {"logins": 500, "failures": 12})
        ]
        
        for control_id, ev_type, title, data in evidence_items:
            ev = platform.evidence_collector.collect(control_id, ev_type, title, data)
            print(f"  ✓ [{control_id}] {title}")
            
        # Update control status
        print("\n📊 Updating Control Status...")
        
        for control in list(platform.control_manager.controls.values())[:5]:
            compliance_pct = random.uniform(60, 100)
            status = (
                ControlStatus.COMPLIANT if compliance_pct >= 90
                else ControlStatus.PARTIALLY_COMPLIANT if compliance_pct >= 70
                else ControlStatus.NON_COMPLIANT
            )
            platform.control_manager.update_status(control.control_id, status, compliance_pct)
            
            status_icon = {"compliant": "✅", "partially_compliant": "⚠️", "non_compliant": "❌"}.get(status.value, "⚪")
            print(f"  {status_icon} {control.control_id}: {control.name} ({compliance_pct:.0f}%)")
            
        # Risk summary
        print("\n⚠️ Risk Assessment Summary:")
        
        risk_levels = defaultdict(int)
        for assessment in platform.assessments:
            risk_levels[assessment.risk_level] += 1
            
        for level in ["critical", "high", "medium", "low"]:
            count = risk_levels[level]
            bar = "█" * count
            print(f"  {level.capitalize():<10}: {count:>3} {bar}")
            
        # Findings by severity
        print("\n🔍 Findings by Severity:")
        
        severity_counts = defaultdict(int)
        for finding in platform.findings:
            severity_counts[finding.severity.value] += 1
            
        for sev in ["critical", "high", "medium", "low", "info"]:
            count = severity_counts[sev]
            icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢", "info": "🔵"}.get(sev, "⚪")
            print(f"  {icon} {sev.capitalize():<10}: {count}")
            
        # Compliance summary
        print("\n📈 Compliance Summary:")
        
        summary = platform.get_compliance_summary()
        
        print(f"\n  Controls: {summary['compliant_controls']}/{summary['total_controls']} compliant ({summary['compliance_percentage']:.1f}%)")
        print(f"  Total Findings: {summary['total_findings']}")
        print(f"  Open Findings: {summary['open_findings']}")
        print(f"  Critical Findings: {summary['critical_findings']}")
        print(f"  Auto-Remediated: {summary['remediated_findings']}")
        print(f"  Evidence Collected: {summary['evidence_collected']}")
        print(f"  Audit Entries: {summary['audit_entries']}")
        
        # Generate reports
        print("\n📝 Generating Reports...")
        
        soc2_report = platform.generate_report(ComplianceFramework.SOC2)
        print(f"\n  SOC2 Report:")
        print(f"    Findings: {soc2_report['findings']}")
        print(f"    By Severity: Critical={soc2_report['by_severity']['critical']}, High={soc2_report['by_severity']['high']}")
        
        pci_report = platform.generate_report(ComplianceFramework.PCI_DSS)
        print(f"\n  PCI-DSS Report:")
        print(f"    Findings: {pci_report['findings']}")
        print(f"    By Status: Open={pci_report['by_status']['open']}, Remediated={pci_report['by_status']['remediated']}")
        
        # Audit trail sample
        print("\n📜 Recent Audit Trail:")
        
        for entry in platform.audit_trail.entries[-5:]:
            status_icon = "✓" if entry.success else "✗"
            print(f"  [{status_icon}] {entry.action} by {entry.actor}")
            print(f"      Resource: {entry.resource_type}/{entry.resource_id}")
            
        # Dashboard
        print("\n📋 Compliance Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │              Compliance Automation Overview                 │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Controls:     {summary['total_controls']:>10}                        │")
        print(f"  │ Compliant:          {summary['compliant_controls']:>10}                        │")
        print(f"  │ Compliance %:       {summary['compliance_percentage']:>10.1f}%                       │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Open Findings:      {summary['open_findings']:>10}                        │")
        print(f"  │ Critical:           {summary['critical_findings']:>10}                        │")
        print(f"  │ Remediated:         {summary['remediated_findings']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Evidence Items:     {summary['evidence_collected']:>10}                        │")
        print(f"  │ Audit Entries:      {summary['audit_entries']:>10}                        │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Compliance Automation Platform initialized!")
    print("=" * 60)
