#!/usr/bin/env python3
"""
Server Init - Iteration 177: Performance Testing Platform
Платформа тестирования производительности

Функционал:
- Load Testing - нагрузочное тестирование
- Stress Testing - стресс-тестирование
- Endurance Testing - длительное тестирование
- Spike Testing - пиковое тестирование
- Metrics Collection - сбор метрик
- Performance Reporting - отчёты о производительности
- Baseline Management - управление базовыми показателями
- SLA Validation - проверка SLA
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid
import statistics


class TestType(Enum):
    """Тип теста"""
    LOAD = "load"  # Normal load testing
    STRESS = "stress"  # Beyond normal capacity
    SPIKE = "spike"  # Sudden traffic spikes
    SOAK = "soak"  # Long duration testing
    ENDURANCE = "endurance"  # Extended period testing
    BREAKPOINT = "breakpoint"  # Find breaking point


class TestStatus(Enum):
    """Статус теста"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MetricType(Enum):
    """Тип метрики"""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CONCURRENT_USERS = "concurrent_users"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    NETWORK_IO = "network_io"


class ComparisonResult(Enum):
    """Результат сравнения"""
    IMPROVED = "improved"
    DEGRADED = "degraded"
    UNCHANGED = "unchanged"


@dataclass
class TestScenario:
    """Сценарий теста"""
    scenario_id: str
    name: str = ""
    description: str = ""
    
    # Target
    target_url: str = ""
    target_method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    body: str = ""
    
    # Timing
    think_time_ms: int = 1000
    ramp_up_seconds: int = 60
    duration_seconds: int = 300
    
    # Load
    virtual_users: int = 100
    requests_per_second: int = 0  # 0 = unlimited


@dataclass
class LoadProfile:
    """Профиль нагрузки"""
    profile_id: str
    name: str = ""
    
    # Stages
    stages: List[Dict] = field(default_factory=list)
    # Each stage: {"duration": 60, "users": 100, "rps": 500}
    
    # Pattern
    pattern: str = "linear"  # linear, step, spike


@dataclass
class PerformanceMetric:
    """Метрика производительности"""
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Values
    value: float = 0.0
    min_value: float = 0.0
    max_value: float = 0.0
    avg_value: float = 0.0
    
    # Percentiles
    p50: float = 0.0
    p90: float = 0.0
    p95: float = 0.0
    p99: float = 0.0
    
    # Unit
    unit: str = ""


@dataclass
class TestResult:
    """Результат теста"""
    test_id: str
    scenario_id: str = ""
    
    # Status
    status: TestStatus = TestStatus.PENDING
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    
    # Summary
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # Response times (ms)
    avg_response_time: float = 0.0
    min_response_time: float = 0.0
    max_response_time: float = 0.0
    p50_response_time: float = 0.0
    p90_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    
    # Throughput
    requests_per_second: float = 0.0
    bytes_per_second: float = 0.0
    
    # Errors
    error_rate: float = 0.0
    errors_by_type: Dict[str, int] = field(default_factory=dict)
    
    # Metrics timeline
    metrics: List[PerformanceMetric] = field(default_factory=list)
    
    # SLA
    sla_passed: bool = True
    sla_violations: List[str] = field(default_factory=list)


@dataclass
class Baseline:
    """Базовые показатели"""
    baseline_id: str
    name: str = ""
    
    # Target
    scenario_id: str = ""
    environment: str = ""
    
    # Metrics
    avg_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    throughput: float = 0.0
    error_rate: float = 0.0
    
    # Created
    created_at: datetime = field(default_factory=datetime.now)
    test_id: str = ""


@dataclass
class SLADefinition:
    """Определение SLA"""
    sla_id: str
    name: str = ""
    
    # Thresholds
    max_response_time_ms: float = 500
    max_p95_response_time_ms: float = 1000
    max_error_rate: float = 1.0  # percent
    min_throughput: float = 100  # req/s
    
    # Custom rules
    custom_rules: List[Dict] = field(default_factory=list)


class LoadGenerator:
    """Генератор нагрузки"""
    
    def __init__(self):
        self.active_users = 0
        self.request_times: List[float] = []
        
    async def generate_request(self, scenario: TestScenario) -> Dict[str, Any]:
        """Генерация запроса"""
        # Simulate request
        await asyncio.sleep(0.001)
        
        # Random response time based on load
        base_time = random.uniform(50, 200)
        load_factor = 1 + (self.active_users / 1000)
        response_time = base_time * load_factor * random.uniform(0.8, 1.5)
        
        # Random errors
        error = random.random() < 0.02  # 2% error rate
        
        status_code = 500 if error else 200
        
        return {
            "response_time": response_time,
            "status_code": status_code,
            "bytes": random.randint(1000, 50000),
            "error": error
        }
        
    async def run_virtual_user(
        self,
        scenario: TestScenario,
        duration: float,
        results: List[Dict]
    ):
        """Запуск виртуального пользователя"""
        self.active_users += 1
        end_time = datetime.now() + timedelta(seconds=duration)
        
        try:
            while datetime.now() < end_time:
                result = await self.generate_request(scenario)
                results.append(result)
                
                # Think time
                await asyncio.sleep(scenario.think_time_ms / 1000)
        finally:
            self.active_users -= 1


class TestExecutor:
    """Исполнитель тестов"""
    
    def __init__(self):
        self.generator = LoadGenerator()
        self.running_tests: Dict[str, asyncio.Task] = {}
        
    async def execute(
        self,
        scenario: TestScenario,
        test_type: TestType,
        profile: Optional[LoadProfile] = None
    ) -> TestResult:
        """Выполнение теста"""
        test_id = f"test_{uuid.uuid4().hex[:8]}"
        
        result = TestResult(
            test_id=test_id,
            scenario_id=scenario.scenario_id,
            status=TestStatus.RUNNING,
            started_at=datetime.now()
        )
        
        results: List[Dict] = []
        
        # Determine load based on test type
        if test_type == TestType.LOAD:
            users = scenario.virtual_users
            duration = scenario.duration_seconds
        elif test_type == TestType.STRESS:
            users = scenario.virtual_users * 2
            duration = scenario.duration_seconds
        elif test_type == TestType.SPIKE:
            users = scenario.virtual_users * 5
            duration = 30
        elif test_type in [TestType.SOAK, TestType.ENDURANCE]:
            users = scenario.virtual_users
            duration = scenario.duration_seconds * 4
        else:
            users = scenario.virtual_users
            duration = scenario.duration_seconds
            
        # Scale down for demo
        users = min(users, 10)
        duration = min(duration, 1)
        
        # Start virtual users
        tasks = []
        for _ in range(users):
            task = asyncio.create_task(
                self.generator.run_virtual_user(scenario, duration, results)
            )
            tasks.append(task)
            await asyncio.sleep(scenario.ramp_up_seconds / users / 100)  # Scaled ramp-up
            
        # Wait for completion
        await asyncio.gather(*tasks)
        
        # Calculate results
        result.completed_at = datetime.now()
        result.duration_seconds = (result.completed_at - result.started_at).total_seconds()
        result.status = TestStatus.COMPLETED
        
        if results:
            response_times = [r["response_time"] for r in results]
            response_times.sort()
            
            result.total_requests = len(results)
            result.successful_requests = len([r for r in results if not r["error"]])
            result.failed_requests = result.total_requests - result.successful_requests
            
            result.avg_response_time = statistics.mean(response_times)
            result.min_response_time = min(response_times)
            result.max_response_time = max(response_times)
            result.p50_response_time = response_times[int(len(response_times) * 0.5)]
            result.p90_response_time = response_times[int(len(response_times) * 0.9)]
            result.p95_response_time = response_times[int(len(response_times) * 0.95)]
            result.p99_response_time = response_times[min(int(len(response_times) * 0.99), len(response_times) - 1)]
            
            result.requests_per_second = result.total_requests / max(result.duration_seconds, 0.001)
            result.bytes_per_second = sum(r["bytes"] for r in results) / max(result.duration_seconds, 0.001)
            
            result.error_rate = result.failed_requests / result.total_requests * 100 if result.total_requests > 0 else 0
            
            # Errors by type
            for r in results:
                if r["error"]:
                    error_type = f"HTTP_{r['status_code']}"
                    result.errors_by_type[error_type] = result.errors_by_type.get(error_type, 0) + 1
                    
        return result


class SLAValidator:
    """Валидатор SLA"""
    
    def validate(self, result: TestResult, sla: SLADefinition) -> bool:
        """Валидация SLA"""
        violations = []
        
        # Response time
        if result.avg_response_time > sla.max_response_time_ms:
            violations.append(f"Avg response time {result.avg_response_time:.0f}ms > {sla.max_response_time_ms}ms")
            
        if result.p95_response_time > sla.max_p95_response_time_ms:
            violations.append(f"P95 response time {result.p95_response_time:.0f}ms > {sla.max_p95_response_time_ms}ms")
            
        # Error rate
        if result.error_rate > sla.max_error_rate:
            violations.append(f"Error rate {result.error_rate:.2f}% > {sla.max_error_rate}%")
            
        # Throughput
        if result.requests_per_second < sla.min_throughput:
            violations.append(f"Throughput {result.requests_per_second:.0f} req/s < {sla.min_throughput} req/s")
            
        result.sla_violations = violations
        result.sla_passed = len(violations) == 0
        
        return result.sla_passed


class BaselineManager:
    """Менеджер базовых показателей"""
    
    def __init__(self):
        self.baselines: Dict[str, Baseline] = {}
        
    def create_baseline(self, result: TestResult, name: str = "") -> Baseline:
        """Создание baseline"""
        baseline = Baseline(
            baseline_id=f"baseline_{uuid.uuid4().hex[:8]}",
            name=name or f"Baseline {datetime.now().strftime('%Y%m%d')}",
            scenario_id=result.scenario_id,
            avg_response_time=result.avg_response_time,
            p95_response_time=result.p95_response_time,
            p99_response_time=result.p99_response_time,
            throughput=result.requests_per_second,
            error_rate=result.error_rate,
            test_id=result.test_id
        )
        
        self.baselines[baseline.baseline_id] = baseline
        return baseline
        
    def compare(self, result: TestResult, baseline_id: str) -> Dict[str, Any]:
        """Сравнение с baseline"""
        baseline = self.baselines.get(baseline_id)
        if not baseline:
            return {}
            
        def calc_change(current: float, baseline_val: float) -> tuple:
            if baseline_val == 0:
                return 0, ComparisonResult.UNCHANGED
            change = ((current - baseline_val) / baseline_val) * 100
            
            if abs(change) < 5:
                status = ComparisonResult.UNCHANGED
            elif change < 0:
                status = ComparisonResult.IMPROVED
            else:
                status = ComparisonResult.DEGRADED
                
            return change, status
            
        response_change, response_status = calc_change(result.avg_response_time, baseline.avg_response_time)
        p95_change, p95_status = calc_change(result.p95_response_time, baseline.p95_response_time)
        throughput_change, throughput_status = calc_change(result.requests_per_second, baseline.throughput)
        error_change, error_status = calc_change(result.error_rate, baseline.error_rate)
        
        # For throughput, higher is better
        if throughput_change > 5:
            throughput_status = ComparisonResult.IMPROVED
        elif throughput_change < -5:
            throughput_status = ComparisonResult.DEGRADED
            
        return {
            "response_time": {
                "baseline": baseline.avg_response_time,
                "current": result.avg_response_time,
                "change_percent": response_change,
                "status": response_status.value
            },
            "p95_response_time": {
                "baseline": baseline.p95_response_time,
                "current": result.p95_response_time,
                "change_percent": p95_change,
                "status": p95_status.value
            },
            "throughput": {
                "baseline": baseline.throughput,
                "current": result.requests_per_second,
                "change_percent": throughput_change,
                "status": throughput_status.value
            },
            "error_rate": {
                "baseline": baseline.error_rate,
                "current": result.error_rate,
                "change_percent": error_change,
                "status": error_status.value
            }
        }


class ReportGenerator:
    """Генератор отчётов"""
    
    def generate_report(self, result: TestResult) -> str:
        """Генерация отчёта"""
        lines = []
        
        lines.append("=" * 60)
        lines.append("Performance Test Report")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"Test ID: {result.test_id}")
        lines.append(f"Scenario: {result.scenario_id}")
        lines.append(f"Status: {result.status.value}")
        lines.append(f"Duration: {result.duration_seconds:.2f}s")
        lines.append("")
        
        lines.append("--- Request Summary ---")
        lines.append(f"Total Requests: {result.total_requests:,}")
        lines.append(f"Successful: {result.successful_requests:,}")
        lines.append(f"Failed: {result.failed_requests:,}")
        lines.append(f"Error Rate: {result.error_rate:.2f}%")
        lines.append("")
        
        lines.append("--- Response Times (ms) ---")
        lines.append(f"Average: {result.avg_response_time:.2f}")
        lines.append(f"Min: {result.min_response_time:.2f}")
        lines.append(f"Max: {result.max_response_time:.2f}")
        lines.append(f"P50: {result.p50_response_time:.2f}")
        lines.append(f"P90: {result.p90_response_time:.2f}")
        lines.append(f"P95: {result.p95_response_time:.2f}")
        lines.append(f"P99: {result.p99_response_time:.2f}")
        lines.append("")
        
        lines.append("--- Throughput ---")
        lines.append(f"Requests/sec: {result.requests_per_second:.2f}")
        lines.append(f"Bytes/sec: {result.bytes_per_second / 1024:.2f} KB/s")
        lines.append("")
        
        if result.sla_violations:
            lines.append("--- SLA Violations ---")
            for violation in result.sla_violations:
                lines.append(f"  ⚠ {violation}")
            lines.append("")
            
        lines.append("=" * 60)
        
        return "\n".join(lines)


class PerformanceTestingPlatform:
    """Платформа тестирования производительности"""
    
    def __init__(self):
        self.scenarios: Dict[str, TestScenario] = {}
        self.executor = TestExecutor()
        self.validator = SLAValidator()
        self.baseline_manager = BaselineManager()
        self.report_generator = ReportGenerator()
        self.test_results: List[TestResult] = []
        self.slas: Dict[str, SLADefinition] = {}
        
    def register_scenario(self, scenario: TestScenario):
        """Регистрация сценария"""
        self.scenarios[scenario.scenario_id] = scenario
        
    def register_sla(self, sla: SLADefinition):
        """Регистрация SLA"""
        self.slas[sla.sla_id] = sla
        
    async def run_test(
        self,
        scenario_id: str,
        test_type: TestType = TestType.LOAD,
        sla_id: str = ""
    ) -> TestResult:
        """Запуск теста"""
        scenario = self.scenarios.get(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")
            
        result = await self.executor.execute(scenario, test_type)
        
        # Validate SLA
        if sla_id:
            sla = self.slas.get(sla_id)
            if sla:
                self.validator.validate(result, sla)
                
        self.test_results.append(result)
        return result
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        return {
            "total_scenarios": len(self.scenarios),
            "total_tests": len(self.test_results),
            "tests_by_status": {
                status.value: len([t for t in self.test_results if t.status == status])
                for status in TestStatus
            },
            "sla_definitions": len(self.slas),
            "baselines": len(self.baseline_manager.baselines),
            "avg_response_time": (
                statistics.mean([t.avg_response_time for t in self.test_results])
                if self.test_results else 0
            ),
            "avg_throughput": (
                statistics.mean([t.requests_per_second for t in self.test_results])
                if self.test_results else 0
            )
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 177: Performance Testing Platform")
    print("=" * 60)
    
    async def demo():
        platform = PerformanceTestingPlatform()
        print("✓ Performance Testing Platform created")
        
        # Register test scenarios
        print("\n📋 Registering Test Scenarios...")
        
        scenarios = [
            TestScenario(
                scenario_id="api_health",
                name="API Health Check",
                description="Simple health endpoint test",
                target_url="https://api.example.com/health",
                target_method="GET",
                think_time_ms=500,
                ramp_up_seconds=30,
                duration_seconds=300,
                virtual_users=50
            ),
            TestScenario(
                scenario_id="api_search",
                name="Search API Test",
                description="Search functionality under load",
                target_url="https://api.example.com/search",
                target_method="POST",
                body='{"query": "test"}',
                think_time_ms=1000,
                duration_seconds=600,
                virtual_users=100
            ),
            TestScenario(
                scenario_id="api_checkout",
                name="Checkout Flow",
                description="E-commerce checkout process",
                target_url="https://api.example.com/checkout",
                target_method="POST",
                think_time_ms=2000,
                duration_seconds=300,
                virtual_users=25
            ),
        ]
        
        for scenario in scenarios:
            platform.register_scenario(scenario)
            print(f"  ✓ {scenario.name}")
            print(f"    URL: {scenario.target_url}")
            print(f"    Users: {scenario.virtual_users}, Duration: {scenario.duration_seconds}s")
            
        # Register SLA
        print("\n📊 Defining SLA...")
        
        sla = SLADefinition(
            sla_id="api_sla",
            name="API Performance SLA",
            max_response_time_ms=300,
            max_p95_response_time_ms=500,
            max_error_rate=1.0,
            min_throughput=100
        )
        platform.register_sla(sla)
        
        print(f"  SLA: {sla.name}")
        print(f"    Max Avg Response: {sla.max_response_time_ms}ms")
        print(f"    Max P95 Response: {sla.max_p95_response_time_ms}ms")
        print(f"    Max Error Rate: {sla.max_error_rate}%")
        print(f"    Min Throughput: {sla.min_throughput} req/s")
        
        # Run load test
        print("\n🚀 Running Load Test...")
        
        result = await platform.run_test("api_health", TestType.LOAD, "api_sla")
        
        print(f"\n  Test: {result.test_id}")
        print(f"  Status: {result.status.value}")
        print(f"  Duration: {result.duration_seconds:.2f}s")
        
        print("\n  📈 Results:")
        print(f"    Total Requests: {result.total_requests:,}")
        print(f"    Successful: {result.successful_requests:,}")
        print(f"    Failed: {result.failed_requests:,}")
        print(f"    Error Rate: {result.error_rate:.2f}%")
        
        print("\n  ⏱ Response Times (ms):")
        print(f"    Average: {result.avg_response_time:.2f}")
        print(f"    Min: {result.min_response_time:.2f}")
        print(f"    Max: {result.max_response_time:.2f}")
        print(f"    P50: {result.p50_response_time:.2f}")
        print(f"    P90: {result.p90_response_time:.2f}")
        print(f"    P95: {result.p95_response_time:.2f}")
        print(f"    P99: {result.p99_response_time:.2f}")
        
        print("\n  📊 Throughput:")
        print(f"    {result.requests_per_second:.2f} req/s")
        print(f"    {result.bytes_per_second / 1024:.2f} KB/s")
        
        print(f"\n  SLA Status: {'✓ PASSED' if result.sla_passed else '✗ FAILED'}")
        if result.sla_violations:
            print("  Violations:")
            for v in result.sla_violations:
                print(f"    ⚠ {v}")
                
        # Create baseline
        print("\n📌 Creating Baseline...")
        
        baseline = platform.baseline_manager.create_baseline(result, "Production Baseline")
        print(f"  Baseline: {baseline.name}")
        print(f"    Avg Response: {baseline.avg_response_time:.2f}ms")
        print(f"    P95 Response: {baseline.p95_response_time:.2f}ms")
        print(f"    Throughput: {baseline.throughput:.2f} req/s")
        print(f"    Error Rate: {baseline.error_rate:.2f}%")
        
        # Run stress test
        print("\n🔥 Running Stress Test...")
        
        stress_result = await platform.run_test("api_search", TestType.STRESS, "api_sla")
        
        print(f"\n  Stress Test Results:")
        print(f"    Total Requests: {stress_result.total_requests:,}")
        print(f"    Avg Response: {stress_result.avg_response_time:.2f}ms")
        print(f"    P95 Response: {stress_result.p95_response_time:.2f}ms")
        print(f"    Error Rate: {stress_result.error_rate:.2f}%")
        print(f"    Throughput: {stress_result.requests_per_second:.2f} req/s")
        
        # Compare with baseline
        print("\n📊 Comparing with Baseline...")
        
        comparison = platform.baseline_manager.compare(stress_result, baseline.baseline_id)
        
        print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────┐")
        print("  │ Metric              │ Baseline     │ Current      │ Change   │ Status    │")
        print("  ├────────────────────────────────────────────────────────────────────────────────────────┤")
        
        for metric_name, data in comparison.items():
            name = metric_name.replace("_", " ").title()[:19].ljust(19)
            baseline_val = f"{data['baseline']:.2f}".rjust(12)
            current_val = f"{data['current']:.2f}".rjust(12)
            change = f"{data['change_percent']:+.1f}%".rjust(8)
            
            status_icons = {
                "improved": "🟢",
                "degraded": "🔴",
                "unchanged": "⚪"
            }
            status = f"{status_icons.get(data['status'], '⚪')} {data['status']}".ljust(10)
            print(f"  │ {name} │ {baseline_val} │ {current_val} │ {change} │ {status} │")
            
        print("  └────────────────────────────────────────────────────────────────────────────────────────┘")
        
        # Run spike test
        print("\n⚡ Running Spike Test...")
        
        spike_result = await platform.run_test("api_checkout", TestType.SPIKE)
        
        print(f"\n  Spike Test Results:")
        print(f"    Total Requests: {spike_result.total_requests:,}")
        print(f"    Avg Response: {spike_result.avg_response_time:.2f}ms")
        print(f"    Max Response: {spike_result.max_response_time:.2f}ms")
        print(f"    Error Rate: {spike_result.error_rate:.2f}%")
        
        # Test summary
        print("\n📋 Test Summary:")
        
        print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
        print("  │ Test               │ Type     │ Requests │ Avg (ms) │ P95 (ms) │ Errors  │ RPS      │ SLA     │")
        print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
        
        test_types = ["load", "stress", "spike"]
        for i, test in enumerate(platform.test_results):
            name = test.test_id[:18].ljust(18)
            ttype = test_types[i % len(test_types)][:8].ljust(8)
            requests = f"{test.total_requests:,}".rjust(8)
            avg = f"{test.avg_response_time:.0f}".rjust(8)
            p95 = f"{test.p95_response_time:.0f}".rjust(8)
            errors = f"{test.error_rate:.1f}%".rjust(7)
            rps = f"{test.requests_per_second:.0f}".rjust(8)
            sla = "✓ Pass" if test.sla_passed else "✗ Fail"
            print(f"  │ {name} │ {ttype} │ {requests} │ {avg} │ {p95} │ {errors} │ {rps} │ {sla:>7} │")
            
        print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
        
        # Generate report
        print("\n📄 Performance Report:")
        
        report = platform.report_generator.generate_report(result)
        for line in report.split("\n")[:25]:
            print(f"  {line}")
            
        # Platform statistics
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Scenarios: {stats['total_scenarios']}")
        print(f"  Total Tests: {stats['total_tests']}")
        print(f"  SLA Definitions: {stats['sla_definitions']}")
        print(f"  Baselines: {stats['baselines']}")
        print(f"  Avg Response Time: {stats['avg_response_time']:.2f}ms")
        print(f"  Avg Throughput: {stats['avg_throughput']:.2f} req/s")
        
        # Dashboard
        print("\n┌────────────────────────────────────────────────────────────────────┐")
        print("│                Performance Testing Dashboard                       │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Test Scenarios:              {stats['total_scenarios']:>10}                       │")
        print(f"│ Total Tests Run:             {stats['total_tests']:>10}                       │")
        print(f"│ SLA Definitions:             {stats['sla_definitions']:>10}                       │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Baselines:                   {stats['baselines']:>10}                       │")
        print(f"│ Avg Response Time:           {stats['avg_response_time']:>10.2f} ms               │")
        print(f"│ Avg Throughput:              {stats['avg_throughput']:>10.2f} req/s            │")
        print("├────────────────────────────────────────────────────────────────────┤")
        completed = stats['tests_by_status'].get('completed', 0)
        failed = stats['tests_by_status'].get('failed', 0)
        print(f"│ Tests Completed:             {completed:>10}                       │")
        print(f"│ Tests Failed:                {failed:>10}                       │")
        print("└────────────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Performance Testing Platform initialized!")
    print("=" * 60)
