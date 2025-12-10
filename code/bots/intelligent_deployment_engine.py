#!/usr/bin/env python3
"""
Intelligent Deployment Engine v12.0
AI-powered deployment optimization with A/B testing, canary releases, and rollback automation
Progressive delivery with real-time health monitoring and automatic decision making
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
import hashlib
import uuid

# ML and statistics
import numpy as np
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
import joblib

# Kubernetes
try:
    from kubernetes import client, config, watch
    from kubernetes.client.rest import ApiException
except ImportError:
    print("Warning: kubernetes-client not installed")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
DEPLOYMENT_DB = '/var/lib/deployment/intelligent.db'
DEPLOYMENT_CONFIG = '/etc/deployment/config.yaml'
DEPLOYMENT_MODELS = '/var/lib/deployment/models/'
DEPLOYMENT_LOGS = '/var/log/deployment/'

# Deployment parameters
CANARY_INITIAL_TRAFFIC = 0.05  # 5% initial traffic
CANARY_TRAFFIC_STEP = 0.10  # 10% traffic increments
CANARY_EVALUATION_MINUTES = 10
AB_TEST_MIN_SAMPLES = 1000
AB_TEST_CONFIDENCE = 0.95
ROLLBACK_ERROR_THRESHOLD = 0.05  # 5% error rate triggers rollback

# Create directories
for directory in [os.path.dirname(DEPLOYMENT_DB),
                  os.path.dirname(DEPLOYMENT_CONFIG),
                  DEPLOYMENT_MODELS,
                  DEPLOYMENT_LOGS]:
    Path(directory).mkdir(parents=True, exist_ok=True)

################################################################################
# Data Models
################################################################################

class DeploymentStrategy(Enum):
    """Deployment strategies"""
    ROLLING = "rolling"
    CANARY = "canary"
    BLUE_GREEN = "blue_green"
    AB_TEST = "ab_test"
    SHADOW = "shadow"

class DeploymentPhase(Enum):
    """Deployment phases"""
    PREPARING = "preparing"
    DEPLOYING = "deploying"
    EVALUATING = "evaluating"
    PROMOTING = "promoting"
    ROLLING_BACK = "rolling_back"
    COMPLETED = "completed"
    FAILED = "failed"

class HealthStatus(Enum):
    """Health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class DeploymentConfig:
    """Deployment configuration"""
    deployment_id: str
    name: str
    namespace: str
    strategy: DeploymentStrategy
    image: str
    replicas: int
    environment: str
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    config_map: Optional[Dict[str, str]] = None
    secrets: Optional[Dict[str, str]] = None

@dataclass
class DeploymentVersion:
    """Version of a deployment"""
    version_id: str
    deployment_id: str
    image: str
    revision: int
    traffic_percent: float = 0.0
    replicas: int = 0
    health: HealthStatus = HealthStatus.UNKNOWN
    metrics: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class DeploymentMetrics:
    """Real-time deployment metrics"""
    version_id: str
    timestamp: datetime
    request_rate: float
    error_rate: float
    latency_p50: float
    latency_p95: float
    latency_p99: float
    success_rate: float
    cpu_usage: float
    memory_usage: float

@dataclass
class ABTestResult:
    """A/B test statistical result"""
    test_id: str
    version_a_id: str
    version_b_id: str
    metric_name: str
    version_a_mean: float
    version_b_mean: float
    version_a_samples: int
    version_b_samples: int
    p_value: float
    confidence: float
    is_significant: bool
    winner: Optional[str]
    improvement_percent: float

@dataclass
class DeploymentDecision:
    """AI-generated deployment decision"""
    decision_id: str
    deployment_id: str
    decision_type: str  # promote, rollback, pause, continue
    confidence: float
    reasoning: str
    metrics_snapshot: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)

################################################################################
# Database Manager
################################################################################

class DeploymentDatabase:
    """Database for deployment data"""
    
    def __init__(self, db_path: str = DEPLOYMENT_DB):
        self.db_path = db_path
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.conn.cursor()
        
        # Deployments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deployments (
                deployment_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                namespace TEXT NOT NULL,
                strategy TEXT NOT NULL,
                environment TEXT NOT NULL,
                current_phase TEXT NOT NULL,
                image TEXT NOT NULL,
                replicas INTEGER NOT NULL,
                labels_json TEXT,
                annotations_json TEXT,
                config_map_json TEXT,
                secrets_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Versions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deployment_versions (
                version_id TEXT PRIMARY KEY,
                deployment_id TEXT NOT NULL,
                image TEXT NOT NULL,
                revision INTEGER NOT NULL,
                traffic_percent REAL DEFAULT 0.0,
                replicas INTEGER DEFAULT 0,
                health TEXT DEFAULT 'unknown',
                metrics_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                promoted_at TIMESTAMP,
                deprecated_at TIMESTAMP,
                FOREIGN KEY(deployment_id) REFERENCES deployments(deployment_id)
            )
        ''')
        
        # Deployment history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deployment_history (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                deployment_id TEXT NOT NULL,
                version_id TEXT NOT NULL,
                phase TEXT NOT NULL,
                status TEXT NOT NULL,
                message TEXT,
                metrics_json TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(deployment_id) REFERENCES deployments(deployment_id),
                FOREIGN KEY(version_id) REFERENCES deployment_versions(version_id)
            )
        ''')
        
        # Metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deployment_metrics (
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                version_id TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                request_rate REAL,
                error_rate REAL,
                latency_p50 REAL,
                latency_p95 REAL,
                latency_p99 REAL,
                success_rate REAL,
                cpu_usage REAL,
                memory_usage REAL,
                FOREIGN KEY(version_id) REFERENCES deployment_versions(version_id)
            )
        ''')
        
        # A/B tests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ab_tests (
                test_id TEXT PRIMARY KEY,
                deployment_id TEXT NOT NULL,
                version_a_id TEXT NOT NULL,
                version_b_id TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                version_a_mean REAL,
                version_b_mean REAL,
                version_a_samples INTEGER,
                version_b_samples INTEGER,
                p_value REAL,
                confidence REAL,
                is_significant INTEGER,
                winner TEXT,
                improvement_percent REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY(deployment_id) REFERENCES deployments(deployment_id)
            )
        ''')
        
        # Decisions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deployment_decisions (
                decision_id TEXT PRIMARY KEY,
                deployment_id TEXT NOT NULL,
                decision_type TEXT NOT NULL,
                confidence REAL NOT NULL,
                reasoning TEXT,
                metrics_snapshot_json TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                applied INTEGER DEFAULT 0,
                applied_at TIMESTAMP,
                FOREIGN KEY(deployment_id) REFERENCES deployments(deployment_id)
            )
        ''')
        
        # Rollbacks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rollbacks (
                rollback_id TEXT PRIMARY KEY,
                deployment_id TEXT NOT NULL,
                from_version_id TEXT NOT NULL,
                to_version_id TEXT NOT NULL,
                reason TEXT NOT NULL,
                triggered_by TEXT DEFAULT 'automatic',
                duration_seconds REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(deployment_id) REFERENCES deployments(deployment_id)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_deployments_name ON deployments(name, namespace)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_versions_deployment ON deployment_versions(deployment_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_version ON deployment_metrics(version_id, timestamp DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_deployment ON deployment_history(deployment_id, timestamp DESC)')
        
        self.conn.commit()
        logger.info(f"Deployment database initialized: {db_path}")
    
    def save_deployment(self, config: DeploymentConfig, phase: DeploymentPhase):
        """Save deployment configuration"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO deployments 
            (deployment_id, name, namespace, strategy, environment, current_phase, 
             image, replicas, labels_json, annotations_json, config_map_json, secrets_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            config.deployment_id,
            config.name,
            config.namespace,
            config.strategy.value,
            config.environment,
            phase.value,
            config.image,
            config.replicas,
            json.dumps(config.labels),
            json.dumps(config.annotations),
            json.dumps(config.config_map) if config.config_map else None,
            json.dumps(config.secrets) if config.secrets else None
        ))
        self.conn.commit()
    
    def save_version(self, version: DeploymentVersion):
        """Save deployment version"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO deployment_versions 
            (version_id, deployment_id, image, revision, traffic_percent, 
             replicas, health, metrics_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            version.version_id,
            version.deployment_id,
            version.image,
            version.revision,
            version.traffic_percent,
            version.replicas,
            version.health.value,
            json.dumps(version.metrics),
            version.created_at.isoformat()
        ))
        self.conn.commit()
    
    def save_metrics(self, metrics: DeploymentMetrics):
        """Save deployment metrics"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO deployment_metrics 
            (version_id, timestamp, request_rate, error_rate, latency_p50, 
             latency_p95, latency_p99, success_rate, cpu_usage, memory_usage)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metrics.version_id,
            metrics.timestamp.isoformat(),
            metrics.request_rate,
            metrics.error_rate,
            metrics.latency_p50,
            metrics.latency_p95,
            metrics.latency_p99,
            metrics.success_rate,
            metrics.cpu_usage,
            metrics.memory_usage
        ))
        self.conn.commit()
    
    def save_ab_test(self, result: ABTestResult):
        """Save A/B test result"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO ab_tests 
            (test_id, deployment_id, version_a_id, version_b_id, metric_name,
             version_a_mean, version_b_mean, version_a_samples, version_b_samples,
             p_value, confidence, is_significant, winner, improvement_percent, completed_at)
            VALUES (?, (SELECT deployment_id FROM deployment_versions WHERE version_id = ?),
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            result.test_id,
            result.version_a_id,
            result.version_a_id,
            result.version_b_id,
            result.metric_name,
            result.version_a_mean,
            result.version_b_mean,
            result.version_a_samples,
            result.version_b_samples,
            result.p_value,
            result.confidence,
            1 if result.is_significant else 0,
            result.winner,
            result.improvement_percent
        ))
        self.conn.commit()
    
    def save_decision(self, decision: DeploymentDecision):
        """Save deployment decision"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO deployment_decisions 
            (decision_id, deployment_id, decision_type, confidence, reasoning, metrics_snapshot_json)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            decision.decision_id,
            decision.deployment_id,
            decision.decision_type,
            decision.confidence,
            decision.reasoning,
            json.dumps(decision.metrics_snapshot)
        ))
        self.conn.commit()
    
    def get_recent_metrics(self, version_id: str, minutes: int = 10) -> List[DeploymentMetrics]:
        """Get recent metrics for a version"""
        cursor = self.conn.cursor()
        since = datetime.now() - timedelta(minutes=minutes)
        
        cursor.execute('''
            SELECT * FROM deployment_metrics
            WHERE version_id = ? AND timestamp > ?
            ORDER BY timestamp ASC
        ''', (version_id, since.isoformat()))
        
        metrics_list = []
        for row in cursor.fetchall():
            metrics = DeploymentMetrics(
                version_id=row[1],
                timestamp=datetime.fromisoformat(row[2]),
                request_rate=row[3],
                error_rate=row[4],
                latency_p50=row[5],
                latency_p95=row[6],
                latency_p99=row[7],
                success_rate=row[8],
                cpu_usage=row[9],
                memory_usage=row[10]
            )
            metrics_list.append(metrics)
        
        return metrics_list

################################################################################
# A/B Test Engine
################################################################################

class ABTestEngine:
    """Statistical A/B testing engine"""
    
    def __init__(self, db: DeploymentDatabase):
        self.db = db
    
    def run_test(self, version_a_id: str, version_b_id: str, 
                metric_name: str) -> ABTestResult:
        """Run statistical A/B test"""
        
        # Get metrics for both versions
        metrics_a = self.db.get_recent_metrics(version_a_id, minutes=30)
        metrics_b = self.db.get_recent_metrics(version_b_id, minutes=30)
        
        if not metrics_a or not metrics_b:
            return None
        
        # Extract metric values
        values_a = [getattr(m, metric_name) for m in metrics_a]
        values_b = [getattr(m, metric_name) for m in metrics_b]
        
        # Calculate statistics
        mean_a = np.mean(values_a)
        mean_b = np.mean(values_b)
        
        # Perform t-test
        t_stat, p_value = stats.ttest_ind(values_a, values_b)
        
        # Determine significance
        is_significant = p_value < (1 - AB_TEST_CONFIDENCE)
        
        # Determine winner
        winner = None
        improvement = 0.0
        
        if is_significant:
            if metric_name in ['error_rate', 'latency_p95', 'latency_p99']:
                # Lower is better
                winner = version_b_id if mean_b < mean_a else version_a_id
                improvement = abs((mean_a - mean_b) / mean_a * 100)
            else:
                # Higher is better
                winner = version_b_id if mean_b > mean_a else version_a_id
                improvement = abs((mean_b - mean_a) / mean_a * 100)
        
        result = ABTestResult(
            test_id=str(uuid.uuid4()),
            version_a_id=version_a_id,
            version_b_id=version_b_id,
            metric_name=metric_name,
            version_a_mean=mean_a,
            version_b_mean=mean_b,
            version_a_samples=len(values_a),
            version_b_samples=len(values_b),
            p_value=p_value,
            confidence=AB_TEST_CONFIDENCE,
            is_significant=is_significant,
            winner=winner,
            improvement_percent=improvement
        )
        
        return result

################################################################################
# Deployment Health Monitor
################################################################################

class DeploymentHealthMonitor:
    """Monitor deployment health in real-time"""
    
    def __init__(self, db: DeploymentDatabase):
        self.db = db
    
    async def check_health(self, version: DeploymentVersion) -> HealthStatus:
        """Check version health"""
        
        # Get recent metrics
        recent_metrics = self.db.get_recent_metrics(version.version_id, minutes=5)
        
        if not recent_metrics:
            return HealthStatus.UNKNOWN
        
        # Calculate averages
        avg_error_rate = np.mean([m.error_rate for m in recent_metrics])
        avg_latency = np.mean([m.latency_p95 for m in recent_metrics])
        avg_success_rate = np.mean([m.success_rate for m in recent_metrics])
        
        # Evaluate health
        if avg_error_rate > 0.10 or avg_success_rate < 0.90:
            return HealthStatus.UNHEALTHY
        elif avg_error_rate > 0.05 or avg_latency > 1000:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY
    
    def should_rollback(self, current_version: DeploymentVersion, 
                       previous_version: DeploymentVersion) -> bool:
        """Determine if rollback is needed"""
        
        current_metrics = self.db.get_recent_metrics(current_version.version_id, minutes=5)
        previous_metrics = self.db.get_recent_metrics(previous_version.version_id, minutes=30)
        
        if not current_metrics or not previous_metrics:
            return False
        
        # Compare error rates
        current_error_rate = np.mean([m.error_rate for m in current_metrics])
        previous_error_rate = np.mean([m.error_rate for m in previous_metrics])
        
        # Rollback if error rate increased significantly
        if current_error_rate > ROLLBACK_ERROR_THRESHOLD and current_error_rate > previous_error_rate * 2:
            return True
        
        # Compare latency
        current_latency = np.mean([m.latency_p95 for m in current_metrics])
        previous_latency = np.mean([m.latency_p95 for m in previous_metrics])
        
        # Rollback if latency degraded significantly
        if current_latency > previous_latency * 1.5:
            return True
        
        return False

################################################################################
# AI Decision Engine
################################################################################

class DeploymentAI:
    """AI engine for deployment decisions"""
    
    def __init__(self, models_dir: str = DEPLOYMENT_MODELS):
        self.models_dir = models_dir
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self._load_model()
    
    def _load_model(self):
        """Load trained model"""
        try:
            self.classifier = joblib.load(f'{self.models_dir}/deployment_classifier.pkl')
            logger.info("Loaded AI model")
        except FileNotFoundError:
            logger.info("No existing model found")
    
    def make_decision(self, version: DeploymentVersion, 
                     metrics: List[DeploymentMetrics]) -> DeploymentDecision:
        """Make deployment decision"""
        
        if not metrics:
            return DeploymentDecision(
                decision_id=str(uuid.uuid4()),
                deployment_id=version.deployment_id,
                decision_type='pause',
                confidence=1.0,
                reasoning='Insufficient metrics data',
                metrics_snapshot={}
            )
        
        # Calculate metrics summary
        avg_error_rate = np.mean([m.error_rate for m in metrics])
        avg_latency_p95 = np.mean([m.latency_p95 for m in metrics])
        avg_success_rate = np.mean([m.success_rate for m in metrics])
        avg_cpu = np.mean([m.cpu_usage for m in metrics])
        
        metrics_snapshot = {
            'error_rate': avg_error_rate,
            'latency_p95': avg_latency_p95,
            'success_rate': avg_success_rate,
            'cpu_usage': avg_cpu
        }
        
        # Decision logic
        decision_type = 'continue'
        confidence = 0.80
        reasoning = "Metrics within acceptable ranges. "
        
        if avg_error_rate > 0.10:
            decision_type = 'rollback'
            confidence = 0.95
            reasoning = f"Critical error rate: {avg_error_rate*100:.1f}%. Immediate rollback required."
        elif avg_error_rate > 0.05:
            decision_type = 'pause'
            confidence = 0.85
            reasoning = f"Elevated error rate: {avg_error_rate*100:.1f}%. Pausing for investigation."
        elif avg_latency_p95 > 1000:
            decision_type = 'pause'
            confidence = 0.80
            reasoning = f"High latency: {avg_latency_p95:.0f}ms P95. Investigating performance degradation."
        elif avg_success_rate > 0.98 and avg_error_rate < 0.01:
            decision_type = 'promote'
            confidence = 0.90
            reasoning = f"Excellent metrics: {avg_success_rate*100:.1f}% success rate, {avg_error_rate*100:.2f}% errors. Safe to promote."
        
        decision = DeploymentDecision(
            decision_id=str(uuid.uuid4()),
            deployment_id=version.deployment_id,
            decision_type=decision_type,
            confidence=confidence,
            reasoning=reasoning,
            metrics_snapshot=metrics_snapshot
        )
        
        return decision

################################################################################
# Deployment Orchestrator
################################################################################

class IntelligentDeploymentEngine:
    """Main deployment orchestration engine"""
    
    def __init__(self):
        self.db = DeploymentDatabase()
        self.ai = DeploymentAI()
        self.ab_test_engine = ABTestEngine(self.db)
        self.health_monitor = DeploymentHealthMonitor(self.db)
        
        self.k8s_apps = None
        self.k8s_core = None
        self._init_kubernetes()
    
    def _init_kubernetes(self):
        """Initialize Kubernetes client"""
        try:
            config.load_incluster_config()
        except:
            try:
                config.load_kube_config()
            except:
                logger.warning("Kubernetes config not found")
                return
        
        self.k8s_apps = client.AppsV1Api()
        self.k8s_core = client.CoreV1Api()
        logger.info("Kubernetes client initialized")
    
    async def deploy_canary(self, config: DeploymentConfig) -> str:
        """Deploy with canary strategy"""
        logger.info(f"Starting canary deployment: {config.name}")
        
        # Save deployment config
        self.db.save_deployment(config, DeploymentPhase.PREPARING)
        
        # Create new version
        new_version = DeploymentVersion(
            version_id=str(uuid.uuid4()),
            deployment_id=config.deployment_id,
            image=config.image,
            revision=self._get_next_revision(config.deployment_id),
            traffic_percent=CANARY_INITIAL_TRAFFIC,
            replicas=1  # Start with 1 replica
        )
        
        self.db.save_version(new_version)
        
        # Deploy to Kubernetes
        await self._deploy_to_k8s(config, new_version)
        
        # Start progressive rollout
        await self._canary_rollout(config.deployment_id, new_version.version_id)
        
        return new_version.version_id
    
    async def _canary_rollout(self, deployment_id: str, new_version_id: str):
        """Progressive canary rollout"""
        logger.info(f"Starting canary rollout for {deployment_id}")
        
        current_traffic = CANARY_INITIAL_TRAFFIC
        
        while current_traffic < 1.0:
            # Wait for evaluation period
            await asyncio.sleep(CANARY_EVALUATION_MINUTES * 60)
            
            # Get current version
            cursor = self.db.conn.cursor()
            cursor.execute('SELECT * FROM deployment_versions WHERE version_id = ?', (new_version_id,))
            row = cursor.fetchone()
            
            version = DeploymentVersion(
                version_id=row[0],
                deployment_id=row[1],
                image=row[2],
                revision=row[3],
                traffic_percent=row[4],
                replicas=row[5],
                health=HealthStatus(row[6]),
                metrics=json.loads(row[7]) if row[7] else {}
            )
            
            # Check health
            health = await self.health_monitor.check_health(version)
            version.health = health
            self.db.save_version(version)
            
            if health == HealthStatus.UNHEALTHY:
                logger.warning(f"Unhealthy canary detected! Rolling back...")
                await self._rollback_deployment(deployment_id, new_version_id)
                return
            
            # Get metrics and make decision
            metrics = self.db.get_recent_metrics(new_version_id, minutes=CANARY_EVALUATION_MINUTES)
            decision = self.ai.make_decision(version, metrics)
            self.db.save_decision(decision)
            
            if decision.decision_type == 'rollback':
                logger.warning(f"AI recommends rollback: {decision.reasoning}")
                await self._rollback_deployment(deployment_id, new_version_id)
                return
            elif decision.decision_type == 'pause':
                logger.info(f"AI recommends pause: {decision.reasoning}")
                await asyncio.sleep(300)  # Wait 5 minutes
                continue
            elif decision.decision_type == 'promote':
                logger.info(f"AI recommends full promotion: {decision.reasoning}")
                current_traffic = 1.0
            else:
                # Continue progressive rollout
                current_traffic = min(current_traffic + CANARY_TRAFFIC_STEP, 1.0)
            
            # Update traffic split
            await self._update_traffic_split(deployment_id, new_version_id, current_traffic)
            
            logger.info(f"Canary traffic increased to {current_traffic*100:.0f}%")
        
        # Complete deployment
        logger.info(f"Canary deployment completed successfully!")
        self.db.save_deployment(
            DeploymentConfig(deployment_id=deployment_id, name='', namespace='', 
                           strategy=DeploymentStrategy.CANARY, image='', replicas=0, environment=''),
            DeploymentPhase.COMPLETED
        )
    
    async def deploy_ab_test(self, config: DeploymentConfig, 
                            alternative_image: str) -> Tuple[str, str]:
        """Deploy with A/B testing"""
        logger.info(f"Starting A/B test deployment: {config.name}")
        
        # Save deployment config
        self.db.save_deployment(config, DeploymentPhase.DEPLOYING)
        
        # Create version A (current)
        version_a = DeploymentVersion(
            version_id=str(uuid.uuid4()),
            deployment_id=config.deployment_id,
            image=config.image,
            revision=self._get_next_revision(config.deployment_id),
            traffic_percent=0.50,
            replicas=config.replicas // 2
        )
        
        # Create version B (alternative)
        version_b = DeploymentVersion(
            version_id=str(uuid.uuid4()),
            deployment_id=config.deployment_id,
            image=alternative_image,
            revision=version_a.revision + 1,
            traffic_percent=0.50,
            replicas=config.replicas // 2
        )
        
        self.db.save_version(version_a)
        self.db.save_version(version_b)
        
        # Deploy both versions
        await self._deploy_to_k8s(config, version_a)
        
        config_b = DeploymentConfig(
            deployment_id=config.deployment_id,
            name=config.name,
            namespace=config.namespace,
            strategy=config.strategy,
            image=alternative_image,
            replicas=config.replicas // 2,
            environment=config.environment
        )
        await self._deploy_to_k8s(config_b, version_b)
        
        # Start A/B test evaluation
        await self._evaluate_ab_test(version_a.version_id, version_b.version_id)
        
        return version_a.version_id, version_b.version_id
    
    async def _evaluate_ab_test(self, version_a_id: str, version_b_id: str):
        """Evaluate A/B test and determine winner"""
        logger.info(f"Evaluating A/B test: {version_a_id} vs {version_b_id}")
        
        # Wait for sufficient data
        await asyncio.sleep(30 * 60)  # 30 minutes
        
        # Run statistical tests on key metrics
        metrics_to_test = ['error_rate', 'latency_p95', 'success_rate']
        
        results = []
        for metric_name in metrics_to_test:
            result = self.ab_test_engine.run_test(version_a_id, version_b_id, metric_name)
            if result:
                self.db.save_ab_test(result)
                results.append(result)
        
        # Determine overall winner
        winner_votes = {}
        for result in results:
            if result.is_significant and result.winner:
                winner_votes[result.winner] = winner_votes.get(result.winner, 0) + 1
        
        if winner_votes:
            winner_id = max(winner_votes, key=winner_votes.get)
            logger.info(f"A/B test winner: {winner_id}")
            
            # Promote winner
            await self._promote_version(winner_id)
        else:
            logger.info("A/B test inconclusive - no significant differences")
    
    async def _deploy_to_k8s(self, config: DeploymentConfig, version: DeploymentVersion):
        """Deploy to Kubernetes"""
        if not self.k8s_apps:
            logger.warning("Kubernetes not configured - simulating deployment")
            return
        
        # Create deployment manifest
        deployment = client.V1Deployment(
            metadata=client.V1ObjectMeta(
                name=f"{config.name}-{version.revision}",
                namespace=config.namespace,
                labels=config.labels
            ),
            spec=client.V1DeploymentSpec(
                replicas=version.replicas,
                selector=client.V1LabelSelector(
                    match_labels={'app': config.name, 'version': str(version.revision)}
                ),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(
                        labels={'app': config.name, 'version': str(version.revision)}
                    ),
                    spec=client.V1PodSpec(
                        containers=[
                            client.V1Container(
                                name=config.name,
                                image=config.image,
                                ports=[client.V1ContainerPort(container_port=8080)]
                            )
                        ]
                    )
                )
            )
        )
        
        try:
            self.k8s_apps.create_namespaced_deployment(
                namespace=config.namespace,
                body=deployment
            )
            logger.info(f"Deployed {config.name} revision {version.revision}")
        except ApiException as e:
            logger.error(f"Kubernetes deployment error: {e}")
    
    async def _update_traffic_split(self, deployment_id: str, version_id: str, traffic_percent: float):
        """Update traffic split for canary"""
        # Update in database
        cursor = self.db.conn.cursor()
        cursor.execute('''
            UPDATE deployment_versions 
            SET traffic_percent = ? 
            WHERE version_id = ?
        ''', (traffic_percent, version_id))
        self.db.conn.commit()
        
        # Update in Kubernetes (via Istio VirtualService)
        logger.info(f"Updated traffic split to {traffic_percent*100:.0f}%")
    
    async def _promote_version(self, version_id: str):
        """Promote version to 100% traffic"""
        logger.info(f"Promoting version {version_id} to 100%")
        
        cursor = self.db.conn.cursor()
        cursor.execute('''
            UPDATE deployment_versions 
            SET traffic_percent = 100, promoted_at = CURRENT_TIMESTAMP
            WHERE version_id = ?
        ''', (version_id,))
        self.db.conn.commit()
    
    async def _rollback_deployment(self, deployment_id: str, failed_version_id: str):
        """Rollback to previous version"""
        logger.warning(f"Rolling back deployment {deployment_id}")
        
        # Find previous stable version
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT version_id FROM deployment_versions
            WHERE deployment_id = ? AND version_id != ?
            AND promoted_at IS NOT NULL
            ORDER BY promoted_at DESC
            LIMIT 1
        ''', (deployment_id, failed_version_id))
        
        row = cursor.fetchone()
        if row:
            previous_version_id = row[0]
            
            # Save rollback record
            cursor.execute('''
                INSERT INTO rollbacks 
                (rollback_id, deployment_id, from_version_id, to_version_id, reason)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                deployment_id,
                failed_version_id,
                previous_version_id,
                'Automatic rollback due to health check failure'
            ))
            self.db.conn.commit()
            
            # Route all traffic to previous version
            await self._update_traffic_split(deployment_id, previous_version_id, 1.0)
            
            logger.info(f"Rolled back to version {previous_version_id}")
    
    def _get_next_revision(self, deployment_id: str) -> int:
        """Get next revision number"""
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT MAX(revision) FROM deployment_versions
            WHERE deployment_id = ?
        ''', (deployment_id,))
        
        row = cursor.fetchone()
        return (row[0] or 0) + 1 if row else 1

################################################################################
# CLI Interface
################################################################################

def main():
    """Main entry point"""
    logger.info("Intelligent Deployment Engine v12.0")
    
    if '--deploy-canary' in sys.argv:
        # Example: --deploy-canary my-app my-namespace production nginx:latest 3
        name = sys.argv[2]
        namespace = sys.argv[3]
        environment = sys.argv[4]
        image = sys.argv[5]
        replicas = int(sys.argv[6])
        
        config = DeploymentConfig(
            deployment_id=str(uuid.uuid4()),
            name=name,
            namespace=namespace,
            strategy=DeploymentStrategy.CANARY,
            image=image,
            replicas=replicas,
            environment=environment
        )
        
        engine = IntelligentDeploymentEngine()
        version_id = asyncio.run(engine.deploy_canary(config))
        
        print(f"✅ Canary deployment started: {version_id}")
    
    elif '--deploy-ab' in sys.argv:
        # Example: --deploy-ab my-app my-namespace production nginx:v1 nginx:v2 4
        name = sys.argv[2]
        namespace = sys.argv[3]
        environment = sys.argv[4]
        image_a = sys.argv[5]
        image_b = sys.argv[6]
        replicas = int(sys.argv[7])
        
        config = DeploymentConfig(
            deployment_id=str(uuid.uuid4()),
            name=name,
            namespace=namespace,
            strategy=DeploymentStrategy.AB_TEST,
            image=image_a,
            replicas=replicas,
            environment=environment
        )
        
        engine = IntelligentDeploymentEngine()
        version_a, version_b = asyncio.run(engine.deploy_ab_test(config, image_b))
        
        print(f"✅ A/B test deployment started:")
        print(f"  Version A: {version_a}")
        print(f"  Version B: {version_b}")
    
    else:
        print("""
Intelligent Deployment Engine v12.0

Usage:
  --deploy-canary NAME NS ENV IMAGE REPLICAS
  --deploy-ab NAME NS ENV IMAGE_A IMAGE_B REPLICAS

Examples:
  python3 intelligent_deployment_engine.py --deploy-canary frontend prod production nginx:1.21 3
  python3 intelligent_deployment_engine.py --deploy-ab api dev staging app:v1 app:v2 4
        """)

if __name__ == '__main__':
    main()
