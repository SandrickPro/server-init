#!/usr/bin/env python3
"""
Server Init - Iteration 168: Log Aggregation Platform
Платформа агрегации логов

Функционал:
- Log Collection - сбор логов
- Log Parsing - парсинг логов
- Log Indexing - индексация логов
- Log Search - поиск по логам
- Log Analytics - аналитика логов
- Log Retention - политики хранения
- Alert Rules - правила алертов
- Dashboard Integration - интеграция дашбордов
"""

import asyncio
import hashlib
import re
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Pattern
from enum import Enum
import uuid
import json
from collections import defaultdict


class LogLevel(Enum):
    """Уровень лога"""
    TRACE = 0
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4
    FATAL = 5


class LogSource(Enum):
    """Источник логов"""
    APPLICATION = "application"
    SYSTEM = "system"
    SECURITY = "security"
    AUDIT = "audit"
    ACCESS = "access"
    DATABASE = "database"
    NETWORK = "network"


class AlertSeverity(Enum):
    """Серьёзность алерта"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class LogEntry:
    """Запись лога"""
    log_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    level: LogLevel = LogLevel.INFO
    source: LogSource = LogSource.APPLICATION
    
    # Content
    message: str = ""
    raw: str = ""
    
    # Context
    service: str = ""
    host: str = ""
    instance: str = ""
    
    # Structured data
    fields: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    # Trace
    trace_id: str = ""
    span_id: str = ""
    parent_id: str = ""
    
    # Processing
    parsed: bool = False
    indexed: bool = False
    
    # Error context
    error_type: str = ""
    stack_trace: str = ""


@dataclass
class LogPattern:
    """Паттерн для парсинга"""
    pattern_id: str
    name: str = ""
    regex: str = ""
    grok: str = ""  # Grok pattern
    
    # Field extraction
    field_names: List[str] = field(default_factory=list)
    field_types: Dict[str, str] = field(default_factory=dict)  # name -> type
    
    # Priority (higher = checked first)
    priority: int = 0
    
    # Statistics
    match_count: int = 0
    last_match: Optional[datetime] = None


@dataclass
class AlertRule:
    """Правило алерта"""
    rule_id: str
    name: str = ""
    description: str = ""
    enabled: bool = True
    
    # Conditions
    level_threshold: LogLevel = LogLevel.ERROR
    message_pattern: str = ""
    service_filter: List[str] = field(default_factory=list)
    
    # Rate-based
    threshold_count: int = 0
    threshold_window_sec: int = 60
    
    # Alert settings
    severity: AlertSeverity = AlertSeverity.MEDIUM
    notification_channels: List[str] = field(default_factory=list)
    
    # Cooldown
    cooldown_sec: int = 300
    last_triggered: Optional[datetime] = None
    
    # Statistics
    trigger_count: int = 0


@dataclass
class Alert:
    """Алерт"""
    alert_id: str
    rule_id: str = ""
    rule_name: str = ""
    
    # Context
    severity: AlertSeverity = AlertSeverity.MEDIUM
    message: str = ""
    
    # Trigger info
    triggered_at: datetime = field(default_factory=datetime.now)
    trigger_count: int = 1
    
    # Related logs
    log_ids: List[str] = field(default_factory=list)
    sample_logs: List[str] = field(default_factory=list)
    
    # Status
    acknowledged: bool = False
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class RetentionPolicy:
    """Политика хранения"""
    policy_id: str
    name: str = ""
    
    # Retention period
    retention_days: int = 30
    
    # Filters
    level_filter: Optional[LogLevel] = None
    source_filter: Optional[LogSource] = None
    service_filter: List[str] = field(default_factory=list)
    
    # Actions
    archive_before_delete: bool = False
    archive_destination: str = ""
    
    # Statistics
    logs_deleted: int = 0
    last_cleanup: Optional[datetime] = None


@dataclass
class SearchQuery:
    """Поисковый запрос"""
    query_id: str
    query_text: str = ""
    
    # Filters
    time_from: Optional[datetime] = None
    time_to: Optional[datetime] = None
    levels: List[LogLevel] = field(default_factory=list)
    sources: List[LogSource] = field(default_factory=list)
    services: List[str] = field(default_factory=list)
    
    # Full-text search
    keywords: List[str] = field(default_factory=list)
    exclude_keywords: List[str] = field(default_factory=list)
    
    # Field search
    field_filters: Dict[str, Any] = field(default_factory=dict)
    
    # Pagination
    limit: int = 100
    offset: int = 0
    
    # Sort
    sort_field: str = "timestamp"
    sort_desc: bool = True


class LogParser:
    """Парсер логов"""
    
    def __init__(self):
        self.patterns: Dict[str, LogPattern] = {}
        self.compiled_patterns: Dict[str, Pattern] = {}
        
        # Built-in patterns
        self._register_builtin_patterns()
        
    def _register_builtin_patterns(self):
        """Регистрация встроенных паттернов"""
        # Apache/Nginx combined log
        self.register_pattern(LogPattern(
            pattern_id="apache_combined",
            name="Apache Combined Log",
            regex=r'^(?P<client_ip>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] "(?P<method>\w+) (?P<path>\S+) (?P<protocol>\S+)" (?P<status>\d+) (?P<bytes>\d+)',
            field_names=["client_ip", "timestamp", "method", "path", "protocol", "status", "bytes"],
            priority=10
        ))
        
        # Syslog
        self.register_pattern(LogPattern(
            pattern_id="syslog",
            name="Syslog",
            regex=r'^(?P<timestamp>\w+\s+\d+\s+[\d:]+) (?P<host>\S+) (?P<program>\S+?)(\[(?P<pid>\d+)\])?: (?P<message>.+)$',
            field_names=["timestamp", "host", "program", "pid", "message"],
            priority=5
        ))
        
        # JSON log
        self.register_pattern(LogPattern(
            pattern_id="json",
            name="JSON Log",
            regex=r'^\{.*\}$',
            priority=20
        ))
        
        # Application log
        self.register_pattern(LogPattern(
            pattern_id="app_log",
            name="Application Log",
            regex=r'^(?P<timestamp>[\d\-T:.Z]+)\s+(?P<level>\w+)\s+\[(?P<service>\w+)\]\s+(?P<message>.+)$',
            field_names=["timestamp", "level", "service", "message"],
            priority=15
        ))
        
    def register_pattern(self, pattern: LogPattern):
        """Регистрация паттерна"""
        self.patterns[pattern.pattern_id] = pattern
        if pattern.regex:
            self.compiled_patterns[pattern.pattern_id] = re.compile(pattern.regex)
            
    def parse(self, raw_log: str) -> LogEntry:
        """Парсинг лога"""
        log_id = f"log_{uuid.uuid4().hex[:12]}"
        
        entry = LogEntry(
            log_id=log_id,
            raw=raw_log,
            message=raw_log
        )
        
        # Try JSON first
        if raw_log.strip().startswith('{'):
            try:
                data = json.loads(raw_log)
                return self._parse_json(data, entry)
            except json.JSONDecodeError:
                pass
                
        # Try patterns by priority
        sorted_patterns = sorted(
            self.patterns.values(),
            key=lambda p: p.priority,
            reverse=True
        )
        
        for pattern in sorted_patterns:
            if pattern.pattern_id not in self.compiled_patterns:
                continue
                
            compiled = self.compiled_patterns[pattern.pattern_id]
            match = compiled.match(raw_log)
            
            if match:
                pattern.match_count += 1
                pattern.last_match = datetime.now()
                
                groups = match.groupdict()
                entry.fields.update(groups)
                
                # Extract common fields
                if 'message' in groups:
                    entry.message = groups['message']
                if 'level' in groups:
                    entry.level = self._parse_level(groups['level'])
                if 'service' in groups:
                    entry.service = groups['service']
                if 'host' in groups:
                    entry.host = groups['host']
                    
                entry.parsed = True
                break
                
        return entry
        
    def _parse_json(self, data: Dict, entry: LogEntry) -> LogEntry:
        """Парсинг JSON лога"""
        entry.fields = data
        entry.parsed = True
        
        # Map common fields
        if 'message' in data or 'msg' in data:
            entry.message = data.get('message') or data.get('msg', '')
        if 'level' in data:
            entry.level = self._parse_level(data['level'])
        if 'service' in data:
            entry.service = data['service']
        if 'host' in data or 'hostname' in data:
            entry.host = data.get('host') or data.get('hostname', '')
        if 'timestamp' in data or 'time' in data or '@timestamp' in data:
            ts = data.get('timestamp') or data.get('time') or data.get('@timestamp')
            # Parse timestamp if string
        if 'trace_id' in data:
            entry.trace_id = data['trace_id']
        if 'span_id' in data:
            entry.span_id = data['span_id']
        if 'error' in data:
            entry.error_type = data.get('error', {}).get('type', '')
            entry.stack_trace = data.get('error', {}).get('stack', '')
            
        return entry
        
    def _parse_level(self, level_str: str) -> LogLevel:
        """Парсинг уровня лога"""
        level_str = level_str.upper()
        
        level_map = {
            'TRACE': LogLevel.TRACE,
            'DEBUG': LogLevel.DEBUG,
            'INFO': LogLevel.INFO,
            'INFORMATION': LogLevel.INFO,
            'WARN': LogLevel.WARN,
            'WARNING': LogLevel.WARN,
            'ERROR': LogLevel.ERROR,
            'ERR': LogLevel.ERROR,
            'FATAL': LogLevel.FATAL,
            'CRITICAL': LogLevel.FATAL,
        }
        
        return level_map.get(level_str, LogLevel.INFO)


class LogIndexer:
    """Индексатор логов"""
    
    def __init__(self):
        # Inverted index for full-text search
        self.word_index: Dict[str, List[str]] = defaultdict(list)
        
        # Field indexes
        self.level_index: Dict[LogLevel, List[str]] = defaultdict(list)
        self.source_index: Dict[LogSource, List[str]] = defaultdict(list)
        self.service_index: Dict[str, List[str]] = defaultdict(list)
        self.time_index: Dict[str, List[str]] = defaultdict(list)  # date -> log_ids
        
        # Log storage
        self.logs: Dict[str, LogEntry] = {}
        
    def index(self, entry: LogEntry):
        """Индексация записи"""
        log_id = entry.log_id
        self.logs[log_id] = entry
        
        # Level index
        self.level_index[entry.level].append(log_id)
        
        # Source index
        self.source_index[entry.source].append(log_id)
        
        # Service index
        if entry.service:
            self.service_index[entry.service].append(log_id)
            
        # Time index (by date)
        date_key = entry.timestamp.strftime("%Y-%m-%d")
        self.time_index[date_key].append(log_id)
        
        # Word index (full-text)
        words = self._tokenize(entry.message)
        for word in words:
            self.word_index[word.lower()].append(log_id)
            
        # Index fields
        for key, value in entry.fields.items():
            if isinstance(value, str):
                for word in self._tokenize(value):
                    self.word_index[f"{key}:{word.lower()}"].append(log_id)
                    
        entry.indexed = True
        
    def _tokenize(self, text: str) -> List[str]:
        """Токенизация текста"""
        # Simple tokenization
        return re.findall(r'\w+', text.lower())
        
    def search(self, query: SearchQuery) -> List[LogEntry]:
        """Поиск по индексу"""
        candidate_ids: Optional[set] = None
        
        # Filter by time range
        if query.time_from or query.time_to:
            time_filtered = set()
            for date_key, log_ids in self.time_index.items():
                date = datetime.strptime(date_key, "%Y-%m-%d")
                if query.time_from and date < query.time_from.replace(hour=0, minute=0, second=0):
                    continue
                if query.time_to and date > query.time_to:
                    continue
                time_filtered.update(log_ids)
            candidate_ids = time_filtered
            
        # Filter by levels
        if query.levels:
            level_filtered = set()
            for level in query.levels:
                level_filtered.update(self.level_index[level])
            candidate_ids = level_filtered if candidate_ids is None else candidate_ids & level_filtered
            
        # Filter by sources
        if query.sources:
            source_filtered = set()
            for source in query.sources:
                source_filtered.update(self.source_index[source])
            candidate_ids = source_filtered if candidate_ids is None else candidate_ids & source_filtered
            
        # Filter by services
        if query.services:
            service_filtered = set()
            for service in query.services:
                service_filtered.update(self.service_index.get(service, []))
            candidate_ids = service_filtered if candidate_ids is None else candidate_ids & service_filtered
            
        # Full-text search
        if query.keywords:
            keyword_filtered = None
            for keyword in query.keywords:
                word_ids = set(self.word_index.get(keyword.lower(), []))
                keyword_filtered = word_ids if keyword_filtered is None else keyword_filtered & word_ids
            candidate_ids = keyword_filtered if candidate_ids is None else candidate_ids & keyword_filtered
            
        # Exclude keywords
        if query.exclude_keywords and candidate_ids:
            for keyword in query.exclude_keywords:
                word_ids = set(self.word_index.get(keyword.lower(), []))
                candidate_ids -= word_ids
                
        # Get all if no filters
        if candidate_ids is None:
            candidate_ids = set(self.logs.keys())
            
        # Fetch logs
        results = [self.logs[log_id] for log_id in candidate_ids if log_id in self.logs]
        
        # Sort
        results.sort(
            key=lambda e: e.timestamp,
            reverse=query.sort_desc
        )
        
        # Pagination
        return results[query.offset:query.offset + query.limit]


class AlertEngine:
    """Движок алертов"""
    
    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.alerts: List[Alert] = []
        
        # Rate counters
        self.rule_counters: Dict[str, List[datetime]] = defaultdict(list)
        
    def add_rule(self, rule: AlertRule):
        """Добавление правила"""
        self.rules[rule.rule_id] = rule
        
    def evaluate(self, entry: LogEntry) -> List[Alert]:
        """Оценка записи"""
        triggered_alerts = []
        
        for rule in self.rules.values():
            if not rule.enabled:
                continue
                
            if self._matches_rule(entry, rule):
                alert = self._trigger_alert(entry, rule)
                if alert:
                    triggered_alerts.append(alert)
                    
        return triggered_alerts
        
    def _matches_rule(self, entry: LogEntry, rule: AlertRule) -> bool:
        """Проверка соответствия правилу"""
        # Level check
        if entry.level.value < rule.level_threshold.value:
            return False
            
        # Service filter
        if rule.service_filter and entry.service not in rule.service_filter:
            return False
            
        # Message pattern
        if rule.message_pattern:
            if not re.search(rule.message_pattern, entry.message, re.IGNORECASE):
                return False
                
        return True
        
    def _trigger_alert(self, entry: LogEntry, rule: AlertRule) -> Optional[Alert]:
        """Создание алерта"""
        now = datetime.now()
        
        # Check cooldown
        if rule.last_triggered:
            cooldown_end = rule.last_triggered + timedelta(seconds=rule.cooldown_sec)
            if now < cooldown_end:
                return None
                
        # Rate-based check
        if rule.threshold_count > 0:
            # Clean old entries
            cutoff = now - timedelta(seconds=rule.threshold_window_sec)
            self.rule_counters[rule.rule_id] = [
                t for t in self.rule_counters[rule.rule_id]
                if t > cutoff
            ]
            
            # Add current
            self.rule_counters[rule.rule_id].append(now)
            
            # Check threshold
            if len(self.rule_counters[rule.rule_id]) < rule.threshold_count:
                return None
                
        # Create alert
        alert = Alert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            rule_id=rule.rule_id,
            rule_name=rule.name,
            severity=rule.severity,
            message=f"Alert triggered: {rule.name}",
            log_ids=[entry.log_id],
            sample_logs=[entry.message[:200]]
        )
        
        rule.last_triggered = now
        rule.trigger_count += 1
        
        self.alerts.append(alert)
        return alert


class LogAnalytics:
    """Аналитика логов"""
    
    def __init__(self, indexer: LogIndexer):
        self.indexer = indexer
        
    def get_level_distribution(self, hours: int = 24) -> Dict[str, int]:
        """Распределение по уровням"""
        distribution = {}
        cutoff = datetime.now() - timedelta(hours=hours)
        
        for level, log_ids in self.indexer.level_index.items():
            count = sum(
                1 for log_id in log_ids
                if log_id in self.indexer.logs and 
                self.indexer.logs[log_id].timestamp > cutoff
            )
            distribution[level.name] = count
            
        return distribution
        
    def get_service_stats(self, hours: int = 24) -> Dict[str, Dict]:
        """Статистика по сервисам"""
        cutoff = datetime.now() - timedelta(hours=hours)
        stats = defaultdict(lambda: {"total": 0, "errors": 0, "warnings": 0})
        
        for log_id, entry in self.indexer.logs.items():
            if entry.timestamp < cutoff:
                continue
                
            service = entry.service or "unknown"
            stats[service]["total"] += 1
            
            if entry.level == LogLevel.ERROR or entry.level == LogLevel.FATAL:
                stats[service]["errors"] += 1
            elif entry.level == LogLevel.WARN:
                stats[service]["warnings"] += 1
                
        return dict(stats)
        
    def get_error_trends(self, hours: int = 24, bucket_minutes: int = 60) -> Dict[str, int]:
        """Тренды ошибок по времени"""
        cutoff = datetime.now() - timedelta(hours=hours)
        buckets = defaultdict(int)
        
        for entry in self.indexer.logs.values():
            if entry.timestamp < cutoff:
                continue
            if entry.level not in [LogLevel.ERROR, LogLevel.FATAL]:
                continue
                
            bucket = entry.timestamp.replace(
                minute=entry.timestamp.minute // bucket_minutes * bucket_minutes,
                second=0,
                microsecond=0
            )
            buckets[bucket.isoformat()] += 1
            
        return dict(sorted(buckets.items()))
        
    def get_top_errors(self, limit: int = 10) -> List[Dict]:
        """Топ ошибок"""
        error_counts = defaultdict(lambda: {"count": 0, "last_seen": None, "sample": ""})
        
        for entry in self.indexer.logs.values():
            if entry.level not in [LogLevel.ERROR, LogLevel.FATAL]:
                continue
                
            # Normalize error message
            key = self._normalize_error(entry.message)
            error_counts[key]["count"] += 1
            error_counts[key]["last_seen"] = entry.timestamp
            error_counts[key]["sample"] = entry.message[:200]
            
        # Sort by count
        sorted_errors = sorted(
            error_counts.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )[:limit]
        
        return [
            {"pattern": k, **v}
            for k, v in sorted_errors
        ]
        
    def _normalize_error(self, message: str) -> str:
        """Нормализация сообщения ошибки"""
        # Remove numbers, IDs, etc.
        normalized = re.sub(r'\b[0-9a-f]{8,}\b', '<ID>', message)
        normalized = re.sub(r'\b\d+\b', '<NUM>', normalized)
        normalized = re.sub(r'\b\d{1,3}(\.\d{1,3}){3}\b', '<IP>', normalized)
        return normalized[:100]


class LogAggregationPlatform:
    """Платформа агрегации логов"""
    
    def __init__(self):
        self.parser = LogParser()
        self.indexer = LogIndexer()
        self.alert_engine = AlertEngine()
        self.analytics = LogAnalytics(self.indexer)
        self.retention_policies: List[RetentionPolicy] = []
        
    async def ingest(self, raw_log: str, source: LogSource = LogSource.APPLICATION, 
                     service: str = "", host: str = "") -> LogEntry:
        """Приём лога"""
        entry = self.parser.parse(raw_log)
        entry.source = source
        
        if service:
            entry.service = service
        if host:
            entry.host = host
            
        self.indexer.index(entry)
        
        # Check alerts
        alerts = self.alert_engine.evaluate(entry)
        for alert in alerts:
            print(f"  🚨 Alert: {alert.message}")
            
        return entry
        
    async def ingest_batch(self, logs: List[Dict]) -> int:
        """Пакетный приём"""
        count = 0
        for log_data in logs:
            await self.ingest(
                log_data.get("raw", ""),
                LogSource[log_data.get("source", "APPLICATION").upper()],
                log_data.get("service", ""),
                log_data.get("host", "")
            )
            count += 1
        return count
        
    def search(self, query_text: str = "", **kwargs) -> List[LogEntry]:
        """Поиск"""
        query = SearchQuery(
            query_id=f"q_{uuid.uuid4().hex[:8]}",
            query_text=query_text,
            **kwargs
        )
        
        if query_text:
            query.keywords = query_text.split()
            
        return self.indexer.search(query)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        return {
            "total_logs": len(self.indexer.logs),
            "patterns": len(self.parser.patterns),
            "alert_rules": len(self.alert_engine.rules),
            "total_alerts": len(self.alert_engine.alerts),
            "indexed_words": len(self.indexer.word_index)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 168: Log Aggregation Platform")
    print("=" * 60)
    
    async def demo():
        platform = LogAggregationPlatform()
        print("✓ Log Aggregation Platform created")
        
        # Setup alert rules
        print("\n🔔 Setting up Alert Rules...")
        
        platform.alert_engine.add_rule(AlertRule(
            rule_id="error_alert",
            name="Error Log Alert",
            level_threshold=LogLevel.ERROR,
            severity=AlertSeverity.HIGH
        ))
        
        platform.alert_engine.add_rule(AlertRule(
            rule_id="auth_failure",
            name="Authentication Failure",
            message_pattern=r"(authentication|login)\s+(failed|failure|error)",
            level_threshold=LogLevel.WARN,
            severity=AlertSeverity.CRITICAL,
            threshold_count=3,
            threshold_window_sec=60
        ))
        
        platform.alert_engine.add_rule(AlertRule(
            rule_id="high_latency",
            name="High Latency Warning",
            message_pattern=r"latency.*(>\s*1000|slow)",
            level_threshold=LogLevel.WARN,
            severity=AlertSeverity.MEDIUM
        ))
        
        print(f"  ✓ {len(platform.alert_engine.rules)} alert rules configured")
        
        # Ingest sample logs
        print("\n📥 Ingesting Logs...")
        
        sample_logs = [
            # Application logs
            {"raw": "2024-01-15T10:30:00Z INFO [api-gateway] Request received: GET /api/users", "service": "api-gateway"},
            {"raw": "2024-01-15T10:30:01Z DEBUG [api-gateway] Authentication successful for user_123", "service": "api-gateway"},
            {"raw": "2024-01-15T10:30:02Z INFO [user-service] Processing request for user_123", "service": "user-service"},
            {"raw": "2024-01-15T10:30:03Z WARN [user-service] Cache miss for user_123", "service": "user-service"},
            {"raw": "2024-01-15T10:30:05Z INFO [user-service] User data retrieved successfully", "service": "user-service"},
            
            # Error logs
            {"raw": "2024-01-15T10:31:00Z ERROR [database] Connection timeout after 5000ms", "service": "database"},
            {"raw": "2024-01-15T10:31:01Z ERROR [api-gateway] Failed to process request: database unavailable", "service": "api-gateway"},
            
            # Auth failures (for rate-based alert)
            {"raw": "2024-01-15T10:32:00Z WARN [auth-service] Authentication failed for user invalid@test.com", "service": "auth-service"},
            {"raw": "2024-01-15T10:32:01Z WARN [auth-service] Authentication failed for user hacker@test.com", "service": "auth-service"},
            {"raw": "2024-01-15T10:32:02Z WARN [auth-service] Authentication failed for user attacker@test.com", "service": "auth-service"},
            
            # JSON logs
            {"raw": '{"timestamp":"2024-01-15T10:33:00Z","level":"INFO","service":"payment-service","message":"Payment processed","amount":99.99,"currency":"USD","trace_id":"abc123"}', "service": "payment-service"},
            {"raw": '{"timestamp":"2024-01-15T10:33:01Z","level":"ERROR","service":"payment-service","message":"Payment gateway error","error":{"type":"GatewayTimeout","code":504}}', "service": "payment-service"},
            
            # Access logs
            {"raw": '192.168.1.100 - admin [15/Jan/2024:10:34:00 +0000] "GET /admin/dashboard HTTP/1.1" 200 5432', "source": "ACCESS"},
            {"raw": '192.168.1.101 - - [15/Jan/2024:10:34:01 +0000] "POST /api/login HTTP/1.1" 401 128', "source": "ACCESS"},
            
            # More variety
            {"raw": "2024-01-15T10:35:00Z INFO [notification-service] Email sent to user@example.com", "service": "notification-service"},
            {"raw": "2024-01-15T10:35:01Z DEBUG [cache-service] Cache hit for key: user_123_profile", "service": "cache-service"},
            {"raw": "2024-01-15T10:35:02Z WARN [api-gateway] High latency detected: response time > 1000ms", "service": "api-gateway"},
        ]
        
        for log_data in sample_logs:
            source = LogSource[log_data.get("source", "APPLICATION").upper()] if "source" in log_data else LogSource.APPLICATION
            await platform.ingest(
                log_data["raw"],
                source=source,
                service=log_data.get("service", ""),
                host="prod-server-01"
            )
            
        print(f"  ✓ Ingested {len(sample_logs)} log entries")
        
        # Show indexed logs
        print("\n📋 Recent Logs:")
        
        recent = platform.search(limit=8)
        
        print("\n  ┌──────────────────────────────────────────────────────────────────────────────────┐")
        print("  │ Level │ Service                │ Message                                           │")
        print("  ├──────────────────────────────────────────────────────────────────────────────────┤")
        
        for entry in recent:
            level = entry.level.name[:5].ljust(5)
            service = entry.service[:20].ljust(20) if entry.service else "unknown".ljust(20)
            message = entry.message[:49].ljust(49)
            print(f"  │ {level} │ {service} │ {message} │")
            
        print("  └──────────────────────────────────────────────────────────────────────────────────┘")
        
        # Search examples
        print("\n🔍 Search Examples:")
        
        # Search by keyword
        error_logs = platform.search("error", levels=[LogLevel.ERROR, LogLevel.FATAL])
        print(f"\n  Error logs found: {len(error_logs)}")
        
        # Search by service
        api_logs = platform.search(services=["api-gateway"])
        print(f"  API Gateway logs: {len(api_logs)}")
        
        # Search by pattern
        auth_logs = platform.search("authentication")
        print(f"  Authentication logs: {len(auth_logs)}")
        
        # Analytics
        print("\n📊 Log Analytics:")
        
        # Level distribution
        level_dist = platform.analytics.get_level_distribution()
        
        print("\n  Level Distribution:")
        print("  ┌──────────────────────────────────┐")
        
        total = sum(level_dist.values())
        for level, count in sorted(level_dist.items()):
            pct = (count / total * 100) if total > 0 else 0
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            print(f"  │ {level:6} │ {bar} │ {count:3} │")
            
        print("  └──────────────────────────────────┘")
        
        # Service stats
        service_stats = platform.analytics.get_service_stats()
        
        print("\n  Service Statistics:")
        print("  ┌────────────────────────────────────────────────────────┐")
        print("  │ Service              │ Total │ Errors │ Warnings │")
        print("  ├────────────────────────────────────────────────────────┤")
        
        for service, stats in list(service_stats.items())[:6]:
            svc = service[:18].ljust(18)
            print(f"  │ {svc} │ {stats['total']:>5} │ {stats['errors']:>6} │ {stats['warnings']:>8} │")
            
        print("  └────────────────────────────────────────────────────────┘")
        
        # Top errors
        print("\n  Top Errors:")
        
        top_errors = platform.analytics.get_top_errors(limit=3)
        
        for i, error in enumerate(top_errors, 1):
            print(f"  {i}. [{error['count']} occurrences] {error['sample'][:60]}...")
            
        # Alerts
        print("\n🚨 Triggered Alerts:")
        
        if platform.alert_engine.alerts:
            print("\n  ┌──────────────────────────────────────────────────────────────────┐")
            print("  │ Severity  │ Rule Name                  │ Time       │")
            print("  ├──────────────────────────────────────────────────────────────────┤")
            
            for alert in platform.alert_engine.alerts[-5:]:
                sev = alert.severity.value.upper()[:9].ljust(9)
                name = alert.rule_name[:26].ljust(26)
                time = alert.triggered_at.strftime("%H:%M:%S")
                print(f"  │ {sev} │ {name} │ {time:>10} │")
                
            print("  └──────────────────────────────────────────────────────────────────┘")
        else:
            print("  No alerts triggered")
            
        # Pattern statistics
        print("\n📐 Parser Patterns:")
        
        print("\n  ┌────────────────────────────────────────────────────────┐")
        print("  │ Pattern              │ Priority │ Matches │")
        print("  ├────────────────────────────────────────────────────────┤")
        
        for pattern in sorted(platform.parser.patterns.values(), key=lambda p: p.priority, reverse=True):
            name = pattern.name[:18].ljust(18)
            print(f"  │ {name} │ {pattern.priority:>8} │ {pattern.match_count:>7} │")
            
        print("  └────────────────────────────────────────────────────────┘")
        
        # Platform statistics
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Logs: {stats['total_logs']}")
        print(f"  Parser Patterns: {stats['patterns']}")
        print(f"  Alert Rules: {stats['alert_rules']}")
        print(f"  Triggered Alerts: {stats['total_alerts']}")
        print(f"  Indexed Words: {stats['indexed_words']}")
        
        # Dashboard
        print("\n┌────────────────────────────────────────────────────────────────────┐")
        print("│                   Log Aggregation Dashboard                        │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Total Logs Indexed:          {stats['total_logs']:>10}                       │")
        print(f"│ Parser Patterns:             {stats['patterns']:>10}                       │")
        print(f"│ Alert Rules Active:          {stats['alert_rules']:>10}                       │")
        print(f"│ Alerts Triggered:            {stats['total_alerts']:>10}                       │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Indexed Vocabulary:          {stats['indexed_words']:>10}                       │")
        print(f"│ Services Tracked:            {len(service_stats):>10}                       │")
        print("└────────────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Log Aggregation Platform initialized!")
    print("=" * 60)
