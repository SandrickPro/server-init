#!/usr/bin/env python3
"""
Server Init - Iteration 199: Policy Engine Platform
Платформа движка политик

Функционал:
- Policy Definition - определение политик
- Policy Evaluation - оценка политик
- Rule Engine - движок правил
- Decision Making - принятие решений
- Audit Logging - логирование аудита
- Policy Versioning - версионирование политик
- Conflict Resolution - разрешение конфликтов
- Policy Testing - тестирование политик
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid


class PolicyType(Enum):
    """Тип политики"""
    ACCESS = "access"
    RESOURCE = "resource"
    NETWORK = "network"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    CUSTOM = "custom"


class PolicyEffect(Enum):
    """Эффект политики"""
    ALLOW = "allow"
    DENY = "deny"
    AUDIT = "audit"


class EvaluationResult(Enum):
    """Результат оценки"""
    ALLOW = "allow"
    DENY = "deny"
    NOT_APPLICABLE = "not_applicable"


class RuleOperator(Enum):
    """Оператор правила"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    REGEX = "regex"


@dataclass
class Condition:
    """Условие"""
    condition_id: str
    field: str = ""
    operator: RuleOperator = RuleOperator.EQUALS
    value: Any = None
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Оценка условия"""
        field_value = context.get(self.field)
        
        if self.operator == RuleOperator.EQUALS:
            return field_value == self.value
        elif self.operator == RuleOperator.NOT_EQUALS:
            return field_value != self.value
        elif self.operator == RuleOperator.IN:
            return field_value in self.value
        elif self.operator == RuleOperator.NOT_IN:
            return field_value not in self.value
        elif self.operator == RuleOperator.CONTAINS:
            return self.value in str(field_value)
        elif self.operator == RuleOperator.STARTS_WITH:
            return str(field_value).startswith(str(self.value))
        elif self.operator == RuleOperator.GREATER_THAN:
            return float(field_value) > float(self.value)
        elif self.operator == RuleOperator.LESS_THAN:
            return float(field_value) < float(self.value)
            
        return False


@dataclass
class Rule:
    """Правило"""
    rule_id: str
    name: str = ""
    description: str = ""
    
    # Conditions
    conditions: List[Condition] = field(default_factory=list)
    
    # Logic
    all_conditions: bool = True  # AND vs OR
    
    # Effect
    effect: PolicyEffect = PolicyEffect.ALLOW
    
    # Priority
    priority: int = 100
    
    # Enabled
    is_enabled: bool = True
    
    def evaluate(self, context: Dict[str, Any]) -> Optional[PolicyEffect]:
        """Оценка правила"""
        if not self.is_enabled:
            return None
            
        if not self.conditions:
            return self.effect
            
        if self.all_conditions:
            # AND logic
            if all(c.evaluate(context) for c in self.conditions):
                return self.effect
        else:
            # OR logic
            if any(c.evaluate(context) for c in self.conditions):
                return self.effect
                
        return None


@dataclass
class Policy:
    """Политика"""
    policy_id: str
    name: str = ""
    description: str = ""
    
    # Type
    policy_type: PolicyType = PolicyType.ACCESS
    
    # Rules
    rules: List[Rule] = field(default_factory=list)
    
    # Target
    target_resources: List[str] = field(default_factory=list)
    target_actions: List[str] = field(default_factory=list)
    
    # Version
    version: int = 1
    
    # Metadata
    owner: str = ""
    tags: List[str] = field(default_factory=list)
    
    # State
    is_enabled: bool = True
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class EvaluationRequest:
    """Запрос на оценку"""
    request_id: str
    
    # Subject
    subject: Dict[str, Any] = field(default_factory=dict)
    
    # Action
    action: str = ""
    
    # Resource
    resource: str = ""
    resource_type: str = ""
    
    # Context
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Time
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EvaluationResponse:
    """Ответ на оценку"""
    response_id: str
    request_id: str
    
    # Result
    result: EvaluationResult = EvaluationResult.DENY
    
    # Applied policies
    applied_policies: List[str] = field(default_factory=list)
    
    # Reasons
    reasons: List[str] = field(default_factory=list)
    
    # Time
    evaluated_at: datetime = field(default_factory=datetime.now)
    duration_ms: float = 0


@dataclass
class AuditLog:
    """Запись аудита"""
    audit_id: str
    
    # Request/Response
    request_id: str = ""
    result: EvaluationResult = EvaluationResult.DENY
    
    # Context
    subject: str = ""
    action: str = ""
    resource: str = ""
    
    # Policies
    applied_policies: List[str] = field(default_factory=list)
    
    # Time
    timestamp: datetime = field(default_factory=datetime.now)


class PolicyRepository:
    """Репозиторий политик"""
    
    def __init__(self):
        self.policies: Dict[str, Policy] = {}
        self.versions: Dict[str, List[Policy]] = {}
        
    def add(self, policy: Policy):
        """Добавление политики"""
        self.policies[policy.policy_id] = policy
        
        if policy.policy_id not in self.versions:
            self.versions[policy.policy_id] = []
        self.versions[policy.policy_id].append(policy)
        
    def update(self, policy_id: str, updates: Dict[str, Any]) -> Policy:
        """Обновление политики"""
        policy = self.policies.get(policy_id)
        if not policy:
            raise ValueError(f"Policy {policy_id} not found")
            
        # Create new version
        new_policy = Policy(
            policy_id=policy.policy_id,
            name=updates.get("name", policy.name),
            description=updates.get("description", policy.description),
            policy_type=policy.policy_type,
            rules=updates.get("rules", policy.rules),
            target_resources=updates.get("target_resources", policy.target_resources),
            target_actions=updates.get("target_actions", policy.target_actions),
            version=policy.version + 1,
            owner=policy.owner,
            tags=updates.get("tags", policy.tags),
            is_enabled=updates.get("is_enabled", policy.is_enabled),
            created_at=policy.created_at,
            updated_at=datetime.now()
        )
        
        self.policies[policy_id] = new_policy
        self.versions[policy_id].append(new_policy)
        
        return new_policy
        
    def get_by_type(self, policy_type: PolicyType) -> List[Policy]:
        """Получение политик по типу"""
        return [p for p in self.policies.values() 
                if p.policy_type == policy_type and p.is_enabled]
                
    def get_applicable(self, resource: str, action: str) -> List[Policy]:
        """Получение применимых политик"""
        applicable = []
        for policy in self.policies.values():
            if not policy.is_enabled:
                continue
            if policy.target_resources and resource not in policy.target_resources:
                if not any(resource.startswith(r) for r in policy.target_resources):
                    continue
            if policy.target_actions and action not in policy.target_actions:
                continue
            applicable.append(policy)
        return applicable


class PolicyEvaluator:
    """Оценщик политик"""
    
    def __init__(self, repository: PolicyRepository):
        self.repository = repository
        self.audit_logs: List[AuditLog] = []
        
    async def evaluate(self, request: EvaluationRequest) -> EvaluationResponse:
        """Оценка запроса"""
        start_time = datetime.now()
        
        # Build full context
        context = {
            **request.context,
            **request.subject,
            "action": request.action,
            "resource": request.resource,
            "resource_type": request.resource_type
        }
        
        # Get applicable policies
        policies = self.repository.get_applicable(request.resource, request.action)
        
        response = EvaluationResponse(
            response_id=f"resp_{uuid.uuid4().hex[:8]}",
            request_id=request.request_id
        )
        
        # Default deny
        final_result = EvaluationResult.DENY
        deny_reasons = []
        allow_policies = []
        
        # Evaluate each policy
        for policy in sorted(policies, key=lambda p: p.policy_id):
            for rule in sorted(policy.rules, key=lambda r: r.priority):
                effect = rule.evaluate(context)
                
                if effect == PolicyEffect.DENY:
                    final_result = EvaluationResult.DENY
                    deny_reasons.append(f"{policy.name}: {rule.name}")
                    response.applied_policies.append(policy.policy_id)
                    
                elif effect == PolicyEffect.ALLOW:
                    if not deny_reasons:  # No explicit deny
                        allow_policies.append(policy.policy_id)
                        
        # If any allow and no deny
        if allow_policies and not deny_reasons:
            final_result = EvaluationResult.ALLOW
            response.applied_policies = allow_policies
            response.reasons = ["Allowed by policy"]
        elif deny_reasons:
            response.reasons = deny_reasons
        else:
            response.reasons = ["No matching policy - default deny"]
            
        response.result = final_result
        response.duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        # Audit log
        audit = AuditLog(
            audit_id=f"audit_{uuid.uuid4().hex[:8]}",
            request_id=request.request_id,
            result=final_result,
            subject=str(request.subject.get("id", "unknown")),
            action=request.action,
            resource=request.resource,
            applied_policies=response.applied_policies
        )
        self.audit_logs.append(audit)
        
        return response


class PolicyTestRunner:
    """Тестировщик политик"""
    
    def __init__(self, evaluator: PolicyEvaluator):
        self.evaluator = evaluator
        
    async def run_test(self, name: str, request: EvaluationRequest,
                      expected: EvaluationResult) -> Dict[str, Any]:
        """Запуск теста"""
        response = await self.evaluator.evaluate(request)
        
        passed = response.result == expected
        
        return {
            "name": name,
            "passed": passed,
            "expected": expected.value,
            "actual": response.result.value,
            "reasons": response.reasons
        }


class PolicyEnginePlatform:
    """Платформа движка политик"""
    
    def __init__(self):
        self.repository = PolicyRepository()
        self.evaluator = PolicyEvaluator(self.repository)
        self.test_runner = PolicyTestRunner(self.evaluator)
        
    def create_policy(self, name: str, policy_type: PolicyType,
                     rules: List[Rule], targets: Dict[str, List[str]] = None) -> Policy:
        """Создание политики"""
        targets = targets or {}
        
        policy = Policy(
            policy_id=f"policy_{uuid.uuid4().hex[:8]}",
            name=name,
            policy_type=policy_type,
            rules=rules,
            target_resources=targets.get("resources", []),
            target_actions=targets.get("actions", [])
        )
        
        self.repository.add(policy)
        return policy
        
    async def evaluate(self, subject: Dict[str, Any], action: str,
                      resource: str, context: Dict[str, Any] = None) -> EvaluationResponse:
        """Оценка запроса"""
        request = EvaluationRequest(
            request_id=f"req_{uuid.uuid4().hex[:8]}",
            subject=subject,
            action=action,
            resource=resource,
            context=context or {}
        )
        
        return await self.evaluator.evaluate(request)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_rules = sum(len(p.rules) for p in self.repository.policies.values())
        
        audit_results = {}
        for log in self.evaluator.audit_logs:
            r = log.result.value
            audit_results[r] = audit_results.get(r, 0) + 1
            
        return {
            "total_policies": len(self.repository.policies),
            "total_rules": total_rules,
            "total_evaluations": len(self.evaluator.audit_logs),
            "evaluation_results": audit_results
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 199: Policy Engine Platform")
    print("=" * 60)
    
    platform = PolicyEnginePlatform()
    print("✓ Policy Engine Platform created")
    
    # Create access policies
    print("\n🔐 Creating Access Policies...")
    
    # Admin access policy
    admin_rule = Rule(
        rule_id=f"rule_{uuid.uuid4().hex[:8]}",
        name="Admin Full Access",
        conditions=[
            Condition(
                condition_id=f"cond_{uuid.uuid4().hex[:8]}",
                field="role",
                operator=RuleOperator.EQUALS,
                value="admin"
            )
        ],
        effect=PolicyEffect.ALLOW,
        priority=10
    )
    
    admin_policy = platform.create_policy(
        "Admin Access Policy",
        PolicyType.ACCESS,
        [admin_rule]
    )
    print(f"  ✓ {admin_policy.name}")
    
    # User access policy
    user_read_rule = Rule(
        rule_id=f"rule_{uuid.uuid4().hex[:8]}",
        name="User Read Access",
        conditions=[
            Condition(
                condition_id=f"cond_{uuid.uuid4().hex[:8]}",
                field="role",
                operator=RuleOperator.IN,
                value=["user", "viewer"]
            )
        ],
        effect=PolicyEffect.ALLOW,
        priority=50
    )
    
    user_policy = platform.create_policy(
        "User Access Policy",
        PolicyType.ACCESS,
        [user_read_rule],
        {"actions": ["read", "list"]}
    )
    print(f"  ✓ {user_policy.name}")
    
    # Resource owner policy
    owner_rule = Rule(
        rule_id=f"rule_{uuid.uuid4().hex[:8]}",
        name="Resource Owner Access",
        conditions=[
            Condition(
                condition_id=f"cond_{uuid.uuid4().hex[:8]}",
                field="is_owner",
                operator=RuleOperator.EQUALS,
                value=True
            )
        ],
        effect=PolicyEffect.ALLOW,
        priority=20
    )
    
    owner_policy = platform.create_policy(
        "Resource Owner Policy",
        PolicyType.ACCESS,
        [owner_rule]
    )
    print(f"  ✓ {owner_policy.name}")
    
    # Security policies
    print("\n🛡️ Creating Security Policies...")
    
    # Deny public access
    deny_public_rule = Rule(
        rule_id=f"rule_{uuid.uuid4().hex[:8]}",
        name="Deny Public Access",
        conditions=[
            Condition(
                condition_id=f"cond_{uuid.uuid4().hex[:8]}",
                field="is_authenticated",
                operator=RuleOperator.EQUALS,
                value=False
            )
        ],
        effect=PolicyEffect.DENY,
        priority=1
    )
    
    security_policy = platform.create_policy(
        "Security Baseline Policy",
        PolicyType.SECURITY,
        [deny_public_rule]
    )
    print(f"  ✓ {security_policy.name}")
    
    # Rate limiting policy
    rate_limit_rule = Rule(
        rule_id=f"rule_{uuid.uuid4().hex[:8]}",
        name="Rate Limit Exceeded",
        conditions=[
            Condition(
                condition_id=f"cond_{uuid.uuid4().hex[:8]}",
                field="request_count",
                operator=RuleOperator.GREATER_THAN,
                value=100
            )
        ],
        effect=PolicyEffect.DENY,
        priority=5
    )
    
    rate_policy = platform.create_policy(
        "Rate Limiting Policy",
        PolicyType.SECURITY,
        [rate_limit_rule]
    )
    print(f"  ✓ {rate_policy.name}")
    
    # Evaluate requests
    print("\n📋 Evaluating Requests...")
    
    test_cases = [
        {
            "name": "Admin Read",
            "subject": {"id": "user1", "role": "admin", "is_authenticated": True},
            "action": "read",
            "resource": "/api/users",
            "expected": EvaluationResult.ALLOW
        },
        {
            "name": "User Read",
            "subject": {"id": "user2", "role": "user", "is_authenticated": True},
            "action": "read",
            "resource": "/api/data",
            "expected": EvaluationResult.ALLOW
        },
        {
            "name": "User Write",
            "subject": {"id": "user3", "role": "user", "is_authenticated": True},
            "action": "write",
            "resource": "/api/data",
            "expected": EvaluationResult.DENY
        },
        {
            "name": "Public Access",
            "subject": {"id": "anon", "role": "none", "is_authenticated": False},
            "action": "read",
            "resource": "/api/public",
            "expected": EvaluationResult.DENY
        },
        {
            "name": "Owner Access",
            "subject": {"id": "user4", "role": "user", "is_authenticated": True, "is_owner": True},
            "action": "delete",
            "resource": "/api/documents/123",
            "expected": EvaluationResult.ALLOW
        },
    ]
    
    results = []
    for tc in test_cases:
        response = await platform.evaluate(
            tc["subject"],
            tc["action"],
            tc["resource"]
        )
        
        result_icon = "✅" if response.result == tc["expected"] else "❌"
        print(f"  {result_icon} {tc['name']}: {response.result.value} ({response.duration_ms:.2f}ms)")
        
        results.append({
            "name": tc["name"],
            "expected": tc["expected"],
            "actual": response.result,
            "passed": response.result == tc["expected"]
        })
        
    # Batch evaluation
    print("\n🔄 Batch Evaluation (100 requests)...")
    
    roles = ["admin", "user", "viewer", "guest"]
    actions = ["read", "write", "delete", "list"]
    resources = ["/api/users", "/api/orders", "/api/products", "/api/admin"]
    
    for _ in range(100):
        subject = {
            "id": f"user_{random.randint(1, 100)}",
            "role": random.choice(roles),
            "is_authenticated": random.random() > 0.1,
            "is_owner": random.random() > 0.8,
            "request_count": random.randint(10, 150)
        }
        action = random.choice(actions)
        resource = random.choice(resources)
        
        await platform.evaluate(subject, action, resource)
        
    print(f"  ✓ Evaluated 100 requests")
    
    # Display evaluation results
    print("\n📊 Evaluation Results Summary:")
    
    print("\n  ┌──────────────────────┬──────────┬──────────┬──────────────────┐")
    print("  │ Test Case            │ Expected │ Actual   │ Status           │")
    print("  ├──────────────────────┼──────────┼──────────┼──────────────────┤")
    
    for r in results:
        name = r["name"][:20].ljust(20)
        expected = r["expected"].value[:8].ljust(8)
        actual = r["actual"].value[:8].ljust(8)
        status = "PASSED".ljust(16) if r["passed"] else "FAILED".ljust(16)
        print(f"  │ {name} │ {expected} │ {actual} │ {status} │")
        
    print("  └──────────────────────┴──────────┴──────────┴──────────────────┘")
    
    # Policy statistics
    print("\n📈 Policy Statistics:")
    
    print("\n  ┌─────────────────────────────┬──────────┬──────────┐")
    print("  │ Policy                      │ Type     │ Rules    │")
    print("  ├─────────────────────────────┼──────────┼──────────┤")
    
    for policy in platform.repository.policies.values():
        name = policy.name[:27].ljust(27)
        ptype = policy.policy_type.value[:8].ljust(8)
        rules = str(len(policy.rules)).center(8)
        print(f"  │ {name} │ {ptype} │ {rules} │")
        
    print("  └─────────────────────────────┴──────────┴──────────┘")
    
    # Audit log analysis
    print("\n📝 Audit Log Analysis:")
    
    stats = platform.get_statistics()
    
    total_evals = stats["total_evaluations"]
    eval_results = stats["evaluation_results"]
    
    print(f"\n  Total Evaluations: {total_evals}")
    print("\n  Results Distribution:")
    
    for result, count in eval_results.items():
        pct = (count / total_evals * 100) if total_evals > 0 else 0
        bar = "█" * int(pct / 2) + "░" * (50 - int(pct / 2))
        print(f"    {result:15} [{bar}] {count} ({pct:.1f}%)")
        
    # Recent audit logs
    print("\n  Recent Audit Logs:")
    
    for log in platform.evaluator.audit_logs[-5:]:
        result_icon = "✅" if log.result == EvaluationResult.ALLOW else "❌"
        print(f"    {result_icon} {log.subject} -> {log.action} -> {log.resource[:20]}")
        
    # Final statistics
    print("\n📊 Platform Statistics:")
    
    print(f"\n  Total Policies: {stats['total_policies']}")
    print(f"  Total Rules: {stats['total_rules']}")
    print(f"  Total Evaluations: {stats['total_evaluations']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                     Policy Engine Dashboard                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Policies:                {stats['total_policies']:>12}                        │")
    print(f"│ Total Rules:                   {stats['total_rules']:>12}                        │")
    print(f"│ Total Evaluations:             {stats['total_evaluations']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    allow_count = eval_results.get("allow", 0)
    deny_count = eval_results.get("deny", 0)
    allow_pct = (allow_count / total_evals * 100) if total_evals > 0 else 0
    print(f"│ Allow Rate:                      {allow_pct:>10.1f}%                   │")
    print(f"│ Deny Rate:                       {100 - allow_pct:>10.1f}%                   │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Policy Engine Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
