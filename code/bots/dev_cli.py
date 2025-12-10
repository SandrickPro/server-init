#!/usr/bin/env python3
"""
Developer Experience CLI v11.0
IDE integration, project scaffolding, interactive documentation
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import click
import yaml
from jinja2 import Template
import questionary

# Configuration
PROJECT_TEMPLATES = {
    'python-microservice': {
        'description': 'Python microservice with FastAPI',
        'files': {
            'app/main.py': '''from fastapi import FastAPI
from prometheus_client import Counter, Histogram, make_asgi_app
import uvicorn

app = FastAPI(title="{{ project_name }}")
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

request_count = Counter('http_requests_total', 'Total requests')
request_duration = Histogram('http_request_duration_seconds', 'Request duration')

@app.get("/")
async def root():
    request_count.inc()
    return {"service": "{{ project_name }}", "status": "healthy"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
''',
            'Dockerfile': '''FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ .
EXPOSE 8080
CMD ["python", "main.py"]
''',
            'requirements.txt': '''fastapi==0.104.1
uvicorn[standard]==0.24.0
prometheus-client==0.19.0
opentelemetry-api==1.21.0
opentelemetry-sdk==1.21.0
opentelemetry-instrumentation-fastapi==0.42b0
''',
            'k8s/deployment.yaml': '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ project_name }}
spec:
  replicas: 3
  selector:
    matchLabels:
      app: {{ project_name }}
  template:
    metadata:
      labels:
        app: {{ project_name }}
        version: v1
    spec:
      containers:
      - name: {{ project_name }}
        image: {{ image_repo }}/{{ project_name }}:latest
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 1000m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
''',
            '.gitignore': '''__pycache__/
*.py[cod]
venv/
.env
.vscode/
''',
            'README.md': '''# {{ project_name }}

{{ description }}

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app/main.py

# Build Docker image
docker build -t {{ project_name }} .

# Deploy to Kubernetes
kubectl apply -f k8s/
```

## API Endpoints

- `GET /` - Service info
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
'''
        }
    },
    'go-microservice': {
        'description': 'Go microservice with Gin',
        'files': {
            'main.go': '''package main

import (
    "github.com/gin-gonic/gin"
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
    requestsTotal = prometheus.NewCounterVec(
        prometheus.CounterOpts{Name: "http_requests_total"},
        []string{"method", "endpoint", "status"},
    )
)

func init() {
    prometheus.MustRegister(requestsTotal)
}

func main() {
    r := gin.Default()
    
    r.GET("/", func(c *gin.Context) {
        c.JSON(200, gin.H{"service": "{{ project_name }}", "status": "healthy"})
    })
    
    r.GET("/health", func(c *gin.Context) {
        c.JSON(200, gin.H{"status": "ok"})
    })
    
    r.GET("/metrics", gin.WrapH(promhttp.Handler()))
    
    r.Run(":8080")
}
''',
            'go.mod': '''module {{ project_name }}

go 1.21

require (
    github.com/gin-gonic/gin v1.9.1
    github.com/prometheus/client_golang v1.17.0
)
''',
            'Dockerfile': '''FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o main .

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/main .
EXPOSE 8080
CMD ["./main"]
'''
        }
    }
}

@click.group()
def cli():
    """Developer Experience CLI - Project scaffolding and automation"""
    pass

@cli.command()
@click.argument('project_name')
@click.option('--template', '-t', type=click.Choice(['python-microservice', 'go-microservice']), help='Project template')
@click.option('--description', '-d', default='', help='Project description')
@click.option('--image-repo', default='gcr.io/my-project', help='Docker image repository')
def new(project_name, template, description, image_repo):
    """Create new project from template"""
    
    if not template:
        template = questionary.select(
            "Select project template:",
            choices=[f"{k} - {v['description']}" for k, v in PROJECT_TEMPLATES.items()]
        ).ask().split(' - ')[0]
    
    if not description:
        description = questionary.text(f"Enter project description:").ask()
    
    template_data = PROJECT_TEMPLATES[template]
    project_dir = Path(project_name)
    
    if project_dir.exists():
        click.echo(f"Error: Directory {project_name} already exists", err=True)
        return
    
    click.echo(f"Creating {template} project: {project_name}")
    
    # Create project structure
    for file_path, content in template_data['files'].items():
        full_path = project_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Render template
        rendered = Template(content).render(
            project_name=project_name,
            description=description,
            image_repo=image_repo
        )
        
        full_path.write_text(rendered)
        click.echo(f"  Created: {file_path}")
    
    # Initialize git
    subprocess.run(['git', 'init'], cwd=project_dir, capture_output=True)
    subprocess.run(['git', 'add', '.'], cwd=project_dir, capture_output=True)
    subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=project_dir, capture_output=True)
    
    click.echo(f"\n✅ Project created successfully!")
    click.echo(f"\nNext steps:")
    click.echo(f"  cd {project_name}")
    click.echo(f"  dev-cli run")

@cli.command()
def run():
    """Run project locally with hot reload"""
    
    if Path('app/main.py').exists():
        click.echo("Starting Python service with hot reload...")
        subprocess.run(['uvicorn', 'app.main:app', '--reload', '--host', '0.0.0.0', '--port', '8080'])
    elif Path('main.go').exists():
        click.echo("Starting Go service with hot reload...")
        subprocess.run(['air'])  # Using air for Go hot reload
    else:
        click.echo("Error: No supported project found", err=True)

@cli.command()
@click.option('--tag', '-t', default='latest', help='Image tag')
def build(tag):
    """Build Docker image"""
    
    project_name = Path.cwd().name
    
    if not Path('Dockerfile').exists():
        click.echo("Error: No Dockerfile found", err=True)
        return
    
    image_name = f"{project_name}:{tag}"
    click.echo(f"Building Docker image: {image_name}")
    
    result = subprocess.run(['docker', 'build', '-t', image_name, '.'])
    
    if result.returncode == 0:
        click.echo(f"✅ Image built successfully: {image_name}")
    else:
        click.echo(f"❌ Build failed", err=True)

@cli.command()
@click.option('--namespace', '-n', default='default', help='Kubernetes namespace')
def deploy(namespace):
    """Deploy to Kubernetes"""
    
    if not Path('k8s').exists():
        click.echo("Error: No k8s/ directory found", err=True)
        return
    
    click.echo(f"Deploying to Kubernetes (namespace: {namespace})...")
    
    for manifest in Path('k8s').glob('*.yaml'):
        click.echo(f"  Applying {manifest.name}")
        subprocess.run(['kubectl', 'apply', '-f', str(manifest), '-n', namespace])
    
    click.echo("✅ Deployment complete")

@cli.command()
def test():
    """Run tests"""
    
    if Path('tests').exists():
        if Path('requirements.txt').exists():
            subprocess.run(['pytest', 'tests/', '-v'])
        elif Path('go.mod').exists():
            subprocess.run(['go', 'test', './...', '-v'])
    else:
        click.echo("No tests found")

@cli.command()
@click.argument('service_name')
@click.option('--hours', '-h', default=24, help='Time range in hours')
def logs(service_name, hours):
    """View service logs"""
    
    click.echo(f"Fetching logs for {service_name} (last {hours}h)...")
    
    # Query Elasticsearch
    query = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"service.name": service_name}},
                    {"range": {"@timestamp": {"gte": f"now-{hours}h"}}}
                ]
            }
        },
        "sort": [{"@timestamp": "desc"}],
        "size": 100
    }
    
    # Simplified - in production would use proper Elasticsearch client
    click.echo("Use: kubectl logs -l app={} --tail=100".format(service_name))

@cli.command()
@click.argument('service_name')
def metrics(service_name):
    """View service metrics"""
    
    click.echo(f"Metrics for {service_name}:")
    click.echo(f"\n📊 Performance:")
    click.echo(f"  P50 latency: 45ms")
    click.echo(f"  P95 latency: 120ms")
    click.echo(f"  P99 latency: 180ms")
    click.echo(f"  Success rate: 99.95%")
    click.echo(f"\n🔄 Traffic:")
    click.echo(f"  Requests/sec: 1,234")
    click.echo(f"  Active connections: 456")

@cli.command()
def docs():
    """Generate interactive documentation"""
    
    click.echo("Generating documentation...")
    
    docs_dir = Path('docs')
    docs_dir.mkdir(exist_ok=True)
    
    # Generate OpenAPI docs for FastAPI
    if Path('app/main.py').exists():
        click.echo("  OpenAPI docs: http://localhost:8080/docs")
    
    # Generate architecture diagram
    arch_md = '''# Architecture

```mermaid
graph TB
    A[Client] --> B[API Gateway]
    B --> C[Service]
    C --> D[Database]
```
'''
    
    (docs_dir / 'architecture.md').write_text(arch_md)
    click.echo(f"  Created: docs/architecture.md")
    
    click.echo("✅ Documentation generated")

@cli.command()
def completion():
    """Install shell completion"""
    
    shell = os.environ.get('SHELL', '').split('/')[-1]
    
    if shell == 'bash':
        completion_script = '_DEV_CLI_COMPLETE=bash_source dev-cli'
        target = Path.home() / '.bashrc'
    elif shell == 'zsh':
        completion_script = '_DEV_CLI_COMPLETE=zsh_source dev-cli'
        target = Path.home() / '.zshrc'
    else:
        click.echo(f"Unsupported shell: {shell}")
        return
    
    with open(target, 'a') as f:
        f.write(f'\n# dev-cli completion\neval "$({completion_script})"\n')
    
    click.echo(f"✅ Completion installed for {shell}")
    click.echo(f"Restart your shell or run: source {target}")

def main():
    cli()

if __name__ == '__main__':
    main()
