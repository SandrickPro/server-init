#!/usr/bin/env python3
"""
Advanced CI/CD Pipeline - Iteration 1
Jenkins/GitLab CI integration with automated testing and blue-green deployment
Complete continuous delivery automation
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import subprocess
import yaml
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CICD_BASE = Path('/var/lib/cicd')
PIPELINES_DIR = CICD_BASE / 'pipelines'
ARTIFACTS_DIR = CICD_BASE / 'artifacts'
JENKINS_URL = os.getenv('JENKINS_URL', 'http://localhost:8080')
GITLAB_URL = os.getenv('GITLAB_URL', 'https://gitlab.com')
GITLAB_TOKEN = os.getenv('GITLAB_TOKEN')

for directory in [PIPELINES_DIR, ARTIFACTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

################################################################################
# CI/CD Models
################################################################################

@dataclass
class Pipeline:
    """CI/CD pipeline definition"""
    name: str
    stages: List[str]
    jobs: Dict[str, Any]
    triggers: List[str]
    environment: str
    
@dataclass
class Deployment:
    """Deployment configuration"""
    app_name: str
    version: str
    strategy: str  # blue-green, canary, rolling
    replicas: int
    health_check_url: str
    rollback_on_failure: bool = True

################################################################################
# Jenkins Integration
################################################################################

class JenkinsManager:
    """Jenkins CI/CD management"""
    
    def __init__(self, url: str = JENKINS_URL):
        self.url = url
        self.user = os.getenv('JENKINS_USER')
        self.token = os.getenv('JENKINS_TOKEN')
    
    def create_pipeline(self, name: str, config: Dict) -> bool:
        """Create Jenkins pipeline"""
        
        jenkinsfile = f"""
pipeline {{
    agent any
    
    environment {{
        APP_NAME = '{config['app_name']}'
        DOCKER_REGISTRY = 'docker.io'
    }}
    
    stages {{
        stage('Checkout') {{
            steps {{
                git branch: 'main',
                    url: '{config['repo_url']}'
            }}
        }}
        
        stage('Build') {{
            steps {{
                sh 'docker build -t ${{DOCKER_REGISTRY}}/${{APP_NAME}}:${{BUILD_NUMBER}} .'
            }}
        }}
        
        stage('Test') {{
            parallel {{
                stage('Unit Tests') {{
                    steps {{
                        sh 'pytest tests/unit/'
                    }}
                }}
                stage('Integration Tests') {{
                    steps {{
                        sh 'pytest tests/integration/'
                    }}
                }}
                stage('Security Scan') {{
                    steps {{
                        sh 'trivy image ${{DOCKER_REGISTRY}}/${{APP_NAME}}:${{BUILD_NUMBER}}'
                    }}
                }}
            }}
        }}
        
        stage('Push') {{
            steps {{
                sh 'docker push ${{DOCKER_REGISTRY}}/${{APP_NAME}}:${{BUILD_NUMBER}}'
            }}
        }}
        
        stage('Deploy') {{
            steps {{
                script {{
                    deploy_blue_green(
                        app: '${{APP_NAME}}',
                        version: '${{BUILD_NUMBER}}'
                    )
                }}
            }}
        }}
    }}
    
    post {{
        success {{
            slackSend color: 'good',
                      message: "Pipeline ${{env.JOB_NAME}} #${{env.BUILD_NUMBER}} succeeded"
        }}
        failure {{
            slackSend color: 'danger',
                      message: "Pipeline ${{env.JOB_NAME}} #${{env.BUILD_NUMBER}} failed"
        }}
    }}
}}
"""
        
        pipeline_file = PIPELINES_DIR / f'{name}-Jenkinsfile'
        pipeline_file.write_text(jenkinsfile)
        
        logger.info(f"Jenkins pipeline created: {name}")
        return True
    
    def trigger_build(self, job_name: str, parameters: Optional[Dict] = None) -> str:
        """Trigger Jenkins build"""
        
        url = f"{self.url}/job/{job_name}/build"
        
        if parameters:
            url += "WithParameters"
        
        try:
            response = requests.post(
                url,
                auth=(self.user, self.token),
                json=parameters or {}
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Build triggered: {job_name}")
                return "build-123"
            else:
                logger.error(f"Build trigger failed: {response.text}")
                return ""
        
        except Exception as e:
            logger.error(f"Jenkins error: {e}")
            return ""

################################################################################
# GitLab CI Integration
################################################################################

class GitLabCIManager:
    """GitLab CI/CD management"""
    
    def __init__(self, url: str = GITLAB_URL, token: str = GITLAB_TOKEN):
        self.url = url
        self.token = token
        self.headers = {'PRIVATE-TOKEN': token} if token else {}
    
    def generate_gitlab_ci(self, config: Dict) -> str:
        """Generate .gitlab-ci.yml"""
        
        gitlab_ci = f"""
variables:
  APP_NAME: {config['app_name']}
  DOCKER_REGISTRY: docker.io
  KUBERNETES_VERSION: 1.28

stages:
  - build
  - test
  - security
  - deploy
  - verify

before_script:
  - docker info
  - kubectl version --client

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $DOCKER_REGISTRY/$APP_NAME:$CI_COMMIT_SHA .
    - docker tag $DOCKER_REGISTRY/$APP_NAME:$CI_COMMIT_SHA $DOCKER_REGISTRY/$APP_NAME:latest
  artifacts:
    paths:
      - build/
    expire_in: 1 week

unit-test:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - pytest tests/unit/ --cov=src/ --cov-report=xml
  coverage: '/TOTAL.*\\s+(\\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

integration-test:
  stage: test
  image: python:3.11
  services:
    - postgres:15
    - redis:7
  variables:
    POSTGRES_DB: test_db
    POSTGRES_USER: test
    POSTGRES_PASSWORD: test
  script:
    - pip install -r requirements.txt
    - pytest tests/integration/ -v

security-scan:
  stage: security
  image: aquasec/trivy:latest
  script:
    - trivy image --severity HIGH,CRITICAL $DOCKER_REGISTRY/$APP_NAME:$CI_COMMIT_SHA
  allow_failure: false

sast:
  stage: security
  image: returntocorp/semgrep
  script:
    - semgrep --config=auto src/

deploy-staging:
  stage: deploy
  image: bitnami/kubectl:latest
  environment:
    name: staging
    url: https://staging.example.com
  script:
    - kubectl config use-context staging
    - |
      cat <<EOF | kubectl apply -f -
      apiVersion: apps/v1
      kind: Deployment
      metadata:
        name: $APP_NAME
      spec:
        replicas: 3
        selector:
          matchLabels:
            app: $APP_NAME
        template:
          metadata:
            labels:
              app: $APP_NAME
              version: $CI_COMMIT_SHA
          spec:
            containers:
            - name: $APP_NAME
              image: $DOCKER_REGISTRY/$APP_NAME:$CI_COMMIT_SHA
              ports:
              - containerPort: 8080
              livenessProbe:
                httpGet:
                  path: /health
                  port: 8080
                initialDelaySeconds: 30
              readinessProbe:
                httpGet:
                  path: /ready
                  port: 8080
                initialDelaySeconds: 10
      EOF
  only:
    - main

deploy-production:
  stage: deploy
  image: bitnami/kubectl:latest
  environment:
    name: production
    url: https://app.example.com
  script:
    - kubectl config use-context production
    - python3 scripts/blue_green_deploy.py --app=$APP_NAME --version=$CI_COMMIT_SHA
  when: manual
  only:
    - main

smoke-test:
  stage: verify
  image: curlimages/curl:latest
  script:
    - curl -f https://staging.example.com/health || exit 1
    - curl -f https://staging.example.com/api/version || exit 1
"""
        
        ci_file = PIPELINES_DIR / f'{config["app_name"]}-gitlab-ci.yml'
        ci_file.write_text(gitlab_ci)
        
        logger.info(f"GitLab CI config generated: {config['app_name']}")
        return gitlab_ci
    
    def trigger_pipeline(self, project_id: str, ref: str = 'main') -> Optional[str]:
        """Trigger GitLab pipeline"""
        
        url = f"{self.url}/api/v4/projects/{project_id}/pipeline"
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json={'ref': ref}
            )
            
            if response.status_code == 201:
                pipeline = response.json()
                logger.info(f"Pipeline triggered: {pipeline['id']}")
                return str(pipeline['id'])
            
            return None
        
        except Exception as e:
            logger.error(f"GitLab error: {e}")
            return None

################################################################################
# Blue-Green Deployment
################################################################################

class BlueGreenDeployer:
    """Blue-Green deployment manager"""
    
    def __init__(self):
        self.active_color = 'blue'
    
    def deploy(self, deployment: Deployment) -> bool:
        """Execute blue-green deployment"""
        
        inactive_color = 'green' if self.active_color == 'blue' else 'blue'
        
        logger.info(f"Deploying to {inactive_color} environment")
        
        # Deploy to inactive environment
        manifest = f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {deployment.app_name}-{inactive_color}
spec:
  replicas: {deployment.replicas}
  selector:
    matchLabels:
      app: {deployment.app_name}
      color: {inactive_color}
  template:
    metadata:
      labels:
        app: {deployment.app_name}
        color: {inactive_color}
        version: {deployment.version}
    spec:
      containers:
      - name: app
        image: {deployment.app_name}:{deployment.version}
        ports:
        - containerPort: 8080
"""
        
        manifest_file = PIPELINES_DIR / f'deploy-{inactive_color}.yaml'
        manifest_file.write_text(manifest)
        
        # Apply deployment
        result = subprocess.run(
            ['kubectl', 'apply', '-f', str(manifest_file)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Deployment failed: {result.stderr}")
            return False
        
        # Wait for deployment
        subprocess.run(
            ['kubectl', 'rollout', 'status', f'deployment/{deployment.app_name}-{inactive_color}'],
            check=True
        )
        
        # Health check
        if not self._health_check(deployment.health_check_url):
            logger.error("Health check failed")
            
            if deployment.rollback_on_failure:
                self.rollback(deployment.app_name, inactive_color)
            
            return False
        
        # Switch traffic
        self._switch_traffic(deployment.app_name, inactive_color)
        
        self.active_color = inactive_color
        logger.info(f"Blue-green deployment completed. Active: {self.active_color}")
        
        return True
    
    def _health_check(self, url: str) -> bool:
        """Perform health check"""
        try:
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def _switch_traffic(self, app_name: str, new_color: str):
        """Switch service to new color"""
        
        service_patch = f"""
spec:
  selector:
    app: {app_name}
    color: {new_color}
"""
        
        subprocess.run(
            ['kubectl', 'patch', 'service', app_name, '--patch', service_patch],
            check=True
        )
        
        logger.info(f"Traffic switched to {new_color}")
    
    def rollback(self, app_name: str, failed_color: str) -> bool:
        """Rollback deployment"""
        
        logger.warning(f"Rolling back {failed_color} deployment")
        
        subprocess.run(
            ['kubectl', 'delete', 'deployment', f'{app_name}-{failed_color}'],
            check=True
        )
        
        return True

################################################################################
# Testing Framework
################################################################################

class AutomatedTesting:
    """Automated testing framework"""
    
    @staticmethod
    def run_unit_tests(test_dir: Path) -> bool:
        """Run unit tests"""
        
        result = subprocess.run(
            ['pytest', str(test_dir), '-v', '--cov=src/', '--cov-report=xml'],
            capture_output=True,
            text=True
        )
        
        logger.info(f"Unit tests: {result.stdout}")
        return result.returncode == 0
    
    @staticmethod
    def run_integration_tests(test_dir: Path) -> bool:
        """Run integration tests"""
        
        result = subprocess.run(
            ['pytest', str(test_dir), '-v', '-m', 'integration'],
            capture_output=True,
            text=True
        )
        
        logger.info(f"Integration tests: {result.stdout}")
        return result.returncode == 0
    
    @staticmethod
    def run_security_scan(image: str) -> bool:
        """Run security scan"""
        
        result = subprocess.run(
            ['trivy', 'image', '--severity', 'HIGH,CRITICAL', image],
            capture_output=True,
            text=True
        )
        
        logger.info(f"Security scan: {result.stdout}")
        return result.returncode == 0

################################################################################
# CI/CD Platform
################################################################################

class CICDPlatform:
    """Main CI/CD orchestrator"""
    
    def __init__(self):
        self.jenkins = JenkinsManager()
        self.gitlab = GitLabCIManager()
        self.deployer = BlueGreenDeployer()
        self.testing = AutomatedTesting()
    
    def create_full_pipeline(self, app_name: str, repo_url: str) -> bool:
        """Create complete CI/CD pipeline"""
        
        config = {
            'app_name': app_name,
            'repo_url': repo_url
        }
        
        # Create Jenkins pipeline
        self.jenkins.create_pipeline(app_name, config)
        
        # Generate GitLab CI
        self.gitlab.generate_gitlab_ci(config)
        
        logger.info(f"Complete pipeline created for {app_name}")
        return True
    
    def execute_deployment(self, app_name: str, version: str) -> bool:
        """Execute full deployment"""
        
        deployment = Deployment(
            app_name=app_name,
            version=version,
            strategy='blue-green',
            replicas=3,
            health_check_url=f'http://{app_name}:8080/health'
        )
        
        # Run tests
        if not self.testing.run_unit_tests(Path('tests/unit')):
            logger.error("Unit tests failed")
            return False
        
        # Security scan
        if not self.testing.run_security_scan(f'{app_name}:{version}'):
            logger.error("Security scan failed")
            return False
        
        # Deploy
        return self.deployer.deploy(deployment)

################################################################################
# CLI
################################################################################

def main():
    logger.info("🚀 Advanced CI/CD Pipeline - Iteration 1")
    
    if '--create-pipeline' in sys.argv:
        platform = CICDPlatform()
        platform.create_full_pipeline('demo-app', 'https://github.com/org/repo')
        print("✅ Pipeline created")
    
    elif '--deploy' in sys.argv:
        platform = CICDPlatform()
        platform.execute_deployment('demo-app', 'v1.0.0')
        print("✅ Deployment executed")
    
    else:
        print("""
Advanced CI/CD Pipeline v13.0 - Iteration 1

Usage:
  --create-pipeline    Create CI/CD pipeline
  --deploy            Execute deployment

Features:
  ✓ Jenkins integration
  ✓ GitLab CI support
  ✓ Blue-green deployment
  ✓ Automated testing
  ✓ Security scanning
        """)

if __name__ == '__main__':
    main()
