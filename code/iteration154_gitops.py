#!/usr/bin/env python3
"""
Server Init - Iteration 154: GitOps Platform
Платформа GitOps

Функционал:
- Repository Management - управление репозиториями
- Application Sync - синхронизация приложений
- Drift Detection - обнаружение дрифта
- Reconciliation - согласование
- Multi-Cluster Deployment - развёртывание в множество кластеров
- RBAC Integration - интеграция RBAC
- Rollback Automation - автоматизация отката
- Webhook Processing - обработка вебхуков
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import hashlib


class SyncStatus(Enum):
    """Статус синхронизации"""
    SYNCED = "synced"
    OUT_OF_SYNC = "out_of_sync"
    UNKNOWN = "unknown"
    PROGRESSING = "progressing"
    DEGRADED = "degraded"


class HealthStatus(Enum):
    """Статус здоровья"""
    HEALTHY = "healthy"
    PROGRESSING = "progressing"
    DEGRADED = "degraded"
    SUSPENDED = "suspended"
    MISSING = "missing"
    UNKNOWN = "unknown"


class OperationPhase(Enum):
    """Фаза операции"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    ERROR = "error"
    TERMINATING = "terminating"


class SyncPolicy(Enum):
    """Политика синхронизации"""
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    AUTOMATIC_PRUNE = "automatic_prune"


class DriftStatus(Enum):
    """Статус дрифта"""
    NO_DRIFT = "no_drift"
    DRIFT_DETECTED = "drift_detected"
    CHECKING = "checking"


@dataclass
class GitRepository:
    """Git репозиторий"""
    repo_id: str
    name: str = ""
    url: str = ""
    
    # Authentication
    auth_type: str = "ssh"  # ssh, https, token
    secret_name: str = ""
    
    # Branch/Path
    branch: str = "main"
    path: str = "/"
    
    # Status
    connected: bool = False
    last_synced: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Application:
    """GitOps приложение"""
    app_id: str
    name: str = ""
    
    # Source
    repo_id: str = ""
    path: str = ""
    target_revision: str = "HEAD"
    
    # Destination
    cluster: str = "default"
    namespace: str = "default"
    
    # Sync
    sync_policy: SyncPolicy = SyncPolicy.MANUAL
    sync_status: SyncStatus = SyncStatus.UNKNOWN
    health_status: HealthStatus = HealthStatus.UNKNOWN
    
    # Drift
    drift_status: DriftStatus = DriftStatus.NO_DRIFT
    drift_resources: List[str] = field(default_factory=list)
    
    # Revision info
    current_revision: str = ""
    target_manifest_hash: str = ""
    live_manifest_hash: str = ""
    
    # Resources
    resources: List[Dict] = field(default_factory=list)
    
    # Timestamps
    last_synced: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SyncOperation:
    """Операция синхронизации"""
    operation_id: str
    app_id: str = ""
    
    # Status
    phase: OperationPhase = OperationPhase.PENDING
    message: str = ""
    
    # Revision
    revision: str = ""
    
    # Resources
    resources_synced: int = 0
    resources_failed: int = 0
    
    # Timing
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    
    # Prune
    prune_enabled: bool = False
    resources_pruned: int = 0


@dataclass
class Cluster:
    """Kubernetes кластер"""
    cluster_id: str
    name: str = ""
    
    # Connection
    server: str = ""
    config_secret: str = ""
    
    # Status
    connected: bool = False
    version: str = ""
    
    # Namespaces
    namespaces: List[str] = field(default_factory=list)
    
    # Metadata
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)


@dataclass
class ApplicationSet:
    """Набор приложений"""
    set_id: str
    name: str = ""
    
    # Template
    template: Dict = field(default_factory=dict)
    
    # Generators
    generators: List[Dict] = field(default_factory=list)
    
    # Generated apps
    applications: List[str] = field(default_factory=list)


@dataclass
class Webhook:
    """Вебхук"""
    webhook_id: str
    
    # Source
    source: str = "github"  # github, gitlab, bitbucket
    repository: str = ""
    
    # Event
    event_type: str = ""  # push, pull_request, tag
    ref: str = ""
    commit: str = ""
    
    # Processing
    processed: bool = False
    triggered_syncs: List[str] = field(default_factory=list)
    
    # Timestamp
    received_at: datetime = field(default_factory=datetime.now)


@dataclass
class Rollback:
    """Откат"""
    rollback_id: str
    app_id: str = ""
    
    # Revision
    from_revision: str = ""
    to_revision: str = ""
    
    # Status
    phase: OperationPhase = OperationPhase.PENDING
    
    # Reason
    reason: str = ""
    initiated_by: str = ""
    
    # Timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class DriftReport:
    """Отчёт о дрифте"""
    report_id: str
    app_id: str = ""
    
    # Findings
    drift_detected: bool = False
    drifted_resources: List[Dict] = field(default_factory=list)
    
    # Comparison
    expected_hash: str = ""
    actual_hash: str = ""
    
    # Timestamp
    checked_at: datetime = field(default_factory=datetime.now)


class RepositoryManager:
    """Менеджер репозиториев"""
    
    def __init__(self):
        self.repositories: Dict[str, GitRepository] = {}
        
    def add_repository(self, name: str, url: str, **kwargs) -> GitRepository:
        """Добавление репозитория"""
        repo = GitRepository(
            repo_id=f"repo_{uuid.uuid4().hex[:8]}",
            name=name,
            url=url,
            **kwargs
        )
        self.repositories[repo.repo_id] = repo
        return repo
        
    async def refresh(self, repo_id: str) -> bool:
        """Обновление репозитория"""
        repo = self.repositories.get(repo_id)
        if not repo:
            return False
            
        # Simulate git fetch
        await asyncio.sleep(0.1)
        repo.connected = True
        repo.last_synced = datetime.now()
        
        return True
        
    def get_manifest(self, repo_id: str, path: str, revision: str) -> Dict:
        """Получение манифеста"""
        # Simulate reading from git
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "app", "namespace": "default"},
            "spec": {"replicas": 3}
        }


class ClusterManager:
    """Менеджер кластеров"""
    
    def __init__(self):
        self.clusters: Dict[str, Cluster] = {}
        
    def add_cluster(self, name: str, server: str, **kwargs) -> Cluster:
        """Добавление кластера"""
        cluster = Cluster(
            cluster_id=f"cluster_{uuid.uuid4().hex[:8]}",
            name=name,
            server=server,
            **kwargs
        )
        self.clusters[cluster.cluster_id] = cluster
        return cluster
        
    async def connect(self, cluster_id: str) -> bool:
        """Подключение к кластеру"""
        cluster = self.clusters.get(cluster_id)
        if not cluster:
            return False
            
        # Simulate connection
        await asyncio.sleep(0.05)
        cluster.connected = True
        cluster.version = "1.28.0"
        cluster.namespaces = ["default", "kube-system", "monitoring", "apps"]
        
        return True
        
    def get_resources(self, cluster_id: str, namespace: str) -> List[Dict]:
        """Получение ресурсов кластера"""
        # Simulate K8s API call
        return [
            {"kind": "Deployment", "name": "api", "replicas": 3},
            {"kind": "Service", "name": "api-svc", "type": "ClusterIP"}
        ]


class ApplicationManager:
    """Менеджер приложений"""
    
    def __init__(self, repo_manager: RepositoryManager, 
                 cluster_manager: ClusterManager):
        self.repo_manager = repo_manager
        self.cluster_manager = cluster_manager
        self.applications: Dict[str, Application] = {}
        self.operations: List[SyncOperation] = []
        
    def create_application(self, name: str, repo_id: str, path: str,
                            cluster: str, namespace: str,
                            **kwargs) -> Application:
        """Создание приложения"""
        app = Application(
            app_id=f"app_{uuid.uuid4().hex[:8]}",
            name=name,
            repo_id=repo_id,
            path=path,
            cluster=cluster,
            namespace=namespace,
            **kwargs
        )
        self.applications[app.app_id] = app
        return app
        
    async def sync(self, app_id: str, prune: bool = False,
                    force: bool = False) -> SyncOperation:
        """Синхронизация приложения"""
        app = self.applications.get(app_id)
        if not app:
            raise ValueError(f"Application not found: {app_id}")
            
        operation = SyncOperation(
            operation_id=f"sync_{uuid.uuid4().hex[:8]}",
            app_id=app_id,
            phase=OperationPhase.RUNNING,
            started_at=datetime.now(),
            prune_enabled=prune
        )
        
        self.operations.append(operation)
        
        try:
            # Get manifests from git
            manifest = self.repo_manager.get_manifest(
                app.repo_id, app.path, app.target_revision
            )
            app.target_manifest_hash = self._hash_manifest(manifest)
            
            # Simulate apply
            await asyncio.sleep(0.1)
            
            # Update application state
            app.sync_status = SyncStatus.SYNCED
            app.health_status = HealthStatus.HEALTHY
            app.current_revision = app.target_revision
            app.live_manifest_hash = app.target_manifest_hash
            app.last_synced = datetime.now()
            app.drift_status = DriftStatus.NO_DRIFT
            app.drift_resources = []
            
            operation.phase = OperationPhase.SUCCEEDED
            operation.resources_synced = 3  # Simulated
            operation.message = "Successfully synced"
            
        except Exception as e:
            operation.phase = OperationPhase.FAILED
            operation.message = str(e)
            app.sync_status = SyncStatus.OUT_OF_SYNC
            
        operation.finished_at = datetime.now()
        return operation
        
    def _hash_manifest(self, manifest: Dict) -> str:
        """Хэширование манифеста"""
        content = json.dumps(manifest, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
        
    async def refresh(self, app_id: str) -> Application:
        """Обновление статуса приложения"""
        app = self.applications.get(app_id)
        if not app:
            raise ValueError(f"Application not found: {app_id}")
            
        # Get current state from cluster
        live_resources = self.cluster_manager.get_resources(
            app.cluster, app.namespace
        )
        
        # Compare with desired state
        manifest = self.repo_manager.get_manifest(
            app.repo_id, app.path, app.target_revision
        )
        
        target_hash = self._hash_manifest(manifest)
        
        if app.live_manifest_hash != target_hash:
            app.sync_status = SyncStatus.OUT_OF_SYNC
        else:
            app.sync_status = SyncStatus.SYNCED
            
        return app


class DriftDetector:
    """Детектор дрифта"""
    
    def __init__(self, app_manager: ApplicationManager):
        self.app_manager = app_manager
        
    async def check_drift(self, app_id: str) -> DriftReport:
        """Проверка дрифта"""
        app = self.app_manager.applications.get(app_id)
        if not app:
            raise ValueError(f"Application not found: {app_id}")
            
        report = DriftReport(
            report_id=f"drift_{uuid.uuid4().hex[:8]}",
            app_id=app_id,
            expected_hash=app.target_manifest_hash,
            actual_hash=app.live_manifest_hash
        )
        
        # Simulate drift detection
        await asyncio.sleep(0.05)
        
        # Check for drift (simulated)
        import random
        if random.random() < 0.3:  # 30% chance of drift
            report.drift_detected = True
            app.drift_status = DriftStatus.DRIFT_DETECTED
            
            # Simulated drifted resources
            report.drifted_resources = [
                {
                    "kind": "Deployment",
                    "name": "api",
                    "field": "spec.replicas",
                    "expected": 3,
                    "actual": 2
                }
            ]
            app.drift_resources = ["Deployment/api"]
        else:
            report.drift_detected = False
            app.drift_status = DriftStatus.NO_DRIFT
            app.drift_resources = []
            
        return report
        
    async def check_all(self) -> List[DriftReport]:
        """Проверка всех приложений"""
        reports = []
        for app_id in self.app_manager.applications:
            report = await self.check_drift(app_id)
            reports.append(report)
        return reports


class RollbackManager:
    """Менеджер откатов"""
    
    def __init__(self, app_manager: ApplicationManager):
        self.app_manager = app_manager
        self.rollbacks: List[Rollback] = []
        self.history: Dict[str, List[str]] = {}  # app_id -> [revisions]
        
    def record_revision(self, app_id: str, revision: str):
        """Запись ревизии"""
        if app_id not in self.history:
            self.history[app_id] = []
        self.history[app_id].append(revision)
        
        # Keep last 10 revisions
        self.history[app_id] = self.history[app_id][-10:]
        
    async def rollback(self, app_id: str, to_revision: str = None,
                        reason: str = "", initiated_by: str = "") -> Rollback:
        """Откат приложения"""
        app = self.app_manager.applications.get(app_id)
        if not app:
            raise ValueError(f"Application not found: {app_id}")
            
        # Determine target revision
        if not to_revision:
            history = self.history.get(app_id, [])
            if len(history) < 2:
                raise ValueError("No previous revision to rollback to")
            to_revision = history[-2]
            
        rollback = Rollback(
            rollback_id=f"rb_{uuid.uuid4().hex[:8]}",
            app_id=app_id,
            from_revision=app.current_revision,
            to_revision=to_revision,
            reason=reason,
            initiated_by=initiated_by,
            started_at=datetime.now()
        )
        
        self.rollbacks.append(rollback)
        
        # Perform rollback
        app.target_revision = to_revision
        operation = await self.app_manager.sync(app_id)
        
        if operation.phase == OperationPhase.SUCCEEDED:
            rollback.phase = OperationPhase.SUCCEEDED
        else:
            rollback.phase = OperationPhase.FAILED
            
        rollback.completed_at = datetime.now()
        return rollback
        
    def get_history(self, app_id: str) -> List[str]:
        """История ревизий"""
        return self.history.get(app_id, [])


class WebhookProcessor:
    """Обработчик вебхуков"""
    
    def __init__(self, app_manager: ApplicationManager):
        self.app_manager = app_manager
        self.webhooks: List[Webhook] = []
        
    async def process(self, payload: Dict, source: str = "github") -> Webhook:
        """Обработка вебхука"""
        webhook = Webhook(
            webhook_id=f"wh_{uuid.uuid4().hex[:8]}",
            source=source,
            repository=payload.get("repository", {}).get("full_name", ""),
            event_type=payload.get("event", "push"),
            ref=payload.get("ref", ""),
            commit=payload.get("after", payload.get("commit", ""))
        )
        
        self.webhooks.append(webhook)
        
        # Find matching applications
        triggered = []
        for app in self.app_manager.applications.values():
            if app.sync_policy == SyncPolicy.AUTOMATIC:
                # Check if repo matches
                repo = self.app_manager.repo_manager.repositories.get(app.repo_id)
                if repo and webhook.repository in repo.url:
                    operation = await self.app_manager.sync(app.app_id)
                    triggered.append(operation.operation_id)
                    
        webhook.triggered_syncs = triggered
        webhook.processed = True
        
        return webhook


class ApplicationSetController:
    """Контроллер наборов приложений"""
    
    def __init__(self, app_manager: ApplicationManager):
        self.app_manager = app_manager
        self.sets: Dict[str, ApplicationSet] = {}
        
    def create_set(self, name: str, template: Dict,
                    generators: List[Dict]) -> ApplicationSet:
        """Создание набора"""
        app_set = ApplicationSet(
            set_id=f"set_{uuid.uuid4().hex[:8]}",
            name=name,
            template=template,
            generators=generators
        )
        self.sets[app_set.set_id] = app_set
        return app_set
        
    async def reconcile(self, set_id: str) -> List[Application]:
        """Согласование набора"""
        app_set = self.sets.get(set_id)
        if not app_set:
            return []
            
        created_apps = []
        
        # Process generators
        for generator in app_set.generators:
            gen_type = generator.get("type")
            
            if gen_type == "list":
                elements = generator.get("elements", [])
                for element in elements:
                    app = self._create_from_template(app_set.template, element)
                    created_apps.append(app)
                    app_set.applications.append(app.app_id)
                    
            elif gen_type == "cluster":
                # Generate app per cluster
                for cluster in self.app_manager.cluster_manager.clusters.values():
                    element = {"cluster": cluster.name}
                    app = self._create_from_template(app_set.template, element)
                    created_apps.append(app)
                    app_set.applications.append(app.app_id)
                    
        return created_apps
        
    def _create_from_template(self, template: Dict, values: Dict) -> Application:
        """Создание из шаблона"""
        name = template.get("name", "app") + "-" + values.get("cluster", "default")
        
        return self.app_manager.create_application(
            name=name,
            repo_id=template.get("repo_id", ""),
            path=template.get("path", ""),
            cluster=values.get("cluster", "default"),
            namespace=template.get("namespace", "default"),
            sync_policy=SyncPolicy[template.get("sync_policy", "MANUAL").upper()]
        )


class GitOpsPlatform:
    """Платформа GitOps"""
    
    def __init__(self):
        self.repo_manager = RepositoryManager()
        self.cluster_manager = ClusterManager()
        self.app_manager = ApplicationManager(self.repo_manager, self.cluster_manager)
        self.drift_detector = DriftDetector(self.app_manager)
        self.rollback_manager = RollbackManager(self.app_manager)
        self.webhook_processor = WebhookProcessor(self.app_manager)
        self.appset_controller = ApplicationSetController(self.app_manager)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        apps = list(self.app_manager.applications.values())
        
        synced = len([a for a in apps if a.sync_status == SyncStatus.SYNCED])
        healthy = len([a for a in apps if a.health_status == HealthStatus.HEALTHY])
        drifted = len([a for a in apps if a.drift_status == DriftStatus.DRIFT_DETECTED])
        
        return {
            "total_repositories": len(self.repo_manager.repositories),
            "total_clusters": len(self.cluster_manager.clusters),
            "total_applications": len(apps),
            "synced_applications": synced,
            "healthy_applications": healthy,
            "drifted_applications": drifted,
            "total_sync_operations": len(self.app_manager.operations),
            "total_rollbacks": len(self.rollback_manager.rollbacks),
            "webhooks_processed": len(self.webhook_processor.webhooks),
            "application_sets": len(self.appset_controller.sets)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 154: GitOps Platform")
    print("=" * 60)
    
    async def demo():
        platform = GitOpsPlatform()
        print("✓ GitOps Platform created")
        
        # Add repositories
        print("\n📁 Adding Git Repositories...")
        
        repos_data = [
            ("platform-apps", "git@github.com:company/platform-apps.git", "main"),
            ("infra-configs", "git@github.com:company/infra-configs.git", "main"),
            ("microservices", "git@github.com:company/microservices.git", "develop")
        ]
        
        for name, url, branch in repos_data:
            repo = platform.repo_manager.add_repository(name, url, branch=branch)
            await platform.repo_manager.refresh(repo.repo_id)
            print(f"  ✓ {name}: {branch} branch")
            
        # Add clusters
        print("\n☸️ Adding Kubernetes Clusters...")
        
        clusters_data = [
            ("production", "https://k8s-prod.company.com:6443"),
            ("staging", "https://k8s-staging.company.com:6443"),
            ("development", "https://k8s-dev.company.com:6443")
        ]
        
        for name, server in clusters_data:
            cluster = platform.cluster_manager.add_cluster(name, server)
            await platform.cluster_manager.connect(cluster.cluster_id)
            print(f"  ✓ {name}: {cluster.version}")
            
        # Create applications
        print("\n📦 Creating Applications...")
        
        repo_ids = list(platform.repo_manager.repositories.keys())
        cluster_names = ["production", "staging", "development"]
        
        apps_data = [
            ("api-gateway", repo_ids[0], "/apps/api-gateway", "production", "api", SyncPolicy.AUTOMATIC),
            ("user-service", repo_ids[0], "/apps/user-service", "production", "services", SyncPolicy.AUTOMATIC),
            ("order-service", repo_ids[0], "/apps/order-service", "production", "services", SyncPolicy.MANUAL),
            ("monitoring", repo_ids[1], "/monitoring", "production", "monitoring", SyncPolicy.AUTOMATIC),
            ("staging-api", repo_ids[0], "/apps/api-gateway", "staging", "api", SyncPolicy.AUTOMATIC)
        ]
        
        for name, repo_id, path, cluster, ns, policy in apps_data:
            app = platform.app_manager.create_application(
                name, repo_id, path, cluster, ns,
                sync_policy=policy
            )
            print(f"  ✓ {name}: {cluster}/{ns} ({policy.value})")
            
        # Sync applications
        print("\n🔄 Syncing Applications...")
        
        for app in platform.app_manager.applications.values():
            operation = await platform.app_manager.sync(app.app_id)
            platform.rollback_manager.record_revision(app.app_id, "rev-" + uuid.uuid4().hex[:6])
            
            status_icon = "✓" if operation.phase == OperationPhase.SUCCEEDED else "✗"
            print(f"  {status_icon} {app.name}: {operation.phase.value}")
            
        # Check drift
        print("\n🔍 Checking for Drift...")
        
        reports = await platform.drift_detector.check_all()
        
        drift_count = 0
        for report in reports:
            app = platform.app_manager.applications[report.app_id]
            if report.drift_detected:
                drift_count += 1
                print(f"  ⚠️ {app.name}: DRIFT DETECTED")
                for resource in report.drifted_resources:
                    print(f"      {resource['kind']}/{resource['name']}: {resource['field']}")
            else:
                print(f"  ✓ {app.name}: No drift")
                
        print(f"\n  Total drifted: {drift_count}/{len(reports)}")
        
        # Simulate webhook
        print("\n🪝 Processing Webhook...")
        
        webhook_payload = {
            "event": "push",
            "repository": {"full_name": "company/platform-apps"},
            "ref": "refs/heads/main",
            "after": "abc123def456"
        }
        
        webhook = await platform.webhook_processor.process(webhook_payload)
        print(f"  ✓ Received: {webhook.event_type} to {webhook.repository}")
        print(f"    Triggered syncs: {len(webhook.triggered_syncs)}")
        
        # Show application status
        print("\n📊 Application Status:")
        print("  ┌─────────────────────────────────────────────────────────────────────────┐")
        print("  │ Application      │ Cluster    │ Sync       │ Health     │ Drift        │")
        print("  ├─────────────────────────────────────────────────────────────────────────┤")
        
        sync_icons = {
            SyncStatus.SYNCED: "✓",
            SyncStatus.OUT_OF_SYNC: "✗",
            SyncStatus.UNKNOWN: "?",
            SyncStatus.PROGRESSING: "⟳"
        }
        
        health_icons = {
            HealthStatus.HEALTHY: "✓",
            HealthStatus.DEGRADED: "✗",
            HealthStatus.PROGRESSING: "⟳",
            HealthStatus.UNKNOWN: "?"
        }
        
        drift_icons = {
            DriftStatus.NO_DRIFT: "✓",
            DriftStatus.DRIFT_DETECTED: "⚠",
            DriftStatus.CHECKING: "?"
        }
        
        for app in platform.app_manager.applications.values():
            sync = f"{sync_icons.get(app.sync_status, '?')} {app.sync_status.value}"
            health = f"{health_icons.get(app.health_status, '?')} {app.health_status.value}"
            drift = f"{drift_icons.get(app.drift_status, '?')} {app.drift_status.value}"
            print(f"  │ {app.name:16} │ {app.cluster:10} │ {sync:10} │ {health:10} │ {drift:12} │")
            
        print("  └─────────────────────────────────────────────────────────────────────────┘")
        
        # Perform rollback
        print("\n⏪ Performing Rollback...")
        
        # Find an app to rollback
        app_to_rollback = list(platform.app_manager.applications.values())[0]
        
        # Record another revision first
        platform.rollback_manager.record_revision(app_to_rollback.app_id, "rev-new123")
        
        rollback = await platform.rollback_manager.rollback(
            app_to_rollback.app_id,
            reason="Performance degradation",
            initiated_by="oncall@company.com"
        )
        
        print(f"  ✓ Rolled back {app_to_rollback.name}")
        print(f"    From: {rollback.from_revision}")
        print(f"    To: {rollback.to_revision}")
        print(f"    Status: {rollback.phase.value}")
        
        # Create ApplicationSet
        print("\n📋 Creating ApplicationSet...")
        
        app_set = platform.appset_controller.create_set(
            "multi-cluster-app",
            template={
                "name": "nginx",
                "repo_id": repo_ids[1],
                "path": "/apps/nginx",
                "namespace": "web",
                "sync_policy": "AUTOMATIC"
            },
            generators=[
                {
                    "type": "cluster"
                }
            ]
        )
        
        generated = await platform.appset_controller.reconcile(app_set.set_id)
        print(f"  ✓ Created ApplicationSet: {app_set.name}")
        print(f"    Generated {len(generated)} applications")
        
        # Sync operations history
        print("\n📜 Recent Sync Operations:")
        
        for op in platform.app_manager.operations[-5:]:
            app = platform.app_manager.applications.get(op.app_id)
            app_name = app.name if app else "unknown"
            phase_icon = "✓" if op.phase == OperationPhase.SUCCEEDED else "✗"
            duration = ""
            if op.started_at and op.finished_at:
                dur = (op.finished_at - op.started_at).total_seconds()
                duration = f" ({dur:.1f}s)"
            print(f"  {phase_icon} {app_name}: {op.phase.value}{duration}")
            
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Repositories: {stats['total_repositories']}")
        print(f"  Clusters: {stats['total_clusters']}")
        print(f"  Applications: {stats['total_applications']}")
        print(f"  Synced: {stats['synced_applications']}")
        print(f"  Healthy: {stats['healthy_applications']}")
        print(f"  Drifted: {stats['drifted_applications']}")
        print(f"  Sync Operations: {stats['total_sync_operations']}")
        print(f"  Rollbacks: {stats['total_rollbacks']}")
        print(f"  Webhooks: {stats['webhooks_processed']}")
        
        # Dashboard
        print("\n📋 GitOps Dashboard:")
        print("  ┌────────────────────────────────────────────────────────────┐")
        print("  │                     GitOps Overview                        │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Repositories:          {stats['total_repositories']:>10}                    │")
        print(f"  │ Clusters:              {stats['total_clusters']:>10}                    │")
        print(f"  │ Applications:          {stats['total_applications']:>10}                    │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Synced:                {stats['synced_applications']:>10}                    │")
        print(f"  │ Healthy:               {stats['healthy_applications']:>10}                    │")
        print(f"  │ Drifted:               {stats['drifted_applications']:>10}                    │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Sync Operations:       {stats['total_sync_operations']:>10}                    │")
        print(f"  │ Rollbacks:             {stats['total_rollbacks']:>10}                    │")
        print("  └────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("GitOps Platform initialized!")
    print("=" * 60)
