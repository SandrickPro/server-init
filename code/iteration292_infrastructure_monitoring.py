#!/usr/bin/env python3
"""
Server Init - Iteration 292: Infrastructure Monitoring Platform
Платформа Infrastructure Monitoring

Функционал:
- Host Discovery - обнаружение хостов
- System Metrics - системные метрики
- Disk Monitoring - мониторинг дисков
- Process Monitoring - мониторинг процессов
- Service Status - статус сервисов
- Uptime Tracking - отслеживание аптайма
- Capacity Planning - планирование ёмкости
- Alert Management - управление алертами
"""

import asyncio
import random
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid


class HostStatus(Enum):
    """Статус хоста"""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"


class DiskType(Enum):
    """Тип диска"""
    SSD = "ssd"
    HDD = "hdd"
    NVME = "nvme"
    NETWORK = "network"


class ProcessState(Enum):
    """Состояние процесса"""
    RUNNING = "running"
    SLEEPING = "sleeping"
    STOPPED = "stopped"
    ZOMBIE = "zombie"


class ServiceStatus(Enum):
    """Статус сервиса"""
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"
    DISABLED = "disabled"


class AlertSeverity(Enum):
    """Серьёзность алерта"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class CPUMetrics:
    """Метрики CPU"""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Usage
    user_percent: float = 0.0
    system_percent: float = 0.0
    idle_percent: float = 0.0
    iowait_percent: float = 0.0
    
    # Total
    total_percent: float = 0.0
    
    # Cores
    per_core: List[float] = field(default_factory=list)
    
    # Load average
    load_1: float = 0.0
    load_5: float = 0.0
    load_15: float = 0.0


@dataclass
class MemoryMetrics:
    """Метрики памяти"""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # RAM
    total_bytes: int = 0
    used_bytes: int = 0
    free_bytes: int = 0
    available_bytes: int = 0
    cached_bytes: int = 0
    buffers_bytes: int = 0
    
    # Swap
    swap_total: int = 0
    swap_used: int = 0
    swap_free: int = 0
    
    # Percent
    used_percent: float = 0.0
    swap_percent: float = 0.0


@dataclass
class DiskMetrics:
    """Метрики диска"""
    mount_point: str
    device: str
    
    # Capacity
    total_bytes: int = 0
    used_bytes: int = 0
    free_bytes: int = 0
    used_percent: float = 0.0
    
    # Type
    disk_type: DiskType = DiskType.SSD
    filesystem: str = "ext4"
    
    # IO
    read_bytes: int = 0
    write_bytes: int = 0
    read_ops: int = 0
    write_ops: int = 0
    io_time_ms: int = 0


@dataclass
class NetworkInterface:
    """Сетевой интерфейс"""
    name: str
    
    # Addresses
    ip_address: str = ""
    mac_address: str = ""
    
    # Status
    is_up: bool = True
    speed_mbps: int = 1000
    
    # Traffic
    rx_bytes: int = 0
    tx_bytes: int = 0
    rx_packets: int = 0
    tx_packets: int = 0
    rx_errors: int = 0
    tx_errors: int = 0


@dataclass
class Process:
    """Процесс"""
    pid: int
    name: str
    
    # State
    state: ProcessState = ProcessState.RUNNING
    
    # Resources
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_rss: int = 0
    
    # User
    user: str = "root"
    
    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    
    # Command
    command: str = ""


@dataclass
class SystemService:
    """Системный сервис"""
    name: str
    
    # Status
    status: ServiceStatus = ServiceStatus.RUNNING
    
    # Config
    enabled: bool = True
    
    # PID
    pid: Optional[int] = None
    
    # Memory
    memory_bytes: int = 0
    
    # Timing
    uptime_seconds: int = 0


@dataclass
class Host:
    """Хост"""
    host_id: str
    hostname: str
    
    # Status
    status: HostStatus = HostStatus.UNKNOWN
    
    # System info
    os_name: str = ""
    os_version: str = ""
    kernel: str = ""
    arch: str = "x86_64"
    
    # Hardware
    cpu_cores: int = 0
    total_memory: int = 0
    
    # Network
    ip_addresses: List[str] = field(default_factory=list)
    network_interfaces: Dict[str, NetworkInterface] = field(default_factory=dict)
    
    # Disks
    disks: Dict[str, DiskMetrics] = field(default_factory=dict)
    
    # Metrics history
    cpu_history: List[CPUMetrics] = field(default_factory=list)
    memory_history: List[MemoryMetrics] = field(default_factory=list)
    
    # Processes
    processes: Dict[int, Process] = field(default_factory=dict)
    
    # Services
    services: Dict[str, SystemService] = field(default_factory=dict)
    
    # Uptime
    uptime_seconds: int = 0
    boot_time: datetime = field(default_factory=datetime.now)
    
    # Health
    health_score: float = 100.0
    
    # Tags
    tags: List[str] = field(default_factory=list)
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class InfraAlert:
    """Инфраструктурный алерт"""
    alert_id: str
    host_id: str
    
    severity: AlertSeverity = AlertSeverity.WARNING
    
    alert_type: str = ""
    message: str = ""
    
    metric_name: str = ""
    current_value: float = 0.0
    threshold: float = 0.0
    
    acknowledged: bool = False
    resolved: bool = False
    
    created_at: datetime = field(default_factory=datetime.now)


class InfrastructureMonitoringManager:
    """Менеджер Infrastructure Monitoring"""
    
    def __init__(self):
        self.hosts: Dict[str, Host] = {}
        self.alerts: List[InfraAlert] = []
        
        # Thresholds
        self.cpu_threshold: float = 80.0
        self.memory_threshold: float = 85.0
        self.disk_threshold: float = 90.0
        self.load_threshold: float = 4.0
        
        # Stats
        self.total_checks: int = 0
        self.failed_checks: int = 0
        
    async def discover_host(self, hostname: str,
                           ip_addresses: List[str],
                           os_name: str = "Linux",
                           os_version: str = "Ubuntu 22.04",
                           cpu_cores: int = 8,
                           total_memory: int = 17179869184,
                           tags: List[str] = None) -> Host:
        """Обнаружение хоста"""
        host = Host(
            host_id=f"host_{uuid.uuid4().hex[:8]}",
            hostname=hostname,
            os_name=os_name,
            os_version=os_version,
            kernel=f"{os_name.lower()}-5.15.0",
            cpu_cores=cpu_cores,
            total_memory=total_memory,
            ip_addresses=ip_addresses,
            boot_time=datetime.now() - timedelta(days=random.randint(1, 30)),
            tags=tags or []
        )
        
        # Calculate uptime
        host.uptime_seconds = int((datetime.now() - host.boot_time).total_seconds())
        
        # Initial status check
        await self._check_host_status(host)
        
        self.hosts[host.host_id] = host
        return host
        
    async def add_network_interface(self, host_id: str,
                                   name: str,
                                   ip_address: str = "",
                                   speed_mbps: int = 1000) -> Optional[NetworkInterface]:
        """Добавление сетевого интерфейса"""
        host = self.hosts.get(host_id)
        if not host:
            return None
            
        interface = NetworkInterface(
            name=name,
            ip_address=ip_address,
            mac_address=self._generate_mac(),
            speed_mbps=speed_mbps
        )
        
        host.network_interfaces[name] = interface
        return interface
        
    async def add_disk(self, host_id: str,
                      mount_point: str,
                      device: str,
                      total_bytes: int,
                      disk_type: DiskType = DiskType.SSD,
                      filesystem: str = "ext4") -> Optional[DiskMetrics]:
        """Добавление диска"""
        host = self.hosts.get(host_id)
        if not host:
            return None
            
        used_bytes = int(total_bytes * random.uniform(0.3, 0.8))
        
        disk = DiskMetrics(
            mount_point=mount_point,
            device=device,
            total_bytes=total_bytes,
            used_bytes=used_bytes,
            free_bytes=total_bytes - used_bytes,
            used_percent=used_bytes / total_bytes * 100,
            disk_type=disk_type,
            filesystem=filesystem
        )
        
        host.disks[mount_point] = disk
        return disk
        
    async def add_service(self, host_id: str,
                         name: str,
                         status: ServiceStatus = ServiceStatus.RUNNING,
                         enabled: bool = True) -> Optional[SystemService]:
        """Добавление сервиса"""
        host = self.hosts.get(host_id)
        if not host:
            return None
            
        service = SystemService(
            name=name,
            status=status,
            enabled=enabled,
            pid=random.randint(1000, 50000) if status == ServiceStatus.RUNNING else None,
            memory_bytes=random.randint(10000000, 500000000) if status == ServiceStatus.RUNNING else 0,
            uptime_seconds=random.randint(3600, 86400 * 7) if status == ServiceStatus.RUNNING else 0
        )
        
        host.services[name] = service
        return service
        
    async def collect_cpu_metrics(self, host_id: str) -> Optional[CPUMetrics]:
        """Сбор метрик CPU"""
        host = self.hosts.get(host_id)
        if not host or host.status == HostStatus.OFFLINE:
            return None
            
        self.total_checks += 1
        
        user = random.uniform(10, 60)
        system = random.uniform(5, 30)
        iowait = random.uniform(0, 10)
        idle = 100 - user - system - iowait
        
        metrics = CPUMetrics(
            user_percent=user,
            system_percent=system,
            idle_percent=idle,
            iowait_percent=iowait,
            total_percent=user + system + iowait,
            per_core=[random.uniform(10, 90) for _ in range(host.cpu_cores)],
            load_1=random.uniform(0.5, 5),
            load_5=random.uniform(0.5, 4),
            load_15=random.uniform(0.5, 3)
        )
        
        host.cpu_history.append(metrics)
        
        if len(host.cpu_history) > 100:
            host.cpu_history = host.cpu_history[-100:]
            
        # Check thresholds
        await self._check_cpu_thresholds(host, metrics)
        
        return metrics
        
    async def collect_memory_metrics(self, host_id: str) -> Optional[MemoryMetrics]:
        """Сбор метрик памяти"""
        host = self.hosts.get(host_id)
        if not host or host.status == HostStatus.OFFLINE:
            return None
            
        used_percent = random.uniform(30, 90)
        used_bytes = int(host.total_memory * used_percent / 100)
        free_bytes = host.total_memory - used_bytes
        
        metrics = MemoryMetrics(
            total_bytes=host.total_memory,
            used_bytes=used_bytes,
            free_bytes=free_bytes,
            available_bytes=int(free_bytes * 1.1),
            cached_bytes=int(used_bytes * 0.2),
            buffers_bytes=int(used_bytes * 0.05),
            swap_total=host.total_memory // 2,
            swap_used=random.randint(0, host.total_memory // 4),
            swap_free=host.total_memory // 2 - random.randint(0, host.total_memory // 4),
            used_percent=used_percent,
            swap_percent=random.uniform(0, 30)
        )
        
        host.memory_history.append(metrics)
        
        if len(host.memory_history) > 100:
            host.memory_history = host.memory_history[-100:]
            
        # Check thresholds
        await self._check_memory_thresholds(host, metrics)
        
        return metrics
        
    async def collect_disk_metrics(self, host_id: str) -> Dict[str, DiskMetrics]:
        """Сбор метрик дисков"""
        host = self.hosts.get(host_id)
        if not host or host.status == HostStatus.OFFLINE:
            return {}
            
        for mount, disk in host.disks.items():
            # Simulate IO
            disk.read_bytes += random.randint(100000, 10000000)
            disk.write_bytes += random.randint(50000, 5000000)
            disk.read_ops += random.randint(100, 10000)
            disk.write_ops += random.randint(50, 5000)
            disk.io_time_ms += random.randint(10, 1000)
            
            # Check threshold
            await self._check_disk_thresholds(host, disk)
            
        return host.disks
        
    async def collect_processes(self, host_id: str) -> Dict[int, Process]:
        """Сбор информации о процессах"""
        host = self.hosts.get(host_id)
        if not host or host.status == HostStatus.OFFLINE:
            return {}
            
        # Simulate process list
        process_list = [
            ("systemd", "root", "/sbin/init"),
            ("sshd", "root", "/usr/sbin/sshd"),
            ("nginx", "www-data", "nginx: worker process"),
            ("postgres", "postgres", "postgres: writer process"),
            ("python3", "app", "python3 app.py"),
            ("node", "app", "node server.js")
        ]
        
        for name, user, cmd in process_list:
            pid = random.randint(1000, 50000)
            process = Process(
                pid=pid,
                name=name,
                user=user,
                command=cmd,
                cpu_percent=random.uniform(0, 20),
                memory_percent=random.uniform(0.1, 10),
                memory_rss=random.randint(10000000, 500000000)
            )
            host.processes[pid] = process
            
        return host.processes
        
    async def _check_host_status(self, host: Host):
        """Проверка статуса хоста"""
        await asyncio.sleep(0.01)
        
        if random.random() < 0.95:
            host.status = HostStatus.ONLINE
        else:
            host.status = HostStatus.OFFLINE
            self.failed_checks += 1
            
    async def _check_cpu_thresholds(self, host: Host, metrics: CPUMetrics):
        """Проверка порогов CPU"""
        if metrics.total_percent > self.cpu_threshold:
            await self._create_alert(
                host.host_id,
                AlertSeverity.WARNING,
                "high_cpu",
                f"High CPU usage on {host.hostname}: {metrics.total_percent:.1f}%",
                "cpu_percent",
                metrics.total_percent,
                self.cpu_threshold
            )
            
        if metrics.load_1 > self.load_threshold * host.cpu_cores:
            await self._create_alert(
                host.host_id,
                AlertSeverity.WARNING,
                "high_load",
                f"High load average on {host.hostname}: {metrics.load_1:.2f}",
                "load_1",
                metrics.load_1,
                self.load_threshold * host.cpu_cores
            )
            
    async def _check_memory_thresholds(self, host: Host, metrics: MemoryMetrics):
        """Проверка порогов памяти"""
        if metrics.used_percent > self.memory_threshold:
            await self._create_alert(
                host.host_id,
                AlertSeverity.ERROR,
                "high_memory",
                f"High memory usage on {host.hostname}: {metrics.used_percent:.1f}%",
                "memory_percent",
                metrics.used_percent,
                self.memory_threshold
            )
            
    async def _check_disk_thresholds(self, host: Host, disk: DiskMetrics):
        """Проверка порогов диска"""
        if disk.used_percent > self.disk_threshold:
            await self._create_alert(
                host.host_id,
                AlertSeverity.CRITICAL,
                "high_disk",
                f"High disk usage on {host.hostname} ({disk.mount_point}): {disk.used_percent:.1f}%",
                "disk_percent",
                disk.used_percent,
                self.disk_threshold
            )
            
    async def _create_alert(self, host_id: str,
                           severity: AlertSeverity,
                           alert_type: str,
                           message: str,
                           metric_name: str,
                           current_value: float,
                           threshold: float):
        """Создание алерта"""
        # Check duplicate
        for alert in self.alerts:
            if (alert.host_id == host_id and
                alert.alert_type == alert_type and
                not alert.resolved):
                return
                
        alert = InfraAlert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            host_id=host_id,
            severity=severity,
            alert_type=alert_type,
            message=message,
            metric_name=metric_name,
            current_value=current_value,
            threshold=threshold
        )
        
        self.alerts.append(alert)
        
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
            
    def _calculate_health_score(self, host: Host) -> float:
        """Расчёт оценки здоровья"""
        score = 100.0
        
        if host.status != HostStatus.ONLINE:
            return 0.0
            
        if host.cpu_history:
            cpu = host.cpu_history[-1]
            if cpu.total_percent > self.cpu_threshold:
                score -= 20
                
        if host.memory_history:
            mem = host.memory_history[-1]
            if mem.used_percent > self.memory_threshold:
                score -= 25
                
        for disk in host.disks.values():
            if disk.used_percent > self.disk_threshold:
                score -= 15
                
        failed_services = sum(1 for s in host.services.values()
                             if s.status == ServiceStatus.FAILED)
        score -= failed_services * 10
        
        host.health_score = max(0, score)
        return host.health_score
        
    def _generate_mac(self) -> str:
        """Генерация MAC адреса"""
        return ":".join([f"{random.randint(0, 255):02x}" for _ in range(6)])
        
    def _format_bytes(self, bytes_val: int) -> str:
        """Форматирование байтов"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024:
                return f"{bytes_val:.1f}{unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f}PB"
        
    def get_active_alerts(self) -> List[InfraAlert]:
        """Активные алерты"""
        return [a for a in self.alerts if not a.resolved]
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_hosts = len(self.hosts)
        online = sum(1 for h in self.hosts.values() if h.status == HostStatus.ONLINE)
        active_alerts = len(self.get_active_alerts())
        
        total_cpu = sum(h.cpu_cores for h in self.hosts.values())
        total_memory = sum(h.total_memory for h in self.hosts.values())
        total_disk = sum(d.total_bytes for h in self.hosts.values() for d in h.disks.values())
        
        avg_health = (
            sum(self._calculate_health_score(h) for h in self.hosts.values()) / total_hosts
            if total_hosts else 0
        )
        
        return {
            "total_hosts": total_hosts,
            "online_hosts": online,
            "total_cpu_cores": total_cpu,
            "total_memory": total_memory,
            "total_disk": total_disk,
            "active_alerts": active_alerts,
            "avg_health_score": avg_health,
            "total_checks": self.total_checks,
            "failed_checks": self.failed_checks
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 292: Infrastructure Monitoring Platform")
    print("=" * 60)
    
    manager = InfrastructureMonitoringManager()
    print("✓ Infrastructure Monitoring Manager created")
    
    # Discover hosts
    print("\n🖥️ Discovering Hosts...")
    
    hosts_config = [
        ("web-server-01", ["10.0.1.10", "192.168.1.10"], "Ubuntu 22.04", 8, 17179869184),
        ("web-server-02", ["10.0.1.11"], "Ubuntu 22.04", 8, 17179869184),
        ("app-server-01", ["10.0.2.10"], "CentOS 8", 16, 34359738368),
        ("app-server-02", ["10.0.2.11"], "CentOS 8", 16, 34359738368),
        ("db-server-01", ["10.0.3.10"], "Ubuntu 20.04", 32, 68719476736),
        ("db-server-02", ["10.0.3.11"], "Ubuntu 20.04", 32, 68719476736),
        ("cache-server-01", ["10.0.4.10"], "Alpine Linux", 4, 8589934592)
    ]
    
    hosts = []
    for hostname, ips, os_ver, cores, mem in hosts_config:
        host = await manager.discover_host(
            hostname, ips, "Linux", os_ver, cores, mem,
            tags=["production"]
        )
        hosts.append(host)
        print(f"  🖥️ {hostname}: {os_ver}, {cores} cores, {manager._format_bytes(mem)} RAM")
        
    # Add network interfaces
    print("\n🌐 Adding Network Interfaces...")
    
    for host in hosts:
        await manager.add_network_interface(host.host_id, "eth0", host.ip_addresses[0], 1000)
        await manager.add_network_interface(host.host_id, "eth1", "", 10000)
        
    print(f"  🌐 Added interfaces to {len(hosts)} hosts")
    
    # Add disks
    print("\n💾 Adding Disks...")
    
    for host in hosts:
        await manager.add_disk(host.host_id, "/", "/dev/sda1", 107374182400, DiskType.SSD)
        await manager.add_disk(host.host_id, "/data", "/dev/sdb1", 536870912000, DiskType.SSD)
        
        if "db" in host.hostname:
            await manager.add_disk(host.host_id, "/backup", "/dev/sdc1", 1099511627776, DiskType.HDD)
            
    print(f"  💾 Added disks to {len(hosts)} hosts")
    
    # Add services
    print("\n⚙️ Adding Services...")
    
    common_services = ["sshd", "crond", "rsyslog"]
    
    for host in hosts:
        for svc in common_services:
            await manager.add_service(host.host_id, svc)
            
        if "web" in host.hostname:
            await manager.add_service(host.host_id, "nginx")
            await manager.add_service(host.host_id, "php-fpm")
            
        if "app" in host.hostname:
            await manager.add_service(host.host_id, "node")
            await manager.add_service(host.host_id, "pm2")
            
        if "db" in host.hostname:
            await manager.add_service(host.host_id, "postgresql")
            await manager.add_service(host.host_id, "pgbouncer")
            
        if "cache" in host.hostname:
            await manager.add_service(host.host_id, "redis")
            
    print(f"  ⚙️ Added services to {len(hosts)} hosts")
    
    # Collect metrics
    print("\n📊 Collecting Metrics...")
    
    for host in hosts:
        await manager.collect_cpu_metrics(host.host_id)
        await manager.collect_memory_metrics(host.host_id)
        await manager.collect_disk_metrics(host.host_id)
        await manager.collect_processes(host.host_id)
        
    print(f"  📊 Collected metrics from {len(hosts)} hosts")
    
    # Host status
    print("\n📋 Host Status:")
    
    print("\n  ┌────────────────────────┬─────────────────┬────────────┬────────────┬────────────┐")
    print("  │ Hostname               │ IP Address      │ OS         │ Status     │ Health     │")
    print("  ├────────────────────────┼─────────────────┼────────────┼────────────┼────────────┤")
    
    for host in hosts:
        manager._calculate_health_score(host)
        
        name = host.hostname[:22].ljust(22)
        ip = host.ip_addresses[0][:15].ljust(15)
        os = host.os_version[:10].ljust(10)
        status_icon = "🟢" if host.status == HostStatus.ONLINE else "🔴"
        status = host.status.value[:10].ljust(10)
        health = f"{host.health_score:.0f}%".ljust(10)
        
        print(f"  │ {name} │ {ip} │ {os} │ {status_icon}{status[:9]} │ {health} │")
        
    print("  └────────────────────────┴─────────────────┴────────────┴────────────┴────────────┘")
    
    # CPU metrics
    print("\n🔥 CPU Metrics:")
    
    for host in hosts[:4]:
        if host.cpu_history:
            cpu = host.cpu_history[-1]
            print(f"\n  🖥️ {host.hostname}:")
            print(f"    Total: {cpu.total_percent:.1f}%")
            print(f"    User: {cpu.user_percent:.1f}%, System: {cpu.system_percent:.1f}%")
            print(f"    Load: {cpu.load_1:.2f} / {cpu.load_5:.2f} / {cpu.load_15:.2f}")
            
    # Memory metrics
    print("\n💾 Memory Metrics:")
    
    for host in hosts[:4]:
        if host.memory_history:
            mem = host.memory_history[-1]
            used = manager._format_bytes(mem.used_bytes)
            total = manager._format_bytes(mem.total_bytes)
            print(f"\n  🖥️ {host.hostname}:")
            print(f"    Used: {used} / {total} ({mem.used_percent:.1f}%)")
            print(f"    Swap: {mem.swap_percent:.1f}%")
            
    # Disk metrics
    print("\n📁 Disk Usage:")
    
    for host in hosts[:3]:
        print(f"\n  🖥️ {host.hostname}:")
        for mount, disk in host.disks.items():
            used = manager._format_bytes(disk.used_bytes)
            total = manager._format_bytes(disk.total_bytes)
            bar_len = 20
            filled = int(disk.used_percent / 100 * bar_len)
            bar = "█" * filled + "░" * (bar_len - filled)
            print(f"    {mount}: [{bar}] {disk.used_percent:.1f}% ({used}/{total})")
            
    # Services
    print("\n⚙️ Service Status:")
    
    for host in hosts[:3]:
        print(f"\n  🖥️ {host.hostname}:")
        for name, svc in list(host.services.items())[:5]:
            status_icon = "🟢" if svc.status == ServiceStatus.RUNNING else "🔴"
            enabled = "enabled" if svc.enabled else "disabled"
            print(f"    {status_icon} {name}: {svc.status.value} ({enabled})")
            
    # Top processes
    print("\n📊 Top Processes (by CPU):")
    
    for host in hosts[:2]:
        print(f"\n  🖥️ {host.hostname}:")
        sorted_procs = sorted(host.processes.values(), 
                             key=lambda p: p.cpu_percent, reverse=True)[:5]
        for proc in sorted_procs:
            mem = manager._format_bytes(proc.memory_rss)
            print(f"    PID {proc.pid}: {proc.name} - CPU: {proc.cpu_percent:.1f}%, Mem: {mem}")
            
    # Network interfaces
    print("\n🌐 Network Interfaces:")
    
    for host in hosts[:3]:
        print(f"\n  🖥️ {host.hostname}:")
        for name, iface in host.network_interfaces.items():
            status = "UP" if iface.is_up else "DOWN"
            print(f"    {name}: {iface.ip_address or 'no ip'} ({iface.speed_mbps}Mbps, {status})")
            
    # Alerts
    print("\n🚨 Active Alerts:")
    
    alerts = manager.get_active_alerts()
    
    if alerts:
        for alert in alerts[:5]:
            severity_icons = {
                AlertSeverity.INFO: "ℹ️",
                AlertSeverity.WARNING: "⚠️",
                AlertSeverity.ERROR: "❌",
                AlertSeverity.CRITICAL: "🔴"
            }
            icon = severity_icons.get(alert.severity, "❓")
            print(f"  {icon} [{alert.severity.value}] {alert.message}")
    else:
        print("  ✅ No active alerts")
        
    # Statistics
    print("\n📊 Infrastructure Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Total Hosts: {stats['total_hosts']}")
    print(f"  Online Hosts: {stats['online_hosts']}")
    print(f"\n  Total CPU Cores: {stats['total_cpu_cores']}")
    print(f"  Total Memory: {manager._format_bytes(stats['total_memory'])}")
    print(f"  Total Disk: {manager._format_bytes(stats['total_disk'])}")
    print(f"\n  Average Health Score: {stats['avg_health_score']:.1f}%")
    print(f"  Active Alerts: {stats['active_alerts']}")
    
    availability = stats['online_hosts'] / max(stats['total_hosts'], 1) * 100
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Infrastructure Monitoring Dashboard              │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Hosts:                   {stats['total_hosts']:>12}                        │")
    print(f"│ Online Hosts:                  {stats['online_hosts']:>12}                        │")
    print(f"│ Total CPU Cores:               {stats['total_cpu_cores']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Infrastructure Availability:   {availability:>11.1f}%                        │")
    print(f"│ Average Health Score:          {stats['avg_health_score']:>11.1f}%                        │")
    print(f"│ Active Alerts:                 {stats['active_alerts']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Infrastructure Monitoring Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
