#!/usr/bin/env python3
"""
Developer Experience Platform - Iteration 9
Internal developer portal, self-service infrastructure, API catalog
Complete developer productivity platform
"""

import os
import sys
import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from flask import Flask, request, jsonify
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEV_PORTAL_BASE = Path('/var/lib/developer-portal')
CATALOGS_DIR = DEV_PORTAL_BASE / 'catalogs'
TEMPLATES_DIR = DEV_PORTAL_BASE / 'templates'
DOCS_DIR = DEV_PORTAL_BASE / 'docs'

for directory in [CATALOGS_DIR, TEMPLATES_DIR, DOCS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)

################################################################################
# Service Catalog
################################################################################

class ServiceCatalog:
    """API and service catalog"""
    
    def __init__(self):
        self.catalog_file = CATALOGS_DIR / 'services.json'
        self.services = self._load_catalog()
    
    def _load_catalog(self) -> Dict:
        """Load service catalog"""
        if self.catalog_file.exists():
            return json.loads(self.catalog_file.read_text())
        return {}
    
    def _save_catalog(self):
        """Save service catalog"""
        self.catalog_file.write_text(json.dumps(self.services, indent=2))
    
    def register_service(self, name: str, metadata: Dict):
        """Register service in catalog"""
        
        self.services[name] = {
            'name': name,
            'version': metadata.get('version', '1.0.0'),
            'description': metadata.get('description', ''),
            'endpoints': metadata.get('endpoints', []),
            'documentation': metadata.get('documentation', ''),
            'team': metadata.get('team', ''),
            'status': 'active',
            'registered_at': datetime.now().isoformat()
        }
        
        self._save_catalog()
        logger.info(f"Service registered: {name}")
    
    def get_service(self, name: str) -> Optional[Dict]:
        """Get service details"""
        return self.services.get(name)
    
    def list_services(self) -> List[Dict]:
        """List all services"""
        return list(self.services.values())
    
    def generate_openapi_spec(self, service_name: str) -> Dict:
        """Generate OpenAPI specification"""
        
        service = self.get_service(service_name)
        
        if not service:
            return {}
        
        spec = {
            'openapi': '3.0.0',
            'info': {
                'title': service['name'],
                'version': service['version'],
                'description': service['description']
            },
            'servers': [{
                'url': f'https://api.example.com/{service_name}',
                'description': 'Production server'
            }],
            'paths': {}
        }
        
        for endpoint in service.get('endpoints', []):
            spec['paths'][endpoint['path']] = {
                endpoint['method'].lower(): {
                    'summary': endpoint.get('summary', ''),
                    'responses': {
                        '200': {
                            'description': 'Successful response'
                        }
                    }
                }
            }
        
        return spec

################################################################################
# Self-Service Infrastructure
################################################################################

class SelfServiceInfrastructure:
    """Self-service infrastructure provisioning"""
    
    @staticmethod
    def create_project_template(template_type: str) -> str:
        """Create project template"""
        
        templates = {
            'python-microservice': {
                'files': {
                    'Dockerfile': """
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
""",
                    'requirements.txt': """
flask==3.0.0
gunicorn==21.2.0
prometheus-client==0.19.0
""",
                    'app.py': """
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
""",
                    'k8s/deployment.yaml': """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-service
  template:
    metadata:
      labels:
        app: my-service
    spec:
      containers:
      - name: app
        image: my-service:latest
        ports:
        - containerPort: 8080
"""
                }
            },
            'nodejs-api': {
                'files': {
                    'package.json': json.dumps({
                        'name': 'my-api',
                        'version': '1.0.0',
                        'main': 'index.js',
                        'dependencies': {
                            'express': '^4.18.0',
                            'prom-client': '^15.0.0'
                        }
                    }, indent=2),
                    'index.js': """
const express = require('express');
const app = express();

app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

app.listen(8080, () => {
  console.log('Server running on port 8080');
});
""",
                    'Dockerfile': """
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
CMD ["node", "index.js"]
"""
                }
            }
        }
        
        template = templates.get(template_type, {})
        
        # Save template files
        template_dir = TEMPLATES_DIR / template_type
        template_dir.mkdir(exist_ok=True)
        
        for file_path, content in template.get('files', {}).items():
            file = template_dir / file_path
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(content)
        
        logger.info(f"Template created: {template_type}")
        return str(template_dir)
    
    @staticmethod
    def provision_namespace(namespace: str, team: str, quotas: Dict) -> bool:
        """Provision Kubernetes namespace with quotas"""
        
        namespace_config = {
            'apiVersion': 'v1',
            'kind': 'Namespace',
            'metadata': {
                'name': namespace,
                'labels': {
                    'team': team
                }
            }
        }
        
        quota_config = {
            'apiVersion': 'v1',
            'kind': 'ResourceQuota',
            'metadata': {
                'name': f'{namespace}-quota',
                'namespace': namespace
            },
            'spec': {
                'hard': quotas
            }
        }
        
        # Apply namespace
        namespace_file = TEMPLATES_DIR / f'{namespace}-ns.yaml'
        namespace_file.write_text(yaml.dump(namespace_config))
        
        result = subprocess.run(
            ['kubectl', 'apply', '-f', str(namespace_file)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Failed to create namespace: {result.stderr}")
            return False
        
        # Apply quota
        quota_file = TEMPLATES_DIR / f'{namespace}-quota.yaml'
        quota_file.write_text(yaml.dump(quota_config))
        
        result = subprocess.run(
            ['kubectl', 'apply', '-f', str(quota_file)],
            capture_output=True,
            text=True
        )
        
        logger.info(f"Namespace provisioned: {namespace}")
        return result.returncode == 0
    
    @staticmethod
    def create_ci_pipeline(project_name: str, repo_url: str) -> str:
        """Create CI/CD pipeline for project"""
        
        pipeline = f"""
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: docker build -t {project_name}:${{{{ github.sha }}}} .
    
    - name: Run tests
      run: docker run {project_name}:${{{{ github.sha }}}} pytest
    
    - name: Push to registry
      run: |
        echo "${{{{ secrets.DOCKER_PASSWORD }}}}" | docker login -u "${{{{ secrets.DOCKER_USERNAME }}}}" --password-stdin
        docker push {project_name}:${{{{ github.sha }}}}
    
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/{project_name} {project_name}={project_name}:${{{{ github.sha }}}}
"""
        
        pipeline_file = TEMPLATES_DIR / f'{project_name}-pipeline.yml'
        pipeline_file.write_text(pipeline)
        
        logger.info(f"CI/CD pipeline created: {project_name}")
        return str(pipeline_file)

################################################################################
# Documentation Generator
################################################################################

class DocumentationGenerator:
    """Automated documentation generation"""
    
    @staticmethod
    def generate_api_docs(service_name: str, endpoints: List[Dict]) -> str:
        """Generate API documentation"""
        
        docs = f"# {service_name} API Documentation\n\n"
        docs += f"Generated: {datetime.now().isoformat()}\n\n"
        
        for endpoint in endpoints:
            docs += f"## {endpoint['method']} {endpoint['path']}\n\n"
            docs += f"{endpoint.get('description', '')}\n\n"
            
            if 'parameters' in endpoint:
                docs += "### Parameters\n\n"
                for param in endpoint['parameters']:
                    docs += f"- **{param['name']}** ({param['type']}): {param['description']}\n"
                docs += "\n"
            
            docs += "### Example Request\n\n"
            docs += f"```bash\ncurl -X {endpoint['method']} https://api.example.com{endpoint['path']}\n```\n\n"
        
        doc_file = DOCS_DIR / f'{service_name}-api.md'
        doc_file.write_text(docs)
        
        logger.info(f"API documentation generated: {service_name}")
        return docs
    
    @staticmethod
    def generate_runbook(service_name: str) -> str:
        """Generate operational runbook"""
        
        runbook = f"""# {service_name} Operational Runbook

## Service Overview
- **Name**: {service_name}
- **Owner**: [Team Name]
- **On-call**: [Rotation Link]

## Architecture
[Architecture diagram]

## Deployment
```bash
kubectl apply -f k8s/
```

## Monitoring
- **Dashboard**: https://grafana.example.com/d/{service_name}
- **Alerts**: https://alertmanager.example.com

## Common Issues

### High Latency
**Symptoms**: P95 latency > 1s

**Resolution**:
1. Check resource usage
2. Review slow queries
3. Scale replicas

### Pod Crashes
**Symptoms**: CrashLoopBackOff

**Resolution**:
1. Check logs: `kubectl logs {service_name}-xxx`
2. Verify configuration
3. Check dependencies

## Emergency Contacts
- **Team Lead**: [Name]
- **Platform**: [Email]
"""
        
        runbook_file = DOCS_DIR / f'{service_name}-runbook.md'
        runbook_file.write_text(runbook)
        
        logger.info(f"Runbook generated: {service_name}")
        return runbook

################################################################################
# Developer Portal API
################################################################################

@app.route('/api/services', methods=['GET'])
def list_services():
    """List all services"""
    catalog = ServiceCatalog()
    return jsonify(catalog.list_services())

@app.route('/api/services/<service_name>', methods=['GET'])
def get_service(service_name):
    """Get service details"""
    catalog = ServiceCatalog()
    service = catalog.get_service(service_name)
    
    if service:
        return jsonify(service)
    return jsonify({'error': 'Service not found'}), 404

@app.route('/api/templates/<template_type>', methods=['POST'])
def create_template(template_type):
    """Create project from template"""
    infra = SelfServiceInfrastructure()
    template_path = infra.create_project_template(template_type)
    return jsonify({'template_path': template_path})

@app.route('/api/namespaces', methods=['POST'])
def create_namespace():
    """Provision namespace"""
    data = request.json
    infra = SelfServiceInfrastructure()
    
    success = infra.provision_namespace(
        namespace=data['namespace'],
        team=data['team'],
        quotas=data.get('quotas', {
            'requests.cpu': '10',
            'requests.memory': '20Gi',
            'pods': '50'
        })
    )
    
    if success:
        return jsonify({'status': 'created'})
    return jsonify({'error': 'Failed to create namespace'}), 500

@app.route('/api/docs/<service_name>', methods=['GET'])
def get_docs(service_name):
    """Get service documentation"""
    doc_file = DOCS_DIR / f'{service_name}-api.md'
    
    if doc_file.exists():
        return jsonify({'documentation': doc_file.read_text()})
    return jsonify({'error': 'Documentation not found'}), 404

################################################################################
# Developer Portal Platform
################################################################################

class DeveloperPortalPlatform:
    """Complete developer experience orchestrator"""
    
    def __init__(self):
        self.catalog = ServiceCatalog()
        self.infra = SelfServiceInfrastructure()
        self.docs_gen = DocumentationGenerator()
    
    def bootstrap_developer_portal(self):
        """Bootstrap complete developer portal"""
        
        # Register sample services
        self.catalog.register_service('user-service', {
            'version': '1.0.0',
            'description': 'User management service',
            'endpoints': [
                {
                    'path': '/users',
                    'method': 'GET',
                    'summary': 'List users'
                },
                {
                    'path': '/users/{id}',
                    'method': 'GET',
                    'summary': 'Get user by ID'
                }
            ],
            'team': 'Platform'
        })
        
        # Create templates
        self.infra.create_project_template('python-microservice')
        self.infra.create_project_template('nodejs-api')
        
        # Generate documentation
        self.docs_gen.generate_api_docs('user-service', [
            {
                'path': '/users',
                'method': 'GET',
                'description': 'Retrieve list of users',
                'parameters': [
                    {'name': 'limit', 'type': 'int', 'description': 'Number of results'}
                ]
            }
        ])
        
        self.docs_gen.generate_runbook('user-service')
        
        logger.info("Developer portal bootstrapped")

################################################################################
# CLI
################################################################################

def main():
    logger.info("🚀 Developer Experience Platform - Iteration 9")
    
    if '--bootstrap' in sys.argv:
        platform = DeveloperPortalPlatform()
        platform.bootstrap_developer_portal()
        print("✅ Developer portal bootstrapped")
    
    elif '--serve' in sys.argv:
        logger.info("Starting developer portal API server")
        app.run(host='0.0.0.0', port=5000)
    
    else:
        print("""
Developer Experience Platform v13.0 - Iteration 9

Usage:
  --bootstrap    Bootstrap developer portal
  --serve        Start portal API server

Features:
  ✓ Service catalog with API discovery
  ✓ Self-service infrastructure
  ✓ Project templates
  ✓ Automated documentation
  ✓ CI/CD pipeline generation
        """)

if __name__ == '__main__':
    main()
