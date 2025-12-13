#!/usr/bin/env python3
"""
Server Init - Iteration 71: Policy Engine Platform (OPA-style)
Движок политик для авторизации и соответствия

Функционал:
- Policy Definition - определение политик
- Policy Evaluation - оценка политик
- Policy Bundles - пакеты политик
- Decision Logging - логирование решений
- Policy Testing - тестирование политик
- Input Transformation - преобразование входных данных
- Policy Discovery - обнаружение политик
- Rego-like DSL - язык описания политик
"""

import json
import asyncio
import re
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
from collections import defaultdict
import uuid
import hashlib


class PolicyDecision(Enum):
    """Решение политики"""
    ALLOW = "allow"
    DENY = "deny"
    UNKNOWN = "unknown"


class PolicyStatus(Enum):
    """Статус политики"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TESTING = "testing"
    DEPRECATED = "deprecated"


class RuleType(Enum):
    """Тип правила"""
    ALLOW = "allow"
    DENY = "deny"
    DEFAULT = "default"
    CONDITIONAL = "conditional"


@dataclass
class PolicyRule:
    """Правило политики"""
    rule_id: str
    name: str
    
    # Тип
    rule_type: RuleType = RuleType.CONDITIONAL
    
    # Условие (простой DSL)
    condition: str = ""
    
    # Действия
    effect: PolicyDecision = PolicyDecision.ALLOW
    
    # Приоритет
    priority: int = 0
    
    # Сообщение
    message: str = ""


@dataclass
class Policy:
    """Политика"""
    policy_id: str
    name: str
    
    # Версия
    version: str = "1.0.0"
    
    # Правила
    rules: List[PolicyRule] = field(default_factory=list)
    
    # Метаданные
    description: str = ""
    package: str = ""  # Пакет/namespace
    
    # Статус
    status: PolicyStatus = PolicyStatus.ACTIVE
    
    # Аудит
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Теги
    tags: List[str] = field(default_factory=list)


@dataclass
class PolicyBundle:
    """Пакет политик"""
    bundle_id: str
    name: str
    
    # Политики
    policy_ids: List[str] = field(default_factory=list)
    
    # Версия
    version: str = "1.0.0"
    
    # Манифест
    revision: str = ""
    
    # Метаданные
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class EvaluationInput:
    """Входные данные для оценки"""
    subject: Dict[str, Any] = field(default_factory=dict)  # Кто
    resource: Dict[str, Any] = field(default_factory=dict)  # Что
    action: str = ""  # Действие
    context: Dict[str, Any] = field(default_factory=dict)  # Контекст


@dataclass
class EvaluationResult:
    """Результат оценки"""
    result_id: str
    
    # Решение
    decision: PolicyDecision = PolicyDecision.UNKNOWN
    
    # Политика
    policy_id: str = ""
    rule_id: str = ""
    
    # Детали
    message: str = ""
    
    # Время
    evaluated_at: datetime = field(default_factory=datetime.now)
    duration_ms: float = 0.0
    
    # Matched rules
    matched_rules: List[str] = field(default_factory=list)


@dataclass
class DecisionLog:
    """Лог решения"""
    log_id: str
    
    # Запрос
    input_hash: str = ""
    input_data: Dict[str, Any] = field(default_factory=dict)
    
    # Решение
    decision: PolicyDecision = PolicyDecision.UNKNOWN
    
    # Метаданные
    policy_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Трассировка
    trace: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class PolicyTest:
    """Тест политики"""
    test_id: str
    name: str
    
    # Политика
    policy_id: str = ""
    
    # Входные данные
    input_data: EvaluationInput = field(default_factory=EvaluationInput)
    
    # Ожидаемый результат
    expected_decision: PolicyDecision = PolicyDecision.ALLOW
    
    # Результат
    passed: Optional[bool] = None
    actual_decision: Optional[PolicyDecision] = None


class ConditionEvaluator:
    """Оценщик условий"""
    
    def __init__(self):
        self.operators = {
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            ">": lambda a, b: a > b,
            "<": lambda a, b: a < b,
            ">=": lambda a, b: a >= b,
            "<=": lambda a, b: a <= b,
            "in": lambda a, b: a in b if isinstance(b, (list, set, tuple)) else False,
            "contains": lambda a, b: b in a if isinstance(a, str) else b in a if isinstance(a, (list, set)) else False,
            "matches": lambda a, b: bool(re.match(b, str(a))) if isinstance(b, str) else False
        }
        
    def evaluate(self, condition: str, input_data: Dict[str, Any]) -> bool:
        """Оценка условия"""
        if not condition:
            return True
            
        # Парсим условие
        # Формат: field.path operator value [AND|OR field.path operator value]
        
        # Разбиваем по AND/OR
        if " AND " in condition:
            parts = condition.split(" AND ")
            return all(self._evaluate_single(p.strip(), input_data) for p in parts)
        elif " OR " in condition:
            parts = condition.split(" OR ")
            return any(self._evaluate_single(p.strip(), input_data) for p in parts)
        else:
            return self._evaluate_single(condition, input_data)
            
    def _evaluate_single(self, condition: str, input_data: Dict[str, Any]) -> bool:
        """Оценка одного условия"""
        # Находим оператор
        for op in sorted(self.operators.keys(), key=len, reverse=True):
            if f" {op} " in condition:
                parts = condition.split(f" {op} ", 1)
                if len(parts) == 2:
                    field_path = parts[0].strip()
                    value_str = parts[1].strip()
                    
                    actual_value = self._get_value(field_path, input_data)
                    expected_value = self._parse_value(value_str)
                    
                    try:
                        return self.operators[op](actual_value, expected_value)
                    except:
                        return False
                        
        return False
        
    def _get_value(self, path: str, data: Dict[str, Any]) -> Any:
        """Получение значения по пути"""
        parts = path.split(".")
        current = data
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
                
        return current
        
    def _parse_value(self, value_str: str) -> Any:
        """Парсинг значения"""
        # Строка в кавычках
        if (value_str.startswith('"') and value_str.endswith('"')) or \
           (value_str.startswith("'") and value_str.endswith("'")):
            return value_str[1:-1]
            
        # Список
        if value_str.startswith("[") and value_str.endswith("]"):
            try:
                return json.loads(value_str)
            except:
                return []
                
        # Boolean
        if value_str.lower() == "true":
            return True
        if value_str.lower() == "false":
            return False
            
        # Число
        try:
            if "." in value_str:
                return float(value_str)
            return int(value_str)
        except:
            pass
            
        return value_str


class PolicyEvaluator:
    """Оценщик политик"""
    
    def __init__(self):
        self.condition_evaluator = ConditionEvaluator()
        self.decision_logs: List[DecisionLog] = []
        
    def evaluate(self, policy: Policy, input_data: EvaluationInput) -> EvaluationResult:
        """Оценка политики"""
        import time
        start_time = time.time()
        
        result = EvaluationResult(
            result_id=f"eval_{uuid.uuid4().hex[:8]}",
            policy_id=policy.policy_id
        )
        
        # Преобразуем входные данные в словарь
        flat_input = {
            "subject": input_data.subject,
            "resource": input_data.resource,
            "action": input_data.action,
            "context": input_data.context
        }
        
        trace = []
        matched_rules = []
        
        # Сортируем правила по приоритету
        sorted_rules = sorted(policy.rules, key=lambda r: -r.priority)
        
        for rule in sorted_rules:
            trace.append({
                "rule_id": rule.rule_id,
                "rule_name": rule.name,
                "condition": rule.condition
            })
            
            if self.condition_evaluator.evaluate(rule.condition, flat_input):
                matched_rules.append(rule.rule_id)
                result.decision = rule.effect
                result.rule_id = rule.rule_id
                result.message = rule.message
                break
                
        # Если нет совпадений - deny по умолчанию
        if not matched_rules:
            result.decision = PolicyDecision.DENY
            result.message = "No matching rule found"
            
        result.matched_rules = matched_rules
        result.duration_ms = (time.time() - start_time) * 1000
        
        # Логируем
        self._log_decision(flat_input, result, trace)
        
        return result
        
    def _log_decision(self, input_data: Dict[str, Any], result: EvaluationResult,
                      trace: List[Dict[str, Any]]):
        """Логирование решения"""
        input_hash = hashlib.sha256(json.dumps(input_data, sort_keys=True).encode()).hexdigest()[:16]
        
        log = DecisionLog(
            log_id=f"log_{uuid.uuid4().hex[:8]}",
            input_hash=input_hash,
            input_data=input_data,
            decision=result.decision,
            policy_id=result.policy_id,
            trace=trace
        )
        
        self.decision_logs.append(log)
        
        # Ограничиваем размер лога
        if len(self.decision_logs) > 10000:
            self.decision_logs = self.decision_logs[-5000:]


class PolicyTestRunner:
    """Запуск тестов политик"""
    
    def __init__(self, evaluator: PolicyEvaluator):
        self.evaluator = evaluator
        
    def run_test(self, test: PolicyTest, policy: Policy) -> PolicyTest:
        """Запуск теста"""
        result = self.evaluator.evaluate(policy, test.input_data)
        
        test.actual_decision = result.decision
        test.passed = result.decision == test.expected_decision
        
        return test
        
    def run_tests(self, tests: List[PolicyTest], policies: Dict[str, Policy]) -> Dict[str, Any]:
        """Запуск множества тестов"""
        results = {
            "total": len(tests),
            "passed": 0,
            "failed": 0,
            "tests": []
        }
        
        for test in tests:
            policy = policies.get(test.policy_id)
            if policy:
                self.run_test(test, policy)
                
                if test.passed:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                    
                results["tests"].append({
                    "test_id": test.test_id,
                    "name": test.name,
                    "passed": test.passed,
                    "expected": test.expected_decision.value,
                    "actual": test.actual_decision.value if test.actual_decision else None
                })
                
        return results


class PolicyEnginePlatform:
    """Платформа движка политик"""
    
    def __init__(self):
        self.policies: Dict[str, Policy] = {}
        self.bundles: Dict[str, PolicyBundle] = {}
        
        self.evaluator = PolicyEvaluator()
        self.test_runner = PolicyTestRunner(self.evaluator)
        
        # Кэш
        self.policy_cache: Dict[str, Dict[str, Any]] = {}
        
    def create_policy(self, name: str, package: str = "",
                       rules: List[Dict[str, Any]] = None,
                       **kwargs) -> Policy:
        """Создание политики"""
        policy_rules = []
        
        for r in (rules or []):
            rule = PolicyRule(
                rule_id=f"rule_{uuid.uuid4().hex[:8]}",
                name=r.get("name", ""),
                rule_type=RuleType(r.get("type", "conditional")),
                condition=r.get("condition", ""),
                effect=PolicyDecision(r.get("effect", "allow")),
                priority=r.get("priority", 0),
                message=r.get("message", "")
            )
            policy_rules.append(rule)
            
        policy = Policy(
            policy_id=f"pol_{uuid.uuid4().hex[:8]}",
            name=name,
            package=package,
            rules=policy_rules,
            **kwargs
        )
        
        self.policies[policy.policy_id] = policy
        return policy
        
    def create_bundle(self, name: str, policy_ids: List[str],
                       **kwargs) -> PolicyBundle:
        """Создание пакета политик"""
        bundle = PolicyBundle(
            bundle_id=f"bundle_{uuid.uuid4().hex[:8]}",
            name=name,
            policy_ids=policy_ids,
            revision=uuid.uuid4().hex[:8],
            **kwargs
        )
        
        self.bundles[bundle.bundle_id] = bundle
        return bundle
        
    def evaluate(self, policy_id: str, subject: Dict[str, Any] = None,
                  resource: Dict[str, Any] = None, action: str = "",
                  context: Dict[str, Any] = None) -> EvaluationResult:
        """Оценка политики"""
        policy = self.policies.get(policy_id)
        if not policy:
            return EvaluationResult(
                result_id=f"eval_{uuid.uuid4().hex[:8]}",
                decision=PolicyDecision.DENY,
                message=f"Policy {policy_id} not found"
            )
            
        if policy.status != PolicyStatus.ACTIVE:
            return EvaluationResult(
                result_id=f"eval_{uuid.uuid4().hex[:8]}",
                decision=PolicyDecision.DENY,
                message=f"Policy {policy_id} is not active"
            )
            
        input_data = EvaluationInput(
            subject=subject or {},
            resource=resource or {},
            action=action,
            context=context or {}
        )
        
        return self.evaluator.evaluate(policy, input_data)
        
    def evaluate_bundle(self, bundle_id: str, **kwargs) -> Dict[str, EvaluationResult]:
        """Оценка всех политик в пакете"""
        bundle = self.bundles.get(bundle_id)
        if not bundle:
            return {}
            
        results = {}
        
        for policy_id in bundle.policy_ids:
            results[policy_id] = self.evaluate(policy_id, **kwargs)
            
        return results
        
    def create_test(self, name: str, policy_id: str,
                     subject: Dict[str, Any] = None,
                     resource: Dict[str, Any] = None,
                     action: str = "",
                     expected: str = "allow") -> PolicyTest:
        """Создание теста"""
        return PolicyTest(
            test_id=f"test_{uuid.uuid4().hex[:8]}",
            name=name,
            policy_id=policy_id,
            input_data=EvaluationInput(
                subject=subject or {},
                resource=resource or {},
                action=action
            ),
            expected_decision=PolicyDecision(expected)
        )
        
    def run_tests(self, tests: List[PolicyTest]) -> Dict[str, Any]:
        """Запуск тестов"""
        return self.test_runner.run_tests(tests, self.policies)
        
    def get_decision_logs(self, policy_id: str = None,
                           limit: int = 100) -> List[DecisionLog]:
        """Получение логов решений"""
        logs = self.evaluator.decision_logs
        
        if policy_id:
            logs = [l for l in logs if l.policy_id == policy_id]
            
        return logs[-limit:]
        
    def get_stats(self) -> Dict[str, Any]:
        """Статистика платформы"""
        logs = self.evaluator.decision_logs
        
        allow_count = len([l for l in logs if l.decision == PolicyDecision.ALLOW])
        deny_count = len([l for l in logs if l.decision == PolicyDecision.DENY])
        
        return {
            "policies": len(self.policies),
            "active_policies": len([p for p in self.policies.values() if p.status == PolicyStatus.ACTIVE]),
            "bundles": len(self.bundles),
            "decision_logs": len(logs),
            "decisions": {
                "allow": allow_count,
                "deny": deny_count
            }
        }
        
    # Примеры политик
    def create_rbac_policy(self, name: str, roles: Dict[str, List[str]]) -> Policy:
        """Создание RBAC политики"""
        rules = []
        
        for role, permissions in roles.items():
            for permission in permissions:
                parts = permission.split(":")
                resource_type = parts[0] if len(parts) > 0 else "*"
                action = parts[1] if len(parts) > 1 else "*"
                
                rules.append({
                    "name": f"{role}_{permission}",
                    "type": "conditional",
                    "condition": f'subject.role == "{role}" AND resource.type == "{resource_type}" AND action == "{action}"',
                    "effect": "allow",
                    "priority": 10,
                    "message": f"Allowed by role {role}"
                })
                
        # Default deny
        rules.append({
            "name": "default_deny",
            "type": "default",
            "condition": "",
            "effect": "deny",
            "priority": -100,
            "message": "No matching rule"
        })
        
        return self.create_policy(name, package="rbac", rules=rules)
        
    def create_abac_policy(self, name: str, conditions: List[Dict[str, Any]]) -> Policy:
        """Создание ABAC политики"""
        rules = []
        
        for i, cond in enumerate(conditions):
            rules.append({
                "name": cond.get("name", f"condition_{i}"),
                "type": "conditional",
                "condition": cond.get("condition", ""),
                "effect": cond.get("effect", "allow"),
                "priority": cond.get("priority", 10 - i),
                "message": cond.get("message", "")
            })
            
        return self.create_policy(name, package="abac", rules=rules)


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 71: Policy Engine Platform")
    print("=" * 60)
    
    async def demo():
        platform = PolicyEnginePlatform()
        print("✓ Policy Engine Platform created")
        
        # Создание RBAC политики
        print("\n📋 Creating RBAC Policy...")
        
        rbac_policy = platform.create_rbac_policy(
            name="API Access Control",
            roles={
                "admin": ["user:read", "user:write", "user:delete", "config:read", "config:write"],
                "editor": ["user:read", "user:write", "config:read"],
                "viewer": ["user:read", "config:read"]
            }
        )
        print(f"  ✓ Policy: {rbac_policy.name}")
        print(f"    Rules: {len(rbac_policy.rules)}")
        
        # Создание ABAC политики
        print("\n📋 Creating ABAC Policy...")
        
        abac_policy = platform.create_abac_policy(
            name="Document Access Control",
            conditions=[
                {
                    "name": "owner_access",
                    "condition": 'subject.id == resource.owner_id',
                    "effect": "allow",
                    "priority": 100,
                    "message": "Owner has full access"
                },
                {
                    "name": "department_access",
                    "condition": 'subject.department == resource.department AND action in ["read", "write"]',
                    "effect": "allow",
                    "priority": 50,
                    "message": "Same department access"
                },
                {
                    "name": "public_read",
                    "condition": 'resource.visibility == "public" AND action == "read"',
                    "effect": "allow",
                    "priority": 10,
                    "message": "Public document read"
                },
                {
                    "name": "default_deny",
                    "condition": "",
                    "effect": "deny",
                    "priority": -100,
                    "message": "Access denied"
                }
            ]
        )
        print(f"  ✓ Policy: {abac_policy.name}")
        print(f"    Rules: {len(abac_policy.rules)}")
        
        # Создание кастомной политики
        print("\n📋 Creating Custom Policy...")
        
        custom_policy = platform.create_policy(
            name="API Rate Limiting",
            package="security",
            rules=[
                {
                    "name": "premium_no_limit",
                    "type": "conditional",
                    "condition": 'subject.tier == "premium"',
                    "effect": "allow",
                    "priority": 100,
                    "message": "Premium tier - no rate limit"
                },
                {
                    "name": "standard_limit",
                    "type": "conditional",
                    "condition": 'subject.tier == "standard" AND context.requests_per_minute <= 100',
                    "effect": "allow",
                    "priority": 50,
                    "message": "Within standard rate limit"
                },
                {
                    "name": "free_limit",
                    "type": "conditional",
                    "condition": 'subject.tier == "free" AND context.requests_per_minute <= 10',
                    "effect": "allow",
                    "priority": 25,
                    "message": "Within free rate limit"
                },
                {
                    "name": "rate_exceeded",
                    "type": "default",
                    "condition": "",
                    "effect": "deny",
                    "priority": -100,
                    "message": "Rate limit exceeded"
                }
            ],
            description="Controls API rate limits based on user tier",
            tags=["security", "rate-limiting"]
        )
        print(f"  ✓ Policy: {custom_policy.name}")
        
        # Тестирование политик
        print("\n🧪 Testing RBAC Policy...")
        
        # Админ читает пользователей
        result = platform.evaluate(
            rbac_policy.policy_id,
            subject={"role": "admin", "id": "user1"},
            resource={"type": "user", "id": "user2"},
            action="read"
        )
        print(f"  Admin read user: {result.decision.value} - {result.message}")
        
        # Viewer пытается удалить
        result = platform.evaluate(
            rbac_policy.policy_id,
            subject={"role": "viewer", "id": "user1"},
            resource={"type": "user", "id": "user2"},
            action="delete"
        )
        print(f"  Viewer delete user: {result.decision.value} - {result.message}")
        
        # Editor редактирует
        result = platform.evaluate(
            rbac_policy.policy_id,
            subject={"role": "editor", "id": "user1"},
            resource={"type": "user", "id": "user2"},
            action="write"
        )
        print(f"  Editor write user: {result.decision.value} - {result.message}")
        
        # Тестирование ABAC
        print("\n🧪 Testing ABAC Policy...")
        
        # Владелец документа
        result = platform.evaluate(
            abac_policy.policy_id,
            subject={"id": "user1", "department": "engineering"},
            resource={"owner_id": "user1", "department": "engineering", "visibility": "private"},
            action="delete"
        )
        print(f"  Owner delete doc: {result.decision.value} - {result.message}")
        
        # Коллега из отдела
        result = platform.evaluate(
            abac_policy.policy_id,
            subject={"id": "user2", "department": "engineering"},
            resource={"owner_id": "user1", "department": "engineering", "visibility": "private"},
            action="read"
        )
        print(f"  Colleague read doc: {result.decision.value} - {result.message}")
        
        # Публичный документ
        result = platform.evaluate(
            abac_policy.policy_id,
            subject={"id": "user3", "department": "sales"},
            resource={"owner_id": "user1", "department": "engineering", "visibility": "public"},
            action="read"
        )
        print(f"  Public doc read: {result.decision.value} - {result.message}")
        
        # Rate limiting
        print("\n🧪 Testing Rate Limiting Policy...")
        
        result = platform.evaluate(
            custom_policy.policy_id,
            subject={"tier": "premium", "id": "user1"},
            context={"requests_per_minute": 500}
        )
        print(f"  Premium 500 req/min: {result.decision.value} - {result.message}")
        
        result = platform.evaluate(
            custom_policy.policy_id,
            subject={"tier": "standard", "id": "user2"},
            context={"requests_per_minute": 50}
        )
        print(f"  Standard 50 req/min: {result.decision.value} - {result.message}")
        
        result = platform.evaluate(
            custom_policy.policy_id,
            subject={"tier": "free", "id": "user3"},
            context={"requests_per_minute": 20}
        )
        print(f"  Free 20 req/min: {result.decision.value} - {result.message}")
        
        # Создание и запуск тестов
        print("\n📝 Running Policy Tests...")
        
        tests = [
            platform.create_test(
                name="Admin can read users",
                policy_id=rbac_policy.policy_id,
                subject={"role": "admin"},
                resource={"type": "user"},
                action="read",
                expected="allow"
            ),
            platform.create_test(
                name="Viewer cannot delete",
                policy_id=rbac_policy.policy_id,
                subject={"role": "viewer"},
                resource={"type": "user"},
                action="delete",
                expected="deny"
            ),
            platform.create_test(
                name="Owner has full access",
                policy_id=abac_policy.policy_id,
                subject={"id": "owner1"},
                resource={"owner_id": "owner1"},
                action="delete",
                expected="allow"
            )
        ]
        
        test_results = platform.run_tests(tests)
        print(f"  Total: {test_results['total']}")
        print(f"  Passed: {test_results['passed']}")
        print(f"  Failed: {test_results['failed']}")
        
        for t in test_results["tests"]:
            status = "✓" if t["passed"] else "✗"
            print(f"    {status} {t['name']}: expected={t['expected']}, actual={t['actual']}")
            
        # Создание пакета политик
        print("\n📦 Creating Policy Bundle...")
        
        bundle = platform.create_bundle(
            name="Production Security Bundle",
            policy_ids=[rbac_policy.policy_id, abac_policy.policy_id, custom_policy.policy_id],
            description="Complete security policy bundle for production"
        )
        print(f"  ✓ Bundle: {bundle.name}")
        print(f"    Policies: {len(bundle.policy_ids)}")
        print(f"    Revision: {bundle.revision}")
        
        # Логи решений
        print("\n📊 Decision Logs:")
        logs = platform.get_decision_logs(limit=5)
        print(f"  Recent decisions: {len(logs)}")
        
        for log in logs[-3:]:
            print(f"    - {log.decision.value} | Policy: {log.policy_id[:12]}... | Hash: {log.input_hash}")
            
        # Статистика
        print("\n📊 Platform Statistics:")
        stats = platform.get_stats()
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    {k}: {v}")
            else:
                print(f"  {key}: {value}")
                
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Policy Engine Platform initialized!")
    print("=" * 60)
