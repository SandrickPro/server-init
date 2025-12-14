#!/usr/bin/env python3
"""
Server Init - Iteration 136: Policy Engine Platform
Платформа Policy Engine

Функционал:
- Policy Definition - определение политик
- Policy Evaluation - оценка политик
- Rule Engine - движок правил
- Attribute-Based Access - атрибутный доступ
- Compliance Checking - проверка соответствия
- Policy Versioning - версионирование политик
- Decision Logging - логирование решений
- Policy Testing - тестирование политик
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
from collections import defaultdict
import uuid
import re


class PolicyEffect(Enum):
    """Эффект политики"""
    ALLOW = "allow"
    DENY = "deny"


class ConditionOperator(Enum):
    """Оператор условия"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IN = "in"
    NOT_IN = "not_in"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    REGEX = "regex"
    EXISTS = "exists"


class CombiningAlgorithm(Enum):
    """Алгоритм комбинирования"""
    DENY_OVERRIDES = "deny_overrides"
    PERMIT_OVERRIDES = "permit_overrides"
    FIRST_APPLICABLE = "first_applicable"
    ONLY_ONE_APPLICABLE = "only_one_applicable"


@dataclass
class Condition:
    """Условие"""
    attribute: str
    operator: ConditionOperator
    value: Any


@dataclass
class Rule:
    """Правило"""
    rule_id: str
    name: str = ""
    description: str = ""
    
    # Effect
    effect: PolicyEffect = PolicyEffect.ALLOW
    
    # Conditions
    conditions: List[Condition] = field(default_factory=list)
    
    # Target
    target_resources: List[str] = field(default_factory=list)
    target_actions: List[str] = field(default_factory=list)
    
    # Priority
    priority: int = 0
    
    # Enabled
    enabled: bool = True


@dataclass
class Policy:
    """Политика"""
    policy_id: str
    name: str = ""
    description: str = ""
    
    # Version
    version: str = "1.0.0"
    
    # Rules
    rules: List[Rule] = field(default_factory=list)
    
    # Combining
    combining_algorithm: CombiningAlgorithm = CombiningAlgorithm.DENY_OVERRIDES
    
    # Target
    target_subjects: List[str] = field(default_factory=list)
    target_resources: List[str] = field(default_factory=list)
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Enabled
    enabled: bool = True


@dataclass
class PolicySet:
    """Набор политик"""
    policy_set_id: str
    name: str = ""
    description: str = ""
    
    # Policies
    policies: List[Policy] = field(default_factory=list)
    
    # Combining
    combining_algorithm: CombiningAlgorithm = CombiningAlgorithm.DENY_OVERRIDES


@dataclass
class Request:
    """Запрос авторизации"""
    request_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    
    # Subject
    subject_id: str = ""
    subject_attributes: Dict = field(default_factory=dict)
    
    # Resource
    resource_id: str = ""
    resource_type: str = ""
    resource_attributes: Dict = field(default_factory=dict)
    
    # Action
    action: str = ""
    
    # Context
    context: Dict = field(default_factory=dict)


@dataclass
class Decision:
    """Решение"""
    decision_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    request_id: str = ""
    
    # Result
    effect: PolicyEffect = PolicyEffect.DENY
    
    # Details
    applicable_policies: List[str] = field(default_factory=list)
    matched_rules: List[str] = field(default_factory=list)
    
    # Obligations
    obligations: List[Dict] = field(default_factory=list)
    
    # Advice
    advice: List[str] = field(default_factory=list)
    
    # Timing
    evaluation_time_ms: float = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ComplianceCheck:
    """Проверка соответствия"""
    check_id: str
    name: str = ""
    
    # Policies to check
    policy_ids: List[str] = field(default_factory=list)
    
    # Results
    compliant: bool = True
    violations: List[Dict] = field(default_factory=list)
    
    # Timestamp
    checked_at: datetime = field(default_factory=datetime.now)


class ConditionEvaluator:
    """Оценщик условий"""
    
    def evaluate(self, condition: Condition, attributes: Dict) -> bool:
        """Оценка условия"""
        value = attributes.get(condition.attribute)
        
        if condition.operator == ConditionOperator.EXISTS:
            return value is not None
            
        if value is None:
            return False
            
        if condition.operator == ConditionOperator.EQUALS:
            return value == condition.value
        elif condition.operator == ConditionOperator.NOT_EQUALS:
            return value != condition.value
        elif condition.operator == ConditionOperator.CONTAINS:
            return condition.value in str(value)
        elif condition.operator == ConditionOperator.STARTS_WITH:
            return str(value).startswith(condition.value)
        elif condition.operator == ConditionOperator.ENDS_WITH:
            return str(value).endswith(condition.value)
        elif condition.operator == ConditionOperator.IN:
            return value in condition.value
        elif condition.operator == ConditionOperator.NOT_IN:
            return value not in condition.value
        elif condition.operator == ConditionOperator.GREATER_THAN:
            return value > condition.value
        elif condition.operator == ConditionOperator.LESS_THAN:
            return value < condition.value
        elif condition.operator == ConditionOperator.REGEX:
            return bool(re.match(condition.value, str(value)))
            
        return False


class RuleEngine:
    """Движок правил"""
    
    def __init__(self):
        self.condition_evaluator = ConditionEvaluator()
        
    def evaluate_rule(self, rule: Rule, request: Request) -> Optional[PolicyEffect]:
        """Оценка правила"""
        if not rule.enabled:
            return None
            
        # Check target resources
        if rule.target_resources:
            if not any(self._matches_pattern(request.resource_type, pattern) 
                      for pattern in rule.target_resources):
                return None
                
        # Check target actions
        if rule.target_actions:
            if not any(self._matches_pattern(request.action, pattern)
                      for pattern in rule.target_actions):
                return None
                
        # Merge all attributes
        all_attributes = {
            **request.subject_attributes,
            **request.resource_attributes,
            **request.context,
            "subject_id": request.subject_id,
            "resource_id": request.resource_id,
            "resource_type": request.resource_type,
            "action": request.action
        }
        
        # Evaluate conditions
        for condition in rule.conditions:
            if not self.condition_evaluator.evaluate(condition, all_attributes):
                return None
                
        return rule.effect
        
    def _matches_pattern(self, value: str, pattern: str) -> bool:
        """Проверка соответствия паттерну"""
        if pattern == "*":
            return True
        if pattern.endswith("*"):
            return value.startswith(pattern[:-1])
        if pattern.startswith("*"):
            return value.endswith(pattern[1:])
        return value == pattern


class PolicyEvaluator:
    """Оценщик политик"""
    
    def __init__(self):
        self.rule_engine = RuleEngine()
        self.decisions: List[Decision] = []
        
    def evaluate(self, policy: Policy, request: Request) -> Optional[PolicyEffect]:
        """Оценка политики"""
        if not policy.enabled:
            return None
            
        # Check target subjects
        if policy.target_subjects:
            if request.subject_id not in policy.target_subjects:
                return None
                
        # Check target resources
        if policy.target_resources:
            if not any(self._matches_pattern(request.resource_type, pattern)
                      for pattern in policy.target_resources):
                return None
                
        # Sort rules by priority
        sorted_rules = sorted(policy.rules, key=lambda r: r.priority, reverse=True)
        
        # Evaluate rules based on combining algorithm
        effects = []
        
        for rule in sorted_rules:
            effect = self.rule_engine.evaluate_rule(rule, request)
            if effect is not None:
                effects.append(effect)
                
                if policy.combining_algorithm == CombiningAlgorithm.FIRST_APPLICABLE:
                    return effect
                    
        if not effects:
            return None
            
        # Apply combining algorithm
        if policy.combining_algorithm == CombiningAlgorithm.DENY_OVERRIDES:
            if PolicyEffect.DENY in effects:
                return PolicyEffect.DENY
            return PolicyEffect.ALLOW
        elif policy.combining_algorithm == CombiningAlgorithm.PERMIT_OVERRIDES:
            if PolicyEffect.ALLOW in effects:
                return PolicyEffect.ALLOW
            return PolicyEffect.DENY
        elif policy.combining_algorithm == CombiningAlgorithm.ONLY_ONE_APPLICABLE:
            if len([e for e in effects if e is not None]) == 1:
                return effects[0]
            return None
            
        return effects[0] if effects else None
        
    def _matches_pattern(self, value: str, pattern: str) -> bool:
        """Проверка соответствия паттерну"""
        if pattern == "*":
            return True
        if pattern.endswith("*"):
            return value.startswith(pattern[:-1])
        if pattern.startswith("*"):
            return value.endswith(pattern[1:])
        return value == pattern


class PolicyManager:
    """Менеджер политик"""
    
    def __init__(self):
        self.policies: Dict[str, Policy] = {}
        self.policy_sets: Dict[str, PolicySet] = {}
        self.versions: Dict[str, List[Policy]] = defaultdict(list)
        
    def create_policy(self, name: str, description: str = "",
                       combining_algorithm: CombiningAlgorithm = CombiningAlgorithm.DENY_OVERRIDES,
                       **kwargs) -> Policy:
        """Создание политики"""
        policy = Policy(
            policy_id=f"policy_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            combining_algorithm=combining_algorithm,
            **kwargs
        )
        self.policies[policy.policy_id] = policy
        self.versions[name].append(policy)
        return policy
        
    def add_rule(self, policy_id: str, name: str, effect: PolicyEffect,
                  conditions: List[Dict] = None, **kwargs) -> Rule:
        """Добавление правила"""
        policy = self.policies.get(policy_id)
        if not policy:
            return None
            
        parsed_conditions = []
        if conditions:
            for cond in conditions:
                parsed_conditions.append(Condition(
                    attribute=cond["attribute"],
                    operator=ConditionOperator(cond["operator"]),
                    value=cond["value"]
                ))
                
        rule = Rule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name=name,
            effect=effect,
            conditions=parsed_conditions,
            **kwargs
        )
        policy.rules.append(rule)
        policy.updated_at = datetime.now()
        return rule
        
    def create_policy_set(self, name: str, policy_ids: List[str],
                           combining_algorithm: CombiningAlgorithm = CombiningAlgorithm.DENY_OVERRIDES) -> PolicySet:
        """Создание набора политик"""
        policies = [self.policies[pid] for pid in policy_ids if pid in self.policies]
        
        policy_set = PolicySet(
            policy_set_id=f"pset_{uuid.uuid4().hex[:8]}",
            name=name,
            policies=policies,
            combining_algorithm=combining_algorithm
        )
        self.policy_sets[policy_set.policy_set_id] = policy_set
        return policy_set
        
    def get_policy_versions(self, name: str) -> List[Dict]:
        """Получение версий политики"""
        return [
            {"version": p.version, "created_at": p.created_at.isoformat()}
            for p in self.versions.get(name, [])
        ]


class PolicyDecisionPoint:
    """Точка принятия решений (PDP)"""
    
    def __init__(self, policy_manager: PolicyManager):
        self.policy_manager = policy_manager
        self.evaluator = PolicyEvaluator()
        self.decision_log: List[Decision] = []
        
    def authorize(self, request: Request, policy_ids: List[str] = None) -> Decision:
        """Авторизация запроса"""
        start_time = datetime.now()
        
        decision = Decision(
            request_id=request.request_id
        )
        
        # Get applicable policies
        if policy_ids:
            policies = [self.policy_manager.policies[pid] 
                       for pid in policy_ids if pid in self.policy_manager.policies]
        else:
            policies = list(self.policy_manager.policies.values())
            
        effects = []
        
        for policy in policies:
            effect = self.evaluator.evaluate(policy, request)
            if effect is not None:
                decision.applicable_policies.append(policy.policy_id)
                effects.append(effect)
                
        # Combine effects (default deny overrides)
        if not effects:
            decision.effect = PolicyEffect.DENY
            decision.advice.append("No applicable policies found")
        elif PolicyEffect.DENY in effects:
            decision.effect = PolicyEffect.DENY
        else:
            decision.effect = PolicyEffect.ALLOW
            
        # Calculate timing
        decision.evaluation_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        # Log decision
        self.decision_log.append(decision)
        
        return decision


class ComplianceChecker:
    """Проверщик соответствия"""
    
    def __init__(self, policy_manager: PolicyManager, pdp: PolicyDecisionPoint):
        self.policy_manager = policy_manager
        self.pdp = pdp
        self.checks: List[ComplianceCheck] = []
        
    def check_compliance(self, name: str, test_requests: List[Request],
                          expected_effects: List[PolicyEffect],
                          policy_ids: List[str] = None) -> ComplianceCheck:
        """Проверка соответствия"""
        check = ComplianceCheck(
            check_id=f"check_{uuid.uuid4().hex[:8]}",
            name=name,
            policy_ids=policy_ids or []
        )
        
        for request, expected in zip(test_requests, expected_effects):
            decision = self.pdp.authorize(request, policy_ids)
            
            if decision.effect != expected:
                check.compliant = False
                check.violations.append({
                    "request_id": request.request_id,
                    "expected": expected.value,
                    "actual": decision.effect.value,
                    "subject": request.subject_id,
                    "action": request.action,
                    "resource": request.resource_type
                })
                
        self.checks.append(check)
        return check


class PolicyTester:
    """Тестер политик"""
    
    def __init__(self, pdp: PolicyDecisionPoint):
        self.pdp = pdp
        
    def test_policy(self, policy_id: str, test_cases: List[Dict]) -> Dict:
        """Тестирование политики"""
        results = {"passed": 0, "failed": 0, "details": []}
        
        for case in test_cases:
            request = Request(
                subject_id=case.get("subject_id", ""),
                subject_attributes=case.get("subject_attributes", {}),
                resource_id=case.get("resource_id", ""),
                resource_type=case.get("resource_type", ""),
                resource_attributes=case.get("resource_attributes", {}),
                action=case.get("action", ""),
                context=case.get("context", {})
            )
            
            expected = PolicyEffect(case.get("expected", "deny"))
            decision = self.pdp.authorize(request, [policy_id])
            
            passed = decision.effect == expected
            
            if passed:
                results["passed"] += 1
            else:
                results["failed"] += 1
                
            results["details"].append({
                "case": case.get("name", "unnamed"),
                "passed": passed,
                "expected": expected.value,
                "actual": decision.effect.value
            })
            
        return results


class PolicyEnginePlatform:
    """Платформа Policy Engine"""
    
    def __init__(self):
        self.policy_manager = PolicyManager()
        self.pdp = PolicyDecisionPoint(self.policy_manager)
        self.compliance_checker = ComplianceChecker(self.policy_manager, self.pdp)
        self.tester = PolicyTester(self.pdp)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        return {
            "policies": len(self.policy_manager.policies),
            "policy_sets": len(self.policy_manager.policy_sets),
            "total_rules": sum(len(p.rules) for p in self.policy_manager.policies.values()),
            "decisions": len(self.pdp.decision_log),
            "allowed": len([d for d in self.pdp.decision_log if d.effect == PolicyEffect.ALLOW]),
            "denied": len([d for d in self.pdp.decision_log if d.effect == PolicyEffect.DENY]),
            "compliance_checks": len(self.compliance_checker.checks)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 136: Policy Engine Platform")
    print("=" * 60)
    
    async def demo():
        platform = PolicyEnginePlatform()
        print("✓ Policy Engine Platform created")
        
        # Create policies
        print("\n📜 Creating Policies...")
        
        # Admin policy
        admin_policy = platform.policy_manager.create_policy(
            "admin-full-access",
            "Full access for administrators",
            CombiningAlgorithm.PERMIT_OVERRIDES,
            tags=["admin", "full-access"]
        )
        
        platform.policy_manager.add_rule(
            admin_policy.policy_id,
            "admin-allow-all",
            PolicyEffect.ALLOW,
            conditions=[
                {"attribute": "role", "operator": "equals", "value": "admin"}
            ],
            target_resources=["*"],
            target_actions=["*"],
            priority=100
        )
        
        print(f"  ✓ {admin_policy.name}")
        
        # User policy
        user_policy = platform.policy_manager.create_policy(
            "user-read-access",
            "Read access for regular users",
            CombiningAlgorithm.DENY_OVERRIDES,
            tags=["user", "read"]
        )
        
        platform.policy_manager.add_rule(
            user_policy.policy_id,
            "user-read-own",
            PolicyEffect.ALLOW,
            conditions=[
                {"attribute": "role", "operator": "in", "value": ["user", "viewer"]},
                {"attribute": "owner_id", "operator": "equals", "value": "${subject_id}"}
            ],
            target_resources=["documents", "files"],
            target_actions=["read", "list"],
            priority=50
        )
        
        platform.policy_manager.add_rule(
            user_policy.policy_id,
            "deny-delete-for-users",
            PolicyEffect.DENY,
            conditions=[
                {"attribute": "role", "operator": "equals", "value": "user"}
            ],
            target_actions=["delete"],
            priority=60
        )
        
        print(f"  ✓ {user_policy.name}")
        
        # Resource policy
        resource_policy = platform.policy_manager.create_policy(
            "sensitive-data-protection",
            "Protection for sensitive data",
            CombiningAlgorithm.DENY_OVERRIDES,
            tags=["security", "sensitive"]
        )
        
        platform.policy_manager.add_rule(
            resource_policy.policy_id,
            "deny-sensitive-external",
            PolicyEffect.DENY,
            conditions=[
                {"attribute": "sensitivity", "operator": "equals", "value": "high"},
                {"attribute": "network", "operator": "equals", "value": "external"}
            ],
            target_resources=["*"],
            target_actions=["read", "write", "delete"],
            priority=90
        )
        
        platform.policy_manager.add_rule(
            resource_policy.policy_id,
            "allow-sensitive-internal",
            PolicyEffect.ALLOW,
            conditions=[
                {"attribute": "network", "operator": "equals", "value": "internal"},
                {"attribute": "clearance", "operator": "greater_than", "value": 3}
            ],
            target_resources=["*"],
            target_actions=["read"],
            priority=80
        )
        
        print(f"  ✓ {resource_policy.name}")
        
        # Time-based policy
        time_policy = platform.policy_manager.create_policy(
            "business-hours-access",
            "Access only during business hours",
            CombiningAlgorithm.DENY_OVERRIDES,
            tags=["time", "business"]
        )
        
        platform.policy_manager.add_rule(
            time_policy.policy_id,
            "allow-business-hours",
            PolicyEffect.ALLOW,
            conditions=[
                {"attribute": "hour", "operator": "greater_than", "value": 8},
                {"attribute": "hour", "operator": "less_than", "value": 18}
            ],
            target_resources=["*"],
            target_actions=["*"],
            priority=40
        )
        
        print(f"  ✓ {time_policy.name}")
        
        # Create policy set
        print("\n📦 Creating Policy Set...")
        
        policy_set = platform.policy_manager.create_policy_set(
            "default-policy-set",
            [admin_policy.policy_id, user_policy.policy_id, resource_policy.policy_id],
            CombiningAlgorithm.DENY_OVERRIDES
        )
        
        print(f"  ✓ {policy_set.name}: {len(policy_set.policies)} policies")
        
        # Test authorization
        print("\n🔐 Testing Authorization...")
        
        test_requests = [
            # Admin request
            Request(
                subject_id="admin-001",
                subject_attributes={"role": "admin", "department": "IT"},
                resource_id="doc-123",
                resource_type="documents",
                resource_attributes={"sensitivity": "high", "owner_id": "user-001"},
                action="delete",
                context={"network": "internal", "hour": 14}
            ),
            # User read own
            Request(
                subject_id="user-001",
                subject_attributes={"role": "user", "clearance": 2},
                resource_id="doc-456",
                resource_type="documents",
                resource_attributes={"sensitivity": "low", "owner_id": "user-001"},
                action="read",
                context={"network": "internal", "hour": 10}
            ),
            # User delete (denied)
            Request(
                subject_id="user-002",
                subject_attributes={"role": "user", "clearance": 1},
                resource_id="doc-789",
                resource_type="files",
                resource_attributes={"sensitivity": "low", "owner_id": "user-002"},
                action="delete",
                context={"network": "internal", "hour": 12}
            ),
            # External sensitive access
            Request(
                subject_id="user-003",
                subject_attributes={"role": "viewer", "clearance": 5},
                resource_id="doc-secret",
                resource_type="documents",
                resource_attributes={"sensitivity": "high", "owner_id": "admin-001"},
                action="read",
                context={"network": "external", "hour": 15}
            )
        ]
        
        for request in test_requests:
            decision = platform.pdp.authorize(request)
            
            icon = "✅" if decision.effect == PolicyEffect.ALLOW else "❌"
            print(f"\n  {icon} Subject: {request.subject_id}")
            print(f"     Action: {request.action} on {request.resource_type}")
            print(f"     Decision: {decision.effect.value}")
            print(f"     Applicable Policies: {len(decision.applicable_policies)}")
            print(f"     Time: {decision.evaluation_time_ms:.2f}ms")
            
        # Compliance check
        print("\n📋 Compliance Check...")
        
        compliance_requests = [
            Request(
                subject_id="admin-test",
                subject_attributes={"role": "admin"},
                resource_type="documents",
                action="delete",
                context={"network": "internal"}
            ),
            Request(
                subject_id="user-test",
                subject_attributes={"role": "user"},
                resource_type="documents",
                action="delete",
                context={"network": "internal"}
            )
        ]
        
        expected = [PolicyEffect.ALLOW, PolicyEffect.DENY]
        
        check = platform.compliance_checker.check_compliance(
            "admin-vs-user-delete",
            compliance_requests,
            expected
        )
        
        status = "✅ Compliant" if check.compliant else "❌ Non-compliant"
        print(f"  {status}")
        
        if check.violations:
            for violation in check.violations:
                print(f"    Violation: {violation}")
                
        # Policy testing
        print("\n🧪 Policy Testing...")
        
        test_cases = [
            {
                "name": "admin-full-access",
                "subject_id": "admin",
                "subject_attributes": {"role": "admin"},
                "resource_type": "secrets",
                "action": "delete",
                "expected": "allow"
            },
            {
                "name": "user-denied-delete",
                "subject_id": "user",
                "subject_attributes": {"role": "user"},
                "resource_type": "documents",
                "action": "delete",
                "expected": "deny"
            }
        ]
        
        for policy in [admin_policy, user_policy]:
            results = platform.tester.test_policy(policy.policy_id, test_cases)
            print(f"\n  {policy.name}:")
            print(f"    Passed: {results['passed']}")
            print(f"    Failed: {results['failed']}")
            
            for detail in results["details"]:
                icon = "✓" if detail["passed"] else "✗"
                print(f"    {icon} {detail['case']}: {detail['actual']}")
                
        # Policy versions
        print("\n📚 Policy Versions:")
        
        for policy_name in ["admin-full-access", "user-read-access"]:
            versions = platform.policy_manager.get_policy_versions(policy_name)
            print(f"  {policy_name}: {len(versions)} version(s)")
            
        # Decision log
        print("\n📝 Recent Decisions:")
        
        for decision in platform.pdp.decision_log[-3:]:
            print(f"  [{decision.timestamp.strftime('%H:%M:%S')}] "
                  f"Request {decision.request_id}: {decision.effect.value}")
            
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Policies: {stats['policies']}")
        print(f"  Policy Sets: {stats['policy_sets']}")
        print(f"  Total Rules: {stats['total_rules']}")
        print(f"  Decisions: {stats['decisions']}")
        print(f"    Allowed: {stats['allowed']}")
        print(f"    Denied: {stats['denied']}")
        print(f"  Compliance Checks: {stats['compliance_checks']}")
        
        # Dashboard
        print("\n📋 Policy Engine Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │                 Policy Engine Overview                      │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Policies:           {stats['policies']:>10}                        │")
        print(f"  │ Policy Sets:        {stats['policy_sets']:>10}                        │")
        print(f"  │ Total Rules:        {stats['total_rules']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Decisions:    {stats['decisions']:>10}                        │")
        print(f"  │   Allowed:          {stats['allowed']:>10}                        │")
        print(f"  │   Denied:           {stats['denied']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Compliance Checks:  {stats['compliance_checks']:>10}                        │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Policy Engine Platform initialized!")
    print("=" * 60)
