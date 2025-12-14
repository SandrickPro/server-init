#!/usr/bin/env python3
"""
Server Init - Iteration 277: Metrics Pipeline Platform
Платформа пайплайна метрик

Функционал:
- Metrics Collection - сбор метрик
- Metrics Transformation - трансформация метрик
- Metrics Aggregation - агрегация метрик
- Metrics Storage - хранение метрик
- Metrics Query - запросы метрик
- Metrics Export - экспорт метрик
- Metrics Rules - правила метрик
- Cardinality Management - управление кардинальностью
"""

import asyncio
import random
import math
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid


class MetricType(Enum):
    """Тип метрики"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    UNTYPED = "untyped"


class AggregationType(Enum):
    """Тип агрегации"""
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    LAST = "last"
    PERCENTILE = "percentile"


class TransformType(Enum):
    """Тип трансформации"""
    RATE = "rate"
    DELTA = "delta"
    DERIVATIVE = "derivative"
    CLAMP = "clamp"
    SCALE = "scale"
    ROUND = "round"
    ABS = "abs"


class StorageBackend(Enum):
    """Backend хранения"""
    MEMORY = "memory"
    PROMETHEUS = "prometheus"
    INFLUXDB = "influxdb"
    VICTORIA_METRICS = "victoria_metrics"


@dataclass
class MetricLabel:
    """Метка метрики"""
    name: str
    value: str


@dataclass
class MetricSample:
    """Сэмпл метрики"""
    sample_id: str
    
    # Metric
    name: str = ""
    metric_type: MetricType = MetricType.GAUGE
    
    # Value
    value: float = 0
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Help
    help_text: str = ""


@dataclass
class MetricSeries:
    """Серия метрики"""
    series_id: str
    name: str
    
    # Type
    metric_type: MetricType = MetricType.GAUGE
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Samples
    samples: List[MetricSample] = field(default_factory=list)
    
    # Stats
    min_value: float = float('inf')
    max_value: float = float('-inf')
    sum_value: float = 0
    count: int = 0


@dataclass
class HistogramBucket:
    """Бакет гистограммы"""
    le: float  # less than or equal
    count: int = 0


@dataclass
class HistogramMetric:
    """Метрика-гистограмма"""
    histogram_id: str
    name: str
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Buckets
    buckets: List[HistogramBucket] = field(default_factory=list)
    
    # Sum
    sum_value: float = 0
    count: int = 0


@dataclass
class SummaryMetric:
    """Метрика-summary"""
    summary_id: str
    name: str
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Quantiles
    quantiles: Dict[float, float] = field(default_factory=dict)  # quantile -> value
    
    # Sum
    sum_value: float = 0
    count: int = 0


@dataclass
class CollectorConfig:
    """Конфигурация коллектора"""
    collector_id: str
    name: str
    
    # Endpoint
    endpoint: str = ""
    
    # Scrape interval
    scrape_interval_seconds: int = 15
    
    # Labels
    static_labels: Dict[str, str] = field(default_factory=dict)
    
    # State
    active: bool = True
    last_scrape: Optional[datetime] = None
    scrape_duration_ms: float = 0


@dataclass
class TransformRule:
    """Правило трансформации"""
    rule_id: str
    name: str
    
    # Source
    source_metric: str = ""
    
    # Transform
    transform_type: TransformType = TransformType.RATE
    
    # Parameters
    params: Dict[str, Any] = field(default_factory=dict)
    
    # Output
    output_metric: str = ""
    
    # Active
    active: bool = True


@dataclass
class AggregationRule:
    """Правило агрегации"""
    rule_id: str
    name: str
    
    # Source
    source_metric: str = ""
    
    # Aggregation
    aggregation_type: AggregationType = AggregationType.AVG
    
    # Group by
    group_by: List[str] = field(default_factory=list)
    
    # Window
    window_seconds: int = 60
    
    # Output
    output_metric: str = ""
    
    # Active
    active: bool = True


@dataclass
class RecordingRule:
    """Recording правило"""
    rule_id: str
    name: str
    
    # Expression (PromQL-like)
    expression: str = ""
    
    # Output
    output_metric: str = ""
    
    # Labels
    output_labels: Dict[str, str] = field(default_factory=dict)
    
    # Interval
    evaluation_interval_seconds: int = 60
    
    # Active
    active: bool = True
    last_evaluation: Optional[datetime] = None


@dataclass
class ExporterConfig:
    """Конфигурация экспортера"""
    exporter_id: str
    name: str
    
    # Backend
    backend: StorageBackend = StorageBackend.PROMETHEUS
    
    # Endpoint
    endpoint: str = ""
    
    # Batch
    batch_size: int = 100
    flush_interval_seconds: int = 10
    
    # State
    active: bool = True
    samples_exported: int = 0


@dataclass
class CardinalityLimit:
    """Лимит кардинальности"""
    limit_id: str
    name: str
    
    # Metric pattern
    metric_pattern: str = ""
    
    # Limits
    max_series: int = 10000
    max_labels_per_series: int = 20
    
    # Current
    current_series: int = 0
    
    # Action on exceed
    drop_on_exceed: bool = True


class MetricsPipelineManager:
    """Менеджер пайплайна метрик"""
    
    def __init__(self):
        self.series: Dict[str, MetricSeries] = {}
        self.histograms: Dict[str, HistogramMetric] = {}
        self.summaries: Dict[str, SummaryMetric] = {}
        self.collectors: Dict[str, CollectorConfig] = {}
        self.transform_rules: Dict[str, TransformRule] = {}
        self.aggregation_rules: Dict[str, AggregationRule] = {}
        self.recording_rules: Dict[str, RecordingRule] = {}
        self.exporters: Dict[str, ExporterConfig] = {}
        self.cardinality_limits: Dict[str, CardinalityLimit] = {}
        
        # Default histogram buckets
        self.default_buckets = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
        
    def _series_key(self, name: str, labels: Dict[str, str]) -> str:
        """Ключ серии"""
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
        
    def add_collector(self, name: str,
                     endpoint: str,
                     scrape_interval: int = 15) -> CollectorConfig:
        """Добавление коллектора"""
        collector = CollectorConfig(
            collector_id=f"collector_{uuid.uuid4().hex[:8]}",
            name=name,
            endpoint=endpoint,
            scrape_interval_seconds=scrape_interval
        )
        
        self.collectors[name] = collector
        return collector
        
    def add_exporter(self, name: str,
                    backend: StorageBackend,
                    endpoint: str) -> ExporterConfig:
        """Добавление экспортера"""
        exporter = ExporterConfig(
            exporter_id=f"exporter_{uuid.uuid4().hex[:8]}",
            name=name,
            backend=backend,
            endpoint=endpoint
        )
        
        self.exporters[name] = exporter
        return exporter
        
    def record_counter(self, name: str,
                      value: float,
                      labels: Dict[str, str] = None,
                      help_text: str = "") -> MetricSample:
        """Запись counter"""
        return self._record_metric(name, value, MetricType.COUNTER, labels, help_text)
        
    def record_gauge(self, name: str,
                    value: float,
                    labels: Dict[str, str] = None,
                    help_text: str = "") -> MetricSample:
        """Запись gauge"""
        return self._record_metric(name, value, MetricType.GAUGE, labels, help_text)
        
    def _record_metric(self, name: str,
                      value: float,
                      metric_type: MetricType,
                      labels: Dict[str, str] = None,
                      help_text: str = "") -> MetricSample:
        """Запись метрики"""
        labels = labels or {}
        series_key = self._series_key(name, labels)
        
        # Check cardinality
        if not self._check_cardinality(name, series_key):
            return None
            
        # Get or create series
        if series_key not in self.series:
            self.series[series_key] = MetricSeries(
                series_id=f"series_{uuid.uuid4().hex[:8]}",
                name=name,
                metric_type=metric_type,
                labels=labels
            )
            
        series = self.series[series_key]
        
        # Create sample
        sample = MetricSample(
            sample_id=f"sample_{uuid.uuid4().hex[:8]}",
            name=name,
            metric_type=metric_type,
            value=value,
            labels=labels,
            help_text=help_text
        )
        
        # Update series
        series.samples.append(sample)
        series.min_value = min(series.min_value, value)
        series.max_value = max(series.max_value, value)
        series.sum_value += value
        series.count += 1
        
        # Keep only last 100 samples
        if len(series.samples) > 100:
            series.samples = series.samples[-100:]
            
        # Apply transforms
        self._apply_transforms(sample)
        
        # Export
        self._export_sample(sample)
        
        return sample
        
    def record_histogram(self, name: str,
                        value: float,
                        labels: Dict[str, str] = None,
                        buckets: List[float] = None) -> HistogramMetric:
        """Запись histogram"""
        labels = labels or {}
        buckets = buckets or self.default_buckets
        hist_key = self._series_key(name, labels)
        
        if hist_key not in self.histograms:
            self.histograms[hist_key] = HistogramMetric(
                histogram_id=f"hist_{uuid.uuid4().hex[:8]}",
                name=name,
                labels=labels,
                buckets=[HistogramBucket(le=b) for b in sorted(buckets)]
            )
            
        hist = self.histograms[hist_key]
        
        # Update buckets
        for bucket in hist.buckets:
            if value <= bucket.le:
                bucket.count += 1
                
        hist.sum_value += value
        hist.count += 1
        
        return hist
        
    def record_summary(self, name: str,
                      value: float,
                      labels: Dict[str, str] = None,
                      quantiles: List[float] = None) -> SummaryMetric:
        """Запись summary"""
        labels = labels or {}
        quantiles = quantiles or [0.5, 0.9, 0.99]
        summary_key = self._series_key(name, labels)
        
        if summary_key not in self.summaries:
            self.summaries[summary_key] = SummaryMetric(
                summary_id=f"summary_{uuid.uuid4().hex[:8]}",
                name=name,
                labels=labels,
                quantiles={q: 0 for q in quantiles}
            )
            
        summary = self.summaries[summary_key]
        summary.sum_value += value
        summary.count += 1
        
        # Simple quantile approximation (would use t-digest in production)
        for q in summary.quantiles:
            if random.random() < 0.1:  # Simplified update
                summary.quantiles[q] = value
                
        return summary
        
    def _check_cardinality(self, name: str, series_key: str) -> bool:
        """Проверка кардинальности"""
        for limit in self.cardinality_limits.values():
            if limit.metric_pattern in name:
                if limit.current_series >= limit.max_series:
                    if limit.drop_on_exceed:
                        return False
                if series_key not in self.series:
                    limit.current_series += 1
        return True
        
    def add_cardinality_limit(self, name: str,
                             metric_pattern: str,
                             max_series: int) -> CardinalityLimit:
        """Добавление лимита кардинальности"""
        limit = CardinalityLimit(
            limit_id=f"limit_{uuid.uuid4().hex[:8]}",
            name=name,
            metric_pattern=metric_pattern,
            max_series=max_series
        )
        
        self.cardinality_limits[name] = limit
        return limit
        
    def add_transform_rule(self, name: str,
                          source_metric: str,
                          transform_type: TransformType,
                          output_metric: str,
                          params: Dict[str, Any] = None) -> TransformRule:
        """Добавление правила трансформации"""
        rule = TransformRule(
            rule_id=f"transform_{uuid.uuid4().hex[:8]}",
            name=name,
            source_metric=source_metric,
            transform_type=transform_type,
            output_metric=output_metric,
            params=params or {}
        )
        
        self.transform_rules[name] = rule
        return rule
        
    def _apply_transforms(self, sample: MetricSample):
        """Применение трансформаций"""
        for rule in self.transform_rules.values():
            if not rule.active:
                continue
            if rule.source_metric not in sample.name:
                continue
                
            transformed_value = sample.value
            
            if rule.transform_type == TransformType.SCALE:
                factor = rule.params.get("factor", 1)
                transformed_value *= factor
                
            elif rule.transform_type == TransformType.ROUND:
                decimals = rule.params.get("decimals", 0)
                transformed_value = round(transformed_value, decimals)
                
            elif rule.transform_type == TransformType.ABS:
                transformed_value = abs(transformed_value)
                
            elif rule.transform_type == TransformType.CLAMP:
                min_val = rule.params.get("min", float('-inf'))
                max_val = rule.params.get("max", float('inf'))
                transformed_value = max(min_val, min(max_val, transformed_value))
                
            # Record transformed metric
            self._record_metric(
                rule.output_metric,
                transformed_value,
                sample.metric_type,
                sample.labels
            )
            
    def add_aggregation_rule(self, name: str,
                            source_metric: str,
                            aggregation_type: AggregationType,
                            output_metric: str,
                            group_by: List[str] = None) -> AggregationRule:
        """Добавление правила агрегации"""
        rule = AggregationRule(
            rule_id=f"agg_{uuid.uuid4().hex[:8]}",
            name=name,
            source_metric=source_metric,
            aggregation_type=aggregation_type,
            output_metric=output_metric,
            group_by=group_by or []
        )
        
        self.aggregation_rules[name] = rule
        return rule
        
    def run_aggregations(self):
        """Выполнение агрегаций"""
        for rule in self.aggregation_rules.values():
            if not rule.active:
                continue
                
            # Find matching series
            matching = [s for s in self.series.values() if rule.source_metric in s.name]
            
            if not matching:
                continue
                
            # Group by labels
            groups: Dict[str, List[MetricSeries]] = {}
            
            for series in matching:
                group_key = ",".join(series.labels.get(k, "") for k in rule.group_by)
                if group_key not in groups:
                    groups[group_key] = []
                groups[group_key].append(series)
                
            # Aggregate each group
            for group_key, group_series in groups.items():
                values = [s.samples[-1].value for s in group_series if s.samples]
                
                if not values:
                    continue
                    
                if rule.aggregation_type == AggregationType.SUM:
                    result = sum(values)
                elif rule.aggregation_type == AggregationType.AVG:
                    result = sum(values) / len(values)
                elif rule.aggregation_type == AggregationType.MIN:
                    result = min(values)
                elif rule.aggregation_type == AggregationType.MAX:
                    result = max(values)
                elif rule.aggregation_type == AggregationType.COUNT:
                    result = len(values)
                else:
                    result = values[-1]
                    
                # Create aggregated labels
                agg_labels = {}
                for label in rule.group_by:
                    if group_series and label in group_series[0].labels:
                        agg_labels[label] = group_series[0].labels[label]
                        
                self.record_gauge(rule.output_metric, result, agg_labels)
                
    def add_recording_rule(self, name: str,
                          expression: str,
                          output_metric: str) -> RecordingRule:
        """Добавление recording rule"""
        rule = RecordingRule(
            rule_id=f"record_{uuid.uuid4().hex[:8]}",
            name=name,
            expression=expression,
            output_metric=output_metric
        )
        
        self.recording_rules[name] = rule
        return rule
        
    def _export_sample(self, sample: MetricSample):
        """Экспорт сэмпла"""
        for exporter in self.exporters.values():
            if exporter.active:
                exporter.samples_exported += 1
                
    def query(self, metric_name: str,
             labels: Dict[str, str] = None,
             start_time: datetime = None,
             end_time: datetime = None) -> List[MetricSample]:
        """Запрос метрик"""
        results = []
        
        for series in self.series.values():
            if metric_name not in series.name:
                continue
                
            # Label match
            if labels:
                match = all(series.labels.get(k) == v for k, v in labels.items())
                if not match:
                    continue
                    
            for sample in series.samples:
                if start_time and sample.timestamp < start_time:
                    continue
                if end_time and sample.timestamp > end_time:
                    continue
                results.append(sample)
                
        return results
        
    def get_current_value(self, metric_name: str,
                         labels: Dict[str, str] = None) -> Optional[float]:
        """Текущее значение метрики"""
        series_key = self._series_key(metric_name, labels or {})
        series = self.series.get(series_key)
        
        if series and series.samples:
            return series.samples[-1].value
        return None
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_samples = sum(len(s.samples) for s in self.series.values())
        
        return {
            "series": len(self.series),
            "histograms": len(self.histograms),
            "summaries": len(self.summaries),
            "total_samples": total_samples,
            "collectors": len(self.collectors),
            "exporters": len(self.exporters),
            "transform_rules": len(self.transform_rules),
            "aggregation_rules": len(self.aggregation_rules),
            "recording_rules": len(self.recording_rules)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 277: Metrics Pipeline Platform")
    print("=" * 60)
    
    manager = MetricsPipelineManager()
    print("✓ Metrics Pipeline Manager created")
    
    # Add collectors
    print("\n📥 Adding Collectors...")
    
    collectors_config = [
        ("node-exporter", "http://localhost:9100/metrics", 15),
        ("app-metrics", "http://localhost:8080/metrics", 10),
        ("cadvisor", "http://localhost:8090/metrics", 30),
    ]
    
    for name, endpoint, interval in collectors_config:
        collector = manager.add_collector(name, endpoint, interval)
        print(f"  📥 {name}: {interval}s interval")
        
    # Add exporters
    print("\n📤 Adding Exporters...")
    
    exporters_config = [
        ("prometheus", StorageBackend.PROMETHEUS, "http://prometheus:9090/api/v1/write"),
        ("victoria", StorageBackend.VICTORIA_METRICS, "http://victoria:8428/api/v1/write"),
    ]
    
    for name, backend, endpoint in exporters_config:
        exporter = manager.add_exporter(name, backend, endpoint)
        print(f"  📤 {name}: {backend.value}")
        
    # Add cardinality limits
    print("\n🔒 Adding Cardinality Limits...")
    
    manager.add_cardinality_limit("http_requests", "http_request", 50000)
    manager.add_cardinality_limit("custom_metrics", "custom_", 10000)
    print("  Limits configured")
    
    # Add transform rules
    print("\n🔄 Adding Transform Rules...")
    
    manager.add_transform_rule(
        "cpu-percentage",
        "cpu_usage",
        TransformType.SCALE,
        "cpu_usage_percent",
        {"factor": 100}
    )
    
    manager.add_transform_rule(
        "memory-gb",
        "memory_bytes",
        TransformType.SCALE,
        "memory_gb",
        {"factor": 1 / (1024**3)}
    )
    print("  Transform rules added")
    
    # Add aggregation rules
    print("\n📊 Adding Aggregation Rules...")
    
    manager.add_aggregation_rule(
        "request-rate-by-service",
        "http_requests_total",
        AggregationType.SUM,
        "http_requests_total_by_service",
        ["service"]
    )
    
    manager.add_aggregation_rule(
        "avg-latency",
        "http_request_duration",
        AggregationType.AVG,
        "http_request_duration_avg",
        ["service"]
    )
    print("  Aggregation rules added")
    
    # Record metrics
    print("\n📊 Recording Metrics...")
    
    services = ["api-gateway", "user-service", "order-service", "payment-service"]
    methods = ["GET", "POST", "PUT", "DELETE"]
    paths = ["/api/users", "/api/orders", "/api/products", "/api/payments"]
    
    # Counters
    for _ in range(100):
        service = random.choice(services)
        method = random.choice(methods)
        path = random.choice(paths)
        status = random.choice([200, 200, 200, 200, 201, 400, 404, 500])
        
        manager.record_counter(
            "http_requests_total",
            1,
            {"service": service, "method": method, "path": path, "status": str(status)},
            "Total HTTP requests"
        )
        
    print(f"  Recorded 100 http_requests_total")
    
    # Gauges
    for service in services:
        manager.record_gauge("cpu_usage", random.uniform(0.1, 0.9), {"service": service})
        manager.record_gauge("memory_bytes", random.uniform(100, 500) * 1024**2, {"service": service})
        manager.record_gauge("goroutines", random.randint(50, 200), {"service": service})
        
    print(f"  Recorded gauges for {len(services)} services")
    
    # Histograms
    for _ in range(50):
        service = random.choice(services)
        latency = random.expovariate(10)  # Exponential distribution
        
        manager.record_histogram(
            "http_request_duration_seconds",
            latency,
            {"service": service}
        )
        
    print("  Recorded 50 histogram samples")
    
    # Summaries
    for _ in range(50):
        service = random.choice(services)
        size = random.paretovariate(1) * 1000  # Pareto distribution
        
        manager.record_summary(
            "http_response_size_bytes",
            size,
            {"service": service}
        )
        
    print("  Recorded 50 summary samples")
    
    # Run aggregations
    print("\n📊 Running Aggregations...")
    manager.run_aggregations()
    print("  Aggregations complete")
    
    # Display series
    print("\n📊 Metric Series:")
    
    print("\n  ┌────────────────────────────────┬──────────┬────────────┬────────────┐")
    print("  │ Metric                         │ Type     │ Samples    │ Last Value │")
    print("  ├────────────────────────────────┼──────────┼────────────┼────────────┤")
    
    shown = 0
    for series in manager.series.values():
        if shown >= 10:
            break
        if not series.samples:
            continue
            
        name = series.name[:30].ljust(30)
        mtype = series.metric_type.value[:8].ljust(8)
        samples = str(len(series.samples))[:10].ljust(10)
        last_val = f"{series.samples[-1].value:.2f}"[:10].ljust(10)
        
        print(f"  │ {name} │ {mtype} │ {samples} │ {last_val} │")
        shown += 1
        
    print("  └────────────────────────────────┴──────────┴────────────┴────────────┘")
    
    # Display histograms
    print("\n📊 Histograms:")
    
    for hist_key, hist in list(manager.histograms.items())[:3]:
        print(f"\n  📊 {hist.name} {hist.labels}")
        print(f"     Count: {hist.count}, Sum: {hist.sum_value:.2f}")
        print("     Buckets:")
        
        prev_count = 0
        for bucket in hist.buckets[:6]:
            bar_len = int((bucket.count - prev_count) / max(hist.count, 1) * 20)
            bar = "█" * bar_len
            pct = (bucket.count - prev_count) / max(hist.count, 1) * 100
            print(f"       le={bucket.le:6.3f}: {bar} {pct:.1f}%")
            prev_count = bucket.count
            
    # Display summaries
    print("\n📊 Summaries:")
    
    for summary_key, summary in list(manager.summaries.items())[:3]:
        print(f"\n  📊 {summary.name} {summary.labels}")
        print(f"     Count: {summary.count}, Sum: {summary.sum_value:.2f}")
        print("     Quantiles:")
        
        for q, v in sorted(summary.quantiles.items()):
            print(f"       {q}: {v:.2f}")
            
    # Query metrics
    print("\n🔎 Query Results:")
    
    cpu_results = manager.query("cpu_usage")
    print(f"\n  cpu_usage: {len(cpu_results)} samples")
    
    for sample in cpu_results[:4]:
        print(f"    {sample.labels.get('service', 'N/A')}: {sample.value:.4f}")
        
    # Current values
    print("\n📊 Current Values:")
    
    for service in services:
        cpu = manager.get_current_value("cpu_usage_percent", {"service": service})
        mem = manager.get_current_value("memory_gb", {"service": service})
        
        if cpu is not None:
            cpu_bar = "█" * int(cpu) + "░" * (100 - int(cpu))
            cpu_bar = cpu_bar[:20]
            print(f"  {service:15s}: CPU [{cpu_bar}] {cpu:.1f}%")
            
    # Exporters status
    print("\n📤 Exporter Statistics:")
    
    for exporter in manager.exporters.values():
        status = "🟢 Active" if exporter.active else "🔴 Inactive"
        print(f"  {exporter.name}: {exporter.samples_exported} samples exported {status}")
        
    # Transform rules
    print("\n🔄 Transform Rules:")
    
    for rule in manager.transform_rules.values():
        print(f"  {rule.source_metric} -> [{rule.transform_type.value}] -> {rule.output_metric}")
        
    # Aggregation rules
    print("\n📊 Aggregation Rules:")
    
    for rule in manager.aggregation_rules.values():
        group_str = ", ".join(rule.group_by) if rule.group_by else "all"
        print(f"  {rule.source_metric} [{rule.aggregation_type.value}] by ({group_str}) -> {rule.output_metric}")
        
    # Cardinality
    print("\n🔒 Cardinality Status:")
    
    for limit in manager.cardinality_limits.values():
        pct = limit.current_series / limit.max_series * 100
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"  {limit.name}: [{bar}] {limit.current_series}/{limit.max_series} ({pct:.1f}%)")
        
    # Statistics
    print("\n📊 Pipeline Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Series: {stats['series']}")
    print(f"  Histograms: {stats['histograms']}")
    print(f"  Summaries: {stats['summaries']}")
    print(f"  Total Samples: {stats['total_samples']}")
    print(f"  Collectors: {stats['collectors']}")
    print(f"  Exporters: {stats['exporters']}")
    print(f"  Transform Rules: {stats['transform_rules']}")
    print(f"  Aggregation Rules: {stats['aggregation_rules']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Metrics Pipeline Dashboard                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Metric Series:                 {stats['series']:>12}                        │")
    print(f"│ Total Samples:                 {stats['total_samples']:>12}                        │")
    print(f"│ Histograms:                    {stats['histograms']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Collectors:                    {stats['collectors']:>12}                        │")
    print(f"│ Exporters:                     {stats['exporters']:>12}                        │")
    print(f"│ Rules:                         {stats['transform_rules'] + stats['aggregation_rules']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Metrics Pipeline Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
