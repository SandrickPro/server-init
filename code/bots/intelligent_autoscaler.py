#!/usr/bin/env python3
"""
Intelligent Auto-Scaler v11.0
AI-driven Kubernetes auto-scaling with predictive capabilities
"""

import os
import sys
import time
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

import numpy as np
import pandas as pd
from kubernetes import client, config
from kubernetes.client.rest import ApiException

# ML Libraries
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import xgboost as xgb

# Monitoring
import requests
from prometheus_client import Gauge, Counter
from redis import Redis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus Metrics
SCALING_DECISIONS_COUNTER = Counter('autoscaler_decisions_total', 'Total scaling decisions', ['action', 'deployment'])
PREDICTED_LOAD_GAUGE = Gauge('autoscaler_predicted_load', 'Predicted workload', ['deployment'])
CURRENT_REPLICAS_GAUGE = Gauge('autoscaler_current_replicas', 'Current replica count', ['deployment'])
COST_SAVINGS_GAUGE = Gauge('autoscaler_cost_savings_usd', 'Estimated cost savings', ['deployment'])

# Configuration
PROMETHEUS_URL = os.getenv('PROMETHEUS_URL', 'http://localhost:9090')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
MIN_REPLICAS = int(os.getenv('MIN_REPLICAS', '2'))
MAX_REPLICAS = int(os.getenv('MAX_REPLICAS', '50'))
TARGET_CPU_UTILIZATION = float(os.getenv('TARGET_CPU_UTILIZATION', '0.7'))
TARGET_MEMORY_UTILIZATION = float(os.getenv('TARGET_MEMORY_UTILIZATION', '0.8'))
SCALE_UP_THRESHOLD = float(os.getenv('SCALE_UP_THRESHOLD', '0.85'))
SCALE_DOWN_THRESHOLD = float(os.getenv('SCALE_DOWN_THRESHOLD', '0.5'))
PREDICTION_WINDOW = int(os.getenv('PREDICTION_WINDOW', '15'))  # minutes
COST_PER_POD_HOUR = float(os.getenv('COST_PER_POD_HOUR', '0.05'))

@dataclass
class ScalingDecision:
    """Represents a scaling decision"""
    deployment: str
    namespace: str
    current_replicas: int
    target_replicas: int
    reason: str
    confidence: float
    predicted_load: float
    estimated_cost_impact: float

@dataclass
class WorkloadMetrics:
    """Current workload metrics"""
    cpu_usage: float
    memory_usage: float
    request_rate: float
    response_time: float
    error_rate: float
    active_connections: int

class PrometheusClient:
    """Client for querying Prometheus"""
    
    def __init__(self, url: str = PROMETHEUS_URL):
        self.url = url
        
    def query(self, query: str) -> Dict:
        """Execute Prometheus query"""
        try:
            response = requests.get(
                f"{self.url}/api/v1/query",
                params={'query': query},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Prometheus query failed: {e}")
            return {}
    
    def query_range(self, query: str, start: datetime, end: datetime, step: str = '1m') -> Dict:
        """Execute Prometheus range query"""
        try:
            response = requests.get(
                f"{self.url}/api/v1/query_range",
                params={
                    'query': query,
                    'start': int(start.timestamp()),
                    'end': int(end.timestamp()),
                    'step': step
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Prometheus range query failed: {e}")
            return {}
    
    def get_deployment_metrics(self, deployment: str, namespace: str) -> Optional[WorkloadMetrics]:
        """Get current metrics for deployment"""
        try:
            # CPU usage
            cpu_query = f'avg(rate(container_cpu_usage_seconds_total{{namespace="{namespace}",pod=~"{deployment}-.*"}}[5m]))'
            cpu_result = self.query(cpu_query)
            cpu_usage = float(cpu_result['data']['result'][0]['value'][1]) if cpu_result.get('data', {}).get('result') else 0
            
            # Memory usage
            mem_query = f'avg(container_memory_usage_bytes{{namespace="{namespace}",pod=~"{deployment}-.*"}})'
            mem_result = self.query(mem_query)
            memory_usage = float(mem_result['data']['result'][0]['value'][1]) if mem_result.get('data', {}).get('result') else 0
            
            # Request rate
            req_query = f'sum(rate(http_requests_total{{deployment="{deployment}"}}[5m]))'
            req_result = self.query(req_query)
            request_rate = float(req_result['data']['result'][0]['value'][1]) if req_result.get('data', {}).get('result') else 0
            
            # Response time
            resp_query = f'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{{deployment="{deployment}"}}[5m]))'
            resp_result = self.query(resp_query)
            response_time = float(resp_result['data']['result'][0]['value'][1]) if resp_result.get('data', {}).get('result') else 0
            
            # Error rate
            err_query = f'sum(rate(http_requests_total{{deployment="{deployment}",status=~"5.."}}[5m]))'
            err_result = self.query(err_query)
            error_rate = float(err_result['data']['result'][0]['value'][1]) if err_result.get('data', {}).get('result') else 0
            
            return WorkloadMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                request_rate=request_rate,
                response_time=response_time,
                error_rate=error_rate,
                active_connections=0
            )
        except Exception as e:
            logger.error(f"Failed to get metrics for {deployment}: {e}")
            return None
    
    def get_historical_metrics(self, deployment: str, namespace: str, hours: int = 24) -> pd.DataFrame:
        """Get historical metrics"""
        end = datetime.now()
        start = end - timedelta(hours=hours)
        
        metrics = {
            'cpu': f'avg(rate(container_cpu_usage_seconds_total{{namespace="{namespace}",pod=~"{deployment}-.*"}}[5m]))',
            'memory': f'avg(container_memory_usage_bytes{{namespace="{namespace}",pod=~"{deployment}-.*"}})',
            'requests': f'sum(rate(http_requests_total{{deployment="{deployment}"}}[5m]))',
            'response_time': f'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{{deployment="{deployment}"}}[5m]))',
        }
        
        all_data = []
        
        for metric_name, query in metrics.items():
            result = self.query_range(query, start, end, step='5m')
            
            if result.get('data', {}).get('result'):
                for timestamp, value in result['data']['result'][0]['values']:
                    all_data.append({
                        'timestamp': datetime.fromtimestamp(timestamp),
                        'metric': metric_name,
                        'value': float(value)
                    })
        
        df = pd.DataFrame(all_data)
        if not df.empty:
            df = df.pivot(index='timestamp', columns='metric', values='value').reset_index()
        
        return df

class LoadPredictor:
    """ML-based load prediction"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for ML"""
        if df.empty:
            return pd.DataFrame()
        
        # Time-based features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_business_hours'] = df['hour'].between(9, 17).astype(int)
        
        # Lag features
        for col in ['cpu', 'memory', 'requests']:
            if col in df.columns:
                df[f'{col}_lag_1'] = df[col].shift(1)
                df[f'{col}_lag_2'] = df[col].shift(2)
                df[f'{col}_lag_3'] = df[col].shift(3)
        
        # Rolling statistics
        for col in ['cpu', 'memory', 'requests']:
            if col in df.columns:
                df[f'{col}_rolling_mean_6'] = df[col].rolling(window=6, min_periods=1).mean()
                df[f'{col}_rolling_std_6'] = df[col].rolling(window=6, min_periods=1).std()
                df[f'{col}_rolling_max_12'] = df[col].rolling(window=12, min_periods=1).max()
        
        # Rate of change
        for col in ['cpu', 'memory', 'requests']:
            if col in df.columns:
                df[f'{col}_change'] = df[col].diff()
                df[f'{col}_pct_change'] = df[col].pct_change()
        
        # Fill NaN
        df = df.fillna(method='bfill').fillna(0)
        
        return df
    
    def train(self, df: pd.DataFrame, target_col: str = 'requests'):
        """Train prediction model"""
        if df.empty or target_col not in df.columns:
            logger.warning("Insufficient data for training")
            return
        
        # Prepare features
        df_features = self.prepare_features(df)
        
        # Select features (exclude timestamp and target)
        feature_cols = [col for col in df_features.columns 
                       if col not in ['timestamp', target_col] and not col.startswith('response_time')]
        
        X = df_features[feature_cols]
        y = df_features[target_col]
        
        # Remove rows with NaN in target
        mask = ~y.isna()
        X = X[mask]
        y = y[mask]
        
        if len(X) < 50:
            logger.warning(f"Insufficient samples for training: {len(X)}")
            return
        
        # Split train/test
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train models
        models_to_try = {
            'random_forest': RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1),
            'xgboost': xgb.XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
        }
        
        best_model_name = None
        best_score = -float('inf')
        
        for name, model in models_to_try.items():
            model.fit(X_train_scaled, y_train)
            
            y_pred = model.predict(X_test_scaled)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            logger.info(f"{name} - MAE: {mae:.3f}, R²: {r2:.3f}")
            
            if r2 > best_score:
                best_score = r2
                best_model_name = name
                self.models[target_col] = model
                self.scalers[target_col] = scaler
                self.feature_columns = feature_cols
        
        logger.info(f"Best model for {target_col}: {best_model_name} (R²: {best_score:.3f})")
    
    def predict(self, df: pd.DataFrame, target_col: str = 'requests', steps_ahead: int = 3) -> np.ndarray:
        """Predict future load"""
        if target_col not in self.models:
            logger.warning(f"No model trained for {target_col}")
            return np.array([])
        
        model = self.models[target_col]
        scaler = self.scalers[target_col]
        
        # Prepare features
        df_features = self.prepare_features(df)
        
        predictions = []
        current_df = df_features.copy()
        
        for _ in range(steps_ahead):
            # Get latest features
            X = current_df[self.feature_columns].iloc[-1:]
            X_scaled = scaler.transform(X)
            
            # Predict
            pred = model.predict(X_scaled)[0]
            predictions.append(pred)
            
            # Update dataframe with prediction for next iteration
            new_row = current_df.iloc[-1].copy()
            new_row[target_col] = pred
            new_row['timestamp'] = new_row['timestamp'] + timedelta(minutes=5)
            
            current_df = pd.concat([current_df, pd.DataFrame([new_row])], ignore_index=True)
            current_df = self.prepare_features(current_df)
        
        return np.array(predictions)

class IntelligentAutoScaler:
    """AI-driven auto-scaler"""
    
    def __init__(self):
        # Initialize Kubernetes client
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()
        
        self.apps_v1 = client.AppsV1Api()
        self.prometheus = PrometheusClient()
        self.predictor = LoadPredictor()
        self.redis = Redis(host=REDIS_HOST, decode_responses=True)
        
    def get_deployments(self, namespace: str = 'production') -> List[str]:
        """Get list of deployments"""
        try:
            deployments = self.apps_v1.list_namespaced_deployment(namespace)
            return [d.metadata.name for d in deployments.items]
        except ApiException as e:
            logger.error(f"Failed to list deployments: {e}")
            return []
    
    def get_current_replicas(self, deployment: str, namespace: str) -> int:
        """Get current replica count"""
        try:
            dep = self.apps_v1.read_namespaced_deployment(deployment, namespace)
            return dep.spec.replicas
        except ApiException as e:
            logger.error(f"Failed to get replicas for {deployment}: {e}")
            return 0
    
    def scale_deployment(self, deployment: str, namespace: str, replicas: int) -> bool:
        """Scale deployment to specified replicas"""
        try:
            # Read deployment
            dep = self.apps_v1.read_namespaced_deployment(deployment, namespace)
            
            # Update replicas
            dep.spec.replicas = replicas
            
            # Patch deployment
            self.apps_v1.patch_namespaced_deployment(deployment, namespace, dep)
            
            logger.info(f"Scaled {deployment} to {replicas} replicas")
            return True
            
        except ApiException as e:
            logger.error(f"Failed to scale {deployment}: {e}")
            return False
    
    def calculate_required_replicas(
        self,
        deployment: str,
        namespace: str,
        current_replicas: int,
        metrics: WorkloadMetrics,
        predicted_load: float
    ) -> Tuple[int, str, float]:
        """Calculate required replicas based on metrics and prediction"""
        
        reasons = []
        scores = []
        
        # CPU-based calculation
        if metrics.cpu_usage > 0:
            cpu_replicas = int(np.ceil(current_replicas * (metrics.cpu_usage / TARGET_CPU_UTILIZATION)))
            if metrics.cpu_usage > SCALE_UP_THRESHOLD:
                reasons.append(f"CPU usage {metrics.cpu_usage:.1%} > threshold {SCALE_UP_THRESHOLD:.1%}")
                scores.append(cpu_replicas)
        
        # Memory-based calculation
        if metrics.memory_usage > 0:
            mem_replicas = int(np.ceil(current_replicas * (metrics.memory_usage / TARGET_MEMORY_UTILIZATION)))
            if metrics.memory_usage > SCALE_UP_THRESHOLD:
                reasons.append(f"Memory usage {metrics.memory_usage:.1%} > threshold")
                scores.append(mem_replicas)
        
        # Request rate prediction
        if predicted_load > 0:
            # Assume each pod can handle 100 RPS
            capacity_per_pod = 100
            predicted_replicas = int(np.ceil(predicted_load / capacity_per_pod))
            
            if predicted_replicas > current_replicas:
                reasons.append(f"Predicted load {predicted_load:.0f} RPS requires more capacity")
                scores.append(predicted_replicas)
        
        # Response time degradation
        if metrics.response_time > 1.0:  # >1s response time
            reasons.append(f"High response time {metrics.response_time:.2f}s")
            scale_factor = min(2.0, metrics.response_time)
            scores.append(int(current_replicas * scale_factor))
        
        # Error rate increase
        if metrics.error_rate > 0.01:  # >1% errors
            reasons.append(f"High error rate {metrics.error_rate:.2%}")
            scores.append(int(current_replicas * 1.5))
        
        # Scale down if underutilized
        if (metrics.cpu_usage < SCALE_DOWN_THRESHOLD and 
            metrics.memory_usage < SCALE_DOWN_THRESHOLD and
            metrics.request_rate < 10):
            reasons.append(f"Low utilization (CPU: {metrics.cpu_usage:.1%}, Mem: {metrics.memory_usage:.1%})")
            scores.append(max(MIN_REPLICAS, int(current_replicas * 0.7)))
        
        # Calculate target replicas
        if scores:
            target_replicas = int(np.median(scores))
        else:
            target_replicas = current_replicas
        
        # Apply constraints
        target_replicas = max(MIN_REPLICAS, min(MAX_REPLICAS, target_replicas))
        
        # Calculate confidence
        confidence = 0.8 if len(scores) > 2 else 0.6
        
        reason = "; ".join(reasons) if reasons else "No scaling needed"
        
        return target_replicas, reason, confidence
    
    def make_scaling_decision(self, deployment: str, namespace: str = 'production') -> Optional[ScalingDecision]:
        """Make intelligent scaling decision"""
        
        # Get current state
        current_replicas = self.get_current_replicas(deployment, namespace)
        if current_replicas == 0:
            return None
        
        # Get current metrics
        metrics = self.prometheus.get_deployment_metrics(deployment, namespace)
        if not metrics:
            logger.warning(f"No metrics available for {deployment}")
            return None
        
        # Get historical data and train/predict
        historical_df = self.prometheus.get_historical_metrics(deployment, namespace, hours=24)
        
        predicted_load = 0
        if not historical_df.empty and 'requests' in historical_df.columns:
            # Train model if not already trained
            if 'requests' not in self.predictor.models:
                self.predictor.train(historical_df, target_col='requests')
            
            # Predict future load
            predictions = self.predictor.predict(historical_df, target_col='requests', steps_ahead=3)
            if len(predictions) > 0:
                predicted_load = np.mean(predictions)
                PREDICTED_LOAD_GAUGE.labels(deployment=deployment).set(predicted_load)
        
        # Calculate required replicas
        target_replicas, reason, confidence = self.calculate_required_replicas(
            deployment, namespace, current_replicas, metrics, predicted_load
        )
        
        # Calculate cost impact
        replica_diff = target_replicas - current_replicas
        estimated_cost_impact = replica_diff * COST_PER_POD_HOUR * 24 * 30  # Monthly cost
        
        # Create decision
        decision = ScalingDecision(
            deployment=deployment,
            namespace=namespace,
            current_replicas=current_replicas,
            target_replicas=target_replicas,
            reason=reason,
            confidence=confidence,
            predicted_load=predicted_load,
            estimated_cost_impact=estimated_cost_impact
        )
        
        # Update metrics
        CURRENT_REPLICAS_GAUGE.labels(deployment=deployment).set(current_replicas)
        
        if abs(estimated_cost_impact) > 0:
            COST_SAVINGS_GAUGE.labels(deployment=deployment).set(-estimated_cost_impact)
        
        return decision
    
    def execute_decision(self, decision: ScalingDecision, dry_run: bool = False) -> bool:
        """Execute scaling decision"""
        
        if decision.current_replicas == decision.target_replicas:
            logger.info(f"{decision.deployment}: No scaling needed ({decision.current_replicas} replicas)")
            return True
        
        action = 'scale_up' if decision.target_replicas > decision.current_replicas else 'scale_down'
        
        logger.info(f"""
{'[DRY RUN] ' if dry_run else ''}Scaling Decision for {decision.deployment}:
  Current: {decision.current_replicas} replicas
  Target: {decision.target_replicas} replicas
  Action: {action}
  Reason: {decision.reason}
  Confidence: {decision.confidence:.1%}
  Predicted Load: {decision.predicted_load:.0f} RPS
  Cost Impact: ${decision.estimated_cost_impact:.2f}/month
""")
        
        if dry_run:
            return True
        
        # Execute scaling
        success = self.scale_deployment(
            decision.deployment,
            decision.namespace,
            decision.target_replicas
        )
        
        if success:
            SCALING_DECISIONS_COUNTER.labels(action=action, deployment=decision.deployment).inc()
            
            # Store decision in Redis
            self.redis.setex(
                f"scaling_decision:{decision.deployment}:{int(time.time())}",
                86400,
                json.dumps({
                    'deployment': decision.deployment,
                    'action': action,
                    'from_replicas': decision.current_replicas,
                    'to_replicas': decision.target_replicas,
                    'reason': decision.reason,
                    'confidence': decision.confidence,
                    'timestamp': datetime.now().isoformat()
                })
            )
        
        return success
    
    def run_cycle(self, namespace: str = 'production', dry_run: bool = False):
        """Run one scaling cycle"""
        logger.info(f"{'[DRY RUN] ' if dry_run else ''}Running auto-scaling cycle...")
        
        deployments = self.get_deployments(namespace)
        logger.info(f"Found {len(deployments)} deployments in {namespace}")
        
        for deployment in deployments:
            try:
                decision = self.make_scaling_decision(deployment, namespace)
                
                if decision:
                    self.execute_decision(decision, dry_run=dry_run)
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error processing {deployment}: {e}", exc_info=True)
        
        logger.info("Auto-scaling cycle complete")
    
    def run(self, interval: int = 60, namespace: str = 'production', dry_run: bool = False):
        """Run continuous auto-scaling"""
        logger.info(f"Starting intelligent auto-scaler (interval: {interval}s)")
        
        while True:
            try:
                self.run_cycle(namespace, dry_run)
                time.sleep(interval)
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in scaling cycle: {e}", exc_info=True)
                time.sleep(60)

def main():
    """Main entry point"""
    scaler = IntelligentAutoScaler()
    
    namespace = os.getenv('NAMESPACE', 'production')
    interval = int(os.getenv('INTERVAL', '60'))
    dry_run = '--dry-run' in sys.argv
    
    if '--once' in sys.argv:
        scaler.run_cycle(namespace, dry_run)
    else:
        scaler.run(interval, namespace, dry_run)

if __name__ == '__main__':
    main()
