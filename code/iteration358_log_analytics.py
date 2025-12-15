#!/usr/bin/env python3
"""
Server Init - Iteration 358: Log Analytics Platform
Платформа аналитики логов

Функционал:
- Log Ingestion - приём логов
- Log Parsing - парсинг логов
- Log Indexing - индексация логов
- Full-Text Search - полнотекстовый поиск
- Log Aggregation - агрегация логов
- Pattern Detection - обнаружение паттернов
- Anomaly Detection - обнаружение аномалий
- Log Retention - ретеншн логов
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import json
import re


class LogFormat(Enum):
    """Формат логов"""
    JSON = "json"
    PLAIN_TEXT = "plain_text"
    SYSLOG = "syslog"
    CLF = "clf"  # Common Log Format
    GROK = "grok"
    CSV = "csv"


class LogLevel(Enum):
    """Уровень лога"""
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    FATAL = "fatal"


class IndexStatus(Enum):
    """Статус индекса"""
    CREATING = "creating"
    ACTIVE = "active"
    READONLY = "readonly"
    DELETING = "deleting"


class RetentionAction(Enum):
    """Действие ретеншена"""
    DELETE = "delete"
    ARCHIVE = "archive"
    COMPRESS = "compress"
    ROLLOVER = "rollover"


class AggregationType(Enum):
    """Тип агрегации"""
    COUNT = "count"
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    PERCENTILE = "percentile"
    CARDINALITY = "cardinality"


class PatternType(Enum):
    """Тип паттерна"""
    COMMON = "common"
    RARE = "rare"
    ERROR = "error"
    ANOMALY = "anomaly"


@dataclass
class LogSource:
    """Источник логов"""
    source_id: str
    name: str
    
    # Type
    source_type: str = ""  # filebeat, fluentd, logstash, api
    
    # Format
    log_format: LogFormat = LogFormat.JSON
    
    # Parser
    parser_id: Optional[str] = None
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Status
    is_active: bool = True
    
    # Stats
    events_received: int = 0
    bytes_received: int = 0
    last_event_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class LogParser:
    """Парсер логов"""
    parser_id: str
    name: str
    
    # Format
    log_format: LogFormat = LogFormat.JSON
    
    # Pattern (for grok)
    grok_pattern: str = ""
    
    # Fields
    timestamp_field: str = "timestamp"
    message_field: str = "message"
    level_field: str = "level"
    
    # Mapping
    field_mapping: Dict[str, str] = field(default_factory=dict)
    
    # Transformations
    transformations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class LogEntry:
    """Запись лога"""
    log_id: str
    
    # Content
    raw_message: str = ""
    parsed_message: str = ""
    
    # Level
    level: LogLevel = LogLevel.INFO
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)
    ingested_at: datetime = field(default_factory=datetime.now)
    
    # Source
    source_id: str = ""
    source_name: str = ""
    
    # Context
    host: str = ""
    service: str = ""
    environment: str = ""
    
    # Trace correlation
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    
    # Fields
    fields: Dict[str, Any] = field(default_factory=dict)
    
    # Tags
    tags: List[str] = field(default_factory=list)


@dataclass
class LogIndex:
    """Индекс логов"""
    index_id: str
    name: str
    
    # Pattern
    index_pattern: str = ""  # logs-*
    
    # Status
    status: IndexStatus = IndexStatus.CREATING
    
    # Stats
    doc_count: int = 0
    size_bytes: int = 0
    
    # Shards
    primary_shards: int = 5
    replica_shards: int = 1
    
    # Mapping
    field_mappings: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    rollover_at: Optional[datetime] = None


@dataclass
class SearchQuery:
    """Поисковый запрос"""
    query_id: str
    
    # Query
    query_string: str = ""
    
    # Filters
    time_range_start: Optional[datetime] = None
    time_range_end: Optional[datetime] = None
    
    # Level filter
    levels: List[LogLevel] = field(default_factory=list)
    
    # Source filter
    sources: List[str] = field(default_factory=list)
    
    # Field filters
    field_filters: Dict[str, Any] = field(default_factory=dict)
    
    # Pagination
    from_offset: int = 0
    size: int = 100
    
    # Sort
    sort_field: str = "timestamp"
    sort_order: str = "desc"
    
    # Timestamps
    executed_at: datetime = field(default_factory=datetime.now)
    duration_ms: float = 0.0


@dataclass
class SearchResult:
    """Результат поиска"""
    result_id: str
    query_id: str
    
    # Results
    total_hits: int = 0
    hits: List[LogEntry] = field(default_factory=list)
    
    # Aggregations
    aggregations: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Aggregation:
    """Агрегация"""
    aggregation_id: str
    name: str
    
    # Type
    agg_type: AggregationType = AggregationType.COUNT
    
    # Field
    field: str = ""
    
    # Interval (for date histogram)
    interval: str = ""  # 1m, 5m, 1h, 1d
    
    # Buckets
    buckets: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SavedSearch:
    """Сохранённый поиск"""
    saved_id: str
    name: str
    
    # Query
    query_string: str = ""
    
    # Filters
    filters: Dict[str, Any] = field(default_factory=dict)
    
    # Columns
    columns: List[str] = field(default_factory=list)
    
    # Time range
    time_range: str = "15m"
    
    # Owner
    owner: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_used_at: Optional[datetime] = None


@dataclass
class RetentionPolicy:
    """Политика ретеншена"""
    policy_id: str
    name: str
    
    # Index pattern
    index_pattern: str = ""
    
    # Age
    max_age_days: int = 30
    
    # Size
    max_size_gb: Optional[int] = None
    
    # Action
    action: RetentionAction = RetentionAction.DELETE
    
    # Archive config
    archive_path: str = ""
    
    # Status
    is_enabled: bool = True
    
    # Stats
    last_executed: Optional[datetime] = None
    indices_affected: int = 0
    bytes_freed: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class LogPattern:
    """Паттерн логов"""
    pattern_id: str
    
    # Pattern
    pattern_template: str = ""
    pattern_regex: str = ""
    
    # Type
    pattern_type: PatternType = PatternType.COMMON
    
    # Stats
    occurrence_count: int = 0
    percentage: float = 0.0
    
    # Samples
    sample_logs: List[str] = field(default_factory=list)
    
    # Fields extracted
    extracted_fields: List[str] = field(default_factory=list)
    
    # Timestamps
    discovered_at: datetime = field(default_factory=datetime.now)
    last_seen: Optional[datetime] = None


@dataclass
class Anomaly:
    """Аномалия"""
    anomaly_id: str
    
    # Description
    description: str = ""
    
    # Score
    anomaly_score: float = 0.0
    
    # Type
    anomaly_type: str = ""  # spike, drop, pattern_change, new_pattern
    
    # Affected
    affected_field: str = ""
    affected_value: Any = None
    
    # Baseline
    baseline_value: float = 0.0
    actual_value: float = 0.0
    
    # Time range
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    # Severity
    severity: str = "medium"  # low, medium, high, critical


@dataclass
class Dashboard:
    """Дашборд логов"""
    dashboard_id: str
    name: str
    
    # Description
    description: str = ""
    
    # Widgets
    widgets: List[Dict[str, Any]] = field(default_factory=list)
    
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
class Alert:
    """Алерт логов"""
    alert_id: str
    name: str
    
    # Query
    query_string: str = ""
    
    # Condition
    condition_type: str = ""  # count, threshold, pattern
    threshold: float = 0.0
    
    # Time window
    time_window: str = "5m"
    
    # Severity
    severity: str = "warning"
    
    # Actions
    actions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Status
    is_enabled: bool = True
    is_triggered: bool = False
    last_triggered: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class LogAnalyticsMetrics:
    """Метрики платформы"""
    metrics_id: str
    
    # Sources
    total_sources: int = 0
    active_sources: int = 0
    
    # Logs
    total_logs: int = 0
    logs_per_second: float = 0.0
    bytes_per_second: float = 0.0
    
    # Indices
    total_indices: int = 0
    total_index_size_gb: float = 0.0
    
    # Searches
    total_searches: int = 0
    avg_search_latency_ms: float = 0.0
    
    # Patterns
    total_patterns: int = 0
    anomalies_detected: int = 0
    
    # Timestamps
    collected_at: datetime = field(default_factory=datetime.now)


class LogAnalyticsPlatform:
    """Платформа аналитики логов"""
    
    def __init__(self, platform_name: str = "log-analytics"):
        self.platform_name = platform_name
        self.sources: Dict[str, LogSource] = {}
        self.parsers: Dict[str, LogParser] = {}
        self.logs: Dict[str, LogEntry] = {}
        self.indices: Dict[str, LogIndex] = {}
        self.queries: Dict[str, SearchQuery] = {}
        self.results: Dict[str, SearchResult] = {}
        self.saved_searches: Dict[str, SavedSearch] = {}
        self.retention_policies: Dict[str, RetentionPolicy] = {}
        self.patterns: Dict[str, LogPattern] = {}
        self.anomalies: Dict[str, Anomaly] = {}
        self.dashboards: Dict[str, Dashboard] = {}
        self.alerts: Dict[str, Alert] = {}
        
    async def create_log_source(self, name: str,
                               source_type: str,
                               log_format: LogFormat = LogFormat.JSON,
                               tags: Dict[str, str] = None) -> LogSource:
        """Создание источника логов"""
        source = LogSource(
            source_id=f"src_{uuid.uuid4().hex[:8]}",
            name=name,
            source_type=source_type,
            log_format=log_format,
            tags=tags or {}
        )
        
        self.sources[source.source_id] = source
        return source
        
    async def create_parser(self, name: str,
                           log_format: LogFormat,
                           grok_pattern: str = "",
                           timestamp_field: str = "timestamp",
                           message_field: str = "message",
                           level_field: str = "level",
                           field_mapping: Dict[str, str] = None) -> LogParser:
        """Создание парсера"""
        parser = LogParser(
            parser_id=f"prs_{uuid.uuid4().hex[:8]}",
            name=name,
            log_format=log_format,
            grok_pattern=grok_pattern,
            timestamp_field=timestamp_field,
            message_field=message_field,
            level_field=level_field,
            field_mapping=field_mapping or {}
        )
        
        self.parsers[parser.parser_id] = parser
        return parser
        
    async def ingest_log(self, source_id: str,
                        raw_message: str,
                        level: LogLevel = LogLevel.INFO,
                        host: str = "",
                        service: str = "",
                        environment: str = "production",
                        trace_id: Optional[str] = None,
                        fields: Dict[str, Any] = None) -> Optional[LogEntry]:
        """Приём лога"""
        source = self.sources.get(source_id)
        if not source:
            return None
            
        log = LogEntry(
            log_id=f"log_{uuid.uuid4().hex[:12]}",
            raw_message=raw_message,
            parsed_message=raw_message,
            level=level,
            source_id=source_id,
            source_name=source.name,
            host=host,
            service=service,
            environment=environment,
            trace_id=trace_id,
            fields=fields or {}
        )
        
        self.logs[log.log_id] = log
        
        # Update source stats
        source.events_received += 1
        source.bytes_received += len(raw_message.encode('utf-8'))
        source.last_event_at = datetime.now()
        
        return log
        
    async def bulk_ingest(self, source_id: str,
                         logs_data: List[Dict[str, Any]]) -> List[LogEntry]:
        """Пакетный приём логов"""
        ingested = []
        for data in logs_data:
            log = await self.ingest_log(
                source_id=source_id,
                raw_message=data.get("message", ""),
                level=LogLevel(data.get("level", "info")),
                host=data.get("host", ""),
                service=data.get("service", ""),
                environment=data.get("environment", "production"),
                trace_id=data.get("trace_id"),
                fields=data.get("fields", {})
            )
            if log:
                ingested.append(log)
        return ingested
        
    async def create_index(self, name: str,
                          index_pattern: str = "",
                          primary_shards: int = 5,
                          replica_shards: int = 1,
                          field_mappings: Dict[str, str] = None) -> LogIndex:
        """Создание индекса"""
        index = LogIndex(
            index_id=f"idx_{uuid.uuid4().hex[:8]}",
            name=name,
            index_pattern=index_pattern or f"{name}-*",
            primary_shards=primary_shards,
            replica_shards=replica_shards,
            field_mappings=field_mappings or {
                "timestamp": "date",
                "message": "text",
                "level": "keyword",
                "service": "keyword",
                "host": "keyword"
            }
        )
        
        # Simulate index creation
        await asyncio.sleep(0.01)
        index.status = IndexStatus.ACTIVE
        
        self.indices[index.index_id] = index
        return index
        
    async def search(self, query_string: str,
                    time_range_start: Optional[datetime] = None,
                    time_range_end: Optional[datetime] = None,
                    levels: List[LogLevel] = None,
                    sources: List[str] = None,
                    field_filters: Dict[str, Any] = None,
                    size: int = 100) -> SearchResult:
        """Поиск логов"""
        query = SearchQuery(
            query_id=f"qry_{uuid.uuid4().hex[:8]}",
            query_string=query_string,
            time_range_start=time_range_start,
            time_range_end=time_range_end,
            levels=levels or [],
            sources=sources or [],
            field_filters=field_filters or {},
            size=size
        )
        
        # Perform search
        hits = []
        query_lower = query_string.lower()
        
        for log in self.logs.values():
            # Text search
            if query_string and query_lower not in log.raw_message.lower():
                continue
                
            # Time range filter
            if time_range_start and log.timestamp < time_range_start:
                continue
            if time_range_end and log.timestamp > time_range_end:
                continue
                
            # Level filter
            if levels and log.level not in levels:
                continue
                
            # Source filter
            if sources and log.source_id not in sources:
                continue
                
            # Field filters
            match = True
            for field_name, field_value in (field_filters or {}).items():
                if log.fields.get(field_name) != field_value:
                    match = False
                    break
                    
            if match:
                hits.append(log)
                
            if len(hits) >= size:
                break
                
        # Sort by timestamp
        hits.sort(key=lambda x: x.timestamp, reverse=True)
        
        query.duration_ms = random.uniform(1, 50)
        self.queries[query.query_id] = query
        
        result = SearchResult(
            result_id=f"res_{uuid.uuid4().hex[:8]}",
            query_id=query.query_id,
            total_hits=len(hits),
            hits=hits[:size]
        )
        
        self.results[result.result_id] = result
        return result
        
    async def aggregate(self, agg_type: AggregationType,
                       field: str,
                       interval: str = "",
                       query_string: str = "") -> Aggregation:
        """Агрегация логов"""
        aggregation = Aggregation(
            aggregation_id=f"agg_{uuid.uuid4().hex[:8]}",
            name=f"{agg_type.value}_{field}",
            agg_type=agg_type,
            field=field,
            interval=interval
        )
        
        # Perform aggregation
        if agg_type == AggregationType.COUNT:
            # Count by field value
            counts = {}
            for log in self.logs.values():
                value = log.fields.get(field, str(getattr(log, field, "unknown")))
                counts[value] = counts.get(value, 0) + 1
                
            aggregation.buckets = [{"key": k, "doc_count": v} for k, v in sorted(counts.items(), key=lambda x: x[1], reverse=True)]
            
        elif agg_type == AggregationType.SUM:
            total = sum(log.fields.get(field, 0) for log in self.logs.values() if isinstance(log.fields.get(field), (int, float)))
            aggregation.buckets = [{"value": total}]
            
        return aggregation
        
    async def save_search(self, name: str,
                         query_string: str,
                         filters: Dict[str, Any] = None,
                         columns: List[str] = None,
                         owner: str = "") -> SavedSearch:
        """Сохранение поиска"""
        saved = SavedSearch(
            saved_id=f"sv_{uuid.uuid4().hex[:8]}",
            name=name,
            query_string=query_string,
            filters=filters or {},
            columns=columns or ["timestamp", "level", "message"],
            owner=owner
        )
        
        self.saved_searches[saved.saved_id] = saved
        return saved
        
    async def create_retention_policy(self, name: str,
                                      index_pattern: str,
                                      max_age_days: int = 30,
                                      action: RetentionAction = RetentionAction.DELETE,
                                      archive_path: str = "") -> RetentionPolicy:
        """Создание политики ретеншена"""
        policy = RetentionPolicy(
            policy_id=f"rp_{uuid.uuid4().hex[:8]}",
            name=name,
            index_pattern=index_pattern,
            max_age_days=max_age_days,
            action=action,
            archive_path=archive_path
        )
        
        self.retention_policies[policy.policy_id] = policy
        return policy
        
    async def execute_retention(self, policy_id: str) -> Optional[RetentionPolicy]:
        """Выполнение политики ретеншена"""
        policy = self.retention_policies.get(policy_id)
        if not policy or not policy.is_enabled:
            return None
            
        # Simulate retention execution
        cutoff_date = datetime.now() - timedelta(days=policy.max_age_days)
        
        logs_to_remove = [
            log_id for log_id, log in self.logs.items()
            if log.timestamp < cutoff_date
        ]
        
        bytes_freed = sum(len(self.logs[log_id].raw_message.encode('utf-8')) for log_id in logs_to_remove)
        
        for log_id in logs_to_remove:
            del self.logs[log_id]
            
        policy.last_executed = datetime.now()
        policy.indices_affected = 1
        policy.bytes_freed = bytes_freed
        
        return policy
        
    async def detect_patterns(self, min_occurrence: int = 10) -> List[LogPattern]:
        """Обнаружение паттернов"""
        # Simple pattern detection - group by message prefix
        pattern_counts = {}
        
        for log in self.logs.values():
            # Extract pattern (first 50 chars as simplified template)
            template = re.sub(r'\d+', '<NUM>', log.raw_message[:50])
            template = re.sub(r'[a-f0-9]{8,}', '<HEX>', template)
            
            if template not in pattern_counts:
                pattern_counts[template] = {
                    "count": 0,
                    "samples": []
                }
                
            pattern_counts[template]["count"] += 1
            if len(pattern_counts[template]["samples"]) < 3:
                pattern_counts[template]["samples"].append(log.raw_message[:200])
                
        total_logs = len(self.logs)
        patterns = []
        
        for template, data in pattern_counts.items():
            if data["count"] >= min_occurrence:
                pattern = LogPattern(
                    pattern_id=f"pat_{uuid.uuid4().hex[:8]}",
                    pattern_template=template,
                    pattern_type=PatternType.COMMON if data["count"] > total_logs * 0.1 else PatternType.RARE,
                    occurrence_count=data["count"],
                    percentage=(data["count"] / total_logs) * 100 if total_logs > 0 else 0,
                    sample_logs=data["samples"],
                    last_seen=datetime.now()
                )
                
                self.patterns[pattern.pattern_id] = pattern
                patterns.append(pattern)
                
        return sorted(patterns, key=lambda x: x.occurrence_count, reverse=True)
        
    async def detect_anomalies(self, field: str = "level",
                              window_minutes: int = 60) -> List[Anomaly]:
        """Обнаружение аномалий"""
        anomalies = []
        
        # Simple anomaly detection - count by level
        level_counts = {}
        for log in self.logs.values():
            level = log.level.value
            level_counts[level] = level_counts.get(level, 0) + 1
            
        # Check for error spike
        error_count = level_counts.get("error", 0) + level_counts.get("fatal", 0)
        total_count = sum(level_counts.values())
        
        if total_count > 0:
            error_rate = (error_count / total_count) * 100
            baseline = 5.0  # Expected 5% error rate
            
            if error_rate > baseline * 2:  # More than 2x baseline
                anomaly = Anomaly(
                    anomaly_id=f"anm_{uuid.uuid4().hex[:8]}",
                    description="Error rate spike detected",
                    anomaly_score=min((error_rate / baseline) * 10, 100),
                    anomaly_type="spike",
                    affected_field="error_rate",
                    baseline_value=baseline,
                    actual_value=error_rate,
                    severity="high" if error_rate > baseline * 5 else "medium"
                )
                
                self.anomalies[anomaly.anomaly_id] = anomaly
                anomalies.append(anomaly)
                
        return anomalies
        
    async def create_dashboard(self, name: str,
                              description: str = "",
                              widgets: List[Dict[str, Any]] = None,
                              time_range: str = "1h",
                              tags: List[str] = None) -> Dashboard:
        """Создание дашборда"""
        dashboard = Dashboard(
            dashboard_id=f"db_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            widgets=widgets or [],
            time_range=time_range,
            tags=tags or []
        )
        
        self.dashboards[dashboard.dashboard_id] = dashboard
        return dashboard
        
    async def create_alert(self, name: str,
                          query_string: str,
                          condition_type: str,
                          threshold: float,
                          time_window: str = "5m",
                          severity: str = "warning",
                          actions: List[Dict[str, Any]] = None) -> Alert:
        """Создание алерта"""
        alert = Alert(
            alert_id=f"alt_{uuid.uuid4().hex[:8]}",
            name=name,
            query_string=query_string,
            condition_type=condition_type,
            threshold=threshold,
            time_window=time_window,
            severity=severity,
            actions=actions or []
        )
        
        self.alerts[alert.alert_id] = alert
        return alert
        
    async def evaluate_alerts(self) -> List[Alert]:
        """Оценка алертов"""
        triggered = []
        
        for alert in self.alerts.values():
            if not alert.is_enabled:
                continue
                
            # Simulate alert evaluation
            result = await self.search(alert.query_string, size=1000)
            
            should_trigger = False
            if alert.condition_type == "count" and result.total_hits > alert.threshold:
                should_trigger = True
            elif alert.condition_type == "threshold" and random.random() < 0.2:
                should_trigger = True
                
            if should_trigger:
                alert.is_triggered = True
                alert.last_triggered = datetime.now()
                triggered.append(alert)
                
        return triggered
        
    async def collect_metrics(self) -> LogAnalyticsMetrics:
        """Сбор метрик платформы"""
        active_sources = sum(1 for s in self.sources.values() if s.is_active)
        
        total_bytes = sum(len(log.raw_message.encode('utf-8')) for log in self.logs.values())
        total_index_size = sum(idx.size_bytes for idx in self.indices.values())
        
        return LogAnalyticsMetrics(
            metrics_id=f"lam_{uuid.uuid4().hex[:8]}",
            total_sources=len(self.sources),
            active_sources=active_sources,
            total_logs=len(self.logs),
            logs_per_second=random.uniform(100, 10000),
            bytes_per_second=random.uniform(10000, 1000000),
            total_indices=len(self.indices),
            total_index_size_gb=total_index_size / (1024**3),
            total_searches=len(self.queries),
            avg_search_latency_ms=sum(q.duration_ms for q in self.queries.values()) / len(self.queries) if self.queries else 0.0,
            total_patterns=len(self.patterns),
            anomalies_detected=len(self.anomalies)
        )
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        active_sources = sum(1 for s in self.sources.values() if s.is_active)
        
        logs_by_level = {}
        for level in LogLevel:
            logs_by_level[level.value] = sum(1 for l in self.logs.values() if l.level == level)
            
        triggered_alerts = sum(1 for a in self.alerts.values() if a.is_triggered)
        
        return {
            "total_sources": len(self.sources),
            "active_sources": active_sources,
            "total_parsers": len(self.parsers),
            "total_logs": len(self.logs),
            "logs_by_level": logs_by_level,
            "total_indices": len(self.indices),
            "total_searches": len(self.queries),
            "saved_searches": len(self.saved_searches),
            "retention_policies": len(self.retention_policies),
            "total_patterns": len(self.patterns),
            "total_anomalies": len(self.anomalies),
            "total_dashboards": len(self.dashboards),
            "total_alerts": len(self.alerts),
            "triggered_alerts": triggered_alerts
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 358: Log Analytics Platform")
    print("=" * 60)
    
    platform = LogAnalyticsPlatform(platform_name="enterprise-logs")
    print("✓ Log Analytics Platform initialized")
    
    # Create Log Sources
    print("\n📡 Creating Log Sources...")
    
    sources_data = [
        ("api-gateway-logs", "fluentd", LogFormat.JSON, {"team": "platform", "env": "production"}),
        ("auth-service-logs", "filebeat", LogFormat.JSON, {"team": "security", "env": "production"}),
        ("order-service-logs", "fluentd", LogFormat.JSON, {"team": "orders", "env": "production"}),
        ("payment-service-logs", "logstash", LogFormat.JSON, {"team": "payments", "env": "production"}),
        ("nginx-access-logs", "filebeat", LogFormat.CLF, {"team": "platform", "type": "access"}),
        ("nginx-error-logs", "filebeat", LogFormat.PLAIN_TEXT, {"team": "platform", "type": "error"}),
        ("kubernetes-logs", "fluentd", LogFormat.JSON, {"team": "platform", "cluster": "production"}),
        ("database-logs", "logstash", LogFormat.SYSLOG, {"team": "dba", "type": "database"})
    ]
    
    sources = []
    for name, stype, fmt, tags in sources_data:
        src = await platform.create_log_source(name, stype, fmt, tags)
        sources.append(src)
        print(f"  📡 {name} ({stype}, {fmt.value})")
        
    # Create Parsers
    print("\n🔧 Creating Log Parsers...")
    
    parsers_data = [
        ("json-parser", LogFormat.JSON, "", "@timestamp", "message", "level"),
        ("clf-parser", LogFormat.CLF, '%{COMMONAPACHELOG}', "timestamp", "request", "response"),
        ("syslog-parser", LogFormat.SYSLOG, '%{SYSLOGBASE}', "timestamp", "message", "severity")
    ]
    
    for name, fmt, grok, ts, msg, lvl in parsers_data:
        await platform.create_parser(name, fmt, grok, ts, msg, lvl)
        print(f"  🔧 {name} ({fmt.value})")
        
    # Create Indices
    print("\n📊 Creating Indices...")
    
    indices_data = [
        ("logs-production", "logs-production-*"),
        ("logs-staging", "logs-staging-*"),
        ("logs-nginx", "logs-nginx-*"),
        ("logs-kubernetes", "logs-kubernetes-*")
    ]
    
    for name, pattern in indices_data:
        idx = await platform.create_index(name, pattern)
        print(f"  📊 {name} ({pattern})")
        
    # Ingest Logs
    print("\n📥 Ingesting Logs...")
    
    log_templates = [
        (LogLevel.INFO, "Request received: GET /api/users/{user_id}", "api-gateway", "api-gateway-001"),
        (LogLevel.INFO, "User authenticated successfully", "auth-service", "auth-001"),
        (LogLevel.DEBUG, "Cache hit for session {session_id}", "auth-service", "auth-001"),
        (LogLevel.INFO, "Order created: order_id={order_id}", "order-service", "order-001"),
        (LogLevel.INFO, "Payment processed: amount=${amount}", "payment-service", "payment-001"),
        (LogLevel.WARN, "High latency detected: {latency}ms", "api-gateway", "api-gateway-002"),
        (LogLevel.ERROR, "Database connection timeout", "order-service", "order-002"),
        (LogLevel.ERROR, "Payment declined: insufficient funds", "payment-service", "payment-001"),
        (LogLevel.FATAL, "Service crashed: OutOfMemoryError", "order-service", "order-003"),
        (LogLevel.INFO, "Health check passed", "api-gateway", "api-gateway-001"),
        (LogLevel.DEBUG, "Processing request: {request_id}", "api-gateway", "api-gateway-001"),
        (LogLevel.INFO, "Database query executed in {time}ms", "order-service", "order-001")
    ]
    
    for _ in range(200):
        level, template, service, host = random.choice(log_templates)
        source = next((s for s in sources if service in s.name), sources[0])
        
        message = template.format(
            user_id=random.randint(1, 1000),
            session_id=uuid.uuid4().hex[:8],
            order_id=random.randint(10000, 99999),
            amount=random.randint(10, 1000),
            latency=random.randint(100, 5000),
            request_id=uuid.uuid4().hex[:12],
            time=random.randint(1, 100)
        )
        
        await platform.ingest_log(
            source_id=source.source_id,
            raw_message=message,
            level=level,
            host=host,
            service=service,
            environment="production",
            trace_id=uuid.uuid4().hex if random.random() < 0.5 else None,
            fields={"request_id": uuid.uuid4().hex[:8], "user_id": random.randint(1, 100)}
        )
        
    print(f"  📥 Ingested {len(platform.logs)} log entries")
    
    # Search Logs
    print("\n🔍 Searching Logs...")
    
    searches = [
        ("error", [LogLevel.ERROR, LogLevel.FATAL]),
        ("payment", []),
        ("timeout", [LogLevel.ERROR]),
        ("order", [LogLevel.INFO])
    ]
    
    for query, levels in searches:
        result = await platform.search(query, levels=levels if levels else None, size=50)
        print(f"  🔍 '{query}': {result.total_hits} hits")
        
    # Aggregate Logs
    print("\n📊 Aggregating Logs...")
    
    level_agg = await platform.aggregate(AggregationType.COUNT, "level")
    print(f"  📊 By Level: {len(level_agg.buckets)} buckets")
    
    for bucket in level_agg.buckets[:5]:
        print(f"      - {bucket['key']}: {bucket['doc_count']}")
        
    # Save Searches
    print("\n💾 Saving Searches...")
    
    saved_data = [
        ("Error Logs", "level:error OR level:fatal", {"level": ["error", "fatal"]}),
        ("Payment Errors", "payment AND error", {"service": "payment-service"}),
        ("High Latency", "latency AND warn", {"level": "warn"})
    ]
    
    for name, query, filters in saved_data:
        await platform.save_search(name, query, filters, owner="admin")
        print(f"  💾 {name}")
        
    # Retention Policies
    print("\n📋 Creating Retention Policies...")
    
    retention_data = [
        ("production-30d", "logs-production-*", 30, RetentionAction.DELETE),
        ("staging-7d", "logs-staging-*", 7, RetentionAction.DELETE),
        ("archive-90d", "logs-*", 90, RetentionAction.ARCHIVE)
    ]
    
    for name, pattern, days, action in retention_data:
        await platform.create_retention_policy(name, pattern, days, action)
        print(f"  📋 {name}: {days} days ({action.value})")
        
    # Detect Patterns
    print("\n🔮 Detecting Patterns...")
    
    patterns = await platform.detect_patterns(min_occurrence=3)
    print(f"  🔮 Detected {len(patterns)} patterns")
    
    for p in patterns[:5]:
        print(f"      - {p.pattern_template[:50]}... ({p.occurrence_count} occurrences)")
        
    # Detect Anomalies
    print("\n⚠️ Detecting Anomalies...")
    
    anomalies = await platform.detect_anomalies()
    print(f"  ⚠️ Detected {len(anomalies)} anomalies")
    
    for a in anomalies:
        print(f"      - {a.description} (score: {a.anomaly_score:.1f})")
        
    # Create Dashboards
    print("\n📈 Creating Dashboards...")
    
    dashboards_data = [
        ("Log Overview", "Main log analytics dashboard", ["overview"]),
        ("Error Analysis", "Error log analysis", ["errors"]),
        ("Service Logs", "Service-level log views", ["services"]),
        ("Security Logs", "Security-related logs", ["security"])
    ]
    
    for name, desc, tags in dashboards_data:
        widgets = [
            {"type": "log_histogram", "query": "*"},
            {"type": "level_breakdown", "field": "level"},
            {"type": "top_services", "field": "service"},
            {"type": "log_stream", "query": "*"}
        ]
        await platform.create_dashboard(name, desc, widgets, "1h", tags)
        print(f"  📈 {name}")
        
    # Create Alerts
    print("\n🚨 Creating Alerts...")
    
    alerts_data = [
        ("High Error Rate", "level:error", "count", 100, "5m", "critical"),
        ("Fatal Errors", "level:fatal", "count", 1, "1m", "critical"),
        ("Payment Errors", "payment AND error", "count", 10, "5m", "warning"),
        ("Timeout Spike", "timeout", "count", 50, "5m", "warning")
    ]
    
    for name, query, cond_type, threshold, window, severity in alerts_data:
        await platform.create_alert(name, query, cond_type, threshold, window, severity)
        print(f"  🚨 {name} ({severity})")
        
    # Evaluate Alerts
    triggered = await platform.evaluate_alerts()
    print(f"\n  ⚡ {len(triggered)} alerts triggered")
    
    # Collect Metrics
    metrics = await platform.collect_metrics()
    
    # Log Sources Dashboard
    print("\n📡 Log Sources:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Source Name                 │ Type      │ Format       │ Events     │ Size (KB)  │ Status                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for src in sources:
        name = src.name[:27].ljust(27)
        stype = src.source_type[:9].ljust(9)
        fmt = src.log_format.value[:12].ljust(12)
        events = f"{src.events_received:,}".ljust(10)
        size = f"{src.bytes_received / 1024:.1f}".ljust(10)
        status = ("✅ Active" if src.is_active else "❌ Inactive").ljust(224)
        
        print(f"  │ {name} │ {stype} │ {fmt} │ {events} │ {size} │ {status} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Log Level Distribution
    stats = platform.get_statistics()
    
    print("\n📊 Log Level Distribution:")
    
    for level, count in stats["logs_by_level"].items():
        percentage = (count / stats["total_logs"]) * 100 if stats["total_logs"] > 0 else 0
        bar = "█" * int(percentage / 2)
        print(f"  {level.upper():8s} │ {bar.ljust(50)} │ {count:>6} ({percentage:.1f}%)")
        
    # Statistics
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Sources: {stats['active_sources']}/{stats['total_sources']} active")
    print(f"  Parsers: {stats['total_parsers']}")
    print(f"  Total Logs: {stats['total_logs']:,}")
    print(f"  Indices: {stats['total_indices']}")
    print(f"  Searches: {stats['total_searches']}")
    print(f"  Saved Searches: {stats['saved_searches']}")
    print(f"  Patterns: {stats['total_patterns']}")
    print(f"  Anomalies: {stats['total_anomalies']}")
    print(f"  Alerts: {stats['triggered_alerts']}/{stats['total_alerts']} triggered")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                       Log Analytics Platform                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Log Sources:             {stats['total_sources']:>12}                      │")
    print(f"│ Active Sources:                {stats['active_sources']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Logs:                    {stats['total_logs']:>12}                      │")
    print(f"│ Logs/Second:                   {metrics.logs_per_second:>12.0f}                      │")
    print(f"│ Bytes/Second:                  {metrics.bytes_per_second:>12.0f}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Indices:                 {stats['total_indices']:>12}                      │")
    print(f"│ Total Searches:                {stats['total_searches']:>12}                      │")
    print(f"│ Avg Search Latency (ms):       {metrics.avg_search_latency_ms:>12.2f}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Patterns Detected:             {stats['total_patterns']:>12}                      │")
    print(f"│ Anomalies Detected:            {stats['total_anomalies']:>12}                      │")
    print(f"│ Triggered Alerts:              {stats['triggered_alerts']:>12}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Log Analytics Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
