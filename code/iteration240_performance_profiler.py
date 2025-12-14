#!/usr/bin/env python3
"""
Server Init - Iteration 240: Performance Profiler Platform
Платформа профилирования производительности

Функционал:
- CPU Profiling - профилирование CPU
- Memory Profiling - профилирование памяти
- Flame Graphs - flame графы
- Call Stack Analysis - анализ стека вызовов
- Hotspot Detection - обнаружение горячих точек
- Performance Baselines - базовые показатели
- Continuous Profiling - непрерывное профилирование
- Profile Comparison - сравнение профилей
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import json


class ProfileType(Enum):
    """Тип профиля"""
    CPU = "cpu"
    MEMORY = "memory"
    HEAP = "heap"
    GOROUTINE = "goroutine"
    BLOCK = "block"
    MUTEX = "mutex"
    ALLOCATION = "allocation"


class ProfileStatus(Enum):
    """Статус профиля"""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class StackFrame:
    """Кадр стека"""
    frame_id: str
    function_name: str = ""
    file_name: str = ""
    line_number: int = 0
    
    # Module/Package
    module: str = ""
    
    # Self and total time/samples
    self_samples: int = 0
    total_samples: int = 0
    
    # Percentage
    self_percent: float = 0.0
    total_percent: float = 0.0


@dataclass
class CallNode:
    """Узел графа вызовов"""
    node_id: str
    function_name: str = ""
    
    # Metrics
    samples: int = 0
    percent: float = 0.0
    
    # Children
    children: List[str] = field(default_factory=list)  # node_ids
    
    # Parent
    parent_id: str = ""


@dataclass
class Hotspot:
    """Горячая точка"""
    hotspot_id: str
    function_name: str = ""
    file_name: str = ""
    
    # Metrics
    samples: int = 0
    percent: float = 0.0
    
    # Type
    hotspot_type: str = "cpu"  # cpu, memory, gc
    
    # Optimization hint
    hint: str = ""


@dataclass
class Profile:
    """Профиль"""
    profile_id: str
    name: str = ""
    
    # Type
    profile_type: ProfileType = ProfileType.CPU
    
    # Target
    service: str = ""
    instance: str = ""
    
    # Duration
    duration_seconds: int = 60
    sample_rate: int = 100  # samples per second
    
    # Status
    status: ProfileStatus = ProfileStatus.RUNNING
    
    # Results
    total_samples: int = 0
    stack_frames: List[StackFrame] = field(default_factory=list)
    hotspots: List[Hotspot] = field(default_factory=list)
    
    # Times
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    # Metadata
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class MemorySnapshot:
    """Снимок памяти"""
    snapshot_id: str
    profile_id: str = ""
    
    # Memory stats
    heap_alloc_bytes: int = 0
    heap_objects: int = 0
    stack_inuse_bytes: int = 0
    gc_cycles: int = 0
    
    # Top allocators
    top_allocators: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Baseline:
    """Базовая линия производительности"""
    baseline_id: str
    name: str = ""
    
    # Service
    service: str = ""
    
    # Metrics
    avg_cpu_percent: float = 0.0
    avg_memory_mb: float = 0.0
    p50_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    
    # Top functions
    top_functions: List[str] = field(default_factory=list)
    
    # Created
    created_at: datetime = field(default_factory=datetime.now)
    
    # Version
    version: str = ""


@dataclass
class Comparison:
    """Сравнение профилей"""
    comparison_id: str
    
    # Profiles
    base_profile_id: str = ""
    compare_profile_id: str = ""
    
    # Differences
    cpu_diff_percent: float = 0.0
    memory_diff_percent: float = 0.0
    
    # New hotspots
    new_hotspots: List[str] = field(default_factory=list)
    
    # Resolved hotspots
    resolved_hotspots: List[str] = field(default_factory=list)
    
    # Regressions
    regressions: List[Dict[str, Any]] = field(default_factory=list)


class FlameGraphGenerator:
    """Генератор flame графов"""
    
    def __init__(self):
        self.sample_functions = [
            ("main", "main.go", 1),
            ("http.Handler", "net/http/server.go", 100),
            ("json.Marshal", "encoding/json/encode.go", 200),
            ("db.Query", "database/sql/sql.go", 150),
            ("cache.Get", "cache/cache.go", 50),
            ("auth.Validate", "auth/validator.go", 75),
            ("log.Info", "log/logger.go", 30),
            ("template.Execute", "html/template/template.go", 120),
            ("compress.Gzip", "compress/gzip/gzip.go", 90),
            ("crypto.Hash", "crypto/sha256/sha256.go", 60),
        ]
        
    def generate_stack_frames(self, total_samples: int) -> List[StackFrame]:
        """Генерация стек фреймов"""
        frames = []
        remaining_samples = total_samples
        
        for func, file, base_samples in self.sample_functions:
            if remaining_samples <= 0:
                break
                
            samples = min(
                random.randint(base_samples, base_samples * 3),
                remaining_samples
            )
            
            frame = StackFrame(
                frame_id=f"frame_{uuid.uuid4().hex[:8]}",
                function_name=func,
                file_name=file,
                line_number=random.randint(10, 500),
                module=file.split("/")[0] if "/" in file else "main",
                self_samples=samples,
                total_samples=samples + random.randint(0, samples // 2),
                self_percent=(samples / total_samples * 100) if total_samples > 0 else 0,
                total_percent=((samples + random.randint(0, samples // 2)) / total_samples * 100) if total_samples > 0 else 0
            )
            
            frames.append(frame)
            remaining_samples -= samples
            
        return sorted(frames, key=lambda f: -f.self_samples)
        
    def generate_hotspots(self, frames: List[StackFrame]) -> List[Hotspot]:
        """Генерация горячих точек"""
        hotspots = []
        
        # Top 5 frames as hotspots
        for frame in frames[:5]:
            hints = [
                "Consider caching this result",
                "Optimize algorithm complexity",
                "Use connection pooling",
                "Reduce allocations",
                "Consider async processing"
            ]
            
            hotspot = Hotspot(
                hotspot_id=f"hot_{uuid.uuid4().hex[:8]}",
                function_name=frame.function_name,
                file_name=frame.file_name,
                samples=frame.self_samples,
                percent=frame.self_percent,
                hint=random.choice(hints)
            )
            
            hotspots.append(hotspot)
            
        return hotspots


class PerformanceProfilerPlatform:
    """Платформа профилирования производительности"""
    
    def __init__(self):
        self.profiles: Dict[str, Profile] = {}
        self.snapshots: List[MemorySnapshot] = []
        self.baselines: Dict[str, Baseline] = {}
        self.comparisons: List[Comparison] = []
        self.flame_generator = FlameGraphGenerator()
        
    def start_profile(self, name: str, service: str,
                     profile_type: ProfileType = ProfileType.CPU,
                     duration_seconds: int = 60,
                     sample_rate: int = 100) -> Profile:
        """Запуск профилирования"""
        profile = Profile(
            profile_id=f"prof_{uuid.uuid4().hex[:8]}",
            name=name,
            profile_type=profile_type,
            service=service,
            instance=f"{service}-{random.randint(1, 5)}",
            duration_seconds=duration_seconds,
            sample_rate=sample_rate
        )
        
        self.profiles[profile.profile_id] = profile
        return profile
        
    def complete_profile(self, profile_id: str) -> Optional[Profile]:
        """Завершение профилирования"""
        profile = self.profiles.get(profile_id)
        if not profile:
            return None
            
        # Generate samples
        profile.total_samples = profile.duration_seconds * profile.sample_rate
        
        # Generate stack frames
        profile.stack_frames = self.flame_generator.generate_stack_frames(
            profile.total_samples
        )
        
        # Generate hotspots
        profile.hotspots = self.flame_generator.generate_hotspots(
            profile.stack_frames
        )
        
        profile.status = ProfileStatus.COMPLETED
        profile.completed_at = datetime.now()
        
        return profile
        
    def take_memory_snapshot(self, profile_id: str) -> MemorySnapshot:
        """Снимок памяти"""
        snapshot = MemorySnapshot(
            snapshot_id=f"snap_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            heap_alloc_bytes=random.randint(100000000, 500000000),
            heap_objects=random.randint(100000, 500000),
            stack_inuse_bytes=random.randint(1000000, 10000000),
            gc_cycles=random.randint(10, 100)
        )
        
        # Top allocators
        allocators = [
            ("[]byte", random.randint(10000000, 50000000)),
            ("string", random.randint(5000000, 20000000)),
            ("map[string]interface{}", random.randint(1000000, 10000000)),
            ("*http.Request", random.randint(500000, 5000000)),
            ("json.RawMessage", random.randint(100000, 1000000)),
        ]
        
        snapshot.top_allocators = [
            {"type": t, "bytes": b, "percent": b / snapshot.heap_alloc_bytes * 100}
            for t, b in allocators
        ]
        
        self.snapshots.append(snapshot)
        return snapshot
        
    def create_baseline(self, name: str, service: str,
                       profile_id: str = None) -> Baseline:
        """Создание базовой линии"""
        baseline = Baseline(
            baseline_id=f"base_{uuid.uuid4().hex[:8]}",
            name=name,
            service=service,
            avg_cpu_percent=random.uniform(20, 60),
            avg_memory_mb=random.uniform(256, 1024),
            p50_latency_ms=random.uniform(5, 50),
            p99_latency_ms=random.uniform(50, 500)
        )
        
        if profile_id:
            profile = self.profiles.get(profile_id)
            if profile:
                baseline.top_functions = [
                    f.function_name for f in profile.stack_frames[:5]
                ]
                
        self.baselines[baseline.baseline_id] = baseline
        return baseline
        
    def compare_profiles(self, base_id: str, compare_id: str) -> Optional[Comparison]:
        """Сравнение профилей"""
        base = self.profiles.get(base_id)
        compare = self.profiles.get(compare_id)
        
        if not base or not compare:
            return None
            
        comparison = Comparison(
            comparison_id=f"cmp_{uuid.uuid4().hex[:8]}",
            base_profile_id=base_id,
            compare_profile_id=compare_id,
            cpu_diff_percent=random.uniform(-20, 30),
            memory_diff_percent=random.uniform(-10, 25)
        )
        
        # Find new hotspots
        base_functions = {f.function_name for f in base.stack_frames[:10]}
        compare_functions = {f.function_name for f in compare.stack_frames[:10]}
        
        comparison.new_hotspots = list(compare_functions - base_functions)
        comparison.resolved_hotspots = list(base_functions - compare_functions)
        
        # Check for regressions
        if comparison.cpu_diff_percent > 10:
            comparison.regressions.append({
                "type": "cpu",
                "change": f"+{comparison.cpu_diff_percent:.1f}%",
                "severity": "high" if comparison.cpu_diff_percent > 20 else "medium"
            })
            
        if comparison.memory_diff_percent > 15:
            comparison.regressions.append({
                "type": "memory",
                "change": f"+{comparison.memory_diff_percent:.1f}%",
                "severity": "high" if comparison.memory_diff_percent > 25 else "medium"
            })
            
        self.comparisons.append(comparison)
        return comparison
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        profiles = list(self.profiles.values())
        completed = [p for p in profiles if p.status == ProfileStatus.COMPLETED]
        
        # By type
        by_type = {}
        for p in profiles:
            t = p.profile_type.value
            by_type[t] = by_type.get(t, 0) + 1
            
        # Total samples
        total_samples = sum(p.total_samples for p in completed)
        
        # Total hotspots
        total_hotspots = sum(len(p.hotspots) for p in completed)
        
        return {
            "total_profiles": len(profiles),
            "completed_profiles": len(completed),
            "total_samples": total_samples,
            "total_hotspots": total_hotspots,
            "memory_snapshots": len(self.snapshots),
            "baselines": len(self.baselines),
            "comparisons": len(self.comparisons),
            "profiles_by_type": by_type
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 240: Performance Profiler Platform")
    print("=" * 60)
    
    platform = PerformanceProfilerPlatform()
    print("✓ Performance Profiler Platform created")
    
    # Start profiles
    print("\n📊 Starting Performance Profiles...")
    
    profiles_config = [
        ("API Service CPU", "api-service", ProfileType.CPU, 60),
        ("API Service Memory", "api-service", ProfileType.MEMORY, 30),
        ("Worker CPU", "worker-service", ProfileType.CPU, 60),
        ("Gateway Heap", "api-gateway", ProfileType.HEAP, 45),
        ("Auth Service", "auth-service", ProfileType.CPU, 60),
    ]
    
    profiles = []
    for name, service, ptype, duration in profiles_config:
        profile = platform.start_profile(name, service, ptype, duration)
        profiles.append(profile)
        
        type_icons = {
            ProfileType.CPU: "🔥",
            ProfileType.MEMORY: "💾",
            ProfileType.HEAP: "📊",
            ProfileType.GOROUTINE: "🔄",
            ProfileType.ALLOCATION: "📦"
        }
        icon = type_icons.get(ptype, "📊")
        print(f"  {icon} {name} ({service}, {duration}s)")
        
    # Complete profiles
    print("\n⏱️ Completing Profiles...")
    
    for profile in profiles:
        completed = platform.complete_profile(profile.profile_id)
        if completed:
            print(f"  ✓ {completed.name}: {completed.total_samples} samples")
            
    # Take memory snapshots
    print("\n📸 Taking Memory Snapshots...")
    
    for profile in profiles[:2]:
        snapshot = platform.take_memory_snapshot(profile.profile_id)
        heap_mb = snapshot.heap_alloc_bytes / (1024**2)
        print(f"  📸 {profile.name}: {heap_mb:.1f} MB heap, {snapshot.heap_objects} objects")
        
    # Create baselines
    print("\n📏 Creating Performance Baselines...")
    
    baselines = [
        platform.create_baseline("API Service v2.0", "api-service", profiles[0].profile_id),
        platform.create_baseline("Worker Service v1.5", "worker-service", profiles[2].profile_id),
    ]
    
    for baseline in baselines:
        print(f"  📏 {baseline.name}: CPU={baseline.avg_cpu_percent:.1f}%, Mem={baseline.avg_memory_mb:.0f}MB")
        
    # Compare profiles
    print("\n🔄 Comparing Profiles...")
    
    comparison = platform.compare_profiles(profiles[0].profile_id, profiles[2].profile_id)
    if comparison:
        cpu_symbol = "📈" if comparison.cpu_diff_percent > 0 else "📉"
        mem_symbol = "📈" if comparison.memory_diff_percent > 0 else "📉"
        print(f"  {cpu_symbol} CPU: {comparison.cpu_diff_percent:+.1f}%")
        print(f"  {mem_symbol} Memory: {comparison.memory_diff_percent:+.1f}%")
        
        if comparison.regressions:
            print("  ⚠️ Regressions detected!")
            
    # Display profiles
    print("\n📊 Performance Profiles:")
    
    print("\n  ┌────────────────────────────────┬──────────────┬──────────┬──────────┐")
    print("  │ Profile                        │ Type         │ Samples  │ Status   │")
    print("  ├────────────────────────────────┼──────────────┼──────────┼──────────┤")
    
    for profile in platform.profiles.values():
        name = profile.name[:30].ljust(30)
        ptype = profile.profile_type.value[:12].ljust(12)
        samples = str(profile.total_samples)[:8].ljust(8)
        
        status_icons = {
            ProfileStatus.COMPLETED: "🟢",
            ProfileStatus.RUNNING: "🔵",
            ProfileStatus.FAILED: "🔴",
            ProfileStatus.CANCELLED: "⚫"
        }
        status = status_icons.get(profile.status, "⚪")[:8].ljust(8)
        
        print(f"  │ {name} │ {ptype} │ {samples} │ {status} │")
        
    print("  └────────────────────────────────┴──────────────┴──────────┴──────────┘")
    
    # Display hotspots
    print("\n🔥 Top Hotspots:")
    
    sample_profile = profiles[0]
    
    print("\n  ┌────────────────────────────────┬──────────┬──────────┐")
    print("  │ Function                       │ Samples  │ Percent  │")
    print("  ├────────────────────────────────┼──────────┼──────────┤")
    
    for hotspot in sample_profile.hotspots[:5]:
        func = hotspot.function_name[:30].ljust(30)
        samples = str(hotspot.samples)[:8].ljust(8)
        pct = f"{hotspot.percent:.1f}%"[:8].ljust(8)
        
        print(f"  │ {func} │ {samples} │ {pct} │")
        
    print("  └────────────────────────────────┴──────────┴──────────┘")
    
    # Flame graph visualization (simplified)
    print("\n🔥 Flame Graph (simplified):")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────┐")
    for frame in sample_profile.stack_frames[:5]:
        bar_len = int(frame.self_percent / 2)
        bar = "█" * bar_len
        
        func = frame.function_name[:15].ljust(15)
        print(f"  │ {func} {bar}")
        
    print("  └─────────────────────────────────────────────────────────────────┘")
    
    # Memory analysis
    print("\n💾 Memory Analysis:")
    
    for snapshot in platform.snapshots[:2]:
        print(f"\n  Snapshot: {snapshot.snapshot_id}")
        print(f"  Heap Alloc: {snapshot.heap_alloc_bytes / (1024**2):.1f} MB")
        print(f"  Heap Objects: {snapshot.heap_objects:,}")
        print(f"  GC Cycles: {snapshot.gc_cycles}")
        
        print("  Top Allocators:")
        for alloc in snapshot.top_allocators[:3]:
            mb = alloc["bytes"] / (1024**2)
            print(f"    {alloc['type']}: {mb:.1f} MB ({alloc['percent']:.1f}%)")
            
    # Optimization hints
    print("\n💡 Optimization Hints:")
    
    for hotspot in sample_profile.hotspots[:3]:
        print(f"  ⚡ {hotspot.function_name}")
        print(f"     {hotspot.hint}")
        
    # Profile comparison
    if comparison:
        print("\n📈 Profile Comparison:")
        
        print(f"\n  Base: {profiles[0].name}")
        print(f"  Compare: {profiles[2].name}")
        print(f"\n  CPU Difference: {comparison.cpu_diff_percent:+.1f}%")
        print(f"  Memory Difference: {comparison.memory_diff_percent:+.1f}%")
        
        if comparison.new_hotspots:
            print(f"\n  New Hotspots: {', '.join(comparison.new_hotspots[:3])}")
            
        if comparison.resolved_hotspots:
            print(f"  Resolved Hotspots: {', '.join(comparison.resolved_hotspots[:3])}")
            
    # Baselines
    print("\n📏 Performance Baselines:")
    
    for baseline in platform.baselines.values():
        print(f"\n  {baseline.name}:")
        print(f"    CPU: {baseline.avg_cpu_percent:.1f}%")
        print(f"    Memory: {baseline.avg_memory_mb:.0f} MB")
        print(f"    P50 Latency: {baseline.p50_latency_ms:.1f} ms")
        print(f"    P99 Latency: {baseline.p99_latency_ms:.1f} ms")
        
    # Statistics
    print("\n📊 Platform Statistics:")
    
    stats = platform.get_statistics()
    
    print(f"\n  Total Profiles: {stats['total_profiles']}")
    print(f"  Completed: {stats['completed_profiles']}")
    print(f"  Total Samples: {stats['total_samples']:,}")
    print(f"  Total Hotspots: {stats['total_hotspots']}")
    print(f"  Memory Snapshots: {stats['memory_snapshots']}")
    print(f"  Baselines: {stats['baselines']}")
    
    # Profile type distribution
    print("\n  By Profile Type:")
    type_icons = {"cpu": "🔥", "memory": "💾", "heap": "📊", "goroutine": "🔄", "allocation": "📦"}
    for ptype, count in stats['profiles_by_type'].items():
        icon = type_icons.get(ptype, "📊")
        bar = "█" * (count * 2) + "░" * (10 - count * 2)
        print(f"    {icon} {ptype:12s} [{bar}] {count}")
        
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                  Performance Profiler Dashboard                     │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Profiles:                {stats['total_profiles']:>12}                        │")
    print(f"│ Total Samples:                {stats['total_samples']:>13,}                       │")
    print(f"│ Hotspots Detected:             {stats['total_hotspots']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Memory Snapshots:              {stats['memory_snapshots']:>12}                        │")
    print(f"│ Performance Baselines:         {stats['baselines']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Performance Profiler Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
