#!/usr/bin/env python3
"""
Server Init - Iteration 322: Virtualization Manager Platform
Платформа управления виртуализацией

Функционал:
- Virtual Machine Management - управление ВМ
- Hypervisor Integration - интеграция с гипервизорами
- Resource Allocation - распределение ресурсов
- VM Templates - шаблоны ВМ
- Snapshots & Cloning - снимки и клонирование
- Live Migration - живая миграция
- HA/Clustering - высокая доступность
- Performance Monitoring - мониторинг производительности
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class HypervisorType(Enum):
    """Тип гипервизора"""
    VMWARE_ESXI = "vmware_esxi"
    MICROSOFT_HYPERV = "microsoft_hyperv"
    KVM = "kvm"
    XEN = "xen"
    PROXMOX = "proxmox"
    NUTANIX = "nutanix"


class VMState(Enum):
    """Состояние ВМ"""
    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"
    SUSPENDED = "suspended"
    MIGRATING = "migrating"
    CREATING = "creating"
    DELETING = "deleting"


class DiskType(Enum):
    """Тип диска"""
    THIN = "thin"
    THICK = "thick"
    THICK_EAGER = "thick_eager"
    RAW = "raw"


class NetworkAdapter(Enum):
    """Тип сетевого адаптера"""
    E1000 = "e1000"
    VMXNET3 = "vmxnet3"
    VIRTIO = "virtio"
    HYPERV = "hyperv"


class BootOrder(Enum):
    """Порядок загрузки"""
    DISK = "disk"
    CDROM = "cdrom"
    NETWORK = "network"
    USB = "usb"


class MigrationMode(Enum):
    """Режим миграции"""
    LIVE = "live"
    COLD = "cold"
    SUSPENDED = "suspended"


@dataclass
class Hypervisor:
    """Гипервизор"""
    hypervisor_id: str
    name: str
    
    # Type
    hypervisor_type: HypervisorType = HypervisorType.KVM
    version: str = ""
    
    # Connection
    hostname: str = ""
    ip_address: str = ""
    
    # Cluster
    cluster_id: str = ""
    
    # Resources
    total_cpu_cores: int = 0
    used_cpu_cores: int = 0
    total_memory_gb: int = 0
    used_memory_gb: int = 0
    total_storage_gb: int = 0
    used_storage_gb: int = 0
    
    # Performance
    cpu_percent: float = 0
    memory_percent: float = 0
    
    # VMs
    vm_count: int = 0
    max_vms: int = 100
    
    # Status
    is_online: bool = True
    is_maintenance: bool = False
    
    # Uptime
    uptime_seconds: int = 0


@dataclass
class Cluster:
    """Кластер гипервизоров"""
    cluster_id: str
    name: str
    
    # Hypervisors
    hypervisor_ids: List[str] = field(default_factory=list)
    
    # HA settings
    ha_enabled: bool = True
    drs_enabled: bool = True  # Distributed Resource Scheduler
    
    # Total resources
    total_cpu_cores: int = 0
    total_memory_gb: int = 0
    total_storage_gb: int = 0
    
    # VM count
    vm_count: int = 0


@dataclass
class VirtualNetwork:
    """Виртуальная сеть"""
    network_id: str
    name: str
    
    # VLAN
    vlan_id: int = 0
    
    # Network
    network: str = ""  # CIDR
    gateway: str = ""
    
    # Type
    is_management: bool = False
    is_storage: bool = False
    is_vmotion: bool = False
    
    # MTU
    mtu: int = 1500


@dataclass
class VirtualDisk:
    """Виртуальный диск"""
    disk_id: str
    vm_id: str
    
    # Name
    name: str = ""
    
    # Type
    disk_type: DiskType = DiskType.THIN
    
    # Size
    size_gb: int = 50
    used_gb: int = 0
    
    # Datastore
    datastore_id: str = ""
    
    # Controller
    controller: str = "scsi"
    unit_number: int = 0
    
    # Performance
    iops: int = 0
    throughput_mbps: float = 0


@dataclass
class NetworkInterface:
    """Сетевой интерфейс ВМ"""
    nic_id: str
    vm_id: str
    
    # Name
    name: str = ""
    
    # Network
    network_id: str = ""
    
    # MAC
    mac_address: str = ""
    
    # IP
    ip_address: str = ""
    
    # Adapter
    adapter_type: NetworkAdapter = NetworkAdapter.VIRTIO
    
    # Status
    is_connected: bool = True


@dataclass
class VMSnapshot:
    """Снимок ВМ"""
    snapshot_id: str
    vm_id: str
    
    # Name
    name: str = ""
    description: str = ""
    
    # Parent
    parent_snapshot_id: Optional[str] = None
    
    # Size
    size_gb: float = 0
    
    # Include memory
    memory_included: bool = False
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class VMTemplate:
    """Шаблон ВМ"""
    template_id: str
    name: str
    
    # Guest OS
    guest_os: str = ""
    
    # Resources
    cpu_cores: int = 2
    memory_gb: int = 4
    disk_size_gb: int = 50
    
    # Description
    description: str = ""
    
    # Version
    version: str = "1.0"
    
    # Customization
    customization_spec: Dict[str, Any] = field(default_factory=dict)
    
    # Usage
    usage_count: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class VirtualMachine:
    """Виртуальная машина"""
    vm_id: str
    name: str
    
    # State
    state: VMState = VMState.STOPPED
    
    # Hypervisor
    hypervisor_id: str = ""
    cluster_id: str = ""
    
    # Template
    template_id: str = ""
    
    # Guest OS
    guest_os: str = ""
    tools_status: str = "not_installed"
    
    # Resources
    cpu_cores: int = 2
    memory_gb: int = 4
    
    # Reserved
    cpu_reservation_mhz: int = 0
    memory_reservation_gb: int = 0
    
    # Limits
    cpu_limit_mhz: int = 0
    memory_limit_gb: int = 0
    
    # Disks
    disk_ids: List[str] = field(default_factory=list)
    
    # Network
    nic_ids: List[str] = field(default_factory=list)
    
    # Snapshots
    snapshot_ids: List[str] = field(default_factory=list)
    current_snapshot_id: Optional[str] = None
    
    # Performance
    cpu_percent: float = 0
    memory_percent: float = 0
    disk_iops: int = 0
    network_mbps: float = 0
    
    # IP
    primary_ip: str = ""
    
    # Boot
    boot_order: List[BootOrder] = field(default_factory=lambda: [BootOrder.DISK])
    
    # BIOS/UEFI
    firmware: str = "bios"  # bios or uefi
    
    # Annotations
    notes: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    
    # Uptime
    uptime_seconds: int = 0


@dataclass
class MigrationTask:
    """Задача миграции"""
    task_id: str
    vm_id: str
    
    # Mode
    mode: MigrationMode = MigrationMode.LIVE
    
    # Source/Destination
    source_hypervisor_id: str = ""
    dest_hypervisor_id: str = ""
    
    # Status
    status: str = "pending"  # pending, in_progress, completed, failed
    progress_percent: int = 0
    
    # Error
    error_message: str = ""
    
    # Timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class Datastore:
    """Хранилище данных"""
    datastore_id: str
    name: str
    
    # Type
    datastore_type: str = "nfs"  # nfs, iscsi, fc, local, vsan
    
    # Capacity
    total_gb: int = 0
    used_gb: int = 0
    free_gb: int = 0
    
    # Performance
    iops_limit: int = 0
    throughput_limit_mbps: int = 0
    
    # Status
    is_online: bool = True
    is_maintenance: bool = False


class VirtualizationManager:
    """Менеджер виртуализации"""
    
    def __init__(self):
        self.hypervisors: Dict[str, Hypervisor] = {}
        self.clusters: Dict[str, Cluster] = {}
        self.virtual_machines: Dict[str, VirtualMachine] = {}
        self.virtual_disks: Dict[str, VirtualDisk] = {}
        self.network_interfaces: Dict[str, NetworkInterface] = {}
        self.virtual_networks: Dict[str, VirtualNetwork] = {}
        self.snapshots: Dict[str, VMSnapshot] = {}
        self.templates: Dict[str, VMTemplate] = {}
        self.migration_tasks: Dict[str, MigrationTask] = {}
        self.datastores: Dict[str, Datastore] = {}
        
    async def add_hypervisor(self, name: str,
                            hypervisor_type: HypervisorType,
                            hostname: str,
                            ip_address: str,
                            total_cpu: int = 64,
                            total_memory: int = 512,
                            total_storage: int = 10000) -> Hypervisor:
        """Добавление гипервизора"""
        hypervisor = Hypervisor(
            hypervisor_id=f"hv_{uuid.uuid4().hex[:8]}",
            name=name,
            hypervisor_type=hypervisor_type,
            hostname=hostname,
            ip_address=ip_address,
            total_cpu_cores=total_cpu,
            total_memory_gb=total_memory,
            total_storage_gb=total_storage,
            uptime_seconds=random.randint(0, 86400 * 30)
        )
        
        self.hypervisors[hypervisor.hypervisor_id] = hypervisor
        return hypervisor
        
    async def create_cluster(self, name: str,
                            hypervisor_ids: List[str],
                            ha_enabled: bool = True,
                            drs_enabled: bool = True) -> Cluster:
        """Создание кластера"""
        cluster = Cluster(
            cluster_id=f"cluster_{uuid.uuid4().hex[:8]}",
            name=name,
            hypervisor_ids=hypervisor_ids.copy(),
            ha_enabled=ha_enabled,
            drs_enabled=drs_enabled
        )
        
        # Calculate total resources
        for hv_id in hypervisor_ids:
            hv = self.hypervisors.get(hv_id)
            if hv:
                hv.cluster_id = cluster.cluster_id
                cluster.total_cpu_cores += hv.total_cpu_cores
                cluster.total_memory_gb += hv.total_memory_gb
                cluster.total_storage_gb += hv.total_storage_gb
                
        self.clusters[cluster.cluster_id] = cluster
        return cluster
        
    async def create_datastore(self, name: str,
                              datastore_type: str,
                              total_gb: int) -> Datastore:
        """Создание хранилища"""
        datastore = Datastore(
            datastore_id=f"ds_{uuid.uuid4().hex[:8]}",
            name=name,
            datastore_type=datastore_type,
            total_gb=total_gb,
            free_gb=total_gb
        )
        
        self.datastores[datastore.datastore_id] = datastore
        return datastore
        
    async def create_virtual_network(self, name: str,
                                    vlan_id: int,
                                    network: str,
                                    gateway: str) -> VirtualNetwork:
        """Создание виртуальной сети"""
        vnet = VirtualNetwork(
            network_id=f"vnet_{uuid.uuid4().hex[:8]}",
            name=name,
            vlan_id=vlan_id,
            network=network,
            gateway=gateway
        )
        
        self.virtual_networks[vnet.network_id] = vnet
        return vnet
        
    async def create_template(self, name: str,
                             guest_os: str,
                             cpu_cores: int = 2,
                             memory_gb: int = 4,
                             disk_size_gb: int = 50) -> VMTemplate:
        """Создание шаблона ВМ"""
        template = VMTemplate(
            template_id=f"tmpl_{uuid.uuid4().hex[:8]}",
            name=name,
            guest_os=guest_os,
            cpu_cores=cpu_cores,
            memory_gb=memory_gb,
            disk_size_gb=disk_size_gb
        )
        
        self.templates[template.template_id] = template
        return template
        
    async def create_vm(self, name: str,
                       hypervisor_id: str,
                       guest_os: str,
                       cpu_cores: int = 2,
                       memory_gb: int = 4,
                       template_id: str = "") -> Optional[VirtualMachine]:
        """Создание ВМ"""
        hypervisor = self.hypervisors.get(hypervisor_id)
        if not hypervisor:
            return None
            
        # Check resources
        if hypervisor.used_cpu_cores + cpu_cores > hypervisor.total_cpu_cores:
            return None
        if hypervisor.used_memory_gb + memory_gb > hypervisor.total_memory_gb:
            return None
            
        vm = VirtualMachine(
            vm_id=f"vm_{uuid.uuid4().hex[:8]}",
            name=name,
            hypervisor_id=hypervisor_id,
            cluster_id=hypervisor.cluster_id,
            guest_os=guest_os,
            cpu_cores=cpu_cores,
            memory_gb=memory_gb,
            template_id=template_id
        )
        
        # Update hypervisor
        hypervisor.used_cpu_cores += cpu_cores
        hypervisor.used_memory_gb += memory_gb
        hypervisor.vm_count += 1
        
        # Update cluster
        if hypervisor.cluster_id:
            cluster = self.clusters.get(hypervisor.cluster_id)
            if cluster:
                cluster.vm_count += 1
                
        # Update template usage
        if template_id:
            template = self.templates.get(template_id)
            if template:
                template.usage_count += 1
                
        self.virtual_machines[vm.vm_id] = vm
        return vm
        
    async def add_disk_to_vm(self, vm_id: str,
                            size_gb: int,
                            disk_type: DiskType = DiskType.THIN,
                            datastore_id: str = "") -> Optional[VirtualDisk]:
        """Добавление диска к ВМ"""
        vm = self.virtual_machines.get(vm_id)
        if not vm:
            return None
            
        disk = VirtualDisk(
            disk_id=f"disk_{uuid.uuid4().hex[:8]}",
            vm_id=vm_id,
            name=f"Disk {len(vm.disk_ids) + 1}",
            disk_type=disk_type,
            size_gb=size_gb,
            datastore_id=datastore_id,
            unit_number=len(vm.disk_ids)
        )
        
        # Update datastore
        if datastore_id:
            ds = self.datastores.get(datastore_id)
            if ds:
                ds.used_gb += size_gb
                ds.free_gb = ds.total_gb - ds.used_gb
                
        self.virtual_disks[disk.disk_id] = disk
        vm.disk_ids.append(disk.disk_id)
        
        return disk
        
    async def add_nic_to_vm(self, vm_id: str,
                           network_id: str,
                           adapter_type: NetworkAdapter = NetworkAdapter.VIRTIO) -> Optional[NetworkInterface]:
        """Добавление сетевого интерфейса"""
        vm = self.virtual_machines.get(vm_id)
        network = self.virtual_networks.get(network_id)
        
        if not vm or not network:
            return None
            
        nic = NetworkInterface(
            nic_id=f"nic_{uuid.uuid4().hex[:8]}",
            vm_id=vm_id,
            name=f"NIC {len(vm.nic_ids) + 1}",
            network_id=network_id,
            adapter_type=adapter_type,
            mac_address=":".join([f"{random.randint(0, 255):02x}" for _ in range(6)])
        )
        
        # Assign IP
        base = network.network.split("/")[0].rsplit(".", 1)[0]
        nic.ip_address = f"{base}.{random.randint(10, 250)}"
        
        if not vm.primary_ip:
            vm.primary_ip = nic.ip_address
            
        self.network_interfaces[nic.nic_id] = nic
        vm.nic_ids.append(nic.nic_id)
        
        return nic
        
    async def start_vm(self, vm_id: str) -> bool:
        """Запуск ВМ"""
        vm = self.virtual_machines.get(vm_id)
        if not vm or vm.state == VMState.RUNNING:
            return False
            
        vm.state = VMState.RUNNING
        vm.started_at = datetime.now()
        vm.tools_status = "running"
        
        return True
        
    async def stop_vm(self, vm_id: str) -> bool:
        """Остановка ВМ"""
        vm = self.virtual_machines.get(vm_id)
        if not vm or vm.state == VMState.STOPPED:
            return False
            
        vm.state = VMState.STOPPED
        vm.uptime_seconds += int((datetime.now() - vm.started_at).total_seconds()) if vm.started_at else 0
        vm.started_at = None
        
        return True
        
    async def create_snapshot(self, vm_id: str,
                             name: str,
                             description: str = "",
                             include_memory: bool = False) -> Optional[VMSnapshot]:
        """Создание снимка"""
        vm = self.virtual_machines.get(vm_id)
        if not vm:
            return None
            
        snapshot = VMSnapshot(
            snapshot_id=f"snap_{uuid.uuid4().hex[:8]}",
            vm_id=vm_id,
            name=name,
            description=description,
            parent_snapshot_id=vm.current_snapshot_id,
            memory_included=include_memory,
            size_gb=random.uniform(0.5, 5)
        )
        
        self.snapshots[snapshot.snapshot_id] = snapshot
        vm.snapshot_ids.append(snapshot.snapshot_id)
        vm.current_snapshot_id = snapshot.snapshot_id
        
        return snapshot
        
    async def delete_snapshot(self, snapshot_id: str) -> bool:
        """Удаление снимка"""
        snapshot = self.snapshots.get(snapshot_id)
        if not snapshot:
            return False
            
        vm = self.virtual_machines.get(snapshot.vm_id)
        if vm:
            vm.snapshot_ids.remove(snapshot_id)
            if vm.current_snapshot_id == snapshot_id:
                vm.current_snapshot_id = snapshot.parent_snapshot_id
                
        del self.snapshots[snapshot_id]
        return True
        
    async def clone_vm(self, source_vm_id: str,
                      new_name: str,
                      full_clone: bool = True) -> Optional[VirtualMachine]:
        """Клонирование ВМ"""
        source_vm = self.virtual_machines.get(source_vm_id)
        if not source_vm:
            return None
            
        # Create new VM
        new_vm = await self.create_vm(
            new_name,
            source_vm.hypervisor_id,
            source_vm.guest_os,
            source_vm.cpu_cores,
            source_vm.memory_gb
        )
        
        if not new_vm:
            return None
            
        # Clone disks
        for disk_id in source_vm.disk_ids:
            disk = self.virtual_disks.get(disk_id)
            if disk:
                await self.add_disk_to_vm(
                    new_vm.vm_id,
                    disk.size_gb,
                    disk.disk_type,
                    disk.datastore_id
                )
                
        # Clone NICs
        for nic_id in source_vm.nic_ids:
            nic = self.network_interfaces.get(nic_id)
            if nic:
                await self.add_nic_to_vm(
                    new_vm.vm_id,
                    nic.network_id,
                    nic.adapter_type
                )
                
        new_vm.notes = f"Cloned from {source_vm.name}"
        new_vm.tags = source_vm.tags.copy()
        
        return new_vm
        
    async def start_migration(self, vm_id: str,
                             dest_hypervisor_id: str,
                             mode: MigrationMode = MigrationMode.LIVE) -> Optional[MigrationTask]:
        """Запуск миграции ВМ"""
        vm = self.virtual_machines.get(vm_id)
        dest_hv = self.hypervisors.get(dest_hypervisor_id)
        
        if not vm or not dest_hv:
            return None
            
        # Check if live migration possible
        if mode == MigrationMode.LIVE and vm.state != VMState.RUNNING:
            mode = MigrationMode.COLD
            
        task = MigrationTask(
            task_id=f"mig_{uuid.uuid4().hex[:8]}",
            vm_id=vm_id,
            mode=mode,
            source_hypervisor_id=vm.hypervisor_id,
            dest_hypervisor_id=dest_hypervisor_id,
            status="in_progress",
            started_at=datetime.now()
        )
        
        vm.state = VMState.MIGRATING
        
        self.migration_tasks[task.task_id] = task
        return task
        
    async def complete_migration(self, task_id: str) -> bool:
        """Завершение миграции"""
        task = self.migration_tasks.get(task_id)
        if not task:
            return False
            
        vm = self.virtual_machines.get(task.vm_id)
        if not vm:
            return False
            
        # Update source hypervisor
        source_hv = self.hypervisors.get(task.source_hypervisor_id)
        if source_hv:
            source_hv.used_cpu_cores -= vm.cpu_cores
            source_hv.used_memory_gb -= vm.memory_gb
            source_hv.vm_count -= 1
            
        # Update destination hypervisor
        dest_hv = self.hypervisors.get(task.dest_hypervisor_id)
        if dest_hv:
            dest_hv.used_cpu_cores += vm.cpu_cores
            dest_hv.used_memory_gb += vm.memory_gb
            dest_hv.vm_count += 1
            
        # Update VM
        vm.hypervisor_id = task.dest_hypervisor_id
        vm.cluster_id = dest_hv.cluster_id if dest_hv else ""
        vm.state = VMState.RUNNING if task.mode == MigrationMode.LIVE else VMState.STOPPED
        
        # Update task
        task.status = "completed"
        task.progress_percent = 100
        task.completed_at = datetime.now()
        
        return True
        
    async def update_performance_stats(self):
        """Обновление статистики производительности"""
        for hv in self.hypervisors.values():
            if hv.is_online and not hv.is_maintenance:
                hv.cpu_percent = random.uniform(10, 80)
                hv.memory_percent = (hv.used_memory_gb / hv.total_memory_gb * 100) if hv.total_memory_gb > 0 else 0
                
        for vm in self.virtual_machines.values():
            if vm.state == VMState.RUNNING:
                vm.cpu_percent = random.uniform(5, 90)
                vm.memory_percent = random.uniform(30, 85)
                vm.disk_iops = random.randint(100, 10000)
                vm.network_mbps = random.uniform(10, 1000)
                
                # Update uptime
                if vm.started_at:
                    vm.uptime_seconds = int((datetime.now() - vm.started_at).total_seconds())
                    
        for disk in self.virtual_disks.values():
            disk.iops = random.randint(50, 5000)
            disk.throughput_mbps = random.uniform(10, 500)
            disk.used_gb = random.randint(1, disk.size_gb)
            
    def select_best_hypervisor(self, cpu_cores: int, memory_gb: int) -> Optional[str]:
        """Выбор лучшего гипервизора для ВМ (DRS)"""
        candidates = []
        
        for hv in self.hypervisors.values():
            if not hv.is_online or hv.is_maintenance:
                continue
                
            available_cpu = hv.total_cpu_cores - hv.used_cpu_cores
            available_mem = hv.total_memory_gb - hv.used_memory_gb
            
            if available_cpu >= cpu_cores and available_mem >= memory_gb:
                # Score based on available resources (lower utilization = better)
                cpu_util = hv.used_cpu_cores / hv.total_cpu_cores
                mem_util = hv.used_memory_gb / hv.total_memory_gb
                score = (cpu_util + mem_util) / 2
                candidates.append((hv.hypervisor_id, score))
                
        if not candidates:
            return None
            
        # Return hypervisor with lowest utilization
        candidates.sort(key=lambda x: x[1])
        return candidates[0][0]
        
    def get_cluster_statistics(self, cluster_id: str) -> Dict[str, Any]:
        """Статистика кластера"""
        cluster = self.clusters.get(cluster_id)
        if not cluster:
            return {}
            
        total_cpu_used = 0
        total_mem_used = 0
        online_hosts = 0
        
        for hv_id in cluster.hypervisor_ids:
            hv = self.hypervisors.get(hv_id)
            if hv:
                total_cpu_used += hv.used_cpu_cores
                total_mem_used += hv.used_memory_gb
                if hv.is_online:
                    online_hosts += 1
                    
        return {
            "cluster_id": cluster_id,
            "name": cluster.name,
            "total_hosts": len(cluster.hypervisor_ids),
            "online_hosts": online_hosts,
            "total_vms": cluster.vm_count,
            "total_cpu": cluster.total_cpu_cores,
            "used_cpu": total_cpu_used,
            "cpu_percent": (total_cpu_used / cluster.total_cpu_cores * 100) if cluster.total_cpu_cores > 0 else 0,
            "total_memory_gb": cluster.total_memory_gb,
            "used_memory_gb": total_mem_used,
            "memory_percent": (total_mem_used / cluster.total_memory_gb * 100) if cluster.total_memory_gb > 0 else 0,
            "ha_enabled": cluster.ha_enabled,
            "drs_enabled": cluster.drs_enabled
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_vms = len(self.virtual_machines)
        running_vms = sum(1 for vm in self.virtual_machines.values() if vm.state == VMState.RUNNING)
        
        total_vcpu = sum(vm.cpu_cores for vm in self.virtual_machines.values())
        total_vmem = sum(vm.memory_gb for vm in self.virtual_machines.values())
        
        total_disk_capacity = sum(d.size_gb for d in self.virtual_disks.values())
        total_disk_used = sum(d.used_gb for d in self.virtual_disks.values())
        
        total_snapshots = len(self.snapshots)
        total_snapshot_size = sum(s.size_gb for s in self.snapshots.values())
        
        total_hypervisors = len(self.hypervisors)
        online_hypervisors = sum(1 for h in self.hypervisors.values() if h.is_online)
        
        by_guest_os = {}
        for vm in self.virtual_machines.values():
            by_guest_os[vm.guest_os] = by_guest_os.get(vm.guest_os, 0) + 1
            
        return {
            "total_vms": total_vms,
            "running_vms": running_vms,
            "stopped_vms": total_vms - running_vms,
            "total_vcpu": total_vcpu,
            "total_vmem_gb": total_vmem,
            "total_disk_capacity_gb": total_disk_capacity,
            "total_disk_used_gb": total_disk_used,
            "total_snapshots": total_snapshots,
            "total_snapshot_size_gb": total_snapshot_size,
            "total_hypervisors": total_hypervisors,
            "online_hypervisors": online_hypervisors,
            "total_clusters": len(self.clusters),
            "total_networks": len(self.virtual_networks),
            "total_datastores": len(self.datastores),
            "total_templates": len(self.templates),
            "by_guest_os": by_guest_os
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 322: Virtualization Manager Platform")
    print("=" * 60)
    
    vm_mgr = VirtualizationManager()
    print("✓ Virtualization Manager created")
    
    # Add hypervisors
    print("\n🖥️ Adding Hypervisors...")
    
    hypervisors_data = [
        ("ESXi-Host-01", HypervisorType.VMWARE_ESXI, "esxi01.local", "10.0.0.101", 64, 512, 20000),
        ("ESXi-Host-02", HypervisorType.VMWARE_ESXI, "esxi02.local", "10.0.0.102", 64, 512, 20000),
        ("ESXi-Host-03", HypervisorType.VMWARE_ESXI, "esxi03.local", "10.0.0.103", 64, 512, 20000),
        ("KVM-Host-01", HypervisorType.KVM, "kvm01.local", "10.0.0.111", 32, 256, 10000),
        ("KVM-Host-02", HypervisorType.KVM, "kvm02.local", "10.0.0.112", 32, 256, 10000)
    ]
    
    hypervisors = []
    for name, h_type, hostname, ip, cpu, mem, storage in hypervisors_data:
        hv = await vm_mgr.add_hypervisor(name, h_type, hostname, ip, cpu, mem, storage)
        hypervisors.append(hv)
        print(f"  🖥️ {name} ({h_type.value})")
        
    # Create clusters
    print("\n🔗 Creating Clusters...")
    
    vsphere_cluster = await vm_mgr.create_cluster(
        "vSphere-Production",
        [h.hypervisor_id for h in hypervisors[:3]],
        ha_enabled=True,
        drs_enabled=True
    )
    print(f"  🔗 {vsphere_cluster.name} (3 hosts)")
    
    kvm_cluster = await vm_mgr.create_cluster(
        "KVM-Development",
        [h.hypervisor_id for h in hypervisors[3:]],
        ha_enabled=True,
        drs_enabled=False
    )
    print(f"  🔗 {kvm_cluster.name} (2 hosts)")
    
    # Create datastores
    print("\n💾 Creating Datastores...")
    
    datastores_data = [
        ("DS-SSD-01", "iscsi", 10000),
        ("DS-SSD-02", "iscsi", 10000),
        ("DS-NFS-01", "nfs", 50000),
        ("DS-VSAN-01", "vsan", 30000)
    ]
    
    datastores = []
    for name, ds_type, size in datastores_data:
        ds = await vm_mgr.create_datastore(name, ds_type, size)
        datastores.append(ds)
        print(f"  💾 {name} ({ds_type}) - {size} GB")
        
    # Create virtual networks
    print("\n🌐 Creating Virtual Networks...")
    
    networks_data = [
        ("VM Network", 100, "192.168.100.0/24", "192.168.100.1"),
        ("Management", 10, "10.0.10.0/24", "10.0.10.1"),
        ("Storage", 20, "10.0.20.0/24", "10.0.20.1"),
        ("vMotion", 30, "10.0.30.0/24", "10.0.30.1"),
        ("DMZ", 200, "172.16.0.0/24", "172.16.0.1")
    ]
    
    networks = []
    for name, vlan, network, gw in networks_data:
        vnet = await vm_mgr.create_virtual_network(name, vlan, network, gw)
        networks.append(vnet)
        print(f"  🌐 {name} (VLAN {vlan})")
        
    # Create templates
    print("\n📋 Creating VM Templates...")
    
    templates_data = [
        ("Ubuntu-22.04-Template", "Ubuntu 22.04 LTS", 2, 4, 50),
        ("CentOS-8-Template", "CentOS 8", 2, 4, 50),
        ("Windows-2022-Template", "Windows Server 2022", 4, 8, 100),
        ("Debian-12-Template", "Debian 12", 2, 2, 30)
    ]
    
    templates = []
    for name, os_name, cpu, mem, disk in templates_data:
        tmpl = await vm_mgr.create_template(name, os_name, cpu, mem, disk)
        templates.append(tmpl)
        print(f"  📋 {name}")
        
    # Create VMs
    print("\n💻 Creating Virtual Machines...")
    
    vms_data = [
        ("web-server-01", "Ubuntu 22.04 LTS", 4, 8),
        ("web-server-02", "Ubuntu 22.04 LTS", 4, 8),
        ("db-server-01", "CentOS 8", 8, 32),
        ("db-server-02", "CentOS 8", 8, 32),
        ("app-server-01", "Ubuntu 22.04 LTS", 4, 16),
        ("app-server-02", "Ubuntu 22.04 LTS", 4, 16),
        ("dc-01", "Windows Server 2022", 4, 8),
        ("monitoring-01", "Debian 12", 2, 4),
        ("jenkins-01", "Ubuntu 22.04 LTS", 4, 8),
        ("gitlab-01", "Ubuntu 22.04 LTS", 4, 16)
    ]
    
    vms = []
    for name, os_name, cpu, mem in vms_data:
        # Use DRS to select best hypervisor
        best_hv = vm_mgr.select_best_hypervisor(cpu, mem)
        if best_hv:
            vm = await vm_mgr.create_vm(name, best_hv, os_name, cpu, mem)
            if vm:
                vms.append(vm)
                
                # Add disk
                ds = random.choice(datastores)
                await vm_mgr.add_disk_to_vm(vm.vm_id, random.choice([50, 100, 200]), DiskType.THIN, ds.datastore_id)
                
                # Add network
                net = networks[0]  # VM Network
                await vm_mgr.add_nic_to_vm(vm.vm_id, net.network_id, NetworkAdapter.VMXNET3)
                
                print(f"  💻 {name} ({cpu} vCPU, {mem} GB RAM)")
                
    # Start some VMs
    print("\n▶️ Starting Virtual Machines...")
    
    for vm in vms[:7]:
        await vm_mgr.start_vm(vm.vm_id)
        print(f"  ▶️ {vm.name} started")
        
    # Create snapshots
    print("\n📸 Creating Snapshots...")
    
    for vm in vms[:3]:
        snap = await vm_mgr.create_snapshot(vm.vm_id, f"Pre-update snapshot for {vm.name}")
        if snap:
            print(f"  📸 Snapshot for {vm.name}")
            
    # Clone a VM
    print("\n📋 Cloning VM...")
    
    cloned_vm = await vm_mgr.clone_vm(vms[0].vm_id, "web-server-03-clone")
    if cloned_vm:
        print(f"  📋 Cloned {vms[0].name} -> {cloned_vm.name}")
        vms.append(cloned_vm)
        
    # Start migration
    print("\n🔄 Starting Live Migration...")
    
    target_hv = [h for h in hypervisors if h.hypervisor_id != vms[0].hypervisor_id][0]
    migration = await vm_mgr.start_migration(vms[0].vm_id, target_hv.hypervisor_id, MigrationMode.LIVE)
    if migration:
        print(f"  🔄 Migrating {vms[0].name} to {target_hv.name}")
        await vm_mgr.complete_migration(migration.task_id)
        print(f"  ✓ Migration completed")
        
    # Update stats
    await vm_mgr.update_performance_stats()
    
    # Hypervisor status
    print("\n🖥️ Hypervisor Status:")
    
    print("\n  ┌─────────────────────────┬───────────────────┬────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Host                    │ Type              │ CPU Usage                                                      │ Memory Usage               │")
    print("  ├─────────────────────────┼───────────────────┼────────────────────────────────────────────────────────────────┼────────────────────────────┤")
    
    for hv in hypervisors:
        name = hv.name[:23].ljust(23)
        h_type = hv.hypervisor_type.value[:17].ljust(17)
        
        cpu_pct = hv.used_cpu_cores / hv.total_cpu_cores * 100 if hv.total_cpu_cores > 0 else 0
        cpu_bar = "█" * int(cpu_pct / 2.5) + "░" * (40 - int(cpu_pct / 2.5))
        cpu = f"[{cpu_bar}] {cpu_pct:.0f}%"
        
        mem_pct = hv.used_memory_gb / hv.total_memory_gb * 100 if hv.total_memory_gb > 0 else 0
        mem = f"{hv.used_memory_gb}/{hv.total_memory_gb} GB ({mem_pct:.0f}%)"
        
        print(f"  │ {name} │ {h_type} │ {cpu} │ {mem:>26} │")
        
    print("  └─────────────────────────┴───────────────────┴────────────────────────────────────────────────────────────────┴────────────────────────────┘")
    
    # Cluster statistics
    print("\n🔗 Cluster Statistics:")
    
    for cluster in [vsphere_cluster, kvm_cluster]:
        stats = vm_mgr.get_cluster_statistics(cluster.cluster_id)
        
        print(f"\n  🔗 {stats['name']}")
        print(f"     Hosts: {stats['online_hosts']}/{stats['total_hosts']} online")
        print(f"     VMs: {stats['total_vms']}")
        print(f"     CPU: {stats['used_cpu']}/{stats['total_cpu']} cores ({stats['cpu_percent']:.1f}%)")
        print(f"     Memory: {stats['used_memory_gb']}/{stats['total_memory_gb']} GB ({stats['memory_percent']:.1f}%)")
        print(f"     HA: {'✓' if stats['ha_enabled'] else '✗'} | DRS: {'✓' if stats['drs_enabled'] else '✗'}")
        
    # VM status
    print("\n💻 Virtual Machine Status:")
    
    print("\n  ┌─────────────────────────┬───────────────────────────┬──────────────┬────────────┬────────────┬────────────────────────────────────────────────────────┐")
    print("  │ VM                      │ Guest OS                  │ vCPU/RAM     │ State      │ IP         │ Performance                                            │")
    print("  ├─────────────────────────┼───────────────────────────┼──────────────┼────────────┼────────────┼────────────────────────────────────────────────────────┤")
    
    for vm in vms:
        name = vm.name[:23].ljust(23)
        os_name = vm.guest_os[:25].ljust(25)
        resources = f"{vm.cpu_cores}C/{vm.memory_gb}G"[:12].ljust(12)
        state = vm.state.value[:10].ljust(10)
        ip = vm.primary_ip[:10].ljust(10)
        
        if vm.state == VMState.RUNNING:
            perf_bar = "█" * int(vm.cpu_percent / 2.5) + "░" * (40 - int(vm.cpu_percent / 2.5))
            perf = f"[{perf_bar}] CPU {vm.cpu_percent:.0f}%"
        else:
            perf = "-".ljust(54)
            
        print(f"  │ {name} │ {os_name} │ {resources} │ {state} │ {ip} │ {perf} │")
        
    print("  └─────────────────────────┴───────────────────────────┴──────────────┴────────────┴────────────┴────────────────────────────────────────────────────────┘")
    
    # Datastore utilization
    print("\n💾 Datastore Utilization:")
    
    for ds in datastores:
        used_pct = ds.used_gb / ds.total_gb * 100 if ds.total_gb > 0 else 0
        bar = "█" * int(used_pct / 2.5) + "░" * (40 - int(used_pct / 2.5))
        
        print(f"\n  💾 {ds.name} ({ds.datastore_type})")
        print(f"     [{bar}] {used_pct:.1f}%")
        print(f"     {ds.used_gb} / {ds.total_gb} GB used ({ds.free_gb} GB free)")
        
    # Snapshots
    print("\n📸 Snapshots:")
    
    for snap in vm_mgr.snapshots.values():
        vm = vm_mgr.virtual_machines.get(snap.vm_id)
        vm_name = vm.name if vm else "Unknown"
        
        print(f"\n  📸 {snap.name}")
        print(f"     VM: {vm_name}")
        print(f"     Size: {snap.size_gb:.2f} GB")
        print(f"     Memory: {'✓' if snap.memory_included else '✗'}")
        print(f"     Created: {snap.created_at.strftime('%Y-%m-%d %H:%M')}")
        
    # Statistics
    print("\n📊 Overall Statistics:")
    
    stats = vm_mgr.get_statistics()
    
    print(f"\n  Virtual Machines: {stats['running_vms']}/{stats['total_vms']} running")
    print(f"  Total vCPU: {stats['total_vcpu']}")
    print(f"  Total Memory: {stats['total_vmem_gb']} GB")
    print(f"  Total Disk: {stats['total_disk_capacity_gb']} GB ({stats['total_disk_used_gb']} GB used)")
    print(f"  Snapshots: {stats['total_snapshots']} ({stats['total_snapshot_size_gb']:.2f} GB)")
    print(f"  Hypervisors: {stats['online_hypervisors']}/{stats['total_hypervisors']} online")
    print(f"  Clusters: {stats['total_clusters']}")
    print(f"  Networks: {stats['total_networks']}")
    print(f"  Datastores: {stats['total_datastores']}")
    print(f"  Templates: {stats['total_templates']}")
    
    print("\n  By Guest OS:")
    for os_name, count in stats['by_guest_os'].items():
        print(f"    {os_name}: {count} VMs")
        
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Virtualization Manager Platform                   │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total VMs:                   {stats['total_vms']:>12}                          │")
    print(f"│ Running VMs:                 {stats['running_vms']:>12}                          │")
    print(f"│ Total vCPU Allocated:        {stats['total_vcpu']:>12}                          │")
    print(f"│ Total Memory Allocated:      {stats['total_vmem_gb']:>9} GB                          │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Hypervisors Online:          {stats['online_hypervisors']:>12}                          │")
    print(f"│ Clusters:                    {stats['total_clusters']:>12}                          │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Virtualization Manager Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
