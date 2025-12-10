#!/bin/bash
#
# Distributed Profiling System v11.0
# Continuous CPU/memory profiling with flame graphs
#

set -euo pipefail

# Configuration
PROFILING_NAMESPACE="${PROFILING_NAMESPACE:-profiling}"
DB_PATH="/var/lib/profiling/profiles.db"
STORAGE_PATH="/var/lib/profiling/data"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

init_database() {
    log_info "Initializing profiling database..."
    
    mkdir -p "$(dirname "$DB_PATH")"
    mkdir -p "$STORAGE_PATH"
    
    sqlite3 "$DB_PATH" <<EOF
CREATE TABLE IF NOT EXISTS profiling_sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name TEXT NOT NULL,
    pod_name TEXT NOT NULL,
    profile_type TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    duration_seconds INTEGER,
    file_path TEXT,
    flamegraph_path TEXT
);

CREATE TABLE IF NOT EXISTS performance_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cpu_usage REAL,
    memory_mb REAL,
    goroutines INTEGER,
    heap_alloc_mb REAL,
    FOREIGN KEY(session_id) REFERENCES profiling_sessions(session_id)
);

CREATE TABLE IF NOT EXISTS regression_alerts (
    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name TEXT NOT NULL,
    regression_type TEXT NOT NULL,
    baseline_value REAL,
    current_value REAL,
    degradation_percent REAL,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_sessions_service ON profiling_sessions(service_name);
CREATE INDEX IF NOT EXISTS idx_metrics_session ON performance_metrics(session_id);
CREATE INDEX IF NOT EXISTS idx_alerts_service ON regression_alerts(service_name);
EOF
    
    log_info "Database initialized: $DB_PATH"
}

install_profiling_tools() {
    log_info "Installing continuous profiling infrastructure..."
    
    # Create namespace
    kubectl create namespace "$PROFILING_NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    
    # Install Pyroscope for continuous profiling
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: pyroscope-config
  namespace: $PROFILING_NAMESPACE
data:
  config.yaml: |
    log-level: info
    storage-path: /var/lib/pyroscope
    retention: 168h
    server:
      http-listen-port: 4040
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pyroscope
  namespace: $PROFILING_NAMESPACE
spec:
  replicas: 1
  selector:
    matchLabels:
      app: pyroscope
  template:
    metadata:
      labels:
        app: pyroscope
    spec:
      containers:
      - name: pyroscope
        image: grafana/pyroscope:1.1.5
        args:
        - server
        - -config.file=/etc/pyroscope/config.yaml
        ports:
        - containerPort: 4040
          name: http
        volumeMounts:
        - name: config
          mountPath: /etc/pyroscope
        - name: storage
          mountPath: /var/lib/pyroscope
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 2000m
            memory: 2Gi
      volumes:
      - name: config
        configMap:
          name: pyroscope-config
      - name: storage
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: pyroscope
  namespace: $PROFILING_NAMESPACE
spec:
  selector:
    app: pyroscope
  ports:
  - port: 4040
    targetPort: 4040
    name: http
EOF
    
    # Wait for deployment
    kubectl wait --for=condition=available --timeout=300s deployment/pyroscope -n "$PROFILING_NAMESPACE"
    
    log_info "Pyroscope installed successfully"
}

configure_application_profiling() {
    local service_name="$1"
    local namespace="${2:-default}"
    local language="${3:-go}"
    
    log_info "Configuring profiling for $service_name ($language)..."
    
    case "$language" in
        go)
            # Add Pyroscope sidecar for Go applications
            cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: ${service_name}-profiling
  namespace: $namespace
data:
  profiling.sh: |
    #!/bin/bash
    # Enable Go pprof
    export PYROSCOPE_SERVER_ADDRESS=http://pyroscope.$PROFILING_NAMESPACE.svc.cluster.local:4040
    export PYROSCOPE_APPLICATION_NAME=$service_name
    export PYROSCOPE_PROFILE_CPU=true
    export PYROSCOPE_PROFILE_MEM=true
    export PYROSCOPE_PROFILE_GOROUTINES=true
    exec "\$@"
EOF
            ;;
        
        python)
            # Python profiling configuration
            cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: ${service_name}-profiling
  namespace: $namespace
data:
  profiling.py: |
    import pyroscope
    pyroscope.configure(
        application_name="$service_name",
        server_address="http://pyroscope.$PROFILING_NAMESPACE.svc.cluster.local:4040",
        detect_subprocesses=True,
        oncpu=True,
        native=True
    )
EOF
            ;;
    esac
    
    log_info "Profiling configured for $service_name"
}

start_cpu_profiling() {
    local service_name="$1"
    local duration="${2:-60}"
    local namespace="${3:-default}"
    
    log_info "Starting CPU profiling for $service_name (${duration}s)..."
    
    # Get pod
    local pod_name
    pod_name=$(kubectl get pods -n "$namespace" -l "app=$service_name" -o jsonpath='{.items[0].metadata.name}')
    
    if [[ -z "$pod_name" ]]; then
        log_error "No pods found for service $service_name"
        return 1
    fi
    
    # Start profiling session
    local session_id
    session_id=$(sqlite3 "$DB_PATH" <<EOF
INSERT INTO profiling_sessions (service_name, pod_name, profile_type, duration_seconds)
VALUES ('$service_name', '$pod_name', 'cpu', $duration);
SELECT last_insert_rowid();
EOF
)
    
    # Capture CPU profile
    local profile_file="$STORAGE_PATH/cpu-${service_name}-${session_id}.prof"
    
    kubectl exec -n "$namespace" "$pod_name" -- bash -c "curl -s http://localhost:6060/debug/pprof/profile?seconds=$duration" > "$profile_file"
    
    # Generate flame graph
    local flamegraph_file="$STORAGE_PATH/cpu-${service_name}-${session_id}.svg"
    go tool pprof -svg -output="$flamegraph_file" "$profile_file" 2>/dev/null || true
    
    # Update session
    sqlite3 "$DB_PATH" <<EOF
UPDATE profiling_sessions
SET ended_at = CURRENT_TIMESTAMP,
    file_path = '$profile_file',
    flamegraph_path = '$flamegraph_file'
WHERE session_id = $session_id;
EOF
    
    log_info "CPU profiling complete: $flamegraph_file"
    echo "$session_id"
}

start_memory_profiling() {
    local service_name="$1"
    local namespace="${2:-default}"
    
    log_info "Starting memory profiling for $service_name..."
    
    local pod_name
    pod_name=$(kubectl get pods -n "$namespace" -l "app=$service_name" -o jsonpath='{.items[0].metadata.name}')
    
    if [[ -z "$pod_name" ]]; then
        log_error "No pods found for service $service_name"
        return 1
    fi
    
    local session_id
    session_id=$(sqlite3 "$DB_PATH" <<EOF
INSERT INTO profiling_sessions (service_name, pod_name, profile_type)
VALUES ('$service_name', '$pod_name', 'memory');
SELECT last_insert_rowid();
EOF
)
    
    local profile_file="$STORAGE_PATH/mem-${service_name}-${session_id}.prof"
    kubectl exec -n "$namespace" "$pod_name" -- bash -c "curl -s http://localhost:6060/debug/pprof/heap" > "$profile_file"
    
    local flamegraph_file="$STORAGE_PATH/mem-${service_name}-${session_id}.svg"
    go tool pprof -svg -output="$flamegraph_file" "$profile_file" 2>/dev/null || true
    
    sqlite3 "$DB_PATH" <<EOF
UPDATE profiling_sessions
SET ended_at = CURRENT_TIMESTAMP,
    file_path = '$profile_file',
    flamegraph_path = '$flamegraph_file'
WHERE session_id = $session_id;
EOF
    
    log_info "Memory profiling complete: $flamegraph_file"
    echo "$session_id"
}

continuous_profiling() {
    local service_name="$1"
    local interval="${2:-300}"
    local namespace="${3:-default}"
    
    log_info "Starting continuous profiling for $service_name (interval: ${interval}s)..."
    
    while true; do
        # CPU profiling
        start_cpu_profiling "$service_name" 30 "$namespace" >/dev/null
        
        # Memory snapshot
        start_memory_profiling "$service_name" "$namespace" >/dev/null
        
        # Collect metrics
        collect_performance_metrics "$service_name" "$namespace"
        
        # Check for regressions
        detect_performance_regression "$service_name"
        
        sleep "$interval"
    done
}

collect_performance_metrics() {
    local service_name="$1"
    local namespace="${2:-default}"
    
    # Query Prometheus for metrics
    local prom_url="http://prometheus.monitoring.svc.cluster.local:9090"
    
    # CPU usage
    local cpu_usage
    cpu_usage=$(curl -s "$prom_url/api/v1/query?query=rate(container_cpu_usage_seconds_total{pod=~\"${service_name}-.*\"}[5m])" | jq -r '.data.result[0].value[1] // "0"')
    
    # Memory usage
    local memory_mb
    memory_mb=$(curl -s "$prom_url/api/v1/query?query=container_memory_working_set_bytes{pod=~\"${service_name}-.*\"}/1024/1024" | jq -r '.data.result[0].value[1] // "0"')
    
    # Get latest session
    local session_id
    session_id=$(sqlite3 "$DB_PATH" "SELECT session_id FROM profiling_sessions WHERE service_name='$service_name' ORDER BY session_id DESC LIMIT 1")
    
    if [[ -n "$session_id" ]]; then
        sqlite3 "$DB_PATH" <<EOF
INSERT INTO performance_metrics (session_id, cpu_usage, memory_mb)
VALUES ($session_id, $cpu_usage, $memory_mb);
EOF
    fi
}

detect_performance_regression() {
    local service_name="$1"
    
    # Get baseline metrics (average of last week)
    local baseline_cpu baseline_memory
    read -r baseline_cpu baseline_memory <<< $(sqlite3 "$DB_PATH" <<EOF
SELECT AVG(pm.cpu_usage), AVG(pm.memory_mb)
FROM performance_metrics pm
JOIN profiling_sessions ps ON pm.session_id = ps.session_id
WHERE ps.service_name = '$service_name'
  AND pm.timestamp > datetime('now', '-7 days')
  AND pm.timestamp < datetime('now', '-1 day');
EOF
)
    
    if [[ -z "$baseline_cpu" || "$baseline_cpu" == "0" ]]; then
        return 0
    fi
    
    # Get current metrics (last hour)
    local current_cpu current_memory
    read -r current_cpu current_memory <<< $(sqlite3 "$DB_PATH" <<EOF
SELECT AVG(pm.cpu_usage), AVG(pm.memory_mb)
FROM performance_metrics pm
JOIN profiling_sessions ps ON pm.session_id = ps.session_id
WHERE ps.service_name = '$service_name'
  AND pm.timestamp > datetime('now', '-1 hour');
EOF
)
    
    # Calculate degradation
    local cpu_degradation
    cpu_degradation=$(awk "BEGIN {print (($current_cpu - $baseline_cpu) / $baseline_cpu) * 100}")
    
    local memory_degradation
    memory_degradation=$(awk "BEGIN {print (($current_memory - $baseline_memory) / $baseline_memory) * 100}")
    
    # Alert on significant degradation
    if (( $(echo "$cpu_degradation > 20" | bc -l) )); then
        log_warn "CPU regression detected: ${cpu_degradation}% increase"
        
        sqlite3 "$DB_PATH" <<EOF
INSERT INTO regression_alerts (service_name, regression_type, baseline_value, current_value, degradation_percent)
VALUES ('$service_name', 'cpu', $baseline_cpu, $current_cpu, $cpu_degradation);
EOF
    fi
    
    if (( $(echo "$memory_degradation > 30" | bc -l) )); then
        log_warn "Memory regression detected: ${memory_degradation}% increase"
        
        sqlite3 "$DB_PATH" <<EOF
INSERT INTO regression_alerts (service_name, regression_type, baseline_value, current_value, degradation_percent)
VALUES ('$service_name', 'memory', $baseline_memory, $current_memory, $memory_degradation);
EOF
    fi
}

compare_profiles() {
    local service_name="$1"
    local session_id1="$2"
    local session_id2="$3"
    
    log_info "Comparing profiles: $session_id1 vs $session_id2"
    
    # Get profile files
    local file1 file2
    file1=$(sqlite3 "$DB_PATH" "SELECT file_path FROM profiling_sessions WHERE session_id=$session_id1")
    file2=$(sqlite3 "$DB_PATH" "SELECT file_path FROM profiling_sessions WHERE session_id=$session_id2")
    
    if [[ ! -f "$file1" ]] || [[ ! -f "$file2" ]]; then
        log_error "Profile files not found"
        return 1
    fi
    
    # Generate diff
    local diff_file="$STORAGE_PATH/diff-${session_id1}-${session_id2}.svg"
    go tool pprof -svg -base="$file1" -output="$diff_file" "$file2" 2>/dev/null || true
    
    log_info "Profile comparison saved: $diff_file"
}

get_profiling_report() {
    local service_name="$1"
    local hours="${2:-24}"
    
    log_info "Generating profiling report for $service_name (last ${hours}h)..."
    
    echo "=== Profiling Sessions ==="
    sqlite3 -header -column "$DB_PATH" <<EOF
SELECT session_id, profile_type, started_at, duration_seconds
FROM profiling_sessions
WHERE service_name = '$service_name'
  AND started_at > datetime('now', '-$hours hours')
ORDER BY started_at DESC
LIMIT 10;
EOF
    
    echo ""
    echo "=== Performance Metrics ==="
    sqlite3 -header -column "$DB_PATH" <<EOF
SELECT 
    AVG(cpu_usage) as avg_cpu,
    MAX(cpu_usage) as max_cpu,
    AVG(memory_mb) as avg_memory_mb,
    MAX(memory_mb) as max_memory_mb
FROM performance_metrics pm
JOIN profiling_sessions ps ON pm.session_id = ps.session_id
WHERE ps.service_name = '$service_name'
  AND pm.timestamp > datetime('now', '-$hours hours');
EOF
    
    echo ""
    echo "=== Recent Regressions ==="
    sqlite3 -header -column "$DB_PATH" <<EOF
SELECT regression_type, degradation_percent || '%' as degradation, detected_at
FROM regression_alerts
WHERE service_name = '$service_name'
  AND detected_at > datetime('now', '-$hours hours')
ORDER BY detected_at DESC;
EOF
}

main() {
    case "${1:-}" in
        init)
            init_database
            ;;
        install)
            install_profiling_tools
            ;;
        configure)
            configure_application_profiling "${2:-}" "${3:-default}" "${4:-go}"
            ;;
        cpu)
            start_cpu_profiling "${2:-}" "${3:-60}" "${4:-default}"
            ;;
        memory)
            start_memory_profiling "${2:-}" "${3:-default}"
            ;;
        continuous)
            continuous_profiling "${2:-}" "${3:-300}" "${4:-default}"
            ;;
        compare)
            compare_profiles "${2:-}" "${3:-}" "${4:-}"
            ;;
        report)
            get_profiling_report "${2:-}" "${3:-24}"
            ;;
        *)
            echo "Distributed Profiling System v11.0"
            echo ""
            echo "Usage: $0 <command> [options]"
            echo ""
            echo "Commands:"
            echo "  init                              Initialize database"
            echo "  install                           Install Pyroscope"
            echo "  configure SERVICE [NS] [LANG]     Configure profiling"
            echo "  cpu SERVICE [DURATION] [NS]       CPU profile"
            echo "  memory SERVICE [NS]               Memory profile"
            echo "  continuous SERVICE [INTERVAL] [NS] Continuous profiling"
            echo "  compare SERVICE SESSION1 SESSION2  Compare profiles"
            echo "  report SERVICE [HOURS]            Generate report"
            ;;
    esac
}

main "$@"
