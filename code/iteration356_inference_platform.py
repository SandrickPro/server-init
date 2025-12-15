#!/usr/bin/env python3
"""
Server Init - Iteration 356: ML Inference Platform
Платформа вывода ML моделей

Функционал:
- Model Serving - обслуживание моделей
- Inference Endpoints - эндпоинты вывода
- Batch Inference - пакетный вывод
- Real-time Inference - вывод в реальном времени
- Model Scaling - масштабирование моделей
- Inference Caching - кэширование вывода
- A/B Testing - A/B тестирование
- Model Monitoring - мониторинг моделей
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import json


class InferenceMode(Enum):
    """Режим вывода"""
    REALTIME = "realtime"
    BATCH = "batch"
    STREAMING = "streaming"


class EndpointStatus(Enum):
    """Статус эндпоинта"""
    CREATING = "creating"
    IN_SERVICE = "in_service"
    UPDATING = "updating"
    FAILED = "failed"
    DELETING = "deleting"
    STOPPED = "stopped"


class ModelFormat(Enum):
    """Формат модели"""
    ONNX = "onnx"
    TORCHSCRIPT = "torchscript"
    SAVEDMODEL = "savedmodel"
    PICKLE = "pickle"
    PMML = "pmml"
    CUSTOM = "custom"


class ScalingPolicy(Enum):
    """Политика масштабирования"""
    MANUAL = "manual"
    TARGET_TRACKING = "target_tracking"
    STEP_SCALING = "step_scaling"
    SCHEDULED = "scheduled"


class LoadBalancerType(Enum):
    """Тип балансировщика"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED = "weighted"
    RANDOM = "random"


class CacheStrategy(Enum):
    """Стратегия кэширования"""
    NO_CACHE = "no_cache"
    LRU = "lru"
    LFU = "lfu"
    TTL = "ttl"


class HealthStatus(Enum):
    """Статус здоровья"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ModelArtifact:
    """Артефакт модели"""
    artifact_id: str
    name: str
    
    # Model info
    model_format: ModelFormat = ModelFormat.ONNX
    model_path: str = ""
    model_size: int = 0
    
    # Version
    version: str = ""
    
    # Framework
    framework: str = ""
    framework_version: str = ""
    
    # Input/Output
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    
    # Config
    preprocessing: Dict[str, Any] = field(default_factory=dict)
    postprocessing: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class InferenceEndpoint:
    """Эндпоинт вывода"""
    endpoint_id: str
    name: str
    
    # URL
    url: str = ""
    
    # Mode
    inference_mode: InferenceMode = InferenceMode.REALTIME
    
    # Status
    status: EndpointStatus = EndpointStatus.CREATING
    
    # Model
    model_artifact_id: str = ""
    
    # Instance config
    instance_type: str = ""
    instance_count: int = 1
    
    # Scaling
    auto_scaling: bool = False
    min_instances: int = 1
    max_instances: int = 10
    
    # Health
    health_status: HealthStatus = HealthStatus.UNKNOWN
    
    # Traffic
    traffic_percent: int = 100
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


@dataclass
class ModelDeployment:
    """Развёртывание модели"""
    deployment_id: str
    endpoint_id: str
    model_artifact_id: str
    
    # Name
    name: str = ""
    
    # Traffic
    traffic_percent: int = 100
    
    # Instance config
    instance_type: str = ""
    instance_count: int = 1
    
    # Resources
    cpu_limit: str = "2"
    memory_limit: str = "4Gi"
    gpu_count: int = 0
    
    # Status
    status: str = "creating"  # creating, running, failed, stopped
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    deployed_at: Optional[datetime] = None


@dataclass
class ScalingConfig:
    """Конфигурация масштабирования"""
    config_id: str
    endpoint_id: str
    
    # Policy
    scaling_policy: ScalingPolicy = ScalingPolicy.TARGET_TRACKING
    
    # Target
    target_metric: str = "cpu_utilization"
    target_value: float = 70.0
    
    # Limits
    min_instances: int = 1
    max_instances: int = 10
    
    # Cooldown
    scale_in_cooldown: int = 300  # seconds
    scale_out_cooldown: int = 60
    
    # Schedule (for scheduled scaling)
    schedule: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class InferenceRequest:
    """Запрос вывода"""
    request_id: str
    endpoint_id: str
    
    # Input
    input_data: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    batch_size: int = 1
    
    # Timing
    received_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    
    # Latency
    latency_ms: float = 0.0
    
    # Status
    success: bool = True
    error: str = ""


@dataclass
class InferenceResponse:
    """Ответ вывода"""
    response_id: str
    request_id: str
    
    # Output
    predictions: List[Any] = field(default_factory=list)
    probabilities: List[List[float]] = field(default_factory=list)
    
    # Metadata
    model_version: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class BatchJob:
    """Пакетное задание"""
    job_id: str
    endpoint_id: str
    
    # Name
    name: str = ""
    
    # Input
    input_path: str = ""
    input_format: str = "csv"  # csv, json, parquet
    
    # Output
    output_path: str = ""
    output_format: str = "csv"
    
    # Config
    batch_size: int = 100
    max_concurrency: int = 10
    
    # Progress
    total_records: int = 0
    processed_records: int = 0
    failed_records: int = 0
    
    # Status
    status: str = "pending"  # pending, running, completed, failed
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class CacheConfig:
    """Конфигурация кэша"""
    config_id: str
    endpoint_id: str
    
    # Strategy
    cache_strategy: CacheStrategy = CacheStrategy.LRU
    
    # Size
    max_size_mb: int = 1024
    
    # TTL
    ttl_seconds: int = 3600
    
    # Stats
    hit_count: int = 0
    miss_count: int = 0
    
    # Status
    is_enabled: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ABTest:
    """A/B тест"""
    test_id: str
    name: str
    endpoint_id: str
    
    # Variants
    control_deployment_id: str = ""
    treatment_deployment_id: str = ""
    
    # Traffic split
    control_traffic_percent: int = 50
    treatment_traffic_percent: int = 50
    
    # Metrics
    primary_metric: str = ""  # latency, accuracy, conversion
    
    # Status
    status: str = "draft"  # draft, running, completed
    
    # Results
    control_metric_value: float = 0.0
    treatment_metric_value: float = 0.0
    winner: str = ""
    
    # Sample size
    total_requests: int = 0
    control_requests: int = 0
    treatment_requests: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None


@dataclass
class ModelMonitor:
    """Монитор модели"""
    monitor_id: str
    endpoint_id: str
    
    # Metrics
    check_data_drift: bool = True
    check_prediction_drift: bool = True
    check_performance: bool = True
    
    # Thresholds
    drift_threshold: float = 0.1
    latency_threshold_ms: float = 100.0
    error_rate_threshold: float = 1.0
    
    # Schedule
    check_interval_minutes: int = 60
    
    # Status
    is_enabled: bool = True
    last_check: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class MonitoringAlert:
    """Алерт мониторинга"""
    alert_id: str
    endpoint_id: str
    
    # Type
    alert_type: str = ""  # drift, latency, error_rate, health
    
    # Details
    message: str = ""
    metric_value: float = 0.0
    threshold: float = 0.0
    
    # Severity
    severity: str = "warning"  # info, warning, critical
    
    # Status
    is_resolved: bool = False
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


@dataclass
class EndpointMetrics:
    """Метрики эндпоинта"""
    metrics_id: str
    endpoint_id: str
    
    # Request metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # Latency
    avg_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    
    # Throughput
    requests_per_second: float = 0.0
    
    # Resource utilization
    cpu_utilization: float = 0.0
    memory_utilization: float = 0.0
    gpu_utilization: float = 0.0
    
    # Timestamps
    collected_at: datetime = field(default_factory=datetime.now)


@dataclass
class InferencePlatformMetrics:
    """Метрики платформы вывода"""
    metrics_id: str
    
    # Endpoints
    total_endpoints: int = 0
    active_endpoints: int = 0
    
    # Deployments
    total_deployments: int = 0
    
    # Requests
    total_requests: int = 0
    avg_latency_ms: float = 0.0
    
    # Batch jobs
    total_batch_jobs: int = 0
    completed_batch_jobs: int = 0
    
    # AB Tests
    active_tests: int = 0
    
    # Alerts
    active_alerts: int = 0
    
    # Timestamps
    collected_at: datetime = field(default_factory=datetime.now)


class InferencePlatform:
    """Платформа вывода ML моделей"""
    
    def __init__(self, platform_name: str = "ml-inference"):
        self.platform_name = platform_name
        self.artifacts: Dict[str, ModelArtifact] = {}
        self.endpoints: Dict[str, InferenceEndpoint] = {}
        self.deployments: Dict[str, ModelDeployment] = {}
        self.scaling_configs: Dict[str, ScalingConfig] = {}
        self.requests: Dict[str, InferenceRequest] = {}
        self.responses: Dict[str, InferenceResponse] = {}
        self.batch_jobs: Dict[str, BatchJob] = {}
        self.cache_configs: Dict[str, CacheConfig] = {}
        self.ab_tests: Dict[str, ABTest] = {}
        self.monitors: Dict[str, ModelMonitor] = {}
        self.alerts: Dict[str, MonitoringAlert] = {}
        self.endpoint_metrics: Dict[str, EndpointMetrics] = {}
        self.platform_metrics: Dict[str, InferencePlatformMetrics] = {}
        
    async def register_model(self, name: str,
                            model_format: ModelFormat,
                            model_path: str,
                            model_size: int = 0,
                            version: str = "",
                            framework: str = "",
                            input_schema: Dict[str, Any] = None,
                            output_schema: Dict[str, Any] = None) -> ModelArtifact:
        """Регистрация модели"""
        artifact = ModelArtifact(
            artifact_id=f"art_{uuid.uuid4().hex[:8]}",
            name=name,
            model_format=model_format,
            model_path=model_path,
            model_size=model_size,
            version=version,
            framework=framework,
            input_schema=input_schema or {},
            output_schema=output_schema or {}
        )
        
        self.artifacts[artifact.artifact_id] = artifact
        return artifact
        
    async def create_endpoint(self, name: str,
                             model_artifact_id: str,
                             inference_mode: InferenceMode = InferenceMode.REALTIME,
                             instance_type: str = "ml.m5.large",
                             instance_count: int = 1,
                             auto_scaling: bool = False,
                             min_instances: int = 1,
                             max_instances: int = 10) -> Optional[InferenceEndpoint]:
        """Создание эндпоинта"""
        artifact = self.artifacts.get(model_artifact_id)
        if not artifact:
            return None
            
        endpoint = InferenceEndpoint(
            endpoint_id=f"ep_{uuid.uuid4().hex[:8]}",
            name=name,
            url=f"https://api.{self.platform_name}.ml/v1/endpoints/{name}/invocations",
            inference_mode=inference_mode,
            model_artifact_id=model_artifact_id,
            instance_type=instance_type,
            instance_count=instance_count,
            auto_scaling=auto_scaling,
            min_instances=min_instances,
            max_instances=max_instances
        )
        
        self.endpoints[endpoint.endpoint_id] = endpoint
        
        # Create default deployment
        await self._create_deployment(endpoint, artifact)
        
        # Simulate endpoint creation
        await asyncio.sleep(0.01)
        endpoint.status = EndpointStatus.IN_SERVICE
        endpoint.health_status = HealthStatus.HEALTHY
        
        return endpoint
        
    async def _create_deployment(self, endpoint: InferenceEndpoint,
                                artifact: ModelArtifact) -> ModelDeployment:
        """Создание развёртывания"""
        deployment = ModelDeployment(
            deployment_id=f"dep_{uuid.uuid4().hex[:8]}",
            endpoint_id=endpoint.endpoint_id,
            model_artifact_id=artifact.artifact_id,
            name=f"{endpoint.name}-deployment",
            instance_type=endpoint.instance_type,
            instance_count=endpoint.instance_count,
            status="running",
            deployed_at=datetime.now()
        )
        
        self.deployments[deployment.deployment_id] = deployment
        return deployment
        
    async def configure_scaling(self, endpoint_id: str,
                               scaling_policy: ScalingPolicy = ScalingPolicy.TARGET_TRACKING,
                               target_metric: str = "cpu_utilization",
                               target_value: float = 70.0,
                               min_instances: int = 1,
                               max_instances: int = 10) -> Optional[ScalingConfig]:
        """Настройка масштабирования"""
        endpoint = self.endpoints.get(endpoint_id)
        if not endpoint:
            return None
            
        config = ScalingConfig(
            config_id=f"sc_{uuid.uuid4().hex[:8]}",
            endpoint_id=endpoint_id,
            scaling_policy=scaling_policy,
            target_metric=target_metric,
            target_value=target_value,
            min_instances=min_instances,
            max_instances=max_instances
        )
        
        self.scaling_configs[config.config_id] = config
        endpoint.auto_scaling = True
        endpoint.min_instances = min_instances
        endpoint.max_instances = max_instances
        
        return config
        
    async def invoke(self, endpoint_id: str,
                    input_data: Dict[str, Any]) -> Optional[InferenceResponse]:
        """Вызов модели"""
        endpoint = self.endpoints.get(endpoint_id)
        if not endpoint or endpoint.status != EndpointStatus.IN_SERVICE:
            return None
            
        request = InferenceRequest(
            request_id=f"req_{uuid.uuid4().hex[:12]}",
            endpoint_id=endpoint_id,
            input_data=input_data,
            batch_size=1
        )
        
        # Simulate inference
        await asyncio.sleep(random.uniform(0.001, 0.01))
        
        request.processed_at = datetime.now()
        request.latency_ms = random.uniform(5, 50)
        
        self.requests[request.request_id] = request
        
        # Generate response
        response = InferenceResponse(
            response_id=f"res_{uuid.uuid4().hex[:8]}",
            request_id=request.request_id,
            predictions=[random.randint(0, 1)],
            probabilities=[[round(random.uniform(0, 1), 4), round(random.uniform(0, 1), 4)]],
            model_version=self.artifacts.get(endpoint.model_artifact_id).version if endpoint.model_artifact_id else ""
        )
        
        self.responses[response.response_id] = response
        return response
        
    async def batch_invoke(self, endpoint_id: str,
                          inputs: List[Dict[str, Any]]) -> List[InferenceResponse]:
        """Пакетный вызов"""
        responses = []
        for input_data in inputs:
            response = await self.invoke(endpoint_id, input_data)
            if response:
                responses.append(response)
        return responses
        
    async def create_batch_job(self, endpoint_id: str,
                              name: str,
                              input_path: str,
                              output_path: str,
                              input_format: str = "csv",
                              output_format: str = "csv",
                              batch_size: int = 100,
                              max_concurrency: int = 10) -> Optional[BatchJob]:
        """Создание пакетного задания"""
        endpoint = self.endpoints.get(endpoint_id)
        if not endpoint:
            return None
            
        job = BatchJob(
            job_id=f"job_{uuid.uuid4().hex[:8]}",
            endpoint_id=endpoint_id,
            name=name,
            input_path=input_path,
            output_path=output_path,
            input_format=input_format,
            output_format=output_format,
            batch_size=batch_size,
            max_concurrency=max_concurrency,
            total_records=random.randint(10000, 100000)
        )
        
        self.batch_jobs[job.job_id] = job
        return job
        
    async def run_batch_job(self, job_id: str) -> Optional[BatchJob]:
        """Запуск пакетного задания"""
        job = self.batch_jobs.get(job_id)
        if not job:
            return None
            
        job.status = "running"
        job.started_at = datetime.now()
        
        # Simulate batch processing
        job.processed_records = job.total_records - random.randint(0, 100)
        job.failed_records = job.total_records - job.processed_records
        
        job.status = "completed"
        job.completed_at = datetime.now()
        
        return job
        
    async def configure_cache(self, endpoint_id: str,
                             cache_strategy: CacheStrategy = CacheStrategy.LRU,
                             max_size_mb: int = 1024,
                             ttl_seconds: int = 3600) -> Optional[CacheConfig]:
        """Настройка кэша"""
        endpoint = self.endpoints.get(endpoint_id)
        if not endpoint:
            return None
            
        config = CacheConfig(
            config_id=f"cc_{uuid.uuid4().hex[:8]}",
            endpoint_id=endpoint_id,
            cache_strategy=cache_strategy,
            max_size_mb=max_size_mb,
            ttl_seconds=ttl_seconds
        )
        
        self.cache_configs[config.config_id] = config
        return config
        
    async def create_ab_test(self, name: str,
                            endpoint_id: str,
                            control_deployment_id: str,
                            treatment_deployment_id: str,
                            control_traffic_percent: int = 50,
                            primary_metric: str = "latency") -> Optional[ABTest]:
        """Создание A/B теста"""
        endpoint = self.endpoints.get(endpoint_id)
        if not endpoint:
            return None
            
        test = ABTest(
            test_id=f"ab_{uuid.uuid4().hex[:8]}",
            name=name,
            endpoint_id=endpoint_id,
            control_deployment_id=control_deployment_id,
            treatment_deployment_id=treatment_deployment_id,
            control_traffic_percent=control_traffic_percent,
            treatment_traffic_percent=100 - control_traffic_percent,
            primary_metric=primary_metric
        )
        
        self.ab_tests[test.test_id] = test
        return test
        
    async def start_ab_test(self, test_id: str) -> Optional[ABTest]:
        """Запуск A/B теста"""
        test = self.ab_tests.get(test_id)
        if not test:
            return None
            
        test.status = "running"
        test.started_at = datetime.now()
        
        return test
        
    async def complete_ab_test(self, test_id: str) -> Optional[ABTest]:
        """Завершение A/B теста"""
        test = self.ab_tests.get(test_id)
        if not test:
            return None
            
        # Simulate results
        test.control_requests = random.randint(1000, 5000)
        test.treatment_requests = random.randint(1000, 5000)
        test.total_requests = test.control_requests + test.treatment_requests
        
        test.control_metric_value = random.uniform(10, 50)
        test.treatment_metric_value = random.uniform(10, 50)
        
        test.winner = "treatment" if test.treatment_metric_value < test.control_metric_value else "control"
        test.status = "completed"
        test.ended_at = datetime.now()
        
        return test
        
    async def create_monitor(self, endpoint_id: str,
                            check_data_drift: bool = True,
                            check_prediction_drift: bool = True,
                            check_performance: bool = True,
                            drift_threshold: float = 0.1,
                            latency_threshold_ms: float = 100.0,
                            error_rate_threshold: float = 1.0) -> Optional[ModelMonitor]:
        """Создание монитора"""
        endpoint = self.endpoints.get(endpoint_id)
        if not endpoint:
            return None
            
        monitor = ModelMonitor(
            monitor_id=f"mon_{uuid.uuid4().hex[:8]}",
            endpoint_id=endpoint_id,
            check_data_drift=check_data_drift,
            check_prediction_drift=check_prediction_drift,
            check_performance=check_performance,
            drift_threshold=drift_threshold,
            latency_threshold_ms=latency_threshold_ms,
            error_rate_threshold=error_rate_threshold
        )
        
        self.monitors[monitor.monitor_id] = monitor
        return monitor
        
    async def run_monitoring_check(self, monitor_id: str) -> List[MonitoringAlert]:
        """Запуск проверки мониторинга"""
        monitor = self.monitors.get(monitor_id)
        if not monitor or not monitor.is_enabled:
            return []
            
        alerts = []
        endpoint = self.endpoints.get(monitor.endpoint_id)
        
        # Simulate checks
        if monitor.check_data_drift and random.random() < 0.1:
            alert = MonitoringAlert(
                alert_id=f"alr_{uuid.uuid4().hex[:8]}",
                endpoint_id=monitor.endpoint_id,
                alert_type="data_drift",
                message="Input data drift detected",
                metric_value=random.uniform(0.1, 0.3),
                threshold=monitor.drift_threshold,
                severity="warning"
            )
            self.alerts[alert.alert_id] = alert
            alerts.append(alert)
            
        if monitor.check_performance and random.random() < 0.05:
            alert = MonitoringAlert(
                alert_id=f"alr_{uuid.uuid4().hex[:8]}",
                endpoint_id=monitor.endpoint_id,
                alert_type="latency",
                message="High latency detected",
                metric_value=random.uniform(100, 200),
                threshold=monitor.latency_threshold_ms,
                severity="critical"
            )
            self.alerts[alert.alert_id] = alert
            alerts.append(alert)
            
        monitor.last_check = datetime.now()
        return alerts
        
    async def collect_endpoint_metrics(self, endpoint_id: str) -> Optional[EndpointMetrics]:
        """Сбор метрик эндпоинта"""
        endpoint = self.endpoints.get(endpoint_id)
        if not endpoint:
            return None
            
        endpoint_requests = [r for r in self.requests.values() if r.endpoint_id == endpoint_id]
        successful = sum(1 for r in endpoint_requests if r.success)
        latencies = [r.latency_ms for r in endpoint_requests]
        
        metrics = EndpointMetrics(
            metrics_id=f"em_{uuid.uuid4().hex[:8]}",
            endpoint_id=endpoint_id,
            total_requests=len(endpoint_requests),
            successful_requests=successful,
            failed_requests=len(endpoint_requests) - successful,
            avg_latency_ms=sum(latencies) / len(latencies) if latencies else 0.0,
            p50_latency_ms=sorted(latencies)[len(latencies)//2] if latencies else 0.0,
            p95_latency_ms=sorted(latencies)[int(len(latencies)*0.95)] if len(latencies) > 20 else max(latencies) if latencies else 0.0,
            p99_latency_ms=sorted(latencies)[int(len(latencies)*0.99)] if len(latencies) > 100 else max(latencies) if latencies else 0.0,
            requests_per_second=random.uniform(10, 100),
            cpu_utilization=random.uniform(20, 80),
            memory_utilization=random.uniform(30, 70),
            gpu_utilization=random.uniform(0, 90) if "gpu" in endpoint.instance_type else 0.0
        )
        
        self.endpoint_metrics[metrics.metrics_id] = metrics
        return metrics
        
    async def collect_platform_metrics(self) -> InferencePlatformMetrics:
        """Сбор метрик платформы"""
        active_endpoints = sum(1 for e in self.endpoints.values() if e.status == EndpointStatus.IN_SERVICE)
        completed_jobs = sum(1 for j in self.batch_jobs.values() if j.status == "completed")
        active_tests = sum(1 for t in self.ab_tests.values() if t.status == "running")
        active_alerts = sum(1 for a in self.alerts.values() if not a.is_resolved)
        
        latencies = [r.latency_ms for r in self.requests.values()]
        
        metrics = InferencePlatformMetrics(
            metrics_id=f"pm_{uuid.uuid4().hex[:8]}",
            total_endpoints=len(self.endpoints),
            active_endpoints=active_endpoints,
            total_deployments=len(self.deployments),
            total_requests=len(self.requests),
            avg_latency_ms=sum(latencies) / len(latencies) if latencies else 0.0,
            total_batch_jobs=len(self.batch_jobs),
            completed_batch_jobs=completed_jobs,
            active_tests=active_tests,
            active_alerts=active_alerts
        )
        
        self.platform_metrics[metrics.metrics_id] = metrics
        return metrics
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_artifacts = len(self.artifacts)
        total_endpoints = len(self.endpoints)
        active_endpoints = sum(1 for e in self.endpoints.values() if e.status == EndpointStatus.IN_SERVICE)
        
        endpoints_by_mode = {}
        for mode in InferenceMode:
            endpoints_by_mode[mode.value] = sum(1 for e in self.endpoints.values() if e.inference_mode == mode)
            
        total_requests = len(self.requests)
        successful_requests = sum(1 for r in self.requests.values() if r.success)
        
        total_batch_jobs = len(self.batch_jobs)
        completed_jobs = sum(1 for j in self.batch_jobs.values() if j.status == "completed")
        
        total_ab_tests = len(self.ab_tests)
        active_tests = sum(1 for t in self.ab_tests.values() if t.status == "running")
        
        active_alerts = sum(1 for a in self.alerts.values() if not a.is_resolved)
        
        return {
            "total_artifacts": total_artifacts,
            "total_endpoints": total_endpoints,
            "active_endpoints": active_endpoints,
            "endpoints_by_mode": endpoints_by_mode,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "total_batch_jobs": total_batch_jobs,
            "completed_jobs": completed_jobs,
            "total_ab_tests": total_ab_tests,
            "active_tests": active_tests,
            "active_alerts": active_alerts
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 356: ML Inference Platform")
    print("=" * 60)
    
    platform = InferencePlatform(platform_name="enterprise-inference")
    print("✓ ML Inference Platform initialized")
    
    # Register Models
    print("\n📦 Registering Model Artifacts...")
    
    models_data = [
        ("customer_churn_v1", ModelFormat.ONNX, "s3://models/churn/v1/model.onnx", "1.0.0", "xgboost", {"features": 50}, {"prediction": "float"}),
        ("customer_churn_v2", ModelFormat.ONNX, "s3://models/churn/v2/model.onnx", "2.0.0", "lightgbm", {"features": 60}, {"prediction": "float"}),
        ("fraud_detector_v1", ModelFormat.TORCHSCRIPT, "s3://models/fraud/v1/model.pt", "1.0.0", "pytorch", {"features": 100}, {"fraud_prob": "float"}),
        ("recommender_v1", ModelFormat.SAVEDMODEL, "s3://models/rec/v1/", "1.0.0", "tensorflow", {"user_id": "int", "items": "array"}, {"recommendations": "array"}),
        ("sentiment_v1", ModelFormat.ONNX, "s3://models/sentiment/v1/model.onnx", "1.0.0", "pytorch", {"text": "string"}, {"sentiment": "string", "confidence": "float"}),
        ("image_classifier_v1", ModelFormat.ONNX, "s3://models/image/v1/model.onnx", "1.0.0", "pytorch", {"image": "tensor"}, {"class": "int", "probabilities": "array"}),
        ("price_predictor_v1", ModelFormat.PICKLE, "s3://models/price/v1/model.pkl", "1.0.0", "sklearn", {"features": 20}, {"price": "float"}),
        ("demand_forecast_v1", ModelFormat.SAVEDMODEL, "s3://models/demand/v1/", "1.0.0", "tensorflow", {"time_series": "array"}, {"forecast": "array"})
    ]
    
    artifacts = []
    for name, fmt, path, ver, fw, inp, out in models_data:
        a = await platform.register_model(name, fmt, path, random.randint(10*1024*1024, 500*1024*1024), ver, fw, inp, out)
        artifacts.append(a)
        print(f"  📦 {name} ({fmt.value})")
        
    # Create Endpoints
    print("\n🔌 Creating Inference Endpoints...")
    
    endpoints_data = [
        ("churn-predictor", artifacts[0].artifact_id, InferenceMode.REALTIME, "ml.m5.large", 2, True, 2, 10),
        ("churn-predictor-v2", artifacts[1].artifact_id, InferenceMode.REALTIME, "ml.m5.large", 1, False, 1, 5),
        ("fraud-detector", artifacts[2].artifact_id, InferenceMode.REALTIME, "ml.c5.xlarge", 4, True, 4, 20),
        ("recommender", artifacts[3].artifact_id, InferenceMode.REALTIME, "ml.g4dn.xlarge", 2, True, 2, 8),
        ("sentiment-analyzer", artifacts[4].artifact_id, InferenceMode.REALTIME, "ml.m5.large", 2, True, 1, 6),
        ("image-classifier", artifacts[5].artifact_id, InferenceMode.REALTIME, "ml.g4dn.xlarge", 2, True, 2, 8),
        ("price-predictor", artifacts[6].artifact_id, InferenceMode.REALTIME, "ml.t3.medium", 1, False, 1, 3),
        ("demand-forecaster", artifacts[7].artifact_id, InferenceMode.BATCH, "ml.m5.xlarge", 4, False, 4, 10)
    ]
    
    endpoints = []
    for name, aid, mode, inst, count, auto, min_i, max_i in endpoints_data:
        ep = await platform.create_endpoint(name, aid, mode, inst, count, auto, min_i, max_i)
        if ep:
            endpoints.append(ep)
            print(f"  🔌 {name} ({mode.value})")
            
    # Configure Scaling
    print("\n⚡ Configuring Auto-Scaling...")
    
    scaling_data = [
        (endpoints[0].endpoint_id, ScalingPolicy.TARGET_TRACKING, "cpu_utilization", 70.0),
        (endpoints[2].endpoint_id, ScalingPolicy.TARGET_TRACKING, "request_count", 1000.0),
        (endpoints[3].endpoint_id, ScalingPolicy.TARGET_TRACKING, "gpu_utilization", 80.0),
        (endpoints[5].endpoint_id, ScalingPolicy.STEP_SCALING, "latency_ms", 50.0)
    ]
    
    for eid, policy, metric, target in scaling_data:
        await platform.configure_scaling(eid, policy, metric, target)
        
    print(f"  ⚡ Configured scaling for {len(scaling_data)} endpoints")
    
    # Configure Cache
    print("\n💾 Configuring Inference Cache...")
    
    cache_data = [
        (endpoints[0].endpoint_id, CacheStrategy.LRU, 2048, 3600),
        (endpoints[2].endpoint_id, CacheStrategy.TTL, 512, 60),
        (endpoints[3].endpoint_id, CacheStrategy.LFU, 4096, 7200),
        (endpoints[4].endpoint_id, CacheStrategy.LRU, 1024, 1800)
    ]
    
    for eid, strategy, size, ttl in cache_data:
        await platform.configure_cache(eid, strategy, size, ttl)
        
    print(f"  💾 Configured cache for {len(cache_data)} endpoints")
    
    # Invoke Models (Realtime)
    print("\n🚀 Invoking Models (Realtime)...")
    
    for _ in range(50):
        ep = random.choice(endpoints[:7])  # Skip batch endpoint
        await platform.invoke(ep.endpoint_id, {"features": [random.random() for _ in range(10)]})
        
    print(f"  🚀 Completed {len(platform.requests)} inference requests")
    
    # Batch Inference
    print("\n📊 Creating Batch Jobs...")
    
    batch_data = [
        (endpoints[7].endpoint_id, "demand_forecast_daily", "s3://data/demand/input/", "s3://data/demand/output/", "parquet", "parquet", 500, 20),
        (endpoints[0].endpoint_id, "churn_scoring_batch", "s3://data/churn/input/", "s3://data/churn/output/", "csv", "csv", 1000, 10)
    ]
    
    batch_jobs = []
    for eid, name, inp, out, inf, outf, bs, mc in batch_data:
        job = await platform.create_batch_job(eid, name, inp, out, inf, outf, bs, mc)
        if job:
            batch_jobs.append(job)
            await platform.run_batch_job(job.job_id)
            print(f"  📊 {name}: {job.processed_records:,}/{job.total_records:,} records")
            
    # Create A/B Tests
    print("\n🧪 Creating A/B Tests...")
    
    # Get deployments for churn endpoints
    churn_deps = [d for d in platform.deployments.values() if d.endpoint_id in [endpoints[0].endpoint_id, endpoints[1].endpoint_id]]
    
    if len(churn_deps) >= 2:
        ab_test = await platform.create_ab_test(
            "churn_model_v1_vs_v2",
            endpoints[0].endpoint_id,
            churn_deps[0].deployment_id,
            churn_deps[1].deployment_id if len(churn_deps) > 1 else churn_deps[0].deployment_id,
            50,
            "latency"
        )
        
        if ab_test:
            await platform.start_ab_test(ab_test.test_id)
            await platform.complete_ab_test(ab_test.test_id)
            print(f"  🧪 {ab_test.name}: Winner = {ab_test.winner}")
            
    # Create Monitors
    print("\n📡 Creating Model Monitors...")
    
    monitors = []
    for ep in endpoints[:5]:
        monitor = await platform.create_monitor(ep.endpoint_id)
        if monitor:
            monitors.append(monitor)
            
    print(f"  📡 Created {len(monitors)} monitors")
    
    # Run Monitoring
    print("\n🔍 Running Monitoring Checks...")
    
    all_alerts = []
    for monitor in monitors:
        alerts = await platform.run_monitoring_check(monitor.monitor_id)
        all_alerts.extend(alerts)
        
    print(f"  🔍 Generated {len(all_alerts)} alerts")
    
    # Collect Endpoint Metrics
    print("\n📈 Collecting Endpoint Metrics...")
    
    endpoint_metrics_list = []
    for ep in endpoints:
        metrics = await platform.collect_endpoint_metrics(ep.endpoint_id)
        if metrics:
            endpoint_metrics_list.append(metrics)
            
    print(f"  📈 Collected metrics for {len(endpoint_metrics_list)} endpoints")
    
    # Collect Platform Metrics
    platform_metrics = await platform.collect_platform_metrics()
    
    # Endpoints Dashboard
    print("\n🔌 Inference Endpoints:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Endpoint Name             │ Mode       │ Instance Type   │ Instances │ Status      │ Health   │ Auto-Scale │ URL                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for ep in endpoints:
        name = ep.name[:25].ljust(25)
        mode = ep.inference_mode.value[:10].ljust(10)
        inst_type = ep.instance_type[:15].ljust(15)
        instances = str(ep.instance_count).ljust(9)
        status = ep.status.value[:11].ljust(11)
        health = ep.health_status.value[:8].ljust(8)
        auto = "✓" if ep.auto_scaling else "✗"
        auto = auto.ljust(10)
        url = ep.url[:300]
        url = url.ljust(300)
        
        print(f"  │ {name} │ {mode} │ {inst_type} │ {instances} │ {status} │ {health} │ {auto} │ {url} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Endpoint Metrics Dashboard
    print("\n📈 Endpoint Performance Metrics:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Endpoint Name             │ Requests  │ Success   │ Avg Latency │ P95 Latency │ RPS     │ CPU %    │ Mem %                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for m in endpoint_metrics_list:
        ep = platform.endpoints.get(m.endpoint_id)
        name = ep.name if ep else "Unknown"
        name = name[:25].ljust(25)
        requests = str(m.total_requests).ljust(9)
        success = str(m.successful_requests).ljust(9)
        avg_lat = f"{m.avg_latency_ms:.1f}ms".ljust(11)
        p95_lat = f"{m.p95_latency_ms:.1f}ms".ljust(11)
        rps = f"{m.requests_per_second:.1f}".ljust(7)
        cpu = f"{m.cpu_utilization:.1f}%".ljust(8)
        mem = f"{m.memory_utilization:.1f}%".ljust(259)
        
        print(f"  │ {name} │ {requests} │ {success} │ {avg_lat} │ {p95_lat} │ {rps} │ {cpu} │ {mem} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Batch Jobs Dashboard
    print("\n📊 Batch Jobs:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Job Name                        │ Total Records │ Processed   │ Failed   │ Status      │ Duration                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for job in batch_jobs:
        name = job.name[:31].ljust(31)
        total = f"{job.total_records:,}".ljust(13)
        processed = f"{job.processed_records:,}".ljust(11)
        failed = f"{job.failed_records:,}".ljust(8)
        status = job.status[:11].ljust(11)
        
        duration = "N/A"
        if job.started_at and job.completed_at:
            dur = (job.completed_at - job.started_at).total_seconds()
            duration = f"{dur:.1f}s"
        duration = duration.ljust(296)
        
        print(f"  │ {name} │ {total} │ {processed} │ {failed} │ {status} │ {duration} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Model Artifacts: {stats['total_artifacts']}")
    print(f"  Endpoints: {stats['active_endpoints']}/{stats['total_endpoints']} active")
    print(f"  Requests: {stats['successful_requests']:,}/{stats['total_requests']:,} successful")
    print(f"  Batch Jobs: {stats['completed_jobs']}/{stats['total_batch_jobs']} completed")
    print(f"  A/B Tests: {stats['active_tests']}/{stats['total_ab_tests']} active")
    print(f"  Active Alerts: {stats['active_alerts']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                       ML Inference Platform                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Model Artifacts:               {stats['total_artifacts']:>12}                      │")
    print(f"│ Active Endpoints:              {stats['active_endpoints']:>12}                      │")
    print(f"│ Total Deployments:             {len(platform.deployments):>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Requests:                {stats['total_requests']:>12}                      │")
    print(f"│ Avg Latency (ms):              {platform_metrics.avg_latency_ms:>12.2f}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Batch Jobs:                    {stats['total_batch_jobs']:>12}                      │")
    print(f"│ A/B Tests:                     {stats['total_ab_tests']:>12}                      │")
    print(f"│ Active Alerts:                 {stats['active_alerts']:>12}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("ML Inference Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
