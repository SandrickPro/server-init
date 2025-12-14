#!/usr/bin/env python3
"""
Server Init - Iteration 273: Traffic Shaping Platform
Платформа формирования трафика

Функционал:
- Bandwidth Control - контроль пропускной способности
- Rate Limiting - ограничение скорости
- Traffic Prioritization - приоритизация трафика
- Queue Management - управление очередями
- Traffic Mirroring - зеркалирование трафика
- Fault Injection - внедрение сбоев
- Delay Injection - внедрение задержек
- Request Transformation - трансформация запросов
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from collections import deque
from enum import Enum
import uuid


class TrafficPriority(Enum):
    """Приоритет трафика"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


class ShapingAlgorithm(Enum):
    """Алгоритм формирования"""
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"
    WEIGHTED_FAIR = "weighted_fair"
    PRIORITY_QUEUE = "priority_queue"


class FaultType(Enum):
    """Тип сбоя"""
    ABORT = "abort"
    DELAY = "delay"
    TIMEOUT = "timeout"
    ERROR = "error"


class QueueState(Enum):
    """Состояние очереди"""
    ACTIVE = "active"
    PAUSED = "paused"
    DRAINING = "draining"
    FULL = "full"


@dataclass
class BandwidthLimit:
    """Ограничение пропускной способности"""
    limit_id: str
    name: str
    
    # Limits
    bytes_per_second: int = 1000000  # 1 MB/s
    burst_size: int = 100000  # 100 KB burst
    
    # Current
    current_tokens: float = 0
    last_refill: datetime = field(default_factory=datetime.now)
    
    # Stats
    bytes_allowed: int = 0
    bytes_throttled: int = 0


@dataclass
class RateLimitConfig:
    """Конфигурация ограничения скорости"""
    config_id: str
    name: str
    
    # Requests
    requests_per_second: int = 100
    burst_size: int = 200
    
    # Current
    current_tokens: float = 0
    last_refill: datetime = field(default_factory=datetime.now)
    
    # Stats
    requests_allowed: int = 0
    requests_rejected: int = 0


@dataclass
class PriorityQueue:
    """Приоритетная очередь"""
    queue_id: str
    name: str
    
    # Priority
    priority: TrafficPriority = TrafficPriority.NORMAL
    
    # Queue
    max_size: int = 1000
    items: deque = field(default_factory=deque)
    
    # State
    state: QueueState = QueueState.ACTIVE
    
    # Stats
    enqueued: int = 0
    dequeued: int = 0
    dropped: int = 0


@dataclass
class QueuedRequest:
    """Запрос в очереди"""
    request_id: str
    
    # Request info
    path: str = "/"
    method: str = "GET"
    
    # Priority
    priority: TrafficPriority = TrafficPriority.NORMAL
    
    # Size
    size_bytes: int = 0
    
    # Timing
    enqueued_at: datetime = field(default_factory=datetime.now)
    
    # Headers
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class MirrorConfig:
    """Конфигурация зеркалирования"""
    config_id: str
    name: str
    
    # Source
    source_service: str = ""
    
    # Mirror target
    mirror_service: str = ""
    
    # Percentage
    mirror_percentage: float = 100.0
    
    # Active
    active: bool = True
    
    # Stats
    mirrored_count: int = 0


@dataclass
class FaultConfig:
    """Конфигурация внедрения сбоев"""
    config_id: str
    name: str
    
    # Target
    target_service: str = ""
    target_path: str = "*"
    
    # Fault type
    fault_type: FaultType = FaultType.DELAY
    
    # Delay settings
    delay_ms: int = 1000
    delay_variance_ms: int = 100
    
    # Abort settings
    abort_code: int = 500
    abort_message: str = "Injected fault"
    
    # Percentage
    fault_percentage: float = 10.0
    
    # Active
    active: bool = True
    
    # Stats
    faults_injected: int = 0


@dataclass
class TransformRule:
    """Правило трансформации"""
    rule_id: str
    name: str
    
    # Match
    match_path: str = "*"
    match_method: str = "*"
    
    # Header transformations
    add_headers: Dict[str, str] = field(default_factory=dict)
    remove_headers: List[str] = field(default_factory=list)
    
    # Path rewrite
    path_rewrite: Optional[str] = None
    
    # Active
    active: bool = True


@dataclass
class TrafficPolicy:
    """Политика трафика"""
    policy_id: str
    name: str
    
    # Service
    service_name: str = ""
    
    # Bandwidth
    bandwidth_limit: Optional[BandwidthLimit] = None
    
    # Rate limit
    rate_limit: Optional[RateLimitConfig] = None
    
    # Priority
    default_priority: TrafficPriority = TrafficPriority.NORMAL
    
    # Active
    active: bool = True


class TrafficShapingManager:
    """Менеджер формирования трафика"""
    
    def __init__(self):
        self.policies: Dict[str, TrafficPolicy] = {}
        self.queues: Dict[TrafficPriority, PriorityQueue] = {}
        self.mirrors: Dict[str, MirrorConfig] = {}
        self.faults: Dict[str, FaultConfig] = {}
        self.transforms: Dict[str, TransformRule] = {}
        
        # Initialize priority queues
        self._init_queues()
        
    def _init_queues(self):
        """Инициализация очередей"""
        for priority in TrafficPriority:
            queue = PriorityQueue(
                queue_id=f"queue_{uuid.uuid4().hex[:8]}",
                name=f"{priority.name.lower()}_queue",
                priority=priority,
                max_size=1000 // priority.value
            )
            self.queues[priority] = queue
            
    def create_policy(self, name: str,
                     service_name: str,
                     rps: int = 100,
                     bandwidth_mbps: float = 10) -> TrafficPolicy:
        """Создание политики трафика"""
        bandwidth = BandwidthLimit(
            limit_id=f"bw_{uuid.uuid4().hex[:8]}",
            name=f"{name}_bandwidth",
            bytes_per_second=int(bandwidth_mbps * 1000000),
            burst_size=int(bandwidth_mbps * 100000)
        )
        bandwidth.current_tokens = float(bandwidth.burst_size)
        
        rate_limit = RateLimitConfig(
            config_id=f"rl_{uuid.uuid4().hex[:8]}",
            name=f"{name}_rate_limit",
            requests_per_second=rps,
            burst_size=rps * 2
        )
        rate_limit.current_tokens = float(rate_limit.burst_size)
        
        policy = TrafficPolicy(
            policy_id=f"policy_{uuid.uuid4().hex[:8]}",
            name=name,
            service_name=service_name,
            bandwidth_limit=bandwidth,
            rate_limit=rate_limit
        )
        
        self.policies[name] = policy
        return policy
        
    def setup_mirror(self, name: str,
                    source: str,
                    mirror_target: str,
                    percentage: float = 100.0) -> MirrorConfig:
        """Настройка зеркалирования"""
        mirror = MirrorConfig(
            config_id=f"mirror_{uuid.uuid4().hex[:8]}",
            name=name,
            source_service=source,
            mirror_service=mirror_target,
            mirror_percentage=percentage
        )
        
        self.mirrors[name] = mirror
        return mirror
        
    def setup_fault(self, name: str,
                   target_service: str,
                   fault_type: FaultType,
                   percentage: float = 10.0,
                   delay_ms: int = 1000,
                   abort_code: int = 500) -> FaultConfig:
        """Настройка внедрения сбоев"""
        fault = FaultConfig(
            config_id=f"fault_{uuid.uuid4().hex[:8]}",
            name=name,
            target_service=target_service,
            fault_type=fault_type,
            fault_percentage=percentage,
            delay_ms=delay_ms,
            abort_code=abort_code
        )
        
        self.faults[name] = fault
        return fault
        
    def add_transform(self, name: str,
                     match_path: str = "*",
                     add_headers: Dict[str, str] = None,
                     remove_headers: List[str] = None) -> TransformRule:
        """Добавление трансформации"""
        rule = TransformRule(
            rule_id=f"transform_{uuid.uuid4().hex[:8]}",
            name=name,
            match_path=match_path,
            add_headers=add_headers or {},
            remove_headers=remove_headers or []
        )
        
        self.transforms[name] = rule
        return rule
        
    def _refill_tokens(self, limiter, rate_per_second: float, max_tokens: float):
        """Пополнение токенов"""
        now = datetime.now()
        elapsed = (now - limiter.last_refill).total_seconds()
        limiter.last_refill = now
        
        tokens_to_add = elapsed * rate_per_second
        limiter.current_tokens = min(max_tokens, limiter.current_tokens + tokens_to_add)
        
    def check_rate_limit(self, policy_name: str) -> bool:
        """Проверка ограничения скорости"""
        policy = self.policies.get(policy_name)
        if not policy or not policy.rate_limit:
            return True
            
        rl = policy.rate_limit
        
        # Refill tokens
        self._refill_tokens(rl, rl.requests_per_second, rl.burst_size)
        
        if rl.current_tokens >= 1:
            rl.current_tokens -= 1
            rl.requests_allowed += 1
            return True
        else:
            rl.requests_rejected += 1
            return False
            
    def check_bandwidth(self, policy_name: str, size_bytes: int) -> bool:
        """Проверка пропускной способности"""
        policy = self.policies.get(policy_name)
        if not policy or not policy.bandwidth_limit:
            return True
            
        bw = policy.bandwidth_limit
        
        # Refill tokens
        self._refill_tokens(bw, bw.bytes_per_second, bw.burst_size)
        
        if bw.current_tokens >= size_bytes:
            bw.current_tokens -= size_bytes
            bw.bytes_allowed += size_bytes
            return True
        else:
            bw.bytes_throttled += size_bytes
            return False
            
    def enqueue_request(self, request: QueuedRequest) -> bool:
        """Добавление запроса в очередь"""
        queue = self.queues.get(request.priority)
        if not queue:
            return False
            
        if queue.state != QueueState.ACTIVE:
            return False
            
        if len(queue.items) >= queue.max_size:
            queue.dropped += 1
            return False
            
        queue.items.append(request)
        queue.enqueued += 1
        return True
        
    def dequeue_request(self) -> Optional[QueuedRequest]:
        """Извлечение запроса из очереди"""
        # Process by priority
        for priority in TrafficPriority:
            queue = self.queues.get(priority)
            if queue and queue.items:
                request = queue.items.popleft()
                queue.dequeued += 1
                return request
                
        return None
        
    async def process_request(self, policy_name: str,
                             request: QueuedRequest) -> Dict[str, Any]:
        """Обработка запроса"""
        result = {
            "allowed": True,
            "mirrored": False,
            "fault_injected": False,
            "transformed": False,
            "delay_ms": 0
        }
        
        # Check rate limit
        if not self.check_rate_limit(policy_name):
            result["allowed"] = False
            result["reason"] = "rate_limited"
            return result
            
        # Check bandwidth
        if not self.check_bandwidth(policy_name, request.size_bytes):
            result["allowed"] = False
            result["reason"] = "bandwidth_exceeded"
            return result
            
        # Check faults
        policy = self.policies.get(policy_name)
        if policy:
            for fault in self.faults.values():
                if fault.active and fault.target_service == policy.service_name:
                    if random.random() * 100 < fault.fault_percentage:
                        result["fault_injected"] = True
                        fault.faults_injected += 1
                        
                        if fault.fault_type == FaultType.DELAY:
                            delay = fault.delay_ms + random.randint(
                                -fault.delay_variance_ms, 
                                fault.delay_variance_ms
                            )
                            result["delay_ms"] = max(0, delay)
                            await asyncio.sleep(delay / 1000)
                        elif fault.fault_type == FaultType.ABORT:
                            result["allowed"] = False
                            result["abort_code"] = fault.abort_code
                            return result
                            
        # Check mirrors
        if policy:
            for mirror in self.mirrors.values():
                if mirror.active and mirror.source_service == policy.service_name:
                    if random.random() * 100 < mirror.mirror_percentage:
                        result["mirrored"] = True
                        mirror.mirrored_count += 1
                        
        # Apply transforms
        for transform in self.transforms.values():
            if transform.active:
                if transform.match_path == "*" or request.path.startswith(transform.match_path):
                    request.headers.update(transform.add_headers)
                    for header in transform.remove_headers:
                        request.headers.pop(header, None)
                    result["transformed"] = True
                    
        return result
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_enqueued = sum(q.enqueued for q in self.queues.values())
        total_dequeued = sum(q.dequeued for q in self.queues.values())
        total_dropped = sum(q.dropped for q in self.queues.values())
        
        total_requests_allowed = sum(
            p.rate_limit.requests_allowed for p in self.policies.values()
            if p.rate_limit
        )
        total_requests_rejected = sum(
            p.rate_limit.requests_rejected for p in self.policies.values()
            if p.rate_limit
        )
        
        total_faults = sum(f.faults_injected for f in self.faults.values())
        total_mirrored = sum(m.mirrored_count for m in self.mirrors.values())
        
        return {
            "policies": len(self.policies),
            "mirrors": len(self.mirrors),
            "faults": len(self.faults),
            "transforms": len(self.transforms),
            "total_enqueued": total_enqueued,
            "total_dequeued": total_dequeued,
            "total_dropped": total_dropped,
            "requests_allowed": total_requests_allowed,
            "requests_rejected": total_requests_rejected,
            "faults_injected": total_faults,
            "mirrored_requests": total_mirrored
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 273: Traffic Shaping Platform")
    print("=" * 60)
    
    manager = TrafficShapingManager()
    print("✓ Traffic Shaping Manager created")
    
    # Create policies
    print("\n📜 Creating Traffic Policies...")
    
    policies_config = [
        ("api-gateway", "api-gateway", 1000, 100),
        ("user-service", "user-service", 500, 50),
        ("order-service", "order-service", 300, 30),
        ("payment-service", "payment-service", 100, 10),
    ]
    
    for name, service, rps, bw in policies_config:
        policy = manager.create_policy(name, service, rps, bw)
        print(f"  📜 {name}: {rps} RPS, {bw} MB/s")
        
    # Setup mirrors
    print("\n🪞 Setting up Traffic Mirrors...")
    
    manager.setup_mirror("orders-shadow", "order-service", "orders-shadow-v2", 50.0)
    print(f"  🪞 orders-shadow: order-service -> orders-shadow-v2 (50%)")
    
    manager.setup_mirror("payments-audit", "payment-service", "audit-service", 100.0)
    print(f"  🪞 payments-audit: payment-service -> audit-service (100%)")
    
    # Setup faults
    print("\n💥 Setting up Fault Injection...")
    
    manager.setup_fault("delay-test", "user-service", FaultType.DELAY, 20.0, 500)
    print(f"  💥 delay-test: 500ms delay on user-service (20%)")
    
    manager.setup_fault("error-test", "order-service", FaultType.ABORT, 5.0, abort_code=503)
    print(f"  💥 error-test: 503 abort on order-service (5%)")
    
    # Add transforms
    print("\n🔄 Adding Transformations...")
    
    manager.add_transform("add-trace-id", "*", 
                         add_headers={"X-Trace-ID": "auto-generated"})
    print(f"  🔄 add-trace-id: Add X-Trace-ID header")
    
    manager.add_transform("api-version", "/api/v2", 
                         add_headers={"X-API-Version": "2.0"})
    print(f"  🔄 api-version: Add X-API-Version for /api/v2")
    
    # Simulate traffic
    print("\n🔄 Simulating Traffic...")
    
    results = {
        "allowed": 0,
        "rate_limited": 0,
        "fault_injected": 0,
        "mirrored": 0,
        "aborted": 0
    }
    
    for i in range(100):
        priority = random.choice(list(TrafficPriority))
        request = QueuedRequest(
            request_id=f"req_{i}",
            path=f"/api/v{random.randint(1, 2)}/resource",
            method=random.choice(["GET", "POST", "PUT"]),
            priority=priority,
            size_bytes=random.randint(100, 10000)
        )
        
        # Enqueue
        manager.enqueue_request(request)
        
        # Process
        policy_name = random.choice(list(manager.policies.keys()))
        result = await manager.process_request(policy_name, request)
        
        if result["allowed"]:
            results["allowed"] += 1
        else:
            if result.get("reason") == "rate_limited":
                results["rate_limited"] += 1
            elif result.get("abort_code"):
                results["aborted"] += 1
                
        if result.get("fault_injected"):
            results["fault_injected"] += 1
        if result.get("mirrored"):
            results["mirrored"] += 1
            
    print(f"\n  Allowed: {results['allowed']}")
    print(f"  Rate Limited: {results['rate_limited']}")
    print(f"  Faults Injected: {results['fault_injected']}")
    print(f"  Mirrored: {results['mirrored']}")
    print(f"  Aborted: {results['aborted']}")
    
    # Display policies
    print("\n📜 Traffic Policies:")
    
    print("\n  ┌─────────────────────┬───────────────────┬──────────────┬──────────────┬──────────────┐")
    print("  │ Policy              │ Service           │ RPS Limit    │ BW (MB/s)    │ Status       │")
    print("  ├─────────────────────┼───────────────────┼──────────────┼──────────────┼──────────────┤")
    
    for policy in manager.policies.values():
        name = policy.name[:19].ljust(19)
        service = policy.service_name[:17].ljust(17)
        rps = str(policy.rate_limit.requests_per_second if policy.rate_limit else "N/A")[:12].ljust(12)
        bw = f"{policy.bandwidth_limit.bytes_per_second / 1000000:.0f}" if policy.bandwidth_limit else "N/A"
        bw = bw[:12].ljust(12)
        status = "Active" if policy.active else "Inactive"
        status = status[:12].ljust(12)
        
        print(f"  │ {name} │ {service} │ {rps} │ {bw} │ {status} │")
        
    print("  └─────────────────────┴───────────────────┴──────────────┴──────────────┴──────────────┘")
    
    # Display queues
    print("\n📊 Priority Queues:")
    
    print("\n  ┌─────────────────┬──────────┬──────────┬──────────┬──────────┬──────────┐")
    print("  │ Priority        │ Max Size │ Enqueued │ Dequeued │ Dropped  │ State    │")
    print("  ├─────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤")
    
    for queue in manager.queues.values():
        priority = queue.priority.name[:15].ljust(15)
        max_size = str(queue.max_size)[:8].ljust(8)
        enqueued = str(queue.enqueued)[:8].ljust(8)
        dequeued = str(queue.dequeued)[:8].ljust(8)
        dropped = str(queue.dropped)[:8].ljust(8)
        state = queue.state.value[:8].ljust(8)
        
        print(f"  │ {priority} │ {max_size} │ {enqueued} │ {dequeued} │ {dropped} │ {state} │")
        
    print("  └─────────────────┴──────────┴──────────┴──────────┴──────────┴──────────┘")
    
    # Display mirrors
    print("\n🪞 Traffic Mirrors:")
    
    for mirror in manager.mirrors.values():
        print(f"\n  {mirror.name}:")
        print(f"    Source: {mirror.source_service} -> Mirror: {mirror.mirror_service}")
        print(f"    Percentage: {mirror.mirror_percentage}%, Mirrored: {mirror.mirrored_count}")
        
    # Display faults
    print("\n💥 Fault Injection:")
    
    for fault in manager.faults.values():
        type_icon = {
            FaultType.DELAY: "⏱️",
            FaultType.ABORT: "❌",
            FaultType.TIMEOUT: "⌛",
            FaultType.ERROR: "⚠️"
        }.get(fault.fault_type, "❓")
        
        print(f"\n  {type_icon} {fault.name}:")
        print(f"    Target: {fault.target_service}")
        print(f"    Type: {fault.fault_type.value}, Percentage: {fault.fault_percentage}%")
        if fault.fault_type == FaultType.DELAY:
            print(f"    Delay: {fault.delay_ms}ms ± {fault.delay_variance_ms}ms")
        elif fault.fault_type == FaultType.ABORT:
            print(f"    Abort Code: {fault.abort_code}")
        print(f"    Faults Injected: {fault.faults_injected}")
        
    # Rate limit stats
    print("\n📊 Rate Limit Statistics:")
    
    for policy in manager.policies.values():
        if policy.rate_limit:
            rl = policy.rate_limit
            total = rl.requests_allowed + rl.requests_rejected
            if total > 0:
                rate = rl.requests_allowed / total * 100
                print(f"\n  {policy.name}:")
                print(f"    Allowed: {rl.requests_allowed}, Rejected: {rl.requests_rejected}")
                bar = "█" * int(rate / 10) + "░" * (10 - int(rate / 10))
                print(f"    Success Rate: [{bar}] {rate:.1f}%")
                
    # Bandwidth stats
    print("\n📊 Bandwidth Statistics:")
    
    for policy in manager.policies.values():
        if policy.bandwidth_limit:
            bw = policy.bandwidth_limit
            allowed_mb = bw.bytes_allowed / 1000000
            throttled_mb = bw.bytes_throttled / 1000000
            print(f"\n  {policy.name}:")
            print(f"    Allowed: {allowed_mb:.2f} MB, Throttled: {throttled_mb:.2f} MB")
            
    # Priority distribution
    print("\n📊 Queue Distribution:")
    
    for priority, queue in manager.queues.items():
        bar = "█" * (queue.enqueued // 5) + "░" * (20 - queue.enqueued // 5)
        icon = {
            TrafficPriority.CRITICAL: "🔴",
            TrafficPriority.HIGH: "🟠",
            TrafficPriority.NORMAL: "🟡",
            TrafficPriority.LOW: "🟢",
            TrafficPriority.BACKGROUND: "🔵"
        }.get(priority, "⚪")
        print(f"  {icon} {priority.name:12s}: [{bar}] {queue.enqueued}")
        
    # Statistics
    print("\n📊 Manager Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Policies: {stats['policies']}")
    print(f"  Mirrors: {stats['mirrors']}")
    print(f"  Faults: {stats['faults']}")
    print(f"  Transforms: {stats['transforms']}")
    print(f"  Requests Allowed: {stats['requests_allowed']}")
    print(f"  Requests Rejected: {stats['requests_rejected']}")
    print(f"  Faults Injected: {stats['faults_injected']}")
    print(f"  Mirrored: {stats['mirrored_requests']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Traffic Shaping Dashboard                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Policies:                      {stats['policies']:>12}                        │")
    print(f"│ Requests Allowed:              {stats['requests_allowed']:>12}                        │")
    print(f"│ Requests Rejected:             {stats['requests_rejected']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Faults Injected:               {stats['faults_injected']:>12}                        │")
    print(f"│ Mirrored Requests:             {stats['mirrored_requests']:>12}                        │")
    print(f"│ Queue Dropped:                 {stats['total_dropped']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Traffic Shaping Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
