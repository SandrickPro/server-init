#!/usr/bin/env python3
"""
Server Init - Iteration 342: Compliance Automation Platform
Платформа автоматизации комплаенса

Функционал:
- Compliance Framework - фреймворки соответствия
- Control Mapping - маппинг контролей
- Evidence Collection - сбор доказательств
- Gap Analysis - анализ пробелов
- Audit Management - управление аудитами
- Remediation Tracking - отслеживание исправлений
- Report Generation - генерация отчетов
- Continuous Monitoring - непрерывный мониторинг
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid


class FrameworkType(Enum):
    """Тип фреймворка"""
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    NIST = "nist"
    COBIT = "cobit"
    CUSTOM = "custom"


class ControlStatus(Enum):
    """Статус контроля"""
    NOT_IMPLEMENTED = "not_implemented"
    PARTIALLY_IMPLEMENTED = "partially_implemented"
    IMPLEMENTED = "implemented"
    NOT_APPLICABLE = "not_applicable"
    UNDER_REVIEW = "under_review"


class ControlType(Enum):
    """Тип контроля"""
    PREVENTIVE = "preventive"
    DETECTIVE = "detective"
    CORRECTIVE = "corrective"
    COMPENSATING = "compensating"


class EvidenceType(Enum):
    """Тип доказательства"""
    SCREENSHOT = "screenshot"
    DOCUMENT = "document"
    LOG = "log"
    CONFIGURATION = "configuration"
    REPORT = "report"
    ATTESTATION = "attestation"
    AUTOMATED = "automated"


class EvidenceStatus(Enum):
    """Статус доказательства"""
    PENDING = "pending"
    COLLECTED = "collected"
    VALIDATED = "validated"
    REJECTED = "rejected"
    EXPIRED = "expired"


class AuditStatus(Enum):
    """Статус аудита"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class FindingSeverity(Enum):
    """Серьезность находки"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RemediationStatus(Enum):
    """Статус исправления"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ACCEPTED = "accepted"
    DEFERRED = "deferred"


class RiskLevel(Enum):
    """Уровень риска"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ComplianceFramework:
    """Фреймворк комплаенса"""
    framework_id: str
    name: str
    
    # Type
    framework_type: FrameworkType = FrameworkType.CUSTOM
    
    # Version
    version: str = "1.0"
    
    # Description
    description: str = ""
    
    # Domain IDs
    domain_ids: List[str] = field(default_factory=list)
    
    # Status
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    effective_date: Optional[datetime] = None


@dataclass
class ComplianceDomain:
    """Домен комплаенса"""
    domain_id: str
    name: str
    
    # Framework
    framework_id: str = ""
    
    # Control IDs
    control_ids: List[str] = field(default_factory=list)
    
    # Description
    description: str = ""
    
    # Weight
    weight: float = 1.0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Control:
    """Контроль"""
    control_id: str
    name: str
    
    # Reference
    reference_id: str = ""  # e.g., "CC1.1", "A.5.1.1"
    
    # Domain
    domain_id: str = ""
    
    # Type
    control_type: ControlType = ControlType.PREVENTIVE
    
    # Status
    status: ControlStatus = ControlStatus.NOT_IMPLEMENTED
    
    # Description
    description: str = ""
    implementation_guidance: str = ""
    
    # Owner
    owner_id: str = ""
    owner_name: str = ""
    
    # Evidence requirements
    required_evidence_types: List[EvidenceType] = field(default_factory=list)
    
    # Assessment
    last_assessed: Optional[datetime] = None
    assessment_frequency_days: int = 90
    
    # Risk
    risk_if_not_implemented: RiskLevel = RiskLevel.MEDIUM
    
    # Effectiveness
    effectiveness_score: float = 0.0  # 0-100
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ControlMapping:
    """Маппинг контролей"""
    mapping_id: str
    
    # Source
    source_control_id: str = ""
    source_framework: str = ""
    
    # Target
    target_control_id: str = ""
    target_framework: str = ""
    
    # Relationship
    relationship: str = "equivalent"  # equivalent, related, partial
    
    # Description
    notes: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Evidence:
    """Доказательство"""
    evidence_id: str
    name: str
    
    # Control
    control_id: str = ""
    
    # Type
    evidence_type: EvidenceType = EvidenceType.DOCUMENT
    
    # Status
    status: EvidenceStatus = EvidenceStatus.PENDING
    
    # Content
    description: str = ""
    file_path: str = ""
    file_hash: str = ""
    
    # Collection
    collected_by: str = ""
    collection_date: Optional[datetime] = None
    
    # Validation
    validated_by: str = ""
    validation_date: Optional[datetime] = None
    validation_notes: str = ""
    
    # Validity
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    
    # Automated
    is_automated: bool = False
    automation_source: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class GapAnalysis:
    """Анализ пробелов"""
    analysis_id: str
    name: str
    
    # Framework
    framework_id: str = ""
    
    # Scope
    domain_ids: List[str] = field(default_factory=list)
    
    # Results
    total_controls: int = 0
    implemented_controls: int = 0
    partial_controls: int = 0
    not_implemented_controls: int = 0
    not_applicable_controls: int = 0
    
    # Compliance score
    compliance_score: float = 0.0
    
    # Gaps by domain
    gaps_by_domain: Dict[str, int] = field(default_factory=dict)
    
    # Risk summary
    critical_gaps: int = 0
    high_gaps: int = 0
    medium_gaps: int = 0
    low_gaps: int = 0
    
    # Analysis
    performed_by: str = ""
    
    # Timestamps
    analysis_date: datetime = field(default_factory=datetime.now)


@dataclass
class Audit:
    """Аудит"""
    audit_id: str
    name: str
    
    # Type
    audit_type: str = "internal"  # internal, external, certification
    
    # Framework
    framework_id: str = ""
    
    # Status
    status: AuditStatus = AuditStatus.PLANNED
    
    # Timeline
    planned_start: Optional[datetime] = None
    planned_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    
    # Scope
    scope_description: str = ""
    in_scope_controls: List[str] = field(default_factory=list)
    
    # Auditor
    auditor_name: str = ""
    auditor_organization: str = ""
    
    # Finding IDs
    finding_ids: List[str] = field(default_factory=list)
    
    # Outcome
    outcome: str = ""
    certification_granted: bool = False
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AuditFinding:
    """Находка аудита"""
    finding_id: str
    title: str
    
    # Audit
    audit_id: str = ""
    
    # Control
    control_id: str = ""
    control_reference: str = ""
    
    # Severity
    severity: FindingSeverity = FindingSeverity.MEDIUM
    
    # Description
    description: str = ""
    root_cause: str = ""
    impact: str = ""
    
    # Recommendation
    recommendation: str = ""
    
    # Status
    status: RemediationStatus = RemediationStatus.OPEN
    
    # Assignment
    assigned_to: str = ""
    
    # Remediation
    remediation_plan_id: str = ""
    due_date: Optional[datetime] = None
    
    # Timestamps
    identified_date: datetime = field(default_factory=datetime.now)
    resolved_date: Optional[datetime] = None


@dataclass
class RemediationPlan:
    """План исправления"""
    plan_id: str
    name: str
    
    # Finding
    finding_id: str = ""
    
    # Actions
    action_items: List[Dict[str, Any]] = field(default_factory=list)
    
    # Owner
    owner_id: str = ""
    owner_name: str = ""
    
    # Status
    status: RemediationStatus = RemediationStatus.OPEN
    
    # Timeline
    due_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    
    # Progress
    progress_percent: float = 0.0
    
    # Notes
    notes: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ComplianceReport:
    """Отчет о соответствии"""
    report_id: str
    name: str
    
    # Type
    report_type: str = "executive"  # executive, detailed, certification
    
    # Framework
    framework_id: str = ""
    
    # Scope
    reporting_period_start: Optional[datetime] = None
    reporting_period_end: Optional[datetime] = None
    
    # Content
    executive_summary: str = ""
    compliance_score: float = 0.0
    key_findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Data
    control_summary: Dict[str, int] = field(default_factory=dict)
    
    # Generated
    generated_by: str = ""
    generation_date: datetime = field(default_factory=datetime.now)
    
    # File
    file_path: str = ""


@dataclass
class MonitoringRule:
    """Правило мониторинга"""
    rule_id: str
    name: str
    
    # Control
    control_id: str = ""
    
    # Condition
    condition_type: str = ""  # evidence_expiry, control_drift, metric_threshold
    threshold: Any = None
    
    # Alert
    alert_severity: FindingSeverity = FindingSeverity.MEDIUM
    alert_recipients: List[str] = field(default_factory=list)
    
    # Status
    is_enabled: bool = True
    last_triggered: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


class ComplianceManager:
    """Менеджер комплаенса"""
    
    def __init__(self):
        self.frameworks: Dict[str, ComplianceFramework] = {}
        self.domains: Dict[str, ComplianceDomain] = {}
        self.controls: Dict[str, Control] = {}
        self.mappings: Dict[str, ControlMapping] = {}
        self.evidence: Dict[str, Evidence] = {}
        self.audits: Dict[str, Audit] = {}
        self.findings: Dict[str, AuditFinding] = {}
        self.remediation_plans: Dict[str, RemediationPlan] = {}
        self.reports: Dict[str, ComplianceReport] = {}
        self.monitoring_rules: Dict[str, MonitoringRule] = {}
        self.gap_analyses: Dict[str, GapAnalysis] = {}
        
    async def create_framework(self, name: str,
                              framework_type: FrameworkType,
                              version: str = "1.0",
                              description: str = "") -> ComplianceFramework:
        """Создание фреймворка"""
        framework = ComplianceFramework(
            framework_id=f"fw_{uuid.uuid4().hex[:8]}",
            name=name,
            framework_type=framework_type,
            version=version,
            description=description
        )
        
        self.frameworks[framework.framework_id] = framework
        return framework
        
    async def create_domain(self, name: str,
                           framework_id: str,
                           description: str = "",
                           weight: float = 1.0) -> Optional[ComplianceDomain]:
        """Создание домена"""
        framework = self.frameworks.get(framework_id)
        if not framework:
            return None
            
        domain = ComplianceDomain(
            domain_id=f"dom_{uuid.uuid4().hex[:8]}",
            name=name,
            framework_id=framework_id,
            description=description,
            weight=weight
        )
        
        framework.domain_ids.append(domain.domain_id)
        self.domains[domain.domain_id] = domain
        return domain
        
    async def create_control(self, name: str,
                            reference_id: str,
                            domain_id: str,
                            control_type: ControlType = ControlType.PREVENTIVE,
                            description: str = "",
                            implementation_guidance: str = "",
                            owner_id: str = "",
                            owner_name: str = "",
                            required_evidence_types: List[EvidenceType] = None,
                            assessment_frequency_days: int = 90,
                            risk_if_not_implemented: RiskLevel = RiskLevel.MEDIUM) -> Optional[Control]:
        """Создание контроля"""
        domain = self.domains.get(domain_id)
        if not domain:
            return None
            
        control = Control(
            control_id=f"ctrl_{uuid.uuid4().hex[:8]}",
            name=name,
            reference_id=reference_id,
            domain_id=domain_id,
            control_type=control_type,
            description=description,
            implementation_guidance=implementation_guidance,
            owner_id=owner_id,
            owner_name=owner_name,
            required_evidence_types=required_evidence_types or [],
            assessment_frequency_days=assessment_frequency_days,
            risk_if_not_implemented=risk_if_not_implemented
        )
        
        domain.control_ids.append(control.control_id)
        self.controls[control.control_id] = control
        return control
        
    async def update_control_status(self, control_id: str,
                                   status: ControlStatus,
                                   effectiveness_score: float = None) -> bool:
        """Обновление статуса контроля"""
        control = self.controls.get(control_id)
        if not control:
            return False
            
        control.status = status
        control.last_assessed = datetime.now()
        
        if effectiveness_score is not None:
            control.effectiveness_score = effectiveness_score
            
        return True
        
    async def create_control_mapping(self, source_control_id: str,
                                    target_control_id: str,
                                    relationship: str = "equivalent",
                                    notes: str = "") -> ControlMapping:
        """Создание маппинга контролей"""
        source = self.controls.get(source_control_id)
        target = self.controls.get(target_control_id)
        
        source_fw = ""
        target_fw = ""
        
        if source:
            domain = self.domains.get(source.domain_id)
            if domain:
                fw = self.frameworks.get(domain.framework_id)
                source_fw = fw.name if fw else ""
                
        if target:
            domain = self.domains.get(target.domain_id)
            if domain:
                fw = self.frameworks.get(domain.framework_id)
                target_fw = fw.name if fw else ""
                
        mapping = ControlMapping(
            mapping_id=f"map_{uuid.uuid4().hex[:8]}",
            source_control_id=source_control_id,
            source_framework=source_fw,
            target_control_id=target_control_id,
            target_framework=target_fw,
            relationship=relationship,
            notes=notes
        )
        
        self.mappings[mapping.mapping_id] = mapping
        return mapping
        
    async def collect_evidence(self, control_id: str,
                              name: str,
                              evidence_type: EvidenceType,
                              description: str,
                              collected_by: str,
                              file_path: str = "",
                              valid_until: datetime = None,
                              is_automated: bool = False,
                              automation_source: str = "") -> Optional[Evidence]:
        """Сбор доказательства"""
        control = self.controls.get(control_id)
        if not control:
            return None
            
        evidence = Evidence(
            evidence_id=f"evd_{uuid.uuid4().hex[:12]}",
            name=name,
            control_id=control_id,
            evidence_type=evidence_type,
            status=EvidenceStatus.COLLECTED,
            description=description,
            file_path=file_path,
            collected_by=collected_by,
            collection_date=datetime.now(),
            valid_from=datetime.now(),
            valid_until=valid_until or (datetime.now() + timedelta(days=365)),
            is_automated=is_automated,
            automation_source=automation_source
        )
        
        self.evidence[evidence.evidence_id] = evidence
        return evidence
        
    async def validate_evidence(self, evidence_id: str,
                               validated_by: str,
                               is_valid: bool,
                               notes: str = "") -> bool:
        """Валидация доказательства"""
        evidence = self.evidence.get(evidence_id)
        if not evidence:
            return False
            
        evidence.status = EvidenceStatus.VALIDATED if is_valid else EvidenceStatus.REJECTED
        evidence.validated_by = validated_by
        evidence.validation_date = datetime.now()
        evidence.validation_notes = notes
        
        return True
        
    async def run_gap_analysis(self, framework_id: str,
                              performed_by: str,
                              domain_ids: List[str] = None) -> Optional[GapAnalysis]:
        """Запуск анализа пробелов"""
        framework = self.frameworks.get(framework_id)
        if not framework:
            return None
            
        # Determine scope
        target_domains = domain_ids or framework.domain_ids
        
        analysis = GapAnalysis(
            analysis_id=f"gap_{uuid.uuid4().hex[:8]}",
            name=f"Gap Analysis - {framework.name}",
            framework_id=framework_id,
            domain_ids=target_domains,
            performed_by=performed_by
        )
        
        # Analyze controls
        for domain_id in target_domains:
            domain = self.domains.get(domain_id)
            if not domain:
                continue
                
            domain_gaps = 0
            
            for control_id in domain.control_ids:
                control = self.controls.get(control_id)
                if not control:
                    continue
                    
                analysis.total_controls += 1
                
                if control.status == ControlStatus.IMPLEMENTED:
                    analysis.implemented_controls += 1
                elif control.status == ControlStatus.PARTIALLY_IMPLEMENTED:
                    analysis.partial_controls += 1
                    domain_gaps += 1
                elif control.status == ControlStatus.NOT_APPLICABLE:
                    analysis.not_applicable_controls += 1
                else:
                    analysis.not_implemented_controls += 1
                    domain_gaps += 1
                    
                    # Count by risk
                    if control.status == ControlStatus.NOT_IMPLEMENTED:
                        if control.risk_if_not_implemented == RiskLevel.CRITICAL:
                            analysis.critical_gaps += 1
                        elif control.risk_if_not_implemented == RiskLevel.HIGH:
                            analysis.high_gaps += 1
                        elif control.risk_if_not_implemented == RiskLevel.MEDIUM:
                            analysis.medium_gaps += 1
                        else:
                            analysis.low_gaps += 1
                            
            analysis.gaps_by_domain[domain.name] = domain_gaps
            
        # Calculate compliance score
        applicable = analysis.total_controls - analysis.not_applicable_controls
        if applicable > 0:
            implemented_score = analysis.implemented_controls * 100
            partial_score = analysis.partial_controls * 50
            analysis.compliance_score = (implemented_score + partial_score) / applicable
            
        self.gap_analyses[analysis.analysis_id] = analysis
        return analysis
        
    async def create_audit(self, name: str,
                          framework_id: str,
                          audit_type: str = "internal",
                          planned_start: datetime = None,
                          planned_end: datetime = None,
                          scope_description: str = "",
                          in_scope_controls: List[str] = None,
                          auditor_name: str = "",
                          auditor_organization: str = "") -> Audit:
        """Создание аудита"""
        audit = Audit(
            audit_id=f"aud_{uuid.uuid4().hex[:8]}",
            name=name,
            framework_id=framework_id,
            audit_type=audit_type,
            planned_start=planned_start,
            planned_end=planned_end,
            scope_description=scope_description,
            in_scope_controls=in_scope_controls or [],
            auditor_name=auditor_name,
            auditor_organization=auditor_organization
        )
        
        self.audits[audit.audit_id] = audit
        return audit
        
    async def start_audit(self, audit_id: str) -> bool:
        """Начало аудита"""
        audit = self.audits.get(audit_id)
        if not audit or audit.status != AuditStatus.PLANNED:
            return False
            
        audit.status = AuditStatus.IN_PROGRESS
        audit.actual_start = datetime.now()
        return True
        
    async def complete_audit(self, audit_id: str,
                            outcome: str,
                            certification_granted: bool = False) -> bool:
        """Завершение аудита"""
        audit = self.audits.get(audit_id)
        if not audit or audit.status != AuditStatus.IN_PROGRESS:
            return False
            
        audit.status = AuditStatus.COMPLETED
        audit.actual_end = datetime.now()
        audit.outcome = outcome
        audit.certification_granted = certification_granted
        return True
        
    async def create_finding(self, audit_id: str,
                            title: str,
                            control_id: str,
                            severity: FindingSeverity,
                            description: str,
                            root_cause: str = "",
                            impact: str = "",
                            recommendation: str = "",
                            assigned_to: str = "",
                            due_date: datetime = None) -> Optional[AuditFinding]:
        """Создание находки"""
        audit = self.audits.get(audit_id)
        if not audit:
            return None
            
        control = self.controls.get(control_id)
        control_reference = control.reference_id if control else ""
        
        finding = AuditFinding(
            finding_id=f"find_{uuid.uuid4().hex[:8]}",
            title=title,
            audit_id=audit_id,
            control_id=control_id,
            control_reference=control_reference,
            severity=severity,
            description=description,
            root_cause=root_cause,
            impact=impact,
            recommendation=recommendation,
            assigned_to=assigned_to,
            due_date=due_date or (datetime.now() + timedelta(days=30))
        )
        
        audit.finding_ids.append(finding.finding_id)
        self.findings[finding.finding_id] = finding
        return finding
        
    async def create_remediation_plan(self, finding_id: str,
                                     name: str,
                                     owner_id: str,
                                     owner_name: str,
                                     action_items: List[Dict[str, Any]],
                                     due_date: datetime = None) -> Optional[RemediationPlan]:
        """Создание плана исправления"""
        finding = self.findings.get(finding_id)
        if not finding:
            return None
            
        plan = RemediationPlan(
            plan_id=f"rem_{uuid.uuid4().hex[:8]}",
            name=name,
            finding_id=finding_id,
            action_items=action_items,
            owner_id=owner_id,
            owner_name=owner_name,
            due_date=due_date or finding.due_date
        )
        
        finding.remediation_plan_id = plan.plan_id
        self.remediation_plans[plan.plan_id] = plan
        return plan
        
    async def update_remediation_progress(self, plan_id: str,
                                         progress: float,
                                         notes: str = "") -> bool:
        """Обновление прогресса исправления"""
        plan = self.remediation_plans.get(plan_id)
        if not plan:
            return False
            
        plan.progress_percent = progress
        if notes:
            plan.notes = notes
            
        if progress >= 100:
            plan.status = RemediationStatus.RESOLVED
            plan.completion_date = datetime.now()
            
            # Update finding
            finding = self.findings.get(plan.finding_id)
            if finding:
                finding.status = RemediationStatus.RESOLVED
                finding.resolved_date = datetime.now()
        elif progress > 0:
            plan.status = RemediationStatus.IN_PROGRESS
            
        return True
        
    async def generate_compliance_report(self, framework_id: str,
                                        report_type: str,
                                        reporting_period_start: datetime,
                                        reporting_period_end: datetime,
                                        generated_by: str) -> Optional[ComplianceReport]:
        """Генерация отчета о соответствии"""
        framework = self.frameworks.get(framework_id)
        if not framework:
            return None
            
        # Run gap analysis for current state
        gap_analysis = await self.run_gap_analysis(framework_id, generated_by)
        
        # Collect statistics
        control_summary = {
            "implemented": gap_analysis.implemented_controls if gap_analysis else 0,
            "partial": gap_analysis.partial_controls if gap_analysis else 0,
            "not_implemented": gap_analysis.not_implemented_controls if gap_analysis else 0,
            "not_applicable": gap_analysis.not_applicable_controls if gap_analysis else 0
        }
        
        # Collect findings
        key_findings = []
        recommendations = []
        
        for finding in self.findings.values():
            audit = self.audits.get(finding.audit_id)
            if audit and audit.framework_id == framework_id:
                if finding.status != RemediationStatus.RESOLVED:
                    key_findings.append(f"{finding.severity.value.upper()}: {finding.title}")
                    if finding.recommendation:
                        recommendations.append(finding.recommendation)
                        
        # Executive summary
        compliance_score = gap_analysis.compliance_score if gap_analysis else 0
        executive_summary = f"""
Compliance Assessment Report for {framework.name}

Assessment Period: {reporting_period_start.strftime('%Y-%m-%d')} to {reporting_period_end.strftime('%Y-%m-%d')}

Overall Compliance Score: {compliance_score:.1f}%

Key Metrics:
- Total Controls: {gap_analysis.total_controls if gap_analysis else 0}
- Implemented: {control_summary['implemented']}
- Partially Implemented: {control_summary['partial']}
- Not Implemented: {control_summary['not_implemented']}
- Not Applicable: {control_summary['not_applicable']}

Open Findings: {len(key_findings)}
"""
        
        report = ComplianceReport(
            report_id=f"rpt_{uuid.uuid4().hex[:12]}",
            name=f"{framework.name} Compliance Report",
            report_type=report_type,
            framework_id=framework_id,
            reporting_period_start=reporting_period_start,
            reporting_period_end=reporting_period_end,
            executive_summary=executive_summary.strip(),
            compliance_score=compliance_score,
            key_findings=key_findings[:10],
            recommendations=recommendations[:10],
            control_summary=control_summary,
            generated_by=generated_by,
            file_path=f"/reports/compliance_{framework.framework_type.value}_{datetime.now().strftime('%Y%m%d')}.pdf"
        )
        
        self.reports[report.report_id] = report
        return report
        
    async def create_monitoring_rule(self, control_id: str,
                                    name: str,
                                    condition_type: str,
                                    threshold: Any,
                                    alert_severity: FindingSeverity = FindingSeverity.MEDIUM,
                                    alert_recipients: List[str] = None) -> MonitoringRule:
        """Создание правила мониторинга"""
        rule = MonitoringRule(
            rule_id=f"mon_{uuid.uuid4().hex[:8]}",
            name=name,
            control_id=control_id,
            condition_type=condition_type,
            threshold=threshold,
            alert_severity=alert_severity,
            alert_recipients=alert_recipients or []
        )
        
        self.monitoring_rules[rule.rule_id] = rule
        return rule
        
    def get_controls_needing_assessment(self) -> List[Control]:
        """Получение контролей, требующих оценки"""
        result = []
        now = datetime.now()
        
        for control in self.controls.values():
            if control.last_assessed:
                next_assessment = control.last_assessed + timedelta(days=control.assessment_frequency_days)
                if next_assessment <= now:
                    result.append(control)
            else:
                result.append(control)
                
        return result
        
    def get_expiring_evidence(self, days: int = 30) -> List[Evidence]:
        """Получение истекающих доказательств"""
        result = []
        threshold = datetime.now() + timedelta(days=days)
        
        for evd in self.evidence.values():
            if evd.status == EvidenceStatus.VALIDATED:
                if evd.valid_until and evd.valid_until <= threshold:
                    result.append(evd)
                    
        return result
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_frameworks = len(self.frameworks)
        total_domains = len(self.domains)
        total_controls = len(self.controls)
        
        # Control status
        implemented = sum(1 for c in self.controls.values() if c.status == ControlStatus.IMPLEMENTED)
        partial = sum(1 for c in self.controls.values() if c.status == ControlStatus.PARTIALLY_IMPLEMENTED)
        not_impl = sum(1 for c in self.controls.values() if c.status == ControlStatus.NOT_IMPLEMENTED)
        
        total_evidence = len(self.evidence)
        validated_evidence = sum(1 for e in self.evidence.values() if e.status == EvidenceStatus.VALIDATED)
        
        total_audits = len(self.audits)
        completed_audits = sum(1 for a in self.audits.values() if a.status == AuditStatus.COMPLETED)
        
        total_findings = len(self.findings)
        open_findings = sum(1 for f in self.findings.values() if f.status == RemediationStatus.OPEN)
        resolved_findings = sum(1 for f in self.findings.values() if f.status == RemediationStatus.RESOLVED)
        
        # By severity
        by_severity = {}
        for finding in self.findings.values():
            sev = finding.severity.value
            by_severity[sev] = by_severity.get(sev, 0) + 1
            
        total_remediation = len(self.remediation_plans)
        
        needing_assessment = len(self.get_controls_needing_assessment())
        expiring_evidence = len(self.get_expiring_evidence())
        
        return {
            "total_frameworks": total_frameworks,
            "total_domains": total_domains,
            "total_controls": total_controls,
            "implemented_controls": implemented,
            "partial_controls": partial,
            "not_implemented_controls": not_impl,
            "total_evidence": total_evidence,
            "validated_evidence": validated_evidence,
            "total_audits": total_audits,
            "completed_audits": completed_audits,
            "total_findings": total_findings,
            "open_findings": open_findings,
            "resolved_findings": resolved_findings,
            "findings_by_severity": by_severity,
            "total_remediation_plans": total_remediation,
            "controls_needing_assessment": needing_assessment,
            "expiring_evidence_30d": expiring_evidence
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 342: Compliance Automation Platform")
    print("=" * 60)
    
    manager = ComplianceManager()
    print("✓ Compliance Manager initialized")
    
    # Create Frameworks
    print("\n📋 Creating Compliance Frameworks...")
    
    frameworks_data = [
        ("SOC 2 Type II", FrameworkType.SOC2, "2017", "Service Organization Control 2"),
        ("ISO 27001:2022", FrameworkType.ISO27001, "2022", "Information Security Management"),
        ("GDPR", FrameworkType.GDPR, "2018", "General Data Protection Regulation"),
        ("PCI DSS v4.0", FrameworkType.PCI_DSS, "4.0", "Payment Card Industry Data Security Standard")
    ]
    
    frameworks = []
    for name, ftype, version, desc in frameworks_data:
        fw = await manager.create_framework(name, ftype, version, desc)
        frameworks.append(fw)
        print(f"  📋 {name}")
        
    # Create Domains for SOC 2
    print("\n🏷️ Creating Compliance Domains...")
    
    soc2_domains_data = [
        ("Security", "Controls related to security of the system", 1.5),
        ("Availability", "Controls related to system availability", 1.2),
        ("Processing Integrity", "Controls related to data processing", 1.0),
        ("Confidentiality", "Controls related to data confidentiality", 1.3),
        ("Privacy", "Controls related to personal data privacy", 1.4)
    ]
    
    domains = []
    for name, desc, weight in soc2_domains_data:
        domain = await manager.create_domain(name, frameworks[0].framework_id, desc, weight)
        if domain:
            domains.append(domain)
            print(f"  🏷️ {name}")
            
    # Create Controls
    print("\n🔒 Creating Controls...")
    
    controls_data = [
        # Security controls
        (domains[0].domain_id, "Access Control Policy", "CC6.1", ControlType.PREVENTIVE, "Define and implement access control policies", RiskLevel.HIGH),
        (domains[0].domain_id, "Multi-Factor Authentication", "CC6.2", ControlType.PREVENTIVE, "Implement MFA for all users", RiskLevel.CRITICAL),
        (domains[0].domain_id, "Security Monitoring", "CC7.1", ControlType.DETECTIVE, "Monitor systems for security events", RiskLevel.HIGH),
        (domains[0].domain_id, "Vulnerability Management", "CC7.2", ControlType.PREVENTIVE, "Regular vulnerability scanning", RiskLevel.HIGH),
        (domains[0].domain_id, "Incident Response", "CC7.3", ControlType.CORRECTIVE, "Incident response procedures", RiskLevel.CRITICAL),
        # Availability controls
        (domains[1].domain_id, "System Monitoring", "A1.1", ControlType.DETECTIVE, "Monitor system performance", RiskLevel.MEDIUM),
        (domains[1].domain_id, "Backup Procedures", "A1.2", ControlType.PREVENTIVE, "Regular data backups", RiskLevel.HIGH),
        (domains[1].domain_id, "Disaster Recovery", "A1.3", ControlType.CORRECTIVE, "DR plan and testing", RiskLevel.CRITICAL),
        # Processing Integrity
        (domains[2].domain_id, "Data Validation", "PI1.1", ControlType.PREVENTIVE, "Input/output validation", RiskLevel.MEDIUM),
        (domains[2].domain_id, "Change Management", "PI1.2", ControlType.PREVENTIVE, "Change management process", RiskLevel.HIGH),
        # Confidentiality
        (domains[3].domain_id, "Data Classification", "C1.1", ControlType.PREVENTIVE, "Data classification scheme", RiskLevel.HIGH),
        (domains[3].domain_id, "Encryption at Rest", "C1.2", ControlType.PREVENTIVE, "Encrypt sensitive data at rest", RiskLevel.CRITICAL),
        (domains[3].domain_id, "Encryption in Transit", "C1.3", ControlType.PREVENTIVE, "Encrypt data in transit", RiskLevel.CRITICAL),
        # Privacy
        (domains[4].domain_id, "Privacy Notice", "P1.1", ControlType.PREVENTIVE, "Privacy notice for users", RiskLevel.MEDIUM),
        (domains[4].domain_id, "Data Subject Rights", "P1.2", ControlType.CORRECTIVE, "Process for data subject requests", RiskLevel.HIGH)
    ]
    
    controls = []
    for domain_id, name, ref, ctype, desc, risk in controls_data:
        control = await manager.create_control(
            name, ref, domain_id, ctype, desc,
            f"Implement {name.lower()} according to best practices",
            "security-team", "Security Team",
            [EvidenceType.DOCUMENT, EvidenceType.CONFIGURATION],
            90, risk
        )
        if control:
            controls.append(control)
            print(f"  🔒 {ref}: {name}")
            
    # Update control statuses
    print("\n📊 Updating Control Statuses...")
    
    status_updates = [
        (0, ControlStatus.IMPLEMENTED, 95.0),
        (1, ControlStatus.IMPLEMENTED, 98.0),
        (2, ControlStatus.IMPLEMENTED, 85.0),
        (3, ControlStatus.PARTIALLY_IMPLEMENTED, 60.0),
        (4, ControlStatus.PARTIALLY_IMPLEMENTED, 50.0),
        (5, ControlStatus.IMPLEMENTED, 90.0),
        (6, ControlStatus.IMPLEMENTED, 92.0),
        (7, ControlStatus.PARTIALLY_IMPLEMENTED, 45.0),
        (8, ControlStatus.IMPLEMENTED, 88.0),
        (9, ControlStatus.IMPLEMENTED, 82.0),
        (10, ControlStatus.NOT_IMPLEMENTED, 0.0),
        (11, ControlStatus.IMPLEMENTED, 95.0),
        (12, ControlStatus.IMPLEMENTED, 97.0),
        (13, ControlStatus.NOT_IMPLEMENTED, 0.0),
        (14, ControlStatus.PARTIALLY_IMPLEMENTED, 40.0)
    ]
    
    for idx, status, score in status_updates:
        if idx < len(controls):
            await manager.update_control_status(controls[idx].control_id, status, score)
            
    implemented = sum(1 for c in controls if c.status == ControlStatus.IMPLEMENTED)
    partial = sum(1 for c in controls if c.status == ControlStatus.PARTIALLY_IMPLEMENTED)
    not_impl = sum(1 for c in controls if c.status == ControlStatus.NOT_IMPLEMENTED)
    print(f"  Updated: {implemented} implemented, {partial} partial, {not_impl} not implemented")
    
    # Collect Evidence
    print("\n📄 Collecting Evidence...")
    
    evidence_data = [
        (controls[0].control_id, "Access Control Policy Document", EvidenceType.DOCUMENT, "access-policy-v3.pdf"),
        (controls[1].control_id, "MFA Configuration Screenshot", EvidenceType.SCREENSHOT, "mfa-config.png"),
        (controls[2].control_id, "SIEM Dashboard Export", EvidenceType.AUTOMATED, "siem-dashboard.json"),
        (controls[5].control_id, "Monitoring Dashboard", EvidenceType.SCREENSHOT, "monitoring.png"),
        (controls[6].control_id, "Backup Configuration", EvidenceType.CONFIGURATION, "backup-config.yaml"),
        (controls[11].control_id, "Encryption Policy", EvidenceType.DOCUMENT, "encryption-policy.pdf"),
        (controls[12].control_id, "TLS Configuration", EvidenceType.CONFIGURATION, "tls-config.json")
    ]
    
    evidence_list = []
    for ctrl_id, name, etype, fpath in evidence_data:
        evd = await manager.collect_evidence(
            ctrl_id, name, etype,
            f"Evidence for control compliance",
            "auditor",
            f"/evidence/{fpath}",
            datetime.now() + timedelta(days=365),
            etype == EvidenceType.AUTOMATED,
            "compliance-collector" if etype == EvidenceType.AUTOMATED else ""
        )
        if evd:
            evidence_list.append(evd)
            await manager.validate_evidence(evd.evidence_id, "compliance-officer", True, "Verified")
            print(f"  📄 {name}")
            
    # Run Gap Analysis
    print("\n🔍 Running Gap Analysis...")
    
    gap_analysis = await manager.run_gap_analysis(frameworks[0].framework_id, "compliance-officer")
    if gap_analysis:
        print(f"  ✓ Analysis completed: {gap_analysis.compliance_score:.1f}% compliance")
        print(f"    Critical gaps: {gap_analysis.critical_gaps}")
        print(f"    High gaps: {gap_analysis.high_gaps}")
        
    # Create Audit
    print("\n📝 Creating and Running Audit...")
    
    audit = await manager.create_audit(
        "SOC 2 Type II Annual Audit",
        frameworks[0].framework_id,
        "external",
        datetime.now() - timedelta(days=30),
        datetime.now() + timedelta(days=30),
        "Annual SOC 2 Type II audit covering all trust service criteria",
        [c.control_id for c in controls],
        "John Smith",
        "Big4 Audit Firm"
    )
    
    await manager.start_audit(audit.audit_id)
    print(f"  📝 Audit started: {audit.name}")
    
    # Create Findings
    print("\n⚠️ Creating Audit Findings...")
    
    findings_data = [
        ("Missing Data Classification", controls[10].control_id, FindingSeverity.HIGH, "Data classification scheme not implemented", "Lack of resource allocation", "Unauthorized access to sensitive data", "Implement data classification within 60 days"),
        ("Incomplete DR Plan", controls[7].control_id, FindingSeverity.CRITICAL, "Disaster recovery plan not fully tested", "Insufficient testing schedule", "Extended downtime in case of disaster", "Complete DR testing immediately"),
        ("Privacy Notice Gaps", controls[13].control_id, FindingSeverity.MEDIUM, "Privacy notice missing required disclosures", "Regulatory changes", "Potential GDPR violations", "Update privacy notice within 30 days"),
        ("Vulnerability Scan Coverage", controls[3].control_id, FindingSeverity.HIGH, "Vulnerability scanning not covering all assets", "Asset inventory incomplete", "Unpatched vulnerabilities", "Expand scan coverage")
    ]
    
    findings = []
    for title, ctrl_id, severity, desc, cause, impact, rec in findings_data:
        finding = await manager.create_finding(
            audit.audit_id, title, ctrl_id, severity, desc, cause, impact, rec,
            "security-team",
            datetime.now() + timedelta(days=30 if severity != FindingSeverity.CRITICAL else 7)
        )
        if finding:
            findings.append(finding)
            print(f"  ⚠️ {severity.value.upper()}: {title}")
            
    # Create Remediation Plans
    print("\n🔧 Creating Remediation Plans...")
    
    for finding in findings[:2]:
        plan = await manager.create_remediation_plan(
            finding.finding_id,
            f"Remediation: {finding.title}",
            "security-team",
            "Security Team",
            [
                {"action": "Assess current state", "status": "completed"},
                {"action": "Design solution", "status": "in_progress"},
                {"action": "Implement changes", "status": "pending"},
                {"action": "Verify implementation", "status": "pending"}
            ],
            finding.due_date
        )
        if plan:
            await manager.update_remediation_progress(plan.plan_id, 35.0)
            print(f"  🔧 {plan.name}")
            
    # Complete Audit
    await manager.complete_audit(audit.audit_id, "Qualified opinion with findings", False)
    print("\n  ✓ Audit completed")
    
    # Generate Report
    print("\n📊 Generating Compliance Report...")
    
    report = await manager.generate_compliance_report(
        frameworks[0].framework_id,
        "executive",
        datetime.now() - timedelta(days=365),
        datetime.now(),
        "compliance-officer"
    )
    if report:
        print(f"  📊 Report generated: {report.name}")
        
    # Create Monitoring Rules
    print("\n👁️ Creating Monitoring Rules...")
    
    monitoring_data = [
        (controls[1].control_id, "MFA Compliance Check", "control_drift", 95, FindingSeverity.CRITICAL),
        (controls[11].control_id, "Encryption Status", "metric_threshold", 100, FindingSeverity.HIGH),
        (controls[6].control_id, "Backup Evidence Expiry", "evidence_expiry", 30, FindingSeverity.MEDIUM)
    ]
    
    for ctrl_id, name, cond, thresh, severity in monitoring_data:
        rule = await manager.create_monitoring_rule(ctrl_id, name, cond, thresh, severity, ["compliance-team@example.com"])
        print(f"  👁️ {name}")
        
    # Compliance Frameworks
    print("\n📋 Compliance Frameworks:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                         │ Type          │ Version │ Domains │ Controls │ Description                                                                              │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for fw in frameworks:
        name = fw.name[:28].ljust(28)
        ftype = fw.framework_type.value[:13].ljust(13)
        version = fw.version[:7].ljust(7)
        dom_count = str(len(fw.domain_ids)).ljust(7)
        
        ctrl_count = 0
        for dom_id in fw.domain_ids:
            dom = manager.domains.get(dom_id)
            if dom:
                ctrl_count += len(dom.control_ids)
        ctrl_count = str(ctrl_count).ljust(8)
        
        desc = fw.description[:86].ljust(86)
        
        print(f"  │ {name} │ {ftype} │ {version} │ {dom_count} │ {ctrl_count} │ {desc} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Controls
    print("\n🔒 Control Status:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Ref      │ Name                         │ Type        │ Status                  │ Effectiveness │ Risk     │ Last Assessed        │ Owner                                                                                │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for control in controls:
        ref = control.reference_id[:8].ljust(8)
        name = control.name[:28].ljust(28)
        ctype = control.control_type.value[:11].ljust(11)
        
        status_icons = {
            "implemented": "✓",
            "partially_implemented": "◐",
            "not_implemented": "✗",
            "not_applicable": "○"
        }
        status_icon = status_icons.get(control.status.value, "?")
        status = f"{status_icon} {control.status.value}"[:23].ljust(23)
        
        effectiveness = f"{control.effectiveness_score:.0f}%".ljust(13)
        
        risk_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
        risk_icon = risk_icons.get(control.risk_if_not_implemented.value, "⚪")
        risk = f"{risk_icon}".ljust(8)
        
        assessed = control.last_assessed.strftime("%Y-%m-%d %H:%M") if control.last_assessed else "Never"
        assessed = assessed[:20].ljust(20)
        
        owner = control.owner_name[:86].ljust(86)
        
        print(f"  │ {ref} │ {name} │ {ctype} │ {status} │ {effectiveness} │ {risk} │ {assessed} │ {owner} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Gap Analysis
    if gap_analysis:
        print("\n🔍 Gap Analysis Results:")
        
        print(f"\n  Framework: {frameworks[0].name}")
        print(f"  Compliance Score: {gap_analysis.compliance_score:.1f}%")
        print(f"  Total Controls: {gap_analysis.total_controls}")
        print(f"  Implemented: {gap_analysis.implemented_controls}")
        print(f"  Partially Implemented: {gap_analysis.partial_controls}")
        print(f"  Not Implemented: {gap_analysis.not_implemented_controls}")
        
        print("\n  Gaps by Domain:")
        for domain, gaps in gap_analysis.gaps_by_domain.items():
            print(f"    {domain}: {gaps} gaps")
            
        print(f"\n  Risk Distribution:")
        print(f"    Critical: {gap_analysis.critical_gaps}")
        print(f"    High: {gap_analysis.high_gaps}")
        print(f"    Medium: {gap_analysis.medium_gaps}")
        print(f"    Low: {gap_analysis.low_gaps}")
        
    # Audit Findings
    print("\n⚠️ Audit Findings:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Finding                            │ Control │ Severity │ Status    │ Due Date             │ Assigned To          │ Description                                                                            │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for finding in findings:
        title = finding.title[:34].ljust(34)
        ctrl_ref = finding.control_reference[:7].ljust(7)
        
        sev_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
        sev_icon = sev_icons.get(finding.severity.value, "⚪")
        severity = f"{sev_icon} {finding.severity.value}"[:8].ljust(8)
        
        status = finding.status.value[:9].ljust(9)
        
        due = finding.due_date.strftime("%Y-%m-%d") if finding.due_date else "N/A"
        due = due[:20].ljust(20)
        
        assigned = finding.assigned_to[:20].ljust(20)
        desc = finding.description[:88].ljust(88)
        
        print(f"  │ {title} │ {ctrl_ref} │ {severity} │ {status} │ {due} │ {assigned} │ {desc} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Evidence
    print("\n📄 Collected Evidence:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                              │ Type          │ Control │ Status     │ Collected          │ Valid Until          │ Automated │ Path                                                                                    │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for evd in evidence_list:
        name = evd.name[:33].ljust(33)
        etype = evd.evidence_type.value[:13].ljust(13)
        
        ctrl = manager.controls.get(evd.control_id)
        ctrl_ref = ctrl.reference_id if ctrl else "N/A"
        ctrl_ref = ctrl_ref[:7].ljust(7)
        
        status_icons = {"validated": "✓", "collected": "○", "pending": "⏳", "rejected": "✗", "expired": "⏰"}
        status_icon = status_icons.get(evd.status.value, "?")
        status = f"{status_icon} {evd.status.value}"[:10].ljust(10)
        
        collected = evd.collection_date.strftime("%Y-%m-%d") if evd.collection_date else "N/A"
        collected = collected[:18].ljust(18)
        
        valid = evd.valid_until.strftime("%Y-%m-%d") if evd.valid_until else "N/A"
        valid = valid[:20].ljust(20)
        
        auto = "✓" if evd.is_automated else "✗"
        auto = auto[:9].ljust(9)
        
        path = evd.file_path[:89].ljust(89)
        
        print(f"  │ {name} │ {etype} │ {ctrl_ref} │ {status} │ {collected} │ {valid} │ {auto} │ {path} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Statistics
    stats = manager.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Frameworks: {stats['total_frameworks']}")
    print(f"  Domains: {stats['total_domains']}")
    print(f"  Controls: {stats['implemented_controls']} implemented, {stats['partial_controls']} partial, {stats['not_implemented_controls']} not implemented")
    print(f"  Evidence: {stats['validated_evidence']}/{stats['total_evidence']} validated")
    print(f"  Audits: {stats['completed_audits']}/{stats['total_audits']} completed")
    print(f"  Findings: {stats['open_findings']} open, {stats['resolved_findings']} resolved")
    print(f"  Remediation Plans: {stats['total_remediation_plans']}")
    print(f"  Controls Needing Assessment: {stats['controls_needing_assessment']}")
    print(f"  Expiring Evidence (30d): {stats['expiring_evidence_30d']}")
    
    print("\n  Findings by Severity:")
    for sev, count in stats['findings_by_severity'].items():
        print(f"    {sev}: {count}")
        
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                  Compliance Automation Platform                    │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Compliance Score:                      {gap_analysis.compliance_score if gap_analysis else 0:>6.1f}%                   │")
    print(f"│ Controls (Impl/Partial/Not):   {stats['implemented_controls']:>5}/{stats['partial_controls']:<5}/{stats['not_implemented_controls']:<5}                   │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Open Findings:                {stats['open_findings']:>12}                      │")
    print(f"│ Validated Evidence:           {stats['validated_evidence']:>12}                      │")
    print(f"│ Completed Audits:             {stats['completed_audits']:>12}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Compliance Automation Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
