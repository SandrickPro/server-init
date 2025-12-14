#!/usr/bin/env python3
"""
Server Init - Iteration 176: Release Management Platform
Платформа управления релизами

Функционал:
- Release Planning - планирование релизов
- Version Control - контроль версий
- Changelog Generation - генерация changelog
- Release Automation - автоматизация релизов
- Rollback Management - управление откатами
- Feature Toggles Integration - интеграция с feature flags
- Release Approval - согласование релизов
- Deployment Orchestration - оркестрация деплоя
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import re


class ReleaseStatus(Enum):
    """Статус релиза"""
    DRAFT = "draft"
    PLANNED = "planned"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    DEPLOYED = "deployed"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"


class ReleaseType(Enum):
    """Тип релиза"""
    MAJOR = "major"  # Breaking changes
    MINOR = "minor"  # New features
    PATCH = "patch"  # Bug fixes
    HOTFIX = "hotfix"  # Critical fixes
    PRE_RELEASE = "pre_release"  # Alpha/Beta


class ChangeType(Enum):
    """Тип изменения"""
    FEATURE = "feature"
    BUGFIX = "bugfix"
    IMPROVEMENT = "improvement"
    SECURITY = "security"
    BREAKING = "breaking"
    DEPRECATED = "deprecated"
    REMOVED = "removed"
    DOCUMENTATION = "documentation"


class ApprovalStatus(Enum):
    """Статус согласования"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    WAIVED = "waived"


class DeploymentEnvironment(Enum):
    """Среда развёртывания"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    CANARY = "canary"


@dataclass
class SemanticVersion:
    """Семантическая версия"""
    major: int = 0
    minor: int = 0
    patch: int = 0
    pre_release: str = ""  # alpha, beta, rc
    build_metadata: str = ""
    
    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.pre_release:
            version += f"-{self.pre_release}"
        if self.build_metadata:
            version += f"+{self.build_metadata}"
        return version
        
    @classmethod
    def parse(cls, version_str: str) -> "SemanticVersion":
        """Парсинг строки версии"""
        pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.]+))?(?:\+([a-zA-Z0-9.]+))?$"
        match = re.match(pattern, version_str)
        if match:
            return cls(
                major=int(match.group(1)),
                minor=int(match.group(2)),
                patch=int(match.group(3)),
                pre_release=match.group(4) or "",
                build_metadata=match.group(5) or ""
            )
        return cls()
        
    def bump(self, release_type: ReleaseType) -> "SemanticVersion":
        """Увеличение версии"""
        if release_type == ReleaseType.MAJOR:
            return SemanticVersion(self.major + 1, 0, 0)
        elif release_type in [ReleaseType.MINOR]:
            return SemanticVersion(self.major, self.minor + 1, 0)
        elif release_type in [ReleaseType.PATCH, ReleaseType.HOTFIX]:
            return SemanticVersion(self.major, self.minor, self.patch + 1)
        elif release_type == ReleaseType.PRE_RELEASE:
            return SemanticVersion(self.major, self.minor + 1, 0, "alpha.1")
        return self


@dataclass
class ChangelogEntry:
    """Запись в changelog"""
    entry_id: str
    change_type: ChangeType = ChangeType.FEATURE
    
    # Description
    title: str = ""
    description: str = ""
    
    # References
    issue_ids: List[str] = field(default_factory=list)
    pull_request_id: str = ""
    commit_sha: str = ""
    
    # Attribution
    author: str = ""
    
    # Metadata
    breaking_change: bool = False
    security_fix: bool = False


@dataclass
class ReleaseApproval:
    """Согласование релиза"""
    approval_id: str
    release_id: str = ""
    
    # Approver
    approver: str = ""
    role: str = ""  # tech-lead, qa, security, product
    
    # Status
    status: ApprovalStatus = ApprovalStatus.PENDING
    
    # Details
    comments: str = ""
    conditions: List[str] = field(default_factory=list)
    
    # Timing
    requested_at: datetime = field(default_factory=datetime.now)
    responded_at: Optional[datetime] = None


@dataclass
class ReleaseArtifact:
    """Артефакт релиза"""
    artifact_id: str
    name: str = ""
    
    # Type
    artifact_type: str = ""  # docker-image, binary, package
    
    # Location
    registry: str = ""
    repository: str = ""
    tag: str = ""
    checksum: str = ""
    
    # Size
    size_bytes: int = 0
    
    # Build info
    built_at: datetime = field(default_factory=datetime.now)
    build_id: str = ""


@dataclass
class Release:
    """Релиз"""
    release_id: str
    name: str = ""
    description: str = ""
    
    # Version
    version: SemanticVersion = field(default_factory=SemanticVersion)
    previous_version: Optional[SemanticVersion] = None
    release_type: ReleaseType = ReleaseType.MINOR
    
    # Status
    status: ReleaseStatus = ReleaseStatus.DRAFT
    
    # Changelog
    changelog_entries: List[ChangelogEntry] = field(default_factory=list)
    
    # Artifacts
    artifacts: List[ReleaseArtifact] = field(default_factory=list)
    
    # Approvals
    approvals: List[ReleaseApproval] = field(default_factory=list)
    approval_required: bool = True
    
    # Deployment
    target_environments: List[DeploymentEnvironment] = field(default_factory=list)
    deployed_environments: List[DeploymentEnvironment] = field(default_factory=list)
    
    # Feature flags
    feature_flags: List[str] = field(default_factory=list)
    
    # Timing
    planned_date: Optional[datetime] = None
    released_at: Optional[datetime] = None
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""


@dataclass
class Deployment:
    """Развёртывание"""
    deployment_id: str
    release_id: str = ""
    
    # Target
    environment: DeploymentEnvironment = DeploymentEnvironment.STAGING
    
    # Status
    status: str = "pending"  # pending, in_progress, completed, failed, rolled_back
    progress_percent: float = 0.0
    
    # Strategy
    strategy: str = "rolling"  # rolling, blue-green, canary
    canary_percentage: int = 0
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    
    # Result
    instances_updated: int = 0
    instances_total: int = 0
    errors: List[str] = field(default_factory=list)


class VersionManager:
    """Менеджер версий"""
    
    def __init__(self):
        self.versions: Dict[str, SemanticVersion] = {}
        self.current_version = SemanticVersion(1, 0, 0)
        
    def get_current_version(self, service: str = "default") -> SemanticVersion:
        """Получение текущей версии"""
        return self.versions.get(service, self.current_version)
        
    def set_version(self, service: str, version: SemanticVersion):
        """Установка версии"""
        self.versions[service] = version
        
    def get_next_version(self, service: str, release_type: ReleaseType) -> SemanticVersion:
        """Получение следующей версии"""
        current = self.get_current_version(service)
        return current.bump(release_type)


class ChangelogGenerator:
    """Генератор changelog"""
    
    def generate(self, release: Release) -> str:
        """Генерация changelog"""
        lines = []
        
        # Header
        lines.append(f"# {release.name or 'Release'} {release.version}")
        lines.append("")
        lines.append(f"**Release Date:** {release.planned_date or datetime.now().strftime('%Y-%m-%d')}")
        lines.append("")
        
        if release.description:
            lines.append(release.description)
            lines.append("")
            
        # Group by type
        entries_by_type: Dict[ChangeType, List[ChangelogEntry]] = {}
        for entry in release.changelog_entries:
            if entry.change_type not in entries_by_type:
                entries_by_type[entry.change_type] = []
            entries_by_type[entry.change_type].append(entry)
            
        # Breaking changes first
        if ChangeType.BREAKING in entries_by_type:
            lines.append("## ⚠️ Breaking Changes")
            lines.append("")
            for entry in entries_by_type[ChangeType.BREAKING]:
                lines.append(f"- **{entry.title}** - {entry.description}")
            lines.append("")
            
        # Features
        if ChangeType.FEATURE in entries_by_type:
            lines.append("## ✨ New Features")
            lines.append("")
            for entry in entries_by_type[ChangeType.FEATURE]:
                refs = ", ".join(entry.issue_ids) if entry.issue_ids else ""
                lines.append(f"- {entry.title} ({refs})")
            lines.append("")
            
        # Improvements
        if ChangeType.IMPROVEMENT in entries_by_type:
            lines.append("## 🔧 Improvements")
            lines.append("")
            for entry in entries_by_type[ChangeType.IMPROVEMENT]:
                lines.append(f"- {entry.title}")
            lines.append("")
            
        # Bug fixes
        if ChangeType.BUGFIX in entries_by_type:
            lines.append("## 🐛 Bug Fixes")
            lines.append("")
            for entry in entries_by_type[ChangeType.BUGFIX]:
                lines.append(f"- {entry.title}")
            lines.append("")
            
        # Security
        if ChangeType.SECURITY in entries_by_type:
            lines.append("## 🔒 Security")
            lines.append("")
            for entry in entries_by_type[ChangeType.SECURITY]:
                lines.append(f"- {entry.title}")
            lines.append("")
            
        return "\n".join(lines)


class ApprovalWorkflow:
    """Workflow согласования"""
    
    def __init__(self):
        self.required_approvers: Dict[str, List[str]] = {
            "hotfix": ["tech-lead"],
            "patch": ["tech-lead", "qa"],
            "minor": ["tech-lead", "qa", "product"],
            "major": ["tech-lead", "qa", "product", "security"]
        }
        
    def get_required_approvers(self, release: Release) -> List[str]:
        """Получение списка необходимых approvers"""
        return self.required_approvers.get(release.release_type.value, [])
        
    def check_approval_status(self, release: Release) -> Dict[str, Any]:
        """Проверка статуса согласования"""
        required = set(self.get_required_approvers(release))
        approved_by = set()
        pending = set()
        rejected = False
        
        for approval in release.approvals:
            if approval.status == ApprovalStatus.APPROVED:
                approved_by.add(approval.role)
            elif approval.status == ApprovalStatus.REJECTED:
                rejected = True
            elif approval.status == ApprovalStatus.PENDING:
                pending.add(approval.role)
                
        missing = required - approved_by
        
        return {
            "required": list(required),
            "approved": list(approved_by),
            "pending": list(pending),
            "missing": list(missing),
            "rejected": rejected,
            "fully_approved": len(missing) == 0 and not rejected
        }


class DeploymentOrchestrator:
    """Оркестратор развёртывания"""
    
    def __init__(self):
        self.deployments: Dict[str, Deployment] = {}
        
    async def deploy(
        self,
        release: Release,
        environment: DeploymentEnvironment,
        strategy: str = "rolling"
    ) -> Deployment:
        """Развёртывание релиза"""
        deployment = Deployment(
            deployment_id=f"deploy_{uuid.uuid4().hex[:8]}",
            release_id=release.release_id,
            environment=environment,
            strategy=strategy,
            status="in_progress",
            started_at=datetime.now(),
            instances_total=random.randint(3, 10)
        )
        
        self.deployments[deployment.deployment_id] = deployment
        
        # Simulate deployment
        for i in range(deployment.instances_total):
            await asyncio.sleep(0.02)
            deployment.instances_updated = i + 1
            deployment.progress_percent = (i + 1) / deployment.instances_total * 100
            
        deployment.completed_at = datetime.now()
        deployment.duration_seconds = (deployment.completed_at - deployment.started_at).total_seconds()
        
        # 95% success rate
        if random.random() < 0.95:
            deployment.status = "completed"
            release.deployed_environments.append(environment)
        else:
            deployment.status = "failed"
            deployment.errors.append("Health check failed on instance")
            
        return deployment
        
    async def rollback(self, deployment_id: str) -> bool:
        """Откат развёртывания"""
        deployment = self.deployments.get(deployment_id)
        if not deployment:
            return False
            
        await asyncio.sleep(0.05)
        
        deployment.status = "rolled_back"
        return True


class ReleaseManager:
    """Менеджер релизов"""
    
    def __init__(self):
        self.releases: Dict[str, Release] = {}
        self.version_manager = VersionManager()
        self.changelog_generator = ChangelogGenerator()
        self.approval_workflow = ApprovalWorkflow()
        self.orchestrator = DeploymentOrchestrator()
        
    def create_release(
        self,
        release_type: ReleaseType,
        name: str = "",
        description: str = ""
    ) -> Release:
        """Создание релиза"""
        current = self.version_manager.get_current_version()
        next_version = self.version_manager.get_next_version("default", release_type)
        
        release = Release(
            release_id=f"release_{uuid.uuid4().hex[:8]}",
            name=name or f"Release {next_version}",
            description=description,
            version=next_version,
            previous_version=current,
            release_type=release_type,
            status=ReleaseStatus.DRAFT
        )
        
        self.releases[release.release_id] = release
        return release
        
    def add_changelog_entry(self, release_id: str, entry: ChangelogEntry):
        """Добавление записи в changelog"""
        release = self.releases.get(release_id)
        if release:
            release.changelog_entries.append(entry)
            
    def request_approval(self, release_id: str, approver: str, role: str) -> ReleaseApproval:
        """Запрос согласования"""
        release = self.releases.get(release_id)
        if not release:
            return None
            
        approval = ReleaseApproval(
            approval_id=f"approval_{uuid.uuid4().hex[:8]}",
            release_id=release_id,
            approver=approver,
            role=role,
            status=ApprovalStatus.PENDING
        )
        
        release.approvals.append(approval)
        return approval
        
    def approve(self, approval_id: str, comments: str = "") -> bool:
        """Согласование"""
        for release in self.releases.values():
            for approval in release.approvals:
                if approval.approval_id == approval_id:
                    approval.status = ApprovalStatus.APPROVED
                    approval.comments = comments
                    approval.responded_at = datetime.now()
                    
                    # Check if fully approved
                    status = self.approval_workflow.check_approval_status(release)
                    if status["fully_approved"]:
                        release.status = ReleaseStatus.APPROVED
                        
                    return True
        return False
        
    async def deploy_release(
        self,
        release_id: str,
        environment: DeploymentEnvironment
    ) -> Optional[Deployment]:
        """Развёртывание релиза"""
        release = self.releases.get(release_id)
        if not release:
            return None
            
        release.status = ReleaseStatus.IN_PROGRESS
        
        deployment = await self.orchestrator.deploy(release, environment)
        
        if deployment.status == "completed":
            if environment == DeploymentEnvironment.PRODUCTION:
                release.status = ReleaseStatus.DEPLOYED
                release.released_at = datetime.now()
                self.version_manager.set_version("default", release.version)
                
        return deployment


class ReleasePipeline:
    """Pipeline релиза"""
    
    def __init__(self, release_manager: ReleaseManager):
        self.release_manager = release_manager
        
    async def run_pipeline(self, release: Release) -> Dict[str, Any]:
        """Запуск pipeline"""
        results = {
            "release_id": release.release_id,
            "stages": [],
            "success": True
        }
        
        # Stage 1: Build artifacts
        stage = {"name": "Build Artifacts", "status": "success"}
        await asyncio.sleep(0.05)
        
        artifact = ReleaseArtifact(
            artifact_id=f"artifact_{uuid.uuid4().hex[:8]}",
            name=f"{release.name}-{release.version}",
            artifact_type="docker-image",
            registry="registry.company.com",
            repository="app",
            tag=str(release.version),
            size_bytes=random.randint(100_000_000, 500_000_000)
        )
        release.artifacts.append(artifact)
        results["stages"].append(stage)
        
        # Stage 2: Deploy to staging
        stage = {"name": "Deploy Staging", "status": "running"}
        deployment = await self.release_manager.deploy_release(
            release.release_id,
            DeploymentEnvironment.STAGING
        )
        stage["status"] = deployment.status if deployment else "failed"
        results["stages"].append(stage)
        
        if stage["status"] != "completed":
            results["success"] = False
            return results
            
        # Stage 3: Integration tests
        stage = {"name": "Integration Tests", "status": "success"}
        await asyncio.sleep(0.03)
        results["stages"].append(stage)
        
        # Stage 4: Deploy to production (if approved)
        approval_status = self.release_manager.approval_workflow.check_approval_status(release)
        
        if approval_status["fully_approved"]:
            stage = {"name": "Deploy Production", "status": "running"}
            deployment = await self.release_manager.deploy_release(
                release.release_id,
                DeploymentEnvironment.PRODUCTION
            )
            stage["status"] = deployment.status if deployment else "failed"
        else:
            stage = {"name": "Deploy Production", "status": "pending_approval"}
            
        results["stages"].append(stage)
        
        return results


class ReleaseManagementPlatform:
    """Платформа управления релизами"""
    
    def __init__(self):
        self.release_manager = ReleaseManager()
        self.pipeline = ReleasePipeline(self.release_manager)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        releases = list(self.release_manager.releases.values())
        
        return {
            "total_releases": len(releases),
            "releases_by_status": {
                status.value: len([r for r in releases if r.status == status])
                for status in ReleaseStatus
            },
            "releases_by_type": {
                rtype.value: len([r for r in releases if r.release_type == rtype])
                for rtype in ReleaseType
            },
            "total_deployments": len(self.release_manager.orchestrator.deployments),
            "current_version": str(self.release_manager.version_manager.get_current_version())
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 176: Release Management Platform")
    print("=" * 60)
    
    async def demo():
        platform = ReleaseManagementPlatform()
        print("✓ Release Management Platform created")
        
        # Create releases
        print("\n📦 Creating Releases...")
        
        # Release 1: Minor release
        release1 = platform.release_manager.create_release(
            ReleaseType.MINOR,
            name="Feature Release",
            description="New features and improvements"
        )
        print(f"\n  Release: {release1.name}")
        print(f"  Version: {release1.version}")
        print(f"  Type: {release1.release_type.value}")
        
        # Add changelog entries
        print("\n  Adding changelog entries...")
        
        entries = [
            ChangelogEntry(
                entry_id="entry_1",
                change_type=ChangeType.FEATURE,
                title="New Dashboard UI",
                description="Completely redesigned dashboard",
                issue_ids=["#123", "#145"],
                author="john@company.com"
            ),
            ChangelogEntry(
                entry_id="entry_2",
                change_type=ChangeType.FEATURE,
                title="API Rate Limiting",
                description="Added configurable rate limits",
                issue_ids=["#167"],
                author="jane@company.com"
            ),
            ChangelogEntry(
                entry_id="entry_3",
                change_type=ChangeType.IMPROVEMENT,
                title="Performance Optimization",
                description="50% faster page loads",
                author="mike@company.com"
            ),
            ChangelogEntry(
                entry_id="entry_4",
                change_type=ChangeType.BUGFIX,
                title="Fixed login timeout",
                description="Session handling improvements",
                issue_ids=["#189"],
                author="sarah@company.com"
            ),
            ChangelogEntry(
                entry_id="entry_5",
                change_type=ChangeType.SECURITY,
                title="Updated dependencies",
                description="Security patches applied",
                security_fix=True,
                author="security@company.com"
            ),
        ]
        
        for entry in entries:
            platform.release_manager.add_changelog_entry(release1.release_id, entry)
            icon = {
                ChangeType.FEATURE: "✨",
                ChangeType.IMPROVEMENT: "🔧",
                ChangeType.BUGFIX: "🐛",
                ChangeType.SECURITY: "🔒"
            }.get(entry.change_type, "📝")
            print(f"    {icon} {entry.title}")
            
        # Generate changelog
        print("\n📄 Generated Changelog:")
        changelog = platform.release_manager.changelog_generator.generate(release1)
        
        for line in changelog.split("\n")[:20]:
            print(f"  {line}")
        print("  ...")
        
        # Request approvals
        print("\n✅ Requesting Approvals...")
        
        approvers = [
            ("alice@company.com", "tech-lead"),
            ("bob@company.com", "qa"),
            ("carol@company.com", "product")
        ]
        
        for approver, role in approvers:
            approval = platform.release_manager.request_approval(
                release1.release_id, approver, role
            )
            print(f"  • Requested from {approver} ({role})")
            
        # Check approval status
        status = platform.release_manager.approval_workflow.check_approval_status(release1)
        print(f"\n  Approval Status:")
        print(f"    Required: {', '.join(status['required'])}")
        print(f"    Pending: {', '.join(status['pending'])}")
        print(f"    Fully Approved: {status['fully_approved']}")
        
        # Approve release
        print("\n  Processing approvals...")
        
        for approval in release1.approvals:
            platform.release_manager.approve(approval.approval_id, "LGTM")
            print(f"    ✓ {approval.role} approved")
            
        status = platform.release_manager.approval_workflow.check_approval_status(release1)
        print(f"\n  Release Status: {release1.status.value}")
        print(f"  Fully Approved: {status['fully_approved']}")
        
        # Run release pipeline
        print("\n🚀 Running Release Pipeline...")
        
        results = await platform.pipeline.run_pipeline(release1)
        
        print("\n  Pipeline Stages:")
        for stage in results["stages"]:
            icon = "✓" if stage["status"] == "completed" or stage["status"] == "success" else "○"
            print(f"    {icon} {stage['name']}: {stage['status']}")
            
        print(f"\n  Pipeline Success: {results['success']}")
        
        # Show deployment details
        print("\n📊 Deployment Details:")
        
        for deployment in platform.release_manager.orchestrator.deployments.values():
            print(f"\n  Deployment: {deployment.deployment_id}")
            print(f"    Environment: {deployment.environment.value}")
            print(f"    Strategy: {deployment.strategy}")
            print(f"    Status: {deployment.status}")
            print(f"    Progress: {deployment.progress_percent:.0f}%")
            print(f"    Instances: {deployment.instances_updated}/{deployment.instances_total}")
            print(f"    Duration: {deployment.duration_seconds:.2f}s")
            
        # Release artifacts
        print("\n📦 Release Artifacts:")
        
        for artifact in release1.artifacts:
            print(f"\n  Artifact: {artifact.name}")
            print(f"    Type: {artifact.artifact_type}")
            print(f"    Registry: {artifact.registry}/{artifact.repository}:{artifact.tag}")
            print(f"    Size: {artifact.size_bytes / (1024**2):.1f} MB")
            
        # Create hotfix
        print("\n🔥 Creating Hotfix Release...")
        
        hotfix = platform.release_manager.create_release(
            ReleaseType.HOTFIX,
            name="Critical Security Hotfix",
            description="Emergency security patch"
        )
        
        platform.release_manager.add_changelog_entry(
            hotfix.release_id,
            ChangelogEntry(
                entry_id="hotfix_1",
                change_type=ChangeType.SECURITY,
                title="CVE-2024-XXXX Fix",
                description="Patched critical vulnerability",
                security_fix=True
            )
        )
        
        print(f"  Version: {hotfix.version}")
        print(f"  Previous: {hotfix.previous_version}")
        
        # Show version history
        print("\n📜 Version History:")
        
        print(f"\n  Current Version: {platform.release_manager.version_manager.get_current_version()}")
        
        print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐")
        print("  │ Release                          │ Version  │ Type     │ Status      │")
        print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────┤")
        
        for release in platform.release_manager.releases.values():
            name = release.name[:32].ljust(32)
            version = str(release.version)[:8].ljust(8)
            rtype = release.release_type.value[:8].ljust(8)
            
            status_icons = {
                ReleaseStatus.DEPLOYED: "🟢",
                ReleaseStatus.APPROVED: "✅",
                ReleaseStatus.IN_PROGRESS: "🟡",
                ReleaseStatus.DRAFT: "⚪"
            }
            status = f"{status_icons.get(release.status, '⚪')} {release.status.value}".ljust(12)
            print(f"  │ {name} │ {version} │ {rtype} │ {status} │")
            
        print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────┘")
        
        # Platform statistics
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Releases: {stats['total_releases']}")
        print(f"  Current Version: {stats['current_version']}")
        print(f"  Total Deployments: {stats['total_deployments']}")
        
        print("\n  By Status:")
        for status, count in stats['releases_by_status'].items():
            if count > 0:
                print(f"    • {status}: {count}")
                
        print("\n  By Type:")
        for rtype, count in stats['releases_by_type'].items():
            if count > 0:
                print(f"    • {rtype}: {count}")
                
        # Dashboard
        print("\n┌────────────────────────────────────────────────────────────────────┐")
        print("│                   Release Management Dashboard                     │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Total Releases:              {stats['total_releases']:>10}                       │")
        print(f"│ Current Version:             {stats['current_version']:>10}                       │")
        print(f"│ Total Deployments:           {stats['total_deployments']:>10}                       │")
        print("├────────────────────────────────────────────────────────────────────┤")
        deployed = stats['releases_by_status'].get('deployed', 0)
        approved = stats['releases_by_status'].get('approved', 0)
        draft = stats['releases_by_status'].get('draft', 0)
        print(f"│ 🟢 Deployed:                 {deployed:>10}                       │")
        print(f"│ ✅ Approved:                 {approved:>10}                       │")
        print(f"│ ⚪ Draft:                    {draft:>10}                       │")
        print("└────────────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Release Management Platform initialized!")
    print("=" * 60)
