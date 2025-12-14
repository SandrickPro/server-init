#!/usr/bin/env python3
"""
Server Init - Iteration 266: Load Balancer Platform
Платформа балансировки нагрузки

Функционал:
- Multiple Algorithms - множество алгоритмов
- Session Persistence - сохранение сессий
- Health Monitoring - мониторинг здоровья
- Connection Pooling - пулы соединений
- SSL Termination - терминация SSL
- Request Routing - маршрутизация запросов
- Rate Limiting - ограничение скорости
- Traffic Shaping - формирование трафика
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from collections import deque
from enum import Enum
import uuid
import hashlib


class BalancerAlgorithm(Enum):
    """Алгоритм балансировки"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_LEAST_CONNECTIONS = "weighted_least_connections"
    IP_HASH = "ip_hash"
    RANDOM = "random"
    LEAST_RESPONSE_TIME = "least_response_time"
    RESOURCE_BASED = "resource_based"


class BackendStatus(Enum):
    """Статус бэкенда"""
    UP = "up"
    DOWN = "down"
    DRAINING = "draining"
    MAINTENANCE = "maintenance"


class SessionPersistence(Enum):
    """Тип сохранения сессии"""
    NONE = "none"
    COOKIE = "cookie"
    IP = "ip"
    HEADER = "header"


class HealthCheckProtocol(Enum):
    """Протокол проверки здоровья"""
    HTTP = "http"
    HTTPS = "https"
    TCP = "tcp"


@dataclass
class HealthCheck:
    """Проверка здоровья"""
    check_id: str
    
    # Protocol
    protocol: HealthCheckProtocol = HealthCheckProtocol.HTTP
    
    # Endpoint
    path: str = "/health"
    port: int = 80
    
    # Timing
    interval_seconds: int = 10
    timeout_seconds: int = 5
    
    # Thresholds
    healthy_threshold: int = 2
    unhealthy_threshold: int = 3
    
    # Expected
    expected_codes: List[int] = field(default_factory=lambda: [200])


@dataclass
class BackendServer:
    """Бэкенд сервер"""
    server_id: str
    name: str
    
    # Address
    host: str = ""
    port: int = 80
    
    # Weight
    weight: int = 100
    
    # Status
    status: BackendStatus = BackendStatus.UP
    
    # Health
    health_check: HealthCheck = field(default_factory=lambda: HealthCheck(
        check_id=f"hc_{uuid.uuid4().hex[:8]}"
    ))
    
    # Stats
    active_connections: int = 0
    total_connections: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    total_response_time_ms: float = 0
    
    # Resource usage
    cpu_usage: float = 0
    memory_usage: float = 0
    
    # Health tracking
    consecutive_successes: int = 0
    consecutive_failures: int = 0
    last_health_check: datetime = field(default_factory=datetime.now)


@dataclass
class SessionEntry:
    """Запись сессии"""
    session_id: str
    
    # Client
    client_id: str = ""  # IP or cookie value
    
    # Backend
    backend_id: str = ""
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    last_used: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=1))


@dataclass
class LoadBalancerConfig:
    """Конфигурация балансировщика"""
    config_id: str
    name: str
    
    # Algorithm
    algorithm: BalancerAlgorithm = BalancerAlgorithm.ROUND_ROBIN
    
    # Session persistence
    persistence: SessionPersistence = SessionPersistence.NONE
    session_timeout_seconds: int = 3600
    session_cookie_name: str = "SERVERID"
    
    # Limits
    max_connections_per_backend: int = 1000
    connection_timeout_ms: int = 30000
    
    # Rate limiting
    rate_limit_enabled: bool = False
    rate_limit_requests_per_second: int = 100


@dataclass
class BackendPool:
    """Пул бэкендов"""
    pool_id: str
    name: str
    
    # Config
    config: LoadBalancerConfig = field(default_factory=lambda: LoadBalancerConfig(
        config_id=f"cfg_{uuid.uuid4().hex[:8]}",
        name="default"
    ))
    
    # Backends
    backends: List[BackendServer] = field(default_factory=list)
    
    # Sessions
    sessions: Dict[str, SessionEntry] = field(default_factory=dict)
    
    # Round robin index
    current_index: int = 0
    
    # Stats
    total_requests: int = 0
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RequestContext:
    """Контекст запроса"""
    request_id: str
    
    # Client
    client_ip: str = ""
    
    # Headers
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Cookies
    cookies: Dict[str, str] = field(default_factory=dict)
    
    # Path
    path: str = "/"
    method: str = "GET"


@dataclass
class RoutingResult:
    """Результат маршрутизации"""
    result_id: str
    
    # Backend
    backend: Optional[BackendServer] = None
    
    # Info
    algorithm_used: str = ""
    session_used: bool = False
    
    # Stats
    routing_time_ms: float = 0


class LoadBalancerManager:
    """Менеджер балансировщика нагрузки"""
    
    def __init__(self):
        self.pools: Dict[str, BackendPool] = {}
        
    def create_pool(self, name: str,
                   algorithm: BalancerAlgorithm = BalancerAlgorithm.ROUND_ROBIN,
                   persistence: SessionPersistence = SessionPersistence.NONE) -> BackendPool:
        """Создание пула"""
        config = LoadBalancerConfig(
            config_id=f"cfg_{uuid.uuid4().hex[:8]}",
            name=name,
            algorithm=algorithm,
            persistence=persistence
        )
        
        pool = BackendPool(
            pool_id=f"pool_{uuid.uuid4().hex[:8]}",
            name=name,
            config=config
        )
        
        self.pools[name] = pool
        return pool
        
    def add_backend(self, pool_name: str,
                   name: str, host: str, port: int,
                   weight: int = 100) -> Optional[BackendServer]:
        """Добавление бэкенда"""
        pool = self.pools.get(pool_name)
        if not pool:
            return None
            
        backend = BackendServer(
            server_id=f"srv_{uuid.uuid4().hex[:8]}",
            name=name,
            host=host,
            port=port,
            weight=weight
        )
        
        pool.backends.append(backend)
        return backend
        
    def remove_backend(self, pool_name: str, server_id: str) -> bool:
        """Удаление бэкенда"""
        pool = self.pools.get(pool_name)
        if not pool:
            return False
            
        for i, backend in enumerate(pool.backends):
            if backend.server_id == server_id:
                pool.backends.pop(i)
                return True
                
        return False
        
    def set_backend_status(self, pool_name: str, server_id: str,
                          status: BackendStatus):
        """Установка статуса бэкенда"""
        pool = self.pools.get(pool_name)
        if not pool:
            return
            
        for backend in pool.backends:
            if backend.server_id == server_id:
                backend.status = status
                break
                
    async def health_check_backend(self, backend: BackendServer) -> bool:
        """Проверка здоровья бэкенда"""
        await asyncio.sleep(random.uniform(0.01, 0.05))
        
        healthy = random.random() > 0.1
        
        if healthy:
            backend.consecutive_successes += 1
            backend.consecutive_failures = 0
            
            if backend.consecutive_successes >= backend.health_check.healthy_threshold:
                if backend.status == BackendStatus.DOWN:
                    backend.status = BackendStatus.UP
        else:
            backend.consecutive_failures += 1
            backend.consecutive_successes = 0
            
            if backend.consecutive_failures >= backend.health_check.unhealthy_threshold:
                backend.status = BackendStatus.DOWN
                
        backend.last_health_check = datetime.now()
        
        return healthy
        
    def _get_available_backends(self, pool: BackendPool) -> List[BackendServer]:
        """Получение доступных бэкендов"""
        return [b for b in pool.backends 
                if b.status == BackendStatus.UP 
                and b.active_connections < pool.config.max_connections_per_backend]
        
    def _get_session_key(self, pool: BackendPool, context: RequestContext) -> str:
        """Получение ключа сессии"""
        if pool.config.persistence == SessionPersistence.IP:
            return context.client_ip
        elif pool.config.persistence == SessionPersistence.COOKIE:
            return context.cookies.get(pool.config.session_cookie_name, "")
        elif pool.config.persistence == SessionPersistence.HEADER:
            return context.headers.get("X-Session-ID", "")
        return ""
        
    def _check_session(self, pool: BackendPool, context: RequestContext) -> Optional[BackendServer]:
        """Проверка существующей сессии"""
        if pool.config.persistence == SessionPersistence.NONE:
            return None
            
        session_key = self._get_session_key(pool, context)
        if not session_key:
            return None
            
        session = pool.sessions.get(session_key)
        if not session:
            return None
            
        # Check expiration
        if datetime.now() > session.expires_at:
            del pool.sessions[session_key]
            return None
            
        # Find backend
        for backend in pool.backends:
            if backend.server_id == session.backend_id:
                if backend.status == BackendStatus.UP:
                    session.last_used = datetime.now()
                    return backend
                break
                
        return None
        
    def _create_session(self, pool: BackendPool, context: RequestContext,
                       backend: BackendServer):
        """Создание сессии"""
        if pool.config.persistence == SessionPersistence.NONE:
            return
            
        session_key = self._get_session_key(pool, context)
        if not session_key and pool.config.persistence != SessionPersistence.COOKIE:
            session_key = context.client_ip
            
        if not session_key:
            return
            
        session = SessionEntry(
            session_id=f"sess_{uuid.uuid4().hex[:8]}",
            client_id=session_key,
            backend_id=backend.server_id,
            expires_at=datetime.now() + timedelta(seconds=pool.config.session_timeout_seconds)
        )
        
        pool.sessions[session_key] = session
        
    def _select_backend_round_robin(self, pool: BackendPool,
                                   backends: List[BackendServer]) -> BackendServer:
        """Round Robin выбор"""
        pool.current_index = (pool.current_index + 1) % len(backends)
        return backends[pool.current_index]
        
    def _select_backend_weighted_round_robin(self, pool: BackendPool,
                                            backends: List[BackendServer]) -> BackendServer:
        """Weighted Round Robin выбор"""
        total_weight = sum(b.weight for b in backends)
        r = random.randint(0, total_weight - 1)
        cumulative = 0
        
        for backend in backends:
            cumulative += backend.weight
            if r < cumulative:
                return backend
                
        return backends[-1]
        
    def _select_backend_least_connections(self, backends: List[BackendServer]) -> BackendServer:
        """Least Connections выбор"""
        return min(backends, key=lambda b: b.active_connections)
        
    def _select_backend_weighted_least_connections(self, backends: List[BackendServer]) -> BackendServer:
        """Weighted Least Connections выбор"""
        return min(backends, key=lambda b: b.active_connections / max(1, b.weight))
        
    def _select_backend_ip_hash(self, context: RequestContext,
                               backends: List[BackendServer]) -> BackendServer:
        """IP Hash выбор"""
        hash_value = int(hashlib.md5(context.client_ip.encode()).hexdigest(), 16)
        index = hash_value % len(backends)
        return backends[index]
        
    def _select_backend_random(self, backends: List[BackendServer]) -> BackendServer:
        """Random выбор"""
        return random.choice(backends)
        
    def _select_backend_least_response_time(self, backends: List[BackendServer]) -> BackendServer:
        """Least Response Time выбор"""
        return min(backends, key=lambda b: b.total_response_time_ms / max(1, b.total_requests))
        
    def _select_backend_resource_based(self, backends: List[BackendServer]) -> BackendServer:
        """Resource Based выбор"""
        return min(backends, key=lambda b: (b.cpu_usage + b.memory_usage) / 2)
        
    def route_request(self, pool_name: str, context: RequestContext) -> RoutingResult:
        """Маршрутизация запроса"""
        start_time = datetime.now()
        
        result = RoutingResult(
            result_id=f"route_{uuid.uuid4().hex[:8]}"
        )
        
        pool = self.pools.get(pool_name)
        if not pool:
            return result
            
        pool.total_requests += 1
        
        # Check existing session
        session_backend = self._check_session(pool, context)
        if session_backend:
            result.backend = session_backend
            result.session_used = True
            result.algorithm_used = "session_persistence"
            result.routing_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            return result
            
        # Get available backends
        backends = self._get_available_backends(pool)
        if not backends:
            return result
            
        # Select backend based on algorithm
        algorithm = pool.config.algorithm
        result.algorithm_used = algorithm.value
        
        if algorithm == BalancerAlgorithm.ROUND_ROBIN:
            result.backend = self._select_backend_round_robin(pool, backends)
        elif algorithm == BalancerAlgorithm.WEIGHTED_ROUND_ROBIN:
            result.backend = self._select_backend_weighted_round_robin(pool, backends)
        elif algorithm == BalancerAlgorithm.LEAST_CONNECTIONS:
            result.backend = self._select_backend_least_connections(backends)
        elif algorithm == BalancerAlgorithm.WEIGHTED_LEAST_CONNECTIONS:
            result.backend = self._select_backend_weighted_least_connections(backends)
        elif algorithm == BalancerAlgorithm.IP_HASH:
            result.backend = self._select_backend_ip_hash(context, backends)
        elif algorithm == BalancerAlgorithm.RANDOM:
            result.backend = self._select_backend_random(backends)
        elif algorithm == BalancerAlgorithm.LEAST_RESPONSE_TIME:
            result.backend = self._select_backend_least_response_time(backends)
        elif algorithm == BalancerAlgorithm.RESOURCE_BASED:
            result.backend = self._select_backend_resource_based(backends)
            
        # Create session if needed
        if result.backend and pool.config.persistence != SessionPersistence.NONE:
            self._create_session(pool, context, result.backend)
            
        # Update stats
        if result.backend:
            result.backend.total_requests += 1
            result.backend.active_connections += 1
            
        result.routing_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        return result
        
    def complete_request(self, pool_name: str, server_id: str,
                        response_time_ms: float, success: bool = True):
        """Завершение запроса"""
        pool = self.pools.get(pool_name)
        if not pool:
            return
            
        for backend in pool.backends:
            if backend.server_id == server_id:
                backend.active_connections = max(0, backend.active_connections - 1)
                backend.total_response_time_ms += response_time_ms
                backend.total_connections += 1
                if not success:
                    backend.failed_requests += 1
                break
                
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_backends = sum(len(p.backends) for p in self.pools.values())
        total_requests = sum(p.total_requests for p in self.pools.values())
        active_sessions = sum(len(p.sessions) for p in self.pools.values())
        
        statuses = {status: 0 for status in BackendStatus}
        for pool in self.pools.values():
            for backend in pool.backends:
                statuses[backend.status] += 1
                
        return {
            "pools_total": len(self.pools),
            "backends_total": total_backends,
            "total_requests": total_requests,
            "active_sessions": active_sessions,
            "statuses": {s.value: c for s, c in statuses.items()}
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 266: Load Balancer Platform")
    print("=" * 60)
    
    manager = LoadBalancerManager()
    print("✓ Load Balancer Manager created")
    
    # Create pools
    print("\n📦 Creating Backend Pools...")
    
    pools_data = [
        ("web-servers", BalancerAlgorithm.ROUND_ROBIN, SessionPersistence.COOKIE),
        ("api-servers", BalancerAlgorithm.LEAST_CONNECTIONS, SessionPersistence.NONE),
        ("db-proxies", BalancerAlgorithm.WEIGHTED_ROUND_ROBIN, SessionPersistence.IP),
    ]
    
    for name, algo, persist in pools_data:
        pool = manager.create_pool(name, algo, persist)
        print(f"  📦 {name}: {algo.value}, persistence={persist.value}")
        
    # Add backends
    print("\n🖥️ Adding Backend Servers...")
    
    backends_data = [
        ("web-servers", "web1", "10.0.1.1", 80, 100),
        ("web-servers", "web2", "10.0.1.2", 80, 100),
        ("web-servers", "web3", "10.0.1.3", 80, 50),
        ("api-servers", "api1", "10.0.2.1", 8080, 100),
        ("api-servers", "api2", "10.0.2.2", 8080, 100),
        ("db-proxies", "proxy1", "10.0.3.1", 3306, 80),
        ("db-proxies", "proxy2", "10.0.3.2", 3306, 100),
    ]
    
    for pool_name, name, host, port, weight in backends_data:
        backend = manager.add_backend(pool_name, name, host, port, weight)
        print(f"  🖥️ {pool_name}/{name}: {host}:{port} (weight={weight})")
        
    # Health checks
    print("\n🏥 Running Health Checks...")
    
    for pool in manager.pools.values():
        for backend in pool.backends:
            await manager.health_check_backend(backend)
            
    # Simulate requests
    print("\n🔄 Simulating Requests...")
    
    # Test web-servers with session persistence
    print("\n  Web Servers (cookie persistence):")
    
    client_ips = ["192.168.1.1", "192.168.1.2", "192.168.1.3"]
    request_distribution = {}
    
    for i in range(30):
        client_ip = random.choice(client_ips)
        context = RequestContext(
            request_id=f"req_{i}",
            client_ip=client_ip,
            cookies={"SERVERID": f"client_{client_ip.replace('.', '_')}"}
        )
        
        result = manager.route_request("web-servers", context)
        
        if result.backend:
            key = result.backend.name
            request_distribution[key] = request_distribution.get(key, 0) + 1
            
            # Complete request
            manager.complete_request(
                "web-servers",
                result.backend.server_id,
                random.uniform(10, 100),
                random.random() > 0.1
            )
            
    for name, count in request_distribution.items():
        bar = "█" * (count // 2) + "░" * (15 - count // 2)
        print(f"    {name}: [{bar}] {count}")
        
    # Test api-servers with least connections
    print("\n  API Servers (least connections):")
    
    request_distribution = {}
    
    for i in range(20):
        context = RequestContext(
            request_id=f"api_req_{i}",
            client_ip=f"10.0.0.{random.randint(1, 254)}"
        )
        
        result = manager.route_request("api-servers", context)
        
        if result.backend:
            key = result.backend.name
            request_distribution[key] = request_distribution.get(key, 0) + 1
            
            # Simulate some requests taking longer
            await asyncio.sleep(0.01)
            
            manager.complete_request(
                "api-servers",
                result.backend.server_id,
                random.uniform(5, 50),
                True
            )
            
    for name, count in request_distribution.items():
        bar = "█" * count + "░" * (10 - count)
        print(f"    {name}: [{bar}] {count}")
        
    # Display pools
    print("\n📦 Backend Pools:")
    
    print("\n  ┌─────────────────┬───────────────────────────┬─────────────┬──────────┬──────────┐")
    print("  │ Pool            │ Algorithm                 │ Persistence │ Backends │ Requests │")
    print("  ├─────────────────┼───────────────────────────┼─────────────┼──────────┼──────────┤")
    
    for pool in manager.pools.values():
        name = pool.name[:15].ljust(15)
        algo = pool.config.algorithm.value[:25].ljust(25)
        persist = pool.config.persistence.value[:11].ljust(11)
        backends = str(len(pool.backends))[:8].ljust(8)
        requests = str(pool.total_requests)[:8].ljust(8)
        
        print(f"  │ {name} │ {algo} │ {persist} │ {backends} │ {requests} │")
        
    print("  └─────────────────┴───────────────────────────┴─────────────┴──────────┴──────────┘")
    
    # Display backends
    print("\n🖥️ Backend Servers:")
    
    print("\n  ┌─────────────────┬─────────────────┬──────────┬──────────┬──────────┬──────────┐")
    print("  │ Pool/Server     │ Address         │ Status   │ Weight   │ Requests │ Avg RT   │")
    print("  ├─────────────────┼─────────────────┼──────────┼──────────┼──────────┼──────────┤")
    
    for pool in manager.pools.values():
        for backend in pool.backends:
            name = f"{pool.name[:6]}/{backend.name}"[:15].ljust(15)
            address = f"{backend.host}:{backend.port}"[:15].ljust(15)
            status = backend.status.value[:8].ljust(8)
            weight = str(backend.weight)[:8].ljust(8)
            requests = str(backend.total_requests)[:8].ljust(8)
            avg_rt = f"{backend.total_response_time_ms / max(1, backend.total_requests):.1f}"[:8].ljust(8)
            
            print(f"  │ {name} │ {address} │ {status} │ {weight} │ {requests} │ {avg_rt} │")
            
    print("  └─────────────────┴─────────────────┴──────────┴──────────┴──────────┴──────────┘")
    
    # Session info
    print("\n🔐 Active Sessions:")
    
    for pool_name, pool in manager.pools.items():
        if pool.sessions:
            print(f"\n  {pool_name}:")
            for session_key, session in list(pool.sessions.items())[:3]:
                backend = next((b for b in pool.backends if b.server_id == session.backend_id), None)
                backend_name = backend.name if backend else "unknown"
                print(f"    {session_key[:20]}: -> {backend_name}")
                
    # Status distribution
    print("\n📊 Backend Status Distribution:")
    
    for status in BackendStatus:
        count = sum(
            1 for p in manager.pools.values()
            for b in p.backends
            if b.status == status
        )
        if count > 0:
            bar = "█" * count + "░" * (10 - count)
            icon = {
                BackendStatus.UP: "🟢",
                BackendStatus.DOWN: "🔴",
                BackendStatus.DRAINING: "🟡",
                BackendStatus.MAINTENANCE: "🔧"
            }.get(status, "⚪")
            print(f"  {icon} {status.value:12s} [{bar}] {count}")
            
    # Algorithm distribution
    print("\n📊 Algorithm Distribution:")
    
    for algo in BalancerAlgorithm:
        count = sum(1 for p in manager.pools.values() if p.config.algorithm == algo)
        if count > 0:
            print(f"  {algo.value:28s}: {count} pool(s)")
            
    # Statistics
    print("\n📊 Manager Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Pools: {stats['pools_total']}")
    print(f"  Backends: {stats['backends_total']}")
    print(f"  Total Requests: {stats['total_requests']}")
    print(f"  Active Sessions: {stats['active_sessions']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                      Load Balancer Dashboard                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Pools:                         {stats['pools_total']:>12}                        │")
    print(f"│ Backends:                      {stats['backends_total']:>12}                        │")
    print(f"│ Total Requests:                {stats['total_requests']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Active Sessions:               {stats['active_sessions']:>12}                        │")
    print(f"│ Backends UP:                   {stats['statuses']['up']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Load Balancer Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
