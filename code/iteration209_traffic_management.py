#!/usr/bin/env python3
"""
Server Init - Iteration 209: Traffic Management Platform
Платформа управления трафиком

Функционал:
- Load Balancing - балансировка нагрузки
- Rate Limiting - ограничение частоты запросов
- Circuit Breaker - прерыватель цепи
- Traffic Shaping - формирование трафика
- Request Routing - маршрутизация запросов
- Retry Policies - политики повторов
- Timeout Management - управление таймаутами
- Traffic Mirroring - зеркалирование трафика
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid
import time


class LoadBalancerAlgorithm(Enum):
    """Алгоритм балансировки"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED = "weighted"
    RANDOM = "random"
    IP_HASH = "ip_hash"


class CircuitState(Enum):
    """Состояние прерывателя"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class RequestResult(Enum):
    """Результат запроса"""
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"


@dataclass
class Backend:
    """Бэкенд сервер"""
    backend_id: str
    address: str = ""
    port: int = 8080
    
    # Weight
    weight: int = 1
    
    # Status
    healthy: bool = True
    active_connections: int = 0
    
    # Metrics
    total_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0


@dataclass
class RateLimitConfig:
    """Конфигурация rate limiting"""
    requests_per_second: int = 100
    burst_size: int = 20
    
    # Per client
    per_client: bool = True


@dataclass
class RateLimiter:
    """Rate limiter"""
    config: RateLimitConfig = field(default_factory=RateLimitConfig)
    
    # Token bucket
    tokens: float = 0
    last_refill: datetime = field(default_factory=datetime.now)
    
    # Per client tokens
    client_tokens: Dict[str, float] = field(default_factory=dict)
    
    def allow_request(self, client_id: str = "") -> bool:
        """Проверка разрешения запроса"""
        now = datetime.now()
        elapsed = (now - self.last_refill).total_seconds()
        
        # Refill tokens
        self.tokens = min(
            self.config.burst_size,
            self.tokens + elapsed * self.config.requests_per_second
        )
        self.last_refill = now
        
        if self.config.per_client and client_id:
            client_tokens = self.client_tokens.get(client_id, self.config.burst_size)
            if client_tokens >= 1:
                self.client_tokens[client_id] = client_tokens - 1
                return True
            return False
            
        if self.tokens >= 1:
            self.tokens -= 1
            return True
            
        return False


@dataclass
class CircuitBreakerConfig:
    """Конфигурация circuit breaker"""
    failure_threshold: int = 5
    recovery_timeout_seconds: int = 30
    half_open_requests: int = 3


@dataclass
class CircuitBreaker:
    """Circuit breaker"""
    circuit_id: str
    config: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    
    # State
    state: CircuitState = CircuitState.CLOSED
    
    # Counters
    failure_count: int = 0
    success_count: int = 0
    half_open_count: int = 0
    
    # Time
    last_failure_time: Optional[datetime] = None
    last_state_change: datetime = field(default_factory=datetime.now)
    
    def record_success(self):
        """Запись успешного запроса"""
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_count += 1
            if self.half_open_count >= self.config.half_open_requests:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.last_state_change = datetime.now()
        else:
            self.success_count += 1
            
    def record_failure(self):
        """Запись неудачного запроса"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
            self.last_state_change = datetime.now()
            
    def allow_request(self) -> bool:
        """Проверка разрешения запроса"""
        if self.state == CircuitState.CLOSED:
            return True
            
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout passed
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed >= self.config.recovery_timeout_seconds:
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_count = 0
                    self.last_state_change = datetime.now()
                    return True
            return False
            
        # Half open - allow limited requests
        return self.half_open_count < self.config.half_open_requests


@dataclass
class RetryPolicy:
    """Политика повторов"""
    max_retries: int = 3
    initial_delay_ms: int = 100
    max_delay_ms: int = 5000
    multiplier: float = 2.0
    
    # Retryable codes
    retryable_errors: List[int] = field(default_factory=lambda: [500, 502, 503, 504])


@dataclass
class TimeoutConfig:
    """Конфигурация таймаутов"""
    connect_timeout_ms: int = 1000
    request_timeout_ms: int = 30000
    idle_timeout_ms: int = 60000


@dataclass
class Route:
    """Маршрут"""
    route_id: str
    path: str = "/"
    
    # Match
    methods: List[str] = field(default_factory=lambda: ["GET"])
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Target
    target_backends: List[str] = field(default_factory=list)
    
    # Policies
    rate_limit: Optional[RateLimitConfig] = None
    retry_policy: Optional[RetryPolicy] = None
    timeout: Optional[TimeoutConfig] = None


@dataclass
class Request:
    """Запрос"""
    request_id: str
    path: str = "/"
    method: str = "GET"
    
    # Client
    client_id: str = ""
    client_ip: str = ""
    
    # Headers
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Result
    result: RequestResult = RequestResult.SUCCESS
    backend_id: Optional[str] = None
    response_time_ms: float = 0
    
    # Time
    timestamp: datetime = field(default_factory=datetime.now)


class LoadBalancer:
    """Балансировщик нагрузки"""
    
    def __init__(self, algorithm: LoadBalancerAlgorithm = LoadBalancerAlgorithm.ROUND_ROBIN):
        self.algorithm = algorithm
        self.current_index = 0
        
    def select_backend(self, backends: List[Backend], client_ip: str = "") -> Optional[Backend]:
        """Выбор бэкенда"""
        healthy_backends = [b for b in backends if b.healthy]
        
        if not healthy_backends:
            return None
            
        if self.algorithm == LoadBalancerAlgorithm.ROUND_ROBIN:
            backend = healthy_backends[self.current_index % len(healthy_backends)]
            self.current_index += 1
            return backend
            
        elif self.algorithm == LoadBalancerAlgorithm.LEAST_CONNECTIONS:
            return min(healthy_backends, key=lambda b: b.active_connections)
            
        elif self.algorithm == LoadBalancerAlgorithm.WEIGHTED:
            total_weight = sum(b.weight for b in healthy_backends)
            r = random.uniform(0, total_weight)
            cumulative = 0
            for backend in healthy_backends:
                cumulative += backend.weight
                if r <= cumulative:
                    return backend
            return healthy_backends[-1]
            
        elif self.algorithm == LoadBalancerAlgorithm.RANDOM:
            return random.choice(healthy_backends)
            
        elif self.algorithm == LoadBalancerAlgorithm.IP_HASH:
            if client_ip:
                idx = hash(client_ip) % len(healthy_backends)
                return healthy_backends[idx]
            return healthy_backends[0]
            
        return healthy_backends[0]


class TrafficManagementPlatform:
    """Платформа управления трафиком"""
    
    def __init__(self):
        self.backends: Dict[str, Backend] = {}
        self.routes: Dict[str, Route] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.requests: List[Request] = []
        self.load_balancer = LoadBalancer()
        self.global_rate_limiter = RateLimiter()
        
    def add_backend(self, address: str, port: int = 8080, weight: int = 1) -> Backend:
        """Добавление бэкенда"""
        backend = Backend(
            backend_id=f"backend_{uuid.uuid4().hex[:8]}",
            address=address,
            port=port,
            weight=weight
        )
        self.backends[backend.backend_id] = backend
        
        # Create circuit breaker for backend
        cb = CircuitBreaker(
            circuit_id=f"cb_{backend.backend_id}"
        )
        self.circuit_breakers[backend.backend_id] = cb
        
        return backend
        
    def add_route(self, path: str, methods: List[str] = None,
                 rate_limit: RateLimitConfig = None) -> Route:
        """Добавление маршрута"""
        route = Route(
            route_id=f"route_{uuid.uuid4().hex[:8]}",
            path=path,
            methods=methods or ["GET"],
            target_backends=list(self.backends.keys()),
            rate_limit=rate_limit
        )
        self.routes[route.route_id] = route
        return route
        
    async def process_request(self, path: str, method: str = "GET",
                            client_id: str = "", client_ip: str = "") -> Request:
        """Обработка запроса"""
        request = Request(
            request_id=f"req_{uuid.uuid4().hex[:8]}",
            path=path,
            method=method,
            client_id=client_id,
            client_ip=client_ip
        )
        
        # Rate limiting
        if not self.global_rate_limiter.allow_request(client_id):
            request.result = RequestResult.RATE_LIMITED
            self.requests.append(request)
            return request
            
        # Select backend
        backends_list = list(self.backends.values())
        backend = self.load_balancer.select_backend(backends_list, client_ip)
        
        if not backend:
            request.result = RequestResult.FAILURE
            self.requests.append(request)
            return request
            
        # Check circuit breaker
        cb = self.circuit_breakers.get(backend.backend_id)
        if cb and not cb.allow_request():
            request.result = RequestResult.FAILURE
            self.requests.append(request)
            return request
            
        # Process request
        request.backend_id = backend.backend_id
        backend.active_connections += 1
        backend.total_requests += 1
        
        # Simulate request
        start_time = time.time()
        await asyncio.sleep(random.uniform(0.001, 0.02))
        
        # Simulate result
        success = random.random() > 0.1
        
        request.response_time_ms = (time.time() - start_time) * 1000
        
        if success:
            request.result = RequestResult.SUCCESS
            if cb:
                cb.record_success()
        else:
            request.result = RequestResult.FAILURE
            backend.failed_requests += 1
            if cb:
                cb.record_failure()
                
        backend.active_connections -= 1
        
        # Update avg response time
        n = backend.total_requests
        backend.avg_response_time_ms = (
            (backend.avg_response_time_ms * (n - 1) + request.response_time_ms) / n
        )
        
        self.requests.append(request)
        return request
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total = len(self.requests)
        success = len([r for r in self.requests if r.result == RequestResult.SUCCESS])
        rate_limited = len([r for r in self.requests if r.result == RequestResult.RATE_LIMITED])
        
        return {
            "total_requests": total,
            "successful_requests": success,
            "failed_requests": total - success - rate_limited,
            "rate_limited": rate_limited,
            "success_rate": (success / total * 100) if total > 0 else 0,
            "total_backends": len(self.backends),
            "healthy_backends": len([b for b in self.backends.values() if b.healthy]),
            "total_routes": len(self.routes)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 209: Traffic Management Platform")
    print("=" * 60)
    
    platform = TrafficManagementPlatform()
    print("✓ Traffic Management Platform created")
    
    # Add backends
    print("\n🖥️ Adding Backends...")
    
    backends_config = [
        ("10.0.1.1", 8080, 3),
        ("10.0.1.2", 8080, 2),
        ("10.0.1.3", 8080, 2),
        ("10.0.1.4", 8080, 1),
        ("10.0.1.5", 8080, 1),
    ]
    
    for address, port, weight in backends_config:
        backend = platform.add_backend(address, port, weight)
        print(f"  ✓ {address}:{port} (weight: {weight})")
        
    # Add routes
    print("\n🛤️ Adding Routes...")
    
    routes_config = [
        ("/api/users", ["GET", "POST"]),
        ("/api/orders", ["GET", "POST", "PUT"]),
        ("/api/products", ["GET"]),
        ("/health", ["GET"]),
    ]
    
    for path, methods in routes_config:
        route = platform.add_route(path, methods)
        print(f"  ✓ {path} [{', '.join(methods)}]")
        
    # Configure rate limiting
    print("\n⚡ Configuring Rate Limiting...")
    
    platform.global_rate_limiter.config = RateLimitConfig(
        requests_per_second=1000,
        burst_size=100,
        per_client=True
    )
    print(f"  ✓ Global: {platform.global_rate_limiter.config.requests_per_second} req/s")
    
    # Process requests
    print("\n📨 Processing Requests...")
    
    clients = ["client_001", "client_002", "client_003", "client_004", "client_005"]
    paths = ["/api/users", "/api/orders", "/api/products", "/health"]
    
    for i in range(50):
        client = random.choice(clients)
        path = random.choice(paths)
        ip = f"192.168.1.{random.randint(1, 100)}"
        
        await platform.process_request(path, "GET", client, ip)
        
    print(f"  ✓ Processed {len(platform.requests)} requests")
    
    # Display backend stats
    print("\n📊 Backend Statistics:")
    
    print("\n  ┌────────────────┬──────────┬──────────┬────────────┬────────────┐")
    print("  │ Backend        │ Requests │ Failed   │ Avg Time   │ Status     │")
    print("  ├────────────────┼──────────┼──────────┼────────────┼────────────┤")
    
    for backend in platform.backends.values():
        address = backend.address[:14].ljust(14)
        requests = str(backend.total_requests).center(8)
        failed = str(backend.failed_requests).center(8)
        avg_time = f"{backend.avg_response_time_ms:.1f}ms".center(10)
        status = "🟢 Healthy" if backend.healthy else "🔴 Down"
        status = status[:10].ljust(10)
        print(f"  │ {address} │ {requests} │ {failed} │ {avg_time} │ {status} │")
        
    print("  └────────────────┴──────────┴──────────┴────────────┴────────────┘")
    
    # Circuit breaker status
    print("\n🔌 Circuit Breaker Status:")
    
    for backend_id, cb in platform.circuit_breakers.items():
        backend = platform.backends.get(backend_id)
        name = backend.address if backend else backend_id
        
        state_icons = {
            CircuitState.CLOSED: "🟢",
            CircuitState.OPEN: "🔴",
            CircuitState.HALF_OPEN: "🟡"
        }
        
        icon = state_icons.get(cb.state, "⚪")
        print(f"  {icon} {name}: {cb.state.value} (failures: {cb.failure_count})")
        
    # Request results distribution
    print("\n📈 Request Results:")
    
    result_counts = {}
    for request in platform.requests:
        r = request.result.value
        result_counts[r] = result_counts.get(r, 0) + 1
        
    for result, count in result_counts.items():
        pct = count / len(platform.requests) * 100 if platform.requests else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"  {result:12s} [{bar}] {count} ({pct:.1f}%)")
        
    # Load balancing distribution
    print("\n⚖️ Load Balancing Distribution:")
    
    backend_requests = {}
    for request in platform.requests:
        if request.backend_id:
            backend_requests[request.backend_id] = backend_requests.get(request.backend_id, 0) + 1
            
    total_distributed = sum(backend_requests.values())
    
    for backend_id, count in backend_requests.items():
        backend = platform.backends.get(backend_id)
        name = backend.address if backend else backend_id
        pct = count / total_distributed * 100 if total_distributed > 0 else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"  {name:12s} [{bar}] {count} ({pct:.1f}%)")
        
    # Response time analysis
    print("\n⏱️ Response Time Analysis:")
    
    response_times = [r.response_time_ms for r in platform.requests if r.response_time_ms > 0]
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Min: {min_time:.2f}ms")
        print(f"  Max: {max_time:.2f}ms")
        
        # Histogram
        print("\n  Response Time Distribution:")
        buckets = [5, 10, 15, 20, 25]
        for bucket in buckets:
            count = len([t for t in response_times if t <= bucket])
            pct = count / len(response_times) * 100
            bar = "█" * int(pct / 5)
            print(f"    <{bucket}ms: {bar} ({pct:.0f}%)")
            
    # Client traffic
    print("\n👥 Traffic by Client:")
    
    client_requests = {}
    for request in platform.requests:
        c = request.client_id or "anonymous"
        client_requests[c] = client_requests.get(c, 0) + 1
        
    for client, count in sorted(client_requests.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * (count // 2)
        print(f"  {client:12s} {bar} ({count})")
        
    # Path statistics
    print("\n🛤️ Traffic by Path:")
    
    path_requests = {}
    for request in platform.requests:
        p = request.path
        path_requests[p] = path_requests.get(p, 0) + 1
        
    for path, count in sorted(path_requests.items(), key=lambda x: x[1], reverse=True):
        pct = count / len(platform.requests) * 100
        print(f"  {path:20s} {count:3d} ({pct:.0f}%)")
        
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📈 Platform Statistics:")
    
    print(f"\n  Total Requests: {stats['total_requests']}")
    print(f"  Successful: {stats['successful_requests']}")
    print(f"  Failed: {stats['failed_requests']}")
    print(f"  Rate Limited: {stats['rate_limited']}")
    print(f"  Success Rate: {stats['success_rate']:.1f}%")
    print(f"  Backends: {stats['healthy_backends']}/{stats['total_backends']} healthy")
    print(f"  Routes: {stats['total_routes']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                  Traffic Management Dashboard                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Requests:                {stats['total_requests']:>12}                        │")
    print(f"│ Successful:                    {stats['successful_requests']:>12}                        │")
    print(f"│ Failed:                        {stats['failed_requests']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Success Rate:                    {stats['success_rate']:>10.1f}%                   │")
    print(f"│ Healthy Backends:            {stats['healthy_backends']}/{stats['total_backends']:>8}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Traffic Management Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
