#!/usr/bin/env python3
"""
Server Init - Iteration 106: GitOps Platform
Платформа GitOps

Функционал:
- Repository Management - управление репозиториями
- Application Sync - синхронизация приложений
- Declarative Configuration - декларативная конфигурация
- Drift Detection - обнаружение отклонений
- Automated Sync - автоматическая синхронизация
- Rollback Management - управление откатами
- Multi-Cluster Support - поддержка кластеров
- Webhook Integration - интеграция вебхуков
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
from collections import defaultdict
import uuid
import random
import hashlib


class SyncStatus(Enum):
    """Статус синхронизации"""
    SYNCED = "synced"
    OUT_OF_SYNC = "out_of_sync"
    SYNCING = "syncing"
    FAILED = "failed"
    UNKNOWN = "unknown"


class HealthStatus(Enum):
    """Статус здоровья"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    PROGRESSING = "progressing"
    SUSPENDED = "suspended"
    MISSING = "missing"
    UNKNOWN = "unknown"


class SyncPolicy(Enum):
    """Политика синхронизации"""
    MANUAL = "manual"
    AUTOMATED = "automated"
    AUTOMATED_PRUNE = "automated_prune"


class SourceType(Enum):
    """Тип источника"""
    GIT = "git"
    HELM = "helm"
    KUSTOMIZE = "kustomize"
    DIRECTORY = "directory"


@dataclass
class Repository:
    """Репозиторий"""
    repo_id: str
    
    # Basic info
    name: str = ""
    url: str = ""
    
    # Credentials
    ssh_key_ref: Optional[str] = None
    username: Optional[str] = None
    password_ref: Optional[str] = None
    
    # Settings
    insecure: bool = False
    enable_lfs: bool = False
    
    # Status
    connected: bool = True
    last_sync: Optional[datetime] = None


@dataclass
class Cluster:
    """Кластер"""
    cluster_id: str
    
    # Basic info
    name: str = ""
    server: str = ""
    
    # Config
    config_ref: Optional[str] = None
    namespace_default: str = "default"
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Status
    connected: bool = True
    version: str = ""


@dataclass
class ApplicationSource:
    """Источник приложения"""
    repo_url: str = ""
    path: str = ""
    target_revision: str = "HEAD"
    
    # Type
    source_type: SourceType = SourceType.GIT
    
    # Helm specific
    helm_values: Dict[str, Any] = field(default_factory=dict)
    helm_chart: str = ""
    
    # Kustomize specific
    kustomize_images: List[str] = field(default_factory=list)


@dataclass
class ApplicationDestination:
    """Назначение приложения"""
    server: str = ""
    namespace: str = "default"
    cluster_name: str = ""


@dataclass
class SyncResult:
    """Результат синхронизации"""
    revision: str = ""
    started_at: datetime = field(default_factory=datetime.now)
    finished_at: Optional[datetime] = None
    
    # Status
    phase: str = ""  # Succeeded, Failed, Running
    message: str = ""
    
    # Resources
    resources_synced: int = 0
    resources_failed: int = 0


@dataclass
class ResourceDrift:
    """Отклонение ресурса"""
    drift_id: str
    
    # Resource
    resource_kind: str = ""
    resource_name: str = ""
    resource_namespace: str = ""
    
    # Drift details
    live_state: Dict[str, Any] = field(default_factory=dict)
    target_state: Dict[str, Any] = field(default_factory=dict)
    diff: List[str] = field(default_factory=list)
    
    # Detection
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class Application:
    """Приложение"""
    app_id: str
    name: str = ""
    
    # Project
    project: str = "default"
    
    # Source & Destination
    source: ApplicationSource = field(default_factory=ApplicationSource)
    destination: ApplicationDestination = field(default_factory=ApplicationDestination)
    
    # Sync policy
    sync_policy: SyncPolicy = SyncPolicy.MANUAL
    auto_prune: bool = False
    self_heal: bool = False
    
    # Status
    sync_status: SyncStatus = SyncStatus.UNKNOWN
    health_status: HealthStatus = HealthStatus.UNKNOWN
    
    # Current state
    current_revision: str = ""
    
    # History
    sync_history: List[SyncResult] = field(default_factory=list)
    
    # Drifts
    drifts: List[ResourceDrift] = field(default_factory=list)
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_synced_at: Optional[datetime] = None


@dataclass
class Project:
    """Проект"""
    project_id: str
    name: str = ""
    
    # Allowed sources
    source_repos: List[str] = field(default_factory=lambda: ["*"])
    
    # Allowed destinations
    destinations: List[Dict[str, str]] = field(default_factory=list)
    
    # Cluster resource allow/deny
    cluster_resource_whitelist: List[Dict[str, str]] = field(default_factory=list)
    cluster_resource_blacklist: List[Dict[str, str]] = field(default_factory=list)


class RepositoryManager:
    """Менеджер репозиториев"""
    
    def __init__(self):
        self.repositories: Dict[str, Repository] = {}
        
    def add(self, name: str, url: str, **kwargs) -> Repository:
        """Добавление репозитория"""
        repo = Repository(
            repo_id=f"repo_{uuid.uuid4().hex[:8]}",
            name=name,
            url=url,
            **kwargs
        )
        self.repositories[repo.repo_id] = repo
        return repo
        
    def validate(self, repo_id: str) -> bool:
        """Валидация репозитория"""
        repo = self.repositories.get(repo_id)
        if not repo:
            return False
            
        # Simulate validation
        repo.connected = random.random() > 0.1
        repo.last_sync = datetime.now()
        return repo.connected
        
    def get_revision(self, repo_id: str, branch: str = "main") -> Optional[str]:
        """Получение ревизии"""
        if repo_id in self.repositories:
            # Simulate git revision
            return hashlib.sha1(f"{repo_id}{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        return None


class ClusterManager:
    """Менеджер кластеров"""
    
    def __init__(self):
        self.clusters: Dict[str, Cluster] = {}
        
    def register(self, name: str, server: str, **kwargs) -> Cluster:
        """Регистрация кластера"""
        cluster = Cluster(
            cluster_id=f"cluster_{uuid.uuid4().hex[:8]}",
            name=name,
            server=server,
            **kwargs
        )
        self.clusters[cluster.cluster_id] = cluster
        return cluster
        
    def health_check(self, cluster_id: str) -> Dict[str, Any]:
        """Проверка здоровья"""
        cluster = self.clusters.get(cluster_id)
        if not cluster:
            return {"status": "unknown"}
            
        # Simulate health check
        cluster.connected = random.random() > 0.05
        cluster.version = "v1.28.0"
        
        return {
            "cluster": cluster.name,
            "connected": cluster.connected,
            "version": cluster.version
        }


class DriftDetector:
    """Детектор отклонений"""
    
    def detect(self, app: Application, live_state: Dict[str, Any],
                desired_state: Dict[str, Any]) -> List[ResourceDrift]:
        """Обнаружение отклонений"""
        drifts = []
        
        # Compare states
        for resource_key, desired in desired_state.items():
            live = live_state.get(resource_key, {})
            
            if live != desired:
                # Find differences
                diff = []
                for key in set(list(desired.keys()) + list(live.keys())):
                    if desired.get(key) != live.get(key):
                        diff.append(f"{key}: {live.get(key)} → {desired.get(key)}")
                        
                if diff:
                    drift = ResourceDrift(
                        drift_id=f"drift_{uuid.uuid4().hex[:8]}",
                        resource_kind=desired.get("kind", "unknown"),
                        resource_name=resource_key,
                        resource_namespace=desired.get("namespace", "default"),
                        live_state=live,
                        target_state=desired,
                        diff=diff
                    )
                    drifts.append(drift)
                    
        return drifts


class SyncEngine:
    """Движок синхронизации"""
    
    def __init__(self, repo_manager: RepositoryManager,
                  cluster_manager: ClusterManager):
        self.repo_manager = repo_manager
        self.cluster_manager = cluster_manager
        self.drift_detector = DriftDetector()
        
    async def sync(self, app: Application,
                    prune: bool = False,
                    dry_run: bool = False) -> SyncResult:
        """Синхронизация приложения"""
        result = SyncResult(
            revision=self.repo_manager.get_revision(
                app.source.repo_url,
                app.source.target_revision
            ) or "unknown"
        )
        
        app.sync_status = SyncStatus.SYNCING
        
        # Simulate sync
        await asyncio.sleep(0.1)
        
        success = random.random() > 0.1
        
        if success:
            result.phase = "Succeeded"
            result.resources_synced = random.randint(5, 20)
            app.sync_status = SyncStatus.SYNCED
            app.health_status = HealthStatus.HEALTHY
            app.current_revision = result.revision
        else:
            result.phase = "Failed"
            result.message = "Failed to apply manifests"
            result.resources_failed = random.randint(1, 3)
            app.sync_status = SyncStatus.FAILED
            app.health_status = HealthStatus.DEGRADED
            
        result.finished_at = datetime.now()
        app.last_synced_at = result.finished_at
        app.sync_history.append(result)
        
        return result
        
    async def refresh(self, app: Application) -> Dict[str, Any]:
        """Обновление состояния"""
        # Get current revision
        new_revision = self.repo_manager.get_revision(
            app.source.repo_url,
            app.source.target_revision
        )
        
        if new_revision and new_revision != app.current_revision:
            app.sync_status = SyncStatus.OUT_OF_SYNC
            
        # Simulate drift detection
        if random.random() > 0.7:
            drift = ResourceDrift(
                drift_id=f"drift_{uuid.uuid4().hex[:8]}",
                resource_kind="Deployment",
                resource_name=f"{app.name}-deployment",
                resource_namespace=app.destination.namespace,
                diff=["replicas: 3 → 2", "image: v1.0.0 → v1.0.1"]
            )
            app.drifts.append(drift)
            
        return {
            "app": app.name,
            "current_revision": app.current_revision,
            "target_revision": new_revision,
            "sync_status": app.sync_status.value,
            "drifts": len(app.drifts)
        }


class ApplicationManager:
    """Менеджер приложений"""
    
    def __init__(self, sync_engine: SyncEngine):
        self.applications: Dict[str, Application] = {}
        self.sync_engine = sync_engine
        
    def create(self, name: str, repo_url: str, path: str,
                cluster: str, namespace: str = "default",
                sync_policy: SyncPolicy = SyncPolicy.MANUAL,
                **kwargs) -> Application:
        """Создание приложения"""
        app = Application(
            app_id=f"app_{uuid.uuid4().hex[:8]}",
            name=name,
            source=ApplicationSource(
                repo_url=repo_url,
                path=path,
                **{k: v for k, v in kwargs.items() if k in ['target_revision', 'source_type', 'helm_values']}
            ),
            destination=ApplicationDestination(
                cluster_name=cluster,
                namespace=namespace
            ),
            sync_policy=sync_policy
        )
        self.applications[app.app_id] = app
        return app
        
    async def sync(self, app_id: str, **kwargs) -> SyncResult:
        """Синхронизация"""
        app = self.applications.get(app_id)
        if not app:
            return SyncResult(phase="Failed", message="App not found")
            
        return await self.sync_engine.sync(app, **kwargs)
        
    async def rollback(self, app_id: str, revision: str) -> SyncResult:
        """Откат"""
        app = self.applications.get(app_id)
        if not app:
            return SyncResult(phase="Failed", message="App not found")
            
        # Find revision in history
        for sync_result in reversed(app.sync_history):
            if sync_result.revision == revision:
                # Perform rollback sync
                app.source.target_revision = revision
                return await self.sync_engine.sync(app)
                
        return SyncResult(phase="Failed", message=f"Revision {revision} not found")
        
    def get_out_of_sync(self) -> List[Application]:
        """Приложения с отклонениями"""
        return [
            app for app in self.applications.values()
            if app.sync_status == SyncStatus.OUT_OF_SYNC
        ]


class WebhookHandler:
    """Обработчик вебхуков"""
    
    def __init__(self, app_manager: ApplicationManager):
        self.app_manager = app_manager
        self.events: List[Dict[str, Any]] = []
        
    async def handle_push(self, repo_url: str, branch: str,
                           commit_sha: str) -> List[str]:
        """Обработка push события"""
        synced_apps = []
        
        for app in self.app_manager.applications.values():
            if app.source.repo_url == repo_url:
                if app.sync_policy == SyncPolicy.AUTOMATED:
                    await self.app_manager.sync(app.app_id)
                    synced_apps.append(app.name)
                else:
                    app.sync_status = SyncStatus.OUT_OF_SYNC
                    
        self.events.append({
            "type": "push",
            "repo_url": repo_url,
            "branch": branch,
            "commit": commit_sha,
            "synced_apps": synced_apps,
            "timestamp": datetime.now().isoformat()
        })
        
        return synced_apps


class GitOpsPlatform:
    """Платформа GitOps"""
    
    def __init__(self):
        self.repo_manager = RepositoryManager()
        self.cluster_manager = ClusterManager()
        self.sync_engine = SyncEngine(self.repo_manager, self.cluster_manager)
        self.app_manager = ApplicationManager(self.sync_engine)
        self.webhook_handler = WebhookHandler(self.app_manager)
        
        self.projects: Dict[str, Project] = {}
        
    def create_project(self, name: str, **kwargs) -> Project:
        """Создание проекта"""
        project = Project(
            project_id=f"proj_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        self.projects[project.project_id] = project
        return project
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        apps = list(self.app_manager.applications.values())
        
        sync_status_counts = defaultdict(int)
        health_status_counts = defaultdict(int)
        
        for app in apps:
            sync_status_counts[app.sync_status.value] += 1
            health_status_counts[app.health_status.value] += 1
            
        total_drifts = sum(len(app.drifts) for app in apps)
        
        return {
            "repositories": len(self.repo_manager.repositories),
            "clusters": len(self.cluster_manager.clusters),
            "projects": len(self.projects),
            "applications": len(apps),
            "sync_status": dict(sync_status_counts),
            "health_status": dict(health_status_counts),
            "total_drifts": total_drifts,
            "webhook_events": len(self.webhook_handler.events)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 106: GitOps Platform")
    print("=" * 60)
    
    async def demo():
        platform = GitOpsPlatform()
        print("✓ GitOps Platform created")
        
        # Register repositories
        print("\n📦 Registering Repositories...")
        
        repos = [
            ("platform-apps", "https://github.com/company/platform-apps.git"),
            ("microservices", "https://github.com/company/microservices.git"),
            ("infrastructure", "https://github.com/company/infrastructure.git"),
            ("helm-charts", "https://github.com/company/helm-charts.git")
        ]
        
        for name, url in repos:
            repo = platform.repo_manager.add(name, url)
            valid = platform.repo_manager.validate(repo.repo_id)
            status = "✓" if valid else "✗"
            print(f"  {status} {name}")
            
        # Register clusters
        print("\n☸️ Registering Clusters...")
        
        clusters = [
            ("production", "https://k8s-prod.company.com", {"env": "prod", "region": "us-east-1"}),
            ("staging", "https://k8s-staging.company.com", {"env": "staging", "region": "us-east-1"}),
            ("development", "https://k8s-dev.company.com", {"env": "dev", "region": "us-west-2"})
        ]
        
        for name, server, labels in clusters:
            cluster = platform.cluster_manager.register(name, server, labels=labels)
            health = platform.cluster_manager.health_check(cluster.cluster_id)
            status = "✓" if health["connected"] else "✗"
            print(f"  {status} {name} ({health['version']})")
            
        # Create project
        print("\n📁 Creating Projects...")
        
        project = platform.create_project(
            "platform",
            source_repos=["*"],
            destinations=[
                {"server": "*", "namespace": "platform-*"},
                {"server": "*", "namespace": "apps"}
            ]
        )
        print(f"  ✓ {project.name}")
        
        # Create applications
        print("\n🚀 Creating Applications...")
        
        apps_config = [
            ("api-gateway", "https://github.com/company/platform-apps.git", "apps/api-gateway", "production", "apps", SyncPolicy.AUTOMATED),
            ("auth-service", "https://github.com/company/microservices.git", "services/auth", "production", "apps", SyncPolicy.AUTOMATED),
            ("user-service", "https://github.com/company/microservices.git", "services/users", "production", "apps", SyncPolicy.MANUAL),
            ("order-service", "https://github.com/company/microservices.git", "services/orders", "production", "apps", SyncPolicy.MANUAL),
            ("monitoring", "https://github.com/company/infrastructure.git", "monitoring", "production", "monitoring", SyncPolicy.AUTOMATED),
            ("logging", "https://github.com/company/infrastructure.git", "logging", "production", "logging", SyncPolicy.AUTOMATED),
            ("staging-apps", "https://github.com/company/platform-apps.git", "apps", "staging", "apps", SyncPolicy.AUTOMATED)
        ]
        
        created_apps = []
        for name, repo, path, cluster, ns, policy in apps_config:
            app = platform.app_manager.create(
                name=name,
                repo_url=repo,
                path=path,
                cluster=cluster,
                namespace=ns,
                sync_policy=policy
            )
            created_apps.append(app)
            policy_icon = "🔄" if policy == SyncPolicy.AUTOMATED else "👆"
            print(f"  {policy_icon} {name} → {cluster}/{ns}")
            
        # Initial sync
        print("\n⚡ Initial Sync...")
        
        for app in created_apps[:4]:
            result = await platform.app_manager.sync(app.app_id)
            status_icon = "✓" if result.phase == "Succeeded" else "✗"
            print(f"  {status_icon} {app.name}: {result.phase} ({result.resources_synced} resources)")
            
        # Refresh state
        print("\n🔄 Refreshing Application State...")
        
        for app in created_apps[:4]:
            state = await platform.sync_engine.refresh(app)
            sync_icon = {"synced": "✅", "out_of_sync": "🔶", "syncing": "🔄", "failed": "❌"}.get(state["sync_status"], "❓")
            print(f"  {sync_icon} {state['app']}: {state['sync_status']}")
            if state["drifts"] > 0:
                print(f"     ⚠️ {state['drifts']} drift(s) detected")
                
        # Show drifts
        print("\n📊 Detected Drifts:")
        
        for app in created_apps:
            for drift in app.drifts:
                print(f"\n  [{app.name}] {drift.resource_kind}/{drift.resource_name}")
                for d in drift.diff[:3]:
                    print(f"    • {d}")
                    
        # Webhook simulation
        print("\n🔔 Simulating Webhook Push...")
        
        synced = await platform.webhook_handler.handle_push(
            "https://github.com/company/microservices.git",
            "main",
            "abc123"
        )
        
        if synced:
            print(f"  ✓ Auto-synced: {', '.join(synced)}")
        else:
            print("  → Marked as out-of-sync (manual sync policy)")
            
        # Out of sync apps
        print("\n⚠️ Out of Sync Applications:")
        
        out_of_sync = platform.app_manager.get_out_of_sync()
        for app in out_of_sync:
            print(f"  🔶 {app.name}")
            
        # Sync history
        print("\n📜 Sync History (api-gateway):")
        
        if created_apps:
            app = created_apps[0]
            for sync in app.sync_history[-5:]:
                status = "✓" if sync.phase == "Succeeded" else "✗"
                print(f"  {status} {sync.revision[:8]} - {sync.phase} ({sync.resources_synced} synced)")
                
        # Rollback example
        print("\n⏪ Rollback Example:")
        
        if created_apps and created_apps[0].sync_history:
            app = created_apps[0]
            if len(app.sync_history) >= 1:
                target_rev = app.sync_history[0].revision
                result = await platform.app_manager.rollback(app.app_id, target_rev)
                print(f"  Rolled back {app.name} to {target_rev[:8]}: {result.phase}")
                
        # Statistics
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Infrastructure:")
        print(f"    Repositories: {stats['repositories']}")
        print(f"    Clusters: {stats['clusters']}")
        print(f"    Projects: {stats['projects']}")
        
        print(f"\n  Applications: {stats['applications']}")
        print(f"    Sync Status:")
        for status, count in stats['sync_status'].items():
            icon = {"synced": "✅", "out_of_sync": "🔶", "syncing": "🔄", "failed": "❌", "unknown": "❓"}.get(status, "⚪")
            print(f"      {icon} {status}: {count}")
            
        print(f"\n    Health Status:")
        for status, count in stats['health_status'].items():
            icon = {"healthy": "💚", "degraded": "🟡", "progressing": "🔄", "missing": "❌", "unknown": "❓"}.get(status, "⚪")
            print(f"      {icon} {status}: {count}")
            
        print(f"\n  Drifts Detected: {stats['total_drifts']}")
        print(f"  Webhook Events: {stats['webhook_events']}")
        
        # Dashboard
        print("\n📋 GitOps Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │                    GitOps Overview                          │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Repositories:      {stats['repositories']:>10}                        │")
        print(f"  │ Clusters:          {stats['clusters']:>10}                        │")
        print(f"  │ Applications:      {stats['applications']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        synced = stats['sync_status'].get('synced', 0)
        out_sync = stats['sync_status'].get('out_of_sync', 0)
        print(f"  │ ✅ Synced:          {synced:>10}                        │")
        print(f"  │ 🔶 Out of Sync:     {out_sync:>10}                        │")
        print(f"  │ ⚠️  Drifts:          {stats['total_drifts']:>10}                        │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("GitOps Platform initialized!")
    print("=" * 60)
