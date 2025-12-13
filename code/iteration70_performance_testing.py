#!/usr/bin/env python3
"""
Server Init - Iteration 70: Performance Testing Platform
Платформа нагрузочного тестирования

Функционал:
- Load Testing - нагрузочное тестирование
- Stress Testing - стресс-тестирование
- Spike Testing - тестирование пиков
- Soak Testing - тестирование на выносливость
- Virtual Users - виртуальные пользователи
- Metrics Collection - сбор метрик
- Report Generation - генерация отчётов
- Threshold Validation - проверка порогов
"""

import json
import asyncio
import random
import statistics
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Awaitable
from enum import Enum
from collections import defaultdict
import uuid
import time


class TestType(Enum):
    """Тип теста"""
    LOAD = "load"           # Нагрузочный
    STRESS = "stress"       # Стресс
    SPIKE = "spike"         # Пик
    SOAK = "soak"          # Выносливость
    SMOKE = "smoke"        # Дымовой


class TestStatus(Enum):
    """Статус теста"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class MetricType(Enum):
    """Тип метрики"""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    LATENCY_P50 = "latency_p50"
    LATENCY_P90 = "latency_p90"
    LATENCY_P95 = "latency_p95"
    LATENCY_P99 = "latency_p99"
    CONCURRENT_USERS = "concurrent_users"
    REQUESTS_PER_SECOND = "requests_per_second"


class ThresholdOperator(Enum):
    """Оператор порога"""
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="
    EQ = "=="


@dataclass
class TestScenario:
    """Сценарий теста"""
    scenario_id: str
    name: str
    
    # Шаги
    steps: List[Dict[str, Any]] = field(default_factory=list)
    
    # Параметры
    weight: float = 1.0  # Вес сценария
    
    # Thinktime
    think_time_min: float = 1.0
    think_time_max: float = 3.0


@dataclass
class VirtualUser:
    """Виртуальный пользователь"""
    user_id: str
    scenario_id: str
    
    # Статистика
    requests_made: int = 0
    requests_failed: int = 0
    total_time: float = 0.0
    
    # Статус
    active: bool = True
    started_at: datetime = field(default_factory=datetime.now)


@dataclass
class RequestResult:
    """Результат запроса"""
    request_id: str
    
    # Запрос
    method: str = "GET"
    url: str = ""
    
    # Результат
    status_code: int = 200
    response_time: float = 0.0  # ms
    success: bool = True
    error: str = ""
    
    # Время
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Контекст
    user_id: str = ""
    scenario_id: str = ""


@dataclass
class Threshold:
    """Порог метрики"""
    metric: MetricType
    operator: ThresholdOperator
    value: float
    abort_on_fail: bool = False


@dataclass
class TestStage:
    """Этап теста"""
    duration_seconds: int
    target_vus: int  # Целевое количество VU


@dataclass
class TestConfig:
    """Конфигурация теста"""
    config_id: str
    name: str
    
    # Тип теста
    test_type: TestType = TestType.LOAD
    
    # Этапы
    stages: List[TestStage] = field(default_factory=list)
    
    # Сценарии
    scenarios: List[str] = field(default_factory=list)  # scenario_ids
    
    # Пороги
    thresholds: List[Threshold] = field(default_factory=list)
    
    # Цель
    target_url: str = ""
    
    # Опции
    max_redirects: int = 5
    timeout_seconds: float = 30.0


@dataclass
class TestRun:
    """Запуск теста"""
    run_id: str
    config_id: str
    
    # Статус
    status: TestStatus = TestStatus.PENDING
    
    # Время
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    
    # Результаты
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # Метрики
    metrics: Dict[str, List[float]] = field(default_factory=lambda: defaultdict(list))
    
    # Пороги
    threshold_results: Dict[str, bool] = field(default_factory=dict)


@dataclass
class TestReport:
    """Отчёт о тестировании"""
    report_id: str
    run_id: str
    
    # Время
    generated_at: datetime = field(default_factory=datetime.now)
    
    # Сводка
    summary: Dict[str, Any] = field(default_factory=dict)
    
    # Метрики
    metrics: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Пороги
    thresholds: Dict[str, Any] = field(default_factory=dict)
    
    # Timeline
    timeline: List[Dict[str, Any]] = field(default_factory=list)


class MetricsCollector:
    """Сборщик метрик"""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.timestamps: List[datetime] = []
        self.errors: List[str] = []
        self.status_codes: Dict[int, int] = defaultdict(int)
        
    def record(self, result: RequestResult):
        """Запись результата"""
        self.response_times.append(result.response_time)
        self.timestamps.append(result.timestamp)
        self.status_codes[result.status_code] += 1
        
        if not result.success:
            self.errors.append(result.error)
            
    def calculate_percentile(self, p: float) -> float:
        """Вычисление перцентиля"""
        if not self.response_times:
            return 0.0
            
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * p / 100)
        return sorted_times[min(index, len(sorted_times) - 1)]
        
    def get_metrics(self) -> Dict[str, float]:
        """Получение метрик"""
        if not self.response_times:
            return {}
            
        total = len(self.response_times)
        errors = len(self.errors)
        
        return {
            MetricType.RESPONSE_TIME.value: statistics.mean(self.response_times),
            MetricType.LATENCY_P50.value: self.calculate_percentile(50),
            MetricType.LATENCY_P90.value: self.calculate_percentile(90),
            MetricType.LATENCY_P95.value: self.calculate_percentile(95),
            MetricType.LATENCY_P99.value: self.calculate_percentile(99),
            MetricType.ERROR_RATE.value: errors / max(total, 1) * 100,
            "min_response_time": min(self.response_times),
            "max_response_time": max(self.response_times),
            "std_dev": statistics.stdev(self.response_times) if len(self.response_times) > 1 else 0
        }
        
    def get_throughput(self) -> float:
        """Вычисление throughput"""
        if len(self.timestamps) < 2:
            return 0.0
            
        duration = (self.timestamps[-1] - self.timestamps[0]).total_seconds()
        if duration <= 0:
            return 0.0
            
        return len(self.timestamps) / duration


class HTTPSimulator:
    """Симулятор HTTP запросов"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        
    async def execute(self, method: str, path: str,
                       **kwargs) -> RequestResult:
        """Выполнение запроса (симуляция)"""
        request_id = f"req_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        
        # Симуляция задержки и результата
        await asyncio.sleep(random.uniform(0.01, 0.2))
        
        # Симуляция разных ответов
        success_rate = 0.95
        is_success = random.random() < success_rate
        
        response_time = (time.time() - start_time) * 1000  # ms
        
        # Добавляем реалистичную вариацию
        response_time += random.uniform(10, 100)
        
        status_code = 200 if is_success else random.choice([500, 502, 503, 429])
        
        return RequestResult(
            request_id=request_id,
            method=method,
            url=f"{self.base_url}{path}",
            status_code=status_code,
            response_time=response_time,
            success=is_success,
            error="" if is_success else f"HTTP {status_code}"
        )


class LoadGenerator:
    """Генератор нагрузки"""
    
    def __init__(self, simulator: HTTPSimulator):
        self.simulator = simulator
        self.active_users: Dict[str, VirtualUser] = {}
        self.running = False
        
    async def spawn_user(self, scenario: TestScenario,
                         collector: MetricsCollector) -> VirtualUser:
        """Создание виртуального пользователя"""
        user = VirtualUser(
            user_id=f"vu_{uuid.uuid4().hex[:8]}",
            scenario_id=scenario.scenario_id
        )
        
        self.active_users[user.user_id] = user
        
        # Запуск в фоне
        asyncio.create_task(self._run_user(user, scenario, collector))
        
        return user
        
    async def _run_user(self, user: VirtualUser, scenario: TestScenario,
                        collector: MetricsCollector):
        """Работа виртуального пользователя"""
        while user.active and self.running:
            for step in scenario.steps:
                if not user.active or not self.running:
                    break
                    
                method = step.get("method", "GET")
                path = step.get("path", "/")
                
                result = await self.simulator.execute(method, path)
                result.user_id = user.user_id
                result.scenario_id = scenario.scenario_id
                
                collector.record(result)
                
                user.requests_made += 1
                user.total_time += result.response_time
                
                if not result.success:
                    user.requests_failed += 1
                    
                # Think time
                think_time = random.uniform(
                    scenario.think_time_min,
                    scenario.think_time_max
                )
                await asyncio.sleep(think_time)
                
    async def stop_user(self, user_id: str):
        """Остановка пользователя"""
        if user_id in self.active_users:
            self.active_users[user_id].active = False
            del self.active_users[user_id]
            
    async def ramp_to(self, target_vus: int, scenario: TestScenario,
                      collector: MetricsCollector, duration: float = 1.0):
        """Изменение количества VU"""
        current = len(self.active_users)
        
        if target_vus > current:
            # Добавляем пользователей
            to_add = target_vus - current
            interval = duration / max(to_add, 1)
            
            for _ in range(to_add):
                await self.spawn_user(scenario, collector)
                await asyncio.sleep(interval)
                
        elif target_vus < current:
            # Убираем пользователей
            to_remove = current - target_vus
            user_ids = list(self.active_users.keys())[:to_remove]
            
            for user_id in user_ids:
                await self.stop_user(user_id)
                
    def get_active_count(self) -> int:
        """Количество активных пользователей"""
        return len(self.active_users)


class ThresholdValidator:
    """Валидатор порогов"""
    
    def validate(self, threshold: Threshold, metrics: Dict[str, float]) -> bool:
        """Проверка порога"""
        metric_key = threshold.metric.value
        
        if metric_key not in metrics:
            return True  # Нет данных - пропускаем
            
        actual = metrics[metric_key]
        expected = threshold.value
        
        if threshold.operator == ThresholdOperator.LT:
            return actual < expected
        elif threshold.operator == ThresholdOperator.LE:
            return actual <= expected
        elif threshold.operator == ThresholdOperator.GT:
            return actual > expected
        elif threshold.operator == ThresholdOperator.GE:
            return actual >= expected
        elif threshold.operator == ThresholdOperator.EQ:
            return actual == expected
            
        return True


class ReportGenerator:
    """Генератор отчётов"""
    
    def generate(self, run: TestRun, collector: MetricsCollector,
                  config: TestConfig) -> TestReport:
        """Генерация отчёта"""
        metrics = collector.get_metrics()
        throughput = collector.get_throughput()
        
        duration = 0.0
        if run.started_at and run.finished_at:
            duration = (run.finished_at - run.started_at).total_seconds()
            
        return TestReport(
            report_id=f"report_{uuid.uuid4().hex[:8]}",
            run_id=run.run_id,
            summary={
                "test_name": config.name,
                "test_type": config.test_type.value,
                "status": run.status.value,
                "duration_seconds": duration,
                "total_requests": run.total_requests,
                "successful_requests": run.successful_requests,
                "failed_requests": run.failed_requests,
                "success_rate": run.successful_requests / max(run.total_requests, 1) * 100,
                "throughput_rps": throughput
            },
            metrics={
                "response_time": {
                    "avg": metrics.get(MetricType.RESPONSE_TIME.value, 0),
                    "min": metrics.get("min_response_time", 0),
                    "max": metrics.get("max_response_time", 0),
                    "std_dev": metrics.get("std_dev", 0)
                },
                "latency": {
                    "p50": metrics.get(MetricType.LATENCY_P50.value, 0),
                    "p90": metrics.get(MetricType.LATENCY_P90.value, 0),
                    "p95": metrics.get(MetricType.LATENCY_P95.value, 0),
                    "p99": metrics.get(MetricType.LATENCY_P99.value, 0)
                },
                "errors": {
                    "rate": metrics.get(MetricType.ERROR_RATE.value, 0),
                    "count": run.failed_requests
                }
            },
            thresholds=run.threshold_results
        )


class PerformanceTestingPlatform:
    """Платформа нагрузочного тестирования"""
    
    def __init__(self):
        self.scenarios: Dict[str, TestScenario] = {}
        self.configs: Dict[str, TestConfig] = {}
        self.runs: Dict[str, TestRun] = {}
        self.reports: Dict[str, TestReport] = {}
        
        self.threshold_validator = ThresholdValidator()
        self.report_generator = ReportGenerator()
        
    def create_scenario(self, name: str, steps: List[Dict[str, Any]],
                        **kwargs) -> TestScenario:
        """Создание сценария"""
        scenario = TestScenario(
            scenario_id=f"scen_{uuid.uuid4().hex[:8]}",
            name=name,
            steps=steps,
            **kwargs
        )
        
        self.scenarios[scenario.scenario_id] = scenario
        return scenario
        
    def create_config(self, name: str, test_type: TestType,
                       stages: List[TestStage], **kwargs) -> TestConfig:
        """Создание конфигурации теста"""
        config = TestConfig(
            config_id=f"cfg_{uuid.uuid4().hex[:8]}",
            name=name,
            test_type=test_type,
            stages=stages,
            **kwargs
        )
        
        self.configs[config.config_id] = config
        return config
        
    async def run_test(self, config_id: str) -> TestRun:
        """Запуск теста"""
        config = self.configs.get(config_id)
        if not config:
            raise ValueError(f"Config {config_id} not found")
            
        run = TestRun(
            run_id=f"run_{uuid.uuid4().hex[:8]}",
            config_id=config_id
        )
        
        self.runs[run.run_id] = run
        
        # Создаём компоненты
        simulator = HTTPSimulator(config.target_url)
        generator = LoadGenerator(simulator)
        collector = MetricsCollector()
        
        # Получаем сценарий
        scenario_id = config.scenarios[0] if config.scenarios else None
        scenario = self.scenarios.get(scenario_id) if scenario_id else TestScenario(
            scenario_id="default",
            name="Default",
            steps=[{"method": "GET", "path": "/"}]
        )
        
        run.status = TestStatus.RUNNING
        run.started_at = datetime.now()
        generator.running = True
        
        try:
            # Выполняем этапы
            for stage in config.stages:
                await generator.ramp_to(stage.target_vus, scenario, collector)
                
                # Ждём duration
                end_time = datetime.now() + timedelta(seconds=stage.duration_seconds)
                
                while datetime.now() < end_time:
                    await asyncio.sleep(1)
                    
                    # Проверяем пороги с abort_on_fail
                    metrics = collector.get_metrics()
                    
                    for threshold in config.thresholds:
                        if threshold.abort_on_fail:
                            if not self.threshold_validator.validate(threshold, metrics):
                                raise Exception(f"Threshold exceeded: {threshold.metric.value}")
                                
                    # Обновляем статистику
                    run.total_requests = len(collector.response_times)
                    run.failed_requests = len(collector.errors)
                    run.successful_requests = run.total_requests - run.failed_requests
                    
            run.status = TestStatus.COMPLETED
            
        except Exception as e:
            run.status = TestStatus.FAILED
            
        finally:
            generator.running = False
            run.finished_at = datetime.now()
            
            # Проверяем все пороги
            metrics = collector.get_metrics()
            for threshold in config.thresholds:
                key = threshold.metric.value
                passed = self.threshold_validator.validate(threshold, metrics)
                run.threshold_results[key] = passed
                
            # Генерируем отчёт
            report = self.report_generator.generate(run, collector, config)
            self.reports[report.report_id] = report
            
        return run
        
    def get_report(self, run_id: str) -> Optional[TestReport]:
        """Получение отчёта"""
        for report in self.reports.values():
            if report.run_id == run_id:
                return report
        return None
        
    def create_load_test(self, name: str, target_url: str,
                          vus: int, duration: int,
                          ramp_up: int = 30, **kwargs) -> TestConfig:
        """Создание load-теста"""
        stages = [
            TestStage(duration_seconds=ramp_up, target_vus=vus),  # Ramp up
            TestStage(duration_seconds=duration, target_vus=vus),  # Steady state
            TestStage(duration_seconds=10, target_vus=0)           # Ramp down
        ]
        
        return self.create_config(
            name=name,
            test_type=TestType.LOAD,
            stages=stages,
            target_url=target_url,
            **kwargs
        )
        
    def create_stress_test(self, name: str, target_url: str,
                            max_vus: int, stages_count: int = 5,
                            stage_duration: int = 60, **kwargs) -> TestConfig:
        """Создание stress-теста"""
        stages = []
        
        for i in range(1, stages_count + 1):
            vus = int(max_vus * i / stages_count)
            stages.append(TestStage(duration_seconds=stage_duration, target_vus=vus))
            
        stages.append(TestStage(duration_seconds=10, target_vus=0))
        
        return self.create_config(
            name=name,
            test_type=TestType.STRESS,
            stages=stages,
            target_url=target_url,
            **kwargs
        )
        
    def create_spike_test(self, name: str, target_url: str,
                           base_vus: int, spike_vus: int,
                           spike_duration: int = 30, **kwargs) -> TestConfig:
        """Создание spike-теста"""
        stages = [
            TestStage(duration_seconds=30, target_vus=base_vus),    # Baseline
            TestStage(duration_seconds=5, target_vus=spike_vus),    # Spike up
            TestStage(duration_seconds=spike_duration, target_vus=spike_vus),  # Spike
            TestStage(duration_seconds=5, target_vus=base_vus),     # Spike down
            TestStage(duration_seconds=30, target_vus=base_vus),    # Recovery
            TestStage(duration_seconds=10, target_vus=0)
        ]
        
        return self.create_config(
            name=name,
            test_type=TestType.SPIKE,
            stages=stages,
            target_url=target_url,
            **kwargs
        )
        
    def get_stats(self) -> Dict[str, Any]:
        """Статистика платформы"""
        completed_runs = [r for r in self.runs.values() if r.status == TestStatus.COMPLETED]
        
        return {
            "scenarios": len(self.scenarios),
            "configs": len(self.configs),
            "runs": len(self.runs),
            "completed_runs": len(completed_runs),
            "reports": len(self.reports)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 70: Performance Testing Platform")
    print("=" * 60)
    
    async def demo():
        platform = PerformanceTestingPlatform()
        print("✓ Performance Testing Platform created")
        
        # Создание сценариев
        print("\n📝 Creating test scenarios...")
        
        browse_scenario = platform.create_scenario(
            name="Browse Products",
            steps=[
                {"method": "GET", "path": "/"},
                {"method": "GET", "path": "/products"},
                {"method": "GET", "path": "/products/1"},
                {"method": "GET", "path": "/products/2"}
            ],
            think_time_min=1.0,
            think_time_max=3.0
        )
        print(f"  ✓ Scenario: {browse_scenario.name} ({len(browse_scenario.steps)} steps)")
        
        checkout_scenario = platform.create_scenario(
            name="Checkout Flow",
            steps=[
                {"method": "GET", "path": "/cart"},
                {"method": "POST", "path": "/cart/add", "body": {"product_id": 1}},
                {"method": "GET", "path": "/checkout"},
                {"method": "POST", "path": "/checkout/complete"}
            ],
            think_time_min=2.0,
            think_time_max=5.0
        )
        print(f"  ✓ Scenario: {checkout_scenario.name} ({len(checkout_scenario.steps)} steps)")
        
        # Создание тестов
        print("\n⚡ Creating test configurations...")
        
        # Load test
        load_test = platform.create_load_test(
            name="API Load Test",
            target_url="https://api.example.com",
            vus=100,
            duration=60,
            ramp_up=30,
            scenarios=[browse_scenario.scenario_id],
            thresholds=[
                Threshold(MetricType.LATENCY_P95, ThresholdOperator.LT, 500),
                Threshold(MetricType.ERROR_RATE, ThresholdOperator.LT, 5)
            ]
        )
        print(f"  ✓ Load Test: {load_test.name}")
        print(f"    - VUs: 100, Duration: 60s")
        print(f"    - Thresholds: p95 < 500ms, Error Rate < 5%")
        
        # Stress test
        stress_test = platform.create_stress_test(
            name="API Stress Test",
            target_url="https://api.example.com",
            max_vus=500,
            stages_count=5,
            stage_duration=30,
            thresholds=[
                Threshold(MetricType.ERROR_RATE, ThresholdOperator.LT, 10, abort_on_fail=True)
            ]
        )
        print(f"  ✓ Stress Test: {stress_test.name}")
        print(f"    - Max VUs: 500, Stages: 5")
        
        # Spike test
        spike_test = platform.create_spike_test(
            name="Traffic Spike Test",
            target_url="https://api.example.com",
            base_vus=50,
            spike_vus=200,
            spike_duration=30
        )
        print(f"  ✓ Spike Test: {spike_test.name}")
        print(f"    - Base: 50 VUs, Spike: 200 VUs")
        
        # Запуск теста (ускоренная демо-версия)
        print("\n🏃 Running quick smoke test...")
        
        quick_test = platform.create_config(
            name="Quick Smoke Test",
            test_type=TestType.SMOKE,
            stages=[
                TestStage(duration_seconds=2, target_vus=5),
                TestStage(duration_seconds=3, target_vus=10),
                TestStage(duration_seconds=1, target_vus=0)
            ],
            target_url="https://api.example.com",
            scenarios=[browse_scenario.scenario_id],
            thresholds=[
                Threshold(MetricType.LATENCY_P95, ThresholdOperator.LT, 500),
                Threshold(MetricType.ERROR_RATE, ThresholdOperator.LT, 10)
            ]
        )
        
        run = await platform.run_test(quick_test.config_id)
        
        print(f"\n📊 Test Results:")
        print(f"  Run ID: {run.run_id}")
        print(f"  Status: {run.status.value}")
        print(f"  Total Requests: {run.total_requests}")
        print(f"  Successful: {run.successful_requests}")
        print(f"  Failed: {run.failed_requests}")
        
        if run.total_requests > 0:
            success_rate = run.successful_requests / run.total_requests * 100
            print(f"  Success Rate: {success_rate:.2f}%")
            
        # Threshold results
        print(f"\n✅ Threshold Results:")
        for metric, passed in run.threshold_results.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"  {metric}: {status}")
            
        # Получение отчёта
        report = platform.get_report(run.run_id)
        
        if report:
            print(f"\n📄 Test Report:")
            print(f"  Report ID: {report.report_id}")
            
            print(f"\n  Summary:")
            for key, value in report.summary.items():
                if isinstance(value, float):
                    print(f"    {key}: {value:.2f}")
                else:
                    print(f"    {key}: {value}")
                    
            print(f"\n  Response Time:")
            rt = report.metrics.get("response_time", {})
            print(f"    Avg: {rt.get('avg', 0):.2f}ms")
            print(f"    Min: {rt.get('min', 0):.2f}ms")
            print(f"    Max: {rt.get('max', 0):.2f}ms")
            
            print(f"\n  Latency Percentiles:")
            lat = report.metrics.get("latency", {})
            print(f"    p50: {lat.get('p50', 0):.2f}ms")
            print(f"    p90: {lat.get('p90', 0):.2f}ms")
            print(f"    p95: {lat.get('p95', 0):.2f}ms")
            print(f"    p99: {lat.get('p99', 0):.2f}ms")
            
        # Статистика платформы
        print("\n📊 Platform Statistics:")
        stats = platform.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Performance Testing Platform initialized!")
    print("=" * 60)
