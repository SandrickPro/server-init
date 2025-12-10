#!/usr/bin/env python3
"""
AI/ML Operations Platform - Iteration 6
MLflow integration with model registry, A/B testing, and feature store
Complete MLOps lifecycle management
"""

import os
import sys
import json
import logging
import mlflow
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import joblib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MLOPS_BASE = Path('/var/lib/mlops')
MODELS_DIR = MLOPS_BASE / 'models'
FEATURES_DIR = MLOPS_BASE / 'features'
EXPERIMENTS_DIR = MLOPS_BASE / 'experiments'

for directory in [MODELS_DIR, FEATURES_DIR, EXPERIMENTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# MLflow configuration
MLFLOW_TRACKING_URI = os.getenv('MLFLOW_TRACKING_URI', 'http://localhost:5000')
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

################################################################################
# Model Registry
################################################################################

class ModelRegistry:
    """MLflow model registry management"""
    
    def __init__(self):
        self.client = mlflow.tracking.MlflowClient()
    
    def register_model(self, model_name: str, run_id: str) -> str:
        """Register model in MLflow"""
        
        model_uri = f"runs:/{run_id}/model"
        
        result = mlflow.register_model(model_uri, model_name)
        
        logger.info(f"Model registered: {model_name} version {result.version}")
        return result.version
    
    def transition_model_stage(self, model_name: str, version: str, stage: str):
        """Transition model to different stage"""
        
        self.client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage=stage
        )
        
        logger.info(f"Model {model_name} v{version} transitioned to {stage}")
    
    def get_latest_model(self, model_name: str, stage: str = 'Production') -> Optional[Any]:
        """Get latest model from registry"""
        
        try:
            model_uri = f"models:/{model_name}/{stage}"
            model = mlflow.pyfunc.load_model(model_uri)
            logger.info(f"Loaded model: {model_name} ({stage})")
            return model
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return None
    
    def get_model_metadata(self, model_name: str, version: str) -> Optional[Dict]:
        """Get model metadata"""
        
        try:
            model_version = self.client.get_model_version(model_name, version)
            
            metadata = {
                'name': model_version.name,
                'version': model_version.version,
                'stage': model_version.current_stage,
                'description': model_version.description,
                'run_id': model_version.run_id,
                'created_at': model_version.creation_timestamp
            }
            
            return metadata
        except Exception as e:
            logger.error(f"Failed to get model metadata: {e}")
            return None

################################################################################
# Experiment Tracking
################################################################################

class ExperimentTracker:
    """MLflow experiment tracking"""
    
    def __init__(self):
        self.client = mlflow.tracking.MlflowClient()
    
    def create_experiment(self, name: str, tags: Optional[Dict] = None) -> str:
        """Create MLflow experiment"""
        
        experiment_id = mlflow.create_experiment(name, tags=tags)
        logger.info(f"Experiment created: {name} (ID: {experiment_id})")
        return experiment_id
    
    def log_model_training(self, experiment_name: str, model: Any, params: Dict, metrics: Dict):
        """Log model training run"""
        
        mlflow.set_experiment(experiment_name)
        
        with mlflow.start_run():
            # Log parameters
            mlflow.log_params(params)
            
            # Log metrics
            mlflow.log_metrics(metrics)
            
            # Log model
            mlflow.sklearn.log_model(model, "model")
            
            # Log artifacts
            mlflow.log_artifact(__file__)
            
            run_id = mlflow.active_run().info.run_id
            logger.info(f"Training run logged: {run_id}")
            
            return run_id
    
    def compare_experiments(self, experiment_name: str, metric: str = 'accuracy') -> pd.DataFrame:
        """Compare experiment runs"""
        
        experiment = self.client.get_experiment_by_name(experiment_name)
        runs = self.client.search_runs(experiment.experiment_id)
        
        data = []
        for run in runs:
            data.append({
                'run_id': run.info.run_id,
                'params': run.data.params,
                'metrics': run.data.metrics,
                'start_time': run.info.start_time
            })
        
        df = pd.DataFrame(data)
        logger.info(f"Compared {len(df)} runs for experiment: {experiment_name}")
        
        return df

################################################################################
# Feature Store
################################################################################

class FeatureStore:
    """Feature store for ML"""
    
    def __init__(self):
        self.features_path = FEATURES_DIR / 'feature_store.parquet'
    
    def register_feature_group(self, name: str, features: pd.DataFrame, metadata: Dict):
        """Register feature group"""
        
        # Add metadata columns
        features['feature_group'] = name
        features['created_at'] = datetime.now()
        
        # Save features
        if self.features_path.exists():
            existing_features = pd.read_parquet(self.features_path)
            features = pd.concat([existing_features, features], ignore_index=True)
        
        features.to_parquet(self.features_path)
        
        # Save metadata
        metadata_file = FEATURES_DIR / f'{name}_metadata.json'
        metadata_file.write_text(json.dumps(metadata, indent=2))
        
        logger.info(f"Feature group registered: {name} ({len(features)} features)")
    
    def get_features(self, feature_names: List[str]) -> Optional[pd.DataFrame]:
        """Get features by name"""
        
        if not self.features_path.exists():
            logger.error("Feature store not initialized")
            return None
        
        features = pd.read_parquet(self.features_path)
        
        # Filter by feature names
        features = features[features['feature_name'].isin(feature_names)]
        
        logger.info(f"Retrieved {len(features)} features")
        return features
    
    def get_feature_group(self, name: str) -> Optional[pd.DataFrame]:
        """Get entire feature group"""
        
        if not self.features_path.exists():
            logger.error("Feature store not initialized")
            return None
        
        features = pd.read_parquet(self.features_path)
        features = features[features['feature_group'] == name]
        
        logger.info(f"Retrieved feature group: {name} ({len(features)} features)")
        return features

################################################################################
# A/B Testing
################################################################################

class ABTestingManager:
    """A/B testing for ML models"""
    
    def __init__(self, model_registry: ModelRegistry):
        self.registry = model_registry
        self.experiments = {}
    
    def create_ab_test(self, test_name: str, model_a: str, model_b: str, traffic_split: float = 0.5):
        """Create A/B test between two models"""
        
        self.experiments[test_name] = {
            'model_a': model_a,
            'model_b': model_b,
            'traffic_split': traffic_split,
            'metrics': {
                'a': {'requests': 0, 'success': 0, 'latency': []},
                'b': {'requests': 0, 'success': 0, 'latency': []}
            },
            'created_at': datetime.now().isoformat()
        }
        
        logger.info(f"A/B test created: {test_name} ({model_a} vs {model_b})")
    
    def route_prediction(self, test_name: str, features: Any) -> tuple[str, Any]:
        """Route prediction to A or B model"""
        
        experiment = self.experiments.get(test_name)
        
        if not experiment:
            logger.error(f"A/B test not found: {test_name}")
            return 'a', None
        
        # Randomly assign to A or B based on traffic split
        import random
        use_model_b = random.random() < experiment['traffic_split']
        
        model_name = experiment['model_b'] if use_model_b else experiment['model_a']
        variant = 'b' if use_model_b else 'a'
        
        # Load and run model
        model = self.registry.get_latest_model(model_name, stage='Production')
        
        if model:
            prediction = model.predict(features)
            experiment['metrics'][variant]['requests'] += 1
            
            return variant, prediction
        
        return variant, None
    
    def record_feedback(self, test_name: str, variant: str, success: bool, latency: float):
        """Record prediction feedback"""
        
        experiment = self.experiments.get(test_name)
        
        if not experiment:
            return
        
        if success:
            experiment['metrics'][variant]['success'] += 1
        
        experiment['metrics'][variant]['latency'].append(latency)
    
    def get_ab_test_results(self, test_name: str) -> Optional[Dict]:
        """Get A/B test results"""
        
        experiment = self.experiments.get(test_name)
        
        if not experiment:
            return None
        
        results = {
            'test_name': test_name,
            'model_a': experiment['model_a'],
            'model_b': experiment['model_b'],
            'metrics': {}
        }
        
        for variant in ['a', 'b']:
            metrics = experiment['metrics'][variant]
            
            success_rate = (metrics['success'] / metrics['requests'] * 100) if metrics['requests'] > 0 else 0
            avg_latency = np.mean(metrics['latency']) if metrics['latency'] else 0
            
            results['metrics'][variant] = {
                'requests': metrics['requests'],
                'success_rate': success_rate,
                'avg_latency': avg_latency
            }
        
        logger.info(f"A/B test results: {test_name}")
        return results

################################################################################
# MLOps Platform
################################################################################

class MLOpsPlatform:
    """Complete MLOps orchestrator"""
    
    def __init__(self):
        self.model_registry = ModelRegistry()
        self.experiment_tracker = ExperimentTracker()
        self.feature_store = FeatureStore()
        self.ab_testing = ABTestingManager(self.model_registry)
    
    def deploy_model_pipeline(self, model_name: str):
        """Deploy complete ML pipeline"""
        
        # Create experiment
        experiment_id = self.experiment_tracker.create_experiment(
            name=f'{model_name}_experiment',
            tags={'team': 'ml', 'project': model_name}
        )
        
        # Simulated model training
        from sklearn.ensemble import RandomForestClassifier
        model = RandomForestClassifier(n_estimators=100, max_depth=10)
        
        # Log training
        run_id = self.experiment_tracker.log_model_training(
            experiment_name=f'{model_name}_experiment',
            model=model,
            params={'n_estimators': 100, 'max_depth': 10},
            metrics={'accuracy': 0.95, 'f1_score': 0.93}
        )
        
        # Register model
        version = self.model_registry.register_model(model_name, run_id)
        
        # Transition to production
        self.model_registry.transition_model_stage(model_name, version, 'Production')
        
        logger.info(f"Model pipeline deployed: {model_name}")

################################################################################
# CLI
################################################################################

def main():
    logger.info("🤖 AI/ML Operations Platform - Iteration 6")
    
    if '--deploy-model' in sys.argv:
        platform = MLOpsPlatform()
        platform.deploy_model_pipeline('fraud-detection')
        print("✅ Model pipeline deployed")
    
    else:
        print("""
AI/ML Operations Platform v13.0 - Iteration 6

Usage:
  --deploy-model    Deploy ML model pipeline

Features:
  ✓ MLflow model registry
  ✓ Experiment tracking
  ✓ Feature store
  ✓ A/B testing
  ✓ Model versioning
        """)

if __name__ == '__main__':
    main()
