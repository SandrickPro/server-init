#!/usr/bin/env python3
"""
Server Init - Iteration 111: Container Registry Platform
Платформа контейнерных реестров

Функционал:
- Registry Management - управление реестрами
- Image Lifecycle - жизненный цикл образов
- Vulnerability Scanning - сканирование уязвимостей
- Image Signing - подпись образов
- Replication - репликация между реестрами
- Access Control - контроль доступа
- Garbage Collection - очистка мусора
- Quota Management - управление квотами
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
import hashlib


class RegistryType(Enum):
    """Тип реестра"""
    PUBLIC = "public"
    PRIVATE = "private"
    HYBRID = "hybrid"


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
    """Критичность уязвимости"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NEGLIGIBLE = "negligible"


class SignatureStatus(Enum):
    """Статус подписи"""
    UNSIGNED = "unsigned"
    SIGNED = "signed"
    VERIFIED = "verified"
    INVALID = "invalid"


@dataclass
class ImageLayer:
    """Слой образа"""
    digest: str
    size_bytes: int = 0
    media_type: str = "application/vnd.docker.image.rootfs.diff.tar.gzip"
    created: datetime = field(default_factory=datetime.now)


@dataclass
class Vulnerability:
    """Уязвимость"""
    cve_id: str
    severity: VulnerabilitySeverity = VulnerabilitySeverity.MEDIUM
    package_name: str = ""
    installed_version: str = ""
    fixed_version: str = ""
    description: str = ""
    published: datetime = field(default_factory=datetime.now)


@dataclass
class ScanResult:
    """Результат сканирования"""
    scan_id: str
    image_digest: str = ""
    status: ScanStatus = ScanStatus.PENDING
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    
    @property
    def critical_count(self) -> int:
        return len([v for v in self.vulnerabilities 
                   if v.severity == VulnerabilitySeverity.CRITICAL])
    
    @property
    def high_count(self) -> int:
        return len([v for v in self.vulnerabilities 
                   if v.severity == VulnerabilitySeverity.HIGH])


@dataclass
class ImageSignature:
    """Подпись образа"""
    signature_id: str
    digest: str = ""
    signer: str = ""
    algorithm: str = "sha256"
    signature: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    status: SignatureStatus = SignatureStatus.UNSIGNED


@dataclass
class ContainerImage:
    """Контейнерный образ"""
    image_id: str
    repository: str = ""
    tag: str = "latest"
    digest: str = ""
    
    # Status
    status: ImageStatus = ImageStatus.ACTIVE
    
    # Size
    size_bytes: int = 0
    
    # Layers
    layers: List[ImageLayer] = field(default_factory=list)
    
    # Metadata
    created: datetime = field(default_factory=datetime.now)
    author: str = ""
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Architecture
    architecture: str = "amd64"
    os: str = "linux"
    
    # Security
    scan_result: Optional[ScanResult] = None
    signature: Optional[ImageSignature] = None
    
    # Usage
    pull_count: int = 0
    last_pulled: Optional[datetime] = None


@dataclass
class Repository:
    """Репозиторий"""
    repo_id: str
    name: str = ""
    description: str = ""
    
    # Visibility
    public: bool = False
    
    # Images
    images: List[str] = field(default_factory=list)
    
    # Quota
    quota_bytes: int = 10 * 1024 * 1024 * 1024  # 10 GB
    used_bytes: int = 0
    
    # Timestamps
    created: datetime = field(default_factory=datetime.now)
    updated: datetime = field(default_factory=datetime.now)
    
    # Stats
    total_pulls: int = 0


@dataclass
class Registry:
    """Реестр контейнеров"""
    registry_id: str
    name: str = ""
    url: str = ""
    
    # Type
    registry_type: RegistryType = RegistryType.PRIVATE
    
    # Repositories
    repositories: List[str] = field(default_factory=list)
    
    # Storage
    storage_backend: str = "s3"
    storage_used_bytes: int = 0
    
    # Config
    immutable_tags: bool = False
    allow_anonymous_pull: bool = False


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
    enabled: bool = True
    trigger: str = "on_push"  # on_push, scheduled, manual
    
    # Status
    last_run: Optional[datetime] = None
    replicated_count: int = 0


class RegistryManager:
    """Менеджер реестров"""
    
    def __init__(self):
        self.registries: Dict[str, Registry] = {}
        
    def create(self, name: str, url: str,
                registry_type: RegistryType = RegistryType.PRIVATE,
                **kwargs) -> Registry:
        """Создание реестра"""
        registry = Registry(
            registry_id=f"reg_{uuid.uuid4().hex[:8]}",
            name=name,
            url=url,
            registry_type=registry_type,
            **kwargs
        )
        self.registries[registry.registry_id] = registry
        return registry
        
    def get_stats(self, registry_id: str) -> Dict[str, Any]:
        """Статистика реестра"""
        registry = self.registries.get(registry_id)
        if not registry:
            return {}
            
        return {
            "registry_id": registry_id,
            "name": registry.name,
            "repositories": len(registry.repositories),
            "storage_used_gb": registry.storage_used_bytes / (1024**3)
        }


class ImageManager:
    """Менеджер образов"""
    
    def __init__(self):
        self.images: Dict[str, ContainerImage] = {}
        self.repositories: Dict[str, Repository] = {}
        
    def create_repository(self, name: str, **kwargs) -> Repository:
        """Создание репозитория"""
        repo = Repository(
            repo_id=f"repo_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        self.repositories[repo.repo_id] = repo
        return repo
        
    def push(self, repository: str, tag: str,
              size_bytes: int, layers: List[ImageLayer] = None,
              **kwargs) -> ContainerImage:
        """Push образа"""
        digest = f"sha256:{hashlib.sha256(f'{repository}:{tag}:{datetime.now()}'.encode()).hexdigest()}"
        
        image = ContainerImage(
            image_id=f"img_{uuid.uuid4().hex[:8]}",
            repository=repository,
            tag=tag,
            digest=digest,
            size_bytes=size_bytes,
            layers=layers or [],
            **kwargs
        )
        self.images[image.image_id] = image
        
        # Update repository
        for repo in self.repositories.values():
            if repo.name == repository:
                repo.images.append(image.image_id)
                repo.used_bytes += size_bytes
                repo.updated = datetime.now()
                break
                
        return image
        
    def pull(self, image_id: str) -> Optional[ContainerImage]:
        """Pull образа"""
        image = self.images.get(image_id)
        if image:
            image.pull_count += 1
            image.last_pulled = datetime.now()
        return image
        
    def list_tags(self, repository: str) -> List[str]:
        """Список тегов"""
        return [img.tag for img in self.images.values() 
               if img.repository == repository]
        
    def delete(self, image_id: str) -> bool:
        """Удаление образа"""
        image = self.images.get(image_id)
        if not image:
            return False
            
        image.status = ImageStatus.DELETED
        
        # Update repository
        for repo in self.repositories.values():
            if image_id in repo.images:
                repo.images.remove(image_id)
                repo.used_bytes -= image.size_bytes
                break
                
        return True


class VulnerabilityScanner:
    """Сканер уязвимостей"""
    
    def __init__(self, image_manager: ImageManager):
        self.image_manager = image_manager
        self.scans: Dict[str, ScanResult] = {}
        
    async def scan(self, image_id: str) -> ScanResult:
        """Сканирование образа"""
        image = self.image_manager.images.get(image_id)
        if not image:
            return None
            
        scan = ScanResult(
            scan_id=f"scan_{uuid.uuid4().hex[:8]}",
            image_digest=image.digest,
            status=ScanStatus.SCANNING
        )
        self.scans[scan.scan_id] = scan
        
        # Simulate scanning
        await asyncio.sleep(0.1)
        
        # Generate random vulnerabilities
        vuln_count = random.randint(0, 15)
        
        for i in range(vuln_count):
            severity = random.choice(list(VulnerabilitySeverity))
            vuln = Vulnerability(
                cve_id=f"CVE-2024-{random.randint(1000, 9999)}",
                severity=severity,
                package_name=random.choice(["openssl", "libssl", "curl", "glibc", "zlib", "busybox"]),
                installed_version=f"{random.randint(1,5)}.{random.randint(0,9)}.{random.randint(0,9)}",
                fixed_version=f"{random.randint(1,5)}.{random.randint(0,9)}.{random.randint(10,20)}",
                description=f"Security vulnerability in package"
            )
            scan.vulnerabilities.append(vuln)
            
        scan.status = ScanStatus.COMPLETED
        scan.completed_at = datetime.now()
        
        # Update image
        image.scan_result = scan
        
        return scan
        
    def get_summary(self, scan_id: str) -> Dict[str, Any]:
        """Сводка по сканированию"""
        scan = self.scans.get(scan_id)
        if not scan:
            return {}
            
        counts = defaultdict(int)
        for vuln in scan.vulnerabilities:
            counts[vuln.severity.value] += 1
            
        return {
            "scan_id": scan_id,
            "status": scan.status.value,
            "total_vulnerabilities": len(scan.vulnerabilities),
            "critical": counts["critical"],
            "high": counts["high"],
            "medium": counts["medium"],
            "low": counts["low"]
        }


class SigningService:
    """Сервис подписи"""
    
    def __init__(self, image_manager: ImageManager):
        self.image_manager = image_manager
        self.signatures: Dict[str, ImageSignature] = {}
        
    def sign(self, image_id: str, signer: str,
              key_id: str = None) -> ImageSignature:
        """Подписать образ"""
        image = self.image_manager.images.get(image_id)
        if not image:
            return None
            
        signature = ImageSignature(
            signature_id=f"sig_{uuid.uuid4().hex[:8]}",
            digest=image.digest,
            signer=signer,
            algorithm="sha256",
            signature=hashlib.sha256(f"{image.digest}:{signer}:{datetime.now()}".encode()).hexdigest(),
            status=SignatureStatus.SIGNED,
            expires_at=datetime.now() + timedelta(days=365)
        )
        
        self.signatures[signature.signature_id] = signature
        image.signature = signature
        
        return signature
        
    def verify(self, image_id: str) -> Dict[str, Any]:
        """Проверка подписи"""
        image = self.image_manager.images.get(image_id)
        if not image or not image.signature:
            return {"verified": False, "reason": "No signature"}
            
        sig = image.signature
        
        # Check expiration
        if sig.expires_at and sig.expires_at < datetime.now():
            sig.status = SignatureStatus.INVALID
            return {"verified": False, "reason": "Signature expired"}
            
        sig.status = SignatureStatus.VERIFIED
        return {
            "verified": True,
            "signer": sig.signer,
            "signed_at": sig.created_at.isoformat(),
            "algorithm": sig.algorithm
        }


class ReplicationService:
    """Сервис репликации"""
    
    def __init__(self):
        self.rules: Dict[str, ReplicationRule] = {}
        
    def create_rule(self, name: str, source: str, target: str,
                     **kwargs) -> ReplicationRule:
        """Создание правила"""
        rule = ReplicationRule(
            rule_id=f"repl_{uuid.uuid4().hex[:8]}",
            name=name,
            source_registry=source,
            target_registry=target,
            **kwargs
        )
        self.rules[rule.rule_id] = rule
        return rule
        
    async def execute(self, rule_id: str) -> Dict[str, Any]:
        """Выполнение репликации"""
        rule = self.rules.get(rule_id)
        if not rule:
            return {"status": "error"}
            
        # Simulate replication
        await asyncio.sleep(0.1)
        
        replicated = random.randint(1, 10)
        rule.last_run = datetime.now()
        rule.replicated_count += replicated
        
        return {
            "status": "success",
            "rule_id": rule_id,
            "replicated": replicated
        }


class GarbageCollector:
    """Сборщик мусора"""
    
    def __init__(self, image_manager: ImageManager):
        self.image_manager = image_manager
        
    def run(self, dry_run: bool = True) -> Dict[str, Any]:
        """Запуск GC"""
        # Find orphaned layers and deleted images
        deleted_images = [img for img in self.image_manager.images.values()
                         if img.status == ImageStatus.DELETED]
        
        # Calculate reclaimable space
        reclaimable = sum(img.size_bytes for img in deleted_images)
        
        result = {
            "dry_run": dry_run,
            "deleted_images": len(deleted_images),
            "reclaimable_bytes": reclaimable,
            "reclaimable_gb": reclaimable / (1024**3)
        }
        
        if not dry_run:
            # Actually delete
            for img in deleted_images:
                del self.image_manager.images[img.image_id]
            result["freed_bytes"] = reclaimable
            
        return result


class ContainerRegistryPlatform:
    """Платформа контейнерных реестров"""
    
    def __init__(self):
        self.registry_manager = RegistryManager()
        self.image_manager = ImageManager()
        self.scanner = VulnerabilityScanner(self.image_manager)
        self.signing = SigningService(self.image_manager)
        self.replication = ReplicationService()
        self.gc = GarbageCollector(self.image_manager)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        images = list(self.image_manager.images.values())
        active_images = [i for i in images if i.status == ImageStatus.ACTIVE]
        
        scanned = [i for i in active_images if i.scan_result]
        signed = [i for i in active_images if i.signature]
        
        total_vulns = sum(len(i.scan_result.vulnerabilities) 
                        for i in scanned if i.scan_result)
        critical_vulns = sum(i.scan_result.critical_count 
                            for i in scanned if i.scan_result)
        
        total_size = sum(i.size_bytes for i in active_images)
        
        return {
            "total_registries": len(self.registry_manager.registries),
            "total_repositories": len(self.image_manager.repositories),
            "total_images": len(active_images),
            "scanned_images": len(scanned),
            "signed_images": len(signed),
            "total_vulnerabilities": total_vulns,
            "critical_vulnerabilities": critical_vulns,
            "total_storage_gb": total_size / (1024**3),
            "replication_rules": len(self.replication.rules)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 111: Container Registry Platform")
    print("=" * 60)
    
    async def demo():
        platform = ContainerRegistryPlatform()
        print("✓ Container Registry Platform created")
        
        # Create registries
        print("\n📦 Creating Registries...")
        
        registries_data = [
            ("production", "registry.prod.example.com", RegistryType.PRIVATE),
            ("staging", "registry.stage.example.com", RegistryType.PRIVATE),
            ("public", "registry.example.com", RegistryType.PUBLIC)
        ]
        
        for name, url, reg_type in registries_data:
            registry = platform.registry_manager.create(name, url, reg_type)
            print(f"  ✓ {name} ({reg_type.value}): {url}")
            
        # Create repositories
        print("\n📁 Creating Repositories...")
        
        repos_data = [
            ("myapp/backend", "Backend API service"),
            ("myapp/frontend", "React frontend"),
            ("myapp/worker", "Background job worker"),
            ("tools/nginx", "Custom nginx image"),
            ("tools/postgres", "PostgreSQL with extensions")
        ]
        
        for name, desc in repos_data:
            repo = platform.image_manager.create_repository(name, description=desc)
            print(f"  ✓ {name}")
            
        # Push images
        print("\n🚀 Pushing Images...")
        
        images_data = [
            ("myapp/backend", "v1.0.0", 150 * 1024 * 1024),
            ("myapp/backend", "v1.1.0", 152 * 1024 * 1024),
            ("myapp/backend", "v1.2.0", 155 * 1024 * 1024),
            ("myapp/frontend", "v2.0.0", 80 * 1024 * 1024),
            ("myapp/frontend", "v2.1.0", 82 * 1024 * 1024),
            ("myapp/worker", "v1.0.0", 120 * 1024 * 1024),
            ("tools/nginx", "1.25-custom", 50 * 1024 * 1024),
            ("tools/postgres", "15.3-ext", 200 * 1024 * 1024)
        ]
        
        pushed_images = []
        for repo, tag, size in images_data:
            layers = [
                ImageLayer(digest=f"sha256:{uuid.uuid4().hex}", size_bytes=size // 3),
                ImageLayer(digest=f"sha256:{uuid.uuid4().hex}", size_bytes=size // 3),
                ImageLayer(digest=f"sha256:{uuid.uuid4().hex}", size_bytes=size // 3)
            ]
            
            image = platform.image_manager.push(repo, tag, size, layers)
            pushed_images.append(image)
            print(f"  ✓ {repo}:{tag} ({size / (1024*1024):.0f} MB)")
            
        # Scan images
        print("\n🔍 Scanning Images for Vulnerabilities...")
        
        for image in pushed_images[:5]:
            scan = await platform.scanner.scan(image.image_id)
            summary = platform.scanner.get_summary(scan.scan_id)
            
            status_icon = "🔴" if summary["critical"] > 0 else "🟡" if summary["high"] > 0 else "🟢"
            print(f"  {status_icon} {image.repository}:{image.tag}")
            print(f"     Critical: {summary['critical']}, High: {summary['high']}, Medium: {summary['medium']}, Low: {summary['low']}")
            
        # Sign images
        print("\n✍️ Signing Images...")
        
        for image in pushed_images[:4]:
            sig = platform.signing.sign(image.image_id, "ci-pipeline")
            verify = platform.signing.verify(image.image_id)
            
            status_icon = "✅" if verify["verified"] else "❌"
            print(f"  {status_icon} {image.repository}:{image.tag} - signed by {sig.signer}")
            
        # Setup replication
        print("\n🔄 Setting up Replication...")
        
        repl_rules = [
            ("prod-to-dr", "production", "dr-site"),
            ("stage-to-prod", "staging", "production")
        ]
        
        for name, source, target in repl_rules:
            rule = platform.replication.create_rule(name, source, target)
            result = await platform.replication.execute(rule.rule_id)
            print(f"  ✓ {name}: {source} → {target} ({result['replicated']} images)")
            
        # Simulate pulls
        print("\n📥 Simulating Image Pulls...")
        
        for image in pushed_images:
            for _ in range(random.randint(5, 50)):
                platform.image_manager.pull(image.image_id)
                
        popular = sorted(pushed_images, key=lambda x: x.pull_count, reverse=True)[:3]
        for img in popular:
            print(f"  📊 {img.repository}:{img.tag} - {img.pull_count} pulls")
            
        # Mark one image as deleted and run GC
        print("\n🗑️ Garbage Collection...")
        
        old_image = pushed_images[-1]
        platform.image_manager.delete(old_image.image_id)
        
        gc_result = platform.gc.run(dry_run=True)
        print(f"  Dry run: {gc_result['deleted_images']} images, {gc_result['reclaimable_gb']:.2f} GB reclaimable")
        
        gc_result = platform.gc.run(dry_run=False)
        print(f"  Cleaned: {gc_result['freed_bytes'] / (1024**3):.2f} GB freed")
        
        # List tags
        print("\n🏷️ Repository Tags:")
        
        for repo in list(platform.image_manager.repositories.values())[:3]:
            tags = platform.image_manager.list_tags(repo.name)
            print(f"  {repo.name}: {', '.join(tags) if tags else 'no tags'}")
            
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Infrastructure:")
        print(f"    Registries: {stats['total_registries']}")
        print(f"    Repositories: {stats['total_repositories']}")
        print(f"    Images: {stats['total_images']}")
        print(f"    Storage: {stats['total_storage_gb']:.2f} GB")
        
        print(f"\n  Security:")
        print(f"    Scanned: {stats['scanned_images']}")
        print(f"    Signed: {stats['signed_images']}")
        print(f"    Vulnerabilities: {stats['total_vulnerabilities']}")
        print(f"    Critical: {stats['critical_vulnerabilities']}")
        
        print(f"\n  Replication Rules: {stats['replication_rules']}")
        
        # Dashboard
        print("\n📋 Container Registry Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │             Container Registry Overview                     │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Registries:         {stats['total_registries']:>10}                        │")
        print(f"  │ Repositories:       {stats['total_repositories']:>10}                        │")
        print(f"  │ Images:             {stats['total_images']:>10}                        │")
        print(f"  │ Storage Used:       {stats['total_storage_gb']:>10.2f} GB                   │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Scanned Images:     {stats['scanned_images']:>10}                        │")
        print(f"  │ Signed Images:      {stats['signed_images']:>10}                        │")
        print(f"  │ Vulnerabilities:    {stats['total_vulnerabilities']:>10}                        │")
        print(f"  │ Critical:           {stats['critical_vulnerabilities']:>10}                        │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Container Registry Platform initialized!")
    print("=" * 60)
