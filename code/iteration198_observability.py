#!/usr/bin/env python3
"""
Server Init - Iteration 198: Observability Platform
Платформа наблюдаемости

Функционал:
- Metrics Collection - сбор метрик
- Distributed Tracing - распределённая трассировка
- Log Aggregation - агрегация логов
- Alerting - оповещения
- Dashboards - дашборды
- SLI/SLO Tracking - отслеживание SLI/SLO
- Correlation - корреляция данных
- Anomaly Detection - обнаружение аномалий
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid


class MetricType(Enum):
    """Тип метрики"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertSeverity(Enum):
    """Серьёзность оповещения"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertState(Enum):
    """Состояние оповещения"""
    PENDING = "pending"
    FIRING = "firing"
    RESOLVED = "resolved"


class LogLevel(Enum):
    """Уровень лога"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Metric:
    """Метрика"""
    metric_id: str
    name: str = ""
    metric_type: MetricType = MetricType.GAUGE
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Value
    value: float = 0.0
    
    # Time
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Metadata
    unit: str = ""
    description: str = ""


@dataclass
class MetricSeries:
    """Временной ряд метрики"""
    series_id: str
    metric_name: str = ""
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Data points
    data_points: List[tuple] = field(default_factory=list)  # (timestamp, value)
    
    # Retention
    retention_days: int = 30
    
    def add_point(self, value: float, timestamp: datetime = None):
        """Добавление точки"""
        ts = timestamp or datetime.now()
        self.data_points.append((ts, value))
        
    def get_avg(self, window_minutes: int = 5) -> float:
        """Среднее за окно"""
        cutoff = datetime.now() - timedelta(minutes=window_minutes)
        recent = [v for ts, v in self.data_points if ts > cutoff]
        return sum(recent) / len(recent) if recent else 0


@dataclass
class Span:
    """Спан трассировки"""
    span_id: str
    trace_id: str
    
    # Parent
    parent_span_id: Optional[str] = None
    
    # Operation
    operation_name: str = ""
    service_name: str = ""
    
    # Time
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Logs
    logs: List[Dict[str, Any]] = field(default_factory=list)
    
    # Status
    status: str = "ok"  # ok, error
    
    @property
    def duration_ms(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0


@dataclass
class Trace:
    """Трасса"""
    trace_id: str
    root_span_id: str = ""
    
    # Spans
    spans: Dict[str, Span] = field(default_factory=dict)
    
    # Services
    services: Set[str] = field(default_factory=set)
    
    # Time
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    @property
    def duration_ms(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0
        
    @property
    def span_count(self) -> int:
        return len(self.spans)


@dataclass
class LogEntry:
    """Запись лога"""
    log_id: str
    
    # Content
    message: str = ""
    level: LogLevel = LogLevel.INFO
    
    # Context
    service: str = ""
    trace_id: str = ""
    span_id: str = ""
    
    # Time
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Fields
    fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AlertRule:
    """Правило оповещения"""
    rule_id: str
    name: str = ""
    
    # Condition
    metric_name: str = ""
    condition: str = ""  # > 90, < 10, etc.
    threshold: float = 0
    
    # Duration
    for_duration_seconds: int = 60
    
    # Severity
    severity: AlertSeverity = AlertSeverity.WARNING
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Annotations
    annotations: Dict[str, str] = field(default_factory=dict)
    
    # State
    is_enabled: bool = True


@dataclass
class Alert:
    """Оповещение"""
    alert_id: str
    rule_id: str
    
    # State
    state: AlertState = AlertState.PENDING
    
    # Time
    started_at: datetime = field(default_factory=datetime.now)
    fired_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Value
    current_value: float = 0
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class Dashboard:
    """Дашборд"""
    dashboard_id: str
    name: str = ""
    description: str = ""
    
    # Panels
    panels: List[Dict[str, Any]] = field(default_factory=list)
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Refresh
    refresh_interval_seconds: int = 30


class MetricsCollector:
    """Сборщик метрик"""
    
    def __init__(self):
        self.series: Dict[str, MetricSeries] = {}
        
    def record(self, name: str, value: float, labels: Dict[str, str] = None):
        """Запись метрики"""
        labels = labels or {}
        series_key = f"{name}:{hash(frozenset(labels.items()))}"
        
        if series_key not in self.series:
            self.series[series_key] = MetricSeries(
                series_id=f"series_{uuid.uuid4().hex[:8]}",
                metric_name=name,
                labels=labels
            )
            
        self.series[series_key].add_point(value)
        
    def query(self, name: str, labels_match: Dict[str, str] = None) -> List[MetricSeries]:
        """Запрос метрик"""
        results = []
        for series in self.series.values():
            if series.metric_name != name:
                continue
            if labels_match:
                if all(series.labels.get(k) == v for k, v in labels_match.items()):
                    results.append(series)
            else:
                results.append(series)
        return results


class TracingCollector:
    """Сборщик трассировок"""
    
    def __init__(self):
        self.traces: Dict[str, Trace] = {}
        
    def start_trace(self, service: str, operation: str) -> Tuple[str, str]:
        """Начало трассы"""
        trace_id = f"trace_{uuid.uuid4().hex[:16]}"
        span_id = f"span_{uuid.uuid4().hex[:12]}"
        
        span = Span(
            span_id=span_id,
            trace_id=trace_id,
            operation_name=operation,
            service_name=service
        )
        
        trace = Trace(
            trace_id=trace_id,
            root_span_id=span_id
        )
        trace.spans[span_id] = span
        trace.services.add(service)
        
        self.traces[trace_id] = trace
        return trace_id, span_id
        
    def start_span(self, trace_id: str, parent_span_id: str,
                  service: str, operation: str) -> str:
        """Начало спана"""
        trace = self.traces.get(trace_id)
        if not trace:
            return ""
            
        span_id = f"span_{uuid.uuid4().hex[:12]}"
        span = Span(
            span_id=span_id,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            operation_name=operation,
            service_name=service
        )
        
        trace.spans[span_id] = span
        trace.services.add(service)
        return span_id
        
    def end_span(self, trace_id: str, span_id: str, status: str = "ok"):
        """Завершение спана"""
        trace = self.traces.get(trace_id)
        if trace and span_id in trace.spans:
            trace.spans[span_id].end_time = datetime.now()
            trace.spans[span_id].status = status
            
    def end_trace(self, trace_id: str):
        """Завершение трассы"""
        trace = self.traces.get(trace_id)
        if trace:
            trace.end_time = datetime.now()


from typing import Tuple


class LogAggregator:
    """Агрегатор логов"""
    
    def __init__(self):
        self.logs: List[LogEntry] = []
        
    def ingest(self, message: str, level: LogLevel = LogLevel.INFO,
               service: str = "", trace_id: str = "",
               fields: Dict[str, Any] = None) -> LogEntry:
        """Приём лога"""
        entry = LogEntry(
            log_id=f"log_{uuid.uuid4().hex[:8]}",
            message=message,
            level=level,
            service=service,
            trace_id=trace_id,
            fields=fields or {}
        )
        self.logs.append(entry)
        return entry
        
    def search(self, query: str = "", service: str = "",
               level: LogLevel = None, limit: int = 100) -> List[LogEntry]:
        """Поиск логов"""
        results = []
        for log in reversed(self.logs):
            if len(results) >= limit:
                break
            if service and log.service != service:
                continue
            if level and log.level != level:
                continue
            if query and query.lower() not in log.message.lower():
                continue
            results.append(log)
        return results


class AlertManager:
    """Менеджер оповещений"""
    
    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.alerts: Dict[str, Alert] = {}
        
    def add_rule(self, rule: AlertRule):
        """Добавление правила"""
        self.rules[rule.rule_id] = rule
        
    async def evaluate(self, metrics_collector: MetricsCollector):
        """Оценка правил"""
        for rule in self.rules.values():
            if not rule.is_enabled:
                continue
                
            series_list = metrics_collector.query(rule.metric_name)
            for series in series_list:
                avg_value = series.get_avg()
                
                triggered = False
                if ">" in rule.condition:
                    triggered = avg_value > rule.threshold
                elif "<" in rule.condition:
                    triggered = avg_value < rule.threshold
                    
                alert_key = f"{rule.rule_id}:{series.series_id}"
                
                if triggered:
                    if alert_key not in self.alerts:
                        alert = Alert(
                            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
                            rule_id=rule.rule_id,
                            state=AlertState.FIRING,
                            fired_at=datetime.now(),
                            current_value=avg_value,
                            labels=series.labels
                        )
                        self.alerts[alert_key] = alert
                else:
                    if alert_key in self.alerts:
                        self.alerts[alert_key].state = AlertState.RESOLVED
                        self.alerts[alert_key].resolved_at = datetime.now()


class ObservabilityPlatform:
    """Платформа наблюдаемости"""
    
    def __init__(self):
        self.metrics = MetricsCollector()
        self.tracing = TracingCollector()
        self.logs = LogAggregator()
        self.alerts = AlertManager()
        self.dashboards: Dict[str, Dashboard] = {}
        
    def create_dashboard(self, name: str, panels: List[Dict[str, Any]]) -> Dashboard:
        """Создание дашборда"""
        dashboard = Dashboard(
            dashboard_id=f"dash_{uuid.uuid4().hex[:8]}",
            name=name,
            panels=panels
        )
        self.dashboards[dashboard.dashboard_id] = dashboard
        return dashboard
        
    def correlate(self, trace_id: str) -> Dict[str, Any]:
        """Корреляция данных по trace_id"""
        trace = self.tracing.traces.get(trace_id)
        logs = [l for l in self.logs.logs if l.trace_id == trace_id]
        
        return {
            "trace": trace,
            "logs": logs,
            "span_count": trace.span_count if trace else 0,
            "services": list(trace.services) if trace else []
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        firing_alerts = len([a for a in self.alerts.alerts.values() 
                            if a.state == AlertState.FIRING])
        
        return {
            "total_series": len(self.metrics.series),
            "total_traces": len(self.tracing.traces),
            "total_logs": len(self.logs.logs),
            "active_alerts": firing_alerts,
            "dashboards": len(self.dashboards),
            "alert_rules": len(self.alerts.rules)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 198: Observability Platform")
    print("=" * 60)
    
    platform = ObservabilityPlatform()
    print("✓ Observability Platform created")
    
    # Generate metrics
    print("\n📊 Generating Metrics...")
    
    services = ["api-gateway", "user-service", "order-service", "payment-service"]
    metrics_names = ["http_requests_total", "http_latency_ms", "cpu_usage", "memory_usage"]
    
    for _ in range(100):
        service = random.choice(services)
        metric = random.choice(metrics_names)
        
        if metric == "http_requests_total":
            value = random.randint(100, 1000)
        elif metric == "http_latency_ms":
            value = random.uniform(10, 500)
        elif metric == "cpu_usage":
            value = random.uniform(10, 90)
        else:
            value = random.uniform(20, 80)
            
        platform.metrics.record(metric, value, {"service": service})
        
    print(f"  ✓ Generated {len(platform.metrics.series)} metric series")
    
    # Generate traces
    print("\n🔍 Generating Traces...")
    
    for i in range(20):
        # Start trace
        trace_id, root_span = platform.tracing.start_trace("api-gateway", "/api/orders")
        
        # Child spans
        span1 = platform.tracing.start_span(trace_id, root_span, "user-service", "get_user")
        await asyncio.sleep(0.01)
        platform.tracing.end_span(trace_id, span1)
        
        span2 = platform.tracing.start_span(trace_id, root_span, "order-service", "create_order")
        
        span3 = platform.tracing.start_span(trace_id, span2, "payment-service", "process_payment")
        await asyncio.sleep(0.01)
        status = "ok" if random.random() > 0.1 else "error"
        platform.tracing.end_span(trace_id, span3, status)
        
        platform.tracing.end_span(trace_id, span2)
        platform.tracing.end_span(trace_id, root_span)
        platform.tracing.end_trace(trace_id)
        
    print(f"  ✓ Generated {len(platform.tracing.traces)} traces")
    
    # Generate logs
    print("\n📝 Generating Logs...")
    
    log_messages = [
        ("Request received", LogLevel.INFO),
        ("Processing order", LogLevel.INFO),
        ("Database query executed", LogLevel.DEBUG),
        ("Cache miss", LogLevel.WARNING),
        ("Payment failed", LogLevel.ERROR),
        ("Service started", LogLevel.INFO),
    ]
    
    for trace_id in list(platform.tracing.traces.keys())[:10]:
        for _ in range(random.randint(3, 8)):
            msg, level = random.choice(log_messages)
            service = random.choice(services)
            platform.logs.ingest(msg, level, service, trace_id)
            
    print(f"  ✓ Generated {len(platform.logs.logs)} log entries")
    
    # Add alert rules
    print("\n🚨 Adding Alert Rules...")
    
    rules = [
        AlertRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name="High CPU Usage",
            metric_name="cpu_usage",
            condition=">",
            threshold=80,
            severity=AlertSeverity.WARNING
        ),
        AlertRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name="High Latency",
            metric_name="http_latency_ms",
            condition=">",
            threshold=400,
            severity=AlertSeverity.ERROR
        ),
        AlertRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name="Low Memory",
            metric_name="memory_usage",
            condition=">",
            threshold=85,
            severity=AlertSeverity.CRITICAL
        ),
    ]
    
    for rule in rules:
        platform.alerts.add_rule(rule)
        print(f"  ✓ {rule.name} ({rule.severity.value})")
        
    # Evaluate alerts
    await platform.alerts.evaluate(platform.metrics)
    
    # Create dashboards
    print("\n📈 Creating Dashboards...")
    
    dashboards_config = [
        ("Service Overview", ["requests", "latency", "errors"]),
        ("Infrastructure", ["cpu", "memory", "disk"]),
        ("Business Metrics", ["orders", "revenue", "users"]),
    ]
    
    for name, panels in dashboards_config:
        dash = platform.create_dashboard(name, [{"type": "graph", "metric": p} for p in panels])
        print(f"  ✓ {name} ({len(dash.panels)} panels)")
        
    # Display metrics summary
    print("\n📊 Metrics Summary:")
    
    print("\n  ┌─────────────────────────┬──────────┬──────────┬──────────┐")
    print("  │ Metric                  │ Series   │ Points   │ Avg      │")
    print("  ├─────────────────────────┼──────────┼──────────┼──────────┤")
    
    metrics_summary = {}
    for series in platform.metrics.series.values():
        name = series.metric_name
        if name not in metrics_summary:
            metrics_summary[name] = {"series": 0, "points": 0, "values": []}
        metrics_summary[name]["series"] += 1
        metrics_summary[name]["points"] += len(series.data_points)
        metrics_summary[name]["values"].extend([v for _, v in series.data_points])
        
    for name, data in metrics_summary.items():
        avg_val = sum(data["values"]) / len(data["values"]) if data["values"] else 0
        metric_name = name[:23].ljust(23)
        series_count = str(data["series"]).center(8)
        points_count = str(data["points"]).center(8)
        avg_str = f"{avg_val:.1f}".rjust(8)
        print(f"  │ {metric_name} │ {series_count} │ {points_count} │ {avg_str} │")
        
    print("  └─────────────────────────┴──────────┴──────────┴──────────┘")
    
    # Display traces
    print("\n🔍 Recent Traces:")
    
    print("\n  ┌──────────────────────┬──────────┬──────────┬──────────┐")
    print("  │ Trace ID             │ Spans    │ Services │ Duration │")
    print("  ├──────────────────────┼──────────┼──────────┼──────────┤")
    
    for trace in list(platform.tracing.traces.values())[:5]:
        trace_short = trace.trace_id[:20].ljust(20)
        spans = str(trace.span_count).center(8)
        services_count = str(len(trace.services)).center(8)
        duration = f"{trace.duration_ms:.1f}ms".rjust(8)
        print(f"  │ {trace_short} │ {spans} │ {services_count} │ {duration} │")
        
    print("  └──────────────────────┴──────────┴──────────┴──────────┘")
    
    # Display alerts
    print("\n🚨 Active Alerts:")
    
    firing = [a for a in platform.alerts.alerts.values() if a.state == AlertState.FIRING]
    if firing:
        for alert in firing[:5]:
            rule = platform.alerts.rules.get(alert.rule_id)
            rule_name = rule.name if rule else "Unknown"
            print(f"  🔴 {rule_name}: {alert.current_value:.1f}")
    else:
        print("  ✓ No active alerts")
        
    # Log level distribution
    print("\n📝 Log Level Distribution:")
    
    level_counts = {}
    for log in platform.logs.logs:
        l = log.level.value
        level_counts[l] = level_counts.get(l, 0) + 1
        
    for level, count in sorted(level_counts.items()):
        bar = "█" * min(count // 2, 30)
        print(f"  {level:10} [{bar}] {count}")
        
    # Correlation example
    print("\n🔗 Correlation Example:")
    
    sample_trace = list(platform.tracing.traces.keys())[0]
    correlation = platform.correlate(sample_trace)
    
    print(f"  Trace: {sample_trace}")
    print(f"  Spans: {correlation['span_count']}")
    print(f"  Services: {', '.join(correlation['services'])}")
    print(f"  Related Logs: {len(correlation['logs'])}")
    
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📈 Platform Statistics:")
    
    print(f"\n  Total Metric Series: {stats['total_series']}")
    print(f"  Total Traces: {stats['total_traces']}")
    print(f"  Total Logs: {stats['total_logs']}")
    print(f"  Active Alerts: {stats['active_alerts']}")
    print(f"  Alert Rules: {stats['alert_rules']}")
    print(f"  Dashboards: {stats['dashboards']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Observability Dashboard                         │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Metric Series:                 {stats['total_series']:>12}                        │")
    print(f"│ Traces:                        {stats['total_traces']:>12}                        │")
    print(f"│ Log Entries:                   {stats['total_logs']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Active Alerts:                 {stats['active_alerts']:>12}                        │")
    print(f"│ Alert Rules:                   {stats['alert_rules']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Observability Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
