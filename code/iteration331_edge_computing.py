#!/usr/bin/env python3
"""
Server Init - Iteration 331: Edge Computing Platform
Платформа управления периферийными вычислениями

Функционал:
- Edge Node Management - управление edge-узлами
- Application Deployment - развёртывание приложений
- Data Synchronization - синхронизация данных
- Latency Optimization - оптимизация задержки
- Offline Capabilities - работа без связи
- Edge Analytics - аналитика на периферии
- Device Management - управление устройствами
- Edge Security - безопасность периферии
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class NodeType(Enum):
    """Тип edge-узла"""
    GATEWAY = "gateway"
    COMPUTE = "compute"
    STORAGE = "storage"
    SENSOR_HUB = "sensor_hub"
    MICRO_DC = "micro_dc"
    IOT_GATEWAY = "iot_gateway"


class NodeStatus(Enum):
    """Статус узла"""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    PROVISIONING = "provisioning"


class DeploymentStatus(Enum):
    """Статус развёртывания"""
    PENDING = "pending"
    DEPLOYING = "deploying"
    RUNNING = "running"
    FAILED = "failed"
    STOPPED = "stopped"
    UPDATING = "updating"


class SyncStatus(Enum):
    """Статус синхронизации"""
    SYNCED = "synced"
    SYNCING = "syncing"
    PENDING = "pending"
    CONFLICT = "conflict"
    OFFLINE = "offline"


class ConnectivityType(Enum):
    """Тип подключения"""
    FIBER = "fiber"
    LTE = "lte"
    FIVE_G = "5g"
    SATELLITE = "satellite"
    WIFI = "wifi"
    ETHERNET = "ethernet"


class DataPriority(Enum):
    """Приоритет данных"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BATCH = "batch"


@dataclass
class EdgeLocation:
    """Локация edge"""
    location_id: str
    name: str
    
    # Geographic
    latitude: float = 0.0
    longitude: float = 0.0
    address: str = ""
    city: str = ""
    country: str = ""
    timezone: str = "UTC"
    
    # Type
    location_type: str = "retail"  # retail, factory, warehouse, office, field
    
    # Nodes
    node_ids: List[str] = field(default_factory=list)
    
    # Status
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class EdgeNode:
    """Edge-узел"""
    node_id: str
    name: str
    
    # Location
    location_id: str = ""
    
    # Type
    node_type: NodeType = NodeType.COMPUTE
    
    # Hardware
    cpu_cores: int = 4
    memory_gb: float = 8.0
    storage_gb: float = 256.0
    gpu_available: bool = False
    
    # Resources available
    cpu_available: float = 100.0  # percentage
    memory_available: float = 100.0
    storage_available: float = 100.0
    
    # Connectivity
    connectivity_type: ConnectivityType = ConnectivityType.ETHERNET
    bandwidth_mbps: float = 1000.0
    latency_to_cloud_ms: float = 50.0
    
    # Status
    status: NodeStatus = NodeStatus.ONLINE
    
    # Health
    cpu_utilization: float = 0.0
    memory_utilization: float = 0.0
    temperature_celsius: float = 45.0
    
    # Software
    os_version: str = ""
    runtime_version: str = ""
    agent_version: str = ""
    
    # Timestamps
    last_heartbeat: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class EdgeApplication:
    """Edge-приложение"""
    app_id: str
    name: str
    
    # Type
    app_type: str = "container"  # container, wasm, binary, function
    
    # Image/Package
    image: str = ""
    version: str = ""
    
    # Resources
    cpu_request: float = 0.5  # cores
    memory_request_mb: int = 256
    storage_request_mb: int = 100
    
    # Requirements
    requires_gpu: bool = False
    min_bandwidth_mbps: float = 10.0
    max_latency_ms: float = 100.0
    
    # Offline
    offline_capable: bool = True
    
    # Ports
    exposed_ports: List[int] = field(default_factory=list)
    
    # Environment
    env_vars: Dict[str, str] = field(default_factory=dict)
    
    # Status
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Deployment:
    """Развёртывание"""
    deployment_id: str
    
    # Application
    app_id: str = ""
    app_name: str = ""
    
    # Target
    node_id: str = ""
    node_name: str = ""
    
    # Replicas
    desired_replicas: int = 1
    running_replicas: int = 0
    
    # Status
    status: DeploymentStatus = DeploymentStatus.PENDING
    
    # Version
    version: str = ""
    
    # Health
    health_score: float = 100.0
    last_health_check: datetime = field(default_factory=datetime.now)
    
    # Metrics
    request_count: int = 0
    error_count: int = 0
    avg_response_time_ms: float = 0.0
    
    # Timestamps
    deployed_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class DataSync:
    """Синхронизация данных"""
    sync_id: str
    name: str
    
    # Source/Target
    source_node_id: str = ""
    target_type: str = "cloud"  # cloud, node, both
    target_node_id: str = ""
    
    # Data
    data_type: str = ""  # metrics, logs, files, database
    data_path: str = ""
    
    # Priority
    priority: DataPriority = DataPriority.NORMAL
    
    # Schedule
    sync_interval_seconds: int = 60
    batch_size_mb: float = 10.0
    
    # Compression
    compression_enabled: bool = True
    compression_ratio: float = 0.3
    
    # Status
    status: SyncStatus = SyncStatus.SYNCED
    
    # Progress
    pending_bytes: int = 0
    synced_bytes: int = 0
    
    # Timestamps
    last_sync: Optional[datetime] = None
    next_sync: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class EdgeDevice:
    """Периферийное устройство"""
    device_id: str
    name: str
    
    # Type
    device_type: str = "sensor"  # sensor, camera, actuator, display, terminal
    
    # Connected to
    connected_node_id: str = ""
    
    # Protocol
    protocol: str = "mqtt"  # mqtt, modbus, opc-ua, http, coap
    
    # Status
    is_online: bool = True
    last_data_at: Optional[datetime] = None
    
    # Properties
    properties: Dict[str, Any] = field(default_factory=dict)
    
    # Data rate
    data_rate_per_second: float = 1.0
    
    # Firmware
    firmware_version: str = ""
    
    # Timestamps
    registered_at: datetime = field(default_factory=datetime.now)


@dataclass
class EdgeAlert:
    """Оповещение edge"""
    alert_id: str
    
    # Source
    node_id: str = ""
    device_id: str = ""
    deployment_id: str = ""
    
    # Type
    alert_type: str = "warning"  # info, warning, error, critical
    
    # Message
    title: str = ""
    message: str = ""
    
    # Status
    is_acknowledged: bool = False
    acknowledged_by: str = ""
    acknowledged_at: Optional[datetime] = None
    
    # Timestamps
    triggered_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


@dataclass
class EdgeMetric:
    """Метрика edge"""
    metric_id: str
    
    # Source
    node_id: str = ""
    deployment_id: str = ""
    
    # Metric
    metric_name: str = ""
    value: float = 0.0
    unit: str = ""
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Timestamp
    collected_at: datetime = field(default_factory=datetime.now)


class EdgeComputingManager:
    """Менеджер периферийных вычислений"""
    
    def __init__(self):
        self.locations: Dict[str, EdgeLocation] = {}
        self.nodes: Dict[str, EdgeNode] = {}
        self.applications: Dict[str, EdgeApplication] = {}
        self.deployments: Dict[str, Deployment] = {}
        self.syncs: Dict[str, DataSync] = {}
        self.devices: Dict[str, EdgeDevice] = {}
        self.alerts: Dict[str, EdgeAlert] = {}
        self.metrics: Dict[str, EdgeMetric] = {}
        
    async def add_location(self, name: str,
                          latitude: float,
                          longitude: float,
                          city: str,
                          country: str,
                          location_type: str = "retail") -> EdgeLocation:
        """Добавление локации"""
        location = EdgeLocation(
            location_id=f"loc_{uuid.uuid4().hex[:8]}",
            name=name,
            latitude=latitude,
            longitude=longitude,
            city=city,
            country=country,
            location_type=location_type
        )
        
        self.locations[location.location_id] = location
        return location
        
    async def add_node(self, name: str,
                      location_id: str,
                      node_type: NodeType,
                      cpu_cores: int = 4,
                      memory_gb: float = 8.0,
                      storage_gb: float = 256.0,
                      connectivity: ConnectivityType = ConnectivityType.ETHERNET,
                      bandwidth_mbps: float = 1000.0) -> Optional[EdgeNode]:
        """Добавление узла"""
        location = self.locations.get(location_id)
        if not location:
            return None
            
        node = EdgeNode(
            node_id=f"node_{uuid.uuid4().hex[:8]}",
            name=name,
            location_id=location_id,
            node_type=node_type,
            cpu_cores=cpu_cores,
            memory_gb=memory_gb,
            storage_gb=storage_gb,
            connectivity_type=connectivity,
            bandwidth_mbps=bandwidth_mbps,
            latency_to_cloud_ms=random.uniform(10, 100),
            os_version="EdgeOS 2.0",
            runtime_version="containerd 1.6",
            agent_version="1.5.0"
        )
        
        location.node_ids.append(node.node_id)
        self.nodes[node.node_id] = node
        return node
        
    async def update_node_health(self, node_id: str,
                                cpu_util: float,
                                memory_util: float,
                                temperature: float) -> bool:
        """Обновление здоровья узла"""
        node = self.nodes.get(node_id)
        if not node:
            return False
            
        node.cpu_utilization = cpu_util
        node.memory_utilization = memory_util
        node.temperature_celsius = temperature
        node.last_heartbeat = datetime.now()
        
        # Update available resources
        node.cpu_available = 100.0 - cpu_util
        node.memory_available = 100.0 - memory_util
        
        # Update status based on health
        if temperature > 80 or cpu_util > 95 or memory_util > 95:
            node.status = NodeStatus.DEGRADED
            await self._create_alert(node_id=node_id, alert_type="warning",
                                    title=f"Node {node.name} degraded",
                                    message="High resource utilization detected")
        elif node.status == NodeStatus.DEGRADED:
            node.status = NodeStatus.ONLINE
            
        return True
        
    async def register_application(self, name: str,
                                  app_type: str,
                                  image: str,
                                  version: str,
                                  cpu_request: float = 0.5,
                                  memory_request_mb: int = 256,
                                  offline_capable: bool = True) -> EdgeApplication:
        """Регистрация приложения"""
        app = EdgeApplication(
            app_id=f"app_{uuid.uuid4().hex[:8]}",
            name=name,
            app_type=app_type,
            image=image,
            version=version,
            cpu_request=cpu_request,
            memory_request_mb=memory_request_mb,
            offline_capable=offline_capable
        )
        
        self.applications[app.app_id] = app
        return app
        
    async def deploy_application(self, app_id: str,
                                node_id: str,
                                replicas: int = 1) -> Optional[Deployment]:
        """Развёртывание приложения"""
        app = self.applications.get(app_id)
        node = self.nodes.get(node_id)
        
        if not app or not node:
            return None
            
        if node.status != NodeStatus.ONLINE:
            return None
            
        # Check resources
        cpu_needed = app.cpu_request * replicas
        memory_needed = app.memory_request_mb * replicas
        
        cpu_available_cores = node.cpu_cores * (node.cpu_available / 100)
        memory_available_mb = node.memory_gb * 1024 * (node.memory_available / 100)
        
        if cpu_needed > cpu_available_cores or memory_needed > memory_available_mb:
            return None
            
        deployment = Deployment(
            deployment_id=f"dep_{uuid.uuid4().hex[:8]}",
            app_id=app_id,
            app_name=app.name,
            node_id=node_id,
            node_name=node.name,
            desired_replicas=replicas,
            running_replicas=replicas,
            status=DeploymentStatus.RUNNING,
            version=app.version
        )
        
        self.deployments[deployment.deployment_id] = deployment
        
        # Update node resources
        node.cpu_available -= (cpu_needed / node.cpu_cores) * 100
        node.memory_available -= (memory_needed / (node.memory_gb * 1024)) * 100
        
        return deployment
        
    async def scale_deployment(self, deployment_id: str,
                              replicas: int) -> bool:
        """Масштабирование развёртывания"""
        deployment = self.deployments.get(deployment_id)
        if not deployment:
            return False
            
        deployment.desired_replicas = replicas
        deployment.status = DeploymentStatus.UPDATING
        deployment.last_updated = datetime.now()
        
        # Simulate scaling
        deployment.running_replicas = replicas
        deployment.status = DeploymentStatus.RUNNING
        
        return True
        
    async def configure_data_sync(self, name: str,
                                 source_node_id: str,
                                 data_type: str,
                                 data_path: str,
                                 target_type: str = "cloud",
                                 priority: DataPriority = DataPriority.NORMAL,
                                 interval_seconds: int = 60) -> Optional[DataSync]:
        """Конфигурация синхронизации данных"""
        node = self.nodes.get(source_node_id)
        if not node:
            return None
            
        sync = DataSync(
            sync_id=f"sync_{uuid.uuid4().hex[:8]}",
            name=name,
            source_node_id=source_node_id,
            target_type=target_type,
            data_type=data_type,
            data_path=data_path,
            priority=priority,
            sync_interval_seconds=interval_seconds,
            next_sync=datetime.now() + timedelta(seconds=interval_seconds)
        )
        
        self.syncs[sync.sync_id] = sync
        return sync
        
    async def trigger_sync(self, sync_id: str) -> bool:
        """Запуск синхронизации"""
        sync = self.syncs.get(sync_id)
        if not sync:
            return False
            
        node = self.nodes.get(sync.source_node_id)
        if not node or node.status == NodeStatus.OFFLINE:
            sync.status = SyncStatus.OFFLINE
            return False
            
        sync.status = SyncStatus.SYNCING
        
        # Simulate sync
        sync.synced_bytes += random.randint(1000, 10000)
        sync.pending_bytes = max(0, sync.pending_bytes - sync.synced_bytes)
        
        sync.status = SyncStatus.SYNCED
        sync.last_sync = datetime.now()
        sync.next_sync = datetime.now() + timedelta(seconds=sync.sync_interval_seconds)
        
        return True
        
    async def register_device(self, name: str,
                             device_type: str,
                             node_id: str,
                             protocol: str = "mqtt",
                             data_rate: float = 1.0) -> Optional[EdgeDevice]:
        """Регистрация устройства"""
        node = self.nodes.get(node_id)
        if not node:
            return None
            
        device = EdgeDevice(
            device_id=f"dev_{uuid.uuid4().hex[:8]}",
            name=name,
            device_type=device_type,
            connected_node_id=node_id,
            protocol=protocol,
            data_rate_per_second=data_rate,
            firmware_version="1.0.0"
        )
        
        self.devices[device.device_id] = device
        return device
        
    async def update_device_status(self, device_id: str,
                                  is_online: bool,
                                  data: Dict[str, Any] = None) -> bool:
        """Обновление статуса устройства"""
        device = self.devices.get(device_id)
        if not device:
            return False
            
        device.is_online = is_online
        
        if data:
            device.properties.update(data)
            device.last_data_at = datetime.now()
            
        return True
        
    async def _create_alert(self, node_id: str = "",
                           device_id: str = "",
                           deployment_id: str = "",
                           alert_type: str = "warning",
                           title: str = "",
                           message: str = "") -> EdgeAlert:
        """Создание оповещения"""
        alert = EdgeAlert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            node_id=node_id,
            device_id=device_id,
            deployment_id=deployment_id,
            alert_type=alert_type,
            title=title,
            message=message
        )
        
        self.alerts[alert.alert_id] = alert
        return alert
        
    async def acknowledge_alert(self, alert_id: str,
                               user: str) -> bool:
        """Подтверждение оповещения"""
        alert = self.alerts.get(alert_id)
        if not alert:
            return False
            
        alert.is_acknowledged = True
        alert.acknowledged_by = user
        alert.acknowledged_at = datetime.now()
        
        return True
        
    async def collect_metrics(self, node_id: str) -> List[EdgeMetric]:
        """Сбор метрик"""
        node = self.nodes.get(node_id)
        if not node:
            return []
            
        metrics = []
        
        # Node metrics
        metric_data = [
            ("cpu_utilization", node.cpu_utilization, "%"),
            ("memory_utilization", node.memory_utilization, "%"),
            ("temperature", node.temperature_celsius, "°C"),
            ("bandwidth_used", random.uniform(0, node.bandwidth_mbps), "Mbps"),
            ("latency", node.latency_to_cloud_ms, "ms")
        ]
        
        for name, value, unit in metric_data:
            metric = EdgeMetric(
                metric_id=f"m_{uuid.uuid4().hex[:8]}",
                node_id=node_id,
                metric_name=name,
                value=value,
                unit=unit
            )
            metrics.append(metric)
            self.metrics[metric.metric_id] = metric
            
        return metrics
        
    def get_node_by_location(self, location_id: str) -> List[EdgeNode]:
        """Получение узлов по локации"""
        location = self.locations.get(location_id)
        if not location:
            return []
            
        return [self.nodes[nid] for nid in location.node_ids if nid in self.nodes]
        
    def get_deployments_by_node(self, node_id: str) -> List[Deployment]:
        """Получение развёртываний по узлу"""
        return [d for d in self.deployments.values() if d.node_id == node_id]
        
    def get_devices_by_node(self, node_id: str) -> List[EdgeDevice]:
        """Получение устройств по узлу"""
        return [d for d in self.devices.values() if d.connected_node_id == node_id]
        
    def calculate_latency_optimization(self) -> Dict[str, Any]:
        """Расчёт оптимизации задержки"""
        total_nodes = len(self.nodes)
        avg_latency = 0.0
        
        if total_nodes > 0:
            avg_latency = sum(n.latency_to_cloud_ms for n in self.nodes.values()) / total_nodes
            
        local_processing = sum(1 for d in self.deployments.values() if d.status == DeploymentStatus.RUNNING)
        
        return {
            "total_nodes": total_nodes,
            "avg_cloud_latency_ms": avg_latency,
            "local_processing_enabled": local_processing,
            "latency_reduction_percent": min(90, local_processing * 10)
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_locations = len(self.locations)
        total_nodes = len(self.nodes)
        
        online_nodes = sum(1 for n in self.nodes.values() if n.status == NodeStatus.ONLINE)
        
        by_type = {}
        for node in self.nodes.values():
            by_type[node.node_type.value] = by_type.get(node.node_type.value, 0) + 1
            
        total_apps = len(self.applications)
        total_deployments = len(self.deployments)
        running_deployments = sum(1 for d in self.deployments.values() if d.status == DeploymentStatus.RUNNING)
        
        total_devices = len(self.devices)
        online_devices = sum(1 for d in self.devices.values() if d.is_online)
        
        total_syncs = len(self.syncs)
        synced = sum(1 for s in self.syncs.values() if s.status == SyncStatus.SYNCED)
        
        unacked_alerts = sum(1 for a in self.alerts.values() if not a.is_acknowledged)
        
        total_cpu = sum(n.cpu_cores for n in self.nodes.values())
        total_memory = sum(n.memory_gb for n in self.nodes.values())
        total_storage = sum(n.storage_gb for n in self.nodes.values())
        
        return {
            "total_locations": total_locations,
            "total_nodes": total_nodes,
            "online_nodes": online_nodes,
            "nodes_by_type": by_type,
            "total_applications": total_apps,
            "total_deployments": total_deployments,
            "running_deployments": running_deployments,
            "total_devices": total_devices,
            "online_devices": online_devices,
            "total_syncs": total_syncs,
            "synced": synced,
            "unacked_alerts": unacked_alerts,
            "total_cpu_cores": total_cpu,
            "total_memory_gb": total_memory,
            "total_storage_gb": total_storage
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 331: Edge Computing Platform")
    print("=" * 60)
    
    edge = EdgeComputingManager()
    print("✓ Edge Computing Manager created")
    
    # Add locations
    print("\n📍 Adding Edge Locations...")
    
    locations_data = [
        ("NYC Store #1", 40.7128, -74.0060, "New York", "USA", "retail"),
        ("LA Warehouse", 34.0522, -118.2437, "Los Angeles", "USA", "warehouse"),
        ("Chicago Factory", 41.8781, -87.6298, "Chicago", "USA", "factory"),
        ("London Office", 51.5074, -0.1278, "London", "UK", "office"),
        ("Tokyo Retail", 35.6762, 139.6503, "Tokyo", "Japan", "retail"),
        ("Berlin Hub", 52.5200, 13.4050, "Berlin", "Germany", "warehouse"),
        ("Sydney Branch", -33.8688, 151.2093, "Sydney", "Australia", "office"),
        ("Singapore DC", 1.3521, 103.8198, "Singapore", "Singapore", "micro_dc")
    ]
    
    locations = []
    for name, lat, lon, city, country, loc_type in locations_data:
        location = await edge.add_location(name, lat, lon, city, country, loc_type)
        locations.append(location)
        print(f"  📍 {name} ({city}, {country})")
        
    # Add nodes
    print("\n🖥️ Adding Edge Nodes...")
    
    nodes_data = [
        # NYC Store
        (0, "nyc-gateway-1", NodeType.GATEWAY, 4, 8, 256, ConnectivityType.FIBER, 1000),
        (0, "nyc-compute-1", NodeType.COMPUTE, 8, 16, 512, ConnectivityType.FIBER, 1000),
        (0, "nyc-iot-hub-1", NodeType.IOT_GATEWAY, 2, 4, 128, ConnectivityType.WIFI, 100),
        # LA Warehouse
        (1, "la-compute-1", NodeType.COMPUTE, 16, 32, 1024, ConnectivityType.FIBER, 10000),
        (1, "la-storage-1", NodeType.STORAGE, 4, 8, 4096, ConnectivityType.ETHERNET, 1000),
        # Chicago Factory
        (2, "chi-gateway-1", NodeType.GATEWAY, 4, 8, 256, ConnectivityType.FIVE_G, 500),
        (2, "chi-sensor-hub-1", NodeType.SENSOR_HUB, 2, 4, 128, ConnectivityType.ETHERNET, 100),
        (2, "chi-compute-1", NodeType.COMPUTE, 8, 16, 512, ConnectivityType.ETHERNET, 1000),
        # London Office
        (3, "lon-compute-1", NodeType.COMPUTE, 8, 16, 512, ConnectivityType.FIBER, 1000),
        # Tokyo Retail
        (4, "tky-gateway-1", NodeType.GATEWAY, 4, 8, 256, ConnectivityType.FIBER, 1000),
        (4, "tky-iot-hub-1", NodeType.IOT_GATEWAY, 2, 4, 128, ConnectivityType.WIFI, 100),
        # Singapore DC
        (7, "sgp-micro-dc-1", NodeType.MICRO_DC, 32, 64, 2048, ConnectivityType.FIBER, 10000),
    ]
    
    nodes = []
    for loc_idx, name, ntype, cpu, mem, storage, conn, bw in nodes_data:
        node = await edge.add_node(name, locations[loc_idx].location_id, ntype, cpu, mem, storage, conn, bw)
        if node:
            nodes.append(node)
            # Set initial health
            await edge.update_node_health(
                node.node_id,
                random.uniform(20, 70),
                random.uniform(30, 60),
                random.uniform(35, 55)
            )
            
    print(f"  ✓ Added {len(nodes)} nodes")
    
    # Register applications
    print("\n📦 Registering Edge Applications...")
    
    apps_data = [
        ("inventory-tracker", "container", "registry.io/inventory:v1.2", "1.2.0", 0.5, 256, True),
        ("pos-system", "container", "registry.io/pos:v3.0", "3.0.0", 1.0, 512, True),
        ("sensor-collector", "container", "registry.io/collector:v1.0", "1.0.0", 0.2, 128, True),
        ("video-analytics", "container", "registry.io/video-ai:v2.1", "2.1.0", 2.0, 1024, False),
        ("quality-inspection", "container", "registry.io/qc:v1.5", "1.5.0", 1.5, 512, True),
        ("local-cache", "container", "registry.io/cache:v1.0", "1.0.0", 0.5, 512, True),
        ("data-aggregator", "container", "registry.io/aggregator:v2.0", "2.0.0", 0.5, 256, True),
        ("ml-inference", "container", "registry.io/ml-edge:v1.0", "1.0.0", 2.0, 2048, False)
    ]
    
    apps = []
    for name, atype, image, version, cpu, mem, offline in apps_data:
        app = await edge.register_application(name, atype, image, version, cpu, mem, offline)
        apps.append(app)
        print(f"  📦 {name} v{version}")
        
    # Deploy applications
    print("\n🚀 Deploying Applications...")
    
    deployments_data = [
        (0, 0, 2),  # inventory-tracker on nyc-gateway
        (1, 1, 1),  # pos-system on nyc-compute
        (2, 2, 1),  # sensor-collector on nyc-iot-hub
        (3, 3, 2),  # video-analytics on la-compute
        (4, 5, 1),  # quality-inspection on la-storage
        (5, 6, 1),  # local-cache on chi-gateway
        (6, 7, 1),  # data-aggregator on chi-sensor-hub
        (7, 8, 2),  # ml-inference on chi-compute
        (0, 9, 1),  # inventory-tracker on lon-compute
        (1, 10, 1), # pos-system on tky-gateway
        (7, 11, 3), # ml-inference on sgp-micro-dc
    ]
    
    deployments = []
    for app_idx, node_idx, replicas in deployments_data:
        if node_idx < len(nodes) and app_idx < len(apps):
            deployment = await edge.deploy_application(apps[app_idx].app_id, nodes[node_idx].node_id, replicas)
            if deployment:
                deployments.append(deployment)
                
    print(f"  ✓ Created {len(deployments)} deployments")
    
    # Configure data sync
    print("\n🔄 Configuring Data Synchronization...")
    
    syncs_data = [
        ("NYC Metrics Sync", 0, "metrics", "/data/metrics", "cloud", DataPriority.HIGH, 30),
        ("LA Video Sync", 3, "files", "/data/video", "cloud", DataPriority.NORMAL, 300),
        ("Chicago Sensor Sync", 6, "metrics", "/data/sensors", "cloud", DataPriority.CRITICAL, 10),
        ("Tokyo POS Sync", 9, "database", "/data/transactions", "cloud", DataPriority.HIGH, 60),
        ("Singapore ML Sync", 11, "files", "/data/models", "cloud", DataPriority.LOW, 3600)
    ]
    
    syncs = []
    for name, node_idx, dtype, dpath, target, priority, interval in syncs_data:
        if node_idx < len(nodes):
            sync = await edge.configure_data_sync(name, nodes[node_idx].node_id, dtype, dpath, target, priority, interval)
            if sync:
                syncs.append(sync)
                await edge.trigger_sync(sync.sync_id)
                
    print(f"  ✓ Configured {len(syncs)} data syncs")
    
    # Register devices
    print("\n📱 Registering Edge Devices...")
    
    devices_data = [
        ("temp-sensor-001", "sensor", 2, "mqtt", 1.0),
        ("rfid-reader-001", "sensor", 2, "mqtt", 10.0),
        ("camera-001", "camera", 3, "rtsp", 30.0),
        ("camera-002", "camera", 3, "rtsp", 30.0),
        ("barcode-scanner-001", "sensor", 0, "http", 5.0),
        ("display-001", "display", 1, "http", 0.1),
        ("robotic-arm-001", "actuator", 7, "opc-ua", 100.0),
        ("conveyor-001", "actuator", 7, "modbus", 10.0),
        ("pos-terminal-001", "terminal", 10, "http", 1.0),
        ("hvac-controller-001", "actuator", 8, "mqtt", 0.5)
    ]
    
    devices = []
    for name, dtype, node_idx, protocol, rate in devices_data:
        if node_idx < len(nodes):
            device = await edge.register_device(name, dtype, nodes[node_idx].node_id, protocol, rate)
            if device:
                devices.append(device)
                await edge.update_device_status(device.device_id, True, {"value": random.uniform(0, 100)})
                
    print(f"  ✓ Registered {len(devices)} devices")
    
    # Collect metrics
    print("\n📊 Collecting Metrics...")
    
    for node in nodes[:5]:
        await edge.collect_metrics(node.node_id)
        
    print(f"  ✓ Collected metrics from {min(5, len(nodes))} nodes")
    
    # Locations summary
    print("\n📍 Edge Locations:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Location                 │ City         │ Type       │ Nodes │ Deployments │ Devices       │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for location in locations:
        name = location.name[:24].ljust(24)
        city = location.city[:12].ljust(12)
        loc_type = location.location_type[:10].ljust(10)
        
        loc_nodes = edge.get_node_by_location(location.location_id)
        nodes_count = str(len(loc_nodes)).ljust(5)
        
        dep_count = sum(len(edge.get_deployments_by_node(n.node_id)) for n in loc_nodes)
        deployments_count = str(dep_count).ljust(11)
        
        dev_count = sum(len(edge.get_devices_by_node(n.node_id)) for n in loc_nodes)
        devices_count = str(dev_count).ljust(13)
        
        print(f"  │ {name} │ {city} │ {loc_type} │ {nodes_count} │ {deployments_count} │ {devices_count} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Nodes status
    print("\n🖥️ Edge Nodes:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Node Name          │ Type        │ CPU      │ Memory   │ Storage  │ Connectivity │ Latency  │ Status           │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for node in nodes:
        name = node.name[:18].ljust(18)
        ntype = node.node_type.value[:11].ljust(11)
        cpu = f"{node.cpu_cores}c/{node.cpu_utilization:.0f}%".ljust(8)
        memory = f"{node.memory_gb:.0f}GB/{node.memory_utilization:.0f}%".ljust(8)
        storage = f"{node.storage_gb:.0f}GB".ljust(8)
        conn = node.connectivity_type.value[:12].ljust(12)
        latency = f"{node.latency_to_cloud_ms:.0f}ms".ljust(8)
        
        status_icon = {"online": "✓", "offline": "✗", "degraded": "⚠", "maintenance": "🔧"}.get(node.status.value, "?")
        status = f"{status_icon} {node.status.value}"[:16].ljust(16)
        
        print(f"  │ {name} │ {ntype} │ {cpu} │ {memory} │ {storage} │ {conn} │ {latency} │ {status} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Deployments
    print("\n🚀 Deployments:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Application          │ Node               │ Replicas │ Version  │ Health   │ Status            │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for dep in deployments:
        app_name = dep.app_name[:20].ljust(20)
        node_name = dep.node_name[:18].ljust(18)
        replicas = f"{dep.running_replicas}/{dep.desired_replicas}".ljust(8)
        version = dep.version[:8].ljust(8)
        health = f"{dep.health_score:.0f}%".ljust(8)
        
        status_icon = {"running": "✓", "stopped": "○", "failed": "✗", "updating": "↻"}.get(dep.status.value, "?")
        status = f"{status_icon} {dep.status.value}"[:17].ljust(17)
        
        print(f"  │ {app_name} │ {node_name} │ {replicas} │ {version} │ {health} │ {status} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Data sync status
    print("\n🔄 Data Synchronization:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Sync Name                │ Type      │ Priority   │ Interval │ Last Sync            │ Status  │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for sync in syncs:
        name = sync.name[:24].ljust(24)
        dtype = sync.data_type[:9].ljust(9)
        priority = sync.priority.value[:10].ljust(10)
        interval = f"{sync.sync_interval_seconds}s".ljust(8)
        last = sync.last_sync.strftime("%Y-%m-%d %H:%M")[:20].ljust(20) if sync.last_sync else "Never".ljust(20)
        
        status_icon = {"synced": "✓", "syncing": "↻", "pending": "○", "offline": "✗"}.get(sync.status.value, "?")
        status = f"{status_icon}".ljust(7)
        
        print(f"  │ {name} │ {dtype} │ {priority} │ {interval} │ {last} │ {status} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Devices
    print("\n📱 Edge Devices:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Device Name            │ Type       │ Protocol  │ Data Rate │ Status                 │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for device in devices:
        name = device.name[:22].ljust(22)
        dtype = device.device_type[:10].ljust(10)
        protocol = device.protocol[:9].ljust(9)
        rate = f"{device.data_rate_per_second}/s".ljust(9)
        
        status = "✓ Online" if device.is_online else "✗ Offline"
        status = status[:22].ljust(22)
        
        print(f"  │ {name} │ {dtype} │ {protocol} │ {rate} │ {status} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Latency optimization
    print("\n⚡ Latency Optimization:")
    
    latency_stats = edge.calculate_latency_optimization()
    
    print(f"\n  Total Nodes: {latency_stats['total_nodes']}")
    print(f"  Average Cloud Latency: {latency_stats['avg_cloud_latency_ms']:.1f}ms")
    print(f"  Local Processing Enabled: {latency_stats['local_processing_enabled']} deployments")
    print(f"  Estimated Latency Reduction: {latency_stats['latency_reduction_percent']}%")
    
    # Resource utilization
    print("\n📊 Resource Utilization:")
    
    stats = edge.get_statistics()
    
    print(f"\n  Total CPU Cores: {stats['total_cpu_cores']}")
    print(f"  Total Memory: {stats['total_memory_gb']:.0f} GB")
    print(f"  Total Storage: {stats['total_storage_gb']:.0f} GB")
    
    # Nodes by type
    print("\n  Nodes by Type:")
    for ntype, count in stats['nodes_by_type'].items():
        print(f"    {ntype}: {count}")
        
    # Alerts
    print("\n🔔 Active Alerts:")
    
    unacked_alerts = [a for a in edge.alerts.values() if not a.is_acknowledged]
    if unacked_alerts:
        for alert in unacked_alerts[:5]:
            icon = {"info": "ℹ", "warning": "⚠", "error": "✗", "critical": "🚨"}.get(alert.alert_type, "?")
            print(f"  {icon} {alert.title}")
            print(f"    {alert.message}")
    else:
        print("  ✓ No active alerts")
        
    # Overall statistics
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Locations: {stats['total_locations']}")
    print(f"  Nodes: {stats['online_nodes']}/{stats['total_nodes']} online")
    print(f"  Applications: {stats['total_applications']}")
    print(f"  Deployments: {stats['running_deployments']}/{stats['total_deployments']} running")
    print(f"  Devices: {stats['online_devices']}/{stats['total_devices']} online")
    print(f"  Data Syncs: {stats['synced']}/{stats['total_syncs']} synced")
    print(f"  Unacknowledged Alerts: {stats['unacked_alerts']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                     Edge Computing Platform                         │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Edge Locations:               {stats['total_locations']:>12}                      │")
    print(f"│ Edge Nodes:                   {stats['online_nodes']:>12} online               │")
    print(f"│ Running Deployments:          {stats['running_deployments']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Connected Devices:            {stats['online_devices']:>12}                      │")
    print(f"│ Data Syncs Active:            {stats['synced']:>12}                      │")
    print(f"│ Latency Reduction:            {latency_stats['latency_reduction_percent']:>11}%                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Edge Computing Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
