#!/usr/bin/env python3
"""
Server Init - Iteration 221: Dependency Scanner Platform
Платформа сканирования зависимостей

Функционал:
- Dependency Discovery - обнаружение зависимостей
- Vulnerability Scanning - сканирование уязвимостей
- License Analysis - анализ лицензий
- Version Tracking - отслеживание версий
- Update Recommendations - рекомендации обновлений
- SBOM Generation - генерация SBOM
- Policy Enforcement - применение политик
- Risk Assessment - оценка рисков
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid


class DependencyType(Enum):
    """Тип зависимости"""
    DIRECT = "direct"
    TRANSITIVE = "transitive"
    DEV = "dev"
    OPTIONAL = "optional"


class VulnerabilitySeverity(Enum):
    """Серьёзность уязвимости"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class LicenseRisk(Enum):
    """Риск лицензии"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class ScanStatus(Enum):
    """Статус сканирования"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Dependency:
    """Зависимость"""
    dep_id: str
    name: str = ""
    version: str = ""
    
    # Type
    dep_type: DependencyType = DependencyType.DIRECT
    
    # Source
    ecosystem: str = ""  # npm, pypi, maven, etc.
    source_url: str = ""
    
    # License
    license: str = ""
    license_risk: LicenseRisk = LicenseRisk.UNKNOWN
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    
    # Metadata
    description: str = ""
    homepage: str = ""
    
    # Versions
    latest_version: str = ""
    is_outdated: bool = False


@dataclass
class Vulnerability:
    """Уязвимость"""
    vuln_id: str
    cve_id: str = ""
    
    # Affected
    affected_package: str = ""
    affected_versions: str = ""  # e.g., "< 2.0.0"
    
    # Fixed
    fixed_version: str = ""
    
    # Severity
    severity: VulnerabilitySeverity = VulnerabilitySeverity.UNKNOWN
    cvss_score: float = 0  # 0-10
    
    # Description
    title: str = ""
    description: str = ""
    
    # References
    references: List[str] = field(default_factory=list)
    
    # Dates
    published_at: datetime = field(default_factory=datetime.now)
    
    # Exploitability
    exploit_available: bool = False


@dataclass
class License:
    """Лицензия"""
    license_id: str
    spdx_id: str = ""
    name: str = ""
    
    # Classification
    osi_approved: bool = False
    copyleft: bool = False
    
    # Risk
    risk: LicenseRisk = LicenseRisk.LOW
    
    # Permissions
    commercial_use: bool = True
    modification: bool = True
    distribution: bool = True
    
    # Requirements
    attribution: bool = False
    disclose_source: bool = False


@dataclass
class ScanResult:
    """Результат сканирования"""
    scan_id: str
    project_name: str = ""
    
    # Status
    status: ScanStatus = ScanStatus.PENDING
    
    # Counts
    total_dependencies: int = 0
    direct_dependencies: int = 0
    transitive_dependencies: int = 0
    
    # Vulnerabilities
    vulnerabilities_critical: int = 0
    vulnerabilities_high: int = 0
    vulnerabilities_medium: int = 0
    vulnerabilities_low: int = 0
    
    # Licenses
    license_issues: int = 0
    
    # Outdated
    outdated_dependencies: int = 0
    
    # Time
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Risk score
    risk_score: float = 0  # 0-100


@dataclass
class SBOM:
    """Software Bill of Materials"""
    sbom_id: str
    project_name: str = ""
    version: str = ""
    
    # Format
    format: str = "CycloneDX"  # CycloneDX, SPDX
    spec_version: str = "1.4"
    
    # Components
    components: List[Dependency] = field(default_factory=list)
    
    # Generated
    generated_at: datetime = field(default_factory=datetime.now)
    
    # Metadata
    supplier: str = ""
    authors: List[str] = field(default_factory=list)


@dataclass
class PolicyRule:
    """Правило политики"""
    rule_id: str
    name: str = ""
    
    # Condition
    condition_type: str = ""  # license, vulnerability, version
    condition_value: str = ""
    
    # Action
    action: str = "warn"  # warn, block, approve
    
    # Active
    active: bool = True


class VulnerabilityDatabase:
    """База данных уязвимостей"""
    
    def __init__(self):
        self.vulnerabilities: Dict[str, List[Vulnerability]] = {}
        
    def add_vulnerability(self, vuln: Vulnerability):
        """Добавление уязвимости"""
        if vuln.affected_package not in self.vulnerabilities:
            self.vulnerabilities[vuln.affected_package] = []
        self.vulnerabilities[vuln.affected_package].append(vuln)
        
    def check_package(self, name: str, version: str) -> List[Vulnerability]:
        """Проверка пакета"""
        vulns = self.vulnerabilities.get(name, [])
        # Simplified version matching
        return [v for v in vulns if self._version_affected(version, v.affected_versions)]
        
    def _version_affected(self, version: str, affected: str) -> bool:
        """Проверка затронутости версии (упрощённо)"""
        # Simplified: randomly determine if affected
        return random.random() > 0.7


class LicenseDatabase:
    """База данных лицензий"""
    
    KNOWN_LICENSES = {
        "MIT": License("mit", "MIT", "MIT License", True, False, LicenseRisk.NONE, True, True, True, True, False),
        "Apache-2.0": License("apache", "Apache-2.0", "Apache License 2.0", True, False, LicenseRisk.NONE, True, True, True, True, False),
        "GPL-3.0": License("gpl3", "GPL-3.0", "GNU GPL v3", True, True, LicenseRisk.HIGH, True, True, True, True, True),
        "BSD-3-Clause": License("bsd3", "BSD-3-Clause", "BSD 3-Clause", True, False, LicenseRisk.NONE, True, True, True, True, False),
        "ISC": License("isc", "ISC", "ISC License", True, False, LicenseRisk.NONE, True, True, True, True, False),
        "LGPL-3.0": License("lgpl3", "LGPL-3.0", "GNU LGPL v3", True, True, LicenseRisk.MEDIUM, True, True, True, True, True),
        "AGPL-3.0": License("agpl3", "AGPL-3.0", "GNU AGPL v3", True, True, LicenseRisk.HIGH, True, True, True, True, True),
    }
    
    def get_license(self, spdx_id: str) -> Optional[License]:
        """Получение лицензии"""
        return self.KNOWN_LICENSES.get(spdx_id)
        
    def assess_risk(self, spdx_id: str) -> LicenseRisk:
        """Оценка риска лицензии"""
        license = self.get_license(spdx_id)
        return license.risk if license else LicenseRisk.UNKNOWN


class DependencyScanner:
    """Сканер зависимостей"""
    
    def __init__(self):
        self.vuln_db = VulnerabilityDatabase()
        self.license_db = LicenseDatabase()
        
        # Populate some vulnerabilities
        self._populate_vulnerabilities()
        
    def _populate_vulnerabilities(self):
        """Наполнение БД уязвимостей"""
        sample_vulns = [
            ("lodash", "CVE-2021-23337", "Prototype Pollution", VulnerabilitySeverity.HIGH, 7.2),
            ("axios", "CVE-2021-3749", "ReDoS vulnerability", VulnerabilitySeverity.HIGH, 7.5),
            ("requests", "CVE-2023-32681", "Unintended header leak", VulnerabilitySeverity.MEDIUM, 6.1),
            ("express", "CVE-2022-24999", "Open redirect", VulnerabilitySeverity.MEDIUM, 5.3),
        ]
        
        for pkg, cve, title, severity, cvss in sample_vulns:
            self.vuln_db.add_vulnerability(Vulnerability(
                vuln_id=f"vuln_{uuid.uuid4().hex[:8]}",
                cve_id=cve,
                affected_package=pkg,
                affected_versions="< 999.0.0",  # Simplified
                severity=severity,
                cvss_score=cvss,
                title=title
            ))
            
    async def scan(self, project_name: str, dependencies: List[Dependency]) -> ScanResult:
        """Сканирование проекта"""
        result = ScanResult(
            scan_id=f"scan_{uuid.uuid4().hex[:8]}",
            project_name=project_name,
            status=ScanStatus.RUNNING,
            started_at=datetime.now()
        )
        
        result.total_dependencies = len(dependencies)
        result.direct_dependencies = len([d for d in dependencies if d.dep_type == DependencyType.DIRECT])
        result.transitive_dependencies = len([d for d in dependencies if d.dep_type == DependencyType.TRANSITIVE])
        
        # Scan each dependency
        for dep in dependencies:
            await asyncio.sleep(0.01)  # Simulate scanning
            
            # Check vulnerabilities
            vulns = self.vuln_db.check_package(dep.name, dep.version)
            for v in vulns:
                if v.severity == VulnerabilitySeverity.CRITICAL:
                    result.vulnerabilities_critical += 1
                elif v.severity == VulnerabilitySeverity.HIGH:
                    result.vulnerabilities_high += 1
                elif v.severity == VulnerabilitySeverity.MEDIUM:
                    result.vulnerabilities_medium += 1
                else:
                    result.vulnerabilities_low += 1
                    
            # Check license
            license_risk = self.license_db.assess_risk(dep.license)
            if license_risk in [LicenseRisk.HIGH, LicenseRisk.UNKNOWN]:
                result.license_issues += 1
                
            # Check outdated
            if dep.is_outdated:
                result.outdated_dependencies += 1
                
        # Calculate risk score
        result.risk_score = self._calculate_risk_score(result)
        
        result.status = ScanStatus.COMPLETED
        result.completed_at = datetime.now()
        
        return result
        
    def _calculate_risk_score(self, result: ScanResult) -> float:
        """Расчёт риск-скора"""
        score = 0
        score += result.vulnerabilities_critical * 25
        score += result.vulnerabilities_high * 15
        score += result.vulnerabilities_medium * 5
        score += result.vulnerabilities_low * 1
        score += result.license_issues * 10
        score += result.outdated_dependencies * 2
        
        return min(100, score)


class DependencyScannerPlatform:
    """Платформа сканирования зависимостей"""
    
    def __init__(self):
        self.scanner = DependencyScanner()
        self.scans: Dict[str, ScanResult] = {}
        self.dependencies: Dict[str, List[Dependency]] = {}  # project -> deps
        self.sboms: Dict[str, SBOM] = {}
        self.policies: Dict[str, PolicyRule] = {}
        
    def add_policy(self, name: str, condition_type: str,
                  condition_value: str, action: str = "warn") -> PolicyRule:
        """Добавление политики"""
        rule = PolicyRule(
            rule_id=f"policy_{uuid.uuid4().hex[:8]}",
            name=name,
            condition_type=condition_type,
            condition_value=condition_value,
            action=action
        )
        self.policies[rule.rule_id] = rule
        return rule
        
    def register_project(self, project_name: str, deps: List[Dict[str, Any]]):
        """Регистрация проекта"""
        dependencies = []
        
        for dep in deps:
            d = Dependency(
                dep_id=f"dep_{uuid.uuid4().hex[:8]}",
                name=dep.get("name", ""),
                version=dep.get("version", ""),
                dep_type=DependencyType(dep.get("type", "direct")),
                ecosystem=dep.get("ecosystem", "npm"),
                license=dep.get("license", "MIT"),
                is_outdated=dep.get("outdated", False),
                latest_version=dep.get("latest", dep.get("version", ""))
            )
            dependencies.append(d)
            
        self.dependencies[project_name] = dependencies
        
    async def scan_project(self, project_name: str) -> Optional[ScanResult]:
        """Сканирование проекта"""
        deps = self.dependencies.get(project_name, [])
        if not deps:
            return None
            
        result = await self.scanner.scan(project_name, deps)
        self.scans[project_name] = result
        
        return result
        
    def generate_sbom(self, project_name: str, version: str = "1.0.0") -> Optional[SBOM]:
        """Генерация SBOM"""
        deps = self.dependencies.get(project_name, [])
        if not deps:
            return None
            
        sbom = SBOM(
            sbom_id=f"sbom_{uuid.uuid4().hex[:8]}",
            project_name=project_name,
            version=version,
            components=deps
        )
        
        self.sboms[project_name] = sbom
        return sbom
        
    def check_policies(self, project_name: str) -> List[tuple[PolicyRule, str]]:
        """Проверка политик"""
        violations = []
        deps = self.dependencies.get(project_name, [])
        
        for rule in self.policies.values():
            if not rule.active:
                continue
                
            for dep in deps:
                violated = False
                reason = ""
                
                if rule.condition_type == "license":
                    if dep.license == rule.condition_value:
                        violated = True
                        reason = f"{dep.name} uses {dep.license} license"
                        
                elif rule.condition_type == "vulnerability":
                    vulns = self.scanner.vuln_db.check_package(dep.name, dep.version)
                    for v in vulns:
                        if v.severity.value == rule.condition_value:
                            violated = True
                            reason = f"{dep.name} has {v.severity.value} vulnerability"
                            break
                            
                if violated:
                    violations.append((rule, reason))
                    
        return violations
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_vulns = sum(
            s.vulnerabilities_critical + s.vulnerabilities_high + 
            s.vulnerabilities_medium + s.vulnerabilities_low
            for s in self.scans.values()
        )
        
        return {
            "projects_scanned": len(self.scans),
            "total_dependencies": sum(len(d) for d in self.dependencies.values()),
            "total_vulnerabilities": total_vulns,
            "critical_vulnerabilities": sum(s.vulnerabilities_critical for s in self.scans.values()),
            "high_vulnerabilities": sum(s.vulnerabilities_high for s in self.scans.values()),
            "license_issues": sum(s.license_issues for s in self.scans.values()),
            "outdated_packages": sum(s.outdated_dependencies for s in self.scans.values()),
            "sboms_generated": len(self.sboms),
            "policies_defined": len(self.policies)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 221: Dependency Scanner Platform")
    print("=" * 60)
    
    platform = DependencyScannerPlatform()
    print("✓ Dependency Scanner Platform created")
    
    # Add policies
    print("\n📋 Adding Security Policies...")
    
    platform.add_policy("Block GPL", "license", "GPL-3.0", "block")
    platform.add_policy("Warn AGPL", "license", "AGPL-3.0", "warn")
    platform.add_policy("Block Critical", "vulnerability", "critical", "block")
    print("  ✓ 3 policies configured")
    
    # Register projects
    print("\n📦 Registering Projects...")
    
    # Project 1: Web App
    platform.register_project("web-frontend", [
        {"name": "react", "version": "18.2.0", "type": "direct", "license": "MIT", "latest": "18.2.0"},
        {"name": "lodash", "version": "4.17.20", "type": "direct", "license": "MIT", "outdated": True, "latest": "4.17.21"},
        {"name": "axios", "version": "0.21.1", "type": "direct", "license": "MIT", "outdated": True, "latest": "1.6.0"},
        {"name": "webpack", "version": "5.88.0", "type": "dev", "license": "MIT"},
        {"name": "typescript", "version": "5.2.0", "type": "dev", "license": "Apache-2.0"},
        {"name": "loose-envify", "version": "1.4.0", "type": "transitive", "license": "MIT"},
        {"name": "object-assign", "version": "4.1.1", "type": "transitive", "license": "MIT"},
    ])
    print("  ✓ web-frontend: 7 dependencies")
    
    # Project 2: API Server
    platform.register_project("api-server", [
        {"name": "express", "version": "4.18.2", "type": "direct", "license": "MIT"},
        {"name": "mongoose", "version": "7.5.0", "type": "direct", "license": "MIT"},
        {"name": "jsonwebtoken", "version": "9.0.0", "type": "direct", "license": "MIT"},
        {"name": "helmet", "version": "7.0.0", "type": "direct", "license": "MIT"},
        {"name": "cors", "version": "2.8.5", "type": "direct", "license": "MIT"},
        {"name": "body-parser", "version": "1.20.2", "type": "transitive", "license": "MIT"},
        {"name": "debug", "version": "4.3.4", "type": "transitive", "license": "MIT"},
    ])
    print("  ✓ api-server: 7 dependencies")
    
    # Project 3: Python Service
    platform.register_project("python-service", [
        {"name": "fastapi", "version": "0.103.0", "type": "direct", "license": "MIT", "ecosystem": "pypi"},
        {"name": "requests", "version": "2.28.0", "type": "direct", "license": "Apache-2.0", "ecosystem": "pypi", "outdated": True},
        {"name": "pydantic", "version": "2.4.0", "type": "direct", "license": "MIT", "ecosystem": "pypi"},
        {"name": "sqlalchemy", "version": "2.0.0", "type": "direct", "license": "MIT", "ecosystem": "pypi"},
        {"name": "uvicorn", "version": "0.23.0", "type": "direct", "license": "BSD-3-Clause", "ecosystem": "pypi"},
    ])
    print("  ✓ python-service: 5 dependencies")
    
    # Scan projects
    print("\n🔍 Scanning Projects...")
    
    for project in ["web-frontend", "api-server", "python-service"]:
        result = await platform.scan_project(project)
        if result:
            risk_icon = "🔴" if result.risk_score > 50 else "🟡" if result.risk_score > 20 else "🟢"
            print(f"  {risk_icon} {project}: risk score {result.risk_score:.0f}")
            
    # Generate SBOMs
    print("\n📄 Generating SBOMs...")
    
    for project in ["web-frontend", "api-server", "python-service"]:
        sbom = platform.generate_sbom(project)
        if sbom:
            print(f"  ✓ {project}: {len(sbom.components)} components")
            
    # Check policies
    print("\n🚨 Policy Violations:")
    
    for project in platform.dependencies.keys():
        violations = platform.check_policies(project)
        if violations:
            print(f"\n  {project}:")
            for rule, reason in violations[:3]:
                action_icon = "🚫" if rule.action == "block" else "⚠️"
                print(f"    {action_icon} [{rule.action}] {reason}")
                
    # Display scan results
    print("\n📊 Scan Results:")
    
    print("\n  ┌──────────────────┬───────┬────────┬────────┬────────┬─────────┐")
    print("  │ Project          │ Deps  │ Crit   │ High   │ Medium │ Risk    │")
    print("  ├──────────────────┼───────┼────────┼────────┼────────┼─────────┤")
    
    for project, result in platform.scans.items():
        name = project[:16].ljust(16)
        deps = str(result.total_dependencies).center(5)
        crit = str(result.vulnerabilities_critical).center(6)
        high = str(result.vulnerabilities_high).center(6)
        med = str(result.vulnerabilities_medium).center(6)
        risk = f"{result.risk_score:.0f}".center(7)
        
        print(f"  │ {name} │ {deps} │ {crit} │ {high} │ {med} │ {risk} │")
        
    print("  └──────────────────┴───────┴────────┴────────┴────────┴─────────┘")
    
    # Vulnerability breakdown
    print("\n🔓 Vulnerability Breakdown:")
    
    total_crit = sum(s.vulnerabilities_critical for s in platform.scans.values())
    total_high = sum(s.vulnerabilities_high for s in platform.scans.values())
    total_med = sum(s.vulnerabilities_medium for s in platform.scans.values())
    total_low = sum(s.vulnerabilities_low for s in platform.scans.values())
    
    print(f"  🔴 Critical: {total_crit}")
    print(f"  🟠 High:     {total_high}")
    print(f"  🟡 Medium:   {total_med}")
    print(f"  🟢 Low:      {total_low}")
    
    # License distribution
    print("\n📜 License Distribution:")
    
    license_count = {}
    for deps in platform.dependencies.values():
        for dep in deps:
            lic = dep.license
            if lic not in license_count:
                license_count[lic] = 0
            license_count[lic] += 1
            
    for lic, count in sorted(license_count.items(), key=lambda x: -x[1]):
        risk = platform.scanner.license_db.assess_risk(lic)
        risk_icon = "🔴" if risk == LicenseRisk.HIGH else "🟡" if risk == LicenseRisk.MEDIUM else "🟢"
        bar = "█" * count
        print(f"  {risk_icon} {lic:15s} [{bar}] {count}")
        
    # Outdated packages
    print("\n📦 Outdated Packages:")
    
    for project, deps in platform.dependencies.items():
        outdated = [d for d in deps if d.is_outdated]
        if outdated:
            print(f"\n  {project}:")
            for dep in outdated[:3]:
                print(f"    • {dep.name}: {dep.version} -> {dep.latest_version}")
                
    # SBOM summary
    print("\n📄 SBOM Summary:")
    
    for project, sbom in platform.sboms.items():
        print(f"  {project}:")
        print(f"    Format: {sbom.format} {sbom.spec_version}")
        print(f"    Components: {len(sbom.components)}")
        print(f"    Generated: {sbom.generated_at.strftime('%Y-%m-%d %H:%M')}")
        
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📈 Platform Statistics:")
    
    print(f"\n  Projects Scanned: {stats['projects_scanned']}")
    print(f"  Total Dependencies: {stats['total_dependencies']}")
    print(f"  Total Vulnerabilities: {stats['total_vulnerabilities']}")
    print(f"  Critical: {stats['critical_vulnerabilities']}")
    print(f"  License Issues: {stats['license_issues']}")
    print(f"  Outdated: {stats['outdated_packages']}")
    print(f"  SBOMs: {stats['sboms_generated']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Dependency Scanner Dashboard                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Projects Scanned:              {stats['projects_scanned']:>12}                        │")
    print(f"│ Total Dependencies:            {stats['total_dependencies']:>12}                        │")
    print(f"│ Total Vulnerabilities:         {stats['total_vulnerabilities']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Critical Vulnerabilities:      {stats['critical_vulnerabilities']:>12}                        │")
    print(f"│ License Issues:                {stats['license_issues']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Dependency Scanner Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
