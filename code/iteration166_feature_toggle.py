#!/usr/bin/env python3
"""
Server Init - Iteration 166: Feature Toggle Platform
Платформа управления фича-флагами

Функционал:
- Feature Flag Management - управление фича-флагами
- Targeting Rules - правила таргетинга
- Gradual Rollouts - постепенные раскатки
- A/B Testing - A/B тестирование
- Environment Management - управление окружениями
- Audit Logging - аудит изменений
- SDK Integration - интеграция SDK
- Analytics - аналитика использования
"""

import asyncio
import json
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Union
from enum import Enum
import uuid
import random


class FlagType(Enum):
    """Тип флага"""
    BOOLEAN = "boolean"
    STRING = "string"
    NUMBER = "number"
    JSON = "json"


class FlagStatus(Enum):
    """Статус флага"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class OperatorType(Enum):
    """Тип оператора"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    IN = "in"
    NOT_IN = "not_in"
    MATCHES_REGEX = "matches_regex"


class RolloutStrategy(Enum):
    """Стратегия раскатки"""
    ALL = "all"
    NONE = "none"
    PERCENTAGE = "percentage"
    USER_LIST = "user_list"
    SEGMENT = "segment"
    GRADUAL = "gradual"


@dataclass
class TargetingAttribute:
    """Атрибут таргетинга"""
    attribute: str  # user_id, email, country, plan, etc.
    operator: OperatorType = OperatorType.EQUALS
    value: Any = None


@dataclass
class TargetingRule:
    """Правило таргетинга"""
    rule_id: str
    name: str = ""
    
    # Conditions (AND)
    conditions: List[TargetingAttribute] = field(default_factory=list)
    
    # Serve value
    serve_value: Any = True
    
    # Priority (lower = higher priority)
    priority: int = 100
    
    # Enabled
    enabled: bool = True


@dataclass
class RolloutConfig:
    """Конфигурация раскатки"""
    strategy: RolloutStrategy = RolloutStrategy.ALL
    
    # Percentage rollout
    percentage: float = 100.0
    
    # User list
    user_ids: List[str] = field(default_factory=list)
    
    # Segment
    segment_id: str = ""
    
    # Gradual rollout
    start_percentage: float = 0.0
    end_percentage: float = 100.0
    duration_hours: int = 24
    started_at: Optional[datetime] = None


@dataclass
class Variation:
    """Вариация значения"""
    variation_id: str
    name: str = ""
    value: Any = None
    
    # Weight for percentage split
    weight: int = 100


@dataclass
class FeatureFlag:
    """Фича-флаг"""
    flag_id: str
    key: str = ""
    name: str = ""
    description: str = ""
    
    # Type
    flag_type: FlagType = FlagType.BOOLEAN
    
    # Status
    status: FlagStatus = FlagStatus.ACTIVE
    
    # Default value
    default_value: Any = False
    
    # Variations (for multi-variate flags)
    variations: List[Variation] = field(default_factory=list)
    
    # Targeting rules
    targeting_rules: List[TargetingRule] = field(default_factory=list)
    
    # Rollout
    rollout: Optional[RolloutConfig] = None
    
    # Environments
    environments: Dict[str, bool] = field(default_factory=dict)  # env -> enabled
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Owner
    owner_id: str = ""
    project_id: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class UserContext:
    """Контекст пользователя"""
    user_id: str
    
    # Attributes
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    # Custom properties
    email: str = ""
    country: str = ""
    plan: str = ""
    beta_user: bool = False


@dataclass
class Segment:
    """Сегмент пользователей"""
    segment_id: str
    name: str = ""
    description: str = ""
    
    # Rules
    rules: List[TargetingRule] = field(default_factory=list)
    
    # Static user list
    included_users: Set[str] = field(default_factory=set)
    excluded_users: Set[str] = field(default_factory=set)


@dataclass
class Experiment:
    """A/B эксперимент"""
    experiment_id: str
    name: str = ""
    description: str = ""
    
    # Flag
    flag_id: str = ""
    
    # Variations
    variations: List[Variation] = field(default_factory=list)
    
    # Traffic allocation
    traffic_percentage: float = 100.0
    
    # Metrics
    primary_metric: str = ""
    secondary_metrics: List[str] = field(default_factory=list)
    
    # Status
    status: str = "draft"  # draft, running, paused, completed
    
    # Results
    results: Dict[str, Dict] = field(default_factory=dict)
    
    # Timeline
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None


@dataclass
class FlagEvaluation:
    """Результат оценки флага"""
    flag_key: str
    value: Any
    
    # Metadata
    variation_id: str = ""
    rule_id: str = ""
    reason: str = ""  # default, rule, rollout, experiment
    
    # Timing
    evaluated_at: datetime = field(default_factory=datetime.now)


@dataclass
class AuditLogEntry:
    """Запись аудит-лога"""
    entry_id: str
    
    # Action
    action: str = ""  # created, updated, deleted, toggled
    entity_type: str = ""  # flag, segment, experiment
    entity_id: str = ""
    
    # Changes
    old_value: Any = None
    new_value: Any = None
    
    # Actor
    actor_id: str = ""
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)


class FlagEvaluator:
    """Оценщик флагов"""
    
    def __init__(self):
        self.evaluation_cache: Dict[str, FlagEvaluation] = {}
        
    def evaluate(self, flag: FeatureFlag, context: UserContext,
                  environment: str = "production") -> FlagEvaluation:
        """Оценка флага"""
        # Check if flag is active
        if flag.status != FlagStatus.ACTIVE:
            return FlagEvaluation(
                flag_key=flag.key,
                value=flag.default_value,
                reason="inactive"
            )
            
        # Check environment
        if environment in flag.environments and not flag.environments[environment]:
            return FlagEvaluation(
                flag_key=flag.key,
                value=flag.default_value,
                reason="environment_disabled"
            )
            
        # Check targeting rules
        for rule in sorted(flag.targeting_rules, key=lambda r: r.priority):
            if rule.enabled and self._matches_rule(rule, context):
                return FlagEvaluation(
                    flag_key=flag.key,
                    value=rule.serve_value,
                    rule_id=rule.rule_id,
                    reason="rule"
                )
                
        # Check rollout
        if flag.rollout:
            in_rollout, value = self._check_rollout(flag, context)
            if in_rollout:
                return FlagEvaluation(
                    flag_key=flag.key,
                    value=value,
                    reason="rollout"
                )
                
        # Return default
        return FlagEvaluation(
            flag_key=flag.key,
            value=flag.default_value,
            reason="default"
        )
        
    def _matches_rule(self, rule: TargetingRule, context: UserContext) -> bool:
        """Проверка соответствия правилу"""
        for condition in rule.conditions:
            if not self._evaluate_condition(condition, context):
                return False
        return True
        
    def _evaluate_condition(self, condition: TargetingAttribute,
                             context: UserContext) -> bool:
        """Оценка условия"""
        # Get attribute value from context
        if condition.attribute == "user_id":
            attr_value = context.user_id
        elif condition.attribute in context.attributes:
            attr_value = context.attributes[condition.attribute]
        elif hasattr(context, condition.attribute):
            attr_value = getattr(context, condition.attribute)
        else:
            return False
            
        # Evaluate operator
        op = condition.operator
        target = condition.value
        
        if op == OperatorType.EQUALS:
            return attr_value == target
        elif op == OperatorType.NOT_EQUALS:
            return attr_value != target
        elif op == OperatorType.CONTAINS:
            return target in str(attr_value)
        elif op == OperatorType.STARTS_WITH:
            return str(attr_value).startswith(str(target))
        elif op == OperatorType.ENDS_WITH:
            return str(attr_value).endswith(str(target))
        elif op == OperatorType.GREATER_THAN:
            return attr_value > target
        elif op == OperatorType.LESS_THAN:
            return attr_value < target
        elif op == OperatorType.IN:
            return attr_value in target
        elif op == OperatorType.NOT_IN:
            return attr_value not in target
            
        return False
        
    def _check_rollout(self, flag: FeatureFlag, context: UserContext) -> tuple:
        """Проверка раскатки"""
        rollout = flag.rollout
        
        if rollout.strategy == RolloutStrategy.ALL:
            return True, flag.default_value if flag.default_value else True
            
        elif rollout.strategy == RolloutStrategy.NONE:
            return False, flag.default_value
            
        elif rollout.strategy == RolloutStrategy.PERCENTAGE:
            # Consistent hashing based on user_id
            hash_input = f"{flag.flag_id}:{context.user_id}"
            hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
            bucket = (hash_value % 100)
            
            return bucket < rollout.percentage, True
            
        elif rollout.strategy == RolloutStrategy.USER_LIST:
            return context.user_id in rollout.user_ids, True
            
        elif rollout.strategy == RolloutStrategy.GRADUAL:
            if rollout.started_at:
                elapsed = (datetime.now() - rollout.started_at).total_seconds() / 3600
                progress = min(1.0, elapsed / rollout.duration_hours)
                current_pct = rollout.start_percentage + (rollout.end_percentage - rollout.start_percentage) * progress
                
                hash_input = f"{flag.flag_id}:{context.user_id}"
                hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
                bucket = (hash_value % 100)
                
                return bucket < current_pct, True
                
        return False, flag.default_value


class FlagManager:
    """Менеджер флагов"""
    
    def __init__(self):
        self.flags: Dict[str, FeatureFlag] = {}
        self.flags_by_key: Dict[str, str] = {}  # key -> flag_id
        
    def create_flag(self, key: str, name: str, flag_type: FlagType = FlagType.BOOLEAN,
                     default_value: Any = False, description: str = "") -> FeatureFlag:
        """Создание флага"""
        flag = FeatureFlag(
            flag_id=f"flag_{uuid.uuid4().hex[:8]}",
            key=key,
            name=name,
            flag_type=flag_type,
            default_value=default_value,
            description=description,
            environments={"production": True, "staging": True, "development": True}
        )
        
        self.flags[flag.flag_id] = flag
        self.flags_by_key[key] = flag.flag_id
        
        return flag
        
    def get_flag(self, key: str) -> Optional[FeatureFlag]:
        """Получение флага по ключу"""
        flag_id = self.flags_by_key.get(key)
        return self.flags.get(flag_id) if flag_id else None
        
    def update_flag(self, flag_id: str, **updates) -> Optional[FeatureFlag]:
        """Обновление флага"""
        if flag_id not in self.flags:
            return None
            
        flag = self.flags[flag_id]
        
        for key, value in updates.items():
            if hasattr(flag, key):
                setattr(flag, key, value)
                
        flag.updated_at = datetime.now()
        return flag
        
    def toggle_flag(self, flag_id: str, enabled: bool, environment: str = "production"):
        """Переключение флага"""
        if flag_id in self.flags:
            self.flags[flag_id].environments[environment] = enabled
            self.flags[flag_id].updated_at = datetime.now()
            
    def add_targeting_rule(self, flag_id: str, rule: TargetingRule):
        """Добавление правила таргетинга"""
        if flag_id in self.flags:
            self.flags[flag_id].targeting_rules.append(rule)
            self.flags[flag_id].updated_at = datetime.now()


class SegmentManager:
    """Менеджер сегментов"""
    
    def __init__(self):
        self.segments: Dict[str, Segment] = {}
        
    def create_segment(self, name: str, description: str = "") -> Segment:
        """Создание сегмента"""
        segment = Segment(
            segment_id=f"seg_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description
        )
        self.segments[segment.segment_id] = segment
        return segment
        
    def add_rule(self, segment_id: str, rule: TargetingRule):
        """Добавление правила"""
        if segment_id in self.segments:
            self.segments[segment_id].rules.append(rule)
            
    def is_user_in_segment(self, segment_id: str, context: UserContext) -> bool:
        """Проверка принадлежности к сегменту"""
        segment = self.segments.get(segment_id)
        
        if not segment:
            return False
            
        # Check exclusion list
        if context.user_id in segment.excluded_users:
            return False
            
        # Check inclusion list
        if context.user_id in segment.included_users:
            return True
            
        # Evaluate rules
        evaluator = FlagEvaluator()
        
        for rule in segment.rules:
            if evaluator._matches_rule(rule, context):
                return True
                
        return False


class ExperimentManager:
    """Менеджер экспериментов"""
    
    def __init__(self, flag_manager: FlagManager):
        self.flag_manager = flag_manager
        self.experiments: Dict[str, Experiment] = {}
        self.assignments: Dict[str, Dict[str, str]] = {}  # user_id -> {experiment_id: variation_id}
        
    def create_experiment(self, name: str, flag_key: str,
                           variations: List[Variation]) -> Experiment:
        """Создание эксперимента"""
        flag = self.flag_manager.get_flag(flag_key)
        
        experiment = Experiment(
            experiment_id=f"exp_{uuid.uuid4().hex[:8]}",
            name=name,
            flag_id=flag.flag_id if flag else "",
            variations=variations
        )
        
        self.experiments[experiment.experiment_id] = experiment
        return experiment
        
    def start_experiment(self, experiment_id: str):
        """Запуск эксперимента"""
        if experiment_id in self.experiments:
            exp = self.experiments[experiment_id]
            exp.status = "running"
            exp.started_at = datetime.now()
            
    def stop_experiment(self, experiment_id: str):
        """Остановка эксперимента"""
        if experiment_id in self.experiments:
            exp = self.experiments[experiment_id]
            exp.status = "completed"
            exp.ended_at = datetime.now()
            
    def get_variation(self, experiment_id: str, user_id: str) -> Optional[Variation]:
        """Получение вариации для пользователя"""
        exp = self.experiments.get(experiment_id)
        
        if not exp or exp.status != "running":
            return None
            
        # Check existing assignment
        if user_id in self.assignments:
            if experiment_id in self.assignments[user_id]:
                var_id = self.assignments[user_id][experiment_id]
                for var in exp.variations:
                    if var.variation_id == var_id:
                        return var
                        
        # Check traffic allocation
        hash_input = f"{experiment_id}:{user_id}:traffic"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        
        if (hash_value % 100) >= exp.traffic_percentage:
            return None  # Not in experiment
            
        # Assign variation based on weights
        hash_input = f"{experiment_id}:{user_id}:variation"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        
        total_weight = sum(v.weight for v in exp.variations)
        bucket = hash_value % total_weight
        
        cumulative = 0
        for var in exp.variations:
            cumulative += var.weight
            if bucket < cumulative:
                # Store assignment
                if user_id not in self.assignments:
                    self.assignments[user_id] = {}
                self.assignments[user_id][experiment_id] = var.variation_id
                return var
                
        return exp.variations[-1] if exp.variations else None


class AnalyticsTracker:
    """Трекер аналитики"""
    
    def __init__(self):
        self.evaluations: List[FlagEvaluation] = []
        self.flag_stats: Dict[str, Dict] = {}
        
    def track_evaluation(self, evaluation: FlagEvaluation, context: UserContext):
        """Отслеживание оценки"""
        self.evaluations.append(evaluation)
        
        key = evaluation.flag_key
        
        if key not in self.flag_stats:
            self.flag_stats[key] = {
                "total_evaluations": 0,
                "unique_users": set(),
                "by_value": {},
                "by_reason": {}
            }
            
        stats = self.flag_stats[key]
        stats["total_evaluations"] += 1
        stats["unique_users"].add(context.user_id)
        
        value_key = str(evaluation.value)
        stats["by_value"][value_key] = stats["by_value"].get(value_key, 0) + 1
        
        reason = evaluation.reason
        stats["by_reason"][reason] = stats["by_reason"].get(reason, 0) + 1
        
    def get_flag_analytics(self, flag_key: str) -> Dict[str, Any]:
        """Аналитика флага"""
        stats = self.flag_stats.get(flag_key)
        
        if not stats:
            return {}
            
        return {
            "flag_key": flag_key,
            "total_evaluations": stats["total_evaluations"],
            "unique_users": len(stats["unique_users"]),
            "value_distribution": stats["by_value"],
            "reason_distribution": stats["by_reason"]
        }


class AuditLogger:
    """Логгер аудита"""
    
    def __init__(self):
        self.entries: List[AuditLogEntry] = []
        
    def log(self, action: str, entity_type: str, entity_id: str,
             old_value: Any = None, new_value: Any = None, actor_id: str = ""):
        """Логирование действия"""
        entry = AuditLogEntry(
            entry_id=f"audit_{uuid.uuid4().hex[:8]}",
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
            actor_id=actor_id
        )
        self.entries.append(entry)
        
    def get_flag_history(self, flag_id: str) -> List[AuditLogEntry]:
        """История флага"""
        return [e for e in self.entries 
                if e.entity_type == "flag" and e.entity_id == flag_id]


class FeatureTogglePlatform:
    """Платформа фича-флагов"""
    
    def __init__(self):
        self.flag_manager = FlagManager()
        self.segment_manager = SegmentManager()
        self.experiment_manager = ExperimentManager(self.flag_manager)
        self.evaluator = FlagEvaluator()
        self.analytics = AnalyticsTracker()
        self.audit = AuditLogger()
        
    def evaluate(self, flag_key: str, context: UserContext,
                  environment: str = "production") -> Any:
        """Оценка флага"""
        flag = self.flag_manager.get_flag(flag_key)
        
        if not flag:
            return None
            
        evaluation = self.evaluator.evaluate(flag, context, environment)
        self.analytics.track_evaluation(evaluation, context)
        
        return evaluation.value
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        return {
            "total_flags": len(self.flag_manager.flags),
            "active_flags": sum(1 for f in self.flag_manager.flags.values() 
                               if f.status == FlagStatus.ACTIVE),
            "segments": len(self.segment_manager.segments),
            "experiments": len(self.experiment_manager.experiments),
            "total_evaluations": sum(s["total_evaluations"] 
                                     for s in self.analytics.flag_stats.values())
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 166: Feature Toggle Platform")
    print("=" * 60)
    
    platform = FeatureTogglePlatform()
    print("✓ Feature Toggle Platform created")
    
    # Create feature flags
    print("\n🚩 Creating Feature Flags...")
    
    # Simple boolean flag
    dark_mode = platform.flag_manager.create_flag(
        key="dark_mode",
        name="Dark Mode",
        flag_type=FlagType.BOOLEAN,
        default_value=False,
        description="Enable dark mode UI"
    )
    
    # Flag with targeting
    new_dashboard = platform.flag_manager.create_flag(
        key="new_dashboard",
        name="New Dashboard",
        flag_type=FlagType.BOOLEAN,
        default_value=False,
        description="New dashboard experience"
    )
    
    # Add targeting rule for beta users
    beta_rule = TargetingRule(
        rule_id=f"rule_{uuid.uuid4().hex[:8]}",
        name="Beta Users",
        conditions=[
            TargetingAttribute(
                attribute="beta_user",
                operator=OperatorType.EQUALS,
                value=True
            )
        ],
        serve_value=True,
        priority=10
    )
    platform.flag_manager.add_targeting_rule(new_dashboard.flag_id, beta_rule)
    
    # Flag with percentage rollout
    new_checkout = platform.flag_manager.create_flag(
        key="new_checkout",
        name="New Checkout Flow",
        flag_type=FlagType.BOOLEAN,
        default_value=False,
        description="Redesigned checkout process"
    )
    new_checkout.rollout = RolloutConfig(
        strategy=RolloutStrategy.PERCENTAGE,
        percentage=30.0
    )
    
    # Multi-variate flag
    button_color = platform.flag_manager.create_flag(
        key="button_color",
        name="CTA Button Color",
        flag_type=FlagType.STRING,
        default_value="blue",
        description="Call-to-action button color"
    )
    button_color.variations = [
        Variation(variation_id="v1", name="Blue", value="blue", weight=50),
        Variation(variation_id="v2", name="Green", value="green", weight=30),
        Variation(variation_id="v3", name="Orange", value="orange", weight=20),
    ]
    
    # Gradual rollout flag
    ai_features = platform.flag_manager.create_flag(
        key="ai_features",
        name="AI Features",
        flag_type=FlagType.BOOLEAN,
        default_value=False,
        description="AI-powered features"
    )
    ai_features.rollout = RolloutConfig(
        strategy=RolloutStrategy.GRADUAL,
        start_percentage=10.0,
        end_percentage=100.0,
        duration_hours=168,  # 1 week
        started_at=datetime.now() - timedelta(hours=48)  # Started 2 days ago
    )
    
    print(f"  ✓ Created {len(platform.flag_manager.flags)} flags")
    
    # Create segments
    print("\n👥 Creating Segments...")
    
    # Premium users segment
    premium_segment = platform.segment_manager.create_segment(
        "Premium Users",
        "Users on premium plan"
    )
    premium_rule = TargetingRule(
        rule_id=f"rule_{uuid.uuid4().hex[:8]}",
        name="Premium Plan",
        conditions=[
            TargetingAttribute(
                attribute="plan",
                operator=OperatorType.IN,
                value=["premium", "enterprise"]
            )
        ]
    )
    platform.segment_manager.add_rule(premium_segment.segment_id, premium_rule)
    
    # US users segment
    us_segment = platform.segment_manager.create_segment(
        "US Users",
        "Users from United States"
    )
    us_rule = TargetingRule(
        rule_id=f"rule_{uuid.uuid4().hex[:8]}",
        name="US Country",
        conditions=[
            TargetingAttribute(
                attribute="country",
                operator=OperatorType.EQUALS,
                value="US"
            )
        ]
    )
    platform.segment_manager.add_rule(us_segment.segment_id, us_rule)
    
    print(f"  ✓ Created {len(platform.segment_manager.segments)} segments")
    
    # Create experiment
    print("\n🧪 Creating A/B Experiment...")
    
    experiment = platform.experiment_manager.create_experiment(
        "Checkout Button Test",
        "button_color",
        [
            Variation(variation_id="control", name="Control (Blue)", value="blue", weight=50),
            Variation(variation_id="variant", name="Variant (Green)", value="green", weight=50),
        ]
    )
    experiment.primary_metric = "conversion_rate"
    experiment.traffic_percentage = 50.0
    platform.experiment_manager.start_experiment(experiment.experiment_id)
    
    print(f"  ✓ Created experiment: {experiment.name}")
    
    # Evaluate flags for different users
    print("\n🔍 Evaluating Flags...")
    
    test_users = [
        UserContext(user_id="user-001", email="alice@example.com", country="US", plan="premium", beta_user=True),
        UserContext(user_id="user-002", email="bob@example.com", country="UK", plan="free", beta_user=False),
        UserContext(user_id="user-003", email="carol@example.com", country="US", plan="enterprise", beta_user=True),
        UserContext(user_id="user-004", email="dave@example.com", country="DE", plan="starter", beta_user=False),
        UserContext(user_id="user-005", email="eve@example.com", country="US", plan="free", beta_user=False),
    ]
    
    flag_keys = ["dark_mode", "new_dashboard", "new_checkout", "ai_features"]
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────┐")
    print("  │ User        │ dark_mode │ new_dashboard │ new_checkout │ ai_features │")
    print("  ├───────────────────────────────────────────────────────────────────────────────┤")
    
    for user in test_users:
        values = []
        for key in flag_keys:
            value = platform.evaluate(key, user)
            values.append("✓" if value else "✗")
            
        user_id = user.user_id[:11].ljust(11)
        v_str = " │ ".join(v.center(11 if i > 0 else 9) for i, v in enumerate(values))
        print(f"  │ {user_id} │ {v_str} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────┘")
    
    # Segment membership
    print("\n📊 Segment Membership:")
    
    for user in test_users:
        in_premium = platform.segment_manager.is_user_in_segment(premium_segment.segment_id, user)
        in_us = platform.segment_manager.is_user_in_segment(us_segment.segment_id, user)
        
        segments = []
        if in_premium:
            segments.append("Premium")
        if in_us:
            segments.append("US")
            
        seg_str = ", ".join(segments) if segments else "None"
        print(f"  {user.user_id}: {seg_str}")
        
    # Experiment variations
    print("\n🎯 Experiment Assignments:")
    
    for user in test_users:
        variation = platform.experiment_manager.get_variation(experiment.experiment_id, user.user_id)
        var_name = variation.name if variation else "Not in experiment"
        print(f"  {user.user_id}: {var_name}")
        
    # Simulate more evaluations for analytics
    print("\n📈 Simulating Traffic (1000 evaluations)...")
    
    for i in range(1000):
        user = UserContext(
            user_id=f"user-{i:04d}",
            email=f"user{i}@example.com",
            country=random.choice(["US", "UK", "DE", "FR", "JP"]),
            plan=random.choice(["free", "starter", "premium", "enterprise"]),
            beta_user=random.random() < 0.1
        )
        
        for key in flag_keys:
            platform.evaluate(key, user)
            
    print("  ✓ Completed 1000 evaluations per flag")
    
    # Flag analytics
    print("\n📊 Flag Analytics:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────┐")
    print("  │ Flag            │ Evaluations │ Users  │ True %  │ False % │")
    print("  ├────────────────────────────────────────────────────────────────────────┤")
    
    for key in flag_keys:
        analytics = platform.analytics.get_flag_analytics(key)
        
        if analytics:
            flag_name = key[:15].ljust(15)
            total = str(analytics["total_evaluations"]).ljust(11)
            users = str(analytics["unique_users"]).ljust(6)
            
            true_count = analytics["value_distribution"].get("True", 0)
            false_count = analytics["value_distribution"].get("False", 0)
            total_count = true_count + false_count
            
            true_pct = f"{true_count / total_count * 100:.1f}%".ljust(7) if total_count > 0 else "N/A".ljust(7)
            false_pct = f"{false_count / total_count * 100:.1f}%".ljust(7) if total_count > 0 else "N/A".ljust(7)
            
            print(f"  │ {flag_name} │ {total} │ {users} │ {true_pct} │ {false_pct} │")
            
    print("  └────────────────────────────────────────────────────────────────────────┘")
    
    # Flag configuration
    print("\n⚙️ Flag Configuration:")
    
    for flag in platform.flag_manager.flags.values():
        rollout_info = ""
        if flag.rollout:
            if flag.rollout.strategy == RolloutStrategy.PERCENTAGE:
                rollout_info = f"Percentage: {flag.rollout.percentage}%"
            elif flag.rollout.strategy == RolloutStrategy.GRADUAL:
                elapsed = (datetime.now() - flag.rollout.started_at).total_seconds() / 3600
                progress = min(100, elapsed / flag.rollout.duration_hours * 100)
                rollout_info = f"Gradual: {progress:.0f}% complete"
                
        rules_count = len(flag.targeting_rules)
        
        print(f"\n  🚩 {flag.name} ({flag.key})")
        print(f"     Type: {flag.flag_type.value}, Default: {flag.default_value}")
        print(f"     Targeting Rules: {rules_count}")
        if rollout_info:
            print(f"     Rollout: {rollout_info}")
            
    # Platform statistics
    print("\n📊 Platform Statistics:")
    
    stats = platform.get_statistics()
    
    print(f"\n  Total Flags: {stats['total_flags']}")
    print(f"  Active Flags: {stats['active_flags']}")
    print(f"  Segments: {stats['segments']}")
    print(f"  Experiments: {stats['experiments']}")
    print(f"  Total Evaluations: {stats['total_evaluations']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Feature Toggle Dashboard                         │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Flags:                  {stats['total_flags']:>10}                       │")
    print(f"│ Active Flags:                 {stats['active_flags']:>10}                       │")
    print(f"│ User Segments:                {stats['segments']:>10}                       │")
    print(f"│ Active Experiments:           {stats['experiments']:>10}                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Evaluations:            {stats['total_evaluations']:>10}                       │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Feature Toggle Platform initialized!")
    print("=" * 60)
