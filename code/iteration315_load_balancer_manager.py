#!/usr/bin/env python3
"""
Server Init - Iteration 315: Load Balancer Manager Platform
Платформа управления балансировщиком нагрузки

Функционал:
- Backend Management - управление бэкендами
- Load Balancing Algorithms - алгоритмы балансировки
- Health Checks - проверки здоровья
- SSL/TLS Termination - SSL терминация
- Session Persistence - персистентность сессий
- Traffic Shaping - управление трафиком
- Monitoring - мониторинг
- Auto-scaling - автомасштабирование
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid
import hashlib


class LoadBalancingAlgorithm(Enum):
    """Алгоритм балансировки"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_LEAST_CONNECTIONS = "weighted_least_connections"
    IP_HASH = "ip_hash"
    RANDOM = "random"
    LEAST_RESPONSE_TIME = "least_response_time"


class HealthCheckType(Enum):
    """Тип проверки здоровья"""
    HTTP = "http"
    HTTPS = "https"
    TCP = "tcp"
    UDP = "udp"
    SCRIPT = "script"


class BackendStatus(Enum):
    """Статус бэкенда"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DRAINING = "draining"
    MAINTENANCE = "maintenance"


class SessionPersistence(Enum):
    """Тип персистентности сессий"""
    NONE = "none"
    SOURCE_IP = "source_ip"
    COOKIE = "cookie"
    HEADER = "header"


class SSLMode(Enum):
    """Режим SSL"""
    NONE = "none"
    TERMINATE = "terminate"
    PASSTHROUGH = "passthrough"
    REENCRYPT = "reencrypt"


@dataclass
class SSLCertificate:
    """SSL сертификат"""
    cert_id: str
    name: str
    
    # Certificate
    domain: str = ""
    issuer: str = ""
    
    # Validity
    valid_from: datetime = field(default_factory=datetime.now)
    valid_to: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=365))
    
    # Status
    is_active: bool = True


@dataclass
class HealthCheck:
    """Конфигурация проверки здоровья"""
    check_id: str
    
    # Type
    check_type: HealthCheckType = HealthCheckType.HTTP
    
    # Config
    path: str = "/health"
    port: int = 0  # 0 = same as backend
    
    # Timing
    interval_seconds: int = 30
    timeout_seconds: int = 5
    
    # Thresholds
    healthy_threshold: int = 2
    unhealthy_threshold: int = 3
    
    # Expected response
    expected_status: int = 200
    expected_body: str = ""


@dataclass
class Backend:
    """Бэкенд сервер"""
    backend_id: str
    name: str
    
    # Address
    host: str = ""
    port: int = 80
    
    # Weight
    weight: int = 1
    
    # Status
    status: BackendStatus = BackendStatus.HEALTHY
    
    # Connections
    active_connections: int = 0
    max_connections: int = 1000
    
    # Health
    health_check_id: str = ""
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_health_check: Optional[datetime] = None
    
    # Stats
    requests_count: int = 0
    bytes_in: int = 0
    bytes_out: int = 0
    avg_response_time_ms: float = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Pool:
    """Пул бэкендов"""
    pool_id: str
    name: str
    
    # Backends
    backends: List[str] = field(default_factory=list)  # backend_ids
    
    # Load balancing
    algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN
    
    # Session persistence
    persistence: SessionPersistence = SessionPersistence.NONE
    persistence_timeout_seconds: int = 1800
    
    # Health check
    health_check_id: str = ""
    
    # Current state
    _current_index: int = 0


@dataclass
class Listener:
    """Слушатель (frontend)"""
    listener_id: str
    name: str
    
    # Binding
    bind_address: str = "0.0.0.0"
    bind_port: int = 80
    protocol: str = "http"
    
    # SSL
    ssl_mode: SSLMode = SSLMode.NONE
    ssl_cert_id: str = ""
    
    # Default pool
    default_pool_id: str = ""
    
    # Rules
    rules: List[Dict[str, Any]] = field(default_factory=list)
    # e.g., [{"condition": "path_prefix:/api", "pool_id": "..."}]
    
    # Stats
    requests_count: int = 0
    connections_current: int = 0
    connections_total: int = 0


@dataclass
class VirtualServer:
    """Виртуальный сервер"""
    server_id: str
    name: str
    
    # Listeners
    listeners: List[str] = field(default_factory=list)  # listener_ids
    
    # Pools
    pools: List[str] = field(default_factory=list)  # pool_ids
    
    # Status
    is_enabled: bool = True
    
    # Stats
    total_requests: int = 0
    total_bytes: int = 0


@dataclass
class Connection:
    """Соединение"""
    connection_id: str
    listener_id: str
    backend_id: str
    
    # Client
    client_ip: str = ""
    client_port: int = 0
    
    # Session
    session_id: str = ""
    
    # Stats
    bytes_in: int = 0
    bytes_out: int = 0
    
    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    duration_ms: float = 0


class LoadBalancerManager:
    """Менеджер балансировщика нагрузки"""
    
    def __init__(self):
        self.certificates: Dict[str, SSLCertificate] = {}
        self.health_checks: Dict[str, HealthCheck] = {}
        self.backends: Dict[str, Backend] = {}
        self.pools: Dict[str, Pool] = {}
        self.listeners: Dict[str, Listener] = {}
        self.virtual_servers: Dict[str, VirtualServer] = {}
        self.connections: List[Connection] = []
        
        # Session store
        self._sessions: Dict[str, str] = {}  # session_key -> backend_id
        
    async def create_certificate(self, name: str,
                                domain: str,
                                issuer: str = "Let's Encrypt",
                                days_valid: int = 365) -> SSLCertificate:
        """Создание сертификата"""
        cert = SSLCertificate(
            cert_id=f"cert_{uuid.uuid4().hex[:8]}",
            name=name,
            domain=domain,
            issuer=issuer,
            valid_to=datetime.now() + timedelta(days=days_valid)
        )
        
        self.certificates[cert.cert_id] = cert
        return cert
        
    async def create_health_check(self, check_type: HealthCheckType = HealthCheckType.HTTP,
                                 path: str = "/health",
                                 interval: int = 30,
                                 timeout: int = 5) -> HealthCheck:
        """Создание проверки здоровья"""
        check = HealthCheck(
            check_id=f"hc_{uuid.uuid4().hex[:8]}",
            check_type=check_type,
            path=path,
            interval_seconds=interval,
            timeout_seconds=timeout
        )
        
        self.health_checks[check.check_id] = check
        return check
        
    async def create_backend(self, name: str,
                            host: str,
                            port: int = 80,
                            weight: int = 1,
                            health_check_id: str = "") -> Backend:
        """Создание бэкенда"""
        backend = Backend(
            backend_id=f"be_{uuid.uuid4().hex[:8]}",
            name=name,
            host=host,
            port=port,
            weight=weight,
            health_check_id=health_check_id
        )
        
        self.backends[backend.backend_id] = backend
        return backend
        
    async def create_pool(self, name: str,
                         algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN,
                         persistence: SessionPersistence = SessionPersistence.NONE,
                         health_check_id: str = "") -> Pool:
        """Создание пула"""
        pool = Pool(
            pool_id=f"pool_{uuid.uuid4().hex[:8]}",
            name=name,
            algorithm=algorithm,
            persistence=persistence,
            health_check_id=health_check_id
        )
        
        self.pools[pool.pool_id] = pool
        return pool
        
    async def add_backend_to_pool(self, pool_id: str, backend_id: str) -> bool:
        """Добавление бэкенда в пул"""
        pool = self.pools.get(pool_id)
        backend = self.backends.get(backend_id)
        
        if not pool or not backend:
            return False
            
        if backend_id not in pool.backends:
            pool.backends.append(backend_id)
            
        return True
        
    async def create_listener(self, name: str,
                             bind_port: int,
                             protocol: str = "http",
                             ssl_mode: SSLMode = SSLMode.NONE,
                             ssl_cert_id: str = "",
                             default_pool_id: str = "") -> Listener:
        """Создание слушателя"""
        listener = Listener(
            listener_id=f"lst_{uuid.uuid4().hex[:8]}",
            name=name,
            bind_port=bind_port,
            protocol=protocol,
            ssl_mode=ssl_mode,
            ssl_cert_id=ssl_cert_id,
            default_pool_id=default_pool_id
        )
        
        self.listeners[listener.listener_id] = listener
        return listener
        
    async def create_virtual_server(self, name: str) -> VirtualServer:
        """Создание виртуального сервера"""
        server = VirtualServer(
            server_id=f"vs_{uuid.uuid4().hex[:8]}",
            name=name
        )
        
        self.virtual_servers[server.server_id] = server
        return server
        
    async def add_listener_to_server(self, server_id: str, listener_id: str) -> bool:
        """Добавление слушателя к серверу"""
        server = self.virtual_servers.get(server_id)
        listener = self.listeners.get(listener_id)
        
        if not server or not listener:
            return False
            
        if listener_id not in server.listeners:
            server.listeners.append(listener_id)
            
        return True
        
    async def add_pool_to_server(self, server_id: str, pool_id: str) -> bool:
        """Добавление пула к серверу"""
        server = self.virtual_servers.get(server_id)
        pool = self.pools.get(pool_id)
        
        if not server or not pool:
            return False
            
        if pool_id not in server.pools:
            server.pools.append(pool_id)
            
        return True
        
    async def run_health_check(self, backend_id: str) -> bool:
        """Запуск проверки здоровья"""
        backend = self.backends.get(backend_id)
        if not backend:
            return False
            
        # Simulate health check
        await asyncio.sleep(random.uniform(0.01, 0.05))
        
        is_healthy = random.random() > 0.05  # 95% healthy
        
        if is_healthy:
            backend.consecutive_successes += 1
            backend.consecutive_failures = 0
            
            check = self.health_checks.get(backend.health_check_id)
            if check and backend.consecutive_successes >= check.healthy_threshold:
                backend.status = BackendStatus.HEALTHY
        else:
            backend.consecutive_failures += 1
            backend.consecutive_successes = 0
            
            check = self.health_checks.get(backend.health_check_id)
            if check and backend.consecutive_failures >= check.unhealthy_threshold:
                backend.status = BackendStatus.UNHEALTHY
                
        backend.last_health_check = datetime.now()
        
        return is_healthy
        
    async def run_health_checks(self):
        """Запуск всех проверок здоровья"""
        for backend in self.backends.values():
            await self.run_health_check(backend.backend_id)
            
    async def select_backend(self, pool_id: str,
                            client_ip: str = "",
                            session_key: str = "") -> Optional[Backend]:
        """Выбор бэкенда"""
        pool = self.pools.get(pool_id)
        if not pool:
            return None
            
        # Check session persistence
        if pool.persistence != SessionPersistence.NONE and session_key:
            persist_key = f"{pool_id}:{session_key}"
            if persist_key in self._sessions:
                backend_id = self._sessions[persist_key]
                backend = self.backends.get(backend_id)
                if backend and backend.status == BackendStatus.HEALTHY:
                    return backend
                    
        # Get healthy backends
        healthy_backends = [
            self.backends[bid] for bid in pool.backends
            if bid in self.backends and self.backends[bid].status == BackendStatus.HEALTHY
        ]
        
        if not healthy_backends:
            return None
            
        # Select based on algorithm
        selected = None
        
        if pool.algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
            selected = healthy_backends[pool._current_index % len(healthy_backends)]
            pool._current_index += 1
            
        elif pool.algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
            total_weight = sum(b.weight for b in healthy_backends)
            r = random.uniform(0, total_weight)
            current = 0
            for backend in healthy_backends:
                current += backend.weight
                if r <= current:
                    selected = backend
                    break
            if not selected:
                selected = healthy_backends[-1]
                
        elif pool.algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            selected = min(healthy_backends, key=lambda b: b.active_connections)
            
        elif pool.algorithm == LoadBalancingAlgorithm.WEIGHTED_LEAST_CONNECTIONS:
            selected = min(healthy_backends, 
                          key=lambda b: b.active_connections / max(b.weight, 1))
                          
        elif pool.algorithm == LoadBalancingAlgorithm.LEAST_RESPONSE_TIME:
            selected = min(healthy_backends, key=lambda b: b.avg_response_time_ms)
            
        elif pool.algorithm == LoadBalancingAlgorithm.IP_HASH:
            if client_ip:
                idx = int(hashlib.md5(client_ip.encode()).hexdigest(), 16) % len(healthy_backends)
                selected = healthy_backends[idx]
            else:
                selected = healthy_backends[0]
                
        elif pool.algorithm == LoadBalancingAlgorithm.RANDOM:
            selected = random.choice(healthy_backends)
            
        else:
            selected = healthy_backends[0]
            
        # Store session
        if pool.persistence != SessionPersistence.NONE and session_key and selected:
            persist_key = f"{pool_id}:{session_key}"
            self._sessions[persist_key] = selected.backend_id
            
        return selected
        
    async def handle_connection(self, listener_id: str,
                               client_ip: str,
                               client_port: int,
                               request_path: str = "/") -> Optional[Connection]:
        """Обработка соединения"""
        listener = self.listeners.get(listener_id)
        if not listener:
            return None
            
        # Find pool based on rules or default
        pool_id = listener.default_pool_id
        
        for rule in listener.rules:
            condition = rule.get("condition", "")
            if condition.startswith("path_prefix:"):
                prefix = condition.split(":")[1]
                if request_path.startswith(prefix):
                    pool_id = rule.get("pool_id", pool_id)
                    break
                    
        # Select backend
        session_key = client_ip if listener.default_pool_id else ""
        pool = self.pools.get(pool_id)
        
        backend = await self.select_backend(pool_id, client_ip, session_key)
        if not backend:
            return None
            
        # Create connection
        connection = Connection(
            connection_id=f"conn_{uuid.uuid4().hex[:8]}",
            listener_id=listener_id,
            backend_id=backend.backend_id,
            client_ip=client_ip,
            client_port=client_port,
            session_id=session_key
        )
        
        self.connections.append(connection)
        
        # Update stats
        listener.requests_count += 1
        listener.connections_total += 1
        listener.connections_current += 1
        
        backend.active_connections += 1
        backend.requests_count += 1
        
        # Simulate request
        await asyncio.sleep(random.uniform(0.01, 0.1))
        
        response_time = random.uniform(10, 200)
        bytes_in = random.randint(100, 5000)
        bytes_out = random.randint(1000, 50000)
        
        connection.bytes_in = bytes_in
        connection.bytes_out = bytes_out
        connection.duration_ms = response_time
        
        backend.bytes_in += bytes_in
        backend.bytes_out += bytes_out
        
        # Update average response time
        total_time = backend.avg_response_time_ms * (backend.requests_count - 1) + response_time
        backend.avg_response_time_ms = total_time / backend.requests_count
        
        # Close connection
        backend.active_connections = max(0, backend.active_connections - 1)
        listener.connections_current = max(0, listener.connections_current - 1)
        
        # Update virtual server stats
        for server in self.virtual_servers.values():
            if listener_id in server.listeners:
                server.total_requests += 1
                server.total_bytes += bytes_in + bytes_out
                break
                
        return connection
        
    async def drain_backend(self, backend_id: str) -> bool:
        """Вывод бэкенда из обслуживания"""
        backend = self.backends.get(backend_id)
        if not backend:
            return False
            
        backend.status = BackendStatus.DRAINING
        
        # Wait for connections to finish
        while backend.active_connections > 0:
            await asyncio.sleep(0.1)
            
        backend.status = BackendStatus.MAINTENANCE
        return True
        
    async def enable_backend(self, backend_id: str) -> bool:
        """Включение бэкенда"""
        backend = self.backends.get(backend_id)
        if not backend:
            return False
            
        backend.status = BackendStatus.HEALTHY
        backend.consecutive_failures = 0
        backend.consecutive_successes = 0
        
        return True
        
    def get_pool_status(self, pool_id: str) -> Dict[str, Any]:
        """Статус пула"""
        pool = self.pools.get(pool_id)
        if not pool:
            return {}
            
        backends_status = []
        total_connections = 0
        total_requests = 0
        
        for backend_id in pool.backends:
            backend = self.backends.get(backend_id)
            if backend:
                backends_status.append({
                    "backend_id": backend_id,
                    "name": backend.name,
                    "status": backend.status.value,
                    "weight": backend.weight,
                    "connections": backend.active_connections,
                    "requests": backend.requests_count,
                    "avg_response_ms": backend.avg_response_time_ms
                })
                total_connections += backend.active_connections
                total_requests += backend.requests_count
                
        healthy_count = sum(1 for b in backends_status if b["status"] == "healthy")
        
        return {
            "pool_id": pool_id,
            "name": pool.name,
            "algorithm": pool.algorithm.value,
            "persistence": pool.persistence.value,
            "backends_count": len(pool.backends),
            "backends_healthy": healthy_count,
            "backends": backends_status,
            "total_connections": total_connections,
            "total_requests": total_requests
        }
        
    def get_listener_status(self, listener_id: str) -> Dict[str, Any]:
        """Статус слушателя"""
        listener = self.listeners.get(listener_id)
        if not listener:
            return {}
            
        return {
            "listener_id": listener_id,
            "name": listener.name,
            "bind": f"{listener.bind_address}:{listener.bind_port}",
            "protocol": listener.protocol,
            "ssl_mode": listener.ssl_mode.value,
            "requests": listener.requests_count,
            "connections_current": listener.connections_current,
            "connections_total": listener.connections_total
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_backends = len(self.backends)
        healthy_backends = sum(1 for b in self.backends.values() if b.status == BackendStatus.HEALTHY)
        
        by_status = {}
        for b in self.backends.values():
            by_status[b.status.value] = by_status.get(b.status.value, 0) + 1
            
        by_algorithm = {}
        for p in self.pools.values():
            by_algorithm[p.algorithm.value] = by_algorithm.get(p.algorithm.value, 0) + 1
            
        total_requests = sum(l.requests_count for l in self.listeners.values())
        total_bytes = sum(b.bytes_in + b.bytes_out for b in self.backends.values())
        
        active_connections = sum(b.active_connections for b in self.backends.values())
        
        certs_active = sum(1 for c in self.certificates.values() if c.is_active)
        certs_expiring = sum(1 for c in self.certificates.values() 
                           if c.valid_to < datetime.now() + timedelta(days=30))
        
        return {
            "total_virtual_servers": len(self.virtual_servers),
            "total_listeners": len(self.listeners),
            "total_pools": len(self.pools),
            "total_backends": total_backends,
            "healthy_backends": healthy_backends,
            "by_backend_status": by_status,
            "by_algorithm": by_algorithm,
            "total_health_checks": len(self.health_checks),
            "total_certificates": len(self.certificates),
            "active_certificates": certs_active,
            "expiring_certificates": certs_expiring,
            "total_requests": total_requests,
            "total_bytes": total_bytes,
            "total_bytes_mb": total_bytes / (1024 * 1024),
            "active_connections": active_connections,
            "total_connections": len(self.connections)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 315: Load Balancer Manager Platform")
    print("=" * 60)
    
    lb = LoadBalancerManager()
    print("✓ Load Balancer Manager created")
    
    # Create certificates
    print("\n🔐 Creating SSL Certificates...")
    
    certs_data = [
        ("api.example.com", "api.example.com", "Let's Encrypt"),
        ("www.example.com", "*.example.com", "DigiCert"),
        ("admin.example.com", "admin.example.com", "Let's Encrypt")
    ]
    
    certs = []
    for name, domain, issuer in certs_data:
        cert = await lb.create_certificate(name, domain, issuer)
        certs.append(cert)
        print(f"  🔐 {name} ({issuer})")
        
    # Create health checks
    print("\n💚 Creating Health Checks...")
    
    health_checks_data = [
        (HealthCheckType.HTTP, "/health", 30, 5),
        (HealthCheckType.HTTP, "/api/health", 15, 3),
        (HealthCheckType.TCP, "", 10, 2)
    ]
    
    health_checks = []
    for h_type, path, interval, timeout in health_checks_data:
        check = await lb.create_health_check(h_type, path, interval, timeout)
        health_checks.append(check)
        print(f"  💚 {h_type.value} ({path or 'TCP'}) every {interval}s")
        
    # Create backends
    print("\n🖥️ Creating Backends...")
    
    backends_data = [
        ("Web Server 1", "web-1.local", 8080, 3),
        ("Web Server 2", "web-2.local", 8080, 3),
        ("Web Server 3", "web-3.local", 8080, 2),
        ("API Server 1", "api-1.local", 9000, 2),
        ("API Server 2", "api-2.local", 9000, 2),
        ("API Server 3", "api-3.local", 9000, 1),
        ("Static Server 1", "static-1.local", 80, 1),
        ("Static Server 2", "static-2.local", 80, 1)
    ]
    
    backends = []
    for name, host, port, weight in backends_data:
        hc_id = health_checks[0].check_id if "Web" in name else health_checks[1].check_id
        backend = await lb.create_backend(name, host, port, weight, hc_id)
        backends.append(backend)
        print(f"  🖥️ {name} ({host}:{port}) weight={weight}")
        
    # Create pools
    print("\n📦 Creating Pools...")
    
    pools_data = [
        ("Web Pool", LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN, SessionPersistence.COOKIE),
        ("API Pool", LoadBalancingAlgorithm.LEAST_CONNECTIONS, SessionPersistence.NONE),
        ("Static Pool", LoadBalancingAlgorithm.ROUND_ROBIN, SessionPersistence.NONE)
    ]
    
    pools = []
    for name, algo, persist in pools_data:
        pool = await lb.create_pool(name, algo, persist, health_checks[0].check_id)
        pools.append(pool)
        print(f"  📦 {name} ({algo.value})")
        
    # Add backends to pools
    for backend in backends[:3]:
        await lb.add_backend_to_pool(pools[0].pool_id, backend.backend_id)
    for backend in backends[3:6]:
        await lb.add_backend_to_pool(pools[1].pool_id, backend.backend_id)
    for backend in backends[6:]:
        await lb.add_backend_to_pool(pools[2].pool_id, backend.backend_id)
        
    # Create listeners
    print("\n👂 Creating Listeners...")
    
    listeners_data = [
        ("HTTP Listener", 80, "http", SSLMode.NONE, ""),
        ("HTTPS Listener", 443, "https", SSLMode.TERMINATE, certs[0].cert_id),
        ("API Listener", 8443, "https", SSLMode.TERMINATE, certs[0].cert_id)
    ]
    
    listeners = []
    for name, port, protocol, ssl_mode, cert_id in listeners_data:
        listener = await lb.create_listener(name, port, protocol, ssl_mode, cert_id, pools[0].pool_id)
        listeners.append(listener)
        print(f"  👂 {name} (:{port}) {ssl_mode.value}")
        
    # Add rules to listeners
    listeners[0].rules = [
        {"condition": "path_prefix:/api", "pool_id": pools[1].pool_id},
        {"condition": "path_prefix:/static", "pool_id": pools[2].pool_id}
    ]
    listeners[1].rules = listeners[0].rules.copy()
    listeners[2].default_pool_id = pools[1].pool_id
    
    # Create virtual servers
    print("\n🌐 Creating Virtual Servers...")
    
    vs = await lb.create_virtual_server("Main Load Balancer")
    
    for listener in listeners:
        await lb.add_listener_to_server(vs.server_id, listener.listener_id)
    for pool in pools:
        await lb.add_pool_to_server(vs.server_id, pool.pool_id)
        
    print(f"  🌐 {vs.name}")
    
    # Run health checks
    print("\n💚 Running Health Checks...")
    
    await lb.run_health_checks()
    
    healthy = sum(1 for b in backends if b.status == BackendStatus.HEALTHY)
    print(f"  ✓ Healthy: {healthy}/{len(backends)}")
    
    # Simulate connections
    print("\n📨 Simulating Connections...")
    
    for _ in range(200):
        listener = random.choice(listeners)
        client_ip = f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"
        client_port = random.randint(30000, 65000)
        
        paths = ["/", "/api/users", "/api/orders", "/static/js/app.js", "/about"]
        path = random.choice(paths)
        
        await lb.handle_connection(listener.listener_id, client_ip, client_port, path)
        
    total_requests = sum(l.requests_count for l in listeners)
    print(f"  ✓ Processed {total_requests} requests")
    
    # Pool status
    print("\n📦 Pool Status:")
    
    for pool in pools:
        status = lb.get_pool_status(pool.pool_id)
        
        print(f"\n  📦 {status['name']} ({status['algorithm']})")
        print(f"     Backends: {status['backends_healthy']}/{status['backends_count']} healthy")
        print(f"     Persistence: {status['persistence']}")
        print(f"     Total Requests: {status['total_requests']}")
        
        print("     Backends:")
        for be in status['backends']:
            health = "✓" if be['status'] == "healthy" else "✗"
            print(f"       [{health}] {be['name']}: {be['requests']} req, {be['avg_response_ms']:.1f}ms avg")
            
    # Listener status
    print("\n👂 Listener Status:")
    
    print("\n  ┌──────────────────────┬────────────────┬──────────────┬─────────────┬────────────────┐")
    print("  │ Listener             │ Bind           │ SSL          │ Requests    │ Connections    │")
    print("  ├──────────────────────┼────────────────┼──────────────┼─────────────┼────────────────┤")
    
    for listener in listeners:
        status = lb.get_listener_status(listener.listener_id)
        
        name = status['name'][:20].ljust(20)
        bind = status['bind'].ljust(14)
        ssl = status['ssl_mode'][:12].ljust(12)
        requests = str(status['requests']).ljust(11)
        conns = f"{status['connections_current']}/{status['connections_total']}".ljust(14)
        
        print(f"  │ {name} │ {bind} │ {ssl} │ {requests} │ {conns} │")
        
    print("  └──────────────────────┴────────────────┴──────────────┴─────────────┴────────────────┘")
    
    # Backend status
    print("\n🖥️ Backend Status:")
    
    print("\n  ┌────────────────────────┬────────────┬────────┬──────────┬───────────┬────────────────┐")
    print("  │ Backend                │ Status     │ Weight │ Requests │ Bytes     │ Avg Response   │")
    print("  ├────────────────────────┼────────────┼────────┼──────────┼───────────┼────────────────┤")
    
    for backend in backends:
        name = backend.name[:22].ljust(22)
        status = ("✓ " + backend.status.value[:8])[:10].ljust(10)
        weight = str(backend.weight).ljust(6)
        requests = str(backend.requests_count).ljust(8)
        total_bytes = backend.bytes_in + backend.bytes_out
        bytes_str = f"{total_bytes / 1024:.1f}KB".ljust(9)
        avg_resp = f"{backend.avg_response_time_ms:.1f}ms".ljust(14)
        
        print(f"  │ {name} │ {status} │ {weight} │ {requests} │ {bytes_str} │ {avg_resp} │")
        
    print("  └────────────────────────┴────────────┴────────┴──────────┴───────────┴────────────────┘")
    
    # Certificate status
    print("\n🔐 Certificate Status:")
    
    for cert in certs:
        days_left = (cert.valid_to - datetime.now()).days
        status = "✓" if days_left > 30 else "⚠" if days_left > 0 else "✗"
        
        print(f"  [{status}] {cert.name}")
        print(f"      Domain: {cert.domain} | Issuer: {cert.issuer}")
        print(f"      Valid until: {cert.valid_to.strftime('%Y-%m-%d')} ({days_left} days)")
        
    # Load distribution
    print("\n📊 Load Distribution:")
    
    for pool in pools:
        status = lb.get_pool_status(pool.pool_id)
        
        print(f"\n  {status['name']}:")
        total = status['total_requests']
        for be in status['backends']:
            if total > 0:
                pct = be['requests'] / total * 100
                bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
                print(f"    {be['name']:20} [{bar}] {pct:.1f}%")
                
    # Statistics
    print("\n📊 Load Balancer Statistics:")
    
    stats = lb.get_statistics()
    
    print(f"\n  Virtual Servers: {stats['total_virtual_servers']}")
    print(f"  Listeners: {stats['total_listeners']}")
    print(f"  Pools: {stats['total_pools']}")
    
    print(f"\n  Total Backends: {stats['total_backends']}")
    print(f"  Healthy: {stats['healthy_backends']}")
    print("  By Status:")
    for status_name, count in stats['by_backend_status'].items():
        print(f"    {status_name}: {count}")
        
    print(f"\n  Total Requests: {stats['total_requests']}")
    print(f"  Total Traffic: {stats['total_bytes_mb']:.2f} MB")
    print(f"  Active Connections: {stats['active_connections']}")
    
    print(f"\n  SSL Certificates: {stats['total_certificates']}")
    print(f"  Active: {stats['active_certificates']}")
    print(f"  Expiring Soon: {stats['expiring_certificates']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Load Balancer Manager Platform                    │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Backends:              {stats['total_backends']:>12}                          │")
    print(f"│ Healthy Backends:            {stats['healthy_backends']:>12}                          │")
    print(f"│ Total Requests:              {stats['total_requests']:>12}                          │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Traffic:               {stats['total_bytes_mb']:>10.2f} MB                        │")
    print(f"│ Active Connections:          {stats['active_connections']:>12}                          │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Load Balancer Manager Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
