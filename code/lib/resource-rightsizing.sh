#!/bin/bash
#
# Resource Right-Sizing System v11.0
# Automatic optimization of K8s resource requests/limits
#

set -euo pipefail

# Configuration
DB_PATH="/var/lib/rightsizing/recommendations.db"
PROMETHEUS_URL="${PROMETHEUS_URL:-http://prometheus.monitoring.svc.cluster.local:9090}"
ANALYSIS_DAYS="${ANALYSIS_DAYS:-30}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }

init_database() {
    log_info "Initializing right-sizing database..."
    
    mkdir -p "$(dirname "$DB_PATH")"
    
    sqlite3 "$DB_PATH" <<EOF
CREATE TABLE IF NOT EXISTS resource_usage (
    usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
    namespace TEXT NOT NULL,
    pod_name TEXT NOT NULL,
    container_name TEXT NOT NULL,
    cpu_usage_avg REAL,
    cpu_usage_p95 REAL,
    memory_usage_avg REAL,
    memory_usage_p95 REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS current_resources (
    resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
    namespace TEXT NOT NULL,
    deployment_name TEXT NOT NULL,
    container_name TEXT NOT NULL,
    cpu_request TEXT,
    cpu_limit TEXT,
    memory_request TEXT,
    memory_limit TEXT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recommendations (
    recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    namespace TEXT NOT NULL,
    deployment_name TEXT NOT NULL,
    container_name TEXT NOT NULL,
    current_cpu_request TEXT,
    recommended_cpu_request TEXT,
    current_memory_request TEXT,
    recommended_memory_request TEXT,
    potential_savings REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    applied BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_usage_pod ON resource_usage(pod_name, timestamp);
CREATE INDEX IF NOT EXISTS idx_recommendations_deployment ON recommendations(deployment_name);
EOF
    
    log_info "Database initialized: $DB_PATH"
}

collect_current_resources() {
    local namespace="${1:-default}"
    
    log_info "Collecting current resource settings for namespace: $namespace"
    
    kubectl get deployments -n "$namespace" -o json | jq -r '
        .items[] | 
        .metadata.name as $deployment |
        .spec.template.spec.containers[] |
        {
            deployment: $deployment,
            container: .name,
            cpu_request: .resources.requests.cpu // "N/A",
            cpu_limit: .resources.limits.cpu // "N/A",
            memory_request: .resources.requests.memory // "N/A",
            memory_limit: .resources.limits.memory // "N/A"
        } | 
        @json
    ' | while read -r resource_json; do
        local deployment container cpu_req cpu_lim mem_req mem_lim
        
        deployment=$(echo "$resource_json" | jq -r '.deployment')
        container=$(echo "$resource_json" | jq -r '.container')
        cpu_req=$(echo "$resource_json" | jq -r '.cpu_request')
        cpu_lim=$(echo "$resource_json" | jq -r '.cpu_limit')
        mem_req=$(echo "$resource_json" | jq -r '.memory_request')
        mem_lim=$(echo "$resource_json" | jq -r '.memory_limit')
        
        sqlite3 "$DB_PATH" <<EOF
INSERT INTO current_resources (namespace, deployment_name, container_name, cpu_request, cpu_limit, memory_request, memory_limit)
VALUES ('$namespace', '$deployment', '$container', '$cpu_req', '$cpu_lim', '$mem_req', '$mem_lim');
EOF
    done
    
    log_info "Current resources recorded"
}

collect_usage_metrics() {
    local namespace="${1:-default}"
    local days="${2:-$ANALYSIS_DAYS}"
    
    log_info "Collecting usage metrics (last $days days)..."
    
    # Get pods in namespace
    kubectl get pods -n "$namespace" -o json | jq -r '.items[].metadata.name' | while read -r pod_name; do
        
        # Query Prometheus for CPU usage (average)
        local cpu_avg_query="avg_over_time(rate(container_cpu_usage_seconds_total{namespace=\"$namespace\",pod=\"$pod_name\"}[5m])[$days"d"])"
        local cpu_avg
        cpu_avg=$(curl -s "$PROMETHEUS_URL/api/v1/query?query=$cpu_avg_query" | jq -r '.data.result[0].value[1] // "0"')
        
        # Query for CPU P95
        local cpu_p95_query="quantile_over_time(0.95, rate(container_cpu_usage_seconds_total{namespace=\"$namespace\",pod=\"$pod_name\"}[5m])[$days"d"])"
        local cpu_p95
        cpu_p95=$(curl -s "$PROMETHEUS_URL/api/v1/query?query=$cpu_p95_query" | jq -r '.data.result[0].value[1] // "0"')
        
        # Query for Memory usage (average)
        local mem_avg_query="avg_over_time(container_memory_working_set_bytes{namespace=\"$namespace\",pod=\"$pod_name\"}[$days"d"])"
        local mem_avg
        mem_avg=$(curl -s "$PROMETHEUS_URL/api/v1/query?query=$mem_avg_query" | jq -r '.data.result[0].value[1] // "0"')
        
        # Query for Memory P95
        local mem_p95_query="quantile_over_time(0.95, container_memory_working_set_bytes{namespace=\"$namespace\",pod=\"$pod_name\"}[$days"d"])"
        local mem_p95
        mem_p95=$(curl -s "$PROMETHEUS_URL/api/v1/query?query=$mem_p95_query" | jq -r '.data.result[0].value[1] // "0"')
        
        # Convert memory to MB
        mem_avg_mb=$(echo "$mem_avg / 1024 / 1024" | bc)
        mem_p95_mb=$(echo "$mem_p95 / 1024 / 1024" | bc)
        
        # Store in database
        sqlite3 "$DB_PATH" <<EOF
INSERT INTO resource_usage (namespace, pod_name, container_name, cpu_usage_avg, cpu_usage_p95, memory_usage_avg, memory_usage_p95)
VALUES ('$namespace', '$pod_name', 'main', $cpu_avg, $cpu_p95, $mem_avg_mb, $mem_p95_mb);
EOF
        
        log_info "  Collected: $pod_name - CPU: ${cpu_avg} avg, ${cpu_p95} p95 | Memory: ${mem_avg_mb}MB avg, ${mem_p95_mb}MB p95"
    done
    
    log_info "Usage metrics collected"
}

generate_recommendations() {
    local namespace="${1:-default}"
    
    log_info "Generating right-sizing recommendations..."
    
    # Get deployments
    kubectl get deployments -n "$namespace" -o json | jq -r '.items[].metadata.name' | while read -r deployment; do
        
        # Get pods for deployment
        local pods
        pods=$(kubectl get pods -n "$namespace" -l "app=$deployment" -o jsonpath='{.items[*].metadata.name}')
        
        if [[ -z "$pods" ]]; then
            continue
        fi
        
        # Calculate average usage across all pods
        local total_cpu_avg=0 total_cpu_p95=0 total_mem_avg=0 total_mem_p95=0 pod_count=0
        
        for pod in $pods; do
            read -r cpu_avg cpu_p95 mem_avg mem_p95 <<< $(sqlite3 "$DB_PATH" <<EOF
SELECT AVG(cpu_usage_avg), AVG(cpu_usage_p95), AVG(memory_usage_avg), AVG(memory_usage_p95)
FROM resource_usage
WHERE pod_name = '$pod';
EOF
)
            
            if [[ -n "$cpu_avg" && "$cpu_avg" != "0" ]]; then
                total_cpu_avg=$(echo "$total_cpu_avg + $cpu_avg" | bc)
                total_cpu_p95=$(echo "$total_cpu_p95 + $cpu_p95" | bc)
                total_mem_avg=$(echo "$total_mem_avg + $mem_avg" | bc)
                total_mem_p95=$(echo "$total_mem_p95 + $mem_p95" | bc)
                ((pod_count++))
            fi
        done
        
        if [[ $pod_count -eq 0 ]]; then
            continue
        fi
        
        # Calculate averages
        local avg_cpu=$(echo "scale=3; $total_cpu_avg / $pod_count" | bc)
        local p95_cpu=$(echo "scale=3; $total_cpu_p95 / $pod_count" | bc)
        local avg_mem=$(echo "scale=0; $total_mem_avg / $pod_count" | bc)
        local p95_mem=$(echo "scale=0; $total_mem_p95 / $pod_count" | bc)
        
        # Recommended resources (P95 + 20% buffer)
        local recommended_cpu=$(echo "scale=3; $p95_cpu * 1.2" | bc)
        local recommended_mem=$(echo "scale=0; $p95_mem * 1.2" | bc)
        
        # Get current resources
        read -r current_cpu current_mem <<< $(sqlite3 "$DB_PATH" <<EOF
SELECT cpu_request, memory_request
FROM current_resources
WHERE deployment_name = '$deployment'
LIMIT 1;
EOF
)
        
        # Convert current to millicores/MB for comparison
        local current_cpu_cores=$(echo "$current_cpu" | sed 's/m$//' | awk '{print $1/1000}')
        local current_mem_mb=$(echo "$current_mem" | sed 's/Mi$//')
        
        # Calculate potential savings (simplified: $0.04/core/hour, $0.005/GB/hour)
        local cpu_diff=$(echo "$current_cpu_cores - $recommended_cpu" | bc)
        local mem_diff=$(echo "($current_mem_mb - $recommended_mem) / 1024" | bc)
        
        local cpu_savings=$(echo "$cpu_diff * 0.04 * 730" | bc)
        local mem_savings=$(echo "$mem_diff * 0.005 * 730" | bc)
        local total_savings=$(echo "$cpu_savings + $mem_savings" | bc)
        
        # Store recommendation
        sqlite3 "$DB_PATH" <<EOF
INSERT INTO recommendations 
(namespace, deployment_name, container_name, current_cpu_request, recommended_cpu_request, 
 current_memory_request, recommended_memory_request, potential_savings)
VALUES ('$namespace', '$deployment', 'main', '$current_cpu', '${recommended_cpu}', 
        '$current_mem', '${recommended_mem}Mi', $total_savings);
EOF
        
        log_info "  $deployment: CPU $current_cpu → ${recommended_cpu} | Memory $current_mem → ${recommended_mem}Mi | Savings: \$${total_savings}/month"
    done
    
    log_info "Recommendations generated"
}

apply_recommendations() {
    local namespace="${1:-default}"
    local deployment="${2:-}"
    
    if [[ -z "$deployment" ]]; then
        log_warn "Apply to all deployments in $namespace? (y/n)"
        read -r confirm
        if [[ "$confirm" != "y" ]]; then
            log_info "Cancelled"
            return
        fi
    fi
    
    log_info "Applying recommendations..."
    
    sqlite3 "$DB_PATH" "SELECT deployment_name, recommended_cpu_request, recommended_memory_request FROM recommendations WHERE namespace='$namespace' AND applied=FALSE" | \
    while IFS='|' read -r dep cpu mem; do
        
        if [[ -n "$deployment" && "$dep" != "$deployment" ]]; then
            continue
        fi
        
        log_info "  Updating $dep..."
        
        kubectl patch deployment "$dep" -n "$namespace" --type='json' -p="[
            {\"op\": \"replace\", \"path\": \"/spec/template/spec/containers/0/resources/requests/cpu\", \"value\": \"$cpu\"},
            {\"op\": \"replace\", \"path\": \"/spec/template/spec/containers/0/resources/requests/memory\", \"value\": \"$mem\"}
        ]"
        
        # Mark as applied
        sqlite3 "$DB_PATH" "UPDATE recommendations SET applied=TRUE WHERE deployment_name='$dep' AND namespace='$namespace'"
    done
    
    log_info "Recommendations applied"
}

generate_report() {
    local namespace="${1:-default}"
    
    echo "=== Right-Sizing Report for $namespace ==="
    echo ""
    
    echo "Current Resources:"
    sqlite3 -header -column "$DB_PATH" <<EOF
SELECT deployment_name, container_name, cpu_request, memory_request
FROM current_resources
WHERE namespace = '$namespace'
ORDER BY deployment_name;
EOF
    
    echo ""
    echo "Recommendations:"
    sqlite3 -header -column "$DB_PATH" <<EOF
SELECT 
    deployment_name,
    current_cpu_request || ' → ' || recommended_cpu_request as cpu_change,
    current_memory_request || ' → ' || recommended_memory_request as memory_change,
    '$' || printf('%.2f', potential_savings) || '/mo' as savings
FROM recommendations
WHERE namespace = '$namespace'
ORDER BY potential_savings DESC;
EOF
    
    echo ""
    echo "Total Potential Savings:"
    sqlite3 "$DB_PATH" <<EOF
SELECT '$' || printf('%.2f', SUM(potential_savings)) || '/month'
FROM recommendations
WHERE namespace = '$namespace';
EOF
}

main() {
    case "${1:-}" in
        init)
            init_database
            ;;
        collect)
            collect_current_resources "${2:-default}"
            collect_usage_metrics "${2:-default}" "${3:-30}"
            ;;
        recommend)
            generate_recommendations "${2:-default}"
            ;;
        apply)
            apply_recommendations "${2:-default}" "${3:-}"
            ;;
        report)
            generate_report "${2:-default}"
            ;;
        *)
            echo "Resource Right-Sizing System v11.0"
            echo ""
            echo "Usage: $0 <command> [options]"
            echo ""
            echo "Commands:"
            echo "  init                     Initialize database"
            echo "  collect NAMESPACE [DAYS] Collect current resources and usage"
            echo "  recommend NAMESPACE      Generate recommendations"
            echo "  apply NAMESPACE [DEPLOY] Apply recommendations"
            echo "  report NAMESPACE         Generate report"
            ;;
    esac
}

main "$@"
