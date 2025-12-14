#!/usr/bin/env python3
"""
Server Init - Iteration 216: Network Policy Platform
Платформа сетевых политик

Функционал:
- Policy Definition - определение политик
- Ingress/Egress Rules - правила входящего/исходящего трафика
- Namespace Isolation - изоляция namespace
- Pod Selectors - селекторы подов
- CIDR Rules - правила CIDR
- Policy Validation - валидация политик
- Audit Logging - логирование аудита
- Compliance Check - проверка соответствия
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid


class PolicyType(Enum):
    """Тип политики"""
    INGRESS = "ingress"
    EGRESS = "egress"
    BOTH = "both"


class RuleAction(Enum):
    """Действие правила"""
    ALLOW = "allow"
    DENY = "deny"


class PolicyStatus(Enum):
    """Статус политики"""
    PENDING = "pending"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"


class Protocol(Enum):
    """Протокол"""
    TCP = "TCP"
    UDP = "UDP"
    SCTP = "SCTP"


class IsolationLevel(Enum):
    """Уровень изоляции"""
    NONE = "none"
    PARTIAL = "partial"
    FULL = "full"


@dataclass
class PortRange:
    """Диапазон портов"""
    port: Optional[int] = None
    end_port: Optional[int] = None
    protocol: Protocol = Protocol.TCP
    
    @property
    def display(self) -> str:
        if self.end_port and self.end_port != self.port:
            return f"{self.port}-{self.end_port}/{self.protocol.value}"
        return f"{self.port}/{self.protocol.value}" if self.port else f"*/{self.protocol.value}"


@dataclass
class CIDRBlock:
    """CIDR блок"""
    cidr: str = "0.0.0.0/0"
    except_cidrs: List[str] = field(default_factory=list)
    
    @property
    def display(self) -> str:
        if self.except_cidrs:
            return f"{self.cidr} except {', '.join(self.except_cidrs)}"
        return self.cidr


@dataclass
class PodSelector:
    """Селектор подов"""
    match_labels: Dict[str, str] = field(default_factory=dict)
    match_expressions: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def is_empty(self) -> bool:
        return not self.match_labels and not self.match_expressions


@dataclass
class NamespaceSelector:
    """Селектор namespace"""
    match_labels: Dict[str, str] = field(default_factory=dict)
    match_names: List[str] = field(default_factory=list)


@dataclass
class NetworkPolicyPeer:
    """Участник сетевой политики"""
    peer_id: str
    
    # Selectors
    pod_selector: Optional[PodSelector] = None
    namespace_selector: Optional[NamespaceSelector] = None
    
    # CIDR
    ip_block: Optional[CIDRBlock] = None


@dataclass
class NetworkPolicyRule:
    """Правило сетевой политики"""
    rule_id: str
    name: str = ""
    
    # Peers
    peers: List[NetworkPolicyPeer] = field(default_factory=list)
    
    # Ports
    ports: List[PortRange] = field(default_factory=list)
    
    # Action
    action: RuleAction = RuleAction.ALLOW


@dataclass
class NetworkPolicy:
    """Сетевая политика"""
    policy_id: str
    name: str = ""
    namespace: str = "default"
    
    # Selector
    pod_selector: PodSelector = field(default_factory=PodSelector)
    
    # Type
    policy_type: PolicyType = PolicyType.BOTH
    
    # Rules
    ingress_rules: List[NetworkPolicyRule] = field(default_factory=list)
    egress_rules: List[NetworkPolicyRule] = field(default_factory=list)
    
    # Status
    status: PolicyStatus = PolicyStatus.PENDING
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    
    # Priority (lower = higher priority)
    priority: int = 100


@dataclass
class PolicyAuditEntry:
    """Запись аудита политики"""
    entry_id: str
    policy_id: str = ""
    
    # Action
    action: str = ""  # created, updated, deleted, applied
    
    # User
    user: str = ""
    
    # Details
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Time
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PolicyViolation:
    """Нарушение политики"""
    violation_id: str
    policy_id: str = ""
    
    # Source/Destination
    source_pod: str = ""
    source_namespace: str = ""
    destination_ip: str = ""
    destination_port: int = 0
    
    # Protocol
    protocol: Protocol = Protocol.TCP
    
    # Time
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Action taken
    action_taken: RuleAction = RuleAction.DENY


@dataclass
class NamespaceIsolation:
    """Изоляция namespace"""
    namespace: str = ""
    isolation_level: IsolationLevel = IsolationLevel.NONE
    
    # Default policies
    default_ingress: RuleAction = RuleAction.ALLOW
    default_egress: RuleAction = RuleAction.ALLOW
    
    # Applied policies
    applied_policies: int = 0


class PolicyValidator:
    """Валидатор политик"""
    
    def validate(self, policy: NetworkPolicy) -> tuple[bool, List[str]]:
        """Валидация политики"""
        errors = []
        
        # Check name
        if not policy.name:
            errors.append("Policy name is required")
            
        # Check namespace
        if not policy.namespace:
            errors.append("Policy namespace is required")
            
        # Check selector
        if policy.pod_selector.is_empty:
            # Empty selector selects all pods
            pass
            
        # Check rules
        if policy.policy_type in [PolicyType.INGRESS, PolicyType.BOTH]:
            if not policy.ingress_rules:
                errors.append("Ingress rules required for ingress policy")
                
        if policy.policy_type in [PolicyType.EGRESS, PolicyType.BOTH]:
            if not policy.egress_rules:
                errors.append("Egress rules required for egress policy")
                
        # Validate port ranges
        for rule in policy.ingress_rules + policy.egress_rules:
            for port in rule.ports:
                if port.port and port.end_port:
                    if port.end_port < port.port:
                        errors.append(f"Invalid port range: {port.port}-{port.end_port}")
                        
        return len(errors) == 0, errors


class NetworkPolicyManager:
    """Менеджер сетевых политик"""
    
    def __init__(self):
        self.policies: Dict[str, NetworkPolicy] = {}
        self.validator = PolicyValidator()
        self.audit_log: List[PolicyAuditEntry] = []
        self.violations: List[PolicyViolation] = []
        self.namespace_isolation: Dict[str, NamespaceIsolation] = {}
        
    def create_policy(self, name: str, namespace: str,
                     policy_type: PolicyType = PolicyType.BOTH,
                     pod_selector: Optional[PodSelector] = None) -> NetworkPolicy:
        """Создание политики"""
        policy = NetworkPolicy(
            policy_id=f"netpol_{uuid.uuid4().hex[:8]}",
            name=name,
            namespace=namespace,
            policy_type=policy_type,
            pod_selector=pod_selector or PodSelector()
        )
        
        self.policies[policy.policy_id] = policy
        
        # Audit
        self._audit("created", policy.policy_id, {"name": name, "namespace": namespace})
        
        # Update namespace isolation
        self._update_namespace_isolation(namespace)
        
        return policy
        
    def add_ingress_rule(self, policy_id: str, name: str = "",
                        ports: Optional[List[PortRange]] = None,
                        from_pods: Optional[PodSelector] = None,
                        from_namespace: Optional[NamespaceSelector] = None,
                        from_cidr: Optional[CIDRBlock] = None) -> Optional[NetworkPolicyRule]:
        """Добавление правила ingress"""
        policy = self.policies.get(policy_id)
        if not policy:
            return None
            
        peer = NetworkPolicyPeer(
            peer_id=f"peer_{uuid.uuid4().hex[:8]}",
            pod_selector=from_pods,
            namespace_selector=from_namespace,
            ip_block=from_cidr
        )
        
        rule = NetworkPolicyRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name=name or f"ingress-{len(policy.ingress_rules) + 1}",
            peers=[peer],
            ports=ports or []
        )
        
        policy.ingress_rules.append(rule)
        policy.updated_at = datetime.now()
        
        self._audit("rule_added", policy_id, {"rule": name, "direction": "ingress"})
        
        return rule
        
    def add_egress_rule(self, policy_id: str, name: str = "",
                       ports: Optional[List[PortRange]] = None,
                       to_pods: Optional[PodSelector] = None,
                       to_namespace: Optional[NamespaceSelector] = None,
                       to_cidr: Optional[CIDRBlock] = None) -> Optional[NetworkPolicyRule]:
        """Добавление правила egress"""
        policy = self.policies.get(policy_id)
        if not policy:
            return None
            
        peer = NetworkPolicyPeer(
            peer_id=f"peer_{uuid.uuid4().hex[:8]}",
            pod_selector=to_pods,
            namespace_selector=to_namespace,
            ip_block=to_cidr
        )
        
        rule = NetworkPolicyRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name=name or f"egress-{len(policy.egress_rules) + 1}",
            peers=[peer],
            ports=ports or []
        )
        
        policy.egress_rules.append(rule)
        policy.updated_at = datetime.now()
        
        self._audit("rule_added", policy_id, {"rule": name, "direction": "egress"})
        
        return rule
        
    async def apply_policy(self, policy_id: str) -> bool:
        """Применение политики"""
        policy = self.policies.get(policy_id)
        if not policy:
            return False
            
        # Validate
        valid, errors = self.validator.validate(policy)
        if not valid:
            policy.status = PolicyStatus.ERROR
            policy.annotations["error"] = "; ".join(errors)
            return False
            
        # Simulate apply
        await asyncio.sleep(random.uniform(0.05, 0.15))
        
        policy.status = PolicyStatus.ACTIVE
        self._audit("applied", policy_id, {"status": "active"})
        
        return True
        
    def record_violation(self, policy_id: str, source_pod: str,
                        source_ns: str, dest_ip: str,
                        dest_port: int, protocol: Protocol = Protocol.TCP):
        """Запись нарушения"""
        violation = PolicyViolation(
            violation_id=f"viol_{uuid.uuid4().hex[:8]}",
            policy_id=policy_id,
            source_pod=source_pod,
            source_namespace=source_ns,
            destination_ip=dest_ip,
            destination_port=dest_port,
            protocol=protocol
        )
        self.violations.append(violation)
        
    def _update_namespace_isolation(self, namespace: str):
        """Обновление изоляции namespace"""
        policies_in_ns = [p for p in self.policies.values() if p.namespace == namespace]
        
        has_ingress = any(p.policy_type in [PolicyType.INGRESS, PolicyType.BOTH] for p in policies_in_ns)
        has_egress = any(p.policy_type in [PolicyType.EGRESS, PolicyType.BOTH] for p in policies_in_ns)
        
        if has_ingress and has_egress:
            level = IsolationLevel.FULL
        elif has_ingress or has_egress:
            level = IsolationLevel.PARTIAL
        else:
            level = IsolationLevel.NONE
            
        self.namespace_isolation[namespace] = NamespaceIsolation(
            namespace=namespace,
            isolation_level=level,
            default_ingress=RuleAction.DENY if has_ingress else RuleAction.ALLOW,
            default_egress=RuleAction.DENY if has_egress else RuleAction.ALLOW,
            applied_policies=len(policies_in_ns)
        )
        
    def _audit(self, action: str, policy_id: str, details: Dict[str, Any]):
        """Запись в аудит"""
        entry = PolicyAuditEntry(
            entry_id=f"audit_{uuid.uuid4().hex[:8]}",
            policy_id=policy_id,
            action=action,
            user="system",
            details=details
        )
        self.audit_log.append(entry)
        
    def get_policies_by_namespace(self, namespace: str) -> List[NetworkPolicy]:
        """Получить политики namespace"""
        return [p for p in self.policies.values() if p.namespace == namespace]
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        active = [p for p in self.policies.values() if p.status == PolicyStatus.ACTIVE]
        
        return {
            "total_policies": len(self.policies),
            "active_policies": len(active),
            "pending_policies": len([p for p in self.policies.values() if p.status == PolicyStatus.PENDING]),
            "error_policies": len([p for p in self.policies.values() if p.status == PolicyStatus.ERROR]),
            "total_ingress_rules": sum(len(p.ingress_rules) for p in self.policies.values()),
            "total_egress_rules": sum(len(p.egress_rules) for p in self.policies.values()),
            "namespaces_with_policies": len(self.namespace_isolation),
            "violations_recorded": len(self.violations),
            "audit_entries": len(self.audit_log)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 216: Network Policy Platform")
    print("=" * 60)
    
    manager = NetworkPolicyManager()
    print("✓ Network Policy Platform created")
    
    # Create policies
    print("\n🔒 Creating Network Policies...")
    
    # Policy 1: Frontend to Backend only
    frontend_policy = manager.create_policy(
        "frontend-policy",
        "production",
        PolicyType.BOTH,
        PodSelector(match_labels={"app": "frontend"})
    )
    
    # Add ingress from load balancer
    manager.add_ingress_rule(
        frontend_policy.policy_id,
        "allow-lb",
        [PortRange(port=80, protocol=Protocol.TCP), PortRange(port=443, protocol=Protocol.TCP)],
        from_cidr=CIDRBlock(cidr="10.0.0.0/8")
    )
    
    # Add egress to backend
    manager.add_egress_rule(
        frontend_policy.policy_id,
        "to-backend",
        [PortRange(port=8080, protocol=Protocol.TCP)],
        to_pods=PodSelector(match_labels={"app": "backend"})
    )
    
    await manager.apply_policy(frontend_policy.policy_id)
    print(f"  ✓ {frontend_policy.name}: {len(frontend_policy.ingress_rules)} ingress, {len(frontend_policy.egress_rules)} egress rules")
    
    # Policy 2: Backend - allow from frontend, to database
    backend_policy = manager.create_policy(
        "backend-policy",
        "production",
        PolicyType.BOTH,
        PodSelector(match_labels={"app": "backend"})
    )
    
    manager.add_ingress_rule(
        backend_policy.policy_id,
        "from-frontend",
        [PortRange(port=8080, protocol=Protocol.TCP)],
        from_pods=PodSelector(match_labels={"app": "frontend"})
    )
    
    manager.add_egress_rule(
        backend_policy.policy_id,
        "to-database",
        [PortRange(port=5432, protocol=Protocol.TCP)],
        to_pods=PodSelector(match_labels={"app": "postgres"})
    )
    
    manager.add_egress_rule(
        backend_policy.policy_id,
        "to-redis",
        [PortRange(port=6379, protocol=Protocol.TCP)],
        to_pods=PodSelector(match_labels={"app": "redis"})
    )
    
    await manager.apply_policy(backend_policy.policy_id)
    print(f"  ✓ {backend_policy.name}: {len(backend_policy.ingress_rules)} ingress, {len(backend_policy.egress_rules)} egress rules")
    
    # Policy 3: Database - only from backend
    db_policy = manager.create_policy(
        "database-policy",
        "production",
        PolicyType.INGRESS,
        PodSelector(match_labels={"app": "postgres"})
    )
    
    manager.add_ingress_rule(
        db_policy.policy_id,
        "from-backend",
        [PortRange(port=5432, protocol=Protocol.TCP)],
        from_pods=PodSelector(match_labels={"app": "backend"})
    )
    
    await manager.apply_policy(db_policy.policy_id)
    print(f"  ✓ {db_policy.name}: {len(db_policy.ingress_rules)} ingress rules")
    
    # Policy 4: Deny all external
    deny_external = manager.create_policy(
        "deny-external",
        "production",
        PolicyType.EGRESS,
        PodSelector()  # All pods
    )
    
    manager.add_egress_rule(
        deny_external.policy_id,
        "internal-only",
        [PortRange(protocol=Protocol.TCP)],
        to_cidr=CIDRBlock(cidr="10.0.0.0/8")
    )
    
    await manager.apply_policy(deny_external.policy_id)
    print(f"  ✓ {deny_external.name}: restricts external traffic")
    
    # Policy 5: Monitoring namespace
    monitoring_policy = manager.create_policy(
        "monitoring-policy",
        "monitoring",
        PolicyType.INGRESS,
        PodSelector(match_labels={"app": "prometheus"})
    )
    
    manager.add_ingress_rule(
        monitoring_policy.policy_id,
        "scrape-targets",
        [PortRange(port=9090, protocol=Protocol.TCP)],
        from_namespace=NamespaceSelector(match_names=["production", "staging"])
    )
    
    await manager.apply_policy(monitoring_policy.policy_id)
    print(f"  ✓ {monitoring_policy.name}: cross-namespace access")
    
    # Simulate violations
    print("\n🚨 Simulating Policy Violations...")
    
    violations_data = [
        ("web-pod-1", "production", "8.8.8.8", 53),
        ("api-pod-2", "production", "203.0.113.1", 443),
        ("worker-pod-1", "production", "external.api.com", 8080),
    ]
    
    for source, ns, dest, port in violations_data:
        manager.record_violation(deny_external.policy_id, source, ns, dest, port)
        print(f"  ⚠ {source} -> {dest}:{port} DENIED")
        
    # Display policies
    print("\n📋 Network Policies:")
    
    print("\n  ┌─────────────────────┬────────────┬──────────┬────────┬──────────┐")
    print("  │ Policy              │ Namespace  │ Type     │ Rules  │ Status   │")
    print("  ├─────────────────────┼────────────┼──────────┼────────┼──────────┤")
    
    for policy in manager.policies.values():
        name = policy.name[:19].ljust(19)
        ns = policy.namespace[:10].ljust(10)
        ptype = policy.policy_type.value[:8].ljust(8)
        rules = f"{len(policy.ingress_rules) + len(policy.egress_rules)}".center(6)
        
        status_icons = {
            PolicyStatus.ACTIVE: "🟢",
            PolicyStatus.PENDING: "🟡",
            PolicyStatus.ERROR: "🔴",
            PolicyStatus.DISABLED: "⚫"
        }
        status = f"{status_icons.get(policy.status, '⚪')} {policy.status.value[:6]}"[:8].ljust(8)
        
        print(f"  │ {name} │ {ns} │ {ptype} │ {rules} │ {status} │")
        
    print("  └─────────────────────┴────────────┴──────────┴────────┴──────────┘")
    
    # Namespace isolation
    print("\n🏷 Namespace Isolation:")
    
    for ns, isolation in manager.namespace_isolation.items():
        level_icons = {
            IsolationLevel.NONE: "⚪",
            IsolationLevel.PARTIAL: "🟡",
            IsolationLevel.FULL: "🟢"
        }
        icon = level_icons.get(isolation.isolation_level, "⚪")
        
        print(f"  {icon} {ns}:")
        print(f"      Isolation: {isolation.isolation_level.value}")
        print(f"      Default Ingress: {isolation.default_ingress.value}")
        print(f"      Default Egress: {isolation.default_egress.value}")
        print(f"      Policies: {isolation.applied_policies}")
        
    # Policy rules detail
    print("\n📜 Policy Rules Detail:")
    
    for policy in list(manager.policies.values())[:3]:
        print(f"\n  {policy.name} ({policy.namespace}):")
        
        if policy.ingress_rules:
            print("    Ingress:")
            for rule in policy.ingress_rules:
                ports_str = ", ".join(p.display for p in rule.ports) if rule.ports else "*"
                print(f"      - {rule.name}: ports {ports_str}")
                
        if policy.egress_rules:
            print("    Egress:")
            for rule in policy.egress_rules:
                ports_str = ", ".join(p.display for p in rule.ports) if rule.ports else "*"
                print(f"      - {rule.name}: ports {ports_str}")
                
    # Audit log
    print("\n📝 Recent Audit Log:")
    
    for entry in manager.audit_log[-5:]:
        time_str = entry.timestamp.strftime("%H:%M:%S")
        policy_name = manager.policies.get(entry.policy_id)
        policy_name = policy_name.name if policy_name else "unknown"
        print(f"  [{time_str}] {entry.action}: {policy_name} - {entry.details}")
        
    # Violations summary
    print("\n🚨 Violations Summary:")
    
    violations_by_dest = {}
    for v in manager.violations:
        if v.destination_ip not in violations_by_dest:
            violations_by_dest[v.destination_ip] = 0
        violations_by_dest[v.destination_ip] += 1
        
    for dest, count in violations_by_dest.items():
        bar = "█" * count + "░" * (5 - count)
        print(f"  {dest:20s} [{bar}] {count}")
        
    # Policies by type
    print("\n📊 Policies by Type:")
    
    by_type = {}
    for policy in manager.policies.values():
        t = policy.policy_type.value
        if t not in by_type:
            by_type[t] = 0
        by_type[t] += 1
        
    for ptype, count in by_type.items():
        bar = "█" * count + "░" * (5 - count)
        print(f"  {ptype:10s} [{bar}] {count}")
        
    # Statistics
    stats = manager.get_statistics()
    
    print("\n📈 Platform Statistics:")
    
    print(f"\n  Total Policies: {stats['total_policies']}")
    print(f"  Active: {stats['active_policies']}")
    print(f"  Pending: {stats['pending_policies']}")
    print(f"  Ingress Rules: {stats['total_ingress_rules']}")
    print(f"  Egress Rules: {stats['total_egress_rules']}")
    print(f"  Namespaces: {stats['namespaces_with_policies']}")
    print(f"  Violations: {stats['violations_recorded']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                     Network Policy Dashboard                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Policies:                {stats['total_policies']:>12}                        │")
    print(f"│ Active Policies:               {stats['active_policies']:>12}                        │")
    print(f"│ Total Rules:                   {stats['total_ingress_rules'] + stats['total_egress_rules']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Violations Blocked:            {stats['violations_recorded']:>12}                        │")
    print(f"│ Audit Entries:                 {stats['audit_entries']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Network Policy Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
