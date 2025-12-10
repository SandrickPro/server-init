#!/usr/bin/env python3
"""
Predictive Maintenance System v11.0
ML-based failure prediction and proactive maintenance
"""

import os
import sys
import json
import time
import logging
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Machine Learning
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import xgboost as xgb

# Monitoring Integration
import requests
from prometheus_client import Gauge, Counter, Histogram
import psycopg2
from redis import Redis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus Metrics
FAILURE_PREDICTION_GAUGE = Gauge('predictive_failure_probability', 'Predicted failure probability', ['component'])
MAINTENANCE_SCHEDULED_COUNTER = Counter('maintenance_scheduled_total', 'Total maintenance tasks scheduled')
PREDICTION_ACCURACY_GAUGE = Gauge('prediction_accuracy', 'Model prediction accuracy')
MODEL_TRAINING_TIME = Histogram('model_training_seconds', 'Time spent training ML models')

# Configuration
PROMETHEUS_URL = os.getenv('PROMETHEUS_URL', 'http://localhost:9090')
POSTGRES_DSN = os.getenv('POSTGRES_DSN', 'postgresql://postgres:password@localhost:5432/metrics')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

@dataclass
class PredictionResult:
    """Result of failure prediction"""
    component: str
    failure_probability: float
    predicted_failure_time: Optional[datetime]
    contributing_factors: List[str]
    recommended_actions: List[str]
    confidence: float

@dataclass
class MaintenanceTask:
    """Scheduled maintenance task"""
    task_id: str
    component: str
    priority: str  # critical, high, medium, low
    description: str
    scheduled_time: datetime
    estimated_duration: int  # minutes
    automated: bool

class MetricsCollector:
    """Collect metrics from various sources"""
    
    def __init__(self):
        self.prometheus_url = PROMETHEUS_URL
        self.redis = Redis(host=REDIS_HOST, decode_responses=True)
        
    def query_prometheus(self, query: str, lookback: str = '1h') -> pd.DataFrame:
        """Query Prometheus for metrics"""
        try:
            url = f"{self.prometheus_url}/api/v1/query"
            params = {
                'query': query,
                'time': int(time.time())
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data['status'] != 'success':
                logger.error(f"Prometheus query failed: {data}")
                return pd.DataFrame()
            
            results = data['data']['result']
            if not results:
                return pd.DataFrame()
            
            # Convert to DataFrame
            records = []
            for result in results:
                metric = result['metric']
                value = float(result['value'][1])
                records.append({**metric, 'value': value})
            
            return pd.DataFrame(records)
            
        except Exception as e:
            logger.error(f"Error querying Prometheus: {e}")
            return pd.DataFrame()
    
    def query_prometheus_range(self, query: str, start: datetime, end: datetime, step: str = '1m') -> pd.DataFrame:
        """Query Prometheus for time range"""
        try:
            url = f"{self.prometheus_url}/api/v1/query_range"
            params = {
                'query': query,
                'start': int(start.timestamp()),
                'end': int(end.timestamp()),
                'step': step
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if data['status'] != 'success':
                return pd.DataFrame()
            
            results = data['data']['result']
            if not results:
                return pd.DataFrame()
            
            # Convert to time series DataFrame
            all_data = []
            for result in results:
                metric = result['metric']
                for timestamp, value in result['values']:
                    all_data.append({
                        **metric,
                        'timestamp': datetime.fromtimestamp(timestamp),
                        'value': float(value)
                    })
            
            df = pd.DataFrame(all_data)
            return df.sort_values('timestamp')
            
        except Exception as e:
            logger.error(f"Error querying Prometheus range: {e}")
            return pd.DataFrame()
    
    def get_system_metrics(self, lookback_hours: int = 24) -> pd.DataFrame:
        """Collect comprehensive system metrics"""
        end = datetime.now()
        start = end - timedelta(hours=lookback_hours)
        
        metrics = {
            'cpu_usage': 'avg(rate(node_cpu_seconds_total{mode!="idle"}[5m])) by (instance)',
            'memory_usage': 'node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes',
            'disk_usage': '(node_filesystem_size_bytes - node_filesystem_avail_bytes) / node_filesystem_size_bytes',
            'network_errors': 'rate(node_network_receive_errs_total[5m]) + rate(node_network_transmit_errs_total[5m])',
            'pod_restarts': 'rate(kube_pod_container_status_restarts_total[5m])',
            'response_time': 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))',
            'error_rate': 'rate(http_requests_total{status=~"5.."}[5m])',
            'disk_io_time': 'rate(node_disk_io_time_seconds_total[5m])',
        }
        
        all_metrics = []
        for metric_name, query in metrics.items():
            df = self.query_prometheus_range(query, start, end, step='5m')
            if not df.empty:
                df['metric_name'] = metric_name
                all_metrics.append(df)
        
        if not all_metrics:
            return pd.DataFrame()
        
        return pd.concat(all_metrics, ignore_index=True)

class FailurePredictor:
    """ML-based failure prediction"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_names = []
        self.model_dir = '/var/lib/predictive-maintenance/models'
        os.makedirs(self.model_dir, exist_ok=True)
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features for ML"""
        if df.empty:
            return pd.DataFrame()
        
        # Pivot metrics to wide format
        features = df.pivot_table(
            index='timestamp',
            columns='metric_name',
            values='value',
            aggfunc='mean'
        ).reset_index()
        
        # Add time-based features
        features['hour'] = features['timestamp'].dt.hour
        features['day_of_week'] = features['timestamp'].dt.dayofweek
        features['is_weekend'] = features['day_of_week'].isin([5, 6]).astype(int)
        
        # Add rolling statistics
        for col in features.select_dtypes(include=[np.number]).columns:
            if col not in ['hour', 'day_of_week', 'is_weekend']:
                features[f'{col}_rolling_mean'] = features[col].rolling(window=6, min_periods=1).mean()
                features[f'{col}_rolling_std'] = features[col].rolling(window=6, min_periods=1).std()
                features[f'{col}_rolling_max'] = features[col].rolling(window=6, min_periods=1).max()
        
        # Add rate of change
        for col in features.select_dtypes(include=[np.number]).columns:
            if col not in ['hour', 'day_of_week', 'is_weekend'] and not col.endswith('_rolling_mean'):
                features[f'{col}_change'] = features[col].diff()
        
        # Fill NaN values
        features = features.fillna(method='bfill').fillna(0)
        
        # Drop timestamp for training
        if 'timestamp' in features.columns:
            features = features.drop('timestamp', axis=1)
        
        return features
    
    def generate_training_labels(self, df: pd.DataFrame) -> np.ndarray:
        """Generate labels for training (simulated failures)"""
        # In production, use actual failure logs
        # For now, use heuristics to identify problematic states
        
        labels = []
        for _, row in df.iterrows():
            failure_score = 0
            
            # High CPU
            if 'cpu_usage' in row and row['cpu_usage'] > 0.9:
                failure_score += 2
            
            # High memory usage
            if 'memory_usage' in row and row['memory_usage'] < 0.1:  # <10% available
                failure_score += 2
            
            # Disk full
            if 'disk_usage' in row and row['disk_usage'] > 0.95:
                failure_score += 3
            
            # Network errors
            if 'network_errors' in row and row['network_errors'] > 0.01:
                failure_score += 2
            
            # Pod restarts
            if 'pod_restarts' in row and row['pod_restarts'] > 0.1:
                failure_score += 2
            
            # High error rate
            if 'error_rate' in row and row['error_rate'] > 0.05:
                failure_score += 2
            
            # Label as failure if score >= 5
            labels.append(1 if failure_score >= 5 else 0)
        
        return np.array(labels)
    
    @MODEL_TRAINING_TIME.time()
    def train_model(self, features: pd.DataFrame, labels: np.ndarray, model_name: str = 'random_forest'):
        """Train failure prediction model"""
        if features.empty or len(labels) == 0:
            logger.warning("No data for training")
            return
        
        # Store feature names
        self.feature_names = features.columns.tolist()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train multiple models
        models_to_train = {
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            ),
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            ),
            'xgboost': xgb.XGBClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        }
        
        best_model = None
        best_score = 0
        
        for name, model in models_to_train.items():
            logger.info(f"Training {name} model...")
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, zero_division=0)
            recall = recall_score(y_test, y_pred, zero_division=0)
            f1 = f1_score(y_test, y_pred, zero_division=0)
            
            logger.info(f"{name} - Accuracy: {accuracy:.3f}, Precision: {precision:.3f}, Recall: {recall:.3f}, F1: {f1:.3f}")
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
            logger.info(f"{name} - CV Score: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")
            
            if f1 > best_score:
                best_score = f1
                best_model = (name, model)
        
        # Save best model
        if best_model:
            model_name, model = best_model
            self.models[model_name] = model
            self.scalers[model_name] = scaler
            
            # Save to disk
            model_path = os.path.join(self.model_dir, f'{model_name}.pkl')
            scaler_path = os.path.join(self.model_dir, f'{model_name}_scaler.pkl')
            
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            
            with open(scaler_path, 'wb') as f:
                pickle.dump(scaler, f)
            
            # Update Prometheus metric
            PREDICTION_ACCURACY_GAUGE.set(best_score)
            
            logger.info(f"Best model: {model_name} (F1: {best_score:.3f})")
    
    def load_model(self, model_name: str = 'random_forest'):
        """Load trained model from disk"""
        model_path = os.path.join(self.model_dir, f'{model_name}.pkl')
        scaler_path = os.path.join(self.model_dir, f'{model_name}_scaler.pkl')
        
        if not os.path.exists(model_path):
            logger.warning(f"Model {model_name} not found")
            return False
        
        with open(model_path, 'rb') as f:
            self.models[model_name] = pickle.load(f)
        
        with open(scaler_path, 'rb') as f:
            self.scalers[model_name] = pickle.load(f)
        
        logger.info(f"Loaded model: {model_name}")
        return True
    
    def predict_failure(self, features: pd.DataFrame, model_name: str = 'random_forest') -> Tuple[np.ndarray, np.ndarray]:
        """Predict failure probability"""
        if model_name not in self.models:
            logger.warning(f"Model {model_name} not loaded")
            return np.array([]), np.array([])
        
        model = self.models[model_name]
        scaler = self.scalers[model_name]
        
        # Ensure features match training
        for col in self.feature_names:
            if col not in features.columns:
                features[col] = 0
        
        features = features[self.feature_names]
        
        # Scale and predict
        X_scaled = scaler.transform(features)
        predictions = model.predict(X_scaled)
        probabilities = model.predict_proba(X_scaled)[:, 1]  # Probability of failure
        
        return predictions, probabilities
    
    def get_feature_importance(self, model_name: str = 'random_forest', top_n: int = 10) -> List[Tuple[str, float]]:
        """Get most important features"""
        if model_name not in self.models:
            return []
        
        model = self.models[model_name]
        
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            feature_importance = list(zip(self.feature_names, importances))
            feature_importance.sort(key=lambda x: x[1], reverse=True)
            return feature_importance[:top_n]
        
        return []

class MaintenanceScheduler:
    """Schedule and manage maintenance tasks"""
    
    def __init__(self):
        self.tasks = []
        self.redis = Redis(host=REDIS_HOST, decode_responses=True)
        
    def create_task(self, prediction: PredictionResult) -> MaintenanceTask:
        """Create maintenance task from prediction"""
        task_id = f"maint_{int(time.time())}_{prediction.component}"
        
        # Determine priority
        if prediction.failure_probability > 0.9:
            priority = 'critical'
            scheduled_time = datetime.now() + timedelta(hours=1)
        elif prediction.failure_probability > 0.7:
            priority = 'high'
            scheduled_time = datetime.now() + timedelta(hours=4)
        elif prediction.failure_probability > 0.5:
            priority = 'medium'
            scheduled_time = datetime.now() + timedelta(hours=12)
        else:
            priority = 'low'
            scheduled_time = datetime.now() + timedelta(days=1)
        
        task = MaintenanceTask(
            task_id=task_id,
            component=prediction.component,
            priority=priority,
            description=f"Predicted failure in {prediction.component} (probability: {prediction.failure_probability:.2%})",
            scheduled_time=scheduled_time,
            estimated_duration=30,
            automated=prediction.failure_probability > 0.8
        )
        
        self.tasks.append(task)
        
        # Store in Redis
        self.redis.setex(
            f"maintenance_task:{task_id}",
            86400,  # 24 hours TTL
            json.dumps({
                'task_id': task.task_id,
                'component': task.component,
                'priority': task.priority,
                'description': task.description,
                'scheduled_time': task.scheduled_time.isoformat(),
                'estimated_duration': task.estimated_duration,
                'automated': task.automated
            })
        )
        
        MAINTENANCE_SCHEDULED_COUNTER.inc()
        
        logger.info(f"Created maintenance task: {task_id} (priority: {priority})")
        return task
    
    def get_pending_tasks(self) -> List[MaintenanceTask]:
        """Get pending maintenance tasks"""
        now = datetime.now()
        return [task for task in self.tasks if task.scheduled_time <= now]
    
    def execute_automated_maintenance(self, task: MaintenanceTask) -> bool:
        """Execute automated maintenance"""
        if not task.automated:
            return False
        
        logger.info(f"Executing automated maintenance: {task.task_id}")
        
        # Implement automated fixes
        if 'disk' in task.component.lower():
            self._cleanup_disk()
        elif 'memory' in task.component.lower():
            self._cleanup_memory()
        elif 'pod' in task.component.lower():
            self._restart_unhealthy_pods()
        
        return True
    
    def _cleanup_disk(self):
        """Clean up disk space"""
        os.system('find /tmp -type f -atime +7 -delete')
        os.system('docker system prune -af --filter "until=48h"')
        logger.info("Disk cleanup completed")
    
    def _cleanup_memory(self):
        """Clean up memory"""
        os.system('sync && echo 3 > /proc/sys/vm/drop_caches')
        logger.info("Memory cleanup completed")
    
    def _restart_unhealthy_pods(self):
        """Restart unhealthy pods"""
        os.system('kubectl delete pods --field-selector status.phase=Failed -A')
        logger.info("Restarted unhealthy pods")

class NotificationService:
    """Send notifications"""
    
    @staticmethod
    def send_telegram(message: str):
        """Send Telegram notification"""
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            return
        
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                'chat_id': TELEGRAM_CHAT_ID,
                'text': message,
                'parse_mode': 'Markdown'
            }
            requests.post(url, json=data, timeout=10)
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")

class PredictiveMaintenanceSystem:
    """Main predictive maintenance system"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.predictor = FailurePredictor()
        self.scheduler = MaintenanceScheduler()
        
    def initialize(self):
        """Initialize the system"""
        logger.info("Initializing Predictive Maintenance System...")
        
        # Try to load existing model
        if not self.predictor.load_model():
            logger.info("No existing model found, will train on first run")
    
    def train(self, lookback_hours: int = 168):  # 1 week
        """Train ML models"""
        logger.info(f"Training models with {lookback_hours} hours of data...")
        
        # Collect historical data
        df = self.metrics_collector.get_system_metrics(lookback_hours)
        
        if df.empty:
            logger.warning("No metrics available for training")
            return
        
        # Prepare features
        features = self.predictor.prepare_features(df)
        
        if features.empty:
            logger.warning("No features generated")
            return
        
        # Generate labels
        labels = self.predictor.generate_training_labels(features)
        
        # Train model
        self.predictor.train_model(features, labels)
        
        logger.info("Model training completed")
    
    def predict(self) -> List[PredictionResult]:
        """Run predictions"""
        logger.info("Running failure predictions...")
        
        # Collect recent metrics
        df = self.metrics_collector.get_system_metrics(lookback_hours=4)
        
        if df.empty:
            logger.warning("No metrics available")
            return []
        
        # Prepare features
        features = self.predictor.prepare_features(df)
        
        if features.empty:
            return []
        
        # Get predictions
        predictions, probabilities = self.predictor.predict_failure(features)
        
        # Analyze results
        results = []
        if len(probabilities) > 0:
            avg_probability = np.mean(probabilities)
            max_probability = np.max(probabilities)
            
            logger.info(f"Average failure probability: {avg_probability:.2%}")
            logger.info(f"Maximum failure probability: {max_probability:.2%}")
            
            # Create prediction result
            if max_probability > 0.5:
                # Get top contributing factors
                feature_importance = self.predictor.get_feature_importance()
                contributing_factors = [f"{name}: {importance:.3f}" for name, importance in feature_importance[:5]]
                
                result = PredictionResult(
                    component='system',
                    failure_probability=max_probability,
                    predicted_failure_time=datetime.now() + timedelta(hours=2),
                    contributing_factors=contributing_factors,
                    recommended_actions=[
                        'Review system resources',
                        'Check for anomalies',
                        'Schedule maintenance window'
                    ],
                    confidence=0.85
                )
                
                results.append(result)
                
                # Update Prometheus
                FAILURE_PREDICTION_GAUGE.labels(component='system').set(max_probability)
        
        return results
    
    def run_cycle(self):
        """Run one prediction cycle"""
        # Run predictions
        predictions = self.predict()
        
        # Schedule maintenance for high-risk predictions
        for prediction in predictions:
            if prediction.failure_probability > 0.5:
                task = self.scheduler.create_task(prediction)
                
                # Send notification
                message = f"""
🔧 *Predictive Maintenance Alert*

Component: {prediction.component}
Failure Probability: {prediction.failure_probability:.1%}
Confidence: {prediction.confidence:.1%}

*Contributing Factors:*
{chr(10).join(f'• {factor}' for factor in prediction.contributing_factors)}

*Recommended Actions:*
{chr(10).join(f'• {action}' for action in prediction.recommended_actions)}

Maintenance scheduled: {task.scheduled_time.strftime('%Y-%m-%d %H:%M')}
Priority: {task.priority.upper()}
"""
                NotificationService.send_telegram(message)
        
        # Execute pending automated maintenance
        pending = self.scheduler.get_pending_tasks()
        for task in pending:
            if task.automated:
                self.scheduler.execute_automated_maintenance(task)
    
    def run(self, interval: int = 300):
        """Run continuous monitoring"""
        logger.info(f"Starting continuous monitoring (interval: {interval}s)")
        
        while True:
            try:
                self.run_cycle()
                time.sleep(interval)
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in prediction cycle: {e}", exc_info=True)
                time.sleep(60)

def main():
    """Main entry point"""
    system = PredictiveMaintenanceSystem()
    system.initialize()
    
    # Train on first run
    if '--train' in sys.argv:
        system.train(lookback_hours=168)
    
    # Run predictions
    if '--predict' in sys.argv:
        results = system.predict()
        for result in results:
            print(json.dumps({
                'component': result.component,
                'failure_probability': result.failure_probability,
                'confidence': result.confidence,
                'contributing_factors': result.contributing_factors
            }, indent=2))
    
    # Continuous monitoring
    if '--monitor' in sys.argv:
        system.run(interval=300)

if __name__ == '__main__':
    main()
