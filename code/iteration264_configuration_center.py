#!/usr/bin/env python3
"""
Server Init - Iteration 264: Configuration Center Platform
Платформа центра конфигурации

Функционал:
- Configuration Storage - хранилище конфигураций
- Environment Management - управление окружениями
- Version Control - версионирование
- Secret Management - управление секретами
- Dynamic Updates - динамические обновления
- Configuration Templates - шаблоны конфигураций
- Validation Rules - правила валидации
- Change Notifications - уведомления об изменениях
"""

import asyncio
import random
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
import uuid
import json
import hashlib


class ConfigType(Enum):
    """Тип конфигурации"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"
    SECRET = "secret"


class Environment(Enum):
    """Окружение"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class ChangeType(Enum):
    """Тип изменения"""
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    ROLLED_BACK = "rolled_back"


class ValidationRuleType(Enum):
    """Тип правила валидации"""
    REQUIRED = "required"
    MIN_VALUE = "min_value"
    MAX_VALUE = "max_value"
    PATTERN = "pattern"
    ENUM = "enum"
    CUSTOM = "custom"


@dataclass
class ValidationRule:
    """Правило валидации"""
    rule_id: str
    rule_type: ValidationRuleType
    
    # Parameters
    value: Any = None  # min/max value, pattern, enum values
    message: str = ""  # error message
    
    # Custom validator
    validator: Optional[Callable[[Any], bool]] = None


@dataclass
class ConfigValue:
    """Значение конфигурации"""
    value_id: str
    
    # Value
    value: Any = None
    encrypted_value: Optional[str] = None  # for secrets
    
    # Type
    config_type: ConfigType = ConfigType.STRING
    
    # Environment
    environment: Environment = Environment.DEVELOPMENT
    
    # Version
    version: int = 1
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""


@dataclass
class ConfigItem:
    """Элемент конфигурации"""
    item_id: str
    key: str  # unique key like "database.host"
    name: str
    
    # Type
    config_type: ConfigType = ConfigType.STRING
    
    # Default value
    default_value: Any = None
    
    # Environment values
    values: Dict[Environment, ConfigValue] = field(default_factory=dict)
    
    # Validation
    validation_rules: List[ValidationRule] = field(default_factory=list)
    
    # Metadata
    description: str = ""
    tags: List[str] = field(default_factory=list)
    
    # History
    history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ConfigNamespace:
    """Пространство имён конфигурации"""
    namespace_id: str
    name: str  # e.g., "database", "api", "cache"
    
    # Items
    items: Dict[str, ConfigItem] = field(default_factory=dict)
    
    # Metadata
    description: str = ""
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ConfigTemplate:
    """Шаблон конфигурации"""
    template_id: str
    name: str
    
    # Template items
    items: List[Dict[str, Any]] = field(default_factory=list)
    
    # Description
    description: str = ""


@dataclass
class ConfigChange:
    """Изменение конфигурации"""
    change_id: str
    item_key: str
    
    # Change type
    change_type: ChangeType = ChangeType.UPDATED
    
    # Values
    old_value: Any = None
    new_value: Any = None
    
    # Environment
    environment: Environment = Environment.DEVELOPMENT
    
    # User
    changed_by: str = ""
    
    # Timing
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ConfigSubscription:
    """Подписка на изменения"""
    subscription_id: str
    
    # Filter
    key_pattern: str = "*"  # glob pattern
    environments: Set[Environment] = field(default_factory=set)
    
    # Callback
    callback: Optional[Callable[[ConfigChange], None]] = None
    
    # Status
    active: bool = True


class ConfigCenterManager:
    """Менеджер центра конфигурации"""
    
    def __init__(self):
        self.namespaces: Dict[str, ConfigNamespace] = {}
        self.templates: Dict[str, ConfigTemplate] = {}
        self.changes: List[ConfigChange] = []
        self.subscriptions: List[ConfigSubscription] = []
        self.current_environment: Environment = Environment.DEVELOPMENT
        
    def create_namespace(self, name: str, description: str = "") -> ConfigNamespace:
        """Создание пространства имён"""
        namespace = ConfigNamespace(
            namespace_id=f"ns_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description
        )
        
        self.namespaces[name] = namespace
        return namespace
        
    def _get_full_key(self, namespace: str, key: str) -> str:
        """Получение полного ключа"""
        return f"{namespace}.{key}"
        
    def _validate_value(self, item: ConfigItem, value: Any) -> List[str]:
        """Валидация значения"""
        errors = []
        
        for rule in item.validation_rules:
            if rule.rule_type == ValidationRuleType.REQUIRED:
                if value is None or value == "":
                    errors.append(rule.message or "Value is required")
                    
            elif rule.rule_type == ValidationRuleType.MIN_VALUE:
                try:
                    if float(value) < float(rule.value):
                        errors.append(rule.message or f"Value must be >= {rule.value}")
                except (ValueError, TypeError):
                    pass
                    
            elif rule.rule_type == ValidationRuleType.MAX_VALUE:
                try:
                    if float(value) > float(rule.value):
                        errors.append(rule.message or f"Value must be <= {rule.value}")
                except (ValueError, TypeError):
                    pass
                    
            elif rule.rule_type == ValidationRuleType.PATTERN:
                import re
                if not re.match(rule.value, str(value)):
                    errors.append(rule.message or f"Value must match pattern {rule.value}")
                    
            elif rule.rule_type == ValidationRuleType.ENUM:
                if value not in rule.value:
                    errors.append(rule.message or f"Value must be one of {rule.value}")
                    
            elif rule.rule_type == ValidationRuleType.CUSTOM:
                if rule.validator and not rule.validator(value):
                    errors.append(rule.message or "Custom validation failed")
                    
        return errors
        
    def _encrypt_secret(self, value: str) -> str:
        """Шифрование секрета (симуляция)"""
        return f"enc:{hashlib.sha256(value.encode()).hexdigest()[:32]}"
        
    def _notify_subscribers(self, change: ConfigChange):
        """Уведомление подписчиков"""
        for sub in self.subscriptions:
            if not sub.active:
                continue
                
            # Check environment filter
            if sub.environments and change.environment not in sub.environments:
                continue
                
            # Check key pattern (simple glob)
            if sub.key_pattern != "*":
                if not change.item_key.startswith(sub.key_pattern.replace("*", "")):
                    continue
                    
            if sub.callback:
                try:
                    sub.callback(change)
                except Exception:
                    pass
                    
    def set_config(self, namespace: str, key: str, value: Any,
                  environment: Environment = None,
                  config_type: ConfigType = ConfigType.STRING,
                  changed_by: str = "system") -> bool:
        """Установка значения конфигурации"""
        environment = environment or self.current_environment
        
        ns = self.namespaces.get(namespace)
        if not ns:
            ns = self.create_namespace(namespace)
            
        full_key = self._get_full_key(namespace, key)
        
        # Get or create item
        if key not in ns.items:
            item = ConfigItem(
                item_id=f"cfg_{uuid.uuid4().hex[:8]}",
                key=full_key,
                name=key,
                config_type=config_type,
                default_value=value
            )
            ns.items[key] = item
            change_type = ChangeType.CREATED
        else:
            item = ns.items[key]
            change_type = ChangeType.UPDATED
            
        # Validate
        errors = self._validate_value(item, value)
        if errors:
            return False
            
        # Store old value for change record
        old_value = None
        if environment in item.values:
            old_value = item.values[environment].value
            
        # Create value
        config_value = ConfigValue(
            value_id=f"val_{uuid.uuid4().hex[:8]}",
            value=value if config_type != ConfigType.SECRET else None,
            encrypted_value=self._encrypt_secret(str(value)) if config_type == ConfigType.SECRET else None,
            config_type=config_type,
            environment=environment,
            version=(item.values[environment].version + 1) if environment in item.values else 1,
            created_by=changed_by
        )
        
        item.values[environment] = config_value
        item.updated_at = datetime.now()
        
        # Record history
        item.history.append({
            "version": config_value.version,
            "value": value if config_type != ConfigType.SECRET else "***",
            "environment": environment.value,
            "changed_by": changed_by,
            "timestamp": datetime.now()
        })
        
        # Record change
        change = ConfigChange(
            change_id=f"chg_{uuid.uuid4().hex[:8]}",
            item_key=full_key,
            change_type=change_type,
            old_value=old_value,
            new_value=value if config_type != ConfigType.SECRET else "***",
            environment=environment,
            changed_by=changed_by
        )
        self.changes.append(change)
        
        # Notify subscribers
        self._notify_subscribers(change)
        
        return True
        
    def get_config(self, namespace: str, key: str,
                  environment: Environment = None,
                  default: Any = None) -> Any:
        """Получение значения конфигурации"""
        environment = environment or self.current_environment
        
        ns = self.namespaces.get(namespace)
        if not ns:
            return default
            
        item = ns.items.get(key)
        if not item:
            return default
            
        if environment in item.values:
            return item.values[environment].value
            
        return item.default_value if item.default_value is not None else default
        
    def delete_config(self, namespace: str, key: str,
                     environment: Environment = None,
                     changed_by: str = "system") -> bool:
        """Удаление конфигурации"""
        environment = environment or self.current_environment
        
        ns = self.namespaces.get(namespace)
        if not ns or key not in ns.items:
            return False
            
        item = ns.items[key]
        old_value = item.values.get(environment)
        
        if environment in item.values:
            del item.values[environment]
            
        # Record change
        change = ConfigChange(
            change_id=f"chg_{uuid.uuid4().hex[:8]}",
            item_key=self._get_full_key(namespace, key),
            change_type=ChangeType.DELETED,
            old_value=old_value.value if old_value else None,
            environment=environment,
            changed_by=changed_by
        )
        self.changes.append(change)
        
        return True
        
    def add_validation_rule(self, namespace: str, key: str,
                           rule_type: ValidationRuleType,
                           value: Any = None,
                           message: str = "") -> bool:
        """Добавление правила валидации"""
        ns = self.namespaces.get(namespace)
        if not ns or key not in ns.items:
            return False
            
        rule = ValidationRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            rule_type=rule_type,
            value=value,
            message=message
        )
        
        ns.items[key].validation_rules.append(rule)
        return True
        
    def subscribe(self, key_pattern: str = "*",
                 environments: Set[Environment] = None,
                 callback: Callable[[ConfigChange], None] = None) -> ConfigSubscription:
        """Подписка на изменения"""
        subscription = ConfigSubscription(
            subscription_id=f"sub_{uuid.uuid4().hex[:8]}",
            key_pattern=key_pattern,
            environments=environments or set(),
            callback=callback
        )
        
        self.subscriptions.append(subscription)
        return subscription
        
    def unsubscribe(self, subscription_id: str):
        """Отписка"""
        self.subscriptions = [s for s in self.subscriptions if s.subscription_id != subscription_id]
        
    def rollback(self, namespace: str, key: str, version: int,
                environment: Environment = None,
                changed_by: str = "system") -> bool:
        """Откат к версии"""
        environment = environment or self.current_environment
        
        ns = self.namespaces.get(namespace)
        if not ns or key not in ns.items:
            return False
            
        item = ns.items[key]
        
        # Find version in history
        history_entry = None
        for entry in item.history:
            if entry["version"] == version and entry["environment"] == environment.value:
                history_entry = entry
                break
                
        if not history_entry:
            return False
            
        # Set the old value
        return self.set_config(namespace, key, history_entry["value"], 
                              environment, item.config_type, changed_by)
        
    def get_all_configs(self, environment: Environment = None) -> Dict[str, Any]:
        """Получение всех конфигураций"""
        environment = environment or self.current_environment
        configs = {}
        
        for ns_name, ns in self.namespaces.items():
            for key, item in ns.items.items():
                full_key = self._get_full_key(ns_name, key)
                if environment in item.values:
                    configs[full_key] = item.values[environment].value
                elif item.default_value is not None:
                    configs[full_key] = item.default_value
                    
        return configs
        
    def export_config(self, environment: Environment = None) -> str:
        """Экспорт конфигурации в JSON"""
        return json.dumps(self.get_all_configs(environment), indent=2)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_items = sum(len(ns.items) for ns in self.namespaces.values())
        total_values = sum(
            sum(len(item.values) for item in ns.items.values())
            for ns in self.namespaces.values()
        )
        
        types = {t: 0 for t in ConfigType}
        for ns in self.namespaces.values():
            for item in ns.items.values():
                types[item.config_type] += 1
                
        return {
            "namespaces_total": len(self.namespaces),
            "items_total": total_items,
            "values_total": total_values,
            "changes_total": len(self.changes),
            "subscriptions_active": sum(1 for s in self.subscriptions if s.active),
            "types": {t.value: c for t, c in types.items()}
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 264: Configuration Center Platform")
    print("=" * 60)
    
    manager = ConfigCenterManager()
    print("✓ Config Center Manager created")
    
    # Create namespaces
    print("\n📁 Creating Namespaces...")
    
    namespaces_data = [
        ("database", "Database configuration"),
        ("api", "API settings"),
        ("cache", "Cache configuration"),
        ("security", "Security settings"),
    ]
    
    for name, desc in namespaces_data:
        ns = manager.create_namespace(name, desc)
        print(f"  📁 {name}: {desc}")
        
    # Set configurations
    print("\n⚙️ Setting Configurations...")
    
    # Database configs
    configs = [
        ("database", "host", "localhost", ConfigType.STRING),
        ("database", "port", 5432, ConfigType.INTEGER),
        ("database", "name", "app_db", ConfigType.STRING),
        ("database", "max_connections", 100, ConfigType.INTEGER),
        ("database", "password", "secret123", ConfigType.SECRET),
        ("api", "base_url", "https://api.example.com", ConfigType.STRING),
        ("api", "timeout", 30, ConfigType.INTEGER),
        ("api", "rate_limit", 1000, ConfigType.INTEGER),
        ("cache", "enabled", True, ConfigType.BOOLEAN),
        ("cache", "ttl", 3600, ConfigType.INTEGER),
        ("security", "jwt_secret", "jwt-secret-key", ConfigType.SECRET),
        ("security", "session_timeout", 1800, ConfigType.INTEGER),
    ]
    
    for namespace, key, value, config_type in configs:
        manager.set_config(namespace, key, value, config_type=config_type)
        display_value = "***" if config_type == ConfigType.SECRET else value
        print(f"  ⚙️ {namespace}.{key} = {display_value}")
        
    # Add validation rules
    print("\n✅ Adding Validation Rules...")
    
    manager.add_validation_rule("database", "port", ValidationRuleType.MIN_VALUE, 1, "Port must be >= 1")
    manager.add_validation_rule("database", "port", ValidationRuleType.MAX_VALUE, 65535, "Port must be <= 65535")
    manager.add_validation_rule("database", "max_connections", ValidationRuleType.MIN_VALUE, 1)
    manager.add_validation_rule("api", "timeout", ValidationRuleType.MIN_VALUE, 1)
    print("  ✅ Validation rules added")
    
    # Set environment-specific values
    print("\n🌍 Setting Environment-Specific Values...")
    
    env_configs = [
        ("database", "host", "staging-db.example.com", Environment.STAGING),
        ("database", "host", "prod-db.example.com", Environment.PRODUCTION),
        ("api", "base_url", "https://staging-api.example.com", Environment.STAGING),
        ("api", "base_url", "https://prod-api.example.com", Environment.PRODUCTION),
    ]
    
    for namespace, key, value, env in env_configs:
        manager.set_config(namespace, key, value, env)
        print(f"  🌍 {env.value}: {namespace}.{key} = {value}")
        
    # Subscribe to changes
    print("\n📬 Setting Up Subscriptions...")
    
    change_log = []
    
    def on_change(change: ConfigChange):
        change_log.append(change)
        
    sub = manager.subscribe("database.*", callback=on_change)
    print(f"  📬 Subscribed to database.* changes")
    
    # Make some changes
    manager.set_config("database", "max_connections", 200)
    manager.set_config("database", "port", 5433)
    
    print(f"  📬 Received {len(change_log)} change notifications")
    
    # Display configurations
    print("\n📋 Configuration Items:")
    
    print("\n  ┌─────────────────────────┬───────────┬────────────────────┬──────────┬──────────┐")
    print("  │ Key                     │ Type      │ Value (dev)        │ Version  │ Rules    │")
    print("  ├─────────────────────────┼───────────┼────────────────────┼──────────┼──────────┤")
    
    for ns_name, ns in manager.namespaces.items():
        for key, item in ns.items.items():
            full_key = f"{ns_name}.{key}"[:23].ljust(23)
            config_type = item.config_type.value[:9].ljust(9)
            
            dev_value = item.values.get(Environment.DEVELOPMENT)
            if dev_value:
                value = str(dev_value.value) if item.config_type != ConfigType.SECRET else "***"
                version = str(dev_value.version)
            else:
                value = str(item.default_value)
                version = "0"
                
            value = value[:18].ljust(18)
            version = version[:8].ljust(8)
            rules = str(len(item.validation_rules))[:8].ljust(8)
            
            print(f"  │ {full_key} │ {config_type} │ {value} │ {version} │ {rules} │")
            
    print("  └─────────────────────────┴───────────┴────────────────────┴──────────┴──────────┘")
    
    # Environment comparison
    print("\n🌍 Environment Comparison (database.host):")
    
    for env in Environment:
        value = manager.get_config("database", "host", env)
        if value:
            print(f"  {env.value:12s}: {value}")
            
    # Change history
    print("\n📜 Recent Changes:")
    
    for change in manager.changes[-8:]:
        print(f"  [{change.timestamp.strftime('%H:%M:%S')}] {change.item_key}: {change.change_type.value}")
        
    # Export config
    print("\n📤 Exported Configuration (development):")
    
    exported = manager.get_all_configs(Environment.DEVELOPMENT)
    for key in list(exported.keys())[:5]:
        value = exported[key]
        print(f"  {key}: {value}")
    print("  ...")
    
    # Namespace summary
    print("\n📁 Namespace Summary:")
    
    for ns_name, ns in manager.namespaces.items():
        print(f"  {ns_name}: {len(ns.items)} items")
        
    # Type distribution
    print("\n📊 Type Distribution:")
    
    for config_type in ConfigType:
        count = sum(
            1 for ns in manager.namespaces.values()
            for item in ns.items.values()
            if item.config_type == config_type
        )
        if count > 0:
            bar = "█" * count + "░" * (10 - count)
            print(f"  {config_type.value:8s} [{bar}] {count}")
            
    # Statistics
    print("\n📊 Manager Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Namespaces: {stats['namespaces_total']}")
    print(f"  Items: {stats['items_total']}")
    print(f"  Values: {stats['values_total']}")
    print(f"  Changes: {stats['changes_total']}")
    print(f"  Active Subscriptions: {stats['subscriptions_active']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Configuration Center Dashboard                    │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Namespaces:                    {stats['namespaces_total']:>12}                        │")
    print(f"│ Config Items:                  {stats['items_total']:>12}                        │")
    print(f"│ Total Values:                  {stats['values_total']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Changes:                 {stats['changes_total']:>12}                        │")
    print(f"│ Active Subscriptions:          {stats['subscriptions_active']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Configuration Center Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
