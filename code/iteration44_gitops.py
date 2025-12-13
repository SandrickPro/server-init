#!/usr/bin/env python3
"""
Server Init - Iteration 44: GitOps & Infrastructure as Code
GitOps и Infrastructure as Code

Функционал:
- GitOps Controller - контроллер GitOps
- Infrastructure as Code Engine - движок IaC
- Drift Detection - обнаружение дрифта
- State Management - управление состоянием
- Reconciliation Loop - цикл согласования
- Multi-Environment Management - управление окружениями
- Secret Management Integration - интеграция управления секретами
- Rollback & Recovery - откат и восстановление
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


class ResourceType(Enum):
    """Тип ресурса"""
    DEPLOYMENT = "deployment"
    SERVICE = "service"
    CONFIGMAP = "configmap"
    SECRET = "secret"
    INGRESS = "ingress"
    NAMESPACE = "namespace"
    CUSTOM_RESOURCE = "custom_resource"
    
    # Infrastructure
    VM = "virtual_machine"
    DATABASE = "database"
    STORAGE = "storage"
    NETWORK = "network"
    LOAD_BALANCER = "load_balancer"


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
    UNHEALTHY = "unhealthy"
    MISSING = "missing"


class DriftType(Enum):
    """Тип дрифта"""
    NONE = "none"
    MODIFIED = "modified"
    DELETED = "deleted"
    ADDED = "added"


class ReconcileAction(Enum):
    """Действие согласования"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    SKIP = "skip"


@dataclass
class GitRepository:
    """Git репозиторий"""
    repo_id: str
    url: str
    branch: str = "main"
    path: str = "/"
    
    # Аутентификация
    auth_type: str = "ssh"  # ssh, https, token
    credentials_ref: Optional[str] = None
    
    # Синхронизация
    poll_interval_seconds: int = 60
    last_sync: Optional[datetime] = None
    last_commit: Optional[str] = None
    
    # Состояние
    connected: bool = False


@dataclass
class ResourceManifest:
    """Манифест ресурса"""
    manifest_id: str
    resource_type: ResourceType
    name: str
    namespace: str = "default"
    
    # Спецификация
    spec: Dict[str, Any] = field(default_factory=dict)
    
    # Метаданные
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    
    # Источник
    source_path: str = ""
    source_hash: str = ""
    
    # Состояние
    applied: bool = False
    applied_at: Optional[datetime] = None


@dataclass
class ResourceState:
    """Состояние ресурса"""
    resource_id: str
    resource_type: ResourceType
    name: str
    namespace: str = "default"
    
    # Текущее состояние
    current_spec: Dict[str, Any] = field(default_factory=dict)
    
    # Желаемое состояние
    desired_spec: Dict[str, Any] = field(default_factory=dict)
    
    # Статусы
    sync_status: SyncStatus = SyncStatus.UNKNOWN
    health_status: HealthStatus = HealthStatus.MISSING
    drift_type: DriftType = DriftType.NONE
    
    # Метаданные
    last_check: Optional[datetime] = None
    last_sync: Optional[datetime] = None
    error_message: Optional[str] = None


@dataclass
class Application:
    """GitOps приложение"""
    app_id: str
    name: str
    
    # Источник
    repository: GitRepository
    source_path: str = "/"
    
    # Целевое окружение
    target_cluster: str = "default"
    target_namespace: str = "default"
    
    # Синхронизация
    sync_policy: str = "manual"  # manual, automatic
    auto_prune: bool = False
    self_heal: bool = False
    
    # Состояние
    sync_status: SyncStatus = SyncStatus.UNKNOWN
    health_status: HealthStatus = HealthStatus.MISSING
    
    # Ресурсы
    resources: List[ResourceState] = field(default_factory=list)
    
    # История
    history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Метаданные
    created_at: datetime = field(default_factory=datetime.now)
    last_synced_at: Optional[datetime] = None


@dataclass
class Environment:
    """Окружение"""
    env_id: str
    name: str
    
    # Тип
    env_type: str = "development"  # development, staging, production
    
    # Кластер
    cluster_name: str = ""
    
    # Настройки
    auto_deploy: bool = False
    require_approval: bool = True
    
    # Приложения
    applications: List[str] = field(default_factory=list)
    
    # Секреты
    secrets_provider: Optional[str] = None  # vault, aws-sm, azure-kv
    
    # Метаданные
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class InfrastructureStack:
    """Стек инфраструктуры"""
    stack_id: str
    name: str
    
    # Провайдер
    provider: str = "terraform"  # terraform, pulumi, cloudformation
    
    # Источник
    source_repo: str = ""
    source_path: str = ""
    
    # Состояние
    state_backend: str = "s3"  # s3, gcs, azure, local
    state_key: str = ""
    
    # Переменные
    variables: Dict[str, Any] = field(default_factory=dict)
    
    # Ресурсы
    resources: List[Dict[str, Any]] = field(default_factory=list)
    
    # Статус
    status: str = "pending"  # pending, planning, applying, applied, failed
    last_apply: Optional[datetime] = None
    
    # Outputs
    outputs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DriftReport:
    """Отчёт о дрифте"""
    report_id: str
    application_id: str
    
    # Результаты
    drifted_resources: List[Dict[str, Any]] = field(default_factory=list)
    total_resources: int = 0
    drifted_count: int = 0
    
    # Детали
    changes: List[Dict[str, Any]] = field(default_factory=list)
    
    # Время
    detected_at: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class GitClient:
    """Git клиент"""
    
    def __init__(self):
        self.repos: Dict[str, GitRepository] = {}
        self.cache: Dict[str, Dict[str, Any]] = {}
        
    def add_repository(self, repo: GitRepository):
        """Добавление репозитория"""
        self.repos[repo.repo_id] = repo
        
    async def fetch(self, repo_id: str) -> Dict[str, Any]:
        """Получение изменений"""
        repo = self.repos.get(repo_id)
        if not repo:
            return {"error": "Repository not found"}
            
        # Симуляция fetch
        await asyncio.sleep(0.1)
        
        new_commit = hashlib.sha256(str(time.time()).encode()).hexdigest()[:7]
        
        repo.last_sync = datetime.now()
        repo.last_commit = new_commit
        repo.connected = True
        
        return {
            "repo_id": repo_id,
            "commit": new_commit,
            "fetched_at": repo.last_sync.isoformat()
        }
        
    async def get_manifests(self, repo_id: str, path: str) -> List[Dict[str, Any]]:
        """Получение манифестов"""
        # Симуляция чтения файлов
        manifests = [
            {
                "kind": "Deployment",
                "metadata": {"name": "app-deployment", "namespace": "default"},
                "spec": {"replicas": 3, "image": "app:latest"}
            },
            {
                "kind": "Service",
                "metadata": {"name": "app-service", "namespace": "default"},
                "spec": {"port": 80, "type": "ClusterIP"}
            },
            {
                "kind": "ConfigMap",
                "metadata": {"name": "app-config", "namespace": "default"},
                "data": {"config.json": "{}"}
            }
        ]
        
        return manifests
        
    def get_diff(self, repo_id: str, from_commit: str, to_commit: str) -> List[Dict[str, Any]]:
        """Получение diff между коммитами"""
        return [
            {"file": "deployment.yaml", "action": "modified"},
            {"file": "service.yaml", "action": "added"}
        ]


class StateManager:
    """Менеджер состояния"""
    
    def __init__(self):
        self.states: Dict[str, ResourceState] = {}
        self.history: List[Dict[str, Any]] = []
        
    def save_state(self, state: ResourceState):
        """Сохранение состояния"""
        key = f"{state.namespace}/{state.name}"
        
        # Сохранение истории
        if key in self.states:
            self.history.append({
                "resource": key,
                "previous_state": self.states[key].current_spec.copy(),
                "timestamp": datetime.now().isoformat()
            })
            
        self.states[key] = state
        
    def get_state(self, namespace: str, name: str) -> Optional[ResourceState]:
        """Получение состояния"""
        key = f"{namespace}/{name}"
        return self.states.get(key)
        
    def list_states(self, namespace: Optional[str] = None) -> List[ResourceState]:
        """Список состояний"""
        states = list(self.states.values())
        
        if namespace:
            states = [s for s in states if s.namespace == namespace]
            
        return states
        
    def get_history(self, resource: str, limit: int = 10) -> List[Dict[str, Any]]:
        """История изменений ресурса"""
        return [h for h in self.history if h["resource"] == resource][-limit:]


class DriftDetector:
    """Детектор дрифта"""
    
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        
    async def detect_drift(self, application: Application) -> DriftReport:
        """Обнаружение дрифта"""
        report = DriftReport(
            report_id=f"drift_{uuid.uuid4().hex[:8]}",
            application_id=application.app_id,
            total_resources=len(application.resources)
        )
        
        for resource in application.resources:
            drift = self._check_resource_drift(resource)
            
            if drift["drift_type"] != DriftType.NONE:
                report.drifted_resources.append(drift)
                report.drifted_count += 1
                
                resource.drift_type = drift["drift_type"]
                resource.sync_status = SyncStatus.OUT_OF_SYNC
                
        return report
        
    def _check_resource_drift(self, resource: ResourceState) -> Dict[str, Any]:
        """Проверка дрифта ресурса"""
        if not resource.current_spec:
            return {
                "resource": resource.name,
                "drift_type": DriftType.DELETED,
                "details": "Resource not found in cluster"
            }
            
        # Сравнение spec
        differences = self._diff_specs(resource.desired_spec, resource.current_spec)
        
        if differences:
            return {
                "resource": resource.name,
                "drift_type": DriftType.MODIFIED,
                "differences": differences,
                "details": f"{len(differences)} fields changed"
            }
            
        return {
            "resource": resource.name,
            "drift_type": DriftType.NONE,
            "details": "In sync"
        }
        
    def _diff_specs(self, desired: Dict, current: Dict) -> List[Dict[str, Any]]:
        """Сравнение спецификаций"""
        differences = []
        
        for key, value in desired.items():
            if key not in current:
                differences.append({
                    "field": key,
                    "desired": value,
                    "current": None,
                    "action": "add"
                })
            elif current[key] != value:
                differences.append({
                    "field": key,
                    "desired": value,
                    "current": current[key],
                    "action": "modify"
                })
                
        for key in current:
            if key not in desired:
                differences.append({
                    "field": key,
                    "desired": None,
                    "current": current[key],
                    "action": "remove"
                })
                
        return differences


class Reconciler:
    """Согласователь ресурсов"""
    
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.reconcile_queue: asyncio.Queue = asyncio.Queue()
        
    async def reconcile(self, resource: ResourceState) -> Dict[str, Any]:
        """Согласование ресурса"""
        action = self._determine_action(resource)
        
        result = {
            "resource": resource.name,
            "namespace": resource.namespace,
            "action": action.value,
            "success": False,
            "message": ""
        }
        
        try:
            if action == ReconcileAction.CREATE:
                await self._create_resource(resource)
            elif action == ReconcileAction.UPDATE:
                await self._update_resource(resource)
            elif action == ReconcileAction.DELETE:
                await self._delete_resource(resource)
            elif action == ReconcileAction.SKIP:
                result["message"] = "No action needed"
                result["success"] = True
                return result
                
            resource.sync_status = SyncStatus.SYNCED
            resource.drift_type = DriftType.NONE
            resource.last_sync = datetime.now()
            resource.current_spec = resource.desired_spec.copy()
            
            self.state_manager.save_state(resource)
            
            result["success"] = True
            result["message"] = f"Resource {action.value}d successfully"
            
        except Exception as e:
            resource.sync_status = SyncStatus.FAILED
            resource.error_message = str(e)
            result["message"] = str(e)
            
        return result
        
    def _determine_action(self, resource: ResourceState) -> ReconcileAction:
        """Определение действия"""
        if resource.health_status == HealthStatus.MISSING:
            return ReconcileAction.CREATE
        elif resource.drift_type == DriftType.MODIFIED:
            return ReconcileAction.UPDATE
        elif resource.drift_type == DriftType.DELETED:
            return ReconcileAction.CREATE
        elif resource.sync_status == SyncStatus.OUT_OF_SYNC:
            return ReconcileAction.UPDATE
        else:
            return ReconcileAction.SKIP
            
    async def _create_resource(self, resource: ResourceState):
        """Создание ресурса"""
        print(f"  Creating resource: {resource.namespace}/{resource.name}")
        await asyncio.sleep(0.1)
        resource.health_status = HealthStatus.PROGRESSING
        await asyncio.sleep(0.1)
        resource.health_status = HealthStatus.HEALTHY
        
    async def _update_resource(self, resource: ResourceState):
        """Обновление ресурса"""
        print(f"  Updating resource: {resource.namespace}/{resource.name}")
        await asyncio.sleep(0.1)
        
    async def _delete_resource(self, resource: ResourceState):
        """Удаление ресурса"""
        print(f"  Deleting resource: {resource.namespace}/{resource.name}")
        await asyncio.sleep(0.1)
        resource.health_status = HealthStatus.MISSING
        
    async def reconcile_application(self, application: Application) -> Dict[str, Any]:
        """Согласование приложения"""
        results = []
        
        application.sync_status = SyncStatus.SYNCING
        
        for resource in application.resources:
            result = await self.reconcile(resource)
            results.append(result)
            
        # Обновление статуса приложения
        failed = [r for r in results if not r["success"]]
        
        if failed:
            application.sync_status = SyncStatus.FAILED
        else:
            application.sync_status = SyncStatus.SYNCED
            application.last_synced_at = datetime.now()
            
        # Обновление health status
        unhealthy = [r for r in application.resources if r.health_status == HealthStatus.UNHEALTHY]
        progressing = [r for r in application.resources if r.health_status == HealthStatus.PROGRESSING]
        
        if unhealthy:
            application.health_status = HealthStatus.UNHEALTHY
        elif progressing:
            application.health_status = HealthStatus.PROGRESSING
        else:
            application.health_status = HealthStatus.HEALTHY
            
        return {
            "application": application.name,
            "sync_status": application.sync_status.value,
            "health_status": application.health_status.value,
            "results": results,
            "failed_count": len(failed)
        }


class InfrastructureEngine:
    """Движок Infrastructure as Code"""
    
    def __init__(self):
        self.stacks: Dict[str, InfrastructureStack] = {}
        
    def create_stack(self, stack: InfrastructureStack) -> str:
        """Создание стека"""
        self.stacks[stack.stack_id] = stack
        return stack.stack_id
        
    async def plan(self, stack_id: str) -> Dict[str, Any]:
        """Планирование изменений"""
        stack = self.stacks.get(stack_id)
        if not stack:
            return {"error": "Stack not found"}
            
        stack.status = "planning"
        
        # Симуляция планирования
        await asyncio.sleep(0.2)
        
        plan = {
            "stack_id": stack_id,
            "provider": stack.provider,
            "changes": [
                {"action": "create", "resource": "aws_instance.web", "details": "t3.micro"},
                {"action": "update", "resource": "aws_security_group.web", "details": "Add port 443"},
                {"action": "create", "resource": "aws_rds.db", "details": "postgres 14"}
            ],
            "add": 2,
            "change": 1,
            "destroy": 0
        }
        
        return plan
        
    async def apply(self, stack_id: str) -> Dict[str, Any]:
        """Применение изменений"""
        stack = self.stacks.get(stack_id)
        if not stack:
            return {"error": "Stack not found"}
            
        stack.status = "applying"
        
        # Симуляция применения
        await asyncio.sleep(0.3)
        
        # Обновление ресурсов
        stack.resources = [
            {"id": "i-12345", "type": "aws_instance", "name": "web"},
            {"id": "sg-67890", "type": "aws_security_group", "name": "web"},
            {"id": "db-abcde", "type": "aws_rds", "name": "db"}
        ]
        
        stack.outputs = {
            "instance_ip": "10.0.1.100",
            "db_endpoint": "db.example.com:5432"
        }
        
        stack.status = "applied"
        stack.last_apply = datetime.now()
        
        return {
            "stack_id": stack_id,
            "status": "applied",
            "resources_created": 2,
            "resources_updated": 1,
            "resources_destroyed": 0,
            "outputs": stack.outputs
        }
        
    async def destroy(self, stack_id: str) -> Dict[str, Any]:
        """Уничтожение стека"""
        stack = self.stacks.get(stack_id)
        if not stack:
            return {"error": "Stack not found"}
            
        stack.status = "destroying"
        
        await asyncio.sleep(0.3)
        
        destroyed_count = len(stack.resources)
        stack.resources = []
        stack.outputs = {}
        stack.status = "destroyed"
        
        return {
            "stack_id": stack_id,
            "status": "destroyed",
            "resources_destroyed": destroyed_count
        }
        
    def get_outputs(self, stack_id: str) -> Dict[str, Any]:
        """Получение outputs"""
        stack = self.stacks.get(stack_id)
        if not stack:
            return {}
        return stack.outputs


class SecretManager:
    """Менеджер секретов"""
    
    def __init__(self):
        self.secrets: Dict[str, Dict[str, Any]] = {}
        self.providers: Dict[str, Dict[str, Any]] = {}
        
    def register_provider(self, name: str, config: Dict[str, Any]):
        """Регистрация провайдера"""
        self.providers[name] = config
        
    async def get_secret(self, path: str, provider: str = "local") -> Optional[str]:
        """Получение секрета"""
        if provider == "local":
            return self.secrets.get(path, {}).get("value")
            
        # Симуляция получения из внешнего провайдера
        await asyncio.sleep(0.05)
        
        return f"secret-value-{path}"
        
    async def set_secret(self, path: str, value: str, provider: str = "local"):
        """Установка секрета"""
        if provider == "local":
            self.secrets[path] = {
                "value": value,
                "updated_at": datetime.now().isoformat()
            }
        else:
            # Симуляция записи во внешний провайдер
            await asyncio.sleep(0.05)
            
    def list_secrets(self, prefix: str = "") -> List[str]:
        """Список секретов"""
        return [k for k in self.secrets.keys() if k.startswith(prefix)]


class RollbackManager:
    """Менеджер отката"""
    
    def __init__(self, state_manager: StateManager, reconciler: Reconciler):
        self.state_manager = state_manager
        self.reconciler = reconciler
        self.rollback_points: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
    def create_rollback_point(self, application_id: str, 
                               resources: List[ResourceState]) -> str:
        """Создание точки отката"""
        rollback_id = f"rb_{uuid.uuid4().hex[:8]}"
        
        point = {
            "rollback_id": rollback_id,
            "application_id": application_id,
            "created_at": datetime.now().isoformat(),
            "resources": [
                {
                    "name": r.name,
                    "namespace": r.namespace,
                    "spec": r.current_spec.copy()
                }
                for r in resources
            ]
        }
        
        self.rollback_points[application_id].append(point)
        
        return rollback_id
        
    async def rollback(self, application_id: str, 
                        rollback_id: Optional[str] = None) -> Dict[str, Any]:
        """Откат к предыдущему состоянию"""
        points = self.rollback_points.get(application_id, [])
        
        if not points:
            return {"error": "No rollback points available"}
            
        if rollback_id:
            point = next((p for p in points if p["rollback_id"] == rollback_id), None)
        else:
            point = points[-1]  # Последняя точка
            
        if not point:
            return {"error": "Rollback point not found"}
            
        # Восстановление ресурсов
        restored = []
        for resource_data in point["resources"]:
            state = self.state_manager.get_state(
                resource_data["namespace"], 
                resource_data["name"]
            )
            
            if state:
                state.desired_spec = resource_data["spec"]
                result = await self.reconciler.reconcile(state)
                restored.append(result)
                
        return {
            "rollback_id": point["rollback_id"],
            "application_id": application_id,
            "restored_resources": len(restored),
            "results": restored
        }
        
    def list_rollback_points(self, application_id: str) -> List[Dict[str, Any]]:
        """Список точек отката"""
        return [
            {"rollback_id": p["rollback_id"], "created_at": p["created_at"]}
            for p in self.rollback_points.get(application_id, [])
        ]


class GitOpsController:
    """Контроллер GitOps"""
    
    def __init__(self):
        self.git_client = GitClient()
        self.state_manager = StateManager()
        self.drift_detector = DriftDetector(self.state_manager)
        self.reconciler = Reconciler(self.state_manager)
        self.infrastructure_engine = InfrastructureEngine()
        self.secret_manager = SecretManager()
        self.rollback_manager = RollbackManager(self.state_manager, self.reconciler)
        
        # Приложения и окружения
        self.applications: Dict[str, Application] = {}
        self.environments: Dict[str, Environment] = {}
        
        # Настройки
        self.reconcile_interval = 30  # секунд
        self.running = False
        
    def create_application(self, name: str, repo_url: str,
                            target_namespace: str = "default",
                            sync_policy: str = "manual") -> Application:
        """Создание приложения"""
        repo = GitRepository(
            repo_id=f"repo_{uuid.uuid4().hex[:8]}",
            url=repo_url
        )
        
        self.git_client.add_repository(repo)
        
        app = Application(
            app_id=f"app_{uuid.uuid4().hex[:8]}",
            name=name,
            repository=repo,
            target_namespace=target_namespace,
            sync_policy=sync_policy
        )
        
        self.applications[app.app_id] = app
        
        return app
        
    def create_environment(self, name: str, env_type: str,
                            cluster_name: str) -> Environment:
        """Создание окружения"""
        env = Environment(
            env_id=f"env_{uuid.uuid4().hex[:8]}",
            name=name,
            env_type=env_type,
            cluster_name=cluster_name
        )
        
        self.environments[env.env_id] = env
        
        return env
        
    async def sync_application(self, app_id: str) -> Dict[str, Any]:
        """Синхронизация приложения"""
        app = self.applications.get(app_id)
        if not app:
            return {"error": "Application not found"}
            
        # 1. Fetch из git
        fetch_result = await self.git_client.fetch(app.repository.repo_id)
        
        # 2. Получение манифестов
        manifests = await self.git_client.get_manifests(
            app.repository.repo_id, 
            app.source_path
        )
        
        # 3. Создание/обновление ResourceState
        app.resources = []
        
        for manifest in manifests:
            resource_type = ResourceType.DEPLOYMENT
            if manifest["kind"] == "Service":
                resource_type = ResourceType.SERVICE
            elif manifest["kind"] == "ConfigMap":
                resource_type = ResourceType.CONFIGMAP
                
            state = ResourceState(
                resource_id=f"res_{uuid.uuid4().hex[:8]}",
                resource_type=resource_type,
                name=manifest["metadata"]["name"],
                namespace=manifest["metadata"].get("namespace", "default"),
                desired_spec=manifest["spec"],
                sync_status=SyncStatus.OUT_OF_SYNC,
                health_status=HealthStatus.MISSING
            )
            
            app.resources.append(state)
            
        # 4. Создание rollback point
        self.rollback_manager.create_rollback_point(app_id, app.resources)
        
        # 5. Согласование
        result = await self.reconciler.reconcile_application(app)
        
        # 6. Сохранение в историю
        app.history.append({
            "commit": fetch_result.get("commit"),
            "synced_at": datetime.now().isoformat(),
            "status": result["sync_status"]
        })
        
        return result
        
    async def detect_drift(self, app_id: str) -> DriftReport:
        """Обнаружение дрифта"""
        app = self.applications.get(app_id)
        if not app:
            return DriftReport(
                report_id="error",
                application_id=app_id
            )
            
        return await self.drift_detector.detect_drift(app)
        
    async def rollback(self, app_id: str, 
                        rollback_id: Optional[str] = None) -> Dict[str, Any]:
        """Откат приложения"""
        return await self.rollback_manager.rollback(app_id, rollback_id)
        
    async def start_reconciliation_loop(self):
        """Запуск цикла согласования"""
        self.running = True
        
        while self.running:
            for app in self.applications.values():
                if app.sync_policy == "automatic":
                    # Проверка дрифта
                    drift_report = await self.detect_drift(app.app_id)
                    
                    if drift_report.drifted_count > 0:
                        if app.self_heal:
                            await self.sync_application(app.app_id)
                            
            await asyncio.sleep(self.reconcile_interval)
            
    def stop(self):
        """Остановка"""
        self.running = False
        
    def get_status(self) -> Dict[str, Any]:
        """Статус контроллера"""
        return {
            "applications": len(self.applications),
            "environments": len(self.environments),
            "synced_apps": len([
                a for a in self.applications.values() 
                if a.sync_status == SyncStatus.SYNCED
            ]),
            "healthy_apps": len([
                a for a in self.applications.values()
                if a.health_status == HealthStatus.HEALTHY
            ]),
            "infrastructure_stacks": len(self.infrastructure_engine.stacks),
            "running": self.running
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 44: GitOps & IaC")
    print("=" * 60)
    
    async def demo():
        # Создание контроллера
        controller = GitOpsController()
        print("✓ GitOps Controller created")
        
        # Создание окружений
        dev_env = controller.create_environment(
            name="development",
            env_type="development",
            cluster_name="dev-cluster"
        )
        print(f"✓ Created environment: {dev_env.name}")
        
        prod_env = controller.create_environment(
            name="production",
            env_type="production",
            cluster_name="prod-cluster"
        )
        print(f"✓ Created environment: {prod_env.name}")
        
        # Создание приложения
        app = controller.create_application(
            name="web-app",
            repo_url="https://github.com/org/web-app.git",
            target_namespace="web",
            sync_policy="manual"
        )
        print(f"✓ Created application: {app.name}")
        
        # Синхронизация
        print(f"\n🔄 Syncing application...")
        sync_result = await controller.sync_application(app.app_id)
        
        print(f"  Sync Status: {sync_result['sync_status']}")
        print(f"  Health Status: {sync_result['health_status']}")
        print(f"  Resources synced: {len(sync_result['results'])}")
        
        for result in sync_result['results']:
            status = "✓" if result['success'] else "✗"
            print(f"    {status} {result['namespace']}/{result['resource']}: {result['action']}")
            
        # Обнаружение дрифта
        print(f"\n🔍 Detecting drift...")
        
        # Симулируем дрифт
        if app.resources:
            app.resources[0].current_spec["replicas"] = 5  # Изменение
            
        drift_report = await controller.detect_drift(app.app_id)
        
        print(f"  Total Resources: {drift_report.total_resources}")
        print(f"  Drifted: {drift_report.drifted_count}")
        
        for drift in drift_report.drifted_resources:
            print(f"    ⚠️ {drift['resource']}: {drift['drift_type'].value}")
            
        # Infrastructure as Code
        print(f"\n🏗️ Infrastructure as Code...")
        
        stack = InfrastructureStack(
            stack_id="stack_web",
            name="web-infrastructure",
            provider="terraform",
            source_repo="https://github.com/org/infra.git",
            variables={
                "region": "us-east-1",
                "instance_type": "t3.micro",
                "db_instance_class": "db.t3.micro"
            }
        )
        
        controller.infrastructure_engine.create_stack(stack)
        print(f"  Created stack: {stack.name}")
        
        # Plan
        plan = await controller.infrastructure_engine.plan(stack.stack_id)
        print(f"\n  Plan Results:")
        print(f"    + Add: {plan['add']}")
        print(f"    ~ Change: {plan['change']}")
        print(f"    - Destroy: {plan['destroy']}")
        
        # Apply
        apply_result = await controller.infrastructure_engine.apply(stack.stack_id)
        print(f"\n  Apply Results:")
        print(f"    Status: {apply_result['status']}")
        print(f"    Resources: {apply_result['resources_created']} created")
        print(f"    Outputs: {list(apply_result['outputs'].keys())}")
        
        # Secrets
        print(f"\n🔐 Secret Management...")
        
        await controller.secret_manager.set_secret("db/password", "super-secret-123")
        await controller.secret_manager.set_secret("api/key", "api-key-456")
        
        secrets = controller.secret_manager.list_secrets()
        print(f"  Secrets stored: {len(secrets)}")
        
        db_password = await controller.secret_manager.get_secret("db/password")
        print(f"  Retrieved secret: db/password = ***")
        
        # Rollback
        print(f"\n⏪ Rollback Management...")
        
        rollback_points = controller.rollback_manager.list_rollback_points(app.app_id)
        print(f"  Rollback points available: {len(rollback_points)}")
        
        # Status
        status = controller.get_status()
        print(f"\n📊 Controller Status:")
        print(f"  Applications: {status['applications']}")
        print(f"  Environments: {status['environments']}")
        print(f"  Synced: {status['synced_apps']}")
        print(f"  Healthy: {status['healthy_apps']}")
        print(f"  Infrastructure Stacks: {status['infrastructure_stacks']}")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("GitOps & IaC Platform initialized!")
    print("=" * 60)
