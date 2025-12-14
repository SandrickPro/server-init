#!/usr/bin/env python3
"""
Server Init - Iteration 124: Network Observability Platform
Платформа сетевой наблюдаемости

Функционал:
- Traffic Analysis - анализ трафика
- Flow Collection - сбор потоков
- Network Mapping - картирование сети
- Latency Monitoring - мониторинг задержек
- Packet Capture - захват пакетов
- Protocol Analysis - анализ протоколов
- Bandwidth Monitoring - мониторинг пропускной способности
- Network Anomaly Detection - обнаружение аномалий
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from collections import defaultdict
import uuid
import random


class Protocol(Enum):
    """Сетевой протокол"""
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    HTTP = "http"
    HTTPS = "https"
    DNS = "dns"
    GRPC = "grpc"


class FlowDirection(Enum):
    """Направление потока"""
    INGRESS = "ingress"
    EGRESS = "egress"
    INTERNAL = "internal"


class AnomalyType(Enum):
    """Тип аномалии"""
    HIGH_LATENCY = "high_latency"
    PACKET_LOSS = "packet_loss"
    BANDWIDTH_SPIKE = "bandwidth_spike"
    CONNECTION_FLOOD = "connection_flood"
    DNS_ANOMALY = "dns_anomaly"
    PORT_SCAN = "port_scan"


class AlertSeverity(Enum):
    """Критичность алерта"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class NetworkInterface:
    """Сетевой интерфейс"""
    interface_id: str
    name: str = ""
    
    # Address
    ip_address: str = ""
    mac_address: str = ""
    
    # Stats
    bytes_in: int = 0
    bytes_out: int = 0
    packets_in: int = 0
    packets_out: int = 0
    errors_in: int = 0
    errors_out: int = 0
    
    # Status
    up: bool = True
    speed_mbps: int = 1000


@dataclass
class NetworkNode:
    """Сетевой узел"""
    node_id: str
    hostname: str = ""
    node_type: str = "server"  # server, router, switch, firewall
    
    # Network
    interfaces: List[NetworkInterface] = field(default_factory=list)
    
    # Location
    datacenter: str = ""
    rack: str = ""
    
    # Status
    online: bool = True


@dataclass
class NetworkFlow:
    """Сетевой поток"""
    flow_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Source
    src_ip: str = ""
    src_port: int = 0
    src_node: str = ""
    
    # Destination
    dst_ip: str = ""
    dst_port: int = 0
    dst_node: str = ""
    
    # Protocol
    protocol: Protocol = Protocol.TCP
    direction: FlowDirection = FlowDirection.INGRESS
    
    # Metrics
    bytes: int = 0
    packets: int = 0
    duration_ms: int = 0
    
    # Quality
    latency_ms: float = 0.0
    jitter_ms: float = 0.0
    packet_loss_percent: float = 0.0


@dataclass
class LatencyProbe:
    """Проба задержки"""
    probe_id: str
    name: str = ""
    
    # Target
    target_ip: str = ""
    target_port: int = 0
    protocol: Protocol = Protocol.TCP
    
    # Results
    last_latency_ms: float = 0.0
    avg_latency_ms: float = 0.0
    max_latency_ms: float = 0.0
    min_latency_ms: float = 0.0
    
    # Stats
    success_count: int = 0
    failure_count: int = 0
    
    # Thresholds
    warning_threshold_ms: float = 100.0
    critical_threshold_ms: float = 500.0


@dataclass
class NetworkAnomaly:
    """Сетевая аномалия"""
    anomaly_id: str
    anomaly_type: AnomalyType = AnomalyType.HIGH_LATENCY
    
    # Details
    severity: AlertSeverity = AlertSeverity.WARNING
    source: str = ""
    description: str = ""
    
    # Metrics
    observed_value: float = 0.0
    expected_value: float = 0.0
    deviation_percent: float = 0.0
    
    # Time
    detected_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


@dataclass
class TopTalker:
    """Топ источник трафика"""
    ip_address: str
    hostname: str = ""
    
    # Traffic
    bytes_total: int = 0
    packets_total: int = 0
    connections: int = 0
    
    # Breakdown
    protocols: Dict[str, int] = field(default_factory=dict)


class FlowCollector:
    """Сборщик потоков"""
    
    def __init__(self):
        self.flows: List[NetworkFlow] = []
        
    def collect(self, src_ip: str, dst_ip: str, protocol: Protocol,
                 bytes_count: int, packets: int, **kwargs) -> NetworkFlow:
        """Сбор потока"""
        flow = NetworkFlow(
            flow_id=f"flow_{uuid.uuid4().hex[:8]}",
            src_ip=src_ip,
            dst_ip=dst_ip,
            protocol=protocol,
            bytes=bytes_count,
            packets=packets,
            **kwargs
        )
        self.flows.append(flow)
        
        # Keep only recent flows
        if len(self.flows) > 10000:
            self.flows = self.flows[-5000:]
            
        return flow
        
    def get_flows(self, minutes: int = 5) -> List[NetworkFlow]:
        """Получить недавние потоки"""
        threshold = datetime.now() - timedelta(minutes=minutes)
        return [f for f in self.flows if f.timestamp >= threshold]
        
    def aggregate_by_protocol(self, minutes: int = 5) -> Dict[str, Dict]:
        """Агрегация по протоколу"""
        flows = self.get_flows(minutes)
        
        result = defaultdict(lambda: {"bytes": 0, "packets": 0, "flows": 0})
        for flow in flows:
            proto = flow.protocol.value
            result[proto]["bytes"] += flow.bytes
            result[proto]["packets"] += flow.packets
            result[proto]["flows"] += 1
            
        return dict(result)


class NetworkMapper:
    """Картограф сети"""
    
    def __init__(self):
        self.nodes: Dict[str, NetworkNode] = {}
        self.connections: List[Tuple[str, str]] = []
        
    def add_node(self, hostname: str, node_type: str,
                  interfaces: List[Dict] = None, **kwargs) -> NetworkNode:
        """Добавление узла"""
        node = NetworkNode(
            node_id=f"node_{uuid.uuid4().hex[:8]}",
            hostname=hostname,
            node_type=node_type,
            **kwargs
        )
        
        # Add interfaces
        for iface_data in (interfaces or []):
            iface = NetworkInterface(
                interface_id=f"iface_{uuid.uuid4().hex[:8]}",
                **iface_data
            )
            node.interfaces.append(iface)
            
        self.nodes[node.node_id] = node
        return node
        
    def add_connection(self, node1_id: str, node2_id: str) -> bool:
        """Добавление соединения"""
        if node1_id in self.nodes and node2_id in self.nodes:
            self.connections.append((node1_id, node2_id))
            return True
        return False
        
    def get_topology(self) -> Dict[str, Any]:
        """Получить топологию"""
        return {
            "nodes": [
                {
                    "id": n.node_id,
                    "hostname": n.hostname,
                    "type": n.node_type,
                    "interfaces": len(n.interfaces),
                    "online": n.online
                }
                for n in self.nodes.values()
            ],
            "connections": self.connections
        }


class LatencyMonitor:
    """Монитор задержек"""
    
    def __init__(self):
        self.probes: Dict[str, LatencyProbe] = {}
        self.measurements: Dict[str, List[float]] = defaultdict(list)
        
    def create_probe(self, name: str, target_ip: str, target_port: int,
                      protocol: Protocol = Protocol.TCP, **kwargs) -> LatencyProbe:
        """Создание пробы"""
        probe = LatencyProbe(
            probe_id=f"probe_{uuid.uuid4().hex[:8]}",
            name=name,
            target_ip=target_ip,
            target_port=target_port,
            protocol=protocol,
            **kwargs
        )
        self.probes[probe.probe_id] = probe
        return probe
        
    async def measure(self, probe_id: str) -> Dict[str, Any]:
        """Измерение"""
        probe = self.probes.get(probe_id)
        if not probe:
            return {"error": "Probe not found"}
            
        # Simulate measurement
        await asyncio.sleep(0.01)
        
        # Generate latency with some variation
        base_latency = random.uniform(5, 50)
        latency = base_latency + random.gauss(0, 5)
        latency = max(1, latency)
        
        success = random.random() > 0.02
        
        if success:
            probe.success_count += 1
            probe.last_latency_ms = latency
            
            # Update stats
            measurements = self.measurements[probe_id]
            measurements.append(latency)
            if len(measurements) > 100:
                measurements.pop(0)
                
            probe.avg_latency_ms = sum(measurements) / len(measurements)
            probe.max_latency_ms = max(measurements)
            probe.min_latency_ms = min(measurements)
        else:
            probe.failure_count += 1
            
        # Check thresholds
        status = "ok"
        if latency > probe.critical_threshold_ms:
            status = "critical"
        elif latency > probe.warning_threshold_ms:
            status = "warning"
            
        return {
            "probe_id": probe_id,
            "latency_ms": latency if success else None,
            "success": success,
            "status": status
        }


class BandwidthMonitor:
    """Монитор пропускной способности"""
    
    def __init__(self):
        self.history: Dict[str, List[Dict]] = defaultdict(list)
        
    def record(self, interface_id: str, bytes_in: int, bytes_out: int,
                interval_seconds: int = 60) -> Dict[str, float]:
        """Запись метрик"""
        history = self.history[interface_id]
        
        # Calculate rate
        if history:
            last = history[-1]
            time_diff = interval_seconds
            
            bytes_in_diff = bytes_in - last["bytes_in"]
            bytes_out_diff = bytes_out - last["bytes_out"]
            
            rate_in_mbps = (bytes_in_diff * 8) / (time_diff * 1_000_000)
            rate_out_mbps = (bytes_out_diff * 8) / (time_diff * 1_000_000)
        else:
            rate_in_mbps = 0
            rate_out_mbps = 0
            
        # Store
        history.append({
            "timestamp": datetime.now(),
            "bytes_in": bytes_in,
            "bytes_out": bytes_out,
            "rate_in_mbps": rate_in_mbps,
            "rate_out_mbps": rate_out_mbps
        })
        
        # Keep recent
        if len(history) > 1440:  # 24 hours at 1-minute intervals
            self.history[interface_id] = history[-720:]
            
        return {
            "rate_in_mbps": rate_in_mbps,
            "rate_out_mbps": rate_out_mbps,
            "total_mbps": rate_in_mbps + rate_out_mbps
        }
        
    def get_utilization(self, interface_id: str, capacity_mbps: int) -> float:
        """Получить утилизацию"""
        history = self.history.get(interface_id, [])
        if not history:
            return 0.0
            
        last = history[-1]
        total_rate = last["rate_in_mbps"] + last["rate_out_mbps"]
        return (total_rate / capacity_mbps * 100) if capacity_mbps > 0 else 0


class AnomalyDetector:
    """Детектор аномалий"""
    
    def __init__(self, flow_collector: FlowCollector, latency_monitor: LatencyMonitor):
        self.flow_collector = flow_collector
        self.latency_monitor = latency_monitor
        self.anomalies: List[NetworkAnomaly] = []
        self.baselines: Dict[str, float] = {}
        
    def set_baseline(self, metric: str, value: float) -> None:
        """Установка baseline"""
        self.baselines[metric] = value
        
    def detect(self) -> List[NetworkAnomaly]:
        """Обнаружение аномалий"""
        detected = []
        
        # Check latency
        for probe in self.latency_monitor.probes.values():
            if probe.last_latency_ms > probe.critical_threshold_ms:
                anomaly = NetworkAnomaly(
                    anomaly_id=f"anom_{uuid.uuid4().hex[:8]}",
                    anomaly_type=AnomalyType.HIGH_LATENCY,
                    severity=AlertSeverity.CRITICAL,
                    source=probe.target_ip,
                    description=f"High latency to {probe.name}",
                    observed_value=probe.last_latency_ms,
                    expected_value=probe.warning_threshold_ms,
                    deviation_percent=((probe.last_latency_ms - probe.warning_threshold_ms) / probe.warning_threshold_ms) * 100
                )
                detected.append(anomaly)
                
        # Check flows for anomalies
        flows = self.flow_collector.get_flows(minutes=5)
        
        # Connection flood detection
        src_connections = defaultdict(int)
        for flow in flows:
            src_connections[flow.src_ip] += 1
            
        for ip, count in src_connections.items():
            if count > 1000:  # Threshold
                anomaly = NetworkAnomaly(
                    anomaly_id=f"anom_{uuid.uuid4().hex[:8]}",
                    anomaly_type=AnomalyType.CONNECTION_FLOOD,
                    severity=AlertSeverity.WARNING,
                    source=ip,
                    description=f"High connection count from {ip}",
                    observed_value=count,
                    expected_value=100,
                    deviation_percent=((count - 100) / 100) * 100
                )
                detected.append(anomaly)
                
        self.anomalies.extend(detected)
        return detected


class TopTalkersAnalyzer:
    """Анализатор топ источников"""
    
    def __init__(self, flow_collector: FlowCollector):
        self.flow_collector = flow_collector
        
    def get_top_talkers(self, minutes: int = 5, limit: int = 10) -> List[TopTalker]:
        """Получить топ источников"""
        flows = self.flow_collector.get_flows(minutes)
        
        # Aggregate by source IP
        by_ip: Dict[str, TopTalker] = {}
        
        for flow in flows:
            if flow.src_ip not in by_ip:
                by_ip[flow.src_ip] = TopTalker(ip_address=flow.src_ip)
                
            talker = by_ip[flow.src_ip]
            talker.bytes_total += flow.bytes
            talker.packets_total += flow.packets
            talker.connections += 1
            
            proto = flow.protocol.value
            talker.protocols[proto] = talker.protocols.get(proto, 0) + flow.bytes
            
        # Sort by bytes
        sorted_talkers = sorted(by_ip.values(), key=lambda t: t.bytes_total, reverse=True)
        return sorted_talkers[:limit]


class NetworkObservabilityPlatform:
    """Платформа сетевой наблюдаемости"""
    
    def __init__(self):
        self.flow_collector = FlowCollector()
        self.network_mapper = NetworkMapper()
        self.latency_monitor = LatencyMonitor()
        self.bandwidth_monitor = BandwidthMonitor()
        self.anomaly_detector = AnomalyDetector(self.flow_collector, self.latency_monitor)
        self.top_talkers = TopTalkersAnalyzer(self.flow_collector)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        flows = self.flow_collector.get_flows(minutes=60)
        
        total_bytes = sum(f.bytes for f in flows)
        total_packets = sum(f.packets for f in flows)
        
        return {
            "nodes": len(self.network_mapper.nodes),
            "connections": len(self.network_mapper.connections),
            "probes": len(self.latency_monitor.probes),
            "flows_last_hour": len(flows),
            "bytes_last_hour": total_bytes,
            "packets_last_hour": total_packets,
            "active_anomalies": len([a for a in self.anomaly_detector.anomalies if not a.resolved_at])
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 124: Network Observability Platform")
    print("=" * 60)
    
    async def demo():
        platform = NetworkObservabilityPlatform()
        print("✓ Network Observability Platform created")
        
        # Build network topology
        print("\n🌐 Building Network Topology...")
        
        nodes_data = [
            ("router-core-1", "router", [{"name": "eth0", "ip_address": "10.0.0.1"}]),
            ("router-core-2", "router", [{"name": "eth0", "ip_address": "10.0.0.2"}]),
            ("switch-access-1", "switch", [{"name": "eth0", "ip_address": "10.0.1.1"}]),
            ("switch-access-2", "switch", [{"name": "eth0", "ip_address": "10.0.2.1"}]),
            ("firewall-1", "firewall", [{"name": "eth0", "ip_address": "10.0.0.254"}]),
            ("web-server-1", "server", [{"name": "eth0", "ip_address": "10.0.1.10"}]),
            ("web-server-2", "server", [{"name": "eth0", "ip_address": "10.0.1.11"}]),
            ("db-server-1", "server", [{"name": "eth0", "ip_address": "10.0.2.10"}]),
            ("app-server-1", "server", [{"name": "eth0", "ip_address": "10.0.1.20"}])
        ]
        
        created_nodes = {}
        for hostname, node_type, interfaces in nodes_data:
            node = platform.network_mapper.add_node(hostname, node_type, interfaces)
            created_nodes[hostname] = node
            icon = {"router": "🔀", "switch": "🔌", "firewall": "🛡️", "server": "🖥️"}.get(node_type, "●")
            print(f"  {icon} {hostname} ({node_type})")
            
        # Add connections
        connections = [
            ("router-core-1", "router-core-2"),
            ("router-core-1", "switch-access-1"),
            ("router-core-2", "switch-access-2"),
            ("router-core-1", "firewall-1"),
            ("switch-access-1", "web-server-1"),
            ("switch-access-1", "web-server-2"),
            ("switch-access-1", "app-server-1"),
            ("switch-access-2", "db-server-1")
        ]
        
        for node1, node2 in connections:
            platform.network_mapper.add_connection(
                created_nodes[node1].node_id,
                created_nodes[node2].node_id
            )
            
        print(f"\n  Connections: {len(connections)}")
        
        # Create latency probes
        print("\n📡 Creating Latency Probes...")
        
        probes_data = [
            ("Web Server 1", "10.0.1.10", 80, Protocol.HTTP),
            ("Web Server 2", "10.0.1.11", 443, Protocol.HTTPS),
            ("Database", "10.0.2.10", 5432, Protocol.TCP),
            ("DNS", "10.0.0.254", 53, Protocol.DNS),
            ("External API", "8.8.8.8", 443, Protocol.HTTPS)
        ]
        
        created_probes = []
        for name, ip, port, proto in probes_data:
            probe = platform.latency_monitor.create_probe(name, ip, port, proto)
            created_probes.append(probe)
            print(f"  ✓ {name} ({ip}:{port})")
            
        # Run latency measurements
        print("\n⏱️ Running Latency Measurements...")
        
        for probe in created_probes:
            results = []
            for _ in range(5):
                result = await platform.latency_monitor.measure(probe.probe_id)
                if result.get("success"):
                    results.append(result["latency_ms"])
                    
            avg = sum(results) / len(results) if results else 0
            status_icon = "🟢" if avg < 50 else "🟡" if avg < 100 else "🔴"
            print(f"  {status_icon} {probe.name}: {avg:.2f}ms avg")
            
        # Simulate flow collection
        print("\n📊 Collecting Network Flows...")
        
        protocols = [Protocol.TCP, Protocol.UDP, Protocol.HTTP, Protocol.HTTPS, Protocol.DNS]
        
        for _ in range(500):
            src_ip = f"10.0.{random.randint(1,2)}.{random.randint(10,100)}"
            dst_ip = f"10.0.{random.randint(1,2)}.{random.randint(10,100)}"
            
            platform.flow_collector.collect(
                src_ip=src_ip,
                dst_ip=dst_ip,
                protocol=random.choice(protocols),
                bytes_count=random.randint(100, 100000),
                packets=random.randint(1, 100),
                latency_ms=random.uniform(1, 50)
            )
            
        flows = platform.flow_collector.get_flows(minutes=5)
        print(f"  Collected: {len(flows)} flows")
        
        # Protocol breakdown
        print("\n📈 Traffic by Protocol:")
        
        by_protocol = platform.flow_collector.aggregate_by_protocol(minutes=5)
        total_bytes = sum(p["bytes"] for p in by_protocol.values())
        
        for proto, stats in sorted(by_protocol.items(), key=lambda x: x[1]["bytes"], reverse=True):
            pct = (stats["bytes"] / total_bytes * 100) if total_bytes > 0 else 0
            bar = "█" * int(pct / 5)
            print(f"  {proto:8}: {bar} {pct:.1f}% ({stats['bytes'] / 1024:.1f} KB)")
            
        # Bandwidth monitoring
        print("\n📶 Bandwidth Utilization:")
        
        for node in list(created_nodes.values())[:4]:
            if node.interfaces:
                iface = node.interfaces[0]
                
                # Simulate traffic
                iface.bytes_in += random.randint(1000000, 10000000)
                iface.bytes_out += random.randint(500000, 5000000)
                
                rates = platform.bandwidth_monitor.record(
                    iface.interface_id,
                    iface.bytes_in,
                    iface.bytes_out
                )
                
                util = platform.bandwidth_monitor.get_utilization(iface.interface_id, iface.speed_mbps)
                bar = "█" * int(util / 5) + "░" * (20 - int(util / 5))
                print(f"  {node.hostname}: [{bar}] {util:.1f}%")
                
        # Top talkers
        print("\n🏆 Top Talkers:")
        
        top = platform.top_talkers.get_top_talkers(minutes=5, limit=5)
        for i, talker in enumerate(top, 1):
            print(f"  {i}. {talker.ip_address}: {talker.bytes_total / 1024:.1f} KB, {talker.connections} connections")
            
        # Anomaly detection
        print("\n🔍 Anomaly Detection...")
        
        # Create some anomalies
        for probe in created_probes[:2]:
            probe.last_latency_ms = random.uniform(200, 600)  # High latency
            
        anomalies = platform.anomaly_detector.detect()
        
        if anomalies:
            for anom in anomalies:
                icon = {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(anom.severity.value, "⚪")
                print(f"  {icon} {anom.anomaly_type.value}: {anom.description}")
                print(f"     Observed: {anom.observed_value:.1f}, Expected: {anom.expected_value:.1f}")
        else:
            print("  ✅ No anomalies detected")
            
        # Network topology summary
        print("\n🗺️ Network Topology:")
        
        topology = platform.network_mapper.get_topology()
        by_type = defaultdict(int)
        for node in topology["nodes"]:
            by_type[node["type"]] += 1
            
        for ntype, count in by_type.items():
            icon = {"router": "🔀", "switch": "🔌", "firewall": "🛡️", "server": "🖥️"}.get(ntype, "●")
            print(f"  {icon} {ntype}s: {count}")
            
        print(f"  🔗 Connections: {len(topology['connections'])}")
        
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Network:")
        print(f"    Nodes: {stats['nodes']}")
        print(f"    Connections: {stats['connections']}")
        print(f"    Probes: {stats['probes']}")
        
        print(f"\n  Traffic (last hour):")
        print(f"    Flows: {stats['flows_last_hour']}")
        print(f"    Bytes: {stats['bytes_last_hour'] / (1024*1024):.2f} MB")
        print(f"    Packets: {stats['packets_last_hour']}")
        
        print(f"\n  Alerts:")
        print(f"    Active Anomalies: {stats['active_anomalies']}")
        
        # Dashboard
        print("\n📋 Network Observability Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │            Network Observability Overview                   │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Network Nodes:      {stats['nodes']:>10}                        │")
        print(f"  │ Connections:        {stats['connections']:>10}                        │")
        print(f"  │ Latency Probes:     {stats['probes']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Flows (1h):         {stats['flows_last_hour']:>10}                        │")
        bytes_mb = stats['bytes_last_hour'] / (1024*1024)
        print(f"  │ Traffic (1h):       {bytes_mb:>10.2f} MB                   │")
        print(f"  │ Active Anomalies:   {stats['active_anomalies']:>10}                        │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Network Observability Platform initialized!")
    print("=" * 60)
