#!/usr/bin/env python3
"""
Advanced Monitoring Hub v12.0
Centralized monitoring with ML predictions, anomaly detection, and auto-remediation
Aggregates data from Prometheus, Elasticsearch, APM, and custom sources
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import sqlite3
from pathlib import Path
import yaml

# Scientific computing
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import joblib

# Time series
try:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    from statsmodels.tsa.arima.model import ARIMA
except ImportError:
    print("Warning: statsmodels not installed")

# Monitoring backends
try:
    from prometheus_api_client import PrometheusConnect
    from elasticsearch import Elasticsearch
    import redis
    import psycopg2
except ImportError:
    print("Warning: monitoring libraries not installed")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
MONITORING_DB = '/var/lib/monitoring/hub.db'
MONITORING_CONFIG = '/etc/monitoring/hub.yaml'
MONITORING_MODELS = '/var/lib/monitoring/models/'
MONITORING_LOGS = '/var/log/monitoring/'

# Thresholds
ANOMALY_THRESHOLD = 0.95  # 95th percentile
PREDICTION_CONFIDENCE_MIN = 0.70
ALERT_COOLDOWN_SECONDS = 300

# Create directories
for directory in [os.path.dirname(MONITORING_DB),
                  os.path.dirname(MONITORING_CONFIG),
                  MONITORING_MODELS,
                  MONITORING_LOGS]:
    Path(directory).mkdir(parents=True, exist_ok=True)

################################################################################
# Data Models
################################################################################

class MetricType(Enum):
    """Types of metrics"""
    GAUGE = "gauge"
    COUNTER = "counter"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class PredictionType(Enum):
    """Types of predictions"""
    CAPACITY = "capacity"
    OUTAGE = "outage"
    ANOMALY = "anomaly"
    PERFORMANCE = "performance"

@dataclass
class Metric:
    """Time-series metric"""
    metric_id: str
    name: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    source: str = "unknown"

@dataclass
class Alert:
    """Monitoring alert"""
    alert_id: str
    severity: AlertSeverity
    title: str
    description: str
    source_metric: str
    threshold_value: float
    actual_value: float
    component: str
    namespace: str
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolved_at: Optional[datetime] = None

@dataclass
class Prediction:
    """ML prediction"""
    prediction_id: str
    prediction_type: PredictionType
    target_metric: str
    predicted_value: float
    confidence: float
    time_horizon_minutes: int
    reasoning: str
    recommended_actions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class Anomaly:
    """Detected anomaly"""
    anomaly_id: str
    metric_name: str
    anomaly_score: float
    expected_value: float
    actual_value: float
    deviation_percent: float
    component: str
    severity: AlertSeverity
    timestamp: datetime = field(default_factory=datetime.now)

################################################################################
# Database Manager
################################################################################

class MonitoringDatabase:
    """Database for monitoring data"""
    
    def __init__(self, db_path: str = MONITORING_DB):
        self.db_path = db_path
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.conn.cursor()
        
        # Metrics table (time-series data)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                metric_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                value REAL NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                labels_json TEXT,
                source TEXT,
                component TEXT,
                namespace TEXT
            )
        ''')
        
        # Aggregated metrics (pre-computed for performance)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics_aggregated (
                agg_id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                component TEXT NOT NULL,
                namespace TEXT NOT NULL,
                time_bucket TIMESTAMP NOT NULL,
                avg_value REAL,
                min_value REAL,
                max_value REAL,
                p50_value REAL,
                p95_value REAL,
                p99_value REAL,
                sample_count INTEGER,
                UNIQUE(metric_name, component, namespace, time_bucket)
            )
        ''')
        
        # Alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                alert_id TEXT PRIMARY KEY,
                severity TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                source_metric TEXT NOT NULL,
                threshold_value REAL NOT NULL,
                actual_value REAL NOT NULL,
                component TEXT NOT NULL,
                namespace TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved INTEGER DEFAULT 0,
                resolved_at TIMESTAMP,
                acknowledged INTEGER DEFAULT 0,
                acknowledged_by TEXT,
                acknowledged_at TIMESTAMP
            )
        ''')
        
        # Predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                prediction_id TEXT PRIMARY KEY,
                prediction_type TEXT NOT NULL,
                target_metric TEXT NOT NULL,
                predicted_value REAL NOT NULL,
                confidence REAL NOT NULL,
                time_horizon_minutes INTEGER NOT NULL,
                reasoning TEXT,
                recommended_actions_json TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                actual_value REAL,
                accuracy REAL
            )
        ''')
        
        # Anomalies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anomalies (
                anomaly_id TEXT PRIMARY KEY,
                metric_name TEXT NOT NULL,
                anomaly_score REAL NOT NULL,
                expected_value REAL NOT NULL,
                actual_value REAL NOT NULL,
                deviation_percent REAL NOT NULL,
                component TEXT NOT NULL,
                severity TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                investigated INTEGER DEFAULT 0,
                root_cause TEXT
            )
        ''')
        
        # Baselines table (normal behavior profiles)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS baselines (
                baseline_id TEXT PRIMARY KEY,
                metric_name TEXT NOT NULL,
                component TEXT NOT NULL,
                hour_of_day INTEGER NOT NULL,
                day_of_week INTEGER NOT NULL,
                avg_value REAL NOT NULL,
                std_value REAL NOT NULL,
                min_value REAL NOT NULL,
                max_value REAL NOT NULL,
                sample_count INTEGER NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(metric_name, component, hour_of_day, day_of_week)
            )
        ''')
        
        # Dashboard configurations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dashboards (
                dashboard_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                config_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_component ON metrics(component)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity, resolved)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_anomalies_timestamp ON anomalies(timestamp DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON predictions(timestamp DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_agg_bucket ON metrics_aggregated(time_bucket DESC)')
        
        self.conn.commit()
        logger.info(f"Monitoring database initialized: {db_path}")
    
    def save_metric(self, metric: Metric):
        """Save metric to database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO metrics 
            (metric_id, name, metric_type, value, timestamp, labels_json, source, component, namespace)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metric.metric_id,
            metric.name,
            metric.metric_type.value,
            metric.value,
            metric.timestamp.isoformat(),
            json.dumps(metric.labels),
            metric.source,
            metric.labels.get('component', 'unknown'),
            metric.labels.get('namespace', 'default')
        ))
        self.conn.commit()
    
    def save_alert(self, alert: Alert):
        """Save alert to database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO alerts 
            (alert_id, severity, title, description, source_metric, threshold_value, 
             actual_value, component, namespace, timestamp, resolved)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            alert.alert_id,
            alert.severity.value,
            alert.title,
            alert.description,
            alert.source_metric,
            alert.threshold_value,
            alert.actual_value,
            alert.component,
            alert.namespace,
            alert.timestamp.isoformat(),
            1 if alert.resolved else 0
        ))
        self.conn.commit()
    
    def save_prediction(self, prediction: Prediction):
        """Save prediction to database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO predictions 
            (prediction_id, prediction_type, target_metric, predicted_value, confidence,
             time_horizon_minutes, reasoning, recommended_actions_json, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            prediction.prediction_id,
            prediction.prediction_type.value,
            prediction.target_metric,
            prediction.predicted_value,
            prediction.confidence,
            prediction.time_horizon_minutes,
            prediction.reasoning,
            json.dumps(prediction.recommended_actions),
            prediction.timestamp.isoformat()
        ))
        self.conn.commit()
    
    def save_anomaly(self, anomaly: Anomaly):
        """Save anomaly to database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO anomalies 
            (anomaly_id, metric_name, anomaly_score, expected_value, actual_value,
             deviation_percent, component, severity, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            anomaly.anomaly_id,
            anomaly.metric_name,
            anomaly.anomaly_score,
            anomaly.expected_value,
            anomaly.actual_value,
            anomaly.deviation_percent,
            anomaly.component,
            anomaly.severity.value,
            anomaly.timestamp.isoformat()
        ))
        self.conn.commit()
    
    def get_metrics(self, metric_name: str, component: str, 
                   start_time: datetime, end_time: datetime) -> List[Metric]:
        """Query metrics by name and time range"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT metric_id, name, metric_type, value, timestamp, labels_json, source
            FROM metrics
            WHERE name = ? AND component = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
        ''', (metric_name, component, start_time.isoformat(), end_time.isoformat()))
        
        metrics = []
        for row in cursor.fetchall():
            metrics.append(Metric(
                metric_id=row[0],
                name=row[1],
                metric_type=MetricType(row[2]),
                value=row[3],
                timestamp=datetime.fromisoformat(row[4]),
                labels=json.loads(row[5]) if row[5] else {},
                source=row[6]
            ))
        
        return metrics
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get active (unresolved) alerts"""
        cursor = self.conn.cursor()
        
        query = 'SELECT * FROM alerts WHERE resolved = 0'
        params = []
        
        if severity:
            query += ' AND severity = ?'
            params.append(severity.value)
        
        query += ' ORDER BY timestamp DESC'
        
        cursor.execute(query, params)
        
        alerts = []
        for row in cursor.fetchall():
            alerts.append(Alert(
                alert_id=row[0],
                severity=AlertSeverity(row[1]),
                title=row[2],
                description=row[3],
                source_metric=row[4],
                threshold_value=row[5],
                actual_value=row[6],
                component=row[7],
                namespace=row[8],
                timestamp=datetime.fromisoformat(row[9]),
                resolved=bool(row[10]),
                resolved_at=datetime.fromisoformat(row[11]) if row[11] else None
            ))
        
        return alerts
    
    def aggregate_metrics(self, time_bucket_minutes: int = 5):
        """Pre-aggregate metrics for performance"""
        cursor = self.conn.cursor()
        
        # Get time range for aggregation
        cursor.execute('''
            SELECT MIN(timestamp), MAX(timestamp)
            FROM metrics
            WHERE timestamp > (
                SELECT COALESCE(MAX(time_bucket), '2020-01-01')
                FROM metrics_aggregated
            )
        ''')
        
        row = cursor.fetchone()
        if not row[0] or not row[1]:
            return
        
        start_time = datetime.fromisoformat(row[0])
        end_time = datetime.fromisoformat(row[1])
        
        # Aggregate by time buckets
        current_time = start_time
        while current_time <= end_time:
            bucket_end = current_time + timedelta(minutes=time_bucket_minutes)
            
            cursor.execute('''
                INSERT OR REPLACE INTO metrics_aggregated
                (metric_name, component, namespace, time_bucket, 
                 avg_value, min_value, max_value, sample_count)
                SELECT 
                    name,
                    component,
                    namespace,
                    ?,
                    AVG(value),
                    MIN(value),
                    MAX(value),
                    COUNT(*)
                FROM metrics
                WHERE timestamp BETWEEN ? AND ?
                GROUP BY name, component, namespace
            ''', (current_time.isoformat(), current_time.isoformat(), bucket_end.isoformat()))
            
            current_time = bucket_end
        
        self.conn.commit()
        logger.info("Metrics aggregated successfully")

################################################################################
# Data Collectors
################################################################################

class PrometheusCollector:
    """Collect metrics from Prometheus"""
    
    def __init__(self, prometheus_url: str = 'http://localhost:9090'):
        self.prometheus_url = prometheus_url
        self.client = None
        
        try:
            self.client = PrometheusConnect(url=prometheus_url, disable_ssl=True)
            logger.info(f"Connected to Prometheus: {prometheus_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Prometheus: {e}")
    
    async def collect_metrics(self, queries: List[Dict[str, str]]) -> List[Metric]:
        """Collect metrics from Prometheus"""
        metrics = []
        
        if not self.client:
            return metrics
        
        for query_config in queries:
            query = query_config['query']
            metric_name = query_config['name']
            
            try:
                result = self.client.custom_query(query=query)
                
                for item in result:
                    metric_value = float(item['value'][1])
                    labels = item['metric']
                    
                    metric = Metric(
                        metric_id=f"prom-{metric_name}-{datetime.now().timestamp()}",
                        name=metric_name,
                        metric_type=MetricType.GAUGE,
                        value=metric_value,
                        timestamp=datetime.now(),
                        labels=labels,
                        source='prometheus'
                    )
                    metrics.append(metric)
            
            except Exception as e:
                logger.error(f"Failed to query Prometheus: {query} - {e}")
        
        return metrics

class ElasticsearchCollector:
    """Collect metrics from Elasticsearch"""
    
    def __init__(self, elasticsearch_url: str = 'http://localhost:9200'):
        self.elasticsearch_url = elasticsearch_url
        self.client = None
        
        try:
            self.client = Elasticsearch([elasticsearch_url])
            logger.info(f"Connected to Elasticsearch: {elasticsearch_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {e}")
    
    async def collect_log_metrics(self) -> List[Metric]:
        """Collect metrics from logs"""
        metrics = []
        
        if not self.client:
            return metrics
        
        # Example: Count errors in last 5 minutes
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"level": "error"}},
                        {"range": {"@timestamp": {"gte": "now-5m"}}}
                    ]
                }
            },
            "aggs": {
                "by_service": {
                    "terms": {"field": "service.keyword"}
                }
            }
        }
        
        try:
            result = self.client.search(index="logs-*", body=query)
            
            for bucket in result['aggregations']['by_service']['buckets']:
                service = bucket['key']
                count = bucket['doc_count']
                
                metric = Metric(
                    metric_id=f"es-errors-{service}-{datetime.now().timestamp()}",
                    name="error_count",
                    metric_type=MetricType.COUNTER,
                    value=count,
                    timestamp=datetime.now(),
                    labels={'service': service},
                    source='elasticsearch'
                )
                metrics.append(metric)
        
        except Exception as e:
            logger.error(f"Failed to query Elasticsearch: {e}")
        
        return metrics

################################################################################
# ML Analytics Engine
################################################################################

class MLAnalyticsEngine:
    """Machine learning for monitoring analytics"""
    
    def __init__(self, models_dir: str = MONITORING_MODELS):
        self.models_dir = models_dir
        self.anomaly_detector = IsolationForest(contamination=0.05, random_state=42)
        self.capacity_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        
        self._load_models()
    
    def _load_models(self):
        """Load existing models"""
        try:
            self.anomaly_detector = joblib.load(f'{self.models_dir}/anomaly_detector.pkl')
            self.capacity_predictor = joblib.load(f'{self.models_dir}/capacity_predictor.pkl')
            self.scaler = joblib.load(f'{self.models_dir}/scaler.pkl')
            logger.info("Loaded ML models")
        except FileNotFoundError:
            logger.info("No existing models found, will train on first run")
    
    def detect_anomalies(self, metrics: List[Metric], baseline: Dict[str, float]) -> List[Anomaly]:
        """Detect anomalies using Isolation Forest"""
        anomalies = []
        
        if len(metrics) < 10:
            return anomalies
        
        # Prepare features
        X = np.array([[m.value] for m in metrics])
        
        # Fit and predict
        predictions = self.anomaly_detector.fit_predict(X)
        scores = self.anomaly_detector.score_samples(X)
        
        for i, (metric, prediction, score) in enumerate(zip(metrics, predictions, scores)):
            if prediction == -1:  # Anomaly detected
                expected = baseline.get(metric.name, metric.value)
                deviation = abs(metric.value - expected) / (expected + 1e-9) * 100
                
                severity = AlertSeverity.WARNING
                if deviation > 50:
                    severity = AlertSeverity.CRITICAL
                elif deviation > 100:
                    severity = AlertSeverity.EMERGENCY
                
                anomaly = Anomaly(
                    anomaly_id=f"anom-{metric.metric_id}",
                    metric_name=metric.name,
                    anomaly_score=abs(score),
                    expected_value=expected,
                    actual_value=metric.value,
                    deviation_percent=deviation,
                    component=metric.labels.get('component', 'unknown'),
                    severity=severity,
                    timestamp=metric.timestamp
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    def predict_capacity(self, historical_metrics: List[Metric], 
                        horizon_hours: int = 24) -> Prediction:
        """Predict future capacity requirements"""
        
        if len(historical_metrics) < 100:
            # Not enough data for prediction
            return None
        
        # Prepare time series
        df = pd.DataFrame([
            {'timestamp': m.timestamp, 'value': m.value} 
            for m in historical_metrics
        ])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp').sort_index()
        df = df.resample('5T').mean().fillna(method='ffill')
        
        # Use exponential smoothing for prediction
        try:
            model = ExponentialSmoothing(
                df['value'],
                trend='add',
                seasonal='add',
                seasonal_periods=12  # 1 hour with 5-min intervals
            )
            fitted = model.fit()
            
            # Predict future values
            forecast_steps = horizon_hours * 12  # 5-min intervals
            forecast = fitted.forecast(steps=forecast_steps)
            
            predicted_max = forecast.max()
            confidence = 0.80  # TODO: Calculate based on model performance
            
            # Determine recommended actions
            current_max = df['value'].tail(12).max()  # Last hour max
            growth_rate = (predicted_max - current_max) / (current_max + 1e-9)
            
            recommended_actions = []
            if growth_rate > 0.50:  # >50% growth expected
                recommended_actions.append("Scale up resources immediately")
                recommended_actions.append(f"Add capacity: {growth_rate*100:.0f}% increase needed")
            elif growth_rate > 0.20:
                recommended_actions.append("Plan capacity increase")
                recommended_actions.append("Monitor closely for next 6 hours")
            
            reasoning = f"Historical trend analysis over {len(historical_metrics)} data points. "
            reasoning += f"Current max: {current_max:.2f}, Predicted max: {predicted_max:.2f}. "
            reasoning += f"Growth rate: {growth_rate*100:.1f}%"
            
            prediction = Prediction(
                prediction_id=f"pred-capacity-{datetime.now().timestamp()}",
                prediction_type=PredictionType.CAPACITY,
                target_metric=historical_metrics[0].name,
                predicted_value=predicted_max,
                confidence=confidence,
                time_horizon_minutes=horizon_hours * 60,
                reasoning=reasoning,
                recommended_actions=recommended_actions
            )
            
            return prediction
        
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return None
    
    def cluster_metrics(self, metrics: List[Metric]) -> Dict[str, List[Metric]]:
        """Cluster similar metrics using DBSCAN"""
        
        if len(metrics) < 10:
            return {'cluster_0': metrics}
        
        # Prepare features
        X = np.array([[m.value] for m in metrics])
        X_scaled = self.scaler.fit_transform(X)
        
        # Cluster
        clustering = DBSCAN(eps=0.3, min_samples=3)
        labels = clustering.fit_predict(X_scaled)
        
        # Group by cluster
        clusters = {}
        for metric, label in zip(metrics, labels):
            cluster_name = f"cluster_{label}"
            if cluster_name not in clusters:
                clusters[cluster_name] = []
            clusters[cluster_name].append(metric)
        
        return clusters

################################################################################
# Alert Manager
################################################################################

class AlertManager:
    """Manage alerts and notifications"""
    
    def __init__(self, db: MonitoringDatabase):
        self.db = db
        self.alert_cooldowns = {}  # Track recent alerts to avoid spam
    
    def evaluate_thresholds(self, metrics: List[Metric], 
                           thresholds: Dict[str, Dict]) -> List[Alert]:
        """Evaluate metrics against thresholds"""
        alerts = []
        
        for metric in metrics:
            if metric.name not in thresholds:
                continue
            
            threshold_config = thresholds[metric.name]
            
            # Check cooldown
            cooldown_key = f"{metric.name}-{metric.labels.get('component', 'default')}"
            if cooldown_key in self.alert_cooldowns:
                last_alert = self.alert_cooldowns[cooldown_key]
                if (datetime.now() - last_alert).total_seconds() < ALERT_COOLDOWN_SECONDS:
                    continue
            
            # Evaluate threshold
            if 'critical' in threshold_config and metric.value > threshold_config['critical']:
                alert = self._create_alert(metric, threshold_config['critical'], 
                                           AlertSeverity.CRITICAL)
                alerts.append(alert)
                self.alert_cooldowns[cooldown_key] = datetime.now()
            
            elif 'warning' in threshold_config and metric.value > threshold_config['warning']:
                alert = self._create_alert(metric, threshold_config['warning'], 
                                           AlertSeverity.WARNING)
                alerts.append(alert)
                self.alert_cooldowns[cooldown_key] = datetime.now()
        
        return alerts
    
    def _create_alert(self, metric: Metric, threshold: float, 
                     severity: AlertSeverity) -> Alert:
        """Create alert from metric"""
        
        title = f"{severity.value.upper()}: {metric.name} exceeded threshold"
        description = f"Metric '{metric.name}' value {metric.value:.2f} exceeds threshold {threshold:.2f}"
        
        alert = Alert(
            alert_id=f"alert-{metric.metric_id}",
            severity=severity,
            title=title,
            description=description,
            source_metric=metric.name,
            threshold_value=threshold,
            actual_value=metric.value,
            component=metric.labels.get('component', 'unknown'),
            namespace=metric.labels.get('namespace', 'default')
        )
        
        return alert
    
    async def send_notifications(self, alerts: List[Alert]):
        """Send alert notifications"""
        for alert in alerts:
            # Send to configured channels (Slack, Email, Telegram, etc.)
            logger.warning(f"ALERT: {alert.title} - {alert.description}")
            
            # Save to database
            self.db.save_alert(alert)

################################################################################
# Monitoring Hub
################################################################################

class AdvancedMonitoringHub:
    """Main monitoring hub orchestrator"""
    
    def __init__(self):
        self.db = MonitoringDatabase()
        self.ml_engine = MLAnalyticsEngine()
        self.alert_manager = AlertManager(self.db)
        
        # Data collectors
        self.prometheus = PrometheusCollector()
        self.elasticsearch = ElasticsearchCollector()
        
        self.running = False
        
        # Load configuration
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load monitoring configuration"""
        default_config = {
            'collection_interval_seconds': 60,
            'aggregation_interval_minutes': 5,
            'prediction_interval_hours': 1,
            'prometheus_queries': [
                {
                    'name': 'cpu_usage',
                    'query': 'rate(container_cpu_usage_seconds_total[5m])'
                },
                {
                    'name': 'memory_usage',
                    'query': 'container_memory_usage_bytes / container_spec_memory_limit_bytes'
                },
                {
                    'name': 'request_rate',
                    'query': 'rate(http_requests_total[5m])'
                }
            ],
            'thresholds': {
                'cpu_usage': {'warning': 0.80, 'critical': 0.90},
                'memory_usage': {'warning': 0.80, 'critical': 0.90},
                'error_rate': {'warning': 0.05, 'critical': 0.10},
                'latency_p95': {'warning': 500, 'critical': 1000}
            }
        }
        
        if os.path.exists(MONITORING_CONFIG):
            with open(MONITORING_CONFIG, 'r') as f:
                return yaml.safe_load(f)
        else:
            # Create default config
            with open(MONITORING_CONFIG, 'w') as f:
                yaml.dump(default_config, f)
            return default_config
    
    async def start(self):
        """Start monitoring hub"""
        logger.info("🚀 Starting Advanced Monitoring Hub v12.0")
        self.running = True
        
        # Start background tasks
        tasks = [
            self._metrics_collection_loop(),
            self._anomaly_detection_loop(),
            self._prediction_loop(),
            self._aggregation_loop()
        ]
        
        await asyncio.gather(*tasks)
    
    async def _metrics_collection_loop(self):
        """Collect metrics from all sources"""
        while self.running:
            try:
                # Collect from Prometheus
                prometheus_metrics = await self.prometheus.collect_metrics(
                    self.config['prometheus_queries']
                )
                
                # Collect from Elasticsearch
                es_metrics = await self.elasticsearch.collect_log_metrics()
                
                # Combine and save
                all_metrics = prometheus_metrics + es_metrics
                
                for metric in all_metrics:
                    self.db.save_metric(metric)
                
                logger.info(f"Collected {len(all_metrics)} metrics")
                
                # Evaluate thresholds and generate alerts
                alerts = self.alert_manager.evaluate_thresholds(
                    all_metrics, 
                    self.config['thresholds']
                )
                
                if alerts:
                    await self.alert_manager.send_notifications(alerts)
                
                await asyncio.sleep(self.config['collection_interval_seconds'])
            
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(30)
    
    async def _anomaly_detection_loop(self):
        """Detect anomalies in metrics"""
        while self.running:
            try:
                # Get recent metrics
                end_time = datetime.now()
                start_time = end_time - timedelta(hours=1)
                
                # Analyze each metric type
                for metric_name in ['cpu_usage', 'memory_usage', 'request_rate']:
                    metrics = self.db.get_metrics(
                        metric_name, 
                        'all',  # All components
                        start_time, 
                        end_time
                    )
                    
                    if metrics:
                        # Calculate baseline
                        baseline = {metric_name: np.mean([m.value for m in metrics])}
                        
                        # Detect anomalies
                        anomalies = self.ml_engine.detect_anomalies(metrics, baseline)
                        
                        # Save anomalies
                        for anomaly in anomalies:
                            self.db.save_anomaly(anomaly)
                            
                            # Create alert for severe anomalies
                            if anomaly.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]:
                                alert = Alert(
                                    alert_id=f"alert-{anomaly.anomaly_id}",
                                    severity=anomaly.severity,
                                    title=f"Anomaly detected: {anomaly.metric_name}",
                                    description=f"Deviation: {anomaly.deviation_percent:.1f}%, Expected: {anomaly.expected_value:.2f}, Actual: {anomaly.actual_value:.2f}",
                                    source_metric=anomaly.metric_name,
                                    threshold_value=anomaly.expected_value,
                                    actual_value=anomaly.actual_value,
                                    component=anomaly.component,
                                    namespace='default'
                                )
                                await self.alert_manager.send_notifications([alert])
                
                await asyncio.sleep(300)  # Every 5 minutes
            
            except Exception as e:
                logger.error(f"Anomaly detection error: {e}")
                await asyncio.sleep(60)
    
    async def _prediction_loop(self):
        """Generate predictions"""
        while self.running:
            try:
                # Get historical data for capacity planning
                end_time = datetime.now()
                start_time = end_time - timedelta(days=7)  # Last week
                
                for metric_name in ['cpu_usage', 'memory_usage']:
                    metrics = self.db.get_metrics(
                        metric_name,
                        'all',
                        start_time,
                        end_time
                    )
                    
                    if metrics:
                        prediction = self.ml_engine.predict_capacity(metrics, horizon_hours=24)
                        
                        if prediction and prediction.confidence > PREDICTION_CONFIDENCE_MIN:
                            self.db.save_prediction(prediction)
                            logger.info(f"Prediction for {metric_name}: {prediction.predicted_value:.2f} (confidence: {prediction.confidence:.2f})")
                
                await asyncio.sleep(self.config['prediction_interval_hours'] * 3600)
            
            except Exception as e:
                logger.error(f"Prediction error: {e}")
                await asyncio.sleep(600)
    
    async def _aggregation_loop(self):
        """Aggregate metrics for performance"""
        while self.running:
            try:
                self.db.aggregate_metrics(
                    time_bucket_minutes=self.config['aggregation_interval_minutes']
                )
                
                await asyncio.sleep(self.config['aggregation_interval_minutes'] * 60)
            
            except Exception as e:
                logger.error(f"Aggregation error: {e}")
                await asyncio.sleep(300)
    
    def stop(self):
        """Stop monitoring hub"""
        logger.info("Stopping monitoring hub")
        self.running = False

################################################################################
# CLI Interface
################################################################################

def main():
    """Main entry point"""
    logger.info("Advanced Monitoring Hub v12.0")
    
    if '--status' in sys.argv:
        db = MonitoringDatabase()
        
        # Show active alerts
        alerts = db.get_active_alerts()
        print(f"\n🚨 Active Alerts: {len(alerts)}")
        
        for alert in alerts[:10]:
            print(f"  [{alert.severity.value.upper()}] {alert.title}")
            print(f"    Component: {alert.component}, Value: {alert.actual_value:.2f}")
        
        # Show recent anomalies
        cursor = db.conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM anomalies 
            WHERE timestamp > datetime('now', '-1 hour')
        ''')
        anomaly_count = cursor.fetchone()[0]
        print(f"\n🔍 Anomalies (last hour): {anomaly_count}")
    
    elif '--run' in sys.argv:
        hub = AdvancedMonitoringHub()
        
        try:
            asyncio.run(hub.start())
        except KeyboardInterrupt:
            hub.stop()
            logger.info("Monitoring hub stopped")
    
    else:
        print("""
Advanced Monitoring Hub v12.0

Usage:
  --status    Show current system status
  --run       Run monitoring hub (continuous)

Examples:
  python3 advanced_monitoring_hub.py --status
  python3 advanced_monitoring_hub.py --run
        """)

if __name__ == '__main__':
    main()
