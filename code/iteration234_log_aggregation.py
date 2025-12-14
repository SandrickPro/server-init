#!/usr/bin/env python3
"""
Server Init - Iteration 234: Log Aggregation Platform
Платформа агрегации логов

Функционал:
- Log Collection - сбор логов
- Log Parsing - парсинг логов
- Log Indexing - индексирование
- Log Search - поиск
- Retention Policies - политики хранения
- Alerting - алерты на паттерны
- Dashboards - дашборды
- Export/Archive - экспорт и архивация
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Pattern
from enum import Enum
import uuid
import re
import hashlib


class LogLevel(Enum):
    """Уровень лога"""
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    FATAL = "fatal"


class SourceType(Enum):
    """Тип источника"""
    APPLICATION = "application"
    CONTAINER = "container"
    SYSTEM = "system"
    NETWORK = "network"
    SECURITY = "security"


class AlertStatus(Enum):
    """Статус алерта"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"


@dataclass
class LogSource:
    """Источник логов"""
    source_id: str
    name: str = ""
    source_type: SourceType = SourceType.APPLICATION
    
    # Connection
    host: str = ""
    port: int = 0
    protocol: str = "tcp"
    
    # Parsing
    parser: str = "json"  # json, regex, syslog, raw
    
    # Active
    is_active: bool = True
    
    # Stats
    events_received: int = 0
    last_event: Optional[datetime] = None


@dataclass
class LogEntry:
    """Запись лога"""
    entry_id: str
    source_id: str = ""
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Level
    level: LogLevel = LogLevel.INFO
    
    # Content
    message: str = ""
    
    # Context
    service: str = ""
    host: str = ""
    container: str = ""
    
    # Structured data
    fields: Dict[str, Any] = field(default_factory=dict)
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Trace
    trace_id: str = ""
    span_id: str = ""


@dataclass
class LogPattern:
    """Паттерн для поиска"""
    pattern_id: str
    name: str = ""
    
    # Pattern
    regex: str = ""
    
    # Level filter
    level_filter: List[LogLevel] = field(default_factory=list)
    
    # Source filter
    source_filter: List[str] = field(default_factory=list)
    
    # Active
    is_active: bool = True


@dataclass
class LogAlert:
    """Алерт на паттерн"""
    alert_id: str
    pattern_id: str = ""
    
    # Name
    name: str = ""
    description: str = ""
    
    # Threshold
    threshold: int = 1
    window_minutes: int = 5
    
    # Status
    status: AlertStatus = AlertStatus.ACTIVE
    
    # Notification
    notify_channels: List[str] = field(default_factory=list)
    
    # Stats
    trigger_count: int = 0
    last_triggered: Optional[datetime] = None


@dataclass
class RetentionPolicy:
    """Политика хранения"""
    policy_id: str
    name: str = ""
    
    # Retention
    hot_days: int = 7
    warm_days: int = 30
    cold_days: int = 90
    archive_days: int = 365
    
    # Filters
    source_filter: str = "*"
    level_filter: List[LogLevel] = field(default_factory=list)


@dataclass
class LogIndex:
    """Индекс логов"""
    index_id: str
    name: str = ""
    
    # Date range
    date: str = ""  # YYYY-MM-DD
    
    # Stats
    document_count: int = 0
    size_bytes: int = 0
    
    # Status
    status: str = "open"  # open, closed, archived


@dataclass
class SavedSearch:
    """Сохранённый поиск"""
    search_id: str
    name: str = ""
    description: str = ""
    
    # Query
    query: str = ""
    
    # Filters
    time_range: str = "24h"
    sources: List[str] = field(default_factory=list)
    levels: List[LogLevel] = field(default_factory=list)
    
    # Owner
    owner: str = ""
    
    # Created
    created_at: datetime = field(default_factory=datetime.now)


class LogParser:
    """Парсер логов"""
    
    def __init__(self):
        self.patterns = {
            "nginx": r'(?P<ip>\S+) - - \[(?P<time>[^\]]+)\] "(?P<request>[^"]+)" (?P<status>\d+)',
            "json": r'\{.*\}',
            "syslog": r'(?P<priority><\d+>)?(?P<timestamp>\w+ +\d+ \d+:\d+:\d+) (?P<host>\S+) (?P<process>\S+): (?P<message>.*)',
        }
        
    def parse(self, raw_line: str, parser_type: str = "json") -> Dict[str, Any]:
        """Парсинг строки лога"""
        if parser_type == "json":
            # Simplified JSON parsing
            try:
                # Extract key-value pairs
                data = {}
                if "level" in raw_line.lower():
                    data["level"] = "info"
                if "error" in raw_line.lower():
                    data["level"] = "error"
                data["message"] = raw_line
                return data
            except:
                return {"message": raw_line}
                
        elif parser_type in self.patterns:
            pattern = self.patterns[parser_type]
            match = re.match(pattern, raw_line)
            if match:
                return match.groupdict()
                
        return {"message": raw_line}


class LogAggregationPlatform:
    """Платформа агрегации логов"""
    
    def __init__(self):
        self.sources: Dict[str, LogSource] = {}
        self.entries: List[LogEntry] = []
        self.patterns: Dict[str, LogPattern] = {}
        self.alerts: Dict[str, LogAlert] = {}
        self.policies: Dict[str, RetentionPolicy] = {}
        self.indices: Dict[str, LogIndex] = {}
        self.saved_searches: Dict[str, SavedSearch] = {}
        self.parser = LogParser()
        
    def add_source(self, name: str, source_type: SourceType,
                  host: str = "", parser: str = "json") -> LogSource:
        """Добавление источника"""
        source = LogSource(
            source_id=f"src_{uuid.uuid4().hex[:8]}",
            name=name,
            source_type=source_type,
            host=host,
            parser=parser
        )
        self.sources[source.source_id] = source
        return source
        
    def ingest_log(self, source_id: str, message: str,
                  level: LogLevel = LogLevel.INFO,
                  fields: Dict[str, Any] = None,
                  tags: List[str] = None) -> LogEntry:
        """Приём записи лога"""
        source = self.sources.get(source_id)
        if not source:
            raise ValueError(f"Source {source_id} not found")
            
        entry = LogEntry(
            entry_id=f"log_{uuid.uuid4().hex[:12]}",
            source_id=source_id,
            level=level,
            message=message,
            service=source.name,
            host=source.host,
            fields=fields or {},
            tags=tags or []
        )
        
        self.entries.append(entry)
        
        # Update source stats
        source.events_received += 1
        source.last_event = datetime.now()
        
        # Update index
        self._update_index(entry)
        
        # Check alerts
        self._check_alerts(entry)
        
        return entry
        
    def _update_index(self, entry: LogEntry):
        """Обновление индекса"""
        date_str = entry.timestamp.strftime("%Y-%m-%d")
        index_name = f"logs-{date_str}"
        
        if index_name not in self.indices:
            self.indices[index_name] = LogIndex(
                index_id=f"idx_{uuid.uuid4().hex[:8]}",
                name=index_name,
                date=date_str
            )
            
        index = self.indices[index_name]
        index.document_count += 1
        index.size_bytes += len(entry.message) * 2
        
    def _check_alerts(self, entry: LogEntry):
        """Проверка алертов"""
        for alert in self.alerts.values():
            if alert.status != AlertStatus.ACTIVE:
                continue
                
            pattern = self.patterns.get(alert.pattern_id)
            if not pattern:
                continue
                
            # Check pattern
            if pattern.regex and re.search(pattern.regex, entry.message):
                # Check level filter
                if pattern.level_filter and entry.level not in pattern.level_filter:
                    continue
                    
                alert.trigger_count += 1
                alert.last_triggered = datetime.now()
                
    def search(self, query: str, time_range: str = "24h",
              levels: List[LogLevel] = None,
              sources: List[str] = None,
              limit: int = 100) -> List[LogEntry]:
        """Поиск логов"""
        results = []
        
        # Parse time range
        hours = 24
        if time_range.endswith("h"):
            hours = int(time_range[:-1])
        elif time_range.endswith("d"):
            hours = int(time_range[:-1]) * 24
            
        cutoff = datetime.now() - timedelta(hours=hours)
        
        for entry in reversed(self.entries):
            if entry.timestamp < cutoff:
                continue
                
            # Level filter
            if levels and entry.level not in levels:
                continue
                
            # Source filter
            if sources and entry.source_id not in sources:
                continue
                
            # Query match
            if query and query.lower() not in entry.message.lower():
                continue
                
            results.append(entry)
            
            if len(results) >= limit:
                break
                
        return results
        
    def create_pattern(self, name: str, regex: str,
                      levels: List[LogLevel] = None) -> LogPattern:
        """Создание паттерна"""
        pattern = LogPattern(
            pattern_id=f"pat_{uuid.uuid4().hex[:8]}",
            name=name,
            regex=regex,
            level_filter=levels or []
        )
        self.patterns[pattern.pattern_id] = pattern
        return pattern
        
    def create_alert(self, name: str, pattern_id: str,
                    threshold: int = 1, window_minutes: int = 5,
                    channels: List[str] = None) -> LogAlert:
        """Создание алерта"""
        alert = LogAlert(
            alert_id=f"alrt_{uuid.uuid4().hex[:8]}",
            pattern_id=pattern_id,
            name=name,
            threshold=threshold,
            window_minutes=window_minutes,
            notify_channels=channels or []
        )
        self.alerts[alert.alert_id] = alert
        return alert
        
    def create_retention_policy(self, name: str,
                               hot_days: int = 7,
                               warm_days: int = 30,
                               cold_days: int = 90) -> RetentionPolicy:
        """Создание политики хранения"""
        policy = RetentionPolicy(
            policy_id=f"ret_{uuid.uuid4().hex[:8]}",
            name=name,
            hot_days=hot_days,
            warm_days=warm_days,
            cold_days=cold_days
        )
        self.policies[policy.policy_id] = policy
        return policy
        
    def save_search(self, name: str, query: str,
                   time_range: str = "24h", owner: str = "") -> SavedSearch:
        """Сохранение поиска"""
        search = SavedSearch(
            search_id=f"srch_{uuid.uuid4().hex[:8]}",
            name=name,
            query=query,
            time_range=time_range,
            owner=owner
        )
        self.saved_searches[search.search_id] = search
        return search
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        entries = self.entries
        
        # By level
        by_level = {}
        for entry in entries:
            lvl = entry.level.value
            by_level[lvl] = by_level.get(lvl, 0) + 1
            
        # By source
        by_source = {}
        for source in self.sources.values():
            by_source[source.name] = source.events_received
            
        # Total size
        total_size = sum(idx.size_bytes for idx in self.indices.values())
        
        # Error rate
        error_count = by_level.get("error", 0) + by_level.get("fatal", 0)
        error_rate = (error_count / len(entries) * 100) if entries else 0
        
        return {
            "total_entries": len(entries),
            "sources": len(self.sources),
            "indices": len(self.indices),
            "total_size_mb": total_size / (1024**2),
            "by_level": by_level,
            "by_source": by_source,
            "error_rate": error_rate,
            "active_alerts": len([a for a in self.alerts.values() if a.status == AlertStatus.ACTIVE])
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 234: Log Aggregation Platform")
    print("=" * 60)
    
    platform = LogAggregationPlatform()
    print("✓ Log Aggregation Platform created")
    
    # Add log sources
    print("\n📡 Adding Log Sources...")
    
    sources_config = [
        ("api-service", SourceType.APPLICATION, "api-01.prod"),
        ("web-frontend", SourceType.APPLICATION, "web-01.prod"),
        ("nginx-proxy", SourceType.NETWORK, "lb-01.prod"),
        ("kubernetes", SourceType.CONTAINER, "k8s-master"),
        ("auth-service", SourceType.SECURITY, "auth-01.prod"),
        ("worker-jobs", SourceType.APPLICATION, "worker-01.prod"),
        ("database", SourceType.SYSTEM, "db-01.prod"),
    ]
    
    sources = []
    for name, stype, host in sources_config:
        source = platform.add_source(name, stype, host)
        sources.append(source)
        
        type_icons = {
            SourceType.APPLICATION: "📱",
            SourceType.CONTAINER: "🐳",
            SourceType.SYSTEM: "💻",
            SourceType.NETWORK: "🌐",
            SourceType.SECURITY: "🔒"
        }
        icon = type_icons.get(stype, "📋")
        print(f"  {icon} {name} ({stype.value})")
        
    # Ingest sample logs
    print("\n📥 Ingesting Logs...")
    
    log_messages = [
        (LogLevel.INFO, "Application started successfully", ["startup"]),
        (LogLevel.INFO, "Request processed in 45ms", ["performance"]),
        (LogLevel.WARN, "High memory usage detected: 85%", ["memory", "warning"]),
        (LogLevel.ERROR, "Connection to database failed", ["database", "error"]),
        (LogLevel.INFO, "User authentication successful", ["auth"]),
        (LogLevel.DEBUG, "Processing batch job #12345", ["batch"]),
        (LogLevel.ERROR, "Request timeout after 30s", ["timeout", "error"]),
        (LogLevel.INFO, "Cache hit ratio: 94%", ["cache", "performance"]),
        (LogLevel.FATAL, "Out of memory exception", ["memory", "fatal"]),
        (LogLevel.INFO, "Deployment completed successfully", ["deploy"]),
        (LogLevel.WARN, "SSL certificate expires in 7 days", ["ssl", "warning"]),
        (LogLevel.ERROR, "Invalid JSON payload received", ["validation", "error"]),
    ]
    
    for i in range(150):
        source = random.choice(sources)
        level, msg, tags = random.choice(log_messages)
        
        fields = {
            "request_id": f"req_{uuid.uuid4().hex[:8]}",
            "duration_ms": random.randint(10, 500)
        }
        
        platform.ingest_log(source.source_id, msg, level, fields, tags)
        
    print(f"  ✓ Ingested {len(platform.entries)} log entries")
    
    # Create patterns
    print("\n🔍 Creating Log Patterns...")
    
    patterns = [
        platform.create_pattern("Error Pattern", r"error|failed|exception", [LogLevel.ERROR, LogLevel.FATAL]),
        platform.create_pattern("Timeout Pattern", r"timeout", [LogLevel.ERROR, LogLevel.WARN]),
        platform.create_pattern("Memory Issues", r"memory|oom", [LogLevel.WARN, LogLevel.ERROR, LogLevel.FATAL]),
    ]
    
    for p in patterns:
        print(f"  📋 {p.name}: /{p.regex}/")
        
    # Create alerts
    print("\n🔔 Creating Alerts...")
    
    alerts = [
        platform.create_alert("Error Rate Alert", patterns[0].pattern_id, 5, 5, ["slack", "email"]),
        platform.create_alert("Timeout Alert", patterns[1].pattern_id, 3, 10, ["pagerduty"]),
        platform.create_alert("Memory Alert", patterns[2].pattern_id, 1, 5, ["slack"]),
    ]
    
    for a in alerts:
        print(f"  🔔 {a.name} (threshold: {a.threshold} in {a.window_minutes}m)")
        
    # Create retention policies
    print("\n📦 Creating Retention Policies...")
    
    policies = [
        platform.create_retention_policy("Production", 7, 30, 90),
        platform.create_retention_policy("Security", 30, 90, 365),
    ]
    
    for p in policies:
        print(f"  📦 {p.name}: hot={p.hot_days}d, warm={p.warm_days}d, cold={p.cold_days}d")
        
    # Search logs
    print("\n🔎 Searching Logs...")
    
    searches = [
        ("error", "1h", [LogLevel.ERROR]),
        ("request", "24h", [LogLevel.INFO]),
        ("memory", "6h", None),
    ]
    
    for query, time_range, levels in searches:
        results = platform.search(query, time_range, levels)
        print(f"  Query '{query}' ({time_range}): {len(results)} results")
        
    # Save searches
    print("\n💾 Saving Searches...")
    
    saved = [
        platform.save_search("Production Errors", "error", "24h", "admin"),
        platform.save_search("Authentication Issues", "auth failed", "1h", "security-team"),
    ]
    
    for s in saved:
        print(f"  💾 {s.name}")
        
    # Display log stream
    print("\n📜 Recent Log Stream:")
    
    recent_logs = platform.entries[-10:]
    
    level_colors = {
        LogLevel.DEBUG: "⚪",
        LogLevel.INFO: "🟢",
        LogLevel.WARN: "🟡",
        LogLevel.ERROR: "🔴",
        LogLevel.FATAL: "💀"
    }
    
    for entry in recent_logs:
        icon = level_colors.get(entry.level, "⚪")
        time_str = entry.timestamp.strftime("%H:%M:%S")
        msg = entry.message[:40] + "..." if len(entry.message) > 40 else entry.message
        print(f"  {icon} [{time_str}] {entry.service}: {msg}")
        
    # Display by source
    print("\n📡 Logs by Source:")
    
    print("\n  ┌────────────────────────┬────────────────┬────────────┬──────────┐")
    print("  │ Source                 │ Type           │ Events     │ Status   │")
    print("  ├────────────────────────┼────────────────┼────────────┼──────────┤")
    
    for source in platform.sources.values():
        name = source.name[:22].ljust(22)
        stype = source.source_type.value[:14].ljust(14)
        events = str(source.events_received)[:10].ljust(10)
        status = "🟢" if source.is_active else "🔴"
        
        print(f"  │ {name} │ {stype} │ {events} │ {status:8s} │")
        
    print("  └────────────────────────┴────────────────┴────────────┴──────────┘")
    
    # Display indices
    print("\n📊 Log Indices:")
    
    for idx in platform.indices.values():
        size_mb = idx.size_bytes / (1024**2)
        print(f"  📁 {idx.name}: {idx.document_count} docs, {size_mb:.1f} MB")
        
    # Log level distribution
    print("\n📈 Log Level Distribution:")
    
    stats = platform.get_statistics()
    
    level_order = ["debug", "info", "warn", "error", "fatal"]
    max_count = max(stats['by_level'].values()) if stats['by_level'] else 1
    
    for level in level_order:
        count = stats['by_level'].get(level, 0)
        bar_len = int((count / max_count) * 20) if max_count > 0 else 0
        bar = "█" * bar_len + "░" * (20 - bar_len)
        icon = level_colors.get(LogLevel(level), "⚪")
        print(f"  {icon} {level:6s} [{bar}] {count}")
        
    # Alert status
    print("\n🔔 Alert Status:")
    
    for alert in platform.alerts.values():
        status_icons = {
            AlertStatus.ACTIVE: "🟢",
            AlertStatus.RESOLVED: "✅",
            AlertStatus.ACKNOWLEDGED: "🔵"
        }
        icon = status_icons.get(alert.status, "⚪")
        triggered = f"triggered: {alert.trigger_count}" if alert.trigger_count > 0 else "no triggers"
        print(f"  {icon} {alert.name} - {triggered}")
        
    # Statistics
    print("\n📊 Platform Statistics:")
    
    print(f"\n  Total Entries: {stats['total_entries']}")
    print(f"  Active Sources: {stats['sources']}")
    print(f"  Indices: {stats['indices']}")
    print(f"  Storage Used: {stats['total_size_mb']:.2f} MB")
    print(f"  Error Rate: {stats['error_rate']:.1f}%")
    print(f"  Active Alerts: {stats['active_alerts']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Log Aggregation Dashboard                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Log Entries:             {stats['total_entries']:>12}                        │")
    print(f"│ Active Sources:                {stats['sources']:>12}                        │")
    print(f"│ Storage Used (MB):               {stats['total_size_mb']:>10.2f}                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Error Rate:                       {stats['error_rate']:>7.1f}%                       │")
    print(f"│ Active Alerts:                 {stats['active_alerts']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Log Aggregation Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
