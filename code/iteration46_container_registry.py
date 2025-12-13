#!/usr/bin/env python3
"""
Server Init - Iteration 46: Container Registry & Artifact Management
Container Registry и управление артефактами

Функционал:
- Container Registry - реестр контейнеров
- Artifact Repository - репозиторий артефактов
- Image Scanning - сканирование образов
- Vulnerability Management - управление уязвимостями
- Retention Policies - политики хранения
- Replication - репликация
- Access Control - контроль доступа
- Garbage Collection - сборка мусора
"""

import json
import asyncio
import hashlib
import time
import os
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Tuple
from enum import Enum
from abc import ABC, abstractmethod
import random
from collections import defaultdict
import uuid


class ArtifactType(Enum):
    """Тип артефакта"""
    CONTAINER_IMAGE = "container_image"
    HELM_CHART = "helm_chart"
    NPM_PACKAGE = "npm_package"
    MAVEN_ARTIFACT = "maven_artifact"
    PYPI_PACKAGE = "pypi_package"
    GENERIC = "generic"


class ScanStatus(Enum):
    """Статус сканирования"""
    PENDING = "pending"
    SCANNING = "scanning"
    COMPLETED = "completed"
    FAILED = "failed"


class Severity(Enum):
    """Критичность уязвимости"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NEGLIGIBLE = "negligible"
    UNKNOWN = "unknown"


class ReplicationMode(Enum):
    """Режим репликации"""
    PUSH = "push"
    PULL = "pull"
    BIDIRECTIONAL = "bidirectional"


@dataclass
class ImageLayer:
    """Слой образа"""
    digest: str
    size: int
    media_type: str = "application/vnd.oci.image.layer.v1.tar+gzip"
    
    # Метаданные
    created_at: datetime = field(default_factory=datetime.now)
    
    # Ссылки
    referenced_by: List[str] = field(default_factory=list)


@dataclass
class ImageManifest:
    """Манифест образа"""
    digest: str
    media_type: str = "application/vnd.oci.image.manifest.v1+json"
    
    # Конфигурация
    config_digest: str = ""
    config_size: int = 0
    
    # Слои
    layers: List[ImageLayer] = field(default_factory=list)
    
    # Размер
    total_size: int = 0
    
    # Метаданные
    annotations: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ContainerImage:
    """Контейнерный образ"""
    image_id: str
    repository: str
    tag: str
    
    # Манифест
    manifest: Optional[ImageManifest] = None
    digest: str = ""
    
    # Метаданные
    architecture: str = "amd64"
    os: str = "linux"
    
    # Размер
    size: int = 0
    compressed_size: int = 0
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Сканирование
    scan_status: ScanStatus = ScanStatus.PENDING
    vulnerabilities: List['Vulnerability'] = field(default_factory=list)
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    pushed_at: datetime = field(default_factory=datetime.now)
    last_pulled_at: Optional[datetime] = None
    pull_count: int = 0


@dataclass
class Vulnerability:
    """Уязвимость"""
    vuln_id: str
    cve_id: str
    
    # Описание
    title: str = ""
    description: str = ""
    
    # Критичность
    severity: Severity = Severity.UNKNOWN
    cvss_score: float = 0.0
    
    # Затронутые пакеты
    package_name: str = ""
    package_version: str = ""
    fixed_version: Optional[str] = None
    
    # Ссылки
    references: List[str] = field(default_factory=list)
    
    # Дата обнаружения
    discovered_at: datetime = field(default_factory=datetime.now)


@dataclass
class ScanReport:
    """Отчёт о сканировании"""
    report_id: str
    image_digest: str
    
    # Результаты
    status: ScanStatus = ScanStatus.PENDING
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    
    # Статистика
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    
    # Время
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    
    # Сканер
    scanner_name: str = ""
    scanner_version: str = ""


@dataclass
class Repository:
    """Репозиторий"""
    repo_id: str
    name: str
    
    # Тип
    artifact_type: ArtifactType = ArtifactType.CONTAINER_IMAGE
    
    # Настройки
    public: bool = False
    immutable_tags: bool = False
    
    # Образы/артефакты
    images: Dict[str, ContainerImage] = field(default_factory=dict)
    
    # Политики
    retention_policy_id: Optional[str] = None
    
    # Статистика
    total_size: int = 0
    image_count: int = 0
    
    # Метаданные
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RetentionPolicy:
    """Политика хранения"""
    policy_id: str
    name: str
    
    # Правила
    rules: List[Dict[str, Any]] = field(default_factory=list)
    
    # Настройки
    keep_last_n_tags: int = 10
    keep_tags_matching: List[str] = field(default_factory=list)  # regex
    delete_untagged: bool = True
    
    # Время
    max_age_days: Optional[int] = None
    
    # Расписание
    schedule_cron: str = "0 0 * * *"  # Ежедневно
    
    # Метаданные
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ReplicationRule:
    """Правило репликации"""
    rule_id: str
    name: str
    
    # Источник и цель
    source_registry: str = ""
    source_repository: str = ""
    destination_registry: str = ""
    destination_repository: str = ""
    
    # Режим
    mode: ReplicationMode = ReplicationMode.PUSH
    
    # Фильтры
    tag_filter: str = "*"  # regex
    
    # Расписание
    trigger: str = "manual"  # manual, scheduled, event
    schedule_cron: Optional[str] = None
    
    # Настройки
    override: bool = False
    delete_propagation: bool = False
    
    # Статус
    enabled: bool = True
    last_run: Optional[datetime] = None


@dataclass
class Artifact:
    """Общий артефакт"""
    artifact_id: str
    name: str
    version: str
    artifact_type: ArtifactType
    
    # Файлы
    files: List[Dict[str, Any]] = field(default_factory=list)
    
    # Checksums
    sha256: str = ""
    md5: str = ""
    
    # Размер
    size: int = 0
    
    # Метаданные
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    downloaded_count: int = 0


class ImageScanner:
    """Сканер образов"""
    
    def __init__(self):
        self.vulnerability_db: Dict[str, List[Vulnerability]] = {}
        self.scan_queue: asyncio.Queue = asyncio.Queue()
        self.reports: Dict[str, ScanReport] = {}
        
    def load_vulnerability_db(self, db_path: str = ""):
        """Загрузка базы уязвимостей"""
        # Симуляция загрузки базы
        self.vulnerability_db = {
            "alpine:3.18": [
                Vulnerability(
                    vuln_id="vuln_1",
                    cve_id="CVE-2023-0001",
                    title="Buffer Overflow in libcurl",
                    severity=Severity.HIGH,
                    cvss_score=7.5,
                    package_name="libcurl",
                    package_version="7.88.0",
                    fixed_version="7.88.1"
                )
            ],
            "debian:bullseye": [
                Vulnerability(
                    vuln_id="vuln_2",
                    cve_id="CVE-2023-0002",
                    title="OpenSSL Security Issue",
                    severity=Severity.CRITICAL,
                    cvss_score=9.8,
                    package_name="openssl",
                    package_version="1.1.1n",
                    fixed_version="1.1.1o"
                )
            ]
        }
        
    async def scan_image(self, image: ContainerImage) -> ScanReport:
        """Сканирование образа"""
        report = ScanReport(
            report_id=f"scan_{uuid.uuid4().hex[:8]}",
            image_digest=image.digest,
            scanner_name="container-scanner",
            scanner_version="1.0.0"
        )
        
        report.status = ScanStatus.SCANNING
        report.started_at = datetime.now()
        
        image.scan_status = ScanStatus.SCANNING
        
        # Симуляция сканирования
        await asyncio.sleep(0.2)
        
        # Поиск уязвимостей (симуляция)
        vulnerabilities = []
        
        # Проверка базы уязвимостей
        for base_image, vulns in self.vulnerability_db.items():
            if base_image in image.repository or random.random() < 0.3:
                vulnerabilities.extend(vulns)
                
        # Добавление случайных уязвимостей
        if random.random() < 0.5:
            vulnerabilities.append(Vulnerability(
                vuln_id=f"vuln_{uuid.uuid4().hex[:6]}",
                cve_id=f"CVE-2023-{random.randint(1000, 9999)}",
                title="Potential Security Issue",
                severity=random.choice(list(Severity)),
                cvss_score=round(random.uniform(1, 10), 1),
                package_name="some-package",
                package_version="1.0.0"
            ))
            
        report.vulnerabilities = vulnerabilities
        
        # Подсчёт статистики
        for vuln in vulnerabilities:
            if vuln.severity == Severity.CRITICAL:
                report.critical_count += 1
            elif vuln.severity == Severity.HIGH:
                report.high_count += 1
            elif vuln.severity == Severity.MEDIUM:
                report.medium_count += 1
            else:
                report.low_count += 1
                
        report.status = ScanStatus.COMPLETED
        report.completed_at = datetime.now()
        report.duration_seconds = (report.completed_at - report.started_at).total_seconds()
        
        # Обновление образа
        image.scan_status = ScanStatus.COMPLETED
        image.vulnerabilities = vulnerabilities
        
        self.reports[report.report_id] = report
        
        return report
        
    def get_report(self, report_id: str) -> Optional[ScanReport]:
        """Получение отчёта"""
        return self.reports.get(report_id)
        
    def get_image_vulnerabilities(self, image_digest: str) -> List[Vulnerability]:
        """Получение уязвимостей образа"""
        for report in self.reports.values():
            if report.image_digest == image_digest:
                return report.vulnerabilities
        return []


class RetentionManager:
    """Менеджер политик хранения"""
    
    def __init__(self):
        self.policies: Dict[str, RetentionPolicy] = {}
        
    def create_policy(self, name: str, **kwargs) -> RetentionPolicy:
        """Создание политики"""
        policy = RetentionPolicy(
            policy_id=f"policy_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        
        self.policies[policy.policy_id] = policy
        return policy
        
    async def execute_policy(self, policy_id: str, 
                              repository: Repository) -> Dict[str, Any]:
        """Выполнение политики"""
        policy = self.policies.get(policy_id)
        if not policy:
            return {"error": "Policy not found"}
            
        deleted_images = []
        kept_images = []
        
        # Сортировка образов по дате
        sorted_images = sorted(
            repository.images.values(),
            key=lambda x: x.pushed_at,
            reverse=True
        )
        
        for idx, image in enumerate(sorted_images):
            should_keep = False
            
            # Keep last N tags
            if idx < policy.keep_last_n_tags:
                should_keep = True
                
            # Keep matching tags
            for pattern in policy.keep_tags_matching:
                if pattern in image.tag:
                    should_keep = True
                    break
                    
            # Check age
            if policy.max_age_days:
                age = (datetime.now() - image.pushed_at).days
                if age > policy.max_age_days:
                    should_keep = False
                    
            # Delete untagged
            if policy.delete_untagged and image.tag == "":
                should_keep = False
                
            if should_keep:
                kept_images.append(image.tag)
            else:
                deleted_images.append(image.tag)
                del repository.images[image.digest]
                
        repository.image_count = len(repository.images)
        
        return {
            "policy_id": policy_id,
            "repository": repository.name,
            "deleted": len(deleted_images),
            "kept": len(kept_images),
            "deleted_tags": deleted_images
        }
        
    def get_policy(self, policy_id: str) -> Optional[RetentionPolicy]:
        """Получение политики"""
        return self.policies.get(policy_id)


class ReplicationManager:
    """Менеджер репликации"""
    
    def __init__(self):
        self.rules: Dict[str, ReplicationRule] = {}
        self.replication_history: List[Dict[str, Any]] = []
        
    def create_rule(self, name: str, **kwargs) -> ReplicationRule:
        """Создание правила"""
        rule = ReplicationRule(
            rule_id=f"repl_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        
        self.rules[rule.rule_id] = rule
        return rule
        
    async def execute_replication(self, rule_id: str,
                                   source_repo: Repository,
                                   dest_registry: 'ContainerRegistry') -> Dict[str, Any]:
        """Выполнение репликации"""
        rule = self.rules.get(rule_id)
        if not rule:
            return {"error": "Rule not found"}
            
        replicated = []
        failed = []
        
        for image in source_repo.images.values():
            # Проверка фильтра
            if rule.tag_filter != "*" and rule.tag_filter not in image.tag:
                continue
                
            # Симуляция репликации
            try:
                await asyncio.sleep(0.05)
                
                # Создание копии в destination
                dest_repo = dest_registry.get_or_create_repository(
                    rule.destination_repository or source_repo.name
                )
                
                # Копирование образа
                new_image = ContainerImage(
                    image_id=f"img_{uuid.uuid4().hex[:8]}",
                    repository=dest_repo.name,
                    tag=image.tag,
                    manifest=image.manifest,
                    digest=image.digest,
                    size=image.size
                )
                
                dest_repo.images[new_image.digest] = new_image
                replicated.append(f"{image.repository}:{image.tag}")
                
            except Exception as e:
                failed.append({
                    "image": f"{image.repository}:{image.tag}",
                    "error": str(e)
                })
                
        rule.last_run = datetime.now()
        
        result = {
            "rule_id": rule_id,
            "replicated": len(replicated),
            "failed": len(failed),
            "replicated_images": replicated
        }
        
        self.replication_history.append({
            **result,
            "timestamp": datetime.now().isoformat()
        })
        
        return result


class GarbageCollector:
    """Сборщик мусора"""
    
    def __init__(self):
        self.last_run: Optional[datetime] = None
        
    async def run(self, registry: 'ContainerRegistry') -> Dict[str, Any]:
        """Запуск сборки мусора"""
        start_time = datetime.now()
        
        freed_space = 0
        deleted_layers = 0
        deleted_manifests = 0
        
        # Сбор всех используемых слоёв
        used_layers: Set[str] = set()
        
        for repo in registry.repositories.values():
            for image in repo.images.values():
                if image.manifest:
                    for layer in image.manifest.layers:
                        used_layers.add(layer.digest)
                        
        # Удаление неиспользуемых слоёв
        layers_to_delete = []
        for layer_digest, layer in registry.layers.items():
            if layer_digest not in used_layers:
                layers_to_delete.append(layer_digest)
                freed_space += layer.size
                deleted_layers += 1
                
        for digest in layers_to_delete:
            del registry.layers[digest]
            
        self.last_run = datetime.now()
        duration = (self.last_run - start_time).total_seconds()
        
        return {
            "freed_space_bytes": freed_space,
            "freed_space_mb": round(freed_space / (1024 * 1024), 2),
            "deleted_layers": deleted_layers,
            "deleted_manifests": deleted_manifests,
            "duration_seconds": duration,
            "timestamp": self.last_run.isoformat()
        }


class ContainerRegistry:
    """Container Registry"""
    
    def __init__(self, name: str = "registry"):
        self.name = name
        
        # Репозитории
        self.repositories: Dict[str, Repository] = {}
        
        # Слои (shared)
        self.layers: Dict[str, ImageLayer] = {}
        
        # Сервисы
        self.scanner = ImageScanner()
        self.retention_manager = RetentionManager()
        self.replication_manager = ReplicationManager()
        self.garbage_collector = GarbageCollector()
        
        # Настройки
        self.auto_scan: bool = True
        
        # Загрузка базы уязвимостей
        self.scanner.load_vulnerability_db()
        
    def get_or_create_repository(self, name: str) -> Repository:
        """Получение или создание репозитория"""
        if name not in self.repositories:
            repo = Repository(
                repo_id=f"repo_{uuid.uuid4().hex[:8]}",
                name=name
            )
            self.repositories[name] = repo
            
        return self.repositories[name]
        
    async def push_image(self, repository: str, tag: str,
                          layers: List[Dict[str, Any]],
                          config: Dict[str, Any] = None) -> ContainerImage:
        """Push образа"""
        repo = self.get_or_create_repository(repository)
        
        # Создание слоёв
        image_layers = []
        total_size = 0
        
        for layer_data in layers:
            layer_digest = hashlib.sha256(
                json.dumps(layer_data).encode()
            ).hexdigest()
            
            layer = ImageLayer(
                digest=f"sha256:{layer_digest}",
                size=layer_data.get("size", random.randint(1000000, 100000000)),
                media_type=layer_data.get("media_type", "application/vnd.oci.image.layer.v1.tar+gzip")
            )
            
            self.layers[layer.digest] = layer
            image_layers.append(layer)
            total_size += layer.size
            
        # Создание манифеста
        manifest_content = {
            "schemaVersion": 2,
            "config": config or {},
            "layers": [{"digest": l.digest, "size": l.size} for l in image_layers]
        }
        
        manifest_digest = hashlib.sha256(
            json.dumps(manifest_content).encode()
        ).hexdigest()
        
        manifest = ImageManifest(
            digest=f"sha256:{manifest_digest}",
            layers=image_layers,
            total_size=total_size,
            config_digest=config.get("digest", "") if config else ""
        )
        
        # Создание образа
        image = ContainerImage(
            image_id=f"img_{uuid.uuid4().hex[:8]}",
            repository=repository,
            tag=tag,
            manifest=manifest,
            digest=manifest.digest,
            size=total_size,
            labels=config.get("labels", {}) if config else {}
        )
        
        repo.images[image.digest] = image
        repo.image_count = len(repo.images)
        repo.total_size += total_size
        
        # Автоматическое сканирование
        if self.auto_scan:
            await self.scanner.scan_image(image)
            
        return image
        
    async def pull_image(self, repository: str, reference: str) -> Optional[ContainerImage]:
        """Pull образа"""
        repo = self.repositories.get(repository)
        if not repo:
            return None
            
        # Поиск по tag или digest
        for image in repo.images.values():
            if image.tag == reference or image.digest == reference:
                image.pull_count += 1
                image.last_pulled_at = datetime.now()
                return image
                
        return None
        
    async def delete_image(self, repository: str, reference: str) -> bool:
        """Удаление образа"""
        repo = self.repositories.get(repository)
        if not repo:
            return False
            
        for digest, image in list(repo.images.items()):
            if image.tag == reference or image.digest == reference:
                repo.total_size -= image.size
                del repo.images[digest]
                repo.image_count = len(repo.images)
                return True
                
        return False
        
    def list_repositories(self) -> List[str]:
        """Список репозиториев"""
        return list(self.repositories.keys())
        
    def list_tags(self, repository: str) -> List[str]:
        """Список тегов"""
        repo = self.repositories.get(repository)
        if not repo:
            return []
            
        return [img.tag for img in repo.images.values() if img.tag]
        
    async def run_garbage_collection(self) -> Dict[str, Any]:
        """Запуск GC"""
        return await self.garbage_collector.run(self)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика registry"""
        total_images = sum(repo.image_count for repo in self.repositories.values())
        total_size = sum(repo.total_size for repo in self.repositories.values())
        
        # Статистика по уязвимостям
        critical = 0
        high = 0
        
        for repo in self.repositories.values():
            for image in repo.images.values():
                for vuln in image.vulnerabilities:
                    if vuln.severity == Severity.CRITICAL:
                        critical += 1
                    elif vuln.severity == Severity.HIGH:
                        high += 1
                        
        return {
            "repositories": len(self.repositories),
            "images": total_images,
            "layers": len(self.layers),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "vulnerabilities": {
                "critical": critical,
                "high": high
            },
            "scan_reports": len(self.scanner.reports)
        }


class ArtifactRepository:
    """Репозиторий артефактов"""
    
    def __init__(self, name: str, artifact_type: ArtifactType):
        self.name = name
        self.artifact_type = artifact_type
        self.artifacts: Dict[str, Dict[str, Artifact]] = defaultdict(dict)
        
    async def publish(self, name: str, version: str, 
                       files: List[Dict[str, Any]],
                       metadata: Dict[str, Any] = None) -> Artifact:
        """Публикация артефакта"""
        artifact = Artifact(
            artifact_id=f"artifact_{uuid.uuid4().hex[:8]}",
            name=name,
            version=version,
            artifact_type=self.artifact_type,
            files=files,
            sha256=hashlib.sha256(json.dumps(files).encode()).hexdigest(),
            size=sum(f.get("size", 0) for f in files),
            metadata=metadata or {}
        )
        
        self.artifacts[name][version] = artifact
        
        return artifact
        
    async def download(self, name: str, version: str) -> Optional[Artifact]:
        """Скачивание артефакта"""
        if name in self.artifacts and version in self.artifacts[name]:
            artifact = self.artifacts[name][version]
            artifact.downloaded_count += 1
            return artifact
            
        return None
        
    def list_versions(self, name: str) -> List[str]:
        """Список версий артефакта"""
        return list(self.artifacts.get(name, {}).keys())
        
    def get_latest(self, name: str) -> Optional[Artifact]:
        """Получение последней версии"""
        versions = self.artifacts.get(name, {})
        if not versions:
            return None
            
        # Сортировка версий (упрощённая)
        sorted_versions = sorted(versions.keys(), reverse=True)
        return versions[sorted_versions[0]]


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 46: Container Registry")
    print("=" * 60)
    
    async def demo():
        # Создание registry
        registry = ContainerRegistry(name="my-registry")
        print("✓ Container Registry created")
        
        # Push образов
        print("\n📦 Pushing images...")
        
        app_image = await registry.push_image(
            repository="myapp",
            tag="v1.0.0",
            layers=[
                {"size": 50000000},  # Base layer
                {"size": 10000000},  # App layer
            ],
            config={"labels": {"maintainer": "team@example.com"}}
        )
        print(f"  ✓ Pushed: myapp:v1.0.0 ({app_image.size / 1024 / 1024:.1f} MB)")
        
        app_image_2 = await registry.push_image(
            repository="myapp",
            tag="v1.1.0",
            layers=[
                {"size": 50000000},
                {"size": 12000000},
            ],
            config={"labels": {"maintainer": "team@example.com"}}
        )
        print(f"  ✓ Pushed: myapp:v1.1.0 ({app_image_2.size / 1024 / 1024:.1f} MB)")
        
        nginx_image = await registry.push_image(
            repository="nginx",
            tag="latest",
            layers=[
                {"size": 30000000},
            ],
            config={}
        )
        print(f"  ✓ Pushed: nginx:latest ({nginx_image.size / 1024 / 1024:.1f} MB)")
        
        # Сканирование
        print("\n🔍 Security Scanning...")
        
        for repo in registry.repositories.values():
            for image in repo.images.values():
                if image.scan_status == ScanStatus.COMPLETED:
                    critical = len([v for v in image.vulnerabilities if v.severity == Severity.CRITICAL])
                    high = len([v for v in image.vulnerabilities if v.severity == Severity.HIGH])
                    print(f"  {image.repository}:{image.tag}")
                    print(f"    Critical: {critical}, High: {high}")
                    
        # Pull образа
        print("\n📥 Pulling images...")
        
        pulled = await registry.pull_image("myapp", "v1.0.0")
        if pulled:
            print(f"  ✓ Pulled: {pulled.repository}:{pulled.tag}")
            print(f"    Pull count: {pulled.pull_count}")
            
        # Retention policy
        print("\n🗑️ Retention Policies...")
        
        policy = registry.retention_manager.create_policy(
            name="keep-latest-5",
            keep_last_n_tags=5,
            keep_tags_matching=["release-"],
            delete_untagged=True,
            max_age_days=90
        )
        print(f"  ✓ Created policy: {policy.name}")
        
        # Replication
        print("\n🔄 Replication...")
        
        rule = registry.replication_manager.create_rule(
            name="replicate-to-dr",
            source_registry="my-registry",
            source_repository="myapp",
            destination_registry="dr-registry",
            mode=ReplicationMode.PUSH,
            tag_filter="v*"
        )
        print(f"  ✓ Created replication rule: {rule.name}")
        
        # Garbage collection
        print("\n♻️ Garbage Collection...")
        
        gc_result = await registry.run_garbage_collection()
        print(f"  Freed space: {gc_result['freed_space_mb']} MB")
        print(f"  Deleted layers: {gc_result['deleted_layers']}")
        
        # Artifact repository
        print("\n📚 Artifact Repository...")
        
        npm_repo = ArtifactRepository("npm-packages", ArtifactType.NPM_PACKAGE)
        
        package = await npm_repo.publish(
            name="my-library",
            version="1.0.0",
            files=[
                {"name": "index.js", "size": 5000},
                {"name": "package.json", "size": 500}
            ],
            metadata={"description": "My awesome library"}
        )
        print(f"  ✓ Published: {package.name}@{package.version}")
        
        # Statistics
        stats = registry.get_statistics()
        print(f"\n📊 Registry Statistics:")
        print(f"  Repositories: {stats['repositories']}")
        print(f"  Images: {stats['images']}")
        print(f"  Layers: {stats['layers']}")
        print(f"  Total size: {stats['total_size_mb']} MB")
        print(f"  Critical vulns: {stats['vulnerabilities']['critical']}")
        print(f"  High vulns: {stats['vulnerabilities']['high']}")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Container Registry & Artifact Management initialized!")
    print("=" * 60)
