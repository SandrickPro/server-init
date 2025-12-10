#!/usr/bin/env bash

###############################################################################
# DISTRIBUTED TRACING MODULE v11.0
# Complete request flow visualization with Jaeger + OpenTelemetry
###############################################################################

set -euo pipefail

# Configuration
JAEGER_VERSION="1.52.0"
OTEL_COLLECTOR_VERSION="0.91.0"
TRACE_SAMPLING_RATE="${TRACE_SAMPLING_RATE:-1.0}"  # 100% sampling for development
JAEGER_STORAGE="${JAEGER_STORAGE:-elasticsearch}"

###############################################################################
# Jaeger Installation
###############################################################################

install_jaeger() {
    echo "🔍 Installing Jaeger ${JAEGER_VERSION}..."
    
    # Create jaeger user
    useradd --system --no-create-home --shell /bin/false jaeger 2>/dev/null || true
    
    # Download Jaeger
    cd /tmp
    wget "https://github.com/jaegertracing/jaeger/releases/download/v${JAEGER_VERSION}/jaeger-${JAEGER_VERSION}-linux-amd64.tar.gz"
    tar -xzf "jaeger-${JAEGER_VERSION}-linux-amd64.tar.gz"
    
    # Install binaries
    cp "jaeger-${JAEGER_VERSION}-linux-amd64/jaeger-all-in-one" /usr/local/bin/
    cp "jaeger-${JAEGER_VERSION}-linux-amd64/jaeger-query" /usr/local/bin/
    cp "jaeger-${JAEGER_VERSION}-linux-amd64/jaeger-collector" /usr/local/bin/
    cp "jaeger-${JAEGER_VERSION}-linux-amd64/jaeger-agent" /usr/local/bin/
    
    chmod +x /usr/local/bin/jaeger-*
    chown jaeger:jaeger /usr/local/bin/jaeger-*
    
    # Cleanup
    rm -rf "jaeger-${JAEGER_VERSION}-linux-amd64"*
    
    echo "✅ Jaeger binaries installed"
}

configure_jaeger_storage() {
    echo "📊 Configuring Jaeger storage backend..."
    
    case $JAEGER_STORAGE in
        elasticsearch)
            # Install Elasticsearch
            wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg
            echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | \
                tee /etc/apt/sources.list.d/elastic-8.x.list
            
            apt-get update
            apt-get install -y elasticsearch
            
            # Configure Elasticsearch
            cat >> /etc/elasticsearch/elasticsearch.yml << EOF
cluster.name: jaeger-cluster
node.name: jaeger-node-1
network.host: 127.0.0.1
http.port: 9200
xpack.security.enabled: false
EOF
            
            systemctl enable elasticsearch
            systemctl start elasticsearch
            
            # Wait for Elasticsearch
            sleep 30
            
            # Create Jaeger indices
            curl -X PUT "localhost:9200/jaeger-span-2024" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1
  },
  "mappings": {
    "properties": {
      "traceID": { "type": "keyword" },
      "spanID": { "type": "keyword" },
      "operationName": { "type": "keyword" },
      "startTime": { "type": "long" },
      "duration": { "type": "long" },
      "tags": { "type": "nested" }
    }
  }
}'
            ;;
        
        badger)
            # Use embedded Badger DB
            mkdir -p /var/lib/jaeger/badger
            chown -R jaeger:jaeger /var/lib/jaeger
            ;;
        
        memory)
            # Use in-memory storage (development only)
            echo "Using in-memory storage (not for production)"
            ;;
    esac
    
    echo "✅ Storage backend configured"
}

create_jaeger_services() {
    echo "🚀 Creating Jaeger systemd services..."
    
    # Jaeger Collector
    cat > /etc/systemd/system/jaeger-collector.service << EOF
[Unit]
Description=Jaeger Collector
After=network.target

[Service]
Type=simple
User=jaeger
ExecStart=/usr/local/bin/jaeger-collector \\
    --span-storage.type=elasticsearch \\
    --es.server-urls=http://localhost:9200 \\
    --collector.zipkin.host-port=:9411 \\
    --collector.grpc-server.host-port=:14250 \\
    --collector.http-server.host-port=:14268
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
    
    # Jaeger Query
    cat > /etc/systemd/system/jaeger-query.service << EOF
[Unit]
Description=Jaeger Query Service
After=network.target jaeger-collector.service

[Service]
Type=simple
User=jaeger
ExecStart=/usr/local/bin/jaeger-query \\
    --span-storage.type=elasticsearch \\
    --es.server-urls=http://localhost:9200 \\
    --query.port=16686
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
    
    # Jaeger Agent
    cat > /etc/systemd/system/jaeger-agent.service << EOF
[Unit]
Description=Jaeger Agent
After=network.target jaeger-collector.service

[Service]
Type=simple
User=jaeger
ExecStart=/usr/local/bin/jaeger-agent \\
    --reporter.grpc.host-port=localhost:14250 \\
    --agent.tags=host=\$(hostname)
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload and start services
    systemctl daemon-reload
    systemctl enable jaeger-collector jaeger-query jaeger-agent
    systemctl start jaeger-collector jaeger-query jaeger-agent
    
    echo "✅ Jaeger services created and started"
}

###############################################################################
# OpenTelemetry Collector
###############################################################################

install_otel_collector() {
    echo "📡 Installing OpenTelemetry Collector ${OTEL_COLLECTOR_VERSION}..."
    
    # Download OTEL Collector
    cd /tmp
    wget "https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v${OTEL_COLLECTOR_VERSION}/otelcol_${OTEL_COLLECTOR_VERSION}_linux_amd64.tar.gz"
    tar -xzf "otelcol_${OTEL_COLLECTOR_VERSION}_linux_amd64.tar.gz"
    
    # Install binary
    mv otelcol /usr/local/bin/otelcol
    chmod +x /usr/local/bin/otelcol
    
    # Create user
    useradd --system --no-create-home --shell /bin/false otel 2>/dev/null || true
    
    # Create config directory
    mkdir -p /etc/otel
    
    # Cleanup
    rm -f "otelcol_${OTEL_COLLECTOR_VERSION}_linux_amd64.tar.gz"
    
    echo "✅ OpenTelemetry Collector installed"
}

configure_otel_collector() {
    echo "⚙️  Configuring OpenTelemetry Collector..."
    
    cat > /etc/otel/config.yaml << EOF
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318
  
  prometheus:
    config:
      scrape_configs:
        - job_name: 'otel-collector'
          scrape_interval: 30s
          static_configs:
            - targets: ['localhost:8888']
  
  jaeger:
    protocols:
      grpc:
        endpoint: 0.0.0.0:14250
      thrift_http:
        endpoint: 0.0.0.0:14268
  
  zipkin:
    endpoint: 0.0.0.0:9411

processors:
  batch:
    timeout: 10s
    send_batch_size: 1024
  
  memory_limiter:
    check_interval: 1s
    limit_mib: 512
  
  resourcedetection:
    detectors: [env, system, docker]
  
  attributes:
    actions:
      - key: environment
        value: production
        action: insert
      - key: service.version
        value: v11.0
        action: insert

exporters:
  jaeger:
    endpoint: localhost:14250
    tls:
      insecure: true
  
  prometheus:
    endpoint: "0.0.0.0:8889"
  
  logging:
    loglevel: info
  
  elasticsearch:
    endpoints: [http://localhost:9200]
    logs_index: otel-logs
    traces_index: otel-traces

extensions:
  health_check:
    endpoint: :13133
  pprof:
    endpoint: :1777
  zpages:
    endpoint: :55679

service:
  extensions: [health_check, pprof, zpages]
  pipelines:
    traces:
      receivers: [otlp, jaeger, zipkin]
      processors: [memory_limiter, batch, resourcedetection, attributes]
      exporters: [jaeger, logging]
    
    metrics:
      receivers: [otlp, prometheus]
      processors: [memory_limiter, batch]
      exporters: [prometheus, logging]
    
    logs:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [elasticsearch, logging]
EOF
    
    chown otel:otel /etc/otel/config.yaml
    
    echo "✅ OpenTelemetry Collector configured"
}

create_otel_service() {
    echo "🚀 Creating OpenTelemetry Collector systemd service..."
    
    cat > /etc/systemd/system/otel-collector.service << EOF
[Unit]
Description=OpenTelemetry Collector
After=network.target

[Service]
Type=simple
User=otel
ExecStart=/usr/local/bin/otelcol --config=/etc/otel/config.yaml
Restart=on-failure
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable otel-collector
    systemctl start otel-collector
    
    echo "✅ OpenTelemetry Collector service created"
}

###############################################################################
# Application Instrumentation
###############################################################################

instrument_nginx() {
    echo "🔧 Instrumenting nginx with tracing..."
    
    # Install nginx OpenTelemetry module
    apt-get install -y nginx-module-otel
    
    # Configure nginx
    cat > /etc/nginx/conf.d/tracing.conf << 'EOF'
load_module modules/ngx_http_opentelemetry_module.so;

http {
    opentelemetry on;
    opentelemetry_config /etc/nginx/otel-config.toml;
    
    opentelemetry_operation_name $request_method;
    opentelemetry_propagate;
    
    opentelemetry_attribute "http.method" $request_method;
    opentelemetry_attribute "http.target" $request_uri;
    opentelemetry_attribute "http.status_code" $status;
    opentelemetry_attribute "http.client_ip" $remote_addr;
}
EOF
    
    # OTEL config for nginx
    cat > /etc/nginx/otel-config.toml << EOF
[exporter.otlp]
host = "localhost"
port = 4317

[processor.batch]
max_queue_size = 2048
schedule_delay_millis = 5000
max_export_batch_size = 512

[service]
name = "nginx"
EOF
    
    nginx -t && systemctl reload nginx
    
    echo "✅ Nginx instrumented"
}

instrument_python_apps() {
    echo "🐍 Instrumenting Python applications..."
    
    # Install OpenTelemetry for Python
    pip3 install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation \
        opentelemetry-exporter-otlp opentelemetry-instrumentation-flask \
        opentelemetry-instrumentation-requests opentelemetry-instrumentation-psycopg2 \
        opentelemetry-instrumentation-redis
    
    # Create instrumentation wrapper
    cat > /opt/telegram-bot/tracing_setup.py << 'EOF'
"""
OpenTelemetry instrumentation setup for Python applications
"""
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

def setup_tracing(service_name: str, version: str = "v11.0"):
    """Setup distributed tracing for the application"""
    
    # Create resource
    resource = Resource.create({
        "service.name": service_name,
        "service.version": version,
        "deployment.environment": "production"
    })
    
    # Create tracer provider
    provider = TracerProvider(resource=resource)
    
    # Create OTLP exporter
    otlp_exporter = OTLPSpanExporter(
        endpoint="http://localhost:4317",
        insecure=True
    )
    
    # Add batch span processor
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    
    # Set global tracer provider
    trace.set_tracer_provider(provider)
    
    # Auto-instrument libraries
    FlaskInstrumentor().instrument()
    RequestsInstrumentor().instrument()
    Psycopg2Instrumentor().instrument()
    RedisInstrumentor().instrument()
    
    return trace.get_tracer(service_name)

# Example usage in application:
# from tracing_setup import setup_tracing
# tracer = setup_tracing("devops-manager-bot")
#
# # Manual span creation
# with tracer.start_as_current_span("process_command") as span:
#     span.set_attribute("command", "/status")
#     # Your code here
#     span.add_event("Command processed successfully")
EOF
    
    echo "✅ Python tracing instrumentation created"
}

instrument_postgresql() {
    echo "🗄️  Instrumenting PostgreSQL with pg_stat_statements..."
    
    # Enable pg_stat_statements
    cat >> /etc/postgresql/*/main/postgresql.conf << EOF

# Query performance tracking
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.max = 10000
pg_stat_statements.track = all
EOF
    
    systemctl restart postgresql
    
    # Enable extension in databases
    su - postgres -c "psql -c 'CREATE EXTENSION IF NOT EXISTS pg_stat_statements;'"
    
    echo "✅ PostgreSQL instrumented"
}

###############################################################################
# Trace Sampling & Filtering
###############################################################################

configure_sampling() {
    echo "🎯 Configuring trace sampling..."
    
    cat > /etc/otel/sampling-rules.yaml << EOF
# Sampling configuration for OpenTelemetry

# Always sample errors
- name: errors
  sample_rate: 1.0
  conditions:
    - attribute: http.status_code
      operator: ">"
      value: 399

# Always sample slow requests (>1s)
- name: slow_requests
  sample_rate: 1.0
  conditions:
    - attribute: http.duration_ms
      operator: ">"
      value: 1000

# Sample 10% of normal traffic
- name: normal_traffic
  sample_rate: 0.1

# Always sample critical endpoints
- name: critical_endpoints
  sample_rate: 1.0
  conditions:
    - attribute: http.route
      operator: "in"
      value: ["/api/deploy", "/api/backup", "/api/security"]
EOF
    
    echo "✅ Sampling rules configured"
}

###############################################################################
# Dashboards & Visualization
###############################################################################

create_jaeger_dashboard() {
    echo "📊 Creating Jaeger dashboards in Grafana..."
    
    # Add Jaeger datasource to Grafana
    cat > /tmp/jaeger-datasource.json << EOF
{
  "name": "Jaeger",
  "type": "jaeger",
  "access": "proxy",
  "url": "http://localhost:16686",
  "basicAuth": false,
  "isDefault": false
}
EOF
    
    # Import datasource
    curl -X POST http://admin:admin@localhost:3000/api/datasources \
        -H "Content-Type: application/json" \
        -d @/tmp/jaeger-datasource.json || true
    
    # Create custom dashboard
    cat > /tmp/tracing-dashboard.json << 'EOF'
{
  "dashboard": {
    "title": "Distributed Tracing Overview",
    "tags": ["tracing", "performance"],
    "timezone": "browser",
    "panels": [
      {
        "title": "Request Throughput",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(jaeger_spans_total[5m])",
            "legendFormat": "{{operation}}"
          }
        ]
      },
      {
        "title": "Request Duration (P95)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, jaeger_duration_bucket)",
            "legendFormat": "P95"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(jaeger_errors_total[5m])",
            "legendFormat": "Errors"
          }
        ]
      },
      {
        "title": "Top Services",
        "type": "table",
        "targets": [
          {
            "expr": "topk(10, sum by (service) (jaeger_spans_total))"
          }
        ]
      }
    ]
  }
}
EOF
    
    curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
        -H "Content-Type: application/json" \
        -d @/tmp/tracing-dashboard.json || true
    
    rm -f /tmp/jaeger-datasource.json /tmp/tracing-dashboard.json
    
    echo "✅ Dashboards created"
}

###############################################################################
# Trace Analysis & Alerts
###############################################################################

setup_trace_alerts() {
    echo "🚨 Setting up trace-based alerts..."
    
    cat > /etc/prometheus/rules/tracing-alerts.yml << 'EOF'
groups:
  - name: tracing_alerts
    interval: 30s
    rules:
      # High error rate
      - alert: HighTraceErrorRate
        expr: rate(jaeger_errors_total[5m]) > 10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High trace error rate detected"
          description: "Error rate is {{ $value }} errors/sec"
      
      # Slow requests
      - alert: SlowTraceP95
        expr: histogram_quantile(0.95, jaeger_duration_bucket) > 2000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "P95 latency is too high"
          description: "P95 latency is {{ $value }}ms"
      
      # Service down
      - alert: ServiceNoTraces
        expr: rate(jaeger_spans_total{service="critical-service"}[5m]) == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "No traces from critical service"
          description: "Service {{ $labels.service }} is not sending traces"
EOF
    
    # Reload Prometheus
    curl -X POST http://localhost:9090/-/reload || true
    
    echo "✅ Trace alerts configured"
}

analyze_traces() {
    echo "🔬 Running trace analysis..."
    
    # Get trace statistics
    local total_spans=$(curl -s "http://localhost:16686/api/services" | jq -r '.data | length')
    echo "Total services traced: $total_spans"
    
    # Find slowest operations
    echo "Top 10 slowest operations:"
    curl -s "http://localhost:16686/api/traces?service=nginx&limit=100" | \
        jq -r '.data[] | .spans[] | "\(.duration) \(.operationName)"' | \
        sort -rn | head -10
    
    # Find error traces
    echo "Recent error traces:"
    curl -s "http://localhost:16686/api/traces?service=nginx&tags={\"error\":\"true\"}&limit=10" | \
        jq -r '.data[] | "\(.traceID) \(.spans[0].operationName)"'
    
    echo "✅ Trace analysis complete"
}

###############################################################################
# Main Setup
###############################################################################

setup_distributed_tracing() {
    echo "🔍 Setting up distributed tracing..."
    
    # Install Jaeger
    install_jaeger
    configure_jaeger_storage
    create_jaeger_services
    
    # Install OpenTelemetry
    install_otel_collector
    configure_otel_collector
    create_otel_service
    
    # Instrument applications
    instrument_nginx
    instrument_python_apps
    instrument_postgresql
    
    # Configure sampling
    configure_sampling
    
    # Setup dashboards
    create_jaeger_dashboard
    
    # Setup alerts
    setup_trace_alerts
    
    echo "✅ Distributed tracing setup complete!"
    echo ""
    echo "📋 Access information:"
    echo "   - Jaeger UI: http://localhost:16686"
    echo "   - OTEL Collector: http://localhost:13133 (health)"
    echo "   - OTEL ZPages: http://localhost:55679"
    echo ""
    echo "📊 Instrumentation:"
    echo "   - Nginx: Automatic via module"
    echo "   - Python: Import tracing_setup.py"
    echo "   - PostgreSQL: pg_stat_statements enabled"
    echo ""
    echo "🎯 Sampling:"
    echo "   - Errors: 100%"
    echo "   - Slow requests (>1s): 100%"
    echo "   - Normal traffic: ${TRACE_SAMPLING_RATE}"
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    setup_distributed_tracing
fi
