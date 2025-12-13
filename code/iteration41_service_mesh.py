#!/usr/bin/env python3
"""
Server Init - Iteration 41: Service Mesh & Traffic Management
Сервисная сетка и управление трафиком

Функционал:
- Service Mesh Control Plane - управляющая плоскость сервисной сетки
- Traffic Management - управление трафиком (canary, blue-green, A/B)
- mTLS & Security Policies - взаимный TLS и политики безопасности
- Circuit Breaker & Retry - автоматические выключатели и повторы
- Load Balancing - балансировка нагрузки
- Observability Integration - интеграция наблюдаемости
- Rate Limiting & Quotas - ограничение скорости и квоты
- Multi-Cluster Mesh - многокластерная сетка
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


class LoadBalancerAlgorithm(Enum):
    """Алгоритм балансировки"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"
    WEIGHTED = "weighted"
    CONSISTENT_HASH = "consistent_hash"
    MAGLEV = "maglev"


class TrafficPolicy(Enum):
    """Политика трафика"""
    CANARY = "canary"
    BLUE_GREEN = "blue_green"
    AB_TEST = "ab_test"
    MIRROR = "mirror"
    HEADER_BASED = "header_based"


class TLSMode(Enum):
    """Режим TLS"""
    DISABLED = "disabled"
    PERMISSIVE = "permissive"
    STRICT = "strict"
    MUTUAL = "mutual"


class CircuitState(Enum):
    """Состояние circuit breaker"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class ServiceEndpoint:
    """Эндпоинт сервиса"""
    endpoint_id: str
    address: str
    port: int
    
    # Метаданные
    version: str = "v1"
    zone: str = ""
    weight: int = 100
    
    # Состояние
    healthy: bool = True
    last_check: datetime = field(default_factory=datetime.now)
    active_connections: int = 0
    
    # Метрики
    request_count: int = 0
    error_count: int = 0
    latency_sum_ms: float = 0.0


@dataclass
class VirtualService:
    """Виртуальный сервис"""
    service_id: str
    name: str
    namespace: str = "default"
    
    # Хосты
    hosts: List[str] = field(default_factory=list)
    
    # Маршруты
    routes: List[Dict[str, Any]] = field(default_factory=list)
    
    # Таймауты
    timeout_ms: int = 30000
    retries: int = 3
    retry_on: List[str] = field(default_factory=lambda: ["5xx", "reset", "connect-failure"])
    
    # Fault injection
    fault_injection: Optional[Dict[str, Any]] = None
    
    # Mirror
    mirror: Optional[Dict[str, Any]] = None
    
    # Метаданные
    labels: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DestinationRule:
    """Правило назначения"""
    rule_id: str
    host: str
    
    # TLS настройки
    tls_mode: TLSMode = TLSMode.MUTUAL
    
    # Балансировка
    load_balancer: LoadBalancerAlgorithm = LoadBalancerAlgorithm.ROUND_ROBIN
    
    # Connection pool
    max_connections: int = 1000
    max_pending_requests: int = 100
    max_requests_per_connection: int = 100
    
    # Circuit breaker
    circuit_breaker_enabled: bool = True
    consecutive_errors: int = 5
    interval_seconds: int = 30
    base_ejection_time_seconds: int = 30
    max_ejection_percent: int = 50
    
    # Subsets (versions)
    subsets: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class AuthorizationPolicy:
    """Политика авторизации"""
    policy_id: str
    name: str
    namespace: str = "default"
    
    # Selector
    selector: Dict[str, str] = field(default_factory=dict)
    
    # Action
    action: str = "ALLOW"  # ALLOW, DENY, CUSTOM
    
    # Rules
    rules: List[Dict[str, Any]] = field(default_factory=list)
    
    # Provider (для CUSTOM)
    provider: Optional[str] = None


@dataclass
class RateLimitConfig:
    """Конфигурация rate limiting"""
    config_id: str
    name: str
    
    # Лимиты
    requests_per_unit: int = 100
    unit: str = "SECOND"  # SECOND, MINUTE, HOUR, DAY
    
    # Правила
    rules: List[Dict[str, Any]] = field(default_factory=list)
    
    # Действие при превышении
    overflow_action: str = "REJECT"  # REJECT, QUEUE


@dataclass
class CircuitBreaker:
    """Circuit Breaker"""
    breaker_id: str
    service: str
    
    # Состояние
    state: CircuitState = CircuitState.CLOSED
    
    # Конфигурация
    failure_threshold: int = 5
    success_threshold: int = 3
    timeout_seconds: int = 30
    half_open_requests: int = 3
    
    # Счётчики
    failure_count: int = 0
    success_count: int = 0
    half_open_success: int = 0
    
    # Время
    last_failure: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    
    def record_success(self):
        """Запись успеха"""
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_success += 1
            if self.half_open_success >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.half_open_success = 0
        elif self.state == CircuitState.CLOSED:
            self.success_count += 1
            
    def record_failure(self):
        """Запись сбоя"""
        self.failure_count += 1
        self.last_failure = datetime.now()
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.opened_at = datetime.now()
        elif self.state == CircuitState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                self.opened_at = datetime.now()
                
    def check_state(self) -> CircuitState:
        """Проверка состояния"""
        if self.state == CircuitState.OPEN:
            if self.opened_at:
                elapsed = (datetime.now() - self.opened_at).total_seconds()
                if elapsed >= self.timeout_seconds:
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_success = 0
                    
        return self.state
        
    def allow_request(self) -> bool:
        """Разрешить запрос?"""
        state = self.check_state()
        
        if state == CircuitState.CLOSED:
            return True
        elif state == CircuitState.OPEN:
            return False
        else:  # HALF_OPEN
            return self.half_open_success < self.half_open_requests


@dataclass
class TrafficRoute:
    """Маршрут трафика"""
    route_id: str
    name: str
    
    # Матчинг
    match_conditions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Destination
    destinations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Веса
    weights: Dict[str, int] = field(default_factory=dict)
    
    # Политика
    policy: TrafficPolicy = TrafficPolicy.CANARY


class ServiceRegistry:
    """Реестр сервисов"""
    
    def __init__(self):
        self.services: Dict[str, Dict[str, Any]] = {}
        self.endpoints: Dict[str, List[ServiceEndpoint]] = defaultdict(list)
        
    def register_service(self, service_name: str, metadata: Dict[str, Any] = None):
        """Регистрация сервиса"""
        self.services[service_name] = {
            "name": service_name,
            "metadata": metadata or {},
            "registered_at": datetime.now().isoformat()
        }
        
    def register_endpoint(self, service_name: str, endpoint: ServiceEndpoint):
        """Регистрация эндпоинта"""
        self.endpoints[service_name].append(endpoint)
        
    def deregister_endpoint(self, service_name: str, endpoint_id: str):
        """Удаление эндпоинта"""
        self.endpoints[service_name] = [
            ep for ep in self.endpoints[service_name]
            if ep.endpoint_id != endpoint_id
        ]
        
    def get_healthy_endpoints(self, service_name: str, 
                               version: Optional[str] = None) -> List[ServiceEndpoint]:
        """Получение здоровых эндпоинтов"""
        endpoints = self.endpoints.get(service_name, [])
        healthy = [ep for ep in endpoints if ep.healthy]
        
        if version:
            healthy = [ep for ep in healthy if ep.version == version]
            
        return healthy
        
    def update_endpoint_health(self, service_name: str, endpoint_id: str, 
                                healthy: bool):
        """Обновление здоровья эндпоинта"""
        for ep in self.endpoints.get(service_name, []):
            if ep.endpoint_id == endpoint_id:
                ep.healthy = healthy
                ep.last_check = datetime.now()
                break


class LoadBalancer:
    """Балансировщик нагрузки"""
    
    def __init__(self, algorithm: LoadBalancerAlgorithm = LoadBalancerAlgorithm.ROUND_ROBIN):
        self.algorithm = algorithm
        self.round_robin_index: Dict[str, int] = defaultdict(int)
        self.connection_counts: Dict[str, int] = defaultdict(int)
        
    def select_endpoint(self, endpoints: List[ServiceEndpoint],
                        key: Optional[str] = None) -> Optional[ServiceEndpoint]:
        """Выбор эндпоинта"""
        if not endpoints:
            return None
            
        if self.algorithm == LoadBalancerAlgorithm.ROUND_ROBIN:
            return self._round_robin(endpoints)
        elif self.algorithm == LoadBalancerAlgorithm.LEAST_CONNECTIONS:
            return self._least_connections(endpoints)
        elif self.algorithm == LoadBalancerAlgorithm.RANDOM:
            return self._random(endpoints)
        elif self.algorithm == LoadBalancerAlgorithm.WEIGHTED:
            return self._weighted(endpoints)
        elif self.algorithm == LoadBalancerAlgorithm.CONSISTENT_HASH:
            return self._consistent_hash(endpoints, key)
        else:
            return self._round_robin(endpoints)
            
    def _round_robin(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Round Robin"""
        key = "_".join(ep.endpoint_id for ep in endpoints)
        idx = self.round_robin_index[key] % len(endpoints)
        self.round_robin_index[key] += 1
        return endpoints[idx]
        
    def _least_connections(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Least Connections"""
        return min(endpoints, key=lambda ep: ep.active_connections)
        
    def _random(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Random"""
        return random.choice(endpoints)
        
    def _weighted(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Weighted Random"""
        total_weight = sum(ep.weight for ep in endpoints)
        r = random.randint(0, total_weight - 1)
        
        cumulative = 0
        for ep in endpoints:
            cumulative += ep.weight
            if r < cumulative:
                return ep
                
        return endpoints[-1]
        
    def _consistent_hash(self, endpoints: List[ServiceEndpoint],
                          key: Optional[str]) -> ServiceEndpoint:
        """Consistent Hash"""
        if not key:
            return self._random(endpoints)
            
        hash_val = int(hashlib.md5(key.encode()).hexdigest(), 16)
        idx = hash_val % len(endpoints)
        return endpoints[idx]


class TrafficManager:
    """Менеджер трафика"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.routes: Dict[str, TrafficRoute] = {}
        self.active_deployments: Dict[str, Dict[str, Any]] = {}
        
    def create_route(self, route: TrafficRoute) -> str:
        """Создание маршрута"""
        self.routes[route.route_id] = route
        return route.route_id
        
    def apply_canary(self, service: str, stable_version: str, 
                     canary_version: str, canary_percent: int) -> Dict[str, Any]:
        """Применение канареечного развёртывания"""
        deployment_id = f"canary_{service}_{int(time.time())}"
        
        route = TrafficRoute(
            route_id=f"route_{deployment_id}",
            name=f"Canary: {service}",
            policy=TrafficPolicy.CANARY,
            destinations=[
                {"version": stable_version, "weight": 100 - canary_percent},
                {"version": canary_version, "weight": canary_percent}
            ],
            weights={
                stable_version: 100 - canary_percent,
                canary_version: canary_percent
            }
        )
        
        self.routes[route.route_id] = route
        self.active_deployments[deployment_id] = {
            "type": "canary",
            "service": service,
            "stable": stable_version,
            "canary": canary_version,
            "percent": canary_percent,
            "route_id": route.route_id,
            "started_at": datetime.now().isoformat()
        }
        
        return {
            "deployment_id": deployment_id,
            "status": "active",
            "route_id": route.route_id
        }
        
    def apply_blue_green(self, service: str, blue_version: str,
                          green_version: str, active: str = "blue") -> Dict[str, Any]:
        """Применение blue-green развёртывания"""
        deployment_id = f"bluegreen_{service}_{int(time.time())}"
        
        active_version = blue_version if active == "blue" else green_version
        
        route = TrafficRoute(
            route_id=f"route_{deployment_id}",
            name=f"Blue-Green: {service}",
            policy=TrafficPolicy.BLUE_GREEN,
            destinations=[{"version": active_version, "weight": 100}],
            weights={active_version: 100}
        )
        
        self.routes[route.route_id] = route
        self.active_deployments[deployment_id] = {
            "type": "blue_green",
            "service": service,
            "blue": blue_version,
            "green": green_version,
            "active": active,
            "route_id": route.route_id,
            "started_at": datetime.now().isoformat()
        }
        
        return {
            "deployment_id": deployment_id,
            "status": "active",
            "active_version": active_version
        }
        
    def switch_blue_green(self, deployment_id: str) -> Dict[str, Any]:
        """Переключение blue-green"""
        deployment = self.active_deployments.get(deployment_id)
        if not deployment or deployment["type"] != "blue_green":
            return {"error": "Deployment not found"}
            
        current = deployment["active"]
        new_active = "green" if current == "blue" else "blue"
        
        new_version = deployment["green"] if new_active == "green" else deployment["blue"]
        
        route = self.routes.get(deployment["route_id"])
        if route:
            route.destinations = [{"version": new_version, "weight": 100}]
            route.weights = {new_version: 100}
            
        deployment["active"] = new_active
        
        return {
            "deployment_id": deployment_id,
            "switched_to": new_active,
            "active_version": new_version
        }
        
    def update_canary_weight(self, deployment_id: str, 
                              new_percent: int) -> Dict[str, Any]:
        """Обновление веса канарейки"""
        deployment = self.active_deployments.get(deployment_id)
        if not deployment or deployment["type"] != "canary":
            return {"error": "Canary deployment not found"}
            
        deployment["percent"] = new_percent
        
        route = self.routes.get(deployment["route_id"])
        if route:
            stable = deployment["stable"]
            canary = deployment["canary"]
            route.weights = {
                stable: 100 - new_percent,
                canary: new_percent
            }
            route.destinations = [
                {"version": stable, "weight": 100 - new_percent},
                {"version": canary, "weight": new_percent}
            ]
            
        return {
            "deployment_id": deployment_id,
            "stable_weight": 100 - new_percent,
            "canary_weight": new_percent
        }
        
    def route_request(self, service: str, headers: Dict[str, str] = None,
                       source_ip: str = None) -> Optional[str]:
        """Маршрутизация запроса"""
        # Поиск активного маршрута
        for route in self.routes.values():
            if service in route.name:
                # Header-based routing
                if route.match_conditions:
                    for condition in route.match_conditions:
                        header_name = condition.get("header")
                        header_value = condition.get("value")
                        if headers and headers.get(header_name) == header_value:
                            return condition.get("destination")
                            
                # Weight-based routing
                if route.weights:
                    r = random.randint(0, 99)
                    cumulative = 0
                    for version, weight in route.weights.items():
                        cumulative += weight
                        if r < cumulative:
                            return version
                            
        return None


class MTLSManager:
    """Менеджер mTLS"""
    
    def __init__(self):
        self.certificates: Dict[str, Dict[str, Any]] = {}
        self.policies: Dict[str, Dict[str, Any]] = {}
        
    def issue_certificate(self, service: str, namespace: str = "default") -> Dict[str, Any]:
        """Выпуск сертификата"""
        cert_id = f"cert_{service}_{namespace}_{int(time.time())}"
        
        cert = {
            "cert_id": cert_id,
            "service": service,
            "namespace": namespace,
            "spiffe_id": f"spiffe://cluster.local/ns/{namespace}/sa/{service}",
            "issued_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=365)).isoformat(),
            "public_key": f"-----BEGIN CERTIFICATE-----\n{hashlib.sha256(cert_id.encode()).hexdigest()}\n-----END CERTIFICATE-----"
        }
        
        self.certificates[cert_id] = cert
        return cert
        
    def set_tls_policy(self, namespace: str, mode: TLSMode,
                        selector: Dict[str, str] = None) -> Dict[str, Any]:
        """Установка TLS политики"""
        policy_id = f"tls_{namespace}_{int(time.time())}"
        
        policy = {
            "policy_id": policy_id,
            "namespace": namespace,
            "mode": mode.value,
            "selector": selector or {},
            "created_at": datetime.now().isoformat()
        }
        
        self.policies[policy_id] = policy
        return policy
        
    def verify_mtls(self, source_service: str, target_service: str,
                     source_cert: str, target_cert: str) -> Dict[str, Any]:
        """Проверка mTLS"""
        source = self.certificates.get(source_cert)
        target = self.certificates.get(target_cert)
        
        if not source or not target:
            return {
                "verified": False,
                "error": "Certificate not found"
            }
            
        # Проверка срока действия
        source_expires = datetime.fromisoformat(source["expires_at"])
        target_expires = datetime.fromisoformat(target["expires_at"])
        
        if datetime.now() > source_expires or datetime.now() > target_expires:
            return {
                "verified": False,
                "error": "Certificate expired"
            }
            
        return {
            "verified": True,
            "source_spiffe": source["spiffe_id"],
            "target_spiffe": target["spiffe_id"],
            "verified_at": datetime.now().isoformat()
        }


class RateLimiter:
    """Rate Limiter"""
    
    def __init__(self):
        self.configs: Dict[str, RateLimitConfig] = {}
        self.counters: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "count": 0,
            "window_start": time.time()
        })
        
    def add_config(self, config: RateLimitConfig):
        """Добавление конфигурации"""
        self.configs[config.config_id] = config
        
    def check_limit(self, config_id: str, key: str) -> Tuple[bool, Dict[str, Any]]:
        """Проверка лимита"""
        config = self.configs.get(config_id)
        if not config:
            return True, {"error": "Config not found"}
            
        counter_key = f"{config_id}:{key}"
        counter = self.counters[counter_key]
        
        # Получение длины окна
        window_seconds = {
            "SECOND": 1,
            "MINUTE": 60,
            "HOUR": 3600,
            "DAY": 86400
        }.get(config.unit, 60)
        
        current_time = time.time()
        
        # Проверка окна
        if current_time - counter["window_start"] >= window_seconds:
            counter["count"] = 0
            counter["window_start"] = current_time
            
        # Проверка лимита
        if counter["count"] >= config.requests_per_unit:
            return False, {
                "allowed": False,
                "limit": config.requests_per_unit,
                "remaining": 0,
                "reset_at": counter["window_start"] + window_seconds
            }
            
        counter["count"] += 1
        
        return True, {
            "allowed": True,
            "limit": config.requests_per_unit,
            "remaining": config.requests_per_unit - counter["count"],
            "reset_at": counter["window_start"] + window_seconds
        }


class AuthorizationEngine:
    """Движок авторизации"""
    
    def __init__(self):
        self.policies: Dict[str, AuthorizationPolicy] = {}
        
    def add_policy(self, policy: AuthorizationPolicy):
        """Добавление политики"""
        self.policies[policy.policy_id] = policy
        
    def check_authorization(self, source: str, target: str,
                             operation: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Проверка авторизации"""
        context = context or {}
        
        # Поиск применимых политик
        applicable_policies = []
        for policy in self.policies.values():
            # Проверка selector
            if self._matches_selector(target, policy.selector):
                applicable_policies.append(policy)
                
        if not applicable_policies:
            return {
                "allowed": True,
                "reason": "No policies defined"
            }
            
        # Проверка правил
        for policy in applicable_policies:
            result = self._evaluate_policy(policy, source, target, operation, context)
            
            if policy.action == "DENY" and result:
                return {
                    "allowed": False,
                    "reason": f"Denied by policy: {policy.name}",
                    "policy_id": policy.policy_id
                }
            elif policy.action == "ALLOW" and result:
                return {
                    "allowed": True,
                    "reason": f"Allowed by policy: {policy.name}",
                    "policy_id": policy.policy_id
                }
                
        return {
            "allowed": False,
            "reason": "No matching allow policy"
        }
        
    def _matches_selector(self, target: str, selector: Dict[str, str]) -> bool:
        """Проверка соответствия селектору"""
        if not selector:
            return True
        # Упрощённая проверка
        return selector.get("service") == target or not selector.get("service")
        
    def _evaluate_policy(self, policy: AuthorizationPolicy, source: str,
                          target: str, operation: str, context: Dict[str, Any]) -> bool:
        """Оценка политики"""
        for rule in policy.rules:
            # Проверка source
            sources = rule.get("from", [])
            if sources and not any(self._matches_principal(source, s) for s in sources):
                continue
                
            # Проверка operation
            operations = rule.get("to", [])
            if operations and operation not in [o.get("operation") for o in operations]:
                continue
                
            # Проверка conditions
            conditions = rule.get("when", [])
            if conditions and not all(self._check_condition(c, context) for c in conditions):
                continue
                
            return True
            
        return False
        
    def _matches_principal(self, source: str, principal: Dict[str, Any]) -> bool:
        """Проверка principal"""
        principals = principal.get("source", {}).get("principals", [])
        if not principals:
            return True
        return source in principals or "*" in principals
        
    def _check_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Проверка условия"""
        key = condition.get("key", "")
        values = condition.get("values", [])
        actual = context.get(key)
        return actual in values if values else True


class SidecarProxy:
    """Sidecar Proxy (Envoy-like)"""
    
    def __init__(self, service_name: str, registry: ServiceRegistry):
        self.service_name = service_name
        self.registry = registry
        self.load_balancer = LoadBalancer()
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.rate_limiter = RateLimiter()
        
        # Метрики
        self.metrics = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_failed": 0,
            "latency_sum_ms": 0.0,
            "active_connections": 0
        }
        
    async def handle_request(self, target_service: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка запроса"""
        start_time = time.time()
        self.metrics["requests_total"] += 1
        self.metrics["active_connections"] += 1
        
        try:
            # 1. Rate limiting
            allowed, rate_info = self.rate_limiter.check_limit(
                f"limit_{target_service}",
                request.get("client_ip", "default")
            )
            
            if not allowed:
                self.metrics["requests_failed"] += 1
                return {
                    "status": 429,
                    "error": "Rate limit exceeded",
                    "rate_limit": rate_info
                }
                
            # 2. Circuit breaker check
            breaker = self.circuit_breakers.get(target_service)
            if breaker and not breaker.allow_request():
                self.metrics["requests_failed"] += 1
                return {
                    "status": 503,
                    "error": "Circuit breaker open",
                    "retry_after": breaker.timeout_seconds
                }
                
            # 3. Get healthy endpoints
            endpoints = self.registry.get_healthy_endpoints(target_service)
            if not endpoints:
                self.metrics["requests_failed"] += 1
                return {
                    "status": 503,
                    "error": "No healthy endpoints"
                }
                
            # 4. Load balancing
            endpoint = self.load_balancer.select_endpoint(
                endpoints,
                key=request.get("session_id")
            )
            
            # 5. Forward request (simulated)
            response = await self._forward_request(endpoint, request)
            
            # 6. Update metrics and circuit breaker
            if response.get("status", 500) < 500:
                self.metrics["requests_success"] += 1
                if breaker:
                    breaker.record_success()
            else:
                self.metrics["requests_failed"] += 1
                if breaker:
                    breaker.record_failure()
                    
            # 7. Record latency
            latency = (time.time() - start_time) * 1000
            self.metrics["latency_sum_ms"] += latency
            endpoint.latency_sum_ms += latency
            endpoint.request_count += 1
            
            response["latency_ms"] = latency
            return response
            
        finally:
            self.metrics["active_connections"] -= 1
            
    async def _forward_request(self, endpoint: ServiceEndpoint,
                                request: Dict[str, Any]) -> Dict[str, Any]:
        """Пересылка запроса (симуляция)"""
        # Симуляция задержки
        await asyncio.sleep(random.uniform(0.001, 0.05))
        
        # Симуляция результата
        if random.random() < 0.95:  # 95% успеха
            return {
                "status": 200,
                "endpoint": f"{endpoint.address}:{endpoint.port}",
                "data": {"message": "success"}
            }
        else:
            endpoint.error_count += 1
            return {
                "status": 500,
                "endpoint": f"{endpoint.address}:{endpoint.port}",
                "error": "Internal server error"
            }
            
    def get_metrics(self) -> Dict[str, Any]:
        """Получение метрик"""
        avg_latency = (
            self.metrics["latency_sum_ms"] / self.metrics["requests_total"]
            if self.metrics["requests_total"] > 0 else 0
        )
        
        return {
            "service": self.service_name,
            "requests": {
                "total": self.metrics["requests_total"],
                "success": self.metrics["requests_success"],
                "failed": self.metrics["requests_failed"],
                "success_rate": (
                    self.metrics["requests_success"] / self.metrics["requests_total"] * 100
                    if self.metrics["requests_total"] > 0 else 0
                )
            },
            "latency": {
                "avg_ms": avg_latency
            },
            "connections": {
                "active": self.metrics["active_connections"]
            }
        }


class ServiceMeshControlPlane:
    """Control Plane сервисной сетки"""
    
    def __init__(self):
        self.registry = ServiceRegistry()
        self.traffic_manager = TrafficManager(self.registry)
        self.mtls_manager = MTLSManager()
        self.rate_limiter = RateLimiter()
        self.auth_engine = AuthorizationEngine()
        
        # Конфигурации
        self.virtual_services: Dict[str, VirtualService] = {}
        self.destination_rules: Dict[str, DestinationRule] = {}
        
        # Proxies
        self.proxies: Dict[str, SidecarProxy] = {}
        
    def register_service(self, service_name: str, endpoints: List[Dict[str, Any]],
                          metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Регистрация сервиса в mesh"""
        self.registry.register_service(service_name, metadata)
        
        # Регистрация эндпоинтов
        for ep_data in endpoints:
            endpoint = ServiceEndpoint(
                endpoint_id=ep_data.get("id", f"ep_{uuid.uuid4().hex[:8]}"),
                address=ep_data.get("address", "127.0.0.1"),
                port=ep_data.get("port", 8080),
                version=ep_data.get("version", "v1"),
                zone=ep_data.get("zone", ""),
                weight=ep_data.get("weight", 100)
            )
            self.registry.register_endpoint(service_name, endpoint)
            
        # Выпуск сертификата
        cert = self.mtls_manager.issue_certificate(service_name)
        
        # Создание sidecar proxy
        proxy = SidecarProxy(service_name, self.registry)
        self.proxies[service_name] = proxy
        
        return {
            "service": service_name,
            "endpoints_registered": len(endpoints),
            "certificate_id": cert["cert_id"],
            "proxy_created": True
        }
        
    def apply_virtual_service(self, vs: VirtualService) -> str:
        """Применение VirtualService"""
        self.virtual_services[vs.service_id] = vs
        return vs.service_id
        
    def apply_destination_rule(self, dr: DestinationRule) -> str:
        """Применение DestinationRule"""
        self.destination_rules[dr.rule_id] = dr
        
        # Настройка circuit breaker
        if dr.circuit_breaker_enabled:
            breaker = CircuitBreaker(
                breaker_id=f"cb_{dr.host}",
                service=dr.host,
                failure_threshold=dr.consecutive_errors,
                timeout_seconds=dr.base_ejection_time_seconds
            )
            
            proxy = self.proxies.get(dr.host)
            if proxy:
                proxy.circuit_breakers[dr.host] = breaker
                
        return dr.rule_id
        
    def apply_authorization_policy(self, policy: AuthorizationPolicy) -> str:
        """Применение AuthorizationPolicy"""
        self.auth_engine.add_policy(policy)
        return policy.policy_id
        
    def apply_rate_limit(self, config: RateLimitConfig) -> str:
        """Применение rate limit"""
        self.rate_limiter.add_config(config)
        
        # Применение к proxies
        for proxy in self.proxies.values():
            proxy.rate_limiter.add_config(config)
            
        return config.config_id
        
    def get_mesh_status(self) -> Dict[str, Any]:
        """Статус mesh"""
        return {
            "services": len(self.registry.services),
            "total_endpoints": sum(
                len(eps) for eps in self.registry.endpoints.values()
            ),
            "healthy_endpoints": sum(
                len([ep for ep in eps if ep.healthy])
                for eps in self.registry.endpoints.values()
            ),
            "virtual_services": len(self.virtual_services),
            "destination_rules": len(self.destination_rules),
            "certificates": len(self.mtls_manager.certificates),
            "authorization_policies": len(self.auth_engine.policies),
            "active_deployments": len(self.traffic_manager.active_deployments)
        }
        
    def get_service_metrics(self, service_name: str) -> Dict[str, Any]:
        """Метрики сервиса"""
        proxy = self.proxies.get(service_name)
        if not proxy:
            return {"error": "Service not found"}
            
        return proxy.get_metrics()


class MultiClusterMesh:
    """Многокластерная сетка"""
    
    def __init__(self):
        self.clusters: Dict[str, ServiceMeshControlPlane] = {}
        self.federation_rules: List[Dict[str, Any]] = []
        
    def add_cluster(self, cluster_name: str) -> ServiceMeshControlPlane:
        """Добавление кластера"""
        mesh = ServiceMeshControlPlane()
        self.clusters[cluster_name] = mesh
        return mesh
        
    def federate_service(self, service_name: str, 
                          source_cluster: str, target_cluster: str) -> Dict[str, Any]:
        """Федерация сервиса между кластерами"""
        rule = {
            "service": service_name,
            "source": source_cluster,
            "target": target_cluster,
            "created_at": datetime.now().isoformat()
        }
        
        self.federation_rules.append(rule)
        
        return {
            "federated": True,
            "service": service_name,
            "source_cluster": source_cluster,
            "target_cluster": target_cluster
        }
        
    def get_global_status(self) -> Dict[str, Any]:
        """Глобальный статус"""
        return {
            "clusters": len(self.clusters),
            "federation_rules": len(self.federation_rules),
            "cluster_status": {
                name: mesh.get_mesh_status()
                for name, mesh in self.clusters.items()
            }
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 41: Service Mesh")
    print("=" * 60)
    
    async def demo():
        # Создание control plane
        mesh = ServiceMeshControlPlane()
        print("✓ Service Mesh Control Plane created")
        
        # Регистрация сервисов
        services = [
            {
                "name": "api-gateway",
                "endpoints": [
                    {"id": "api-1", "address": "10.0.1.1", "port": 8080, "version": "v1"},
                    {"id": "api-2", "address": "10.0.1.2", "port": 8080, "version": "v1"},
                    {"id": "api-3", "address": "10.0.1.3", "port": 8080, "version": "v2"}
                ]
            },
            {
                "name": "user-service",
                "endpoints": [
                    {"id": "user-1", "address": "10.0.2.1", "port": 8081, "version": "v1"},
                    {"id": "user-2", "address": "10.0.2.2", "port": 8081, "version": "v1"}
                ]
            },
            {
                "name": "order-service",
                "endpoints": [
                    {"id": "order-1", "address": "10.0.3.1", "port": 8082, "version": "v1"},
                    {"id": "order-2", "address": "10.0.3.2", "port": 8082, "version": "v2"}
                ]
            }
        ]
        
        for svc in services:
            result = mesh.register_service(svc["name"], svc["endpoints"])
            print(f"  Registered: {svc['name']} ({result['endpoints_registered']} endpoints)")
            
        # Применение VirtualService
        vs = VirtualService(
            service_id="vs_api_gateway",
            name="api-gateway",
            hosts=["api.example.com"],
            timeout_ms=30000,
            retries=3
        )
        mesh.apply_virtual_service(vs)
        print(f"\n✓ Applied VirtualService: {vs.name}")
        
        # Применение DestinationRule с circuit breaker
        dr = DestinationRule(
            rule_id="dr_user_service",
            host="user-service",
            tls_mode=TLSMode.MUTUAL,
            load_balancer=LoadBalancerAlgorithm.LEAST_CONNECTIONS,
            circuit_breaker_enabled=True,
            consecutive_errors=5,
            base_ejection_time_seconds=30
        )
        mesh.apply_destination_rule(dr)
        print(f"✓ Applied DestinationRule with Circuit Breaker")
        
        # Rate Limiting
        rate_config = RateLimitConfig(
            config_id="rate_api",
            name="API Rate Limit",
            requests_per_unit=100,
            unit="SECOND"
        )
        mesh.apply_rate_limit(rate_config)
        print(f"✓ Applied Rate Limit: {rate_config.requests_per_unit}/sec")
        
        # Authorization Policy
        auth_policy = AuthorizationPolicy(
            policy_id="auth_user_service",
            name="user-service-policy",
            action="ALLOW",
            rules=[
                {
                    "from": [{"source": {"principals": ["api-gateway"]}}],
                    "to": [{"operation": "GET"}, {"operation": "POST"}]
                }
            ]
        )
        mesh.apply_authorization_policy(auth_policy)
        print(f"✓ Applied Authorization Policy")
        
        # Canary Deployment
        print(f"\n🚀 Starting Canary Deployment...")
        canary = mesh.traffic_manager.apply_canary(
            "order-service", 
            stable_version="v1",
            canary_version="v2",
            canary_percent=10
        )
        print(f"  Deployment ID: {canary['deployment_id']}")
        print(f"  Traffic split: v1=90%, v2=10%")
        
        # Увеличение веса канарейки
        mesh.traffic_manager.update_canary_weight(canary['deployment_id'], 30)
        print(f"  Updated: v1=70%, v2=30%")
        
        # Симуляция запросов
        print(f"\n📊 Simulating traffic...")
        proxy = mesh.proxies.get("api-gateway")
        
        for i in range(50):
            response = await proxy.handle_request(
                "user-service",
                {"path": "/users", "method": "GET", "client_ip": f"192.168.1.{i % 10}"}
            )
            
        metrics = proxy.get_metrics()
        print(f"  Requests: {metrics['requests']['total']}")
        print(f"  Success Rate: {metrics['requests']['success_rate']:.1f}%")
        print(f"  Avg Latency: {metrics['latency']['avg_ms']:.2f}ms")
        
        # mTLS Status
        print(f"\n🔐 mTLS Status:")
        print(f"  Certificates issued: {len(mesh.mtls_manager.certificates)}")
        print(f"  TLS Mode: {dr.tls_mode.value}")
        
        # Mesh Status
        status = mesh.get_mesh_status()
        print(f"\n📈 Mesh Status:")
        print(f"  Services: {status['services']}")
        print(f"  Total Endpoints: {status['total_endpoints']}")
        print(f"  Healthy: {status['healthy_endpoints']}")
        print(f"  Virtual Services: {status['virtual_services']}")
        print(f"  Destination Rules: {status['destination_rules']}")
        
        # Multi-cluster
        print(f"\n🌐 Multi-Cluster Setup...")
        multi = MultiClusterMesh()
        multi.clusters["us-east"] = mesh
        multi.add_cluster("us-west")
        multi.federate_service("user-service", "us-east", "us-west")
        
        global_status = multi.get_global_status()
        print(f"  Clusters: {global_status['clusters']}")
        print(f"  Federation Rules: {global_status['federation_rules']}")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Service Mesh initialized successfully!")
    print("=" * 60)
