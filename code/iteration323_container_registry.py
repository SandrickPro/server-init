#!/usr/bin/env python3
"""
Server Init - Iteration 323: Container Registry Platform
Платформа управления реестром контейнеров

Функционал:
- Image Management - управление образами
- Repository Management - управление репозиториями
- Tag Management - управление тегами
- Access Control - контроль доступа
- Vulnerability Scanning - сканирование уязвимостей
- Image Signing - подпись образов
- Replication - репликация между реестрами
- Garbage Collection - очистка неиспользуемых образов
"""

import asyncio
import random
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid


class ImageStatus(Enum):
    """Статус образа"""
    ACTIVE = "active"
    SCANNING = "scanning"
    QUARANTINE = "quarantine"
    DEPRECATED = "deprecated"
    DELETED = "deleted"


class ScanStatus(Enum):
    """Статус сканирования"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class VulnerabilitySeverity(Enum):
    """Серьезность уязвимости"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NEGLIGIBLE = "negligible"


class AccessLevel(Enum):
    """Уровень доступа"""
    ADMIN = "admin"
    WRITE = "write"
    READ = "read"
    NONE = "none"


class ReplicationTrigger(Enum):
    """Триггер репликации"""
    PUSH = "push"
    SCHEDULE = "schedule"
    MANUAL = "manual"


@dataclass
class Registry:
    """Реестр контейнеров"""
    registry_id: str
    name: str
    
    # URL
    url: str = ""
    
    # Type
    registry_type: str = "harbor"  # harbor, docker, quay, ecr, gcr, acr
    
    # Capacity
    storage_quota_gb: int = 1000
    storage_used_gb: float = 0
    
    # Counts
    repository_count: int = 0
    image_count: int = 0
    
    # Status
    is_online: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Repository:
    """Репозиторий"""
    repo_id: str
    name: str
    
    # Registry
    registry_id: str = ""
    
    # Project/Namespace
    project: str = ""
    
    # Description
    description: str = ""
    
    # Visibility
    is_public: bool = False
    
    # Counts
    tag_count: int = 0
    pull_count: int = 0
    
    # Size
    size_mb: float = 0
    
    # Status
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ImageLayer:
    """Слой образа"""
    layer_id: str
    
    # Digest
    digest: str = ""
    
    # Size
    size_bytes: int = 0
    
    # Media type
    media_type: str = "application/vnd.docker.image.rootfs.diff.tar.gzip"


@dataclass
class ContainerImage:
    """Образ контейнера"""
    image_id: str
    repo_id: str
    
    # Digest
    digest: str = ""
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Layers
    layer_ids: List[str] = field(default_factory=list)
    
    # Size
    size_mb: float = 0
    
    # Architecture
    architecture: str = "amd64"
    os_type: str = "linux"
    
    # Status
    status: ImageStatus = ImageStatus.ACTIVE
    
    # Author
    author: str = ""
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Config
    exposed_ports: List[int] = field(default_factory=list)
    entrypoint: List[str] = field(default_factory=list)
    cmd: List[str] = field(default_factory=list)
    env_vars: List[str] = field(default_factory=list)
    
    # Signature
    is_signed: bool = False
    signature: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    pushed_at: datetime = field(default_factory=datetime.now)
    
    # Pull count
    pull_count: int = 0


@dataclass
class ImageTag:
    """Тег образа"""
    tag_id: str
    repo_id: str
    
    # Name
    name: str = ""
    
    # Image
    image_id: str = ""
    
    # Immutable
    is_immutable: bool = False
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Vulnerability:
    """Уязвимость"""
    vuln_id: str
    
    # CVE
    cve_id: str = ""
    
    # Severity
    severity: VulnerabilitySeverity = VulnerabilitySeverity.MEDIUM
    
    # Package
    package_name: str = ""
    installed_version: str = ""
    fixed_version: str = ""
    
    # Description
    description: str = ""
    
    # Links
    links: List[str] = field(default_factory=list)
    
    # CVSS
    cvss_score: float = 0


@dataclass
class ScanReport:
    """Отчет о сканировании"""
    report_id: str
    image_id: str
    
    # Scanner
    scanner: str = "trivy"
    scanner_version: str = ""
    
    # Status
    status: ScanStatus = ScanStatus.PENDING
    
    # Results
    vulnerability_ids: List[str] = field(default_factory=list)
    
    # Summary
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    
    # Timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Duration
    duration_seconds: int = 0


@dataclass
class AccessPolicy:
    """Политика доступа"""
    policy_id: str
    
    # Target
    repo_pattern: str = "*"
    
    # Subject
    user_or_group: str = ""
    
    # Level
    access_level: AccessLevel = AccessLevel.READ
    
    # Status
    is_active: bool = True


@dataclass
class ReplicationRule:
    """Правило репликации"""
    rule_id: str
    name: str
    
    # Source
    source_registry_id: str = ""
    source_filter: str = "*"
    
    # Destination
    dest_registry_id: str = ""
    dest_namespace: str = ""
    
    # Trigger
    trigger: ReplicationTrigger = ReplicationTrigger.PUSH
    cron_schedule: str = ""
    
    # Options
    override_existing: bool = True
    replicate_deletion: bool = False
    
    # Status
    is_enabled: bool = True
    
    # Stats
    last_run: Optional[datetime] = None
    success_count: int = 0
    failed_count: int = 0


@dataclass
class ReplicationTask:
    """Задача репликации"""
    task_id: str
    rule_id: str
    
    # Image
    image_digest: str = ""
    
    # Status
    status: str = "pending"  # pending, in_progress, completed, failed
    progress_percent: int = 0
    
    # Error
    error_message: str = ""
    
    # Timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class WebhookConfig:
    """Конфигурация вебхука"""
    webhook_id: str
    name: str
    
    # URL
    target_url: str = ""
    
    # Events
    event_types: List[str] = field(default_factory=list)
    
    # Auth
    auth_header: str = ""
    secret: str = ""
    
    # Status
    is_enabled: bool = True
    
    # Stats
    success_count: int = 0
    failed_count: int = 0


class ContainerRegistryManager:
    """Менеджер реестра контейнеров"""
    
    def __init__(self):
        self.registries: Dict[str, Registry] = {}
        self.repositories: Dict[str, Repository] = {}
        self.images: Dict[str, ContainerImage] = {}
        self.layers: Dict[str, ImageLayer] = {}
        self.tags: Dict[str, ImageTag] = {}
        self.vulnerabilities: Dict[str, Vulnerability] = {}
        self.scan_reports: Dict[str, ScanReport] = {}
        self.access_policies: Dict[str, AccessPolicy] = {}
        self.replication_rules: Dict[str, ReplicationRule] = {}
        self.replication_tasks: Dict[str, ReplicationTask] = {}
        self.webhooks: Dict[str, WebhookConfig] = {}
        
    async def create_registry(self, name: str,
                             url: str,
                             registry_type: str = "harbor",
                             storage_quota_gb: int = 1000) -> Registry:
        """Создание реестра"""
        registry = Registry(
            registry_id=f"reg_{uuid.uuid4().hex[:8]}",
            name=name,
            url=url,
            registry_type=registry_type,
            storage_quota_gb=storage_quota_gb
        )
        
        self.registries[registry.registry_id] = registry
        return registry
        
    async def create_repository(self, name: str,
                               registry_id: str,
                               project: str = "",
                               description: str = "",
                               is_public: bool = False) -> Optional[Repository]:
        """Создание репозитория"""
        registry = self.registries.get(registry_id)
        if not registry:
            return None
            
        repo = Repository(
            repo_id=f"repo_{uuid.uuid4().hex[:8]}",
            name=name,
            registry_id=registry_id,
            project=project,
            description=description,
            is_public=is_public
        )
        
        registry.repository_count += 1
        
        self.repositories[repo.repo_id] = repo
        return repo
        
    async def push_image(self, repo_id: str,
                        tags: List[str],
                        size_mb: float,
                        architecture: str = "amd64",
                        os_type: str = "linux",
                        author: str = "",
                        labels: Dict[str, str] = None) -> Optional[ContainerImage]:
        """Пуш образа"""
        repo = self.repositories.get(repo_id)
        if not repo:
            return None
            
        # Generate digest
        digest = f"sha256:{hashlib.sha256(uuid.uuid4().bytes).hexdigest()}"
        
        image = ContainerImage(
            image_id=f"img_{uuid.uuid4().hex[:8]}",
            repo_id=repo_id,
            digest=digest,
            tags=tags.copy(),
            size_mb=size_mb,
            architecture=architecture,
            os_type=os_type,
            author=author,
            labels=labels or {}
        )
        
        # Create layers (simplified)
        num_layers = random.randint(3, 10)
        for i in range(num_layers):
            layer = ImageLayer(
                layer_id=f"layer_{uuid.uuid4().hex[:8]}",
                digest=f"sha256:{hashlib.sha256(uuid.uuid4().bytes).hexdigest()}",
                size_bytes=int(size_mb * 1024 * 1024 / num_layers)
            )
            self.layers[layer.layer_id] = layer
            image.layer_ids.append(layer.layer_id)
            
        # Create tags
        for tag_name in tags:
            tag = ImageTag(
                tag_id=f"tag_{uuid.uuid4().hex[:8]}",
                repo_id=repo_id,
                name=tag_name,
                image_id=image.image_id
            )
            self.tags[tag.tag_id] = tag
            
        # Update repo
        repo.tag_count += len(tags)
        repo.size_mb += size_mb
        repo.updated_at = datetime.now()
        
        # Update registry
        registry = self.registries.get(repo.registry_id)
        if registry:
            registry.image_count += 1
            registry.storage_used_gb += size_mb / 1024
            
        self.images[image.image_id] = image
        return image
        
    async def pull_image(self, image_id: str) -> bool:
        """Пулл образа"""
        image = self.images.get(image_id)
        if not image:
            return False
            
        image.pull_count += 1
        
        repo = self.repositories.get(image.repo_id)
        if repo:
            repo.pull_count += 1
            
        return True
        
    async def tag_image(self, image_id: str, new_tag: str) -> Optional[ImageTag]:
        """Добавление тега"""
        image = self.images.get(image_id)
        if not image:
            return None
            
        tag = ImageTag(
            tag_id=f"tag_{uuid.uuid4().hex[:8]}",
            repo_id=image.repo_id,
            name=new_tag,
            image_id=image_id
        )
        
        image.tags.append(new_tag)
        
        repo = self.repositories.get(image.repo_id)
        if repo:
            repo.tag_count += 1
            
        self.tags[tag.tag_id] = tag
        return tag
        
    async def delete_tag(self, tag_id: str) -> bool:
        """Удаление тега"""
        tag = self.tags.get(tag_id)
        if not tag or tag.is_immutable:
            return False
            
        image = self.images.get(tag.image_id)
        if image and tag.name in image.tags:
            image.tags.remove(tag.name)
            
        repo = self.repositories.get(tag.repo_id)
        if repo:
            repo.tag_count -= 1
            
        del self.tags[tag_id]
        return True
        
    async def sign_image(self, image_id: str) -> bool:
        """Подпись образа"""
        image = self.images.get(image_id)
        if not image:
            return False
            
        image.is_signed = True
        image.signature = f"sig_{hashlib.sha256(image.digest.encode()).hexdigest()[:32]}"
        
        return True
        
    async def scan_image(self, image_id: str,
                        scanner: str = "trivy") -> Optional[ScanReport]:
        """Сканирование образа"""
        image = self.images.get(image_id)
        if not image:
            return None
            
        image.status = ImageStatus.SCANNING
        
        report = ScanReport(
            report_id=f"scan_{uuid.uuid4().hex[:8]}",
            image_id=image_id,
            scanner=scanner,
            scanner_version="0.45.0",
            status=ScanStatus.RUNNING,
            started_at=datetime.now()
        )
        
        # Simulate scan results
        num_vulns = random.randint(0, 20)
        
        for _ in range(num_vulns):
            severity = random.choice(list(VulnerabilitySeverity))
            
            vuln = Vulnerability(
                vuln_id=f"vuln_{uuid.uuid4().hex[:8]}",
                cve_id=f"CVE-{random.randint(2019, 2024)}-{random.randint(1000, 99999)}",
                severity=severity,
                package_name=random.choice(["openssl", "curl", "libc", "python", "nodejs", "nginx"]),
                installed_version=f"{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
                fixed_version=f"{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(10, 20)}",
                cvss_score=random.uniform(0, 10)
            )
            
            self.vulnerabilities[vuln.vuln_id] = vuln
            report.vulnerability_ids.append(vuln.vuln_id)
            
            if severity == VulnerabilitySeverity.CRITICAL:
                report.critical_count += 1
            elif severity == VulnerabilitySeverity.HIGH:
                report.high_count += 1
            elif severity == VulnerabilitySeverity.MEDIUM:
                report.medium_count += 1
            else:
                report.low_count += 1
                
        report.status = ScanStatus.COMPLETED
        report.completed_at = datetime.now()
        report.duration_seconds = random.randint(10, 60)
        
        image.status = ImageStatus.ACTIVE
        
        # Quarantine if critical vulns
        if report.critical_count > 0:
            image.status = ImageStatus.QUARANTINE
            
        self.scan_reports[report.report_id] = report
        return report
        
    async def create_access_policy(self, repo_pattern: str,
                                   user_or_group: str,
                                   access_level: AccessLevel) -> AccessPolicy:
        """Создание политики доступа"""
        policy = AccessPolicy(
            policy_id=f"pol_{uuid.uuid4().hex[:8]}",
            repo_pattern=repo_pattern,
            user_or_group=user_or_group,
            access_level=access_level
        )
        
        self.access_policies[policy.policy_id] = policy
        return policy
        
    async def create_replication_rule(self, name: str,
                                      source_registry_id: str,
                                      dest_registry_id: str,
                                      source_filter: str = "*",
                                      trigger: ReplicationTrigger = ReplicationTrigger.PUSH) -> ReplicationRule:
        """Создание правила репликации"""
        rule = ReplicationRule(
            rule_id=f"repl_{uuid.uuid4().hex[:8]}",
            name=name,
            source_registry_id=source_registry_id,
            dest_registry_id=dest_registry_id,
            source_filter=source_filter,
            trigger=trigger
        )
        
        self.replication_rules[rule.rule_id] = rule
        return rule
        
    async def run_replication(self, rule_id: str) -> Optional[ReplicationTask]:
        """Запуск репликации"""
        rule = self.replication_rules.get(rule_id)
        if not rule or not rule.is_enabled:
            return None
            
        task = ReplicationTask(
            task_id=f"rtask_{uuid.uuid4().hex[:8]}",
            rule_id=rule_id,
            status="in_progress",
            started_at=datetime.now()
        )
        
        # Simulate replication
        task.progress_percent = 100
        task.status = "completed"
        task.completed_at = datetime.now()
        
        rule.last_run = datetime.now()
        rule.success_count += 1
        
        self.replication_tasks[task.task_id] = task
        return task
        
    async def create_webhook(self, name: str,
                            target_url: str,
                            event_types: List[str]) -> WebhookConfig:
        """Создание вебхука"""
        webhook = WebhookConfig(
            webhook_id=f"wh_{uuid.uuid4().hex[:8]}",
            name=name,
            target_url=target_url,
            event_types=event_types,
            secret=uuid.uuid4().hex
        )
        
        self.webhooks[webhook.webhook_id] = webhook
        return webhook
        
    async def garbage_collect(self, registry_id: str) -> Dict[str, Any]:
        """Сборка мусора"""
        registry = self.registries.get(registry_id)
        if not registry:
            return {}
            
        # Find unreferenced layers
        referenced_layers: Set[str] = set()
        for image in self.images.values():
            referenced_layers.update(image.layer_ids)
            
        unreferenced = []
        freed_bytes = 0
        
        for layer_id, layer in list(self.layers.items()):
            if layer_id not in referenced_layers:
                unreferenced.append(layer_id)
                freed_bytes += layer.size_bytes
                del self.layers[layer_id]
                
        freed_mb = freed_bytes / (1024 * 1024)
        registry.storage_used_gb -= freed_mb / 1024
        
        return {
            "layers_removed": len(unreferenced),
            "freed_mb": freed_mb
        }
        
    def check_access(self, user: str, repo_name: str, required_level: AccessLevel) -> bool:
        """Проверка доступа"""
        level_order = [AccessLevel.NONE, AccessLevel.READ, AccessLevel.WRITE, AccessLevel.ADMIN]
        
        user_level = AccessLevel.NONE
        
        for policy in self.access_policies.values():
            if not policy.is_active:
                continue
                
            # Check pattern match (simplified)
            if policy.repo_pattern == "*" or policy.repo_pattern in repo_name:
                if policy.user_or_group == user or policy.user_or_group == "*":
                    if level_order.index(policy.access_level) > level_order.index(user_level):
                        user_level = policy.access_level
                        
        return level_order.index(user_level) >= level_order.index(required_level)
        
    def get_repository_statistics(self, repo_id: str) -> Dict[str, Any]:
        """Статистика репозитория"""
        repo = self.repositories.get(repo_id)
        if not repo:
            return {}
            
        images = [img for img in self.images.values() if img.repo_id == repo_id]
        
        total_size = sum(img.size_mb for img in images)
        total_pulls = sum(img.pull_count for img in images)
        signed_count = sum(1 for img in images if img.is_signed)
        
        # Vulnerability summary
        critical = high = medium = low = 0
        for img in images:
            for report in self.scan_reports.values():
                if report.image_id == img.image_id:
                    critical += report.critical_count
                    high += report.high_count
                    medium += report.medium_count
                    low += report.low_count
                    
        return {
            "repo_id": repo_id,
            "name": repo.name,
            "image_count": len(images),
            "tag_count": repo.tag_count,
            "total_size_mb": total_size,
            "total_pulls": total_pulls,
            "signed_images": signed_count,
            "vulnerabilities": {
                "critical": critical,
                "high": high,
                "medium": medium,
                "low": low
            }
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_images = len(self.images)
        total_tags = len(self.tags)
        total_pulls = sum(img.pull_count for img in self.images.values())
        
        total_size_gb = sum(img.size_mb for img in self.images.values()) / 1024
        
        signed_images = sum(1 for img in self.images.values() if img.is_signed)
        
        by_status = {}
        for img in self.images.values():
            by_status[img.status.value] = by_status.get(img.status.value, 0) + 1
            
        total_vulns = len(self.vulnerabilities)
        critical_vulns = sum(1 for v in self.vulnerabilities.values() if v.severity == VulnerabilitySeverity.CRITICAL)
        
        return {
            "total_registries": len(self.registries),
            "total_repositories": len(self.repositories),
            "total_images": total_images,
            "total_tags": total_tags,
            "total_layers": len(self.layers),
            "total_pulls": total_pulls,
            "total_size_gb": total_size_gb,
            "signed_images": signed_images,
            "by_status": by_status,
            "total_vulnerabilities": total_vulns,
            "critical_vulnerabilities": critical_vulns,
            "scan_reports": len(self.scan_reports),
            "replication_rules": len(self.replication_rules),
            "webhooks": len(self.webhooks)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 323: Container Registry Platform")
    print("=" * 60)
    
    registry_mgr = ContainerRegistryManager()
    print("✓ Container Registry Manager created")
    
    # Create registries
    print("\n📦 Creating Container Registries...")
    
    main_registry = await registry_mgr.create_registry(
        "production-registry",
        "registry.company.com",
        "harbor",
        5000
    )
    print(f"  📦 {main_registry.name} ({main_registry.url})")
    
    dr_registry = await registry_mgr.create_registry(
        "dr-registry",
        "dr-registry.company.com",
        "harbor",
        5000
    )
    print(f"  📦 {dr_registry.name} ({dr_registry.url})")
    
    # Create repositories
    print("\n📁 Creating Repositories...")
    
    repos_data = [
        ("nginx", "infrastructure", "Official nginx images", False),
        ("redis", "infrastructure", "Redis cache images", False),
        ("postgres", "databases", "PostgreSQL database images", False),
        ("api-gateway", "services", "API Gateway service", False),
        ("auth-service", "services", "Authentication service", False),
        ("user-service", "services", "User management service", False),
        ("order-service", "services", "Order processing service", False),
        ("payment-service", "services", "Payment service", False),
        ("base-python", "base-images", "Base Python image", True),
        ("base-node", "base-images", "Base Node.js image", True)
    ]
    
    repos = []
    for name, project, desc, public in repos_data:
        repo = await registry_mgr.create_repository(name, main_registry.registry_id, project, desc, public)
        if repo:
            repos.append(repo)
            visibility = "🌐 Public" if public else "🔒 Private"
            print(f"  📁 {project}/{name} [{visibility}]")
            
    # Push images
    print("\n📤 Pushing Container Images...")
    
    images = []
    for repo in repos:
        # Push multiple versions
        versions = ["1.0.0", "1.1.0", "1.2.0", "latest"]
        for version in versions:
            tags = [version]
            if version != "latest":
                tags.append(f"v{version}")
                
            size = random.uniform(50, 500)
            
            image = await registry_mgr.push_image(
                repo.repo_id,
                tags,
                size,
                author="ci-pipeline",
                labels={
                    "maintainer": "platform-team@company.com",
                    "version": version,
                    "build.number": str(random.randint(100, 999))
                }
            )
            
            if image:
                images.append(image)
                
    print(f"  ✓ Pushed {len(images)} images")
    
    # Sign some images
    print("\n🔏 Signing Images...")
    
    for image in images[:15]:
        await registry_mgr.sign_image(image.image_id)
        
    print(f"  ✓ Signed 15 images")
    
    # Scan images
    print("\n🔍 Scanning Images for Vulnerabilities...")
    
    scan_reports = []
    for image in images[:20]:
        report = await registry_mgr.scan_image(image.image_id)
        if report:
            scan_reports.append(report)
            
    print(f"  ✓ Scanned {len(scan_reports)} images")
    
    # Pull some images
    print("\n📥 Simulating Image Pulls...")
    
    for _ in range(100):
        image = random.choice(images)
        await registry_mgr.pull_image(image.image_id)
        
    print(f"  ✓ Simulated 100 pulls")
    
    # Create access policies
    print("\n🔐 Creating Access Policies...")
    
    policies_data = [
        ("*", "admin-group", AccessLevel.ADMIN),
        ("services/*", "dev-team", AccessLevel.WRITE),
        ("infrastructure/*", "dev-team", AccessLevel.READ),
        ("base-images/*", "*", AccessLevel.READ)
    ]
    
    policies = []
    for pattern, subject, level in policies_data:
        policy = await registry_mgr.create_access_policy(pattern, subject, level)
        policies.append(policy)
        print(f"  🔐 {pattern} -> {subject}: {level.value}")
        
    # Create replication rules
    print("\n🔄 Creating Replication Rules...")
    
    repl_rule = await registry_mgr.create_replication_rule(
        "DR Replication",
        main_registry.registry_id,
        dr_registry.registry_id,
        "*",
        ReplicationTrigger.PUSH
    )
    print(f"  🔄 {repl_rule.name}")
    
    # Run replication
    await registry_mgr.run_replication(repl_rule.rule_id)
    print(f"  ✓ Replication completed")
    
    # Create webhooks
    print("\n🔔 Creating Webhooks...")
    
    webhook = await registry_mgr.create_webhook(
        "CI/CD Notification",
        "https://jenkins.company.com/webhooks/registry",
        ["push", "delete", "scan_completed"]
    )
    print(f"  🔔 {webhook.name}")
    
    # Garbage collection
    print("\n🗑️ Running Garbage Collection...")
    
    gc_result = await registry_mgr.garbage_collect(main_registry.registry_id)
    print(f"  ✓ Removed {gc_result.get('layers_removed', 0)} unreferenced layers")
    print(f"  ✓ Freed {gc_result.get('freed_mb', 0):.2f} MB")
    
    # Registry status
    print("\n📦 Registry Status:")
    
    for reg in [main_registry, dr_registry]:
        status = "✓ Online" if reg.is_online else "✗ Offline"
        used_pct = reg.storage_used_gb / reg.storage_quota_gb * 100 if reg.storage_quota_gb > 0 else 0
        
        print(f"\n  📦 {reg.name} [{status}]")
        print(f"     URL: {reg.url}")
        print(f"     Type: {reg.registry_type}")
        print(f"     Repositories: {reg.repository_count}")
        print(f"     Images: {reg.image_count}")
        print(f"     Storage: {reg.storage_used_gb:.2f} / {reg.storage_quota_gb} GB ({used_pct:.1f}%)")
        
    # Repository list
    print("\n📁 Repositories:")
    
    print("\n  ┌──────────────────────────────────────┬─────────────────────────┬──────────────┬──────────────┬──────────────┬──────────────┐")
    print("  │ Repository                           │ Project                 │ Tags         │ Size (MB)    │ Pulls        │ Visibility   │")
    print("  ├──────────────────────────────────────┼─────────────────────────┼──────────────┼──────────────┼──────────────┼──────────────┤")
    
    for repo in repos:
        name = repo.name[:36].ljust(36)
        project = repo.project[:23].ljust(23)
        tags = str(repo.tag_count)[:12].ljust(12)
        size = f"{repo.size_mb:.1f}"[:12].ljust(12)
        pulls = str(repo.pull_count)[:12].ljust(12)
        vis = ("Public" if repo.is_public else "Private")[:12].ljust(12)
        
        print(f"  │ {name} │ {project} │ {tags} │ {size} │ {pulls} │ {vis} │")
        
    print("  └──────────────────────────────────────┴─────────────────────────┴──────────────┴──────────────┴──────────────┴──────────────┘")
    
    # Image list (recent)
    print("\n📦 Recent Images:")
    
    print("\n  ┌────────────────────────────────────────────────┬─────────────────────┬────────────────┬──────────────┬─────────────────────────────┐")
    print("  │ Repository/Tags                                │ Digest              │ Size           │ Pulls        │ Status                      │")
    print("  ├────────────────────────────────────────────────┼─────────────────────┼────────────────┼──────────────┼─────────────────────────────┤")
    
    for image in images[:10]:
        repo = registry_mgr.repositories.get(image.repo_id)
        repo_name = repo.name if repo else "unknown"
        tags_str = ", ".join(image.tags[:2])
        if len(image.tags) > 2:
            tags_str += "..."
        name = f"{repo_name}:{tags_str}"[:46].ljust(46)
        digest = image.digest[:17].ljust(17) + "..."
        size = f"{image.size_mb:.1f} MB"[:14].ljust(14)
        pulls = str(image.pull_count)[:12].ljust(12)
        
        status_icons = []
        if image.is_signed:
            status_icons.append("🔏")
        if image.status == ImageStatus.QUARANTINE:
            status_icons.append("⚠️")
        else:
            status_icons.append("✓")
        status = " ".join(status_icons) + " " + image.status.value
        status = status[:27].ljust(27)
        
        print(f"  │ {name} │ {digest} │ {size} │ {pulls} │ {status} │")
        
    print("  └────────────────────────────────────────────────┴─────────────────────┴────────────────┴──────────────┴─────────────────────────────┘")
    
    # Vulnerability summary
    print("\n🔍 Vulnerability Summary:")
    
    total_critical = sum(r.critical_count for r in scan_reports)
    total_high = sum(r.high_count for r in scan_reports)
    total_medium = sum(r.medium_count for r in scan_reports)
    total_low = sum(r.low_count for r in scan_reports)
    
    print(f"\n  🔴 Critical: {total_critical}")
    print(f"  🟠 High:     {total_high}")
    print(f"  🟡 Medium:   {total_medium}")
    print(f"  🟢 Low:      {total_low}")
    
    # Top vulnerabilities
    print("\n  Top Vulnerabilities:")
    
    critical_vulns = [v for v in registry_mgr.vulnerabilities.values() if v.severity == VulnerabilitySeverity.CRITICAL][:5]
    
    for vuln in critical_vulns:
        print(f"\n  ⚠️ {vuln.cve_id} [{vuln.severity.value.upper()}]")
        print(f"     Package: {vuln.package_name} {vuln.installed_version}")
        print(f"     Fixed in: {vuln.fixed_version}")
        print(f"     CVSS: {vuln.cvss_score:.1f}")
        
    # Access check demo
    print("\n🔐 Access Check Demo:")
    
    checks = [
        ("dev-user", "services/api-gateway", AccessLevel.WRITE),
        ("dev-user", "infrastructure/nginx", AccessLevel.WRITE),
        ("guest", "base-images/python", AccessLevel.READ)
    ]
    
    for user, repo, level in checks:
        result = registry_mgr.check_access(user, repo, level)
        status = "✓ Allowed" if result else "✗ Denied"
        print(f"  {user} -> {repo} ({level.value}): {status}")
        
    # Replication status
    print("\n🔄 Replication Status:")
    
    for rule in registry_mgr.replication_rules.values():
        src = registry_mgr.registries.get(rule.source_registry_id)
        dst = registry_mgr.registries.get(rule.dest_registry_id)
        src_name = src.name if src else "unknown"
        dst_name = dst.name if dst else "unknown"
        
        print(f"\n  🔄 {rule.name}")
        print(f"     {src_name} -> {dst_name}")
        print(f"     Trigger: {rule.trigger.value}")
        print(f"     Filter: {rule.source_filter}")
        print(f"     Success: {rule.success_count} | Failed: {rule.failed_count}")
        
    # Statistics
    print("\n📊 Overall Statistics:")
    
    stats = registry_mgr.get_statistics()
    
    print(f"\n  Registries: {stats['total_registries']}")
    print(f"  Repositories: {stats['total_repositories']}")
    print(f"  Images: {stats['total_images']}")
    print(f"  Tags: {stats['total_tags']}")
    print(f"  Layers: {stats['total_layers']}")
    print(f"  Total Size: {stats['total_size_gb']:.2f} GB")
    print(f"  Total Pulls: {stats['total_pulls']}")
    print(f"  Signed Images: {stats['signed_images']}")
    
    print("\n  By Status:")
    for status, count in stats['by_status'].items():
        print(f"    {status}: {count}")
        
    print(f"\n  Vulnerabilities: {stats['total_vulnerabilities']} (Critical: {stats['critical_vulnerabilities']})")
    print(f"  Scan Reports: {stats['scan_reports']}")
    print(f"  Replication Rules: {stats['replication_rules']}")
    print(f"  Webhooks: {stats['webhooks']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Container Registry Platform                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Repositories:          {stats['total_repositories']:>12}                          │")
    print(f"│ Total Images:                {stats['total_images']:>12}                          │")
    print(f"│ Total Tags:                  {stats['total_tags']:>12}                          │")
    print(f"│ Total Storage:               {stats['total_size_gb']:>10.2f} GB                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Signed Images:               {stats['signed_images']:>12}                          │")
    print(f"│ Critical Vulnerabilities:    {stats['critical_vulnerabilities']:>12}                          │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Container Registry Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
