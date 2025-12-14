#!/usr/bin/env python3
"""
Server Init - Iteration 118: Log Aggregation Platform
Платформа агрегации логов

Функционал:
- Log Collection - сбор логов
- Log Parsing - парсинг логов
- Log Storage - хранение логов
- Log Search - поиск по логам
- Log Streaming - потоковая передача
- Alerting - алертинг
- Retention Policies - политики хранения
- Log Analytics - аналитика
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Pattern
from enum import Enum
from collections import defaultdict
import uuid
import random
import re


class LogLevel(Enum):
    """Уровень лога"""
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    FATAL = "fatal"


class LogSourceType(Enum):
    """Тип источника"""
    APPLICATION = "application"
    SYSTEM = "system"
    CONTAINER = "container"
    NETWORK = "network"
    SECURITY = "security"
    DATABASE = "database"


class AlertSeverity(Enum):
    """Критичность алерта"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ParserType(Enum):
    """Тип парсера"""
    JSON = "json"
    REGEX = "regex"
    GROK = "grok"
    SYSLOG = "syslog"
    CUSTOM = "custom"


@dataclass
class LogSource:
    """Источник логов"""
    source_id: str
    name: str = ""
    
    # Type
    source_type: LogSourceType = LogSourceType.APPLICATION
    
    # Connection
    endpoint: str = ""
    protocol: str = "tcp"  # tcp, udp, http, file
    
    # Parser
    parser_type: ParserType = ParserType.JSON
    parser_config: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    active: bool = True
    last_received: Optional[datetime] = None
    
    # Stats
    messages_received: int = 0
    bytes_received: int = 0


@dataclass
class LogEntry:
    """Запись лога"""
    log_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Source
    source_id: str = ""
    source_name: str = ""
    
    # Level
    level: LogLevel = LogLevel.INFO
    
    # Content
    message: str = ""
    raw_message: str = ""
    
    # Context
    service: str = ""
    host: str = ""
    container_id: str = ""
    
    # Structured data
    fields: Dict[str, Any] = field(default_factory=dict)
    
    # Tags
    tags: List[str] = field(default_factory=list)


@dataclass
class LogParser:
    """Парсер логов"""
    parser_id: str
    name: str = ""
    
    # Type
    parser_type: ParserType = ParserType.REGEX
    
    # Config
    pattern: str = ""
    field_mappings: Dict[str, str] = field(default_factory=dict)
    
    # Stats
    parsed_count: int = 0
    failed_count: int = 0


@dataclass
class AlertRule:
    """Правило алерта"""
    rule_id: str
    name: str = ""
    
    # Condition
    query: str = ""
    threshold: int = 1
    window_minutes: int = 5
    
    # Severity
    severity: AlertSeverity = AlertSeverity.MEDIUM
    
    # Actions
    notify_channels: List[str] = field(default_factory=list)
    
    # Status
    enabled: bool = True
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0


@dataclass
class Alert:
    """Алерт"""
    alert_id: str
    rule_id: str = ""
    rule_name: str = ""
    
    # Details
    severity: AlertSeverity = AlertSeverity.MEDIUM
    message: str = ""
    
    # Context
    matching_logs: int = 0
    sample_logs: List[str] = field(default_factory=list)
    
    # Timing
    triggered_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    
    # Status
    acknowledged: bool = False
    acknowledged_by: str = ""


@dataclass
class RetentionPolicy:
    """Политика хранения"""
    policy_id: str
    name: str = ""
    
    # Scope
    source_types: List[LogSourceType] = field(default_factory=list)
    log_levels: List[LogLevel] = field(default_factory=list)
    
    # Retention
    retention_days: int = 30
    
    # Archival
    archive_enabled: bool = False
    archive_after_days: int = 7
    
    # Status
    active: bool = True


@dataclass
class SearchQuery:
    """Поисковый запрос"""
    query_id: str
    
    # Query
    query_string: str = ""
    
    # Filters
    source_ids: List[str] = field(default_factory=list)
    log_levels: List[LogLevel] = field(default_factory=list)
    time_range_start: Optional[datetime] = None
    time_range_end: Optional[datetime] = None
    
    # Results
    total_hits: int = 0
    execution_time_ms: float = 0.0


class LogCollector:
    """Коллектор логов"""
    
    def __init__(self):
        self.sources: Dict[str, LogSource] = {}
        self.logs: List[LogEntry] = []
        
    def register_source(self, name: str, source_type: LogSourceType,
                         endpoint: str, **kwargs) -> LogSource:
        """Регистрация источника"""
        source = LogSource(
            source_id=f"src_{uuid.uuid4().hex[:8]}",
            name=name,
            source_type=source_type,
            endpoint=endpoint,
            **kwargs
        )
        self.sources[source.source_id] = source
        return source
        
    def collect(self, source_id: str, raw_message: str,
                 level: LogLevel = LogLevel.INFO,
                 **kwargs) -> LogEntry:
        """Сбор лога"""
        source = self.sources.get(source_id)
        if not source:
            return None
            
        entry = LogEntry(
            log_id=f"log_{uuid.uuid4().hex[:12]}",
            source_id=source_id,
            source_name=source.name,
            level=level,
            raw_message=raw_message,
            **kwargs
        )
        
        self.logs.append(entry)
        
        # Update source stats
        source.messages_received += 1
        source.bytes_received += len(raw_message)
        source.last_received = datetime.now()
        
        return entry


class LogParserEngine:
    """Движок парсинга"""
    
    def __init__(self):
        self.parsers: Dict[str, LogParser] = {}
        
    def create_parser(self, name: str, parser_type: ParserType,
                       pattern: str = "", **kwargs) -> LogParser:
        """Создание парсера"""
        parser = LogParser(
            parser_id=f"parser_{uuid.uuid4().hex[:8]}",
            name=name,
            parser_type=parser_type,
            pattern=pattern,
            **kwargs
        )
        self.parsers[parser.parser_id] = parser
        return parser
        
    def parse(self, parser_id: str, raw_message: str) -> Dict[str, Any]:
        """Парсинг сообщения"""
        parser = self.parsers.get(parser_id)
        if not parser:
            return {"message": raw_message}
            
        try:
            if parser.parser_type == ParserType.JSON:
                result = json.loads(raw_message)
                parser.parsed_count += 1
                return result
                
            elif parser.parser_type == ParserType.REGEX:
                match = re.match(parser.pattern, raw_message)
                if match:
                    parser.parsed_count += 1
                    return match.groupdict()
                    
            elif parser.parser_type == ParserType.SYSLOG:
                # Simplified syslog parsing
                parts = raw_message.split(" ", 5)
                if len(parts) >= 6:
                    parser.parsed_count += 1
                    return {
                        "priority": parts[0],
                        "timestamp": parts[1] + " " + parts[2],
                        "hostname": parts[3],
                        "program": parts[4],
                        "message": parts[5]
                    }
                    
            parser.failed_count += 1
            return {"message": raw_message, "_parse_error": True}
            
        except Exception as e:
            parser.failed_count += 1
            return {"message": raw_message, "_parse_error": str(e)}


class LogStorage:
    """Хранилище логов"""
    
    def __init__(self):
        self.logs: List[LogEntry] = []
        self.index: Dict[str, List[int]] = defaultdict(list)
        
    def store(self, entry: LogEntry):
        """Сохранение"""
        idx = len(self.logs)
        self.logs.append(entry)
        
        # Index by various fields
        self.index[f"source:{entry.source_id}"].append(idx)
        self.index[f"level:{entry.level.value}"].append(idx)
        self.index[f"service:{entry.service}"].append(idx)
        
        for tag in entry.tags:
            self.index[f"tag:{tag}"].append(idx)
            
    def count(self) -> int:
        """Количество логов"""
        return len(self.logs)
        
    def size_bytes(self) -> int:
        """Размер в байтах"""
        return sum(len(log.raw_message) for log in self.logs)


class LogSearchEngine:
    """Поисковый движок"""
    
    def __init__(self, storage: LogStorage):
        self.storage = storage
        
    def search(self, query_string: str,
                source_ids: List[str] = None,
                log_levels: List[LogLevel] = None,
                time_start: datetime = None,
                time_end: datetime = None,
                limit: int = 100) -> SearchQuery:
        """Поиск"""
        start_time = datetime.now()
        
        query = SearchQuery(
            query_id=f"q_{uuid.uuid4().hex[:8]}",
            query_string=query_string,
            source_ids=source_ids or [],
            log_levels=log_levels or [],
            time_range_start=time_start,
            time_range_end=time_end
        )
        
        # Filter logs
        results = []
        for log in self.storage.logs:
            # Text match
            if query_string and query_string.lower() not in log.message.lower():
                if query_string.lower() not in log.raw_message.lower():
                    continue
                    
            # Source filter
            if source_ids and log.source_id not in source_ids:
                continue
                
            # Level filter
            if log_levels and log.level not in log_levels:
                continue
                
            # Time filter
            if time_start and log.timestamp < time_start:
                continue
            if time_end and log.timestamp > time_end:
                continue
                
            results.append(log)
            
            if len(results) >= limit:
                break
                
        query.total_hits = len(results)
        query.execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        return query


class AlertEngine:
    """Движок алертов"""
    
    def __init__(self, storage: LogStorage):
        self.storage = storage
        self.rules: Dict[str, AlertRule] = {}
        self.alerts: List[Alert] = []
        
    def create_rule(self, name: str, query: str,
                     threshold: int = 1,
                     severity: AlertSeverity = AlertSeverity.MEDIUM,
                     **kwargs) -> AlertRule:
        """Создание правила"""
        rule = AlertRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name=name,
            query=query,
            threshold=threshold,
            severity=severity,
            **kwargs
        )
        self.rules[rule.rule_id] = rule
        return rule
        
    def evaluate(self, rule_id: str) -> Optional[Alert]:
        """Оценка правила"""
        rule = self.rules.get(rule_id)
        if not rule or not rule.enabled:
            return None
            
        # Count matching logs in window
        window_start = datetime.now() - timedelta(minutes=rule.window_minutes)
        
        matching = [log for log in self.storage.logs
                   if log.timestamp >= window_start
                   and rule.query.lower() in log.message.lower()]
        
        if len(matching) >= rule.threshold:
            alert = Alert(
                alert_id=f"alert_{uuid.uuid4().hex[:8]}",
                rule_id=rule_id,
                rule_name=rule.name,
                severity=rule.severity,
                message=f"Alert: {rule.name} - {len(matching)} matching logs",
                matching_logs=len(matching),
                sample_logs=[log.log_id for log in matching[:5]]
            )
            
            rule.last_triggered = datetime.now()
            rule.trigger_count += 1
            
            self.alerts.append(alert)
            return alert
            
        return None
        
    def evaluate_all(self) -> List[Alert]:
        """Оценка всех правил"""
        triggered = []
        for rule_id in self.rules:
            alert = self.evaluate(rule_id)
            if alert:
                triggered.append(alert)
        return triggered


class RetentionManager:
    """Менеджер хранения"""
    
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
        
    def apply_policies(self) -> Dict[str, Any]:
        """Применение политик"""
        deleted = 0
        archived = 0
        
        for policy in self.policies.values():
            if not policy.active:
                continue
                
            retention_threshold = datetime.now() - timedelta(days=policy.retention_days)
            archive_threshold = datetime.now() - timedelta(days=policy.archive_after_days)
            
            logs_to_delete = []
            
            for i, log in enumerate(self.storage.logs):
                # Check scope
                if policy.source_types:
                    source = None  # Would check source type
                    
                if policy.log_levels and log.level not in policy.log_levels:
                    continue
                    
                # Check retention
                if log.timestamp < retention_threshold:
                    logs_to_delete.append(i)
                    deleted += 1
                elif policy.archive_enabled and log.timestamp < archive_threshold:
                    # Archive log (simplified)
                    archived += 1
                    
        # Remove deleted (in reverse order)
        for i in reversed(logs_to_delete):
            if i < len(self.storage.logs):
                self.storage.logs.pop(i)
                
        return {
            "deleted": deleted,
            "archived": archived
        }


class LogAggregationPlatform:
    """Платформа агрегации логов"""
    
    def __init__(self):
        self.collector = LogCollector()
        self.parser_engine = LogParserEngine()
        self.storage = LogStorage()
        self.search_engine = LogSearchEngine(self.storage)
        self.alert_engine = AlertEngine(self.storage)
        self.retention_manager = RetentionManager(self.storage)
        
    def ingest(self, source_id: str, raw_message: str,
                parser_id: str = None, **kwargs) -> LogEntry:
        """Приём лога"""
        # Collect
        entry = self.collector.collect(source_id, raw_message, **kwargs)
        if not entry:
            return None
            
        # Parse
        if parser_id:
            parsed = self.parser_engine.parse(parser_id, raw_message)
            entry.fields = parsed
            entry.message = parsed.get("message", raw_message)
        else:
            entry.message = raw_message
            
        # Store
        self.storage.store(entry)
        
        return entry
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        logs = self.storage.logs
        
        by_level = defaultdict(int)
        by_source = defaultdict(int)
        
        for log in logs:
            by_level[log.level.value] += 1
            by_source[log.source_name] += 1
            
        return {
            "total_sources": len(self.collector.sources),
            "total_logs": self.storage.count(),
            "storage_bytes": self.storage.size_bytes(),
            "logs_by_level": dict(by_level),
            "logs_by_source": dict(by_source),
            "total_parsers": len(self.parser_engine.parsers),
            "alert_rules": len(self.alert_engine.rules),
            "active_alerts": len([a for a in self.alert_engine.alerts if not a.resolved_at]),
            "retention_policies": len(self.retention_manager.policies)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 118: Log Aggregation Platform")
    print("=" * 60)
    
    async def demo():
        platform = LogAggregationPlatform()
        print("✓ Log Aggregation Platform created")
        
        # Register log sources
        print("\n📡 Registering Log Sources...")
        
        sources_data = [
            ("api-gateway", LogSourceType.APPLICATION, "tcp://gateway:5000"),
            ("user-service", LogSourceType.APPLICATION, "tcp://user:5000"),
            ("nginx", LogSourceType.SYSTEM, "file:///var/log/nginx/access.log"),
            ("kubernetes", LogSourceType.CONTAINER, "http://k8s:9200"),
            ("firewall", LogSourceType.SECURITY, "udp://fw:514")
        ]
        
        created_sources = []
        for name, stype, endpoint in sources_data:
            source = platform.collector.register_source(name, stype, endpoint)
            created_sources.append(source)
            print(f"  ✓ {name} ({stype.value}): {endpoint}")
            
        # Create parsers
        print("\n🔧 Creating Log Parsers...")
        
        json_parser = platform.parser_engine.create_parser(
            "json-parser", ParserType.JSON
        )
        
        nginx_parser = platform.parser_engine.create_parser(
            "nginx-parser", ParserType.REGEX,
            pattern=r'(?P<ip>\S+) - - \[(?P<time>[^\]]+)\] "(?P<request>[^"]+)" (?P<status>\d+)'
        )
        
        syslog_parser = platform.parser_engine.create_parser(
            "syslog-parser", ParserType.SYSLOG
        )
        
        print(f"  ✓ JSON Parser")
        print(f"  ✓ Nginx Parser")
        print(f"  ✓ Syslog Parser")
        
        # Generate sample logs
        print("\n📝 Generating Sample Logs...")
        
        messages = [
            (LogLevel.INFO, "User logged in successfully", {"user_id": "123", "ip": "192.168.1.1"}),
            (LogLevel.INFO, "Request processed in 45ms", {"endpoint": "/api/users", "duration": 45}),
            (LogLevel.WARN, "High memory usage detected", {"memory_percent": 85}),
            (LogLevel.ERROR, "Database connection timeout", {"db": "primary", "timeout": 30}),
            (LogLevel.ERROR, "Authentication failed for user", {"user": "unknown", "attempts": 5}),
            (LogLevel.INFO, "Cache hit for key users:list", {"cache": "redis", "ttl": 300}),
            (LogLevel.DEBUG, "Processing batch job", {"job_id": "batch_001", "items": 1000}),
            (LogLevel.INFO, "Order created successfully", {"order_id": "ord_123", "total": 99.99}),
            (LogLevel.WARN, "Rate limit approaching threshold", {"current": 950, "limit": 1000}),
            (LogLevel.FATAL, "Critical service failure", {"service": "payment", "error": "connection_refused"})
        ]
        
        for _ in range(50):
            level, msg, fields = random.choice(messages)
            source = random.choice(created_sources)
            
            # Create JSON log
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "level": level.value,
                "message": msg,
                "service": source.name,
                **fields
            }
            
            entry = platform.ingest(
                source.source_id,
                json.dumps(log_data),
                parser_id=json_parser.parser_id,
                level=level,
                service=source.name,
                host=f"{source.name}-pod-{random.randint(1,5)}"
            )
            
        print(f"  ✓ Generated 50 log entries")
        
        # Show log level distribution
        print("\n📊 Log Level Distribution:")
        
        level_counts = defaultdict(int)
        for log in platform.storage.logs:
            level_counts[log.level.value] += 1
            
        level_icons = {
            "trace": "⚪", "debug": "🔵", "info": "🟢",
            "warn": "🟡", "error": "🔴", "fatal": "💀"
        }
        
        for level, count in sorted(level_counts.items()):
            icon = level_icons.get(level, "❓")
            bar = "█" * (count // 2)
            print(f"  {icon} {level:6}: {bar} ({count})")
            
        # Create alert rules
        print("\n🚨 Creating Alert Rules...")
        
        alert_rules = [
            ("High Error Rate", "error", 5, AlertSeverity.HIGH),
            ("Auth Failures", "Authentication failed", 3, AlertSeverity.CRITICAL),
            ("Database Issues", "Database connection", 2, AlertSeverity.HIGH),
            ("Service Failures", "Critical service failure", 1, AlertSeverity.CRITICAL)
        ]
        
        created_rules = []
        for name, query, threshold, severity in alert_rules:
            rule = platform.alert_engine.create_rule(
                name, query, threshold, severity,
                window_minutes=5
            )
            created_rules.append(rule)
            print(f"  ✓ {name}: '{query}' >= {threshold} in 5m ({severity.value})")
            
        # Evaluate alerts
        print("\n🔔 Evaluating Alerts...")
        
        triggered = platform.alert_engine.evaluate_all()
        
        if triggered:
            for alert in triggered:
                icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}.get(alert.severity.value, "⚪")
                print(f"  {icon} {alert.rule_name}: {alert.matching_logs} matches")
        else:
            print("  ✓ No alerts triggered")
            
        # Search logs
        print("\n🔍 Searching Logs...")
        
        searches = [
            ("error", None),
            ("user", [LogLevel.INFO]),
            ("connection", [LogLevel.ERROR, LogLevel.WARN])
        ]
        
        for query, levels in searches:
            result = platform.search_engine.search(
                query, log_levels=levels, limit=10
            )
            levels_str = ",".join(l.value for l in levels) if levels else "all"
            print(f"  '{query}' ({levels_str}): {result.total_hits} hits ({result.execution_time_ms:.2f}ms)")
            
        # Create retention policies
        print("\n🗂️ Creating Retention Policies...")
        
        policies_data = [
            ("Short-term Debug", 7, [LogLevel.DEBUG, LogLevel.TRACE]),
            ("Standard Logs", 30, [LogLevel.INFO, LogLevel.WARN]),
            ("Long-term Errors", 90, [LogLevel.ERROR, LogLevel.FATAL])
        ]
        
        for name, days, levels in policies_data:
            policy = platform.retention_manager.create_policy(
                name, days, log_levels=levels
            )
            levels_str = ",".join(l.value for l in levels)
            print(f"  ✓ {name}: {days} days ({levels_str})")
            
        # Source statistics
        print("\n📈 Source Statistics:")
        
        for source in created_sources:
            if source.messages_received > 0:
                kb = source.bytes_received / 1024
                print(f"  {source.name}: {source.messages_received} messages ({kb:.1f} KB)")
                
        # Parser statistics
        print("\n🔧 Parser Statistics:")
        
        for parser in platform.parser_engine.parsers.values():
            total = parser.parsed_count + parser.failed_count
            success_rate = (parser.parsed_count / total * 100) if total > 0 else 0
            print(f"  {parser.name}: {parser.parsed_count}/{total} ({success_rate:.1f}% success)")
            
        # Platform statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Collection:")
        print(f"    Sources: {stats['total_sources']}")
        print(f"    Logs: {stats['total_logs']}")
        print(f"    Storage: {stats['storage_bytes'] / 1024:.1f} KB")
        
        print(f"\n  Processing:")
        print(f"    Parsers: {stats['total_parsers']}")
        
        print(f"\n  Alerting:")
        print(f"    Rules: {stats['alert_rules']}")
        print(f"    Active Alerts: {stats['active_alerts']}")
        
        print(f"\n  Retention:")
        print(f"    Policies: {stats['retention_policies']}")
        
        # Recent logs
        print("\n📜 Recent Logs:")
        
        for log in platform.storage.logs[-5:]:
            icon = level_icons.get(log.level.value, "❓")
            time_str = log.timestamp.strftime("%H:%M:%S")
            print(f"  {icon} [{time_str}] {log.source_name}: {log.message[:50]}...")
            
        # Dashboard
        print("\n📋 Log Aggregation Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │              Log Aggregation Overview                       │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Log Sources:        {stats['total_sources']:>10}                        │")
        print(f"  │ Total Logs:         {stats['total_logs']:>10}                        │")
        print(f"  │ Storage Size:       {stats['storage_bytes']/1024:>10.1f} KB                   │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Parsers:            {stats['total_parsers']:>10}                        │")
        print(f"  │ Alert Rules:        {stats['alert_rules']:>10}                        │")
        print(f"  │ Active Alerts:      {stats['active_alerts']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ INFO:               {stats['logs_by_level'].get('info', 0):>10}                        │")
        print(f"  │ WARN:               {stats['logs_by_level'].get('warn', 0):>10}                        │")
        print(f"  │ ERROR:              {stats['logs_by_level'].get('error', 0):>10}                        │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Log Aggregation Platform initialized!")
    print("=" * 60)
