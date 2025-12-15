#!/usr/bin/env python3
"""
Server Init - Iteration 368: Network Monitoring Platform
Платформа мониторинга сети

Функционал:
- Device Monitoring - мониторинг устройств
- Traffic Analysis - анализ трафика
- SNMP Polling - опрос SNMP
- Flow Collection - сбор потоков
- Topology Discovery - обнаружение топологии
- Performance Metrics - метрики производительности
- Alert Management - управление оповещениями
- Bandwidth Monitoring - мониторинг пропускной способности
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
import uuid


class DeviceType(Enum):
    """Тип устройства"""
    ROUTER = "router"
    SWITCH = "switch"
    FIREWALL = "firewall"
    LOAD_BALANCER = "load_balancer"
    ACCESS_POINT = "access_point"
    SERVER = "server"
    GATEWAY = "gateway"
    IDS_IPS = "ids_ips"


class DeviceStatus(Enum):
    """Статус устройства"""
    UP = "up"
    DOWN = "down"
    WARNING = "warning"
    UNREACHABLE = "unreachable"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"


class InterfaceStatus(Enum):
    """Статус интерфейса"""
    UP = "up"
    DOWN = "down"
    ADMIN_DOWN = "admin_down"
    ERROR = "error"


class AlertSeverity(Enum):
    """Серьезность оповещения"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertType(Enum):
    """Тип оповещения"""
    DEVICE_DOWN = "device_down"
    INTERFACE_DOWN = "interface_down"
    HIGH_CPU = "high_cpu"
    HIGH_MEMORY = "high_memory"
    HIGH_BANDWIDTH = "high_bandwidth"
    PACKET_LOSS = "packet_loss"
    HIGH_LATENCY = "high_latency"
    FLAPPING = "flapping"


class ProtocolType(Enum):
    """Тип протокола"""
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    HTTP = "http"
    HTTPS = "https"
    DNS = "dns"
    SSH = "ssh"
    SNMP = "snmp"


class FlowDirection(Enum):
    """Направление потока"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BIDIRECTIONAL = "bidirectional"


@dataclass
class NetworkInterface:
    """Сетевой интерфейс"""
    interface_id: str
    
    # Identity
    name: str = ""
    description: str = ""
    alias: str = ""
    
    # Physical
    mac_address: str = ""
    speed_mbps: int = 0
    mtu: int = 1500
    
    # Status
    status: InterfaceStatus = InterfaceStatus.UP
    admin_status: InterfaceStatus = InterfaceStatus.UP
    
    # IP
    ip_address: str = ""
    subnet_mask: str = ""
    
    # Traffic
    bytes_in: int = 0
    bytes_out: int = 0
    packets_in: int = 0
    packets_out: int = 0
    errors_in: int = 0
    errors_out: int = 0
    discards_in: int = 0
    discards_out: int = 0
    
    # Utilization
    utilization_in_percent: float = 0.0
    utilization_out_percent: float = 0.0
    
    # Last update
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class NetworkDevice:
    """Сетевое устройство"""
    device_id: str
    
    # Identity
    hostname: str = ""
    ip_address: str = ""
    fqdn: str = ""
    
    # Type
    device_type: DeviceType = DeviceType.ROUTER
    vendor: str = ""
    model: str = ""
    
    # Status
    status: DeviceStatus = DeviceStatus.UNKNOWN
    
    # SNMP
    snmp_community: str = ""
    snmp_version: str = "2c"
    
    # System info
    sys_name: str = ""
    sys_description: str = ""
    sys_uptime: int = 0  # seconds
    sys_location: str = ""
    sys_contact: str = ""
    
    # Performance
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    temperature: float = 0.0
    
    # Interfaces
    interfaces: Dict[str, NetworkInterface] = field(default_factory=dict)
    
    # Neighbors
    neighbors: List[str] = field(default_factory=list)  # device IDs
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Monitoring
    poll_interval: int = 60  # seconds
    last_polled: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class NetworkAlert:
    """Сетевое оповещение"""
    alert_id: str
    
    # Source
    device_id: str = ""
    interface_id: str = ""
    
    # Alert details
    alert_type: AlertType = AlertType.DEVICE_DOWN
    severity: AlertSeverity = AlertSeverity.WARNING
    
    # Message
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Threshold
    threshold_value: float = 0.0
    current_value: float = 0.0
    
    # Status
    is_acknowledged: bool = False
    acknowledged_by: str = ""
    acknowledged_at: Optional[datetime] = None
    
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None
    
    # Timestamps
    triggered_at: datetime = field(default_factory=datetime.now)


@dataclass
class TrafficFlow:
    """Трафик поток"""
    flow_id: str
    
    # Source
    source_ip: str = ""
    source_port: int = 0
    source_device: str = ""
    
    # Destination
    dest_ip: str = ""
    dest_port: int = 0
    dest_device: str = ""
    
    # Protocol
    protocol: ProtocolType = ProtocolType.TCP
    
    # Direction
    direction: FlowDirection = FlowDirection.BIDIRECTIONAL
    
    # Metrics
    bytes: int = 0
    packets: int = 0
    duration_sec: int = 0
    
    # Application
    application: str = ""
    
    # Timestamps
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None


@dataclass
class TopologyLink:
    """Связь в топологии"""
    link_id: str
    
    # Endpoints
    source_device_id: str = ""
    source_interface: str = ""
    target_device_id: str = ""
    target_interface: str = ""
    
    # Link type
    link_type: str = ""  # ethernet, fiber, wireless
    
    # Capacity
    bandwidth_mbps: int = 0
    
    # Status
    status: str = "up"  # up, down, degraded
    
    # Utilization
    utilization_percent: float = 0.0


@dataclass
class BandwidthReport:
    """Отчет о пропускной способности"""
    report_id: str
    
    # Scope
    device_id: str = ""
    interface_id: str = ""
    
    # Time range
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime = field(default_factory=datetime.now)
    
    # Metrics
    avg_bandwidth_in_mbps: float = 0.0
    avg_bandwidth_out_mbps: float = 0.0
    peak_bandwidth_in_mbps: float = 0.0
    peak_bandwidth_out_mbps: float = 0.0
    
    # 95th percentile
    percentile_95_in_mbps: float = 0.0
    percentile_95_out_mbps: float = 0.0
    
    # Total
    total_bytes_in: int = 0
    total_bytes_out: int = 0


@dataclass
class ThresholdRule:
    """Правило порога"""
    rule_id: str
    
    # Identity
    name: str = ""
    
    # Scope
    device_type: Optional[DeviceType] = None
    devices: List[str] = field(default_factory=list)
    
    # Metric
    metric_name: str = ""  # cpu_usage, memory_usage, interface_utilization
    
    # Thresholds
    warning_threshold: float = 0.0
    critical_threshold: float = 0.0
    
    # Duration
    duration_minutes: int = 5  # Sustain period
    
    # Status
    is_enabled: bool = True


@dataclass
class SNMPPollResult:
    """Результат SNMP опроса"""
    poll_id: str
    
    # Target
    device_id: str = ""
    
    # Status
    success: bool = True
    error_message: str = ""
    
    # Response time
    response_time_ms: float = 0.0
    
    # OIDs
    collected_oids: int = 0
    
    # Timestamp
    polled_at: datetime = field(default_factory=datetime.now)


@dataclass
class NetworkMetrics:
    """Метрики сети"""
    metrics_id: str
    
    # Devices
    total_devices: int = 0
    devices_up: int = 0
    devices_down: int = 0
    
    # Interfaces
    total_interfaces: int = 0
    interfaces_up: int = 0
    
    # Traffic
    total_traffic_in_gbps: float = 0.0
    total_traffic_out_gbps: float = 0.0
    
    # Alerts
    active_alerts: int = 0
    alerts_24h: int = 0
    
    # Availability
    average_availability: float = 0.0
    
    # Timestamps
    collected_at: datetime = field(default_factory=datetime.now)


class NetworkMonitoringPlatform:
    """Платформа мониторинга сети"""
    
    def __init__(self, platform_name: str = "netmon"):
        self.platform_name = platform_name
        self.devices: Dict[str, NetworkDevice] = {}
        self.alerts: Dict[str, NetworkAlert] = {}
        self.flows: List[TrafficFlow] = []
        self.topology_links: Dict[str, TopologyLink] = {}
        self.threshold_rules: Dict[str, ThresholdRule] = {}
        self.poll_results: List[SNMPPollResult] = []
        
    async def add_device(self, hostname: str,
                        ip_address: str,
                        device_type: DeviceType,
                        vendor: str = "",
                        model: str = "",
                        snmp_community: str = "public") -> NetworkDevice:
        """Добавление устройства"""
        device = NetworkDevice(
            device_id=f"dev_{uuid.uuid4().hex[:8]}",
            hostname=hostname,
            ip_address=ip_address,
            device_type=device_type,
            vendor=vendor,
            model=model,
            snmp_community=snmp_community,
            status=DeviceStatus.UNKNOWN
        )
        
        self.devices[device.device_id] = device
        
        # Initial poll
        await self._poll_device(device)
        
        return device
        
    async def _poll_device(self, device: NetworkDevice):
        """Опрос устройства"""
        # Simulate SNMP poll
        await asyncio.sleep(0.01)
        
        poll_result = SNMPPollResult(
            poll_id=f"poll_{uuid.uuid4().hex[:8]}",
            device_id=device.device_id,
            success=random.random() > 0.05,  # 95% success rate
            response_time_ms=random.uniform(1, 50)
        )
        
        if poll_result.success:
            device.status = DeviceStatus.UP
            device.last_polled = datetime.now()
            
            # Simulate metrics
            device.cpu_usage = random.uniform(10, 80)
            device.memory_usage = random.uniform(30, 85)
            device.sys_uptime = random.randint(86400, 86400 * 365)  # 1 day to 1 year
            
            # Generate interfaces if empty
            if not device.interfaces:
                await self._generate_interfaces(device)
                
            # Update interface stats
            for iface in device.interfaces.values():
                iface.bytes_in += random.randint(1000000, 100000000)
                iface.bytes_out += random.randint(1000000, 100000000)
                iface.packets_in += random.randint(1000, 100000)
                iface.packets_out += random.randint(1000, 100000)
                iface.utilization_in_percent = random.uniform(5, 70)
                iface.utilization_out_percent = random.uniform(5, 70)
                iface.last_updated = datetime.now()
                
            poll_result.collected_oids = random.randint(50, 200)
        else:
            device.status = DeviceStatus.UNREACHABLE
            poll_result.error_message = "SNMP timeout"
            
        self.poll_results.append(poll_result)
        
    async def _generate_interfaces(self, device: NetworkDevice):
        """Генерация интерфейсов"""
        interface_counts = {
            DeviceType.ROUTER: random.randint(4, 12),
            DeviceType.SWITCH: random.randint(24, 48),
            DeviceType.FIREWALL: random.randint(4, 8),
            DeviceType.LOAD_BALANCER: random.randint(2, 4),
            DeviceType.ACCESS_POINT: random.randint(1, 2),
            DeviceType.SERVER: random.randint(2, 4),
            DeviceType.GATEWAY: random.randint(2, 4)
        }
        
        count = interface_counts.get(device.device_type, 4)
        
        for i in range(count):
            iface = NetworkInterface(
                interface_id=f"if_{uuid.uuid4().hex[:8]}",
                name=f"eth{i}" if device.device_type != DeviceType.SWITCH else f"Gi0/{i}",
                description=f"Interface {i}",
                mac_address=":".join([f"{random.randint(0, 255):02x}" for _ in range(6)]),
                speed_mbps=random.choice([100, 1000, 10000]),
                status=InterfaceStatus.UP if random.random() > 0.1 else InterfaceStatus.DOWN,
                ip_address=f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{i + 1}" if i < 4 else ""
            )
            device.interfaces[iface.interface_id] = iface
            
    async def poll_all_devices(self):
        """Опрос всех устройств"""
        for device in self.devices.values():
            await self._poll_device(device)
            
    async def create_alert(self, device_id: str,
                          alert_type: AlertType,
                          severity: AlertSeverity,
                          message: str,
                          interface_id: str = "",
                          threshold: float = 0.0,
                          current: float = 0.0) -> NetworkAlert:
        """Создание оповещения"""
        alert = NetworkAlert(
            alert_id=f"alt_{uuid.uuid4().hex[:8]}",
            device_id=device_id,
            interface_id=interface_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            threshold_value=threshold,
            current_value=current
        )
        
        self.alerts[alert.alert_id] = alert
        return alert
        
    async def check_thresholds(self):
        """Проверка порогов"""
        for device in self.devices.values():
            # CPU threshold
            if device.cpu_usage > 90:
                await self.create_alert(
                    device.device_id,
                    AlertType.HIGH_CPU,
                    AlertSeverity.CRITICAL,
                    f"High CPU usage on {device.hostname}",
                    threshold=90,
                    current=device.cpu_usage
                )
            elif device.cpu_usage > 80:
                await self.create_alert(
                    device.device_id,
                    AlertType.HIGH_CPU,
                    AlertSeverity.WARNING,
                    f"Elevated CPU usage on {device.hostname}",
                    threshold=80,
                    current=device.cpu_usage
                )
                
            # Memory threshold
            if device.memory_usage > 95:
                await self.create_alert(
                    device.device_id,
                    AlertType.HIGH_MEMORY,
                    AlertSeverity.CRITICAL,
                    f"Critical memory usage on {device.hostname}",
                    threshold=95,
                    current=device.memory_usage
                )
                
            # Interface utilization
            for iface in device.interfaces.values():
                max_util = max(iface.utilization_in_percent, iface.utilization_out_percent)
                if max_util > 90:
                    await self.create_alert(
                        device.device_id,
                        AlertType.HIGH_BANDWIDTH,
                        AlertSeverity.WARNING,
                        f"High bandwidth on {device.hostname}:{iface.name}",
                        interface_id=iface.interface_id,
                        threshold=90,
                        current=max_util
                    )
                    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Подтверждение оповещения"""
        alert = self.alerts.get(alert_id)
        if not alert:
            return False
            
        alert.is_acknowledged = True
        alert.acknowledged_by = acknowledged_by
        alert.acknowledged_at = datetime.now()
        return True
        
    async def resolve_alert(self, alert_id: str) -> bool:
        """Разрешение оповещения"""
        alert = self.alerts.get(alert_id)
        if not alert:
            return False
            
        alert.is_resolved = True
        alert.resolved_at = datetime.now()
        return True
        
    async def discover_topology(self) -> List[TopologyLink]:
        """Обнаружение топологии"""
        links = []
        
        device_list = list(self.devices.values())
        
        # Create random links between devices
        for device in device_list:
            # Each device connects to 1-3 other devices
            connections = random.randint(1, min(3, len(device_list) - 1))
            targets = random.sample([d for d in device_list if d.device_id != device.device_id], connections)
            
            for target in targets:
                # Check if reverse link exists
                existing = any(
                    l.source_device_id == target.device_id and l.target_device_id == device.device_id
                    for l in links
                )
                if existing:
                    continue
                    
                source_iface = list(device.interfaces.values())[0] if device.interfaces else None
                target_iface = list(target.interfaces.values())[0] if target.interfaces else None
                
                link = TopologyLink(
                    link_id=f"lnk_{uuid.uuid4().hex[:8]}",
                    source_device_id=device.device_id,
                    source_interface=source_iface.interface_id if source_iface else "",
                    target_device_id=target.device_id,
                    target_interface=target_iface.interface_id if target_iface else "",
                    link_type=random.choice(["ethernet", "fiber"]),
                    bandwidth_mbps=random.choice([1000, 10000]),
                    status="up" if random.random() > 0.1 else "degraded",
                    utilization_percent=random.uniform(10, 60)
                )
                links.append(link)
                self.topology_links[link.link_id] = link
                
                # Update neighbors
                device.neighbors.append(target.device_id)
                target.neighbors.append(device.device_id)
                
        return links
        
    async def collect_flow(self, source_ip: str,
                          dest_ip: str,
                          protocol: ProtocolType,
                          bytes_count: int,
                          packets: int) -> TrafficFlow:
        """Сбор потока трафика"""
        flow = TrafficFlow(
            flow_id=f"flw_{uuid.uuid4().hex[:8]}",
            source_ip=source_ip,
            dest_ip=dest_ip,
            protocol=protocol,
            bytes=bytes_count,
            packets=packets,
            duration_sec=random.randint(1, 300)
        )
        
        self.flows.append(flow)
        return flow
        
    async def generate_bandwidth_report(self, device_id: str,
                                       interface_id: str = "") -> BandwidthReport:
        """Генерация отчета о пропускной способности"""
        device = self.devices.get(device_id)
        if not device:
            return None
            
        # Simulate metrics
        report = BandwidthReport(
            report_id=f"bw_{uuid.uuid4().hex[:8]}",
            device_id=device_id,
            interface_id=interface_id,
            start_time=datetime.now() - timedelta(days=1),
            end_time=datetime.now(),
            avg_bandwidth_in_mbps=random.uniform(100, 500),
            avg_bandwidth_out_mbps=random.uniform(100, 500),
            peak_bandwidth_in_mbps=random.uniform(500, 1000),
            peak_bandwidth_out_mbps=random.uniform(500, 1000),
            percentile_95_in_mbps=random.uniform(400, 800),
            percentile_95_out_mbps=random.uniform(400, 800),
            total_bytes_in=random.randint(10**9, 10**12),
            total_bytes_out=random.randint(10**9, 10**12)
        )
        
        return report
        
    async def create_threshold_rule(self, name: str,
                                   metric_name: str,
                                   warning_threshold: float,
                                   critical_threshold: float,
                                   device_type: DeviceType = None) -> ThresholdRule:
        """Создание правила порога"""
        rule = ThresholdRule(
            rule_id=f"thr_{uuid.uuid4().hex[:8]}",
            name=name,
            device_type=device_type,
            metric_name=metric_name,
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold
        )
        
        self.threshold_rules[rule.rule_id] = rule
        return rule
        
    async def collect_metrics(self) -> NetworkMetrics:
        """Сбор метрик"""
        devices_up = sum(1 for d in self.devices.values() if d.status == DeviceStatus.UP)
        devices_down = sum(1 for d in self.devices.values() if d.status in [DeviceStatus.DOWN, DeviceStatus.UNREACHABLE])
        
        total_interfaces = sum(len(d.interfaces) for d in self.devices.values())
        interfaces_up = sum(
            sum(1 for i in d.interfaces.values() if i.status == InterfaceStatus.UP)
            for d in self.devices.values()
        )
        
        # Calculate traffic
        total_in = sum(
            sum(i.bytes_in for i in d.interfaces.values())
            for d in self.devices.values()
        )
        total_out = sum(
            sum(i.bytes_out for i in d.interfaces.values())
            for d in self.devices.values()
        )
        
        active_alerts = sum(1 for a in self.alerts.values() if not a.is_resolved)
        
        now = datetime.now()
        alerts_24h = sum(
            1 for a in self.alerts.values()
            if (now - a.triggered_at).total_seconds() < 86400
        )
        
        # Availability (simplified)
        availability = (devices_up / len(self.devices) * 100) if self.devices else 0.0
        
        return NetworkMetrics(
            metrics_id=f"nm_{uuid.uuid4().hex[:8]}",
            total_devices=len(self.devices),
            devices_up=devices_up,
            devices_down=devices_down,
            total_interfaces=total_interfaces,
            interfaces_up=interfaces_up,
            total_traffic_in_gbps=total_in / 1e9,
            total_traffic_out_gbps=total_out / 1e9,
            active_alerts=active_alerts,
            alerts_24h=alerts_24h,
            average_availability=availability
        )
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        by_type = {}
        for dtype in DeviceType:
            by_type[dtype.value] = sum(1 for d in self.devices.values() if d.device_type == dtype)
            
        by_status = {}
        for status in DeviceStatus:
            by_status[status.value] = sum(1 for d in self.devices.values() if d.status == status)
            
        by_vendor = {}
        for device in self.devices.values():
            vendor = device.vendor or "Unknown"
            by_vendor[vendor] = by_vendor.get(vendor, 0) + 1
            
        alerts_by_severity = {}
        for severity in AlertSeverity:
            alerts_by_severity[severity.value] = sum(
                1 for a in self.alerts.values()
                if a.severity == severity and not a.is_resolved
            )
            
        return {
            "total_devices": len(self.devices),
            "by_type": by_type,
            "by_status": by_status,
            "by_vendor": by_vendor,
            "total_interfaces": sum(len(d.interfaces) for d in self.devices.values()),
            "total_alerts": len(self.alerts),
            "active_alerts": sum(1 for a in self.alerts.values() if not a.is_resolved),
            "alerts_by_severity": alerts_by_severity,
            "topology_links": len(self.topology_links),
            "threshold_rules": len(self.threshold_rules),
            "flow_records": len(self.flows)
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 368: Network Monitoring Platform")
    print("=" * 60)
    
    platform = NetworkMonitoringPlatform(platform_name="enterprise-netmon")
    print("✓ Network Monitoring Platform initialized")
    
    # Add Network Devices
    print("\n🖧 Adding Network Devices...")
    
    devices_data = [
        ("core-router-01", "10.0.0.1", DeviceType.ROUTER, "Cisco", "ASR 9000"),
        ("core-router-02", "10.0.0.2", DeviceType.ROUTER, "Juniper", "MX480"),
        ("dist-switch-01", "10.0.1.1", DeviceType.SWITCH, "Cisco", "Nexus 9300"),
        ("dist-switch-02", "10.0.1.2", DeviceType.SWITCH, "Arista", "7050X"),
        ("dist-switch-03", "10.0.1.3", DeviceType.SWITCH, "Cisco", "Catalyst 9500"),
        ("firewall-01", "10.0.2.1", DeviceType.FIREWALL, "Palo Alto", "PA-5260"),
        ("firewall-02", "10.0.2.2", DeviceType.FIREWALL, "Fortinet", "FortiGate 600E"),
        ("lb-01", "10.0.3.1", DeviceType.LOAD_BALANCER, "F5", "BIG-IP i5800"),
        ("lb-02", "10.0.3.2", DeviceType.LOAD_BALANCER, "Citrix", "ADC VPX"),
        ("access-sw-01", "10.1.1.1", DeviceType.SWITCH, "Cisco", "Catalyst 9200"),
        ("access-sw-02", "10.1.1.2", DeviceType.SWITCH, "HP", "Aruba 2930F"),
        ("wifi-ap-01", "10.2.1.1", DeviceType.ACCESS_POINT, "Cisco", "Aironet 9120")
    ]
    
    for hostname, ip, dtype, vendor, model in devices_data:
        device = await platform.add_device(hostname, ip, dtype, vendor, model)
        iface_count = len(device.interfaces)
        print(f"  🖧 {hostname} ({dtype.value}) - {iface_count} interfaces")
        
    # Poll all devices
    print("\n📡 Polling devices...")
    await platform.poll_all_devices()
    print(f"  ✓ Polled {len(platform.devices)} devices")
    
    # Discover Topology
    print("\n🗺️ Discovering Network Topology...")
    
    links = await platform.discover_topology()
    print(f"  ✓ Discovered {len(links)} topology links")
    
    # Create Threshold Rules
    print("\n⚙️ Creating Threshold Rules...")
    
    rules_data = [
        ("CPU Warning", "cpu_usage", 75.0, 90.0),
        ("Memory Warning", "memory_usage", 80.0, 95.0),
        ("Bandwidth Alert", "interface_utilization", 70.0, 90.0)
    ]
    
    for name, metric, warn, crit in rules_data:
        await platform.create_threshold_rule(name, metric, warn, crit)
        print(f"  ⚙️ {name}: Warning>{warn}%, Critical>{crit}%")
        
    # Check Thresholds
    print("\n🔔 Checking Thresholds...")
    await platform.check_thresholds()
    
    active_alerts = sum(1 for a in platform.alerts.values() if not a.is_resolved)
    print(f"  ⚠️ Active alerts: {active_alerts}")
    
    # Collect Traffic Flows
    print("\n📊 Collecting Traffic Flows...")
    
    protocols = list(ProtocolType)
    for _ in range(20):
        src_ip = f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
        dst_ip = f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
        await platform.collect_flow(
            src_ip, dst_ip,
            random.choice(protocols),
            random.randint(1000, 1000000),
            random.randint(10, 10000)
        )
    print(f"  ✓ Collected {len(platform.flows)} flow records")
    
    # Generate Bandwidth Report
    print("\n📈 Generating Bandwidth Reports...")
    
    sample_device = list(platform.devices.values())[0]
    report = await platform.generate_bandwidth_report(sample_device.device_id)
    print(f"  Device: {sample_device.hostname}")
    print(f"  Avg In:  {report.avg_bandwidth_in_mbps:.1f} Mbps")
    print(f"  Avg Out: {report.avg_bandwidth_out_mbps:.1f} Mbps")
    print(f"  Peak In: {report.peak_bandwidth_in_mbps:.1f} Mbps")
    print(f"  95th In: {report.percentile_95_in_mbps:.1f} Mbps")
    
    # Collect Metrics
    metrics = await platform.collect_metrics()
    
    # Device Table
    print("\n🖧 Network Devices:")
    
    print("\n  ┌──────────────────────┬──────────────────┬──────────────────┬─────────────┬──────────────┬──────────┐")
    print("  │ Hostname             │ Type             │ IP               │ Vendor      │ Status       │ CPU      │")
    print("  ├──────────────────────┼──────────────────┼──────────────────┼─────────────┼──────────────┼──────────┤")
    
    for device in platform.devices.values():
        hostname = device.hostname[:20].ljust(20)
        dtype = device.device_type.value[:16].ljust(16)
        ip = device.ip_address[:16].ljust(16)
        vendor = device.vendor[:11].ljust(11)
        status = device.status.value[:12].ljust(12)
        cpu = f"{device.cpu_usage:5.1f}%".ljust(8)
        
        print(f"  │ {hostname} │ {dtype} │ {ip} │ {vendor} │ {status} │ {cpu} │")
        
    print("  └──────────────────────┴──────────────────┴──────────────────┴─────────────┴──────────────┴──────────┘")
    
    # Interface Summary
    print("\n🔌 Interface Summary (Sample Device: {})".format(sample_device.hostname))
    
    for iface_id, iface in list(sample_device.interfaces.items())[:6]:
        status_icon = "🟢" if iface.status == InterfaceStatus.UP else "🔴"
        speed = f"{iface.speed_mbps}M"
        util = f"↓{iface.utilization_in_percent:.0f}% ↑{iface.utilization_out_percent:.0f}%"
        print(f"  {status_icon} {iface.name:12s} │ {speed:7s} │ {util}")
        
    # Active Alerts
    print("\n🔔 Active Alerts:")
    
    for alert in list(platform.alerts.values())[:8]:
        if not alert.is_resolved:
            device = platform.devices.get(alert.device_id)
            hostname = device.hostname if device else "Unknown"
            severity_icon = {"info": "ℹ️", "warning": "⚠️", "error": "❌", "critical": "🔴"}
            icon = severity_icon.get(alert.severity.value, "❓")
            print(f"  {icon} [{alert.severity.value:8s}] {hostname}: {alert.message[:50]}")
            
    # Topology
    print("\n🗺️ Network Topology (Sample Links):")
    
    for link in list(platform.topology_links.values())[:6]:
        src_device = platform.devices.get(link.source_device_id)
        tgt_device = platform.devices.get(link.target_device_id)
        if src_device and tgt_device:
            status_icon = "━━" if link.status == "up" else "╍╍"
            print(f"  {src_device.hostname} {status_icon}[{link.bandwidth_mbps}M]{status_icon}> {tgt_device.hostname}")
            
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📊 Device Distribution:")
    
    # By Type
    print("\n  By Type:")
    for dtype, count in stats["by_type"].items():
        if count > 0:
            bar = "█" * count
            print(f"    {dtype:18s} │ {bar} ({count})")
            
    # By Vendor
    print("\n  By Vendor:")
    for vendor, count in sorted(stats["by_vendor"].items(), key=lambda x: -x[1]):
        bar = "█" * count
        print(f"    {vendor:15s} │ {bar} ({count})")
        
    # By Status
    print("\n  By Status:")
    for status, count in stats["by_status"].items():
        if count > 0:
            bar = "█" * count
            print(f"    {status:12s} │ {bar} ({count})")
            
    # Alerts by Severity
    print("\n  Active Alerts by Severity:")
    for severity, count in stats["alerts_by_severity"].items():
        if count > 0:
            bar = "█" * count
            print(f"    {severity:10s} │ {bar} ({count})")
            
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Network Monitoring Platform                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Devices:                 {stats['total_devices']:>12}                      │")
    print(f"│ Devices Up:                    {metrics.devices_up:>12}                      │")
    print(f"│ Devices Down:                  {metrics.devices_down:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Interfaces:              {stats['total_interfaces']:>12}                      │")
    print(f"│ Interfaces Up:                 {metrics.interfaces_up:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Traffic In:                    {metrics.total_traffic_in_gbps:>11.2f} GB                     │")
    print(f"│ Traffic Out:                   {metrics.total_traffic_out_gbps:>11.2f} GB                     │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Active Alerts:                 {stats['active_alerts']:>12}                      │")
    print(f"│ Alerts (24h):                  {metrics.alerts_24h:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Topology Links:                {stats['topology_links']:>12}                      │")
    print(f"│ Flow Records:                  {stats['flow_records']:>12}                      │")
    print(f"│ Availability:                  {metrics.average_availability:>11.1f}%                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Network Monitoring Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
