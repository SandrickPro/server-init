#!/usr/bin/env python3
"""
Server Init - Iteration 291: Container Monitoring Platform
Платформа Container Monitoring

Функционал:
- Container Discovery - обнаружение контейнеров
- Resource Monitoring - мониторинг ресурсов
- Log Collection - сбор логов
- Event Tracking - отслеживание событий
- Health Checking - проверка здоровья
- Performance Analysis - анализ производительности
- Alert Management - управление алертами
- Cluster Overview - обзор кластера
"""

import asyncio
import random
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid


class ContainerState(Enum):
    """Состояние контейнера"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    RESTARTING = "restarting"
    REMOVING = "removing"
    EXITED = "exited"
    DEAD = "dead"


class HealthStatus(Enum):
    """Статус здоровья"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    NONE = "none"


class EventType(Enum):
    """Тип события"""
    CREATE = "create"
    START = "start"
    STOP = "stop"
    RESTART = "restart"
    KILL = "kill"
    DIE = "die"
    OOM = "oom"
    HEALTH_STATUS = "health_status"


class AlertLevel(Enum):
    """Уровень алерта"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ResourceUsage:
    """Использование ресурсов"""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # CPU
    cpu_percent: float = 0.0
    cpu_cores: float = 0.0
    
    # Memory
    memory_bytes: int = 0
    memory_limit: int = 0
    memory_percent: float = 0.0
    
    # Network
    network_rx_bytes: int = 0
    network_tx_bytes: int = 0
    
    # Disk
    disk_read_bytes: int = 0
    disk_write_bytes: int = 0
    
    # PIDs
    pids: int = 0


@dataclass
class ContainerLog:
    """Лог контейнера"""
    timestamp: datetime
    stream: str = "stdout"
    message: str = ""


@dataclass
class ContainerEvent:
    """Событие контейнера"""
    event_id: str
    container_id: str
    
    event_type: EventType = EventType.CREATE
    
    timestamp: datetime = field(default_factory=datetime.now)
    
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Container:
    """Контейнер"""
    container_id: str
    name: str
    
    # Image
    image: str = ""
    image_id: str = ""
    
    # State
    state: ContainerState = ContainerState.CREATED
    health: HealthStatus = HealthStatus.NONE
    
    # Resources
    cpu_limit: float = 0.0
    memory_limit: int = 0
    
    # Network
    ip_address: str = ""
    ports: Dict[str, str] = field(default_factory=dict)
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Environment
    environment: Dict[str, str] = field(default_factory=dict)
    
    # Metrics
    resource_history: List[ResourceUsage] = field(default_factory=list)
    
    # Logs
    logs: List[ContainerLog] = field(default_factory=list)
    
    # Events
    events: List[ContainerEvent] = field(default_factory=list)
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    
    # Stats
    restart_count: int = 0
    exit_code: Optional[int] = None


@dataclass
class ContainerAlert:
    """Алерт контейнера"""
    alert_id: str
    container_id: str
    
    level: AlertLevel = AlertLevel.WARNING
    
    alert_type: str = ""
    message: str = ""
    
    metric_name: str = ""
    current_value: float = 0.0
    threshold: float = 0.0
    
    acknowledged: bool = False
    resolved: bool = False
    
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Namespace:
    """Namespace/Project"""
    namespace_id: str
    name: str
    
    containers: Dict[str, Container] = field(default_factory=dict)
    
    labels: Dict[str, str] = field(default_factory=dict)


class ContainerMonitoringManager:
    """Менеджер Container Monitoring"""
    
    def __init__(self):
        self.namespaces: Dict[str, Namespace] = {}
        self.containers: Dict[str, Container] = {}
        self.alerts: List[ContainerAlert] = []
        
        # Thresholds
        self.cpu_threshold: float = 80.0
        self.memory_threshold: float = 85.0
        self.restart_threshold: int = 5
        
        # Stats
        self.total_events: int = 0
        self.total_logs: int = 0
        
    async def create_namespace(self, name: str,
                              labels: Dict[str, str] = None) -> Namespace:
        """Создание namespace"""
        ns = Namespace(
            namespace_id=f"ns_{uuid.uuid4().hex[:8]}",
            name=name,
            labels=labels or {}
        )
        
        self.namespaces[name] = ns
        return ns
        
    async def discover_container(self, name: str,
                                image: str,
                                namespace: str = "default",
                                labels: Dict[str, str] = None,
                                cpu_limit: float = 1.0,
                                memory_limit: int = 536870912) -> Container:
        """Обнаружение контейнера"""
        # Ensure namespace exists
        if namespace not in self.namespaces:
            await self.create_namespace(namespace)
            
        container = Container(
            container_id=f"{uuid.uuid4().hex[:12]}",
            name=name,
            image=image,
            image_id=f"sha256:{uuid.uuid4().hex[:12]}",
            labels=labels or {},
            cpu_limit=cpu_limit,
            memory_limit=memory_limit,
            ip_address=f"172.17.0.{random.randint(2, 254)}"
        )
        
        self.containers[container.container_id] = container
        self.namespaces[namespace].containers[container.container_id] = container
        
        # Generate create event
        await self._record_event(container.container_id, EventType.CREATE)
        
        return container
        
    async def start_container(self, container_id: str) -> bool:
        """Запуск контейнера"""
        container = self.containers.get(container_id)
        if not container:
            return False
            
        container.state = ContainerState.RUNNING
        container.started_at = datetime.now()
        container.health = HealthStatus.STARTING
        
        await self._record_event(container_id, EventType.START)
        
        # Simulate health check
        await asyncio.sleep(0.1)
        container.health = HealthStatus.HEALTHY
        
        return True
        
    async def stop_container(self, container_id: str) -> bool:
        """Остановка контейнера"""
        container = self.containers.get(container_id)
        if not container:
            return False
            
        container.state = ContainerState.EXITED
        container.finished_at = datetime.now()
        container.exit_code = 0
        
        await self._record_event(container_id, EventType.STOP)
        
        return True
        
    async def restart_container(self, container_id: str) -> bool:
        """Перезапуск контейнера"""
        container = self.containers.get(container_id)
        if not container:
            return False
            
        container.restart_count += 1
        container.state = ContainerState.RESTARTING
        
        await self._record_event(container_id, EventType.RESTART)
        
        await asyncio.sleep(0.1)
        container.state = ContainerState.RUNNING
        container.started_at = datetime.now()
        
        # Check restart threshold
        if container.restart_count >= self.restart_threshold:
            await self._create_alert(
                container_id,
                AlertLevel.WARNING,
                "high_restart_count",
                f"Container {container.name} has restarted {container.restart_count} times",
                "restart_count",
                container.restart_count,
                self.restart_threshold
            )
            
        return True
        
    async def collect_metrics(self, container_id: str) -> Optional[ResourceUsage]:
        """Сбор метрик"""
        container = self.containers.get(container_id)
        if not container:
            return None
            
        if container.state != ContainerState.RUNNING:
            return None
            
        # Simulate metrics collection
        cpu_percent = random.uniform(5, 95)
        memory_bytes = int(container.memory_limit * random.uniform(0.2, 0.9))
        
        usage = ResourceUsage(
            cpu_percent=cpu_percent,
            cpu_cores=cpu_percent / 100 * container.cpu_limit,
            memory_bytes=memory_bytes,
            memory_limit=container.memory_limit,
            memory_percent=(memory_bytes / container.memory_limit * 100) if container.memory_limit > 0 else 0,
            network_rx_bytes=random.randint(10000, 10000000),
            network_tx_bytes=random.randint(5000, 5000000),
            disk_read_bytes=random.randint(1000, 1000000),
            disk_write_bytes=random.randint(500, 500000),
            pids=random.randint(1, 50)
        )
        
        container.resource_history.append(usage)
        
        # Keep only last 100 metrics
        if len(container.resource_history) > 100:
            container.resource_history = container.resource_history[-100:]
            
        # Check thresholds
        await self._check_resource_thresholds(container, usage)
        
        return usage
        
    async def collect_logs(self, container_id: str,
                          tail: int = 100) -> List[ContainerLog]:
        """Сбор логов"""
        container = self.containers.get(container_id)
        if not container:
            return []
            
        # Simulate log generation
        log_messages = [
            "Application started successfully",
            "Processing request...",
            "Connection established",
            "Data received",
            "Task completed",
            "Warning: High memory usage",
            "Health check passed"
        ]
        
        new_logs = []
        for i in range(random.randint(1, 5)):
            log = ContainerLog(
                timestamp=datetime.now(),
                stream=random.choice(["stdout", "stderr"]),
                message=random.choice(log_messages)
            )
            new_logs.append(log)
            container.logs.append(log)
            self.total_logs += 1
            
        # Keep only last 1000 logs
        if len(container.logs) > 1000:
            container.logs = container.logs[-1000:]
            
        return container.logs[-tail:]
        
    async def _record_event(self, container_id: str,
                           event_type: EventType,
                           details: Dict[str, Any] = None):
        """Запись события"""
        container = self.containers.get(container_id)
        if not container:
            return
            
        event = ContainerEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            container_id=container_id,
            event_type=event_type,
            details=details or {}
        )
        
        container.events.append(event)
        self.total_events += 1
        
        # Keep only last 100 events
        if len(container.events) > 100:
            container.events = container.events[-100:]
            
    async def _check_resource_thresholds(self, container: Container,
                                        usage: ResourceUsage):
        """Проверка порогов ресурсов"""
        # CPU threshold
        if usage.cpu_percent > self.cpu_threshold:
            await self._create_alert(
                container.container_id,
                AlertLevel.WARNING,
                "high_cpu",
                f"Container {container.name} CPU usage is {usage.cpu_percent:.1f}%",
                "cpu_percent",
                usage.cpu_percent,
                self.cpu_threshold
            )
            
        # Memory threshold
        if usage.memory_percent > self.memory_threshold:
            await self._create_alert(
                container.container_id,
                AlertLevel.ERROR,
                "high_memory",
                f"Container {container.name} memory usage is {usage.memory_percent:.1f}%",
                "memory_percent",
                usage.memory_percent,
                self.memory_threshold
            )
            
    async def _create_alert(self, container_id: str,
                           level: AlertLevel,
                           alert_type: str,
                           message: str,
                           metric_name: str,
                           current_value: float,
                           threshold: float):
        """Создание алерта"""
        # Check for duplicate
        for alert in self.alerts:
            if (alert.container_id == container_id and
                alert.alert_type == alert_type and
                not alert.resolved):
                return
                
        alert = ContainerAlert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            container_id=container_id,
            level=level,
            alert_type=alert_type,
            message=message,
            metric_name=metric_name,
            current_value=current_value,
            threshold=threshold
        )
        
        self.alerts.append(alert)
        
        # Keep only last 1000 alerts
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
            
    async def run_health_checks(self):
        """Запуск проверок здоровья"""
        for container in self.containers.values():
            if container.state == ContainerState.RUNNING:
                # Simulate health check
                if random.random() < 0.95:
                    container.health = HealthStatus.HEALTHY
                else:
                    container.health = HealthStatus.UNHEALTHY
                    await self._record_event(
                        container.container_id,
                        EventType.HEALTH_STATUS,
                        {"status": "unhealthy"}
                    )
                    
    def get_container_stats(self, container_id: str) -> Dict[str, Any]:
        """Статистика контейнера"""
        container = self.containers.get(container_id)
        if not container:
            return {}
            
        stats = {
            "name": container.name,
            "state": container.state.value,
            "health": container.health.value,
            "restart_count": container.restart_count,
            "events": len(container.events),
            "logs": len(container.logs)
        }
        
        if container.resource_history:
            latest = container.resource_history[-1]
            stats["cpu_percent"] = latest.cpu_percent
            stats["memory_percent"] = latest.memory_percent
            stats["network_rx"] = latest.network_rx_bytes
            stats["network_tx"] = latest.network_tx_bytes
            
        return stats
        
    def get_namespace_summary(self, namespace: str) -> Dict[str, Any]:
        """Сводка по namespace"""
        ns = self.namespaces.get(namespace)
        if not ns:
            return {}
            
        total = len(ns.containers)
        running = sum(1 for c in ns.containers.values() 
                     if c.state == ContainerState.RUNNING)
        healthy = sum(1 for c in ns.containers.values()
                     if c.health == HealthStatus.HEALTHY)
                     
        return {
            "name": namespace,
            "total_containers": total,
            "running": running,
            "healthy": healthy,
            "stopped": total - running
        }
        
    def get_active_alerts(self) -> List[ContainerAlert]:
        """Активные алерты"""
        return [a for a in self.alerts if not a.resolved]
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_containers = len(self.containers)
        running = sum(1 for c in self.containers.values()
                     if c.state == ContainerState.RUNNING)
        healthy = sum(1 for c in self.containers.values()
                     if c.health == HealthStatus.HEALTHY)
        active_alerts = len(self.get_active_alerts())
        
        return {
            "namespaces": len(self.namespaces),
            "total_containers": total_containers,
            "running_containers": running,
            "healthy_containers": healthy,
            "active_alerts": active_alerts,
            "total_events": self.total_events,
            "total_logs": self.total_logs
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 291: Container Monitoring Platform")
    print("=" * 60)
    
    manager = ContainerMonitoringManager()
    print("✓ Container Monitoring Manager created")
    
    # Create namespaces
    print("\n📁 Creating Namespaces...")
    
    await manager.create_namespace("production", {"env": "prod"})
    await manager.create_namespace("staging", {"env": "staging"})
    await manager.create_namespace("development", {"env": "dev"})
    print("  📁 Created: production, staging, development")
    
    # Discover containers
    print("\n🐳 Discovering Containers...")
    
    # Production containers
    prod_containers = [
        ("web-frontend", "nginx:1.21", 2.0, 1073741824),
        ("api-server", "node:18-alpine", 4.0, 2147483648),
        ("auth-service", "python:3.11-slim", 1.0, 536870912),
        ("worker", "python:3.11-slim", 2.0, 1073741824),
        ("redis-cache", "redis:7-alpine", 1.0, 536870912),
        ("postgres-db", "postgres:15", 4.0, 4294967296)
    ]
    
    for name, image, cpu, mem in prod_containers:
        container = await manager.discover_container(
            name, image, "production",
            labels={"app": name, "env": "prod"},
            cpu_limit=cpu, memory_limit=mem
        )
        await manager.start_container(container.container_id)
        print(f"  🐳 {name}: {image} (started)")
        
    # Staging containers
    staging_containers = [
        ("web-frontend-stg", "nginx:1.21", 1.0, 536870912),
        ("api-server-stg", "node:18-alpine", 2.0, 1073741824)
    ]
    
    for name, image, cpu, mem in staging_containers:
        container = await manager.discover_container(
            name, image, "staging",
            cpu_limit=cpu, memory_limit=mem
        )
        await manager.start_container(container.container_id)
        print(f"  🐳 {name}: {image}")
        
    # Collect metrics
    print("\n📊 Collecting Metrics...")
    
    for container in manager.containers.values():
        if container.state == ContainerState.RUNNING:
            await manager.collect_metrics(container.container_id)
            
    print(f"  📊 Collected metrics for {len(manager.containers)} containers")
    
    # Collect logs
    print("\n📝 Collecting Logs...")
    
    for container in list(manager.containers.values())[:3]:
        logs = await manager.collect_logs(container.container_id, tail=5)
        print(f"  📝 {container.name}: {len(logs)} log entries")
        
    # Simulate restart
    print("\n🔄 Simulating Container Restart...")
    
    first_container = list(manager.containers.values())[0]
    for _ in range(3):
        await manager.restart_container(first_container.container_id)
    print(f"  🔄 {first_container.name}: restarted {first_container.restart_count} times")
    
    # Run health checks
    print("\n💚 Running Health Checks...")
    
    await manager.run_health_checks()
    
    healthy = sum(1 for c in manager.containers.values()
                 if c.health == HealthStatus.HEALTHY)
    print(f"  💚 Healthy containers: {healthy}/{len(manager.containers)}")
    
    # Container status
    print("\n📋 Container Status:")
    
    print("\n  ┌────────────────────────┬─────────────────────────┬────────────┬────────────┬────────────┐")
    print("  │ Container              │ Image                   │ State      │ Health     │ Restarts   │")
    print("  ├────────────────────────┼─────────────────────────┼────────────┼────────────┼────────────┤")
    
    for container in manager.containers.values():
        name = container.name[:22].ljust(22)
        image = container.image[:23].ljust(23)
        state_icon = "🟢" if container.state == ContainerState.RUNNING else "🔴"
        state = container.state.value[:10].ljust(10)
        health_icon = "💚" if container.health == HealthStatus.HEALTHY else "❤️"
        health = container.health.value[:10].ljust(10)
        restarts = str(container.restart_count).ljust(10)
        
        print(f"  │ {name} │ {image} │ {state_icon}{state[:9]} │ {health_icon}{health[:9]} │ {restarts} │")
        
    print("  └────────────────────────┴─────────────────────────┴────────────┴────────────┴────────────┘")
    
    # Resource usage
    print("\n📊 Resource Usage:")
    
    print("\n  ┌────────────────────────┬────────────┬────────────┬────────────────┬────────────────┐")
    print("  │ Container              │ CPU %      │ Memory %   │ Network RX     │ Network TX     │")
    print("  ├────────────────────────┼────────────┼────────────┼────────────────┼────────────────┤")
    
    for container in manager.containers.values():
        if container.resource_history:
            usage = container.resource_history[-1]
            name = container.name[:22].ljust(22)
            cpu = f"{usage.cpu_percent:.1f}%".ljust(10)
            mem = f"{usage.memory_percent:.1f}%".ljust(10)
            rx = f"{usage.network_rx_bytes/1024/1024:.1f}MB".ljust(14)
            tx = f"{usage.network_tx_bytes/1024/1024:.1f}MB".ljust(14)
            
            print(f"  │ {name} │ {cpu} │ {mem} │ {rx} │ {tx} │")
            
    print("  └────────────────────────┴────────────┴────────────┴────────────────┴────────────────┘")
    
    # Namespace summary
    print("\n📁 Namespace Summary:")
    
    for ns_name in manager.namespaces:
        summary = manager.get_namespace_summary(ns_name)
        running = summary['running']
        total = summary['total_containers']
        healthy = summary['healthy']
        
        print(f"\n  📁 {ns_name}:")
        print(f"    Total: {total} containers")
        print(f"    Running: {running}")
        print(f"    Healthy: {healthy}")
        
    # Container logs
    print("\n📝 Recent Logs (first container):")
    
    first_container = list(manager.containers.values())[0]
    logs = await manager.collect_logs(first_container.container_id, tail=5)
    
    for log in logs[-5:]:
        stream_icon = "📤" if log.stream == "stdout" else "📥"
        print(f"  {stream_icon} [{log.timestamp.strftime('%H:%M:%S')}] {log.message}")
        
    # Container events
    print("\n📋 Recent Events:")
    
    all_events = []
    for container in manager.containers.values():
        for event in container.events[-3:]:
            all_events.append((container.name, event))
            
    all_events.sort(key=lambda x: x[1].timestamp, reverse=True)
    
    for name, event in all_events[:10]:
        event_icons = {
            EventType.CREATE: "🆕",
            EventType.START: "▶️",
            EventType.STOP: "⏹️",
            EventType.RESTART: "🔄",
            EventType.DIE: "💀",
            EventType.OOM: "💥",
            EventType.HEALTH_STATUS: "💚"
        }
        icon = event_icons.get(event.event_type, "📋")
        print(f"  {icon} {name}: {event.event_type.value}")
        
    # Alerts
    print("\n🚨 Active Alerts:")
    
    alerts = manager.get_active_alerts()
    
    if alerts:
        for alert in alerts[:5]:
            level_icons = {
                AlertLevel.INFO: "ℹ️",
                AlertLevel.WARNING: "⚠️",
                AlertLevel.ERROR: "❌",
                AlertLevel.CRITICAL: "🔴"
            }
            icon = level_icons.get(alert.level, "❓")
            container = manager.containers.get(alert.container_id)
            name = container.name if container else "unknown"
            print(f"  {icon} [{alert.level.value}] {name}: {alert.message}")
    else:
        print("  ✅ No active alerts")
        
    # Statistics
    print("\n📊 Overall Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Namespaces: {stats['namespaces']}")
    print(f"  Total Containers: {stats['total_containers']}")
    print(f"  Running: {stats['running_containers']}")
    print(f"  Healthy: {stats['healthy_containers']}")
    print(f"\n  Active Alerts: {stats['active_alerts']}")
    print(f"  Total Events: {stats['total_events']}")
    print(f"  Total Logs: {stats['total_logs']}")
    
    running_rate = stats['running_containers'] / max(stats['total_containers'], 1) * 100
    health_rate = stats['healthy_containers'] / max(stats['running_containers'], 1) * 100
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Container Monitoring Dashboard                    │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Containers:              {stats['total_containers']:>12}                        │")
    print(f"│ Running Containers:            {stats['running_containers']:>12}                        │")
    print(f"│ Healthy Containers:            {stats['healthy_containers']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Running Rate:                  {running_rate:>11.1f}%                        │")
    print(f"│ Health Rate:                   {health_rate:>11.1f}%                        │")
    print(f"│ Active Alerts:                 {stats['active_alerts']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Container Monitoring Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
