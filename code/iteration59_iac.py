#!/usr/bin/env python3
"""
Server Init - Iteration 59: Infrastructure as Code (IaC)
Инфраструктура как код

Функционал:
- Resource Definitions - определение ресурсов
- State Management - управление состоянием
- Plan & Apply - планирование и применение
- Provider Abstraction - абстракция провайдеров
- Module System - модульная система
- Dependency Resolution - разрешение зависимостей
- Drift Detection - обнаружение отклонений
- Import/Export - импорт/экспорт ресурсов
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from collections import defaultdict
import uuid
import hashlib
import copy


class ResourceStatus(Enum):
    """Статус ресурса"""
    PENDING = "pending"
    CREATING = "creating"
    CREATED = "created"
    UPDATING = "updating"
    DELETING = "deleting"
    DELETED = "deleted"
    FAILED = "failed"


class ChangeType(Enum):
    """Тип изменения"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    REPLACE = "replace"
    NO_CHANGE = "no_change"


class ProviderType(Enum):
    """Тип провайдера"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    KUBERNETES = "kubernetes"
    DOCKER = "docker"
    LOCAL = "local"


@dataclass
class ResourceSpec:
    """Спецификация ресурса"""
    resource_id: str
    resource_type: str
    name: str
    
    # Провайдер
    provider: ProviderType = ProviderType.LOCAL
    
    # Конфигурация
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Метаданные
    tags: Dict[str, str] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Зависимости
    depends_on: List[str] = field(default_factory=list)
    
    # Lifecycle
    prevent_destroy: bool = False
    create_before_destroy: bool = False
    ignore_changes: List[str] = field(default_factory=list)


@dataclass
class ResourceState:
    """Состояние ресурса"""
    resource_id: str
    resource_type: str
    name: str
    
    # Провайдер
    provider: ProviderType = ProviderType.LOCAL
    
    # ID в облаке
    provider_id: str = ""
    
    # Статус
    status: ResourceStatus = ResourceStatus.PENDING
    
    # Атрибуты (реальные значения)
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    # Время
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Хеш конфигурации
    config_hash: str = ""


@dataclass
class ResourceChange:
    """Изменение ресурса"""
    resource_id: str
    resource_type: str
    name: str
    
    # Тип изменения
    change_type: ChangeType = ChangeType.NO_CHANGE
    
    # Детали
    before: Dict[str, Any] = field(default_factory=dict)
    after: Dict[str, Any] = field(default_factory=dict)
    
    # Diff
    changes: Dict[str, tuple] = field(default_factory=dict)  # attr -> (old, new)


@dataclass
class Plan:
    """План изменений"""
    plan_id: str
    
    # Изменения
    changes: List[ResourceChange] = field(default_factory=list)
    
    # Сводка
    to_create: int = 0
    to_update: int = 0
    to_delete: int = 0
    to_replace: int = 0
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Module:
    """Модуль IaC"""
    module_id: str
    name: str
    
    # Источник
    source: str = ""  # path, git, registry
    version: str = "1.0.0"
    
    # Переменные
    variables: Dict[str, Any] = field(default_factory=dict)
    
    # Ресурсы
    resources: List[ResourceSpec] = field(default_factory=list)
    
    # Outputs
    outputs: Dict[str, str] = field(default_factory=dict)  # name -> resource_attr


@dataclass
class State:
    """Состояние инфраструктуры"""
    state_id: str
    
    # Ресурсы
    resources: Dict[str, ResourceState] = field(default_factory=dict)
    
    # Outputs
    outputs: Dict[str, Any] = field(default_factory=dict)
    
    # Версия
    version: int = 1
    serial: int = 0
    
    # Время
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Блокировка
    lock_id: Optional[str] = None
    locked_by: Optional[str] = None


class Provider:
    """Базовый провайдер"""
    
    def __init__(self, provider_type: ProviderType):
        self.provider_type = provider_type
        self.resources: Dict[str, Dict[str, Any]] = {}
        
    async def create(self, resource_type: str, name: str,
                      config: Dict[str, Any]) -> Dict[str, Any]:
        """Создание ресурса"""
        provider_id = f"{self.provider_type.value}_{resource_type}_{uuid.uuid4().hex[:8]}"
        
        attributes = {
            "id": provider_id,
            "name": name,
            **config,
            "created_at": datetime.now().isoformat()
        }
        
        self.resources[provider_id] = attributes
        
        # Симуляция задержки
        await asyncio.sleep(0.1)
        
        return attributes
        
    async def read(self, provider_id: str) -> Optional[Dict[str, Any]]:
        """Чтение ресурса"""
        return self.resources.get(provider_id)
        
    async def update(self, provider_id: str,
                      config: Dict[str, Any]) -> Dict[str, Any]:
        """Обновление ресурса"""
        if provider_id not in self.resources:
            raise ValueError("Resource not found")
            
        self.resources[provider_id].update(config)
        self.resources[provider_id]["updated_at"] = datetime.now().isoformat()
        
        await asyncio.sleep(0.1)
        
        return self.resources[provider_id]
        
    async def delete(self, provider_id: str) -> bool:
        """Удаление ресурса"""
        if provider_id in self.resources:
            del self.resources[provider_id]
            await asyncio.sleep(0.1)
            return True
        return False


class ProviderRegistry:
    """Реестр провайдеров"""
    
    def __init__(self):
        self.providers: Dict[ProviderType, Provider] = {}
        
        # Регистрация провайдеров
        for provider_type in ProviderType:
            self.providers[provider_type] = Provider(provider_type)
            
    def get(self, provider_type: ProviderType) -> Provider:
        """Получение провайдера"""
        return self.providers.get(provider_type)


class StateManager:
    """Менеджер состояния"""
    
    def __init__(self):
        self.states: Dict[str, State] = {}
        self.history: List[State] = []
        
    def get_or_create(self, state_id: str) -> State:
        """Получение или создание состояния"""
        if state_id not in self.states:
            self.states[state_id] = State(state_id=state_id)
        return self.states[state_id]
        
    def save(self, state: State):
        """Сохранение состояния"""
        state.serial += 1
        state.updated_at = datetime.now()
        
        # Сохраняем копию в историю
        self.history.append(copy.deepcopy(state))
        
        # Ограничиваем историю
        if len(self.history) > 100:
            self.history = self.history[-50:]
            
        self.states[state.state_id] = state
        
    def lock(self, state_id: str, locked_by: str) -> Optional[str]:
        """Блокировка состояния"""
        state = self.states.get(state_id)
        
        if state and state.lock_id:
            return None  # Уже заблокировано
            
        lock_id = f"lock_{uuid.uuid4().hex[:8]}"
        
        if state:
            state.lock_id = lock_id
            state.locked_by = locked_by
        else:
            self.states[state_id] = State(
                state_id=state_id,
                lock_id=lock_id,
                locked_by=locked_by
            )
            
        return lock_id
        
    def unlock(self, state_id: str, lock_id: str) -> bool:
        """Разблокировка состояния"""
        state = self.states.get(state_id)
        
        if state and state.lock_id == lock_id:
            state.lock_id = None
            state.locked_by = None
            return True
            
        return False


class DependencyResolver:
    """Разрешение зависимостей"""
    
    def resolve(self, resources: List[ResourceSpec]) -> List[ResourceSpec]:
        """Топологическая сортировка ресурсов"""
        # Построение графа
        graph = {r.resource_id: set(r.depends_on) for r in resources}
        resources_map = {r.resource_id: r for r in resources}
        
        # Алгоритм Кана
        in_degree = {node: 0 for node in graph}
        
        for node in graph:
            for dep in graph[node]:
                if dep in in_degree:
                    in_degree[node] += 1
                    
        queue = [node for node, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(resources_map[node])
            
            for other in graph:
                if node in graph[other]:
                    in_degree[other] -= 1
                    if in_degree[other] == 0:
                        queue.append(other)
                        
        if len(result) != len(resources):
            raise ValueError("Circular dependency detected")
            
        return result


class PlanEngine:
    """Движок планирования"""
    
    def __init__(self):
        self.dependency_resolver = DependencyResolver()
        
    def create_plan(self, desired: List[ResourceSpec], state: State) -> Plan:
        """Создание плана"""
        plan = Plan(plan_id=f"plan_{uuid.uuid4().hex[:8]}")
        
        desired_map = {r.resource_id: r for r in desired}
        existing_ids = set(state.resources.keys())
        desired_ids = set(desired_map.keys())
        
        # Ресурсы для создания
        to_create = desired_ids - existing_ids
        
        # Ресурсы для удаления
        to_delete = existing_ids - desired_ids
        
        # Ресурсы для проверки обновлений
        to_check = existing_ids & desired_ids
        
        # Создание
        for resource_id in to_create:
            spec = desired_map[resource_id]
            change = ResourceChange(
                resource_id=resource_id,
                resource_type=spec.resource_type,
                name=spec.name,
                change_type=ChangeType.CREATE,
                after=spec.config
            )
            plan.changes.append(change)
            plan.to_create += 1
            
        # Удаление
        for resource_id in to_delete:
            existing = state.resources[resource_id]
            change = ResourceChange(
                resource_id=resource_id,
                resource_type=existing.resource_type,
                name=existing.name,
                change_type=ChangeType.DELETE,
                before=existing.attributes
            )
            plan.changes.append(change)
            plan.to_delete += 1
            
        # Проверка обновлений
        for resource_id in to_check:
            spec = desired_map[resource_id]
            existing = state.resources[resource_id]
            
            # Сравнение конфигураций
            changes = self._diff_config(existing.attributes, spec.config, spec.ignore_changes)
            
            if changes:
                # Проверяем, требуется ли замена
                requires_replace = self._check_replace_required(spec, changes)
                
                change_type = ChangeType.REPLACE if requires_replace else ChangeType.UPDATE
                
                change = ResourceChange(
                    resource_id=resource_id,
                    resource_type=spec.resource_type,
                    name=spec.name,
                    change_type=change_type,
                    before=existing.attributes,
                    after=spec.config,
                    changes=changes
                )
                plan.changes.append(change)
                
                if requires_replace:
                    plan.to_replace += 1
                else:
                    plan.to_update += 1
                    
        return plan
        
    def _diff_config(self, current: Dict[str, Any], desired: Dict[str, Any],
                      ignore: List[str]) -> Dict[str, tuple]:
        """Сравнение конфигураций"""
        changes = {}
        
        all_keys = set(current.keys()) | set(desired.keys())
        
        for key in all_keys:
            if key in ignore or key in ['id', 'created_at', 'updated_at']:
                continue
                
            old_val = current.get(key)
            new_val = desired.get(key)
            
            if old_val != new_val:
                changes[key] = (old_val, new_val)
                
        return changes
        
    def _check_replace_required(self, spec: ResourceSpec,
                                  changes: Dict[str, tuple]) -> bool:
        """Проверка необходимости замены"""
        # Некоторые атрибуты требуют пересоздания
        force_replace_attrs = ['name', 'availability_zone', 'subnet_id']
        
        for attr in changes:
            if attr in force_replace_attrs:
                return True
                
        return False


class ApplyEngine:
    """Движок применения"""
    
    def __init__(self, provider_registry: ProviderRegistry,
                  state_manager: StateManager):
        self.provider_registry = provider_registry
        self.state_manager = state_manager
        self.dependency_resolver = DependencyResolver()
        
    async def apply(self, plan: Plan, desired: List[ResourceSpec],
                     state: State) -> List[Dict[str, Any]]:
        """Применение плана"""
        results = []
        
        # Сортируем изменения по зависимостям
        ordered_changes = self._order_changes(plan.changes, desired)
        
        for change in ordered_changes:
            result = await self._apply_change(change, desired, state)
            results.append(result)
            
            # Сохраняем состояние после каждого изменения
            self.state_manager.save(state)
            
        return results
        
    def _order_changes(self, changes: List[ResourceChange],
                        desired: List[ResourceSpec]) -> List[ResourceChange]:
        """Упорядочивание изменений"""
        # Удаления в обратном порядке
        deletes = [c for c in changes if c.change_type == ChangeType.DELETE]
        deletes.reverse()
        
        # Создания и обновления по зависимостям
        other = [c for c in changes if c.change_type != ChangeType.DELETE]
        
        return other + deletes
        
    async def _apply_change(self, change: ResourceChange,
                             desired: List[ResourceSpec],
                             state: State) -> Dict[str, Any]:
        """Применение одного изменения"""
        spec = next((r for r in desired if r.resource_id == change.resource_id), None)
        
        try:
            if change.change_type == ChangeType.CREATE:
                return await self._create_resource(spec, state)
                
            elif change.change_type == ChangeType.UPDATE:
                return await self._update_resource(spec, state)
                
            elif change.change_type == ChangeType.DELETE:
                return await self._delete_resource(change.resource_id, state)
                
            elif change.change_type == ChangeType.REPLACE:
                # Сначала создаём новый, потом удаляем старый
                if spec and spec.create_before_destroy:
                    result = await self._create_resource(spec, state)
                    await self._delete_resource(change.resource_id, state)
                    return result
                else:
                    await self._delete_resource(change.resource_id, state)
                    return await self._create_resource(spec, state)
                    
        except Exception as e:
            return {
                "resource_id": change.resource_id,
                "status": "failed",
                "error": str(e)
            }
            
        return {"resource_id": change.resource_id, "status": "no_change"}
        
    async def _create_resource(self, spec: ResourceSpec, state: State) -> Dict[str, Any]:
        """Создание ресурса"""
        provider = self.provider_registry.get(spec.provider)
        
        # Обновляем статус
        resource_state = ResourceState(
            resource_id=spec.resource_id,
            resource_type=spec.resource_type,
            name=spec.name,
            provider=spec.provider,
            status=ResourceStatus.CREATING
        )
        state.resources[spec.resource_id] = resource_state
        
        # Создаём ресурс
        attributes = await provider.create(spec.resource_type, spec.name, spec.config)
        
        # Обновляем состояние
        resource_state.provider_id = attributes['id']
        resource_state.status = ResourceStatus.CREATED
        resource_state.attributes = attributes
        resource_state.created_at = datetime.now()
        resource_state.config_hash = self._hash_config(spec.config)
        
        return {
            "resource_id": spec.resource_id,
            "status": "created",
            "provider_id": attributes['id']
        }
        
    async def _update_resource(self, spec: ResourceSpec, state: State) -> Dict[str, Any]:
        """Обновление ресурса"""
        resource_state = state.resources.get(spec.resource_id)
        
        if not resource_state:
            return {"resource_id": spec.resource_id, "status": "not_found"}
            
        provider = self.provider_registry.get(spec.provider)
        
        resource_state.status = ResourceStatus.UPDATING
        
        # Обновляем ресурс
        attributes = await provider.update(resource_state.provider_id, spec.config)
        
        resource_state.status = ResourceStatus.CREATED
        resource_state.attributes = attributes
        resource_state.updated_at = datetime.now()
        resource_state.config_hash = self._hash_config(spec.config)
        
        return {
            "resource_id": spec.resource_id,
            "status": "updated"
        }
        
    async def _delete_resource(self, resource_id: str, state: State) -> Dict[str, Any]:
        """Удаление ресурса"""
        resource_state = state.resources.get(resource_id)
        
        if not resource_state:
            return {"resource_id": resource_id, "status": "not_found"}
            
        # Проверка prevent_destroy не делаем в demo
        
        provider = self.provider_registry.get(resource_state.provider)
        
        resource_state.status = ResourceStatus.DELETING
        
        # Удаляем ресурс
        await provider.delete(resource_state.provider_id)
        
        resource_state.status = ResourceStatus.DELETED
        del state.resources[resource_id]
        
        return {
            "resource_id": resource_id,
            "status": "deleted"
        }
        
    def _hash_config(self, config: Dict[str, Any]) -> str:
        """Хеширование конфигурации"""
        return hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:16]


class DriftDetector:
    """Детектор отклонений"""
    
    def __init__(self, provider_registry: ProviderRegistry):
        self.provider_registry = provider_registry
        
    async def detect(self, state: State) -> List[Dict[str, Any]]:
        """Обнаружение отклонений"""
        drifts = []
        
        for resource_id, resource_state in state.resources.items():
            provider = self.provider_registry.get(resource_state.provider)
            
            # Получаем текущее состояние из провайдера
            current = await provider.read(resource_state.provider_id)
            
            if current is None:
                drifts.append({
                    "resource_id": resource_id,
                    "drift_type": "deleted",
                    "message": "Resource was deleted outside of IaC"
                })
                continue
                
            # Сравниваем атрибуты
            changes = {}
            for key, value in current.items():
                if key in ['created_at', 'updated_at']:
                    continue
                    
                expected = resource_state.attributes.get(key)
                
                if value != expected:
                    changes[key] = {"expected": expected, "actual": value}
                    
            if changes:
                drifts.append({
                    "resource_id": resource_id,
                    "drift_type": "modified",
                    "changes": changes
                })
                
        return drifts


class ModuleRegistry:
    """Реестр модулей"""
    
    def __init__(self):
        self.modules: Dict[str, Module] = {}
        
    def register(self, name: str, source: str, version: str,
                  resources: List[ResourceSpec], **kwargs) -> Module:
        """Регистрация модуля"""
        module = Module(
            module_id=f"mod_{uuid.uuid4().hex[:8]}",
            name=name,
            source=source,
            version=version,
            resources=resources,
            **kwargs
        )
        
        self.modules[name] = module
        return module
        
    def instantiate(self, module_name: str, name_prefix: str,
                     variables: Dict[str, Any]) -> List[ResourceSpec]:
        """Инстанцирование модуля"""
        module = self.modules.get(module_name)
        
        if not module:
            raise ValueError(f"Module {module_name} not found")
            
        resources = []
        
        for resource in module.resources:
            # Копируем ресурс с новым ID и именем
            new_resource = ResourceSpec(
                resource_id=f"{name_prefix}_{resource.resource_id}",
                resource_type=resource.resource_type,
                name=f"{name_prefix}-{resource.name}",
                provider=resource.provider,
                config=self._apply_variables(resource.config, variables),
                tags=resource.tags.copy(),
                depends_on=[f"{name_prefix}_{dep}" for dep in resource.depends_on]
            )
            resources.append(new_resource)
            
        return resources
        
    def _apply_variables(self, config: Dict[str, Any],
                          variables: Dict[str, Any]) -> Dict[str, Any]:
        """Применение переменных"""
        result = {}
        
        for key, value in config.items():
            if isinstance(value, str) and value.startswith("var."):
                var_name = value[4:]
                result[key] = variables.get(var_name, value)
            elif isinstance(value, dict):
                result[key] = self._apply_variables(value, variables)
            else:
                result[key] = value
                
        return result


class IaCPlatform:
    """Платформа IaC"""
    
    def __init__(self):
        self.provider_registry = ProviderRegistry()
        self.state_manager = StateManager()
        self.plan_engine = PlanEngine()
        self.apply_engine = ApplyEngine(self.provider_registry, self.state_manager)
        self.drift_detector = DriftDetector(self.provider_registry)
        self.module_registry = ModuleRegistry()
        
        self.workspace = "default"
        
    def set_workspace(self, workspace: str):
        """Установка рабочего пространства"""
        self.workspace = workspace
        
    def plan(self, resources: List[ResourceSpec]) -> Plan:
        """Планирование изменений"""
        state = self.state_manager.get_or_create(self.workspace)
        return self.plan_engine.create_plan(resources, state)
        
    async def apply(self, resources: List[ResourceSpec]) -> List[Dict[str, Any]]:
        """Применение изменений"""
        state = self.state_manager.get_or_create(self.workspace)
        plan = self.plan_engine.create_plan(resources, state)
        return await self.apply_engine.apply(plan, resources, state)
        
    async def destroy(self) -> List[Dict[str, Any]]:
        """Уничтожение всех ресурсов"""
        return await self.apply([])  # Пустой список = удалить всё
        
    async def detect_drift(self) -> List[Dict[str, Any]]:
        """Обнаружение отклонений"""
        state = self.state_manager.get_or_create(self.workspace)
        return await self.drift_detector.detect(state)
        
    def get_state(self) -> State:
        """Получение состояния"""
        return self.state_manager.get_or_create(self.workspace)
        
    def get_output(self, output_name: str) -> Any:
        """Получение output"""
        state = self.state_manager.get_or_create(self.workspace)
        return state.outputs.get(output_name)


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 59: Infrastructure as Code (IaC)")
    print("=" * 60)
    
    async def demo():
        # Создание платформы
        iac = IaCPlatform()
        print("✓ IaC Platform created")
        
        # Определение ресурсов
        print("\n📝 Defining resources...")
        
        resources = [
            ResourceSpec(
                resource_id="vpc_main",
                resource_type="vpc",
                name="main-vpc",
                provider=ProviderType.AWS,
                config={
                    "cidr_block": "10.0.0.0/16",
                    "enable_dns": True
                },
                tags={"Environment": "production"}
            ),
            ResourceSpec(
                resource_id="subnet_public",
                resource_type="subnet",
                name="public-subnet",
                provider=ProviderType.AWS,
                config={
                    "cidr_block": "10.0.1.0/24",
                    "availability_zone": "us-east-1a",
                    "public": True
                },
                depends_on=["vpc_main"]
            ),
            ResourceSpec(
                resource_id="subnet_private",
                resource_type="subnet",
                name="private-subnet",
                provider=ProviderType.AWS,
                config={
                    "cidr_block": "10.0.2.0/24",
                    "availability_zone": "us-east-1b",
                    "public": False
                },
                depends_on=["vpc_main"]
            ),
            ResourceSpec(
                resource_id="instance_web",
                resource_type="instance",
                name="web-server",
                provider=ProviderType.AWS,
                config={
                    "instance_type": "t3.medium",
                    "ami": "ami-12345678"
                },
                depends_on=["subnet_public"]
            ),
            ResourceSpec(
                resource_id="instance_db",
                resource_type="instance",
                name="db-server",
                provider=ProviderType.AWS,
                config={
                    "instance_type": "r5.large",
                    "ami": "ami-87654321"
                },
                depends_on=["subnet_private"]
            ),
        ]
        
        for r in resources:
            deps = f" (depends: {', '.join(r.depends_on)})" if r.depends_on else ""
            print(f"  ✓ {r.resource_type}.{r.name}{deps}")
            
        # Планирование
        print("\n📋 Planning...")
        
        plan = iac.plan(resources)
        
        print(f"  Plan: {plan.plan_id}")
        print(f"  To create: {plan.to_create}")
        print(f"  To update: {plan.to_update}")
        print(f"  To delete: {plan.to_delete}")
        print(f"  To replace: {plan.to_replace}")
        
        print("\n  Changes:")
        for change in plan.changes:
            symbol = {"create": "+", "update": "~", "delete": "-", "replace": "-/+"}
            s = symbol.get(change.change_type.value, "?")
            print(f"    {s} {change.resource_type}.{change.name}")
            
        # Применение
        print("\n🚀 Applying...")
        
        results = await iac.apply(resources)
        
        for result in results:
            status = "✓" if result["status"] in ["created", "updated"] else "✗"
            print(f"  {status} {result['resource_id']}: {result['status']}")
            
        # Просмотр состояния
        print("\n📊 Current state:")
        
        state = iac.get_state()
        print(f"  State: {state.state_id} (serial: {state.serial})")
        print(f"  Resources: {len(state.resources)}")
        
        for resource_id, resource_state in state.resources.items():
            print(f"    - {resource_state.resource_type}.{resource_state.name}: {resource_state.status.value}")
            
        # Обновление ресурса
        print("\n🔄 Updating resource...")
        
        # Меняем instance type
        resources[3].config["instance_type"] = "t3.large"
        
        plan = iac.plan(resources)
        print(f"  To update: {plan.to_update}")
        
        if plan.to_update > 0:
            for change in plan.changes:
                if change.change_type == ChangeType.UPDATE:
                    print(f"  Changes for {change.name}:")
                    for attr, (old, new) in change.changes.items():
                        print(f"    {attr}: {old} -> {new}")
                        
            results = await iac.apply(resources)
            print(f"  Applied: {len(results)} changes")
            
        # Модули
        print("\n📦 Using modules...")
        
        # Создание модуля
        module_resources = [
            ResourceSpec(
                resource_id="app_instance",
                resource_type="instance",
                name="app",
                provider=ProviderType.AWS,
                config={
                    "instance_type": "var.instance_type",
                    "ami": "var.ami"
                }
            ),
            ResourceSpec(
                resource_id="app_lb",
                resource_type="load_balancer",
                name="lb",
                provider=ProviderType.AWS,
                config={
                    "type": "application",
                    "port": 80
                },
                depends_on=["app_instance"]
            )
        ]
        
        iac.module_registry.register(
            name="web-app",
            source="./modules/web-app",
            version="1.0.0",
            resources=module_resources,
            variables={"instance_type": "t3.micro", "ami": "ami-default"}
        )
        print("  ✓ Module 'web-app' registered")
        
        # Инстанцирование модуля
        app1_resources = iac.module_registry.instantiate(
            "web-app",
            "app1",
            {"instance_type": "t3.small", "ami": "ami-12345"}
        )
        print(f"  ✓ Module instantiated: {len(app1_resources)} resources")
        
        for r in app1_resources:
            print(f"    - {r.resource_type}.{r.name}")
            
        # Drift detection
        print("\n🔍 Drift detection...")
        
        # Симулируем изменение в провайдере (вне IaC)
        provider = iac.provider_registry.get(ProviderType.AWS)
        
        for provider_id in list(provider.resources.keys())[:1]:
            provider.resources[provider_id]["instance_type"] = "t3.xlarge"
            print(f"  Simulated external change to {provider_id}")
            
        drifts = await iac.detect_drift()
        
        if drifts:
            print(f"  Found {len(drifts)} drifts:")
            for drift in drifts:
                print(f"    - {drift['resource_id']}: {drift['drift_type']}")
                if 'changes' in drift:
                    for attr, values in drift['changes'].items():
                        print(f"      {attr}: {values['expected']} -> {values['actual']}")
        else:
            print("  No drift detected")
            
        # Destroy
        print("\n💥 Destroying infrastructure...")
        
        plan = iac.plan([])  # Пустой список = destroy
        print(f"  To delete: {plan.to_delete}")
        
        results = await iac.destroy()
        
        for result in results:
            print(f"  ✓ {result['resource_id']}: {result['status']}")
            
        # Финальное состояние
        print("\n📊 Final state:")
        state = iac.get_state()
        print(f"  Resources remaining: {len(state.resources)}")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Infrastructure as Code Platform initialized!")
    print("=" * 60)
