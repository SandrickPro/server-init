#!/usr/bin/env python3
"""
Server Init - Iteration 93: Metric Collection Platform
Платформа сбора метрик

Функционал:
- Metric Types - типы метрик (counter, gauge, histogram)
- Metric Collection - сбор метрик
- Time Series Storage - хранение временных рядов
- Aggregation - агрегация данных
- Query Engine - движок запросов
- Dashboards - панели мониторинга
- Alerting - алертинг
- Export/Import - экспорт/импорт
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Tuple, Union
from enum import Enum
from collections import defaultdict
import uuid
import random
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
    PERCENTILE = "percentile"


class AlertState(Enum):
    """Состояние алерта"""
    OK = "ok"
    PENDING = "pending"
    FIRING = "firing"


@dataclass
class Label:
    """Метка метрики"""
    key: str
    value: str


@dataclass
class MetricPoint:
    """Точка данных метрики"""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class Metric:
    """Метрика"""
    name: str
    metric_type: MetricType
    description: str = ""
    unit: str = ""
    
    # Метки
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Значение (для gauge/counter)
    value: float = 0
    
    # Histogram buckets
    buckets: Dict[float, int] = field(default_factory=dict)
    bucket_sum: float = 0
    bucket_count: int = 0
    
    # Summary quantiles
    quantiles: Dict[float, float] = field(default_factory=dict)
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class TimeSeries:
    """Временной ряд"""
    series_id: str
    metric_name: str
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Точки данных
    points: List[MetricPoint] = field(default_factory=list)
    
    # Статистика
    min_value: float = float('inf')
    max_value: float = float('-inf')
    sum_value: float = 0
    count: int = 0
    
    @property
    def avg_value(self) -> float:
        return self.sum_value / self.count if self.count > 0 else 0


@dataclass
class MetricQuery:
    """Запрос метрик"""
    query_id: str
    
    # Имя метрики
    metric_name: str = ""
    
    # Фильтры по меткам
    label_filters: Dict[str, str] = field(default_factory=dict)
    
    # Временной диапазон
    start_time: datetime = field(default_factory=lambda: datetime.now() - timedelta(hours=1))
    end_time: datetime = field(default_factory=datetime.now)
    
    # Агрегация
    aggregation: Optional[AggregationType] = None
    group_by: List[str] = field(default_factory=list)
    
    # Шаг
    step_seconds: int = 60
    
    # Лимит
    limit: int = 1000


@dataclass
class QueryResult:
    """Результат запроса"""
    query_id: str
    
    # Данные
    series: List[Dict[str, Any]] = field(default_factory=list)
    
    # Метаданные
    total_points: int = 0
    execution_time_ms: float = 0


@dataclass
class AlertRule:
    """Правило алерта"""
    rule_id: str
    name: str = ""
    
    # Условие
    metric_name: str = ""
    label_filters: Dict[str, str] = field(default_factory=dict)
    
    # Порог
    condition: str = ">"  # >, <, >=, <=, ==, !=
    threshold: float = 0
    
    # Длительность
    for_duration_seconds: int = 60
    
    # Состояние
    state: AlertState = AlertState.OK
    pending_since: Optional[datetime] = None
    firing_since: Optional[datetime] = None
    
    # Уведомления
    severity: str = "warning"
    annotations: Dict[str, str] = field(default_factory=dict)


@dataclass
class DashboardPanel:
    """Панель дашборда"""
    panel_id: str
    title: str = ""
    
    # Тип визуализации
    visualization: str = "line"  # line, bar, gauge, stat
    
    # Запросы
    queries: List[MetricQuery] = field(default_factory=list)
    
    # Позиция
    x: int = 0
    y: int = 0
    width: int = 12
    height: int = 8


@dataclass
class Dashboard:
    """Дашборд"""
    dashboard_id: str
    name: str = ""
    description: str = ""
    
    # Панели
    panels: List[DashboardPanel] = field(default_factory=list)
    
    # Переменные
    variables: Dict[str, Any] = field(default_factory=dict)
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class MetricRegistry:
    """Реестр метрик"""
    
    def __init__(self):
        self.metrics: Dict[str, Dict[str, Metric]] = {}  # name -> labels_hash -> metric
        
    def _labels_hash(self, labels: Dict[str, str]) -> str:
        """Хеш меток"""
        return "|".join(f"{k}={v}" for k, v in sorted(labels.items()))
        
    def register(self, name: str, metric_type: MetricType,
                  description: str = "", unit: str = "",
                  labels: Dict[str, str] = None) -> Metric:
        """Регистрация метрики"""
        labels = labels or {}
        labels_hash = self._labels_hash(labels)
        
        if name not in self.metrics:
            self.metrics[name] = {}
            
        if labels_hash not in self.metrics[name]:
            metric = Metric(
                name=name,
                metric_type=metric_type,
                description=description,
                unit=unit,
                labels=labels
            )
            self.metrics[name][labels_hash] = metric
            
        return self.metrics[name][labels_hash]
        
    def get(self, name: str, labels: Dict[str, str] = None) -> Optional[Metric]:
        """Получение метрики"""
        labels = labels or {}
        labels_hash = self._labels_hash(labels)
        
        if name in self.metrics and labels_hash in self.metrics[name]:
            return self.metrics[name][labels_hash]
        return None
        
    def get_all(self, name: str) -> List[Metric]:
        """Получение всех метрик с именем"""
        return list(self.metrics.get(name, {}).values())


class Counter:
    """Счётчик"""
    
    def __init__(self, registry: MetricRegistry, name: str,
                  description: str = "", labels: Dict[str, str] = None):
        self.metric = registry.register(
            name, MetricType.COUNTER, description, "count", labels
        )
        
    def inc(self, value: float = 1):
        """Инкремент"""
        self.metric.value += value
        self.metric.updated_at = datetime.now()
        
    @property
    def value(self) -> float:
        return self.metric.value


class Gauge:
    """Измеритель"""
    
    def __init__(self, registry: MetricRegistry, name: str,
                  description: str = "", unit: str = "",
                  labels: Dict[str, str] = None):
        self.metric = registry.register(
            name, MetricType.GAUGE, description, unit, labels
        )
        
    def set(self, value: float):
        """Установка значения"""
        self.metric.value = value
        self.metric.updated_at = datetime.now()
        
    def inc(self, value: float = 1):
        """Инкремент"""
        self.metric.value += value
        self.metric.updated_at = datetime.now()
        
    def dec(self, value: float = 1):
        """Декремент"""
        self.metric.value -= value
        self.metric.updated_at = datetime.now()
        
    @property
    def value(self) -> float:
        return self.metric.value


class Histogram:
    """Гистограмма"""
    
    DEFAULT_BUCKETS = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, float('inf')]
    
    def __init__(self, registry: MetricRegistry, name: str,
                  description: str = "", buckets: List[float] = None,
                  labels: Dict[str, str] = None):
        self.metric = registry.register(
            name, MetricType.HISTOGRAM, description, "seconds", labels
        )
        
        self.bucket_boundaries = buckets or self.DEFAULT_BUCKETS
        for boundary in self.bucket_boundaries:
            self.metric.buckets[boundary] = 0
            
    def observe(self, value: float):
        """Запись наблюдения"""
        self.metric.bucket_sum += value
        self.metric.bucket_count += 1
        self.metric.updated_at = datetime.now()
        
        for boundary in self.bucket_boundaries:
            if value <= boundary:
                self.metric.buckets[boundary] += 1


class TimeSeriesDB:
    """Хранилище временных рядов"""
    
    def __init__(self, retention_hours: int = 24):
        self.series: Dict[str, TimeSeries] = {}
        self.retention_hours = retention_hours
        
    def _series_id(self, metric_name: str, labels: Dict[str, str]) -> str:
        """ID временного ряда"""
        labels_str = "|".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{metric_name}:{labels_str}"
        
    def write(self, metric_name: str, value: float,
               labels: Dict[str, str] = None, timestamp: datetime = None):
        """Запись точки"""
        labels = labels or {}
        timestamp = timestamp or datetime.now()
        
        series_id = self._series_id(metric_name, labels)
        
        if series_id not in self.series:
            self.series[series_id] = TimeSeries(
                series_id=series_id,
                metric_name=metric_name,
                labels=labels
            )
            
        series = self.series[series_id]
        
        point = MetricPoint(timestamp=timestamp, value=value, labels=labels)
        series.points.append(point)
        
        # Обновляем статистику
        series.min_value = min(series.min_value, value)
        series.max_value = max(series.max_value, value)
        series.sum_value += value
        series.count += 1
        
    def query(self, metric_name: str, label_filters: Dict[str, str] = None,
               start_time: datetime = None, end_time: datetime = None) -> List[TimeSeries]:
        """Запрос временных рядов"""
        label_filters = label_filters or {}
        start_time = start_time or (datetime.now() - timedelta(hours=1))
        end_time = end_time or datetime.now()
        
        results = []
        
        for series in self.series.values():
            if series.metric_name != metric_name:
                continue
                
            # Проверяем метки
            matches = True
            for key, value in label_filters.items():
                if series.labels.get(key) != value:
                    matches = False
                    break
                    
            if not matches:
                continue
                
            # Фильтруем точки по времени
            filtered_points = [
                p for p in series.points
                if start_time <= p.timestamp <= end_time
            ]
            
            if filtered_points:
                filtered_series = TimeSeries(
                    series_id=series.series_id,
                    metric_name=series.metric_name,
                    labels=series.labels,
                    points=filtered_points
                )
                results.append(filtered_series)
                
        return results
        
    def cleanup(self):
        """Очистка старых данных"""
        cutoff = datetime.now() - timedelta(hours=self.retention_hours)
        
        for series in self.series.values():
            series.points = [p for p in series.points if p.timestamp >= cutoff]


class QueryEngine:
    """Движок запросов"""
    
    def __init__(self, tsdb: TimeSeriesDB):
        self.tsdb = tsdb
        
    def execute(self, query: MetricQuery) -> QueryResult:
        """Выполнение запроса"""
        start = datetime.now()
        
        result = QueryResult(query_id=query.query_id)
        
        # Получаем временные ряды
        series_list = self.tsdb.query(
            query.metric_name,
            query.label_filters,
            query.start_time,
            query.end_time
        )
        
        # Применяем агрегацию
        if query.aggregation:
            series_list = self._aggregate(series_list, query)
            
        # Форматируем результат
        for series in series_list:
            result.series.append({
                "metric": series.metric_name,
                "labels": series.labels,
                "values": [(p.timestamp.isoformat(), p.value) for p in series.points]
            })
            result.total_points += len(series.points)
            
        result.execution_time_ms = (datetime.now() - start).total_seconds() * 1000
        
        return result
        
    def _aggregate(self, series_list: List[TimeSeries],
                    query: MetricQuery) -> List[TimeSeries]:
        """Агрегация"""
        if query.aggregation == AggregationType.SUM:
            return self._sum_series(series_list, query)
        elif query.aggregation == AggregationType.AVG:
            return self._avg_series(series_list, query)
        elif query.aggregation == AggregationType.MAX:
            return self._max_series(series_list, query)
        elif query.aggregation == AggregationType.MIN:
            return self._min_series(series_list, query)
        elif query.aggregation == AggregationType.RATE:
            return self._rate_series(series_list, query)
        return series_list
        
    def _sum_series(self, series_list: List[TimeSeries],
                     query: MetricQuery) -> List[TimeSeries]:
        """Суммирование"""
        if not series_list:
            return []
            
        # Группируем точки по времени
        time_buckets: Dict[datetime, float] = defaultdict(float)
        
        for series in series_list:
            for point in series.points:
                # Округляем до шага
                bucket = self._round_time(point.timestamp, query.step_seconds)
                time_buckets[bucket] += point.value
                
        # Создаём результирующий ряд
        result = TimeSeries(
            series_id="sum",
            metric_name=f"sum({query.metric_name})",
            labels={}
        )
        
        for timestamp, value in sorted(time_buckets.items()):
            result.points.append(MetricPoint(timestamp=timestamp, value=value))
            
        return [result]
        
    def _avg_series(self, series_list: List[TimeSeries],
                     query: MetricQuery) -> List[TimeSeries]:
        """Среднее"""
        if not series_list:
            return []
            
        time_buckets: Dict[datetime, List[float]] = defaultdict(list)
        
        for series in series_list:
            for point in series.points:
                bucket = self._round_time(point.timestamp, query.step_seconds)
                time_buckets[bucket].append(point.value)
                
        result = TimeSeries(
            series_id="avg",
            metric_name=f"avg({query.metric_name})",
            labels={}
        )
        
        for timestamp, values in sorted(time_buckets.items()):
            avg = sum(values) / len(values)
            result.points.append(MetricPoint(timestamp=timestamp, value=avg))
            
        return [result]
        
    def _max_series(self, series_list: List[TimeSeries],
                     query: MetricQuery) -> List[TimeSeries]:
        """Максимум"""
        if not series_list:
            return []
            
        time_buckets: Dict[datetime, float] = {}
        
        for series in series_list:
            for point in series.points:
                bucket = self._round_time(point.timestamp, query.step_seconds)
                if bucket not in time_buckets:
                    time_buckets[bucket] = point.value
                else:
                    time_buckets[bucket] = max(time_buckets[bucket], point.value)
                    
        result = TimeSeries(
            series_id="max",
            metric_name=f"max({query.metric_name})",
            labels={}
        )
        
        for timestamp, value in sorted(time_buckets.items()):
            result.points.append(MetricPoint(timestamp=timestamp, value=value))
            
        return [result]
        
    def _min_series(self, series_list: List[TimeSeries],
                     query: MetricQuery) -> List[TimeSeries]:
        """Минимум"""
        if not series_list:
            return []
            
        time_buckets: Dict[datetime, float] = {}
        
        for series in series_list:
            for point in series.points:
                bucket = self._round_time(point.timestamp, query.step_seconds)
                if bucket not in time_buckets:
                    time_buckets[bucket] = point.value
                else:
                    time_buckets[bucket] = min(time_buckets[bucket], point.value)
                    
        result = TimeSeries(
            series_id="min",
            metric_name=f"min({query.metric_name})",
            labels={}
        )
        
        for timestamp, value in sorted(time_buckets.items()):
            result.points.append(MetricPoint(timestamp=timestamp, value=value))
            
        return [result]
        
    def _rate_series(self, series_list: List[TimeSeries],
                      query: MetricQuery) -> List[TimeSeries]:
        """Rate (скорость изменения)"""
        results = []
        
        for series in series_list:
            if len(series.points) < 2:
                continue
                
            rate_series = TimeSeries(
                series_id=f"rate_{series.series_id}",
                metric_name=f"rate({series.metric_name})",
                labels=series.labels
            )
            
            sorted_points = sorted(series.points, key=lambda p: p.timestamp)
            
            for i in range(1, len(sorted_points)):
                prev = sorted_points[i - 1]
                curr = sorted_points[i]
                
                time_diff = (curr.timestamp - prev.timestamp).total_seconds()
                if time_diff > 0:
                    rate = (curr.value - prev.value) / time_diff
                    rate_series.points.append(MetricPoint(
                        timestamp=curr.timestamp,
                        value=max(0, rate)  # rate не может быть отрицательным для counter
                    ))
                    
            if rate_series.points:
                results.append(rate_series)
                
        return results
        
    def _round_time(self, dt: datetime, step_seconds: int) -> datetime:
        """Округление времени до шага"""
        seconds = (dt - datetime.min).total_seconds()
        rounded = (seconds // step_seconds) * step_seconds
        return datetime.min + timedelta(seconds=rounded)


class AlertManager:
    """Менеджер алертов"""
    
    def __init__(self, query_engine: QueryEngine):
        self.query_engine = query_engine
        self.rules: Dict[str, AlertRule] = {}
        self.alerts: List[Dict[str, Any]] = []
        
    def add_rule(self, name: str, metric_name: str, condition: str,
                  threshold: float, for_duration: int = 60,
                  label_filters: Dict[str, str] = None,
                  severity: str = "warning") -> AlertRule:
        """Добавление правила"""
        rule = AlertRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name=name,
            metric_name=metric_name,
            label_filters=label_filters or {},
            condition=condition,
            threshold=threshold,
            for_duration_seconds=for_duration,
            severity=severity
        )
        self.rules[rule.rule_id] = rule
        return rule
        
    def evaluate(self):
        """Оценка правил"""
        now = datetime.now()
        
        for rule in self.rules.values():
            # Получаем текущее значение
            query = MetricQuery(
                query_id=f"alert_{rule.rule_id}",
                metric_name=rule.metric_name,
                label_filters=rule.label_filters,
                start_time=now - timedelta(minutes=5),
                end_time=now,
                aggregation=AggregationType.AVG
            )
            
            result = self.query_engine.execute(query)
            
            # Проверяем условие
            current_value = None
            if result.series and result.series[0]["values"]:
                current_value = result.series[0]["values"][-1][1]
                
            if current_value is None:
                continue
                
            triggered = self._check_condition(current_value, rule.condition, rule.threshold)
            
            if triggered:
                if rule.state == AlertState.OK:
                    rule.state = AlertState.PENDING
                    rule.pending_since = now
                elif rule.state == AlertState.PENDING:
                    pending_duration = (now - rule.pending_since).total_seconds()
                    if pending_duration >= rule.for_duration_seconds:
                        rule.state = AlertState.FIRING
                        rule.firing_since = now
                        
                        self.alerts.append({
                            "rule_id": rule.rule_id,
                            "name": rule.name,
                            "value": current_value,
                            "threshold": rule.threshold,
                            "timestamp": now
                        })
            else:
                rule.state = AlertState.OK
                rule.pending_since = None
                rule.firing_since = None
                
    def _check_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Проверка условия"""
        if condition == ">":
            return value > threshold
        elif condition == ">=":
            return value >= threshold
        elif condition == "<":
            return value < threshold
        elif condition == "<=":
            return value <= threshold
        elif condition == "==":
            return value == threshold
        elif condition == "!=":
            return value != threshold
        return False


class MetricCollectionPlatform:
    """Платформа сбора метрик"""
    
    def __init__(self):
        self.registry = MetricRegistry()
        self.tsdb = TimeSeriesDB()
        self.query_engine = QueryEngine(self.tsdb)
        self.alert_manager = AlertManager(self.query_engine)
        self.dashboards: Dict[str, Dashboard] = {}
        
        # Collectors
        self.collectors: List[Callable] = []
        
    def counter(self, name: str, description: str = "",
                 labels: Dict[str, str] = None) -> Counter:
        """Создание счётчика"""
        return Counter(self.registry, name, description, labels)
        
    def gauge(self, name: str, description: str = "",
               unit: str = "", labels: Dict[str, str] = None) -> Gauge:
        """Создание измерителя"""
        return Gauge(self.registry, name, description, unit, labels)
        
    def histogram(self, name: str, description: str = "",
                   buckets: List[float] = None,
                   labels: Dict[str, str] = None) -> Histogram:
        """Создание гистограммы"""
        return Histogram(self.registry, name, description, buckets, labels)
        
    async def collect(self):
        """Сбор метрик"""
        for metric_name, metrics_by_labels in self.registry.metrics.items():
            for metric in metrics_by_labels.values():
                self.tsdb.write(
                    metric.name,
                    metric.value,
                    metric.labels
                )
                
        # Запускаем collectors
        for collector in self.collectors:
            if asyncio.iscoroutinefunction(collector):
                await collector(self)
            else:
                collector(self)
                
    def create_dashboard(self, name: str, description: str = "") -> Dashboard:
        """Создание дашборда"""
        dashboard = Dashboard(
            dashboard_id=f"dash_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description
        )
        self.dashboards[dashboard.dashboard_id] = dashboard
        return dashboard
        
    def add_panel(self, dashboard_id: str, title: str,
                   metric_name: str, visualization: str = "line",
                   **kwargs) -> DashboardPanel:
        """Добавление панели"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            raise ValueError(f"Dashboard {dashboard_id} not found")
            
        query = MetricQuery(
            query_id=f"query_{uuid.uuid4().hex[:8]}",
            metric_name=metric_name,
            **kwargs
        )
        
        panel = DashboardPanel(
            panel_id=f"panel_{uuid.uuid4().hex[:8]}",
            title=title,
            visualization=visualization,
            queries=[query]
        )
        dashboard.panels.append(panel)
        return panel
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_metrics = sum(
            len(metrics) for metrics in self.registry.metrics.values()
        )
        
        return {
            "total_metrics": total_metrics,
            "metric_names": len(self.registry.metrics),
            "time_series": len(self.tsdb.series),
            "alert_rules": len(self.alert_manager.rules),
            "firing_alerts": sum(
                1 for r in self.alert_manager.rules.values()
                if r.state == AlertState.FIRING
            ),
            "dashboards": len(self.dashboards)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 93: Metric Collection Platform")
    print("=" * 60)
    
    async def demo():
        platform = MetricCollectionPlatform()
        print("✓ Metric Collection Platform created")
        
        # Создание метрик
        print("\n📊 Creating Metrics...")
        
        # Counters
        http_requests = platform.counter(
            "http_requests_total",
            "Total HTTP requests",
            labels={"service": "api"}
        )
        
        errors = platform.counter(
            "errors_total",
            "Total errors",
            labels={"service": "api"}
        )
        
        print(f"  ✓ Counter: http_requests_total")
        print(f"  ✓ Counter: errors_total")
        
        # Gauges
        cpu_usage = platform.gauge(
            "cpu_usage_percent",
            "CPU usage percentage",
            unit="%",
            labels={"host": "server-01"}
        )
        
        memory_usage = platform.gauge(
            "memory_usage_bytes",
            "Memory usage in bytes",
            unit="bytes",
            labels={"host": "server-01"}
        )
        
        active_connections = platform.gauge(
            "active_connections",
            "Active connections",
            labels={"service": "api"}
        )
        
        print(f"  ✓ Gauge: cpu_usage_percent")
        print(f"  ✓ Gauge: memory_usage_bytes")
        print(f"  ✓ Gauge: active_connections")
        
        # Histogram
        request_duration = platform.histogram(
            "http_request_duration_seconds",
            "HTTP request duration",
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],
            labels={"service": "api"}
        )
        
        print(f"  ✓ Histogram: http_request_duration_seconds")
        
        # Генерация данных
        print("\n📥 Generating Metric Data...")
        
        # Симуляция запросов
        for i in range(100):
            http_requests.inc()
            
            # 5% ошибок
            if random.random() < 0.05:
                errors.inc()
                
            # Время ответа
            duration = random.uniform(0.01, 0.5)
            if random.random() < 0.1:  # 10% медленных
                duration = random.uniform(1, 5)
            request_duration.observe(duration)
            
        print(f"  ✓ HTTP Requests: {http_requests.value}")
        print(f"  ✓ Errors: {errors.value}")
        print(f"  ✓ Histogram observations: {request_duration.metric.bucket_count}")
        
        # Обновление gauges
        cpu_usage.set(random.uniform(20, 80))
        memory_usage.set(random.uniform(1e9, 4e9))
        active_connections.set(random.randint(50, 200))
        
        print(f"\n  ✓ CPU Usage: {cpu_usage.value:.1f}%")
        print(f"  ✓ Memory Usage: {memory_usage.value / 1e9:.2f} GB")
        print(f"  ✓ Active Connections: {active_connections.value}")
        
        # Сбор метрик в TSDB
        print("\n📈 Collecting Metrics to TSDB...")
        
        # Симуляция временного ряда
        base_time = datetime.now() - timedelta(hours=1)
        
        for i in range(60):  # 60 минут данных
            timestamp = base_time + timedelta(minutes=i)
            
            # HTTP requests rate
            platform.tsdb.write(
                "http_requests_total",
                random.randint(100, 500),
                {"service": "api"},
                timestamp
            )
            
            # CPU usage
            platform.tsdb.write(
                "cpu_usage_percent",
                random.uniform(20, 80),
                {"host": "server-01"},
                timestamp
            )
            
            # Memory
            platform.tsdb.write(
                "memory_usage_bytes",
                random.uniform(1e9, 4e9),
                {"host": "server-01"},
                timestamp
            )
            
            # Errors
            platform.tsdb.write(
                "errors_total",
                random.randint(0, 20),
                {"service": "api"},
                timestamp
            )
            
        print(f"  ✓ Written {len(platform.tsdb.series)} time series")
        
        # Запросы
        print("\n🔍 Query Examples...")
        
        # Простой запрос
        query = MetricQuery(
            query_id="q1",
            metric_name="cpu_usage_percent",
            label_filters={"host": "server-01"},
            start_time=datetime.now() - timedelta(hours=1)
        )
        
        result = platform.query_engine.execute(query)
        
        print(f"\n  Query: cpu_usage_percent{{host='server-01'}}")
        print(f"  Points: {result.total_points}")
        print(f"  Execution: {result.execution_time_ms:.2f}ms")
        
        if result.series and result.series[0]["values"]:
            values = [v[1] for v in result.series[0]["values"][-5:]]
            print(f"  Last 5 values: {[f'{v:.1f}' for v in values]}")
            
        # Запрос с агрегацией (AVG)
        query = MetricQuery(
            query_id="q2",
            metric_name="cpu_usage_percent",
            aggregation=AggregationType.AVG,
            step_seconds=300,  # 5 минут
            start_time=datetime.now() - timedelta(hours=1)
        )
        
        result = platform.query_engine.execute(query)
        
        print(f"\n  Query: avg(cpu_usage_percent) step 5m")
        print(f"  Points: {result.total_points}")
        
        if result.series and result.series[0]["values"]:
            values = [v[1] for v in result.series[0]["values"][-5:]]
            print(f"  Last 5 avg values: {[f'{v:.1f}' for v in values]}")
            
        # Запрос с RATE
        query = MetricQuery(
            query_id="q3",
            metric_name="http_requests_total",
            aggregation=AggregationType.RATE,
            start_time=datetime.now() - timedelta(hours=1)
        )
        
        result = platform.query_engine.execute(query)
        
        print(f"\n  Query: rate(http_requests_total)")
        print(f"  Points: {result.total_points}")
        
        # Алерты
        print("\n🚨 Creating Alert Rules...")
        
        platform.alert_manager.add_rule(
            "High CPU Usage",
            "cpu_usage_percent",
            ">",
            threshold=80,
            for_duration=60,
            label_filters={"host": "server-01"},
            severity="warning"
        )
        
        platform.alert_manager.add_rule(
            "Critical CPU Usage",
            "cpu_usage_percent",
            ">",
            threshold=95,
            for_duration=30,
            severity="critical"
        )
        
        platform.alert_manager.add_rule(
            "High Error Rate",
            "errors_total",
            ">",
            threshold=50,
            for_duration=60,
            severity="warning"
        )
        
        print(f"  ✓ Created {len(platform.alert_manager.rules)} alert rules")
        
        # Оценка алертов
        print("\n  Evaluating alerts...")
        platform.alert_manager.evaluate()
        
        for rule in platform.alert_manager.rules.values():
            state_icon = {
                AlertState.OK: "✅",
                AlertState.PENDING: "⏳",
                AlertState.FIRING: "🔥"
            }.get(rule.state, "?")
            
            print(f"  {state_icon} {rule.name}: {rule.state.value}")
            
        # Дашборд
        print("\n📋 Creating Dashboard...")
        
        dashboard = platform.create_dashboard(
            "Infrastructure Overview",
            "Main infrastructure monitoring dashboard"
        )
        
        platform.add_panel(
            dashboard.dashboard_id,
            "CPU Usage",
            "cpu_usage_percent",
            visualization="line"
        )
        
        platform.add_panel(
            dashboard.dashboard_id,
            "Memory Usage",
            "memory_usage_bytes",
            visualization="line"
        )
        
        platform.add_panel(
            dashboard.dashboard_id,
            "HTTP Requests",
            "http_requests_total",
            visualization="line"
        )
        
        platform.add_panel(
            dashboard.dashboard_id,
            "Error Rate",
            "errors_total",
            visualization="bar"
        )
        
        print(f"  ✓ Dashboard: {dashboard.name}")
        print(f"  ✓ Panels: {len(dashboard.panels)}")
        
        # Histogram buckets
        print("\n📊 Histogram Analysis:")
        
        print(f"\n  http_request_duration_seconds")
        print(f"  Count: {request_duration.metric.bucket_count}")
        print(f"  Sum: {request_duration.metric.bucket_sum:.2f}s")
        print(f"  Avg: {request_duration.metric.bucket_sum / request_duration.metric.bucket_count:.3f}s")
        
        print("\n  Bucket distribution:")
        for bucket, count in sorted(request_duration.metric.buckets.items()):
            if bucket == float('inf'):
                label = "+Inf"
            else:
                label = f"<={bucket}s"
            bar = "█" * (count // 5)
            print(f"    {label:>8}: {bar} ({count})")
            
        # Статистика
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Metrics: {stats['total_metrics']}")
        print(f"  Metric Names: {stats['metric_names']}")
        print(f"  Time Series: {stats['time_series']}")
        print(f"  Alert Rules: {stats['alert_rules']}")
        print(f"  Firing Alerts: {stats['firing_alerts']}")
        print(f"  Dashboards: {stats['dashboards']}")
        
        # Метрики по типам
        print("\n  Metrics by Type:")
        
        type_counts = defaultdict(int)
        for metrics in platform.registry.metrics.values():
            for metric in metrics.values():
                type_counts[metric.metric_type.value] += 1
                
        for mtype, count in sorted(type_counts.items()):
            print(f"    {mtype}: {count}")
            
        # Dashboard Render
        print("\n📋 Metric Collection Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │             Metric Collection Overview                      │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Metrics:   {stats['total_metrics']:>6}                              │")
        print(f"  │ Time Series:     {stats['time_series']:>6}                              │")
        print(f"  │ Alert Rules:     {stats['alert_rules']:>6}                              │")
        print(f"  │ Firing Alerts:   {stats['firing_alerts']:>6}                              │")
        print(f"  │ Dashboards:      {stats['dashboards']:>6}                              │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Metric Collection Platform initialized!")
    print("=" * 60)
