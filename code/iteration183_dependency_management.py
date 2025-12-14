#!/usr/bin/env python3
"""
Server Init - Iteration 183: Dependency Management Platform
Платформа управления зависимостями

Функционал:
- Dependency Graph - граф зависимостей
- Version Resolution - разрешение версий
- Vulnerability Scanning - сканирование уязвимостей
- License Compliance - соответствие лицензий
- Update Management - управление обновлениями
- Breaking Change Detection - обнаружение несовместимости
- Dependency Health Scores - оценки здоровья
- SBOM Generation - генерация SBOM
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
import uuid


class DependencyType(Enum):
    """Тип зависимости"""
    DIRECT = "direct"
    TRANSITIVE = "transitive"
    DEV = "dev"
    PEER = "peer"
    OPTIONAL = "optional"


class LicenseType(Enum):
    """Тип лицензии"""
    MIT = "MIT"
    APACHE_2 = "Apache-2.0"
    GPL_3 = "GPL-3.0"
    BSD_3 = "BSD-3-Clause"
    ISC = "ISC"
    LGPL = "LGPL"
    PROPRIETARY = "Proprietary"
    UNKNOWN = "Unknown"


class VulnerabilitySeverity(Enum):
    """Серьёзность уязвимости"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class UpdateStatus(Enum):
    """Статус обновления"""
    UP_TO_DATE = "up_to_date"
    PATCH_AVAILABLE = "patch_available"
    MINOR_AVAILABLE = "minor_available"
    MAJOR_AVAILABLE = "major_available"
    DEPRECATED = "deprecated"


@dataclass
class Dependency:
    """Зависимость"""
    dependency_id: str
    name: str = ""
    version: str = ""
    
    # Type
    dep_type: DependencyType = DependencyType.DIRECT
    
    # Source
    registry: str = "npm"  # npm, pypi, maven, etc.
    repository: str = ""
    
    # License
    license: LicenseType = LicenseType.MIT
    
    # Metadata
    description: str = ""
    homepage: str = ""
    maintainers: List[str] = field(default_factory=list)
    
    # Dependencies (transitive)
    dependencies: List[str] = field(default_factory=list)  # List of dependency_ids
    
    # Stats
    weekly_downloads: int = 0
    last_published: Optional[datetime] = None


@dataclass
class Vulnerability:
    """Уязвимость"""
    vuln_id: str
    cve_id: str = ""
    
    # Affected
    dependency_name: str = ""
    affected_versions: str = ""  # semver range
    
    # Severity
    severity: VulnerabilitySeverity = VulnerabilitySeverity.MEDIUM
    cvss_score: float = 5.0
    
    # Description
    title: str = ""
    description: str = ""
    
    # Fix
    patched_versions: str = ""
    recommendation: str = ""
    
    # Timeline
    published_at: datetime = field(default_factory=datetime.now)


@dataclass
class LicensePolicy:
    """Политика лицензий"""
    policy_id: str
    name: str = ""
    
    # Rules
    allowed_licenses: List[LicenseType] = field(default_factory=list)
    denied_licenses: List[LicenseType] = field(default_factory=list)
    
    # Exceptions
    exceptions: Dict[str, str] = field(default_factory=dict)  # package -> reason


@dataclass
class DependencyHealth:
    """Здоровье зависимости"""
    dependency_id: str
    
    # Scores (0-100)
    overall_score: float = 100.0
    security_score: float = 100.0
    maintenance_score: float = 100.0
    popularity_score: float = 100.0
    license_score: float = 100.0
    
    # Issues
    vulnerabilities_count: int = 0
    outdated_days: int = 0
    
    # Risk factors
    risk_factors: List[str] = field(default_factory=list)


@dataclass
class UpdateRecommendation:
    """Рекомендация обновления"""
    recommendation_id: str
    dependency_name: str = ""
    
    # Versions
    current_version: str = ""
    recommended_version: str = ""
    latest_version: str = ""
    
    # Status
    update_status: UpdateStatus = UpdateStatus.UP_TO_DATE
    
    # Risk
    breaking_changes: bool = False
    changelog_url: str = ""
    
    # Impact
    affected_files: List[str] = field(default_factory=list)


class DependencyGraph:
    """Граф зависимостей"""
    
    def __init__(self):
        self.dependencies: Dict[str, Dependency] = {}
        self.edges: Dict[str, Set[str]] = {}  # dep_id -> set of dependent dep_ids
        
    def add_dependency(self, dep: Dependency):
        """Добавление зависимости"""
        self.dependencies[dep.dependency_id] = dep
        if dep.dependency_id not in self.edges:
            self.edges[dep.dependency_id] = set()
            
    def add_edge(self, from_id: str, to_id: str):
        """Добавление связи"""
        if from_id not in self.edges:
            self.edges[from_id] = set()
        self.edges[from_id].add(to_id)
        
    def get_all_transitive(self, dep_id: str) -> Set[str]:
        """Получение всех транзитивных зависимостей"""
        visited = set()
        
        def traverse(current_id: str):
            if current_id in visited:
                return
            visited.add(current_id)
            
            dep = self.dependencies.get(current_id)
            if dep:
                for child_id in dep.dependencies:
                    traverse(child_id)
                    
        traverse(dep_id)
        visited.discard(dep_id)
        return visited
        
    def find_cycles(self) -> List[List[str]]:
        """Поиск циклов"""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.edges.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path)
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:])
                    
            path.pop()
            rec_stack.discard(node)
            
        for node in self.dependencies:
            if node not in visited:
                dfs(node, [])
                
        return cycles


class VulnerabilityScanner:
    """Сканер уязвимостей"""
    
    def __init__(self):
        self.vulnerability_db: Dict[str, List[Vulnerability]] = {}
        
    def add_vulnerability(self, vuln: Vulnerability):
        """Добавление уязвимости в базу"""
        if vuln.dependency_name not in self.vulnerability_db:
            self.vulnerability_db[vuln.dependency_name] = []
        self.vulnerability_db[vuln.dependency_name].append(vuln)
        
    def scan(self, dependencies: List[Dependency]) -> List[Vulnerability]:
        """Сканирование зависимостей"""
        found = []
        
        for dep in dependencies:
            vulns = self.vulnerability_db.get(dep.name, [])
            for vuln in vulns:
                # Simple version check (in real - semver matching)
                if dep.version in vuln.affected_versions or "*" in vuln.affected_versions:
                    found.append(vuln)
                    
        return found


class LicenseChecker:
    """Проверщик лицензий"""
    
    def __init__(self, policy: LicensePolicy):
        self.policy = policy
        
    def check(self, dependencies: List[Dependency]) -> Dict[str, Any]:
        """Проверка лицензий"""
        results = {
            "compliant": [],
            "violations": [],
            "unknown": []
        }
        
        for dep in dependencies:
            if dep.name in self.policy.exceptions:
                results["compliant"].append({
                    "dependency": dep.name,
                    "license": dep.license.value,
                    "status": "exception",
                    "reason": self.policy.exceptions[dep.name]
                })
            elif dep.license in self.policy.denied_licenses:
                results["violations"].append({
                    "dependency": dep.name,
                    "license": dep.license.value,
                    "status": "denied"
                })
            elif dep.license in self.policy.allowed_licenses:
                results["compliant"].append({
                    "dependency": dep.name,
                    "license": dep.license.value,
                    "status": "allowed"
                })
            elif dep.license == LicenseType.UNKNOWN:
                results["unknown"].append({
                    "dependency": dep.name,
                    "status": "unknown"
                })
            else:
                results["violations"].append({
                    "dependency": dep.name,
                    "license": dep.license.value,
                    "status": "not_allowed"
                })
                
        return results


class HealthAnalyzer:
    """Анализатор здоровья"""
    
    def analyze(self, dep: Dependency, vulns: List[Vulnerability]) -> DependencyHealth:
        """Анализ здоровья зависимости"""
        health = DependencyHealth(dependency_id=dep.dependency_id)
        
        # Security score
        vuln_count = len([v for v in vulns if v.dependency_name == dep.name])
        health.vulnerabilities_count = vuln_count
        health.security_score = max(0, 100 - vuln_count * 25)
        
        # Maintenance score
        if dep.last_published:
            days_since_update = (datetime.now() - dep.last_published).days
            health.outdated_days = days_since_update
            health.maintenance_score = max(0, 100 - days_since_update / 3)
            if days_since_update > 365:
                health.risk_factors.append("Not updated for over a year")
                
        # Popularity score
        if dep.weekly_downloads > 1000000:
            health.popularity_score = 100
        elif dep.weekly_downloads > 100000:
            health.popularity_score = 80
        elif dep.weekly_downloads > 10000:
            health.popularity_score = 60
        else:
            health.popularity_score = 40
            health.risk_factors.append("Low download count")
            
        # License score
        if dep.license in [LicenseType.MIT, LicenseType.APACHE_2, LicenseType.BSD_3]:
            health.license_score = 100
        elif dep.license == LicenseType.UNKNOWN:
            health.license_score = 0
            health.risk_factors.append("Unknown license")
        else:
            health.license_score = 70
            
        # Overall score
        health.overall_score = (
            health.security_score * 0.4 +
            health.maintenance_score * 0.25 +
            health.popularity_score * 0.2 +
            health.license_score * 0.15
        )
        
        return health


class SBOMGenerator:
    """Генератор SBOM"""
    
    def generate(self, project_name: str, dependencies: List[Dependency]) -> Dict[str, Any]:
        """Генерация SBOM (Software Bill of Materials)"""
        return {
            "bomFormat": "CycloneDX",
            "specVersion": "1.4",
            "version": 1,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "component": {
                    "type": "application",
                    "name": project_name,
                }
            },
            "components": [
                {
                    "type": "library",
                    "name": dep.name,
                    "version": dep.version,
                    "purl": f"pkg:{dep.registry}/{dep.name}@{dep.version}",
                    "licenses": [{"license": {"id": dep.license.value}}]
                }
                for dep in dependencies
            ]
        }


class DependencyManagementPlatform:
    """Платформа управления зависимостями"""
    
    def __init__(self):
        self.graph = DependencyGraph()
        self.scanner = VulnerabilityScanner()
        self.health_analyzer = HealthAnalyzer()
        self.sbom_generator = SBOMGenerator()
        self.license_policy: Optional[LicensePolicy] = None
        
    def set_license_policy(self, policy: LicensePolicy):
        """Установка политики лицензий"""
        self.license_policy = policy
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        deps = list(self.graph.dependencies.values())
        
        return {
            "total_dependencies": len(deps),
            "by_type": {
                dt.value: len([d for d in deps if d.dep_type == dt])
                for dt in DependencyType
            },
            "by_license": {
                lt.value: len([d for d in deps if d.license == lt])
                for lt in LicenseType if len([d for d in deps if d.license == lt]) > 0
            },
            "vulnerabilities_in_db": sum(len(v) for v in self.scanner.vulnerability_db.values())
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 183: Dependency Management Platform")
    print("=" * 60)
    
    platform = DependencyManagementPlatform()
    print("✓ Dependency Management Platform created")
    
    # Create dependencies
    print("\n📦 Creating Dependencies...")
    
    dependencies = [
        Dependency(
            dependency_id="react",
            name="react",
            version="18.2.0",
            dep_type=DependencyType.DIRECT,
            registry="npm",
            license=LicenseType.MIT,
            weekly_downloads=18000000,
            last_published=datetime.now() - timedelta(days=30)
        ),
        Dependency(
            dependency_id="lodash",
            name="lodash",
            version="4.17.21",
            dep_type=DependencyType.DIRECT,
            registry="npm",
            license=LicenseType.MIT,
            weekly_downloads=45000000,
            last_published=datetime.now() - timedelta(days=400)
        ),
        Dependency(
            dependency_id="express",
            name="express",
            version="4.18.2",
            dep_type=DependencyType.DIRECT,
            registry="npm",
            license=LicenseType.MIT,
            weekly_downloads=28000000,
            last_published=datetime.now() - timedelta(days=60)
        ),
        Dependency(
            dependency_id="axios",
            name="axios",
            version="1.5.0",
            dep_type=DependencyType.DIRECT,
            registry="npm",
            license=LicenseType.MIT,
            weekly_downloads=38000000,
            last_published=datetime.now() - timedelta(days=15)
        ),
        Dependency(
            dependency_id="moment",
            name="moment",
            version="2.29.4",
            dep_type=DependencyType.TRANSITIVE,
            registry="npm",
            license=LicenseType.MIT,
            weekly_downloads=15000000,
            last_published=datetime.now() - timedelta(days=500)
        ),
        Dependency(
            dependency_id="debug",
            name="debug",
            version="4.3.4",
            dep_type=DependencyType.TRANSITIVE,
            registry="npm",
            license=LicenseType.MIT,
            weekly_downloads=200000000,
            last_published=datetime.now() - timedelta(days=180)
        ),
        Dependency(
            dependency_id="jest",
            name="jest",
            version="29.6.0",
            dep_type=DependencyType.DEV,
            registry="npm",
            license=LicenseType.MIT,
            weekly_downloads=20000000,
            last_published=datetime.now() - timedelta(days=20)
        ),
        Dependency(
            dependency_id="typescript",
            name="typescript",
            version="5.2.0",
            dep_type=DependencyType.DEV,
            registry="npm",
            license=LicenseType.APACHE_2,
            weekly_downloads=40000000,
            last_published=datetime.now() - timedelta(days=10)
        ),
    ]
    
    for dep in dependencies:
        platform.graph.add_dependency(dep)
        print(f"  ✓ {dep.name}@{dep.version} ({dep.dep_type.value})")
        
    # Build dependency edges
    platform.graph.add_edge("express", "debug")
    platform.graph.add_edge("axios", "debug")
    
    # Set license policy
    print("\n📜 Setting License Policy...")
    
    policy = LicensePolicy(
        policy_id="corporate_policy",
        name="Corporate License Policy",
        allowed_licenses=[LicenseType.MIT, LicenseType.APACHE_2, LicenseType.BSD_3, LicenseType.ISC],
        denied_licenses=[LicenseType.GPL_3, LicenseType.PROPRIETARY]
    )
    
    platform.set_license_policy(policy)
    print(f"  Allowed: {', '.join([l.value for l in policy.allowed_licenses])}")
    print(f"  Denied: {', '.join([l.value for l in policy.denied_licenses])}")
    
    # Check licenses
    print("\n🔍 License Compliance Check...")
    
    checker = LicenseChecker(policy)
    results = checker.check(dependencies)
    
    print(f"\n  Compliant: {len(results['compliant'])}")
    print(f"  Violations: {len(results['violations'])}")
    print(f"  Unknown: {len(results['unknown'])}")
    
    # Add vulnerabilities
    print("\n⚠️ Adding Vulnerability Database...")
    
    vulns = [
        Vulnerability(
            vuln_id="VULN-001",
            cve_id="CVE-2023-1234",
            dependency_name="lodash",
            affected_versions="<4.17.22",
            severity=VulnerabilitySeverity.HIGH,
            cvss_score=7.5,
            title="Prototype Pollution",
            description="Prototype pollution vulnerability in lodash",
            patched_versions=">=4.17.22"
        ),
        Vulnerability(
            vuln_id="VULN-002",
            cve_id="CVE-2023-5678",
            dependency_name="moment",
            affected_versions="*",
            severity=VulnerabilitySeverity.MEDIUM,
            cvss_score=5.3,
            title="ReDoS vulnerability",
            description="Regular expression denial of service",
            patched_versions="None - migrate to dayjs",
            recommendation="Migrate to dayjs or date-fns"
        ),
    ]
    
    for vuln in vulns:
        platform.scanner.add_vulnerability(vuln)
        
    # Scan for vulnerabilities
    print("\n🔒 Vulnerability Scan...")
    
    found_vulns = platform.scanner.scan(dependencies)
    
    print(f"\n  Found {len(found_vulns)} vulnerabilities:")
    
    for vuln in found_vulns:
        icon = "🔴" if vuln.severity == VulnerabilitySeverity.CRITICAL else ("🟠" if vuln.severity == VulnerabilitySeverity.HIGH else "🟡")
        print(f"\n  {icon} {vuln.cve_id}: {vuln.title}")
        print(f"     Package: {vuln.dependency_name}")
        print(f"     Severity: {vuln.severity.value.upper()} (CVSS: {vuln.cvss_score})")
        print(f"     Fix: {vuln.patched_versions}")
        if vuln.recommendation:
            print(f"     Recommendation: {vuln.recommendation}")
            
    # Health analysis
    print("\n💚 Dependency Health Analysis...")
    
    print("\n  ┌────────────────┬─────────┬──────────┬───────────┬─────────┬─────────┐")
    print("  │ Package        │ Overall │ Security │ Maintain. │ Popular │ License │")
    print("  ├────────────────┼─────────┼──────────┼───────────┼─────────┼─────────┤")
    
    health_reports = []
    for dep in dependencies:
        health = platform.health_analyzer.analyze(dep, found_vulns)
        health_reports.append((dep, health))
        
        name = dep.name[:14].ljust(14)
        overall = f"{health.overall_score:.0f}".rjust(7)
        security = f"{health.security_score:.0f}".rjust(8)
        maint = f"{health.maintenance_score:.0f}".rjust(9)
        popular = f"{health.popularity_score:.0f}".rjust(7)
        lic = f"{health.license_score:.0f}".rjust(7)
        
        print(f"  │ {name} │ {overall} │ {security} │ {maint} │ {popular} │ {lic} │")
        
    print("  └────────────────┴─────────┴──────────┴───────────┴─────────┴─────────┘")
    
    # Risk factors
    print("\n⚠️ Risk Factors:")
    
    for dep, health in health_reports:
        if health.risk_factors:
            print(f"\n  {dep.name}:")
            for factor in health.risk_factors:
                print(f"    • {factor}")
                
    # Transitive dependencies
    print("\n🌳 Dependency Tree:")
    
    for dep in dependencies:
        if dep.dep_type == DependencyType.DIRECT:
            transitive = platform.graph.get_all_transitive(dep.dependency_id)
            if transitive:
                print(f"\n  {dep.name}@{dep.version}")
                for t_id in transitive:
                    t_dep = platform.graph.dependencies.get(t_id)
                    if t_dep:
                        print(f"    └── {t_dep.name}@{t_dep.version}")
                        
    # Generate SBOM
    print("\n📄 Generating SBOM...")
    
    sbom = platform.sbom_generator.generate("my-application", dependencies)
    
    print(f"\n  Format: {sbom['bomFormat']}")
    print(f"  Spec Version: {sbom['specVersion']}")
    print(f"  Components: {len(sbom['components'])}")
    
    # Update recommendations
    print("\n🔄 Update Recommendations:")
    
    updates = [
        UpdateRecommendation(
            recommendation_id="rec1",
            dependency_name="lodash",
            current_version="4.17.21",
            recommended_version="4.17.22",
            latest_version="4.17.22",
            update_status=UpdateStatus.PATCH_AVAILABLE,
            breaking_changes=False
        ),
        UpdateRecommendation(
            recommendation_id="rec2",
            dependency_name="moment",
            current_version="2.29.4",
            recommended_version="dayjs",
            latest_version="2.29.4",
            update_status=UpdateStatus.DEPRECATED,
            breaking_changes=True
        ),
    ]
    
    for rec in updates:
        icon = "🟢" if rec.update_status == UpdateStatus.UP_TO_DATE else ("🟡" if not rec.breaking_changes else "🔴")
        print(f"\n  {icon} {rec.dependency_name}")
        print(f"     Current: {rec.current_version}")
        print(f"     Recommended: {rec.recommended_version}")
        print(f"     Status: {rec.update_status.value.replace('_', ' ').title()}")
        if rec.breaking_changes:
            print(f"     ⚠️ Breaking changes expected")
            
    # Platform statistics
    print("\n📊 Platform Statistics:")
    
    stats = platform.get_statistics()
    
    print(f"\n  Total Dependencies: {stats['total_dependencies']}")
    
    print("\n  By Type:")
    for dtype, count in stats['by_type'].items():
        if count > 0:
            print(f"    • {dtype}: {count}")
            
    print("\n  By License:")
    for lic, count in stats['by_license'].items():
        print(f"    • {lic}: {count}")
        
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                 Dependency Management Dashboard                    │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Dependencies:            {stats['total_dependencies']:>10}                     │")
    print(f"│ Direct Dependencies:           {stats['by_type'].get('direct', 0):>10}                     │")
    print(f"│ Dev Dependencies:              {stats['by_type'].get('dev', 0):>10}                     │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Vulnerabilities Found:         {len(found_vulns):>10}                     │")
    print(f"│ License Compliant:             {len(results['compliant']):>10}                     │")
    print(f"│ Updates Available:             {len(updates):>10}                     │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Dependency Management Platform initialized!")
    print("=" * 60)
