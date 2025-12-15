#!/usr/bin/env python3
"""
Server Init - Iteration 360: Distributed Tracing Platform
Платформа распределённой трассировки

Функционал:
- Trace Collection - сбор трейсов
- Span Processing - обработка спанов
- Service Dependency Maps - карты зависимостей сервисов
- Trace Analysis - анализ трейсов
- Error Tracking - отслеживание ошибок
- Latency Analysis - анализ латентности
- Sampling Strategies - стратегии семплирования
- Trace Comparison - сравнение трейсов
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
import uuid
import json


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


class SamplingDecision(Enum):
    """Решение о семплировании"""
    DROP = "drop"
    RECORD_ONLY = "record_only"
    RECORD_AND_SAMPLE = "record_and_sample"


class SamplerType(Enum):
    """Тип семплера"""
    ALWAYS_ON = "always_on"
    ALWAYS_OFF = "always_off"
    PROBABILITY = "probability"
    RATE_LIMITING = "rate_limiting"
    PARENT_BASED = "parent_based"
    ADAPTIVE = "adaptive"


class TraceState(Enum):
    """Состояние трейса"""
    ACTIVE = "active"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class TraceContext:
    """Контекст трейса"""
    trace_id: str
    span_id: str
    
    # Flags
    trace_flags: int = 1  # 1 = sampled
    
    # Parent
    parent_span_id: Optional[str] = None
    
    # State
    trace_state: str = ""


@dataclass
class SpanEvent:
    """Событие спана"""
    event_id: str
    name: str
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Attributes
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SpanLink:
    """Связь спана"""
    link_id: str
    
    # Linked trace/span
    trace_id: str = ""
    span_id: str = ""
    
    # Attributes
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Span:
    """Спан"""
    span_id: str
    trace_id: str
    
    # Name
    name: str = ""
    
    # Kind
    kind: SpanKind = SpanKind.INTERNAL
    
    # Parent
    parent_span_id: Optional[str] = None
    
    # Service
    service_name: str = ""
    
    # Timing
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_us: int = 0
    
    # Status
    status: SpanStatus = SpanStatus.UNSET
    status_message: str = ""
    
    # Attributes
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    # Resource
    resource: Dict[str, str] = field(default_factory=dict)
    
    # Events
    events: List[SpanEvent] = field(default_factory=list)
    
    # Links
    links: List[SpanLink] = field(default_factory=list)
    
    # Dropped counts
    dropped_attributes: int = 0
    dropped_events: int = 0
    dropped_links: int = 0


@dataclass
class Trace:
    """Трейс"""
    trace_id: str
    
    # Root span
    root_span_id: str = ""
    
    # Services
    services: Set[str] = field(default_factory=set)
    
    # Spans
    span_ids: List[str] = field(default_factory=list)
    span_count: int = 0
    
    # Timing
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_us: int = 0
    
    # Status
    state: TraceState = TraceState.ACTIVE
    has_errors: bool = False
    error_count: int = 0
    
    # Depth
    max_depth: int = 0


@dataclass
class Service:
    """Сервис"""
    service_id: str
    name: str
    
    # Metadata
    version: str = ""
    environment: str = ""
    
    # Resource attributes
    resource_attributes: Dict[str, str] = field(default_factory=dict)
    
    # Stats
    trace_count: int = 0
    span_count: int = 0
    error_count: int = 0
    
    # Latency
    avg_latency_us: float = 0.0
    p50_latency_us: float = 0.0
    p95_latency_us: float = 0.0
    p99_latency_us: float = 0.0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_seen: Optional[datetime] = None


@dataclass
class ServiceDependency:
    """Зависимость сервиса"""
    dependency_id: str
    
    # Source and target
    source_service: str = ""
    target_service: str = ""
    
    # Stats
    call_count: int = 0
    error_count: int = 0
    
    # Latency
    avg_latency_us: float = 0.0
    
    # Timestamps
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: Optional[datetime] = None


@dataclass
class Sampler:
    """Семплер"""
    sampler_id: str
    name: str
    
    # Type
    sampler_type: SamplerType = SamplerType.PROBABILITY
    
    # Config
    probability: float = 1.0
    rate_limit: int = 100  # traces per second
    
    # Parent-based config
    root_sampler_type: Optional[SamplerType] = None
    
    # Status
    is_enabled: bool = True
    
    # Stats
    total_decisions: int = 0
    sampled_count: int = 0
    dropped_count: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TraceQuery:
    """Запрос трейсов"""
    query_id: str
    
    # Filters
    service_name: Optional[str] = None
    operation_name: Optional[str] = None
    
    # Time range
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime = field(default_factory=datetime.now)
    
    # Duration filter
    min_duration_us: Optional[int] = None
    max_duration_us: Optional[int] = None
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Errors only
    errors_only: bool = False
    
    # Limit
    limit: int = 100
    
    # Execution
    executed_at: datetime = field(default_factory=datetime.now)
    duration_ms: float = 0.0


@dataclass
class TraceSearchResult:
    """Результат поиска трейсов"""
    result_id: str
    query_id: str
    
    # Traces
    traces: List[Trace] = field(default_factory=list)
    total_count: int = 0
    
    # Stats
    avg_duration_us: float = 0.0
    error_rate: float = 0.0


@dataclass
class ServiceMap:
    """Карта сервисов"""
    map_id: str
    name: str
    
    # Nodes (services)
    nodes: List[Dict[str, Any]] = field(default_factory=list)
    
    # Edges (dependencies)
    edges: List[Dict[str, Any]] = field(default_factory=list)
    
    # Time range
    time_range: str = "1h"
    
    # Timestamps
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class LatencyHistogram:
    """Гистограмма латентности"""
    histogram_id: str
    service_name: str
    operation_name: str
    
    # Buckets
    buckets: List[Tuple[int, int]] = field(default_factory=list)  # (upper_bound_us, count)
    
    # Stats
    total_count: int = 0
    sum_us: int = 0
    
    # Percentiles
    p50_us: float = 0.0
    p75_us: float = 0.0
    p90_us: float = 0.0
    p95_us: float = 0.0
    p99_us: float = 0.0
    
    # Timestamps
    collected_at: datetime = field(default_factory=datetime.now)


@dataclass
class ErrorGroup:
    """Группа ошибок"""
    group_id: str
    
    # Error info
    error_type: str = ""
    error_message: str = ""
    
    # Services affected
    services: Set[str] = field(default_factory=set)
    
    # Stats
    occurrence_count: int = 0
    affected_traces: int = 0
    
    # Sample traces
    sample_trace_ids: List[str] = field(default_factory=list)
    
    # Timestamps
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: Optional[datetime] = None


@dataclass
class TraceComparison:
    """Сравнение трейсов"""
    comparison_id: str
    
    # Traces
    trace_id_a: str = ""
    trace_id_b: str = ""
    
    # Differences
    duration_diff_us: int = 0
    span_count_diff: int = 0
    service_diff: List[str] = field(default_factory=list)
    
    # Similar spans
    matching_spans: List[Tuple[str, str]] = field(default_factory=list)
    
    # Missing spans
    missing_in_a: List[str] = field(default_factory=list)
    missing_in_b: List[str] = field(default_factory=list)


@dataclass
class TracingMetrics:
    """Метрики платформы трассировки"""
    metrics_id: str
    
    # Services
    total_services: int = 0
    
    # Traces
    total_traces: int = 0
    traces_with_errors: int = 0
    
    # Spans
    total_spans: int = 0
    
    # Latency
    avg_trace_duration_us: float = 0.0
    
    # Sampling
    sampling_rate: float = 0.0
    
    # Errors
    error_groups: int = 0
    
    # Dependencies
    total_dependencies: int = 0
    
    # Timestamps
    collected_at: datetime = field(default_factory=datetime.now)


class DistributedTracingPlatform:
    """Платформа распределённой трассировки"""
    
    def __init__(self, platform_name: str = "tracing"):
        self.platform_name = platform_name
        self.services: Dict[str, Service] = {}
        self.traces: Dict[str, Trace] = {}
        self.spans: Dict[str, Span] = {}
        self.dependencies: Dict[str, ServiceDependency] = {}
        self.samplers: Dict[str, Sampler] = {}
        self.queries: Dict[str, TraceQuery] = {}
        self.error_groups: Dict[str, ErrorGroup] = {}
        self.service_maps: Dict[str, ServiceMap] = {}
        self.latency_histograms: Dict[str, LatencyHistogram] = {}
        
    async def register_service(self, name: str,
                              version: str = "",
                              environment: str = "production",
                              resource_attributes: Dict[str, str] = None) -> Service:
        """Регистрация сервиса"""
        service = Service(
            service_id=f"svc_{uuid.uuid4().hex[:8]}",
            name=name,
            version=version,
            environment=environment,
            resource_attributes=resource_attributes or {}
        )
        
        self.services[service.service_id] = service
        return service
        
    async def start_trace(self, service_name: str,
                         operation_name: str,
                         kind: SpanKind = SpanKind.SERVER,
                         attributes: Dict[str, Any] = None) -> Tuple[Trace, Span]:
        """Начало трейса"""
        trace_id = uuid.uuid4().hex
        span_id = uuid.uuid4().hex[:16]
        
        trace = Trace(
            trace_id=trace_id,
            root_span_id=span_id,
            services={service_name},
            span_ids=[span_id],
            span_count=1
        )
        
        span = Span(
            span_id=span_id,
            trace_id=trace_id,
            name=operation_name,
            kind=kind,
            service_name=service_name,
            attributes=attributes or {},
            resource={"service.name": service_name}
        )
        
        self.traces[trace_id] = trace
        self.spans[span_id] = span
        
        # Update service stats
        service = next((s for s in self.services.values() if s.name == service_name), None)
        if service:
            service.trace_count += 1
            service.span_count += 1
            service.last_seen = datetime.now()
            
        return trace, span
        
    async def start_span(self, trace_id: str,
                        parent_span_id: str,
                        service_name: str,
                        operation_name: str,
                        kind: SpanKind = SpanKind.INTERNAL,
                        attributes: Dict[str, Any] = None) -> Optional[Span]:
        """Начало спана"""
        trace = self.traces.get(trace_id)
        if not trace:
            return None
            
        span = Span(
            span_id=uuid.uuid4().hex[:16],
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            name=operation_name,
            kind=kind,
            service_name=service_name,
            attributes=attributes or {},
            resource={"service.name": service_name}
        )
        
        self.spans[span.span_id] = span
        trace.span_ids.append(span.span_id)
        trace.span_count += 1
        trace.services.add(service_name)
        
        # Calculate depth
        depth = 1
        current_parent = parent_span_id
        while current_parent:
            depth += 1
            parent_span = self.spans.get(current_parent)
            current_parent = parent_span.parent_span_id if parent_span else None
        trace.max_depth = max(trace.max_depth, depth)
        
        # Update service stats
        service = next((s for s in self.services.values() if s.name == service_name), None)
        if service:
            service.span_count += 1
            service.last_seen = datetime.now()
            
        # Track dependency
        parent_span = self.spans.get(parent_span_id)
        if parent_span and parent_span.service_name != service_name:
            await self._track_dependency(parent_span.service_name, service_name)
            
        return span
        
    async def _track_dependency(self, source: str, target: str):
        """Отслеживание зависимости"""
        dep_key = f"{source}->{target}"
        
        if dep_key not in self.dependencies:
            self.dependencies[dep_key] = ServiceDependency(
                dependency_id=f"dep_{uuid.uuid4().hex[:8]}",
                source_service=source,
                target_service=target
            )
            
        dep = self.dependencies[dep_key]
        dep.call_count += 1
        dep.last_seen = datetime.now()
        
    async def end_span(self, span_id: str,
                      status: SpanStatus = SpanStatus.OK,
                      status_message: str = "",
                      attributes: Dict[str, Any] = None) -> Optional[Span]:
        """Завершение спана"""
        span = self.spans.get(span_id)
        if not span:
            return None
            
        span.end_time = datetime.now()
        span.duration_us = int((span.end_time - span.start_time).total_seconds() * 1_000_000)
        span.status = status
        span.status_message = status_message
        
        if attributes:
            span.attributes.update(attributes)
            
        # Update trace
        trace = self.traces.get(span.trace_id)
        if trace:
            if status == SpanStatus.ERROR:
                trace.has_errors = True
                trace.error_count += 1
                
                # Track error group
                await self._track_error(span.trace_id, status_message, span.service_name)
                
            # Check if this is the root span
            if span.span_id == trace.root_span_id:
                trace.end_time = span.end_time
                trace.duration_us = span.duration_us
                trace.state = TraceState.ERROR if trace.has_errors else TraceState.COMPLETE
                
        return span
        
    async def _track_error(self, trace_id: str, error_message: str, service_name: str):
        """Отслеживание ошибки"""
        # Simple grouping by error message prefix
        error_key = error_message[:50] if error_message else "unknown"
        
        if error_key not in self.error_groups:
            self.error_groups[error_key] = ErrorGroup(
                group_id=f"err_{uuid.uuid4().hex[:8]}",
                error_type="error",
                error_message=error_message
            )
            
        group = self.error_groups[error_key]
        group.occurrence_count += 1
        group.services.add(service_name)
        group.affected_traces += 1
        group.last_seen = datetime.now()
        
        if len(group.sample_trace_ids) < 5:
            group.sample_trace_ids.append(trace_id)
            
    async def add_span_event(self, span_id: str,
                            name: str,
                            attributes: Dict[str, Any] = None) -> Optional[SpanEvent]:
        """Добавление события спана"""
        span = self.spans.get(span_id)
        if not span:
            return None
            
        event = SpanEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            name=name,
            attributes=attributes or {}
        )
        
        span.events.append(event)
        return event
        
    async def add_span_link(self, span_id: str,
                           linked_trace_id: str,
                           linked_span_id: str,
                           attributes: Dict[str, Any] = None) -> Optional[SpanLink]:
        """Добавление связи спана"""
        span = self.spans.get(span_id)
        if not span:
            return None
            
        link = SpanLink(
            link_id=f"lnk_{uuid.uuid4().hex[:8]}",
            trace_id=linked_trace_id,
            span_id=linked_span_id,
            attributes=attributes or {}
        )
        
        span.links.append(link)
        return link
        
    async def create_sampler(self, name: str,
                            sampler_type: SamplerType,
                            probability: float = 1.0,
                            rate_limit: int = 100) -> Sampler:
        """Создание семплера"""
        sampler = Sampler(
            sampler_id=f"smp_{uuid.uuid4().hex[:8]}",
            name=name,
            sampler_type=sampler_type,
            probability=probability,
            rate_limit=rate_limit
        )
        
        self.samplers[sampler.sampler_id] = sampler
        return sampler
        
    async def should_sample(self, sampler_id: str,
                           trace_id: str,
                           parent_context: Optional[TraceContext] = None) -> SamplingDecision:
        """Принятие решения о семплировании"""
        sampler = self.samplers.get(sampler_id)
        if not sampler or not sampler.is_enabled:
            return SamplingDecision.DROP
            
        sampler.total_decisions += 1
        
        decision = SamplingDecision.DROP
        
        if sampler.sampler_type == SamplerType.ALWAYS_ON:
            decision = SamplingDecision.RECORD_AND_SAMPLE
        elif sampler.sampler_type == SamplerType.ALWAYS_OFF:
            decision = SamplingDecision.DROP
        elif sampler.sampler_type == SamplerType.PROBABILITY:
            if random.random() < sampler.probability:
                decision = SamplingDecision.RECORD_AND_SAMPLE
        elif sampler.sampler_type == SamplerType.RATE_LIMITING:
            # Simplified rate limiting
            if sampler.sampled_count < sampler.rate_limit:
                decision = SamplingDecision.RECORD_AND_SAMPLE
        elif sampler.sampler_type == SamplerType.PARENT_BASED:
            if parent_context and parent_context.trace_flags & 1:
                decision = SamplingDecision.RECORD_AND_SAMPLE
            elif random.random() < sampler.probability:
                decision = SamplingDecision.RECORD_AND_SAMPLE
                
        if decision == SamplingDecision.RECORD_AND_SAMPLE:
            sampler.sampled_count += 1
        else:
            sampler.dropped_count += 1
            
        return decision
        
    async def search_traces(self, service_name: Optional[str] = None,
                           operation_name: Optional[str] = None,
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None,
                           min_duration_us: Optional[int] = None,
                           max_duration_us: Optional[int] = None,
                           tags: Dict[str, str] = None,
                           errors_only: bool = False,
                           limit: int = 100) -> TraceSearchResult:
        """Поиск трейсов"""
        query = TraceQuery(
            query_id=f"qry_{uuid.uuid4().hex[:8]}",
            service_name=service_name,
            operation_name=operation_name,
            start_time=start_time or datetime.now() - timedelta(hours=1),
            end_time=end_time or datetime.now(),
            min_duration_us=min_duration_us,
            max_duration_us=max_duration_us,
            tags=tags or {},
            errors_only=errors_only,
            limit=limit
        )
        
        # Search traces
        matching_traces = []
        
        for trace in self.traces.values():
            # Service filter
            if service_name and service_name not in trace.services:
                continue
                
            # Time filter
            if trace.start_time < query.start_time or trace.start_time > query.end_time:
                continue
                
            # Duration filter
            if min_duration_us and trace.duration_us < min_duration_us:
                continue
            if max_duration_us and trace.duration_us > max_duration_us:
                continue
                
            # Errors only
            if errors_only and not trace.has_errors:
                continue
                
            # Operation filter (check root span)
            if operation_name:
                root_span = self.spans.get(trace.root_span_id)
                if not root_span or operation_name not in root_span.name:
                    continue
                    
            matching_traces.append(trace)
            
            if len(matching_traces) >= limit:
                break
                
        query.duration_ms = random.uniform(1, 50)
        self.queries[query.query_id] = query
        
        # Calculate stats
        durations = [t.duration_us for t in matching_traces if t.duration_us > 0]
        errors = sum(1 for t in matching_traces if t.has_errors)
        
        return TraceSearchResult(
            result_id=f"res_{uuid.uuid4().hex[:8]}",
            query_id=query.query_id,
            traces=matching_traces,
            total_count=len(matching_traces),
            avg_duration_us=sum(durations) / len(durations) if durations else 0.0,
            error_rate=(errors / len(matching_traces)) * 100 if matching_traces else 0.0
        )
        
    async def get_trace(self, trace_id: str) -> Optional[Tuple[Trace, List[Span]]]:
        """Получение трейса со спанами"""
        trace = self.traces.get(trace_id)
        if not trace:
            return None
            
        spans = [self.spans[sid] for sid in trace.span_ids if sid in self.spans]
        return trace, spans
        
    async def generate_service_map(self, time_range: str = "1h") -> ServiceMap:
        """Генерация карты сервисов"""
        nodes = []
        edges = []
        
        # Generate nodes
        for service in self.services.values():
            nodes.append({
                "id": service.service_id,
                "name": service.name,
                "version": service.version,
                "trace_count": service.trace_count,
                "error_count": service.error_count,
                "avg_latency_us": service.avg_latency_us
            })
            
        # Generate edges
        for dep in self.dependencies.values():
            edges.append({
                "source": dep.source_service,
                "target": dep.target_service,
                "call_count": dep.call_count,
                "error_count": dep.error_count,
                "avg_latency_us": dep.avg_latency_us
            })
            
        service_map = ServiceMap(
            map_id=f"map_{uuid.uuid4().hex[:8]}",
            name="Service Dependency Map",
            nodes=nodes,
            edges=edges,
            time_range=time_range
        )
        
        self.service_maps[service_map.map_id] = service_map
        return service_map
        
    async def calculate_latency_histogram(self, service_name: str,
                                         operation_name: str = "*") -> LatencyHistogram:
        """Расчёт гистограммы латентности"""
        durations = []
        
        for span in self.spans.values():
            if span.service_name != service_name:
                continue
            if operation_name != "*" and operation_name not in span.name:
                continue
            if span.duration_us > 0:
                durations.append(span.duration_us)
                
        # Create histogram buckets
        bucket_boundaries = [100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000]
        buckets = []
        
        for boundary in bucket_boundaries:
            count = sum(1 for d in durations if d <= boundary)
            buckets.append((boundary, count))
            
        # Calculate percentiles
        sorted_durations = sorted(durations)
        
        def percentile(p):
            if not sorted_durations:
                return 0.0
            idx = int(len(sorted_durations) * p)
            return float(sorted_durations[min(idx, len(sorted_durations) - 1)])
            
        histogram = LatencyHistogram(
            histogram_id=f"hist_{uuid.uuid4().hex[:8]}",
            service_name=service_name,
            operation_name=operation_name,
            buckets=buckets,
            total_count=len(durations),
            sum_us=sum(durations),
            p50_us=percentile(0.50),
            p75_us=percentile(0.75),
            p90_us=percentile(0.90),
            p95_us=percentile(0.95),
            p99_us=percentile(0.99)
        )
        
        self.latency_histograms[histogram.histogram_id] = histogram
        return histogram
        
    async def compare_traces(self, trace_id_a: str, trace_id_b: str) -> Optional[TraceComparison]:
        """Сравнение трейсов"""
        trace_a = self.traces.get(trace_id_a)
        trace_b = self.traces.get(trace_id_b)
        
        if not trace_a or not trace_b:
            return None
            
        comparison = TraceComparison(
            comparison_id=f"cmp_{uuid.uuid4().hex[:8]}",
            trace_id_a=trace_id_a,
            trace_id_b=trace_id_b,
            duration_diff_us=trace_a.duration_us - trace_b.duration_us,
            span_count_diff=trace_a.span_count - trace_b.span_count,
            service_diff=list(trace_a.services.symmetric_difference(trace_b.services))
        )
        
        return comparison
        
    async def collect_metrics(self) -> TracingMetrics:
        """Сбор метрик платформы"""
        traces_with_errors = sum(1 for t in self.traces.values() if t.has_errors)
        durations = [t.duration_us for t in self.traces.values() if t.duration_us > 0]
        
        total_sampled = sum(s.sampled_count for s in self.samplers.values())
        total_decisions = sum(s.total_decisions for s in self.samplers.values())
        
        return TracingMetrics(
            metrics_id=f"tm_{uuid.uuid4().hex[:8]}",
            total_services=len(self.services),
            total_traces=len(self.traces),
            traces_with_errors=traces_with_errors,
            total_spans=len(self.spans),
            avg_trace_duration_us=sum(durations) / len(durations) if durations else 0.0,
            sampling_rate=(total_sampled / total_decisions) * 100 if total_decisions > 0 else 100.0,
            error_groups=len(self.error_groups),
            total_dependencies=len(self.dependencies)
        )
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        traces_with_errors = sum(1 for t in self.traces.values() if t.has_errors)
        total_errors = sum(t.error_count for t in self.traces.values())
        
        durations = [t.duration_us for t in self.traces.values() if t.duration_us > 0]
        
        return {
            "total_services": len(self.services),
            "total_traces": len(self.traces),
            "traces_with_errors": traces_with_errors,
            "total_spans": len(self.spans),
            "total_errors": total_errors,
            "avg_duration_us": sum(durations) / len(durations) if durations else 0.0,
            "total_dependencies": len(self.dependencies),
            "total_samplers": len(self.samplers),
            "error_groups": len(self.error_groups),
            "service_maps": len(self.service_maps)
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 360: Distributed Tracing Platform")
    print("=" * 60)
    
    platform = DistributedTracingPlatform(platform_name="enterprise-tracing")
    print("✓ Distributed Tracing Platform initialized")
    
    # Register Services
    print("\n🔧 Registering Services...")
    
    services_data = [
        ("api-gateway", "2.1.0", {"k8s.namespace": "production", "k8s.pod.name": "api-gateway-abc123"}),
        ("auth-service", "1.5.0", {"k8s.namespace": "production", "k8s.pod.name": "auth-service-def456"}),
        ("user-service", "3.0.0", {"k8s.namespace": "production", "k8s.pod.name": "user-service-ghi789"}),
        ("order-service", "2.3.0", {"k8s.namespace": "production", "k8s.pod.name": "order-service-jkl012"}),
        ("inventory-service", "1.8.0", {"k8s.namespace": "production", "k8s.pod.name": "inventory-service-mno345"}),
        ("payment-service", "2.0.0", {"k8s.namespace": "production", "k8s.pod.name": "payment-service-pqr678"}),
        ("notification-service", "1.2.0", {"k8s.namespace": "production", "k8s.pod.name": "notification-service-stu901"}),
        ("postgres", "14.0", {"db.type": "postgresql"}),
        ("redis", "7.0", {"cache.type": "redis"}),
        ("kafka", "3.4", {"messaging.system": "kafka"})
    ]
    
    for name, version, attrs in services_data:
        await platform.register_service(name, version, "production", attrs)
        print(f"  🔧 {name} v{version}")
        
    # Create Samplers
    print("\n🎲 Creating Samplers...")
    
    samplers_data = [
        ("production-sampler", SamplerType.PROBABILITY, 0.1),
        ("debug-sampler", SamplerType.ALWAYS_ON, 1.0),
        ("rate-limiter", SamplerType.RATE_LIMITING, 0.5),
        ("adaptive-sampler", SamplerType.ADAPTIVE, 0.2)
    ]
    
    for name, stype, prob in samplers_data:
        await platform.create_sampler(name, stype, prob)
        print(f"  🎲 {name} ({stype.value})")
        
    # Generate Traces
    print("\n🔍 Generating Distributed Traces...")
    
    operations = [
        ("HTTP GET /api/orders", SpanKind.SERVER),
        ("HTTP POST /api/orders", SpanKind.SERVER),
        ("HTTP GET /api/users/{id}", SpanKind.SERVER),
        ("HTTP POST /api/auth/login", SpanKind.SERVER),
        ("HTTP GET /api/inventory/{id}", SpanKind.SERVER)
    ]
    
    traces = []
    for i in range(30):
        op_name, kind = random.choice(operations)
        
        # Start trace at API Gateway
        trace, root_span = await platform.start_trace("api-gateway", op_name, kind, {
            "http.method": op_name.split()[1],
            "http.url": op_name.split()[2],
            "http.user_agent": "Mozilla/5.0"
        })
        traces.append(trace)
        
        # Add auth span
        auth_span = await platform.start_span(
            trace.trace_id, root_span.span_id,
            "auth-service", "validate_token", SpanKind.CLIENT,
            {"auth.method": "jwt"}
        )
        await asyncio.sleep(0.001)
        await platform.end_span(auth_span.span_id)
        
        # Add service-specific spans
        if "orders" in op_name:
            order_span = await platform.start_span(
                trace.trace_id, root_span.span_id,
                "order-service", "process_order", SpanKind.CLIENT,
                {"order.id": f"ORD-{random.randint(10000, 99999)}"}
            )
            
            # DB call
            db_span = await platform.start_span(
                trace.trace_id, order_span.span_id,
                "postgres", "SELECT * FROM orders", SpanKind.CLIENT,
                {"db.system": "postgresql", "db.name": "orders"}
            )
            await asyncio.sleep(0.001)
            await platform.end_span(db_span.span_id)
            
            # Inventory check
            inv_span = await platform.start_span(
                trace.trace_id, order_span.span_id,
                "inventory-service", "check_availability", SpanKind.CLIENT
            )
            await asyncio.sleep(0.001)
            await platform.end_span(inv_span.span_id)
            
            # Payment
            if "POST" in op_name:
                pay_span = await platform.start_span(
                    trace.trace_id, order_span.span_id,
                    "payment-service", "process_payment", SpanKind.CLIENT,
                    {"payment.method": "credit_card"}
                )
                await asyncio.sleep(0.001)
                
                # Simulate occasional payment errors
                pay_status = SpanStatus.ERROR if random.random() < 0.1 else SpanStatus.OK
                await platform.end_span(pay_span.span_id, pay_status, "Payment declined" if pay_status == SpanStatus.ERROR else "")
                
            await platform.end_span(order_span.span_id)
            
        elif "users" in op_name:
            user_span = await platform.start_span(
                trace.trace_id, root_span.span_id,
                "user-service", "get_user", SpanKind.CLIENT
            )
            
            # Cache check
            cache_span = await platform.start_span(
                trace.trace_id, user_span.span_id,
                "redis", "GET user:*", SpanKind.CLIENT,
                {"db.system": "redis", "db.operation": "GET"}
            )
            await asyncio.sleep(0.001)
            await platform.end_span(cache_span.span_id)
            
            await platform.end_span(user_span.span_id)
            
        # End root span
        root_status = SpanStatus.ERROR if random.random() < 0.05 else SpanStatus.OK
        await platform.end_span(root_span.span_id, root_status, "Internal error" if root_status == SpanStatus.ERROR else "")
        
    print(f"  🔍 Generated {len(platform.traces)} traces with {len(platform.spans)} spans")
    
    # Search Traces
    print("\n🔎 Searching Traces...")
    
    # Search all
    all_result = await platform.search_traces(limit=100)
    print(f"  🔎 All traces: {all_result.total_count}")
    
    # Search by service
    order_result = await platform.search_traces(service_name="order-service", limit=50)
    print(f"  🔎 Order service traces: {order_result.total_count}")
    
    # Search errors only
    error_result = await platform.search_traces(errors_only=True, limit=50)
    print(f"  🔎 Error traces: {error_result.total_count}")
    
    # Search slow traces
    slow_result = await platform.search_traces(min_duration_us=10000, limit=50)
    print(f"  🔎 Slow traces (>10ms): {slow_result.total_count}")
    
    # Generate Service Map
    print("\n🗺️ Generating Service Map...")
    
    service_map = await platform.generate_service_map()
    print(f"  🗺️ Map with {len(service_map.nodes)} services and {len(service_map.edges)} dependencies")
    
    # Calculate Latency Histograms
    print("\n📊 Calculating Latency Histograms...")
    
    for service_name in ["api-gateway", "order-service", "payment-service"]:
        histogram = await platform.calculate_latency_histogram(service_name)
        print(f"  📊 {service_name}: p50={histogram.p50_us:.0f}µs, p95={histogram.p95_us:.0f}µs, p99={histogram.p99_us:.0f}µs")
        
    # Sampling Decisions
    print("\n🎲 Sampling Decisions...")
    
    sampler = list(platform.samplers.values())[0]
    for _ in range(100):
        await platform.should_sample(sampler.sampler_id, uuid.uuid4().hex)
        
    print(f"  🎲 {sampler.name}: {sampler.sampled_count}/{sampler.total_decisions} sampled")
    
    # Collect Metrics
    metrics = await platform.collect_metrics()
    
    # Services Dashboard
    print("\n🔧 Services:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Service Name              │ Version    │ Traces    │ Spans     │ Errors    │ Last Seen                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for svc in platform.services.values():
        name = svc.name[:25].ljust(25)
        version = svc.version[:10].ljust(10)
        traces_cnt = str(svc.trace_count).ljust(9)
        spans_cnt = str(svc.span_count).ljust(9)
        errors = str(svc.error_count).ljust(9)
        last_seen = svc.last_seen.strftime("%H:%M:%S") if svc.last_seen else "N/A"
        last_seen = last_seen.ljust(244)
        
        print(f"  │ {name} │ {version} │ {traces_cnt} │ {spans_cnt} │ {errors} │ {last_seen} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Dependencies Dashboard
    print("\n🔗 Service Dependencies:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Source                    │ Target                    │ Calls     │ Errors    │ Error Rate                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for dep in sorted(platform.dependencies.values(), key=lambda x: x.call_count, reverse=True)[:10]:
        source = dep.source_service[:25].ljust(25)
        target = dep.target_service[:25].ljust(25)
        calls = str(dep.call_count).ljust(9)
        errors = str(dep.error_count).ljust(9)
        error_rate = f"{(dep.error_count / dep.call_count * 100) if dep.call_count > 0 else 0:.1f}%"
        error_rate = error_rate.ljust(218)
        
        print(f"  │ {source} │ {target} │ {calls} │ {errors} │ {error_rate} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Error Groups
    print("\n❌ Error Groups:")
    
    for group in sorted(platform.error_groups.values(), key=lambda x: x.occurrence_count, reverse=True)[:5]:
        print(f"  - {group.error_message[:50]}... ({group.occurrence_count} occurrences)")
        
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Services: {stats['total_services']}")
    print(f"  Traces: {stats['total_traces']} ({stats['traces_with_errors']} with errors)")
    print(f"  Spans: {stats['total_spans']}")
    print(f"  Avg Duration: {stats['avg_duration_us']:.0f}µs ({stats['avg_duration_us']/1000:.2f}ms)")
    print(f"  Dependencies: {stats['total_dependencies']}")
    print(f"  Error Groups: {stats['error_groups']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Distributed Tracing Platform                     │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Services:                {stats['total_services']:>12}                      │")
    print(f"│ Total Dependencies:            {stats['total_dependencies']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Traces:                  {stats['total_traces']:>12}                      │")
    print(f"│ Traces with Errors:            {stats['traces_with_errors']:>12}                      │")
    print(f"│ Total Spans:                   {stats['total_spans']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Avg Trace Duration (µs):       {stats['avg_duration_us']:>12.0f}                      │")
    print(f"│ Sampling Rate (%):             {metrics.sampling_rate:>12.1f}                      │")
    print(f"│ Error Groups:                  {stats['error_groups']:>12}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Distributed Tracing Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
