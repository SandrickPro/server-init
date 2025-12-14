#!/usr/bin/env python3
"""
Server Init - Iteration 296: Dependency Tracker Platform
Платформа отслеживания зависимостей

Функционал:
- Dependency Discovery - обнаружение зависимостей
- Version Tracking - отслеживание версий
- Vulnerability Scanning - сканирование уязвимостей
- License Compliance - соответствие лицензий
- Update Management - управление обновлениями
- Dependency Graph - граф зависимостей
- Security Alerts - алерты безопасности
- Impact Analysis - анализ влияния
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
    PEER = "peer"


class LicenseType(Enum):
    """Тип лицензии"""
    MIT = "MIT"
    APACHE_2 = "Apache-2.0"
    GPL_2 = "GPL-2.0"
    GPL_3 = "GPL-3.0"
    BSD_3 = "BSD-3-Clause"
    ISC = "ISC"
    UNLICENSED = "Unlicensed"
    PROPRIETARY = "Proprietary"


class VulnerabilitySeverity(Enum):
    """Серьёзность уязвимости"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class UpdateType(Enum):
    """Тип обновления"""
    PATCH = "patch"
    MINOR = "minor"
    MAJOR = "major"
    SECURITY = "security"


class RiskLevel(Enum):
    """Уровень риска"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Dependency:
    """Зависимость"""
    dep_id: str
    name: str
    
    # Version
    current_version: str = "1.0.0"
    latest_version: str = "1.0.0"
    
    # Type
    dep_type: DependencyType = DependencyType.DIRECT
    
    # License
    license: LicenseType = LicenseType.MIT
    
    # Source
    registry: str = "npm"
    repository: str = ""
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    
    # Status
    outdated: bool = False
    deprecated: bool = False
    
    # Timestamps
    installed_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Vulnerability:
    """Уязвимость"""
    vuln_id: str
    cve_id: str
    
    # Affected
    dependency_name: str
    affected_versions: str = ""
    
    # Details
    title: str = ""
    description: str = ""
    severity: VulnerabilitySeverity = VulnerabilitySeverity.MEDIUM
    
    # Fix
    fixed_version: Optional[str] = None
    patch_available: bool = False
    
    # Risk
    cvss_score: float = 0.0
    exploitable: bool = False
    
    # Status
    resolved: bool = False
    
    discovered_at: datetime = field(default_factory=datetime.now)


@dataclass
class Update:
    """Обновление"""
    update_id: str
    dependency_name: str
    
    # Versions
    from_version: str = ""
    to_version: str = ""
    update_type: UpdateType = UpdateType.MINOR
    
    # Changes
    changelog: str = ""
    breaking_changes: bool = False
    
    # Risk
    risk_level: RiskLevel = RiskLevel.LOW
    
    # Status
    applied: bool = False
    tested: bool = False
    
    available_since: datetime = field(default_factory=datetime.now)


@dataclass
class LicenseIssue:
    """Проблема лицензии"""
    issue_id: str
    dependency_name: str
    
    # License
    license: LicenseType
    
    # Issue
    issue_type: str = ""
    description: str = ""
    
    # Compliance
    compliant: bool = False
    requires_attribution: bool = False
    allows_commercial: bool = True
    
    # Resolution
    resolved: bool = False


@dataclass
class Project:
    """Проект"""
    project_id: str
    name: str
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    
    # Stats
    total_deps: int = 0
    direct_deps: int = 0
    transitive_deps: int = 0
    
    # Health
    vulnerabilities: int = 0
    outdated: int = 0
    
    created_at: datetime = field(default_factory=datetime.now)


class DependencyTrackerManager:
    """Менеджер Dependency Tracker"""
    
    def __init__(self):
        self.dependencies: Dict[str, Dependency] = {}
        self.vulnerabilities: Dict[str, Vulnerability] = {}
        self.updates: Dict[str, Update] = {}
        self.license_issues: Dict[str, LicenseIssue] = {}
        self.projects: Dict[str, Project] = {}
        
        # Stats
        self.scans_completed: int = 0
        self.updates_applied: int = 0
        
    async def create_project(self, name: str) -> Project:
        """Создание проекта"""
        project = Project(
            project_id=f"proj_{uuid.uuid4().hex[:8]}",
            name=name
        )
        
        self.projects[project.project_id] = project
        return project
        
    async def add_dependency(self, name: str,
                            version: str,
                            dep_type: DependencyType = DependencyType.DIRECT,
                            license_type: LicenseType = LicenseType.MIT,
                            registry: str = "npm") -> Dependency:
        """Добавление зависимости"""
        dep = Dependency(
            dep_id=f"dep_{uuid.uuid4().hex[:8]}",
            name=name,
            current_version=version,
            latest_version=self._generate_latest_version(version),
            dep_type=dep_type,
            license=license_type,
            registry=registry
        )
        
        dep.outdated = dep.current_version != dep.latest_version
        
        self.dependencies[dep.dep_id] = dep
        return dep
        
    def _generate_latest_version(self, current: str) -> str:
        """Генерация последней версии"""
        try:
            parts = current.split(".")
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2]) if len(parts) > 2 else 0
            
            # Random update type
            update = random.choice(["none", "patch", "minor", "major"])
            
            if update == "patch":
                patch += random.randint(1, 5)
            elif update == "minor":
                minor += random.randint(1, 3)
                patch = 0
            elif update == "major":
                major += 1
                minor = 0
                patch = 0
                
            return f"{major}.{minor}.{patch}"
        except:
            return current
            
    async def add_transitive_deps(self, dep_id: str, count: int = 3) -> List[Dependency]:
        """Добавление транзитивных зависимостей"""
        parent = self.dependencies.get(dep_id)
        if not parent:
            return []
            
        trans_deps = []
        
        for i in range(count):
            name = f"{parent.name}-dep-{i+1}"
            version = f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}"
            
            dep = await self.add_dependency(
                name,
                version,
                DependencyType.TRANSITIVE,
                random.choice(list(LicenseType)),
                parent.registry
            )
            
            parent.dependencies.append(dep.dep_id)
            dep.dependents.append(parent.dep_id)
            trans_deps.append(dep)
            
        return trans_deps
        
    async def scan_vulnerabilities(self) -> List[Vulnerability]:
        """Сканирование уязвимостей"""
        self.scans_completed += 1
        found = []
        
        for dep in self.dependencies.values():
            # Random chance of vulnerability
            if random.random() < 0.15:
                severity = random.choice(list(VulnerabilitySeverity))
                
                vuln = Vulnerability(
                    vuln_id=f"vuln_{uuid.uuid4().hex[:8]}",
                    cve_id=f"CVE-{datetime.now().year}-{random.randint(10000, 99999)}",
                    dependency_name=dep.name,
                    affected_versions=f"< {dep.latest_version}",
                    title=f"Security issue in {dep.name}",
                    description=f"Potential {severity.value} security vulnerability",
                    severity=severity,
                    fixed_version=dep.latest_version,
                    patch_available=random.random() > 0.3,
                    cvss_score=random.uniform(1, 10),
                    exploitable=random.random() > 0.7
                )
                
                self.vulnerabilities[vuln.vuln_id] = vuln
                found.append(vuln)
                
        return found
        
    async def check_licenses(self) -> List[LicenseIssue]:
        """Проверка лицензий"""
        issues = []
        
        problematic = [LicenseType.GPL_2, LicenseType.GPL_3, LicenseType.PROPRIETARY, LicenseType.UNLICENSED]
        
        for dep in self.dependencies.values():
            if dep.license in problematic:
                issue = LicenseIssue(
                    issue_id=f"lic_{uuid.uuid4().hex[:8]}",
                    dependency_name=dep.name,
                    license=dep.license,
                    issue_type="compatibility",
                    description=f"{dep.license.value} license may have restrictions",
                    compliant=dep.license not in [LicenseType.UNLICENSED, LicenseType.PROPRIETARY],
                    requires_attribution=dep.license in [LicenseType.MIT, LicenseType.BSD_3, LicenseType.APACHE_2],
                    allows_commercial=dep.license not in [LicenseType.GPL_2, LicenseType.GPL_3]
                )
                
                self.license_issues[issue.issue_id] = issue
                issues.append(issue)
                
        return issues
        
    async def check_updates(self) -> List[Update]:
        """Проверка обновлений"""
        updates = []
        
        for dep in self.dependencies.values():
            if dep.outdated:
                update_type = self._determine_update_type(dep.current_version, dep.latest_version)
                
                update = Update(
                    update_id=f"upd_{uuid.uuid4().hex[:8]}",
                    dependency_name=dep.name,
                    from_version=dep.current_version,
                    to_version=dep.latest_version,
                    update_type=update_type,
                    changelog=f"Various improvements and fixes",
                    breaking_changes=update_type == UpdateType.MAJOR,
                    risk_level=self._assess_update_risk(update_type)
                )
                
                self.updates[update.update_id] = update
                updates.append(update)
                
        return updates
        
    def _determine_update_type(self, current: str, latest: str) -> UpdateType:
        """Определение типа обновления"""
        try:
            curr = [int(x) for x in current.split(".")[:3]]
            lat = [int(x) for x in latest.split(".")[:3]]
            
            while len(curr) < 3:
                curr.append(0)
            while len(lat) < 3:
                lat.append(0)
                
            if lat[0] > curr[0]:
                return UpdateType.MAJOR
            elif lat[1] > curr[1]:
                return UpdateType.MINOR
            else:
                return UpdateType.PATCH
        except:
            return UpdateType.PATCH
            
    def _assess_update_risk(self, update_type: UpdateType) -> RiskLevel:
        """Оценка риска обновления"""
        risk_map = {
            UpdateType.PATCH: RiskLevel.LOW,
            UpdateType.MINOR: RiskLevel.MEDIUM,
            UpdateType.MAJOR: RiskLevel.HIGH,
            UpdateType.SECURITY: RiskLevel.CRITICAL
        }
        return risk_map.get(update_type, RiskLevel.LOW)
        
    async def apply_update(self, update_id: str) -> bool:
        """Применение обновления"""
        update = self.updates.get(update_id)
        if not update or update.applied:
            return False
            
        # Find dependency
        dep = None
        for d in self.dependencies.values():
            if d.name == update.dependency_name:
                dep = d
                break
                
        if dep:
            dep.current_version = update.to_version
            dep.outdated = dep.current_version != dep.latest_version
            dep.updated_at = datetime.now()
            
        update.applied = True
        update.tested = True
        self.updates_applied += 1
        
        return True
        
    async def get_dependency_graph(self) -> Dict[str, List[str]]:
        """Получение графа зависимостей"""
        graph = {}
        
        for dep in self.dependencies.values():
            graph[dep.name] = [
                self.dependencies[d_id].name 
                for d_id in dep.dependencies 
                if d_id in self.dependencies
            ]
            
        return graph
        
    async def analyze_impact(self, dep_name: str) -> Dict[str, Any]:
        """Анализ влияния"""
        dep = None
        for d in self.dependencies.values():
            if d.name == dep_name:
                dep = d
                break
                
        if not dep:
            return {}
            
        # Find all dependents
        dependents = set()
        to_check = [dep.dep_id]
        
        while to_check:
            current_id = to_check.pop()
            current = self.dependencies.get(current_id)
            
            if current:
                for d in self.dependencies.values():
                    if current.dep_id in d.dependencies and d.dep_id not in dependents:
                        dependents.add(d.dep_id)
                        to_check.append(d.dep_id)
                        
        # Get vulnerabilities
        vulns = [v for v in self.vulnerabilities.values() if v.dependency_name == dep_name]
        
        return {
            "dependency": dep_name,
            "version": dep.current_version,
            "type": dep.dep_type.value,
            "direct_dependents": len(dep.dependents),
            "total_impact": len(dependents),
            "vulnerabilities": len(vulns),
            "outdated": dep.outdated,
            "license": dep.license.value
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        outdated = sum(1 for d in self.dependencies.values() if d.outdated)
        deprecated = sum(1 for d in self.dependencies.values() if d.deprecated)
        direct = sum(1 for d in self.dependencies.values() if d.dep_type == DependencyType.DIRECT)
        transitive = sum(1 for d in self.dependencies.values() if d.dep_type == DependencyType.TRANSITIVE)
        
        critical_vulns = sum(1 for v in self.vulnerabilities.values() 
                           if v.severity == VulnerabilitySeverity.CRITICAL and not v.resolved)
        high_vulns = sum(1 for v in self.vulnerabilities.values()
                        if v.severity == VulnerabilitySeverity.HIGH and not v.resolved)
                        
        pending_updates = sum(1 for u in self.updates.values() if not u.applied)
        license_problems = sum(1 for l in self.license_issues.values() if not l.resolved)
        
        return {
            "total_dependencies": len(self.dependencies),
            "direct_dependencies": direct,
            "transitive_dependencies": transitive,
            "outdated_deps": outdated,
            "deprecated_deps": deprecated,
            "total_vulnerabilities": len(self.vulnerabilities),
            "critical_vulnerabilities": critical_vulns,
            "high_vulnerabilities": high_vulns,
            "pending_updates": pending_updates,
            "license_issues": license_problems,
            "scans_completed": self.scans_completed,
            "updates_applied": self.updates_applied
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 296: Dependency Tracker Platform")
    print("=" * 60)
    
    manager = DependencyTrackerManager()
    print("✓ Dependency Tracker Manager created")
    
    # Create project
    print("\n📦 Creating Project...")
    
    project = await manager.create_project("web-application")
    print(f"  📦 Project: {project.name}")
    
    # Add dependencies
    print("\n📦 Adding Dependencies...")
    
    deps_data = [
        ("react", "18.2.0", DependencyType.DIRECT, LicenseType.MIT),
        ("typescript", "5.0.0", DependencyType.DEV, LicenseType.APACHE_2),
        ("webpack", "5.75.0", DependencyType.DEV, LicenseType.MIT),
        ("express", "4.18.0", DependencyType.DIRECT, LicenseType.MIT),
        ("lodash", "4.17.21", DependencyType.DIRECT, LicenseType.MIT),
        ("axios", "1.3.0", DependencyType.DIRECT, LicenseType.MIT),
        ("moment", "2.29.0", DependencyType.DIRECT, LicenseType.MIT),
        ("uuid", "9.0.0", DependencyType.DIRECT, LicenseType.MIT),
        ("jsonwebtoken", "9.0.0", DependencyType.DIRECT, LicenseType.MIT),
        ("redis", "4.5.0", DependencyType.DIRECT, LicenseType.MIT),
        ("gpl-module", "1.0.0", DependencyType.DIRECT, LicenseType.GPL_3),
        ("proprietary-lib", "2.0.0", DependencyType.DIRECT, LicenseType.PROPRIETARY)
    ]
    
    main_deps = []
    for name, version, dep_type, license_type in deps_data:
        dep = await manager.add_dependency(name, version, dep_type, license_type)
        main_deps.append(dep)
        project.dependencies.append(dep.dep_id)
        
        status = "⚠️" if dep.outdated else "✅"
        print(f"  {status} {name}@{version} [{dep_type.value}] ({license_type.value})")
        
    # Add transitive dependencies
    print("\n🔗 Adding Transitive Dependencies...")
    
    trans_count = 0
    for dep in main_deps[:5]:
        trans_deps = await manager.add_transitive_deps(dep.dep_id, random.randint(2, 4))
        trans_count += len(trans_deps)
        
    print(f"  📦 Added {trans_count} transitive dependencies")
    
    # Scan vulnerabilities
    print("\n🔍 Scanning Vulnerabilities...")
    
    vulnerabilities = await manager.scan_vulnerabilities()
    
    if vulnerabilities:
        print(f"\n  ⚠️ Found {len(vulnerabilities)} vulnerabilities:")
        
        severity_order = {
            VulnerabilitySeverity.CRITICAL: 0,
            VulnerabilitySeverity.HIGH: 1,
            VulnerabilitySeverity.MEDIUM: 2,
            VulnerabilitySeverity.LOW: 3
        }
        
        for vuln in sorted(vulnerabilities, key=lambda x: severity_order.get(x.severity, 4))[:8]:
            severity_icons = {
                VulnerabilitySeverity.CRITICAL: "🔴",
                VulnerabilitySeverity.HIGH: "🟠",
                VulnerabilitySeverity.MEDIUM: "🟡",
                VulnerabilitySeverity.LOW: "🟢"
            }
            icon = severity_icons.get(vuln.severity, "⚪")
            
            print(f"\n  {icon} [{vuln.severity.value.upper()}] {vuln.cve_id}")
            print(f"     Package: {vuln.dependency_name}")
            print(f"     Affected: {vuln.affected_versions}")
            print(f"     CVSS: {vuln.cvss_score:.1f}")
            
            if vuln.patch_available:
                print(f"     Fix: Update to {vuln.fixed_version}")
    else:
        print("  ✅ No vulnerabilities found")
        
    # Check licenses
    print("\n📜 Checking Licenses...")
    
    license_issues = await manager.check_licenses()
    
    if license_issues:
        print(f"\n  ⚠️ Found {len(license_issues)} license issues:")
        
        for issue in license_issues[:5]:
            commercial = "✅" if issue.allows_commercial else "❌"
            compliant = "✅" if issue.compliant else "❌"
            
            print(f"\n  📜 {issue.dependency_name} ({issue.license.value})")
            print(f"     Compliant: {compliant} | Commercial Use: {commercial}")
            print(f"     Issue: {issue.description}")
    else:
        print("  ✅ No license issues found")
        
    # Check updates
    print("\n🔄 Checking Updates...")
    
    updates = await manager.check_updates()
    
    if updates:
        print(f"\n  📦 {len(updates)} updates available:")
        
        print("\n  ┌────────────────────────┬────────────┬────────────┬────────────┬──────────┐")
        print("  │ Package                │ Current    │ Latest     │ Type       │ Risk     │")
        print("  ├────────────────────────┼────────────┼────────────┼────────────┼──────────┤")
        
        for update in sorted(updates, key=lambda x: x.risk_level.value, reverse=True)[:10]:
            name = update.dependency_name[:22].ljust(22)
            current = update.from_version[:10].ljust(10)
            latest = update.to_version[:10].ljust(10)
            utype = update.update_type.value[:10].ljust(10)
            
            risk_colors = {
                RiskLevel.LOW: "🟢",
                RiskLevel.MEDIUM: "🟡",
                RiskLevel.HIGH: "🟠",
                RiskLevel.CRITICAL: "🔴"
            }
            risk = f"{risk_colors.get(update.risk_level, '⚪')} {update.risk_level.value}".ljust(8)
            
            print(f"  │ {name} │ {current} │ {latest} │ {utype} │ {risk} │")
            
        print("  └────────────────────────┴────────────┴────────────┴────────────┴──────────┘")
        
    # Apply some updates
    print("\n⬆️ Applying Security Updates...")
    
    applied = 0
    for update in updates:
        if update.update_type == UpdateType.SECURITY or update.risk_level == RiskLevel.LOW:
            if await manager.apply_update(update.update_id):
                applied += 1
                if applied >= 3:
                    break
                    
    print(f"  ✅ Applied {applied} updates")
    
    # Dependency graph
    print("\n🕸️ Dependency Graph:")
    
    graph = await manager.get_dependency_graph()
    
    for name, deps in list(graph.items())[:6]:
        if deps:
            print(f"\n  📦 {name}")
            for d in deps[:3]:
                print(f"     └── {d}")
                
    # Impact analysis
    print("\n📊 Impact Analysis:")
    
    for dep in main_deps[:4]:
        impact = await manager.analyze_impact(dep.name)
        
        if impact:
            print(f"\n  📦 {impact['dependency']}")
            print(f"     Version: {impact['version']}")
            print(f"     Type: {impact['type']}")
            print(f"     Direct Dependents: {impact['direct_dependents']}")
            print(f"     Total Impact: {impact['total_impact']} packages")
            print(f"     Vulnerabilities: {impact['vulnerabilities']}")
            
    # License summary
    print("\n📜 License Summary:")
    
    license_counts: Dict[str, int] = {}
    for dep in manager.dependencies.values():
        lic = dep.license.value
        license_counts[lic] = license_counts.get(lic, 0) + 1
        
    for lic, count in sorted(license_counts.items(), key=lambda x: x[1], reverse=True)[:6]:
        bar_len = min(count * 2, 20)
        bar = "█" * bar_len
        print(f"  {lic:15} {bar} {count}")
        
    # Statistics
    print("\n📊 Dependency Tracker Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Total Dependencies: {stats['total_dependencies']}")
    print(f"    Direct: {stats['direct_dependencies']}")
    print(f"    Transitive: {stats['transitive_dependencies']}")
    print(f"\n  Outdated: {stats['outdated_deps']}")
    print(f"  Deprecated: {stats['deprecated_deps']}")
    print(f"\n  Vulnerabilities: {stats['total_vulnerabilities']}")
    print(f"    Critical: {stats['critical_vulnerabilities']}")
    print(f"    High: {stats['high_vulnerabilities']}")
    print(f"\n  Pending Updates: {stats['pending_updates']}")
    print(f"  License Issues: {stats['license_issues']}")
    
    # Health score
    vuln_penalty = (stats['critical_vulnerabilities'] * 20 + stats['high_vulnerabilities'] * 10)
    outdated_penalty = stats['outdated_deps'] * 2
    license_penalty = stats['license_issues'] * 5
    
    health_score = max(0, 100 - vuln_penalty - outdated_penalty - license_penalty)
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Dependency Tracker Dashboard                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Dependencies:            {stats['total_dependencies']:>12}                        │")
    print(f"│ Outdated Packages:             {stats['outdated_deps']:>12}                        │")
    print(f"│ Vulnerabilities:               {stats['total_vulnerabilities']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Critical Vulnerabilities:      {stats['critical_vulnerabilities']:>12}                        │")
    print(f"│ High Vulnerabilities:          {stats['high_vulnerabilities']:>12}                        │")
    print(f"│ License Issues:                {stats['license_issues']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Health Score:                  {health_score:>11.0f}%                        │")
    print(f"│ Updates Applied:               {stats['updates_applied']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Dependency Tracker Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
