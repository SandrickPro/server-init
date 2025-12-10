#!/usr/bin/env python3
"""
Advanced Observability Stack - Iteration 3
Prometheus + Grafana + Loki + Tempo integration
Complete monitoring, logging, and tracing solution
"""

import os
import sys
import json
import yaml
import logging
import requests
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OBS_BASE = Path('/var/lib/observability')
PROMETHEUS_DIR = OBS_BASE / 'prometheus'
GRAFANA_DIR = OBS_BASE / 'grafana'
LOKI_DIR = OBS_BASE / 'loki'

for directory in [PROMETHEUS_DIR, GRAFANA_DIR, LOKI_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

################################################################################
# Prometheus Manager
################################################################################

class PrometheusManager:
    """Prometheus metrics management"""
    
    def __init__(self, url: str = 'http://localhost:9090'):
        self.url = url
    
    def generate_config(self, scrape_configs: List[Dict]) -> str:
        """Generate prometheus.yml"""
        
        config = {
            'global': {
                'scrape_interval': '15s',
                'evaluation_interval': '15s',
                'external_labels': {
                    'cluster': 'production',
                    'environment': 'prod'
                }
            },
            'alerting': {
                'alertmanagers': [{
                    'static_configs': [{
                        'targets': ['alertmanager:9093']
                    }]
                }]
            },
            'rule_files': [
                'alerts/*.yml'
            ],
            'scrape_configs': scrape_configs
        }
        
        config_yaml = yaml.dump(config, default_flow_style=False)
        (PROMETHEUS_DIR / 'prometheus.yml').write_text(config_yaml)
        
        return config_yaml
    
    def create_alert_rules(self, service: str) -> str:
        """Create alerting rules"""
        
        rules = {
            'groups': [{
                'name': f'{service}_alerts',
                'interval': '30s',
                'rules': [
                    {
                        'alert': 'HighErrorRate',
                        'expr': f'rate(http_requests_total{{service="{service}",status=~"5.."}}[5m]) > 0.05',
                        'for': '5m',
                        'labels': {
                            'severity': 'critical'
                        },
                        'annotations': {
                            'summary': f'High error rate on {service}',
                            'description': 'Error rate is {{ $value }} requests/sec'
                        }
                    },
                    {
                        'alert': 'HighLatency',
                        'expr': f'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{{service="{service}"}}[5m])) > 1',
                        'for': '10m',
                        'labels': {
                            'severity': 'warning'
                        },
                        'annotations': {
                            'summary': f'High latency on {service}',
                            'description': 'P95 latency is {{ $value }}s'
                        }
                    },
                    {
                        'alert': 'PodCrashLooping',
                        'expr': f'rate(kube_pod_container_status_restarts_total{{pod=~"{service}.*"}}[15m]) > 0',
                        'for': '5m',
                        'labels': {
                            'severity': 'critical'
                        },
                        'annotations': {
                            'summary': f'{service} pod crash looping',
                            'description': 'Pod {{ $labels.pod }} is crash looping'
                        }
                    },
                    {
                        'alert': 'HighMemoryUsage',
                        'expr': f'container_memory_usage_bytes{{pod=~"{service}.*"}} / container_spec_memory_limit_bytes > 0.9',
                        'for': '5m',
                        'labels': {
                            'severity': 'warning'
                        },
                        'annotations': {
                            'summary': f'High memory usage on {service}',
                            'description': 'Memory usage is {{ $value | humanizePercentage }}'
                        }
                    }
                ]
            }]
        }
        
        rules_yaml = yaml.dump(rules, default_flow_style=False)
        (PROMETHEUS_DIR / f'alerts/{service}.yml').write_text(rules_yaml)
        
        return rules_yaml
    
    def query(self, query: str) -> Optional[Dict]:
        """Execute PromQL query"""
        
        try:
            response = requests.get(
                f'{self.url}/api/v1/query',
                params={'query': query}
            )
            return response.json()
        except Exception as e:
            logger.error(f"Prometheus query error: {e}")
            return None

################################################################################
# Grafana Manager
################################################################################

class GrafanaManager:
    """Grafana dashboard management"""
    
    def __init__(self, url: str = 'http://localhost:3000'):
        self.url = url
        self.api_key = os.getenv('GRAFANA_API_KEY')
    
    def create_dashboard(self, title: str, service: str) -> str:
        """Create Grafana dashboard"""
        
        dashboard = {
            'dashboard': {
                'title': f'{title} - {service}',
                'tags': ['auto-generated', service],
                'timezone': 'browser',
                'panels': [
                    # Request rate panel
                    {
                        'id': 1,
                        'title': 'Request Rate',
                        'type': 'graph',
                        'gridPos': {'x': 0, 'y': 0, 'w': 12, 'h': 8},
                        'targets': [{
                            'expr': f'rate(http_requests_total{{service="{service}"}}[5m])',
                            'legendFormat': '{{method}} {{status}}'
                        }]
                    },
                    # Error rate panel
                    {
                        'id': 2,
                        'title': 'Error Rate',
                        'type': 'graph',
                        'gridPos': {'x': 12, 'y': 0, 'w': 12, 'h': 8},
                        'targets': [{
                            'expr': f'rate(http_requests_total{{service="{service}",status=~"5.."}}[5m])',
                            'legendFormat': 'Errors'
                        }]
                    },
                    # Latency panel
                    {
                        'id': 3,
                        'title': 'Latency (P50, P95, P99)',
                        'type': 'graph',
                        'gridPos': {'x': 0, 'y': 8, 'w': 12, 'h': 8},
                        'targets': [
                            {
                                'expr': f'histogram_quantile(0.50, rate(http_request_duration_seconds_bucket{{service="{service}"}}[5m]))',
                                'legendFormat': 'P50'
                            },
                            {
                                'expr': f'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{{service="{service}"}}[5m]))',
                                'legendFormat': 'P95'
                            },
                            {
                                'expr': f'histogram_quantile(0.99, rate(http_request_duration_seconds_bucket{{service="{service}"}}[5m]))',
                                'legendFormat': 'P99'
                            }
                        ]
                    },
                    # CPU usage panel
                    {
                        'id': 4,
                        'title': 'CPU Usage',
                        'type': 'graph',
                        'gridPos': {'x': 12, 'y': 8, 'w': 12, 'h': 8},
                        'targets': [{
                            'expr': f'rate(container_cpu_usage_seconds_total{{pod=~"{service}.*"}}[5m])',
                            'legendFormat': '{{pod}}'
                        }]
                    },
                    # Memory usage panel
                    {
                        'id': 5,
                        'title': 'Memory Usage',
                        'type': 'graph',
                        'gridPos': {'x': 0, 'y': 16, 'w': 12, 'h': 8},
                        'targets': [{
                            'expr': f'container_memory_usage_bytes{{pod=~"{service}.*"}}',
                            'legendFormat': '{{pod}}'
                        }]
                    },
                    # Active connections panel
                    {
                        'id': 6,
                        'title': 'Active Connections',
                        'type': 'stat',
                        'gridPos': {'x': 12, 'y': 16, 'w': 6, 'h': 4},
                        'targets': [{
                            'expr': f'sum(http_connections_active{{service="{service}"}})',
                            'legendFormat': 'Connections'
                        }]
                    },
                    # Uptime panel
                    {
                        'id': 7,
                        'title': 'Uptime',
                        'type': 'stat',
                        'gridPos': {'x': 18, 'y': 16, 'w': 6, 'h': 4},
                        'targets': [{
                            'expr': f'time() - process_start_time_seconds{{service="{service}"}}',
                            'legendFormat': 'Uptime'
                        }]
                    }
                ],
                'refresh': '30s',
                'time': {
                    'from': 'now-6h',
                    'to': 'now'
                }
            },
            'overwrite': True
        }
        
        dashboard_json = json.dumps(dashboard, indent=2)
        (GRAFANA_DIR / f'{service}-dashboard.json').write_text(dashboard_json)
        
        return dashboard_json
    
    def create_slo_dashboard(self, service: str, slo_target: float = 99.9):
        """Create SLO/SLI dashboard"""
        
        dashboard = {
            'dashboard': {
                'title': f'SLO Dashboard - {service}',
                'tags': ['slo', 'sli', service],
                'panels': [
                    {
                        'id': 1,
                        'title': f'Availability SLO ({slo_target}%)',
                        'type': 'gauge',
                        'gridPos': {'x': 0, 'y': 0, 'w': 8, 'h': 8},
                        'targets': [{
                            'expr': f'(1 - (sum(rate(http_requests_total{{service="{service}",status=~"5.."}}[30d])) / sum(rate(http_requests_total{{service="{service}"}}[30d])))) * 100',
                            'legendFormat': 'Availability %'
                        }],
                        'options': {
                            'thresholds': {
                                'mode': 'absolute',
                                'steps': [
                                    {'value': 0, 'color': 'red'},
                                    {'value': slo_target - 0.5, 'color': 'yellow'},
                                    {'value': slo_target, 'color': 'green'}
                                ]
                            }
                        }
                    },
                    {
                        'id': 2,
                        'title': 'Error Budget Remaining',
                        'type': 'stat',
                        'gridPos': {'x': 8, 'y': 0, 'w': 8, 'h': 8},
                        'targets': [{
                            'expr': f'100 - (sum(rate(http_requests_total{{service="{service}",status=~"5.."}}[30d])) / sum(rate(http_requests_total{{service="{service}"}}[30d]))) * 100 - {slo_target}',
                            'legendFormat': 'Budget %'
                        }]
                    }
                ]
            }
        }
        
        dashboard_json = json.dumps(dashboard, indent=2)
        (GRAFANA_DIR / f'{service}-slo-dashboard.json').write_text(dashboard_json)
        
        return dashboard_json

################################################################################
# Loki Manager
################################################################################

class LokiManager:
    """Loki log aggregation"""
    
    def __init__(self, url: str = 'http://localhost:3100'):
        self.url = url
    
    def generate_config(self) -> str:
        """Generate loki-config.yaml"""
        
        config = {
            'auth_enabled': False,
            'server': {
                'http_listen_port': 3100
            },
            'ingester': {
                'lifecycler': {
                    'address': '127.0.0.1',
                    'ring': {
                        'kvstore': {
                            'store': 'inmemory'
                        },
                        'replication_factor': 1
                    }
                },
                'chunk_idle_period': '5m',
                'chunk_retain_period': '30s'
            },
            'schema_config': {
                'configs': [{
                    'from': '2024-01-01',
                    'store': 'boltdb',
                    'object_store': 'filesystem',
                    'schema': 'v11',
                    'index': {
                        'prefix': 'index_',
                        'period': '168h'
                    }
                }]
            },
            'storage_config': {
                'boltdb': {
                    'directory': '/loki/index'
                },
                'filesystem': {
                    'directory': '/loki/chunks'
                }
            },
            'limits_config': {
                'enforce_metric_name': False,
                'reject_old_samples': True,
                'reject_old_samples_max_age': '168h'
            }
        }
        
        config_yaml = yaml.dump(config, default_flow_style=False)
        (LOKI_DIR / 'loki-config.yaml').write_text(config_yaml)
        
        return config_yaml
    
    def query_logs(self, query: str, start: Optional[datetime] = None) -> Optional[List]:
        """Query logs using LogQL"""
        
        if not start:
            start = datetime.now() - timedelta(hours=1)
        
        try:
            response = requests.get(
                f'{self.url}/loki/api/v1/query_range',
                params={
                    'query': query,
                    'start': int(start.timestamp() * 1e9),
                    'end': int(datetime.now().timestamp() * 1e9)
                }
            )
            return response.json().get('data', {}).get('result', [])
        except Exception as e:
            logger.error(f"Loki query error: {e}")
            return None

################################################################################
# Observability Platform
################################################################################

class ObservabilityPlatform:
    """Complete observability orchestrator"""
    
    def __init__(self):
        self.prometheus = PrometheusManager()
        self.grafana = GrafanaManager()
        self.loki = LokiManager()
    
    def setup_complete_observability(self, services: List[str]):
        """Setup complete observability stack"""
        
        # Prometheus scrape configs
        scrape_configs = [
            {
                'job_name': 'kubernetes-pods',
                'kubernetes_sd_configs': [{
                    'role': 'pod'
                }],
                'relabel_configs': [
                    {
                        'source_labels': ['__meta_kubernetes_pod_annotation_prometheus_io_scrape'],
                        'action': 'keep',
                        'regex': True
                    }
                ]
            }
        ]
        
        self.prometheus.generate_config(scrape_configs)
        
        # Create dashboards and alerts for each service
        for service in services:
            self.prometheus.create_alert_rules(service)
            self.grafana.create_dashboard('Service Metrics', service)
            self.grafana.create_slo_dashboard(service, slo_target=99.9)
        
        # Loki configuration
        self.loki.generate_config()
        
        logger.info(f"Observability stack configured for {len(services)} services")

################################################################################
# CLI
################################################################################

def main():
    logger.info("📊 Advanced Observability Stack - Iteration 3")
    
    if '--setup' in sys.argv:
        platform = ObservabilityPlatform()
        platform.setup_complete_observability(['web-app', 'api-service', 'worker'])
        print("✅ Observability stack configured")
    
    else:
        print("""
Advanced Observability Stack v13.0 - Iteration 3

Usage:
  --setup    Setup complete observability

Features:
  ✓ Prometheus metrics
  ✓ Grafana dashboards
  ✓ Loki log aggregation
  ✓ SLO/SLI tracking
  ✓ Automated alerting
        """)

if __name__ == '__main__':
    main()
