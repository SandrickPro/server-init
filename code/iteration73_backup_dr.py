#!/usr/bin/env python3
"""
Server Init - Iteration 73: Backup & Disaster Recovery Platform
Платформа резервного копирования и восстановления

Функционал:
- Backup Scheduling - планирование бэкапов
- Incremental Backups - инкрементальные бэкапы
- Snapshot Management - управление снимками
- Replication - репликация данных
- Recovery Points - точки восстановления
- DR Testing - тестирование DR
- Retention Policies - политики хранения
- Cross-Region DR - кросс-региональное DR
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from collections import defaultdict
import uuid
import random
import hashlib


class BackupType(Enum):
    """Тип бэкапа"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"


class BackupStatus(Enum):
    """Статус бэкапа"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class StorageType(Enum):
    """Тип хранилища"""
    LOCAL = "local"
    S3 = "s3"
    AZURE_BLOB = "azure_blob"
    GCS = "gcs"
    NFS = "nfs"


class RecoveryStatus(Enum):
    """Статус восстановления"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"


class ReplicationMode(Enum):
    """Режим репликации"""
    SYNC = "sync"
    ASYNC = "async"
    SCHEDULED = "scheduled"


@dataclass
class BackupTarget:
    """Цель бэкапа"""
    target_id: str
    name: str
    
    # Тип
    target_type: str = "database"  # database, filesystem, vm, container
    
    # Конфигурация
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Статус
    enabled: bool = True
    last_backup_at: Optional[datetime] = None


@dataclass
class BackupJob:
    """Задание бэкапа"""
    job_id: str
    name: str
    
    # Цель
    target_id: str = ""
    
    # Тип
    backup_type: BackupType = BackupType.FULL
    
    # Расписание (cron-like)
    schedule: str = ""  # "0 2 * * *" = каждый день в 2:00
    
    # Хранение
    retention_days: int = 30
    
    # Статус
    enabled: bool = True
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None


@dataclass
class Backup:
    """Бэкап"""
    backup_id: str
    job_id: str
    
    # Тип
    backup_type: BackupType = BackupType.FULL
    
    # Статус
    status: BackupStatus = BackupStatus.PENDING
    
    # Размер
    size_bytes: int = 0
    compressed_size: int = 0
    
    # Время
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Хранилище
    storage_type: StorageType = StorageType.LOCAL
    storage_path: str = ""
    
    # Верификация
    checksum: str = ""
    verified: bool = False
    
    # Метаданные
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Snapshot:
    """Снимок"""
    snapshot_id: str
    name: str
    
    # Источник
    source_id: str = ""
    source_type: str = ""
    
    # Статус
    status: str = "available"  # creating, available, deleting, error
    
    # Размер
    size_bytes: int = 0
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    # Инкрементальность
    parent_snapshot_id: str = ""
    
    # Теги
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class RecoveryPoint:
    """Точка восстановления"""
    point_id: str
    
    # Источник
    backup_id: str = ""
    snapshot_id: str = ""
    
    # Время
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Тип
    point_type: str = "backup"  # backup, snapshot, replication
    
    # Метрики
    rpo_seconds: int = 0  # Recovery Point Objective
    estimated_rto_seconds: int = 0  # Recovery Time Objective
    
    # Статус
    recoverable: bool = True


@dataclass
class RecoveryJob:
    """Задание восстановления"""
    recovery_id: str
    
    # Источник
    recovery_point_id: str = ""
    
    # Цель
    target_id: str = ""
    target_config: Dict[str, Any] = field(default_factory=dict)
    
    # Статус
    status: RecoveryStatus = RecoveryStatus.PENDING
    
    # Время
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Прогресс
    progress_percent: float = 0.0
    bytes_restored: int = 0
    
    # Ошибка
    error: str = ""


@dataclass
class ReplicationConfig:
    """Конфигурация репликации"""
    replication_id: str
    name: str
    
    # Источник и цель
    source_region: str = ""
    target_region: str = ""
    
    # Режим
    mode: ReplicationMode = ReplicationMode.ASYNC
    
    # Ресурсы
    resource_ids: List[str] = field(default_factory=list)
    
    # Статус
    enabled: bool = True
    lag_seconds: int = 0
    last_sync_at: Optional[datetime] = None


@dataclass
class DRTestResult:
    """Результат DR теста"""
    test_id: str
    
    # Время
    executed_at: datetime = field(default_factory=datetime.now)
    duration_seconds: int = 0
    
    # Результат
    success: bool = False
    
    # Метрики
    actual_rto_seconds: int = 0
    actual_rpo_seconds: int = 0
    
    # Детали
    steps: List[Dict[str, Any]] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)


class BackupScheduler:
    """Планировщик бэкапов"""
    
    def __init__(self):
        self.jobs: Dict[str, BackupJob] = {}
        
    def add_job(self, name: str, target_id: str, backup_type: BackupType,
                schedule: str, retention_days: int = 30) -> BackupJob:
        """Добавление задания"""
        job = BackupJob(
            job_id=f"job_{uuid.uuid4().hex[:8]}",
            name=name,
            target_id=target_id,
            backup_type=backup_type,
            schedule=schedule,
            retention_days=retention_days,
            next_run_at=self._calculate_next_run(schedule)
        )
        
        self.jobs[job.job_id] = job
        return job
        
    def _calculate_next_run(self, schedule: str) -> datetime:
        """Вычисление следующего запуска"""
        # Упрощённый парсер cron
        now = datetime.now()
        
        if schedule == "0 * * * *":  # Каждый час
            return now + timedelta(hours=1)
        elif schedule == "0 2 * * *":  # Каждый день в 2:00
            next_run = now.replace(hour=2, minute=0, second=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            return next_run
        elif schedule == "0 2 * * 0":  # Каждое воскресенье в 2:00
            days_until_sunday = (6 - now.weekday() + 1) % 7
            if days_until_sunday == 0:
                days_until_sunday = 7
            next_run = now + timedelta(days=days_until_sunday)
            return next_run.replace(hour=2, minute=0, second=0)
        else:
            return now + timedelta(hours=1)
            
    def get_due_jobs(self) -> List[BackupJob]:
        """Получение заданий для выполнения"""
        now = datetime.now()
        due_jobs = []
        
        for job in self.jobs.values():
            if job.enabled and job.next_run_at and job.next_run_at <= now:
                due_jobs.append(job)
                
        return due_jobs


class BackupEngine:
    """Движок бэкапов"""
    
    def __init__(self):
        self.backups: Dict[str, Backup] = {}
        self.snapshots: Dict[str, Snapshot] = {}
        
    async def create_backup(self, job: BackupJob, target: BackupTarget) -> Backup:
        """Создание бэкапа"""
        backup = Backup(
            backup_id=f"backup_{uuid.uuid4().hex[:8]}",
            job_id=job.job_id,
            backup_type=job.backup_type,
            status=BackupStatus.RUNNING,
            started_at=datetime.now()
        )
        
        self.backups[backup.backup_id] = backup
        
        try:
            # Симуляция создания бэкапа
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
            # Размер
            base_size = random.randint(1000000, 100000000)
            
            if job.backup_type == BackupType.FULL:
                backup.size_bytes = base_size
            elif job.backup_type == BackupType.INCREMENTAL:
                backup.size_bytes = base_size // 10
            elif job.backup_type == BackupType.DIFFERENTIAL:
                backup.size_bytes = base_size // 3
            elif job.backup_type == BackupType.SNAPSHOT:
                backup.size_bytes = base_size // 5
                
            backup.compressed_size = int(backup.size_bytes * 0.4)
            
            # Checksum
            backup.checksum = hashlib.sha256(
                f"{backup.backup_id}{datetime.now()}".encode()
            ).hexdigest()[:32]
            
            # Storage
            backup.storage_path = f"/backups/{job.target_id}/{backup.backup_id}"
            
            backup.status = BackupStatus.COMPLETED
            backup.completed_at = datetime.now()
            backup.expires_at = datetime.now() + timedelta(days=job.retention_days)
            
            # Обновляем job
            job.last_run_at = datetime.now()
            
        except Exception as e:
            backup.status = BackupStatus.FAILED
            
        return backup
        
    async def create_snapshot(self, source_id: str, source_type: str,
                               name: str = "", parent_id: str = "") -> Snapshot:
        """Создание снимка"""
        snapshot = Snapshot(
            snapshot_id=f"snap_{uuid.uuid4().hex[:8]}",
            name=name or f"snapshot-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            source_id=source_id,
            source_type=source_type,
            status="creating",
            parent_snapshot_id=parent_id
        )
        
        self.snapshots[snapshot.snapshot_id] = snapshot
        
        # Симуляция создания
        await asyncio.sleep(random.uniform(0.3, 1.0))
        
        # Размер зависит от того, инкрементальный ли это снимок
        if parent_id:
            snapshot.size_bytes = random.randint(10000, 1000000)
        else:
            snapshot.size_bytes = random.randint(1000000, 50000000)
            
        snapshot.status = "available"
        
        return snapshot
        
    def verify_backup(self, backup_id: str) -> bool:
        """Верификация бэкапа"""
        backup = self.backups.get(backup_id)
        if not backup:
            return False
            
        # Симуляция верификации
        backup.verified = random.random() > 0.05  # 95% успех
        return backup.verified


class RecoveryEngine:
    """Движок восстановления"""
    
    def __init__(self, backup_engine: BackupEngine):
        self.backup_engine = backup_engine
        self.recovery_points: Dict[str, RecoveryPoint] = {}
        self.recovery_jobs: Dict[str, RecoveryJob] = {}
        
    def create_recovery_point(self, backup_id: str = "",
                               snapshot_id: str = "") -> RecoveryPoint:
        """Создание точки восстановления"""
        point = RecoveryPoint(
            point_id=f"rp_{uuid.uuid4().hex[:8]}",
            backup_id=backup_id,
            snapshot_id=snapshot_id,
            point_type="backup" if backup_id else "snapshot",
            rpo_seconds=random.randint(300, 86400),
            estimated_rto_seconds=random.randint(600, 7200)
        )
        
        self.recovery_points[point.point_id] = point
        return point
        
    async def restore(self, recovery_point_id: str,
                      target_config: Dict[str, Any] = None) -> RecoveryJob:
        """Восстановление"""
        point = self.recovery_points.get(recovery_point_id)
        if not point:
            raise ValueError(f"Recovery point {recovery_point_id} not found")
            
        job = RecoveryJob(
            recovery_id=f"rec_{uuid.uuid4().hex[:8]}",
            recovery_point_id=recovery_point_id,
            target_config=target_config or {},
            status=RecoveryStatus.IN_PROGRESS,
            started_at=datetime.now()
        )
        
        self.recovery_jobs[job.recovery_id] = job
        
        try:
            # Симуляция восстановления
            total_bytes = random.randint(10000000, 500000000)
            
            for progress in range(0, 101, 10):
                await asyncio.sleep(random.uniform(0.1, 0.3))
                job.progress_percent = progress
                job.bytes_restored = int(total_bytes * progress / 100)
                
            job.status = RecoveryStatus.VERIFYING
            await asyncio.sleep(0.5)
            
            job.status = RecoveryStatus.COMPLETED
            job.completed_at = datetime.now()
            
        except Exception as e:
            job.status = RecoveryStatus.FAILED
            job.error = str(e)
            
        return job
        
    def get_recovery_points(self, target_id: str = None,
                             limit: int = 10) -> List[RecoveryPoint]:
        """Получение точек восстановления"""
        points = list(self.recovery_points.values())
        points.sort(key=lambda p: p.timestamp, reverse=True)
        return points[:limit]


class ReplicationManager:
    """Менеджер репликации"""
    
    def __init__(self):
        self.configs: Dict[str, ReplicationConfig] = {}
        
    def create_replication(self, name: str, source_region: str,
                            target_region: str, mode: ReplicationMode,
                            resource_ids: List[str]) -> ReplicationConfig:
        """Создание репликации"""
        config = ReplicationConfig(
            replication_id=f"repl_{uuid.uuid4().hex[:8]}",
            name=name,
            source_region=source_region,
            target_region=target_region,
            mode=mode,
            resource_ids=resource_ids
        )
        
        self.configs[config.replication_id] = config
        return config
        
    async def sync(self, replication_id: str) -> bool:
        """Синхронизация"""
        config = self.configs.get(replication_id)
        if not config or not config.enabled:
            return False
            
        # Симуляция синхронизации
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        config.last_sync_at = datetime.now()
        config.lag_seconds = random.randint(0, 300)
        
        return True


class DRTestRunner:
    """Запуск DR тестов"""
    
    def __init__(self, recovery_engine: RecoveryEngine):
        self.recovery_engine = recovery_engine
        self.test_results: List[DRTestResult] = []
        
    async def run_dr_test(self, recovery_point_ids: List[str]) -> DRTestResult:
        """Запуск DR теста"""
        result = DRTestResult(
            test_id=f"drtest_{uuid.uuid4().hex[:8]}"
        )
        
        start_time = datetime.now()
        steps = []
        issues = []
        
        try:
            # Шаг 1: Инициализация
            steps.append({
                "step": "initialization",
                "status": "success",
                "duration": random.randint(5, 30)
            })
            await asyncio.sleep(0.2)
            
            # Шаг 2: Валидация точек восстановления
            for rp_id in recovery_point_ids:
                rp = self.recovery_engine.recovery_points.get(rp_id)
                if rp and rp.recoverable:
                    steps.append({
                        "step": f"validate_{rp_id}",
                        "status": "success",
                        "duration": random.randint(10, 60)
                    })
                else:
                    steps.append({
                        "step": f"validate_{rp_id}",
                        "status": "failed",
                        "duration": random.randint(5, 20)
                    })
                    issues.append(f"Recovery point {rp_id} not recoverable")
                    
            await asyncio.sleep(0.3)
            
            # Шаг 3: Тестовое восстановление
            if recovery_point_ids:
                steps.append({
                    "step": "test_restore",
                    "status": "success",
                    "duration": random.randint(300, 1800)
                })
                
            # Шаг 4: Верификация данных
            steps.append({
                "step": "data_verification",
                "status": "success",
                "duration": random.randint(60, 300)
            })
            
            # Шаг 5: Очистка
            steps.append({
                "step": "cleanup",
                "status": "success",
                "duration": random.randint(30, 120)
            })
            
            result.success = len(issues) == 0
            
        except Exception as e:
            issues.append(str(e))
            result.success = False
            
        result.duration_seconds = int((datetime.now() - start_time).total_seconds())
        result.actual_rto_seconds = sum(s.get("duration", 0) for s in steps)
        result.actual_rpo_seconds = random.randint(300, 3600)
        result.steps = steps
        result.issues = issues
        
        self.test_results.append(result)
        
        return result


class BackupDRPlatform:
    """Платформа резервного копирования и DR"""
    
    def __init__(self):
        self.targets: Dict[str, BackupTarget] = {}
        
        self.scheduler = BackupScheduler()
        self.backup_engine = BackupEngine()
        self.recovery_engine = RecoveryEngine(self.backup_engine)
        self.replication_manager = ReplicationManager()
        self.dr_test_runner = DRTestRunner(self.recovery_engine)
        
    def add_target(self, name: str, target_type: str,
                    config: Dict[str, Any] = None) -> BackupTarget:
        """Добавление цели бэкапа"""
        target = BackupTarget(
            target_id=f"target_{uuid.uuid4().hex[:8]}",
            name=name,
            target_type=target_type,
            config=config or {}
        )
        
        self.targets[target.target_id] = target
        return target
        
    def create_backup_job(self, name: str, target_id: str,
                           backup_type: BackupType, schedule: str,
                           retention_days: int = 30) -> BackupJob:
        """Создание задания бэкапа"""
        return self.scheduler.add_job(
            name, target_id, backup_type, schedule, retention_days
        )
        
    async def run_backup(self, job_id: str) -> Optional[Backup]:
        """Запуск бэкапа"""
        job = self.scheduler.jobs.get(job_id)
        target = self.targets.get(job.target_id) if job else None
        
        if not job or not target:
            return None
            
        backup = await self.backup_engine.create_backup(job, target)
        
        if backup.status == BackupStatus.COMPLETED:
            # Создаём точку восстановления
            self.recovery_engine.create_recovery_point(backup_id=backup.backup_id)
            
            # Обновляем цель
            target.last_backup_at = datetime.now()
            
        return backup
        
    async def create_snapshot(self, target_id: str) -> Optional[Snapshot]:
        """Создание снимка"""
        target = self.targets.get(target_id)
        if not target:
            return None
            
        snapshot = await self.backup_engine.create_snapshot(
            source_id=target_id,
            source_type=target.target_type
        )
        
        if snapshot.status == "available":
            self.recovery_engine.create_recovery_point(snapshot_id=snapshot.snapshot_id)
            
        return snapshot
        
    async def restore(self, recovery_point_id: str,
                      target_config: Dict[str, Any] = None) -> RecoveryJob:
        """Восстановление"""
        return await self.recovery_engine.restore(recovery_point_id, target_config)
        
    def create_replication(self, name: str, source_region: str,
                            target_region: str, mode: ReplicationMode,
                            target_ids: List[str]) -> ReplicationConfig:
        """Создание репликации"""
        return self.replication_manager.create_replication(
            name, source_region, target_region, mode, target_ids
        )
        
    async def run_dr_test(self) -> DRTestResult:
        """Запуск DR теста"""
        recovery_points = self.recovery_engine.get_recovery_points(limit=5)
        point_ids = [rp.point_id for rp in recovery_points]
        
        return await self.dr_test_runner.run_dr_test(point_ids)
        
    def get_stats(self) -> Dict[str, Any]:
        """Статистика платформы"""
        backups = self.backup_engine.backups.values()
        completed = [b for b in backups if b.status == BackupStatus.COMPLETED]
        
        total_size = sum(b.size_bytes for b in completed)
        compressed_size = sum(b.compressed_size for b in completed)
        
        return {
            "targets": len(self.targets),
            "backup_jobs": len(self.scheduler.jobs),
            "backups": len(self.backup_engine.backups),
            "completed_backups": len(completed),
            "snapshots": len(self.backup_engine.snapshots),
            "recovery_points": len(self.recovery_engine.recovery_points),
            "replications": len(self.replication_manager.configs),
            "dr_tests": len(self.dr_test_runner.test_results),
            "total_backup_size_gb": total_size / (1024**3),
            "compressed_size_gb": compressed_size / (1024**3)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 73: Backup & Disaster Recovery")
    print("=" * 60)
    
    async def demo():
        platform = BackupDRPlatform()
        print("✓ Backup & DR Platform created")
        
        # Добавление целей бэкапа
        print("\n📁 Adding Backup Targets...")
        
        db_target = platform.add_target(
            name="Production Database",
            target_type="database",
            config={
                "type": "postgresql",
                "host": "db.example.com",
                "database": "production"
            }
        )
        print(f"  ✓ Target: {db_target.name}")
        
        files_target = platform.add_target(
            name="File Server",
            target_type="filesystem",
            config={
                "path": "/data/files",
                "exclude": ["*.tmp", "*.log"]
            }
        )
        print(f"  ✓ Target: {files_target.name}")
        
        vm_target = platform.add_target(
            name="Web Server VM",
            target_type="vm",
            config={
                "vm_id": "vm-web-001",
                "hypervisor": "vmware"
            }
        )
        print(f"  ✓ Target: {vm_target.name}")
        
        # Создание заданий бэкапа
        print("\n📋 Creating Backup Jobs...")
        
        db_full_job = platform.create_backup_job(
            name="Database Full Backup",
            target_id=db_target.target_id,
            backup_type=BackupType.FULL,
            schedule="0 2 * * 0",  # Еженедельно в воскресенье
            retention_days=90
        )
        print(f"  ✓ Job: {db_full_job.name} (Full, Weekly)")
        
        db_incr_job = platform.create_backup_job(
            name="Database Incremental",
            target_id=db_target.target_id,
            backup_type=BackupType.INCREMENTAL,
            schedule="0 2 * * *",  # Ежедневно
            retention_days=14
        )
        print(f"  ✓ Job: {db_incr_job.name} (Incremental, Daily)")
        
        files_job = platform.create_backup_job(
            name="File Server Backup",
            target_id=files_target.target_id,
            backup_type=BackupType.DIFFERENTIAL,
            schedule="0 3 * * *",
            retention_days=30
        )
        print(f"  ✓ Job: {files_job.name} (Differential, Daily)")
        
        # Выполнение бэкапов
        print("\n💾 Running Backups...")
        
        for job in [db_full_job, db_incr_job, files_job]:
            backup = await platform.run_backup(job.job_id)
            if backup:
                status = "✓" if backup.status == BackupStatus.COMPLETED else "✗"
                size_mb = backup.size_bytes / (1024 * 1024)
                compressed_mb = backup.compressed_size / (1024 * 1024)
                print(f"  {status} {job.name}:")
                print(f"      Size: {size_mb:.2f} MB → {compressed_mb:.2f} MB")
                print(f"      Checksum: {backup.checksum[:16]}...")
                
        # Создание снимков
        print("\n📸 Creating Snapshots...")
        
        for target in [db_target, vm_target]:
            snapshot = await platform.create_snapshot(target.target_id)
            if snapshot:
                size_mb = snapshot.size_bytes / (1024 * 1024)
                print(f"  ✓ Snapshot: {snapshot.name}")
                print(f"      Source: {target.name}, Size: {size_mb:.2f} MB")
                
        # Точки восстановления
        print("\n⏱️ Recovery Points:")
        recovery_points = platform.recovery_engine.get_recovery_points(limit=5)
        
        for rp in recovery_points:
            rpo_hours = rp.rpo_seconds / 3600
            rto_minutes = rp.estimated_rto_seconds / 60
            print(f"  - {rp.point_id[:12]}... ({rp.point_type})")
            print(f"      RPO: {rpo_hours:.1f}h, Estimated RTO: {rto_minutes:.0f}min")
            
        # Восстановление
        print("\n🔄 Testing Recovery...")
        
        if recovery_points:
            rp = recovery_points[0]
            recovery_job = await platform.restore(
                rp.point_id,
                target_config={"restore_to": "test_environment"}
            )
            
            print(f"  Recovery Job: {recovery_job.recovery_id}")
            print(f"  Status: {recovery_job.status.value}")
            print(f"  Progress: {recovery_job.progress_percent:.0f}%")
            print(f"  Restored: {recovery_job.bytes_restored / (1024*1024):.2f} MB")
            
        # Настройка репликации
        print("\n🔄 Setting Up Replication...")
        
        replication = platform.create_replication(
            name="Cross-Region DR",
            source_region="us-east-1",
            target_region="us-west-2",
            mode=ReplicationMode.ASYNC,
            target_ids=[db_target.target_id, files_target.target_id]
        )
        print(f"  ✓ Replication: {replication.name}")
        print(f"    {replication.source_region} → {replication.target_region}")
        print(f"    Mode: {replication.mode.value}")
        
        await platform.replication_manager.sync(replication.replication_id)
        print(f"    Lag: {replication.lag_seconds}s")
        
        # DR тест
        print("\n🧪 Running DR Test...")
        
        dr_result = await platform.run_dr_test()
        
        status = "✓ PASSED" if dr_result.success else "✗ FAILED"
        print(f"  {status}")
        print(f"  Duration: {dr_result.duration_seconds}s")
        print(f"  Actual RTO: {dr_result.actual_rto_seconds}s")
        print(f"  Actual RPO: {dr_result.actual_rpo_seconds}s")
        
        print(f"  Steps:")
        for step in dr_result.steps[:5]:
            print(f"    - {step['step']}: {step['status']} ({step['duration']}s)")
            
        if dr_result.issues:
            print(f"  Issues:")
            for issue in dr_result.issues:
                print(f"    ⚠️ {issue}")
                
        # Статистика
        print("\n📊 Platform Statistics:")
        stats = platform.get_stats()
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")
                
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Backup & Disaster Recovery Platform initialized!")
    print("=" * 60)
