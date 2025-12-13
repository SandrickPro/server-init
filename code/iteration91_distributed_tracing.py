#!/usr/bin/env python3
"""
Server Init - Iteration 91: Distributed Tracing Platform
Платформа распределённой трассировки

Функционал:
- Span Management - управление спанами
- Context Propagation - распространение контекста
- Trace Aggregation - агрегация трейсов
- Service Map - карта сервисов
- Latency Analysis - анализ задержек
- Error Tracking - отслеживание ошибок
- Performance Insights - инсайты производительности
- Root Cause Analysis - анализ причин
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Tuple
from enum import Enum
from collections import defaultdict
import uuid
import random


class SpanKind(Enum):
    """Тип спана"""
    INTERNAL = "internal"
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"


class SpanStatus(Enum):
    """Статус спана"""
    UNSET = "unset"
    OK = "ok"
    ERROR = "error"


class AlertSeverity(Enum):
    """Серьёзность алерта"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class SpanContext:
    """Контекст спана"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    trace_flags: int = 0
    baggage: Dict[str, str] = field(default_factory=dict)


@dataclass
class SpanEvent:
    """Событие спана"""
    name: str
    timestamp: datetime = field(default_factory=datetime.now)
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SpanLink:
    """Связь между спанами"""
    context: SpanContext
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Span:
    """Спан трассировки"""
    context: SpanContext
    name: str
    kind: SpanKind = SpanKind.INTERNAL
    status: SpanStatus = SpanStatus.UNSET
    
    # Время
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    # Атрибуты
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    # События
    events: List[SpanEvent] = field(default_factory=list)
    
    # Связи
    links: List[SpanLink] = field(default_factory=list)
    
    # Сервис
    service_name: str = ""
    service_version: str = ""
    
    # Ресурс
    resource: Dict[str, str] = field(default_factory=dict)
    
    # Ошибка
    error_message: str = ""
    exception_type: str = ""
    stack_trace: str = ""
    
    @property
    def duration_ms(self) -> float:
        """Длительность в мс"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0


@dataclass
class Trace:
    """Трейс (коллекция спанов)"""
    trace_id: str
    spans: List[Span] = field(default_factory=list)
    
    # Метаданные
    root_span: Optional[Span] = None
    service_count: int = 0
    span_count: int = 0
    
    # Время
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @property
    def duration_ms(self) -> float:
        """Общая длительность"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0
    
    @property
    def has_errors(self) -> bool:
        """Есть ли ошибки"""
        return any(span.status == SpanStatus.ERROR for span in self.spans)


@dataclass
class ServiceInfo:
    """Информация о сервисе"""
    service_name: str
    version: str = ""
    
    # Статистика
    total_spans: int = 0
    error_count: int = 0
    
    # Задержки
    avg_latency_ms: float = 0
    p50_latency_ms: float = 0
    p95_latency_ms: float = 0
    p99_latency_ms: float = 0
    
    # Связи
    calls_to: Dict[str, int] = field(default_factory=dict)  # service -> count
    called_by: Dict[str, int] = field(default_factory=dict)
    
    # Операции
    operations: Dict[str, int] = field(default_factory=dict)


@dataclass
class ServiceEdge:
    """Связь между сервисами"""
    source: str
    target: str
    
    # Статистика
    call_count: int = 0
    error_count: int = 0
    avg_latency_ms: float = 0
    
    # Протокол
    protocol: str = "http"


@dataclass
class LatencyHistogram:
    """Гистограмма задержек"""
    buckets: Dict[str, int] = field(default_factory=dict)
    total_count: int = 0
    sum_ms: float = 0
    
    @property
    def avg_ms(self) -> float:
        return self.sum_ms / self.total_count if self.total_count > 0 else 0


@dataclass
class TracingAlert:
    """Алерт трассировки"""
    alert_id: str
    severity: AlertSeverity = AlertSeverity.WARNING
    title: str = ""
    description: str = ""
    
    # Связанный трейс
    trace_id: str = ""
    span_id: str = ""
    service: str = ""
    
    # Время
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Статус
    acknowledged: bool = False


class SpanProcessor:
    """Процессор спанов"""
    
    def __init__(self):
        self.processors: List[Callable] = []
        
    def add_processor(self, processor: Callable):
        """Добавление процессора"""
        self.processors.append(processor)
        
    async def process(self, span: Span) -> Span:
        """Обработка спана"""
        for processor in self.processors:
            if asyncio.iscoroutinefunction(processor):
                span = await processor(span)
            else:
                span = processor(span)
        return span


class ContextPropagator:
    """Распространение контекста"""
    
    TRACE_HEADER = "traceparent"
    BAGGAGE_HEADER = "baggage"
    
    def inject(self, context: SpanContext) -> Dict[str, str]:
        """Внедрение контекста в заголовки"""
        headers = {}
        
        # W3C Trace Context format
        trace_parent = f"00-{context.trace_id}-{context.span_id}-{context.trace_flags:02x}"
        headers[self.TRACE_HEADER] = trace_parent
        
        # Baggage
        if context.baggage:
            baggage = ",".join(f"{k}={v}" for k, v in context.baggage.items())
            headers[self.BAGGAGE_HEADER] = baggage
            
        return headers
        
    def extract(self, headers: Dict[str, str]) -> Optional[SpanContext]:
        """Извлечение контекста из заголовков"""
        trace_parent = headers.get(self.TRACE_HEADER)
        if not trace_parent:
            return None
            
        try:
            parts = trace_parent.split("-")
            if len(parts) < 4:
                return None
                
            context = SpanContext(
                trace_id=parts[1],
                span_id=parts[2],
                trace_flags=int(parts[3], 16)
            )
            
            # Baggage
            baggage = headers.get(self.BAGGAGE_HEADER, "")
            if baggage:
                for item in baggage.split(","):
                    if "=" in item:
                        k, v = item.split("=", 1)
                        context.baggage[k.strip()] = v.strip()
                        
            return context
            
        except Exception:
            return None


class Tracer:
    """Трейсер"""
    
    def __init__(self, service_name: str, version: str = "1.0.0"):
        self.service_name = service_name
        self.version = version
        self.span_processor = SpanProcessor()
        self.propagator = ContextPropagator()
        
        # Текущие спаны
        self.active_spans: Dict[str, Span] = {}
        
        # Callback для завершения
        self.on_span_end: Optional[Callable] = None
        
    def start_span(self, name: str, parent: Optional[SpanContext] = None,
                    kind: SpanKind = SpanKind.INTERNAL,
                    attributes: Dict[str, Any] = None) -> Span:
        """Создание спана"""
        # Генерируем IDs
        trace_id = parent.trace_id if parent else uuid.uuid4().hex
        span_id = uuid.uuid4().hex[:16]
        parent_span_id = parent.span_id if parent else None
        
        context = SpanContext(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            baggage=parent.baggage.copy() if parent else {}
        )
        
        span = Span(
            context=context,
            name=name,
            kind=kind,
            service_name=self.service_name,
            service_version=self.version,
            attributes=attributes or {}
        )
        
        self.active_spans[span_id] = span
        return span
        
    async def end_span(self, span: Span, status: SpanStatus = SpanStatus.OK,
                        error: Exception = None):
        """Завершение спана"""
        span.end_time = datetime.now()
        span.status = status
        
        if error:
            span.status = SpanStatus.ERROR
            span.error_message = str(error)
            span.exception_type = type(error).__name__
            
        # Обработка
        span = await self.span_processor.process(span)
        
        # Callback
        if self.on_span_end:
            if asyncio.iscoroutinefunction(self.on_span_end):
                await self.on_span_end(span)
            else:
                self.on_span_end(span)
                
        # Удаляем из активных
        self.active_spans.pop(span.context.span_id, None)
        
        return span


class TraceAggregator:
    """Агрегатор трейсов"""
    
    def __init__(self):
        self.traces: Dict[str, Trace] = {}
        self.spans_buffer: Dict[str, List[Span]] = defaultdict(list)
        
    def add_span(self, span: Span):
        """Добавление спана"""
        trace_id = span.context.trace_id
        self.spans_buffer[trace_id].append(span)
        
    def build_trace(self, trace_id: str) -> Optional[Trace]:
        """Построение трейса"""
        spans = self.spans_buffer.get(trace_id, [])
        if not spans:
            return None
            
        trace = Trace(trace_id=trace_id, spans=spans)
        
        # Находим root span
        for span in spans:
            if span.context.parent_span_id is None:
                trace.root_span = span
                break
                
        # Статистика
        trace.span_count = len(spans)
        trace.service_count = len(set(s.service_name for s in spans))
        
        # Время
        if spans:
            trace.start_time = min(s.start_time for s in spans)
            end_times = [s.end_time for s in spans if s.end_time]
            if end_times:
                trace.end_time = max(end_times)
                
        self.traces[trace_id] = trace
        return trace
        
    def get_trace(self, trace_id: str) -> Optional[Trace]:
        """Получение трейса"""
        if trace_id not in self.traces:
            return self.build_trace(trace_id)
        return self.traces.get(trace_id)


class ServiceMap:
    """Карта сервисов"""
    
    def __init__(self):
        self.services: Dict[str, ServiceInfo] = {}
        self.edges: Dict[str, ServiceEdge] = {}  # "source->target" -> edge
        
    def update_from_span(self, span: Span):
        """Обновление карты из спана"""
        # Обновляем информацию о сервисе
        if span.service_name not in self.services:
            self.services[span.service_name] = ServiceInfo(
                service_name=span.service_name,
                version=span.service_version
            )
            
        service = self.services[span.service_name]
        service.total_spans += 1
        
        if span.status == SpanStatus.ERROR:
            service.error_count += 1
            
        # Обновляем операции
        service.operations[span.name] = service.operations.get(span.name, 0) + 1
        
    def add_call(self, source: str, target: str, latency_ms: float, error: bool = False):
        """Добавление вызова"""
        edge_key = f"{source}->{target}"
        
        if edge_key not in self.edges:
            self.edges[edge_key] = ServiceEdge(source=source, target=target)
            
        edge = self.edges[edge_key]
        edge.call_count += 1
        
        if error:
            edge.error_count += 1
            
        # Обновляем avg latency (простое скользящее среднее)
        edge.avg_latency_ms = (edge.avg_latency_ms * (edge.call_count - 1) + latency_ms) / edge.call_count
        
        # Обновляем связи в сервисах
        if source in self.services:
            self.services[source].calls_to[target] = self.services[source].calls_to.get(target, 0) + 1
        if target in self.services:
            self.services[target].called_by[source] = self.services[target].called_by.get(source, 0) + 1


class LatencyAnalyzer:
    """Анализатор задержек"""
    
    def __init__(self):
        self.histograms: Dict[str, LatencyHistogram] = {}
        self.latencies: Dict[str, List[float]] = defaultdict(list)
        
    def record(self, service: str, operation: str, latency_ms: float):
        """Запись задержки"""
        key = f"{service}:{operation}"
        self.latencies[key].append(latency_ms)
        
        # Обновляем гистограмму
        if key not in self.histograms:
            self.histograms[key] = LatencyHistogram()
            
        histogram = self.histograms[key]
        histogram.total_count += 1
        histogram.sum_ms += latency_ms
        
        # Bucket
        bucket = self._get_bucket(latency_ms)
        histogram.buckets[bucket] = histogram.buckets.get(bucket, 0) + 1
        
    def _get_bucket(self, latency_ms: float) -> str:
        """Определение bucket для задержки"""
        if latency_ms < 10:
            return "0-10ms"
        elif latency_ms < 50:
            return "10-50ms"
        elif latency_ms < 100:
            return "50-100ms"
        elif latency_ms < 500:
            return "100-500ms"
        elif latency_ms < 1000:
            return "500ms-1s"
        else:
            return ">1s"
            
    def get_percentiles(self, service: str, operation: str) -> Dict[str, float]:
        """Получение перцентилей"""
        key = f"{service}:{operation}"
        values = sorted(self.latencies.get(key, []))
        
        if not values:
            return {}
            
        def percentile(p: float) -> float:
            idx = int(len(values) * p / 100)
            return values[min(idx, len(values) - 1)]
            
        return {
            "p50": percentile(50),
            "p75": percentile(75),
            "p90": percentile(90),
            "p95": percentile(95),
            "p99": percentile(99)
        }


class RootCauseAnalyzer:
    """Анализатор корневых причин"""
    
    def analyze_error_trace(self, trace: Trace) -> Dict[str, Any]:
        """Анализ трейса с ошибкой"""
        analysis = {
            "root_cause_span": None,
            "error_path": [],
            "affected_services": set(),
            "suggestions": []
        }
        
        # Находим первый спан с ошибкой
        error_spans = [s for s in trace.spans if s.status == SpanStatus.ERROR]
        
        if not error_spans:
            return analysis
            
        # Сортируем по времени
        error_spans.sort(key=lambda s: s.start_time)
        root_cause = error_spans[0]
        analysis["root_cause_span"] = root_cause
        
        # Путь ошибки
        analysis["error_path"] = self._build_error_path(trace, root_cause)
        
        # Затронутые сервисы
        analysis["affected_services"] = set(s.service_name for s in error_spans)
        
        # Предложения
        analysis["suggestions"] = self._generate_suggestions(root_cause)
        
        return analysis
        
    def _build_error_path(self, trace: Trace, root_span: Span) -> List[str]:
        """Построение пути ошибки"""
        path = [f"{root_span.service_name}:{root_span.name}"]
        
        # Находим родительские спаны
        span_map = {s.context.span_id: s for s in trace.spans}
        current = root_span
        
        while current.context.parent_span_id:
            parent = span_map.get(current.context.parent_span_id)
            if parent:
                path.insert(0, f"{parent.service_name}:{parent.name}")
                current = parent
            else:
                break
                
        return path
        
    def _generate_suggestions(self, span: Span) -> List[str]:
        """Генерация предложений"""
        suggestions = []
        
        if "timeout" in span.error_message.lower():
            suggestions.append("Consider increasing timeout settings")
            suggestions.append("Check network latency between services")
            
        if "connection" in span.error_message.lower():
            suggestions.append("Verify service connectivity")
            suggestions.append("Check connection pool settings")
            
        if span.duration_ms > 1000:
            suggestions.append("Operation took too long, consider optimization")
            
        if not suggestions:
            suggestions.append("Review logs for more details")
            suggestions.append("Check service health status")
            
        return suggestions


class AlertManager:
    """Менеджер алертов"""
    
    def __init__(self):
        self.alerts: List[TracingAlert] = []
        self.rules: List[Dict[str, Any]] = []
        
    def add_rule(self, name: str, condition: Callable, severity: AlertSeverity):
        """Добавление правила"""
        self.rules.append({
            "name": name,
            "condition": condition,
            "severity": severity
        })
        
    def check_span(self, span: Span) -> Optional[TracingAlert]:
        """Проверка спана на алерты"""
        for rule in self.rules:
            if rule["condition"](span):
                alert = TracingAlert(
                    alert_id=f"alert_{uuid.uuid4().hex[:8]}",
                    severity=rule["severity"],
                    title=rule["name"],
                    description=f"Alert triggered for span {span.name}",
                    trace_id=span.context.trace_id,
                    span_id=span.context.span_id,
                    service=span.service_name
                )
                self.alerts.append(alert)
                return alert
                
        return None


class DistributedTracingPlatform:
    """Платформа распределённой трассировки"""
    
    def __init__(self):
        self.tracers: Dict[str, Tracer] = {}
        self.aggregator = TraceAggregator()
        self.service_map = ServiceMap()
        self.latency_analyzer = LatencyAnalyzer()
        self.root_cause_analyzer = RootCauseAnalyzer()
        self.alert_manager = AlertManager()
        
        # Настройка правил алертов
        self._setup_default_alerts()
        
    def _setup_default_alerts(self):
        """Настройка алертов по умолчанию"""
        # Высокая задержка
        self.alert_manager.add_rule(
            "High Latency",
            lambda span: span.duration_ms > 5000,
            AlertSeverity.WARNING
        )
        
        # Ошибки
        self.alert_manager.add_rule(
            "Span Error",
            lambda span: span.status == SpanStatus.ERROR,
            AlertSeverity.ERROR
        )
        
    def create_tracer(self, service_name: str, version: str = "1.0.0") -> Tracer:
        """Создание трейсера для сервиса"""
        tracer = Tracer(service_name, version)
        
        # Callback для обработки завершённых спанов
        async def on_span_end(span: Span):
            self.aggregator.add_span(span)
            self.service_map.update_from_span(span)
            
            if span.duration_ms > 0:
                self.latency_analyzer.record(
                    span.service_name,
                    span.name,
                    span.duration_ms
                )
                
            self.alert_manager.check_span(span)
            
        tracer.on_span_end = on_span_end
        self.tracers[service_name] = tracer
        return tracer
        
    async def simulate_distributed_call(self, services: List[str],
                                          operations: List[str]) -> str:
        """Симуляция распределённого вызова"""
        # Создаём трейсеры если нужно
        for service in services:
            if service not in self.tracers:
                self.create_tracer(service)
                
        trace_id = None
        parent_context = None
        
        for i, (service, operation) in enumerate(zip(services, operations)):
            tracer = self.tracers[service]
            
            # Создаём спан
            span = tracer.start_span(
                operation,
                parent=parent_context,
                kind=SpanKind.SERVER if i > 0 else SpanKind.INTERNAL,
                attributes={
                    "http.method": "GET",
                    "http.url": f"http://{service}/{operation}"
                }
            )
            
            if trace_id is None:
                trace_id = span.context.trace_id
                
            # Симуляция работы
            await asyncio.sleep(random.uniform(0.01, 0.1))
            
            # Случайная ошибка
            error = None
            if random.random() < 0.1:
                error = Exception(f"Simulated error in {service}:{operation}")
                
            # Завершаем спан
            await tracer.end_span(
                span,
                status=SpanStatus.ERROR if error else SpanStatus.OK,
                error=error
            )
            
            # Записываем вызов между сервисами
            if parent_context:
                prev_service = services[i - 1]
                self.service_map.add_call(
                    prev_service,
                    service,
                    span.duration_ms,
                    error is not None
                )
                
            parent_context = span.context
            
        return trace_id
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_spans = sum(len(spans) for spans in self.aggregator.spans_buffer.values())
        error_spans = sum(
            1 for spans in self.aggregator.spans_buffer.values()
            for span in spans if span.status == SpanStatus.ERROR
        )
        
        return {
            "total_traces": len(self.aggregator.traces),
            "total_spans": total_spans,
            "services": len(self.service_map.services),
            "edges": len(self.service_map.edges),
            "error_spans": error_spans,
            "error_rate": (error_spans / total_spans * 100) if total_spans > 0 else 0,
            "alerts": len(self.alert_manager.alerts)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 91: Distributed Tracing Platform")
    print("=" * 60)
    
    async def demo():
        platform = DistributedTracingPlatform()
        print("✓ Distributed Tracing Platform created")
        
        # Создание трейсеров
        print("\n📦 Creating Service Tracers...")
        
        services = ["api-gateway", "user-service", "order-service", "payment-service", "notification-service"]
        
        for service in services:
            tracer = platform.create_tracer(service, "1.0.0")
            print(f"  ✓ {service} tracer created")
            
        # Context Propagation
        print("\n🔄 Context Propagation Demo...")
        
        tracer = platform.tracers["api-gateway"]
        propagator = tracer.propagator
        
        span = tracer.start_span("incoming_request", kind=SpanKind.SERVER)
        span.context.baggage["user_id"] = "user_123"
        span.context.baggage["request_id"] = "req_abc"
        
        headers = propagator.inject(span.context)
        print(f"\n  Injected Headers:")
        for k, v in headers.items():
            print(f"    {k}: {v}")
            
        extracted = propagator.extract(headers)
        print(f"\n  Extracted Context:")
        print(f"    Trace ID: {extracted.trace_id}")
        print(f"    Span ID: {extracted.span_id}")
        print(f"    Baggage: {extracted.baggage}")
        
        await tracer.end_span(span)
        
        # Симуляция распределённых вызовов
        print("\n🔀 Simulating Distributed Calls...")
        
        call_scenarios = [
            (["api-gateway", "user-service", "notification-service"], 
             ["GET /users", "get_user", "send_email"]),
            (["api-gateway", "order-service", "payment-service", "notification-service"],
             ["POST /orders", "create_order", "process_payment", "send_confirmation"]),
            (["api-gateway", "user-service"],
             ["GET /profile", "get_profile"]),
            (["api-gateway", "order-service", "user-service", "payment-service"],
             ["GET /orders/{id}", "get_order", "get_user", "get_payment_status"]),
        ]
        
        trace_ids = []
        for services_list, operations in call_scenarios:
            trace_id = await platform.simulate_distributed_call(services_list, operations)
            trace_ids.append(trace_id)
            print(f"  ✓ Trace: {trace_id[:16]}... ({len(services_list)} spans)")
            
        # Дополнительные вызовы для статистики
        print("\n  Running additional simulations...")
        for _ in range(20):
            scenario = random.choice(call_scenarios)
            await platform.simulate_distributed_call(scenario[0], scenario[1])
            
        print("  ✓ 20 additional traces generated")
        
        # Анализ трейса
        print("\n📊 Trace Analysis...")
        
        trace = platform.aggregator.build_trace(trace_ids[1])
        
        if trace:
            print(f"\n  Trace ID: {trace.trace_id}")
            print(f"  Spans: {trace.span_count}")
            print(f"  Services: {trace.service_count}")
            print(f"  Duration: {trace.duration_ms:.2f}ms")
            print(f"  Has Errors: {trace.has_errors}")
            
            print("\n  Span Tree:")
            
            # Строим дерево
            span_map = {s.context.span_id: s for s in trace.spans}
            
            for span in trace.spans:
                depth = 0
                parent_id = span.context.parent_span_id
                while parent_id:
                    depth += 1
                    parent = span_map.get(parent_id)
                    parent_id = parent.context.parent_span_id if parent else None
                    
                status_icon = "✅" if span.status == SpanStatus.OK else "❌"
                indent = "  " * depth
                print(f"    {indent}{status_icon} {span.service_name}:{span.name} ({span.duration_ms:.1f}ms)")
                
        # Service Map
        print("\n🗺️ Service Map:")
        
        for service_name, service_info in platform.service_map.services.items():
            print(f"\n  📦 {service_name}")
            print(f"     Total Spans: {service_info.total_spans}")
            print(f"     Error Count: {service_info.error_count}")
            
            if service_info.operations:
                top_ops = sorted(service_info.operations.items(), key=lambda x: -x[1])[:3]
                print(f"     Top Operations: {', '.join(f'{op}({cnt})' for op, cnt in top_ops)}")
                
        # Service Connections
        print("\n🔗 Service Connections:")
        
        for edge_key, edge in platform.service_map.edges.items():
            error_rate = (edge.error_count / edge.call_count * 100) if edge.call_count > 0 else 0
            print(f"  {edge.source} → {edge.target}")
            print(f"     Calls: {edge.call_count}, Avg Latency: {edge.avg_latency_ms:.1f}ms, Errors: {error_rate:.1f}%")
            
        # Latency Analysis
        print("\n⏱️ Latency Analysis:")
        
        for key, histogram in platform.latency_analyzer.histograms.items():
            if histogram.total_count >= 5:
                percentiles = platform.latency_analyzer.get_percentiles(*key.split(":"))
                print(f"\n  {key}")
                print(f"     Avg: {histogram.avg_ms:.1f}ms")
                if percentiles:
                    print(f"     p50: {percentiles.get('p50', 0):.1f}ms")
                    print(f"     p95: {percentiles.get('p95', 0):.1f}ms")
                    print(f"     p99: {percentiles.get('p99', 0):.1f}ms")
                    
        # Root Cause Analysis
        print("\n🔍 Root Cause Analysis:")
        
        # Находим трейс с ошибкой
        error_trace = None
        for trace_id in trace_ids:
            trace = platform.aggregator.get_trace(trace_id)
            if trace and trace.has_errors:
                error_trace = trace
                break
                
        if error_trace:
            analysis = platform.root_cause_analyzer.analyze_error_trace(error_trace)
            
            if analysis["root_cause_span"]:
                span = analysis["root_cause_span"]
                print(f"\n  Root Cause Span:")
                print(f"    Service: {span.service_name}")
                print(f"    Operation: {span.name}")
                print(f"    Error: {span.error_message}")
                
            if analysis["error_path"]:
                print(f"\n  Error Path:")
                for step in analysis["error_path"]:
                    print(f"    → {step}")
                    
            if analysis["suggestions"]:
                print(f"\n  Suggestions:")
                for suggestion in analysis["suggestions"]:
                    print(f"    💡 {suggestion}")
        else:
            print("  No error traces found")
            
        # Alerts
        print("\n🚨 Alerts:")
        
        if platform.alert_manager.alerts:
            for alert in platform.alert_manager.alerts[:5]:
                severity_icon = {
                    AlertSeverity.INFO: "ℹ️",
                    AlertSeverity.WARNING: "⚠️",
                    AlertSeverity.ERROR: "❌",
                    AlertSeverity.CRITICAL: "🔥"
                }.get(alert.severity, "?")
                
                print(f"\n  {severity_icon} {alert.title}")
                print(f"     Service: {alert.service}")
                print(f"     Trace: {alert.trace_id[:16]}...")
        else:
            print("  No alerts triggered")
            
        # Statistics
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Traces: {stats['total_traces']}")
        print(f"  Total Spans: {stats['total_spans']}")
        print(f"  Services: {stats['services']}")
        print(f"  Service Connections: {stats['edges']}")
        print(f"  Error Spans: {stats['error_spans']}")
        print(f"  Error Rate: {stats['error_rate']:.1f}%")
        print(f"  Alerts: {stats['alerts']}")
        
        # Dashboard
        print("\n📋 Tracing Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │            Distributed Tracing Overview                     │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Traces:    {stats['total_traces']:>6}     │  Spans:    {stats['total_spans']:>6}         │")
        print(f"  │ Services:  {stats['services']:>6}     │  Edges:    {stats['edges']:>6}         │")
        print(f"  │ Errors:    {stats['error_spans']:>6}     │  Rate:     {stats['error_rate']:>5.1f}%         │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Distributed Tracing Platform initialized!")
    print("=" * 60)
