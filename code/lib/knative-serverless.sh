#!/bin/bash

################################################################################
# Knative Serverless Platform v11.0
# Event-driven serverless with auto-scaling 0-N and <100ms cold start
################################################################################

set -euo pipefail

# Configuration
KNATIVE_VERSION="1.12.0"
KNATIVE_SERVING_VERSION="1.12.0"
KNATIVE_EVENTING_VERSION="1.12.0"
KOURIER_VERSION="1.12.0"

# Directories
KNATIVE_CONFIG_DIR="/etc/knative"
KNATIVE_LOG_DIR="/var/log/knative"
KNATIVE_DB="/var/lib/knative/serverless.db"

# Performance targets
COLD_START_TARGET=100    # milliseconds
SCALE_TO_ZERO_GRACE=30   # seconds
MAX_SCALE=100
MIN_SCALE=0

# Create directories
mkdir -p "$KNATIVE_CONFIG_DIR" "$KNATIVE_LOG_DIR" "$(dirname $KNATIVE_DB)"

# Logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$KNATIVE_LOG_DIR/knative.log"
}

error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $*" | tee -a "$KNATIVE_LOG_DIR/knative.log" >&2
}

################################################################################
# Database initialization
################################################################################

init_database() {
    log "Initializing Knative database..."
    
    sqlite3 "$KNATIVE_DB" <<EOF
CREATE TABLE IF NOT EXISTS services (
    service_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    namespace TEXT NOT NULL,
    image TEXT NOT NULL,
    min_scale INTEGER DEFAULT 0,
    max_scale INTEGER DEFAULT 100,
    target_concurrency INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS revisions (
    revision_id TEXT PRIMARY KEY,
    service_id TEXT NOT NULL,
    revision_name TEXT NOT NULL,
    image TEXT NOT NULL,
    traffic_percent INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ready INTEGER DEFAULT 0,
    FOREIGN KEY(service_id) REFERENCES services(service_id)
);

CREATE TABLE IF NOT EXISTS scaling_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_type TEXT NOT NULL,
    replicas_before INTEGER,
    replicas_after INTEGER,
    reason TEXT,
    cold_start_time_ms INTEGER,
    FOREIGN KEY(service_id) REFERENCES services(service_id)
);

CREATE TABLE IF NOT EXISTS metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    requests_per_second REAL,
    avg_response_time_ms REAL,
    cold_starts INTEGER,
    active_pods INTEGER,
    cpu_usage REAL,
    memory_usage REAL,
    FOREIGN KEY(service_id) REFERENCES services(service_id)
);

CREATE INDEX IF NOT EXISTS idx_service_name ON services(name, namespace);
CREATE INDEX IF NOT EXISTS idx_scaling_timestamp ON scaling_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp);
EOF
    
    log "Database initialized successfully"
}

################################################################################
# Knative installation
################################################################################

install_knative_serving() {
    log "Installing Knative Serving v${KNATIVE_SERVING_VERSION}..."
    
    # Install CRDs
    kubectl apply -f "https://github.com/knative/serving/releases/download/knative-v${KNATIVE_SERVING_VERSION}/serving-crds.yaml"
    
    # Install core components
    kubectl apply -f "https://github.com/knative/serving/releases/download/knative-v${KNATIVE_SERVING_VERSION}/serving-core.yaml"
    
    # Wait for deployment
    kubectl wait --for=condition=Available --timeout=300s \
        -n knative-serving deployment/controller deployment/webhook
    
    log "Knative Serving installed successfully"
}

install_kourier_networking() {
    log "Installing Kourier networking layer v${KOURIER_VERSION}..."
    
    # Install Kourier
    kubectl apply -f "https://github.com/knative/net-kourier/releases/download/knative-v${KOURIER_VERSION}/kourier.yaml"
    
    # Configure Knative to use Kourier
    kubectl patch configmap/config-network \
        --namespace knative-serving \
        --type merge \
        --patch '{"data":{"ingress-class":"kourier.ingress.networking.knative.dev"}}'
    
    # Wait for Kourier
    kubectl wait --for=condition=Available --timeout=300s \
        -n kourier-system deployment/3scale-kourier-gateway
    
    log "Kourier networking installed successfully"
}

install_knative_eventing() {
    log "Installing Knative Eventing v${KNATIVE_EVENTING_VERSION}..."
    
    # Install CRDs
    kubectl apply -f "https://github.com/knative/eventing/releases/download/knative-v${KNATIVE_EVENTING_VERSION}/eventing-crds.yaml"
    
    # Install core components
    kubectl apply -f "https://github.com/knative/eventing/releases/download/knative-v${KNATIVE_EVENTING_VERSION}/eventing-core.yaml"
    
    # Install in-memory channel
    kubectl apply -f "https://github.com/knative/eventing/releases/download/knative-v${KNATIVE_EVENTING_VERSION}/in-memory-channel.yaml"
    
    # Install broker
    kubectl apply -f "https://github.com/knative/eventing/releases/download/knative-v${KNATIVE_EVENTING_VERSION}/mt-channel-broker.yaml"
    
    # Wait for deployment
    kubectl wait --for=condition=Available --timeout=300s \
        -n knative-eventing deployment/eventing-controller deployment/eventing-webhook
    
    log "Knative Eventing installed successfully"
}

configure_autoscaling() {
    log "Configuring advanced autoscaling..."
    
    # Configure autoscaler
    kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: config-autoscaler
  namespace: knative-serving
data:
  # Scale to zero configuration
  enable-scale-to-zero: "true"
  scale-to-zero-grace-period: "${SCALE_TO_ZERO_GRACE}s"
  scale-to-zero-pod-retention-period: "0s"
  
  # Scaling parameters
  max-scale-up-rate: "10.0"
  max-scale-down-rate: "2.0"
  stable-window: "60s"
  panic-window-percentage: "10.0"
  panic-threshold-percentage: "200.0"
  
  # Target metrics
  container-concurrency-target-default: "100"
  container-concurrency-target-percentage: "0.7"
  requests-per-second-target-default: "200"
  
  # Activator
  activator-capacity: "100.0"
  
  # Initial scale
  initial-scale: "1"
  allow-zero-initial-scale: "true"
  
  # Pod autoscaler class
  pod-autoscaler-class: "kpa.autoscaling.knative.dev"
EOF
    
    log "Autoscaling configured successfully"
}

configure_deployment_optimizations() {
    log "Configuring deployment optimizations for fast cold starts..."
    
    # Configure deployment settings
    kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: config-deployment
  namespace: knative-serving
data:
  # Progressive deployment
  progressDeadline: "600s"
  
  # Queue proxy configuration for fast startup
  queue-sidecar-image: "gcr.io/knative-releases/knative.dev/serving/cmd/queue@sha256:latest"
  
  # Concurrency settings
  container-concurrency: "0"
  
  # Liveness and readiness probes
  revision-timeout-seconds: "300"
  
  # Progress deadline
  progress-deadline: "600s"
EOF
    
    # Configure features
    kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: config-features
  namespace: knative-serving
data:
  # Enable Kubernetes pod spec affinity
  kubernetes.podspec-affinity: "enabled"
  
  # Enable Kubernetes pod spec tolerations
  kubernetes.podspec-tolerations: "enabled"
  
  # Enable Kubernetes pod spec topology spread constraints
  kubernetes.podspec-topologyspreadconstraints: "enabled"
  
  # Enable EmptyDir volume
  kubernetes.podspec-volumes-emptydir: "enabled"
  
  # Enable persistent volumes
  kubernetes.podspec-persistent-volume-claim: "enabled"
  
  # Enable init containers
  kubernetes.podspec-init-containers: "enabled"
  
  # Enable security context
  kubernetes.podspec-securitycontext: "enabled"
EOF
    
    log "Deployment optimizations configured"
}

################################################################################
# Service deployment functions
################################################################################

deploy_serverless_service() {
    local service_name="$1"
    local namespace="${2:-default}"
    local image="$3"
    local min_scale="${4:-0}"
    local max_scale="${5:-100}"
    local target_concurrency="${6:-10}"
    
    log "Deploying serverless service: $service_name in namespace $namespace"
    
    local service_id=$(uuidgen | tr -d '-' | head -c 16)
    
    # Create Knative Service
    cat <<EOF | kubectl apply -f -
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: ${service_name}
  namespace: ${namespace}
spec:
  template:
    metadata:
      annotations:
        # Autoscaling
        autoscaling.knative.dev/min-scale: "${min_scale}"
        autoscaling.knative.dev/max-scale: "${max_scale}"
        autoscaling.knative.dev/target: "${target_concurrency}"
        autoscaling.knative.dev/class: "kpa.autoscaling.knative.dev"
        autoscaling.knative.dev/metric: "concurrency"
        
        # Scale to zero
        autoscaling.knative.dev/scale-to-zero-pod-retention-period: "0s"
        
        # Cold start optimization
        autoscaling.knative.dev/initial-scale: "1"
        
        # Traffic management
        serving.knative.dev/visibility: "cluster-local"
    spec:
      # Fast startup timeout
      timeoutSeconds: 300
      
      # Container concurrency
      containerConcurrency: ${target_concurrency}
      
      containers:
      - image: ${image}
        ports:
        - containerPort: 8080
          protocol: TCP
        
        # Resource limits for predictable cold starts
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "1000m"
            memory: "512Mi"
        
        # Fast liveness/readiness probes
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 0
          periodSeconds: 10
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 0
          periodSeconds: 1
          failureThreshold: 3
        
        # Environment variables
        env:
        - name: SERVICE_NAME
          value: "${service_name}"
        - name: NAMESPACE
          value: "${namespace}"
        - name: TARGET_CONCURRENCY
          value: "${target_concurrency}"
EOF
    
    # Store in database
    sqlite3 "$KNATIVE_DB" <<EOF
INSERT OR REPLACE INTO services VALUES (
    '${service_id}',
    '${service_name}',
    '${namespace}',
    '${image}',
    ${min_scale},
    ${max_scale},
    ${target_concurrency},
    datetime('now'),
    datetime('now'),
    'active'
);
EOF
    
    log "Service deployed successfully: $service_name (ID: $service_id)"
    echo "$service_id"
}

create_traffic_split() {
    local service_name="$1"
    local namespace="${2:-default}"
    
    log "Creating traffic split for $service_name..."
    
    # Get revisions
    local revisions=$(kubectl get revisions -n "$namespace" \
        -l serving.knative.dev/service="$service_name" \
        --sort-by=.metadata.creationTimestamp \
        -o jsonpath='{.items[*].metadata.name}')
    
    local revision_array=($revisions)
    local num_revisions=${#revision_array[@]}
    
    if [ $num_revisions -lt 2 ]; then
        log "Only one revision exists, skipping traffic split"
        return
    fi
    
    # Create canary deployment (90% old, 10% new)
    local old_revision="${revision_array[-2]}"
    local new_revision="${revision_array[-1]}"
    
    cat <<EOF | kubectl apply -f -
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: ${service_name}
  namespace: ${namespace}
spec:
  traffic:
  - revisionName: ${old_revision}
    percent: 90
    tag: stable
  - revisionName: ${new_revision}
    percent: 10
    tag: canary
  - latestRevision: true
    percent: 0
    tag: latest
EOF
    
    log "Traffic split created: 90% ${old_revision}, 10% ${new_revision}"
}

promote_canary() {
    local service_name="$1"
    local namespace="${2:-default}"
    
    log "Promoting canary to production for $service_name..."
    
    # Get latest revision
    local latest_revision=$(kubectl get revisions -n "$namespace" \
        -l serving.knative.dev/service="$service_name" \
        --sort-by=.metadata.creationTimestamp \
        -o jsonpath='{.items[-1].metadata.name}')
    
    # Route 100% traffic to latest
    cat <<EOF | kubectl apply -f -
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: ${service_name}
  namespace: ${namespace}
spec:
  traffic:
  - revisionName: ${latest_revision}
    percent: 100
    tag: stable
  - latestRevision: true
    percent: 0
    tag: latest
EOF
    
    log "Canary promoted: 100% traffic to ${latest_revision}"
}

################################################################################
# Event-driven architecture
################################################################################

create_event_source() {
    local source_name="$1"
    local source_type="$2"  # ping, kafka, sqs, etc
    local namespace="${3:-default}"
    
    log "Creating event source: $source_name (type: $source_type)"
    
    case "$source_type" in
        ping)
            # Ping source (cron-like)
            cat <<EOF | kubectl apply -f -
apiVersion: sources.knative.dev/v1
kind: PingSource
metadata:
  name: ${source_name}
  namespace: ${namespace}
spec:
  schedule: "*/1 * * * *"  # Every minute
  contentType: "application/json"
  data: '{"message": "Hello from PingSource"}'
  sink:
    ref:
      apiVersion: serving.knative.dev/v1
      kind: Service
      name: ${source_name}-handler
EOF
            ;;
        
        kafka)
            # Kafka source
            cat <<EOF | kubectl apply -f -
apiVersion: sources.knative.dev/v1beta1
kind: KafkaSource
metadata:
  name: ${source_name}
  namespace: ${namespace}
spec:
  consumerGroup: knative-group
  bootstrapServers:
  - kafka-broker:9092
  topics:
  - events-topic
  sink:
    ref:
      apiVersion: serving.knative.dev/v1
      kind: Service
      name: ${source_name}-handler
EOF
            ;;
        
        container)
            # Container source (custom)
            cat <<EOF | kubectl apply -f -
apiVersion: sources.knative.dev/v1
kind: ContainerSource
metadata:
  name: ${source_name}
  namespace: ${namespace}
spec:
  template:
    spec:
      containers:
      - image: gcr.io/knative-releases/knative.dev/eventing/cmd/heartbeats
        name: heartbeats
        env:
        - name: POD_NAME
          value: "heartbeats"
        - name: POD_NAMESPACE
          value: "${namespace}"
  sink:
    ref:
      apiVersion: serving.knative.dev/v1
      kind: Service
      name: ${source_name}-handler
EOF
            ;;
    esac
    
    log "Event source created: $source_name"
}

create_broker() {
    local broker_name="$1"
    local namespace="${2:-default}"
    
    log "Creating event broker: $broker_name"
    
    cat <<EOF | kubectl apply -f -
apiVersion: eventing.knative.dev/v1
kind: Broker
metadata:
  name: ${broker_name}
  namespace: ${namespace}
spec:
  config:
    apiVersion: v1
    kind: ConfigMap
    name: config-br-default-channel
    namespace: knative-eventing
  delivery:
    deadLetterSink:
      ref:
        apiVersion: serving.knative.dev/v1
        kind: Service
        name: ${broker_name}-dlq
    retry: 3
    backoffPolicy: exponential
    backoffDelay: "PT1S"
EOF
    
    log "Broker created: $broker_name"
}

create_trigger() {
    local trigger_name="$1"
    local broker_name="$2"
    local service_name="$3"
    local event_type="${4:-*}"
    local namespace="${5:-default}"
    
    log "Creating trigger: $trigger_name for broker $broker_name"
    
    cat <<EOF | kubectl apply -f -
apiVersion: eventing.knative.dev/v1
kind: Trigger
metadata:
  name: ${trigger_name}
  namespace: ${namespace}
spec:
  broker: ${broker_name}
  filter:
    attributes:
      type: ${event_type}
  subscriber:
    ref:
      apiVersion: serving.knative.dev/v1
      kind: Service
      name: ${service_name}
EOF
    
    log "Trigger created: $trigger_name"
}

################################################################################
# Monitoring and metrics
################################################################################

monitor_cold_starts() {
    log "Monitoring cold start performance..."
    
    # Watch for pod creation events
    kubectl get events --all-namespaces -w --field-selector reason=Created | \
    while read -r line; do
        if echo "$line" | grep -q "knative"; then
            local timestamp=$(echo "$line" | awk '{print $1}')
            local namespace=$(echo "$line" | awk '{print $2}')
            local pod=$(echo "$line" | awk '{print $4}')
            
            # Extract service name
            local service_name=$(kubectl get pod "$pod" -n "$namespace" \
                -o jsonpath='{.metadata.labels.serving\.knative\.dev/service}' 2>/dev/null)
            
            if [ -n "$service_name" ]; then
                # Measure time until pod is ready
                local start_time=$(date +%s%3N)
                
                kubectl wait --for=condition=Ready pod/"$pod" -n "$namespace" --timeout=30s 2>/dev/null
                
                local end_time=$(date +%s%3N)
                local cold_start_time=$((end_time - start_time))
                
                log "Cold start detected: $service_name - ${cold_start_time}ms"
                
                # Store in database
                local service_id=$(sqlite3 "$KNATIVE_DB" \
                    "SELECT service_id FROM services WHERE name='$service_name' AND namespace='$namespace' LIMIT 1")
                
                if [ -n "$service_id" ]; then
                    sqlite3 "$KNATIVE_DB" <<EOF
INSERT INTO scaling_events (service_id, event_type, replicas_before, replicas_after, reason, cold_start_time_ms)
VALUES ('$service_id', 'scale_up', 0, 1, 'cold_start', $cold_start_time);
EOF
                fi
                
                # Alert if cold start exceeds target
                if [ $cold_start_time -gt $COLD_START_TARGET ]; then
                    error "Cold start time exceeded target: ${cold_start_time}ms > ${COLD_START_TARGET}ms"
                fi
            fi
        fi
    done
}

collect_metrics() {
    log "Collecting service metrics..."
    
    while true; do
        # Get all Knative services
        local services=$(kubectl get ksvc --all-namespaces \
            -o jsonpath='{range .items[*]}{.metadata.namespace}{" "}{.metadata.name}{"\n"}{end}')
        
        while IFS= read -r line; do
            if [ -z "$line" ]; then continue; fi
            
            local namespace=$(echo "$line" | awk '{print $1}')
            local service_name=$(echo "$line" | awk '{print $2}')
            
            # Get service metrics
            local ready_pods=$(kubectl get pods -n "$namespace" \
                -l serving.knative.dev/service="$service_name" \
                --field-selector=status.phase=Running \
                -o json | jq '.items | length')
            
            # Get resource usage
            local cpu_usage=$(kubectl top pods -n "$namespace" \
                -l serving.knative.dev/service="$service_name" 2>/dev/null | \
                awk 'NR>1 {sum+=$2} END {print sum+0}')
            
            local memory_usage=$(kubectl top pods -n "$namespace" \
                -l serving.knative.dev/service="$service_name" 2>/dev/null | \
                awk 'NR>1 {sum+=$3} END {print sum+0}')
            
            # Store metrics
            local service_id=$(sqlite3 "$KNATIVE_DB" \
                "SELECT service_id FROM services WHERE name='$service_name' AND namespace='$namespace' LIMIT 1")
            
            if [ -n "$service_id" ]; then
                sqlite3 "$KNATIVE_DB" <<EOF
INSERT INTO metrics (service_id, active_pods, cpu_usage, memory_usage)
VALUES ('$service_id', $ready_pods, ${cpu_usage:-0}, ${memory_usage:-0});
EOF
            fi
            
        done <<< "$services"
        
        sleep 30
    done
}

get_service_metrics() {
    local service_name="$1"
    local namespace="${2:-default}"
    local hours="${3:-24}"
    
    local service_id=$(sqlite3 "$KNATIVE_DB" \
        "SELECT service_id FROM services WHERE name='$service_name' AND namespace='$namespace' LIMIT 1")
    
    if [ -z "$service_id" ]; then
        error "Service not found: $service_name"
        return 1
    fi
    
    echo "=== Metrics for $service_name (last ${hours}h) ==="
    
    # Scaling events
    local total_cold_starts=$(sqlite3 "$KNATIVE_DB" \
        "SELECT COUNT(*) FROM scaling_events 
         WHERE service_id='$service_id' 
         AND event_type='scale_up' 
         AND timestamp > datetime('now', '-${hours} hours')")
    
    local avg_cold_start=$(sqlite3 "$KNATIVE_DB" \
        "SELECT AVG(cold_start_time_ms) FROM scaling_events 
         WHERE service_id='$service_id' 
         AND event_type='scale_up' 
         AND cold_start_time_ms IS NOT NULL
         AND timestamp > datetime('now', '-${hours} hours')")
    
    echo "Cold starts: $total_cold_starts"
    echo "Avg cold start time: ${avg_cold_start:-0}ms"
    
    # Current status
    local current_pods=$(kubectl get pods -n "$namespace" \
        -l serving.knative.dev/service="$service_name" \
        --field-selector=status.phase=Running \
        -o json | jq '.items | length')
    
    echo "Current pods: $current_pods"
    
    # Resource usage
    local avg_cpu=$(sqlite3 "$KNATIVE_DB" \
        "SELECT AVG(cpu_usage) FROM metrics 
         WHERE service_id='$service_id' 
         AND timestamp > datetime('now', '-${hours} hours')")
    
    local avg_memory=$(sqlite3 "$KNATIVE_DB" \
        "SELECT AVG(memory_usage) FROM metrics 
         WHERE service_id='$service_id' 
         AND timestamp > datetime('now', '-${hours} hours')")
    
    echo "Avg CPU usage: ${avg_cpu:-0}m"
    echo "Avg Memory usage: ${avg_memory:-0}Mi"
}

################################################################################
# Optimization functions
################################################################################

optimize_cold_starts() {
    local service_name="$1"
    local namespace="${2:-default}"
    
    log "Optimizing cold starts for $service_name..."
    
    # Apply optimizations
    kubectl patch ksvc "$service_name" -n "$namespace" --type merge -p '{
      "spec": {
        "template": {
          "metadata": {
            "annotations": {
              "autoscaling.knative.dev/initial-scale": "1",
              "autoscaling.knative.dev/scale-to-zero-pod-retention-period": "10m"
            }
          },
          "spec": {
            "containers": [{
              "readinessProbe": {
                "initialDelaySeconds": 0,
                "periodSeconds": 1,
                "timeoutSeconds": 1
              }
            }]
          }
        }
      }
    }'
    
    log "Cold start optimizations applied"
}

enable_concurrency_limits() {
    local service_name="$1"
    local namespace="${2:-default}"
    local limit="${3:-10}"
    
    log "Setting concurrency limit for $service_name to $limit..."
    
    kubectl patch ksvc "$service_name" -n "$namespace" --type merge -p "{
      \"spec\": {
        \"template\": {
          \"spec\": {
            \"containerConcurrency\": $limit
          }
        }
      }
    }"
    
    log "Concurrency limit set to $limit"
}

################################################################################
# Main functions
################################################################################

install_knative() {
    log "Starting Knative installation..."
    
    init_database
    install_knative_serving
    install_kourier_networking
    install_knative_eventing
    configure_autoscaling
    configure_deployment_optimizations
    
    log "Knative installation completed successfully"
}

usage() {
    cat <<EOF
Knative Serverless Platform v11.0

Usage: $0 COMMAND [OPTIONS]

Commands:
  install                          Install Knative platform
  deploy SERVICE NAMESPACE IMAGE   Deploy serverless service
  split SERVICE NAMESPACE          Create traffic split (canary)
  promote SERVICE NAMESPACE        Promote canary to production
  
  event-source NAME TYPE NS        Create event source
  broker NAME NAMESPACE            Create event broker
  trigger NAME BROKER SERVICE NS   Create event trigger
  
  metrics SERVICE NAMESPACE        Show service metrics
  monitor-cold-starts              Monitor cold start performance
  collect-metrics                  Start metrics collection
  
  optimize SERVICE NAMESPACE       Optimize cold starts
  set-concurrency SERVICE NS LIMIT Set concurrency limit

Examples:
  $0 install
  $0 deploy hello-service default gcr.io/my-project/hello:latest
  $0 split hello-service default
  $0 event-source heartbeat ping default
  $0 metrics hello-service default

EOF
}

main() {
    case "${1:-}" in
        install)
            install_knative
            ;;
        deploy)
            deploy_serverless_service "${2:-}" "${3:-default}" "${4:-}" "${5:-0}" "${6:-100}" "${7:-10}"
            ;;
        split)
            create_traffic_split "${2:-}" "${3:-default}"
            ;;
        promote)
            promote_canary "${2:-}" "${3:-default}"
            ;;
        event-source)
            create_event_source "${2:-}" "${3:-}" "${4:-default}"
            ;;
        broker)
            create_broker "${2:-}" "${3:-default}"
            ;;
        trigger)
            create_trigger "${2:-}" "${3:-}" "${4:-}" "${5:-*}" "${6:-default}"
            ;;
        metrics)
            get_service_metrics "${2:-}" "${3:-default}" "${4:-24}"
            ;;
        monitor-cold-starts)
            monitor_cold_starts
            ;;
        collect-metrics)
            collect_metrics
            ;;
        optimize)
            optimize_cold_starts "${2:-}" "${3:-default}"
            ;;
        set-concurrency)
            enable_concurrency_limits "${2:-}" "${3:-default}" "${4:-10}"
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
