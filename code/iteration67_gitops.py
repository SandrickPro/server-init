#!/usr/bin/env python3
"""
Server Init - Iteration 67: GitOps & Deployment Automation Platform
GitOps и автоматизация развёртывания

Функционал:
- GitOps Controller - GitOps контроллер
- Deployment Pipelines - конвейеры развёртывания
- Rollback Management - управление откатами
- Canary Deployments - канареечные развёртывания
- Blue-Green Deployments - сине-зелёные развёртывания
- Progressive Delivery - прогрессивная доставка
- Sync Status - статус синхронизации
- Drift Detection - обнаружение дрейфа
"""

import json
import asyncio
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from collections import defaultdict
import uuid
import random


class SyncStatus(Enum):
    """Статус синхронизации"""
    SYNCED = "synced"
    OUT_OF_SYNC = "out_of_sync"
    SYNCING = "syncing"
    UNKNOWN = "unknown"
    ERROR = "error"


class DeploymentStrategy(Enum):
    """Стратегия развёртывания"""
    ROLLING = "rolling"
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    RECREATE = "recreate"
    A_B = "a_b"


class DeploymentStatus(Enum):
    """Статус развёртывания"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLED_BACK = "rolled_back"


class HealthStatus(Enum):
    """Статус здоровья"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    PROGRESSING = "progressing"
    UNKNOWN = "unknown"


@dataclass
class GitRepository:
    """Git репозиторий"""
    repo_id: str
    name: str
    
    # URL
    url: str = ""
    branch: str = "main"
    path: str = "/"
    
    # Credentials
    ssh_key_secret: str = ""
    
    # Polling
    poll_interval_seconds: int = 60
    
    # Последняя синхронизация
    last_commit: str = ""
    last_sync: Optional[datetime] = None


@dataclass
class Application:
    """Приложение GitOps"""
    app_id: str
    name: str
    
    # Источник
    repo: GitRepository = None
    
    # Назначение
    target_namespace: str = "default"
    target_cluster: str = "in-cluster"
    
    # Синхронизация
    sync_policy: Dict[str, Any] = field(default_factory=dict)
    auto_sync: bool = True
    
    # Статус
    sync_status: SyncStatus = SyncStatus.UNKNOWN
    health_status: HealthStatus = HealthStatus.UNKNOWN
    
    # Метаданные
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    last_synced_at: Optional[datetime] = None


@dataclass
class Deployment:
    """Развёртывание"""
    deployment_id: str
    app_id: str
    
    # Версия
    version: str = ""
    commit: str = ""
    
    # Стратегия
    strategy: DeploymentStrategy = DeploymentStrategy.ROLLING
    
    # Конфигурация стратегии
    strategy_config: Dict[str, Any] = field(default_factory=dict)
    
    # Статус
    status: DeploymentStatus = DeploymentStatus.PENDING
    
    # Прогресс
    replicas_desired: int = 3
    replicas_ready: int = 0
    replicas_updated: int = 0
    
    # Время
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # История
    events: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class CanaryRelease:
    """Канареечный релиз"""
    release_id: str
    deployment_id: str
    
    # Конфигурация
    steps: List[Dict[str, Any]] = field(default_factory=list)
    current_step: int = 0
    
    # Трафик
    canary_weight: int = 0
    stable_weight: int = 100
    
    # Анализ
    analysis_runs: List[Dict[str, Any]] = field(default_factory=list)
    
    # Статус
    phase: str = "progressing"  # progressing, paused, succeeded, failed
    
    # Время
    started_at: datetime = field(default_factory=datetime.now)


@dataclass
class BlueGreenRelease:
    """Blue-Green релиз"""
    release_id: str
    deployment_id: str
    
    # Среды
    blue_version: str = ""
    green_version: str = ""
    
    # Активная среда
    active_environment: str = "blue"
    
    # Предварительный просмотр
    preview_enabled: bool = False
    preview_service: str = ""
    
    # Promotion
    auto_promote: bool = False
    promotion_delay_seconds: int = 300
    
    # Статус
    phase: str = "waiting"  # waiting, preview, promoted, aborted


@dataclass
class Rollback:
    """Откат"""
    rollback_id: str
    deployment_id: str
    
    # Цель
    target_revision: str = ""
    target_version: str = ""
    
    # Причина
    reason: str = ""
    initiated_by: str = ""
    
    # Статус
    status: str = "pending"  # pending, in_progress, completed, failed
    
    # Время
    initiated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class SyncResult:
    """Результат синхронизации"""
    result_id: str
    app_id: str
    
    # Ревизия
    revision: str = ""
    
    # Статус
    status: SyncStatus = SyncStatus.UNKNOWN
    
    # Изменения
    resources_created: int = 0
    resources_updated: int = 0
    resources_deleted: int = 0
    
    # Ошибки
    errors: List[str] = field(default_factory=list)
    
    # Время
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class GitOpsController:
    """GitOps контроллер"""
    
    def __init__(self):
        self.applications: Dict[str, Application] = {}
        self.repositories: Dict[str, GitRepository] = {}
        self.sync_history: List[SyncResult] = []
        
    def register_repository(self, name: str, url: str, **kwargs) -> GitRepository:
        """Регистрация репозитория"""
        repo = GitRepository(
            repo_id=f"repo_{uuid.uuid4().hex[:8]}",
            name=name,
            url=url,
            **kwargs
        )
        
        self.repositories[repo.repo_id] = repo
        return repo
        
    def create_application(self, name: str, repo_id: str, **kwargs) -> Application:
        """Создание приложения"""
        repo = self.repositories.get(repo_id)
        
        app = Application(
            app_id=f"app_{uuid.uuid4().hex[:8]}",
            name=name,
            repo=repo,
            **kwargs
        )
        
        self.applications[app.app_id] = app
        return app
        
    async def sync(self, app_id: str) -> SyncResult:
        """Синхронизация приложения"""
        app = self.applications.get(app_id)
        
        if not app:
            raise ValueError("Application not found")
            
        result = SyncResult(
            result_id=f"sync_{uuid.uuid4().hex[:8]}",
            app_id=app_id
        )
        
        app.sync_status = SyncStatus.SYNCING
        
        try:
            # Симуляция git pull
            await asyncio.sleep(0.2)
            
            new_commit = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:7]
            result.revision = new_commit
            
            if app.repo:
                app.repo.last_commit = new_commit
                app.repo.last_sync = datetime.now()
                
            # Симуляция применения манифестов
            await asyncio.sleep(0.3)
            
            result.resources_created = random.randint(0, 3)
            result.resources_updated = random.randint(1, 5)
            result.resources_deleted = random.randint(0, 1)
            
            result.status = SyncStatus.SYNCED
            app.sync_status = SyncStatus.SYNCED
            app.health_status = HealthStatus.HEALTHY
            app.last_synced_at = datetime.now()
            
        except Exception as e:
            result.status = SyncStatus.ERROR
            result.errors.append(str(e))
            app.sync_status = SyncStatus.ERROR
            
        result.completed_at = datetime.now()
        self.sync_history.append(result)
        
        return result
        
    def detect_drift(self, app_id: str) -> Dict[str, Any]:
        """Обнаружение дрейфа"""
        app = self.applications.get(app_id)
        
        if not app:
            return {"error": "Application not found"}
            
        # Симуляция обнаружения дрейфа
        has_drift = random.random() > 0.8  # 20% вероятность дрейфа
        
        drift_report = {
            "app_id": app_id,
            "has_drift": has_drift,
            "checked_at": datetime.now(),
            "drifted_resources": []
        }
        
        if has_drift:
            drift_report["drifted_resources"] = [
                {"resource": "Deployment/api", "field": "replicas", "expected": 3, "actual": 2},
                {"resource": "ConfigMap/config", "field": "data.setting", "expected": "value1", "actual": "value2"}
            ]
            app.sync_status = SyncStatus.OUT_OF_SYNC
            
        return drift_report


class DeploymentManager:
    """Менеджер развёртываний"""
    
    def __init__(self):
        self.deployments: Dict[str, Deployment] = {}
        self.canary_releases: Dict[str, CanaryRelease] = {}
        self.blue_green_releases: Dict[str, BlueGreenRelease] = {}
        self.rollbacks: Dict[str, Rollback] = {}
        
    def create_deployment(self, app_id: str, version: str,
                           strategy: DeploymentStrategy = DeploymentStrategy.ROLLING,
                           **kwargs) -> Deployment:
        """Создание развёртывания"""
        deployment = Deployment(
            deployment_id=f"deploy_{uuid.uuid4().hex[:8]}",
            app_id=app_id,
            version=version,
            strategy=strategy,
            commit=hashlib.md5(version.encode()).hexdigest()[:7],
            **kwargs
        )
        
        self.deployments[deployment.deployment_id] = deployment
        return deployment
        
    async def execute(self, deployment_id: str) -> Deployment:
        """Выполнение развёртывания"""
        deployment = self.deployments.get(deployment_id)
        
        if not deployment:
            raise ValueError("Deployment not found")
            
        deployment.status = DeploymentStatus.IN_PROGRESS
        deployment.started_at = datetime.now()
        
        self._log_event(deployment, "started", f"Deployment started with strategy {deployment.strategy.value}")
        
        try:
            if deployment.strategy == DeploymentStrategy.ROLLING:
                await self._rolling_deploy(deployment)
            elif deployment.strategy == DeploymentStrategy.BLUE_GREEN:
                await self._blue_green_deploy(deployment)
            elif deployment.strategy == DeploymentStrategy.CANARY:
                await self._canary_deploy(deployment)
            elif deployment.strategy == DeploymentStrategy.RECREATE:
                await self._recreate_deploy(deployment)
                
            deployment.status = DeploymentStatus.SUCCEEDED
            self._log_event(deployment, "succeeded", "Deployment completed successfully")
            
        except Exception as e:
            deployment.status = DeploymentStatus.FAILED
            self._log_event(deployment, "failed", str(e))
            
        deployment.completed_at = datetime.now()
        return deployment
        
    async def _rolling_deploy(self, deployment: Deployment):
        """Rolling deployment"""
        max_surge = deployment.strategy_config.get("max_surge", 1)
        max_unavailable = deployment.strategy_config.get("max_unavailable", 0)
        
        for i in range(deployment.replicas_desired):
            await asyncio.sleep(0.1)
            deployment.replicas_updated = i + 1
            deployment.replicas_ready = i + 1
            self._log_event(deployment, "pod_updated", f"Pod {i+1}/{deployment.replicas_desired} updated")
            
    async def _blue_green_deploy(self, deployment: Deployment):
        """Blue-Green deployment"""
        release = BlueGreenRelease(
            release_id=f"bg_{uuid.uuid4().hex[:8]}",
            deployment_id=deployment.deployment_id,
            blue_version=deployment.strategy_config.get("current_version", "v1"),
            green_version=deployment.version
        )
        
        self.blue_green_releases[release.release_id] = release
        
        # Деплоим в inactive среду
        self._log_event(deployment, "deploying_green", f"Deploying {release.green_version} to green environment")
        await asyncio.sleep(0.2)
        
        # Проверка здоровья
        self._log_event(deployment, "health_check", "Running health checks on green environment")
        await asyncio.sleep(0.1)
        
        # Switch traffic
        release.active_environment = "green"
        release.phase = "promoted"
        self._log_event(deployment, "traffic_switched", "Traffic switched to green environment")
        
        deployment.replicas_ready = deployment.replicas_desired
        deployment.replicas_updated = deployment.replicas_desired
        
    async def _canary_deploy(self, deployment: Deployment):
        """Canary deployment"""
        steps = deployment.strategy_config.get("steps", [
            {"weight": 10, "pause": 30},
            {"weight": 30, "pause": 60},
            {"weight": 50, "pause": 60},
            {"weight": 100}
        ])
        
        release = CanaryRelease(
            release_id=f"canary_{uuid.uuid4().hex[:8]}",
            deployment_id=deployment.deployment_id,
            steps=steps
        )
        
        self.canary_releases[release.release_id] = release
        
        for i, step in enumerate(steps):
            weight = step.get("weight", 0)
            release.canary_weight = weight
            release.stable_weight = 100 - weight
            release.current_step = i
            
            self._log_event(deployment, "canary_step", f"Step {i+1}: {weight}% traffic to canary")
            
            # Анализ метрик
            await asyncio.sleep(0.1)
            
            analysis = {
                "step": i,
                "error_rate": random.uniform(0, 0.02),
                "latency_p99": random.uniform(100, 200),
                "success": True
            }
            release.analysis_runs.append(analysis)
            
            # Симуляция паузы
            if "pause" in step:
                await asyncio.sleep(0.05)
                
        release.phase = "succeeded"
        deployment.replicas_ready = deployment.replicas_desired
        deployment.replicas_updated = deployment.replicas_desired
        
    async def _recreate_deploy(self, deployment: Deployment):
        """Recreate deployment"""
        # Удаляем все поды
        self._log_event(deployment, "scaling_down", "Scaling down to 0 replicas")
        deployment.replicas_ready = 0
        await asyncio.sleep(0.1)
        
        # Создаём новые
        self._log_event(deployment, "scaling_up", f"Scaling up to {deployment.replicas_desired} replicas")
        for i in range(deployment.replicas_desired):
            await asyncio.sleep(0.05)
            deployment.replicas_ready = i + 1
            deployment.replicas_updated = i + 1
            
    async def rollback(self, deployment_id: str, target_version: str,
                        reason: str = "") -> Rollback:
        """Откат развёртывания"""
        rollback = Rollback(
            rollback_id=f"rollback_{uuid.uuid4().hex[:8]}",
            deployment_id=deployment_id,
            target_version=target_version,
            reason=reason
        )
        
        self.rollbacks[rollback.rollback_id] = rollback
        rollback.status = "in_progress"
        
        # Выполняем откат
        await asyncio.sleep(0.2)
        
        rollback.status = "completed"
        rollback.completed_at = datetime.now()
        
        return rollback
        
    def _log_event(self, deployment: Deployment, event_type: str, message: str):
        """Логирование события"""
        deployment.events.append({
            "type": event_type,
            "message": message,
            "timestamp": datetime.now()
        })


class PipelineEngine:
    """Движок конвейеров"""
    
    def __init__(self, deployment_manager: DeploymentManager):
        self.deployment_manager = deployment_manager
        self.pipelines: Dict[str, Dict[str, Any]] = {}
        self.runs: List[Dict[str, Any]] = []
        
    def create_pipeline(self, name: str, stages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Создание конвейера"""
        pipeline = {
            "pipeline_id": f"pipe_{uuid.uuid4().hex[:8]}",
            "name": name,
            "stages": stages,
            "created_at": datetime.now()
        }
        
        self.pipelines[pipeline["pipeline_id"]] = pipeline
        return pipeline
        
    async def execute_pipeline(self, pipeline_id: str,
                                params: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение конвейера"""
        pipeline = self.pipelines.get(pipeline_id)
        
        if not pipeline:
            raise ValueError("Pipeline not found")
            
        run = {
            "run_id": f"run_{uuid.uuid4().hex[:8]}",
            "pipeline_id": pipeline_id,
            "params": params,
            "started_at": datetime.now(),
            "stages_completed": [],
            "status": "running"
        }
        
        self.runs.append(run)
        
        try:
            for stage in pipeline["stages"]:
                stage_name = stage.get("name", "unknown")
                stage_result = await self._execute_stage(stage, params)
                
                run["stages_completed"].append({
                    "name": stage_name,
                    "result": stage_result,
                    "completed_at": datetime.now()
                })
                
                if not stage_result.get("success", True):
                    raise Exception(f"Stage {stage_name} failed")
                    
            run["status"] = "succeeded"
            
        except Exception as e:
            run["status"] = "failed"
            run["error"] = str(e)
            
        run["completed_at"] = datetime.now()
        return run
        
    async def _execute_stage(self, stage: Dict[str, Any],
                              params: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение этапа"""
        stage_type = stage.get("type", "")
        
        if stage_type == "build":
            await asyncio.sleep(0.1)
            return {"success": True, "artifact": f"image:{params.get('version', 'latest')}"}
            
        elif stage_type == "test":
            await asyncio.sleep(0.1)
            return {"success": True, "tests_passed": 42, "tests_failed": 0}
            
        elif stage_type == "deploy":
            deployment = self.deployment_manager.create_deployment(
                app_id=params.get("app_id", "unknown"),
                version=params.get("version", "latest"),
                strategy=DeploymentStrategy(stage.get("strategy", "rolling"))
            )
            
            await self.deployment_manager.execute(deployment.deployment_id)
            return {"success": deployment.status == DeploymentStatus.SUCCEEDED,
                   "deployment_id": deployment.deployment_id}
                   
        elif stage_type == "approval":
            # Автоматическое одобрение для демо
            await asyncio.sleep(0.05)
            return {"success": True, "approved_by": "auto"}
            
        return {"success": True}


class GitOpsDeploymentPlatform:
    """Платформа GitOps и развёртывания"""
    
    def __init__(self):
        self.gitops = GitOpsController()
        self.deployment_manager = DeploymentManager()
        self.pipeline_engine = PipelineEngine(self.deployment_manager)
        
    def setup_repository(self, name: str, url: str, **kwargs) -> GitRepository:
        """Настройка репозитория"""
        return self.gitops.register_repository(name, url, **kwargs)
        
    def create_application(self, name: str, repo_id: str, **kwargs) -> Application:
        """Создание приложения"""
        return self.gitops.create_application(name, repo_id, **kwargs)
        
    async def sync_application(self, app_id: str) -> SyncResult:
        """Синхронизация приложения"""
        return await self.gitops.sync(app_id)
        
    async def deploy(self, app_id: str, version: str,
                      strategy: DeploymentStrategy = DeploymentStrategy.ROLLING,
                      **kwargs) -> Deployment:
        """Развёртывание"""
        deployment = self.deployment_manager.create_deployment(
            app_id, version, strategy, **kwargs
        )
        return await self.deployment_manager.execute(deployment.deployment_id)
        
    async def rollback_deployment(self, deployment_id: str,
                                   target_version: str) -> Rollback:
        """Откат развёртывания"""
        return await self.deployment_manager.rollback(
            deployment_id, target_version, "Manual rollback"
        )
        
    def create_pipeline(self, name: str, stages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Создание конвейера"""
        return self.pipeline_engine.create_pipeline(name, stages)
        
    async def run_pipeline(self, pipeline_id: str,
                            params: Dict[str, Any]) -> Dict[str, Any]:
        """Запуск конвейера"""
        return await self.pipeline_engine.execute_pipeline(pipeline_id, params)
        
    def get_stats(self) -> Dict[str, Any]:
        """Статистика платформы"""
        successful_deployments = len([d for d in self.deployment_manager.deployments.values()
                                      if d.status == DeploymentStatus.SUCCEEDED])
        failed_deployments = len([d for d in self.deployment_manager.deployments.values()
                                  if d.status == DeploymentStatus.FAILED])
                                  
        return {
            "repositories": len(self.gitops.repositories),
            "applications": len(self.gitops.applications),
            "deployments": {
                "total": len(self.deployment_manager.deployments),
                "successful": successful_deployments,
                "failed": failed_deployments
            },
            "canary_releases": len(self.deployment_manager.canary_releases),
            "blue_green_releases": len(self.deployment_manager.blue_green_releases),
            "rollbacks": len(self.deployment_manager.rollbacks),
            "pipelines": len(self.pipeline_engine.pipelines),
            "pipeline_runs": len(self.pipeline_engine.runs),
            "syncs": len(self.gitops.sync_history)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 67: GitOps & Deployment Platform")
    print("=" * 60)
    
    async def demo():
        platform = GitOpsDeploymentPlatform()
        print("✓ GitOps Platform created")
        
        # Настройка репозитория
        print("\n📦 Setting up repository...")
        
        repo = platform.setup_repository(
            name="my-app-manifests",
            url="git@github.com:org/my-app-manifests.git",
            branch="main",
            path="/manifests",
            poll_interval_seconds=60
        )
        print(f"  ✓ Repository: {repo.name} ({repo.url})")
        
        # Создание приложения
        print("\n📱 Creating application...")
        
        app = platform.create_application(
            name="my-application",
            repo_id=repo.repo_id,
            target_namespace="production",
            target_cluster="prod-cluster",
            auto_sync=True,
            sync_policy={
                "automated": {
                    "prune": True,
                    "self_heal": True
                }
            },
            labels={"team": "platform", "env": "production"}
        )
        print(f"  ✓ Application: {app.name}")
        print(f"  Target: {app.target_cluster}/{app.target_namespace}")
        print(f"  Auto-sync: {app.auto_sync}")
        
        # Синхронизация
        print("\n🔄 Syncing application...")
        
        sync_result = await platform.sync_application(app.app_id)
        print(f"  ✓ Sync status: {sync_result.status.value}")
        print(f"  Revision: {sync_result.revision}")
        print(f"  Changes: +{sync_result.resources_created} ~{sync_result.resources_updated} -{sync_result.resources_deleted}")
        
        # Проверка дрейфа
        print("\n🔍 Checking for drift...")
        
        drift = platform.gitops.detect_drift(app.app_id)
        print(f"  Has drift: {drift['has_drift']}")
        if drift['drifted_resources']:
            for resource in drift['drifted_resources']:
                print(f"    - {resource['resource']}: {resource['field']}")
                
        # Rolling Deployment
        print("\n\n🚀 Rolling Deployment:")
        
        deployment1 = await platform.deploy(
            app_id=app.app_id,
            version="v2.1.0",
            strategy=DeploymentStrategy.ROLLING,
            replicas_desired=5,
            strategy_config={"max_surge": 1, "max_unavailable": 0}
        )
        print(f"  ✓ Deployment: {deployment1.deployment_id}")
        print(f"  Status: {deployment1.status.value}")
        print(f"  Version: {deployment1.version}")
        print(f"  Replicas: {deployment1.replicas_ready}/{deployment1.replicas_desired}")
        
        # Canary Deployment
        print("\n\n🐤 Canary Deployment:")
        
        deployment2 = await platform.deploy(
            app_id=app.app_id,
            version="v2.2.0-canary",
            strategy=DeploymentStrategy.CANARY,
            replicas_desired=3,
            strategy_config={
                "steps": [
                    {"weight": 10, "pause": 60},
                    {"weight": 30, "pause": 120},
                    {"weight": 50, "pause": 180},
                    {"weight": 100}
                ]
            }
        )
        print(f"  ✓ Deployment: {deployment2.deployment_id}")
        print(f"  Status: {deployment2.status.value}")
        
        canary = list(platform.deployment_manager.canary_releases.values())[0]
        print(f"  Canary release: {canary.release_id}")
        print(f"  Phase: {canary.phase}")
        print(f"  Steps completed: {len(canary.analysis_runs)}")
        
        # Blue-Green Deployment
        print("\n\n🔵🟢 Blue-Green Deployment:")
        
        deployment3 = await platform.deploy(
            app_id=app.app_id,
            version="v3.0.0",
            strategy=DeploymentStrategy.BLUE_GREEN,
            replicas_desired=3,
            strategy_config={"current_version": "v2.2.0"}
        )
        print(f"  ✓ Deployment: {deployment3.deployment_id}")
        print(f"  Status: {deployment3.status.value}")
        
        bg = list(platform.deployment_manager.blue_green_releases.values())[0]
        print(f"  Active environment: {bg.active_environment}")
        print(f"  Blue: {bg.blue_version}, Green: {bg.green_version}")
        
        # Rollback
        print("\n\n⏪ Rollback:")
        
        rollback = await platform.rollback_deployment(
            deployment3.deployment_id,
            target_version="v2.2.0"
        )
        print(f"  ✓ Rollback: {rollback.rollback_id}")
        print(f"  Status: {rollback.status}")
        print(f"  Target version: {rollback.target_version}")
        
        # CI/CD Pipeline
        print("\n\n🔧 CI/CD Pipeline:")
        
        pipeline = platform.create_pipeline(
            name="production-deploy",
            stages=[
                {"name": "build", "type": "build"},
                {"name": "test", "type": "test"},
                {"name": "staging-deploy", "type": "deploy", "strategy": "rolling"},
                {"name": "approval", "type": "approval"},
                {"name": "production-deploy", "type": "deploy", "strategy": "canary"}
            ]
        )
        print(f"  ✓ Pipeline: {pipeline['name']} ({pipeline['pipeline_id']})")
        print(f"  Stages: {', '.join(s['name'] for s in pipeline['stages'])}")
        
        # Запуск конвейера
        print("\n  Running pipeline...")
        
        run = await platform.run_pipeline(
            pipeline["pipeline_id"],
            params={
                "app_id": app.app_id,
                "version": "v4.0.0"
            }
        )
        print(f"  ✓ Run: {run['run_id']}")
        print(f"  Status: {run['status']}")
        print(f"  Stages completed: {len(run['stages_completed'])}")
        
        for stage in run['stages_completed']:
            print(f"    - {stage['name']}: {stage['result']}")
            
        # События развёртывания
        print("\n\n📋 Deployment Events (last deployment):")
        
        for event in deployment3.events[-5:]:
            print(f"  [{event['type']}] {event['message']}")
            
        # Статистика
        print("\n\n📊 Platform Statistics:")
        stats = platform.get_stats()
        print(f"  Repositories: {stats['repositories']}")
        print(f"  Applications: {stats['applications']}")
        print(f"  Deployments: {stats['deployments']['total']} (success: {stats['deployments']['successful']}, failed: {stats['deployments']['failed']})")
        print(f"  Canary Releases: {stats['canary_releases']}")
        print(f"  Blue-Green Releases: {stats['blue_green_releases']}")
        print(f"  Rollbacks: {stats['rollbacks']}")
        print(f"  Pipelines: {stats['pipelines']}")
        print(f"  Pipeline Runs: {stats['pipeline_runs']}")
        print(f"  Syncs: {stats['syncs']}")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("GitOps & Deployment Platform initialized!")
    print("=" * 60)
