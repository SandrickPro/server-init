#!/usr/bin/env python3
"""
Server Init - Iteration 94: Health Check System
Система проверки здоровья

Функционал:
- Health Probes - проверки здоровья (liveness, readiness, startup)
- Dependency Checks - проверка зависимостей
- Health Aggregation - агрегация статусов
- Health History - история проверок
- Alerting - алертинг по статусу
- Self-Healing - самовосстановление
- Reporting - отчётность
- Dashboard - панель мониторинга
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Tuple, Awaitable
from enum import Enum
from collections import defaultdict
import uuid
import random


class HealthStatus(Enum):
    """Статус здоровья"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ProbeType(Enum):
    """Тип проверки"""
    LIVENESS = "liveness"
    READINESS = "readiness"
    STARTUP = "startup"


class CheckType(Enum):
    """Тип проверки зависимости"""
    HTTP = "http"
    TCP = "tcp"
    DATABASE = "database"
    REDIS = "redis"
    CUSTOM = "custom"


class AlertSeverity(Enum):
    """Серьёзность алерта"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class HealthCheckResult:
    """Результат проверки"""
    check_id: str
    name: str = ""
    
    # Статус
    status: HealthStatus = HealthStatus.UNKNOWN
    
    # Детали
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Время
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: float = 0
    
    # Ошибка
    error: str = ""


@dataclass
class HealthProbe:
    """Проверка здоровья"""
    probe_id: str
    name: str = ""
    probe_type: ProbeType = ProbeType.LIVENESS
    
    # Настройки
    interval_seconds: int = 30
    timeout_seconds: int = 10
    failure_threshold: int = 3
    success_threshold: int = 1
    
    # Проверка
    check_func: Optional[Callable] = None
    
    # Состояние
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_result: Optional[HealthCheckResult] = None
    
    # Статус
    status: HealthStatus = HealthStatus.UNKNOWN
    
    # История
    history: List[HealthCheckResult] = field(default_factory=list)
    history_limit: int = 100


@dataclass
class DependencyCheck:
    """Проверка зависимости"""
    check_id: str
    name: str = ""
    
    # Тип и параметры
    check_type: CheckType = CheckType.HTTP
    endpoint: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    
    # Настройки
    timeout_seconds: int = 5
    required: bool = True  # Критичная зависимость
    
    # Состояние
    status: HealthStatus = HealthStatus.UNKNOWN
    last_check: Optional[datetime] = None
    last_error: str = ""
    
    # Время отклика
    response_time_ms: float = 0


@dataclass 
class ServiceHealth:
    """Здоровье сервиса"""
    service_id: str
    name: str = ""
    version: str = ""
    
    # Проверки
    probes: Dict[str, HealthProbe] = field(default_factory=dict)
    dependencies: Dict[str, DependencyCheck] = field(default_factory=dict)
    
    # Общий статус
    status: HealthStatus = HealthStatus.UNKNOWN
    
    # Метаданные
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Время
    started_at: datetime = field(default_factory=datetime.now)
    last_check: Optional[datetime] = None


@dataclass
class HealthAlert:
    """Алерт здоровья"""
    alert_id: str
    
    # Источник
    service_id: str = ""
    probe_id: str = ""
    
    # Статус
    severity: AlertSeverity = AlertSeverity.WARNING
    title: str = ""
    message: str = ""
    
    # Время
    timestamp: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    
    # Уведомления
    notified: bool = False


@dataclass
class SelfHealingAction:
    """Действие самовосстановления"""
    action_id: str
    name: str = ""
    
    # Триггер
    trigger_status: HealthStatus = HealthStatus.UNHEALTHY
    trigger_threshold: int = 3
    
    # Действие
    action_func: Optional[Callable] = None
    
    # Cooldown
    cooldown_seconds: int = 300
    last_executed: Optional[datetime] = None
    
    # Статистика
    execution_count: int = 0


class HealthChecker:
    """Проверщик здоровья"""
    
    async def check_http(self, endpoint: str, timeout: int = 5) -> HealthCheckResult:
        """HTTP проверка"""
        check_id = f"http_{uuid.uuid4().hex[:8]}"
        start = datetime.now()
        
        try:
            # Симуляция HTTP запроса
            await asyncio.sleep(random.uniform(0.01, 0.1))
            
            if random.random() < 0.9:  # 90% успех
                return HealthCheckResult(
                    check_id=check_id,
                    name=f"HTTP {endpoint}",
                    status=HealthStatus.HEALTHY,
                    message="OK",
                    details={"status_code": 200},
                    duration_ms=(datetime.now() - start).total_seconds() * 1000
                )
            else:
                raise Exception("Connection timeout")
                
        except Exception as e:
            return HealthCheckResult(
                check_id=check_id,
                name=f"HTTP {endpoint}",
                status=HealthStatus.UNHEALTHY,
                error=str(e),
                duration_ms=(datetime.now() - start).total_seconds() * 1000
            )
            
    async def check_tcp(self, host: str, port: int, timeout: int = 5) -> HealthCheckResult:
        """TCP проверка"""
        check_id = f"tcp_{uuid.uuid4().hex[:8]}"
        start = datetime.now()
        
        try:
            await asyncio.sleep(random.uniform(0.01, 0.05))
            
            if random.random() < 0.95:
                return HealthCheckResult(
                    check_id=check_id,
                    name=f"TCP {host}:{port}",
                    status=HealthStatus.HEALTHY,
                    message=f"Port {port} is open",
                    duration_ms=(datetime.now() - start).total_seconds() * 1000
                )
            else:
                raise Exception("Connection refused")
                
        except Exception as e:
            return HealthCheckResult(
                check_id=check_id,
                name=f"TCP {host}:{port}",
                status=HealthStatus.UNHEALTHY,
                error=str(e),
                duration_ms=(datetime.now() - start).total_seconds() * 1000
            )
            
    async def check_database(self, connection_string: str, timeout: int = 5) -> HealthCheckResult:
        """Database проверка"""
        check_id = f"db_{uuid.uuid4().hex[:8]}"
        start = datetime.now()
        
        try:
            await asyncio.sleep(random.uniform(0.02, 0.1))
            
            if random.random() < 0.85:
                return HealthCheckResult(
                    check_id=check_id,
                    name="Database",
                    status=HealthStatus.HEALTHY,
                    message="Database connection OK",
                    details={
                        "active_connections": random.randint(5, 50),
                        "max_connections": 100
                    },
                    duration_ms=(datetime.now() - start).total_seconds() * 1000
                )
            else:
                raise Exception("Database connection failed")
                
        except Exception as e:
            return HealthCheckResult(
                check_id=check_id,
                name="Database",
                status=HealthStatus.UNHEALTHY,
                error=str(e),
                duration_ms=(datetime.now() - start).total_seconds() * 1000
            )
            
    async def check_redis(self, host: str, port: int = 6379, timeout: int = 5) -> HealthCheckResult:
        """Redis проверка"""
        check_id = f"redis_{uuid.uuid4().hex[:8]}"
        start = datetime.now()
        
        try:
            await asyncio.sleep(random.uniform(0.01, 0.05))
            
            if random.random() < 0.95:
                return HealthCheckResult(
                    check_id=check_id,
                    name="Redis",
                    status=HealthStatus.HEALTHY,
                    message="PONG",
                    details={
                        "used_memory": f"{random.randint(100, 500)}MB",
                        "connected_clients": random.randint(5, 30)
                    },
                    duration_ms=(datetime.now() - start).total_seconds() * 1000
                )
            else:
                raise Exception("Redis connection timeout")
                
        except Exception as e:
            return HealthCheckResult(
                check_id=check_id,
                name="Redis",
                status=HealthStatus.UNHEALTHY,
                error=str(e),
                duration_ms=(datetime.now() - start).total_seconds() * 1000
            )


class HealthAggregator:
    """Агрегатор здоровья"""
    
    def aggregate(self, results: List[HealthCheckResult],
                   required_checks: Set[str] = None) -> HealthStatus:
        """Агрегация статусов"""
        if not results:
            return HealthStatus.UNKNOWN
            
        required_checks = required_checks or set()
        
        has_unhealthy = False
        has_degraded = False
        
        for result in results:
            if result.status == HealthStatus.UNHEALTHY:
                if result.check_id in required_checks or not required_checks:
                    has_unhealthy = True
                else:
                    has_degraded = True
            elif result.status == HealthStatus.DEGRADED:
                has_degraded = True
                
        if has_unhealthy:
            return HealthStatus.UNHEALTHY
        elif has_degraded:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY


class AlertManager:
    """Менеджер алертов"""
    
    def __init__(self):
        self.alerts: Dict[str, HealthAlert] = {}
        self.alert_history: List[HealthAlert] = []
        
    def create_alert(self, service_id: str, probe_id: str,
                      severity: AlertSeverity, title: str, message: str) -> HealthAlert:
        """Создание алерта"""
        alert_key = f"{service_id}:{probe_id}"
        
        # Проверяем активный алерт
        if alert_key in self.alerts:
            return self.alerts[alert_key]
            
        alert = HealthAlert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            service_id=service_id,
            probe_id=probe_id,
            severity=severity,
            title=title,
            message=message
        )
        
        self.alerts[alert_key] = alert
        return alert
        
    def resolve_alert(self, service_id: str, probe_id: str):
        """Разрешение алерта"""
        alert_key = f"{service_id}:{probe_id}"
        
        if alert_key in self.alerts:
            alert = self.alerts.pop(alert_key)
            alert.resolved_at = datetime.now()
            self.alert_history.append(alert)


class SelfHealingEngine:
    """Движок самовосстановления"""
    
    def __init__(self):
        self.actions: Dict[str, SelfHealingAction] = {}
        self.execution_log: List[Dict[str, Any]] = []
        
    def register_action(self, name: str, action_func: Callable,
                         trigger_status: HealthStatus = HealthStatus.UNHEALTHY,
                         trigger_threshold: int = 3,
                         cooldown: int = 300) -> SelfHealingAction:
        """Регистрация действия"""
        action = SelfHealingAction(
            action_id=f"action_{uuid.uuid4().hex[:8]}",
            name=name,
            action_func=action_func,
            trigger_status=trigger_status,
            trigger_threshold=trigger_threshold,
            cooldown_seconds=cooldown
        )
        self.actions[action.action_id] = action
        return action
        
    async def check_and_execute(self, service: ServiceHealth, probe: HealthProbe):
        """Проверка и выполнение действия"""
        now = datetime.now()
        
        for action in self.actions.values():
            # Проверяем статус
            if probe.status != action.trigger_status:
                continue
                
            # Проверяем threshold
            if probe.consecutive_failures < action.trigger_threshold:
                continue
                
            # Проверяем cooldown
            if action.last_executed:
                elapsed = (now - action.last_executed).total_seconds()
                if elapsed < action.cooldown_seconds:
                    continue
                    
            # Выполняем действие
            try:
                if action.action_func:
                    if asyncio.iscoroutinefunction(action.action_func):
                        await action.action_func(service, probe)
                    else:
                        action.action_func(service, probe)
                        
                action.last_executed = now
                action.execution_count += 1
                
                self.execution_log.append({
                    "action_id": action.action_id,
                    "action_name": action.name,
                    "service_id": service.service_id,
                    "probe_id": probe.probe_id,
                    "timestamp": now
                })
                
            except Exception as e:
                self.execution_log.append({
                    "action_id": action.action_id,
                    "error": str(e),
                    "timestamp": now
                })


class HealthCheckSystem:
    """Система проверки здоровья"""
    
    def __init__(self):
        self.services: Dict[str, ServiceHealth] = {}
        self.checker = HealthChecker()
        self.aggregator = HealthAggregator()
        self.alert_manager = AlertManager()
        self.self_healing = SelfHealingEngine()
        
        # Запущенные проверки
        self.running_checks: Dict[str, asyncio.Task] = {}
        
    def register_service(self, name: str, version: str = "1.0.0",
                          **metadata) -> ServiceHealth:
        """Регистрация сервиса"""
        service = ServiceHealth(
            service_id=f"svc_{uuid.uuid4().hex[:8]}",
            name=name,
            version=version,
            metadata=metadata
        )
        self.services[service.service_id] = service
        return service
        
    def add_probe(self, service_id: str, name: str,
                   probe_type: ProbeType = ProbeType.LIVENESS,
                   check_func: Callable = None,
                   interval: int = 30, timeout: int = 10,
                   failure_threshold: int = 3) -> HealthProbe:
        """Добавление проверки"""
        service = self.services.get(service_id)
        if not service:
            raise ValueError(f"Service {service_id} not found")
            
        probe = HealthProbe(
            probe_id=f"probe_{uuid.uuid4().hex[:8]}",
            name=name,
            probe_type=probe_type,
            check_func=check_func,
            interval_seconds=interval,
            timeout_seconds=timeout,
            failure_threshold=failure_threshold
        )
        
        service.probes[probe.probe_id] = probe
        return probe
        
    def add_dependency(self, service_id: str, name: str,
                        check_type: CheckType, endpoint: str,
                        required: bool = True, **params) -> DependencyCheck:
        """Добавление зависимости"""
        service = self.services.get(service_id)
        if not service:
            raise ValueError(f"Service {service_id} not found")
            
        dep = DependencyCheck(
            check_id=f"dep_{uuid.uuid4().hex[:8]}",
            name=name,
            check_type=check_type,
            endpoint=endpoint,
            required=required,
            params=params
        )
        
        service.dependencies[dep.check_id] = dep
        return dep
        
    async def run_probe(self, service_id: str, probe_id: str) -> HealthCheckResult:
        """Выполнение проверки"""
        service = self.services.get(service_id)
        if not service:
            raise ValueError(f"Service {service_id} not found")
            
        probe = service.probes.get(probe_id)
        if not probe:
            raise ValueError(f"Probe {probe_id} not found")
            
        # Выполняем проверку
        start = datetime.now()
        
        try:
            if probe.check_func:
                if asyncio.iscoroutinefunction(probe.check_func):
                    result = await asyncio.wait_for(
                        probe.check_func(),
                        timeout=probe.timeout_seconds
                    )
                else:
                    result = probe.check_func()
                    
                if isinstance(result, HealthCheckResult):
                    pass  # Уже правильный тип
                elif isinstance(result, bool):
                    result = HealthCheckResult(
                        check_id=probe.probe_id,
                        name=probe.name,
                        status=HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY,
                        duration_ms=(datetime.now() - start).total_seconds() * 1000
                    )
                else:
                    result = HealthCheckResult(
                        check_id=probe.probe_id,
                        name=probe.name,
                        status=HealthStatus.HEALTHY,
                        details={"result": result},
                        duration_ms=(datetime.now() - start).total_seconds() * 1000
                    )
            else:
                # Дефолтная проверка - всегда OK
                result = HealthCheckResult(
                    check_id=probe.probe_id,
                    name=probe.name,
                    status=HealthStatus.HEALTHY,
                    message="OK",
                    duration_ms=(datetime.now() - start).total_seconds() * 1000
                )
                
        except asyncio.TimeoutError:
            result = HealthCheckResult(
                check_id=probe.probe_id,
                name=probe.name,
                status=HealthStatus.UNHEALTHY,
                error=f"Timeout after {probe.timeout_seconds}s",
                duration_ms=probe.timeout_seconds * 1000
            )
        except Exception as e:
            result = HealthCheckResult(
                check_id=probe.probe_id,
                name=probe.name,
                status=HealthStatus.UNHEALTHY,
                error=str(e),
                duration_ms=(datetime.now() - start).total_seconds() * 1000
            )
            
        # Обновляем состояние
        probe.last_result = result
        
        if result.status == HealthStatus.HEALTHY:
            probe.consecutive_successes += 1
            probe.consecutive_failures = 0
            
            if probe.consecutive_successes >= probe.success_threshold:
                probe.status = HealthStatus.HEALTHY
                self.alert_manager.resolve_alert(service_id, probe_id)
        else:
            probe.consecutive_failures += 1
            probe.consecutive_successes = 0
            
            if probe.consecutive_failures >= probe.failure_threshold:
                probe.status = HealthStatus.UNHEALTHY
                
                # Создаём алерт
                self.alert_manager.create_alert(
                    service_id, probe_id,
                    AlertSeverity.CRITICAL,
                    f"Probe {probe.name} unhealthy",
                    result.error or result.message
                )
                
                # Проверяем self-healing
                await self.self_healing.check_and_execute(service, probe)
                
        # Добавляем в историю
        probe.history.append(result)
        if len(probe.history) > probe.history_limit:
            probe.history = probe.history[-probe.history_limit:]
            
        return result
        
    async def run_dependency_check(self, service_id: str,
                                     dep_id: str) -> HealthCheckResult:
        """Проверка зависимости"""
        service = self.services.get(service_id)
        if not service:
            raise ValueError(f"Service {service_id} not found")
            
        dep = service.dependencies.get(dep_id)
        if not dep:
            raise ValueError(f"Dependency {dep_id} not found")
            
        # Выбираем метод проверки
        if dep.check_type == CheckType.HTTP:
            result = await self.checker.check_http(dep.endpoint, dep.timeout_seconds)
        elif dep.check_type == CheckType.TCP:
            host, port = dep.endpoint.split(":")
            result = await self.checker.check_tcp(host, int(port), dep.timeout_seconds)
        elif dep.check_type == CheckType.DATABASE:
            result = await self.checker.check_database(dep.endpoint, dep.timeout_seconds)
        elif dep.check_type == CheckType.REDIS:
            parts = dep.endpoint.split(":")
            host = parts[0]
            port = int(parts[1]) if len(parts) > 1 else 6379
            result = await self.checker.check_redis(host, port, dep.timeout_seconds)
        else:
            result = HealthCheckResult(
                check_id=dep.check_id,
                name=dep.name,
                status=HealthStatus.UNKNOWN,
                message="Unknown check type"
            )
            
        dep.status = result.status
        dep.last_check = datetime.now()
        dep.response_time_ms = result.duration_ms
        
        if result.error:
            dep.last_error = result.error
            
        return result
        
    async def check_service(self, service_id: str) -> Dict[str, Any]:
        """Полная проверка сервиса"""
        service = self.services.get(service_id)
        if not service:
            raise ValueError(f"Service {service_id} not found")
            
        results = []
        
        # Проверяем все probes
        for probe_id in service.probes:
            result = await self.run_probe(service_id, probe_id)
            results.append(result)
            
        # Проверяем все зависимости
        for dep_id in service.dependencies:
            result = await self.run_dependency_check(service_id, dep_id)
            results.append(result)
            
        # Агрегируем статус
        required = set(
            d.check_id for d in service.dependencies.values() if d.required
        )
        service.status = self.aggregator.aggregate(results, required)
        service.last_check = datetime.now()
        
        return {
            "service_id": service_id,
            "name": service.name,
            "status": service.status.value,
            "probes": {
                pid: {"status": p.status.value, "consecutive_failures": p.consecutive_failures}
                for pid, p in service.probes.items()
            },
            "dependencies": {
                did: {"status": d.status.value, "response_time_ms": d.response_time_ms}
                for did, d in service.dependencies.items()
            }
        }
        
    def get_health_report(self) -> Dict[str, Any]:
        """Отчёт о здоровье"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "services": {},
            "summary": {
                "total": len(self.services),
                "healthy": 0,
                "degraded": 0,
                "unhealthy": 0
            },
            "alerts": {
                "active": len(self.alert_manager.alerts),
                "total": len(self.alert_manager.alert_history) + len(self.alert_manager.alerts)
            }
        }
        
        for sid, service in self.services.items():
            report["services"][service.name] = {
                "status": service.status.value,
                "probes": len(service.probes),
                "dependencies": len(service.dependencies)
            }
            
            if service.status == HealthStatus.HEALTHY:
                report["summary"]["healthy"] += 1
            elif service.status == HealthStatus.DEGRADED:
                report["summary"]["degraded"] += 1
            else:
                report["summary"]["unhealthy"] += 1
                
        return report
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_probes = sum(len(s.probes) for s in self.services.values())
        total_deps = sum(len(s.dependencies) for s in self.services.values())
        
        return {
            "services": len(self.services),
            "total_probes": total_probes,
            "total_dependencies": total_deps,
            "active_alerts": len(self.alert_manager.alerts),
            "self_healing_actions": len(self.self_healing.actions),
            "self_healing_executions": sum(a.execution_count for a in self.self_healing.actions.values())
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 94: Health Check System")
    print("=" * 60)
    
    async def demo():
        system = HealthCheckSystem()
        print("✓ Health Check System created")
        
        # Регистрация сервисов
        print("\n📦 Registering Services...")
        
        # API Gateway
        api_service = system.register_service(
            "api-gateway",
            version="2.1.0",
            environment="production",
            region="us-east-1"
        )
        
        # User Service
        user_service = system.register_service(
            "user-service",
            version="1.5.0"
        )
        
        # Order Service
        order_service = system.register_service(
            "order-service",
            version="1.3.0"
        )
        
        print(f"  ✓ {api_service.name} (v{api_service.version})")
        print(f"  ✓ {user_service.name} (v{user_service.version})")
        print(f"  ✓ {order_service.name} (v{order_service.version})")
        
        # Добавление probes
        print("\n🔍 Adding Health Probes...")
        
        # API Gateway probes
        async def api_liveness():
            await asyncio.sleep(0.01)
            return random.random() < 0.95  # 95% success
            
        async def api_readiness():
            await asyncio.sleep(0.02)
            # Проверяем memory и connections
            return HealthCheckResult(
                check_id="api_readiness",
                name="API Readiness",
                status=HealthStatus.HEALTHY if random.random() < 0.9 else HealthStatus.DEGRADED,
                details={
                    "memory_usage": f"{random.randint(40, 80)}%",
                    "active_connections": random.randint(100, 500)
                }
            )
            
        system.add_probe(
            api_service.service_id,
            "liveness",
            ProbeType.LIVENESS,
            api_liveness,
            interval=10,
            failure_threshold=3
        )
        
        system.add_probe(
            api_service.service_id,
            "readiness",
            ProbeType.READINESS,
            api_readiness,
            interval=30,
            failure_threshold=2
        )
        
        print(f"  ✓ {api_service.name}: liveness, readiness")
        
        # User Service probe
        system.add_probe(
            user_service.service_id,
            "liveness",
            ProbeType.LIVENESS,
            interval=15
        )
        
        print(f"  ✓ {user_service.name}: liveness")
        
        # Order Service probe
        system.add_probe(
            order_service.service_id,
            "liveness",
            ProbeType.LIVENESS,
            interval=15
        )
        
        print(f"  ✓ {order_service.name}: liveness")
        
        # Добавление зависимостей
        print("\n🔗 Adding Dependencies...")
        
        # API Gateway dependencies
        system.add_dependency(
            api_service.service_id,
            "PostgreSQL",
            CheckType.DATABASE,
            "postgresql://localhost:5432/api",
            required=True
        )
        
        system.add_dependency(
            api_service.service_id,
            "Redis Cache",
            CheckType.REDIS,
            "localhost:6379",
            required=False
        )
        
        system.add_dependency(
            api_service.service_id,
            "User Service",
            CheckType.HTTP,
            "http://user-service:8080/health",
            required=True
        )
        
        print(f"  ✓ {api_service.name}: PostgreSQL, Redis, User Service")
        
        # User Service dependencies
        system.add_dependency(
            user_service.service_id,
            "PostgreSQL",
            CheckType.DATABASE,
            "postgresql://localhost:5432/users",
            required=True
        )
        
        print(f"  ✓ {user_service.name}: PostgreSQL")
        
        # Order Service dependencies  
        system.add_dependency(
            order_service.service_id,
            "PostgreSQL",
            CheckType.DATABASE,
            "postgresql://localhost:5432/orders",
            required=True
        )
        
        system.add_dependency(
            order_service.service_id,
            "Kafka",
            CheckType.TCP,
            "localhost:9092",
            required=True
        )
        
        print(f"  ✓ {order_service.name}: PostgreSQL, Kafka")
        
        # Self-healing actions
        print("\n🔄 Registering Self-Healing Actions...")
        
        async def restart_service(service, probe):
            print(f"    🔄 Self-healing: Restarting {service.name}...")
            await asyncio.sleep(0.1)
            
        system.self_healing.register_action(
            "Restart Service",
            restart_service,
            trigger_status=HealthStatus.UNHEALTHY,
            trigger_threshold=3,
            cooldown=60
        )
        
        print(f"  ✓ Registered 'Restart Service' action")
        
        # Выполнение проверок
        print("\n⚡ Running Health Checks...")
        
        for service in system.services.values():
            result = await system.check_service(service.service_id)
            
            status_icon = {
                "healthy": "✅",
                "degraded": "⚠️",
                "unhealthy": "❌",
                "unknown": "❓"
            }.get(result["status"], "?")
            
            print(f"\n  {status_icon} {result['name']}: {result['status']}")
            
            # Probes
            for probe_id, probe_info in result["probes"].items():
                probe = service.probes[probe_id]
                probe_icon = "✅" if probe_info["status"] == "healthy" else "❌"
                print(f"     {probe_icon} Probe '{probe.name}': {probe_info['status']}")
                
            # Dependencies
            for dep_id, dep_info in result["dependencies"].items():
                dep = service.dependencies[dep_id]
                dep_icon = "✅" if dep_info["status"] == "healthy" else "❌"
                print(f"     {dep_icon} Dep '{dep.name}': {dep_info['status']} ({dep_info['response_time_ms']:.1f}ms)")
                
        # Выполняем несколько раундов проверок
        print("\n📊 Running Multiple Check Rounds...")
        
        for i in range(5):
            for service in system.services.values():
                await system.check_service(service.service_id)
                
        print(f"  ✓ Completed 5 rounds of checks")
        
        # Отчёт о здоровье
        print("\n📋 Health Report:")
        
        report = system.get_health_report()
        
        print(f"\n  Timestamp: {report['timestamp']}")
        print(f"\n  Summary:")
        print(f"    Total Services: {report['summary']['total']}")
        print(f"    Healthy:   {report['summary']['healthy']}")
        print(f"    Degraded:  {report['summary']['degraded']}")
        print(f"    Unhealthy: {report['summary']['unhealthy']}")
        
        print(f"\n  Services:")
        for name, info in report["services"].items():
            status_icon = {"healthy": "✅", "degraded": "⚠️", "unhealthy": "❌"}.get(info["status"], "?")
            print(f"    {status_icon} {name}: {info['status']}")
            print(f"       Probes: {info['probes']}, Dependencies: {info['dependencies']}")
            
        print(f"\n  Alerts:")
        print(f"    Active: {report['alerts']['active']}")
        print(f"    Total: {report['alerts']['total']}")
        
        # История проверок
        print("\n📜 Probe History (API Gateway Liveness):")
        
        api_liveness_probe = list(api_service.probes.values())[0]
        
        if api_liveness_probe.history:
            for result in api_liveness_probe.history[-5:]:
                status_icon = "✅" if result.status == HealthStatus.HEALTHY else "❌"
                print(f"  {status_icon} {result.timestamp.strftime('%H:%M:%S')} - {result.status.value} ({result.duration_ms:.1f}ms)")
                
        # Активные алерты
        print("\n🚨 Active Alerts:")
        
        if system.alert_manager.alerts:
            for alert_key, alert in system.alert_manager.alerts.items():
                severity_icon = {
                    AlertSeverity.INFO: "ℹ️",
                    AlertSeverity.WARNING: "⚠️",
                    AlertSeverity.CRITICAL: "🔥"
                }.get(alert.severity, "?")
                
                print(f"  {severity_icon} {alert.title}")
                print(f"     Service: {alert.service_id}")
                print(f"     Message: {alert.message}")
        else:
            print("  No active alerts")
            
        # Self-healing история
        print("\n🔄 Self-Healing Log:")
        
        if system.self_healing.execution_log:
            for log in system.self_healing.execution_log[-5:]:
                print(f"  → {log.get('action_name', 'Unknown')}")
                print(f"     Service: {log.get('service_id', 'N/A')}")
                print(f"     Time: {log.get('timestamp', 'N/A')}")
        else:
            print("  No self-healing actions executed")
            
        # Статистика
        print("\n📈 System Statistics:")
        
        stats = system.get_statistics()
        
        print(f"\n  Services: {stats['services']}")
        print(f"  Total Probes: {stats['total_probes']}")
        print(f"  Total Dependencies: {stats['total_dependencies']}")
        print(f"  Active Alerts: {stats['active_alerts']}")
        print(f"  Self-Healing Actions: {stats['self_healing_actions']}")
        print(f"  Self-Healing Executions: {stats['self_healing_executions']}")
        
        # Dashboard
        print("\n📋 Health Check Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │              Health Check Overview                          │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Services:      {stats['services']:>6}                                │")
        print(f"  │ Probes:        {stats['total_probes']:>6}                                │")
        print(f"  │ Dependencies:  {stats['total_dependencies']:>6}                                │")
        print(f"  │ Active Alerts: {stats['active_alerts']:>6}                                │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Health Check System initialized!")
    print("=" * 60)
