#!/usr/bin/env python3
"""
Server Init - Iteration 318: Backup Manager Platform
Платформа управления резервным копированием

Функционал:
- Backup Policies - политики резервного копирования
- Full/Incremental/Differential - типы бэкапов
- Backup Scheduling - планирование бэкапов
- Storage Targets - целевые хранилища
- Retention Management - управление сроками хранения
- Restore Operations - операции восстановления
- Verification - верификация бэкапов
- Reporting - отчетность
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class BackupType(Enum):
    """Тип резервного копирования"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SYNTHETIC = "synthetic"
    SNAPSHOT = "snapshot"


class BackupStatus(Enum):
    """Статус бэкапа"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"
    EXPIRED = "expired"


class StorageType(Enum):
    """Тип хранилища"""
    LOCAL = "local"
    NFS = "nfs"
    S3 = "s3"
    AZURE_BLOB = "azure_blob"
    GCS = "gcs"
    TAPE = "tape"


class RetentionType(Enum):
    """Тип ретеншена"""
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"
    FOREVER = "forever"


class SourceType(Enum):
    """Тип источника"""
    FILESYSTEM = "filesystem"
    DATABASE = "database"
    VIRTUAL_MACHINE = "virtual_machine"
    CONTAINER = "container"
    APPLICATION = "application"


class CompressionType(Enum):
    """Тип сжатия"""
    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"
    ZSTD = "zstd"
    XZ = "xz"


class EncryptionType(Enum):
    """Тип шифрования"""
    NONE = "none"
    AES_128 = "aes_128"
    AES_256 = "aes_256"


@dataclass
class StorageTarget:
    """Целевое хранилище"""
    target_id: str
    name: str
    
    # Type
    storage_type: StorageType = StorageType.LOCAL
    
    # Path/Endpoint
    path: str = ""
    endpoint: str = ""
    
    # Credentials
    access_key: str = ""
    secret_key: str = ""
    
    # Bucket/Container
    bucket: str = ""
    
    # Capacity
    total_bytes: int = 1024 * 1024 * 1024 * 100  # 100GB
    used_bytes: int = 0
    
    # Status
    is_available: bool = True


@dataclass
class BackupSource:
    """Источник для бэкапа"""
    source_id: str
    name: str
    
    # Type
    source_type: SourceType = SourceType.FILESYSTEM
    
    # Location
    paths: List[str] = field(default_factory=list)
    
    # Connection (for DB)
    host: str = ""
    port: int = 0
    database: str = ""
    
    # Exclude patterns
    excludes: List[str] = field(default_factory=list)
    
    # Size estimate
    estimated_size_bytes: int = 0


@dataclass
class BackupPolicy:
    """Политика резервного копирования"""
    policy_id: str
    name: str
    
    # Sources
    source_ids: List[str] = field(default_factory=list)
    
    # Target
    target_id: str = ""
    
    # Backup types
    full_backup_enabled: bool = True
    incremental_enabled: bool = True
    differential_enabled: bool = False
    
    # Schedule (cron-like)
    full_schedule: str = "0 0 * * 0"  # Sunday midnight
    incremental_schedule: str = "0 0 * * 1-6"  # Mon-Sat midnight
    
    # Compression & Encryption
    compression: CompressionType = CompressionType.GZIP
    encryption: EncryptionType = EncryptionType.AES_256
    
    # Retention
    retention_type: RetentionType = RetentionType.DAYS
    retention_value: int = 30
    
    # Options
    verify_after_backup: bool = True
    parallel_streams: int = 4
    bandwidth_limit_mbps: int = 0  # 0 = unlimited
    
    # Status
    is_enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None


@dataclass
class Backup:
    """Резервная копия"""
    backup_id: str
    policy_id: str
    
    # Type
    backup_type: BackupType = BackupType.FULL
    
    # Status
    status: BackupStatus = BackupStatus.PENDING
    
    # Parent (for incremental/differential)
    parent_backup_id: str = ""
    
    # Size
    source_size_bytes: int = 0
    backup_size_bytes: int = 0
    
    # Deduplication
    dedup_ratio: float = 1.0
    
    # Files
    files_count: int = 0
    files_changed: int = 0
    files_new: int = 0
    files_deleted: int = 0
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0
    
    # Performance
    bytes_per_second: float = 0
    
    # Verification
    is_verified: bool = False
    verification_date: Optional[datetime] = None
    
    # Retention
    expires_at: Optional[datetime] = None
    
    # Storage
    target_id: str = ""
    storage_path: str = ""
    
    # Checksum
    checksum: str = ""
    
    # Errors
    error_message: str = ""


@dataclass
class RestoreJob:
    """Задание восстановления"""
    job_id: str
    backup_id: str
    
    # Target
    restore_path: str = ""
    
    # Options
    overwrite_existing: bool = False
    preserve_permissions: bool = True
    
    # Status
    status: BackupStatus = BackupStatus.PENDING
    
    # Progress
    progress_percent: float = 0
    bytes_restored: int = 0
    files_restored: int = 0
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Errors
    error_message: str = ""


@dataclass
class BackupReport:
    """Отчет о резервном копировании"""
    report_id: str
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Statistics
    total_backups: int = 0
    successful_backups: int = 0
    failed_backups: int = 0
    
    # Data
    total_source_bytes: int = 0
    total_backup_bytes: int = 0
    
    # Time
    total_duration_seconds: float = 0
    avg_duration_seconds: float = 0
    
    # Generated
    generated_at: datetime = field(default_factory=datetime.now)


class BackupManager:
    """Менеджер резервного копирования"""
    
    def __init__(self):
        self.storage_targets: Dict[str, StorageTarget] = {}
        self.sources: Dict[str, BackupSource] = {}
        self.policies: Dict[str, BackupPolicy] = {}
        self.backups: Dict[str, Backup] = {}
        self.restore_jobs: Dict[str, RestoreJob] = {}
        self.reports: List[BackupReport] = []
        
    async def create_storage_target(self, name: str,
                                   storage_type: StorageType,
                                   path: str = "",
                                   endpoint: str = "",
                                   bucket: str = "",
                                   total_gb: int = 100) -> StorageTarget:
        """Создание целевого хранилища"""
        target = StorageTarget(
            target_id=f"tgt_{uuid.uuid4().hex[:8]}",
            name=name,
            storage_type=storage_type,
            path=path,
            endpoint=endpoint,
            bucket=bucket,
            total_bytes=total_gb * 1024 * 1024 * 1024
        )
        
        self.storage_targets[target.target_id] = target
        return target
        
    async def create_source(self, name: str,
                           source_type: SourceType,
                           paths: List[str] = None,
                           host: str = "",
                           database: str = "",
                           excludes: List[str] = None,
                           estimated_gb: int = 10) -> BackupSource:
        """Создание источника"""
        source = BackupSource(
            source_id=f"src_{uuid.uuid4().hex[:8]}",
            name=name,
            source_type=source_type,
            paths=paths or [],
            host=host,
            database=database,
            excludes=excludes or [],
            estimated_size_bytes=estimated_gb * 1024 * 1024 * 1024
        )
        
        self.sources[source.source_id] = source
        return source
        
    async def create_policy(self, name: str,
                           source_ids: List[str],
                           target_id: str,
                           full_schedule: str = "0 0 * * 0",
                           incremental_schedule: str = "0 0 * * 1-6",
                           retention_days: int = 30,
                           compression: CompressionType = CompressionType.GZIP,
                           encryption: EncryptionType = EncryptionType.AES_256) -> BackupPolicy:
        """Создание политики"""
        policy = BackupPolicy(
            policy_id=f"pol_{uuid.uuid4().hex[:8]}",
            name=name,
            source_ids=source_ids,
            target_id=target_id,
            full_schedule=full_schedule,
            incremental_schedule=incremental_schedule,
            retention_value=retention_days,
            compression=compression,
            encryption=encryption,
            next_run=datetime.now() + timedelta(hours=random.randint(1, 24))
        )
        
        self.policies[policy.policy_id] = policy
        return policy
        
    async def run_backup(self, policy_id: str,
                        backup_type: BackupType = None,
                        parent_backup_id: str = "") -> Optional[Backup]:
        """Запуск резервного копирования"""
        policy = self.policies.get(policy_id)
        if not policy:
            return None
            
        target = self.storage_targets.get(policy.target_id)
        if not target or not target.is_available:
            return None
            
        # Determine backup type
        if backup_type is None:
            # Check if we need full backup
            full_exists = any(
                b.policy_id == policy_id and 
                b.backup_type == BackupType.FULL and
                b.status == BackupStatus.COMPLETED
                for b in self.backups.values()
            )
            
            backup_type = BackupType.INCREMENTAL if full_exists else BackupType.FULL
            
        # Create backup
        backup = Backup(
            backup_id=f"bkp_{uuid.uuid4().hex[:8]}",
            policy_id=policy_id,
            backup_type=backup_type,
            parent_backup_id=parent_backup_id,
            target_id=policy.target_id,
            started_at=datetime.now()
        )
        
        backup.status = BackupStatus.RUNNING
        
        # Calculate source size
        total_source_size = 0
        for source_id in policy.source_ids:
            source = self.sources.get(source_id)
            if source:
                total_source_size += source.estimated_size_bytes
                
        backup.source_size_bytes = total_source_size
        
        # Simulate backup
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # Simulate compression and dedup
        if backup_type == BackupType.FULL:
            dedup_ratio = random.uniform(1.5, 3.0)
            backup.files_count = random.randint(10000, 100000)
            backup.files_changed = backup.files_count
            backup.files_new = backup.files_count
        else:
            dedup_ratio = random.uniform(5.0, 20.0)
            backup.files_count = random.randint(10000, 100000)
            backup.files_changed = random.randint(100, 5000)
            backup.files_new = random.randint(10, 500)
            backup.files_deleted = random.randint(0, 100)
            
        backup.dedup_ratio = dedup_ratio
        backup.backup_size_bytes = int(total_source_size / dedup_ratio)
        
        # Update storage
        target.used_bytes += backup.backup_size_bytes
        
        # Complete backup
        backup.completed_at = datetime.now()
        backup.duration_seconds = (backup.completed_at - backup.started_at).total_seconds()
        backup.bytes_per_second = backup.backup_size_bytes / max(backup.duration_seconds, 0.001)
        
        backup.storage_path = f"{target.path}/{policy.name}/{backup.backup_id}"
        backup.checksum = f"sha256:{uuid.uuid4().hex}"
        
        # Set retention
        if policy.retention_type == RetentionType.DAYS:
            backup.expires_at = datetime.now() + timedelta(days=policy.retention_value)
        elif policy.retention_type == RetentionType.WEEKS:
            backup.expires_at = datetime.now() + timedelta(weeks=policy.retention_value)
        elif policy.retention_type == RetentionType.MONTHS:
            backup.expires_at = datetime.now() + timedelta(days=policy.retention_value * 30)
        elif policy.retention_type == RetentionType.YEARS:
            backup.expires_at = datetime.now() + timedelta(days=policy.retention_value * 365)
            
        # Simulate success/failure
        if random.random() > 0.05:  # 95% success rate
            backup.status = BackupStatus.COMPLETED
            
            # Verify if enabled
            if policy.verify_after_backup:
                backup.is_verified = True
                backup.verification_date = datetime.now()
                backup.status = BackupStatus.VERIFIED
        else:
            backup.status = BackupStatus.FAILED
            backup.error_message = random.choice([
                "Connection timeout",
                "Insufficient disk space",
                "Permission denied",
                "Network error"
            ])
            
        self.backups[backup.backup_id] = backup
        
        # Update policy
        policy.last_run = datetime.now()
        policy.next_run = datetime.now() + timedelta(hours=24)
        
        return backup
        
    async def verify_backup(self, backup_id: str) -> bool:
        """Верификация бэкапа"""
        backup = self.backups.get(backup_id)
        if not backup:
            return False
            
        # Simulate verification
        await asyncio.sleep(random.uniform(0.05, 0.2))
        
        if random.random() > 0.02:  # 98% verification success
            backup.is_verified = True
            backup.verification_date = datetime.now()
            backup.status = BackupStatus.VERIFIED
            return True
        else:
            backup.error_message = "Verification failed: checksum mismatch"
            return False
            
    async def create_restore_job(self, backup_id: str,
                                restore_path: str,
                                overwrite: bool = False) -> Optional[RestoreJob]:
        """Создание задания восстановления"""
        backup = self.backups.get(backup_id)
        if not backup:
            return None
            
        job = RestoreJob(
            job_id=f"rst_{uuid.uuid4().hex[:8]}",
            backup_id=backup_id,
            restore_path=restore_path,
            overwrite_existing=overwrite
        )
        
        self.restore_jobs[job.job_id] = job
        return job
        
    async def run_restore(self, job_id: str) -> bool:
        """Запуск восстановления"""
        job = self.restore_jobs.get(job_id)
        if not job:
            return False
            
        backup = self.backups.get(job.backup_id)
        if not backup:
            job.status = BackupStatus.FAILED
            job.error_message = "Backup not found"
            return False
            
        job.status = BackupStatus.RUNNING
        job.started_at = datetime.now()
        
        # Simulate restore
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        if random.random() > 0.03:  # 97% success
            job.status = BackupStatus.COMPLETED
            job.progress_percent = 100
            job.bytes_restored = backup.source_size_bytes
            job.files_restored = backup.files_count
        else:
            job.status = BackupStatus.FAILED
            job.error_message = "Restore failed: corrupted data"
            
        job.completed_at = datetime.now()
        
        return job.status == BackupStatus.COMPLETED
        
    async def delete_expired_backups(self) -> int:
        """Удаление просроченных бэкапов"""
        now = datetime.now()
        deleted = 0
        
        for backup_id in list(self.backups.keys()):
            backup = self.backups[backup_id]
            if backup.expires_at and backup.expires_at < now:
                # Free storage
                target = self.storage_targets.get(backup.target_id)
                if target:
                    target.used_bytes -= backup.backup_size_bytes
                    
                backup.status = BackupStatus.EXPIRED
                deleted += 1
                
        return deleted
        
    def generate_report(self, days: int = 7) -> BackupReport:
        """Генерация отчета"""
        cutoff = datetime.now() - timedelta(days=days)
        
        report = BackupReport(
            report_id=f"rpt_{uuid.uuid4().hex[:8]}",
            period_start=cutoff,
            period_end=datetime.now()
        )
        
        for backup in self.backups.values():
            if backup.started_at and backup.started_at >= cutoff:
                report.total_backups += 1
                
                if backup.status in [BackupStatus.COMPLETED, BackupStatus.VERIFIED]:
                    report.successful_backups += 1
                elif backup.status == BackupStatus.FAILED:
                    report.failed_backups += 1
                    
                report.total_source_bytes += backup.source_size_bytes
                report.total_backup_bytes += backup.backup_size_bytes
                report.total_duration_seconds += backup.duration_seconds
                
        if report.total_backups > 0:
            report.avg_duration_seconds = report.total_duration_seconds / report.total_backups
            
        self.reports.append(report)
        return report
        
    def get_backup_chain(self, backup_id: str) -> List[Backup]:
        """Получение цепочки бэкапов"""
        chain = []
        current = self.backups.get(backup_id)
        
        while current:
            chain.append(current)
            if current.parent_backup_id:
                current = self.backups.get(current.parent_backup_id)
            else:
                current = None
                
        return list(reversed(chain))
        
    def get_storage_usage(self) -> Dict[str, Any]:
        """Использование хранилища"""
        usage = {}
        
        for target in self.storage_targets.values():
            used_pct = (target.used_bytes / target.total_bytes * 100) if target.total_bytes > 0 else 0
            free_bytes = target.total_bytes - target.used_bytes
            
            backup_count = sum(1 for b in self.backups.values() if b.target_id == target.target_id)
            
            usage[target.target_id] = {
                "name": target.name,
                "type": target.storage_type.value,
                "total_gb": target.total_bytes / (1024**3),
                "used_gb": target.used_bytes / (1024**3),
                "free_gb": free_bytes / (1024**3),
                "used_percent": used_pct,
                "backup_count": backup_count,
                "is_available": target.is_available
            }
            
        return usage
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_backups = len(self.backups)
        
        by_status = {}
        for b in self.backups.values():
            by_status[b.status.value] = by_status.get(b.status.value, 0) + 1
            
        by_type = {}
        for b in self.backups.values():
            by_type[b.backup_type.value] = by_type.get(b.backup_type.value, 0) + 1
            
        total_source_bytes = sum(b.source_size_bytes for b in self.backups.values())
        total_backup_bytes = sum(b.backup_size_bytes for b in self.backups.values())
        
        successful = sum(1 for b in self.backups.values() 
                        if b.status in [BackupStatus.COMPLETED, BackupStatus.VERIFIED])
        success_rate = (successful / total_backups * 100) if total_backups > 0 else 0
        
        avg_dedup = sum(b.dedup_ratio for b in self.backups.values()) / total_backups if total_backups > 0 else 0
        
        return {
            "total_policies": len(self.policies),
            "enabled_policies": sum(1 for p in self.policies.values() if p.is_enabled),
            "total_sources": len(self.sources),
            "total_targets": len(self.storage_targets),
            "total_backups": total_backups,
            "by_status": by_status,
            "by_type": by_type,
            "total_source_gb": total_source_bytes / (1024**3),
            "total_backup_gb": total_backup_bytes / (1024**3),
            "success_rate": success_rate,
            "avg_dedup_ratio": avg_dedup,
            "total_restore_jobs": len(self.restore_jobs)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 318: Backup Manager Platform")
    print("=" * 60)
    
    bkp = BackupManager()
    print("✓ Backup Manager created")
    
    # Create storage targets
    print("\n💾 Creating Storage Targets...")
    
    targets_data = [
        ("Local NAS", StorageType.NFS, "/backup/nas", "", "", 500),
        ("AWS S3", StorageType.S3, "", "s3.amazonaws.com", "backups-bucket", 1000),
        ("Azure Blob", StorageType.AZURE_BLOB, "", "blob.core.windows.net", "backup-container", 1000),
        ("Tape Library", StorageType.TAPE, "/dev/tape0", "", "", 5000)
    ]
    
    targets = []
    for name, s_type, path, endpoint, bucket, size_gb in targets_data:
        target = await bkp.create_storage_target(name, s_type, path, endpoint, bucket, size_gb)
        targets.append(target)
        print(f"  💾 {name} ({s_type.value}) - {size_gb} GB")
        
    # Create sources
    print("\n📁 Creating Backup Sources...")
    
    sources_data = [
        ("Web Server Files", SourceType.FILESYSTEM, ["/var/www", "/etc/nginx"], 50),
        ("Application Data", SourceType.FILESYSTEM, ["/opt/app/data"], 100),
        ("Database MySQL", SourceType.DATABASE, [], 200),
        ("Database PostgreSQL", SourceType.DATABASE, [], 150),
        ("User Home Directories", SourceType.FILESYSTEM, ["/home"], 500),
        ("Docker Volumes", SourceType.CONTAINER, ["/var/lib/docker/volumes"], 75)
    ]
    
    sources = []
    for name, s_type, paths, size_gb in sources_data:
        source = await bkp.create_source(name, s_type, paths, estimated_gb=size_gb)
        sources.append(source)
        print(f"  📁 {name} ({s_type.value}) - ~{size_gb} GB")
        
    # Create policies
    print("\n📋 Creating Backup Policies...")
    
    policies_data = [
        ("Web Server Backup", [sources[0].source_id], targets[0].target_id, 
         "0 2 * * 0", "0 2 * * 1-6", 30, CompressionType.GZIP),
        ("Application Backup", [sources[1].source_id], targets[0].target_id,
         "0 3 * * 0", "0 3 * * 1-6", 60, CompressionType.ZSTD),
        ("Database Backup", [sources[2].source_id, sources[3].source_id], targets[1].target_id,
         "0 1 * * *", "", 90, CompressionType.LZ4),
        ("User Data Backup", [sources[4].source_id], targets[1].target_id,
         "0 4 * * 0", "0 4 * * 3", 180, CompressionType.GZIP),
        ("Archive to Tape", [sources[0].source_id, sources[1].source_id, sources[4].source_id], 
         targets[3].target_id, "0 0 1 * *", "", 365, CompressionType.XZ)
    ]
    
    policies = []
    for name, src_ids, tgt_id, full_sched, incr_sched, retention, compression in policies_data:
        policy = await bkp.create_policy(name, src_ids, tgt_id, full_sched, incr_sched, retention, compression)
        policies.append(policy)
        print(f"  📋 {name} (retention: {retention} days)")
        
    # Run backups
    print("\n🔄 Running Backups...")
    
    backups = []
    
    # Run full backups first
    for policy in policies[:4]:
        backup = await bkp.run_backup(policy.policy_id, BackupType.FULL)
        if backup:
            backups.append(backup)
            status = "✓" if backup.status in [BackupStatus.COMPLETED, BackupStatus.VERIFIED] else "✗"
            size_mb = backup.backup_size_bytes / (1024 * 1024)
            print(f"  [{status}] {policy.name} - Full backup ({size_mb:.1f} MB)")
            
    # Run incremental backups
    for policy in policies[:3]:
        # Find parent backup
        parent = None
        for b in backups:
            if b.policy_id == policy.policy_id and b.backup_type == BackupType.FULL:
                parent = b
                break
                
        if parent:
            backup = await bkp.run_backup(policy.policy_id, BackupType.INCREMENTAL, parent.backup_id)
            if backup:
                backups.append(backup)
                status = "✓" if backup.status in [BackupStatus.COMPLETED, BackupStatus.VERIFIED] else "✗"
                size_mb = backup.backup_size_bytes / (1024 * 1024)
                print(f"  [{status}] {policy.name} - Incremental ({size_mb:.1f} MB)")
                
    # Backup policies
    print("\n📋 Backup Policies:")
    
    print("\n  ┌──────────────────────────┬─────────────────────┬───────────────┬─────────────┬─────────────────────────┐")
    print("  │ Policy                   │ Compression         │ Encryption    │ Retention   │ Next Run                │")
    print("  ├──────────────────────────┼─────────────────────┼───────────────┼─────────────┼─────────────────────────┤")
    
    for policy in policies:
        name = policy.name[:24].ljust(24)
        comp = policy.compression.value[:19].ljust(19)
        enc = policy.encryption.value[:13].ljust(13)
        ret = f"{policy.retention_value} {policy.retention_type.value}"[:11].ljust(11)
        next_run = policy.next_run.strftime("%Y-%m-%d %H:%M") if policy.next_run else "N/A"
        next_run = next_run[:23].ljust(23)
        
        print(f"  │ {name} │ {comp} │ {enc} │ {ret} │ {next_run} │")
        
    print("  └──────────────────────────┴─────────────────────┴───────────────┴─────────────┴─────────────────────────┘")
    
    # Backup list
    print("\n💾 Backups:")
    
    print("\n  ┌──────────────────────────┬───────────────┬───────────────┬────────────────┬───────────────┬──────────────┐")
    print("  │ Backup                   │ Type          │ Status        │ Size           │ Dedup Ratio   │ Duration     │")
    print("  ├──────────────────────────┼───────────────┼───────────────┼────────────────┼───────────────┼──────────────┤")
    
    for backup in backups:
        policy = bkp.policies.get(backup.policy_id)
        name = (policy.name if policy else "Unknown")[:24].ljust(24)
        b_type = backup.backup_type.value[:13].ljust(13)
        status = backup.status.value[:13].ljust(13)
        size = f"{backup.backup_size_bytes / (1024 * 1024):.1f} MB"[:14].ljust(14)
        dedup = f"{backup.dedup_ratio:.1f}x"[:13].ljust(13)
        duration = f"{backup.duration_seconds:.1f}s"[:12].ljust(12)
        
        print(f"  │ {name} │ {b_type} │ {status} │ {size} │ {dedup} │ {duration} │")
        
    print("  └──────────────────────────┴───────────────┴───────────────┴────────────────┴───────────────┴──────────────┘")
    
    # Backup details
    print("\n📊 Backup Details:")
    
    for backup in backups[:3]:
        policy = bkp.policies.get(backup.policy_id)
        
        print(f"\n  💾 {policy.name if policy else 'Unknown'} ({backup.backup_type.value})")
        print(f"     Status: {backup.status.value}")
        print(f"     Source Size: {backup.source_size_bytes / (1024 * 1024 * 1024):.2f} GB")
        print(f"     Backup Size: {backup.backup_size_bytes / (1024 * 1024):.1f} MB")
        print(f"     Dedup Ratio: {backup.dedup_ratio:.1f}x")
        print(f"     Files: {backup.files_count:,} total, {backup.files_changed:,} changed")
        print(f"     Duration: {backup.duration_seconds:.1f}s ({backup.bytes_per_second / (1024 * 1024):.1f} MB/s)")
        print(f"     Verified: {'✓' if backup.is_verified else '✗'}")
        print(f"     Expires: {backup.expires_at.strftime('%Y-%m-%d') if backup.expires_at else 'Never'}")
        
    # Storage usage
    print("\n💽 Storage Usage:")
    
    usage = bkp.get_storage_usage()
    
    print("\n  ┌─────────────────────────┬───────────────┬─────────────────────────────────────┬────────────────┬──────────┐")
    print("  │ Target                  │ Type          │ Usage                               │ Backups        │ Status   │")
    print("  ├─────────────────────────┼───────────────┼─────────────────────────────────────┼────────────────┼──────────┤")
    
    for target_id, info in usage.items():
        name = info['name'][:23].ljust(23)
        t_type = info['type'][:13].ljust(13)
        
        used_pct = info['used_percent']
        bar_len = int(used_pct / 5)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        usage_str = f"[{bar}] {used_pct:.1f}%".ljust(35)
        
        backups_cnt = str(info['backup_count']).ljust(14)
        status = ("✓ Online" if info['is_available'] else "✗ Offline")[:8].ljust(8)
        
        print(f"  │ {name} │ {t_type} │ {usage_str} │ {backups_cnt} │ {status} │")
        
    print("  └─────────────────────────┴───────────────┴─────────────────────────────────────┴────────────────┴──────────┘")
    
    # Restore demo
    print("\n♻️ Restore Demo:")
    
    if backups:
        restore_backup = backups[0]
        restore_job = await bkp.create_restore_job(restore_backup.backup_id, "/restore/test")
        if restore_job:
            success = await bkp.run_restore(restore_job.job_id)
            status = "✓" if success else "✗"
            print(f"  [{status}] Restored {restore_backup.backup_id}")
            print(f"      Files: {restore_job.files_restored:,}")
            print(f"      Size: {restore_job.bytes_restored / (1024 * 1024):.1f} MB")
            
    # Backup chain
    print("\n🔗 Backup Chain:")
    
    for backup in backups:
        if backup.backup_type == BackupType.INCREMENTAL:
            chain = bkp.get_backup_chain(backup.backup_id)
            
            print(f"\n  Chain for {backup.backup_id}:")
            for i, b in enumerate(chain):
                indent = "  " * i
                print(f"    {indent}└─ {b.backup_id} ({b.backup_type.value})")
            break
            
    # Generate report
    print("\n📊 Backup Report:")
    
    report = bkp.generate_report(30)
    
    print(f"\n  Period: {report.period_start.strftime('%Y-%m-%d')} to {report.period_end.strftime('%Y-%m-%d')}")
    print(f"  Total Backups: {report.total_backups}")
    print(f"  Successful: {report.successful_backups}")
    print(f"  Failed: {report.failed_backups}")
    
    success_rate = (report.successful_backups / report.total_backups * 100) if report.total_backups > 0 else 0
    print(f"  Success Rate: {success_rate:.1f}%")
    
    print(f"\n  Data Protected: {report.total_source_bytes / (1024**3):.2f} GB")
    print(f"  Storage Used: {report.total_backup_bytes / (1024**3):.2f} GB")
    print(f"  Avg Duration: {report.avg_duration_seconds:.1f}s")
    
    # Statistics
    print("\n📊 Backup Statistics:")
    
    stats = bkp.get_statistics()
    
    print(f"\n  Total Policies: {stats['total_policies']}")
    print(f"  Enabled: {stats['enabled_policies']}")
    print(f"  Total Sources: {stats['total_sources']}")
    print(f"  Total Targets: {stats['total_targets']}")
    
    print(f"\n  Total Backups: {stats['total_backups']}")
    print("  By Status:")
    for status, count in stats['by_status'].items():
        print(f"    {status}: {count}")
        
    print("  By Type:")
    for b_type, count in stats['by_type'].items():
        print(f"    {b_type}: {count}")
        
    print(f"\n  Total Data Protected: {stats['total_source_gb']:.2f} GB")
    print(f"  Total Storage Used: {stats['total_backup_gb']:.2f} GB")
    print(f"  Success Rate: {stats['success_rate']:.1f}%")
    print(f"  Avg Dedup Ratio: {stats['avg_dedup_ratio']:.1f}x")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                      Backup Manager Platform                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Policies:              {stats['total_policies']:>12}                          │")
    print(f"│ Total Backups:               {stats['total_backups']:>12}                          │")
    print(f"│ Success Rate:                {stats['success_rate']:>11.1f}%                          │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Data Protected:              {stats['total_source_gb']:>10.2f} GB                        │")
    print(f"│ Storage Used:                {stats['total_backup_gb']:>10.2f} GB                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Backup Manager Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
