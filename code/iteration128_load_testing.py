#!/usr/bin/env python3
"""
Server Init - Iteration 128: Load Testing Platform
Платформа нагрузочного тестирования

Функционал:
- Test Scenarios - сценарии тестирования
- Virtual Users - виртуальные пользователи
- Request Generation - генерация запросов
- Metrics Collection - сбор метрик
- Threshold Validation - валидация порогов
- Report Generation - генерация отчётов
- Distributed Testing - распределённое тестирование
- Real-time Monitoring - мониторинг в реальном времени
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from collections import defaultdict
import uuid
import random
import math


class TestStatus(Enum):
    """Статус теста"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RequestMethod(Enum):
    """HTTP метод"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class ThresholdOperator(Enum):
    """Оператор порога"""
    LT = "lt"          # Less than
    LTE = "lte"        # Less than or equal
    GT = "gt"          # Greater than
    GTE = "gte"        # Greater than or equal
    EQ = "eq"          # Equal
    P95_LT = "p95_lt"  # 95th percentile less than
    P99_LT = "p99_lt"  # 99th percentile less than


@dataclass
class RequestConfig:
    """Конфигурация запроса"""
    request_id: str
    name: str = ""
    
    # HTTP
    method: RequestMethod = RequestMethod.GET
    url: str = ""
    headers: Dict = field(default_factory=dict)
    body: Optional[Dict] = None
    
    # Timing
    timeout: int = 30000  # ms
    
    # Weight
    weight: float = 1.0  # For weighted distribution


@dataclass
class VirtualUser:
    """Виртуальный пользователь"""
    user_id: str
    scenario_id: str = ""
    
    # Status
    active: bool = True
    
    # Metrics
    requests_made: int = 0
    requests_failed: int = 0
    
    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    last_request_at: Optional[datetime] = None


@dataclass
class ResponseMetrics:
    """Метрики ответа"""
    request_id: str
    user_id: str = ""
    
    # Response
    status_code: int = 200
    response_time_ms: int = 0
    response_size_bytes: int = 0
    
    # Status
    success: bool = True
    error_message: str = ""
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Threshold:
    """Порог"""
    threshold_id: str
    name: str = ""
    
    # Metric
    metric: str = "response_time_ms"
    operator: ThresholdOperator = ThresholdOperator.LT
    value: float = 1000
    
    # Result
    passed: Optional[bool] = None
    actual_value: Optional[float] = None


@dataclass
class LoadProfile:
    """Профиль нагрузки"""
    profile_id: str
    name: str = ""
    
    # Stages
    stages: List[Dict] = field(default_factory=list)
    # Stage format: {"duration": 60, "target_vus": 100}
    
    # Current state
    current_vus: int = 0


@dataclass
class TestScenario:
    """Сценарий тестирования"""
    scenario_id: str
    name: str = ""
    description: str = ""
    
    # Requests
    requests: List[str] = field(default_factory=list)  # Request IDs
    
    # Profile
    profile_id: str = ""
    
    # Thresholds
    thresholds: List[str] = field(default_factory=list)  # Threshold IDs
    
    # Status
    status: TestStatus = TestStatus.PENDING
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class TestResult:
    """Результат теста"""
    result_id: str
    scenario_id: str = ""
    
    # Duration
    duration_seconds: int = 0
    
    # Requests
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
    
    # Virtual users
    max_vus: int = 0
    
    # Thresholds
    thresholds_passed: int = 0
    thresholds_failed: int = 0
    
    # Status
    passed: bool = True


class RequestManager:
    """Менеджер запросов"""
    
    def __init__(self):
        self.requests: Dict[str, RequestConfig] = {}
        
    def create(self, name: str, method: RequestMethod, url: str,
                headers: Dict = None, body: Dict = None, **kwargs) -> RequestConfig:
        """Создание запроса"""
        request = RequestConfig(
            request_id=f"req_{uuid.uuid4().hex[:8]}",
            name=name,
            method=method,
            url=url,
            headers=headers or {},
            body=body,
            **kwargs
        )
        self.requests[request.request_id] = request
        return request


class LoadProfileManager:
    """Менеджер профилей нагрузки"""
    
    def __init__(self):
        self.profiles: Dict[str, LoadProfile] = {}
        
    def create(self, name: str, stages: List[Dict]) -> LoadProfile:
        """Создание профиля"""
        profile = LoadProfile(
            profile_id=f"profile_{uuid.uuid4().hex[:8]}",
            name=name,
            stages=stages
        )
        self.profiles[profile.profile_id] = profile
        return profile
        
    def constant(self, name: str, vus: int, duration: int) -> LoadProfile:
        """Постоянная нагрузка"""
        return self.create(name, [{"duration": duration, "target_vus": vus}])
        
    def ramping(self, name: str, stages: List[Tuple]) -> LoadProfile:
        """Нарастающая нагрузка"""
        stage_list = [{"duration": d, "target_vus": v} for d, v in stages]
        return self.create(name, stage_list)
        
    def spike(self, name: str, base_vus: int, spike_vus: int,
               warmup: int = 60, spike_duration: int = 30) -> LoadProfile:
        """Пиковая нагрузка"""
        stages = [
            {"duration": warmup, "target_vus": base_vus},
            {"duration": spike_duration, "target_vus": spike_vus},
            {"duration": spike_duration, "target_vus": base_vus}
        ]
        return self.create(name, stages)


class ThresholdManager:
    """Менеджер порогов"""
    
    def __init__(self):
        self.thresholds: Dict[str, Threshold] = {}
        
    def create(self, name: str, metric: str,
                operator: ThresholdOperator, value: float) -> Threshold:
        """Создание порога"""
        threshold = Threshold(
            threshold_id=f"threshold_{uuid.uuid4().hex[:8]}",
            name=name,
            metric=metric,
            operator=operator,
            value=value
        )
        self.thresholds[threshold.threshold_id] = threshold
        return threshold
        
    def evaluate(self, threshold_id: str, metrics: Dict) -> bool:
        """Оценка порога"""
        threshold = self.thresholds.get(threshold_id)
        if not threshold:
            return False
            
        actual = metrics.get(threshold.metric, 0)
        threshold.actual_value = actual
        
        if threshold.operator == ThresholdOperator.LT:
            passed = actual < threshold.value
        elif threshold.operator == ThresholdOperator.LTE:
            passed = actual <= threshold.value
        elif threshold.operator == ThresholdOperator.GT:
            passed = actual > threshold.value
        elif threshold.operator == ThresholdOperator.GTE:
            passed = actual >= threshold.value
        elif threshold.operator == ThresholdOperator.EQ:
            passed = actual == threshold.value
        elif threshold.operator == ThresholdOperator.P95_LT:
            passed = metrics.get("p95_response_time", 0) < threshold.value
        elif threshold.operator == ThresholdOperator.P99_LT:
            passed = metrics.get("p99_response_time", 0) < threshold.value
        else:
            passed = False
            
        threshold.passed = passed
        return passed


class ScenarioRunner:
    """Запуск сценариев"""
    
    def __init__(self, request_manager: RequestManager,
                 profile_manager: LoadProfileManager,
                 threshold_manager: ThresholdManager):
        self.request_manager = request_manager
        self.profile_manager = profile_manager
        self.threshold_manager = threshold_manager
        self.scenarios: Dict[str, TestScenario] = {}
        self.virtual_users: Dict[str, List[VirtualUser]] = defaultdict(list)
        self.metrics: Dict[str, List[ResponseMetrics]] = defaultdict(list)
        
    def create_scenario(self, name: str, request_ids: List[str],
                         profile_id: str, threshold_ids: List[str] = None,
                         **kwargs) -> TestScenario:
        """Создание сценария"""
        scenario = TestScenario(
            scenario_id=f"scenario_{uuid.uuid4().hex[:8]}",
            name=name,
            requests=request_ids,
            profile_id=profile_id,
            thresholds=threshold_ids or [],
            **kwargs
        )
        self.scenarios[scenario.scenario_id] = scenario
        return scenario
        
    async def run(self, scenario_id: str) -> TestResult:
        """Запуск сценария"""
        scenario = self.scenarios.get(scenario_id)
        if not scenario:
            return None
            
        profile = self.profile_manager.profiles.get(scenario.profile_id)
        if not profile:
            return None
            
        scenario.status = TestStatus.RUNNING
        scenario.started_at = datetime.now()
        
        # Simulate test execution
        for stage in profile.stages:
            target_vus = stage["target_vus"]
            duration = stage["duration"]
            
            # Create virtual users
            while len(self.virtual_users[scenario_id]) < target_vus:
                vu = VirtualUser(
                    user_id=f"vu_{uuid.uuid4().hex[:8]}",
                    scenario_id=scenario_id
                )
                self.virtual_users[scenario_id].append(vu)
                
            # Simulate requests
            for _ in range(min(duration * 10, 100)):  # Limit iterations for demo
                for vu in self.virtual_users[scenario_id][:target_vus]:
                    await self._simulate_request(scenario, vu)
                    
                await asyncio.sleep(0.01)  # Small delay for demo
                
        scenario.status = TestStatus.COMPLETED
        scenario.completed_at = datetime.now()
        
        return self._calculate_results(scenario)
        
    async def _simulate_request(self, scenario: TestScenario, vu: VirtualUser):
        """Симуляция запроса"""
        # Select random request
        request_id = random.choice(scenario.requests)
        request = self.request_manager.requests.get(request_id)
        
        if not request:
            return
            
        # Simulate response
        success = random.random() > 0.02  # 2% error rate
        response_time = int(random.gauss(150, 50))  # ~150ms average
        response_time = max(10, min(response_time, 5000))  # Clamp
        
        if not success:
            response_time *= 3  # Failures are slower
            
        metric = ResponseMetrics(
            request_id=request_id,
            user_id=vu.user_id,
            status_code=200 if success else 500,
            response_time_ms=response_time,
            response_size_bytes=random.randint(100, 10000),
            success=success,
            error_message="" if success else "Simulated error"
        )
        
        self.metrics[scenario.scenario_id].append(metric)
        
        vu.requests_made += 1
        if not success:
            vu.requests_failed += 1
        vu.last_request_at = datetime.now()
        
    def _calculate_results(self, scenario: TestScenario) -> TestResult:
        """Расчёт результатов"""
        metrics = self.metrics.get(scenario.scenario_id, [])
        
        if not metrics:
            return TestResult(
                result_id=f"result_{uuid.uuid4().hex[:8]}",
                scenario_id=scenario.scenario_id
            )
            
        response_times = sorted([m.response_time_ms for m in metrics])
        
        total = len(metrics)
        successful = len([m for m in metrics if m.success])
        
        duration = (scenario.completed_at - scenario.started_at).total_seconds() if scenario.started_at else 0
        
        # Calculate percentiles
        p50_idx = int(len(response_times) * 0.50)
        p90_idx = int(len(response_times) * 0.90)
        p95_idx = int(len(response_times) * 0.95)
        p99_idx = int(len(response_times) * 0.99)
        
        result = TestResult(
            result_id=f"result_{uuid.uuid4().hex[:8]}",
            scenario_id=scenario.scenario_id,
            duration_seconds=int(duration),
            total_requests=total,
            successful_requests=successful,
            failed_requests=total - successful,
            avg_response_time=sum(response_times) / len(response_times),
            min_response_time=min(response_times),
            max_response_time=max(response_times),
            p50_response_time=response_times[p50_idx] if p50_idx < len(response_times) else 0,
            p90_response_time=response_times[p90_idx] if p90_idx < len(response_times) else 0,
            p95_response_time=response_times[p95_idx] if p95_idx < len(response_times) else 0,
            p99_response_time=response_times[p99_idx] if p99_idx < len(response_times) else 0,
            requests_per_second=total / duration if duration > 0 else 0,
            max_vus=len(self.virtual_users.get(scenario.scenario_id, []))
        )
        
        # Evaluate thresholds
        metrics_dict = {
            "response_time_ms": result.avg_response_time,
            "p95_response_time": result.p95_response_time,
            "p99_response_time": result.p99_response_time,
            "error_rate": (result.failed_requests / result.total_requests * 100) if result.total_requests > 0 else 0,
            "rps": result.requests_per_second
        }
        
        for threshold_id in scenario.thresholds:
            if self.threshold_manager.evaluate(threshold_id, metrics_dict):
                result.thresholds_passed += 1
            else:
                result.thresholds_failed += 1
                result.passed = False
                
        return result


class LoadTestingPlatform:
    """Платформа нагрузочного тестирования"""
    
    def __init__(self):
        self.request_manager = RequestManager()
        self.profile_manager = LoadProfileManager()
        self.threshold_manager = ThresholdManager()
        self.scenario_runner = ScenarioRunner(
            self.request_manager,
            self.profile_manager,
            self.threshold_manager
        )
        self.results: List[TestResult] = []
        
    async def quick_test(self, url: str, vus: int = 10, duration: int = 30) -> TestResult:
        """Быстрый тест"""
        request = self.request_manager.create("Quick Test", RequestMethod.GET, url)
        profile = self.profile_manager.constant("Quick Profile", vus, duration)
        
        threshold_rt = self.threshold_manager.create(
            "Response Time < 500ms",
            "response_time_ms",
            ThresholdOperator.LT,
            500
        )
        
        scenario = self.scenario_runner.create_scenario(
            "Quick Load Test",
            [request.request_id],
            profile.profile_id,
            [threshold_rt.threshold_id]
        )
        
        result = await self.scenario_runner.run(scenario.scenario_id)
        self.results.append(result)
        return result
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        scenarios = list(self.scenario_runner.scenarios.values())
        
        return {
            "total_requests": len(self.request_manager.requests),
            "total_profiles": len(self.profile_manager.profiles),
            "total_thresholds": len(self.threshold_manager.thresholds),
            "total_scenarios": len(scenarios),
            "completed_tests": len([s for s in scenarios if s.status == TestStatus.COMPLETED]),
            "total_results": len(self.results)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 128: Load Testing Platform")
    print("=" * 60)
    
    async def demo():
        platform = LoadTestingPlatform()
        print("✓ Load Testing Platform created")
        
        # Create requests
        print("\n📝 Creating Test Requests...")
        
        requests_data = [
            ("Homepage", RequestMethod.GET, "https://api.example.com/"),
            ("User List", RequestMethod.GET, "https://api.example.com/users"),
            ("Create User", RequestMethod.POST, "https://api.example.com/users"),
            ("Get User", RequestMethod.GET, "https://api.example.com/users/1"),
            ("Update User", RequestMethod.PUT, "https://api.example.com/users/1"),
            ("Delete User", RequestMethod.DELETE, "https://api.example.com/users/1")
        ]
        
        created_requests = []
        for name, method, url in requests_data:
            request = platform.request_manager.create(name, method, url)
            created_requests.append(request)
            print(f"  ✓ {name} ({method.value})")
            
        # Create load profiles
        print("\n📊 Creating Load Profiles...")
        
        # Constant load
        constant_profile = platform.profile_manager.constant(
            "Constant Load",
            vus=50,
            duration=60
        )
        print(f"  ✓ {constant_profile.name}: 50 VUs for 60s")
        
        # Ramping load
        ramping_profile = platform.profile_manager.ramping(
            "Ramping Load",
            [(30, 10), (60, 50), (60, 100), (30, 0)]
        )
        print(f"  ✓ {ramping_profile.name}: 10->50->100->0 VUs")
        
        # Spike test
        spike_profile = platform.profile_manager.spike(
            "Spike Test",
            base_vus=20,
            spike_vus=200,
            warmup=30,
            spike_duration=10
        )
        print(f"  ✓ {spike_profile.name}: 20->200->20 VUs")
        
        # Create thresholds
        print("\n🎯 Creating Thresholds...")
        
        thresholds_data = [
            ("Avg Response Time < 200ms", "response_time_ms", ThresholdOperator.LT, 200),
            ("P95 Response Time < 500ms", "p95_response_time", ThresholdOperator.P95_LT, 500),
            ("P99 Response Time < 1000ms", "p99_response_time", ThresholdOperator.P99_LT, 1000),
            ("Error Rate < 5%", "error_rate", ThresholdOperator.LT, 5),
            ("RPS > 100", "rps", ThresholdOperator.GT, 100)
        ]
        
        created_thresholds = []
        for name, metric, op, value in thresholds_data:
            threshold = platform.threshold_manager.create(name, metric, op, value)
            created_thresholds.append(threshold)
            print(f"  ✓ {name}")
            
        # Create scenarios
        print("\n🎬 Creating Test Scenarios...")
        
        # Scenario 1: API Smoke Test
        smoke_scenario = platform.scenario_runner.create_scenario(
            "API Smoke Test",
            [created_requests[0].request_id, created_requests[1].request_id],
            constant_profile.profile_id,
            [created_thresholds[0].threshold_id, created_thresholds[3].threshold_id]
        )
        print(f"  ✓ {smoke_scenario.name}")
        
        # Scenario 2: Full API Load Test
        load_scenario = platform.scenario_runner.create_scenario(
            "Full API Load Test",
            [r.request_id for r in created_requests],
            ramping_profile.profile_id,
            [t.threshold_id for t in created_thresholds]
        )
        print(f"  ✓ {load_scenario.name}")
        
        # Scenario 3: Spike Test
        spike_scenario = platform.scenario_runner.create_scenario(
            "API Spike Test",
            [created_requests[0].request_id, created_requests[3].request_id],
            spike_profile.profile_id,
            [created_thresholds[0].threshold_id, created_thresholds[1].threshold_id]
        )
        print(f"  ✓ {spike_scenario.name}")
        
        # Run tests
        print("\n🚀 Running Load Tests...")
        
        results = []
        
        for scenario in [smoke_scenario, load_scenario]:
            print(f"\n  Running: {scenario.name}...")
            result = await platform.scenario_runner.run(scenario.scenario_id)
            results.append(result)
            platform.results.append(result)
            
            status_icon = "✅" if result.passed else "❌"
            print(f"  {status_icon} {scenario.name} - {'PASSED' if result.passed else 'FAILED'}")
            
        # Display results
        print("\n📊 Test Results:")
        
        for result in results:
            scenario = platform.scenario_runner.scenarios.get(result.scenario_id)
            
            print(f"\n  📋 {scenario.name if scenario else 'Unknown'}:")
            print(f"     Duration: {result.duration_seconds}s")
            print(f"     Total Requests: {result.total_requests}")
            print(f"     Successful: {result.successful_requests} ({result.successful_requests/result.total_requests*100:.1f}%)")
            print(f"     Failed: {result.failed_requests}")
            print(f"     RPS: {result.requests_per_second:.1f}")
            print(f"     Max VUs: {result.max_vus}")
            
            print(f"\n     Response Times:")
            print(f"       Avg: {result.avg_response_time:.1f}ms")
            print(f"       Min: {result.min_response_time:.1f}ms")
            print(f"       Max: {result.max_response_time:.1f}ms")
            print(f"       P50: {result.p50_response_time:.1f}ms")
            print(f"       P90: {result.p90_response_time:.1f}ms")
            print(f"       P95: {result.p95_response_time:.1f}ms")
            print(f"       P99: {result.p99_response_time:.1f}ms")
            
            print(f"\n     Thresholds: {result.thresholds_passed} passed, {result.thresholds_failed} failed")
            
        # Threshold details
        print("\n🎯 Threshold Results:")
        
        for threshold in platform.threshold_manager.thresholds.values():
            if threshold.passed is not None:
                icon = "✅" if threshold.passed else "❌"
                print(f"  {icon} {threshold.name}")
                print(f"     Expected: {threshold.operator.value} {threshold.value}")
                print(f"     Actual: {threshold.actual_value:.1f}")
                
        # Quick test
        print("\n⚡ Quick Load Test Demo:")
        
        quick_result = await platform.quick_test(
            "https://api.example.com/health",
            vus=10,
            duration=10
        )
        
        print(f"  URL: https://api.example.com/health")
        print(f"  VUs: 10")
        print(f"  Duration: 10s")
        print(f"  Result: {'PASSED' if quick_result.passed else 'FAILED'}")
        print(f"  Avg Response: {quick_result.avg_response_time:.1f}ms")
        print(f"  RPS: {quick_result.requests_per_second:.1f}")
        
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Requests: {stats['total_requests']}")
        print(f"  Profiles: {stats['total_profiles']}")
        print(f"  Thresholds: {stats['total_thresholds']}")
        print(f"  Scenarios: {stats['total_scenarios']}")
        print(f"  Completed Tests: {stats['completed_tests']}")
        print(f"  Total Results: {stats['total_results']}")
        
        # Dashboard
        total_passed = len([r for r in platform.results if r.passed])
        total_failed = len([r for r in platform.results if not r.passed])
        
        print("\n📋 Load Testing Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │                Load Testing Overview                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Scenarios:    {stats['total_scenarios']:>10}                        │")
        print(f"  │ Completed Tests:    {stats['completed_tests']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Tests Passed:       {total_passed:>10}                        │")
        print(f"  │ Tests Failed:       {total_failed:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Requests:     {stats['total_requests']:>10}                        │")
        print(f"  │ Load Profiles:      {stats['total_profiles']:>10}                        │")
        print(f"  │ Thresholds:         {stats['total_thresholds']:>10}                        │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Load Testing Platform initialized!")
    print("=" * 60)
