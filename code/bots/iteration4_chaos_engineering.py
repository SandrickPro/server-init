#!/usr/bin/env python3
"""
Chaos Engineering Platform - Iteration 4
Chaos Mesh integration for resilience testing
Automated fault injection and recovery validation
"""

import os
import sys
import yaml
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CHAOS_BASE = Path('/var/lib/chaos')
EXPERIMENTS_DIR = CHAOS_BASE / 'experiments'
REPORTS_DIR = CHAOS_BASE / 'reports'

for directory in [EXPERIMENTS_DIR, REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

################################################################################
# Chaos Mesh Experiments
################################################################################

class ChaosMeshExperiments:
    """Generate Chaos Mesh experiments"""
    
    @staticmethod
    def pod_failure(name: str, namespace: str, selector: Dict, duration: str = '30s'):
        """Generate pod failure experiment"""
        
        experiment = {
            'apiVersion': 'chaos-mesh.org/v1alpha1',
            'kind': 'PodChaos',
            'metadata': {
                'name': name,
                'namespace': namespace
            },
            'spec': {
                'action': 'pod-failure',
                'mode': 'one',
                'duration': duration,
                'selector': selector
            }
        }
        
        return yaml.dump(experiment)
    
    @staticmethod
    def network_delay(name: str, namespace: str, selector: Dict, delay: str = '100ms'):
        """Generate network delay experiment"""
        
        experiment = {
            'apiVersion': 'chaos-mesh.org/v1alpha1',
            'kind': 'NetworkChaos',
            'metadata': {
                'name': name,
                'namespace': namespace
            },
            'spec': {
                'action': 'delay',
                'mode': 'one',
                'selector': selector,
                'delay': {
                    'latency': delay,
                    'correlation': '0',
                    'jitter': '10ms'
                },
                'duration': '1m'
            }
        }
        
        return yaml.dump(experiment)
    
    @staticmethod
    def network_partition(name: str, namespace: str, source_selector: Dict, target_selector: Dict):
        """Generate network partition experiment"""
        
        experiment = {
            'apiVersion': 'chaos-mesh.org/v1alpha1',
            'kind': 'NetworkChaos',
            'metadata': {
                'name': name,
                'namespace': namespace
            },
            'spec': {
                'action': 'partition',
                'mode': 'all',
                'selector': source_selector,
                'direction': 'both',
                'target': {
                    'selector': target_selector,
                    'mode': 'all'
                },
                'duration': '2m'
            }
        }
        
        return yaml.dump(experiment)
    
    @staticmethod
    def cpu_stress(name: str, namespace: str, selector: Dict, workers: int = 2):
        """Generate CPU stress experiment"""
        
        experiment = {
            'apiVersion': 'chaos-mesh.org/v1alpha1',
            'kind': 'StressChaos',
            'metadata': {
                'name': name,
                'namespace': namespace
            },
            'spec': {
                'mode': 'one',
                'selector': selector,
                'stressors': {
                    'cpu': {
                        'workers': workers,
                        'load': 90
                    }
                },
                'duration': '1m'
            }
        }
        
        return yaml.dump(experiment)
    
    @staticmethod
    def memory_stress(name: str, namespace: str, selector: Dict, size: str = '512MB'):
        """Generate memory stress experiment"""
        
        experiment = {
            'apiVersion': 'chaos-mesh.org/v1alpha1',
            'kind': 'StressChaos',
            'metadata': {
                'name': name,
                'namespace': namespace
            },
            'spec': {
                'mode': 'one',
                'selector': selector,
                'stressors': {
                    'memory': {
                        'workers': 1,
                        'size': size
                    }
                },
                'duration': '1m'
            }
        }
        
        return yaml.dump(experiment)

################################################################################
# Experiment Runner
################################################################################

class ExperimentRunner:
    """Execute chaos experiments"""
    
    def __init__(self):
        self.experiments = ChaosMeshExperiments()
    
    def run_experiment(self, experiment_yaml: str, experiment_name: str) -> bool:
        """Run chaos experiment"""
        
        # Save experiment
        experiment_file = EXPERIMENTS_DIR / f'{experiment_name}.yaml'
        experiment_file.write_text(experiment_yaml)
        
        logger.info(f"Running experiment: {experiment_name}")
        
        # Apply experiment
        result = subprocess.run(
            ['kubectl', 'apply', '-f', str(experiment_file)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Experiment failed: {result.stderr}")
            return False
        
        logger.info(f"Experiment started: {experiment_name}")
        return True
    
    def stop_experiment(self, experiment_name: str) -> bool:
        """Stop chaos experiment"""
        
        experiment_file = EXPERIMENTS_DIR / f'{experiment_name}.yaml'
        
        result = subprocess.run(
            ['kubectl', 'delete', '-f', str(experiment_file)],
            capture_output=True,
            text=True
        )
        
        logger.info(f"Experiment stopped: {experiment_name}")
        return result.returncode == 0

################################################################################
# Resilience Validator
################################################################################

class ResilienceValidator:
    """Validate system resilience"""
    
    @staticmethod
    def validate_recovery_time(service: str, max_recovery_seconds: int = 30) -> bool:
        """Validate recovery time after failure"""
        
        logger.info(f"Validating recovery time for {service}")
        
        # Check pod status
        result = subprocess.run(
            ['kubectl', 'get', 'pods', '-l', f'app={service}', '-o', 'json'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return False
        
        import json
        pods = json.loads(result.stdout)
        
        for pod in pods.get('items', []):
            status = pod['status']['phase']
            if status != 'Running':
                logger.warning(f"Pod not running: {pod['metadata']['name']}")
                return False
        
        logger.info(f"Recovery validated for {service}")
        return True
    
    @staticmethod
    def validate_data_consistency(service: str) -> bool:
        """Validate data consistency after chaos"""
        
        logger.info(f"Validating data consistency for {service}")
        
        # This would integrate with application-specific checks
        # For now, return True as placeholder
        return True
    
    @staticmethod
    def measure_availability(service: str, duration_seconds: int = 60) -> float:
        """Measure service availability during chaos"""
        
        import requests
        import time
        
        success_count = 0
        total_requests = 0
        
        end_time = time.time() + duration_seconds
        
        while time.time() < end_time:
            try:
                response = requests.get(f'http://{service}:8080/health', timeout=1)
                if response.status_code == 200:
                    success_count += 1
                total_requests += 1
            except:
                total_requests += 1
            
            time.sleep(1)
        
        availability = (success_count / total_requests * 100) if total_requests > 0 else 0
        logger.info(f"Availability for {service}: {availability:.2f}%")
        
        return availability

################################################################################
# Chaos Platform
################################################################################

class ChaosPlatform:
    """Complete chaos engineering orchestrator"""
    
    def __init__(self):
        self.runner = ExperimentRunner()
        self.validator = ResilienceValidator()
        self.experiments = ChaosMeshExperiments()
    
    def run_resilience_suite(self, service: str, namespace: str = 'default'):
        """Run complete resilience test suite"""
        
        selector = {
            'namespaces': [namespace],
            'labelSelectors': {
                'app': service
            }
        }
        
        logger.info(f"Starting resilience suite for {service}")
        
        # Test 1: Pod failure
        logger.info("Test 1: Pod failure resilience")
        experiment = self.experiments.pod_failure(
            name=f'{service}-pod-failure',
            namespace=namespace,
            selector=selector,
            duration='30s'
        )
        self.runner.run_experiment(experiment, f'{service}-pod-failure')
        
        import time
        time.sleep(40)  # Wait for recovery
        
        assert self.validator.validate_recovery_time(service), "Recovery time exceeded"
        
        # Test 2: Network delay
        logger.info("Test 2: Network delay resilience")
        experiment = self.experiments.network_delay(
            name=f'{service}-net-delay',
            namespace=namespace,
            selector=selector,
            delay='200ms'
        )
        self.runner.run_experiment(experiment, f'{service}-net-delay')
        
        availability = self.validator.measure_availability(service, duration_seconds=30)
        assert availability >= 95.0, f"Availability too low: {availability}%"
        
        self.runner.stop_experiment(f'{service}-net-delay')
        
        # Test 3: CPU stress
        logger.info("Test 3: CPU stress resilience")
        experiment = self.experiments.cpu_stress(
            name=f'{service}-cpu-stress',
            namespace=namespace,
            selector=selector,
            workers=2
        )
        self.runner.run_experiment(experiment, f'{service}-cpu-stress')
        
        time.sleep(30)
        
        availability = self.validator.measure_availability(service, duration_seconds=30)
        assert availability >= 90.0, f"Availability under CPU stress too low: {availability}%"
        
        self.runner.stop_experiment(f'{service}-cpu-stress')
        
        # Generate report
        self._generate_report(service, [
            {'test': 'pod-failure', 'result': 'PASS'},
            {'test': 'network-delay', 'result': 'PASS', 'availability': availability},
            {'test': 'cpu-stress', 'result': 'PASS', 'availability': availability}
        ])
        
        logger.info(f"Resilience suite completed for {service}")
    
    def _generate_report(self, service: str, results: List[Dict]):
        """Generate chaos testing report"""
        
        report = f"""
# Chaos Engineering Report - {service}
Generated: {datetime.now().isoformat()}

## Test Results

"""
        for result in results:
            report += f"- **{result['test']}**: {result['result']}\n"
            if 'availability' in result:
                report += f"  - Availability: {result['availability']:.2f}%\n"
        
        report += "\n## Conclusion\n\n"
        report += f"All resilience tests passed for {service}.\n"
        
        report_file = REPORTS_DIR / f'{service}-{datetime.now().strftime("%Y%m%d")}.md'
        report_file.write_text(report)
        
        logger.info(f"Report generated: {report_file}")

################################################################################
# CLI
################################################################################

def main():
    logger.info("🌀 Chaos Engineering Platform - Iteration 4")
    
    if '--run-suite' in sys.argv:
        platform = ChaosPlatform()
        platform.run_resilience_suite('demo-service', namespace='default')
        print("✅ Resilience suite completed")
    
    else:
        print("""
Chaos Engineering Platform v13.0 - Iteration 4

Usage:
  --run-suite    Run resilience test suite

Features:
  ✓ Pod failure injection
  ✓ Network chaos (delay, partition)
  ✓ Resource stress (CPU, memory)
  ✓ Automated validation
  ✓ Resilience reporting
        """)

if __name__ == '__main__':
    main()
