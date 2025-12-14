#!/usr/bin/env python3
"""
Server Init - Iteration 204: Config Management Platform
Платформа управления конфигурацией

Функционал:
- Config Storage - хранение конфигураций
- Environment Management - управление окружениями
- Secret Management - управление секретами
- Config Versioning - версионирование
- Config Validation - валидация
- Config Distribution - распространение
- Hot Reload - горячая перезагрузка
- Audit Trail - аудит изменений
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import json
import hashlib


class ConfigType(Enum):
    """Тип конфигурации"""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    JSON = "json"
    SECRET = "secret"


class EnvironmentType(Enum):
    """Тип окружения"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class ChangeType(Enum):
    """Тип изменения"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ROLLBACK = "rollback"


@dataclass
class ConfigValue:
    """Значение конфигурации"""
    value_id: str
    
    # Key
    key: str = ""
    
    # Value
    value: Any = None
    config_type: ConfigType = ConfigType.STRING
    
    # Encrypted for secrets
    is_encrypted: bool = False
    
    # Version
    version: int = 1
    
    # Metadata
    description: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def get_hash(self) -> str:
        """Получение хэша значения"""
        return hashlib.sha256(str(self.value).encode()).hexdigest()[:16]


@dataclass
class ConfigNamespace:
    """Пространство имён конфигурации"""
    namespace_id: str
    name: str = ""
    
    # Values
    values: Dict[str, ConfigValue] = field(default_factory=dict)
    
    # Environment
    environment: EnvironmentType = EnvironmentType.DEVELOPMENT
    
    # Application
    application: str = ""
    
    # Metadata
    owner: str = ""
    description: str = ""
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ConfigVersion:
    """Версия конфигурации"""
    version_id: str
    namespace_id: str
    
    # Version
    version: int = 1
    
    # Snapshot
    snapshot: Dict[str, Any] = field(default_factory=dict)
    
    # Change
    change_type: ChangeType = ChangeType.UPDATE
    changed_keys: List[str] = field(default_factory=list)
    
    # Author
    author: str = ""
    message: str = ""
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ConfigAuditEntry:
    """Запись аудита"""
    audit_id: str
    
    # Target
    namespace_id: str = ""
    key: str = ""
    
    # Change
    change_type: ChangeType = ChangeType.UPDATE
    old_value: Any = None
    new_value: Any = None
    
    # Author
    author: str = ""
    
    # Time
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ValidationRule:
    """Правило валидации"""
    rule_id: str
    name: str = ""
    
    # Target
    key_pattern: str = ""
    
    # Validation
    required: bool = False
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    pattern: str = ""
    allowed_values: List[Any] = field(default_factory=list)


@dataclass
class WatchSubscription:
    """Подписка на изменения"""
    subscription_id: str
    
    # Target
    namespace_id: str = ""
    key_pattern: str = ""
    
    # Callback
    callback_url: str = ""
    
    # State
    is_active: bool = True
    
    # Created
    created_at: datetime = field(default_factory=datetime.now)


class ConfigStore:
    """Хранилище конфигураций"""
    
    def __init__(self):
        self.namespaces: Dict[str, ConfigNamespace] = {}
        self.versions: Dict[str, List[ConfigVersion]] = {}
        
    def create_namespace(self, name: str, environment: EnvironmentType,
                        application: str = "") -> ConfigNamespace:
        """Создание пространства имён"""
        namespace = ConfigNamespace(
            namespace_id=f"ns_{uuid.uuid4().hex[:8]}",
            name=name,
            environment=environment,
            application=application
        )
        self.namespaces[namespace.namespace_id] = namespace
        self.versions[namespace.namespace_id] = []
        return namespace
        
    def set_value(self, namespace_id: str, key: str, value: Any,
                 config_type: ConfigType = ConfigType.STRING,
                 description: str = "") -> ConfigValue:
        """Установка значения"""
        namespace = self.namespaces.get(namespace_id)
        if not namespace:
            raise ValueError(f"Namespace {namespace_id} not found")
            
        existing = namespace.values.get(key)
        version = existing.version + 1 if existing else 1
        
        config_value = ConfigValue(
            value_id=f"val_{uuid.uuid4().hex[:8]}",
            key=key,
            value=value,
            config_type=config_type,
            version=version,
            description=description,
            is_encrypted=config_type == ConfigType.SECRET
        )
        
        namespace.values[key] = config_value
        namespace.updated_at = datetime.now()
        
        return config_value
        
    def get_value(self, namespace_id: str, key: str) -> Optional[ConfigValue]:
        """Получение значения"""
        namespace = self.namespaces.get(namespace_id)
        if namespace:
            return namespace.values.get(key)
        return None
        
    def get_all_values(self, namespace_id: str) -> Dict[str, Any]:
        """Получение всех значений"""
        namespace = self.namespaces.get(namespace_id)
        if namespace:
            return {k: v.value for k, v in namespace.values.items()}
        return {}
        
    def delete_value(self, namespace_id: str, key: str) -> bool:
        """Удаление значения"""
        namespace = self.namespaces.get(namespace_id)
        if namespace and key in namespace.values:
            del namespace.values[key]
            return True
        return False


class SecretManager:
    """Менеджер секретов"""
    
    def __init__(self, store: ConfigStore):
        self.store = store
        self.encryption_key = "secret_key_placeholder"
        
    def encrypt(self, value: str) -> str:
        """Шифрование (симуляция)"""
        return f"encrypted:{hashlib.sha256(value.encode()).hexdigest()[:32]}"
        
    def decrypt(self, encrypted_value: str) -> str:
        """Дешифрование (симуляция)"""
        return "***DECRYPTED***"
        
    def set_secret(self, namespace_id: str, key: str, value: str) -> ConfigValue:
        """Установка секрета"""
        encrypted = self.encrypt(value)
        return self.store.set_value(
            namespace_id, key, encrypted,
            ConfigType.SECRET,
            "Encrypted secret"
        )
        
    def get_secret(self, namespace_id: str, key: str) -> Optional[str]:
        """Получение секрета"""
        config_value = self.store.get_value(namespace_id, key)
        if config_value and config_value.config_type == ConfigType.SECRET:
            return self.decrypt(config_value.value)
        return None


class ConfigValidator:
    """Валидатор конфигураций"""
    
    def __init__(self):
        self.rules: List[ValidationRule] = []
        
    def add_rule(self, rule: ValidationRule):
        """Добавление правила"""
        self.rules.append(rule)
        
    def validate(self, key: str, value: Any) -> List[str]:
        """Валидация значения"""
        errors = []
        
        for rule in self.rules:
            if rule.key_pattern and rule.key_pattern not in key:
                continue
                
            if rule.required and value is None:
                errors.append(f"{key}: required value is missing")
                
            if rule.min_value is not None and isinstance(value, (int, float)):
                if value < rule.min_value:
                    errors.append(f"{key}: value {value} < min {rule.min_value}")
                    
            if rule.max_value is not None and isinstance(value, (int, float)):
                if value > rule.max_value:
                    errors.append(f"{key}: value {value} > max {rule.max_value}")
                    
            if rule.allowed_values and value not in rule.allowed_values:
                errors.append(f"{key}: value not in allowed list")
                
        return errors


class AuditTrail:
    """Аудит изменений"""
    
    def __init__(self):
        self.entries: List[ConfigAuditEntry] = []
        
    def log(self, namespace_id: str, key: str, change_type: ChangeType,
           old_value: Any, new_value: Any, author: str = ""):
        """Запись в аудит"""
        entry = ConfigAuditEntry(
            audit_id=f"audit_{uuid.uuid4().hex[:8]}",
            namespace_id=namespace_id,
            key=key,
            change_type=change_type,
            old_value=old_value,
            new_value=new_value,
            author=author
        )
        self.entries.append(entry)
        return entry
        
    def get_history(self, namespace_id: str = None, key: str = None,
                   limit: int = 100) -> List[ConfigAuditEntry]:
        """Получение истории"""
        entries = self.entries
        
        if namespace_id:
            entries = [e for e in entries if e.namespace_id == namespace_id]
            
        if key:
            entries = [e for e in entries if e.key == key]
            
        return entries[-limit:]


class ConfigManagementPlatform:
    """Платформа управления конфигурацией"""
    
    def __init__(self):
        self.store = ConfigStore()
        self.secrets = SecretManager(self.store)
        self.validator = ConfigValidator()
        self.audit = AuditTrail()
        self.subscriptions: Dict[str, WatchSubscription] = {}
        
    def create_namespace(self, name: str, environment: EnvironmentType,
                        application: str = "") -> ConfigNamespace:
        """Создание пространства имён"""
        return self.store.create_namespace(name, environment, application)
        
    def set_config(self, namespace_id: str, key: str, value: Any,
                  config_type: ConfigType = ConfigType.STRING,
                  author: str = "") -> ConfigValue:
        """Установка конфигурации"""
        # Validate
        errors = self.validator.validate(key, value)
        if errors:
            raise ValueError(f"Validation errors: {errors}")
            
        # Get old value for audit
        old_value = self.store.get_value(namespace_id, key)
        old_val = old_value.value if old_value else None
        
        # Set new value
        if config_type == ConfigType.SECRET:
            config_value = self.secrets.set_secret(namespace_id, key, str(value))
        else:
            config_value = self.store.set_value(namespace_id, key, value, config_type)
            
        # Audit
        change_type = ChangeType.UPDATE if old_value else ChangeType.CREATE
        self.audit.log(namespace_id, key, change_type, old_val, value, author)
        
        return config_value
        
    def get_config(self, namespace_id: str, key: str = None) -> Any:
        """Получение конфигурации"""
        if key:
            val = self.store.get_value(namespace_id, key)
            return val.value if val else None
        return self.store.get_all_values(namespace_id)
        
    def delete_config(self, namespace_id: str, key: str, author: str = "") -> bool:
        """Удаление конфигурации"""
        old_value = self.store.get_value(namespace_id, key)
        if old_value:
            self.store.delete_value(namespace_id, key)
            self.audit.log(namespace_id, key, ChangeType.DELETE, 
                          old_value.value, None, author)
            return True
        return False
        
    def subscribe(self, namespace_id: str, callback_url: str,
                 key_pattern: str = "") -> WatchSubscription:
        """Подписка на изменения"""
        subscription = WatchSubscription(
            subscription_id=f"sub_{uuid.uuid4().hex[:8]}",
            namespace_id=namespace_id,
            key_pattern=key_pattern,
            callback_url=callback_url
        )
        self.subscriptions[subscription.subscription_id] = subscription
        return subscription
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_values = sum(len(ns.values) for ns in self.store.namespaces.values())
        secrets = sum(1 for ns in self.store.namespaces.values() 
                     for v in ns.values.values() if v.config_type == ConfigType.SECRET)
        
        return {
            "total_namespaces": len(self.store.namespaces),
            "total_values": total_values,
            "total_secrets": secrets,
            "audit_entries": len(self.audit.entries),
            "subscriptions": len(self.subscriptions),
            "validation_rules": len(self.validator.rules)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 204: Config Management Platform")
    print("=" * 60)
    
    platform = ConfigManagementPlatform()
    print("✓ Config Management Platform created")
    
    # Add validation rules
    print("\n📋 Adding Validation Rules...")
    
    rules = [
        ValidationRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name="Port Range",
            key_pattern="port",
            min_value=1,
            max_value=65535
        ),
        ValidationRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name="Log Level",
            key_pattern="log_level",
            allowed_values=["debug", "info", "warning", "error"]
        ),
    ]
    
    for rule in rules:
        platform.validator.add_rule(rule)
        print(f"  ✓ {rule.name}")
        
    # Create namespaces
    print("\n📁 Creating Namespaces...")
    
    namespaces = {}
    for env in [EnvironmentType.DEVELOPMENT, EnvironmentType.STAGING, EnvironmentType.PRODUCTION]:
        ns = platform.create_namespace(f"api-service-{env.value}", env, "api-service")
        namespaces[env] = ns
        print(f"  ✓ {ns.name}")
        
    # Set configurations
    print("\n⚙️ Setting Configurations...")
    
    configs = [
        ("database.host", "localhost", ConfigType.STRING),
        ("database.port", 5432, ConfigType.NUMBER),
        ("database.pool_size", 10, ConfigType.NUMBER),
        ("cache.enabled", True, ConfigType.BOOLEAN),
        ("cache.ttl_seconds", 3600, ConfigType.NUMBER),
        ("log_level", "info", ConfigType.STRING),
        ("api.rate_limit", 100, ConfigType.NUMBER),
        ("api.timeout_ms", 5000, ConfigType.NUMBER),
    ]
    
    # Development config
    dev_ns = namespaces[EnvironmentType.DEVELOPMENT]
    for key, value, ctype in configs:
        platform.set_config(dev_ns.namespace_id, key, value, ctype, "admin")
        
    print(f"  ✓ Development: {len(configs)} values")
    
    # Production config (different values)
    prod_ns = namespaces[EnvironmentType.PRODUCTION]
    prod_configs = [
        ("database.host", "prod-db.internal", ConfigType.STRING),
        ("database.port", 5432, ConfigType.NUMBER),
        ("database.pool_size", 50, ConfigType.NUMBER),
        ("cache.enabled", True, ConfigType.BOOLEAN),
        ("cache.ttl_seconds", 7200, ConfigType.NUMBER),
        ("log_level", "warning", ConfigType.STRING),
        ("api.rate_limit", 1000, ConfigType.NUMBER),
        ("api.timeout_ms", 3000, ConfigType.NUMBER),
    ]
    
    for key, value, ctype in prod_configs:
        platform.set_config(prod_ns.namespace_id, key, value, ctype, "admin")
        
    print(f"  ✓ Production: {len(prod_configs)} values")
    
    # Set secrets
    print("\n🔐 Setting Secrets...")
    
    secrets = [
        "database.password",
        "api.key",
        "jwt.secret"
    ]
    
    for secret_key in secrets:
        platform.set_config(
            prod_ns.namespace_id, 
            secret_key, 
            f"super_secret_{random.randint(1000, 9999)}",
            ConfigType.SECRET,
            "admin"
        )
        print(f"  ✓ {secret_key}")
        
    # Subscribe to changes
    print("\n👁️ Setting Up Subscriptions...")
    
    sub = platform.subscribe(prod_ns.namespace_id, "http://notifier:8080/config-changed")
    print(f"  ✓ Watching production namespace")
    
    # Display configurations
    print("\n📊 Configuration Overview:")
    
    print("\n  Development Environment:")
    dev_config = platform.get_config(dev_ns.namespace_id)
    for key, value in dev_config.items():
        print(f"    {key}: {value}")
        
    print("\n  Production Environment:")
    prod_config = platform.get_config(prod_ns.namespace_id)
    for key, value in list(prod_config.items())[:8]:
        display_value = value if "encrypted:" not in str(value) else "********"
        print(f"    {key}: {display_value}")
        
    # Configuration comparison
    print("\n🔄 Environment Comparison:")
    
    print("\n  ┌──────────────────────────┬─────────────────┬─────────────────┐")
    print("  │ Config Key               │ Development     │ Production      │")
    print("  ├──────────────────────────┼─────────────────┼─────────────────┤")
    
    for key in ["database.host", "database.pool_size", "cache.ttl_seconds", "log_level", "api.rate_limit"]:
        dev_val = str(platform.get_config(dev_ns.namespace_id, key))[:15].ljust(15)
        prod_val = str(platform.get_config(prod_ns.namespace_id, key))[:15].ljust(15)
        key_str = key[:24].ljust(24)
        print(f"  │ {key_str} │ {dev_val} │ {prod_val} │")
        
    print("  └──────────────────────────┴─────────────────┴─────────────────┘")
    
    # Audit trail
    print("\n📝 Audit Trail (Recent Changes):")
    
    history = platform.audit.get_history(limit=10)
    
    print("\n  ┌──────────────────────────┬──────────┬──────────────────┐")
    print("  │ Key                      │ Action   │ Author           │")
    print("  ├──────────────────────────┼──────────┼──────────────────┤")
    
    for entry in history[:8]:
        key = entry.key[:24].ljust(24)
        action = entry.change_type.value[:8].ljust(8)
        author = entry.author[:16].ljust(16)
        print(f"  │ {key} │ {action} │ {author} │")
        
    print("  └──────────────────────────┴──────────┴──────────────────┘")
    
    # Namespace summary
    print("\n📁 Namespace Summary:")
    
    print("\n  ┌──────────────────────────────┬──────────────┬──────────┬──────────┐")
    print("  │ Namespace                    │ Environment  │ Values   │ Secrets  │")
    print("  ├──────────────────────────────┼──────────────┼──────────┼──────────┤")
    
    for ns in platform.store.namespaces.values():
        name = ns.name[:28].ljust(28)
        env = ns.environment.value[:12].ljust(12)
        values = str(len(ns.values)).center(8)
        secrets_count = len([v for v in ns.values.values() if v.config_type == ConfigType.SECRET])
        secrets_str = str(secrets_count).center(8)
        print(f"  │ {name} │ {env} │ {values} │ {secrets_str} │")
        
    print("  └──────────────────────────────┴──────────────┴──────────┴──────────┘")
    
    # Update configuration
    print("\n🔄 Updating Configuration...")
    
    old_val = platform.get_config(prod_ns.namespace_id, "api.rate_limit")
    platform.set_config(prod_ns.namespace_id, "api.rate_limit", 2000, ConfigType.NUMBER, "ops-team")
    new_val = platform.get_config(prod_ns.namespace_id, "api.rate_limit")
    
    print(f"  api.rate_limit: {old_val} -> {new_val}")
    
    # Config types distribution
    print("\n📊 Config Types Distribution:")
    
    type_counts = {}
    for ns in platform.store.namespaces.values():
        for v in ns.values.values():
            t = v.config_type.value
            type_counts[t] = type_counts.get(t, 0) + 1
            
    for ctype, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * count + "░" * (30 - count)
        print(f"  {ctype:10} [{bar}] {count}")
        
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📈 Platform Statistics:")
    
    print(f"\n  Total Namespaces: {stats['total_namespaces']}")
    print(f"  Total Values: {stats['total_values']}")
    print(f"  Total Secrets: {stats['total_secrets']}")
    print(f"  Audit Entries: {stats['audit_entries']}")
    print(f"  Subscriptions: {stats['subscriptions']}")
    print(f"  Validation Rules: {stats['validation_rules']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Config Management Dashboard                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Namespaces:                    {stats['total_namespaces']:>12}                        │")
    print(f"│ Config Values:                 {stats['total_values']:>12}                        │")
    print(f"│ Secrets:                       {stats['total_secrets']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Audit Entries:                 {stats['audit_entries']:>12}                        │")
    print(f"│ Subscriptions:                 {stats['subscriptions']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Config Management Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
