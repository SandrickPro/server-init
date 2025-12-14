#!/usr/bin/env python3
"""
Server Init - Iteration 271: Sidecar Proxy Manager
Менеджер sidecar-прокси

Функционал:
- Proxy Injection - внедрение прокси
- Configuration Management - управление конфигурацией
- Traffic Interception - перехват трафика
- Protocol Detection - обнаружение протоколов
- Health Probing - проверка здоровья
- Metrics Collection - сбор метрик
- Log Aggregation - агрегация логов
- Hot Reload - горячая перезагрузка
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid


class ProxyState(Enum):
    """Состояние прокси"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    DRAINING = "draining"
    STOPPED = "stopped"
    ERROR = "error"


class InjectionMode(Enum):
    """Режим внедрения"""
    AUTO = "auto"
    MANUAL = "manual"
    DISABLED = "disabled"


class ProtocolType(Enum):
    """Тип протокола"""
    HTTP = "http"
    HTTP2 = "http2"
    GRPC = "grpc"
    TCP = "tcp"
    MONGO = "mongo"
    REDIS = "redis"
    MYSQL = "mysql"


class TrafficDirection(Enum):
    """Направление трафика"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BOTH = "both"


@dataclass
class ListenerConfig:
    """Конфигурация слушателя"""
    listener_id: str
    name: str
    
    # Address
    address: str = "0.0.0.0"
    port: int = 15001
    
    # Direction
    direction: TrafficDirection = TrafficDirection.INBOUND
    
    # Protocol
    protocol: ProtocolType = ProtocolType.HTTP
    
    # TLS
    tls_enabled: bool = True
    
    # Stats
    connections: int = 0
    requests: int = 0


@dataclass
class ClusterConfig:
    """Конфигурация кластера"""
    cluster_id: str
    name: str
    
    # Type
    cluster_type: str = "eds"  # eds, static, strict_dns
    
    # Endpoints
    endpoints: List[str] = field(default_factory=list)
    
    # Load balancing
    lb_policy: str = "round_robin"
    
    # Health check
    health_check_path: str = "/health"
    health_check_interval_ms: int = 5000
    
    # Circuit breaker
    max_connections: int = 1000
    max_pending_requests: int = 100
    max_requests: int = 1000


@dataclass
class RouteConfig:
    """Конфигурация маршрута"""
    route_id: str
    name: str
    
    # Match
    match_prefix: str = "/"
    match_headers: Dict[str, str] = field(default_factory=dict)
    
    # Action
    cluster: str = ""
    timeout_ms: int = 15000
    
    # Retry
    retry_on: str = "5xx"
    num_retries: int = 3


@dataclass
class ProxyConfig:
    """Конфигурация прокси"""
    config_id: str
    version: str
    
    # Listeners
    listeners: List[ListenerConfig] = field(default_factory=list)
    
    # Clusters
    clusters: List[ClusterConfig] = field(default_factory=list)
    
    # Routes
    routes: List[RouteConfig] = field(default_factory=list)
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    applied_at: Optional[datetime] = None


@dataclass
class ProxyMetrics:
    """Метрики прокси"""
    metrics_id: str
    
    # Connections
    active_connections: int = 0
    total_connections: int = 0
    
    # Requests
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # Latency
    latency_p50_ms: float = 0
    latency_p95_ms: float = 0
    latency_p99_ms: float = 0
    
    # Bandwidth
    bytes_sent: int = 0
    bytes_received: int = 0
    
    # Timestamp
    collected_at: datetime = field(default_factory=datetime.now)


@dataclass
class SidecarProxy:
    """Sidecar прокси"""
    proxy_id: str
    name: str
    
    # Pod info
    pod_name: str = ""
    namespace: str = "default"
    
    # State
    state: ProxyState = ProxyState.INITIALIZING
    
    # Config
    config: Optional[ProxyConfig] = None
    config_version: str = ""
    
    # Ports
    inbound_port: int = 15006
    outbound_port: int = 15001
    admin_port: int = 15000
    stats_port: int = 15090
    
    # Metrics
    metrics: ProxyMetrics = field(default_factory=lambda: ProxyMetrics(
        metrics_id=f"metrics_{uuid.uuid4().hex[:8]}"
    ))
    
    # Connection
    last_heartbeat: datetime = field(default_factory=datetime.now)
    connected: bool = True
    
    # Timing
    started_at: datetime = field(default_factory=datetime.now)


@dataclass
class InjectionTemplate:
    """Шаблон внедрения"""
    template_id: str
    name: str
    
    # Mode
    mode: InjectionMode = InjectionMode.AUTO
    
    # Selector
    namespace_selector: str = "*"
    label_selector: Dict[str, str] = field(default_factory=dict)
    
    # Exclude
    exclude_namespaces: List[str] = field(default_factory=list)
    exclude_labels: Dict[str, str] = field(default_factory=dict)
    
    # Proxy config
    proxy_image: str = "envoy:latest"
    resources_cpu: str = "100m"
    resources_memory: str = "128Mi"
    
    # Active
    active: bool = True


@dataclass
class WorkloadProxy:
    """Прокси рабочей нагрузки"""
    workload_id: str
    workload_name: str
    
    # Type
    workload_type: str = "deployment"  # deployment, statefulset, daemonset
    
    # Namespace
    namespace: str = "default"
    
    # Proxies
    proxies: List[SidecarProxy] = field(default_factory=list)
    
    # Injection
    injection_status: str = "injected"
    injection_template: str = ""
    
    # Stats
    replicas: int = 0
    ready_proxies: int = 0


class SidecarProxyManager:
    """Менеджер sidecar-прокси"""
    
    def __init__(self):
        self.proxies: Dict[str, SidecarProxy] = {}
        self.workloads: Dict[str, WorkloadProxy] = {}
        self.templates: Dict[str, InjectionTemplate] = {}
        self.configs: Dict[str, ProxyConfig] = {}
        
    def create_injection_template(self, name: str,
                                  mode: InjectionMode = InjectionMode.AUTO,
                                  namespace_selector: str = "*") -> InjectionTemplate:
        """Создание шаблона внедрения"""
        template = InjectionTemplate(
            template_id=f"tmpl_{uuid.uuid4().hex[:8]}",
            name=name,
            mode=mode,
            namespace_selector=namespace_selector
        )
        
        self.templates[name] = template
        return template
        
    def create_proxy_config(self, version: str) -> ProxyConfig:
        """Создание конфигурации прокси"""
        config = ProxyConfig(
            config_id=f"cfg_{uuid.uuid4().hex[:8]}",
            version=version
        )
        
        self.configs[version] = config
        return config
        
    def add_listener(self, config_version: str,
                    name: str,
                    port: int,
                    direction: TrafficDirection,
                    protocol: ProtocolType = ProtocolType.HTTP) -> Optional[ListenerConfig]:
        """Добавление слушателя"""
        config = self.configs.get(config_version)
        if not config:
            return None
            
        listener = ListenerConfig(
            listener_id=f"listener_{uuid.uuid4().hex[:8]}",
            name=name,
            port=port,
            direction=direction,
            protocol=protocol
        )
        
        config.listeners.append(listener)
        return listener
        
    def add_cluster(self, config_version: str,
                   name: str,
                   endpoints: List[str],
                   lb_policy: str = "round_robin") -> Optional[ClusterConfig]:
        """Добавление кластера"""
        config = self.configs.get(config_version)
        if not config:
            return None
            
        cluster = ClusterConfig(
            cluster_id=f"cluster_{uuid.uuid4().hex[:8]}",
            name=name,
            endpoints=endpoints,
            lb_policy=lb_policy
        )
        
        config.clusters.append(cluster)
        return cluster
        
    def add_route(self, config_version: str,
                 name: str,
                 match_prefix: str,
                 cluster: str,
                 timeout_ms: int = 15000) -> Optional[RouteConfig]:
        """Добавление маршрута"""
        config = self.configs.get(config_version)
        if not config:
            return None
            
        route = RouteConfig(
            route_id=f"route_{uuid.uuid4().hex[:8]}",
            name=name,
            match_prefix=match_prefix,
            cluster=cluster,
            timeout_ms=timeout_ms
        )
        
        config.routes.append(route)
        return route
        
    def inject_proxy(self, workload_name: str,
                    workload_type: str,
                    namespace: str,
                    replicas: int,
                    template_name: str = "default") -> WorkloadProxy:
        """Внедрение прокси в рабочую нагрузку"""
        template = self.templates.get(template_name)
        
        workload = WorkloadProxy(
            workload_id=f"wl_{uuid.uuid4().hex[:8]}",
            workload_name=workload_name,
            workload_type=workload_type,
            namespace=namespace,
            replicas=replicas,
            injection_template=template_name
        )
        
        # Create proxy for each replica
        for i in range(replicas):
            proxy = SidecarProxy(
                proxy_id=f"proxy_{uuid.uuid4().hex[:8]}",
                name=f"{workload_name}-{i}-proxy",
                pod_name=f"{workload_name}-{uuid.uuid4().hex[:5]}",
                namespace=namespace,
                state=ProxyState.RUNNING
            )
            
            workload.proxies.append(proxy)
            self.proxies[proxy.proxy_id] = proxy
            
        workload.ready_proxies = replicas
        self.workloads[workload_name] = workload
        
        return workload
        
    async def apply_config(self, proxy_id: str,
                          config_version: str) -> bool:
        """Применение конфигурации"""
        proxy = self.proxies.get(proxy_id)
        config = self.configs.get(config_version)
        
        if not proxy or not config:
            return False
            
        # Simulate config application
        await asyncio.sleep(random.uniform(0.01, 0.05))
        
        proxy.config = config
        proxy.config_version = config_version
        config.applied_at = datetime.now()
        
        return True
        
    async def apply_config_to_workload(self, workload_name: str,
                                       config_version: str) -> int:
        """Применение конфигурации к рабочей нагрузке"""
        workload = self.workloads.get(workload_name)
        if not workload:
            return 0
            
        applied = 0
        for proxy in workload.proxies:
            if await self.apply_config(proxy.proxy_id, config_version):
                applied += 1
                
        return applied
        
    async def hot_reload(self, proxy_id: str) -> bool:
        """Горячая перезагрузка"""
        proxy = self.proxies.get(proxy_id)
        if not proxy:
            return False
            
        # Simulate reload
        await asyncio.sleep(random.uniform(0.005, 0.02))
        
        proxy.last_heartbeat = datetime.now()
        
        return True
        
    def collect_metrics(self, proxy_id: str) -> Optional[ProxyMetrics]:
        """Сбор метрик"""
        proxy = self.proxies.get(proxy_id)
        if not proxy:
            return None
            
        # Simulate metrics
        proxy.metrics.total_requests += random.randint(10, 100)
        proxy.metrics.successful_requests += random.randint(9, 99)
        proxy.metrics.active_connections = random.randint(5, 50)
        proxy.metrics.latency_p50_ms = random.uniform(5, 20)
        proxy.metrics.latency_p95_ms = random.uniform(20, 100)
        proxy.metrics.latency_p99_ms = random.uniform(100, 500)
        proxy.metrics.bytes_sent += random.randint(1000, 10000)
        proxy.metrics.bytes_received += random.randint(1000, 10000)
        proxy.metrics.collected_at = datetime.now()
        
        return proxy.metrics
        
    def drain_proxy(self, proxy_id: str):
        """Осушение прокси"""
        proxy = self.proxies.get(proxy_id)
        if proxy:
            proxy.state = ProxyState.DRAINING
            
    def stop_proxy(self, proxy_id: str):
        """Остановка прокси"""
        proxy = self.proxies.get(proxy_id)
        if proxy:
            proxy.state = ProxyState.STOPPED
            proxy.connected = False
            
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_proxies = len(self.proxies)
        running = sum(1 for p in self.proxies.values() if p.state == ProxyState.RUNNING)
        
        total_requests = sum(p.metrics.total_requests for p in self.proxies.values())
        total_connections = sum(p.metrics.active_connections for p in self.proxies.values())
        
        return {
            "proxies_total": total_proxies,
            "proxies_running": running,
            "workloads_total": len(self.workloads),
            "templates_total": len(self.templates),
            "configs_total": len(self.configs),
            "total_requests": total_requests,
            "total_connections": total_connections
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 271: Sidecar Proxy Manager")
    print("=" * 60)
    
    manager = SidecarProxyManager()
    print("✓ Sidecar Proxy Manager created")
    
    # Create injection templates
    print("\n📋 Creating Injection Templates...")
    
    default_template = manager.create_injection_template(
        "default",
        InjectionMode.AUTO,
        "*"
    )
    default_template.exclude_namespaces = ["kube-system", "istio-system"]
    print(f"  📋 default: AUTO, exclude={default_template.exclude_namespaces}")
    
    strict_template = manager.create_injection_template(
        "strict",
        InjectionMode.AUTO,
        "production"
    )
    print(f"  📋 strict: AUTO, namespace=production")
    
    manual_template = manager.create_injection_template(
        "manual",
        InjectionMode.MANUAL,
        "*"
    )
    print(f"  📋 manual: MANUAL")
    
    # Create proxy config
    print("\n⚙️ Creating Proxy Configuration...")
    
    config = manager.create_proxy_config("v1.0.0")
    
    # Add listeners
    manager.add_listener("v1.0.0", "inbound-http", 15006, TrafficDirection.INBOUND, ProtocolType.HTTP)
    manager.add_listener("v1.0.0", "outbound-http", 15001, TrafficDirection.OUTBOUND, ProtocolType.HTTP)
    manager.add_listener("v1.0.0", "inbound-grpc", 15007, TrafficDirection.INBOUND, ProtocolType.GRPC)
    
    print(f"  Listeners: {len(config.listeners)}")
    for listener in config.listeners:
        print(f"    📡 {listener.name}: {listener.port} ({listener.direction.value})")
        
    # Add clusters
    manager.add_cluster("v1.0.0", "user-service", 
                       ["10.0.1.1:8080", "10.0.1.2:8080"])
    manager.add_cluster("v1.0.0", "order-service",
                       ["10.0.2.1:8080", "10.0.2.2:8080", "10.0.2.3:8080"])
    manager.add_cluster("v1.0.0", "payment-service",
                       ["10.0.3.1:8080"])
    
    print(f"\n  Clusters: {len(config.clusters)}")
    for cluster in config.clusters:
        print(f"    🎯 {cluster.name}: {len(cluster.endpoints)} endpoints")
        
    # Add routes
    manager.add_route("v1.0.0", "users-route", "/api/users", "user-service", 15000)
    manager.add_route("v1.0.0", "orders-route", "/api/orders", "order-service", 30000)
    manager.add_route("v1.0.0", "payments-route", "/api/payments", "payment-service", 60000)
    
    print(f"\n  Routes: {len(config.routes)}")
    for route in config.routes:
        print(f"    🛤️ {route.name}: {route.match_prefix} -> {route.cluster}")
        
    # Inject proxies
    print("\n💉 Injecting Sidecar Proxies...")
    
    workloads = [
        ("api-gateway", "deployment", "default", 3),
        ("user-service", "deployment", "default", 2),
        ("order-service", "deployment", "default", 3),
        ("payment-service", "deployment", "default", 2),
        ("notification-worker", "deployment", "default", 1),
    ]
    
    for name, wtype, ns, replicas in workloads:
        workload = manager.inject_proxy(name, wtype, ns, replicas, "default")
        print(f"  💉 {name}: {replicas} proxies injected")
        
    # Apply configuration
    print("\n⚙️ Applying Configuration...")
    
    for workload_name in ["api-gateway", "user-service", "order-service"]:
        applied = await manager.apply_config_to_workload(workload_name, "v1.0.0")
        print(f"  ✓ {workload_name}: {applied} proxies configured")
        
    # Collect metrics
    print("\n📊 Collecting Metrics...")
    
    for proxy_id, proxy in list(manager.proxies.items())[:5]:
        metrics = manager.collect_metrics(proxy_id)
        if metrics:
            print(f"  📊 {proxy.name}: {metrics.total_requests} requests, {metrics.active_connections} conns")
            
    # Display workloads
    print("\n📦 Workloads:")
    
    print("\n  ┌─────────────────────┬─────────────┬───────────┬──────────┬──────────┐")
    print("  │ Workload            │ Type        │ Namespace │ Replicas │ Ready    │")
    print("  ├─────────────────────┼─────────────┼───────────┼──────────┼──────────┤")
    
    for workload in manager.workloads.values():
        name = workload.workload_name[:19].ljust(19)
        wtype = workload.workload_type[:11].ljust(11)
        ns = workload.namespace[:9].ljust(9)
        replicas = str(workload.replicas)[:8].ljust(8)
        ready = str(workload.ready_proxies)[:8].ljust(8)
        
        print(f"  │ {name} │ {wtype} │ {ns} │ {replicas} │ {ready} │")
        
    print("  └─────────────────────┴─────────────┴───────────┴──────────┴──────────┘")
    
    # Display proxies
    print("\n🔲 Sidecar Proxies:")
    
    print("\n  ┌─────────────────────────────┬──────────────┬───────────┬─────────────────┐")
    print("  │ Proxy                       │ State        │ Version   │ Last Heartbeat  │")
    print("  ├─────────────────────────────┼──────────────┼───────────┼─────────────────┤")
    
    for proxy in list(manager.proxies.values())[:8]:
        name = proxy.name[:27].ljust(27)
        state = proxy.state.value[:12].ljust(12)
        version = (proxy.config_version or "N/A")[:9].ljust(9)
        heartbeat = proxy.last_heartbeat.strftime("%H:%M:%S")[:15].ljust(15)
        
        print(f"  │ {name} │ {state} │ {version} │ {heartbeat} │")
        
    print("  └─────────────────────────────┴──────────────┴───────────┴─────────────────┘")
    
    # Proxy ports
    print("\n🔌 Proxy Ports (first proxy):")
    
    first_proxy = list(manager.proxies.values())[0]
    print(f"  Inbound:  {first_proxy.inbound_port}")
    print(f"  Outbound: {first_proxy.outbound_port}")
    print(f"  Admin:    {first_proxy.admin_port}")
    print(f"  Stats:    {first_proxy.stats_port}")
    
    # Config details
    print("\n📋 Configuration Details:")
    
    print(f"\n  Version: {config.version}")
    print(f"  Listeners: {len(config.listeners)}")
    print(f"  Clusters: {len(config.clusters)}")
    print(f"  Routes: {len(config.routes)}")
    
    # Protocol distribution
    print("\n📊 Protocol Distribution:")
    
    protocol_counts = {}
    for listener in config.listeners:
        protocol_counts[listener.protocol] = protocol_counts.get(listener.protocol, 0) + 1
        
    for protocol, count in protocol_counts.items():
        bar = "█" * count + "░" * (5 - count)
        print(f"  {protocol.value:8s}: [{bar}] {count}")
        
    # Proxy state distribution
    print("\n📊 Proxy State Distribution:")
    
    state_counts = {}
    for proxy in manager.proxies.values():
        state_counts[proxy.state] = state_counts.get(proxy.state, 0) + 1
        
    for state, count in state_counts.items():
        icon = {
            ProxyState.RUNNING: "🟢",
            ProxyState.DRAINING: "🟡",
            ProxyState.STOPPED: "🔴",
            ProxyState.ERROR: "❌"
        }.get(state, "⚪")
        bar = "█" * count + "░" * (15 - count)
        print(f"  {icon} {state.value:12s}: [{bar}] {count}")
        
    # Metrics summary
    print("\n📊 Metrics Summary:")
    
    total_requests = sum(p.metrics.total_requests for p in manager.proxies.values())
    total_bytes_sent = sum(p.metrics.bytes_sent for p in manager.proxies.values())
    avg_latency = sum(p.metrics.latency_p50_ms for p in manager.proxies.values()) / max(1, len(manager.proxies))
    
    print(f"\n  Total Requests: {total_requests:,}")
    print(f"  Total Bytes Sent: {total_bytes_sent:,} bytes")
    print(f"  Average Latency P50: {avg_latency:.2f}ms")
    
    # Injection templates
    print("\n📋 Injection Templates:")
    
    for template in manager.templates.values():
        mode_icon = {
            InjectionMode.AUTO: "🤖",
            InjectionMode.MANUAL: "👤",
            InjectionMode.DISABLED: "❌"
        }.get(template.mode, "❓")
        
        print(f"  {mode_icon} {template.name}: {template.mode.value}, ns={template.namespace_selector}")
        
    # Statistics
    print("\n📊 Manager Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Proxies Total: {stats['proxies_total']}")
    print(f"  Proxies Running: {stats['proxies_running']}")
    print(f"  Workloads: {stats['workloads_total']}")
    print(f"  Templates: {stats['templates_total']}")
    print(f"  Configs: {stats['configs_total']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                     Sidecar Proxy Dashboard                         │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Proxies:                 {stats['proxies_total']:>12}                        │")
    print(f"│ Running Proxies:               {stats['proxies_running']:>12}                        │")
    print(f"│ Workloads:                     {stats['workloads_total']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Requests:                {stats['total_requests']:>12}                        │")
    print(f"│ Active Connections:            {stats['total_connections']:>12}                        │")
    print(f"│ Config Versions:               {stats['configs_total']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Sidecar Proxy Manager initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
