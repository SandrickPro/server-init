#!/usr/bin/env python3
"""
Server Init - Iteration 259: Rate Limiter Advanced Platform
Расширенная платформа ограничения скорости

Функционал:
- Token Bucket - алгоритм токенного ведра
- Sliding Window Log - скользящий лог окна
- Sliding Window Counter - скользящий счётчик окна
- Fixed Window Counter - фиксированный счётчик окна
- Leaky Bucket - алгоритм протекающего ведра
- Multi-Tier Limiting - многоуровневое ограничение
- Distributed Rate Limiting - распределённое ограничение
- Analytics & Reporting - аналитика и отчётность
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Deque
from collections import deque
from enum import Enum
import uuid


class RateLimitAlgorithm(Enum):
    """Алгоритм rate limiting"""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW_LOG = "sliding_window_log"
    SLIDING_WINDOW_COUNTER = "sliding_window_counter"
    FIXED_WINDOW_COUNTER = "fixed_window_counter"
    LEAKY_BUCKET = "leaky_bucket"


class RateLimitScope(Enum):
    """Область действия лимита"""
    GLOBAL = "global"
    PER_USER = "per_user"
    PER_IP = "per_ip"
    PER_API_KEY = "per_api_key"
    PER_ENDPOINT = "per_endpoint"


class RateLimitResponse(Enum):
    """Ответ на rate limit"""
    ALLOWED = "allowed"
    DENIED = "denied"
    QUEUED = "queued"
    THROTTLED = "throttled"


@dataclass
class TokenBucket:
    """Токенное ведро"""
    capacity: int = 100
    tokens: float = 100
    refill_rate: float = 10  # tokens per second
    last_refill: datetime = field(default_factory=datetime.now)


@dataclass
class SlidingWindowLog:
    """Лог скользящего окна"""
    window_size_ms: int = 60000  # 1 minute
    requests: Deque[datetime] = field(default_factory=deque)


@dataclass
class SlidingWindowCounter:
    """Счётчик скользящего окна"""
    window_size_ms: int = 60000
    current_window_start: datetime = field(default_factory=datetime.now)
    current_count: int = 0
    previous_count: int = 0


@dataclass
class FixedWindowCounter:
    """Счётчик фиксированного окна"""
    window_size_ms: int = 60000
    window_start: datetime = field(default_factory=datetime.now)
    count: int = 0


@dataclass
class LeakyBucket:
    """Протекающее ведро"""
    capacity: int = 100
    queue: Deque[datetime] = field(default_factory=deque)
    leak_rate: float = 10  # requests per second
    last_leak: datetime = field(default_factory=datetime.now)


@dataclass
class RateLimitConfig:
    """Конфигурация rate limiter"""
    config_id: str
    name: str
    
    # Algorithm
    algorithm: RateLimitAlgorithm = RateLimitAlgorithm.TOKEN_BUCKET
    
    # Limits
    requests_per_second: float = 10
    requests_per_minute: int = 600
    requests_per_hour: int = 36000
    
    # Burst
    burst_capacity: int = 100
    
    # Scope
    scope: RateLimitScope = RateLimitScope.GLOBAL
    
    # Window
    window_size_ms: int = 60000
    
    # Response
    queue_excess: bool = False
    max_queue_wait_ms: int = 5000


@dataclass
class RateLimitEntry:
    """Запись rate limit"""
    entry_id: str
    identifier: str  # user_id, ip, api_key, etc.
    
    # Buckets/Windows
    token_bucket: Optional[TokenBucket] = None
    sliding_log: Optional[SlidingWindowLog] = None
    sliding_counter: Optional[SlidingWindowCounter] = None
    fixed_counter: Optional[FixedWindowCounter] = None
    leaky_bucket: Optional[LeakyBucket] = None
    
    # Stats
    total_requests: int = 0
    allowed_requests: int = 0
    denied_requests: int = 0
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    last_request: datetime = field(default_factory=datetime.now)


@dataclass
class RateLimitResult:
    """Результат проверки rate limit"""
    result_id: str
    identifier: str
    
    # Response
    response: RateLimitResponse = RateLimitResponse.ALLOWED
    
    # Info
    remaining: int = 0
    reset_at: Optional[datetime] = None
    retry_after_ms: int = 0
    
    # Stats
    current_rate: float = 0


@dataclass
class RateLimitMetrics:
    """Метрики rate limiter"""
    limiter_name: str
    
    # Totals
    total_requests: int = 0
    total_allowed: int = 0
    total_denied: int = 0
    
    # Rates
    current_rate_per_second: float = 0
    peak_rate_per_second: float = 0
    
    # Identifiers
    unique_identifiers: int = 0
    identifiers_at_limit: int = 0


class RateLimiterManager:
    """Менеджер rate limiter"""
    
    def __init__(self):
        self.configs: Dict[str, RateLimitConfig] = {}
        self.entries: Dict[str, Dict[str, RateLimitEntry]] = {}  # limiter_name -> identifier -> entry
        self.metrics: Dict[str, RateLimitMetrics] = {}
        
    def create_config(self, name: str,
                     algorithm: RateLimitAlgorithm = RateLimitAlgorithm.TOKEN_BUCKET,
                     requests_per_second: float = 10,
                     burst_capacity: int = 100,
                     scope: RateLimitScope = RateLimitScope.GLOBAL) -> RateLimitConfig:
        """Создание конфигурации"""
        config = RateLimitConfig(
            config_id=f"cfg_{uuid.uuid4().hex[:8]}",
            name=name,
            algorithm=algorithm,
            requests_per_second=requests_per_second,
            burst_capacity=burst_capacity,
            scope=scope,
            requests_per_minute=int(requests_per_second * 60),
            requests_per_hour=int(requests_per_second * 3600)
        )
        
        self.configs[name] = config
        self.entries[name] = {}
        self.metrics[name] = RateLimitMetrics(limiter_name=name)
        
        return config
        
    def _get_or_create_entry(self, limiter_name: str, identifier: str) -> RateLimitEntry:
        """Получение или создание записи"""
        if limiter_name not in self.entries:
            self.entries[limiter_name] = {}
            
        if identifier not in self.entries[limiter_name]:
            config = self.configs.get(limiter_name)
            entry = RateLimitEntry(
                entry_id=f"ent_{uuid.uuid4().hex[:8]}",
                identifier=identifier
            )
            
            if config:
                if config.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
                    entry.token_bucket = TokenBucket(
                        capacity=config.burst_capacity,
                        tokens=config.burst_capacity,
                        refill_rate=config.requests_per_second
                    )
                elif config.algorithm == RateLimitAlgorithm.SLIDING_WINDOW_LOG:
                    entry.sliding_log = SlidingWindowLog(
                        window_size_ms=config.window_size_ms
                    )
                elif config.algorithm == RateLimitAlgorithm.SLIDING_WINDOW_COUNTER:
                    entry.sliding_counter = SlidingWindowCounter(
                        window_size_ms=config.window_size_ms
                    )
                elif config.algorithm == RateLimitAlgorithm.FIXED_WINDOW_COUNTER:
                    entry.fixed_counter = FixedWindowCounter(
                        window_size_ms=config.window_size_ms
                    )
                elif config.algorithm == RateLimitAlgorithm.LEAKY_BUCKET:
                    entry.leaky_bucket = LeakyBucket(
                        capacity=config.burst_capacity,
                        leak_rate=config.requests_per_second
                    )
                    
            self.entries[limiter_name][identifier] = entry
            
        return self.entries[limiter_name][identifier]
        
    def _check_token_bucket(self, entry: RateLimitEntry, config: RateLimitConfig) -> RateLimitResult:
        """Проверка token bucket"""
        bucket = entry.token_bucket
        now = datetime.now()
        
        # Refill tokens
        elapsed = (now - bucket.last_refill).total_seconds()
        bucket.tokens = min(
            bucket.capacity,
            bucket.tokens + elapsed * bucket.refill_rate
        )
        bucket.last_refill = now
        
        result = RateLimitResult(
            result_id=f"res_{uuid.uuid4().hex[:8]}",
            identifier=entry.identifier,
            remaining=int(bucket.tokens),
            current_rate=config.requests_per_second
        )
        
        if bucket.tokens >= 1:
            bucket.tokens -= 1
            result.response = RateLimitResponse.ALLOWED
            result.remaining = int(bucket.tokens)
        else:
            result.response = RateLimitResponse.DENIED
            result.retry_after_ms = int((1 - bucket.tokens) / bucket.refill_rate * 1000)
            
        return result
        
    def _check_sliding_window_log(self, entry: RateLimitEntry, config: RateLimitConfig) -> RateLimitResult:
        """Проверка sliding window log"""
        log = entry.sliding_log
        now = datetime.now()
        cutoff = now - timedelta(milliseconds=log.window_size_ms)
        
        # Remove old requests
        while log.requests and log.requests[0] < cutoff:
            log.requests.popleft()
            
        result = RateLimitResult(
            result_id=f"res_{uuid.uuid4().hex[:8]}",
            identifier=entry.identifier,
            remaining=max(0, config.requests_per_minute - len(log.requests)),
            reset_at=now + timedelta(milliseconds=log.window_size_ms)
        )
        
        if len(log.requests) < config.requests_per_minute:
            log.requests.append(now)
            result.response = RateLimitResponse.ALLOWED
        else:
            result.response = RateLimitResponse.DENIED
            if log.requests:
                oldest = log.requests[0]
                result.retry_after_ms = int((oldest - cutoff).total_seconds() * 1000)
                
        result.current_rate = len(log.requests) / (log.window_size_ms / 1000)
        
        return result
        
    def _check_sliding_window_counter(self, entry: RateLimitEntry, config: RateLimitConfig) -> RateLimitResult:
        """Проверка sliding window counter"""
        counter = entry.sliding_counter
        now = datetime.now()
        window_ms = counter.window_size_ms
        
        # Check if we need new window
        elapsed = (now - counter.current_window_start).total_seconds() * 1000
        if elapsed >= window_ms:
            counter.previous_count = counter.current_count
            counter.current_count = 0
            counter.current_window_start = now
            elapsed = 0
            
        # Calculate weighted count
        weight = 1 - (elapsed / window_ms)
        weighted_count = counter.previous_count * weight + counter.current_count
        
        result = RateLimitResult(
            result_id=f"res_{uuid.uuid4().hex[:8]}",
            identifier=entry.identifier,
            remaining=max(0, int(config.requests_per_minute - weighted_count)),
            reset_at=counter.current_window_start + timedelta(milliseconds=window_ms)
        )
        
        if weighted_count < config.requests_per_minute:
            counter.current_count += 1
            result.response = RateLimitResponse.ALLOWED
        else:
            result.response = RateLimitResponse.DENIED
            result.retry_after_ms = int(window_ms - elapsed)
            
        result.current_rate = weighted_count / (window_ms / 1000)
        
        return result
        
    def _check_fixed_window_counter(self, entry: RateLimitEntry, config: RateLimitConfig) -> RateLimitResult:
        """Проверка fixed window counter"""
        counter = entry.fixed_counter
        now = datetime.now()
        
        # Check if window expired
        elapsed = (now - counter.window_start).total_seconds() * 1000
        if elapsed >= counter.window_size_ms:
            counter.window_start = now
            counter.count = 0
            elapsed = 0
            
        result = RateLimitResult(
            result_id=f"res_{uuid.uuid4().hex[:8]}",
            identifier=entry.identifier,
            remaining=max(0, config.requests_per_minute - counter.count),
            reset_at=counter.window_start + timedelta(milliseconds=counter.window_size_ms)
        )
        
        if counter.count < config.requests_per_minute:
            counter.count += 1
            result.response = RateLimitResponse.ALLOWED
        else:
            result.response = RateLimitResponse.DENIED
            result.retry_after_ms = int(counter.window_size_ms - elapsed)
            
        result.current_rate = counter.count / ((elapsed or 1) / 1000)
        
        return result
        
    def _check_leaky_bucket(self, entry: RateLimitEntry, config: RateLimitConfig) -> RateLimitResult:
        """Проверка leaky bucket"""
        bucket = entry.leaky_bucket
        now = datetime.now()
        
        # Leak requests
        elapsed = (now - bucket.last_leak).total_seconds()
        leak_count = int(elapsed * bucket.leak_rate)
        for _ in range(min(leak_count, len(bucket.queue))):
            bucket.queue.popleft()
        bucket.last_leak = now
        
        result = RateLimitResult(
            result_id=f"res_{uuid.uuid4().hex[:8]}",
            identifier=entry.identifier,
            remaining=max(0, bucket.capacity - len(bucket.queue))
        )
        
        if len(bucket.queue) < bucket.capacity:
            bucket.queue.append(now)
            result.response = RateLimitResponse.ALLOWED
        else:
            result.response = RateLimitResponse.DENIED
            result.retry_after_ms = int(1000 / bucket.leak_rate)
            
        result.current_rate = len(bucket.queue) * bucket.leak_rate / bucket.capacity if bucket.capacity > 0 else 0
        
        return result
        
    def check_rate_limit(self, limiter_name: str, identifier: str = "global") -> RateLimitResult:
        """Проверка rate limit"""
        config = self.configs.get(limiter_name)
        if not config:
            return RateLimitResult(
                result_id=f"res_{uuid.uuid4().hex[:8]}",
                identifier=identifier,
                response=RateLimitResponse.ALLOWED
            )
            
        entry = self._get_or_create_entry(limiter_name, identifier)
        entry.total_requests += 1
        entry.last_request = datetime.now()
        
        # Check based on algorithm
        if config.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
            result = self._check_token_bucket(entry, config)
        elif config.algorithm == RateLimitAlgorithm.SLIDING_WINDOW_LOG:
            result = self._check_sliding_window_log(entry, config)
        elif config.algorithm == RateLimitAlgorithm.SLIDING_WINDOW_COUNTER:
            result = self._check_sliding_window_counter(entry, config)
        elif config.algorithm == RateLimitAlgorithm.FIXED_WINDOW_COUNTER:
            result = self._check_fixed_window_counter(entry, config)
        elif config.algorithm == RateLimitAlgorithm.LEAKY_BUCKET:
            result = self._check_leaky_bucket(entry, config)
        else:
            result = RateLimitResult(
                result_id=f"res_{uuid.uuid4().hex[:8]}",
                identifier=identifier,
                response=RateLimitResponse.ALLOWED
            )
            
        # Update stats
        if result.response == RateLimitResponse.ALLOWED:
            entry.allowed_requests += 1
        else:
            entry.denied_requests += 1
            
        # Update metrics
        metrics = self.metrics.get(limiter_name)
        if metrics:
            metrics.total_requests += 1
            if result.response == RateLimitResponse.ALLOWED:
                metrics.total_allowed += 1
            else:
                metrics.total_denied += 1
            metrics.unique_identifiers = len(self.entries.get(limiter_name, {}))
            
        return result
        
    def get_remaining(self, limiter_name: str, identifier: str = "global") -> int:
        """Получение оставшегося лимита"""
        entry = self.entries.get(limiter_name, {}).get(identifier)
        if not entry:
            config = self.configs.get(limiter_name)
            return config.burst_capacity if config else 0
            
        if entry.token_bucket:
            return int(entry.token_bucket.tokens)
        elif entry.sliding_log:
            config = self.configs.get(limiter_name)
            return max(0, config.requests_per_minute - len(entry.sliding_log.requests)) if config else 0
        elif entry.sliding_counter:
            config = self.configs.get(limiter_name)
            return max(0, config.requests_per_minute - entry.sliding_counter.current_count) if config else 0
        elif entry.fixed_counter:
            config = self.configs.get(limiter_name)
            return max(0, config.requests_per_minute - entry.fixed_counter.count) if config else 0
        elif entry.leaky_bucket:
            return entry.leaky_bucket.capacity - len(entry.leaky_bucket.queue)
            
        return 0
        
    def reset(self, limiter_name: str, identifier: str = None):
        """Сброс лимита"""
        if identifier:
            if limiter_name in self.entries and identifier in self.entries[limiter_name]:
                del self.entries[limiter_name][identifier]
        else:
            self.entries[limiter_name] = {}
            
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_requests = 0
        total_allowed = 0
        total_denied = 0
        
        for metrics in self.metrics.values():
            total_requests += metrics.total_requests
            total_allowed += metrics.total_allowed
            total_denied += metrics.total_denied
            
        return {
            "limiters_total": len(self.configs),
            "total_requests": total_requests,
            "total_allowed": total_allowed,
            "total_denied": total_denied,
            "denial_rate": (total_denied / max(1, total_requests)) * 100
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 259: Rate Limiter Advanced Platform")
    print("=" * 60)
    
    manager = RateLimiterManager()
    print("✓ Rate Limiter Manager created")
    
    # Create configurations
    print("\n⚙️ Creating Configurations...")
    
    configs_data = [
        ("api-public", RateLimitAlgorithm.TOKEN_BUCKET, 10.0, 50, RateLimitScope.PER_IP),
        ("api-authenticated", RateLimitAlgorithm.SLIDING_WINDOW_LOG, 100.0, 200, RateLimitScope.PER_USER),
        ("api-premium", RateLimitAlgorithm.SLIDING_WINDOW_COUNTER, 500.0, 1000, RateLimitScope.PER_API_KEY),
        ("webhook", RateLimitAlgorithm.LEAKY_BUCKET, 5.0, 20, RateLimitScope.PER_ENDPOINT),
    ]
    
    for name, algo, rps, burst, scope in configs_data:
        config = manager.create_config(name, algo, rps, burst, scope)
        print(f"  ⚙️ {name}: {algo.value}, {rps}/s, burst={burst}")
        
    # Test rate limiting
    print("\n🔄 Testing Rate Limits...")
    
    # Token Bucket test
    print("\n  Token Bucket (api-public):")
    
    results = {"allowed": 0, "denied": 0}
    for i in range(60):
        result = manager.check_rate_limit("api-public", f"ip_{i % 3}")
        if result.response == RateLimitResponse.ALLOWED:
            results["allowed"] += 1
        else:
            results["denied"] += 1
            
    print(f"    Allowed: {results['allowed']}, Denied: {results['denied']}")
    
    # Sliding Window Log test
    print("\n  Sliding Window Log (api-authenticated):")
    
    results = {"allowed": 0, "denied": 0}
    for i in range(150):
        result = manager.check_rate_limit("api-authenticated", f"user_{i % 2}")
        if result.response == RateLimitResponse.ALLOWED:
            results["allowed"] += 1
        else:
            results["denied"] += 1
            
    print(f"    Allowed: {results['allowed']}, Denied: {results['denied']}")
    
    # Display configurations
    print("\n⚙️ Rate Limit Configurations:")
    
    print("\n  ┌─────────────────────┬──────────────────────┬──────────┬──────────┬───────────────┐")
    print("  │ Name                │ Algorithm            │ RPS      │ Burst    │ Scope         │")
    print("  ├─────────────────────┼──────────────────────┼──────────┼──────────┼───────────────┤")
    
    for config in manager.configs.values():
        name = config.name[:19].ljust(19)
        algo = config.algorithm.value[:20].ljust(20)
        rps = f"{config.requests_per_second:.0f}"[:8].ljust(8)
        burst = str(config.burst_capacity)[:8].ljust(8)
        scope = config.scope.value[:13].ljust(13)
        
        print(f"  │ {name} │ {algo} │ {rps} │ {burst} │ {scope} │")
        
    print("  └─────────────────────┴──────────────────────┴──────────┴──────────┴───────────────┘")
    
    # Metrics
    print("\n📊 Rate Limit Metrics:")
    
    print("\n  ┌─────────────────────┬──────────┬──────────┬──────────┬──────────┬──────────┐")
    print("  │ Limiter             │ Total    │ Allowed  │ Denied   │ Deny(%)  │ Entries  │")
    print("  ├─────────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤")
    
    for name, metrics in manager.metrics.items():
        limiter_name = name[:19].ljust(19)
        total = str(metrics.total_requests)[:8].ljust(8)
        allowed = str(metrics.total_allowed)[:8].ljust(8)
        denied = str(metrics.total_denied)[:8].ljust(8)
        deny_rate = f"{(metrics.total_denied / max(1, metrics.total_requests)) * 100:.1f}"[:8].ljust(8)
        entries = str(metrics.unique_identifiers)[:8].ljust(8)
        
        print(f"  │ {limiter_name} │ {total} │ {allowed} │ {denied} │ {deny_rate} │ {entries} │")
        
    print("  └─────────────────────┴──────────┴──────────┴──────────┴──────────┴──────────┘")
    
    # Per-identifier stats
    print("\n📊 Per-Identifier Statistics:")
    
    for limiter_name, entries in manager.entries.items():
        if entries:
            print(f"\n  {limiter_name}:")
            for identifier, entry in list(entries.items())[:5]:
                remaining = manager.get_remaining(limiter_name, identifier)
                print(f"    {identifier}: {entry.allowed_requests} allowed, {entry.denied_requests} denied, {remaining} remaining")
                
    # Algorithm comparison
    print("\n📊 Algorithm Comparison:")
    
    for algo in RateLimitAlgorithm:
        configs = [c for c in manager.configs.values() if c.algorithm == algo]
        count = len(configs)
        bar = "█" * count + "░" * (5 - count)
        print(f"  {algo.value:25s} [{bar}] {count}")
        
    # Scope distribution
    print("\n📊 Scope Distribution:")
    
    for scope in RateLimitScope:
        configs = [c for c in manager.configs.values() if c.scope == scope]
        count = len(configs)
        if count > 0:
            print(f"  {scope.value:15s}: {count} limiter(s)")
            
    # Statistics
    print("\n📊 Manager Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Total Limiters: {stats['limiters_total']}")
    print(f"  Total Requests: {stats['total_requests']}")
    print(f"  Total Allowed: {stats['total_allowed']}")
    print(f"  Total Denied: {stats['total_denied']}")
    print(f"  Denial Rate: {stats['denial_rate']:.1f}%")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Rate Limiter Advanced Dashboard                   │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Limiters:                      {stats['limiters_total']:>12}                        │")
    print(f"│ Total Requests:                {stats['total_requests']:>12}                        │")
    print(f"│ Total Allowed:                 {stats['total_allowed']:>12}                        │")
    print(f"│ Total Denied:                  {stats['total_denied']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Denial Rate:                   {stats['denial_rate']:>11.1f}%                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Rate Limiter Advanced Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
