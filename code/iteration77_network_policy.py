#!/usr/bin/env python3
"""
Server Init - Iteration 77: Network Policy Engine
Движок сетевых политик

Функционал:
- Network Rules - сетевые правила
- Traffic Control - управление трафиком
- Segmentation - сегментация сети
- Firewall Rules - правила фаервола
- Service Mesh Policies - политики сервис меш
- Ingress/Egress Control - контроль входа/выхода
- Network Isolation - сетевая изоляция
- Policy Enforcement - применение политик
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
from collections import defaultdict
import uuid
import ipaddress


class PolicyAction(Enum):
    """Действие политики"""
    ALLOW = "allow"
    DENY = "deny"
    DROP = "drop"
    REJECT = "reject"
    LOG = "log"
    RATE_LIMIT = "rate_limit"


class Protocol(Enum):
    """Протокол"""
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    ANY = "any"


class Direction(Enum):
    """Направление"""
    INGRESS = "ingress"
    EGRESS = "egress"
    BOTH = "both"


class NetworkZone(Enum):
    """Сетевая зона"""
    PUBLIC = "public"
    PRIVATE = "private"
    DMZ = "dmz"
    TRUSTED = "trusted"
    MANAGEMENT = "management"


class PolicyType(Enum):
    """Тип политики"""
    FIREWALL = "firewall"
    NETWORK_POLICY = "network_policy"
    SERVICE_MESH = "service_mesh"
    SECURITY_GROUP = "security_group"


@dataclass
class PortRange:
    """Диапазон портов"""
    start: int = 0
    end: int = 65535
    
    def contains(self, port: int) -> bool:
        return self.start <= port <= self.end
        
    def __str__(self) -> str:
        if self.start == self.end:
            return str(self.start)
        return f"{self.start}-{self.end}"


@dataclass
class NetworkEndpoint:
    """Сетевая точка"""
    endpoint_id: str
    name: str = ""
    
    # Идентификация
    cidr: str = ""  # CIDR блок
    ip_addresses: List[str] = field(default_factory=list)
    
    # Labels для Kubernetes-стиля
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Namespace/Zone
    namespace: str = ""
    zone: NetworkZone = NetworkZone.PRIVATE
    
    # Сервис
    service_name: str = ""
    
    def matches_ip(self, ip: str) -> bool:
        """Проверка соответствия IP"""
        if ip in self.ip_addresses:
            return True
            
        if self.cidr:
            try:
                network = ipaddress.ip_network(self.cidr, strict=False)
                addr = ipaddress.ip_address(ip)
                return addr in network
            except ValueError:
                pass
                
        return False
        
    def matches_labels(self, target_labels: Dict[str, str]) -> bool:
        """Проверка соответствия labels"""
        for key, value in self.labels.items():
            if target_labels.get(key) != value:
                return False
        return True


@dataclass
class TrafficRule:
    """Правило трафика"""
    rule_id: str
    name: str = ""
    
    # Источник
    source: Optional[NetworkEndpoint] = None
    source_selector: Dict[str, str] = field(default_factory=dict)
    
    # Назначение
    destination: Optional[NetworkEndpoint] = None
    destination_selector: Dict[str, str] = field(default_factory=dict)
    
    # Протокол и порты
    protocol: Protocol = Protocol.TCP
    ports: List[PortRange] = field(default_factory=list)
    
    # Действие
    action: PolicyAction = PolicyAction.ALLOW
    
    # Направление
    direction: Direction = Direction.INGRESS
    
    # Приоритет
    priority: int = 100
    
    # Rate limit
    rate_limit_rps: int = 0
    
    # Логирование
    log_enabled: bool = False
    
    # Статус
    enabled: bool = True


@dataclass
class NetworkPolicy:
    """Сетевая политика"""
    policy_id: str
    name: str
    
    # Тип
    policy_type: PolicyType = PolicyType.NETWORK_POLICY
    
    # Селектор (к чему применяется)
    selector: Dict[str, str] = field(default_factory=dict)
    namespace: str = ""
    
    # Правила
    ingress_rules: List[TrafficRule] = field(default_factory=list)
    egress_rules: List[TrafficRule] = field(default_factory=list)
    
    # Действие по умолчанию
    default_ingress_action: PolicyAction = PolicyAction.DENY
    default_egress_action: PolicyAction = PolicyAction.ALLOW
    
    # Статус
    enabled: bool = True
    
    # Метаданные
    created_at: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class FirewallRule:
    """Правило фаервола"""
    rule_id: str
    name: str = ""
    
    # Источник
    source_cidr: str = "0.0.0.0/0"
    source_zone: Optional[NetworkZone] = None
    
    # Назначение
    destination_cidr: str = "0.0.0.0/0"
    destination_zone: Optional[NetworkZone] = None
    
    # Протокол
    protocol: Protocol = Protocol.TCP
    
    # Порты
    source_ports: List[PortRange] = field(default_factory=list)
    destination_ports: List[PortRange] = field(default_factory=list)
    
    # Действие
    action: PolicyAction = PolicyAction.ALLOW
    
    # Приоритет
    priority: int = 100
    
    # Логирование
    log_enabled: bool = False
    log_prefix: str = ""
    
    # Счётчики
    packets_matched: int = 0
    bytes_matched: int = 0
    
    # Статус
    enabled: bool = True


@dataclass
class ServiceMeshPolicy:
    """Политика сервис меш"""
    policy_id: str
    name: str = ""
    
    # Источник сервиса
    source_service: str = ""
    source_namespace: str = ""
    
    # Назначение сервиса
    destination_service: str = ""
    destination_namespace: str = ""
    
    # HTTP правила
    http_methods: List[str] = field(default_factory=list)  # GET, POST, etc.
    http_paths: List[str] = field(default_factory=list)  # /api/*, /health
    
    # Headers
    required_headers: Dict[str, str] = field(default_factory=dict)
    
    # mTLS
    mtls_mode: str = "STRICT"  # STRICT, PERMISSIVE, DISABLE
    
    # Timeout
    timeout_seconds: int = 30
    
    # Retry
    retry_attempts: int = 3
    
    # Circuit breaker
    circuit_breaker_enabled: bool = False
    max_connections: int = 100
    max_pending_requests: int = 100
    
    # Действие
    action: PolicyAction = PolicyAction.ALLOW
    
    # Статус
    enabled: bool = True


@dataclass
class TrafficRequest:
    """Запрос на проверку трафика"""
    request_id: str
    
    # Источник
    source_ip: str = ""
    source_port: int = 0
    source_labels: Dict[str, str] = field(default_factory=dict)
    source_namespace: str = ""
    
    # Назначение
    destination_ip: str = ""
    destination_port: int = 0
    destination_labels: Dict[str, str] = field(default_factory=dict)
    destination_namespace: str = ""
    
    # Протокол
    protocol: Protocol = Protocol.TCP
    
    # HTTP (опционально)
    http_method: str = ""
    http_path: str = ""
    http_headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class TrafficDecision:
    """Решение по трафику"""
    request_id: str
    
    # Результат
    allowed: bool = True
    action: PolicyAction = PolicyAction.ALLOW
    
    # Правило
    matched_rule_id: str = ""
    matched_policy_id: str = ""
    
    # Причина
    reason: str = ""
    
    # Rate limit info
    rate_limited: bool = False
    retry_after_ms: int = 0


class PolicyMatcher:
    """Сопоставление политик"""
    
    def match_endpoint(self, endpoint: NetworkEndpoint,
                        ip: str, labels: Dict[str, str]) -> bool:
        """Сопоставление endpoint"""
        if endpoint.cidr:
            if not endpoint.matches_ip(ip):
                return False
                
        if endpoint.labels:
            if not endpoint.matches_labels(labels):
                return False
                
        return True
        
    def match_port(self, port_ranges: List[PortRange], port: int) -> bool:
        """Сопоставление порта"""
        if not port_ranges:
            return True  # Любой порт
            
        for pr in port_ranges:
            if pr.contains(port):
                return True
        return False
        
    def match_rule(self, rule: TrafficRule, request: TrafficRequest) -> bool:
        """Сопоставление правила"""
        if not rule.enabled:
            return False
            
        # Протокол
        if rule.protocol != Protocol.ANY and rule.protocol != request.protocol:
            return False
            
        # Порты
        if rule.ports and not self.match_port(rule.ports, request.destination_port):
            return False
            
        # Источник
        if rule.source and not self.match_endpoint(
            rule.source, request.source_ip, request.source_labels
        ):
            return False
            
        if rule.source_selector:
            match = all(
                request.source_labels.get(k) == v
                for k, v in rule.source_selector.items()
            )
            if not match:
                return False
                
        # Назначение
        if rule.destination and not self.match_endpoint(
            rule.destination, request.destination_ip, request.destination_labels
        ):
            return False
            
        if rule.destination_selector:
            match = all(
                request.destination_labels.get(k) == v
                for k, v in rule.destination_selector.items()
            )
            if not match:
                return False
                
        return True


class PolicyEvaluator:
    """Оценка политик"""
    
    def __init__(self):
        self.matcher = PolicyMatcher()
        self.policies: Dict[str, NetworkPolicy] = {}
        self.firewall_rules: Dict[str, FirewallRule] = {}
        self.mesh_policies: Dict[str, ServiceMeshPolicy] = {}
        
        self.rate_limiters: Dict[str, Dict[str, List[datetime]]] = defaultdict(
            lambda: defaultdict(list)
        )
        
    def add_policy(self, policy: NetworkPolicy):
        """Добавление политики"""
        self.policies[policy.policy_id] = policy
        
    def add_firewall_rule(self, rule: FirewallRule):
        """Добавление правила фаервола"""
        self.firewall_rules[rule.rule_id] = rule
        
    def add_mesh_policy(self, policy: ServiceMeshPolicy):
        """Добавление mesh политики"""
        self.mesh_policies[policy.policy_id] = policy
        
    def evaluate(self, request: TrafficRequest) -> TrafficDecision:
        """Оценка запроса"""
        decision = TrafficDecision(request_id=request.request_id)
        
        # 1. Проверка firewall rules
        fw_decision = self._check_firewall(request)
        if fw_decision and fw_decision.action == PolicyAction.DENY:
            return fw_decision
            
        # 2. Проверка network policies
        np_decision = self._check_network_policies(request)
        if np_decision:
            return np_decision
            
        # 3. Проверка mesh policies (для HTTP)
        if request.http_method:
            mesh_decision = self._check_mesh_policies(request)
            if mesh_decision:
                return mesh_decision
                
        return decision
        
    def _check_firewall(self, request: TrafficRequest) -> Optional[TrafficDecision]:
        """Проверка firewall rules"""
        # Сортируем по приоритету
        rules = sorted(
            [r for r in self.firewall_rules.values() if r.enabled],
            key=lambda r: r.priority
        )
        
        for rule in rules:
            if self._matches_firewall_rule(rule, request):
                rule.packets_matched += 1
                
                return TrafficDecision(
                    request_id=request.request_id,
                    allowed=rule.action == PolicyAction.ALLOW,
                    action=rule.action,
                    matched_rule_id=rule.rule_id,
                    reason=f"Firewall rule: {rule.name}"
                )
                
        return None
        
    def _matches_firewall_rule(self, rule: FirewallRule, request: TrafficRequest) -> bool:
        """Сопоставление firewall rule"""
        # Протокол
        if rule.protocol != Protocol.ANY and rule.protocol != request.protocol:
            return False
            
        # Source CIDR
        if rule.source_cidr != "0.0.0.0/0":
            try:
                network = ipaddress.ip_network(rule.source_cidr, strict=False)
                if ipaddress.ip_address(request.source_ip) not in network:
                    return False
            except ValueError:
                return False
                
        # Destination CIDR
        if rule.destination_cidr != "0.0.0.0/0":
            try:
                network = ipaddress.ip_network(rule.destination_cidr, strict=False)
                if ipaddress.ip_address(request.destination_ip) not in network:
                    return False
            except ValueError:
                return False
                
        # Destination ports
        if rule.destination_ports:
            if not any(pr.contains(request.destination_port) for pr in rule.destination_ports):
                return False
                
        return True
        
    def _check_network_policies(self, request: TrafficRequest) -> Optional[TrafficDecision]:
        """Проверка network policies"""
        for policy in self.policies.values():
            if not policy.enabled:
                continue
                
            # Проверяем селектор политики
            if policy.namespace and policy.namespace != request.destination_namespace:
                continue
                
            if policy.selector:
                if not all(
                    request.destination_labels.get(k) == v
                    for k, v in policy.selector.items()
                ):
                    continue
                    
            # Проверяем ingress rules
            for rule in policy.ingress_rules:
                if self.matcher.match_rule(rule, request):
                    # Rate limiting
                    if rule.rate_limit_rps > 0:
                        if self._is_rate_limited(rule.rule_id, rule.rate_limit_rps):
                            return TrafficDecision(
                                request_id=request.request_id,
                                allowed=False,
                                action=PolicyAction.RATE_LIMIT,
                                matched_rule_id=rule.rule_id,
                                matched_policy_id=policy.policy_id,
                                rate_limited=True,
                                retry_after_ms=1000
                            )
                            
                    return TrafficDecision(
                        request_id=request.request_id,
                        allowed=rule.action == PolicyAction.ALLOW,
                        action=rule.action,
                        matched_rule_id=rule.rule_id,
                        matched_policy_id=policy.policy_id,
                        reason=f"Policy: {policy.name}, Rule: {rule.name}"
                    )
                    
            # Если правила не нашлось - применяем default
            return TrafficDecision(
                request_id=request.request_id,
                allowed=policy.default_ingress_action == PolicyAction.ALLOW,
                action=policy.default_ingress_action,
                matched_policy_id=policy.policy_id,
                reason=f"Default ingress action for {policy.name}"
            )
            
        return None
        
    def _check_mesh_policies(self, request: TrafficRequest) -> Optional[TrafficDecision]:
        """Проверка mesh policies"""
        for policy in self.mesh_policies.values():
            if not policy.enabled:
                continue
                
            # Сопоставление источника
            if policy.source_namespace and policy.source_namespace != request.source_namespace:
                continue
                
            # Сопоставление назначения
            if policy.destination_namespace and policy.destination_namespace != request.destination_namespace:
                continue
                
            # HTTP метод
            if policy.http_methods and request.http_method not in policy.http_methods:
                continue
                
            # HTTP путь
            if policy.http_paths:
                path_match = False
                for pattern in policy.http_paths:
                    if pattern.endswith("*"):
                        if request.http_path.startswith(pattern[:-1]):
                            path_match = True
                            break
                    elif pattern == request.http_path:
                        path_match = True
                        break
                if not path_match:
                    continue
                    
            # Required headers
            if policy.required_headers:
                if not all(
                    request.http_headers.get(k) == v
                    for k, v in policy.required_headers.items()
                ):
                    continue
                    
            return TrafficDecision(
                request_id=request.request_id,
                allowed=policy.action == PolicyAction.ALLOW,
                action=policy.action,
                matched_policy_id=policy.policy_id,
                reason=f"Mesh policy: {policy.name}"
            )
            
        return None
        
    def _is_rate_limited(self, rule_id: str, limit_rps: int) -> bool:
        """Проверка rate limit"""
        now = datetime.now()
        window_start = now - timedelta(seconds=1)
        
        # Очистка старых записей
        self.rate_limiters[rule_id]["requests"] = [
            ts for ts in self.rate_limiters[rule_id]["requests"]
            if ts > window_start
        ]
        
        current_count = len(self.rate_limiters[rule_id]["requests"])
        
        if current_count >= limit_rps:
            return True
            
        self.rate_limiters[rule_id]["requests"].append(now)
        return False


class NetworkPolicyEngine:
    """Движок сетевых политик"""
    
    def __init__(self):
        self.evaluator = PolicyEvaluator()
        self.endpoints: Dict[str, NetworkEndpoint] = {}
        self.decision_log: List[TrafficDecision] = []
        
    def create_endpoint(self, name: str, **kwargs) -> NetworkEndpoint:
        """Создание endpoint"""
        endpoint = NetworkEndpoint(
            endpoint_id=f"ep_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        self.endpoints[endpoint.endpoint_id] = endpoint
        return endpoint
        
    def create_network_policy(self, name: str, **kwargs) -> NetworkPolicy:
        """Создание network policy"""
        policy = NetworkPolicy(
            policy_id=f"np_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        self.evaluator.add_policy(policy)
        return policy
        
    def create_firewall_rule(self, name: str, **kwargs) -> FirewallRule:
        """Создание firewall rule"""
        rule = FirewallRule(
            rule_id=f"fw_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        self.evaluator.add_firewall_rule(rule)
        return rule
        
    def create_mesh_policy(self, name: str, **kwargs) -> ServiceMeshPolicy:
        """Создание mesh policy"""
        policy = ServiceMeshPolicy(
            policy_id=f"mesh_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        self.evaluator.add_mesh_policy(policy)
        return policy
        
    def create_traffic_rule(self, name: str, **kwargs) -> TrafficRule:
        """Создание traffic rule"""
        return TrafficRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        
    def check_traffic(self, source_ip: str, destination_ip: str,
                       destination_port: int, protocol: Protocol = Protocol.TCP,
                       **kwargs) -> TrafficDecision:
        """Проверка трафика"""
        request = TrafficRequest(
            request_id=f"req_{uuid.uuid4().hex[:8]}",
            source_ip=source_ip,
            destination_ip=destination_ip,
            destination_port=destination_port,
            protocol=protocol,
            **kwargs
        )
        
        decision = self.evaluator.evaluate(request)
        self.decision_log.append(decision)
        
        return decision
        
    def get_stats(self) -> Dict[str, Any]:
        """Статистика"""
        total_decisions = len(self.decision_log)
        allowed = len([d for d in self.decision_log if d.allowed])
        denied = total_decisions - allowed
        
        return {
            "network_policies": len(self.evaluator.policies),
            "firewall_rules": len(self.evaluator.firewall_rules),
            "mesh_policies": len(self.evaluator.mesh_policies),
            "endpoints": len(self.endpoints),
            "total_decisions": total_decisions,
            "allowed": allowed,
            "denied": denied,
            "allow_rate": f"{allowed/total_decisions*100:.1f}%" if total_decisions > 0 else "N/A"
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 77: Network Policy Engine")
    print("=" * 60)
    
    async def demo():
        engine = NetworkPolicyEngine()
        print("✓ Network Policy Engine created")
        
        # Создание endpoints
        print("\n🌐 Creating Network Endpoints...")
        
        web_frontend = engine.create_endpoint(
            "web-frontend",
            cidr="10.0.1.0/24",
            labels={"app": "frontend", "tier": "web"},
            namespace="production",
            zone=NetworkZone.DMZ
        )
        print(f"  ✓ {web_frontend.name} ({web_frontend.cidr})")
        
        api_backend = engine.create_endpoint(
            "api-backend",
            cidr="10.0.2.0/24",
            labels={"app": "api", "tier": "backend"},
            namespace="production",
            zone=NetworkZone.PRIVATE
        )
        print(f"  ✓ {api_backend.name} ({api_backend.cidr})")
        
        database = engine.create_endpoint(
            "database",
            cidr="10.0.3.0/24",
            labels={"app": "postgres", "tier": "database"},
            namespace="production",
            zone=NetworkZone.TRUSTED
        )
        print(f"  ✓ {database.name} ({database.cidr})")
        
        # Firewall rules
        print("\n🔥 Creating Firewall Rules...")
        
        # Разрешить HTTP/HTTPS извне
        web_rule = engine.create_firewall_rule(
            "allow-web-traffic",
            source_cidr="0.0.0.0/0",
            destination_cidr="10.0.1.0/24",
            protocol=Protocol.TCP,
            destination_ports=[PortRange(80, 80), PortRange(443, 443)],
            action=PolicyAction.ALLOW,
            priority=10
        )
        print(f"  ✓ {web_rule.name}: HTTP/HTTPS to frontend")
        
        # Блокировать SSH извне
        ssh_block = engine.create_firewall_rule(
            "block-external-ssh",
            source_cidr="0.0.0.0/0",
            destination_cidr="10.0.0.0/8",
            protocol=Protocol.TCP,
            destination_ports=[PortRange(22, 22)],
            action=PolicyAction.DENY,
            priority=5,
            log_enabled=True,
            log_prefix="SSH_BLOCKED"
        )
        print(f"  ✓ {ssh_block.name}: Block external SSH")
        
        # Разрешить management SSH
        mgmt_ssh = engine.create_firewall_rule(
            "allow-mgmt-ssh",
            source_cidr="10.255.0.0/24",  # Management network
            destination_cidr="10.0.0.0/8",
            protocol=Protocol.TCP,
            destination_ports=[PortRange(22, 22)],
            action=PolicyAction.ALLOW,
            priority=4
        )
        print(f"  ✓ {mgmt_ssh.name}: Allow management SSH")
        
        # Network policies
        print("\n📋 Creating Network Policies...")
        
        # Политика для API
        api_rule = engine.create_traffic_rule(
            "frontend-to-api",
            source_selector={"app": "frontend"},
            destination_selector={"app": "api"},
            protocol=Protocol.TCP,
            ports=[PortRange(8080, 8080)],
            action=PolicyAction.ALLOW,
            rate_limit_rps=1000
        )
        
        api_policy = engine.create_network_policy(
            "api-access-policy",
            selector={"app": "api"},
            namespace="production",
            ingress_rules=[api_rule],
            default_ingress_action=PolicyAction.DENY
        )
        print(f"  ✓ {api_policy.name}")
        print(f"    Ingress rules: {len(api_policy.ingress_rules)}")
        print(f"    Default: {api_policy.default_ingress_action.value}")
        
        # Политика для базы данных
        db_rule = engine.create_traffic_rule(
            "api-to-database",
            source_selector={"app": "api"},
            destination_selector={"app": "postgres"},
            protocol=Protocol.TCP,
            ports=[PortRange(5432, 5432)],
            action=PolicyAction.ALLOW
        )
        
        db_policy = engine.create_network_policy(
            "database-access-policy",
            selector={"app": "postgres"},
            namespace="production",
            ingress_rules=[db_rule],
            default_ingress_action=PolicyAction.DENY
        )
        print(f"  ✓ {db_policy.name}")
        
        # Service mesh policies
        print("\n🔗 Creating Service Mesh Policies...")
        
        api_mesh = engine.create_mesh_policy(
            "api-http-policy",
            source_service="frontend",
            destination_service="api",
            source_namespace="production",
            destination_namespace="production",
            http_methods=["GET", "POST", "PUT", "DELETE"],
            http_paths=["/api/*", "/health"],
            mtls_mode="STRICT",
            timeout_seconds=30,
            retry_attempts=3,
            circuit_breaker_enabled=True,
            max_connections=100
        )
        print(f"  ✓ {api_mesh.name}")
        print(f"    mTLS: {api_mesh.mtls_mode}")
        print(f"    Methods: {api_mesh.http_methods}")
        
        # Тестирование трафика
        print("\n🔍 Testing Traffic Decisions...")
        
        # Web traffic - должен быть разрешён
        decision = engine.check_traffic(
            source_ip="8.8.8.8",
            destination_ip="10.0.1.100",
            destination_port=443
        )
        status = "✓ Allowed" if decision.allowed else "✗ Denied"
        print(f"\n  External → Web (443): {status}")
        print(f"    Reason: {decision.reason}")
        
        # SSH извне - должен быть заблокирован
        decision = engine.check_traffic(
            source_ip="8.8.8.8",
            destination_ip="10.0.1.100",
            destination_port=22
        )
        status = "✓ Allowed" if decision.allowed else "✗ Denied"
        print(f"\n  External → Web (SSH): {status}")
        print(f"    Reason: {decision.reason}")
        
        # Management SSH - должен быть разрешён
        decision = engine.check_traffic(
            source_ip="10.255.0.10",
            destination_ip="10.0.2.50",
            destination_port=22
        )
        status = "✓ Allowed" if decision.allowed else "✗ Denied"
        print(f"\n  Management → Server (SSH): {status}")
        print(f"    Reason: {decision.reason}")
        
        # Frontend → API - разрешён
        decision = engine.check_traffic(
            source_ip="10.0.1.100",
            destination_ip="10.0.2.50",
            destination_port=8080,
            source_labels={"app": "frontend"},
            destination_labels={"app": "api"},
            source_namespace="production",
            destination_namespace="production"
        )
        status = "✓ Allowed" if decision.allowed else "✗ Denied"
        print(f"\n  Frontend → API (8080): {status}")
        print(f"    Reason: {decision.reason}")
        
        # Direct to Database - должен быть заблокирован
        decision = engine.check_traffic(
            source_ip="10.0.1.100",
            destination_ip="10.0.3.10",
            destination_port=5432,
            source_labels={"app": "frontend"},
            destination_labels={"app": "postgres"},
            source_namespace="production",
            destination_namespace="production"
        )
        status = "✓ Allowed" if decision.allowed else "✗ Denied"
        print(f"\n  Frontend → Database (5432): {status}")
        print(f"    Reason: {decision.reason}")
        
        # API → Database - разрешён
        decision = engine.check_traffic(
            source_ip="10.0.2.50",
            destination_ip="10.0.3.10",
            destination_port=5432,
            source_labels={"app": "api"},
            destination_labels={"app": "postgres"},
            source_namespace="production",
            destination_namespace="production"
        )
        status = "✓ Allowed" if decision.allowed else "✗ Denied"
        print(f"\n  API → Database (5432): {status}")
        print(f"    Reason: {decision.reason}")
        
        # HTTP request через mesh
        decision = engine.check_traffic(
            source_ip="10.0.1.100",
            destination_ip="10.0.2.50",
            destination_port=8080,
            http_method="GET",
            http_path="/api/users",
            source_namespace="production",
            destination_namespace="production"
        )
        status = "✓ Allowed" if decision.allowed else "✗ Denied"
        print(f"\n  GET /api/users (mesh): {status}")
        print(f"    Reason: {decision.reason}")
        
        # Статистика
        print("\n📊 Engine Statistics:")
        stats = engine.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
        # Визуализация зон
        print("\n🏠 Network Zones:")
        zones = defaultdict(list)
        for ep in engine.endpoints.values():
            zones[ep.zone.value].append(ep)
            
        for zone, endpoints in zones.items():
            print(f"\n  [{zone.upper()}]")
            for ep in endpoints:
                print(f"    └─ {ep.name}: {ep.cidr}")
                
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Network Policy Engine initialized!")
    print("=" * 60)
