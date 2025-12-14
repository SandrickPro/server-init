#!/usr/bin/env python3
"""
Server Init - Iteration 238: Caching Platform
Платформа кэширования

Функционал:
- Cache Management - управление кэшем
- Cache Invalidation - инвалидация кэша
- Cache Replication - репликация кэша
- TTL Management - управление TTL
- Cache Statistics - статистика кэша
- Cache Clustering - кластеризация
- Write-Through/Write-Behind - стратегии записи
- Cache Warming - прогрев кэша
"""

import asyncio
import random
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
import uuid
import json


class CacheType(Enum):
    """Тип кэша"""
    IN_MEMORY = "in_memory"
    DISTRIBUTED = "distributed"
    LOCAL = "local"
    HIERARCHICAL = "hierarchical"


class EvictionPolicy(Enum):
    """Политика вытеснения"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"  # Time To Live
    RANDOM = "random"


class WritePolicy(Enum):
    """Политика записи"""
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    WRITE_AROUND = "write_around"


class CacheStatus(Enum):
    """Статус кэша"""
    ACTIVE = "active"
    WARMING = "warming"
    FLUSHING = "flushing"
    DISABLED = "disabled"


@dataclass
class CacheNode:
    """Узел кэша"""
    node_id: str
    host: str = ""
    port: int = 6379
    
    # Status
    is_primary: bool = False
    is_healthy: bool = True
    
    # Capacity
    max_memory_mb: int = 1024
    used_memory_mb: int = 0
    
    # Stats
    hits: int = 0
    misses: int = 0
    
    # Connected
    connected_at: datetime = field(default_factory=datetime.now)


@dataclass
class CacheEntry:
    """Запись кэша"""
    key: str
    value: Any = None
    
    # Metadata
    size_bytes: int = 0
    
    # TTL
    ttl_seconds: int = 3600
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=1))
    
    # Stats
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)
    
    # Tags for invalidation
    tags: List[str] = field(default_factory=list)


@dataclass
class CacheRegion:
    """Регион кэша"""
    region_id: str
    name: str = ""
    
    # Type
    cache_type: CacheType = CacheType.IN_MEMORY
    
    # Policies
    eviction_policy: EvictionPolicy = EvictionPolicy.LRU
    write_policy: WritePolicy = WritePolicy.WRITE_THROUGH
    
    # Capacity
    max_entries: int = 10000
    max_memory_mb: int = 256
    
    # TTL
    default_ttl_seconds: int = 3600
    
    # Status
    status: CacheStatus = CacheStatus.ACTIVE
    
    # Stats
    entry_count: int = 0
    memory_used_mb: float = 0
    hits: int = 0
    misses: int = 0


@dataclass
class InvalidationRule:
    """Правило инвалидации"""
    rule_id: str
    name: str = ""
    
    # Pattern
    key_pattern: str = "*"
    tag_pattern: str = ""
    
    # Trigger
    trigger: str = "manual"  # manual, event, schedule
    
    # Schedule (cron expression)
    schedule: str = ""
    
    # Active
    is_active: bool = True
    
    # Stats
    invalidations: int = 0
    last_run: Optional[datetime] = None


@dataclass
class WarmingTask:
    """Задача прогрева кэша"""
    task_id: str
    region_id: str = ""
    
    # Status
    status: str = "pending"  # pending, running, completed, failed
    
    # Progress
    total_keys: int = 0
    loaded_keys: int = 0
    
    # Times
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class CachePlatform:
    """Платформа кэширования"""
    
    def __init__(self):
        self.nodes: Dict[str, CacheNode] = {}
        self.regions: Dict[str, CacheRegion] = {}
        self.entries: Dict[str, Dict[str, CacheEntry]] = {}  # region_id -> key -> entry
        self.invalidation_rules: Dict[str, InvalidationRule] = {}
        self.warming_tasks: List[WarmingTask] = []
        
    def add_node(self, host: str, port: int = 6379,
                max_memory_mb: int = 1024,
                is_primary: bool = False) -> CacheNode:
        """Добавление узла кэша"""
        node = CacheNode(
            node_id=f"node_{uuid.uuid4().hex[:8]}",
            host=host,
            port=port,
            max_memory_mb=max_memory_mb,
            is_primary=is_primary
        )
        
        self.nodes[node.node_id] = node
        return node
        
    def create_region(self, name: str,
                     cache_type: CacheType = CacheType.IN_MEMORY,
                     eviction_policy: EvictionPolicy = EvictionPolicy.LRU,
                     max_entries: int = 10000,
                     max_memory_mb: int = 256,
                     default_ttl: int = 3600) -> CacheRegion:
        """Создание региона кэша"""
        region = CacheRegion(
            region_id=f"reg_{uuid.uuid4().hex[:8]}",
            name=name,
            cache_type=cache_type,
            eviction_policy=eviction_policy,
            max_entries=max_entries,
            max_memory_mb=max_memory_mb,
            default_ttl_seconds=default_ttl
        )
        
        self.regions[region.region_id] = region
        self.entries[region.region_id] = {}
        
        return region
        
    def put(self, region_id: str, key: str, value: Any,
           ttl_seconds: int = None,
           tags: List[str] = None) -> bool:
        """Запись в кэш"""
        region = self.regions.get(region_id)
        if not region:
            return False
            
        # Check capacity
        if region.entry_count >= region.max_entries:
            self._evict(region_id)
            
        ttl = ttl_seconds or region.default_ttl_seconds
        
        # Calculate size
        value_str = json.dumps(value) if not isinstance(value, str) else value
        size = len(value_str.encode())
        
        entry = CacheEntry(
            key=key,
            value=value,
            size_bytes=size,
            ttl_seconds=ttl,
            expires_at=datetime.now() + timedelta(seconds=ttl),
            tags=tags or []
        )
        
        self.entries[region_id][key] = entry
        region.entry_count = len(self.entries[region_id])
        region.memory_used_mb = sum(e.size_bytes for e in self.entries[region_id].values()) / (1024**2)
        
        return True
        
    def get(self, region_id: str, key: str) -> Optional[Any]:
        """Чтение из кэша"""
        region = self.regions.get(region_id)
        if not region:
            return None
            
        region_entries = self.entries.get(region_id, {})
        entry = region_entries.get(key)
        
        if not entry:
            region.misses += 1
            return None
            
        # Check expiration
        if datetime.now() > entry.expires_at:
            del region_entries[key]
            region.misses += 1
            region.entry_count = len(region_entries)
            return None
            
        # Update stats
        entry.access_count += 1
        entry.last_accessed = datetime.now()
        region.hits += 1
        
        return entry.value
        
    def delete(self, region_id: str, key: str) -> bool:
        """Удаление из кэша"""
        region = self.regions.get(region_id)
        if not region:
            return False
            
        region_entries = self.entries.get(region_id, {})
        if key in region_entries:
            del region_entries[key]
            region.entry_count = len(region_entries)
            return True
            
        return False
        
    def _evict(self, region_id: str):
        """Вытеснение записей"""
        region = self.regions.get(region_id)
        if not region:
            return
            
        region_entries = self.entries.get(region_id, {})
        if not region_entries:
            return
            
        # Select entry to evict based on policy
        entries_list = list(region_entries.values())
        
        if region.eviction_policy == EvictionPolicy.LRU:
            victim = min(entries_list, key=lambda e: e.last_accessed)
        elif region.eviction_policy == EvictionPolicy.LFU:
            victim = min(entries_list, key=lambda e: e.access_count)
        elif region.eviction_policy == EvictionPolicy.FIFO:
            victim = min(entries_list, key=lambda e: e.created_at)
        elif region.eviction_policy == EvictionPolicy.TTL:
            victim = min(entries_list, key=lambda e: e.expires_at)
        else:
            victim = random.choice(entries_list)
            
        del region_entries[victim.key]
        region.entry_count = len(region_entries)
        
    def invalidate_by_pattern(self, region_id: str, pattern: str) -> int:
        """Инвалидация по паттерну"""
        region_entries = self.entries.get(region_id, {})
        
        # Simple pattern matching (supports *)
        import fnmatch
        
        keys_to_delete = [
            key for key in region_entries.keys()
            if fnmatch.fnmatch(key, pattern)
        ]
        
        for key in keys_to_delete:
            del region_entries[key]
            
        region = self.regions.get(region_id)
        if region:
            region.entry_count = len(region_entries)
            
        return len(keys_to_delete)
        
    def invalidate_by_tag(self, region_id: str, tag: str) -> int:
        """Инвалидация по тегу"""
        region_entries = self.entries.get(region_id, {})
        
        keys_to_delete = [
            key for key, entry in region_entries.items()
            if tag in entry.tags
        ]
        
        for key in keys_to_delete:
            del region_entries[key]
            
        region = self.regions.get(region_id)
        if region:
            region.entry_count = len(region_entries)
            
        return len(keys_to_delete)
        
    def flush_region(self, region_id: str) -> int:
        """Очистка региона"""
        region_entries = self.entries.get(region_id, {})
        count = len(region_entries)
        
        region_entries.clear()
        
        region = self.regions.get(region_id)
        if region:
            region.entry_count = 0
            region.memory_used_mb = 0
            
        return count
        
    def create_invalidation_rule(self, name: str,
                                key_pattern: str = "*",
                                tag_pattern: str = "",
                                trigger: str = "manual") -> InvalidationRule:
        """Создание правила инвалидации"""
        rule = InvalidationRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name=name,
            key_pattern=key_pattern,
            tag_pattern=tag_pattern,
            trigger=trigger
        )
        
        self.invalidation_rules[rule.rule_id] = rule
        return rule
        
    def warm_cache(self, region_id: str,
                  data: Dict[str, Any]) -> WarmingTask:
        """Прогрев кэша"""
        task = WarmingTask(
            task_id=f"warm_{uuid.uuid4().hex[:8]}",
            region_id=region_id,
            total_keys=len(data),
            started_at=datetime.now()
        )
        
        task.status = "running"
        
        # Load data
        for key, value in data.items():
            if self.put(region_id, key, value):
                task.loaded_keys += 1
                
        task.status = "completed"
        task.completed_at = datetime.now()
        
        self.warming_tasks.append(task)
        return task
        
    def get_region_stats(self, region_id: str) -> Dict[str, Any]:
        """Статистика региона"""
        region = self.regions.get(region_id)
        if not region:
            return {}
            
        total = region.hits + region.misses
        hit_rate = (region.hits / total * 100) if total > 0 else 0
        
        return {
            "name": region.name,
            "entry_count": region.entry_count,
            "memory_used_mb": region.memory_used_mb,
            "max_memory_mb": region.max_memory_mb,
            "hits": region.hits,
            "misses": region.misses,
            "hit_rate": hit_rate,
            "eviction_policy": region.eviction_policy.value
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        regions = list(self.regions.values())
        nodes = list(self.nodes.values())
        
        total_entries = sum(r.entry_count for r in regions)
        total_hits = sum(r.hits for r in regions)
        total_misses = sum(r.misses for r in regions)
        total = total_hits + total_misses
        
        return {
            "total_nodes": len(nodes),
            "total_regions": len(regions),
            "total_entries": total_entries,
            "total_hits": total_hits,
            "total_misses": total_misses,
            "hit_rate": (total_hits / total * 100) if total > 0 else 0,
            "healthy_nodes": len([n for n in nodes if n.is_healthy]),
            "invalidation_rules": len(self.invalidation_rules)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 238: Caching Platform")
    print("=" * 60)
    
    platform = CachePlatform()
    print("✓ Caching Platform created")
    
    # Add cache nodes
    print("\n🖥️ Adding Cache Nodes...")
    
    nodes_config = [
        ("cache-01.prod", 6379, 2048, True),
        ("cache-02.prod", 6379, 2048, False),
        ("cache-03.prod", 6379, 2048, False),
    ]
    
    nodes = []
    for host, port, memory, is_primary in nodes_config:
        node = platform.add_node(host, port, memory, is_primary)
        nodes.append(node)
        role = "PRIMARY" if is_primary else "REPLICA"
        print(f"  🖥️ {host}:{port} ({role}, {memory}MB)")
        
    # Create cache regions
    print("\n📦 Creating Cache Regions...")
    
    regions_config = [
        ("user-sessions", CacheType.DISTRIBUTED, EvictionPolicy.LRU, 50000, 512, 3600),
        ("api-responses", CacheType.IN_MEMORY, EvictionPolicy.TTL, 10000, 256, 300),
        ("product-catalog", CacheType.DISTRIBUTED, EvictionPolicy.LFU, 100000, 1024, 86400),
        ("rate-limits", CacheType.LOCAL, EvictionPolicy.TTL, 100000, 128, 60),
        ("config-cache", CacheType.IN_MEMORY, EvictionPolicy.LRU, 1000, 64, 600),
    ]
    
    regions = []
    for name, ctype, eviction, max_entries, memory, ttl in regions_config:
        region = platform.create_region(name, ctype, eviction, max_entries, memory, ttl)
        regions.append(region)
        
        type_icons = {
            CacheType.IN_MEMORY: "💾",
            CacheType.DISTRIBUTED: "🌐",
            CacheType.LOCAL: "📍",
            CacheType.HIERARCHICAL: "📊"
        }
        icon = type_icons.get(ctype, "📦")
        print(f"  {icon} {name} ({eviction.value}, TTL={ttl}s)")
        
    # Populate cache with data
    print("\n📝 Populating Cache...")
    
    # User sessions
    for i in range(100):
        platform.put(
            regions[0].region_id,
            f"session:{uuid.uuid4().hex[:12]}",
            {"user_id": i, "created": datetime.now().isoformat()},
            3600,
            ["sessions", f"user:{i}"]
        )
        
    # API responses
    endpoints = ["/api/users", "/api/products", "/api/orders", "/api/stats"]
    for endpoint in endpoints:
        for i in range(20):
            platform.put(
                regions[1].region_id,
                f"api:{endpoint}:page:{i}",
                {"data": f"response for {endpoint} page {i}"},
                300,
                ["api", endpoint.replace("/", "_")]
            )
            
    # Products
    for i in range(500):
        platform.put(
            regions[2].region_id,
            f"product:{i}",
            {"id": i, "name": f"Product {i}", "price": random.randint(10, 1000)},
            86400,
            ["products", f"category:{i % 10}"]
        )
        
    total_entries = sum(r.entry_count for r in regions)
    print(f"  ✓ Cached {total_entries} entries")
    
    # Simulate cache operations
    print("\n🔄 Simulating Cache Operations...")
    
    # Read operations
    hits = 0
    misses = 0
    
    for _ in range(200):
        region = random.choice(regions)
        
        # 70% chance to hit existing key
        if random.random() < 0.7:
            region_entries = platform.entries.get(region.region_id, {})
            if region_entries:
                key = random.choice(list(region_entries.keys()))
                result = platform.get(region.region_id, key)
                if result:
                    hits += 1
                else:
                    misses += 1
        else:
            # Try non-existent key
            result = platform.get(region.region_id, f"nonexistent:{uuid.uuid4().hex}")
            misses += 1
            
    print(f"  ✅ Hits: {hits}")
    print(f"  ❌ Misses: {misses}")
    print(f"  📊 Hit Rate: {(hits / (hits + misses) * 100):.1f}%")
    
    # Cache invalidation
    print("\n🗑️ Testing Cache Invalidation...")
    
    # Invalidate by pattern
    invalidated = platform.invalidate_by_pattern(regions[1].region_id, "api:/api/users:*")
    print(f"  ✓ Invalidated {invalidated} entries by pattern")
    
    # Invalidate by tag
    invalidated = platform.invalidate_by_tag(regions[2].region_id, "category:5")
    print(f"  ✓ Invalidated {invalidated} entries by tag")
    
    # Create invalidation rules
    print("\n📋 Creating Invalidation Rules...")
    
    rules = [
        platform.create_invalidation_rule("Session Cleanup", "session:*", "", "schedule"),
        platform.create_invalidation_rule("API Cache Reset", "api:*", "", "event"),
        platform.create_invalidation_rule("Product Update", "", "products", "manual"),
    ]
    
    for rule in rules:
        print(f"  📋 {rule.name} ({rule.trigger})")
        
    # Cache warming
    print("\n🔥 Warming Cache...")
    
    warm_data = {f"config:{i}": {"setting": f"value_{i}"} for i in range(50)}
    task = platform.warm_cache(regions[4].region_id, warm_data)
    print(f"  ✓ Loaded {task.loaded_keys}/{task.total_keys} keys")
    
    # Display cache regions
    print("\n📦 Cache Regions:")
    
    print("\n  ┌──────────────────────┬────────────────┬──────────┬─────────┬──────────┐")
    print("  │ Region               │ Type           │ Entries  │ Memory  │ Hit Rate │")
    print("  ├──────────────────────┼────────────────┼──────────┼─────────┼──────────┤")
    
    for region in platform.regions.values():
        name = region.name[:20].ljust(20)
        rtype = region.cache_type.value[:14].ljust(14)
        entries = str(region.entry_count)[:8].ljust(8)
        memory = f"{region.memory_used_mb:.1f}MB"[:7].ljust(7)
        
        total = region.hits + region.misses
        hit_rate = f"{(region.hits / total * 100):.0f}%" if total > 0 else "N/A"
        hit_rate = hit_rate[:8].ljust(8)
        
        print(f"  │ {name} │ {rtype} │ {entries} │ {memory} │ {hit_rate} │")
        
    print("  └──────────────────────┴────────────────┴──────────┴─────────┴──────────┘")
    
    # Display nodes
    print("\n🖥️ Cache Nodes:")
    
    for node in platform.nodes.values():
        role = "🔵 PRIMARY" if node.is_primary else "⚪ REPLICA"
        status = "🟢" if node.is_healthy else "🔴"
        memory_pct = (node.used_memory_mb / node.max_memory_mb * 100) if node.max_memory_mb > 0 else 0
        print(f"  {status} {node.host}:{node.port} {role}")
        print(f"     Memory: {memory_pct:.0f}% used")
        
    # Cache performance
    print("\n📊 Cache Performance:")
    
    stats = platform.get_statistics()
    
    print(f"\n  Total Hits: {stats['total_hits']}")
    print(f"  Total Misses: {stats['total_misses']}")
    print(f"  Overall Hit Rate: {stats['hit_rate']:.1f}%")
    
    # Per-region hit rates
    print("\n  Per-Region Hit Rates:")
    for region in platform.regions.values():
        total = region.hits + region.misses
        if total > 0:
            rate = region.hits / total * 100
            bar_len = int(rate / 10)
            bar = "█" * bar_len + "░" * (10 - bar_len)
            print(f"    {region.name:20s} [{bar}] {rate:.0f}%")
            
    # Eviction policy distribution
    print("\n📋 Eviction Policies:")
    
    policy_counts = {}
    for region in platform.regions.values():
        p = region.eviction_policy.value
        policy_counts[p] = policy_counts.get(p, 0) + 1
        
    policy_icons = {"lru": "⏮️", "lfu": "📉", "ttl": "⏰", "fifo": "📋", "random": "🎲"}
    for policy, count in policy_counts.items():
        icon = policy_icons.get(policy, "📋")
        bar = "█" * (count * 2) + "░" * (10 - count * 2)
        print(f"  {icon} {policy:8s} [{bar}] {count}")
        
    # Memory usage
    print("\n💾 Memory Usage:")
    
    total_used = sum(r.memory_used_mb for r in platform.regions.values())
    total_max = sum(r.max_memory_mb for r in platform.regions.values())
    
    print(f"  Total Used: {total_used:.2f} MB")
    print(f"  Total Max: {total_max} MB")
    print(f"  Utilization: {(total_used / total_max * 100):.1f}%")
    
    # Statistics
    print("\n📊 Platform Statistics:")
    
    print(f"\n  Nodes: {stats['total_nodes']} ({stats['healthy_nodes']} healthy)")
    print(f"  Regions: {stats['total_regions']}")
    print(f"  Total Entries: {stats['total_entries']}")
    print(f"  Invalidation Rules: {stats['invalidation_rules']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                       Caching Dashboard                            │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Cache Nodes:                   {stats['total_nodes']:>12}                        │")
    print(f"│ Cache Regions:                 {stats['total_regions']:>12}                        │")
    print(f"│ Total Entries:                 {stats['total_entries']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Hit Rate:                         {stats['hit_rate']:>7.1f}%                       │")
    print(f"│ Memory Used (MB):                {total_used:>8.2f}                       │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Caching Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
