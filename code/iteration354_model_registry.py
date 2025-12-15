#!/usr/bin/env python3
"""
Server Init - Iteration 354: Model Registry Platform
Платформа реестра ML моделей

Функционал:
- Model Registration - регистрация моделей
- Model Versioning - версионирование моделей
- Model Stages - стадии моделей (staging, production)
- Model Artifacts - артефакты моделей
- Model Lineage - линия моделей
- Model Metadata - метаданные моделей
- Model Comparison - сравнение моделей
- Model Deployment - развёртывание моделей
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import json


class ModelFramework(Enum):
    """ML фреймворк"""
    SKLEARN = "sklearn"
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    CATBOOST = "catboost"
    ONNX = "onnx"
    CUSTOM = "custom"


class ModelStage(Enum):
    """Стадия модели"""
    NONE = "none"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"


class ModelStatus(Enum):
    """Статус модели"""
    DRAFT = "draft"
    REGISTERED = "registered"
    DEPLOYED = "deployed"
    RETIRED = "retired"


class ArtifactType(Enum):
    """Тип артефакта"""
    MODEL = "model"
    WEIGHTS = "weights"
    CONFIG = "config"
    PREPROCESSING = "preprocessing"
    REQUIREMENTS = "requirements"
    DOCKERFILE = "dockerfile"


class MetricType(Enum):
    """Тип метрики"""
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    AUC_ROC = "auc_roc"
    MSE = "mse"
    MAE = "mae"
    RMSE = "rmse"
    R2 = "r2"
    CUSTOM = "custom"


class DeploymentStatus(Enum):
    """Статус развёртывания"""
    PENDING = "pending"
    DEPLOYING = "deploying"
    RUNNING = "running"
    FAILED = "failed"
    STOPPED = "stopped"


@dataclass
class RegisteredModel:
    """Зарегистрированная модель"""
    model_id: str
    name: str
    
    # Description
    description: str = ""
    
    # Owner
    owner: str = ""
    team: str = ""
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Latest version
    latest_version: int = 0
    
    # Versions count
    version_count: int = 0
    
    # Status
    status: ModelStatus = ModelStatus.DRAFT
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


@dataclass
class ModelVersion:
    """Версия модели"""
    version_id: str
    model_id: str
    version: int
    
    # Framework
    framework: ModelFramework = ModelFramework.SKLEARN
    framework_version: str = ""
    
    # Stage
    stage: ModelStage = ModelStage.NONE
    
    # Source
    source_run_id: str = ""
    source_experiment_id: str = ""
    
    # Artifact path
    artifact_path: str = ""
    
    # Model signature
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    
    # Metrics
    metrics: Dict[str, float] = field(default_factory=dict)
    
    # Parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Description
    description: str = ""
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Status
    status: ModelStatus = ModelStatus.REGISTERED
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


@dataclass
class ModelArtifact:
    """Артефакт модели"""
    artifact_id: str
    version_id: str
    
    # Type
    artifact_type: ArtifactType = ArtifactType.MODEL
    
    # File info
    file_name: str = ""
    file_path: str = ""
    file_size: int = 0
    checksum: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ModelMetric:
    """Метрика модели"""
    metric_id: str
    version_id: str
    
    # Metric
    metric_type: MetricType = MetricType.ACCURACY
    metric_name: str = ""
    value: float = 0.0
    
    # Dataset
    dataset_name: str = ""
    dataset_version: str = ""
    
    # Timestamps
    computed_at: datetime = field(default_factory=datetime.now)


@dataclass
class ModelLineage:
    """Линия модели"""
    lineage_id: str
    version_id: str
    
    # Training data
    training_data_sources: List[str] = field(default_factory=list)
    
    # Feature store
    feature_group_ids: List[str] = field(default_factory=list)
    
    # Parent model
    parent_version_id: str = ""
    
    # Code version
    code_repository: str = ""
    code_commit: str = ""
    
    # Environment
    environment_id: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ModelExperiment:
    """Эксперимент"""
    experiment_id: str
    name: str
    
    # Description
    description: str = ""
    
    # Artifact location
    artifact_location: str = ""
    
    # Lifecycle stage
    lifecycle_stage: str = "active"
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ExperimentRun:
    """Запуск эксперимента"""
    run_id: str
    experiment_id: str
    
    # Name
    run_name: str = ""
    
    # Status
    status: str = "RUNNING"  # RUNNING, FINISHED, FAILED, KILLED
    
    # Metrics
    metrics: Dict[str, float] = field(default_factory=dict)
    
    # Parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Artifact URI
    artifact_uri: str = ""
    
    # Timestamps
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None


@dataclass
class ModelDeployment:
    """Развёртывание модели"""
    deployment_id: str
    version_id: str
    
    # Deployment name
    name: str = ""
    
    # Environment
    environment: str = "production"  # production, staging, development
    
    # Endpoint
    endpoint_name: str = ""
    endpoint_url: str = ""
    
    # Config
    instance_type: str = ""
    instance_count: int = 1
    
    # Traffic
    traffic_percent: int = 100
    
    # Status
    status: DeploymentStatus = DeploymentStatus.PENDING
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    deployed_at: Optional[datetime] = None


@dataclass
class ModelEndpoint:
    """Эндпоинт модели"""
    endpoint_id: str
    name: str
    
    # URL
    url: str = ""
    
    # Deployments
    deployment_ids: List[str] = field(default_factory=list)
    
    # Status
    status: str = "creating"  # creating, in_service, updating, failed, deleting
    
    # Config
    auto_scaling: bool = False
    min_instances: int = 1
    max_instances: int = 10
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


@dataclass
class ModelComparison:
    """Сравнение моделей"""
    comparison_id: str
    name: str
    
    # Versions to compare
    version_ids: List[str] = field(default_factory=list)
    
    # Metrics
    metrics_to_compare: List[str] = field(default_factory=list)
    
    # Results
    results: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Winner
    winner_version_id: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ModelApproval:
    """Одобрение модели"""
    approval_id: str
    version_id: str
    
    # Target stage
    target_stage: ModelStage = ModelStage.PRODUCTION
    
    # Approver
    approver: str = ""
    
    # Status
    status: str = "pending"  # pending, approved, rejected
    
    # Comments
    comments: str = ""
    
    # Timestamps
    requested_at: datetime = field(default_factory=datetime.now)
    decided_at: Optional[datetime] = None


@dataclass
class ModelAlert:
    """Алерт модели"""
    alert_id: str
    version_id: str
    
    # Alert type
    alert_type: str = ""  # drift, performance, latency
    
    # Message
    message: str = ""
    
    # Severity
    severity: str = "warning"  # info, warning, critical
    
    # Status
    is_resolved: bool = False
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


@dataclass
class ModelRegistryMetrics:
    """Метрики реестра моделей"""
    metrics_id: str
    
    # Models
    total_models: int = 0
    total_versions: int = 0
    
    # Stages
    staging_versions: int = 0
    production_versions: int = 0
    
    # Deployments
    active_deployments: int = 0
    
    # Experiments
    total_experiments: int = 0
    total_runs: int = 0
    
    # Timestamps
    collected_at: datetime = field(default_factory=datetime.now)


class ModelRegistryPlatform:
    """Платформа реестра моделей"""
    
    def __init__(self, registry_name: str = "ml-registry"):
        self.registry_name = registry_name
        self.models: Dict[str, RegisteredModel] = {}
        self.versions: Dict[str, ModelVersion] = {}
        self.artifacts: Dict[str, ModelArtifact] = {}
        self.model_metrics: Dict[str, ModelMetric] = {}
        self.lineages: Dict[str, ModelLineage] = {}
        self.experiments: Dict[str, ModelExperiment] = {}
        self.runs: Dict[str, ExperimentRun] = {}
        self.deployments: Dict[str, ModelDeployment] = {}
        self.endpoints: Dict[str, ModelEndpoint] = {}
        self.comparisons: Dict[str, ModelComparison] = {}
        self.approvals: Dict[str, ModelApproval] = {}
        self.alerts: Dict[str, ModelAlert] = {}
        self.metrics: Dict[str, ModelRegistryMetrics] = {}
        
    async def register_model(self, name: str,
                            description: str = "",
                            owner: str = "",
                            team: str = "",
                            tags: List[str] = None) -> RegisteredModel:
        """Регистрация модели"""
        model = RegisteredModel(
            model_id=f"mod_{uuid.uuid4().hex[:12]}",
            name=name,
            description=description,
            owner=owner,
            team=team,
            tags=tags or [],
            status=ModelStatus.REGISTERED
        )
        
        self.models[model.model_id] = model
        return model
        
    async def create_version(self, model_id: str,
                            framework: ModelFramework,
                            framework_version: str,
                            artifact_path: str,
                            input_schema: Dict[str, Any] = None,
                            output_schema: Dict[str, Any] = None,
                            metrics: Dict[str, float] = None,
                            parameters: Dict[str, Any] = None,
                            description: str = "",
                            tags: List[str] = None,
                            source_run_id: str = "",
                            source_experiment_id: str = "") -> Optional[ModelVersion]:
        """Создание версии модели"""
        model = self.models.get(model_id)
        if not model:
            return None
            
        version_num = model.latest_version + 1
        
        version = ModelVersion(
            version_id=f"ver_{uuid.uuid4().hex[:8]}",
            model_id=model_id,
            version=version_num,
            framework=framework,
            framework_version=framework_version,
            artifact_path=artifact_path,
            input_schema=input_schema or {},
            output_schema=output_schema or {},
            metrics=metrics or {},
            parameters=parameters or {},
            description=description,
            tags=tags or [],
            source_run_id=source_run_id,
            source_experiment_id=source_experiment_id
        )
        
        self.versions[version.version_id] = version
        model.latest_version = version_num
        model.version_count += 1
        model.updated_at = datetime.now()
        
        return version
        
    async def transition_stage(self, version_id: str,
                              target_stage: ModelStage,
                              archive_existing: bool = True) -> Optional[ModelVersion]:
        """Переход на стадию"""
        version = self.versions.get(version_id)
        if not version:
            return None
            
        # Archive existing versions in target stage
        if archive_existing and target_stage == ModelStage.PRODUCTION:
            for v in self.versions.values():
                if v.model_id == version.model_id and v.stage == ModelStage.PRODUCTION:
                    v.stage = ModelStage.ARCHIVED
                    v.updated_at = datetime.now()
                    
        version.stage = target_stage
        version.updated_at = datetime.now()
        
        return version
        
    async def add_artifact(self, version_id: str,
                          artifact_type: ArtifactType,
                          file_name: str,
                          file_path: str,
                          file_size: int = 0,
                          checksum: str = "") -> Optional[ModelArtifact]:
        """Добавление артефакта"""
        version = self.versions.get(version_id)
        if not version:
            return None
            
        artifact = ModelArtifact(
            artifact_id=f"art_{uuid.uuid4().hex[:8]}",
            version_id=version_id,
            artifact_type=artifact_type,
            file_name=file_name,
            file_path=file_path,
            file_size=file_size,
            checksum=checksum or uuid.uuid4().hex
        )
        
        self.artifacts[artifact.artifact_id] = artifact
        return artifact
        
    async def log_metric(self, version_id: str,
                        metric_type: MetricType,
                        value: float,
                        dataset_name: str = "",
                        dataset_version: str = "") -> Optional[ModelMetric]:
        """Логирование метрики"""
        version = self.versions.get(version_id)
        if not version:
            return None
            
        metric = ModelMetric(
            metric_id=f"met_{uuid.uuid4().hex[:8]}",
            version_id=version_id,
            metric_type=metric_type,
            metric_name=metric_type.value,
            value=value,
            dataset_name=dataset_name,
            dataset_version=dataset_version
        )
        
        self.model_metrics[metric.metric_id] = metric
        version.metrics[metric_type.value] = value
        
        return metric
        
    async def add_lineage(self, version_id: str,
                         training_data_sources: List[str] = None,
                         feature_group_ids: List[str] = None,
                         parent_version_id: str = "",
                         code_repository: str = "",
                         code_commit: str = "") -> Optional[ModelLineage]:
        """Добавление линии модели"""
        version = self.versions.get(version_id)
        if not version:
            return None
            
        lineage = ModelLineage(
            lineage_id=f"lin_{uuid.uuid4().hex[:8]}",
            version_id=version_id,
            training_data_sources=training_data_sources or [],
            feature_group_ids=feature_group_ids or [],
            parent_version_id=parent_version_id,
            code_repository=code_repository,
            code_commit=code_commit
        )
        
        self.lineages[lineage.lineage_id] = lineage
        return lineage
        
    async def create_experiment(self, name: str,
                               description: str = "",
                               artifact_location: str = "",
                               tags: Dict[str, str] = None) -> ModelExperiment:
        """Создание эксперимента"""
        experiment = ModelExperiment(
            experiment_id=f"exp_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            artifact_location=artifact_location or f"s3://{self.registry_name}/experiments/{name}",
            tags=tags or {}
        )
        
        self.experiments[experiment.experiment_id] = experiment
        return experiment
        
    async def start_run(self, experiment_id: str,
                       run_name: str = "",
                       parameters: Dict[str, Any] = None,
                       tags: Dict[str, str] = None) -> Optional[ExperimentRun]:
        """Запуск эксперимента"""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            return None
            
        run = ExperimentRun(
            run_id=f"run_{uuid.uuid4().hex[:8]}",
            experiment_id=experiment_id,
            run_name=run_name or f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            parameters=parameters or {},
            tags=tags or {},
            artifact_uri=f"{experiment.artifact_location}/runs/{uuid.uuid4().hex[:8]}"
        )
        
        self.runs[run.run_id] = run
        return run
        
    async def finish_run(self, run_id: str,
                        status: str = "FINISHED",
                        metrics: Dict[str, float] = None) -> Optional[ExperimentRun]:
        """Завершение запуска"""
        run = self.runs.get(run_id)
        if not run:
            return None
            
        run.status = status
        run.end_time = datetime.now()
        if metrics:
            run.metrics.update(metrics)
            
        return run
        
    async def deploy_model(self, version_id: str,
                          name: str,
                          environment: str = "production",
                          endpoint_name: str = "",
                          instance_type: str = "ml.m5.large",
                          instance_count: int = 1,
                          traffic_percent: int = 100) -> Optional[ModelDeployment]:
        """Развёртывание модели"""
        version = self.versions.get(version_id)
        if not version:
            return None
            
        deployment = ModelDeployment(
            deployment_id=f"dep_{uuid.uuid4().hex[:8]}",
            version_id=version_id,
            name=name,
            environment=environment,
            endpoint_name=endpoint_name,
            instance_type=instance_type,
            instance_count=instance_count,
            traffic_percent=traffic_percent,
            status=DeploymentStatus.DEPLOYING
        )
        
        self.deployments[deployment.deployment_id] = deployment
        
        # Simulate deployment
        await asyncio.sleep(0.01)
        deployment.status = DeploymentStatus.RUNNING
        deployment.deployed_at = datetime.now()
        deployment.endpoint_url = f"https://api.{self.registry_name}.ml/{endpoint_name}"
        
        version.status = ModelStatus.DEPLOYED
        version.updated_at = datetime.now()
        
        return deployment
        
    async def create_endpoint(self, name: str,
                             auto_scaling: bool = False,
                             min_instances: int = 1,
                             max_instances: int = 10) -> ModelEndpoint:
        """Создание эндпоинта"""
        endpoint = ModelEndpoint(
            endpoint_id=f"ep_{uuid.uuid4().hex[:8]}",
            name=name,
            url=f"https://api.{self.registry_name}.ml/{name}",
            auto_scaling=auto_scaling,
            min_instances=min_instances,
            max_instances=max_instances,
            status="in_service"
        )
        
        self.endpoints[endpoint.endpoint_id] = endpoint
        return endpoint
        
    async def compare_models(self, name: str,
                            version_ids: List[str],
                            metrics_to_compare: List[str]) -> ModelComparison:
        """Сравнение моделей"""
        results = {}
        
        for vid in version_ids:
            version = self.versions.get(vid)
            if version:
                results[vid] = {}
                for metric in metrics_to_compare:
                    results[vid][metric] = version.metrics.get(metric, 0.0)
                    
        # Find winner (highest first metric)
        winner_id = ""
        best_score = -float("inf")
        if metrics_to_compare and results:
            first_metric = metrics_to_compare[0]
            for vid, metrics in results.items():
                if metrics.get(first_metric, 0) > best_score:
                    best_score = metrics.get(first_metric, 0)
                    winner_id = vid
                    
        comparison = ModelComparison(
            comparison_id=f"cmp_{uuid.uuid4().hex[:8]}",
            name=name,
            version_ids=version_ids,
            metrics_to_compare=metrics_to_compare,
            results=results,
            winner_version_id=winner_id
        )
        
        self.comparisons[comparison.comparison_id] = comparison
        return comparison
        
    async def request_approval(self, version_id: str,
                              target_stage: ModelStage = ModelStage.PRODUCTION,
                              comments: str = "") -> Optional[ModelApproval]:
        """Запрос одобрения"""
        version = self.versions.get(version_id)
        if not version:
            return None
            
        approval = ModelApproval(
            approval_id=f"apr_{uuid.uuid4().hex[:8]}",
            version_id=version_id,
            target_stage=target_stage,
            comments=comments
        )
        
        self.approvals[approval.approval_id] = approval
        return approval
        
    async def approve(self, approval_id: str,
                     approver: str,
                     comments: str = "") -> Optional[ModelApproval]:
        """Одобрение"""
        approval = self.approvals.get(approval_id)
        if not approval:
            return None
            
        approval.status = "approved"
        approval.approver = approver
        approval.comments = comments
        approval.decided_at = datetime.now()
        
        # Transition to target stage
        await self.transition_stage(approval.version_id, approval.target_stage)
        
        return approval
        
    async def create_alert(self, version_id: str,
                          alert_type: str,
                          message: str,
                          severity: str = "warning") -> Optional[ModelAlert]:
        """Создание алерта"""
        version = self.versions.get(version_id)
        if not version:
            return None
            
        alert = ModelAlert(
            alert_id=f"alr_{uuid.uuid4().hex[:8]}",
            version_id=version_id,
            alert_type=alert_type,
            message=message,
            severity=severity
        )
        
        self.alerts[alert.alert_id] = alert
        return alert
        
    async def collect_metrics(self) -> ModelRegistryMetrics:
        """Сбор метрик"""
        staging = sum(1 for v in self.versions.values() if v.stage == ModelStage.STAGING)
        production = sum(1 for v in self.versions.values() if v.stage == ModelStage.PRODUCTION)
        active_deployments = sum(1 for d in self.deployments.values() if d.status == DeploymentStatus.RUNNING)
        
        metrics = ModelRegistryMetrics(
            metrics_id=f"mrm_{uuid.uuid4().hex[:8]}",
            total_models=len(self.models),
            total_versions=len(self.versions),
            staging_versions=staging,
            production_versions=production,
            active_deployments=active_deployments,
            total_experiments=len(self.experiments),
            total_runs=len(self.runs)
        )
        
        self.metrics[metrics.metrics_id] = metrics
        return metrics
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_models = len(self.models)
        total_versions = len(self.versions)
        
        versions_by_stage = {}
        for stage in ModelStage:
            versions_by_stage[stage.value] = sum(1 for v in self.versions.values() if v.stage == stage)
            
        versions_by_framework = {}
        for framework in ModelFramework:
            versions_by_framework[framework.value] = sum(1 for v in self.versions.values() if v.framework == framework)
            
        total_experiments = len(self.experiments)
        total_runs = len(self.runs)
        successful_runs = sum(1 for r in self.runs.values() if r.status == "FINISHED")
        
        total_deployments = len(self.deployments)
        active_deployments = sum(1 for d in self.deployments.values() if d.status == DeploymentStatus.RUNNING)
        
        total_artifacts = len(self.artifacts)
        
        pending_approvals = sum(1 for a in self.approvals.values() if a.status == "pending")
        active_alerts = sum(1 for a in self.alerts.values() if not a.is_resolved)
        
        return {
            "total_models": total_models,
            "total_versions": total_versions,
            "versions_by_stage": versions_by_stage,
            "versions_by_framework": versions_by_framework,
            "total_experiments": total_experiments,
            "total_runs": total_runs,
            "successful_runs": successful_runs,
            "total_deployments": total_deployments,
            "active_deployments": active_deployments,
            "total_artifacts": total_artifacts,
            "pending_approvals": pending_approvals,
            "active_alerts": active_alerts
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 354: Model Registry Platform")
    print("=" * 60)
    
    platform = ModelRegistryPlatform(registry_name="enterprise-ml")
    print("✓ Model Registry Platform initialized")
    
    # Register Models
    print("\n📦 Registering Models...")
    
    models_data = [
        ("customer_churn_predictor", "Predicts customer churn probability", "ml-team", "platform", ["churn", "classification", "customer"]),
        ("product_recommender", "Product recommendation model", "recommender-team", "recommendations", ["recommendation", "collaborative-filtering"]),
        ("fraud_detector", "Real-time fraud detection", "risk-team", "fraud", ["fraud", "classification", "real-time"]),
        ("demand_forecaster", "Demand forecasting model", "supply-chain", "forecasting", ["forecasting", "time-series"]),
        ("sentiment_analyzer", "NLP sentiment analysis", "nlp-team", "nlp", ["nlp", "sentiment", "classification"]),
        ("image_classifier", "Product image classification", "cv-team", "vision", ["cv", "classification", "images"]),
        ("price_optimizer", "Dynamic pricing optimization", "pricing-team", "revenue", ["pricing", "optimization"]),
        ("click_predictor", "CTR prediction model", "ads-team", "advertising", ["ctr", "prediction", "ads"])
    ]
    
    models = []
    for name, desc, owner, team, tags in models_data:
        m = await platform.register_model(name, desc, owner, team, tags)
        models.append(m)
        print(f"  📦 {name}")
        
    # Create Model Versions
    print("\n📌 Creating Model Versions...")
    
    versions_data = [
        (models[0].model_id, ModelFramework.XGBOOST, "1.7.0", {"accuracy": 0.92, "f1_score": 0.89, "auc_roc": 0.95}, {"max_depth": 6, "learning_rate": 0.1}),
        (models[0].model_id, ModelFramework.LIGHTGBM, "3.3.0", {"accuracy": 0.94, "f1_score": 0.91, "auc_roc": 0.96}, {"num_leaves": 31, "learning_rate": 0.05}),
        (models[1].model_id, ModelFramework.PYTORCH, "2.0.0", {"accuracy": 0.85, "precision": 0.82, "recall": 0.88}, {"embedding_dim": 128, "hidden_size": 256}),
        (models[2].model_id, ModelFramework.SKLEARN, "1.2.0", {"accuracy": 0.98, "precision": 0.97, "recall": 0.99}, {"n_estimators": 100}),
        (models[2].model_id, ModelFramework.CATBOOST, "1.1.0", {"accuracy": 0.985, "precision": 0.98, "recall": 0.99}, {"iterations": 500}),
        (models[3].model_id, ModelFramework.TENSORFLOW, "2.12.0", {"mae": 12.5, "rmse": 18.2, "r2": 0.91}, {"lstm_units": 64, "dense_units": 32}),
        (models[4].model_id, ModelFramework.PYTORCH, "2.0.0", {"accuracy": 0.88, "f1_score": 0.86}, {"model_name": "bert-base", "max_length": 512}),
        (models[5].model_id, ModelFramework.ONNX, "1.14.0", {"accuracy": 0.92, "top5_accuracy": 0.99}, {"backbone": "resnet50"}),
        (models[6].model_id, ModelFramework.SKLEARN, "1.2.0", {"mae": 2.3, "r2": 0.87}, {"model_type": "elasticnet"}),
        (models[7].model_id, ModelFramework.XGBOOST, "1.7.0", {"auc_roc": 0.82, "logloss": 0.42}, {"max_depth": 5})
    ]
    
    versions = []
    for mid, framework, fver, metrics, params in versions_data:
        v = await platform.create_version(
            mid, framework, fver,
            f"s3://ml-artifacts/models/{mid}/{uuid.uuid4().hex[:8]}",
            {"features": ["f1", "f2", "f3"]},
            {"prediction": "float"},
            metrics, params,
            f"Version trained with {framework.value}"
        )
        if v:
            versions.append(v)
            model = platform.models.get(mid)
            print(f"  📌 {model.name} v{v.version} ({framework.value})")
            
    # Add Artifacts
    print("\n📁 Adding Artifacts...")
    
    artifact_count = 0
    for v in versions:
        # Model artifact
        await platform.add_artifact(v.version_id, ArtifactType.MODEL, "model.pkl", f"{v.artifact_path}/model.pkl", random.randint(1024*1024, 500*1024*1024))
        
        # Config
        await platform.add_artifact(v.version_id, ArtifactType.CONFIG, "config.yaml", f"{v.artifact_path}/config.yaml", random.randint(1024, 10*1024))
        
        # Requirements
        await platform.add_artifact(v.version_id, ArtifactType.REQUIREMENTS, "requirements.txt", f"{v.artifact_path}/requirements.txt", random.randint(512, 2048))
        
        artifact_count += 3
        
    print(f"  📁 Added {artifact_count} artifacts")
    
    # Transition Stages
    print("\n🎯 Transitioning Model Stages...")
    
    # Stage some models
    await platform.transition_stage(versions[1].version_id, ModelStage.STAGING)
    await platform.transition_stage(versions[4].version_id, ModelStage.STAGING)
    await platform.transition_stage(versions[2].version_id, ModelStage.STAGING)
    
    # Production
    await platform.transition_stage(versions[0].version_id, ModelStage.PRODUCTION)
    await platform.transition_stage(versions[3].version_id, ModelStage.PRODUCTION)
    await platform.transition_stage(versions[5].version_id, ModelStage.PRODUCTION)
    
    print("  🎯 Staged and promoted models")
    
    # Add Lineage
    print("\n🔗 Adding Model Lineage...")
    
    for v in versions:
        await platform.add_lineage(
            v.version_id,
            [f"s3://data-lake/training/{uuid.uuid4().hex[:8]}"],
            [f"fg_{uuid.uuid4().hex[:8]}"],
            "",
            "github.com/ml-team/models",
            uuid.uuid4().hex[:7]
        )
        
    print(f"  🔗 Added lineage for {len(versions)} versions")
    
    # Create Experiments
    print("\n🧪 Creating Experiments...")
    
    experiments_data = [
        ("churn_hyperparameter_tuning", "Hyperparameter search for churn model", {"type": "hpo", "model": "xgboost"}),
        ("recommender_architecture_search", "Neural architecture search for recommender", {"type": "nas", "model": "pytorch"}),
        ("fraud_feature_engineering", "Feature engineering experiments", {"type": "feature", "model": "catboost"}),
        ("demand_model_comparison", "Compare different forecasting approaches", {"type": "comparison", "model": "lstm"})
    ]
    
    experiments = []
    for name, desc, tags in experiments_data:
        e = await platform.create_experiment(name, desc, tags=tags)
        experiments.append(e)
        print(f"  🧪 {name}")
        
    # Start Experiment Runs
    print("\n🏃 Running Experiments...")
    
    runs = []
    for exp in experiments:
        for i in range(random.randint(3, 7)):
            r = await platform.start_run(
                exp.experiment_id,
                f"run_{i+1}",
                {"learning_rate": random.uniform(0.001, 0.1), "batch_size": random.choice([16, 32, 64, 128])},
                {"experiment_type": "training"}
            )
            if r:
                # Finish run with metrics
                await platform.finish_run(r.run_id, "FINISHED", {
                    "accuracy": random.uniform(0.8, 0.99),
                    "loss": random.uniform(0.01, 0.5)
                })
                runs.append(r)
                
    print(f"  🏃 Completed {len(runs)} experiment runs")
    
    # Deploy Models
    print("\n🚀 Deploying Models...")
    
    deployments_data = [
        (versions[0].version_id, "churn-predictor-prod", "production", "ml.m5.large", 2),
        (versions[3].version_id, "fraud-detector-prod", "production", "ml.c5.xlarge", 4),
        (versions[5].version_id, "demand-forecaster-prod", "production", "ml.m5.xlarge", 2),
        (versions[1].version_id, "churn-predictor-staging", "staging", "ml.t3.medium", 1),
        (versions[4].version_id, "fraud-detector-staging", "staging", "ml.t3.medium", 1)
    ]
    
    deployments = []
    for vid, name, env, instance, count in deployments_data:
        d = await platform.deploy_model(vid, name, env, name, instance, count)
        if d:
            deployments.append(d)
            print(f"  🚀 {name} ({env})")
            
    # Create Endpoints
    print("\n🔌 Creating Endpoints...")
    
    endpoints_data = [
        ("churn-predictor", True, 2, 10),
        ("fraud-detector", True, 4, 20),
        ("demand-forecaster", False, 2, 8)
    ]
    
    endpoints = []
    for name, auto_scale, min_inst, max_inst in endpoints_data:
        ep = await platform.create_endpoint(name, auto_scale, min_inst, max_inst)
        endpoints.append(ep)
        print(f"  🔌 {name}")
        
    # Compare Models
    print("\n📊 Comparing Models...")
    
    # Compare churn model versions
    comparison = await platform.compare_models(
        "churn_model_comparison",
        [versions[0].version_id, versions[1].version_id],
        ["accuracy", "f1_score", "auc_roc"]
    )
    print(f"  📊 Compared {len(comparison.version_ids)} versions, winner: v{platform.versions.get(comparison.winner_version_id).version if comparison.winner_version_id else 'N/A'}")
    
    # Request Approvals
    print("\n✅ Requesting Approvals...")
    
    approvals_data = [
        (versions[1].version_id, ModelStage.PRODUCTION, "Improved accuracy, ready for production"),
        (versions[4].version_id, ModelStage.PRODUCTION, "Better precision for fraud detection")
    ]
    
    approvals = []
    for vid, stage, comments in approvals_data:
        a = await platform.request_approval(vid, stage, comments)
        if a:
            approvals.append(a)
            
    # Approve one
    await platform.approve(approvals[0].approval_id, "ml-lead@company.com", "Approved after review")
    
    print(f"  ✅ Created {len(approvals)} approval requests")
    
    # Create Alerts
    print("\n⚠️ Creating Alerts...")
    
    alerts_data = [
        (versions[0].version_id, "drift", "Feature drift detected in customer_tenure", "warning"),
        (versions[3].version_id, "performance", "Model accuracy dropped below threshold", "critical"),
        (versions[5].version_id, "latency", "Inference latency increased", "warning")
    ]
    
    alerts = []
    for vid, atype, msg, severity in alerts_data:
        a = await platform.create_alert(vid, atype, msg, severity)
        if a:
            alerts.append(a)
            print(f"  ⚠️ {atype}: {msg[:40]}...")
            
    # Collect Metrics
    registry_metrics = await platform.collect_metrics()
    
    # Models Dashboard
    print("\n📦 Registered Models:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Model Name                      │ Owner           │ Team            │ Versions │ Latest │ Status      │ Tags                                                                                                                                                                                                                                                                                                                   │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for m in models:
        name = m.name[:31].ljust(31)
        owner = m.owner[:15].ljust(15)
        team = m.team[:15].ljust(15)
        vers = str(m.version_count).ljust(8)
        latest = f"v{m.latest_version}".ljust(6)
        status = m.status.value[:11].ljust(11)
        tags = ", ".join(m.tags[:3])[:196]
        tags = tags.ljust(196)
        
        print(f"  │ {name} │ {owner} │ {team} │ {vers} │ {latest} │ {status} │ {tags} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Versions Dashboard
    print("\n📌 Model Versions:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Model                           │ Version │ Framework   │ Stage        │ Accuracy │ F1 Score │ AUC-ROC  │ Status      │ Created                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for v in versions:
        model = platform.models.get(v.model_id)
        model_name = model.name if model else "Unknown"
        model_name = model_name[:31].ljust(31)
        version = f"v{v.version}".ljust(7)
        framework = v.framework.value[:11].ljust(11)
        stage = v.stage.value[:12].ljust(12)
        acc = f"{v.metrics.get('accuracy', 0.0):.3f}".ljust(8)
        f1 = f"{v.metrics.get('f1_score', 0.0):.3f}".ljust(8)
        auc = f"{v.metrics.get('auc_roc', 0.0):.3f}".ljust(8)
        status = v.status.value[:11].ljust(11)
        created = v.created_at.strftime("%Y-%m-%d %H:%M")
        created = created.ljust(276)
        
        print(f"  │ {model_name} │ {version} │ {framework} │ {stage} │ {acc} │ {f1} │ {auc} │ {status} │ {created} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Deployments Dashboard
    print("\n🚀 Active Deployments:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Deployment Name                 │ Environment │ Instance Type │ Instances │ Traffic │ Status    │ Endpoint URL                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for d in deployments:
        name = d.name[:31].ljust(31)
        env = d.environment[:11].ljust(11)
        inst_type = d.instance_type[:13].ljust(13)
        instances = str(d.instance_count).ljust(9)
        traffic = f"{d.traffic_percent}%".ljust(7)
        status = d.status.value[:9].ljust(9)
        url = d.endpoint_url[:350]
        url = url.ljust(350)
        
        print(f"  │ {name} │ {env} │ {inst_type} │ {instances} │ {traffic} │ {status} │ {url} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Models: {stats['total_models']}, Versions: {stats['total_versions']}")
    print(f"  Staging: {stats['versions_by_stage'].get('staging', 0)}, Production: {stats['versions_by_stage'].get('production', 0)}")
    print(f"  Experiments: {stats['total_experiments']}, Runs: {stats['successful_runs']}/{stats['total_runs']} successful")
    print(f"  Deployments: {stats['active_deployments']}/{stats['total_deployments']} active")
    print(f"  Pending Approvals: {stats['pending_approvals']}, Active Alerts: {stats['active_alerts']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                      Model Registry Platform                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Registered Models:             {stats['total_models']:>12}                      │")
    print(f"│ Total Versions:                {stats['total_versions']:>12}                      │")
    print(f"│ Production Versions:           {stats['versions_by_stage'].get('production', 0):>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Experiments:             {stats['total_experiments']:>12}                      │")
    print(f"│ Experiment Runs:               {stats['total_runs']:>12}                      │")
    print(f"│ Successful Runs:               {stats['successful_runs']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Active Deployments:            {stats['active_deployments']:>12}                      │")
    print(f"│ Total Artifacts:               {stats['total_artifacts']:>12}                      │")
    print(f"│ Pending Approvals:             {stats['pending_approvals']:>12}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Model Registry Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
