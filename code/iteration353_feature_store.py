#!/usr/bin/env python3
"""
Server Init - Iteration 353: Feature Store Platform
Платформа хранилища признаков для ML

Функционал:
- Feature Registry - реестр признаков
- Feature Groups - группы признаков
- Feature Serving - обслуживание признаков
- Feature Versioning - версионирование признаков
- Feature Monitoring - мониторинг признаков
- Online/Offline Store - онлайн/оффлайн хранилища
- Feature Validation - валидация признаков
- Feature Transformation - трансформации признаков
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import json


class FeatureType(Enum):
    """Тип признака"""
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "boolean"
    ARRAY = "array"
    STRUCT = "struct"
    TIMESTAMP = "timestamp"
    EMBEDDING = "embedding"


class StoreType(Enum):
    """Тип хранилища"""
    ONLINE = "online"
    OFFLINE = "offline"
    BOTH = "both"


class SourceType(Enum):
    """Тип источника"""
    BATCH = "batch"
    STREAM = "stream"
    ON_DEMAND = "on_demand"


class TransformationType(Enum):
    """Тип трансформации"""
    AGGREGATION = "aggregation"
    DERIVED = "derived"
    PASSTHROUGH = "passthrough"
    CUSTOM = "custom"


class FeatureStatus(Enum):
    """Статус признака"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"
    ARCHIVED = "archived"


class ValidationStatus(Enum):
    """Статус валидации"""
    VALID = "valid"
    WARNING = "warning"
    FAILED = "failed"


class MonitoringAlertType(Enum):
    """Тип алерта мониторинга"""
    DATA_DRIFT = "data_drift"
    NULL_RATE = "null_rate"
    VALUE_RANGE = "value_range"
    FRESHNESS = "freshness"
    CARDINALITY = "cardinality"


@dataclass
class Entity:
    """Сущность"""
    entity_id: str
    name: str
    
    # Join keys
    join_keys: List[str] = field(default_factory=list)
    value_type: FeatureType = FeatureType.STRING
    
    # Description
    description: str = ""
    
    # Owner
    owner: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class FeatureDefinition:
    """Определение признака"""
    feature_id: str
    name: str
    group_id: str
    
    # Type
    feature_type: FeatureType = FeatureType.FLOAT
    
    # Source
    source_type: SourceType = SourceType.BATCH
    
    # Store
    store_type: StoreType = StoreType.BOTH
    
    # Status
    status: FeatureStatus = FeatureStatus.ACTIVE
    
    # Description
    description: str = ""
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Default value
    default_value: Any = None
    
    # Validation
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: List[Any] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


@dataclass
class FeatureGroup:
    """Группа признаков"""
    group_id: str
    name: str
    
    # Entity
    entity_id: str = ""
    
    # Features
    feature_ids: List[str] = field(default_factory=list)
    
    # Source
    source_type: SourceType = SourceType.BATCH
    source_config: Dict[str, Any] = field(default_factory=dict)
    
    # Store
    online_store_id: str = ""
    offline_store_id: str = ""
    
    # TTL
    online_ttl_days: int = 7
    offline_ttl_days: int = 365
    
    # Status
    status: FeatureStatus = FeatureStatus.ACTIVE
    
    # Description
    description: str = ""
    
    # Owner
    owner: str = ""
    team: str = ""
    
    # Version
    version: int = 1
    
    # Stats
    feature_count: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


@dataclass
class FeatureTransformation:
    """Трансформация признака"""
    transform_id: str
    name: str
    feature_id: str
    
    # Type
    transformation_type: TransformationType = TransformationType.DERIVED
    
    # Expression
    expression: str = ""
    
    # Input features
    input_feature_ids: List[str] = field(default_factory=list)
    
    # Parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class FeatureVersion:
    """Версия признака"""
    version_id: str
    feature_id: str
    version: int = 1
    
    # Schema
    feature_type: FeatureType = FeatureType.FLOAT
    
    # Description
    change_description: str = ""
    
    # Is current
    is_current: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class OnlineStore:
    """Онлайн хранилище"""
    store_id: str
    name: str
    
    # Type
    store_type: str = "redis"  # redis, dynamodb, bigtable
    
    # Connection
    connection_string: str = ""
    
    # Config
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Stats
    key_count: int = 0
    size_bytes: int = 0
    
    # Latency
    avg_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class OfflineStore:
    """Оффлайн хранилище"""
    store_id: str
    name: str
    
    # Type
    store_type: str = "parquet"  # parquet, delta, bigquery
    
    # Location
    path: str = ""
    
    # Config
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Stats
    row_count: int = 0
    size_bytes: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class FeatureView:
    """Представление признаков"""
    view_id: str
    name: str
    
    # Feature groups
    group_ids: List[str] = field(default_factory=list)
    
    # Features
    feature_ids: List[str] = field(default_factory=list)
    
    # Entity
    entity_id: str = ""
    
    # Filter
    filter_expression: str = ""
    
    # TTL
    ttl_days: int = 7
    
    # Description
    description: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class FeatureRequest:
    """Запрос признаков"""
    request_id: str
    feature_ids: List[str]
    entity_keys: Dict[str, Any]
    
    # Request type
    request_type: str = "online"  # online, offline, training
    
    # Timestamps
    requested_at: datetime = field(default_factory=datetime.now)
    responded_at: Optional[datetime] = None
    
    # Latency
    latency_ms: float = 0.0
    
    # Status
    success: bool = True


@dataclass
class FeatureValue:
    """Значение признака"""
    value_id: str
    feature_id: str
    entity_key: str
    
    # Value
    value: Any = None
    
    # Timestamp
    event_timestamp: datetime = field(default_factory=datetime.now)
    ingestion_timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ValidationRule:
    """Правило валидации"""
    rule_id: str
    name: str
    feature_id: str
    
    # Rule type
    rule_type: str = ""  # range, not_null, regex, custom
    
    # Expression
    expression: str = ""
    
    # Threshold
    threshold: float = 100.0
    
    # Status
    is_enabled: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ValidationResult:
    """Результат валидации"""
    result_id: str
    rule_id: str
    feature_id: str
    
    # Results
    total_values: int = 0
    valid_values: int = 0
    invalid_values: int = 0
    
    # Status
    status: ValidationStatus = ValidationStatus.VALID
    
    # Timestamps
    validated_at: datetime = field(default_factory=datetime.now)


@dataclass
class FeatureMonitoringConfig:
    """Конфигурация мониторинга"""
    config_id: str
    feature_id: str
    
    # Checks
    check_drift: bool = True
    check_null_rate: bool = True
    check_value_range: bool = True
    check_freshness: bool = True
    
    # Thresholds
    drift_threshold: float = 0.1
    null_rate_threshold: float = 5.0
    freshness_hours: int = 24
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class MonitoringAlert:
    """Алерт мониторинга"""
    alert_id: str
    feature_id: str
    
    # Alert type
    alert_type: MonitoringAlertType = MonitoringAlertType.DATA_DRIFT
    
    # Details
    message: str = ""
    current_value: float = 0.0
    threshold: float = 0.0
    
    # Status
    is_resolved: bool = False
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


@dataclass
class FeatureStatistics:
    """Статистика признака"""
    stats_id: str
    feature_id: str
    
    # Basic stats
    count: int = 0
    null_count: int = 0
    null_rate: float = 0.0
    
    # Numeric stats
    mean: float = 0.0
    std: float = 0.0
    min_value: float = 0.0
    max_value: float = 0.0
    median: float = 0.0
    
    # Distribution
    percentiles: Dict[str, float] = field(default_factory=dict)
    
    # Timestamps
    computed_at: datetime = field(default_factory=datetime.now)


@dataclass
class FeatureStoreMetrics:
    """Метрики хранилища признаков"""
    metrics_id: str
    
    # Serving
    online_requests: int = 0
    offline_requests: int = 0
    avg_latency_ms: float = 0.0
    
    # Storage
    online_keys: int = 0
    offline_rows: int = 0
    
    # Features
    active_features: int = 0
    active_groups: int = 0
    
    # Alerts
    active_alerts: int = 0
    
    # Timestamps
    collected_at: datetime = field(default_factory=datetime.now)


class FeatureStorePlatform:
    """Платформа хранилища признаков"""
    
    def __init__(self, project: str = "ml-platform"):
        self.project = project
        self.entities: Dict[str, Entity] = {}
        self.features: Dict[str, FeatureDefinition] = {}
        self.groups: Dict[str, FeatureGroup] = {}
        self.transformations: Dict[str, FeatureTransformation] = {}
        self.versions: Dict[str, FeatureVersion] = {}
        self.online_stores: Dict[str, OnlineStore] = {}
        self.offline_stores: Dict[str, OfflineStore] = {}
        self.views: Dict[str, FeatureView] = {}
        self.requests: Dict[str, FeatureRequest] = {}
        self.validation_rules: Dict[str, ValidationRule] = {}
        self.validation_results: Dict[str, ValidationResult] = {}
        self.monitoring_configs: Dict[str, FeatureMonitoringConfig] = {}
        self.alerts: Dict[str, MonitoringAlert] = {}
        self.statistics: Dict[str, FeatureStatistics] = {}
        self.metrics: Dict[str, FeatureStoreMetrics] = {}
        
    async def register_entity(self, name: str,
                             join_keys: List[str],
                             value_type: FeatureType = FeatureType.STRING,
                             description: str = "",
                             owner: str = "") -> Entity:
        """Регистрация сущности"""
        entity = Entity(
            entity_id=f"ent_{uuid.uuid4().hex[:8]}",
            name=name,
            join_keys=join_keys,
            value_type=value_type,
            description=description,
            owner=owner
        )
        
        self.entities[entity.entity_id] = entity
        return entity
        
    async def create_feature_group(self, name: str,
                                  entity_id: str,
                                  source_type: SourceType = SourceType.BATCH,
                                  source_config: Dict[str, Any] = None,
                                  online_ttl_days: int = 7,
                                  offline_ttl_days: int = 365,
                                  description: str = "",
                                  owner: str = "",
                                  team: str = "") -> FeatureGroup:
        """Создание группы признаков"""
        group = FeatureGroup(
            group_id=f"fg_{uuid.uuid4().hex[:8]}",
            name=name,
            entity_id=entity_id,
            source_type=source_type,
            source_config=source_config or {},
            online_ttl_days=online_ttl_days,
            offline_ttl_days=offline_ttl_days,
            description=description,
            owner=owner,
            team=team
        )
        
        self.groups[group.group_id] = group
        return group
        
    async def register_feature(self, name: str,
                              group_id: str,
                              feature_type: FeatureType = FeatureType.FLOAT,
                              source_type: SourceType = SourceType.BATCH,
                              store_type: StoreType = StoreType.BOTH,
                              description: str = "",
                              tags: List[str] = None,
                              default_value: Any = None,
                              min_value: float = None,
                              max_value: float = None) -> Optional[FeatureDefinition]:
        """Регистрация признака"""
        group = self.groups.get(group_id)
        if not group:
            return None
            
        feature = FeatureDefinition(
            feature_id=f"feat_{uuid.uuid4().hex[:8]}",
            name=name,
            group_id=group_id,
            feature_type=feature_type,
            source_type=source_type,
            store_type=store_type,
            description=description,
            tags=tags or [],
            default_value=default_value,
            min_value=min_value,
            max_value=max_value
        )
        
        self.features[feature.feature_id] = feature
        group.feature_ids.append(feature.feature_id)
        group.feature_count += 1
        
        # Create initial version
        await self._create_version(feature)
        
        return feature
        
    async def _create_version(self, feature: FeatureDefinition) -> FeatureVersion:
        """Создание версии признака"""
        existing = [v for v in self.versions.values() if v.feature_id == feature.feature_id]
        version_num = max([v.version for v in existing], default=0) + 1
        
        for v in existing:
            v.is_current = False
            
        version = FeatureVersion(
            version_id=f"ver_{uuid.uuid4().hex[:8]}",
            feature_id=feature.feature_id,
            version=version_num,
            feature_type=feature.feature_type,
            change_description=f"Version {version_num}" if version_num > 1 else "Initial version"
        )
        
        self.versions[version.version_id] = version
        return version
        
    async def add_transformation(self, name: str,
                                feature_id: str,
                                transformation_type: TransformationType,
                                expression: str,
                                input_feature_ids: List[str] = None,
                                parameters: Dict[str, Any] = None) -> Optional[FeatureTransformation]:
        """Добавление трансформации"""
        feature = self.features.get(feature_id)
        if not feature:
            return None
            
        transform = FeatureTransformation(
            transform_id=f"tr_{uuid.uuid4().hex[:8]}",
            name=name,
            feature_id=feature_id,
            transformation_type=transformation_type,
            expression=expression,
            input_feature_ids=input_feature_ids or [],
            parameters=parameters or {}
        )
        
        self.transformations[transform.transform_id] = transform
        return transform
        
    async def create_online_store(self, name: str,
                                 store_type: str = "redis",
                                 connection_string: str = "",
                                 config: Dict[str, Any] = None) -> OnlineStore:
        """Создание онлайн хранилища"""
        store = OnlineStore(
            store_id=f"os_{uuid.uuid4().hex[:8]}",
            name=name,
            store_type=store_type,
            connection_string=connection_string,
            config=config or {}
        )
        
        self.online_stores[store.store_id] = store
        return store
        
    async def create_offline_store(self, name: str,
                                  store_type: str = "parquet",
                                  path: str = "",
                                  config: Dict[str, Any] = None) -> OfflineStore:
        """Создание оффлайн хранилища"""
        store = OfflineStore(
            store_id=f"offs_{uuid.uuid4().hex[:8]}",
            name=name,
            store_type=store_type,
            path=path,
            config=config or {}
        )
        
        self.offline_stores[store.store_id] = store
        return store
        
    async def create_feature_view(self, name: str,
                                 group_ids: List[str],
                                 feature_ids: List[str] = None,
                                 entity_id: str = "",
                                 filter_expression: str = "",
                                 ttl_days: int = 7,
                                 description: str = "") -> FeatureView:
        """Создание представления признаков"""
        view = FeatureView(
            view_id=f"fv_{uuid.uuid4().hex[:8]}",
            name=name,
            group_ids=group_ids,
            feature_ids=feature_ids or [],
            entity_id=entity_id,
            filter_expression=filter_expression,
            ttl_days=ttl_days,
            description=description
        )
        
        self.views[view.view_id] = view
        return view
        
    async def get_online_features(self, feature_ids: List[str],
                                 entity_keys: Dict[str, Any]) -> Dict[str, Any]:
        """Получение онлайн признаков"""
        request = FeatureRequest(
            request_id=f"req_{uuid.uuid4().hex[:8]}",
            feature_ids=feature_ids,
            entity_keys=entity_keys,
            request_type="online"
        )
        
        # Simulate fetching features
        await asyncio.sleep(0.001)  # Simulate latency
        
        results = {}
        for fid in feature_ids:
            feature = self.features.get(fid)
            if feature:
                # Generate simulated value based on type
                if feature.feature_type == FeatureType.FLOAT:
                    results[feature.name] = round(random.uniform(0, 100), 4)
                elif feature.feature_type == FeatureType.INT:
                    results[feature.name] = random.randint(0, 1000)
                elif feature.feature_type == FeatureType.BOOLEAN:
                    results[feature.name] = random.choice([True, False])
                else:
                    results[feature.name] = feature.default_value
                    
        request.responded_at = datetime.now()
        request.latency_ms = random.uniform(1, 10)
        self.requests[request.request_id] = request
        
        return results
        
    async def get_training_features(self, feature_ids: List[str],
                                   entity_df: List[Dict[str, Any]],
                                   start_time: datetime = None,
                                   end_time: datetime = None) -> List[Dict[str, Any]]:
        """Получение признаков для обучения"""
        request = FeatureRequest(
            request_id=f"req_{uuid.uuid4().hex[:8]}",
            feature_ids=feature_ids,
            entity_keys={},
            request_type="training"
        )
        
        results = []
        for entity in entity_df:
            row = entity.copy()
            for fid in feature_ids:
                feature = self.features.get(fid)
                if feature:
                    if feature.feature_type == FeatureType.FLOAT:
                        row[feature.name] = round(random.uniform(0, 100), 4)
                    elif feature.feature_type == FeatureType.INT:
                        row[feature.name] = random.randint(0, 1000)
                    else:
                        row[feature.name] = feature.default_value
            results.append(row)
            
        request.responded_at = datetime.now()
        request.latency_ms = random.uniform(100, 500)
        self.requests[request.request_id] = request
        
        return results
        
    async def add_validation_rule(self, name: str,
                                 feature_id: str,
                                 rule_type: str,
                                 expression: str,
                                 threshold: float = 100.0) -> Optional[ValidationRule]:
        """Добавление правила валидации"""
        feature = self.features.get(feature_id)
        if not feature:
            return None
            
        rule = ValidationRule(
            rule_id=f"vr_{uuid.uuid4().hex[:8]}",
            name=name,
            feature_id=feature_id,
            rule_type=rule_type,
            expression=expression,
            threshold=threshold
        )
        
        self.validation_rules[rule.rule_id] = rule
        return rule
        
    async def validate_features(self, feature_ids: List[str]) -> List[ValidationResult]:
        """Валидация признаков"""
        results = []
        
        for fid in feature_ids:
            rules = [r for r in self.validation_rules.values() if r.feature_id == fid and r.is_enabled]
            
            for rule in rules:
                total = random.randint(10000, 100000)
                valid_rate = random.uniform(0.95, 1.0)
                valid = int(total * valid_rate)
                
                status = ValidationStatus.VALID
                if valid_rate * 100 < rule.threshold:
                    status = ValidationStatus.FAILED
                elif valid_rate * 100 < rule.threshold + 5:
                    status = ValidationStatus.WARNING
                    
                result = ValidationResult(
                    result_id=f"vres_{uuid.uuid4().hex[:8]}",
                    rule_id=rule.rule_id,
                    feature_id=fid,
                    total_values=total,
                    valid_values=valid,
                    invalid_values=total - valid,
                    status=status
                )
                
                self.validation_results[result.result_id] = result
                results.append(result)
                
        return results
        
    async def configure_monitoring(self, feature_id: str,
                                  check_drift: bool = True,
                                  check_null_rate: bool = True,
                                  check_value_range: bool = True,
                                  check_freshness: bool = True,
                                  drift_threshold: float = 0.1,
                                  null_rate_threshold: float = 5.0,
                                  freshness_hours: int = 24) -> Optional[FeatureMonitoringConfig]:
        """Настройка мониторинга признака"""
        feature = self.features.get(feature_id)
        if not feature:
            return None
            
        config = FeatureMonitoringConfig(
            config_id=f"mon_{uuid.uuid4().hex[:8]}",
            feature_id=feature_id,
            check_drift=check_drift,
            check_null_rate=check_null_rate,
            check_value_range=check_value_range,
            check_freshness=check_freshness,
            drift_threshold=drift_threshold,
            null_rate_threshold=null_rate_threshold,
            freshness_hours=freshness_hours
        )
        
        self.monitoring_configs[config.config_id] = config
        return config
        
    async def run_monitoring(self) -> List[MonitoringAlert]:
        """Запуск мониторинга"""
        new_alerts = []
        
        for config in self.monitoring_configs.values():
            feature = self.features.get(config.feature_id)
            if not feature:
                continue
                
            # Simulate monitoring checks
            if config.check_drift and random.random() < 0.1:
                alert = MonitoringAlert(
                    alert_id=f"alert_{uuid.uuid4().hex[:8]}",
                    feature_id=config.feature_id,
                    alert_type=MonitoringAlertType.DATA_DRIFT,
                    message=f"Data drift detected in {feature.name}",
                    current_value=random.uniform(0.1, 0.3),
                    threshold=config.drift_threshold
                )
                self.alerts[alert.alert_id] = alert
                new_alerts.append(alert)
                
            if config.check_null_rate and random.random() < 0.05:
                alert = MonitoringAlert(
                    alert_id=f"alert_{uuid.uuid4().hex[:8]}",
                    feature_id=config.feature_id,
                    alert_type=MonitoringAlertType.NULL_RATE,
                    message=f"High null rate in {feature.name}",
                    current_value=random.uniform(5, 15),
                    threshold=config.null_rate_threshold
                )
                self.alerts[alert.alert_id] = alert
                new_alerts.append(alert)
                
        return new_alerts
        
    async def compute_statistics(self, feature_id: str) -> Optional[FeatureStatistics]:
        """Вычисление статистики признака"""
        feature = self.features.get(feature_id)
        if not feature:
            return None
            
        count = random.randint(100000, 1000000)
        null_count = random.randint(0, int(count * 0.05))
        
        stats = FeatureStatistics(
            stats_id=f"stats_{uuid.uuid4().hex[:8]}",
            feature_id=feature_id,
            count=count,
            null_count=null_count,
            null_rate=null_count / count * 100,
            mean=random.uniform(0, 100),
            std=random.uniform(1, 20),
            min_value=random.uniform(-100, 0),
            max_value=random.uniform(100, 500),
            median=random.uniform(40, 60),
            percentiles={
                "p25": random.uniform(20, 40),
                "p50": random.uniform(40, 60),
                "p75": random.uniform(60, 80),
                "p95": random.uniform(80, 95),
                "p99": random.uniform(95, 100)
            }
        )
        
        self.statistics[stats.stats_id] = stats
        return stats
        
    async def collect_metrics(self) -> FeatureStoreMetrics:
        """Сбор метрик"""
        online_requests = sum(1 for r in self.requests.values() if r.request_type == "online")
        offline_requests = sum(1 for r in self.requests.values() if r.request_type in ["offline", "training"])
        
        latencies = [r.latency_ms for r in self.requests.values()]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        
        active_features = sum(1 for f in self.features.values() if f.status == FeatureStatus.ACTIVE)
        active_groups = sum(1 for g in self.groups.values() if g.status == FeatureStatus.ACTIVE)
        active_alerts = sum(1 for a in self.alerts.values() if not a.is_resolved)
        
        metrics = FeatureStoreMetrics(
            metrics_id=f"fsm_{uuid.uuid4().hex[:8]}",
            online_requests=online_requests,
            offline_requests=offline_requests,
            avg_latency_ms=avg_latency,
            online_keys=sum(s.key_count for s in self.online_stores.values()),
            offline_rows=sum(s.row_count for s in self.offline_stores.values()),
            active_features=active_features,
            active_groups=active_groups,
            active_alerts=active_alerts
        )
        
        self.metrics[metrics.metrics_id] = metrics
        return metrics
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_entities = len(self.entities)
        total_groups = len(self.groups)
        active_groups = sum(1 for g in self.groups.values() if g.status == FeatureStatus.ACTIVE)
        
        total_features = len(self.features)
        active_features = sum(1 for f in self.features.values() if f.status == FeatureStatus.ACTIVE)
        
        features_by_type = {}
        for ftype in FeatureType:
            features_by_type[ftype.value] = sum(1 for f in self.features.values() if f.feature_type == ftype)
            
        total_transformations = len(self.transformations)
        total_versions = len(self.versions)
        
        total_validation_rules = len(self.validation_rules)
        total_monitoring_configs = len(self.monitoring_configs)
        
        active_alerts = sum(1 for a in self.alerts.values() if not a.is_resolved)
        
        return {
            "total_entities": total_entities,
            "total_groups": total_groups,
            "active_groups": active_groups,
            "total_features": total_features,
            "active_features": active_features,
            "features_by_type": features_by_type,
            "total_transformations": total_transformations,
            "total_versions": total_versions,
            "total_validation_rules": total_validation_rules,
            "total_monitoring_configs": total_monitoring_configs,
            "active_alerts": active_alerts
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 353: Feature Store Platform")
    print("=" * 60)
    
    platform = FeatureStorePlatform(project="ml-platform")
    print("✓ Feature Store Platform initialized")
    
    # Register Entities
    print("\n🎯 Registering Entities...")
    
    entities_data = [
        ("customer", ["customer_id"], FeatureType.STRING, "Customer entity for customer-centric features", "ml-team"),
        ("product", ["product_id"], FeatureType.STRING, "Product entity for product features", "ml-team"),
        ("order", ["order_id"], FeatureType.STRING, "Order entity for transaction features", "ml-team"),
        ("session", ["session_id"], FeatureType.STRING, "Session entity for clickstream features", "analytics"),
        ("user_product", ["user_id", "product_id"], FeatureType.STRING, "User-Product interaction entity", "recommender-team")
    ]
    
    entities = []
    for name, keys, vtype, desc, owner in entities_data:
        e = await platform.register_entity(name, keys, vtype, desc, owner)
        entities.append(e)
        print(f"  🎯 {name} (keys: {', '.join(keys)})")
        
    # Create Feature Groups
    print("\n📦 Creating Feature Groups...")
    
    groups_data = [
        ("customer_profile", entities[0].entity_id, SourceType.BATCH, {"table": "customer_profile"}, 7, 365, "Customer profile features", "ml-team", "platform"),
        ("customer_behavior", entities[0].entity_id, SourceType.STREAM, {"topic": "customer_events"}, 1, 90, "Customer behavioral features", "ml-team", "platform"),
        ("product_catalog", entities[1].entity_id, SourceType.BATCH, {"table": "products"}, 30, 365, "Product catalog features", "ml-team", "catalog"),
        ("order_history", entities[2].entity_id, SourceType.BATCH, {"table": "orders"}, 7, 365, "Order history features", "ml-team", "transactions"),
        ("session_features", entities[3].entity_id, SourceType.STREAM, {"topic": "sessions"}, 1, 30, "Session features", "analytics", "clickstream"),
        ("user_product_interactions", entities[4].entity_id, SourceType.BATCH, {"table": "interactions"}, 7, 180, "User-product interaction features", "recommender-team", "recommendations")
    ]
    
    groups = []
    for name, eid, stype, sconfig, online_ttl, offline_ttl, desc, owner, team in groups_data:
        g = await platform.create_feature_group(name, eid, stype, sconfig, online_ttl, offline_ttl, desc, owner, team)
        groups.append(g)
        print(f"  📦 {name} ({stype.value})")
        
    # Register Features
    print("\n✨ Registering Features...")
    
    features_data = [
        # Customer profile
        ("customer_age", groups[0].group_id, FeatureType.INT, StoreType.BOTH, "Customer age", ["demographic"], 0, 18, 120),
        ("customer_gender", groups[0].group_id, FeatureType.STRING, StoreType.BOTH, "Customer gender", ["demographic"], None, None, None),
        ("customer_tenure_days", groups[0].group_id, FeatureType.INT, StoreType.BOTH, "Days since registration", ["engagement"], 0, 0, 10000),
        ("customer_segment", groups[0].group_id, FeatureType.STRING, StoreType.BOTH, "Customer segment", ["segmentation"], None, None, None),
        # Customer behavior
        ("last_purchase_days_ago", groups[1].group_id, FeatureType.INT, StoreType.ONLINE, "Days since last purchase", ["recency"], 0, 0, 365),
        ("purchase_count_30d", groups[1].group_id, FeatureType.INT, StoreType.BOTH, "Purchases in last 30 days", ["frequency"], 0, 0, 100),
        ("total_spend_30d", groups[1].group_id, FeatureType.FLOAT, StoreType.BOTH, "Total spend in last 30 days", ["monetary"], 0.0, 0, 100000),
        ("avg_order_value", groups[1].group_id, FeatureType.FLOAT, StoreType.BOTH, "Average order value", ["monetary"], 0.0, 0, 10000),
        # Product catalog
        ("product_price", groups[2].group_id, FeatureType.FLOAT, StoreType.BOTH, "Product price", ["pricing"], 0.0, 0, 100000),
        ("product_category", groups[2].group_id, FeatureType.STRING, StoreType.BOTH, "Product category", ["catalog"], None, None, None),
        ("product_rating", groups[2].group_id, FeatureType.FLOAT, StoreType.BOTH, "Average product rating", ["ratings"], 0.0, 0, 5),
        ("product_review_count", groups[2].group_id, FeatureType.INT, StoreType.BOTH, "Number of reviews", ["engagement"], 0, 0, 10000),
        # Order history
        ("order_total", groups[3].group_id, FeatureType.FLOAT, StoreType.OFFLINE, "Order total amount", ["transactions"], 0.0, 0, 100000),
        ("order_item_count", groups[3].group_id, FeatureType.INT, StoreType.OFFLINE, "Items in order", ["transactions"], 0, 1, 100),
        # Session features
        ("session_duration_sec", groups[4].group_id, FeatureType.INT, StoreType.ONLINE, "Session duration in seconds", ["engagement"], 0, 0, 36000),
        ("pages_viewed", groups[4].group_id, FeatureType.INT, StoreType.ONLINE, "Pages viewed in session", ["engagement"], 0, 1, 100),
        # User-product interactions
        ("view_count", groups[5].group_id, FeatureType.INT, StoreType.BOTH, "Product views by user", ["interaction"], 0, 0, 1000),
        ("purchase_flag", groups[5].group_id, FeatureType.BOOLEAN, StoreType.BOTH, "Has user purchased product", ["conversion"], False, None, None),
        ("interaction_score", groups[5].group_id, FeatureType.FLOAT, StoreType.ONLINE, "User-product affinity score", ["recommendation"], 0.0, 0, 1)
    ]
    
    features = []
    for name, gid, ftype, stype, desc, tags, default, minv, maxv in features_data:
        f = await platform.register_feature(name, gid, ftype, SourceType.BATCH, stype, desc, tags, default, minv, maxv)
        if f:
            features.append(f)
            print(f"  ✨ {name} ({ftype.value})")
            
    # Add Transformations
    print("\n🔄 Adding Transformations...")
    
    transform_data = [
        ("customer_lifetime_value", features[6].feature_id, TransformationType.AGGREGATION, "SUM(order_total)", [features[12].feature_id], {"window": "365d"}),
        ("recency_score", features[4].feature_id, TransformationType.DERIVED, "1 / (1 + last_purchase_days_ago)", [], {}),
        ("frequency_score", features[5].feature_id, TransformationType.DERIVED, "purchase_count_30d / 30", [], {}),
        ("monetary_score", features[6].feature_id, TransformationType.DERIVED, "log1p(total_spend_30d)", [], {}),
        ("normalized_rating", features[10].feature_id, TransformationType.DERIVED, "product_rating / 5.0", [], {})
    ]
    
    transformations = []
    for name, fid, ttype, expr, inputs, params in transform_data:
        t = await platform.add_transformation(name, fid, ttype, expr, inputs, params)
        if t:
            transformations.append(t)
            print(f"  🔄 {name} ({ttype.value})")
            
    # Create Stores
    print("\n💾 Creating Stores...")
    
    online_store = await platform.create_online_store(
        "redis_online",
        "redis",
        "redis://localhost:6379/0",
        {"max_connections": 100, "timeout": 5}
    )
    online_store.key_count = random.randint(100000, 1000000)
    online_store.avg_latency_ms = random.uniform(1, 5)
    online_store.p99_latency_ms = random.uniform(5, 20)
    print(f"  💾 Online Store: {online_store.name}")
    
    offline_store = await platform.create_offline_store(
        "parquet_offline",
        "parquet",
        "s3://feature-store/offline/",
        {"partition_by": ["date"]}
    )
    offline_store.row_count = random.randint(10000000, 100000000)
    offline_store.size_bytes = random.randint(1024**3, 10 * 1024**3)
    print(f"  💾 Offline Store: {offline_store.name}")
    
    # Create Feature Views
    print("\n👁️ Creating Feature Views...")
    
    views_data = [
        ("customer_360", [groups[0].group_id, groups[1].group_id], features[:8], entities[0].entity_id, "", "360-degree customer view"),
        ("product_features", [groups[2].group_id], features[8:12], entities[1].entity_id, "", "Product feature view"),
        ("recommendation_features", [groups[5].group_id], features[16:19], entities[4].entity_id, "", "Features for recommendations")
    ]
    
    views = []
    for name, gids, feats, eid, filt, desc in views_data:
        fids = [f.feature_id for f in feats]
        v = await platform.create_feature_view(name, gids, fids, eid, filt, 7, desc)
        views.append(v)
        print(f"  👁️ {name} ({len(fids)} features)")
        
    # Add Validation Rules
    print("\n✅ Adding Validation Rules...")
    
    validation_data = [
        ("age_range", features[0].feature_id, "range", "value BETWEEN 18 AND 120", 99.9),
        ("tenure_positive", features[2].feature_id, "range", "value >= 0", 100.0),
        ("spend_positive", features[6].feature_id, "range", "value >= 0", 100.0),
        ("rating_range", features[10].feature_id, "range", "value BETWEEN 0 AND 5", 100.0),
        ("score_normalized", features[18].feature_id, "range", "value BETWEEN 0 AND 1", 100.0)
    ]
    
    validation_rules = []
    for name, fid, rtype, expr, threshold in validation_data:
        r = await platform.add_validation_rule(name, fid, rtype, expr, threshold)
        if r:
            validation_rules.append(r)
            print(f"  ✅ {name} ({rtype})")
            
    # Configure Monitoring
    print("\n📡 Configuring Monitoring...")
    
    for feature in features[:10]:
        await platform.configure_monitoring(feature.feature_id)
        
    print(f"  📡 Configured monitoring for {len(platform.monitoring_configs)} features")
    
    # Simulate Feature Requests
    print("\n🔍 Simulating Feature Requests...")
    
    for _ in range(20):
        fids = [f.feature_id for f in random.sample(features[:8], random.randint(3, 6))]
        await platform.get_online_features(fids, {"customer_id": f"cust_{random.randint(1000, 9999)}"})
        
    # Training features
    entity_df = [{"customer_id": f"cust_{i}"} for i in range(100)]
    await platform.get_training_features([f.feature_id for f in features[:8]], entity_df)
    
    print(f"  🔍 Executed {len(platform.requests)} feature requests")
    
    # Run Validation
    print("\n🔒 Running Feature Validation...")
    
    validation_results = await platform.validate_features([f.feature_id for f in features[:5]])
    print(f"  🔒 Validated {len(validation_results)} rules")
    
    # Run Monitoring
    print("\n📊 Running Monitoring...")
    
    alerts = await platform.run_monitoring()
    print(f"  📊 Generated {len(alerts)} alerts")
    
    # Compute Statistics
    print("\n📈 Computing Feature Statistics...")
    
    all_stats = []
    for feature in features[:10]:
        stats = await platform.compute_statistics(feature.feature_id)
        if stats:
            all_stats.append(stats)
            
    print(f"  📈 Computed statistics for {len(all_stats)} features")
    
    # Collect Metrics
    metrics = await platform.collect_metrics()
    
    # Feature Groups Dashboard
    print("\n📦 Feature Groups:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Group Name                      │ Entity       │ Source   │ Features │ Online TTL │ Offline TTL │ Owner       │ Status                                                                              │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for g in groups:
        name = g.name[:31].ljust(31)
        entity = platform.entities.get(g.entity_id)
        ent_name = entity.name if entity else "N/A"
        ent_name = ent_name[:12].ljust(12)
        source = g.source_type.value[:8].ljust(8)
        feats = str(g.feature_count).ljust(8)
        online_ttl = f"{g.online_ttl_days}d".ljust(10)
        offline_ttl = f"{g.offline_ttl_days}d".ljust(11)
        owner = g.owner[:11].ljust(11)
        status = g.status.value[:68].ljust(68)
        
        print(f"  │ {name} │ {ent_name} │ {source} │ {feats} │ {online_ttl} │ {offline_ttl} │ {owner} │ {status} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Features Dashboard
    print("\n✨ Features:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Feature Name                    │ Group                           │ Type        │ Store      │ Tags                                           │ Status                                                                              │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for f in features:
        name = f.name[:31].ljust(31)
        group = platform.groups.get(f.group_id)
        grp_name = group.name if group else "N/A"
        grp_name = grp_name[:31].ljust(31)
        ftype = f.feature_type.value[:11].ljust(11)
        store = f.store_type.value[:10].ljust(10)
        tags = ", ".join(f.tags[:2])[:46]
        tags = tags.ljust(46)
        status = f.status.value[:68].ljust(68)
        
        print(f"  │ {name} │ {grp_name} │ {ftype} │ {store} │ {tags} │ {status} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Statistics Dashboard
    print("\n📈 Feature Statistics:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Feature Name                    │ Count       │ Null Rate │ Mean       │ Std Dev   │ Min        │ Max        │ Median                                                                                               │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for s in all_stats:
        feature = platform.features.get(s.feature_id)
        name = feature.name if feature else "Unknown"
        name = name[:31].ljust(31)
        count = f"{s.count:,}".ljust(11)
        null_rate = f"{s.null_rate:.2f}%".ljust(9)
        mean = f"{s.mean:.2f}".ljust(10)
        std = f"{s.std:.2f}".ljust(9)
        min_v = f"{s.min_value:.2f}".ljust(10)
        max_v = f"{s.max_value:.2f}".ljust(10)
        median = f"{s.median:.2f}".ljust(100)
        
        print(f"  │ {name} │ {count} │ {null_rate} │ {mean} │ {std} │ {min_v} │ {max_v} │ {median} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Validation Results
    print("\n✅ Validation Results:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Rule Name                       │ Feature                         │ Total      │ Valid     │ Invalid   │ Status                                                                                                                                                                                                                                                                                                           │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for vr in validation_results:
        rule = platform.validation_rules.get(vr.rule_id)
        rule_name = rule.name if rule else "Unknown"
        rule_name = rule_name[:31].ljust(31)
        feature = platform.features.get(vr.feature_id)
        feat_name = feature.name if feature else "Unknown"
        feat_name = feat_name[:31].ljust(31)
        total = f"{vr.total_values:,}".ljust(10)
        valid = f"{vr.valid_values:,}".ljust(9)
        invalid = f"{vr.invalid_values:,}".ljust(9)
        status_str = "✅ Valid" if vr.status == ValidationStatus.VALID else "⚠️ Warning" if vr.status == ValidationStatus.WARNING else "❌ Failed"
        status_str = status_str[:266].ljust(266)
        
        print(f"  │ {rule_name} │ {feat_name} │ {total} │ {valid} │ {invalid} │ {status_str} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Entities: {stats['total_entities']}")
    print(f"  Feature Groups: {stats['active_groups']}/{stats['total_groups']} active")
    print(f"  Features: {stats['active_features']}/{stats['total_features']} active")
    print(f"  Transformations: {stats['total_transformations']}")
    print(f"  Validation Rules: {stats['total_validation_rules']}")
    print(f"  Active Alerts: {stats['active_alerts']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                      Feature Store Platform                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Entities:                {stats['total_entities']:>12}                      │")
    print(f"│ Feature Groups:                {stats['active_groups']:>12}                      │")
    print(f"│ Active Features:               {stats['active_features']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Online Requests:               {metrics.online_requests:>12}                      │")
    print(f"│ Offline Requests:              {metrics.offline_requests:>12}                      │")
    print(f"│ Avg Latency (ms):              {metrics.avg_latency_ms:>12.2f}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Transformations:               {stats['total_transformations']:>12}                      │")
    print(f"│ Validation Rules:              {stats['total_validation_rules']:>12}                      │")
    print(f"│ Active Alerts:                 {stats['active_alerts']:>12}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Feature Store Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
