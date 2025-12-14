#!/usr/bin/env python3
"""
Server Init - Iteration 256: Retry Policy Manager Platform
Платформа управления политиками повторных попыток

Функционал:
- Policy Definition - определение политик
- Retry Strategies - стратегии повторов
- Backoff Algorithms - алгоритмы отступа
- Jitter Support - поддержка jitter
- Circuit Integration - интеграция с circuit breaker
- Context Propagation - распространение контекста
- Metrics Collection - сбор метрик
- Error Classification - классификация ошибок
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set, Awaitable
from enum import Enum
import uuid
import math


class RetryStrategy(Enum):
    """Стратегия повторов"""
    FIXED = "fixed"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    FIBONACCI = "fibonacci"
    DECORRELATED_JITTER = "decorrelated_jitter"


class ErrorType(Enum):
    """Тип ошибки"""
    RETRYABLE = "retryable"
    NON_RETRYABLE = "non_retryable"
    TRANSIENT = "transient"
    TIMEOUT = "timeout"
    CIRCUIT_OPEN = "circuit_open"


class RetryState(Enum):
    """Состояние повтора"""
    PENDING = "pending"
    EXECUTING = "executing"
    SUCCESS = "success"
    FAILED = "failed"
    EXHAUSTED = "exhausted"


class JitterType(Enum):
    """Тип jitter"""
    NONE = "none"
    FULL = "full"
    EQUAL = "equal"
    DECORRELATED = "decorrelated"


@dataclass
class RetryPolicy:
    """Политика повторов"""
    policy_id: str
    name: str
    
    # Strategy
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    
    # Limits
    max_retries: int = 3
    max_delay_ms: int = 60000  # 1 minute
    
    # Timing
    initial_delay_ms: int = 1000
    multiplier: float = 2.0
    
    # Jitter
    jitter_type: JitterType = JitterType.FULL
    jitter_factor: float = 0.5
    
    # Error handling
    retryable_errors: Set[str] = field(default_factory=set)
    non_retryable_errors: Set[str] = field(default_factory=set)
    
    # Circuit breaker
    circuit_breaker_enabled: bool = False
    circuit_breaker_threshold: int = 5
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RetryAttempt:
    """Попытка повтора"""
    attempt_id: str
    execution_id: str
    
    # Attempt info
    attempt_number: int = 0
    
    # Timing
    scheduled_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    delay_ms: int = 0
    
    # Result
    state: RetryState = RetryState.PENDING
    error: str = ""
    error_type: ErrorType = ErrorType.RETRYABLE
    
    # Response
    response: Any = None


@dataclass
class RetryExecution:
    """Выполнение с повторами"""
    execution_id: str
    policy_id: str
    
    # Operation
    operation_name: str = ""
    
    # State
    state: RetryState = RetryState.PENDING
    
    # Attempts
    attempts: List[RetryAttempt] = field(default_factory=list)
    current_attempt: int = 0
    
    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    total_delay_ms: int = 0
    
    # Result
    final_result: Any = None
    final_error: str = ""
    
    # Context
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetryMetrics:
    """Метрики повторов"""
    policy_name: str
    
    # Counters
    total_executions: int = 0
    successful_first_try: int = 0
    successful_after_retry: int = 0
    exhausted: int = 0
    
    # Attempts
    total_attempts: int = 0
    
    # Timing
    total_delay_ms: int = 0
    
    # Errors
    errors_by_type: Dict[str, int] = field(default_factory=dict)


class RetryPolicyManager:
    """Менеджер политик повторов"""
    
    def __init__(self):
        self.policies: Dict[str, RetryPolicy] = {}
        self.executions: Dict[str, RetryExecution] = {}
        self.metrics: Dict[str, RetryMetrics] = {}
        
        # Fibonacci cache
        self._fib_cache: Dict[int, int] = {0: 0, 1: 1}
        
    def create_policy(self, name: str,
                     strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
                     max_retries: int = 3,
                     initial_delay_ms: int = 1000,
                     max_delay_ms: int = 60000,
                     multiplier: float = 2.0,
                     jitter_type: JitterType = JitterType.FULL) -> RetryPolicy:
        """Создание политики повторов"""
        policy = RetryPolicy(
            policy_id=f"pol_{uuid.uuid4().hex[:8]}",
            name=name,
            strategy=strategy,
            max_retries=max_retries,
            initial_delay_ms=initial_delay_ms,
            max_delay_ms=max_delay_ms,
            multiplier=multiplier,
            jitter_type=jitter_type
        )
        
        self.policies[policy.policy_id] = policy
        self.metrics[name] = RetryMetrics(policy_name=name)
        
        return policy
        
    def calculate_delay(self, policy: RetryPolicy, attempt: int,
                       last_delay: int = 0) -> int:
        """Расчёт задержки для попытки"""
        base_delay = 0
        
        if policy.strategy == RetryStrategy.FIXED:
            base_delay = policy.initial_delay_ms
            
        elif policy.strategy == RetryStrategy.LINEAR:
            base_delay = policy.initial_delay_ms * (attempt + 1)
            
        elif policy.strategy == RetryStrategy.EXPONENTIAL:
            base_delay = int(policy.initial_delay_ms * (policy.multiplier ** attempt))
            
        elif policy.strategy == RetryStrategy.FIBONACCI:
            base_delay = policy.initial_delay_ms * self._fibonacci(attempt + 1)
            
        elif policy.strategy == RetryStrategy.DECORRELATED_JITTER:
            if last_delay == 0:
                last_delay = policy.initial_delay_ms
            base_delay = random.randint(
                policy.initial_delay_ms,
                int(last_delay * 3)
            )
            
        # Apply jitter
        delay = self._apply_jitter(base_delay, policy)
        
        # Cap at max delay
        return min(delay, policy.max_delay_ms)
        
    def _fibonacci(self, n: int) -> int:
        """Вычисление числа Фибоначчи"""
        if n in self._fib_cache:
            return self._fib_cache[n]
            
        self._fib_cache[n] = self._fibonacci(n - 1) + self._fibonacci(n - 2)
        return self._fib_cache[n]
        
    def _apply_jitter(self, delay: int, policy: RetryPolicy) -> int:
        """Применение jitter к задержке"""
        if policy.jitter_type == JitterType.NONE:
            return delay
            
        elif policy.jitter_type == JitterType.FULL:
            return random.randint(0, delay)
            
        elif policy.jitter_type == JitterType.EQUAL:
            half = delay // 2
            return half + random.randint(0, half)
            
        elif policy.jitter_type == JitterType.DECORRELATED:
            jitter_range = int(delay * policy.jitter_factor)
            return delay + random.randint(-jitter_range, jitter_range)
            
        return delay
        
    def classify_error(self, error: Exception, policy: RetryPolicy) -> ErrorType:
        """Классификация ошибки"""
        error_str = str(error).lower()
        error_class = type(error).__name__
        
        # Check explicit lists
        if error_class in policy.non_retryable_errors:
            return ErrorType.NON_RETRYABLE
            
        if error_class in policy.retryable_errors:
            return ErrorType.RETRYABLE
            
        # Heuristic classification
        if any(x in error_str for x in ["timeout", "timed out"]):
            return ErrorType.TIMEOUT
            
        if any(x in error_str for x in ["circuit", "breaker", "open"]):
            return ErrorType.CIRCUIT_OPEN
            
        if any(x in error_str for x in ["connection", "unavailable", "temporary"]):
            return ErrorType.TRANSIENT
            
        if any(x in error_str for x in ["permission", "forbidden", "invalid"]):
            return ErrorType.NON_RETRYABLE
            
        return ErrorType.RETRYABLE
        
    async def execute_with_retry(self, policy_name: str,
                                operation: Callable[..., Awaitable[Any]],
                                *args,
                                operation_name: str = "",
                                context: Dict[str, Any] = None,
                                **kwargs) -> Any:
        """Выполнение операции с повторами"""
        # Find policy
        policy = None
        for p in self.policies.values():
            if p.name == policy_name:
                policy = p
                break
                
        if not policy:
            raise ValueError(f"Policy {policy_name} not found")
            
        metrics = self.metrics.get(policy_name)
        if metrics:
            metrics.total_executions += 1
            
        # Create execution
        execution = RetryExecution(
            execution_id=f"exec_{uuid.uuid4().hex[:8]}",
            policy_id=policy.policy_id,
            operation_name=operation_name or operation.__name__,
            context=context or {}
        )
        
        self.executions[execution.execution_id] = execution
        execution.state = RetryState.EXECUTING
        
        last_delay = 0
        
        for attempt in range(policy.max_retries + 1):
            execution.current_attempt = attempt
            
            # Calculate delay (except first attempt)
            delay_ms = 0
            if attempt > 0:
                delay_ms = self.calculate_delay(policy, attempt - 1, last_delay)
                last_delay = delay_ms
                execution.total_delay_ms += delay_ms
                
                await asyncio.sleep(delay_ms / 1000)
                
            # Create attempt record
            retry_attempt = RetryAttempt(
                attempt_id=f"att_{uuid.uuid4().hex[:8]}",
                execution_id=execution.execution_id,
                attempt_number=attempt,
                delay_ms=delay_ms,
                started_at=datetime.now()
            )
            
            execution.attempts.append(retry_attempt)
            
            if metrics:
                metrics.total_attempts += 1
                
            try:
                # Execute operation
                result = await operation(*args, **kwargs)
                
                # Success
                retry_attempt.state = RetryState.SUCCESS
                retry_attempt.response = result
                retry_attempt.completed_at = datetime.now()
                
                execution.state = RetryState.SUCCESS
                execution.final_result = result
                execution.completed_at = datetime.now()
                
                if metrics:
                    if attempt == 0:
                        metrics.successful_first_try += 1
                    else:
                        metrics.successful_after_retry += 1
                    metrics.total_delay_ms += execution.total_delay_ms
                    
                return result
                
            except Exception as e:
                error_type = self.classify_error(e, policy)
                
                retry_attempt.state = RetryState.FAILED
                retry_attempt.error = str(e)
                retry_attempt.error_type = error_type
                retry_attempt.completed_at = datetime.now()
                
                if metrics:
                    metrics.errors_by_type[error_type.value] = metrics.errors_by_type.get(error_type.value, 0) + 1
                    
                # Check if should retry
                if error_type == ErrorType.NON_RETRYABLE:
                    execution.state = RetryState.FAILED
                    execution.final_error = str(e)
                    execution.completed_at = datetime.now()
                    raise
                    
                if attempt >= policy.max_retries:
                    execution.state = RetryState.EXHAUSTED
                    execution.final_error = str(e)
                    execution.completed_at = datetime.now()
                    
                    if metrics:
                        metrics.exhausted += 1
                        
                    raise
                    
        # Should not reach here
        raise RuntimeError("Unexpected end of retry loop")
        
    def get_execution(self, execution_id: str) -> Optional[RetryExecution]:
        """Получение выполнения"""
        return self.executions.get(execution_id)
        
    def get_policy_metrics(self, policy_name: str) -> Optional[RetryMetrics]:
        """Метрики политики"""
        return self.metrics.get(policy_name)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_executions = sum(m.total_executions for m in self.metrics.values())
        total_successful = sum(m.successful_first_try + m.successful_after_retry for m in self.metrics.values())
        total_exhausted = sum(m.exhausted for m in self.metrics.values())
        total_attempts = sum(m.total_attempts for m in self.metrics.values())
        
        return {
            "policies_count": len(self.policies),
            "total_executions": total_executions,
            "total_attempts": total_attempts,
            "avg_attempts_per_execution": total_attempts / max(1, total_executions),
            "success_rate": (total_successful / max(1, total_executions)) * 100,
            "exhausted_rate": (total_exhausted / max(1, total_executions)) * 100,
            "active_executions": sum(1 for e in self.executions.values() if e.state == RetryState.EXECUTING)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 256: Retry Policy Manager Platform")
    print("=" * 60)
    
    manager = RetryPolicyManager()
    print("✓ Retry Policy Manager created")
    
    # Create policies
    print("\n📋 Creating Retry Policies...")
    
    policies_data = [
        ("api-calls", RetryStrategy.EXPONENTIAL, 3, 1000, 30000, 2.0, JitterType.FULL),
        ("database", RetryStrategy.FIBONACCI, 5, 500, 60000, 1.0, JitterType.EQUAL),
        ("messaging", RetryStrategy.LINEAR, 3, 2000, 10000, 1.0, JitterType.NONE),
        ("external-service", RetryStrategy.DECORRELATED_JITTER, 4, 1000, 120000, 3.0, JitterType.DECORRELATED),
    ]
    
    policies = []
    for name, strategy, max_retries, initial, max_delay, mult, jitter in policies_data:
        policy = manager.create_policy(
            name, strategy, max_retries,
            initial, max_delay, mult, jitter
        )
        policies.append(policy)
        print(f"  📋 {name}: {strategy.value}, max={max_retries}, jitter={jitter.value}")
        
    # Calculate delays example
    print("\n⏱️ Delay Calculations (api-calls policy):")
    
    policy = policies[0]
    last_delay = 0
    for attempt in range(4):
        delay = manager.calculate_delay(policy, attempt, last_delay)
        last_delay = delay
        print(f"  Attempt {attempt + 1}: {delay}ms")
        
    # Define test operations
    attempt_counter = {"count": 0}
    
    async def flaky_operation():
        attempt_counter["count"] += 1
        await asyncio.sleep(random.uniform(0.01, 0.05))
        
        if attempt_counter["count"] < 3:
            raise ConnectionError("Connection timeout (simulated)")
        return {"status": "success", "attempt": attempt_counter["count"]}
        
    async def always_fail():
        await asyncio.sleep(0.01)
        raise ValueError("Invalid input (non-retryable)")
        
    async def always_succeed():
        await asyncio.sleep(0.01)
        return {"status": "ok"}
        
    # Execute operations
    print("\n🔄 Executing Operations with Retry...")
    
    # Flaky operation
    attempt_counter["count"] = 0
    try:
        result = await manager.execute_with_retry(
            "api-calls",
            flaky_operation,
            operation_name="fetch_data"
        )
        print(f"  ✓ flaky_operation: success after {attempt_counter['count']} attempts")
    except Exception as e:
        print(f"  ✗ flaky_operation: {e}")
        
    # Always succeed
    try:
        result = await manager.execute_with_retry(
            "database",
            always_succeed,
            operation_name="db_query"
        )
        print(f"  ✓ always_succeed: immediate success")
    except Exception as e:
        print(f"  ✗ always_succeed: {e}")
        
    # Non-retryable error
    policies[0].non_retryable_errors.add("ValueError")
    try:
        await manager.execute_with_retry(
            "api-calls",
            always_fail,
            operation_name="validate_input"
        )
    except ValueError as e:
        print(f"  ✗ always_fail: non-retryable error")
        
    # Display policies
    print("\n📋 Retry Policies:")
    
    print("\n  ┌─────────────────┬────────────────┬──────────┬──────────┬───────────┐")
    print("  │ Policy          │ Strategy       │ Max      │ Initial  │ Jitter    │")
    print("  ├─────────────────┼────────────────┼──────────┼──────────┼───────────┤")
    
    for policy in manager.policies.values():
        name = policy.name[:15].ljust(15)
        strategy = policy.strategy.value[:14].ljust(14)
        max_ret = str(policy.max_retries)[:8].ljust(8)
        initial = f"{policy.initial_delay_ms}ms"[:8].ljust(8)
        jitter = policy.jitter_type.value[:9].ljust(9)
        
        print(f"  │ {name} │ {strategy} │ {max_ret} │ {initial} │ {jitter} │")
        
    print("  └─────────────────┴────────────────┴──────────┴──────────┴───────────┘")
    
    # Display executions
    print("\n🔄 Executions:")
    
    print("\n  ┌──────────────────┬─────────────────┬───────────┬──────────┬──────────┐")
    print("  │ Execution        │ Operation       │ Attempts  │ Delay    │ State    │")
    print("  ├──────────────────┼─────────────────┼───────────┼──────────┼──────────┤")
    
    for execution in manager.executions.values():
        exec_id = execution.execution_id[:16].ljust(16)
        op_name = execution.operation_name[:15].ljust(15)
        attempts = str(len(execution.attempts))[:9].ljust(9)
        delay = f"{execution.total_delay_ms}ms"[:8].ljust(8)
        state = execution.state.value[:8].ljust(8)
        
        print(f"  │ {exec_id} │ {op_name} │ {attempts} │ {delay} │ {state} │")
        
    print("  └──────────────────┴─────────────────┴───────────┴──────────┴──────────┘")
    
    # Display attempts for first execution
    if manager.executions:
        first_exec = list(manager.executions.values())[0]
        print(f"\n📝 Attempts for {first_exec.operation_name}:")
        
        for att in first_exec.attempts:
            status = "✓" if att.state == RetryState.SUCCESS else "✗"
            error = f" ({att.error[:30]}...)" if att.error else ""
            print(f"  {status} Attempt {att.attempt_number + 1}: delay={att.delay_ms}ms{error}")
            
    # Metrics
    print("\n📊 Policy Metrics:")
    
    print("\n  ┌─────────────────┬──────────┬──────────┬──────────┬──────────┐")
    print("  │ Policy          │ Total    │ 1st Try  │ Retried  │ Exhaust  │")
    print("  ├─────────────────┼──────────┼──────────┼──────────┼──────────┤")
    
    for name, metrics in manager.metrics.items():
        policy_name = name[:15].ljust(15)
        total = str(metrics.total_executions)[:8].ljust(8)
        first = str(metrics.successful_first_try)[:8].ljust(8)
        retried = str(metrics.successful_after_retry)[:8].ljust(8)
        exhausted = str(metrics.exhausted)[:8].ljust(8)
        
        print(f"  │ {policy_name} │ {total} │ {first} │ {retried} │ {exhausted} │")
        
    print("  └─────────────────┴──────────┴──────────┴──────────┴──────────┘")
    
    # Strategy comparison
    print("\n📊 Delay by Strategy (5 attempts):")
    
    strategies = [
        ("Fixed", RetryStrategy.FIXED),
        ("Linear", RetryStrategy.LINEAR),
        ("Exponential", RetryStrategy.EXPONENTIAL),
        ("Fibonacci", RetryStrategy.FIBONACCI),
    ]
    
    for name, strategy in strategies:
        test_policy = RetryPolicy(
            policy_id="test",
            name="test",
            strategy=strategy,
            initial_delay_ms=1000,
            multiplier=2.0,
            jitter_type=JitterType.NONE
        )
        
        delays = [manager.calculate_delay(test_policy, i, 0) for i in range(5)]
        print(f"  {name:12s}: {' -> '.join(f'{d}ms' for d in delays)}")
        
    # Error type distribution
    print("\n📊 Error Types (api-calls):")
    
    api_metrics = manager.metrics.get("api-calls")
    if api_metrics and api_metrics.errors_by_type:
        for error_type, count in api_metrics.errors_by_type.items():
            bar = "█" * count
            print(f"  {error_type:15s} [{bar:10s}] {count}")
            
    # Statistics
    print("\n📊 Manager Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Policies: {stats['policies_count']}")
    print(f"  Total Executions: {stats['total_executions']}")
    print(f"  Total Attempts: {stats['total_attempts']}")
    print(f"  Avg Attempts/Execution: {stats['avg_attempts_per_execution']:.2f}")
    
    print(f"\n  Success Rate: {stats['success_rate']:.1f}%")
    print(f"  Exhausted Rate: {stats['exhausted_rate']:.1f}%")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Retry Policy Manager Dashboard                    │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Policies:                      {stats['policies_count']:>12}                        │")
    print(f"│ Total Executions:              {stats['total_executions']:>12}                        │")
    print(f"│ Total Attempts:                {stats['total_attempts']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Success Rate:                  {stats['success_rate']:>11.1f}%                        │")
    print(f"│ Avg Attempts:                  {stats['avg_attempts_per_execution']:>12.2f}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Retry Policy Manager Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
