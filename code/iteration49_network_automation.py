#!/usr/bin/env python3
"""
Server Init - Iteration 49: Network Automation & SDN
Автоматизация сети и SDN

Функционал:
- Network Topology Management - управление топологией
- Software-Defined Networking - программно-определяемые сети
- Network Policy Engine - движок сетевых политик
- Load Balancer Management - управление балансировщиками
- DNS Management - управление DNS
- VPN & Tunneling - VPN и туннелирование
- Traffic Analysis - анализ трафика
- Network Monitoring - мониторинг сети
"""

import json
import asyncio
import hashlib
import time
import os
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Tuple
from enum import Enum
from abc import ABC, abstractmethod
import random
from collections import defaultdict
import uuid
import ipaddress


class NetworkType(Enum):
    """Тип сети"""
    VPC = "vpc"
    VLAN = "vlan"
    OVERLAY = "overlay"
    UNDERLAY = "underlay"
    BRIDGE = "bridge"


class DeviceType(Enum):
    """Тип устройства"""
    ROUTER = "router"
    SWITCH = "switch"
    FIREWALL = "firewall"
    LOAD_BALANCER = "load_balancer"
    GATEWAY = "gateway"
    HOST = "host"


class PolicyAction(Enum):
    """Действие политики"""
    ALLOW = "allow"
    DENY = "deny"
    DROP = "drop"
    LOG = "log"
    RATE_LIMIT = "rate_limit"


class Protocol(Enum):
    """Протокол"""
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    HTTP = "http"
    HTTPS = "https"
    ANY = "any"


class LoadBalancerAlgorithm(Enum):
    """Алгоритм балансировки"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    IP_HASH = "ip_hash"
    WEIGHTED = "weighted"
    RANDOM = "random"


@dataclass
class IPRange:
    """IP диапазон"""
    cidr: str
    
    @property
    def network(self) -> ipaddress.IPv4Network:
        return ipaddress.ip_network(self.cidr, strict=False)
        
    @property
    def first_ip(self) -> str:
        return str(list(self.network.hosts())[0]) if self.network.num_addresses > 1 else str(self.network.network_address)
        
    @property
    def last_ip(self) -> str:
        hosts = list(self.network.hosts())
        return str(hosts[-1]) if hosts else str(self.network.network_address)


@dataclass
class NetworkInterface:
    """Сетевой интерфейс"""
    interface_id: str
    name: str
    
    # IP адреса
    ip_address: str = ""
    mac_address: str = ""
    
    # Сеть
    network_id: str = ""
    subnet_id: str = ""
    
    # Состояние
    status: str = "up"  # up, down, unknown
    
    # Метрики
    rx_bytes: int = 0
    tx_bytes: int = 0
    rx_packets: int = 0
    tx_packets: int = 0


@dataclass
class Subnet:
    """Подсеть"""
    subnet_id: str
    name: str
    cidr: str
    
    # Сеть
    network_id: str = ""
    
    # Gateway
    gateway: str = ""
    
    # DHCP
    dhcp_enabled: bool = True
    dhcp_start: str = ""
    dhcp_end: str = ""
    
    # DNS
    dns_servers: List[str] = field(default_factory=list)
    
    # Зона доступности
    availability_zone: str = ""


@dataclass
class Network:
    """Сеть"""
    network_id: str
    name: str
    network_type: NetworkType = NetworkType.VPC
    
    # CIDR
    cidr: str = "10.0.0.0/16"
    
    # Подсети
    subnets: List[str] = field(default_factory=list)
    
    # Метаданные
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Состояние
    status: str = "active"
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class NetworkDevice:
    """Сетевое устройство"""
    device_id: str
    name: str
    device_type: DeviceType
    
    # Интерфейсы
    interfaces: List[NetworkInterface] = field(default_factory=list)
    
    # Конфигурация
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Состояние
    status: str = "online"  # online, offline, degraded
    
    # Метрики
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    uptime_seconds: int = 0


@dataclass
class NetworkPolicy:
    """Сетевая политика"""
    policy_id: str
    name: str
    priority: int = 100
    
    # Источник
    source_cidrs: List[str] = field(default_factory=list)
    source_ports: List[int] = field(default_factory=list)
    
    # Назначение
    destination_cidrs: List[str] = field(default_factory=list)
    destination_ports: List[int] = field(default_factory=list)
    
    # Протокол
    protocol: Protocol = Protocol.ANY
    
    # Действие
    action: PolicyAction = PolicyAction.ALLOW
    
    # Опции
    log_enabled: bool = False
    
    # Состояние
    enabled: bool = True
    hits: int = 0


@dataclass
class LoadBalancer:
    """Балансировщик нагрузки"""
    lb_id: str
    name: str
    
    # Frontend
    frontend_ip: str = ""
    frontend_port: int = 80
    
    # Backend
    backend_servers: List[Dict[str, Any]] = field(default_factory=list)
    
    # Алгоритм
    algorithm: LoadBalancerAlgorithm = LoadBalancerAlgorithm.ROUND_ROBIN
    
    # Health check
    health_check_path: str = "/health"
    health_check_interval: int = 30
    
    # Состояние
    status: str = "active"
    
    # Метрики
    active_connections: int = 0
    requests_per_second: float = 0.0


@dataclass
class DNSRecord:
    """DNS запись"""
    record_id: str
    name: str
    record_type: str  # A, AAAA, CNAME, MX, TXT, SRV
    
    # Значение
    value: str = ""
    
    # TTL
    ttl: int = 300
    
    # Приоритет (для MX, SRV)
    priority: Optional[int] = None
    
    # Метаданные
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DNSZone:
    """DNS зона"""
    zone_id: str
    domain: str
    
    # Записи
    records: List[DNSRecord] = field(default_factory=list)
    
    # SOA
    primary_ns: str = ""
    admin_email: str = ""
    
    # Серийный номер
    serial: int = 1
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class VPNTunnel:
    """VPN туннель"""
    tunnel_id: str
    name: str
    
    # Тип
    tunnel_type: str = "ipsec"  # ipsec, wireguard, openvpn
    
    # Endpoints
    local_endpoint: str = ""
    remote_endpoint: str = ""
    
    # Сети
    local_networks: List[str] = field(default_factory=list)
    remote_networks: List[str] = field(default_factory=list)
    
    # Состояние
    status: str = "down"  # up, down, establishing
    
    # Метрики
    rx_bytes: int = 0
    tx_bytes: int = 0


@dataclass
class TrafficFlow:
    """Поток трафика"""
    flow_id: str
    
    # Источник
    src_ip: str = ""
    src_port: int = 0
    
    # Назначение
    dst_ip: str = ""
    dst_port: int = 0
    
    # Протокол
    protocol: Protocol = Protocol.TCP
    
    # Метрики
    bytes: int = 0
    packets: int = 0
    
    # Время
    start_time: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)


class NetworkTopologyManager:
    """Менеджер топологии сети"""
    
    def __init__(self):
        self.networks: Dict[str, Network] = {}
        self.subnets: Dict[str, Subnet] = {}
        self.devices: Dict[str, NetworkDevice] = {}
        self.interfaces: Dict[str, NetworkInterface] = {}
        
    def create_network(self, name: str, cidr: str, 
                        network_type: NetworkType = NetworkType.VPC) -> Network:
        """Создание сети"""
        network = Network(
            network_id=f"net_{uuid.uuid4().hex[:8]}",
            name=name,
            cidr=cidr,
            network_type=network_type
        )
        
        self.networks[network.network_id] = network
        return network
        
    def create_subnet(self, network_id: str, name: str, cidr: str,
                       gateway: str = "") -> Optional[Subnet]:
        """Создание подсети"""
        network = self.networks.get(network_id)
        if not network:
            return None
            
        # Проверка что подсеть входит в сеть
        net_range = ipaddress.ip_network(network.cidr, strict=False)
        subnet_range = ipaddress.ip_network(cidr, strict=False)
        
        if not subnet_range.subnet_of(net_range):
            return None
            
        subnet = Subnet(
            subnet_id=f"subnet_{uuid.uuid4().hex[:8]}",
            name=name,
            cidr=cidr,
            network_id=network_id,
            gateway=gateway or str(list(subnet_range.hosts())[0])
        )
        
        self.subnets[subnet.subnet_id] = subnet
        network.subnets.append(subnet.subnet_id)
        
        return subnet
        
    def add_device(self, name: str, device_type: DeviceType,
                    interfaces: List[Dict[str, Any]] = None) -> NetworkDevice:
        """Добавление устройства"""
        device = NetworkDevice(
            device_id=f"dev_{uuid.uuid4().hex[:8]}",
            name=name,
            device_type=device_type
        )
        
        if interfaces:
            for iface_data in interfaces:
                iface = NetworkInterface(
                    interface_id=f"iface_{uuid.uuid4().hex[:8]}",
                    name=iface_data.get("name", "eth0"),
                    ip_address=iface_data.get("ip", ""),
                    mac_address=iface_data.get("mac", f"02:00:00:{uuid.uuid4().hex[:2]}:{uuid.uuid4().hex[:2]}:{uuid.uuid4().hex[:2]}"),
                    subnet_id=iface_data.get("subnet_id", "")
                )
                device.interfaces.append(iface)
                self.interfaces[iface.interface_id] = iface
                
        self.devices[device.device_id] = device
        return device
        
    def get_topology(self) -> Dict[str, Any]:
        """Получение топологии"""
        return {
            "networks": len(self.networks),
            "subnets": len(self.subnets),
            "devices": len(self.devices),
            "interfaces": len(self.interfaces),
            "topology": [
                {
                    "network": net.name,
                    "cidr": net.cidr,
                    "subnets": [
                        self.subnets[sid].name 
                        for sid in net.subnets 
                        if sid in self.subnets
                    ]
                }
                for net in self.networks.values()
            ]
        }


class NetworkPolicyEngine:
    """Движок сетевых политик"""
    
    def __init__(self):
        self.policies: Dict[str, NetworkPolicy] = {}
        
    def create_policy(self, name: str, **kwargs) -> NetworkPolicy:
        """Создание политики"""
        policy = NetworkPolicy(
            policy_id=f"policy_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        
        self.policies[policy.policy_id] = policy
        return policy
        
    def evaluate(self, src_ip: str, dst_ip: str, 
                  protocol: Protocol, dst_port: int) -> PolicyAction:
        """Оценка трафика"""
        # Сортировка по приоритету
        sorted_policies = sorted(
            self.policies.values(),
            key=lambda p: p.priority
        )
        
        for policy in sorted_policies:
            if not policy.enabled:
                continue
                
            # Проверка источника
            if policy.source_cidrs:
                src_match = any(
                    ipaddress.ip_address(src_ip) in ipaddress.ip_network(cidr, strict=False)
                    for cidr in policy.source_cidrs
                )
                if not src_match:
                    continue
                    
            # Проверка назначения
            if policy.destination_cidrs:
                dst_match = any(
                    ipaddress.ip_address(dst_ip) in ipaddress.ip_network(cidr, strict=False)
                    for cidr in policy.destination_cidrs
                )
                if not dst_match:
                    continue
                    
            # Проверка портов
            if policy.destination_ports and dst_port not in policy.destination_ports:
                continue
                
            # Проверка протокола
            if policy.protocol != Protocol.ANY and policy.protocol != protocol:
                continue
                
            # Совпадение найдено
            policy.hits += 1
            return policy.action
            
        # Default: allow
        return PolicyAction.ALLOW
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика политик"""
        return {
            "total_policies": len(self.policies),
            "enabled_policies": len([p for p in self.policies.values() if p.enabled]),
            "total_hits": sum(p.hits for p in self.policies.values()),
            "by_action": {
                action.value: len([p for p in self.policies.values() if p.action == action])
                for action in PolicyAction
            }
        }


class LoadBalancerManager:
    """Менеджер балансировщиков"""
    
    def __init__(self):
        self.load_balancers: Dict[str, LoadBalancer] = {}
        
    def create_lb(self, name: str, frontend_ip: str, frontend_port: int,
                   algorithm: LoadBalancerAlgorithm = LoadBalancerAlgorithm.ROUND_ROBIN) -> LoadBalancer:
        """Создание балансировщика"""
        lb = LoadBalancer(
            lb_id=f"lb_{uuid.uuid4().hex[:8]}",
            name=name,
            frontend_ip=frontend_ip,
            frontend_port=frontend_port,
            algorithm=algorithm
        )
        
        self.load_balancers[lb.lb_id] = lb
        return lb
        
    def add_backend(self, lb_id: str, server_ip: str, 
                     server_port: int, weight: int = 1) -> bool:
        """Добавление backend сервера"""
        lb = self.load_balancers.get(lb_id)
        if not lb:
            return False
            
        lb.backend_servers.append({
            "ip": server_ip,
            "port": server_port,
            "weight": weight,
            "status": "healthy",
            "connections": 0
        })
        
        return True
        
    def remove_backend(self, lb_id: str, server_ip: str) -> bool:
        """Удаление backend сервера"""
        lb = self.load_balancers.get(lb_id)
        if not lb:
            return False
            
        lb.backend_servers = [
            s for s in lb.backend_servers 
            if s["ip"] != server_ip
        ]
        
        return True
        
    def get_next_server(self, lb_id: str) -> Optional[Dict[str, Any]]:
        """Получение следующего сервера"""
        lb = self.load_balancers.get(lb_id)
        if not lb or not lb.backend_servers:
            return None
            
        healthy_servers = [s for s in lb.backend_servers if s["status"] == "healthy"]
        if not healthy_servers:
            return None
            
        if lb.algorithm == LoadBalancerAlgorithm.ROUND_ROBIN:
            # Simple round robin
            server = healthy_servers[0]
            lb.backend_servers.remove(server)
            lb.backend_servers.append(server)
            return server
            
        elif lb.algorithm == LoadBalancerAlgorithm.LEAST_CONNECTIONS:
            return min(healthy_servers, key=lambda s: s["connections"])
            
        elif lb.algorithm == LoadBalancerAlgorithm.RANDOM:
            return random.choice(healthy_servers)
            
        elif lb.algorithm == LoadBalancerAlgorithm.WEIGHTED:
            total_weight = sum(s["weight"] for s in healthy_servers)
            r = random.randint(1, total_weight)
            cumulative = 0
            for server in healthy_servers:
                cumulative += server["weight"]
                if r <= cumulative:
                    return server
                    
        return healthy_servers[0]
        
    async def health_check(self, lb_id: str) -> Dict[str, Any]:
        """Проверка здоровья"""
        lb = self.load_balancers.get(lb_id)
        if not lb:
            return {"error": "Load balancer not found"}
            
        results = []
        
        for server in lb.backend_servers:
            # Симуляция health check
            await asyncio.sleep(0.01)
            
            healthy = random.random() > 0.1  # 90% healthy
            server["status"] = "healthy" if healthy else "unhealthy"
            
            results.append({
                "server": server["ip"],
                "status": server["status"]
            })
            
        return {
            "lb_id": lb_id,
            "healthy_count": len([r for r in results if r["status"] == "healthy"]),
            "unhealthy_count": len([r for r in results if r["status"] == "unhealthy"]),
            "results": results
        }


class DNSManager:
    """Менеджер DNS"""
    
    def __init__(self):
        self.zones: Dict[str, DNSZone] = {}
        
    def create_zone(self, domain: str, primary_ns: str = "") -> DNSZone:
        """Создание зоны"""
        zone = DNSZone(
            zone_id=f"zone_{uuid.uuid4().hex[:8]}",
            domain=domain,
            primary_ns=primary_ns or f"ns1.{domain}"
        )
        
        self.zones[zone.zone_id] = zone
        return zone
        
    def add_record(self, zone_id: str, name: str, record_type: str,
                    value: str, ttl: int = 300) -> Optional[DNSRecord]:
        """Добавление записи"""
        zone = self.zones.get(zone_id)
        if not zone:
            return None
            
        record = DNSRecord(
            record_id=f"record_{uuid.uuid4().hex[:8]}",
            name=name,
            record_type=record_type,
            value=value,
            ttl=ttl
        )
        
        zone.records.append(record)
        zone.serial += 1
        
        return record
        
    def resolve(self, domain: str, record_type: str = "A") -> List[str]:
        """Разрешение DNS"""
        results = []
        
        for zone in self.zones.values():
            if domain.endswith(zone.domain):
                for record in zone.records:
                    if record.name == domain and record.record_type == record_type:
                        results.append(record.value)
                        
        return results
        
    def delete_record(self, zone_id: str, record_id: str) -> bool:
        """Удаление записи"""
        zone = self.zones.get(zone_id)
        if not zone:
            return False
            
        zone.records = [r for r in zone.records if r.record_id != record_id]
        zone.serial += 1
        
        return True


class VPNManager:
    """Менеджер VPN"""
    
    def __init__(self):
        self.tunnels: Dict[str, VPNTunnel] = {}
        
    def create_tunnel(self, name: str, tunnel_type: str,
                       local_endpoint: str, remote_endpoint: str,
                       local_networks: List[str],
                       remote_networks: List[str]) -> VPNTunnel:
        """Создание туннеля"""
        tunnel = VPNTunnel(
            tunnel_id=f"vpn_{uuid.uuid4().hex[:8]}",
            name=name,
            tunnel_type=tunnel_type,
            local_endpoint=local_endpoint,
            remote_endpoint=remote_endpoint,
            local_networks=local_networks,
            remote_networks=remote_networks
        )
        
        self.tunnels[tunnel.tunnel_id] = tunnel
        return tunnel
        
    async def establish(self, tunnel_id: str) -> bool:
        """Установка соединения"""
        tunnel = self.tunnels.get(tunnel_id)
        if not tunnel:
            return False
            
        tunnel.status = "establishing"
        
        # Симуляция установки
        await asyncio.sleep(0.2)
        
        # 90% успех
        if random.random() > 0.1:
            tunnel.status = "up"
            return True
        else:
            tunnel.status = "down"
            return False
            
    async def disconnect(self, tunnel_id: str) -> bool:
        """Разрыв соединения"""
        tunnel = self.tunnels.get(tunnel_id)
        if not tunnel:
            return False
            
        tunnel.status = "down"
        return True
        
    def get_status(self) -> Dict[str, Any]:
        """Статус туннелей"""
        return {
            "total_tunnels": len(self.tunnels),
            "active_tunnels": len([t for t in self.tunnels.values() if t.status == "up"]),
            "tunnels": [
                {
                    "name": t.name,
                    "type": t.tunnel_type,
                    "status": t.status,
                    "rx_bytes": t.rx_bytes,
                    "tx_bytes": t.tx_bytes
                }
                for t in self.tunnels.values()
            ]
        }


class TrafficAnalyzer:
    """Анализатор трафика"""
    
    def __init__(self):
        self.flows: Dict[str, TrafficFlow] = {}
        self.statistics: Dict[str, Any] = defaultdict(int)
        
    def record_flow(self, src_ip: str, dst_ip: str, 
                     src_port: int, dst_port: int,
                     protocol: Protocol, bytes_count: int):
        """Запись потока"""
        flow_key = f"{src_ip}:{src_port}->{dst_ip}:{dst_port}:{protocol.value}"
        
        if flow_key in self.flows:
            flow = self.flows[flow_key]
            flow.bytes += bytes_count
            flow.packets += 1
            flow.last_seen = datetime.now()
        else:
            flow = TrafficFlow(
                flow_id=f"flow_{uuid.uuid4().hex[:8]}",
                src_ip=src_ip,
                src_port=src_port,
                dst_ip=dst_ip,
                dst_port=dst_port,
                protocol=protocol,
                bytes=bytes_count,
                packets=1
            )
            self.flows[flow_key] = flow
            
        # Обновление статистики
        self.statistics["total_bytes"] += bytes_count
        self.statistics["total_packets"] += 1
        self.statistics[f"protocol_{protocol.value}"] += bytes_count
        
    def get_top_talkers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Топ источников трафика"""
        src_bytes = defaultdict(int)
        
        for flow in self.flows.values():
            src_bytes[flow.src_ip] += flow.bytes
            
        sorted_srcs = sorted(src_bytes.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {"ip": ip, "bytes": bytes_count}
            for ip, bytes_count in sorted_srcs[:limit]
        ]
        
    def get_top_destinations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Топ назначений"""
        dst_bytes = defaultdict(int)
        
        for flow in self.flows.values():
            dst_bytes[flow.dst_ip] += flow.bytes
            
        sorted_dsts = sorted(dst_bytes.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {"ip": ip, "bytes": bytes_count}
            for ip, bytes_count in sorted_dsts[:limit]
        ]
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика трафика"""
        return {
            "total_flows": len(self.flows),
            "total_bytes": self.statistics.get("total_bytes", 0),
            "total_packets": self.statistics.get("total_packets", 0),
            "by_protocol": {
                p.value: self.statistics.get(f"protocol_{p.value}", 0)
                for p in Protocol if self.statistics.get(f"protocol_{p.value}", 0) > 0
            }
        }


class NetworkAutomationPlatform:
    """Платформа сетевой автоматизации"""
    
    def __init__(self):
        self.topology_manager = NetworkTopologyManager()
        self.policy_engine = NetworkPolicyEngine()
        self.lb_manager = LoadBalancerManager()
        self.dns_manager = DNSManager()
        self.vpn_manager = VPNManager()
        self.traffic_analyzer = TrafficAnalyzer()
        
    def get_status(self) -> Dict[str, Any]:
        """Статус платформы"""
        return {
            "topology": self.topology_manager.get_topology(),
            "policies": self.policy_engine.get_statistics(),
            "load_balancers": len(self.lb_manager.load_balancers),
            "dns_zones": len(self.dns_manager.zones),
            "vpn_tunnels": self.vpn_manager.get_status(),
            "traffic": self.traffic_analyzer.get_statistics()
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 49: Network Automation & SDN")
    print("=" * 60)
    
    async def demo():
        # Создание платформы
        platform = NetworkAutomationPlatform()
        print("✓ Network Automation Platform created")
        
        # Создание топологии
        print("\n🌐 Creating Network Topology...")
        
        # VPC
        vpc = platform.topology_manager.create_network(
            name="production-vpc",
            cidr="10.0.0.0/16",
            network_type=NetworkType.VPC
        )
        print(f"  ✓ Created VPC: {vpc.name} ({vpc.cidr})")
        
        # Подсети
        public_subnet = platform.topology_manager.create_subnet(
            network_id=vpc.network_id,
            name="public-subnet",
            cidr="10.0.1.0/24"
        )
        print(f"  ✓ Created subnet: {public_subnet.name} ({public_subnet.cidr})")
        
        private_subnet = platform.topology_manager.create_subnet(
            network_id=vpc.network_id,
            name="private-subnet",
            cidr="10.0.2.0/24"
        )
        print(f"  ✓ Created subnet: {private_subnet.name} ({private_subnet.cidr})")
        
        # Устройства
        router = platform.topology_manager.add_device(
            name="main-router",
            device_type=DeviceType.ROUTER,
            interfaces=[
                {"name": "eth0", "ip": "10.0.1.1", "subnet_id": public_subnet.subnet_id},
                {"name": "eth1", "ip": "10.0.2.1", "subnet_id": private_subnet.subnet_id}
            ]
        )
        print(f"  ✓ Added device: {router.name}")
        
        # Сетевые политики
        print("\n🛡️ Network Policies...")
        
        # Allow HTTP/HTTPS from internet
        web_policy = platform.policy_engine.create_policy(
            name="allow-web-traffic",
            priority=100,
            source_cidrs=["0.0.0.0/0"],
            destination_cidrs=["10.0.1.0/24"],
            destination_ports=[80, 443],
            protocol=Protocol.TCP,
            action=PolicyAction.ALLOW
        )
        print(f"  ✓ Created policy: {web_policy.name}")
        
        # Block all other traffic
        deny_policy = platform.policy_engine.create_policy(
            name="deny-default",
            priority=1000,
            source_cidrs=["0.0.0.0/0"],
            action=PolicyAction.DENY
        )
        print(f"  ✓ Created policy: {deny_policy.name}")
        
        # Тестирование политик
        result1 = platform.policy_engine.evaluate(
            src_ip="8.8.8.8",
            dst_ip="10.0.1.50",
            protocol=Protocol.TCP,
            dst_port=80
        )
        print(f"\n  Test: 8.8.8.8 -> 10.0.1.50:80 = {result1.value}")
        
        result2 = platform.policy_engine.evaluate(
            src_ip="8.8.8.8",
            dst_ip="10.0.2.50",
            protocol=Protocol.TCP,
            dst_port=22
        )
        print(f"  Test: 8.8.8.8 -> 10.0.2.50:22 = {result2.value}")
        
        # Load Balancer
        print("\n⚖️ Load Balancer...")
        
        lb = platform.lb_manager.create_lb(
            name="web-lb",
            frontend_ip="10.0.1.100",
            frontend_port=80,
            algorithm=LoadBalancerAlgorithm.ROUND_ROBIN
        )
        print(f"  ✓ Created LB: {lb.name}")
        
        # Backend servers
        for i in range(3):
            platform.lb_manager.add_backend(
                lb_id=lb.lb_id,
                server_ip=f"10.0.2.{10 + i}",
                server_port=8080,
                weight=1
            )
        print(f"  ✓ Added {len(lb.backend_servers)} backend servers")
        
        # Health check
        health = await platform.lb_manager.health_check(lb.lb_id)
        print(f"  Health check: {health['healthy_count']} healthy, {health['unhealthy_count']} unhealthy")
        
        # DNS
        print("\n🌍 DNS Management...")
        
        zone = platform.dns_manager.create_zone(
            domain="example.com",
            primary_ns="ns1.example.com"
        )
        print(f"  ✓ Created zone: {zone.domain}")
        
        # A record
        platform.dns_manager.add_record(
            zone_id=zone.zone_id,
            name="www.example.com",
            record_type="A",
            value="10.0.1.100",
            ttl=300
        )
        print(f"  ✓ Added A record: www.example.com")
        
        # CNAME
        platform.dns_manager.add_record(
            zone_id=zone.zone_id,
            name="api.example.com",
            record_type="CNAME",
            value="www.example.com"
        )
        print(f"  ✓ Added CNAME: api.example.com")
        
        # Resolve
        resolved = platform.dns_manager.resolve("www.example.com", "A")
        print(f"  Resolve www.example.com: {resolved}")
        
        # VPN
        print("\n🔐 VPN Tunnels...")
        
        tunnel = platform.vpn_manager.create_tunnel(
            name="site-to-site",
            tunnel_type="ipsec",
            local_endpoint="203.0.113.1",
            remote_endpoint="198.51.100.1",
            local_networks=["10.0.0.0/16"],
            remote_networks=["172.16.0.0/16"]
        )
        print(f"  ✓ Created tunnel: {tunnel.name}")
        
        # Establish
        success = await platform.vpn_manager.establish(tunnel.tunnel_id)
        print(f"  Tunnel status: {tunnel.status}")
        
        # Traffic Analysis
        print("\n📊 Traffic Analysis...")
        
        # Simulate traffic
        for _ in range(100):
            platform.traffic_analyzer.record_flow(
                src_ip=f"10.0.1.{random.randint(10, 50)}",
                dst_ip=f"10.0.2.{random.randint(10, 50)}",
                src_port=random.randint(1024, 65535),
                dst_port=random.choice([80, 443, 8080]),
                protocol=random.choice([Protocol.TCP, Protocol.HTTP, Protocol.HTTPS]),
                bytes_count=random.randint(100, 10000)
            )
            
        traffic_stats = platform.traffic_analyzer.get_statistics()
        print(f"  Total flows: {traffic_stats['total_flows']}")
        print(f"  Total bytes: {traffic_stats['total_bytes']:,}")
        
        top_talkers = platform.traffic_analyzer.get_top_talkers(3)
        print(f"  Top talkers: {[t['ip'] for t in top_talkers]}")
        
        # Итоговый статус
        print("\n📈 Platform Status:")
        status = platform.get_status()
        print(f"  Networks: {status['topology']['networks']}")
        print(f"  Subnets: {status['topology']['subnets']}")
        print(f"  Devices: {status['topology']['devices']}")
        print(f"  Policies: {status['policies']['total_policies']}")
        print(f"  Load Balancers: {status['load_balancers']}")
        print(f"  DNS Zones: {status['dns_zones']}")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Network Automation & SDN Platform initialized!")
    print("=" * 60)
