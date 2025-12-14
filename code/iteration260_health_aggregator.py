#!/usr/bin/env python3
"""
Server Init - Iteration 260: Health Aggregator Platform
Платформа агрегации здоровья сервисов

Функционал:
- Service Health Checks - проверки здоровья сервисов
- Dependency Mapping - маппинг зависимостей
- Health Aggregation - агрегация состояния
- Degradation Detection - обнаружение деградации
- Threshold Management - управление порогами
- Alert Integration - интеграция алертинга
- Dashboard Generation - генерация дашборда
- Historical Analysis - исторический анализ
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
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
    DATABASE = "database"
    CUSTOM = "custom"


class AggregationStrategy(Enum):
    """Стратегия агрегации"""
    ALL_HEALTHY = "all_healthy"  # All must be healthy
    ANY_HEALTHY = "any_healthy"  # At least one healthy
    MAJORITY_HEALTHY = "majority_healthy"  # >50% healthy
    WEIGHTED = "weighted"  # Weighted by importance


class AlertSeverity(Enum):
    """Серьёзность алерта"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class HealthCheckConfig:
    """Конфигурация проверки здоровья"""
    check_id: str
    name: str
    
    # Check type
    check_type: CheckType = CheckType.HTTP
    
    # Endpoint
    endpoint: str = ""
    port: int = 80
    path: str = "/health"
    
    # Timing
    interval_ms: int = 30000
    timeout_ms: int = 5000
    
    # Thresholds
    healthy_threshold: int = 2  # consecutive successes
    unhealthy_threshold: int = 3  # consecutive failures
    
    # Weight
    weight: float = 1.0


@dataclass
class HealthCheckResult:
    """Результат проверки здоровья"""
    result_id: str
    check_id: str
    
    # Status
    status: HealthStatus = HealthStatus.UNKNOWN
    response_time_ms: float = 0
    
    # Details
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    checked_at: datetime = field(default_factory=datetime.now)


@dataclass
class ServiceHealth:
    """Здоровье сервиса"""
    service_id: str
    name: str
    
    # Status
    status: HealthStatus = HealthStatus.UNKNOWN
    
    # Checks
    checks: List[HealthCheckConfig] = field(default_factory=list)
    latest_results: Dict[str, HealthCheckResult] = field(default_factory=dict)
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    
    # Stats
    consecutive_healthy: int = 0
    consecutive_unhealthy: int = 0
    
    # History
    status_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timing
    last_check: datetime = field(default_factory=datetime.now)
    status_changed_at: datetime = field(default_factory=datetime.now)


@dataclass
class DependencyNode:
    """Узел зависимости"""
    service_id: str
    name: str
    
    # Relations
    depends_on: Set[str] = field(default_factory=set)
    depended_by: Set[str] = field(default_factory=set)
    
    # Impact
    impact_weight: float = 1.0
    critical: bool = False


@dataclass
class HealthAlert:
    """Алерт о здоровье"""
    alert_id: str
    service_id: str
    
    # Alert info
    severity: AlertSeverity = AlertSeverity.WARNING
    message: str = ""
    
    # Status
    acknowledged: bool = False
    resolved: bool = False
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


@dataclass
class AggregatedHealth:
    """Агрегированное здоровье"""
    aggregation_id: str
    name: str
    
    # Status
    overall_status: HealthStatus = HealthStatus.UNKNOWN
    
    # Services
    services_total: int = 0
    services_healthy: int = 0
    services_degraded: int = 0
    services_unhealthy: int = 0
    
    # Metrics
    health_percentage: float = 100.0
    avg_response_time_ms: float = 0
    
    # Timing
    aggregated_at: datetime = field(default_factory=datetime.now)


class HealthAggregatorManager:
    """Менеджер агрегации здоровья"""
    
    def __init__(self):
        self.services: Dict[str, ServiceHealth] = {}
        self.dependencies: Dict[str, DependencyNode] = {}
        self.alerts: List[HealthAlert] = []
        self.aggregation_strategy: AggregationStrategy = AggregationStrategy.MAJORITY_HEALTHY
        
    def register_service(self, name: str, dependencies: List[str] = None) -> ServiceHealth:
        """Регистрация сервиса"""
        service = ServiceHealth(
            service_id=f"svc_{uuid.uuid4().hex[:8]}",
            name=name,
            dependencies=dependencies or []
        )
        
        self.services[name] = service
        
        # Create dependency node
        node = DependencyNode(
            service_id=service.service_id,
            name=name,
            depends_on=set(dependencies or [])
        )
        self.dependencies[name] = node
        
        # Update reverse dependencies
        for dep_name in dependencies or []:
            if dep_name in self.dependencies:
                self.dependencies[dep_name].depended_by.add(name)
                
        return service
        
    def add_health_check(self, service_name: str,
                        check_name: str,
                        check_type: CheckType = CheckType.HTTP,
                        endpoint: str = "",
                        interval_ms: int = 30000) -> HealthCheckConfig:
        """Добавление проверки здоровья"""
        service = self.services.get(service_name)
        if not service:
            return None
            
        check = HealthCheckConfig(
            check_id=f"chk_{uuid.uuid4().hex[:8]}",
            name=check_name,
            check_type=check_type,
            endpoint=endpoint,
            interval_ms=interval_ms
        )
        
        service.checks.append(check)
        return check
        
    async def perform_check(self, service_name: str, check_id: str) -> HealthCheckResult:
        """Выполнение проверки"""
        service = self.services.get(service_name)
        if not service:
            return None
            
        check = next((c for c in service.checks if c.check_id == check_id), None)
        if not check:
            return None
            
        # Simulate check
        start_time = datetime.now()
        await asyncio.sleep(random.uniform(0.01, 0.1))
        
        # Simulate random results
        success = random.random() > 0.2  # 80% success rate
        response_time = random.uniform(10, 500)
        
        result = HealthCheckResult(
            result_id=f"res_{uuid.uuid4().hex[:8]}",
            check_id=check_id,
            status=HealthStatus.HEALTHY if success else HealthStatus.UNHEALTHY,
            response_time_ms=response_time,
            message="OK" if success else "Connection failed"
        )
        
        service.latest_results[check_id] = result
        return result
        
    def update_service_status(self, service_name: str):
        """Обновление статуса сервиса"""
        service = self.services.get(service_name)
        if not service:
            return
            
        if not service.latest_results:
            service.status = HealthStatus.UNKNOWN
            return
            
        # Count status from checks
        healthy = 0
        unhealthy = 0
        
        for result in service.latest_results.values():
            if result.status == HealthStatus.HEALTHY:
                healthy += 1
            else:
                unhealthy += 1
                
        total = healthy + unhealthy
        
        # Determine status
        old_status = service.status
        
        if unhealthy == 0:
            service.status = HealthStatus.HEALTHY
            service.consecutive_healthy += 1
            service.consecutive_unhealthy = 0
        elif healthy == 0:
            service.status = HealthStatus.UNHEALTHY
            service.consecutive_unhealthy += 1
            service.consecutive_healthy = 0
        else:
            service.status = HealthStatus.DEGRADED
            
        # Record status change
        if old_status != service.status:
            service.status_changed_at = datetime.now()
            service.status_history.append({
                "from": old_status.value,
                "to": service.status.value,
                "timestamp": datetime.now()
            })
            
            # Create alert if unhealthy
            if service.status == HealthStatus.UNHEALTHY:
                self._create_alert(service_name, AlertSeverity.ERROR, 
                                  f"Service {service_name} is unhealthy")
            elif service.status == HealthStatus.DEGRADED:
                self._create_alert(service_name, AlertSeverity.WARNING,
                                  f"Service {service_name} is degraded")
                                  
        service.last_check = datetime.now()
        
    def _create_alert(self, service_id: str, severity: AlertSeverity, message: str):
        """Создание алерта"""
        alert = HealthAlert(
            alert_id=f"alt_{uuid.uuid4().hex[:8]}",
            service_id=service_id,
            severity=severity,
            message=message
        )
        
        self.alerts.append(alert)
        return alert
        
    def aggregate_health(self, name: str = "system") -> AggregatedHealth:
        """Агрегация здоровья"""
        aggregation = AggregatedHealth(
            aggregation_id=f"agg_{uuid.uuid4().hex[:8]}",
            name=name,
            services_total=len(self.services)
        )
        
        total_response_time = 0
        response_count = 0
        
        for service in self.services.values():
            if service.status == HealthStatus.HEALTHY:
                aggregation.services_healthy += 1
            elif service.status == HealthStatus.DEGRADED:
                aggregation.services_degraded += 1
            elif service.status == HealthStatus.UNHEALTHY:
                aggregation.services_unhealthy += 1
                
            for result in service.latest_results.values():
                total_response_time += result.response_time_ms
                response_count += 1
                
        # Calculate overall status
        if self.aggregation_strategy == AggregationStrategy.ALL_HEALTHY:
            if aggregation.services_healthy == aggregation.services_total:
                aggregation.overall_status = HealthStatus.HEALTHY
            elif aggregation.services_unhealthy > 0:
                aggregation.overall_status = HealthStatus.UNHEALTHY
            else:
                aggregation.overall_status = HealthStatus.DEGRADED
                
        elif self.aggregation_strategy == AggregationStrategy.ANY_HEALTHY:
            if aggregation.services_healthy > 0:
                aggregation.overall_status = HealthStatus.HEALTHY
            else:
                aggregation.overall_status = HealthStatus.UNHEALTHY
                
        elif self.aggregation_strategy == AggregationStrategy.MAJORITY_HEALTHY:
            healthy_ratio = aggregation.services_healthy / max(1, aggregation.services_total)
            if healthy_ratio > 0.5:
                aggregation.overall_status = HealthStatus.HEALTHY
            elif healthy_ratio > 0.25:
                aggregation.overall_status = HealthStatus.DEGRADED
            else:
                aggregation.overall_status = HealthStatus.UNHEALTHY
                
        # Calculate metrics
        if aggregation.services_total > 0:
            aggregation.health_percentage = (aggregation.services_healthy / aggregation.services_total) * 100
            
        if response_count > 0:
            aggregation.avg_response_time_ms = total_response_time / response_count
            
        return aggregation
        
    def get_dependency_impact(self, service_name: str) -> List[str]:
        """Получение зависимых сервисов"""
        node = self.dependencies.get(service_name)
        if not node:
            return []
            
        impacted = list(node.depended_by)
        
        # Recursively find all impacted services
        for dep in list(impacted):
            impacted.extend(self.get_dependency_impact(dep))
            
        return list(set(impacted))
        
    def get_active_alerts(self) -> List[HealthAlert]:
        """Получение активных алертов"""
        return [a for a in self.alerts if not a.resolved]
        
    def acknowledge_alert(self, alert_id: str):
        """Подтверждение алерта"""
        alert = next((a for a in self.alerts if a.alert_id == alert_id), None)
        if alert:
            alert.acknowledged = True
            alert.acknowledged_at = datetime.now()
            
    def resolve_alert(self, alert_id: str):
        """Разрешение алерта"""
        alert = next((a for a in self.alerts if a.alert_id == alert_id), None)
        if alert:
            alert.resolved = True
            alert.resolved_at = datetime.now()
            
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        statuses = {status: 0 for status in HealthStatus}
        
        for service in self.services.values():
            statuses[service.status] += 1
            
        active_alerts = len(self.get_active_alerts())
        
        return {
            "services_total": len(self.services),
            "services_healthy": statuses[HealthStatus.HEALTHY],
            "services_degraded": statuses[HealthStatus.DEGRADED],
            "services_unhealthy": statuses[HealthStatus.UNHEALTHY],
            "services_unknown": statuses[HealthStatus.UNKNOWN],
            "alerts_active": active_alerts,
            "alerts_total": len(self.alerts)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 260: Health Aggregator Platform")
    print("=" * 60)
    
    manager = HealthAggregatorManager()
    print("✓ Health Aggregator Manager created")
    
    # Register services
    print("\n📦 Registering Services...")
    
    services_data = [
        ("api-gateway", []),
        ("auth-service", ["database"]),
        ("user-service", ["database", "cache"]),
        ("order-service", ["database", "user-service", "payment-service"]),
        ("payment-service", ["database"]),
        ("notification-service", ["queue"]),
        ("database", []),
        ("cache", []),
        ("queue", []),
    ]
    
    for name, deps in services_data:
        service = manager.register_service(name, deps)
        deps_str = ", ".join(deps) if deps else "none"
        print(f"  📦 {name}: depends on [{deps_str}]")
        
    # Add health checks
    print("\n🏥 Adding Health Checks...")
    
    for service_name in manager.services:
        check = manager.add_health_check(
            service_name,
            f"{service_name}-http",
            CheckType.HTTP,
            f"http://{service_name}:8080/health"
        )
        if check:
            print(f"  🏥 {service_name}: HTTP check added")
            
    # Perform checks
    print("\n🔄 Performing Health Checks...")
    
    for service_name, service in manager.services.items():
        for check in service.checks:
            result = await manager.perform_check(service_name, check.check_id)
            if result:
                status_icon = "✅" if result.status == HealthStatus.HEALTHY else "❌"
                print(f"  {status_icon} {service_name}: {result.status.value} ({result.response_time_ms:.1f}ms)")
                
        manager.update_service_status(service_name)
        
    # Display services
    print("\n📊 Service Health Status:")
    
    print("\n  ┌─────────────────────┬───────────┬──────────┬──────────┬──────────────────┐")
    print("  │ Service             │ Status    │ Checks   │ Healthy  │ Last Check       │")
    print("  ├─────────────────────┼───────────┼──────────┼──────────┼──────────────────┤")
    
    for service in manager.services.values():
        name = service.name[:19].ljust(19)
        status = service.status.value[:9].ljust(9)
        checks = str(len(service.checks))[:8].ljust(8)
        healthy = str(service.consecutive_healthy)[:8].ljust(8)
        last_check = service.last_check.strftime("%H:%M:%S")[:16].ljust(16)
        
        print(f"  │ {name} │ {status} │ {checks} │ {healthy} │ {last_check} │")
        
    print("  └─────────────────────┴───────────┴──────────┴──────────┴──────────────────┘")
    
    # Dependencies
    print("\n🔗 Service Dependencies:")
    
    for name, node in manager.dependencies.items():
        if node.depends_on or node.depended_by:
            deps = ", ".join(node.depends_on) if node.depends_on else "none"
            depended = ", ".join(node.depended_by) if node.depended_by else "none"
            print(f"  {name}:")
            print(f"    ↓ depends on: {deps}")
            print(f"    ↑ depended by: {depended}")
            
    # Dependency impact
    print("\n💥 Dependency Impact Analysis:")
    
    for critical_service in ["database", "cache", "queue"]:
        impacted = manager.get_dependency_impact(critical_service)
        if impacted:
            print(f"  If {critical_service} fails: {', '.join(impacted)} affected")
            
    # Aggregated health
    print("\n📊 Aggregated Health:")
    
    aggregation = manager.aggregate_health()
    
    print(f"\n  Overall Status: {aggregation.overall_status.value}")
    print(f"  Health Percentage: {aggregation.health_percentage:.1f}%")
    print(f"  Avg Response Time: {aggregation.avg_response_time_ms:.1f}ms")
    
    print(f"\n  Services:")
    print(f"    Total: {aggregation.services_total}")
    print(f"    Healthy: {aggregation.services_healthy}")
    print(f"    Degraded: {aggregation.services_degraded}")
    print(f"    Unhealthy: {aggregation.services_unhealthy}")
    
    # Status distribution
    print("\n📊 Status Distribution:")
    
    for status in HealthStatus:
        count = sum(1 for s in manager.services.values() if s.status == status)
        bar_filled = int((count / max(1, len(manager.services))) * 10)
        bar = "█" * bar_filled + "░" * (10 - bar_filled)
        
        icon = {
            HealthStatus.HEALTHY: "🟢",
            HealthStatus.DEGRADED: "🟡",
            HealthStatus.UNHEALTHY: "🔴",
            HealthStatus.UNKNOWN: "⚪"
        }.get(status, "⚪")
        
        print(f"  {icon} {status.value:12s} [{bar}] {count}")
        
    # Alerts
    print("\n🚨 Active Alerts:")
    
    active_alerts = manager.get_active_alerts()
    if active_alerts:
        for alert in active_alerts[:5]:
            severity_icon = {
                AlertSeverity.INFO: "ℹ️",
                AlertSeverity.WARNING: "⚠️",
                AlertSeverity.ERROR: "❌",
                AlertSeverity.CRITICAL: "🔥"
            }.get(alert.severity, "❓")
            print(f"  {severity_icon} [{alert.severity.value}] {alert.message}")
    else:
        print("  ✅ No active alerts")
        
    # Statistics
    print("\n📊 Manager Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Services Total: {stats['services_total']}")
    print(f"  Services Healthy: {stats['services_healthy']}")
    print(f"  Services Degraded: {stats['services_degraded']}")
    print(f"  Services Unhealthy: {stats['services_unhealthy']}")
    print(f"\n  Alerts Active: {stats['alerts_active']}")
    print(f"  Alerts Total: {stats['alerts_total']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Health Aggregator Dashboard                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Overall Status:                {aggregation.overall_status.value:>12}                        │")
    print(f"│ Health Percentage:             {aggregation.health_percentage:>11.1f}%                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Services Total:                {stats['services_total']:>12}                        │")
    print(f"│ Services Healthy:              {stats['services_healthy']:>12}                        │")
    print(f"│ Services Unhealthy:            {stats['services_unhealthy']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Active Alerts:                 {stats['alerts_active']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Health Aggregator Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
