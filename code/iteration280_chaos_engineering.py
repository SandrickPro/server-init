#!/usr/bin/env python3
"""
Server Init - Iteration 280: Chaos Engineering Platform
Платформа хаос-инженерии

Функционал:
- Experiment Design - дизайн экспериментов
- Fault Injection - внедрение сбоев
- Steady State Hypothesis - гипотеза устойчивого состояния
- Blast Radius - радиус поражения
- Safety Controls - контроли безопасности
- Experiment Scheduling - планирование экспериментов
- Result Analysis - анализ результатов
- Resilience Score - оценка устойчивости
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid


class FaultType(Enum):
    """Тип сбоя"""
    LATENCY = "latency"
    ERROR = "error"
    KILL = "kill"
    CPU_STRESS = "cpu_stress"
    MEMORY_STRESS = "memory_stress"
    DISK_FILL = "disk_fill"
    NETWORK_PARTITION = "network_partition"
    DNS_FAILURE = "dns_failure"
    PACKET_LOSS = "packet_loss"
    BLACKHOLE = "blackhole"


class ExperimentStatus(Enum):
    """Статус эксперимента"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABORTED = "aborted"
    FAILED = "failed"


class TargetType(Enum):
    """Тип цели"""
    SERVICE = "service"
    POD = "pod"
    NODE = "node"
    CONTAINER = "container"
    NETWORK = "network"


class SteadyStateType(Enum):
    """Тип устойчивого состояния"""
    METRIC = "metric"
    PROBE = "probe"
    HTTP = "http"
    COMMAND = "command"


@dataclass
class SteadyStateProbe:
    """Проба устойчивого состояния"""
    probe_id: str
    name: str
    
    # Type
    probe_type: SteadyStateType = SteadyStateType.METRIC
    
    # Configuration
    metric_name: str = ""
    http_url: str = ""
    command: str = ""
    
    # Tolerance
    operator: str = "<"  # <, >, ==, <=, >=
    value: float = 0
    
    # Result
    passed: bool = True
    actual_value: Optional[float] = None
    last_check: Optional[datetime] = None


@dataclass
class FaultConfig:
    """Конфигурация сбоя"""
    config_id: str
    
    # Fault type
    fault_type: FaultType = FaultType.LATENCY
    
    # Parameters
    latency_ms: int = 0
    error_rate: float = 0
    cpu_percent: int = 0
    memory_mb: int = 0
    disk_gb: int = 0
    packet_loss_percent: int = 0
    
    # Duration
    duration_seconds: int = 60
    
    # Ramp
    ramp_up_seconds: int = 0
    ramp_down_seconds: int = 0


@dataclass
class Target:
    """Цель эксперимента"""
    target_id: str
    name: str
    
    # Type
    target_type: TargetType = TargetType.SERVICE
    
    # Selection
    namespace: str = "default"
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Specific targets
    service_name: str = ""
    pod_names: List[str] = field(default_factory=list)
    node_names: List[str] = field(default_factory=list)
    
    # Percentage
    percentage: int = 100  # % of targets to affect


@dataclass
class BlastRadius:
    """Радиус поражения"""
    radius_id: str
    
    # Scope
    max_services: int = 1
    max_pods: int = 3
    max_nodes: int = 1
    
    # Percentage
    max_percentage: int = 50
    
    # Exclusions
    excluded_namespaces: List[str] = field(default_factory=list)
    excluded_services: List[str] = field(default_factory=list)


@dataclass
class SafetyControl:
    """Контроль безопасности"""
    control_id: str
    name: str
    
    # Type
    check_type: str = "metric"  # metric, http, manual
    
    # Condition
    metric_name: str = ""
    threshold: float = 0
    operator: str = ">"
    
    # Action
    abort_on_failure: bool = True
    
    # State
    triggered: bool = False


@dataclass
class ExperimentResult:
    """Результат эксперимента"""
    result_id: str
    experiment_id: str
    
    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    
    # Steady state
    pre_hypothesis_passed: bool = False
    post_hypothesis_passed: bool = False
    
    # Metrics
    metrics_collected: Dict[str, List[float]] = field(default_factory=dict)
    
    # Status
    success: bool = False
    failure_reason: str = ""
    
    # Learnings
    observations: List[str] = field(default_factory=list)


@dataclass
class Experiment:
    """Эксперимент"""
    experiment_id: str
    name: str
    
    # Description
    description: str = ""
    hypothesis: str = ""
    
    # Steady state
    steady_state_probes: List[SteadyStateProbe] = field(default_factory=list)
    
    # Faults
    faults: List[FaultConfig] = field(default_factory=list)
    
    # Target
    target: Optional[Target] = None
    
    # Blast radius
    blast_radius: Optional[BlastRadius] = None
    
    # Safety controls
    safety_controls: List[SafetyControl] = field(default_factory=list)
    
    # Schedule
    scheduled_time: Optional[datetime] = None
    recurring: bool = False
    cron_expression: str = ""
    
    # Status
    status: ExperimentStatus = ExperimentStatus.DRAFT
    
    # Results
    results: List[ExperimentResult] = field(default_factory=list)
    
    # Owner
    owner: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ResilienceScore:
    """Оценка устойчивости"""
    score_id: str
    service: str
    
    # Scores
    overall_score: float = 0  # 0-100
    
    # Categories
    latency_resilience: float = 0
    error_resilience: float = 0
    resource_resilience: float = 0
    network_resilience: float = 0
    
    # Experiments
    experiments_run: int = 0
    experiments_passed: int = 0
    
    # Timestamp
    calculated_at: datetime = field(default_factory=datetime.now)


class ChaosEngineeringManager:
    """Менеджер хаос-инженерии"""
    
    def __init__(self):
        self.experiments: Dict[str, Experiment] = {}
        self.resilience_scores: Dict[str, ResilienceScore] = {}
        self.global_blast_radius: Optional[BlastRadius] = None
        self.global_safety_controls: List[SafetyControl] = []
        self.running_experiments: List[str] = []
        
    def set_global_blast_radius(self,
                               max_services: int = 1,
                               max_pods: int = 3,
                               max_nodes: int = 1) -> BlastRadius:
        """Установка глобального радиуса поражения"""
        self.global_blast_radius = BlastRadius(
            radius_id=f"radius_{uuid.uuid4().hex[:8]}",
            max_services=max_services,
            max_pods=max_pods,
            max_nodes=max_nodes
        )
        return self.global_blast_radius
        
    def add_global_safety_control(self, name: str,
                                 metric_name: str,
                                 threshold: float,
                                 operator: str = ">") -> SafetyControl:
        """Добавление глобального контроля безопасности"""
        control = SafetyControl(
            control_id=f"safety_{uuid.uuid4().hex[:8]}",
            name=name,
            metric_name=metric_name,
            threshold=threshold,
            operator=operator
        )
        
        self.global_safety_controls.append(control)
        return control
        
    def create_experiment(self, name: str,
                         description: str = "",
                         hypothesis: str = "") -> Experiment:
        """Создание эксперимента"""
        experiment = Experiment(
            experiment_id=f"exp_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            hypothesis=hypothesis
        )
        
        # Apply global blast radius
        if self.global_blast_radius:
            experiment.blast_radius = self.global_blast_radius
            
        # Apply global safety controls
        experiment.safety_controls = self.global_safety_controls.copy()
        
        self.experiments[name] = experiment
        return experiment
        
    def add_steady_state_probe(self, experiment_name: str,
                              probe_name: str,
                              probe_type: SteadyStateType,
                              **kwargs) -> SteadyStateProbe:
        """Добавление пробы устойчивого состояния"""
        experiment = self.experiments.get(experiment_name)
        if not experiment:
            return None
            
        probe = SteadyStateProbe(
            probe_id=f"probe_{uuid.uuid4().hex[:8]}",
            name=probe_name,
            probe_type=probe_type,
            **kwargs
        )
        
        experiment.steady_state_probes.append(probe)
        return probe
        
    def add_fault(self, experiment_name: str,
                 fault_type: FaultType,
                 duration_seconds: int = 60,
                 **kwargs) -> FaultConfig:
        """Добавление сбоя"""
        experiment = self.experiments.get(experiment_name)
        if not experiment:
            return None
            
        fault = FaultConfig(
            config_id=f"fault_{uuid.uuid4().hex[:8]}",
            fault_type=fault_type,
            duration_seconds=duration_seconds,
            **kwargs
        )
        
        experiment.faults.append(fault)
        return fault
        
    def set_target(self, experiment_name: str,
                  target_type: TargetType,
                  **kwargs) -> Target:
        """Установка цели"""
        experiment = self.experiments.get(experiment_name)
        if not experiment:
            return None
            
        target = Target(
            target_id=f"target_{uuid.uuid4().hex[:8]}",
            name=kwargs.get("name", "target"),
            target_type=target_type,
            **{k: v for k, v in kwargs.items() if k != "name"}
        )
        
        experiment.target = target
        return target
        
    async def run_experiment(self, experiment_name: str) -> ExperimentResult:
        """Запуск эксперимента"""
        experiment = self.experiments.get(experiment_name)
        if not experiment:
            return None
            
        # Check if already running
        if experiment_name in self.running_experiments:
            return None
            
        experiment.status = ExperimentStatus.RUNNING
        self.running_experiments.append(experiment_name)
        
        result = ExperimentResult(
            result_id=f"result_{uuid.uuid4().hex[:8]}",
            experiment_id=experiment.experiment_id
        )
        
        try:
            # Check pre-hypothesis
            result.pre_hypothesis_passed = await self._check_steady_state(experiment)
            
            if not result.pre_hypothesis_passed:
                result.success = False
                result.failure_reason = "Pre-hypothesis failed"
                result.observations.append("System was not in steady state before experiment")
            else:
                # Inject faults
                await self._inject_faults(experiment, result)
                
                # Check safety controls during execution
                safety_triggered = await self._check_safety_controls(experiment)
                
                if safety_triggered:
                    result.success = False
                    result.failure_reason = "Safety control triggered"
                    result.observations.append("Experiment aborted due to safety control")
                else:
                    # Check post-hypothesis
                    result.post_hypothesis_passed = await self._check_steady_state(experiment)
                    
                    if result.post_hypothesis_passed:
                        result.success = True
                        result.observations.append("System maintained steady state during chaos")
                    else:
                        result.success = False
                        result.failure_reason = "Post-hypothesis failed"
                        result.observations.append("System did not maintain steady state")
                        
        except Exception as e:
            result.success = False
            result.failure_reason = str(e)
            experiment.status = ExperimentStatus.FAILED
        finally:
            result.ended_at = datetime.now()
            experiment.results.append(result)
            experiment.status = ExperimentStatus.COMPLETED
            self.running_experiments.remove(experiment_name)
            
            # Update resilience score
            if experiment.target:
                self._update_resilience_score(experiment, result)
                
        return result
        
    async def _check_steady_state(self, experiment: Experiment) -> bool:
        """Проверка устойчивого состояния"""
        for probe in experiment.steady_state_probes:
            # Simulate probe check
            await asyncio.sleep(0.1)
            
            probe.actual_value = random.uniform(0, 100)
            probe.last_check = datetime.now()
            
            # Check against tolerance
            if probe.operator == "<":
                probe.passed = probe.actual_value < probe.value
            elif probe.operator == ">":
                probe.passed = probe.actual_value > probe.value
            elif probe.operator == "==":
                probe.passed = abs(probe.actual_value - probe.value) < 0.1
            elif probe.operator == "<=":
                probe.passed = probe.actual_value <= probe.value
            elif probe.operator == ">=":
                probe.passed = probe.actual_value >= probe.value
                
            if not probe.passed:
                return False
                
        return True
        
    async def _inject_faults(self, experiment: Experiment,
                            result: ExperimentResult):
        """Внедрение сбоев"""
        for fault in experiment.faults:
            # Simulate fault injection
            result.observations.append(f"Injected {fault.fault_type.value} fault")
            
            # Collect metrics during fault
            metrics = []
            for _ in range(fault.duration_seconds // 10):
                await asyncio.sleep(0.1)  # Simulated
                metrics.append(random.uniform(50, 150))
                
            result.metrics_collected[fault.fault_type.value] = metrics
            
    async def _check_safety_controls(self, experiment: Experiment) -> bool:
        """Проверка контролей безопасности"""
        for control in experiment.safety_controls:
            # Simulate metric check
            current_value = random.uniform(0, 100)
            
            triggered = False
            if control.operator == ">" and current_value > control.threshold:
                triggered = True
            elif control.operator == "<" and current_value < control.threshold:
                triggered = True
                
            if triggered and control.abort_on_failure:
                control.triggered = True
                return True
                
        return False
        
    def _update_resilience_score(self, experiment: Experiment,
                                result: ExperimentResult):
        """Обновление оценки устойчивости"""
        service = experiment.target.service_name or experiment.target.name
        
        if service not in self.resilience_scores:
            self.resilience_scores[service] = ResilienceScore(
                score_id=f"score_{uuid.uuid4().hex[:8]}",
                service=service
            )
            
        score = self.resilience_scores[service]
        score.experiments_run += 1
        
        if result.success:
            score.experiments_passed += 1
            
        # Calculate overall score
        score.overall_score = (score.experiments_passed / score.experiments_run) * 100
        
        # Update category scores based on fault types
        for fault in experiment.faults:
            if fault.fault_type == FaultType.LATENCY:
                score.latency_resilience = score.overall_score * random.uniform(0.8, 1.2)
            elif fault.fault_type in [FaultType.ERROR, FaultType.KILL]:
                score.error_resilience = score.overall_score * random.uniform(0.8, 1.2)
            elif fault.fault_type in [FaultType.CPU_STRESS, FaultType.MEMORY_STRESS, FaultType.DISK_FILL]:
                score.resource_resilience = score.overall_score * random.uniform(0.8, 1.2)
            elif fault.fault_type in [FaultType.NETWORK_PARTITION, FaultType.PACKET_LOSS, FaultType.BLACKHOLE]:
                score.network_resilience = score.overall_score * random.uniform(0.8, 1.2)
                
        # Clamp scores
        score.latency_resilience = min(100, max(0, score.latency_resilience))
        score.error_resilience = min(100, max(0, score.error_resilience))
        score.resource_resilience = min(100, max(0, score.resource_resilience))
        score.network_resilience = min(100, max(0, score.network_resilience))
        
        score.calculated_at = datetime.now()
        
    def schedule_experiment(self, experiment_name: str,
                           scheduled_time: datetime) -> bool:
        """Планирование эксперимента"""
        experiment = self.experiments.get(experiment_name)
        if not experiment:
            return False
            
        experiment.scheduled_time = scheduled_time
        experiment.status = ExperimentStatus.SCHEDULED
        return True
        
    def abort_experiment(self, experiment_name: str) -> bool:
        """Отмена эксперимента"""
        experiment = self.experiments.get(experiment_name)
        if not experiment:
            return False
            
        if experiment_name in self.running_experiments:
            self.running_experiments.remove(experiment_name)
            
        experiment.status = ExperimentStatus.ABORTED
        return True
        
    def get_resilience_report(self) -> Dict[str, Any]:
        """Получение отчета об устойчивости"""
        report = {
            "total_experiments": len(self.experiments),
            "completed": sum(1 for e in self.experiments.values() if e.status == ExperimentStatus.COMPLETED),
            "services": {},
            "overall_resilience": 0
        }
        
        for service, score in self.resilience_scores.items():
            report["services"][service] = {
                "overall": score.overall_score,
                "latency": score.latency_resilience,
                "error": score.error_resilience,
                "resource": score.resource_resilience,
                "network": score.network_resilience,
                "experiments_run": score.experiments_run,
                "experiments_passed": score.experiments_passed
            }
            
        if self.resilience_scores:
            report["overall_resilience"] = sum(
                s.overall_score for s in self.resilience_scores.values()
            ) / len(self.resilience_scores)
            
        return report
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        status_counts = {s.value: 0 for s in ExperimentStatus}
        
        for exp in self.experiments.values():
            status_counts[exp.status.value] += 1
            
        total_results = sum(len(e.results) for e in self.experiments.values())
        successful = sum(
            sum(1 for r in e.results if r.success)
            for e in self.experiments.values()
        )
        
        return {
            "total_experiments": len(self.experiments),
            "status_counts": status_counts,
            "running": len(self.running_experiments),
            "total_runs": total_results,
            "successful_runs": successful,
            "services_tested": len(self.resilience_scores)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 280: Chaos Engineering Platform")
    print("=" * 60)
    
    manager = ChaosEngineeringManager()
    print("✓ Chaos Engineering Manager created")
    
    # Set global blast radius
    print("\n💥 Setting Global Blast Radius...")
    
    manager.set_global_blast_radius(
        max_services=2,
        max_pods=5,
        max_nodes=2
    )
    print("  Max services: 2, Max pods: 5, Max nodes: 2")
    
    # Add global safety controls
    print("\n🛡️ Adding Global Safety Controls...")
    
    manager.add_global_safety_control("error-rate", "error_rate", 10, ">")
    manager.add_global_safety_control("latency-p99", "latency_p99", 1000, ">")
    manager.add_global_safety_control("availability", "availability", 95, "<")
    print("  Added 3 global safety controls")
    
    # Create experiments
    print("\n🧪 Creating Experiments...")
    
    experiments_config = [
        {
            "name": "api-latency-test",
            "description": "Test API gateway resilience to latency",
            "hypothesis": "API should maintain SLO when upstream latency increases",
            "target": ("api-gateway", TargetType.SERVICE),
            "faults": [(FaultType.LATENCY, {"latency_ms": 500, "duration_seconds": 60})],
            "probes": [("error_rate", SteadyStateType.METRIC, "<", 5)]
        },
        {
            "name": "payment-error-injection",
            "description": "Test payment service error handling",
            "hypothesis": "System should gracefully handle payment failures",
            "target": ("payment-service", TargetType.SERVICE),
            "faults": [(FaultType.ERROR, {"error_rate": 0.2, "duration_seconds": 30})],
            "probes": [("order_success_rate", SteadyStateType.METRIC, ">", 90)]
        },
        {
            "name": "database-stress-test",
            "description": "Test system under database resource stress",
            "hypothesis": "System should handle database resource constraints",
            "target": ("database", TargetType.SERVICE),
            "faults": [(FaultType.CPU_STRESS, {"cpu_percent": 80, "duration_seconds": 120})],
            "probes": [("query_latency", SteadyStateType.METRIC, "<", 100)]
        },
        {
            "name": "network-partition-test",
            "description": "Test resilience to network partitions",
            "hypothesis": "Services should recover from network partition",
            "target": ("order-service", TargetType.SERVICE),
            "faults": [(FaultType.NETWORK_PARTITION, {"duration_seconds": 30})],
            "probes": [("availability", SteadyStateType.METRIC, ">", 99)]
        },
        {
            "name": "pod-kill-test",
            "description": "Test auto-recovery when pods are killed",
            "hypothesis": "System should auto-recover from pod failures",
            "target": ("user-service", TargetType.POD),
            "faults": [(FaultType.KILL, {"duration_seconds": 10})],
            "probes": [("pod_count", SteadyStateType.METRIC, ">=", 3)]
        },
    ]
    
    for config in experiments_config:
        exp = manager.create_experiment(
            config["name"],
            config["description"],
            config["hypothesis"]
        )
        
        # Set target
        target_name, target_type = config["target"]
        manager.set_target(
            config["name"],
            target_type,
            name=target_name,
            service_name=target_name
        )
        
        # Add faults
        for fault_type, params in config["faults"]:
            manager.add_fault(config["name"], fault_type, **params)
            
        # Add probes
        for probe_name, probe_type, operator, value in config["probes"]:
            manager.add_steady_state_probe(
                config["name"],
                probe_name,
                probe_type,
                metric_name=probe_name,
                operator=operator,
                value=value
            )
            
        print(f"  🧪 {config['name']}")
        
    # Run experiments
    print("\n🚀 Running Experiments...")
    
    for exp_name in list(manager.experiments.keys()):
        result = await manager.run_experiment(exp_name)
        
        if result:
            status = "✅ PASSED" if result.success else "❌ FAILED"
            print(f"  {status} {exp_name}")
            
            if not result.success:
                print(f"    Reason: {result.failure_reason}")
                
    # Display experiments
    print("\n🧪 Experiment Results:")
    
    print("\n  ┌────────────────────────────┬─────────────┬────────────┬────────────┐")
    print("  │ Experiment                 │ Status      │ Pre-Check  │ Post-Check │")
    print("  ├────────────────────────────┼─────────────┼────────────┼────────────┤")
    
    for exp in manager.experiments.values():
        name = exp.name[:26].ljust(26)
        status = exp.status.value[:11].ljust(11)
        
        last_result = exp.results[-1] if exp.results else None
        pre = "✅" if last_result and last_result.pre_hypothesis_passed else "❌"
        post = "✅" if last_result and last_result.post_hypothesis_passed else "❌"
        
        print(f"  │ {name} │ {status} │ {pre:^10} │ {post:^10} │")
        
    print("  └────────────────────────────┴─────────────┴────────────┴────────────┘")
    
    # Display fault summary
    print("\n💥 Fault Injection Summary:")
    
    fault_counts = {}
    for exp in manager.experiments.values():
        for fault in exp.faults:
            fault_counts[fault.fault_type.value] = fault_counts.get(fault.fault_type.value, 0) + 1
            
    for fault_type, count in sorted(fault_counts.items()):
        bar = "█" * count
        print(f"  {fault_type:20s}: [{bar}] {count}")
        
    # Display resilience scores
    print("\n📊 Resilience Scores:")
    
    print("\n  ┌────────────────────┬──────────┬──────────┬──────────┬──────────┬──────────┐")
    print("  │ Service            │ Overall  │ Latency  │ Error    │ Resource │ Network  │")
    print("  ├────────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤")
    
    for score in manager.resilience_scores.values():
        service = score.service[:18].ljust(18)
        overall = f"{score.overall_score:.0f}%"[:8].center(8)
        latency = f"{score.latency_resilience:.0f}%"[:8].center(8)
        error = f"{score.error_resilience:.0f}%"[:8].center(8)
        resource = f"{score.resource_resilience:.0f}%"[:8].center(8)
        network = f"{score.network_resilience:.0f}%"[:8].center(8)
        
        print(f"  │ {service} │ {overall} │ {latency} │ {error} │ {resource} │ {network} │")
        
    print("  └────────────────────┴──────────┴──────────┴──────────┴──────────┴──────────┘")
    
    # Resilience report
    print("\n📋 Resilience Report:")
    
    report = manager.get_resilience_report()
    
    print(f"\n  Total Experiments: {report['total_experiments']}")
    print(f"  Completed: {report['completed']}")
    print(f"  Overall Resilience: {report['overall_resilience']:.1f}%")
    
    # Service-specific resilience
    print("\n  Service Resilience Details:")
    
    for service, data in report["services"].items():
        bar_len = int(data["overall"] / 10)
        bar = "█" * bar_len + "░" * (10 - bar_len)
        
        color = "🟢" if data["overall"] >= 80 else "🟡" if data["overall"] >= 50 else "🔴"
        
        print(f"\n  {color} {service}:")
        print(f"    Overall: [{bar}] {data['overall']:.0f}%")
        print(f"    Pass rate: {data['experiments_passed']}/{data['experiments_run']}")
        
    # Safety controls status
    print("\n🛡️ Safety Controls:")
    
    for control in manager.global_safety_controls:
        status = "🔴 Triggered" if control.triggered else "🟢 OK"
        print(f"  {control.name}: {control.metric_name} {control.operator} {control.threshold} - {status}")
        
    # Blast radius
    print("\n💥 Global Blast Radius:")
    
    if manager.global_blast_radius:
        br = manager.global_blast_radius
        print(f"  Max services: {br.max_services}")
        print(f"  Max pods: {br.max_pods}")
        print(f"  Max nodes: {br.max_nodes}")
        print(f"  Max percentage: {br.max_percentage}%")
        
    # Experiment observations
    print("\n📝 Key Observations:")
    
    for exp in manager.experiments.values():
        if exp.results:
            last_result = exp.results[-1]
            for obs in last_result.observations:
                print(f"  • {exp.name}: {obs}")
                
    # Statistics
    print("\n📊 Platform Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Total Experiments: {stats['total_experiments']}")
    print(f"  Currently Running: {stats['running']}")
    print(f"  Total Runs: {stats['total_runs']}")
    print(f"  Successful Runs: {stats['successful_runs']}")
    print(f"  Services Tested: {stats['services_tested']}")
    
    print("\n  Status Distribution:")
    for status, count in stats["status_counts"].items():
        if count > 0:
            print(f"    {status}: {count}")
            
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Chaos Engineering Dashboard                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Experiments:             {stats['total_experiments']:>12}                        │")
    print(f"│ Successful Runs:               {stats['successful_runs']:>12}                        │")
    print(f"│ Services Tested:               {stats['services_tested']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Overall Resilience:            {report['overall_resilience']:>11.1f}%                        │")
    print(f"│ Currently Running:             {stats['running']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Chaos Engineering Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
