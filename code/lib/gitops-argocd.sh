#!/bin/bash

################################################################################
# GitOps with ArgoCD Integration v11.0
# Declarative deployments, auto-sync, drift detection, multi-cluster management
################################################################################

set -euo pipefail

# Configuration
ARGOCD_VERSION="2.9.3"
ARGOCD_NAMESPACE="argocd"
ARGOCD_SERVER_ADDR=""
ARGOCD_ADMIN_PASSWORD=""

# Directories
ARGOCD_CONFIG_DIR="/etc/argocd"
ARGOCD_LOG_DIR="/var/log/argocd"
ARGOCD_DB="/var/lib/argocd/gitops.db"
MANIFESTS_REPO="/var/lib/argocd/manifests"

# GitOps configuration
GIT_REPO_URL=""
GIT_BRANCH="main"
GIT_PATH="k8s"
SYNC_POLICY="automated"
PRUNE_ENABLED=true
SELF_HEAL_ENABLED=true

# Create directories
mkdir -p "$ARGOCD_CONFIG_DIR" "$ARGOCD_LOG_DIR" "$(dirname $ARGOCD_DB)" "$MANIFESTS_REPO"

# Logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$ARGOCD_LOG_DIR/argocd.log"
}

error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $*" | tee -a "$ARGOCD_LOG_DIR/argocd.log" >&2
}

################################################################################
# Database initialization
################################################################################

init_database() {
    log "Initializing ArgoCD database..."
    
    sqlite3 "$ARGOCD_DB" <<EOF
CREATE TABLE IF NOT EXISTS applications (
    app_id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    namespace TEXT NOT NULL,
    repo_url TEXT NOT NULL,
    path TEXT NOT NULL,
    branch TEXT DEFAULT 'main',
    cluster TEXT DEFAULT 'in-cluster',
    sync_policy TEXT DEFAULT 'manual',
    auto_prune INTEGER DEFAULT 0,
    self_heal INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'unknown'
);

CREATE TABLE IF NOT EXISTS sync_operations (
    operation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    operation_type TEXT NOT NULL,
    status TEXT NOT NULL,
    revision TEXT,
    duration_seconds INTEGER,
    message TEXT,
    FOREIGN KEY(app_id) REFERENCES applications(app_id)
);

CREATE TABLE IF NOT EXISTS drift_events (
    drift_id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resource_kind TEXT NOT NULL,
    resource_name TEXT NOT NULL,
    drift_type TEXT NOT NULL,
    expected_state TEXT,
    actual_state TEXT,
    auto_corrected INTEGER DEFAULT 0,
    FOREIGN KEY(app_id) REFERENCES applications(app_id)
);

CREATE TABLE IF NOT EXISTS clusters (
    cluster_id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    server_url TEXT NOT NULL,
    config TEXT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'unknown'
);

CREATE TABLE IF NOT EXISTS repositories (
    repo_id TEXT PRIMARY KEY,
    url TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL,
    credentials TEXT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_sync TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_app_name ON applications(name);
CREATE INDEX IF NOT EXISTS idx_sync_timestamp ON sync_operations(timestamp);
CREATE INDEX IF NOT EXISTS idx_drift_timestamp ON drift_events(timestamp);
EOF
    
    log "Database initialized successfully"
}

################################################################################
# ArgoCD installation
################################################################################

install_argocd() {
    log "Installing ArgoCD v${ARGOCD_VERSION}..."
    
    # Create namespace
    kubectl create namespace "$ARGOCD_NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    
    # Install ArgoCD
    kubectl apply -n "$ARGOCD_NAMESPACE" \
        -f "https://raw.githubusercontent.com/argoproj/argo-cd/v${ARGOCD_VERSION}/manifests/install.yaml"
    
    # Wait for deployments
    kubectl wait --for=condition=Available --timeout=600s \
        -n "$ARGOCD_NAMESPACE" \
        deployment/argocd-server \
        deployment/argocd-repo-server \
        deployment/argocd-application-controller \
        deployment/argocd-dex-server \
        deployment/argocd-redis
    
    log "ArgoCD core components installed"
}

configure_argocd() {
    log "Configuring ArgoCD..."
    
    # Configure ArgoCD ConfigMap
    kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-cm
  namespace: ${ARGOCD_NAMESPACE}
data:
  # Application reconciliation timeout
  timeout.reconciliation: 180s
  
  # Enable anonymous access (for metrics)
  users.anonymous.enabled: "false"
  
  # Resource exclusions
  resource.exclusions: |
    - apiGroups:
      - cilium.io
      kinds:
      - CiliumIdentity
      clusters:
      - "*"
  
  # Resource inclusions
  resource.inclusions: |
    - apiGroups:
      - "*"
      kinds:
      - "*"
      clusters:
      - "*"
  
  # Diff customization
  resource.customizations: |
    admissionregistration.k8s.io/MutatingWebhookConfiguration:
      ignoreDifferences: |
        jsonPointers:
        - /webhooks/0/clientConfig/caBundle
    admissionregistration.k8s.io/ValidatingWebhookConfiguration:
      ignoreDifferences: |
        jsonPointers:
        - /webhooks/0/clientConfig/caBundle
  
  # Status badge
  statusbadge.enabled: "true"
  
  # Application instance label key
  application.instanceLabelKey: "argocd.argoproj.io/instance"
EOF
    
    # Configure ArgoCD RBAC
    kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-rbac-cm
  namespace: ${ARGOCD_NAMESPACE}
data:
  policy.default: role:readonly
  policy.csv: |
    # Admin role
    p, role:admin, applications, *, */*, allow
    p, role:admin, clusters, *, *, allow
    p, role:admin, repositories, *, *, allow
    p, role:admin, projects, *, *, allow
    
    # Developer role
    p, role:developer, applications, get, */*, allow
    p, role:developer, applications, sync, */*, allow
    p, role:developer, applications, create, */*, allow
    p, role:developer, applications, update, */*, allow
    
    # Readonly role
    p, role:readonly, applications, get, */*, allow
    p, role:readonly, projects, get, *, allow
    
    # Grant admin role to admin user
    g, admin, role:admin
EOF
    
    log "ArgoCD configuration applied"
}

expose_argocd_server() {
    log "Exposing ArgoCD server..."
    
    # Create LoadBalancer service
    kubectl patch svc argocd-server -n "$ARGOCD_NAMESPACE" -p '{"spec": {"type": "LoadBalancer"}}'
    
    # Wait for external IP
    log "Waiting for external IP..."
    while [ -z "$ARGOCD_SERVER_ADDR" ]; do
        ARGOCD_SERVER_ADDR=$(kubectl get svc argocd-server -n "$ARGOCD_NAMESPACE" \
            -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
        sleep 5
    done
    
    log "ArgoCD server exposed at: $ARGOCD_SERVER_ADDR"
    
    # Get initial admin password
    ARGOCD_ADMIN_PASSWORD=$(kubectl get secret argocd-initial-admin-secret \
        -n "$ARGOCD_NAMESPACE" \
        -o jsonpath='{.data.password}' | base64 -d)
    
    log "Initial admin password: $ARGOCD_ADMIN_PASSWORD"
    
    # Save credentials
    cat > "$ARGOCD_CONFIG_DIR/credentials.conf" <<EOF
ARGOCD_SERVER=${ARGOCD_SERVER_ADDR}
ARGOCD_USERNAME=admin
ARGOCD_PASSWORD=${ARGOCD_ADMIN_PASSWORD}
EOF
    chmod 600 "$ARGOCD_CONFIG_DIR/credentials.conf"
}

install_argocd_cli() {
    log "Installing ArgoCD CLI..."
    
    local arch=""
    case $(uname -m) in
        x86_64) arch="amd64" ;;
        aarch64) arch="arm64" ;;
        *) error "Unsupported architecture"; return 1 ;;
    esac
    
    curl -sSL -o /usr/local/bin/argocd \
        "https://github.com/argoproj/argo-cd/releases/download/v${ARGOCD_VERSION}/argocd-linux-${arch}"
    
    chmod +x /usr/local/bin/argocd
    
    log "ArgoCD CLI installed successfully"
}

################################################################################
# Application management
################################################################################

create_application() {
    local app_name="$1"
    local namespace="$2"
    local repo_url="$3"
    local path="$4"
    local branch="${5:-main}"
    local cluster="${6:-https://kubernetes.default.svc}"
    local sync_policy="${7:-automated}"
    
    log "Creating ArgoCD application: $app_name"
    
    local app_id=$(uuidgen | tr -d '-' | head -c 16)
    
    # Determine sync policy options
    local auto_prune="false"
    local self_heal="false"
    
    if [ "$sync_policy" = "automated" ]; then
        auto_prune="true"
        self_heal="true"
    fi
    
    # Create ArgoCD Application
    cat <<EOF | kubectl apply -f -
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: ${app_name}
  namespace: ${ARGOCD_NAMESPACE}
  finalizers:
  - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  
  source:
    repoURL: ${repo_url}
    targetRevision: ${branch}
    path: ${path}
  
  destination:
    server: ${cluster}
    namespace: ${namespace}
  
  syncPolicy:
    automated:
      prune: ${auto_prune}
      selfHeal: ${self_heal}
      allowEmpty: false
    syncOptions:
    - CreateNamespace=true
    - PrunePropagationPolicy=foreground
    - PruneLast=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
EOF
    
    # Store in database
    sqlite3 "$ARGOCD_DB" <<EOF
INSERT INTO applications VALUES (
    '${app_id}',
    '${app_name}',
    '${namespace}',
    '${repo_url}',
    '${path}',
    '${branch}',
    '${cluster}',
    '${sync_policy}',
    $([ "$auto_prune" = "true" ] && echo 1 || echo 0),
    $([ "$self_heal" = "true" ] && echo 1 || echo 0),
    datetime('now'),
    'Synced'
);
EOF
    
    log "Application created: $app_name (ID: $app_id)"
    echo "$app_id"
}

sync_application() {
    local app_name="$1"
    local prune="${2:-false}"
    
    log "Syncing application: $app_name"
    
    local start_time=$(date +%s)
    
    # Perform sync
    if [ "$prune" = "true" ]; then
        argocd app sync "$app_name" --prune --timeout 300
    else
        argocd app sync "$app_name" --timeout 300
    fi
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # Get revision
    local revision=$(argocd app get "$app_name" -o json | jq -r '.status.sync.revision // "unknown"')
    
    # Store sync operation
    local app_id=$(sqlite3 "$ARGOCD_DB" \
        "SELECT app_id FROM applications WHERE name='$app_name' LIMIT 1")
    
    if [ -n "$app_id" ]; then
        sqlite3 "$ARGOCD_DB" <<EOF
INSERT INTO sync_operations (app_id, operation_type, status, revision, duration_seconds, message)
VALUES ('$app_id', 'manual_sync', 'Succeeded', '$revision', $duration, 'Manual sync completed');
EOF
    fi
    
    log "Sync completed in ${duration}s"
}

rollback_application() {
    local app_name="$1"
    local revision="${2:-}"
    
    log "Rolling back application: $app_name"
    
    if [ -z "$revision" ]; then
        # Get previous revision
        revision=$(argocd app history "$app_name" -o json | \
            jq -r '.[1].revision // "HEAD~1"')
    fi
    
    argocd app rollback "$app_name" "$revision"
    
    log "Rollback to revision $revision completed"
}

delete_application() {
    local app_name="$1"
    local cascade="${2:-true}"
    
    log "Deleting application: $app_name"
    
    if [ "$cascade" = "true" ]; then
        argocd app delete "$app_name" --cascade --yes
    else
        argocd app delete "$app_name" --yes
    fi
    
    # Update database
    sqlite3 "$ARGOCD_DB" \
        "UPDATE applications SET status='Deleted' WHERE name='$app_name'"
    
    log "Application deleted: $app_name"
}

################################################################################
# Drift detection and remediation
################################################################################

detect_drift() {
    local app_name="$1"
    
    log "Detecting drift for application: $app_name"
    
    # Get application diff
    local diff_output=$(argocd app diff "$app_name" 2>&1 || true)
    
    if echo "$diff_output" | grep -q "No differences"; then
        log "No drift detected for $app_name"
        return 0
    fi
    
    # Parse drift
    local drift_count=$(echo "$diff_output" | grep -c "^====" || true)
    
    if [ $drift_count -gt 0 ]; then
        log "Drift detected: $drift_count resources out of sync"
        
        # Store drift events
        local app_id=$(sqlite3 "$ARGOCD_DB" \
            "SELECT app_id FROM applications WHERE name='$app_name' LIMIT 1")
        
        if [ -n "$app_id" ]; then
            echo "$diff_output" | grep -A 10 "^====" | while read -r line; do
                if echo "$line" | grep -q "^===="; then
                    local resource=$(echo "$line" | sed 's/==== //g' | sed 's/ ====//g')
                    
                    sqlite3 "$ARGOCD_DB" <<EOF
INSERT INTO drift_events (app_id, resource_kind, resource_name, drift_type)
VALUES ('$app_id', 'unknown', '$resource', 'modified');
EOF
                fi
            done
        fi
        
        return 1
    fi
    
    return 0
}

auto_remediate_drift() {
    local app_name="$1"
    
    log "Auto-remediating drift for: $app_name"
    
    # Check if self-heal is enabled
    local self_heal=$(sqlite3 "$ARGOCD_DB" \
        "SELECT self_heal FROM applications WHERE name='$app_name' LIMIT 1")
    
    if [ "$self_heal" != "1" ]; then
        log "Self-heal not enabled for $app_name, skipping auto-remediation"
        return
    fi
    
    # Sync to remediate
    sync_application "$app_name" "true"
    
    # Update drift events
    local app_id=$(sqlite3 "$ARGOCD_DB" \
        "SELECT app_id FROM applications WHERE name='$app_name' LIMIT 1")
    
    sqlite3 "$ARGOCD_DB" \
        "UPDATE drift_events SET auto_corrected=1 
         WHERE app_id='$app_id' AND auto_corrected=0"
    
    log "Drift auto-remediated for $app_name"
}

continuous_drift_monitoring() {
    log "Starting continuous drift monitoring..."
    
    while true; do
        # Get all applications
        local apps=$(sqlite3 "$ARGOCD_DB" \
            "SELECT name FROM applications WHERE status='Synced'")
        
        while IFS= read -r app_name; do
            if [ -z "$app_name" ]; then continue; fi
            
            # Detect drift
            if ! detect_drift "$app_name"; then
                # Drift detected, auto-remediate if enabled
                auto_remediate_drift "$app_name"
            fi
        done <<< "$apps"
        
        sleep 300  # Check every 5 minutes
    done
}

################################################################################
# Multi-cluster management
################################################################################

add_cluster() {
    local cluster_name="$1"
    local server_url="$2"
    local kubeconfig="${3:-$HOME/.kube/config}"
    
    log "Adding cluster: $cluster_name"
    
    local cluster_id=$(uuidgen | tr -d '-' | head -c 16)
    
    # Add cluster to ArgoCD
    argocd cluster add "$cluster_name" \
        --kubeconfig "$kubeconfig" \
        --name "$cluster_name" \
        --yes
    
    # Store in database
    sqlite3 "$ARGOCD_DB" <<EOF
INSERT INTO clusters VALUES (
    '${cluster_id}',
    '${cluster_name}',
    '${server_url}',
    '',
    datetime('now'),
    'Healthy'
);
EOF
    
    log "Cluster added: $cluster_name (ID: $cluster_id)"
    echo "$cluster_id"
}

list_clusters() {
    log "Listing clusters..."
    
    argocd cluster list
}

remove_cluster() {
    local cluster_name="$1"
    
    log "Removing cluster: $cluster_name"
    
    argocd cluster rm "$cluster_name"
    
    sqlite3 "$ARGOCD_DB" \
        "UPDATE clusters SET status='Removed' WHERE name='$cluster_name'"
    
    log "Cluster removed: $cluster_name"
}

################################################################################
# Repository management
################################################################################

add_repository() {
    local repo_url="$1"
    local username="${2:-}"
    local password="${3:-}"
    local ssh_private_key="${4:-}"
    
    log "Adding repository: $repo_url"
    
    local repo_id=$(uuidgen | tr -d '-' | head -c 16)
    
    # Add repository to ArgoCD
    if [ -n "$ssh_private_key" ]; then
        argocd repo add "$repo_url" \
            --ssh-private-key-path "$ssh_private_key"
    elif [ -n "$username" ] && [ -n "$password" ]; then
        argocd repo add "$repo_url" \
            --username "$username" \
            --password "$password"
    else
        argocd repo add "$repo_url"
    fi
    
    # Determine repo type
    local repo_type="git"
    if echo "$repo_url" | grep -q "helm"; then
        repo_type="helm"
    fi
    
    # Store in database
    sqlite3 "$ARGOCD_DB" <<EOF
INSERT INTO repositories VALUES (
    '${repo_id}',
    '${repo_url}',
    '${repo_type}',
    '',
    datetime('now'),
    datetime('now')
);
EOF
    
    log "Repository added: $repo_url (ID: $repo_id)"
    echo "$repo_id"
}

list_repositories() {
    log "Listing repositories..."
    
    argocd repo list
}

################################################################################
# Application of Applications pattern
################################################################################

create_app_of_apps() {
    local project_name="$1"
    local repo_url="$2"
    local path="$3"
    
    log "Creating App of Apps for project: $project_name"
    
    cat <<EOF | kubectl apply -f -
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: ${project_name}-apps
  namespace: ${ARGOCD_NAMESPACE}
spec:
  project: default
  
  source:
    repoURL: ${repo_url}
    targetRevision: HEAD
    path: ${path}
  
  destination:
    server: https://kubernetes.default.svc
    namespace: ${ARGOCD_NAMESPACE}
  
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
EOF
    
    log "App of Apps created: ${project_name}-apps"
}

################################################################################
# Monitoring and metrics
################################################################################

get_application_health() {
    local app_name="$1"
    
    argocd app get "$app_name" -o json | \
        jq -r '.status.health.status // "Unknown"'
}

get_sync_status() {
    local app_name="$1"
    
    argocd app get "$app_name" -o json | \
        jq -r '.status.sync.status // "Unknown"'
}

get_application_metrics() {
    local app_name="$1"
    local hours="${2:-24}"
    
    local app_id=$(sqlite3 "$ARGOCD_DB" \
        "SELECT app_id FROM applications WHERE name='$app_name' LIMIT 1")
    
    if [ -z "$app_id" ]; then
        error "Application not found: $app_name"
        return 1
    fi
    
    echo "=== Metrics for $app_name (last ${hours}h) ==="
    
    # Sync operations
    local total_syncs=$(sqlite3 "$ARGOCD_DB" \
        "SELECT COUNT(*) FROM sync_operations 
         WHERE app_id='$app_id' 
         AND timestamp > datetime('now', '-${hours} hours')")
    
    local successful_syncs=$(sqlite3 "$ARGOCD_DB" \
        "SELECT COUNT(*) FROM sync_operations 
         WHERE app_id='$app_id' 
         AND status='Succeeded'
         AND timestamp > datetime('now', '-${hours} hours')")
    
    local avg_sync_time=$(sqlite3 "$ARGOCD_DB" \
        "SELECT AVG(duration_seconds) FROM sync_operations 
         WHERE app_id='$app_id' 
         AND timestamp > datetime('now', '-${hours} hours')")
    
    echo "Total syncs: $total_syncs"
    echo "Successful syncs: $successful_syncs"
    echo "Avg sync time: ${avg_sync_time:-0}s"
    
    # Drift events
    local total_drift=$(sqlite3 "$ARGOCD_DB" \
        "SELECT COUNT(*) FROM drift_events 
         WHERE app_id='$app_id' 
         AND timestamp > datetime('now', '-${hours} hours')")
    
    local auto_corrected=$(sqlite3 "$ARGOCD_DB" \
        "SELECT COUNT(*) FROM drift_events 
         WHERE app_id='$app_id' 
         AND auto_corrected=1
         AND timestamp > datetime('now', '-${hours} hours')")
    
    echo "Drift events: $total_drift"
    echo "Auto-corrected: $auto_corrected"
    
    # Current status
    local health=$(get_application_health "$app_name")
    local sync_status=$(get_sync_status "$app_name")
    
    echo "Health: $health"
    echo "Sync status: $sync_status"
}

generate_gitops_report() {
    log "Generating GitOps report..."
    
    echo "=== GitOps Status Report ==="
    echo "Generated: $(date)"
    echo ""
    
    # Total applications
    local total_apps=$(sqlite3 "$ARGOCD_DB" "SELECT COUNT(*) FROM applications")
    echo "Total applications: $total_apps"
    
    # Application health
    argocd app list -o json | jq -r '
        group_by(.status.health.status) | 
        map({status: .[0].status.health.status, count: length}) | 
        .[] | 
        "\(.status): \(.count)"
    '
    
    echo ""
    
    # Sync statistics (last 24h)
    local total_syncs=$(sqlite3 "$ARGOCD_DB" \
        "SELECT COUNT(*) FROM sync_operations 
         WHERE timestamp > datetime('now', '-24 hours')")
    
    local successful_syncs=$(sqlite3 "$ARGOCD_DB" \
        "SELECT COUNT(*) FROM sync_operations 
         WHERE status='Succeeded' 
         AND timestamp > datetime('now', '-24 hours')")
    
    echo "Syncs (24h): $total_syncs (Success: $successful_syncs)"
    
    # Drift events (last 24h)
    local drift_events=$(sqlite3 "$ARGOCD_DB" \
        "SELECT COUNT(*) FROM drift_events 
         WHERE timestamp > datetime('now', '-24 hours')")
    
    echo "Drift events (24h): $drift_events"
}

################################################################################
# Main functions
################################################################################

setup_gitops() {
    log "Setting up GitOps with ArgoCD..."
    
    init_database
    install_argocd
    configure_argocd
    install_argocd_cli
    expose_argocd_server
    
    log "GitOps setup completed successfully"
    log "ArgoCD UI: https://${ARGOCD_SERVER_ADDR}"
    log "Username: admin"
    log "Password: ${ARGOCD_ADMIN_PASSWORD}"
}

usage() {
    cat <<EOF
GitOps with ArgoCD Integration v11.0

Usage: $0 COMMAND [OPTIONS]

Commands:
  setup                                  Setup ArgoCD
  
  create-app NAME NS REPO PATH [BRANCH] Create application
  sync APP [PRUNE]                       Sync application
  rollback APP [REVISION]                Rollback application
  delete APP [CASCADE]                   Delete application
  
  detect-drift APP                       Detect drift
  monitor-drift                          Continuous drift monitoring
  
  add-cluster NAME URL [KUBECONFIG]      Add cluster
  list-clusters                          List clusters
  remove-cluster NAME                    Remove cluster
  
  add-repo URL [USER] [PASS] [SSH_KEY]   Add repository
  list-repos                             List repositories
  
  app-of-apps PROJECT REPO PATH          Create App of Apps
  
  metrics APP [HOURS]                    Show application metrics
  report                                 Generate GitOps report

Examples:
  $0 setup
  $0 create-app myapp default https://github.com/org/repo k8s/myapp
  $0 sync myapp true
  $0 detect-drift myapp

EOF
}

main() {
    case "${1:-}" in
        setup)
            setup_gitops
            ;;
        create-app)
            create_application "${2:-}" "${3:-}" "${4:-}" "${5:-}" "${6:-main}" "${7:-https://kubernetes.default.svc}" "${8:-automated}"
            ;;
        sync)
            sync_application "${2:-}" "${3:-false}"
            ;;
        rollback)
            rollback_application "${2:-}" "${3:-}"
            ;;
        delete)
            delete_application "${2:-}" "${3:-true}"
            ;;
        detect-drift)
            detect_drift "${2:-}"
            ;;
        monitor-drift)
            continuous_drift_monitoring
            ;;
        add-cluster)
            add_cluster "${2:-}" "${3:-}" "${4:-}"
            ;;
        list-clusters)
            list_clusters
            ;;
        remove-cluster)
            remove_cluster "${2:-}"
            ;;
        add-repo)
            add_repository "${2:-}" "${3:-}" "${4:-}" "${5:-}"
            ;;
        list-repos)
            list_repositories
            ;;
        app-of-apps)
            create_app_of_apps "${2:-}" "${3:-}" "${4:-}"
            ;;
        metrics)
            get_application_metrics "${2:-}" "${3:-24}"
            ;;
        report)
            generate_gitops_report
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
