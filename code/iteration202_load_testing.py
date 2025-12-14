#!/usr/bin/env python3
"""
Server Init - Iteration 202: Load Testing Platform
Платформа нагрузочного тестирования

Функционал:
- Test Scenarios - сценарии тестирования
- Load Generation - генерация нагрузки
- Virtual Users - виртуальные пользователи
- Metrics Collection - сбор метрик
- Threshold Validation - валидация порогов
- Result Analysis - анализ результатов
- Performance Reports - отчёты о производительности
- Distributed Testing - распределённое тестирование
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid
import statistics


class TestStatus(Enum):
    """Статус теста"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class LoadPattern(Enum):
    """Паттерн нагрузки"""
    CONSTANT = "constant"
    RAMP_UP = "ramp_up"
    STEP = "step"
    SPIKE = "spike"
    STRESS = "stress"


class ThresholdStatus(Enum):
    """Статус порога"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"


@dataclass
class RequestResult:
    """Результат запроса"""
    request_id: str
    
    # Request
    method: str = "GET"
    url: str = ""
    
    # Response
    status_code: int = 200
    response_time_ms: float = 0
    response_size_bytes: int = 0
    
    # Status
    success: bool = True
    error: str = ""
    
    # Time
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TestStep:
    """Шаг теста"""
    step_id: str
    name: str = ""
    
    # Request
    method: str = "GET"
    url: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    body: Any = None
    
    # Validation
    expected_status: int = 200
    
    # Think time
    think_time_ms: int = 1000


@dataclass
class TestScenario:
    """Сценарий теста"""
    scenario_id: str
    name: str = ""
    description: str = ""
    
    # Steps
    steps: List[TestStep] = field(default_factory=list)
    
    # Weight
    weight: int = 100  # For distributed load
    
    # Tags
    tags: List[str] = field(default_factory=list)


@dataclass
class LoadProfile:
    """Профиль нагрузки"""
    profile_id: str
    name: str = ""
    
    # Pattern
    pattern: LoadPattern = LoadPattern.CONSTANT
    
    # Users
    initial_users: int = 1
    max_users: int = 100
    
    # Duration
    ramp_up_duration_sec: int = 60
    steady_duration_sec: int = 300
    ramp_down_duration_sec: int = 30
    
    @property
    def total_duration_sec(self) -> int:
        return self.ramp_up_duration_sec + self.steady_duration_sec + self.ramp_down_duration_sec


@dataclass
class Threshold:
    """Порог"""
    threshold_id: str
    name: str = ""
    
    # Metric
    metric: str = ""  # response_time_p95, error_rate, etc.
    
    # Condition
    operator: str = "<"  # <, >, <=, >=, ==
    value: float = 0
    
    # Result
    actual_value: float = 0
    status: ThresholdStatus = ThresholdStatus.PASSED


@dataclass
class VirtualUser:
    """Виртуальный пользователь"""
    user_id: str
    
    # State
    is_active: bool = True
    
    # Scenario
    scenario_id: str = ""
    current_step: int = 0
    
    # Metrics
    requests_made: int = 0
    errors: int = 0


@dataclass
class TestRun:
    """Запуск теста"""
    run_id: str
    name: str = ""
    
    # Scenarios
    scenarios: List[TestScenario] = field(default_factory=list)
    
    # Load profile
    load_profile: LoadProfile = field(default_factory=LoadProfile)
    
    # Thresholds
    thresholds: List[Threshold] = field(default_factory=list)
    
    # Status
    status: TestStatus = TestStatus.PENDING
    
    # Results
    results: List[RequestResult] = field(default_factory=list)
    
    # Virtual users
    virtual_users: List[VirtualUser] = field(default_factory=list)
    
    # Time
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    @property
    def duration_sec(self) -> float:
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return 0


class MetricsCalculator:
    """Калькулятор метрик"""
    
    @staticmethod
    def calculate(results: List[RequestResult]) -> Dict[str, Any]:
        """Расчёт метрик"""
        if not results:
            return {}
            
        response_times = [r.response_time_ms for r in results]
        successful = [r for r in results if r.success]
        
        metrics = {
            "total_requests": len(results),
            "successful_requests": len(successful),
            "failed_requests": len(results) - len(successful),
            "error_rate": (len(results) - len(successful)) / len(results) * 100,
            "response_time_min": min(response_times),
            "response_time_max": max(response_times),
            "response_time_avg": statistics.mean(response_times),
            "response_time_median": statistics.median(response_times),
            "response_time_p90": statistics.quantiles(response_times, n=10)[-1] if len(response_times) > 1 else response_times[0],
            "response_time_p95": statistics.quantiles(response_times, n=20)[-1] if len(response_times) > 1 else response_times[0],
            "response_time_p99": statistics.quantiles(response_times, n=100)[-1] if len(response_times) > 1 else response_times[0],
            "total_bytes": sum(r.response_size_bytes for r in results),
        }
        
        # Calculate throughput
        if results:
            duration = (results[-1].timestamp - results[0].timestamp).total_seconds()
            if duration > 0:
                metrics["requests_per_second"] = len(results) / duration
            else:
                metrics["requests_per_second"] = len(results)
                
        return metrics


class LoadGenerator:
    """Генератор нагрузки"""
    
    def __init__(self):
        self.is_running = False
        
    async def simulate_request(self, step: TestStep) -> RequestResult:
        """Симуляция запроса"""
        # Simulate network latency
        latency = random.uniform(50, 500)
        await asyncio.sleep(latency / 1000)
        
        # Random success/failure
        success = random.random() > 0.05  # 95% success rate
        status_code = 200 if success else random.choice([500, 502, 503, 504])
        
        return RequestResult(
            request_id=f"req_{uuid.uuid4().hex[:8]}",
            method=step.method,
            url=step.url,
            status_code=status_code,
            response_time_ms=latency,
            response_size_bytes=random.randint(500, 5000),
            success=success,
            error="" if success else "Server error"
        )
        
    async def run_scenario(self, scenario: TestScenario, user: VirtualUser) -> List[RequestResult]:
        """Выполнение сценария"""
        results = []
        
        for step in scenario.steps:
            result = await self.simulate_request(step)
            results.append(result)
            user.requests_made += 1
            
            if not result.success:
                user.errors += 1
                
            # Think time
            await asyncio.sleep(step.think_time_ms / 10000)  # Reduced for demo
            
        return results


class ThresholdValidator:
    """Валидатор порогов"""
    
    @staticmethod
    def validate(thresholds: List[Threshold], metrics: Dict[str, Any]) -> List[Threshold]:
        """Валидация порогов"""
        for threshold in thresholds:
            actual = metrics.get(threshold.metric, 0)
            threshold.actual_value = actual
            
            if threshold.operator == "<":
                passed = actual < threshold.value
            elif threshold.operator == ">":
                passed = actual > threshold.value
            elif threshold.operator == "<=":
                passed = actual <= threshold.value
            elif threshold.operator == ">=":
                passed = actual >= threshold.value
            else:
                passed = actual == threshold.value
                
            threshold.status = ThresholdStatus.PASSED if passed else ThresholdStatus.FAILED
            
        return thresholds


class LoadTestingPlatform:
    """Платформа нагрузочного тестирования"""
    
    def __init__(self):
        self.test_runs: Dict[str, TestRun] = {}
        self.scenarios: Dict[str, TestScenario] = {}
        self.generator = LoadGenerator()
        
    def create_scenario(self, name: str, steps: List[Dict[str, Any]]) -> TestScenario:
        """Создание сценария"""
        scenario = TestScenario(
            scenario_id=f"scen_{uuid.uuid4().hex[:8]}",
            name=name
        )
        
        for step_data in steps:
            step = TestStep(
                step_id=f"step_{uuid.uuid4().hex[:8]}",
                name=step_data.get("name", ""),
                method=step_data.get("method", "GET"),
                url=step_data.get("url", ""),
                expected_status=step_data.get("expected_status", 200),
                think_time_ms=step_data.get("think_time_ms", 1000)
            )
            scenario.steps.append(step)
            
        self.scenarios[scenario.scenario_id] = scenario
        return scenario
        
    def create_load_profile(self, name: str, pattern: LoadPattern,
                           max_users: int, duration_sec: int) -> LoadProfile:
        """Создание профиля нагрузки"""
        return LoadProfile(
            profile_id=f"profile_{uuid.uuid4().hex[:8]}",
            name=name,
            pattern=pattern,
            max_users=max_users,
            ramp_up_duration_sec=duration_sec // 4,
            steady_duration_sec=duration_sec // 2,
            ramp_down_duration_sec=duration_sec // 4
        )
        
    async def run_test(self, name: str, scenario_ids: List[str],
                      profile: LoadProfile, thresholds: List[Dict[str, Any]] = None) -> TestRun:
        """Запуск теста"""
        scenarios = [self.scenarios[sid] for sid in scenario_ids if sid in self.scenarios]
        
        test_run = TestRun(
            run_id=f"run_{uuid.uuid4().hex[:8]}",
            name=name,
            scenarios=scenarios,
            load_profile=profile,
            status=TestStatus.RUNNING,
            started_at=datetime.now()
        )
        
        # Add thresholds
        for th_data in (thresholds or []):
            threshold = Threshold(
                threshold_id=f"th_{uuid.uuid4().hex[:8]}",
                name=th_data.get("name", ""),
                metric=th_data.get("metric", ""),
                operator=th_data.get("operator", "<"),
                value=th_data.get("value", 0)
            )
            test_run.thresholds.append(threshold)
            
        # Create virtual users
        for i in range(profile.max_users):
            user = VirtualUser(
                user_id=f"vu_{uuid.uuid4().hex[:8]}",
                scenario_id=random.choice(scenarios).scenario_id if scenarios else ""
            )
            test_run.virtual_users.append(user)
            
        self.test_runs[test_run.run_id] = test_run
        
        # Run load test (simplified for demo)
        tasks = []
        for user in test_run.virtual_users[:20]:  # Limit for demo
            scenario = next((s for s in scenarios if s.scenario_id == user.scenario_id), None)
            if scenario:
                tasks.append(self.generator.run_scenario(scenario, user))
                
        results_lists = await asyncio.gather(*tasks)
        
        for results in results_lists:
            test_run.results.extend(results)
            
        # Complete test
        test_run.completed_at = datetime.now()
        test_run.status = TestStatus.COMPLETED
        
        # Validate thresholds
        metrics = MetricsCalculator.calculate(test_run.results)
        ThresholdValidator.validate(test_run.thresholds, metrics)
        
        # Update status based on thresholds
        if any(t.status == ThresholdStatus.FAILED for t in test_run.thresholds):
            test_run.status = TestStatus.FAILED
            
        return test_run
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        all_results = []
        for run in self.test_runs.values():
            all_results.extend(run.results)
            
        total_requests = len(all_results)
        successful = len([r for r in all_results if r.success])
        
        return {
            "total_test_runs": len(self.test_runs),
            "total_scenarios": len(self.scenarios),
            "total_requests": total_requests,
            "successful_requests": successful,
            "success_rate": (successful / total_requests * 100) if total_requests > 0 else 0
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 202: Load Testing Platform")
    print("=" * 60)
    
    platform = LoadTestingPlatform()
    print("✓ Load Testing Platform created")
    
    # Create scenarios
    print("\n📋 Creating Test Scenarios...")
    
    # User flow scenario
    user_flow = platform.create_scenario("User Login Flow", [
        {"name": "Home Page", "method": "GET", "url": "/", "think_time_ms": 2000},
        {"name": "Login Page", "method": "GET", "url": "/login", "think_time_ms": 3000},
        {"name": "Submit Login", "method": "POST", "url": "/api/auth", "think_time_ms": 1000},
        {"name": "Dashboard", "method": "GET", "url": "/dashboard", "think_time_ms": 5000},
    ])
    print(f"  ✓ {user_flow.name} ({len(user_flow.steps)} steps)")
    
    # API scenario
    api_flow = platform.create_scenario("API Operations", [
        {"name": "List Items", "method": "GET", "url": "/api/items", "think_time_ms": 1000},
        {"name": "Get Item", "method": "GET", "url": "/api/items/1", "think_time_ms": 500},
        {"name": "Create Item", "method": "POST", "url": "/api/items", "think_time_ms": 1000},
        {"name": "Update Item", "method": "PUT", "url": "/api/items/1", "think_time_ms": 500},
        {"name": "Delete Item", "method": "DELETE", "url": "/api/items/1", "think_time_ms": 500},
    ])
    print(f"  ✓ {api_flow.name} ({len(api_flow.steps)} steps)")
    
    # Search scenario
    search_flow = platform.create_scenario("Search Operations", [
        {"name": "Search Query", "method": "GET", "url": "/api/search?q=test", "think_time_ms": 2000},
        {"name": "Filter Results", "method": "GET", "url": "/api/search?q=test&filter=active", "think_time_ms": 1500},
        {"name": "View Result", "method": "GET", "url": "/api/items/123", "think_time_ms": 3000},
    ])
    print(f"  ✓ {search_flow.name} ({len(search_flow.steps)} steps)")
    
    # Create load profiles
    print("\n📈 Creating Load Profiles...")
    
    smoke_profile = platform.create_load_profile("Smoke Test", LoadPattern.CONSTANT, 5, 60)
    print(f"  ✓ {smoke_profile.name} ({smoke_profile.max_users} users)")
    
    load_profile = platform.create_load_profile("Load Test", LoadPattern.RAMP_UP, 50, 300)
    print(f"  ✓ {load_profile.name} ({load_profile.max_users} users)")
    
    stress_profile = platform.create_load_profile("Stress Test", LoadPattern.STRESS, 200, 600)
    print(f"  ✓ {stress_profile.name} ({stress_profile.max_users} users)")
    
    # Define thresholds
    thresholds = [
        {"name": "P95 Response Time", "metric": "response_time_p95", "operator": "<", "value": 500},
        {"name": "Error Rate", "metric": "error_rate", "operator": "<", "value": 5},
        {"name": "Avg Response Time", "metric": "response_time_avg", "operator": "<", "value": 300},
    ]
    
    # Run tests
    print("\n🚀 Running Load Tests...")
    
    # Smoke test
    smoke_run = await platform.run_test(
        "Smoke Test Run",
        [user_flow.scenario_id, api_flow.scenario_id],
        smoke_profile,
        thresholds
    )
    
    status_icon = "✅" if smoke_run.status == TestStatus.COMPLETED else "❌"
    print(f"  {status_icon} Smoke Test: {smoke_run.status.value} ({len(smoke_run.results)} requests)")
    
    # Load test
    load_run = await platform.run_test(
        "Load Test Run",
        [user_flow.scenario_id, api_flow.scenario_id, search_flow.scenario_id],
        load_profile,
        thresholds
    )
    
    status_icon = "✅" if load_run.status == TestStatus.COMPLETED else "❌"
    print(f"  {status_icon} Load Test: {load_run.status.value} ({len(load_run.results)} requests)")
    
    # Display metrics
    print("\n📊 Test Metrics (Load Test):")
    
    metrics = MetricsCalculator.calculate(load_run.results)
    
    print("\n  ┌───────────────────────────┬──────────────────┐")
    print("  │ Metric                    │ Value            │")
    print("  ├───────────────────────────┼──────────────────┤")
    
    metric_display = [
        ("Total Requests", f"{metrics.get('total_requests', 0):,}"),
        ("Successful Requests", f"{metrics.get('successful_requests', 0):,}"),
        ("Failed Requests", f"{metrics.get('failed_requests', 0):,}"),
        ("Error Rate", f"{metrics.get('error_rate', 0):.2f}%"),
        ("Requests/Second", f"{metrics.get('requests_per_second', 0):.2f}"),
        ("Response Time Min", f"{metrics.get('response_time_min', 0):.2f} ms"),
        ("Response Time Max", f"{metrics.get('response_time_max', 0):.2f} ms"),
        ("Response Time Avg", f"{metrics.get('response_time_avg', 0):.2f} ms"),
        ("Response Time P90", f"{metrics.get('response_time_p90', 0):.2f} ms"),
        ("Response Time P95", f"{metrics.get('response_time_p95', 0):.2f} ms"),
        ("Response Time P99", f"{metrics.get('response_time_p99', 0):.2f} ms"),
    ]
    
    for name, value in metric_display:
        name_str = name[:25].ljust(25)
        value_str = value[:16].rjust(16)
        print(f"  │ {name_str} │ {value_str} │")
        
    print("  └───────────────────────────┴──────────────────┘")
    
    # Threshold results
    print("\n✅ Threshold Validation:")
    
    print("\n  ┌───────────────────────────┬──────────┬──────────┬──────────┐")
    print("  │ Threshold                 │ Expected │ Actual   │ Status   │")
    print("  ├───────────────────────────┼──────────┼──────────┼──────────┤")
    
    for threshold in load_run.thresholds:
        name = threshold.name[:25].ljust(25)
        expected = f"{threshold.operator}{threshold.value}".rjust(8)
        actual = f"{threshold.actual_value:.1f}".rjust(8)
        status = threshold.status.value[:8].ljust(8)
        print(f"  │ {name} │ {expected} │ {actual} │ {status} │")
        
    print("  └───────────────────────────┴──────────┴──────────┴──────────┘")
    
    # Virtual users summary
    print("\n👥 Virtual Users Summary:")
    
    active_users = [u for u in load_run.virtual_users if u.requests_made > 0]
    total_requests = sum(u.requests_made for u in active_users)
    total_errors = sum(u.errors for u in active_users)
    
    print(f"\n  Total Virtual Users: {len(load_run.virtual_users)}")
    print(f"  Active Users: {len(active_users)}")
    print(f"  Total Requests: {total_requests}")
    print(f"  Total Errors: {total_errors}")
    
    # Response time distribution
    print("\n📈 Response Time Distribution:")
    
    response_times = [r.response_time_ms for r in load_run.results]
    
    ranges = [
        (0, 100, "0-100ms"),
        (100, 200, "100-200ms"),
        (200, 300, "200-300ms"),
        (300, 400, "300-400ms"),
        (400, 500, "400-500ms"),
        (500, float('inf'), ">500ms"),
    ]
    
    for low, high, label in ranges:
        count = len([t for t in response_times if low <= t < high])
        pct = (count / len(response_times) * 100) if response_times else 0
        bar = "█" * int(pct / 2) + "░" * (50 - int(pct / 2))
        print(f"  {label:12} [{bar}] {count} ({pct:.1f}%)")
        
    # Test runs comparison
    print("\n📊 Test Runs Comparison:")
    
    print("\n  ┌──────────────────────┬──────────┬──────────┬──────────┬──────────┐")
    print("  │ Test                 │ Requests │ Errors   │ Avg Time │ Status   │")
    print("  ├──────────────────────┼──────────┼──────────┼──────────┼──────────┤")
    
    for run in platform.test_runs.values():
        run_metrics = MetricsCalculator.calculate(run.results)
        name = run.name[:20].ljust(20)
        requests = str(run_metrics.get('total_requests', 0)).center(8)
        errors = str(run_metrics.get('failed_requests', 0)).center(8)
        avg_time = f"{run_metrics.get('response_time_avg', 0):.0f}ms".center(8)
        status = run.status.value[:8].ljust(8)
        print(f"  │ {name} │ {requests} │ {errors} │ {avg_time} │ {status} │")
        
    print("  └──────────────────────┴──────────┴──────────┴──────────┴──────────┘")
    
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📈 Platform Statistics:")
    
    print(f"\n  Total Test Runs: {stats['total_test_runs']}")
    print(f"  Total Scenarios: {stats['total_scenarios']}")
    print(f"  Total Requests: {stats['total_requests']}")
    print(f"  Success Rate: {stats['success_rate']:.1f}%")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Load Testing Dashboard                          │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Test Runs:                     {stats['total_test_runs']:>12}                        │")
    print(f"│ Scenarios:                     {stats['total_scenarios']:>12}                        │")
    print(f"│ Total Requests:                {stats['total_requests']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Success Rate:                    {stats['success_rate']:>10.1f}%                   │")
    avg_rt = metrics.get('response_time_avg', 0)
    print(f"│ Avg Response Time:               {avg_rt:>10.1f} ms                  │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Load Testing Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
