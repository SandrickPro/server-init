#!/usr/bin/env python3
"""
Server Init - Iteration 54: Configuration Management & Drift Detection
Управление конфигурацией и обнаружение дрифта

Функционал:
- Configuration Store - хранилище конфигураций
- Version Control - контроль версий конфигураций
- Environment Management - управление окружениями
- Configuration Templates - шаблоны конфигураций
- Drift Detection - обнаружение дрифта
- Auto Remediation - автоматическое исправление
- Configuration Validation - валидация конфигураций
- Audit Trail - аудит изменений
"""

import json
import asyncio
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
from abc import ABC, abstractmethod
from collections import defaultdict
import random
import uuid
import copy


class ConfigType(Enum):
    """Тип конфигурации"""
    APPLICATION = "application"
    INFRASTRUCTURE = "infrastructure"
    SECURITY = "security"
    NETWORK = "network"
    DATABASE = "database"
    MONITORING = "monitoring"
    SECRET = "secret"


class Environment(Enum):
    """Окружение"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    DR = "dr"


class DriftStatus(Enum):
    """Статус дрифта"""
    IN_SYNC = "in_sync"
    DRIFTED = "drifted"
    UNKNOWN = "unknown"


class DriftSeverity(Enum):
    """Серьёзность дрифта"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RemediationAction(Enum):
    """Действие исправления"""
    AUTO_FIX = "auto_fix"
    MANUAL = "manual"
    IGNORE = "ignore"
    ROLLBACK = "rollback"


class ValidationResult(Enum):
    """Результат валидации"""
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"


@dataclass
class ConfigItem:
    """Элемент конфигурации"""
    item_id: str
    key: str
    value: Any
    
    # Тип
    config_type: ConfigType = ConfigType.APPLICATION
    
    # Окружение
    environment: Environment = Environment.DEVELOPMENT
    
    # Метаданные
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Версионирование
    version: int = 1
    checksum: str = ""
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Автор
    created_by: str = "system"
    updated_by: str = "system"
    
    # Секрет
    is_secret: bool = False
    
    # Статус
    enabled: bool = True


@dataclass
class ConfigVersion:
    """Версия конфигурации"""
    version_id: str
    item_id: str
    version: int
    
    # Значение
    value: Any = None
    checksum: str = ""
    
    # Изменения
    change_type: str = "update"  # create, update, delete
    changes_summary: str = ""
    
    # Время и автор
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    
    # Комментарий
    comment: str = ""


@dataclass
class ConfigTemplate:
    """Шаблон конфигурации"""
    template_id: str
    name: str
    description: str = ""
    
    # Содержимое
    template: Dict[str, Any] = field(default_factory=dict)
    
    # Переменные
    variables: List[str] = field(default_factory=list)
    defaults: Dict[str, Any] = field(default_factory=dict)
    
    # Валидация
    schema: Optional[Dict[str, Any]] = None
    
    # Тип
    config_type: ConfigType = ConfigType.APPLICATION


@dataclass
class DriftRecord:
    """Запись о дрифте"""
    drift_id: str
    item_id: str
    
    # Значения
    expected_value: Any = None
    actual_value: Any = None
    
    # Тип дрифта
    drift_type: str = ""  # value_change, missing, extra
    
    # Серьёзность
    severity: DriftSeverity = DriftSeverity.MEDIUM
    
    # Статус
    status: DriftStatus = DriftStatus.DRIFTED
    
    # Remediation
    remediation_action: Optional[RemediationAction] = None
    remediated_at: Optional[datetime] = None
    
    # Время
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class ValidationError:
    """Ошибка валидации"""
    error_id: str
    item_id: str
    
    # Ошибка
    field: str = ""
    message: str = ""
    
    # Результат
    result: ValidationResult = ValidationResult.INVALID
    
    # Время
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class AuditEntry:
    """Запись аудита"""
    entry_id: str
    item_id: str
    
    # Действие
    action: str = ""  # create, update, delete, read, remediate
    
    # Детали
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    
    # Автор
    actor: str = "system"
    
    # Время
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Результат
    success: bool = True
    error_message: Optional[str] = None


class ConfigStore:
    """Хранилище конфигураций"""
    
    def __init__(self):
        self.items: Dict[str, ConfigItem] = {}
        self.versions: Dict[str, List[ConfigVersion]] = defaultdict(list)
        self.templates: Dict[str, ConfigTemplate] = {}
        self.audit_log: List[AuditEntry] = []
        
    def _calculate_checksum(self, value: Any) -> str:
        """Расчёт контрольной суммы"""
        return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()[:16]
        
    def _audit(self, item_id: str, action: str, actor: str = "system",
                old_value: Any = None, new_value: Any = None,
                success: bool = True, error: str = None):
        """Добавление записи аудита"""
        entry = AuditEntry(
            entry_id=f"audit_{uuid.uuid4().hex[:8]}",
            item_id=item_id,
            action=action,
            old_value=old_value,
            new_value=new_value,
            actor=actor,
            success=success,
            error_message=error
        )
        self.audit_log.append(entry)
        
    def set(self, key: str, value: Any, config_type: ConfigType = ConfigType.APPLICATION,
             environment: Environment = Environment.DEVELOPMENT,
             actor: str = "system", **kwargs) -> ConfigItem:
        """Установка значения"""
        item_key = f"{environment.value}:{key}"
        
        old_value = None
        if item_key in self.items:
            old_item = self.items[item_key]
            old_value = old_item.value
            
            # Создание новой версии
            version = ConfigVersion(
                version_id=f"ver_{uuid.uuid4().hex[:8]}",
                item_id=old_item.item_id,
                version=old_item.version,
                value=old_value,
                checksum=old_item.checksum,
                change_type="update",
                created_by=actor
            )
            self.versions[old_item.item_id].append(version)
            
            # Обновление
            old_item.value = value
            old_item.version += 1
            old_item.checksum = self._calculate_checksum(value)
            old_item.updated_at = datetime.now()
            old_item.updated_by = actor
            
            item = old_item
        else:
            item = ConfigItem(
                item_id=f"cfg_{uuid.uuid4().hex[:8]}",
                key=key,
                value=value,
                config_type=config_type,
                environment=environment,
                checksum=self._calculate_checksum(value),
                created_by=actor,
                updated_by=actor,
                **kwargs
            )
            self.items[item_key] = item
            
        self._audit(item.item_id, "update" if old_value else "create",
                    actor, old_value, value)
        
        return item
        
    def get(self, key: str, environment: Environment = Environment.DEVELOPMENT,
             default: Any = None) -> Any:
        """Получение значения"""
        item_key = f"{environment.value}:{key}"
        item = self.items.get(item_key)
        
        if item:
            self._audit(item.item_id, "read")
            return item.value
            
        return default
        
    def get_item(self, key: str, environment: Environment = Environment.DEVELOPMENT) -> Optional[ConfigItem]:
        """Получение элемента конфигурации"""
        item_key = f"{environment.value}:{key}"
        return self.items.get(item_key)
        
    def delete(self, key: str, environment: Environment = Environment.DEVELOPMENT,
                actor: str = "system") -> bool:
        """Удаление значения"""
        item_key = f"{environment.value}:{key}"
        
        if item_key in self.items:
            item = self.items[item_key]
            
            # Сохранение версии
            version = ConfigVersion(
                version_id=f"ver_{uuid.uuid4().hex[:8]}",
                item_id=item.item_id,
                version=item.version,
                value=item.value,
                checksum=item.checksum,
                change_type="delete",
                created_by=actor
            )
            self.versions[item.item_id].append(version)
            
            self._audit(item.item_id, "delete", actor, item.value)
            
            del self.items[item_key]
            return True
            
        return False
        
    def list_items(self, environment: Optional[Environment] = None,
                    config_type: Optional[ConfigType] = None) -> List[ConfigItem]:
        """Список элементов"""
        items = list(self.items.values())
        
        if environment:
            items = [i for i in items if i.environment == environment]
            
        if config_type:
            items = [i for i in items if i.config_type == config_type]
            
        return items
        
    def get_history(self, item_id: str) -> List[ConfigVersion]:
        """История версий"""
        return sorted(self.versions.get(item_id, []),
                      key=lambda v: v.version, reverse=True)
        
    def rollback(self, item_id: str, version: int,
                  actor: str = "system") -> Optional[ConfigItem]:
        """Откат к версии"""
        # Поиск элемента
        item = None
        for i in self.items.values():
            if i.item_id == item_id:
                item = i
                break
                
        if not item:
            return None
            
        # Поиск версии
        target_version = None
        for v in self.versions.get(item_id, []):
            if v.version == version:
                target_version = v
                break
                
        if not target_version:
            return None
            
        # Откат
        old_value = item.value
        item.value = target_version.value
        item.version += 1
        item.checksum = self._calculate_checksum(target_version.value)
        item.updated_at = datetime.now()
        item.updated_by = actor
        
        self._audit(item_id, "rollback", actor, old_value, target_version.value)
        
        return item


class TemplateEngine:
    """Движок шаблонов"""
    
    def __init__(self, store: ConfigStore):
        self.store = store
        
    def create_template(self, name: str, template: Dict[str, Any],
                         **kwargs) -> ConfigTemplate:
        """Создание шаблона"""
        # Извлечение переменных из шаблона
        variables = self._extract_variables(template)
        
        tpl = ConfigTemplate(
            template_id=f"tpl_{uuid.uuid4().hex[:8]}",
            name=name,
            template=template,
            variables=variables,
            **kwargs
        )
        
        self.store.templates[tpl.template_id] = tpl
        return tpl
        
    def _extract_variables(self, obj: Any, prefix: str = "") -> List[str]:
        """Извлечение переменных из шаблона"""
        variables = []
        
        if isinstance(obj, str):
            # Поиск ${var} паттернов
            import re
            matches = re.findall(r'\$\{([^}]+)\}', obj)
            variables.extend(matches)
            
        elif isinstance(obj, dict):
            for key, value in obj.items():
                variables.extend(self._extract_variables(value, f"{prefix}.{key}"))
                
        elif isinstance(obj, list):
            for item in obj:
                variables.extend(self._extract_variables(item, prefix))
                
        return list(set(variables))
        
    def render_template(self, template_id: str,
                         variables: Dict[str, Any]) -> Dict[str, Any]:
        """Рендеринг шаблона"""
        template = self.store.templates.get(template_id)
        if not template:
            raise ValueError("Template not found")
            
        # Объединение с defaults
        merged_vars = {**template.defaults, **variables}
        
        return self._substitute_variables(copy.deepcopy(template.template), merged_vars)
        
    def _substitute_variables(self, obj: Any, variables: Dict[str, Any]) -> Any:
        """Подстановка переменных"""
        if isinstance(obj, str):
            import re
            def replacer(match):
                var_name = match.group(1)
                return str(variables.get(var_name, match.group(0)))
                
            return re.sub(r'\$\{([^}]+)\}', replacer, obj)
            
        elif isinstance(obj, dict):
            return {k: self._substitute_variables(v, variables) for k, v in obj.items()}
            
        elif isinstance(obj, list):
            return [self._substitute_variables(item, variables) for item in obj]
            
        return obj
        
    def apply_template(self, template_id: str, environment: Environment,
                        variables: Dict[str, Any], actor: str = "system") -> List[ConfigItem]:
        """Применение шаблона"""
        rendered = self.render_template(template_id, variables)
        template = self.store.templates[template_id]
        
        items = []
        
        for key, value in rendered.items():
            item = self.store.set(
                key=key,
                value=value,
                config_type=template.config_type,
                environment=environment,
                actor=actor
            )
            items.append(item)
            
        return items


class ConfigValidator:
    """Валидатор конфигураций"""
    
    def __init__(self, store: ConfigStore):
        self.store = store
        self.rules: Dict[str, List[Callable]] = defaultdict(list)
        
    def add_rule(self, config_type: ConfigType, rule: Callable):
        """Добавление правила валидации"""
        self.rules[config_type.value].append(rule)
        
    def validate_item(self, item: ConfigItem) -> List[ValidationError]:
        """Валидация элемента"""
        errors = []
        
        # Применение правил
        rules = self.rules.get(item.config_type.value, [])
        
        for rule in rules:
            try:
                result = rule(item)
                if result:
                    errors.append(result)
            except Exception as e:
                errors.append(ValidationError(
                    error_id=f"err_{uuid.uuid4().hex[:8]}",
                    item_id=item.item_id,
                    message=f"Rule execution error: {str(e)}",
                    result=ValidationResult.INVALID
                ))
                
        return errors
        
    def validate_all(self, environment: Optional[Environment] = None) -> Dict[str, List[ValidationError]]:
        """Валидация всех элементов"""
        results = {}
        
        items = self.store.list_items(environment=environment)
        
        for item in items:
            errors = self.validate_item(item)
            if errors:
                results[item.item_id] = errors
                
        return results


class DriftDetector:
    """Детектор дрифта"""
    
    def __init__(self, store: ConfigStore):
        self.store = store
        self.expected_state: Dict[str, Any] = {}
        self.drifts: Dict[str, DriftRecord] = {}
        
    def set_expected_state(self, key: str, environment: Environment, value: Any):
        """Установка ожидаемого состояния"""
        state_key = f"{environment.value}:{key}"
        self.expected_state[state_key] = value
        
    def import_expected_state(self, state: Dict[str, Any], environment: Environment):
        """Импорт ожидаемого состояния"""
        for key, value in state.items():
            self.set_expected_state(key, environment, value)
            
    async def detect_drift(self, environment: Optional[Environment] = None) -> List[DriftRecord]:
        """Обнаружение дрифта"""
        drifts = []
        
        items = self.store.list_items(environment=environment)
        
        for item in items:
            state_key = f"{item.environment.value}:{item.key}"
            
            if state_key in self.expected_state:
                expected = self.expected_state[state_key]
                
                if item.value != expected:
                    drift = DriftRecord(
                        drift_id=f"drift_{uuid.uuid4().hex[:8]}",
                        item_id=item.item_id,
                        expected_value=expected,
                        actual_value=item.value,
                        drift_type="value_change",
                        severity=self._assess_severity(item, expected),
                        status=DriftStatus.DRIFTED
                    )
                    
                    self.drifts[drift.drift_id] = drift
                    drifts.append(drift)
                    
        # Проверка на отсутствующие элементы
        for state_key, expected in self.expected_state.items():
            env_str, key = state_key.split(":", 1)
            environment_val = Environment(env_str)
            
            item = self.store.get_item(key, environment_val)
            
            if not item:
                drift = DriftRecord(
                    drift_id=f"drift_{uuid.uuid4().hex[:8]}",
                    item_id=f"missing_{key}",
                    expected_value=expected,
                    actual_value=None,
                    drift_type="missing",
                    severity=DriftSeverity.HIGH,
                    status=DriftStatus.DRIFTED
                )
                
                self.drifts[drift.drift_id] = drift
                drifts.append(drift)
                
        return drifts
        
    def _assess_severity(self, item: ConfigItem, expected: Any) -> DriftSeverity:
        """Оценка серьёзности дрифта"""
        # Секреты - критический
        if item.is_secret:
            return DriftSeverity.CRITICAL
            
        # Security конфиги - высокий
        if item.config_type == ConfigType.SECURITY:
            return DriftSeverity.HIGH
            
        # Production - высокий
        if item.environment == Environment.PRODUCTION:
            return DriftSeverity.HIGH
            
        return DriftSeverity.MEDIUM
        
    def get_drift_summary(self) -> Dict[str, Any]:
        """Сводка по дрифту"""
        by_severity = defaultdict(int)
        by_type = defaultdict(int)
        
        for drift in self.drifts.values():
            if drift.status == DriftStatus.DRIFTED:
                by_severity[drift.severity.value] += 1
                by_type[drift.drift_type] += 1
                
        return {
            "total_drifts": len([d for d in self.drifts.values() if d.status == DriftStatus.DRIFTED]),
            "by_severity": dict(by_severity),
            "by_type": dict(by_type)
        }


class RemediationEngine:
    """Движок исправлений"""
    
    def __init__(self, store: ConfigStore, detector: DriftDetector):
        self.store = store
        self.detector = detector
        
    async def remediate_drift(self, drift_id: str,
                               action: RemediationAction = RemediationAction.AUTO_FIX,
                               actor: str = "system") -> DriftRecord:
        """Исправление дрифта"""
        drift = self.detector.drifts.get(drift_id)
        if not drift:
            raise ValueError("Drift not found")
            
        if action == RemediationAction.AUTO_FIX:
            # Автоматическое исправление
            if drift.drift_type == "value_change":
                # Поиск элемента
                for item in self.store.items.values():
                    if item.item_id == drift.item_id:
                        # Обновление до ожидаемого значения
                        old_value = item.value
                        item.value = drift.expected_value
                        item.version += 1
                        item.checksum = self.store._calculate_checksum(drift.expected_value)
                        item.updated_at = datetime.now()
                        item.updated_by = actor
                        
                        self.store._audit(item.item_id, "remediate", actor,
                                          old_value, drift.expected_value)
                        break
                        
            elif drift.drift_type == "missing":
                # Создание отсутствующего элемента
                key = drift.item_id.replace("missing_", "")
                self.store.set(key, drift.expected_value, actor=actor)
                
            drift.status = DriftStatus.IN_SYNC
            drift.remediation_action = action
            drift.remediated_at = datetime.now()
            
        elif action == RemediationAction.ROLLBACK:
            # Откат к предыдущей версии
            for item in self.store.items.values():
                if item.item_id == drift.item_id:
                    history = self.store.get_history(item.item_id)
                    if history:
                        self.store.rollback(item.item_id, history[0].version, actor)
                        drift.status = DriftStatus.IN_SYNC
                        drift.remediation_action = action
                        drift.remediated_at = datetime.now()
                    break
                    
        elif action == RemediationAction.IGNORE:
            drift.remediation_action = action
            
        return drift
        
    async def remediate_all(self, severity_threshold: DriftSeverity = DriftSeverity.HIGH,
                             actor: str = "system") -> List[DriftRecord]:
        """Исправление всех дрифтов"""
        severity_order = [DriftSeverity.CRITICAL, DriftSeverity.HIGH, 
                          DriftSeverity.MEDIUM, DriftSeverity.LOW]
        threshold_idx = severity_order.index(severity_threshold)
        
        remediated = []
        
        for drift in self.detector.drifts.values():
            if drift.status != DriftStatus.DRIFTED:
                continue
                
            drift_idx = severity_order.index(drift.severity)
            
            if drift_idx <= threshold_idx:
                await self.remediate_drift(drift.drift_id, RemediationAction.AUTO_FIX, actor)
                remediated.append(drift)
                
        return remediated


class EnvironmentManager:
    """Менеджер окружений"""
    
    def __init__(self, store: ConfigStore):
        self.store = store
        
    def promote_config(self, key: str, from_env: Environment,
                        to_env: Environment, actor: str = "system") -> Optional[ConfigItem]:
        """Продвижение конфигурации между окружениями"""
        source = self.store.get_item(key, from_env)
        if not source:
            return None
            
        return self.store.set(
            key=key,
            value=source.value,
            config_type=source.config_type,
            environment=to_env,
            actor=actor,
            description=source.description,
            tags=source.tags
        )
        
    def compare_environments(self, env1: Environment,
                              env2: Environment) -> Dict[str, Any]:
        """Сравнение окружений"""
        items1 = {i.key: i for i in self.store.list_items(environment=env1)}
        items2 = {i.key: i for i in self.store.list_items(environment=env2)}
        
        all_keys = set(items1.keys()) | set(items2.keys())
        
        differences = []
        only_in_env1 = []
        only_in_env2 = []
        
        for key in all_keys:
            item1 = items1.get(key)
            item2 = items2.get(key)
            
            if item1 and item2:
                if item1.value != item2.value:
                    differences.append({
                        "key": key,
                        f"{env1.value}_value": item1.value,
                        f"{env2.value}_value": item2.value
                    })
            elif item1:
                only_in_env1.append(key)
            else:
                only_in_env2.append(key)
                
        return {
            "env1": env1.value,
            "env2": env2.value,
            "differences": differences,
            f"only_in_{env1.value}": only_in_env1,
            f"only_in_{env2.value}": only_in_env2,
            "total_differences": len(differences) + len(only_in_env1) + len(only_in_env2)
        }
        
    def sync_environments(self, source_env: Environment,
                           target_env: Environment,
                           keys: Optional[List[str]] = None,
                           actor: str = "system") -> List[ConfigItem]:
        """Синхронизация окружений"""
        source_items = self.store.list_items(environment=source_env)
        
        if keys:
            source_items = [i for i in source_items if i.key in keys]
            
        synced = []
        
        for item in source_items:
            synced_item = self.promote_config(item.key, source_env, target_env, actor)
            if synced_item:
                synced.append(synced_item)
                
        return synced


class ConfigManagementPlatform:
    """Платформа управления конфигурациями"""
    
    def __init__(self):
        self.store = ConfigStore()
        self.template_engine = TemplateEngine(self.store)
        self.validator = ConfigValidator(self.store)
        self.drift_detector = DriftDetector(self.store)
        self.remediation_engine = RemediationEngine(self.store, self.drift_detector)
        self.env_manager = EnvironmentManager(self.store)
        
        # Добавление стандартных правил валидации
        self._setup_default_rules()
        
    def _setup_default_rules(self):
        """Настройка правил по умолчанию"""
        # Правило: security конфиги не должны быть пустыми
        def security_not_empty(item: ConfigItem) -> Optional[ValidationError]:
            if item.config_type == ConfigType.SECURITY and not item.value:
                return ValidationError(
                    error_id=f"err_{uuid.uuid4().hex[:8]}",
                    item_id=item.item_id,
                    field="value",
                    message="Security configuration cannot be empty",
                    result=ValidationResult.INVALID
                )
            return None
            
        self.validator.add_rule(ConfigType.SECURITY, security_not_empty)
        
    def get_status(self) -> Dict[str, Any]:
        """Статус платформы"""
        return {
            "items": len(self.store.items),
            "templates": len(self.store.templates),
            "versions": sum(len(v) for v in self.store.versions.values()),
            "audit_entries": len(self.store.audit_log),
            "drift": self.drift_detector.get_drift_summary()
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 54: Configuration Management")
    print("=" * 60)
    
    async def demo():
        # Создание платформы
        platform = ConfigManagementPlatform()
        print("✓ Configuration Management Platform created")
        
        # Добавление конфигураций
        print("\n⚙️ Setting configurations...")
        
        configs = [
            ("app.name", "MyApplication", ConfigType.APPLICATION),
            ("app.version", "2.1.0", ConfigType.APPLICATION),
            ("app.port", 8080, ConfigType.APPLICATION),
            ("db.host", "localhost", ConfigType.DATABASE),
            ("db.port", 5432, ConfigType.DATABASE),
            ("db.max_connections", 100, ConfigType.DATABASE),
            ("security.ssl_enabled", True, ConfigType.SECURITY),
            ("security.min_tls_version", "1.2", ConfigType.SECURITY),
            ("monitoring.metrics_enabled", True, ConfigType.MONITORING)
        ]
        
        for key, value, config_type in configs:
            platform.store.set(key, value, config_type, Environment.DEVELOPMENT, actor="admin")
            print(f"  ✓ {key} = {value}")
            
        # Обновление конфигурации
        print("\n📝 Updating configuration...")
        platform.store.set("app.version", "2.2.0", Environment.DEVELOPMENT, actor="deploy-bot")
        print("  ✓ Updated app.version to 2.2.0")
        
        # История версий
        print("\n📜 Version history for app.version:")
        item = platform.store.get_item("app.version", Environment.DEVELOPMENT)
        history = platform.store.get_history(item.item_id)
        
        for ver in history:
            print(f"  v{ver.version}: {ver.value} ({ver.change_type}) by {ver.created_by}")
            
        # Шаблоны
        print("\n📋 Creating configuration template...")
        
        template = platform.template_engine.create_template(
            name="microservice-config",
            template={
                "service.name": "${service_name}",
                "service.port": "${port}",
                "service.replicas": "${replicas}",
                "service.health_check": "/health",
                "logging.level": "${log_level}"
            },
            defaults={"log_level": "INFO", "replicas": 3},
            config_type=ConfigType.APPLICATION
        )
        print(f"  ✓ Created template: {template.name}")
        print(f"    Variables: {template.variables}")
        
        # Применение шаблона
        print("\n🔧 Applying template...")
        
        items = platform.template_engine.apply_template(
            template.template_id,
            Environment.STAGING,
            variables={"service_name": "order-service", "port": 8090},
            actor="platform"
        )
        
        for item in items:
            print(f"  ✓ {item.key} = {item.value}")
            
        # Продвижение конфигураций
        print("\n🚀 Promoting configurations to production...")
        
        # Сначала в staging
        for key, value, config_type in configs[:3]:
            platform.store.set(key, value, config_type, Environment.STAGING, actor="admin")
            
        # Сравнение окружений
        print("\n🔍 Comparing environments...")
        comparison = platform.env_manager.compare_environments(
            Environment.DEVELOPMENT,
            Environment.STAGING
        )
        
        print(f"  Differences: {len(comparison['differences'])}")
        print(f"  Only in dev: {len(comparison['only_in_development'])}")
        print(f"  Only in staging: {len(comparison['only_in_staging'])}")
        
        # Синхронизация
        print("\n🔄 Syncing staging to production...")
        synced = platform.env_manager.sync_environments(
            Environment.STAGING,
            Environment.PRODUCTION,
            actor="deploy-bot"
        )
        print(f"  ✓ Synced {len(synced)} items")
        
        # Drift detection
        print("\n🔎 Setting up drift detection...")
        
        # Установка ожидаемого состояния
        expected_state = {
            "app.version": "2.2.0",
            "app.port": 8080,
            "db.max_connections": 100,
            "security.ssl_enabled": True
        }
        
        platform.drift_detector.import_expected_state(expected_state, Environment.DEVELOPMENT)
        
        # Создание дрифта (изменение значения)
        platform.store.set("db.max_connections", 50, ConfigType.DATABASE, 
                          Environment.DEVELOPMENT, actor="someone")
        
        # Обнаружение дрифта
        print("\n⚠️ Detecting drift...")
        drifts = await platform.drift_detector.detect_drift(Environment.DEVELOPMENT)
        
        for drift in drifts:
            print(f"  {drift.severity.value.upper()}: {drift.drift_type}")
            print(f"    Expected: {drift.expected_value}")
            print(f"    Actual: {drift.actual_value}")
            
        # Drift summary
        summary = platform.drift_detector.get_drift_summary()
        print(f"\n  Drift summary:")
        print(f"    Total: {summary['total_drifts']}")
        print(f"    By severity: {summary['by_severity']}")
        
        # Remediation
        print("\n🔧 Remediating drifts...")
        
        if drifts:
            for drift in drifts:
                remediated = await platform.remediation_engine.remediate_drift(
                    drift.drift_id,
                    RemediationAction.AUTO_FIX,
                    actor="drift-bot"
                )
                print(f"  ✓ Remediated: {remediated.item_id} -> {remediated.status.value}")
                
        # Валидация
        print("\n✅ Validating configurations...")
        
        # Добавление пустого security конфига для теста
        platform.store.set("security.empty_test", "", ConfigType.SECURITY,
                          Environment.DEVELOPMENT)
        
        errors = platform.validator.validate_all(Environment.DEVELOPMENT)
        
        if errors:
            for item_id, item_errors in errors.items():
                for err in item_errors:
                    print(f"  ⚠️ {err.result.value}: {err.message}")
        else:
            print("  ✓ All configurations valid")
            
        # Аудит
        print("\n📊 Recent audit entries:")
        
        for entry in platform.store.audit_log[-5:]:
            print(f"  {entry.timestamp.strftime('%H:%M:%S')} - {entry.action} by {entry.actor}")
            
        # Rollback
        print("\n⏪ Rolling back configuration...")
        
        item = platform.store.get_item("app.version", Environment.DEVELOPMENT)
        history = platform.store.get_history(item.item_id)
        
        if history:
            rolled_back = platform.store.rollback(item.item_id, history[0].version, "admin")
            print(f"  ✓ Rolled back app.version to {rolled_back.value}")
            
        # Статус платформы
        print("\n📊 Platform Status:")
        status = platform.get_status()
        print(f"  Items: {status['items']}")
        print(f"  Templates: {status['templates']}")
        print(f"  Versions: {status['versions']}")
        print(f"  Audit entries: {status['audit_entries']}")
        print(f"  Active drifts: {status['drift']['total_drifts']}")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Configuration Management Platform initialized!")
    print("=" * 60)
