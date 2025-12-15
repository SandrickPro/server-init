#!/usr/bin/env python3
"""
Server Init - Iteration 320: Storage Manager Platform
Платформа управления хранилищами данных

Функционал:
- Volume Management - управление томами
- Storage Pools - пулы хранения
- Quotas - квоты
- Snapshots - снимки
- Replication - репликация
- Tiering - тиринг данных
- Deduplication - дедупликация
- Performance Monitoring - мониторинг производительности
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class StorageType(Enum):
    """Тип хранилища"""
    BLOCK = "block"
    FILE = "file"
    OBJECT = "object"


class StorageTier(Enum):
    """Уровень хранилища"""
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"
    ARCHIVE = "archive"


class VolumeStatus(Enum):
    """Статус тома"""
    CREATING = "creating"
    AVAILABLE = "available"
    IN_USE = "in_use"
    DELETING = "deleting"
    ERROR = "error"


class PoolStatus(Enum):
    """Статус пула"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    REBUILDING = "rebuilding"
    OFFLINE = "offline"


class RAIDLevel(Enum):
    """Уровень RAID"""
    RAID0 = "raid0"
    RAID1 = "raid1"
    RAID5 = "raid5"
    RAID6 = "raid6"
    RAID10 = "raid10"


class ReplicationMode(Enum):
    """Режим репликации"""
    SYNC = "synchronous"
    ASYNC = "asynchronous"
    MIRROR = "mirror"


@dataclass
class Disk:
    """Физический диск"""
    disk_id: str
    
    # Model
    model: str = ""
    serial: str = ""
    
    # Capacity
    capacity_gb: int = 0
    
    # Type
    disk_type: str = "SSD"  # SSD, HDD, NVMe
    
    # Status
    is_healthy: bool = True
    is_allocated: bool = False
    
    # SMART stats
    power_on_hours: int = 0
    temperature_c: int = 35
    reallocated_sectors: int = 0
    
    # Performance
    read_iops: int = 0
    write_iops: int = 0
    read_throughput_mbps: float = 0
    write_throughput_mbps: float = 0


@dataclass
class StoragePool:
    """Пул хранения"""
    pool_id: str
    name: str
    
    # Disks
    disk_ids: List[str] = field(default_factory=list)
    
    # RAID
    raid_level: RAIDLevel = RAIDLevel.RAID5
    
    # Capacity
    total_capacity_gb: int = 0
    used_capacity_gb: int = 0
    reserved_capacity_gb: int = 0
    
    # Tier
    tier: StorageTier = StorageTier.HOT
    
    # Status
    status: PoolStatus = PoolStatus.HEALTHY
    
    # Features
    dedup_enabled: bool = False
    compression_enabled: bool = True
    
    # Dedup stats
    dedup_ratio: float = 1.0
    compression_ratio: float = 1.0
    
    # Performance
    iops_limit: int = 0
    throughput_limit_mbps: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Volume:
    """Том"""
    volume_id: str
    name: str
    
    # Pool
    pool_id: str = ""
    
    # Type
    storage_type: StorageType = StorageType.BLOCK
    
    # Size
    size_gb: int = 0
    used_gb: int = 0
    
    # Tier
    tier: StorageTier = StorageTier.HOT
    
    # Status
    status: VolumeStatus = VolumeStatus.AVAILABLE
    
    # Attachment
    attached_to: str = ""  # host/vm id
    mount_point: str = ""
    
    # Thin provisioning
    thin_provisioned: bool = True
    
    # IOPS/Throughput limits
    iops_limit: int = 0
    throughput_limit_mbps: int = 0
    
    # Encryption
    encrypted: bool = False
    encryption_key_id: str = ""
    
    # Snapshots
    snapshot_ids: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    
    # Stats
    read_iops: int = 0
    write_iops: int = 0
    read_throughput_mbps: float = 0
    write_throughput_mbps: float = 0
    latency_ms: float = 0


@dataclass
class Snapshot:
    """Снимок тома"""
    snapshot_id: str
    volume_id: str
    
    # Name
    name: str = ""
    description: str = ""
    
    # Size
    size_gb: int = 0
    
    # Status
    is_consistent: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


@dataclass
class Quota:
    """Квота"""
    quota_id: str
    
    # Target
    target_type: str = "user"  # user, group, project
    target_id: str = ""
    
    # Pool
    pool_id: str = ""
    
    # Limits
    capacity_limit_gb: int = 0
    used_capacity_gb: int = 0
    
    iops_limit: int = 0
    throughput_limit_mbps: int = 0
    
    # Status
    is_enforced: bool = True
    
    # Alerts
    warning_threshold_percent: int = 80
    critical_threshold_percent: int = 95


@dataclass
class ReplicationRule:
    """Правило репликации"""
    rule_id: str
    name: str
    
    # Source/Target
    source_volume_id: str = ""
    target_volume_id: str = ""
    target_pool_id: str = ""
    
    # Mode
    mode: ReplicationMode = ReplicationMode.ASYNC
    
    # Schedule
    schedule: str = "*/15 * * * *"  # every 15 minutes
    
    # Status
    is_enabled: bool = True
    last_sync: Optional[datetime] = None
    
    # Lag
    lag_seconds: int = 0
    
    # Stats
    bytes_replicated: int = 0


@dataclass
class TieringRule:
    """Правило тиринга"""
    rule_id: str
    name: str
    
    # Source
    source_pool_id: str = ""
    
    # Target
    target_tier: StorageTier = StorageTier.COLD
    target_pool_id: str = ""
    
    # Criteria
    days_not_accessed: int = 30
    min_size_mb: int = 100
    
    # Status
    is_enabled: bool = True
    
    # Stats
    bytes_tiered: int = 0
    files_tiered: int = 0


class StorageManager:
    """Менеджер хранилищ"""
    
    def __init__(self):
        self.disks: Dict[str, Disk] = {}
        self.pools: Dict[str, StoragePool] = {}
        self.volumes: Dict[str, Volume] = {}
        self.snapshots: Dict[str, Snapshot] = {}
        self.quotas: Dict[str, Quota] = {}
        self.replication_rules: Dict[str, ReplicationRule] = {}
        self.tiering_rules: Dict[str, TieringRule] = {}
        
    async def add_disk(self, model: str,
                      capacity_gb: int,
                      disk_type: str = "SSD") -> Disk:
        """Добавление диска"""
        disk = Disk(
            disk_id=f"disk_{uuid.uuid4().hex[:8]}",
            model=model,
            serial=uuid.uuid4().hex[:12].upper(),
            capacity_gb=capacity_gb,
            disk_type=disk_type,
            power_on_hours=random.randint(0, 50000)
        )
        
        self.disks[disk.disk_id] = disk
        return disk
        
    async def create_pool(self, name: str,
                         disk_ids: List[str],
                         raid_level: RAIDLevel = RAIDLevel.RAID5,
                         tier: StorageTier = StorageTier.HOT,
                         dedup: bool = False,
                         compression: bool = True) -> StoragePool:
        """Создание пула"""
        total_capacity = 0
        
        for disk_id in disk_ids:
            disk = self.disks.get(disk_id)
            if disk:
                total_capacity += disk.capacity_gb
                disk.is_allocated = True
                
        # Apply RAID overhead
        raid_overhead = {
            RAIDLevel.RAID0: 1.0,
            RAIDLevel.RAID1: 0.5,
            RAIDLevel.RAID5: (len(disk_ids) - 1) / len(disk_ids) if disk_ids else 0.7,
            RAIDLevel.RAID6: (len(disk_ids) - 2) / len(disk_ids) if len(disk_ids) > 2 else 0.6,
            RAIDLevel.RAID10: 0.5
        }
        
        usable_capacity = int(total_capacity * raid_overhead.get(raid_level, 0.8))
        
        pool = StoragePool(
            pool_id=f"pool_{uuid.uuid4().hex[:8]}",
            name=name,
            disk_ids=disk_ids,
            raid_level=raid_level,
            total_capacity_gb=usable_capacity,
            tier=tier,
            dedup_enabled=dedup,
            compression_enabled=compression
        )
        
        self.pools[pool.pool_id] = pool
        return pool
        
    async def create_volume(self, name: str,
                           pool_id: str,
                           size_gb: int,
                           storage_type: StorageType = StorageType.BLOCK,
                           thin: bool = True,
                           encrypted: bool = False,
                           iops_limit: int = 0,
                           throughput_limit: int = 0) -> Optional[Volume]:
        """Создание тома"""
        pool = self.pools.get(pool_id)
        if not pool:
            return None
            
        # Check capacity
        available = pool.total_capacity_gb - pool.used_capacity_gb - pool.reserved_capacity_gb
        if not thin and size_gb > available:
            return None
            
        volume = Volume(
            volume_id=f"vol_{uuid.uuid4().hex[:8]}",
            name=name,
            pool_id=pool_id,
            storage_type=storage_type,
            size_gb=size_gb,
            tier=pool.tier,
            thin_provisioned=thin,
            encrypted=encrypted,
            encryption_key_id=f"key_{uuid.uuid4().hex[:8]}" if encrypted else "",
            iops_limit=iops_limit,
            throughput_limit_mbps=throughput_limit
        )
        
        self.volumes[volume.volume_id] = volume
        
        # Update pool usage
        if not thin:
            pool.used_capacity_gb += size_gb
        else:
            pool.reserved_capacity_gb += size_gb
            
        return volume
        
    async def attach_volume(self, volume_id: str,
                           host_id: str,
                           mount_point: str = "") -> bool:
        """Подключение тома"""
        volume = self.volumes.get(volume_id)
        if not volume or volume.status != VolumeStatus.AVAILABLE:
            return False
            
        volume.attached_to = host_id
        volume.mount_point = mount_point
        volume.status = VolumeStatus.IN_USE
        
        return True
        
    async def detach_volume(self, volume_id: str) -> bool:
        """Отключение тома"""
        volume = self.volumes.get(volume_id)
        if not volume:
            return False
            
        volume.attached_to = ""
        volume.mount_point = ""
        volume.status = VolumeStatus.AVAILABLE
        
        return True
        
    async def create_snapshot(self, volume_id: str,
                             name: str = "",
                             description: str = "",
                             retention_days: int = 0) -> Optional[Snapshot]:
        """Создание снимка"""
        volume = self.volumes.get(volume_id)
        if not volume:
            return None
            
        snapshot = Snapshot(
            snapshot_id=f"snap_{uuid.uuid4().hex[:8]}",
            volume_id=volume_id,
            name=name or f"snap-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            description=description,
            size_gb=volume.used_gb or int(volume.size_gb * 0.1)  # Estimate
        )
        
        if retention_days > 0:
            snapshot.expires_at = datetime.now() + timedelta(days=retention_days)
            
        self.snapshots[snapshot.snapshot_id] = snapshot
        volume.snapshot_ids.append(snapshot.snapshot_id)
        
        return snapshot
        
    async def delete_snapshot(self, snapshot_id: str) -> bool:
        """Удаление снимка"""
        snapshot = self.snapshots.get(snapshot_id)
        if not snapshot:
            return False
            
        volume = self.volumes.get(snapshot.volume_id)
        if volume and snapshot_id in volume.snapshot_ids:
            volume.snapshot_ids.remove(snapshot_id)
            
        del self.snapshots[snapshot_id]
        return True
        
    async def restore_from_snapshot(self, snapshot_id: str,
                                   new_volume_name: str = "") -> Optional[Volume]:
        """Восстановление из снимка"""
        snapshot = self.snapshots.get(snapshot_id)
        if not snapshot:
            return None
            
        source_volume = self.volumes.get(snapshot.volume_id)
        if not source_volume:
            return None
            
        # Create new volume from snapshot
        new_volume = await self.create_volume(
            name=new_volume_name or f"restore-{snapshot.name}",
            pool_id=source_volume.pool_id,
            size_gb=source_volume.size_gb,
            storage_type=source_volume.storage_type,
            encrypted=source_volume.encrypted
        )
        
        if new_volume:
            new_volume.used_gb = snapshot.size_gb
            
        return new_volume
        
    async def create_quota(self, target_type: str,
                          target_id: str,
                          pool_id: str,
                          capacity_limit_gb: int,
                          iops_limit: int = 0,
                          throughput_limit: int = 0) -> Quota:
        """Создание квоты"""
        quota = Quota(
            quota_id=f"quota_{uuid.uuid4().hex[:8]}",
            target_type=target_type,
            target_id=target_id,
            pool_id=pool_id,
            capacity_limit_gb=capacity_limit_gb,
            iops_limit=iops_limit,
            throughput_limit_mbps=throughput_limit
        )
        
        self.quotas[quota.quota_id] = quota
        return quota
        
    async def create_replication_rule(self, name: str,
                                     source_volume_id: str,
                                     target_pool_id: str,
                                     mode: ReplicationMode = ReplicationMode.ASYNC,
                                     schedule: str = "*/15 * * * *") -> Optional[ReplicationRule]:
        """Создание правила репликации"""
        source_volume = self.volumes.get(source_volume_id)
        if not source_volume:
            return None
            
        # Create target volume
        target_volume = await self.create_volume(
            name=f"{source_volume.name}-replica",
            pool_id=target_pool_id,
            size_gb=source_volume.size_gb,
            storage_type=source_volume.storage_type
        )
        
        if not target_volume:
            return None
            
        rule = ReplicationRule(
            rule_id=f"repl_{uuid.uuid4().hex[:8]}",
            name=name,
            source_volume_id=source_volume_id,
            target_volume_id=target_volume.volume_id,
            target_pool_id=target_pool_id,
            mode=mode,
            schedule=schedule
        )
        
        self.replication_rules[rule.rule_id] = rule
        return rule
        
    async def create_tiering_rule(self, name: str,
                                 source_pool_id: str,
                                 target_pool_id: str,
                                 target_tier: StorageTier,
                                 days_not_accessed: int = 30) -> TieringRule:
        """Создание правила тиринга"""
        rule = TieringRule(
            rule_id=f"tier_{uuid.uuid4().hex[:8]}",
            name=name,
            source_pool_id=source_pool_id,
            target_pool_id=target_pool_id,
            target_tier=target_tier,
            days_not_accessed=days_not_accessed
        )
        
        self.tiering_rules[rule.rule_id] = rule
        return rule
        
    async def run_replication(self):
        """Запуск репликации"""
        for rule in self.replication_rules.values():
            if not rule.is_enabled:
                continue
                
            # Simulate replication
            source_vol = self.volumes.get(rule.source_volume_id)
            if source_vol:
                bytes_to_replicate = random.randint(1000000, 100000000)
                rule.bytes_replicated += bytes_to_replicate
                rule.last_sync = datetime.now()
                
                if rule.mode == ReplicationMode.SYNC:
                    rule.lag_seconds = random.randint(0, 5)
                else:
                    rule.lag_seconds = random.randint(0, 300)
                    
    async def run_tiering(self):
        """Запуск тиринга"""
        for rule in self.tiering_rules.values():
            if not rule.is_enabled:
                continue
                
            # Simulate tiering
            bytes_tiered = random.randint(100000000, 1000000000)
            files_tiered = random.randint(100, 1000)
            
            rule.bytes_tiered += bytes_tiered
            rule.files_tiered += files_tiered
            
    async def update_performance_stats(self):
        """Обновление статистики производительности"""
        for volume in self.volumes.values():
            if volume.status == VolumeStatus.IN_USE:
                volume.read_iops = random.randint(100, 10000)
                volume.write_iops = random.randint(50, 5000)
                volume.read_throughput_mbps = random.uniform(50, 500)
                volume.write_throughput_mbps = random.uniform(25, 250)
                volume.latency_ms = random.uniform(0.5, 10)
                
                # Update used space
                growth = random.uniform(0, 0.01)  # 0-1% growth
                volume.used_gb = min(volume.size_gb, int(volume.used_gb + volume.size_gb * growth))
                
        for disk in self.disks.values():
            if disk.is_allocated:
                disk.read_iops = random.randint(1000, 100000)
                disk.write_iops = random.randint(500, 50000)
                disk.read_throughput_mbps = random.uniform(100, 1000)
                disk.write_throughput_mbps = random.uniform(50, 500)
                disk.temperature_c = random.randint(30, 50)
                
        for pool in self.pools.values():
            # Update dedup ratio
            if pool.dedup_enabled:
                pool.dedup_ratio = random.uniform(1.2, 3.0)
            if pool.compression_enabled:
                pool.compression_ratio = random.uniform(1.1, 2.5)
                
    def get_pool_utilization(self) -> Dict[str, Any]:
        """Утилизация пулов"""
        utilization = {}
        
        for pool in self.pools.values():
            used = pool.used_capacity_gb
            reserved = pool.reserved_capacity_gb
            total = pool.total_capacity_gb
            
            # Count actual usage from volumes
            actual_used = sum(
                v.used_gb for v in self.volumes.values()
                if v.pool_id == pool.pool_id
            )
            
            free = total - used - reserved
            used_pct = (used + reserved) / total * 100 if total > 0 else 0
            
            utilization[pool.pool_id] = {
                "name": pool.name,
                "tier": pool.tier.value,
                "total_gb": total,
                "used_gb": used,
                "reserved_gb": reserved,
                "actual_used_gb": actual_used,
                "free_gb": free,
                "used_percent": used_pct,
                "status": pool.status.value,
                "dedup_ratio": pool.dedup_ratio,
                "compression_ratio": pool.compression_ratio
            }
            
        return utilization
        
    def get_quota_status(self) -> List[Dict[str, Any]]:
        """Статус квот"""
        status = []
        
        for quota in self.quotas.values():
            # Calculate actual usage
            actual_used = sum(
                v.used_gb for v in self.volumes.values()
                if v.pool_id == quota.pool_id  # Simplified check
            )
            
            quota.used_capacity_gb = actual_used
            
            used_pct = (actual_used / quota.capacity_limit_gb * 100) if quota.capacity_limit_gb > 0 else 0
            
            alert = "ok"
            if used_pct >= quota.critical_threshold_percent:
                alert = "critical"
            elif used_pct >= quota.warning_threshold_percent:
                alert = "warning"
                
            status.append({
                "quota_id": quota.quota_id,
                "target_type": quota.target_type,
                "target_id": quota.target_id,
                "limit_gb": quota.capacity_limit_gb,
                "used_gb": actual_used,
                "used_percent": used_pct,
                "alert": alert
            })
            
        return status
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_disks = len(self.disks)
        healthy_disks = sum(1 for d in self.disks.values() if d.is_healthy)
        
        total_disk_capacity = sum(d.capacity_gb for d in self.disks.values())
        
        by_disk_type = {}
        for d in self.disks.values():
            by_disk_type[d.disk_type] = by_disk_type.get(d.disk_type, 0) + 1
            
        total_pools = len(self.pools)
        healthy_pools = sum(1 for p in self.pools.values() if p.status == PoolStatus.HEALTHY)
        
        pool_capacity = sum(p.total_capacity_gb for p in self.pools.values())
        pool_used = sum(p.used_capacity_gb + p.reserved_capacity_gb for p in self.pools.values())
        
        by_tier = {}
        for p in self.pools.values():
            by_tier[p.tier.value] = by_tier.get(p.tier.value, 0) + p.total_capacity_gb
            
        total_volumes = len(self.volumes)
        
        by_volume_status = {}
        for v in self.volumes.values():
            by_volume_status[v.status.value] = by_volume_status.get(v.status.value, 0) + 1
            
        total_snapshots = len(self.snapshots)
        snapshot_size = sum(s.size_gb for s in self.snapshots.values())
        
        return {
            "total_disks": total_disks,
            "healthy_disks": healthy_disks,
            "total_disk_capacity_gb": total_disk_capacity,
            "by_disk_type": by_disk_type,
            "total_pools": total_pools,
            "healthy_pools": healthy_pools,
            "pool_capacity_gb": pool_capacity,
            "pool_used_gb": pool_used,
            "by_tier_gb": by_tier,
            "total_volumes": total_volumes,
            "by_volume_status": by_volume_status,
            "total_snapshots": total_snapshots,
            "snapshot_size_gb": snapshot_size,
            "total_quotas": len(self.quotas),
            "replication_rules": len(self.replication_rules),
            "tiering_rules": len(self.tiering_rules)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 320: Storage Manager Platform")
    print("=" * 60)
    
    storage = StorageManager()
    print("✓ Storage Manager created")
    
    # Add disks
    print("\n💿 Adding Disks...")
    
    disks_data = [
        ("Samsung 980 PRO", 1000, "NVMe"),
        ("Samsung 980 PRO", 1000, "NVMe"),
        ("Samsung 870 EVO", 2000, "SSD"),
        ("Samsung 870 EVO", 2000, "SSD"),
        ("Samsung 870 EVO", 2000, "SSD"),
        ("Samsung 870 EVO", 2000, "SSD"),
        ("Seagate IronWolf", 8000, "HDD"),
        ("Seagate IronWolf", 8000, "HDD"),
        ("Seagate IronWolf", 8000, "HDD"),
        ("Seagate IronWolf", 8000, "HDD")
    ]
    
    disks = []
    for model, capacity, d_type in disks_data:
        disk = await storage.add_disk(model, capacity, d_type)
        disks.append(disk)
        
    print(f"  ✓ Added {len(disks)} disks")
    
    by_type = {}
    for d in disks:
        by_type[d.disk_type] = by_type.get(d.disk_type, 0) + 1
    for d_type, count in by_type.items():
        print(f"    {d_type}: {count} disks")
        
    # Create storage pools
    print("\n📦 Creating Storage Pools...")
    
    pools_data = [
        ("Fast Pool", [d.disk_id for d in disks[:2]], RAIDLevel.RAID1, StorageTier.HOT, True, True),
        ("Standard Pool", [d.disk_id for d in disks[2:6]], RAIDLevel.RAID5, StorageTier.WARM, True, True),
        ("Archive Pool", [d.disk_id for d in disks[6:]], RAIDLevel.RAID6, StorageTier.COLD, True, True)
    ]
    
    pools = []
    for name, disk_ids, raid, tier, dedup, compress in pools_data:
        pool = await storage.create_pool(name, disk_ids, raid, tier, dedup, compress)
        pools.append(pool)
        print(f"  📦 {name} ({raid.value}, {tier.value}) - {pool.total_capacity_gb} GB")
        
    # Create volumes
    print("\n💾 Creating Volumes...")
    
    volumes_data = [
        ("db-data", pools[0].pool_id, 200, StorageType.BLOCK, True, True, 10000, 500),
        ("db-logs", pools[0].pool_id, 100, StorageType.BLOCK, False, True, 5000, 200),
        ("app-data", pools[1].pool_id, 500, StorageType.BLOCK, True, False, 3000, 300),
        ("user-home", pools[1].pool_id, 1000, StorageType.FILE, True, False, 1000, 100),
        ("media-files", pools[1].pool_id, 2000, StorageType.FILE, True, False, 500, 200),
        ("backups", pools[2].pool_id, 5000, StorageType.FILE, True, False, 100, 500),
        ("archive", pools[2].pool_id, 10000, StorageType.OBJECT, True, False, 50, 200)
    ]
    
    volumes = []
    for name, pool_id, size, s_type, thin, encrypted, iops, throughput in volumes_data:
        volume = await storage.create_volume(name, pool_id, size, s_type, thin, encrypted, iops, throughput)
        if volume:
            volumes.append(volume)
            volume.used_gb = int(size * random.uniform(0.1, 0.6))  # Simulate usage
            enc_str = "🔐" if encrypted else ""
            print(f"  💾 {name} {enc_str} ({size} GB, {s_type.value})")
            
    # Attach volumes
    print("\n🔗 Attaching Volumes...")
    
    attachments = [
        (volumes[0], "db-server-01", "/dev/sdb"),
        (volumes[1], "db-server-01", "/dev/sdc"),
        (volumes[2], "app-server-01", "/dev/sdb"),
        (volumes[3], "file-server-01", "/data/homes")
    ]
    
    for volume, host, mount in attachments:
        await storage.attach_volume(volume.volume_id, host, mount)
        print(f"  🔗 {volume.name} -> {host}:{mount}")
        
    # Create snapshots
    print("\n📸 Creating Snapshots...")
    
    snapshots = []
    for volume in volumes[:4]:
        for i in range(2):
            snap = await storage.create_snapshot(
                volume.volume_id,
                f"{volume.name}-snap-{i+1}",
                f"Daily snapshot {i+1}",
                retention_days=30
            )
            if snap:
                snapshots.append(snap)
                
    print(f"  ✓ Created {len(snapshots)} snapshots")
    
    # Create quotas
    print("\n📊 Creating Quotas...")
    
    quotas_data = [
        ("user", "user-001", pools[1].pool_id, 100),
        ("user", "user-002", pools[1].pool_id, 100),
        ("user", "user-003", pools[1].pool_id, 200),
        ("group", "developers", pools[1].pool_id, 1000),
        ("project", "project-alpha", pools[0].pool_id, 500)
    ]
    
    quotas = []
    for target_type, target_id, pool_id, limit in quotas_data:
        quota = await storage.create_quota(target_type, target_id, pool_id, limit)
        quotas.append(quota)
        print(f"  📊 {target_type}/{target_id}: {limit} GB")
        
    # Create replication rules
    print("\n🔄 Creating Replication Rules...")
    
    repl_rule = await storage.create_replication_rule(
        "DB Replication",
        volumes[0].volume_id,
        pools[2].pool_id,
        ReplicationMode.ASYNC,
        "*/5 * * * *"
    )
    
    if repl_rule:
        print(f"  🔄 {repl_rule.name} ({repl_rule.mode.value})")
        
    # Create tiering rules
    print("\n📊 Creating Tiering Rules...")
    
    tier_rule = await storage.create_tiering_rule(
        "Archive Old Data",
        pools[1].pool_id,
        pools[2].pool_id,
        StorageTier.COLD,
        60
    )
    
    print(f"  📊 {tier_rule.name} (after {tier_rule.days_not_accessed} days)")
    
    # Run operations
    await storage.run_replication()
    await storage.run_tiering()
    await storage.update_performance_stats()
    
    # Disk status
    print("\n💿 Disk Status:")
    
    print("\n  ┌────────────────────────┬─────────┬───────────────┬────────────┬────────────────┬───────────┐")
    print("  │ Model                  │ Type    │ Capacity      │ Status     │ Read IOPS      │ Temp °C   │")
    print("  ├────────────────────────┼─────────┼───────────────┼────────────┼────────────────┼───────────┤")
    
    for disk in disks[:6]:
        model = disk.model[:22].ljust(22)
        d_type = disk.disk_type[:7].ljust(7)
        capacity = f"{disk.capacity_gb} GB"[:13].ljust(13)
        status = ("✓ Healthy" if disk.is_healthy else "✗ Failed")[:10].ljust(10)
        iops = str(disk.read_iops).ljust(14)
        temp = str(disk.temperature_c).ljust(9)
        
        print(f"  │ {model} │ {d_type} │ {capacity} │ {status} │ {iops} │ {temp} │")
        
    print("  └────────────────────────┴─────────┴───────────────┴────────────┴────────────────┴───────────┘")
    
    # Pool status
    print("\n📦 Pool Status:")
    
    utilization = storage.get_pool_utilization()
    
    print("\n  ┌─────────────────────┬─────────┬───────────┬────────────────────────────────────────────────────┐")
    print("  │ Pool                │ Tier    │ RAID      │ Utilization                                        │")
    print("  ├─────────────────────┼─────────┼───────────┼────────────────────────────────────────────────────┤")
    
    for pool_id, info in utilization.items():
        pool = storage.pools[pool_id]
        name = info['name'][:19].ljust(19)
        tier = info['tier'][:7].ljust(7)
        raid = pool.raid_level.value[:9].ljust(9)
        
        used_pct = info['used_percent']
        bar = "█" * int(used_pct / 2.5) + "░" * (40 - int(used_pct / 2.5))
        util_str = f"[{bar}] {used_pct:.1f}%"
        
        print(f"  │ {name} │ {tier} │ {raid} │ {util_str} │")
        
    print("  └─────────────────────┴─────────┴───────────┴────────────────────────────────────────────────────┘")
    
    # Pool details
    for pool_id, info in utilization.items():
        print(f"\n  📦 {info['name']}")
        print(f"     Total: {info['total_gb']} GB")
        print(f"     Used: {info['used_gb']} GB")
        print(f"     Reserved: {info['reserved_gb']} GB")
        print(f"     Free: {info['free_gb']} GB")
        if info['dedup_ratio'] > 1:
            print(f"     Dedup Ratio: {info['dedup_ratio']:.2f}x")
        if info['compression_ratio'] > 1:
            print(f"     Compression: {info['compression_ratio']:.2f}x")
            
    # Volume status
    print("\n💾 Volume Status:")
    
    print("\n  ┌───────────────────┬─────────────┬──────────────┬────────────────────────┬─────────┬─────────────┐")
    print("  │ Volume            │ Type        │ Size/Used    │ Host                   │ Status  │ Latency     │")
    print("  ├───────────────────┼─────────────┼──────────────┼────────────────────────┼─────────┼─────────────┤")
    
    for volume in volumes:
        name = volume.name[:17].ljust(17)
        v_type = volume.storage_type.value[:11].ljust(11)
        size = f"{volume.size_gb}/{volume.used_gb}GB"[:12].ljust(12)
        host = (volume.attached_to or "-")[:22].ljust(22)
        status = volume.status.value[:7].ljust(7)
        latency = f"{volume.latency_ms:.1f}ms"[:11].ljust(11)
        
        print(f"  │ {name} │ {v_type} │ {size} │ {host} │ {status} │ {latency} │")
        
    print("  └───────────────────┴─────────────┴──────────────┴────────────────────────┴─────────┴─────────────┘")
    
    # Volume performance
    print("\n⚡ Volume Performance:")
    
    for volume in volumes[:4]:
        if volume.status == VolumeStatus.IN_USE:
            print(f"\n  💾 {volume.name}")
            print(f"     Read: {volume.read_iops} IOPS, {volume.read_throughput_mbps:.1f} MB/s")
            print(f"     Write: {volume.write_iops} IOPS, {volume.write_throughput_mbps:.1f} MB/s")
            print(f"     Latency: {volume.latency_ms:.2f} ms")
            
    # Snapshots
    print("\n📸 Snapshots:")
    
    print("\n  ┌───────────────────────┬──────────────────────────┬─────────────┬─────────────────────────┐")
    print("  │ Volume                │ Snapshot                 │ Size        │ Expires                 │")
    print("  ├───────────────────────┼──────────────────────────┼─────────────┼─────────────────────────┤")
    
    for snap in snapshots[:6]:
        volume = storage.volumes.get(snap.volume_id)
        vol_name = (volume.name if volume else "Unknown")[:21].ljust(21)
        snap_name = snap.name[:24].ljust(24)
        size = f"{snap.size_gb} GB"[:11].ljust(11)
        expires = snap.expires_at.strftime("%Y-%m-%d") if snap.expires_at else "Never"
        expires = expires[:23].ljust(23)
        
        print(f"  │ {vol_name} │ {snap_name} │ {size} │ {expires} │")
        
    print("  └───────────────────────┴──────────────────────────┴─────────────┴─────────────────────────┘")
    
    # Quota status
    print("\n📊 Quota Status:")
    
    quota_status = storage.get_quota_status()
    
    for qs in quota_status[:5]:
        alert_icon = {"ok": "✓", "warning": "⚠", "critical": "🔴"}.get(qs['alert'], "?")
        
        print(f"  [{alert_icon}] {qs['target_type']}/{qs['target_id']}")
        print(f"      Used: {qs['used_gb']} GB / {qs['limit_gb']} GB ({qs['used_percent']:.1f}%)")
        
    # Replication status
    print("\n🔄 Replication Status:")
    
    for rule in storage.replication_rules.values():
        source_vol = storage.volumes.get(rule.source_volume_id)
        
        print(f"\n  🔄 {rule.name}")
        print(f"     Source: {source_vol.name if source_vol else 'Unknown'}")
        print(f"     Mode: {rule.mode.value}")
        print(f"     Lag: {rule.lag_seconds}s")
        print(f"     Replicated: {rule.bytes_replicated / (1024**3):.2f} GB")
        print(f"     Last Sync: {rule.last_sync.strftime('%H:%M:%S') if rule.last_sync else 'Never'}")
        
    # Tiering status
    print("\n📊 Tiering Status:")
    
    for rule in storage.tiering_rules.values():
        print(f"\n  📊 {rule.name}")
        print(f"     Target Tier: {rule.target_tier.value}")
        print(f"     After {rule.days_not_accessed} days inactive")
        print(f"     Tiered: {rule.bytes_tiered / (1024**3):.2f} GB ({rule.files_tiered} files)")
        
    # Statistics
    print("\n📊 Storage Statistics:")
    
    stats = storage.get_statistics()
    
    print(f"\n  Disks: {stats['healthy_disks']}/{stats['total_disks']} healthy")
    print(f"  Total Disk Capacity: {stats['total_disk_capacity_gb']} GB")
    print("  By Disk Type:")
    for d_type, count in stats['by_disk_type'].items():
        print(f"    {d_type}: {count}")
        
    print(f"\n  Pools: {stats['healthy_pools']}/{stats['total_pools']} healthy")
    print(f"  Pool Capacity: {stats['pool_capacity_gb']} GB")
    print(f"  Pool Used: {stats['pool_used_gb']} GB")
    print("  By Tier (GB):")
    for tier, capacity in stats['by_tier_gb'].items():
        print(f"    {tier}: {capacity}")
        
    print(f"\n  Volumes: {stats['total_volumes']}")
    print("  By Status:")
    for status, count in stats['by_volume_status'].items():
        print(f"    {status}: {count}")
        
    print(f"\n  Snapshots: {stats['total_snapshots']} ({stats['snapshot_size_gb']} GB)")
    print(f"  Quotas: {stats['total_quotas']}")
    print(f"  Replication Rules: {stats['replication_rules']}")
    print(f"  Tiering Rules: {stats['tiering_rules']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                      Storage Manager Platform                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Disk Capacity:         {stats['total_disk_capacity_gb']:>10} GB                        │")
    print(f"│ Pool Capacity:               {stats['pool_capacity_gb']:>10} GB                        │")
    print(f"│ Pool Used:                   {stats['pool_used_gb']:>10} GB                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Volumes:               {stats['total_volumes']:>12}                          │")
    print(f"│ Total Snapshots:             {stats['total_snapshots']:>12}                          │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Storage Manager Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
