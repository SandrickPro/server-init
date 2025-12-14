#!/usr/bin/env python3
"""
Server Init - Iteration 286: Cache Manager Platform
Платформа Cache Manager

Функционал:
- Multi-tier Caching - многоуровневое кэширование
- Cache Policies - политики кэширования
- TTL Management - управление временем жизни
- Eviction Strategies - стратегии вытеснения
- Cache Invalidation - инвалидация кэша
- Distributed Cache - распределённый кэш
- Cache Statistics - статистика кэша
- Write-through/Write-back - режимы записи
"""

import asyncio
import random
import time
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid
from collections import OrderedDict


class CacheLevel(Enum):
    """Уровень кэша"""
    L1 = "l1"  # In-process memory
    L2 = "l2"  # Distributed cache (Redis)
    L3 = "l3"  # Persistent (Disk/DB)


class EvictionPolicy(Enum):
    """Политика вытеснения"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"  # Time To Live
    RANDOM = "random"


class WritePolicy(Enum):
    """Политика записи"""
    WRITE_THROUGH = "write_through"  # Write to cache and storage
    WRITE_BACK = "write_back"  # Write to cache, async to storage
    WRITE_AROUND = "write_around"  # Write to storage only


class CacheState(Enum):
    """Состояние кэша"""
    VALID = "valid"
    STALE = "stale"
    EXPIRED = "expired"
    INVALID = "invalid"


@dataclass
class CacheEntry:
    """Запись кэша"""
    key: str
    value: Any
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    # TTL
    ttl_seconds: int = 0
    
    # Stats
    hit_count: int = 0
    size_bytes: int = 0
    
    # State
    state: CacheState = CacheState.VALID
    
    # Version
    version: int = 1
    
    # Tags
    tags: List[str] = field(default_factory=list)


@dataclass
class CacheConfig:
    """Конфигурация кэша"""
    name: str
    level: CacheLevel
    
    # Capacity
    max_entries: int = 10000
    max_bytes: int = 0  # 0 = unlimited
    
    # TTL
    default_ttl_seconds: int = 300
    max_ttl_seconds: int = 86400
    
    # Eviction
    eviction_policy: EvictionPolicy = EvictionPolicy.LRU
    
    # Write
    write_policy: WritePolicy = WritePolicy.WRITE_THROUGH


@dataclass
class CacheStats:
    """Статистика кэша"""
    hits: int = 0
    misses: int = 0
    writes: int = 0
    evictions: int = 0
    invalidations: int = 0
    
    # Bytes
    bytes_read: int = 0
    bytes_written: int = 0
    
    # Latency
    avg_read_latency_ms: float = 0
    avg_write_latency_ms: float = 0
    
    # Time
    started_at: datetime = field(default_factory=datetime.now)


class CacheStore:
    """Хранилище кэша"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.entries: OrderedDict[str, CacheEntry] = OrderedDict()
        self.stats = CacheStats()
        
        # LFU tracking
        self.frequency: Dict[str, int] = {}
        
        # Size tracking
        self.current_bytes: int = 0
        
    async def get(self, key: str) -> Optional[CacheEntry]:
        """Получение записи"""
        start = time.time()
        
        if key not in self.entries:
            self.stats.misses += 1
            return None
            
        entry = self.entries[key]
        
        # Check expiration
        if entry.expires_at and entry.expires_at < datetime.now():
            entry.state = CacheState.EXPIRED
            self.stats.misses += 1
            del self.entries[key]
            return None
            
        # Update access
        entry.accessed_at = datetime.now()
        entry.hit_count += 1
        
        # Update LRU order
        if self.config.eviction_policy == EvictionPolicy.LRU:
            self.entries.move_to_end(key)
            
        # Update LFU
        if self.config.eviction_policy == EvictionPolicy.LFU:
            self.frequency[key] = self.frequency.get(key, 0) + 1
            
        self.stats.hits += 1
        self.stats.bytes_read += entry.size_bytes
        
        # Update latency
        latency = (time.time() - start) * 1000
        self._update_read_latency(latency)
        
        return entry
        
    async def set(self, key: str, value: Any,
                 ttl_seconds: int = 0,
                 tags: List[str] = None) -> CacheEntry:
        """Установка записи"""
        start = time.time()
        
        size = len(str(value))
        
        # Check capacity
        while self._needs_eviction(size):
            await self._evict()
            
        # Calculate TTL
        effective_ttl = ttl_seconds or self.config.default_ttl_seconds
        if effective_ttl > self.config.max_ttl_seconds:
            effective_ttl = self.config.max_ttl_seconds
            
        expires_at = datetime.now() + timedelta(seconds=effective_ttl) if effective_ttl > 0 else None
        
        # Create or update entry
        if key in self.entries:
            entry = self.entries[key]
            entry.value = value
            entry.updated_at = datetime.now()
            entry.expires_at = expires_at
            entry.version += 1
            entry.state = CacheState.VALID
            
            self.current_bytes -= entry.size_bytes
            entry.size_bytes = size
            self.current_bytes += size
        else:
            entry = CacheEntry(
                key=key,
                value=value,
                ttl_seconds=effective_ttl,
                expires_at=expires_at,
                size_bytes=size,
                tags=tags or []
            )
            self.entries[key] = entry
            self.current_bytes += size
            
        self.stats.writes += 1
        self.stats.bytes_written += size
        
        # Update latency
        latency = (time.time() - start) * 1000
        self._update_write_latency(latency)
        
        return entry
        
    async def delete(self, key: str) -> bool:
        """Удаление записи"""
        if key not in self.entries:
            return False
            
        entry = self.entries[key]
        self.current_bytes -= entry.size_bytes
        del self.entries[key]
        
        if key in self.frequency:
            del self.frequency[key]
            
        self.stats.invalidations += 1
        return True
        
    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Инвалидация по тегам"""
        count = 0
        keys_to_delete = []
        
        for key, entry in self.entries.items():
            if any(tag in entry.tags for tag in tags):
                keys_to_delete.append(key)
                
        for key in keys_to_delete:
            await self.delete(key)
            count += 1
            
        return count
        
    async def invalidate_pattern(self, pattern: str) -> int:
        """Инвалидация по паттерну"""
        count = 0
        keys_to_delete = []
        
        for key in self.entries:
            if self._match_pattern(pattern, key):
                keys_to_delete.append(key)
                
        for key in keys_to_delete:
            await self.delete(key)
            count += 1
            
        return count
        
    def _match_pattern(self, pattern: str, key: str) -> bool:
        """Сопоставление паттерна"""
        import fnmatch
        return fnmatch.fnmatch(key, pattern)
        
    def _needs_eviction(self, new_size: int) -> bool:
        """Проверка необходимости вытеснения"""
        if self.config.max_entries > 0 and len(self.entries) >= self.config.max_entries:
            return True
            
        if self.config.max_bytes > 0 and self.current_bytes + new_size > self.config.max_bytes:
            return True
            
        return False
        
    async def _evict(self):
        """Вытеснение записи"""
        if not self.entries:
            return
            
        key_to_evict = None
        
        if self.config.eviction_policy == EvictionPolicy.LRU:
            # Remove oldest (first in OrderedDict)
            key_to_evict = next(iter(self.entries))
            
        elif self.config.eviction_policy == EvictionPolicy.LFU:
            # Remove least frequently used
            min_freq = min(self.frequency.values()) if self.frequency else 0
            for key, freq in self.frequency.items():
                if freq == min_freq:
                    key_to_evict = key
                    break
                    
        elif self.config.eviction_policy == EvictionPolicy.FIFO:
            key_to_evict = next(iter(self.entries))
            
        elif self.config.eviction_policy == EvictionPolicy.TTL:
            # Remove entry closest to expiration
            min_expires = None
            for key, entry in self.entries.items():
                if entry.expires_at:
                    if min_expires is None or entry.expires_at < min_expires:
                        min_expires = entry.expires_at
                        key_to_evict = key
            if not key_to_evict:
                key_to_evict = next(iter(self.entries))
                
        elif self.config.eviction_policy == EvictionPolicy.RANDOM:
            key_to_evict = random.choice(list(self.entries.keys()))
            
        if key_to_evict:
            entry = self.entries[key_to_evict]
            self.current_bytes -= entry.size_bytes
            del self.entries[key_to_evict]
            
            if key_to_evict in self.frequency:
                del self.frequency[key_to_evict]
                
            self.stats.evictions += 1
            
    def _update_read_latency(self, latency: float):
        """Обновление latency чтения"""
        total_reads = self.stats.hits + self.stats.misses
        self.stats.avg_read_latency_ms = (
            (self.stats.avg_read_latency_ms * (total_reads - 1) + latency) / total_reads
        )
        
    def _update_write_latency(self, latency: float):
        """Обновление latency записи"""
        self.stats.avg_write_latency_ms = (
            (self.stats.avg_write_latency_ms * (self.stats.writes - 1) + latency) / self.stats.writes
        )
        
    async def cleanup_expired(self) -> int:
        """Очистка истёкших записей"""
        now = datetime.now()
        keys_to_delete = []
        
        for key, entry in self.entries.items():
            if entry.expires_at and entry.expires_at < now:
                keys_to_delete.append(key)
                
        for key in keys_to_delete:
            await self.delete(key)
            
        return len(keys_to_delete)
        
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики"""
        total_requests = self.stats.hits + self.stats.misses
        hit_rate = self.stats.hits / max(total_requests, 1) * 100
        
        return {
            "entries": len(self.entries),
            "bytes": self.current_bytes,
            "hits": self.stats.hits,
            "misses": self.stats.misses,
            "hit_rate": hit_rate,
            "writes": self.stats.writes,
            "evictions": self.stats.evictions,
            "invalidations": self.stats.invalidations,
            "avg_read_latency_ms": self.stats.avg_read_latency_ms,
            "avg_write_latency_ms": self.stats.avg_write_latency_ms
        }


class CacheManager:
    """Менеджер многоуровневого кэша"""
    
    def __init__(self):
        self.stores: Dict[CacheLevel, CacheStore] = {}
        self.key_locations: Dict[str, List[CacheLevel]] = {}
        
        # Write-back queue
        self.write_back_queue: List[CacheEntry] = []
        
        # Origin loader
        self.origin_loader: Optional[Callable] = None
        
    def add_cache_level(self, config: CacheConfig) -> CacheStore:
        """Добавление уровня кэша"""
        store = CacheStore(config)
        self.stores[config.level] = store
        return store
        
    def set_origin_loader(self, loader: Callable):
        """Установка загрузчика из origin"""
        self.origin_loader = loader
        
    async def get(self, key: str,
                 load_from_origin: bool = True) -> Optional[Any]:
        """Получение значения"""
        # Check each level
        for level in sorted(self.stores.keys(), key=lambda x: x.value):
            store = self.stores[level]
            entry = await store.get(key)
            
            if entry:
                # Populate upper levels
                await self._populate_upper_levels(key, entry, level)
                return entry.value
                
        # Load from origin
        if load_from_origin and self.origin_loader:
            value = await self.origin_loader(key)
            if value is not None:
                await self.set(key, value)
                return value
                
        return None
        
    async def set(self, key: str, value: Any,
                 ttl_seconds: int = 0,
                 tags: List[str] = None,
                 write_policy: WritePolicy = None) -> bool:
        """Установка значения"""
        success = True
        
        for level, store in self.stores.items():
            policy = write_policy or store.config.write_policy
            
            if policy == WritePolicy.WRITE_THROUGH:
                entry = await store.set(key, value, ttl_seconds, tags)
                if not entry:
                    success = False
                    
            elif policy == WritePolicy.WRITE_BACK:
                # Write to L1 only, queue for others
                if level == CacheLevel.L1:
                    entry = await store.set(key, value, ttl_seconds, tags)
                    if entry:
                        self.write_back_queue.append(entry)
                        
            elif policy == WritePolicy.WRITE_AROUND:
                # Write to storage only (L3)
                if level == CacheLevel.L3:
                    await store.set(key, value, ttl_seconds, tags)
                    
        # Track key location
        self.key_locations[key] = list(self.stores.keys())
        
        return success
        
    async def delete(self, key: str) -> bool:
        """Удаление значения"""
        deleted = False
        
        for store in self.stores.values():
            if await store.delete(key):
                deleted = True
                
        if key in self.key_locations:
            del self.key_locations[key]
            
        return deleted
        
    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Инвалидация по тегам"""
        total = 0
        
        for store in self.stores.values():
            count = await store.invalidate_by_tags(tags)
            total += count
            
        return total
        
    async def invalidate_pattern(self, pattern: str) -> int:
        """Инвалидация по паттерну"""
        total = 0
        
        for store in self.stores.values():
            count = await store.invalidate_pattern(pattern)
            total += count
            
        return total
        
    async def _populate_upper_levels(self, key: str,
                                    entry: CacheEntry,
                                    found_level: CacheLevel):
        """Заполнение верхних уровней"""
        for level in sorted(self.stores.keys(), key=lambda x: x.value):
            if level.value >= found_level.value:
                break
                
            store = self.stores[level]
            await store.set(key, entry.value, entry.ttl_seconds, entry.tags)
            
    async def flush_write_back(self):
        """Сброс write-back очереди"""
        for entry in self.write_back_queue:
            for level, store in self.stores.items():
                if level != CacheLevel.L1:
                    await store.set(entry.key, entry.value, entry.ttl_seconds, entry.tags)
                    
        self.write_back_queue.clear()
        
    async def cleanup_all(self) -> int:
        """Очистка истёкших во всех уровнях"""
        total = 0
        
        for store in self.stores.values():
            count = await store.cleanup_expired()
            total += count
            
        return total
        
    async def warm_up(self, keys: List[str]):
        """Прогрев кэша"""
        if not self.origin_loader:
            return
            
        for key in keys:
            await self.get(key, load_from_origin=True)
            
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        stats = {}
        total_hits = 0
        total_misses = 0
        
        for level, store in self.stores.items():
            level_stats = store.get_stats()
            stats[level.value] = level_stats
            total_hits += level_stats["hits"]
            total_misses += level_stats["misses"]
            
        stats["total"] = {
            "hits": total_hits,
            "misses": total_misses,
            "hit_rate": total_hits / max(total_hits + total_misses, 1) * 100,
            "write_back_pending": len(self.write_back_queue)
        }
        
        return stats


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 286: Cache Manager Platform")
    print("=" * 60)
    
    manager = CacheManager()
    print("✓ Cache Manager created")
    
    # Configure cache levels
    print("\n📦 Configuring Cache Levels...")
    
    # L1 - In-memory (fast, small)
    l1_config = CacheConfig(
        name="L1-Memory",
        level=CacheLevel.L1,
        max_entries=1000,
        max_bytes=10 * 1024 * 1024,  # 10MB
        default_ttl_seconds=60,
        eviction_policy=EvictionPolicy.LRU,
        write_policy=WritePolicy.WRITE_THROUGH
    )
    manager.add_cache_level(l1_config)
    print(f"  📦 L1 Memory: {l1_config.max_entries} entries, {l1_config.max_bytes // 1024 // 1024}MB")
    
    # L2 - Distributed (Redis-like)
    l2_config = CacheConfig(
        name="L2-Distributed",
        level=CacheLevel.L2,
        max_entries=100000,
        max_bytes=1024 * 1024 * 1024,  # 1GB
        default_ttl_seconds=300,
        eviction_policy=EvictionPolicy.LFU,
        write_policy=WritePolicy.WRITE_THROUGH
    )
    manager.add_cache_level(l2_config)
    print(f"  📦 L2 Distributed: {l2_config.max_entries} entries, {l2_config.max_bytes // 1024 // 1024}MB")
    
    # L3 - Persistent (Disk)
    l3_config = CacheConfig(
        name="L3-Persistent",
        level=CacheLevel.L3,
        max_entries=1000000,
        default_ttl_seconds=86400,
        eviction_policy=EvictionPolicy.TTL,
        write_policy=WritePolicy.WRITE_BACK
    )
    manager.add_cache_level(l3_config)
    print(f"  📦 L3 Persistent: {l3_config.max_entries} entries, 24h TTL")
    
    # Set origin loader
    async def load_from_origin(key: str):
        # Simulate database lookup
        await asyncio.sleep(0.05)
        return {"key": key, "data": f"origin_data_{key}", "loaded_at": datetime.now().isoformat()}
        
    manager.set_origin_loader(load_from_origin)
    print("\n✓ Origin loader configured")
    
    # Cache operations
    print("\n💾 Cache Operations...")
    
    # Set values
    for i in range(20):
        await manager.set(
            f"user:{i}",
            {"id": i, "name": f"User {i}", "email": f"user{i}@example.com"},
            ttl_seconds=120,
            tags=["users", f"tier_{i % 3}"]
        )
        
    print("  ✓ Cached 20 user records")
    
    # Set with different TTLs
    await manager.set("config:app", {"debug": False, "version": "1.0"}, ttl_seconds=3600, tags=["config"])
    await manager.set("session:abc123", {"user_id": 1, "expires": "2024-12-31"}, ttl_seconds=1800, tags=["sessions"])
    print("  ✓ Cached config and session")
    
    # Get values
    print("\n📖 Reading from Cache...")
    
    for i in range(10):
        key = f"user:{random.randint(0, 19)}"
        value = await manager.get(key)
        
    print("  ✓ Read 10 random users")
    
    # Simulate cache misses and origin loads
    print("\n🔄 Loading from Origin...")
    
    for i in range(30, 35):
        value = await manager.get(f"user:{i}", load_from_origin=True)
        print(f"  📥 user:{i}: loaded from origin")
        
    # Invalidation
    print("\n🗑️ Cache Invalidation...")
    
    count = await manager.invalidate_by_tags(["tier_0"])
    print(f"  🗑️ Invalidated by tag 'tier_0': {count} entries")
    
    count = await manager.invalidate_pattern("session:*")
    print(f"  🗑️ Invalidated pattern 'session:*': {count} entries")
    
    # Bulk operations
    print("\n📦 Bulk Operations...")
    
    for i in range(100):
        await manager.set(
            f"product:{i}",
            {"id": i, "name": f"Product {i}", "price": random.randint(10, 1000)},
            tags=["products", f"category_{i % 5}"]
        )
        
    print("  ✓ Cached 100 products")
    
    # Read mix
    for i in range(200):
        key = random.choice([
            f"user:{random.randint(0, 24)}",
            f"product:{random.randint(0, 99)}",
            f"config:app"
        ])
        await manager.get(key)
        
    print("  ✓ Performed 200 mixed reads")
    
    # Display L1 cache
    print("\n📊 L1 Cache (Top Entries):")
    
    l1_store = manager.stores[CacheLevel.L1]
    
    print("\n  ┌────────────────────────┬─────────────────────────┬────────────┬────────────┐")
    print("  │ Key                    │ TTL                     │ Hits       │ Size       │")
    print("  ├────────────────────────┼─────────────────────────┼────────────┼────────────┤")
    
    for key, entry in list(l1_store.entries.items())[:8]:
        key_display = key[:22].ljust(22)
        
        if entry.expires_at:
            remaining = (entry.expires_at - datetime.now()).total_seconds()
            ttl_display = f"{int(remaining)}s".ljust(23)
        else:
            ttl_display = "never".ljust(23)
            
        hits = str(entry.hit_count).ljust(10)
        size = f"{entry.size_bytes}B".ljust(10)
        
        print(f"  │ {key_display} │ {ttl_display} │ {hits} │ {size} │")
        
    print("  └────────────────────────┴─────────────────────────┴────────────┴────────────┘")
    
    # Display per-level statistics
    print("\n📈 Per-Level Statistics:")
    
    for level, store in manager.stores.items():
        stats = store.get_stats()
        
        print(f"\n  📦 {level.value.upper()} ({store.config.name}):")
        print(f"    Entries: {stats['entries']}")
        print(f"    Size: {stats['bytes']} bytes")
        print(f"    Hits: {stats['hits']}")
        print(f"    Misses: {stats['misses']}")
        print(f"    Hit Rate: {stats['hit_rate']:.1f}%")
        print(f"    Evictions: {stats['evictions']}")
        print(f"    Read Latency: {stats['avg_read_latency_ms']:.3f}ms")
        print(f"    Write Latency: {stats['avg_write_latency_ms']:.3f}ms")
        
    # Eviction policies
    print("\n🔄 Eviction Policies:")
    
    for level, store in manager.stores.items():
        policy = store.config.eviction_policy
        print(f"  {level.value.upper()}: {policy.value}")
        
    # Write policies
    print("\n✍️ Write Policies:")
    
    for level, store in manager.stores.items():
        policy = store.config.write_policy
        print(f"  {level.value.upper()}: {policy.value}")
        
    # Cleanup expired
    print("\n🧹 Cleanup...")
    
    cleaned = await manager.cleanup_all()
    print(f"  Cleaned {cleaned} expired entries")
    
    # Flush write-back
    await manager.flush_write_back()
    print("  Flushed write-back queue")
    
    # Overall statistics
    print("\n📊 Overall Statistics:")
    
    all_stats = manager.get_statistics()
    
    print(f"\n  Total Hits: {all_stats['total']['hits']}")
    print(f"  Total Misses: {all_stats['total']['misses']}")
    print(f"  Overall Hit Rate: {all_stats['total']['hit_rate']:.1f}%")
    print(f"  Write-back Pending: {all_stats['total']['write_back_pending']}")
    
    # Cache hierarchy visualization
    print("\n🏗️ Cache Hierarchy:")
    
    for level, store in manager.stores.items():
        stats = store.get_stats()
        fill = int(stats['entries'] / store.config.max_entries * 20) if store.config.max_entries > 0 else 0
        bar = "█" * fill + "░" * (20 - fill)
        
        print(f"\n  {level.value.upper()} [{bar}] {stats['entries']}/{store.config.max_entries}")
        print(f"     Hit Rate: {stats['hit_rate']:.1f}% | Latency: {stats['avg_read_latency_ms']:.3f}ms")
        
    # Dashboard
    total_entries = sum(s.get_stats()['entries'] for s in manager.stores.values())
    total_bytes = sum(s.get_stats()['bytes'] for s in manager.stores.values())
    
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                      Cache Manager Dashboard                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Cache Levels:                  {len(manager.stores):>12}                        │")
    print(f"│ Total Entries:                 {total_entries:>12}                        │")
    print(f"│ Total Size:                    {total_bytes:>12} bytes                  │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Overall Hit Rate:              {all_stats['total']['hit_rate']:>11.1f}%                        │")
    print(f"│ Total Hits:                    {all_stats['total']['hits']:>12}                        │")
    print(f"│ Total Misses:                  {all_stats['total']['misses']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Cache Manager Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
