#!/usr/bin/env python3
"""
Server Init - Iteration 123: Configuration Management Platform
Платформа управления конфигурацией

Функционал:
- Configuration Store - хранилище конфигураций
- Version Control - контроль версий
- Schema Validation - валидация схем
- Environment Management - управление окружениями
- Config Inheritance - наследование конфигураций
- Secret Integration - интеграция секретов
- Change History - история изменений
- Config Distribution - распространение конфигураций
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Union
from enum import Enum
from collections import defaultdict
import uuid
import random
import hashlib
import copy


class ConfigFormat(Enum):
    """Формат конфигурации"""
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    ENV = "env"
    PROPERTIES = "properties"


class ConfigScope(Enum):
    """Область конфигурации"""
    GLOBAL = "global"
    ENVIRONMENT = "environment"
    SERVICE = "service"
    INSTANCE = "instance"


class ChangeType(Enum):
    """Тип изменения"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ROLLBACK = "rollback"


class ValidationStatus(Enum):
    """Статус валидации"""
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"


@dataclass
class ConfigValue:
    """Значение конфигурации"""
    key: str
    value: Any = None
    
    # Type
    value_type: str = "string"
    
    # Metadata
    description: str = ""
    default: Any = None
    required: bool = False
    sensitive: bool = False
    
    # Validation
    pattern: str = ""
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: List[Any] = field(default_factory=list)


@dataclass
class ConfigVersion:
    """Версия конфигурации"""
    version_id: str
    version: int = 1
    
    # Content
    values: Dict[str, Any] = field(default_factory=dict)
    checksum: str = ""
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    message: str = ""
    
    # Status
    active: bool = False


@dataclass
class ConfigNamespace:
    """Пространство имён конфигурации"""
    namespace_id: str
    name: str = ""
    
    # Scope
    scope: ConfigScope = ConfigScope.SERVICE
    
    # Versions
    versions: List[ConfigVersion] = field(default_factory=list)
    current_version: int = 0
    
    # Schema
    schema: Dict[str, ConfigValue] = field(default_factory=dict)
    
    # Inheritance
    parent_namespace: str = ""
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Environment:
    """Окружение"""
    environment_id: str
    name: str = ""  # dev, staging, production
    
    # Config
    base_config: Dict[str, Any] = field(default_factory=dict)
    overrides: Dict[str, Any] = field(default_factory=dict)
    
    # Services
    services: List[str] = field(default_factory=list)
    
    # Status
    active: bool = True


@dataclass
class ConfigChange:
    """Изменение конфигурации"""
    change_id: str
    namespace_id: str = ""
    
    # Change
    change_type: ChangeType = ChangeType.UPDATE
    key: str = ""
    old_value: Any = None
    new_value: Any = None
    
    # Metadata
    changed_at: datetime = field(default_factory=datetime.now)
    changed_by: str = ""
    reason: str = ""


@dataclass
class ConfigSubscriber:
    """Подписчик на конфигурацию"""
    subscriber_id: str
    namespace_id: str = ""
    
    # Callback
    callback_url: str = ""
    
    # Status
    active: bool = True
    last_notified: Optional[datetime] = None
    
    # Stats
    notifications_sent: int = 0


@dataclass
class ValidationResult:
    """Результат валидации"""
    status: ValidationStatus = ValidationStatus.VALID
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class ConfigStore:
    """Хранилище конфигураций"""
    
    def __init__(self):
        self.namespaces: Dict[str, ConfigNamespace] = {}
        self.changes: List[ConfigChange] = []
        
    def create_namespace(self, name: str, scope: ConfigScope = ConfigScope.SERVICE,
                          parent: str = "", **kwargs) -> ConfigNamespace:
        """Создание пространства имён"""
        namespace = ConfigNamespace(
            namespace_id=f"ns_{uuid.uuid4().hex[:8]}",
            name=name,
            scope=scope,
            parent_namespace=parent,
            **kwargs
        )
        
        # Create initial version
        initial_version = ConfigVersion(
            version_id=f"v_{uuid.uuid4().hex[:8]}",
            version=1,
            active=True,
            message="Initial version"
        )
        namespace.versions.append(initial_version)
        namespace.current_version = 1
        
        self.namespaces[namespace.namespace_id] = namespace
        return namespace
        
    def set_value(self, namespace_id: str, key: str, value: Any,
                   changed_by: str = "system") -> bool:
        """Установка значения"""
        namespace = self.namespaces.get(namespace_id)
        if not namespace:
            return False
            
        # Get current version values
        current = self._get_active_version(namespace)
        if not current:
            return False
            
        old_value = current.values.get(key)
        
        # Create new version
        new_version = ConfigVersion(
            version_id=f"v_{uuid.uuid4().hex[:8]}",
            version=namespace.current_version + 1,
            values=current.values.copy(),
            created_by=changed_by,
            message=f"Update {key}",
            active=True
        )
        new_version.values[key] = value
        new_version.checksum = self._calculate_checksum(new_version.values)
        
        # Deactivate old version
        current.active = False
        
        namespace.versions.append(new_version)
        namespace.current_version = new_version.version
        namespace.updated_at = datetime.now()
        
        # Record change
        change = ConfigChange(
            change_id=f"chg_{uuid.uuid4().hex[:8]}",
            namespace_id=namespace_id,
            change_type=ChangeType.UPDATE,
            key=key,
            old_value=old_value,
            new_value=value,
            changed_by=changed_by
        )
        self.changes.append(change)
        
        return True
        
    def get_value(self, namespace_id: str, key: str) -> Any:
        """Получение значения"""
        namespace = self.namespaces.get(namespace_id)
        if not namespace:
            return None
            
        current = self._get_active_version(namespace)
        if not current:
            return None
            
        # Check inheritance
        value = current.values.get(key)
        if value is None and namespace.parent_namespace:
            return self.get_value(namespace.parent_namespace, key)
            
        return value
        
    def get_config(self, namespace_id: str) -> Dict[str, Any]:
        """Получение всей конфигурации"""
        namespace = self.namespaces.get(namespace_id)
        if not namespace:
            return {}
            
        result = {}
        
        # Get parent config first
        if namespace.parent_namespace:
            result = self.get_config(namespace.parent_namespace)
            
        # Override with current values
        current = self._get_active_version(namespace)
        if current:
            result.update(current.values)
            
        return result
        
    def rollback(self, namespace_id: str, version: int,
                  changed_by: str = "system") -> bool:
        """Откат к версии"""
        namespace = self.namespaces.get(namespace_id)
        if not namespace:
            return False
            
        target_version = None
        for v in namespace.versions:
            if v.version == version:
                target_version = v
                break
                
        if not target_version:
            return False
            
        # Create rollback version
        rollback_version = ConfigVersion(
            version_id=f"v_{uuid.uuid4().hex[:8]}",
            version=namespace.current_version + 1,
            values=target_version.values.copy(),
            created_by=changed_by,
            message=f"Rollback to version {version}",
            active=True
        )
        rollback_version.checksum = self._calculate_checksum(rollback_version.values)
        
        # Deactivate current
        current = self._get_active_version(namespace)
        if current:
            current.active = False
            
        namespace.versions.append(rollback_version)
        namespace.current_version = rollback_version.version
        namespace.updated_at = datetime.now()
        
        # Record change
        change = ConfigChange(
            change_id=f"chg_{uuid.uuid4().hex[:8]}",
            namespace_id=namespace_id,
            change_type=ChangeType.ROLLBACK,
            changed_by=changed_by,
            reason=f"Rollback to version {version}"
        )
        self.changes.append(change)
        
        return True
        
    def _get_active_version(self, namespace: ConfigNamespace) -> Optional[ConfigVersion]:
        """Активная версия"""
        for v in namespace.versions:
            if v.active:
                return v
        return namespace.versions[-1] if namespace.versions else None
        
    def _calculate_checksum(self, values: Dict[str, Any]) -> str:
        """Расчёт контрольной суммы"""
        content = json.dumps(values, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class SchemaValidator:
    """Валидатор схем"""
    
    def __init__(self):
        self.schemas: Dict[str, Dict[str, ConfigValue]] = {}
        
    def register_schema(self, namespace_id: str,
                         schema: Dict[str, ConfigValue]):
        """Регистрация схемы"""
        self.schemas[namespace_id] = schema
        
    def validate(self, namespace_id: str, values: Dict[str, Any]) -> ValidationResult:
        """Валидация значений"""
        result = ValidationResult()
        
        schema = self.schemas.get(namespace_id, {})
        if not schema:
            return result
            
        for key, definition in schema.items():
            value = values.get(key)
            
            # Required check
            if definition.required and value is None:
                result.errors.append(f"Required field missing: {key}")
                continue
                
            if value is None:
                continue
                
            # Type check
            if definition.value_type == "int" and not isinstance(value, int):
                result.errors.append(f"Type mismatch for {key}: expected int")
            elif definition.value_type == "float" and not isinstance(value, (int, float)):
                result.errors.append(f"Type mismatch for {key}: expected float")
            elif definition.value_type == "bool" and not isinstance(value, bool):
                result.errors.append(f"Type mismatch for {key}: expected bool")
            elif definition.value_type == "string" and not isinstance(value, str):
                result.errors.append(f"Type mismatch for {key}: expected string")
                
            # Range check
            if definition.min_value is not None and isinstance(value, (int, float)):
                if value < definition.min_value:
                    result.errors.append(f"{key} below minimum: {definition.min_value}")
                    
            if definition.max_value is not None and isinstance(value, (int, float)):
                if value > definition.max_value:
                    result.errors.append(f"{key} above maximum: {definition.max_value}")
                    
            # Allowed values check
            if definition.allowed_values and value not in definition.allowed_values:
                result.errors.append(f"{key} not in allowed values: {definition.allowed_values}")
                
        # Unknown keys warning
        for key in values:
            if key not in schema:
                result.warnings.append(f"Unknown configuration key: {key}")
                
        result.status = (ValidationStatus.INVALID if result.errors 
                        else ValidationStatus.WARNING if result.warnings 
                        else ValidationStatus.VALID)
        
        return result


class EnvironmentManager:
    """Менеджер окружений"""
    
    def __init__(self, store: ConfigStore):
        self.store = store
        self.environments: Dict[str, Environment] = {}
        
    def create_environment(self, name: str, base_config: Dict[str, Any] = None) -> Environment:
        """Создание окружения"""
        env = Environment(
            environment_id=f"env_{uuid.uuid4().hex[:8]}",
            name=name,
            base_config=base_config or {}
        )
        
        self.environments[env.environment_id] = env
        return env
        
    def get_config_for_service(self, environment_id: str,
                                 service_name: str) -> Dict[str, Any]:
        """Конфигурация для сервиса"""
        env = self.environments.get(environment_id)
        if not env:
            return {}
            
        config = env.base_config.copy()
        config.update(env.overrides)
        
        # Service-specific config
        service_ns = None
        for namespace in self.store.namespaces.values():
            if namespace.name == service_name:
                service_ns = namespace
                break
                
        if service_ns:
            service_config = self.store.get_config(service_ns.namespace_id)
            config.update(service_config)
            
        return config


class ConfigDistributor:
    """Распространитель конфигураций"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[ConfigSubscriber]] = defaultdict(list)
        
    def subscribe(self, namespace_id: str, callback_url: str) -> ConfigSubscriber:
        """Подписка"""
        subscriber = ConfigSubscriber(
            subscriber_id=f"sub_{uuid.uuid4().hex[:8]}",
            namespace_id=namespace_id,
            callback_url=callback_url
        )
        
        self.subscribers[namespace_id].append(subscriber)
        return subscriber
        
    async def notify(self, namespace_id: str, change: ConfigChange):
        """Уведомление подписчиков"""
        for subscriber in self.subscribers.get(namespace_id, []):
            if subscriber.active:
                # Simulate notification
                await asyncio.sleep(0.01)
                subscriber.last_notified = datetime.now()
                subscriber.notifications_sent += 1


class ConfigurationManagementPlatform:
    """Платформа управления конфигурацией"""
    
    def __init__(self):
        self.store = ConfigStore()
        self.validator = SchemaValidator()
        self.environment_manager = EnvironmentManager(self.store)
        self.distributor = ConfigDistributor()
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_versions = sum(
            len(ns.versions) for ns in self.store.namespaces.values()
        )
        
        total_keys = sum(
            len(self._get_namespace_values(ns.namespace_id))
            for ns in self.store.namespaces.values()
        )
        
        return {
            "total_namespaces": len(self.store.namespaces),
            "total_versions": total_versions,
            "total_keys": total_keys,
            "total_changes": len(self.store.changes),
            "total_environments": len(self.environment_manager.environments),
            "total_subscribers": sum(len(s) for s in self.distributor.subscribers.values())
        }
        
    def _get_namespace_values(self, namespace_id: str) -> Dict[str, Any]:
        """Значения namespace"""
        return self.store.get_config(namespace_id)


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 123: Configuration Management Platform")
    print("=" * 60)
    
    async def demo():
        platform = ConfigurationManagementPlatform()
        print("✓ Configuration Management Platform created")
        
        # Create namespaces
        print("\n📁 Creating Config Namespaces...")
        
        # Global config
        global_ns = platform.store.create_namespace(
            "global", ConfigScope.GLOBAL
        )
        
        platform.store.set_value(global_ns.namespace_id, "app.name", "MyApp", "admin")
        platform.store.set_value(global_ns.namespace_id, "app.version", "1.0.0", "admin")
        platform.store.set_value(global_ns.namespace_id, "logging.level", "INFO", "admin")
        platform.store.set_value(global_ns.namespace_id, "metrics.enabled", True, "admin")
        
        print(f"  ✓ global: 4 keys (v{global_ns.current_version})")
        
        # Service configs
        services_config = [
            ("user-service", {"db.host": "localhost", "db.port": 5432, "cache.ttl": 300}),
            ("order-service", {"db.host": "localhost", "db.port": 5433, "queue.size": 1000}),
            ("payment-service", {"api.timeout": 30, "retry.max": 3, "ssl.enabled": True}),
            ("notification-service", {"smtp.host": "smtp.example.com", "template.path": "/templates"}),
        ]
        
        created_namespaces = [global_ns]
        for name, config in services_config:
            ns = platform.store.create_namespace(
                name, ConfigScope.SERVICE, parent=global_ns.namespace_id
            )
            for key, value in config.items():
                platform.store.set_value(ns.namespace_id, key, value, "admin")
            created_namespaces.append(ns)
            print(f"  ✓ {name}: {len(config)} keys (inherits global)")
            
        # Create schemas
        print("\n📋 Registering Config Schemas...")
        
        user_schema = {
            "db.host": ConfigValue("db.host", value_type="string", required=True),
            "db.port": ConfigValue("db.port", value_type="int", min_value=1, max_value=65535),
            "cache.ttl": ConfigValue("cache.ttl", value_type="int", min_value=0, max_value=3600),
        }
        
        platform.validator.register_schema(
            created_namespaces[1].namespace_id, user_schema
        )
        print(f"  ✓ user-service schema: {len(user_schema)} fields")
        
        # Create environments
        print("\n🌍 Creating Environments...")
        
        environments_data = [
            ("development", {"logging.level": "DEBUG", "metrics.enabled": False}),
            ("staging", {"logging.level": "INFO", "metrics.enabled": True}),
            ("production", {"logging.level": "WARN", "metrics.enabled": True}),
        ]
        
        created_envs = []
        for name, base in environments_data:
            env = platform.environment_manager.create_environment(name, base)
            created_envs.append(env)
            print(f"  ✓ {name}: {len(base)} overrides")
            
        # Subscribe to changes
        print("\n📬 Creating Subscriptions...")
        
        for ns in created_namespaces[1:]:
            sub = platform.distributor.subscribe(
                ns.namespace_id,
                f"http://{ns.name}:8080/config-update"
            )
            print(f"  ✓ {ns.name}: {sub.callback_url}")
            
        # Make config changes
        print("\n✏️ Making Configuration Changes...")
        
        changes_data = [
            (created_namespaces[1].namespace_id, "db.pool_size", 20),
            (created_namespaces[1].namespace_id, "cache.ttl", 600),
            (created_namespaces[2].namespace_id, "queue.size", 2000),
            (created_namespaces[3].namespace_id, "retry.max", 5),
        ]
        
        for ns_id, key, value in changes_data:
            platform.store.set_value(ns_id, key, value, "devops")
            ns = platform.store.namespaces.get(ns_id)
            print(f"  ✓ {ns.name}.{key} = {value}")
            
        # Validate configuration
        print("\n🔍 Validating Configurations...")
        
        for ns in created_namespaces[1:3]:
            config = platform.store.get_config(ns.namespace_id)
            result = platform.validator.validate(ns.namespace_id, config)
            
            status_icon = {"valid": "✓", "invalid": "✗", "warning": "⚠"}.get(result.status.value, "?")
            print(f"  {status_icon} {ns.name}: {result.status.value}")
            for error in result.errors:
                print(f"      Error: {error}")
            for warning in result.warnings[:2]:
                print(f"      Warning: {warning}")
                
        # Get resolved config
        print("\n📦 Resolved Configurations:")
        
        for ns in created_namespaces[1:3]:
            config = platform.store.get_config(ns.namespace_id)
            print(f"\n  {ns.name}:")
            for key, value in list(config.items())[:5]:
                print(f"    {key}: {value}")
            if len(config) > 5:
                print(f"    ... +{len(config)-5} more")
                
        # Version history
        print("\n📜 Version History:")
        
        for ns in created_namespaces[:2]:
            print(f"\n  {ns.name}:")
            for v in ns.versions[-3:]:
                status = "●" if v.active else "○"
                print(f"    {status} v{v.version}: {v.message} ({v.created_by})")
                
        # Rollback demonstration
        print("\n⏪ Rollback Demonstration:")
        
        user_ns = created_namespaces[1]
        before_config = platform.store.get_config(user_ns.namespace_id)
        print(f"  Before: cache.ttl = {before_config.get('cache.ttl')}")
        
        # Rollback to version 2
        platform.store.rollback(user_ns.namespace_id, 2, "admin")
        
        after_config = platform.store.get_config(user_ns.namespace_id)
        print(f"  After rollback to v2: cache.ttl = {after_config.get('cache.ttl')}")
        print(f"  Current version: v{user_ns.current_version}")
        
        # Environment-specific config
        print("\n🌐 Environment-Specific Config:")
        
        for env in created_envs[:2]:
            config = platform.environment_manager.get_config_for_service(
                env.environment_id, "user-service"
            )
            print(f"\n  {env.name}:")
            print(f"    logging.level: {config.get('logging.level', 'N/A')}")
            print(f"    metrics.enabled: {config.get('metrics.enabled', 'N/A')}")
            
        # Change history
        print("\n📊 Recent Changes:")
        
        for change in platform.store.changes[-5:]:
            ns = platform.store.namespaces.get(change.namespace_id)
            ns_name = ns.name if ns else "unknown"
            time_str = change.changed_at.strftime("%H:%M:%S")
            print(f"  [{time_str}] {ns_name}: {change.change_type.value} {change.key or ''}")
            
        # Statistics
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Namespaces: {stats['total_namespaces']}")
        print(f"  Versions: {stats['total_versions']}")
        print(f"  Config Keys: {stats['total_keys']}")
        print(f"  Changes: {stats['total_changes']}")
        print(f"  Environments: {stats['total_environments']}")
        print(f"  Subscribers: {stats['total_subscribers']}")
        
        # Namespace breakdown
        print("\n📁 Namespace Breakdown:")
        
        for ns in created_namespaces:
            config = platform.store.get_config(ns.namespace_id)
            print(f"  {ns.name}: {len(config)} keys, {len(ns.versions)} versions")
            
        # Dashboard
        print("\n📋 Configuration Management Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │          Configuration Management Overview                  │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Namespaces:           {stats['total_namespaces']:>10}                      │")
        print(f"  │ Total Versions:       {stats['total_versions']:>10}                      │")
        print(f"  │ Config Keys:          {stats['total_keys']:>10}                      │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Changes:        {stats['total_changes']:>10}                      │")
        print(f"  │ Environments:         {stats['total_environments']:>10}                      │")
        print(f"  │ Subscribers:          {stats['total_subscribers']:>10}                      │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Configuration Management Platform initialized!")
    print("=" * 60)
