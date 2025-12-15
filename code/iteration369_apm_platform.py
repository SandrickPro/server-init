#!/usr/bin/env python3
"""
Server Init - Iteration 369: APM Platform (Application Performance Monitoring)
Платформа мониторинга производительности приложений

Функционал:
- Transaction Tracing - трассировка транзакций
- Service Mapping - карта сервисов
- Error Tracking - отслеживание ошибок
- Performance Metrics - метрики производительности
- User Experience Monitoring - мониторинг UX
- Code-Level Diagnostics - диагностика на уровне кода
- Anomaly Detection - обнаружение аномалий
- SLA Monitoring - мониторинг SLA
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
import uuid


class ServiceType(Enum):
    """Тип сервиса"""
    WEB = "web"
    API = "api"
    MICROSERVICE = "microservice"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    EXTERNAL = "external"
    GATEWAY = "gateway"


class ServiceStatus(Enum):
    """Статус сервиса"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class TransactionStatus(Enum):
    """Статус транзакции"""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class ErrorSeverity(Enum):
    """Серьезность ошибки"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AnomalyType(Enum):
    """Тип аномалии"""
    LATENCY_SPIKE = "latency_spike"
    ERROR_RATE_SPIKE = "error_rate_spike"
    THROUGHPUT_DROP = "throughput_drop"
    MEMORY_LEAK = "memory_leak"
    CPU_SPIKE = "cpu_spike"
    APDEX_DROP = "apdex_drop"


class MetricType(Enum):
    """Тип метрики"""
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    APDEX = "apdex"
    CPU = "cpu"
    MEMORY = "memory"
    HEAP = "heap"
    GC = "gc"


@dataclass
class Span:
    """Span в распределенной трассировке"""
    span_id: str
    trace_id: str
    
    # Parent
    parent_span_id: str = ""
    
    # Identity
    name: str = ""
    service_name: str = ""
    
    # Operation
    operation_name: str = ""
    operation_kind: str = ""  # server, client, producer, consumer
    
    # Timing
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_ms: float = 0.0
    
    # Status
    status: TransactionStatus = TransactionStatus.SUCCESS
    error_message: str = ""
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Events
    events: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Trace:
    """Распределенная трассировка"""
    trace_id: str
    
    # Root span
    root_span_id: str = ""
    
    # Service
    entry_service: str = ""
    
    # Request
    http_method: str = ""
    http_url: str = ""
    http_status: int = 0
    
    # User
    user_id: str = ""
    session_id: str = ""
    
    # Timing
    start_time: datetime = field(default_factory=datetime.now)
    duration_ms: float = 0.0
    
    # Status
    status: TransactionStatus = TransactionStatus.SUCCESS
    
    # Spans
    spans: List[Span] = field(default_factory=list)
    
    # Service path
    service_path: List[str] = field(default_factory=list)


@dataclass
class Service:
    """Сервис приложения"""
    service_id: str
    
    # Identity
    name: str = ""
    display_name: str = ""
    
    # Type
    service_type: ServiceType = ServiceType.MICROSERVICE
    
    # Environment
    environment: str = ""  # production, staging, development
    
    # Version
    version: str = ""
    
    # Status
    status: ServiceStatus = ServiceStatus.UNKNOWN
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)  # service IDs
    dependents: List[str] = field(default_factory=list)  # service IDs
    
    # Instances
    instances: int = 0
    
    # Metrics
    avg_response_time_ms: float = 0.0
    error_rate: float = 0.0
    throughput_rpm: float = 0.0
    apdex: float = 0.0
    
    # Resource
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Owner
    owner_team: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class Error:
    """Ошибка приложения"""
    error_id: str
    
    # Source
    service_id: str = ""
    trace_id: str = ""
    span_id: str = ""
    
    # Error details
    error_type: str = ""
    error_message: str = ""
    error_class: str = ""  # Exception class
    
    # Stack trace
    stack_trace: List[str] = field(default_factory=list)
    
    # Context
    http_method: str = ""
    http_url: str = ""
    user_id: str = ""
    
    # Severity
    severity: ErrorSeverity = ErrorSeverity.ERROR
    
    # Fingerprint (for grouping)
    fingerprint: str = ""
    
    # Count
    occurrence_count: int = 1
    
    # Status
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None
    
    # Timestamps
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)


@dataclass
class Anomaly:
    """Аномалия"""
    anomaly_id: str
    
    # Source
    service_id: str = ""
    metric_name: str = ""
    
    # Type
    anomaly_type: AnomalyType = AnomalyType.LATENCY_SPIKE
    
    # Values
    expected_value: float = 0.0
    actual_value: float = 0.0
    deviation_percent: float = 0.0
    
    # Severity
    severity: ErrorSeverity = ErrorSeverity.WARNING
    
    # Duration
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    # Status
    is_resolved: bool = False


@dataclass
class SLADefinition:
    """Определение SLA"""
    sla_id: str
    
    # Identity
    name: str = ""
    
    # Service
    service_id: str = ""
    
    # Targets
    availability_target: float = 99.9  # percent
    latency_target_ms: float = 200.0  # P95
    error_rate_target: float = 0.1  # percent
    
    # Window
    measurement_window_hours: int = 24
    
    # Status
    is_compliant: bool = True


@dataclass
class SLAReport:
    """Отчет SLA"""
    report_id: str
    
    # SLA
    sla_id: str = ""
    service_id: str = ""
    
    # Period
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime = field(default_factory=datetime.now)
    
    # Metrics
    availability: float = 0.0
    latency_p95_ms: float = 0.0
    error_rate: float = 0.0
    
    # Compliance
    availability_compliant: bool = True
    latency_compliant: bool = True
    error_rate_compliant: bool = True
    overall_compliant: bool = True
    
    # Violation minutes
    violation_minutes: int = 0


@dataclass
class UserSession:
    """Пользовательская сессия"""
    session_id: str
    
    # User
    user_id: str = ""
    
    # Device
    device_type: str = ""  # desktop, mobile, tablet
    browser: str = ""
    os: str = ""
    
    # Location
    country: str = ""
    region: str = ""
    city: str = ""
    
    # Session
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    # Pages
    page_views: int = 0
    
    # Performance
    avg_page_load_ms: float = 0.0
    
    # Actions
    actions: int = 0
    errors: int = 0


@dataclass
class EndpointMetrics:
    """Метрики эндпоинта"""
    endpoint_id: str
    
    # Identity
    service_id: str = ""
    method: str = ""  # GET, POST, etc.
    path: str = ""
    
    # Metrics
    request_count: int = 0
    error_count: int = 0
    
    # Latency
    latency_avg_ms: float = 0.0
    latency_p50_ms: float = 0.0
    latency_p95_ms: float = 0.0
    latency_p99_ms: float = 0.0
    
    # Throughput
    rpm: float = 0.0  # requests per minute
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)


@dataclass
class APMMetrics:
    """Метрики APM"""
    metrics_id: str
    
    # Services
    total_services: int = 0
    healthy_services: int = 0
    
    # Transactions
    transactions_per_minute: float = 0.0
    avg_response_time_ms: float = 0.0
    
    # Errors
    error_rate: float = 0.0
    errors_per_minute: float = 0.0
    
    # Apdex
    overall_apdex: float = 0.0
    
    # Anomalies
    active_anomalies: int = 0
    
    # SLA
    sla_compliance_rate: float = 0.0
    
    # Timestamps
    collected_at: datetime = field(default_factory=datetime.now)


class APMPlatform:
    """Платформа APM"""
    
    def __init__(self, platform_name: str = "apm"):
        self.platform_name = platform_name
        self.services: Dict[str, Service] = {}
        self.traces: Dict[str, Trace] = {}
        self.errors: Dict[str, Error] = {}
        self.anomalies: Dict[str, Anomaly] = {}
        self.slas: Dict[str, SLADefinition] = {}
        self.sessions: Dict[str, UserSession] = {}
        self.endpoints: Dict[str, EndpointMetrics] = {}
        
    async def register_service(self, name: str,
                              service_type: ServiceType,
                              environment: str = "production",
                              version: str = "1.0.0",
                              owner_team: str = "") -> Service:
        """Регистрация сервиса"""
        service = Service(
            service_id=f"svc_{uuid.uuid4().hex[:8]}",
            name=name,
            display_name=name,
            service_type=service_type,
            environment=environment,
            version=version,
            owner_team=owner_team,
            status=ServiceStatus.HEALTHY,
            instances=random.randint(2, 8)
        )
        
        # Initialize metrics
        service.avg_response_time_ms = random.uniform(20, 200)
        service.error_rate = random.uniform(0.01, 2.0)
        service.throughput_rpm = random.uniform(100, 10000)
        service.apdex = random.uniform(0.85, 0.99)
        service.cpu_usage = random.uniform(20, 70)
        service.memory_usage = random.uniform(40, 80)
        
        self.services[service.service_id] = service
        return service
        
    async def add_dependency(self, service_id: str, depends_on_id: str):
        """Добавление зависимости"""
        service = self.services.get(service_id)
        depends_on = self.services.get(depends_on_id)
        
        if service and depends_on:
            if depends_on_id not in service.dependencies:
                service.dependencies.append(depends_on_id)
            if service_id not in depends_on.dependents:
                depends_on.dependents.append(service_id)
                
    async def record_trace(self, entry_service_id: str,
                          http_method: str = "GET",
                          http_url: str = "",
                          user_id: str = "") -> Trace:
        """Запись трассировки"""
        trace = Trace(
            trace_id=f"trc_{uuid.uuid4().hex[:16]}",
            entry_service=entry_service_id,
            http_method=http_method,
            http_url=http_url,
            user_id=user_id,
            status=TransactionStatus.SUCCESS
        )
        
        # Generate spans
        service = self.services.get(entry_service_id)
        if service:
            trace.service_path = [service.name]
            await self._generate_spans(trace, service)
            
        # Calculate total duration
        if trace.spans:
            trace.duration_ms = sum(s.duration_ms for s in trace.spans if s.parent_span_id == "")
            trace.root_span_id = trace.spans[0].span_id
            
        self.traces[trace.trace_id] = trace
        return trace
        
    async def _generate_spans(self, trace: Trace, service: Service,
                             parent_span_id: str = "", depth: int = 0):
        """Генерация spans"""
        if depth > 4:
            return
            
        # Root span
        span = Span(
            span_id=f"spn_{uuid.uuid4().hex[:12]}",
            trace_id=trace.trace_id,
            parent_span_id=parent_span_id,
            name=f"{service.name}.{trace.http_method}",
            service_name=service.name,
            operation_name=trace.http_url or "/api/endpoint",
            operation_kind="server" if not parent_span_id else "client",
            duration_ms=random.uniform(5, 100),
            status=TransactionStatus.SUCCESS if random.random() > 0.05 else TransactionStatus.ERROR
        )
        
        span.tags["service.name"] = service.name
        span.tags["http.method"] = trace.http_method
        span.tags["http.url"] = trace.http_url
        
        span.end_time = span.start_time + timedelta(milliseconds=span.duration_ms)
        
        trace.spans.append(span)
        
        # Child spans for dependencies
        for dep_id in service.dependencies[:2]:  # Limit to 2 dependencies per level
            dep_service = self.services.get(dep_id)
            if dep_service and dep_service.name not in trace.service_path:
                trace.service_path.append(dep_service.name)
                await self._generate_spans(trace, dep_service, span.span_id, depth + 1)
                
    async def record_error(self, service_id: str,
                          error_type: str,
                          error_message: str,
                          error_class: str = "Exception",
                          trace_id: str = "",
                          severity: ErrorSeverity = ErrorSeverity.ERROR) -> Error:
        """Запись ошибки"""
        # Create fingerprint for grouping
        fingerprint = f"{service_id}:{error_class}:{error_type}"
        
        # Check if similar error exists
        existing = None
        for err in self.errors.values():
            if err.fingerprint == fingerprint and not err.is_resolved:
                existing = err
                break
                
        if existing:
            existing.occurrence_count += 1
            existing.last_seen = datetime.now()
            return existing
            
        error = Error(
            error_id=f"err_{uuid.uuid4().hex[:8]}",
            service_id=service_id,
            trace_id=trace_id,
            error_type=error_type,
            error_message=error_message,
            error_class=error_class,
            severity=severity,
            fingerprint=fingerprint,
            stack_trace=[
                f"at {service_id}.handler({error_class}.java:42)",
                f"at {service_id}.process(Service.java:128)",
                f"at {service_id}.main(Application.java:15)"
            ]
        )
        
        self.errors[error.error_id] = error
        
        # Update service status
        service = self.services.get(service_id)
        if service and severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]:
            service.error_rate += 0.1
            if service.error_rate > 5:
                service.status = ServiceStatus.DEGRADED
                
        return error
        
    async def detect_anomaly(self, service_id: str,
                            metric_name: str,
                            anomaly_type: AnomalyType,
                            expected: float,
                            actual: float) -> Anomaly:
        """Обнаружение аномалии"""
        deviation = abs(actual - expected) / expected * 100 if expected else 0
        
        severity = ErrorSeverity.INFO
        if deviation > 50:
            severity = ErrorSeverity.WARNING
        if deviation > 100:
            severity = ErrorSeverity.ERROR
        if deviation > 200:
            severity = ErrorSeverity.CRITICAL
            
        anomaly = Anomaly(
            anomaly_id=f"anm_{uuid.uuid4().hex[:8]}",
            service_id=service_id,
            metric_name=metric_name,
            anomaly_type=anomaly_type,
            expected_value=expected,
            actual_value=actual,
            deviation_percent=deviation,
            severity=severity
        )
        
        self.anomalies[anomaly.anomaly_id] = anomaly
        return anomaly
        
    async def create_sla(self, name: str,
                        service_id: str,
                        availability_target: float = 99.9,
                        latency_target_ms: float = 200.0,
                        error_rate_target: float = 0.1) -> SLADefinition:
        """Создание SLA"""
        sla = SLADefinition(
            sla_id=f"sla_{uuid.uuid4().hex[:8]}",
            name=name,
            service_id=service_id,
            availability_target=availability_target,
            latency_target_ms=latency_target_ms,
            error_rate_target=error_rate_target
        )
        
        self.slas[sla.sla_id] = sla
        return sla
        
    async def check_sla_compliance(self, sla_id: str) -> SLAReport:
        """Проверка соответствия SLA"""
        sla = self.slas.get(sla_id)
        if not sla:
            return None
            
        service = self.services.get(sla.service_id)
        if not service:
            return None
            
        # Simulate metrics
        availability = random.uniform(99.0, 99.99)
        latency_p95 = service.avg_response_time_ms * random.uniform(1.5, 3.0)
        error_rate = service.error_rate
        
        report = SLAReport(
            report_id=f"slr_{uuid.uuid4().hex[:8]}",
            sla_id=sla_id,
            service_id=sla.service_id,
            start_time=datetime.now() - timedelta(hours=sla.measurement_window_hours),
            end_time=datetime.now(),
            availability=availability,
            latency_p95_ms=latency_p95,
            error_rate=error_rate,
            availability_compliant=availability >= sla.availability_target,
            latency_compliant=latency_p95 <= sla.latency_target_ms,
            error_rate_compliant=error_rate <= sla.error_rate_target
        )
        
        report.overall_compliant = (
            report.availability_compliant and
            report.latency_compliant and
            report.error_rate_compliant
        )
        
        if not report.overall_compliant:
            report.violation_minutes = random.randint(5, 60)
            
        sla.is_compliant = report.overall_compliant
        
        return report
        
    async def record_session(self, user_id: str,
                            device_type: str = "desktop",
                            browser: str = "Chrome",
                            country: str = "US") -> UserSession:
        """Запись сессии пользователя"""
        session = UserSession(
            session_id=f"ses_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            device_type=device_type,
            browser=browser,
            os=random.choice(["Windows", "macOS", "Linux", "iOS", "Android"]),
            country=country,
            page_views=random.randint(1, 20),
            avg_page_load_ms=random.uniform(500, 3000),
            actions=random.randint(5, 50),
            errors=random.randint(0, 3)
        )
        
        self.sessions[session.session_id] = session
        return session
        
    async def update_endpoint_metrics(self, service_id: str,
                                      method: str,
                                      path: str,
                                      latency_ms: float,
                                      is_error: bool = False) -> EndpointMetrics:
        """Обновление метрик эндпоинта"""
        endpoint_key = f"{service_id}:{method}:{path}"
        
        if endpoint_key not in self.endpoints:
            self.endpoints[endpoint_key] = EndpointMetrics(
                endpoint_id=f"ep_{uuid.uuid4().hex[:8]}",
                service_id=service_id,
                method=method,
                path=path
            )
            
        endpoint = self.endpoints[endpoint_key]
        endpoint.request_count += 1
        if is_error:
            endpoint.error_count += 1
            
        # Update latency (rolling average)
        endpoint.latency_avg_ms = (
            endpoint.latency_avg_ms * (endpoint.request_count - 1) + latency_ms
        ) / endpoint.request_count
        
        endpoint.latency_p50_ms = endpoint.latency_avg_ms * 0.8
        endpoint.latency_p95_ms = endpoint.latency_avg_ms * 2.0
        endpoint.latency_p99_ms = endpoint.latency_avg_ms * 3.0
        
        return endpoint
        
    async def collect_metrics(self) -> APMMetrics:
        """Сбор метрик"""
        healthy = sum(1 for s in self.services.values() if s.status == ServiceStatus.HEALTHY)
        
        total_rpm = sum(s.throughput_rpm for s in self.services.values())
        avg_response = sum(s.avg_response_time_ms for s in self.services.values()) / len(self.services) if self.services else 0
        avg_error_rate = sum(s.error_rate for s in self.services.values()) / len(self.services) if self.services else 0
        avg_apdex = sum(s.apdex for s in self.services.values()) / len(self.services) if self.services else 0
        
        active_anomalies = sum(1 for a in self.anomalies.values() if not a.is_resolved)
        
        # SLA compliance
        compliant_slas = sum(1 for s in self.slas.values() if s.is_compliant)
        sla_compliance = (compliant_slas / len(self.slas) * 100) if self.slas else 100.0
        
        return APMMetrics(
            metrics_id=f"apm_{uuid.uuid4().hex[:8]}",
            total_services=len(self.services),
            healthy_services=healthy,
            transactions_per_minute=total_rpm,
            avg_response_time_ms=avg_response,
            error_rate=avg_error_rate,
            overall_apdex=avg_apdex,
            active_anomalies=active_anomalies,
            sla_compliance_rate=sla_compliance
        )
        
    def get_service_map(self) -> List[Dict[str, Any]]:
        """Получение карты сервисов"""
        nodes = []
        edges = []
        
        for service in self.services.values():
            nodes.append({
                "id": service.service_id,
                "name": service.name,
                "type": service.service_type.value,
                "status": service.status.value,
                "apdex": service.apdex
            })
            
            for dep_id in service.dependencies:
                edges.append({
                    "source": service.service_id,
                    "target": dep_id
                })
                
        return {"nodes": nodes, "edges": edges}
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        by_type = {}
        for stype in ServiceType:
            by_type[stype.value] = sum(1 for s in self.services.values() if s.service_type == stype)
            
        by_status = {}
        for status in ServiceStatus:
            by_status[status.value] = sum(1 for s in self.services.values() if s.status == status)
            
        errors_by_severity = {}
        for severity in ErrorSeverity:
            errors_by_severity[severity.value] = sum(
                1 for e in self.errors.values()
                if e.severity == severity and not e.is_resolved
            )
            
        anomalies_by_type = {}
        for atype in AnomalyType:
            anomalies_by_type[atype.value] = sum(
                1 for a in self.anomalies.values()
                if a.anomaly_type == atype and not a.is_resolved
            )
            
        return {
            "total_services": len(self.services),
            "by_type": by_type,
            "by_status": by_status,
            "total_traces": len(self.traces),
            "total_errors": len(self.errors),
            "unresolved_errors": sum(1 for e in self.errors.values() if not e.is_resolved),
            "errors_by_severity": errors_by_severity,
            "total_anomalies": len(self.anomalies),
            "active_anomalies": sum(1 for a in self.anomalies.values() if not a.is_resolved),
            "anomalies_by_type": anomalies_by_type,
            "sla_definitions": len(self.slas),
            "sessions": len(self.sessions),
            "endpoints": len(self.endpoints)
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 369: APM Platform")
    print("=" * 60)
    
    platform = APMPlatform(platform_name="enterprise-apm")
    print("✓ APM Platform initialized")
    
    # Register Services
    print("\n🔧 Registering Application Services...")
    
    services_data = [
        ("api-gateway", ServiceType.GATEWAY, "v2.5.0", "Platform Team"),
        ("user-service", ServiceType.MICROSERVICE, "v3.2.1", "User Team"),
        ("auth-service", ServiceType.MICROSERVICE, "v1.8.0", "Security Team"),
        ("order-service", ServiceType.MICROSERVICE, "v4.1.0", "Commerce Team"),
        ("payment-service", ServiceType.MICROSERVICE, "v2.0.5", "Payments Team"),
        ("inventory-service", ServiceType.MICROSERVICE, "v1.5.3", "Supply Team"),
        ("notification-service", ServiceType.MICROSERVICE, "v1.2.0", "Platform Team"),
        ("search-service", ServiceType.MICROSERVICE, "v2.3.1", "Search Team"),
        ("postgres-primary", ServiceType.DATABASE, "v15.2", "DBA Team"),
        ("redis-cache", ServiceType.CACHE, "v7.0", "Platform Team"),
        ("rabbitmq", ServiceType.QUEUE, "v3.12", "Platform Team"),
        ("external-payment-api", ServiceType.EXTERNAL, "v1.0", "External")
    ]
    
    services = {}
    for name, stype, version, team in services_data:
        service = await platform.register_service(name, stype, "production", version, team)
        services[name] = service
        status_icon = "🟢" if service.status == ServiceStatus.HEALTHY else "🟡"
        print(f"  {status_icon} {name} ({stype.value}) - Apdex: {service.apdex:.2f}")
        
    # Add Dependencies
    print("\n🔗 Creating Service Dependencies...")
    
    dependencies = [
        ("api-gateway", "user-service"),
        ("api-gateway", "auth-service"),
        ("api-gateway", "order-service"),
        ("api-gateway", "search-service"),
        ("user-service", "postgres-primary"),
        ("user-service", "redis-cache"),
        ("auth-service", "postgres-primary"),
        ("auth-service", "redis-cache"),
        ("order-service", "postgres-primary"),
        ("order-service", "inventory-service"),
        ("order-service", "payment-service"),
        ("order-service", "notification-service"),
        ("payment-service", "external-payment-api"),
        ("payment-service", "postgres-primary"),
        ("inventory-service", "postgres-primary"),
        ("notification-service", "rabbitmq"),
        ("search-service", "redis-cache")
    ]
    
    for source, target in dependencies:
        source_id = services[source].service_id
        target_id = services[target].service_id
        await platform.add_dependency(source_id, target_id)
        
    print(f"  ✓ Created {len(dependencies)} service dependencies")
    
    # Record Traces
    print("\n📊 Recording Distributed Traces...")
    
    endpoints = [
        ("GET", "/api/users/me"),
        ("POST", "/api/orders"),
        ("GET", "/api/products/search"),
        ("POST", "/api/auth/login"),
        ("GET", "/api/inventory/check")
    ]
    
    for method, url in endpoints:
        for _ in range(10):
            trace = await platform.record_trace(
                services["api-gateway"].service_id,
                method,
                url,
                f"user_{random.randint(1000, 9999)}"
            )
            
    print(f"  ✓ Recorded {len(platform.traces)} traces")
    print(f"  📈 Total spans: {sum(len(t.spans) for t in platform.traces.values())}")
    
    # Record Errors
    print("\n❌ Recording Application Errors...")
    
    errors_data = [
        ("user-service", "NullPointerException", "User not found in cache", ErrorSeverity.ERROR),
        ("payment-service", "TimeoutException", "External payment API timeout", ErrorSeverity.CRITICAL),
        ("order-service", "ValidationException", "Invalid order payload", ErrorSeverity.WARNING),
        ("auth-service", "AuthenticationException", "Invalid credentials", ErrorSeverity.WARNING),
        ("search-service", "IndexNotFoundException", "Search index not available", ErrorSeverity.ERROR)
    ]
    
    for service_name, error_type, message, severity in errors_data:
        for _ in range(random.randint(1, 10)):
            await platform.record_error(
                services[service_name].service_id,
                error_type,
                message,
                error_type,
                severity=severity
            )
            
    print(f"  ✓ Recorded {len(platform.errors)} unique errors")
    
    # Detect Anomalies
    print("\n🔍 Detecting Anomalies...")
    
    anomalies_data = [
        ("order-service", "latency_p95", AnomalyType.LATENCY_SPIKE, 150.0, 450.0),
        ("payment-service", "error_rate", AnomalyType.ERROR_RATE_SPIKE, 0.5, 5.0),
        ("user-service", "throughput", AnomalyType.THROUGHPUT_DROP, 5000.0, 2000.0),
        ("api-gateway", "cpu_usage", AnomalyType.CPU_SPIKE, 50.0, 85.0)
    ]
    
    for service_name, metric, atype, expected, actual in anomalies_data:
        anomaly = await platform.detect_anomaly(
            services[service_name].service_id,
            metric,
            atype,
            expected,
            actual
        )
        print(f"  ⚠️ {service_name}: {atype.value} (deviation: {anomaly.deviation_percent:.0f}%)")
        
    # Create SLAs
    print("\n📋 Creating SLA Definitions...")
    
    sla_configs = [
        ("API Gateway SLA", "api-gateway", 99.95, 100.0, 0.5),
        ("User Service SLA", "user-service", 99.9, 150.0, 1.0),
        ("Order Service SLA", "order-service", 99.9, 200.0, 0.5),
        ("Payment Service SLA", "payment-service", 99.99, 300.0, 0.1)
    ]
    
    for name, service_name, avail, latency, error in sla_configs:
        sla = await platform.create_sla(
            name,
            services[service_name].service_id,
            avail,
            latency,
            error
        )
        await platform.check_sla_compliance(sla.sla_id)
        status = "✅" if sla.is_compliant else "❌"
        print(f"  {status} {name}: Availability>{avail}%, Latency<{latency}ms")
        
    # Record User Sessions
    print("\n👥 Recording User Sessions...")
    
    devices = ["desktop", "mobile", "tablet"]
    browsers = ["Chrome", "Safari", "Firefox", "Edge"]
    countries = ["US", "UK", "DE", "FR", "JP"]
    
    for _ in range(50):
        await platform.record_session(
            f"user_{random.randint(1000, 9999)}",
            random.choice(devices),
            random.choice(browsers),
            random.choice(countries)
        )
        
    print(f"  ✓ Recorded {len(platform.sessions)} user sessions")
    
    # Update Endpoint Metrics
    print("\n📈 Collecting Endpoint Metrics...")
    
    for method, path in endpoints:
        for _ in range(100):
            await platform.update_endpoint_metrics(
                services["api-gateway"].service_id,
                method,
                path,
                random.uniform(20, 500),
                random.random() < 0.02
            )
            
    print(f"  ✓ {len(platform.endpoints)} endpoints tracked")
    
    # Collect Metrics
    metrics = await platform.collect_metrics()
    
    # Service Table
    print("\n🔧 Application Services:")
    
    print("\n  ┌──────────────────────────┬───────────────────┬───────────────┬───────────┬─────────────┬───────────┐")
    print("  │ Service                  │ Type              │ Status        │ Apdex     │ Latency(ms) │ Error(%)  │")
    print("  ├──────────────────────────┼───────────────────┼───────────────┼───────────┼─────────────┼───────────┤")
    
    for service in platform.services.values():
        name = service.name[:24].ljust(24)
        stype = service.service_type.value[:17].ljust(17)
        status = service.status.value[:13].ljust(13)
        apdex = f"{service.apdex:.2f}".ljust(9)
        latency = f"{service.avg_response_time_ms:.1f}".ljust(11)
        error = f"{service.error_rate:.2f}".ljust(9)
        
        print(f"  │ {name} │ {stype} │ {status} │ {apdex} │ {latency} │ {error} │")
        
    print("  └──────────────────────────┴───────────────────┴───────────────┴───────────┴─────────────┴───────────┘")
    
    # Service Map
    print("\n🗺️ Service Dependency Map:")
    
    for service in list(platform.services.values())[:6]:
        deps = [platform.services.get(d) for d in service.dependencies if platform.services.get(d)]
        dep_names = [d.name for d in deps]
        if dep_names:
            print(f"  {service.name} → {', '.join(dep_names)}")
            
    # Active Errors
    print("\n❌ Active Errors:")
    
    for error in list(platform.errors.values())[:6]:
        if not error.is_resolved:
            service = platform.services.get(error.service_id)
            svc_name = service.name if service else "Unknown"
            severity_icon = {"info": "ℹ️", "warning": "⚠️", "error": "❌", "critical": "🔴"}
            icon = severity_icon.get(error.severity.value, "❓")
            print(f"  {icon} [{svc_name}] {error.error_type}: {error.error_message[:40]} (x{error.occurrence_count})")
            
    # Anomalies
    print("\n🔍 Active Anomalies:")
    
    for anomaly in platform.anomalies.values():
        if not anomaly.is_resolved:
            service = platform.services.get(anomaly.service_id)
            svc_name = service.name if service else "Unknown"
            print(f"  ⚠️ {svc_name}: {anomaly.anomaly_type.value} - expected {anomaly.expected_value:.1f}, actual {anomaly.actual_value:.1f}")
            
    # SLA Status
    print("\n📋 SLA Compliance:")
    
    for sla in platform.slas.values():
        service = platform.services.get(sla.service_id)
        svc_name = service.name if service else "Unknown"
        status = "✅ Compliant" if sla.is_compliant else "❌ Violation"
        print(f"  {status} {sla.name}")
        
    # Endpoint Performance
    print("\n📈 Top Endpoints by Latency:")
    
    sorted_endpoints = sorted(platform.endpoints.values(), key=lambda x: -x.latency_p95_ms)[:5]
    for ep in sorted_endpoints:
        print(f"  {ep.method:6s} {ep.path:25s} │ P95: {ep.latency_p95_ms:.0f}ms │ Req: {ep.request_count}")
        
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📊 Service Distribution:")
    
    # By Type
    print("\n  By Type:")
    for stype, count in stats["by_type"].items():
        if count > 0:
            bar = "█" * count
            print(f"    {stype:15s} │ {bar} ({count})")
            
    # By Status
    print("\n  By Status:")
    for status, count in stats["by_status"].items():
        if count > 0:
            bar = "█" * count
            print(f"    {status:12s} │ {bar} ({count})")
            
    # Errors by Severity
    print("\n  Errors by Severity:")
    for severity, count in stats["errors_by_severity"].items():
        if count > 0:
            bar = "█" * count
            print(f"    {severity:10s} │ {bar} ({count})")
            
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                        APM Platform                                │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Services:                {stats['total_services']:>12}                      │")
    print(f"│ Healthy Services:              {metrics.healthy_services:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Transactions/min:              {metrics.transactions_per_minute:>12.0f}                      │")
    print(f"│ Avg Response Time:             {metrics.avg_response_time_ms:>11.1f}ms                      │")
    print(f"│ Overall Apdex:                 {metrics.overall_apdex:>12.2f}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Error Rate:                    {metrics.error_rate:>11.2f}%                      │")
    print(f"│ Unresolved Errors:             {stats['unresolved_errors']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Active Anomalies:              {stats['active_anomalies']:>12}                      │")
    print(f"│ Distributed Traces:            {stats['total_traces']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ SLA Definitions:               {stats['sla_definitions']:>12}                      │")
    print(f"│ SLA Compliance:                {metrics.sla_compliance_rate:>11.1f}%                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ User Sessions:                 {stats['sessions']:>12}                      │")
    print(f"│ Tracked Endpoints:             {stats['endpoints']:>12}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("APM Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
