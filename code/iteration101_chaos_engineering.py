#!/usr/bin/env python3
"""
Server Init - Iteration 101: Chaos Engineering Platform
Платформа хаос-инжиниринга

Функционал:
- Fault Injection - внедрение сбоев
- Chaos Experiments - эксперименты хаоса
- Steady State Hypothesis - гипотезы стабильного состояния
- Blast Radius Control - контроль радиуса поражения
- Rollback Mechanisms - механизмы отката
- Game Days - игровые дни
- Resilience Testing - тестирование устойчивости
- Incident Simulation - симуляция инцидентов
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Union, Tuple
from enum import Enum
from collections import defaultdict
import uuid
import random


class FaultType(Enum):
    """Тип сбоя"""
    LATENCY = "latency"
    ERROR = "error"
    TIMEOUT = "timeout"
    CPU_STRESS = "cpu_stress"
    MEMORY_STRESS = "memory_stress"
    DISK_STRESS = "disk_stress"
    NETWORK_PARTITION = "network_partition"
    PACKET_LOSS = "packet_loss"
    DNS_FAILURE = "dns_failure"
    PROCESS_KILL = "process_kill"
    CONTAINER_KILL = "container_kill"
    NODE_DRAIN = "node_drain"


class ExperimentStatus(Enum):
    """Статус эксперимента"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class TargetType(Enum):
    """Тип цели"""
    SERVICE = "service"
    POD = "pod"
    CONTAINER = "container"
    NODE = "node"
    NETWORK = "network"
    DATABASE = "database"


class HypothesisResult(Enum):
    """Результат гипотезы"""
    PASSED = "passed"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass
class Target:
    """Цель эксперимента"""
    target_id: str
    target_type: TargetType = TargetType.SERVICE
    
    # Идентификация
    name: str = ""
    namespace: str = "default"
    
    # Селекторы
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Ограничения
    percentage: int = 100  # Процент целей
    count: int = 0  # Конкретное количество (0 = все)


@dataclass
class Fault:
    """Описание сбоя"""
    fault_id: str
    fault_type: FaultType = FaultType.LATENCY
    
    # Параметры по типу
    # Latency
    latency_ms: int = 0
    jitter_ms: int = 0
    
    # Error
    error_code: int = 500
    error_message: str = ""
    error_rate: float = 1.0  # 0-1
    
    # Stress
    stress_level: int = 80  # percent
    workers: int = 1
    
    # Network
    packet_loss_percent: float = 0.0
    bandwidth_limit: str = ""  # e.g., "100kbps"
    
    # Duration
    duration_seconds: int = 60


@dataclass
class SteadyStateHypothesis:
    """Гипотеза стабильного состояния"""
    hypothesis_id: str
    description: str = ""
    
    # Проверки
    probes: List[Dict[str, Any]] = field(default_factory=list)
    
    # Пороги
    tolerance: Dict[str, Any] = field(default_factory=dict)
    
    # Результат
    result: HypothesisResult = HypothesisResult.UNKNOWN
    evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChaosExperiment:
    """Эксперимент хаоса"""
    experiment_id: str
    name: str = ""
    description: str = ""
    
    # Targets
    targets: List[Target] = field(default_factory=list)
    
    # Faults
    faults: List[Fault] = field(default_factory=list)
    
    # Hypothesis
    steady_state_hypothesis: Optional[SteadyStateHypothesis] = None
    
    # Safety
    abort_conditions: List[Dict[str, Any]] = field(default_factory=list)
    rollback_strategy: str = "immediate"
    
    # Blast radius
    max_affected_percentage: int = 50
    
    # Schedule
    scheduled_at: Optional[datetime] = None
    
    # Status
    status: ExperimentStatus = ExperimentStatus.DRAFT
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results
    results: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    created_by: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class GameDay:
    """Игровой день"""
    gameday_id: str
    name: str = ""
    description: str = ""
    
    # Эксперименты
    experiments: List[str] = field(default_factory=list)
    
    # Участники
    participants: List[str] = field(default_factory=list)
    
    # Сценарий
    scenario: str = ""
    
    # Расписание
    scheduled_date: Optional[datetime] = None
    duration_hours: int = 4
    
    # Статус
    status: str = "planned"  # planned, in_progress, completed
    
    # Результаты
    findings: List[str] = field(default_factory=list)
    action_items: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ExperimentRun:
    """Запуск эксперимента"""
    run_id: str
    experiment_id: str = ""
    
    # Статус
    status: ExperimentStatus = ExperimentStatus.RUNNING
    
    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    # Progress
    current_phase: str = "init"
    progress_percent: int = 0
    
    # Affected targets
    affected_targets: List[str] = field(default_factory=list)
    
    # Events
    events: List[Dict[str, Any]] = field(default_factory=list)
    
    # Results
    hypothesis_result: HypothesisResult = HypothesisResult.UNKNOWN
    metrics_before: Dict[str, float] = field(default_factory=dict)
    metrics_after: Dict[str, float] = field(default_factory=dict)


class FaultInjector:
    """Инжектор сбоев"""
    
    async def inject(self, target: Target, fault: Fault) -> Dict[str, Any]:
        """Внедрение сбоя"""
        result = {
            "target": target.name,
            "fault_type": fault.fault_type.value,
            "injected_at": datetime.now().isoformat(),
            "success": True
        }
        
        # Simulate injection
        await asyncio.sleep(0.1)
        
        if fault.fault_type == FaultType.LATENCY:
            result["details"] = f"Added {fault.latency_ms}ms latency"
        elif fault.fault_type == FaultType.ERROR:
            result["details"] = f"Injecting {fault.error_code} errors at {fault.error_rate*100}% rate"
        elif fault.fault_type == FaultType.CPU_STRESS:
            result["details"] = f"CPU stress at {fault.stress_level}%"
        elif fault.fault_type == FaultType.MEMORY_STRESS:
            result["details"] = f"Memory stress at {fault.stress_level}%"
        elif fault.fault_type == FaultType.NETWORK_PARTITION:
            result["details"] = "Network partition created"
        elif fault.fault_type == FaultType.PACKET_LOSS:
            result["details"] = f"Packet loss at {fault.packet_loss_percent}%"
        elif fault.fault_type == FaultType.PROCESS_KILL:
            result["details"] = f"Process killed on {target.name}"
        elif fault.fault_type == FaultType.CONTAINER_KILL:
            result["details"] = f"Container killed: {target.name}"
        else:
            result["details"] = f"Fault {fault.fault_type.value} injected"
            
        return result
        
    async def rollback(self, target: Target, fault: Fault) -> Dict[str, Any]:
        """Откат сбоя"""
        await asyncio.sleep(0.05)
        
        return {
            "target": target.name,
            "fault_type": fault.fault_type.value,
            "rolled_back_at": datetime.now().isoformat(),
            "success": True
        }


class HypothesisValidator:
    """Валидатор гипотез"""
    
    async def validate(self, hypothesis: SteadyStateHypothesis) -> HypothesisResult:
        """Валидация гипотезы"""
        if not hypothesis.probes:
            return HypothesisResult.UNKNOWN
            
        all_passed = True
        evidence = {}
        
        for probe in hypothesis.probes:
            probe_name = probe.get("name", "unnamed")
            probe_type = probe.get("type", "http")
            
            # Simulate probe execution
            await asyncio.sleep(0.02)
            
            # Random result for demo
            passed = random.random() > 0.2
            evidence[probe_name] = {
                "type": probe_type,
                "passed": passed,
                "value": random.uniform(0, 100)
            }
            
            if not passed:
                all_passed = False
                
        hypothesis.evidence = evidence
        hypothesis.result = HypothesisResult.PASSED if all_passed else HypothesisResult.FAILED
        
        return hypothesis.result


class SafetyController:
    """Контроллер безопасности"""
    
    def __init__(self):
        self.abort_triggered = False
        self.abort_reason = ""
        
    async def check_abort_conditions(self, run: ExperimentRun,
                                       conditions: List[Dict[str, Any]]) -> bool:
        """Проверка условий прерывания"""
        for condition in conditions:
            condition_type = condition.get("type")
            threshold = condition.get("threshold")
            
            # Simulate metric check
            current_value = random.uniform(0, 100)
            
            if condition_type == "error_rate" and current_value > threshold:
                self.abort_triggered = True
                self.abort_reason = f"Error rate {current_value:.1f}% exceeded threshold {threshold}%"
                return True
                
            if condition_type == "latency_p99" and current_value > threshold:
                self.abort_triggered = True
                self.abort_reason = f"P99 latency {current_value:.1f}ms exceeded threshold {threshold}ms"
                return True
                
        return False
        
    def reset(self):
        """Сброс состояния"""
        self.abort_triggered = False
        self.abort_reason = ""


class MetricsCollector:
    """Сборщик метрик"""
    
    async def collect_baseline(self, targets: List[Target]) -> Dict[str, float]:
        """Сбор базовых метрик"""
        metrics = {}
        
        for target in targets:
            await asyncio.sleep(0.01)
            metrics[f"{target.name}_latency_p50"] = random.uniform(10, 50)
            metrics[f"{target.name}_latency_p99"] = random.uniform(50, 200)
            metrics[f"{target.name}_error_rate"] = random.uniform(0, 2)
            metrics[f"{target.name}_throughput"] = random.uniform(100, 1000)
            
        return metrics
        
    async def collect_during_experiment(self, targets: List[Target]) -> Dict[str, float]:
        """Сбор метрик во время эксперимента"""
        metrics = {}
        
        for target in targets:
            await asyncio.sleep(0.01)
            # Simulated degradation during chaos
            metrics[f"{target.name}_latency_p50"] = random.uniform(50, 200)
            metrics[f"{target.name}_latency_p99"] = random.uniform(200, 800)
            metrics[f"{target.name}_error_rate"] = random.uniform(1, 10)
            metrics[f"{target.name}_throughput"] = random.uniform(50, 500)
            
        return metrics


class ChaosEngineeringPlatform:
    """Платформа хаос-инжиниринга"""
    
    def __init__(self):
        self.experiments: Dict[str, ChaosExperiment] = {}
        self.runs: Dict[str, ExperimentRun] = {}
        self.gamedays: Dict[str, GameDay] = {}
        
        self.fault_injector = FaultInjector()
        self.hypothesis_validator = HypothesisValidator()
        self.safety_controller = SafetyController()
        self.metrics_collector = MetricsCollector()
        
        # Statistics
        self.stats = {
            "total_experiments": 0,
            "successful_experiments": 0,
            "failed_experiments": 0,
            "aborted_experiments": 0,
            "total_faults_injected": 0,
            "total_gamedays": 0
        }
        
    def create_experiment(self, name: str, description: str = "",
                           **kwargs) -> ChaosExperiment:
        """Создание эксперимента"""
        experiment = ChaosExperiment(
            experiment_id=f"exp_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            **kwargs
        )
        self.experiments[experiment.experiment_id] = experiment
        self.stats["total_experiments"] += 1
        return experiment
        
    def add_target(self, experiment_id: str, target_type: TargetType,
                    name: str, **kwargs) -> Target:
        """Добавление цели"""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            raise ValueError(f"Experiment {experiment_id} not found")
            
        target = Target(
            target_id=f"target_{uuid.uuid4().hex[:8]}",
            target_type=target_type,
            name=name,
            **kwargs
        )
        experiment.targets.append(target)
        return target
        
    def add_fault(self, experiment_id: str, fault_type: FaultType,
                   **kwargs) -> Fault:
        """Добавление сбоя"""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            raise ValueError(f"Experiment {experiment_id} not found")
            
        fault = Fault(
            fault_id=f"fault_{uuid.uuid4().hex[:8]}",
            fault_type=fault_type,
            **kwargs
        )
        experiment.faults.append(fault)
        return fault
        
    def set_hypothesis(self, experiment_id: str, description: str,
                        probes: List[Dict[str, Any]]) -> SteadyStateHypothesis:
        """Установка гипотезы"""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            raise ValueError(f"Experiment {experiment_id} not found")
            
        hypothesis = SteadyStateHypothesis(
            hypothesis_id=f"hyp_{uuid.uuid4().hex[:8]}",
            description=description,
            probes=probes
        )
        experiment.steady_state_hypothesis = hypothesis
        return hypothesis
        
    async def run_experiment(self, experiment_id: str) -> ExperimentRun:
        """Запуск эксперимента"""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            raise ValueError(f"Experiment {experiment_id} not found")
            
        # Create run
        run = ExperimentRun(
            run_id=f"run_{uuid.uuid4().hex[:8]}",
            experiment_id=experiment_id
        )
        self.runs[run.run_id] = run
        
        experiment.status = ExperimentStatus.RUNNING
        self.safety_controller.reset()
        
        try:
            # Phase 1: Validate steady state before
            run.current_phase = "steady_state_before"
            run.progress_percent = 10
            
            if experiment.steady_state_hypothesis:
                run.events.append({
                    "phase": "steady_state_before",
                    "timestamp": datetime.now().isoformat(),
                    "message": "Validating steady state hypothesis (before)"
                })
                
                result = await self.hypothesis_validator.validate(
                    experiment.steady_state_hypothesis
                )
                
                if result == HypothesisResult.FAILED:
                    run.status = ExperimentStatus.FAILED
                    run.events.append({
                        "phase": "steady_state_before",
                        "timestamp": datetime.now().isoformat(),
                        "message": "Steady state hypothesis failed before experiment",
                        "result": "FAILED"
                    })
                    self.stats["failed_experiments"] += 1
                    return run
                    
            # Phase 2: Collect baseline metrics
            run.current_phase = "baseline"
            run.progress_percent = 20
            
            run.metrics_before = await self.metrics_collector.collect_baseline(
                experiment.targets
            )
            
            run.events.append({
                "phase": "baseline",
                "timestamp": datetime.now().isoformat(),
                "message": "Baseline metrics collected",
                "metrics": run.metrics_before
            })
            
            # Phase 3: Inject faults
            run.current_phase = "injection"
            run.progress_percent = 40
            
            for target in experiment.targets:
                for fault in experiment.faults:
                    # Check abort conditions
                    if await self.safety_controller.check_abort_conditions(
                        run, experiment.abort_conditions
                    ):
                        run.status = ExperimentStatus.ABORTED
                        run.events.append({
                            "phase": "injection",
                            "timestamp": datetime.now().isoformat(),
                            "message": f"Experiment aborted: {self.safety_controller.abort_reason}"
                        })
                        
                        # Rollback
                        await self._rollback_all(experiment, run)
                        self.stats["aborted_experiments"] += 1
                        return run
                        
                    # Inject fault
                    result = await self.fault_injector.inject(target, fault)
                    run.affected_targets.append(target.name)
                    run.events.append({
                        "phase": "injection",
                        "timestamp": datetime.now().isoformat(),
                        "message": f"Fault injected: {result['details']}",
                        "target": target.name
                    })
                    self.stats["total_faults_injected"] += 1
                    
            # Phase 4: Wait for fault duration
            run.current_phase = "observation"
            run.progress_percent = 60
            
            max_duration = max((f.duration_seconds for f in experiment.faults), default=60)
            
            # Simulate observation period (scaled down for demo)
            await asyncio.sleep(min(max_duration * 0.01, 1))
            
            # Collect metrics during experiment
            run.metrics_after = await self.metrics_collector.collect_during_experiment(
                experiment.targets
            )
            
            run.events.append({
                "phase": "observation",
                "timestamp": datetime.now().isoformat(),
                "message": "Observation period completed",
                "metrics": run.metrics_after
            })
            
            # Phase 5: Rollback
            run.current_phase = "rollback"
            run.progress_percent = 80
            
            await self._rollback_all(experiment, run)
            
            # Phase 6: Validate steady state after
            run.current_phase = "steady_state_after"
            run.progress_percent = 90
            
            if experiment.steady_state_hypothesis:
                # Reset hypothesis for re-validation
                experiment.steady_state_hypothesis.result = HypothesisResult.UNKNOWN
                
                result = await self.hypothesis_validator.validate(
                    experiment.steady_state_hypothesis
                )
                
                run.hypothesis_result = result
                run.events.append({
                    "phase": "steady_state_after",
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Steady state hypothesis result: {result.value}",
                    "evidence": experiment.steady_state_hypothesis.evidence
                })
                
            # Complete
            run.current_phase = "complete"
            run.progress_percent = 100
            run.status = ExperimentStatus.COMPLETED
            run.completed_at = datetime.now()
            
            experiment.status = ExperimentStatus.COMPLETED
            experiment.completed_at = datetime.now()
            experiment.results = {
                "run_id": run.run_id,
                "hypothesis_result": run.hypothesis_result.value,
                "metrics_before": run.metrics_before,
                "metrics_after": run.metrics_after,
                "affected_targets": run.affected_targets
            }
            
            if run.hypothesis_result == HypothesisResult.PASSED:
                self.stats["successful_experiments"] += 1
            else:
                self.stats["failed_experiments"] += 1
                
        except Exception as e:
            run.status = ExperimentStatus.FAILED
            run.events.append({
                "phase": run.current_phase,
                "timestamp": datetime.now().isoformat(),
                "message": f"Experiment failed: {str(e)}",
                "error": True
            })
            experiment.status = ExperimentStatus.FAILED
            self.stats["failed_experiments"] += 1
            
        return run
        
    async def _rollback_all(self, experiment: ChaosExperiment,
                             run: ExperimentRun) -> None:
        """Откат всех сбоев"""
        for target in experiment.targets:
            for fault in experiment.faults:
                result = await self.fault_injector.rollback(target, fault)
                run.events.append({
                    "phase": "rollback",
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Rolled back {fault.fault_type.value} on {target.name}"
                })
                
    def create_gameday(self, name: str, description: str,
                        scheduled_date: datetime,
                        experiments: List[str] = None,
                        **kwargs) -> GameDay:
        """Создание игрового дня"""
        gameday = GameDay(
            gameday_id=f"gd_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            scheduled_date=scheduled_date,
            experiments=experiments or [],
            **kwargs
        )
        self.gamedays[gameday.gameday_id] = gameday
        self.stats["total_gamedays"] += 1
        return gameday
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        return {
            **self.stats,
            "experiments_count": len(self.experiments),
            "runs_count": len(self.runs),
            "gamedays_count": len(self.gamedays)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 101: Chaos Engineering Platform")
    print("=" * 60)
    
    async def demo():
        platform = ChaosEngineeringPlatform()
        print("✓ Chaos Engineering Platform created")
        
        # Create experiment 1: Latency injection
        print("\n🔬 Creating Chaos Experiments...")
        
        exp1 = platform.create_experiment(
            "API Latency Resilience Test",
            description="Test system resilience to increased API latency",
            created_by="sre-team",
            tags=["api", "latency", "resilience"]
        )
        
        # Add targets
        platform.add_target(
            exp1.experiment_id,
            TargetType.SERVICE,
            "api-gateway",
            namespace="production",
            labels={"app": "api-gateway"},
            percentage=50
        )
        
        platform.add_target(
            exp1.experiment_id,
            TargetType.SERVICE,
            "user-service",
            namespace="production",
            labels={"app": "user-service"}
        )
        
        # Add faults
        platform.add_fault(
            exp1.experiment_id,
            FaultType.LATENCY,
            latency_ms=500,
            jitter_ms=100,
            duration_seconds=120
        )
        
        # Set hypothesis
        platform.set_hypothesis(
            exp1.experiment_id,
            "System should maintain 99th percentile latency below 2s under 500ms injected latency",
            probes=[
                {"name": "latency_p99", "type": "prometheus", "query": "histogram_quantile(0.99, http_request_duration_seconds)"},
                {"name": "error_rate", "type": "prometheus", "query": "rate(http_requests_total{status=~'5..'}[5m])"},
                {"name": "health_check", "type": "http", "url": "http://api-gateway/health"}
            ]
        )
        
        # Add abort conditions
        exp1.abort_conditions = [
            {"type": "error_rate", "threshold": 50},
            {"type": "latency_p99", "threshold": 5000}
        ]
        
        print(f"  ✓ Experiment: {exp1.name}")
        print(f"    Targets: {len(exp1.targets)}")
        print(f"    Faults: {len(exp1.faults)}")
        
        # Create experiment 2: Error injection
        exp2 = platform.create_experiment(
            "Payment Service Error Handling",
            description="Test error handling in payment processing",
            created_by="payments-team",
            tags=["payments", "errors", "resilience"]
        )
        
        platform.add_target(
            exp2.experiment_id,
            TargetType.SERVICE,
            "payment-service",
            namespace="production"
        )
        
        platform.add_fault(
            exp2.experiment_id,
            FaultType.ERROR,
            error_code=503,
            error_message="Service Unavailable",
            error_rate=0.3,
            duration_seconds=60
        )
        
        platform.set_hypothesis(
            exp2.experiment_id,
            "Payment retries should handle 30% error rate without user impact",
            probes=[
                {"name": "payment_success_rate", "type": "custom", "metric": "payment_success_rate"},
                {"name": "retry_count", "type": "custom", "metric": "payment_retries_total"}
            ]
        )
        
        print(f"  ✓ Experiment: {exp2.name}")
        
        # Create experiment 3: CPU Stress
        exp3 = platform.create_experiment(
            "CPU Stress Test",
            description="Test system behavior under CPU pressure",
            created_by="platform-team",
            tags=["cpu", "stress", "performance"]
        )
        
        platform.add_target(
            exp3.experiment_id,
            TargetType.NODE,
            "worker-node-1",
            percentage=100
        )
        
        platform.add_fault(
            exp3.experiment_id,
            FaultType.CPU_STRESS,
            stress_level=80,
            workers=4,
            duration_seconds=180
        )
        
        print(f"  ✓ Experiment: {exp3.name}")
        
        # Create experiment 4: Network partition
        exp4 = platform.create_experiment(
            "Database Network Partition",
            description="Test behavior during database connectivity issues",
            created_by="dba-team",
            tags=["database", "network", "partition"]
        )
        
        platform.add_target(
            exp4.experiment_id,
            TargetType.DATABASE,
            "postgres-primary",
            namespace="databases"
        )
        
        platform.add_fault(
            exp4.experiment_id,
            FaultType.NETWORK_PARTITION,
            duration_seconds=30
        )
        
        print(f"  ✓ Experiment: {exp4.name}")
        
        # Run experiments
        print("\n🚀 Running Chaos Experiments...")
        
        runs = []
        for exp in [exp1, exp2, exp3]:
            print(f"\n  Running: {exp.name}")
            run = await platform.run_experiment(exp.experiment_id)
            runs.append(run)
            
            status_icon = {
                ExperimentStatus.COMPLETED: "✅",
                ExperimentStatus.FAILED: "❌",
                ExperimentStatus.ABORTED: "⛔"
            }.get(run.status, "❓")
            
            print(f"    {status_icon} Status: {run.status.value}")
            print(f"    Hypothesis: {run.hypothesis_result.value}")
            print(f"    Affected targets: {len(run.affected_targets)}")
            print(f"    Events: {len(run.events)}")
            
        # Show experiment timeline
        print("\n📊 Experiment Timeline:")
        
        for run in runs:
            exp = platform.experiments[run.experiment_id]
            print(f"\n  {exp.name}:")
            
            for event in run.events[:5]:
                phase = event.get("phase", "unknown")
                message = event.get("message", "")[:50]
                print(f"    [{phase}] {message}")
                
            if len(run.events) > 5:
                print(f"    ... and {len(run.events) - 5} more events")
                
        # Metrics comparison
        print("\n📈 Metrics Comparison (Before vs During):")
        
        for run in runs[:2]:
            exp = platform.experiments[run.experiment_id]
            print(f"\n  {exp.name}:")
            
            for key in list(run.metrics_before.keys())[:3]:
                before = run.metrics_before.get(key, 0)
                after = run.metrics_after.get(key, 0)
                change = ((after - before) / before * 100) if before > 0 else 0
                
                arrow = "↑" if change > 0 else "↓" if change < 0 else "→"
                print(f"    {key}: {before:.1f} → {after:.1f} ({arrow}{abs(change):.1f}%)")
                
        # Create Game Day
        print("\n🎮 Creating Game Day...")
        
        gameday = platform.create_gameday(
            "Q4 Resilience Game Day",
            description="Quarterly chaos engineering exercise to validate system resilience",
            scheduled_date=datetime.now() + timedelta(days=7),
            experiments=[exp1.experiment_id, exp2.experiment_id, exp4.experiment_id],
            participants=["sre-team", "platform-team", "dev-team"],
            scenario="""
            Scenario: Black Friday Traffic Surge
            1. Inject 500ms latency to API Gateway
            2. Introduce 30% errors in Payment Service  
            3. Simulate database failover
            4. Monitor system recovery
            """,
            duration_hours=4
        )
        
        print(f"  ✓ Game Day: {gameday.name}")
        print(f"    Date: {gameday.scheduled_date.strftime('%Y-%m-%d')}")
        print(f"    Duration: {gameday.duration_hours} hours")
        print(f"    Experiments: {len(gameday.experiments)}")
        print(f"    Participants: {', '.join(gameday.participants)}")
        
        # Statistics
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Experiments: {stats['total_experiments']}")
        print(f"  Successful: {stats['successful_experiments']}")
        print(f"  Failed: {stats['failed_experiments']}")
        print(f"  Aborted: {stats['aborted_experiments']}")
        print(f"  Total Faults Injected: {stats['total_faults_injected']}")
        print(f"  Game Days: {stats['total_gamedays']}")
        
        # Dashboard
        print("\n📋 Chaos Engineering Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │             Chaos Engineering Overview                      │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Experiments:     {stats['experiments_count']:>6}                                │")
        print(f"  │ Runs:            {stats['runs_count']:>6}                                │")
        print(f"  │ Successful:      {stats['successful_experiments']:>6}                                │")
        print(f"  │ Failed:          {stats['failed_experiments']:>6}                                │")
        print(f"  │ Faults Injected: {stats['total_faults_injected']:>6}                                │")
        print(f"  │ Game Days:       {stats['total_gamedays']:>6}                                │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Chaos Engineering Platform initialized!")
    print("=" * 60)
