#!/usr/bin/env python3
"""
Server Init - Iteration 72: Compliance Management Platform
Платформа управления соответствием требованиям

Функционал:
- Framework Management - управление фреймворками
- Control Assessment - оценка контролей
- Evidence Collection - сбор доказательств
- Gap Analysis - анализ пробелов
- Audit Trail - аудит
- Risk Assessment - оценка рисков
- Report Generation - генерация отчётов
- Continuous Compliance - непрерывное соответствие
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


class ComplianceFramework(Enum):
    """Фреймворк соответствия"""
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    NIST = "nist"
    CIS = "cis"
    CUSTOM = "custom"


class ControlStatus(Enum):
    """Статус контроля"""
    NOT_ASSESSED = "not_assessed"
    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    NOT_APPLICABLE = "not_applicable"


class EvidenceType(Enum):
    """Тип доказательства"""
    DOCUMENT = "document"
    SCREENSHOT = "screenshot"
    LOG = "log"
    CONFIGURATION = "configuration"
    INTERVIEW = "interview"
    AUTOMATED_SCAN = "automated_scan"


class RiskLevel(Enum):
    """Уровень риска"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AssessmentStatus(Enum):
    """Статус оценки"""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass
class Control:
    """Контроль"""
    control_id: str
    name: str
    
    # Фреймворк
    framework: ComplianceFramework = ComplianceFramework.CUSTOM
    
    # Категория
    category: str = ""
    domain: str = ""
    
    # Описание
    description: str = ""
    requirements: List[str] = field(default_factory=list)
    
    # Статус
    status: ControlStatus = ControlStatus.NOT_ASSESSED
    
    # Оценка
    assessed_at: Optional[datetime] = None
    assessor: str = ""
    
    # Связи
    parent_control_id: str = ""
    related_controls: List[str] = field(default_factory=list)


@dataclass
class Evidence:
    """Доказательство"""
    evidence_id: str
    
    # Тип
    evidence_type: EvidenceType = EvidenceType.DOCUMENT
    
    # Контент
    title: str = ""
    description: str = ""
    content: str = ""  # URL или содержимое
    
    # Связь с контролем
    control_ids: List[str] = field(default_factory=list)
    
    # Метаданные
    collected_at: datetime = field(default_factory=datetime.now)
    collector: str = ""
    valid_until: Optional[datetime] = None
    
    # Теги
    tags: List[str] = field(default_factory=list)


@dataclass
class Finding:
    """Находка (несоответствие)"""
    finding_id: str
    
    # Контроль
    control_id: str = ""
    
    # Описание
    title: str = ""
    description: str = ""
    
    # Риск
    risk_level: RiskLevel = RiskLevel.MEDIUM
    
    # Рекомендации
    remediation: str = ""
    
    # Статус
    status: str = "open"  # open, in_progress, resolved, accepted
    
    # Время
    identified_at: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Ответственные
    owner: str = ""


@dataclass
class Assessment:
    """Оценка соответствия"""
    assessment_id: str
    name: str
    
    # Фреймворк
    framework: ComplianceFramework = ComplianceFramework.CUSTOM
    
    # Статус
    status: AssessmentStatus = AssessmentStatus.DRAFT
    
    # Время
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Контроли
    control_results: Dict[str, ControlStatus] = field(default_factory=dict)
    
    # Доказательства
    evidence_ids: List[str] = field(default_factory=list)
    
    # Находки
    finding_ids: List[str] = field(default_factory=list)
    
    # Результат
    compliance_score: float = 0.0
    
    # Участники
    assessor: str = ""
    reviewer: str = ""


@dataclass
class ComplianceReport:
    """Отчёт о соответствии"""
    report_id: str
    assessment_id: str
    
    # Сводка
    framework: ComplianceFramework = ComplianceFramework.CUSTOM
    generated_at: datetime = field(default_factory=datetime.now)
    
    # Результаты
    compliance_score: float = 0.0
    total_controls: int = 0
    compliant_controls: int = 0
    non_compliant_controls: int = 0
    
    # Риски
    findings_by_risk: Dict[str, int] = field(default_factory=dict)
    
    # Детали
    summary: str = ""
    recommendations: List[str] = field(default_factory=list)


class FrameworkManager:
    """Менеджер фреймворков"""
    
    def __init__(self):
        self.controls: Dict[str, Control] = {}
        
    def load_framework(self, framework: ComplianceFramework) -> List[Control]:
        """Загрузка контролей фреймворка"""
        if framework == ComplianceFramework.SOC2:
            return self._load_soc2()
        elif framework == ComplianceFramework.ISO27001:
            return self._load_iso27001()
        elif framework == ComplianceFramework.GDPR:
            return self._load_gdpr()
        elif framework == ComplianceFramework.PCI_DSS:
            return self._load_pci_dss()
        elif framework == ComplianceFramework.CIS:
            return self._load_cis()
            
        return []
        
    def _load_soc2(self) -> List[Control]:
        """Загрузка SOC2 контролей"""
        controls = []
        
        soc2_controls = [
            ("CC1", "Security", "Control Environment", [
                ("CC1.1", "Demonstrates commitment to integrity", [
                    "Integrity and ethical values established",
                    "Board of directors demonstrates oversight"
                ]),
                ("CC1.2", "Board demonstrates independence", [
                    "Board exercises oversight",
                    "Establishes structures and processes"
                ]),
                ("CC1.3", "Management establishes structure", [
                    "Defines organizational structure",
                    "Establishes reporting lines"
                ])
            ]),
            ("CC2", "Security", "Communication and Information", [
                ("CC2.1", "COSO Principle 13", [
                    "Relevant and quality information obtained",
                    "Information processed and reported"
                ]),
                ("CC2.2", "Internal communication", [
                    "Internal communication policies defined",
                    "Communication channels established"
                ])
            ]),
            ("CC3", "Security", "Risk Assessment", [
                ("CC3.1", "Specifies suitable objectives", [
                    "Objectives clearly defined",
                    "Risk tolerance established"
                ]),
                ("CC3.2", "Identifies and analyzes risks", [
                    "Risk identification process exists",
                    "Risk analysis performed regularly"
                ])
            ]),
            ("CC6", "Security", "Logical and Physical Access", [
                ("CC6.1", "Logical access security", [
                    "Logical access policies defined",
                    "Access controls implemented"
                ]),
                ("CC6.2", "Authentication mechanisms", [
                    "Strong authentication required",
                    "MFA implemented where appropriate"
                ]),
                ("CC6.3", "Access removal procedures", [
                    "Termination procedures defined",
                    "Access revoked timely"
                ])
            ]),
            ("CC7", "Security", "System Operations", [
                ("CC7.1", "Vulnerability management", [
                    "Vulnerability scanning implemented",
                    "Patches applied timely"
                ]),
                ("CC7.2", "Incident management", [
                    "Incident response plan exists",
                    "Incidents tracked and resolved"
                ])
            ])
        ]
        
        for category, domain, cat_name, items in soc2_controls:
            for control_id, name, requirements in items:
                control = Control(
                    control_id=f"soc2_{control_id.lower()}",
                    name=f"{control_id}: {name}",
                    framework=ComplianceFramework.SOC2,
                    category=cat_name,
                    domain=domain,
                    description=name,
                    requirements=requirements
                )
                controls.append(control)
                self.controls[control.control_id] = control
                
        return controls
        
    def _load_iso27001(self) -> List[Control]:
        """Загрузка ISO27001 контролей"""
        controls = []
        
        iso_controls = [
            ("A.5", "Information Security Policies", [
                ("A.5.1.1", "Policies for information security"),
                ("A.5.1.2", "Review of policies")
            ]),
            ("A.6", "Organization of Information Security", [
                ("A.6.1.1", "Information security roles"),
                ("A.6.1.2", "Segregation of duties")
            ]),
            ("A.7", "Human Resource Security", [
                ("A.7.1.1", "Screening"),
                ("A.7.2.2", "Information security awareness")
            ]),
            ("A.8", "Asset Management", [
                ("A.8.1.1", "Inventory of assets"),
                ("A.8.2.1", "Classification of information")
            ]),
            ("A.9", "Access Control", [
                ("A.9.1.1", "Access control policy"),
                ("A.9.2.1", "User registration and de-registration"),
                ("A.9.4.1", "Information access restriction")
            ]),
            ("A.12", "Operations Security", [
                ("A.12.2.1", "Controls against malware"),
                ("A.12.4.1", "Event logging"),
                ("A.12.6.1", "Management of technical vulnerabilities")
            ]),
            ("A.13", "Communications Security", [
                ("A.13.1.1", "Network controls"),
                ("A.13.2.1", "Information transfer policies")
            ])
        ]
        
        for domain, domain_name, items in iso_controls:
            for control_id, name in items:
                control = Control(
                    control_id=f"iso_{control_id.lower().replace('.', '_')}",
                    name=f"{control_id}: {name}",
                    framework=ComplianceFramework.ISO27001,
                    category=domain,
                    domain=domain_name,
                    description=name
                )
                controls.append(control)
                self.controls[control.control_id] = control
                
        return controls
        
    def _load_gdpr(self) -> List[Control]:
        """Загрузка GDPR контролей"""
        controls = []
        
        gdpr_articles = [
            ("Article 5", "Data Processing Principles", [
                ("5.1.a", "Lawfulness, fairness, transparency"),
                ("5.1.b", "Purpose limitation"),
                ("5.1.c", "Data minimization"),
                ("5.1.d", "Accuracy"),
                ("5.1.e", "Storage limitation"),
                ("5.1.f", "Integrity and confidentiality")
            ]),
            ("Article 6", "Lawfulness of Processing", [
                ("6.1", "Lawful basis for processing")
            ]),
            ("Article 7", "Consent", [
                ("7.1", "Demonstrating consent"),
                ("7.3", "Right to withdraw consent")
            ]),
            ("Article 13-14", "Information to Data Subject", [
                ("13", "Information provision at collection"),
                ("14", "Information when data not from subject")
            ]),
            ("Article 17", "Right to Erasure", [
                ("17.1", "Right to be forgotten")
            ]),
            ("Article 32", "Security of Processing", [
                ("32.1", "Appropriate technical measures"),
                ("32.2", "Risk assessment for processing")
            ]),
            ("Article 33-34", "Breach Notification", [
                ("33", "Notification to supervisory authority"),
                ("34", "Communication to data subject")
            ])
        ]
        
        for article, name, items in gdpr_articles:
            for control_id, desc in items:
                control = Control(
                    control_id=f"gdpr_{control_id.lower().replace('.', '_')}",
                    name=f"GDPR {control_id}: {desc}",
                    framework=ComplianceFramework.GDPR,
                    category=article,
                    domain=name,
                    description=desc
                )
                controls.append(control)
                self.controls[control.control_id] = control
                
        return controls
        
    def _load_pci_dss(self) -> List[Control]:
        """Загрузка PCI-DSS контролей"""
        controls = []
        
        pci_requirements = [
            ("Req 1", "Firewall Configuration", ["1.1", "1.2", "1.3"]),
            ("Req 2", "Default Passwords", ["2.1", "2.2", "2.3"]),
            ("Req 3", "Protect Cardholder Data", ["3.1", "3.2", "3.4"]),
            ("Req 4", "Encryption Transmission", ["4.1", "4.2"]),
            ("Req 6", "Secure Systems", ["6.1", "6.2", "6.5"]),
            ("Req 7", "Access Control", ["7.1", "7.2"]),
            ("Req 8", "Authentication", ["8.1", "8.2", "8.3"]),
            ("Req 10", "Logging", ["10.1", "10.2", "10.5"]),
            ("Req 11", "Security Testing", ["11.1", "11.2", "11.3"]),
            ("Req 12", "Security Policy", ["12.1", "12.10"])
        ]
        
        for req, name, controls_list in pci_requirements:
            for ctrl in controls_list:
                control = Control(
                    control_id=f"pci_{ctrl.replace('.', '_')}",
                    name=f"PCI-DSS {ctrl}",
                    framework=ComplianceFramework.PCI_DSS,
                    category=req,
                    domain=name
                )
                controls.append(control)
                self.controls[control.control_id] = control
                
        return controls
        
    def _load_cis(self) -> List[Control]:
        """Загрузка CIS контролей"""
        controls = []
        
        cis_controls = [
            ("CIS 1", "Inventory of Assets", ["1.1", "1.2", "1.3"]),
            ("CIS 2", "Software Inventory", ["2.1", "2.2"]),
            ("CIS 3", "Data Protection", ["3.1", "3.2", "3.4"]),
            ("CIS 4", "Secure Configuration", ["4.1", "4.2"]),
            ("CIS 5", "Account Management", ["5.1", "5.2", "5.3"]),
            ("CIS 6", "Access Control", ["6.1", "6.2"]),
            ("CIS 7", "Vulnerability Management", ["7.1", "7.2", "7.3"]),
            ("CIS 8", "Audit Log Management", ["8.1", "8.2"]),
            ("CIS 10", "Malware Defenses", ["10.1", "10.2"]),
            ("CIS 11", "Data Recovery", ["11.1", "11.2"])
        ]
        
        for cis, name, controls_list in cis_controls:
            for ctrl in controls_list:
                control = Control(
                    control_id=f"cis_{ctrl.replace('.', '_')}",
                    name=f"CIS {ctrl}: {name}",
                    framework=ComplianceFramework.CIS,
                    category=cis,
                    domain=name
                )
                controls.append(control)
                self.controls[control.control_id] = control
                
        return controls


class AssessmentEngine:
    """Движок оценки"""
    
    def __init__(self, framework_manager: FrameworkManager):
        self.framework_manager = framework_manager
        self.assessments: Dict[str, Assessment] = {}
        self.evidence: Dict[str, Evidence] = {}
        self.findings: Dict[str, Finding] = {}
        
    def create_assessment(self, name: str, framework: ComplianceFramework,
                          **kwargs) -> Assessment:
        """Создание оценки"""
        assessment = Assessment(
            assessment_id=f"assess_{uuid.uuid4().hex[:8]}",
            name=name,
            framework=framework,
            **kwargs
        )
        
        # Загружаем контроли фреймворка
        controls = self.framework_manager.load_framework(framework)
        
        for control in controls:
            assessment.control_results[control.control_id] = ControlStatus.NOT_ASSESSED
            
        self.assessments[assessment.assessment_id] = assessment
        return assessment
        
    def assess_control(self, assessment_id: str, control_id: str,
                       status: ControlStatus, assessor: str = "") -> bool:
        """Оценка контроля"""
        assessment = self.assessments.get(assessment_id)
        control = self.framework_manager.controls.get(control_id)
        
        if not assessment or not control:
            return False
            
        assessment.control_results[control_id] = status
        control.status = status
        control.assessed_at = datetime.now()
        control.assessor = assessor
        
        # Обновляем score
        self._update_score(assessment)
        
        return True
        
    def _update_score(self, assessment: Assessment):
        """Обновление оценки соответствия"""
        total = len(assessment.control_results)
        if total == 0:
            return
            
        compliant = 0
        partial = 0
        
        for status in assessment.control_results.values():
            if status == ControlStatus.COMPLIANT:
                compliant += 1
            elif status == ControlStatus.PARTIALLY_COMPLIANT:
                partial += 0.5
            elif status == ControlStatus.NOT_APPLICABLE:
                total -= 1
                
        if total > 0:
            assessment.compliance_score = (compliant + partial) / total * 100
            
    def add_evidence(self, control_ids: List[str], evidence_type: EvidenceType,
                     title: str, **kwargs) -> Evidence:
        """Добавление доказательства"""
        evidence = Evidence(
            evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
            evidence_type=evidence_type,
            title=title,
            control_ids=control_ids,
            **kwargs
        )
        
        self.evidence[evidence.evidence_id] = evidence
        return evidence
        
    def add_finding(self, control_id: str, title: str,
                    risk_level: RiskLevel, **kwargs) -> Finding:
        """Добавление находки"""
        finding = Finding(
            finding_id=f"find_{uuid.uuid4().hex[:8]}",
            control_id=control_id,
            title=title,
            risk_level=risk_level,
            **kwargs
        )
        
        self.findings[finding.finding_id] = finding
        return finding


class ReportGenerator:
    """Генератор отчётов"""
    
    def generate(self, assessment: Assessment,
                 findings: List[Finding]) -> ComplianceReport:
        """Генерация отчёта"""
        compliant = 0
        non_compliant = 0
        partial = 0
        na = 0
        
        for status in assessment.control_results.values():
            if status == ControlStatus.COMPLIANT:
                compliant += 1
            elif status == ControlStatus.NON_COMPLIANT:
                non_compliant += 1
            elif status == ControlStatus.PARTIALLY_COMPLIANT:
                partial += 1
            elif status == ControlStatus.NOT_APPLICABLE:
                na += 1
                
        findings_by_risk = defaultdict(int)
        for finding in findings:
            findings_by_risk[finding.risk_level.value] += 1
            
        total = len(assessment.control_results) - na
        
        return ComplianceReport(
            report_id=f"rep_{uuid.uuid4().hex[:8]}",
            assessment_id=assessment.assessment_id,
            framework=assessment.framework,
            compliance_score=assessment.compliance_score,
            total_controls=total,
            compliant_controls=compliant,
            non_compliant_controls=non_compliant,
            findings_by_risk=dict(findings_by_risk),
            summary=f"Assessment of {assessment.framework.value} with {compliant}/{total} compliant controls",
            recommendations=[
                "Address critical findings immediately",
                "Review partially compliant controls",
                "Update evidence documentation",
                "Schedule follow-up assessment"
            ]
        )


class ComplianceManagementPlatform:
    """Платформа управления соответствием"""
    
    def __init__(self):
        self.framework_manager = FrameworkManager()
        self.assessment_engine = AssessmentEngine(self.framework_manager)
        self.report_generator = ReportGenerator()
        
        self.reports: Dict[str, ComplianceReport] = {}
        
    def create_assessment(self, name: str, framework: ComplianceFramework,
                          **kwargs) -> Assessment:
        """Создание оценки"""
        return self.assessment_engine.create_assessment(name, framework, **kwargs)
        
    def assess_control(self, assessment_id: str, control_id: str,
                       status: ControlStatus, assessor: str = "") -> bool:
        """Оценка контроля"""
        return self.assessment_engine.assess_control(
            assessment_id, control_id, status, assessor
        )
        
    def add_evidence(self, control_ids: List[str], evidence_type: EvidenceType,
                     title: str, **kwargs) -> Evidence:
        """Добавление доказательства"""
        return self.assessment_engine.add_evidence(
            control_ids, evidence_type, title, **kwargs
        )
        
    def add_finding(self, control_id: str, title: str,
                    risk_level: RiskLevel, **kwargs) -> Finding:
        """Добавление находки"""
        return self.assessment_engine.add_finding(
            control_id, title, risk_level, **kwargs
        )
        
    def generate_report(self, assessment_id: str) -> Optional[ComplianceReport]:
        """Генерация отчёта"""
        assessment = self.assessment_engine.assessments.get(assessment_id)
        if not assessment:
            return None
            
        findings = list(self.assessment_engine.findings.values())
        report = self.report_generator.generate(assessment, findings)
        
        self.reports[report.report_id] = report
        return report
        
    def get_gap_analysis(self, assessment_id: str) -> Dict[str, Any]:
        """Анализ пробелов"""
        assessment = self.assessment_engine.assessments.get(assessment_id)
        if not assessment:
            return {}
            
        gaps = []
        
        for control_id, status in assessment.control_results.items():
            if status in [ControlStatus.NON_COMPLIANT, ControlStatus.PARTIALLY_COMPLIANT]:
                control = self.framework_manager.controls.get(control_id)
                if control:
                    gaps.append({
                        "control_id": control_id,
                        "name": control.name,
                        "status": status.value,
                        "category": control.category,
                        "requirements": control.requirements
                    })
                    
        return {
            "total_gaps": len(gaps),
            "gaps": gaps,
            "by_status": {
                "non_compliant": len([g for g in gaps if g["status"] == "non_compliant"]),
                "partially_compliant": len([g for g in gaps if g["status"] == "partially_compliant"])
            }
        }
        
    def get_risk_summary(self) -> Dict[str, Any]:
        """Сводка по рискам"""
        findings = self.assessment_engine.findings
        
        by_risk = defaultdict(list)
        for finding in findings.values():
            by_risk[finding.risk_level.value].append(finding)
            
        open_findings = [f for f in findings.values() if f.status == "open"]
        
        return {
            "total_findings": len(findings),
            "open_findings": len(open_findings),
            "by_risk_level": {k: len(v) for k, v in by_risk.items()},
            "critical_count": len(by_risk.get("critical", [])),
            "high_count": len(by_risk.get("high", []))
        }
        
    def get_stats(self) -> Dict[str, Any]:
        """Статистика платформы"""
        return {
            "controls": len(self.framework_manager.controls),
            "assessments": len(self.assessment_engine.assessments),
            "evidence": len(self.assessment_engine.evidence),
            "findings": len(self.assessment_engine.findings),
            "reports": len(self.reports)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 72: Compliance Management Platform")
    print("=" * 60)
    
    async def demo():
        platform = ComplianceManagementPlatform()
        print("✓ Compliance Management Platform created")
        
        # Создание оценки SOC2
        print("\n📋 Creating SOC2 Assessment...")
        
        soc2_assessment = platform.create_assessment(
            name="SOC2 Type II Assessment 2024",
            framework=ComplianceFramework.SOC2,
            assessor="John Auditor"
        )
        print(f"  ✓ Assessment: {soc2_assessment.name}")
        print(f"    Controls to assess: {len(soc2_assessment.control_results)}")
        
        # Оценка контролей
        print("\n🔍 Assessing Controls...")
        
        controls = list(soc2_assessment.control_results.keys())
        statuses = [
            ControlStatus.COMPLIANT, ControlStatus.COMPLIANT, 
            ControlStatus.COMPLIANT, ControlStatus.PARTIALLY_COMPLIANT,
            ControlStatus.NON_COMPLIANT
        ]
        
        for i, control_id in enumerate(controls[:10]):
            status = statuses[i % len(statuses)]
            platform.assess_control(
                soc2_assessment.assessment_id,
                control_id,
                status,
                "John Auditor"
            )
            
        print(f"  Assessed 10 controls")
        print(f"  Current compliance score: {soc2_assessment.compliance_score:.1f}%")
        
        # Добавление доказательств
        print("\n📎 Adding Evidence...")
        
        evidence1 = platform.add_evidence(
            control_ids=[controls[0], controls[1]],
            evidence_type=EvidenceType.DOCUMENT,
            title="Information Security Policy v2.0",
            description="Company-wide information security policy document",
            content="/docs/security-policy.pdf"
        )
        print(f"  ✓ Evidence: {evidence1.title}")
        
        evidence2 = platform.add_evidence(
            control_ids=[controls[2], controls[3]],
            evidence_type=EvidenceType.AUTOMATED_SCAN,
            title="Vulnerability Scan Report",
            description="Weekly vulnerability scan results",
            content="/scans/vuln-scan-2024-01.html"
        )
        print(f"  ✓ Evidence: {evidence2.title}")
        
        evidence3 = platform.add_evidence(
            control_ids=[controls[4]],
            evidence_type=EvidenceType.SCREENSHOT,
            title="Access Control Configuration",
            description="Screenshot of IAM configuration",
            content="/screenshots/iam-config.png"
        )
        print(f"  ✓ Evidence: {evidence3.title}")
        
        # Добавление находок
        print("\n⚠️ Recording Findings...")
        
        finding1 = platform.add_finding(
            control_id=controls[4],
            title="Missing MFA for privileged accounts",
            risk_level=RiskLevel.HIGH,
            description="Several admin accounts do not have MFA enabled",
            remediation="Enable MFA for all privileged accounts",
            due_date=datetime.now() + timedelta(days=30),
            owner="Security Team"
        )
        print(f"  ✓ Finding: {finding1.title} (Risk: {finding1.risk_level.value})")
        
        finding2 = platform.add_finding(
            control_id=controls[3],
            title="Incomplete access review documentation",
            risk_level=RiskLevel.MEDIUM,
            description="Access reviews are performed but not fully documented",
            remediation="Implement formal access review documentation process",
            due_date=datetime.now() + timedelta(days=60),
            owner="IT Operations"
        )
        print(f"  ✓ Finding: {finding2.title} (Risk: {finding2.risk_level.value})")
        
        finding3 = platform.add_finding(
            control_id=controls[2],
            title="Outdated security awareness training",
            risk_level=RiskLevel.LOW,
            description="Security awareness training content is 18 months old",
            remediation="Update and refresh training materials",
            due_date=datetime.now() + timedelta(days=90),
            owner="HR"
        )
        print(f"  ✓ Finding: {finding3.title} (Risk: {finding3.risk_level.value})")
        
        # Gap Analysis
        print("\n📊 Gap Analysis:")
        gap_analysis = platform.get_gap_analysis(soc2_assessment.assessment_id)
        print(f"  Total gaps: {gap_analysis['total_gaps']}")
        print(f"  Non-compliant: {gap_analysis['by_status']['non_compliant']}")
        print(f"  Partially compliant: {gap_analysis['by_status']['partially_compliant']}")
        
        if gap_analysis['gaps']:
            print("  Gap details:")
            for gap in gap_analysis['gaps'][:3]:
                print(f"    - {gap['name']}: {gap['status']}")
                
        # Risk Summary
        print("\n🎯 Risk Summary:")
        risk_summary = platform.get_risk_summary()
        print(f"  Total findings: {risk_summary['total_findings']}")
        print(f"  Open findings: {risk_summary['open_findings']}")
        print(f"  By risk level: {risk_summary['by_risk_level']}")
        
        # Генерация отчёта
        print("\n📄 Generating Compliance Report...")
        
        report = platform.generate_report(soc2_assessment.assessment_id)
        
        if report:
            print(f"  Report ID: {report.report_id}")
            print(f"  Framework: {report.framework.value}")
            print(f"  Compliance Score: {report.compliance_score:.1f}%")
            print(f"  Total Controls: {report.total_controls}")
            print(f"  Compliant: {report.compliant_controls}")
            print(f"  Non-Compliant: {report.non_compliant_controls}")
            print(f"  Findings by Risk: {report.findings_by_risk}")
            
            print("\n  Recommendations:")
            for rec in report.recommendations[:3]:
                print(f"    - {rec}")
                
        # Создание оценок для других фреймворков
        print("\n📋 Loading Other Frameworks...")
        
        for framework in [ComplianceFramework.ISO27001, ComplianceFramework.GDPR, ComplianceFramework.PCI_DSS]:
            assessment = platform.create_assessment(
                name=f"{framework.value.upper()} Assessment",
                framework=framework
            )
            print(f"  ✓ {framework.value}: {len(assessment.control_results)} controls")
            
        # Статистика платформы
        print("\n📊 Platform Statistics:")
        stats = platform.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Compliance Management Platform initialized!")
    print("=" * 60)
