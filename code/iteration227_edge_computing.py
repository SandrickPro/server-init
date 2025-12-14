#!/usr/bin/env python3
"""
Server Init - Iteration 227: Edge Computing Platform
Платформа граничных вычислений

Функционал:
- Edge Node Management - управление edge узлами
- Workload Distribution - распределение нагрузки
- Data Synchronization - синхронизация данных
- Offline Operations - оффлайн операции
- Edge Analytics - edge аналитика
- Config Propagation - распространение конфигов
- Health Monitoring - мониторинг здоровья
- Deployment Orchestration - оркестрация деплоя
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid


class NodeStatus(Enum):
    """Статус узла"""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    PROVISIONING = "provisioning"


class NodeType(Enum):
    """Тип узла"""
    GATEWAY = "gateway"
    COMPUTE = "compute"
    STORAGE = "storage"
    SENSOR = "sensor"
    HYBRID = "hybrid"


class SyncStatus(Enum):
    """Статус синхронизации"""
    SYNCED = "synced"
    SYNCING = "syncing"
    PENDING = "pending"
    FAILED = "failed"
    OFFLINE = "offline"


class WorkloadType(Enum):
    """Тип нагрузки"""
    CONTAINER = "container"
    FUNCTION = "function"
    MODEL = "model"
    DATA_PIPELINE = "data_pipeline"


@dataclass
class EdgeLocation:
    """Локация edge узла"""
    location_id: str
    name: str = ""
    region: str = ""
    zone: str = ""
    latitude: float = 0
    longitude: float = 0


@dataclass
class NodeResources:
    """Ресурсы узла"""
    cpu_cores: int = 4
    memory_gb: float = 8.0
    storage_gb: float = 100.0
    gpu_count: int = 0
    cpu_used_percent: float = 0
    memory_used_percent: float = 0
    storage_used_percent: float = 0


@dataclass
class EdgeNode:
    """Edge узел"""
    node_id: str
    name: str = ""
    
    # Type and status
    node_type: NodeType = NodeType.COMPUTE
    status: NodeStatus = NodeStatus.PROVISIONING
    
    # Location
    location: Optional[EdgeLocation] = None
    
    # Resources
    resources: NodeResources = field(default_factory=NodeResources)
    
    # Networking
    ip_address: str = ""
    public_ip: str = ""
    vpn_connected: bool = False
    
    # Sync
    sync_status: SyncStatus = SyncStatus.PENDING
    last_sync: Optional[datetime] = None
    
    # Workloads
    workloads: List[str] = field(default_factory=list)
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Times
    registered_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: Optional[datetime] = None


@dataclass
class EdgeWorkload:
    """Edge нагрузка"""
    workload_id: str
    name: str = ""
    
    # Type
    workload_type: WorkloadType = WorkloadType.CONTAINER
    
    # Image/code
    image: str = ""
    
    # Resources required
    cpu_cores: float = 0.5
    memory_mb: int = 512
    
    # Placement
    node_selector: Dict[str, str] = field(default_factory=dict)
    replicas: int = 1
    
    # Deployed nodes
    deployed_nodes: List[str] = field(default_factory=list)
    
    # Status
    is_running: bool = False
    
    # Config
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Times
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DataSync:
    """Синхронизация данных"""
    sync_id: str
    node_id: str = ""
    
    # Data info
    data_type: str = ""  # config, model, dataset
    data_key: str = ""
    data_version: str = ""
    data_size_bytes: int = 0
    
    # Status
    status: SyncStatus = SyncStatus.PENDING
    
    # Times
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Progress
    progress_percent: float = 0


@dataclass
class EdgeMetrics:
    """Метрики edge узла"""
    metrics_id: str
    node_id: str = ""
    
    # Performance
    cpu_percent: float = 0
    memory_percent: float = 0
    network_rx_mbps: float = 0
    network_tx_mbps: float = 0
    
    # Edge specific
    latency_to_cloud_ms: float = 0
    requests_processed: int = 0
    offline_operations: int = 0
    
    # Collected
    collected_at: datetime = field(default_factory=datetime.now)


class EdgeNodeManager:
    """Менеджер edge узлов"""
    
    def __init__(self):
        self.nodes: Dict[str, EdgeNode] = {}
        self.locations: Dict[str, EdgeLocation] = {}
        
    def create_location(self, name: str, region: str, zone: str,
                       lat: float = 0, lon: float = 0) -> EdgeLocation:
        """Создание локации"""
        location = EdgeLocation(
            location_id=f"loc_{uuid.uuid4().hex[:8]}",
            name=name,
            region=region,
            zone=zone,
            latitude=lat,
            longitude=lon
        )
        self.locations[location.location_id] = location
        return location
        
    def register_node(self, name: str, node_type: NodeType,
                     location_id: str = "", ip: str = "") -> EdgeNode:
        """Регистрация узла"""
        location = self.locations.get(location_id)
        
        node = EdgeNode(
            node_id=f"edge_{uuid.uuid4().hex[:8]}",
            name=name,
            node_type=node_type,
            location=location,
            ip_address=ip or f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
        )
        
        self.nodes[node.node_id] = node
        return node
        
    def set_online(self, node_id: str) -> bool:
        """Перевод в online"""
        node = self.nodes.get(node_id)
        if not node:
            return False
        node.status = NodeStatus.ONLINE
        node.last_heartbeat = datetime.now()
        return True
        
    def heartbeat(self, node_id: str) -> bool:
        """Обновление heartbeat"""
        node = self.nodes.get(node_id)
        if not node:
            return False
        node.last_heartbeat = datetime.now()
        return True
        
    def get_available_nodes(self, selector: Dict[str, str] = None) -> List[EdgeNode]:
        """Получение доступных узлов"""
        available = []
        for node in self.nodes.values():
            if node.status != NodeStatus.ONLINE:
                continue
                
            if selector:
                match = all(node.labels.get(k) == v for k, v in selector.items())
                if not match:
                    continue
                    
            available.append(node)
        return available


class WorkloadScheduler:
    """Планировщик нагрузки"""
    
    def __init__(self, node_manager: EdgeNodeManager):
        self.node_manager = node_manager
        self.workloads: Dict[str, EdgeWorkload] = {}
        
    def create_workload(self, name: str, workload_type: WorkloadType,
                       image: str, cpu: float = 0.5, memory: int = 512,
                       replicas: int = 1) -> EdgeWorkload:
        """Создание нагрузки"""
        workload = EdgeWorkload(
            workload_id=f"wl_{uuid.uuid4().hex[:8]}",
            name=name,
            workload_type=workload_type,
            image=image,
            cpu_cores=cpu,
            memory_mb=memory,
            replicas=replicas
        )
        self.workloads[workload.workload_id] = workload
        return workload
        
    def schedule(self, workload_id: str) -> List[str]:
        """Планирование нагрузки"""
        workload = self.workloads.get(workload_id)
        if not workload:
            return []
            
        available = self.node_manager.get_available_nodes(workload.node_selector)
        
        # Simple round-robin scheduling
        deployed = []
        for i in range(min(workload.replicas, len(available))):
            node = available[i % len(available)]
            node.workloads.append(workload_id)
            deployed.append(node.node_id)
            
        workload.deployed_nodes = deployed
        workload.is_running = len(deployed) > 0
        
        return deployed


class DataSyncManager:
    """Менеджер синхронизации данных"""
    
    def __init__(self):
        self.syncs: Dict[str, DataSync] = {}
        self.data_store: Dict[str, Any] = {}  # Cloud data store
        
    def register_data(self, key: str, data: Any, version: str = "1.0"):
        """Регистрация данных"""
        self.data_store[key] = {
            "data": data,
            "version": version,
            "size": len(str(data))
        }
        
    def create_sync(self, node_id: str, data_key: str,
                   data_type: str) -> Optional[DataSync]:
        """Создание задачи синхронизации"""
        if data_key not in self.data_store:
            return None
            
        data_info = self.data_store[data_key]
        
        sync = DataSync(
            sync_id=f"sync_{uuid.uuid4().hex[:8]}",
            node_id=node_id,
            data_type=data_type,
            data_key=data_key,
            data_version=data_info["version"],
            data_size_bytes=data_info["size"]
        )
        
        self.syncs[sync.sync_id] = sync
        return sync
        
    def start_sync(self, sync_id: str) -> bool:
        """Запуск синхронизации"""
        sync = self.syncs.get(sync_id)
        if not sync:
            return False
        sync.status = SyncStatus.SYNCING
        sync.started_at = datetime.now()
        return True
        
    def complete_sync(self, sync_id: str) -> bool:
        """Завершение синхронизации"""
        sync = self.syncs.get(sync_id)
        if not sync:
            return False
        sync.status = SyncStatus.SYNCED
        sync.completed_at = datetime.now()
        sync.progress_percent = 100
        return True


class EdgeComputingPlatform:
    """Платформа граничных вычислений"""
    
    def __init__(self):
        self.node_manager = EdgeNodeManager()
        self.scheduler = WorkloadScheduler(self.node_manager)
        self.sync_manager = DataSyncManager()
        self.metrics: List[EdgeMetrics] = []
        
    def create_location(self, name: str, region: str, zone: str) -> EdgeLocation:
        """Создание локации"""
        return self.node_manager.create_location(name, region, zone)
        
    def register_node(self, name: str, node_type: NodeType,
                     location_id: str = "") -> EdgeNode:
        """Регистрация узла"""
        node = self.node_manager.register_node(name, node_type, location_id)
        return node
        
    def provision_node(self, node_id: str, cpu: int = 4, memory: float = 8.0,
                      storage: float = 100.0) -> bool:
        """Провижионинг узла"""
        node = self.node_manager.nodes.get(node_id)
        if not node:
            return False
            
        node.resources = NodeResources(
            cpu_cores=cpu,
            memory_gb=memory,
            storage_gb=storage
        )
        node.status = NodeStatus.ONLINE
        node.last_heartbeat = datetime.now()
        
        return True
        
    def deploy_workload(self, name: str, workload_type: WorkloadType,
                       image: str, replicas: int = 1,
                       selector: Dict[str, str] = None) -> EdgeWorkload:
        """Деплой нагрузки"""
        workload = self.scheduler.create_workload(
            name, workload_type, image, replicas=replicas
        )
        if selector:
            workload.node_selector = selector
            
        self.scheduler.schedule(workload.workload_id)
        return workload
        
    def sync_data(self, node_id: str, data_key: str, data_type: str) -> Optional[DataSync]:
        """Синхронизация данных на узел"""
        sync = self.sync_manager.create_sync(node_id, data_key, data_type)
        if sync:
            self.sync_manager.start_sync(sync.sync_id)
            # Simulate sync completion
            self.sync_manager.complete_sync(sync.sync_id)
            
            # Update node sync status
            node = self.node_manager.nodes.get(node_id)
            if node:
                node.sync_status = SyncStatus.SYNCED
                node.last_sync = datetime.now()
                
        return sync
        
    def collect_metrics(self, node_id: str) -> EdgeMetrics:
        """Сбор метрик"""
        metrics = EdgeMetrics(
            metrics_id=f"met_{uuid.uuid4().hex[:8]}",
            node_id=node_id,
            cpu_percent=random.uniform(10, 80),
            memory_percent=random.uniform(20, 70),
            network_rx_mbps=random.uniform(1, 100),
            network_tx_mbps=random.uniform(1, 50),
            latency_to_cloud_ms=random.uniform(5, 200),
            requests_processed=random.randint(100, 10000),
            offline_operations=random.randint(0, 100)
        )
        self.metrics.append(metrics)
        return metrics
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        nodes = list(self.node_manager.nodes.values())
        online = [n for n in nodes if n.status == NodeStatus.ONLINE]
        
        by_type = {}
        for n in nodes:
            t = n.node_type.value
            if t not in by_type:
                by_type[t] = 0
            by_type[t] += 1
            
        by_location = {}
        for n in nodes:
            loc = n.location.name if n.location else "unassigned"
            if loc not in by_location:
                by_location[loc] = 0
            by_location[loc] += 1
            
        workloads = list(self.scheduler.workloads.values())
        running = [w for w in workloads if w.is_running]
        
        return {
            "total_nodes": len(nodes),
            "online_nodes": len(online),
            "by_type": by_type,
            "by_location": by_location,
            "total_workloads": len(workloads),
            "running_workloads": len(running),
            "total_syncs": len(self.sync_manager.syncs),
            "locations": len(self.node_manager.locations)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 227: Edge Computing Platform")
    print("=" * 60)
    
    platform = EdgeComputingPlatform()
    print("✓ Edge Computing Platform created")
    
    # Create locations
    print("\n📍 Creating Edge Locations...")
    
    locations = [
        platform.create_location("US West", "us-west-2", "zone-a"),
        platform.create_location("US East", "us-east-1", "zone-b"),
        platform.create_location("EU Central", "eu-central-1", "zone-a"),
        platform.create_location("Asia Pacific", "ap-southeast-1", "zone-a"),
    ]
    
    for loc in locations:
        print(f"  ✓ {loc.name} ({loc.region}/{loc.zone})")
        
    # Register nodes
    print("\n🖥 Registering Edge Nodes...")
    
    nodes_config = [
        ("edge-gw-usw-1", NodeType.GATEWAY, locations[0].location_id, {"tier": "gateway"}),
        ("edge-compute-usw-1", NodeType.COMPUTE, locations[0].location_id, {"tier": "compute"}),
        ("edge-compute-usw-2", NodeType.COMPUTE, locations[0].location_id, {"tier": "compute"}),
        ("edge-gw-use-1", NodeType.GATEWAY, locations[1].location_id, {"tier": "gateway"}),
        ("edge-compute-use-1", NodeType.COMPUTE, locations[1].location_id, {"tier": "compute"}),
        ("edge-storage-eu-1", NodeType.STORAGE, locations[2].location_id, {"tier": "storage"}),
        ("edge-compute-eu-1", NodeType.COMPUTE, locations[2].location_id, {"tier": "compute"}),
        ("edge-sensor-ap-1", NodeType.SENSOR, locations[3].location_id, {"tier": "sensor"}),
    ]
    
    nodes = []
    for name, ntype, loc_id, labels in nodes_config:
        node = platform.register_node(name, ntype, loc_id)
        node.labels = labels
        nodes.append(node)
        
        type_icons = {
            NodeType.GATEWAY: "🌐",
            NodeType.COMPUTE: "💻",
            NodeType.STORAGE: "💾",
            NodeType.SENSOR: "📡",
            NodeType.HYBRID: "🔀"
        }
        print(f"  {type_icons[ntype]} {name} ({ntype.value})")
        
    # Provision nodes
    print("\n⚙️ Provisioning Nodes...")
    
    resource_configs = [
        (8, 16.0, 200.0),  # Gateway
        (4, 8.0, 100.0),   # Compute
        (4, 8.0, 100.0),
        (8, 16.0, 200.0),
        (4, 8.0, 100.0),
        (2, 4.0, 500.0),   # Storage
        (4, 8.0, 100.0),
        (1, 2.0, 32.0),    # Sensor
    ]
    
    for i, node in enumerate(nodes):
        cpu, mem, storage = resource_configs[i]
        platform.provision_node(node.node_id, cpu, mem, storage)
        
    print(f"  ✓ Provisioned {len(nodes)} nodes")
    
    # Register data for sync
    print("\n📦 Registering Data for Sync...")
    
    platform.sync_manager.register_data("ml-model-v1", {"type": "model", "size": 100}, "1.0.0")
    platform.sync_manager.register_data("config-v1", {"type": "config", "settings": {}}, "1.0.0")
    platform.sync_manager.register_data("dataset-v1", {"type": "dataset", "rows": 10000}, "1.0.0")
    
    print(f"  ✓ Registered {len(platform.sync_manager.data_store)} data items")
    
    # Sync data to nodes
    print("\n🔄 Syncing Data to Nodes...")
    
    for node in nodes[:5]:
        sync = platform.sync_data(node.node_id, "config-v1", "config")
        if sync:
            print(f"  ✓ {node.name}: config synced")
            
    # Deploy workloads
    print("\n🚀 Deploying Workloads...")
    
    workloads_config = [
        ("inference-service", WorkloadType.MODEL, "ml-inference:latest", 3, {"tier": "compute"}),
        ("data-collector", WorkloadType.CONTAINER, "data-collector:latest", 4, {}),
        ("edge-function", WorkloadType.FUNCTION, "edge-func:latest", 2, {"tier": "gateway"}),
        ("analytics-pipeline", WorkloadType.DATA_PIPELINE, "analytics:latest", 2, {"tier": "compute"}),
    ]
    
    workloads = []
    for name, wtype, image, replicas, selector in workloads_config:
        workload = platform.deploy_workload(name, wtype, image, replicas, selector)
        workloads.append(workload)
        
        type_icons = {
            WorkloadType.CONTAINER: "📦",
            WorkloadType.FUNCTION: "⚡",
            WorkloadType.MODEL: "🤖",
            WorkloadType.DATA_PIPELINE: "🔀"
        }
        deployed = len(workload.deployed_nodes)
        print(f"  {type_icons[wtype]} {name}: {deployed} replicas deployed")
        
    # Collect metrics
    print("\n📊 Collecting Metrics...")
    
    for node in nodes:
        for _ in range(3):
            platform.collect_metrics(node.node_id)
            
    print(f"  ✓ Collected metrics from {len(nodes)} nodes")
    
    # Display nodes
    print("\n🖥 Edge Nodes:")
    
    print("\n  ┌────────────────────────┬──────────┬──────────┬────────┬──────────┐")
    print("  │ Node                   │ Type     │ Status   │ CPU    │ Location │")
    print("  ├────────────────────────┼──────────┼──────────┼────────┼──────────┤")
    
    for node in platform.node_manager.nodes.values():
        name = node.name[:20].ljust(20)
        ntype = node.node_type.value[:8].ljust(8)
        
        status_icons = {
            NodeStatus.ONLINE: "🟢",
            NodeStatus.OFFLINE: "🔴",
            NodeStatus.DEGRADED: "🟡",
            NodeStatus.MAINTENANCE: "🔧",
            NodeStatus.PROVISIONING: "⏳"
        }
        status = f"{status_icons.get(node.status, '⚪')}"[:8].ljust(8)
        
        cpu = f"{node.resources.cpu_cores}c"[:6].ljust(6)
        loc = (node.location.name if node.location else "N/A")[:8].ljust(8)
        
        print(f"  │ {name} │ {ntype} │ {status} │ {cpu} │ {loc} │")
        
    print("  └────────────────────────┴──────────┴──────────┴────────┴──────────┘")
    
    # Workload distribution
    print("\n📦 Workload Distribution:")
    
    for workload in workloads:
        print(f"\n  {workload.name}:")
        for node_id in workload.deployed_nodes:
            node = platform.node_manager.nodes.get(node_id)
            if node:
                print(f"    └─ {node.name}")
                
    # Nodes by type
    print("\n📊 Nodes by Type:")
    
    stats = platform.get_statistics()
    
    type_icons = {
        "gateway": "🌐",
        "compute": "💻",
        "storage": "💾",
        "sensor": "📡",
        "hybrid": "🔀"
    }
    
    for ntype, count in stats["by_type"].items():
        icon = type_icons.get(ntype, "⚪")
        bar = "█" * count + "░" * (5 - count)
        print(f"  {icon} {ntype:10s} [{bar}] {count}")
        
    # Nodes by location
    print("\n📍 Nodes by Location:")
    
    for loc, count in stats["by_location"].items():
        bar = "█" * count + "░" * (5 - count)
        print(f"  {loc:15s} [{bar}] {count}")
        
    # Node metrics
    print("\n📈 Node Performance:")
    
    for node in nodes[:4]:
        node_metrics = [m for m in platform.metrics if m.node_id == node.node_id]
        if node_metrics:
            latest = node_metrics[-1]
            print(f"  {node.name}:")
            print(f"    CPU: {latest.cpu_percent:.0f}%, Mem: {latest.memory_percent:.0f}%")
            print(f"    Latency: {latest.latency_to_cloud_ms:.0f}ms")
            
    # Sync status
    print("\n🔄 Sync Status:")
    
    synced = len([s for s in platform.sync_manager.syncs.values() if s.status == SyncStatus.SYNCED])
    total = len(platform.sync_manager.syncs)
    
    print(f"  Synced: {synced}/{total}")
    
    # Statistics
    print("\n📈 Platform Statistics:")
    
    print(f"\n  Total Nodes: {stats['total_nodes']}")
    print(f"  Online: {stats['online_nodes']}")
    print(f"  Locations: {stats['locations']}")
    print(f"  Workloads: {stats['total_workloads']} ({stats['running_workloads']} running)")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                     Edge Computing Dashboard                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Edge Nodes:              {stats['total_nodes']:>12}                        │")
    print(f"│ Online Nodes:                  {stats['online_nodes']:>12}                        │")
    print(f"│ Edge Locations:                {stats['locations']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Running Workloads:             {stats['running_workloads']:>12}                        │")
    print(f"│ Data Syncs Completed:          {synced:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Edge Computing Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
