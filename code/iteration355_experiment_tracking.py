#!/usr/bin/env python3
"""
Server Init - Iteration 355: Experiment Tracking Platform
Платформа отслеживания ML экспериментов

Функционал:
- Experiment Management - управление экспериментами
- Run Tracking - отслеживание запусков
- Metric Logging - логирование метрик
- Parameter Tracking - отслеживание параметров
- Artifact Management - управление артефактами
- Comparison Tools - инструменты сравнения
- Visualization - визуализация
- Collaboration - совместная работа
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import json


class RunStatus(Enum):
    """Статус запуска"""
    SCHEDULED = "scheduled"
    RUNNING = "running"
    FINISHED = "finished"
    FAILED = "failed"
    KILLED = "killed"


class ExperimentLifecycle(Enum):
    """Жизненный цикл эксперимента"""
    ACTIVE = "active"
    DELETED = "deleted"
    ARCHIVED = "archived"


class MetricStep(Enum):
    """Шаг метрики"""
    EPOCH = "epoch"
    STEP = "step"
    BATCH = "batch"
    CUSTOM = "custom"


class ArtifactType(Enum):
    """Тип артефакта"""
    MODEL = "model"
    DATA = "data"
    IMAGE = "image"
    TABLE = "table"
    PLOT = "plot"
    CONFIG = "config"
    CODE = "code"
    OTHER = "other"


class VisualizationType(Enum):
    """Тип визуализации"""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    SCATTER_PLOT = "scatter_plot"
    HISTOGRAM = "histogram"
    CONFUSION_MATRIX = "confusion_matrix"
    ROC_CURVE = "roc_curve"
    CUSTOM = "custom"


@dataclass
class Project:
    """Проект"""
    project_id: str
    name: str
    
    # Description
    description: str = ""
    
    # Owner
    owner: str = ""
    team: str = ""
    
    # Visibility
    visibility: str = "private"  # private, team, public
    
    # Stats
    experiment_count: int = 0
    run_count: int = 0
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


@dataclass
class Experiment:
    """Эксперимент"""
    experiment_id: str
    project_id: str
    name: str
    
    # Description
    description: str = ""
    
    # Lifecycle
    lifecycle_stage: ExperimentLifecycle = ExperimentLifecycle.ACTIVE
    
    # Artifact location
    artifact_location: str = ""
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Stats
    run_count: int = 0
    active_runs: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: Optional[datetime] = None


@dataclass
class Run:
    """Запуск эксперимента"""
    run_id: str
    experiment_id: str
    
    # Name
    run_name: str = ""
    
    # Status
    status: RunStatus = RunStatus.SCHEDULED
    
    # User
    user_id: str = ""
    
    # Source
    source_type: str = ""  # notebook, script, job
    source_name: str = ""
    source_version: str = ""
    
    # Git info
    git_commit: str = ""
    git_branch: str = ""
    git_repo_url: str = ""
    
    # Artifact URI
    artifact_uri: str = ""
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Notes
    notes: str = ""
    
    # Timestamps
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None


@dataclass
class Parameter:
    """Параметр"""
    param_id: str
    run_id: str
    
    # Key-value
    key: str = ""
    value: str = ""
    
    # Type
    param_type: str = "string"  # string, int, float, bool
    
    # Timestamps
    logged_at: datetime = field(default_factory=datetime.now)


@dataclass
class Metric:
    """Метрика"""
    metric_id: str
    run_id: str
    
    # Key-value
    key: str = ""
    value: float = 0.0
    
    # Step
    step: int = 0
    step_type: MetricStep = MetricStep.EPOCH
    
    # Timestamps
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MetricHistory:
    """История метрики"""
    history_id: str
    run_id: str
    metric_key: str
    
    # Values
    values: List[float] = field(default_factory=list)
    steps: List[int] = field(default_factory=list)
    timestamps: List[datetime] = field(default_factory=list)
    
    # Stats
    min_value: float = 0.0
    max_value: float = 0.0
    last_value: float = 0.0


@dataclass
class Artifact:
    """Артефакт"""
    artifact_id: str
    run_id: str
    
    # Type
    artifact_type: ArtifactType = ArtifactType.OTHER
    
    # File info
    file_name: str = ""
    file_path: str = ""
    file_size: int = 0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    logged_at: datetime = field(default_factory=datetime.now)


@dataclass
class Dataset:
    """Набор данных"""
    dataset_id: str
    run_id: str
    
    # Name
    name: str = ""
    
    # Source
    source: str = ""
    version: str = ""
    
    # Profile
    row_count: int = 0
    column_count: int = 0
    size_bytes: int = 0
    
    # Schema
    schema: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    logged_at: datetime = field(default_factory=datetime.now)


@dataclass
class Model:
    """Модель"""
    model_id: str
    run_id: str
    
    # Name
    name: str = ""
    
    # Framework
    framework: str = ""
    framework_version: str = ""
    
    # Signature
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    
    # Path
    artifact_path: str = ""
    
    # Timestamps
    logged_at: datetime = field(default_factory=datetime.now)


@dataclass
class Tag:
    """Тег"""
    tag_id: str
    run_id: str
    
    # Key-value
    key: str = ""
    value: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RunComparison:
    """Сравнение запусков"""
    comparison_id: str
    name: str
    
    # Runs
    run_ids: List[str] = field(default_factory=list)
    
    # Metrics to compare
    metric_keys: List[str] = field(default_factory=list)
    
    # Results
    results: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Best run
    best_run_id: str = ""
    best_metric_key: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Visualization:
    """Визуализация"""
    viz_id: str
    run_id: str
    
    # Type
    viz_type: VisualizationType = VisualizationType.LINE_CHART
    
    # Name
    name: str = ""
    
    # Config
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Data
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Notification:
    """Уведомление"""
    notification_id: str
    run_id: str
    
    # Type
    notification_type: str = ""  # run_finished, run_failed, metric_threshold
    
    # Message
    message: str = ""
    
    # Recipients
    recipients: List[str] = field(default_factory=list)
    
    # Status
    is_sent: bool = False
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Comment:
    """Комментарий"""
    comment_id: str
    run_id: str
    
    # Author
    author: str = ""
    
    # Content
    content: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


@dataclass
class ExperimentMetrics:
    """Метрики эксперимента"""
    metrics_id: str
    
    # Projects
    total_projects: int = 0
    
    # Experiments
    total_experiments: int = 0
    active_experiments: int = 0
    
    # Runs
    total_runs: int = 0
    running_runs: int = 0
    finished_runs: int = 0
    failed_runs: int = 0
    
    # Metrics logged
    total_metrics: int = 0
    
    # Artifacts
    total_artifacts: int = 0
    total_artifact_size: int = 0
    
    # Timestamps
    collected_at: datetime = field(default_factory=datetime.now)


class ExperimentTrackingPlatform:
    """Платформа отслеживания экспериментов"""
    
    def __init__(self, tracking_uri: str = "http://localhost:5000"):
        self.tracking_uri = tracking_uri
        self.projects: Dict[str, Project] = {}
        self.experiments: Dict[str, Experiment] = {}
        self.runs: Dict[str, Run] = {}
        self.parameters: Dict[str, Parameter] = {}
        self.metrics: Dict[str, Metric] = {}
        self.metric_histories: Dict[str, MetricHistory] = {}
        self.artifacts: Dict[str, Artifact] = {}
        self.datasets: Dict[str, Dataset] = {}
        self.models: Dict[str, Model] = {}
        self.tags: Dict[str, Tag] = {}
        self.comparisons: Dict[str, RunComparison] = {}
        self.visualizations: Dict[str, Visualization] = {}
        self.notifications: Dict[str, Notification] = {}
        self.comments: Dict[str, Comment] = {}
        self.platform_metrics: Dict[str, ExperimentMetrics] = {}
        
    async def create_project(self, name: str,
                            description: str = "",
                            owner: str = "",
                            team: str = "",
                            visibility: str = "private",
                            tags: List[str] = None) -> Project:
        """Создание проекта"""
        project = Project(
            project_id=f"proj_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            owner=owner,
            team=team,
            visibility=visibility,
            tags=tags or []
        )
        
        self.projects[project.project_id] = project
        return project
        
    async def create_experiment(self, project_id: str,
                               name: str,
                               description: str = "",
                               artifact_location: str = "",
                               tags: Dict[str, str] = None) -> Optional[Experiment]:
        """Создание эксперимента"""
        project = self.projects.get(project_id)
        if not project:
            return None
            
        experiment = Experiment(
            experiment_id=f"exp_{uuid.uuid4().hex[:8]}",
            project_id=project_id,
            name=name,
            description=description,
            artifact_location=artifact_location or f"s3://experiments/{project_id}/{name}",
            tags=tags or {}
        )
        
        self.experiments[experiment.experiment_id] = experiment
        project.experiment_count += 1
        project.updated_at = datetime.now()
        
        return experiment
        
    async def start_run(self, experiment_id: str,
                       run_name: str = "",
                       user_id: str = "",
                       source_type: str = "",
                       source_name: str = "",
                       git_commit: str = "",
                       git_branch: str = "",
                       tags: Dict[str, str] = None) -> Optional[Run]:
        """Запуск эксперимента"""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            return None
            
        run = Run(
            run_id=f"run_{uuid.uuid4().hex[:12]}",
            experiment_id=experiment_id,
            run_name=run_name or f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            status=RunStatus.RUNNING,
            user_id=user_id,
            source_type=source_type,
            source_name=source_name,
            git_commit=git_commit,
            git_branch=git_branch,
            artifact_uri=f"{experiment.artifact_location}/runs/{uuid.uuid4().hex[:8]}",
            tags=tags or {}
        )
        
        self.runs[run.run_id] = run
        experiment.run_count += 1
        experiment.active_runs += 1
        experiment.last_updated = datetime.now()
        
        # Update project
        project = self.projects.get(experiment.project_id)
        if project:
            project.run_count += 1
            
        return run
        
    async def end_run(self, run_id: str,
                     status: RunStatus = RunStatus.FINISHED) -> Optional[Run]:
        """Завершение запуска"""
        run = self.runs.get(run_id)
        if not run:
            return None
            
        run.status = status
        run.end_time = datetime.now()
        
        experiment = self.experiments.get(run.experiment_id)
        if experiment:
            experiment.active_runs -= 1
            experiment.last_updated = datetime.now()
            
        return run
        
    async def log_param(self, run_id: str,
                       key: str,
                       value: Any,
                       param_type: str = "string") -> Optional[Parameter]:
        """Логирование параметра"""
        run = self.runs.get(run_id)
        if not run:
            return None
            
        param = Parameter(
            param_id=f"param_{uuid.uuid4().hex[:8]}",
            run_id=run_id,
            key=key,
            value=str(value),
            param_type=param_type
        )
        
        self.parameters[param.param_id] = param
        return param
        
    async def log_params(self, run_id: str,
                        params: Dict[str, Any]) -> List[Parameter]:
        """Логирование нескольких параметров"""
        logged = []
        for key, value in params.items():
            param = await self.log_param(run_id, key, value)
            if param:
                logged.append(param)
        return logged
        
    async def log_metric(self, run_id: str,
                        key: str,
                        value: float,
                        step: int = 0,
                        step_type: MetricStep = MetricStep.EPOCH) -> Optional[Metric]:
        """Логирование метрики"""
        run = self.runs.get(run_id)
        if not run:
            return None
            
        metric = Metric(
            metric_id=f"met_{uuid.uuid4().hex[:8]}",
            run_id=run_id,
            key=key,
            value=value,
            step=step,
            step_type=step_type
        )
        
        self.metrics[metric.metric_id] = metric
        
        # Update metric history
        history_key = f"{run_id}_{key}"
        if history_key not in self.metric_histories:
            self.metric_histories[history_key] = MetricHistory(
                history_id=f"hist_{uuid.uuid4().hex[:8]}",
                run_id=run_id,
                metric_key=key
            )
            
        history = self.metric_histories[history_key]
        history.values.append(value)
        history.steps.append(step)
        history.timestamps.append(datetime.now())
        history.last_value = value
        history.min_value = min(history.values)
        history.max_value = max(history.values)
        
        return metric
        
    async def log_metrics(self, run_id: str,
                         metrics: Dict[str, float],
                         step: int = 0) -> List[Metric]:
        """Логирование нескольких метрик"""
        logged = []
        for key, value in metrics.items():
            metric = await self.log_metric(run_id, key, value, step)
            if metric:
                logged.append(metric)
        return logged
        
    async def log_artifact(self, run_id: str,
                          file_name: str,
                          file_path: str,
                          artifact_type: ArtifactType = ArtifactType.OTHER,
                          file_size: int = 0,
                          metadata: Dict[str, Any] = None) -> Optional[Artifact]:
        """Логирование артефакта"""
        run = self.runs.get(run_id)
        if not run:
            return None
            
        artifact = Artifact(
            artifact_id=f"art_{uuid.uuid4().hex[:8]}",
            run_id=run_id,
            artifact_type=artifact_type,
            file_name=file_name,
            file_path=file_path,
            file_size=file_size,
            metadata=metadata or {}
        )
        
        self.artifacts[artifact.artifact_id] = artifact
        return artifact
        
    async def log_dataset(self, run_id: str,
                         name: str,
                         source: str,
                         version: str = "",
                         row_count: int = 0,
                         column_count: int = 0,
                         schema: Dict[str, str] = None) -> Optional[Dataset]:
        """Логирование набора данных"""
        run = self.runs.get(run_id)
        if not run:
            return None
            
        dataset = Dataset(
            dataset_id=f"ds_{uuid.uuid4().hex[:8]}",
            run_id=run_id,
            name=name,
            source=source,
            version=version,
            row_count=row_count,
            column_count=column_count,
            schema=schema or {}
        )
        
        self.datasets[dataset.dataset_id] = dataset
        return dataset
        
    async def log_model(self, run_id: str,
                       name: str,
                       framework: str,
                       framework_version: str = "",
                       input_schema: Dict[str, Any] = None,
                       output_schema: Dict[str, Any] = None) -> Optional[Model]:
        """Логирование модели"""
        run = self.runs.get(run_id)
        if not run:
            return None
            
        model = Model(
            model_id=f"mdl_{uuid.uuid4().hex[:8]}",
            run_id=run_id,
            name=name,
            framework=framework,
            framework_version=framework_version,
            input_schema=input_schema or {},
            output_schema=output_schema or {},
            artifact_path=f"{run.artifact_uri}/model"
        )
        
        self.models[model.model_id] = model
        return model
        
    async def set_tag(self, run_id: str,
                     key: str,
                     value: str) -> Optional[Tag]:
        """Установка тега"""
        run = self.runs.get(run_id)
        if not run:
            return None
            
        tag = Tag(
            tag_id=f"tag_{uuid.uuid4().hex[:8]}",
            run_id=run_id,
            key=key,
            value=value
        )
        
        self.tags[tag.tag_id] = tag
        run.tags[key] = value
        
        return tag
        
    async def compare_runs(self, name: str,
                          run_ids: List[str],
                          metric_keys: List[str]) -> RunComparison:
        """Сравнение запусков"""
        results = {}
        
        for run_id in run_ids:
            results[run_id] = {}
            run_metrics = [m for m in self.metrics.values() if m.run_id == run_id]
            for key in metric_keys:
                # Get last value for each metric
                key_metrics = [m for m in run_metrics if m.key == key]
                if key_metrics:
                    results[run_id][key] = key_metrics[-1].value
                else:
                    results[run_id][key] = 0.0
                    
        # Find best run (by first metric)
        best_run_id = ""
        best_value = -float("inf")
        if metric_keys and results:
            first_key = metric_keys[0]
            for rid, metrics in results.items():
                if metrics.get(first_key, 0) > best_value:
                    best_value = metrics.get(first_key, 0)
                    best_run_id = rid
                    
        comparison = RunComparison(
            comparison_id=f"cmp_{uuid.uuid4().hex[:8]}",
            name=name,
            run_ids=run_ids,
            metric_keys=metric_keys,
            results=results,
            best_run_id=best_run_id,
            best_metric_key=metric_keys[0] if metric_keys else ""
        )
        
        self.comparisons[comparison.comparison_id] = comparison
        return comparison
        
    async def create_visualization(self, run_id: str,
                                  name: str,
                                  viz_type: VisualizationType,
                                  config: Dict[str, Any] = None,
                                  data: Dict[str, Any] = None) -> Optional[Visualization]:
        """Создание визуализации"""
        run = self.runs.get(run_id)
        if not run:
            return None
            
        viz = Visualization(
            viz_id=f"viz_{uuid.uuid4().hex[:8]}",
            run_id=run_id,
            viz_type=viz_type,
            name=name,
            config=config or {},
            data=data or {}
        )
        
        self.visualizations[viz.viz_id] = viz
        return viz
        
    async def add_comment(self, run_id: str,
                         author: str,
                         content: str) -> Optional[Comment]:
        """Добавление комментария"""
        run = self.runs.get(run_id)
        if not run:
            return None
            
        comment = Comment(
            comment_id=f"com_{uuid.uuid4().hex[:8]}",
            run_id=run_id,
            author=author,
            content=content
        )
        
        self.comments[comment.comment_id] = comment
        return comment
        
    async def send_notification(self, run_id: str,
                               notification_type: str,
                               message: str,
                               recipients: List[str]) -> Optional[Notification]:
        """Отправка уведомления"""
        notification = Notification(
            notification_id=f"not_{uuid.uuid4().hex[:8]}",
            run_id=run_id,
            notification_type=notification_type,
            message=message,
            recipients=recipients,
            is_sent=True
        )
        
        self.notifications[notification.notification_id] = notification
        return notification
        
    async def search_runs(self, experiment_id: str = None,
                         status: RunStatus = None,
                         user_id: str = None,
                         tag_filter: Dict[str, str] = None,
                         metric_filter: Dict[str, tuple] = None,
                         max_results: int = 100) -> List[Run]:
        """Поиск запусков"""
        results = []
        
        for run in self.runs.values():
            # Filter by experiment
            if experiment_id and run.experiment_id != experiment_id:
                continue
                
            # Filter by status
            if status and run.status != status:
                continue
                
            # Filter by user
            if user_id and run.user_id != user_id:
                continue
                
            # Filter by tags
            if tag_filter:
                match = True
                for key, value in tag_filter.items():
                    if run.tags.get(key) != value:
                        match = False
                        break
                if not match:
                    continue
                    
            results.append(run)
            
            if len(results) >= max_results:
                break
                
        return results
        
    async def get_run_metrics(self, run_id: str) -> Dict[str, float]:
        """Получение метрик запуска"""
        result = {}
        
        for metric in self.metrics.values():
            if metric.run_id == run_id:
                # Get latest value for each key
                if metric.key not in result:
                    result[metric.key] = metric.value
                    
        return result
        
    async def get_run_params(self, run_id: str) -> Dict[str, str]:
        """Получение параметров запуска"""
        result = {}
        
        for param in self.parameters.values():
            if param.run_id == run_id:
                result[param.key] = param.value
                
        return result
        
    async def collect_metrics(self) -> ExperimentMetrics:
        """Сбор метрик платформы"""
        active_experiments = sum(1 for e in self.experiments.values() 
                                if e.lifecycle_stage == ExperimentLifecycle.ACTIVE)
        
        running_runs = sum(1 for r in self.runs.values() if r.status == RunStatus.RUNNING)
        finished_runs = sum(1 for r in self.runs.values() if r.status == RunStatus.FINISHED)
        failed_runs = sum(1 for r in self.runs.values() if r.status == RunStatus.FAILED)
        
        total_artifact_size = sum(a.file_size for a in self.artifacts.values())
        
        metrics = ExperimentMetrics(
            metrics_id=f"exm_{uuid.uuid4().hex[:8]}",
            total_projects=len(self.projects),
            total_experiments=len(self.experiments),
            active_experiments=active_experiments,
            total_runs=len(self.runs),
            running_runs=running_runs,
            finished_runs=finished_runs,
            failed_runs=failed_runs,
            total_metrics=len(self.metrics),
            total_artifacts=len(self.artifacts),
            total_artifact_size=total_artifact_size
        )
        
        self.platform_metrics[metrics.metrics_id] = metrics
        return metrics
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_projects = len(self.projects)
        total_experiments = len(self.experiments)
        active_experiments = sum(1 for e in self.experiments.values() 
                                if e.lifecycle_stage == ExperimentLifecycle.ACTIVE)
        
        total_runs = len(self.runs)
        runs_by_status = {}
        for status in RunStatus:
            runs_by_status[status.value] = sum(1 for r in self.runs.values() if r.status == status)
            
        total_params = len(self.parameters)
        total_metrics = len(self.metrics)
        total_artifacts = len(self.artifacts)
        total_models = len(self.models)
        total_datasets = len(self.datasets)
        
        return {
            "total_projects": total_projects,
            "total_experiments": total_experiments,
            "active_experiments": active_experiments,
            "total_runs": total_runs,
            "runs_by_status": runs_by_status,
            "total_params": total_params,
            "total_metrics": total_metrics,
            "total_artifacts": total_artifacts,
            "total_models": total_models,
            "total_datasets": total_datasets
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 355: Experiment Tracking Platform")
    print("=" * 60)
    
    platform = ExperimentTrackingPlatform(tracking_uri="http://tracking.ml.internal:5000")
    print("✓ Experiment Tracking Platform initialized")
    
    # Create Projects
    print("\n📁 Creating Projects...")
    
    projects_data = [
        ("customer-churn", "Customer churn prediction models", "ml-team", "platform", "team", ["churn", "classification"]),
        ("recommender-systems", "Product recommendation engines", "recommender-team", "recommendations", "team", ["recommendation", "collaborative-filtering"]),
        ("fraud-detection", "Fraud detection models", "risk-team", "fraud", "private", ["fraud", "real-time"]),
        ("nlp-research", "NLP research experiments", "nlp-team", "nlp", "team", ["nlp", "transformers"]),
        ("computer-vision", "Computer vision experiments", "cv-team", "vision", "team", ["cv", "deep-learning"])
    ]
    
    projects = []
    for name, desc, owner, team, vis, tags in projects_data:
        p = await platform.create_project(name, desc, owner, team, vis, tags)
        projects.append(p)
        print(f"  📁 {name}")
        
    # Create Experiments
    print("\n🧪 Creating Experiments...")
    
    experiments_data = [
        (projects[0].project_id, "xgboost-baseline", "XGBoost baseline for churn", {"model_type": "xgboost"}),
        (projects[0].project_id, "lightgbm-tuning", "LightGBM hyperparameter tuning", {"model_type": "lightgbm"}),
        (projects[0].project_id, "neural-network", "Neural network approach", {"model_type": "neural"}),
        (projects[1].project_id, "collaborative-filtering", "CF based recommendations", {"type": "cf"}),
        (projects[1].project_id, "deep-learning-rec", "Deep learning recommender", {"type": "deep"}),
        (projects[2].project_id, "fraud-v1", "Fraud detection v1", {"version": "1"}),
        (projects[3].project_id, "bert-finetuning", "BERT fine-tuning experiments", {"model": "bert"}),
        (projects[4].project_id, "resnet-classification", "ResNet image classification", {"backbone": "resnet"})
    ]
    
    experiments = []
    for pid, name, desc, tags in experiments_data:
        e = await platform.create_experiment(pid, name, desc, tags=tags)
        if e:
            experiments.append(e)
            print(f"  🧪 {name}")
            
    # Start Runs
    print("\n🏃 Starting Experiment Runs...")
    
    runs = []
    for exp in experiments:
        num_runs = random.randint(3, 8)
        for i in range(num_runs):
            run = await platform.start_run(
                exp.experiment_id,
                f"run_{i+1}",
                f"user_{random.randint(1, 5)}",
                random.choice(["notebook", "script", "job"]),
                f"train_{exp.name}.py",
                uuid.uuid4().hex[:7],
                "main",
                {"run_type": "training", "iteration": str(i+1)}
            )
            if run:
                runs.append(run)
                
    print(f"  🏃 Started {len(runs)} runs")
    
    # Log Parameters
    print("\n⚙️ Logging Parameters...")
    
    param_count = 0
    for run in runs:
        params = {
            "learning_rate": round(random.uniform(0.001, 0.1), 4),
            "batch_size": random.choice([16, 32, 64, 128, 256]),
            "epochs": random.randint(10, 100),
            "optimizer": random.choice(["adam", "sgd", "adamw"]),
            "dropout": round(random.uniform(0.1, 0.5), 2),
            "hidden_size": random.choice([64, 128, 256, 512])
        }
        await platform.log_params(run.run_id, params)
        param_count += len(params)
        
    print(f"  ⚙️ Logged {param_count} parameters")
    
    # Log Metrics over epochs
    print("\n📈 Logging Metrics...")
    
    metric_count = 0
    for run in runs:
        num_epochs = random.randint(10, 50)
        base_acc = random.uniform(0.6, 0.8)
        base_loss = random.uniform(0.5, 1.5)
        
        for epoch in range(num_epochs):
            # Simulate improving metrics
            acc = min(0.99, base_acc + epoch * 0.01 * random.uniform(0.5, 1.5))
            loss = max(0.01, base_loss - epoch * 0.02 * random.uniform(0.5, 1.5))
            
            await platform.log_metrics(run.run_id, {
                "accuracy": round(acc, 4),
                "loss": round(loss, 4),
                "val_accuracy": round(acc - random.uniform(0, 0.05), 4),
                "val_loss": round(loss + random.uniform(0, 0.1), 4)
            }, epoch)
            metric_count += 4
            
    print(f"  📈 Logged {metric_count} metric values")
    
    # Log Artifacts
    print("\n📦 Logging Artifacts...")
    
    artifact_count = 0
    for run in runs[:20]:  # First 20 runs
        # Model artifact
        await platform.log_artifact(
            run.run_id,
            "model.pkl",
            f"{run.artifact_uri}/model.pkl",
            ArtifactType.MODEL,
            random.randint(1024*1024, 100*1024*1024)
        )
        
        # Config
        await platform.log_artifact(
            run.run_id,
            "config.yaml",
            f"{run.artifact_uri}/config.yaml",
            ArtifactType.CONFIG,
            random.randint(1024, 10*1024)
        )
        
        # Plot
        await platform.log_artifact(
            run.run_id,
            "training_curves.png",
            f"{run.artifact_uri}/training_curves.png",
            ArtifactType.PLOT,
            random.randint(50*1024, 500*1024)
        )
        
        artifact_count += 3
        
    print(f"  📦 Logged {artifact_count} artifacts")
    
    # Log Datasets
    print("\n📊 Logging Datasets...")
    
    for run in runs[:15]:
        await platform.log_dataset(
            run.run_id,
            "training_data",
            "s3://data-lake/training/",
            "v1.2.0",
            random.randint(100000, 1000000),
            random.randint(20, 100),
            {"id": "int", "features": "array", "label": "int"}
        )
        
    print(f"  📊 Logged {len([d for d in platform.datasets.values()])} datasets")
    
    # Log Models
    print("\n🤖 Logging Models...")
    
    frameworks = ["sklearn", "pytorch", "tensorflow", "xgboost", "lightgbm"]
    for run in runs[:20]:
        framework = random.choice(frameworks)
        await platform.log_model(
            run.run_id,
            f"model_{run.run_id[:8]}",
            framework,
            "1.0.0",
            {"features": {"type": "array", "shape": [None, 50]}},
            {"prediction": {"type": "float"}}
        )
        
    print(f"  🤖 Logged {len(platform.models)} models")
    
    # End Runs
    print("\n✅ Completing Runs...")
    
    for run in runs:
        status = RunStatus.FINISHED if random.random() > 0.1 else RunStatus.FAILED
        await platform.end_run(run.run_id, status)
        
    finished = sum(1 for r in runs if platform.runs[r.run_id].status == RunStatus.FINISHED)
    failed = len(runs) - finished
    print(f"  ✅ Completed: {finished} finished, {failed} failed")
    
    # Compare Runs
    print("\n📊 Comparing Runs...")
    
    comparisons = []
    for exp in experiments[:4]:
        exp_runs = [r for r in runs if r.experiment_id == exp.experiment_id]
        if len(exp_runs) >= 3:
            run_ids = [r.run_id for r in exp_runs[:5]]
            comp = await platform.compare_runs(
                f"{exp.name}_comparison",
                run_ids,
                ["accuracy", "val_accuracy", "loss"]
            )
            comparisons.append(comp)
            
    print(f"  📊 Created {len(comparisons)} comparisons")
    
    # Create Visualizations
    print("\n📉 Creating Visualizations...")
    
    viz_count = 0
    for run in runs[:10]:
        # Training curves
        await platform.create_visualization(
            run.run_id,
            "Training Curves",
            VisualizationType.LINE_CHART,
            {"x_axis": "epoch", "y_axis": "value"},
            {"metrics": ["accuracy", "val_accuracy", "loss", "val_loss"]}
        )
        
        # Confusion matrix
        await platform.create_visualization(
            run.run_id,
            "Confusion Matrix",
            VisualizationType.CONFUSION_MATRIX,
            {"classes": ["class_0", "class_1"]},
            {"matrix": [[random.randint(80, 100), random.randint(0, 20)],
                       [random.randint(0, 20), random.randint(80, 100)]]}
        )
        viz_count += 2
        
    print(f"  📉 Created {viz_count} visualizations")
    
    # Add Comments
    print("\n💬 Adding Comments...")
    
    for run in runs[:10]:
        await platform.add_comment(
            run.run_id,
            f"user_{random.randint(1, 5)}@company.com",
            random.choice([
                "Good results, let's proceed to staging",
                "Need to investigate the high validation loss",
                "Best run so far!",
                "Try increasing batch size",
                "Overfitting observed after epoch 30"
            ])
        )
        
    print(f"  💬 Added {len(platform.comments)} comments")
    
    # Send Notifications
    print("\n🔔 Sending Notifications...")
    
    for run in runs[:5]:
        await platform.send_notification(
            run.run_id,
            "run_finished",
            f"Run {run.run_name} completed successfully",
            [f"user_{random.randint(1, 5)}@company.com"]
        )
        
    print(f"  🔔 Sent {len(platform.notifications)} notifications")
    
    # Collect Platform Metrics
    platform_metrics = await platform.collect_metrics()
    
    # Projects Dashboard
    print("\n📁 Projects:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Project Name             │ Owner           │ Team              │ Visibility │ Experiments │ Runs   │ Tags                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for p in projects:
        name = p.name[:24].ljust(24)
        owner = p.owner[:15].ljust(15)
        team = p.team[:17].ljust(17)
        vis = p.visibility[:10].ljust(10)
        exps = str(p.experiment_count).ljust(11)
        runs_count = str(p.run_count).ljust(6)
        tags = ", ".join(p.tags[:3])[:405]
        tags = tags.ljust(405)
        
        print(f"  │ {name} │ {owner} │ {team} │ {vis} │ {exps} │ {runs_count} │ {tags} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Experiments Dashboard
    print("\n🧪 Experiments:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Experiment Name                 │ Project                  │ Runs   │ Active │ Lifecycle │ Last Updated                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for e in experiments:
        name = e.name[:31].ljust(31)
        project = platform.projects.get(e.project_id)
        proj_name = project.name if project else "Unknown"
        proj_name = proj_name[:24].ljust(24)
        runs_count = str(e.run_count).ljust(6)
        active = str(e.active_runs).ljust(6)
        lifecycle = e.lifecycle_stage.value[:9].ljust(9)
        updated = e.last_updated.strftime("%Y-%m-%d %H:%M") if e.last_updated else "N/A"
        updated = updated.ljust(317)
        
        print(f"  │ {name} │ {proj_name} │ {runs_count} │ {active} │ {lifecycle} │ {updated} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Run Comparisons Dashboard
    print("\n📊 Run Comparisons:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Comparison Name                 │ Runs  │ Metrics                         │ Best Run                          │ Best Score                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for c in comparisons:
        name = c.name[:31].ljust(31)
        num_runs = str(len(c.run_ids)).ljust(5)
        metrics_str = ", ".join(c.metric_keys[:3])[:31]
        metrics_str = metrics_str.ljust(31)
        best = c.best_run_id[:35] if c.best_run_id else "N/A"
        best = best.ljust(35)
        
        best_score = "N/A"
        if c.best_run_id and c.best_metric_key:
            score = c.results.get(c.best_run_id, {}).get(c.best_metric_key, 0)
            best_score = f"{score:.4f}"
        best_score = best_score.ljust(277)
        
        print(f"  │ {name} │ {num_runs} │ {metrics_str} │ {best} │ {best_score} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Projects: {stats['total_projects']}")
    print(f"  Experiments: {stats['active_experiments']}/{stats['total_experiments']} active")
    print(f"  Runs: {stats['total_runs']} (Finished: {stats['runs_by_status'].get('finished', 0)}, Failed: {stats['runs_by_status'].get('failed', 0)})")
    print(f"  Parameters: {stats['total_params']}, Metrics: {stats['total_metrics']}")
    print(f"  Artifacts: {stats['total_artifacts']}, Models: {stats['total_models']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Experiment Tracking Platform                     │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Projects:                {stats['total_projects']:>12}                      │")
    print(f"│ Active Experiments:            {stats['active_experiments']:>12}                      │")
    print(f"│ Total Runs:                    {stats['total_runs']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Finished Runs:                 {stats['runs_by_status'].get('finished', 0):>12}                      │")
    print(f"│ Failed Runs:                   {stats['runs_by_status'].get('failed', 0):>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Parameters:              {stats['total_params']:>12}                      │")
    print(f"│ Total Metrics:                 {stats['total_metrics']:>12}                      │")
    print(f"│ Total Artifacts:               {stats['total_artifacts']:>12}                      │")
    print(f"│ Total Models:                  {stats['total_models']:>12}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Experiment Tracking Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
