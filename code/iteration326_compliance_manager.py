#!/usr/bin/env python3
"""
Server Init - Iteration 326: Compliance Manager Platform
Платформа управления соответствием

Функционал:
- Policy Management - управление политиками
- Compliance Frameworks - фреймворки соответствия (SOC2, HIPAA, GDPR, PCI-DSS)
- Control Assessment - оценка контролей
- Evidence Collection - сбор доказательств
- Risk Assessment - оценка рисков
- Audit Management - управление аудитами
- Remediation Tracking - отслеживание исправлений
- Reporting & Dashboards - отчетность
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class Framework(Enum):
    """Фреймворк соответствия"""
    SOC2 = "SOC2"
    HIPAA = "HIPAA"
    GDPR = "GDPR"
    PCI_DSS = "PCI-DSS"
    ISO_27001 = "ISO-27001"
    NIST = "NIST"
    CIS = "CIS"
    FEDRAMP = "FedRAMP"


class ControlStatus(Enum):
    """Статус контроля"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_ASSESSED = "not_assessed"
    NOT_APPLICABLE = "not_applicable"


class RiskLevel(Enum):
    """Уровень риска"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class EvidenceType(Enum):
    """Тип доказательства"""
    SCREENSHOT = "screenshot"
    DOCUMENT = "document"
    LOG = "log"
    CONFIGURATION = "configuration"
    POLICY = "policy"
    ATTESTATION = "attestation"
    SCAN_RESULT = "scan_result"


class AssessmentStatus(Enum):
    """Статус оценки"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    COMPLETED = "completed"
    FAILED = "failed"


class RemediationStatus(Enum):
    """Статус исправления"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING_VERIFICATION = "pending_verification"
    VERIFIED = "verified"
    CLOSED = "closed"
    ACCEPTED_RISK = "accepted_risk"


@dataclass
class ComplianceFramework:
    """Фреймворк соответствия"""
    framework_id: str
    name: str
    
    # Type
    framework: Framework = Framework.SOC2
    version: str = ""
    
    # Description
    description: str = ""
    
    # Controls
    control_ids: List[str] = field(default_factory=list)
    
    # Stats
    total_controls: int = 0
    compliant_controls: int = 0
    
    # Status
    is_active: bool = True
    
    # Timestamps
    effective_date: datetime = field(default_factory=datetime.now)


@dataclass
class Control:
    """Контроль соответствия"""
    control_id: str
    framework_id: str
    
    # Identifier
    control_number: str = ""  # e.g., "CC1.1", "A.5.1.1"
    
    # Name
    name: str = ""
    description: str = ""
    
    # Category
    category: str = ""  # e.g., "Access Control", "Data Protection"
    
    # Status
    status: ControlStatus = ControlStatus.NOT_ASSESSED
    
    # Risk
    risk_level: RiskLevel = RiskLevel.MEDIUM
    
    # Owner
    owner: str = ""
    
    # Evidence
    evidence_ids: List[str] = field(default_factory=list)
    
    # Automation
    is_automated: bool = False
    automation_script: str = ""
    
    # Last assessment
    last_assessed: Optional[datetime] = None
    next_assessment: Optional[datetime] = None


@dataclass
class Evidence:
    """Доказательство"""
    evidence_id: str
    control_id: str
    
    # Type
    evidence_type: EvidenceType = EvidenceType.DOCUMENT
    
    # Name
    name: str = ""
    description: str = ""
    
    # File
    file_path: str = ""
    file_hash: str = ""
    
    # Source
    source_system: str = ""
    
    # Validity
    valid_from: datetime = field(default_factory=datetime.now)
    valid_until: Optional[datetime] = None
    
    # Collection
    collected_at: datetime = field(default_factory=datetime.now)
    collected_by: str = ""
    
    # Status
    is_valid: bool = True


@dataclass
class Assessment:
    """Оценка соответствия"""
    assessment_id: str
    
    # Framework
    framework_id: str = ""
    
    # Scope
    scope: str = ""
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=365))
    
    # Status
    status: AssessmentStatus = AssessmentStatus.NOT_STARTED
    
    # Results
    control_results: Dict[str, ControlStatus] = field(default_factory=dict)
    
    # Assessor
    assessor: str = ""
    
    # Summary
    total_controls: int = 0
    compliant: int = 0
    non_compliant: int = 0
    partially_compliant: int = 0
    
    # Timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class Risk:
    """Риск"""
    risk_id: str
    
    # Title
    title: str = ""
    description: str = ""
    
    # Control
    control_id: str = ""
    
    # Level
    risk_level: RiskLevel = RiskLevel.MEDIUM
    
    # Impact & Likelihood
    impact: int = 3  # 1-5
    likelihood: int = 3  # 1-5
    
    # Owner
    owner: str = ""
    
    # Status
    status: str = "open"  # open, mitigated, accepted, closed
    
    # Mitigation
    mitigation_plan: str = ""
    
    # Timestamps
    identified_at: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None


@dataclass
class Remediation:
    """Исправление"""
    remediation_id: str
    
    # Finding
    finding_id: str = ""
    control_id: str = ""
    
    # Title
    title: str = ""
    description: str = ""
    
    # Priority
    priority: RiskLevel = RiskLevel.MEDIUM
    
    # Status
    status: RemediationStatus = RemediationStatus.OPEN
    
    # Owner
    owner: str = ""
    
    # Plan
    remediation_plan: str = ""
    
    # Timeline
    due_date: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=30))
    
    # Progress
    progress_percent: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class Finding:
    """Находка аудита"""
    finding_id: str
    assessment_id: str
    
    # Control
    control_id: str = ""
    
    # Title
    title: str = ""
    description: str = ""
    
    # Severity
    severity: RiskLevel = RiskLevel.MEDIUM
    
    # Status
    status: str = "open"  # open, remediated, accepted, closed
    
    # Recommendation
    recommendation: str = ""
    
    # Remediation
    remediation_id: str = ""
    
    # Timestamps
    found_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


@dataclass
class Policy:
    """Политика"""
    policy_id: str
    
    # Name
    name: str = ""
    description: str = ""
    
    # Category
    category: str = ""
    
    # Content
    content: str = ""
    
    # Version
    version: str = "1.0"
    
    # Approval
    approved_by: str = ""
    approved_at: Optional[datetime] = None
    
    # Status
    status: str = "draft"  # draft, approved, published, retired
    
    # Review
    review_frequency_days: int = 365
    next_review: Optional[datetime] = None
    
    # Controls
    related_control_ids: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    effective_date: Optional[datetime] = None


@dataclass
class Audit:
    """Аудит"""
    audit_id: str
    
    # Name
    name: str = ""
    
    # Type
    audit_type: str = "internal"  # internal, external, regulatory
    
    # Framework
    framework_ids: List[str] = field(default_factory=list)
    
    # Period
    audit_period_start: datetime = field(default_factory=datetime.now)
    audit_period_end: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=365))
    
    # Auditor
    auditor: str = ""
    auditor_org: str = ""
    
    # Findings
    finding_ids: List[str] = field(default_factory=list)
    
    # Status
    status: str = "planning"  # planning, fieldwork, reporting, completed
    
    # Opinion
    opinion: str = ""  # unqualified, qualified, adverse, disclaimer
    
    # Timestamps
    scheduled_start: datetime = field(default_factory=datetime.now)
    scheduled_end: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=30))
    completed_at: Optional[datetime] = None


class ComplianceManager:
    """Менеджер соответствия"""
    
    def __init__(self):
        self.frameworks: Dict[str, ComplianceFramework] = {}
        self.controls: Dict[str, Control] = {}
        self.evidence: Dict[str, Evidence] = {}
        self.assessments: Dict[str, Assessment] = {}
        self.risks: Dict[str, Risk] = {}
        self.remediations: Dict[str, Remediation] = {}
        self.findings: Dict[str, Finding] = {}
        self.policies: Dict[str, Policy] = {}
        self.audits: Dict[str, Audit] = {}
        
    async def add_framework(self, name: str,
                           framework: Framework,
                           version: str = "",
                           description: str = "") -> ComplianceFramework:
        """Добавление фреймворка"""
        fw = ComplianceFramework(
            framework_id=f"fw_{uuid.uuid4().hex[:8]}",
            name=name,
            framework=framework,
            version=version,
            description=description
        )
        
        self.frameworks[fw.framework_id] = fw
        return fw
        
    async def add_control(self, framework_id: str,
                         control_number: str,
                         name: str,
                         description: str = "",
                         category: str = "",
                         risk_level: RiskLevel = RiskLevel.MEDIUM,
                         owner: str = "") -> Optional[Control]:
        """Добавление контроля"""
        fw = self.frameworks.get(framework_id)
        if not fw:
            return None
            
        control = Control(
            control_id=f"ctrl_{uuid.uuid4().hex[:8]}",
            framework_id=framework_id,
            control_number=control_number,
            name=name,
            description=description,
            category=category,
            risk_level=risk_level,
            owner=owner
        )
        
        self.controls[control.control_id] = control
        fw.control_ids.append(control.control_id)
        fw.total_controls += 1
        
        return control
        
    async def add_evidence(self, control_id: str,
                          evidence_type: EvidenceType,
                          name: str,
                          description: str = "",
                          file_path: str = "",
                          source_system: str = "",
                          collected_by: str = "") -> Optional[Evidence]:
        """Добавление доказательства"""
        control = self.controls.get(control_id)
        if not control:
            return None
            
        evidence = Evidence(
            evidence_id=f"evd_{uuid.uuid4().hex[:8]}",
            control_id=control_id,
            evidence_type=evidence_type,
            name=name,
            description=description,
            file_path=file_path,
            source_system=source_system,
            collected_by=collected_by,
            file_hash=uuid.uuid4().hex,
            valid_until=datetime.now() + timedelta(days=365)
        )
        
        self.evidence[evidence.evidence_id] = evidence
        control.evidence_ids.append(evidence.evidence_id)
        
        return evidence
        
    async def assess_control(self, control_id: str,
                            status: ControlStatus,
                            assessor: str = "") -> bool:
        """Оценка контроля"""
        control = self.controls.get(control_id)
        if not control:
            return False
            
        old_status = control.status
        control.status = status
        control.last_assessed = datetime.now()
        control.next_assessment = datetime.now() + timedelta(days=90)
        
        # Update framework stats
        fw = self.frameworks.get(control.framework_id)
        if fw:
            if old_status == ControlStatus.COMPLIANT and status != ControlStatus.COMPLIANT:
                fw.compliant_controls -= 1
            elif old_status != ControlStatus.COMPLIANT and status == ControlStatus.COMPLIANT:
                fw.compliant_controls += 1
                
        return True
        
    async def create_assessment(self, framework_id: str,
                               scope: str,
                               assessor: str = "",
                               period_days: int = 365) -> Optional[Assessment]:
        """Создание оценки"""
        fw = self.frameworks.get(framework_id)
        if not fw:
            return None
            
        assessment = Assessment(
            assessment_id=f"asmt_{uuid.uuid4().hex[:8]}",
            framework_id=framework_id,
            scope=scope,
            assessor=assessor,
            period_end=datetime.now() + timedelta(days=period_days),
            total_controls=fw.total_controls
        )
        
        self.assessments[assessment.assessment_id] = assessment
        return assessment
        
    async def run_assessment(self, assessment_id: str) -> Optional[Assessment]:
        """Запуск оценки"""
        assessment = self.assessments.get(assessment_id)
        if not assessment:
            return None
            
        assessment.status = AssessmentStatus.IN_PROGRESS
        assessment.started_at = datetime.now()
        
        fw = self.frameworks.get(assessment.framework_id)
        if not fw:
            return None
            
        # Assess all controls
        for ctrl_id in fw.control_ids:
            ctrl = self.controls.get(ctrl_id)
            if ctrl:
                # Simulate assessment (in production, this would run actual checks)
                status = random.choice([
                    ControlStatus.COMPLIANT,
                    ControlStatus.COMPLIANT,
                    ControlStatus.COMPLIANT,
                    ControlStatus.PARTIALLY_COMPLIANT,
                    ControlStatus.NON_COMPLIANT
                ])
                
                await self.assess_control(ctrl_id, status, assessment.assessor)
                assessment.control_results[ctrl_id] = status
                
                if status == ControlStatus.COMPLIANT:
                    assessment.compliant += 1
                elif status == ControlStatus.NON_COMPLIANT:
                    assessment.non_compliant += 1
                elif status == ControlStatus.PARTIALLY_COMPLIANT:
                    assessment.partially_compliant += 1
                    
        assessment.status = AssessmentStatus.COMPLETED
        assessment.completed_at = datetime.now()
        
        return assessment
        
    async def identify_risk(self, title: str,
                           description: str,
                           control_id: str = "",
                           risk_level: RiskLevel = RiskLevel.MEDIUM,
                           impact: int = 3,
                           likelihood: int = 3,
                           owner: str = "") -> Risk:
        """Идентификация риска"""
        risk = Risk(
            risk_id=f"risk_{uuid.uuid4().hex[:8]}",
            title=title,
            description=description,
            control_id=control_id,
            risk_level=risk_level,
            impact=impact,
            likelihood=likelihood,
            owner=owner,
            due_date=datetime.now() + timedelta(days=30)
        )
        
        self.risks[risk.risk_id] = risk
        return risk
        
    async def create_finding(self, assessment_id: str,
                            control_id: str,
                            title: str,
                            description: str,
                            severity: RiskLevel = RiskLevel.MEDIUM,
                            recommendation: str = "") -> Optional[Finding]:
        """Создание находки"""
        assessment = self.assessments.get(assessment_id)
        if not assessment:
            return None
            
        finding = Finding(
            finding_id=f"fnd_{uuid.uuid4().hex[:8]}",
            assessment_id=assessment_id,
            control_id=control_id,
            title=title,
            description=description,
            severity=severity,
            recommendation=recommendation
        )
        
        self.findings[finding.finding_id] = finding
        return finding
        
    async def create_remediation(self, finding_id: str,
                                title: str,
                                description: str,
                                priority: RiskLevel = RiskLevel.MEDIUM,
                                owner: str = "",
                                plan: str = "",
                                due_days: int = 30) -> Optional[Remediation]:
        """Создание плана исправления"""
        finding = self.findings.get(finding_id)
        if not finding:
            return None
            
        remediation = Remediation(
            remediation_id=f"rem_{uuid.uuid4().hex[:8]}",
            finding_id=finding_id,
            control_id=finding.control_id,
            title=title,
            description=description,
            priority=priority,
            owner=owner,
            remediation_plan=plan,
            due_date=datetime.now() + timedelta(days=due_days)
        )
        
        finding.remediation_id = remediation.remediation_id
        
        self.remediations[remediation.remediation_id] = remediation
        return remediation
        
    async def update_remediation(self, remediation_id: str,
                                status: RemediationStatus,
                                progress: int = 0) -> bool:
        """Обновление исправления"""
        rem = self.remediations.get(remediation_id)
        if not rem:
            return False
            
        rem.status = status
        rem.progress_percent = progress
        
        if status == RemediationStatus.CLOSED or status == RemediationStatus.VERIFIED:
            rem.completed_at = datetime.now()
            
            # Update finding
            finding = self.findings.get(rem.finding_id)
            if finding:
                finding.status = "remediated"
                finding.resolved_at = datetime.now()
                
        return True
        
    async def create_policy(self, name: str,
                           description: str,
                           category: str,
                           content: str,
                           related_controls: List[str] = None) -> Policy:
        """Создание политики"""
        policy = Policy(
            policy_id=f"pol_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            category=category,
            content=content,
            related_control_ids=related_controls or [],
            next_review=datetime.now() + timedelta(days=365)
        )
        
        self.policies[policy.policy_id] = policy
        return policy
        
    async def approve_policy(self, policy_id: str,
                            approved_by: str) -> bool:
        """Утверждение политики"""
        policy = self.policies.get(policy_id)
        if not policy:
            return False
            
        policy.status = "approved"
        policy.approved_by = approved_by
        policy.approved_at = datetime.now()
        
        return True
        
    async def publish_policy(self, policy_id: str) -> bool:
        """Публикация политики"""
        policy = self.policies.get(policy_id)
        if not policy or policy.status != "approved":
            return False
            
        policy.status = "published"
        policy.effective_date = datetime.now()
        
        return True
        
    async def create_audit(self, name: str,
                          audit_type: str,
                          framework_ids: List[str],
                          auditor: str,
                          auditor_org: str = "",
                          days: int = 30) -> Audit:
        """Создание аудита"""
        audit = Audit(
            audit_id=f"aud_{uuid.uuid4().hex[:8]}",
            name=name,
            audit_type=audit_type,
            framework_ids=framework_ids,
            auditor=auditor,
            auditor_org=auditor_org,
            scheduled_end=datetime.now() + timedelta(days=days)
        )
        
        self.audits[audit.audit_id] = audit
        return audit
        
    async def complete_audit(self, audit_id: str,
                            opinion: str) -> bool:
        """Завершение аудита"""
        audit = self.audits.get(audit_id)
        if not audit:
            return False
            
        audit.status = "completed"
        audit.opinion = opinion
        audit.completed_at = datetime.now()
        
        return True
        
    def get_compliance_score(self, framework_id: str) -> float:
        """Расчет показателя соответствия"""
        fw = self.frameworks.get(framework_id)
        if not fw or fw.total_controls == 0:
            return 0.0
            
        compliant = 0
        partial = 0
        total = 0
        
        for ctrl_id in fw.control_ids:
            ctrl = self.controls.get(ctrl_id)
            if ctrl and ctrl.status != ControlStatus.NOT_APPLICABLE:
                total += 1
                if ctrl.status == ControlStatus.COMPLIANT:
                    compliant += 1
                elif ctrl.status == ControlStatus.PARTIALLY_COMPLIANT:
                    partial += 1
                    
        if total == 0:
            return 0.0
            
        return ((compliant + partial * 0.5) / total) * 100
        
    def get_risk_score(self) -> Dict[str, Any]:
        """Расчет показателя риска"""
        total_score = 0
        by_level = {level.value: 0 for level in RiskLevel}
        open_risks = 0
        
        for risk in self.risks.values():
            if risk.status == "open":
                open_risks += 1
                score = risk.impact * risk.likelihood
                total_score += score
                by_level[risk.risk_level.value] += 1
                
        return {
            "total_score": total_score,
            "open_risks": open_risks,
            "by_level": by_level,
            "avg_score": total_score / open_risks if open_risks > 0 else 0
        }
        
    def get_remediation_status(self) -> Dict[str, Any]:
        """Статус исправлений"""
        by_status = {status.value: 0 for status in RemediationStatus}
        overdue = 0
        
        for rem in self.remediations.values():
            by_status[rem.status.value] += 1
            if rem.status in [RemediationStatus.OPEN, RemediationStatus.IN_PROGRESS]:
                if rem.due_date < datetime.now():
                    overdue += 1
                    
        total = len(self.remediations)
        closed = by_status.get("closed", 0) + by_status.get("verified", 0)
        
        return {
            "total": total,
            "by_status": by_status,
            "overdue": overdue,
            "completion_rate": (closed / total * 100) if total > 0 else 0
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_frameworks = len(self.frameworks)
        total_controls = len(self.controls)
        
        by_status = {status.value: 0 for status in ControlStatus}
        for ctrl in self.controls.values():
            by_status[ctrl.status.value] += 1
            
        total_evidence = len(self.evidence)
        valid_evidence = sum(1 for e in self.evidence.values() if e.is_valid)
        
        total_risks = len(self.risks)
        open_risks = sum(1 for r in self.risks.values() if r.status == "open")
        
        total_findings = len(self.findings)
        open_findings = sum(1 for f in self.findings.values() if f.status == "open")
        
        total_policies = len(self.policies)
        published_policies = sum(1 for p in self.policies.values() if p.status == "published")
        
        total_audits = len(self.audits)
        completed_audits = sum(1 for a in self.audits.values() if a.status == "completed")
        
        return {
            "total_frameworks": total_frameworks,
            "total_controls": total_controls,
            "controls_by_status": by_status,
            "total_evidence": total_evidence,
            "valid_evidence": valid_evidence,
            "total_risks": total_risks,
            "open_risks": open_risks,
            "total_findings": total_findings,
            "open_findings": open_findings,
            "total_remediations": len(self.remediations),
            "total_policies": total_policies,
            "published_policies": published_policies,
            "total_audits": total_audits,
            "completed_audits": completed_audits
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 326: Compliance Manager Platform")
    print("=" * 60)
    
    compliance = ComplianceManager()
    print("✓ Compliance Manager created")
    
    # Add frameworks
    print("\n📋 Adding Compliance Frameworks...")
    
    frameworks_data = [
        ("SOC 2 Type II", Framework.SOC2, "2017", "Service Organization Control 2"),
        ("HIPAA Security Rule", Framework.HIPAA, "2013", "Health Insurance Portability Act"),
        ("GDPR", Framework.GDPR, "2018", "General Data Protection Regulation"),
        ("PCI DSS", Framework.PCI_DSS, "4.0", "Payment Card Industry Data Security Standard"),
        ("ISO 27001", Framework.ISO_27001, "2022", "Information Security Management")
    ]
    
    frameworks = []
    for name, fw_type, version, desc in frameworks_data:
        fw = await compliance.add_framework(name, fw_type, version, desc)
        frameworks.append(fw)
        print(f"  📋 {name} ({fw_type.value})")
        
    # Add controls for SOC2
    print("\n🔒 Adding Controls...")
    
    soc2_controls = [
        ("CC1.1", "Control Environment", "Access Control", RiskLevel.HIGH),
        ("CC1.2", "Board Oversight", "Governance", RiskLevel.MEDIUM),
        ("CC2.1", "Information and Communication", "Communication", RiskLevel.MEDIUM),
        ("CC3.1", "Risk Assessment", "Risk Management", RiskLevel.HIGH),
        ("CC4.1", "Monitoring Activities", "Monitoring", RiskLevel.MEDIUM),
        ("CC5.1", "Logical Access Controls", "Access Control", RiskLevel.CRITICAL),
        ("CC5.2", "Physical Access Controls", "Access Control", RiskLevel.HIGH),
        ("CC6.1", "Encryption", "Data Protection", RiskLevel.CRITICAL),
        ("CC6.2", "Change Management", "Change Control", RiskLevel.HIGH),
        ("CC7.1", "System Operations", "Operations", RiskLevel.MEDIUM),
        ("CC7.2", "Security Monitoring", "Monitoring", RiskLevel.HIGH),
        ("CC8.1", "Incident Response", "Incident Management", RiskLevel.CRITICAL)
    ]
    
    controls = []
    for ctrl_num, name, category, risk in soc2_controls:
        ctrl = await compliance.add_control(
            frameworks[0].framework_id,
            ctrl_num,
            name,
            f"Control for {name}",
            category,
            risk,
            "security-team@company.com"
        )
        if ctrl:
            controls.append(ctrl)
            
    print(f"  ✓ Added {len(controls)} controls for SOC 2")
    
    # Add controls for other frameworks
    for fw in frameworks[1:]:
        for i in range(8):
            await compliance.add_control(
                fw.framework_id,
                f"{fw.framework.value[:3]}.{i+1}",
                f"Control {i+1}",
                f"Control for {fw.name}",
                random.choice(["Access Control", "Data Protection", "Monitoring", "Governance"]),
                random.choice(list(RiskLevel)),
                "security-team@company.com"
            )
            
    print(f"  ✓ Added controls for other frameworks")
    
    # Add evidence
    print("\n📎 Collecting Evidence...")
    
    evidence_data = [
        (EvidenceType.SCREENSHOT, "MFA Configuration Screenshot", "Authentication system"),
        (EvidenceType.DOCUMENT, "Access Control Policy", "Policy repository"),
        (EvidenceType.LOG, "Access Logs Export", "SIEM"),
        (EvidenceType.CONFIGURATION, "Firewall Rules Export", "Firewall"),
        (EvidenceType.SCAN_RESULT, "Vulnerability Scan Report", "Security scanner"),
        (EvidenceType.ATTESTATION, "Management Attestation", "GRC system")
    ]
    
    for i, ctrl in enumerate(controls[:6]):
        evd_type, name, source = evidence_data[i]
        await compliance.add_evidence(
            ctrl.control_id,
            evd_type,
            name,
            f"Evidence for {ctrl.name}",
            f"/evidence/{name.lower().replace(' ', '_')}.pdf",
            source,
            "compliance-team@company.com"
        )
        
    print(f"  ✓ Collected {len(evidence_data)} pieces of evidence")
    
    # Create and run assessment
    print("\n📊 Running Compliance Assessment...")
    
    assessment = await compliance.create_assessment(
        frameworks[0].framework_id,
        "Production Environment",
        "external-auditor@audit-firm.com",
        365
    )
    
    await compliance.run_assessment(assessment.assessment_id)
    print(f"  ✓ Assessment completed")
    print(f"    Compliant: {assessment.compliant}")
    print(f"    Non-compliant: {assessment.non_compliant}")
    print(f"    Partially compliant: {assessment.partially_compliant}")
    
    # Create findings for non-compliant controls
    print("\n⚠️ Creating Findings...")
    
    findings = []
    for ctrl_id, status in assessment.control_results.items():
        if status == ControlStatus.NON_COMPLIANT:
            ctrl = compliance.controls.get(ctrl_id)
            if ctrl:
                finding = await compliance.create_finding(
                    assessment.assessment_id,
                    ctrl_id,
                    f"Non-compliance in {ctrl.name}",
                    f"Control {ctrl.control_number} was found to be non-compliant",
                    ctrl.risk_level,
                    f"Implement proper controls for {ctrl.name}"
                )
                if finding:
                    findings.append(finding)
                    
    print(f"  ✓ Created {len(findings)} findings")
    
    # Create remediations
    print("\n🔧 Creating Remediation Plans...")
    
    remediations = []
    for finding in findings:
        ctrl = compliance.controls.get(finding.control_id)
        rem = await compliance.create_remediation(
            finding.finding_id,
            f"Remediate {ctrl.name if ctrl else 'control'}",
            f"Implementation plan for {finding.title}",
            finding.severity,
            "remediation-owner@company.com",
            "1. Assess current state\n2. Implement controls\n3. Verify effectiveness",
            30
        )
        if rem:
            remediations.append(rem)
            
    print(f"  ✓ Created {len(remediations)} remediation plans")
    
    # Update some remediations
    for rem in remediations[:len(remediations)//2]:
        await compliance.update_remediation(
            rem.remediation_id,
            RemediationStatus.IN_PROGRESS,
            random.randint(25, 75)
        )
        
    # Identify risks
    print("\n⚡ Identifying Risks...")
    
    risks_data = [
        ("Data Breach Risk", "Unauthorized access to customer data", RiskLevel.CRITICAL, 5, 3),
        ("Compliance Gap", "Missing encryption for data at rest", RiskLevel.HIGH, 4, 4),
        ("Access Control Weakness", "Insufficient privilege management", RiskLevel.HIGH, 4, 3),
        ("Incident Response Gap", "Delayed detection of security incidents", RiskLevel.MEDIUM, 3, 3),
        ("Third-party Risk", "Vendor security compliance issues", RiskLevel.MEDIUM, 3, 2)
    ]
    
    risks = []
    for title, desc, level, impact, likelihood in risks_data:
        risk = await compliance.identify_risk(
            title, desc, "", level, impact, likelihood, "risk-owner@company.com"
        )
        risks.append(risk)
        print(f"  ⚡ {title} [{level.value}]")
        
    # Create policies
    print("\n📜 Creating Policies...")
    
    policies_data = [
        ("Information Security Policy", "Overall security policy", "Security"),
        ("Access Control Policy", "User access management", "Access Control"),
        ("Data Protection Policy", "Data handling requirements", "Data Protection"),
        ("Incident Response Policy", "Security incident handling", "Incident Management"),
        ("Acceptable Use Policy", "Acceptable use of systems", "Governance")
    ]
    
    policies = []
    for name, desc, category in policies_data:
        policy = await compliance.create_policy(
            name, desc, category,
            f"Policy content for {name}...",
            [controls[0].control_id]
        )
        policies.append(policy)
        await compliance.approve_policy(policy.policy_id, "ciso@company.com")
        await compliance.publish_policy(policy.policy_id)
        print(f"  📜 {name}")
        
    # Create audit
    print("\n🔍 Creating Audit...")
    
    audit = await compliance.create_audit(
        "Annual SOC 2 Audit",
        "external",
        [frameworks[0].framework_id],
        "Lead Auditor",
        "Big Four Audit Firm",
        30
    )
    print(f"  🔍 {audit.name}")
    
    # Framework compliance scores
    print("\n📊 Compliance Scores:")
    
    for fw in frameworks:
        score = compliance.get_compliance_score(fw.framework_id)
        
        bar = "█" * int(score / 2.5) + "░" * (40 - int(score / 2.5))
        status = "✓" if score >= 80 else "⚠" if score >= 60 else "✗"
        
        print(f"\n  {status} {fw.name}")
        print(f"    [{bar}] {score:.1f}%")
        print(f"    Controls: {fw.total_controls}")
        
    # Control status
    print("\n🔒 Control Status:")
    
    print("\n  ┌───────────────┬────────────────────────────────────┬──────────────────┬──────────────────┬──────────────────┐")
    print("  │ Control       │ Name                               │ Category         │ Status           │ Risk             │")
    print("  ├───────────────┼────────────────────────────────────┼──────────────────┼──────────────────┼──────────────────┤")
    
    for ctrl in controls[:10]:
        num = ctrl.control_number[:13].ljust(13)
        name = ctrl.name[:34].ljust(34)
        category = ctrl.category[:16].ljust(16)
        
        status_icon = {
            "compliant": "✓",
            "non_compliant": "✗",
            "partially_compliant": "⚠",
            "not_assessed": "○"
        }.get(ctrl.status.value, "?")
        status = f"{status_icon} {ctrl.status.value}"[:16].ljust(16)
        
        risk = ctrl.risk_level.value[:16].ljust(16)
        
        print(f"  │ {num} │ {name} │ {category} │ {status} │ {risk} │")
        
    print("  └───────────────┴────────────────────────────────────┴──────────────────┴──────────────────┴──────────────────┘")
    
    # Risk summary
    print("\n⚡ Risk Summary:")
    
    risk_stats = compliance.get_risk_score()
    
    print(f"\n  Open Risks: {risk_stats['open_risks']}")
    print(f"  Total Risk Score: {risk_stats['total_score']}")
    print(f"  Average Score: {risk_stats['avg_score']:.1f}")
    
    print("\n  By Level:")
    for level, count in risk_stats['by_level'].items():
        if count > 0:
            print(f"    {level}: {count}")
            
    # Findings and remediations
    print("\n⚠️ Findings & Remediations:")
    
    rem_stats = compliance.get_remediation_status()
    
    print(f"\n  Total Findings: {len(compliance.findings)}")
    print(f"  Open Findings: {sum(1 for f in compliance.findings.values() if f.status == 'open')}")
    
    print(f"\n  Total Remediations: {rem_stats['total']}")
    print(f"  Completion Rate: {rem_stats['completion_rate']:.1f}%")
    print(f"  Overdue: {rem_stats['overdue']}")
    
    print("\n  By Status:")
    for status, count in rem_stats['by_status'].items():
        if count > 0:
            print(f"    {status}: {count}")
            
    # Policies
    print("\n📜 Policy Status:")
    
    print("\n  ┌───────────────────────────────────────────┬──────────────────┬──────────────────┬────────────────────────┐")
    print("  │ Policy                                    │ Category         │ Status           │ Next Review            │")
    print("  ├───────────────────────────────────────────┼──────────────────┼──────────────────┼────────────────────────┤")
    
    for policy in policies:
        name = policy.name[:41].ljust(41)
        category = policy.category[:16].ljust(16)
        status = policy.status[:16].ljust(16)
        next_review = policy.next_review.strftime("%Y-%m-%d")[:22].ljust(22) if policy.next_review else "N/A".ljust(22)
        
        print(f"  │ {name} │ {category} │ {status} │ {next_review} │")
        
    print("  └───────────────────────────────────────────┴──────────────────┴──────────────────┴────────────────────────┘")
    
    # Audit status
    print("\n🔍 Audit Status:")
    
    print(f"\n  🔍 {audit.name}")
    print(f"     Type: {audit.audit_type}")
    print(f"     Auditor: {audit.auditor} ({audit.auditor_org})")
    print(f"     Status: {audit.status}")
    print(f"     Period: {audit.audit_period_start.strftime('%Y-%m-%d')} - {audit.audit_period_end.strftime('%Y-%m-%d')}")
    
    # Evidence summary
    print("\n📎 Evidence Summary:")
    
    by_type = {}
    for evd in compliance.evidence.values():
        by_type[evd.evidence_type.value] = by_type.get(evd.evidence_type.value, 0) + 1
        
    print(f"\n  Total Evidence: {len(compliance.evidence)}")
    print(f"  Valid: {sum(1 for e in compliance.evidence.values() if e.is_valid)}")
    
    print("\n  By Type:")
    for evd_type, count in by_type.items():
        print(f"    {evd_type}: {count}")
        
    # Statistics
    print("\n📊 Overall Statistics:")
    
    stats = compliance.get_statistics()
    
    print(f"\n  Frameworks: {stats['total_frameworks']}")
    print(f"  Controls: {stats['total_controls']}")
    print(f"  Evidence: {stats['valid_evidence']}/{stats['total_evidence']} valid")
    print(f"  Risks: {stats['open_risks']}/{stats['total_risks']} open")
    print(f"  Findings: {stats['open_findings']}/{stats['total_findings']} open")
    print(f"  Remediations: {stats['total_remediations']}")
    print(f"  Policies: {stats['published_policies']}/{stats['total_policies']} published")
    print(f"  Audits: {stats['completed_audits']}/{stats['total_audits']} completed")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                      Compliance Manager Platform                    │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Active Frameworks:           {stats['total_frameworks']:>12}                          │")
    print(f"│ Total Controls:              {stats['total_controls']:>12}                          │")
    print(f"│ Compliant Controls:          {stats['controls_by_status']['compliant']:>12}                          │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Open Risks:                  {stats['open_risks']:>12}                          │")
    print(f"│ Open Findings:               {stats['open_findings']:>12}                          │")
    print(f"│ Published Policies:          {stats['published_policies']:>12}                          │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Compliance Manager Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
