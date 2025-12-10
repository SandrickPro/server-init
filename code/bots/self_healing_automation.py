#!/usr/bin/env python3
"""
AI-POWERED SELF-HEALING AUTOMATION v11.0
Intelligent auto-remediation with machine learning
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple

import aiohttp
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IssueType(Enum):
    """Types of issues that can be detected"""
    HIGH_CPU = "high_cpu"
    HIGH_MEMORY = "high_memory"
    HIGH_DISK = "high_disk"
    SERVICE_DOWN = "service_down"
    NETWORK_ERROR = "network_error"
    DATABASE_SLOW = "database_slow"
    CACHE_MISS = "cache_miss"
    HIGH_LATENCY = "high_latency"
    ERROR_SPIKE = "error_spike"


class RemediationAction(Enum):
    """Available remediation actions"""
    RESTART_SERVICE = "restart_service"
    CLEAR_CACHE = "clear_cache"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    KILL_PROCESS = "kill_process"
    CLEANUP_DISK = "cleanup_disk"
    OPTIMIZE_QUERY = "optimize_query"
    ROTATE_LOGS = "rotate_logs"
    REBOOT = "reboot"
    ALERT_HUMAN = "alert_human"


@dataclass
class Issue:
    """Represents a detected issue"""
    issue_type: IssueType
    severity: str  # critical, warning, info
    value: float
    threshold: float
    timestamp: datetime
    metadata: Dict


@dataclass
class RemediationPlan:
    """Represents a remediation plan"""
    issue: Issue
    actions: List[RemediationAction]
    confidence: float
    estimated_duration: int  # seconds
    risk_level: str  # low, medium, high


class MetricsCollector:
    """Collects system and application metrics"""
    
    def __init__(self):
        self.prometheus_url = os.getenv('PROMETHEUS_URL', 'http://localhost:9090')
    
    async def get_cpu_usage(self) -> float:
        """Get current CPU usage"""
        result = subprocess.run(
            ["top", "-bn1"],
            capture_output=True,
            text=True
        )
        for line in result.stdout.split('\n'):
            if "Cpu(s)" in line:
                # Extract CPU usage
                idle = float(line.split()[7].replace('%id,', ''))
                return 100 - idle
        return 0.0
    
    async def get_memory_usage(self) -> float:
        """Get current memory usage percentage"""
        result = subprocess.run(
            ["free"],
            capture_output=True,
            text=True
        )
        lines = result.stdout.split('\n')
        for line in lines:
            if line.startswith('Mem:'):
                parts = line.split()
                total = float(parts[1])
                used = float(parts[2])
                return (used / total) * 100
        return 0.0
    
    async def get_disk_usage(self) -> float:
        """Get disk usage percentage"""
        result = subprocess.run(
            ["df", "-h", "/"],
            capture_output=True,
            text=True
        )
        lines = result.stdout.split('\n')
        if len(lines) > 1:
            parts = lines[1].split()
            usage = parts[4].replace('%', '')
            return float(usage)
        return 0.0
    
    async def get_service_status(self, service: str) -> bool:
        """Check if a service is running"""
        result = subprocess.run(
            ["systemctl", "is-active", service],
            capture_output=True,
            text=True
        )
        return result.stdout.strip() == "active"
    
    async def get_network_errors(self) -> int:
        """Get network error count"""
        result = subprocess.run(
            ["netstat", "-i"],
            capture_output=True,
            text=True
        )
        total_errors = 0
        for line in result.stdout.split('\n')[2:]:  # Skip headers
            if line.strip():
                parts = line.split()
                if len(parts) >= 5:
                    rx_errors = int(parts[3]) if parts[3].isdigit() else 0
                    tx_errors = int(parts[7]) if len(parts) > 7 and parts[7].isdigit() else 0
                    total_errors += rx_errors + tx_errors
        return total_errors
    
    async def get_database_latency(self) -> float:
        """Get database query latency (ms)"""
        start = time.time()
        try:
            result = subprocess.run(
                ["psql", "-U", "postgres", "-c", "SELECT 1;"],
                capture_output=True,
                timeout=5
            )
            latency = (time.time() - start) * 1000
            return latency if result.returncode == 0 else 999999
        except Exception:
            return 999999
    
    async def query_prometheus(self, query: str) -> Optional[float]:
        """Query Prometheus for metrics"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.prometheus_url}/api/v1/query"
                params = {'query': query}
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data['data']['result']:
                            return float(data['data']['result'][0]['value'][1])
        except Exception as e:
            logger.error(f"Prometheus query failed: {e}")
        return None


class IssueDetector:
    """Detects issues from metrics"""
    
    # Thresholds
    CPU_THRESHOLD = 80.0
    MEMORY_THRESHOLD = 85.0
    DISK_THRESHOLD = 90.0
    LATENCY_THRESHOLD = 1000.0  # ms
    ERROR_RATE_THRESHOLD = 10.0  # errors/sec
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.baseline_metrics = {}
        self.history = []
    
    async def detect_issues(self) -> List[Issue]:
        """Detect all current issues"""
        issues = []
        
        # CPU check
        cpu = await self.metrics.get_cpu_usage()
        if cpu > self.CPU_THRESHOLD:
            issues.append(Issue(
                issue_type=IssueType.HIGH_CPU,
                severity="critical" if cpu > 95 else "warning",
                value=cpu,
                threshold=self.CPU_THRESHOLD,
                timestamp=datetime.now(),
                metadata={"source": "system"}
            ))
        
        # Memory check
        memory = await self.metrics.get_memory_usage()
        if memory > self.MEMORY_THRESHOLD:
            issues.append(Issue(
                issue_type=IssueType.HIGH_MEMORY,
                severity="critical" if memory > 95 else "warning",
                value=memory,
                threshold=self.MEMORY_THRESHOLD,
                timestamp=datetime.now(),
                metadata={"source": "system"}
            ))
        
        # Disk check
        disk = await self.metrics.get_disk_usage()
        if disk > self.DISK_THRESHOLD:
            issues.append(Issue(
                issue_type=IssueType.HIGH_DISK,
                severity="critical" if disk > 95 else "warning",
                value=disk,
                threshold=self.DISK_THRESHOLD,
                timestamp=datetime.now(),
                metadata={"source": "system"}
            ))
        
        # Service checks
        for service in ['nginx', 'postgresql', 'redis']:
            if not await self.metrics.get_service_status(service):
                issues.append(Issue(
                    issue_type=IssueType.SERVICE_DOWN,
                    severity="critical",
                    value=0,
                    threshold=1,
                    timestamp=datetime.now(),
                    metadata={"service": service}
                ))
        
        # Database latency check
        db_latency = await self.metrics.get_database_latency()
        if db_latency > self.LATENCY_THRESHOLD:
            issues.append(Issue(
                issue_type=IssueType.DATABASE_SLOW,
                severity="warning",
                value=db_latency,
                threshold=self.LATENCY_THRESHOLD,
                timestamp=datetime.now(),
                metadata={"database": "postgresql"}
            ))
        
        # Network errors
        net_errors = await self.metrics.get_network_errors()
        if net_errors > 100:
            issues.append(Issue(
                issue_type=IssueType.NETWORK_ERROR,
                severity="warning",
                value=net_errors,
                threshold=100,
                timestamp=datetime.now(),
                metadata={"source": "network"}
            ))
        
        # Store history for trend analysis
        self.history.append({
            'timestamp': datetime.now(),
            'cpu': cpu,
            'memory': memory,
            'disk': disk,
            'latency': db_latency
        })
        
        # Keep only last 1000 entries
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
        
        return issues
    
    def detect_anomalies(self) -> List[Issue]:
        """Detect anomalies using statistical methods"""
        issues = []
        
        if len(self.history) < 100:
            return issues  # Not enough data
        
        # Extract recent metrics
        recent = self.history[-100:]
        cpu_values = [h['cpu'] for h in recent]
        mem_values = [h['memory'] for h in recent]
        
        # Calculate statistics
        cpu_mean = np.mean(cpu_values)
        cpu_std = np.std(cpu_values)
        mem_mean = np.mean(mem_values)
        mem_std = np.std(mem_values)
        
        # Current values
        current_cpu = cpu_values[-1]
        current_mem = mem_values[-1]
        
        # Detect anomalies (3-sigma rule)
        if current_cpu > cpu_mean + 3 * cpu_std:
            issues.append(Issue(
                issue_type=IssueType.HIGH_CPU,
                severity="warning",
                value=current_cpu,
                threshold=cpu_mean + 3 * cpu_std,
                timestamp=datetime.now(),
                metadata={"type": "anomaly", "mean": cpu_mean, "std": cpu_std}
            ))
        
        if current_mem > mem_mean + 3 * mem_std:
            issues.append(Issue(
                issue_type=IssueType.HIGH_MEMORY,
                severity="warning",
                value=current_mem,
                threshold=mem_mean + 3 * mem_std,
                timestamp=datetime.now(),
                metadata={"type": "anomaly", "mean": mem_mean, "std": mem_std}
            ))
        
        return issues


class AIRemediationEngine:
    """AI-powered remediation engine using machine learning"""
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.training_data = []
        self.action_success_rate = {}
        
        # Load pre-trained model if exists
        self.load_model()
    
    def load_model(self):
        """Load pre-trained model from disk"""
        try:
            import pickle
            with open('/var/lib/ai-remediation-model.pkl', 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.scaler = data['scaler']
                self.is_trained = True
                logger.info("Pre-trained model loaded successfully")
        except FileNotFoundError:
            logger.info("No pre-trained model found, will train on first data")
    
    def save_model(self):
        """Save trained model to disk"""
        try:
            import pickle
            with open('/var/lib/ai-remediation-model.pkl', 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'scaler': self.scaler
                }, f)
            logger.info("Model saved successfully")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def prepare_features(self, issue: Issue) -> np.ndarray:
        """Convert issue to feature vector"""
        features = [
            # Issue characteristics
            issue.value,
            issue.threshold,
            (issue.value - issue.threshold) / issue.threshold,  # Severity ratio
            1 if issue.severity == "critical" else 0.5 if issue.severity == "warning" else 0,
            
            # Issue type (one-hot encoding)
            1 if issue.issue_type == IssueType.HIGH_CPU else 0,
            1 if issue.issue_type == IssueType.HIGH_MEMORY else 0,
            1 if issue.issue_type == IssueType.HIGH_DISK else 0,
            1 if issue.issue_type == IssueType.SERVICE_DOWN else 0,
            1 if issue.issue_type == IssueType.DATABASE_SLOW else 0,
            
            # Temporal features
            issue.timestamp.hour,
            issue.timestamp.weekday(),
        ]
        
        return np.array(features).reshape(1, -1)
    
    async def recommend_actions(self, issue: Issue) -> RemediationPlan:
        """Recommend remediation actions using AI"""
        
        # Define action mappings
        action_rules = {
            IssueType.HIGH_CPU: [
                RemediationAction.SCALE_UP,
                RemediationAction.KILL_PROCESS,
                RemediationAction.OPTIMIZE_QUERY
            ],
            IssueType.HIGH_MEMORY: [
                RemediationAction.CLEAR_CACHE,
                RemediationAction.RESTART_SERVICE,
                RemediationAction.SCALE_UP
            ],
            IssueType.HIGH_DISK: [
                RemediationAction.CLEANUP_DISK,
                RemediationAction.ROTATE_LOGS,
                RemediationAction.ALERT_HUMAN
            ],
            IssueType.SERVICE_DOWN: [
                RemediationAction.RESTART_SERVICE,
                RemediationAction.ALERT_HUMAN
            ],
            IssueType.DATABASE_SLOW: [
                RemediationAction.OPTIMIZE_QUERY,
                RemediationAction.CLEAR_CACHE,
                RemediationAction.RESTART_SERVICE
            ]
        }
        
        # Get candidate actions
        candidate_actions = action_rules.get(issue.issue_type, [RemediationAction.ALERT_HUMAN])
        
        # Calculate confidence based on historical success rate
        confidence = 0.8  # Default
        if self.is_trained:
            features = self.prepare_features(issue)
            features_scaled = self.scaler.transform(features)
            probabilities = self.model.predict_proba(features_scaled)
            confidence = float(np.max(probabilities))
        
        # Estimate duration based on action type
        duration_map = {
            RemediationAction.RESTART_SERVICE: 30,
            RemediationAction.CLEAR_CACHE: 10,
            RemediationAction.SCALE_UP: 120,
            RemediationAction.CLEANUP_DISK: 60,
            RemediationAction.OPTIMIZE_QUERY: 5,
            RemediationAction.ROTATE_LOGS: 20,
        }
        
        estimated_duration = sum(duration_map.get(a, 30) for a in candidate_actions)
        
        # Determine risk level
        risk_level = "high" if issue.severity == "critical" else "medium" if issue.severity == "warning" else "low"
        
        return RemediationPlan(
            issue=issue,
            actions=candidate_actions,
            confidence=confidence,
            estimated_duration=estimated_duration,
            risk_level=risk_level
        )
    
    def record_outcome(self, issue: Issue, actions: List[RemediationAction], success: bool):
        """Record remediation outcome for learning"""
        features = self.prepare_features(issue)
        label = 1 if success else 0
        
        self.training_data.append((features, label))
        
        # Update success rates
        for action in actions:
            if action not in self.action_success_rate:
                self.action_success_rate[action] = {'success': 0, 'total': 0}
            
            self.action_success_rate[action]['total'] += 1
            if success:
                self.action_success_rate[action]['success'] += 1
        
        # Retrain model if enough data
        if len(self.training_data) >= 100 and len(self.training_data) % 50 == 0:
            self.train_model()
    
    def train_model(self):
        """Train the ML model with accumulated data"""
        if len(self.training_data) < 50:
            return
        
        X = np.vstack([x[0] for x in self.training_data])
        y = np.array([x[1] for x in self.training_data])
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        # Save model
        self.save_model()
        
        logger.info(f"Model trained with {len(self.training_data)} samples")


class RemediationExecutor:
    """Executes remediation actions"""
    
    def __init__(self):
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
        self.max_retries = 3
    
    async def execute(self, plan: RemediationPlan) -> Tuple[bool, str]:
        """Execute remediation plan"""
        logger.info(f"Executing remediation plan for {plan.issue.issue_type.value}")
        logger.info(f"Actions: {[a.value for a in plan.actions]}")
        logger.info(f"Confidence: {plan.confidence:.2%}")
        logger.info(f"Risk Level: {plan.risk_level}")
        
        if self.dry_run:
            logger.info("DRY RUN MODE - No actions will be executed")
            return True, "Dry run successful"
        
        # Ask for confirmation if high risk
        if plan.risk_level == "high":
            logger.warning("HIGH RISK operation - manual approval required")
            await self.send_approval_request(plan)
            return False, "Awaiting manual approval"
        
        # Execute actions sequentially
        for action in plan.actions:
            success, message = await self.execute_action(action, plan.issue)
            if not success:
                logger.error(f"Action {action.value} failed: {message}")
                return False, message
        
        return True, "All actions executed successfully"
    
    async def execute_action(self, action: RemediationAction, issue: Issue) -> Tuple[bool, str]:
        """Execute a single remediation action"""
        
        if action == RemediationAction.RESTART_SERVICE:
            service = issue.metadata.get('service', 'nginx')
            return await self.restart_service(service)
        
        elif action == RemediationAction.CLEAR_CACHE:
            return await self.clear_cache()
        
        elif action == RemediationAction.CLEANUP_DISK:
            return await self.cleanup_disk()
        
        elif action == RemediationAction.ROTATE_LOGS:
            return await self.rotate_logs()
        
        elif action == RemediationAction.SCALE_UP:
            return await self.scale_up()
        
        elif action == RemediationAction.KILL_PROCESS:
            return await self.kill_high_cpu_process()
        
        elif action == RemediationAction.ALERT_HUMAN:
            return await self.alert_human(issue)
        
        else:
            return False, f"Unknown action: {action}"
    
    async def restart_service(self, service: str) -> Tuple[bool, str]:
        """Restart a systemd service"""
        try:
            result = subprocess.run(
                ["systemctl", "restart", service],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                logger.info(f"Service {service} restarted successfully")
                return True, f"Service {service} restarted"
            else:
                return False, f"Failed to restart {service}: {result.stderr}"
        except Exception as e:
            return False, str(e)
    
    async def clear_cache(self) -> Tuple[bool, str]:
        """Clear system caches"""
        try:
            # Clear page cache, dentries and inodes
            subprocess.run(["sync"], check=True)
            with open('/proc/sys/vm/drop_caches', 'w') as f:
                f.write('3')
            
            # Clear Redis cache
            subprocess.run(["redis-cli", "FLUSHALL"], check=True)
            
            logger.info("Caches cleared successfully")
            return True, "Caches cleared"
        except Exception as e:
            return False, str(e)
    
    async def cleanup_disk(self) -> Tuple[bool, str]:
        """Clean up disk space"""
        try:
            # Remove old logs
            subprocess.run(
                ["find", "/var/log", "-name", "*.log", "-mtime", "+30", "-delete"],
                check=True
            )
            
            # Clean apt cache
            subprocess.run(["apt-get", "clean"], check=True)
            
            # Remove old Docker images
            subprocess.run(["docker", "system", "prune", "-af", "--volumes"], check=True)
            
            logger.info("Disk cleanup completed")
            return True, "Disk cleaned up"
        except Exception as e:
            return False, str(e)
    
    async def rotate_logs(self) -> Tuple[bool, str]:
        """Rotate log files"""
        try:
            subprocess.run(["logrotate", "-f", "/etc/logrotate.conf"], check=True)
            logger.info("Logs rotated successfully")
            return True, "Logs rotated"
        except Exception as e:
            return False, str(e)
    
    async def scale_up(self) -> Tuple[bool, str]:
        """Scale up resources (Kubernetes)"""
        try:
            # Increase replica count
            subprocess.run([
                "kubectl", "scale", "deployment", "app",
                "--replicas=5", "-n", "production"
            ], check=True)
            logger.info("Scaled up deployment")
            return True, "Scaled up to 5 replicas"
        except Exception as e:
            return False, str(e)
    
    async def kill_high_cpu_process(self) -> Tuple[bool, str]:
        """Kill process with highest CPU usage"""
        try:
            # Get highest CPU process
            result = subprocess.run(
                ["ps", "-eo", "pid,pcpu,comm", "--sort=-pcpu"],
                capture_output=True,
                text=True
            )
            lines = result.stdout.split('\n')[1:]  # Skip header
            if lines:
                pid = lines[0].split()[0]
                logger.warning(f"Killing high CPU process: PID {pid}")
                subprocess.run(["kill", "-9", pid], check=True)
                return True, f"Killed process {pid}"
            return False, "No high CPU process found"
        except Exception as e:
            return False, str(e)
    
    async def alert_human(self, issue: Issue) -> Tuple[bool, str]:
        """Send alert to human operator"""
        try:
            # Send Telegram notification
            message = f"""
🚨 Manual Intervention Required

Issue: {issue.issue_type.value}
Severity: {issue.severity}
Value: {issue.value:.2f}
Threshold: {issue.threshold:.2f}
Time: {issue.timestamp}

Please investigate and take appropriate action.
"""
            
            # Use existing Telegram bot
            subprocess.run([
                "/opt/telegram-bot/send-alert.sh",
                "Manual Intervention Required",
                message
            ])
            
            return True, "Alert sent to human operator"
        except Exception as e:
            return False, str(e)
    
    async def send_approval_request(self, plan: RemediationPlan):
        """Send approval request for high-risk operations"""
        message = f"""
⚠️ High Risk Operation Approval Required

Issue: {plan.issue.issue_type.value}
Severity: {plan.issue.severity}
Planned Actions:
{chr(10).join(f'  - {a.value}' for a in plan.actions)}

Confidence: {plan.confidence:.2%}
Estimated Duration: {plan.estimated_duration}s
Risk Level: {plan.risk_level}

Reply /approve or /reject
"""
        
        subprocess.run([
            "/opt/telegram-bot/send-alert.sh",
            "Approval Required",
            message
        ])


class SelfHealingOrchestrator:
    """Main orchestrator for self-healing automation"""
    
    def __init__(self):
        self.metrics = MetricsCollector()
        self.detector = IssueDetector(self.metrics)
        self.ai_engine = AIRemediationEngine()
        self.executor = RemediationExecutor()
        self.check_interval = 60  # seconds
        self.running = False
    
    async def start(self):
        """Start the self-healing loop"""
        self.running = True
        logger.info("🤖 Self-Healing Automation started")
        
        while self.running:
            try:
                await self.heal_cycle()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in heal cycle: {e}", exc_info=True)
                await asyncio.sleep(self.check_interval)
    
    async def heal_cycle(self):
        """Execute one healing cycle"""
        # Detect issues
        issues = await self.detector.detect_issues()
        
        if not issues:
            logger.debug("No issues detected")
            return
        
        logger.info(f"Detected {len(issues)} issues")
        
        # Process each issue
        for issue in issues:
            logger.info(f"Processing issue: {issue.issue_type.value} (severity: {issue.severity})")
            
            # Get remediation plan from AI
            plan = await self.ai_engine.recommend_actions(issue)
            
            # Execute remediation
            success, message = await self.executor.execute(plan)
            
            # Record outcome for learning
            self.ai_engine.record_outcome(issue, plan.actions, success)
            
            # Log result
            if success:
                logger.info(f"✅ Issue resolved: {message}")
            else:
                logger.warning(f"❌ Remediation failed: {message}")
    
    def stop(self):
        """Stop the self-healing loop"""
        self.running = False
        logger.info("Self-Healing Automation stopped")


# Main entry point
if __name__ == "__main__":
    orchestrator = SelfHealingOrchestrator()
    
    try:
        asyncio.run(orchestrator.start())
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
        orchestrator.stop()
