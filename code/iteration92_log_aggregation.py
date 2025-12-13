#!/usr/bin/env python3
"""
Server Init - Iteration 92: Log Aggregation Platform
Платформа агрегации логов

Функционал:
- Log Collection - сбор логов
- Log Parsing - парсинг логов
- Log Storage - хранение логов
- Log Search - поиск по логам
- Log Analysis - анализ логов
- Pattern Detection - обнаружение паттернов
- Alert Rules - правила алертов
- Retention Management - управление ретеншеном
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Pattern, Tuple
from enum import Enum
from collections import defaultdict
import uuid
import random
import re


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
    NETWORK = "network"
    DATABASE = "database"


class AlertState(Enum):
    """Состояние алерта"""
    PENDING = "pending"
    FIRING = "firing"
    RESOLVED = "resolved"


@dataclass
class LogEntry:
    """Запись лога"""
    log_id: str
    
    # Время
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Уровень
    level: LogLevel = LogLevel.INFO
    
    # Сообщение
    message: str = ""
    
    # Источник
    source: LogSource = LogSource.APPLICATION
    service: str = ""
    host: str = ""
    
    # Контекст
    trace_id: str = ""
    span_id: str = ""
    request_id: str = ""
    
    # Структурированные данные
    fields: Dict[str, Any] = field(default_factory=dict)
    
    # Теги
    tags: List[str] = field(default_factory=list)
    
    # Raw лог
    raw: str = ""
    
    # Парсинг
    parsed: bool = False
    parser_name: str = ""


@dataclass
class LogStream:
    """Поток логов"""
    stream_id: str
    name: str = ""
    
    # Фильтры
    services: List[str] = field(default_factory=list)
    hosts: List[str] = field(default_factory=list)
    levels: List[LogLevel] = field(default_factory=list)
    
    # Буфер
    buffer: List[LogEntry] = field(default_factory=list)
    buffer_size: int = 1000
    
    # Статистика
    total_logs: int = 0
    logs_per_second: float = 0


@dataclass
class LogPattern:
    """Паттерн лога"""
    pattern_id: str
    name: str = ""
    
    # Regex паттерн
    regex: str = ""
    compiled: Optional[Pattern] = None
    
    # Извлекаемые поля
    fields: List[str] = field(default_factory=list)
    
    # Примеры
    examples: List[str] = field(default_factory=list)
    
    # Статистика
    match_count: int = 0


@dataclass
class LogQuery:
    """Запрос к логам"""
    query_id: str
    
    # Текстовый поиск
    text: str = ""
    regex: str = ""
    
    # Фильтры
    services: List[str] = field(default_factory=list)
    hosts: List[str] = field(default_factory=list)
    levels: List[LogLevel] = field(default_factory=list)
    
    # Временной диапазон
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # Поля
    field_filters: Dict[str, Any] = field(default_factory=dict)
    
    # Пагинация
    limit: int = 100
    offset: int = 0


@dataclass
class LogQueryResult:
    """Результат запроса"""
    query_id: str
    total_count: int = 0
    returned_count: int = 0
    
    logs: List[LogEntry] = field(default_factory=list)
    
    # Время выполнения
    execution_time_ms: float = 0
    
    # Агрегации
    aggregations: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LogAlert:
    """Алерт по логам"""
    alert_id: str
    name: str = ""
    description: str = ""
    
    # Условие
    query: str = ""
    threshold: int = 1
    time_window_minutes: int = 5
    
    # Уровень
    severity: str = "warning"
    
    # Состояние
    state: AlertState = AlertState.PENDING
    
    # Количество срабатываний
    current_count: int = 0
    
    # Время
    last_triggered: Optional[datetime] = None
    
    # Уведомления
    notification_channels: List[str] = field(default_factory=list)


@dataclass
class RetentionPolicy:
    """Политика хранения"""
    policy_id: str
    name: str = ""
    
    # Срок хранения
    retention_days: int = 30
    
    # Фильтры
    services: List[str] = field(default_factory=list)
    levels: List[LogLevel] = field(default_factory=list)
    
    # Действия
    archive_before_delete: bool = True
    compress: bool = True


class LogParser:
    """Парсер логов"""
    
    def __init__(self):
        self.patterns: Dict[str, LogPattern] = {}
        
        # Стандартные паттерны
        self._add_default_patterns()
        
    def _add_default_patterns(self):
        """Добавление стандартных паттернов"""
        # Apache Combined Log Format
        self.add_pattern(
            "apache_combined",
            r'^(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] "(?P<method>\S+) (?P<path>\S+) \S+" (?P<status>\d+) (?P<size>\d+)',
            ["ip", "timestamp", "method", "path", "status", "size"]
        )
        
        # Nginx
        self.add_pattern(
            "nginx",
            r'^(?P<ip>\S+) - \S+ \[(?P<timestamp>[^\]]+)\] "(?P<request>[^"]+)" (?P<status>\d+) (?P<bytes>\d+)',
            ["ip", "timestamp", "request", "status", "bytes"]
        )
        
        # JSON
        self.add_pattern(
            "json",
            r'^\{.*\}$',
            []
        )
        
        # Syslog
        self.add_pattern(
            "syslog",
            r'^(?P<priority><\d+>)?(?P<timestamp>\w{3}\s+\d+\s+\d+:\d+:\d+) (?P<host>\S+) (?P<process>\S+): (?P<message>.*)$',
            ["priority", "timestamp", "host", "process", "message"]
        )
        
    def add_pattern(self, name: str, regex: str, fields: List[str]) -> LogPattern:
        """Добавление паттерна"""
        pattern = LogPattern(
            pattern_id=f"pattern_{uuid.uuid4().hex[:8]}",
            name=name,
            regex=regex,
            compiled=re.compile(regex),
            fields=fields
        )
        self.patterns[name] = pattern
        return pattern
        
    def parse(self, raw: str, pattern_name: str = None) -> Tuple[bool, Dict[str, Any]]:
        """Парсинг лога"""
        if pattern_name and pattern_name in self.patterns:
            return self._try_pattern(raw, self.patterns[pattern_name])
            
        # Пробуем все паттерны
        for pattern in self.patterns.values():
            success, fields = self._try_pattern(raw, pattern)
            if success:
                return success, fields
                
        return False, {}
        
    def _try_pattern(self, raw: str, pattern: LogPattern) -> Tuple[bool, Dict[str, Any]]:
        """Попытка применить паттерн"""
        if pattern.name == "json":
            try:
                data = json.loads(raw)
                pattern.match_count += 1
                return True, data
            except:
                return False, {}
                
        if pattern.compiled:
            match = pattern.compiled.match(raw)
            if match:
                pattern.match_count += 1
                return True, match.groupdict()
                
        return False, {}


class LogStorage:
    """Хранилище логов"""
    
    def __init__(self):
        self.logs: Dict[str, LogEntry] = {}
        self.indexes: Dict[str, Dict[Any, List[str]]] = defaultdict(lambda: defaultdict(list))
        
    def store(self, log: LogEntry):
        """Сохранение лога"""
        self.logs[log.log_id] = log
        
        # Индексация
        self.indexes["service"][log.service].append(log.log_id)
        self.indexes["host"][log.host].append(log.log_id)
        self.indexes["level"][log.level].append(log.log_id)
        
        # Временной индекс (по часам)
        hour_key = log.timestamp.strftime("%Y-%m-%d-%H")
        self.indexes["time"][hour_key].append(log.log_id)
        
    def get(self, log_id: str) -> Optional[LogEntry]:
        """Получение лога"""
        return self.logs.get(log_id)
        
    def delete(self, log_id: str):
        """Удаление лога"""
        log = self.logs.pop(log_id, None)
        if log:
            # Удаление из индексов
            self.indexes["service"][log.service].remove(log_id)
            self.indexes["host"][log.host].remove(log_id)
            self.indexes["level"][log.level].remove(log_id)
            
    def count(self) -> int:
        """Количество логов"""
        return len(self.logs)


class LogSearchEngine:
    """Поисковый движок"""
    
    def __init__(self, storage: LogStorage):
        self.storage = storage
        
    def search(self, query: LogQuery) -> LogQueryResult:
        """Поиск логов"""
        start = datetime.now()
        
        result = LogQueryResult(query_id=query.query_id)
        
        # Получаем кандидатов
        candidates = self._get_candidates(query)
        
        # Фильтруем
        filtered = []
        for log_id in candidates:
            log = self.storage.get(log_id)
            if log and self._matches(log, query):
                filtered.append(log)
                
        # Сортируем по времени (новые первые)
        filtered.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Пагинация
        result.total_count = len(filtered)
        result.logs = filtered[query.offset:query.offset + query.limit]
        result.returned_count = len(result.logs)
        
        # Агрегации
        result.aggregations = self._aggregate(filtered)
        
        result.execution_time_ms = (datetime.now() - start).total_seconds() * 1000
        
        return result
        
    def _get_candidates(self, query: LogQuery) -> Set[str]:
        """Получение кандидатов из индексов"""
        candidates = set(self.storage.logs.keys())
        
        # Фильтр по сервисам
        if query.services:
            service_logs = set()
            for service in query.services:
                service_logs.update(self.storage.indexes["service"].get(service, []))
            candidates &= service_logs
            
        # Фильтр по уровням
        if query.levels:
            level_logs = set()
            for level in query.levels:
                level_logs.update(self.storage.indexes["level"].get(level, []))
            candidates &= level_logs
            
        return candidates
        
    def _matches(self, log: LogEntry, query: LogQuery) -> bool:
        """Проверка соответствия логу запросу"""
        # Текстовый поиск
        if query.text and query.text.lower() not in log.message.lower():
            return False
            
        # Regex поиск
        if query.regex:
            try:
                if not re.search(query.regex, log.message):
                    return False
            except:
                pass
                
        # Временной диапазон
        if query.start_time and log.timestamp < query.start_time:
            return False
        if query.end_time and log.timestamp > query.end_time:
            return False
            
        # Фильтры по полям
        for field, value in query.field_filters.items():
            if log.fields.get(field) != value:
                return False
                
        return True
        
    def _aggregate(self, logs: List[LogEntry]) -> Dict[str, Any]:
        """Агрегации"""
        aggs = {
            "by_level": defaultdict(int),
            "by_service": defaultdict(int),
            "by_hour": defaultdict(int)
        }
        
        for log in logs:
            aggs["by_level"][log.level.name] += 1
            aggs["by_service"][log.service] += 1
            aggs["by_hour"][log.timestamp.strftime("%H:00")] += 1
            
        return {k: dict(v) for k, v in aggs.items()}


class PatternDetector:
    """Детектор паттернов"""
    
    def __init__(self):
        self.known_patterns: Dict[str, int] = defaultdict(int)
        self.anomalies: List[Dict[str, Any]] = []
        
    def analyze(self, logs: List[LogEntry]) -> Dict[str, Any]:
        """Анализ паттернов"""
        # Группируем похожие сообщения
        message_groups = defaultdict(list)
        
        for log in logs:
            # Нормализуем сообщение
            normalized = self._normalize_message(log.message)
            message_groups[normalized].append(log)
            self.known_patterns[normalized] += 1
            
        # Находим топ паттерны
        top_patterns = sorted(
            message_groups.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:10]
        
        # Обнаружение аномалий
        error_rate = sum(1 for l in logs if l.level in [LogLevel.ERROR, LogLevel.FATAL]) / len(logs) if logs else 0
        
        if error_rate > 0.1:  # > 10% ошибок
            self.anomalies.append({
                "type": "high_error_rate",
                "rate": error_rate,
                "timestamp": datetime.now()
            })
            
        return {
            "total_logs": len(logs),
            "unique_patterns": len(message_groups),
            "top_patterns": [(p, len(logs)) for p, logs in top_patterns],
            "error_rate": error_rate
        }
        
    def _normalize_message(self, message: str) -> str:
        """Нормализация сообщения"""
        # Заменяем числа
        normalized = re.sub(r'\d+', 'N', message)
        # Заменяем UUID
        normalized = re.sub(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', 'UUID', normalized)
        # Заменяем IP адреса
        normalized = re.sub(r'\d+\.\d+\.\d+\.\d+', 'IP', normalized)
        return normalized


class AlertEngine:
    """Движок алертов"""
    
    def __init__(self):
        self.alerts: Dict[str, LogAlert] = {}
        self.triggered_alerts: List[Dict[str, Any]] = []
        
    def create_alert(self, name: str, query: str, threshold: int = 1,
                      time_window: int = 5, severity: str = "warning") -> LogAlert:
        """Создание алерта"""
        alert = LogAlert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            name=name,
            query=query,
            threshold=threshold,
            time_window_minutes=time_window,
            severity=severity
        )
        self.alerts[alert.alert_id] = alert
        return alert
        
    def check(self, logs: List[LogEntry]):
        """Проверка алертов"""
        for alert in self.alerts.values():
            # Считаем совпадения
            matches = 0
            for log in logs:
                if self._matches_query(log, alert.query):
                    matches += 1
                    
            alert.current_count = matches
            
            if matches >= alert.threshold:
                if alert.state != AlertState.FIRING:
                    alert.state = AlertState.FIRING
                    alert.last_triggered = datetime.now()
                    
                    self.triggered_alerts.append({
                        "alert_id": alert.alert_id,
                        "name": alert.name,
                        "count": matches,
                        "timestamp": datetime.now()
                    })
            else:
                if alert.state == AlertState.FIRING:
                    alert.state = AlertState.RESOLVED
                    
    def _matches_query(self, log: LogEntry, query: str) -> bool:
        """Проверка соответствия запросу"""
        # Простой поиск по подстроке
        return query.lower() in log.message.lower()


class RetentionManager:
    """Менеджер ретеншена"""
    
    def __init__(self, storage: LogStorage):
        self.storage = storage
        self.policies: Dict[str, RetentionPolicy] = {}
        self.archived: List[str] = []
        self.deleted_count: int = 0
        
    def add_policy(self, name: str, retention_days: int,
                    services: List[str] = None, **kwargs) -> RetentionPolicy:
        """Добавление политики"""
        policy = RetentionPolicy(
            policy_id=f"policy_{uuid.uuid4().hex[:8]}",
            name=name,
            retention_days=retention_days,
            services=services or [],
            **kwargs
        )
        self.policies[policy.policy_id] = policy
        return policy
        
    async def apply_policies(self):
        """Применение политик"""
        now = datetime.now()
        
        for log_id, log in list(self.storage.logs.items()):
            policy = self._find_matching_policy(log)
            
            if policy:
                cutoff = now - timedelta(days=policy.retention_days)
                
                if log.timestamp < cutoff:
                    if policy.archive_before_delete:
                        self.archived.append(log_id)
                        
                    self.storage.delete(log_id)
                    self.deleted_count += 1
                    
    def _find_matching_policy(self, log: LogEntry) -> Optional[RetentionPolicy]:
        """Поиск подходящей политики"""
        for policy in self.policies.values():
            if policy.services and log.service not in policy.services:
                continue
            if policy.levels and log.level not in policy.levels:
                continue
            return policy
        return None


class LogAggregationPlatform:
    """Платформа агрегации логов"""
    
    def __init__(self):
        self.parser = LogParser()
        self.storage = LogStorage()
        self.search_engine = LogSearchEngine(self.storage)
        self.pattern_detector = PatternDetector()
        self.alert_engine = AlertEngine()
        self.retention_manager = RetentionManager(self.storage)
        
        self.streams: Dict[str, LogStream] = {}
        
    def create_stream(self, name: str, services: List[str] = None,
                       levels: List[LogLevel] = None) -> LogStream:
        """Создание потока логов"""
        stream = LogStream(
            stream_id=f"stream_{uuid.uuid4().hex[:8]}",
            name=name,
            services=services or [],
            levels=levels or []
        )
        self.streams[stream.stream_id] = stream
        return stream
        
    async def ingest(self, raw: str, service: str, host: str,
                      level: LogLevel = None, **kwargs) -> LogEntry:
        """Приём лога"""
        # Парсинг
        parsed, fields = self.parser.parse(raw)
        
        # Определяем уровень из полей или используем переданный
        if not level:
            level_str = fields.get("level", fields.get("severity", "INFO")).upper()
            try:
                level = LogLevel[level_str]
            except:
                level = LogLevel.INFO
                
        # Создаём запись
        log = LogEntry(
            log_id=f"log_{uuid.uuid4().hex[:8]}",
            message=fields.get("message", raw),
            level=level,
            service=service,
            host=host,
            fields=fields,
            raw=raw,
            parsed=parsed,
            **kwargs
        )
        
        # Сохраняем
        self.storage.store(log)
        
        # Обновляем потоки
        for stream in self.streams.values():
            if self._matches_stream(log, stream):
                stream.buffer.append(log)
                stream.total_logs += 1
                
                # Ограничиваем буфер
                if len(stream.buffer) > stream.buffer_size:
                    stream.buffer = stream.buffer[-stream.buffer_size:]
                    
        # Проверяем алерты
        self.alert_engine.check([log])
        
        return log
        
    def _matches_stream(self, log: LogEntry, stream: LogStream) -> bool:
        """Проверка принадлежности потоку"""
        if stream.services and log.service not in stream.services:
            return False
        if stream.levels and log.level not in stream.levels:
            return False
        return True
        
    def search(self, text: str = "", services: List[str] = None,
                levels: List[LogLevel] = None, **kwargs) -> LogQueryResult:
        """Поиск логов"""
        query = LogQuery(
            query_id=f"query_{uuid.uuid4().hex[:8]}",
            text=text,
            services=services or [],
            levels=levels or [],
            **kwargs
        )
        return self.search_engine.search(query)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        return {
            "total_logs": self.storage.count(),
            "streams": len(self.streams),
            "patterns": len(self.parser.patterns),
            "alerts": len(self.alert_engine.alerts),
            "triggered_alerts": len(self.alert_engine.triggered_alerts),
            "retention_policies": len(self.retention_manager.policies)
        }


# Генератор демо-логов
def generate_demo_log(service: str) -> Tuple[str, LogLevel]:
    """Генерация демо-лога"""
    templates = [
        ("INFO", f"Request processed successfully in {{}}ms", lambda: random.randint(10, 500)),
        ("DEBUG", f"Cache hit for key: user_{{}} ", lambda: random.randint(1000, 9999)),
        ("INFO", f"User {{}} logged in from IP {{}}", lambda: (random.randint(1, 1000), f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}")),
        ("WARN", f"Slow query detected: {{}}ms for query {{}}", lambda: (random.randint(1000, 5000), f"SELECT * FROM users WHERE id = {random.randint(1, 100)}")),
        ("ERROR", f"Failed to connect to database: timeout after {{}}s", lambda: random.randint(30, 120)),
        ("INFO", f"Health check passed, uptime: {{}} hours", lambda: random.randint(1, 720)),
        ("ERROR", f"OutOfMemoryError: Java heap space", lambda: None),
        ("FATAL", f"Service crashed: segmentation fault", lambda: None),
    ]
    
    level_str, template, gen = random.choice(templates)
    
    args = gen() if gen else None
    if args is not None:
        if isinstance(args, tuple):
            message = template.format(*args)
        else:
            message = template.format(args)
    else:
        message = template
        
    level = LogLevel[level_str]
    
    return message, level


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 92: Log Aggregation Platform")
    print("=" * 60)
    
    async def demo():
        platform = LogAggregationPlatform()
        print("✓ Log Aggregation Platform created")
        
        # Создание потоков
        print("\n📊 Creating Log Streams...")
        
        all_logs = platform.create_stream("all_logs")
        errors_only = platform.create_stream(
            "errors_only",
            levels=[LogLevel.ERROR, LogLevel.FATAL]
        )
        api_logs = platform.create_stream(
            "api_logs",
            services=["api-gateway", "auth-service"]
        )
        
        print(f"  ✓ Stream: {all_logs.name}")
        print(f"  ✓ Stream: {errors_only.name} (errors & fatals only)")
        print(f"  ✓ Stream: {api_logs.name} (api & auth services)")
        
        # Паттерны парсинга
        print("\n📝 Log Parsers:")
        
        for name, pattern in platform.parser.patterns.items():
            print(f"  ✓ {name}")
            
        # Создание алертов
        print("\n🚨 Creating Alerts...")
        
        platform.alert_engine.create_alert(
            "High Error Rate",
            "error",
            threshold=5,
            time_window=5,
            severity="critical"
        )
        
        platform.alert_engine.create_alert(
            "Database Connection Issues",
            "failed to connect to database",
            threshold=3,
            time_window=1,
            severity="critical"
        )
        
        platform.alert_engine.create_alert(
            "Out of Memory",
            "OutOfMemoryError",
            threshold=1,
            time_window=1,
            severity="critical"
        )
        
        print(f"  ✓ Created {len(platform.alert_engine.alerts)} alerts")
        
        # Политики ретеншена
        print("\n📦 Creating Retention Policies...")
        
        platform.retention_manager.add_policy(
            "default",
            retention_days=30
        )
        
        platform.retention_manager.add_policy(
            "errors_extended",
            retention_days=90,
            levels=[LogLevel.ERROR, LogLevel.FATAL]
        )
        
        print(f"  ✓ Created {len(platform.retention_manager.policies)} retention policies")
        
        # Генерация логов
        print("\n📥 Ingesting Logs...")
        
        services = ["api-gateway", "auth-service", "user-service", "order-service", "payment-service"]
        hosts = ["server-01", "server-02", "server-03"]
        
        for _ in range(100):
            service = random.choice(services)
            host = random.choice(hosts)
            message, level = generate_demo_log(service)
            
            await platform.ingest(
                message,
                service=service,
                host=host,
                level=level,
                trace_id=uuid.uuid4().hex,
                request_id=f"req_{uuid.uuid4().hex[:8]}"
            )
            
        print(f"  ✓ Ingested {platform.storage.count()} logs")
        
        # Статус потоков
        print("\n📊 Stream Status:")
        
        for stream in platform.streams.values():
            print(f"  {stream.name}: {stream.total_logs} logs")
            
        # Поиск
        print("\n🔍 Log Search Examples...")
        
        # Поиск ошибок
        print("\n  Searching for errors...")
        result = platform.search(levels=[LogLevel.ERROR, LogLevel.FATAL])
        
        print(f"    Found: {result.total_count} logs")
        print(f"    Execution time: {result.execution_time_ms:.2f}ms")
        
        if result.logs:
            print("\n    Sample Errors:")
            for log in result.logs[:3]:
                print(f"      [{log.level.name}] {log.service}: {log.message[:60]}...")
                
        # Поиск по тексту
        print("\n  Searching for 'database'...")
        result = platform.search(text="database")
        print(f"    Found: {result.total_count} logs")
        
        # Поиск по сервису
        print("\n  Searching in api-gateway...")
        result = platform.search(services=["api-gateway"])
        print(f"    Found: {result.total_count} logs")
        
        # Агрегации
        print("\n  Aggregations:")
        result = platform.search()
        
        if result.aggregations.get("by_level"):
            print("\n    By Level:")
            for level, count in sorted(result.aggregations["by_level"].items()):
                bar = "█" * (count // 5)
                print(f"      {level:>6}: {bar} ({count})")
                
        if result.aggregations.get("by_service"):
            print("\n    By Service:")
            for service, count in sorted(result.aggregations["by_service"].items(), key=lambda x: -x[1]):
                bar = "█" * (count // 5)
                print(f"      {service:>15}: {bar} ({count})")
                
        # Анализ паттернов
        print("\n🔬 Pattern Analysis...")
        
        all_logs_list = list(platform.storage.logs.values())
        analysis = platform.pattern_detector.analyze(all_logs_list)
        
        print(f"\n  Total Logs: {analysis['total_logs']}")
        print(f"  Unique Patterns: {analysis['unique_patterns']}")
        print(f"  Error Rate: {analysis['error_rate']:.1%}")
        
        print("\n  Top Patterns:")
        for pattern, count in analysis["top_patterns"][:5]:
            short_pattern = pattern[:50] + "..." if len(pattern) > 50 else pattern
            print(f"    ({count:>3}) {short_pattern}")
            
        # Алерты
        print("\n🚨 Alert Status:")
        
        for alert in platform.alert_engine.alerts.values():
            state_icon = {
                AlertState.PENDING: "⏳",
                AlertState.FIRING: "🔥",
                AlertState.RESOLVED: "✅"
            }.get(alert.state, "?")
            
            print(f"  {state_icon} {alert.name}")
            print(f"     Query: '{alert.query}'")
            print(f"     Threshold: {alert.threshold}")
            print(f"     Current: {alert.current_count}")
            print(f"     State: {alert.state.value}")
            
        if platform.alert_engine.triggered_alerts:
            print("\n  Triggered Alerts:")
            for trigger in platform.alert_engine.triggered_alerts[-5:]:
                print(f"    🔔 {trigger['name']}: {trigger['count']} matches")
                
        # Парсинг примеров
        print("\n📋 Log Parsing Examples...")
        
        examples = [
            '{"level": "INFO", "message": "User logged in", "user_id": 123}',
            '192.168.1.100 - - [15/Jan/2024:10:30:00 +0000] "GET /api/users HTTP/1.1" 200 1234',
            '<14>Jan 15 10:30:00 server-01 nginx: connection accepted'
        ]
        
        for raw in examples:
            parsed, fields = platform.parser.parse(raw)
            print(f"\n  Raw: {raw[:60]}...")
            print(f"  Parsed: {parsed}")
            if fields:
                print(f"  Fields: {dict(list(fields.items())[:3])}...")
                
        # Статистика
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Logs: {stats['total_logs']}")
        print(f"  Streams: {stats['streams']}")
        print(f"  Patterns: {stats['patterns']}")
        print(f"  Alerts: {stats['alerts']}")
        print(f"  Triggered: {stats['triggered_alerts']}")
        print(f"  Retention Policies: {stats['retention_policies']}")
        
        # Dashboard
        print("\n📋 Log Aggregation Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │              Log Aggregation Overview                       │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Logs:     {stats['total_logs']:>6}                               │")
        print(f"  │ Active Streams: {stats['streams']:>6}                               │")
        print(f"  │ Alert Rules:    {stats['alerts']:>6}                               │")
        print(f"  │ Triggered:      {stats['triggered_alerts']:>6}                               │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Log Aggregation Platform initialized!")
    print("=" * 60)
