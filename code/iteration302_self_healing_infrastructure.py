#!/usr/bin/env python3
"""
Server Init - Iteration 302: Self-Healing Infrastructure Platform
Платформа самовосстанавливающейся инфраструктуры

Функционал:
- Anomaly Detection - обнаружение аномалий
- Auto-Remediation - автоматическое восстановление
- Health Monitoring - мониторинг здоровья
- Policy Engine - движок политик
- Recovery Actions - действия восстановления
- Predictive Analysis - предиктивный анализ
- Escalation Management - управление эскалациями
- Learning System - система обучения
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid


class HealthStatus(Enum):
    """Статус здоровья"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class AnomalyType(Enum):
    """Тип аномалии"""
    CPU_SPIKE = "cpu_spike"
    MEMORY_LEAK = "memory_leak"
    DISK_FULL = "disk_full"
    NETWORK_LATENCY = "network_latency"
    ERROR_RATE = "error_rate"
    CONNECTION_POOL = "connection_pool"
    PROCESS_CRASH = "process_crash"
    CERTIFICATE_EXPIRY = "certificate_expiry"


class RemediationAction(Enum):
    """Действие восстановления"""
    RESTART_SERVICE = "restart_service"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    CLEAR_CACHE = "clear_cache"
    ROTATE_LOGS = "rotate_logs"
    FAILOVER = "failover"
    ROLLBACK = "rollback"
    ALERT_ONLY = "alert_only"


class PolicyTrigger(Enum):
    """Триггер политики"""
    THRESHOLD = "threshold"
    PATTERN = "pattern"
    SCHEDULE = "schedule"
    DEPENDENCY = "dependency"


@dataclass
class HealthCheck:
    """Проверка здоровья"""
    check_id: str
    resource_id: str
    
    # Type
    check_type: str = "http"  # http, tcp, exec, dns
    
    # Target
    endpoint: str = ""
    
    # Configuration
    interval: int = 30  # seconds
    timeout: int = 10
    
    # Thresholds
    healthy_threshold: int = 2
    unhealthy_threshold: int = 3
    
    # State
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_check: Optional[datetime] = None
    last_status: HealthStatus = HealthStatus.UNKNOWN


@dataclass
class Anomaly:
    """Аномалия"""
    anomaly_id: str
    resource_id: str
    
    # Type
    anomaly_type: AnomalyType = AnomalyType.CPU_SPIKE
    
    # Details
    description: str = ""
    severity: float = 0.0  # 0-1
    
    # Metrics
    current_value: float = 0.0
    expected_value: float = 0.0
    deviation: float = 0.0
    
    # Status
    resolved: bool = False
    auto_resolved: bool = False
    
    # Timestamps
    detected_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


@dataclass
class RemediationPolicy:
    """Политика восстановления"""
    policy_id: str
    name: str
    
    # Trigger
    trigger_type: PolicyTrigger = PolicyTrigger.THRESHOLD
    anomaly_type: AnomalyType = AnomalyType.CPU_SPIKE
    
    # Conditions
    threshold: float = 0.0
    duration: int = 0  # seconds
    
    # Actions
    actions: List[RemediationAction] = field(default_factory=list)
    
    # Limits
    max_executions_per_hour: int = 3
    cooldown_seconds: int = 300
    
    # Status
    enabled: bool = True
    execution_count: int = 0
    last_executed: Optional[datetime] = None


@dataclass
class Remediation:
    """Выполнение восстановления"""
    remediation_id: str
    anomaly_id: str
    policy_id: str
    
    # Actions
    actions: List[RemediationAction] = field(default_factory=list)
    
    # Status
    status: str = "pending"  # pending, executing, completed, failed
    
    # Results
    actions_executed: List[str] = field(default_factory=list)
    success: bool = False
    
    # Timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class Resource:
    """Ресурс"""
    resource_id: str
    name: str
    resource_type: str
    
    # Health
    health_status: HealthStatus = HealthStatus.UNKNOWN
    health_score: float = 100.0
    
    # Health checks
    health_checks: List[str] = field(default_factory=list)
    
    # Metrics
    metrics: Dict[str, float] = field(default_factory=dict)
    
    # History
    anomaly_history: List[str] = field(default_factory=list)
    remediation_history: List[str] = field(default_factory=list)
    
    # State
    last_incident: Optional[datetime] = None
    mttr: float = 0.0  # Mean Time To Recovery


@dataclass
class LearningPattern:
    """Паттерн обучения"""
    pattern_id: str
    
    # Pattern
    anomaly_type: AnomalyType
    successful_action: RemediationAction
    
    # Statistics
    occurrences: int = 0
    success_rate: float = 0.0
    avg_recovery_time: float = 0.0


class SelfHealingManager:
    """Менеджер Self-Healing Infrastructure"""
    
    def __init__(self):
        self.resources: Dict[str, Resource] = {}
        self.health_checks: Dict[str, HealthCheck] = {}
        self.anomalies: Dict[str, Anomaly] = {}
        self.policies: Dict[str, RemediationPolicy] = {}
        self.remediations: Dict[str, Remediation] = {}
        self.patterns: Dict[str, LearningPattern] = {}
        
        # Stats
        self.total_anomalies: int = 0
        self.auto_resolved: int = 0
        self.manual_resolved: int = 0
        
    async def register_resource(self, name: str,
                               resource_type: str) -> Resource:
        """Регистрация ресурса"""
        resource = Resource(
            resource_id=f"res_{uuid.uuid4().hex[:8]}",
            name=name,
            resource_type=resource_type
        )
        
        self.resources[resource.resource_id] = resource
        return resource
        
    async def add_health_check(self, resource_id: str,
                              check_type: str = "http",
                              endpoint: str = "",
                              interval: int = 30) -> Optional[HealthCheck]:
        """Добавление проверки здоровья"""
        resource = self.resources.get(resource_id)
        if not resource:
            return None
            
        check = HealthCheck(
            check_id=f"hc_{uuid.uuid4().hex[:8]}",
            resource_id=resource_id,
            check_type=check_type,
            endpoint=endpoint,
            interval=interval
        )
        
        self.health_checks[check.check_id] = check
        resource.health_checks.append(check.check_id)
        
        return check
        
    async def run_health_check(self, check_id: str) -> HealthStatus:
        """Выполнение проверки здоровья"""
        check = self.health_checks.get(check_id)
        if not check:
            return HealthStatus.UNKNOWN
            
        # Simulate health check (90% healthy)
        is_healthy = random.random() > 0.1
        
        check.last_check = datetime.now()
        
        if is_healthy:
            check.consecutive_successes += 1
            check.consecutive_failures = 0
            
            if check.consecutive_successes >= check.healthy_threshold:
                check.last_status = HealthStatus.HEALTHY
        else:
            check.consecutive_failures += 1
            check.consecutive_successes = 0
            
            if check.consecutive_failures >= check.unhealthy_threshold:
                check.last_status = HealthStatus.UNHEALTHY
            elif check.consecutive_failures >= 1:
                check.last_status = HealthStatus.DEGRADED
                
        return check.last_status
        
    async def update_resource_health(self, resource_id: str) -> HealthStatus:
        """Обновление здоровья ресурса"""
        resource = self.resources.get(resource_id)
        if not resource:
            return HealthStatus.UNKNOWN
            
        statuses = []
        for check_id in resource.health_checks:
            check = self.health_checks.get(check_id)
            if check:
                statuses.append(check.last_status)
                
        if not statuses:
            resource.health_status = HealthStatus.UNKNOWN
        elif all(s == HealthStatus.HEALTHY for s in statuses):
            resource.health_status = HealthStatus.HEALTHY
            resource.health_score = 100.0
        elif any(s == HealthStatus.CRITICAL for s in statuses):
            resource.health_status = HealthStatus.CRITICAL
            resource.health_score = 0.0
        elif any(s == HealthStatus.UNHEALTHY for s in statuses):
            resource.health_status = HealthStatus.UNHEALTHY
            resource.health_score = 30.0
        elif any(s == HealthStatus.DEGRADED for s in statuses):
            resource.health_status = HealthStatus.DEGRADED
            resource.health_score = 70.0
        else:
            resource.health_status = HealthStatus.UNKNOWN
            resource.health_score = 50.0
            
        return resource.health_status
        
    async def detect_anomaly(self, resource_id: str,
                            anomaly_type: AnomalyType,
                            current_value: float,
                            expected_value: float) -> Optional[Anomaly]:
        """Обнаружение аномалии"""
        resource = self.resources.get(resource_id)
        if not resource:
            return None
            
        deviation = abs(current_value - expected_value) / max(expected_value, 0.001)
        severity = min(deviation, 1.0)
        
        anomaly = Anomaly(
            anomaly_id=f"anom_{uuid.uuid4().hex[:8]}",
            resource_id=resource_id,
            anomaly_type=anomaly_type,
            description=f"{anomaly_type.value} detected on {resource.name}",
            severity=severity,
            current_value=current_value,
            expected_value=expected_value,
            deviation=deviation
        )
        
        self.anomalies[anomaly.anomaly_id] = anomaly
        resource.anomaly_history.append(anomaly.anomaly_id)
        resource.last_incident = datetime.now()
        self.total_anomalies += 1
        
        return anomaly
        
    async def create_policy(self, name: str,
                           anomaly_type: AnomalyType,
                           actions: List[RemediationAction],
                           threshold: float = 0.8,
                           cooldown: int = 300) -> RemediationPolicy:
        """Создание политики восстановления"""
        policy = RemediationPolicy(
            policy_id=f"pol_{uuid.uuid4().hex[:8]}",
            name=name,
            anomaly_type=anomaly_type,
            threshold=threshold,
            actions=actions,
            cooldown_seconds=cooldown
        )
        
        self.policies[policy.policy_id] = policy
        return policy
        
    async def find_matching_policy(self, anomaly: Anomaly) -> Optional[RemediationPolicy]:
        """Поиск подходящей политики"""
        for policy in self.policies.values():
            if not policy.enabled:
                continue
                
            if policy.anomaly_type != anomaly.anomaly_type:
                continue
                
            if anomaly.severity < policy.threshold:
                continue
                
            # Check cooldown
            if policy.last_executed:
                elapsed = (datetime.now() - policy.last_executed).total_seconds()
                if elapsed < policy.cooldown_seconds:
                    continue
                    
            return policy
            
        return None
        
    async def execute_remediation(self, anomaly_id: str,
                                 policy_id: str) -> Optional[Remediation]:
        """Выполнение восстановления"""
        anomaly = self.anomalies.get(anomaly_id)
        policy = self.policies.get(policy_id)
        
        if not anomaly or not policy:
            return None
            
        remediation = Remediation(
            remediation_id=f"rem_{uuid.uuid4().hex[:8]}",
            anomaly_id=anomaly_id,
            policy_id=policy_id,
            actions=policy.actions,
            started_at=datetime.now()
        )
        
        remediation.status = "executing"
        
        # Execute actions
        for action in policy.actions:
            # Simulate action execution
            await asyncio.sleep(0.01)
            
            success = random.random() > 0.1  # 90% success rate
            
            if success:
                remediation.actions_executed.append(f"{action.value}: success")
            else:
                remediation.actions_executed.append(f"{action.value}: failed")
                break
                
        # Determine overall success
        remediation.success = all("success" in a for a in remediation.actions_executed)
        remediation.status = "completed" if remediation.success else "failed"
        remediation.completed_at = datetime.now()
        
        # Update anomaly
        if remediation.success:
            anomaly.resolved = True
            anomaly.auto_resolved = True
            anomaly.resolved_at = datetime.now()
            self.auto_resolved += 1
            
        # Update policy
        policy.execution_count += 1
        policy.last_executed = datetime.now()
        
        # Update resource
        resource = self.resources.get(anomaly.resource_id)
        if resource:
            resource.remediation_history.append(remediation.remediation_id)
            
            if anomaly.resolved and anomaly.resolved_at:
                recovery_time = (anomaly.resolved_at - anomaly.detected_at).total_seconds()
                # Update MTTR
                if resource.mttr == 0:
                    resource.mttr = recovery_time
                else:
                    resource.mttr = (resource.mttr + recovery_time) / 2
                    
        # Learn from this remediation
        await self._learn_from_remediation(anomaly, policy.actions[0] if policy.actions else None, remediation.success)
        
        self.remediations[remediation.remediation_id] = remediation
        return remediation
        
    async def _learn_from_remediation(self, anomaly: Anomaly,
                                     action: Optional[RemediationAction],
                                     success: bool):
        """Обучение на основе восстановления"""
        if not action:
            return
            
        pattern_key = f"{anomaly.anomaly_type.value}_{action.value}"
        
        if pattern_key not in self.patterns:
            pattern = LearningPattern(
                pattern_id=f"pat_{uuid.uuid4().hex[:8]}",
                anomaly_type=anomaly.anomaly_type,
                successful_action=action
            )
            self.patterns[pattern_key] = pattern
        else:
            pattern = self.patterns[pattern_key]
            
        pattern.occurrences += 1
        
        if success:
            # Update success rate
            pattern.success_rate = ((pattern.success_rate * (pattern.occurrences - 1)) + 1) / pattern.occurrences
        else:
            pattern.success_rate = (pattern.success_rate * (pattern.occurrences - 1)) / pattern.occurrences
            
    async def auto_heal(self, anomaly_id: str) -> Optional[Remediation]:
        """Автоматическое восстановление"""
        anomaly = self.anomalies.get(anomaly_id)
        if not anomaly or anomaly.resolved:
            return None
            
        # Find matching policy
        policy = await self.find_matching_policy(anomaly)
        
        if not policy:
            return None
            
        # Execute remediation
        return await self.execute_remediation(anomaly_id, policy.policy_id)
        
    async def predict_issues(self, resource_id: str) -> List[Dict[str, Any]]:
        """Предсказание проблем"""
        resource = self.resources.get(resource_id)
        if not resource:
            return []
            
        predictions = []
        
        # Analyze history
        recent_anomalies = [
            self.anomalies.get(a_id)
            for a_id in resource.anomaly_history[-20:]
            if self.anomalies.get(a_id)
        ]
        
        # Count anomaly types
        type_counts: Dict[AnomalyType, int] = {}
        for anomaly in recent_anomalies:
            type_counts[anomaly.anomaly_type] = type_counts.get(anomaly.anomaly_type, 0) + 1
            
        # Generate predictions
        for anomaly_type, count in type_counts.items():
            if count >= 3:
                probability = min(count / 10, 0.9)
                predictions.append({
                    "anomaly_type": anomaly_type.value,
                    "probability": probability,
                    "recommendation": f"Consider proactive scaling for {anomaly_type.value}"
                })
                
        return predictions
        
    def get_resource_health_report(self, resource_id: str) -> Dict[str, Any]:
        """Отчёт о здоровье ресурса"""
        resource = self.resources.get(resource_id)
        if not resource:
            return {}
            
        recent_anomalies = len([
            a_id for a_id in resource.anomaly_history[-50:]
            if self.anomalies.get(a_id) and 
            (datetime.now() - self.anomalies[a_id].detected_at).total_seconds() < 86400
        ])
        
        resolved_anomalies = sum(
            1 for a_id in resource.anomaly_history
            if self.anomalies.get(a_id) and self.anomalies[a_id].resolved
        )
        
        return {
            "resource_id": resource_id,
            "name": resource.name,
            "type": resource.resource_type,
            "health_status": resource.health_status.value,
            "health_score": resource.health_score,
            "total_anomalies": len(resource.anomaly_history),
            "resolved_anomalies": resolved_anomalies,
            "recent_anomalies_24h": recent_anomalies,
            "mttr_seconds": resource.mttr,
            "health_checks": len(resource.health_checks)
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        healthy = sum(1 for r in self.resources.values() if r.health_status == HealthStatus.HEALTHY)
        degraded = sum(1 for r in self.resources.values() if r.health_status == HealthStatus.DEGRADED)
        unhealthy = sum(1 for r in self.resources.values() if r.health_status == HealthStatus.UNHEALTHY)
        
        active_anomalies = sum(1 for a in self.anomalies.values() if not a.resolved)
        
        successful_remediations = sum(1 for r in self.remediations.values() if r.success)
        
        avg_mttr = sum(r.mttr for r in self.resources.values() if r.mttr > 0)
        mttr_count = sum(1 for r in self.resources.values() if r.mttr > 0)
        avg_mttr = avg_mttr / mttr_count if mttr_count > 0 else 0
        
        return {
            "total_resources": len(self.resources),
            "healthy_resources": healthy,
            "degraded_resources": degraded,
            "unhealthy_resources": unhealthy,
            "total_health_checks": len(self.health_checks),
            "total_anomalies": self.total_anomalies,
            "active_anomalies": active_anomalies,
            "auto_resolved": self.auto_resolved,
            "manual_resolved": self.manual_resolved,
            "total_policies": len(self.policies),
            "total_remediations": len(self.remediations),
            "successful_remediations": successful_remediations,
            "learned_patterns": len(self.patterns),
            "avg_mttr_seconds": avg_mttr
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 302: Self-Healing Infrastructure")
    print("=" * 60)
    
    manager = SelfHealingManager()
    print("✓ Self-Healing Infrastructure Manager created")
    
    # Register resources
    print("\n📦 Registering Resources...")
    
    resources_data = [
        ("web-server-1", "compute"),
        ("web-server-2", "compute"),
        ("api-server-1", "compute"),
        ("database-primary", "database"),
        ("database-replica", "database"),
        ("cache-cluster", "cache"),
        ("message-queue", "queue"),
        ("load-balancer", "network")
    ]
    
    resources = []
    for name, r_type in resources_data:
        resource = await manager.register_resource(name, r_type)
        resources.append(resource)
        print(f"  📦 {name} ({r_type})")
        
    # Add health checks
    print("\n❤️ Adding Health Checks...")
    
    for resource in resources:
        # HTTP health check
        await manager.add_health_check(
            resource.resource_id,
            check_type="http",
            endpoint=f"http://{resource.name}:8080/health",
            interval=30
        )
        
        # TCP health check
        await manager.add_health_check(
            resource.resource_id,
            check_type="tcp",
            endpoint=f"{resource.name}:8080",
            interval=15
        )
        
    print(f"  ❤️ Added {len(manager.health_checks)} health checks")
    
    # Create remediation policies
    print("\n📋 Creating Remediation Policies...")
    
    policies_data = [
        ("CPU Spike Recovery", AnomalyType.CPU_SPIKE, 
         [RemediationAction.SCALE_UP, RemediationAction.ALERT_ONLY]),
        ("Memory Leak Recovery", AnomalyType.MEMORY_LEAK,
         [RemediationAction.RESTART_SERVICE]),
        ("Disk Full Recovery", AnomalyType.DISK_FULL,
         [RemediationAction.ROTATE_LOGS, RemediationAction.CLEAR_CACHE]),
        ("High Error Rate Recovery", AnomalyType.ERROR_RATE,
         [RemediationAction.ROLLBACK, RemediationAction.ALERT_ONLY]),
        ("Connection Pool Recovery", AnomalyType.CONNECTION_POOL,
         [RemediationAction.RESTART_SERVICE]),
        ("Process Crash Recovery", AnomalyType.PROCESS_CRASH,
         [RemediationAction.RESTART_SERVICE, RemediationAction.FAILOVER])
    ]
    
    policies = []
    for name, anomaly_type, actions in policies_data:
        policy = await manager.create_policy(name, anomaly_type, actions)
        policies.append(policy)
        actions_str = ", ".join([a.value for a in actions])
        print(f"  📋 {name}")
        print(f"     Trigger: {anomaly_type.value} | Actions: {actions_str}")
        
    # Run health checks
    print("\n🔍 Running Health Checks...")
    
    for check in manager.health_checks.values():
        await manager.run_health_check(check.check_id)
        
    for resource in resources:
        await manager.update_resource_health(resource.resource_id)
        
    health_summary = {}
    for resource in resources:
        status = resource.health_status.value
        health_summary[status] = health_summary.get(status, 0) + 1
        
    for status, count in health_summary.items():
        print(f"  {status}: {count} resources")
        
    # Simulate anomalies
    print("\n⚠️ Simulating Anomalies...")
    
    anomaly_scenarios = [
        (resources[0], AnomalyType.CPU_SPIKE, 95.0, 50.0),
        (resources[1], AnomalyType.MEMORY_LEAK, 85.0, 60.0),
        (resources[3], AnomalyType.CONNECTION_POOL, 950, 500),
        (resources[5], AnomalyType.DISK_FULL, 92.0, 70.0),
        (resources[6], AnomalyType.ERROR_RATE, 5.5, 0.5),
        (resources[2], AnomalyType.PROCESS_CRASH, 0, 1)
    ]
    
    anomalies = []
    for resource, anomaly_type, current, expected in anomaly_scenarios:
        anomaly = await manager.detect_anomaly(
            resource.resource_id,
            anomaly_type,
            current,
            expected
        )
        anomalies.append(anomaly)
        
        severity_bar = "█" * int(anomaly.severity * 10) + "░" * (10 - int(anomaly.severity * 10))
        print(f"\n  ⚠️ {resource.name}: {anomaly_type.value}")
        print(f"     Value: {current} (expected: {expected})")
        print(f"     Severity: [{severity_bar}] {anomaly.severity:.1%}")
        
    # Auto-heal anomalies
    print("\n🔧 Auto-Healing Anomalies...")
    
    for anomaly in anomalies:
        remediation = await manager.auto_heal(anomaly.anomaly_id)
        
        if remediation:
            resource = manager.resources.get(anomaly.resource_id)
            status_icon = "✅" if remediation.success else "❌"
            print(f"\n  {status_icon} {resource.name if resource else 'Unknown'}")
            print(f"     Anomaly: {anomaly.anomaly_type.value}")
            print(f"     Actions: {', '.join(remediation.actions_executed)}")
        else:
            print(f"  ⏭️ No matching policy for anomaly {anomaly.anomaly_id}")
            
    # Resource health report
    print("\n📊 Resource Health Reports:")
    
    print("\n  ┌────────────────────────┬────────────┬────────────┬────────┬──────────┐")
    print("  │ Resource               │ Status     │ Score      │ Anoms  │ MTTR     │")
    print("  ├────────────────────────┼────────────┼────────────┼────────┼──────────┤")
    
    for resource in resources:
        report = manager.get_resource_health_report(resource.resource_id)
        
        name = resource.name[:22].ljust(22)
        
        status_icons = {
            "healthy": "🟢",
            "degraded": "🟡",
            "unhealthy": "🔴",
            "critical": "⚫",
            "unknown": "⚪"
        }
        status = f"{status_icons.get(report['health_status'], '⚪')} {report['health_status'][:8]}".ljust(10)
        
        score = f"{report['health_score']:.0f}%".ljust(10)
        anoms = str(report['total_anomalies']).ljust(6)
        mttr = f"{report['mttr_seconds']:.1f}s".ljust(8) if report['mttr_seconds'] > 0 else "N/A".ljust(8)
        
        print(f"  │ {name} │ {status} │ {score} │ {anoms} │ {mttr} │")
        
    print("  └────────────────────────┴────────────┴────────────┴────────┴──────────┘")
    
    # Predict issues
    print("\n🔮 Predictive Analysis:")
    
    for resource in resources[:4]:
        predictions = await manager.predict_issues(resource.resource_id)
        
        if predictions:
            print(f"\n  🔮 {resource.name}:")
            for pred in predictions:
                prob_bar = "█" * int(pred['probability'] * 10) + "░" * (10 - int(pred['probability'] * 10))
                print(f"     {pred['anomaly_type']}: [{prob_bar}] {pred['probability']:.0%}")
                
    # Learned patterns
    print("\n🧠 Learned Patterns:")
    
    for pattern in list(manager.patterns.values())[:5]:
        print(f"\n  🧠 {pattern.anomaly_type.value} → {pattern.successful_action.value}")
        print(f"     Occurrences: {pattern.occurrences} | Success: {pattern.success_rate:.0%}")
        
    # Remediation history
    print("\n📋 Recent Remediations:")
    
    for remediation in list(manager.remediations.values())[:5]:
        anomaly = manager.anomalies.get(remediation.anomaly_id)
        resource = manager.resources.get(anomaly.resource_id) if anomaly else None
        
        status_icon = "✅" if remediation.success else "❌"
        
        if anomaly and resource:
            duration = 0
            if remediation.completed_at and remediation.started_at:
                duration = (remediation.completed_at - remediation.started_at).total_seconds()
            print(f"  {status_icon} {resource.name}: {anomaly.anomaly_type.value} ({duration:.2f}s)")
            
    # Statistics
    print("\n📊 Self-Healing Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Total Resources: {stats['total_resources']}")
    print(f"    Healthy: {stats['healthy_resources']}")
    print(f"    Degraded: {stats['degraded_resources']}")
    print(f"    Unhealthy: {stats['unhealthy_resources']}")
    
    print(f"\n  Total Anomalies: {stats['total_anomalies']}")
    print(f"  Active Anomalies: {stats['active_anomalies']}")
    print(f"  Auto-Resolved: {stats['auto_resolved']}")
    
    print(f"\n  Total Remediations: {stats['total_remediations']}")
    print(f"  Successful: {stats['successful_remediations']}")
    print(f"\n  Learned Patterns: {stats['learned_patterns']}")
    print(f"  Avg MTTR: {stats['avg_mttr_seconds']:.1f}s")
    
    auto_heal_rate = (stats['auto_resolved'] / max(stats['total_anomalies'], 1)) * 100
    success_rate = (stats['successful_remediations'] / max(stats['total_remediations'], 1)) * 100
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Self-Healing Infrastructure Dashboard             │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Resources:               {stats['total_resources']:>12}                        │")
    print(f"│ Healthy Resources:             {stats['healthy_resources']:>12}                        │")
    print(f"│ Total Anomalies:               {stats['total_anomalies']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Auto-Heal Rate:                {auto_heal_rate:>11.1f}%                        │")
    print(f"│ Remediation Success:           {success_rate:>11.1f}%                        │")
    print(f"│ Average MTTR:                  {stats['avg_mttr_seconds']:>10.1f}s                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Self-Healing Infrastructure Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
