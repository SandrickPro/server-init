#!/usr/bin/env python3
"""
Log Analytics ML v11.0
ML-powered log analysis, anomaly detection, predictive alerting
"""

import os
import sys
import json
import re
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import Counter
import sqlite3

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN, KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
ELASTIC_HOST = os.getenv('ELASTIC_HOST', 'http://localhost:9200')
DB_PATH = '/var/lib/log-analytics/logs.db'
MODELS_PATH = '/var/lib/log-analytics/models'

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(MODELS_PATH, exist_ok=True)

class LogDatabase:
    """SQLite database for log analytics"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS log_patterns (
                pattern_id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_text TEXT NOT NULL,
                cluster_id INTEGER,
                count INTEGER DEFAULT 0,
                first_seen TIMESTAMP,
                last_seen TIMESTAMP,
                severity TEXT,
                service_name TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS log_anomalies (
                anomaly_id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT NOT NULL,
                log_message TEXT,
                anomaly_score REAL,
                severity TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved BOOLEAN DEFAULT FALSE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictive_alerts (
                alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                prediction TEXT,
                confidence REAL,
                triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved BOOLEAN DEFAULT FALSE
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_patterns_cluster ON log_patterns(cluster_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_anomalies_timestamp ON log_anomalies(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_service ON predictive_alerts(service_name)')
        
        self.conn.commit()
        logger.info(f"Log analytics database initialized: {self.db_path}")

class LogPatternExtractor:
    """Extract patterns from log messages using ML clustering"""
    
    def __init__(self, db: LogDatabase):
        self.db = db
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
    
    def extract_patterns(self, logs: List[str], service: str) -> List[Dict]:
        """Extract common patterns from logs using clustering"""
        
        if len(logs) < 10:
            logger.warning(f"Insufficient logs for pattern extraction: {len(logs)}")
            return []
        
        # Preprocess logs - remove timestamps, IDs, numbers
        cleaned_logs = []
        for log in logs:
            # Remove timestamps
            cleaned = re.sub(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}', '', log)
            # Remove UUIDs
            cleaned = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', 'UUID', cleaned)
            # Remove numbers
            cleaned = re.sub(r'\b\d+\b', 'NUM', cleaned)
            # Remove IPs
            cleaned = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', 'IP', cleaned)
            cleaned_logs.append(cleaned)
        
        # Vectorize
        try:
            tfidf_matrix = self.vectorizer.fit_transform(cleaned_logs)
        except:
            return []
        
        # Cluster using DBSCAN
        clustering = DBSCAN(eps=0.5, min_samples=3, metric='cosine')
        labels = clustering.fit_predict(tfidf_matrix)
        
        # Extract pattern for each cluster
        patterns = []
        for cluster_id in set(labels):
            if cluster_id == -1:  # Noise
                continue
            
            cluster_logs = [cleaned_logs[i] for i, label in enumerate(labels) if label == cluster_id]
            
            # Find common pattern (most common tokens)
            tokens_counter = Counter()
            for log in cluster_logs:
                tokens = log.split()
                tokens_counter.update(tokens)
            
            # Build pattern from most common tokens
            common_tokens = [token for token, count in tokens_counter.most_common(10) if count > len(cluster_logs) * 0.5]
            pattern_text = ' '.join(common_tokens)
            
            patterns.append({
                'cluster_id': int(cluster_id),
                'pattern': pattern_text,
                'count': len(cluster_logs),
                'service': service
            })
        
        # Store patterns
        cursor = self.db.conn.cursor()
        for pattern in patterns:
            cursor.execute('''
                INSERT INTO log_patterns (pattern_text, cluster_id, count, first_seen, last_seen, service_name)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(pattern_id) DO UPDATE SET count = count + ?, last_seen = ?
            ''', (
                pattern['pattern'], pattern['cluster_id'], pattern['count'],
                datetime.now(), datetime.now(), pattern['service'],
                pattern['count'], datetime.now()
            ))
        self.db.conn.commit()
        
        logger.info(f"Extracted {len(patterns)} patterns from {len(logs)} logs")
        return patterns

class LogAnomalyDetector:
    """ML-based anomaly detection in logs"""
    
    def __init__(self, db: LogDatabase):
        self.db = db
        self.model = None
        self.scaler = StandardScaler()
        self.vectorizer = TfidfVectorizer(max_features=50)
    
    def train(self, logs: List[Dict], service: str):
        """Train anomaly detection model"""
        
        if len(logs) < 100:
            logger.warning(f"Insufficient logs for training: {len(logs)}")
            return
        
        # Extract features
        messages = [log.get('message', '') for log in logs]
        
        # Text features
        try:
            tfidf_features = self.vectorizer.fit_transform(messages).toarray()
        except:
            logger.error("Failed to vectorize logs")
            return
        
        # Temporal features
        timestamps = [datetime.fromisoformat(log.get('timestamp', datetime.now().isoformat())) for log in logs]
        hours = np.array([t.hour for t in timestamps]).reshape(-1, 1)
        
        # Combine features
        features = np.hstack([tfidf_features, hours])
        
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        # Train Isolation Forest
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.model.fit(features_scaled)
        
        # Save model
        model_path = os.path.join(MODELS_PATH, f'{service}_anomaly_model.pkl')
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'vectorizer': self.vectorizer
        }, model_path)
        
        logger.info(f"Trained anomaly model for {service} with {len(logs)} samples")
    
    def detect(self, log: Dict, service: str) -> Optional[Dict]:
        """Detect if log is anomalous"""
        
        # Load model if not in memory
        if not self.model:
            model_path = os.path.join(MODELS_PATH, f'{service}_anomaly_model.pkl')
            if os.path.exists(model_path):
                data = joblib.load(model_path)
                self.model = data['model']
                self.scaler = data['scaler']
                self.vectorizer = data['vectorizer']
            else:
                return None
        
        # Extract features
        message = log.get('message', '')
        timestamp = datetime.fromisoformat(log.get('timestamp', datetime.now().isoformat()))
        
        try:
            tfidf_features = self.vectorizer.transform([message]).toarray()
        except:
            return None
        
        hour = np.array([[timestamp.hour]])
        features = np.hstack([tfidf_features, hour])
        features_scaled = self.scaler.transform(features)
        
        # Predict
        prediction = self.model.predict(features_scaled)
        anomaly_score = self.model.score_samples(features_scaled)[0]
        
        if prediction[0] == -1:  # Anomaly
            # Determine severity based on score
            if anomaly_score < -0.5:
                severity = 'critical'
            elif anomaly_score < -0.3:
                severity = 'high'
            elif anomaly_score < -0.1:
                severity = 'medium'
            else:
                severity = 'low'
            
            anomaly = {
                'service': service,
                'message': message,
                'score': float(anomaly_score),
                'severity': severity,
                'timestamp': timestamp
            }
            
            # Store anomaly
            cursor = self.db.conn.cursor()
            cursor.execute('''
                INSERT INTO log_anomalies (service_name, log_message, anomaly_score, severity, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (service, message, anomaly_score, severity, timestamp))
            self.db.conn.commit()
            
            logger.warning(f"Log anomaly detected: {service} - {severity} - {message[:100]}")
            return anomaly
        
        return None

class PredictiveAlertEngine:
    """Predictive alerting based on log trends"""
    
    def __init__(self, db: LogDatabase):
        self.db = db
    
    def analyze_trends(self, service: str, hours: int = 24) -> List[Dict]:
        """Analyze log trends and predict issues"""
        
        # Get recent anomalies
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT severity, COUNT(*) as count
            FROM log_anomalies
            WHERE service_name = ? AND timestamp > datetime('now', ? || ' hours')
            GROUP BY severity
        ''', (service, -hours))
        
        anomaly_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        predictions = []
        
        # Predict potential issues
        critical_count = anomaly_counts.get('critical', 0)
        high_count = anomaly_counts.get('high', 0)
        
        if critical_count > 10:
            predictions.append({
                'type': 'service_degradation',
                'prediction': f'Service {service} may experience degradation due to {critical_count} critical anomalies',
                'confidence': min(0.95, 0.5 + (critical_count / 20)),
                'severity': 'critical'
            })
        
        if high_count > 50:
            predictions.append({
                'type': 'performance_issue',
                'prediction': f'Performance issues detected in {service} ({high_count} high-severity anomalies)',
                'confidence': min(0.90, 0.5 + (high_count / 100)),
                'severity': 'high'
            })
        
        # Store predictions
        for pred in predictions:
            cursor.execute('''
                INSERT INTO predictive_alerts (service_name, alert_type, prediction, confidence)
                VALUES (?, ?, ?, ?)
            ''', (service, pred['type'], pred['prediction'], pred['confidence']))
        self.db.conn.commit()
        
        return predictions

class ElasticsearchLogQuery:
    """Optimized Elasticsearch queries for logs"""
    
    def __init__(self):
        try:
            self.es = Elasticsearch([ELASTIC_HOST], request_timeout=30)
        except:
            self.es = None
            logger.warning("Elasticsearch not available")
    
    def search_logs(self, service: str, query: str, start_time: datetime, end_time: datetime, size: int = 1000) -> List[Dict]:
        """Optimized log search with <1s target"""
        
        if not self.es:
            return []
        
        search_query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"service.name": service}},
                        {"range": {"@timestamp": {"gte": start_time.isoformat(), "lte": end_time.isoformat()}}}
                    ]
                }
            },
            "sort": [{"@timestamp": "desc"}],
            "size": size
        }
        
        if query:
            search_query['query']['bool']['must'].append({"query_string": {"query": query}})
        
        try:
            start = time.time()
            result = self.es.search(index="logs-*", body=search_query)
            elapsed = time.time() - start
            
            logger.info(f"Log search completed in {elapsed:.3f}s (target: <1s)")
            
            return [hit['_source'] for hit in result['hits']['hits']]
        except Exception as e:
            logger.error(f"Error searching logs: {e}")
            return []
    
    def aggregate_error_rates(self, service: str, hours: int = 24) -> Dict:
        """Aggregate error rates by time"""
        
        if not self.es:
            return {}
        
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"service.name": service}},
                        {"range": {"@timestamp": {"gte": f"now-{hours}h"}}}
                    ]
                }
            },
            "aggs": {
                "errors_over_time": {
                    "date_histogram": {
                        "field": "@timestamp",
                        "fixed_interval": "1h"
                    },
                    "aggs": {
                        "error_count": {
                            "filter": {"term": {"log.level": "ERROR"}}
                        }
                    }
                },
                "total_errors": {
                    "filter": {"term": {"log.level": "ERROR"}}
                }
            }
        }
        
        try:
            result = self.es.search(index="logs-*", body=query, size=0)
            
            return {
                'total_logs': result['hits']['total']['value'],
                'total_errors': result['aggregations']['total_errors']['doc_count'],
                'error_rate': result['aggregations']['total_errors']['doc_count'] / max(result['hits']['total']['value'], 1),
                'timeline': [
                    {
                        'timestamp': bucket['key_as_string'],
                        'errors': bucket['error_count']['doc_count']
                    }
                    for bucket in result['aggregations']['errors_over_time']['buckets']
                ]
            }
        except Exception as e:
            logger.error(f"Error aggregating logs: {e}")
            return {}

class LogAnalyticsEngine:
    """Main log analytics engine"""
    
    def __init__(self):
        self.db = LogDatabase()
        self.pattern_extractor = LogPatternExtractor(self.db)
        self.anomaly_detector = LogAnomalyDetector(self.db)
        self.alert_engine = PredictiveAlertEngine(self.db)
        self.query_engine = ElasticsearchLogQuery()
    
    def analyze_service(self, service: str, hours: int = 24):
        """Comprehensive service log analysis"""
        
        # Fetch logs
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        logs = self.query_engine.search_logs(service, '', start_time, end_time, size=5000)
        
        if not logs:
            logger.warning(f"No logs found for {service}")
            return
        
        # Extract patterns
        messages = [log.get('message', '') for log in logs]
        patterns = self.pattern_extractor.extract_patterns(messages, service)
        
        # Train anomaly detector
        self.anomaly_detector.train(logs, service)
        
        # Detect anomalies in recent logs
        recent_logs = logs[:100]
        anomalies = []
        for log in recent_logs:
            anomaly = self.anomaly_detector.detect(log, service)
            if anomaly:
                anomalies.append(anomaly)
        
        # Generate predictions
        predictions = self.alert_engine.analyze_trends(service, hours)
        
        # Get error rates
        error_stats = self.query_engine.aggregate_error_rates(service, hours)
        
        return {
            'service': service,
            'total_logs': len(logs),
            'patterns': len(patterns),
            'anomalies': len(anomalies),
            'predictions': predictions,
            'error_stats': error_stats
        }

def main():
    """Main entry point"""
    logger.info("Log Analytics ML v11.0")
    
    engine = LogAnalyticsEngine()
    
    if '--analyze' in sys.argv:
        service = sys.argv[2] if len(sys.argv) > 2 else 'frontend'
        hours = int(sys.argv[3]) if len(sys.argv) > 3 else 24
        
        logger.info(f"Analyzing {service} (last {hours}h)...")
        result = engine.analyze_service(service, hours)
        print(json.dumps(result, indent=2, default=str))
    
    elif '--query' in sys.argv:
        service = sys.argv[2] if len(sys.argv) > 2 else 'frontend'
        query = sys.argv[3] if len(sys.argv) > 3 else ''
        
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=1)
        logs = engine.query_engine.search_logs(service, query, start_time, end_time)
        
        for log in logs[:20]:
            print(f"{log.get('timestamp', 'N/A')} [{log.get('log.level', 'INFO')}] {log.get('message', '')}")
    
    else:
        print("Usage:")
        print("  --analyze SERVICE [HOURS]    Analyze service logs")
        print("  --query SERVICE [QUERY]      Query logs")

if __name__ == '__main__':
    main()
