#!/usr/bin/env python3
"""
Server Init - Iteration 171: Compliance Automation Platform
Платформа автоматизации compliance

Функционал:
- Policy Management - управление политиками
- Compliance Scanning - сканирование соответствия
- Audit Trail - аудиторский след
- Remediation Actions - действия по исправлению
- Report Generation - генерация отчётов
- Framework Support - поддержка фреймворков (SOC2, HIPAA, PCI-DSS)
- Continuous Monitoring - непрерывный мониторинг
- Evidence Collection - сбор доказательств
"""

import asyncio
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid
from collections import defaultdict
import json


class ComplianceFramework(Enum):
    """Фреймворк compliance"""
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
    NOT_ASSESSED = "not_assessed"


class Severity(Enum):
    """Серьёзность"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ResourceType(Enum):
    """Тип ресурса"""
    SERVER = "server"
    DATABASE = "database"
    STORAGE = "storage"
    NETWORK = "network"
    APPLICATION = "application"
    IDENTITY = "identity"
    ENCRYPTION = "encryption"
    LOGGING = "logging"


class RemediationStatus(Enum):
    """Статус исправления"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ComplianceControl:
    """Контроль compliance"""
    control_id: str
    name: str = ""
    description: str = ""
    
    # Framework
    framework: ComplianceFramework = ComplianceFramework.CUSTOM
    framework_ref: str = ""  # e.g., SOC2-CC6.1, PCI-DSS-3.4
    
    # Category
    category: str = ""  # Access Control, Encryption, Logging, etc.
    subcategory: str = ""
    
    # Requirements
    requirements: List[str] = field(default_factory=list)
    
    # Assessment
    check_type: str = ""  # automated, manual
    check_query: str = ""  # Query or script to run
    
    # Severity
    severity: Severity = Severity.MEDIUM
    
    # Status
    status: ControlStatus = ControlStatus.NOT_ASSESSED
    
    # Evidence
    evidence_required: List[str] = field(default_factory=list)


@dataclass
class CompliancePolicy:
    """Политика compliance"""
    policy_id: str
    name: str = ""
    description: str = ""
    
    # Framework association
    frameworks: List[ComplianceFramework] = field(default_factory=list)
    
    # Controls
    controls: List[ComplianceControl] = field(default_factory=list)
    
    # Scope
    resource_types: List[ResourceType] = field(default_factory=list)
    tags_filter: Dict[str, str] = field(default_factory=dict)
    
    # Schedule
    scan_schedule: str = ""  # cron format
    last_scan: Optional[datetime] = None
    
    # Status
    enabled: bool = True
    
    # Metadata
    owner: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ScanResult:
    """Результат сканирования"""
    result_id: str
    control_id: str = ""
    control_name: str = ""
    
    # Status
    status: ControlStatus = ControlStatus.NOT_ASSESSED
    
    # Resource
    resource_id: str = ""
    resource_type: ResourceType = ResourceType.SERVER
    resource_name: str = ""
    
    # Details
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Severity
    severity: Severity = Severity.INFO
    
    # Evidence
    evidence: List[str] = field(default_factory=list)
    
    # Timing
    scanned_at: datetime = field(default_factory=datetime.now)


@dataclass
class Finding:
    """Находка (нарушение)"""
    finding_id: str
    control_id: str = ""
    control_name: str = ""
    
    # Framework
    framework: ComplianceFramework = ComplianceFramework.CUSTOM
    framework_ref: str = ""
    
    # Resource
    resource_id: str = ""
    resource_type: ResourceType = ResourceType.SERVER
    resource_name: str = ""
    
    # Details
    title: str = ""
    description: str = ""
    severity: Severity = Severity.MEDIUM
    
    # Impact
    impact: str = ""
    
    # Remediation
    remediation_steps: List[str] = field(default_factory=list)
    remediation_status: RemediationStatus = RemediationStatus.PENDING
    remediation_due: Optional[datetime] = None
    
    # Assignment
    assigned_to: str = ""
    
    # Timestamps
    found_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    
    # Evidence
    evidence: List[str] = field(default_factory=list)


@dataclass
class Evidence:
    """Доказательство"""
    evidence_id: str
    control_id: str = ""
    
    # Type
    evidence_type: str = ""  # screenshot, log, config, report
    
    # Content
    title: str = ""
    description: str = ""
    content: str = ""  # Base64 or text
    
    # Source
    source: str = ""
    collected_at: datetime = field(default_factory=datetime.now)
    
    # Validity
    valid_until: Optional[datetime] = None
    
    # Hash for integrity
    content_hash: str = ""


@dataclass
class ComplianceReport:
    """Отчёт compliance"""
    report_id: str
    title: str = ""
    
    # Scope
    frameworks: List[ComplianceFramework] = field(default_factory=list)
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Summary
    total_controls: int = 0
    compliant_controls: int = 0
    non_compliant_controls: int = 0
    not_applicable_controls: int = 0
    
    # Score
    compliance_score: float = 0.0
    
    # Findings
    total_findings: int = 0
    critical_findings: int = 0
    high_findings: int = 0
    
    # Details
    sections: List[Dict] = field(default_factory=list)
    
    # Metadata
    generated_at: datetime = field(default_factory=datetime.now)
    generated_by: str = ""


class ControlLibrary:
    """Библиотека контролей"""
    
    def __init__(self):
        self.controls: Dict[str, ComplianceControl] = {}
        self._load_standard_controls()
        
    def _load_standard_controls(self):
        """Загрузка стандартных контролей"""
        # SOC2 Controls
        soc2_controls = [
            ComplianceControl(
                control_id="soc2_cc6_1",
                name="Logical Access Controls",
                description="Restrict logical access to system components",
                framework=ComplianceFramework.SOC2,
                framework_ref="CC6.1",
                category="Access Control",
                severity=Severity.HIGH,
                requirements=[
                    "Implement role-based access control",
                    "Enforce least privilege principle",
                    "Regular access reviews"
                ],
                evidence_required=["access_policy", "user_list", "role_assignments"]
            ),
            ComplianceControl(
                control_id="soc2_cc6_6",
                name="Encryption of Data",
                description="Protect data using encryption",
                framework=ComplianceFramework.SOC2,
                framework_ref="CC6.6",
                category="Encryption",
                severity=Severity.HIGH,
                requirements=[
                    "Encrypt data at rest",
                    "Encrypt data in transit",
                    "Secure key management"
                ],
                evidence_required=["encryption_config", "key_management_policy"]
            ),
            ComplianceControl(
                control_id="soc2_cc7_2",
                name="Security Monitoring",
                description="Monitor system components for security events",
                framework=ComplianceFramework.SOC2,
                framework_ref="CC7.2",
                category="Monitoring",
                severity=Severity.MEDIUM,
                requirements=[
                    "Implement security monitoring",
                    "Configure alerts for security events",
                    "Regular log review"
                ],
                evidence_required=["monitoring_config", "alert_rules", "log_samples"]
            ),
        ]
        
        # PCI-DSS Controls
        pci_controls = [
            ComplianceControl(
                control_id="pci_3_4",
                name="Encrypt Stored Cardholder Data",
                description="Render PAN unreadable anywhere it is stored",
                framework=ComplianceFramework.PCI_DSS,
                framework_ref="3.4",
                category="Data Protection",
                severity=Severity.CRITICAL,
                requirements=[
                    "One-way hashes based on strong cryptography",
                    "Truncation",
                    "Index tokens and pads",
                    "Strong cryptography with key-management"
                ],
                evidence_required=["encryption_method", "key_procedures"]
            ),
            ComplianceControl(
                control_id="pci_8_2",
                name="Unique User Identification",
                description="Assign unique ID to each person with computer access",
                framework=ComplianceFramework.PCI_DSS,
                framework_ref="8.2",
                category="Access Control",
                severity=Severity.HIGH,
                requirements=[
                    "Unique user IDs",
                    "Proper user authentication",
                    "No shared accounts"
                ],
                evidence_required=["user_accounts", "authentication_policy"]
            ),
        ]
        
        # HIPAA Controls
        hipaa_controls = [
            ComplianceControl(
                control_id="hipaa_164_312_a",
                name="Access Control",
                description="Implement technical policies for access to ePHI",
                framework=ComplianceFramework.HIPAA,
                framework_ref="164.312(a)",
                category="Access Control",
                severity=Severity.CRITICAL,
                requirements=[
                    "Unique user identification",
                    "Emergency access procedure",
                    "Automatic logoff",
                    "Encryption and decryption"
                ],
                evidence_required=["access_controls", "emergency_procedures"]
            ),
            ComplianceControl(
                control_id="hipaa_164_312_b",
                name="Audit Controls",
                description="Implement hardware/software to record and examine activity",
                framework=ComplianceFramework.HIPAA,
                framework_ref="164.312(b)",
                category="Audit",
                severity=Severity.HIGH,
                requirements=[
                    "Record access to ePHI",
                    "Monitor system activity",
                    "Audit log retention"
                ],
                evidence_required=["audit_logs", "monitoring_config"]
            ),
        ]
        
        for control in soc2_controls + pci_controls + hipaa_controls:
            self.controls[control.control_id] = control
            
    def get_controls_by_framework(self, framework: ComplianceFramework) -> List[ComplianceControl]:
        """Получение контролей по фреймворку"""
        return [c for c in self.controls.values() if c.framework == framework]
        
    def get_controls_by_category(self, category: str) -> List[ComplianceControl]:
        """Получение контролей по категории"""
        return [c for c in self.controls.values() if c.category == category]


class ComplianceScanner:
    """Сканер compliance"""
    
    def __init__(self, control_library: ControlLibrary):
        self.library = control_library
        self.checkers: Dict[str, Callable] = {}
        self._register_default_checkers()
        
    def _register_default_checkers(self):
        """Регистрация проверок по умолчанию"""
        # Access control checker
        async def check_access_control(resource: Dict) -> ScanResult:
            has_rbac = resource.get("rbac_enabled", False)
            has_mfa = resource.get("mfa_enabled", False)
            
            if has_rbac and has_mfa:
                status = ControlStatus.COMPLIANT
            elif has_rbac or has_mfa:
                status = ControlStatus.PARTIALLY_COMPLIANT
            else:
                status = ControlStatus.NON_COMPLIANT
                
            return ScanResult(
                result_id=f"res_{uuid.uuid4().hex[:8]}",
                status=status,
                message=f"RBAC: {has_rbac}, MFA: {has_mfa}"
            )
            
        self.checkers["access_control"] = check_access_control
        
        # Encryption checker
        async def check_encryption(resource: Dict) -> ScanResult:
            encrypted_at_rest = resource.get("encryption_at_rest", False)
            encrypted_in_transit = resource.get("encryption_in_transit", False)
            
            if encrypted_at_rest and encrypted_in_transit:
                status = ControlStatus.COMPLIANT
            elif encrypted_at_rest or encrypted_in_transit:
                status = ControlStatus.PARTIALLY_COMPLIANT
            else:
                status = ControlStatus.NON_COMPLIANT
                
            return ScanResult(
                result_id=f"res_{uuid.uuid4().hex[:8]}",
                status=status,
                message=f"At rest: {encrypted_at_rest}, In transit: {encrypted_in_transit}"
            )
            
        self.checkers["encryption"] = check_encryption
        
        # Logging checker
        async def check_logging(resource: Dict) -> ScanResult:
            logging_enabled = resource.get("logging_enabled", False)
            log_retention = resource.get("log_retention_days", 0)
            
            if logging_enabled and log_retention >= 90:
                status = ControlStatus.COMPLIANT
            elif logging_enabled:
                status = ControlStatus.PARTIALLY_COMPLIANT
            else:
                status = ControlStatus.NON_COMPLIANT
                
            return ScanResult(
                result_id=f"res_{uuid.uuid4().hex[:8]}",
                status=status,
                message=f"Logging: {logging_enabled}, Retention: {log_retention} days"
            )
            
        self.checkers["logging"] = check_logging
        
    async def scan_resource(self, resource: Dict, controls: List[ComplianceControl]) -> List[ScanResult]:
        """Сканирование ресурса"""
        results = []
        
        for control in controls:
            checker_key = control.category.lower().replace(" ", "_")
            
            if checker_key in self.checkers:
                result = await self.checkers[checker_key](resource)
                result.control_id = control.control_id
                result.control_name = control.name
                result.resource_id = resource.get("id", "")
                result.resource_name = resource.get("name", "")
                result.severity = control.severity
                results.append(result)
            else:
                # Manual check required
                result = ScanResult(
                    result_id=f"res_{uuid.uuid4().hex[:8]}",
                    control_id=control.control_id,
                    control_name=control.name,
                    status=ControlStatus.NOT_ASSESSED,
                    message="Manual assessment required"
                )
                results.append(result)
                
        return results


class FindingsManager:
    """Менеджер находок"""
    
    def __init__(self):
        self.findings: Dict[str, Finding] = {}
        
    def create_finding(self, result: ScanResult, control: ComplianceControl) -> Finding:
        """Создание находки"""
        # Calculate due date based on severity
        due_days = {
            Severity.CRITICAL: 7,
            Severity.HIGH: 14,
            Severity.MEDIUM: 30,
            Severity.LOW: 90,
            Severity.INFO: 180
        }
        
        finding = Finding(
            finding_id=f"find_{uuid.uuid4().hex[:8]}",
            control_id=control.control_id,
            control_name=control.name,
            framework=control.framework,
            framework_ref=control.framework_ref,
            resource_id=result.resource_id,
            resource_name=result.resource_name,
            title=f"Non-compliance: {control.name}",
            description=result.message,
            severity=control.severity,
            remediation_steps=control.requirements,
            remediation_due=datetime.now() + timedelta(days=due_days.get(control.severity, 30))
        )
        
        self.findings[finding.finding_id] = finding
        return finding
        
    def update_status(self, finding_id: str, status: RemediationStatus):
        """Обновление статуса"""
        if finding_id in self.findings:
            self.findings[finding_id].remediation_status = status
            if status == RemediationStatus.COMPLETED:
                self.findings[finding_id].resolved_at = datetime.now()
                
    def get_open_findings(self) -> List[Finding]:
        """Открытые находки"""
        return [f for f in self.findings.values() 
                if f.remediation_status not in [RemediationStatus.COMPLETED, RemediationStatus.SKIPPED]]
                
    def get_overdue_findings(self) -> List[Finding]:
        """Просроченные находки"""
        now = datetime.now()
        return [f for f in self.get_open_findings() 
                if f.remediation_due and f.remediation_due < now]


class ReportGenerator:
    """Генератор отчётов"""
    
    def generate_report(self, scan_results: List[ScanResult], 
                       findings: List[Finding],
                       frameworks: List[ComplianceFramework]) -> ComplianceReport:
        """Генерация отчёта"""
        # Calculate statistics
        total = len(scan_results)
        compliant = len([r for r in scan_results if r.status == ControlStatus.COMPLIANT])
        non_compliant = len([r for r in scan_results if r.status == ControlStatus.NON_COMPLIANT])
        partial = len([r for r in scan_results if r.status == ControlStatus.PARTIALLY_COMPLIANT])
        na = len([r for r in scan_results if r.status == ControlStatus.NOT_APPLICABLE])
        
        # Calculate score
        assessed = total - na
        score = (compliant + partial * 0.5) / assessed * 100 if assessed > 0 else 0
        
        # Count findings by severity
        critical = len([f for f in findings if f.severity == Severity.CRITICAL])
        high = len([f for f in findings if f.severity == Severity.HIGH])
        
        report = ComplianceReport(
            report_id=f"rpt_{uuid.uuid4().hex[:8]}",
            title="Compliance Assessment Report",
            frameworks=frameworks,
            period_end=datetime.now(),
            total_controls=total,
            compliant_controls=compliant,
            non_compliant_controls=non_compliant + partial,
            not_applicable_controls=na,
            compliance_score=round(score, 1),
            total_findings=len(findings),
            critical_findings=critical,
            high_findings=high
        )
        
        # Build sections by framework
        for framework in frameworks:
            fw_results = [r for r in scan_results 
                        if any(c.framework == framework for c in [] )]  # Simplified
            
            section = {
                "framework": framework.value,
                "controls_assessed": len(fw_results),
                "status_summary": {}
            }
            report.sections.append(section)
            
        return report


class ComplianceAutomationPlatform:
    """Платформа автоматизации compliance"""
    
    def __init__(self):
        self.control_library = ControlLibrary()
        self.scanner = ComplianceScanner(self.control_library)
        self.findings_manager = FindingsManager()
        self.report_generator = ReportGenerator()
        
        self.policies: Dict[str, CompliancePolicy] = {}
        self.scan_history: List[Dict] = []
        self.evidence_store: Dict[str, Evidence] = {}
        
    def create_policy(self, name: str, frameworks: List[ComplianceFramework],
                     resource_types: List[ResourceType] = None) -> CompliancePolicy:
        """Создание политики"""
        # Get controls for frameworks
        controls = []
        for fw in frameworks:
            controls.extend(self.control_library.get_controls_by_framework(fw))
            
        policy = CompliancePolicy(
            policy_id=f"pol_{uuid.uuid4().hex[:8]}",
            name=name,
            frameworks=frameworks,
            controls=controls,
            resource_types=resource_types or []
        )
        
        self.policies[policy.policy_id] = policy
        return policy
        
    async def run_scan(self, policy_id: str, resources: List[Dict]) -> Dict:
        """Запуск сканирования"""
        policy = self.policies.get(policy_id)
        if not policy:
            return {"error": "Policy not found"}
            
        all_results = []
        new_findings = []
        
        for resource in resources:
            results = await self.scanner.scan_resource(resource, policy.controls)
            all_results.extend(results)
            
            # Create findings for non-compliant
            for result in results:
                if result.status in [ControlStatus.NON_COMPLIANT, ControlStatus.PARTIALLY_COMPLIANT]:
                    control = next((c for c in policy.controls if c.control_id == result.control_id), None)
                    if control:
                        finding = self.findings_manager.create_finding(result, control)
                        new_findings.append(finding)
                        
        # Update policy
        policy.last_scan = datetime.now()
        
        # Record scan
        scan_record = {
            "scan_id": f"scan_{uuid.uuid4().hex[:8]}",
            "policy_id": policy_id,
            "timestamp": datetime.now(),
            "resources_scanned": len(resources),
            "controls_checked": len(all_results),
            "findings_created": len(new_findings)
        }
        self.scan_history.append(scan_record)
        
        return {
            "scan_id": scan_record["scan_id"],
            "results": all_results,
            "findings": new_findings,
            "summary": {
                "compliant": len([r for r in all_results if r.status == ControlStatus.COMPLIANT]),
                "non_compliant": len([r for r in all_results if r.status == ControlStatus.NON_COMPLIANT]),
                "partial": len([r for r in all_results if r.status == ControlStatus.PARTIALLY_COMPLIANT])
            }
        }
        
    def collect_evidence(self, control_id: str, evidence_type: str, 
                        content: str, title: str) -> Evidence:
        """Сбор доказательств"""
        evidence = Evidence(
            evidence_id=f"evd_{uuid.uuid4().hex[:8]}",
            control_id=control_id,
            evidence_type=evidence_type,
            title=title,
            content=content,
            content_hash=hashlib.sha256(content.encode()).hexdigest()
        )
        
        self.evidence_store[evidence.evidence_id] = evidence
        return evidence
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        open_findings = self.findings_manager.get_open_findings()
        overdue = self.findings_manager.get_overdue_findings()
        
        return {
            "total_controls": len(self.control_library.controls),
            "total_policies": len(self.policies),
            "total_scans": len(self.scan_history),
            "open_findings": len(open_findings),
            "overdue_findings": len(overdue),
            "total_evidence": len(self.evidence_store)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 171: Compliance Automation Platform")
    print("=" * 60)
    
    async def demo():
        platform = ComplianceAutomationPlatform()
        print("✓ Compliance Automation Platform created")
        
        # Show available controls
        print("\n📚 Control Library:")
        
        print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────┐")
        print("  │ Framework │ Control ID          │ Name                              │ Severity │")
        print("  ├────────────────────────────────────────────────────────────────────────────────────────────┤")
        
        for control in list(platform.control_library.controls.values())[:8]:
            fw = control.framework.value[:9].ljust(9)
            cid = control.control_id[:19].ljust(19)
            name = control.name[:33].ljust(33)
            sev = control.severity.value[:8].ljust(8)
            print(f"  │ {fw} │ {cid} │ {name} │ {sev} │")
            
        print("  └────────────────────────────────────────────────────────────────────────────────────────────┘")
        
        # Create compliance policy
        print("\n📋 Creating Compliance Policies...")
        
        # SOC2 + HIPAA policy
        healthcare_policy = platform.create_policy(
            name="Healthcare Infrastructure Compliance",
            frameworks=[ComplianceFramework.SOC2, ComplianceFramework.HIPAA],
            resource_types=[ResourceType.SERVER, ResourceType.DATABASE, ResourceType.STORAGE]
        )
        print(f"  ✓ {healthcare_policy.name}")
        print(f"    Frameworks: {[f.value for f in healthcare_policy.frameworks]}")
        print(f"    Controls: {len(healthcare_policy.controls)}")
        
        # PCI-DSS policy
        payment_policy = platform.create_policy(
            name="Payment Systems Compliance",
            frameworks=[ComplianceFramework.PCI_DSS],
            resource_types=[ResourceType.SERVER, ResourceType.DATABASE]
        )
        print(f"  ✓ {payment_policy.name}")
        print(f"    Controls: {len(payment_policy.controls)}")
        
        # Define resources to scan
        print("\n🖥️ Resources to Scan:")
        
        resources = [
            {
                "id": "srv-prod-001",
                "name": "Production Web Server",
                "type": ResourceType.SERVER.value,
                "rbac_enabled": True,
                "mfa_enabled": True,
                "encryption_at_rest": True,
                "encryption_in_transit": True,
                "logging_enabled": True,
                "log_retention_days": 365
            },
            {
                "id": "db-prod-001",
                "name": "Production Database",
                "type": ResourceType.DATABASE.value,
                "rbac_enabled": True,
                "mfa_enabled": False,  # Non-compliant
                "encryption_at_rest": True,
                "encryption_in_transit": True,
                "logging_enabled": True,
                "log_retention_days": 90
            },
            {
                "id": "storage-001",
                "name": "Document Storage",
                "type": ResourceType.STORAGE.value,
                "rbac_enabled": True,
                "mfa_enabled": False,
                "encryption_at_rest": False,  # Non-compliant
                "encryption_in_transit": True,
                "logging_enabled": True,
                "log_retention_days": 30  # Partially compliant
            },
            {
                "id": "srv-dev-001",
                "name": "Development Server",
                "type": ResourceType.SERVER.value,
                "rbac_enabled": False,  # Non-compliant
                "mfa_enabled": False,
                "encryption_at_rest": False,
                "encryption_in_transit": False,
                "logging_enabled": False,
                "log_retention_days": 0
            },
        ]
        
        for res in resources:
            compliance_flags = []
            if res.get("rbac_enabled"):
                compliance_flags.append("RBAC")
            if res.get("mfa_enabled"):
                compliance_flags.append("MFA")
            if res.get("encryption_at_rest"):
                compliance_flags.append("Enc@Rest")
            if res.get("encryption_in_transit"):
                compliance_flags.append("Enc@Transit")
            if res.get("logging_enabled"):
                compliance_flags.append("Logging")
                
            flags_str = ", ".join(compliance_flags) if compliance_flags else "None"
            print(f"  • {res['name']} ({res['id']})")
            print(f"    Features: {flags_str}")
            
        # Run compliance scan
        print("\n🔍 Running Compliance Scan...")
        
        scan_result = await platform.run_scan(healthcare_policy.policy_id, resources)
        
        print(f"\n  Scan ID: {scan_result['scan_id']}")
        print(f"  Resources scanned: {len(resources)}")
        print(f"  Controls checked: {len(scan_result['results'])}")
        
        # Summary
        print("\n📊 Scan Summary:")
        
        summary = scan_result["summary"]
        total = summary["compliant"] + summary["non_compliant"] + summary["partial"]
        
        print(f"\n  ┌───────────────────────────────────────┐")
        print(f"  │ Status               │ Count │ %     │")
        print(f"  ├───────────────────────────────────────┤")
        
        if total > 0:
            compliant_pct = summary["compliant"] / total * 100
            non_compliant_pct = summary["non_compliant"] / total * 100
            partial_pct = summary["partial"] / total * 100
            
            print(f"  │ ✓ Compliant          │ {summary['compliant']:>5} │ {compliant_pct:>4.1f}% │")
            print(f"  │ ✗ Non-Compliant      │ {summary['non_compliant']:>5} │ {non_compliant_pct:>4.1f}% │")
            print(f"  │ ⚠ Partial            │ {summary['partial']:>5} │ {partial_pct:>4.1f}% │")
            
        print(f"  └───────────────────────────────────────┘")
        
        # Detailed results
        print("\n📋 Scan Results by Resource:")
        
        results_by_resource = defaultdict(list)
        for result in scan_result["results"]:
            results_by_resource[result.resource_name].append(result)
            
        for resource_name, results in results_by_resource.items():
            compliant_count = len([r for r in results if r.status == ControlStatus.COMPLIANT])
            total_count = len(results)
            score = compliant_count / total_count * 100 if total_count > 0 else 0
            
            status_icon = "✓" if score == 100 else "⚠" if score >= 50 else "✗"
            print(f"\n  {status_icon} {resource_name} ({score:.0f}% compliant)")
            
            for result in results:
                status_mark = "✓" if result.status == ControlStatus.COMPLIANT else "✗" if result.status == ControlStatus.NON_COMPLIANT else "⚠"
                print(f"    {status_mark} {result.control_name}: {result.message}")
                
        # Findings
        print("\n🚨 Findings (Non-Compliance Issues):")
        
        findings = scan_result["findings"]
        
        if findings:
            print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────┐")
            print("  │ Severity  │ Resource            │ Control                    │ Due Date   │")
            print("  ├────────────────────────────────────────────────────────────────────────────────────────────────┤")
            
            for finding in sorted(findings, key=lambda f: f.severity.value):
                sev = finding.severity.value[:9].ljust(9)
                res = finding.resource_name[:19].ljust(19)
                ctrl = finding.control_name[:26].ljust(26)
                due = finding.remediation_due.strftime("%Y-%m-%d") if finding.remediation_due else "N/A"
                print(f"  │ {sev} │ {res} │ {ctrl} │ {due:>10} │")
                
            print("  └────────────────────────────────────────────────────────────────────────────────────────────────┘")
        else:
            print("  No findings - all controls are compliant!")
            
        # Collect evidence
        print("\n📎 Collecting Evidence...")
        
        evidence1 = platform.collect_evidence(
            control_id="soc2_cc6_1",
            evidence_type="config",
            content='{"rbac_enabled": true, "roles": ["admin", "user", "viewer"]}',
            title="RBAC Configuration Export"
        )
        print(f"  ✓ {evidence1.title} (ID: {evidence1.evidence_id})")
        
        evidence2 = platform.collect_evidence(
            control_id="soc2_cc6_6",
            evidence_type="report",
            content="Encryption audit completed. All production data encrypted with AES-256.",
            title="Encryption Audit Report"
        )
        print(f"  ✓ {evidence2.title} (ID: {evidence2.evidence_id})")
        
        # Generate report
        print("\n📄 Generating Compliance Report...")
        
        report = platform.report_generator.generate_report(
            scan_results=scan_result["results"],
            findings=findings,
            frameworks=[ComplianceFramework.SOC2, ComplianceFramework.HIPAA]
        )
        
        print(f"\n  Report ID: {report.report_id}")
        print(f"  Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n  ┌────────────────────────────────────────┐")
        print(f"  │         COMPLIANCE REPORT              │")
        print(f"  ├────────────────────────────────────────┤")
        print(f"  │ Compliance Score:    {report.compliance_score:>6.1f}%          │")
        print(f"  │ Total Controls:      {report.total_controls:>6}            │")
        print(f"  │ Compliant:           {report.compliant_controls:>6}            │")
        print(f"  │ Non-Compliant:       {report.non_compliant_controls:>6}            │")
        print(f"  ├────────────────────────────────────────┤")
        print(f"  │ Total Findings:      {report.total_findings:>6}            │")
        print(f"  │ Critical Findings:   {report.critical_findings:>6}            │")
        print(f"  │ High Findings:       {report.high_findings:>6}            │")
        print(f"  └────────────────────────────────────────┘")
        
        # Platform statistics
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Controls in Library: {stats['total_controls']}")
        print(f"  Active Policies: {stats['total_policies']}")
        print(f"  Scans Completed: {stats['total_scans']}")
        print(f"  Open Findings: {stats['open_findings']}")
        print(f"  Overdue Findings: {stats['overdue_findings']}")
        print(f"  Evidence Collected: {stats['total_evidence']}")
        
        # Compliance by framework
        print("\n  Controls by Framework:")
        
        fw_counts = defaultdict(int)
        for control in platform.control_library.controls.values():
            fw_counts[control.framework.value] += 1
            
        for fw, count in sorted(fw_counts.items()):
            bar = "█" * count * 2
            print(f"    {fw:10}: {bar} {count}")
            
        # Dashboard
        print("\n┌────────────────────────────────────────────────────────────────────┐")
        print("│                Compliance Automation Dashboard                     │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Compliance Score:            {report.compliance_score:>6.1f}%                       │")
        print(f"│ Controls Assessed:           {report.total_controls:>10}                       │")
        print(f"│ Open Findings:               {stats['open_findings']:>10}                       │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Policies Active:             {stats['total_policies']:>10}                       │")
        print(f"│ Evidence Items:              {stats['total_evidence']:>10}                       │")
        print(f"│ Scans Completed:             {stats['total_scans']:>10}                       │")
        print("└────────────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Compliance Automation Platform initialized!")
    print("=" * 60)
