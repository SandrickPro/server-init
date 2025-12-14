#!/usr/bin/env python3
"""
Server Init - Iteration 269: Canary Release Manager
Менеджер канареечных релизов

Функционал:
- Progressive Rollout - прогрессивное развертывание
- Traffic Splitting - разделение трафика
- Metrics Analysis - анализ метрик
- Auto-promotion/Rollback - авто-продвижение/откат
- Analysis Templates - шаблоны анализа
- Webhook Integration - интеграция вебхуков
- Multi-cluster Support - поддержка мульти-кластеров
- Baseline Comparison - сравнение с базовой линией
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
import uuid
import statistics


class ReleasePhase(Enum):
    """Фаза релиза"""
    INITIALIZING = "initializing"
    PROGRESSING = "progressing"
    ANALYZING = "analyzing"
    PROMOTING = "promoting"
    ROLLING_BACK = "rolling_back"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class AnalysisResult(Enum):
    """Результат анализа"""
    SUCCESSFUL = "successful"
    FAILED = "failed"
    INCONCLUSIVE = "inconclusive"
    RUNNING = "running"


class MetricType(Enum):
    """Тип метрики"""
    SUCCESS_RATE = "success_rate"
    LATENCY_P50 = "latency_p50"
    LATENCY_P95 = "latency_p95"
    LATENCY_P99 = "latency_p99"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    CUSTOM = "custom"


class ComparisonType(Enum):
    """Тип сравнения"""
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    WITHIN_RANGE = "within_range"
    DEVIATION = "deviation"


@dataclass
class MetricThreshold:
    """Порог метрики"""
    threshold_id: str
    name: str
    
    # Metric
    metric_type: MetricType = MetricType.SUCCESS_RATE
    metric_query: str = ""
    
    # Comparison
    comparison: ComparisonType = ComparisonType.GREATER_THAN
    threshold_value: float = 99.0
    
    # Range
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    
    # Deviation
    max_deviation_percent: float = 5.0
    
    # Weight
    weight: float = 1.0


@dataclass
class AnalysisTemplate:
    """Шаблон анализа"""
    template_id: str
    name: str
    
    # Thresholds
    thresholds: List[MetricThreshold] = field(default_factory=list)
    
    # Analysis settings
    analysis_interval_seconds: int = 60
    min_sample_count: int = 100
    
    # Pass criteria
    success_threshold: float = 0.95  # 95% of thresholds must pass


@dataclass
class RolloutStep:
    """Шаг развертывания"""
    step_id: str
    step_number: int
    
    # Traffic
    traffic_percent: int = 10
    
    # Duration
    duration_seconds: int = 300
    
    # Status
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Analysis
    analysis_result: AnalysisResult = AnalysisResult.RUNNING
    metrics_collected: Dict[str, float] = field(default_factory=dict)


@dataclass
class CanaryRelease:
    """Канареечный релиз"""
    release_id: str
    name: str
    
    # Service
    service_name: str = ""
    
    # Versions
    baseline_version: str = ""
    canary_version: str = ""
    
    # Phase
    phase: ReleasePhase = ReleasePhase.INITIALIZING
    
    # Steps
    steps: List[RolloutStep] = field(default_factory=list)
    current_step: int = 0
    
    # Traffic
    current_canary_traffic: int = 0
    
    # Analysis
    analysis_template: Optional[AnalysisTemplate] = None
    overall_analysis: AnalysisResult = AnalysisResult.RUNNING
    
    # Auto actions
    auto_promote: bool = True
    auto_rollback: bool = True
    
    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    # Logs
    events: List[str] = field(default_factory=list)


@dataclass
class MetricSample:
    """Образец метрики"""
    sample_id: str
    
    # Metric
    metric_type: MetricType = MetricType.SUCCESS_RATE
    
    # Values
    baseline_value: float = 0
    canary_value: float = 0
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AnalysisRun:
    """Запуск анализа"""
    run_id: str
    release_id: str
    
    # Step
    step_number: int = 0
    
    # Samples
    samples: List[MetricSample] = field(default_factory=list)
    
    # Results
    threshold_results: Dict[str, bool] = field(default_factory=dict)
    overall_result: AnalysisResult = AnalysisResult.RUNNING
    
    # Score
    score: float = 0
    
    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class WebhookConfig:
    """Конфигурация вебхука"""
    webhook_id: str
    name: str
    
    # URL
    url: str = ""
    
    # Events
    events: List[str] = field(default_factory=list)  # phase_change, analysis_complete, etc.
    
    # Headers
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Active
    active: bool = True


class CanaryReleaseManager:
    """Менеджер канареечных релизов"""
    
    def __init__(self):
        self.releases: Dict[str, CanaryRelease] = {}
        self.templates: Dict[str, AnalysisTemplate] = {}
        self.analysis_runs: Dict[str, List[AnalysisRun]] = {}
        self.webhooks: List[WebhookConfig] = []
        
    def create_template(self, name: str) -> AnalysisTemplate:
        """Создание шаблона анализа"""
        template = AnalysisTemplate(
            template_id=f"tmpl_{uuid.uuid4().hex[:8]}",
            name=name
        )
        
        self.templates[name] = template
        return template
        
    def add_threshold(self, template_name: str,
                     metric_type: MetricType,
                     comparison: ComparisonType,
                     threshold_value: float,
                     weight: float = 1.0) -> Optional[MetricThreshold]:
        """Добавление порога"""
        template = self.templates.get(template_name)
        if not template:
            return None
            
        threshold = MetricThreshold(
            threshold_id=f"thresh_{uuid.uuid4().hex[:8]}",
            name=f"{metric_type.value}_{comparison.value}",
            metric_type=metric_type,
            comparison=comparison,
            threshold_value=threshold_value,
            weight=weight
        )
        
        template.thresholds.append(threshold)
        return threshold
        
    def create_release(self, name: str,
                      service_name: str,
                      baseline_version: str,
                      canary_version: str,
                      template_name: Optional[str] = None,
                      steps: List[int] = None) -> CanaryRelease:
        """Создание канареечного релиза"""
        release = CanaryRelease(
            release_id=f"release_{uuid.uuid4().hex[:8]}",
            name=name,
            service_name=service_name,
            baseline_version=baseline_version,
            canary_version=canary_version,
            analysis_template=self.templates.get(template_name)
        )
        
        # Create steps
        traffic_steps = steps or [10, 25, 50, 75, 100]
        
        for i, traffic in enumerate(traffic_steps):
            step = RolloutStep(
                step_id=f"step_{uuid.uuid4().hex[:8]}",
                step_number=i,
                traffic_percent=traffic
            )
            release.steps.append(step)
            
        release.events.append(f"[{datetime.now()}] Release created: {baseline_version} -> {canary_version}")
        
        self.releases[name] = release
        self.analysis_runs[release.release_id] = []
        
        return release
        
    def add_webhook(self, name: str, url: str,
                   events: List[str]) -> WebhookConfig:
        """Добавление вебхука"""
        webhook = WebhookConfig(
            webhook_id=f"webhook_{uuid.uuid4().hex[:8]}",
            name=name,
            url=url,
            events=events
        )
        
        self.webhooks.append(webhook)
        return webhook
        
    async def _trigger_webhooks(self, event: str, data: Dict[str, Any]):
        """Триггер вебхуков"""
        for webhook in self.webhooks:
            if webhook.active and event in webhook.events:
                # Simulate webhook call
                await asyncio.sleep(0.01)
                
    def _collect_metric(self, metric_type: MetricType) -> MetricSample:
        """Сбор метрики"""
        # Simulate metric collection
        baseline_base = {
            MetricType.SUCCESS_RATE: 99.5,
            MetricType.LATENCY_P50: 50,
            MetricType.LATENCY_P95: 150,
            MetricType.LATENCY_P99: 300,
            MetricType.ERROR_RATE: 0.5,
            MetricType.THROUGHPUT: 1000
        }.get(metric_type, 0)
        
        baseline_value = baseline_base * random.uniform(0.95, 1.05)
        canary_value = baseline_base * random.uniform(0.90, 1.10)
        
        return MetricSample(
            sample_id=f"sample_{uuid.uuid4().hex[:8]}",
            metric_type=metric_type,
            baseline_value=baseline_value,
            canary_value=canary_value
        )
        
    def _evaluate_threshold(self, threshold: MetricThreshold,
                           baseline_value: float,
                           canary_value: float) -> bool:
        """Оценка порога"""
        if threshold.comparison == ComparisonType.GREATER_THAN:
            return canary_value >= threshold.threshold_value
        elif threshold.comparison == ComparisonType.LESS_THAN:
            return canary_value <= threshold.threshold_value
        elif threshold.comparison == ComparisonType.WITHIN_RANGE:
            return threshold.min_value <= canary_value <= threshold.max_value
        elif threshold.comparison == ComparisonType.DEVIATION:
            if baseline_value == 0:
                return True
            deviation = abs(canary_value - baseline_value) / baseline_value * 100
            return deviation <= threshold.max_deviation_percent
            
        return False
        
    async def run_analysis(self, release: CanaryRelease) -> AnalysisRun:
        """Запуск анализа"""
        analysis = AnalysisRun(
            run_id=f"analysis_{uuid.uuid4().hex[:8]}",
            release_id=release.release_id,
            step_number=release.current_step
        )
        
        template = release.analysis_template
        
        if not template:
            analysis.overall_result = AnalysisResult.INCONCLUSIVE
            return analysis
            
        # Collect samples
        for threshold in template.thresholds:
            sample = self._collect_metric(threshold.metric_type)
            analysis.samples.append(sample)
            
            # Evaluate threshold
            passed = self._evaluate_threshold(
                threshold,
                sample.baseline_value,
                sample.canary_value
            )
            analysis.threshold_results[threshold.threshold_id] = passed
            
        # Calculate score
        total_weight = sum(t.weight for t in template.thresholds)
        passed_weight = sum(
            t.weight for t in template.thresholds
            if analysis.threshold_results.get(t.threshold_id, False)
        )
        
        analysis.score = passed_weight / total_weight if total_weight > 0 else 0
        
        # Determine result
        if analysis.score >= template.success_threshold:
            analysis.overall_result = AnalysisResult.SUCCESSFUL
        elif analysis.score < 0.5:
            analysis.overall_result = AnalysisResult.FAILED
        else:
            analysis.overall_result = AnalysisResult.INCONCLUSIVE
            
        analysis.completed_at = datetime.now()
        
        # Store analysis
        self.analysis_runs[release.release_id].append(analysis)
        
        return analysis
        
    async def advance_step(self, release: CanaryRelease) -> bool:
        """Продвижение на следующий шаг"""
        if release.current_step >= len(release.steps):
            return False
            
        current_step = release.steps[release.current_step]
        current_step.started_at = datetime.now()
        
        # Set traffic
        release.current_canary_traffic = current_step.traffic_percent
        release.events.append(
            f"[{datetime.now()}] Advanced to step {release.current_step}: {current_step.traffic_percent}% traffic"
        )
        
        # Simulate step duration
        await asyncio.sleep(0.05)
        
        # Run analysis
        release.phase = ReleasePhase.ANALYZING
        analysis = await self.run_analysis(release)
        
        current_step.analysis_result = analysis.overall_result
        current_step.metrics_collected = {
            s.metric_type.value: s.canary_value for s in analysis.samples
        }
        current_step.completed_at = datetime.now()
        
        return analysis.overall_result == AnalysisResult.SUCCESSFUL
        
    async def execute_release(self, release_name: str) -> bool:
        """Выполнение канареечного релиза"""
        release = self.releases.get(release_name)
        if not release:
            return False
            
        release.phase = ReleasePhase.PROGRESSING
        release.events.append(f"[{datetime.now()}] Release execution started")
        
        await self._trigger_webhooks("phase_change", {
            "release": release_name,
            "phase": release.phase.value
        })
        
        for step_num in range(len(release.steps)):
            release.current_step = step_num
            
            step_success = await self.advance_step(release)
            
            if not step_success:
                if release.auto_rollback:
                    release.phase = ReleasePhase.ROLLING_BACK
                    release.events.append(f"[{datetime.now()}] Analysis failed at step {step_num}, rolling back")
                    
                    await self.rollback(release)
                    return False
                else:
                    release.phase = ReleasePhase.PAUSED
                    release.events.append(f"[{datetime.now()}] Analysis failed at step {step_num}, paused")
                    return False
                    
            # Check if final step
            if step_num == len(release.steps) - 1:
                if release.auto_promote:
                    release.phase = ReleasePhase.PROMOTING
                    await self.promote(release)
                    
        return True
        
    async def promote(self, release: CanaryRelease):
        """Продвижение релиза"""
        release.phase = ReleasePhase.COMPLETED
        release.overall_analysis = AnalysisResult.SUCCESSFUL
        release.current_canary_traffic = 100
        release.completed_at = datetime.now()
        release.events.append(f"[{datetime.now()}] Release promoted to production")
        
        await self._trigger_webhooks("release_promoted", {
            "release": release.name,
            "version": release.canary_version
        })
        
    async def rollback(self, release: CanaryRelease):
        """Откат релиза"""
        release.phase = ReleasePhase.FAILED
        release.overall_analysis = AnalysisResult.FAILED
        release.current_canary_traffic = 0
        release.completed_at = datetime.now()
        release.events.append(f"[{datetime.now()}] Release rolled back to {release.baseline_version}")
        
        await self._trigger_webhooks("release_rollback", {
            "release": release.name,
            "version": release.baseline_version
        })
        
    async def pause(self, release_name: str):
        """Пауза релиза"""
        release = self.releases.get(release_name)
        if release:
            release.phase = ReleasePhase.PAUSED
            release.events.append(f"[{datetime.now()}] Release paused")
            
    async def resume(self, release_name: str):
        """Возобновление релиза"""
        release = self.releases.get(release_name)
        if release and release.phase == ReleasePhase.PAUSED:
            release.phase = ReleasePhase.PROGRESSING
            release.events.append(f"[{datetime.now()}] Release resumed")
            
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total = len(self.releases)
        completed = sum(1 for r in self.releases.values() if r.phase == ReleasePhase.COMPLETED)
        failed = sum(1 for r in self.releases.values() if r.phase == ReleasePhase.FAILED)
        in_progress = sum(1 for r in self.releases.values() 
                        if r.phase in [ReleasePhase.PROGRESSING, ReleasePhase.ANALYZING])
        
        return {
            "releases_total": total,
            "releases_completed": completed,
            "releases_failed": failed,
            "releases_in_progress": in_progress,
            "templates_total": len(self.templates),
            "webhooks_total": len(self.webhooks),
            "success_rate": (completed / total * 100) if total > 0 else 0
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 269: Canary Release Manager")
    print("=" * 60)
    
    manager = CanaryReleaseManager()
    print("✓ Canary Release Manager created")
    
    # Create analysis template
    print("\n📋 Creating Analysis Templates...")
    
    template = manager.create_template("standard-analysis")
    
    manager.add_threshold("standard-analysis", MetricType.SUCCESS_RATE, 
                         ComparisonType.GREATER_THAN, 99.0, weight=2.0)
    manager.add_threshold("standard-analysis", MetricType.LATENCY_P95,
                         ComparisonType.LESS_THAN, 200, weight=1.5)
    manager.add_threshold("standard-analysis", MetricType.ERROR_RATE,
                         ComparisonType.LESS_THAN, 1.0, weight=2.0)
    manager.add_threshold("standard-analysis", MetricType.THROUGHPUT,
                         ComparisonType.DEVIATION, 0, weight=1.0)
    
    print(f"  📋 {template.name}: {len(template.thresholds)} thresholds")
    
    for threshold in template.thresholds:
        print(f"    - {threshold.metric_type.value}: {threshold.comparison.value} {threshold.threshold_value}")
        
    # Create webhooks
    print("\n🔗 Creating Webhooks...")
    
    manager.add_webhook("slack-notify", "https://hooks.slack.com/...",
                       ["phase_change", "release_promoted", "release_rollback"])
    manager.add_webhook("pagerduty", "https://events.pagerduty.com/...",
                       ["release_rollback"])
    
    for webhook in manager.webhooks:
        print(f"  🔗 {webhook.name}: {webhook.events}")
        
    # Create canary releases
    print("\n🐤 Creating Canary Releases...")
    
    releases_config = [
        ("api-release-1", "api-service", "1.0.0", "1.1.0", [10, 25, 50, 100]),
        ("web-release-1", "web-service", "2.0.0", "2.1.0", [5, 10, 25, 50, 75, 100]),
        ("worker-release-1", "worker-service", "1.2.0", "1.3.0", [20, 50, 100]),
    ]
    
    for name, service, baseline, canary, steps in releases_config:
        release = manager.create_release(name, service, baseline, canary,
                                        "standard-analysis", steps)
        print(f"  🐤 {name}: {baseline} -> {canary}")
        print(f"     Steps: {' -> '.join(f'{s}%' for s in steps)}")
        
    # Execute releases
    print("\n🚀 Executing Canary Releases...")
    
    release_results = []
    
    for release_name in ["api-release-1", "web-release-1", "worker-release-1"]:
        release = manager.releases[release_name]
        print(f"\n  🐤 {release_name} ({release.baseline_version} -> {release.canary_version})...")
        
        success = await manager.execute_release(release_name)
        
        status_icon = "✅" if success else "❌"
        print(f"  {status_icon} {release_name}: {release.phase.value}")
        
        release_results.append({
            "name": release_name,
            "success": success,
            "release": release
        })
        
    # Display releases
    print("\n🐤 Canary Releases:")
    
    print("\n  ┌─────────────────────┬─────────────┬─────────────┬──────────────┬─────────────┐")
    print("  │ Release             │ Baseline    │ Canary      │ Phase        │ Traffic     │")
    print("  ├─────────────────────┼─────────────┼─────────────┼──────────────┼─────────────┤")
    
    for release in manager.releases.values():
        name = release.name[:19].ljust(19)
        baseline = release.baseline_version[:11].ljust(11)
        canary = release.canary_version[:11].ljust(11)
        phase = release.phase.value[:12].ljust(12)
        traffic = f"{release.current_canary_traffic}%"[:11].ljust(11)
        
        print(f"  │ {name} │ {baseline} │ {canary} │ {phase} │ {traffic} │")
        
    print("  └─────────────────────┴─────────────┴─────────────┴──────────────┴─────────────┘")
    
    # Display steps
    print("\n📊 Rollout Steps:")
    
    for result in release_results:
        release = result["release"]
        print(f"\n  {release.name}:")
        
        for step in release.steps:
            result_icon = {
                AnalysisResult.SUCCESSFUL: "✅",
                AnalysisResult.FAILED: "❌",
                AnalysisResult.INCONCLUSIVE: "⚠️",
                AnalysisResult.RUNNING: "⏳"
            }.get(step.analysis_result, "❓")
            
            print(f"    Step {step.step_number}: {step.traffic_percent}% - {result_icon} {step.analysis_result.value}")
            
    # Analysis results
    print("\n📈 Analysis Results:")
    
    for release_name, runs in list(manager.analysis_runs.items())[:2]:
        release = next((r for r in manager.releases.values() if r.release_id == release_name), None)
        if release and runs:
            print(f"\n  {release.name}:")
            
            for run in runs[-3:]:
                result_icon = {
                    AnalysisResult.SUCCESSFUL: "✅",
                    AnalysisResult.FAILED: "❌",
                    AnalysisResult.INCONCLUSIVE: "⚠️"
                }.get(run.overall_result, "❓")
                
                print(f"    Step {run.step_number}: {result_icon} Score: {run.score:.2%}")
                
    # Metric samples
    print("\n📊 Recent Metric Samples:")
    
    first_release = list(manager.releases.values())[0]
    first_runs = manager.analysis_runs.get(first_release.release_id, [])
    
    if first_runs:
        last_run = first_runs[-1]
        print(f"\n  {first_release.name} (last step):")
        
        print("\n    ┌─────────────────────┬──────────────┬──────────────┬────────────┐")
        print("    │ Metric              │ Baseline     │ Canary       │ Status     │")
        print("    ├─────────────────────┼──────────────┼──────────────┼────────────┤")
        
        for sample in last_run.samples:
            metric = sample.metric_type.value[:19].ljust(19)
            baseline = f"{sample.baseline_value:.2f}"[:12].ljust(12)
            canary = f"{sample.canary_value:.2f}"[:12].ljust(12)
            
            # Compare
            if sample.metric_type in [MetricType.LATENCY_P50, MetricType.LATENCY_P95, 
                                     MetricType.LATENCY_P99, MetricType.ERROR_RATE]:
                status = "✅" if sample.canary_value <= sample.baseline_value * 1.1 else "⚠️"
            else:
                status = "✅" if sample.canary_value >= sample.baseline_value * 0.9 else "⚠️"
                
            status = status.ljust(10)
            
            print(f"    │ {metric} │ {baseline} │ {canary} │ {status} │")
            
        print("    └─────────────────────┴──────────────┴──────────────┴────────────┘")
        
    # Traffic progression
    print("\n📊 Traffic Progression:")
    
    for release in list(manager.releases.values())[:2]:
        print(f"\n  {release.name}:")
        
        for step in release.steps:
            bar = "█" * (step.traffic_percent // 10) + "░" * (10 - step.traffic_percent // 10)
            status = "→" if step.analysis_result == AnalysisResult.SUCCESSFUL else "✗"
            print(f"    Step {step.step_number}: [{bar}] {step.traffic_percent:3d}% {status}")
            
    # Event logs
    print("\n📋 Recent Events:")
    
    for release in list(manager.releases.values())[:1]:
        print(f"\n  {release.name}:")
        for event in release.events[-5:]:
            print(f"    {event}")
            
    # Phase distribution
    print("\n📊 Phase Distribution:")
    
    phase_counts = {}
    for release in manager.releases.values():
        phase_counts[release.phase] = phase_counts.get(release.phase, 0) + 1
        
    for phase, count in sorted(phase_counts.items(), key=lambda x: -x[1]):
        icon = {
            ReleasePhase.COMPLETED: "✅",
            ReleasePhase.FAILED: "❌",
            ReleasePhase.PROGRESSING: "🔄",
            ReleasePhase.PAUSED: "⏸️"
        }.get(phase, "❓")
        bar = "█" * count + "░" * (5 - count)
        print(f"  {icon} {phase.value:15s}: [{bar}] {count}")
        
    # Statistics
    print("\n📊 Manager Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Releases Total: {stats['releases_total']}")
    print(f"  Completed: {stats['releases_completed']}")
    print(f"  Failed: {stats['releases_failed']}")
    print(f"  In Progress: {stats['releases_in_progress']}")
    print(f"  Success Rate: {stats['success_rate']:.1f}%")
    print(f"  Templates: {stats['templates_total']}")
    print(f"  Webhooks: {stats['webhooks_total']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                     Canary Release Dashboard                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Releases:                {stats['releases_total']:>12}                        │")
    print(f"│ Completed:                     {stats['releases_completed']:>12}                        │")
    print(f"│ Success Rate:                  {stats['success_rate']:>11.1f}%                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Failed:                        {stats['releases_failed']:>12}                        │")
    print(f"│ In Progress:                   {stats['releases_in_progress']:>12}                        │")
    print(f"│ Analysis Templates:            {stats['templates_total']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Canary Release Manager initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
