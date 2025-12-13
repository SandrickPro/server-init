#!/usr/bin/env python3
"""
Server Init - Iteration 48: Log Management & Analytics
Управление логами и аналитика

Функционал:
- Log Aggregation - агрегация логов
- Log Parsing & Enrichment - парсинг и обогащение
- Full-Text Search - полнотекстовый поиск
- Log Analytics - аналитика логов
- Anomaly Detection - обнаружение аномалий
- Alert Rules - правила оповещений
- Log Retention - политики хранения
- Dashboard & Visualization - дашборды и визуализация
"""

import json
import asyncio
import hashlib
import time
import os
import re
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Tuple, Pattern
from enum import Enum
from abc import ABC, abstractmethod
import random
from collections import defaultdict
import uuid


class LogLevel(Enum):
    """Уровень логирования"""
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    FATAL = "fatal"


class LogSource(Enum):
    """Источник логов"""
    APPLICATION = "application"
    CONTAINER = "container"
    KUBERNETES = "kubernetes"
    SYSTEM = "system"
    NETWORK = "network"
    SECURITY = "security"
    DATABASE = "database"
    CUSTOM = "custom"


class AlertSeverity(Enum):
    """Критичность оповещения"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class LogEntry:
    """Запись лога"""
    log_id: str
    timestamp: datetime
    level: LogLevel
    message: str
    
    # Источник
    source: LogSource = LogSource.APPLICATION
    service: str = ""
    host: str = ""
    
    # Метаданные
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Структурированные данные
    fields: Dict[str, Any] = field(default_factory=dict)
    
    # Trace context
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    
    # Raw
    raw: str = ""


@dataclass
class LogStream:
    """Поток логов"""
    stream_id: str
    name: str
    
    # Лейблы
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Статистика
    entries_count: int = 0
    bytes_count: int = 0
    
    # Время
    first_entry_at: Optional[datetime] = None
    last_entry_at: Optional[datetime] = None


@dataclass
class ParseRule:
    """Правило парсинга"""
    rule_id: str
    name: str
    
    # Паттерн
    pattern: str = ""
    pattern_type: str = "regex"  # regex, json, grok
    
    # Извлекаемые поля
    fields: List[str] = field(default_factory=list)
    
    # Условия применения
    source_filter: Optional[str] = None
    level_filter: Optional[LogLevel] = None
    
    # Статистика
    matches: int = 0


@dataclass
class SearchQuery:
    """Поисковый запрос"""
    query_id: str
    query_string: str
    
    # Фильтры
    time_range: Tuple[datetime, datetime] = field(default_factory=lambda: (datetime.now() - timedelta(hours=1), datetime.now()))
    sources: List[LogSource] = field(default_factory=list)
    levels: List[LogLevel] = field(default_factory=list)
    services: List[str] = field(default_factory=list)
    
    # Лимиты
    limit: int = 1000
    
    # Результаты
    results: List[LogEntry] = field(default_factory=list)
    total_hits: int = 0
    execution_time_ms: float = 0.0


@dataclass
class AlertRule:
    """Правило оповещения"""
    rule_id: str
    name: str
    
    # Условие
    query: str = ""
    condition: str = "count"  # count, rate, pattern
    threshold: float = 0.0
    operator: str = ">"  # >, <, >=, <=, ==
    
    # Период
    evaluation_window: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    
    # Оповещение
    severity: AlertSeverity = AlertSeverity.WARNING
    notification_channels: List[str] = field(default_factory=list)
    
    # Состояние
    enabled: bool = True
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0


@dataclass
class Alert:
    """Оповещение"""
    alert_id: str
    rule_id: str
    
    # Данные
    title: str = ""
    message: str = ""
    severity: AlertSeverity = AlertSeverity.WARNING
    
    # Время
    triggered_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    
    # Метрики
    value: float = 0.0
    threshold: float = 0.0
    
    # Статус
    status: str = "firing"  # firing, resolved, acknowledged


@dataclass
class RetentionPolicy:
    """Политика хранения логов"""
    policy_id: str
    name: str
    
    # Условия
    retention_days: int = 30
    source_filter: Optional[LogSource] = None
    level_filter: Optional[LogLevel] = None
    
    # Архивация
    archive_before_delete: bool = False
    archive_destination: str = ""
    
    # Статус
    enabled: bool = True


@dataclass
class Dashboard:
    """Дашборд"""
    dashboard_id: str
    name: str
    
    # Панели
    panels: List[Dict[str, Any]] = field(default_factory=list)
    
    # Настройки
    refresh_interval: int = 30  # seconds
    time_range: str = "1h"
    
    # Метаданные
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class LogParser:
    """Парсер логов"""
    
    def __init__(self):
        self.rules: Dict[str, ParseRule] = {}
        self.grok_patterns: Dict[str, str] = {
            "TIMESTAMP": r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?",
            "LOGLEVEL": r"(?:TRACE|DEBUG|INFO|WARN|ERROR|FATAL)",
            "IP": r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
            "UUID": r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}",
            "NUMBER": r"\d+(?:\.\d+)?",
            "WORD": r"\w+",
            "GREEDYDATA": r".*"
        }
        
    def add_rule(self, rule: ParseRule):
        """Добавление правила"""
        self.rules[rule.rule_id] = rule
        
    def parse(self, raw_log: str, source: LogSource = LogSource.APPLICATION) -> LogEntry:
        """Парсинг лога"""
        log_id = f"log_{uuid.uuid4().hex[:12]}"
        
        # Базовый парсинг
        entry = LogEntry(
            log_id=log_id,
            timestamp=datetime.now(),
            level=LogLevel.INFO,
            message=raw_log,
            source=source,
            raw=raw_log
        )
        
        # Попытка JSON парсинга
        if raw_log.strip().startswith("{"):
            try:
                data = json.loads(raw_log)
                entry.message = data.get("message", data.get("msg", raw_log))
                entry.level = self._parse_level(data.get("level", data.get("severity", "info")))
                entry.fields = {k: v for k, v in data.items() if k not in ["message", "msg", "level", "severity"]}
                
                if "timestamp" in data:
                    entry.timestamp = self._parse_timestamp(data["timestamp"])
                if "service" in data:
                    entry.service = data["service"]
                if "trace_id" in data:
                    entry.trace_id = data["trace_id"]
                    
            except json.JSONDecodeError:
                pass
                
        # Применение правил парсинга
        for rule in self.rules.values():
            if rule.source_filter and rule.source_filter != source.value:
                continue
                
            match = self._apply_rule(rule, raw_log)
            if match:
                entry.fields.update(match)
                rule.matches += 1
                
        return entry
        
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
        if isinstance(ts, (int, float)):
            return datetime.fromtimestamp(ts)
        if isinstance(ts, str):
            try:
                return datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except:
                pass
        return datetime.now()
        
    def _apply_rule(self, rule: ParseRule, raw_log: str) -> Optional[Dict[str, Any]]:
        """Применение правила парсинга"""
        if rule.pattern_type == "regex":
            try:
                match = re.search(rule.pattern, raw_log)
                if match:
                    return match.groupdict()
            except:
                pass
        return None


class LogStore:
    """Хранилище логов"""
    
    def __init__(self):
        self.entries: List[LogEntry] = []
        self.streams: Dict[str, LogStream] = {}
        self.index: Dict[str, List[int]] = defaultdict(list)  # Индекс для поиска
        
    def append(self, entry: LogEntry):
        """Добавление записи"""
        idx = len(self.entries)
        self.entries.append(entry)
        
        # Обновление индекса
        self._update_index(entry, idx)
        
        # Обновление stream
        stream_id = self._get_stream_id(entry)
        if stream_id not in self.streams:
            self.streams[stream_id] = LogStream(
                stream_id=stream_id,
                name=entry.service or "default",
                labels=entry.labels
            )
            
        stream = self.streams[stream_id]
        stream.entries_count += 1
        stream.bytes_count += len(entry.raw)
        stream.last_entry_at = entry.timestamp
        
        if not stream.first_entry_at:
            stream.first_entry_at = entry.timestamp
            
    def _update_index(self, entry: LogEntry, idx: int):
        """Обновление индекса"""
        # Индекс по уровню
        self.index[f"level:{entry.level.value}"].append(idx)
        
        # Индекс по источнику
        self.index[f"source:{entry.source.value}"].append(idx)
        
        # Индекс по сервису
        if entry.service:
            self.index[f"service:{entry.service}"].append(idx)
            
        # Полнотекстовый индекс (упрощённый)
        words = entry.message.lower().split()
        for word in words[:50]:  # Лимит слов
            if len(word) > 2:
                self.index[f"text:{word}"].append(idx)
                
    def _get_stream_id(self, entry: LogEntry) -> str:
        """Получение ID потока"""
        labels = sorted(entry.labels.items())
        label_str = ",".join(f"{k}={v}" for k, v in labels)
        return hashlib.md5(f"{entry.source.value}:{entry.service}:{label_str}".encode()).hexdigest()[:16]
        
    def query(self, query: SearchQuery) -> SearchQuery:
        """Выполнение запроса"""
        start_time = time.time()
        
        results = []
        
        # Фильтрация по индексу
        candidate_indices = None
        
        # Фильтр по уровням
        if query.levels:
            level_indices = set()
            for level in query.levels:
                level_indices.update(self.index.get(f"level:{level.value}", []))
            candidate_indices = level_indices
            
        # Фильтр по источникам
        if query.sources:
            source_indices = set()
            for source in query.sources:
                source_indices.update(self.index.get(f"source:{source.value}", []))
            if candidate_indices is not None:
                candidate_indices &= source_indices
            else:
                candidate_indices = source_indices
                
        # Текстовый поиск
        if query.query_string:
            text_indices = set()
            words = query.query_string.lower().split()
            for word in words:
                text_indices.update(self.index.get(f"text:{word}", []))
            if candidate_indices is not None:
                candidate_indices &= text_indices
            else:
                candidate_indices = text_indices
                
        # Если нет фильтров, берём все
        if candidate_indices is None:
            candidate_indices = set(range(len(self.entries)))
            
        # Фильтрация по времени
        for idx in candidate_indices:
            if idx >= len(self.entries):
                continue
                
            entry = self.entries[idx]
            
            if entry.timestamp < query.time_range[0] or entry.timestamp > query.time_range[1]:
                continue
                
            results.append(entry)
            
            if len(results) >= query.limit:
                break
                
        # Сортировка по времени
        results.sort(key=lambda e: e.timestamp, reverse=True)
        
        query.results = results[:query.limit]
        query.total_hits = len(results)
        query.execution_time_ms = (time.time() - start_time) * 1000
        
        return query
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика хранилища"""
        if not self.entries:
            return {"entries": 0}
            
        level_counts = defaultdict(int)
        source_counts = defaultdict(int)
        
        for entry in self.entries:
            level_counts[entry.level.value] += 1
            source_counts[entry.source.value] += 1
            
        return {
            "entries": len(self.entries),
            "streams": len(self.streams),
            "by_level": dict(level_counts),
            "by_source": dict(source_counts),
            "time_range": {
                "from": min(e.timestamp for e in self.entries).isoformat(),
                "to": max(e.timestamp for e in self.entries).isoformat()
            }
        }


class AnomalyDetector:
    """Детектор аномалий в логах"""
    
    def __init__(self):
        self.baselines: Dict[str, Dict[str, float]] = {}
        self.anomalies: List[Dict[str, Any]] = []
        
    def train_baseline(self, entries: List[LogEntry], window: timedelta = timedelta(hours=1)):
        """Обучение baseline"""
        # Подсчёт по уровням
        level_counts = defaultdict(int)
        error_rate = 0
        
        for entry in entries:
            level_counts[entry.level.value] += 1
            
        total = len(entries)
        
        if total > 0:
            error_rate = (level_counts.get("error", 0) + level_counts.get("fatal", 0)) / total
            
        self.baselines["default"] = {
            "avg_rate": total / (window.total_seconds() / 60),  # logs per minute
            "error_rate": error_rate,
            "level_distribution": {k: v / total for k, v in level_counts.items()}
        }
        
    def detect(self, entries: List[LogEntry], window: timedelta = timedelta(minutes=5)) -> List[Dict[str, Any]]:
        """Обнаружение аномалий"""
        if "default" not in self.baselines:
            return []
            
        baseline = self.baselines["default"]
        detected = []
        
        # Текущие метрики
        level_counts = defaultdict(int)
        for entry in entries:
            level_counts[entry.level.value] += 1
            
        total = len(entries)
        
        if total == 0:
            return []
            
        current_error_rate = (level_counts.get("error", 0) + level_counts.get("fatal", 0)) / total
        current_rate = total / (window.total_seconds() / 60)
        
        # Проверка аномалий
        # Всплеск ошибок
        if current_error_rate > baseline["error_rate"] * 2:
            anomaly = {
                "type": "error_spike",
                "severity": "high",
                "message": f"Error rate increased: {current_error_rate:.2%} vs baseline {baseline['error_rate']:.2%}",
                "detected_at": datetime.now().isoformat()
            }
            detected.append(anomaly)
            
        # Всплеск объёма
        if current_rate > baseline["avg_rate"] * 3:
            anomaly = {
                "type": "volume_spike",
                "severity": "medium",
                "message": f"Log volume increased: {current_rate:.1f}/min vs baseline {baseline['avg_rate']:.1f}/min",
                "detected_at": datetime.now().isoformat()
            }
            detected.append(anomaly)
            
        # Падение объёма (возможная проблема)
        if current_rate < baseline["avg_rate"] * 0.1 and baseline["avg_rate"] > 1:
            anomaly = {
                "type": "volume_drop",
                "severity": "medium",
                "message": f"Log volume dropped: {current_rate:.1f}/min vs baseline {baseline['avg_rate']:.1f}/min",
                "detected_at": datetime.now().isoformat()
            }
            detected.append(anomaly)
            
        self.anomalies.extend(detected)
        return detected


class AlertManager:
    """Менеджер оповещений"""
    
    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.alerts: List[Alert] = []
        self.notification_handlers: Dict[str, Callable] = {}
        
    def add_rule(self, rule: AlertRule):
        """Добавление правила"""
        self.rules[rule.rule_id] = rule
        
    def register_notification_handler(self, channel: str, handler: Callable):
        """Регистрация обработчика оповещений"""
        self.notification_handlers[channel] = handler
        
    async def evaluate(self, store: LogStore) -> List[Alert]:
        """Оценка правил"""
        triggered = []
        
        now = datetime.now()
        
        for rule in self.rules.values():
            if not rule.enabled:
                continue
                
            # Запрос логов для правила
            query = SearchQuery(
                query_id=f"alert_query_{rule.rule_id}",
                query_string=rule.query,
                time_range=(now - rule.evaluation_window, now)
            )
            
            store.query(query)
            
            # Оценка условия
            value = len(query.results)
            
            if rule.condition == "rate":
                value = value / (rule.evaluation_window.total_seconds() / 60)
                
            should_trigger = self._evaluate_condition(value, rule.threshold, rule.operator)
            
            if should_trigger:
                alert = Alert(
                    alert_id=f"alert_{uuid.uuid4().hex[:8]}",
                    rule_id=rule.rule_id,
                    title=f"Alert: {rule.name}",
                    message=f"Rule triggered: {rule.query} {rule.operator} {rule.threshold}",
                    severity=rule.severity,
                    value=value,
                    threshold=rule.threshold
                )
                
                self.alerts.append(alert)
                triggered.append(alert)
                
                rule.last_triggered = now
                rule.trigger_count += 1
                
                # Отправка оповещений
                await self._send_notifications(alert, rule.notification_channels)
                
        return triggered
        
    def _evaluate_condition(self, value: float, threshold: float, operator: str) -> bool:
        """Оценка условия"""
        ops = {
            ">": lambda v, t: v > t,
            "<": lambda v, t: v < t,
            ">=": lambda v, t: v >= t,
            "<=": lambda v, t: v <= t,
            "==": lambda v, t: v == t
        }
        return ops.get(operator, lambda v, t: False)(value, threshold)
        
    async def _send_notifications(self, alert: Alert, channels: List[str]):
        """Отправка оповещений"""
        for channel in channels:
            handler = self.notification_handlers.get(channel)
            if handler:
                try:
                    await handler(alert)
                except:
                    pass
                    
    def get_active_alerts(self) -> List[Alert]:
        """Активные оповещения"""
        return [a for a in self.alerts if a.status == "firing"]
        
    def acknowledge_alert(self, alert_id: str):
        """Подтверждение оповещения"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.status = "acknowledged"
                break
                
    def resolve_alert(self, alert_id: str):
        """Разрешение оповещения"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.status = "resolved"
                alert.resolved_at = datetime.now()
                break


class LogManagementPlatform:
    """Платформа управления логами"""
    
    def __init__(self):
        self.parser = LogParser()
        self.store = LogStore()
        self.anomaly_detector = AnomalyDetector()
        self.alert_manager = AlertManager()
        
        # Retention policies
        self.retention_policies: Dict[str, RetentionPolicy] = {}
        
        # Dashboards
        self.dashboards: Dict[str, Dashboard] = {}
        
    def ingest(self, raw_logs: List[str], source: LogSource = LogSource.APPLICATION):
        """Загрузка логов"""
        for raw in raw_logs:
            entry = self.parser.parse(raw, source)
            self.store.append(entry)
            
    def search(self, query_string: str, 
               time_range: Optional[Tuple[datetime, datetime]] = None,
               **filters) -> SearchQuery:
        """Поиск логов"""
        query = SearchQuery(
            query_id=f"query_{uuid.uuid4().hex[:8]}",
            query_string=query_string,
            time_range=time_range or (datetime.now() - timedelta(hours=1), datetime.now()),
            sources=[LogSource(s) for s in filters.get("sources", [])],
            levels=[LogLevel(l) for l in filters.get("levels", [])],
            services=filters.get("services", []),
            limit=filters.get("limit", 1000)
        )
        
        return self.store.query(query)
        
    def add_parse_rule(self, name: str, pattern: str, 
                        fields: List[str], **kwargs) -> str:
        """Добавление правила парсинга"""
        rule = ParseRule(
            rule_id=f"parse_{uuid.uuid4().hex[:8]}",
            name=name,
            pattern=pattern,
            fields=fields,
            **kwargs
        )
        self.parser.add_rule(rule)
        return rule.rule_id
        
    def add_alert_rule(self, name: str, query: str,
                        threshold: float, **kwargs) -> str:
        """Добавление правила оповещения"""
        rule = AlertRule(
            rule_id=f"alert_{uuid.uuid4().hex[:8]}",
            name=name,
            query=query,
            threshold=threshold,
            **kwargs
        )
        self.alert_manager.add_rule(rule)
        return rule.rule_id
        
    def create_dashboard(self, name: str, panels: List[Dict[str, Any]]) -> str:
        """Создание дашборда"""
        dashboard = Dashboard(
            dashboard_id=f"dash_{uuid.uuid4().hex[:8]}",
            name=name,
            panels=panels
        )
        self.dashboards[dashboard.dashboard_id] = dashboard
        return dashboard.dashboard_id
        
    async def detect_anomalies(self) -> List[Dict[str, Any]]:
        """Обнаружение аномалий"""
        recent_entries = self.store.entries[-1000:]  # Последние 1000 записей
        
        # Обучение baseline если необходимо
        if not self.anomaly_detector.baselines:
            self.anomaly_detector.train_baseline(recent_entries)
            
        return self.anomaly_detector.detect(recent_entries)
        
    async def evaluate_alerts(self) -> List[Alert]:
        """Оценка правил оповещений"""
        return await self.alert_manager.evaluate(self.store)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика платформы"""
        return {
            "store": self.store.get_statistics(),
            "parse_rules": len(self.parser.rules),
            "alert_rules": len(self.alert_manager.rules),
            "active_alerts": len(self.alert_manager.get_active_alerts()),
            "dashboards": len(self.dashboards),
            "anomalies_detected": len(self.anomaly_detector.anomalies)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 48: Log Management & Analytics")
    print("=" * 60)
    
    async def demo():
        # Создание платформы
        platform = LogManagementPlatform()
        print("✓ Log Management Platform created")
        
        # Генерация тестовых логов
        print("\n📝 Ingesting logs...")
        
        sample_logs = []
        
        services = ["api-gateway", "user-service", "order-service", "payment-service"]
        levels = ["info", "info", "info", "info", "warn", "error"]  # Weighted
        
        for i in range(500):
            service = random.choice(services)
            level = random.choice(levels)
            
            if level == "error":
                messages = [
                    "Database connection timeout",
                    "Failed to process request",
                    "Authentication failed",
                    "Invalid input data"
                ]
            elif level == "warn":
                messages = [
                    "High memory usage detected",
                    "Slow query execution",
                    "Rate limit approaching"
                ]
            else:
                messages = [
                    "Request processed successfully",
                    "User logged in",
                    "Order created",
                    "Health check passed"
                ]
                
            log = json.dumps({
                "timestamp": (datetime.now() - timedelta(minutes=random.randint(0, 60))).isoformat(),
                "level": level,
                "service": service,
                "message": random.choice(messages),
                "trace_id": uuid.uuid4().hex[:16],
                "duration_ms": random.randint(10, 500)
            })
            
            sample_logs.append(log)
            
        platform.ingest(sample_logs, LogSource.APPLICATION)
        print(f"  ✓ Ingested {len(sample_logs)} log entries")
        
        # Статистика
        stats = platform.store.get_statistics()
        print(f"\n📊 Log Statistics:")
        print(f"  Total entries: {stats['entries']}")
        print(f"  Streams: {stats['streams']}")
        print(f"  By level: {stats['by_level']}")
        
        # Поиск
        print("\n🔍 Search Examples...")
        
        # Поиск ошибок
        error_query = platform.search(
            query_string="error failed",
            levels=["error"]
        )
        print(f"  Error search: {error_query.total_hits} hits in {error_query.execution_time_ms:.2f}ms")
        
        # Поиск по сервису
        service_query = platform.search(
            query_string="",
            services=["api-gateway"]
        )
        print(f"  Service search: {service_query.total_hits} hits")
        
        # Добавление правила парсинга
        print("\n📋 Parse Rules...")
        
        rule_id = platform.add_parse_rule(
            name="duration-extractor",
            pattern=r'"duration_ms":\s*(\d+)',
            fields=["duration"]
        )
        print(f"  ✓ Added parse rule: {rule_id}")
        
        # Добавление правил оповещений
        print("\n🔔 Alert Rules...")
        
        alert_rule_id = platform.add_alert_rule(
            name="High Error Rate",
            query="error failed",
            threshold=10,
            operator=">",
            severity=AlertSeverity.WARNING,
            notification_channels=["slack", "email"]
        )
        print(f"  ✓ Added alert rule: High Error Rate")
        
        critical_rule_id = platform.add_alert_rule(
            name="Critical Errors",
            query="fatal critical",
            threshold=1,
            operator=">=",
            severity=AlertSeverity.CRITICAL,
            notification_channels=["pagerduty"]
        )
        print(f"  ✓ Added alert rule: Critical Errors")
        
        # Оценка оповещений
        alerts = await platform.evaluate_alerts()
        print(f"\n  Triggered alerts: {len(alerts)}")
        
        for alert in alerts:
            print(f"    [{alert.severity.value}] {alert.title}")
            
        # Обнаружение аномалий
        print("\n🔮 Anomaly Detection...")
        
        anomalies = await platform.detect_anomalies()
        print(f"  Anomalies detected: {len(anomalies)}")
        
        for anomaly in anomalies:
            print(f"    [{anomaly['severity']}] {anomaly['type']}: {anomaly['message']}")
            
        # Создание дашборда
        print("\n📊 Dashboard...")
        
        dashboard_id = platform.create_dashboard(
            name="Application Logs Overview",
            panels=[
                {
                    "title": "Log Volume",
                    "type": "time_series",
                    "query": "*"
                },
                {
                    "title": "Error Rate",
                    "type": "gauge",
                    "query": "level:error"
                },
                {
                    "title": "Top Services",
                    "type": "bar_chart",
                    "query": "*",
                    "group_by": "service"
                },
                {
                    "title": "Recent Errors",
                    "type": "table",
                    "query": "level:error",
                    "limit": 10
                }
            ]
        )
        print(f"  ✓ Created dashboard: {dashboard_id}")
        
        # Итоговая статистика
        final_stats = platform.get_statistics()
        print(f"\n📈 Platform Statistics:")
        print(f"  Log entries: {final_stats['store']['entries']}")
        print(f"  Parse rules: {final_stats['parse_rules']}")
        print(f"  Alert rules: {final_stats['alert_rules']}")
        print(f"  Active alerts: {final_stats['active_alerts']}")
        print(f"  Dashboards: {final_stats['dashboards']}")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Log Management & Analytics Platform initialized!")
    print("=" * 60)
