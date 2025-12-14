#!/usr/bin/env python3
"""
Server Init - Iteration 163: Distributed Tracing Platform
Платформа распределённой трассировки

Функционал:
- Span Management - управление спанами
- Trace Collection - сбор трасс
- Context Propagation - распространение контекста
- Sampling Strategies - стратегии сэмплирования
- Service Maps - карты сервисов
- Latency Analysis - анализ задержек
- Error Tracking - отслеживание ошибок
- Trace Visualization - визуализация трасс
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import random
import time


class SpanKind(Enum):
    """Тип спана"""
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"
    INTERNAL = "internal"


class SpanStatus(Enum):
    """Статус спана"""
    OK = "ok"
    ERROR = "error"
    UNSET = "unset"


class SamplingDecision(Enum):
    """Решение о сэмплировании"""
    SAMPLE = "sample"
    DROP = "drop"
    DEFER = "defer"


class SamplerType(Enum):
    """Тип сэмплера"""
    ALWAYS_ON = "always_on"
    ALWAYS_OFF = "always_off"
    PROBABILITY = "probability"
    RATE_LIMITING = "rate_limiting"
    ADAPTIVE = "adaptive"


@dataclass
class TraceContext:
    """Контекст трассировки"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    
    # Flags
    sampled: bool = True
    
    # Baggage
    baggage: Dict[str, str] = field(default_factory=dict)
    
    def to_headers(self) -> Dict[str, str]:
        """Конвертация в заголовки"""
        return {
            "traceparent": f"00-{self.trace_id}-{self.span_id}-{'01' if self.sampled else '00'}",
            "tracestate": "",
            "baggage": ",".join(f"{k}={v}" for k, v in self.baggage.items())
        }
        
    @classmethod
    def from_headers(cls, headers: Dict[str, str]) -> Optional['TraceContext']:
        """Создание из заголовков"""
        traceparent = headers.get("traceparent")
        
        if not traceparent:
            return None
            
        parts = traceparent.split("-")
        
        if len(parts) < 4:
            return None
            
        return cls(
            trace_id=parts[1],
            span_id=parts[2],
            sampled=parts[3] == "01"
        )


@dataclass
class SpanEvent:
    """Событие спана"""
    name: str
    timestamp: datetime = field(default_factory=datetime.now)
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SpanLink:
    """Ссылка спана"""
    trace_id: str
    span_id: str
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Span:
    """Спан"""
    span_id: str
    trace_id: str
    
    # Naming
    name: str = ""
    service_name: str = ""
    
    # Type
    kind: SpanKind = SpanKind.INTERNAL
    
    # Parent
    parent_span_id: Optional[str] = None
    
    # Timing
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_ms: float = 0.0
    
    # Status
    status: SpanStatus = SpanStatus.UNSET
    error_message: str = ""
    
    # Attributes
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    # Events
    events: List[SpanEvent] = field(default_factory=list)
    
    # Links
    links: List[SpanLink] = field(default_factory=list)
    
    # Resource
    resource_attributes: Dict[str, Any] = field(default_factory=dict)
    
    def end(self, status: SpanStatus = SpanStatus.OK, error_message: str = ""):
        """Завершение спана"""
        self.end_time = datetime.now()
        self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000
        self.status = status
        self.error_message = error_message
        
    def add_event(self, name: str, attributes: Optional[Dict] = None):
        """Добавление события"""
        event = SpanEvent(
            name=name,
            attributes=attributes or {}
        )
        self.events.append(event)
        
    def set_attribute(self, key: str, value: Any):
        """Установка атрибута"""
        self.attributes[key] = value


@dataclass
class Trace:
    """Трасса"""
    trace_id: str
    
    # Spans
    spans: Dict[str, Span] = field(default_factory=dict)
    
    # Root span
    root_span_id: Optional[str] = None
    
    # Services
    services: Set[str] = field(default_factory=set)
    
    # Timing
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_ms: float = 0.0
    
    # Status
    has_errors: bool = False
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_span(self, span: Span):
        """Добавление спана"""
        self.spans[span.span_id] = span
        self.services.add(span.service_name)
        
        # Update root
        if span.parent_span_id is None:
            self.root_span_id = span.span_id
            
        # Update timing
        if self.start_time is None or span.start_time < self.start_time:
            self.start_time = span.start_time
            
        if span.end_time:
            if self.end_time is None or span.end_time > self.end_time:
                self.end_time = span.end_time
                
        if self.start_time and self.end_time:
            self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000
            
        # Check errors
        if span.status == SpanStatus.ERROR:
            self.has_errors = True


@dataclass
class ServiceStats:
    """Статистика сервиса"""
    service_name: str
    
    # Counts
    trace_count: int = 0
    span_count: int = 0
    error_count: int = 0
    
    # Latency
    avg_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    
    # Dependencies
    upstream: Set[str] = field(default_factory=set)
    downstream: Set[str] = field(default_factory=set)


@dataclass
class ServiceEdge:
    """Ребро между сервисами"""
    source: str
    target: str
    
    # Counts
    call_count: int = 0
    error_count: int = 0
    
    # Latency
    avg_latency_ms: float = 0.0


class Sampler:
    """Сэмплер"""
    
    def __init__(self, sampler_type: SamplerType = SamplerType.PROBABILITY,
                 probability: float = 0.1, rate_limit: int = 100):
        self.sampler_type = sampler_type
        self.probability = probability
        self.rate_limit = rate_limit
        self.samples_this_second = 0
        self.last_second = int(time.time())
        
    def should_sample(self, trace_id: str, parent_sampled: Optional[bool] = None) -> SamplingDecision:
        """Решение о сэмплировании"""
        # Always honor parent decision
        if parent_sampled is not None:
            return SamplingDecision.SAMPLE if parent_sampled else SamplingDecision.DROP
            
        if self.sampler_type == SamplerType.ALWAYS_ON:
            return SamplingDecision.SAMPLE
            
        if self.sampler_type == SamplerType.ALWAYS_OFF:
            return SamplingDecision.DROP
            
        if self.sampler_type == SamplerType.PROBABILITY:
            if random.random() < self.probability:
                return SamplingDecision.SAMPLE
            return SamplingDecision.DROP
            
        if self.sampler_type == SamplerType.RATE_LIMITING:
            current_second = int(time.time())
            
            if current_second != self.last_second:
                self.samples_this_second = 0
                self.last_second = current_second
                
            if self.samples_this_second < self.rate_limit:
                self.samples_this_second += 1
                return SamplingDecision.SAMPLE
                
            return SamplingDecision.DROP
            
        return SamplingDecision.DEFER


class SpanProcessor:
    """Процессор спанов"""
    
    def __init__(self):
        self.processors: List['SpanProcessor'] = []
        
    def on_start(self, span: Span, parent_context: Optional[TraceContext]):
        """При старте спана"""
        pass
        
    def on_end(self, span: Span):
        """При завершении спана"""
        pass


class BatchSpanProcessor(SpanProcessor):
    """Батч-процессор спанов"""
    
    def __init__(self, exporter: 'SpanExporter', max_batch_size: int = 512,
                 export_interval_ms: int = 5000):
        super().__init__()
        self.exporter = exporter
        self.max_batch_size = max_batch_size
        self.export_interval_ms = export_interval_ms
        self.pending_spans: List[Span] = []
        
    def on_end(self, span: Span):
        """При завершении спана"""
        self.pending_spans.append(span)
        
        if len(self.pending_spans) >= self.max_batch_size:
            self.flush()
            
    def flush(self):
        """Экспорт спанов"""
        if self.pending_spans:
            self.exporter.export(self.pending_spans)
            self.pending_spans = []


class SpanExporter:
    """Экспортёр спанов"""
    
    def export(self, spans: List[Span]):
        """Экспорт спанов"""
        pass


class InMemoryExporter(SpanExporter):
    """In-memory экспортёр"""
    
    def __init__(self):
        self.exported_spans: List[Span] = []
        
    def export(self, spans: List[Span]):
        """Экспорт спанов"""
        self.exported_spans.extend(spans)


class Tracer:
    """Трассировщик"""
    
    def __init__(self, service_name: str, sampler: Optional[Sampler] = None):
        self.service_name = service_name
        self.sampler = sampler or Sampler()
        self.processors: List[SpanProcessor] = []
        self.active_spans: Dict[str, Span] = {}
        self.resource_attributes = {
            "service.name": service_name,
            "service.version": "1.0.0"
        }
        
    def start_span(self, name: str, kind: SpanKind = SpanKind.INTERNAL,
                    parent_context: Optional[TraceContext] = None,
                    attributes: Optional[Dict] = None) -> Span:
        """Создание спана"""
        # Determine trace/span IDs
        if parent_context:
            trace_id = parent_context.trace_id
            parent_span_id = parent_context.span_id
            sampled = parent_context.sampled
        else:
            trace_id = uuid.uuid4().hex
            parent_span_id = None
            decision = self.sampler.should_sample(trace_id)
            sampled = decision == SamplingDecision.SAMPLE
            
        span = Span(
            span_id=uuid.uuid4().hex[:16],
            trace_id=trace_id,
            name=name,
            service_name=self.service_name,
            kind=kind,
            parent_span_id=parent_span_id,
            attributes=attributes or {},
            resource_attributes=self.resource_attributes.copy()
        )
        
        # Notify processors
        context = TraceContext(trace_id=trace_id, span_id=span.span_id,
                               parent_span_id=parent_span_id, sampled=sampled)
        for processor in self.processors:
            processor.on_start(span, context)
            
        self.active_spans[span.span_id] = span
        return span
        
    def end_span(self, span: Span, status: SpanStatus = SpanStatus.OK,
                  error_message: str = ""):
        """Завершение спана"""
        span.end(status, error_message)
        
        # Notify processors
        for processor in self.processors:
            processor.on_end(span)
            
        # Remove from active
        self.active_spans.pop(span.span_id, None)
        
    def add_processor(self, processor: SpanProcessor):
        """Добавление процессора"""
        self.processors.append(processor)


class TraceCollector:
    """Сборщик трасс"""
    
    def __init__(self):
        self.traces: Dict[str, Trace] = {}
        self.service_stats: Dict[str, ServiceStats] = {}
        self.service_edges: Dict[str, ServiceEdge] = {}
        
    def collect_span(self, span: Span):
        """Сбор спана"""
        # Get or create trace
        if span.trace_id not in self.traces:
            self.traces[span.trace_id] = Trace(trace_id=span.trace_id)
            
        trace = self.traces[span.trace_id]
        trace.add_span(span)
        
        # Update service stats
        self._update_service_stats(span)
        
        # Update edges
        self._update_edges(span)
        
    def _update_service_stats(self, span: Span):
        """Обновление статистики сервиса"""
        service = span.service_name
        
        if service not in self.service_stats:
            self.service_stats[service] = ServiceStats(service_name=service)
            
        stats = self.service_stats[service]
        stats.span_count += 1
        
        if span.status == SpanStatus.ERROR:
            stats.error_count += 1
            
        # Update latency (simple moving average)
        if span.duration_ms > 0:
            count = stats.span_count
            stats.avg_latency_ms = (stats.avg_latency_ms * (count - 1) + span.duration_ms) / count
            
    def _update_edges(self, span: Span):
        """Обновление рёбер"""
        if span.parent_span_id:
            # Find parent span
            trace = self.traces.get(span.trace_id)
            if trace:
                parent_span = trace.spans.get(span.parent_span_id)
                if parent_span and parent_span.service_name != span.service_name:
                    edge_key = f"{parent_span.service_name}->{span.service_name}"
                    
                    if edge_key not in self.service_edges:
                        self.service_edges[edge_key] = ServiceEdge(
                            source=parent_span.service_name,
                            target=span.service_name
                        )
                        
                    edge = self.service_edges[edge_key]
                    edge.call_count += 1
                    
                    if span.status == SpanStatus.ERROR:
                        edge.error_count += 1
                        
                    # Update upstream/downstream
                    self.service_stats[parent_span.service_name].downstream.add(span.service_name)
                    self.service_stats[span.service_name].upstream.add(parent_span.service_name)
                    
    def get_trace(self, trace_id: str) -> Optional[Trace]:
        """Получение трассы"""
        return self.traces.get(trace_id)
        
    def search_traces(self, service: Optional[str] = None,
                       has_errors: Optional[bool] = None,
                       min_duration_ms: Optional[float] = None,
                       limit: int = 100) -> List[Trace]:
        """Поиск трасс"""
        results = []
        
        for trace in self.traces.values():
            if service and service not in trace.services:
                continue
                
            if has_errors is not None and trace.has_errors != has_errors:
                continue
                
            if min_duration_ms and trace.duration_ms < min_duration_ms:
                continue
                
            results.append(trace)
            
            if len(results) >= limit:
                break
                
        return results


class ServiceMapBuilder:
    """Строитель карты сервисов"""
    
    def __init__(self, collector: TraceCollector):
        self.collector = collector
        
    def build_map(self) -> Dict[str, Any]:
        """Построение карты сервисов"""
        nodes = []
        edges = []
        
        # Build nodes
        for service, stats in self.collector.service_stats.items():
            node = {
                "id": service,
                "name": service,
                "span_count": stats.span_count,
                "error_count": stats.error_count,
                "error_rate": stats.error_count / stats.span_count * 100 if stats.span_count > 0 else 0,
                "avg_latency_ms": stats.avg_latency_ms
            }
            nodes.append(node)
            
        # Build edges
        for edge_key, edge in self.collector.service_edges.items():
            edge_data = {
                "source": edge.source,
                "target": edge.target,
                "call_count": edge.call_count,
                "error_count": edge.error_count,
                "error_rate": edge.error_count / edge.call_count * 100 if edge.call_count > 0 else 0
            }
            edges.append(edge_data)
            
        return {
            "nodes": nodes,
            "edges": edges,
            "service_count": len(nodes),
            "edge_count": len(edges)
        }


class LatencyAnalyzer:
    """Анализатор задержек"""
    
    def __init__(self, collector: TraceCollector):
        self.collector = collector
        
    def analyze_trace(self, trace_id: str) -> Dict[str, Any]:
        """Анализ трассы"""
        trace = self.collector.get_trace(trace_id)
        
        if not trace:
            return {}
            
        # Calculate critical path
        critical_path = self._find_critical_path(trace)
        
        # Find slow spans
        slow_spans = self._find_slow_spans(trace)
        
        # Service breakdown
        service_breakdown = self._service_breakdown(trace)
        
        return {
            "trace_id": trace_id,
            "total_duration_ms": trace.duration_ms,
            "span_count": len(trace.spans),
            "service_count": len(trace.services),
            "critical_path": critical_path,
            "slow_spans": slow_spans,
            "service_breakdown": service_breakdown,
            "has_errors": trace.has_errors
        }
        
    def _find_critical_path(self, trace: Trace) -> List[Dict]:
        """Поиск критического пути"""
        if not trace.root_span_id:
            return []
            
        path = []
        current_span_id = trace.root_span_id
        
        while current_span_id:
            span = trace.spans.get(current_span_id)
            if not span:
                break
                
            path.append({
                "span_id": span.span_id,
                "name": span.name,
                "service": span.service_name,
                "duration_ms": span.duration_ms
            })
            
            # Find child with longest duration
            children = [s for s in trace.spans.values() 
                       if s.parent_span_id == current_span_id]
                       
            if children:
                longest_child = max(children, key=lambda s: s.duration_ms)
                current_span_id = longest_child.span_id
            else:
                current_span_id = None
                
        return path
        
    def _find_slow_spans(self, trace: Trace, threshold_ms: float = 100) -> List[Dict]:
        """Поиск медленных спанов"""
        slow = []
        
        for span in trace.spans.values():
            if span.duration_ms >= threshold_ms:
                slow.append({
                    "span_id": span.span_id,
                    "name": span.name,
                    "service": span.service_name,
                    "duration_ms": span.duration_ms
                })
                
        return sorted(slow, key=lambda s: s["duration_ms"], reverse=True)[:10]
        
    def _service_breakdown(self, trace: Trace) -> Dict[str, float]:
        """Разбивка по сервисам"""
        breakdown = {}
        
        for span in trace.spans.values():
            service = span.service_name
            breakdown[service] = breakdown.get(service, 0) + span.duration_ms
            
        return breakdown


class ErrorTracker:
    """Трекер ошибок"""
    
    def __init__(self, collector: TraceCollector):
        self.collector = collector
        self.error_patterns: Dict[str, List[str]] = {}  # error_type -> trace_ids
        
    def track_errors(self):
        """Отслеживание ошибок"""
        for trace in self.collector.traces.values():
            if trace.has_errors:
                for span in trace.spans.values():
                    if span.status == SpanStatus.ERROR:
                        error_type = span.error_message or "Unknown Error"
                        
                        if error_type not in self.error_patterns:
                            self.error_patterns[error_type] = []
                            
                        if trace.trace_id not in self.error_patterns[error_type]:
                            self.error_patterns[error_type].append(trace.trace_id)
                            
    def get_error_summary(self) -> Dict[str, Any]:
        """Сводка по ошибкам"""
        self.track_errors()
        
        total_errors = sum(len(traces) for traces in self.error_patterns.values())
        
        error_types = []
        for error_type, traces in sorted(self.error_patterns.items(),
                                          key=lambda x: len(x[1]), reverse=True):
            error_types.append({
                "error_type": error_type,
                "count": len(traces),
                "sample_traces": traces[:5]
            })
            
        return {
            "total_errors": total_errors,
            "error_types": error_types[:10]
        }


class TraceVisualizer:
    """Визуализатор трасс"""
    
    def __init__(self, collector: TraceCollector):
        self.collector = collector
        
    def visualize_trace(self, trace_id: str) -> str:
        """Визуализация трассы"""
        trace = self.collector.get_trace(trace_id)
        
        if not trace:
            return "Trace not found"
            
        lines = []
        lines.append(f"Trace: {trace_id}")
        lines.append(f"Duration: {trace.duration_ms:.2f}ms")
        lines.append(f"Services: {', '.join(trace.services)}")
        lines.append("")
        
        # Build tree
        self._build_tree(trace, trace.root_span_id, lines, 0)
        
        return "\n".join(lines)
        
    def _build_tree(self, trace: Trace, span_id: Optional[str],
                     lines: List[str], depth: int):
        """Построение дерева"""
        if not span_id:
            return
            
        span = trace.spans.get(span_id)
        if not span:
            return
            
        indent = "  " * depth
        status_icon = "✓" if span.status == SpanStatus.OK else "✗"
        
        lines.append(f"{indent}{status_icon} [{span.service_name}] {span.name} ({span.duration_ms:.2f}ms)")
        
        # Find children
        children = [s for s in trace.spans.values() if s.parent_span_id == span_id]
        children.sort(key=lambda s: s.start_time)
        
        for child in children:
            self._build_tree(trace, child.span_id, lines, depth + 1)


class DistributedTracingPlatform:
    """Платформа распределённой трассировки"""
    
    def __init__(self):
        self.collector = TraceCollector()
        self.tracers: Dict[str, Tracer] = {}
        self.sampler = Sampler(SamplerType.PROBABILITY, probability=1.0)
        self.service_map_builder = ServiceMapBuilder(self.collector)
        self.latency_analyzer = LatencyAnalyzer(self.collector)
        self.error_tracker = ErrorTracker(self.collector)
        self.visualizer = TraceVisualizer(self.collector)
        
        # Setup exporter
        self.exporter = InMemoryExporter()
        self.batch_processor = BatchSpanProcessor(self.exporter)
        
    def get_tracer(self, service_name: str) -> Tracer:
        """Получение трассировщика"""
        if service_name not in self.tracers:
            tracer = Tracer(service_name, self.sampler)
            tracer.add_processor(self.batch_processor)
            self.tracers[service_name] = tracer
            
        return self.tracers[service_name]
        
    def collect_exported_spans(self):
        """Сбор экспортированных спанов"""
        self.batch_processor.flush()
        
        for span in self.exporter.exported_spans:
            self.collector.collect_span(span)
            
        self.exporter.exported_spans = []
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        return {
            "total_traces": len(self.collector.traces),
            "total_services": len(self.collector.service_stats),
            "total_edges": len(self.collector.service_edges)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 163: Distributed Tracing Platform")
    print("=" * 60)
    
    platform = DistributedTracingPlatform()
    print("✓ Distributed Tracing Platform created")
    
    # Simulate distributed traces
    print("\n🔍 Simulating Distributed Traces...")
    
    services = ["api-gateway", "user-service", "order-service", "payment-service", "notification-service"]
    
    # Create tracers
    tracers = {svc: platform.get_tracer(svc) for svc in services}
    
    # Simulate 10 requests
    for req_num in range(10):
        # API Gateway receives request
        gateway = tracers["api-gateway"]
        
        # Start root span
        root_span = gateway.start_span(
            "HTTP GET /api/orders",
            kind=SpanKind.SERVER,
            attributes={"http.method": "GET", "http.url": "/api/orders"}
        )
        
        context = TraceContext(
            trace_id=root_span.trace_id,
            span_id=root_span.span_id
        )
        
        # Simulate latency
        time.sleep(random.uniform(0.001, 0.01))
        
        # Call user service
        user_tracer = tracers["user-service"]
        user_span = user_tracer.start_span(
            "authenticate",
            kind=SpanKind.SERVER,
            parent_context=context
        )
        
        user_context = TraceContext(
            trace_id=user_span.trace_id,
            span_id=user_span.span_id,
            parent_span_id=root_span.span_id
        )
        
        time.sleep(random.uniform(0.001, 0.005))
        user_tracer.end_span(user_span)
        
        # Call order service
        order_tracer = tracers["order-service"]
        order_span = order_tracer.start_span(
            "get_orders",
            kind=SpanKind.SERVER,
            parent_context=context
        )
        
        order_context = TraceContext(
            trace_id=order_span.trace_id,
            span_id=order_span.span_id,
            parent_span_id=root_span.span_id
        )
        
        time.sleep(random.uniform(0.002, 0.01))
        
        # Simulate occasional errors
        if random.random() < 0.2:
            order_tracer.end_span(order_span, SpanStatus.ERROR, "Database timeout")
        else:
            order_tracer.end_span(order_span)
            
        # Call payment service for some requests
        if random.random() < 0.5:
            payment_tracer = tracers["payment-service"]
            payment_span = payment_tracer.start_span(
                "process_payment",
                kind=SpanKind.SERVER,
                parent_context=order_context
            )
            
            time.sleep(random.uniform(0.005, 0.02))
            
            if random.random() < 0.1:
                payment_tracer.end_span(payment_span, SpanStatus.ERROR, "Payment declined")
            else:
                payment_tracer.end_span(payment_span)
                
        # Send notification
        if random.random() < 0.3:
            notif_tracer = tracers["notification-service"]
            notif_span = notif_tracer.start_span(
                "send_notification",
                kind=SpanKind.PRODUCER,
                parent_context=context
            )
            time.sleep(random.uniform(0.001, 0.003))
            notif_tracer.end_span(notif_span)
            
        # End root span
        gateway.end_span(root_span)
        
    print(f"  ✓ Simulated {10} requests")
    
    # Collect spans
    platform.collect_exported_spans()
    
    # Service statistics
    print("\n📊 Service Statistics:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────┐")
    print("  │ Service              │ Spans │ Errors │ Error Rate │ Avg Latency  │")
    print("  ├────────────────────────────────────────────────────────────────────┤")
    
    for service, stats in platform.collector.service_stats.items():
        name = service[:20].ljust(20)
        spans = str(stats.span_count).ljust(5)
        errors = str(stats.error_count).ljust(6)
        error_rate = f"{stats.error_count / stats.span_count * 100:.1f}%".ljust(10) if stats.span_count > 0 else "0%".ljust(10)
        latency = f"{stats.avg_latency_ms:.2f}ms".ljust(12)
        print(f"  │ {name} │ {spans} │ {errors} │ {error_rate} │ {latency} │")
        
    print("  └────────────────────────────────────────────────────────────────────┘")
    
    # Service map
    print("\n🗺️ Service Map:")
    
    service_map = platform.service_map_builder.build_map()
    
    print(f"\n  Services: {service_map['service_count']}")
    print(f"  Edges: {service_map['edge_count']}")
    
    print("\n  Service Dependencies:")
    for edge in service_map["edges"]:
        error_indicator = "🔴" if edge["error_rate"] > 10 else "🟢"
        print(f"    {error_indicator} {edge['source']} → {edge['target']}: {edge['call_count']} calls ({edge['error_rate']:.1f}% errors)")
        
    # Trace analysis
    print("\n🔬 Trace Analysis:")
    
    # Get a sample trace
    sample_trace = list(platform.collector.traces.values())[0] if platform.collector.traces else None
    
    if sample_trace:
        analysis = platform.latency_analyzer.analyze_trace(sample_trace.trace_id)
        
        print(f"\n  Sample Trace: {analysis['trace_id'][:16]}...")
        print(f"  Total Duration: {analysis['total_duration_ms']:.2f}ms")
        print(f"  Span Count: {analysis['span_count']}")
        print(f"  Service Count: {analysis['service_count']}")
        print(f"  Has Errors: {analysis['has_errors']}")
        
        print("\n  Critical Path:")
        for i, step in enumerate(analysis["critical_path"][:5], 1):
            print(f"    {i}. [{step['service']}] {step['name']}: {step['duration_ms']:.2f}ms")
            
        print("\n  Service Time Breakdown:")
        for service, duration in sorted(analysis["service_breakdown"].items(),
                                         key=lambda x: x[1], reverse=True):
            pct = duration / analysis["total_duration_ms"] * 100 if analysis["total_duration_ms"] > 0 else 0
            bar = "█" * int(pct / 5)
            print(f"    {service.ljust(20)}: {duration:>7.2f}ms ({pct:>5.1f}%) {bar}")
            
    # Error summary
    print("\n❌ Error Summary:")
    
    error_summary = platform.error_tracker.get_error_summary()
    
    print(f"\n  Total Errors: {error_summary['total_errors']}")
    
    if error_summary["error_types"]:
        print("\n  Error Types:")
        for error_type in error_summary["error_types"]:
            print(f"    • {error_type['error_type']}: {error_type['count']} occurrences")
            
    # Trace visualization
    print("\n📜 Trace Visualization (Sample):")
    
    if sample_trace:
        visualization = platform.visualizer.visualize_trace(sample_trace.trace_id)
        for line in visualization.split("\n"):
            print(f"  {line}")
            
    # Search traces
    print("\n🔎 Trace Search:")
    
    # Search for traces with errors
    error_traces = platform.collector.search_traces(has_errors=True, limit=5)
    print(f"\n  Traces with errors: {len(error_traces)}")
    
    # Search for traces from specific service
    service_traces = platform.collector.search_traces(service="order-service", limit=5)
    print(f"  Traces involving order-service: {len(service_traces)}")
    
    # Platform statistics
    print("\n📈 Platform Statistics:")
    
    stats = platform.get_statistics()
    
    print(f"\n  Total Traces: {stats['total_traces']}")
    print(f"  Total Services: {stats['total_services']}")
    print(f"  Service Edges: {stats['total_edges']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                 Distributed Tracing Dashboard                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Traces Collected:             {stats['total_traces']:>10}                       │")
    print(f"│ Services Tracked:             {stats['total_services']:>10}                       │")
    print(f"│ Service Dependencies:         {stats['total_edges']:>10}                       │")
    print(f"│ Error Traces:                 {len(error_traces):>10}                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    
    # Calculate totals
    total_spans = sum(s.span_count for s in platform.collector.service_stats.values())
    total_errors = sum(s.error_count for s in platform.collector.service_stats.values())
    avg_latency = sum(s.avg_latency_ms for s in platform.collector.service_stats.values()) / len(platform.collector.service_stats) if platform.collector.service_stats else 0
    
    print(f"│ Total Spans:                  {total_spans:>10}                       │")
    print(f"│ Total Errors:                 {total_errors:>10}                       │")
    print(f"│ Avg Service Latency:          {avg_latency:>7.2f}ms                       │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Distributed Tracing Platform initialized!")
    print("=" * 60)
