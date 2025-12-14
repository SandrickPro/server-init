#!/usr/bin/env python3
"""
Server Init - Iteration 255: Idempotency Manager Platform
Платформа управления идемпотентностью операций

Функционал:
- Idempotency Key Management - управление ключами
- Request Deduplication - дедупликация запросов
- Response Caching - кэширование ответов
- TTL Management - управление временем жизни
- Conflict Detection - обнаружение конфликтов
- Key Generation - генерация ключей
- Audit Trail - аудит
- Metrics - метрики
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid
import hashlib
import json


class IdempotencyState(Enum):
    """Состояние идемпотентности"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class KeySource(Enum):
    """Источник ключа"""
    CLIENT = "client"
    GENERATED = "generated"
    COMPUTED = "computed"


class ConflictResolution(Enum):
    """Разрешение конфликтов"""
    REJECT = "reject"
    RETURN_CACHED = "return_cached"
    WAIT = "wait"
    OVERRIDE = "override"


class OperationType(Enum):
    """Тип операции"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    TRANSFER = "transfer"
    PROCESS = "process"


@dataclass
class IdempotencyKey:
    """Ключ идемпотентности"""
    key_id: str
    key_value: str
    
    # Source
    source: KeySource = KeySource.CLIENT
    
    # State
    state: IdempotencyState = IdempotencyState.PENDING
    
    # Operation
    operation_type: OperationType = OperationType.CREATE
    resource_type: str = ""
    resource_id: str = ""
    
    # Request
    request_hash: str = ""
    request_payload: Any = None
    
    # Response
    response_payload: Any = None
    response_code: int = 0
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=24))
    
    # Metadata
    client_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IdempotencyConfig:
    """Конфигурация идемпотентности"""
    config_id: str
    resource_type: str
    
    # TTL
    default_ttl_hours: int = 24
    max_ttl_hours: int = 168  # 7 days
    
    # Conflict
    conflict_resolution: ConflictResolution = ConflictResolution.RETURN_CACHED
    
    # Key generation
    key_fields: List[str] = field(default_factory=list)
    include_timestamp: bool = False
    
    # Options
    cache_failures: bool = False
    require_key: bool = True


@dataclass
class ConflictRecord:
    """Запись о конфликте"""
    conflict_id: str
    key_value: str
    
    # Requests
    original_request_hash: str = ""
    conflicting_request_hash: str = ""
    
    # Resolution
    resolution: ConflictResolution = ConflictResolution.REJECT
    resolved: bool = False
    
    # Time
    detected_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


@dataclass
class IdempotencyMetrics:
    """Метрики идемпотентности"""
    resource_type: str
    
    # Counters
    total_requests: int = 0
    duplicate_requests: int = 0
    new_requests: int = 0
    conflicts: int = 0
    
    # Cache
    cache_hits: int = 0
    cache_misses: int = 0
    
    # Latency
    total_latency_ms: float = 0
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)


class IdempotencyManager:
    """Менеджер идемпотентности"""
    
    def __init__(self):
        self.keys: Dict[str, IdempotencyKey] = {}
        self.configs: Dict[str, IdempotencyConfig] = {}
        self.conflicts: List[ConflictRecord] = []
        self.metrics: Dict[str, IdempotencyMetrics] = {}
        
        # Processing lock
        self._processing: Dict[str, asyncio.Lock] = {}
        
    def create_config(self, resource_type: str,
                     default_ttl_hours: int = 24,
                     conflict_resolution: ConflictResolution = ConflictResolution.RETURN_CACHED,
                     key_fields: List[str] = None) -> IdempotencyConfig:
        """Создание конфигурации"""
        config = IdempotencyConfig(
            config_id=f"cfg_{uuid.uuid4().hex[:8]}",
            resource_type=resource_type,
            default_ttl_hours=default_ttl_hours,
            conflict_resolution=conflict_resolution,
            key_fields=key_fields or []
        )
        
        self.configs[resource_type] = config
        self.metrics[resource_type] = IdempotencyMetrics(resource_type=resource_type)
        
        return config
        
    def generate_key(self, resource_type: str,
                    payload: Dict[str, Any]) -> str:
        """Генерация ключа идемпотентности"""
        config = self.configs.get(resource_type)
        
        if config and config.key_fields:
            # Use specific fields
            key_data = {f: payload.get(f) for f in config.key_fields}
        else:
            # Use entire payload
            key_data = payload
            
        if config and config.include_timestamp:
            key_data["_ts"] = datetime.now().isoformat()
            
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_str.encode()).hexdigest()[:32]
        
    def compute_request_hash(self, payload: Any) -> str:
        """Вычисление хэша запроса"""
        payload_str = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.md5(payload_str.encode()).hexdigest()
        
    async def check_idempotency(self, key_value: str, resource_type: str,
                               payload: Any) -> Optional[IdempotencyKey]:
        """Проверка идемпотентности"""
        config = self.configs.get(resource_type)
        metrics = self.metrics.get(resource_type)
        
        if metrics:
            metrics.total_requests += 1
            
        existing = self.keys.get(key_value)
        
        if existing:
            # Check expiration
            if existing.expires_at < datetime.now():
                existing.state = IdempotencyState.EXPIRED
                del self.keys[key_value]
                
                if metrics:
                    metrics.cache_misses += 1
                    
                return None
                
            # Check request hash
            request_hash = self.compute_request_hash(payload)
            
            if existing.request_hash != request_hash:
                # Conflict - different payload, same key
                self._record_conflict(key_value, existing.request_hash, request_hash, config)
                
                if config and config.conflict_resolution == ConflictResolution.REJECT:
                    if metrics:
                        metrics.conflicts += 1
                    raise ValueError(f"Idempotency conflict for key {key_value}")
                    
            if metrics:
                metrics.duplicate_requests += 1
                metrics.cache_hits += 1
                
            return existing
            
        if metrics:
            metrics.cache_misses += 1
            metrics.new_requests += 1
            
        return None
        
    async def start_operation(self, key_value: str, resource_type: str,
                             operation_type: OperationType,
                             payload: Any, client_id: str = "",
                             source: KeySource = KeySource.CLIENT) -> IdempotencyKey:
        """Начало операции"""
        config = self.configs.get(resource_type)
        ttl = config.default_ttl_hours if config else 24
        
        key = IdempotencyKey(
            key_id=f"idem_{uuid.uuid4().hex[:8]}",
            key_value=key_value,
            source=source,
            operation_type=operation_type,
            resource_type=resource_type,
            request_hash=self.compute_request_hash(payload),
            request_payload=payload,
            client_id=client_id,
            expires_at=datetime.now() + timedelta(hours=ttl)
        )
        
        key.state = IdempotencyState.PROCESSING
        self.keys[key_value] = key
        
        # Create lock
        self._processing[key_value] = asyncio.Lock()
        
        return key
        
    async def complete_operation(self, key_value: str,
                                response: Any, response_code: int = 200) -> bool:
        """Завершение операции"""
        key = self.keys.get(key_value)
        if not key:
            return False
            
        key.state = IdempotencyState.COMPLETED
        key.response_payload = response
        key.response_code = response_code
        key.processed_at = datetime.now()
        
        # Release lock
        if key_value in self._processing:
            del self._processing[key_value]
            
        return True
        
    async def fail_operation(self, key_value: str, error: str,
                            cache_failure: bool = False) -> bool:
        """Провал операции"""
        key = self.keys.get(key_value)
        if not key:
            return False
            
        config = self.configs.get(key.resource_type)
        
        if cache_failure or (config and config.cache_failures):
            key.state = IdempotencyState.FAILED
            key.response_payload = {"error": error}
            key.response_code = 500
            key.processed_at = datetime.now()
        else:
            # Remove key to allow retry
            del self.keys[key_value]
            
        # Release lock
        if key_value in self._processing:
            del self._processing[key_value]
            
        return True
        
    def _record_conflict(self, key_value: str, original_hash: str,
                        conflicting_hash: str,
                        config: Optional[IdempotencyConfig]):
        """Запись конфликта"""
        conflict = ConflictRecord(
            conflict_id=f"conf_{uuid.uuid4().hex[:8]}",
            key_value=key_value,
            original_request_hash=original_hash,
            conflicting_request_hash=conflicting_hash,
            resolution=config.conflict_resolution if config else ConflictResolution.REJECT
        )
        
        self.conflicts.append(conflict)
        
    async def execute_idempotent(self, key_value: str, resource_type: str,
                                operation_type: OperationType,
                                payload: Any,
                                operation: Callable,
                                client_id: str = "") -> Dict[str, Any]:
        """Выполнение идемпотентной операции"""
        start_time = datetime.now()
        metrics = self.metrics.get(resource_type)
        
        # Check for existing result
        existing = await self.check_idempotency(key_value, resource_type, payload)
        
        if existing and existing.state == IdempotencyState.COMPLETED:
            return {
                "cached": True,
                "key": existing.key_value,
                "response": existing.response_payload,
                "code": existing.response_code
            }
            
        # Start new operation
        key = await self.start_operation(
            key_value, resource_type, operation_type,
            payload, client_id
        )
        
        try:
            # Execute operation
            result = await operation(payload)
            
            await self.complete_operation(key_value, result, 200)
            
            if metrics:
                metrics.total_latency_ms += (datetime.now() - start_time).total_seconds() * 1000
                
            return {
                "cached": False,
                "key": key_value,
                "response": result,
                "code": 200
            }
            
        except Exception as e:
            await self.fail_operation(key_value, str(e))
            raise
            
    def cleanup_expired(self) -> int:
        """Очистка истёкших ключей"""
        now = datetime.now()
        expired_keys = [
            k for k, v in self.keys.items()
            if v.expires_at < now
        ]
        
        for key in expired_keys:
            del self.keys[key]
            
        return len(expired_keys)
        
    def get_key(self, key_value: str) -> Optional[IdempotencyKey]:
        """Получение ключа"""
        return self.keys.get(key_value)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        state_counts: Dict[IdempotencyState, int] = {}
        for key in self.keys.values():
            state_counts[key.state] = state_counts.get(key.state, 0) + 1
            
        total_requests = sum(m.total_requests for m in self.metrics.values())
        total_duplicates = sum(m.duplicate_requests for m in self.metrics.values())
        cache_hits = sum(m.cache_hits for m in self.metrics.values())
        cache_misses = sum(m.cache_misses for m in self.metrics.values())
        
        return {
            "keys_total": len(self.keys),
            "keys_pending": state_counts.get(IdempotencyState.PENDING, 0),
            "keys_processing": state_counts.get(IdempotencyState.PROCESSING, 0),
            "keys_completed": state_counts.get(IdempotencyState.COMPLETED, 0),
            "keys_failed": state_counts.get(IdempotencyState.FAILED, 0),
            "configs_count": len(self.configs),
            "total_requests": total_requests,
            "duplicate_requests": total_duplicates,
            "duplicate_rate": (total_duplicates / total_requests * 100) if total_requests > 0 else 0,
            "cache_hit_rate": (cache_hits / (cache_hits + cache_misses) * 100) if (cache_hits + cache_misses) > 0 else 0,
            "conflicts_total": len(self.conflicts)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 255: Idempotency Manager Platform")
    print("=" * 60)
    
    manager = IdempotencyManager()
    print("✓ Idempotency Manager created")
    
    # Create configurations
    print("\n⚙️ Creating Configurations...")
    
    configs_data = [
        ("payment", 24, ConflictResolution.RETURN_CACHED, ["amount", "currency", "recipient"]),
        ("order", 48, ConflictResolution.REJECT, ["customer_id", "items"]),
        ("transfer", 72, ConflictResolution.WAIT, ["from_account", "to_account", "amount"]),
        ("notification", 1, ConflictResolution.OVERRIDE, []),
    ]
    
    for resource_type, ttl, resolution, fields in configs_data:
        config = manager.create_config(resource_type, ttl, resolution, fields)
        print(f"  ⚙️ {resource_type}: TTL={ttl}h, resolution={resolution.value}")
        
    # Simulate operations
    print("\n💳 Executing Idempotent Operations...")
    
    # Define operation handler
    async def process_payment(payload):
        await asyncio.sleep(random.uniform(0.01, 0.1))
        return {
            "payment_id": f"PAY_{uuid.uuid4().hex[:8]}",
            "status": "completed",
            "amount": payload.get("amount")
        }
        
    # First payment request
    payment_key = "PAY_KEY_001"
    payment_payload = {"amount": 99.99, "currency": "USD", "recipient": "ACCT_001"}
    
    result1 = await manager.execute_idempotent(
        payment_key, "payment",
        OperationType.TRANSFER,
        payment_payload,
        process_payment,
        "client_001"
    )
    print(f"  💳 Payment 1: cached={result1['cached']}, payment_id={result1['response'].get('payment_id', 'N/A')}")
    
    # Duplicate request (same key)
    result2 = await manager.execute_idempotent(
        payment_key, "payment",
        OperationType.TRANSFER,
        payment_payload,
        process_payment,
        "client_001"
    )
    print(f"  💳 Payment 2 (dup): cached={result2['cached']}, same result={result1['response'] == result2['response']}")
    
    # Different payment
    async def process_order(payload):
        await asyncio.sleep(random.uniform(0.01, 0.05))
        return {"order_id": f"ORD_{uuid.uuid4().hex[:8]}", "status": "created"}
        
    order_key = "ORD_KEY_001"
    order_payload = {"customer_id": "CUST_001", "items": ["item1", "item2"]}
    
    result3 = await manager.execute_idempotent(
        order_key, "order",
        OperationType.CREATE,
        order_payload,
        process_order,
        "client_002"
    )
    print(f"  📦 Order: cached={result3['cached']}, order_id={result3['response'].get('order_id', 'N/A')}")
    
    # Generate keys
    print("\n🔑 Key Generation:")
    
    test_payloads = [
        {"amount": 100, "currency": "EUR", "recipient": "ACC_002"},
        {"amount": 100, "currency": "EUR", "recipient": "ACC_002"},  # Same
        {"amount": 100, "currency": "USD", "recipient": "ACC_002"},  # Different currency
    ]
    
    for i, payload in enumerate(test_payloads):
        key = manager.generate_key("payment", payload)
        print(f"  🔑 Payload {i+1}: {key}")
        
    # Display keys
    print("\n🗝️ Idempotency Keys:")
    
    print("\n  ┌──────────────────┬───────────────┬───────────────┬───────────┬──────────┐")
    print("  │ Key              │ Resource      │ Operation     │ State     │ TTL      │")
    print("  ├──────────────────┼───────────────┼───────────────┼───────────┼──────────┤")
    
    for key in manager.keys.values():
        key_val = key.key_value[:16].ljust(16)
        resource = key.resource_type[:13].ljust(13)
        operation = key.operation_type.value[:13].ljust(13)
        state = key.state.value[:9].ljust(9)
        ttl = f"{(key.expires_at - datetime.now()).total_seconds() / 3600:.0f}h"[:8].ljust(8)
        
        print(f"  │ {key_val} │ {resource} │ {operation} │ {state} │ {ttl} │")
        
    print("  └──────────────────┴───────────────┴───────────────┴───────────┴──────────┘")
    
    # Conflict test
    print("\n⚠️ Conflict Detection Test...")
    
    try:
        # Same key, different payload for order (REJECT policy)
        different_payload = {"customer_id": "CUST_001", "items": ["item3"]}
        await manager.execute_idempotent(
            order_key, "order",
            OperationType.CREATE,
            different_payload,
            process_order,
            "client_002"
        )
    except ValueError as e:
        print(f"  ⚠️ Conflict detected: {e}")
        
    # Display configurations
    print("\n⚙️ Configurations:")
    
    print("\n  ┌───────────────┬──────────┬─────────────────┬───────────────────────────┐")
    print("  │ Resource      │ TTL      │ Conflict        │ Key Fields                │")
    print("  ├───────────────┼──────────┼─────────────────┼───────────────────────────┤")
    
    for config in manager.configs.values():
        resource = config.resource_type[:13].ljust(13)
        ttl = f"{config.default_ttl_hours}h"[:8].ljust(8)
        conflict = config.conflict_resolution.value[:15].ljust(15)
        fields = ", ".join(config.key_fields[:3])[:25].ljust(25)
        
        print(f"  │ {resource} │ {ttl} │ {conflict} │ {fields} │")
        
    print("  └───────────────┴──────────┴─────────────────┴───────────────────────────┘")
    
    # Metrics by resource
    print("\n📊 Metrics by Resource:")
    
    print("\n  ┌───────────────┬──────────┬──────────┬──────────┬──────────┐")
    print("  │ Resource      │ Total    │ Duplicate│ Cache Hit│ Conflicts│")
    print("  ├───────────────┼──────────┼──────────┼──────────┼──────────┤")
    
    for resource_type, metrics in manager.metrics.items():
        resource = resource_type[:13].ljust(13)
        total = str(metrics.total_requests)[:8].ljust(8)
        dup = str(metrics.duplicate_requests)[:8].ljust(8)
        hits = str(metrics.cache_hits)[:8].ljust(8)
        conflicts = str(metrics.conflicts)[:8].ljust(8)
        
        print(f"  │ {resource} │ {total} │ {dup} │ {hits} │ {conflicts} │")
        
    print("  └───────────────┴──────────┴──────────┴──────────┴──────────┘")
    
    # State distribution
    print("\n📊 Key State Distribution:")
    
    state_counts: Dict[IdempotencyState, int] = {}
    for key in manager.keys.values():
        state_counts[key.state] = state_counts.get(key.state, 0) + 1
        
    for state in IdempotencyState:
        count = state_counts.get(state, 0)
        bar = "█" * count + "░" * (10 - count)
        icon = {
            IdempotencyState.PENDING: "○",
            IdempotencyState.PROCESSING: "◐",
            IdempotencyState.COMPLETED: "✓",
            IdempotencyState.FAILED: "✗",
            IdempotencyState.EXPIRED: "⏰"
        }.get(state, "?")
        print(f"  {icon} {state.value:12s} [{bar}] {count}")
        
    # Statistics
    print("\n📊 Idempotency Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Keys: {stats['keys_total']} (completed: {stats['keys_completed']})")
    print(f"  Configurations: {stats['configs_count']}")
    
    print(f"\n  Total Requests: {stats['total_requests']}")
    print(f"  Duplicate Requests: {stats['duplicate_requests']}")
    print(f"  Duplicate Rate: {stats['duplicate_rate']:.1f}%")
    
    print(f"\n  Cache Hit Rate: {stats['cache_hit_rate']:.1f}%")
    print(f"  Conflicts: {stats['conflicts_total']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Idempotency Manager Dashboard                     │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Keys Total:                    {stats['keys_total']:>12}                        │")
    print(f"│ Keys Completed:                {stats['keys_completed']:>12}                        │")
    print(f"│ Configurations:                {stats['configs_count']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Duplicate Rate:                {stats['duplicate_rate']:>11.1f}%                        │")
    print(f"│ Cache Hit Rate:                {stats['cache_hit_rate']:>11.1f}%                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Idempotency Manager Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
