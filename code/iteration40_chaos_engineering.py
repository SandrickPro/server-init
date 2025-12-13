#!/usr/bin/env python3
"""
Server Init - Iteration 40: Chaos Engineering & Resilience Testing
Хаос-инженерия и тестирование устойчивости

Функционал:
- Chaos Experiments - хаос-эксперименты
- Failure Injection - внедрение сбоев
- Blast Radius Control - контроль радиуса поражения
- Steady State Hypothesis - гипотеза стабильного состояния
- Game Days - игровые дни
- Resilience Scoring - оценка устойчивости
- Automated Rollback - автоматический откат
- Learning from Chaos - обучение на хаосе
"""

import json
import asyncio
import hashlib
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Tuple
from enum import Enum
from abc import ABC, abstractmethod
import random
from collections import defaultdict
import uuid


class ExperimentType(Enum):
    """Тип эксперимента"""
    NETWORK = "network"
    RESOURCE = "resource"
    STATE = "state"
    APPLICATION = "application"
    INFRASTRUCTURE = "infrastructure"


class FaultType(Enum):
    """Тип сбоя"""
    # Network
    LATENCY = "latency"
    PACKET_LOSS = "packet_loss"
    DNS_FAILURE = "dns_failure"
    NETWORK_PARTITION = "network_partition"
    BANDWIDTH_LIMIT = "bandwidth_limit"
    
    # Resource
    CPU_STRESS = "cpu_stress"
    MEMORY_STRESS = "memory_stress"
    DISK_FILL = "disk_fill"
    IO_STRESS = "io_stress"
    
    # State
    PROCESS_KILL = "process_kill"
    CONTAINER_KILL = "container_kill"
    POD_DELETE = "pod_delete"
    NODE_DRAIN = "node_drain"
    
    # Application
    EXCEPTION_INJECTION = "exception_injection"
    HTTP_ERROR = "http_error"
    TIMEOUT = "timeout"
    
    # Infrastructure
    AZ_FAILURE = "az_failure"
    REGION_FAILURE = "region_failure"


class ExperimentStatus(Enum):
    """Статус эксперимента"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class SeverityLevel(Enum):
    """Уровень серьёзности"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SteadyStateHypothesis:
    """Гипотеза стабильного состояния"""
    hypothesis_id: str
    name: str
    description: str
    
    # Проверки
    probes: List[Dict[str, Any]] = field(default_factory=list)
    
    # Пороги
    thresholds: Dict[str, Any] = field(default_factory=dict)
    
    # Результаты
    initial_state: Optional[Dict[str, Any]] = None
    final_state: Optional[Dict[str, Any]] = None
    hypothesis_met: Optional[bool] = None


@dataclass
class FaultInjection:
    """Внедрение сбоя"""
    fault_id: str
    fault_type: FaultType
    
    # Цель
    target_type: str = "service"  # service, container, pod, node, az
    target_selector: Dict[str, Any] = field(default_factory=dict)
    
    # Параметры
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Время
    duration_seconds: int = 60
    delay_seconds: int = 0
    
    # Процент affected
    percentage: float = 100.0
    
    # Статус
    status: str = "pending"
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None


@dataclass
class BlastRadius:
    """Радиус поражения"""
    services_affected: List[str] = field(default_factory=list)
    users_affected_percent: float = 0.0
    regions_affected: List[str] = field(default_factory=list)
    pods_affected: int = 0
    max_allowed_impact: float = 10.0  # max % affected


@dataclass
class ChaosExperiment:
    """Хаос-эксперимент"""
    experiment_id: str
    name: str
    description: str
    experiment_type: ExperimentType
    
    # Гипотеза
    hypothesis: SteadyStateHypothesis = field(default_factory=lambda: SteadyStateHypothesis(
        hypothesis_id="", name="", description=""
    ))
    
    # Сбои
    faults: List[FaultInjection] = field(default_factory=list)
    
    # Радиус поражения
    blast_radius: BlastRadius = field(default_factory=BlastRadius)
    
    # Безопасность
    safety_checks: List[Dict[str, Any]] = field(default_factory=list)
    abort_conditions: List[Dict[str, Any]] = field(default_factory=list)
    rollback_steps: List[Dict[str, Any]] = field(default_factory=list)
    
    # Окружение
    environment: str = "staging"
    
    # Статус
    status: ExperimentStatus = ExperimentStatus.DRAFT
    
    # Результаты
    results: Dict[str, Any] = field(default_factory=dict)
    findings: List[str] = field(default_factory=list)
    
    # Время
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Метаданные
    owner: str = ""
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class GameDay:
    """Игровой день"""
    game_day_id: str
    name: str
    description: str
    
    # Сценарий
    scenario: str = ""
    objectives: List[str] = field(default_factory=list)
    
    # Эксперименты
    experiments: List[str] = field(default_factory=list)
    
    # Участники
    participants: List[str] = field(default_factory=list)
    facilitator: str = ""
    
    # Расписание
    scheduled_date: Optional[datetime] = None
    duration_hours: int = 4
    
    # Статус
    status: str = "planned"
    
    # Результаты
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    findings: List[Dict[str, Any]] = field(default_factory=list)
    action_items: List[Dict[str, Any]] = field(default_factory=list)
    
    # Метрики
    mttr_actual: Optional[float] = None
    incidents_detected: int = 0
    
    # Метаданные
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ResilienceScore:
    """Оценка устойчивости"""
    service_id: str
    overall_score: float = 0.0
    
    # Компоненты оценки
    fault_tolerance: float = 0.0
    recovery_time: float = 0.0
    error_handling: float = 0.0
    circuit_breaker_effectiveness: float = 0.0
    retry_logic: float = 0.0
    graceful_degradation: float = 0.0
    
    # Детали
    experiments_run: int = 0
    experiments_passed: int = 0
    weaknesses: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Время
    evaluated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ChaosReport:
    """Отчёт о хаос-тестировании"""
    report_id: str
    experiment_id: str
    
    # Результаты
    hypothesis_validated: bool = False
    steady_state_maintained: bool = False
    
    # Метрики
    duration_seconds: float = 0.0
    faults_injected: int = 0
    services_impacted: List[str] = field(default_factory=list)
    
    # Наблюдения
    observations: List[Dict[str, Any]] = field(default_factory=list)
    anomalies_detected: List[Dict[str, Any]] = field(default_factory=list)
    
    # Уроки
    lessons_learned: List[str] = field(default_factory=list)
    improvements_identified: List[str] = field(default_factory=list)
    
    # Рекомендации
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Метаданные
    generated_at: datetime = field(default_factory=datetime.now)


class FaultInjector(ABC):
    """Базовый класс инжектора сбоев"""
    
    @abstractmethod
    async def inject(self, fault: FaultInjection) -> bool:
        """Внедрение сбоя"""
        pass
        
    @abstractmethod
    async def revert(self, fault: FaultInjection) -> bool:
        """Откат сбоя"""
        pass
        
    @abstractmethod
    async def check_status(self, fault: FaultInjection) -> str:
        """Проверка статуса"""
        pass


class NetworkFaultInjector(FaultInjector):
    """Инжектор сетевых сбоев"""
    
    async def inject(self, fault: FaultInjection) -> bool:
        """Внедрение сетевого сбоя"""
        params = fault.parameters
        
        if fault.fault_type == FaultType.LATENCY:
            latency_ms = params.get("latency_ms", 100)
            jitter_ms = params.get("jitter_ms", 10)
            # tc qdisc add dev eth0 root netem delay {latency_ms}ms {jitter_ms}ms
            print(f"  💉 Injecting latency: {latency_ms}ms (±{jitter_ms}ms)")
            
        elif fault.fault_type == FaultType.PACKET_LOSS:
            loss_percent = params.get("loss_percent", 5)
            # tc qdisc add dev eth0 root netem loss {loss_percent}%
            print(f"  💉 Injecting packet loss: {loss_percent}%")
            
        elif fault.fault_type == FaultType.NETWORK_PARTITION:
            target = params.get("target", "")
            # iptables -A OUTPUT -d {target} -j DROP
            print(f"  💉 Creating network partition to: {target}")
            
        elif fault.fault_type == FaultType.DNS_FAILURE:
            domains = params.get("domains", [])
            # Modify /etc/hosts or DNS server
            print(f"  💉 Injecting DNS failure for: {domains}")
            
        elif fault.fault_type == FaultType.BANDWIDTH_LIMIT:
            rate = params.get("rate", "1mbit")
            # tc qdisc add dev eth0 root tbf rate {rate}
            print(f"  💉 Limiting bandwidth to: {rate}")
            
        fault.status = "active"
        fault.started_at = datetime.now()
        return True
        
    async def revert(self, fault: FaultInjection) -> bool:
        """Откат сетевого сбоя"""
        # tc qdisc del dev eth0 root
        print(f"  🔄 Reverting network fault: {fault.fault_type.value}")
        fault.status = "reverted"
        fault.ended_at = datetime.now()
        return True
        
    async def check_status(self, fault: FaultInjection) -> str:
        """Проверка статуса"""
        return fault.status


class ResourceFaultInjector(FaultInjector):
    """Инжектор ресурсных сбоев"""
    
    async def inject(self, fault: FaultInjection) -> bool:
        """Внедрение ресурсного сбоя"""
        params = fault.parameters
        
        if fault.fault_type == FaultType.CPU_STRESS:
            cores = params.get("cores", 1)
            load_percent = params.get("load_percent", 80)
            # stress-ng --cpu {cores} --cpu-load {load_percent}
            print(f"  💉 Stressing CPU: {cores} cores at {load_percent}%")
            
        elif fault.fault_type == FaultType.MEMORY_STRESS:
            size_mb = params.get("size_mb", 512)
            # stress-ng --vm 1 --vm-bytes {size_mb}M
            print(f"  💉 Stressing memory: {size_mb}MB")
            
        elif fault.fault_type == FaultType.DISK_FILL:
            size_gb = params.get("size_gb", 10)
            path = params.get("path", "/tmp")
            # fallocate -l {size_gb}G {path}/chaos-fill
            print(f"  💉 Filling disk: {size_gb}GB at {path}")
            
        elif fault.fault_type == FaultType.IO_STRESS:
            iops = params.get("iops", 1000)
            # stress-ng --io {iops}
            print(f"  💉 Stressing I/O: {iops} IOPS")
            
        fault.status = "active"
        fault.started_at = datetime.now()
        return True
        
    async def revert(self, fault: FaultInjection) -> bool:
        """Откат ресурсного сбоя"""
        print(f"  🔄 Reverting resource fault: {fault.fault_type.value}")
        fault.status = "reverted"
        fault.ended_at = datetime.now()
        return True
        
    async def check_status(self, fault: FaultInjection) -> str:
        """Проверка статуса"""
        return fault.status


class StateFaultInjector(FaultInjector):
    """Инжектор сбоев состояния"""
    
    async def inject(self, fault: FaultInjection) -> bool:
        """Внедрение сбоя состояния"""
        params = fault.parameters
        selector = fault.target_selector
        
        if fault.fault_type == FaultType.PROCESS_KILL:
            signal = params.get("signal", "SIGKILL")
            process = selector.get("process", "")
            # kill -{signal} $(pgrep {process})
            print(f"  💉 Killing process: {process} with {signal}")
            
        elif fault.fault_type == FaultType.CONTAINER_KILL:
            container = selector.get("container", "")
            # docker kill {container}
            print(f"  💉 Killing container: {container}")
            
        elif fault.fault_type == FaultType.POD_DELETE:
            namespace = selector.get("namespace", "default")
            pod = selector.get("pod", "")
            # kubectl delete pod {pod} -n {namespace}
            print(f"  💉 Deleting pod: {namespace}/{pod}")
            
        elif fault.fault_type == FaultType.NODE_DRAIN:
            node = selector.get("node", "")
            # kubectl drain {node} --ignore-daemonsets
            print(f"  💉 Draining node: {node}")
            
        fault.status = "active"
        fault.started_at = datetime.now()
        return True
        
    async def revert(self, fault: FaultInjection) -> bool:
        """Откат сбоя состояния"""
        # Восстановление зависит от типа сбоя
        print(f"  🔄 Reverting state fault: {fault.fault_type.value}")
        fault.status = "reverted"
        fault.ended_at = datetime.now()
        return True
        
    async def check_status(self, fault: FaultInjection) -> str:
        """Проверка статуса"""
        return fault.status


class SteadyStateProbe:
    """Проба стабильного состояния"""
    
    def __init__(self):
        self.probes: Dict[str, Callable] = {}
        
    def register_probe(self, name: str, probe: Callable):
        """Регистрация пробы"""
        self.probes[name] = probe
        
    async def execute_probes(self, probes_config: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Выполнение проб"""
        results = {}
        
        for probe_config in probes_config:
            probe_name = probe_config.get("name", "")
            probe_type = probe_config.get("type", "")
            
            if probe_type == "http":
                result = await self._http_probe(probe_config)
            elif probe_type == "metric":
                result = await self._metric_probe(probe_config)
            elif probe_type == "process":
                result = await self._process_probe(probe_config)
            elif probe_name in self.probes:
                result = await self.probes[probe_name](probe_config)
            else:
                result = {"error": f"Unknown probe type: {probe_type}"}
                
            results[probe_name] = result
            
        return results
        
    async def _http_probe(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """HTTP проба"""
        url = config.get("url", "")
        expected_status = config.get("expected_status", 200)
        timeout = config.get("timeout", 5)
        
        # Симуляция HTTP запроса
        simulated_status = random.choice([200, 200, 200, 500])
        simulated_latency = random.uniform(10, 100)
        
        return {
            "url": url,
            "status_code": simulated_status,
            "latency_ms": simulated_latency,
            "success": simulated_status == expected_status
        }
        
    async def _metric_probe(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Метрическая проба"""
        metric = config.get("metric", "")
        threshold = config.get("threshold", 0)
        operator = config.get("operator", "<")
        
        # Симуляция метрики
        value = random.uniform(0, 100)
        
        if operator == "<":
            success = value < threshold
        elif operator == ">":
            success = value > threshold
        elif operator == "==":
            success = value == threshold
        else:
            success = True
            
        return {
            "metric": metric,
            "value": value,
            "threshold": threshold,
            "success": success
        }
        
    async def _process_probe(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Проба процесса"""
        process = config.get("process", "")
        
        # Симуляция проверки процесса
        running = random.choice([True, True, True, False])
        
        return {
            "process": process,
            "running": running,
            "success": running
        }


class BlastRadiusController:
    """Контроллер радиуса поражения"""
    
    def __init__(self):
        self.service_dependencies: Dict[str, List[str]] = {}
        self.traffic_distribution: Dict[str, float] = {}
        
    def set_dependencies(self, service: str, dependencies: List[str]):
        """Установка зависимостей"""
        self.service_dependencies[service] = dependencies
        
    def set_traffic(self, service: str, traffic_percent: float):
        """Установка трафика"""
        self.traffic_distribution[service] = traffic_percent
        
    def calculate_blast_radius(self, target_services: List[str], 
                                fault_percentage: float) -> BlastRadius:
        """Расчёт радиуса поражения"""
        affected_services = set(target_services)
        
        # Добавляем зависимые сервисы
        for service in target_services:
            for svc, deps in self.service_dependencies.items():
                if service in deps:
                    affected_services.add(svc)
                    
        # Расчёт affected users
        users_affected = 0.0
        for service in affected_services:
            traffic = self.traffic_distribution.get(service, 0)
            users_affected += traffic * (fault_percentage / 100)
            
        return BlastRadius(
            services_affected=list(affected_services),
            users_affected_percent=min(users_affected, 100.0),
            pods_affected=len(affected_services) * int(fault_percentage / 10)
        )
        
    def is_within_limits(self, blast_radius: BlastRadius) -> bool:
        """Проверка в пределах лимитов"""
        return blast_radius.users_affected_percent <= blast_radius.max_allowed_impact
        
    def get_safe_percentage(self, target_services: List[str],
                             max_user_impact: float) -> float:
        """Получение безопасного процента"""
        # Бинарный поиск безопасного процента
        low, high = 0.0, 100.0
        
        while high - low > 1.0:
            mid = (low + high) / 2
            blast_radius = self.calculate_blast_radius(target_services, mid)
            blast_radius.max_allowed_impact = max_user_impact
            
            if self.is_within_limits(blast_radius):
                low = mid
            else:
                high = mid
                
        return low


class SafetyController:
    """Контроллер безопасности"""
    
    def __init__(self):
        self.abort_handlers: List[Callable] = []
        self.safety_checks: List[Dict[str, Any]] = []
        self.is_aborted: bool = False
        
    def add_safety_check(self, check: Dict[str, Any]):
        """Добавление проверки безопасности"""
        self.safety_checks.append(check)
        
    def add_abort_handler(self, handler: Callable):
        """Добавление обработчика abort"""
        self.abort_handlers.append(handler)
        
    async def run_safety_checks(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Выполнение проверок безопасности"""
        failures = []
        
        for check in self.safety_checks:
            check_type = check.get("type", "")
            
            if check_type == "metric":
                metric = check.get("metric", "")
                threshold = check.get("threshold", 0)
                operator = check.get("operator", "<")
                
                # Симуляция получения метрики
                value = random.uniform(0, 100)
                
                if operator == "<" and value >= threshold:
                    failures.append(f"Safety check failed: {metric} = {value} >= {threshold}")
                elif operator == ">" and value <= threshold:
                    failures.append(f"Safety check failed: {metric} = {value} <= {threshold}")
                    
            elif check_type == "http":
                url = check.get("url", "")
                # Симуляция HTTP проверки
                status = random.choice([200, 200, 500])
                if status != 200:
                    failures.append(f"Safety check failed: {url} returned {status}")
                    
        return len(failures) == 0, failures
        
    async def abort_experiment(self, reason: str):
        """Аварийная остановка эксперимента"""
        self.is_aborted = True
        print(f"  ⚠️  ABORT: {reason}")
        
        for handler in self.abort_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(reason)
                else:
                    handler(reason)
            except Exception as e:
                print(f"  ❌ Abort handler failed: {e}")


class ChaosExperimentRunner:
    """Запускатор хаос-экспериментов"""
    
    def __init__(self):
        self.injectors: Dict[ExperimentType, FaultInjector] = {
            ExperimentType.NETWORK: NetworkFaultInjector(),
            ExperimentType.RESOURCE: ResourceFaultInjector(),
            ExperimentType.STATE: StateFaultInjector()
        }
        self.probe = SteadyStateProbe()
        self.blast_radius_controller = BlastRadiusController()
        self.safety_controller = SafetyController()
        
    async def run_experiment(self, experiment: ChaosExperiment) -> ChaosReport:
        """Запуск эксперимента"""
        report = ChaosReport(
            report_id=f"rpt_{uuid.uuid4().hex[:8]}",
            experiment_id=experiment.experiment_id
        )
        
        print(f"\n🧪 Running experiment: {experiment.name}")
        print(f"   Type: {experiment.experiment_type.value}")
        print(f"   Environment: {experiment.environment}")
        
        experiment.status = ExperimentStatus.RUNNING
        experiment.started_at = datetime.now()
        
        try:
            # 1. Проверка стабильного состояния (before)
            print("\n📊 Checking steady state (before)...")
            initial_state = await self.probe.execute_probes(experiment.hypothesis.probes)
            experiment.hypothesis.initial_state = initial_state
            
            all_probes_pass = all(
                p.get("success", False) for p in initial_state.values()
            )
            
            if not all_probes_pass:
                print("  ❌ Initial steady state check failed!")
                experiment.status = ExperimentStatus.FAILED
                report.hypothesis_validated = False
                return report
                
            print("  ✓ Steady state validated")
            
            # 2. Проверка blast radius
            print("\n🎯 Checking blast radius...")
            target_services = [
                f.target_selector.get("service", "")
                for f in experiment.faults
            ]
            
            blast_radius = self.blast_radius_controller.calculate_blast_radius(
                target_services,
                experiment.faults[0].percentage if experiment.faults else 100
            )
            
            experiment.blast_radius = blast_radius
            
            if not self.blast_radius_controller.is_within_limits(blast_radius):
                print(f"  ❌ Blast radius exceeds limits: {blast_radius.users_affected_percent}%")
                experiment.status = ExperimentStatus.FAILED
                return report
                
            print(f"  ✓ Blast radius OK: {blast_radius.users_affected_percent:.1f}% users")
            
            # 3. Внедрение сбоев
            print("\n💉 Injecting faults...")
            
            for fault in experiment.faults:
                injector = self._get_injector(fault.fault_type)
                if injector:
                    await injector.inject(fault)
                    report.faults_injected += 1
                    
            # 4. Ожидание и мониторинг
            print("\n⏳ Running fault injection...")
            
            duration = max(f.duration_seconds for f in experiment.faults) if experiment.faults else 60
            check_interval = 5  # seconds
            
            for elapsed in range(0, duration, check_interval):
                # Проверка безопасности
                safe, failures = await self.safety_controller.run_safety_checks({})
                
                if not safe:
                    print(f"\n  ⚠️  Safety check failed at {elapsed}s:")
                    for f in failures:
                        print(f"     - {f}")
                        
                    # Abort и rollback
                    await self._rollback(experiment)
                    experiment.status = ExperimentStatus.ROLLED_BACK
                    report.observations.append({
                        "time": elapsed,
                        "type": "abort",
                        "reason": failures
                    })
                    return report
                    
                # Симуляция прогресса
                progress = (elapsed / duration) * 100
                print(f"\r  Progress: {progress:.0f}%", end="", flush=True)
                await asyncio.sleep(0.1)  # Симуляция
                
            print("\r  Progress: 100%")
            
            # 5. Откат сбоев
            print("\n🔄 Reverting faults...")
            
            for fault in experiment.faults:
                injector = self._get_injector(fault.fault_type)
                if injector:
                    await injector.revert(fault)
                    
            # 6. Проверка стабильного состояния (after)
            print("\n📊 Checking steady state (after)...")
            await asyncio.sleep(0.5)  # Время на восстановление
            
            final_state = await self.probe.execute_probes(experiment.hypothesis.probes)
            experiment.hypothesis.final_state = final_state
            
            all_probes_pass = all(
                p.get("success", False) for p in final_state.values()
            )
            
            if all_probes_pass:
                print("  ✓ Steady state maintained!")
                report.steady_state_maintained = True
                report.hypothesis_validated = True
            else:
                print("  ❌ Steady state NOT maintained!")
                report.steady_state_maintained = False
                report.hypothesis_validated = False
                
            experiment.status = ExperimentStatus.COMPLETED
            experiment.completed_at = datetime.now()
            
            # Расчёт метрик
            report.duration_seconds = (
                experiment.completed_at - experiment.started_at
            ).total_seconds()
            report.services_impacted = blast_radius.services_affected
            
        except Exception as e:
            print(f"\n❌ Experiment failed: {e}")
            experiment.status = ExperimentStatus.FAILED
            await self._rollback(experiment)
            report.observations.append({
                "type": "error",
                "message": str(e)
            })
            
        return report
        
    def _get_injector(self, fault_type: FaultType) -> Optional[FaultInjector]:
        """Получение инжектора для типа сбоя"""
        if fault_type in [FaultType.LATENCY, FaultType.PACKET_LOSS, 
                          FaultType.DNS_FAILURE, FaultType.NETWORK_PARTITION,
                          FaultType.BANDWIDTH_LIMIT]:
            return self.injectors.get(ExperimentType.NETWORK)
        elif fault_type in [FaultType.CPU_STRESS, FaultType.MEMORY_STRESS,
                            FaultType.DISK_FILL, FaultType.IO_STRESS]:
            return self.injectors.get(ExperimentType.RESOURCE)
        elif fault_type in [FaultType.PROCESS_KILL, FaultType.CONTAINER_KILL,
                            FaultType.POD_DELETE, FaultType.NODE_DRAIN]:
            return self.injectors.get(ExperimentType.STATE)
        return None
        
    async def _rollback(self, experiment: ChaosExperiment):
        """Откат эксперимента"""
        print("\n🔄 Rolling back experiment...")
        
        for fault in experiment.faults:
            injector = self._get_injector(fault.fault_type)
            if injector:
                try:
                    await injector.revert(fault)
                except Exception as e:
                    print(f"  ❌ Rollback failed for {fault.fault_id}: {e}")


class ResilienceScorer:
    """Оценщик устойчивости"""
    
    def __init__(self):
        self.experiment_results: Dict[str, List[ChaosReport]] = defaultdict(list)
        
    def add_experiment_result(self, service_id: str, report: ChaosReport):
        """Добавление результата эксперимента"""
        self.experiment_results[service_id].append(report)
        
    def calculate_score(self, service_id: str) -> ResilienceScore:
        """Расчёт оценки устойчивости"""
        reports = self.experiment_results.get(service_id, [])
        
        if not reports:
            return ResilienceScore(service_id=service_id)
            
        score = ResilienceScore(service_id=service_id)
        score.experiments_run = len(reports)
        score.experiments_passed = len([r for r in reports if r.hypothesis_validated])
        
        # Расчёт компонентов
        pass_rate = score.experiments_passed / score.experiments_run if score.experiments_run > 0 else 0
        
        score.fault_tolerance = pass_rate * 100
        score.recovery_time = self._calculate_recovery_score(reports)
        score.error_handling = random.uniform(60, 95)  # Симуляция
        score.circuit_breaker_effectiveness = random.uniform(70, 100)
        score.retry_logic = random.uniform(65, 95)
        score.graceful_degradation = random.uniform(50, 90)
        
        # Общая оценка
        score.overall_score = (
            score.fault_tolerance * 0.25 +
            score.recovery_time * 0.20 +
            score.error_handling * 0.15 +
            score.circuit_breaker_effectiveness * 0.15 +
            score.retry_logic * 0.10 +
            score.graceful_degradation * 0.15
        )
        
        # Анализ слабостей и сильных сторон
        if score.fault_tolerance < 70:
            score.weaknesses.append("Low fault tolerance - service fails under stress")
        if score.recovery_time < 70:
            score.weaknesses.append("Slow recovery time")
        if score.graceful_degradation < 60:
            score.weaknesses.append("Poor graceful degradation")
            
        if score.fault_tolerance >= 90:
            score.strengths.append("Excellent fault tolerance")
        if score.circuit_breaker_effectiveness >= 90:
            score.strengths.append("Effective circuit breakers")
        if score.error_handling >= 90:
            score.strengths.append("Robust error handling")
            
        # Рекомендации
        if score.overall_score < 70:
            score.recommendations.append("Run more chaos experiments to identify weaknesses")
            score.recommendations.append("Implement circuit breakers")
            score.recommendations.append("Add retry logic with exponential backoff")
        elif score.overall_score < 85:
            score.recommendations.append("Focus on improving graceful degradation")
            score.recommendations.append("Reduce recovery time")
            
        return score
        
    def _calculate_recovery_score(self, reports: List[ChaosReport]) -> float:
        """Расчёт оценки восстановления"""
        recovery_times = []
        
        for report in reports:
            if report.steady_state_maintained:
                recovery_times.append(report.duration_seconds)
                
        if not recovery_times:
            return 50.0
            
        avg_recovery = sum(recovery_times) / len(recovery_times)
        
        # Нормализация (1 минута = 100%, 10 минут = 0%)
        score = max(0, 100 - (avg_recovery / 6))
        return score


class GameDayManager:
    """Менеджер игровых дней"""
    
    def __init__(self, experiment_runner: ChaosExperimentRunner):
        self.experiment_runner = experiment_runner
        self.game_days: Dict[str, GameDay] = {}
        self.experiments: Dict[str, ChaosExperiment] = {}
        
    def create_game_day(self, game_day: GameDay) -> str:
        """Создание игрового дня"""
        self.game_days[game_day.game_day_id] = game_day
        return game_day.game_day_id
        
    def add_experiment_to_game_day(self, game_day_id: str, 
                                    experiment: ChaosExperiment) -> bool:
        """Добавление эксперимента"""
        game_day = self.game_days.get(game_day_id)
        if not game_day:
            return False
            
        self.experiments[experiment.experiment_id] = experiment
        game_day.experiments.append(experiment.experiment_id)
        return True
        
    async def run_game_day(self, game_day_id: str) -> Dict[str, Any]:
        """Запуск игрового дня"""
        game_day = self.game_days.get(game_day_id)
        if not game_day:
            return {"error": "Game day not found"}
            
        print(f"\n🎮 Starting Game Day: {game_day.name}")
        print(f"   Scenario: {game_day.scenario}")
        print(f"   Participants: {len(game_day.participants)}")
        
        game_day.status = "running"
        results = []
        start_time = datetime.now()
        
        for exp_id in game_day.experiments:
            experiment = self.experiments.get(exp_id)
            if experiment:
                game_day.timeline.append({
                    "time": datetime.now().isoformat(),
                    "event": f"Started experiment: {experiment.name}"
                })
                
                report = await self.experiment_runner.run_experiment(experiment)
                results.append(report)
                
                game_day.timeline.append({
                    "time": datetime.now().isoformat(),
                    "event": f"Completed experiment: {experiment.name}",
                    "result": "passed" if report.hypothesis_validated else "failed"
                })
                
        # Расчёт MTTR
        end_time = datetime.now()
        game_day.mttr_actual = (end_time - start_time).total_seconds() / 60
        
        game_day.status = "completed"
        
        return {
            "game_day_id": game_day_id,
            "status": "completed",
            "experiments_run": len(results),
            "experiments_passed": len([r for r in results if r.hypothesis_validated]),
            "mttr_minutes": game_day.mttr_actual,
            "timeline": game_day.timeline
        }


class ChaosLearningEngine:
    """Движок обучения на хаосе"""
    
    def __init__(self):
        self.lessons: List[Dict[str, Any]] = []
        self.patterns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
    def analyze_report(self, report: ChaosReport, 
                       experiment: ChaosExperiment) -> Dict[str, Any]:
        """Анализ отчёта"""
        analysis = {
            "report_id": report.report_id,
            "success": report.hypothesis_validated,
            "insights": [],
            "patterns_detected": [],
            "recommendations": []
        }
        
        # Анализ паттернов
        if not report.hypothesis_validated:
            analysis["insights"].append(
                f"Service failed to maintain steady state after {experiment.experiment_type.value} fault"
            )
            
            # Определение паттерна
            for fault in experiment.faults:
                pattern = {
                    "fault_type": fault.fault_type.value,
                    "failure_mode": "steady_state_lost",
                    "services": experiment.blast_radius.services_affected
                }
                self.patterns[fault.fault_type.value].append(pattern)
                analysis["patterns_detected"].append(pattern)
                
        # Рекомендации на основе паттернов
        for fault in experiment.faults:
            if fault.fault_type == FaultType.LATENCY:
                analysis["recommendations"].append(
                    "Implement timeout and retry policies"
                )
            elif fault.fault_type == FaultType.NETWORK_PARTITION:
                analysis["recommendations"].append(
                    "Add circuit breakers for inter-service communication"
                )
            elif fault.fault_type in [FaultType.CPU_STRESS, FaultType.MEMORY_STRESS]:
                analysis["recommendations"].append(
                    "Configure resource limits and auto-scaling"
                )
                
        # Сохранение урока
        lesson = {
            "experiment_id": experiment.experiment_id,
            "experiment_type": experiment.experiment_type.value,
            "success": report.hypothesis_validated,
            "insights": analysis["insights"],
            "recommendations": analysis["recommendations"],
            "timestamp": datetime.now().isoformat()
        }
        self.lessons.append(lesson)
        
        return analysis
        
    def get_recommendations_for_service(self, service_id: str) -> List[str]:
        """Получение рекомендаций для сервиса"""
        recommendations = set()
        
        for lesson in self.lessons:
            if not lesson["success"]:
                recommendations.update(lesson["recommendations"])
                
        return list(recommendations)
        
    def generate_improvement_report(self) -> Dict[str, Any]:
        """Генерация отчёта об улучшениях"""
        total_experiments = len(self.lessons)
        successful = len([l for l in self.lessons if l["success"]])
        
        # Анализ частых паттернов сбоев
        failure_patterns = defaultdict(int)
        for fault_type, patterns in self.patterns.items():
            failure_patterns[fault_type] = len(patterns)
            
        return {
            "summary": {
                "total_experiments": total_experiments,
                "successful": successful,
                "success_rate": (successful / total_experiments * 100) if total_experiments > 0 else 0
            },
            "top_failure_patterns": dict(
                sorted(failure_patterns.items(), key=lambda x: x[1], reverse=True)[:5]
            ),
            "overall_recommendations": self.get_recommendations_for_service("*"),
            "generated_at": datetime.now().isoformat()
        }


class ChaosEngineeringPlatform:
    """Платформа хаос-инженерии"""
    
    def __init__(self):
        self.runner = ChaosExperimentRunner()
        self.scorer = ResilienceScorer()
        self.game_day_manager = GameDayManager(self.runner)
        self.learning_engine = ChaosLearningEngine()
        self.experiments: Dict[str, ChaosExperiment] = {}
        
    def create_experiment(self, experiment: ChaosExperiment) -> str:
        """Создание эксперимента"""
        self.experiments[experiment.experiment_id] = experiment
        return experiment.experiment_id
        
    async def run_experiment(self, experiment_id: str) -> ChaosReport:
        """Запуск эксперимента"""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            raise ValueError(f"Experiment not found: {experiment_id}")
            
        report = await self.runner.run_experiment(experiment)
        
        # Добавление в scorer
        for service in experiment.blast_radius.services_affected:
            self.scorer.add_experiment_result(service, report)
            
        # Анализ для обучения
        analysis = self.learning_engine.analyze_report(report, experiment)
        report.lessons_learned = analysis.get("insights", [])
        report.recommendations = analysis.get("recommendations", [])
        
        return report
        
    def get_resilience_score(self, service_id: str) -> ResilienceScore:
        """Получение оценки устойчивости"""
        return self.scorer.calculate_score(service_id)
        
    def get_platform_dashboard(self) -> Dict[str, Any]:
        """Дашборд платформы"""
        return {
            "experiments": {
                "total": len(self.experiments),
                "by_status": {
                    status.value: len([
                        e for e in self.experiments.values()
                        if e.status == status
                    ])
                    for status in ExperimentStatus
                }
            },
            "game_days": {
                "total": len(self.game_day_manager.game_days),
                "planned": len([
                    g for g in self.game_day_manager.game_days.values()
                    if g.status == "planned"
                ])
            },
            "learning": self.learning_engine.generate_improvement_report()
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 40: Chaos Engineering")
    print("=" * 60)
    
    async def demo():
        platform = ChaosEngineeringPlatform()
        
        # Настройка blast radius controller
        platform.runner.blast_radius_controller.set_dependencies("api-gateway", [])
        platform.runner.blast_radius_controller.set_dependencies("user-service", ["api-gateway"])
        platform.runner.blast_radius_controller.set_dependencies("order-service", ["api-gateway", "user-service"])
        
        platform.runner.blast_radius_controller.set_traffic("api-gateway", 100)
        platform.runner.blast_radius_controller.set_traffic("user-service", 60)
        platform.runner.blast_radius_controller.set_traffic("order-service", 40)
        
        # Создание эксперимента: Latency Injection
        experiment1 = ChaosExperiment(
            experiment_id="exp_latency_001",
            name="API Gateway Latency Test",
            description="Test system behavior with increased API latency",
            experiment_type=ExperimentType.NETWORK,
            environment="staging",
            hypothesis=SteadyStateHypothesis(
                hypothesis_id="hyp_001",
                name="System maintains 95% availability",
                description="P99 latency should stay below 500ms",
                probes=[
                    {"name": "api_health", "type": "http", "url": "http://api-gateway/health", "expected_status": 200},
                    {"name": "latency_p99", "type": "metric", "metric": "http_request_duration_p99", "threshold": 500, "operator": "<"}
                ]
            ),
            faults=[
                FaultInjection(
                    fault_id="fault_001",
                    fault_type=FaultType.LATENCY,
                    target_selector={"service": "api-gateway"},
                    parameters={"latency_ms": 200, "jitter_ms": 50},
                    duration_seconds=30,
                    percentage=50
                )
            ],
            owner="chaos-team"
        )
        
        platform.create_experiment(experiment1)
        print(f"✓ Created experiment: {experiment1.name}")
        
        # Запуск эксперимента
        report1 = await platform.run_experiment("exp_latency_001")
        
        print(f"\n📋 Experiment Report:")
        print(f"   Hypothesis Validated: {report1.hypothesis_validated}")
        print(f"   Steady State Maintained: {report1.steady_state_maintained}")
        print(f"   Duration: {report1.duration_seconds:.1f}s")
        print(f"   Services Impacted: {report1.services_impacted}")
        
        # Создание эксперимента: Pod Delete
        experiment2 = ChaosExperiment(
            experiment_id="exp_pod_delete_001",
            name="User Service Pod Kill",
            description="Test recovery when user-service pods are killed",
            experiment_type=ExperimentType.STATE,
            environment="staging",
            hypothesis=SteadyStateHypothesis(
                hypothesis_id="hyp_002",
                name="Service recovers within 60 seconds",
                description="User service should auto-recover",
                probes=[
                    {"name": "user_svc_health", "type": "http", "url": "http://user-service/health", "expected_status": 200},
                    {"name": "user_svc_process", "type": "process", "process": "user-service"}
                ]
            ),
            faults=[
                FaultInjection(
                    fault_id="fault_002",
                    fault_type=FaultType.POD_DELETE,
                    target_selector={"service": "user-service", "namespace": "default", "pod": "user-service-pod-1"},
                    duration_seconds=60,
                    percentage=33  # Kill 1 of 3 pods
                )
            ],
            owner="chaos-team"
        )
        
        platform.create_experiment(experiment2)
        report2 = await platform.run_experiment("exp_pod_delete_001")
        
        print(f"\n📋 Second Experiment Report:")
        print(f"   Hypothesis Validated: {report2.hypothesis_validated}")
        
        # Расчёт Resilience Score
        score = platform.get_resilience_score("user-service")
        
        print(f"\n🏆 Resilience Score for user-service:")
        print(f"   Overall: {score.overall_score:.1f}/100")
        print(f"   Fault Tolerance: {score.fault_tolerance:.1f}")
        print(f"   Recovery Time: {score.recovery_time:.1f}")
        print(f"   Error Handling: {score.error_handling:.1f}")
        print(f"   Experiments: {score.experiments_run} run, {score.experiments_passed} passed")
        
        if score.weaknesses:
            print(f"   Weaknesses: {score.weaknesses}")
        if score.recommendations:
            print(f"   Recommendations: {score.recommendations}")
            
        # Game Day
        game_day = GameDay(
            game_day_id="gd_001",
            name="Q4 Resilience Game Day",
            description="Testing overall system resilience",
            scenario="Region failure simulation",
            objectives=[
                "Validate failover to backup region",
                "Test recovery procedures",
                "Measure MTTR"
            ],
            participants=["sre-team", "dev-team", "ops-team"],
            facilitator="chaos-lead"
        )
        
        platform.game_day_manager.create_game_day(game_day)
        print(f"\n🎮 Created Game Day: {game_day.name}")
        
        # Дашборд платформы
        dashboard = platform.get_platform_dashboard()
        print(f"\n📊 Platform Dashboard:")
        print(f"   Total Experiments: {dashboard['experiments']['total']}")
        print(f"   Game Days: {dashboard['game_days']['total']}")
        print(f"   Learning - Success Rate: {dashboard['learning']['summary']['success_rate']:.0f}%")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Chaos Engineering Platform initialized successfully!")
    print("=" * 60)
