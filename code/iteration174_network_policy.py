#!/usr/bin/env python3
"""
Server Init - Iteration 174: Network Policy Platform
Платформа сетевых политик

Функционал:
- Policy Definition - определение политик
- Traffic Rules - правила трафика
- Ingress/Egress Control - контроль входящего/исходящего трафика
- Microsegmentation - микросегментация
- Service Mesh Integration - интеграция с service mesh
- Policy Enforcement - применение политик
- Audit Logging - аудит
- Compliance Validation - проверка соответствия
"""

import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import ipaddress


class PolicyAction(Enum):
    """Действие политики"""
    ALLOW = "allow"
    DENY = "deny"
    LOG = "log"
    RATE_LIMIT = "rate_limit"
    REDIRECT = "redirect"


class TrafficDirection(Enum):
    """Направление трафика"""
    INGRESS = "ingress"
    EGRESS = "egress"
    BOTH = "both"


class Protocol(Enum):
    """Протокол"""
    TCP = "TCP"
    UDP = "UDP"
    ICMP = "ICMP"
    ANY = "ANY"


class PolicyType(Enum):
    """Тип политики"""
    NETWORK = "network"
    APPLICATION = "application"
    IDENTITY = "identity"
    MICROSEGMENTATION = "microsegmentation"


class PolicyStatus(Enum):
    """Статус политики"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ERROR = "error"


class Selector:
    """Селектор для выбора ресурсов"""
    
    def __init__(self):
        self.labels: Dict[str, str] = {}
        self.namespaces: List[str] = []
        self.pod_selectors: Dict[str, str] = {}
        self.ip_blocks: List[str] = []
        self.services: List[str] = []
        
    def match_labels(self, **labels) -> "Selector":
        """Добавить label selector"""
        self.labels.update(labels)
        return self
        
    def in_namespace(self, *namespaces) -> "Selector":
        """Добавить namespaces"""
        self.namespaces.extend(namespaces)
        return self
        
    def with_ip_block(self, *cidr_blocks) -> "Selector":
        """Добавить IP блоки"""
        self.ip_blocks.extend(cidr_blocks)
        return self
        
    def for_service(self, *services) -> "Selector":
        """Добавить сервисы"""
        self.services.extend(services)
        return self
        
    def matches(self, resource: Dict) -> bool:
        """Проверка соответствия"""
        # Match labels
        if self.labels:
            resource_labels = resource.get("labels", {})
            for key, value in self.labels.items():
                if resource_labels.get(key) != value:
                    return False
                    
        # Match namespace
        if self.namespaces:
            if resource.get("namespace") not in self.namespaces:
                return False
                
        # Match IP
        if self.ip_blocks:
            resource_ip = resource.get("ip")
            if resource_ip:
                ip = ipaddress.ip_address(resource_ip)
                matched = False
                for cidr in self.ip_blocks:
                    if ip in ipaddress.ip_network(cidr, strict=False):
                        matched = True
                        break
                if not matched:
                    return False
                    
        return True


@dataclass
class PortRule:
    """Правило порта"""
    port: int
    end_port: Optional[int] = None  # For port range
    protocol: Protocol = Protocol.TCP
    
    def matches(self, port: int, proto: Protocol) -> bool:
        """Проверка соответствия"""
        if self.protocol != Protocol.ANY and self.protocol != proto:
            return False
            
        if self.end_port:
            return self.port <= port <= self.end_port
        return self.port == port


@dataclass
class TrafficRule:
    """Правило трафика"""
    rule_id: str
    name: str = ""
    description: str = ""
    
    # Direction
    direction: TrafficDirection = TrafficDirection.INGRESS
    
    # Source/Destination
    source_selector: Optional[Selector] = None
    destination_selector: Optional[Selector] = None
    
    # Ports
    ports: List[PortRule] = field(default_factory=list)
    
    # Action
    action: PolicyAction = PolicyAction.ALLOW
    
    # Priority (lower = higher priority)
    priority: int = 1000
    
    # Rate limiting
    rate_limit_requests: int = 0
    rate_limit_period_seconds: int = 60
    
    # Metadata
    enabled: bool = True


@dataclass
class NetworkPolicy:
    """Сетевая политика"""
    policy_id: str
    name: str = ""
    description: str = ""
    
    # Type
    policy_type: PolicyType = PolicyType.NETWORK
    
    # Target selector (what this policy applies to)
    target_selector: Optional[Selector] = None
    
    # Rules
    ingress_rules: List[TrafficRule] = field(default_factory=list)
    egress_rules: List[TrafficRule] = field(default_factory=list)
    
    # Default action
    default_ingress_action: PolicyAction = PolicyAction.DENY
    default_egress_action: PolicyAction = PolicyAction.ALLOW
    
    # Status
    status: PolicyStatus = PolicyStatus.PENDING
    applied_to: List[str] = field(default_factory=list)  # Resource IDs
    
    # Metadata
    namespace: str = "default"
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PolicyEvaluation:
    """Результат оценки политики"""
    allowed: bool = False
    matched_policy: str = ""
    matched_rule: str = ""
    action: PolicyAction = PolicyAction.DENY
    reason: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TrafficLog:
    """Лог трафика"""
    log_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Source
    source_ip: str = ""
    source_port: int = 0
    source_service: str = ""
    source_namespace: str = ""
    
    # Destination
    destination_ip: str = ""
    destination_port: int = 0
    destination_service: str = ""
    destination_namespace: str = ""
    
    # Protocol
    protocol: Protocol = Protocol.TCP
    
    # Result
    allowed: bool = True
    matched_policy: str = ""
    matched_rule: str = ""
    action: PolicyAction = PolicyAction.ALLOW
    
    # Metadata
    bytes_transferred: int = 0


class PolicyStore:
    """Хранилище политик"""
    
    def __init__(self):
        self.policies: Dict[str, NetworkPolicy] = {}
        
    def add(self, policy: NetworkPolicy):
        """Добавление политики"""
        self.policies[policy.policy_id] = policy
        
    def get(self, policy_id: str) -> Optional[NetworkPolicy]:
        """Получение политики"""
        return self.policies.get(policy_id)
        
    def list_by_namespace(self, namespace: str) -> List[NetworkPolicy]:
        """Получение политик namespace"""
        return [p for p in self.policies.values() if p.namespace == namespace]
        
    def list_by_type(self, policy_type: PolicyType) -> List[NetworkPolicy]:
        """Получение политик по типу"""
        return [p for p in self.policies.values() if p.policy_type == policy_type]
        
    def list_active(self) -> List[NetworkPolicy]:
        """Получение активных политик"""
        return [p for p in self.policies.values() if p.status == PolicyStatus.ACTIVE]


class PolicyEvaluator:
    """Оценщик политик"""
    
    def __init__(self, policy_store: PolicyStore):
        self.policy_store = policy_store
        
    def evaluate(
        self,
        source: Dict,
        destination: Dict,
        port: int,
        protocol: Protocol,
        direction: TrafficDirection
    ) -> PolicyEvaluation:
        """Оценка трафика"""
        result = PolicyEvaluation()
        
        # Get all active policies
        policies = self.policy_store.list_active()
        
        # Sort by target selector match and priority
        matched_policies = []
        for policy in policies:
            if policy.target_selector:
                target = destination if direction == TrafficDirection.INGRESS else source
                if policy.target_selector.matches(target):
                    matched_policies.append(policy)
                    
        if not matched_policies:
            # No policies match - use default allow
            result.allowed = True
            result.action = PolicyAction.ALLOW
            result.reason = "No matching policy"
            return result
            
        # Check rules
        for policy in matched_policies:
            rules = policy.ingress_rules if direction == TrafficDirection.INGRESS else policy.egress_rules
            
            for rule in rules:
                if not rule.enabled:
                    continue
                    
                # Check source/destination
                if direction == TrafficDirection.INGRESS:
                    if rule.source_selector and not rule.source_selector.matches(source):
                        continue
                else:
                    if rule.destination_selector and not rule.destination_selector.matches(destination):
                        continue
                        
                # Check ports
                if rule.ports:
                    port_match = False
                    for port_rule in rule.ports:
                        if port_rule.matches(port, protocol):
                            port_match = True
                            break
                    if not port_match:
                        continue
                        
                # Rule matched!
                result.matched_policy = policy.policy_id
                result.matched_rule = rule.rule_id
                result.action = rule.action
                result.allowed = rule.action in [PolicyAction.ALLOW, PolicyAction.LOG, PolicyAction.RATE_LIMIT]
                result.reason = f"Matched rule {rule.name}"
                return result
                
        # No rules matched - use default action
        default_action = (
            matched_policies[0].default_ingress_action
            if direction == TrafficDirection.INGRESS
            else matched_policies[0].default_egress_action
        )
        result.action = default_action
        result.allowed = default_action == PolicyAction.ALLOW
        result.matched_policy = matched_policies[0].policy_id
        result.reason = "Default policy action"
        
        return result


class PolicyEnforcer:
    """Применитель политик"""
    
    def __init__(self, policy_store: PolicyStore, evaluator: PolicyEvaluator):
        self.policy_store = policy_store
        self.evaluator = evaluator
        self.traffic_logs: List[TrafficLog] = []
        
    async def enforce(
        self,
        source: Dict,
        destination: Dict,
        port: int,
        protocol: Protocol = Protocol.TCP,
        direction: TrafficDirection = TrafficDirection.INGRESS
    ) -> PolicyEvaluation:
        """Применение политики"""
        # Evaluate
        result = self.evaluator.evaluate(source, destination, port, protocol, direction)
        
        # Log traffic
        log = TrafficLog(
            log_id=f"log_{uuid.uuid4().hex[:8]}",
            source_ip=source.get("ip", ""),
            source_port=source.get("port", 0),
            source_service=source.get("service", ""),
            source_namespace=source.get("namespace", ""),
            destination_ip=destination.get("ip", ""),
            destination_port=port,
            destination_service=destination.get("service", ""),
            destination_namespace=destination.get("namespace", ""),
            protocol=protocol,
            allowed=result.allowed,
            matched_policy=result.matched_policy,
            matched_rule=result.matched_rule,
            action=result.action
        )
        self.traffic_logs.append(log)
        
        # Keep only last 10000 logs
        if len(self.traffic_logs) > 10000:
            self.traffic_logs = self.traffic_logs[-10000:]
            
        return result


class MicrosegmentationManager:
    """Менеджер микросегментации"""
    
    def __init__(self, policy_store: PolicyStore):
        self.policy_store = policy_store
        self.segments: Dict[str, Set[str]] = {}  # segment_id -> set of services
        
    def create_segment(self, segment_id: str, services: List[str]):
        """Создание сегмента"""
        self.segments[segment_id] = set(services)
        
    def add_to_segment(self, segment_id: str, service: str):
        """Добавление в сегмент"""
        if segment_id not in self.segments:
            self.segments[segment_id] = set()
        self.segments[segment_id].add(service)
        
    def create_isolation_policy(self, segment_id: str) -> NetworkPolicy:
        """Создание политики изоляции сегмента"""
        services = self.segments.get(segment_id, set())
        
        # Create selector for segment
        selector = Selector().for_service(*services)
        
        # Allow intra-segment traffic
        allow_rule = TrafficRule(
            rule_id=f"allow_intra_{segment_id}",
            name="Allow intra-segment",
            direction=TrafficDirection.BOTH,
            source_selector=selector,
            destination_selector=selector,
            action=PolicyAction.ALLOW,
            priority=100
        )
        
        policy = NetworkPolicy(
            policy_id=f"microseg_{segment_id}",
            name=f"Microsegmentation - {segment_id}",
            policy_type=PolicyType.MICROSEGMENTATION,
            target_selector=selector,
            ingress_rules=[allow_rule],
            egress_rules=[allow_rule],
            default_ingress_action=PolicyAction.DENY,
            default_egress_action=PolicyAction.DENY
        )
        
        return policy


class PolicyValidator:
    """Валидатор политик"""
    
    def validate(self, policy: NetworkPolicy) -> List[str]:
        """Валидация политики"""
        errors = []
        
        # Check name
        if not policy.name:
            errors.append("Policy name is required")
            
        # Check target selector
        if not policy.target_selector:
            errors.append("Target selector is required")
            
        # Validate rules
        for rule in policy.ingress_rules + policy.egress_rules:
            if not rule.name:
                errors.append(f"Rule {rule.rule_id} missing name")
                
            # Validate ports
            for port_rule in rule.ports:
                if port_rule.port < 0 or port_rule.port > 65535:
                    errors.append(f"Invalid port {port_rule.port}")
                if port_rule.end_port and port_rule.end_port < port_rule.port:
                    errors.append(f"Invalid port range {port_rule.port}-{port_rule.end_port}")
                    
        return errors


class PolicyAuditor:
    """Аудитор политик"""
    
    def __init__(self, enforcer: PolicyEnforcer):
        self.enforcer = enforcer
        
    def get_traffic_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Получение сводки трафика"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_logs = [l for l in self.enforcer.traffic_logs if l.timestamp > cutoff]
        
        total = len(recent_logs)
        allowed = len([l for l in recent_logs if l.allowed])
        denied = total - allowed
        
        # By policy
        by_policy: Dict[str, int] = {}
        for log in recent_logs:
            policy = log.matched_policy or "no_match"
            by_policy[policy] = by_policy.get(policy, 0) + 1
            
        # By action
        by_action: Dict[str, int] = {}
        for log in recent_logs:
            action = log.action.value
            by_action[action] = by_action.get(action, 0) + 1
            
        # By service
        services: Dict[str, int] = {}
        for log in recent_logs:
            svc = log.destination_service or "unknown"
            services[svc] = services.get(svc, 0) + 1
            
        return {
            "total_requests": total,
            "allowed": allowed,
            "denied": denied,
            "by_policy": by_policy,
            "by_action": by_action,
            "by_service": services
        }
        
    def get_denied_traffic(self, limit: int = 100) -> List[TrafficLog]:
        """Получение запрещённого трафика"""
        denied = [l for l in self.enforcer.traffic_logs if not l.allowed]
        return denied[-limit:]


class NetworkPolicyPlatform:
    """Платформа сетевых политик"""
    
    def __init__(self):
        self.policy_store = PolicyStore()
        self.evaluator = PolicyEvaluator(self.policy_store)
        self.enforcer = PolicyEnforcer(self.policy_store, self.evaluator)
        self.microsegmentation = MicrosegmentationManager(self.policy_store)
        self.validator = PolicyValidator()
        self.auditor = PolicyAuditor(self.enforcer)
        
    def apply_policy(self, policy: NetworkPolicy) -> List[str]:
        """Применение политики"""
        # Validate
        errors = self.validator.validate(policy)
        if errors:
            policy.status = PolicyStatus.ERROR
            return errors
            
        # Store and activate
        self.policy_store.add(policy)
        policy.status = PolicyStatus.ACTIVE
        return []
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        policies = list(self.policy_store.policies.values())
        
        return {
            "total_policies": len(policies),
            "active_policies": len([p for p in policies if p.status == PolicyStatus.ACTIVE]),
            "by_type": {
                PolicyType.NETWORK.value: len([p for p in policies if p.policy_type == PolicyType.NETWORK]),
                PolicyType.APPLICATION.value: len([p for p in policies if p.policy_type == PolicyType.APPLICATION]),
                PolicyType.MICROSEGMENTATION.value: len([p for p in policies if p.policy_type == PolicyType.MICROSEGMENTATION])
            },
            "total_rules": sum(len(p.ingress_rules) + len(p.egress_rules) for p in policies),
            "segments": len(self.microsegmentation.segments),
            "traffic_logs": len(self.enforcer.traffic_logs)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 174: Network Policy Platform")
    print("=" * 60)
    
    async def demo():
        platform = NetworkPolicyPlatform()
        print("✓ Network Policy Platform created")
        
        # Create network policies
        print("\n🔒 Creating Network Policies...")
        
        # Policy 1: Web tier can receive traffic from load balancer
        web_selector = Selector().match_labels(tier="web")
        lb_selector = Selector().match_labels(tier="loadbalancer")
        
        policy1 = NetworkPolicy(
            policy_id="policy_web_ingress",
            name="Web Tier Ingress",
            description="Allow traffic from load balancer to web tier",
            policy_type=PolicyType.NETWORK,
            target_selector=web_selector,
            namespace="production",
            ingress_rules=[
                TrafficRule(
                    rule_id="allow_lb_http",
                    name="Allow LB HTTP",
                    direction=TrafficDirection.INGRESS,
                    source_selector=lb_selector,
                    ports=[
                        PortRule(port=80, protocol=Protocol.TCP),
                        PortRule(port=443, protocol=Protocol.TCP)
                    ],
                    action=PolicyAction.ALLOW,
                    priority=100
                )
            ],
            default_ingress_action=PolicyAction.DENY
        )
        
        errors = platform.apply_policy(policy1)
        print(f"  ✓ {policy1.name}: {'Applied' if not errors else 'Error: ' + str(errors)}")
        
        # Policy 2: App tier can only communicate with database
        app_selector = Selector().match_labels(tier="app")
        db_selector = Selector().match_labels(tier="database")
        
        policy2 = NetworkPolicy(
            policy_id="policy_app_egress",
            name="App Tier Egress",
            description="App tier can only talk to database",
            policy_type=PolicyType.NETWORK,
            target_selector=app_selector,
            namespace="production",
            egress_rules=[
                TrafficRule(
                    rule_id="allow_db_postgres",
                    name="Allow PostgreSQL",
                    direction=TrafficDirection.EGRESS,
                    destination_selector=db_selector,
                    ports=[
                        PortRule(port=5432, protocol=Protocol.TCP)
                    ],
                    action=PolicyAction.ALLOW,
                    priority=100
                ),
                TrafficRule(
                    rule_id="allow_dns",
                    name="Allow DNS",
                    direction=TrafficDirection.EGRESS,
                    ports=[
                        PortRule(port=53, protocol=Protocol.UDP)
                    ],
                    action=PolicyAction.ALLOW,
                    priority=200
                )
            ],
            default_egress_action=PolicyAction.DENY
        )
        
        errors = platform.apply_policy(policy2)
        print(f"  ✓ {policy2.name}: {'Applied' if not errors else 'Error: ' + str(errors)}")
        
        # Policy 3: Database - deny all ingress except from app tier
        policy3 = NetworkPolicy(
            policy_id="policy_db_ingress",
            name="Database Tier Ingress",
            description="Only app tier can access database",
            policy_type=PolicyType.NETWORK,
            target_selector=db_selector,
            namespace="production",
            ingress_rules=[
                TrafficRule(
                    rule_id="allow_app_postgres",
                    name="Allow App PostgreSQL",
                    direction=TrafficDirection.INGRESS,
                    source_selector=app_selector,
                    ports=[
                        PortRule(port=5432, protocol=Protocol.TCP)
                    ],
                    action=PolicyAction.ALLOW,
                    priority=100
                )
            ],
            default_ingress_action=PolicyAction.DENY,
            default_egress_action=PolicyAction.DENY
        )
        
        errors = platform.apply_policy(policy3)
        print(f"  ✓ {policy3.name}: {'Applied' if not errors else 'Error: ' + str(errors)}")
        
        # Policy 4: IP-based deny list
        deny_selector = Selector().with_ip_block("10.0.0.0/8")
        
        policy4 = NetworkPolicy(
            policy_id="policy_deny_internal",
            name="Deny Internal to External",
            description="Block external access from internal network",
            policy_type=PolicyType.NETWORK,
            target_selector=Selector().in_namespace("production"),
            namespace="production",
            egress_rules=[
                TrafficRule(
                    rule_id="deny_external",
                    name="Deny External",
                    direction=TrafficDirection.EGRESS,
                    destination_selector=Selector().with_ip_block("0.0.0.0/0"),
                    action=PolicyAction.DENY,
                    priority=500
                )
            ]
        )
        
        errors = platform.apply_policy(policy4)
        print(f"  ✓ {policy4.name}: {'Applied' if not errors else 'Error: ' + str(errors)}")
        
        # Show policies
        print("\n📋 Applied Policies:")
        
        print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────┐")
        print("  │ Policy                       │ Type            │ Namespace  │ Rules │ Status    │")
        print("  ├─────────────────────────────────────────────────────────────────────────────────────────────┤")
        
        for policy in platform.policy_store.policies.values():
            name = policy.name[:28].ljust(28)
            ptype = policy.policy_type.value[:15].ljust(15)
            ns = policy.namespace[:10].ljust(10)
            rules = f"{len(policy.ingress_rules) + len(policy.egress_rules)}".rjust(5)
            
            status_icons = {
                PolicyStatus.ACTIVE: "🟢",
                PolicyStatus.INACTIVE: "⚪",
                PolicyStatus.PENDING: "🟡",
                PolicyStatus.ERROR: "🔴"
            }
            status = f"{status_icons.get(policy.status, '⚪')} {policy.status.value}".ljust(10)
            print(f"  │ {name} │ {ptype} │ {ns} │ {rules} │ {status} │")
            
        print("  └─────────────────────────────────────────────────────────────────────────────────────────────┘")
        
        # Simulate traffic
        print("\n🌐 Simulating Network Traffic...")
        
        traffic_scenarios = [
            {
                "name": "LB to Web (HTTP)",
                "source": {"ip": "10.0.1.10", "labels": {"tier": "loadbalancer"}, "namespace": "production"},
                "destination": {"ip": "10.0.2.20", "labels": {"tier": "web"}, "namespace": "production"},
                "port": 80,
                "protocol": Protocol.TCP,
                "direction": TrafficDirection.INGRESS
            },
            {
                "name": "Web to App (HTTP)",
                "source": {"ip": "10.0.2.20", "labels": {"tier": "web"}, "namespace": "production"},
                "destination": {"ip": "10.0.3.30", "labels": {"tier": "app"}, "namespace": "production"},
                "port": 8080,
                "protocol": Protocol.TCP,
                "direction": TrafficDirection.INGRESS
            },
            {
                "name": "App to DB (PostgreSQL)",
                "source": {"ip": "10.0.3.30", "labels": {"tier": "app"}, "namespace": "production"},
                "destination": {"ip": "10.0.4.40", "labels": {"tier": "database"}, "namespace": "production"},
                "port": 5432,
                "protocol": Protocol.TCP,
                "direction": TrafficDirection.EGRESS
            },
            {
                "name": "Web to DB (Direct - Should Deny)",
                "source": {"ip": "10.0.2.20", "labels": {"tier": "web"}, "namespace": "production"},
                "destination": {"ip": "10.0.4.40", "labels": {"tier": "database"}, "namespace": "production"},
                "port": 5432,
                "protocol": Protocol.TCP,
                "direction": TrafficDirection.EGRESS
            },
            {
                "name": "External to Web (SSH - Should Deny)",
                "source": {"ip": "192.168.1.100", "labels": {}, "namespace": "external"},
                "destination": {"ip": "10.0.2.20", "labels": {"tier": "web"}, "namespace": "production"},
                "port": 22,
                "protocol": Protocol.TCP,
                "direction": TrafficDirection.INGRESS
            },
        ]
        
        print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
        print("  │ Scenario                           │ Result  │ Action   │ Policy                     │")
        print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
        
        for scenario in traffic_scenarios:
            result = await platform.enforcer.enforce(
                scenario["source"],
                scenario["destination"],
                scenario["port"],
                scenario["protocol"],
                scenario["direction"]
            )
            
            name = scenario["name"][:35].ljust(35)
            allowed = "✓ Allow" if result.allowed else "✗ Deny "
            action = result.action.value[:8].ljust(8)
            policy = result.matched_policy[:26].ljust(26)
            
            print(f"  │ {name} │ {allowed} │ {action} │ {policy} │")
            
        print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
        
        # Microsegmentation
        print("\n🔲 Creating Microsegmentation...")
        
        # Define segments
        platform.microsegmentation.create_segment("payment", ["payment-api", "payment-processor", "payment-gateway"])
        platform.microsegmentation.create_segment("auth", ["auth-service", "token-service", "user-service"])
        platform.microsegmentation.create_segment("analytics", ["analytics-collector", "analytics-processor"])
        
        print("  Segments created:")
        for seg_id, services in platform.microsegmentation.segments.items():
            print(f"    • {seg_id}: {', '.join(services)}")
            
        # Create isolation policies
        for seg_id in platform.microsegmentation.segments:
            policy = platform.microsegmentation.create_isolation_policy(seg_id)
            errors = platform.apply_policy(policy)
            print(f"  ✓ Isolation policy for '{seg_id}': {'Applied' if not errors else 'Error'}")
            
        # Traffic audit
        print("\n📊 Traffic Audit Summary:")
        
        # Generate more traffic for audit
        for _ in range(50):
            import random
            scenario = random.choice(traffic_scenarios)
            await platform.enforcer.enforce(
                scenario["source"],
                scenario["destination"],
                scenario["port"],
                scenario["protocol"],
                scenario["direction"]
            )
            
        summary = platform.auditor.get_traffic_summary(hours=1)
        
        print(f"\n  Total Requests: {summary['total_requests']}")
        print(f"  Allowed: {summary['allowed']}")
        print(f"  Denied: {summary['denied']}")
        
        if summary['total_requests'] > 0:
            allow_rate = summary['allowed'] / summary['total_requests'] * 100
            print(f"  Allow Rate: {allow_rate:.1f}%")
            
        print("\n  By Action:")
        for action, count in summary['by_action'].items():
            pct = count / summary['total_requests'] * 100 if summary['total_requests'] > 0 else 0
            bar = "█" * int(pct / 5)
            print(f"    {action.ljust(12)}: {bar} {count}")
            
        # Denied traffic
        print("\n  Recent Denied Traffic:")
        denied = platform.auditor.get_denied_traffic(5)
        for log in denied[:5]:
            print(f"    • {log.source_ip}:{log.source_port} → {log.destination_ip}:{log.destination_port} ({log.protocol.value})")
            
        # Platform statistics
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Policies: {stats['total_policies']}")
        print(f"  Active Policies: {stats['active_policies']}")
        print(f"  Total Rules: {stats['total_rules']}")
        print(f"  Segments: {stats['segments']}")
        print(f"  Traffic Logs: {stats['traffic_logs']}")
        
        print("\n  By Type:")
        for ptype, count in stats['by_type'].items():
            print(f"    • {ptype}: {count}")
            
        # Dashboard
        print("\n┌────────────────────────────────────────────────────────────────────┐")
        print("│                   Network Policy Dashboard                         │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Total Policies:              {stats['total_policies']:>10}                       │")
        print(f"│ Active Policies:             {stats['active_policies']:>10}                       │")
        print(f"│ Total Rules:                 {stats['total_rules']:>10}                       │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Segments:                    {stats['segments']:>10}                       │")
        print(f"│ Traffic Logs:                {stats['traffic_logs']:>10}                       │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Requests Allowed:            {summary['allowed']:>10}                       │")
        print(f"│ Requests Denied:             {summary['denied']:>10}                       │")
        print("└────────────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Network Policy Platform initialized!")
    print("=" * 60)
