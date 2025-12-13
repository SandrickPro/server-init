#!/usr/bin/env python3
"""
Server Init - Iteration 61: Feature Flags & A/B Testing Platform
Флаги функций и A/B тестирование

Функционал:
- Feature Flags - флаги функций
- Gradual Rollouts - постепенное развёртывание
- A/B Testing - A/B тестирование
- User Targeting - таргетирование пользователей
- Experiment Analytics - аналитика экспериментов
- Kill Switches - аварийное отключение
- Multi-Variant Testing - многовариантное тестирование
- Statistical Analysis - статистический анализ
"""

import json
import asyncio
import hashlib
import math
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
from collections import defaultdict
import uuid


class FlagStatus(Enum):
    """Статус флага"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class RolloutStrategy(Enum):
    """Стратегия развёртывания"""
    PERCENTAGE = "percentage"
    USER_LIST = "user_list"
    USER_ATTRIBUTE = "user_attribute"
    GRADUAL = "gradual"
    SCHEDULE = "schedule"


class ExperimentStatus(Enum):
    """Статус эксперимента"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MetricType(Enum):
    """Тип метрики"""
    CONVERSION = "conversion"
    COUNT = "count"
    REVENUE = "revenue"
    DURATION = "duration"


@dataclass
class TargetingRule:
    """Правило таргетирования"""
    rule_id: str
    attribute: str
    operator: str  # eq, neq, gt, lt, contains, in, regex
    value: Any
    
    # Группировка
    group: str = "default"


@dataclass
class FeatureFlag:
    """Флаг функции"""
    flag_id: str
    key: str
    name: str
    
    # Описание
    description: str = ""
    
    # Статус
    status: FlagStatus = FlagStatus.INACTIVE
    
    # Значение по умолчанию
    default_value: Any = False
    
    # Стратегия
    rollout_strategy: RolloutStrategy = RolloutStrategy.PERCENTAGE
    rollout_percentage: float = 0.0
    
    # Таргетирование
    targeting_rules: List[TargetingRule] = field(default_factory=list)
    
    # Whitelist/Blacklist
    whitelist: List[str] = field(default_factory=list)
    blacklist: List[str] = field(default_factory=list)
    
    # Kill switch
    is_kill_switch: bool = False
    
    # Варианты (для multivariate)
    variants: Dict[str, Any] = field(default_factory=dict)
    
    # Метаданные
    tags: List[str] = field(default_factory=list)
    owner: str = ""
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Расписание
    scheduled_on: Optional[datetime] = None
    scheduled_off: Optional[datetime] = None


@dataclass
class Experiment:
    """A/B эксперимент"""
    experiment_id: str
    key: str
    name: str
    
    # Описание
    description: str = ""
    hypothesis: str = ""
    
    # Статус
    status: ExperimentStatus = ExperimentStatus.DRAFT
    
    # Варианты
    variants: List[Dict[str, Any]] = field(default_factory=list)
    # [{id: "control", name: "Control", weight: 50}, {id: "treatment", name: "Treatment", weight: 50}]
    
    # Таргетирование
    targeting_rules: List[TargetingRule] = field(default_factory=list)
    traffic_allocation: float = 100.0  # % трафика в эксперименте
    
    # Метрики
    primary_metric: str = ""
    secondary_metrics: List[str] = field(default_factory=list)
    
    # Статистика
    minimum_sample_size: int = 1000
    confidence_level: float = 0.95
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    
    # Результаты
    winner: Optional[str] = None


@dataclass
class ExperimentMetric:
    """Метрика эксперимента"""
    metric_id: str
    name: str
    
    # Тип
    metric_type: MetricType = MetricType.CONVERSION
    
    # Описание
    description: str = ""
    
    # Агрегация
    aggregation: str = "sum"  # sum, avg, count, min, max


@dataclass
class ExperimentEvent:
    """Событие эксперимента"""
    event_id: str
    experiment_id: str
    variant_id: str
    
    # Пользователь
    user_id: str = ""
    
    # Событие
    event_type: str = ""  # exposure, conversion, etc.
    
    # Данные
    value: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Время
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class VariantStats:
    """Статистика варианта"""
    variant_id: str
    
    # Exposures
    exposures: int = 0
    unique_users: int = 0
    
    # Конверсии
    conversions: int = 0
    conversion_rate: float = 0.0
    
    # Значения
    total_value: float = 0.0
    average_value: float = 0.0
    
    # Статистическая значимость
    confidence_interval: tuple = (0.0, 0.0)
    p_value: Optional[float] = None
    is_significant: bool = False
    
    # Uplift
    uplift: float = 0.0
    uplift_confidence: tuple = (0.0, 0.0)


@dataclass
class UserContext:
    """Контекст пользователя"""
    user_id: str
    
    # Атрибуты
    attributes: Dict[str, Any] = field(default_factory=dict)
    # e.g., {"country": "US", "plan": "pro", "age": 25}
    
    # Сегменты
    segments: List[str] = field(default_factory=list)


class FlagEvaluator:
    """Оценщик флагов"""
    
    def __init__(self):
        self.evaluation_cache: Dict[str, Dict[str, Any]] = {}
        
    def evaluate(self, flag: FeatureFlag, context: UserContext) -> Any:
        """Оценка флага для пользователя"""
        # Kill switch
        if flag.is_kill_switch and flag.status == FlagStatus.ACTIVE:
            return flag.default_value
            
        # Статус
        if flag.status != FlagStatus.ACTIVE:
            return flag.default_value
            
        # Расписание
        now = datetime.now()
        if flag.scheduled_on and now < flag.scheduled_on:
            return flag.default_value
        if flag.scheduled_off and now > flag.scheduled_off:
            return flag.default_value
            
        # Blacklist
        if context.user_id in flag.blacklist:
            return flag.default_value
            
        # Whitelist
        if context.user_id in flag.whitelist:
            return self._get_flag_value(flag, "treatment")
            
        # Таргетирование
        if flag.targeting_rules:
            if not self._evaluate_targeting(flag.targeting_rules, context):
                return flag.default_value
                
        # Стратегия развёртывания
        if flag.rollout_strategy == RolloutStrategy.PERCENTAGE:
            if self._is_in_percentage(context.user_id, flag.key, flag.rollout_percentage):
                return self._get_flag_value(flag, "treatment")
            return flag.default_value
            
        elif flag.rollout_strategy == RolloutStrategy.USER_ATTRIBUTE:
            # Проверяем атрибуты в правилах
            return self._get_flag_value(flag, "treatment") if flag.targeting_rules else flag.default_value
            
        return flag.default_value
        
    def _evaluate_targeting(self, rules: List[TargetingRule],
                             context: UserContext) -> bool:
        """Оценка правил таргетирования"""
        # Группируем правила
        groups = defaultdict(list)
        for rule in rules:
            groups[rule.group].append(rule)
            
        # Правила внутри группы - OR, между группами - AND
        for group_rules in groups.values():
            group_match = False
            
            for rule in group_rules:
                value = context.attributes.get(rule.attribute)
                
                if self._evaluate_rule(rule, value):
                    group_match = True
                    break
                    
            if not group_match:
                return False
                
        return True
        
    def _evaluate_rule(self, rule: TargetingRule, value: Any) -> bool:
        """Оценка одного правила"""
        if value is None:
            return False
            
        op = rule.operator
        target = rule.value
        
        if op == "eq":
            return value == target
        elif op == "neq":
            return value != target
        elif op == "gt":
            return value > target
        elif op == "lt":
            return value < target
        elif op == "gte":
            return value >= target
        elif op == "lte":
            return value <= target
        elif op == "contains":
            return target in str(value)
        elif op == "in":
            return value in target
        elif op == "not_in":
            return value not in target
            
        return False
        
    def _is_in_percentage(self, user_id: str, flag_key: str,
                           percentage: float) -> bool:
        """Проверка попадания в процент"""
        hash_input = f"{user_id}:{flag_key}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        bucket = hash_value % 100
        
        return bucket < percentage
        
    def _get_flag_value(self, flag: FeatureFlag, variant: str) -> Any:
        """Получение значения флага"""
        if flag.variants and variant in flag.variants:
            return flag.variants[variant]
        return True  # Default enabled value


class ExperimentEngine:
    """Движок экспериментов"""
    
    def __init__(self):
        self.experiments: Dict[str, Experiment] = {}
        self.metrics: Dict[str, ExperimentMetric] = {}
        self.events: List[ExperimentEvent] = []
        self.assignments: Dict[str, Dict[str, str]] = {}  # user_id -> {exp_key -> variant_id}
        
    def create_experiment(self, key: str, name: str,
                           variants: List[Dict[str, Any]], **kwargs) -> Experiment:
        """Создание эксперимента"""
        experiment = Experiment(
            experiment_id=f"exp_{uuid.uuid4().hex[:8]}",
            key=key,
            name=name,
            variants=variants,
            **kwargs
        )
        
        self.experiments[key] = experiment
        return experiment
        
    def create_metric(self, name: str, metric_type: MetricType,
                       **kwargs) -> ExperimentMetric:
        """Создание метрики"""
        metric = ExperimentMetric(
            metric_id=f"metric_{uuid.uuid4().hex[:8]}",
            name=name,
            metric_type=metric_type,
            **kwargs
        )
        
        self.metrics[name] = metric
        return metric
        
    def start_experiment(self, experiment_key: str) -> bool:
        """Запуск эксперимента"""
        experiment = self.experiments.get(experiment_key)
        
        if not experiment or experiment.status != ExperimentStatus.DRAFT:
            return False
            
        experiment.status = ExperimentStatus.RUNNING
        experiment.started_at = datetime.now()
        return True
        
    def stop_experiment(self, experiment_key: str, winner: str = None) -> bool:
        """Остановка эксперимента"""
        experiment = self.experiments.get(experiment_key)
        
        if not experiment or experiment.status != ExperimentStatus.RUNNING:
            return False
            
        experiment.status = ExperimentStatus.COMPLETED
        experiment.ended_at = datetime.now()
        experiment.winner = winner
        return True
        
    def get_variant(self, experiment_key: str, context: UserContext) -> Optional[str]:
        """Получение варианта для пользователя"""
        experiment = self.experiments.get(experiment_key)
        
        if not experiment or experiment.status != ExperimentStatus.RUNNING:
            return None
            
        # Проверяем существующее назначение
        if context.user_id in self.assignments:
            if experiment_key in self.assignments[context.user_id]:
                return self.assignments[context.user_id][experiment_key]
                
        # Таргетирование
        if experiment.targeting_rules:
            evaluator = FlagEvaluator()
            if not evaluator._evaluate_targeting(experiment.targeting_rules, context):
                return None
                
        # Traffic allocation
        hash_input = f"{context.user_id}:{experiment_key}:traffic"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        traffic_bucket = hash_value % 100
        
        if traffic_bucket >= experiment.traffic_allocation:
            return None
            
        # Выбор варианта по весам
        variant_id = self._select_variant(context.user_id, experiment)
        
        # Сохраняем назначение
        if context.user_id not in self.assignments:
            self.assignments[context.user_id] = {}
        self.assignments[context.user_id][experiment_key] = variant_id
        
        # Записываем exposure
        self._record_event(experiment.experiment_id, variant_id,
                           context.user_id, "exposure")
        
        return variant_id
        
    def _select_variant(self, user_id: str, experiment: Experiment) -> str:
        """Выбор варианта по весам"""
        hash_input = f"{user_id}:{experiment.key}:variant"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        bucket = hash_value % 100
        
        cumulative = 0
        for variant in experiment.variants:
            cumulative += variant.get("weight", 0)
            if bucket < cumulative:
                return variant["id"]
                
        return experiment.variants[-1]["id"] if experiment.variants else "control"
        
    def _record_event(self, experiment_id: str, variant_id: str,
                       user_id: str, event_type: str, value: float = 0.0):
        """Запись события"""
        event = ExperimentEvent(
            event_id=f"ev_{uuid.uuid4().hex[:8]}",
            experiment_id=experiment_id,
            variant_id=variant_id,
            user_id=user_id,
            event_type=event_type,
            value=value
        )
        
        self.events.append(event)
        
    def track_conversion(self, experiment_key: str, user_id: str,
                          metric_name: str, value: float = 1.0):
        """Отслеживание конверсии"""
        experiment = self.experiments.get(experiment_key)
        
        if not experiment:
            return
            
        # Находим вариант пользователя
        variant_id = self.assignments.get(user_id, {}).get(experiment_key)
        
        if variant_id:
            self._record_event(experiment.experiment_id, variant_id,
                               user_id, f"conversion:{metric_name}", value)


class StatisticalAnalyzer:
    """Статистический анализатор"""
    
    def analyze_experiment(self, experiment: Experiment,
                            events: List[ExperimentEvent]) -> Dict[str, VariantStats]:
        """Анализ эксперимента"""
        # Группируем события по вариантам
        variant_events = defaultdict(list)
        variant_users = defaultdict(set)
        
        for event in events:
            if event.experiment_id == experiment.experiment_id:
                variant_events[event.variant_id].append(event)
                variant_users[event.variant_id].add(event.user_id)
                
        # Вычисляем статистику для каждого варианта
        stats = {}
        control_stats = None
        
        for variant in experiment.variants:
            variant_id = variant["id"]
            events_list = variant_events[variant_id]
            
            exposures = len([e for e in events_list if e.event_type == "exposure"])
            conversions = len([e for e in events_list if e.event_type.startswith("conversion:")])
            total_value = sum(e.value for e in events_list if e.event_type.startswith("conversion:"))
            
            conversion_rate = conversions / exposures if exposures > 0 else 0
            avg_value = total_value / conversions if conversions > 0 else 0
            
            variant_stat = VariantStats(
                variant_id=variant_id,
                exposures=exposures,
                unique_users=len(variant_users[variant_id]),
                conversions=conversions,
                conversion_rate=conversion_rate,
                total_value=total_value,
                average_value=avg_value
            )
            
            # Расчёт доверительного интервала
            if exposures > 0:
                se = math.sqrt(conversion_rate * (1 - conversion_rate) / exposures)
                z = 1.96  # 95% confidence
                variant_stat.confidence_interval = (
                    max(0, conversion_rate - z * se),
                    min(1, conversion_rate + z * se)
                )
                
            stats[variant_id] = variant_stat
            
            if variant_id == "control":
                control_stats = variant_stat
                
        # Вычисляем uplift и значимость для treatment вариантов
        if control_stats and control_stats.conversion_rate > 0:
            for variant_id, stat in stats.items():
                if variant_id != "control":
                    stat.uplift = (stat.conversion_rate - control_stats.conversion_rate) / control_stats.conversion_rate * 100
                    
                    # Упрощённый расчёт p-value (Z-test)
                    if stat.exposures > 0 and control_stats.exposures > 0:
                        p1 = stat.conversion_rate
                        p2 = control_stats.conversion_rate
                        n1 = stat.exposures
                        n2 = control_stats.exposures
                        
                        p_pooled = (stat.conversions + control_stats.conversions) / (n1 + n2)
                        
                        if p_pooled > 0 and p_pooled < 1:
                            se = math.sqrt(p_pooled * (1 - p_pooled) * (1/n1 + 1/n2))
                            if se > 0:
                                z_score = abs(p1 - p2) / se
                                # Упрощённое p-value
                                stat.p_value = max(0.001, 1 - min(0.999, z_score / 3))
                                stat.is_significant = stat.p_value < 0.05
                                
        return stats


class FeatureFlagPlatform:
    """Платформа Feature Flags"""
    
    def __init__(self):
        self.flags: Dict[str, FeatureFlag] = {}
        self.evaluator = FlagEvaluator()
        self.experiment_engine = ExperimentEngine()
        self.analyzer = StatisticalAnalyzer()
        
        # Аудит
        self.evaluation_log: List[Dict[str, Any]] = []
        
    def create_flag(self, key: str, name: str, **kwargs) -> FeatureFlag:
        """Создание флага"""
        flag = FeatureFlag(
            flag_id=f"flag_{uuid.uuid4().hex[:8]}",
            key=key,
            name=name,
            **kwargs
        )
        
        self.flags[key] = flag
        return flag
        
    def evaluate(self, flag_key: str, context: UserContext,
                  default: Any = None) -> Any:
        """Оценка флага"""
        flag = self.flags.get(flag_key)
        
        if not flag:
            return default
            
        result = self.evaluator.evaluate(flag, context)
        
        # Логирование
        self.evaluation_log.append({
            "flag_key": flag_key,
            "user_id": context.user_id,
            "result": result,
            "timestamp": datetime.now()
        })
        
        return result
        
    def enable_flag(self, flag_key: str, percentage: float = 100.0):
        """Включение флага"""
        flag = self.flags.get(flag_key)
        
        if flag:
            flag.status = FlagStatus.ACTIVE
            flag.rollout_percentage = percentage
            flag.updated_at = datetime.now()
            
    def disable_flag(self, flag_key: str):
        """Отключение флага"""
        flag = self.flags.get(flag_key)
        
        if flag:
            flag.status = FlagStatus.INACTIVE
            flag.updated_at = datetime.now()
            
    def gradual_rollout(self, flag_key: str, target_percentage: float,
                         step: float = 10.0, interval_minutes: int = 30) -> Dict[str, Any]:
        """Постепенное развёртывание"""
        flag = self.flags.get(flag_key)
        
        if not flag:
            return {"error": "Flag not found"}
            
        steps = []
        current = flag.rollout_percentage
        
        while current < target_percentage:
            current = min(current + step, target_percentage)
            steps.append({
                "percentage": current,
                "scheduled_at": datetime.now() + timedelta(minutes=len(steps) * interval_minutes)
            })
            
        return {
            "flag_key": flag_key,
            "start_percentage": flag.rollout_percentage,
            "target_percentage": target_percentage,
            "steps": steps,
            "total_duration_minutes": len(steps) * interval_minutes
        }
        
    def create_kill_switch(self, key: str, name: str) -> FeatureFlag:
        """Создание kill switch"""
        return self.create_flag(
            key=key,
            name=name,
            is_kill_switch=True,
            status=FlagStatus.INACTIVE,
            default_value=True  # Когда активен, возвращает True (функция отключена)
        )
        
    def get_experiment_results(self, experiment_key: str) -> Dict[str, Any]:
        """Получение результатов эксперимента"""
        experiment = self.experiment_engine.experiments.get(experiment_key)
        
        if not experiment:
            return {"error": "Experiment not found"}
            
        stats = self.analyzer.analyze_experiment(
            experiment,
            self.experiment_engine.events
        )
        
        # Определяем победителя
        winner = None
        best_uplift = 0
        
        for variant_id, stat in stats.items():
            if variant_id != "control" and stat.is_significant and stat.uplift > best_uplift:
                best_uplift = stat.uplift
                winner = variant_id
                
        return {
            "experiment_key": experiment_key,
            "status": experiment.status.value,
            "variants": {
                vid: {
                    "exposures": s.exposures,
                    "conversions": s.conversions,
                    "conversion_rate": round(s.conversion_rate * 100, 2),
                    "uplift": round(s.uplift, 2),
                    "is_significant": s.is_significant,
                    "p_value": round(s.p_value, 4) if s.p_value else None
                }
                for vid, s in stats.items()
            },
            "winner": winner,
            "recommendation": f"Roll out {winner}" if winner else "Continue experiment"
        }
        
    def get_stats(self) -> Dict[str, Any]:
        """Статистика платформы"""
        active_flags = len([f for f in self.flags.values() if f.status == FlagStatus.ACTIVE])
        running_experiments = len([
            e for e in self.experiment_engine.experiments.values()
            if e.status == ExperimentStatus.RUNNING
        ])
        
        return {
            "total_flags": len(self.flags),
            "active_flags": active_flags,
            "kill_switches": len([f for f in self.flags.values() if f.is_kill_switch]),
            "total_experiments": len(self.experiment_engine.experiments),
            "running_experiments": running_experiments,
            "total_events": len(self.experiment_engine.events),
            "evaluations_logged": len(self.evaluation_log)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 61: Feature Flags & A/B Testing")
    print("=" * 60)
    
    async def demo():
        # Создание платформы
        platform = FeatureFlagPlatform()
        print("✓ Feature Flag Platform created")
        
        # Создание флагов
        print("\n🚩 Creating feature flags...")
        
        flag1 = platform.create_flag(
            key="new_checkout",
            name="New Checkout Flow",
            description="Redesigned checkout experience",
            rollout_strategy=RolloutStrategy.PERCENTAGE,
            rollout_percentage=0,
            tags=["checkout", "frontend"]
        )
        print(f"  ✓ Flag: {flag1.key}")
        
        flag2 = platform.create_flag(
            key="dark_mode",
            name="Dark Mode",
            description="Dark theme support",
            status=FlagStatus.ACTIVE,
            rollout_percentage=100,
            tags=["ui", "theme"]
        )
        print(f"  ✓ Flag: {flag2.key} (active)")
        
        flag3 = platform.create_flag(
            key="premium_features",
            name="Premium Features",
            description="Premium-only features",
            status=FlagStatus.ACTIVE,
            rollout_strategy=RolloutStrategy.USER_ATTRIBUTE,
            targeting_rules=[
                TargetingRule(
                    rule_id="r1",
                    attribute="plan",
                    operator="in",
                    value=["pro", "enterprise"]
                )
            ]
        )
        print(f"  ✓ Flag: {flag3.key} (targeted)")
        
        # Kill switch
        kill_switch = platform.create_kill_switch(
            key="disable_payments",
            name="Disable Payments"
        )
        print(f"  ✓ Kill Switch: {kill_switch.key}")
        
        # Оценка флагов
        print("\n🔍 Evaluating flags...")
        
        users = [
            UserContext(user_id="user_1", attributes={"country": "US", "plan": "free"}),
            UserContext(user_id="user_2", attributes={"country": "UK", "plan": "pro"}),
            UserContext(user_id="user_3", attributes={"country": "DE", "plan": "enterprise"}),
        ]
        
        for user in users:
            dark_mode = platform.evaluate("dark_mode", user)
            premium = platform.evaluate("premium_features", user)
            print(f"  {user.user_id} (plan={user.attributes['plan']}): dark_mode={dark_mode}, premium={premium}")
            
        # Gradual rollout
        print("\n📈 Gradual rollout...")
        
        rollout = platform.gradual_rollout(
            "new_checkout",
            target_percentage=100,
            step=25,
            interval_minutes=60
        )
        print(f"  Flag: {rollout['flag_key']}")
        print(f"  Steps: {len(rollout['steps'])}")
        for step in rollout['steps']:
            print(f"    -> {step['percentage']}%")
            
        # Включение флага
        platform.enable_flag("new_checkout", percentage=50)
        print(f"\n  ✓ Flag enabled at 50%")
        
        # Проверка процентного rollout
        in_rollout = 0
        for i in range(100):
            ctx = UserContext(user_id=f"test_user_{i}", attributes={})
            if platform.evaluate("new_checkout", ctx):
                in_rollout += 1
        print(f"  Users in rollout: {in_rollout}% (target: 50%)")
        
        # A/B Testing
        print("\n🧪 A/B Testing...")
        
        # Создание эксперимента
        experiment = platform.experiment_engine.create_experiment(
            key="checkout_button_color",
            name="Checkout Button Color Test",
            hypothesis="Green button will increase conversions",
            variants=[
                {"id": "control", "name": "Blue Button", "weight": 50},
                {"id": "treatment", "name": "Green Button", "weight": 50}
            ],
            primary_metric="purchase",
            traffic_allocation=100
        )
        print(f"  ✓ Experiment: {experiment.key}")
        
        # Запуск
        platform.experiment_engine.start_experiment("checkout_button_color")
        print("  ✓ Experiment started")
        
        # Создание метрики
        platform.experiment_engine.create_metric(
            name="purchase",
            metric_type=MetricType.CONVERSION,
            description="Completed purchase"
        )
        
        # Симуляция трафика
        print("\n  Simulating traffic...")
        
        control_conversions = 0
        treatment_conversions = 0
        
        for i in range(1000):
            user = UserContext(user_id=f"exp_user_{i}", attributes={"country": "US"})
            variant = platform.experiment_engine.get_variant("checkout_button_color", user)
            
            if variant:
                # Симуляция конверсии (treatment лучше)
                conversion_prob = 0.10 if variant == "control" else 0.12
                
                if random.random() < conversion_prob:
                    platform.experiment_engine.track_conversion(
                        "checkout_button_color",
                        user.user_id,
                        "purchase"
                    )
                    
                    if variant == "control":
                        control_conversions += 1
                    else:
                        treatment_conversions += 1
                        
        print(f"  Control conversions: {control_conversions}")
        print(f"  Treatment conversions: {treatment_conversions}")
        
        # Результаты эксперимента
        print("\n📊 Experiment Results:")
        
        results = platform.get_experiment_results("checkout_button_color")
        
        for variant_id, data in results["variants"].items():
            sig = "✓" if data["is_significant"] else ""
            print(f"  {variant_id}:")
            print(f"    Exposures: {data['exposures']}")
            print(f"    Conversions: {data['conversions']}")
            print(f"    Rate: {data['conversion_rate']}%")
            if variant_id != "control":
                print(f"    Uplift: {data['uplift']}% {sig}")
                print(f"    P-value: {data['p_value']}")
                
        print(f"\n  Winner: {results['winner'] or 'Not determined'}")
        print(f"  Recommendation: {results['recommendation']}")
        
        # Multi-variant test
        print("\n🎨 Multi-Variant Test...")
        
        mv_experiment = platform.experiment_engine.create_experiment(
            key="homepage_layout",
            name="Homepage Layout Test",
            variants=[
                {"id": "control", "name": "Current Layout", "weight": 25},
                {"id": "variant_a", "name": "Grid Layout", "weight": 25},
                {"id": "variant_b", "name": "Card Layout", "weight": 25},
                {"id": "variant_c", "name": "Minimal Layout", "weight": 25}
            ],
            traffic_allocation=50
        )
        print(f"  ✓ Experiment: {mv_experiment.key}")
        print(f"  Variants: {len(mv_experiment.variants)}")
        
        # Статистика платформы
        print("\n📈 Platform Statistics:")
        stats = platform.get_stats()
        print(f"  Total flags: {stats['total_flags']}")
        print(f"  Active flags: {stats['active_flags']}")
        print(f"  Kill switches: {stats['kill_switches']}")
        print(f"  Experiments: {stats['total_experiments']}")
        print(f"  Running experiments: {stats['running_experiments']}")
        print(f"  Total events: {stats['total_events']}")
        print(f"  Evaluations: {stats['evaluations_logged']}")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Feature Flags & A/B Testing Platform initialized!")
    print("=" * 60)
