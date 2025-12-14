#!/usr/bin/env python3
"""
Server Init - Iteration 158: Container Registry Platform
Платформа реестра контейнеров

Функционал:
- Image Management - управление образами
- Tag Management - управление тегами
- Vulnerability Scanning - сканирование уязвимостей
- Image Signing - подпись образов
- Garbage Collection - сборка мусора
- Replication - репликация
- Access Control - контроль доступа
- Webhook Notifications - уведомления через вебхуки
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid
import hashlib


class ImageStatus(Enum):
    """Статус образа"""
    PUSHING = "pushing"
    READY = "ready"
    SCANNING = "scanning"
    QUARANTINED = "quarantined"
    DELETED = "deleted"


class VulnerabilitySeverity(Enum):
    """Серьёзность уязвимости"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NEGLIGIBLE = "negligible"


class ScanStatus(Enum):
    """Статус сканирования"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ReplicationStatus(Enum):
    """Статус репликации"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class AccessLevel(Enum):
    """Уровень доступа"""
    NONE = "none"
    PULL = "pull"
    PUSH = "push"
    ADMIN = "admin"


@dataclass
class Layer:
    """Слой образа"""
    digest: str
    size: int = 0
    media_type: str = "application/vnd.docker.image.rootfs.diff.tar.gzip"


@dataclass
class ImageManifest:
    """Манифест образа"""
    digest: str
    media_type: str = "application/vnd.docker.distribution.manifest.v2+json"
    
    # Config
    config_digest: str = ""
    
    # Layers
    layers: List[Layer] = field(default_factory=list)
    
    # Size
    total_size: int = 0
    
    # Created
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Image:
    """Образ контейнера"""
    image_id: str
    repository: str = ""
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Manifest
    manifest: Optional[ImageManifest] = None
    digest: str = ""
    
    # Metadata
    architecture: str = "amd64"
    os: str = "linux"
    
    # Status
    status: ImageStatus = ImageStatus.READY
    
    # Security
    signed: bool = False
    signature: str = ""
    scan_status: ScanStatus = ScanStatus.PENDING
    
    # Statistics
    pull_count: int = 0
    push_count: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_pulled: Optional[datetime] = None
    last_pushed: Optional[datetime] = None


@dataclass
class Repository:
    """Репозиторий"""
    repo_id: str
    name: str = ""
    
    # Project
    project: str = ""
    
    # Images
    images: Dict[str, Image] = field(default_factory=dict)
    
    # Settings
    public: bool = False
    immutable_tags: bool = False
    
    # Statistics
    image_count: int = 0
    total_size: int = 0
    
    # Retention
    retention_days: int = 0  # 0 = unlimited
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Vulnerability:
    """Уязвимость"""
    vuln_id: str
    cve_id: str = ""
    
    # Severity
    severity: VulnerabilitySeverity = VulnerabilitySeverity.MEDIUM
    
    # Package
    package_name: str = ""
    package_version: str = ""
    fixed_version: str = ""
    
    # Description
    description: str = ""
    
    # Links
    references: List[str] = field(default_factory=list)


@dataclass
class ScanReport:
    """Отчёт сканирования"""
    report_id: str
    image_digest: str = ""
    
    # Status
    status: ScanStatus = ScanStatus.PENDING
    
    # Vulnerabilities
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    
    # Summary
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    
    # Timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class ImageSignature:
    """Подпись образа"""
    signature_id: str
    image_digest: str = ""
    
    # Signer
    signer: str = ""
    key_id: str = ""
    
    # Signature
    signature_data: str = ""
    algorithm: str = "SHA256"
    
    # Verification
    verified: bool = False
    
    # Timestamps
    signed_at: datetime = field(default_factory=datetime.now)


@dataclass
class ReplicationRule:
    """Правило репликации"""
    rule_id: str
    name: str = ""
    
    # Source/Target
    source_registry: str = ""
    target_registry: str = ""
    
    # Filters
    repository_filter: str = ""  # regex
    tag_filter: str = ""  # regex
    
    # Settings
    enabled: bool = True
    trigger: str = "push"  # push, manual, scheduled
    
    # Status
    last_replicated: Optional[datetime] = None
    replication_count: int = 0


@dataclass
class ReplicationTask:
    """Задача репликации"""
    task_id: str
    rule_id: str = ""
    
    # Image
    source_image: str = ""
    target_image: str = ""
    
    # Status
    status: ReplicationStatus = ReplicationStatus.PENDING
    
    # Progress
    bytes_transferred: int = 0
    total_bytes: int = 0
    
    # Timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class AccessPolicy:
    """Политика доступа"""
    policy_id: str
    
    # Scope
    repository: str = ""
    project: str = ""
    
    # Principal
    user: str = ""
    group: str = ""
    
    # Access
    access_level: AccessLevel = AccessLevel.NONE


@dataclass
class Webhook:
    """Вебхук"""
    webhook_id: str
    name: str = ""
    
    # Target
    url: str = ""
    secret: str = ""
    
    # Events
    events: List[str] = field(default_factory=list)  # push, pull, scan, delete
    
    # Settings
    enabled: bool = True
    
    # Statistics
    deliveries: int = 0
    failures: int = 0


class ImageManager:
    """Менеджер образов"""
    
    def __init__(self):
        self.repositories: Dict[str, Repository] = {}
        self.images: Dict[str, Image] = {}
        self.layers: Dict[str, Layer] = {}
        
    def create_repository(self, name: str, project: str = "library",
                           **kwargs) -> Repository:
        """Создание репозитория"""
        repo = Repository(
            repo_id=f"repo_{uuid.uuid4().hex[:8]}",
            name=name,
            project=project,
            **kwargs
        )
        
        full_name = f"{project}/{name}"
        self.repositories[full_name] = repo
        
        return repo
        
    def push_image(self, repository: str, tag: str,
                    layers: List[Dict], config: Dict) -> Image:
        """Загрузка образа"""
        if repository not in self.repositories:
            # Auto-create repository
            parts = repository.split("/")
            project = parts[0] if len(parts) > 1 else "library"
            name = parts[-1]
            self.create_repository(name, project)
            
        # Create layers
        image_layers = []
        total_size = 0
        
        for layer_data in layers:
            layer = Layer(
                digest=layer_data.get("digest", f"sha256:{uuid.uuid4().hex}"),
                size=layer_data.get("size", 0),
                media_type=layer_data.get("media_type", "application/vnd.docker.image.rootfs.diff.tar.gzip")
            )
            image_layers.append(layer)
            total_size += layer.size
            
            # Store layer
            self.layers[layer.digest] = layer
            
        # Create manifest
        manifest_digest = f"sha256:{hashlib.sha256(json.dumps(config).encode()).hexdigest()}"
        
        manifest = ImageManifest(
            digest=manifest_digest,
            config_digest=config.get("digest", ""),
            layers=image_layers,
            total_size=total_size
        )
        
        # Create or update image
        image_key = f"{repository}:{tag}"
        
        if image_key in self.images:
            image = self.images[image_key]
            image.manifest = manifest
            image.digest = manifest_digest
            image.push_count += 1
            image.last_pushed = datetime.now()
        else:
            image = Image(
                image_id=f"img_{uuid.uuid4().hex[:8]}",
                repository=repository,
                tags=[tag],
                manifest=manifest,
                digest=manifest_digest,
                architecture=config.get("architecture", "amd64"),
                os=config.get("os", "linux"),
                push_count=1,
                last_pushed=datetime.now()
            )
            self.images[image_key] = image
            
        # Update repository
        repo = self.repositories.get(repository)
        if repo:
            repo.images[tag] = image
            repo.image_count = len(repo.images)
            repo.total_size = sum(img.manifest.total_size for img in repo.images.values() if img.manifest)
            
        return image
        
    def pull_image(self, repository: str, tag: str) -> Optional[Image]:
        """Получение образа"""
        image_key = f"{repository}:{tag}"
        image = self.images.get(image_key)
        
        if image:
            image.pull_count += 1
            image.last_pulled = datetime.now()
            
        return image
        
    def delete_image(self, repository: str, tag: str) -> bool:
        """Удаление образа"""
        image_key = f"{repository}:{tag}"
        
        if image_key in self.images:
            image = self.images[image_key]
            image.status = ImageStatus.DELETED
            
            # Remove from repository
            repo = self.repositories.get(repository)
            if repo and tag in repo.images:
                del repo.images[tag]
                repo.image_count = len(repo.images)
                
            return True
            
        return False
        
    def list_tags(self, repository: str) -> List[str]:
        """Список тегов"""
        repo = self.repositories.get(repository)
        if repo:
            return list(repo.images.keys())
        return []


class VulnerabilityScanner:
    """Сканер уязвимостей"""
    
    def __init__(self):
        self.reports: Dict[str, ScanReport] = {}
        self.vulnerability_db: Dict[str, Vulnerability] = {}
        
    def _load_sample_vulns(self):
        """Загрузка примеров уязвимостей"""
        sample_vulns = [
            ("CVE-2021-44228", VulnerabilitySeverity.CRITICAL, "log4j-core", "2.14.1", "2.17.0", "Log4j RCE"),
            ("CVE-2021-3711", VulnerabilitySeverity.HIGH, "openssl", "1.1.1k", "1.1.1l", "OpenSSL SM2 Decryption Buffer Overflow"),
            ("CVE-2021-22946", VulnerabilitySeverity.MEDIUM, "curl", "7.77.0", "7.79.0", "Curl TLS protocol bypass"),
            ("CVE-2021-33574", VulnerabilitySeverity.LOW, "glibc", "2.33", "2.34", "glibc mq_notify bug"),
        ]
        
        for cve, sev, pkg, ver, fixed, desc in sample_vulns:
            self.vulnerability_db[cve] = Vulnerability(
                vuln_id=f"vuln_{uuid.uuid4().hex[:8]}",
                cve_id=cve,
                severity=sev,
                package_name=pkg,
                package_version=ver,
                fixed_version=fixed,
                description=desc
            )
            
    async def scan(self, image: Image) -> ScanReport:
        """Сканирование образа"""
        report = ScanReport(
            report_id=f"scan_{uuid.uuid4().hex[:8]}",
            image_digest=image.digest,
            status=ScanStatus.IN_PROGRESS,
            started_at=datetime.now()
        )
        
        image.scan_status = ScanStatus.IN_PROGRESS
        
        # Load sample vulnerabilities
        self._load_sample_vulns()
        
        # Simulate scanning
        await asyncio.sleep(0.2)
        
        # Add some vulnerabilities based on image
        import random
        num_vulns = random.randint(0, len(self.vulnerability_db))
        vulns = random.sample(list(self.vulnerability_db.values()), num_vulns)
        
        report.vulnerabilities = vulns
        
        # Count by severity
        for vuln in vulns:
            if vuln.severity == VulnerabilitySeverity.CRITICAL:
                report.critical_count += 1
            elif vuln.severity == VulnerabilitySeverity.HIGH:
                report.high_count += 1
            elif vuln.severity == VulnerabilitySeverity.MEDIUM:
                report.medium_count += 1
            else:
                report.low_count += 1
                
        report.status = ScanStatus.COMPLETED
        report.completed_at = datetime.now()
        
        image.scan_status = ScanStatus.COMPLETED
        
        # Quarantine if critical vulns
        if report.critical_count > 0:
            image.status = ImageStatus.QUARANTINED
            
        self.reports[report.report_id] = report
        
        return report


class ImageSigner:
    """Подпись образов"""
    
    def __init__(self):
        self.signatures: Dict[str, ImageSignature] = {}
        self.trusted_keys: Dict[str, str] = {}
        
    def add_trusted_key(self, key_id: str, public_key: str):
        """Добавление доверенного ключа"""
        self.trusted_keys[key_id] = public_key
        
    def sign(self, image: Image, signer: str, key_id: str,
              private_key: str = "") -> ImageSignature:
        """Подпись образа"""
        # Create signature (simplified)
        signature_data = hashlib.sha256(
            f"{image.digest}:{signer}:{key_id}".encode()
        ).hexdigest()
        
        sig = ImageSignature(
            signature_id=f"sig_{uuid.uuid4().hex[:8]}",
            image_digest=image.digest,
            signer=signer,
            key_id=key_id,
            signature_data=signature_data
        )
        
        image.signed = True
        image.signature = sig.signature_id
        
        self.signatures[sig.signature_id] = sig
        
        return sig
        
    def verify(self, image: Image) -> tuple:
        """Проверка подписи"""
        if not image.signed:
            return False, "Image not signed"
            
        sig = self.signatures.get(image.signature)
        if not sig:
            return False, "Signature not found"
            
        if sig.key_id not in self.trusted_keys:
            return False, "Key not trusted"
            
        # Verify signature (simplified)
        expected = hashlib.sha256(
            f"{image.digest}:{sig.signer}:{sig.key_id}".encode()
        ).hexdigest()
        
        if sig.signature_data == expected:
            sig.verified = True
            return True, "Signature valid"
        else:
            return False, "Signature invalid"


class ReplicationManager:
    """Менеджер репликации"""
    
    def __init__(self, image_manager: ImageManager):
        self.image_manager = image_manager
        self.rules: Dict[str, ReplicationRule] = {}
        self.tasks: List[ReplicationTask] = []
        
    def create_rule(self, name: str, source_registry: str,
                     target_registry: str, **kwargs) -> ReplicationRule:
        """Создание правила"""
        rule = ReplicationRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name=name,
            source_registry=source_registry,
            target_registry=target_registry,
            **kwargs
        )
        self.rules[rule.rule_id] = rule
        return rule
        
    async def replicate(self, rule: ReplicationRule, repository: str,
                         tag: str) -> ReplicationTask:
        """Репликация образа"""
        task = ReplicationTask(
            task_id=f"task_{uuid.uuid4().hex[:8]}",
            rule_id=rule.rule_id,
            source_image=f"{rule.source_registry}/{repository}:{tag}",
            target_image=f"{rule.target_registry}/{repository}:{tag}",
            status=ReplicationStatus.IN_PROGRESS,
            started_at=datetime.now()
        )
        
        self.tasks.append(task)
        
        # Simulate replication
        image = self.image_manager.images.get(f"{repository}:{tag}")
        
        if image and image.manifest:
            task.total_bytes = image.manifest.total_size
            
            # Simulate transfer
            await asyncio.sleep(0.1)
            task.bytes_transferred = task.total_bytes
            task.status = ReplicationStatus.COMPLETED
        else:
            task.status = ReplicationStatus.FAILED
            
        task.completed_at = datetime.now()
        rule.last_replicated = datetime.now()
        rule.replication_count += 1
        
        return task


class GarbageCollector:
    """Сборщик мусора"""
    
    def __init__(self, image_manager: ImageManager):
        self.image_manager = image_manager
        self.collections: List[Dict] = []
        
    async def collect(self, dry_run: bool = False) -> Dict:
        """Сборка мусора"""
        result = {
            "collected_layers": 0,
            "collected_images": 0,
            "freed_bytes": 0,
            "dry_run": dry_run
        }
        
        # Find unreferenced layers
        referenced_layers = set()
        
        for image in self.image_manager.images.values():
            if image.manifest:
                for layer in image.manifest.layers:
                    referenced_layers.add(layer.digest)
                    
        # Find unreferenced
        unreferenced = []
        for digest, layer in self.image_manager.layers.items():
            if digest not in referenced_layers:
                unreferenced.append((digest, layer))
                
        # Collect
        for digest, layer in unreferenced:
            result["collected_layers"] += 1
            result["freed_bytes"] += layer.size
            
            if not dry_run:
                del self.image_manager.layers[digest]
                
        # Find deleted images
        deleted_images = [
            img for img in self.image_manager.images.values()
            if img.status == ImageStatus.DELETED
        ]
        
        result["collected_images"] = len(deleted_images)
        
        if not dry_run:
            for img in deleted_images:
                key = f"{img.repository}:{img.tags[0]}" if img.tags else img.image_id
                if key in self.image_manager.images:
                    del self.image_manager.images[key]
                    
        self.collections.append({
            "timestamp": datetime.now().isoformat(),
            "result": result
        })
        
        return result


class WebhookManager:
    """Менеджер вебхуков"""
    
    def __init__(self):
        self.webhooks: Dict[str, Webhook] = {}
        self.deliveries: List[Dict] = []
        
    def create_webhook(self, name: str, url: str, events: List[str],
                        **kwargs) -> Webhook:
        """Создание вебхука"""
        webhook = Webhook(
            webhook_id=f"hook_{uuid.uuid4().hex[:8]}",
            name=name,
            url=url,
            events=events,
            **kwargs
        )
        self.webhooks[webhook.webhook_id] = webhook
        return webhook
        
    async def trigger(self, event_type: str, payload: Dict):
        """Отправка события"""
        for webhook in self.webhooks.values():
            if not webhook.enabled:
                continue
                
            if event_type not in webhook.events:
                continue
                
            # Simulate delivery
            delivery = {
                "webhook_id": webhook.webhook_id,
                "event_type": event_type,
                "payload": payload,
                "status": "delivered",
                "timestamp": datetime.now().isoformat()
            }
            
            self.deliveries.append(delivery)
            webhook.deliveries += 1


class ContainerRegistryPlatform:
    """Платформа реестра контейнеров"""
    
    def __init__(self):
        self.image_manager = ImageManager()
        self.scanner = VulnerabilityScanner()
        self.signer = ImageSigner()
        self.replication_manager = ReplicationManager(self.image_manager)
        self.gc = GarbageCollector(self.image_manager)
        self.webhooks = WebhookManager()
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        repos = list(self.image_manager.repositories.values())
        images = list(self.image_manager.images.values())
        
        total_size = sum(r.total_size for r in repos)
        total_pulls = sum(i.pull_count for i in images)
        total_pushes = sum(i.push_count for i in images)
        
        return {
            "repositories": len(repos),
            "images": len(images),
            "layers": len(self.image_manager.layers),
            "total_size_bytes": total_size,
            "total_pulls": total_pulls,
            "total_pushes": total_pushes,
            "scan_reports": len(self.scanner.reports),
            "signatures": len(self.signer.signatures),
            "replication_rules": len(self.replication_manager.rules),
            "webhooks": len(self.webhooks.webhooks)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 158: Container Registry Platform")
    print("=" * 60)
    
    async def demo():
        platform = ContainerRegistryPlatform()
        print("✓ Container Registry Platform created")
        
        # Create repositories
        print("\n📦 Creating Repositories...")
        
        repos = [
            ("nginx", "library"),
            ("api-service", "myproject"),
            ("web-frontend", "myproject"),
            ("database", "myproject"),
        ]
        
        for name, project in repos:
            repo = platform.image_manager.create_repository(name, project)
            print(f"  ✓ {project}/{name}")
            
        # Push images
        print("\n📤 Pushing Images...")
        
        images_data = [
            {
                "repository": "library/nginx",
                "tag": "1.21",
                "layers": [
                    {"digest": "sha256:layer1", "size": 28000000},
                    {"digest": "sha256:layer2", "size": 15000000},
                ],
                "config": {"architecture": "amd64", "os": "linux"}
            },
            {
                "repository": "library/nginx",
                "tag": "latest",
                "layers": [
                    {"digest": "sha256:layer1", "size": 28000000},
                    {"digest": "sha256:layer3", "size": 16000000},
                ],
                "config": {"architecture": "amd64", "os": "linux"}
            },
            {
                "repository": "myproject/api-service",
                "tag": "v1.0.0",
                "layers": [
                    {"digest": "sha256:layer4", "size": 50000000},
                    {"digest": "sha256:layer5", "size": 25000000},
                ],
                "config": {"architecture": "amd64", "os": "linux"}
            },
            {
                "repository": "myproject/web-frontend",
                "tag": "v2.1.0",
                "layers": [
                    {"digest": "sha256:layer6", "size": 35000000},
                ],
                "config": {"architecture": "amd64", "os": "linux"}
            },
        ]
        
        for img_data in images_data:
            image = platform.image_manager.push_image(
                img_data["repository"],
                img_data["tag"],
                img_data["layers"],
                img_data["config"]
            )
            size_mb = image.manifest.total_size / 1024 / 1024
            print(f"  ✓ {img_data['repository']}:{img_data['tag']} ({size_mb:.1f} MB)")
            
        # Pull images
        print("\n📥 Pulling Images...")
        
        for _ in range(5):
            image = platform.image_manager.pull_image("library/nginx", "latest")
            
        print(f"  ✓ library/nginx:latest (pulled {image.pull_count} times)")
        
        # Add trusted key
        print("\n🔑 Setting Up Image Signing...")
        
        platform.signer.add_trusted_key(
            "key-001",
            "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhki..."
        )
        print("  ✓ Added trusted key: key-001")
        
        # Sign image
        image = platform.image_manager.images.get("myproject/api-service:v1.0.0")
        if image:
            sig = platform.signer.sign(image, "release-bot", "key-001")
            print(f"  ✓ Signed: {image.repository}:{image.tags[0]}")
            
            # Verify
            valid, msg = platform.signer.verify(image)
            print(f"  ✓ Verification: {msg}")
            
        # Scan images
        print("\n🔍 Scanning Images for Vulnerabilities...")
        
        for key, image in list(platform.image_manager.images.items())[:3]:
            report = await platform.scanner.scan(image)
            
            status_icon = "🟢" if report.critical_count == 0 else "🔴"
            print(f"\n  {status_icon} {key}")
            print(f"     Critical: {report.critical_count}, High: {report.high_count}, "
                  f"Medium: {report.medium_count}, Low: {report.low_count}")
                  
            if report.vulnerabilities:
                for vuln in report.vulnerabilities[:2]:
                    print(f"     - {vuln.cve_id}: {vuln.package_name} ({vuln.severity.value})")
                    
        # Set up replication
        print("\n🔄 Setting Up Replication...")
        
        rule = platform.replication_manager.create_rule(
            name="prod-mirror",
            source_registry="registry.local",
            target_registry="registry.prod",
            repository_filter="myproject/*",
            trigger="push"
        )
        print(f"  ✓ Rule: {rule.name}")
        print(f"    Source: {rule.source_registry}")
        print(f"    Target: {rule.target_registry}")
        
        # Replicate
        task = await platform.replication_manager.replicate(
            rule,
            "myproject/api-service",
            "v1.0.0"
        )
        print(f"\n  Replication: {task.status.value}")
        print(f"    {task.source_image} → {task.target_image}")
        print(f"    Transferred: {task.bytes_transferred / 1024 / 1024:.1f} MB")
        
        # Create webhook
        print("\n🔔 Setting Up Webhooks...")
        
        webhook = platform.webhooks.create_webhook(
            name="ci-trigger",
            url="https://ci.example.com/webhook",
            events=["push", "scan"]
        )
        print(f"  ✓ {webhook.name}: {webhook.url}")
        print(f"    Events: {', '.join(webhook.events)}")
        
        # Trigger webhook
        await platform.webhooks.trigger("push", {
            "repository": "myproject/api-service",
            "tag": "v1.0.0",
            "digest": image.digest if image else ""
        })
        print(f"  ✓ Webhook triggered: push event")
        
        # Garbage collection
        print("\n🗑️ Garbage Collection...")
        
        # Delete an image first
        platform.image_manager.delete_image("library/nginx", "1.21")
        print("  ✓ Deleted: library/nginx:1.21")
        
        # Run GC
        gc_result = await platform.gc.collect(dry_run=True)
        print(f"\n  Dry run results:")
        print(f"    Layers to collect: {gc_result['collected_layers']}")
        print(f"    Images to collect: {gc_result['collected_images']}")
        print(f"    Bytes to free: {gc_result['freed_bytes'] / 1024 / 1024:.1f} MB")
        
        # Repository statistics
        print("\n📊 Repository Statistics:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │ Repository              │ Images │ Size (MB)  │ Pulls      │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        
        for name, repo in platform.image_manager.repositories.items():
            repo_name = name[:23].ljust(23)
            size_mb = repo.total_size / 1024 / 1024
            total_pulls = sum(img.pull_count for img in repo.images.values())
            print(f"  │ {repo_name} │ {repo.image_count:6} │ {size_mb:10.1f} │ {total_pulls:10} │")
            
        print("  └─────────────────────────────────────────────────────────────┘")
        
        # Image list
        print("\n📋 Image List:")
        print("  ┌────────────────────────────────────────────────────────────────────────┐")
        print("  │ Image                        │ Digest    │ Status     │ Signed │ Scan │")
        print("  ├────────────────────────────────────────────────────────────────────────┤")
        
        for key, image in platform.image_manager.images.items():
            if image.status == ImageStatus.DELETED:
                continue
                
            name = key[:28].ljust(28)
            digest = image.digest[:10] if image.digest else "-".ljust(10)
            status = image.status.value[:10].ljust(10)
            signed = "✓" if image.signed else "-"
            scan = image.scan_status.value[:4]
            print(f"  │ {name} │ {digest} │ {status} │ {signed:6} │ {scan:4} │")
            
        print("  └────────────────────────────────────────────────────────────────────────┘")
        
        # Security summary
        print("\n🔒 Security Summary:")
        
        scanned_images = [
            img for img in platform.image_manager.images.values()
            if img.scan_status == ScanStatus.COMPLETED
        ]
        signed_images = [
            img for img in platform.image_manager.images.values()
            if img.signed
        ]
        quarantined_images = [
            img for img in platform.image_manager.images.values()
            if img.status == ImageStatus.QUARANTINED
        ]
        
        print(f"\n  Scanned: {len(scanned_images)}")
        print(f"  Signed: {len(signed_images)}")
        print(f"  Quarantined: {len(quarantined_images)}")
        
        # Platform statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Repositories: {stats['repositories']}")
        print(f"  Images: {stats['images']}")
        print(f"  Layers: {stats['layers']}")
        print(f"  Total Size: {stats['total_size_bytes'] / 1024 / 1024:.1f} MB")
        print(f"  Total Pulls: {stats['total_pulls']}")
        print(f"  Total Pushes: {stats['total_pushes']}")
        print(f"  Scan Reports: {stats['scan_reports']}")
        print(f"  Signatures: {stats['signatures']}")
        
        # Dashboard
        print("\n📋 Container Registry Dashboard:")
        print("  ┌────────────────────────────────────────────────────────────┐")
        print("  │               Container Registry Overview                  │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Repositories:            {stats['repositories']:>10}                   │")
        print(f"  │ Images:                  {stats['images']:>10}                   │")
        print(f"  │ Layers:                  {stats['layers']:>10}                   │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Pulls:             {stats['total_pulls']:>10}                   │")
        print(f"  │ Total Pushes:            {stats['total_pushes']:>10}                   │")
        print(f"  │ Replication Rules:       {stats['replication_rules']:>10}                   │")
        print("  └────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Container Registry Platform initialized!")
    print("=" * 60)
