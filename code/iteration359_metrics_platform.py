#!/usr/bin/env python3
"""
Server Init - Iteration 359: Metrics Platform
Платформа метрик

Функционал:
- Metrics Collection - сбор метрик
- Time Series Storage - хранение временных рядов
- Query Engine - движок запросов
- Aggregations - агрегации
- Recording Rules - правила записи
- Alerting Rules - правила алертинга
- Dashboards - дашборды
- Cardinality Management - управление кардинальностью
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
import uuid
import json
import math


class MetricType(Enum):
    """Тип метрики"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AggregationType(Enum):
    """Тип агрегации"""
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    RATE = "rate"
    INCREASE = "increase"
    HISTOGRAM_QUANTILE = "histogram_quantile"


class AlertState(Enum):
    """Состояние алерта"""
    INACTIVE = "inactive"
    PENDING = "pending"
    FIRING = "firing"
    RESOLVED = "resolved"


class AlertSeverity(Enum):
    """Критичность алерта"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class TargetHealth(Enum):
    """Здоровье таргета"""
    UP = "up"
    DOWN = "down"
    UNKNOWN = "unknown"


class StorageStatus(Enum):
    """Статус хранилища"""
    ACTIVE = "active"
    READONLY = "readonly"
    COMPACTING = "compacting"


@dataclass
class MetricDescriptor:
    """Дескриптор метрики"""
    descriptor_id: str
    name: str
    
    # Type
    metric_type: MetricType = MetricType.GAUGE
    
    # Description
    description: str = ""
    
    # Unit
    unit: str = ""
    
    # Labels
    label_names: List[str] = field(default_factory=list)
    
    # Histogram buckets
    buckets: List[float] = field(default_factory=list)
    
    # Summary quantiles
    quantiles: List[float] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class MetricSample:
    """Сэмпл метрики"""
    sample_id: str
    metric_name: str
    
    # Value
    value: float = 0.0
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TimeSeries:
    """Временной ряд"""
    series_id: str
    metric_name: str
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Fingerprint (unique identifier)
    fingerprint: str = ""
    
    # Samples
    samples: List[Tuple[datetime, float]] = field(default_factory=list)
    
    # Stats
    sample_count: int = 0
    first_timestamp: Optional[datetime] = None
    last_timestamp: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ScrapeTarget:
    """Цель скрейпинга"""
    target_id: str
    job_name: str
    
    # Endpoint
    endpoint: str = ""
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Health
    health: TargetHealth = TargetHealth.UNKNOWN
    last_error: str = ""
    
    # Scrape config
    scrape_interval: str = "15s"
    scrape_timeout: str = "10s"
    
    # Stats
    last_scrape: Optional[datetime] = None
    scrape_duration_ms: float = 0.0
    samples_scraped: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ScrapeJob:
    """Задание скрейпинга"""
    job_id: str
    name: str
    
    # Config
    scrape_interval: str = "15s"
    scrape_timeout: str = "10s"
    
    # Metrics path
    metrics_path: str = "/metrics"
    
    # Scheme
    scheme: str = "http"
    
    # Targets
    static_targets: List[str] = field(default_factory=list)
    
    # Relabel configs
    relabel_configs: List[Dict[str, Any]] = field(default_factory=list)
    
    # Status
    is_enabled: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RecordingRule:
    """Правило записи"""
    rule_id: str
    name: str
    
    # Expression
    expr: str = ""
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Group
    group_name: str = ""
    
    # Interval
    interval: str = "15s"
    
    # Status
    is_enabled: bool = True
    last_evaluation: Optional[datetime] = None
    evaluation_duration_ms: float = 0.0
    
    # Stats
    samples_produced: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AlertRule:
    """Правило алерта"""
    rule_id: str
    name: str
    
    # Expression
    expr: str = ""
    
    # Duration
    for_duration: str = "5m"
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Annotations
    summary: str = ""
    description: str = ""
    
    # Severity
    severity: AlertSeverity = AlertSeverity.WARNING
    
    # Group
    group_name: str = ""
    
    # Status
    is_enabled: bool = True
    state: AlertState = AlertState.INACTIVE
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_evaluation: Optional[datetime] = None


@dataclass
class Alert:
    """Активный алерт"""
    alert_id: str
    rule_id: str
    
    # Name
    name: str = ""
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Annotations
    summary: str = ""
    description: str = ""
    
    # State
    state: AlertState = AlertState.PENDING
    
    # Severity
    severity: AlertSeverity = AlertSeverity.WARNING
    
    # Value
    value: float = 0.0
    
    # Timestamps
    active_at: datetime = field(default_factory=datetime.now)
    fired_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


@dataclass
class Query:
    """Запрос"""
    query_id: str
    
    # Expression
    expr: str = ""
    
    # Time range
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime = field(default_factory=datetime.now)
    
    # Step
    step: str = "15s"
    
    # Execution
    executed_at: datetime = field(default_factory=datetime.now)
    duration_ms: float = 0.0
    
    # Stats
    samples_processed: int = 0


@dataclass
class QueryResult:
    """Результат запроса"""
    result_id: str
    query_id: str
    
    # Result type
    result_type: str = "matrix"  # vector, matrix, scalar, string
    
    # Data
    data: List[Dict[str, Any]] = field(default_factory=list)
    
    # Stats
    series_count: int = 0
    sample_count: int = 0


@dataclass
class Dashboard:
    """Дашборд"""
    dashboard_id: str
    name: str
    
    # Description
    description: str = ""
    
    # Panels
    panels: List[Dict[str, Any]] = field(default_factory=list)
    
    # Variables
    variables: List[Dict[str, Any]] = field(default_factory=list)
    
    # Time range
    time_range: str = "1h"
    
    # Refresh
    refresh_interval: str = "30s"
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


@dataclass
class Panel:
    """Панель дашборда"""
    panel_id: str
    dashboard_id: str
    
    # Title
    title: str = ""
    
    # Type
    panel_type: str = "graph"  # graph, gauge, stat, table, heatmap
    
    # Queries
    queries: List[str] = field(default_factory=list)
    
    # Position
    grid_pos: Dict[str, int] = field(default_factory=dict)
    
    # Options
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StorageBlock:
    """Блок хранилища"""
    block_id: str
    
    # Time range
    min_time: datetime = field(default_factory=datetime.now)
    max_time: datetime = field(default_factory=datetime.now)
    
    # Stats
    num_samples: int = 0
    num_series: int = 0
    num_chunks: int = 0
    
    # Size
    size_bytes: int = 0
    
    # Status
    status: StorageStatus = StorageStatus.ACTIVE
    
    # Compaction
    compaction_level: int = 0


@dataclass
class CardinalityInfo:
    """Информация о кардинальности"""
    info_id: str
    
    # Total series
    total_series: int = 0
    
    # By label
    series_by_label: Dict[str, int] = field(default_factory=dict)
    
    # By metric
    series_by_metric: Dict[str, int] = field(default_factory=dict)
    
    # Top labels
    top_label_values: Dict[str, List[Tuple[str, int]]] = field(default_factory=dict)
    
    # Timestamps
    collected_at: datetime = field(default_factory=datetime.now)


@dataclass
class MetricsPlatformMetrics:
    """Метрики платформы"""
    metrics_id: str
    
    # Targets
    total_targets: int = 0
    targets_up: int = 0
    
    # Series
    total_series: int = 0
    total_samples: int = 0
    
    # Storage
    storage_size_gb: float = 0.0
    
    # Queries
    total_queries: int = 0
    avg_query_duration_ms: float = 0.0
    
    # Rules
    recording_rules: int = 0
    alert_rules: int = 0
    active_alerts: int = 0
    
    # Scrape
    samples_per_second: float = 0.0
    
    # Timestamps
    collected_at: datetime = field(default_factory=datetime.now)


class MetricsPlatform:
    """Платформа метрик"""
    
    def __init__(self, platform_name: str = "metrics"):
        self.platform_name = platform_name
        self.descriptors: Dict[str, MetricDescriptor] = {}
        self.samples: Dict[str, MetricSample] = {}
        self.time_series: Dict[str, TimeSeries] = {}
        self.targets: Dict[str, ScrapeTarget] = {}
        self.scrape_jobs: Dict[str, ScrapeJob] = {}
        self.recording_rules: Dict[str, RecordingRule] = {}
        self.alert_rules: Dict[str, AlertRule] = {}
        self.alerts: Dict[str, Alert] = {}
        self.queries: Dict[str, Query] = {}
        self.dashboards: Dict[str, Dashboard] = {}
        self.panels: Dict[str, Panel] = {}
        self.storage_blocks: Dict[str, StorageBlock] = {}
        
    async def register_metric(self, name: str,
                             metric_type: MetricType,
                             description: str = "",
                             unit: str = "",
                             label_names: List[str] = None,
                             buckets: List[float] = None,
                             quantiles: List[float] = None) -> MetricDescriptor:
        """Регистрация метрики"""
        descriptor = MetricDescriptor(
            descriptor_id=f"desc_{uuid.uuid4().hex[:8]}",
            name=name,
            metric_type=metric_type,
            description=description,
            unit=unit,
            label_names=label_names or [],
            buckets=buckets or [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],
            quantiles=quantiles or [0.5, 0.9, 0.99]
        )
        
        self.descriptors[descriptor.descriptor_id] = descriptor
        return descriptor
        
    async def record_sample(self, metric_name: str,
                           value: float,
                           labels: Dict[str, str] = None,
                           timestamp: Optional[datetime] = None) -> MetricSample:
        """Запись сэмпла"""
        sample = MetricSample(
            sample_id=f"smp_{uuid.uuid4().hex[:12]}",
            metric_name=metric_name,
            value=value,
            labels=labels or {},
            timestamp=timestamp or datetime.now()
        )
        
        self.samples[sample.sample_id] = sample
        
        # Update time series
        fingerprint = f"{metric_name}_{json.dumps(labels or {}, sort_keys=True)}"
        
        if fingerprint not in self.time_series:
            self.time_series[fingerprint] = TimeSeries(
                series_id=f"ts_{uuid.uuid4().hex[:8]}",
                metric_name=metric_name,
                labels=labels or {},
                fingerprint=fingerprint
            )
            
        series = self.time_series[fingerprint]
        series.samples.append((sample.timestamp, value))
        series.sample_count += 1
        
        if not series.first_timestamp or sample.timestamp < series.first_timestamp:
            series.first_timestamp = sample.timestamp
        if not series.last_timestamp or sample.timestamp > series.last_timestamp:
            series.last_timestamp = sample.timestamp
            
        # Keep last 10000 samples per series
        if len(series.samples) > 10000:
            series.samples = series.samples[-10000:]
            
        return sample
        
    async def create_scrape_job(self, name: str,
                               static_targets: List[str],
                               scrape_interval: str = "15s",
                               scrape_timeout: str = "10s",
                               metrics_path: str = "/metrics",
                               scheme: str = "http") -> ScrapeJob:
        """Создание задания скрейпинга"""
        job = ScrapeJob(
            job_id=f"job_{uuid.uuid4().hex[:8]}",
            name=name,
            scrape_interval=scrape_interval,
            scrape_timeout=scrape_timeout,
            metrics_path=metrics_path,
            scheme=scheme,
            static_targets=static_targets
        )
        
        self.scrape_jobs[job.job_id] = job
        
        # Create targets
        for target_endpoint in static_targets:
            target = ScrapeTarget(
                target_id=f"tgt_{uuid.uuid4().hex[:8]}",
                job_name=name,
                endpoint=target_endpoint,
                labels={"job": name, "instance": target_endpoint},
                scrape_interval=scrape_interval,
                scrape_timeout=scrape_timeout
            )
            self.targets[target.target_id] = target
            
        return job
        
    async def scrape_target(self, target_id: str) -> Optional[ScrapeTarget]:
        """Скрейпинг таргета"""
        target = self.targets.get(target_id)
        if not target:
            return None
            
        # Simulate scrape
        await asyncio.sleep(0.01)
        
        # Simulate success/failure
        if random.random() < 0.95:  # 95% success rate
            target.health = TargetHealth.UP
            target.last_error = ""
            target.samples_scraped = random.randint(100, 500)
            target.scrape_duration_ms = random.uniform(10, 100)
            
            # Generate sample metrics
            metrics_to_scrape = [
                ("up", 1.0),
                ("process_cpu_seconds_total", random.uniform(100, 10000)),
                ("process_resident_memory_bytes", random.uniform(50*1024*1024, 500*1024*1024)),
                ("http_requests_total", random.randint(1000, 100000)),
                ("http_request_duration_seconds_bucket", random.uniform(0, 10)),
            ]
            
            for metric_name, value in metrics_to_scrape:
                await self.record_sample(
                    metric_name,
                    value,
                    {"job": target.job_name, "instance": target.endpoint}
                )
        else:
            target.health = TargetHealth.DOWN
            target.last_error = "connection refused"
            target.samples_scraped = 0
            
        target.last_scrape = datetime.now()
        return target
        
    async def create_recording_rule(self, name: str,
                                   expr: str,
                                   labels: Dict[str, str] = None,
                                   group_name: str = "",
                                   interval: str = "15s") -> RecordingRule:
        """Создание правила записи"""
        rule = RecordingRule(
            rule_id=f"rr_{uuid.uuid4().hex[:8]}",
            name=name,
            expr=expr,
            labels=labels or {},
            group_name=group_name,
            interval=interval
        )
        
        self.recording_rules[rule.rule_id] = rule
        return rule
        
    async def evaluate_recording_rule(self, rule_id: str) -> Optional[RecordingRule]:
        """Оценка правила записи"""
        rule = self.recording_rules.get(rule_id)
        if not rule or not rule.is_enabled:
            return None
            
        start_time = datetime.now()
        
        # Simulate rule evaluation
        await asyncio.sleep(0.001)
        
        # Record result as new metric
        value = random.uniform(0, 100)
        await self.record_sample(rule.name, value, rule.labels)
        
        rule.last_evaluation = datetime.now()
        rule.evaluation_duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        rule.samples_produced += 1
        
        return rule
        
    async def create_alert_rule(self, name: str,
                               expr: str,
                               for_duration: str = "5m",
                               severity: AlertSeverity = AlertSeverity.WARNING,
                               labels: Dict[str, str] = None,
                               summary: str = "",
                               description: str = "",
                               group_name: str = "") -> AlertRule:
        """Создание правила алерта"""
        rule = AlertRule(
            rule_id=f"ar_{uuid.uuid4().hex[:8]}",
            name=name,
            expr=expr,
            for_duration=for_duration,
            severity=severity,
            labels=labels or {},
            summary=summary,
            description=description,
            group_name=group_name
        )
        
        self.alert_rules[rule.rule_id] = rule
        return rule
        
    async def evaluate_alert_rule(self, rule_id: str) -> List[Alert]:
        """Оценка правила алерта"""
        rule = self.alert_rules.get(rule_id)
        if not rule or not rule.is_enabled:
            return []
            
        new_alerts = []
        
        # Simulate alert evaluation
        if random.random() < 0.15:  # 15% chance of alert
            alert = Alert(
                alert_id=f"alt_{uuid.uuid4().hex[:8]}",
                rule_id=rule_id,
                name=rule.name,
                labels={**rule.labels, "alertname": rule.name},
                summary=rule.summary,
                description=rule.description,
                state=AlertState.FIRING,
                severity=rule.severity,
                value=random.uniform(80, 100),
                fired_at=datetime.now()
            )
            
            self.alerts[alert.alert_id] = alert
            new_alerts.append(alert)
            
            rule.state = AlertState.FIRING
        else:
            rule.state = AlertState.INACTIVE
            
        rule.last_evaluation = datetime.now()
        return new_alerts
        
    async def resolve_alert(self, alert_id: str) -> Optional[Alert]:
        """Разрешение алерта"""
        alert = self.alerts.get(alert_id)
        if not alert:
            return None
            
        alert.state = AlertState.RESOLVED
        alert.resolved_at = datetime.now()
        
        return alert
        
    async def query_instant(self, expr: str) -> QueryResult:
        """Мгновенный запрос"""
        query = Query(
            query_id=f"qry_{uuid.uuid4().hex[:8]}",
            expr=expr,
            start_time=datetime.now(),
            end_time=datetime.now()
        )
        
        # Simulate query execution
        await asyncio.sleep(0.001)
        
        # Find matching series
        results = []
        for series in self.time_series.values():
            if expr in series.metric_name or expr == "*":
                if series.samples:
                    latest = series.samples[-1]
                    results.append({
                        "metric": {"__name__": series.metric_name, **series.labels},
                        "value": [latest[0].timestamp(), latest[1]]
                    })
                    
        query.duration_ms = random.uniform(1, 50)
        query.samples_processed = sum(s.sample_count for s in self.time_series.values())
        self.queries[query.query_id] = query
        
        return QueryResult(
            result_id=f"res_{uuid.uuid4().hex[:8]}",
            query_id=query.query_id,
            result_type="vector",
            data=results[:100],
            series_count=len(results),
            sample_count=len(results)
        )
        
    async def query_range(self, expr: str,
                         start_time: datetime,
                         end_time: datetime,
                         step: str = "15s") -> QueryResult:
        """Запрос диапазона"""
        query = Query(
            query_id=f"qry_{uuid.uuid4().hex[:8]}",
            expr=expr,
            start_time=start_time,
            end_time=end_time,
            step=step
        )
        
        # Simulate query execution
        await asyncio.sleep(0.005)
        
        # Find matching series
        results = []
        for series in self.time_series.values():
            if expr in series.metric_name or expr == "*":
                values = [
                    [s[0].timestamp(), s[1]]
                    for s in series.samples
                    if start_time <= s[0] <= end_time
                ]
                if values:
                    results.append({
                        "metric": {"__name__": series.metric_name, **series.labels},
                        "values": values[-100:]  # Limit samples
                    })
                    
        query.duration_ms = random.uniform(10, 200)
        query.samples_processed = sum(len(r.get("values", [])) for r in results)
        self.queries[query.query_id] = query
        
        return QueryResult(
            result_id=f"res_{uuid.uuid4().hex[:8]}",
            query_id=query.query_id,
            result_type="matrix",
            data=results[:50],
            series_count=len(results),
            sample_count=query.samples_processed
        )
        
    async def create_dashboard(self, name: str,
                              description: str = "",
                              time_range: str = "1h",
                              refresh_interval: str = "30s",
                              tags: List[str] = None) -> Dashboard:
        """Создание дашборда"""
        dashboard = Dashboard(
            dashboard_id=f"db_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            time_range=time_range,
            refresh_interval=refresh_interval,
            tags=tags or []
        )
        
        self.dashboards[dashboard.dashboard_id] = dashboard
        return dashboard
        
    async def add_panel(self, dashboard_id: str,
                       title: str,
                       panel_type: str,
                       queries: List[str],
                       grid_pos: Dict[str, int] = None) -> Optional[Panel]:
        """Добавление панели"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            return None
            
        panel = Panel(
            panel_id=f"pnl_{uuid.uuid4().hex[:8]}",
            dashboard_id=dashboard_id,
            title=title,
            panel_type=panel_type,
            queries=queries,
            grid_pos=grid_pos or {"x": 0, "y": 0, "w": 12, "h": 8}
        )
        
        self.panels[panel.panel_id] = panel
        dashboard.panels.append({
            "panel_id": panel.panel_id,
            "title": title,
            "type": panel_type
        })
        
        return panel
        
    async def get_cardinality(self) -> CardinalityInfo:
        """Получение информации о кардинальности"""
        series_by_metric = {}
        series_by_label = {}
        label_values = {}
        
        for series in self.time_series.values():
            # By metric
            series_by_metric[series.metric_name] = series_by_metric.get(series.metric_name, 0) + 1
            
            # By label
            for label_name, label_value in series.labels.items():
                series_by_label[label_name] = series_by_label.get(label_name, 0) + 1
                
                if label_name not in label_values:
                    label_values[label_name] = {}
                label_values[label_name][label_value] = label_values[label_name].get(label_value, 0) + 1
                
        # Get top label values
        top_label_values = {}
        for label_name, values in label_values.items():
            sorted_values = sorted(values.items(), key=lambda x: x[1], reverse=True)[:10]
            top_label_values[label_name] = sorted_values
            
        return CardinalityInfo(
            info_id=f"card_{uuid.uuid4().hex[:8]}",
            total_series=len(self.time_series),
            series_by_label=series_by_label,
            series_by_metric=series_by_metric,
            top_label_values=top_label_values
        )
        
    async def compact_storage(self) -> StorageBlock:
        """Компактификация хранилища"""
        # Simulate compaction
        total_samples = sum(s.sample_count for s in self.time_series.values())
        total_series = len(self.time_series)
        
        block = StorageBlock(
            block_id=f"blk_{uuid.uuid4().hex[:8]}",
            min_time=datetime.now() - timedelta(hours=2),
            max_time=datetime.now(),
            num_samples=total_samples,
            num_series=total_series,
            num_chunks=total_series * 10,
            size_bytes=total_samples * 16,  # ~16 bytes per sample
            status=StorageStatus.ACTIVE,
            compaction_level=1
        )
        
        self.storage_blocks[block.block_id] = block
        return block
        
    async def collect_metrics(self) -> MetricsPlatformMetrics:
        """Сбор метрик платформы"""
        targets_up = sum(1 for t in self.targets.values() if t.health == TargetHealth.UP)
        total_samples = sum(s.sample_count for s in self.time_series.values())
        storage_size = sum(b.size_bytes for b in self.storage_blocks.values())
        
        query_durations = [q.duration_ms for q in self.queries.values()]
        active_alerts = sum(1 for a in self.alerts.values() if a.state == AlertState.FIRING)
        
        return MetricsPlatformMetrics(
            metrics_id=f"mpm_{uuid.uuid4().hex[:8]}",
            total_targets=len(self.targets),
            targets_up=targets_up,
            total_series=len(self.time_series),
            total_samples=total_samples,
            storage_size_gb=storage_size / (1024**3),
            total_queries=len(self.queries),
            avg_query_duration_ms=sum(query_durations) / len(query_durations) if query_durations else 0.0,
            recording_rules=len(self.recording_rules),
            alert_rules=len(self.alert_rules),
            active_alerts=active_alerts,
            samples_per_second=random.uniform(10000, 100000)
        )
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        targets_up = sum(1 for t in self.targets.values() if t.health == TargetHealth.UP)
        active_alerts = sum(1 for a in self.alerts.values() if a.state == AlertState.FIRING)
        total_samples = sum(s.sample_count for s in self.time_series.values())
        
        return {
            "total_descriptors": len(self.descriptors),
            "total_series": len(self.time_series),
            "total_samples": total_samples,
            "total_targets": len(self.targets),
            "targets_up": targets_up,
            "scrape_jobs": len(self.scrape_jobs),
            "recording_rules": len(self.recording_rules),
            "alert_rules": len(self.alert_rules),
            "active_alerts": active_alerts,
            "total_queries": len(self.queries),
            "total_dashboards": len(self.dashboards),
            "storage_blocks": len(self.storage_blocks)
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 359: Metrics Platform")
    print("=" * 60)
    
    platform = MetricsPlatform(platform_name="enterprise-metrics")
    print("✓ Metrics Platform initialized")
    
    # Register Metrics
    print("\n📊 Registering Metrics...")
    
    metrics_data = [
        ("http_requests_total", MetricType.COUNTER, "Total HTTP requests", "requests", ["method", "status", "handler"]),
        ("http_request_duration_seconds", MetricType.HISTOGRAM, "HTTP request latency", "seconds", ["method", "handler"]),
        ("http_requests_in_flight", MetricType.GAUGE, "HTTP requests currently in flight", "requests", ["handler"]),
        ("process_cpu_seconds_total", MetricType.COUNTER, "Total user and system CPU time", "seconds", []),
        ("process_resident_memory_bytes", MetricType.GAUGE, "Resident memory size", "bytes", []),
        ("go_goroutines", MetricType.GAUGE, "Number of goroutines", "goroutines", []),
        ("database_connections", MetricType.GAUGE, "Number of database connections", "connections", ["state"]),
        ("cache_hits_total", MetricType.COUNTER, "Total cache hits", "hits", ["cache"]),
        ("cache_misses_total", MetricType.COUNTER, "Total cache misses", "misses", ["cache"]),
        ("kafka_consumer_lag", MetricType.GAUGE, "Kafka consumer lag", "messages", ["topic", "partition"])
    ]
    
    for name, mtype, desc, unit, labels in metrics_data:
        await platform.register_metric(name, mtype, desc, unit, labels)
        print(f"  📊 {name} ({mtype.value})")
        
    # Create Scrape Jobs
    print("\n🔧 Creating Scrape Jobs...")
    
    jobs_data = [
        ("api-gateway", ["api-gateway-1:9090", "api-gateway-2:9090", "api-gateway-3:9090"]),
        ("auth-service", ["auth-service-1:9090", "auth-service-2:9090"]),
        ("order-service", ["order-service-1:9090", "order-service-2:9090", "order-service-3:9090"]),
        ("payment-service", ["payment-service-1:9090", "payment-service-2:9090"]),
        ("user-service", ["user-service-1:9090", "user-service-2:9090"]),
        ("postgres-exporter", ["postgres-exporter:9187"]),
        ("redis-exporter", ["redis-exporter:9121"]),
        ("kafka-exporter", ["kafka-exporter:9308"]),
        ("node-exporter", ["node-1:9100", "node-2:9100", "node-3:9100", "node-4:9100", "node-5:9100"])
    ]
    
    for name, targets in jobs_data:
        await platform.create_scrape_job(name, targets, "15s", "10s")
        print(f"  🔧 {name}: {len(targets)} targets")
        
    # Scrape Targets
    print("\n🔄 Scraping Targets...")
    
    for target in list(platform.targets.values()):
        await platform.scrape_target(target.target_id)
        
    targets_up = sum(1 for t in platform.targets.values() if t.health == TargetHealth.UP)
    print(f"  🔄 Scraped {len(platform.targets)} targets ({targets_up} up)")
    
    # Record Additional Metrics
    print("\n📈 Recording Metrics...")
    
    services = ["api-gateway", "auth-service", "order-service", "payment-service", "user-service"]
    methods = ["GET", "POST", "PUT", "DELETE"]
    status_codes = ["200", "201", "400", "404", "500"]
    
    for _ in range(500):
        service = random.choice(services)
        method = random.choice(methods)
        status = random.choice(status_codes)
        
        await platform.record_sample(
            "http_requests_total",
            random.randint(1, 100),
            {"job": service, "method": method, "status": status}
        )
        
        await platform.record_sample(
            "http_request_duration_seconds",
            random.uniform(0.001, 1.0),
            {"job": service, "method": method}
        )
        
    print(f"  📈 Recorded {len(platform.samples)} samples in {len(platform.time_series)} series")
    
    # Create Recording Rules
    print("\n📝 Creating Recording Rules...")
    
    recording_rules_data = [
        ("job:http_requests:rate5m", "sum(rate(http_requests_total[5m])) by (job)", "http_rules"),
        ("job:http_errors:rate5m", "sum(rate(http_requests_total{status=~'5..'}[5m])) by (job)", "http_rules"),
        ("job:http_request_duration:p95", "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, job))", "http_rules"),
        ("instance:cpu:rate5m", "sum(rate(process_cpu_seconds_total[5m])) by (instance)", "resource_rules"),
        ("instance:memory:avg", "avg(process_resident_memory_bytes) by (instance)", "resource_rules")
    ]
    
    for name, expr, group in recording_rules_data:
        await platform.create_recording_rule(name, expr, {}, group)
        print(f"  📝 {name}")
        
    # Evaluate Recording Rules
    for rule_id in list(platform.recording_rules.keys()):
        await platform.evaluate_recording_rule(rule_id)
        
    # Create Alert Rules
    print("\n🚨 Creating Alert Rules...")
    
    alert_rules_data = [
        ("HighErrorRate", "sum(rate(http_requests_total{status=~'5..'}[5m])) / sum(rate(http_requests_total[5m])) > 0.01", "5m", AlertSeverity.CRITICAL, "High HTTP error rate", "Error rate is above 1%"),
        ("HighLatency", "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le)) > 1", "5m", AlertSeverity.WARNING, "High request latency", "P95 latency is above 1s"),
        ("HighCPU", "sum(rate(process_cpu_seconds_total[5m])) by (instance) > 0.9", "5m", AlertSeverity.WARNING, "High CPU usage", "CPU usage is above 90%"),
        ("HighMemory", "process_resident_memory_bytes / 1e9 > 4", "5m", AlertSeverity.WARNING, "High memory usage", "Memory usage is above 4GB"),
        ("TargetDown", "up == 0", "1m", AlertSeverity.CRITICAL, "Target is down", "Scrape target is unreachable"),
        ("KafkaLag", "kafka_consumer_lag > 10000", "5m", AlertSeverity.WARNING, "High Kafka lag", "Consumer lag is above 10000"),
        ("DatabaseConnections", "database_connections > 100", "5m", AlertSeverity.WARNING, "High DB connections", "Database connections above 100"),
        ("LowCacheHitRate", "rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m])) < 0.8", "5m", AlertSeverity.INFO, "Low cache hit rate", "Cache hit rate below 80%")
    ]
    
    for name, expr, duration, severity, summary, desc in alert_rules_data:
        await platform.create_alert_rule(name, expr, duration, severity, {}, summary, desc, "alerts")
        print(f"  🚨 {name} ({severity.value})")
        
    # Evaluate Alert Rules
    print("\n⚡ Evaluating Alert Rules...")
    
    all_alerts = []
    for rule_id in list(platform.alert_rules.keys()):
        alerts = await platform.evaluate_alert_rule(rule_id)
        all_alerts.extend(alerts)
        
    print(f"  ⚡ {len(all_alerts)} alerts fired")
    
    # Execute Queries
    print("\n🔍 Executing Queries...")
    
    queries_data = [
        "http_requests_total",
        "http_request_duration_seconds",
        "process_cpu_seconds_total",
        "up"
    ]
    
    for expr in queries_data:
        result = await platform.query_instant(expr)
        print(f"  🔍 {expr}: {result.series_count} series")
        
    # Range Query
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)
    range_result = await platform.query_range("http_requests_total", start_time, end_time, "1m")
    print(f"  🔍 Range query: {range_result.sample_count} samples")
    
    # Create Dashboards
    print("\n📈 Creating Dashboards...")
    
    dashboards_data = [
        ("Service Overview", "Main service metrics", ["overview", "sre"]),
        ("HTTP Metrics", "HTTP request metrics", ["http", "traffic"]),
        ("Resource Usage", "CPU and memory usage", ["resources", "infrastructure"]),
        ("Database Metrics", "Database performance", ["database", "postgres"]),
        ("Kafka Metrics", "Kafka consumer metrics", ["kafka", "messaging"]),
        ("Alert Dashboard", "Active alerts overview", ["alerts", "oncall"])
    ]
    
    for name, desc, tags in dashboards_data:
        db = await platform.create_dashboard(name, desc, "1h", "30s", tags)
        
        # Add panels
        await platform.add_panel(db.dashboard_id, "Request Rate", "graph", ["rate(http_requests_total[5m])"], {"x": 0, "y": 0, "w": 12, "h": 8})
        await platform.add_panel(db.dashboard_id, "Error Rate", "graph", ["rate(http_requests_total{status=~'5..'}[5m])"], {"x": 12, "y": 0, "w": 12, "h": 8})
        await platform.add_panel(db.dashboard_id, "Latency P95", "graph", ["histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"], {"x": 0, "y": 8, "w": 12, "h": 8})
        await platform.add_panel(db.dashboard_id, "Active Targets", "stat", ["count(up)"], {"x": 12, "y": 8, "w": 6, "h": 4})
        
        print(f"  📈 {name} ({len(db.panels)} panels)")
        
    # Get Cardinality Info
    print("\n📊 Cardinality Analysis...")
    
    cardinality = await platform.get_cardinality()
    print(f"  📊 Total series: {cardinality.total_series}")
    print(f"  📊 Top metrics by series count:")
    for metric, count in sorted(cardinality.series_by_metric.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"      - {metric}: {count}")
        
    # Compact Storage
    print("\n💾 Compacting Storage...")
    
    block = await platform.compact_storage()
    print(f"  💾 Block created: {block.num_samples:,} samples, {block.size_bytes / 1024:.1f} KB")
    
    # Collect Platform Metrics
    platform_metrics = await platform.collect_metrics()
    
    # Targets Dashboard
    print("\n🎯 Scrape Targets:")
    
    # Group by job
    targets_by_job = {}
    for target in platform.targets.values():
        if target.job_name not in targets_by_job:
            targets_by_job[target.job_name] = []
        targets_by_job[target.job_name].append(target)
        
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Job Name                │ Targets   │ Up    │ Down  │ Samples/Scrape │ Avg Duration                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for job_name, targets in sorted(targets_by_job.items()):
        total = len(targets)
        up = sum(1 for t in targets if t.health == TargetHealth.UP)
        down = total - up
        avg_samples = sum(t.samples_scraped for t in targets) / total if total > 0 else 0
        avg_duration = sum(t.scrape_duration_ms for t in targets) / total if total > 0 else 0
        
        name = job_name[:23].ljust(23)
        targets_str = str(total).ljust(9)
        up_str = str(up).ljust(5)
        down_str = str(down).ljust(5)
        samples = f"{avg_samples:.0f}".ljust(14)
        duration = f"{avg_duration:.1f}ms".ljust(266)
        
        print(f"  │ {name} │ {targets_str} │ {up_str} │ {down_str} │ {samples} │ {duration} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Alert Rules Dashboard
    print("\n🚨 Alert Rules:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Alert Name                   │ Severity    │ State      │ For       │ Summary                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for rule in platform.alert_rules.values():
        name = rule.name[:28].ljust(28)
        severity = rule.severity.value[:11].ljust(11)
        state = rule.state.value[:10].ljust(10)
        for_dur = rule.for_duration[:9].ljust(9)
        summary = rule.summary[:245].ljust(245)
        
        print(f"  │ {name} │ {severity} │ {state} │ {for_dur} │ {summary} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Metric Descriptors: {stats['total_descriptors']}")
    print(f"  Time Series: {stats['total_series']:,}")
    print(f"  Total Samples: {stats['total_samples']:,}")
    print(f"  Scrape Targets: {stats['targets_up']}/{stats['total_targets']} up")
    print(f"  Recording Rules: {stats['recording_rules']}")
    print(f"  Alert Rules: {stats['alert_rules']} ({stats['active_alerts']} firing)")
    print(f"  Dashboards: {stats['total_dashboards']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                         Metrics Platform                           │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Time Series:             {stats['total_series']:>12}                      │")
    print(f"│ Total Samples:                 {stats['total_samples']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Scrape Targets:                {stats['total_targets']:>12}                      │")
    print(f"│ Targets Up:                    {stats['targets_up']:>12}                      │")
    print(f"│ Samples/Second:                {platform_metrics.samples_per_second:>12.0f}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Recording Rules:               {stats['recording_rules']:>12}                      │")
    print(f"│ Alert Rules:                   {stats['alert_rules']:>12}                      │")
    print(f"│ Active Alerts:                 {stats['active_alerts']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Queries:                 {stats['total_queries']:>12}                      │")
    print(f"│ Avg Query Duration (ms):       {platform_metrics.avg_query_duration_ms:>12.2f}                      │")
    print(f"│ Storage Size (GB):             {platform_metrics.storage_size_gb:>12.4f}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Metrics Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
