#!/usr/bin/env python3
"""
Server Init - Iteration 357: Observability Platform
Комплексная платформа наблюдаемости

Функционал:
- Unified Telemetry - унифицированная телеметрия
- Distributed Tracing - распределённая трассировка
- Metrics Collection - сбор метрик
- Log Aggregation - агрегация логов
- Service Maps - карты сервисов
- Alerting - алертинг
- Dashboards - дашборды
- SLO/SLI Tracking - трекинг SLO/SLI
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import json


class TelemetryType(Enum):
    """Тип телеметрии"""
    TRACES = "traces"
    METRICS = "metrics"
    LOGS = "logs"


class SignalType(Enum):
    """Тип сигнала"""
    TRACE = "trace"
    SPAN = "span"
    METRIC = "metric"
    LOG = "log"
    EVENT = "event"


class MetricType(Enum):
    """Тип метрики"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class LogLevel(Enum):
    """Уровень лога"""
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    FATAL = "fatal"


class AlertSeverity(Enum):
    """Критичность алерта"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertState(Enum):
    """Состояние алерта"""
    PENDING = "pending"
    FIRING = "firing"
    RESOLVED = "resolved"


class SLOType(Enum):
    """Тип SLO"""
    AVAILABILITY = "availability"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"


class ComparisonOp(Enum):
    """Операция сравнения"""
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="
    EQ = "=="
    NEQ = "!="


@dataclass
class Service:
    """Сервис"""
    service_id: str
    name: str
    
    # Metadata
    version: str = ""
    environment: str = "production"
    namespace: str = "default"
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Health
    is_healthy: bool = True
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_seen: Optional[datetime] = None


@dataclass
class Span:
    """Спан трейса"""
    span_id: str
    trace_id: str
    
    # Name
    name: str = ""
    service_name: str = ""
    
    # Parent
    parent_span_id: Optional[str] = None
    
    # Timing
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_ms: float = 0.0
    
    # Status
    status_code: str = "OK"  # OK, ERROR, UNSET
    
    # Attributes
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    # Events
    events: List[Dict[str, Any]] = field(default_factory=list)
    
    # Resource
    resource: Dict[str, str] = field(default_factory=dict)


@dataclass
class Trace:
    """Трейс"""
    trace_id: str
    
    # Spans
    root_span_id: str = ""
    span_count: int = 0
    
    # Services
    services: Set[str] = field(default_factory=set)
    
    # Timing
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_ms: float = 0.0
    
    # Status
    has_errors: bool = False


@dataclass
class Metric:
    """Метрика"""
    metric_id: str
    name: str
    
    # Type
    metric_type: MetricType = MetricType.GAUGE
    
    # Value
    value: float = 0.0
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Unit
    unit: str = ""
    
    # Description
    description: str = ""
    
    # Timestamps
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MetricSeries:
    """Временной ряд метрики"""
    series_id: str
    metric_name: str
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Datapoints
    datapoints: List[tuple] = field(default_factory=list)  # (timestamp, value)
    
    # Aggregation
    aggregation: str = "avg"  # avg, sum, min, max, count


@dataclass
class LogEntry:
    """Запись лога"""
    log_id: str
    
    # Content
    message: str = ""
    
    # Level
    level: LogLevel = LogLevel.INFO
    
    # Context
    service_name: str = ""
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    
    # Attributes
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    # Resource
    resource: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AlertRule:
    """Правило алерта"""
    rule_id: str
    name: str
    
    # Query
    metric_query: str = ""
    
    # Condition
    comparison_op: ComparisonOp = ComparisonOp.GT
    threshold: float = 0.0
    
    # Duration
    for_duration: str = "5m"  # Alert fires after condition is true for this duration
    
    # Severity
    severity: AlertSeverity = AlertSeverity.WARNING
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Annotations
    summary: str = ""
    description: str = ""
    
    # Notification
    notification_channels: List[str] = field(default_factory=list)
    
    # Status
    is_enabled: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Alert:
    """Алерт"""
    alert_id: str
    rule_id: str
    
    # Details
    name: str = ""
    
    # State
    state: AlertState = AlertState.PENDING
    
    # Severity
    severity: AlertSeverity = AlertSeverity.WARNING
    
    # Value
    current_value: float = 0.0
    threshold: float = 0.0
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Annotations
    summary: str = ""
    description: str = ""
    
    # Timestamps
    started_at: datetime = field(default_factory=datetime.now)
    fired_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


@dataclass
class SLO:
    """Service Level Objective"""
    slo_id: str
    name: str
    service_name: str
    
    # Type
    slo_type: SLOType = SLOType.AVAILABILITY
    
    # Target
    target: float = 99.9  # Percentage
    
    # Window
    window_days: int = 30
    
    # Query
    total_query: str = ""
    good_query: str = ""
    
    # Current
    current_value: float = 100.0
    error_budget_remaining: float = 100.0
    
    # Status
    is_breached: bool = False
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SLI:
    """Service Level Indicator"""
    sli_id: str
    slo_id: str
    
    # Values
    total_events: int = 0
    good_events: int = 0
    
    # Rate
    success_rate: float = 100.0
    
    # Window
    window_start: datetime = field(default_factory=datetime.now)
    window_end: Optional[datetime] = None


@dataclass
class Dashboard:
    """Дашборд"""
    dashboard_id: str
    name: str
    
    # Description
    description: str = ""
    
    # Layout
    panels: List[Dict[str, Any]] = field(default_factory=list)
    
    # Variables
    variables: Dict[str, Any] = field(default_factory=dict)
    
    # Time range
    time_range: str = "1h"  # 1h, 6h, 24h, 7d, 30d
    
    # Refresh
    refresh_interval: str = "1m"
    
    # Sharing
    is_public: bool = False
    
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
    
    # Name
    title: str = ""
    
    # Type
    panel_type: str = "graph"  # graph, gauge, stat, table, logs, trace
    
    # Query
    query: str = ""
    
    # Position
    x: int = 0
    y: int = 0
    width: int = 12
    height: int = 8
    
    # Options
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceMap:
    """Карта сервисов"""
    map_id: str
    name: str
    
    # Nodes
    nodes: List[Dict[str, Any]] = field(default_factory=list)
    
    # Edges
    edges: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timestamps
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ObservabilityMetrics:
    """Метрики платформы наблюдаемости"""
    metrics_id: str
    
    # Services
    total_services: int = 0
    healthy_services: int = 0
    
    # Traces
    total_traces: int = 0
    traces_with_errors: int = 0
    avg_trace_duration_ms: float = 0.0
    
    # Metrics
    total_metric_series: int = 0
    metrics_ingestion_rate: float = 0.0
    
    # Logs
    total_logs: int = 0
    logs_ingestion_rate: float = 0.0
    
    # Alerts
    active_alerts: int = 0
    
    # SLOs
    total_slos: int = 0
    breached_slos: int = 0
    
    # Timestamps
    collected_at: datetime = field(default_factory=datetime.now)


class ObservabilityPlatform:
    """Платформа наблюдаемости"""
    
    def __init__(self, platform_name: str = "observability"):
        self.platform_name = platform_name
        self.services: Dict[str, Service] = {}
        self.traces: Dict[str, Trace] = {}
        self.spans: Dict[str, Span] = {}
        self.metrics: Dict[str, Metric] = {}
        self.metric_series: Dict[str, MetricSeries] = {}
        self.logs: Dict[str, LogEntry] = {}
        self.alert_rules: Dict[str, AlertRule] = {}
        self.alerts: Dict[str, Alert] = {}
        self.slos: Dict[str, SLO] = {}
        self.slis: Dict[str, SLI] = {}
        self.dashboards: Dict[str, Dashboard] = {}
        self.panels: Dict[str, Panel] = {}
        self.service_maps: Dict[str, ServiceMap] = {}
        
    async def register_service(self, name: str,
                              version: str = "",
                              environment: str = "production",
                              namespace: str = "default",
                              tags: Dict[str, str] = None,
                              dependencies: List[str] = None) -> Service:
        """Регистрация сервиса"""
        service = Service(
            service_id=f"svc_{uuid.uuid4().hex[:8]}",
            name=name,
            version=version,
            environment=environment,
            namespace=namespace,
            tags=tags or {},
            dependencies=dependencies or [],
            last_seen=datetime.now()
        )
        
        self.services[service.service_id] = service
        return service
        
    async def start_trace(self, service_name: str,
                         span_name: str,
                         attributes: Dict[str, Any] = None) -> tuple:
        """Начало трейса"""
        trace_id = uuid.uuid4().hex
        span_id = uuid.uuid4().hex[:16]
        
        trace = Trace(
            trace_id=trace_id,
            root_span_id=span_id,
            span_count=1,
            services={service_name}
        )
        
        span = Span(
            span_id=span_id,
            trace_id=trace_id,
            name=span_name,
            service_name=service_name,
            attributes=attributes or {},
            resource={"service.name": service_name}
        )
        
        self.traces[trace_id] = trace
        self.spans[span_id] = span
        
        return trace, span
        
    async def add_span(self, trace_id: str,
                      parent_span_id: str,
                      service_name: str,
                      span_name: str,
                      attributes: Dict[str, Any] = None) -> Optional[Span]:
        """Добавление спана"""
        trace = self.traces.get(trace_id)
        if not trace:
            return None
            
        span = Span(
            span_id=uuid.uuid4().hex[:16],
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            name=span_name,
            service_name=service_name,
            attributes=attributes or {},
            resource={"service.name": service_name}
        )
        
        self.spans[span.span_id] = span
        trace.span_count += 1
        trace.services.add(service_name)
        
        return span
        
    async def end_span(self, span_id: str,
                      status_code: str = "OK",
                      attributes: Dict[str, Any] = None) -> Optional[Span]:
        """Завершение спана"""
        span = self.spans.get(span_id)
        if not span:
            return None
            
        span.end_time = datetime.now()
        span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
        span.status_code = status_code
        
        if attributes:
            span.attributes.update(attributes)
            
        # Update trace
        trace = self.traces.get(span.trace_id)
        if trace:
            if status_code == "ERROR":
                trace.has_errors = True
                
            if span.span_id == trace.root_span_id:
                trace.end_time = span.end_time
                trace.duration_ms = span.duration_ms
                
        return span
        
    async def record_metric(self, name: str,
                           value: float,
                           metric_type: MetricType = MetricType.GAUGE,
                           labels: Dict[str, str] = None,
                           unit: str = "",
                           description: str = "") -> Metric:
        """Запись метрики"""
        metric = Metric(
            metric_id=f"met_{uuid.uuid4().hex[:8]}",
            name=name,
            metric_type=metric_type,
            value=value,
            labels=labels or {},
            unit=unit,
            description=description
        )
        
        self.metrics[metric.metric_id] = metric
        
        # Update series
        series_key = f"{name}_{json.dumps(labels or {}, sort_keys=True)}"
        if series_key not in self.metric_series:
            self.metric_series[series_key] = MetricSeries(
                series_id=f"ser_{uuid.uuid4().hex[:8]}",
                metric_name=name,
                labels=labels or {}
            )
            
        series = self.metric_series[series_key]
        series.datapoints.append((metric.timestamp, value))
        
        # Keep last 1000 datapoints
        if len(series.datapoints) > 1000:
            series.datapoints = series.datapoints[-1000:]
            
        return metric
        
    async def log(self, message: str,
                 level: LogLevel = LogLevel.INFO,
                 service_name: str = "",
                 trace_id: Optional[str] = None,
                 span_id: Optional[str] = None,
                 attributes: Dict[str, Any] = None) -> LogEntry:
        """Запись лога"""
        log_entry = LogEntry(
            log_id=f"log_{uuid.uuid4().hex[:12]}",
            message=message,
            level=level,
            service_name=service_name,
            trace_id=trace_id,
            span_id=span_id,
            attributes=attributes or {},
            resource={"service.name": service_name} if service_name else {}
        )
        
        self.logs[log_entry.log_id] = log_entry
        return log_entry
        
    async def create_alert_rule(self, name: str,
                               metric_query: str,
                               comparison_op: ComparisonOp,
                               threshold: float,
                               severity: AlertSeverity = AlertSeverity.WARNING,
                               for_duration: str = "5m",
                               summary: str = "",
                               description: str = "",
                               notification_channels: List[str] = None) -> AlertRule:
        """Создание правила алерта"""
        rule = AlertRule(
            rule_id=f"ar_{uuid.uuid4().hex[:8]}",
            name=name,
            metric_query=metric_query,
            comparison_op=comparison_op,
            threshold=threshold,
            severity=severity,
            for_duration=for_duration,
            summary=summary,
            description=description,
            notification_channels=notification_channels or []
        )
        
        self.alert_rules[rule.rule_id] = rule
        return rule
        
    async def evaluate_alert_rules(self) -> List[Alert]:
        """Оценка правил алертов"""
        new_alerts = []
        
        for rule in self.alert_rules.values():
            if not rule.is_enabled:
                continue
                
            # Simulate metric evaluation
            current_value = random.uniform(0, 100)
            
            is_firing = False
            if rule.comparison_op == ComparisonOp.GT:
                is_firing = current_value > rule.threshold
            elif rule.comparison_op == ComparisonOp.GTE:
                is_firing = current_value >= rule.threshold
            elif rule.comparison_op == ComparisonOp.LT:
                is_firing = current_value < rule.threshold
            elif rule.comparison_op == ComparisonOp.LTE:
                is_firing = current_value <= rule.threshold
                
            if is_firing and random.random() < 0.2:  # 20% chance
                alert = Alert(
                    alert_id=f"alt_{uuid.uuid4().hex[:8]}",
                    rule_id=rule.rule_id,
                    name=rule.name,
                    state=AlertState.FIRING,
                    severity=rule.severity,
                    current_value=current_value,
                    threshold=rule.threshold,
                    labels=rule.labels.copy(),
                    summary=rule.summary,
                    description=rule.description,
                    fired_at=datetime.now()
                )
                
                self.alerts[alert.alert_id] = alert
                new_alerts.append(alert)
                
        return new_alerts
        
    async def resolve_alert(self, alert_id: str) -> Optional[Alert]:
        """Разрешение алерта"""
        alert = self.alerts.get(alert_id)
        if not alert:
            return None
            
        alert.state = AlertState.RESOLVED
        alert.resolved_at = datetime.now()
        
        return alert
        
    async def create_slo(self, name: str,
                        service_name: str,
                        slo_type: SLOType,
                        target: float,
                        window_days: int = 30,
                        total_query: str = "",
                        good_query: str = "") -> SLO:
        """Создание SLO"""
        slo = SLO(
            slo_id=f"slo_{uuid.uuid4().hex[:8]}",
            name=name,
            service_name=service_name,
            slo_type=slo_type,
            target=target,
            window_days=window_days,
            total_query=total_query,
            good_query=good_query
        )
        
        self.slos[slo.slo_id] = slo
        return slo
        
    async def calculate_sli(self, slo_id: str) -> Optional[SLI]:
        """Расчёт SLI"""
        slo = self.slos.get(slo_id)
        if not slo:
            return None
            
        # Simulate SLI calculation
        total_events = random.randint(100000, 1000000)
        good_events = int(total_events * random.uniform(0.98, 1.0))
        success_rate = (good_events / total_events) * 100
        
        sli = SLI(
            sli_id=f"sli_{uuid.uuid4().hex[:8]}",
            slo_id=slo_id,
            total_events=total_events,
            good_events=good_events,
            success_rate=success_rate
        )
        
        self.slis[sli.sli_id] = sli
        
        # Update SLO
        slo.current_value = success_rate
        slo.error_budget_remaining = max(0, ((success_rate - slo.target) / (100 - slo.target)) * 100) if slo.target < 100 else 100
        slo.is_breached = success_rate < slo.target
        
        return sli
        
    async def create_dashboard(self, name: str,
                              description: str = "",
                              time_range: str = "1h",
                              refresh_interval: str = "1m",
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
                       query: str,
                       x: int = 0,
                       y: int = 0,
                       width: int = 12,
                       height: int = 8) -> Optional[Panel]:
        """Добавление панели"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            return None
            
        panel = Panel(
            panel_id=f"pnl_{uuid.uuid4().hex[:8]}",
            dashboard_id=dashboard_id,
            title=title,
            panel_type=panel_type,
            query=query,
            x=x,
            y=y,
            width=width,
            height=height
        )
        
        self.panels[panel.panel_id] = panel
        dashboard.panels.append({
            "panel_id": panel.panel_id,
            "title": title,
            "type": panel_type
        })
        
        return panel
        
    async def generate_service_map(self, name: str = "default") -> ServiceMap:
        """Генерация карты сервисов"""
        nodes = []
        edges = []
        
        for service in self.services.values():
            nodes.append({
                "id": service.service_id,
                "name": service.name,
                "version": service.version,
                "is_healthy": service.is_healthy
            })
            
            for dep in service.dependencies:
                # Find dependency service
                dep_service = next((s for s in self.services.values() if s.name == dep), None)
                if dep_service:
                    edges.append({
                        "source": service.service_id,
                        "target": dep_service.service_id,
                        "label": "calls"
                    })
                    
        service_map = ServiceMap(
            map_id=f"map_{uuid.uuid4().hex[:8]}",
            name=name,
            nodes=nodes,
            edges=edges
        )
        
        self.service_maps[service_map.map_id] = service_map
        return service_map
        
    async def query_traces(self, service_name: Optional[str] = None,
                          has_errors: Optional[bool] = None,
                          min_duration_ms: Optional[float] = None,
                          limit: int = 100) -> List[Trace]:
        """Поиск трейсов"""
        results = []
        
        for trace in self.traces.values():
            if service_name and service_name not in trace.services:
                continue
            if has_errors is not None and trace.has_errors != has_errors:
                continue
            if min_duration_ms and trace.duration_ms < min_duration_ms:
                continue
                
            results.append(trace)
            
            if len(results) >= limit:
                break
                
        return results
        
    async def query_logs(self, service_name: Optional[str] = None,
                        level: Optional[LogLevel] = None,
                        trace_id: Optional[str] = None,
                        search_text: Optional[str] = None,
                        limit: int = 100) -> List[LogEntry]:
        """Поиск логов"""
        results = []
        
        for log in self.logs.values():
            if service_name and log.service_name != service_name:
                continue
            if level and log.level != level:
                continue
            if trace_id and log.trace_id != trace_id:
                continue
            if search_text and search_text.lower() not in log.message.lower():
                continue
                
            results.append(log)
            
            if len(results) >= limit:
                break
                
        return sorted(results, key=lambda x: x.timestamp, reverse=True)[:limit]
        
    async def collect_metrics(self) -> ObservabilityMetrics:
        """Сбор метрик платформы"""
        healthy_services = sum(1 for s in self.services.values() if s.is_healthy)
        traces_with_errors = sum(1 for t in self.traces.values() if t.has_errors)
        durations = [t.duration_ms for t in self.traces.values() if t.duration_ms > 0]
        active_alerts = sum(1 for a in self.alerts.values() if a.state == AlertState.FIRING)
        breached_slos = sum(1 for s in self.slos.values() if s.is_breached)
        
        return ObservabilityMetrics(
            metrics_id=f"om_{uuid.uuid4().hex[:8]}",
            total_services=len(self.services),
            healthy_services=healthy_services,
            total_traces=len(self.traces),
            traces_with_errors=traces_with_errors,
            avg_trace_duration_ms=sum(durations) / len(durations) if durations else 0.0,
            total_metric_series=len(self.metric_series),
            metrics_ingestion_rate=random.uniform(10000, 100000),
            total_logs=len(self.logs),
            logs_ingestion_rate=random.uniform(1000, 10000),
            active_alerts=active_alerts,
            total_slos=len(self.slos),
            breached_slos=breached_slos
        )
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        healthy_services = sum(1 for s in self.services.values() if s.is_healthy)
        traces_with_errors = sum(1 for t in self.traces.values() if t.has_errors)
        active_alerts = sum(1 for a in self.alerts.values() if a.state == AlertState.FIRING)
        breached_slos = sum(1 for s in self.slos.values() if s.is_breached)
        
        logs_by_level = {}
        for level in LogLevel:
            logs_by_level[level.value] = sum(1 for l in self.logs.values() if l.level == level)
            
        return {
            "total_services": len(self.services),
            "healthy_services": healthy_services,
            "total_traces": len(self.traces),
            "traces_with_errors": traces_with_errors,
            "total_spans": len(self.spans),
            "total_metrics": len(self.metrics),
            "total_metric_series": len(self.metric_series),
            "total_logs": len(self.logs),
            "logs_by_level": logs_by_level,
            "total_alert_rules": len(self.alert_rules),
            "active_alerts": active_alerts,
            "total_slos": len(self.slos),
            "breached_slos": breached_slos,
            "total_dashboards": len(self.dashboards)
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 357: Observability Platform")
    print("=" * 60)
    
    platform = ObservabilityPlatform(platform_name="enterprise-observability")
    print("✓ Observability Platform initialized")
    
    # Register Services
    print("\n🔧 Registering Services...")
    
    services_data = [
        ("api-gateway", "2.1.0", ["auth-service", "user-service", "order-service"]),
        ("auth-service", "1.5.0", ["user-service", "redis-cache"]),
        ("user-service", "3.0.0", ["postgres-db", "redis-cache"]),
        ("order-service", "2.3.0", ["user-service", "inventory-service", "payment-service", "postgres-db"]),
        ("inventory-service", "1.8.0", ["postgres-db", "redis-cache"]),
        ("payment-service", "2.0.0", ["stripe-api", "postgres-db"]),
        ("notification-service", "1.2.0", ["kafka", "sendgrid-api"]),
        ("analytics-service", "1.0.0", ["clickhouse-db", "kafka"]),
        ("redis-cache", "7.0.0", []),
        ("postgres-db", "14.0", []),
        ("kafka", "3.4.0", []),
        ("clickhouse-db", "23.0", [])
    ]
    
    services = []
    for name, version, deps in services_data:
        svc = await platform.register_service(
            name=name,
            version=version,
            environment="production",
            namespace="default",
            tags={"team": "platform"},
            dependencies=deps
        )
        services.append(svc)
        print(f"  🔧 {name} v{version}")
        
    # Generate Traces
    print("\n🔍 Generating Distributed Traces...")
    
    for i in range(20):
        # Start trace at API Gateway
        trace, root_span = await platform.start_trace(
            "api-gateway",
            f"HTTP GET /api/orders/{i+1}",
            {"http.method": "GET", "http.path": f"/api/orders/{i+1}"}
        )
        
        # Add auth span
        auth_span = await platform.add_span(
            trace.trace_id,
            root_span.span_id,
            "auth-service",
            "validate_token",
            {"user_id": f"user_{random.randint(1, 100)}"}
        )
        await asyncio.sleep(0.001)
        await platform.end_span(auth_span.span_id)
        
        # Add order span
        order_span = await platform.add_span(
            trace.trace_id,
            root_span.span_id,
            "order-service",
            "get_order",
            {"order_id": i+1}
        )
        
        # Add DB span
        db_span = await platform.add_span(
            trace.trace_id,
            order_span.span_id,
            "postgres-db",
            "SELECT * FROM orders",
            {"db.name": "orders", "db.operation": "SELECT"}
        )
        await asyncio.sleep(0.001)
        await platform.end_span(db_span.span_id)
        
        await platform.end_span(order_span.span_id, "ERROR" if random.random() < 0.1 else "OK")
        await platform.end_span(root_span.span_id, "ERROR" if random.random() < 0.05 else "OK")
        
    print(f"  🔍 Generated {len(platform.traces)} traces with {len(platform.spans)} spans")
    
    # Record Metrics
    print("\n📊 Recording Metrics...")
    
    metrics_data = [
        ("http_requests_total", MetricType.COUNTER, "api-gateway"),
        ("http_request_duration_seconds", MetricType.HISTOGRAM, "api-gateway"),
        ("http_requests_in_flight", MetricType.GAUGE, "api-gateway"),
        ("database_connections", MetricType.GAUGE, "postgres-db"),
        ("database_query_duration_seconds", MetricType.HISTOGRAM, "postgres-db"),
        ("cache_hits_total", MetricType.COUNTER, "redis-cache"),
        ("cache_misses_total", MetricType.COUNTER, "redis-cache"),
        ("kafka_messages_produced_total", MetricType.COUNTER, "kafka"),
        ("kafka_consumer_lag", MetricType.GAUGE, "kafka"),
        ("cpu_usage_percent", MetricType.GAUGE, "order-service"),
        ("memory_usage_bytes", MetricType.GAUGE, "order-service"),
        ("error_rate", MetricType.GAUGE, "order-service")
    ]
    
    for name, mtype, service in metrics_data:
        for _ in range(10):
            value = random.uniform(0, 100) if mtype == MetricType.GAUGE else random.randint(100, 10000)
            await platform.record_metric(
                name=name,
                value=value,
                metric_type=mtype,
                labels={"service": service, "instance": f"{service}-{random.randint(1, 3)}"},
                unit="1" if mtype == MetricType.COUNTER else "seconds"
            )
            
    print(f"  📊 Recorded {len(platform.metrics)} metrics in {len(platform.metric_series)} series")
    
    # Log Entries
    print("\n📝 Generating Logs...")
    
    log_messages = [
        (LogLevel.INFO, "Request received", "api-gateway"),
        (LogLevel.INFO, "User authenticated successfully", "auth-service"),
        (LogLevel.DEBUG, "Cache hit for user profile", "redis-cache"),
        (LogLevel.INFO, "Order created successfully", "order-service"),
        (LogLevel.WARN, "High latency detected", "postgres-db"),
        (LogLevel.ERROR, "Connection pool exhausted", "postgres-db"),
        (LogLevel.INFO, "Payment processed", "payment-service"),
        (LogLevel.ERROR, "Payment declined", "payment-service"),
        (LogLevel.INFO, "Notification sent", "notification-service"),
        (LogLevel.DEBUG, "Message published to Kafka", "kafka")
    ]
    
    for _ in range(100):
        level, msg, service = random.choice(log_messages)
        trace = random.choice(list(platform.traces.values())) if platform.traces else None
        await platform.log(
            message=f"{msg} - request_id={uuid.uuid4().hex[:8]}",
            level=level,
            service_name=service,
            trace_id=trace.trace_id if trace else None,
            attributes={"env": "production"}
        )
        
    print(f"  📝 Generated {len(platform.logs)} log entries")
    
    # Alert Rules
    print("\n🚨 Creating Alert Rules...")
    
    alert_rules_data = [
        ("HighErrorRate", "sum(rate(http_requests_total{status=~'5..'}[5m]))", ComparisonOp.GT, 0.01, AlertSeverity.CRITICAL),
        ("HighLatency", "histogram_quantile(0.95, http_request_duration_seconds)", ComparisonOp.GT, 1.0, AlertSeverity.WARNING),
        ("LowCacheHitRate", "rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m]))", ComparisonOp.LT, 0.8, AlertSeverity.WARNING),
        ("HighCPU", "cpu_usage_percent", ComparisonOp.GT, 80.0, AlertSeverity.WARNING),
        ("HighMemory", "memory_usage_bytes / memory_limit_bytes * 100", ComparisonOp.GT, 85.0, AlertSeverity.WARNING),
        ("DatabaseConnectionPoolExhausted", "database_connections / database_max_connections * 100", ComparisonOp.GT, 90.0, AlertSeverity.CRITICAL),
        ("KafkaConsumerLag", "kafka_consumer_lag", ComparisonOp.GT, 10000, AlertSeverity.WARNING),
        ("ServiceDown", "up", ComparisonOp.EQ, 0, AlertSeverity.CRITICAL)
    ]
    
    for name, query, op, threshold, severity in alert_rules_data:
        await platform.create_alert_rule(
            name=name,
            metric_query=query,
            comparison_op=op,
            threshold=threshold,
            severity=severity,
            summary=f"Alert: {name}",
            description=f"Threshold {op.value} {threshold}"
        )
        print(f"  🚨 {name} ({severity.value})")
        
    # Evaluate Alerts
    new_alerts = await platform.evaluate_alert_rules()
    print(f"\n  ⚠️ {len(new_alerts)} new alerts fired")
    
    # Create SLOs
    print("\n🎯 Creating SLOs...")
    
    slos_data = [
        ("API Gateway Availability", "api-gateway", SLOType.AVAILABILITY, 99.9),
        ("API Gateway Latency P95", "api-gateway", SLOType.LATENCY, 99.0),
        ("Order Service Availability", "order-service", SLOType.AVAILABILITY, 99.95),
        ("Payment Service Availability", "payment-service", SLOType.AVAILABILITY, 99.99),
        ("Database Error Rate", "postgres-db", SLOType.ERROR_RATE, 99.9),
        ("Cache Hit Rate", "redis-cache", SLOType.THROUGHPUT, 95.0)
    ]
    
    slos = []
    for name, service, slo_type, target in slos_data:
        slo = await platform.create_slo(
            name=name,
            service_name=service,
            slo_type=slo_type,
            target=target,
            total_query=f"sum(rate(requests_total{{service='{service}'}}[30d]))",
            good_query=f"sum(rate(requests_total{{service='{service}',status!~'5..'}}[30d]))"
        )
        slos.append(slo)
        await platform.calculate_sli(slo.slo_id)
        status = "❌ BREACHED" if slo.is_breached else "✅ OK"
        print(f"  🎯 {name}: {slo.current_value:.2f}% (target: {target}%) {status}")
        
    # Create Dashboards
    print("\n📈 Creating Dashboards...")
    
    dashboards_data = [
        ("Service Overview", "Main service overview dashboard", ["overview", "sre"]),
        ("API Gateway", "API Gateway metrics and traces", ["api", "gateway"]),
        ("Order Service", "Order service performance", ["orders", "business"]),
        ("Database Performance", "Database metrics and queries", ["database", "performance"]),
        ("SLO Dashboard", "SLO/SLI tracking dashboard", ["slo", "sli", "reliability"])
    ]
    
    dashboards = []
    for name, desc, tags in dashboards_data:
        db = await platform.create_dashboard(name, desc, "1h", "30s", tags)
        dashboards.append(db)
        
        # Add panels
        await platform.add_panel(db.dashboard_id, "Request Rate", "graph", "rate(http_requests_total[5m])", 0, 0, 8, 6)
        await platform.add_panel(db.dashboard_id, "Error Rate", "graph", "rate(http_errors_total[5m])", 8, 0, 8, 6)
        await platform.add_panel(db.dashboard_id, "Latency P95", "graph", "histogram_quantile(0.95, http_request_duration_seconds)", 16, 0, 8, 6)
        await platform.add_panel(db.dashboard_id, "Active Services", "stat", "count(up)", 0, 6, 6, 4)
        
        print(f"  📈 {name} with {len(db.panels)} panels")
        
    # Generate Service Map
    print("\n🗺️ Generating Service Map...")
    
    service_map = await platform.generate_service_map("Production Environment")
    print(f"  🗺️ Generated map with {len(service_map.nodes)} nodes and {len(service_map.edges)} edges")
    
    # Collect Platform Metrics
    platform_metrics = await platform.collect_metrics()
    
    # Services Dashboard
    print("\n🔧 Services:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Service Name              │ Version    │ Environment │ Health   │ Dependencies                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for svc in services:
        name = svc.name[:25].ljust(25)
        version = svc.version[:10].ljust(10)
        env = svc.environment[:11].ljust(11)
        health = ("✅ Healthy" if svc.is_healthy else "❌ Unhealthy").ljust(8)
        deps = ", ".join(svc.dependencies[:3]) + ("..." if len(svc.dependencies) > 3 else "")
        deps = deps[:285].ljust(285)
        
        print(f"  │ {name} │ {version} │ {env} │ {health} │ {deps} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # SLO Dashboard
    print("\n🎯 SLO Status:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ SLO Name                              │ Service           │ Type          │ Target   │ Current   │ Budget    │ Status                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for slo in slos:
        name = slo.name[:39].ljust(39)
        service = slo.service_name[:17].ljust(17)
        slo_type = slo.slo_type.value[:13].ljust(13)
        target = f"{slo.target:.1f}%".ljust(8)
        current = f"{slo.current_value:.2f}%".ljust(9)
        budget = f"{slo.error_budget_remaining:.1f}%".ljust(9)
        status = "❌ BREACHED" if slo.is_breached else "✅ OK"
        status = status.ljust(200)
        
        print(f"  │ {name} │ {service} │ {slo_type} │ {target} │ {current} │ {budget} │ {status} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Services: {stats['healthy_services']}/{stats['total_services']} healthy")
    print(f"  Traces: {stats['total_traces']} ({stats['traces_with_errors']} with errors)")
    print(f"  Spans: {stats['total_spans']}")
    print(f"  Metrics: {stats['total_metrics']} in {stats['total_metric_series']} series")
    print(f"  Logs: {stats['total_logs']}")
    print(f"  Alert Rules: {stats['total_alert_rules']} ({stats['active_alerts']} active)")
    print(f"  SLOs: {stats['total_slos']} ({stats['breached_slos']} breached)")
    print(f"  Dashboards: {stats['total_dashboards']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                      Observability Platform                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Services:                {stats['total_services']:>12}                      │")
    print(f"│ Healthy Services:              {stats['healthy_services']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Traces:                  {stats['total_traces']:>12}                      │")
    print(f"│ Total Spans:                   {stats['total_spans']:>12}                      │")
    print(f"│ Avg Trace Duration (ms):       {platform_metrics.avg_trace_duration_ms:>12.2f}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Metrics:                 {stats['total_metrics']:>12}                      │")
    print(f"│ Metric Series:                 {stats['total_metric_series']:>12}                      │")
    print(f"│ Total Logs:                    {stats['total_logs']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Alert Rules:                   {stats['total_alert_rules']:>12}                      │")
    print(f"│ Active Alerts:                 {stats['active_alerts']:>12}                      │")
    print(f"│ SLOs (Breached):               {stats['breached_slos']:>3}/{stats['total_slos']:<8}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Observability Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
