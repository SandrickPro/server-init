#!/usr/bin/env python3
"""
Server Init - Iteration 188: Distributed Tracing Platform
Платформа распределённой трассировки

Функционал:
- Trace Collection - сбор трейсов
- Span Management - управление спанами
- Context Propagation - распространение контекста
- Service Maps - карты сервисов
- Latency Analysis - анализ задержек
- Error Tracking - отслеживание ошибок
- Sampling Strategies - стратегии семплинга
- Trace Search - поиск трейсов
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
import uuid
import time


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
    """Решение о семплинге"""
    DROP = "drop"
    RECORD_ONLY = "record_only"
    RECORD_AND_SAMPLE = "record_and_sample"


@dataclass
class SpanContext:
    """Контекст спана"""
    trace_id: str
    span_id: str
    trace_flags: int = 1  # sampled
    trace_state: str = ""


@dataclass
class SpanEvent:
    """Событие спана"""
    name: str
    timestamp: datetime = field(default_factory=datetime.now)
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SpanLink:
    """Связь спана"""
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
    
    # Status
    status: SpanStatus = SpanStatus.UNSET
    status_message: str = ""
    
    # Attributes
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    # Events and links
    events: List[SpanEvent] = field(default_factory=list)
    links: List[SpanLink] = field(default_factory=list)
    
    @property
    def duration_ms(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0
        
    def add_event(self, name: str, attributes: Dict = None):
        """Добавление события"""
        self.events.append(SpanEvent(name=name, attributes=attributes or {}))
        
    def set_error(self, message: str):
        """Установка ошибки"""
        self.status = SpanStatus.ERROR
        self.status_message = message


@dataclass
class Trace:
    """Трейс"""
    trace_id: str
    
    # Spans
    spans: List[Span] = field(default_factory=list)
    
    # Root span
    root_span_id: Optional[str] = None
    
    # Services involved
    services: Set[str] = field(default_factory=set)
    
    # Timing
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @property
    def duration_ms(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0
        
    @property
    def span_count(self) -> int:
        return len(self.spans)
        
    @property
    def has_error(self) -> bool:
        return any(s.status == SpanStatus.ERROR for s in self.spans)


@dataclass
class ServiceNode:
    """Узел сервиса"""
    service_name: str
    
    # Stats
    request_count: int = 0
    error_count: int = 0
    avg_latency_ms: float = 0.0
    
    # Connections
    upstream: Set[str] = field(default_factory=set)
    downstream: Set[str] = field(default_factory=set)


class TraceCollector:
    """Сборщик трейсов"""
    
    def __init__(self):
        self.traces: Dict[str, Trace] = {}
        self.spans: Dict[str, Span] = {}
        
    def start_trace(self) -> str:
        """Начало нового трейса"""
        trace_id = uuid.uuid4().hex[:32]
        self.traces[trace_id] = Trace(trace_id=trace_id)
        return trace_id
        
    def start_span(self, trace_id: str, name: str, service_name: str,
                  kind: SpanKind = SpanKind.INTERNAL,
                  parent_span_id: str = None) -> Span:
        """Начало спана"""
        span = Span(
            span_id=uuid.uuid4().hex[:16],
            trace_id=trace_id,
            name=name,
            service_name=service_name,
            kind=kind,
            parent_span_id=parent_span_id
        )
        
        self.spans[span.span_id] = span
        
        trace = self.traces.get(trace_id)
        if trace:
            trace.spans.append(span)
            trace.services.add(service_name)
            
            if not parent_span_id:
                trace.root_span_id = span.span_id
                trace.start_time = span.start_time
                
        return span
        
    def end_span(self, span_id: str, status: SpanStatus = SpanStatus.OK):
        """Завершение спана"""
        span = self.spans.get(span_id)
        if span:
            span.end_time = datetime.now()
            span.status = status
            
            trace = self.traces.get(span.trace_id)
            if trace and span.span_id == trace.root_span_id:
                trace.end_time = span.end_time


class Sampler:
    """Семплер"""
    
    def __init__(self, rate: float = 1.0):
        self.rate = rate  # 0.0 to 1.0
        self.always_sample_errors = True
        
    def should_sample(self, trace_id: str, has_error: bool = False) -> SamplingDecision:
        """Решение о семплинге"""
        if has_error and self.always_sample_errors:
            return SamplingDecision.RECORD_AND_SAMPLE
            
        if random.random() < self.rate:
            return SamplingDecision.RECORD_AND_SAMPLE
            
        return SamplingDecision.DROP


class LatencyAnalyzer:
    """Анализатор задержек"""
    
    def __init__(self, collector: TraceCollector):
        self.collector = collector
        
    def analyze_trace(self, trace_id: str) -> Dict[str, Any]:
        """Анализ задержек трейса"""
        trace = self.collector.traces.get(trace_id)
        if not trace:
            return {}
            
        span_latencies = {}
        service_latencies = {}
        
        for span in trace.spans:
            span_latencies[span.span_id] = span.duration_ms
            
            if span.service_name not in service_latencies:
                service_latencies[span.service_name] = []
            service_latencies[span.service_name].append(span.duration_ms)
            
        return {
            "total_duration_ms": trace.duration_ms,
            "span_count": trace.span_count,
            "service_latencies": {
                svc: {"avg": sum(lats)/len(lats), "max": max(lats), "min": min(lats)}
                for svc, lats in service_latencies.items()
            },
            "critical_path": self._find_critical_path(trace)
        }
        
    def _find_critical_path(self, trace: Trace) -> List[str]:
        """Поиск критического пути"""
        # Simple critical path - longest chain
        path = []
        
        root_span = next((s for s in trace.spans if s.span_id == trace.root_span_id), None)
        if root_span:
            path.append(f"{root_span.service_name}/{root_span.name}")
            
            # Find children
            current = root_span.span_id
            while True:
                children = [s for s in trace.spans if s.parent_span_id == current]
                if not children:
                    break
                longest = max(children, key=lambda s: s.duration_ms)
                path.append(f"{longest.service_name}/{longest.name}")
                current = longest.span_id
                
        return path


class ServiceMapBuilder:
    """Построитель карты сервисов"""
    
    def __init__(self, collector: TraceCollector):
        self.collector = collector
        
    def build_map(self) -> Dict[str, ServiceNode]:
        """Построение карты"""
        nodes: Dict[str, ServiceNode] = {}
        
        for trace in self.collector.traces.values():
            for span in trace.spans:
                if span.service_name not in nodes:
                    nodes[span.service_name] = ServiceNode(service_name=span.service_name)
                    
                node = nodes[span.service_name]
                node.request_count += 1
                
                if span.status == SpanStatus.ERROR:
                    node.error_count += 1
                    
                # Update latency
                node.avg_latency_ms = (
                    (node.avg_latency_ms * (node.request_count - 1) + span.duration_ms) 
                    / node.request_count
                )
                
                # Find parent service
                if span.parent_span_id:
                    parent = self.collector.spans.get(span.parent_span_id)
                    if parent and parent.service_name != span.service_name:
                        node.upstream.add(parent.service_name)
                        
                        if parent.service_name in nodes:
                            nodes[parent.service_name].downstream.add(span.service_name)
                            
        return nodes


class TraceSearcher:
    """Поиск трейсов"""
    
    def __init__(self, collector: TraceCollector):
        self.collector = collector
        
    def search(self, service_name: str = None, min_duration_ms: float = None,
              has_error: bool = None, start_time: datetime = None,
              end_time: datetime = None, limit: int = 100) -> List[Trace]:
        """Поиск трейсов"""
        results = []
        
        for trace in self.collector.traces.values():
            # Filter by service
            if service_name and service_name not in trace.services:
                continue
                
            # Filter by duration
            if min_duration_ms and trace.duration_ms < min_duration_ms:
                continue
                
            # Filter by error
            if has_error is not None and trace.has_error != has_error:
                continue
                
            # Filter by time
            if start_time and trace.start_time and trace.start_time < start_time:
                continue
            if end_time and trace.end_time and trace.end_time > end_time:
                continue
                
            results.append(trace)
            
            if len(results) >= limit:
                break
                
        return results


class DistributedTracingPlatform:
    """Платформа распределённой трассировки"""
    
    def __init__(self):
        self.collector = TraceCollector()
        self.sampler = Sampler(rate=1.0)
        self.latency_analyzer = LatencyAnalyzer(self.collector)
        self.service_map_builder = ServiceMapBuilder(self.collector)
        self.searcher = TraceSearcher(self.collector)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        traces = list(self.collector.traces.values())
        spans = list(self.collector.spans.values())
        
        return {
            "total_traces": len(traces),
            "total_spans": len(spans),
            "error_traces": len([t for t in traces if t.has_error]),
            "services": len(set(s.service_name for s in spans)),
            "avg_trace_duration": sum(t.duration_ms for t in traces) / len(traces) if traces else 0,
            "avg_spans_per_trace": len(spans) / len(traces) if traces else 0
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 188: Distributed Tracing Platform")
    print("=" * 60)
    
    platform = DistributedTracingPlatform()
    print("✓ Distributed Tracing Platform created")
    
    # Simulate traces
    print("\n🔍 Simulating Distributed Traces...")
    
    services = ["api-gateway", "user-service", "order-service", "payment-service", "notification-service", "inventory-service"]
    
    # Create multiple traces
    for i in range(10):
        trace_id = platform.collector.start_trace()
        
        # Start root span (API Gateway)
        root_span = platform.collector.start_span(
            trace_id, "HTTP GET /api/orders", "api-gateway", SpanKind.SERVER
        )
        root_span.attributes["http.method"] = "GET"
        root_span.attributes["http.url"] = "/api/orders"
        
        await_time = random.uniform(0.001, 0.01)
        time.sleep(await_time)
        
        # Downstream calls
        downstream_services = random.sample(services[1:], random.randint(2, 4))
        
        child_spans = []
        for svc in downstream_services:
            child_span = platform.collector.start_span(
                trace_id, f"RPC call to {svc}", svc, SpanKind.CLIENT, root_span.span_id
            )
            child_span.attributes["rpc.service"] = svc
            child_spans.append(child_span)
            
            # Simulate some work
            time.sleep(random.uniform(0.001, 0.02))
            
            # Some calls fail
            if random.random() < 0.1:
                child_span.set_error("Connection timeout")
                child_span.add_event("error", {"message": "Timeout after 5000ms"})
                
            platform.collector.end_span(child_span.span_id)
            
        # End root span
        platform.collector.end_span(root_span.span_id)
        
    traces = list(platform.collector.traces.values())
    print(f"  Created {len(traces)} traces with {len(platform.collector.spans)} spans")
    
    # Show recent traces
    print("\n📋 Recent Traces:")
    
    print("\n  ┌──────────────────────────────────┬─────────┬──────────┬───────────┬─────────┐")
    print("  │ Trace ID                         │ Spans   │ Duration │ Services  │ Error   │")
    print("  ├──────────────────────────────────┼─────────┼──────────┼───────────┼─────────┤")
    
    for trace in traces[:5]:
        tid = trace.trace_id[:32].ljust(32)
        spans = str(trace.span_count).rjust(7)
        duration = f"{trace.duration_ms:.1f}ms".rjust(8)
        services = str(len(trace.services)).rjust(9)
        error = "Yes" if trace.has_error else "No"
        print(f"  │ {tid} │ {spans} │ {duration} │ {services} │ {error:^7} │")
        
    print("  └──────────────────────────────────┴─────────┴──────────┴───────────┴─────────┘")
    
    # Trace details
    print("\n🔎 Trace Details (first trace):")
    
    sample_trace = traces[0]
    
    print(f"\n  Trace ID: {sample_trace.trace_id}")
    print(f"  Duration: {sample_trace.duration_ms:.2f}ms")
    print(f"  Services: {', '.join(sample_trace.services)}")
    
    print("\n  Span Hierarchy:")
    
    # Build hierarchy
    root_span = next((s for s in sample_trace.spans if s.span_id == sample_trace.root_span_id), None)
    if root_span:
        print(f"    └─ {root_span.service_name}/{root_span.name} ({root_span.duration_ms:.1f}ms)")
        
        children = [s for s in sample_trace.spans if s.parent_span_id == root_span.span_id]
        for child in children:
            status_icon = "✓" if child.status != SpanStatus.ERROR else "✗"
            print(f"       └─ {status_icon} {child.service_name}/{child.name} ({child.duration_ms:.1f}ms)")
            
    # Latency analysis
    print("\n📊 Latency Analysis:")
    
    analysis = platform.latency_analyzer.analyze_trace(sample_trace.trace_id)
    
    print(f"\n  Total Duration: {analysis['total_duration_ms']:.2f}ms")
    print(f"  Span Count: {analysis['span_count']}")
    
    print("\n  Service Latencies:")
    for svc, stats in analysis['service_latencies'].items():
        print(f"    {svc}: avg={stats['avg']:.2f}ms, min={stats['min']:.2f}ms, max={stats['max']:.2f}ms")
        
    print("\n  Critical Path:")
    for step in analysis['critical_path']:
        print(f"    → {step}")
        
    # Service map
    print("\n🗺️ Service Map:")
    
    service_map = platform.service_map_builder.build_map()
    
    print("\n  ┌─────────────────────┬───────────┬──────────┬────────────┬──────────────────────────┐")
    print("  │ Service             │ Requests  │ Errors   │ Avg Lat    │ Downstream               │")
    print("  ├─────────────────────┼───────────┼──────────┼────────────┼──────────────────────────┤")
    
    for node in service_map.values():
        name = node.service_name[:19].ljust(19)
        requests = str(node.request_count).rjust(9)
        errors = str(node.error_count).rjust(8)
        latency = f"{node.avg_latency_ms:.1f}ms".rjust(10)
        downstream = ", ".join(list(node.downstream)[:2])[:24].ljust(24)
        print(f"  │ {name} │ {requests} │ {errors} │ {latency} │ {downstream} │")
        
    print("  └─────────────────────┴───────────┴──────────┴────────────┴──────────────────────────┘")
    
    # Error traces
    print("\n❌ Error Traces:")
    
    error_traces = platform.searcher.search(has_error=True)
    
    for trace in error_traces[:3]:
        print(f"\n  Trace: {trace.trace_id[:16]}...")
        error_spans = [s for s in trace.spans if s.status == SpanStatus.ERROR]
        for span in error_spans:
            print(f"    ✗ {span.service_name}/{span.name}: {span.status_message}")
            
    # Search traces
    print("\n🔍 Search Results:")
    
    # By service
    service_traces = platform.searcher.search(service_name="payment-service")
    print(f"\n  Traces involving payment-service: {len(service_traces)}")
    
    # By duration
    slow_traces = platform.searcher.search(min_duration_ms=10)
    print(f"  Traces >10ms: {len(slow_traces)}")
    
    # Sampling
    print("\n📈 Sampling Statistics:")
    
    sampler = Sampler(rate=0.1)  # 10% sampling
    sample_results = {SamplingDecision.RECORD_AND_SAMPLE: 0, SamplingDecision.DROP: 0}
    
    for _ in range(1000):
        decision = sampler.should_sample(uuid.uuid4().hex, has_error=False)
        sample_results[decision] += 1
        
    print(f"  Sample Rate: 10%")
    print(f"  Sampled: {sample_results[SamplingDecision.RECORD_AND_SAMPLE]}")
    print(f"  Dropped: {sample_results[SamplingDecision.DROP]}")
    
    # Span attributes
    print("\n📋 Span Attributes (sample):")
    
    for span in list(platform.collector.spans.values())[:3]:
        print(f"\n  {span.service_name}/{span.name}:")
        for key, value in span.attributes.items():
            print(f"    {key}: {value}")
            
    # Platform statistics
    print("\n📊 Platform Statistics:")
    
    stats = platform.get_statistics()
    
    print(f"\n  Total Traces: {stats['total_traces']}")
    print(f"  Total Spans: {stats['total_spans']}")
    print(f"  Error Traces: {stats['error_traces']}")
    print(f"  Services: {stats['services']}")
    print(f"  Avg Trace Duration: {stats['avg_trace_duration']:.2f}ms")
    print(f"  Avg Spans/Trace: {stats['avg_spans_per_trace']:.1f}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Distributed Tracing Dashboard                    │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Traces:                  {stats['total_traces']:>10}                     │")
    print(f"│ Total Spans:                   {stats['total_spans']:>10}                     │")
    print(f"│ Active Services:               {stats['services']:>10}                     │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Error Traces:                  {stats['error_traces']:>10}                     │")
    error_rate = (stats['error_traces'] / stats['total_traces'] * 100) if stats['total_traces'] > 0 else 0
    print(f"│ Error Rate:                      {error_rate:>8.1f}%                   │")
    print(f"│ Avg Duration:                   {stats['avg_trace_duration']:>9.2f}ms                  │")
    print(f"│ Avg Spans/Trace:                {stats['avg_spans_per_trace']:>9.1f}                    │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Distributed Tracing Platform initialized!")
    print("=" * 60)
