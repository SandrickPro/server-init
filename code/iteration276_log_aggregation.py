#!/usr/bin/env python3
"""
Server Init - Iteration 276: Log Aggregation Platform
Платформа агрегации логов

Функционал:
- Log Collection - сбор логов
- Log Parsing - парсинг логов
- Log Indexing - индексация логов
- Log Search - поиск по логам
- Log Streaming - потоковая передача логов
- Log Retention - хранение логов
- Log Alerting - оповещения по логам
- Log Analytics - аналитика логов
"""

import asyncio
import random
import re
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Pattern
from enum import Enum
import uuid


class LogLevel(Enum):
    """Уровень логов"""
    TRACE = 0
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5


class LogFormat(Enum):
    """Формат логов"""
    JSON = "json"
    PLAINTEXT = "plaintext"
    SYSLOG = "syslog"
    APACHE = "apache"
    NGINX = "nginx"
    CUSTOM = "custom"


class LogSourceType(Enum):
    """Тип источника логов"""
    FILE = "file"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    SYSLOG = "syslog"
    HTTP = "http"
    TCP = "tcp"
    UDP = "udp"


class AlertCondition(Enum):
    """Условие оповещения"""
    CONTAINS = "contains"
    MATCHES_REGEX = "matches_regex"
    COUNT_EXCEEDS = "count_exceeds"
    RATE_EXCEEDS = "rate_exceeds"


@dataclass
class LogEntry:
    """Запись лога"""
    log_id: str
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Level
    level: LogLevel = LogLevel.INFO
    
    # Message
    message: str = ""
    raw_message: str = ""
    
    # Source
    source: str = ""
    host: str = ""
    
    # Application
    application: str = ""
    environment: str = ""
    
    # Context
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    
    # Extra fields
    fields: Dict[str, Any] = field(default_factory=dict)
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Indexed
    indexed: bool = False


@dataclass
class LogSource:
    """Источник логов"""
    source_id: str
    name: str
    
    # Type
    source_type: LogSourceType = LogSourceType.FILE
    
    # Path/URL
    path: str = ""
    
    # Format
    log_format: LogFormat = LogFormat.JSON
    
    # Parser
    parser_pattern: Optional[str] = None
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # State
    active: bool = True
    logs_collected: int = 0
    last_collection: Optional[datetime] = None


@dataclass
class LogParser:
    """Парсер логов"""
    parser_id: str
    name: str
    
    # Format
    log_format: LogFormat = LogFormat.JSON
    
    # Pattern
    pattern: Optional[str] = None
    compiled_pattern: Optional[Pattern] = None
    
    # Field mappings
    field_mappings: Dict[str, str] = field(default_factory=dict)
    
    # Timestamp format
    timestamp_format: str = "%Y-%m-%dT%H:%M:%S"


@dataclass
class LogIndex:
    """Индекс логов"""
    index_id: str
    name: str
    
    # Shards
    shards: int = 1
    replicas: int = 0
    
    # Retention
    retention_days: int = 30
    
    # Stats
    doc_count: int = 0
    size_bytes: int = 0
    
    # Created
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class LogStream:
    """Поток логов"""
    stream_id: str
    name: str
    
    # Filter
    filter_query: str = "*"
    level_filter: Optional[LogLevel] = None
    
    # Sources
    source_filters: List[str] = field(default_factory=list)
    
    # Active subscribers
    subscribers: int = 0
    
    # State
    active: bool = True


@dataclass
class LogAlert:
    """Оповещение по логам"""
    alert_id: str
    name: str
    
    # Condition
    condition: AlertCondition = AlertCondition.CONTAINS
    condition_value: str = ""
    threshold: int = 1
    
    # Window
    window_minutes: int = 5
    
    # Actions
    notify_channels: List[str] = field(default_factory=list)
    
    # State
    active: bool = True
    triggered: bool = False
    trigger_count: int = 0
    last_triggered: Optional[datetime] = None


@dataclass
class LogQuery:
    """Запрос логов"""
    query_id: str
    
    # Query
    query_string: str = "*"
    
    # Filters
    level: Optional[LogLevel] = None
    source: Optional[str] = None
    application: Optional[str] = None
    
    # Time range
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # Pagination
    offset: int = 0
    limit: int = 100


@dataclass
class LogAnalytics:
    """Аналитика логов"""
    analytics_id: str
    name: str
    
    # Aggregation
    group_by: List[str] = field(default_factory=list)  # fields to group by
    
    # Metrics
    count: int = 0
    error_count: int = 0
    
    # Time series
    time_buckets: Dict[str, int] = field(default_factory=dict)


@dataclass
class RetentionPolicy:
    """Политика хранения"""
    policy_id: str
    name: str
    
    # Duration
    retention_days: int = 30
    
    # Actions
    delete_after_days: int = 90
    archive_after_days: int = 30
    
    # Filters
    level_filter: Optional[LogLevel] = None
    source_filter: Optional[str] = None
    
    # State
    active: bool = True


class LogAggregationManager:
    """Менеджер агрегации логов"""
    
    def __init__(self):
        self.logs: List[LogEntry] = []
        self.sources: Dict[str, LogSource] = {}
        self.parsers: Dict[str, LogParser] = {}
        self.indexes: Dict[str, LogIndex] = {}
        self.streams: Dict[str, LogStream] = {}
        self.alerts: Dict[str, LogAlert] = {}
        self.policies: Dict[str, RetentionPolicy] = {}
        
        # Initialize default parser
        self._init_default_parsers()
        
    def _init_default_parsers(self):
        """Инициализация парсеров по умолчанию"""
        # JSON parser
        self.parsers["json"] = LogParser(
            parser_id="parser_json",
            name="json",
            log_format=LogFormat.JSON
        )
        
        # Apache parser
        apache_pattern = r'^(?P<host>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] "(?P<method>\S+) (?P<path>\S+) (?P<protocol>[^"]*)" (?P<status>\d+) (?P<size>\d+)'
        self.parsers["apache"] = LogParser(
            parser_id="parser_apache",
            name="apache",
            log_format=LogFormat.APACHE,
            pattern=apache_pattern,
            compiled_pattern=re.compile(apache_pattern)
        )
        
    def add_source(self, name: str,
                  source_type: LogSourceType,
                  path: str,
                  log_format: LogFormat = LogFormat.JSON,
                  labels: Dict[str, str] = None) -> LogSource:
        """Добавление источника"""
        source = LogSource(
            source_id=f"source_{uuid.uuid4().hex[:8]}",
            name=name,
            source_type=source_type,
            path=path,
            log_format=log_format,
            labels=labels or {}
        )
        
        self.sources[name] = source
        return source
        
    def create_parser(self, name: str,
                     log_format: LogFormat,
                     pattern: str = None,
                     field_mappings: Dict[str, str] = None) -> LogParser:
        """Создание парсера"""
        parser = LogParser(
            parser_id=f"parser_{uuid.uuid4().hex[:8]}",
            name=name,
            log_format=log_format,
            pattern=pattern,
            field_mappings=field_mappings or {}
        )
        
        if pattern:
            parser.compiled_pattern = re.compile(pattern)
            
        self.parsers[name] = parser
        return parser
        
    def parse_log(self, raw_message: str,
                 parser_name: str = "json") -> Optional[LogEntry]:
        """Парсинг лога"""
        parser = self.parsers.get(parser_name)
        if not parser:
            return None
            
        entry = LogEntry(
            log_id=f"log_{uuid.uuid4().hex[:8]}",
            raw_message=raw_message
        )
        
        if parser.log_format == LogFormat.JSON:
            try:
                import json
                data = json.loads(raw_message)
                
                entry.message = data.get("message", data.get("msg", raw_message))
                entry.level = self._parse_level(data.get("level", "info"))
                entry.timestamp = self._parse_timestamp(data.get("timestamp", data.get("time")))
                entry.source = data.get("source", data.get("logger", ""))
                entry.application = data.get("application", data.get("app", ""))
                
                # Extract extra fields
                for key, value in data.items():
                    if key not in ["message", "msg", "level", "timestamp", "time", "source", "logger", "application", "app"]:
                        entry.fields[key] = value
                        
            except:
                entry.message = raw_message
                
        elif parser.compiled_pattern:
            match = parser.compiled_pattern.match(raw_message)
            if match:
                groups = match.groupdict()
                entry.message = groups.get("message", raw_message)
                entry.level = self._parse_level(groups.get("level", "info"))
                entry.timestamp = self._parse_timestamp(groups.get("timestamp"))
                entry.host = groups.get("host", "")
                entry.fields = {k: v for k, v in groups.items() if k not in ["message", "level", "timestamp", "host"]}
            else:
                entry.message = raw_message
        else:
            entry.message = raw_message
            
        return entry
        
    def _parse_level(self, level_str: str) -> LogLevel:
        """Парсинг уровня"""
        level_str = level_str.lower()
        level_map = {
            "trace": LogLevel.TRACE,
            "debug": LogLevel.DEBUG,
            "info": LogLevel.INFO,
            "warn": LogLevel.WARNING,
            "warning": LogLevel.WARNING,
            "error": LogLevel.ERROR,
            "err": LogLevel.ERROR,
            "critical": LogLevel.CRITICAL,
            "fatal": LogLevel.CRITICAL
        }
        return level_map.get(level_str, LogLevel.INFO)
        
    def _parse_timestamp(self, ts) -> datetime:
        """Парсинг timestamp"""
        if ts is None:
            return datetime.now()
        if isinstance(ts, datetime):
            return ts
        if isinstance(ts, (int, float)):
            return datetime.fromtimestamp(ts)
        try:
            return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        except:
            return datetime.now()
            
    def ingest_log(self, entry: LogEntry,
                  source_name: str = None) -> LogEntry:
        """Прием лога"""
        if source_name:
            entry.source = source_name
            if source_name in self.sources:
                source = self.sources[source_name]
                source.logs_collected += 1
                source.last_collection = datetime.now()
                
        self.logs.append(entry)
        
        # Check alerts
        self._check_alerts(entry)
        
        return entry
        
    def create_index(self, name: str,
                    shards: int = 1,
                    retention_days: int = 30) -> LogIndex:
        """Создание индекса"""
        index = LogIndex(
            index_id=f"index_{uuid.uuid4().hex[:8]}",
            name=name,
            shards=shards,
            retention_days=retention_days
        )
        
        self.indexes[name] = index
        return index
        
    def index_log(self, entry: LogEntry,
                 index_name: str) -> bool:
        """Индексация лога"""
        index = self.indexes.get(index_name)
        if not index:
            return False
            
        entry.indexed = True
        index.doc_count += 1
        index.size_bytes += len(entry.raw_message or entry.message)
        
        return True
        
    def search(self, query: LogQuery) -> List[LogEntry]:
        """Поиск логов"""
        results = []
        
        for entry in self.logs:
            if not self._matches_query(entry, query):
                continue
            results.append(entry)
            
        # Sort by timestamp desc
        results.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply pagination
        return results[query.offset:query.offset + query.limit]
        
    def _matches_query(self, entry: LogEntry, query: LogQuery) -> bool:
        """Проверка соответствия запросу"""
        # Query string
        if query.query_string and query.query_string != "*":
            if query.query_string.lower() not in entry.message.lower():
                return False
                
        # Level filter
        if query.level and entry.level.value < query.level.value:
            return False
            
        # Source filter
        if query.source and entry.source != query.source:
            return False
            
        # Application filter
        if query.application and entry.application != query.application:
            return False
            
        # Time range
        if query.start_time and entry.timestamp < query.start_time:
            return False
        if query.end_time and entry.timestamp > query.end_time:
            return False
            
        return True
        
    def create_stream(self, name: str,
                     filter_query: str = "*",
                     level_filter: LogLevel = None) -> LogStream:
        """Создание потока"""
        stream = LogStream(
            stream_id=f"stream_{uuid.uuid4().hex[:8]}",
            name=name,
            filter_query=filter_query,
            level_filter=level_filter
        )
        
        self.streams[name] = stream
        return stream
        
    def create_alert(self, name: str,
                    condition: AlertCondition,
                    condition_value: str,
                    threshold: int = 1,
                    notify_channels: List[str] = None) -> LogAlert:
        """Создание оповещения"""
        alert = LogAlert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            name=name,
            condition=condition,
            condition_value=condition_value,
            threshold=threshold,
            notify_channels=notify_channels or []
        )
        
        self.alerts[name] = alert
        return alert
        
    def _check_alerts(self, entry: LogEntry):
        """Проверка оповещений"""
        for alert in self.alerts.values():
            if not alert.active:
                continue
                
            triggered = False
            
            if alert.condition == AlertCondition.CONTAINS:
                if alert.condition_value.lower() in entry.message.lower():
                    triggered = True
                    
            elif alert.condition == AlertCondition.MATCHES_REGEX:
                try:
                    if re.search(alert.condition_value, entry.message):
                        triggered = True
                except:
                    pass
                    
            if triggered:
                alert.trigger_count += 1
                if alert.trigger_count >= alert.threshold:
                    alert.triggered = True
                    alert.last_triggered = datetime.now()
                    
    def set_retention_policy(self, name: str,
                            retention_days: int,
                            level_filter: LogLevel = None) -> RetentionPolicy:
        """Установка политики хранения"""
        policy = RetentionPolicy(
            policy_id=f"policy_{uuid.uuid4().hex[:8]}",
            name=name,
            retention_days=retention_days,
            level_filter=level_filter
        )
        
        self.policies[name] = policy
        return policy
        
    def apply_retention(self):
        """Применение политик хранения"""
        cutoff = datetime.now()
        deleted = 0
        
        for policy in self.policies.values():
            if not policy.active:
                continue
                
            policy_cutoff = cutoff - timedelta(days=policy.retention_days)
            
            new_logs = []
            for entry in self.logs:
                keep = True
                
                if entry.timestamp < policy_cutoff:
                    if policy.level_filter:
                        if entry.level.value <= policy.level_filter.value:
                            keep = False
                    else:
                        keep = False
                        
                if keep:
                    new_logs.append(entry)
                else:
                    deleted += 1
                    
            self.logs = new_logs
            
        return deleted
        
    def get_analytics(self, group_by: List[str] = None,
                     start_time: datetime = None,
                     end_time: datetime = None) -> LogAnalytics:
        """Получение аналитики"""
        analytics = LogAnalytics(
            analytics_id=f"analytics_{uuid.uuid4().hex[:8]}",
            name="log_analytics",
            group_by=group_by or []
        )
        
        for entry in self.logs:
            if start_time and entry.timestamp < start_time:
                continue
            if end_time and entry.timestamp > end_time:
                continue
                
            analytics.count += 1
            if entry.level.value >= LogLevel.ERROR.value:
                analytics.error_count += 1
                
            # Time bucket
            bucket = entry.timestamp.strftime("%Y-%m-%d %H:00")
            analytics.time_buckets[bucket] = analytics.time_buckets.get(bucket, 0) + 1
            
        return analytics
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        level_counts = {}
        for entry in self.logs:
            level_counts[entry.level.name] = level_counts.get(entry.level.name, 0) + 1
            
        return {
            "total_logs": len(self.logs),
            "sources": len(self.sources),
            "parsers": len(self.parsers),
            "indexes": len(self.indexes),
            "streams": len(self.streams),
            "alerts": len(self.alerts),
            "policies": len(self.policies),
            "level_distribution": level_counts
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 276: Log Aggregation Platform")
    print("=" * 60)
    
    manager = LogAggregationManager()
    print("✓ Log Aggregation Manager created")
    
    # Add sources
    print("\n📥 Adding Log Sources...")
    
    sources_config = [
        ("nginx-access", LogSourceType.FILE, "/var/log/nginx/access.log", LogFormat.NGINX),
        ("app-logs", LogSourceType.DOCKER, "container://app", LogFormat.JSON),
        ("kubernetes", LogSourceType.KUBERNETES, "namespace/default", LogFormat.JSON),
        ("syslog", LogSourceType.SYSLOG, "udp://0.0.0.0:514", LogFormat.SYSLOG),
    ]
    
    for name, stype, path, fmt in sources_config:
        source = manager.add_source(name, stype, path, fmt)
        print(f"  📥 {name}: {stype.value}")
        
    # Create indexes
    print("\n📇 Creating Indexes...")
    
    indexes_config = [
        ("logs-daily", 3, 7),
        ("logs-weekly", 1, 30),
        ("errors", 2, 90),
    ]
    
    for name, shards, retention in indexes_config:
        index = manager.create_index(name, shards, retention)
        print(f"  📇 {name}: {shards} shards, {retention}d retention")
        
    # Create streams
    print("\n🌊 Creating Log Streams...")
    
    error_stream = manager.create_stream("errors", "error OR exception", LogLevel.ERROR)
    print(f"  🌊 {error_stream.name}: level >= ERROR")
    
    auth_stream = manager.create_stream("authentication", "login OR logout OR auth")
    print(f"  🌊 {auth_stream.name}: auth events")
    
    # Create alerts
    print("\n🚨 Creating Alerts...")
    
    alerts_config = [
        ("high-error-rate", AlertCondition.MATCHES_REGEX, r"(error|exception|failed)", 10),
        ("security-alert", AlertCondition.CONTAINS, "unauthorized", 1),
        ("database-error", AlertCondition.CONTAINS, "database connection failed", 3),
    ]
    
    for name, condition, value, threshold in alerts_config:
        alert = manager.create_alert(name, condition, value, threshold, ["slack", "email"])
        print(f"  🚨 {name}: {condition.value} threshold={threshold}")
        
    # Set retention policies
    print("\n📋 Setting Retention Policies...")
    
    manager.set_retention_policy("debug-short", 7, LogLevel.DEBUG)
    manager.set_retention_policy("info-medium", 30, LogLevel.INFO)
    manager.set_retention_policy("error-long", 90, LogLevel.ERROR)
    print("  Policies: debug=7d, info=30d, error=90d")
    
    # Ingest logs
    print("\n📝 Ingesting Logs...")
    
    applications = ["api-gateway", "user-service", "order-service", "payment-service"]
    log_templates = [
        ('{"level": "info", "message": "Request received from %s", "application": "%s", "timestamp": "%s"}', LogLevel.INFO),
        ('{"level": "debug", "message": "Processing order %d", "application": "%s", "timestamp": "%s"}', LogLevel.DEBUG),
        ('{"level": "warning", "message": "High latency detected: %dms", "application": "%s", "timestamp": "%s"}', LogLevel.WARNING),
        ('{"level": "error", "message": "Database connection failed: %s", "application": "%s", "timestamp": "%s"}', LogLevel.ERROR),
        ('{"level": "info", "message": "User login successful: %s", "application": "%s", "timestamp": "%s"}', LogLevel.INFO),
        ('{"level": "error", "message": "Payment processing exception: %s", "application": "%s", "timestamp": "%s"}', LogLevel.ERROR),
        ('{"level": "critical", "message": "Service unavailable: unauthorized access", "application": "%s", "timestamp": "%s"}', LogLevel.CRITICAL),
    ]
    
    for i in range(50):
        template, level = random.choice(log_templates)
        app = random.choice(applications)
        ts = (datetime.now() - timedelta(minutes=random.randint(0, 60))).isoformat()
        
        if "%d" in template:
            raw = template % (random.randint(100, 9999), app, ts)
        elif template.count("%s") == 3:
            raw = template % (f"192.168.1.{random.randint(1, 254)}", app, ts)
        else:
            raw = template % (app, ts)
            
        entry = manager.parse_log(raw, "json")
        if entry:
            manager.ingest_log(entry, "app-logs")
            manager.index_log(entry, "logs-daily")
            
    print(f"  Ingested {len(manager.logs)} logs")
    
    # Search logs
    print("\n🔎 Searching Logs...")
    
    # Search errors
    query = LogQuery(
        query_id="q1",
        query_string="error",
        level=LogLevel.ERROR,
        limit=5
    )
    
    results = manager.search(query)
    print(f"\n  Error logs: {len(results)} results")
    
    for entry in results[:3]:
        level_icon = {
            LogLevel.DEBUG: "🔍",
            LogLevel.INFO: "ℹ️",
            LogLevel.WARNING: "⚠️",
            LogLevel.ERROR: "❌",
            LogLevel.CRITICAL: "🚨"
        }.get(entry.level, "❓")
        
        msg = entry.message[:50] + "..." if len(entry.message) > 50 else entry.message
        print(f"    {level_icon} [{entry.application}] {msg}")
        
    # Get analytics
    print("\n📊 Log Analytics...")
    
    analytics = manager.get_analytics()
    print(f"  Total logs: {analytics.count}")
    print(f"  Error logs: {analytics.error_count}")
    print(f"  Error rate: {analytics.error_count / analytics.count * 100:.1f}%")
    
    # Display level distribution
    print("\n📊 Level Distribution:")
    
    stats = manager.get_statistics()
    level_dist = stats["level_distribution"]
    
    total = sum(level_dist.values())
    for level, count in sorted(level_dist.items(), key=lambda x: LogLevel[x[0]].value):
        pct = count / total * 100
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"  {level:10s} [{bar}] {count:4d} ({pct:5.1f}%)")
        
    # Display time buckets
    print("\n📈 Log Volume by Hour:")
    
    sorted_buckets = sorted(analytics.time_buckets.items())
    if sorted_buckets:
        max_count = max(analytics.time_buckets.values())
        for bucket, count in sorted_buckets[-5:]:
            bar_len = int(count / max_count * 20)
            bar = "█" * bar_len
            print(f"  {bucket[-5:]}: {bar} {count}")
            
    # Display sources
    print("\n📥 Source Statistics:")
    
    print("\n  ┌────────────────────┬─────────────┬─────────────┬──────────────────────┐")
    print("  │ Source             │ Type        │ Logs        │ Last Collection      │")
    print("  ├────────────────────┼─────────────┼─────────────┼──────────────────────┤")
    
    for source in manager.sources.values():
        name = source.name[:18].ljust(18)
        stype = source.source_type.value[:11].ljust(11)
        logs = str(source.logs_collected)[:11].ljust(11)
        last = source.last_collection.strftime("%Y-%m-%d %H:%M") if source.last_collection else "Never"
        last = last[:20].ljust(20)
        
        print(f"  │ {name} │ {stype} │ {logs} │ {last} │")
        
    print("  └────────────────────┴─────────────┴─────────────┴──────────────────────┘")
    
    # Display indexes
    print("\n📇 Index Statistics:")
    
    print("\n  ┌────────────────────┬─────────┬─────────────┬─────────────┐")
    print("  │ Index              │ Shards  │ Documents   │ Size        │")
    print("  ├────────────────────┼─────────┼─────────────┼─────────────┤")
    
    for index in manager.indexes.values():
        name = index.name[:18].ljust(18)
        shards = str(index.shards)[:7].ljust(7)
        docs = str(index.doc_count)[:11].ljust(11)
        size = f"{index.size_bytes / 1024:.1f}KB"[:11].ljust(11)
        
        print(f"  │ {name} │ {shards} │ {docs} │ {size} │")
        
    print("  └────────────────────┴─────────┴─────────────┴─────────────┘")
    
    # Display alerts
    print("\n🚨 Alert Status:")
    
    for alert in manager.alerts.values():
        status = "🔥 FIRING" if alert.triggered else "✅ OK"
        print(f"  {alert.name}: {status} (triggers: {alert.trigger_count}/{alert.threshold})")
        
    # Display streams
    print("\n🌊 Stream Status:")
    
    for stream in manager.streams.values():
        status = "🟢 Active" if stream.active else "🔴 Inactive"
        level_str = f">= {stream.level_filter.name}" if stream.level_filter else "all"
        print(f"  {stream.name}: {status}, filter='{stream.filter_query[:20]}', level={level_str}")
        
    # Recent logs
    print("\n📝 Recent Logs:")
    
    recent_query = LogQuery(query_id="recent", limit=5)
    recent_logs = manager.search(recent_query)
    
    for entry in recent_logs:
        level_icon = {
            LogLevel.DEBUG: "🔍",
            LogLevel.INFO: "ℹ️",
            LogLevel.WARNING: "⚠️",
            LogLevel.ERROR: "❌",
            LogLevel.CRITICAL: "🚨"
        }.get(entry.level, "❓")
        
        time_str = entry.timestamp.strftime("%H:%M:%S")
        msg = entry.message[:45] + "..." if len(entry.message) > 45 else entry.message
        print(f"  {level_icon} {time_str} [{entry.application[:12]}] {msg}")
        
    # Statistics
    print("\n📊 Platform Statistics:")
    
    print(f"\n  Total Logs: {stats['total_logs']}")
    print(f"  Sources: {stats['sources']}")
    print(f"  Indexes: {stats['indexes']}")
    print(f"  Streams: {stats['streams']}")
    print(f"  Alerts: {stats['alerts']}")
    print(f"  Retention Policies: {stats['policies']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Log Aggregation Dashboard                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Logs:                    {stats['total_logs']:>12}                        │")
    print(f"│ Log Sources:                   {stats['sources']:>12}                        │")
    print(f"│ Indexes:                       {stats['indexes']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Active Streams:                {stats['streams']:>12}                        │")
    print(f"│ Alert Rules:                   {stats['alerts']:>12}                        │")
    print(f"│ Retention Policies:            {stats['policies']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Log Aggregation Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
