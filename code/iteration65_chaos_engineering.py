#!/usr/bin/env python3
"""
Server Init - Iteration 65: Chaos Engineering Platform
Хаос-инжиниринг и тестирование устойчивости

Функционал:
- Chaos Experiments - хаос-эксперименты
- Fault Injection - инъекция сбоев
- Steady State Hypothesis - гипотеза стабильного состояния
- Blast Radius - радиус поражения
- Game Days - игровые дни
- Resilience Scoring - оценка устойчивости
- Automated Rollback - автоматический откат
- Observability Integration - интеграция с наблюдаемостью
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
from collections import defaultdict
import uuid
import random


class ExperimentStatus(Enum):
    """Статус эксперимента"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class FaultType(Enum):
    """Тип сбоя"""
    CPU_STRESS = "cpu_stress"
    MEMORY_STRESS = "memory_stress"
    DISK_STRESS = "disk_stress"
    NETWORK_LATENCY = "network_latency"
    NETWORK_LOSS = "network_loss"
    NETWORK_PARTITION = "network_partition"
    PROCESS_KILL = "process_kill"
    SERVICE_UNAVAILABLE = "service_unavailable"
    DNS_FAILURE = "dns_failure"
    CLOCK_SKEW = "clock_skew"


class TargetType(Enum):
    """Тип цели"""
    HOST = "host"
    CONTAINER = "container"
    POD = "pod"
    SERVICE = "service"
    NAMESPACE = "namespace"
    ZONE = "zone"


class HypothesisResult(Enum):
    """Результат гипотезы"""
    PASSED = "passed"
    FAILED = "failed"
    UNKNOWN = "unknown"


class SeverityLevel(Enum):
    """Уровень серьёзности"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Target:
    """Цель хаос-эксперимента"""
    target_id: str
    name: str
    
    # Тип
    target_type: TargetType = TargetType.HOST
    
    # Идентификаторы
    identifiers: Dict[str, str] = field(default_factory=dict)  # labels, tags, etc.
    
    # Ограничения
    percentage: int = 100  # Процент целей
    count: Optional[int] = None  # Или конкретное число


@dataclass
class Fault:
    """Конфигурация сбоя"""
    fault_id: str
    name: str
    
    # Тип
    fault_type: FaultType = FaultType.CPU_STRESS
    
    # Параметры
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Длительность
    duration_seconds: int = 60
    
    # Ramping
    ramp_up_seconds: int = 0
    ramp_down_seconds: int = 0


@dataclass
class SteadyStateHypothesis:
    """Гипотеза стабильного состояния"""
    hypothesis_id: str
    name: str
    description: str = ""
    
    # Проверки
    probes: List[Dict[str, Any]] = field(default_factory=list)
    
    # Допустимые отклонения
    tolerance: Dict[str, Any] = field(default_factory=dict)
    
    # Результат
    result: HypothesisResult = HypothesisResult.UNKNOWN


@dataclass
class Experiment:
    """Хаос-эксперимент"""
    experiment_id: str
    name: str
    description: str = ""
    
    # Гипотеза
    hypothesis: Optional[SteadyStateHypothesis] = None
    
    # Цели
    targets: List[Target] = field(default_factory=list)
    
    # Сбои
    faults: List[Fault] = field(default_factory=list)
    
    # Статус
    status: ExperimentStatus = ExperimentStatus.DRAFT
    
    # Безопасность
    blast_radius: str = "single-host"  # single-host, zone, region, global
    severity: SeverityLevel = SeverityLevel.LOW
    
    # Rollback
    auto_rollback: bool = True
    rollback_on_hypothesis_failure: bool = True
    
    # Schedule
    schedule: Optional[str] = None  # cron expression
    
    # Метаданные
    tags: List[str] = field(default_factory=list)
    owner: str = ""
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class ExperimentRun:
    """Запуск эксперимента"""
    run_id: str
    experiment_id: str
    
    # Статус
    status: ExperimentStatus = ExperimentStatus.RUNNING
    
    # Результаты
    hypothesis_before: HypothesisResult = HypothesisResult.UNKNOWN
    hypothesis_after: HypothesisResult = HypothesisResult.UNKNOWN
    
    # Метрики во время эксперимента
    metrics: Dict[str, List[float]] = field(default_factory=dict)
    
    # События
    events: List[Dict[str, Any]] = field(default_factory=list)
    
    # Время
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    # Влияние
    affected_targets: List[str] = field(default_factory=list)
    
    # Примечания
    notes: str = ""


@dataclass
class GameDay:
    """Игровой день"""
    gameday_id: str
    name: str
    description: str = ""
    
    # Эксперименты
    experiments: List[str] = field(default_factory=list)  # experiment IDs
    
    # Участники
    participants: List[str] = field(default_factory=list)
    
    # Сценарий
    scenario: Dict[str, Any] = field(default_factory=dict)
    
    # Время
    scheduled_date: Optional[datetime] = None
    duration_hours: int = 4
    
    # Статус
    status: str = "planned"  # planned, in_progress, completed, cancelled


@dataclass
class ResilienceScore:
    """Оценка устойчивости"""
    service: str
    
    # Общий скор (0-100)
    overall_score: float = 0.0
    
    # Компоненты
    availability_score: float = 0.0
    recovery_score: float = 0.0
    degradation_score: float = 0.0
    
    # Статистика
    experiments_run: int = 0
    experiments_passed: int = 0
    
    # MTTR
    mean_time_to_recovery_seconds: float = 0.0
    
    # Последнее обновление
    updated_at: datetime = field(default_factory=datetime.now)


class FaultInjector:
    """Инжектор сбоев"""
    
    def __init__(self):
        self.active_faults: Dict[str, Dict[str, Any]] = {}
        
    async def inject(self, fault: Fault, targets: List[Target]) -> Dict[str, Any]:
        """Инъекция сбоя"""
        injection_id = f"inj_{uuid.uuid4().hex[:8]}"
        
        result = {
            "injection_id": injection_id,
            "fault_type": fault.fault_type.value,
            "targets_affected": [],
            "start_time": datetime.now(),
            "duration": fault.duration_seconds
        }
        
        # Симуляция ramp up
        if fault.ramp_up_seconds > 0:
            await asyncio.sleep(0.1)
            
        # Применяем к целям
        for target in targets:
            success = await self._apply_fault(fault, target)
            if success:
                result["targets_affected"].append(target.target_id)
                
        self.active_faults[injection_id] = {
            "fault": fault,
            "targets": targets,
            "result": result
        }
        
        return result
        
    async def _apply_fault(self, fault: Fault, target: Target) -> bool:
        """Применение сбоя к цели"""
        # Симуляция различных типов сбоев
        if fault.fault_type == FaultType.CPU_STRESS:
            print(f"  [FAULT] CPU stress on {target.name}: {fault.parameters.get('load', 80)}%")
            
        elif fault.fault_type == FaultType.MEMORY_STRESS:
            print(f"  [FAULT] Memory stress on {target.name}: {fault.parameters.get('size_mb', 512)}MB")
            
        elif fault.fault_type == FaultType.NETWORK_LATENCY:
            print(f"  [FAULT] Network latency on {target.name}: {fault.parameters.get('latency_ms', 100)}ms")
            
        elif fault.fault_type == FaultType.NETWORK_LOSS:
            print(f"  [FAULT] Network packet loss on {target.name}: {fault.parameters.get('loss_percent', 10)}%")
            
        elif fault.fault_type == FaultType.PROCESS_KILL:
            print(f"  [FAULT] Process kill on {target.name}: {fault.parameters.get('process', 'app')}")
            
        elif fault.fault_type == FaultType.SERVICE_UNAVAILABLE:
            print(f"  [FAULT] Service unavailable on {target.name}")
            
        await asyncio.sleep(0.05)  # Симуляция
        return True
        
    async def rollback(self, injection_id: str) -> bool:
        """Откат сбоя"""
        if injection_id not in self.active_faults:
            return False
            
        fault_data = self.active_faults[injection_id]
        
        for target in fault_data["targets"]:
            await self._remove_fault(fault_data["fault"], target)
            
        del self.active_faults[injection_id]
        return True
        
    async def _remove_fault(self, fault: Fault, target: Target):
        """Удаление сбоя"""
        print(f"  [ROLLBACK] Removing {fault.fault_type.value} from {target.name}")
        await asyncio.sleep(0.01)


class HypothesisValidator:
    """Валидатор гипотез"""
    
    def __init__(self):
        self.probe_handlers: Dict[str, Callable] = {}
        self._register_default_probes()
        
    def _register_default_probes(self):
        """Регистрация стандартных проверок"""
        self.probe_handlers["http_health"] = self._probe_http_health
        self.probe_handlers["metric_threshold"] = self._probe_metric_threshold
        self.probe_handlers["error_rate"] = self._probe_error_rate
        self.probe_handlers["latency_p99"] = self._probe_latency
        
    async def validate(self, hypothesis: SteadyStateHypothesis) -> HypothesisResult:
        """Валидация гипотезы"""
        results = []
        
        for probe in hypothesis.probes:
            probe_type = probe.get("type", "")
            handler = self.probe_handlers.get(probe_type)
            
            if not handler:
                results.append(False)
                continue
                
            result = await handler(probe)
            results.append(result)
            
        # Все проверки должны пройти
        if all(results):
            hypothesis.result = HypothesisResult.PASSED
        elif not results:
            hypothesis.result = HypothesisResult.UNKNOWN
        else:
            hypothesis.result = HypothesisResult.FAILED
            
        return hypothesis.result
        
    async def _probe_http_health(self, probe: Dict[str, Any]) -> bool:
        """Проверка HTTP health"""
        # Симуляция
        endpoint = probe.get("endpoint", "/health")
        expected_status = probe.get("expected_status", 200)
        
        # 90% успех в симуляции
        return random.random() < 0.9
        
    async def _probe_metric_threshold(self, probe: Dict[str, Any]) -> bool:
        """Проверка метрики"""
        metric = probe.get("metric", "")
        threshold = probe.get("threshold", 0)
        operator = probe.get("operator", "lt")  # lt, gt, eq
        
        # Симуляция значения метрики
        value = random.uniform(0, 100)
        
        if operator == "lt":
            return value < threshold
        elif operator == "gt":
            return value > threshold
        else:
            return abs(value - threshold) < 0.1
            
    async def _probe_error_rate(self, probe: Dict[str, Any]) -> bool:
        """Проверка частоты ошибок"""
        max_rate = probe.get("max_rate", 0.01)
        current_rate = random.uniform(0, 0.05)
        return current_rate <= max_rate
        
    async def _probe_latency(self, probe: Dict[str, Any]) -> bool:
        """Проверка задержки"""
        max_p99 = probe.get("max_p99_ms", 500)
        current_p99 = random.uniform(50, 600)
        return current_p99 <= max_p99


class ExperimentOrchestrator:
    """Оркестратор экспериментов"""
    
    def __init__(self):
        self.fault_injector = FaultInjector()
        self.hypothesis_validator = HypothesisValidator()
        self.runs: Dict[str, ExperimentRun] = {}
        
    async def execute(self, experiment: Experiment) -> ExperimentRun:
        """Выполнение эксперимента"""
        run = ExperimentRun(
            run_id=f"run_{uuid.uuid4().hex[:8]}",
            experiment_id=experiment.experiment_id,
            status=ExperimentStatus.RUNNING
        )
        
        self.runs[run.run_id] = run
        experiment.status = ExperimentStatus.RUNNING
        experiment.started_at = datetime.now()
        
        self._log_event(run, "experiment_started", {"experiment": experiment.name})
        
        try:
            # 1. Проверка гипотезы ДО эксперимента
            if experiment.hypothesis:
                print("  📊 Validating hypothesis BEFORE experiment...")
                run.hypothesis_before = await self.hypothesis_validator.validate(experiment.hypothesis)
                self._log_event(run, "hypothesis_before", {"result": run.hypothesis_before.value})
                
                if run.hypothesis_before == HypothesisResult.FAILED:
                    print("    ⚠️ Hypothesis failed BEFORE experiment - system already unstable")
                    if experiment.rollback_on_hypothesis_failure:
                        run.status = ExperimentStatus.ABORTED
                        return run
                        
            # 2. Инъекция сбоев
            print("  💥 Injecting faults...")
            injections = []
            
            for fault in experiment.faults:
                injection = await self.fault_injector.inject(fault, experiment.targets)
                injections.append(injection)
                run.affected_targets.extend(injection["targets_affected"])
                self._log_event(run, "fault_injected", {
                    "fault": fault.name,
                    "targets": injection["targets_affected"]
                })
                
            # 3. Ожидание (симуляция длительности эксперимента)
            max_duration = max((f.duration_seconds for f in experiment.faults), default=60)
            print(f"  ⏱️ Running experiment for {max_duration}s (simulated)...")
            await asyncio.sleep(0.5)  # Ускоренная симуляция
            
            # 4. Сбор метрик во время эксперимента
            run.metrics["error_rate"] = [random.uniform(0, 0.1) for _ in range(10)]
            run.metrics["latency_p99"] = [random.uniform(100, 800) for _ in range(10)]
            run.metrics["availability"] = [random.uniform(0.95, 1.0) for _ in range(10)]
            
            # 5. Проверка гипотезы ПОСЛЕ эксперимента
            if experiment.hypothesis:
                print("  📊 Validating hypothesis AFTER experiment...")
                run.hypothesis_after = await self.hypothesis_validator.validate(experiment.hypothesis)
                self._log_event(run, "hypothesis_after", {"result": run.hypothesis_after.value})
                
            # 6. Откат сбоев
            print("  🔄 Rolling back faults...")
            for injection in injections:
                await self.fault_injector.rollback(injection["injection_id"])
                
            # 7. Определение статуса
            if run.hypothesis_after == HypothesisResult.PASSED:
                run.status = ExperimentStatus.COMPLETED
                print("  ✅ Experiment PASSED - system is resilient!")
            elif run.hypothesis_after == HypothesisResult.FAILED:
                run.status = ExperimentStatus.FAILED
                print("  ❌ Experiment FAILED - resilience issue detected!")
            else:
                run.status = ExperimentStatus.COMPLETED
                
        except Exception as e:
            run.status = ExperimentStatus.FAILED
            self._log_event(run, "error", {"error": str(e)})
            
            # Автоматический откат
            if experiment.auto_rollback:
                for injection_id in self.fault_injector.active_faults:
                    await self.fault_injector.rollback(injection_id)
                    
        finally:
            run.completed_at = datetime.now()
            experiment.completed_at = datetime.now()
            experiment.status = run.status
            
        return run
        
    def _log_event(self, run: ExperimentRun, event_type: str, data: Dict[str, Any]):
        """Логирование события"""
        run.events.append({
            "type": event_type,
            "timestamp": datetime.now(),
            "data": data
        })


class ResilienceAnalyzer:
    """Анализатор устойчивости"""
    
    def __init__(self):
        self.scores: Dict[str, ResilienceScore] = {}
        
    def analyze_runs(self, service: str, runs: List[ExperimentRun]) -> ResilienceScore:
        """Анализ запусков для расчёта скора"""
        if not runs:
            return ResilienceScore(service=service)
            
        passed = len([r for r in runs if r.status == ExperimentStatus.COMPLETED and 
                      r.hypothesis_after == HypothesisResult.PASSED])
        total = len(runs)
        
        # Recovery time (из метрик)
        recovery_times = []
        for run in runs:
            if run.completed_at and run.started_at:
                recovery_times.append((run.completed_at - run.started_at).total_seconds())
                
        mttr = sum(recovery_times) / len(recovery_times) if recovery_times else 0
        
        # Расчёт скоров
        pass_rate = passed / total if total > 0 else 0
        availability_score = pass_rate * 100
        recovery_score = max(0, 100 - (mttr / 60) * 10)  # Штраф за долгое восстановление
        
        # Degradation score (на основе метрик во время экспериментов)
        degradation_scores = []
        for run in runs:
            if "availability" in run.metrics:
                avg_availability = sum(run.metrics["availability"]) / len(run.metrics["availability"])
                degradation_scores.append(avg_availability * 100)
                
        degradation_score = sum(degradation_scores) / len(degradation_scores) if degradation_scores else 50
        
        # Общий скор
        overall = (availability_score * 0.4 + recovery_score * 0.3 + degradation_score * 0.3)
        
        score = ResilienceScore(
            service=service,
            overall_score=round(overall, 1),
            availability_score=round(availability_score, 1),
            recovery_score=round(recovery_score, 1),
            degradation_score=round(degradation_score, 1),
            experiments_run=total,
            experiments_passed=passed,
            mean_time_to_recovery_seconds=round(mttr, 1)
        )
        
        self.scores[service] = score
        return score


class ChaosEngineeringPlatform:
    """Платформа хаос-инжиниринга"""
    
    def __init__(self):
        self.experiments: Dict[str, Experiment] = {}
        self.orchestrator = ExperimentOrchestrator()
        self.analyzer = ResilienceAnalyzer()
        self.game_days: Dict[str, GameDay] = {}
        
    def create_experiment(self, name: str, description: str = "",
                           **kwargs) -> Experiment:
        """Создание эксперимента"""
        experiment = Experiment(
            experiment_id=f"exp_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            **kwargs
        )
        
        self.experiments[experiment.experiment_id] = experiment
        return experiment
        
    def add_target(self, experiment_id: str, name: str,
                    target_type: TargetType, **kwargs) -> Target:
        """Добавление цели"""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            raise ValueError("Experiment not found")
            
        target = Target(
            target_id=f"target_{uuid.uuid4().hex[:8]}",
            name=name,
            target_type=target_type,
            **kwargs
        )
        
        experiment.targets.append(target)
        return target
        
    def add_fault(self, experiment_id: str, name: str,
                   fault_type: FaultType, **kwargs) -> Fault:
        """Добавление сбоя"""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            raise ValueError("Experiment not found")
            
        fault = Fault(
            fault_id=f"fault_{uuid.uuid4().hex[:8]}",
            name=name,
            fault_type=fault_type,
            **kwargs
        )
        
        experiment.faults.append(fault)
        return fault
        
    def set_hypothesis(self, experiment_id: str, name: str,
                        probes: List[Dict[str, Any]],
                        **kwargs) -> SteadyStateHypothesis:
        """Установка гипотезы"""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            raise ValueError("Experiment not found")
            
        hypothesis = SteadyStateHypothesis(
            hypothesis_id=f"hyp_{uuid.uuid4().hex[:8]}",
            name=name,
            probes=probes,
            **kwargs
        )
        
        experiment.hypothesis = hypothesis
        return hypothesis
        
    async def run_experiment(self, experiment_id: str) -> ExperimentRun:
        """Запуск эксперимента"""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            raise ValueError("Experiment not found")
            
        return await self.orchestrator.execute(experiment)
        
    def create_game_day(self, name: str, experiments: List[str],
                         **kwargs) -> GameDay:
        """Создание игрового дня"""
        game_day = GameDay(
            gameday_id=f"gd_{uuid.uuid4().hex[:8]}",
            name=name,
            experiments=experiments,
            **kwargs
        )
        
        self.game_days[game_day.gameday_id] = game_day
        return game_day
        
    async def run_game_day(self, gameday_id: str) -> Dict[str, Any]:
        """Запуск игрового дня"""
        game_day = self.game_days.get(gameday_id)
        if not game_day:
            raise ValueError("Game day not found")
            
        game_day.status = "in_progress"
        results = []
        
        for exp_id in game_day.experiments:
            if exp_id in self.experiments:
                run = await self.run_experiment(exp_id)
                results.append({
                    "experiment_id": exp_id,
                    "run_id": run.run_id,
                    "status": run.status.value,
                    "hypothesis_result": run.hypothesis_after.value
                })
                
        game_day.status = "completed"
        
        return {
            "gameday_id": gameday_id,
            "name": game_day.name,
            "experiments_run": len(results),
            "results": results
        }
        
    def get_resilience_report(self, service: str) -> Dict[str, Any]:
        """Отчёт об устойчивости"""
        # Собираем все запуски для сервиса
        runs = []
        for exp in self.experiments.values():
            if any(t.name == service for t in exp.targets):
                runs.extend(self.orchestrator.runs.values())
                
        score = self.analyzer.analyze_runs(service, runs)
        
        return {
            "service": service,
            "overall_score": score.overall_score,
            "scores": {
                "availability": score.availability_score,
                "recovery": score.recovery_score,
                "degradation": score.degradation_score
            },
            "statistics": {
                "experiments_run": score.experiments_run,
                "experiments_passed": score.experiments_passed,
                "pass_rate": round(score.experiments_passed / max(score.experiments_run, 1) * 100, 1),
                "mttr_seconds": score.mean_time_to_recovery_seconds
            },
            "grade": self._calculate_grade(score.overall_score)
        }
        
    def _calculate_grade(self, score: float) -> str:
        """Расчёт оценки"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
            
    def get_experiment_library(self) -> List[Dict[str, Any]]:
        """Библиотека экспериментов"""
        return [
            {
                "name": "CPU Stress Test",
                "fault_type": FaultType.CPU_STRESS.value,
                "description": "Stress CPU to test system behavior under high load",
                "parameters": {"load": 90, "duration": 300}
            },
            {
                "name": "Memory Pressure",
                "fault_type": FaultType.MEMORY_STRESS.value,
                "description": "Consume memory to test OOM handling",
                "parameters": {"size_mb": 1024, "duration": 180}
            },
            {
                "name": "Network Latency Injection",
                "fault_type": FaultType.NETWORK_LATENCY.value,
                "description": "Add network latency to test timeout handling",
                "parameters": {"latency_ms": 500, "jitter_ms": 100}
            },
            {
                "name": "Network Partition",
                "fault_type": FaultType.NETWORK_PARTITION.value,
                "description": "Isolate services to test split-brain scenarios",
                "parameters": {"partition_mode": "complete"}
            },
            {
                "name": "Process Kill",
                "fault_type": FaultType.PROCESS_KILL.value,
                "description": "Kill processes to test recovery mechanisms",
                "parameters": {"signal": "SIGKILL", "restart_delay": 30}
            },
            {
                "name": "DNS Failure",
                "fault_type": FaultType.DNS_FAILURE.value,
                "description": "Inject DNS failures to test service discovery",
                "parameters": {"failure_rate": 0.5}
            }
        ]


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 65: Chaos Engineering Platform")
    print("=" * 60)
    
    async def demo():
        platform = ChaosEngineeringPlatform()
        print("✓ Chaos Engineering Platform created")
        
        # Библиотека экспериментов
        print("\n📚 Experiment Library:")
        for exp_template in platform.get_experiment_library()[:3]:
            print(f"  • {exp_template['name']}: {exp_template['description']}")
            
        # Создание эксперимента
        print("\n🧪 Creating experiment: Network Latency Test")
        
        experiment = platform.create_experiment(
            name="API Gateway Latency Resilience",
            description="Test API gateway behavior under network latency conditions",
            blast_radius="single-host",
            severity=SeverityLevel.MEDIUM,
            auto_rollback=True
        )
        print(f"  ✓ Experiment: {experiment.name} ({experiment.experiment_id})")
        
        # Добавление цели
        target = platform.add_target(
            experiment.experiment_id,
            name="api-gateway-1",
            target_type=TargetType.SERVICE,
            identifiers={"app": "api-gateway", "env": "staging"},
            percentage=100
        )
        print(f"  ✓ Target: {target.name} ({target.target_type.value})")
        
        # Добавление сбоя
        fault = platform.add_fault(
            experiment.experiment_id,
            name="inject-latency",
            fault_type=FaultType.NETWORK_LATENCY,
            parameters={"latency_ms": 500, "jitter_ms": 100},
            duration_seconds=120,
            ramp_up_seconds=10
        )
        print(f"  ✓ Fault: {fault.name} ({fault.fault_type.value})")
        
        # Установка гипотезы
        hypothesis = platform.set_hypothesis(
            experiment.experiment_id,
            name="API remains responsive",
            description="The API should maintain acceptable response times and error rates",
            probes=[
                {"type": "http_health", "endpoint": "/health", "expected_status": 200},
                {"type": "error_rate", "max_rate": 0.05},
                {"type": "latency_p99", "max_p99_ms": 1000}
            ]
        )
        print(f"  ✓ Hypothesis: {hypothesis.name}")
        
        # Запуск эксперимента
        print("\n🚀 Running experiment...")
        run = await platform.run_experiment(experiment.experiment_id)
        
        print(f"\n📊 Experiment Results:")
        print(f"  Run ID: {run.run_id}")
        print(f"  Status: {run.status.value}")
        print(f"  Hypothesis Before: {run.hypothesis_before.value}")
        print(f"  Hypothesis After: {run.hypothesis_after.value}")
        print(f"  Affected Targets: {run.affected_targets}")
        
        # Метрики
        print(f"\n  Metrics during experiment:")
        for metric, values in run.metrics.items():
            avg = sum(values) / len(values)
            print(f"    {metric}: avg={avg:.3f}")
            
        # События
        print(f"\n  Events ({len(run.events)}):")
        for event in run.events[:5]:
            print(f"    [{event['type']}] {event['data']}")
            
        # Создание второго эксперимента
        print("\n\n🧪 Creating experiment: Process Kill Test")
        
        exp2 = platform.create_experiment(
            name="Service Recovery Test",
            description="Test service recovery after process termination",
            severity=SeverityLevel.HIGH
        )
        
        platform.add_target(
            exp2.experiment_id,
            name="payment-service",
            target_type=TargetType.CONTAINER
        )
        
        platform.add_fault(
            exp2.experiment_id,
            name="kill-process",
            fault_type=FaultType.PROCESS_KILL,
            parameters={"process": "payment-worker", "signal": "SIGKILL"},
            duration_seconds=60
        )
        
        platform.set_hypothesis(
            exp2.experiment_id,
            name="Service recovers automatically",
            probes=[
                {"type": "http_health", "endpoint": "/health"},
                {"type": "metric_threshold", "metric": "active_connections", "threshold": 1, "operator": "gt"}
            ]
        )
        
        run2 = await platform.run_experiment(exp2.experiment_id)
        print(f"  Run ID: {run2.run_id}, Status: {run2.status.value}")
        
        # Game Day
        print("\n\n🎮 Creating Game Day...")
        
        game_day = platform.create_game_day(
            name="Q4 Resilience Testing",
            experiments=[experiment.experiment_id, exp2.experiment_id],
            participants=["team-platform", "team-sre", "team-backend"],
            duration_hours=4,
            scenario={
                "objective": "Test system resilience under various failure conditions",
                "success_criteria": "All critical services maintain 99.9% availability"
            }
        )
        print(f"  ✓ Game Day: {game_day.name}")
        print(f"  Experiments: {len(game_day.experiments)}")
        print(f"  Participants: {', '.join(game_day.participants)}")
        
        # Запуск Game Day
        print("\n  Running Game Day...")
        gd_results = await platform.run_game_day(game_day.gameday_id)
        print(f"  ✓ Completed! Experiments run: {gd_results['experiments_run']}")
        
        for result in gd_results["results"]:
            print(f"    - {result['experiment_id']}: {result['status']} ({result['hypothesis_result']})")
            
        # Отчёт об устойчивости
        print("\n\n📈 Resilience Report:")
        report = platform.get_resilience_report("api-gateway-1")
        print(f"  Service: {report['service']}")
        print(f"  Overall Score: {report['overall_score']} (Grade: {report['grade']})")
        print(f"  Scores:")
        print(f"    Availability: {report['scores']['availability']}")
        print(f"    Recovery: {report['scores']['recovery']}")
        print(f"    Degradation: {report['scores']['degradation']}")
        print(f"  Statistics:")
        print(f"    Experiments Run: {report['statistics']['experiments_run']}")
        print(f"    Pass Rate: {report['statistics']['pass_rate']}%")
        print(f"    MTTR: {report['statistics']['mttr_seconds']}s")
        
        # Общая статистика
        print("\n📊 Platform Statistics:")
        print(f"  Total Experiments: {len(platform.experiments)}")
        print(f"  Total Runs: {len(platform.orchestrator.runs)}")
        print(f"  Game Days: {len(platform.game_days)}")
        print(f"  Active Faults: {len(platform.orchestrator.fault_injector.active_faults)}")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Chaos Engineering Platform initialized!")
    print("=" * 60)
