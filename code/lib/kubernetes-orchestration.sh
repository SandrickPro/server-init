#!/usr/bin/env bash

###############################################################################
# KUBERNETES ORCHESTRATION MODULE v11.0
# Cloud-native infrastructure with K8s, Helm, and Service Mesh
###############################################################################

set -euo pipefail

# Configuration
K8S_VERSION="${K8S_VERSION:-1.28}"
HELM_VERSION="3.13.0"
ISTIO_VERSION="1.19.0"
CLUSTER_NAME="${CLUSTER_NAME:-devops-cluster}"
NAMESPACE="${NAMESPACE:-production}"

###############################################################################
# Kubernetes Installation
###############################################################################

install_kubernetes() {
    echo "☸️  Installing Kubernetes ${K8S_VERSION}..."
    
    # Install dependencies
    apt-get update
    apt-get install -y apt-transport-https ca-certificates curl gpg
    
    # Add Kubernetes repository
    curl -fsSL https://pkgs.k8s.io/core:/stable:/v${K8S_VERSION}/deb/Release.key | \
        gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
    
    echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v${K8S_VERSION}/deb/ /" | \
        tee /etc/apt/sources.list.d/kubernetes.list
    
    # Install Kubernetes components
    apt-get update
    apt-get install -y kubelet kubeadm kubectl
    apt-mark hold kubelet kubeadm kubectl
    
    # Initialize control plane
    if [[ ! -f /etc/kubernetes/admin.conf ]]; then
        kubeadm init --pod-network-cidr=10.244.0.0/16 --cluster-name="$CLUSTER_NAME"
        
        # Setup kubeconfig
        mkdir -p $HOME/.kube
        cp /etc/kubernetes/admin.conf $HOME/.kube/config
        chown $(id -u):$(id -g) $HOME/.kube/config
    fi
    
    # Install CNI (Calico)
    kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
    
    # Allow scheduling on control plane (for single-node clusters)
    kubectl taint nodes --all node-role.kubernetes.io/control-plane- || true
    
    echo "✅ Kubernetes installed successfully"
}

install_helm() {
    echo "⎈ Installing Helm ${HELM_VERSION}..."
    
    curl -fsSL https://get.helm.sh/helm-v${HELM_VERSION}-linux-amd64.tar.gz | tar -xz
    mv linux-amd64/helm /usr/local/bin/helm
    rm -rf linux-amd64
    
    # Add popular repositories
    helm repo add stable https://charts.helm.sh/stable
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo add jetstack https://charts.jetstack.io
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    
    echo "✅ Helm installed successfully"
}

install_istio() {
    echo "🕸️  Installing Istio ${ISTIO_VERSION}..."
    
    # Download Istio
    curl -L https://istio.io/downloadIstio | ISTIO_VERSION=${ISTIO_VERSION} sh -
    cd istio-${ISTIO_VERSION}
    
    # Install Istio
    ./bin/istioctl install --set profile=production -y
    
    # Enable automatic sidecar injection
    kubectl label namespace "$NAMESPACE" istio-injection=enabled --overwrite
    
    # Install Istio addons (Kiali, Prometheus, Grafana, Jaeger)
    kubectl apply -f samples/addons/
    
    # Move istioctl to PATH
    mv ./bin/istioctl /usr/local/bin/
    cd ..
    rm -rf istio-${ISTIO_VERSION}
    
    echo "✅ Istio service mesh installed successfully"
}

###############################################################################
# Application Deployment
###############################################################################

create_helm_chart() {
    local app_name=$1
    local chart_dir="./helm/${app_name}"
    
    echo "📦 Creating Helm chart for ${app_name}..."
    
    mkdir -p "$chart_dir/templates"
    
    # Chart.yaml
    cat > "${chart_dir}/Chart.yaml" << EOF
apiVersion: v2
name: ${app_name}
description: A Helm chart for ${app_name}
type: application
version: 1.0.0
appVersion: "1.0.0"
EOF
    
    # values.yaml
    cat > "${chart_dir}/values.yaml" << EOF
replicaCount: 3

image:
  repository: ${app_name}
  pullPolicy: IfNotPresent
  tag: "latest"

service:
  type: ClusterIP
  port: 80
  targetPort: 8080

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: ${app_name}.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: ${app_name}-tls
      hosts:
        - ${app_name}.example.com

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

postgresql:
  enabled: true
  auth:
    database: ${app_name}
    username: ${app_name}
    password: changeme

redis:
  enabled: true
  auth:
    enabled: true
    password: changeme
  master:
    persistence:
      enabled: true
      size: 8Gi

monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
    interval: 30s
EOF
    
    # Deployment template
    cat > "${chart_dir}/templates/deployment.yaml" << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "app.fullname" . }}
  labels:
    {{- include "app.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "app.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
      labels:
        {{- include "app.selectorLabels" . | nindent 8 }}
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - name: http
          containerPort: {{ .Values.service.targetPort }}
          protocol: TCP
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: http
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          {{- toYaml .Values.resources | nindent 12 }}
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: {{ include "app.fullname" . }}-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: {{ include "app.fullname" . }}-secrets
              key: redis-url
EOF
    
    # Service template
    cat > "${chart_dir}/templates/service.yaml" << 'EOF'
apiVersion: v1
kind: Service
metadata:
  name: {{ include "app.fullname" . }}
  labels:
    {{- include "app.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: http
      protocol: TCP
      name: http
  selector:
    {{- include "app.selectorLabels" . | nindent 4 }}
EOF
    
    # Ingress template
    cat > "${chart_dir}/templates/ingress.yaml" << 'EOF'
{{- if .Values.ingress.enabled -}}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ include "app.fullname" . }}
  labels:
    {{- include "app.labels" . | nindent 4 }}
  {{- with .Values.ingress.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
spec:
  ingressClassName: {{ .Values.ingress.className }}
  {{- if .Values.ingress.tls }}
  tls:
    {{- range .Values.ingress.tls }}
    - hosts:
        {{- range .hosts }}
        - {{ . | quote }}
        {{- end }}
      secretName: {{ .secretName }}
    {{- end }}
  {{- end }}
  rules:
    {{- range .Values.ingress.hosts }}
    - host: {{ .host | quote }}
      http:
        paths:
          {{- range .paths }}
          - path: {{ .path }}
            pathType: {{ .pathType }}
            backend:
              service:
                name: {{ include "app.fullname" $ }}
                port:
                  number: {{ $.Values.service.port }}
          {{- end }}
    {{- end }}
{{- end }}
EOF
    
    # HPA template
    cat > "${chart_dir}/templates/hpa.yaml" << 'EOF'
{{- if .Values.autoscaling.enabled }}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ include "app.fullname" . }}
  labels:
    {{- include "app.labels" . | nindent 4 }}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ include "app.fullname" . }}
  minReplicas: {{ .Values.autoscaling.minReplicas }}
  maxReplicas: {{ .Values.autoscaling.maxReplicas }}
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: {{ .Values.autoscaling.targetCPUUtilizationPercentage }}
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: {{ .Values.autoscaling.targetMemoryUtilizationPercentage }}
{{- end }}
EOF
    
    # Helpers template
    cat > "${chart_dir}/templates/_helpers.tpl" << 'EOF'
{{- define "app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "app.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{- define "app.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "app.labels" -}}
helm.sh/chart: {{ include "app.chart" . }}
{{ include "app.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
EOF
    
    echo "✅ Helm chart created: ${chart_dir}"
}

deploy_application() {
    local app_name=$1
    local namespace=${2:-$NAMESPACE}
    
    echo "🚀 Deploying ${app_name} to ${namespace}..."
    
    # Create namespace if not exists
    kubectl create namespace "$namespace" --dry-run=client -o yaml | kubectl apply -f -
    
    # Enable Istio injection
    kubectl label namespace "$namespace" istio-injection=enabled --overwrite
    
    # Deploy with Helm
    helm upgrade --install "$app_name" "./helm/${app_name}" \
        --namespace "$namespace" \
        --create-namespace \
        --wait \
        --timeout 10m
    
    echo "✅ ${app_name} deployed successfully"
}

###############################################################################
# Monitoring & Observability
###############################################################################

install_monitoring_stack() {
    echo "📊 Installing monitoring stack..."
    
    # Create monitoring namespace
    kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
    
    # Install Prometheus Operator
    helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
        --namespace monitoring \
        --set prometheus.prometheusSpec.retention=30d \
        --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=100Gi \
        --set grafana.enabled=true \
        --set grafana.adminPassword=admin \
        --set alertmanager.enabled=true
    
    # Install Loki for log aggregation
    helm upgrade --install loki bitnami/grafana-loki \
        --namespace monitoring \
        --set loki.auth.enabled=false \
        --set persistence.enabled=true \
        --set persistence.size=50Gi
    
    # Install Jaeger for distributed tracing
    kubectl apply -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/main/deploy/crds/jaegertracing.io_jaegers_crd.yaml
    kubectl apply -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/main/deploy/service_account.yaml
    kubectl apply -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/main/deploy/role.yaml
    kubectl apply -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/main/deploy/role_binding.yaml
    kubectl apply -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/main/deploy/operator.yaml
    
    # Deploy Jaeger instance
    cat <<EOF | kubectl apply -f -
apiVersion: jaegertracing.io/v1
kind: Jaeger
metadata:
  name: jaeger
  namespace: monitoring
spec:
  strategy: production
  storage:
    type: elasticsearch
    options:
      es:
        server-urls: http://elasticsearch:9200
EOF
    
    echo "✅ Monitoring stack installed"
}

###############################################################################
# Security & Compliance
###############################################################################

install_cert_manager() {
    echo "🔒 Installing cert-manager..."
    
    # Install cert-manager
    kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
    
    # Wait for cert-manager to be ready
    kubectl wait --for=condition=available --timeout=300s deployment/cert-manager -n cert-manager
    kubectl wait --for=condition=available --timeout=300s deployment/cert-manager-webhook -n cert-manager
    kubectl wait --for=condition=available --timeout=300s deployment/cert-manager-cainjector -n cert-manager
    
    # Create Let's Encrypt ClusterIssuer
    cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
    
    echo "✅ cert-manager installed"
}

install_policy_engine() {
    echo "🛡️  Installing OPA Gatekeeper..."
    
    # Install Gatekeeper
    kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/release-3.14/deploy/gatekeeper.yaml
    
    # Create constraint template for required labels
    cat <<EOF | kubectl apply -f -
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        openAPIV3Schema:
          type: object
          properties:
            labels:
              type: array
              items:
                type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels
        
        violation[{"msg": msg, "details": {"missing_labels": missing}}] {
          provided := {label | input.review.object.metadata.labels[label]}
          required := {label | label := input.parameters.labels[_]}
          missing := required - provided
          count(missing) > 0
          msg := sprintf("You must provide labels: %v", [missing])
        }
EOF
    
    # Create constraint
    cat <<EOF | kubectl apply -f -
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: must-have-owner
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
  parameters:
    labels: ["owner", "app", "env"]
EOF
    
    echo "✅ OPA Gatekeeper installed"
}

###############################################################################
# Service Mesh Configuration
###############################################################################

configure_service_mesh() {
    echo "🕸️  Configuring service mesh..."
    
    # Create virtual service for canary deployments
    cat <<EOF | kubectl apply -f -
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: app-canary
  namespace: $NAMESPACE
spec:
  hosts:
  - app.example.com
  http:
  - match:
    - headers:
        x-canary:
          exact: "true"
    route:
    - destination:
        host: app
        subset: canary
      weight: 100
  - route:
    - destination:
        host: app
        subset: stable
      weight: 90
    - destination:
        host: app
        subset: canary
      weight: 10
EOF
    
    # Create destination rule
    cat <<EOF | kubectl apply -f -
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: app
  namespace: $NAMESPACE
spec:
  host: app
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
        http2MaxRequests: 100
        maxRequestsPerConnection: 2
    loadBalancer:
      simple: LEAST_REQUEST
    outlierDetection:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
  subsets:
  - name: stable
    labels:
      version: stable
  - name: canary
    labels:
      version: canary
EOF
    
    # Create circuit breaker
    cat <<EOF | kubectl apply -f -
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: circuit-breaker
  namespace: $NAMESPACE
spec:
  host: app
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 1
      http:
        http1MaxPendingRequests: 1
        maxRequestsPerConnection: 1
    outlierDetection:
      consecutiveErrors: 1
      interval: 1s
      baseEjectionTime: 3m
      maxEjectionPercent: 100
EOF
    
    echo "✅ Service mesh configured"
}

###############################################################################
# Disaster Recovery
###############################################################################

setup_backup_restore() {
    echo "💾 Setting up backup and restore..."
    
    # Install Velero
    wget https://github.com/vmware-tanzu/velero/releases/download/v1.12.0/velero-v1.12.0-linux-amd64.tar.gz
    tar -xvf velero-v1.12.0-linux-amd64.tar.gz
    mv velero-v1.12.0-linux-amd64/velero /usr/local/bin/
    rm -rf velero-v1.12.0-linux-amd64*
    
    # Configure Velero (example with MinIO)
    velero install \
        --provider aws \
        --plugins velero/velero-plugin-for-aws:v1.8.0 \
        --bucket velero \
        --secret-file ./credentials-velero \
        --use-volume-snapshots=false \
        --backup-location-config region=minio,s3ForcePathStyle="true",s3Url=http://minio.velero.svc:9000
    
    # Create backup schedule
    velero schedule create daily-backup --schedule="0 2 * * *"
    
    echo "✅ Backup and restore configured"
}

###############################################################################
# Main Setup
###############################################################################

setup_kubernetes_cluster() {
    echo "☸️  Setting up Kubernetes cluster..."
    
    # Core installation
    install_kubernetes
    install_helm
    install_istio
    
    # Security
    install_cert_manager
    install_policy_engine
    
    # Monitoring
    install_monitoring_stack
    
    # Service Mesh
    configure_service_mesh
    
    # Disaster Recovery
    setup_backup_restore
    
    echo "✅ Kubernetes cluster setup complete!"
    echo ""
    echo "📋 Access information:"
    echo "   - Kubernetes Dashboard: kubectl proxy"
    echo "   - Grafana: kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80"
    echo "   - Prometheus: kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090"
    echo "   - Jaeger: kubectl port-forward -n monitoring svc/jaeger-query 16686:16686"
    echo "   - Kiali: kubectl port-forward -n istio-system svc/kiali 20001:20001"
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    setup_kubernetes_cluster
fi
