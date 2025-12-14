#!/usr/bin/env python3
"""
Server Init - Iteration 175: Backup & Recovery Platform
Платформа резервного копирования и восстановления

Функционал:
- Backup Management - управление резервными копиями
- Incremental/Full Backups - инкрементные/полные бэкапы
- Retention Policies - политики хранения
- Point-in-Time Recovery - восстановление на момент времени
- Disaster Recovery - аварийное восстановление
- Cross-Region Replication - репликация между регионами
- Backup Verification - проверка бэкапов
- Recovery Testing - тестирование восстановления
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid
import hashlib


class BackupType(Enum):
    """Тип резервной копии"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"


class BackupStatus(Enum):
    """Статус резервной копии"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"
    EXPIRED = "expired"
    DELETED = "deleted"


class RecoveryStatus(Enum):
    """Статус восстановления"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class StorageClass(Enum):
    """Класс хранилища"""
    HOT = "hot"  # Fast access, high cost
    WARM = "warm"  # Medium access, medium cost
    COLD = "cold"  # Slow access, low cost
    ARCHIVE = "archive"  # Very slow, very low cost


class ResourceType(Enum):
    """Тип ресурса"""
    DATABASE = "database"
    FILESYSTEM = "filesystem"
    VOLUME = "volume"
    CONFIG = "config"
    SECRET = "secret"
    APPLICATION = "application"


@dataclass
class BackupTarget:
    """Целевой ресурс для бэкапа"""
    target_id: str
    name: str = ""
    resource_type: ResourceType = ResourceType.DATABASE
    
    # Connection
    connection_string: str = ""
    credentials_secret: str = ""
    
    # Configuration
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    
    # Size info
    estimated_size_gb: float = 0.0
    last_backup_size_gb: float = 0.0


@dataclass
class RetentionPolicy:
    """Политика хранения"""
    policy_id: str
    name: str = ""
    
    # Retention periods
    hourly_retention: int = 24  # Keep hourly backups for N hours
    daily_retention: int = 7  # Keep daily backups for N days
    weekly_retention: int = 4  # Keep weekly backups for N weeks
    monthly_retention: int = 12  # Keep monthly backups for N months
    yearly_retention: int = 3  # Keep yearly backups for N years
    
    # Storage transitions
    hot_to_warm_days: int = 7
    warm_to_cold_days: int = 30
    cold_to_archive_days: int = 90


@dataclass
class BackupSchedule:
    """Расписание резервного копирования"""
    schedule_id: str
    name: str = ""
    
    # Target
    target_id: str = ""
    
    # Schedule
    cron_expression: str = "0 2 * * *"  # 2 AM daily
    timezone: str = "UTC"
    
    # Type
    backup_type: BackupType = BackupType.FULL
    full_backup_day: int = 0  # 0 = Sunday for weekly full
    
    # Retention
    retention_policy_id: str = ""
    
    # State
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None


@dataclass
class Backup:
    """Резервная копия"""
    backup_id: str
    name: str = ""
    
    # Target
    target_id: str = ""
    target_name: str = ""
    
    # Type
    backup_type: BackupType = BackupType.FULL
    parent_backup_id: str = ""  # For incremental
    
    # Status
    status: BackupStatus = BackupStatus.PENDING
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    
    # Size
    size_bytes: int = 0
    compressed_size_bytes: int = 0
    dedup_size_bytes: int = 0
    
    # Storage
    storage_class: StorageClass = StorageClass.HOT
    storage_location: str = ""
    replication_regions: List[str] = field(default_factory=list)
    
    # Verification
    checksum: str = ""
    verified: bool = False
    verification_date: Optional[datetime] = None
    
    # Retention
    retention_policy_id: str = ""
    expires_at: Optional[datetime] = None
    
    # Metadata
    tags: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RecoveryPoint:
    """Точка восстановления"""
    point_id: str
    target_id: str = ""
    
    # Point in time
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Backups needed
    backup_chain: List[str] = field(default_factory=list)  # Backup IDs
    
    # Recovery info
    recovery_time_estimate_minutes: int = 0
    data_size_bytes: int = 0


@dataclass
class RecoveryJob:
    """Задание восстановления"""
    job_id: str
    name: str = ""
    
    # Source
    source_backup_id: str = ""
    recovery_point_id: str = ""
    
    # Target
    target_id: str = ""
    target_type: ResourceType = ResourceType.DATABASE
    restore_location: str = ""  # Where to restore
    
    # Options
    point_in_time: Optional[datetime] = None
    overwrite_existing: bool = False
    verify_after_restore: bool = True
    
    # Status
    status: RecoveryStatus = RecoveryStatus.PENDING
    progress_percent: float = 0.0
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    
    # Result
    files_restored: int = 0
    bytes_restored: int = 0
    errors: List[str] = field(default_factory=list)


@dataclass
class DisasterRecoveryPlan:
    """План аварийного восстановления"""
    plan_id: str
    name: str = ""
    description: str = ""
    
    # Targets
    target_ids: List[str] = field(default_factory=list)
    
    # RPO/RTO
    rpo_minutes: int = 60  # Recovery Point Objective
    rto_minutes: int = 240  # Recovery Time Objective
    
    # Failover
    primary_region: str = ""
    failover_region: str = ""
    auto_failover: bool = False
    
    # Steps
    recovery_steps: List[Dict] = field(default_factory=list)
    
    # Testing
    last_test: Optional[datetime] = None
    test_result: str = ""
    
    # Metadata
    owner: str = ""
    created_at: datetime = field(default_factory=datetime.now)


class BackupStorage:
    """Хранилище бэкапов"""
    
    def __init__(self):
        self.backups: Dict[str, Backup] = {}
        
    def store(self, backup: Backup):
        """Сохранение бэкапа"""
        self.backups[backup.backup_id] = backup
        
    def get(self, backup_id: str) -> Optional[Backup]:
        """Получение бэкапа"""
        return self.backups.get(backup_id)
        
    def list_by_target(self, target_id: str) -> List[Backup]:
        """Получение бэкапов по target"""
        return [b for b in self.backups.values() if b.target_id == target_id]
        
    def list_by_status(self, status: BackupStatus) -> List[Backup]:
        """Получение бэкапов по статусу"""
        return [b for b in self.backups.values() if b.status == status]


class BackupManager:
    """Менеджер резервных копий"""
    
    def __init__(self, storage: BackupStorage):
        self.storage = storage
        self.targets: Dict[str, BackupTarget] = {}
        self.schedules: Dict[str, BackupSchedule] = {}
        self.retention_policies: Dict[str, RetentionPolicy] = {}
        
    def register_target(self, target: BackupTarget):
        """Регистрация target"""
        self.targets[target.target_id] = target
        
    def add_schedule(self, schedule: BackupSchedule):
        """Добавление расписания"""
        self.schedules[schedule.schedule_id] = schedule
        
    def add_retention_policy(self, policy: RetentionPolicy):
        """Добавление политики хранения"""
        self.retention_policies[policy.policy_id] = policy
        
    async def create_backup(
        self,
        target_id: str,
        backup_type: BackupType = BackupType.FULL,
        parent_backup_id: str = ""
    ) -> Backup:
        """Создание бэкапа"""
        target = self.targets.get(target_id)
        if not target:
            raise ValueError(f"Target {target_id} not found")
            
        backup = Backup(
            backup_id=f"backup_{uuid.uuid4().hex[:12]}",
            name=f"{target.name}_{backup_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            target_id=target_id,
            target_name=target.name,
            backup_type=backup_type,
            parent_backup_id=parent_backup_id,
            status=BackupStatus.IN_PROGRESS,
            started_at=datetime.now()
        )
        
        # Simulate backup
        await asyncio.sleep(0.1)
        
        # Calculate size
        base_size = int(target.estimated_size_gb * 1024 * 1024 * 1024)
        
        if backup_type == BackupType.FULL:
            backup.size_bytes = base_size
        elif backup_type == BackupType.INCREMENTAL:
            backup.size_bytes = int(base_size * random.uniform(0.05, 0.2))
        elif backup_type == BackupType.DIFFERENTIAL:
            backup.size_bytes = int(base_size * random.uniform(0.1, 0.4))
        else:
            backup.size_bytes = base_size
            
        # Compression
        backup.compressed_size_bytes = int(backup.size_bytes * random.uniform(0.3, 0.6))
        backup.dedup_size_bytes = int(backup.compressed_size_bytes * random.uniform(0.5, 0.8))
        
        # Generate checksum
        backup.checksum = hashlib.sha256(backup.backup_id.encode()).hexdigest()
        
        # Complete
        backup.completed_at = datetime.now()
        backup.duration_seconds = (backup.completed_at - backup.started_at).total_seconds()
        backup.status = BackupStatus.COMPLETED
        backup.storage_location = f"s3://backups/{target.name}/{backup.backup_id}"
        
        # Set expiration
        backup.expires_at = datetime.now() + timedelta(days=30)
        
        self.storage.store(backup)
        target.last_backup_size_gb = backup.size_bytes / (1024 ** 3)
        
        return backup
        
    async def verify_backup(self, backup_id: str) -> bool:
        """Проверка бэкапа"""
        backup = self.storage.get(backup_id)
        if not backup:
            return False
            
        # Simulate verification
        await asyncio.sleep(0.05)
        
        # 95% success rate
        verified = random.random() < 0.95
        
        if verified:
            backup.status = BackupStatus.VERIFIED
            backup.verified = True
            backup.verification_date = datetime.now()
            
        return verified


class RecoveryManager:
    """Менеджер восстановления"""
    
    def __init__(self, storage: BackupStorage, backup_manager: BackupManager):
        self.storage = storage
        self.backup_manager = backup_manager
        self.recovery_jobs: Dict[str, RecoveryJob] = {}
        
    def get_recovery_points(self, target_id: str) -> List[RecoveryPoint]:
        """Получение точек восстановления"""
        backups = self.storage.list_by_target(target_id)
        completed = [b for b in backups if b.status in [BackupStatus.COMPLETED, BackupStatus.VERIFIED]]
        completed.sort(key=lambda b: b.created_at, reverse=True)
        
        points = []
        for backup in completed:
            # Build backup chain
            chain = [backup.backup_id]
            
            if backup.backup_type != BackupType.FULL:
                # Find parent chain
                current = backup
                while current.parent_backup_id:
                    parent = self.storage.get(current.parent_backup_id)
                    if parent:
                        chain.append(parent.backup_id)
                        if parent.backup_type == BackupType.FULL:
                            break
                        current = parent
                    else:
                        break
                        
            chain.reverse()
            
            point = RecoveryPoint(
                point_id=f"rp_{uuid.uuid4().hex[:8]}",
                target_id=target_id,
                timestamp=backup.created_at,
                backup_chain=chain,
                recovery_time_estimate_minutes=len(chain) * 5 + int(backup.size_bytes / (1024 ** 3) * 2),
                data_size_bytes=sum(
                    self.storage.get(bid).size_bytes
                    for bid in chain if self.storage.get(bid)
                )
            )
            points.append(point)
            
        return points
        
    async def start_recovery(
        self,
        backup_id: str,
        restore_location: str,
        point_in_time: Optional[datetime] = None
    ) -> RecoveryJob:
        """Запуск восстановления"""
        backup = self.storage.get(backup_id)
        if not backup:
            raise ValueError(f"Backup {backup_id} not found")
            
        job = RecoveryJob(
            job_id=f"recovery_{uuid.uuid4().hex[:8]}",
            name=f"Recovery_{backup.target_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            source_backup_id=backup_id,
            target_id=backup.target_id,
            restore_location=restore_location,
            point_in_time=point_in_time,
            status=RecoveryStatus.IN_PROGRESS,
            started_at=datetime.now()
        )
        
        self.recovery_jobs[job.job_id] = job
        
        # Simulate recovery
        await asyncio.sleep(0.1)
        
        job.progress_percent = 100.0
        job.bytes_restored = backup.size_bytes
        job.files_restored = random.randint(100, 10000)
        job.completed_at = datetime.now()
        job.duration_seconds = (job.completed_at - job.started_at).total_seconds()
        job.status = RecoveryStatus.COMPLETED
        
        return job


class ReplicationManager:
    """Менеджер репликации"""
    
    def __init__(self, storage: BackupStorage):
        self.storage = storage
        self.regions = ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]
        
    async def replicate(self, backup_id: str, target_regions: List[str]) -> Dict[str, bool]:
        """Репликация бэкапа в регионы"""
        backup = self.storage.get(backup_id)
        if not backup:
            return {}
            
        results = {}
        for region in target_regions:
            # Simulate replication
            await asyncio.sleep(0.02)
            
            # 98% success rate
            success = random.random() < 0.98
            results[region] = success
            
            if success and region not in backup.replication_regions:
                backup.replication_regions.append(region)
                
        return results


class DisasterRecoveryManager:
    """Менеджер аварийного восстановления"""
    
    def __init__(self, backup_manager: BackupManager, recovery_manager: RecoveryManager):
        self.backup_manager = backup_manager
        self.recovery_manager = recovery_manager
        self.plans: Dict[str, DisasterRecoveryPlan] = {}
        
    def create_plan(self, plan: DisasterRecoveryPlan):
        """Создание плана DR"""
        # Add default steps
        if not plan.recovery_steps:
            plan.recovery_steps = [
                {"order": 1, "name": "Assess damage", "duration_minutes": 15},
                {"order": 2, "name": "Activate DR plan", "duration_minutes": 5},
                {"order": 3, "name": "Restore critical systems", "duration_minutes": 60},
                {"order": 4, "name": "Verify data integrity", "duration_minutes": 30},
                {"order": 5, "name": "Update DNS/routing", "duration_minutes": 10},
                {"order": 6, "name": "Validate services", "duration_minutes": 30},
                {"order": 7, "name": "Notify stakeholders", "duration_minutes": 5}
            ]
            
        self.plans[plan.plan_id] = plan
        
    async def test_plan(self, plan_id: str) -> Dict[str, Any]:
        """Тестирование плана DR"""
        plan = self.plans.get(plan_id)
        if not plan:
            return {"success": False, "error": "Plan not found"}
            
        results = {
            "plan_id": plan_id,
            "test_started": datetime.now(),
            "steps_completed": [],
            "issues": []
        }
        
        total_time = 0
        for step in plan.recovery_steps:
            # Simulate step
            await asyncio.sleep(0.01)
            
            # 95% success per step
            success = random.random() < 0.95
            
            results["steps_completed"].append({
                "name": step["name"],
                "success": success,
                "duration_minutes": step["duration_minutes"]
            })
            
            total_time += step["duration_minutes"]
            
            if not success:
                results["issues"].append(f"Step '{step['name']}' failed")
                
        results["test_completed"] = datetime.now()
        results["total_time_minutes"] = total_time
        results["rto_met"] = total_time <= plan.rto_minutes
        results["success"] = len(results["issues"]) == 0
        
        plan.last_test = datetime.now()
        plan.test_result = "PASSED" if results["success"] else "FAILED"
        
        return results


class BackupRecoveryPlatform:
    """Платформа резервного копирования и восстановления"""
    
    def __init__(self):
        self.storage = BackupStorage()
        self.backup_manager = BackupManager(self.storage)
        self.recovery_manager = RecoveryManager(self.storage, self.backup_manager)
        self.replication_manager = ReplicationManager(self.storage)
        self.dr_manager = DisasterRecoveryManager(self.backup_manager, self.recovery_manager)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        backups = list(self.storage.backups.values())
        
        total_size = sum(b.size_bytes for b in backups)
        compressed_size = sum(b.compressed_size_bytes for b in backups)
        
        return {
            "total_targets": len(self.backup_manager.targets),
            "total_schedules": len(self.backup_manager.schedules),
            "total_backups": len(backups),
            "backups_by_status": {
                status.value: len([b for b in backups if b.status == status])
                for status in BackupStatus
            },
            "backups_by_type": {
                btype.value: len([b for b in backups if b.backup_type == btype])
                for btype in BackupType
            },
            "total_size_gb": total_size / (1024 ** 3),
            "compressed_size_gb": compressed_size / (1024 ** 3),
            "compression_ratio": total_size / compressed_size if compressed_size > 0 else 0,
            "recovery_jobs": len(self.recovery_manager.recovery_jobs),
            "dr_plans": len(self.dr_manager.plans)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 175: Backup & Recovery Platform")
    print("=" * 60)
    
    async def demo():
        platform = BackupRecoveryPlatform()
        print("✓ Backup & Recovery Platform created")
        
        # Register backup targets
        print("\n📦 Registering Backup Targets...")
        
        targets = [
            BackupTarget(
                target_id="target_postgres",
                name="production-postgres",
                resource_type=ResourceType.DATABASE,
                connection_string="postgres://prod-db:5432",
                estimated_size_gb=50.0
            ),
            BackupTarget(
                target_id="target_mongodb",
                name="production-mongodb",
                resource_type=ResourceType.DATABASE,
                connection_string="mongodb://prod-mongo:27017",
                estimated_size_gb=120.0
            ),
            BackupTarget(
                target_id="target_files",
                name="application-data",
                resource_type=ResourceType.FILESYSTEM,
                estimated_size_gb=200.0,
                include_patterns=["/data/**", "/uploads/**"],
                exclude_patterns=["*.tmp", "*.log"]
            ),
            BackupTarget(
                target_id="target_config",
                name="kubernetes-configs",
                resource_type=ResourceType.CONFIG,
                estimated_size_gb=0.1
            ),
        ]
        
        for target in targets:
            platform.backup_manager.register_target(target)
            print(f"  ✓ {target.name} ({target.resource_type.value}) - {target.estimated_size_gb} GB")
            
        # Create retention policies
        print("\n📅 Creating Retention Policies...")
        
        policies = [
            RetentionPolicy(
                policy_id="policy_standard",
                name="Standard Retention",
                hourly_retention=24,
                daily_retention=7,
                weekly_retention=4,
                monthly_retention=12
            ),
            RetentionPolicy(
                policy_id="policy_compliance",
                name="Compliance Retention",
                hourly_retention=48,
                daily_retention=30,
                weekly_retention=12,
                monthly_retention=36,
                yearly_retention=7
            ),
        ]
        
        for policy in policies:
            platform.backup_manager.add_retention_policy(policy)
            print(f"  ✓ {policy.name}")
            print(f"    Hourly: {policy.hourly_retention}h, Daily: {policy.daily_retention}d, Monthly: {policy.monthly_retention}m")
            
        # Create backup schedules
        print("\n⏰ Creating Backup Schedules...")
        
        schedules = [
            BackupSchedule(
                schedule_id="sched_postgres_full",
                name="PostgreSQL Full Backup",
                target_id="target_postgres",
                cron_expression="0 2 * * 0",  # Sunday 2 AM
                backup_type=BackupType.FULL,
                retention_policy_id="policy_compliance"
            ),
            BackupSchedule(
                schedule_id="sched_postgres_incr",
                name="PostgreSQL Incremental",
                target_id="target_postgres",
                cron_expression="0 2 * * 1-6",  # Mon-Sat 2 AM
                backup_type=BackupType.INCREMENTAL,
                retention_policy_id="policy_compliance"
            ),
            BackupSchedule(
                schedule_id="sched_mongo_snap",
                name="MongoDB Snapshot",
                target_id="target_mongodb",
                cron_expression="0 */6 * * *",  # Every 6 hours
                backup_type=BackupType.SNAPSHOT,
                retention_policy_id="policy_standard"
            ),
        ]
        
        for schedule in schedules:
            platform.backup_manager.add_schedule(schedule)
            print(f"  ✓ {schedule.name}")
            print(f"    Target: {schedule.target_id}, Type: {schedule.backup_type.value}")
            print(f"    Cron: {schedule.cron_expression}")
            
        # Create backups
        print("\n💾 Creating Backups...")
        
        # Full backup for PostgreSQL
        full_backup = await platform.backup_manager.create_backup(
            "target_postgres",
            BackupType.FULL
        )
        print(f"\n  Full Backup: {full_backup.name}")
        print(f"    Status: {full_backup.status.value}")
        print(f"    Size: {full_backup.size_bytes / (1024**3):.2f} GB")
        print(f"    Compressed: {full_backup.compressed_size_bytes / (1024**3):.2f} GB")
        print(f"    Duration: {full_backup.duration_seconds:.2f}s")
        
        # Incremental backups
        prev_backup = full_backup
        for i in range(3):
            incr_backup = await platform.backup_manager.create_backup(
                "target_postgres",
                BackupType.INCREMENTAL,
                prev_backup.backup_id
            )
            print(f"\n  Incremental Backup #{i+1}: {incr_backup.name}")
            print(f"    Size: {incr_backup.size_bytes / (1024**3):.2f} GB")
            print(f"    Parent: {incr_backup.parent_backup_id[:20]}...")
            prev_backup = incr_backup
            
        # Snapshot for MongoDB
        mongo_snapshot = await platform.backup_manager.create_backup(
            "target_mongodb",
            BackupType.SNAPSHOT
        )
        print(f"\n  Snapshot: {mongo_snapshot.name}")
        print(f"    Size: {mongo_snapshot.size_bytes / (1024**3):.2f} GB")
        
        # Verify backups
        print("\n✅ Verifying Backups...")
        
        for backup in list(platform.storage.backups.values())[:3]:
            verified = await platform.backup_manager.verify_backup(backup.backup_id)
            status = "✓ Verified" if verified else "✗ Failed"
            print(f"  {backup.name[:40]}: {status}")
            
        # Backup summary
        print("\n📊 Backup Summary:")
        
        print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
        print("  │ Backup                                       │ Type         │ Size (GB) │ Compressed │ Status    │")
        print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
        
        for backup in platform.storage.backups.values():
            name = backup.name[:44].ljust(44)
            btype = backup.backup_type.value[:12].ljust(12)
            size = f"{backup.size_bytes / (1024**3):.2f}".rjust(9)
            comp = f"{backup.compressed_size_bytes / (1024**3):.2f}".rjust(10)
            
            status_icons = {
                BackupStatus.COMPLETED: "🟢",
                BackupStatus.VERIFIED: "✅",
                BackupStatus.FAILED: "🔴",
                BackupStatus.IN_PROGRESS: "🟡",
                BackupStatus.PENDING: "⚪"
            }
            status = f"{status_icons.get(backup.status, '⚪')} {backup.status.value[:7]}".ljust(10)
            print(f"  │ {name} │ {btype} │ {size} │ {comp} │ {status} │")
            
        print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
        
        # Cross-region replication
        print("\n🌍 Cross-Region Replication...")
        
        results = await platform.replication_manager.replicate(
            full_backup.backup_id,
            ["us-west-2", "eu-west-1"]
        )
        
        for region, success in results.items():
            status = "✓ Replicated" if success else "✗ Failed"
            print(f"  {region}: {status}")
            
        print(f"  Replicated to: {', '.join(full_backup.replication_regions)}")
        
        # Recovery points
        print("\n🕐 Available Recovery Points:")
        
        points = platform.recovery_manager.get_recovery_points("target_postgres")
        
        print("\n  ┌─────────────────────────────────────────────────────────────────────────────────┐")
        print("  │ Timestamp                  │ Chain Size │ Data (GB) │ Est. Time │")
        print("  ├─────────────────────────────────────────────────────────────────────────────────┤")
        
        for point in points[:5]:
            ts = point.timestamp.strftime("%Y-%m-%d %H:%M:%S").ljust(26)
            chain = str(len(point.backup_chain)).rjust(10)
            data = f"{point.data_size_bytes / (1024**3):.2f}".rjust(9)
            est = f"{point.recovery_time_estimate_minutes}m".rjust(9)
            print(f"  │ {ts} │ {chain} │ {data} │ {est} │")
            
        print("  └─────────────────────────────────────────────────────────────────────────────────┘")
        
        # Perform recovery
        print("\n🔄 Starting Recovery...")
        
        recovery_job = await platform.recovery_manager.start_recovery(
            full_backup.backup_id,
            restore_location="/restore/postgres_recovery"
        )
        
        print(f"\n  Recovery Job: {recovery_job.name}")
        print(f"  Status: {recovery_job.status.value}")
        print(f"  Progress: {recovery_job.progress_percent:.0f}%")
        print(f"  Files Restored: {recovery_job.files_restored:,}")
        print(f"  Bytes Restored: {recovery_job.bytes_restored / (1024**3):.2f} GB")
        print(f"  Duration: {recovery_job.duration_seconds:.2f}s")
        
        # Disaster Recovery Plan
        print("\n🚨 Creating Disaster Recovery Plan...")
        
        dr_plan = DisasterRecoveryPlan(
            plan_id="dr_critical_systems",
            name="Critical Systems DR Plan",
            description="Recovery plan for critical production systems",
            target_ids=["target_postgres", "target_mongodb"],
            rpo_minutes=15,
            rto_minutes=60,
            primary_region="us-east-1",
            failover_region="us-west-2",
            owner="platform-team@company.com"
        )
        
        platform.dr_manager.create_plan(dr_plan)
        
        print(f"  Plan: {dr_plan.name}")
        print(f"  RPO: {dr_plan.rpo_minutes} minutes")
        print(f"  RTO: {dr_plan.rto_minutes} minutes")
        print(f"  Primary Region: {dr_plan.primary_region}")
        print(f"  Failover Region: {dr_plan.failover_region}")
        
        print("\n  Recovery Steps:")
        for step in dr_plan.recovery_steps:
            print(f"    {step['order']}. {step['name']} ({step['duration_minutes']}m)")
            
        # Test DR Plan
        print("\n🧪 Testing DR Plan...")
        
        test_results = await platform.dr_manager.test_plan(dr_plan.plan_id)
        
        print(f"\n  Test Result: {'✓ PASSED' if test_results['success'] else '✗ FAILED'}")
        print(f"  Total Time: {test_results['total_time_minutes']} minutes")
        print(f"  RTO Met: {'Yes' if test_results['rto_met'] else 'No'}")
        
        if test_results['issues']:
            print("  Issues:")
            for issue in test_results['issues']:
                print(f"    • {issue}")
                
        # Platform statistics
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Targets: {stats['total_targets']}")
        print(f"  Total Schedules: {stats['total_schedules']}")
        print(f"  Total Backups: {stats['total_backups']}")
        print(f"  Total Size: {stats['total_size_gb']:.2f} GB")
        print(f"  Compressed Size: {stats['compressed_size_gb']:.2f} GB")
        print(f"  Compression Ratio: {stats['compression_ratio']:.1f}x")
        print(f"  DR Plans: {stats['dr_plans']}")
        
        print("\n  Backups by Status:")
        for status, count in stats['backups_by_status'].items():
            if count > 0:
                print(f"    • {status}: {count}")
                
        print("\n  Backups by Type:")
        for btype, count in stats['backups_by_type'].items():
            if count > 0:
                print(f"    • {btype}: {count}")
                
        # Dashboard
        print("\n┌────────────────────────────────────────────────────────────────────┐")
        print("│                  Backup & Recovery Dashboard                       │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Backup Targets:              {stats['total_targets']:>10}                       │")
        print(f"│ Active Schedules:            {stats['total_schedules']:>10}                       │")
        print(f"│ Total Backups:               {stats['total_backups']:>10}                       │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Total Data:                  {stats['total_size_gb']:>10.2f} GB                 │")
        print(f"│ Compressed:                  {stats['compressed_size_gb']:>10.2f} GB                 │")
        print(f"│ Compression Ratio:           {stats['compression_ratio']:>10.1f}x                   │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Recovery Jobs:               {stats['recovery_jobs']:>10}                       │")
        print(f"│ DR Plans:                    {stats['dr_plans']:>10}                       │")
        print("└────────────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Backup & Recovery Platform initialized!")
    print("=" * 60)
