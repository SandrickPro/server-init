#!/usr/bin/env python3
"""
Server Init - Iteration 321: Network Manager Platform
Платформа управления сетевой инфраструктурой

Функционал:
- Network Topology - топология сети
- VLAN Management - управление VLAN
- Firewall Rules - правила файрвола
- VPN Management - управление VPN
- IP Address Management (IPAM) - управление IP адресами
- Traffic Analysis - анализ трафика
- QoS Policies - политики QoS
- Network Monitoring - мониторинг сети
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class DeviceType(Enum):
    """Тип сетевого устройства"""
    ROUTER = "router"
    SWITCH = "switch"
    FIREWALL = "firewall"
    LOAD_BALANCER = "load_balancer"
    ACCESS_POINT = "access_point"
    VPN_GATEWAY = "vpn_gateway"


class DeviceStatus(Enum):
    """Статус устройства"""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"


class InterfaceType(Enum):
    """Тип интерфейса"""
    ETHERNET = "ethernet"
    FIBER = "fiber"
    WIFI = "wifi"
    VLAN = "vlan"
    TUNNEL = "tunnel"


class FirewallAction(Enum):
    """Действие файрвола"""
    ALLOW = "allow"
    DENY = "deny"
    DROP = "drop"
    LOG = "log"


class VPNType(Enum):
    """Тип VPN"""
    SITE_TO_SITE = "site_to_site"
    CLIENT_TO_SITE = "client_to_site"
    SSL_VPN = "ssl_vpn"
    IPSEC = "ipsec"
    WIREGUARD = "wireguard"


class TrafficDirection(Enum):
    """Направление трафика"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BOTH = "both"


@dataclass
class NetworkInterface:
    """Сетевой интерфейс"""
    interface_id: str
    device_id: str
    
    # Name
    name: str = ""
    
    # Type
    interface_type: InterfaceType = InterfaceType.ETHERNET
    
    # IP
    ip_address: str = ""
    subnet_mask: str = "255.255.255.0"
    gateway: str = ""
    
    # MAC
    mac_address: str = ""
    
    # VLAN
    vlan_id: int = 0
    
    # Speed
    speed_mbps: int = 1000
    
    # Status
    is_up: bool = True
    is_connected: bool = True
    
    # Traffic stats
    rx_bytes: int = 0
    tx_bytes: int = 0
    rx_packets: int = 0
    tx_packets: int = 0
    errors: int = 0


@dataclass
class NetworkDevice:
    """Сетевое устройство"""
    device_id: str
    name: str
    
    # Type
    device_type: DeviceType = DeviceType.SWITCH
    
    # Model
    model: str = ""
    vendor: str = ""
    firmware_version: str = ""
    
    # Status
    status: DeviceStatus = DeviceStatus.ONLINE
    
    # Management
    management_ip: str = ""
    
    # Location
    location: str = ""
    rack: str = ""
    
    # Interfaces
    interface_ids: List[str] = field(default_factory=list)
    
    # Uptime
    uptime_seconds: int = 0
    
    # Performance
    cpu_percent: float = 0
    memory_percent: float = 0
    
    # Timestamps
    last_seen: datetime = field(default_factory=datetime.now)


@dataclass
class VLAN:
    """VLAN"""
    vlan_id: int
    name: str
    
    # Description
    description: str = ""
    
    # Network
    network: str = ""  # e.g., "192.168.10.0/24"
    gateway: str = ""
    
    # DHCP
    dhcp_enabled: bool = True
    dhcp_range_start: str = ""
    dhcp_range_end: str = ""
    
    # Status
    is_active: bool = True
    
    # Devices
    member_device_ids: List[str] = field(default_factory=list)


@dataclass
class Subnet:
    """Подсеть"""
    subnet_id: str
    
    # Network
    network: str = ""  # CIDR notation
    
    # VLAN
    vlan_id: int = 0
    
    # Gateway
    gateway: str = ""
    
    # DNS
    dns_servers: List[str] = field(default_factory=list)
    
    # Description
    description: str = ""
    
    # Usage
    total_addresses: int = 0
    used_addresses: int = 0
    reserved_addresses: int = 0


@dataclass
class IPAddress:
    """IP адрес"""
    ip_id: str
    
    # Address
    address: str = ""
    
    # Subnet
    subnet_id: str = ""
    
    # Assignment
    assignment_type: str = "dhcp"  # dhcp, static, reserved
    assigned_to: str = ""  # hostname or device
    
    # MAC
    mac_address: str = ""
    
    # Status
    is_allocated: bool = False
    
    # Timestamps
    allocated_at: Optional[datetime] = None
    lease_expires: Optional[datetime] = None


@dataclass
class FirewallRule:
    """Правило файрвола"""
    rule_id: str
    name: str
    
    # Priority
    priority: int = 100
    
    # Source
    source_network: str = "any"
    source_port: str = "any"
    
    # Destination
    dest_network: str = "any"
    dest_port: str = "any"
    
    # Protocol
    protocol: str = "any"  # tcp, udp, icmp, any
    
    # Action
    action: FirewallAction = FirewallAction.ALLOW
    
    # Direction
    direction: TrafficDirection = TrafficDirection.BOTH
    
    # Logging
    log_enabled: bool = False
    
    # Status
    is_enabled: bool = True
    
    # Stats
    hit_count: int = 0


@dataclass
class VPNTunnel:
    """VPN туннель"""
    tunnel_id: str
    name: str
    
    # Type
    vpn_type: VPNType = VPNType.SITE_TO_SITE
    
    # Endpoints
    local_endpoint: str = ""
    remote_endpoint: str = ""
    
    # Networks
    local_networks: List[str] = field(default_factory=list)
    remote_networks: List[str] = field(default_factory=list)
    
    # Encryption
    encryption_algorithm: str = "AES-256"
    authentication: str = "SHA256"
    
    # Status
    is_up: bool = True
    
    # Stats
    bytes_in: int = 0
    bytes_out: int = 0
    
    # Timestamps
    established_at: Optional[datetime] = None


@dataclass
class QoSPolicy:
    """Политика QoS"""
    policy_id: str
    name: str
    
    # Match criteria
    source_network: str = "any"
    dest_network: str = "any"
    protocol: str = "any"
    dest_port: str = "any"
    
    # Priority
    priority: int = 0  # 0-7, higher = more important
    
    # Bandwidth
    guaranteed_bandwidth_mbps: int = 0
    max_bandwidth_mbps: int = 0
    
    # DSCP marking
    dscp_value: int = 0
    
    # Status
    is_enabled: bool = True


@dataclass
class TrafficFlow:
    """Поток трафика"""
    flow_id: str
    
    # Source/Destination
    source_ip: str = ""
    dest_ip: str = ""
    source_port: int = 0
    dest_port: int = 0
    protocol: str = ""
    
    # Device
    device_id: str = ""
    interface_id: str = ""
    
    # Volume
    bytes: int = 0
    packets: int = 0
    
    # Timestamps
    start_time: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)


class NetworkManager:
    """Менеджер сети"""
    
    def __init__(self):
        self.devices: Dict[str, NetworkDevice] = {}
        self.interfaces: Dict[str, NetworkInterface] = {}
        self.vlans: Dict[int, VLAN] = {}
        self.subnets: Dict[str, Subnet] = {}
        self.ip_addresses: Dict[str, IPAddress] = {}
        self.firewall_rules: Dict[str, FirewallRule] = {}
        self.vpn_tunnels: Dict[str, VPNTunnel] = {}
        self.qos_policies: Dict[str, QoSPolicy] = {}
        self.traffic_flows: List[TrafficFlow] = []
        
    async def add_device(self, name: str,
                        device_type: DeviceType,
                        management_ip: str,
                        model: str = "",
                        vendor: str = "",
                        location: str = "") -> NetworkDevice:
        """Добавление устройства"""
        device = NetworkDevice(
            device_id=f"dev_{uuid.uuid4().hex[:8]}",
            name=name,
            device_type=device_type,
            management_ip=management_ip,
            model=model,
            vendor=vendor,
            location=location,
            uptime_seconds=random.randint(0, 86400 * 30)
        )
        
        self.devices[device.device_id] = device
        return device
        
    async def add_interface(self, device_id: str,
                           name: str,
                           interface_type: InterfaceType = InterfaceType.ETHERNET,
                           ip_address: str = "",
                           vlan_id: int = 0,
                           speed_mbps: int = 1000) -> Optional[NetworkInterface]:
        """Добавление интерфейса"""
        device = self.devices.get(device_id)
        if not device:
            return None
            
        interface = NetworkInterface(
            interface_id=f"if_{uuid.uuid4().hex[:8]}",
            device_id=device_id,
            name=name,
            interface_type=interface_type,
            ip_address=ip_address,
            vlan_id=vlan_id,
            speed_mbps=speed_mbps,
            mac_address=":".join([f"{random.randint(0, 255):02x}" for _ in range(6)])
        )
        
        self.interfaces[interface.interface_id] = interface
        device.interface_ids.append(interface.interface_id)
        
        return interface
        
    async def create_vlan(self, vlan_id: int,
                         name: str,
                         network: str,
                         gateway: str,
                         dhcp_enabled: bool = True) -> VLAN:
        """Создание VLAN"""
        vlan = VLAN(
            vlan_id=vlan_id,
            name=name,
            network=network,
            gateway=gateway,
            dhcp_enabled=dhcp_enabled
        )
        
        if dhcp_enabled:
            # Generate DHCP range from network
            base = network.split("/")[0].rsplit(".", 1)[0]
            vlan.dhcp_range_start = f"{base}.100"
            vlan.dhcp_range_end = f"{base}.250"
            
        self.vlans[vlan_id] = vlan
        return vlan
        
    async def create_subnet(self, network: str,
                           vlan_id: int = 0,
                           gateway: str = "",
                           dns_servers: List[str] = None,
                           description: str = "") -> Subnet:
        """Создание подсети"""
        # Calculate total addresses from CIDR
        cidr = int(network.split("/")[1]) if "/" in network else 24
        total_addresses = 2 ** (32 - cidr) - 2  # Exclude network and broadcast
        
        subnet = Subnet(
            subnet_id=f"subnet_{uuid.uuid4().hex[:8]}",
            network=network,
            vlan_id=vlan_id,
            gateway=gateway,
            dns_servers=dns_servers or ["8.8.8.8", "8.8.4.4"],
            description=description,
            total_addresses=total_addresses
        )
        
        self.subnets[subnet.subnet_id] = subnet
        return subnet
        
    async def allocate_ip(self, subnet_id: str,
                         assignment_type: str = "dhcp",
                         assigned_to: str = "",
                         mac_address: str = "") -> Optional[IPAddress]:
        """Выделение IP адреса"""
        subnet = self.subnets.get(subnet_id)
        if not subnet:
            return None
            
        if subnet.used_addresses >= subnet.total_addresses:
            return None
            
        # Generate IP (simplified)
        base = subnet.network.split("/")[0].rsplit(".", 1)[0]
        host = subnet.used_addresses + 10  # Start from .10
        address = f"{base}.{host}"
        
        ip = IPAddress(
            ip_id=f"ip_{uuid.uuid4().hex[:8]}",
            address=address,
            subnet_id=subnet_id,
            assignment_type=assignment_type,
            assigned_to=assigned_to,
            mac_address=mac_address,
            is_allocated=True,
            allocated_at=datetime.now()
        )
        
        if assignment_type == "dhcp":
            ip.lease_expires = datetime.now() + timedelta(hours=24)
            
        self.ip_addresses[ip.ip_id] = ip
        subnet.used_addresses += 1
        
        return ip
        
    async def create_firewall_rule(self, name: str,
                                   source_network: str = "any",
                                   dest_network: str = "any",
                                   dest_port: str = "any",
                                   protocol: str = "any",
                                   action: FirewallAction = FirewallAction.ALLOW,
                                   priority: int = 100,
                                   log_enabled: bool = False) -> FirewallRule:
        """Создание правила файрвола"""
        rule = FirewallRule(
            rule_id=f"fw_{uuid.uuid4().hex[:8]}",
            name=name,
            source_network=source_network,
            dest_network=dest_network,
            dest_port=dest_port,
            protocol=protocol,
            action=action,
            priority=priority,
            log_enabled=log_enabled
        )
        
        self.firewall_rules[rule.rule_id] = rule
        return rule
        
    async def create_vpn_tunnel(self, name: str,
                               vpn_type: VPNType,
                               local_endpoint: str,
                               remote_endpoint: str,
                               local_networks: List[str],
                               remote_networks: List[str]) -> VPNTunnel:
        """Создание VPN туннеля"""
        tunnel = VPNTunnel(
            tunnel_id=f"vpn_{uuid.uuid4().hex[:8]}",
            name=name,
            vpn_type=vpn_type,
            local_endpoint=local_endpoint,
            remote_endpoint=remote_endpoint,
            local_networks=local_networks,
            remote_networks=remote_networks,
            established_at=datetime.now()
        )
        
        self.vpn_tunnels[tunnel.tunnel_id] = tunnel
        return tunnel
        
    async def create_qos_policy(self, name: str,
                               dest_port: str = "any",
                               protocol: str = "any",
                               priority: int = 0,
                               guaranteed_bw: int = 0,
                               max_bw: int = 0) -> QoSPolicy:
        """Создание политики QoS"""
        policy = QoSPolicy(
            policy_id=f"qos_{uuid.uuid4().hex[:8]}",
            name=name,
            dest_port=dest_port,
            protocol=protocol,
            priority=priority,
            guaranteed_bandwidth_mbps=guaranteed_bw,
            max_bandwidth_mbps=max_bw
        )
        
        self.qos_policies[policy.policy_id] = policy
        return policy
        
    async def update_traffic_stats(self):
        """Обновление статистики трафика"""
        for interface in self.interfaces.values():
            if interface.is_up and interface.is_connected:
                interface.rx_bytes += random.randint(100000, 10000000)
                interface.tx_bytes += random.randint(100000, 10000000)
                interface.rx_packets += random.randint(100, 10000)
                interface.tx_packets += random.randint(100, 10000)
                interface.errors += random.randint(0, 5)
                
        for device in self.devices.values():
            if device.status == DeviceStatus.ONLINE:
                device.cpu_percent = random.uniform(5, 80)
                device.memory_percent = random.uniform(20, 70)
                device.last_seen = datetime.now()
                
        for vpn in self.vpn_tunnels.values():
            if vpn.is_up:
                vpn.bytes_in += random.randint(10000, 1000000)
                vpn.bytes_out += random.randint(10000, 1000000)
                
        for rule in self.firewall_rules.values():
            if rule.is_enabled:
                rule.hit_count += random.randint(0, 1000)
                
    async def simulate_traffic_flows(self, count: int = 10):
        """Симуляция потоков трафика"""
        protocols = ["tcp", "udp", "icmp"]
        common_ports = [22, 80, 443, 3306, 5432, 8080]
        
        for _ in range(count):
            flow = TrafficFlow(
                flow_id=f"flow_{uuid.uuid4().hex[:8]}",
                source_ip=f"192.168.{random.randint(1, 100)}.{random.randint(1, 254)}",
                dest_ip=f"10.0.{random.randint(1, 10)}.{random.randint(1, 254)}",
                source_port=random.randint(30000, 65535),
                dest_port=random.choice(common_ports),
                protocol=random.choice(protocols),
                bytes=random.randint(1000, 1000000),
                packets=random.randint(10, 10000)
            )
            
            self.traffic_flows.append(flow)
            
    def get_topology(self) -> Dict[str, Any]:
        """Получение топологии сети"""
        nodes = []
        links = []
        
        for device in self.devices.values():
            nodes.append({
                "id": device.device_id,
                "name": device.name,
                "type": device.device_type.value,
                "status": device.status.value,
                "ip": device.management_ip
            })
            
        # Simplified link detection (devices on same VLAN)
        for vlan in self.vlans.values():
            members = vlan.member_device_ids
            for i, dev1 in enumerate(members):
                for dev2 in members[i+1:]:
                    links.append({
                        "source": dev1,
                        "target": dev2,
                        "vlan": vlan.vlan_id
                    })
                    
        return {
            "nodes": nodes,
            "links": links,
            "vlans": len(self.vlans),
            "devices": len(self.devices)
        }
        
    def get_ipam_summary(self) -> Dict[str, Any]:
        """Сводка IPAM"""
        summary = {
            "subnets": [],
            "total_addresses": 0,
            "used_addresses": 0,
            "reserved_addresses": 0
        }
        
        for subnet in self.subnets.values():
            used_pct = (subnet.used_addresses / subnet.total_addresses * 100) if subnet.total_addresses > 0 else 0
            
            summary["subnets"].append({
                "network": subnet.network,
                "vlan_id": subnet.vlan_id,
                "total": subnet.total_addresses,
                "used": subnet.used_addresses,
                "reserved": subnet.reserved_addresses,
                "available": subnet.total_addresses - subnet.used_addresses - subnet.reserved_addresses,
                "used_percent": used_pct
            })
            
            summary["total_addresses"] += subnet.total_addresses
            summary["used_addresses"] += subnet.used_addresses
            summary["reserved_addresses"] += subnet.reserved_addresses
            
        return summary
        
    def get_traffic_analysis(self) -> Dict[str, Any]:
        """Анализ трафика"""
        by_protocol = {}
        by_port = {}
        top_talkers = {}
        
        for flow in self.traffic_flows:
            # By protocol
            by_protocol[flow.protocol] = by_protocol.get(flow.protocol, 0) + flow.bytes
            
            # By port
            port = str(flow.dest_port)
            by_port[port] = by_port.get(port, 0) + flow.bytes
            
            # Top talkers
            top_talkers[flow.source_ip] = top_talkers.get(flow.source_ip, 0) + flow.bytes
            
        # Sort
        top_ports = sorted(by_port.items(), key=lambda x: x[1], reverse=True)[:10]
        top_sources = sorted(top_talkers.items(), key=lambda x: x[1], reverse=True)[:10]
        
        total_bytes = sum(f.bytes for f in self.traffic_flows)
        
        return {
            "total_flows": len(self.traffic_flows),
            "total_bytes": total_bytes,
            "by_protocol": by_protocol,
            "top_ports": dict(top_ports),
            "top_talkers": dict(top_sources)
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_devices = len(self.devices)
        online_devices = sum(1 for d in self.devices.values() if d.status == DeviceStatus.ONLINE)
        
        by_device_type = {}
        for d in self.devices.values():
            by_device_type[d.device_type.value] = by_device_type.get(d.device_type.value, 0) + 1
            
        total_interfaces = len(self.interfaces)
        up_interfaces = sum(1 for i in self.interfaces.values() if i.is_up)
        
        total_vlans = len(self.vlans)
        active_vlans = sum(1 for v in self.vlans.values() if v.is_active)
        
        total_ips = len(self.ip_addresses)
        allocated_ips = sum(1 for ip in self.ip_addresses.values() if ip.is_allocated)
        
        total_fw_rules = len(self.firewall_rules)
        enabled_rules = sum(1 for r in self.firewall_rules.values() if r.is_enabled)
        
        total_vpns = len(self.vpn_tunnels)
        up_vpns = sum(1 for v in self.vpn_tunnels.values() if v.is_up)
        
        total_rx = sum(i.rx_bytes for i in self.interfaces.values())
        total_tx = sum(i.tx_bytes for i in self.interfaces.values())
        
        return {
            "total_devices": total_devices,
            "online_devices": online_devices,
            "by_device_type": by_device_type,
            "total_interfaces": total_interfaces,
            "up_interfaces": up_interfaces,
            "total_vlans": total_vlans,
            "active_vlans": active_vlans,
            "total_subnets": len(self.subnets),
            "total_ips": total_ips,
            "allocated_ips": allocated_ips,
            "firewall_rules": total_fw_rules,
            "enabled_fw_rules": enabled_rules,
            "total_vpns": total_vpns,
            "up_vpns": up_vpns,
            "qos_policies": len(self.qos_policies),
            "total_rx_gb": total_rx / (1024**3),
            "total_tx_gb": total_tx / (1024**3)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 321: Network Manager Platform")
    print("=" * 60)
    
    net = NetworkManager()
    print("✓ Network Manager created")
    
    # Add network devices
    print("\n📡 Adding Network Devices...")
    
    devices_data = [
        ("Core Router", DeviceType.ROUTER, "10.0.0.1", "Cisco ASR 1000", "Cisco"),
        ("Distribution Switch 1", DeviceType.SWITCH, "10.0.0.2", "Cisco Nexus 9000", "Cisco"),
        ("Distribution Switch 2", DeviceType.SWITCH, "10.0.0.3", "Cisco Nexus 9000", "Cisco"),
        ("Edge Firewall", DeviceType.FIREWALL, "10.0.0.4", "Palo Alto PA-5200", "Palo Alto"),
        ("VPN Gateway", DeviceType.VPN_GATEWAY, "10.0.0.5", "Cisco ASA 5500", "Cisco"),
        ("Load Balancer", DeviceType.LOAD_BALANCER, "10.0.0.6", "F5 BIG-IP", "F5"),
        ("Wireless Controller", DeviceType.ACCESS_POINT, "10.0.0.7", "Cisco 9800", "Cisco")
    ]
    
    devices = []
    for name, d_type, ip, model, vendor in devices_data:
        device = await net.add_device(name, d_type, ip, model, vendor)
        devices.append(device)
        print(f"  📡 {name} ({d_type.value}) - {ip}")
        
    # Add interfaces
    print("\n🔌 Adding Interfaces...")
    
    for device in devices[:3]:
        for i in range(4):
            iface = await net.add_interface(
                device.device_id,
                f"GigabitEthernet0/{i}",
                InterfaceType.ETHERNET,
                f"192.168.{i+1}.1",
                vlan_id=i+1,
                speed_mbps=10000
            )
            
    print(f"  ✓ Added {len(net.interfaces)} interfaces")
    
    # Create VLANs
    print("\n🏷️ Creating VLANs...")
    
    vlans_data = [
        (10, "Management", "10.0.10.0/24", "10.0.10.1"),
        (20, "Servers", "10.0.20.0/24", "10.0.20.1"),
        (30, "Users", "10.0.30.0/24", "10.0.30.1"),
        (40, "Guest", "10.0.40.0/24", "10.0.40.1"),
        (50, "DMZ", "10.0.50.0/24", "10.0.50.1"),
        (100, "VoIP", "10.0.100.0/24", "10.0.100.1")
    ]
    
    vlans = []
    for vlan_id, name, network, gateway in vlans_data:
        vlan = await net.create_vlan(vlan_id, name, network, gateway)
        vlans.append(vlan)
        print(f"  🏷️ VLAN {vlan_id}: {name} ({network})")
        
    # Create subnets
    print("\n🌐 Creating Subnets...")
    
    subnets = []
    for vlan in vlans:
        subnet = await net.create_subnet(
            vlan.network,
            vlan.vlan_id,
            vlan.gateway,
            description=f"Subnet for {vlan.name}"
        )
        subnets.append(subnet)
        
    print(f"  ✓ Created {len(subnets)} subnets")
    
    # Allocate IP addresses
    print("\n🔢 Allocating IP Addresses...")
    
    for subnet in subnets[:3]:
        for i in range(5):
            ip = await net.allocate_ip(
                subnet.subnet_id,
                "static" if i < 2 else "dhcp",
                f"host-{i+1}"
            )
            
    print(f"  ✓ Allocated {len(net.ip_addresses)} IP addresses")
    
    # Create firewall rules
    print("\n🔥 Creating Firewall Rules...")
    
    fw_rules_data = [
        ("Allow SSH", "any", "10.0.10.0/24", "22", "tcp", FirewallAction.ALLOW, 100),
        ("Allow HTTPS", "any", "any", "443", "tcp", FirewallAction.ALLOW, 110),
        ("Allow HTTP", "any", "any", "80", "tcp", FirewallAction.ALLOW, 120),
        ("Block Telnet", "any", "any", "23", "tcp", FirewallAction.DROP, 50),
        ("Allow DNS", "any", "any", "53", "udp", FirewallAction.ALLOW, 130),
        ("Allow ICMP", "any", "any", "any", "icmp", FirewallAction.ALLOW, 140),
        ("Block All Other", "any", "any", "any", "any", FirewallAction.DENY, 999)
    ]
    
    fw_rules = []
    for name, src, dest, port, proto, action, prio in fw_rules_data:
        rule = await net.create_firewall_rule(name, src, dest, port, proto, action, prio)
        fw_rules.append(rule)
        action_icon = {"allow": "✓", "deny": "✗", "drop": "⊘"}.get(action.value, "?")
        print(f"  [{action_icon}] {name}: {proto}/{port}")
        
    # Create VPN tunnels
    print("\n🔐 Creating VPN Tunnels...")
    
    vpn_data = [
        ("Site-to-Site NYC", VPNType.SITE_TO_SITE, "203.0.113.1", "198.51.100.1", 
         ["10.0.0.0/16"], ["172.16.0.0/16"]),
        ("Site-to-Site LON", VPNType.SITE_TO_SITE, "203.0.113.1", "203.0.113.100",
         ["10.0.0.0/16"], ["192.168.0.0/16"]),
        ("Remote Access VPN", VPNType.CLIENT_TO_SITE, "203.0.113.1", "0.0.0.0",
         ["10.0.0.0/16"], [])
    ]
    
    vpn_tunnels = []
    for name, v_type, local, remote, local_nets, remote_nets in vpn_data:
        vpn = await net.create_vpn_tunnel(name, v_type, local, remote, local_nets, remote_nets)
        vpn_tunnels.append(vpn)
        print(f"  🔐 {name} ({v_type.value})")
        
    # Create QoS policies
    print("\n⚡ Creating QoS Policies...")
    
    qos_data = [
        ("VoIP Traffic", "5060", "udp", 7, 10, 50),
        ("Video Conferencing", "443", "tcp", 6, 20, 100),
        ("Business Apps", "8080", "tcp", 4, 10, 50),
        ("Bulk Transfer", "any", "tcp", 1, 0, 100)
    ]
    
    qos_policies = []
    for name, port, proto, prio, min_bw, max_bw in qos_data:
        policy = await net.create_qos_policy(name, port, proto, prio, min_bw, max_bw)
        qos_policies.append(policy)
        print(f"  ⚡ {name} (Priority {prio})")
        
    # Update stats and simulate traffic
    await net.update_traffic_stats()
    await net.simulate_traffic_flows(50)
    
    # Device status
    print("\n📡 Device Status:")
    
    print("\n  ┌─────────────────────────────┬───────────────┬──────────────┬────────────┬────────────┬──────────────┐")
    print("  │ Device                      │ Type          │ IP           │ Status     │ CPU        │ Memory       │")
    print("  ├─────────────────────────────┼───────────────┼──────────────┼────────────┼────────────┼──────────────┤")
    
    for device in devices:
        name = device.name[:27].ljust(27)
        d_type = device.device_type.value[:13].ljust(13)
        ip = device.management_ip[:12].ljust(12)
        status = device.status.value[:10].ljust(10)
        cpu = f"{device.cpu_percent:.1f}%"[:10].ljust(10)
        mem = f"{device.memory_percent:.1f}%"[:12].ljust(12)
        
        print(f"  │ {name} │ {d_type} │ {ip} │ {status} │ {cpu} │ {mem} │")
        
    print("  └─────────────────────────────┴───────────────┴──────────────┴────────────┴────────────┴──────────────┘")
    
    # VLAN status
    print("\n🏷️ VLAN Status:")
    
    print("\n  ┌──────────┬──────────────────────┬──────────────────────┬─────────────┬────────────────┐")
    print("  │ VLAN ID  │ Name                 │ Network              │ DHCP        │ Status         │")
    print("  ├──────────┼──────────────────────┼──────────────────────┼─────────────┼────────────────┤")
    
    for vlan in vlans:
        vid = str(vlan.vlan_id).ljust(8)
        name = vlan.name[:20].ljust(20)
        network = vlan.network[:20].ljust(20)
        dhcp = ("✓ Enabled" if vlan.dhcp_enabled else "✗ Disabled")[:11].ljust(11)
        status = ("✓ Active" if vlan.is_active else "✗ Inactive")[:14].ljust(14)
        
        print(f"  │ {vid} │ {name} │ {network} │ {dhcp} │ {status} │")
        
    print("  └──────────┴──────────────────────┴──────────────────────┴─────────────┴────────────────┘")
    
    # IPAM Summary
    print("\n🔢 IPAM Summary:")
    
    ipam = net.get_ipam_summary()
    
    print("\n  ┌──────────────────────────┬───────────────┬─────────────────────────────────────────────────────────┐")
    print("  │ Network                  │ VLAN          │ Utilization                                             │")
    print("  ├──────────────────────────┼───────────────┼─────────────────────────────────────────────────────────┤")
    
    for subnet in ipam["subnets"]:
        network = subnet["network"][:24].ljust(24)
        vlan = f"VLAN {subnet['vlan_id']}"[:13].ljust(13)
        
        used_pct = subnet["used_percent"]
        bar = "█" * int(used_pct / 2.5) + "░" * (40 - int(used_pct / 2.5))
        util = f"[{bar}] {used_pct:.0f}%"
        
        print(f"  │ {network} │ {vlan} │ {util} │")
        
    print("  └──────────────────────────┴───────────────┴─────────────────────────────────────────────────────────┘")
    
    print(f"\n  Total Addresses: {ipam['total_addresses']}")
    print(f"  Used: {ipam['used_addresses']}")
    print(f"  Available: {ipam['total_addresses'] - ipam['used_addresses'] - ipam['reserved_addresses']}")
    
    # Firewall rules
    print("\n🔥 Firewall Rules:")
    
    print("\n  ┌───────────────────────┬─────────┬───────────────────────┬──────────┬──────────┬────────────────┐")
    print("  │ Rule                  │ Action  │ Destination           │ Port     │ Protocol │ Hits           │")
    print("  ├───────────────────────┼─────────┼───────────────────────┼──────────┼──────────┼────────────────┤")
    
    for rule in sorted(fw_rules, key=lambda r: r.priority):
        name = rule.name[:21].ljust(21)
        action = rule.action.value[:7].ljust(7)
        dest = rule.dest_network[:21].ljust(21)
        port = rule.dest_port[:8].ljust(8)
        proto = rule.protocol[:8].ljust(8)
        hits = str(rule.hit_count).ljust(14)
        
        print(f"  │ {name} │ {action} │ {dest} │ {port} │ {proto} │ {hits} │")
        
    print("  └───────────────────────┴─────────┴───────────────────────┴──────────┴──────────┴────────────────┘")
    
    # VPN status
    print("\n🔐 VPN Status:")
    
    for vpn in vpn_tunnels:
        status = "✓ UP" if vpn.is_up else "✗ DOWN"
        
        print(f"\n  🔐 {vpn.name} [{status}]")
        print(f"     Type: {vpn.vpn_type.value}")
        print(f"     Local: {vpn.local_endpoint}")
        print(f"     Remote: {vpn.remote_endpoint}")
        print(f"     Encryption: {vpn.encryption_algorithm}")
        print(f"     Traffic: ↓{vpn.bytes_in / (1024**2):.1f} MB / ↑{vpn.bytes_out / (1024**2):.1f} MB")
        
    # Traffic analysis
    print("\n📊 Traffic Analysis:")
    
    traffic = net.get_traffic_analysis()
    
    print(f"\n  Total Flows: {traffic['total_flows']}")
    print(f"  Total Traffic: {traffic['total_bytes'] / (1024**2):.1f} MB")
    
    print("\n  By Protocol:")
    for proto, bytes_count in traffic["by_protocol"].items():
        pct = bytes_count / traffic["total_bytes"] * 100 if traffic["total_bytes"] > 0 else 0
        print(f"    {proto:10} {bytes_count / (1024**2):>8.1f} MB ({pct:.1f}%)")
        
    print("\n  Top Ports:")
    for port, bytes_count in list(traffic["top_ports"].items())[:5]:
        print(f"    Port {port:>5}: {bytes_count / (1024**2):>8.1f} MB")
        
    print("\n  Top Talkers:")
    for ip, bytes_count in list(traffic["top_talkers"].items())[:5]:
        print(f"    {ip:>15}: {bytes_count / (1024**2):>8.1f} MB")
        
    # QoS Policies
    print("\n⚡ QoS Policies:")
    
    for policy in sorted(qos_policies, key=lambda p: p.priority, reverse=True):
        print(f"\n  ⚡ {policy.name} (Priority {policy.priority})")
        print(f"     Match: {policy.protocol}/{policy.dest_port}")
        print(f"     Bandwidth: {policy.guaranteed_bandwidth_mbps}-{policy.max_bandwidth_mbps} Mbps")
        
    # Statistics
    print("\n📊 Network Statistics:")
    
    stats = net.get_statistics()
    
    print(f"\n  Devices: {stats['online_devices']}/{stats['total_devices']} online")
    print("  By Type:")
    for d_type, count in stats['by_device_type'].items():
        print(f"    {d_type}: {count}")
        
    print(f"\n  Interfaces: {stats['up_interfaces']}/{stats['total_interfaces']} up")
    print(f"  VLANs: {stats['active_vlans']}/{stats['total_vlans']} active")
    print(f"  Subnets: {stats['total_subnets']}")
    print(f"  IP Addresses: {stats['allocated_ips']}/{stats['total_ips']} allocated")
    
    print(f"\n  Firewall Rules: {stats['enabled_fw_rules']}/{stats['firewall_rules']} enabled")
    print(f"  VPN Tunnels: {stats['up_vpns']}/{stats['total_vpns']} up")
    print(f"  QoS Policies: {stats['qos_policies']}")
    
    print(f"\n  Total Traffic:")
    print(f"    Received: {stats['total_rx_gb']:.2f} GB")
    print(f"    Transmitted: {stats['total_tx_gb']:.2f} GB")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                      Network Manager Platform                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Devices:               {stats['total_devices']:>12}                          │")
    print(f"│ Online Devices:              {stats['online_devices']:>12}                          │")
    print(f"│ Active VLANs:                {stats['active_vlans']:>12}                          │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ VPN Tunnels Up:              {stats['up_vpns']:>12}                          │")
    print(f"│ Total Traffic:               {(stats['total_rx_gb'] + stats['total_tx_gb']):>10.2f} GB                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Network Manager Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
