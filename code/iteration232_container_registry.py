#!/usr/bin/env python3
"""
Server Init - Iteration 232: Container Registry Platform
Платформа реестра контейнеров

Функционал:
- Image Management - управление образами
- Tag Management - управление тегами
- Vulnerability Scanning - сканирование уязвимостей
- Access Control - контроль доступа
- Garbage Collection - сборка мусора
- Replication - репликация
- Webhooks - вебхуки
- Usage Analytics - аналитика использования
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import hashlib


class ImageStatus(Enum):
    """Статус образа"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    QUARANTINED = "quarantined"
    DELETED = "deleted"


class ScanStatus(Enum):
    """Статус сканирования"""
    PENDING = "pending"
    SCANNING = "scanning"
    COMPLETED = "completed"
    FAILED = "failed"


class VulnerabilitySeverity(Enum):
    """Серьёзность уязвимости"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NEGLIGIBLE = "negligible"


class ReplicationStatus(Enum):
    """Статус репликации"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Repository:
    """Репозиторий"""
    repo_id: str
    name: str = ""
    description: str = ""
    
    # Visibility
    is_public: bool = False
    
    # Owner
    owner: str = ""
    namespace: str = ""
    
    # Stats
    pull_count: int = 0
    star_count: int = 0
    
    # Created
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ImageLayer:
    """Слой образа"""
    layer_id: str
    digest: str = ""
    size_bytes: int = 0
    media_type: str = "application/vnd.docker.image.rootfs.diff.tar.gzip"


@dataclass
class ImageTag:
    """Тег образа"""
    tag_id: str
    name: str = "latest"
    digest: str = ""
    
    # Times
    pushed_at: datetime = field(default_factory=datetime.now)
    
    # Immutable
    is_immutable: bool = False


@dataclass
class ContainerImage:
    """Образ контейнера"""
    image_id: str
    repo_id: str = ""
    
    # Digest
    digest: str = ""
    
    # Tags
    tags: List[ImageTag] = field(default_factory=list)
    
    # Layers
    layers: List[ImageLayer] = field(default_factory=list)
    
    # Size
    size_bytes: int = 0
    
    # Config
    architecture: str = "amd64"
    os: str = "linux"
    
    # Status
    status: ImageStatus = ImageStatus.ACTIVE
    
    # Scan
    scan_status: ScanStatus = ScanStatus.PENDING
    last_scanned: Optional[datetime] = None
    
    # Times
    created_at: datetime = field(default_factory=datetime.now)
    pushed_at: datetime = field(default_factory=datetime.now)
    
    # Pushed by
    pushed_by: str = ""


@dataclass
class Vulnerability:
    """Уязвимость"""
    vuln_id: str
    cve_id: str = ""
    
    # Details
    package: str = ""
    version: str = ""
    fixed_version: str = ""
    
    # Severity
    severity: VulnerabilitySeverity = VulnerabilitySeverity.MEDIUM
    
    # Description
    description: str = ""
    
    # Link
    link: str = ""


@dataclass
class ScanResult:
    """Результат сканирования"""
    scan_id: str
    image_id: str = ""
    
    # Status
    status: ScanStatus = ScanStatus.COMPLETED
    
    # Vulnerabilities
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    
    # Counts
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    
    # Times
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime = field(default_factory=datetime.now)


@dataclass
class ReplicationRule:
    """Правило репликации"""
    rule_id: str
    name: str = ""
    
    # Source/Target
    source_registry: str = ""
    target_registry: str = ""
    
    # Filter
    repository_filter: str = "*"
    tag_filter: str = "*"
    
    # Schedule
    trigger: str = "on_push"  # on_push, scheduled
    
    # Active
    is_enabled: bool = True


@dataclass
class ReplicationTask:
    """Задача репликации"""
    task_id: str
    rule_id: str = ""
    image_digest: str = ""
    
    # Status
    status: ReplicationStatus = ReplicationStatus.PENDING
    
    # Progress
    bytes_transferred: int = 0
    total_bytes: int = 0
    
    # Times
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ImageScanner:
    """Сканер образов"""
    
    def __init__(self):
        self.known_vulns = [
            ("CVE-2023-0001", "openssl", "1.1.1", "1.1.1t", VulnerabilitySeverity.CRITICAL),
            ("CVE-2023-0002", "curl", "7.88.0", "7.88.1", VulnerabilitySeverity.HIGH),
            ("CVE-2023-0003", "zlib", "1.2.11", "1.2.13", VulnerabilitySeverity.MEDIUM),
            ("CVE-2023-0004", "libpng", "1.6.37", "1.6.39", VulnerabilitySeverity.LOW),
        ]
        
    def scan(self, image: ContainerImage) -> ScanResult:
        """Сканирование образа"""
        result = ScanResult(
            scan_id=f"scan_{uuid.uuid4().hex[:8]}",
            image_id=image.image_id
        )
        
        # Simulate finding vulnerabilities
        num_vulns = random.randint(0, len(self.known_vulns))
        found_vulns = random.sample(self.known_vulns, num_vulns)
        
        for cve, pkg, ver, fixed, sev in found_vulns:
            vuln = Vulnerability(
                vuln_id=f"v_{uuid.uuid4().hex[:8]}",
                cve_id=cve,
                package=pkg,
                version=ver,
                fixed_version=fixed,
                severity=sev,
                description=f"Vulnerability in {pkg}",
                link=f"https://nvd.nist.gov/vuln/detail/{cve}"
            )
            result.vulnerabilities.append(vuln)
            
            if sev == VulnerabilitySeverity.CRITICAL:
                result.critical_count += 1
            elif sev == VulnerabilitySeverity.HIGH:
                result.high_count += 1
            elif sev == VulnerabilitySeverity.MEDIUM:
                result.medium_count += 1
            else:
                result.low_count += 1
                
        result.completed_at = datetime.now()
        return result


class ContainerRegistryPlatform:
    """Платформа реестра контейнеров"""
    
    def __init__(self):
        self.repositories: Dict[str, Repository] = {}
        self.images: Dict[str, ContainerImage] = {}
        self.scans: Dict[str, ScanResult] = {}
        self.replication_rules: Dict[str, ReplicationRule] = {}
        self.replication_tasks: List[ReplicationTask] = []
        self.scanner = ImageScanner()
        
    def create_repository(self, name: str, namespace: str,
                         is_public: bool = False, owner: str = "") -> Repository:
        """Создание репозитория"""
        repo = Repository(
            repo_id=f"repo_{uuid.uuid4().hex[:8]}",
            name=name,
            namespace=namespace,
            is_public=is_public,
            owner=owner
        )
        self.repositories[repo.repo_id] = repo
        return repo
        
    def push_image(self, repo_id: str, tag: str = "latest",
                  size_mb: int = 100, pushed_by: str = "") -> Optional[ContainerImage]:
        """Пуш образа"""
        repo = self.repositories.get(repo_id)
        if not repo:
            return None
            
        # Generate digest
        digest = f"sha256:{hashlib.sha256(uuid.uuid4().bytes).hexdigest()}"
        
        # Create layers
        num_layers = random.randint(3, 10)
        layers = []
        total_size = 0
        
        for i in range(num_layers):
            layer_size = random.randint(1000000, 50000000)
            layer = ImageLayer(
                layer_id=f"layer_{uuid.uuid4().hex[:8]}",
                digest=f"sha256:{hashlib.sha256(uuid.uuid4().bytes).hexdigest()}",
                size_bytes=layer_size
            )
            layers.append(layer)
            total_size += layer_size
            
        # Create tag
        image_tag = ImageTag(
            tag_id=f"tag_{uuid.uuid4().hex[:8]}",
            name=tag,
            digest=digest
        )
        
        image = ContainerImage(
            image_id=f"img_{uuid.uuid4().hex[:8]}",
            repo_id=repo_id,
            digest=digest,
            tags=[image_tag],
            layers=layers,
            size_bytes=total_size,
            pushed_by=pushed_by
        )
        
        self.images[image.image_id] = image
        repo.pull_count += 1
        
        return image
        
    def pull_image(self, repo_id: str, tag: str = "latest") -> Optional[ContainerImage]:
        """Пулл образа"""
        repo = self.repositories.get(repo_id)
        if not repo:
            return None
            
        for image in self.images.values():
            if image.repo_id == repo_id:
                for t in image.tags:
                    if t.name == tag:
                        repo.pull_count += 1
                        return image
        return None
        
    def scan_image(self, image_id: str) -> Optional[ScanResult]:
        """Сканирование образа"""
        image = self.images.get(image_id)
        if not image:
            return None
            
        image.scan_status = ScanStatus.SCANNING
        result = self.scanner.scan(image)
        
        image.scan_status = ScanStatus.COMPLETED
        image.last_scanned = datetime.now()
        
        # Quarantine if critical vulns found
        if result.critical_count > 0:
            image.status = ImageStatus.QUARANTINED
            
        self.scans[result.scan_id] = result
        return result
        
    def create_replication_rule(self, name: str, source: str,
                               target: str, repo_filter: str = "*") -> ReplicationRule:
        """Создание правила репликации"""
        rule = ReplicationRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name=name,
            source_registry=source,
            target_registry=target,
            repository_filter=repo_filter
        )
        self.replication_rules[rule.rule_id] = rule
        return rule
        
    def run_garbage_collection(self) -> Dict[str, int]:
        """Запуск сборки мусора"""
        # Find unreferenced layers
        referenced_digests = set()
        for image in self.images.values():
            if image.status != ImageStatus.DELETED:
                for layer in image.layers:
                    referenced_digests.add(layer.digest)
                    
        # Count "deleted" items
        deleted_layers = random.randint(0, 10)
        freed_bytes = deleted_layers * random.randint(10000000, 100000000)
        
        return {
            "deleted_layers": deleted_layers,
            "freed_bytes": freed_bytes
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        repos = list(self.repositories.values())
        images = list(self.images.values())
        
        total_size = sum(i.size_bytes for i in images)
        total_pulls = sum(r.pull_count for r in repos)
        
        scanned = [i for i in images if i.scan_status == ScanStatus.COMPLETED]
        quarantined = [i for i in images if i.status == ImageStatus.QUARANTINED]
        
        scans = list(self.scans.values())
        total_vulns = sum(len(s.vulnerabilities) for s in scans)
        critical_vulns = sum(s.critical_count for s in scans)
        
        return {
            "total_repositories": len(repos),
            "total_images": len(images),
            "total_size_gb": total_size / (1024**3),
            "total_pulls": total_pulls,
            "scanned_images": len(scanned),
            "quarantined_images": len(quarantined),
            "total_vulnerabilities": total_vulns,
            "critical_vulnerabilities": critical_vulns,
            "replication_rules": len(self.replication_rules)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 232: Container Registry Platform")
    print("=" * 60)
    
    platform = ContainerRegistryPlatform()
    print("✓ Container Registry Platform created")
    
    # Create repositories
    print("\n📦 Creating Repositories...")
    
    repos_config = [
        ("api-service", "production", False, "platform-team"),
        ("web-frontend", "production", False, "frontend-team"),
        ("worker", "production", False, "backend-team"),
        ("base-python", "library", True, "platform-team"),
        ("base-node", "library", True, "platform-team"),
        ("ml-service", "production", False, "ml-team"),
    ]
    
    repos = []
    for name, namespace, is_public, owner in repos_config:
        repo = platform.create_repository(name, namespace, is_public, owner)
        repos.append(repo)
        visibility = "public" if is_public else "private"
        print(f"  ✓ {namespace}/{name} ({visibility})")
        
    # Push images
    print("\n📤 Pushing Images...")
    
    images = []
    tags = ["latest", "v1.0.0", "v1.1.0", "v1.2.0", "dev"]
    
    for repo in repos:
        for tag in random.sample(tags, random.randint(2, 4)):
            image = platform.push_image(repo.repo_id, tag, random.randint(50, 500), "ci-bot")
            if image:
                images.append(image)
                
    print(f"  ✓ Pushed {len(images)} images")
    
    # Scan images
    print("\n🔍 Scanning Images for Vulnerabilities...")
    
    scan_results = []
    for image in images[:8]:
        result = platform.scan_image(image.image_id)
        if result:
            scan_results.append(result)
            
            repo = platform.repositories.get(image.repo_id)
            repo_name = repo.name if repo else "unknown"
            tag = image.tags[0].name if image.tags else "unknown"
            
            status_icon = "🔴" if result.critical_count > 0 else "🟢" if result.high_count == 0 else "🟡"
            print(f"  {status_icon} {repo_name}:{tag} - C:{result.critical_count} H:{result.high_count} M:{result.medium_count}")
            
    # Create replication rules
    print("\n🔄 Creating Replication Rules...")
    
    rules = [
        platform.create_replication_rule("DR Replication", "registry.main.com", "registry.dr.com", "production/*"),
        platform.create_replication_rule("Edge Sync", "registry.main.com", "registry.edge.com", "library/*"),
    ]
    
    for rule in rules:
        print(f"  ✓ {rule.name}: {rule.source_registry} -> {rule.target_registry}")
        
    # Run garbage collection
    print("\n🗑️ Running Garbage Collection...")
    
    gc_result = platform.run_garbage_collection()
    freed_mb = gc_result["freed_bytes"] / (1024**2)
    print(f"  ✓ Deleted {gc_result['deleted_layers']} layers, freed {freed_mb:.1f} MB")
    
    # Display repositories
    print("\n📦 Repositories:")
    
    print("\n  ┌────────────────────────────┬────────────┬────────┬─────────┐")
    print("  │ Repository                 │ Namespace  │ Images │ Pulls   │")
    print("  ├────────────────────────────┼────────────┼────────┼─────────┤")
    
    for repo in platform.repositories.values():
        name = repo.name[:26].ljust(26)
        namespace = repo.namespace[:10].ljust(10)
        
        img_count = len([i for i in platform.images.values() if i.repo_id == repo.repo_id])
        images_str = str(img_count)[:6].ljust(6)
        pulls = str(repo.pull_count)[:7].ljust(7)
        
        print(f"  │ {name} │ {namespace} │ {images_str} │ {pulls} │")
        
    print("  └────────────────────────────┴────────────┴────────┴─────────┘")
    
    # Image list
    print("\n🐳 Recent Images:")
    
    print("\n  ┌─────────────────────────────────┬──────────┬──────────┬──────────┐")
    print("  │ Image                           │ Tag      │ Size     │ Status   │")
    print("  ├─────────────────────────────────┼──────────┼──────────┼──────────┤")
    
    for image in list(platform.images.values())[:8]:
        repo = platform.repositories.get(image.repo_id)
        repo_name = repo.name if repo else "unknown"
        tag = image.tags[0].name if image.tags else "unknown"
        
        name = f"{repo_name}:{tag}"[:31].ljust(31)
        tag_str = tag[:8].ljust(8)
        size = f"{image.size_bytes / (1024**2):.0f}MB"[:8].ljust(8)
        
        status_icons = {
            ImageStatus.ACTIVE: "🟢",
            ImageStatus.QUARANTINED: "🔴",
            ImageStatus.DEPRECATED: "🟡",
            ImageStatus.DELETED: "⚫"
        }
        status = f"{status_icons.get(image.status, '⚪')}"[:8].ljust(8)
        
        print(f"  │ {name} │ {tag_str} │ {size} │ {status} │")
        
    print("  └─────────────────────────────────┴──────────┴──────────┴──────────┘")
    
    # Vulnerability summary
    print("\n🛡️ Vulnerability Summary:")
    
    stats = platform.get_statistics()
    
    print(f"  Total Vulnerabilities: {stats['total_vulnerabilities']}")
    print(f"  Critical: {stats['critical_vulnerabilities']}")
    
    sev_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for scan in scan_results:
        sev_counts["critical"] += scan.critical_count
        sev_counts["high"] += scan.high_count
        sev_counts["medium"] += scan.medium_count
        sev_counts["low"] += scan.low_count
        
    sev_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
    
    print("\n  By Severity:")
    for sev, count in sev_counts.items():
        icon = sev_icons.get(sev, "⚪")
        bar = "█" * min(count, 10) + "░" * (10 - min(count, 10))
        print(f"    {icon} {sev:10s} [{bar}] {count}")
        
    # Top vulnerabilities
    print("\n🔍 Top Vulnerabilities:")
    
    all_vulns = []
    for scan in scan_results:
        all_vulns.extend(scan.vulnerabilities)
        
    critical_vulns = [v for v in all_vulns if v.severity == VulnerabilitySeverity.CRITICAL]
    
    for vuln in critical_vulns[:3]:
        print(f"  {sev_icons['critical']} {vuln.cve_id}: {vuln.package} {vuln.version}")
        print(f"     Fixed in: {vuln.fixed_version}")
        
    # Storage usage
    print("\n💾 Storage Usage:")
    
    print(f"  Total Size: {stats['total_size_gb']:.2f} GB")
    print(f"  Images: {stats['total_images']}")
    
    # By namespace
    by_namespace = {}
    for image in platform.images.values():
        repo = platform.repositories.get(image.repo_id)
        if repo:
            ns = repo.namespace
            if ns not in by_namespace:
                by_namespace[ns] = 0
            by_namespace[ns] += image.size_bytes
            
    print("\n  By Namespace:")
    for ns, size in sorted(by_namespace.items(), key=lambda x: -x[1]):
        size_gb = size / (1024**3)
        bar_len = min(int(size_gb * 2), 10)
        bar = "█" * bar_len + "░" * (10 - bar_len)
        print(f"    {ns:15s} [{bar}] {size_gb:.2f} GB")
        
    # Statistics
    print("\n📈 Registry Statistics:")
    
    print(f"\n  Repositories: {stats['total_repositories']}")
    print(f"  Images: {stats['total_images']}")
    print(f"  Total Pulls: {stats['total_pulls']}")
    print(f"  Scanned: {stats['scanned_images']}")
    print(f"  Quarantined: {stats['quarantined_images']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Container Registry Dashboard                     │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Repositories:            {stats['total_repositories']:>12}                        │")
    print(f"│ Total Images:                  {stats['total_images']:>12}                        │")
    print(f"│ Storage Used (GB):               {stats['total_size_gb']:>10.2f}                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Scanned Images:                {stats['scanned_images']:>12}                        │")
    print(f"│ Critical Vulnerabilities:      {stats['critical_vulnerabilities']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Container Registry Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
