#!/usr/bin/env python3
"""
Advanced APM (Application Performance Monitoring) v11.0
Distributed tracing, performance profiling, anomaly detection
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import sqlite3

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor

from prometheus_client import Counter, Histogram, Gauge, start_http_server
import redis
from elasticsearch import Elasticsearch
import numpy as np
from sklearn.ensemble import IsolationForest

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
JAEGER_HOST = os.getenv('JAEGER_HOST', 'localhost')
JAEGER_PORT = int(os.getenv('JAEGER_PORT', '6831'))
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
ELASTIC_HOST = os.getenv('ELASTIC_HOST', 'http://localhost:9200')
DB_PATH = '/var/lib/apm/apm.db'

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Prometheus metrics
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint', 'status'])
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
error_count = Counter('http_errors_total', 'Total HTTP errors', ['method', 'endpoint'])
active_requests = Gauge('http_active_requests', 'Active HTTP requests')

@dataclass
class PerformanceMetric:
    """Performance metric data"""
    service_name: str
    endpoint: str
    method: str
    duration_ms: float
    status_code: int
    timestamp: datetime
    trace_id: str
    span_id: str

@dataclass
class PerformanceAnomaly:
    """Detected performance anomaly"""
    service_name: str
    endpoint: str
    anomaly_type: str
    severity: str
    baseline_value: float
    actual_value: float
    timestamp: datetime
    description: str

class APMDatabase:
    """SQLite database for APM data"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                method TEXT NOT NULL,
                duration_ms REAL NOT NULL,
                status_code INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                trace_id TEXT,
                span_id TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anomalies (
                anomaly_id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                anomaly_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                baseline_value REAL,
                actual_value REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS service_slo (
                service_name TEXT PRIMARY KEY,
                target_p50_ms REAL DEFAULT 100,
                target_p95_ms REAL DEFAULT 500,
                target_p99_ms REAL DEFAULT 1000,
                target_error_rate REAL DEFAULT 0.01,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON performance_metrics(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_service ON performance_metrics(service_name, endpoint)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_anomalies_timestamp ON anomalies(timestamp)')
        
        self.conn.commit()
        logger.info(f"APM database initialized: {self.db_path}")
    
    def record_metric(self, metric: PerformanceMetric):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO performance_metrics (service_name, endpoint, method, duration_ms, status_code, timestamp, trace_id, span_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (metric.service_name, metric.endpoint, metric.method, metric.duration_ms, metric.status_code, metric.timestamp, metric.trace_id, metric.span_id))
        self.conn.commit()
    
    def record_anomaly(self, anomaly: PerformanceAnomaly):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO anomalies (service_name, endpoint, anomaly_type, severity, baseline_value, actual_value, timestamp, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (anomaly.service_name, anomaly.endpoint, anomaly.type, anomaly.severity, anomaly.baseline_value, anomaly.actual_value, anomaly.timestamp, anomaly.description))
        self.conn.commit()
    
    def get_metrics(self, service: str, endpoint: str, hours: int = 24) -> List[PerformanceMetric]:
        cursor = self.conn.cursor()
        since = datetime.now() - timedelta(hours=hours)
        cursor.execute('''
            SELECT service_name, endpoint, method, duration_ms, status_code, timestamp, trace_id, span_id
            FROM performance_metrics
            WHERE service_name = ? AND endpoint = ? AND timestamp > ?
            ORDER BY timestamp DESC
        ''', (service, endpoint, since))
        
        metrics = []
        for row in cursor.fetchall():
            metrics.append(PerformanceMetric(
                service_name=row[0], endpoint=row[1], method=row[2], duration_ms=row[3],
                status_code=row[4], timestamp=datetime.fromisoformat(row[5]), trace_id=row[6], span_id=row[7]
            ))
        return metrics

class DistributedTracer:
    """Distributed tracing with OpenTelemetry and Jaeger"""
    
    def __init__(self):
        # Setup tracer
        trace.set_tracer_provider(TracerProvider())
        tracer_provider = trace.get_tracer_provider()
        
        # Jaeger exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name=JAEGER_HOST,
            agent_port=JAEGER_PORT,
        )
        
        tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
        
        self.tracer = trace.get_tracer(__name__)
        
        # Auto-instrumentation
        RequestsInstrumentor().instrument()
        
        logger.info(f"Distributed tracing initialized (Jaeger: {JAEGER_HOST}:{JAEGER_PORT})")
    
    def create_span(self, name: str, attributes: Dict = None):
        """Create a new span"""
        return self.tracer.start_as_current_span(name, attributes=attributes or {})
    
    def get_trace_context(self):
        """Get current trace context"""
        span = trace.get_current_span()
        if span:
            ctx = span.get_span_context()
            return {
                'trace_id': format(ctx.trace_id, '032x'),
                'span_id': format(ctx.span_id, '016x')
            }
        return {'trace_id': None, 'span_id': None}

class PerformanceProfiler:
    """Advanced performance profiling"""
    
    def __init__(self, db: APMDatabase):
        self.db = db
        self.redis = redis.Redis(host=REDIS_HOST, decode_responses=True)
    
    def profile_request(self, service: str, endpoint: str, method: str, duration_ms: float, status_code: int, trace_context: Dict):
        """Profile HTTP request"""
        metric = PerformanceMetric(
            service_name=service,
            endpoint=endpoint,
            method=method,
            duration_ms=duration_ms,
            status_code=status_code,
            timestamp=datetime.now(),
            trace_id=trace_context.get('trace_id'),
            span_id=trace_context.get('span_id')
        )
        
        self.db.record_metric(metric)
        
        # Update Prometheus metrics
        request_duration.labels(method=method, endpoint=endpoint, status=status_code).observe(duration_ms / 1000)
        request_count.labels(method=method, endpoint=endpoint, status=status_code).inc()
        
        if status_code >= 500:
            error_count.labels(method=method, endpoint=endpoint).inc()
        
        # Update Redis cache for real-time stats
        cache_key = f"perf:{service}:{endpoint}"
        self.redis.lpush(cache_key, duration_ms)
        self.redis.ltrim(cache_key, 0, 999)  # Keep last 1000 requests
        self.redis.expire(cache_key, 3600)
    
    def get_percentiles(self, service: str, endpoint: str) -> Dict:
        """Calculate percentiles from cached data"""
        cache_key = f"perf:{service}:{endpoint}"
        durations = [float(d) for d in self.redis.lrange(cache_key, 0, -1)]
        
        if not durations:
            return {'p50': 0, 'p95': 0, 'p99': 0, 'count': 0}
        
        return {
            'p50': np.percentile(durations, 50),
            'p95': np.percentile(durations, 95),
            'p99': np.percentile(durations, 99),
            'mean': np.mean(durations),
            'count': len(durations)
        }
    
    def check_slo_compliance(self, service: str, endpoint: str) -> Dict:
        """Check SLO compliance"""
        stats = self.get_percentiles(service, endpoint)
        
        # Get SLO targets (default values)
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT target_p50_ms, target_p95_ms, target_p99_ms FROM service_slo WHERE service_name = ?', (service,))
        row = cursor.fetchone()
        
        if row:
            target_p50, target_p95, target_p99 = row
        else:
            target_p50, target_p95, target_p99 = 100, 500, 1000
        
        return {
            'compliant': stats['p50'] <= target_p50 and stats['p95'] <= target_p95 and stats['p99'] <= target_p99,
            'p50_compliant': stats['p50'] <= target_p50,
            'p95_compliant': stats['p95'] <= target_p95,
            'p99_compliant': stats['p99'] <= target_p99,
            'stats': stats,
            'targets': {'p50': target_p50, 'p95': target_p95, 'p99': target_p99}
        }

class AnomalyDetector:
    """ML-based anomaly detection"""
    
    def __init__(self, db: APMDatabase):
        self.db = db
        self.models = {}  # service:endpoint -> IsolationForest model
    
    def train_model(self, service: str, endpoint: str):
        """Train anomaly detection model"""
        metrics = self.db.get_metrics(service, endpoint, hours=24*7)  # 7 days of data
        
        if len(metrics) < 100:
            logger.warning(f"Insufficient data for {service}/{endpoint}: {len(metrics)} samples")
            return
        
        # Extract features
        durations = np.array([m.duration_ms for m in metrics]).reshape(-1, 1)
        
        # Train Isolation Forest
        model = IsolationForest(contamination=0.05, random_state=42)
        model.fit(durations)
        
        self.models[f"{service}:{endpoint}"] = {
            'model': model,
            'baseline_mean': np.mean(durations),
            'baseline_std': np.std(durations)
        }
        
        logger.info(f"Trained anomaly model for {service}/{endpoint}")
    
    def detect_anomalies(self, service: str, endpoint: str, duration_ms: float) -> Optional[PerformanceAnomaly]:
        """Detect if current request is anomalous"""
        model_key = f"{service}:{endpoint}"
        
        if model_key not in self.models:
            self.train_model(service, endpoint)
            if model_key not in self.models:
                return None
        
        model_data = self.models[model_key]
        model = model_data['model']
        baseline_mean = model_data['baseline_mean']
        
        # Predict
        prediction = model.predict([[duration_ms]])
        
        if prediction[0] == -1:  # Anomaly detected
            # Determine severity
            deviation = abs(duration_ms - baseline_mean) / baseline_mean
            
            if deviation > 2.0:
                severity = 'critical'
            elif deviation > 1.0:
                severity = 'high'
            elif deviation > 0.5:
                severity = 'medium'
            else:
                severity = 'low'
            
            anomaly = PerformanceAnomaly(
                service_name=service,
                endpoint=endpoint,
                anomaly_type='latency_spike',
                severity=severity,
                baseline_value=baseline_mean,
                actual_value=duration_ms,
                timestamp=datetime.now(),
                description=f"Latency {deviation:.1%} above baseline"
            )
            
            self.db.record_anomaly(anomaly)
            logger.warning(f"Anomaly detected: {service}/{endpoint} - {duration_ms}ms (baseline: {baseline_mean:.1f}ms)")
            
            return anomaly
        
        return None

class LogAnalyzer:
    """ML-powered log analysis"""
    
    def __init__(self):
        try:
            self.es = Elasticsearch([ELASTIC_HOST])
        except:
            self.es = None
            logger.warning("Elasticsearch not available")
    
    def analyze_error_patterns(self, service: str, hours: int = 24) -> Dict:
        """Analyze error log patterns"""
        if not self.es:
            return {}
        
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"service.name": service}},
                        {"term": {"log.level": "ERROR"}},
                        {"range": {"@timestamp": {"gte": f"now-{hours}h"}}}
                    ]
                }
            },
            "aggs": {
                "error_types": {
                    "terms": {"field": "error.type", "size": 10}
                },
                "error_messages": {
                    "terms": {"field": "error.message.keyword", "size": 10}
                }
            }
        }
        
        try:
            result = self.es.search(index="logs-*", body=query)
            
            return {
                'total_errors': result['hits']['total']['value'],
                'error_types': [
                    {'type': b['key'], 'count': b['doc_count']}
                    for b in result['aggregations']['error_types']['buckets']
                ],
                'error_messages': [
                    {'message': b['key'], 'count': b['doc_count']}
                    for b in result['aggregations']['error_messages']['buckets']
                ]
            }
        except Exception as e:
            logger.error(f"Error analyzing logs: {e}")
            return {}
    
    def search_logs(self, service: str, query: str, hours: int = 1) -> List[Dict]:
        """Search logs with natural language query"""
        if not self.es:
            return []
        
        search_query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"service.name": service}},
                        {"query_string": {"query": query}},
                        {"range": {"@timestamp": {"gte": f"now-{hours}h"}}}
                    ]
                }
            },
            "sort": [{"@timestamp": "desc"}],
            "size": 100
        }
        
        try:
            result = self.es.search(index="logs-*", body=search_query)
            return [hit['_source'] for hit in result['hits']['hits']]
        except Exception as e:
            logger.error(f"Error searching logs: {e}")
            return []

class APMCollector:
    """Main APM collector"""
    
    def __init__(self):
        self.db = APMDatabase()
        self.tracer = DistributedTracer()
        self.profiler = PerformanceProfiler(self.db)
        self.anomaly_detector = AnomalyDetector(self.db)
        self.log_analyzer = LogAnalyzer()
        
        # Start Prometheus metrics server
        start_http_server(9090)
        logger.info("Prometheus metrics server started on :9090")
    
    def record_request(self, service: str, endpoint: str, method: str, duration_ms: float, status_code: int):
        """Record HTTP request with full observability"""
        trace_context = self.tracer.get_trace_context()
        
        # Profile request
        self.profiler.profile_request(service, endpoint, method, duration_ms, status_code, trace_context)
        
        # Detect anomalies
        self.anomaly_detector.detect_anomalies(service, endpoint, duration_ms)
    
    def get_service_health(self, service: str) -> Dict:
        """Get comprehensive service health"""
        cursor = self.db.conn.cursor()
        
        # Get endpoints
        cursor.execute('SELECT DISTINCT endpoint FROM performance_metrics WHERE service_name = ?', (service,))
        endpoints = [row[0] for row in cursor.fetchall()]
        
        health = {
            'service': service,
            'endpoints': {},
            'overall_health': 'healthy'
        }
        
        for endpoint in endpoints:
            stats = self.profiler.get_percentiles(service, endpoint)
            slo = self.profiler.check_slo_compliance(service, endpoint)
            
            # Get recent anomalies
            cursor.execute('''
                SELECT COUNT(*) FROM anomalies
                WHERE service_name = ? AND endpoint = ? AND timestamp > datetime('now', '-1 hour')
            ''', (service, endpoint))
            recent_anomalies = cursor.fetchone()[0]
            
            endpoint_health = 'healthy'
            if not slo['compliant']:
                endpoint_health = 'degraded'
            if recent_anomalies > 5:
                endpoint_health = 'critical'
            
            health['endpoints'][endpoint] = {
                'health': endpoint_health,
                'stats': stats,
                'slo_compliance': slo,
                'recent_anomalies': recent_anomalies
            }
            
            if endpoint_health == 'critical':
                health['overall_health'] = 'critical'
            elif endpoint_health == 'degraded' and health['overall_health'] == 'healthy':
                health['overall_health'] = 'degraded'
        
        return health

def main():
    """Main entry point"""
    logger.info("Advanced APM System v11.0")
    
    collector = APMCollector()
    
    if '--simulate' in sys.argv:
        # Simulate requests for testing
        import random
        services = ['frontend', 'backend', 'api']
        endpoints = ['/api/users', '/api/orders', '/api/products']
        methods = ['GET', 'POST', 'PUT']
        
        logger.info("Starting simulation...")
        while True:
            service = random.choice(services)
            endpoint = random.choice(endpoints)
            method = random.choice(methods)
            duration = random.gauss(150, 50)  # Normal distribution
            status = random.choices([200, 500], weights=[0.99, 0.01])[0]
            
            collector.record_request(service, endpoint, method, duration, status)
            time.sleep(0.1)
    
    elif '--health' in sys.argv:
        service = sys.argv[2] if len(sys.argv) > 2 else 'frontend'
        health = collector.get_service_health(service)
        print(json.dumps(health, indent=2))
    
    elif '--analyze-logs' in sys.argv:
        service = sys.argv[2] if len(sys.argv) > 2 else 'frontend'
        errors = collector.log_analyzer.analyze_error_patterns(service)
        print(json.dumps(errors, indent=2))
    
    else:
        print("Usage:")
        print("  --simulate           Simulate requests")
        print("  --health SERVICE     Get service health")
        print("  --analyze-logs SVC   Analyze error logs")

if __name__ == '__main__':
    main()
