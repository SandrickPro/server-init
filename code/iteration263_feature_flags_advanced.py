#!/usr/bin/env python3
"""
Server Init - Iteration 263: Feature Flags Advanced Platform
Расширенная платформа управления флагами функций

Функционал:
- Flag Management - управление флагами
- Targeting Rules - правила таргетинга
- Percentage Rollouts - процентное раскатывание
- A/B Testing - A/B тестирование
- Scheduled Flags - запланированные флаги
- Flag Dependencies - зависимости флагов
- Audit Logging - аудит логирование
- Analytics Integration - интеграция аналитики
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import hashlib


class FlagType(Enum):
    """Тип флага"""
    BOOLEAN = "boolean"
    STRING = "string"
    INTEGER = "integer"
    JSON = "json"


class FlagState(Enum):
    """Состояние флага"""
    ENABLED = "enabled"
    DISABLED = "disabled"
    SCHEDULED = "scheduled"
    ARCHIVED = "archived"


class RuleOperator(Enum):
    """Оператор правила"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IN = "in"
    NOT_IN = "not_in"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    MATCHES_REGEX = "matches_regex"


class RolloutStrategy(Enum):
    """Стратегия раскатывания"""
    ALL = "all"
    PERCENTAGE = "percentage"
    USER_IDS = "user_ids"
    GROUPS = "groups"
    CUSTOM = "custom"


@dataclass
class TargetingRule:
    """Правило таргетинга"""
    rule_id: str
    name: str
    
    # Conditions
    attribute: str = ""  # user attribute to check
    operator: RuleOperator = RuleOperator.EQUALS
    value: Any = None
    
    # Result
    enabled: bool = True
    variation: Optional[str] = None
    
    # Priority
    priority: int = 0


@dataclass
class Variant:
    """Вариант значения флага"""
    variant_id: str
    name: str
    value: Any = None
    weight: int = 50  # percentage weight for rollout


@dataclass
class Schedule:
    """Расписание флага"""
    schedule_id: str
    
    # Timing
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    
    # Value
    enabled_value: bool = True
    
    # Timezone
    timezone: str = "UTC"


@dataclass
class FeatureFlag:
    """Флаг функции"""
    flag_id: str
    key: str  # unique identifier
    name: str
    
    # Type
    flag_type: FlagType = FlagType.BOOLEAN
    
    # State
    state: FlagState = FlagState.DISABLED
    
    # Values
    default_value: Any = False
    variants: List[Variant] = field(default_factory=list)
    
    # Targeting
    targeting_rules: List[TargetingRule] = field(default_factory=list)
    
    # Rollout
    rollout_strategy: RolloutStrategy = RolloutStrategy.ALL
    rollout_percentage: int = 100
    rollout_user_ids: Set[str] = field(default_factory=set)
    rollout_groups: Set[str] = field(default_factory=set)
    
    # Schedule
    schedules: List[Schedule] = field(default_factory=list)
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)  # flag keys
    
    # Metadata
    description: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Stats
    evaluations: int = 0
    enabled_count: int = 0
    disabled_count: int = 0
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class EvaluationContext:
    """Контекст оценки флага"""
    user_id: Optional[str] = None
    
    # User attributes
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    # Groups
    groups: List[str] = field(default_factory=list)
    
    # Custom
    custom: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationResult:
    """Результат оценки флага"""
    result_id: str
    flag_key: str
    
    # Value
    value: Any = None
    variant: Optional[str] = None
    
    # Reason
    reason: str = ""  # why this value was returned
    
    # Rule
    matched_rule_id: Optional[str] = None
    
    # Timing
    evaluated_at: datetime = field(default_factory=datetime.now)


@dataclass
class AuditLogEntry:
    """Запись аудит лога"""
    entry_id: str
    flag_key: str
    
    # Action
    action: str = ""  # created, updated, enabled, disabled, etc.
    
    # Changes
    previous_value: Any = None
    new_value: Any = None
    
    # User
    changed_by: str = ""
    
    # Timing
    timestamp: datetime = field(default_factory=datetime.now)


class FeatureFlagManager:
    """Менеджер флагов функций"""
    
    def __init__(self):
        self.flags: Dict[str, FeatureFlag] = {}
        self.audit_log: List[AuditLogEntry] = []
        self.evaluation_cache: Dict[str, EvaluationResult] = {}
        
    def create_flag(self, key: str, name: str,
                   flag_type: FlagType = FlagType.BOOLEAN,
                   default_value: Any = False,
                   description: str = "") -> FeatureFlag:
        """Создание флага"""
        flag = FeatureFlag(
            flag_id=f"flag_{uuid.uuid4().hex[:8]}",
            key=key,
            name=name,
            flag_type=flag_type,
            default_value=default_value,
            description=description
        )
        
        self.flags[key] = flag
        
        self._log_audit(key, "created", None, {"state": "disabled", "default": default_value})
        
        return flag
        
    def _log_audit(self, flag_key: str, action: str,
                  previous_value: Any = None, new_value: Any = None,
                  changed_by: str = "system"):
        """Запись в аудит лог"""
        entry = AuditLogEntry(
            entry_id=f"audit_{uuid.uuid4().hex[:8]}",
            flag_key=flag_key,
            action=action,
            previous_value=previous_value,
            new_value=new_value,
            changed_by=changed_by
        )
        
        self.audit_log.append(entry)
        
    def enable_flag(self, key: str, changed_by: str = "system"):
        """Включение флага"""
        flag = self.flags.get(key)
        if flag:
            old_state = flag.state
            flag.state = FlagState.ENABLED
            flag.updated_at = datetime.now()
            self._log_audit(key, "enabled", old_state.value, FlagState.ENABLED.value, changed_by)
            
    def disable_flag(self, key: str, changed_by: str = "system"):
        """Выключение флага"""
        flag = self.flags.get(key)
        if flag:
            old_state = flag.state
            flag.state = FlagState.DISABLED
            flag.updated_at = datetime.now()
            self._log_audit(key, "disabled", old_state.value, FlagState.DISABLED.value, changed_by)
            
    def add_targeting_rule(self, flag_key: str, name: str,
                          attribute: str, operator: RuleOperator,
                          value: Any, enabled: bool = True,
                          priority: int = 0) -> Optional[TargetingRule]:
        """Добавление правила таргетинга"""
        flag = self.flags.get(flag_key)
        if not flag:
            return None
            
        rule = TargetingRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name=name,
            attribute=attribute,
            operator=operator,
            value=value,
            enabled=enabled,
            priority=priority
        )
        
        flag.targeting_rules.append(rule)
        flag.targeting_rules.sort(key=lambda r: r.priority)
        flag.updated_at = datetime.now()
        
        self._log_audit(flag_key, "rule_added", None, {"rule": name})
        
        return rule
        
    def add_variant(self, flag_key: str, name: str,
                   value: Any, weight: int = 50) -> Optional[Variant]:
        """Добавление варианта"""
        flag = self.flags.get(flag_key)
        if not flag:
            return None
            
        variant = Variant(
            variant_id=f"var_{uuid.uuid4().hex[:8]}",
            name=name,
            value=value,
            weight=weight
        )
        
        flag.variants.append(variant)
        flag.updated_at = datetime.now()
        
        return variant
        
    def set_rollout_percentage(self, flag_key: str, percentage: int):
        """Установка процента раскатывания"""
        flag = self.flags.get(flag_key)
        if flag:
            old_pct = flag.rollout_percentage
            flag.rollout_percentage = max(0, min(100, percentage))
            flag.rollout_strategy = RolloutStrategy.PERCENTAGE
            flag.updated_at = datetime.now()
            self._log_audit(flag_key, "rollout_changed", old_pct, percentage)
            
    def add_schedule(self, flag_key: str,
                    start_at: datetime = None,
                    end_at: datetime = None) -> Optional[Schedule]:
        """Добавление расписания"""
        flag = self.flags.get(flag_key)
        if not flag:
            return None
            
        schedule = Schedule(
            schedule_id=f"sch_{uuid.uuid4().hex[:8]}",
            start_at=start_at,
            end_at=end_at
        )
        
        flag.schedules.append(schedule)
        flag.state = FlagState.SCHEDULED
        flag.updated_at = datetime.now()
        
        return schedule
        
    def _check_schedule(self, flag: FeatureFlag) -> bool:
        """Проверка расписания"""
        now = datetime.now()
        
        for schedule in flag.schedules:
            if schedule.start_at and now < schedule.start_at:
                continue
            if schedule.end_at and now > schedule.end_at:
                continue
            return schedule.enabled_value
            
        return False
        
    def _check_targeting_rules(self, flag: FeatureFlag,
                              context: EvaluationContext) -> Optional[TargetingRule]:
        """Проверка правил таргетинга"""
        for rule in flag.targeting_rules:
            attr_value = context.attributes.get(rule.attribute)
            
            if attr_value is None:
                continue
                
            matched = False
            
            if rule.operator == RuleOperator.EQUALS:
                matched = attr_value == rule.value
            elif rule.operator == RuleOperator.NOT_EQUALS:
                matched = attr_value != rule.value
            elif rule.operator == RuleOperator.CONTAINS:
                matched = rule.value in str(attr_value)
            elif rule.operator == RuleOperator.STARTS_WITH:
                matched = str(attr_value).startswith(str(rule.value))
            elif rule.operator == RuleOperator.IN:
                matched = attr_value in rule.value
            elif rule.operator == RuleOperator.GREATER_THAN:
                matched = float(attr_value) > float(rule.value)
            elif rule.operator == RuleOperator.LESS_THAN:
                matched = float(attr_value) < float(rule.value)
                
            if matched:
                return rule
                
        return None
        
    def _check_rollout(self, flag: FeatureFlag, context: EvaluationContext) -> bool:
        """Проверка раскатывания"""
        if flag.rollout_strategy == RolloutStrategy.ALL:
            return True
            
        if flag.rollout_strategy == RolloutStrategy.USER_IDS:
            return context.user_id in flag.rollout_user_ids
            
        if flag.rollout_strategy == RolloutStrategy.GROUPS:
            return any(g in flag.rollout_groups for g in context.groups)
            
        if flag.rollout_strategy == RolloutStrategy.PERCENTAGE:
            if context.user_id:
                # Consistent hash for user
                hash_input = f"{flag.key}:{context.user_id}"
                hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
                bucket = hash_value % 100
                return bucket < flag.rollout_percentage
            return random.randint(0, 99) < flag.rollout_percentage
            
        return False
        
    def _select_variant(self, flag: FeatureFlag, context: EvaluationContext) -> Optional[Variant]:
        """Выбор варианта"""
        if not flag.variants:
            return None
            
        if context.user_id:
            # Consistent variant selection
            hash_input = f"{flag.key}:variant:{context.user_id}"
            hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
            bucket = hash_value % 100
        else:
            bucket = random.randint(0, 99)
            
        cumulative = 0
        for variant in flag.variants:
            cumulative += variant.weight
            if bucket < cumulative:
                return variant
                
        return flag.variants[-1] if flag.variants else None
        
    def _check_dependencies(self, flag: FeatureFlag, context: EvaluationContext) -> bool:
        """Проверка зависимостей"""
        for dep_key in flag.depends_on:
            dep_result = self.evaluate(dep_key, context)
            if not dep_result.value:
                return False
        return True
        
    def evaluate(self, flag_key: str, context: EvaluationContext = None) -> EvaluationResult:
        """Оценка флага"""
        context = context or EvaluationContext()
        
        result = EvaluationResult(
            result_id=f"eval_{uuid.uuid4().hex[:8]}",
            flag_key=flag_key
        )
        
        flag = self.flags.get(flag_key)
        if not flag:
            result.value = False
            result.reason = "flag_not_found"
            return result
            
        # Update stats
        flag.evaluations += 1
        
        # Check state
        if flag.state == FlagState.DISABLED:
            result.value = flag.default_value
            result.reason = "flag_disabled"
            flag.disabled_count += 1
            return result
            
        if flag.state == FlagState.ARCHIVED:
            result.value = flag.default_value
            result.reason = "flag_archived"
            return result
            
        # Check dependencies
        if flag.depends_on and not self._check_dependencies(flag, context):
            result.value = flag.default_value
            result.reason = "dependency_not_met"
            return result
            
        # Check schedule
        if flag.state == FlagState.SCHEDULED:
            if not self._check_schedule(flag):
                result.value = flag.default_value
                result.reason = "outside_schedule"
                return result
                
        # Check targeting rules
        matched_rule = self._check_targeting_rules(flag, context)
        if matched_rule:
            result.value = matched_rule.enabled
            result.matched_rule_id = matched_rule.rule_id
            result.reason = f"rule_matched:{matched_rule.name}"
            if matched_rule.enabled:
                flag.enabled_count += 1
            else:
                flag.disabled_count += 1
            return result
            
        # Check rollout
        if not self._check_rollout(flag, context):
            result.value = flag.default_value
            result.reason = "rollout_excluded"
            flag.disabled_count += 1
            return result
            
        # Select variant if multivariate
        if flag.variants:
            variant = self._select_variant(flag, context)
            if variant:
                result.value = variant.value
                result.variant = variant.name
                result.reason = f"variant_selected:{variant.name}"
            else:
                result.value = flag.default_value
                result.reason = "default_value"
        else:
            result.value = True if flag.flag_type == FlagType.BOOLEAN else flag.default_value
            result.reason = "flag_enabled"
            
        flag.enabled_count += 1
        return result
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика флагов"""
        states = {state: 0 for state in FlagState}
        types = {ftype: 0 for ftype in FlagType}
        total_evaluations = 0
        
        for flag in self.flags.values():
            states[flag.state] += 1
            types[flag.flag_type] += 1
            total_evaluations += flag.evaluations
            
        return {
            "flags_total": len(self.flags),
            "audit_entries": len(self.audit_log),
            "total_evaluations": total_evaluations,
            "states": {s.value: c for s, c in states.items()},
            "types": {t.value: c for t, c in types.items()}
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 263: Feature Flags Advanced Platform")
    print("=" * 60)
    
    manager = FeatureFlagManager()
    print("✓ Feature Flag Manager created")
    
    # Create flags
    print("\n🚩 Creating Feature Flags...")
    
    # Boolean flag - new UI
    flag1 = manager.create_flag(
        "new_checkout_ui",
        "New Checkout UI",
        FlagType.BOOLEAN,
        False,
        "Enable new checkout experience"
    )
    
    # String flag - payment provider
    flag2 = manager.create_flag(
        "payment_provider",
        "Payment Provider",
        FlagType.STRING,
        "stripe",
        "Select payment provider"
    )
    manager.add_variant(flag2.key, "stripe", "stripe", 70)
    manager.add_variant(flag2.key, "paypal", "paypal", 30)
    
    # Boolean flag with targeting
    flag3 = manager.create_flag(
        "beta_features",
        "Beta Features",
        FlagType.BOOLEAN,
        False,
        "Enable beta features for specific users"
    )
    
    # Integer flag - max items
    flag4 = manager.create_flag(
        "max_cart_items",
        "Max Cart Items",
        FlagType.INTEGER,
        10,
        "Maximum items in cart"
    )
    
    for flag in [flag1, flag2, flag3, flag4]:
        print(f"  🚩 {flag.name}: {flag.flag_type.value}")
        
    # Enable flags and configure
    print("\n⚙️ Configuring Flags...")
    
    # Enable new checkout with 50% rollout
    manager.enable_flag("new_checkout_ui")
    manager.set_rollout_percentage("new_checkout_ui", 50)
    print("  ⚙️ new_checkout_ui: enabled, 50% rollout")
    
    # Enable payment provider
    manager.enable_flag("payment_provider")
    print("  ⚙️ payment_provider: enabled with variants")
    
    # Add targeting rules to beta features
    manager.enable_flag("beta_features")
    manager.add_targeting_rule(
        "beta_features",
        "Premium Users",
        "subscription",
        RuleOperator.EQUALS,
        "premium",
        True,
        1
    )
    manager.add_targeting_rule(
        "beta_features",
        "Internal Users",
        "email",
        RuleOperator.ENDS_WITH,
        "@company.com",
        True,
        2
    )
    print("  ⚙️ beta_features: enabled with targeting rules")
    
    # Schedule max cart items
    manager.enable_flag("max_cart_items")
    manager.add_schedule(
        "max_cart_items",
        datetime.now() - timedelta(hours=1),
        datetime.now() + timedelta(days=7)
    )
    print("  ⚙️ max_cart_items: scheduled")
    
    # Display flags
    print("\n🚩 Feature Flags:")
    
    print("\n  ┌─────────────────────┬───────────┬───────────┬──────────┬──────────┬──────────┐")
    print("  │ Flag                │ Type      │ State     │ Rollout  │ Rules    │ Evals    │")
    print("  ├─────────────────────┼───────────┼───────────┼──────────┼──────────┼──────────┤")
    
    for flag in manager.flags.values():
        name = flag.key[:19].ljust(19)
        ftype = flag.flag_type.value[:9].ljust(9)
        state = flag.state.value[:9].ljust(9)
        rollout = f"{flag.rollout_percentage}%"[:8].ljust(8)
        rules = str(len(flag.targeting_rules))[:8].ljust(8)
        evals = str(flag.evaluations)[:8].ljust(8)
        
        print(f"  │ {name} │ {ftype} │ {state} │ {rollout} │ {rules} │ {evals} │")
        
    print("  └─────────────────────┴───────────┴───────────┴──────────┴──────────┴──────────┘")
    
    # Evaluate flags
    print("\n🔍 Evaluating Flags...")
    
    # Test contexts
    contexts = [
        EvaluationContext(user_id="user_001", attributes={"subscription": "free"}),
        EvaluationContext(user_id="user_002", attributes={"subscription": "premium"}),
        EvaluationContext(user_id="user_003", attributes={"email": "john@company.com"}),
        EvaluationContext(user_id="user_004", attributes={"country": "US"}),
    ]
    
    for ctx in contexts:
        print(f"\n  User: {ctx.user_id}")
        for flag_key in ["new_checkout_ui", "beta_features", "payment_provider"]:
            result = manager.evaluate(flag_key, ctx)
            print(f"    {flag_key}: {result.value} ({result.reason})")
            
    # Targeting rules
    print("\n🎯 Targeting Rules:")
    
    for flag in manager.flags.values():
        if flag.targeting_rules:
            print(f"\n  {flag.name}:")
            for rule in flag.targeting_rules:
                print(f"    [{rule.priority}] {rule.name}: {rule.attribute} {rule.operator.value} {rule.value}")
                
    # Variants
    print("\n🔀 Variants:")
    
    for flag in manager.flags.values():
        if flag.variants:
            print(f"\n  {flag.name}:")
            for variant in flag.variants:
                print(f"    {variant.name}: {variant.value} ({variant.weight}%)")
                
    # State distribution
    print("\n📊 State Distribution:")
    
    for state in FlagState:
        count = sum(1 for f in manager.flags.values() if f.state == state)
        if count > 0:
            bar = "█" * count + "░" * (5 - count)
            print(f"  {state.value:10s} [{bar}] {count}")
            
    # Audit log
    print("\n📜 Recent Audit Log:")
    
    for entry in manager.audit_log[-8:]:
        print(f"  [{entry.timestamp.strftime('%H:%M:%S')}] {entry.flag_key}: {entry.action}")
        
    # Statistics
    print("\n📊 Manager Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Flags Total: {stats['flags_total']}")
    print(f"  Audit Entries: {stats['audit_entries']}")
    print(f"  Total Evaluations: {stats['total_evaluations']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                  Feature Flags Advanced Dashboard                   │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Flags Total:                   {stats['flags_total']:>12}                        │")
    print(f"│ Total Evaluations:             {stats['total_evaluations']:>12}                        │")
    print(f"│ Audit Entries:                 {stats['audit_entries']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Enabled:                       {stats['states']['enabled']:>12}                        │")
    print(f"│ Disabled:                      {stats['states']['disabled']:>12}                        │")
    print(f"│ Scheduled:                     {stats['states']['scheduled']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Feature Flags Advanced Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
