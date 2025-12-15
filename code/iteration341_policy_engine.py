#!/usr/bin/env python3
"""
Server Init - Iteration 341: Policy Engine Platform
Платформа движка политик

Функционал:
- Policy Definition - определение политик
- Policy Evaluation - оценка политик
- Rule Engine - движок правил
- Context Attributes - контекстные атрибуты
- Policy Composition - композиция политик
- Decision Caching - кэширование решений
- Audit Trail - аудиторский след
- Policy Versioning - версионирование политик
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
import uuid
import json
import re


class PolicyEffect(Enum):
    """Эффект политики"""
    ALLOW = "allow"
    DENY = "deny"
    DEFER = "defer"


class CombiningAlgorithm(Enum):
    """Алгоритм комбинирования"""
    DENY_OVERRIDES = "deny_overrides"
    ALLOW_OVERRIDES = "allow_overrides"
    FIRST_APPLICABLE = "first_applicable"
    ONLY_ONE_APPLICABLE = "only_one_applicable"
    HIGHEST_PRIORITY = "highest_priority"


class RuleType(Enum):
    """Тип правила"""
    CONDITION = "condition"
    TEMPORAL = "temporal"
    OBLIGATION = "obligation"
    ADVICE = "advice"


class AttributeType(Enum):
    """Тип атрибута"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DATETIME = "datetime"
    IP_ADDRESS = "ip_address"
    REGEX = "regex"


class Operator(Enum):
    """Оператор сравнения"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_OR_EQUAL = "greater_or_equal"
    LESS_OR_EQUAL = "less_or_equal"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IN = "in"
    NOT_IN = "not_in"
    MATCHES = "matches"
    IS_BETWEEN = "is_between"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"


class DecisionResult(Enum):
    """Результат решения"""
    PERMIT = "permit"
    DENY = "deny"
    NOT_APPLICABLE = "not_applicable"
    INDETERMINATE = "indeterminate"


class PolicyStatus(Enum):
    """Статус политики"""
    DRAFT = "draft"
    ACTIVE = "active"
    DISABLED = "disabled"
    ARCHIVED = "archived"


@dataclass
class AttributeDefinition:
    """Определение атрибута"""
    attribute_id: str
    name: str
    
    # Type
    attribute_type: AttributeType = AttributeType.STRING
    
    # Category
    category: str = "subject"  # subject, resource, action, environment
    
    # Default
    default_value: Any = None
    
    # Validation
    required: bool = False
    allowed_values: List[Any] = field(default_factory=list)
    
    # Description
    description: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Condition:
    """Условие"""
    condition_id: str
    
    # Attribute
    attribute_id: str = ""
    attribute_name: str = ""
    
    # Operator
    operator: Operator = Operator.EQUALS
    
    # Value
    value: Any = None
    values: List[Any] = field(default_factory=list)  # For IN, NOT_IN
    
    # Negation
    negate: bool = False
    
    # Description
    description: str = ""


@dataclass
class Rule:
    """Правило"""
    rule_id: str
    name: str
    
    # Type
    rule_type: RuleType = RuleType.CONDITION
    
    # Conditions (AND logic)
    conditions: List[Condition] = field(default_factory=list)
    
    # Effect
    effect: PolicyEffect = PolicyEffect.ALLOW
    
    # Priority
    priority: int = 0
    
    # Temporal constraints
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    
    # Time-based
    allowed_hours: List[int] = field(default_factory=list)  # 0-23
    allowed_days: List[int] = field(default_factory=list)  # 0-6
    
    # Obligation
    obligations: List[str] = field(default_factory=list)
    
    # Description
    description: str = ""
    
    # Status
    is_enabled: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Policy:
    """Политика"""
    policy_id: str
    name: str
    
    # Version
    version: int = 1
    
    # Target (conditions for applicability)
    target_conditions: List[Condition] = field(default_factory=list)
    
    # Rules
    rule_ids: List[str] = field(default_factory=list)
    
    # Combining algorithm
    combining_algorithm: CombiningAlgorithm = CombiningAlgorithm.DENY_OVERRIDES
    
    # Priority
    priority: int = 0
    
    # Status
    status: PolicyStatus = PolicyStatus.DRAFT
    
    # Description
    description: str = ""
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # History
    created_by: str = ""
    updated_by: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


@dataclass
class PolicySet:
    """Набор политик"""
    set_id: str
    name: str
    
    # Policies
    policy_ids: List[str] = field(default_factory=list)
    
    # Combining algorithm
    combining_algorithm: CombiningAlgorithm = CombiningAlgorithm.DENY_OVERRIDES
    
    # Target
    target_conditions: List[Condition] = field(default_factory=list)
    
    # Status
    is_enabled: bool = True
    
    # Description
    description: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class EvaluationContext:
    """Контекст оценки"""
    context_id: str
    
    # Attributes
    subject_attributes: Dict[str, Any] = field(default_factory=dict)
    resource_attributes: Dict[str, Any] = field(default_factory=dict)
    action_attributes: Dict[str, Any] = field(default_factory=dict)
    environment_attributes: Dict[str, Any] = field(default_factory=dict)
    
    # Request info
    request_time: datetime = field(default_factory=datetime.now)
    
    # Custom attributes
    custom_attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationResult:
    """Результат оценки"""
    result_id: str
    
    # Decision
    decision: DecisionResult = DecisionResult.NOT_APPLICABLE
    
    # Policy info
    policy_id: str = ""
    rule_id: str = ""
    
    # Obligations
    obligations: List[str] = field(default_factory=list)
    
    # Advice
    advice: List[str] = field(default_factory=list)
    
    # Evaluation details
    evaluated_policies: int = 0
    evaluated_rules: int = 0
    
    # Timing
    evaluation_time_ms: float = 0.0
    
    # Reason
    reason: str = ""
    
    # Timestamps
    evaluated_at: datetime = field(default_factory=datetime.now)


@dataclass
class CacheEntry:
    """Запись кэша"""
    cache_key: str
    
    # Result
    decision: DecisionResult = DecisionResult.NOT_APPLICABLE
    policy_id: str = ""
    
    # TTL
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(minutes=5))
    
    # Stats
    hit_count: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AuditRecord:
    """Запись аудита"""
    record_id: str
    
    # Request
    context_id: str = ""
    
    # Subject
    subject_id: str = ""
    subject_type: str = ""
    
    # Resource
    resource_id: str = ""
    resource_type: str = ""
    
    # Action
    action: str = ""
    
    # Decision
    decision: DecisionResult = DecisionResult.NOT_APPLICABLE
    
    # Evaluation
    policy_id: str = ""
    rule_id: str = ""
    
    # Reason
    reason: str = ""
    
    # Context
    context_snapshot: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PolicyVersion:
    """Версия политики"""
    version_id: str
    
    # Policy
    policy_id: str = ""
    version_number: int = 1
    
    # Snapshot
    policy_snapshot: Dict[str, Any] = field(default_factory=dict)
    
    # Change info
    changed_by: str = ""
    change_reason: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


class PolicyEngine:
    """Движок политик"""
    
    def __init__(self):
        self.attributes: Dict[str, AttributeDefinition] = {}
        self.rules: Dict[str, Rule] = {}
        self.policies: Dict[str, Policy] = {}
        self.policy_sets: Dict[str, PolicySet] = {}
        self.cache: Dict[str, CacheEntry] = {}
        self.audit_records: List[AuditRecord] = []
        self.versions: Dict[str, List[PolicyVersion]] = {}
        
        # Stats
        self.total_evaluations = 0
        self.cache_hits = 0
        self.cache_misses = 0
        
    async def define_attribute(self, name: str,
                              attribute_type: AttributeType,
                              category: str = "subject",
                              default_value: Any = None,
                              required: bool = False,
                              allowed_values: List[Any] = None,
                              description: str = "") -> AttributeDefinition:
        """Определение атрибута"""
        attr = AttributeDefinition(
            attribute_id=f"attr_{uuid.uuid4().hex[:8]}",
            name=name,
            attribute_type=attribute_type,
            category=category,
            default_value=default_value,
            required=required,
            allowed_values=allowed_values or [],
            description=description
        )
        
        self.attributes[attr.attribute_id] = attr
        return attr
        
    async def create_rule(self, name: str,
                         conditions: List[Dict[str, Any]],
                         effect: PolicyEffect = PolicyEffect.ALLOW,
                         rule_type: RuleType = RuleType.CONDITION,
                         priority: int = 0,
                         valid_from: datetime = None,
                         valid_until: datetime = None,
                         allowed_hours: List[int] = None,
                         allowed_days: List[int] = None,
                         obligations: List[str] = None,
                         description: str = "") -> Rule:
        """Создание правила"""
        rule_conditions = []
        
        for cond_data in conditions:
            condition = Condition(
                condition_id=f"cond_{uuid.uuid4().hex[:8]}",
                attribute_id=cond_data.get("attribute_id", ""),
                attribute_name=cond_data.get("attribute_name", ""),
                operator=Operator(cond_data.get("operator", "equals")),
                value=cond_data.get("value"),
                values=cond_data.get("values", []),
                negate=cond_data.get("negate", False),
                description=cond_data.get("description", "")
            )
            rule_conditions.append(condition)
            
        rule = Rule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name=name,
            rule_type=rule_type,
            conditions=rule_conditions,
            effect=effect,
            priority=priority,
            valid_from=valid_from,
            valid_until=valid_until,
            allowed_hours=allowed_hours or [],
            allowed_days=allowed_days or [],
            obligations=obligations or [],
            description=description
        )
        
        self.rules[rule.rule_id] = rule
        return rule
        
    async def create_policy(self, name: str,
                           rule_ids: List[str],
                           target_conditions: List[Dict[str, Any]] = None,
                           combining_algorithm: CombiningAlgorithm = CombiningAlgorithm.DENY_OVERRIDES,
                           priority: int = 0,
                           created_by: str = "",
                           description: str = "",
                           labels: Dict[str, str] = None) -> Policy:
        """Создание политики"""
        target_conds = []
        
        for cond_data in (target_conditions or []):
            condition = Condition(
                condition_id=f"cond_{uuid.uuid4().hex[:8]}",
                attribute_id=cond_data.get("attribute_id", ""),
                attribute_name=cond_data.get("attribute_name", ""),
                operator=Operator(cond_data.get("operator", "equals")),
                value=cond_data.get("value"),
                values=cond_data.get("values", [])
            )
            target_conds.append(condition)
            
        policy = Policy(
            policy_id=f"pol_{uuid.uuid4().hex[:8]}",
            name=name,
            rule_ids=rule_ids,
            target_conditions=target_conds,
            combining_algorithm=combining_algorithm,
            priority=priority,
            created_by=created_by,
            description=description,
            labels=labels or {}
        )
        
        self.policies[policy.policy_id] = policy
        
        # Save version
        await self._save_version(policy, created_by, "Initial creation")
        
        return policy
        
    async def create_policy_set(self, name: str,
                               policy_ids: List[str],
                               combining_algorithm: CombiningAlgorithm = CombiningAlgorithm.DENY_OVERRIDES,
                               description: str = "") -> PolicySet:
        """Создание набора политик"""
        policy_set = PolicySet(
            set_id=f"pset_{uuid.uuid4().hex[:8]}",
            name=name,
            policy_ids=policy_ids,
            combining_algorithm=combining_algorithm,
            description=description
        )
        
        self.policy_sets[policy_set.set_id] = policy_set
        return policy_set
        
    async def activate_policy(self, policy_id: str,
                             activated_by: str) -> bool:
        """Активация политики"""
        policy = self.policies.get(policy_id)
        if not policy:
            return False
            
        policy.status = PolicyStatus.ACTIVE
        policy.updated_by = activated_by
        policy.updated_at = datetime.now()
        
        # Clear cache for this policy
        await self._invalidate_cache()
        
        return True
        
    async def disable_policy(self, policy_id: str,
                            disabled_by: str) -> bool:
        """Деактивация политики"""
        policy = self.policies.get(policy_id)
        if not policy:
            return False
            
        policy.status = PolicyStatus.DISABLED
        policy.updated_by = disabled_by
        policy.updated_at = datetime.now()
        
        # Clear cache
        await self._invalidate_cache()
        
        return True
        
    async def evaluate(self, context: EvaluationContext,
                      use_cache: bool = True) -> EvaluationResult:
        """Оценка запроса"""
        start_time = datetime.now()
        self.total_evaluations += 1
        
        result = EvaluationResult(
            result_id=f"res_{uuid.uuid4().hex[:12]}"
        )
        
        # Check cache
        if use_cache:
            cache_key = self._generate_cache_key(context)
            cached = self.cache.get(cache_key)
            
            if cached and cached.expires_at > datetime.now():
                self.cache_hits += 1
                cached.hit_count += 1
                
                result.decision = cached.decision
                result.policy_id = cached.policy_id
                result.reason = "Cached decision"
                result.evaluation_time_ms = (datetime.now() - start_time).total_seconds() * 1000
                
                return result
            else:
                self.cache_misses += 1
                
        # Get applicable policies
        applicable_policies = await self._get_applicable_policies(context)
        result.evaluated_policies = len(applicable_policies)
        
        if not applicable_policies:
            result.decision = DecisionResult.NOT_APPLICABLE
            result.reason = "No applicable policies"
        else:
            # Sort by priority
            applicable_policies.sort(key=lambda p: p.priority, reverse=True)
            
            # Evaluate policies
            decisions = []
            
            for policy in applicable_policies:
                policy_result = await self._evaluate_policy(policy, context)
                decisions.append((policy, policy_result))
                result.evaluated_rules += 1
                
            # Combine decisions
            final_decision = await self._combine_decisions(decisions, CombiningAlgorithm.DENY_OVERRIDES)
            result.decision = final_decision[0]
            result.policy_id = final_decision[1].policy_id if final_decision[1] else ""
            result.rule_id = final_decision[2]
            
            if result.decision == DecisionResult.PERMIT:
                result.reason = f"Permitted by policy: {final_decision[1].name if final_decision[1] else 'N/A'}"
            elif result.decision == DecisionResult.DENY:
                result.reason = f"Denied by policy: {final_decision[1].name if final_decision[1] else 'N/A'}"
                
        # Calculate time
        result.evaluation_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        # Cache result
        if use_cache:
            cache_key = self._generate_cache_key(context)
            self.cache[cache_key] = CacheEntry(
                cache_key=cache_key,
                decision=result.decision,
                policy_id=result.policy_id
            )
            
        # Audit
        await self._record_audit(context, result)
        
        return result
        
    async def _get_applicable_policies(self, context: EvaluationContext) -> List[Policy]:
        """Получение применимых политик"""
        applicable = []
        
        for policy in self.policies.values():
            if policy.status != PolicyStatus.ACTIVE:
                continue
                
            # Check target conditions
            if policy.target_conditions:
                if await self._evaluate_conditions(policy.target_conditions, context):
                    applicable.append(policy)
            else:
                applicable.append(policy)
                
        return applicable
        
    async def _evaluate_policy(self, policy: Policy, 
                              context: EvaluationContext) -> DecisionResult:
        """Оценка политики"""
        rule_results = []
        
        for rule_id in policy.rule_ids:
            rule = self.rules.get(rule_id)
            if not rule or not rule.is_enabled:
                continue
                
            # Check temporal constraints
            if not await self._check_temporal_constraints(rule, context):
                continue
                
            # Evaluate conditions
            if await self._evaluate_conditions(rule.conditions, context):
                rule_results.append((rule, rule.effect))
                
        # Combine rule results
        if not rule_results:
            return DecisionResult.NOT_APPLICABLE
            
        return await self._combine_rule_results(rule_results, policy.combining_algorithm)
        
    async def _evaluate_conditions(self, conditions: List[Condition],
                                  context: EvaluationContext) -> bool:
        """Оценка условий (AND логика)"""
        for condition in conditions:
            if not await self._evaluate_condition(condition, context):
                return False
        return True
        
    async def _evaluate_condition(self, condition: Condition,
                                 context: EvaluationContext) -> bool:
        """Оценка отдельного условия"""
        # Get attribute value from context
        attr_value = await self._get_attribute_value(condition.attribute_name, context)
        
        result = False
        
        if condition.operator == Operator.EQUALS:
            result = attr_value == condition.value
        elif condition.operator == Operator.NOT_EQUALS:
            result = attr_value != condition.value
        elif condition.operator == Operator.GREATER_THAN:
            result = attr_value is not None and attr_value > condition.value
        elif condition.operator == Operator.LESS_THAN:
            result = attr_value is not None and attr_value < condition.value
        elif condition.operator == Operator.GREATER_OR_EQUAL:
            result = attr_value is not None and attr_value >= condition.value
        elif condition.operator == Operator.LESS_OR_EQUAL:
            result = attr_value is not None and attr_value <= condition.value
        elif condition.operator == Operator.CONTAINS:
            result = condition.value in str(attr_value) if attr_value else False
        elif condition.operator == Operator.NOT_CONTAINS:
            result = condition.value not in str(attr_value) if attr_value else True
        elif condition.operator == Operator.STARTS_WITH:
            result = str(attr_value).startswith(condition.value) if attr_value else False
        elif condition.operator == Operator.ENDS_WITH:
            result = str(attr_value).endswith(condition.value) if attr_value else False
        elif condition.operator == Operator.IN:
            result = attr_value in condition.values
        elif condition.operator == Operator.NOT_IN:
            result = attr_value not in condition.values
        elif condition.operator == Operator.MATCHES:
            result = bool(re.match(condition.value, str(attr_value))) if attr_value else False
        elif condition.operator == Operator.IS_NULL:
            result = attr_value is None
        elif condition.operator == Operator.IS_NOT_NULL:
            result = attr_value is not None
        elif condition.operator == Operator.IS_BETWEEN:
            if isinstance(condition.values, list) and len(condition.values) == 2:
                result = condition.values[0] <= attr_value <= condition.values[1]
                
        # Apply negation
        if condition.negate:
            result = not result
            
        return result
        
    async def _get_attribute_value(self, attribute_name: str,
                                  context: EvaluationContext) -> Any:
        """Получение значения атрибута из контекста"""
        # Parse attribute name (format: category.name)
        parts = attribute_name.split(".", 1)
        
        if len(parts) == 2:
            category, name = parts
        else:
            category, name = "subject", parts[0]
            
        # Get from appropriate category
        if category == "subject":
            return context.subject_attributes.get(name)
        elif category == "resource":
            return context.resource_attributes.get(name)
        elif category == "action":
            return context.action_attributes.get(name)
        elif category == "environment":
            return context.environment_attributes.get(name)
        else:
            return context.custom_attributes.get(attribute_name)
            
    async def _check_temporal_constraints(self, rule: Rule,
                                         context: EvaluationContext) -> bool:
        """Проверка временных ограничений"""
        now = context.request_time
        
        # Check validity period
        if rule.valid_from and now < rule.valid_from:
            return False
        if rule.valid_until and now > rule.valid_until:
            return False
            
        # Check allowed hours
        if rule.allowed_hours and now.hour not in rule.allowed_hours:
            return False
            
        # Check allowed days
        if rule.allowed_days and now.weekday() not in rule.allowed_days:
            return False
            
        return True
        
    async def _combine_rule_results(self, results: List[tuple],
                                   algorithm: CombiningAlgorithm) -> DecisionResult:
        """Комбинирование результатов правил"""
        if algorithm == CombiningAlgorithm.DENY_OVERRIDES:
            # Any deny = deny
            for rule, effect in results:
                if effect == PolicyEffect.DENY:
                    return DecisionResult.DENY
            return DecisionResult.PERMIT
            
        elif algorithm == CombiningAlgorithm.ALLOW_OVERRIDES:
            # Any allow = permit
            for rule, effect in results:
                if effect == PolicyEffect.ALLOW:
                    return DecisionResult.PERMIT
            return DecisionResult.DENY
            
        elif algorithm == CombiningAlgorithm.FIRST_APPLICABLE:
            # First matched result
            if results:
                effect = results[0][1]
                return DecisionResult.PERMIT if effect == PolicyEffect.ALLOW else DecisionResult.DENY
            return DecisionResult.NOT_APPLICABLE
            
        elif algorithm == CombiningAlgorithm.HIGHEST_PRIORITY:
            # Highest priority rule wins
            if results:
                results.sort(key=lambda x: x[0].priority, reverse=True)
                effect = results[0][1]
                return DecisionResult.PERMIT if effect == PolicyEffect.ALLOW else DecisionResult.DENY
            return DecisionResult.NOT_APPLICABLE
            
        return DecisionResult.NOT_APPLICABLE
        
    async def _combine_decisions(self, decisions: List[tuple],
                                algorithm: CombiningAlgorithm) -> tuple:
        """Комбинирование решений политик"""
        if not decisions:
            return (DecisionResult.NOT_APPLICABLE, None, "")
            
        if algorithm == CombiningAlgorithm.DENY_OVERRIDES:
            for policy, result in decisions:
                if result == DecisionResult.DENY:
                    return (DecisionResult.DENY, policy, "")
            for policy, result in decisions:
                if result == DecisionResult.PERMIT:
                    return (DecisionResult.PERMIT, policy, "")
                    
        elif algorithm == CombiningAlgorithm.ALLOW_OVERRIDES:
            for policy, result in decisions:
                if result == DecisionResult.PERMIT:
                    return (DecisionResult.PERMIT, policy, "")
            for policy, result in decisions:
                if result == DecisionResult.DENY:
                    return (DecisionResult.DENY, policy, "")
                    
        elif algorithm == CombiningAlgorithm.FIRST_APPLICABLE:
            if decisions:
                return (decisions[0][1], decisions[0][0], "")
                
        elif algorithm == CombiningAlgorithm.HIGHEST_PRIORITY:
            decisions.sort(key=lambda x: x[0].priority, reverse=True)
            if decisions:
                return (decisions[0][1], decisions[0][0], "")
                
        return (DecisionResult.NOT_APPLICABLE, None, "")
        
    def _generate_cache_key(self, context: EvaluationContext) -> str:
        """Генерация ключа кэша"""
        key_parts = [
            json.dumps(context.subject_attributes, sort_keys=True),
            json.dumps(context.resource_attributes, sort_keys=True),
            json.dumps(context.action_attributes, sort_keys=True)
        ]
        return str(hash("|".join(key_parts)))
        
    async def _invalidate_cache(self):
        """Инвалидация кэша"""
        self.cache.clear()
        
    async def _save_version(self, policy: Policy,
                           changed_by: str,
                           change_reason: str):
        """Сохранение версии политики"""
        version = PolicyVersion(
            version_id=f"ver_{uuid.uuid4().hex[:8]}",
            policy_id=policy.policy_id,
            version_number=policy.version,
            policy_snapshot={
                "name": policy.name,
                "rule_ids": policy.rule_ids,
                "combining_algorithm": policy.combining_algorithm.value,
                "priority": policy.priority
            },
            changed_by=changed_by,
            change_reason=change_reason
        )
        
        if policy.policy_id not in self.versions:
            self.versions[policy.policy_id] = []
        self.versions[policy.policy_id].append(version)
        
    async def _record_audit(self, context: EvaluationContext,
                           result: EvaluationResult):
        """Запись аудита"""
        record = AuditRecord(
            record_id=f"aud_{uuid.uuid4().hex[:12]}",
            context_id=context.context_id,
            subject_id=context.subject_attributes.get("id", ""),
            subject_type=context.subject_attributes.get("type", ""),
            resource_id=context.resource_attributes.get("id", ""),
            resource_type=context.resource_attributes.get("type", ""),
            action=context.action_attributes.get("action", ""),
            decision=result.decision,
            policy_id=result.policy_id,
            rule_id=result.rule_id,
            reason=result.reason,
            context_snapshot={
                "subject": context.subject_attributes,
                "resource": context.resource_attributes,
                "action": context.action_attributes
            }
        )
        
        self.audit_records.append(record)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_attributes = len(self.attributes)
        total_rules = len(self.rules)
        enabled_rules = sum(1 for r in self.rules.values() if r.is_enabled)
        
        total_policies = len(self.policies)
        active_policies = sum(1 for p in self.policies.values() if p.status == PolicyStatus.ACTIVE)
        
        total_policy_sets = len(self.policy_sets)
        
        cache_size = len(self.cache)
        cache_hit_rate = (self.cache_hits / (self.cache_hits + self.cache_misses) * 100) if (self.cache_hits + self.cache_misses) > 0 else 0
        
        # By combining algorithm
        by_algorithm = {}
        for policy in self.policies.values():
            alg = policy.combining_algorithm.value
            by_algorithm[alg] = by_algorithm.get(alg, 0) + 1
            
        # Audit stats
        total_audits = len(self.audit_records)
        permitted = sum(1 for a in self.audit_records if a.decision == DecisionResult.PERMIT)
        denied = sum(1 for a in self.audit_records if a.decision == DecisionResult.DENY)
        
        return {
            "total_attributes": total_attributes,
            "total_rules": total_rules,
            "enabled_rules": enabled_rules,
            "total_policies": total_policies,
            "active_policies": active_policies,
            "total_policy_sets": total_policy_sets,
            "total_evaluations": self.total_evaluations,
            "cache_size": cache_size,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": cache_hit_rate,
            "policies_by_algorithm": by_algorithm,
            "total_audit_records": total_audits,
            "permitted_decisions": permitted,
            "denied_decisions": denied
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 341: Policy Engine Platform")
    print("=" * 60)
    
    engine = PolicyEngine()
    print("✓ Policy Engine initialized")
    
    # Define Attributes
    print("\n📋 Defining Attributes...")
    
    attributes_data = [
        ("user_id", AttributeType.STRING, "subject", None, True, "User identifier"),
        ("user_role", AttributeType.STRING, "subject", None, True, "User role"),
        ("user_department", AttributeType.STRING, "subject", None, False, "User department"),
        ("user_level", AttributeType.INTEGER, "subject", 0, False, "User security level"),
        ("resource_id", AttributeType.STRING, "resource", None, True, "Resource identifier"),
        ("resource_type", AttributeType.STRING, "resource", None, True, "Resource type"),
        ("resource_classification", AttributeType.STRING, "resource", "internal", False, "Resource classification"),
        ("resource_owner", AttributeType.STRING, "resource", None, False, "Resource owner"),
        ("action", AttributeType.STRING, "action", None, True, "Action type"),
        ("source_ip", AttributeType.IP_ADDRESS, "environment", None, False, "Source IP address"),
        ("request_time", AttributeType.DATETIME, "environment", None, False, "Request timestamp")
    ]
    
    attributes = []
    for name, atype, category, default, required, desc in attributes_data:
        attr = await engine.define_attribute(name, atype, category, default, required, description=desc)
        attributes.append(attr)
        print(f"  📋 {name} ({atype.value})")
        
    # Create Rules
    print("\n📏 Creating Rules...")
    
    rules_data = [
        # Admin access
        ("Admin Full Access", [{"attribute_name": "subject.user_role", "operator": "equals", "value": "admin"}], PolicyEffect.ALLOW, 100, "Allow admins full access"),
        # Department access
        ("Department Access", [
            {"attribute_name": "subject.user_department", "operator": "equals", "value": "finance"},
            {"attribute_name": "resource.resource_type", "operator": "equals", "value": "financial_report"}
        ], PolicyEffect.ALLOW, 50, "Finance department can access financial reports"),
        # Classification rules
        ("Confidential Deny", [{"attribute_name": "resource.resource_classification", "operator": "equals", "value": "confidential"}], PolicyEffect.DENY, 80, "Deny access to confidential resources by default"),
        ("Public Allow", [{"attribute_name": "resource.resource_classification", "operator": "equals", "value": "public"}], PolicyEffect.ALLOW, 10, "Allow access to public resources"),
        # Level-based
        ("High Security Level", [
            {"attribute_name": "subject.user_level", "operator": "greater_or_equal", "value": 3},
            {"attribute_name": "resource.resource_classification", "operator": "equals", "value": "secret"}
        ], PolicyEffect.ALLOW, 70, "Allow high security level users to access secret"),
        # Read-only
        ("Read Only Access", [{"attribute_name": "action.action", "operator": "equals", "value": "read"}], PolicyEffect.ALLOW, 20, "Allow read-only access by default"),
        # Write restriction
        ("Write Restriction", [
            {"attribute_name": "action.action", "operator": "in", "values": ["write", "delete", "update"]},
            {"attribute_name": "subject.user_role", "operator": "not_in", "values": ["admin", "editor"]}
        ], PolicyEffect.DENY, 90, "Restrict write operations for non-editors"),
        # IP restriction
        ("Internal Network Only", [{"attribute_name": "environment.source_ip", "operator": "starts_with", "value": "10."}], PolicyEffect.ALLOW, 30, "Allow only internal network"),
        # Owner access
        ("Owner Access", [{"attribute_name": "resource.resource_owner", "operator": "equals", "value": "{{subject.user_id}}"}], PolicyEffect.ALLOW, 60, "Owners have access to their resources"),
        # Default deny
        ("Default Deny", [], PolicyEffect.DENY, 0, "Default deny rule")
    ]
    
    rules = []
    for name, conditions, effect, priority, desc in rules_data:
        rule = await engine.create_rule(name, conditions, effect, priority=priority, description=desc)
        rules.append(rule)
        print(f"  📏 {name} ({effect.value})")
        
    # Create time-based rule
    business_hours_rule = await engine.create_rule(
        "Business Hours Only",
        [{"attribute_name": "action.action", "operator": "equals", "value": "admin_action"}],
        PolicyEffect.ALLOW,
        allowed_hours=list(range(9, 18)),  # 9 AM - 6 PM
        allowed_days=[0, 1, 2, 3, 4],  # Mon-Fri
        priority=40,
        description="Admin actions only during business hours"
    )
    rules.append(business_hours_rule)
    print(f"  📏 Business Hours Only (temporal)")
    
    # Create Policies
    print("\n📜 Creating Policies...")
    
    policies_data = [
        ("Admin Policy", [rules[0].rule_id], [{"attribute_name": "subject.user_role", "operator": "equals", "value": "admin"}], CombiningAlgorithm.DENY_OVERRIDES, 100),
        ("Document Access Policy", [rules[1].rule_id, rules[2].rule_id, rules[3].rule_id], [{"attribute_name": "resource.resource_type", "operator": "contains", "value": "document"}], CombiningAlgorithm.DENY_OVERRIDES, 50),
        ("Security Classification Policy", [rules[4].rule_id, rules[2].rule_id, rules[3].rule_id], [], CombiningAlgorithm.DENY_OVERRIDES, 80),
        ("CRUD Policy", [rules[5].rule_id, rules[6].rule_id], [], CombiningAlgorithm.DENY_OVERRIDES, 40),
        ("Network Policy", [rules[7].rule_id], [], CombiningAlgorithm.FIRST_APPLICABLE, 30),
        ("Owner Policy", [rules[8].rule_id], [], CombiningAlgorithm.ALLOW_OVERRIDES, 60),
        ("Default Policy", [rules[9].rule_id], [], CombiningAlgorithm.DENY_OVERRIDES, 0)
    ]
    
    policies = []
    for name, rule_ids, target_conditions, algorithm, priority in policies_data:
        policy = await engine.create_policy(
            name, rule_ids, target_conditions, algorithm, priority, "admin", f"Policy: {name}"
        )
        policies.append(policy)
        await engine.activate_policy(policy.policy_id, "admin")
        print(f"  📜 {name}")
        
    # Create Policy Set
    print("\n📚 Creating Policy Sets...")
    
    policy_set = await engine.create_policy_set(
        "Default Policy Set",
        [p.policy_id for p in policies],
        CombiningAlgorithm.DENY_OVERRIDES,
        "Default policy set for all resources"
    )
    print(f"  📚 {policy_set.name}")
    
    # Evaluate Requests
    print("\n🔍 Evaluating Access Requests...")
    
    requests_data = [
        # Admin request
        ({"id": "user-001", "role": "admin", "department": "IT", "level": 5},
         {"id": "doc-001", "type": "document", "classification": "secret", "owner": "user-002"},
         {"action": "read"},
         {"source_ip": "10.0.1.100"}),
        # Finance accessing financial report
        ({"id": "user-002", "role": "analyst", "department": "finance", "level": 2},
         {"id": "report-001", "type": "financial_report", "classification": "internal", "owner": "finance"},
         {"action": "read"},
         {"source_ip": "10.0.2.50"}),
        # Regular user accessing public
        ({"id": "user-003", "role": "user", "department": "marketing", "level": 1},
         {"id": "doc-002", "type": "document", "classification": "public", "owner": "marketing"},
         {"action": "read"},
         {"source_ip": "10.0.3.25"}),
        # User trying to write
        ({"id": "user-004", "role": "user", "department": "sales", "level": 1},
         {"id": "doc-003", "type": "document", "classification": "internal", "owner": "sales"},
         {"action": "write"},
         {"source_ip": "10.0.4.10"}),
        # Editor writing
        ({"id": "user-005", "role": "editor", "department": "content", "level": 2},
         {"id": "doc-004", "type": "document", "classification": "internal", "owner": "content"},
         {"action": "write"},
         {"source_ip": "10.0.5.15"}),
        # Accessing confidential
        ({"id": "user-006", "role": "user", "department": "HR", "level": 2},
         {"id": "doc-005", "type": "document", "classification": "confidential", "owner": "HR"},
         {"action": "read"},
         {"source_ip": "10.0.6.20"}),
        # High level accessing secret
        ({"id": "user-007", "role": "manager", "department": "security", "level": 4},
         {"id": "doc-006", "type": "document", "classification": "secret", "owner": "security"},
         {"action": "read"},
         {"source_ip": "10.0.7.30"}),
        # Owner accessing own resource
        ({"id": "user-008", "role": "user", "department": "engineering", "level": 2},
         {"id": "doc-007", "type": "document", "classification": "internal", "owner": "user-008"},
         {"action": "read"},
         {"source_ip": "10.0.8.40"}),
        # External IP (simulated)
        ({"id": "user-009", "role": "contractor", "department": "external", "level": 1},
         {"id": "doc-008", "type": "document", "classification": "public", "owner": "external"},
         {"action": "read"},
         {"source_ip": "203.0.113.50"}),
        # Delete attempt
        ({"id": "user-010", "role": "user", "department": "support", "level": 1},
         {"id": "doc-009", "type": "document", "classification": "internal", "owner": "support"},
         {"action": "delete"},
         {"source_ip": "10.0.9.55"})
    ]
    
    results = []
    for subject, resource, action, env in requests_data:
        context = EvaluationContext(
            context_id=f"ctx_{uuid.uuid4().hex[:8]}",
            subject_attributes={"id": subject["id"], "type": "user", **{f"user_{k}": v for k, v in subject.items()}},
            resource_attributes={"id": resource["id"], "type": resource["type"], **{f"resource_{k}": v for k, v in resource.items()}},
            action_attributes=action,
            environment_attributes=env
        )
        
        result = await engine.evaluate(context)
        results.append((subject, resource, action, result))
        
        icon = "✓" if result.decision == DecisionResult.PERMIT else "✗"
        print(f"  {icon} {subject['id']} → {resource['id']} ({action['action']}): {result.decision.value}")
        
    # Re-evaluate some requests (to test cache)
    print("\n🔄 Testing Cache (re-evaluating)...")
    
    for subject, resource, action, env in requests_data[:3]:
        context = EvaluationContext(
            context_id=f"ctx_{uuid.uuid4().hex[:8]}",
            subject_attributes={"id": subject["id"], "type": "user", **{f"user_{k}": v for k, v in subject.items()}},
            resource_attributes={"id": resource["id"], "type": resource["type"], **{f"resource_{k}": v for k, v in resource.items()}},
            action_attributes=action,
            environment_attributes=env
        )
        
        result = await engine.evaluate(context, use_cache=True)
        cached_indicator = "(cached)" if "Cached" in result.reason else ""
        print(f"  ↻ {subject['id']} → {resource['id']}: {result.decision.value} {cached_indicator}")
        
    # Attributes
    print("\n📋 Attribute Definitions:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                      │ Type          │ Category       │ Required │ Description                                                                  │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for attr in attributes:
        name = attr.name[:25].ljust(25)
        atype = attr.attribute_type.value[:13].ljust(13)
        category = attr.category[:14].ljust(14)
        required = "Yes" if attr.required else "No"
        required = required[:8].ljust(8)
        desc = attr.description[:78].ljust(78)
        
        print(f"  │ {name} │ {atype} │ {category} │ {required} │ {desc} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Rules
    print("\n📏 Policy Rules:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                         │ Conditions │ Effect │ Priority │ Type        │ Status                                                          │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for rule in rules:
        name = rule.name[:28].ljust(28)
        cond_count = str(len(rule.conditions)).ljust(10)
        
        effect_icon = "✓" if rule.effect == PolicyEffect.ALLOW else "✗"
        effect = f"{effect_icon} {rule.effect.value}"[:6].ljust(6)
        
        priority = str(rule.priority).ljust(8)
        rtype = rule.rule_type.value[:11].ljust(11)
        status = "✓ Enabled" if rule.is_enabled else "○ Disabled"
        status = status[:65].ljust(65)
        
        print(f"  │ {name} │ {cond_count} │ {effect} │ {priority} │ {rtype} │ {status} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Policies
    print("\n📜 Policies:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                         │ Rules │ Algorithm            │ Priority │ Version │ Status                                                                                                       │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for policy in policies:
        name = policy.name[:28].ljust(28)
        rule_count = str(len(policy.rule_ids)).ljust(5)
        algorithm = policy.combining_algorithm.value[:20].ljust(20)
        priority = str(policy.priority).ljust(8)
        version = f"v{policy.version}".ljust(7)
        
        status_icon = {"active": "🟢", "draft": "🟡", "disabled": "⚫", "archived": "📦"}.get(policy.status.value, "⚪")
        status = f"{status_icon} {policy.status.value}"[:110].ljust(110)
        
        print(f"  │ {name} │ {rule_count} │ {algorithm} │ {priority} │ {version} │ {status} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Recent Evaluations
    print("\n🔍 Recent Evaluation Results:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Subject              │ Resource             │ Action    │ Decision      │ Policy                       │ Time (ms) │ Reason                                                                        │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for subject, resource, action, result in results:
        subj = subject["id"][:20].ljust(20)
        res = resource["id"][:20].ljust(20)
        act = action["action"][:9].ljust(9)
        
        decision_icon = {"permit": "✓", "deny": "✗", "not_applicable": "○", "indeterminate": "?"}.get(result.decision.value, "?")
        decision = f"{decision_icon} {result.decision.value}"[:13].ljust(13)
        
        pol = engine.policies.get(result.policy_id)
        pol_name = pol.name if pol else "N/A"
        pol_name = pol_name[:28].ljust(28)
        
        time_ms = f"{result.evaluation_time_ms:.2f}".ljust(9)
        reason = result.reason[:79].ljust(79)
        
        print(f"  │ {subj} │ {res} │ {act} │ {decision} │ {pol_name} │ {time_ms} │ {reason} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Recent Audit Records
    print("\n📋 Recent Audit Records:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Subject              │ Resource             │ Action    │ Decision      │ Timestamp            │ Reason                                                                                              │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for record in engine.audit_records[-10:]:
        subj = record.subject_id[:20].ljust(20)
        res = record.resource_id[:20].ljust(20)
        act = record.action[:9].ljust(9)
        
        decision_icon = {"permit": "✓", "deny": "✗"}.get(record.decision.value, "○")
        decision = f"{decision_icon} {record.decision.value}"[:13].ljust(13)
        
        timestamp = record.timestamp.strftime("%Y-%m-%d %H:%M:%S")[:20].ljust(20)
        reason = record.reason[:101].ljust(101)
        
        print(f"  │ {subj} │ {res} │ {act} │ {decision} │ {timestamp} │ {reason} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Statistics
    stats = engine.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Attributes: {stats['total_attributes']}")
    print(f"  Rules: {stats['enabled_rules']}/{stats['total_rules']} enabled")
    print(f"  Policies: {stats['active_policies']}/{stats['total_policies']} active")
    print(f"  Policy Sets: {stats['total_policy_sets']}")
    print(f"  Total Evaluations: {stats['total_evaluations']}")
    print(f"  Cache: {stats['cache_size']} entries, {stats['cache_hit_rate']:.1f}% hit rate")
    print(f"  Audit Records: {stats['total_audit_records']}")
    print(f"  Decisions: {stats['permitted_decisions']} permitted, {stats['denied_decisions']} denied")
    
    print("\n  Policies by Algorithm:")
    for alg, count in stats['policies_by_algorithm'].items():
        print(f"    {alg}: {count}")
        
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                     Policy Engine Platform                         │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Attribute Definitions:        {stats['total_attributes']:>12}                      │")
    print(f"│ Rules (enabled):              {stats['enabled_rules']:>12}                      │")
    print(f"│ Policies (active):            {stats['active_policies']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Evaluations:            {stats['total_evaluations']:>12}                      │")
    print(f"│ Cache Hit Rate:                     {stats['cache_hit_rate']:>6.1f}%                      │")
    print(f"│ Permitted / Denied:      {stats['permitted_decisions']:>5} / {stats['denied_decisions']:<5}                          │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Policy Engine Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
