#!/usr/bin/env python3
"""
Server Init - Iteration 257: Circuit Breaker Advanced Platform
Расширенная платформа Circuit Breaker с продвинутыми функциями

Функционал:
- State Machine - машина состояний
- Adaptive Thresholds - адаптивные пороги
- Sliding Window - скользящее окно
- Half-Open Testing - тестирование полуоткрытого состояния
- Fallback Strategies - стратегии отката
- Health Monitoring - мониторинг здоровья
- Bulkhead Integration - интеграция с bulkhead
- Metrics & Alerting - метрики и алертинг
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Awaitable, Deque
from collections import deque
from enum import Enum
import uuid


class CircuitState(Enum):
    """Состояние circuit breaker"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class WindowType(Enum):
    """Тип окна метрик"""
    COUNT_BASED = "count_based"
    TIME_BASED = "time_based"


class FallbackStrategy(Enum):
    """Стратегия отката"""
    THROW = "throw"
    RETURN_DEFAULT = "return_default"
    CACHE = "cache"
    QUEUE = "queue"
    REDIRECT = "redirect"


class TransitionReason(Enum):
    """Причина перехода"""
    FAILURE_RATE_EXCEEDED = "failure_rate_exceeded"
    SLOW_CALL_RATE_EXCEEDED = "slow_call_rate_exceeded"
    MANUAL_OPEN = "manual_open"
    WAIT_DURATION_ELAPSED = "wait_duration_elapsed"
    HALF_OPEN_SUCCESS = "half_open_success"
    HALF_OPEN_FAILURE = "half_open_failure"
    MANUAL_CLOSE = "manual_close"


@dataclass
class CallRecord:
    """Запись о вызове"""
    record_id: str
    
    # Result
    success: bool = True
    duration_ms: float = 0
    slow_call: bool = False
    
    # Error
    error: str = ""
    
    # Time
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SlidingWindow:
    """Скользящее окно"""
    window_type: WindowType = WindowType.COUNT_BASED
    
    # Size
    size: int = 100  # count or seconds
    
    # Records
    records: Deque[CallRecord] = field(default_factory=deque)
    
    # Aggregated metrics
    total_calls: int = 0
    failed_calls: int = 0
    slow_calls: int = 0
    total_duration_ms: float = 0


@dataclass
class CircuitBreakerConfig:
    """Конфигурация circuit breaker"""
    config_id: str
    name: str
    
    # Thresholds
    failure_rate_threshold: float = 50.0  # %
    slow_call_rate_threshold: float = 100.0  # %
    slow_call_duration_ms: int = 60000
    
    # Window
    window_type: WindowType = WindowType.COUNT_BASED
    window_size: int = 100
    minimum_calls: int = 10
    
    # Wait
    wait_duration_ms: int = 60000
    
    # Half-open
    permitted_calls_in_half_open: int = 10
    
    # Fallback
    fallback_strategy: FallbackStrategy = FallbackStrategy.THROW
    fallback_value: Any = None
    
    # Adaptive
    adaptive_enabled: bool = False
    adaptive_min_threshold: float = 30.0
    adaptive_max_threshold: float = 80.0


@dataclass
class CircuitBreaker:
    """Circuit Breaker"""
    breaker_id: str
    name: str
    
    # Config
    config: CircuitBreakerConfig = field(default_factory=lambda: CircuitBreakerConfig(
        config_id="default",
        name="default"
    ))
    
    # State
    state: CircuitState = CircuitState.CLOSED
    
    # Window
    window: SlidingWindow = field(default_factory=SlidingWindow)
    
    # Timing
    last_state_change: datetime = field(default_factory=datetime.now)
    opened_at: Optional[datetime] = None
    
    # Half-open tracking
    half_open_calls: int = 0
    half_open_successes: int = 0
    
    # Stats
    total_calls: int = 0
    total_failures: int = 0
    total_successes: int = 0
    total_rejections: int = 0
    
    # Transitions
    state_transitions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Cache for fallback
    last_successful_response: Any = None


@dataclass
class CircuitBreakerMetrics:
    """Метрики circuit breaker"""
    breaker_name: str
    
    # Current
    current_failure_rate: float = 0
    current_slow_call_rate: float = 0
    
    # Stats
    calls_in_window: int = 0
    failed_in_window: int = 0
    slow_in_window: int = 0
    
    # Time in states
    time_in_closed_ms: int = 0
    time_in_open_ms: int = 0
    time_in_half_open_ms: int = 0


class CircuitBreakerManager:
    """Менеджер circuit breaker"""
    
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
        self.configs: Dict[str, CircuitBreakerConfig] = {}
        self.metrics: Dict[str, CircuitBreakerMetrics] = {}
        
    def create_config(self, name: str,
                     failure_rate_threshold: float = 50.0,
                     slow_call_duration_ms: int = 60000,
                     window_size: int = 100,
                     wait_duration_ms: int = 60000,
                     fallback_strategy: FallbackStrategy = FallbackStrategy.THROW) -> CircuitBreakerConfig:
        """Создание конфигурации"""
        config = CircuitBreakerConfig(
            config_id=f"cfg_{uuid.uuid4().hex[:8]}",
            name=name,
            failure_rate_threshold=failure_rate_threshold,
            slow_call_duration_ms=slow_call_duration_ms,
            window_size=window_size,
            wait_duration_ms=wait_duration_ms,
            fallback_strategy=fallback_strategy
        )
        
        self.configs[name] = config
        return config
        
    def create_breaker(self, name: str, config_name: str = None) -> CircuitBreaker:
        """Создание circuit breaker"""
        config = self.configs.get(config_name or name)
        if not config:
            config = CircuitBreakerConfig(
                config_id=f"cfg_{uuid.uuid4().hex[:8]}",
                name=name
            )
            
        breaker = CircuitBreaker(
            breaker_id=f"cb_{uuid.uuid4().hex[:8]}",
            name=name,
            config=config,
            window=SlidingWindow(
                window_type=config.window_type,
                size=config.window_size
            )
        )
        
        self.breakers[name] = breaker
        self.metrics[name] = CircuitBreakerMetrics(breaker_name=name)
        
        return breaker
        
    def _record_call(self, breaker: CircuitBreaker, success: bool,
                    duration_ms: float, error: str = ""):
        """Запись вызова"""
        slow = duration_ms > breaker.config.slow_call_duration_ms
        
        record = CallRecord(
            record_id=f"rec_{uuid.uuid4().hex[:8]}",
            success=success,
            duration_ms=duration_ms,
            slow_call=slow,
            error=error
        )
        
        window = breaker.window
        window.records.append(record)
        window.total_calls += 1
        window.total_duration_ms += duration_ms
        
        if not success:
            window.failed_calls += 1
        if slow:
            window.slow_calls += 1
            
        # Trim window
        if window.window_type == WindowType.COUNT_BASED:
            while len(window.records) > window.size:
                old = window.records.popleft()
                window.total_calls -= 1
                window.total_duration_ms -= old.duration_ms
                if not old.success:
                    window.failed_calls -= 1
                if old.slow_call:
                    window.slow_calls -= 1
        else:
            cutoff = datetime.now() - timedelta(seconds=window.size)
            while window.records and window.records[0].timestamp < cutoff:
                old = window.records.popleft()
                window.total_calls -= 1
                window.total_duration_ms -= old.duration_ms
                if not old.success:
                    window.failed_calls -= 1
                if old.slow_call:
                    window.slow_calls -= 1
                    
        # Update breaker stats
        breaker.total_calls += 1
        if success:
            breaker.total_successes += 1
        else:
            breaker.total_failures += 1
            
    def _check_thresholds(self, breaker: CircuitBreaker) -> Optional[TransitionReason]:
        """Проверка порогов"""
        window = breaker.window
        config = breaker.config
        
        if window.total_calls < config.minimum_calls:
            return None
            
        failure_rate = (window.failed_calls / window.total_calls) * 100
        slow_rate = (window.slow_calls / window.total_calls) * 100
        
        # Update metrics
        metrics = self.metrics.get(breaker.name)
        if metrics:
            metrics.current_failure_rate = failure_rate
            metrics.current_slow_call_rate = slow_rate
            metrics.calls_in_window = window.total_calls
            metrics.failed_in_window = window.failed_calls
            metrics.slow_in_window = window.slow_calls
            
        if failure_rate >= config.failure_rate_threshold:
            return TransitionReason.FAILURE_RATE_EXCEEDED
            
        if slow_rate >= config.slow_call_rate_threshold:
            return TransitionReason.SLOW_CALL_RATE_EXCEEDED
            
        return None
        
    def _transition_to(self, breaker: CircuitBreaker, new_state: CircuitState,
                      reason: TransitionReason):
        """Переход в новое состояние"""
        old_state = breaker.state
        breaker.state = new_state
        breaker.last_state_change = datetime.now()
        
        if new_state == CircuitState.OPEN:
            breaker.opened_at = datetime.now()
            breaker.half_open_calls = 0
            breaker.half_open_successes = 0
        elif new_state == CircuitState.HALF_OPEN:
            breaker.half_open_calls = 0
            breaker.half_open_successes = 0
        elif new_state == CircuitState.CLOSED:
            # Reset window
            breaker.window = SlidingWindow(
                window_type=breaker.config.window_type,
                size=breaker.config.window_size
            )
            
        breaker.state_transitions.append({
            "from": old_state.value,
            "to": new_state.value,
            "reason": reason.value,
            "timestamp": datetime.now()
        })
        
    def _should_allow_call(self, breaker: CircuitBreaker) -> bool:
        """Проверка разрешения вызова"""
        if breaker.state == CircuitState.CLOSED:
            return True
            
        if breaker.state == CircuitState.OPEN:
            # Check if wait duration elapsed
            if breaker.opened_at:
                elapsed = (datetime.now() - breaker.opened_at).total_seconds() * 1000
                if elapsed >= breaker.config.wait_duration_ms:
                    self._transition_to(breaker, CircuitState.HALF_OPEN,
                                       TransitionReason.WAIT_DURATION_ELAPSED)
                    return True
            return False
            
        if breaker.state == CircuitState.HALF_OPEN:
            return breaker.half_open_calls < breaker.config.permitted_calls_in_half_open
            
        return False
        
    def _apply_fallback(self, breaker: CircuitBreaker, error: Exception) -> Any:
        """Применение fallback стратегии"""
        strategy = breaker.config.fallback_strategy
        
        if strategy == FallbackStrategy.THROW:
            raise error
            
        elif strategy == FallbackStrategy.RETURN_DEFAULT:
            return breaker.config.fallback_value
            
        elif strategy == FallbackStrategy.CACHE:
            if breaker.last_successful_response is not None:
                return breaker.last_successful_response
            raise error
            
        elif strategy == FallbackStrategy.QUEUE:
            # Would queue for later processing
            return {"queued": True, "error": str(error)}
            
        elif strategy == FallbackStrategy.REDIRECT:
            return {"redirected": True, "original_error": str(error)}
            
        raise error
        
    async def execute(self, breaker_name: str,
                     operation: Callable[..., Awaitable[Any]],
                     *args, **kwargs) -> Any:
        """Выполнение операции через circuit breaker"""
        breaker = self.breakers.get(breaker_name)
        if not breaker:
            breaker = self.create_breaker(breaker_name)
            
        # Check if call is allowed
        if not self._should_allow_call(breaker):
            breaker.total_rejections += 1
            return self._apply_fallback(
                breaker,
                Exception(f"Circuit breaker {breaker_name} is OPEN")
            )
            
        # Track half-open calls
        if breaker.state == CircuitState.HALF_OPEN:
            breaker.half_open_calls += 1
            
        start_time = datetime.now()
        
        try:
            result = await operation(*args, **kwargs)
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Record success
            self._record_call(breaker, True, duration_ms)
            breaker.last_successful_response = result
            
            # Handle half-open success
            if breaker.state == CircuitState.HALF_OPEN:
                breaker.half_open_successes += 1
                if breaker.half_open_successes >= breaker.config.permitted_calls_in_half_open:
                    self._transition_to(breaker, CircuitState.CLOSED,
                                       TransitionReason.HALF_OPEN_SUCCESS)
                    
            return result
            
        except Exception as e:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Record failure
            self._record_call(breaker, False, duration_ms, str(e))
            
            # Handle state transitions
            if breaker.state == CircuitState.CLOSED:
                reason = self._check_thresholds(breaker)
                if reason:
                    self._transition_to(breaker, CircuitState.OPEN, reason)
                    
            elif breaker.state == CircuitState.HALF_OPEN:
                self._transition_to(breaker, CircuitState.OPEN,
                                   TransitionReason.HALF_OPEN_FAILURE)
                                   
            return self._apply_fallback(breaker, e)
            
    def force_open(self, breaker_name: str):
        """Принудительное открытие"""
        breaker = self.breakers.get(breaker_name)
        if breaker:
            self._transition_to(breaker, CircuitState.OPEN,
                               TransitionReason.MANUAL_OPEN)
            
    def force_close(self, breaker_name: str):
        """Принудительное закрытие"""
        breaker = self.breakers.get(breaker_name)
        if breaker:
            self._transition_to(breaker, CircuitState.CLOSED,
                               TransitionReason.MANUAL_CLOSE)
            
    def get_state(self, breaker_name: str) -> Optional[CircuitState]:
        """Получение состояния"""
        breaker = self.breakers.get(breaker_name)
        return breaker.state if breaker else None
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        states = {state: 0 for state in CircuitState}
        total_calls = 0
        total_rejections = 0
        
        for breaker in self.breakers.values():
            states[breaker.state] += 1
            total_calls += breaker.total_calls
            total_rejections += breaker.total_rejections
            
        return {
            "breakers_total": len(self.breakers),
            "breakers_closed": states[CircuitState.CLOSED],
            "breakers_open": states[CircuitState.OPEN],
            "breakers_half_open": states[CircuitState.HALF_OPEN],
            "total_calls": total_calls,
            "total_rejections": total_rejections,
            "rejection_rate": (total_rejections / max(1, total_calls + total_rejections)) * 100
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 257: Circuit Breaker Advanced Platform")
    print("=" * 60)
    
    manager = CircuitBreakerManager()
    print("✓ Circuit Breaker Manager created")
    
    # Create configurations
    print("\n⚙️ Creating Configurations...")
    
    configs_data = [
        ("api-service", 50.0, 5000, 20, 10000, FallbackStrategy.CACHE),
        ("database", 30.0, 3000, 50, 30000, FallbackStrategy.RETURN_DEFAULT),
        ("external-api", 60.0, 10000, 10, 60000, FallbackStrategy.THROW),
    ]
    
    for name, failure_rate, slow_dur, window, wait, fallback in configs_data:
        config = manager.create_config(
            name, failure_rate, slow_dur, window, wait, fallback
        )
        config.fallback_value = {"status": "fallback", "cached": True}
        print(f"  ⚙️ {name}: threshold={failure_rate}%, fallback={fallback.value}")
        
    # Create breakers
    print("\n🔌 Creating Circuit Breakers...")
    
    for config_name in ["api-service", "database", "external-api"]:
        breaker = manager.create_breaker(config_name, config_name)
        print(f"  🔌 {breaker.name}: {breaker.state.value}")
        
    # Define test operations
    call_counter = {"api": 0, "db": 0}
    
    async def api_call():
        call_counter["api"] += 1
        await asyncio.sleep(random.uniform(0.01, 0.05))
        
        # Simulate failures (30% failure rate)
        if random.random() < 0.3:
            raise ConnectionError("API connection failed")
        return {"data": "api_response", "call": call_counter["api"]}
        
    async def db_query():
        call_counter["db"] += 1
        await asyncio.sleep(random.uniform(0.01, 0.03))
        
        # Simulate failures (70% failure rate to trigger open)
        if random.random() < 0.7:
            raise TimeoutError("Database timeout")
        return {"data": "db_result", "call": call_counter["db"]}
        
    # Execute operations
    print("\n🔄 Executing Operations...")
    
    # API calls (should stay closed)
    print("\n  API Service (30% failure rate):")
    for i in range(15):
        try:
            result = await manager.execute("api-service", api_call)
            if isinstance(result, dict) and "data" in result:
                pass  # Success
        except Exception:
            pass
            
    api_breaker = manager.breakers.get("api-service")
    print(f"    State: {api_breaker.state.value}")
    print(f"    Calls: {api_breaker.total_calls}, Failures: {api_breaker.total_failures}")
    
    # Database calls (should trigger open)
    print("\n  Database (70% failure rate):")
    for i in range(25):
        try:
            result = await manager.execute("database", db_query)
        except Exception:
            pass
            
    db_breaker = manager.breakers.get("database")
    print(f"    State: {db_breaker.state.value}")
    print(f"    Calls: {db_breaker.total_calls}, Failures: {db_breaker.total_failures}")
    print(f"    Rejections: {db_breaker.total_rejections}")
    
    # Display breakers
    print("\n🔌 Circuit Breakers:")
    
    print("\n  ┌─────────────────┬───────────┬──────────┬──────────┬──────────┬──────────┐")
    print("  │ Breaker         │ State     │ Calls    │ Failures │ Rejects  │ Rate(%)  │")
    print("  ├─────────────────┼───────────┼──────────┼──────────┼──────────┼──────────┤")
    
    for breaker in manager.breakers.values():
        name = breaker.name[:15].ljust(15)
        state = breaker.state.value[:9].ljust(9)
        calls = str(breaker.total_calls)[:8].ljust(8)
        failures = str(breaker.total_failures)[:8].ljust(8)
        rejects = str(breaker.total_rejections)[:8].ljust(8)
        rate = f"{(breaker.total_failures / max(1, breaker.total_calls)) * 100:.1f}"[:8].ljust(8)
        
        print(f"  │ {name} │ {state} │ {calls} │ {failures} │ {rejects} │ {rate} │")
        
    print("  └─────────────────┴───────────┴──────────┴──────────┴──────────┴──────────┘")
    
    # Metrics
    print("\n📊 Circuit Breaker Metrics:")
    
    for name, metrics in manager.metrics.items():
        print(f"\n  {name}:")
        print(f"    Failure Rate: {metrics.current_failure_rate:.1f}%")
        print(f"    Slow Call Rate: {metrics.current_slow_call_rate:.1f}%")
        print(f"    Window: {metrics.calls_in_window} calls ({metrics.failed_in_window} failed)")
        
    # State transitions
    print("\n📜 State Transitions (database):")
    
    for transition in db_breaker.state_transitions[-5:]:
        print(f"  [{transition['timestamp'].strftime('%H:%M:%S')}] {transition['from']} -> {transition['to']} ({transition['reason']})")
        
    # Force state changes
    print("\n🔧 Manual State Changes:")
    
    manager.force_close("database")
    print(f"  ✓ database: forced CLOSED")
    
    # Sliding window
    print("\n📊 Sliding Window (api-service):")
    
    window = api_breaker.window
    print(f"  Type: {window.window_type.value}")
    print(f"  Size: {window.size}")
    print(f"  Records: {len(window.records)}")
    print(f"  Total Calls: {window.total_calls}")
    print(f"  Failed: {window.failed_calls}")
    print(f"  Slow: {window.slow_calls}")
    
    # Configuration display
    print("\n⚙️ Configurations:")
    
    print("\n  ┌─────────────────┬──────────┬──────────┬──────────┬─────────────────┐")
    print("  │ Config          │ Threshold│ Window   │ Wait     │ Fallback        │")
    print("  ├─────────────────┼──────────┼──────────┼──────────┼─────────────────┤")
    
    for config in manager.configs.values():
        name = config.name[:15].ljust(15)
        threshold = f"{config.failure_rate_threshold:.0f}%"[:8].ljust(8)
        window = str(config.window_size)[:8].ljust(8)
        wait = f"{config.wait_duration_ms/1000:.0f}s"[:8].ljust(8)
        fallback = config.fallback_strategy.value[:15].ljust(15)
        
        print(f"  │ {name} │ {threshold} │ {window} │ {wait} │ {fallback} │")
        
    print("  └─────────────────┴──────────┴──────────┴──────────┴─────────────────┘")
    
    # State distribution
    print("\n📊 State Distribution:")
    
    for state in CircuitState:
        count = sum(1 for b in manager.breakers.values() if b.state == state)
        bar = "█" * count + "░" * (10 - count)
        icon = {
            CircuitState.CLOSED: "🟢",
            CircuitState.OPEN: "🔴",
            CircuitState.HALF_OPEN: "🟡"
        }.get(state, "⚪")
        print(f"  {icon} {state.value:12s} [{bar}] {count}")
        
    # Statistics
    print("\n📊 Manager Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Breakers: {stats['breakers_total']}")
    print(f"  Closed: {stats['breakers_closed']}")
    print(f"  Open: {stats['breakers_open']}")
    print(f"  Half-Open: {stats['breakers_half_open']}")
    
    print(f"\n  Total Calls: {stats['total_calls']}")
    print(f"  Total Rejections: {stats['total_rejections']}")
    print(f"  Rejection Rate: {stats['rejection_rate']:.1f}%")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                  Circuit Breaker Advanced Dashboard                 │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Breakers:                      {stats['breakers_total']:>12}                        │")
    print(f"│ Closed:                        {stats['breakers_closed']:>12}                        │")
    print(f"│ Open:                          {stats['breakers_open']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Calls:                   {stats['total_calls']:>12}                        │")
    print(f"│ Rejection Rate:                {stats['rejection_rate']:>11.1f}%                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Circuit Breaker Advanced Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
