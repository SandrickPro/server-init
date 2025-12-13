#!/usr/bin/env python3
"""
Server Init - Iteration 50: Backup & Disaster Recovery
Резервное копирование и аварийное восстановление

Функционал:
- Backup Orchestration - оркестрация резервного копирования
- Snapshot Management - управление снимками
- Incremental Backup - инкрементальное резервное копирование
- Cross-Region Replication - репликация между регионами
- Point-in-Time Recovery - восстановление на момент времени
- Disaster Recovery Plans - планы аварийного восстановления
- RTO/RPO Management - управление RTO/RPO
- Backup Verification - верификация бэкапов
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


class BackupType(Enum):
    """Тип резервного копирования"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"
    CONTINUOUS = "continuous"


class BackupStatus(Enum):
    """Статус бэкапа"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFYING = "verifying"
    VERIFIED = "verified"
    EXPIRED = "expired"


class ResourceType(Enum):
    """Тип ресурса"""
    DATABASE = "database"
    FILESYSTEM = "filesystem"
    VIRTUAL_MACHINE = "virtual_machine"
    CONTAINER = "container"
    KUBERNETES = "kubernetes"
    OBJECT_STORAGE = "object_storage"
    BLOCK_STORAGE = "block_storage"


class RecoveryStatus(Enum):
    """Статус восстановления"""
    PENDING = "pending"
    PREPARING = "preparing"
    RESTORING = "restoring"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DRStatus(Enum):
    """Статус DR"""
    ACTIVE = "active"
    FAILOVER = "failover"
    FAILBACK = "failback"
    MAINTENANCE = "maintenance"
    DEGRADED = "degraded"


@dataclass
class BackupTarget:
    """Цель резервного копирования"""
    target_id: str
    name: str
    resource_type: ResourceType
    
    # Источник
    source_path: str = ""
    source_host: str = ""
    
    # Конфигурация
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    
    # Метаданные
    size_bytes: int = 0
    last_backup: Optional[datetime] = None
    
    # Статус
    enabled: bool = True


@dataclass
class BackupJob:
    """Задача резервного копирования"""
    job_id: str
    name: str
    
    # Тип
    backup_type: BackupType = BackupType.FULL
    
    # Цели
    targets: List[str] = field(default_factory=list)
    
    # Расписание
    schedule_cron: str = "0 2 * * *"  # 2:00 AM daily
    
    # Retention
    retention_days: int = 30
    retention_count: int = 10
    
    # Destination
    destination: str = ""  # s3://bucket/path, /backup/path
    
    # Опции
    compression: bool = True
    encryption: bool = True
    deduplication: bool = False
    
    # Состояние
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None


@dataclass
class Backup:
    """Резервная копия"""
    backup_id: str
    job_id: str
    
    # Тип
    backup_type: BackupType = BackupType.FULL
    
    # Родитель (для инкрементальных)
    parent_backup_id: Optional[str] = None
    
    # Данные
    size_bytes: int = 0
    compressed_size_bytes: int = 0
    
    # Файлы
    files_count: int = 0
    
    # Checksums
    checksum: str = ""
    
    # Время
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    
    # Expiration
    expires_at: Optional[datetime] = None
    
    # Статус
    status: BackupStatus = BackupStatus.PENDING
    error_message: Optional[str] = None
    
    # Location
    location: str = ""
    
    # Verification
    verified: bool = False
    verified_at: Optional[datetime] = None


@dataclass
class Snapshot:
    """Снимок"""
    snapshot_id: str
    resource_id: str
    resource_type: ResourceType
    
    # Данные
    size_bytes: int = 0
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    
    # Консистентность
    consistent: bool = True
    
    # Описание
    description: str = ""
    
    # Статус
    status: BackupStatus = BackupStatus.COMPLETED
    
    # Теги
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class RecoveryPoint:
    """Точка восстановления"""
    point_id: str
    
    # Время
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Связанные бэкапы
    backup_ids: List[str] = field(default_factory=list)
    snapshot_ids: List[str] = field(default_factory=list)
    
    # Тип
    point_type: str = "scheduled"  # scheduled, manual, pre-change
    
    # Описание
    description: str = ""
    
    # Восстановимость
    restorable: bool = True


@dataclass
class RecoveryJob:
    """Задача восстановления"""
    recovery_id: str
    
    # Источник
    backup_id: Optional[str] = None
    snapshot_id: Optional[str] = None
    point_in_time: Optional[datetime] = None
    
    # Цель
    target_location: str = ""
    target_host: str = ""
    
    # Опции
    overwrite: bool = False
    parallel_streams: int = 4
    
    # Прогресс
    progress_percent: float = 0.0
    bytes_restored: int = 0
    files_restored: int = 0
    
    # Время
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_time_remaining: Optional[timedelta] = None
    
    # Статус
    status: RecoveryStatus = RecoveryStatus.PENDING
    error_message: Optional[str] = None


@dataclass
class DRPlan:
    """План аварийного восстановления"""
    plan_id: str
    name: str
    
    # Цели
    rto_minutes: int = 60  # Recovery Time Objective
    rpo_minutes: int = 15  # Recovery Point Objective
    
    # Ресурсы
    protected_resources: List[str] = field(default_factory=list)
    
    # Регионы
    primary_region: str = ""
    dr_region: str = ""
    
    # Replication
    replication_mode: str = "async"  # sync, async
    replication_lag_seconds: int = 0
    
    # Runbook
    runbook_steps: List[Dict[str, Any]] = field(default_factory=list)
    
    # Состояние
    status: DRStatus = DRStatus.ACTIVE
    
    # Тестирование
    last_test: Optional[datetime] = None
    test_result: Optional[str] = None
    
    # Failover
    last_failover: Optional[datetime] = None


@dataclass
class ReplicationTarget:
    """Цель репликации"""
    target_id: str
    name: str
    
    # Регион
    region: str = ""
    
    # Endpoint
    endpoint: str = ""
    
    # Статус
    status: str = "active"  # active, syncing, error
    
    # Метрики
    lag_seconds: int = 0
    last_sync: Optional[datetime] = None
    
    # Bytes replicated
    bytes_replicated: int = 0


class BackupOrchestrator:
    """Оркестратор резервного копирования"""
    
    def __init__(self):
        self.targets: Dict[str, BackupTarget] = {}
        self.jobs: Dict[str, BackupJob] = {}
        self.backups: Dict[str, Backup] = {}
        self.snapshots: Dict[str, Snapshot] = {}
        self.recovery_points: Dict[str, RecoveryPoint] = {}
        
    def register_target(self, name: str, resource_type: ResourceType,
                         source_path: str, **kwargs) -> BackupTarget:
        """Регистрация цели"""
        target = BackupTarget(
            target_id=f"target_{uuid.uuid4().hex[:8]}",
            name=name,
            resource_type=resource_type,
            source_path=source_path,
            **kwargs
        )
        
        self.targets[target.target_id] = target
        return target
        
    def create_job(self, name: str, targets: List[str],
                    backup_type: BackupType = BackupType.FULL,
                    **kwargs) -> BackupJob:
        """Создание задачи"""
        job = BackupJob(
            job_id=f"job_{uuid.uuid4().hex[:8]}",
            name=name,
            targets=targets,
            backup_type=backup_type,
            **kwargs
        )
        
        self.jobs[job.job_id] = job
        return job
        
    async def run_backup(self, job_id: str) -> Backup:
        """Запуск резервного копирования"""
        job = self.jobs.get(job_id)
        if not job:
            raise ValueError("Job not found")
            
        backup = Backup(
            backup_id=f"backup_{uuid.uuid4().hex[:8]}",
            job_id=job_id,
            backup_type=job.backup_type,
            location=job.destination,
            expires_at=datetime.now() + timedelta(days=job.retention_days)
        )
        
        backup.status = BackupStatus.RUNNING
        self.backups[backup.backup_id] = backup
        
        try:
            # Симуляция бэкапа
            total_size = 0
            files_count = 0
            
            for target_id in job.targets:
                target = self.targets.get(target_id)
                if not target:
                    continue
                    
                # Симуляция обработки
                await asyncio.sleep(0.1)
                
                target_size = random.randint(1000000, 100000000)
                total_size += target_size
                files_count += random.randint(100, 1000)
                
                target.last_backup = datetime.now()
                
            backup.size_bytes = total_size
            backup.compressed_size_bytes = int(total_size * 0.4) if job.compression else total_size
            backup.files_count = files_count
            backup.checksum = hashlib.sha256(str(time.time()).encode()).hexdigest()
            
            backup.status = BackupStatus.COMPLETED
            backup.completed_at = datetime.now()
            backup.duration_seconds = (backup.completed_at - backup.started_at).total_seconds()
            
            # Создание recovery point
            self._create_recovery_point(backup)
            
            job.last_run = datetime.now()
            
        except Exception as e:
            backup.status = BackupStatus.FAILED
            backup.error_message = str(e)
            
        return backup
        
    def _create_recovery_point(self, backup: Backup):
        """Создание точки восстановления"""
        point = RecoveryPoint(
            point_id=f"rp_{uuid.uuid4().hex[:8]}",
            timestamp=backup.completed_at or datetime.now(),
            backup_ids=[backup.backup_id],
            point_type="scheduled"
        )
        
        self.recovery_points[point.point_id] = point
        
    async def create_snapshot(self, resource_id: str, 
                               resource_type: ResourceType,
                               description: str = "") -> Snapshot:
        """Создание снимка"""
        snapshot = Snapshot(
            snapshot_id=f"snap_{uuid.uuid4().hex[:8]}",
            resource_id=resource_id,
            resource_type=resource_type,
            description=description,
            status=BackupStatus.PENDING
        )
        
        self.snapshots[snapshot.snapshot_id] = snapshot
        
        # Симуляция создания снимка
        await asyncio.sleep(0.1)
        
        snapshot.size_bytes = random.randint(10000000, 1000000000)
        snapshot.status = BackupStatus.COMPLETED
        
        return snapshot
        
    async def verify_backup(self, backup_id: str) -> Dict[str, Any]:
        """Верификация бэкапа"""
        backup = self.backups.get(backup_id)
        if not backup:
            return {"error": "Backup not found"}
            
        backup.status = BackupStatus.VERIFYING
        
        # Симуляция верификации
        await asyncio.sleep(0.1)
        
        # 95% успешная верификация
        if random.random() > 0.05:
            backup.verified = True
            backup.verified_at = datetime.now()
            backup.status = BackupStatus.VERIFIED
            
            return {
                "backup_id": backup_id,
                "verified": True,
                "checksum_valid": True,
                "files_intact": True
            }
        else:
            backup.status = BackupStatus.COMPLETED  # Не прошёл верификацию
            
            return {
                "backup_id": backup_id,
                "verified": False,
                "error": "Checksum mismatch"
            }
            
    def get_recovery_points(self, start_time: Optional[datetime] = None,
                             end_time: Optional[datetime] = None) -> List[RecoveryPoint]:
        """Получение точек восстановления"""
        points = list(self.recovery_points.values())
        
        if start_time:
            points = [p for p in points if p.timestamp >= start_time]
            
        if end_time:
            points = [p for p in points if p.timestamp <= end_time]
            
        return sorted(points, key=lambda p: p.timestamp, reverse=True)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_size = sum(b.size_bytes for b in self.backups.values())
        compressed_size = sum(b.compressed_size_bytes for b in self.backups.values())
        
        return {
            "targets": len(self.targets),
            "jobs": len(self.jobs),
            "backups": len(self.backups),
            "snapshots": len(self.snapshots),
            "recovery_points": len(self.recovery_points),
            "total_size_gb": round(total_size / (1024**3), 2),
            "compressed_size_gb": round(compressed_size / (1024**3), 2),
            "compression_ratio": round(compressed_size / total_size, 2) if total_size > 0 else 0,
            "verified_backups": len([b for b in self.backups.values() if b.verified])
        }


class RecoveryManager:
    """Менеджер восстановления"""
    
    def __init__(self, orchestrator: BackupOrchestrator):
        self.orchestrator = orchestrator
        self.recovery_jobs: Dict[str, RecoveryJob] = {}
        
    async def restore_from_backup(self, backup_id: str,
                                   target_location: str,
                                   **kwargs) -> RecoveryJob:
        """Восстановление из бэкапа"""
        backup = self.orchestrator.backups.get(backup_id)
        if not backup:
            raise ValueError("Backup not found")
            
        job = RecoveryJob(
            recovery_id=f"recovery_{uuid.uuid4().hex[:8]}",
            backup_id=backup_id,
            target_location=target_location,
            **kwargs
        )
        
        self.recovery_jobs[job.recovery_id] = job
        
        job.status = RecoveryStatus.PREPARING
        job.started_at = datetime.now()
        
        try:
            # Симуляция восстановления
            job.status = RecoveryStatus.RESTORING
            
            total_bytes = backup.size_bytes
            chunk_size = total_bytes // 10
            
            for i in range(10):
                await asyncio.sleep(0.05)
                
                job.bytes_restored += chunk_size
                job.files_restored += backup.files_count // 10
                job.progress_percent = (i + 1) * 10
                
            job.status = RecoveryStatus.COMPLETED
            job.completed_at = datetime.now()
            
        except Exception as e:
            job.status = RecoveryStatus.FAILED
            job.error_message = str(e)
            
        return job
        
    async def restore_to_point_in_time(self, point_time: datetime,
                                        target_location: str) -> RecoveryJob:
        """Восстановление на момент времени"""
        # Поиск ближайшего recovery point
        points = self.orchestrator.get_recovery_points()
        
        closest_point = None
        for point in points:
            if point.timestamp <= point_time:
                closest_point = point
                break
                
        if not closest_point or not closest_point.backup_ids:
            raise ValueError("No recovery point found")
            
        return await self.restore_from_backup(
            closest_point.backup_ids[0],
            target_location
        )
        
    def get_recovery_status(self, recovery_id: str) -> Optional[Dict[str, Any]]:
        """Статус восстановления"""
        job = self.recovery_jobs.get(recovery_id)
        if not job:
            return None
            
        return {
            "recovery_id": recovery_id,
            "status": job.status.value,
            "progress_percent": job.progress_percent,
            "bytes_restored": job.bytes_restored,
            "files_restored": job.files_restored,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None
        }


class DisasterRecoveryManager:
    """Менеджер аварийного восстановления"""
    
    def __init__(self, orchestrator: BackupOrchestrator):
        self.orchestrator = orchestrator
        self.plans: Dict[str, DRPlan] = {}
        self.replication_targets: Dict[str, ReplicationTarget] = {}
        
    def create_dr_plan(self, name: str, primary_region: str,
                        dr_region: str, **kwargs) -> DRPlan:
        """Создание DR плана"""
        plan = DRPlan(
            plan_id=f"dr_{uuid.uuid4().hex[:8]}",
            name=name,
            primary_region=primary_region,
            dr_region=dr_region,
            **kwargs
        )
        
        self.plans[plan.plan_id] = plan
        return plan
        
    def add_replication_target(self, name: str, region: str,
                                 endpoint: str) -> ReplicationTarget:
        """Добавление цели репликации"""
        target = ReplicationTarget(
            target_id=f"repl_{uuid.uuid4().hex[:8]}",
            name=name,
            region=region,
            endpoint=endpoint
        )
        
        self.replication_targets[target.target_id] = target
        return target
        
    async def sync_replication(self, target_id: str) -> Dict[str, Any]:
        """Синхронизация репликации"""
        target = self.replication_targets.get(target_id)
        if not target:
            return {"error": "Target not found"}
            
        target.status = "syncing"
        
        # Симуляция синхронизации
        await asyncio.sleep(0.2)
        
        bytes_synced = random.randint(10000000, 100000000)
        
        target.bytes_replicated += bytes_synced
        target.last_sync = datetime.now()
        target.lag_seconds = random.randint(0, 30)
        target.status = "active"
        
        return {
            "target_id": target_id,
            "bytes_synced": bytes_synced,
            "lag_seconds": target.lag_seconds
        }
        
    async def test_dr_plan(self, plan_id: str) -> Dict[str, Any]:
        """Тестирование DR плана"""
        plan = self.plans.get(plan_id)
        if not plan:
            return {"error": "Plan not found"}
            
        results = {
            "plan_id": plan_id,
            "test_started_at": datetime.now().isoformat(),
            "steps": []
        }
        
        # Симуляция выполнения runbook
        for i, step in enumerate(plan.runbook_steps):
            await asyncio.sleep(0.1)
            
            step_result = {
                "step": i + 1,
                "name": step.get("name", "Unknown step"),
                "status": "success" if random.random() > 0.1 else "warning",
                "duration_seconds": round(random.uniform(1, 30), 2)
            }
            
            results["steps"].append(step_result)
            
        # Расчёт времени восстановления
        total_time = sum(s["duration_seconds"] for s in results["steps"])
        results["total_time_seconds"] = total_time
        results["rto_met"] = total_time < plan.rto_minutes * 60
        
        plan.last_test = datetime.now()
        plan.test_result = "passed" if results["rto_met"] else "failed"
        
        return results
        
    async def failover(self, plan_id: str) -> Dict[str, Any]:
        """Переключение на DR"""
        plan = self.plans.get(plan_id)
        if not plan:
            return {"error": "Plan not found"}
            
        plan.status = DRStatus.FAILOVER
        
        results = {
            "plan_id": plan_id,
            "failover_started_at": datetime.now().isoformat(),
            "steps": []
        }
        
        # Выполнение шагов failover
        steps = [
            "Stop traffic to primary",
            "Verify replication is current",
            "Promote DR to primary",
            "Update DNS records",
            "Verify services in DR region"
        ]
        
        for step in steps:
            await asyncio.sleep(0.1)
            
            results["steps"].append({
                "step": step,
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            })
            
        plan.last_failover = datetime.now()
        results["failover_completed_at"] = datetime.now().isoformat()
        
        return results
        
    async def failback(self, plan_id: str) -> Dict[str, Any]:
        """Возврат на основной регион"""
        plan = self.plans.get(plan_id)
        if not plan:
            return {"error": "Plan not found"}
            
        plan.status = DRStatus.FAILBACK
        
        # Симуляция failback
        await asyncio.sleep(0.3)
        
        plan.status = DRStatus.ACTIVE
        
        return {
            "plan_id": plan_id,
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }
        
    def get_dr_status(self) -> Dict[str, Any]:
        """Статус DR"""
        return {
            "plans": len(self.plans),
            "replication_targets": len(self.replication_targets),
            "active_targets": len([t for t in self.replication_targets.values() if t.status == "active"]),
            "plans_tested_recently": len([
                p for p in self.plans.values()
                if p.last_test and (datetime.now() - p.last_test).days < 30
            ]),
            "avg_lag_seconds": sum(t.lag_seconds for t in self.replication_targets.values()) / max(len(self.replication_targets), 1)
        }


class BackupDisasterRecoveryPlatform:
    """Платформа резервного копирования и DR"""
    
    def __init__(self):
        self.orchestrator = BackupOrchestrator()
        self.recovery_manager = RecoveryManager(self.orchestrator)
        self.dr_manager = DisasterRecoveryManager(self.orchestrator)
        
    def get_status(self) -> Dict[str, Any]:
        """Статус платформы"""
        return {
            "backup": self.orchestrator.get_statistics(),
            "dr": self.dr_manager.get_dr_status()
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 50: Backup & Disaster Recovery")
    print("=" * 60)
    
    async def demo():
        # Создание платформы
        platform = BackupDisasterRecoveryPlatform()
        print("✓ Backup & DR Platform created")
        
        # Регистрация целей
        print("\n📁 Registering backup targets...")
        
        db_target = platform.orchestrator.register_target(
            name="production-database",
            resource_type=ResourceType.DATABASE,
            source_path="/var/lib/postgresql/data"
        )
        print(f"  ✓ Registered: {db_target.name}")
        
        app_target = platform.orchestrator.register_target(
            name="application-data",
            resource_type=ResourceType.FILESYSTEM,
            source_path="/opt/application/data",
            include_patterns=["*.dat", "*.log"],
            exclude_patterns=["*.tmp"]
        )
        print(f"  ✓ Registered: {app_target.name}")
        
        config_target = platform.orchestrator.register_target(
            name="configuration-files",
            resource_type=ResourceType.FILESYSTEM,
            source_path="/etc/application"
        )
        print(f"  ✓ Registered: {config_target.name}")
        
        # Создание backup job
        print("\n📋 Creating backup jobs...")
        
        daily_job = platform.orchestrator.create_job(
            name="daily-full-backup",
            targets=[db_target.target_id, app_target.target_id, config_target.target_id],
            backup_type=BackupType.FULL,
            schedule_cron="0 2 * * *",
            retention_days=30,
            destination="s3://backups/daily",
            compression=True,
            encryption=True
        )
        print(f"  ✓ Created job: {daily_job.name}")
        
        hourly_job = platform.orchestrator.create_job(
            name="hourly-incremental",
            targets=[db_target.target_id],
            backup_type=BackupType.INCREMENTAL,
            schedule_cron="0 * * * *",
            retention_days=7,
            destination="s3://backups/hourly",
            compression=True
        )
        print(f"  ✓ Created job: {hourly_job.name}")
        
        # Запуск бэкапа
        print("\n💾 Running backups...")
        
        backup1 = await platform.orchestrator.run_backup(daily_job.job_id)
        print(f"  ✓ Backup completed: {backup1.backup_id}")
        print(f"    Size: {backup1.size_bytes / 1024 / 1024:.2f} MB")
        print(f"    Compressed: {backup1.compressed_size_bytes / 1024 / 1024:.2f} MB")
        print(f"    Files: {backup1.files_count}")
        print(f"    Duration: {backup1.duration_seconds:.2f}s")
        
        backup2 = await platform.orchestrator.run_backup(hourly_job.job_id)
        print(f"  ✓ Backup completed: {backup2.backup_id}")
        
        # Создание снимка
        print("\n📸 Creating snapshots...")
        
        snapshot = await platform.orchestrator.create_snapshot(
            resource_id="db-server-1",
            resource_type=ResourceType.DATABASE,
            description="Pre-migration snapshot"
        )
        print(f"  ✓ Snapshot created: {snapshot.snapshot_id}")
        print(f"    Size: {snapshot.size_bytes / 1024 / 1024:.2f} MB")
        
        # Верификация
        print("\n✅ Verifying backups...")
        
        verify_result = await platform.orchestrator.verify_backup(backup1.backup_id)
        print(f"  Verification: {'Passed' if verify_result['verified'] else 'Failed'}")
        
        # Recovery points
        print("\n📍 Recovery Points:")
        
        points = platform.orchestrator.get_recovery_points()
        print(f"  Available points: {len(points)}")
        
        for point in points[:3]:
            print(f"    - {point.timestamp.strftime('%Y-%m-%d %H:%M')} ({point.point_type})")
            
        # Восстановление
        print("\n🔄 Testing recovery...")
        
        recovery_job = await platform.recovery_manager.restore_from_backup(
            backup_id=backup1.backup_id,
            target_location="/restore/test"
        )
        print(f"  Recovery status: {recovery_job.status.value}")
        print(f"  Progress: {recovery_job.progress_percent}%")
        print(f"  Files restored: {recovery_job.files_restored}")
        
        # DR план
        print("\n🌍 Disaster Recovery...")
        
        dr_plan = platform.dr_manager.create_dr_plan(
            name="production-dr-plan",
            primary_region="us-east-1",
            dr_region="us-west-2",
            rto_minutes=30,
            rpo_minutes=5,
            protected_resources=[db_target.target_id, app_target.target_id],
            runbook_steps=[
                {"name": "Stop primary traffic", "type": "manual"},
                {"name": "Verify replication lag", "type": "automated"},
                {"name": "Promote DR database", "type": "automated"},
                {"name": "Update DNS records", "type": "automated"},
                {"name": "Verify application health", "type": "automated"}
            ]
        )
        print(f"  ✓ Created DR plan: {dr_plan.name}")
        print(f"    RTO: {dr_plan.rto_minutes} minutes")
        print(f"    RPO: {dr_plan.rpo_minutes} minutes")
        
        # Replication target
        repl_target = platform.dr_manager.add_replication_target(
            name="dr-region-target",
            region="us-west-2",
            endpoint="s3://dr-backups"
        )
        print(f"  ✓ Added replication target: {repl_target.name}")
        
        # Sync
        sync_result = await platform.dr_manager.sync_replication(repl_target.target_id)
        print(f"  ✓ Sync completed: {sync_result['bytes_synced'] / 1024 / 1024:.2f} MB")
        print(f"    Lag: {sync_result['lag_seconds']}s")
        
        # Тест DR плана
        print("\n🧪 Testing DR Plan...")
        
        test_result = await platform.dr_manager.test_dr_plan(dr_plan.plan_id)
        print(f"  Test completed in {test_result['total_time_seconds']:.2f}s")
        print(f"  RTO met: {test_result['rto_met']}")
        
        for step in test_result["steps"][:3]:
            print(f"    {step['step']}. {step['name']}: {step['status']}")
            
        # Итоговая статистика
        print("\n📊 Platform Statistics:")
        stats = platform.get_status()
        
        print(f"\n  Backup:")
        print(f"    Targets: {stats['backup']['targets']}")
        print(f"    Jobs: {stats['backup']['jobs']}")
        print(f"    Backups: {stats['backup']['backups']}")
        print(f"    Total size: {stats['backup']['total_size_gb']} GB")
        print(f"    Compression ratio: {stats['backup']['compression_ratio']}")
        
        print(f"\n  Disaster Recovery:")
        print(f"    Plans: {stats['dr']['plans']}")
        print(f"    Replication targets: {stats['dr']['replication_targets']}")
        print(f"    Average lag: {stats['dr']['avg_lag_seconds']:.1f}s")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Backup & Disaster Recovery Platform initialized!")
    print("=" * 60)
