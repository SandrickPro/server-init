#!/usr/bin/env python3
"""
Server Init - Iteration 150: A/B Testing Platform
Платформа A/B тестирования

Функционал:
- Experiment Management - управление экспериментами
- Variant Configuration - конфигурация вариантов
- Traffic Allocation - распределение трафика
- Statistical Analysis - статистический анализ
- Feature Targeting - таргетирование фичей
- Result Tracking - отслеживание результатов
- Significance Testing - тестирование значимости
- Rollout Strategy - стратегия раскатки
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid
import random
import math


class ExperimentStatus(Enum):
    """Статус эксперимента"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    STOPPED = "stopped"


class VariantType(Enum):
    """Тип варианта"""
    CONTROL = "control"
    TREATMENT = "treatment"


class MetricType(Enum):
    """Тип метрики"""
    CONVERSION = "conversion"
    REVENUE = "revenue"
    ENGAGEMENT = "engagement"
    RETENTION = "retention"
    CUSTOM = "custom"


class AllocationStrategy(Enum):
    """Стратегия распределения"""
    RANDOM = "random"
    USER_ID_HASH = "user_id_hash"
    STICKY = "sticky"
    GEOGRAPHIC = "geographic"


class SignificanceLevel(Enum):
    """Уровень значимости"""
    LOW = 0.1
    MEDIUM = 0.05
    HIGH = 0.01


@dataclass
class Variant:
    """Вариант эксперимента"""
    variant_id: str
    name: str = ""
    
    # Type
    variant_type: VariantType = VariantType.TREATMENT
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Traffic allocation
    weight: int = 50  # Percentage
    
    # Metrics
    conversions: int = 0
    visitors: int = 0
    revenue: float = 0.0
    
    # Custom metrics
    custom_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class Experiment:
    """Эксперимент"""
    experiment_id: str
    name: str = ""
    description: str = ""
    
    # Variants
    variants: List[Variant] = field(default_factory=list)
    
    # Status
    status: ExperimentStatus = ExperimentStatus.DRAFT
    
    # Schedule
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    # Configuration
    primary_metric: str = "conversion_rate"
    secondary_metrics: List[str] = field(default_factory=list)
    
    # Targeting
    targeting_rules: List[Dict] = field(default_factory=list)
    
    # Settings
    allocation_strategy: AllocationStrategy = AllocationStrategy.USER_ID_HASH
    minimum_sample_size: int = 1000
    significance_level: float = 0.05
    
    # Metadata
    owner: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ExperimentResult:
    """Результат эксперимента"""
    result_id: str
    experiment_id: str = ""
    
    # Sample sizes
    control_visitors: int = 0
    treatment_visitors: int = 0
    
    # Conversion rates
    control_conversion: float = 0.0
    treatment_conversion: float = 0.0
    
    # Lift
    relative_lift: float = 0.0
    absolute_lift: float = 0.0
    
    # Statistical significance
    p_value: float = 1.0
    confidence_interval: tuple = (0.0, 0.0)
    is_significant: bool = False
    
    # Winner
    winner: str = ""
    
    # Timestamp
    calculated_at: datetime = field(default_factory=datetime.now)


@dataclass
class UserAssignment:
    """Назначение пользователя"""
    user_id: str
    experiment_id: str = ""
    variant_id: str = ""
    
    # Tracking
    assigned_at: datetime = field(default_factory=datetime.now)
    converted: bool = False
    conversion_value: float = 0.0


@dataclass
class TargetingRule:
    """Правило таргетирования"""
    rule_id: str
    attribute: str = ""
    operator: str = "equals"  # equals, contains, gt, lt, in
    value: Any = None
    
    # Priority
    priority: int = 0


@dataclass
class MetricDefinition:
    """Определение метрики"""
    metric_id: str
    name: str = ""
    
    # Type
    metric_type: MetricType = MetricType.CONVERSION
    
    # Calculation
    numerator: str = ""  # Event name for numerator
    denominator: str = "visitors"  # Event name for denominator
    
    # Settings
    minimum_detectable_effect: float = 0.05
    is_primary: bool = False


class StatisticalAnalyzer:
    """Статистический анализатор"""
    
    def __init__(self):
        self.significance_level: float = 0.05
        
    def calculate_conversion_rate(self, conversions: int, visitors: int) -> float:
        """Расчёт коэффициента конверсии"""
        if visitors == 0:
            return 0.0
        return conversions / visitors
        
    def calculate_standard_error(self, rate: float, n: int) -> float:
        """Расчёт стандартной ошибки"""
        if n == 0:
            return 0.0
        return math.sqrt(rate * (1 - rate) / n)
        
    def calculate_z_score(self, p1: float, p2: float, n1: int, n2: int) -> float:
        """Расчёт Z-score"""
        if n1 == 0 or n2 == 0:
            return 0.0
            
        pooled_p = (p1 * n1 + p2 * n2) / (n1 + n2)
        se = math.sqrt(pooled_p * (1 - pooled_p) * (1/n1 + 1/n2))
        
        if se == 0:
            return 0.0
            
        return (p2 - p1) / se
        
    def calculate_p_value(self, z_score: float) -> float:
        """Расчёт p-value (two-tailed)"""
        # Approximation using error function
        return 2 * (1 - self._standard_normal_cdf(abs(z_score)))
        
    def _standard_normal_cdf(self, x: float) -> float:
        """CDF стандартного нормального распределения"""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))
        
    def calculate_confidence_interval(self, rate: float, n: int,
                                        confidence: float = 0.95) -> tuple:
        """Расчёт доверительного интервала"""
        z = 1.96  # 95% confidence
        if confidence == 0.99:
            z = 2.576
        elif confidence == 0.90:
            z = 1.645
            
        se = self.calculate_standard_error(rate, n)
        margin = z * se
        
        return (max(0, rate - margin), min(1, rate + margin))
        
    def analyze_experiment(self, control: Variant, treatment: Variant) -> ExperimentResult:
        """Анализ эксперимента"""
        result = ExperimentResult(
            result_id=f"res_{uuid.uuid4().hex[:8]}"
        )
        
        result.control_visitors = control.visitors
        result.treatment_visitors = treatment.visitors
        
        result.control_conversion = self.calculate_conversion_rate(
            control.conversions, control.visitors
        )
        result.treatment_conversion = self.calculate_conversion_rate(
            treatment.conversions, treatment.visitors
        )
        
        # Calculate lift
        if result.control_conversion > 0:
            result.relative_lift = (
                (result.treatment_conversion - result.control_conversion) /
                result.control_conversion * 100
            )
        result.absolute_lift = result.treatment_conversion - result.control_conversion
        
        # Statistical significance
        z_score = self.calculate_z_score(
            result.control_conversion,
            result.treatment_conversion,
            result.control_visitors,
            result.treatment_visitors
        )
        
        result.p_value = self.calculate_p_value(z_score)
        result.is_significant = result.p_value < self.significance_level
        
        # Confidence interval for treatment
        result.confidence_interval = self.calculate_confidence_interval(
            result.treatment_conversion,
            result.treatment_visitors
        )
        
        # Determine winner
        if result.is_significant:
            if result.treatment_conversion > result.control_conversion:
                result.winner = "treatment"
            else:
                result.winner = "control"
        else:
            result.winner = "inconclusive"
            
        return result
        
    def calculate_sample_size(self, baseline_rate: float,
                               mde: float,  # Minimum Detectable Effect
                               alpha: float = 0.05,
                               power: float = 0.8) -> int:
        """Расчёт необходимого размера выборки"""
        # Z-scores for alpha and power
        z_alpha = 1.96  # Two-tailed, alpha=0.05
        z_beta = 0.84   # Power=0.8
        
        expected_rate = baseline_rate * (1 + mde)
        
        p1 = baseline_rate
        p2 = expected_rate
        p_avg = (p1 + p2) / 2
        
        numerator = (z_alpha * math.sqrt(2 * p_avg * (1 - p_avg)) +
                     z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
        denominator = (p2 - p1) ** 2
        
        if denominator == 0:
            return 10000
            
        return int(math.ceil(numerator / denominator))


class TrafficAllocator:
    """Распределитель трафика"""
    
    def __init__(self):
        self.assignments: Dict[str, Dict[str, str]] = {}  # user_id -> {exp_id: variant_id}
        
    def assign_user(self, user_id: str, experiment: Experiment,
                     user_attributes: Dict = None) -> Optional[Variant]:
        """Назначение пользователя в вариант"""
        # Check if already assigned
        if user_id in self.assignments:
            if experiment.experiment_id in self.assignments[user_id]:
                variant_id = self.assignments[user_id][experiment.experiment_id]
                for v in experiment.variants:
                    if v.variant_id == variant_id:
                        return v
                        
        # Check targeting rules
        if user_attributes and not self._check_targeting(experiment, user_attributes):
            return None
            
        # Allocate based on strategy
        variant = self._allocate(user_id, experiment)
        
        if variant:
            if user_id not in self.assignments:
                self.assignments[user_id] = {}
            self.assignments[user_id][experiment.experiment_id] = variant.variant_id
            variant.visitors += 1
            
        return variant
        
    def _check_targeting(self, experiment: Experiment,
                          attributes: Dict) -> bool:
        """Проверка таргетирования"""
        for rule in experiment.targeting_rules:
            attr = rule.get("attribute")
            operator = rule.get("operator", "equals")
            value = rule.get("value")
            
            if attr not in attributes:
                return False
                
            user_value = attributes[attr]
            
            if operator == "equals" and user_value != value:
                return False
            elif operator == "contains" and value not in str(user_value):
                return False
            elif operator == "gt" and user_value <= value:
                return False
            elif operator == "lt" and user_value >= value:
                return False
            elif operator == "in" and user_value not in value:
                return False
                
        return True
        
    def _allocate(self, user_id: str, experiment: Experiment) -> Optional[Variant]:
        """Распределение пользователя"""
        if experiment.allocation_strategy == AllocationStrategy.USER_ID_HASH:
            # Deterministic based on user_id
            hash_val = hash(f"{user_id}:{experiment.experiment_id}") % 100
        else:
            # Random
            hash_val = random.randint(0, 99)
            
        cumulative = 0
        for variant in experiment.variants:
            cumulative += variant.weight
            if hash_val < cumulative:
                return variant
                
        return experiment.variants[-1] if experiment.variants else None


class ExperimentManager:
    """Менеджер экспериментов"""
    
    def __init__(self):
        self.experiments: Dict[str, Experiment] = {}
        self.analyzer = StatisticalAnalyzer()
        self.allocator = TrafficAllocator()
        
    def create_experiment(self, name: str, control_config: Dict,
                           treatment_config: Dict, **kwargs) -> Experiment:
        """Создание эксперимента"""
        experiment = Experiment(
            experiment_id=f"exp_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        
        # Add control variant
        control = Variant(
            variant_id=f"var_{uuid.uuid4().hex[:8]}",
            name="Control",
            variant_type=VariantType.CONTROL,
            config=control_config,
            weight=50
        )
        experiment.variants.append(control)
        
        # Add treatment variant
        treatment = Variant(
            variant_id=f"var_{uuid.uuid4().hex[:8]}",
            name="Treatment",
            variant_type=VariantType.TREATMENT,
            config=treatment_config,
            weight=50
        )
        experiment.variants.append(treatment)
        
        self.experiments[experiment.experiment_id] = experiment
        return experiment
        
    def start_experiment(self, experiment_id: str) -> bool:
        """Запуск эксперимента"""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            return False
            
        experiment.status = ExperimentStatus.RUNNING
        experiment.start_date = datetime.now()
        return True
        
    def stop_experiment(self, experiment_id: str) -> bool:
        """Остановка эксперимента"""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            return False
            
        experiment.status = ExperimentStatus.STOPPED
        experiment.end_date = datetime.now()
        return True
        
    def get_variant(self, experiment_id: str, user_id: str,
                     user_attributes: Dict = None) -> Optional[Variant]:
        """Получение варианта для пользователя"""
        experiment = self.experiments.get(experiment_id)
        if not experiment or experiment.status != ExperimentStatus.RUNNING:
            return None
            
        return self.allocator.assign_user(user_id, experiment, user_attributes)
        
    def record_conversion(self, experiment_id: str, user_id: str,
                           value: float = 1.0) -> bool:
        """Запись конверсии"""
        if user_id not in self.allocator.assignments:
            return False
            
        if experiment_id not in self.allocator.assignments[user_id]:
            return False
            
        variant_id = self.allocator.assignments[user_id][experiment_id]
        experiment = self.experiments.get(experiment_id)
        
        if not experiment:
            return False
            
        for variant in experiment.variants:
            if variant.variant_id == variant_id:
                variant.conversions += 1
                variant.revenue += value
                return True
                
        return False
        
    def get_results(self, experiment_id: str) -> Optional[ExperimentResult]:
        """Получение результатов"""
        experiment = self.experiments.get(experiment_id)
        if not experiment or len(experiment.variants) < 2:
            return None
            
        control = next((v for v in experiment.variants 
                        if v.variant_type == VariantType.CONTROL), None)
        treatment = next((v for v in experiment.variants 
                          if v.variant_type == VariantType.TREATMENT), None)
                          
        if not control or not treatment:
            return None
            
        result = self.analyzer.analyze_experiment(control, treatment)
        result.experiment_id = experiment_id
        
        return result


class RolloutManager:
    """Менеджер раскатки"""
    
    def __init__(self, experiment_manager: ExperimentManager):
        self.manager = experiment_manager
        self.rollouts: Dict[str, Dict] = {}
        
    def gradual_rollout(self, experiment_id: str,
                         start_percent: int = 10,
                         end_percent: int = 100,
                         step: int = 10) -> Dict:
        """Постепенная раскатка"""
        rollout = {
            "experiment_id": experiment_id,
            "current_percent": start_percent,
            "end_percent": end_percent,
            "step": step,
            "history": [{"percent": start_percent, "time": datetime.now()}]
        }
        self.rollouts[experiment_id] = rollout
        
        # Update experiment allocation
        experiment = self.manager.experiments.get(experiment_id)
        if experiment:
            for variant in experiment.variants:
                if variant.variant_type == VariantType.TREATMENT:
                    variant.weight = start_percent
                elif variant.variant_type == VariantType.CONTROL:
                    variant.weight = 100 - start_percent
                    
        return rollout
        
    def increase_rollout(self, experiment_id: str) -> Optional[Dict]:
        """Увеличение процента раскатки"""
        rollout = self.rollouts.get(experiment_id)
        if not rollout:
            return None
            
        new_percent = min(
            rollout["current_percent"] + rollout["step"],
            rollout["end_percent"]
        )
        rollout["current_percent"] = new_percent
        rollout["history"].append({"percent": new_percent, "time": datetime.now()})
        
        # Update experiment
        experiment = self.manager.experiments.get(experiment_id)
        if experiment:
            for variant in experiment.variants:
                if variant.variant_type == VariantType.TREATMENT:
                    variant.weight = new_percent
                elif variant.variant_type == VariantType.CONTROL:
                    variant.weight = 100 - new_percent
                    
        return rollout


class ABTestingPlatform:
    """Платформа A/B тестирования"""
    
    def __init__(self):
        self.experiment_manager = ExperimentManager()
        self.rollout_manager = RolloutManager(self.experiment_manager)
        self.metrics: Dict[str, MetricDefinition] = {}
        
    def define_metric(self, name: str, metric_type: MetricType,
                       **kwargs) -> MetricDefinition:
        """Определение метрики"""
        metric = MetricDefinition(
            metric_id=f"met_{uuid.uuid4().hex[:8]}",
            name=name,
            metric_type=metric_type,
            **kwargs
        )
        self.metrics[metric.metric_id] = metric
        return metric
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        experiments = self.experiment_manager.experiments
        
        running = len([e for e in experiments.values() 
                       if e.status == ExperimentStatus.RUNNING])
        completed = len([e for e in experiments.values() 
                         if e.status == ExperimentStatus.COMPLETED])
                         
        total_visitors = sum(
            sum(v.visitors for v in e.variants)
            for e in experiments.values()
        )
        total_conversions = sum(
            sum(v.conversions for v in e.variants)
            for e in experiments.values()
        )
        
        return {
            "total_experiments": len(experiments),
            "running_experiments": running,
            "completed_experiments": completed,
            "total_visitors": total_visitors,
            "total_conversions": total_conversions,
            "defined_metrics": len(self.metrics)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 150: A/B Testing Platform")
    print("=" * 60)
    
    async def demo():
        platform = ABTestingPlatform()
        print("✓ A/B Testing Platform created")
        
        # Define metrics
        print("\n📏 Defining Metrics...")
        
        metrics_data = [
            ("conversion_rate", MetricType.CONVERSION, True),
            ("revenue_per_user", MetricType.REVENUE, False),
            ("click_through_rate", MetricType.ENGAGEMENT, False),
            ("time_on_page", MetricType.ENGAGEMENT, False)
        ]
        
        for name, mtype, is_primary in metrics_data:
            metric = platform.define_metric(name, mtype, is_primary=is_primary)
            primary_str = " (primary)" if is_primary else ""
            print(f"  ✓ {name}: {mtype.value}{primary_str}")
            
        # Create experiments
        print("\n🧪 Creating Experiments...")
        
        # Experiment 1: Button Color
        exp1 = platform.experiment_manager.create_experiment(
            name="Button Color Test",
            control_config={"button_color": "blue"},
            treatment_config={"button_color": "green"},
            description="Testing green button vs blue button",
            primary_metric="conversion_rate",
            minimum_sample_size=1000,
            owner="product@company.com"
        )
        print(f"  ✓ {exp1.name}: {exp1.experiment_id}")
        
        # Experiment 2: Pricing Page Layout
        exp2 = platform.experiment_manager.create_experiment(
            name="Pricing Page Layout",
            control_config={"layout": "horizontal"},
            treatment_config={"layout": "vertical"},
            description="Testing vertical vs horizontal pricing layout",
            primary_metric="conversion_rate",
            minimum_sample_size=2000,
            owner="growth@company.com",
            targeting_rules=[
                {"attribute": "country", "operator": "in", "value": ["US", "UK", "CA"]}
            ]
        )
        print(f"  ✓ {exp2.name}: {exp2.experiment_id}")
        
        # Experiment 3: Checkout Flow
        exp3 = platform.experiment_manager.create_experiment(
            name="Simplified Checkout",
            control_config={"checkout_steps": 3},
            treatment_config={"checkout_steps": 1},
            description="One-page checkout vs multi-step",
            primary_metric="conversion_rate",
            secondary_metrics=["revenue_per_user"],
            minimum_sample_size=5000
        )
        print(f"  ✓ {exp3.name}: {exp3.experiment_id}")
        
        # Start experiments
        print("\n▶️ Starting Experiments...")
        
        platform.experiment_manager.start_experiment(exp1.experiment_id)
        platform.experiment_manager.start_experiment(exp2.experiment_id)
        print(f"  ✓ {exp1.name}: RUNNING")
        print(f"  ✓ {exp2.name}: RUNNING")
        
        # Simulate traffic
        print("\n🚦 Simulating Traffic...")
        
        # Simulate users for exp1
        for i in range(5000):
            user_id = f"user_{i:05d}"
            variant = platform.experiment_manager.get_variant(
                exp1.experiment_id,
                user_id
            )
            
            if variant:
                # Simulate conversion (treatment has 15% lift)
                base_rate = 0.10
                if variant.variant_type == VariantType.TREATMENT:
                    rate = base_rate * 1.15
                else:
                    rate = base_rate
                    
                if random.random() < rate:
                    platform.experiment_manager.record_conversion(
                        exp1.experiment_id,
                        user_id,
                        value=random.uniform(20, 100)
                    )
                    
        # Simulate users for exp2 with targeting
        for i in range(3000):
            user_id = f"user_geo_{i:05d}"
            country = random.choice(["US", "UK", "CA", "DE", "FR"])
            
            variant = platform.experiment_manager.get_variant(
                exp2.experiment_id,
                user_id,
                {"country": country}
            )
            
            if variant:
                base_rate = 0.08
                if variant.variant_type == VariantType.TREATMENT:
                    rate = base_rate * 1.20
                else:
                    rate = base_rate
                    
                if random.random() < rate:
                    platform.experiment_manager.record_conversion(
                        exp2.experiment_id,
                        user_id
                    )
                    
        print("  ✓ Simulated 5000 users for Button Color Test")
        print("  ✓ Simulated 3000 users for Pricing Layout")
        
        # Show experiment status
        print("\n📊 Experiment Status:")
        
        for exp in [exp1, exp2]:
            print(f"\n  {exp.name}:")
            print(f"    Status: {exp.status.value}")
            for variant in exp.variants:
                conv_rate = (variant.conversions / variant.visitors * 100) if variant.visitors > 0 else 0
                print(f"    {variant.name}: {variant.visitors:,} visitors, {variant.conversions:,} conversions ({conv_rate:.2f}%)")
                
        # Get results
        print("\n📈 Experiment Results:")
        
        for exp in [exp1, exp2]:
            result = platform.experiment_manager.get_results(exp.experiment_id)
            if result:
                print(f"\n  {exp.name}:")
                print(f"    Control Conversion: {result.control_conversion * 100:.2f}%")
                print(f"    Treatment Conversion: {result.treatment_conversion * 100:.2f}%")
                print(f"    Relative Lift: {result.relative_lift:+.2f}%")
                print(f"    P-Value: {result.p_value:.4f}")
                
                sig_str = "✓ YES" if result.is_significant else "✗ NO"
                print(f"    Significant (p<0.05): {sig_str}")
                print(f"    Winner: {result.winner.upper()}")
                print(f"    CI 95%: [{result.confidence_interval[0]*100:.2f}%, {result.confidence_interval[1]*100:.2f}%]")
                
        # Sample size calculation
        print("\n🔢 Required Sample Sizes:")
        
        analyzer = platform.experiment_manager.analyzer
        
        scenarios = [
            (0.05, 0.10),  # 5% baseline, 10% MDE
            (0.10, 0.05),  # 10% baseline, 5% MDE
            (0.20, 0.10),  # 20% baseline, 10% MDE
        ]
        
        for baseline, mde in scenarios:
            sample_size = analyzer.calculate_sample_size(baseline, mde)
            print(f"  Baseline {baseline*100}%, MDE {mde*100}%: {sample_size:,} per variant")
            
        # Gradual rollout
        print("\n🚀 Gradual Rollout:")
        
        # Start exp3 with gradual rollout
        platform.experiment_manager.start_experiment(exp3.experiment_id)
        rollout = platform.rollout_manager.gradual_rollout(
            exp3.experiment_id,
            start_percent=10,
            end_percent=100,
            step=10
        )
        
        print(f"\n  {exp3.name}:")
        print(f"    Initial: {rollout['current_percent']}%")
        
        # Increase rollout
        for _ in range(3):
            rollout = platform.rollout_manager.increase_rollout(exp3.experiment_id)
            print(f"    Increased to: {rollout['current_percent']}%")
            
        # Experiment overview
        print("\n📋 All Experiments Overview:")
        print("  ┌─────────────────────────────────────────────────────────────────────────┐")
        print("  │ Experiment               │ Status  │ Visitors │ Conv. │ Lift    │ Sig.  │")
        print("  ├─────────────────────────────────────────────────────────────────────────┤")
        
        for exp_id, exp in platform.experiment_manager.experiments.items():
            result = platform.experiment_manager.get_results(exp_id)
            if result:
                total_visitors = result.control_visitors + result.treatment_visitors
                avg_conv = (result.control_conversion + result.treatment_conversion) / 2 * 100
                lift_str = f"{result.relative_lift:+.1f}%"
                sig_str = "Yes" if result.is_significant else "No"
            else:
                total_visitors = sum(v.visitors for v in exp.variants)
                avg_conv = 0
                lift_str = "N/A"
                sig_str = "N/A"
                
            name_short = exp.name[:22] + "..." if len(exp.name) > 25 else exp.name.ljust(25)
            print(f"  │ {name_short} │ {exp.status.value:7} │ {total_visitors:8,} │ {avg_conv:5.1f}% │ {lift_str:7} │ {sig_str:5} │")
            
        print("  └─────────────────────────────────────────────────────────────────────────┘")
        
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Experiments: {stats['total_experiments']}")
        print(f"  Running: {stats['running_experiments']}")
        print(f"  Completed: {stats['completed_experiments']}")
        print(f"  Total Visitors: {stats['total_visitors']:,}")
        print(f"  Total Conversions: {stats['total_conversions']:,}")
        print(f"  Defined Metrics: {stats['defined_metrics']}")
        
        # Dashboard
        print("\n📋 A/B Testing Dashboard:")
        print("  ┌────────────────────────────────────────────────────────────┐")
        print("  │                 A/B Testing Overview                       │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Experiments:     {stats['total_experiments']:>10}                    │")
        print(f"  │ Running:               {stats['running_experiments']:>10}                    │")
        print(f"  │ Completed:             {stats['completed_experiments']:>10}                    │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Visitors:        {stats['total_visitors']:>10,}                    │")
        print(f"  │ Total Conversions:     {stats['total_conversions']:>10,}                    │")
        print(f"  │ Defined Metrics:       {stats['defined_metrics']:>10}                    │")
        print("  └────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("A/B Testing Platform initialized!")
    print("=" * 60)
