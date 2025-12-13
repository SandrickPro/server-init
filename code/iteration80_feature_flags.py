#!/usr/bin/env python3
"""
Server Init - Iteration 80: Feature Flags & Toggles
Система Feature Flags и Feature Toggles

Функционал:
- Flag Management - управление флагами
- Targeting Rules - правила таргетинга
- Gradual Rollout - постепенный rollout
- User Segmentation - сегментация пользователей
- Flag Scheduling - планирование флагов
- Environment Support - поддержка окружений
- A/B Testing - A/B тестирование
- Analytics & Insights - аналитика
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
from collections import defaultdict
import uuid
import hashlib
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


class RolloutStrategy(Enum):
    """Стратегия раскатки"""
    ALL_USERS = "all_users"
    PERCENTAGE = "percentage"
    USER_LIST = "user_list"
    SEGMENT = "segment"
    GRADUAL = "gradual"


class TargetOperator(Enum):
    """Оператор таргетинга"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IN_LIST = "in_list"
    NOT_IN_LIST = "not_in_list"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    MATCHES_REGEX = "matches_regex"


@dataclass
class TargetCondition:
    """Условие таргетинга"""
    attribute: str  # user.country, user.plan, etc.
    operator: TargetOperator = TargetOperator.EQUALS
    value: Any = None
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Оценка условия"""
        # Получаем значение атрибута из контекста
        attr_value = self._get_nested_value(context, self.attribute)
        
        if self.operator == TargetOperator.EQUALS:
            return attr_value == self.value
        elif self.operator == TargetOperator.NOT_EQUALS:
            return attr_value != self.value
        elif self.operator == TargetOperator.CONTAINS:
            return self.value in str(attr_value) if attr_value else False
        elif self.operator == TargetOperator.STARTS_WITH:
            return str(attr_value).startswith(str(self.value)) if attr_value else False
        elif self.operator == TargetOperator.ENDS_WITH:
            return str(attr_value).endswith(str(self.value)) if attr_value else False
        elif self.operator == TargetOperator.IN_LIST:
            return attr_value in self.value if isinstance(self.value, list) else False
        elif self.operator == TargetOperator.NOT_IN_LIST:
            return attr_value not in self.value if isinstance(self.value, list) else True
        elif self.operator == TargetOperator.GREATER_THAN:
            return float(attr_value) > float(self.value) if attr_value else False
        elif self.operator == TargetOperator.LESS_THAN:
            return float(attr_value) < float(self.value) if attr_value else False
            
        return False
        
    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """Получение вложенного значения"""
        keys = path.split(".")
        value = data
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
                
        return value


@dataclass
class TargetRule:
    """Правило таргетинга"""
    rule_id: str
    name: str = ""
    
    # Условия (AND)
    conditions: List[TargetCondition] = field(default_factory=list)
    
    # Значение при совпадении
    variation: Any = None
    
    # Приоритет
    priority: int = 0
    
    # Статус
    enabled: bool = True
    
    def evaluate(self, context: Dict[str, Any]) -> Optional[Any]:
        """Оценка правила"""
        if not self.enabled:
            return None
            
        # Все условия должны выполниться (AND)
        for condition in self.conditions:
            if not condition.evaluate(context):
                return None
                
        return self.variation


@dataclass
class UserSegment:
    """Сегмент пользователей"""
    segment_id: str
    name: str = ""
    description: str = ""
    
    # Условия попадания в сегмент
    conditions: List[TargetCondition] = field(default_factory=list)
    
    # Тип соединения условий
    match_type: str = "all"  # all, any
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    
    def matches(self, context: Dict[str, Any]) -> bool:
        """Проверка соответствия"""
        if not self.conditions:
            return True
            
        if self.match_type == "all":
            return all(c.evaluate(context) for c in self.conditions)
        else:  # any
            return any(c.evaluate(context) for c in self.conditions)


@dataclass
class Variation:
    """Вариация флага"""
    variation_id: str
    name: str = ""
    value: Any = None
    weight: int = 100  # Вес для процентного распределения


@dataclass
class Schedule:
    """Расписание флага"""
    schedule_id: str
    
    # Время активации
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # Дни недели (0-6, 0=понедельник)
    days_of_week: List[int] = field(default_factory=list)
    
    # Часы активности
    active_hours_start: int = 0  # 0-23
    active_hours_end: int = 24
    
    # Timezone
    timezone: str = "UTC"
    
    def is_active(self, now: datetime = None) -> bool:
        """Проверка активности"""
        now = now or datetime.now()
        
        if self.start_time and now < self.start_time:
            return False
            
        if self.end_time and now > self.end_time:
            return False
            
        if self.days_of_week:
            if now.weekday() not in self.days_of_week:
                return False
                
        if self.active_hours_start <= now.hour < self.active_hours_end:
            return True
        elif self.active_hours_start > self.active_hours_end:
            # Ночной диапазон (например 22-6)
            return now.hour >= self.active_hours_start or now.hour < self.active_hours_end
        else:
            return False
            
        return True


@dataclass
class FeatureFlag:
    """Feature Flag"""
    flag_id: str
    key: str  # Уникальный ключ флага
    name: str = ""
    description: str = ""
    
    # Тип и значения
    flag_type: FlagType = FlagType.BOOLEAN
    default_value: Any = False
    
    # Вариации
    variations: List[Variation] = field(default_factory=list)
    
    # Статус
    status: FlagStatus = FlagStatus.INACTIVE
    
    # Правила таргетинга
    targeting_rules: List[TargetRule] = field(default_factory=list)
    
    # Стратегия раскатки
    rollout_strategy: RolloutStrategy = RolloutStrategy.ALL_USERS
    rollout_percentage: int = 100
    
    # Расписание
    schedule: Optional[Schedule] = None
    
    # Окружения
    environments: List[str] = field(default_factory=lambda: ["development", "staging", "production"])
    environment_overrides: Dict[str, Any] = field(default_factory=dict)
    
    # Метаданные
    tags: List[str] = field(default_factory=list)
    owner: str = ""
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class FlagEvaluation:
    """Результат оценки флага"""
    flag_key: str
    value: Any
    
    # Причина
    reason: str = ""  # default, targeting_rule, percentage, etc.
    rule_id: str = ""
    
    # Контекст
    user_id: str = ""
    
    # Время
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class FlagAnalytics:
    """Аналитика флага"""
    flag_id: str
    
    # Оценки
    total_evaluations: int = 0
    true_count: int = 0
    false_count: int = 0
    
    # По вариациям
    variation_counts: Dict[str, int] = field(default_factory=dict)
    
    # По сегментам
    segment_counts: Dict[str, int] = field(default_factory=dict)
    
    # По времени
    hourly_counts: Dict[int, int] = field(default_factory=dict)


class FlagEvaluator:
    """Оценка флагов"""
    
    def __init__(self):
        self.flags: Dict[str, FeatureFlag] = {}
        self.segments: Dict[str, UserSegment] = {}
        self.analytics: Dict[str, FlagAnalytics] = {}
        self.evaluation_log: List[FlagEvaluation] = []
        
    def add_flag(self, flag: FeatureFlag):
        """Добавление флага"""
        self.flags[flag.key] = flag
        self.analytics[flag.flag_id] = FlagAnalytics(flag_id=flag.flag_id)
        
    def add_segment(self, segment: UserSegment):
        """Добавление сегмента"""
        self.segments[segment.segment_id] = segment
        
    def evaluate(self, flag_key: str, context: Dict[str, Any] = None,
                  environment: str = "production") -> FlagEvaluation:
        """Оценка флага"""
        context = context or {}
        user_id = context.get("user", {}).get("id", "anonymous")
        
        flag = self.flags.get(flag_key)
        if not flag:
            return FlagEvaluation(
                flag_key=flag_key,
                value=None,
                reason="flag_not_found",
                user_id=user_id
            )
            
        evaluation = FlagEvaluation(flag_key=flag_key, user_id=user_id)
        
        # Проверяем статус
        if flag.status != FlagStatus.ACTIVE:
            evaluation.value = flag.default_value
            evaluation.reason = "flag_inactive"
            self._record_evaluation(flag, evaluation)
            return evaluation
            
        # Проверяем расписание
        if flag.schedule and not flag.schedule.is_active():
            evaluation.value = flag.default_value
            evaluation.reason = "schedule_inactive"
            self._record_evaluation(flag, evaluation)
            return evaluation
            
        # Проверяем environment override
        if environment in flag.environment_overrides:
            evaluation.value = flag.environment_overrides[environment]
            evaluation.reason = "environment_override"
            self._record_evaluation(flag, evaluation)
            return evaluation
            
        # Проверяем правила таргетинга
        sorted_rules = sorted(flag.targeting_rules, key=lambda r: -r.priority)
        for rule in sorted_rules:
            result = rule.evaluate(context)
            if result is not None:
                evaluation.value = result
                evaluation.reason = "targeting_rule"
                evaluation.rule_id = rule.rule_id
                self._record_evaluation(flag, evaluation)
                return evaluation
                
        # Применяем стратегию раскатки
        if flag.rollout_strategy == RolloutStrategy.PERCENTAGE:
            if self._is_in_percentage(user_id, flag_key, flag.rollout_percentage):
                evaluation.value = self._get_variation(flag, user_id)
                evaluation.reason = "percentage_rollout"
            else:
                evaluation.value = flag.default_value
                evaluation.reason = "percentage_excluded"
                
        elif flag.rollout_strategy == RolloutStrategy.ALL_USERS:
            evaluation.value = self._get_variation(flag, user_id)
            evaluation.reason = "all_users"
            
        else:
            evaluation.value = flag.default_value
            evaluation.reason = "default"
            
        self._record_evaluation(flag, evaluation)
        return evaluation
        
    def _is_in_percentage(self, user_id: str, flag_key: str, percentage: int) -> bool:
        """Проверка попадания в процент"""
        hash_key = f"{user_id}:{flag_key}"
        hash_value = int(hashlib.md5(hash_key.encode()).hexdigest(), 16)
        bucket = hash_value % 100
        return bucket < percentage
        
    def _get_variation(self, flag: FeatureFlag, user_id: str) -> Any:
        """Получение вариации"""
        if not flag.variations:
            return flag.default_value
            
        # Детерминированный выбор на основе user_id
        hash_key = f"{user_id}:{flag.key}:variation"
        hash_value = int(hashlib.md5(hash_key.encode()).hexdigest(), 16)
        
        total_weight = sum(v.weight for v in flag.variations)
        bucket = hash_value % total_weight
        
        cumulative = 0
        for variation in flag.variations:
            cumulative += variation.weight
            if bucket < cumulative:
                return variation.value
                
        return flag.variations[0].value
        
    def _record_evaluation(self, flag: FeatureFlag, evaluation: FlagEvaluation):
        """Запись оценки"""
        self.evaluation_log.append(evaluation)
        
        analytics = self.analytics.get(flag.flag_id)
        if analytics:
            analytics.total_evaluations += 1
            
            if evaluation.value == True:
                analytics.true_count += 1
            elif evaluation.value == False:
                analytics.false_count += 1
                
            # По вариациям
            var_key = str(evaluation.value)
            analytics.variation_counts[var_key] = analytics.variation_counts.get(var_key, 0) + 1
            
            # По времени
            hour = evaluation.timestamp.hour
            analytics.hourly_counts[hour] = analytics.hourly_counts.get(hour, 0) + 1


class FeatureFlagPlatform:
    """Платформа Feature Flags"""
    
    def __init__(self):
        self.evaluator = FlagEvaluator()
        
    def create_flag(self, key: str, name: str = None, **kwargs) -> FeatureFlag:
        """Создание флага"""
        flag = FeatureFlag(
            flag_id=f"flag_{uuid.uuid4().hex[:8]}",
            key=key,
            name=name or key,
            **kwargs
        )
        self.evaluator.add_flag(flag)
        return flag
        
    def create_segment(self, name: str, **kwargs) -> UserSegment:
        """Создание сегмента"""
        segment = UserSegment(
            segment_id=f"seg_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        self.evaluator.add_segment(segment)
        return segment
        
    def get_flag(self, key: str, context: Dict[str, Any] = None,
                  environment: str = "production") -> Any:
        """Получение значения флага"""
        evaluation = self.evaluator.evaluate(key, context, environment)
        return evaluation.value
        
    def get_flag_details(self, key: str, context: Dict[str, Any] = None,
                          environment: str = "production") -> FlagEvaluation:
        """Получение деталей оценки"""
        return self.evaluator.evaluate(key, context, environment)
        
    def enable_flag(self, key: str):
        """Включение флага"""
        flag = self.evaluator.flags.get(key)
        if flag:
            flag.status = FlagStatus.ACTIVE
            flag.updated_at = datetime.now()
            
    def disable_flag(self, key: str):
        """Выключение флага"""
        flag = self.evaluator.flags.get(key)
        if flag:
            flag.status = FlagStatus.INACTIVE
            flag.updated_at = datetime.now()
            
    def set_rollout_percentage(self, key: str, percentage: int):
        """Установка процента раскатки"""
        flag = self.evaluator.flags.get(key)
        if flag:
            flag.rollout_percentage = max(0, min(100, percentage))
            flag.rollout_strategy = RolloutStrategy.PERCENTAGE
            flag.updated_at = datetime.now()
            
    def add_targeting_rule(self, flag_key: str, rule: TargetRule):
        """Добавление правила таргетинга"""
        flag = self.evaluator.flags.get(flag_key)
        if flag:
            flag.targeting_rules.append(rule)
            flag.updated_at = datetime.now()
            
    def get_analytics(self, flag_key: str) -> Optional[FlagAnalytics]:
        """Получение аналитики"""
        flag = self.evaluator.flags.get(flag_key)
        if flag:
            return self.evaluator.analytics.get(flag.flag_id)
        return None
        
    def get_stats(self) -> Dict[str, Any]:
        """Статистика платформы"""
        active_flags = len([f for f in self.evaluator.flags.values() 
                           if f.status == FlagStatus.ACTIVE])
        total_evaluations = sum(a.total_evaluations 
                               for a in self.evaluator.analytics.values())
        
        return {
            "total_flags": len(self.evaluator.flags),
            "active_flags": active_flags,
            "segments": len(self.evaluator.segments),
            "total_evaluations": total_evaluations
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 80: Feature Flags & Toggles")
    print("=" * 60)
    
    async def demo():
        platform = FeatureFlagPlatform()
        print("✓ Feature Flag Platform created")
        
        # Создание простого boolean флага
        print("\n🚩 Creating Feature Flags...")
        
        new_ui = platform.create_flag(
            key="new-dashboard-ui",
            name="New Dashboard UI",
            description="Enable the new dashboard user interface",
            flag_type=FlagType.BOOLEAN,
            default_value=False,
            tags=["ui", "dashboard", "frontend"],
            owner="frontend-team"
        )
        print(f"  ✓ Flag: {new_ui.name}")
        print(f"    Key: {new_ui.key}")
        print(f"    Default: {new_ui.default_value}")
        
        # Флаг с вариациями
        payment_flow = platform.create_flag(
            key="checkout-flow",
            name="Checkout Flow",
            description="A/B test different checkout flows",
            flag_type=FlagType.STRING,
            default_value="classic",
            variations=[
                Variation(variation_id="v1", name="Classic", value="classic", weight=50),
                Variation(variation_id="v2", name="Streamlined", value="streamlined", weight=30),
                Variation(variation_id="v3", name="One-Click", value="one_click", weight=20),
            ],
            tags=["checkout", "payment", "ab-test"],
            owner="payments-team"
        )
        print(f"  ✓ Flag: {payment_flow.name}")
        print(f"    Variations: {[v.name for v in payment_flow.variations]}")
        
        # Флаг с числовым значением
        rate_limit = platform.create_flag(
            key="api-rate-limit",
            name="API Rate Limit",
            description="Rate limit per minute for API calls",
            flag_type=FlagType.NUMBER,
            default_value=100,
            tags=["api", "rate-limit", "backend"],
            owner="platform-team"
        )
        print(f"  ✓ Flag: {rate_limit.name}")
        print(f"    Default: {rate_limit.default_value} req/min")
        
        # JSON флаг для конфигурации
        feature_config = platform.create_flag(
            key="feature-config",
            name="Feature Configuration",
            description="Dynamic feature configuration",
            flag_type=FlagType.JSON,
            default_value={"max_items": 10, "cache_ttl": 300, "debug": False},
            tags=["config"],
            owner="platform-team"
        )
        print(f"  ✓ Flag: {feature_config.name}")
        
        # Создание сегментов
        print("\n👥 Creating User Segments...")
        
        beta_users = platform.create_segment(
            "Beta Users",
            description="Users in beta program",
            conditions=[
                TargetCondition(attribute="user.beta", operator=TargetOperator.EQUALS, value=True)
            ]
        )
        print(f"  ✓ Segment: {beta_users.name}")
        
        premium_users = platform.create_segment(
            "Premium Users",
            description="Users with premium subscription",
            conditions=[
                TargetCondition(attribute="user.plan", operator=TargetOperator.IN_LIST, 
                               value=["premium", "enterprise"])
            ]
        )
        print(f"  ✓ Segment: {premium_users.name}")
        
        us_users = platform.create_segment(
            "US Users",
            description="Users from United States",
            conditions=[
                TargetCondition(attribute="user.country", operator=TargetOperator.EQUALS, value="US")
            ]
        )
        print(f"  ✓ Segment: {us_users.name}")
        
        # Добавление правил таргетинга
        print("\n🎯 Adding Targeting Rules...")
        
        # Правило для beta пользователей
        beta_rule = TargetRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name="Beta Users Get New UI",
            conditions=[
                TargetCondition(attribute="user.beta", operator=TargetOperator.EQUALS, value=True)
            ],
            variation=True,
            priority=100
        )
        platform.add_targeting_rule("new-dashboard-ui", beta_rule)
        print(f"  ✓ Rule: {beta_rule.name}")
        
        # Правило для premium пользователей
        premium_rule = TargetRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name="Premium Users Higher Rate Limit",
            conditions=[
                TargetCondition(attribute="user.plan", operator=TargetOperator.IN_LIST,
                               value=["premium", "enterprise"])
            ],
            variation=1000,
            priority=100
        )
        platform.add_targeting_rule("api-rate-limit", premium_rule)
        print(f"  ✓ Rule: {premium_rule.name}")
        
        # Правило по стране
        us_checkout_rule = TargetRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name="US Users One-Click Checkout",
            conditions=[
                TargetCondition(attribute="user.country", operator=TargetOperator.EQUALS, value="US"),
                TargetCondition(attribute="user.purchases", operator=TargetOperator.GREATER_THAN, value=5)
            ],
            variation="one_click",
            priority=90
        )
        platform.add_targeting_rule("checkout-flow", us_checkout_rule)
        print(f"  ✓ Rule: {us_checkout_rule.name}")
        
        # Включение флагов
        print("\n✅ Enabling Flags...")
        
        platform.enable_flag("new-dashboard-ui")
        platform.set_rollout_percentage("new-dashboard-ui", 20)  # 20% rollout
        print(f"  ✓ new-dashboard-ui: 20% rollout")
        
        platform.enable_flag("checkout-flow")
        print(f"  ✓ checkout-flow: enabled")
        
        platform.enable_flag("api-rate-limit")
        print(f"  ✓ api-rate-limit: enabled")
        
        platform.enable_flag("feature-config")
        print(f"  ✓ feature-config: enabled")
        
        # Оценка флагов для разных пользователей
        print("\n🔍 Evaluating Flags...")
        
        test_users = [
            {
                "user": {"id": "user_001", "beta": True, "plan": "free", "country": "US", "purchases": 3},
                "device": {"type": "mobile", "os": "ios"}
            },
            {
                "user": {"id": "user_002", "beta": False, "plan": "premium", "country": "UK", "purchases": 10},
                "device": {"type": "desktop", "os": "windows"}
            },
            {
                "user": {"id": "user_003", "beta": False, "plan": "enterprise", "country": "US", "purchases": 50},
                "device": {"type": "desktop", "os": "macos"}
            },
            {
                "user": {"id": "user_004", "beta": False, "plan": "free", "country": "DE", "purchases": 1},
                "device": {"type": "mobile", "os": "android"}
            },
        ]
        
        for user_context in test_users:
            user_id = user_context["user"]["id"]
            plan = user_context["user"]["plan"]
            beta = user_context["user"]["beta"]
            
            print(f"\n  User: {user_id} (plan={plan}, beta={beta})")
            
            # Оценка каждого флага
            for flag_key in ["new-dashboard-ui", "checkout-flow", "api-rate-limit", "feature-config"]:
                evaluation = platform.get_flag_details(flag_key, user_context)
                value_str = str(evaluation.value)
                if len(value_str) > 30:
                    value_str = value_str[:30] + "..."
                print(f"    {flag_key}: {value_str}")
                print(f"      Reason: {evaluation.reason}")
                
        # Симуляция множества оценок
        print("\n📊 Simulating Evaluations...")
        
        for _ in range(100):
            for user_context in test_users:
                platform.get_flag("new-dashboard-ui", user_context)
                platform.get_flag("checkout-flow", user_context)
                
        # Аналитика
        print("\n📈 Flag Analytics...")
        
        for flag_key in ["new-dashboard-ui", "checkout-flow"]:
            analytics = platform.get_analytics(flag_key)
            if analytics:
                flag = platform.evaluator.flags.get(flag_key)
                print(f"\n  {flag.name}:")
                print(f"    Total evaluations: {analytics.total_evaluations}")
                
                if flag.flag_type == FlagType.BOOLEAN:
                    true_pct = (analytics.true_count / analytics.total_evaluations * 100) if analytics.total_evaluations > 0 else 0
                    print(f"    True: {analytics.true_count} ({true_pct:.1f}%)")
                    print(f"    False: {analytics.false_count} ({100-true_pct:.1f}%)")
                else:
                    print(f"    Variations:")
                    for var, count in analytics.variation_counts.items():
                        pct = count / analytics.total_evaluations * 100 if analytics.total_evaluations > 0 else 0
                        print(f"      {var}: {count} ({pct:.1f}%)")
                        
        # Gradual Rollout демонстрация
        print("\n🚀 Gradual Rollout Demo...")
        
        rollout_flag = platform.create_flag(
            key="gradual-feature",
            name="Gradual Feature",
            description="Feature with gradual rollout",
            default_value=False,
            rollout_strategy=RolloutStrategy.PERCENTAGE,
            rollout_percentage=0
        )
        platform.enable_flag("gradual-feature")
        
        rollout_stages = [10, 25, 50, 75, 100]
        
        for stage in rollout_stages:
            platform.set_rollout_percentage("gradual-feature", stage)
            
            # Тестируем на 100 пользователях
            enabled_count = 0
            for i in range(100):
                context = {"user": {"id": f"test_user_{i}"}}
                if platform.get_flag("gradual-feature", context):
                    enabled_count += 1
                    
            print(f"  {stage}% rollout: ~{enabled_count}% of users enabled")
            
        # Scheduled flag
        print("\n⏰ Scheduled Flag Example...")
        
        scheduled_flag = platform.create_flag(
            key="weekend-promo",
            name="Weekend Promotion",
            description="Special promotion for weekends",
            default_value=False,
            schedule=Schedule(
                schedule_id=f"sched_{uuid.uuid4().hex[:8]}",
                days_of_week=[5, 6],  # Суббота, Воскресенье
                active_hours_start=0,
                active_hours_end=24
            ),
            tags=["promo", "weekend"]
        )
        platform.enable_flag("weekend-promo")
        
        current_day = datetime.now().weekday()
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        is_weekend = current_day in [5, 6]
        
        print(f"  Current day: {day_names[current_day]}")
        print(f"  Weekend promo active: {is_weekend}")
        
        # Environment Overrides
        print("\n🌍 Environment Overrides...")
        
        debug_flag = platform.create_flag(
            key="debug-mode",
            name="Debug Mode",
            description="Enable debug mode",
            default_value=False,
            environment_overrides={
                "development": True,
                "staging": True,
                "production": False
            }
        )
        platform.enable_flag("debug-mode")
        
        for env in ["development", "staging", "production"]:
            value = platform.get_flag("debug-mode", {}, environment=env)
            print(f"  {env}: debug_mode = {value}")
            
        # Platform Statistics
        print("\n📊 Platform Statistics:")
        stats = platform.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
        # List all flags
        print("\n🚩 All Feature Flags:")
        for flag in platform.evaluator.flags.values():
            status_icon = "✓" if flag.status == FlagStatus.ACTIVE else "○"
            print(f"  {status_icon} {flag.key}")
            print(f"    Type: {flag.flag_type.value}")
            print(f"    Tags: {', '.join(flag.tags) if flag.tags else 'none'}")
            if flag.rollout_strategy == RolloutStrategy.PERCENTAGE:
                print(f"    Rollout: {flag.rollout_percentage}%")
                
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Feature Flags & Toggles Platform initialized!")
    print("=" * 60)
