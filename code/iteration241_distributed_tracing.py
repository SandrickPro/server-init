#!/usr/bin/env python3
"""
Server Init - Iteration 241: Distributed Tracing Platform
Платформа распределённой трассировки

Функционал:
- Trace Collection - сбор трейсов
- Span Management - управление спанами
- Context Propagation - распространение контекста
- Service Map - карта сервисов
- Latency Analysis - анализ латентности
- Error Tracking - отслеживание ошибок
- Trace Sampling - сэмплирование трейсов
- Trace Search - поиск трейсов
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
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
    OK = "ok"
    ERROR = "error"
    UNSET = "unset"


class SamplingDecision(Enum):
    """Решение сэмплирования"""
    SAMPLED = "sampled"
    NOT_SAMPLED = "not_sampled"
    DEFERRED = "deferred"


@dataclass
class SpanContext:
    """Контекст спана"""
    trace_id: str = ""
    span_id: str = ""
    parent_span_id: str = ""
    
    # Flags
    sampled: bool = True
    
    # Baggage
    baggage: Dict[str, str] = field(default_factory=dict)


@dataclass
class SpanEvent:
    """Событие в спане"""
    event_id: str
    name: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SpanLink:
    """Связь между спанами"""
    link_id: str
    trace_id: str = ""
    span_id: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Span:
    """Спан"""
    span_id: str
    trace_id: str = ""
    parent_span_id: str = ""
    
    # Info
    name: str = ""
    service: str = ""
    operation: str = ""
    
    # Kind
    kind: SpanKind = SpanKind.INTERNAL
    
    # Status
    status: SpanStatus = SpanStatus.UNSET
    status_message: str = ""
    
    # Time
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_ms: float = 0
    
    # Attributes
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    # Events
    events: List[SpanEvent] = field(default_factory=list)
    
    # Links
    links: List[SpanLink] = field(default_factory=list)
    
    # Resource
    resource_attributes: Dict[str, str] = field(default_factory=dict)


@dataclass
class Trace:
    """Трейс"""
    trace_id: str
    
    # Root span
    root_span_id: str = ""
    
    # All spans
    spans: List[Span] = field(default_factory=list)
    
    # Services involved
    services: Set[str] = field(default_factory=set)
    
    # Timing
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_duration_ms: float = 0
    
    # Status
    has_errors: bool = False
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class ServiceNode:
    """Узел в карте сервисов"""
    service: str
    
    # Connections
    calls_to: Dict[str, int] = field(default_factory=dict)  # service -> call count
    called_by: Dict[str, int] = field(default_factory=dict)
    
    # Stats
    total_requests: int = 0
    error_count: int = 0
    avg_latency_ms: float = 0
    
    # Operations
    operations: Set[str] = field(default_factory=set)


@dataclass
class SamplingRule:
    """Правило сэмплирования"""
    rule_id: str
    name: str = ""
    
    # Match
    service_pattern: str = "*"
    operation_pattern: str = "*"
    
    # Rate (0.0 - 1.0)
    sampling_rate: float = 1.0
    
    # Priority (higher = more important)
    priority: int = 0
    
    # Active
    is_active: bool = True


class DistributedTracingPlatform:
    """Платформа распределённой трассировки"""
    
    def __init__(self):
        self.traces: Dict[str, Trace] = {}
        self.spans: Dict[str, Span] = {}
        self.service_map: Dict[str, ServiceNode] = {}
        self.sampling_rules: Dict[str, SamplingRule] = {}
        
        self._init_default_rules()
        
    def _init_default_rules(self):
        """Инициализация правил сэмплирования по умолчанию"""
        default_rule = SamplingRule(
            rule_id="rule_default",
            name="Default",
            sampling_rate=0.1
        )
        
        error_rule = SamplingRule(
            rule_id="rule_errors",
            name="Always sample errors",
            service_pattern="*",
            operation_pattern="*",
            sampling_rate=1.0,
            priority=100
        )
        
        self.sampling_rules = {
            default_rule.rule_id: default_rule,
            error_rule.rule_id: error_rule
        }
        
    def start_trace(self, service: str, operation: str,
                   tags: Dict[str, str] = None) -> Trace:
        """Начало трейса"""
        trace_id = uuid.uuid4().hex[:32]
        
        trace = Trace(
            trace_id=trace_id,
            tags=tags or {}
        )
        
        # Create root span
        root_span = self.start_span(
            trace_id=trace_id,
            name=operation,
            service=service,
            operation=operation,
            kind=SpanKind.SERVER
        )
        
        trace.root_span_id = root_span.span_id
        trace.start_time = root_span.start_time
        trace.spans.append(root_span)
        trace.services.add(service)
        
        self.traces[trace_id] = trace
        
        return trace
        
    def start_span(self, trace_id: str, name: str,
                  service: str, operation: str,
                  parent_span_id: str = "",
                  kind: SpanKind = SpanKind.INTERNAL,
                  attributes: Dict[str, Any] = None) -> Span:
        """Начало спана"""
        span = Span(
            span_id=uuid.uuid4().hex[:16],
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            name=name,
            service=service,
            operation=operation,
            kind=kind,
            attributes=attributes or {},
            resource_attributes={"service.name": service}
        )
        
        self.spans[span.span_id] = span
        
        # Update service map
        self._update_service_map(span, parent_span_id)
        
        return span
        
    def end_span(self, span_id: str, status: SpanStatus = SpanStatus.OK,
                status_message: str = "") -> Optional[Span]:
        """Завершение спана"""
        span = self.spans.get(span_id)
        if not span:
            return None
            
        span.end_time = datetime.now()
        span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
        span.status = status
        span.status_message = status_message
        
        # Update trace
        trace = self.traces.get(span.trace_id)
        if trace:
            if span not in trace.spans:
                trace.spans.append(span)
            trace.services.add(span.service)
            
            if status == SpanStatus.ERROR:
                trace.has_errors = True
                
            # Update trace end time
            if trace.end_time is None or span.end_time > trace.end_time:
                trace.end_time = span.end_time
                trace.total_duration_ms = (trace.end_time - trace.start_time).total_seconds() * 1000
                
        return span
        
    def add_span_event(self, span_id: str, name: str,
                      attributes: Dict[str, Any] = None) -> Optional[SpanEvent]:
        """Добавление события в спан"""
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
        
    def _update_service_map(self, span: Span, parent_span_id: str):
        """Обновление карты сервисов"""
        service = span.service
        
        if service not in self.service_map:
            self.service_map[service] = ServiceNode(service=service)
            
        node = self.service_map[service]
        node.total_requests += 1
        node.operations.add(span.operation)
        
        # Update connections
        if parent_span_id:
            parent_span = self.spans.get(parent_span_id)
            if parent_span and parent_span.service != service:
                parent_service = parent_span.service
                
                # Parent calls this service
                if parent_service not in self.service_map:
                    self.service_map[parent_service] = ServiceNode(service=parent_service)
                    
                parent_node = self.service_map[parent_service]
                parent_node.calls_to[service] = parent_node.calls_to.get(service, 0) + 1
                
                node.called_by[parent_service] = node.called_by.get(parent_service, 0) + 1
                
    def search_traces(self, service: str = None,
                     operation: str = None,
                     has_errors: bool = None,
                     min_duration_ms: float = None,
                     max_duration_ms: float = None,
                     limit: int = 100) -> List[Trace]:
        """Поиск трейсов"""
        results = []
        
        for trace in self.traces.values():
            # Filter by service
            if service and service not in trace.services:
                continue
                
            # Filter by operation
            if operation:
                has_op = any(s.operation == operation for s in trace.spans)
                if not has_op:
                    continue
                    
            # Filter by errors
            if has_errors is not None and trace.has_errors != has_errors:
                continue
                
            # Filter by duration
            if min_duration_ms and trace.total_duration_ms < min_duration_ms:
                continue
                
            if max_duration_ms and trace.total_duration_ms > max_duration_ms:
                continue
                
            results.append(trace)
            
            if len(results) >= limit:
                break
                
        return results
        
    def get_trace_details(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Детали трейса"""
        trace = self.traces.get(trace_id)
        if not trace:
            return None
            
        return {
            "trace_id": trace.trace_id,
            "services": list(trace.services),
            "span_count": len(trace.spans),
            "duration_ms": trace.total_duration_ms,
            "has_errors": trace.has_errors,
            "spans": [
                {
                    "span_id": s.span_id,
                    "name": s.name,
                    "service": s.service,
                    "duration_ms": s.duration_ms,
                    "status": s.status.value
                }
                for s in trace.spans
            ]
        }
        
    def create_sampling_rule(self, name: str, service_pattern: str = "*",
                            operation_pattern: str = "*",
                            sampling_rate: float = 1.0,
                            priority: int = 0) -> SamplingRule:
        """Создание правила сэмплирования"""
        rule = SamplingRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name=name,
            service_pattern=service_pattern,
            operation_pattern=operation_pattern,
            sampling_rate=sampling_rate,
            priority=priority
        )
        
        self.sampling_rules[rule.rule_id] = rule
        return rule
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        traces = list(self.traces.values())
        spans = list(self.spans.values())
        
        error_traces = [t for t in traces if t.has_errors]
        
        # Average duration
        if traces:
            avg_duration = sum(t.total_duration_ms for t in traces) / len(traces)
        else:
            avg_duration = 0
            
        # Spans by service
        by_service = {}
        for span in spans:
            s = span.service
            by_service[s] = by_service.get(s, 0) + 1
            
        return {
            "total_traces": len(traces),
            "total_spans": len(spans),
            "error_traces": len(error_traces),
            "error_rate": (len(error_traces) / len(traces) * 100) if traces else 0,
            "avg_duration_ms": avg_duration,
            "services": len(self.service_map),
            "sampling_rules": len(self.sampling_rules),
            "spans_by_service": by_service
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 241: Distributed Tracing Platform")
    print("=" * 60)
    
    platform = DistributedTracingPlatform()
    print("✓ Distributed Tracing Platform created")
    
    # Simulate traces
    print("\n📊 Creating Traces...")
    
    services = ["api-gateway", "user-service", "order-service", "payment-service", "inventory-service"]
    operations = ["GET /users", "POST /orders", "GET /products", "POST /payments", "GET /inventory"]
    
    traces = []
    
    for i in range(20):
        # Start trace
        service = random.choice(services)
        operation = random.choice(operations)
        
        trace = platform.start_trace(
            service=service,
            operation=operation,
            tags={"environment": "production", "version": "2.1.0"}
        )
        traces.append(trace)
        
        # Add child spans (simulate service calls)
        root_span = platform.spans.get(trace.root_span_id)
        
        num_children = random.randint(2, 5)
        parent_id = root_span.span_id
        
        for j in range(num_children):
            child_service = random.choice([s for s in services if s != service])
            child_op = random.choice(operations)
            
            child_span = platform.start_span(
                trace_id=trace.trace_id,
                name=child_op,
                service=child_service,
                operation=child_op,
                parent_span_id=parent_id,
                kind=random.choice([SpanKind.CLIENT, SpanKind.SERVER]),
                attributes={
                    "http.method": "GET" if "GET" in child_op else "POST",
                    "http.url": f"http://{child_service}/{child_op.split()[1]}"
                }
            )
            
            # Add events
            if random.random() > 0.7:
                platform.add_span_event(
                    child_span.span_id,
                    "cache.miss",
                    {"cache.key": f"key_{random.randint(1, 100)}"}
                )
                
            # End child span
            status = SpanStatus.ERROR if random.random() > 0.9 else SpanStatus.OK
            platform.end_span(child_span.span_id, status)
            
            parent_id = child_span.span_id
            
        # End root span
        root_status = SpanStatus.ERROR if random.random() > 0.85 else SpanStatus.OK
        platform.end_span(root_span.span_id, root_status)
        
    print(f"  ✓ Created {len(traces)} traces")
    
    # Create sampling rules
    print("\n📋 Creating Sampling Rules...")
    
    rules = [
        platform.create_sampling_rule("API Gateway Full", "api-gateway", "*", 1.0, 10),
        platform.create_sampling_rule("Payment Service Full", "payment-service", "*", 1.0, 10),
        platform.create_sampling_rule("Slow Requests", "*", "*", 0.5, 5),
    ]
    
    for rule in rules:
        print(f"  📋 {rule.name}: {rule.sampling_rate * 100:.0f}% sampling")
        
    # Search traces
    print("\n🔍 Searching Traces...")
    
    # Find error traces
    error_traces = platform.search_traces(has_errors=True, limit=5)
    print(f"  ❌ Found {len(error_traces)} traces with errors")
    
    # Find by service
    api_traces = platform.search_traces(service="api-gateway", limit=5)
    print(f"  🌐 Found {len(api_traces)} API Gateway traces")
    
    # Find slow traces
    slow_traces = platform.search_traces(min_duration_ms=100, limit=5)
    print(f"  🐢 Found {len(slow_traces)} slow traces (>100ms)")
    
    # Display traces
    print("\n📊 Recent Traces:")
    
    print("\n  ┌────────────────────────────────┬──────────────┬──────────┬─────────┬─────────┐")
    print("  │ Trace ID                       │ Root Service │ Spans    │ Duration│ Status  │")
    print("  ├────────────────────────────────┼──────────────┼──────────┼─────────┼─────────┤")
    
    for trace in list(platform.traces.values())[:10]:
        trace_id = trace.trace_id[:30].ljust(30)
        
        root_span = platform.spans.get(trace.root_span_id)
        service = (root_span.service if root_span else "unknown")[:12].ljust(12)
        
        spans = str(len(trace.spans))[:8].ljust(8)
        duration = f"{trace.total_duration_ms:.0f}ms"[:7].ljust(7)
        status = "🔴" if trace.has_errors else "🟢"
        
        print(f"  │ {trace_id} │ {service} │ {spans} │ {duration} │ {status:7s} │")
        
    print("  └────────────────────────────────┴──────────────┴──────────┴─────────┴─────────┘")
    
    # Display service map
    print("\n🗺️ Service Map:")
    
    for service, node in platform.service_map.items():
        print(f"\n  📦 {service}")
        print(f"     Requests: {node.total_requests}")
        print(f"     Operations: {', '.join(list(node.operations)[:3])}")
        
        if node.calls_to:
            print(f"     Calls to: {', '.join(node.calls_to.keys())}")
        if node.called_by:
            print(f"     Called by: {', '.join(node.called_by.keys())}")
            
    # Trace details
    print("\n🔍 Trace Details:")
    
    sample_trace = traces[0]
    details = platform.get_trace_details(sample_trace.trace_id)
    
    if details:
        print(f"\n  Trace ID: {details['trace_id'][:16]}...")
        print(f"  Services: {', '.join(details['services'])}")
        print(f"  Span Count: {details['span_count']}")
        print(f"  Duration: {details['duration_ms']:.0f}ms")
        print(f"  Has Errors: {details['has_errors']}")
        
        print("\n  Spans:")
        for span in details['spans'][:5]:
            status_icon = "🔴" if span['status'] == 'error' else "🟢"
            print(f"    {status_icon} {span['name']} ({span['service']}) - {span['duration_ms']:.0f}ms")
            
    # Span timeline (waterfall)
    print("\n📈 Span Timeline (Waterfall):")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────┐")
    
    trace_spans = sample_trace.spans[:6]
    if trace_spans:
        min_start = min(s.start_time for s in trace_spans)
        max_end = max((s.end_time or s.start_time) for s in trace_spans)
        total_time = (max_end - min_start).total_seconds() * 1000
        
        for span in trace_spans:
            offset = ((span.start_time - min_start).total_seconds() * 1000 / total_time) if total_time > 0 else 0
            width = (span.duration_ms / total_time) if total_time > 0 else 0
            
            padding = int(offset * 40)
            bar_len = max(1, int(width * 40))
            
            name = span.name[:15].ljust(15)
            bar = " " * padding + "█" * bar_len
            
            status_icon = "🔴" if span.status == SpanStatus.ERROR else "🟢"
            
            print(f"  │ {status_icon} {name} {bar}")
            
    print("  └─────────────────────────────────────────────────────────────────┘")
    
    # Latency distribution
    print("\n⏱️ Latency Distribution:")
    
    latencies = [t.total_duration_ms for t in traces]
    if latencies:
        p50 = sorted(latencies)[len(latencies) // 2]
        p95 = sorted(latencies)[int(len(latencies) * 0.95)]
        p99 = sorted(latencies)[int(len(latencies) * 0.99)]
        
        print(f"  P50: {p50:.0f}ms")
        print(f"  P95: {p95:.0f}ms")
        print(f"  P99: {p99:.0f}ms")
        
    # Service call graph
    print("\n📊 Service Call Graph:")
    
    for service, node in platform.service_map.items():
        if node.calls_to:
            for target, count in node.calls_to.items():
                print(f"  {service} ──({count})──> {target}")
                
    # Statistics
    print("\n📊 Platform Statistics:")
    
    stats = platform.get_statistics()
    
    print(f"\n  Total Traces: {stats['total_traces']}")
    print(f"  Total Spans: {stats['total_spans']}")
    print(f"  Error Traces: {stats['error_traces']}")
    print(f"  Error Rate: {stats['error_rate']:.1f}%")
    print(f"  Avg Duration: {stats['avg_duration_ms']:.0f}ms")
    print(f"  Services: {stats['services']}")
    
    # Spans by service
    print("\n  Spans by Service:")
    for service, count in stats['spans_by_service'].items():
        bar = "█" * min(count, 10) + "░" * (10 - min(count, 10))
        print(f"    {service:20s} [{bar}] {count}")
        
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                  Distributed Tracing Dashboard                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Traces:                  {stats['total_traces']:>12}                        │")
    print(f"│ Total Spans:                   {stats['total_spans']:>12}                        │")
    print(f"│ Services Tracked:              {stats['services']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Error Rate:                       {stats['error_rate']:>7.1f}%                       │")
    print(f"│ Avg Duration (ms):               {stats['avg_duration_ms']:>8.0f}                       │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Distributed Tracing Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
