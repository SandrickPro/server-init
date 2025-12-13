#!/usr/bin/env python3
"""
Server Init - Iteration 79: MLOps Platform
Платформа для MLOps

Функционал:
- Model Registry - реестр моделей
- Experiment Tracking - отслеживание экспериментов
- Model Versioning - версионирование моделей
- Model Deployment - развёртывание моделей
- Model Monitoring - мониторинг моделей
- Feature Store - хранилище признаков
- A/B Testing - A/B тестирование моделей
- Model Lineage - происхождение моделей
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
from collections import defaultdict
import uuid
import hashlib
import random


class ModelStatus(Enum):
    """Статус модели"""
    DRAFT = "draft"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


class ExperimentStatus(Enum):
    """Статус эксперимента"""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


class DeploymentStatus(Enum):
    """Статус развёртывания"""
    PENDING = "pending"
    DEPLOYING = "deploying"
    RUNNING = "running"
    FAILED = "failed"
    STOPPED = "stopped"


class ModelFramework(Enum):
    """Фреймворк модели"""
    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"
    SKLEARN = "sklearn"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    ONNX = "onnx"
    CUSTOM = "custom"


class FeatureType(Enum):
    """Тип признака"""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    TEXT = "text"
    EMBEDDING = "embedding"
    TIMESTAMP = "timestamp"


@dataclass
class Metric:
    """Метрика"""
    name: str
    value: float
    step: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Parameter:
    """Параметр"""
    name: str
    value: Any
    param_type: str = "string"


@dataclass
class Artifact:
    """Артефакт"""
    artifact_id: str
    name: str = ""
    
    # Тип
    artifact_type: str = ""  # model, dataset, plot, config
    
    # Путь
    path: str = ""
    
    # Размер
    size_bytes: int = 0
    
    # Хэш
    checksum: str = ""
    
    # Метаданные
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Experiment:
    """Эксперимент"""
    experiment_id: str
    name: str = ""
    
    # Статус
    status: ExperimentStatus = ExperimentStatus.RUNNING
    
    # Время
    started_at: datetime = field(default_factory=datetime.now)
    finished_at: Optional[datetime] = None
    
    # Параметры и метрики
    parameters: Dict[str, Parameter] = field(default_factory=dict)
    metrics: Dict[str, List[Metric]] = field(default_factory=lambda: defaultdict(list))
    
    # Артефакты
    artifacts: Dict[str, Artifact] = field(default_factory=dict)
    
    # Git info
    git_commit: str = ""
    git_branch: str = ""
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Описание
    description: str = ""


@dataclass
class ModelVersion:
    """Версия модели"""
    version_id: str
    model_id: str = ""
    version: str = ""
    
    # Статус
    status: ModelStatus = ModelStatus.DRAFT
    
    # Фреймворк
    framework: ModelFramework = ModelFramework.SKLEARN
    
    # Эксперимент
    experiment_id: str = ""
    
    # Артефакты
    model_path: str = ""
    model_checksum: str = ""
    
    # Метрики
    metrics: Dict[str, float] = field(default_factory=dict)
    
    # Входные/выходные схемы
    input_schema: Dict[str, str] = field(default_factory=dict)
    output_schema: Dict[str, str] = field(default_factory=dict)
    
    # Размер и производительность
    model_size_mb: float = 0.0
    avg_inference_time_ms: float = 0.0
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    
    # Метаданные
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RegisteredModel:
    """Зарегистрированная модель"""
    model_id: str
    name: str = ""
    description: str = ""
    
    # Версии
    versions: Dict[str, ModelVersion] = field(default_factory=dict)
    latest_version: str = ""
    production_version: str = ""
    
    # Владелец
    owner: str = ""
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Feature:
    """Признак"""
    feature_id: str
    name: str = ""
    
    # Тип
    feature_type: FeatureType = FeatureType.NUMERICAL
    
    # Описание
    description: str = ""
    
    # Источник
    source: str = ""
    
    # Статистика
    statistics: Dict[str, Any] = field(default_factory=dict)
    
    # Трансформации
    transformations: List[str] = field(default_factory=list)
    
    # Метаданные
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FeatureGroup:
    """Группа признаков"""
    group_id: str
    name: str = ""
    
    # Признаки
    features: Dict[str, Feature] = field(default_factory=dict)
    
    # Первичный ключ
    primary_key: List[str] = field(default_factory=list)
    
    # Timestamp key
    event_time_column: str = ""
    
    # Описание
    description: str = ""
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ModelEndpoint:
    """Endpoint модели"""
    endpoint_id: str
    name: str = ""
    
    # Модель
    model_id: str = ""
    version_id: str = ""
    
    # Статус
    status: DeploymentStatus = DeploymentStatus.PENDING
    
    # URL
    url: str = ""
    
    # Ресурсы
    cpu_limit: str = "1"
    memory_limit: str = "2Gi"
    replicas: int = 1
    
    # Автоскейлинг
    min_replicas: int = 1
    max_replicas: int = 10
    target_cpu_utilization: int = 70
    
    # Traffic splitting
    traffic_percent: int = 100
    
    # Метрики
    requests_total: int = 0
    requests_success: int = 0
    avg_latency_ms: float = 0.0
    
    # Время
    deployed_at: Optional[datetime] = None


@dataclass
class ABTest:
    """A/B тест"""
    test_id: str
    name: str = ""
    
    # Варианты (model_version_id -> traffic_percent)
    variants: Dict[str, int] = field(default_factory=dict)
    
    # Метрика
    primary_metric: str = ""
    
    # Результаты
    results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Статус
    active: bool = True
    
    # Время
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None


@dataclass
class PredictionLog:
    """Лог предсказания"""
    log_id: str
    
    # Модель
    model_id: str = ""
    version_id: str = ""
    
    # Вход/выход
    input_data: Dict[str, Any] = field(default_factory=dict)
    prediction: Any = None
    
    # Время
    timestamp: datetime = field(default_factory=datetime.now)
    latency_ms: float = 0.0
    
    # Метаданные
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExperimentTracker:
    """Трекер экспериментов"""
    
    def __init__(self):
        self.experiments: Dict[str, Experiment] = {}
        self.active_experiment: Optional[str] = None
        
    def create_experiment(self, name: str, **kwargs) -> Experiment:
        """Создание эксперимента"""
        experiment = Experiment(
            experiment_id=f"exp_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        self.experiments[experiment.experiment_id] = experiment
        self.active_experiment = experiment.experiment_id
        return experiment
        
    def log_param(self, name: str, value: Any, experiment_id: str = None):
        """Логирование параметра"""
        exp_id = experiment_id or self.active_experiment
        if not exp_id:
            return
            
        experiment = self.experiments.get(exp_id)
        if experiment:
            experiment.parameters[name] = Parameter(
                name=name,
                value=value,
                param_type=type(value).__name__
            )
            
    def log_metric(self, name: str, value: float, step: int = 0,
                    experiment_id: str = None):
        """Логирование метрики"""
        exp_id = experiment_id or self.active_experiment
        if not exp_id:
            return
            
        experiment = self.experiments.get(exp_id)
        if experiment:
            experiment.metrics[name].append(Metric(
                name=name,
                value=value,
                step=step
            ))
            
    def log_artifact(self, name: str, path: str, artifact_type: str = "file",
                      experiment_id: str = None):
        """Логирование артефакта"""
        exp_id = experiment_id or self.active_experiment
        if not exp_id:
            return
            
        experiment = self.experiments.get(exp_id)
        if experiment:
            artifact = Artifact(
                artifact_id=f"art_{uuid.uuid4().hex[:8]}",
                name=name,
                path=path,
                artifact_type=artifact_type,
                checksum=hashlib.md5(path.encode()).hexdigest()
            )
            experiment.artifacts[name] = artifact
            
    def end_experiment(self, status: ExperimentStatus = ExperimentStatus.COMPLETED,
                        experiment_id: str = None):
        """Завершение эксперимента"""
        exp_id = experiment_id or self.active_experiment
        if not exp_id:
            return
            
        experiment = self.experiments.get(exp_id)
        if experiment:
            experiment.status = status
            experiment.finished_at = datetime.now()
            
        if exp_id == self.active_experiment:
            self.active_experiment = None


class ModelRegistry:
    """Реестр моделей"""
    
    def __init__(self):
        self.models: Dict[str, RegisteredModel] = {}
        
    def create_model(self, name: str, **kwargs) -> RegisteredModel:
        """Создание модели"""
        model = RegisteredModel(
            model_id=f"model_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        self.models[model.model_id] = model
        return model
        
    def register_version(self, model_id: str, version: str,
                          **kwargs) -> ModelVersion:
        """Регистрация версии"""
        model = self.models.get(model_id)
        if not model:
            raise ValueError(f"Model {model_id} not found")
            
        model_version = ModelVersion(
            version_id=f"ver_{uuid.uuid4().hex[:8]}",
            model_id=model_id,
            version=version,
            **kwargs
        )
        
        model.versions[model_version.version_id] = model_version
        model.latest_version = model_version.version_id
        model.updated_at = datetime.now()
        
        return model_version
        
    def transition_stage(self, version_id: str, stage: ModelStatus):
        """Изменение стадии модели"""
        for model in self.models.values():
            if version_id in model.versions:
                model.versions[version_id].status = stage
                
                if stage == ModelStatus.PRODUCTION:
                    # Переводим предыдущую production в archived
                    if model.production_version and model.production_version != version_id:
                        old_ver = model.versions.get(model.production_version)
                        if old_ver:
                            old_ver.status = ModelStatus.ARCHIVED
                    model.production_version = version_id
                    
                model.updated_at = datetime.now()
                return
                
        raise ValueError(f"Version {version_id} not found")
        
    def get_production_version(self, model_id: str) -> Optional[ModelVersion]:
        """Получение production версии"""
        model = self.models.get(model_id)
        if model and model.production_version:
            return model.versions.get(model.production_version)
        return None


class FeatureStore:
    """Хранилище признаков"""
    
    def __init__(self):
        self.groups: Dict[str, FeatureGroup] = {}
        self.features: Dict[str, Feature] = {}
        
    def create_feature_group(self, name: str, features: List[Dict[str, Any]],
                              **kwargs) -> FeatureGroup:
        """Создание группы признаков"""
        group = FeatureGroup(
            group_id=f"fg_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        
        for feat_data in features:
            feature = Feature(
                feature_id=f"feat_{uuid.uuid4().hex[:8]}",
                **feat_data
            )
            group.features[feature.feature_id] = feature
            self.features[feature.feature_id] = feature
            
        self.groups[group.group_id] = group
        return group
        
    def get_features(self, feature_ids: List[str]) -> Dict[str, Feature]:
        """Получение признаков"""
        return {fid: self.features[fid] for fid in feature_ids if fid in self.features}
        
    def compute_statistics(self, group_id: str, data: List[Dict[str, Any]]):
        """Вычисление статистики"""
        group = self.groups.get(group_id)
        if not group:
            return
            
        for feature in group.features.values():
            values = [row.get(feature.name) for row in data if row.get(feature.name) is not None]
            
            if feature.feature_type == FeatureType.NUMERICAL and values:
                feature.statistics = {
                    "count": len(values),
                    "mean": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values)
                }
            elif feature.feature_type == FeatureType.CATEGORICAL and values:
                unique_values = list(set(values))
                feature.statistics = {
                    "count": len(values),
                    "unique": len(unique_values),
                    "top_values": unique_values[:5]
                }


class ModelDeployer:
    """Развёртывание моделей"""
    
    def __init__(self, registry: ModelRegistry):
        self.registry = registry
        self.endpoints: Dict[str, ModelEndpoint] = {}
        self.ab_tests: Dict[str, ABTest] = {}
        self.prediction_logs: List[PredictionLog] = []
        
    async def deploy(self, model_id: str, version_id: str,
                      name: str = None, **kwargs) -> ModelEndpoint:
        """Развёртывание модели"""
        model = self.registry.models.get(model_id)
        if not model:
            raise ValueError(f"Model {model_id} not found")
            
        version = model.versions.get(version_id)
        if not version:
            raise ValueError(f"Version {version_id} not found")
            
        endpoint = ModelEndpoint(
            endpoint_id=f"ep_{uuid.uuid4().hex[:8]}",
            name=name or f"{model.name}-{version.version}",
            model_id=model_id,
            version_id=version_id,
            status=DeploymentStatus.DEPLOYING,
            **kwargs
        )
        
        # Симуляция развёртывания
        await asyncio.sleep(0.2)
        
        endpoint.status = DeploymentStatus.RUNNING
        endpoint.deployed_at = datetime.now()
        endpoint.url = f"https://models.example.com/v1/{endpoint.endpoint_id}/predict"
        
        self.endpoints[endpoint.endpoint_id] = endpoint
        return endpoint
        
    async def predict(self, endpoint_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Предсказание"""
        endpoint = self.endpoints.get(endpoint_id)
        if not endpoint or endpoint.status != DeploymentStatus.RUNNING:
            raise ValueError(f"Endpoint {endpoint_id} not available")
            
        start_time = datetime.now()
        
        # Симуляция inference
        await asyncio.sleep(0.01)
        prediction = {"class": random.choice(["A", "B", "C"]), "probability": random.random()}
        
        latency = (datetime.now() - start_time).total_seconds() * 1000
        
        # Обновляем метрики endpoint
        endpoint.requests_total += 1
        endpoint.requests_success += 1
        endpoint.avg_latency_ms = (
            endpoint.avg_latency_ms * (endpoint.requests_total - 1) + latency
        ) / endpoint.requests_total
        
        # Логируем предсказание
        log = PredictionLog(
            log_id=f"pred_{uuid.uuid4().hex[:8]}",
            model_id=endpoint.model_id,
            version_id=endpoint.version_id,
            input_data=input_data,
            prediction=prediction,
            latency_ms=latency
        )
        self.prediction_logs.append(log)
        
        return prediction
        
    def create_ab_test(self, name: str, variants: Dict[str, int],
                        primary_metric: str = "accuracy") -> ABTest:
        """Создание A/B теста"""
        test = ABTest(
            test_id=f"ab_{uuid.uuid4().hex[:8]}",
            name=name,
            variants=variants,
            primary_metric=primary_metric
        )
        self.ab_tests[test.test_id] = test
        return test
        
    def route_request(self, test_id: str) -> str:
        """Маршрутизация запроса по A/B тесту"""
        test = self.ab_tests.get(test_id)
        if not test or not test.active:
            return None
            
        total = sum(test.variants.values())
        rand = random.randint(1, total)
        
        cumulative = 0
        for version_id, percent in test.variants.items():
            cumulative += percent
            if rand <= cumulative:
                return version_id
                
        return list(test.variants.keys())[0]


class MLOpsPlatform:
    """Платформа MLOps"""
    
    def __init__(self):
        self.tracker = ExperimentTracker()
        self.registry = ModelRegistry()
        self.feature_store = FeatureStore()
        self.deployer = ModelDeployer(self.registry)
        
    def get_stats(self) -> Dict[str, Any]:
        """Статистика платформы"""
        total_predictions = len(self.deployer.prediction_logs)
        
        return {
            "experiments": len(self.tracker.experiments),
            "models": len(self.registry.models),
            "model_versions": sum(len(m.versions) for m in self.registry.models.values()),
            "feature_groups": len(self.feature_store.groups),
            "features": len(self.feature_store.features),
            "endpoints": len(self.deployer.endpoints),
            "active_ab_tests": len([t for t in self.deployer.ab_tests.values() if t.active]),
            "total_predictions": total_predictions
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 79: MLOps Platform")
    print("=" * 60)
    
    async def demo():
        platform = MLOpsPlatform()
        print("✓ MLOps Platform created")
        
        # Experiment Tracking
        print("\n🧪 Experiment Tracking...")
        
        exp1 = platform.tracker.create_experiment(
            "fraud_detection_v1",
            description="Initial fraud detection model",
            git_branch="feature/fraud-model",
            tags={"team": "ml", "project": "fraud"}
        )
        print(f"  ✓ Created experiment: {exp1.name}")
        
        # Логирование параметров
        platform.tracker.log_param("learning_rate", 0.001)
        platform.tracker.log_param("batch_size", 32)
        platform.tracker.log_param("hidden_layers", [128, 64, 32])
        platform.tracker.log_param("dropout", 0.3)
        print("  ✓ Logged parameters")
        
        # Логирование метрик
        for epoch in range(5):
            loss = 1.0 - epoch * 0.15
            accuracy = 0.7 + epoch * 0.05
            platform.tracker.log_metric("loss", loss, step=epoch)
            platform.tracker.log_metric("accuracy", accuracy, step=epoch)
            platform.tracker.log_metric("f1_score", accuracy * 0.95, step=epoch)
            
        print("  ✓ Logged metrics for 5 epochs")
        
        # Артефакты
        platform.tracker.log_artifact("model", "/models/fraud_v1.pkl", "model")
        platform.tracker.log_artifact("config", "/configs/fraud_v1.yaml", "config")
        print("  ✓ Logged artifacts")
        
        # Завершение эксперимента
        platform.tracker.end_experiment(ExperimentStatus.COMPLETED)
        print(f"  ✓ Experiment completed")
        
        # Просмотр метрик
        print("\n  Final Metrics:")
        for name, metrics in exp1.metrics.items():
            last_value = metrics[-1].value if metrics else 0
            print(f"    {name}: {last_value:.4f}")
            
        # Feature Store
        print("\n📦 Feature Store...")
        
        user_features = platform.feature_store.create_feature_group(
            "user_features",
            features=[
                {"name": "user_age", "feature_type": FeatureType.NUMERICAL, "description": "User age"},
                {"name": "account_age_days", "feature_type": FeatureType.NUMERICAL, "description": "Days since signup"},
                {"name": "transaction_count", "feature_type": FeatureType.NUMERICAL, "description": "Total transactions"},
                {"name": "avg_transaction_amount", "feature_type": FeatureType.NUMERICAL, "description": "Average amount"},
                {"name": "user_country", "feature_type": FeatureType.CATEGORICAL, "description": "Country code"},
            ],
            primary_key=["user_id"],
            event_time_column="event_timestamp",
            description="User features for fraud detection"
        )
        print(f"  ✓ Created feature group: {user_features.name}")
        print(f"    Features: {len(user_features.features)}")
        
        # Вычисление статистики
        sample_data = [
            {"user_age": 25, "account_age_days": 100, "transaction_count": 50, "avg_transaction_amount": 150.0, "user_country": "US"},
            {"user_age": 35, "account_age_days": 500, "transaction_count": 200, "avg_transaction_amount": 250.0, "user_country": "UK"},
            {"user_age": 45, "account_age_days": 300, "transaction_count": 100, "avg_transaction_amount": 180.0, "user_country": "US"},
        ]
        
        platform.feature_store.compute_statistics(user_features.group_id, sample_data)
        print("  ✓ Computed feature statistics")
        
        for feat in user_features.features.values():
            if feat.statistics:
                print(f"    {feat.name}: {feat.statistics}")
                
        # Model Registry
        print("\n📋 Model Registry...")
        
        fraud_model = platform.registry.create_model(
            "fraud_detector",
            description="Fraud detection model",
            owner="ml-team",
            tags=["fraud", "classification", "production"]
        )
        print(f"  ✓ Created model: {fraud_model.name}")
        
        # Регистрация версий
        v1 = platform.registry.register_version(
            fraud_model.model_id,
            version="1.0.0",
            framework=ModelFramework.SKLEARN,
            experiment_id=exp1.experiment_id,
            model_path="/models/fraud_v1.pkl",
            metrics={"accuracy": 0.95, "f1_score": 0.92, "auc": 0.98},
            input_schema={"features": "array<float>"},
            output_schema={"prediction": "int", "probability": "float"},
            model_size_mb=15.5,
            avg_inference_time_ms=5.2
        )
        print(f"  ✓ Registered version: {v1.version}")
        print(f"    Metrics: accuracy={v1.metrics['accuracy']}, f1={v1.metrics['f1_score']}")
        
        v2 = platform.registry.register_version(
            fraud_model.model_id,
            version="1.1.0",
            framework=ModelFramework.SKLEARN,
            metrics={"accuracy": 0.96, "f1_score": 0.94, "auc": 0.99},
            model_size_mb=18.2,
            avg_inference_time_ms=4.8
        )
        print(f"  ✓ Registered version: {v2.version}")
        print(f"    Metrics: accuracy={v2.metrics['accuracy']}, f1={v2.metrics['f1_score']}")
        
        # Переход в production
        print("\n🚀 Model Lifecycle...")
        
        platform.registry.transition_stage(v1.version_id, ModelStatus.STAGING)
        print(f"  ✓ {v1.version} → STAGING")
        
        platform.registry.transition_stage(v1.version_id, ModelStatus.PRODUCTION)
        print(f"  ✓ {v1.version} → PRODUCTION")
        
        # Получение production версии
        prod_ver = platform.registry.get_production_version(fraud_model.model_id)
        print(f"  ✓ Current production: {prod_ver.version}")
        
        # Model Deployment
        print("\n📡 Model Deployment...")
        
        endpoint = await platform.deployer.deploy(
            fraud_model.model_id,
            v1.version_id,
            name="fraud-detector-prod",
            replicas=3,
            cpu_limit="2",
            memory_limit="4Gi"
        )
        print(f"  ✓ Deployed endpoint: {endpoint.name}")
        print(f"    URL: {endpoint.url}")
        print(f"    Status: {endpoint.status.value}")
        print(f"    Replicas: {endpoint.replicas}")
        
        # Predictions
        print("\n🔮 Making Predictions...")
        
        test_inputs = [
            {"user_age": 25, "transaction_amount": 1500, "merchant_type": "online"},
            {"user_age": 60, "transaction_amount": 50, "merchant_type": "retail"},
            {"user_age": 18, "transaction_amount": 9999, "merchant_type": "online"},
        ]
        
        for i, input_data in enumerate(test_inputs):
            result = await platform.deployer.predict(endpoint.endpoint_id, input_data)
            print(f"  Prediction {i+1}: {result}")
            
        print(f"\n  Endpoint Metrics:")
        print(f"    Total requests: {endpoint.requests_total}")
        print(f"    Success rate: {endpoint.requests_success/endpoint.requests_total*100:.1f}%")
        print(f"    Avg latency: {endpoint.avg_latency_ms:.2f}ms")
        
        # A/B Testing
        print("\n🔬 A/B Testing...")
        
        # Развёртывание второй версии
        endpoint_v2 = await platform.deployer.deploy(
            fraud_model.model_id,
            v2.version_id,
            name="fraud-detector-canary",
            replicas=1
        )
        print(f"  ✓ Deployed canary: {endpoint_v2.name}")
        
        # Создание A/B теста
        ab_test = platform.deployer.create_ab_test(
            "fraud_model_v1_vs_v2",
            variants={v1.version_id: 80, v2.version_id: 20},
            primary_metric="accuracy"
        )
        print(f"  ✓ Created A/B test: {ab_test.name}")
        print(f"    Variants: v1={ab_test.variants[v1.version_id]}%, v2={ab_test.variants[v2.version_id]}%")
        
        # Симуляция маршрутизации
        routing_counts = defaultdict(int)
        for _ in range(100):
            routed_to = platform.deployer.route_request(ab_test.test_id)
            routing_counts[routed_to] += 1
            
        print("\n  Traffic Distribution (100 requests):")
        for version_id, count in routing_counts.items():
            version = fraud_model.versions.get(version_id)
            print(f"    {version.version}: {count}%")
            
        # Model Lineage
        print("\n📊 Model Lineage:")
        print(f"  Model: {fraud_model.name}")
        print(f"  └─ Version: {v1.version}")
        print(f"     ├─ Experiment: {exp1.name}")
        print(f"     ├─ Framework: {v1.framework.value}")
        print(f"     ├─ Metrics: accuracy={v1.metrics['accuracy']}")
        print(f"     └─ Deployment: {endpoint.name}")
        
        # Platform Statistics
        print("\n📈 Platform Statistics:")
        stats = platform.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
        # Все модели
        print("\n📋 All Models:")
        for model in platform.registry.models.values():
            prod = model.versions.get(model.production_version)
            print(f"  • {model.name}")
            print(f"    Versions: {len(model.versions)}")
            print(f"    Production: {prod.version if prod else 'None'}")
            
        # Все endpoints
        print("\n📡 All Endpoints:")
        for ep in platform.deployer.endpoints.values():
            print(f"  • {ep.name}")
            print(f"    Status: {ep.status.value}")
            print(f"    Requests: {ep.requests_total}")
            
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("MLOps Platform initialized!")
    print("=" * 60)
