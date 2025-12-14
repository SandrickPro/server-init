#!/usr/bin/env python3
"""
Server Init - Iteration 208: Health Monitor Platform
Платформа мониторинга здоровья

Функционал:
- Health Checks - проверки здоровья
- Liveness Probes - проверки жизнеспособности
- Readiness Probes - проверки готовности
- Dependency Monitoring - мониторинг зависимостей
- Health Aggregation - агрегация состояния
- Alert Integration - интеграция с алертами
- Health Reports - отчёты о здоровье
- Recovery Actions - действия по восстановлению
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
    UNKNOWN = "unknown"


class CheckType(Enum):
    """Тип проверки"""
    HTTP = "http"
    TCP = "tcp"
    GRPC = "grpc"
    EXEC = "exec"
    CUSTOM = "custom"


class ProbeType(Enum):
    """Тип пробы"""
    LIVENESS = "liveness"
    READINESS = "readiness"
    STARTUP = "startup"


class SeverityLevel(Enum):
    """Уровень серьёзности"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class HealthCheckConfig:
    """Конфигурация проверки здоровья"""
    check_type: CheckType = CheckType.HTTP
    
    # Endpoint
    endpoint: str = "/health"
    port: int = 8080
    
    # Timing
    interval_seconds: int = 30
    timeout_seconds: int = 5
    
    # Thresholds
    success_threshold: int = 1
    failure_threshold: int = 3
    
    # Initial delay
    initial_delay_seconds: int = 0


@dataclass
class HealthCheckResult:
    """Результат проверки здоровья"""
    check_id: str
    status: HealthStatus = HealthStatus.UNKNOWN
    
    # Response
    response_time_ms: float = 0
    status_code: int = 0
    message: str = ""
    
    # Time
    checked_at: datetime = field(default_factory=datetime.now)
    
    # Metrics
    consecutive_failures: int = 0
    consecutive_successes: int = 0


@dataclass
class Component:
    """Компонент системы"""
    component_id: str
    name: str = ""
    
    # Type
    component_type: str = "service"
    
    # Health
    health_status: HealthStatus = HealthStatus.UNKNOWN
    
    # Checks
    health_config: HealthCheckConfig = field(default_factory=HealthCheckConfig)
    last_result: Optional[HealthCheckResult] = None
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    
    # History
    check_history: List[HealthCheckResult] = field(default_factory=list)
    
    # Metadata
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class Dependency:
    """Зависимость"""
    dependency_id: str
    
    # Source and target
    source_id: str = ""
    target_id: str = ""
    
    # Type
    dependency_type: str = "required"  # required, optional
    
    # Health
    healthy: bool = True
    
    # Latency
    latency_ms: float = 0


@dataclass
class HealthAlert:
    """Алерт здоровья"""
    alert_id: str
    component_id: str = ""
    
    # Severity
    severity: SeverityLevel = SeverityLevel.WARNING
    
    # Status
    status: HealthStatus = HealthStatus.UNHEALTHY
    
    # Message
    title: str = ""
    description: str = ""
    
    # Time
    triggered_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    
    @property
    def is_active(self) -> bool:
        return self.resolved_at is None


@dataclass
class RecoveryAction:
    """Действие по восстановлению"""
    action_id: str
    name: str = ""
    
    # Target
    component_id: str = ""
    
    # Type
    action_type: str = "restart"  # restart, scale, failover
    
    # Status
    executed: bool = False
    success: bool = False
    
    # Time
    executed_at: Optional[datetime] = None


class HealthChecker:
    """Проверщик здоровья"""
    
    async def check(self, component: Component) -> HealthCheckResult:
        """Выполнение проверки здоровья"""
        config = component.health_config
        
        # Simulate check
        await asyncio.sleep(random.uniform(0.01, 0.05))
        
        # Simulate result
        is_healthy = random.random() > 0.15
        response_time = random.uniform(10, 500)
        
        result = HealthCheckResult(
            check_id=f"check_{uuid.uuid4().hex[:8]}",
            status=HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY,
            response_time_ms=response_time,
            status_code=200 if is_healthy else 500,
            message="OK" if is_healthy else "Service unavailable"
        )
        
        # Update consecutive counts
        if component.last_result:
            if is_healthy:
                result.consecutive_successes = component.last_result.consecutive_successes + 1
                result.consecutive_failures = 0
            else:
                result.consecutive_failures = component.last_result.consecutive_failures + 1
                result.consecutive_successes = 0
                
        return result


class DependencyChecker:
    """Проверщик зависимостей"""
    
    def __init__(self, components: Dict[str, Component]):
        self.components = components
        
    def check_dependencies(self, component_id: str) -> List[Dependency]:
        """Проверка зависимостей компонента"""
        component = self.components.get(component_id)
        if not component:
            return []
            
        dependencies = []
        
        for dep_id in component.dependencies:
            dep_component = self.components.get(dep_id)
            
            dependency = Dependency(
                dependency_id=f"dep_{uuid.uuid4().hex[:8]}",
                source_id=component_id,
                target_id=dep_id,
                healthy=dep_component.health_status == HealthStatus.HEALTHY if dep_component else False,
                latency_ms=random.uniform(1, 100)
            )
            dependencies.append(dependency)
            
        return dependencies


class HealthAggregator:
    """Агрегатор здоровья"""
    
    def aggregate(self, components: List[Component]) -> HealthStatus:
        """Агрегация статуса здоровья"""
        if not components:
            return HealthStatus.UNKNOWN
            
        statuses = [c.health_status for c in components]
        
        # If any is unhealthy - system is unhealthy
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
            
        # If any is degraded - system is degraded
        if HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
            
        # If all are healthy
        if all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY
            
        return HealthStatus.UNKNOWN


class AlertManager:
    """Менеджер алертов"""
    
    def __init__(self):
        self.alerts: Dict[str, HealthAlert] = {}
        
    def create_alert(self, component: Component, severity: SeverityLevel) -> HealthAlert:
        """Создание алерта"""
        alert = HealthAlert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            component_id=component.component_id,
            severity=severity,
            status=component.health_status,
            title=f"{component.name} is {component.health_status.value}",
            description=f"Component {component.name} health status changed to {component.health_status.value}"
        )
        self.alerts[alert.alert_id] = alert
        return alert
        
    def resolve_alert(self, alert_id: str) -> bool:
        """Разрешение алерта"""
        alert = self.alerts.get(alert_id)
        if not alert:
            return False
            
        alert.resolved_at = datetime.now()
        return True
        
    def get_active_alerts(self) -> List[HealthAlert]:
        """Получение активных алертов"""
        return [a for a in self.alerts.values() if a.is_active]


class RecoveryManager:
    """Менеджер восстановления"""
    
    def __init__(self):
        self.actions: List[RecoveryAction] = []
        
    async def execute_recovery(self, component: Component, action_type: str) -> RecoveryAction:
        """Выполнение действия по восстановлению"""
        action = RecoveryAction(
            action_id=f"recovery_{uuid.uuid4().hex[:8]}",
            name=f"{action_type} {component.name}",
            component_id=component.component_id,
            action_type=action_type
        )
        
        # Simulate recovery
        await asyncio.sleep(0.1)
        
        action.executed = True
        action.executed_at = datetime.now()
        action.success = random.random() > 0.1
        
        self.actions.append(action)
        return action


class HealthMonitorPlatform:
    """Платформа мониторинга здоровья"""
    
    def __init__(self):
        self.components: Dict[str, Component] = {}
        self.checker = HealthChecker()
        self.aggregator = HealthAggregator()
        self.alert_manager = AlertManager()
        self.recovery_manager = RecoveryManager()
        
    def register_component(self, name: str, component_type: str = "service",
                          dependencies: List[str] = None,
                          check_type: CheckType = CheckType.HTTP,
                          endpoint: str = "/health") -> Component:
        """Регистрация компонента"""
        component = Component(
            component_id=f"comp_{uuid.uuid4().hex[:8]}",
            name=name,
            component_type=component_type,
            dependencies=dependencies or [],
            health_config=HealthCheckConfig(
                check_type=check_type,
                endpoint=endpoint
            )
        )
        self.components[component.component_id] = component
        return component
        
    async def check_health(self, component_id: str) -> HealthCheckResult:
        """Проверка здоровья компонента"""
        component = self.components.get(component_id)
        if not component:
            return HealthCheckResult(check_id="", status=HealthStatus.UNKNOWN)
            
        result = await self.checker.check(component)
        
        # Update component
        component.last_result = result
        component.check_history.append(result)
        
        # Determine health status
        config = component.health_config
        
        if result.consecutive_successes >= config.success_threshold:
            component.health_status = HealthStatus.HEALTHY
        elif result.consecutive_failures >= config.failure_threshold:
            component.health_status = HealthStatus.UNHEALTHY
            
            # Create alert
            self.alert_manager.create_alert(component, SeverityLevel.CRITICAL)
        elif result.consecutive_failures > 0:
            component.health_status = HealthStatus.DEGRADED
            
        return result
        
    async def check_all(self) -> Dict[str, HealthStatus]:
        """Проверка всех компонентов"""
        results = {}
        
        for component_id in self.components:
            await self.check_health(component_id)
            component = self.components[component_id]
            results[component.name] = component.health_status
            
        return results
        
    def get_system_health(self) -> HealthStatus:
        """Получение общего здоровья системы"""
        return self.aggregator.aggregate(list(self.components.values()))
        
    def get_health_report(self) -> Dict[str, Any]:
        """Генерация отчёта о здоровье"""
        return {
            "system_status": self.get_system_health().value,
            "total_components": len(self.components),
            "healthy": len([c for c in self.components.values() 
                          if c.health_status == HealthStatus.HEALTHY]),
            "degraded": len([c for c in self.components.values() 
                          if c.health_status == HealthStatus.DEGRADED]),
            "unhealthy": len([c for c in self.components.values() 
                           if c.health_status == HealthStatus.UNHEALTHY]),
            "active_alerts": len(self.alert_manager.get_active_alerts()),
            "timestamp": datetime.now().isoformat()
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 208: Health Monitor Platform")
    print("=" * 60)
    
    platform = HealthMonitorPlatform()
    print("✓ Health Monitor Platform created")
    
    # Register components
    print("\n📦 Registering Components...")
    
    # Core services
    api_gateway = platform.register_component("api-gateway", "gateway", endpoint="/health/live")
    user_service = platform.register_component("user-service", "service", [api_gateway.component_id])
    order_service = platform.register_component("order-service", "service", [api_gateway.component_id, user_service.component_id])
    payment_service = platform.register_component("payment-service", "service", [order_service.component_id])
    
    # Data stores
    postgres = platform.register_component("postgres", "database", check_type=CheckType.TCP, endpoint="5432")
    redis = platform.register_component("redis", "cache", check_type=CheckType.TCP, endpoint="6379")
    
    # Message queue
    kafka = platform.register_component("kafka", "message-queue", check_type=CheckType.TCP, endpoint="9092")
    
    # External
    stripe = platform.register_component("stripe-api", "external", endpoint="/v1/health")
    
    print(f"  ✓ Registered {len(platform.components)} components")
    
    # Run health checks
    print("\n🔍 Running Health Checks...")
    
    await platform.check_all()
    
    # Display component health
    print("\n📊 Component Health Status:")
    
    print("\n  ┌────────────────────────┬──────────────┬────────────┬──────────────┐")
    print("  │ Component              │ Type         │ Status     │ Response     │")
    print("  ├────────────────────────┼──────────────┼────────────┼──────────────┤")
    
    for component in platform.components.values():
        name = component.name[:22].ljust(22)
        comp_type = component.component_type[:12].ljust(12)
        
        status = component.health_status.value[:10].ljust(10)
        if component.health_status == HealthStatus.HEALTHY:
            status_icon = "🟢"
        elif component.health_status == HealthStatus.DEGRADED:
            status_icon = "🟡"
        else:
            status_icon = "🔴"
            
        response = "N/A"
        if component.last_result:
            response = f"{component.last_result.response_time_ms:.0f}ms"
        response = response[:12].ljust(12)
        
        print(f"  │ {name} │ {comp_type} │ {status_icon} {status[:8]} │ {response} │")
        
    print("  └────────────────────────┴──────────────┴────────────┴──────────────┘")
    
    # System health
    system_health = platform.get_system_health()
    print(f"\n🏥 System Health: {system_health.value.upper()}")
    
    # Health by type
    print("\n📈 Health by Component Type:")
    
    type_health = {}
    for component in platform.components.values():
        t = component.component_type
        if t not in type_health:
            type_health[t] = {"healthy": 0, "total": 0}
        type_health[t]["total"] += 1
        if component.health_status == HealthStatus.HEALTHY:
            type_health[t]["healthy"] += 1
            
    for comp_type, data in type_health.items():
        healthy = data["healthy"]
        total = data["total"]
        pct = healthy / total * 100 if total > 0 else 0
        bar = "█" * int(pct / 10) + "░" * (10 - int(pct / 10))
        print(f"  {comp_type:15s} [{bar}] {healthy}/{total} ({pct:.0f}%)")
        
    # Dependencies
    print("\n🔗 Dependency Health:")
    
    dep_checker = DependencyChecker(platform.components)
    
    for component in platform.components.values():
        if component.dependencies:
            deps = dep_checker.check_dependencies(component.component_id)
            dep_status = all(d.healthy for d in deps)
            status_icon = "✓" if dep_status else "✗"
            dep_names = []
            for dep in deps:
                dep_comp = platform.components.get(dep.target_id)
                if dep_comp:
                    icon = "🟢" if dep.healthy else "🔴"
                    dep_names.append(f"{icon} {dep_comp.name}")
            print(f"  {status_icon} {component.name} -> {', '.join(dep_names)}")
            
    # Active alerts
    print("\n🚨 Active Alerts:")
    
    active_alerts = platform.alert_manager.get_active_alerts()
    
    if active_alerts:
        for alert in active_alerts:
            component = platform.components.get(alert.component_id)
            comp_name = component.name if component else "Unknown"
            severity_icon = "🔴" if alert.severity == SeverityLevel.CRITICAL else "🟡"
            print(f"  {severity_icon} [{alert.severity.value.upper()}] {alert.title}")
            print(f"      Component: {comp_name}")
            print(f"      Time: {alert.triggered_at.strftime('%H:%M:%S')}")
    else:
        print("  ✓ No active alerts")
        
    # Recovery actions for unhealthy components
    print("\n🔧 Recovery Actions:")
    
    unhealthy = [c for c in platform.components.values() 
                if c.health_status == HealthStatus.UNHEALTHY]
    
    for component in unhealthy[:2]:  # Limit to 2 for demo
        action = await platform.recovery_manager.execute_recovery(component, "restart")
        status = "✓" if action.success else "✗"
        print(f"  {status} {action.name}: {'Success' if action.success else 'Failed'}")
        
    # Response time analysis
    print("\n⏱️ Response Time Analysis:")
    
    response_times = []
    for component in platform.components.values():
        if component.last_result:
            response_times.append((component.name, component.last_result.response_time_ms))
            
    response_times.sort(key=lambda x: x[1], reverse=True)
    
    print("\n  Top 5 Slowest Components:")
    for i, (name, rt) in enumerate(response_times[:5], 1):
        bar_len = int(rt / 50) if rt < 500 else 10
        bar = "█" * bar_len + "░" * (10 - bar_len)
        print(f"    {i}. {name:20s} [{bar}] {rt:.0f}ms")
        
    # Health check history
    print("\n📜 Health Check Summary:")
    
    total_checks = sum(len(c.check_history) for c in platform.components.values())
    successful_checks = sum(
        len([h for h in c.check_history if h.status == HealthStatus.HEALTHY])
        for c in platform.components.values()
    )
    
    print(f"  Total Checks: {total_checks}")
    print(f"  Successful: {successful_checks}")
    print(f"  Success Rate: {(successful_checks/total_checks*100):.1f}%" if total_checks > 0 else "N/A")
    
    # Health report
    report = platform.get_health_report()
    
    print("\n📋 Health Report:")
    print(f"\n  System Status: {report['system_status'].upper()}")
    print(f"  Components: {report['total_components']}")
    print(f"    Healthy: {report['healthy']}")
    print(f"    Degraded: {report['degraded']}")
    print(f"    Unhealthy: {report['unhealthy']}")
    print(f"  Active Alerts: {report['active_alerts']}")
    
    # Health score
    health_score = (report['healthy'] / report['total_components'] * 100) if report['total_components'] > 0 else 0
    
    print(f"\n  Health Score: {health_score:.0f}/100")
    score_bar = "█" * int(health_score / 10) + "░" * (10 - int(health_score / 10))
    print(f"  [{score_bar}]")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Health Monitor Dashboard                         │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ System Status:           {report['system_status'].upper():>12}                        │")
    print(f"│ Total Components:                {report['total_components']:>12}                  │")
    print(f"│ Healthy:                         {report['healthy']:>12}                  │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Active Alerts:                   {report['active_alerts']:>12}                  │")
    print(f"│ Health Score:                       {health_score:>9.0f}/100             │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Health Monitor Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
