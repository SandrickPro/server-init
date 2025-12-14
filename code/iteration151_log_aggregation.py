#!/usr/bin/env python3
"""
Server Init - Iteration 151: Log Aggregation Platform
Платформа агрегации логов

Функционал:
- Log Collection - сбор логов
- Log Parsing - парсинг логов
- Log Storage - хранение логов
- Search & Query - поиск и запросы
- Log Analysis - анализ логов
- Alerting - алертинг
- Log Retention - ретенция логов
- Dashboard & Visualization - дашборды и визуализация
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid
import re
import random


class LogLevel(Enum):
    """Уровень логирования"""
    TRACE = 0
    DEBUG = 10
    INFO = 20
    WARN = 30
    ERROR = 40
    FATAL = 50


class LogSource(Enum):
    """Источник логов"""
    APPLICATION = "application"
    SYSTEM = "system"
    ACCESS = "access"
    SECURITY = "security"
    AUDIT = "audit"


class ParserType(Enum):
    """Тип парсера"""
    JSON = "json"
    REGEX = "regex"
    GROK = "grok"
    CSV = "csv"
    SYSLOG = "syslog"


class StorageType(Enum):
    """Тип хранилища"""
    ELASTICSEARCH = "elasticsearch"
    OPENSEARCH = "opensearch"
    LOKI = "loki"
    SPLUNK = "splunk"
    S3 = "s3"


class AlertSeverity(Enum):
    """Серьёзность алерта"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class LogEntry:
    """Запись лога"""
    log_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Content
    message: str = ""
    level: LogLevel = LogLevel.INFO
    
    # Source
    source: LogSource = LogSource.APPLICATION
    service: str = ""
    host: str = ""
    
    # Context
    trace_id: str = ""
    span_id: str = ""
    user_id: str = ""
    
    # Metadata
    labels: Dict[str, str] = field(default_factory=dict)
    fields: Dict[str, Any] = field(default_factory=dict)
    
    # Raw
    raw_message: str = ""


@dataclass
class LogStream:
    """Поток логов"""
    stream_id: str
    name: str = ""
    
    # Source
    source_type: str = ""  # file, tcp, udp, kafka, etc.
    source_config: Dict = field(default_factory=dict)
    
    # Parser
    parser_type: ParserType = ParserType.JSON
    parser_config: Dict = field(default_factory=dict)
    
    # Filters
    filters: List[Dict] = field(default_factory=list)
    
    # Status
    active: bool = True
    logs_received: int = 0


@dataclass
class LogIndex:
    """Индекс логов"""
    index_id: str
    name: str = ""
    
    # Settings
    retention_days: int = 30
    shards: int = 1
    replicas: int = 1
    
    # Mappings
    field_mappings: Dict[str, str] = field(default_factory=dict)
    
    # Stats
    document_count: int = 0
    size_bytes: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SearchQuery:
    """Поисковый запрос"""
    query_id: str
    
    # Query
    query_string: str = ""
    filters: List[Dict] = field(default_factory=list)
    
    # Time range
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # Pagination
    offset: int = 0
    limit: int = 100
    
    # Sorting
    sort_field: str = "timestamp"
    sort_order: str = "desc"
    
    # Aggregations
    aggregations: List[Dict] = field(default_factory=list)


@dataclass
class SearchResult:
    """Результат поиска"""
    result_id: str
    query_id: str = ""
    
    # Results
    total_hits: int = 0
    logs: List[LogEntry] = field(default_factory=list)
    
    # Aggregations
    aggregation_results: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    took_ms: float = 0.0
    
    # Timestamp
    executed_at: datetime = field(default_factory=datetime.now)


@dataclass
class LogAlert:
    """Алерт на логи"""
    alert_id: str
    name: str = ""
    
    # Condition
    query: str = ""
    threshold: int = 10
    time_window_minutes: int = 5
    
    # Severity
    severity: AlertSeverity = AlertSeverity.WARNING
    
    # Actions
    notification_channels: List[str] = field(default_factory=list)
    
    # Status
    enabled: bool = True
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0


@dataclass
class LogDashboard:
    """Дашборд логов"""
    dashboard_id: str
    name: str = ""
    
    # Panels
    panels: List[Dict] = field(default_factory=list)
    
    # Filters
    default_filters: Dict = field(default_factory=dict)
    time_range: str = "1h"
    
    # Metadata
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RetentionPolicy:
    """Политика ретенции"""
    policy_id: str
    name: str = ""
    
    # Conditions
    index_pattern: str = ""
    retention_days: int = 30
    
    # Actions
    action: str = "delete"  # delete, archive, compress
    archive_location: str = ""
    
    # Schedule
    run_interval_hours: int = 24
    last_run: Optional[datetime] = None


class LogParser:
    """Парсер логов"""
    
    def __init__(self):
        self.parsers: Dict[ParserType, Callable] = {
            ParserType.JSON: self._parse_json,
            ParserType.REGEX: self._parse_regex,
            ParserType.SYSLOG: self._parse_syslog,
            ParserType.GROK: self._parse_grok
        }
        
    def parse(self, raw_message: str, parser_type: ParserType,
               config: Dict = None) -> LogEntry:
        """Парсинг сообщения"""
        parser = self.parsers.get(parser_type, self._parse_json)
        return parser(raw_message, config or {})
        
    def _parse_json(self, raw: str, config: Dict) -> LogEntry:
        """JSON парсинг"""
        try:
            data = json.loads(raw)
            
            return LogEntry(
                log_id=f"log_{uuid.uuid4().hex[:8]}",
                message=data.get("message", data.get("msg", raw)),
                level=self._parse_level(data.get("level", "info")),
                service=data.get("service", ""),
                host=data.get("host", ""),
                trace_id=data.get("trace_id", ""),
                fields=data,
                raw_message=raw
            )
        except:
            return LogEntry(
                log_id=f"log_{uuid.uuid4().hex[:8]}",
                message=raw,
                raw_message=raw
            )
            
    def _parse_regex(self, raw: str, config: Dict) -> LogEntry:
        """Regex парсинг"""
        pattern = config.get("pattern", r"(?P<message>.+)")
        
        match = re.match(pattern, raw)
        if match:
            data = match.groupdict()
            return LogEntry(
                log_id=f"log_{uuid.uuid4().hex[:8]}",
                message=data.get("message", raw),
                level=self._parse_level(data.get("level", "info")),
                fields=data,
                raw_message=raw
            )
            
        return LogEntry(
            log_id=f"log_{uuid.uuid4().hex[:8]}",
            message=raw,
            raw_message=raw
        )
        
    def _parse_syslog(self, raw: str, config: Dict) -> LogEntry:
        """Syslog парсинг"""
        # Simplified syslog parsing
        pattern = r"<(?P<pri>\d+)>(?P<timestamp>\w+ \d+ \d+:\d+:\d+) (?P<host>\S+) (?P<message>.+)"
        
        match = re.match(pattern, raw)
        if match:
            data = match.groupdict()
            return LogEntry(
                log_id=f"log_{uuid.uuid4().hex[:8]}",
                message=data.get("message", raw),
                host=data.get("host", ""),
                source=LogSource.SYSTEM,
                raw_message=raw
            )
            
        return LogEntry(
            log_id=f"log_{uuid.uuid4().hex[:8]}",
            message=raw,
            raw_message=raw
        )
        
    def _parse_grok(self, raw: str, config: Dict) -> LogEntry:
        """GROK парсинг (упрощённый)"""
        # Simplified - just use regex
        return self._parse_regex(raw, config)
        
    def _parse_level(self, level_str: str) -> LogLevel:
        """Парсинг уровня"""
        level_map = {
            "trace": LogLevel.TRACE,
            "debug": LogLevel.DEBUG,
            "info": LogLevel.INFO,
            "warn": LogLevel.WARN,
            "warning": LogLevel.WARN,
            "error": LogLevel.ERROR,
            "fatal": LogLevel.FATAL,
            "critical": LogLevel.FATAL
        }
        return level_map.get(level_str.lower(), LogLevel.INFO)


class LogStorage:
    """Хранилище логов"""
    
    def __init__(self):
        self.logs: List[LogEntry] = []
        self.indexes: Dict[str, LogIndex] = {}
        self.max_logs: int = 100000
        
    def create_index(self, name: str, **kwargs) -> LogIndex:
        """Создание индекса"""
        index = LogIndex(
            index_id=f"idx_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        self.indexes[index.index_id] = index
        return index
        
    def store(self, log: LogEntry, index_name: str = "default"):
        """Сохранение лога"""
        self.logs.append(log)
        
        # Update index stats
        for index in self.indexes.values():
            if index.name == index_name:
                index.document_count += 1
                index.size_bytes += len(log.raw_message or log.message)
                break
                
        # Trim if over limit
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]
            
    def search(self, query: SearchQuery) -> SearchResult:
        """Поиск логов"""
        start_time = datetime.now()
        
        # Filter logs
        results = self.logs.copy()
        
        # Time filter
        if query.start_time:
            results = [l for l in results if l.timestamp >= query.start_time]
        if query.end_time:
            results = [l for l in results if l.timestamp <= query.end_time]
            
        # Query string filter
        if query.query_string:
            query_lower = query.query_string.lower()
            results = [l for l in results if query_lower in l.message.lower()]
            
        # Apply additional filters
        for f in query.filters:
            field = f.get("field")
            value = f.get("value")
            if field == "level":
                results = [l for l in results if l.level.name.lower() == value.lower()]
            elif field == "service":
                results = [l for l in results if l.service == value]
                
        # Sort
        reverse = query.sort_order == "desc"
        if query.sort_field == "timestamp":
            results.sort(key=lambda l: l.timestamp, reverse=reverse)
        elif query.sort_field == "level":
            results.sort(key=lambda l: l.level.value, reverse=reverse)
            
        total = len(results)
        
        # Paginate
        results = results[query.offset:query.offset + query.limit]
        
        # Aggregations
        agg_results = {}
        if query.aggregations:
            for agg in query.aggregations:
                if agg.get("type") == "terms":
                    field = agg.get("field")
                    counts = {}
                    for log in self.logs:
                        val = getattr(log, field, None)
                        if val:
                            key = val.name if hasattr(val, 'name') else str(val)
                            counts[key] = counts.get(key, 0) + 1
                    agg_results[agg.get("name", field)] = counts
                    
        end_time = datetime.now()
        
        return SearchResult(
            result_id=f"res_{uuid.uuid4().hex[:8]}",
            query_id=query.query_id,
            total_hits=total,
            logs=results,
            aggregation_results=agg_results,
            took_ms=(end_time - start_time).total_seconds() * 1000
        )


class LogCollector:
    """Сборщик логов"""
    
    def __init__(self, parser: LogParser, storage: LogStorage):
        self.parser = parser
        self.storage = storage
        self.streams: Dict[str, LogStream] = {}
        
    def create_stream(self, name: str, source_type: str,
                       parser_type: ParserType = ParserType.JSON,
                       **kwargs) -> LogStream:
        """Создание потока"""
        stream = LogStream(
            stream_id=f"stream_{uuid.uuid4().hex[:8]}",
            name=name,
            source_type=source_type,
            parser_type=parser_type,
            **kwargs
        )
        self.streams[stream.stream_id] = stream
        return stream
        
    async def collect(self, stream_id: str, raw_message: str):
        """Сбор лога"""
        stream = self.streams.get(stream_id)
        if not stream or not stream.active:
            return
            
        log = self.parser.parse(
            raw_message,
            stream.parser_type,
            stream.parser_config
        )
        
        # Apply filters
        for f in stream.filters:
            if not self._apply_filter(log, f):
                return
                
        stream.logs_received += 1
        self.storage.store(log, stream.name)
        
    def _apply_filter(self, log: LogEntry, filter_config: Dict) -> bool:
        """Применение фильтра"""
        action = filter_config.get("action", "include")
        field = filter_config.get("field")
        pattern = filter_config.get("pattern", "")
        
        value = getattr(log, field, "")
        if hasattr(value, 'name'):
            value = value.name
            
        matches = pattern.lower() in str(value).lower()
        
        if action == "include":
            return matches
        elif action == "exclude":
            return not matches
            
        return True


class AlertManager:
    """Менеджер алертов"""
    
    def __init__(self, storage: LogStorage):
        self.storage = storage
        self.alerts: Dict[str, LogAlert] = {}
        
    def create_alert(self, name: str, query: str, threshold: int,
                      **kwargs) -> LogAlert:
        """Создание алерта"""
        alert = LogAlert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            name=name,
            query=query,
            threshold=threshold,
            **kwargs
        )
        self.alerts[alert.alert_id] = alert
        return alert
        
    async def check_alerts(self) -> List[Dict]:
        """Проверка алертов"""
        triggered = []
        
        for alert in self.alerts.values():
            if not alert.enabled:
                continue
                
            # Create search query
            query = SearchQuery(
                query_id=f"q_{uuid.uuid4().hex[:8]}",
                query_string=alert.query,
                start_time=datetime.now() - timedelta(minutes=alert.time_window_minutes),
                end_time=datetime.now()
            )
            
            result = self.storage.search(query)
            
            if result.total_hits >= alert.threshold:
                alert.last_triggered = datetime.now()
                alert.trigger_count += 1
                
                triggered.append({
                    "alert": alert,
                    "count": result.total_hits,
                    "threshold": alert.threshold,
                    "triggered_at": alert.last_triggered
                })
                
        return triggered


class RetentionManager:
    """Менеджер ретенции"""
    
    def __init__(self, storage: LogStorage):
        self.storage = storage
        self.policies: Dict[str, RetentionPolicy] = {}
        
    def create_policy(self, name: str, retention_days: int,
                       **kwargs) -> RetentionPolicy:
        """Создание политики"""
        policy = RetentionPolicy(
            policy_id=f"ret_{uuid.uuid4().hex[:8]}",
            name=name,
            retention_days=retention_days,
            **kwargs
        )
        self.policies[policy.policy_id] = policy
        return policy
        
    async def apply_retention(self) -> Dict:
        """Применение ретенции"""
        stats = {
            "deleted": 0,
            "archived": 0,
            "policies_applied": 0
        }
        
        for policy in self.policies.values():
            cutoff = datetime.now() - timedelta(days=policy.retention_days)
            
            original_count = len(self.storage.logs)
            
            if policy.action == "delete":
                self.storage.logs = [
                    l for l in self.storage.logs
                    if l.timestamp > cutoff
                ]
                stats["deleted"] += original_count - len(self.storage.logs)
                
            policy.last_run = datetime.now()
            stats["policies_applied"] += 1
            
        return stats


class DashboardManager:
    """Менеджер дашбордов"""
    
    def __init__(self):
        self.dashboards: Dict[str, LogDashboard] = {}
        
    def create_dashboard(self, name: str, panels: List[Dict],
                          **kwargs) -> LogDashboard:
        """Создание дашборда"""
        dashboard = LogDashboard(
            dashboard_id=f"dash_{uuid.uuid4().hex[:8]}",
            name=name,
            panels=panels,
            **kwargs
        )
        self.dashboards[dashboard.dashboard_id] = dashboard
        return dashboard


class LogAggregationPlatform:
    """Платформа агрегации логов"""
    
    def __init__(self):
        self.parser = LogParser()
        self.storage = LogStorage()
        self.collector = LogCollector(self.parser, self.storage)
        self.alert_manager = AlertManager(self.storage)
        self.retention_manager = RetentionManager(self.storage)
        self.dashboard_manager = DashboardManager()
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        level_counts = {}
        for log in self.storage.logs:
            level = log.level.name
            level_counts[level] = level_counts.get(level, 0) + 1
            
        return {
            "total_logs": len(self.storage.logs),
            "total_streams": len(self.collector.streams),
            "total_indexes": len(self.storage.indexes),
            "total_alerts": len(self.alert_manager.alerts),
            "total_policies": len(self.retention_manager.policies),
            "total_dashboards": len(self.dashboard_manager.dashboards),
            "logs_by_level": level_counts
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 151: Log Aggregation Platform")
    print("=" * 60)
    
    async def demo():
        platform = LogAggregationPlatform()
        print("✓ Log Aggregation Platform created")
        
        # Create indexes
        print("\n📂 Creating Indexes...")
        
        indexes_data = [
            ("application-logs", 30, 3, 1),
            ("security-logs", 90, 1, 2),
            ("access-logs", 14, 5, 1),
            ("audit-logs", 365, 1, 2)
        ]
        
        for name, retention, shards, replicas in indexes_data:
            index = platform.storage.create_index(
                name,
                retention_days=retention,
                shards=shards,
                replicas=replicas
            )
            print(f"  ✓ {name}: {retention} days retention")
            
        # Create log streams
        print("\n📡 Creating Log Streams...")
        
        streams_data = [
            ("app-stream", "kafka", ParserType.JSON),
            ("nginx-stream", "file", ParserType.REGEX),
            ("syslog-stream", "udp", ParserType.SYSLOG)
        ]
        
        for name, source, parser in streams_data:
            stream = platform.collector.create_stream(name, source, parser)
            print(f"  ✓ {name}: {source} → {parser.value}")
            
        # Simulate log ingestion
        print("\n📥 Ingesting Logs...")
        
        services = ["api-gateway", "user-service", "order-service", "payment-service"]
        levels = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARN, LogLevel.ERROR]
        level_weights = [10, 60, 20, 10]
        
        messages = [
            "Request processed successfully",
            "User authentication completed",
            "Database query executed",
            "Cache hit for key",
            "Connection pool exhausted",
            "Rate limit exceeded",
            "Invalid request format",
            "External API timeout",
            "Memory usage warning",
            "Disk space low"
        ]
        
        stream_ids = list(platform.collector.streams.keys())
        
        for i in range(1000):
            level = random.choices(levels, weights=level_weights)[0]
            service = random.choice(services)
            message = random.choice(messages)
            
            log_data = json.dumps({
                "timestamp": datetime.now().isoformat(),
                "level": level.name.lower(),
                "message": f"{message} (id={i})",
                "service": service,
                "host": f"host-{random.randint(1, 10)}",
                "trace_id": f"trace_{uuid.uuid4().hex[:16]}",
                "duration_ms": random.randint(1, 1000)
            })
            
            await platform.collector.collect(stream_ids[0], log_data)
            
        print(f"  ✓ Ingested 1000 log entries")
        
        # Show stream stats
        print("\n📊 Stream Statistics:")
        
        for stream in platform.collector.streams.values():
            print(f"  {stream.name}: {stream.logs_received:,} logs received")
            
        # Create alerts
        print("\n🔔 Creating Alerts...")
        
        alerts_data = [
            ("High Error Rate", "error", 50, 5, AlertSeverity.CRITICAL),
            ("Warning Spike", "warning", 100, 10, AlertSeverity.WARNING),
            ("Auth Failures", "authentication failed", 10, 5, AlertSeverity.CRITICAL)
        ]
        
        for name, query, threshold, window, severity in alerts_data:
            alert = platform.alert_manager.create_alert(
                name, query, threshold,
                time_window_minutes=window,
                severity=severity,
                notification_channels=["slack", "email"]
            )
            print(f"  ✓ {name}: threshold={threshold}, window={window}min")
            
        # Check alerts
        print("\n⚠️ Checking Alerts...")
        
        triggered = await platform.alert_manager.check_alerts()
        
        if triggered:
            for t in triggered:
                print(f"  🚨 {t['alert'].name}: {t['count']} matches (threshold: {t['threshold']})")
        else:
            print("  ✓ No alerts triggered")
            
        # Create retention policies
        print("\n🗑️ Creating Retention Policies...")
        
        policy = platform.retention_manager.create_policy(
            "default-retention",
            retention_days=30,
            action="delete"
        )
        print(f"  ✓ {policy.name}: {policy.retention_days} days")
        
        # Search logs
        print("\n🔍 Searching Logs...")
        
        # Search by level
        query = SearchQuery(
            query_id=f"q_{uuid.uuid4().hex[:8]}",
            filters=[{"field": "level", "value": "error"}],
            limit=10
        )
        
        result = platform.storage.search(query)
        print(f"\n  Error logs: {result.total_hits} found ({result.took_ms:.2f}ms)")
        
        # Search by query string
        query = SearchQuery(
            query_id=f"q_{uuid.uuid4().hex[:8]}",
            query_string="timeout",
            limit=10
        )
        
        result = platform.storage.search(query)
        print(f"  'timeout' logs: {result.total_hits} found ({result.took_ms:.2f}ms)")
        
        # Aggregation
        query = SearchQuery(
            query_id=f"q_{uuid.uuid4().hex[:8]}",
            aggregations=[
                {"name": "level_counts", "type": "terms", "field": "level"},
                {"name": "service_counts", "type": "terms", "field": "service"}
            ]
        )
        
        result = platform.storage.search(query)
        
        print("\n📊 Log Distribution by Level:")
        if "level_counts" in result.aggregation_results:
            for level, count in sorted(result.aggregation_results["level_counts"].items()):
                bar = "█" * (count // 20)
                print(f"    {level:8}: {count:5} {bar}")
                
        print("\n📊 Log Distribution by Service:")
        if "service_counts" in result.aggregation_results:
            for service, count in sorted(result.aggregation_results["service_counts"].items()):
                bar = "█" * (count // 20)
                print(f"    {service:15}: {count:5} {bar}")
                
        # Create dashboard
        print("\n📋 Creating Dashboard...")
        
        dashboard = platform.dashboard_manager.create_dashboard(
            "Main Dashboard",
            panels=[
                {"type": "log_stream", "query": "*", "title": "Live Logs"},
                {"type": "pie_chart", "field": "level", "title": "Logs by Level"},
                {"type": "line_chart", "field": "timestamp", "title": "Log Volume"},
                {"type": "table", "query": "level:error", "title": "Recent Errors"}
            ],
            time_range="1h",
            created_by="admin@company.com"
        )
        print(f"  ✓ {dashboard.name}: {len(dashboard.panels)} panels")
        
        # Recent logs sample
        print("\n📜 Recent Logs (last 5):")
        
        query = SearchQuery(
            query_id=f"q_{uuid.uuid4().hex[:8]}",
            limit=5,
            sort_order="desc"
        )
        
        result = platform.storage.search(query)
        
        for log in result.logs:
            level_icon = {
                LogLevel.INFO: "ℹ️",
                LogLevel.WARN: "⚠️",
                LogLevel.ERROR: "❌",
                LogLevel.DEBUG: "🔍",
                LogLevel.FATAL: "💀"
            }
            icon = level_icon.get(log.level, "📝")
            time_str = log.timestamp.strftime("%H:%M:%S")
            msg = log.message[:50] + "..." if len(log.message) > 50 else log.message
            print(f"  {icon} [{time_str}] {log.service}: {msg}")
            
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Logs: {stats['total_logs']:,}")
        print(f"  Streams: {stats['total_streams']}")
        print(f"  Indexes: {stats['total_indexes']}")
        print(f"  Alerts: {stats['total_alerts']}")
        print(f"  Retention Policies: {stats['total_policies']}")
        print(f"  Dashboards: {stats['total_dashboards']}")
        
        # Dashboard
        print("\n📋 Log Aggregation Dashboard:")
        print("  ┌────────────────────────────────────────────────────────────┐")
        print("  │                  Log Aggregation Overview                  │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Logs:            {stats['total_logs']:>10,}                    │")
        print(f"  │ Active Streams:        {stats['total_streams']:>10}                    │")
        print(f"  │ Indexes:               {stats['total_indexes']:>10}                    │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Alerts Configured:     {stats['total_alerts']:>10}                    │")
        print(f"  │ Retention Policies:    {stats['total_policies']:>10}                    │")
        print(f"  │ Dashboards:            {stats['total_dashboards']:>10}                    │")
        print("  └────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Log Aggregation Platform initialized!")
    print("=" * 60)
