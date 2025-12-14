#!/usr/bin/env python3
"""
Server Init - Iteration 275: Distributed Tracing Platform
Платформа распределенной трассировки

Функционал:
- Span Collection - сбор span'ов
- Context Propagation - распространение контекста
- Trace Sampling - семплирование трассировок
- Baggage Items - передача данных в контексте
- Trace Aggregation - агрегация трассировок
- Service Dependencies - зависимости сервисов
- Latency Analysis - анализ задержек
- Error Tracking - отслеживание ошибок
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid


class SpanKind(Enum):
    """Тип span'а"""
    INTERNAL = "internal"
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"


class SpanStatus(Enum):
    """Статус span'а"""
    UNSET = "unset"
    OK = "ok"
    ERROR = "error"


class SamplingDecision(Enum):
    """Решение семплирования"""
    DROP = "drop"
    RECORD_ONLY = "record_only"
    RECORD_AND_SAMPLE = "record_and_sample"


class PropagationFormat(Enum):
    """Формат распространения"""
    W3C_TRACE_CONTEXT = "w3c_trace_context"
    B3 = "b3"
    JAEGER = "jaeger"
    DATADOG = "datadog"


@dataclass
class SpanContext:
    """Контекст span'а"""
    trace_id: str
    span_id: str
    trace_flags: int = 0  # 1 = sampled
    trace_state: str = ""
    is_remote: bool = False
    
    @property
    def is_sampled(self) -> bool:
        return (self.trace_flags & 1) == 1


@dataclass
class SpanEvent:
    """Событие span'а"""
    name: str
    timestamp: datetime = field(default_factory=datetime.now)
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SpanLink:
    """Связь span'а"""
    context: SpanContext
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TracingSpan:
    """Span трассировки"""
    context: SpanContext
    name: str
    
    # Kind
    kind: SpanKind = SpanKind.INTERNAL
    
    # Parent
    parent_context: Optional[SpanContext] = None
    
    # Timing
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    # Status
    status: SpanStatus = SpanStatus.UNSET
    status_message: str = ""
    
    # Attributes
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    # Events
    events: List[SpanEvent] = field(default_factory=list)
    
    # Links
    links: List[SpanLink] = field(default_factory=list)
    
    # Service
    service_name: str = ""
    
    @property
    def duration_ms(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0


@dataclass 
class BaggageItem:
    """Элемент багажа"""
    key: str
    value: str
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class TraceContext:
    """Контекст трассировки"""
    trace_id: str
    
    # Current span
    current_span: Optional[TracingSpan] = None
    
    # Baggage
    baggage: Dict[str, BaggageItem] = field(default_factory=dict)
    
    # Sampling
    sampled: bool = True


@dataclass
class SamplerConfig:
    """Конфигурация семплера"""
    sampler_id: str
    name: str
    
    # Rate
    sample_rate: float = 1.0  # 0.0 - 1.0
    
    # Rules
    rate_limit: int = 100  # per second
    
    # Patterns
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)


@dataclass
class TraceExporter:
    """Экспортер трассировок"""
    exporter_id: str
    name: str
    
    # Endpoint
    endpoint: str = ""
    
    # Format
    format: str = "otlp"  # otlp, jaeger, zipkin
    
    # Batching
    batch_size: int = 100
    batch_timeout_ms: int = 5000
    
    # State
    active: bool = True
    spans_exported: int = 0


@dataclass
class ServiceDependency:
    """Зависимость сервиса"""
    source: str
    target: str
    
    # Statistics
    call_count: int = 0
    error_count: int = 0
    avg_latency_ms: float = 0
    p99_latency_ms: float = 0


@dataclass
class TraceAggregate:
    """Агрегированная информация о трассировках"""
    service: str
    operation: str
    
    # Counts
    trace_count: int = 0
    error_count: int = 0
    
    # Latency
    min_latency_ms: float = float('inf')
    max_latency_ms: float = 0
    avg_latency_ms: float = 0
    p50_latency_ms: float = 0
    p95_latency_ms: float = 0
    p99_latency_ms: float = 0
    
    # Latencies for percentile calculation
    latencies: List[float] = field(default_factory=list)


class DistributedTracingManager:
    """Менеджер распределенной трассировки"""
    
    def __init__(self):
        self.traces: Dict[str, List[TracingSpan]] = {}
        self.samplers: Dict[str, SamplerConfig] = {}
        self.exporters: Dict[str, TraceExporter] = {}
        self.dependencies: Dict[str, ServiceDependency] = {}
        self.aggregates: Dict[str, TraceAggregate] = {}
        self.active_contexts: Dict[str, TraceContext] = {}
        self.propagation_format: PropagationFormat = PropagationFormat.W3C_TRACE_CONTEXT
        
    def create_sampler(self, name: str,
                      sample_rate: float = 1.0) -> SamplerConfig:
        """Создание семплера"""
        sampler = SamplerConfig(
            sampler_id=f"sampler_{uuid.uuid4().hex[:8]}",
            name=name,
            sample_rate=sample_rate
        )
        
        self.samplers[name] = sampler
        return sampler
        
    def add_exporter(self, name: str,
                    endpoint: str,
                    format: str = "otlp") -> TraceExporter:
        """Добавление экспортера"""
        exporter = TraceExporter(
            exporter_id=f"exporter_{uuid.uuid4().hex[:8]}",
            name=name,
            endpoint=endpoint,
            format=format
        )
        
        self.exporters[name] = exporter
        return exporter
        
    def _should_sample(self, name: str) -> SamplingDecision:
        """Проверка семплирования"""
        for sampler in self.samplers.values():
            # Check patterns
            if sampler.exclude_patterns:
                for pattern in sampler.exclude_patterns:
                    if pattern in name:
                        return SamplingDecision.DROP
                        
            if sampler.include_patterns:
                matched = False
                for pattern in sampler.include_patterns:
                    if pattern in name:
                        matched = True
                        break
                if not matched:
                    return SamplingDecision.DROP
                    
            # Sample rate
            if random.random() < sampler.sample_rate:
                return SamplingDecision.RECORD_AND_SAMPLE
            else:
                return SamplingDecision.RECORD_ONLY
                
        return SamplingDecision.RECORD_AND_SAMPLE
        
    def start_trace(self, name: str,
                   service_name: str,
                   kind: SpanKind = SpanKind.SERVER,
                   attributes: Dict[str, Any] = None,
                   parent: Optional[SpanContext] = None) -> TracingSpan:
        """Начало трассировки"""
        sampling = self._should_sample(name)
        
        if parent:
            trace_id = parent.trace_id
        else:
            trace_id = uuid.uuid4().hex[:32]
            
        span_id = uuid.uuid4().hex[:16]
        
        context = SpanContext(
            trace_id=trace_id,
            span_id=span_id,
            trace_flags=1 if sampling == SamplingDecision.RECORD_AND_SAMPLE else 0
        )
        
        span = TracingSpan(
            context=context,
            name=name,
            kind=kind,
            parent_context=parent,
            service_name=service_name,
            attributes=attributes or {}
        )
        
        if trace_id not in self.traces:
            self.traces[trace_id] = []
        self.traces[trace_id].append(span)
        
        # Create trace context
        trace_ctx = TraceContext(
            trace_id=trace_id,
            current_span=span,
            sampled=context.is_sampled
        )
        self.active_contexts[span_id] = trace_ctx
        
        return span
        
    def create_child_span(self, parent: TracingSpan,
                         name: str,
                         service_name: str = None,
                         kind: SpanKind = SpanKind.INTERNAL,
                         attributes: Dict[str, Any] = None) -> TracingSpan:
        """Создание дочернего span'а"""
        return self.start_trace(
            name=name,
            service_name=service_name or parent.service_name,
            kind=kind,
            attributes=attributes,
            parent=parent.context
        )
        
    def add_event(self, span: TracingSpan,
                 name: str,
                 attributes: Dict[str, Any] = None):
        """Добавление события к span'у"""
        event = SpanEvent(
            name=name,
            attributes=attributes or {}
        )
        span.events.append(event)
        
    def add_link(self, span: TracingSpan,
                linked_context: SpanContext,
                attributes: Dict[str, Any] = None):
        """Добавление связи к span'у"""
        link = SpanLink(
            context=linked_context,
            attributes=attributes or {}
        )
        span.links.append(link)
        
    def set_baggage(self, span: TracingSpan,
                   key: str, value: str):
        """Установка багажа"""
        span_id = span.context.span_id
        if span_id in self.active_contexts:
            ctx = self.active_contexts[span_id]
            ctx.baggage[key] = BaggageItem(key=key, value=value)
            
    def get_baggage(self, span: TracingSpan,
                   key: str) -> Optional[str]:
        """Получение багажа"""
        span_id = span.context.span_id
        if span_id in self.active_contexts:
            ctx = self.active_contexts[span_id]
            if key in ctx.baggage:
                return ctx.baggage[key].value
        return None
        
    def end_span(self, span: TracingSpan,
                status: SpanStatus = SpanStatus.OK,
                status_message: str = ""):
        """Завершение span'а"""
        span.end_time = datetime.now()
        span.status = status
        span.status_message = status_message
        
        # Update dependencies
        if span.parent_context:
            # Find parent span
            parent_spans = self.traces.get(span.parent_context.trace_id, [])
            parent_span = None
            for ps in parent_spans:
                if ps.context.span_id == span.parent_context.span_id:
                    parent_span = ps
                    break
                    
            if parent_span and parent_span.service_name != span.service_name:
                dep_key = f"{parent_span.service_name}->{span.service_name}"
                
                if dep_key not in self.dependencies:
                    self.dependencies[dep_key] = ServiceDependency(
                        source=parent_span.service_name,
                        target=span.service_name
                    )
                    
                dep = self.dependencies[dep_key]
                dep.call_count += 1
                if status == SpanStatus.ERROR:
                    dep.error_count += 1
                    
                # Update latency (simple moving average)
                old_avg = dep.avg_latency_ms
                dep.avg_latency_ms = old_avg + (span.duration_ms - old_avg) / dep.call_count
                
        # Update aggregates
        agg_key = f"{span.service_name}:{span.name}"
        
        if agg_key not in self.aggregates:
            self.aggregates[agg_key] = TraceAggregate(
                service=span.service_name,
                operation=span.name
            )
            
        agg = self.aggregates[agg_key]
        agg.trace_count += 1
        
        if status == SpanStatus.ERROR:
            agg.error_count += 1
            
        agg.latencies.append(span.duration_ms)
        agg.min_latency_ms = min(agg.min_latency_ms, span.duration_ms)
        agg.max_latency_ms = max(agg.max_latency_ms, span.duration_ms)
        
        # Calculate percentiles
        if agg.latencies:
            sorted_latencies = sorted(agg.latencies)
            agg.avg_latency_ms = sum(sorted_latencies) / len(sorted_latencies)
            agg.p50_latency_ms = sorted_latencies[int(len(sorted_latencies) * 0.5)]
            agg.p95_latency_ms = sorted_latencies[int(len(sorted_latencies) * 0.95)]
            agg.p99_latency_ms = sorted_latencies[int(len(sorted_latencies) * 0.99)]
            
        # Export
        if span.context.is_sampled:
            self._export_span(span)
            
        # Cleanup
        if span.context.span_id in self.active_contexts:
            del self.active_contexts[span.context.span_id]
            
    def _export_span(self, span: TracingSpan):
        """Экспорт span'а"""
        for exporter in self.exporters.values():
            if exporter.active:
                exporter.spans_exported += 1
                
    def inject_context(self, span: TracingSpan) -> Dict[str, str]:
        """Внедрение контекста в headers"""
        headers = {}
        
        if self.propagation_format == PropagationFormat.W3C_TRACE_CONTEXT:
            headers["traceparent"] = f"00-{span.context.trace_id}-{span.context.span_id}-{span.context.trace_flags:02x}"
            if span.context.trace_state:
                headers["tracestate"] = span.context.trace_state
                
        elif self.propagation_format == PropagationFormat.B3:
            headers["X-B3-TraceId"] = span.context.trace_id
            headers["X-B3-SpanId"] = span.context.span_id
            headers["X-B3-Sampled"] = "1" if span.context.is_sampled else "0"
            
        elif self.propagation_format == PropagationFormat.JAEGER:
            headers["uber-trace-id"] = f"{span.context.trace_id}:{span.context.span_id}:0:{span.context.trace_flags}"
            
        return headers
        
    def extract_context(self, headers: Dict[str, str]) -> Optional[SpanContext]:
        """Извлечение контекста из headers"""
        if self.propagation_format == PropagationFormat.W3C_TRACE_CONTEXT:
            traceparent = headers.get("traceparent")
            if traceparent:
                parts = traceparent.split("-")
                if len(parts) == 4:
                    return SpanContext(
                        trace_id=parts[1],
                        span_id=parts[2],
                        trace_flags=int(parts[3], 16),
                        is_remote=True
                    )
                    
        elif self.propagation_format == PropagationFormat.B3:
            trace_id = headers.get("X-B3-TraceId")
            span_id = headers.get("X-B3-SpanId")
            if trace_id and span_id:
                sampled = headers.get("X-B3-Sampled", "0") == "1"
                return SpanContext(
                    trace_id=trace_id,
                    span_id=span_id,
                    trace_flags=1 if sampled else 0,
                    is_remote=True
                )
                
        return None
        
    def get_trace(self, trace_id: str) -> List[TracingSpan]:
        """Получение трассировки"""
        return self.traces.get(trace_id, [])
        
    def search_traces(self, service: str = None,
                     operation: str = None,
                     min_duration_ms: float = None,
                     has_error: bool = None,
                     limit: int = 100) -> List[List[TracingSpan]]:
        """Поиск трассировок"""
        results = []
        
        for trace_id, spans in self.traces.items():
            if len(results) >= limit:
                break
                
            match = True
            
            for span in spans:
                if service and span.service_name != service:
                    match = False
                    continue
                if operation and span.name != operation:
                    match = False
                    continue
                    
            if match:
                if min_duration_ms:
                    total_duration = sum(s.duration_ms for s in spans if s.end_time)
                    if total_duration < min_duration_ms:
                        match = False
                        
            if match and has_error is not None:
                has_err = any(s.status == SpanStatus.ERROR for s in spans)
                if has_err != has_error:
                    match = False
                    
            if match:
                results.append(spans)
                
        return results
        
    def get_service_dependencies(self) -> List[ServiceDependency]:
        """Получение зависимостей сервисов"""
        return list(self.dependencies.values())
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_spans = sum(len(spans) for spans in self.traces.values())
        error_spans = sum(
            1 for spans in self.traces.values() 
            for span in spans 
            if span.status == SpanStatus.ERROR
        )
        
        return {
            "traces": len(self.traces),
            "spans": total_spans,
            "error_spans": error_spans,
            "samplers": len(self.samplers),
            "exporters": len(self.exporters),
            "dependencies": len(self.dependencies),
            "operations": len(self.aggregates)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 275: Distributed Tracing Platform")
    print("=" * 60)
    
    manager = DistributedTracingManager()
    print("✓ Distributed Tracing Manager created")
    
    # Configure sampler
    print("\n🎲 Configuring Sampler...")
    
    sampler = manager.create_sampler("default", sample_rate=0.8)
    sampler.rate_limit = 1000
    print(f"  Sampler: {sampler.name}, rate={sampler.sample_rate}")
    
    # Add exporters
    print("\n📤 Adding Exporters...")
    
    exporters_config = [
        ("jaeger", "http://jaeger:14268/api/traces", "jaeger"),
        ("zipkin", "http://zipkin:9411/api/v2/spans", "zipkin"),
        ("otlp", "http://collector:4318/v1/traces", "otlp"),
    ]
    
    for name, endpoint, fmt in exporters_config:
        exporter = manager.add_exporter(name, endpoint, fmt)
        print(f"  📤 {name}: {endpoint}")
        
    # Simulate traces
    print("\n🔍 Creating Traces...")
    
    services = ["api-gateway", "user-service", "order-service", "payment-service", "inventory-service"]
    operations = ["HTTP GET", "HTTP POST", "gRPC Call", "Database Query", "Cache Lookup"]
    
    for i in range(20):
        # Root span
        root = manager.start_trace(
            name=f"{random.choice(operations)} /api/v1/orders",
            service_name="api-gateway",
            kind=SpanKind.SERVER,
            attributes={"http.method": "GET", "http.url": "/api/v1/orders"}
        )
        
        # Set baggage
        manager.set_baggage(root, "user-id", f"user-{random.randint(1000, 9999)}")
        manager.set_baggage(root, "request-id", str(uuid.uuid4())[:8])
        
        # Add event
        manager.add_event(root, "request_received", {"client_ip": "192.168.1.100"})
        
        # Child spans
        await asyncio.sleep(random.uniform(0.001, 0.01))
        
        child1 = manager.create_child_span(
            root,
            name="GetUser",
            service_name="user-service",
            kind=SpanKind.CLIENT
        )
        await asyncio.sleep(random.uniform(0.001, 0.02))
        manager.end_span(child1, SpanStatus.OK)
        
        child2 = manager.create_child_span(
            root,
            name="CreateOrder",
            service_name="order-service",
            kind=SpanKind.CLIENT
        )
        
        # Nested span
        child2_1 = manager.create_child_span(
            child2,
            name="ProcessPayment",
            service_name="payment-service",
            kind=SpanKind.CLIENT
        )
        await asyncio.sleep(random.uniform(0.001, 0.03))
        
        has_error = random.random() < 0.1
        manager.end_span(child2_1, 
                        SpanStatus.ERROR if has_error else SpanStatus.OK,
                        "Payment failed" if has_error else "")
        
        child2_2 = manager.create_child_span(
            child2,
            name="UpdateInventory",
            service_name="inventory-service",
            kind=SpanKind.CLIENT
        )
        await asyncio.sleep(random.uniform(0.001, 0.015))
        manager.end_span(child2_2, SpanStatus.OK)
        
        await asyncio.sleep(random.uniform(0.001, 0.01))
        manager.end_span(child2, SpanStatus.OK)
        
        # Add event before finishing
        manager.add_event(root, "request_completed", {"status": "success"})
        
        manager.end_span(root, SpanStatus.OK)
        
    print(f"  Created {len(manager.traces)} traces")
    
    # Context propagation
    print("\n🔗 Context Propagation Demo...")
    
    span = manager.start_trace("test-operation", "test-service")
    headers = manager.inject_context(span)
    print(f"  Injected headers: {headers}")
    
    extracted = manager.extract_context(headers)
    if extracted:
        print(f"  Extracted: trace_id={extracted.trace_id[:16]}..., sampled={extracted.is_sampled}")
        
    manager.end_span(span)
    
    # Display traces
    print("\n🔍 Recent Traces:")
    
    print("\n  ┌──────────────────┬─────────────────┬────────┬──────────┬─────────┐")
    print("  │ Trace ID         │ Root Operation  │ Spans  │ Duration │ Status  │")
    print("  ├──────────────────┼─────────────────┼────────┼──────────┼─────────┤")
    
    for trace_id, spans in list(manager.traces.items())[:8]:
        tid = trace_id[:16]
        root = spans[0] if spans else None
        root_name = (root.name[:15] if root else "N/A").ljust(15)
        span_count = str(len(spans)).center(6)
        
        duration = sum(s.duration_ms for s in spans if s.end_time)
        duration_str = f"{duration:.1f}ms"[:8].center(8)
        
        has_error = any(s.status == SpanStatus.ERROR for s in spans)
        status = "ERROR" if has_error else "OK"
        status = status.center(7)
        
        print(f"  │ {tid} │ {root_name} │ {span_count} │ {duration_str} │ {status} │")
        
    print("  └──────────────────┴─────────────────┴────────┴──────────┴─────────┘")
    
    # Display single trace detail
    print("\n📋 Trace Detail (first trace):")
    
    first_trace_id = list(manager.traces.keys())[0]
    first_trace = manager.get_trace(first_trace_id)
    
    for span in first_trace[:5]:
        indent = "  " if not span.parent_context else "    "
        kind_icon = {
            SpanKind.SERVER: "🖥️",
            SpanKind.CLIENT: "📱",
            SpanKind.INTERNAL: "⚙️",
            SpanKind.PRODUCER: "📤",
            SpanKind.CONSUMER: "📥"
        }.get(span.kind, "❓")
        
        status_icon = "✅" if span.status == SpanStatus.OK else "❌"
        
        print(f"{indent}{kind_icon} {span.service_name}: {span.name[:30]} {status_icon} ({span.duration_ms:.2f}ms)")
        
        if span.events:
            for event in span.events[:2]:
                print(f"{indent}  📌 {event.name}")
                
    # Service dependencies
    print("\n🔗 Service Dependencies:")
    
    print("\n  ┌─────────────────────┬─────────────────────┬────────┬────────┬──────────┐")
    print("  │ Source              │ Target              │ Calls  │ Errors │ Avg (ms) │")
    print("  ├─────────────────────┼─────────────────────┼────────┼────────┼──────────┤")
    
    deps = manager.get_service_dependencies()
    for dep in deps[:6]:
        source = dep.source[:19].ljust(19)
        target = dep.target[:19].ljust(19)
        calls = str(dep.call_count)[:6].center(6)
        errors = str(dep.error_count)[:6].center(6)
        latency = f"{dep.avg_latency_ms:.1f}"[:8].center(8)
        
        print(f"  │ {source} │ {target} │ {calls} │ {errors} │ {latency} │")
        
    print("  └─────────────────────┴─────────────────────┴────────┴────────┴──────────┘")
    
    # Operation aggregates
    print("\n📊 Operation Statistics:")
    
    print("\n  ┌───────────────────────────────┬────────┬────────┬──────────┬──────────┐")
    print("  │ Operation                     │ Count  │ Errors │ P50 (ms) │ P99 (ms) │")
    print("  ├───────────────────────────────┼────────┼────────┼──────────┼──────────┤")
    
    for key, agg in list(manager.aggregates.items())[:8]:
        op_name = f"{agg.service}:{agg.operation}"[:29].ljust(29)
        count = str(agg.trace_count)[:6].center(6)
        errors = str(agg.error_count)[:6].center(6)
        p50 = f"{agg.p50_latency_ms:.1f}"[:8].center(8)
        p99 = f"{agg.p99_latency_ms:.1f}"[:8].center(8)
        
        print(f"  │ {op_name} │ {count} │ {errors} │ {p50} │ {p99} │")
        
    print("  └───────────────────────────────┴────────┴────────┴──────────┴──────────┘")
    
    # Exporter stats
    print("\n📤 Exporter Statistics:")
    
    for exporter in manager.exporters.values():
        status = "🟢 Active" if exporter.active else "🔴 Inactive"
        print(f"  {exporter.name}: {exporter.spans_exported} spans exported {status}")
        
    # Search traces
    print("\n🔎 Search Results (traces with errors):")
    
    error_traces = manager.search_traces(has_error=True, limit=3)
    for trace_spans in error_traces:
        root = trace_spans[0] if trace_spans else None
        if root:
            error_spans = [s for s in trace_spans if s.status == SpanStatus.ERROR]
            print(f"  ❌ {root.context.trace_id[:16]}: {len(error_spans)} error span(s)")
            for es in error_spans:
                print(f"     - {es.service_name}:{es.name}: {es.status_message}")
                
    # Statistics
    print("\n📊 Tracing Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Traces: {stats['traces']}")
    print(f"  Total Spans: {stats['spans']}")
    print(f"  Error Spans: {stats['error_spans']}")
    print(f"  Samplers: {stats['samplers']}")
    print(f"  Exporters: {stats['exporters']}")
    print(f"  Dependencies: {stats['dependencies']}")
    print(f"  Operations: {stats['operations']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                  Distributed Tracing Dashboard                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Traces:                  {stats['traces']:>12}                        │")
    print(f"│ Total Spans:                   {stats['spans']:>12}                        │")
    print(f"│ Error Spans:                   {stats['error_spans']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Service Dependencies:          {stats['dependencies']:>12}                        │")
    print(f"│ Unique Operations:             {stats['operations']:>12}                        │")
    print(f"│ Active Exporters:              {stats['exporters']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Distributed Tracing Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
