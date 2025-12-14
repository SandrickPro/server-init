#!/usr/bin/env python3
"""
Server Init - Iteration 135: Distributed Tracing Platform
Платформа Distributed Tracing

Функционал:
- Trace Collection - сбор трейсов
- Span Management - управление спанами
- Context Propagation - распространение контекста
- Trace Visualization - визуализация трейсов
- Performance Analysis - анализ производительности
- Service Dependencies - зависимости сервисов
- Sampling Strategies - стратегии сэмплирования
- Alerting on Latency - алерты по задержкам
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from collections import defaultdict
import uuid
import random


class SpanKind(Enum):
    """Тип спана"""
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"
    INTERNAL = "internal"


class SpanStatus(Enum):
    """Статус спана"""
    UNSET = "unset"
    OK = "ok"
    ERROR = "error"


class SamplingDecision(Enum):
    """Решение сэмплирования"""
    DROP = "drop"
    RECORD_ONLY = "record_only"
    RECORD_AND_SAMPLE = "record_and_sample"


@dataclass
class SpanContext:
    """Контекст спана"""
    trace_id: str
    span_id: str
    trace_flags: int = 1
    trace_state: str = ""
    is_remote: bool = False


@dataclass
class SpanEvent:
    """Событие спана"""
    name: str
    timestamp: datetime = field(default_factory=datetime.now)
    attributes: Dict = field(default_factory=dict)


@dataclass
class SpanLink:
    """Связь спана"""
    context: SpanContext = None
    attributes: Dict = field(default_factory=dict)


@dataclass
class Span:
    """Спан трейса"""
    span_id: str
    trace_id: str = ""
    
    # Hierarchy
    parent_span_id: Optional[str] = None
    
    # Info
    name: str = ""
    kind: SpanKind = SpanKind.INTERNAL
    
    # Service
    service_name: str = ""
    
    # Timing
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_ms: float = 0
    
    # Status
    status: SpanStatus = SpanStatus.UNSET
    status_message: str = ""
    
    # Attributes
    attributes: Dict = field(default_factory=dict)
    
    # Events
    events: List[SpanEvent] = field(default_factory=list)
    
    # Links
    links: List[SpanLink] = field(default_factory=list)


@dataclass
class Trace:
    """Трейс"""
    trace_id: str
    root_span_id: str = ""
    
    # Spans
    spans: List[Span] = field(default_factory=list)
    span_count: int = 0
    
    # Timing
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_ms: float = 0
    
    # Services
    services: List[str] = field(default_factory=list)
    
    # Status
    has_error: bool = False


@dataclass
class ServiceDependency:
    """Зависимость сервиса"""
    source: str = ""
    target: str = ""
    
    # Stats
    call_count: int = 0
    error_count: int = 0
    avg_latency_ms: float = 0
    
    # Operations
    operations: List[str] = field(default_factory=list)


@dataclass
class SamplingRule:
    """Правило сэмплирования"""
    rule_id: str
    name: str = ""
    
    # Conditions
    service_name: Optional[str] = None
    operation_name: Optional[str] = None
    min_duration_ms: Optional[float] = None
    
    # Sampling
    sampling_rate: float = 1.0  # 0.0 - 1.0
    
    # Priority
    priority: int = 0


@dataclass
class LatencyAlert:
    """Алерт по задержке"""
    alert_id: str
    service: str = ""
    operation: str = ""
    
    # Thresholds
    p50_threshold_ms: float = 100
    p95_threshold_ms: float = 500
    p99_threshold_ms: float = 1000
    
    # Current
    current_p50: float = 0
    current_p95: float = 0
    current_p99: float = 0
    
    # Status
    triggered: bool = False


class TraceCollector:
    """Коллектор трейсов"""
    
    def __init__(self):
        self.traces: Dict[str, Trace] = {}
        self.spans: Dict[str, Span] = {}
        
    def start_trace(self, name: str, service_name: str) -> Tuple[Trace, Span]:
        """Начало трейса"""
        trace_id = uuid.uuid4().hex[:32]
        span_id = uuid.uuid4().hex[:16]
        
        span = Span(
            span_id=span_id,
            trace_id=trace_id,
            name=name,
            service_name=service_name,
            kind=SpanKind.SERVER
        )
        
        trace = Trace(
            trace_id=trace_id,
            root_span_id=span_id,
            services=[service_name]
        )
        trace.spans.append(span)
        trace.span_count = 1
        
        self.traces[trace_id] = trace
        self.spans[span_id] = span
        
        return trace, span
        
    def start_span(self, trace_id: str, parent_span_id: str, name: str,
                    service_name: str, kind: SpanKind = SpanKind.CLIENT) -> Span:
        """Начало спана"""
        span = Span(
            span_id=uuid.uuid4().hex[:16],
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            name=name,
            service_name=service_name,
            kind=kind
        )
        
        self.spans[span.span_id] = span
        
        trace = self.traces.get(trace_id)
        if trace:
            trace.spans.append(span)
            trace.span_count += 1
            if service_name not in trace.services:
                trace.services.append(service_name)
                
        return span
        
    def end_span(self, span_id: str, status: SpanStatus = SpanStatus.OK,
                  attributes: Dict = None) -> Span:
        """Завершение спана"""
        span = self.spans.get(span_id)
        if not span:
            return None
            
        span.end_time = datetime.now()
        span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
        span.status = status
        
        if attributes:
            span.attributes.update(attributes)
            
        return span
        
    def end_trace(self, trace_id: str) -> Trace:
        """Завершение трейса"""
        trace = self.traces.get(trace_id)
        if not trace:
            return None
            
        trace.end_time = datetime.now()
        trace.duration_ms = (trace.end_time - trace.start_time).total_seconds() * 1000
        trace.has_error = any(s.status == SpanStatus.ERROR for s in trace.spans)
        
        return trace
        
    def add_event(self, span_id: str, name: str, attributes: Dict = None) -> SpanEvent:
        """Добавление события"""
        span = self.spans.get(span_id)
        if not span:
            return None
            
        event = SpanEvent(
            name=name,
            attributes=attributes or {}
        )
        span.events.append(event)
        return event


from typing import Tuple


class TraceSampler:
    """Сэмплер трейсов"""
    
    def __init__(self):
        self.rules: List[SamplingRule] = []
        self.default_rate: float = 1.0
        
    def add_rule(self, name: str, sampling_rate: float,
                  service_name: str = None, operation_name: str = None,
                  min_duration_ms: float = None, priority: int = 0) -> SamplingRule:
        """Добавление правила"""
        rule = SamplingRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name=name,
            service_name=service_name,
            operation_name=operation_name,
            min_duration_ms=min_duration_ms,
            sampling_rate=sampling_rate,
            priority=priority
        )
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
        return rule
        
    def should_sample(self, service_name: str, operation_name: str,
                       duration_ms: float = None) -> SamplingDecision:
        """Решение о сэмплировании"""
        for rule in self.rules:
            if rule.service_name and rule.service_name != service_name:
                continue
            if rule.operation_name and rule.operation_name != operation_name:
                continue
            if rule.min_duration_ms and duration_ms and duration_ms < rule.min_duration_ms:
                continue
                
            if random.random() <= rule.sampling_rate:
                return SamplingDecision.RECORD_AND_SAMPLE
            else:
                return SamplingDecision.DROP
                
        # Default
        if random.random() <= self.default_rate:
            return SamplingDecision.RECORD_AND_SAMPLE
        return SamplingDecision.DROP


class DependencyAnalyzer:
    """Анализатор зависимостей"""
    
    def __init__(self, collector: TraceCollector):
        self.collector = collector
        self.dependencies: Dict[str, ServiceDependency] = {}
        
    def analyze(self, trace_id: str) -> List[ServiceDependency]:
        """Анализ зависимостей трейса"""
        trace = self.collector.traces.get(trace_id)
        if not trace:
            return []
            
        deps = []
        
        for span in trace.spans:
            if span.parent_span_id:
                parent = self.collector.spans.get(span.parent_span_id)
                if parent and parent.service_name != span.service_name:
                    key = f"{parent.service_name}->{span.service_name}"
                    
                    if key not in self.dependencies:
                        self.dependencies[key] = ServiceDependency(
                            source=parent.service_name,
                            target=span.service_name
                        )
                        
                    dep = self.dependencies[key]
                    dep.call_count += 1
                    
                    if span.status == SpanStatus.ERROR:
                        dep.error_count += 1
                        
                    if span.name not in dep.operations:
                        dep.operations.append(span.name)
                        
                    # Update average latency
                    dep.avg_latency_ms = (dep.avg_latency_ms * (dep.call_count - 1) + span.duration_ms) / dep.call_count
                    
                    deps.append(dep)
                    
        return deps
        
    def get_service_map(self) -> List[Dict]:
        """Карта сервисов"""
        return [
            {
                "source": dep.source,
                "target": dep.target,
                "calls": dep.call_count,
                "errors": dep.error_count,
                "avg_latency_ms": round(dep.avg_latency_ms, 2)
            }
            for dep in self.dependencies.values()
        ]


class LatencyAnalyzer:
    """Анализатор задержек"""
    
    def __init__(self, collector: TraceCollector):
        self.collector = collector
        self.latencies: Dict[str, List[float]] = defaultdict(list)
        self.alerts: Dict[str, LatencyAlert] = {}
        
    def record_latency(self, service: str, operation: str, latency_ms: float):
        """Запись задержки"""
        key = f"{service}:{operation}"
        self.latencies[key].append(latency_ms)
        
        # Keep last 1000
        if len(self.latencies[key]) > 1000:
            self.latencies[key] = self.latencies[key][-1000:]
            
    def get_percentiles(self, service: str, operation: str) -> Dict[str, float]:
        """Получение перцентилей"""
        key = f"{service}:{operation}"
        latencies = sorted(self.latencies.get(key, []))
        
        if not latencies:
            return {"p50": 0, "p95": 0, "p99": 0}
            
        n = len(latencies)
        return {
            "p50": latencies[int(n * 0.50)],
            "p95": latencies[int(n * 0.95)] if n >= 20 else latencies[-1],
            "p99": latencies[int(n * 0.99)] if n >= 100 else latencies[-1]
        }
        
    def add_alert(self, service: str, operation: str,
                   p50_threshold: float, p95_threshold: float,
                   p99_threshold: float) -> LatencyAlert:
        """Добавление алерта"""
        alert = LatencyAlert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            service=service,
            operation=operation,
            p50_threshold_ms=p50_threshold,
            p95_threshold_ms=p95_threshold,
            p99_threshold_ms=p99_threshold
        )
        self.alerts[alert.alert_id] = alert
        return alert
        
    def check_alerts(self) -> List[Dict]:
        """Проверка алертов"""
        triggered = []
        
        for alert in self.alerts.values():
            percentiles = self.get_percentiles(alert.service, alert.operation)
            
            alert.current_p50 = percentiles["p50"]
            alert.current_p95 = percentiles["p95"]
            alert.current_p99 = percentiles["p99"]
            
            if (alert.current_p50 > alert.p50_threshold_ms or
                alert.current_p95 > alert.p95_threshold_ms or
                alert.current_p99 > alert.p99_threshold_ms):
                alert.triggered = True
                triggered.append({
                    "service": alert.service,
                    "operation": alert.operation,
                    "p50": f"{alert.current_p50:.1f}ms (threshold: {alert.p50_threshold_ms}ms)",
                    "p95": f"{alert.current_p95:.1f}ms (threshold: {alert.p95_threshold_ms}ms)",
                    "p99": f"{alert.current_p99:.1f}ms (threshold: {alert.p99_threshold_ms}ms)"
                })
            else:
                alert.triggered = False
                
        return triggered


class TraceVisualizer:
    """Визуализатор трейсов"""
    
    def __init__(self, collector: TraceCollector):
        self.collector = collector
        
    def visualize_trace(self, trace_id: str) -> str:
        """Визуализация трейса"""
        trace = self.collector.traces.get(trace_id)
        if not trace:
            return "Trace not found"
            
        lines = [
            f"Trace: {trace_id}",
            f"Duration: {trace.duration_ms:.2f}ms",
            f"Services: {', '.join(trace.services)}",
            f"Spans: {trace.span_count}",
            f"Has Error: {trace.has_error}",
            "",
            "Timeline:"
        ]
        
        # Build span tree
        def build_tree(parent_id: str = None, depth: int = 0) -> List[str]:
            result = []
            for span in trace.spans:
                if span.parent_span_id == parent_id:
                    indent = "  " * depth
                    status_icon = "✓" if span.status == SpanStatus.OK else "✗" if span.status == SpanStatus.ERROR else "○"
                    result.append(f"{indent}{status_icon} [{span.service_name}] {span.name} ({span.duration_ms:.2f}ms)")
                    result.extend(build_tree(span.span_id, depth + 1))
            return result
            
        lines.extend(build_tree())
        
        return "\n".join(lines)


class DistributedTracingPlatform:
    """Платформа распределённого трейсинга"""
    
    def __init__(self):
        self.collector = TraceCollector()
        self.sampler = TraceSampler()
        self.dependency_analyzer = DependencyAnalyzer(self.collector)
        self.latency_analyzer = LatencyAnalyzer(self.collector)
        self.visualizer = TraceVisualizer(self.collector)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        traces = list(self.collector.traces.values())
        spans = list(self.collector.spans.values())
        
        return {
            "traces": len(traces),
            "spans": len(spans),
            "error_traces": len([t for t in traces if t.has_error]),
            "services": len(set(s.service_name for s in spans)),
            "sampling_rules": len(self.sampler.rules),
            "dependencies": len(self.dependency_analyzer.dependencies),
            "alerts": len(self.latency_analyzer.alerts),
            "triggered_alerts": len([a for a in self.latency_analyzer.alerts.values() if a.triggered])
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 135: Distributed Tracing Platform")
    print("=" * 60)
    
    async def demo():
        platform = DistributedTracingPlatform()
        print("✓ Distributed Tracing Platform created")
        
        # Add sampling rules
        print("\n📋 Adding Sampling Rules...")
        
        rules = [
            ("sample-all-errors", 1.0, None, None, None, 100),
            ("sample-slow-requests", 1.0, None, None, 500, 90),
            ("sample-api-gateway", 0.5, "api-gateway", None, None, 50),
            ("default-sample", 0.1, None, None, None, 0)
        ]
        
        for name, rate, svc, op, min_dur, priority in rules:
            rule = platform.sampler.add_rule(name, rate, svc, op, min_dur, priority)
            print(f"  ✓ {name}: {rate * 100}% sampling")
            
        # Simulate traces
        print("\n🔍 Simulating Distributed Traces...")
        
        services = ["api-gateway", "user-service", "order-service", "payment-service", "inventory-service"]
        
        created_traces = []
        
        for i in range(10):
            # Start trace
            trace, root_span = platform.collector.start_trace(
                f"HTTP GET /api/orders/{i}",
                "api-gateway"
            )
            created_traces.append(trace)
            
            # Simulate child spans
            spans_created = [root_span]
            
            for j, service in enumerate(services[1:], 1):
                if random.random() > 0.3:  # 70% chance
                    parent = random.choice(spans_created)
                    span = platform.collector.start_span(
                        trace.trace_id,
                        parent.span_id,
                        f"Call {service}",
                        service,
                        SpanKind.CLIENT if j % 2 == 0 else SpanKind.SERVER
                    )
                    spans_created.append(span)
                    
                    # Simulate delay
                    await asyncio.sleep(random.uniform(0.01, 0.05))
                    
                    # End span
                    status = SpanStatus.ERROR if random.random() > 0.9 else SpanStatus.OK
                    platform.collector.end_span(
                        span.span_id,
                        status,
                        {"db.query": "SELECT * FROM...", "http.status_code": 200}
                    )
                    
            # End root span
            platform.collector.end_span(root_span.span_id, SpanStatus.OK)
            
            # End trace
            platform.collector.end_trace(trace.trace_id)
            
            print(f"  ✓ Trace {i + 1}: {trace.span_count} spans, {trace.duration_ms:.2f}ms")
            
        # Analyze dependencies
        print("\n🔗 Analyzing Service Dependencies...")
        
        for trace in created_traces:
            platform.dependency_analyzer.analyze(trace.trace_id)
            
        service_map = platform.dependency_analyzer.get_service_map()
        
        print("\n  Service Map:")
        for dep in service_map:
            error_rate = (dep["errors"] / dep["calls"] * 100) if dep["calls"] > 0 else 0
            print(f"  {dep['source']} -> {dep['target']}")
            print(f"     Calls: {dep['calls']} | Errors: {dep['errors']} ({error_rate:.1f}%)")
            print(f"     Avg Latency: {dep['avg_latency_ms']}ms")
            
        # Record latencies
        print("\n⏱️ Recording Latencies...")
        
        for trace in created_traces:
            for span in trace.spans:
                platform.latency_analyzer.record_latency(
                    span.service_name,
                    span.name,
                    span.duration_ms
                )
                
        # Get percentiles
        print("\n📊 Latency Percentiles:")
        
        for service in services:
            spans = [s for s in platform.collector.spans.values() if s.service_name == service]
            if spans:
                sample_span = spans[0]
                percentiles = platform.latency_analyzer.get_percentiles(
                    service, sample_span.name
                )
                print(f"  {service}:")
                print(f"     p50: {percentiles['p50']:.2f}ms")
                print(f"     p95: {percentiles['p95']:.2f}ms")
                print(f"     p99: {percentiles['p99']:.2f}ms")
                
        # Add alerts
        print("\n🚨 Adding Latency Alerts...")
        
        for service in services[:3]:
            alert = platform.latency_analyzer.add_alert(
                service,
                f"Call {service}",
                p50_threshold=50,
                p95_threshold=200,
                p99_threshold=500
            )
            print(f"  ✓ Alert for {service}")
            
        # Check alerts
        triggered = platform.latency_analyzer.check_alerts()
        
        print(f"\n  Triggered Alerts: {len(triggered)}")
        for alert in triggered:
            print(f"  🔴 {alert['service']} - {alert['operation']}")
            print(f"     p50: {alert['p50']}")
            print(f"     p95: {alert['p95']}")
            print(f"     p99: {alert['p99']}")
            
        # Visualize trace
        print("\n📈 Trace Visualization:")
        
        if created_traces:
            visualization = platform.visualizer.visualize_trace(created_traces[0].trace_id)
            print("\n" + visualization)
            
        # Sampling decisions
        print("\n🎲 Sampling Decisions:")
        
        test_cases = [
            ("api-gateway", "HTTP GET /api/users", None),
            ("user-service", "GetUser", 100),
            ("order-service", "CreateOrder", 600),
            ("payment-service", "ProcessPayment", 50)
        ]
        
        for service, operation, duration in test_cases:
            decision = platform.sampler.should_sample(service, operation, duration)
            icon = "✓" if decision == SamplingDecision.RECORD_AND_SAMPLE else "✗"
            print(f"  {icon} {service}/{operation}: {decision.value}")
            
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Traces: {stats['traces']}")
        print(f"  Spans: {stats['spans']}")
        print(f"  Error Traces: {stats['error_traces']}")
        print(f"  Services: {stats['services']}")
        print(f"  Sampling Rules: {stats['sampling_rules']}")
        print(f"  Dependencies: {stats['dependencies']}")
        print(f"  Alerts: {stats['alerts']}")
        print(f"  Triggered Alerts: {stats['triggered_alerts']}")
        
        # Dashboard
        print("\n📋 Distributed Tracing Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │             Distributed Tracing Overview                    │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Traces:       {stats['traces']:>10}                        │")
        print(f"  │ Total Spans:        {stats['spans']:>10}                        │")
        print(f"  │ Error Traces:       {stats['error_traces']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Services:           {stats['services']:>10}                        │")
        print(f"  │ Dependencies:       {stats['dependencies']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Sampling Rules:     {stats['sampling_rules']:>10}                        │")
        print(f"  │ Latency Alerts:     {stats['alerts']:>10}                        │")
        print(f"  │ Triggered:          {stats['triggered_alerts']:>10}                        │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Distributed Tracing Platform initialized!")
    print("=" * 60)
