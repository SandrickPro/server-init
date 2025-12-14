#!/usr/bin/env python3
"""
Server Init - Iteration 205: Log Analytics Platform
Платформа аналитики логов

Функционал:
- Log Ingestion - приём логов
- Log Parsing - парсинг логов
- Log Indexing - индексирование
- Search & Query - поиск и запросы
- Aggregations - агрегации
- Alerting - оповещения
- Dashboards - дашборды
- Log Retention - хранение логов
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid
import re


class LogLevel(Enum):
    """Уровень лога"""
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    FATAL = "fatal"


class AggregationType(Enum):
    """Тип агрегации"""
    COUNT = "count"
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    TERMS = "terms"
    HISTOGRAM = "histogram"


class AlertSeverity(Enum):
    """Серьёзность оповещения"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class LogEntry:
    """Запись лога"""
    log_id: str
    
    # Content
    message: str = ""
    level: LogLevel = LogLevel.INFO
    
    # Source
    source: str = ""
    service: str = ""
    host: str = ""
    
    # Time
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Context
    trace_id: str = ""
    span_id: str = ""
    
    # Fields
    fields: Dict[str, Any] = field(default_factory=dict)
    
    # Index
    index: str = ""


@dataclass
class LogStream:
    """Поток логов"""
    stream_id: str
    name: str = ""
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Entries
    entries: List[LogEntry] = field(default_factory=list)
    
    # Retention
    retention_days: int = 30
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ParseRule:
    """Правило парсинга"""
    rule_id: str
    name: str = ""
    
    # Pattern
    pattern: str = ""  # Regex pattern
    
    # Field extraction
    extract_fields: List[str] = field(default_factory=list)
    
    # Enabled
    is_enabled: bool = True


@dataclass
class SearchQuery:
    """Поисковый запрос"""
    query_id: str
    
    # Query
    query_string: str = ""
    
    # Filters
    services: List[str] = field(default_factory=list)
    levels: List[LogLevel] = field(default_factory=list)
    
    # Time range
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # Limit
    limit: int = 100


@dataclass
class AggregationQuery:
    """Запрос агрегации"""
    agg_id: str
    name: str = ""
    
    # Type
    agg_type: AggregationType = AggregationType.COUNT
    
    # Field
    field: str = ""
    
    # Group by
    group_by: List[str] = field(default_factory=list)
    
    # Interval (for histogram)
    interval: str = "1h"


@dataclass
class AlertRule:
    """Правило оповещения"""
    rule_id: str
    name: str = ""
    
    # Condition
    query: str = ""
    threshold: int = 0
    comparison: str = ">"  # >, <, >=, <=, ==
    
    # Time window
    window_minutes: int = 5
    
    # Severity
    severity: AlertSeverity = AlertSeverity.MEDIUM
    
    # State
    is_enabled: bool = True
    last_triggered: Optional[datetime] = None


@dataclass
class Alert:
    """Оповещение"""
    alert_id: str
    rule_id: str
    
    # Trigger
    triggered_at: datetime = field(default_factory=datetime.now)
    
    # Value
    current_value: int = 0
    
    # Status
    status: str = "firing"  # firing, resolved
    
    # Message
    message: str = ""


class LogParser:
    """Парсер логов"""
    
    def __init__(self):
        self.rules: List[ParseRule] = []
        
        # Default patterns
        self.default_patterns = [
            (r'\[(\w+)\]', 'level'),
            (r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', 'timestamp'),
            (r'trace_id=(\w+)', 'trace_id'),
            (r'error|exception|failed', 'has_error'),
        ]
        
    def add_rule(self, rule: ParseRule):
        """Добавление правила"""
        self.rules.append(rule)
        
    def parse(self, raw_log: str) -> Dict[str, Any]:
        """Парсинг лога"""
        result = {}
        
        for pattern, field_name in self.default_patterns:
            match = re.search(pattern, raw_log, re.IGNORECASE)
            if match:
                result[field_name] = match.group(1) if match.groups() else True
                
        # Apply custom rules
        for rule in self.rules:
            if not rule.is_enabled:
                continue
            match = re.search(rule.pattern, raw_log)
            if match:
                for i, field in enumerate(rule.extract_fields):
                    if i < len(match.groups()):
                        result[field] = match.group(i + 1)
                        
        return result


class LogIndex:
    """Индекс логов"""
    
    def __init__(self):
        self.entries: List[LogEntry] = []
        self.by_service: Dict[str, List[int]] = {}
        self.by_level: Dict[str, List[int]] = {}
        self.by_hour: Dict[str, List[int]] = {}
        
    def index(self, entry: LogEntry) -> int:
        """Индексирование записи"""
        idx = len(self.entries)
        self.entries.append(entry)
        
        # Index by service
        if entry.service not in self.by_service:
            self.by_service[entry.service] = []
        self.by_service[entry.service].append(idx)
        
        # Index by level
        level = entry.level.value
        if level not in self.by_level:
            self.by_level[level] = []
        self.by_level[level].append(idx)
        
        # Index by hour
        hour_key = entry.timestamp.strftime("%Y-%m-%d-%H")
        if hour_key not in self.by_hour:
            self.by_hour[hour_key] = []
        self.by_hour[hour_key].append(idx)
        
        return idx
        
    def search(self, query: SearchQuery) -> List[LogEntry]:
        """Поиск"""
        candidates = set(range(len(self.entries)))
        
        # Filter by service
        if query.services:
            service_indices = set()
            for service in query.services:
                service_indices.update(self.by_service.get(service, []))
            candidates &= service_indices
            
        # Filter by level
        if query.levels:
            level_indices = set()
            for level in query.levels:
                level_indices.update(self.by_level.get(level.value, []))
            candidates &= level_indices
            
        # Get results
        results = []
        for idx in candidates:
            entry = self.entries[idx]
            
            # Time filter
            if query.start_time and entry.timestamp < query.start_time:
                continue
            if query.end_time and entry.timestamp > query.end_time:
                continue
                
            # Text search
            if query.query_string:
                if query.query_string.lower() not in entry.message.lower():
                    continue
                    
            results.append(entry)
            
            if len(results) >= query.limit:
                break
                
        return results


class LogAggregator:
    """Агрегатор логов"""
    
    def __init__(self, index: LogIndex):
        self.index = index
        
    def aggregate(self, query: AggregationQuery,
                 entries: List[LogEntry] = None) -> Dict[str, Any]:
        """Агрегация"""
        entries = entries or self.index.entries
        
        if query.agg_type == AggregationType.COUNT:
            return {"count": len(entries)}
            
        elif query.agg_type == AggregationType.TERMS:
            terms = {}
            for entry in entries:
                value = getattr(entry, query.field, None) or entry.fields.get(query.field)
                if value:
                    if hasattr(value, 'value'):
                        value = value.value
                    terms[str(value)] = terms.get(str(value), 0) + 1
            return {"terms": terms}
            
        elif query.agg_type == AggregationType.HISTOGRAM:
            buckets = {}
            for entry in entries:
                if query.interval == "1h":
                    bucket = entry.timestamp.strftime("%Y-%m-%d %H:00")
                elif query.interval == "1d":
                    bucket = entry.timestamp.strftime("%Y-%m-%d")
                else:
                    bucket = entry.timestamp.strftime("%Y-%m-%d %H:%M")
                buckets[bucket] = buckets.get(bucket, 0) + 1
            return {"histogram": buckets}
            
        return {}


class AlertEngine:
    """Движок оповещений"""
    
    def __init__(self, index: LogIndex):
        self.index = index
        self.rules: Dict[str, AlertRule] = {}
        self.alerts: List[Alert] = []
        
    def add_rule(self, rule: AlertRule):
        """Добавление правила"""
        self.rules[rule.rule_id] = rule
        
    async def evaluate(self):
        """Оценка правил"""
        cutoff = datetime.now() - timedelta(minutes=5)
        
        for rule in self.rules.values():
            if not rule.is_enabled:
                continue
                
            # Count matching logs
            count = 0
            for entry in self.index.entries:
                if entry.timestamp < cutoff:
                    continue
                if rule.query.lower() in entry.message.lower():
                    count += 1
                    
            # Check threshold
            triggered = False
            if rule.comparison == ">":
                triggered = count > rule.threshold
            elif rule.comparison == ">=":
                triggered = count >= rule.threshold
            elif rule.comparison == "<":
                triggered = count < rule.threshold
            elif rule.comparison == "<=":
                triggered = count <= rule.threshold
            elif rule.comparison == "==":
                triggered = count == rule.threshold
                
            if triggered:
                alert = Alert(
                    alert_id=f"alert_{uuid.uuid4().hex[:8]}",
                    rule_id=rule.rule_id,
                    current_value=count,
                    message=f"{rule.name}: {count} {rule.comparison} {rule.threshold}"
                )
                self.alerts.append(alert)
                rule.last_triggered = datetime.now()


class LogAnalyticsPlatform:
    """Платформа аналитики логов"""
    
    def __init__(self):
        self.parser = LogParser()
        self.index = LogIndex()
        self.aggregator = LogAggregator(self.index)
        self.alerts = AlertEngine(self.index)
        self.streams: Dict[str, LogStream] = {}
        
    def ingest(self, message: str, level: LogLevel = LogLevel.INFO,
               service: str = "", fields: Dict[str, Any] = None) -> LogEntry:
        """Приём лога"""
        entry = LogEntry(
            log_id=f"log_{uuid.uuid4().hex[:8]}",
            message=message,
            level=level,
            service=service,
            fields=fields or {},
            timestamp=datetime.now()
        )
        
        self.index.index(entry)
        return entry
        
    def search(self, query_string: str, services: List[str] = None,
               levels: List[LogLevel] = None, limit: int = 100) -> List[LogEntry]:
        """Поиск"""
        query = SearchQuery(
            query_id=f"q_{uuid.uuid4().hex[:8]}",
            query_string=query_string,
            services=services or [],
            levels=levels or [],
            limit=limit
        )
        return self.index.search(query)
        
    def aggregate(self, agg_type: AggregationType,
                 field: str = "") -> Dict[str, Any]:
        """Агрегация"""
        query = AggregationQuery(
            agg_id=f"agg_{uuid.uuid4().hex[:8]}",
            agg_type=agg_type,
            field=field
        )
        return self.aggregator.aggregate(query)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        return {
            "total_logs": len(self.index.entries),
            "services": len(self.index.by_service),
            "streams": len(self.streams),
            "alert_rules": len(self.alerts.rules),
            "active_alerts": len([a for a in self.alerts.alerts if a.status == "firing"]),
            "parse_rules": len(self.parser.rules)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 205: Log Analytics Platform")
    print("=" * 60)
    
    platform = LogAnalyticsPlatform()
    print("✓ Log Analytics Platform created")
    
    # Add alert rules
    print("\n🚨 Adding Alert Rules...")
    
    rules = [
        AlertRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name="High Error Rate",
            query="error",
            threshold=10,
            comparison=">=",
            severity=AlertSeverity.HIGH
        ),
        AlertRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name="Critical Failures",
            query="fatal",
            threshold=1,
            comparison=">=",
            severity=AlertSeverity.CRITICAL
        ),
    ]
    
    for rule in rules:
        platform.alerts.add_rule(rule)
        print(f"  ✓ {rule.name} (threshold: {rule.threshold})")
        
    # Ingest logs
    print("\n📥 Ingesting Logs...")
    
    services = ["api-gateway", "user-service", "order-service", "payment-service", "notification-service"]
    
    log_templates = [
        (LogLevel.INFO, "Request processed successfully"),
        (LogLevel.INFO, "User authenticated"),
        (LogLevel.INFO, "Database query executed"),
        (LogLevel.INFO, "Cache hit for key"),
        (LogLevel.WARNING, "Slow query detected"),
        (LogLevel.WARNING, "High memory usage"),
        (LogLevel.WARNING, "Connection pool exhausted"),
        (LogLevel.ERROR, "Failed to process request"),
        (LogLevel.ERROR, "Database connection error"),
        (LogLevel.ERROR, "External API timeout"),
        (LogLevel.DEBUG, "Processing request"),
        (LogLevel.DEBUG, "Validating input"),
    ]
    
    for _ in range(200):
        level, message = random.choice(log_templates)
        service = random.choice(services)
        
        entry = platform.ingest(
            f"{message} - request_id={uuid.uuid4().hex[:8]}",
            level,
            service,
            {"request_id": uuid.uuid4().hex[:8], "duration_ms": random.randint(10, 500)}
        )
        
    print(f"  ✓ Ingested {len(platform.index.entries)} log entries")
    
    # Run alert evaluation
    await platform.alerts.evaluate()
    
    # Search logs
    print("\n🔍 Searching Logs...")
    
    searches = [
        ("error", None, None),
        ("processed", ["api-gateway"], None),
        ("", None, [LogLevel.WARNING, LogLevel.ERROR]),
    ]
    
    for query, services, levels in searches:
        results = platform.search(query, services, levels, 10)
        query_desc = query or "all"
        service_desc = f"services={services}" if services else ""
        level_desc = f"levels={[l.value for l in levels]}" if levels else ""
        print(f"  '{query_desc}' {service_desc} {level_desc}: {len(results)} results")
        
    # Display search results
    print("\n📋 Search Results (errors):")
    
    error_logs = platform.search("error", limit=5)
    for log in error_logs[:5]:
        time_str = log.timestamp.strftime("%H:%M:%S")
        print(f"  [{time_str}] [{log.level.value:7}] {log.service}: {log.message[:50]}...")
        
    # Aggregations
    print("\n📊 Aggregations:")
    
    # Count by level
    level_agg = platform.aggregate(AggregationType.TERMS, "level")
    print("\n  Logs by Level:")
    for level, count in sorted(level_agg.get("terms", {}).items(), key=lambda x: x[1], reverse=True):
        bar = "█" * min(count // 5, 30) + "░" * max(0, 30 - count // 5)
        print(f"    {level:10} [{bar}] {count}")
        
    # Count by service
    service_agg = platform.aggregate(AggregationType.TERMS, "service")
    print("\n  Logs by Service:")
    for service, count in sorted(service_agg.get("terms", {}).items(), key=lambda x: x[1], reverse=True):
        bar = "█" * min(count // 5, 30) + "░" * max(0, 30 - count // 5)
        print(f"    {service:20} [{bar}] {count}")
        
    # Time histogram
    time_agg = platform.aggregator.aggregate(AggregationQuery(
        agg_id=f"agg_{uuid.uuid4().hex[:8]}",
        agg_type=AggregationType.HISTOGRAM,
        interval="1h"
    ))
    
    print("\n  Logs by Hour:")
    for bucket, count in sorted(time_agg.get("histogram", {}).items())[-5:]:
        bar = "█" * min(count // 5, 30) + "░" * max(0, 30 - count // 5)
        print(f"    {bucket} [{bar}] {count}")
        
    # Display logs table
    print("\n📋 Recent Logs:")
    
    print("\n  ┌───────────┬─────────┬─────────────────────┬──────────────────────────────────────────┐")
    print("  │ Time      │ Level   │ Service             │ Message                                  │")
    print("  ├───────────┼─────────┼─────────────────────┼──────────────────────────────────────────┤")
    
    for log in platform.index.entries[-10:]:
        time_str = log.timestamp.strftime("%H:%M:%S")
        level = log.level.value[:7].ljust(7)
        service = log.service[:19].ljust(19)
        message = log.message[:40].ljust(40)
        print(f"  │ {time_str} │ {level} │ {service} │ {message} │")
        
    print("  └───────────┴─────────┴─────────────────────┴──────────────────────────────────────────┘")
    
    # Alerts
    print("\n🚨 Active Alerts:")
    
    if platform.alerts.alerts:
        for alert in platform.alerts.alerts[:5]:
            rule = platform.alerts.rules.get(alert.rule_id)
            severity = rule.severity.value if rule else "unknown"
            print(f"  🔴 [{severity:8}] {alert.message}")
    else:
        print("  ✓ No active alerts")
        
    # Error analysis
    print("\n📈 Error Analysis:")
    
    error_entries = [e for e in platform.index.entries 
                    if e.level in [LogLevel.ERROR, LogLevel.FATAL]]
    
    if error_entries:
        error_by_service = {}
        for entry in error_entries:
            error_by_service[entry.service] = error_by_service.get(entry.service, 0) + 1
            
        print("\n  Errors by Service:")
        for service, count in sorted(error_by_service.items(), key=lambda x: x[1], reverse=True):
            pct = (count / len(error_entries) * 100)
            bar = "█" * int(pct / 2) + "░" * (50 - int(pct / 2))
            print(f"    {service:20} [{bar}] {count} ({pct:.1f}%)")
            
    # Log patterns
    print("\n📝 Common Log Patterns:")
    
    patterns = {}
    for entry in platform.index.entries:
        # Extract pattern (first few words)
        words = entry.message.split()[:3]
        pattern = " ".join(words)
        patterns[pattern] = patterns.get(pattern, 0) + 1
        
    for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"    {count:4}x {pattern}...")
        
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📊 Platform Statistics:")
    
    print(f"\n  Total Logs: {stats['total_logs']}")
    print(f"  Services: {stats['services']}")
    print(f"  Alert Rules: {stats['alert_rules']}")
    print(f"  Active Alerts: {stats['active_alerts']}")
    
    # Error rate
    total_logs = len(platform.index.entries)
    error_logs_count = len(error_entries)
    error_rate = (error_logs_count / total_logs * 100) if total_logs > 0 else 0
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                     Log Analytics Dashboard                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Logs:                    {stats['total_logs']:>12}                        │")
    print(f"│ Services:                      {stats['services']:>12}                        │")
    print(f"│ Error Rate:                      {error_rate:>10.2f}%                   │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Alert Rules:                   {stats['alert_rules']:>12}                        │")
    print(f"│ Active Alerts:                 {stats['active_alerts']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Log Analytics Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
