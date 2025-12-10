#!/usr/bin/env bash

###############################################################################
# ANOMALY DETECTION MODULE v11.0
# Real-time anomaly detection using statistical and ML methods
###############################################################################

set -euo pipefail

# Configuration
ANOMALY_THRESHOLD=3.0  # Standard deviations
PROMETHEUS_URL="${PROMETHEUS_URL:-http://localhost:9090}"
ALERT_WEBHOOK="${ALERT_WEBHOOK:-}"
LOG_DIR="/var/log/anomaly-detection"
MODEL_DIR="/var/lib/anomaly-detection"

mkdir -p "$LOG_DIR" "$MODEL_DIR"

###############################################################################
# Statistical Anomaly Detection
###############################################################################

detect_statistical_anomalies() {
    local metric_name=$1
    local lookback_minutes=${2:-60}
    
    echo "🔍 Detecting anomalies in $metric_name (lookback: ${lookback_minutes}m)..."
    
    # Query Prometheus
    local query="${metric_name}[${lookback_minutes}m]"
    local response=$(curl -s -G "$PROMETHEUS_URL/api/v1/query" \
        --data-urlencode "query=$query" \
        --data-urlencode "time=$(date +%s)")
    
    # Parse values
    local values=$(echo "$response" | jq -r '.data.result[0].values[][1]' 2>/dev/null || echo "")
    
    if [[ -z "$values" ]]; then
        echo "⚠️  No data available for $metric_name"
        return 1
    fi
    
    # Calculate statistics
    local stats=$(echo "$values" | python3 -c "
import sys
import numpy as np

values = [float(line.strip()) for line in sys.stdin if line.strip()]
if not values:
    sys.exit(1)

arr = np.array(values)
mean = np.mean(arr)
std = np.std(arr)
current = arr[-1]
z_score = (current - mean) / std if std > 0 else 0
percentile_95 = np.percentile(arr, 95)
percentile_99 = np.percentile(arr, 99)

print(f'{mean:.4f},{std:.4f},{current:.4f},{z_score:.4f},{percentile_95:.4f},{percentile_99:.4f}')
")
    
    IFS=',' read -r mean std current z_score p95 p99 <<< "$stats"
    
    # Check for anomaly
    local is_anomaly=0
    local anomaly_type=""
    
    if (( $(echo "$z_score > $ANOMALY_THRESHOLD" | bc -l) )); then
        is_anomaly=1
        anomaly_type="spike"
    elif (( $(echo "$z_score < -$ANOMALY_THRESHOLD" | bc -l) )); then
        is_anomaly=1
        anomaly_type="drop"
    fi
    
    if [[ $is_anomaly -eq 1 ]]; then
        echo "🚨 ANOMALY DETECTED: $metric_name"
        echo "   Type: $anomaly_type"
        echo "   Current: $current"
        echo "   Mean: $mean"
        echo "   Std Dev: $std"
        echo "   Z-Score: $z_score"
        
        # Log anomaly
        log_anomaly "$metric_name" "$anomaly_type" "$current" "$mean" "$z_score"
        
        # Send alert
        send_anomaly_alert "$metric_name" "$anomaly_type" "$current" "$mean" "$z_score"
        
        return 0
    else
        echo "✅ No anomaly detected in $metric_name (z-score: $z_score)"
        return 1
    fi
}

###############################################################################
# Time Series Anomaly Detection
###############################################################################

detect_time_series_anomalies() {
    local metric_name=$1
    local sensitivity=${2:-0.95}  # 0-1, higher = more sensitive
    
    echo "📊 Time series anomaly detection for $metric_name..."
    
    # Get 7 days of data
    local end_time=$(date +%s)
    local start_time=$((end_time - 604800))  # 7 days
    
    local response=$(curl -s -G "$PROMETHEUS_URL/api/v1/query_range" \
        --data-urlencode "query=$metric_name" \
        --data-urlencode "start=$start_time" \
        --data-urlencode "end=$end_time" \
        --data-urlencode "step=300")  # 5 minute intervals
    
    # Extract time series
    local data=$(echo "$response" | jq -r '.data.result[0].values[] | "\(.[0]),\(.[1])"' 2>/dev/null || echo "")
    
    if [[ -z "$data" ]]; then
        echo "⚠️  No time series data for $metric_name"
        return 1
    fi
    
    # Use Python for advanced analysis
    python3 << EOF
import sys
import numpy as np
from datetime import datetime

# Parse data
data = """$data"""
timestamps = []
values = []

for line in data.strip().split('\n'):
    if line:
        ts, val = line.split(',')
        timestamps.append(float(ts))
        values.append(float(val))

if len(values) < 10:
    sys.exit(1)

arr = np.array(values)

# Detect outliers using Isolation Forest approach (simplified)
# Calculate rolling statistics
window = min(24, len(arr) // 4)  # 2 hours at 5min intervals
rolling_mean = np.convolve(arr, np.ones(window)/window, mode='valid')
rolling_std = np.array([np.std(arr[max(0, i-window):i+1]) for i in range(len(arr))])

# Calculate anomaly score
anomaly_scores = np.abs(arr - np.pad(rolling_mean, (len(arr)-len(rolling_mean), 0), mode='edge')) / (rolling_std + 1e-6)

# Find anomalies
threshold = np.percentile(anomaly_scores, $sensitivity * 100)
anomalies = np.where(anomaly_scores > threshold)[0]

if len(anomalies) > 0:
    print(f"ANOMALIES_FOUND:{len(anomalies)}")
    for idx in anomalies[-5:]:  # Last 5 anomalies
        ts = datetime.fromtimestamp(timestamps[idx])
        print(f"ANOMALY:{ts.isoformat()}:{values[idx]:.4f}:{anomaly_scores[idx]:.2f}")
else:
    print("NO_ANOMALIES")
EOF
}

###############################################################################
# Pattern-Based Anomaly Detection
###############################################################################

detect_pattern_anomalies() {
    echo "🔎 Pattern-based anomaly detection..."
    
    # Check for unusual patterns
    check_sudden_spike
    check_gradual_degradation
    check_oscillation_patterns
    check_flatline_patterns
}

check_sudden_spike() {
    local metric="rate(http_requests_total[5m])"
    
    # Get current and previous values
    local current=$(query_prometheus "$metric" | jq -r '.data.result[0].value[1]' 2>/dev/null || echo "0")
    sleep 60
    local previous=$(query_prometheus "$metric" | jq -r '.data.result[0].value[1]' 2>/dev/null || echo "0")
    
    # Calculate rate of change
    local change=$(echo "scale=4; ($current - $previous) / ($previous + 0.0001) * 100" | bc)
    
    if (( $(echo "$change > 200" | bc -l) )); then
        echo "🚨 SUDDEN SPIKE detected: ${change}% increase in requests"
        send_anomaly_alert "http_requests" "sudden_spike" "$current" "$previous" "$change"
    fi
}

check_gradual_degradation() {
    local metric="node_memory_MemAvailable_bytes"
    
    # Get 1 hour trend
    local trend=$(curl -s -G "$PROMETHEUS_URL/api/v1/query_range" \
        --data-urlencode "query=$metric" \
        --data-urlencode "start=$(($(date +%s) - 3600))" \
        --data-urlencode "end=$(date +%s)" \
        --data-urlencode "step=300" | \
        jq -r '.data.result[0].values[][1]' | \
        python3 -c "
import sys
import numpy as np

values = [float(line.strip()) for line in sys.stdin if line.strip()]
if len(values) < 2:
    sys.exit(1)

# Linear regression to detect trend
x = np.arange(len(values))
y = np.array(values)
slope = np.polyfit(x, y, 1)[0]

# Check if decreasing
if slope < -1e8:  # Losing 100MB per interval
    print('DEGRADATION')
else:
    print('OK')
" || echo "OK")
    
    if [[ "$trend" == "DEGRADATION" ]]; then
        echo "🚨 GRADUAL DEGRADATION detected: Memory continuously decreasing"
        send_anomaly_alert "memory_available" "degradation" "N/A" "N/A" "continuous_decrease"
    fi
}

check_oscillation_patterns() {
    local metric="node_cpu_seconds_total"
    
    # Detect rapid oscillations (possible instability)
    local values=$(curl -s -G "$PROMETHEUS_URL/api/v1/query_range" \
        --data-urlencode "query=rate($metric[5m])" \
        --data-urlencode "start=$(($(date +%s) - 1800))" \
        --data-urlencode "end=$(date +%s)" \
        --data-urlencode "step=60" | \
        jq -r '.data.result[0].values[][1]' || echo "")
    
    if [[ -n "$values" ]]; then
        local oscillation=$(echo "$values" | python3 -c "
import sys
import numpy as np

values = [float(line.strip()) for line in sys.stdin if line.strip()]
if len(values) < 10:
    sys.exit(1)

# Count zero crossings (sign changes in derivative)
diff = np.diff(values)
signs = np.sign(diff)
crossings = np.sum(np.abs(np.diff(signs))) / 2

# High number of crossings = oscillation
if crossings > len(values) * 0.4:
    print('OSCILLATING')
else:
    print('OK')
" || echo "OK")
        
        if [[ "$oscillation" == "OSCILLATING" ]]; then
            echo "🚨 OSCILLATION detected: CPU usage rapidly fluctuating"
            send_anomaly_alert "cpu_usage" "oscillation" "N/A" "N/A" "rapid_fluctuation"
        fi
    fi
}

check_flatline_patterns() {
    local metric="up{job='node-exporter'}"
    
    # Check if metric is stuck at same value (possible monitoring failure)
    local values=$(curl -s -G "$PROMETHEUS_URL/api/v1/query_range" \
        --data-urlencode "query=$metric" \
        --data-urlencode "start=$(($(date +%s) - 600))" \
        --data-urlencode "end=$(date +%s)" \
        --data-urlencode "step=60" | \
        jq -r '.data.result[0].values[][1]' || echo "")
    
    if [[ -n "$values" ]]; then
        local variance=$(echo "$values" | python3 -c "
import sys
import numpy as np

values = [float(line.strip()) for line in sys.stdin if line.strip()]
if len(values) < 5:
    sys.exit(1)

variance = np.var(values)
print(variance)
" || echo "1")
        
        if (( $(echo "$variance < 0.001" | bc -l) )); then
            echo "🚨 FLATLINE detected: Metric not changing (monitoring issue?)"
            send_anomaly_alert "$metric" "flatline" "N/A" "N/A" "no_variance"
        fi
    fi
}

###############################################################################
# ML-Based Anomaly Detection
###############################################################################

train_anomaly_detector() {
    echo "🤖 Training ML-based anomaly detector..."
    
    python3 << 'EOF'
import numpy as np
import pickle
import requests
import json
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

PROMETHEUS_URL = "http://localhost:9090"
MODEL_DIR = "/var/lib/anomaly-detection"

# Collect training data (7 days)
end_time = int(datetime.now().timestamp())
start_time = end_time - (7 * 24 * 3600)

metrics_to_monitor = [
    'rate(node_cpu_seconds_total{mode="system"}[5m])',
    'node_memory_MemAvailable_bytes',
    'rate(node_disk_io_time_seconds_total[5m])',
    'rate(node_network_receive_bytes_total[5m])',
    'rate(http_requests_total[5m])',
]

all_features = []

for metric in metrics_to_monitor:
    try:
        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query_range",
            params={
                'query': metric,
                'start': start_time,
                'end': end_time,
                'step': '300'
            },
            timeout=30
        )
        
        data = response.json()
        if data['status'] == 'success' and data['data']['result']:
            values = [float(v[1]) for v in data['data']['result'][0]['values']]
            all_features.append(values)
            print(f"Collected {len(values)} samples for {metric}")
    except Exception as e:
        print(f"Error collecting {metric}: {e}")

if not all_features:
    print("No data collected, exiting")
    exit(1)

# Align lengths
min_length = min(len(f) for f in all_features)
features_matrix = np.array([f[:min_length] for f in all_features]).T

# Scale features
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features_matrix)

# Train Isolation Forest
model = IsolationForest(
    contamination=0.05,  # Expect 5% anomalies
    random_state=42,
    n_estimators=100
)

model.fit(features_scaled)

# Save model
with open(f"{MODEL_DIR}/isolation_forest.pkl", 'wb') as f:
    pickle.dump(model, f)

with open(f"{MODEL_DIR}/scaler.pkl", 'wb') as f:
    pickle.dump(scaler, f)

print("✅ Model trained and saved")
print(f"   Features: {features_matrix.shape[1]}")
print(f"   Samples: {features_matrix.shape[0]}")
EOF
}

detect_ml_anomalies() {
    echo "🤖 Running ML-based anomaly detection..."
    
    python3 << 'EOF'
import numpy as np
import pickle
import requests
import json
from datetime import datetime

PROMETHEUS_URL = "http://localhost:9090"
MODEL_DIR = "/var/lib/anomaly-detection"

# Load model
try:
    with open(f"{MODEL_DIR}/isolation_forest.pkl", 'rb') as f:
        model = pickle.load(f)
    
    with open(f"{MODEL_DIR}/scaler.pkl", 'rb') as f:
        scaler = pickle.load(f)
except FileNotFoundError:
    print("Model not found, please train first")
    exit(1)

# Collect current metrics
metrics_to_monitor = [
    'rate(node_cpu_seconds_total{mode="system"}[5m])',
    'node_memory_MemAvailable_bytes',
    'rate(node_disk_io_time_seconds_total[5m])',
    'rate(node_network_receive_bytes_total[5m])',
    'rate(http_requests_total[5m])',
]

current_values = []

for metric in metrics_to_monitor:
    try:
        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={'query': metric},
            timeout=10
        )
        
        data = response.json()
        if data['status'] == 'success' and data['data']['result']:
            value = float(data['data']['result'][0]['value'][1])
            current_values.append(value)
    except Exception as e:
        print(f"Error querying {metric}: {e}")
        current_values.append(0)

if len(current_values) != len(metrics_to_monitor):
    print("Incomplete data")
    exit(1)

# Scale and predict
features = np.array(current_values).reshape(1, -1)
features_scaled = scaler.transform(features)
prediction = model.predict(features_scaled)[0]
anomaly_score = model.score_samples(features_scaled)[0]

if prediction == -1:
    print(f"🚨 ML ANOMALY DETECTED")
    print(f"   Anomaly Score: {anomaly_score:.4f}")
    print(f"   Features: {current_values}")
    exit(0)
else:
    print(f"✅ No anomalies detected (score: {anomaly_score:.4f})")
    exit(1)
EOF
}

###############################################################################
# Correlation Analysis
###############################################################################

analyze_metric_correlations() {
    echo "🔗 Analyzing metric correlations..."
    
    python3 << 'EOF'
import numpy as np
import requests
from datetime import datetime

PROMETHEUS_URL = "http://localhost:9090"

# Key metrics
metrics = {
    'cpu': 'rate(node_cpu_seconds_total[5m])',
    'memory': 'node_memory_MemAvailable_bytes',
    'disk_io': 'rate(node_disk_io_time_seconds_total[5m])',
    'network': 'rate(node_network_receive_bytes_total[5m])',
    'errors': 'rate(http_requests_total{status=~"5.."}[5m])',
}

# Collect last hour
end_time = int(datetime.now().timestamp())
start_time = end_time - 3600

data_matrix = []
metric_names = []

for name, query in metrics.items():
    try:
        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query_range",
            params={
                'query': query,
                'start': start_time,
                'end': end_time,
                'step': '60'
            },
            timeout=30
        )
        
        result = response.json()
        if result['status'] == 'success' and result['data']['result']:
            values = [float(v[1]) for v in result['data']['result'][0]['values']]
            data_matrix.append(values)
            metric_names.append(name)
    except Exception as e:
        print(f"Error: {e}")

if len(data_matrix) < 2:
    print("Insufficient data")
    exit(1)

# Calculate correlation matrix
min_len = min(len(d) for d in data_matrix)
matrix = np.array([d[:min_len] for d in data_matrix])
corr_matrix = np.corrcoef(matrix)

print("\n📊 Correlation Matrix:")
print("     ", "  ".join(f"{n:8s}" for n in metric_names))
for i, name in enumerate(metric_names):
    print(f"{name:8s}", "  ".join(f"{corr_matrix[i,j]:8.3f}" for j in range(len(metric_names))))

# Find high correlations (unusual relationships)
for i in range(len(metric_names)):
    for j in range(i+1, len(metric_names)):
        corr = corr_matrix[i, j]
        if abs(corr) > 0.8:
            print(f"\n⚠️  Strong correlation: {metric_names[i]} ↔ {metric_names[j]} ({corr:.3f})")
EOF
}

###############################################################################
# Alert Management
###############################################################################

log_anomaly() {
    local metric=$1
    local type=$2
    local current=$3
    local baseline=$4
    local score=$5
    
    local timestamp=$(date -Iseconds)
    local log_file="$LOG_DIR/anomalies.log"
    
    echo "$timestamp|$metric|$type|$current|$baseline|$score" >> "$log_file"
}

send_anomaly_alert() {
    local metric=$1
    local type=$2
    local current=$3
    local baseline=$4
    local score=$5
    
    local message=$(cat << EOF
🚨 *Anomaly Detected*

*Metric:* \`$metric\`
*Type:* $type
*Current Value:* $current
*Baseline:* $baseline
*Anomaly Score:* $score

*Timestamp:* $(date -Iseconds)
*Host:* $(hostname)

*Recommended Actions:*
• Review system logs
• Check for resource constraints
• Verify recent deployments
• Escalate if persists
EOF
)
    
    # Send via Telegram bot
    if [[ -f /opt/telegram-bot/send-alert.sh ]]; then
        /opt/telegram-bot/send-alert.sh "Anomaly Alert" "$message"
    fi
    
    # Send to webhook if configured
    if [[ -n "$ALERT_WEBHOOK" ]]; then
        curl -X POST "$ALERT_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{\"text\":\"$message\"}" \
            --max-time 10 2>/dev/null || true
    fi
}

###############################################################################
# Utility Functions
###############################################################################

query_prometheus() {
    local query=$1
    local time=${2:-$(date +%s)}
    
    curl -s -G "$PROMETHEUS_URL/api/v1/query" \
        --data-urlencode "query=$query" \
        --data-urlencode "time=$time"
}

###############################################################################
# Continuous Monitoring
###############################################################################

run_continuous_monitoring() {
    echo "🔄 Starting continuous anomaly detection..."
    
    while true; do
        echo ""
        echo "=== Anomaly Detection Cycle: $(date -Iseconds) ==="
        
        # Statistical detection
        detect_statistical_anomalies "rate(http_requests_total[5m])" 60
        detect_statistical_anomalies "node_memory_MemAvailable_bytes" 60
        detect_statistical_anomalies "rate(node_disk_io_time_seconds_total[5m])" 60
        
        # Pattern detection
        detect_pattern_anomalies
        
        # ML detection
        if [[ -f "$MODEL_DIR/isolation_forest.pkl" ]]; then
            detect_ml_anomalies
        fi
        
        # Correlation analysis (every 10 minutes)
        if (( $(date +%M) % 10 == 0 )); then
            analyze_metric_correlations
        fi
        
        echo "✅ Cycle complete, sleeping 60s..."
        sleep 60
    done
}

###############################################################################
# Main Execution
###############################################################################

main() {
    echo "🔍 Anomaly Detection System v11.0"
    echo "================================="
    echo ""
    
    case "${1:-monitor}" in
        train)
            train_anomaly_detector
            ;;
        detect)
            detect_statistical_anomalies "${2:-rate(http_requests_total[5m])}" 60
            ;;
        ml)
            detect_ml_anomalies
            ;;
        patterns)
            detect_pattern_anomalies
            ;;
        correlations)
            analyze_metric_correlations
            ;;
        monitor)
            run_continuous_monitoring
            ;;
        *)
            echo "Usage: $0 {train|detect|ml|patterns|correlations|monitor}"
            exit 1
            ;;
    esac
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
