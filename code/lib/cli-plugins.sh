#!/bin/bash
#
# CLI Plugins System v11.0
# Custom kubectl plugins with auto-completion and interactive wizards
#

set -euo pipefail

# Configuration
PLUGINS_DIR="${HOME}/.kube/plugins"
COMPLETIONS_DIR="${HOME}/.kube/completions"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

init_plugins() {
    log_info "Initializing CLI plugins system..."
    
    mkdir -p "$PLUGINS_DIR"
    mkdir -p "$COMPLETIONS_DIR"
    
    # Add plugins to PATH
    if ! grep -q "PLUGINS_DIR" ~/.bashrc 2>/dev/null; then
        echo "export PATH=\"\$PATH:$PLUGINS_DIR\"" >> ~/.bashrc
    fi
    
    log_info "Plugins directory: $PLUGINS_DIR"
}

create_plugin() {
    local plugin_name="$1"
    local description="${2:-Custom kubectl plugin}"
    
    log_info "Creating plugin: kubectl-${plugin_name}"
    
    cat > "$PLUGINS_DIR/kubectl-${plugin_name}" <<'EOF'
#!/bin/bash
#
# kubectl-PLUGIN_NAME plugin
# DESCRIPTION
#

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

show_help() {
    cat <<HELP
kubectl-PLUGIN_NAME - DESCRIPTION

Usage:
  kubectl PLUGIN_NAME [options]

Options:
  -h, --help     Show this help message
  -n, --namespace NAMESPACE   Kubernetes namespace (default: default)

Examples:
  kubectl PLUGIN_NAME
  kubectl PLUGIN_NAME -n production

HELP
}

main() {
    local namespace="default"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -n|--namespace)
                namespace="$2"
                shift 2
                ;;
            *)
                echo "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    echo -e "${GREEN}[INFO]${NC} Running kubectl-PLUGIN_NAME in namespace: $namespace"
    
    # Plugin logic here
    kubectl get pods -n "$namespace"
}

main "$@"
EOF
    
    # Replace placeholders
    sed -i "s/PLUGIN_NAME/${plugin_name}/g" "$PLUGINS_DIR/kubectl-${plugin_name}"
    sed -i "s/DESCRIPTION/${description}/g" "$PLUGINS_DIR/kubectl-${plugin_name}"
    
    chmod +x "$PLUGINS_DIR/kubectl-${plugin_name}"
    
    log_info "Plugin created: kubectl-${plugin_name}"
}

# Plugin: kubectl-status
create_status_plugin() {
    log_info "Creating kubectl-status plugin..."
    
    cat > "$PLUGINS_DIR/kubectl-status" <<'EOF'
#!/bin/bash
#
# kubectl-status - Show comprehensive cluster status
#

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

main() {
    local namespace="${1:-default}"
    
    echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║           Cluster Status Overview             ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Cluster info
    echo -e "${GREEN}▶ Cluster Info${NC}"
    kubectl cluster-info | head -1
    echo ""
    
    # Nodes
    echo -e "${GREEN}▶ Nodes ($(kubectl get nodes --no-headers | wc -l))${NC}"
    kubectl get nodes -o custom-columns=\
NAME:.metadata.name,\
STATUS:.status.conditions[-1].type,\
ROLE:.metadata.labels.node-role\\.kubernetes\\.io/.*,\
VERSION:.status.nodeInfo.kubeletVersion,\
CPU:.status.capacity.cpu,\
MEMORY:.status.capacity.memory
    echo ""
    
    # Namespaces
    echo -e "${GREEN}▶ Namespaces ($(kubectl get namespaces --no-headers | wc -l))${NC}"
    kubectl get namespaces -o custom-columns=\
NAME:.metadata.name,\
STATUS:.status.phase,\
AGE:.metadata.creationTimestamp | head -10
    echo ""
    
    # Pods in namespace
    echo -e "${GREEN}▶ Pods in $namespace${NC}"
    kubectl get pods -n "$namespace" -o custom-columns=\
NAME:.metadata.name,\
STATUS:.status.phase,\
READY:.status.conditions[?@.type==\"Ready\"].status,\
RESTARTS:.status.containerStatuses[0].restartCount,\
AGE:.metadata.creationTimestamp
    echo ""
    
    # Resource usage
    echo -e "${GREEN}▶ Resource Usage${NC}"
    kubectl top nodes 2>/dev/null || echo "Metrics server not available"
    echo ""
    
    # Recent events
    echo -e "${GREEN}▶ Recent Events (last 10)${NC}"
    kubectl get events -n "$namespace" --sort-by='.lastTimestamp' | tail -10
}

main "$@"
EOF
    
    chmod +x "$PLUGINS_DIR/kubectl-status"
    log_info "✅ kubectl-status created"
}

# Plugin: kubectl-debug
create_debug_plugin() {
    log_info "Creating kubectl-debug plugin..."
    
    cat > "$PLUGINS_DIR/kubectl-debug" <<'EOF'
#!/bin/bash
#
# kubectl-debug - Interactive debugging for pods
#

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

debug_pod() {
    local pod_name="$1"
    local namespace="${2:-default}"
    
    echo -e "${GREEN}[DEBUG]${NC} Debugging pod: $pod_name"
    echo ""
    
    # Show pod details
    echo "=== Pod Details ==="
    kubectl describe pod "$pod_name" -n "$namespace" | head -20
    echo ""
    
    # Show logs
    echo "=== Recent Logs (last 20 lines) ==="
    kubectl logs "$pod_name" -n "$namespace" --tail=20
    echo ""
    
    # Check events
    echo "=== Events ==="
    kubectl get events -n "$namespace" --field-selector involvedObject.name="$pod_name"
    echo ""
    
    # Resource usage
    echo "=== Resource Usage ==="
    kubectl top pod "$pod_name" -n "$namespace" 2>/dev/null || echo "Metrics not available"
    echo ""
    
    # Interactive menu
    echo "=== Debug Options ==="
    echo "1. View full logs"
    echo "2. Exec into container"
    echo "3. Port forward"
    echo "4. Copy files from pod"
    echo "5. Exit"
    echo ""
    
    read -p "Select option: " choice
    
    case $choice in
        1)
            kubectl logs "$pod_name" -n "$namespace" --follow
            ;;
        2)
            local container
            container=$(kubectl get pod "$pod_name" -n "$namespace" -o jsonpath='{.spec.containers[0].name}')
            kubectl exec -it "$pod_name" -n "$namespace" -c "$container" -- /bin/bash || \
            kubectl exec -it "$pod_name" -n "$namespace" -c "$container" -- /bin/sh
            ;;
        3)
            read -p "Local port: " local_port
            read -p "Pod port: " pod_port
            kubectl port-forward "$pod_name" -n "$namespace" "$local_port:$pod_port"
            ;;
        4)
            read -p "Source path in pod: " src_path
            read -p "Destination path: " dest_path
            kubectl cp "$namespace/$pod_name:$src_path" "$dest_path"
            ;;
        5)
            exit 0
            ;;
        *)
            echo "Invalid option"
            ;;
    esac
}

main() {
    local namespace="${1:-default}"
    local pod_name="${2:-}"
    
    if [[ -z "$pod_name" ]]; then
        echo "Available pods in $namespace:"
        kubectl get pods -n "$namespace" -o custom-columns=NAME:.metadata.name,STATUS:.status.phase
        echo ""
        read -p "Enter pod name: " pod_name
    fi
    
    debug_pod "$pod_name" "$namespace"
}

main "$@"
EOF
    
    chmod +x "$PLUGINS_DIR/kubectl-debug"
    log_info "✅ kubectl-debug created"
}

# Plugin: kubectl-deploy
create_deploy_plugin() {
    log_info "Creating kubectl-deploy plugin..."
    
    cat > "$PLUGINS_DIR/kubectl-deploy" <<'EOF'
#!/bin/bash
#
# kubectl-deploy - Interactive deployment wizard
#

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

deploy_wizard() {
    echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║        Interactive Deployment Wizard           ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Collect inputs
    read -p "Application name: " app_name
    read -p "Docker image: " image
    read -p "Replicas (default: 3): " replicas
    replicas=${replicas:-3}
    read -p "Container port (default: 8080): " port
    port=${port:-8080}
    read -p "Namespace (default: default): " namespace
    namespace=${namespace:-default}
    
    echo ""
    echo -e "${GREEN}▶ Deployment Configuration${NC}"
    echo "  App name: $app_name"
    echo "  Image: $image"
    echo "  Replicas: $replicas"
    echo "  Port: $port"
    echo "  Namespace: $namespace"
    echo ""
    
    read -p "Proceed with deployment? (y/n): " confirm
    if [[ "$confirm" != "y" ]]; then
        echo "Deployment cancelled"
        exit 0
    fi
    
    # Create namespace if needed
    kubectl create namespace "$namespace" --dry-run=client -o yaml | kubectl apply -f -
    
    # Generate deployment
    cat <<YAML | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: $app_name
  namespace: $namespace
spec:
  replicas: $replicas
  selector:
    matchLabels:
      app: $app_name
  template:
    metadata:
      labels:
        app: $app_name
    spec:
      containers:
      - name: $app_name
        image: $image
        ports:
        - containerPort: $port
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 1000m
            memory: 512Mi
---
apiVersion: v1
kind: Service
metadata:
  name: $app_name
  namespace: $namespace
spec:
  selector:
    app: $app_name
  ports:
  - port: 80
    targetPort: $port
  type: ClusterIP
YAML
    
    echo ""
    echo -e "${GREEN}✅ Deployment created successfully${NC}"
    echo ""
    echo "View status:"
    echo "  kubectl get pods -n $namespace -l app=$app_name"
    echo ""
    echo "View logs:"
    echo "  kubectl logs -n $namespace -l app=$app_name --follow"
}

main() {
    deploy_wizard
}

main "$@"
EOF
    
    chmod +x "$PLUGINS_DIR/kubectl-deploy"
    log_info "✅ kubectl-deploy created"
}

# Plugin: kubectl-cost
create_cost_plugin() {
    log_info "Creating kubectl-cost plugin..."
    
    cat > "$PLUGINS_DIR/kubectl-cost" <<'EOF'
#!/bin/bash
#
# kubectl-cost - Estimate resource costs
#

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Cost per hour (example rates)
CPU_COST_PER_CORE=0.04  # $0.04/core/hour
MEM_COST_PER_GB=0.005   # $0.005/GB/hour

calculate_costs() {
    local namespace="${1:-default}"
    
    echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║          Resource Cost Estimation             ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Get all pods
    kubectl get pods -n "$namespace" -o json | jq -r '
        .items[] | 
        .spec.containers[] | 
        {
            pod: .name,
            cpu: .resources.requests.cpu,
            memory: .resources.requests.memory
        } | 
        @json
    ' | while read -r pod_json; do
        local pod_name cpu_req mem_req
        pod_name=$(echo "$pod_json" | jq -r '.pod')
        cpu_req=$(echo "$pod_json" | jq -r '.cpu // "0"')
        mem_req=$(echo "$pod_json" | jq -r '.memory // "0"')
        
        # Convert CPU (100m -> 0.1)
        cpu_cores=$(echo "$cpu_req" | sed 's/m$//' | awk '{print $1/1000}')
        
        # Convert Memory (128Mi -> GB)
        mem_gb=$(echo "$mem_req" | sed 's/Mi$//' | awk '{print $1/1024}')
        
        # Calculate costs
        cpu_cost=$(echo "$cpu_cores * $CPU_COST_PER_CORE * 730" | bc)
        mem_cost=$(echo "$mem_gb * $MEM_COST_PER_GB * 730" | bc)
        total_cost=$(echo "$cpu_cost + $mem_cost" | bc)
        
        echo "Pod: $pod_name"
        echo "  CPU: ${cpu_cores} cores (~\$${cpu_cost}/month)"
        echo "  Memory: ${mem_gb} GB (~\$${mem_cost}/month)"
        echo "  Total: ~\$${total_cost}/month"
        echo ""
    done
}

main() {
    calculate_costs "$@"
}

main "$@"
EOF
    
    chmod +x "$PLUGINS_DIR/kubectl-cost"
    log_info "✅ kubectl-cost created"
}

install_auto_completion() {
    log_info "Installing auto-completion..."
    
    # Bash completion
    if [[ -f ~/.bashrc ]]; then
        cat >> ~/.bashrc <<'EOF'

# kubectl plugins auto-completion
if command -v kubectl &> /dev/null; then
    source <(kubectl completion bash)
    complete -F __start_kubectl k
fi

# Custom plugin completions
_kubectl_status_completion() {
    COMPREPLY=($(compgen -W "$(kubectl get namespaces -o jsonpath='{.items[*].metadata.name}')" -- "${COMP_WORDS[COMP_CWORD]}"))
}
complete -F _kubectl_status_completion kubectl-status

_kubectl_debug_completion() {
    local namespace="${COMP_WORDS[1]:-default}"
    COMPREPLY=($(compgen -W "$(kubectl get pods -n "$namespace" -o jsonpath='{.items[*].metadata.name}')" -- "${COMP_WORDS[COMP_CWORD]}"))
}
complete -F _kubectl_debug_completion kubectl-debug
EOF
        log_info "✅ Bash completion added to ~/.bashrc"
    fi
    
    # Zsh completion
    if [[ -f ~/.zshrc ]]; then
        cat >> ~/.zshrc <<'EOF'

# kubectl plugins auto-completion
if command -v kubectl &> /dev/null; then
    source <(kubectl completion zsh)
fi
EOF
        log_info "✅ Zsh completion added to ~/.zshrc"
    fi
}

list_plugins() {
    echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║            Installed CLI Plugins               ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
    echo ""
    
    if [[ ! -d "$PLUGINS_DIR" ]]; then
        echo "No plugins installed"
        return
    fi
    
    for plugin in "$PLUGINS_DIR"/kubectl-*; do
        if [[ -f "$plugin" ]]; then
            local plugin_name description
            plugin_name=$(basename "$plugin")
            description=$(grep -m1 '^#' "$plugin" | sed 's/^# //' | grep -v '#!/bin/bash')
            
            echo -e "${GREEN}▶ $plugin_name${NC}"
            echo "  $description"
            echo ""
        fi
    done
}

main() {
    case "${1:-}" in
        init)
            init_plugins
            ;;
        create)
            create_plugin "${2:-}" "${3:-Custom plugin}"
            ;;
        install-all)
            init_plugins
            create_status_plugin
            create_debug_plugin
            create_deploy_plugin
            create_cost_plugin
            install_auto_completion
            log_info "✅ All plugins installed"
            ;;
        list)
            list_plugins
            ;;
        completion)
            install_auto_completion
            ;;
        *)
            echo "CLI Plugins System v11.0"
            echo ""
            echo "Usage: $0 <command> [options]"
            echo ""
            echo "Commands:"
            echo "  init                      Initialize plugins system"
            echo "  create NAME [DESC]        Create custom plugin"
            echo "  install-all               Install all built-in plugins"
            echo "  list                      List installed plugins"
            echo "  completion                Install shell completion"
            echo ""
            echo "Built-in plugins:"
            echo "  kubectl-status            Comprehensive cluster status"
            echo "  kubectl-debug             Interactive pod debugging"
            echo "  kubectl-deploy            Deployment wizard"
            echo "  kubectl-cost              Resource cost estimation"
            ;;
    esac
}

main "$@"
