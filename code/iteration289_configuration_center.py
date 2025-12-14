#!/usr/bin/env python3
"""
Server Init - Iteration 289: Configuration Center Platform
Платформа Configuration Center

Функционал:
- Configuration Storage - хранение конфигураций
- Namespace Management - управление пространствами имён
- Version Control - контроль версий
- Hot Reload - горячая перезагрузка
- Environment Override - переопределение по окружению
- Config Validation - валидация конфигураций
- Encryption - шифрование секретов
- Watch/Subscribe - подписка на изменения
"""

import asyncio
import random
import time
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Union
from enum import Enum
import uuid
import hashlib


class ConfigFormat(Enum):
    """Формат конфигурации"""
    JSON = "json"
    YAML = "yaml"
    PROPERTIES = "properties"
    TOML = "toml"
    INI = "ini"


class ConfigScope(Enum):
    """Область конфигурации"""
    GLOBAL = "global"
    NAMESPACE = "namespace"
    SERVICE = "service"
    INSTANCE = "instance"


class ConfigStatus(Enum):
    """Статус конфигурации"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    DRAFT = "draft"
    ARCHIVED = "archived"


class ValueType(Enum):
    """Тип значения"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"
    SECRET = "secret"


@dataclass
class ConfigValue:
    """Значение конфигурации"""
    key: str
    value: Any
    
    # Type
    value_type: ValueType = ValueType.STRING
    
    # Metadata
    description: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Encryption
    encrypted: bool = False
    
    # Validation
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    pattern: str = ""
    allowed_values: List[Any] = field(default_factory=list)
    
    # History
    version: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ConfigVersion:
    """Версия конфигурации"""
    version_id: str
    version_number: int
    
    # Values snapshot
    values: Dict[str, Any] = field(default_factory=dict)
    
    # Changes
    changes: List[str] = field(default_factory=list)
    
    # Metadata
    comment: str = ""
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ConfigNamespace:
    """Пространство имён конфигурации"""
    namespace_id: str
    name: str
    
    # Configs
    configs: Dict[str, ConfigValue] = field(default_factory=dict)
    
    # Versions
    versions: List[ConfigVersion] = field(default_factory=list)
    current_version: int = 1
    
    # Scope
    scope: ConfigScope = ConfigScope.NAMESPACE
    
    # Status
    status: ConfigStatus = ConfigStatus.ACTIVE
    
    # Metadata
    description: str = ""
    owner: str = ""
    
    # Created
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Environment:
    """Окружение"""
    env_id: str
    name: str
    
    # Priority (higher overrides lower)
    priority: int = 0
    
    # Overrides
    overrides: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Active
    active: bool = True


@dataclass
class ConfigWatcher:
    """Наблюдатель конфигурации"""
    watcher_id: str
    namespace: str
    keys: List[str] = field(default_factory=list)  # Empty = all keys
    
    # Callback
    callback: Optional[Callable] = None
    
    # Last seen version
    last_version: int = 0


@dataclass
class ValidationRule:
    """Правило валидации"""
    rule_id: str
    key_pattern: str
    
    # Rules
    required: bool = False
    value_type: ValueType = ValueType.STRING
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    pattern: str = ""
    custom_validator: Optional[Callable] = None


class ConfigurationCenterManager:
    """Менеджер Configuration Center"""
    
    def __init__(self, encryption_key: str = "default_key"):
        self.namespaces: Dict[str, ConfigNamespace] = {}
        self.environments: Dict[str, Environment] = {}
        self.watchers: Dict[str, List[ConfigWatcher]] = {}
        self.validation_rules: Dict[str, ValidationRule] = {}
        
        # Encryption
        self.encryption_key = encryption_key
        
        # Cache
        self.resolved_cache: Dict[str, Dict[str, Any]] = {}
        
        # Stats
        self.reads: int = 0
        self.writes: int = 0
        self.notifications: int = 0
        
    async def create_namespace(self, name: str,
                              scope: ConfigScope = ConfigScope.NAMESPACE,
                              description: str = "",
                              owner: str = "") -> ConfigNamespace:
        """Создание пространства имён"""
        namespace = ConfigNamespace(
            namespace_id=f"ns_{uuid.uuid4().hex[:8]}",
            name=name,
            scope=scope,
            description=description,
            owner=owner
        )
        
        self.namespaces[name] = namespace
        self.watchers[name] = []
        
        return namespace
        
    async def set_config(self, namespace: str,
                        key: str,
                        value: Any,
                        value_type: ValueType = ValueType.STRING,
                        description: str = "",
                        encrypted: bool = False) -> ConfigValue:
        """Установка конфигурации"""
        ns = self.namespaces.get(namespace)
        if not ns:
            ns = await self.create_namespace(namespace)
            
        # Validate
        if not await self._validate_value(namespace, key, value, value_type):
            raise ValueError(f"Validation failed for {key}")
            
        # Encrypt if needed
        stored_value = value
        if encrypted:
            stored_value = self._encrypt(value)
            
        # Check if exists
        old_value = None
        if key in ns.configs:
            old_value = ns.configs[key].value
            config = ns.configs[key]
            config.value = stored_value
            config.version += 1
            config.updated_at = datetime.now()
            config.encrypted = encrypted
        else:
            config = ConfigValue(
                key=key,
                value=stored_value,
                value_type=value_type,
                description=description,
                encrypted=encrypted
            )
            ns.configs[key] = config
            
        self.writes += 1
        
        # Clear cache
        self._clear_cache(namespace)
        
        # Create version if significant change
        if old_value != stored_value:
            await self._create_version(namespace, f"Updated {key}")
            await self._notify_watchers(namespace, key, value)
            
        return config
        
    async def set_configs(self, namespace: str,
                         configs: Dict[str, Any]) -> int:
        """Установка множества конфигураций"""
        count = 0
        
        for key, value in configs.items():
            await self.set_config(namespace, key, value)
            count += 1
            
        return count
        
    async def get_config(self, namespace: str,
                        key: str,
                        environment: str = None,
                        default: Any = None) -> Any:
        """Получение конфигурации"""
        self.reads += 1
        
        ns = self.namespaces.get(namespace)
        if not ns:
            return default
            
        config = ns.configs.get(key)
        if not config:
            return default
            
        value = config.value
        
        # Apply environment override
        if environment:
            env = self.environments.get(environment)
            if env and namespace in env.overrides:
                if key in env.overrides[namespace]:
                    value = env.overrides[namespace][key]
                    
        # Decrypt if needed
        if config.encrypted:
            value = self._decrypt(value)
            
        return value
        
    async def get_all_configs(self, namespace: str,
                             environment: str = None) -> Dict[str, Any]:
        """Получение всех конфигураций"""
        self.reads += 1
        
        # Check cache
        cache_key = f"{namespace}:{environment or 'default'}"
        if cache_key in self.resolved_cache:
            return self.resolved_cache[cache_key].copy()
            
        ns = self.namespaces.get(namespace)
        if not ns:
            return {}
            
        result = {}
        
        for key, config in ns.configs.items():
            value = config.value
            
            if config.encrypted:
                value = self._decrypt(value)
                
            result[key] = value
            
        # Apply environment overrides
        if environment:
            env = self.environments.get(environment)
            if env and namespace in env.overrides:
                result.update(env.overrides[namespace])
                
        # Cache result
        self.resolved_cache[cache_key] = result.copy()
        
        return result
        
    async def delete_config(self, namespace: str, key: str) -> bool:
        """Удаление конфигурации"""
        ns = self.namespaces.get(namespace)
        if not ns or key not in ns.configs:
            return False
            
        del ns.configs[key]
        
        # Clear cache
        self._clear_cache(namespace)
        
        await self._create_version(namespace, f"Deleted {key}")
        await self._notify_watchers(namespace, key, None)
        
        return True
        
    async def create_environment(self, name: str,
                                priority: int = 0) -> Environment:
        """Создание окружения"""
        env = Environment(
            env_id=f"env_{uuid.uuid4().hex[:8]}",
            name=name,
            priority=priority
        )
        
        self.environments[name] = env
        return env
        
    async def set_override(self, environment: str,
                          namespace: str,
                          key: str,
                          value: Any):
        """Установка переопределения"""
        env = self.environments.get(environment)
        if not env:
            env = await self.create_environment(environment)
            
        if namespace not in env.overrides:
            env.overrides[namespace] = {}
            
        env.overrides[namespace][key] = value
        
        # Clear cache
        self._clear_cache(namespace)
        
    async def watch(self, namespace: str,
                   keys: List[str] = None,
                   callback: Callable = None) -> ConfigWatcher:
        """Подписка на изменения"""
        ns = self.namespaces.get(namespace)
        
        watcher = ConfigWatcher(
            watcher_id=f"watch_{uuid.uuid4().hex[:8]}",
            namespace=namespace,
            keys=keys or [],
            callback=callback,
            last_version=ns.current_version if ns else 0
        )
        
        if namespace not in self.watchers:
            self.watchers[namespace] = []
            
        self.watchers[namespace].append(watcher)
        return watcher
        
    def unwatch(self, watcher_id: str):
        """Отписка"""
        for ns, watchers in self.watchers.items():
            self.watchers[ns] = [w for w in watchers if w.watcher_id != watcher_id]
            
    async def _notify_watchers(self, namespace: str, key: str, value: Any):
        """Уведомление наблюдателей"""
        if namespace not in self.watchers:
            return
            
        ns = self.namespaces.get(namespace)
        
        for watcher in self.watchers[namespace]:
            # Check if interested in this key
            if watcher.keys and key not in watcher.keys:
                continue
                
            if watcher.callback:
                try:
                    await watcher.callback(namespace, key, value)
                    self.notifications += 1
                    
                    if ns:
                        watcher.last_version = ns.current_version
                except Exception:
                    pass
                    
    async def _create_version(self, namespace: str, comment: str = ""):
        """Создание версии"""
        ns = self.namespaces.get(namespace)
        if not ns:
            return
            
        # Snapshot current values
        values = {}
        for key, config in ns.configs.items():
            values[key] = config.value
            
        version = ConfigVersion(
            version_id=f"ver_{uuid.uuid4().hex[:8]}",
            version_number=ns.current_version + 1,
            values=values,
            comment=comment
        )
        
        ns.versions.append(version)
        ns.current_version += 1
        
        # Keep only last 100 versions
        if len(ns.versions) > 100:
            ns.versions = ns.versions[-100:]
            
    async def rollback(self, namespace: str, version_number: int) -> bool:
        """Откат к версии"""
        ns = self.namespaces.get(namespace)
        if not ns:
            return False
            
        # Find version
        version = None
        for v in ns.versions:
            if v.version_number == version_number:
                version = v
                break
                
        if not version:
            return False
            
        # Restore values
        ns.configs.clear()
        
        for key, value in version.values.items():
            ns.configs[key] = ConfigValue(key=key, value=value)
            
        await self._create_version(namespace, f"Rollback to v{version_number}")
        
        # Clear cache
        self._clear_cache(namespace)
        
        return True
        
    async def add_validation_rule(self, key_pattern: str,
                                 rule: ValidationRule) -> str:
        """Добавление правила валидации"""
        rule_id = f"rule_{uuid.uuid4().hex[:8]}"
        rule.rule_id = rule_id
        rule.key_pattern = key_pattern
        
        self.validation_rules[rule_id] = rule
        return rule_id
        
    async def _validate_value(self, namespace: str,
                             key: str,
                             value: Any,
                             value_type: ValueType) -> bool:
        """Валидация значения"""
        for rule in self.validation_rules.values():
            if key.startswith(rule.key_pattern.replace("*", "")):
                # Check type
                if rule.value_type != value_type:
                    return False
                    
                # Check numeric bounds
                if isinstance(value, (int, float)):
                    if rule.min_value and value < rule.min_value:
                        return False
                    if rule.max_value and value > rule.max_value:
                        return False
                        
                # Custom validator
                if rule.custom_validator:
                    if not rule.custom_validator(value):
                        return False
                        
        return True
        
    def _encrypt(self, value: str) -> str:
        """Шифрование"""
        # Simple XOR encryption for demo
        key = self.encryption_key
        result = []
        for i, char in enumerate(str(value)):
            result.append(chr(ord(char) ^ ord(key[i % len(key)])))
        return "enc:" + "".join(result)
        
    def _decrypt(self, value: str) -> str:
        """Дешифрование"""
        if not value.startswith("enc:"):
            return value
            
        encrypted = value[4:]
        key = self.encryption_key
        result = []
        for i, char in enumerate(encrypted):
            result.append(chr(ord(char) ^ ord(key[i % len(key)])))
        return "".join(result)
        
    def _clear_cache(self, namespace: str):
        """Очистка кэша"""
        keys_to_delete = [k for k in self.resolved_cache if k.startswith(namespace)]
        for key in keys_to_delete:
            del self.resolved_cache[key]
            
    def export_namespace(self, namespace: str,
                        format: ConfigFormat = ConfigFormat.JSON) -> str:
        """Экспорт пространства имён"""
        ns = self.namespaces.get(namespace)
        if not ns:
            return ""
            
        data = {}
        for key, config in ns.configs.items():
            data[key] = {
                "value": config.value,
                "type": config.value_type.value,
                "description": config.description
            }
            
        if format == ConfigFormat.JSON:
            return json.dumps(data, indent=2, default=str)
            
        return json.dumps(data, default=str)
        
    async def import_namespace(self, namespace: str,
                              data: str,
                              format: ConfigFormat = ConfigFormat.JSON):
        """Импорт пространства имён"""
        if format == ConfigFormat.JSON:
            configs = json.loads(data)
            
            for key, config in configs.items():
                value = config.get("value")
                desc = config.get("description", "")
                
                await self.set_config(namespace, key, value, description=desc)
                
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_configs = sum(len(ns.configs) for ns in self.namespaces.values())
        
        return {
            "namespaces": len(self.namespaces),
            "total_configs": total_configs,
            "environments": len(self.environments),
            "watchers": sum(len(w) for w in self.watchers.values()),
            "reads": self.reads,
            "writes": self.writes,
            "notifications": self.notifications,
            "cache_entries": len(self.resolved_cache)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 289: Configuration Center Platform")
    print("=" * 60)
    
    manager = ConfigurationCenterManager(encryption_key="my_secret_key_123")
    print("✓ Configuration Center Manager created")
    
    # Create namespaces
    print("\n📁 Creating Namespaces...")
    
    await manager.create_namespace(
        "application",
        scope=ConfigScope.GLOBAL,
        description="Main application configuration"
    )
    print("  📁 Created: application")
    
    await manager.create_namespace(
        "database",
        description="Database configuration"
    )
    print("  📁 Created: database")
    
    await manager.create_namespace(
        "security",
        description="Security settings"
    )
    print("  📁 Created: security")
    
    # Set configurations
    print("\n⚙️ Setting Configurations...")
    
    # Application config
    await manager.set_config(
        "application", "app.name", "MyApp",
        description="Application name"
    )
    await manager.set_config(
        "application", "app.version", "2.0.0",
        description="Application version"
    )
    await manager.set_config(
        "application", "app.debug", True,
        value_type=ValueType.BOOLEAN
    )
    await manager.set_config(
        "application", "app.port", 8080,
        value_type=ValueType.INTEGER
    )
    print("  ⚙️ Set application configs: 4 keys")
    
    # Database config
    await manager.set_configs("database", {
        "db.host": "localhost",
        "db.port": 5432,
        "db.name": "myapp_db",
        "db.pool_size": 10,
        "db.timeout": 30
    })
    print("  ⚙️ Set database configs: 5 keys")
    
    # Security config with encryption
    await manager.set_config(
        "security", "jwt.secret", "super_secret_jwt_key",
        encrypted=True,
        description="JWT signing secret"
    )
    await manager.set_config(
        "security", "api.key", "api_key_12345",
        encrypted=True
    )
    await manager.set_config(
        "security", "session.timeout", 3600,
        value_type=ValueType.INTEGER
    )
    print("  🔐 Set security configs: 3 keys (2 encrypted)")
    
    # Create environments
    print("\n🌍 Creating Environments...")
    
    await manager.create_environment("development", priority=0)
    await manager.create_environment("staging", priority=1)
    await manager.create_environment("production", priority=2)
    print("  🌍 Created: development, staging, production")
    
    # Set environment overrides
    print("\n🔄 Setting Environment Overrides...")
    
    # Production overrides
    await manager.set_override("production", "application", "app.debug", False)
    await manager.set_override("production", "database", "db.host", "db.production.internal")
    await manager.set_override("production", "database", "db.pool_size", 50)
    print("  🔄 Production: 3 overrides")
    
    # Staging overrides
    await manager.set_override("staging", "database", "db.host", "db.staging.internal")
    await manager.set_override("staging", "database", "db.pool_size", 20)
    print("  🔄 Staging: 2 overrides")
    
    # Watch for changes
    print("\n👁️ Setting up Watchers...")
    
    async def on_config_change(namespace: str, key: str, value: Any):
        print(f"  🔔 Config changed: {namespace}/{key} = {value}")
        
    watcher = await manager.watch("application", callback=on_config_change)
    print(f"  👁️ Watching application namespace")
    
    # Read configurations
    print("\n📖 Reading Configurations...")
    
    # Default environment
    app_name = await manager.get_config("application", "app.name")
    app_debug = await manager.get_config("application", "app.debug")
    print(f"\n  Default Environment:")
    print(f"    app.name: {app_name}")
    print(f"    app.debug: {app_debug}")
    
    # Production environment
    print(f"\n  Production Environment:")
    app_debug_prod = await manager.get_config("application", "app.debug", "production")
    db_host_prod = await manager.get_config("database", "db.host", "production")
    print(f"    app.debug: {app_debug_prod}")
    print(f"    db.host: {db_host_prod}")
    
    # Staging environment
    print(f"\n  Staging Environment:")
    db_host_staging = await manager.get_config("database", "db.host", "staging")
    db_pool_staging = await manager.get_config("database", "db.pool_size", "staging")
    print(f"    db.host: {db_host_staging}")
    print(f"    db.pool_size: {db_pool_staging}")
    
    # Get all configs
    print("\n📋 All Configurations by Namespace:")
    
    for ns_name in ["application", "database"]:
        configs = await manager.get_all_configs(ns_name)
        print(f"\n  📁 {ns_name}:")
        for key, value in configs.items():
            print(f"    {key}: {value}")
            
    # Read encrypted value
    print("\n🔐 Reading Encrypted Values...")
    
    jwt_secret = await manager.get_config("security", "jwt.secret")
    print(f"  jwt.secret (decrypted): {jwt_secret}")
    
    # Update config (triggers watcher)
    print("\n✏️ Updating Configuration...")
    
    await manager.set_config("application", "app.version", "2.1.0")
    
    # Export namespace
    print("\n📤 Exporting Namespace...")
    
    exported = manager.export_namespace("application")
    print(f"  Exported application namespace (JSON):")
    print(f"  {exported[:100]}...")
    
    # Version history
    print("\n📚 Version History:")
    
    for ns_name, ns in manager.namespaces.items():
        if ns.versions:
            print(f"\n  📁 {ns_name}:")
            for version in ns.versions[-5:]:
                print(f"    v{version.version_number}: {version.comment}")
                
    # Namespace details
    print("\n📋 Namespace Details:")
    
    print("\n  ┌────────────────────┬────────────┬────────────┬────────────┬───────────────┐")
    print("  │ Namespace          │ Configs    │ Versions   │ Scope      │ Status        │")
    print("  ├────────────────────┼────────────┼────────────┼────────────┼───────────────┤")
    
    for ns in manager.namespaces.values():
        name = ns.name[:18].ljust(18)
        configs = str(len(ns.configs)).ljust(10)
        versions = str(len(ns.versions)).ljust(10)
        scope = ns.scope.value[:10].ljust(10)
        status = ns.status.value[:13].ljust(13)
        
        print(f"  │ {name} │ {configs} │ {versions} │ {scope} │ {status} │")
        
    print("  └────────────────────┴────────────┴────────────┴────────────┴───────────────┘")
    
    # Environment overrides
    print("\n🌍 Environment Overrides:")
    
    for env in manager.environments.values():
        print(f"\n  🌍 {env.name} (priority: {env.priority}):")
        for ns, overrides in env.overrides.items():
            for key, value in overrides.items():
                print(f"    {ns}/{key}: {value}")
                
    # Watchers
    print("\n👁️ Active Watchers:")
    
    for ns_name, watchers in manager.watchers.items():
        if watchers:
            print(f"\n  📁 {ns_name}: {len(watchers)} watchers")
            for w in watchers:
                keys = w.keys or ["*"]
                print(f"    • {w.watcher_id}: watching {keys}")
                
    # Statistics
    print("\n📊 Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Namespaces: {stats['namespaces']}")
    print(f"  Total Configs: {stats['total_configs']}")
    print(f"  Environments: {stats['environments']}")
    print(f"  Active Watchers: {stats['watchers']}")
    print(f"\n  Reads: {stats['reads']}")
    print(f"  Writes: {stats['writes']}")
    print(f"  Notifications: {stats['notifications']}")
    print(f"  Cache Entries: {stats['cache_entries']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Configuration Center Dashboard                    │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Namespaces:              {stats['namespaces']:>12}                        │")
    print(f"│ Total Configurations:          {stats['total_configs']:>12}                        │")
    print(f"│ Environments:                  {stats['environments']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Read Operations:               {stats['reads']:>12}                        │")
    print(f"│ Write Operations:              {stats['writes']:>12}                        │")
    print(f"│ Change Notifications:          {stats['notifications']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Configuration Center Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
