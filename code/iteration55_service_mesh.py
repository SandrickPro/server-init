#!/usr/bin/env python3
"""
Server Init - Iteration 55: Service Mesh Management
Управление сервисной сеткой

Функционал:
- Service Discovery - обнаружение сервисов
- Traffic Management - управление трафиком
- Load Balancing - балансировка нагрузки
- Circuit Breaker - предохранитель
- Retry Policies - политики повторов
- Rate Limiting - ограничение скорости
- mTLS Management - управление mTLS
- Observability - наблюдаемость (traces, metrics)
"""

import json
import asyncio
import hashlib
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
from abc import ABC, abstractmethod
import random
from collections import defaultdict
import uuid


class ServiceStatus(Enum):
    """Статус сервиса"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class LoadBalancerAlgorithm(Enum):
    """Алгоритм балансировки"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"
    WEIGHTED = "weighted"
    CONSISTENT_HASH = "consistent_hash"


class CircuitState(Enum):
    """Состояние предохранителя"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class TrafficPolicy(Enum):
    """Политика трафика"""
    ALLOW_ALL = "allow_all"
    DENY_ALL = "deny_all"
    CUSTOM = "custom"


class TLSMode(Enum):
    """Режим TLS"""
    DISABLE = "disable"
    PERMISSIVE = "permissive"
    STRICT = "strict"
    MUTUAL = "mutual"


@dataclass
class ServiceEndpoint:
    """Эндпоинт сервиса"""
    endpoint_id: str
    address: str
    port: int
    
    # Метаданные
    zone: str = ""
    region: str = ""
    
    # Веса
    weight: int = 100
    
    # Состояние
    status: ServiceStatus = ServiceStatus.UNKNOWN
    
    # Метрики
    active_connections: int = 0
    total_requests: int = 0
    error_count: int = 0
    avg_latency_ms: float = 0.0
    
    # Health check
    last_health_check: Optional[datetime] = None
    consecutive_failures: int = 0


@dataclass
class Service:
    """Сервис в mesh"""
    service_id: str
    name: str
    namespace: str = "default"
    
    # Эндпоинты
    endpoints: List[ServiceEndpoint] = field(default_factory=list)
    
    # Версии
    version: str = "v1"
    
    # Метаданные
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    
    # Порты
    ports: List[Dict[str, Any]] = field(default_factory=list)
    
    # Статус
    status: ServiceStatus = ServiceStatus.UNKNOWN
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class VirtualService:
    """Виртуальный сервис для маршрутизации"""
    vs_id: str
    name: str
    
    # Хосты
    hosts: List[str] = field(default_factory=list)
    
    # HTTP маршруты
    http_routes: List[Dict[str, Any]] = field(default_factory=list)
    
    # TCP маршруты
    tcp_routes: List[Dict[str, Any]] = field(default_factory=list)
    
    # Таймауты
    timeout_seconds: int = 30
    
    # Retries
    retries: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DestinationRule:
    """Правило назначения"""
    rule_id: str
    name: str
    host: str
    
    # Traffic policy
    load_balancer: LoadBalancerAlgorithm = LoadBalancerAlgorithm.ROUND_ROBIN
    
    # Connection pool
    max_connections: int = 100
    max_pending_requests: int = 100
    max_requests_per_connection: int = 0
    
    # Circuit breaker
    consecutive_errors: int = 5
    interval_seconds: int = 30
    base_ejection_time_seconds: int = 30
    max_ejection_percent: int = 100
    
    # Subsets
    subsets: List[Dict[str, Any]] = field(default_factory=list)
    
    # TLS
    tls_mode: TLSMode = TLSMode.DISABLE


@dataclass
class CircuitBreaker:
    """Предохранитель"""
    breaker_id: str
    service_name: str
    
    # Конфигурация
    failure_threshold: int = 5
    success_threshold: int = 3
    timeout_seconds: int = 30
    half_open_max_calls: int = 3
    
    # Состояние
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure: Optional[datetime] = None
    last_state_change: datetime = field(default_factory=datetime.now)
    
    # Статистика
    total_requests: int = 0
    rejected_requests: int = 0


@dataclass
class RateLimiter:
    """Ограничитель скорости"""
    limiter_id: str
    service_name: str
    
    # Лимиты
    requests_per_second: int = 100
    burst_size: int = 200
    
    # Состояние
    current_tokens: float = 0.0
    last_refill: datetime = field(default_factory=datetime.now)
    
    # Статистика
    total_requests: int = 0
    rejected_requests: int = 0


@dataclass
class RetryPolicy:
    """Политика повторов"""
    policy_id: str
    service_name: str
    
    # Конфигурация
    max_retries: int = 3
    retry_on: List[str] = field(default_factory=lambda: ["5xx", "reset", "connect-failure"])
    per_try_timeout_seconds: int = 2
    
    # Backoff
    base_interval_ms: int = 25
    max_interval_ms: int = 1000


@dataclass
class TrafficSplit:
    """Разделение трафика"""
    split_id: str
    service_name: str
    
    # Версии и веса
    versions: Dict[str, int] = field(default_factory=dict)  # version -> weight %
    
    # Canary
    canary_version: Optional[str] = None
    canary_weight: int = 0
    
    # Headers для маршрутизации
    header_routing: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TraceSpan:
    """Span трассировки"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    
    # Операция
    operation_name: str = ""
    service_name: str = ""
    
    # Время
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_ms: float = 0.0
    
    # Статус
    status: str = "ok"  # ok, error
    
    # Теги
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Логи
    logs: List[Dict[str, Any]] = field(default_factory=list)


class ServiceRegistry:
    """Реестр сервисов"""
    
    def __init__(self):
        self.services: Dict[str, Service] = {}
        self.endpoints: Dict[str, List[ServiceEndpoint]] = defaultdict(list)
        
    def register_service(self, name: str, namespace: str = "default",
                          **kwargs) -> Service:
        """Регистрация сервиса"""
        service = Service(
            service_id=f"svc_{uuid.uuid4().hex[:8]}",
            name=name,
            namespace=namespace,
            **kwargs
        )
        
        key = f"{namespace}/{name}"
        self.services[key] = service
        return service
        
    def add_endpoint(self, service_name: str, address: str, port: int,
                      namespace: str = "default", **kwargs) -> ServiceEndpoint:
        """Добавление эндпоинта"""
        endpoint = ServiceEndpoint(
            endpoint_id=f"ep_{uuid.uuid4().hex[:8]}",
            address=address,
            port=port,
            **kwargs
        )
        
        key = f"{namespace}/{service_name}"
        self.endpoints[key].append(endpoint)
        
        if key in self.services:
            self.services[key].endpoints.append(endpoint)
            
        return endpoint
        
    def deregister_endpoint(self, service_name: str, endpoint_id: str,
                             namespace: str = "default"):
        """Удаление эндпоинта"""
        key = f"{namespace}/{service_name}"
        
        self.endpoints[key] = [
            ep for ep in self.endpoints[key]
            if ep.endpoint_id != endpoint_id
        ]
        
        if key in self.services:
            self.services[key].endpoints = [
                ep for ep in self.services[key].endpoints
                if ep.endpoint_id != endpoint_id
            ]
            
    def discover_service(self, name: str, namespace: str = "default") -> Optional[Service]:
        """Обнаружение сервиса"""
        key = f"{namespace}/{name}"
        return self.services.get(key)
        
    def get_healthy_endpoints(self, service_name: str,
                               namespace: str = "default") -> List[ServiceEndpoint]:
        """Получение здоровых эндпоинтов"""
        key = f"{namespace}/{service_name}"
        return [
            ep for ep in self.endpoints.get(key, [])
            if ep.status == ServiceStatus.HEALTHY
        ]
        
    async def health_check(self, service_name: str, namespace: str = "default"):
        """Проверка здоровья"""
        key = f"{namespace}/{service_name}"
        
        for endpoint in self.endpoints.get(key, []):
            # Симуляция health check
            await asyncio.sleep(0.01)
            
            # 90% вероятность здорового эндпоинта
            if random.random() > 0.1:
                endpoint.status = ServiceStatus.HEALTHY
                endpoint.consecutive_failures = 0
            else:
                endpoint.consecutive_failures += 1
                if endpoint.consecutive_failures >= 3:
                    endpoint.status = ServiceStatus.UNHEALTHY
                else:
                    endpoint.status = ServiceStatus.DEGRADED
                    
            endpoint.last_health_check = datetime.now()


class LoadBalancer:
    """Балансировщик нагрузки"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.round_robin_counters: Dict[str, int] = defaultdict(int)
        
    def select_endpoint(self, service_name: str, namespace: str = "default",
                         algorithm: LoadBalancerAlgorithm = LoadBalancerAlgorithm.ROUND_ROBIN,
                         **kwargs) -> Optional[ServiceEndpoint]:
        """Выбор эндпоинта"""
        endpoints = self.registry.get_healthy_endpoints(service_name, namespace)
        
        if not endpoints:
            return None
            
        if algorithm == LoadBalancerAlgorithm.ROUND_ROBIN:
            return self._round_robin(service_name, endpoints)
        elif algorithm == LoadBalancerAlgorithm.LEAST_CONNECTIONS:
            return self._least_connections(endpoints)
        elif algorithm == LoadBalancerAlgorithm.RANDOM:
            return random.choice(endpoints)
        elif algorithm == LoadBalancerAlgorithm.WEIGHTED:
            return self._weighted(endpoints)
        elif algorithm == LoadBalancerAlgorithm.CONSISTENT_HASH:
            key = kwargs.get("hash_key", "")
            return self._consistent_hash(endpoints, key)
            
        return endpoints[0]
        
    def _round_robin(self, service_name: str,
                      endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Round Robin"""
        idx = self.round_robin_counters[service_name] % len(endpoints)
        self.round_robin_counters[service_name] += 1
        return endpoints[idx]
        
    def _least_connections(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Least Connections"""
        return min(endpoints, key=lambda ep: ep.active_connections)
        
    def _weighted(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Weighted selection"""
        total_weight = sum(ep.weight for ep in endpoints)
        r = random.uniform(0, total_weight)
        
        cumulative = 0
        for ep in endpoints:
            cumulative += ep.weight
            if r <= cumulative:
                return ep
                
        return endpoints[-1]
        
    def _consistent_hash(self, endpoints: List[ServiceEndpoint],
                          key: str) -> ServiceEndpoint:
        """Consistent Hash"""
        if not key:
            return random.choice(endpoints)
            
        hash_val = int(hashlib.md5(key.encode()).hexdigest(), 16)
        idx = hash_val % len(endpoints)
        return endpoints[idx]


class CircuitBreakerManager:
    """Менеджер предохранителей"""
    
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
        
    def get_or_create(self, service_name: str, **kwargs) -> CircuitBreaker:
        """Получение или создание предохранителя"""
        if service_name not in self.breakers:
            self.breakers[service_name] = CircuitBreaker(
                breaker_id=f"cb_{uuid.uuid4().hex[:8]}",
                service_name=service_name,
                **kwargs
            )
        return self.breakers[service_name]
        
    def can_execute(self, service_name: str) -> bool:
        """Можно ли выполнить запрос"""
        breaker = self.breakers.get(service_name)
        if not breaker:
            return True
            
        if breaker.state == CircuitState.CLOSED:
            return True
            
        if breaker.state == CircuitState.OPEN:
            # Проверка таймаута
            elapsed = (datetime.now() - breaker.last_state_change).total_seconds()
            if elapsed >= breaker.timeout_seconds:
                breaker.state = CircuitState.HALF_OPEN
                breaker.last_state_change = datetime.now()
                breaker.success_count = 0
                return True
            return False
            
        if breaker.state == CircuitState.HALF_OPEN:
            # Ограниченное количество запросов
            return breaker.success_count < breaker.half_open_max_calls
            
        return True
        
    def record_success(self, service_name: str):
        """Запись успеха"""
        breaker = self.breakers.get(service_name)
        if not breaker:
            return
            
        breaker.total_requests += 1
        
        if breaker.state == CircuitState.HALF_OPEN:
            breaker.success_count += 1
            if breaker.success_count >= breaker.success_threshold:
                breaker.state = CircuitState.CLOSED
                breaker.last_state_change = datetime.now()
                breaker.failure_count = 0
                
        elif breaker.state == CircuitState.CLOSED:
            breaker.failure_count = 0
            
    def record_failure(self, service_name: str):
        """Запись неудачи"""
        breaker = self.breakers.get(service_name)
        if not breaker:
            return
            
        breaker.total_requests += 1
        breaker.failure_count += 1
        breaker.last_failure = datetime.now()
        
        if breaker.state == CircuitState.HALF_OPEN:
            breaker.state = CircuitState.OPEN
            breaker.last_state_change = datetime.now()
            
        elif breaker.state == CircuitState.CLOSED:
            if breaker.failure_count >= breaker.failure_threshold:
                breaker.state = CircuitState.OPEN
                breaker.last_state_change = datetime.now()


class RateLimiterManager:
    """Менеджер ограничителей скорости"""
    
    def __init__(self):
        self.limiters: Dict[str, RateLimiter] = {}
        
    def create_limiter(self, service_name: str, rps: int = 100,
                        burst: int = 200) -> RateLimiter:
        """Создание лимитера"""
        limiter = RateLimiter(
            limiter_id=f"rl_{uuid.uuid4().hex[:8]}",
            service_name=service_name,
            requests_per_second=rps,
            burst_size=burst,
            current_tokens=float(burst)
        )
        
        self.limiters[service_name] = limiter
        return limiter
        
    def allow_request(self, service_name: str) -> bool:
        """Разрешён ли запрос"""
        limiter = self.limiters.get(service_name)
        if not limiter:
            return True
            
        # Token bucket refill
        now = datetime.now()
        elapsed = (now - limiter.last_refill).total_seconds()
        
        tokens_to_add = elapsed * limiter.requests_per_second
        limiter.current_tokens = min(
            limiter.burst_size,
            limiter.current_tokens + tokens_to_add
        )
        limiter.last_refill = now
        
        limiter.total_requests += 1
        
        if limiter.current_tokens >= 1:
            limiter.current_tokens -= 1
            return True
        else:
            limiter.rejected_requests += 1
            return False


class TrafficManager:
    """Менеджер трафика"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.virtual_services: Dict[str, VirtualService] = {}
        self.destination_rules: Dict[str, DestinationRule] = {}
        self.traffic_splits: Dict[str, TrafficSplit] = {}
        
    def create_virtual_service(self, name: str, hosts: List[str],
                                **kwargs) -> VirtualService:
        """Создание виртуального сервиса"""
        vs = VirtualService(
            vs_id=f"vs_{uuid.uuid4().hex[:8]}",
            name=name,
            hosts=hosts,
            **kwargs
        )
        
        self.virtual_services[name] = vs
        return vs
        
    def create_destination_rule(self, name: str, host: str,
                                  **kwargs) -> DestinationRule:
        """Создание правила назначения"""
        rule = DestinationRule(
            rule_id=f"dr_{uuid.uuid4().hex[:8]}",
            name=name,
            host=host,
            **kwargs
        )
        
        self.destination_rules[name] = rule
        return rule
        
    def setup_traffic_split(self, service_name: str,
                             versions: Dict[str, int]) -> TrafficSplit:
        """Настройка разделения трафика"""
        split = TrafficSplit(
            split_id=f"ts_{uuid.uuid4().hex[:8]}",
            service_name=service_name,
            versions=versions
        )
        
        self.traffic_splits[service_name] = split
        return split
        
    def route_request(self, service_name: str,
                       headers: Dict[str, str] = None) -> str:
        """Маршрутизация запроса"""
        split = self.traffic_splits.get(service_name)
        
        if not split:
            return "v1"
            
        # Header-based routing
        if headers and split.header_routing:
            for rule in split.header_routing:
                header_name = rule.get("header")
                header_value = rule.get("value")
                target_version = rule.get("version")
                
                if headers.get(header_name) == header_value:
                    return target_version
                    
        # Weight-based routing
        total_weight = sum(split.versions.values())
        r = random.uniform(0, total_weight)
        
        cumulative = 0
        for version, weight in split.versions.items():
            cumulative += weight
            if r <= cumulative:
                return version
                
        return list(split.versions.keys())[0]


class TracingManager:
    """Менеджер трассировки"""
    
    def __init__(self):
        self.traces: Dict[str, List[TraceSpan]] = defaultdict(list)
        
    def start_span(self, operation_name: str, service_name: str,
                    trace_id: str = None, parent_span_id: str = None) -> TraceSpan:
        """Начало span"""
        span = TraceSpan(
            trace_id=trace_id or f"trace_{uuid.uuid4().hex[:16]}",
            span_id=f"span_{uuid.uuid4().hex[:8]}",
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            service_name=service_name
        )
        
        self.traces[span.trace_id].append(span)
        return span
        
    def end_span(self, span: TraceSpan, status: str = "ok"):
        """Завершение span"""
        span.end_time = datetime.now()
        span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
        span.status = status
        
    def add_span_tag(self, span: TraceSpan, key: str, value: str):
        """Добавление тега"""
        span.tags[key] = value
        
    def get_trace(self, trace_id: str) -> List[TraceSpan]:
        """Получение трассы"""
        return sorted(self.traces.get(trace_id, []), key=lambda s: s.start_time)
        
    def get_service_latency(self, service_name: str) -> Dict[str, float]:
        """Получение latency сервиса"""
        spans = [
            s for spans in self.traces.values()
            for s in spans
            if s.service_name == service_name and s.end_time
        ]
        
        if not spans:
            return {"avg": 0, "p50": 0, "p95": 0, "p99": 0}
            
        durations = sorted([s.duration_ms for s in spans])
        n = len(durations)
        
        return {
            "avg": sum(durations) / n,
            "p50": durations[int(n * 0.5)],
            "p95": durations[int(n * 0.95)] if n > 20 else durations[-1],
            "p99": durations[int(n * 0.99)] if n > 100 else durations[-1]
        }


class ServiceMeshPlatform:
    """Платформа Service Mesh"""
    
    def __init__(self):
        self.registry = ServiceRegistry()
        self.load_balancer = LoadBalancer(self.registry)
        self.circuit_breaker_manager = CircuitBreakerManager()
        self.rate_limiter_manager = RateLimiterManager()
        self.traffic_manager = TrafficManager(self.registry)
        self.tracing_manager = TracingManager()
        
    async def execute_request(self, service_name: str, namespace: str = "default",
                               headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Выполнение запроса через mesh"""
        result = {
            "success": False,
            "endpoint": None,
            "version": None,
            "latency_ms": 0,
            "error": None
        }
        
        # Rate limiting
        if not self.rate_limiter_manager.allow_request(service_name):
            result["error"] = "rate_limited"
            return result
            
        # Circuit breaker
        if not self.circuit_breaker_manager.can_execute(service_name):
            result["error"] = "circuit_open"
            return result
            
        # Version routing
        version = self.traffic_manager.route_request(service_name, headers)
        result["version"] = version
        
        # Load balancing
        endpoint = self.load_balancer.select_endpoint(service_name, namespace)
        
        if not endpoint:
            result["error"] = "no_healthy_endpoints"
            self.circuit_breaker_manager.record_failure(service_name)
            return result
            
        result["endpoint"] = f"{endpoint.address}:{endpoint.port}"
        
        # Start trace
        span = self.tracing_manager.start_span(
            operation_name=f"call_{service_name}",
            service_name=service_name
        )
        
        # Simulate request
        start = time.time()
        await asyncio.sleep(random.uniform(0.001, 0.05))
        
        # 95% success rate
        if random.random() > 0.05:
            result["success"] = True
            endpoint.total_requests += 1
            self.circuit_breaker_manager.record_success(service_name)
            self.tracing_manager.end_span(span, "ok")
        else:
            result["error"] = "request_failed"
            endpoint.error_count += 1
            self.circuit_breaker_manager.record_failure(service_name)
            self.tracing_manager.end_span(span, "error")
            
        result["latency_ms"] = (time.time() - start) * 1000
        
        return result
        
    def get_status(self) -> Dict[str, Any]:
        """Статус mesh"""
        services = list(self.registry.services.values())
        
        total_endpoints = sum(len(s.endpoints) for s in services)
        healthy_endpoints = sum(
            len([e for e in s.endpoints if e.status == ServiceStatus.HEALTHY])
            for s in services
        )
        
        return {
            "services": len(services),
            "endpoints": {
                "total": total_endpoints,
                "healthy": healthy_endpoints
            },
            "circuit_breakers": {
                "total": len(self.circuit_breaker_manager.breakers),
                "open": len([
                    b for b in self.circuit_breaker_manager.breakers.values()
                    if b.state == CircuitState.OPEN
                ])
            },
            "rate_limiters": len(self.rate_limiter_manager.limiters),
            "virtual_services": len(self.traffic_manager.virtual_services),
            "traces": len(self.tracing_manager.traces)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 55: Service Mesh Management")
    print("=" * 60)
    
    async def demo():
        # Создание платформы
        mesh = ServiceMeshPlatform()
        print("✓ Service Mesh Platform created")
        
        # Регистрация сервисов
        print("\n📡 Registering services...")
        
        services = [
            ("api-gateway", "production"),
            ("user-service", "production"),
            ("order-service", "production"),
            ("payment-service", "production"),
            ("notification-service", "production")
        ]
        
        for name, namespace in services:
            svc = mesh.registry.register_service(name, namespace)
            print(f"  ✓ Registered: {name}")
            
            # Добавление эндпоинтов
            for i in range(3):
                ep = mesh.registry.add_endpoint(
                    name,
                    f"10.0.{random.randint(1, 254)}.{random.randint(1, 254)}",
                    8080 + i,
                    namespace,
                    zone=f"zone-{chr(97 + i)}",
                    weight=100
                )
                ep.status = ServiceStatus.HEALTHY
                
        # Health checks
        print("\n🏥 Running health checks...")
        
        for name, namespace in services[:2]:
            await mesh.registry.health_check(name, namespace)
            healthy = len(mesh.registry.get_healthy_endpoints(name, namespace))
            print(f"  {name}: {healthy}/3 healthy")
            
        # Traffic management
        print("\n🚦 Setting up traffic management...")
        
        # Canary deployment
        split = mesh.traffic_manager.setup_traffic_split(
            "user-service",
            {"v1": 90, "v2": 10}
        )
        print(f"  ✓ Traffic split: v1=90%, v2=10%")
        
        # Virtual service
        vs = mesh.traffic_manager.create_virtual_service(
            "user-service-vs",
            ["user-service.production.svc.cluster.local"],
            timeout_seconds=30,
            retries={"attempts": 3, "perTryTimeout": "2s"}
        )
        print(f"  ✓ Virtual service: {vs.name}")
        
        # Destination rule
        dr = mesh.traffic_manager.create_destination_rule(
            "user-service-dr",
            "user-service",
            load_balancer=LoadBalancerAlgorithm.LEAST_CONNECTIONS,
            max_connections=1000,
            consecutive_errors=5,
            tls_mode=TLSMode.MUTUAL
        )
        print(f"  ✓ Destination rule: {dr.name}")
        
        # Rate limiting
        print("\n⏱️ Setting up rate limiting...")
        
        rl = mesh.rate_limiter_manager.create_limiter(
            "api-gateway",
            rps=1000,
            burst=2000
        )
        print(f"  ✓ Rate limiter for api-gateway: {rl.requests_per_second} RPS")
        
        # Circuit breaker
        print("\n🔌 Setting up circuit breakers...")
        
        cb = mesh.circuit_breaker_manager.get_or_create(
            "payment-service",
            failure_threshold=5,
            timeout_seconds=30
        )
        print(f"  ✓ Circuit breaker for payment-service")
        print(f"    Threshold: {cb.failure_threshold} failures")
        print(f"    Timeout: {cb.timeout_seconds}s")
        
        # Execute requests
        print("\n📤 Executing requests through mesh...")
        
        results = {"success": 0, "failed": 0, "rate_limited": 0, "circuit_open": 0}
        
        for i in range(50):
            service = random.choice(["user-service", "order-service", "payment-service"])
            
            result = await mesh.execute_request(
                service,
                "production",
                headers={"x-user-id": f"user_{i % 10}"}
            )
            
            if result["success"]:
                results["success"] += 1
            elif result["error"] == "rate_limited":
                results["rate_limited"] += 1
            elif result["error"] == "circuit_open":
                results["circuit_open"] += 1
            else:
                results["failed"] += 1
                
        print(f"  Requests: 50")
        print(f"  Success: {results['success']}")
        print(f"  Failed: {results['failed']}")
        print(f"  Rate limited: {results['rate_limited']}")
        print(f"  Circuit open: {results['circuit_open']}")
        
        # Version routing
        print("\n🔀 Version routing test:")
        
        version_counts = defaultdict(int)
        for _ in range(100):
            version = mesh.traffic_manager.route_request("user-service")
            version_counts[version] += 1
            
        for version, count in sorted(version_counts.items()):
            print(f"  {version}: {count}%")
            
        # Tracing
        print("\n🔍 Tracing:")
        
        latency = mesh.tracing_manager.get_service_latency("user-service")
        print(f"  user-service latency:")
        print(f"    Avg: {latency['avg']:.2f}ms")
        print(f"    P50: {latency['p50']:.2f}ms")
        print(f"    P95: {latency['p95']:.2f}ms")
        
        # Circuit breaker status
        print("\n🔌 Circuit breaker status:")
        
        for name, breaker in mesh.circuit_breaker_manager.breakers.items():
            print(f"  {name}: {breaker.state.value}")
            print(f"    Failures: {breaker.failure_count}")
            print(f"    Total requests: {breaker.total_requests}")
            
        # Platform status
        print("\n📊 Mesh Status:")
        status = mesh.get_status()
        
        print(f"  Services: {status['services']}")
        print(f"  Endpoints: {status['endpoints']['healthy']}/{status['endpoints']['total']} healthy")
        print(f"  Circuit breakers: {status['circuit_breakers']['total']} ({status['circuit_breakers']['open']} open)")
        print(f"  Rate limiters: {status['rate_limiters']}")
        print(f"  Virtual services: {status['virtual_services']}")
        print(f"  Traces: {status['traces']}")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Service Mesh Platform initialized!")
    print("=" * 60)
