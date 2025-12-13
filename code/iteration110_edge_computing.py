#!/usr/bin/env python3
"""
Server Init - Iteration 110: Edge Computing Platform
Платформа граничных вычислений

Функционал:
- Edge Node Management - управление edge узлами
- Workload Distribution - распределение нагрузки
- Data Synchronization - синхронизация данных
- Offline Support - поддержка offline
- Edge Analytics - аналитика на edge
- Device Management - управление устройствами
- Latency Optimization - оптимизация задержек
- Geo-Distribution - гео-распределение
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
from collections import defaultdict
import uuid
import random
import math


class EdgeNodeStatus(Enum):
    """Статус edge узла"""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    PROVISIONING = "provisioning"


class WorkloadType(Enum):
    """Тип нагрузки"""
    COMPUTE = "compute"
    INFERENCE = "inference"
    CACHING = "caching"
    STREAMING = "streaming"
    IOT_GATEWAY = "iot_gateway"
    DATA_PROCESSING = "data_processing"


class SyncMode(Enum):
    """Режим синхронизации"""
    REALTIME = "realtime"
    BATCH = "batch"
    ON_DEMAND = "on_demand"
    OFFLINE_FIRST = "offline_first"


class DeviceType(Enum):
    """Тип устройства"""
    SENSOR = "sensor"
    CAMERA = "camera"
    GATEWAY = "gateway"
    INDUSTRIAL = "industrial"
    VEHICLE = "vehicle"
    WEARABLE = "wearable"


@dataclass
class GeoLocation:
    """Геолокация"""
    latitude: float = 0.0
    longitude: float = 0.0
    region: str = ""
    country: str = ""
    city: str = ""


@dataclass
class EdgeNode:
    """Edge узел"""
    node_id: str
    name: str = ""
    
    # Location
    location: GeoLocation = field(default_factory=GeoLocation)
    
    # Status
    status: EdgeNodeStatus = EdgeNodeStatus.PROVISIONING
    
    # Resources
    cpu_cores: int = 4
    memory_gb: float = 8.0
    storage_gb: float = 100.0
    gpu_available: bool = False
    
    # Utilization
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    storage_usage: float = 0.0
    
    # Network
    bandwidth_mbps: float = 100.0
    latency_to_cloud_ms: float = 50.0
    
    # Workloads
    workloads: List[str] = field(default_factory=list)
    
    # Devices
    connected_devices: int = 0
    
    # Last seen
    last_heartbeat: datetime = field(default_factory=datetime.now)
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class EdgeWorkload:
    """Нагрузка на edge"""
    workload_id: str
    name: str = ""
    
    # Type
    workload_type: WorkloadType = WorkloadType.COMPUTE
    
    # Image/Code
    image: str = ""
    version: str = ""
    
    # Requirements
    cpu_request: float = 0.5
    memory_request_mb: float = 512.0
    gpu_required: bool = False
    
    # Placement
    placement_strategy: str = "nearest"  # nearest, spread, binpack
    target_nodes: List[str] = field(default_factory=list)
    
    # Sync
    sync_mode: SyncMode = SyncMode.BATCH
    
    # Status
    deployed_nodes: List[str] = field(default_factory=list)
    
    # Config
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EdgeDevice:
    """Edge устройство"""
    device_id: str
    name: str = ""
    
    # Type
    device_type: DeviceType = DeviceType.SENSOR
    
    # Connection
    connected_to_node: Optional[str] = None
    online: bool = False
    
    # Metadata
    model: str = ""
    firmware_version: str = ""
    
    # Data
    last_data_received: Optional[datetime] = None
    data_points_today: int = 0
    
    # Location
    location: GeoLocation = field(default_factory=GeoLocation)


@dataclass
class DataSync:
    """Синхронизация данных"""
    sync_id: str
    
    # Source/Target
    source_node: str = ""
    target: str = ""  # cloud or another node
    
    # Mode
    sync_mode: SyncMode = SyncMode.BATCH
    
    # Status
    last_sync: Optional[datetime] = None
    pending_records: int = 0
    synced_records: int = 0
    
    # Config
    batch_size: int = 1000
    sync_interval_seconds: int = 60


@dataclass
class EdgeAnalytics:
    """Аналитика edge"""
    node_id: str
    
    # Metrics
    requests_processed: int = 0
    data_points_collected: int = 0
    events_generated: int = 0
    
    # Latency
    avg_processing_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    
    # Bandwidth
    data_sent_mb: float = 0.0
    data_received_mb: float = 0.0
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)


class EdgeNodeManager:
    """Менеджер edge узлов"""
    
    def __init__(self):
        self.nodes: Dict[str, EdgeNode] = {}
        
    def register(self, name: str, location: GeoLocation,
                  **kwargs) -> EdgeNode:
        """Регистрация узла"""
        node = EdgeNode(
            node_id=f"edge_{uuid.uuid4().hex[:8]}",
            name=name,
            location=location,
            status=EdgeNodeStatus.ONLINE,
            **kwargs
        )
        self.nodes[node.node_id] = node
        return node
        
    def update_status(self, node_id: str) -> Dict[str, Any]:
        """Обновление статуса"""
        node = self.nodes.get(node_id)
        if not node:
            return {"status": "not_found"}
            
        # Simulate resource usage
        node.cpu_usage = random.uniform(10, 80)
        node.memory_usage = random.uniform(20, 70)
        node.storage_usage = random.uniform(30, 60)
        node.last_heartbeat = datetime.now()
        
        # Check health
        if node.cpu_usage > 90 or node.memory_usage > 90:
            node.status = EdgeNodeStatus.DEGRADED
        elif random.random() > 0.95:
            node.status = EdgeNodeStatus.OFFLINE
        else:
            node.status = EdgeNodeStatus.ONLINE
            
        return {
            "node_id": node_id,
            "status": node.status.value,
            "cpu_usage": node.cpu_usage,
            "memory_usage": node.memory_usage
        }
        
    def find_nearest(self, location: GeoLocation,
                      available_only: bool = True) -> Optional[EdgeNode]:
        """Поиск ближайшего узла"""
        nodes = list(self.nodes.values())
        
        if available_only:
            nodes = [n for n in nodes if n.status == EdgeNodeStatus.ONLINE]
            
        if not nodes:
            return None
            
        def distance(node):
            # Simplified distance calculation
            lat_diff = node.location.latitude - location.latitude
            lon_diff = node.location.longitude - location.longitude
            return math.sqrt(lat_diff**2 + lon_diff**2)
            
        return min(nodes, key=distance)
        
    def get_by_region(self, region: str) -> List[EdgeNode]:
        """Узлы по региону"""
        return [n for n in self.nodes.values() if n.location.region == region]


class WorkloadOrchestrator:
    """Оркестратор нагрузок"""
    
    def __init__(self, node_manager: EdgeNodeManager):
        self.node_manager = node_manager
        self.workloads: Dict[str, EdgeWorkload] = {}
        
    def create(self, name: str, workload_type: WorkloadType,
                image: str, **kwargs) -> EdgeWorkload:
        """Создание нагрузки"""
        workload = EdgeWorkload(
            workload_id=f"wl_{uuid.uuid4().hex[:8]}",
            name=name,
            workload_type=workload_type,
            image=image,
            **kwargs
        )
        self.workloads[workload.workload_id] = workload
        return workload
        
    def deploy(self, workload_id: str, target_nodes: List[str] = None,
                placement: str = "spread") -> Dict[str, Any]:
        """Развёртывание"""
        workload = self.workloads.get(workload_id)
        if not workload:
            return {"status": "error", "message": "Workload not found"}
            
        # Determine target nodes
        if target_nodes:
            nodes = [self.node_manager.nodes[nid] for nid in target_nodes 
                     if nid in self.node_manager.nodes]
        else:
            nodes = [n for n in self.node_manager.nodes.values()
                     if n.status == EdgeNodeStatus.ONLINE]
                     
        if placement == "spread":
            # Deploy to all matching nodes
            pass
        elif placement == "binpack":
            # Deploy to nodes with most capacity
            nodes = sorted(nodes, key=lambda n: n.cpu_usage)[:3]
            
        deployed = []
        for node in nodes:
            # Check resources
            if node.cpu_usage + workload.cpu_request * 100 <= 100:
                workload.deployed_nodes.append(node.node_id)
                node.workloads.append(workload.workload_id)
                deployed.append(node.node_id)
                
        return {
            "status": "success",
            "workload_id": workload_id,
            "deployed_to": deployed,
            "nodes_count": len(deployed)
        }
        
    def scale(self, workload_id: str, replicas: int) -> Dict[str, Any]:
        """Масштабирование"""
        workload = self.workloads.get(workload_id)
        if not workload:
            return {"status": "error"}
            
        current = len(workload.deployed_nodes)
        
        if replicas > current:
            # Scale up
            available = [n for n in self.node_manager.nodes.values()
                        if n.status == EdgeNodeStatus.ONLINE
                        and n.node_id not in workload.deployed_nodes]
            
            for node in available[:replicas - current]:
                workload.deployed_nodes.append(node.node_id)
                node.workloads.append(workload_id)
                
        elif replicas < current:
            # Scale down
            to_remove = workload.deployed_nodes[replicas:]
            workload.deployed_nodes = workload.deployed_nodes[:replicas]
            
            for node_id in to_remove:
                node = self.node_manager.nodes.get(node_id)
                if node and workload_id in node.workloads:
                    node.workloads.remove(workload_id)
                    
        return {
            "status": "success",
            "previous": current,
            "current": len(workload.deployed_nodes)
        }


class DeviceManager:
    """Менеджер устройств"""
    
    def __init__(self, node_manager: EdgeNodeManager):
        self.node_manager = node_manager
        self.devices: Dict[str, EdgeDevice] = {}
        
    def register(self, name: str, device_type: DeviceType,
                  location: GeoLocation = None, **kwargs) -> EdgeDevice:
        """Регистрация устройства"""
        device = EdgeDevice(
            device_id=f"dev_{uuid.uuid4().hex[:8]}",
            name=name,
            device_type=device_type,
            location=location or GeoLocation(),
            **kwargs
        )
        self.devices[device.device_id] = device
        return device
        
    def connect_to_node(self, device_id: str,
                         node_id: str = None) -> Dict[str, Any]:
        """Подключение к узлу"""
        device = self.devices.get(device_id)
        if not device:
            return {"status": "error", "message": "Device not found"}
            
        # Auto-select nearest node if not specified
        if not node_id and device.location:
            nearest = self.node_manager.find_nearest(device.location)
            if nearest:
                node_id = nearest.node_id
                
        if not node_id:
            return {"status": "error", "message": "No available node"}
            
        node = self.node_manager.nodes.get(node_id)
        if not node:
            return {"status": "error", "message": "Node not found"}
            
        device.connected_to_node = node_id
        device.online = True
        node.connected_devices += 1
        
        return {
            "status": "success",
            "device_id": device_id,
            "connected_to": node_id,
            "node_name": node.name
        }
        
    def receive_data(self, device_id: str, data: Dict[str, Any]) -> bool:
        """Получение данных"""
        device = self.devices.get(device_id)
        if not device:
            return False
            
        device.last_data_received = datetime.now()
        device.data_points_today += 1
        return True


class DataSyncManager:
    """Менеджер синхронизации"""
    
    def __init__(self):
        self.syncs: Dict[str, DataSync] = {}
        
    def create(self, source_node: str, target: str,
                sync_mode: SyncMode = SyncMode.BATCH,
                **kwargs) -> DataSync:
        """Создание синхронизации"""
        sync = DataSync(
            sync_id=f"sync_{uuid.uuid4().hex[:8]}",
            source_node=source_node,
            target=target,
            sync_mode=sync_mode,
            **kwargs
        )
        self.syncs[sync.sync_id] = sync
        return sync
        
    async def execute_sync(self, sync_id: str) -> Dict[str, Any]:
        """Выполнение синхронизации"""
        sync = self.syncs.get(sync_id)
        if not sync:
            return {"status": "error"}
            
        # Simulate sync
        await asyncio.sleep(0.1)
        
        synced = random.randint(100, sync.batch_size)
        sync.synced_records += synced
        sync.pending_records = max(0, sync.pending_records - synced)
        sync.last_sync = datetime.now()
        
        return {
            "status": "success",
            "synced_records": synced,
            "pending": sync.pending_records
        }


class EdgeComputingPlatform:
    """Платформа граничных вычислений"""
    
    def __init__(self):
        self.node_manager = EdgeNodeManager()
        self.workload_orchestrator = WorkloadOrchestrator(self.node_manager)
        self.device_manager = DeviceManager(self.node_manager)
        self.sync_manager = DataSyncManager()
        
        self.analytics: Dict[str, EdgeAnalytics] = {}
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        nodes = list(self.node_manager.nodes.values())
        online_nodes = len([n for n in nodes if n.status == EdgeNodeStatus.ONLINE])
        
        total_devices = len(self.device_manager.devices)
        online_devices = len([d for d in self.device_manager.devices.values() if d.online])
        
        workloads = list(self.workload_orchestrator.workloads.values())
        deployed_workloads = len([w for w in workloads if w.deployed_nodes])
        
        avg_cpu = sum(n.cpu_usage for n in nodes) / len(nodes) if nodes else 0
        avg_memory = sum(n.memory_usage for n in nodes) / len(nodes) if nodes else 0
        
        return {
            "total_nodes": len(nodes),
            "online_nodes": online_nodes,
            "total_devices": total_devices,
            "online_devices": online_devices,
            "total_workloads": len(workloads),
            "deployed_workloads": deployed_workloads,
            "sync_jobs": len(self.sync_manager.syncs),
            "avg_cpu_usage": avg_cpu,
            "avg_memory_usage": avg_memory
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 110: Edge Computing Platform")
    print("=" * 60)
    
    async def demo():
        platform = EdgeComputingPlatform()
        print("✓ Edge Computing Platform created")
        
        # Register edge nodes
        print("\n🌐 Registering Edge Nodes...")
        
        locations = [
            ("edge-nyc-1", GeoLocation(40.7128, -74.0060, "us-east", "USA", "New York")),
            ("edge-lon-1", GeoLocation(51.5074, -0.1278, "eu-west", "UK", "London")),
            ("edge-tok-1", GeoLocation(35.6762, 139.6503, "ap-north", "Japan", "Tokyo")),
            ("edge-syd-1", GeoLocation(-33.8688, 151.2093, "ap-south", "Australia", "Sydney")),
            ("edge-fra-1", GeoLocation(50.1109, 8.6821, "eu-central", "Germany", "Frankfurt")),
            ("edge-sfo-1", GeoLocation(37.7749, -122.4194, "us-west", "USA", "San Francisco"))
        ]
        
        for name, location in locations:
            node = platform.node_manager.register(
                name, location,
                cpu_cores=8,
                memory_gb=16.0,
                storage_gb=500.0,
                gpu_available=random.random() > 0.5
            )
            status = platform.node_manager.update_status(node.node_id)
            
            status_icon = {"online": "🟢", "offline": "🔴", "degraded": "🟡"}.get(status["status"], "⚪")
            gpu_icon = "🎮" if node.gpu_available else ""
            print(f"  {status_icon} {name} ({location.city}) {gpu_icon}")
            print(f"     CPU: {status['cpu_usage']:.1f}%, Memory: {status['memory_usage']:.1f}%")
            
        # Register devices
        print("\n📱 Registering Devices...")
        
        devices_data = [
            ("temp-sensor-1", DeviceType.SENSOR, GeoLocation(40.71, -74.01, "us-east", "USA", "New York")),
            ("camera-1", DeviceType.CAMERA, GeoLocation(51.51, -0.13, "eu-west", "UK", "London")),
            ("gateway-1", DeviceType.GATEWAY, GeoLocation(35.68, 139.65, "ap-north", "Japan", "Tokyo")),
            ("industrial-1", DeviceType.INDUSTRIAL, GeoLocation(50.11, 8.68, "eu-central", "Germany", "Frankfurt")),
            ("vehicle-1", DeviceType.VEHICLE, GeoLocation(37.77, -122.42, "us-west", "USA", "San Francisco"))
        ]
        
        for name, device_type, location in devices_data:
            device = platform.device_manager.register(name, device_type, location)
            result = platform.device_manager.connect_to_node(device.device_id)
            
            if result["status"] == "success":
                print(f"  ✓ {name} ({device_type.value}) → {result['node_name']}")
                
                # Simulate data reception
                platform.device_manager.receive_data(device.device_id, {"value": random.random()})
            else:
                print(f"  ✗ {name}: {result.get('message', 'Failed')}")
                
        # Create and deploy workloads
        print("\n📦 Deploying Workloads...")
        
        workloads_data = [
            ("ml-inference", WorkloadType.INFERENCE, "ml-model:v1.0", 1.0, 1024),
            ("data-cache", WorkloadType.CACHING, "redis:7.0", 0.5, 512),
            ("stream-processor", WorkloadType.STREAMING, "flink:1.17", 2.0, 2048),
            ("iot-gateway", WorkloadType.IOT_GATEWAY, "gateway:latest", 0.25, 256)
        ]
        
        for name, wl_type, image, cpu, memory in workloads_data:
            workload = platform.workload_orchestrator.create(
                name, wl_type, image,
                cpu_request=cpu,
                memory_request_mb=memory
            )
            
            result = platform.workload_orchestrator.deploy(
                workload.workload_id,
                placement="spread"
            )
            
            print(f"  ✓ {name} ({wl_type.value}): deployed to {result['nodes_count']} nodes")
            
        # Scale a workload
        print("\n📈 Scaling Workloads...")
        
        workloads = list(platform.workload_orchestrator.workloads.values())
        if workloads:
            wl = workloads[0]
            result = platform.workload_orchestrator.scale(wl.workload_id, 5)
            print(f"  ✓ {wl.name}: {result['previous']} → {result['current']} replicas")
            
        # Setup data sync
        print("\n🔄 Setting up Data Synchronization...")
        
        nodes = list(platform.node_manager.nodes.values())
        for node in nodes[:3]:
            sync = platform.sync_manager.create(
                node.node_id, "cloud",
                sync_mode=SyncMode.BATCH,
                batch_size=1000
            )
            sync.pending_records = random.randint(500, 5000)
            
            result = await platform.sync_manager.execute_sync(sync.sync_id)
            print(f"  ✓ {node.name} → cloud: {result['synced_records']} records synced")
            
        # Find nearest node
        print("\n🔍 Finding Nearest Nodes...")
        
        test_locations = [
            GeoLocation(41.8781, -87.6298, "", "USA", "Chicago"),
            GeoLocation(48.8566, 2.3522, "", "France", "Paris")
        ]
        
        for loc in test_locations:
            nearest = platform.node_manager.find_nearest(loc)
            if nearest:
                print(f"  {loc.city} → {nearest.name} ({nearest.location.city})")
                
        # Regional overview
        print("\n🗺️ Regional Overview:")
        
        regions = set(n.location.region for n in platform.node_manager.nodes.values())
        for region in sorted(regions):
            region_nodes = platform.node_manager.get_by_region(region)
            online = len([n for n in region_nodes if n.status == EdgeNodeStatus.ONLINE])
            print(f"  {region}: {online}/{len(region_nodes)} nodes online")
            
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Nodes:")
        print(f"    Total: {stats['total_nodes']}")
        print(f"    Online: {stats['online_nodes']}")
        print(f"    Avg CPU: {stats['avg_cpu_usage']:.1f}%")
        print(f"    Avg Memory: {stats['avg_memory_usage']:.1f}%")
        
        print(f"\n  Devices:")
        print(f"    Total: {stats['total_devices']}")
        print(f"    Online: {stats['online_devices']}")
        
        print(f"\n  Workloads:")
        print(f"    Total: {stats['total_workloads']}")
        print(f"    Deployed: {stats['deployed_workloads']}")
        
        print(f"\n  Sync Jobs: {stats['sync_jobs']}")
        
        # Dashboard
        print("\n📋 Edge Computing Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │              Edge Computing Overview                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Edge Nodes:         {stats['total_nodes']:>10} ({stats['online_nodes']} online)       │")
        print(f"  │ Connected Devices:  {stats['total_devices']:>10} ({stats['online_devices']} online)       │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Workloads:          {stats['total_workloads']:>10}                        │")
        print(f"  │ Deployed:           {stats['deployed_workloads']:>10}                        │")
        print(f"  │ Sync Jobs:          {stats['sync_jobs']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Avg CPU Usage:      {stats['avg_cpu_usage']:>10.1f}%                       │")
        print(f"  │ Avg Memory Usage:   {stats['avg_memory_usage']:>10.1f}%                       │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Edge Computing Platform initialized!")
    print("=" * 60)
