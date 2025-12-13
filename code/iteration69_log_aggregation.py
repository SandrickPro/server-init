#!/usr/bin/env python3
"""
Server Init - Iteration 69: Log Aggregation & Analysis Platform
Агрегация и анализ логов

Функционал:
- Log Collection - сбор логов
- Log Parsing - парсинг логов
- Log Storage - хранение логов
- Full-Text Search - полнотекстовый поиск
- Log Analytics - аналитика логов
- Alerting - алертинг на основе логов
- Log Retention - политики хранения
- Dashboard - дашборды и визуализация
"""

import json
import asyncio
import re
import gzip
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Pattern
from enum import Enum
from collections import defaultdict
import uuid
import random


class LogLevel(Enum):
    """Уровень лога"""
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    FATAL = "fatal"


class LogSourceType(Enum):
    """Тип источника логов"""
    FILE = "file"
    SYSLOG = "syslog"
    HTTP = "http"
    KAFKA = "kafka"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"


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
    
    # Контент
    message: str = ""
    level: LogLevel = LogLevel.INFO
    
    # Источник
    source: str = ""
    source_type: LogSourceType = LogSourceType.FILE
    
    # Метаданные
    host: str = ""
    service: str = ""
    
    # Структурированные данные
    fields: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    # Время
    timestamp: datetime = field(default_factory=datetime.now)
    ingested_at: datetime = field(default_factory=datetime.now)
    
    # Трассировка
    trace_id: str = ""
    span_id: str = ""


@dataclass
class LogSource:
    """Источник логов"""
    source_id: str
    name: str
    
    # Тип
    source_type: LogSourceType = LogSourceType.FILE
    
    # Конфигурация
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Парсер
    parser: str = ""  # json, regex, grok, etc.
    parser_pattern: str = ""
    
    # Статус
    enabled: bool = True
    last_event_at: Optional[datetime] = None
    
    # Статистика
    events_received: int = 0
    events_failed: int = 0


@dataclass
class Pipeline:
    """Конвейер обработки логов"""
    pipeline_id: str
    name: str
    
    # Этапы
    stages: List[Dict[str, Any]] = field(default_factory=list)
    
    # Фильтры
    source_filter: str = ""  # Какие источники обрабатывать
    
    # Статус
    enabled: bool = True


@dataclass
class LogQuery:
    """Запрос к логам"""
    query_id: str
    
    # Фильтры
    query_string: str = ""
    
    # Временной диапазон
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # Фильтры по полям
    filters: Dict[str, Any] = field(default_factory=dict)
    
    # Пагинация
    limit: int = 100
    offset: int = 0
    
    # Сортировка
    sort_field: str = "timestamp"
    sort_order: str = "desc"


@dataclass
class LogAlert:
    """Алерт на основе логов"""
    alert_id: str
    name: str
    
    # Условие
    query: str = ""
    condition: str = ""  # count > 100, rate > 10/min
    
    # Окно
    window_minutes: int = 5
    
    # Серьёзность
    severity: AlertSeverity = AlertSeverity.MEDIUM
    
    # Уведомления
    notification_channels: List[str] = field(default_factory=list)
    
    # Статус
    enabled: bool = True
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0


@dataclass
class RetentionPolicy:
    """Политика хранения"""
    policy_id: str
    name: str
    
    # Критерии
    index_pattern: str = "*"
    
    # Retention
    retention_days: int = 30
    
    # Архивирование
    archive_after_days: int = 7
    archive_storage: str = ""  # S3, GCS, etc.
    
    # Статус
    enabled: bool = True


@dataclass
class Dashboard:
    """Дашборд"""
    dashboard_id: str
    name: str
    
    # Виджеты
    widgets: List[Dict[str, Any]] = field(default_factory=list)
    
    # Параметры
    time_range: str = "15m"
    auto_refresh: int = 30  # секунд
    
    # Метаданные
    description: str = ""
    tags: List[str] = field(default_factory=list)


class LogParser:
    """Парсер логов"""
    
    def __init__(self):
        self.patterns: Dict[str, Pattern] = {}
        self._init_patterns()
        
    def _init_patterns(self):
        """Инициализация паттернов"""
        # Apache/Nginx combined log format
        self.patterns["combined"] = re.compile(
            r'(?P<client_ip>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] '
            r'"(?P<method>\S+) (?P<path>\S+) (?P<protocol>\S+)" '
            r'(?P<status>\d+) (?P<bytes>\d+)'
        )
        
        # JSON
        self.patterns["json"] = None  # Будем использовать json.loads
        
        # Syslog
        self.patterns["syslog"] = re.compile(
            r'<(?P<priority>\d+)>(?P<timestamp>\S+ \S+ \S+) '
            r'(?P<host>\S+) (?P<program>\S+): (?P<message>.*)'
        )
        
    def parse(self, raw_log: str, parser_type: str = "json") -> Optional[Dict[str, Any]]:
        """Парсинг лога"""
        if parser_type == "json":
            return self._parse_json(raw_log)
        elif parser_type == "combined":
            return self._parse_regex(raw_log, "combined")
        elif parser_type == "syslog":
            return self._parse_regex(raw_log, "syslog")
        elif parser_type == "raw":
            return {"message": raw_log}
            
        return None
        
    def _parse_json(self, raw_log: str) -> Optional[Dict[str, Any]]:
        """Парсинг JSON"""
        try:
            return json.loads(raw_log)
        except:
            return None
            
    def _parse_regex(self, raw_log: str, pattern_name: str) -> Optional[Dict[str, Any]]:
        """Парсинг по regex"""
        pattern = self.patterns.get(pattern_name)
        if not pattern:
            return None
            
        match = pattern.match(raw_log)
        if match:
            return match.groupdict()
            
        return None


class LogStorage:
    """Хранилище логов"""
    
    def __init__(self):
        self.logs: List[LogEntry] = []
        self.indices: Dict[str, Dict[str, List[int]]] = defaultdict(lambda: defaultdict(list))
        # indices[field_name][field_value] = [log_indices]
        
    def store(self, log: LogEntry):
        """Сохранение лога"""
        index = len(self.logs)
        self.logs.append(log)
        
        # Индексируем
        self._index_log(log, index)
        
    def _index_log(self, log: LogEntry, index: int):
        """Индексирование лога"""
        self.indices["level"][log.level.value].append(index)
        self.indices["service"][log.service].append(index)
        self.indices["host"][log.host].append(index)
        self.indices["source"][log.source].append(index)
        
        for tag in log.tags:
            self.indices["tags"][tag].append(index)
            
        # Индексируем час для быстрого поиска по времени
        hour_key = log.timestamp.strftime("%Y-%m-%d-%H")
        self.indices["hour"][hour_key].append(index)
        
    def search(self, query: LogQuery) -> List[LogEntry]:
        """Поиск логов"""
        # Начинаем со всех логов или фильтруем по индексу
        candidate_indices = set(range(len(self.logs)))
        
        # Фильтруем по полям
        for field, value in query.filters.items():
            if field in self.indices and value in self.indices[field]:
                field_indices = set(self.indices[field][value])
                candidate_indices &= field_indices
                
        # Получаем кандидаты
        candidates = [self.logs[i] for i in candidate_indices]
        
        # Фильтруем по времени
        if query.start_time:
            candidates = [l for l in candidates if l.timestamp >= query.start_time]
        if query.end_time:
            candidates = [l for l in candidates if l.timestamp <= query.end_time]
            
        # Полнотекстовый поиск
        if query.query_string:
            candidates = self._fulltext_search(candidates, query.query_string)
            
        # Сортировка
        reverse = query.sort_order == "desc"
        candidates.sort(key=lambda l: getattr(l, query.sort_field, l.timestamp), reverse=reverse)
        
        # Пагинация
        return candidates[query.offset:query.offset + query.limit]
        
    def _fulltext_search(self, logs: List[LogEntry], query_string: str) -> List[LogEntry]:
        """Полнотекстовый поиск"""
        terms = query_string.lower().split()
        results = []
        
        for log in logs:
            message_lower = log.message.lower()
            if all(term in message_lower for term in terms):
                results.append(log)
                
        return results
        
    def aggregate(self, field: str, query: LogQuery = None) -> Dict[str, int]:
        """Агрегация по полю"""
        if query:
            logs = self.search(query)
        else:
            logs = self.logs
            
        counts = defaultdict(int)
        
        for log in logs:
            if field == "level":
                counts[log.level.value] += 1
            elif field == "service":
                counts[log.service] += 1
            elif field == "host":
                counts[log.host] += 1
            elif hasattr(log, field):
                counts[getattr(log, field)] += 1
            elif field in log.fields:
                counts[log.fields[field]] += 1
                
        return dict(counts)
        
    def get_stats(self) -> Dict[str, Any]:
        """Статистика хранилища"""
        return {
            "total_logs": len(self.logs),
            "by_level": self.aggregate("level"),
            "by_service": dict(list(self.aggregate("service").items())[:10]),
            "indices": {k: len(v) for k, v in self.indices.items()}
        }


class LogCollector:
    """Сборщик логов"""
    
    def __init__(self, storage: LogStorage, parser: LogParser):
        self.storage = storage
        self.parser = parser
        self.sources: Dict[str, LogSource] = {}
        self.pipelines: Dict[str, Pipeline] = {}
        
    def add_source(self, name: str, source_type: LogSourceType,
                    parser: str = "json", **kwargs) -> LogSource:
        """Добавление источника"""
        source = LogSource(
            source_id=f"src_{uuid.uuid4().hex[:8]}",
            name=name,
            source_type=source_type,
            parser=parser,
            **kwargs
        )
        
        self.sources[source.source_id] = source
        return source
        
    def add_pipeline(self, name: str, stages: List[Dict[str, Any]],
                      **kwargs) -> Pipeline:
        """Добавление конвейера"""
        pipeline = Pipeline(
            pipeline_id=f"pipe_{uuid.uuid4().hex[:8]}",
            name=name,
            stages=stages,
            **kwargs
        )
        
        self.pipelines[pipeline.pipeline_id] = pipeline
        return pipeline
        
    async def ingest(self, source_id: str, raw_log: str) -> Optional[LogEntry]:
        """Приём лога"""
        source = self.sources.get(source_id)
        
        if not source or not source.enabled:
            return None
            
        # Парсинг
        parsed = self.parser.parse(raw_log, source.parser)
        
        if not parsed:
            source.events_failed += 1
            return None
            
        # Создаём запись
        log = LogEntry(
            log_id=f"log_{uuid.uuid4().hex[:8]}",
            message=parsed.get("message", raw_log),
            level=self._parse_level(parsed.get("level", "info")),
            source=source.name,
            source_type=source.source_type,
            host=parsed.get("host", ""),
            service=parsed.get("service", ""),
            fields=parsed,
            timestamp=self._parse_timestamp(parsed.get("timestamp")),
            trace_id=parsed.get("trace_id", ""),
            span_id=parsed.get("span_id", "")
        )
        
        # Применяем конвейеры
        for pipeline in self.pipelines.values():
            if pipeline.enabled:
                log = await self._apply_pipeline(log, pipeline)
                
        # Сохраняем
        self.storage.store(log)
        
        source.events_received += 1
        source.last_event_at = datetime.now()
        
        return log
        
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
        
    def _parse_timestamp(self, ts: Any) -> datetime:
        """Парсинг timestamp"""
        if ts is None:
            return datetime.now()
            
        if isinstance(ts, datetime):
            return ts
            
        if isinstance(ts, (int, float)):
            return datetime.fromtimestamp(ts)
            
        # Пробуем распарсить строку
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except:
            return datetime.now()
            
    async def _apply_pipeline(self, log: LogEntry, pipeline: Pipeline) -> LogEntry:
        """Применение конвейера"""
        for stage in pipeline.stages:
            stage_type = stage.get("type", "")
            
            if stage_type == "add_field":
                field_name = stage.get("field", "")
                field_value = stage.get("value", "")
                log.fields[field_name] = field_value
                
            elif stage_type == "rename_field":
                old_name = stage.get("old", "")
                new_name = stage.get("new", "")
                if old_name in log.fields:
                    log.fields[new_name] = log.fields.pop(old_name)
                    
            elif stage_type == "add_tag":
                tag = stage.get("tag", "")
                if tag:
                    log.tags.append(tag)
                    
            elif stage_type == "geoip":
                # Симуляция GeoIP
                ip_field = stage.get("source", "client_ip")
                if ip_field in log.fields:
                    log.fields["geo"] = {
                        "country": "US",
                        "city": "New York",
                        "location": {"lat": 40.7, "lon": -74.0}
                    }
                    
        return log


class AlertEngine:
    """Движок алертинга"""
    
    def __init__(self, storage: LogStorage):
        self.storage = storage
        self.alerts: Dict[str, LogAlert] = {}
        self.triggered_alerts: List[Dict[str, Any]] = []
        
    def create_alert(self, name: str, query: str, condition: str,
                      **kwargs) -> LogAlert:
        """Создание алерта"""
        alert = LogAlert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            name=name,
            query=query,
            condition=condition,
            **kwargs
        )
        
        self.alerts[alert.alert_id] = alert
        return alert
        
    async def evaluate_alerts(self):
        """Проверка всех алертов"""
        for alert in self.alerts.values():
            if not alert.enabled:
                continue
                
            triggered = await self._evaluate_alert(alert)
            
            if triggered:
                alert.last_triggered = datetime.now()
                alert.trigger_count += 1
                
                self.triggered_alerts.append({
                    "alert_id": alert.alert_id,
                    "alert_name": alert.name,
                    "triggered_at": datetime.now(),
                    "severity": alert.severity.value
                })
                
    async def _evaluate_alert(self, alert: LogAlert) -> bool:
        """Оценка алерта"""
        now = datetime.now()
        window_start = now - timedelta(minutes=alert.window_minutes)
        
        # Выполняем запрос
        query = LogQuery(
            query_id="temp",
            query_string=alert.query,
            start_time=window_start,
            end_time=now
        )
        
        results = self.storage.search(query)
        count = len(results)
        
        # Парсим условие
        if ">" in alert.condition:
            parts = alert.condition.split(">")
            threshold = int(parts[1].strip())
            return count > threshold
        elif "<" in alert.condition:
            parts = alert.condition.split("<")
            threshold = int(parts[1].strip())
            return count < threshold
            
        return False


class AnalyticsEngine:
    """Движок аналитики"""
    
    def __init__(self, storage: LogStorage):
        self.storage = storage
        
    def get_log_volume(self, interval_minutes: int = 5,
                        hours: int = 24) -> List[Dict[str, Any]]:
        """Объём логов по времени"""
        now = datetime.now()
        start = now - timedelta(hours=hours)
        
        intervals = []
        current = start
        
        while current < now:
            interval_end = current + timedelta(minutes=interval_minutes)
            
            query = LogQuery(
                query_id="temp",
                start_time=current,
                end_time=interval_end,
                limit=10000
            )
            
            count = len(self.storage.search(query))
            
            intervals.append({
                "timestamp": current.isoformat(),
                "count": count
            })
            
            current = interval_end
            
        return intervals
        
    def get_error_rate(self, service: str = None,
                        window_minutes: int = 60) -> Dict[str, Any]:
        """Частота ошибок"""
        now = datetime.now()
        start = now - timedelta(minutes=window_minutes)
        
        filters = {}
        if service:
            filters["service"] = service
            
        all_query = LogQuery(query_id="temp", start_time=start, filters=filters, limit=100000)
        error_filters = {**filters, "level": "error"}
        error_query = LogQuery(query_id="temp", start_time=start, filters=error_filters, limit=100000)
        
        total = len(self.storage.search(all_query))
        errors = len(self.storage.search(error_query))
        
        return {
            "total_logs": total,
            "error_count": errors,
            "error_rate": errors / max(total, 1) * 100,
            "window_minutes": window_minutes
        }
        
    def get_top_errors(self, limit: int = 10,
                        window_minutes: int = 60) -> List[Dict[str, Any]]:
        """Топ ошибок"""
        now = datetime.now()
        start = now - timedelta(minutes=window_minutes)
        
        query = LogQuery(
            query_id="temp",
            start_time=start,
            filters={"level": "error"},
            limit=10000
        )
        
        errors = self.storage.search(query)
        
        # Группируем по сообщению
        error_counts = defaultdict(int)
        for log in errors:
            # Берём первые 100 символов как ключ
            key = log.message[:100]
            error_counts[key] += 1
            
        # Сортируем
        sorted_errors = sorted(error_counts.items(), key=lambda x: -x[1])[:limit]
        
        return [{"message": msg, "count": count} for msg, count in sorted_errors]


class LogAggregationPlatform:
    """Платформа агрегации логов"""
    
    def __init__(self):
        self.parser = LogParser()
        self.storage = LogStorage()
        self.collector = LogCollector(self.storage, self.parser)
        self.alert_engine = AlertEngine(self.storage)
        self.analytics = AnalyticsEngine(self.storage)
        
        self.retention_policies: Dict[str, RetentionPolicy] = {}
        self.dashboards: Dict[str, Dashboard] = {}
        
    def add_source(self, name: str, source_type: LogSourceType,
                    **kwargs) -> LogSource:
        """Добавление источника"""
        return self.collector.add_source(name, source_type, **kwargs)
        
    async def ingest(self, source_id: str, raw_log: str) -> Optional[LogEntry]:
        """Приём лога"""
        return await self.collector.ingest(source_id, raw_log)
        
    def search(self, query_string: str = "", start_time: datetime = None,
                end_time: datetime = None, filters: Dict[str, Any] = None,
                limit: int = 100) -> List[LogEntry]:
        """Поиск логов"""
        query = LogQuery(
            query_id=f"q_{uuid.uuid4().hex[:8]}",
            query_string=query_string,
            start_time=start_time,
            end_time=end_time,
            filters=filters or {},
            limit=limit
        )
        
        return self.storage.search(query)
        
    def create_alert(self, name: str, query: str, condition: str,
                      **kwargs) -> LogAlert:
        """Создание алерта"""
        return self.alert_engine.create_alert(name, query, condition, **kwargs)
        
    def create_retention_policy(self, name: str, index_pattern: str,
                                  retention_days: int, **kwargs) -> RetentionPolicy:
        """Создание политики хранения"""
        policy = RetentionPolicy(
            policy_id=f"ret_{uuid.uuid4().hex[:8]}",
            name=name,
            index_pattern=index_pattern,
            retention_days=retention_days,
            **kwargs
        )
        
        self.retention_policies[policy.policy_id] = policy
        return policy
        
    def create_dashboard(self, name: str, widgets: List[Dict[str, Any]],
                          **kwargs) -> Dashboard:
        """Создание дашборда"""
        dashboard = Dashboard(
            dashboard_id=f"dash_{uuid.uuid4().hex[:8]}",
            name=name,
            widgets=widgets,
            **kwargs
        )
        
        self.dashboards[dashboard.dashboard_id] = dashboard
        return dashboard
        
    def get_stats(self) -> Dict[str, Any]:
        """Статистика платформы"""
        storage_stats = self.storage.get_stats()
        
        return {
            "sources": len(self.collector.sources),
            "pipelines": len(self.collector.pipelines),
            "logs": storage_stats["total_logs"],
            "by_level": storage_stats["by_level"],
            "alerts": len(self.alert_engine.alerts),
            "triggered_alerts": len(self.alert_engine.triggered_alerts),
            "retention_policies": len(self.retention_policies),
            "dashboards": len(self.dashboards)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 69: Log Aggregation Platform")
    print("=" * 60)
    
    async def demo():
        platform = LogAggregationPlatform()
        print("✓ Log Aggregation Platform created")
        
        # Добавление источников
        print("\n📥 Adding log sources...")
        
        app_source = platform.add_source(
            name="app-logs",
            source_type=LogSourceType.FILE,
            parser="json",
            config={"path": "/var/log/app/*.log"}
        )
        print(f"  ✓ Source: {app_source.name} ({app_source.source_type.value})")
        
        nginx_source = platform.add_source(
            name="nginx-access",
            source_type=LogSourceType.FILE,
            parser="combined",
            config={"path": "/var/log/nginx/access.log"}
        )
        print(f"  ✓ Source: {nginx_source.name}")
        
        k8s_source = platform.add_source(
            name="kubernetes",
            source_type=LogSourceType.KUBERNETES,
            parser="json",
            config={"namespace": "production"}
        )
        print(f"  ✓ Source: {k8s_source.name}")
        
        # Добавление конвейера
        print("\n🔧 Creating pipeline...")
        
        pipeline = platform.collector.add_pipeline(
            name="enrichment",
            stages=[
                {"type": "add_field", "field": "environment", "value": "production"},
                {"type": "add_tag", "tag": "processed"},
                {"type": "geoip", "source": "client_ip"}
            ]
        )
        print(f"  ✓ Pipeline: {pipeline.name} ({len(pipeline.stages)} stages)")
        
        # Приём логов
        print("\n📝 Ingesting logs...")
        
        services = ["api-gateway", "user-service", "payment-service", "auth-service"]
        hosts = ["prod-1", "prod-2", "prod-3"]
        levels = ["info", "info", "info", "info", "warn", "error"]
        
        messages = [
            "Request processed successfully",
            "User authentication successful",
            "Database query executed",
            "Cache hit for key",
            "Slow query detected",
            "Connection timeout to upstream",
            "Failed to process payment",
            "Rate limit exceeded",
            "Invalid request format",
            "Service health check passed"
        ]
        
        for i in range(200):
            log_data = {
                "timestamp": (datetime.now() - timedelta(minutes=random.randint(0, 60))).isoformat(),
                "level": random.choice(levels),
                "service": random.choice(services),
                "host": random.choice(hosts),
                "message": random.choice(messages),
                "request_id": f"req_{uuid.uuid4().hex[:8]}",
                "duration_ms": random.randint(5, 500),
                "trace_id": f"trace_{uuid.uuid4().hex[:16]}"
            }
            
            await platform.ingest(app_source.source_id, json.dumps(log_data))
            
        print(f"  ✓ Ingested 200 logs")
        
        # Поиск логов
        print("\n🔍 Searching logs...")
        
        # По уровню
        error_logs = platform.search(filters={"level": "error"}, limit=10)
        print(f"  Error logs: {len(error_logs)}")
        
        # По сервису
        api_logs = platform.search(filters={"service": "api-gateway"}, limit=10)
        print(f"  API Gateway logs: {len(api_logs)}")
        
        # Полнотекстовый поиск
        timeout_logs = platform.search(query_string="timeout", limit=10)
        print(f"  Logs with 'timeout': {len(timeout_logs)}")
        
        # За последние 30 минут
        recent_logs = platform.search(
            start_time=datetime.now() - timedelta(minutes=30),
            limit=100
        )
        print(f"  Recent logs (30min): {len(recent_logs)}")
        
        # Агрегация
        print("\n📊 Log Aggregation:")
        
        by_level = platform.storage.aggregate("level")
        print(f"  By level: {by_level}")
        
        by_service = platform.storage.aggregate("service")
        print(f"  By service: {by_service}")
        
        # Аналитика
        print("\n📈 Analytics:")
        
        error_rate = platform.analytics.get_error_rate(window_minutes=60)
        print(f"  Error rate: {error_rate['error_rate']:.2f}%")
        print(f"  Total logs: {error_rate['total_logs']}, Errors: {error_rate['error_count']}")
        
        top_errors = platform.analytics.get_top_errors(limit=5)
        if top_errors:
            print(f"  Top errors:")
            for err in top_errors[:3]:
                print(f"    - {err['message'][:50]}... ({err['count']})")
                
        # Алерты
        print("\n🚨 Creating alerts...")
        
        error_alert = platform.create_alert(
            name="High Error Rate",
            query="error",
            condition="count > 10",
            window_minutes=5,
            severity=AlertSeverity.HIGH,
            notification_channels=["slack", "pagerduty"]
        )
        print(f"  ✓ Alert: {error_alert.name}")
        
        timeout_alert = platform.create_alert(
            name="Connection Timeouts",
            query="timeout",
            condition="count > 5",
            window_minutes=10,
            severity=AlertSeverity.MEDIUM
        )
        print(f"  ✓ Alert: {timeout_alert.name}")
        
        # Проверка алертов
        await platform.alert_engine.evaluate_alerts()
        print(f"  Triggered alerts: {len(platform.alert_engine.triggered_alerts)}")
        
        # Политики хранения
        print("\n📦 Retention Policies:")
        
        policy = platform.create_retention_policy(
            name="default",
            index_pattern="logs-*",
            retention_days=30,
            archive_after_days=7,
            archive_storage="s3://logs-archive"
        )
        print(f"  ✓ Policy: {policy.name} (retain {policy.retention_days} days)")
        
        # Дашборд
        print("\n📊 Creating Dashboard...")
        
        dashboard = platform.create_dashboard(
            name="Operations Overview",
            widgets=[
                {"type": "log_volume", "title": "Log Volume", "interval": "5m"},
                {"type": "pie_chart", "title": "Logs by Level", "field": "level"},
                {"type": "bar_chart", "title": "Logs by Service", "field": "service"},
                {"type": "table", "title": "Recent Errors", "query": "level:error", "limit": 10},
                {"type": "metric", "title": "Error Rate", "metric": "error_rate"}
            ],
            time_range="1h",
            auto_refresh=30,
            description="Main operations dashboard",
            tags=["operations", "monitoring"]
        )
        print(f"  ✓ Dashboard: {dashboard.name} ({len(dashboard.widgets)} widgets)")
        
        # Статистика источников
        print("\n📡 Source Statistics:")
        for source in platform.collector.sources.values():
            print(f"  {source.name}:")
            print(f"    Received: {source.events_received}")
            print(f"    Failed: {source.events_failed}")
            
        # Общая статистика
        print("\n📊 Platform Statistics:")
        stats = platform.get_stats()
        print(f"  Sources: {stats['sources']}")
        print(f"  Pipelines: {stats['pipelines']}")
        print(f"  Total Logs: {stats['logs']}")
        print(f"  By Level: {stats['by_level']}")
        print(f"  Alerts: {stats['alerts']}")
        print(f"  Dashboards: {stats['dashboards']}")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Log Aggregation Platform initialized!")
    print("=" * 60)
