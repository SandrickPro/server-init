#!/usr/bin/env python3
"""
Server Init - Iteration 230: Chaos Testing Platform
Платформа хаос-тестирования

Функционал:
- Fault Injection - инъекция сбоев
- Experiment Design - дизайн экспериментов
- Steady State - устойчивое состояние
- Blast Radius - радиус поражения
- Game Days - игровые дни
- Hypothesis Testing - тестирование гипотез
- Recovery Validation - валидация восстановления
- Reports & Analytics - отчёты и аналитика
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class FaultType(Enum):
    """Тип сбоя"""
    LATENCY = "latency"
    CPU_STRESS = "cpu_stress"
    MEMORY_STRESS = "memory_stress"
    NETWORK_PARTITION = "network_partition"
    PROCESS_KILL = "process_kill"
    DISK_FILL = "disk_fill"
    DNS_FAILURE = "dns_failure"
    PACKET_LOSS = "packet_loss"


class ExperimentStatus(Enum):
    """Статус эксперимента"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class HypothesisResult(Enum):
    """Результат гипотезы"""
    PASSED = "passed"
    FAILED = "failed"
    INCONCLUSIVE = "inconclusive"


class TargetType(Enum):
    """Тип цели"""
    SERVICE = "service"
    POD = "pod"
    NODE = "node"
    CONTAINER = "container"
    NETWORK = "network"


@dataclass
class Target:
    """Цель для хаос-теста"""
    target_id: str
    name: str = ""
    target_type: TargetType = TargetType.SERVICE
    selector: Dict[str, str] = field(default_factory=dict)
    namespace: str = "default"


@dataclass
class FaultAction:
    """Действие сбоя"""
    action_id: str
    fault_type: FaultType = FaultType.LATENCY
    
    # Parameters
    duration_seconds: int = 60
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Target
    target: Optional[Target] = None
    
    # Percentage of targets to affect
    percentage: int = 100


@dataclass
class SteadyState:
    """Устойчивое состояние"""
    state_id: str
    name: str = ""
    description: str = ""
    
    # Probes
    probes: List[str] = field(default_factory=list)  # Health check URLs
    
    # Expected values
    expected_latency_ms: float = 100
    expected_error_rate: float = 0.01
    expected_availability: float = 99.9
    
    # Actual values (filled during experiment)
    actual_latency_ms: float = 0
    actual_error_rate: float = 0
    actual_availability: float = 0
    
    # Result
    is_met: bool = False


@dataclass
class Hypothesis:
    """Гипотеза"""
    hypothesis_id: str
    description: str = ""
    
    # Steady state before and after
    steady_state: Optional[SteadyState] = None
    
    # Result
    result: HypothesisResult = HypothesisResult.INCONCLUSIVE
    
    # Evidence
    evidence: str = ""


@dataclass
class ChaosExperiment:
    """Хаос-эксперимент"""
    experiment_id: str
    name: str = ""
    description: str = ""
    
    # Status
    status: ExperimentStatus = ExperimentStatus.DRAFT
    
    # Hypothesis
    hypothesis: Optional[Hypothesis] = None
    
    # Actions
    actions: List[FaultAction] = field(default_factory=list)
    
    # Blast radius
    blast_radius: str = "single-service"  # single-service, namespace, cluster
    
    # Rollback
    auto_rollback: bool = True
    rollback_threshold_error_rate: float = 0.5
    
    # Schedule
    scheduled_at: Optional[datetime] = None
    
    # Execution
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Owner
    owner: str = ""


@dataclass
class GameDay:
    """Игровой день"""
    game_day_id: str
    name: str = ""
    description: str = ""
    
    # Experiments
    experiments: List[str] = field(default_factory=list)
    
    # Schedule
    scheduled_date: datetime = field(default_factory=datetime.now)
    duration_hours: int = 4
    
    # Participants
    participants: List[str] = field(default_factory=list)
    
    # Status
    is_completed: bool = False
    
    # Results
    total_experiments: int = 0
    passed_experiments: int = 0
    failed_experiments: int = 0


@dataclass
class ExperimentResult:
    """Результат эксперимента"""
    result_id: str
    experiment_id: str = ""
    
    # Outcome
    hypothesis_validated: bool = False
    
    # Metrics during experiment
    avg_latency_ms: float = 0
    max_latency_ms: float = 0
    error_rate: float = 0
    
    # Recovery
    recovery_time_seconds: float = 0
    
    # Findings
    findings: List[str] = field(default_factory=list)
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)


class FaultInjector:
    """Инжектор сбоев"""
    
    def __init__(self):
        self.active_faults: Dict[str, FaultAction] = {}
        
    async def inject(self, action: FaultAction) -> bool:
        """Инъекция сбоя"""
        self.active_faults[action.action_id] = action
        
        # Simulate fault injection
        await asyncio.sleep(0.1)
        
        return True
        
    async def rollback(self, action_id: str) -> bool:
        """Откат сбоя"""
        if action_id in self.active_faults:
            del self.active_faults[action_id]
            return True
        return False
        
    async def rollback_all(self):
        """Откат всех сбоев"""
        self.active_faults.clear()


class SteadyStateValidator:
    """Валидатор устойчивого состояния"""
    
    def validate(self, state: SteadyState) -> bool:
        """Валидация устойчивого состояния"""
        # Simulate validation
        state.actual_latency_ms = random.uniform(50, 200)
        state.actual_error_rate = random.uniform(0, 0.05)
        state.actual_availability = random.uniform(98, 100)
        
        state.is_met = (
            state.actual_latency_ms <= state.expected_latency_ms * 1.5 and
            state.actual_error_rate <= state.expected_error_rate * 2 and
            state.actual_availability >= state.expected_availability * 0.99
        )
        
        return state.is_met


class ChaosTestingPlatform:
    """Платформа хаос-тестирования"""
    
    def __init__(self):
        self.experiments: Dict[str, ChaosExperiment] = {}
        self.game_days: Dict[str, GameDay] = {}
        self.results: Dict[str, ExperimentResult] = {}
        self.injector = FaultInjector()
        self.validator = SteadyStateValidator()
        
    def create_target(self, name: str, target_type: TargetType,
                     selector: Dict[str, str] = None) -> Target:
        """Создание цели"""
        return Target(
            target_id=f"tgt_{uuid.uuid4().hex[:8]}",
            name=name,
            target_type=target_type,
            selector=selector or {}
        )
        
    def create_action(self, fault_type: FaultType, target: Target,
                     duration: int = 60, params: Dict[str, Any] = None) -> FaultAction:
        """Создание действия сбоя"""
        return FaultAction(
            action_id=f"act_{uuid.uuid4().hex[:8]}",
            fault_type=fault_type,
            duration_seconds=duration,
            parameters=params or {},
            target=target
        )
        
    def create_experiment(self, name: str, description: str,
                         hypothesis_desc: str,
                         owner: str = "") -> ChaosExperiment:
        """Создание эксперимента"""
        # Create steady state
        steady_state = SteadyState(
            state_id=f"ss_{uuid.uuid4().hex[:8]}",
            name=f"Steady state for {name}"
        )
        
        # Create hypothesis
        hypothesis = Hypothesis(
            hypothesis_id=f"hyp_{uuid.uuid4().hex[:8]}",
            description=hypothesis_desc,
            steady_state=steady_state
        )
        
        experiment = ChaosExperiment(
            experiment_id=f"exp_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            hypothesis=hypothesis,
            owner=owner
        )
        
        self.experiments[experiment.experiment_id] = experiment
        return experiment
        
    def add_action(self, experiment_id: str, action: FaultAction):
        """Добавление действия"""
        exp = self.experiments.get(experiment_id)
        if exp:
            exp.actions.append(action)
            
    async def run_experiment(self, experiment_id: str) -> Optional[ExperimentResult]:
        """Запуск эксперимента"""
        exp = self.experiments.get(experiment_id)
        if not exp:
            return None
            
        exp.status = ExperimentStatus.RUNNING
        exp.started_at = datetime.now()
        
        # Validate steady state before
        if exp.hypothesis and exp.hypothesis.steady_state:
            self.validator.validate(exp.hypothesis.steady_state)
            
        # Inject faults
        for action in exp.actions:
            await self.injector.inject(action)
            
        # Wait for experiment duration
        max_duration = max((a.duration_seconds for a in exp.actions), default=60)
        await asyncio.sleep(0.1)  # Simulated wait
        
        # Validate steady state after
        hypothesis_validated = True
        if exp.hypothesis and exp.hypothesis.steady_state:
            hypothesis_validated = self.validator.validate(exp.hypothesis.steady_state)
            exp.hypothesis.result = (
                HypothesisResult.PASSED if hypothesis_validated 
                else HypothesisResult.FAILED
            )
            
        # Rollback
        await self.injector.rollback_all()
        
        # Complete experiment
        exp.status = ExperimentStatus.COMPLETED
        exp.completed_at = datetime.now()
        exp.duration_seconds = (exp.completed_at - exp.started_at).total_seconds()
        
        # Create result
        result = ExperimentResult(
            result_id=f"res_{uuid.uuid4().hex[:8]}",
            experiment_id=experiment_id,
            hypothesis_validated=hypothesis_validated,
            avg_latency_ms=random.uniform(50, 300),
            max_latency_ms=random.uniform(200, 1000),
            error_rate=random.uniform(0, 0.1),
            recovery_time_seconds=random.uniform(5, 60),
            findings=[
                "System recovered within SLO",
                "Circuit breaker activated correctly"
            ] if hypothesis_validated else [
                "Recovery time exceeded threshold",
                "Error rate spiked above acceptable levels"
            ],
            recommendations=[
                "Consider adding retry logic",
                "Increase timeout for downstream calls"
            ]
        )
        
        self.results[result.result_id] = result
        return result
        
    def create_game_day(self, name: str, description: str,
                       experiments: List[str], participants: List[str]) -> GameDay:
        """Создание игрового дня"""
        game_day = GameDay(
            game_day_id=f"gd_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            experiments=experiments,
            participants=participants,
            total_experiments=len(experiments)
        )
        self.game_days[game_day.game_day_id] = game_day
        return game_day
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        experiments = list(self.experiments.values())
        completed = [e for e in experiments if e.status == ExperimentStatus.COMPLETED]
        
        results = list(self.results.values())
        validated = [r for r in results if r.hypothesis_validated]
        
        by_fault_type = {}
        for e in experiments:
            for a in e.actions:
                t = a.fault_type.value
                if t not in by_fault_type:
                    by_fault_type[t] = 0
                by_fault_type[t] += 1
                
        return {
            "total_experiments": len(experiments),
            "completed_experiments": len(completed),
            "hypotheses_validated": len(validated),
            "hypotheses_failed": len(results) - len(validated),
            "by_fault_type": by_fault_type,
            "game_days": len(self.game_days),
            "avg_recovery_time": sum(r.recovery_time_seconds for r in results) / len(results) if results else 0
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 230: Chaos Testing Platform")
    print("=" * 60)
    
    platform = ChaosTestingPlatform()
    print("✓ Chaos Testing Platform created")
    
    # Create targets
    print("\n🎯 Creating Targets...")
    
    targets = [
        platform.create_target("api-gateway", TargetType.SERVICE, {"app": "api-gateway"}),
        platform.create_target("user-service", TargetType.SERVICE, {"app": "user-service"}),
        platform.create_target("payment-service", TargetType.SERVICE, {"app": "payment"}),
        platform.create_target("database-pod", TargetType.POD, {"app": "postgres"}),
        platform.create_target("cache-node", TargetType.NODE, {"role": "cache"}),
    ]
    
    for target in targets:
        type_icons = {
            TargetType.SERVICE: "🔧",
            TargetType.POD: "📦",
            TargetType.NODE: "🖥️",
            TargetType.CONTAINER: "🐳",
            TargetType.NETWORK: "🌐"
        }
        print(f"  {type_icons[target.target_type]} {target.name} ({target.target_type.value})")
        
    # Create experiments
    print("\n🔬 Creating Chaos Experiments...")
    
    experiments_config = [
        ("api-latency-test", "Test API resilience to latency", 
         "API should maintain <500ms p99 under 200ms added latency",
         targets[0], FaultType.LATENCY, {"latency_ms": 200}),
        ("cpu-stress-test", "Test service under CPU pressure",
         "Service should auto-scale when CPU exceeds 80%",
         targets[1], FaultType.CPU_STRESS, {"percentage": 90}),
        ("network-partition", "Test network partition handling",
         "System should handle network partition with graceful degradation",
         targets[2], FaultType.NETWORK_PARTITION, {}),
        ("database-failover", "Test database failover",
         "Application should failover to replica within 30s",
         targets[3], FaultType.PROCESS_KILL, {}),
        ("cache-failure", "Test cache failure handling",
         "Application should function without cache with degraded performance",
         targets[4], FaultType.MEMORY_STRESS, {"percentage": 95}),
    ]
    
    experiments = []
    for name, desc, hypothesis, target, fault_type, params in experiments_config:
        exp = platform.create_experiment(name, desc, hypothesis, "SRE Team")
        action = platform.create_action(fault_type, target, 60, params)
        platform.add_action(exp.experiment_id, action)
        experiments.append(exp)
        
        fault_icons = {
            FaultType.LATENCY: "⏱️",
            FaultType.CPU_STRESS: "🔥",
            FaultType.MEMORY_STRESS: "🧠",
            FaultType.NETWORK_PARTITION: "🔌",
            FaultType.PROCESS_KILL: "💀",
            FaultType.DISK_FILL: "💾",
            FaultType.DNS_FAILURE: "🌐",
            FaultType.PACKET_LOSS: "📡"
        }
        print(f"  {fault_icons[fault_type]} {name}: {fault_type.value}")
        
    # Run experiments
    print("\n🚀 Running Experiments...")
    
    results = []
    for exp in experiments:
        result = await platform.run_experiment(exp.experiment_id)
        if result:
            results.append(result)
            
            status_icon = "✓" if result.hypothesis_validated else "✗"
            status_text = "PASSED" if result.hypothesis_validated else "FAILED"
            print(f"  {status_icon} {exp.name}: {status_text}")
            
    # Create game day
    print("\n🎮 Creating Game Day...")
    
    game_day = platform.create_game_day(
        "Q4 Resilience Game Day",
        "Quarterly chaos engineering game day",
        [e.experiment_id for e in experiments],
        ["SRE Team", "Platform Team", "Backend Team"]
    )
    
    game_day.passed_experiments = len([r for r in results if r.hypothesis_validated])
    game_day.failed_experiments = len(results) - game_day.passed_experiments
    game_day.is_completed = True
    
    print(f"  ✓ {game_day.name}")
    print(f"    Experiments: {game_day.passed_experiments}/{game_day.total_experiments} passed")
    print(f"    Participants: {', '.join(game_day.participants)}")
    
    # Display experiments
    print("\n📋 Experiment Results:")
    
    print("\n  ┌────────────────────────────┬─────────────────┬──────────┬────────────┐")
    print("  │ Experiment                 │ Fault Type      │ Result   │ Recovery   │")
    print("  ├────────────────────────────┼─────────────────┼──────────┼────────────┤")
    
    for i, exp in enumerate(experiments):
        name = exp.name[:26].ljust(26)
        fault = exp.actions[0].fault_type.value if exp.actions else "N/A"
        fault = fault[:15].ljust(15)
        
        result = results[i] if i < len(results) else None
        if result:
            res = "✓ PASS" if result.hypothesis_validated else "✗ FAIL"
            recovery = f"{result.recovery_time_seconds:.1f}s"
        else:
            res = "N/A"
            recovery = "N/A"
        res = res[:8].ljust(8)
        recovery = recovery[:10].ljust(10)
        
        print(f"  │ {name} │ {fault} │ {res} │ {recovery} │")
        
    print("  └────────────────────────────┴─────────────────┴──────────┴────────────┘")
    
    # Hypothesis details
    print("\n📊 Hypothesis Results:")
    
    for exp in experiments:
        if exp.hypothesis:
            result_icons = {
                HypothesisResult.PASSED: "✓",
                HypothesisResult.FAILED: "✗",
                HypothesisResult.INCONCLUSIVE: "?"
            }
            icon = result_icons.get(exp.hypothesis.result, "?")
            print(f"  {icon} {exp.name}:")
            print(f"    \"{exp.hypothesis.description[:60]}...\"")
            
    # Findings and recommendations
    print("\n💡 Key Findings:")
    
    for result in results[:3]:
        exp = platform.experiments.get(result.experiment_id)
        name = exp.name if exp else "unknown"
        print(f"\n  {name}:")
        for finding in result.findings[:2]:
            print(f"    • {finding}")
            
    print("\n📝 Recommendations:")
    
    all_recs = set()
    for result in results:
        all_recs.update(result.recommendations)
        
    for rec in list(all_recs)[:5]:
        print(f"  • {rec}")
        
    # Fault type distribution
    print("\n🔥 Experiments by Fault Type:")
    
    stats = platform.get_statistics()
    
    fault_icons = {
        "latency": "⏱️",
        "cpu_stress": "🔥",
        "memory_stress": "🧠",
        "network_partition": "🔌",
        "process_kill": "💀"
    }
    
    for fault, count in stats["by_fault_type"].items():
        icon = fault_icons.get(fault, "❓")
        bar = "█" * count + "░" * (3 - count)
        print(f"  {icon} {fault:18s} [{bar}] {count}")
        
    # Statistics
    print("\n📈 Platform Statistics:")
    
    print(f"\n  Total Experiments: {stats['total_experiments']}")
    print(f"  Completed: {stats['completed_experiments']}")
    print(f"  Hypotheses Validated: {stats['hypotheses_validated']}")
    print(f"  Hypotheses Failed: {stats['hypotheses_failed']}")
    print(f"  Avg Recovery Time: {stats['avg_recovery_time']:.1f}s")
    
    # Success rate
    total = stats['hypotheses_validated'] + stats['hypotheses_failed']
    success_rate = (stats['hypotheses_validated'] / total * 100) if total > 0 else 0
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                      Chaos Testing Dashboard                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Experiments:             {stats['total_experiments']:>12}                        │")
    print(f"│ Completed:                     {stats['completed_experiments']:>12}                        │")
    print(f"│ Hypotheses Validated:          {stats['hypotheses_validated']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Success Rate:                    {success_rate:>10.1f}%                       │")
    print(f"│ Avg Recovery (seconds):          {stats['avg_recovery_time']:>10.1f}                       │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Chaos Testing Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
