#!/usr/bin/env python3
"""
Server Init - Iteration 192: Anomaly Detection Platform
Платформа обнаружения аномалий

Функционал:
- Statistical Analysis - статистический анализ
- Time Series Detection - обнаружение на временных рядах
- Machine Learning Detection - ML обнаружение
- Threshold Management - управление порогами
- Alert Generation - генерация алертов
- Baseline Learning - обучение базовых линий
- Multi-dimensional Detection - многомерное обнаружение
- Root Cause Analysis - анализ причин
"""

import asyncio
import random
import math
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import uuid


class AnomalyType(Enum):
    """Тип аномалии"""
    SPIKE = "spike"
    DROP = "drop"
    DRIFT = "drift"
    SEASONAL = "seasonal"
    CONTEXTUAL = "contextual"
    COLLECTIVE = "collective"
    POINT = "point"


class DetectionMethod(Enum):
    """Метод обнаружения"""
    STATISTICAL = "statistical"
    ZSCORE = "zscore"
    MAD = "mad"  # Median Absolute Deviation
    IQR = "iqr"  # Interquartile Range
    ISOLATION_FOREST = "isolation_forest"
    ARIMA = "arima"
    PROPHET = "prophet"
    LSTM = "lstm"


class Severity(Enum):
    """Серьёзность"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Статус алерта"""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


@dataclass
class DataPoint:
    """Точка данных"""
    timestamp: datetime
    value: float
    metric_name: str = ""
    dimensions: Dict[str, str] = field(default_factory=dict)
    
    # Anomaly info
    is_anomaly: bool = False
    anomaly_score: float = 0.0
    expected_value: float = 0.0


@dataclass
class Baseline:
    """Базовая линия"""
    metric_name: str
    
    # Statistics
    mean: float = 0.0
    std: float = 0.0
    median: float = 0.0
    min_value: float = 0.0
    max_value: float = 0.0
    
    # Percentiles
    p25: float = 0.0
    p75: float = 0.0
    p95: float = 0.0
    p99: float = 0.0
    
    # Time-based
    hourly_means: Dict[int, float] = field(default_factory=dict)
    daily_means: Dict[int, float] = field(default_factory=dict)
    
    # Period
    training_start: datetime = field(default_factory=datetime.now)
    training_end: datetime = field(default_factory=datetime.now)
    data_points: int = 0


@dataclass
class Anomaly:
    """Аномалия"""
    anomaly_id: str
    
    # Detection
    detected_at: datetime = field(default_factory=datetime.now)
    detection_method: DetectionMethod = DetectionMethod.STATISTICAL
    
    # Type
    anomaly_type: AnomalyType = AnomalyType.POINT
    severity: Severity = Severity.MEDIUM
    
    # Metric
    metric_name: str = ""
    dimensions: Dict[str, str] = field(default_factory=dict)
    
    # Values
    actual_value: float = 0.0
    expected_value: float = 0.0
    anomaly_score: float = 0.0
    
    # Context
    baseline_mean: float = 0.0
    baseline_std: float = 0.0
    deviation_percent: float = 0.0
    
    # Time
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    # Analysis
    probable_causes: List[str] = field(default_factory=list)
    related_anomalies: List[str] = field(default_factory=list)


@dataclass
class Alert:
    """Алерт"""
    alert_id: str
    anomaly_id: str
    
    # Info
    title: str = ""
    description: str = ""
    
    # Status
    status: AlertStatus = AlertStatus.OPEN
    severity: Severity = Severity.MEDIUM
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Assignment
    assigned_to: str = ""
    
    # Notes
    notes: List[str] = field(default_factory=list)


@dataclass
class DetectionRule:
    """Правило обнаружения"""
    rule_id: str
    name: str = ""
    
    # Method
    method: DetectionMethod = DetectionMethod.ZSCORE
    
    # Thresholds
    threshold: float = 3.0  # e.g., 3 sigma for z-score
    min_duration: int = 1  # minimum consecutive anomalies
    
    # Scope
    metric_patterns: List[str] = field(default_factory=list)
    
    # Severity mapping
    severity_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "low": 2.0,
        "medium": 3.0,
        "high": 4.0,
        "critical": 5.0
    })
    
    # Status
    is_enabled: bool = True


class StatisticalDetector:
    """Статистический детектор"""
    
    def __init__(self):
        self.baselines: Dict[str, Baseline] = {}
        
    def train_baseline(self, metric_name: str, 
                      data_points: List[DataPoint]) -> Baseline:
        """Обучение базовой линии"""
        if not data_points:
            return Baseline(metric_name=metric_name)
            
        values = [dp.value for dp in data_points]
        sorted_values = sorted(values)
        n = len(values)
        
        baseline = Baseline(
            metric_name=metric_name,
            mean=sum(values) / n,
            median=sorted_values[n // 2],
            min_value=min(values),
            max_value=max(values),
            data_points=n
        )
        
        # Standard deviation
        variance = sum((v - baseline.mean) ** 2 for v in values) / n
        baseline.std = math.sqrt(variance)
        
        # Percentiles
        baseline.p25 = sorted_values[int(n * 0.25)]
        baseline.p75 = sorted_values[int(n * 0.75)]
        baseline.p95 = sorted_values[int(n * 0.95)]
        baseline.p99 = sorted_values[int(n * 0.99)]
        
        # Hourly means
        hourly_values = {}
        for dp in data_points:
            hour = dp.timestamp.hour
            if hour not in hourly_values:
                hourly_values[hour] = []
            hourly_values[hour].append(dp.value)
            
        baseline.hourly_means = {
            h: sum(v) / len(v) for h, v in hourly_values.items()
        }
        
        self.baselines[metric_name] = baseline
        return baseline
        
    def detect_zscore(self, data_point: DataPoint, 
                     threshold: float = 3.0) -> Tuple[bool, float]:
        """Z-score обнаружение"""
        baseline = self.baselines.get(data_point.metric_name)
        if not baseline or baseline.std == 0:
            return False, 0.0
            
        z_score = abs(data_point.value - baseline.mean) / baseline.std
        is_anomaly = z_score > threshold
        
        return is_anomaly, z_score
        
    def detect_iqr(self, data_point: DataPoint,
                  multiplier: float = 1.5) -> Tuple[bool, float]:
        """IQR обнаружение"""
        baseline = self.baselines.get(data_point.metric_name)
        if not baseline:
            return False, 0.0
            
        iqr = baseline.p75 - baseline.p25
        lower_bound = baseline.p25 - multiplier * iqr
        upper_bound = baseline.p75 + multiplier * iqr
        
        if data_point.value < lower_bound:
            score = (lower_bound - data_point.value) / iqr if iqr > 0 else 0
            return True, score
        elif data_point.value > upper_bound:
            score = (data_point.value - upper_bound) / iqr if iqr > 0 else 0
            return True, score
            
        return False, 0.0
        
    def detect_mad(self, data_point: DataPoint, 
                  threshold: float = 3.0) -> Tuple[bool, float]:
        """MAD обнаружение"""
        baseline = self.baselines.get(data_point.metric_name)
        if not baseline:
            return False, 0.0
            
        # Approximate MAD using IQR
        mad = (baseline.p75 - baseline.p25) / 1.35
        
        if mad == 0:
            return False, 0.0
            
        modified_z = 0.6745 * abs(data_point.value - baseline.median) / mad
        is_anomaly = modified_z > threshold
        
        return is_anomaly, modified_z


class TimeSeriesDetector:
    """Детектор временных рядов"""
    
    def __init__(self):
        self.history: Dict[str, List[DataPoint]] = {}
        self.predictions: Dict[str, float] = {}
        
    def add_point(self, data_point: DataPoint):
        """Добавление точки"""
        metric = data_point.metric_name
        if metric not in self.history:
            self.history[metric] = []
        self.history[metric].append(data_point)
        
        # Keep last 1000 points
        if len(self.history[metric]) > 1000:
            self.history[metric] = self.history[metric][-1000:]
            
    def detect_trend_change(self, metric_name: str, 
                           window: int = 10) -> Tuple[bool, str]:
        """Обнаружение изменения тренда"""
        if metric_name not in self.history:
            return False, ""
            
        points = self.history[metric_name]
        if len(points) < window * 2:
            return False, ""
            
        # Compare recent window to previous
        recent = [p.value for p in points[-window:]]
        previous = [p.value for p in points[-window*2:-window]]
        
        recent_mean = sum(recent) / len(recent)
        previous_mean = sum(previous) / len(previous)
        
        change_percent = ((recent_mean - previous_mean) / previous_mean * 100) if previous_mean != 0 else 0
        
        if abs(change_percent) > 20:  # 20% change threshold
            direction = "increasing" if change_percent > 0 else "decreasing"
            return True, direction
            
        return False, ""
        
    def predict_next(self, metric_name: str, 
                    window: int = 10) -> Optional[float]:
        """Простое предсказание"""
        if metric_name not in self.history:
            return None
            
        points = self.history[metric_name]
        if len(points) < window:
            return None
            
        # Simple moving average
        recent = [p.value for p in points[-window:]]
        return sum(recent) / len(recent)


class AnomalyDetectionEngine:
    """Движок обнаружения аномалий"""
    
    def __init__(self):
        self.statistical = StatisticalDetector()
        self.timeseries = TimeSeriesDetector()
        self.rules: Dict[str, DetectionRule] = {}
        self.anomalies: List[Anomaly] = []
        
    def add_rule(self, rule: DetectionRule):
        """Добавление правила"""
        self.rules[rule.rule_id] = rule
        
    def detect(self, data_point: DataPoint) -> Optional[Anomaly]:
        """Обнаружение аномалии"""
        self.timeseries.add_point(data_point)
        
        for rule in self.rules.values():
            if not rule.is_enabled:
                continue
                
            # Check if metric matches pattern
            match = any(
                pattern in data_point.metric_name 
                for pattern in rule.metric_patterns
            ) or not rule.metric_patterns
            
            if not match:
                continue
                
            # Apply detection method
            is_anomaly, score = self._apply_method(data_point, rule)
            
            if is_anomaly:
                anomaly = self._create_anomaly(data_point, rule, score)
                self.anomalies.append(anomaly)
                return anomaly
                
        return None
        
    def _apply_method(self, data_point: DataPoint, 
                     rule: DetectionRule) -> Tuple[bool, float]:
        """Применение метода"""
        if rule.method == DetectionMethod.ZSCORE:
            return self.statistical.detect_zscore(data_point, rule.threshold)
        elif rule.method == DetectionMethod.IQR:
            return self.statistical.detect_iqr(data_point, rule.threshold)
        elif rule.method == DetectionMethod.MAD:
            return self.statistical.detect_mad(data_point, rule.threshold)
        else:
            return self.statistical.detect_zscore(data_point, rule.threshold)
            
    def _create_anomaly(self, data_point: DataPoint, 
                       rule: DetectionRule, score: float) -> Anomaly:
        """Создание аномалии"""
        baseline = self.statistical.baselines.get(data_point.metric_name)
        
        # Determine severity
        severity = Severity.LOW
        for sev_name, threshold in sorted(rule.severity_thresholds.items(), 
                                         key=lambda x: x[1], reverse=True):
            if score >= threshold:
                severity = Severity[sev_name.upper()]
                break
                
        # Determine anomaly type
        if baseline:
            if data_point.value > baseline.mean:
                anomaly_type = AnomalyType.SPIKE
            else:
                anomaly_type = AnomalyType.DROP
        else:
            anomaly_type = AnomalyType.POINT
            
        return Anomaly(
            anomaly_id=f"anom_{uuid.uuid4().hex[:8]}",
            detection_method=rule.method,
            anomaly_type=anomaly_type,
            severity=severity,
            metric_name=data_point.metric_name,
            dimensions=data_point.dimensions,
            actual_value=data_point.value,
            expected_value=baseline.mean if baseline else 0,
            anomaly_score=score,
            baseline_mean=baseline.mean if baseline else 0,
            baseline_std=baseline.std if baseline else 0,
            deviation_percent=((data_point.value - baseline.mean) / baseline.mean * 100) if baseline and baseline.mean != 0 else 0
        )


class AlertManager:
    """Менеджер алертов"""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        
    def create_alert(self, anomaly: Anomaly) -> Alert:
        """Создание алерта"""
        alert = Alert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            anomaly_id=anomaly.anomaly_id,
            title=f"Anomaly detected: {anomaly.metric_name}",
            description=f"{anomaly.anomaly_type.value} detected with score {anomaly.anomaly_score:.2f}",
            severity=anomaly.severity
        )
        
        self.alerts[alert.alert_id] = alert
        return alert
        
    def acknowledge(self, alert_id: str, user: str = "") -> bool:
        """Подтверждение алерта"""
        alert = self.alerts.get(alert_id)
        if alert:
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.now()
            alert.assigned_to = user
            return True
        return False
        
    def resolve(self, alert_id: str, note: str = "") -> bool:
        """Разрешение алерта"""
        alert = self.alerts.get(alert_id)
        if alert:
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            if note:
                alert.notes.append(note)
            self.alert_history.append(alert)
            return True
        return False


class RootCauseAnalyzer:
    """Анализатор причин"""
    
    def __init__(self, engine: AnomalyDetectionEngine):
        self.engine = engine
        
    def analyze(self, anomaly: Anomaly) -> List[str]:
        """Анализ причин"""
        causes = []
        
        # Check for related anomalies
        related = self._find_related_anomalies(anomaly)
        if related:
            causes.append(f"Related anomalies found in {len(related)} other metrics")
            
        # Check baseline
        baseline = self.engine.statistical.baselines.get(anomaly.metric_name)
        if baseline:
            # Seasonal check
            current_hour = anomaly.detected_at.hour
            if current_hour in baseline.hourly_means:
                expected = baseline.hourly_means[current_hour]
                if abs(anomaly.actual_value - expected) > baseline.std * 2:
                    causes.append(f"Value deviates from hourly pattern (expected: {expected:.2f})")
                    
        # Trend check
        is_trend_change, direction = self.engine.timeseries.detect_trend_change(
            anomaly.metric_name
        )
        if is_trend_change:
            causes.append(f"Trend change detected: {direction}")
            
        # Default causes based on type
        if anomaly.anomaly_type == AnomalyType.SPIKE:
            causes.append("Sudden increase in metric value")
        elif anomaly.anomaly_type == AnomalyType.DROP:
            causes.append("Sudden decrease in metric value")
            
        anomaly.probable_causes = causes
        return causes
        
    def _find_related_anomalies(self, anomaly: Anomaly, 
                               time_window_minutes: int = 5) -> List[Anomaly]:
        """Поиск связанных аномалий"""
        related = []
        
        for other in self.engine.anomalies:
            if other.anomaly_id == anomaly.anomaly_id:
                continue
                
            time_diff = abs((other.detected_at - anomaly.detected_at).total_seconds())
            
            if time_diff < time_window_minutes * 60:
                related.append(other)
                anomaly.related_anomalies.append(other.anomaly_id)
                
        return related


class AnomalyDetectionPlatform:
    """Платформа обнаружения аномалий"""
    
    def __init__(self):
        self.engine = AnomalyDetectionEngine()
        self.alert_manager = AlertManager()
        self.rca = RootCauseAnalyzer(self.engine)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        anomalies = self.engine.anomalies
        alerts = list(self.alert_manager.alerts.values())
        
        by_severity = {}
        by_type = {}
        
        for a in anomalies:
            sev = a.severity.value
            atype = a.anomaly_type.value
            by_severity[sev] = by_severity.get(sev, 0) + 1
            by_type[atype] = by_type.get(atype, 0) + 1
            
        return {
            "total_anomalies": len(anomalies),
            "open_alerts": len([a for a in alerts if a.status == AlertStatus.OPEN]),
            "by_severity": by_severity,
            "by_type": by_type,
            "baselines": len(self.engine.statistical.baselines),
            "rules": len(self.engine.rules)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 192: Anomaly Detection Platform")
    print("=" * 60)
    
    platform = AnomalyDetectionPlatform()
    print("✓ Anomaly Detection Platform created")
    
    # Create detection rules
    print("\n📋 Creating Detection Rules...")
    
    rules = [
        DetectionRule(
            rule_id="rule_zscore",
            name="Z-Score Detection",
            method=DetectionMethod.ZSCORE,
            threshold=2.5,
            metric_patterns=["cpu", "memory", "latency"]
        ),
        DetectionRule(
            rule_id="rule_iqr",
            name="IQR Detection",
            method=DetectionMethod.IQR,
            threshold=1.5,
            metric_patterns=["requests", "errors"]
        ),
        DetectionRule(
            rule_id="rule_mad",
            name="MAD Detection",
            method=DetectionMethod.MAD,
            threshold=3.0,
            metric_patterns=["response_time"]
        ),
    ]
    
    for rule in rules:
        platform.engine.add_rule(rule)
        print(f"  ✓ {rule.name} ({rule.method.value})")
        
    # Generate training data
    print("\n📈 Training Baselines...")
    
    metrics = [
        ("cpu_usage", 50, 10),
        ("memory_usage", 70, 8),
        ("request_latency", 100, 20),
        ("requests_per_second", 1000, 100),
        ("error_rate", 0.5, 0.1),
        ("response_time", 150, 30),
    ]
    
    for metric_name, mean, std in metrics:
        # Generate normal data
        training_data = []
        base_time = datetime.now() - timedelta(hours=24)
        
        for i in range(500):
            value = random.gauss(mean, std)
            training_data.append(DataPoint(
                timestamp=base_time + timedelta(minutes=i * 3),
                value=max(0, value),
                metric_name=metric_name
            ))
            
        baseline = platform.engine.statistical.train_baseline(metric_name, training_data)
        print(f"  ✓ {metric_name}: mean={baseline.mean:.2f}, std={baseline.std:.2f}")
        
    # Simulate real-time detection
    print("\n🔍 Running Anomaly Detection...")
    
    detected_anomalies = []
    alerts_created = []
    
    for _ in range(100):
        # Pick random metric
        metric_name, mean, std = random.choice(metrics)
        
        # Normal value most of the time
        if random.random() < 0.9:
            value = random.gauss(mean, std)
        else:
            # Inject anomaly
            if random.random() < 0.5:
                value = mean + std * random.uniform(3, 6)  # Spike
            else:
                value = mean - std * random.uniform(3, 6)  # Drop
                
        data_point = DataPoint(
            timestamp=datetime.now(),
            value=max(0, value),
            metric_name=metric_name,
            dimensions={"host": f"server-{random.randint(1, 5)}"}
        )
        
        # Detect
        anomaly = platform.engine.detect(data_point)
        
        if anomaly:
            detected_anomalies.append(anomaly)
            
            # Analyze root cause
            platform.rca.analyze(anomaly)
            
            # Create alert
            alert = platform.alert_manager.create_alert(anomaly)
            alerts_created.append(alert)
            
    print(f"  Detected {len(detected_anomalies)} anomalies")
    print(f"  Created {len(alerts_created)} alerts")
    
    # Show detected anomalies
    print("\n⚠️ Detected Anomalies:")
    
    print("\n  ┌─────────────────────┬───────────┬──────────┬─────────┬───────────┐")
    print("  │ Metric              │ Type      │ Severity │ Score   │ Deviation │")
    print("  ├─────────────────────┼───────────┼──────────┼─────────┼───────────┤")
    
    for anomaly in detected_anomalies[:10]:
        metric = anomaly.metric_name[:19].ljust(19)
        atype = anomaly.anomaly_type.value[:9].ljust(9)
        severity = anomaly.severity.value[:8].ljust(8)
        score = f"{anomaly.anomaly_score:.2f}".rjust(7)
        deviation = f"{anomaly.deviation_percent:+.1f}%".rjust(9)
        print(f"  │ {metric} │ {atype} │ {severity} │ {score} │ {deviation} │")
        
    print("  └─────────────────────┴───────────┴──────────┴─────────┴───────────┘")
    
    # Detailed anomaly view
    print("\n📋 Anomaly Details (Sample):")
    
    if detected_anomalies:
        sample = detected_anomalies[0]
        print(f"\n  ID: {sample.anomaly_id}")
        print(f"  Metric: {sample.metric_name}")
        print(f"  Type: {sample.anomaly_type.value}")
        print(f"  Severity: {sample.severity.value}")
        print(f"  Detection Method: {sample.detection_method.value}")
        print(f"\n  Values:")
        print(f"    Actual: {sample.actual_value:.2f}")
        print(f"    Expected: {sample.expected_value:.2f}")
        print(f"    Deviation: {sample.deviation_percent:+.1f}%")
        print(f"    Score: {sample.anomaly_score:.2f}")
        print(f"\n  Baseline:")
        print(f"    Mean: {sample.baseline_mean:.2f}")
        print(f"    Std: {sample.baseline_std:.2f}")
        print(f"\n  Probable Causes:")
        for cause in sample.probable_causes:
            print(f"    • {cause}")
            
    # Baseline statistics
    print("\n📊 Baseline Statistics:")
    
    for metric_name, baseline in platform.engine.statistical.baselines.items():
        print(f"\n  {metric_name}:")
        print(f"    Mean: {baseline.mean:.2f}")
        print(f"    Std: {baseline.std:.2f}")
        print(f"    Range: [{baseline.min_value:.2f} - {baseline.max_value:.2f}]")
        print(f"    P95: {baseline.p95:.2f}")
        print(f"    P99: {baseline.p99:.2f}")
        
    # Alert summary
    print("\n🔔 Alert Summary:")
    
    open_alerts = [a for a in platform.alert_manager.alerts.values() if a.status == AlertStatus.OPEN]
    
    print(f"\n  Total Alerts: {len(platform.alert_manager.alerts)}")
    print(f"  Open: {len(open_alerts)}")
    
    # Acknowledge and resolve some alerts
    for alert in open_alerts[:3]:
        platform.alert_manager.acknowledge(alert.alert_id, "admin")
        platform.alert_manager.resolve(alert.alert_id, "Issue resolved")
        
    print(f"  Resolved: {len(platform.alert_manager.alert_history)}")
    
    # Severity distribution
    print("\n📈 Severity Distribution:")
    
    stats = platform.get_statistics()
    
    for severity, count in sorted(stats["by_severity"].items(), key=lambda x: x[1], reverse=True):
        bar = "█" * min(count, 20) + "░" * max(0, 20 - count)
        print(f"  {severity:10} [{bar}] {count}")
        
    # Anomaly type distribution
    print("\n📊 Anomaly Type Distribution:")
    
    for atype, count in sorted(stats["by_type"].items(), key=lambda x: x[1], reverse=True):
        bar = "█" * min(count, 15) + "░" * max(0, 15 - count)
        print(f"  {atype:12} [{bar}] {count}")
        
    # Time series analysis
    print("\n📈 Time Series Analysis:")
    
    for metric_name in ["cpu_usage", "memory_usage", "requests_per_second"]:
        is_trend, direction = platform.engine.timeseries.detect_trend_change(metric_name)
        predicted = platform.engine.timeseries.predict_next(metric_name)
        
        trend_icon = "↗️" if direction == "increasing" else ("↘️" if direction == "decreasing" else "→")
        print(f"  {metric_name}:")
        print(f"    Trend: {trend_icon} {direction if direction else 'stable'}")
        print(f"    Next Predicted: {predicted:.2f}" if predicted else "    Insufficient data")
        
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Anomaly Detection Dashboard                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Anomalies:               {stats['total_anomalies']:>12}                        │")
    print(f"│ Open Alerts:                   {stats['open_alerts']:>12}                        │")
    print(f"│ Detection Rules:               {stats['rules']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Trained Baselines:             {stats['baselines']:>12}                        │")
    critical = stats['by_severity'].get('critical', 0)
    high = stats['by_severity'].get('high', 0)
    print(f"│ Critical Anomalies:            {critical:>12}                        │")
    print(f"│ High Anomalies:                {high:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Anomaly Detection Platform initialized!")
    print("=" * 60)
