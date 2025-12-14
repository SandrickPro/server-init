#!/usr/bin/env python3
"""
Server Init - Iteration 129: Security Scanning Platform
Платформа сканирования безопасности

Функционал:
- Vulnerability Scanning - сканирование уязвимостей
- SAST (Static Analysis) - статический анализ
- DAST (Dynamic Analysis) - динамический анализ
- Dependency Scanning - сканирование зависимостей
- Secret Detection - обнаружение секретов
- Container Scanning - сканирование контейнеров
- Compliance Checking - проверка соответствия
- Remediation Tracking - отслеживание исправлений
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
import re


class ScanType(Enum):
    """Тип сканирования"""
    SAST = "sast"
    DAST = "dast"
    SCA = "sca"  # Software Composition Analysis
    SECRET = "secret"
    CONTAINER = "container"
    INFRASTRUCTURE = "infrastructure"


class Severity(Enum):
    """Критичность"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class VulnerabilityStatus(Enum):
    """Статус уязвимости"""
    OPEN = "open"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    FIXED = "fixed"
    FALSE_POSITIVE = "false_positive"
    ACCEPTED_RISK = "accepted_risk"


class ComplianceStandard(Enum):
    """Стандарт соответствия"""
    OWASP_TOP10 = "owasp_top10"
    CIS = "cis"
    PCI_DSS = "pci_dss"
    SOC2 = "soc2"
    HIPAA = "hipaa"
    GDPR = "gdpr"


@dataclass
class Vulnerability:
    """Уязвимость"""
    vuln_id: str
    cve_id: str = ""
    
    # Details
    title: str = ""
    description: str = ""
    
    # Severity
    severity: Severity = Severity.MEDIUM
    cvss_score: float = 0.0
    
    # Location
    file_path: str = ""
    line_number: int = 0
    code_snippet: str = ""
    
    # Package info
    package_name: str = ""
    package_version: str = ""
    fixed_version: str = ""
    
    # Status
    status: VulnerabilityStatus = VulnerabilityStatus.OPEN
    
    # Scan info
    scan_type: ScanType = ScanType.SAST
    scanner: str = ""
    
    # Timestamps
    detected_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


@dataclass
class Secret:
    """Обнаруженный секрет"""
    secret_id: str
    
    # Type
    secret_type: str = ""  # api_key, password, token, etc.
    
    # Location
    file_path: str = ""
    line_number: int = 0
    
    # Details
    masked_value: str = ""
    entropy: float = 0.0
    
    # Status
    status: VulnerabilityStatus = VulnerabilityStatus.OPEN
    
    # Timestamps
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class ScanResult:
    """Результат сканирования"""
    scan_id: str
    scan_type: ScanType = ScanType.SAST
    
    # Target
    target: str = ""
    
    # Results
    vulnerabilities: List[str] = field(default_factory=list)  # Vuln IDs
    
    # Summary
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    info_count: int = 0
    
    # Status
    status: str = "completed"
    duration_seconds: int = 0
    
    # Timestamps
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class ComplianceCheck:
    """Проверка соответствия"""
    check_id: str
    standard: ComplianceStandard = ComplianceStandard.OWASP_TOP10
    
    # Rule
    rule_id: str = ""
    rule_name: str = ""
    
    # Result
    passed: bool = True
    findings: List[str] = field(default_factory=list)
    
    # Details
    description: str = ""
    remediation: str = ""


@dataclass
class ScanPolicy:
    """Политика сканирования"""
    policy_id: str
    name: str = ""
    
    # Scans to run
    scan_types: List[ScanType] = field(default_factory=list)
    
    # Thresholds
    fail_on_critical: bool = True
    fail_on_high: bool = True
    max_critical: int = 0
    max_high: int = 5
    
    # Compliance
    compliance_standards: List[ComplianceStandard] = field(default_factory=list)
    
    # Schedule
    schedule_cron: str = "0 0 * * *"  # Daily


class VulnerabilityScanner:
    """Сканер уязвимостей"""
    
    def __init__(self):
        self.vulnerabilities: Dict[str, Vulnerability] = {}
        self.scans: Dict[str, ScanResult] = {}
        
    async def scan_sast(self, target: str) -> ScanResult:
        """Статический анализ"""
        scan = ScanResult(
            scan_id=f"scan_{uuid.uuid4().hex[:8]}",
            scan_type=ScanType.SAST,
            target=target,
            started_at=datetime.now()
        )
        
        # Simulate SAST findings
        findings = [
            ("SQL Injection", Severity.CRITICAL, "SQL query with user input", "CVE-2024-0001"),
            ("XSS Vulnerability", Severity.HIGH, "Unsanitized user output", "CVE-2024-0002"),
            ("Hardcoded Password", Severity.HIGH, "Password in source code", ""),
            ("Insecure Deserialization", Severity.MEDIUM, "Unsafe object deserialization", "CVE-2024-0003"),
            ("Debug Mode Enabled", Severity.LOW, "Debug flag set to true", "")
        ]
        
        for title, severity, desc, cve in findings:
            if random.random() > 0.3:  # 70% chance to find
                vuln = Vulnerability(
                    vuln_id=f"vuln_{uuid.uuid4().hex[:8]}",
                    cve_id=cve,
                    title=title,
                    description=desc,
                    severity=severity,
                    cvss_score={"critical": 9.5, "high": 7.5, "medium": 5.0, "low": 2.5, "info": 0.0}[severity.value],
                    file_path=f"{target}/src/app.py",
                    line_number=random.randint(10, 500),
                    scan_type=ScanType.SAST,
                    scanner="sast-scanner"
                )
                self.vulnerabilities[vuln.vuln_id] = vuln
                scan.vulnerabilities.append(vuln.vuln_id)
                
        self._update_counts(scan)
        scan.completed_at = datetime.now()
        scan.duration_seconds = 30
        self.scans[scan.scan_id] = scan
        
        return scan
        
    async def scan_dependencies(self, target: str) -> ScanResult:
        """Сканирование зависимостей"""
        scan = ScanResult(
            scan_id=f"scan_{uuid.uuid4().hex[:8]}",
            scan_type=ScanType.SCA,
            target=target,
            started_at=datetime.now()
        )
        
        # Simulate dependency vulnerabilities
        deps = [
            ("lodash", "4.17.15", "4.17.21", Severity.HIGH, "CVE-2020-8203"),
            ("axios", "0.19.0", "0.21.1", Severity.MEDIUM, "CVE-2020-28168"),
            ("minimist", "1.2.0", "1.2.6", Severity.CRITICAL, "CVE-2021-44906"),
            ("node-fetch", "2.6.0", "2.6.7", Severity.HIGH, "CVE-2022-0235"),
            ("tar", "4.4.10", "4.4.19", Severity.HIGH, "CVE-2021-32803")
        ]
        
        for pkg, version, fixed, severity, cve in deps:
            if random.random() > 0.4:
                vuln = Vulnerability(
                    vuln_id=f"vuln_{uuid.uuid4().hex[:8]}",
                    cve_id=cve,
                    title=f"Vulnerable {pkg}",
                    description=f"Package {pkg} has known vulnerability",
                    severity=severity,
                    package_name=pkg,
                    package_version=version,
                    fixed_version=fixed,
                    scan_type=ScanType.SCA,
                    scanner="dependency-scanner"
                )
                self.vulnerabilities[vuln.vuln_id] = vuln
                scan.vulnerabilities.append(vuln.vuln_id)
                
        self._update_counts(scan)
        scan.completed_at = datetime.now()
        scan.duration_seconds = 15
        self.scans[scan.scan_id] = scan
        
        return scan
        
    async def scan_container(self, image: str) -> ScanResult:
        """Сканирование контейнера"""
        scan = ScanResult(
            scan_id=f"scan_{uuid.uuid4().hex[:8]}",
            scan_type=ScanType.CONTAINER,
            target=image,
            started_at=datetime.now()
        )
        
        # Simulate container vulnerabilities
        container_vulns = [
            ("OpenSSL Buffer Overflow", Severity.CRITICAL, "CVE-2022-0778"),
            ("Curl Vulnerability", Severity.HIGH, "CVE-2022-35252"),
            ("Linux Kernel Issue", Severity.MEDIUM, "CVE-2022-0847"),
            ("glibc Vulnerability", Severity.HIGH, "CVE-2021-3999")
        ]
        
        for title, severity, cve in container_vulns:
            if random.random() > 0.5:
                vuln = Vulnerability(
                    vuln_id=f"vuln_{uuid.uuid4().hex[:8]}",
                    cve_id=cve,
                    title=title,
                    severity=severity,
                    scan_type=ScanType.CONTAINER,
                    scanner="container-scanner"
                )
                self.vulnerabilities[vuln.vuln_id] = vuln
                scan.vulnerabilities.append(vuln.vuln_id)
                
        self._update_counts(scan)
        scan.completed_at = datetime.now()
        scan.duration_seconds = 45
        self.scans[scan.scan_id] = scan
        
        return scan
        
    def _update_counts(self, scan: ScanResult):
        """Обновление счётчиков"""
        for vuln_id in scan.vulnerabilities:
            vuln = self.vulnerabilities.get(vuln_id)
            if vuln:
                if vuln.severity == Severity.CRITICAL:
                    scan.critical_count += 1
                elif vuln.severity == Severity.HIGH:
                    scan.high_count += 1
                elif vuln.severity == Severity.MEDIUM:
                    scan.medium_count += 1
                elif vuln.severity == Severity.LOW:
                    scan.low_count += 1
                else:
                    scan.info_count += 1


class SecretScanner:
    """Сканер секретов"""
    
    def __init__(self):
        self.secrets: Dict[str, Secret] = {}
        self.patterns = {
            "api_key": r'["\']?api[_-]?key["\']?\s*[:=]\s*["\']([a-zA-Z0-9]{32,})["\']',
            "aws_key": r'AKIA[0-9A-Z]{16}',
            "private_key": r'-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----',
            "github_token": r'gh[ps]_[a-zA-Z0-9]{36}',
            "password": r'["\']?password["\']?\s*[:=]\s*["\']([^"\']+)["\']'
        }
        
    async def scan(self, target: str) -> List[Secret]:
        """Сканирование секретов"""
        found = []
        
        # Simulate secret findings
        secret_types = ["api_key", "aws_key", "github_token", "password", "private_key"]
        
        for _ in range(random.randint(0, 5)):
            secret_type = random.choice(secret_types)
            secret = Secret(
                secret_id=f"secret_{uuid.uuid4().hex[:8]}",
                secret_type=secret_type,
                file_path=f"{target}/config/secrets.env",
                line_number=random.randint(1, 100),
                masked_value=f"****{uuid.uuid4().hex[:4]}****",
                entropy=random.uniform(4.0, 6.0)
            )
            self.secrets[secret.secret_id] = secret
            found.append(secret)
            
        return found


class ComplianceChecker:
    """Проверка соответствия"""
    
    def __init__(self):
        self.checks: Dict[str, ComplianceCheck] = {}
        
    async def check(self, standard: ComplianceStandard,
                     vulnerabilities: List[Vulnerability]) -> List[ComplianceCheck]:
        """Проверка соответствия"""
        results = []
        
        if standard == ComplianceStandard.OWASP_TOP10:
            rules = [
                ("A01:2021", "Broken Access Control", Severity.CRITICAL),
                ("A02:2021", "Cryptographic Failures", Severity.HIGH),
                ("A03:2021", "Injection", Severity.CRITICAL),
                ("A04:2021", "Insecure Design", Severity.HIGH),
                ("A05:2021", "Security Misconfiguration", Severity.MEDIUM),
                ("A06:2021", "Vulnerable Components", Severity.HIGH),
                ("A07:2021", "Auth Failures", Severity.HIGH),
                ("A08:2021", "Software Integrity Failures", Severity.MEDIUM),
                ("A09:2021", "Logging Failures", Severity.LOW),
                ("A10:2021", "SSRF", Severity.MEDIUM)
            ]
        else:
            rules = [
                ("R01", "Rule 1", Severity.HIGH),
                ("R02", "Rule 2", Severity.MEDIUM),
                ("R03", "Rule 3", Severity.LOW)
            ]
            
        for rule_id, rule_name, min_severity in rules:
            # Check if any vulnerabilities match this rule
            relevant_vulns = [v for v in vulnerabilities 
                            if v.severity.value in ["critical", "high"] 
                            and random.random() > 0.7]
            
            check = ComplianceCheck(
                check_id=f"check_{uuid.uuid4().hex[:8]}",
                standard=standard,
                rule_id=rule_id,
                rule_name=rule_name,
                passed=len(relevant_vulns) == 0,
                findings=[v.vuln_id for v in relevant_vulns]
            )
            self.checks[check.check_id] = check
            results.append(check)
            
        return results


class RemediationTracker:
    """Отслеживание исправлений"""
    
    def __init__(self, vuln_scanner: VulnerabilityScanner):
        self.vuln_scanner = vuln_scanner
        self.remediation_plans: Dict[str, Dict] = {}
        
    def create_plan(self, vuln_id: str, assignee: str = "", due_date: datetime = None) -> Dict:
        """Создание плана исправления"""
        vuln = self.vuln_scanner.vulnerabilities.get(vuln_id)
        if not vuln:
            return {"error": "Vulnerability not found"}
            
        plan = {
            "plan_id": f"plan_{uuid.uuid4().hex[:8]}",
            "vuln_id": vuln_id,
            "title": vuln.title,
            "severity": vuln.severity.value,
            "assignee": assignee,
            "due_date": due_date or (datetime.now() + timedelta(days=7)),
            "status": "open",
            "created_at": datetime.now()
        }
        
        self.remediation_plans[plan["plan_id"]] = plan
        return plan
        
    def update_status(self, vuln_id: str, status: VulnerabilityStatus) -> Dict:
        """Обновление статуса"""
        vuln = self.vuln_scanner.vulnerabilities.get(vuln_id)
        if not vuln:
            return {"error": "Vulnerability not found"}
            
        vuln.status = status
        if status == VulnerabilityStatus.FIXED:
            vuln.resolved_at = datetime.now()
            
        return {"vuln_id": vuln_id, "status": status.value}
        
    def get_summary(self) -> Dict:
        """Сводка по исправлениям"""
        vulns = list(self.vuln_scanner.vulnerabilities.values())
        
        return {
            "total": len(vulns),
            "open": len([v for v in vulns if v.status == VulnerabilityStatus.OPEN]),
            "in_progress": len([v for v in vulns if v.status == VulnerabilityStatus.IN_PROGRESS]),
            "fixed": len([v for v in vulns if v.status == VulnerabilityStatus.FIXED]),
            "false_positive": len([v for v in vulns if v.status == VulnerabilityStatus.FALSE_POSITIVE]),
            "accepted_risk": len([v for v in vulns if v.status == VulnerabilityStatus.ACCEPTED_RISK])
        }


class SecurityScanningPlatform:
    """Платформа сканирования безопасности"""
    
    def __init__(self):
        self.vuln_scanner = VulnerabilityScanner()
        self.secret_scanner = SecretScanner()
        self.compliance_checker = ComplianceChecker()
        self.remediation_tracker = RemediationTracker(self.vuln_scanner)
        self.policies: Dict[str, ScanPolicy] = {}
        
    async def full_scan(self, target: str) -> Dict[str, Any]:
        """Полное сканирование"""
        results = {}
        
        # SAST
        results["sast"] = await self.vuln_scanner.scan_sast(target)
        
        # Dependencies
        results["sca"] = await self.vuln_scanner.scan_dependencies(target)
        
        # Secrets
        results["secrets"] = await self.secret_scanner.scan(target)
        
        # Container (if applicable)
        if ":" in target or target.endswith(".tar"):
            results["container"] = await self.vuln_scanner.scan_container(target)
            
        return results
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        vulns = list(self.vuln_scanner.vulnerabilities.values())
        
        return {
            "total_vulnerabilities": len(vulns),
            "critical": len([v for v in vulns if v.severity == Severity.CRITICAL]),
            "high": len([v for v in vulns if v.severity == Severity.HIGH]),
            "medium": len([v for v in vulns if v.severity == Severity.MEDIUM]),
            "low": len([v for v in vulns if v.severity == Severity.LOW]),
            "total_secrets": len(self.secret_scanner.secrets),
            "total_scans": len(self.vuln_scanner.scans),
            "compliance_checks": len(self.compliance_checker.checks)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 129: Security Scanning Platform")
    print("=" * 60)
    
    async def demo():
        platform = SecurityScanningPlatform()
        print("✓ Security Scanning Platform created")
        
        # Create scan policy
        print("\n📋 Creating Scan Policy...")
        
        policy = ScanPolicy(
            policy_id=f"policy_{uuid.uuid4().hex[:8]}",
            name="Production Security Policy",
            scan_types=[ScanType.SAST, ScanType.SCA, ScanType.SECRET, ScanType.CONTAINER],
            fail_on_critical=True,
            fail_on_high=True,
            max_critical=0,
            max_high=5,
            compliance_standards=[ComplianceStandard.OWASP_TOP10, ComplianceStandard.PCI_DSS]
        )
        platform.policies[policy.policy_id] = policy
        print(f"  ✓ {policy.name}")
        print(f"    Scans: {[st.value for st in policy.scan_types]}")
        print(f"    Fail on critical: {policy.fail_on_critical}")
        
        # Run SAST scan
        print("\n🔍 Running SAST Scan...")
        
        sast_result = await platform.vuln_scanner.scan_sast("/app/backend")
        
        print(f"  ✓ Scan completed in {sast_result.duration_seconds}s")
        print(f"    Critical: {sast_result.critical_count}")
        print(f"    High: {sast_result.high_count}")
        print(f"    Medium: {sast_result.medium_count}")
        print(f"    Low: {sast_result.low_count}")
        
        # Run dependency scan
        print("\n📦 Running Dependency Scan...")
        
        sca_result = await platform.vuln_scanner.scan_dependencies("/app/backend")
        
        print(f"  ✓ Scan completed in {sca_result.duration_seconds}s")
        print(f"    Critical: {sca_result.critical_count}")
        print(f"    High: {sca_result.high_count}")
        print(f"    Medium: {sca_result.medium_count}")
        
        # Run secret scan
        print("\n🔐 Running Secret Scan...")
        
        secrets = await platform.secret_scanner.scan("/app/backend")
        
        print(f"  ✓ Found {len(secrets)} potential secrets")
        for secret in secrets[:3]:
            print(f"    - {secret.secret_type}: {secret.file_path}:{secret.line_number}")
            
        # Run container scan
        print("\n🐳 Running Container Scan...")
        
        container_result = await platform.vuln_scanner.scan_container("myapp:latest")
        
        print(f"  ✓ Scan completed in {container_result.duration_seconds}s")
        print(f"    Critical: {container_result.critical_count}")
        print(f"    High: {container_result.high_count}")
        
        # Display vulnerabilities
        print("\n⚠️ Vulnerability Summary:")
        
        by_severity = defaultdict(list)
        for vuln in platform.vuln_scanner.vulnerabilities.values():
            by_severity[vuln.severity].append(vuln)
            
        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
            vulns = by_severity[severity]
            if vulns:
                icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(severity.value, "⚪")
                print(f"\n  {icon} {severity.value.upper()} ({len(vulns)}):")
                for vuln in vulns[:3]:
                    print(f"    - {vuln.title}")
                    if vuln.cve_id:
                        print(f"      CVE: {vuln.cve_id}")
                    if vuln.package_name:
                        print(f"      Package: {vuln.package_name} {vuln.package_version} -> {vuln.fixed_version}")
                        
        # Compliance check
        print("\n📜 Compliance Check (OWASP Top 10):")
        
        all_vulns = list(platform.vuln_scanner.vulnerabilities.values())
        compliance_results = await platform.compliance_checker.check(
            ComplianceStandard.OWASP_TOP10,
            all_vulns
        )
        
        passed = len([c for c in compliance_results if c.passed])
        failed = len([c for c in compliance_results if not c.passed])
        
        print(f"  Passed: {passed}/{len(compliance_results)}")
        print(f"  Failed: {failed}/{len(compliance_results)}")
        
        for check in compliance_results:
            icon = "✅" if check.passed else "❌"
            print(f"    {icon} {check.rule_id}: {check.rule_name}")
            
        # Create remediation plans
        print("\n🔧 Creating Remediation Plans...")
        
        critical_vulns = [v for v in platform.vuln_scanner.vulnerabilities.values() 
                        if v.severity == Severity.CRITICAL]
        
        for vuln in critical_vulns[:3]:
            plan = platform.remediation_tracker.create_plan(
                vuln.vuln_id,
                assignee="security-team",
                due_date=datetime.now() + timedelta(days=3)
            )
            print(f"  ✓ Plan created for {vuln.title}")
            print(f"    Due: {plan['due_date'].strftime('%Y-%m-%d')}")
            
        # Simulate fixing
        print("\n✅ Simulating Fixes...")
        
        for vuln in list(platform.vuln_scanner.vulnerabilities.values())[:2]:
            platform.remediation_tracker.update_status(vuln.vuln_id, VulnerabilityStatus.FIXED)
            print(f"  ✓ Fixed: {vuln.title}")
            
        # Remediation summary
        print("\n📊 Remediation Summary:")
        
        summary = platform.remediation_tracker.get_summary()
        
        print(f"  Total: {summary['total']}")
        print(f"  Open: {summary['open']}")
        print(f"  In Progress: {summary['in_progress']}")
        print(f"  Fixed: {summary['fixed']}")
        print(f"  False Positive: {summary['false_positive']}")
        print(f"  Accepted Risk: {summary['accepted_risk']}")
        
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Vulnerabilities: {stats['total_vulnerabilities']}")
        print(f"    Critical: {stats['critical']}")
        print(f"    High: {stats['high']}")
        print(f"    Medium: {stats['medium']}")
        print(f"    Low: {stats['low']}")
        print(f"  Total Secrets: {stats['total_secrets']}")
        print(f"  Total Scans: {stats['total_scans']}")
        print(f"  Compliance Checks: {stats['compliance_checks']}")
        
        # Dashboard
        print("\n📋 Security Scanning Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │              Security Scanning Overview                     │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Vulnerabilities: {stats['total_vulnerabilities']:>10}                        │")
        print(f"  │   Critical:           {stats['critical']:>10}                        │")
        print(f"  │   High:               {stats['high']:>10}                        │")
        print(f"  │   Medium:             {stats['medium']:>10}                        │")
        print(f"  │   Low:                {stats['low']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Exposed Secrets:      {stats['total_secrets']:>10}                        │")
        print(f"  │ Total Scans:          {stats['total_scans']:>10}                        │")
        print(f"  │ Compliance Checks:    {stats['compliance_checks']:>10}                        │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Security Scanning Platform initialized!")
    print("=" * 60)
