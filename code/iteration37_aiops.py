#!/usr/bin/env python3
"""
Server Init - Iteration 37: Intelligent Operations (AIOps)
Интеллектуальные операции на базе AI

Функционал:
- Anomaly Detection - обнаружение аномалий
- Predictive Analytics - предиктивная аналитика
- Root Cause Analysis - анализ первопричин
- Auto-Remediation - автоматическое исправление
- Capacity Planning - планирование ёмкости
- Incident Prediction - предсказание инцидентов
- Performance Optimization - оптимизация производительности
- Intelligent Alerting - интеллектуальные алерты
"""

import json
import asyncio
import hashlib
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Tuple
from enum import Enum
from abc import ABC, abstractmethod
import random
from collections import defaultdict
import uuid
import math
import statistics


class AnomalyType(Enum):
    """Тип аномалии"""
    SPIKE = "spike"
    DIP = "dip"
    TREND_CHANGE = "trend_change"
    SEASONALITY_BREAK = "seasonality_break"
    LEVEL_SHIFT = "level_shift"
    OUTLIER = "outlier"


class AlertSeverity(Enum):
    """Серьёзность алерта"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IncidentStatus(Enum):
    """Статус инцидента"""
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    REMEDIATING = "remediating"
    RESOLVED = "resolved"
    CLOSED = "closed"


class RemediationAction(Enum):
    """Действие по исправлению"""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    RESTART_SERVICE = "restart_service"
    ROLLBACK = "rollback"
    FAILOVER = "failover"
    CLEAR_CACHE = "clear_cache"
    INCREASE_TIMEOUT = "increase_timeout"
    BLOCK_TRAFFIC = "block_traffic"


@dataclass
class MetricPoint:
    """Точка метрики"""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class TimeSeries:
    """Временной ряд"""
    metric_name: str
    points: List[MetricPoint] = field(default_factory=list)
    
    def add_point(self, value: float, labels: Optional[Dict[str, str]] = None):
        """Добавление точки"""
        self.points.append(MetricPoint(
            timestamp=datetime.now(),
            value=value,
            labels=labels or {}
        ))
        
    def get_values(self, window_minutes: int = 60) -> List[float]:
        """Получение значений за окно"""
        cutoff = datetime.now() - timedelta(minutes=window_minutes)
        return [p.value for p in self.points if p.timestamp > cutoff]
        
    def get_statistics(self, window_minutes: int = 60) -> Dict[str, float]:
        """Получение статистики"""
        values = self.get_values(window_minutes)
        if not values:
            return {}
            
        return {
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "stddev": statistics.stdev(values) if len(values) > 1 else 0,
            "count": len(values)
        }


@dataclass
class Anomaly:
    """Аномалия"""
    anomaly_id: str
    metric_name: str
    anomaly_type: AnomalyType
    severity: AlertSeverity
    
    # Детали
    detected_at: datetime = field(default_factory=datetime.now)
    value: float = 0.0
    expected_value: float = 0.0
    deviation: float = 0.0
    
    # Контекст
    labels: Dict[str, str] = field(default_factory=dict)
    related_metrics: List[str] = field(default_factory=list)
    
    # Статус
    acknowledged: bool = False
    resolved: bool = False


@dataclass
class Incident:
    """Инцидент"""
    incident_id: str
    title: str
    description: str
    severity: AlertSeverity
    status: IncidentStatus = IncidentStatus.DETECTED
    
    # Время
    detected_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Связи
    anomalies: List[str] = field(default_factory=list)
    affected_services: List[str] = field(default_factory=list)
    related_incidents: List[str] = field(default_factory=list)
    
    # Root Cause
    root_cause: Optional[str] = None
    root_cause_confidence: float = 0.0
    
    # Remediation
    remediation_actions: List[Dict[str, Any]] = field(default_factory=list)
    auto_remediation_enabled: bool = True
    
    # Timeline
    timeline: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class CapacityForecast:
    """Прогноз ёмкости"""
    resource_type: str
    current_usage: float
    current_capacity: float
    
    # Прогнозы
    forecast_7d: float = 0.0
    forecast_30d: float = 0.0
    forecast_90d: float = 0.0
    
    # Рекомендации
    exhaustion_date: Optional[datetime] = None
    recommended_capacity: float = 0.0
    recommendation: str = ""
    confidence: float = 0.0


@dataclass
class PerformanceInsight:
    """Инсайт производительности"""
    insight_id: str
    category: str
    title: str
    description: str
    impact: str
    
    # Метрики
    affected_metrics: List[str] = field(default_factory=list)
    improvement_potential: float = 0.0
    
    # Рекомендации
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    priority: int = 1


class AnomalyDetector:
    """Детектор аномалий"""
    
    def __init__(self):
        self.time_series: Dict[str, TimeSeries] = {}
        self.baselines: Dict[str, Dict[str, float]] = {}
        self.anomalies: List[Anomaly] = []
        
        # Параметры детекции
        self.zscore_threshold = 3.0
        self.iqr_multiplier = 1.5
        self.min_samples = 30
        
    def record_metric(self, metric_name: str, value: float,
                      labels: Optional[Dict[str, str]] = None):
        """Запись метрики"""
        if metric_name not in self.time_series:
            self.time_series[metric_name] = TimeSeries(metric_name=metric_name)
            
        self.time_series[metric_name].add_point(value, labels)
        
        # Ограничение истории
        if len(self.time_series[metric_name].points) > 10000:
            self.time_series[metric_name].points = \
                self.time_series[metric_name].points[-5000:]
                
        # Проверка аномалий
        anomaly = self._detect_anomaly(metric_name, value, labels)
        if anomaly:
            self.anomalies.append(anomaly)
            
    def _detect_anomaly(self, metric_name: str, value: float,
                        labels: Optional[Dict[str, str]]) -> Optional[Anomaly]:
        """Детекция аномалии"""
        ts = self.time_series.get(metric_name)
        if not ts or len(ts.points) < self.min_samples:
            return None
            
        stats = ts.get_statistics(window_minutes=60)
        if not stats:
            return None
            
        # Z-score метод
        if stats["stddev"] > 0:
            zscore = abs(value - stats["mean"]) / stats["stddev"]
            
            if zscore > self.zscore_threshold:
                anomaly_type = AnomalyType.SPIKE if value > stats["mean"] else AnomalyType.DIP
                severity = self._calculate_severity(zscore)
                
                return Anomaly(
                    anomaly_id=f"anomaly_{uuid.uuid4().hex[:8]}",
                    metric_name=metric_name,
                    anomaly_type=anomaly_type,
                    severity=severity,
                    value=value,
                    expected_value=stats["mean"],
                    deviation=zscore,
                    labels=labels or {}
                )
                
        # IQR метод для outliers
        values = ts.get_values(window_minutes=60)
        q1 = statistics.quantiles(values, n=4)[0]
        q3 = statistics.quantiles(values, n=4)[2]
        iqr = q3 - q1
        
        lower_bound = q1 - self.iqr_multiplier * iqr
        upper_bound = q3 + self.iqr_multiplier * iqr
        
        if value < lower_bound or value > upper_bound:
            return Anomaly(
                anomaly_id=f"anomaly_{uuid.uuid4().hex[:8]}",
                metric_name=metric_name,
                anomaly_type=AnomalyType.OUTLIER,
                severity=AlertSeverity.MEDIUM,
                value=value,
                expected_value=stats["median"],
                deviation=abs(value - stats["median"]) / iqr if iqr > 0 else 0,
                labels=labels or {}
            )
            
        return None
        
    def _calculate_severity(self, zscore: float) -> AlertSeverity:
        """Расчёт серьёзности"""
        if zscore > 5:
            return AlertSeverity.CRITICAL
        elif zscore > 4:
            return AlertSeverity.HIGH
        elif zscore > 3.5:
            return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.LOW
            
    def update_baseline(self, metric_name: str):
        """Обновление baseline"""
        ts = self.time_series.get(metric_name)
        if not ts:
            return
            
        # Baseline на основе последних 24 часов
        stats = ts.get_statistics(window_minutes=1440)
        if stats:
            self.baselines[metric_name] = stats
            
    def get_anomalies(self, metric_name: Optional[str] = None,
                      severity: Optional[AlertSeverity] = None,
                      resolved: Optional[bool] = None) -> List[Anomaly]:
        """Получение аномалий"""
        results = self.anomalies
        
        if metric_name:
            results = [a for a in results if a.metric_name == metric_name]
            
        if severity:
            results = [a for a in results if a.severity == severity]
            
        if resolved is not None:
            results = [a for a in results if a.resolved == resolved]
            
        return sorted(results, key=lambda a: a.detected_at, reverse=True)


class PredictiveAnalytics:
    """Предиктивная аналитика"""
    
    def __init__(self, anomaly_detector: AnomalyDetector):
        self.anomaly_detector = anomaly_detector
        self.models: Dict[str, Dict[str, Any]] = {}
        self.forecasts: Dict[str, List[float]] = {}
        
    def train_model(self, metric_name: str):
        """Обучение модели для метрики"""
        ts = self.anomaly_detector.time_series.get(metric_name)
        if not ts or len(ts.points) < 100:
            return
            
        values = [p.value for p in ts.points]
        
        # Простая модель: скользящее среднее + тренд
        window_size = min(24, len(values) // 4)
        
        # Скользящее среднее
        moving_avg = []
        for i in range(len(values) - window_size + 1):
            moving_avg.append(statistics.mean(values[i:i+window_size]))
            
        # Тренд (линейная регрессия)
        n = len(moving_avg)
        if n > 1:
            x_mean = (n - 1) / 2
            y_mean = statistics.mean(moving_avg)
            
            numerator = sum((i - x_mean) * (moving_avg[i] - y_mean) for i in range(n))
            denominator = sum((i - x_mean) ** 2 for i in range(n))
            
            slope = numerator / denominator if denominator != 0 else 0
            intercept = y_mean - slope * x_mean
        else:
            slope = 0
            intercept = values[-1] if values else 0
            
        self.models[metric_name] = {
            "type": "linear_trend",
            "slope": slope,
            "intercept": intercept,
            "baseline": statistics.mean(values[-window_size:]) if values else 0,
            "stddev": statistics.stdev(values[-window_size:]) if len(values) > 1 else 0,
            "trained_at": datetime.now().isoformat()
        }
        
    def forecast(self, metric_name: str, periods: int = 24) -> List[float]:
        """Прогнозирование"""
        model = self.models.get(metric_name)
        if not model:
            self.train_model(metric_name)
            model = self.models.get(metric_name)
            
        if not model:
            return []
            
        ts = self.anomaly_detector.time_series.get(metric_name)
        if not ts:
            return []
            
        current_idx = len(ts.points)
        forecasts = []
        
        for i in range(periods):
            predicted = model["slope"] * (current_idx + i) + model["intercept"]
            
            # Добавление сезонности (упрощённо)
            if model["stddev"] > 0:
                noise = random.gauss(0, model["stddev"] * 0.1)
                predicted += noise
                
            forecasts.append(max(0, predicted))
            
        self.forecasts[metric_name] = forecasts
        return forecasts
        
    def predict_incident(self, metric_name: str,
                         threshold: float) -> Optional[datetime]:
        """Предсказание инцидента (когда метрика достигнет порога)"""
        forecast = self.forecast(metric_name, periods=168)  # 7 дней
        
        for i, value in enumerate(forecast):
            if value >= threshold:
                return datetime.now() + timedelta(hours=i)
                
        return None
        
    def get_trend(self, metric_name: str) -> Dict[str, Any]:
        """Получение тренда"""
        model = self.models.get(metric_name)
        if not model:
            return {"trend": "unknown"}
            
        slope = model["slope"]
        
        if slope > 0.1:
            trend = "increasing"
        elif slope < -0.1:
            trend = "decreasing"
        else:
            trend = "stable"
            
        return {
            "trend": trend,
            "slope": slope,
            "change_per_hour": slope
        }


class RootCauseAnalyzer:
    """Анализатор первопричин"""
    
    def __init__(self, anomaly_detector: AnomalyDetector):
        self.anomaly_detector = anomaly_detector
        self.service_dependencies: Dict[str, List[str]] = {}
        self.metric_correlations: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.known_patterns: List[Dict[str, Any]] = []
        
    def add_service_dependency(self, service: str, depends_on: List[str]):
        """Добавление зависимости сервиса"""
        self.service_dependencies[service] = depends_on
        
    def add_known_pattern(self, pattern: Dict[str, Any]):
        """Добавление известного паттерна"""
        self.known_patterns.append(pattern)
        
    def calculate_correlations(self, metric1: str, metric2: str) -> float:
        """Расчёт корреляции между метриками"""
        ts1 = self.anomaly_detector.time_series.get(metric1)
        ts2 = self.anomaly_detector.time_series.get(metric2)
        
        if not ts1 or not ts2:
            return 0.0
            
        values1 = ts1.get_values(window_minutes=60)
        values2 = ts2.get_values(window_minutes=60)
        
        if len(values1) < 10 or len(values2) < 10:
            return 0.0
            
        # Выравнивание длин
        min_len = min(len(values1), len(values2))
        values1 = values1[-min_len:]
        values2 = values2[-min_len:]
        
        # Pearson correlation
        mean1 = statistics.mean(values1)
        mean2 = statistics.mean(values2)
        
        numerator = sum((v1 - mean1) * (v2 - mean2) for v1, v2 in zip(values1, values2))
        denom1 = math.sqrt(sum((v - mean1) ** 2 for v in values1))
        denom2 = math.sqrt(sum((v - mean2) ** 2 for v in values2))
        
        if denom1 * denom2 == 0:
            return 0.0
            
        correlation = numerator / (denom1 * denom2)
        self.metric_correlations[metric1][metric2] = correlation
        
        return correlation
        
    def analyze(self, incident: Incident) -> Dict[str, Any]:
        """Анализ первопричины инцидента"""
        results = {
            "incident_id": incident.incident_id,
            "possible_causes": [],
            "confidence": 0.0,
            "analysis_time": datetime.now().isoformat()
        }
        
        # 1. Анализ связанных аномалий
        anomaly_causes = self._analyze_anomalies(incident.anomalies)
        results["possible_causes"].extend(anomaly_causes)
        
        # 2. Анализ зависимостей сервисов
        dependency_causes = self._analyze_dependencies(incident.affected_services)
        results["possible_causes"].extend(dependency_causes)
        
        # 3. Сопоставление с известными паттернами
        pattern_matches = self._match_patterns(incident)
        results["possible_causes"].extend(pattern_matches)
        
        # 4. Корреляционный анализ
        correlation_causes = self._analyze_correlations(incident)
        results["possible_causes"].extend(correlation_causes)
        
        # Сортировка по уверенности
        results["possible_causes"].sort(key=lambda x: x["confidence"], reverse=True)
        
        if results["possible_causes"]:
            results["confidence"] = results["possible_causes"][0]["confidence"]
            results["root_cause"] = results["possible_causes"][0]
            
        return results
        
    def _analyze_anomalies(self, anomaly_ids: List[str]) -> List[Dict[str, Any]]:
        """Анализ аномалий"""
        causes = []
        
        # Поиск первой аномалии (потенциальная причина)
        anomalies = [a for a in self.anomaly_detector.anomalies 
                    if a.anomaly_id in anomaly_ids]
                    
        if not anomalies:
            return causes
            
        # Сортировка по времени
        anomalies.sort(key=lambda a: a.detected_at)
        
        first_anomaly = anomalies[0]
        
        causes.append({
            "type": "first_anomaly",
            "description": f"First anomaly detected in {first_anomaly.metric_name}",
            "metric": first_anomaly.metric_name,
            "anomaly_type": first_anomaly.anomaly_type.value,
            "confidence": 0.7,
            "timestamp": first_anomaly.detected_at.isoformat()
        })
        
        return causes
        
    def _analyze_dependencies(self, services: List[str]) -> List[Dict[str, Any]]:
        """Анализ зависимостей"""
        causes = []
        
        for service in services:
            dependencies = self.service_dependencies.get(service, [])
            
            for dep in dependencies:
                # Проверка аномалий в зависимостях
                dep_anomalies = [
                    a for a in self.anomaly_detector.anomalies
                    if dep in a.labels.get("service", "")
                    and not a.resolved
                ]
                
                if dep_anomalies:
                    causes.append({
                        "type": "dependency_failure",
                        "description": f"Anomalies detected in dependency: {dep}",
                        "service": dep,
                        "dependent": service,
                        "anomaly_count": len(dep_anomalies),
                        "confidence": 0.8
                    })
                    
        return causes
        
    def _match_patterns(self, incident: Incident) -> List[Dict[str, Any]]:
        """Сопоставление с паттернами"""
        matches = []
        
        for pattern in self.known_patterns:
            # Проверка соответствия паттерну
            match_score = self._calculate_pattern_match(incident, pattern)
            
            if match_score > 0.5:
                matches.append({
                    "type": "pattern_match",
                    "pattern_name": pattern.get("name", "Unknown"),
                    "description": pattern.get("description", ""),
                    "resolution": pattern.get("resolution", ""),
                    "confidence": match_score
                })
                
        return matches
        
    def _calculate_pattern_match(self, incident: Incident, 
                                  pattern: Dict[str, Any]) -> float:
        """Расчёт соответствия паттерну"""
        score = 0.0
        checks = 0
        
        # Проверка severity
        if "severity" in pattern:
            checks += 1
            if incident.severity.value == pattern["severity"]:
                score += 1
                
        # Проверка сервисов
        if "services" in pattern:
            checks += 1
            matches = len(set(incident.affected_services) & set(pattern["services"]))
            if matches > 0:
                score += matches / len(pattern["services"])
                
        # Проверка метрик
        if "metrics" in pattern:
            checks += 1
            anomaly_metrics = set()
            for aid in incident.anomalies:
                for a in self.anomaly_detector.anomalies:
                    if a.anomaly_id == aid:
                        anomaly_metrics.add(a.metric_name)
                        
            matches = len(anomaly_metrics & set(pattern["metrics"]))
            if matches > 0:
                score += matches / len(pattern["metrics"])
                
        return score / checks if checks > 0 else 0
        
    def _analyze_correlations(self, incident: Incident) -> List[Dict[str, Any]]:
        """Корреляционный анализ"""
        causes = []
        
        # Получение метрик из аномалий
        anomaly_metrics = set()
        for aid in incident.anomalies:
            for a in self.anomaly_detector.anomalies:
                if a.anomaly_id == aid:
                    anomaly_metrics.add(a.metric_name)
                    
        # Поиск коррелирующих метрик
        for metric in anomaly_metrics:
            for other_metric in self.anomaly_detector.time_series:
                if other_metric == metric:
                    continue
                    
                correlation = self.calculate_correlations(metric, other_metric)
                
                if abs(correlation) > 0.8:
                    causes.append({
                        "type": "correlation",
                        "description": f"Strong correlation between {metric} and {other_metric}",
                        "metric1": metric,
                        "metric2": other_metric,
                        "correlation": correlation,
                        "confidence": abs(correlation) * 0.7
                    })
                    
        return causes


class AutoRemediation:
    """Автоматическое исправление"""
    
    def __init__(self):
        self.remediation_rules: List[Dict[str, Any]] = []
        self.execution_history: List[Dict[str, Any]] = []
        self.enabled = True
        self.dry_run = False
        
    def add_rule(self, rule: Dict[str, Any]):
        """Добавление правила исправления"""
        self.remediation_rules.append({
            "id": f"rule_{uuid.uuid4().hex[:8]}",
            "condition": rule.get("condition", {}),
            "action": rule.get("action"),
            "params": rule.get("params", {}),
            "cooldown_minutes": rule.get("cooldown_minutes", 5),
            "max_executions": rule.get("max_executions", 3),
            "enabled": rule.get("enabled", True),
            "last_execution": None,
            "execution_count": 0
        })
        
    def evaluate(self, incident: Incident) -> List[Dict[str, Any]]:
        """Оценка применимых действий"""
        applicable_actions = []
        
        for rule in self.remediation_rules:
            if not rule["enabled"]:
                continue
                
            if self._check_condition(rule["condition"], incident):
                # Проверка cooldown
                if rule["last_execution"]:
                    elapsed = (datetime.now() - rule["last_execution"]).total_seconds() / 60
                    if elapsed < rule["cooldown_minutes"]:
                        continue
                        
                # Проверка лимита выполнений
                if rule["execution_count"] >= rule["max_executions"]:
                    continue
                    
                applicable_actions.append({
                    "rule_id": rule["id"],
                    "action": rule["action"],
                    "params": rule["params"],
                    "incident_id": incident.incident_id
                })
                
        return applicable_actions
        
    def _check_condition(self, condition: Dict[str, Any], 
                          incident: Incident) -> bool:
        """Проверка условия"""
        # Проверка severity
        if "severity" in condition:
            if isinstance(condition["severity"], list):
                if incident.severity.value not in condition["severity"]:
                    return False
            else:
                if incident.severity.value != condition["severity"]:
                    return False
                    
        # Проверка сервисов
        if "services" in condition:
            if not any(s in incident.affected_services for s in condition["services"]):
                return False
                
        # Проверка статуса
        if "status" in condition:
            if incident.status.value != condition["status"]:
                return False
                
        return True
        
    async def execute(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение действия"""
        if not self.enabled:
            return {"success": False, "reason": "Auto-remediation disabled"}
            
        action_type = RemediationAction(action["action"])
        params = action["params"]
        
        execution = {
            "action": action,
            "started_at": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "success": False,
            "result": None
        }
        
        try:
            if self.dry_run:
                result = {"dry_run": True, "would_execute": action_type.value}
            else:
                result = await self._execute_action(action_type, params)
                
            execution["success"] = True
            execution["result"] = result
            
            # Обновление правила
            for rule in self.remediation_rules:
                if rule["id"] == action.get("rule_id"):
                    rule["last_execution"] = datetime.now()
                    rule["execution_count"] += 1
                    break
                    
        except Exception as e:
            execution["success"] = False
            execution["error"] = str(e)
            
        execution["completed_at"] = datetime.now().isoformat()
        self.execution_history.append(execution)
        
        return execution
        
    async def _execute_action(self, action_type: RemediationAction,
                               params: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение конкретного действия"""
        # Симуляция действий
        await asyncio.sleep(0.5)
        
        if action_type == RemediationAction.SCALE_UP:
            return {
                "action": "scale_up",
                "service": params.get("service"),
                "from_replicas": params.get("current_replicas", 1),
                "to_replicas": params.get("current_replicas", 1) + params.get("increment", 1)
            }
            
        elif action_type == RemediationAction.RESTART_SERVICE:
            return {
                "action": "restart",
                "service": params.get("service"),
                "status": "restarted"
            }
            
        elif action_type == RemediationAction.ROLLBACK:
            return {
                "action": "rollback",
                "service": params.get("service"),
                "from_version": params.get("current_version"),
                "to_version": params.get("target_version")
            }
            
        elif action_type == RemediationAction.CLEAR_CACHE:
            return {
                "action": "clear_cache",
                "service": params.get("service"),
                "cache_cleared": True
            }
            
        return {"action": action_type.value, "executed": True}


class CapacityPlanner:
    """Планировщик ёмкости"""
    
    def __init__(self, predictive: PredictiveAnalytics):
        self.predictive = predictive
        self.resources: Dict[str, Dict[str, Any]] = {}
        self.thresholds: Dict[str, float] = {}
        
    def register_resource(self, resource_name: str, 
                          capacity: float,
                          unit: str = "units"):
        """Регистрация ресурса"""
        self.resources[resource_name] = {
            "name": resource_name,
            "capacity": capacity,
            "unit": unit,
            "registered_at": datetime.now().isoformat()
        }
        
    def set_threshold(self, resource_name: str, threshold: float):
        """Установка порога"""
        self.thresholds[resource_name] = threshold
        
    def forecast_capacity(self, resource_name: str) -> Optional[CapacityForecast]:
        """Прогноз ёмкости"""
        resource = self.resources.get(resource_name)
        if not resource:
            return None
            
        metric_name = f"{resource_name}_usage"
        ts = self.predictive.anomaly_detector.time_series.get(metric_name)
        
        if not ts or not ts.points:
            return None
            
        current_usage = ts.points[-1].value
        capacity = resource["capacity"]
        
        # Прогнозы
        forecast_7d = self.predictive.forecast(metric_name, periods=168)
        forecast_30d = self.predictive.forecast(metric_name, periods=720)
        
        max_7d = max(forecast_7d) if forecast_7d else current_usage
        max_30d = max(forecast_30d) if forecast_30d else current_usage
        
        # Дата исчерпания
        exhaustion_date = None
        threshold = self.thresholds.get(resource_name, capacity * 0.9)
        
        for i, value in enumerate(forecast_30d):
            if value >= threshold:
                exhaustion_date = datetime.now() + timedelta(hours=i)
                break
                
        # Рекомендации
        usage_ratio = current_usage / capacity
        
        if usage_ratio > 0.9:
            recommendation = "Critical: Immediate capacity increase needed"
            recommended_capacity = capacity * 1.5
        elif usage_ratio > 0.8:
            recommendation = "Warning: Plan capacity increase within 2 weeks"
            recommended_capacity = capacity * 1.3
        elif usage_ratio > 0.7:
            recommendation = "Monitor: Consider capacity increase within 1 month"
            recommended_capacity = capacity * 1.2
        else:
            recommendation = "Healthy: Current capacity is sufficient"
            recommended_capacity = capacity
            
        return CapacityForecast(
            resource_type=resource_name,
            current_usage=current_usage,
            current_capacity=capacity,
            forecast_7d=max_7d,
            forecast_30d=max_30d,
            exhaustion_date=exhaustion_date,
            recommended_capacity=recommended_capacity,
            recommendation=recommendation,
            confidence=0.8
        )


class IntelligentAlerting:
    """Интеллектуальные алерты"""
    
    def __init__(self, anomaly_detector: AnomalyDetector):
        self.anomaly_detector = anomaly_detector
        self.alert_rules: List[Dict[str, Any]] = []
        self.active_alerts: Dict[str, Dict[str, Any]] = {}
        self.suppression_rules: List[Dict[str, Any]] = []
        self.alert_history: List[Dict[str, Any]] = []
        
        # Группировка и дедупликация
        self.grouping_window_minutes = 5
        self.dedup_window_minutes = 15
        
    def add_rule(self, rule: Dict[str, Any]):
        """Добавление правила алерта"""
        self.alert_rules.append({
            "id": f"alert_rule_{uuid.uuid4().hex[:8]}",
            "name": rule.get("name", "Unnamed"),
            "condition": rule.get("condition", {}),
            "severity": rule.get("severity", "medium"),
            "message": rule.get("message", "Alert triggered"),
            "channels": rule.get("channels", ["default"]),
            "enabled": rule.get("enabled", True)
        })
        
    def add_suppression_rule(self, rule: Dict[str, Any]):
        """Добавление правила подавления"""
        self.suppression_rules.append({
            "id": f"suppress_{uuid.uuid4().hex[:8]}",
            "condition": rule.get("condition", {}),
            "duration_minutes": rule.get("duration_minutes", 60),
            "reason": rule.get("reason", "Manual suppression"),
            "created_at": datetime.now(),
            "enabled": True
        })
        
    def evaluate(self, anomaly: Anomaly) -> Optional[Dict[str, Any]]:
        """Оценка и создание алерта"""
        # Проверка подавления
        if self._is_suppressed(anomaly):
            return None
            
        # Проверка дедупликации
        existing_alert = self._find_duplicate(anomaly)
        if existing_alert:
            self._update_alert(existing_alert, anomaly)
            return None
            
        # Поиск подходящего правила
        for rule in self.alert_rules:
            if not rule["enabled"]:
                continue
                
            if self._matches_rule(anomaly, rule):
                alert = self._create_alert(anomaly, rule)
                self.active_alerts[alert["id"]] = alert
                self.alert_history.append(alert)
                return alert
                
        return None
        
    def _is_suppressed(self, anomaly: Anomaly) -> bool:
        """Проверка подавления"""
        now = datetime.now()
        
        for rule in self.suppression_rules:
            if not rule["enabled"]:
                continue
                
            # Проверка срока действия
            elapsed = (now - rule["created_at"]).total_seconds() / 60
            if elapsed > rule["duration_minutes"]:
                rule["enabled"] = False
                continue
                
            # Проверка условия
            condition = rule["condition"]
            
            if "metric" in condition:
                if anomaly.metric_name != condition["metric"]:
                    continue
                    
            if "severity" in condition:
                if anomaly.severity.value not in condition["severity"]:
                    continue
                    
            return True
            
        return False
        
    def _find_duplicate(self, anomaly: Anomaly) -> Optional[Dict[str, Any]]:
        """Поиск дубликата"""
        cutoff = datetime.now() - timedelta(minutes=self.dedup_window_minutes)
        
        for alert_id, alert in self.active_alerts.items():
            if datetime.fromisoformat(alert["created_at"]) < cutoff:
                continue
                
            if alert["metric"] == anomaly.metric_name:
                return alert
                
        return None
        
    def _update_alert(self, alert: Dict[str, Any], anomaly: Anomaly):
        """Обновление существующего алерта"""
        alert["occurrence_count"] = alert.get("occurrence_count", 1) + 1
        alert["last_occurrence"] = datetime.now().isoformat()
        
        # Эскалация severity если нужно
        if anomaly.severity.value == "critical" and alert["severity"] != "critical":
            alert["severity"] = "critical"
            alert["escalated"] = True
            
    def _matches_rule(self, anomaly: Anomaly, rule: Dict[str, Any]) -> bool:
        """Проверка соответствия правилу"""
        condition = rule["condition"]
        
        if "metric_pattern" in condition:
            pattern = condition["metric_pattern"]
            if not anomaly.metric_name.startswith(pattern.replace("*", "")):
                return False
                
        if "severity" in condition:
            if anomaly.severity.value not in condition["severity"]:
                return False
                
        if "anomaly_type" in condition:
            if anomaly.anomaly_type.value not in condition["anomaly_type"]:
                return False
                
        if "threshold" in condition:
            if anomaly.deviation < condition["threshold"]:
                return False
                
        return True
        
    def _create_alert(self, anomaly: Anomaly, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Создание алерта"""
        return {
            "id": f"alert_{uuid.uuid4().hex[:8]}",
            "rule_id": rule["id"],
            "rule_name": rule["name"],
            "metric": anomaly.metric_name,
            "severity": rule["severity"],
            "message": rule["message"].format(
                metric=anomaly.metric_name,
                value=anomaly.value,
                expected=anomaly.expected_value
            ),
            "anomaly_id": anomaly.anomaly_id,
            "anomaly_type": anomaly.anomaly_type.value,
            "value": anomaly.value,
            "expected_value": anomaly.expected_value,
            "deviation": anomaly.deviation,
            "channels": rule["channels"],
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "occurrence_count": 1
        }
        
    def resolve_alert(self, alert_id: str, resolution: str = ""):
        """Разрешение алерта"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert["status"] = "resolved"
            alert["resolved_at"] = datetime.now().isoformat()
            alert["resolution"] = resolution
            del self.active_alerts[alert_id]
            
    def get_active_alerts(self, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """Получение активных алертов"""
        alerts = list(self.active_alerts.values())
        
        if severity:
            alerts = [a for a in alerts if a["severity"] == severity]
            
        return sorted(alerts, key=lambda a: a["created_at"], reverse=True)


class AIOpsEngine:
    """AIOps движок"""
    
    def __init__(self):
        self.anomaly_detector = AnomalyDetector()
        self.predictive = PredictiveAnalytics(self.anomaly_detector)
        self.root_cause = RootCauseAnalyzer(self.anomaly_detector)
        self.auto_remediation = AutoRemediation()
        self.capacity_planner = CapacityPlanner(self.predictive)
        self.alerting = IntelligentAlerting(self.anomaly_detector)
        
        self.incidents: Dict[str, Incident] = {}
        self.insights: List[PerformanceInsight] = []
        
    def initialize(self):
        """Инициализация движка"""
        # Добавление стандартных правил алертов
        self.alerting.add_rule({
            "name": "High CPU",
            "condition": {
                "metric_pattern": "cpu_*",
                "severity": ["critical", "high"]
            },
            "severity": "high",
            "message": "High CPU usage detected on {metric}: {value}%"
        })
        
        self.alerting.add_rule({
            "name": "Memory Critical",
            "condition": {
                "metric_pattern": "memory_*",
                "anomaly_type": ["spike"],
                "threshold": 4.0
            },
            "severity": "critical",
            "message": "Critical memory spike on {metric}"
        })
        
        # Добавление правил auto-remediation
        self.auto_remediation.add_rule({
            "condition": {
                "severity": ["critical"],
                "services": ["api-gateway"]
            },
            "action": "scale_up",
            "params": {"service": "api-gateway", "increment": 2},
            "cooldown_minutes": 10
        })
        
        self.auto_remediation.add_rule({
            "condition": {
                "severity": ["high", "critical"]
            },
            "action": "clear_cache",
            "params": {},
            "cooldown_minutes": 15
        })
        
        # Добавление известных паттернов для RCA
        self.root_cause.add_known_pattern({
            "name": "Database Connection Exhaustion",
            "description": "Database connection pool exhausted",
            "metrics": ["db_connections", "db_latency"],
            "services": ["database", "api-service"],
            "resolution": "Increase connection pool size or optimize queries"
        })
        
    def ingest_metric(self, metric_name: str, value: float,
                      labels: Optional[Dict[str, str]] = None):
        """Приём метрики"""
        self.anomaly_detector.record_metric(metric_name, value, labels)
        
        # Проверка новых аномалий для алертинга
        recent_anomalies = self.anomaly_detector.get_anomalies()
        if recent_anomalies:
            latest = recent_anomalies[0]
            if (datetime.now() - latest.detected_at).seconds < 5:
                self.alerting.evaluate(latest)
                
    def create_incident(self, title: str, description: str,
                        severity: AlertSeverity,
                        affected_services: List[str]) -> Incident:
        """Создание инцидента"""
        # Поиск связанных аномалий
        related_anomalies = []
        for service in affected_services:
            anomalies = [
                a.anomaly_id for a in self.anomaly_detector.anomalies
                if service in a.labels.get("service", "") and not a.resolved
            ]
            related_anomalies.extend(anomalies)
            
        incident = Incident(
            incident_id=f"inc_{uuid.uuid4().hex[:8]}",
            title=title,
            description=description,
            severity=severity,
            anomalies=related_anomalies,
            affected_services=affected_services
        )
        
        # Добавление в timeline
        incident.timeline.append({
            "timestamp": datetime.now().isoformat(),
            "event": "incident_created",
            "description": "Incident created"
        })
        
        self.incidents[incident.incident_id] = incident
        
        return incident
        
    async def analyze_incident(self, incident_id: str) -> Dict[str, Any]:
        """Анализ инцидента"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return {"error": "Incident not found"}
            
        incident.status = IncidentStatus.INVESTIGATING
        incident.timeline.append({
            "timestamp": datetime.now().isoformat(),
            "event": "analysis_started",
            "description": "Root cause analysis started"
        })
        
        # RCA
        rca_result = self.root_cause.analyze(incident)
        
        if rca_result.get("root_cause"):
            incident.root_cause = rca_result["root_cause"]["description"]
            incident.root_cause_confidence = rca_result["confidence"]
            incident.status = IncidentStatus.IDENTIFIED
            
            incident.timeline.append({
                "timestamp": datetime.now().isoformat(),
                "event": "root_cause_identified",
                "description": f"Root cause: {incident.root_cause}"
            })
            
        # Auto-remediation
        if incident.auto_remediation_enabled:
            actions = self.auto_remediation.evaluate(incident)
            
            for action in actions:
                incident.status = IncidentStatus.REMEDIATING
                result = await self.auto_remediation.execute(action)
                
                incident.remediation_actions.append({
                    "action": action,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                })
                
                incident.timeline.append({
                    "timestamp": datetime.now().isoformat(),
                    "event": "remediation_executed",
                    "description": f"Executed: {action['action']}"
                })
                
        return {
            "incident_id": incident_id,
            "status": incident.status.value,
            "root_cause": incident.root_cause,
            "confidence": incident.root_cause_confidence,
            "remediation_actions": len(incident.remediation_actions),
            "rca_details": rca_result
        }
        
    def get_insights(self) -> List[PerformanceInsight]:
        """Получение инсайтов"""
        insights = []
        
        # Анализ трендов
        for metric_name, ts in self.anomaly_detector.time_series.items():
            trend = self.predictive.get_trend(metric_name)
            
            if trend["trend"] == "increasing" and "cpu" in metric_name.lower():
                insights.append(PerformanceInsight(
                    insight_id=f"insight_{uuid.uuid4().hex[:8]}",
                    category="resource",
                    title=f"Increasing CPU trend: {metric_name}",
                    description="CPU usage is trending upward",
                    impact="May lead to performance degradation",
                    affected_metrics=[metric_name],
                    improvement_potential=15.0,
                    recommendations=[
                        {"action": "optimize_code", "description": "Review and optimize CPU-intensive code"},
                        {"action": "scale_horizontal", "description": "Consider horizontal scaling"}
                    ],
                    priority=2
                ))
                
        # Анализ аномалий
        critical_anomalies = self.anomaly_detector.get_anomalies(severity=AlertSeverity.CRITICAL)
        if len(critical_anomalies) > 3:
            insights.append(PerformanceInsight(
                insight_id=f"insight_{uuid.uuid4().hex[:8]}",
                category="stability",
                title="High frequency of critical anomalies",
                description=f"{len(critical_anomalies)} critical anomalies detected",
                impact="System stability at risk",
                improvement_potential=30.0,
                recommendations=[
                    {"action": "investigate", "description": "Investigate root causes"},
                    {"action": "add_monitoring", "description": "Add more granular monitoring"}
                ],
                priority=1
            ))
            
        self.insights = insights
        return insights
        
    def get_dashboard(self) -> Dict[str, Any]:
        """Получение данных дашборда"""
        # Активные алерты
        active_alerts = self.alerting.get_active_alerts()
        
        # Открытые инциденты
        open_incidents = [
            i for i in self.incidents.values()
            if i.status not in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]
        ]
        
        # Недавние аномалии
        recent_anomalies = self.anomaly_detector.get_anomalies()[:10]
        
        # Статистика
        total_metrics = len(self.anomaly_detector.time_series)
        total_anomalies = len(self.anomaly_detector.anomalies)
        
        return {
            "summary": {
                "total_metrics": total_metrics,
                "total_anomalies": total_anomalies,
                "active_alerts": len(active_alerts),
                "open_incidents": len(open_incidents),
                "insights_count": len(self.insights)
            },
            "alerts": {
                "critical": len([a for a in active_alerts if a["severity"] == "critical"]),
                "high": len([a for a in active_alerts if a["severity"] == "high"]),
                "medium": len([a for a in active_alerts if a["severity"] == "medium"]),
                "low": len([a for a in active_alerts if a["severity"] == "low"])
            },
            "incidents": {
                "total": len(self.incidents),
                "open": len(open_incidents),
                "by_severity": {
                    s.value: len([i for i in open_incidents if i.severity == s])
                    for s in AlertSeverity
                }
            },
            "recent_anomalies": [
                {
                    "id": a.anomaly_id,
                    "metric": a.metric_name,
                    "type": a.anomaly_type.value,
                    "severity": a.severity.value,
                    "detected_at": a.detected_at.isoformat()
                }
                for a in recent_anomalies
            ],
            "auto_remediation": {
                "enabled": self.auto_remediation.enabled,
                "executions_today": len([
                    e for e in self.auto_remediation.execution_history
                    if datetime.fromisoformat(e["started_at"]).date() == datetime.now().date()
                ])
            }
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 37: Intelligent Operations (AIOps)")
    print("=" * 60)
    
    async def demo():
        # Создание AIOps движка
        aiops = AIOpsEngine()
        aiops.initialize()
        
        print("✓ AIOps Engine initialized")
        
        # Симуляция метрик
        print("\n📊 Simulating metrics...")
        
        # Нормальные метрики
        for i in range(100):
            aiops.ingest_metric("cpu_usage", 45 + random.gauss(0, 5), {"service": "api"})
            aiops.ingest_metric("memory_usage", 60 + random.gauss(0, 3), {"service": "api"})
            aiops.ingest_metric("request_latency", 100 + random.gauss(0, 10), {"service": "api"})
            
        # Аномальные метрики
        aiops.ingest_metric("cpu_usage", 95, {"service": "api"})
        aiops.ingest_metric("memory_usage", 92, {"service": "api"})
        
        print(f"✓ Ingested metrics, detected {len(aiops.anomaly_detector.anomalies)} anomalies")
        
        # Создание инцидента
        incident = aiops.create_incident(
            title="High Resource Usage",
            description="API service experiencing high CPU and memory usage",
            severity=AlertSeverity.HIGH,
            affected_services=["api", "database"]
        )
        print(f"✓ Created incident: {incident.incident_id}")
        
        # Добавление зависимостей для RCA
        aiops.root_cause.add_service_dependency("api", ["database", "cache"])
        aiops.root_cause.add_service_dependency("frontend", ["api"])
        
        # Анализ инцидента
        analysis = await aiops.analyze_incident(incident.incident_id)
        print(f"✓ Analyzed incident:")
        print(f"   Status: {analysis['status']}")
        print(f"   Root Cause: {analysis.get('root_cause', 'Not identified')}")
        print(f"   Confidence: {analysis['confidence']:.1%}")
        print(f"   Remediation Actions: {analysis['remediation_actions']}")
        
        # Capacity Planning
        aiops.capacity_planner.register_resource("compute", 100, "vCPUs")
        aiops.capacity_planner.set_threshold("compute", 90)
        
        # Добавление метрик использования
        for i in range(50):
            aiops.ingest_metric("compute_usage", 70 + i * 0.3 + random.gauss(0, 2))
            
        forecast = aiops.capacity_planner.forecast_capacity("compute")
        if forecast:
            print(f"\n📈 Capacity Forecast:")
            print(f"   Current Usage: {forecast.current_usage:.1f}/{forecast.current_capacity}")
            print(f"   7-day forecast: {forecast.forecast_7d:.1f}")
            print(f"   Recommendation: {forecast.recommendation}")
            
        # Получение инсайтов
        insights = aiops.get_insights()
        print(f"\n💡 Performance Insights: {len(insights)}")
        for insight in insights[:3]:
            print(f"   - [{insight.category}] {insight.title}")
            
        # Дашборд
        dashboard = aiops.get_dashboard()
        print(f"\n📊 Dashboard:")
        print(f"   Total Metrics: {dashboard['summary']['total_metrics']}")
        print(f"   Total Anomalies: {dashboard['summary']['total_anomalies']}")
        print(f"   Active Alerts: {dashboard['summary']['active_alerts']}")
        print(f"   Open Incidents: {dashboard['summary']['open_incidents']}")
        
        print(f"\n   Alerts by Severity:")
        for severity, count in dashboard['alerts'].items():
            if count > 0:
                print(f"      {severity}: {count}")
                
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("AIOps Engine initialized successfully!")
    print("=" * 60)
