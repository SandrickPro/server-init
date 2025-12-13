#!/usr/bin/env python3
"""
Server Init - Iteration 102: Feature Flag Platform
Платформа управления feature flags

Функционал:
- Feature Toggles - переключатели функций
- Gradual Rollouts - постепенные выкатки
- A/B Testing - A/B тестирование
- User Targeting - таргетирование пользователей
- Environments - окружения
- Audit Logging - аудит
- SDK Integration - интеграция SDK
- Analytics - аналитика
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Union, Tuple
from enum import Enum
from collections import defaultdict
import uuid
import random
import hashlib


class FlagType(Enum):
    """Тип флага"""
    BOOLEAN = "boolean"
    STRING = "string"
    NUMBER = "number"
    JSON = "json"


class RolloutType(Enum):
    """Тип выкатки"""
    PERCENTAGE = "percentage"
    USER_LIST = "user_list"
    USER_ATTRIBUTE = "user_attribute"
    SCHEDULE = "schedule"
    GRADUAL = "gradual"


class EnvironmentType(Enum):
    """Тип окружения"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class ExperimentStatus(Enum):
    """Статус эксперимента"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass
class UserContext:
    """Контекст пользователя"""
    user_id: str
    
    # Attributes
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    # Segments
    segments: List[str] = field(default_factory=list)
    
    # Device
    device_type: str = ""
    platform: str = ""
    
    # Location
    country: str = ""
    region: str = ""


@dataclass
class TargetingRule:
    """Правило таргетирования"""
    rule_id: str
    name: str = ""
    
    # Conditions
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Result
    variation: str = ""
    percentage: int = 100


@dataclass
class Variation:
    """Вариация флага"""
    variation_id: str
    name: str = ""
    value: Any = None
    description: str = ""


@dataclass
class FeatureFlag:
    """Feature flag"""
    flag_id: str
    key: str = ""
    name: str = ""
    description: str = ""
    
    # Type
    flag_type: FlagType = FlagType.BOOLEAN
    
    # Variations
    variations: List[Variation] = field(default_factory=list)
    default_variation: str = ""
    
    # Targeting
    targeting_rules: List[TargetingRule] = field(default_factory=list)
    
    # Rollout
    rollout_percentage: int = 0
    
    # Status
    enabled: bool = False
    
    # Environment overrides
    environment_settings: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""


@dataclass
class GradualRollout:
    """Постепенная выкатка"""
    rollout_id: str
    flag_key: str = ""
    
    # Progress
    current_percentage: int = 0
    target_percentage: int = 100
    
    # Schedule
    start_percentage: int = 0
    increment: int = 10
    interval_minutes: int = 60
    
    # Status
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    paused: bool = False
    
    # Metrics
    error_threshold: float = 5.0  # Pause if error rate > 5%


@dataclass
class Experiment:
    """A/B эксперимент"""
    experiment_id: str
    name: str = ""
    description: str = ""
    
    # Hypothesis
    hypothesis: str = ""
    
    # Variations
    control_variation: str = ""
    treatment_variations: List[str] = field(default_factory=list)
    
    # Traffic allocation
    traffic_percentage: int = 100
    variation_weights: Dict[str, int] = field(default_factory=dict)
    
    # Metrics
    primary_metric: str = ""
    secondary_metrics: List[str] = field(default_factory=list)
    
    # Status
    status: ExperimentStatus = ExperimentStatus.DRAFT
    
    # Timing
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    
    # Results
    results: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FlagEvaluation:
    """Результат вычисления флага"""
    flag_key: str
    variation: str = ""
    value: Any = None
    
    # Reason
    reason: str = ""  # targeting, rollout, default, etc.
    rule_id: str = ""
    
    # Context
    user_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AuditEvent:
    """Событие аудита"""
    event_id: str
    action: str = ""
    
    # Target
    flag_key: str = ""
    
    # Changes
    changes: Dict[str, Any] = field(default_factory=dict)
    
    # Actor
    actor: str = ""
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)


class TargetingEngine:
    """Движок таргетирования"""
    
    def evaluate_rules(self, user: UserContext,
                        rules: List[TargetingRule]) -> Optional[str]:
        """Оценка правил таргетирования"""
        for rule in rules:
            if self._evaluate_conditions(user, rule.conditions):
                # Check percentage
                if rule.percentage < 100:
                    if not self._is_in_percentage(user.user_id, rule.percentage):
                        continue
                return rule.variation
        return None
        
    def _evaluate_conditions(self, user: UserContext,
                              conditions: List[Dict[str, Any]]) -> bool:
        """Оценка условий"""
        for condition in conditions:
            attribute = condition.get("attribute")
            operator = condition.get("operator")
            value = condition.get("value")
            
            user_value = self._get_user_value(user, attribute)
            
            if not self._evaluate_operator(user_value, operator, value):
                return False
                
        return True
        
    def _get_user_value(self, user: UserContext, attribute: str) -> Any:
        """Получение значения атрибута пользователя"""
        if attribute == "user_id":
            return user.user_id
        elif attribute == "country":
            return user.country
        elif attribute == "platform":
            return user.platform
        elif attribute == "device_type":
            return user.device_type
        elif attribute in user.attributes:
            return user.attributes[attribute]
        return None
        
    def _evaluate_operator(self, user_value: Any, operator: str,
                            condition_value: Any) -> bool:
        """Оценка оператора"""
        if operator == "equals":
            return user_value == condition_value
        elif operator == "not_equals":
            return user_value != condition_value
        elif operator == "contains":
            return condition_value in str(user_value)
        elif operator == "in":
            return user_value in condition_value
        elif operator == "not_in":
            return user_value not in condition_value
        elif operator == "greater_than":
            return user_value > condition_value
        elif operator == "less_than":
            return user_value < condition_value
        elif operator == "matches_segment":
            return condition_value in getattr(user, 'segments', [])
        return False
        
    def _is_in_percentage(self, user_id: str, percentage: int) -> bool:
        """Проверка попадания в процент"""
        hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        bucket = hash_value % 100
        return bucket < percentage


class RolloutManager:
    """Менеджер выкаток"""
    
    def __init__(self):
        self.rollouts: Dict[str, GradualRollout] = {}
        
    def create_rollout(self, flag_key: str, target_percentage: int,
                        increment: int = 10, interval_minutes: int = 60) -> GradualRollout:
        """Создание постепенной выкатки"""
        rollout = GradualRollout(
            rollout_id=f"rollout_{uuid.uuid4().hex[:8]}",
            flag_key=flag_key,
            target_percentage=target_percentage,
            increment=increment,
            interval_minutes=interval_minutes,
            started_at=datetime.now()
        )
        self.rollouts[rollout.rollout_id] = rollout
        return rollout
        
    async def advance_rollout(self, rollout_id: str,
                               error_rate: float = 0.0) -> Tuple[int, bool]:
        """Продвижение выкатки"""
        rollout = self.rollouts.get(rollout_id)
        if not rollout or rollout.paused:
            return 0, False
            
        # Check error threshold
        if error_rate > rollout.error_threshold:
            rollout.paused = True
            return rollout.current_percentage, False
            
        # Advance percentage
        new_percentage = min(
            rollout.current_percentage + rollout.increment,
            rollout.target_percentage
        )
        rollout.current_percentage = new_percentage
        
        # Check completion
        if new_percentage >= rollout.target_percentage:
            rollout.completed_at = datetime.now()
            return new_percentage, True
            
        return new_percentage, False


class ExperimentEngine:
    """Движок экспериментов"""
    
    def __init__(self):
        self.experiments: Dict[str, Experiment] = {}
        self.assignments: Dict[str, Dict[str, str]] = defaultdict(dict)
        
    def create_experiment(self, name: str, flag_key: str,
                           control: str, treatments: List[str],
                           **kwargs) -> Experiment:
        """Создание эксперимента"""
        experiment = Experiment(
            experiment_id=f"exp_{uuid.uuid4().hex[:8]}",
            name=name,
            control_variation=control,
            treatment_variations=treatments,
            **kwargs
        )
        
        # Default weights
        total_variations = 1 + len(treatments)
        weight = 100 // total_variations
        experiment.variation_weights[control] = weight
        for treatment in treatments:
            experiment.variation_weights[treatment] = weight
            
        self.experiments[experiment.experiment_id] = experiment
        return experiment
        
    def assign_variation(self, experiment_id: str, user_id: str) -> str:
        """Назначение вариации"""
        experiment = self.experiments.get(experiment_id)
        if not experiment or experiment.status != ExperimentStatus.RUNNING:
            return experiment.control_variation if experiment else ""
            
        # Check existing assignment
        if user_id in self.assignments[experiment_id]:
            return self.assignments[experiment_id][user_id]
            
        # Check traffic percentage
        hash_val = int(hashlib.md5(f"{experiment_id}:{user_id}".encode()).hexdigest(), 16)
        if (hash_val % 100) >= experiment.traffic_percentage:
            return experiment.control_variation
            
        # Assign based on weights
        bucket = hash_val % 100
        cumulative = 0
        
        for variation, weight in experiment.variation_weights.items():
            cumulative += weight
            if bucket < cumulative:
                self.assignments[experiment_id][user_id] = variation
                return variation
                
        return experiment.control_variation


class AnalyticsCollector:
    """Сборщик аналитики"""
    
    def __init__(self):
        self.evaluations: List[FlagEvaluation] = []
        self.events: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
    def record_evaluation(self, evaluation: FlagEvaluation) -> None:
        """Запись оценки"""
        self.evaluations.append(evaluation)
        
    def record_event(self, flag_key: str, event_name: str,
                      user_id: str, value: float = 1.0) -> None:
        """Запись события"""
        self.events[flag_key].append({
            "event_name": event_name,
            "user_id": user_id,
            "value": value,
            "timestamp": datetime.now().isoformat()
        })
        
    def get_flag_stats(self, flag_key: str) -> Dict[str, Any]:
        """Статистика по флагу"""
        flag_evals = [e for e in self.evaluations if e.flag_key == flag_key]
        
        variation_counts = defaultdict(int)
        for eval in flag_evals:
            variation_counts[eval.variation] += 1
            
        return {
            "total_evaluations": len(flag_evals),
            "unique_users": len(set(e.user_id for e in flag_evals)),
            "variation_distribution": dict(variation_counts),
            "events": len(self.events.get(flag_key, []))
        }


class FeatureFlagPlatform:
    """Платформа feature flags"""
    
    def __init__(self):
        self.flags: Dict[str, FeatureFlag] = {}
        
        self.targeting_engine = TargetingEngine()
        self.rollout_manager = RolloutManager()
        self.experiment_engine = ExperimentEngine()
        self.analytics = AnalyticsCollector()
        
        self.audit_log: List[AuditEvent] = []
        
    def create_flag(self, key: str, name: str,
                     flag_type: FlagType = FlagType.BOOLEAN,
                     variations: List[Dict[str, Any]] = None,
                     **kwargs) -> FeatureFlag:
        """Создание флага"""
        # Default variations for boolean
        if variations is None and flag_type == FlagType.BOOLEAN:
            variations = [
                {"name": "on", "value": True},
                {"name": "off", "value": False}
            ]
            
        flag = FeatureFlag(
            flag_id=f"flag_{uuid.uuid4().hex[:8]}",
            key=key,
            name=name,
            flag_type=flag_type,
            variations=[
                Variation(
                    variation_id=f"var_{uuid.uuid4().hex[:8]}",
                    name=v.get("name", ""),
                    value=v.get("value"),
                    description=v.get("description", "")
                )
                for v in (variations or [])
            ],
            **kwargs
        )
        
        if flag.variations:
            flag.default_variation = flag.variations[-1].name
            
        self.flags[key] = flag
        
        self._audit("create", key, {}, kwargs.get("created_by", "system"))
        return flag
        
    def update_flag(self, key: str, actor: str, **updates) -> FeatureFlag:
        """Обновление флага"""
        flag = self.flags.get(key)
        if not flag:
            raise ValueError(f"Flag {key} not found")
            
        changes = {}
        for attr, value in updates.items():
            if hasattr(flag, attr):
                old_value = getattr(flag, attr)
                setattr(flag, attr, value)
                changes[attr] = {"old": old_value, "new": value}
                
        flag.updated_at = datetime.now()
        
        self._audit("update", key, changes, actor)
        return flag
        
    def add_targeting_rule(self, flag_key: str, name: str,
                            conditions: List[Dict[str, Any]],
                            variation: str, percentage: int = 100) -> TargetingRule:
        """Добавление правила таргетирования"""
        flag = self.flags.get(flag_key)
        if not flag:
            raise ValueError(f"Flag {flag_key} not found")
            
        rule = TargetingRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name=name,
            conditions=conditions,
            variation=variation,
            percentage=percentage
        )
        flag.targeting_rules.append(rule)
        flag.updated_at = datetime.now()
        
        return rule
        
    def evaluate(self, flag_key: str, user: UserContext,
                  environment: EnvironmentType = EnvironmentType.PRODUCTION) -> FlagEvaluation:
        """Вычисление флага"""
        flag = self.flags.get(flag_key)
        
        evaluation = FlagEvaluation(
            flag_key=flag_key,
            user_id=user.user_id
        )
        
        if not flag:
            evaluation.reason = "flag_not_found"
            return evaluation
            
        # Check if enabled
        if not flag.enabled:
            evaluation.variation = flag.default_variation
            evaluation.value = self._get_variation_value(flag, flag.default_variation)
            evaluation.reason = "flag_disabled"
            self.analytics.record_evaluation(evaluation)
            return evaluation
            
        # Check environment settings
        env_settings = flag.environment_settings.get(environment.value, {})
        if env_settings.get("enabled") == False:
            evaluation.variation = flag.default_variation
            evaluation.value = self._get_variation_value(flag, flag.default_variation)
            evaluation.reason = "environment_disabled"
            self.analytics.record_evaluation(evaluation)
            return evaluation
            
        # Evaluate targeting rules
        targeted_variation = self.targeting_engine.evaluate_rules(
            user, flag.targeting_rules
        )
        
        if targeted_variation:
            evaluation.variation = targeted_variation
            evaluation.value = self._get_variation_value(flag, targeted_variation)
            evaluation.reason = "targeting_rule"
            self.analytics.record_evaluation(evaluation)
            return evaluation
            
        # Check rollout percentage
        if flag.rollout_percentage > 0:
            if self.targeting_engine._is_in_percentage(user.user_id, flag.rollout_percentage):
                # Return "on" variation
                on_variation = next(
                    (v.name for v in flag.variations if v.value == True),
                    flag.variations[0].name if flag.variations else ""
                )
                evaluation.variation = on_variation
                evaluation.value = self._get_variation_value(flag, on_variation)
                evaluation.reason = "rollout"
                self.analytics.record_evaluation(evaluation)
                return evaluation
                
        # Return default
        evaluation.variation = flag.default_variation
        evaluation.value = self._get_variation_value(flag, flag.default_variation)
        evaluation.reason = "default"
        self.analytics.record_evaluation(evaluation)
        
        return evaluation
        
    def _get_variation_value(self, flag: FeatureFlag, variation_name: str) -> Any:
        """Получение значения вариации"""
        for variation in flag.variations:
            if variation.name == variation_name:
                return variation.value
        return None
        
    def _audit(self, action: str, flag_key: str,
                changes: Dict[str, Any], actor: str) -> None:
        """Запись аудита"""
        event = AuditEvent(
            event_id=f"audit_{uuid.uuid4().hex[:8]}",
            action=action,
            flag_key=flag_key,
            changes=changes,
            actor=actor
        )
        self.audit_log.append(event)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        enabled_flags = sum(1 for f in self.flags.values() if f.enabled)
        
        return {
            "total_flags": len(self.flags),
            "enabled_flags": enabled_flags,
            "disabled_flags": len(self.flags) - enabled_flags,
            "experiments": len(self.experiment_engine.experiments),
            "rollouts": len(self.rollout_manager.rollouts),
            "total_evaluations": len(self.analytics.evaluations),
            "audit_events": len(self.audit_log)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 102: Feature Flag Platform")
    print("=" * 60)
    
    async def demo():
        platform = FeatureFlagPlatform()
        print("✓ Feature Flag Platform created")
        
        # Create feature flags
        print("\n🚩 Creating Feature Flags...")
        
        # Boolean flag
        flag1 = platform.create_flag(
            "new_checkout_flow",
            "New Checkout Flow",
            flag_type=FlagType.BOOLEAN,
            description="Enable new streamlined checkout experience",
            tags=["checkout", "ux"],
            created_by="product-team"
        )
        print(f"  ✓ {flag1.key} (boolean)")
        
        # Enable and set rollout
        platform.update_flag(
            "new_checkout_flow",
            actor="product-team",
            enabled=True,
            rollout_percentage=25
        )
        
        # String flag
        flag2 = platform.create_flag(
            "payment_provider",
            "Payment Provider",
            flag_type=FlagType.STRING,
            variations=[
                {"name": "stripe", "value": "stripe"},
                {"name": "paypal", "value": "paypal"},
                {"name": "square", "value": "square"}
            ],
            description="Select payment provider",
            created_by="payments-team"
        )
        platform.update_flag("payment_provider", actor="payments-team", enabled=True)
        print(f"  ✓ {flag2.key} (string)")
        
        # Number flag
        flag3 = platform.create_flag(
            "max_items_in_cart",
            "Max Items in Cart",
            flag_type=FlagType.NUMBER,
            variations=[
                {"name": "default", "value": 10},
                {"name": "premium", "value": 50},
                {"name": "unlimited", "value": 999}
            ],
            description="Maximum items allowed in cart",
            created_by="ecommerce-team"
        )
        platform.update_flag("max_items_in_cart", actor="ecommerce-team", enabled=True)
        print(f"  ✓ {flag3.key} (number)")
        
        # JSON flag
        flag4 = platform.create_flag(
            "homepage_config",
            "Homepage Configuration",
            flag_type=FlagType.JSON,
            variations=[
                {"name": "control", "value": {"hero": "classic", "products": 8}},
                {"name": "variant_a", "value": {"hero": "video", "products": 12}},
                {"name": "variant_b", "value": {"hero": "carousel", "products": 6}}
            ],
            description="Homepage layout configuration",
            created_by="ux-team"
        )
        platform.update_flag("homepage_config", actor="ux-team", enabled=True)
        print(f"  ✓ {flag4.key} (json)")
        
        # Add targeting rules
        print("\n🎯 Adding Targeting Rules...")
        
        # Beta users rule
        platform.add_targeting_rule(
            "new_checkout_flow",
            "Beta Users",
            conditions=[
                {"attribute": "segments", "operator": "matches_segment", "value": "beta"}
            ],
            variation="on",
            percentage=100
        )
        print("  ✓ Beta users → new_checkout_flow: ON")
        
        # Country-based rule
        platform.add_targeting_rule(
            "payment_provider",
            "US Users",
            conditions=[
                {"attribute": "country", "operator": "equals", "value": "US"}
            ],
            variation="stripe"
        )
        
        platform.add_targeting_rule(
            "payment_provider",
            "EU Users",
            conditions=[
                {"attribute": "country", "operator": "in", "value": ["DE", "FR", "UK", "ES"]}
            ],
            variation="paypal"
        )
        print("  ✓ US users → stripe, EU users → paypal")
        
        # Premium users rule
        platform.add_targeting_rule(
            "max_items_in_cart",
            "Premium Users",
            conditions=[
                {"attribute": "plan", "operator": "equals", "value": "premium"}
            ],
            variation="premium"
        )
        print("  ✓ Premium users → 50 items limit")
        
        # Create gradual rollout
        print("\n📈 Creating Gradual Rollout...")
        
        rollout = platform.rollout_manager.create_rollout(
            "new_checkout_flow",
            target_percentage=100,
            increment=10,
            interval_minutes=30
        )
        print(f"  ✓ Rollout: {rollout.rollout_id}")
        print(f"    Target: {rollout.target_percentage}%")
        print(f"    Increment: {rollout.increment}% every {rollout.interval_minutes}min")
        
        # Simulate rollout advancement
        for i in range(3):
            new_pct, completed = await platform.rollout_manager.advance_rollout(
                rollout.rollout_id,
                error_rate=random.uniform(0, 3)
            )
            print(f"    Advanced to {new_pct}%")
            
        # Create A/B experiment
        print("\n🧪 Creating A/B Experiment...")
        
        experiment = platform.experiment_engine.create_experiment(
            "Homepage Hero Test",
            "homepage_config",
            control="control",
            treatments=["variant_a", "variant_b"],
            hypothesis="Video hero will increase engagement by 15%",
            primary_metric="click_through_rate",
            secondary_metrics=["time_on_page", "bounce_rate"],
            traffic_percentage=50
        )
        experiment.status = ExperimentStatus.RUNNING
        experiment.started_at = datetime.now()
        
        print(f"  ✓ Experiment: {experiment.name}")
        print(f"    Hypothesis: {experiment.hypothesis}")
        print(f"    Variations: control vs {experiment.treatment_variations}")
        print(f"    Traffic: {experiment.traffic_percentage}%")
        
        # Evaluate flags for different users
        print("\n👥 Evaluating Flags for Users...")
        
        test_users = [
            UserContext(
                user_id="user_001",
                attributes={"plan": "free"},
                segments=["beta"],
                country="US",
                platform="web"
            ),
            UserContext(
                user_id="user_002",
                attributes={"plan": "premium"},
                country="DE",
                platform="mobile"
            ),
            UserContext(
                user_id="user_003",
                attributes={"plan": "free"},
                country="US",
                platform="web"
            ),
            UserContext(
                user_id="user_004",
                attributes={"plan": "free"},
                segments=[],
                country="JP",
                platform="mobile"
            )
        ]
        
        print("\n  Evaluation Results:")
        
        for user in test_users:
            print(f"\n  User: {user.user_id} ({user.country}, {user.attributes.get('plan', 'free')})")
            
            for flag_key in ["new_checkout_flow", "payment_provider", "max_items_in_cart"]:
                result = platform.evaluate(flag_key, user)
                print(f"    {flag_key}: {result.value} ({result.reason})")
                
        # Bulk evaluation simulation
        print("\n  Bulk Evaluation (1000 users):")
        
        for i in range(1000):
            user = UserContext(
                user_id=f"user_{1000+i}",
                attributes={"plan": random.choice(["free", "premium"])},
                country=random.choice(["US", "DE", "UK", "JP", "FR"]),
                platform=random.choice(["web", "mobile", "tablet"])
            )
            
            for flag_key in platform.flags:
                platform.evaluate(flag_key, user)
                
        print("  ✓ 1000 users evaluated for all flags")
        
        # Analytics
        print("\n📊 Flag Analytics:")
        
        for flag_key in platform.flags:
            stats = platform.analytics.get_flag_stats(flag_key)
            print(f"\n  {flag_key}:")
            print(f"    Evaluations: {stats['total_evaluations']}")
            print(f"    Unique users: {stats['unique_users']}")
            print(f"    Distribution: {stats['variation_distribution']}")
            
        # Experiment assignments
        print("\n🔬 Experiment Assignments:")
        
        assignment_counts = defaultdict(int)
        for i in range(100):
            variation = platform.experiment_engine.assign_variation(
                experiment.experiment_id,
                f"exp_user_{i}"
            )
            assignment_counts[variation] += 1
            
        print(f"  {experiment.name}:")
        for variation, count in assignment_counts.items():
            print(f"    {variation}: {count}%")
            
        # Audit log
        print("\n📝 Audit Log (Recent):")
        
        for event in platform.audit_log[-5:]:
            print(f"  [{event.timestamp.strftime('%H:%M:%S')}] {event.action}: {event.flag_key}")
            if event.changes:
                for key, change in list(event.changes.items())[:2]:
                    print(f"    {key}: {change.get('old')} → {change.get('new')}")
                    
        # Statistics
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Flags: {stats['total_flags']}")
        print(f"  Enabled: {stats['enabled_flags']}")
        print(f"  Disabled: {stats['disabled_flags']}")
        print(f"  Experiments: {stats['experiments']}")
        print(f"  Active Rollouts: {stats['rollouts']}")
        print(f"  Total Evaluations: {stats['total_evaluations']}")
        print(f"  Audit Events: {stats['audit_events']}")
        
        # Dashboard
        print("\n📋 Feature Flag Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │               Feature Flag Overview                         │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Flags:    {stats['total_flags']:>6}                                │")
        print(f"  │ Enabled:        {stats['enabled_flags']:>6}                                │")
        print(f"  │ Disabled:       {stats['disabled_flags']:>6}                                │")
        print(f"  │ Experiments:    {stats['experiments']:>6}                                │")
        print(f"  │ Rollouts:       {stats['rollouts']:>6}                                │")
        print(f"  │ Evaluations:    {stats['total_evaluations']:>6}                                │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Feature Flag Platform initialized!")
    print("=" * 60)
