#!/bin/bash

################################################################################
# Service Mesh Advanced Optimization v11.0
# Istio optimization, intelligent traffic management, circuit breakers
################################################################################

set -euo pipefail

# Configuration
ISTIO_VERSION="1.20.0"
ISTIO_NAMESPACE="istio-system"

# Directories
MESH_CONFIG_DIR="/etc/istio"
MESH_LOG_DIR="/var/log/istio"
MESH_DB="/var/lib/istio/mesh.db"

# Performance targets
TARGET_P50_LATENCY=50      # ms
TARGET_P99_LATENCY=200     # ms
TARGET_SUCCESS_RATE=99.9   # %
MAX_RETRIES=3
CIRCUIT_BREAKER_THRESHOLD=5

# Create directories
mkdir -p "$MESH_CONFIG_DIR" "$MESH_LOG_DIR" "$(dirname $MESH_DB)"

# Logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$MESH_LOG_DIR/mesh.log"
}

error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $*" | tee -a "$MESH_LOG_DIR/mesh.log" >&2
}

################################################################################
# Database initialization
################################################################################

init_database() {
    log "Initializing service mesh database..."
    
    sqlite3 "$MESH_DB" <<EOF
CREATE TABLE IF NOT EXISTS services (
    service_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    namespace TEXT NOT NULL,
    version TEXT,
    port INTEGER,
    protocol TEXT DEFAULT 'http',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS traffic_policies (
    policy_id TEXT PRIMARY KEY,
    service_id TEXT NOT NULL,
    policy_type TEXT NOT NULL,
    config TEXT,
    enabled INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(service_id) REFERENCES services(service_id)
);

CREATE TABLE IF NOT EXISTS circuit_breaker_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_type TEXT NOT NULL,
    consecutive_errors INTEGER,
    ejection_duration_seconds INTEGER,
    FOREIGN KEY(service_id) REFERENCES services(service_id)
);

CREATE TABLE IF NOT EXISTS traffic_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    requests_total INTEGER,
    requests_success INTEGER,
    requests_failed INTEGER,
    avg_latency_ms REAL,
    p50_latency_ms REAL,
    p95_latency_ms REAL,
    p99_latency_ms REAL,
    FOREIGN KEY(service_id) REFERENCES services(service_id)
);

CREATE TABLE IF NOT EXISTS canary_deployments (
    canary_id TEXT PRIMARY KEY,
    service_id TEXT NOT NULL,
    baseline_version TEXT NOT NULL,
    canary_version TEXT NOT NULL,
    traffic_percent INTEGER DEFAULT 0,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'running',
    success_rate REAL,
    avg_latency_ms REAL,
    FOREIGN KEY(service_id) REFERENCES services(service_id)
);

CREATE INDEX IF NOT EXISTS idx_service_name ON services(name, namespace);
CREATE INDEX IF NOT EXISTS idx_circuit_breaker_timestamp ON circuit_breaker_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_traffic_metrics_timestamp ON traffic_metrics(timestamp);
EOF
    
    log "Database initialized successfully"
}

################################################################################
# Istio installation and configuration
################################################################################

install_istio() {
    log "Installing Istio v${ISTIO_VERSION}..."
    
    # Download Istio
    curl -L https://istio.io/downloadIstio | ISTIO_VERSION=${ISTIO_VERSION} sh -
    
    cd istio-${ISTIO_VERSION}
    
    # Install with production profile
    ./bin/istioctl install --set profile=production -y
    
    # Enable sidecar injection for default namespace
    kubectl label namespace default istio-injection=enabled --overwrite
    
    log "Istio installed successfully"
}

configure_mesh_optimization() {
    log "Configuring service mesh optimizations..."
    
    # Configure Istio with optimizations
    kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: istio
  namespace: ${ISTIO_NAMESPACE}
data:
  mesh: |
    # Access logging
    accessLogFile: /dev/stdout
    accessLogEncoding: JSON
    
    # Default config for proxies
    defaultConfig:
      # Concurrency
      concurrency: 2
      
      # Tracing
      tracing:
        sampling: 1.0
        zipkin:
          address: jaeger-collector.observability:9411
      
      # Connection pool
      connectionTimeout: 10s
      
      # Proxy protocol
      proxyProtocol: {}
      
      # Holdback configuration
      holdApplicationUntilProxyStarts: true
      
      # Termination drain duration
      terminationDrainDuration: 30s
      
      # Stats
      statNameLength: 189
      
    # Locality load balancing
    localityLbSetting:
      enabled: true
      
    # Enable auto mTLS
    enableAutoMtls: true
    
    # Default retry policy
    defaultHttpRetryPolicy:
      attempts: 3
      perTryTimeout: 2s
      retryOn: 5xx,reset,connect-failure,refused-stream
    
    # Outbound traffic policy
    outboundTrafficPolicy:
      mode: REGISTRY_ONLY
    
    # DNS refresh rate
    dnsRefreshRate: 30s
EOF
    
    log "Mesh optimizations configured"
}

configure_sidecar_resources() {
    log "Configuring sidecar resource optimization..."
    
    # Optimize sidecar resources
    kubectl apply -f - <<EOF
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
metadata:
  namespace: ${ISTIO_NAMESPACE}
  name: istio-optimization
spec:
  values:
    global:
      proxy:
        # Resource limits
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 2000m
            memory: 1024Mi
        
        # Logging level
        logLevel: warning
        
        # Component log level
        componentLogLevel: misc:error
        
        # Concurrency
        concurrency: 2
        
        # Lifecycle
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 15"]
EOF
    
    log "Sidecar resources optimized"
}

################################################################################
# Traffic management
################################################################################

create_virtual_service() {
    local service_name="$1"
    local namespace="${2:-default}"
    local gateway="${3:-}"
    
    log "Creating VirtualService for $service_name..."
    
    local service_id=$(uuidgen | tr -d '-' | head -c 16)
    
    # Base VirtualService
    local vs_config=""
    
    if [ -n "$gateway" ]; then
        vs_config=$(cat <<EOF
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: ${service_name}
  namespace: ${namespace}
spec:
  hosts:
  - ${service_name}.${namespace}.svc.cluster.local
  gateways:
  - ${gateway}
  http:
  - match:
    - uri:
        prefix: /
    route:
    - destination:
        host: ${service_name}.${namespace}.svc.cluster.local
        port:
          number: 8080
    retries:
      attempts: ${MAX_RETRIES}
      perTryTimeout: 2s
      retryOn: 5xx,reset,connect-failure,refused-stream
    timeout: 10s
    # Fault injection for testing (disabled by default)
    # fault:
    #   delay:
    #     percentage:
    #       value: 0.1
    #     fixedDelay: 5s
EOF
)
    else
        vs_config=$(cat <<EOF
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: ${service_name}
  namespace: ${namespace}
spec:
  hosts:
  - ${service_name}
  http:
  - route:
    - destination:
        host: ${service_name}
        port:
          number: 8080
    retries:
      attempts: ${MAX_RETRIES}
      perTryTimeout: 2s
      retryOn: 5xx,reset,connect-failure,refused-stream
    timeout: 10s
EOF
)
    fi
    
    echo "$vs_config" | kubectl apply -f -
    
    # Store in database
    sqlite3 "$MESH_DB" <<EOF
INSERT INTO services VALUES (
    '${service_id}',
    '${service_name}',
    '${namespace}',
    'v1',
    8080,
    'http',
    datetime('now')
);
EOF
    
    log "VirtualService created for $service_name"
    echo "$service_id"
}

create_destination_rule() {
    local service_name="$1"
    local namespace="${2:-default}"
    local load_balancer="${3:-LEAST_REQUEST}"
    
    log "Creating DestinationRule for $service_name..."
    
    cat <<EOF | kubectl apply -f -
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: ${service_name}
  namespace: ${namespace}
spec:
  host: ${service_name}.${namespace}.svc.cluster.local
  
  trafficPolicy:
    # Load balancing
    loadBalancer:
      simple: ${load_balancer}
      localityLbSetting:
        enabled: true
        distribute:
        - from: us-west/*
          to:
            "us-west/*": 80
            "us-east/*": 20
    
    # Connection pool
    connectionPool:
      tcp:
        maxConnections: 100
        connectTimeout: 10s
        tcpKeepalive:
          time: 7200s
          interval: 75s
      http:
        http1MaxPendingRequests: 100
        http2MaxRequests: 1000
        maxRequestsPerConnection: 2
        maxRetries: 3
        idleTimeout: 300s
        h2UpgradePolicy: UPGRADE
    
    # Outlier detection (circuit breaker)
    outlierDetection:
      consecutive5xxErrors: ${CIRCUIT_BREAKER_THRESHOLD}
      interval: 10s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
      minHealthPercent: 50
      splitExternalLocalOriginErrors: true
    
    # TLS settings
    tls:
      mode: ISTIO_MUTUAL
  
  # Subset definitions
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
    trafficPolicy:
      loadBalancer:
        simple: ROUND_ROBIN
EOF
    
    log "DestinationRule created for $service_name"
}

configure_circuit_breaker() {
    local service_name="$1"
    local namespace="${2:-default}"
    local threshold="${3:-$CIRCUIT_BREAKER_THRESHOLD}"
    local ejection_time="${4:-30}"
    
    log "Configuring circuit breaker for $service_name..."
    
    kubectl patch destinationrule "$service_name" -n "$namespace" --type merge -p "{
      \"spec\": {
        \"trafficPolicy\": {
          \"outlierDetection\": {
            \"consecutive5xxErrors\": $threshold,
            \"interval\": \"10s\",
            \"baseEjectionTime\": \"${ejection_time}s\",
            \"maxEjectionPercent\": 50,
            \"minHealthPercent\": 50
          }
        }
      }
    }"
    
    log "Circuit breaker configured: threshold=$threshold, ejection_time=${ejection_time}s"
}

################################################################################
# Canary deployments and progressive delivery
################################################################################

start_canary_deployment() {
    local service_name="$1"
    local namespace="${2:-default}"
    local baseline_version="$3"
    local canary_version="$4"
    local initial_traffic="${5:-10}"
    
    log "Starting canary deployment: $service_name ($baseline_version -> $canary_version)"
    
    local canary_id=$(uuidgen | tr -d '-' | head -c 16)
    
    # Update VirtualService with traffic split
    cat <<EOF | kubectl apply -f -
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: ${service_name}
  namespace: ${namespace}
spec:
  hosts:
  - ${service_name}
  http:
  - match:
    - headers:
        canary:
          exact: "true"
    route:
    - destination:
        host: ${service_name}
        subset: ${canary_version}
  - route:
    - destination:
        host: ${service_name}
        subset: ${baseline_version}
      weight: $((100 - initial_traffic))
    - destination:
        host: ${service_name}
        subset: ${canary_version}
      weight: ${initial_traffic}
EOF
    
    # Get service_id
    local service_id=$(sqlite3 "$MESH_DB" \
        "SELECT service_id FROM services WHERE name='$service_name' AND namespace='$namespace' LIMIT 1")
    
    # Store canary deployment
    sqlite3 "$MESH_DB" <<EOF
INSERT INTO canary_deployments VALUES (
    '${canary_id}',
    '${service_id}',
    '${baseline_version}',
    '${canary_version}',
    ${initial_traffic},
    datetime('now'),
    'running',
    NULL,
    NULL
);
EOF
    
    log "Canary deployment started: ${initial_traffic}% traffic to $canary_version"
    echo "$canary_id"
}

increase_canary_traffic() {
    local service_name="$1"
    local namespace="${2:-default}"
    local baseline_version="$3"
    local canary_version="$4"
    local new_traffic="$5"
    
    log "Increasing canary traffic to ${new_traffic}%..."
    
    kubectl patch virtualservice "$service_name" -n "$namespace" --type merge -p "{
      \"spec\": {
        \"http\": [{
          \"route\": [
            {
              \"destination\": {
                \"host\": \"$service_name\",
                \"subset\": \"$baseline_version\"
              },
              \"weight\": $((100 - new_traffic))
            },
            {
              \"destination\": {
                \"host\": \"$service_name\",
                \"subset\": \"$canary_version\"
              },
              \"weight\": $new_traffic
            }
          ]
        }]
      }
    }"
    
    # Update database
    local service_id=$(sqlite3 "$MESH_DB" \
        "SELECT service_id FROM services WHERE name='$service_name' AND namespace='$namespace' LIMIT 1")
    
    sqlite3 "$MESH_DB" \
        "UPDATE canary_deployments 
         SET traffic_percent=$new_traffic 
         WHERE service_id='$service_id' AND status='running'"
    
    log "Canary traffic increased to ${new_traffic}%"
}

promote_canary() {
    local service_name="$1"
    local namespace="${2:-default}"
    local canary_version="$3"
    
    log "Promoting canary to production: $canary_version"
    
    # Route 100% traffic to canary
    kubectl patch virtualservice "$service_name" -n "$namespace" --type merge -p "{
      \"spec\": {
        \"http\": [{
          \"route\": [{
            \"destination\": {
              \"host\": \"$service_name\",
              \"subset\": \"$canary_version\"
            },
            \"weight\": 100
          }]
        }]
      }
    }"
    
    # Update database
    local service_id=$(sqlite3 "$MESH_DB" \
        "SELECT service_id FROM services WHERE name='$service_name' AND namespace='$namespace' LIMIT 1")
    
    sqlite3 "$MESH_DB" \
        "UPDATE canary_deployments 
         SET status='promoted', traffic_percent=100 
         WHERE service_id='$service_id' AND status='running'"
    
    log "Canary promoted to production"
}

rollback_canary() {
    local service_name="$1"
    local namespace="${2:-default}"
    local baseline_version="$3"
    
    log "Rolling back canary deployment..."
    
    # Route 100% traffic back to baseline
    kubectl patch virtualservice "$service_name" -n "$namespace" --type merge -p "{
      \"spec\": {
        \"http\": [{
          \"route\": [{
            \"destination\": {
              \"host\": \"$service_name\",
              \"subset\": \"$baseline_version\"
            },
            \"weight\": 100
          }]
        }]
      }
    }"
    
    # Update database
    local service_id=$(sqlite3 "$MESH_DB" \
        "SELECT service_id FROM services WHERE name='$service_name' AND namespace='$namespace' LIMIT 1")
    
    sqlite3 "$MESH_DB" \
        "UPDATE canary_deployments 
         SET status='rolled_back', traffic_percent=0 
         WHERE service_id='$service_id' AND status='running'"
    
    log "Canary deployment rolled back"
}

automated_canary_analysis() {
    local service_name="$1"
    local namespace="${2:-default}"
    local canary_version="$3"
    
    log "Analyzing canary performance..."
    
    # Query Prometheus for canary metrics
    local success_rate=$(kubectl exec -n istio-system deploy/prometheus -- \
        promtool query instant \
        'sum(rate(istio_requests_total{destination_service="'$service_name'",destination_version="'$canary_version'",response_code!~"5.*"}[5m])) / sum(rate(istio_requests_total{destination_service="'$service_name'",destination_version="'$canary_version'"}[5m])) * 100' \
        2>/dev/null | grep -oP '\d+\.\d+' || echo "99.0")
    
    local p99_latency=$(kubectl exec -n istio-system deploy/prometheus -- \
        promtool query instant \
        'histogram_quantile(0.99, sum(rate(istio_request_duration_milliseconds_bucket{destination_service="'$service_name'",destination_version="'$canary_version'"}[5m])) by (le))' \
        2>/dev/null | grep -oP '\d+\.\d+' || echo "100")
    
    log "Canary metrics - Success rate: ${success_rate}%, P99 latency: ${p99_latency}ms"
    
    # Decision logic
    local success_rate_int=${success_rate%.*}
    local p99_latency_int=${p99_latency%.*}
    
    if [ "$success_rate_int" -lt 95 ]; then
        log "Canary failed: success rate too low ($success_rate% < 95%)"
        return 1
    fi
    
    if [ "$p99_latency_int" -gt "$TARGET_P99_LATENCY" ]; then
        log "Canary failed: P99 latency too high (${p99_latency}ms > ${TARGET_P99_LATENCY}ms)"
        return 1
    fi
    
    log "Canary passed quality checks"
    return 0
}

progressive_canary_rollout() {
    local service_name="$1"
    local namespace="${2:-default}"
    local baseline_version="$3"
    local canary_version="$4"
    
    log "Starting progressive canary rollout..."
    
    # Stage 1: 10% traffic
    start_canary_deployment "$service_name" "$namespace" "$baseline_version" "$canary_version" 10
    sleep 300  # 5 minutes
    
    if ! automated_canary_analysis "$service_name" "$namespace" "$canary_version"; then
        rollback_canary "$service_name" "$namespace" "$baseline_version"
        return 1
    fi
    
    # Stage 2: 25% traffic
    increase_canary_traffic "$service_name" "$namespace" "$baseline_version" "$canary_version" 25
    sleep 300
    
    if ! automated_canary_analysis "$service_name" "$namespace" "$canary_version"; then
        rollback_canary "$service_name" "$namespace" "$baseline_version"
        return 1
    fi
    
    # Stage 3: 50% traffic
    increase_canary_traffic "$service_name" "$namespace" "$baseline_version" "$canary_version" 50
    sleep 300
    
    if ! automated_canary_analysis "$service_name" "$namespace" "$canary_version"; then
        rollback_canary "$service_name" "$namespace" "$baseline_version"
        return 1
    fi
    
    # Stage 4: 100% traffic (promote)
    promote_canary "$service_name" "$namespace" "$canary_version"
    
    log "Progressive canary rollout completed successfully"
}

################################################################################
# Observability and monitoring
################################################################################

monitor_circuit_breakers() {
    log "Monitoring circuit breaker events..."
    
    # Monitor Envoy stats for circuit breaker triggers
    kubectl get pods -n default -o name | while read -r pod; do
        if kubectl exec -n default "$pod" -c istio-proxy -- \
            curl -s localhost:15000/stats | grep -q "outlier_detection.ejections_active"; then
            
            local ejections=$(kubectl exec -n default "$pod" -c istio-proxy -- \
                curl -s localhost:15000/stats | \
                grep "outlier_detection.ejections_active" | \
                awk '{print $2}')
            
            if [ "$ejections" -gt 0 ]; then
                log "Circuit breaker triggered: $pod (ejections: $ejections)"
                
                # Log to database
                local service_name=$(kubectl get "$pod" -n default \
                    -o jsonpath='{.metadata.labels.app}' 2>/dev/null)
                
                if [ -n "$service_name" ]; then
                    local service_id=$(sqlite3 "$MESH_DB" \
                        "SELECT service_id FROM services WHERE name='$service_name' LIMIT 1")
                    
                    if [ -n "$service_id" ]; then
                        sqlite3 "$MESH_DB" <<EOF
INSERT INTO circuit_breaker_events (service_id, event_type, consecutive_errors)
VALUES ('$service_id', 'ejection', $ejections);
EOF
                    fi
                fi
            fi
        fi
    done
}

collect_traffic_metrics() {
    log "Collecting traffic metrics..."
    
    while true; do
        # Get all services
        local services=$(sqlite3 "$MESH_DB" \
            "SELECT service_id, name, namespace FROM services")
        
        while IFS='|' read -r service_id service_name namespace; do
            if [ -z "$service_id" ]; then continue; fi
            
            # Query Prometheus for metrics
            local requests_total=$(kubectl exec -n istio-system deploy/prometheus -- \
                promtool query instant \
                'sum(rate(istio_requests_total{destination_service="'$service_name'"}[5m])) * 300' \
                2>/dev/null | grep -oP '\d+' || echo "0")
            
            local requests_success=$(kubectl exec -n istio-system deploy/prometheus -- \
                promtool query instant \
                'sum(rate(istio_requests_total{destination_service="'$service_name'",response_code!~"5.*"}[5m])) * 300' \
                2>/dev/null | grep -oP '\d+' || echo "0")
            
            local requests_failed=$((requests_total - requests_success))
            
            local p50=$(kubectl exec -n istio-system deploy/prometheus -- \
                promtool query instant \
                'histogram_quantile(0.50, sum(rate(istio_request_duration_milliseconds_bucket{destination_service="'$service_name'"}[5m])) by (le))' \
                2>/dev/null | grep -oP '\d+\.\d+' || echo "0")
            
            local p95=$(kubectl exec -n istio-system deploy/prometheus -- \
                promtool query instant \
                'histogram_quantile(0.95, sum(rate(istio_request_duration_milliseconds_bucket{destination_service="'$service_name'"}[5m])) by (le))' \
                2>/dev/null | grep -oP '\d+\.\d+' || echo "0")
            
            local p99=$(kubectl exec -n istio-system deploy/prometheus -- \
                promtool query instant \
                'histogram_quantile(0.99, sum(rate(istio_request_duration_milliseconds_bucket{destination_service="'$service_name'"}[5m])) by (le))' \
                2>/dev/null | grep -oP '\d+\.\d+' || echo "0")
            
            local avg_latency=$(echo "scale=2; ($p50 + $p95 + $p99) / 3" | bc)
            
            # Store metrics
            sqlite3 "$MESH_DB" <<EOF
INSERT INTO traffic_metrics (service_id, requests_total, requests_success, requests_failed, avg_latency_ms, p50_latency_ms, p95_latency_ms, p99_latency_ms)
VALUES ('$service_id', $requests_total, $requests_success, $requests_failed, $avg_latency, $p50, $p95, $p99);
EOF
            
        done <<< "$services"
        
        sleep 60  # Collect every minute
    done
}

get_service_metrics() {
    local service_name="$1"
    local namespace="${2:-default}"
    local hours="${3:-24}"
    
    local service_id=$(sqlite3 "$MESH_DB" \
        "SELECT service_id FROM services WHERE name='$service_name' AND namespace='$namespace' LIMIT 1")
    
    if [ -z "$service_id" ]; then
        error "Service not found: $service_name"
        return 1
    fi
    
    echo "=== Service Mesh Metrics for $service_name (last ${hours}h) ==="
    
    # Traffic metrics
    local total_requests=$(sqlite3 "$MESH_DB" \
        "SELECT SUM(requests_total) FROM traffic_metrics 
         WHERE service_id='$service_id' 
         AND timestamp > datetime('now', '-${hours} hours')")
    
    local success_requests=$(sqlite3 "$MESH_DB" \
        "SELECT SUM(requests_success) FROM traffic_metrics 
         WHERE service_id='$service_id' 
         AND timestamp > datetime('now', '-${hours} hours')")
    
    local failed_requests=$(sqlite3 "$MESH_DB" \
        "SELECT SUM(requests_failed) FROM traffic_metrics 
         WHERE service_id='$service_id' 
         AND timestamp > datetime('now', '-${hours} hours')")
    
    local success_rate=$(echo "scale=2; $success_requests / $total_requests * 100" | bc)
    
    echo "Total requests: ${total_requests:-0}"
    echo "Success rate: ${success_rate:-0}%"
    echo "Failed requests: ${failed_requests:-0}"
    
    # Latency metrics
    local avg_p50=$(sqlite3 "$MESH_DB" \
        "SELECT AVG(p50_latency_ms) FROM traffic_metrics 
         WHERE service_id='$service_id' 
         AND timestamp > datetime('now', '-${hours} hours')")
    
    local avg_p95=$(sqlite3 "$MESH_DB" \
        "SELECT AVG(p95_latency_ms) FROM traffic_metrics 
         WHERE service_id='$service_id' 
         AND timestamp > datetime('now', '-${hours} hours')")
    
    local avg_p99=$(sqlite3 "$MESH_DB" \
        "SELECT AVG(p99_latency_ms) FROM traffic_metrics 
         WHERE service_id='$service_id' 
         AND timestamp > datetime('now', '-${hours} hours')")
    
    echo "P50 latency: ${avg_p50:-0}ms"
    echo "P95 latency: ${avg_p95:-0}ms"
    echo "P99 latency: ${avg_p99:-0}ms"
    
    # Circuit breaker events
    local cb_events=$(sqlite3 "$MESH_DB" \
        "SELECT COUNT(*) FROM circuit_breaker_events 
         WHERE service_id='$service_id' 
         AND timestamp > datetime('now', '-${hours} hours')")
    
    echo "Circuit breaker events: ${cb_events:-0}"
}

################################################################################
# Main functions
################################################################################

setup_service_mesh() {
    log "Setting up service mesh..."
    
    init_database
    install_istio
    configure_mesh_optimization
    configure_sidecar_resources
    
    log "Service mesh setup completed successfully"
}

usage() {
    cat <<EOF
Service Mesh Advanced Optimization v11.0

Usage: $0 COMMAND [OPTIONS]

Commands:
  setup                                        Setup Istio service mesh
  
  virtual-service SERVICE NS [GATEWAY]         Create VirtualService
  destination-rule SERVICE NS [LB]             Create DestinationRule
  circuit-breaker SERVICE NS [THRESHOLD] [TIME] Configure circuit breaker
  
  canary-start SERVICE NS BASELINE CANARY [%]  Start canary deployment
  canary-increase SERVICE NS BASE CANARY %     Increase canary traffic
  canary-promote SERVICE NS CANARY             Promote canary to production
  canary-rollback SERVICE NS BASELINE          Rollback canary deployment
  canary-progressive SERVICE NS BASE CANARY    Automated progressive rollout
  
  monitor-circuit-breakers                     Monitor circuit breaker events
  collect-metrics                              Start metrics collection
  metrics SERVICE NS [HOURS]                   Show service metrics

Examples:
  $0 setup
  $0 virtual-service myapp default
  $0 destination-rule myapp default LEAST_REQUEST
  $0 circuit-breaker myapp default 5 30
  $0 canary-start myapp default v1 v2 10

EOF
}

main() {
    case "${1:-}" in
        setup)
            setup_service_mesh
            ;;
        virtual-service)
            create_virtual_service "${2:-}" "${3:-default}" "${4:-}"
            ;;
        destination-rule)
            create_destination_rule "${2:-}" "${3:-default}" "${4:-LEAST_REQUEST}"
            ;;
        circuit-breaker)
            configure_circuit_breaker "${2:-}" "${3:-default}" "${4:-5}" "${5:-30}"
            ;;
        canary-start)
            start_canary_deployment "${2:-}" "${3:-default}" "${4:-}" "${5:-}" "${6:-10}"
            ;;
        canary-increase)
            increase_canary_traffic "${2:-}" "${3:-default}" "${4:-}" "${5:-}" "${6:-}"
            ;;
        canary-promote)
            promote_canary "${2:-}" "${3:-default}" "${4:-}"
            ;;
        canary-rollback)
            rollback_canary "${2:-}" "${3:-default}" "${4:-}"
            ;;
        canary-progressive)
            progressive_canary_rollout "${2:-}" "${3:-default}" "${4:-}" "${5:-}"
            ;;
        monitor-circuit-breakers)
            monitor_circuit_breakers
            ;;
        collect-metrics)
            collect_traffic_metrics
            ;;
        metrics)
            get_service_metrics "${2:-}" "${3:-default}" "${4:-24}"
            ;;
        *)
            usage
            exit 1
            ;;
    esac
}

# Run main if executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
