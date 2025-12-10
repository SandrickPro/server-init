#!/usr/bin/env bash

###############################################################################
# ZERO TRUST ADVANCED v11.0 (ZTNA 2.0)
# Advanced Zero Trust Network Access with behavioral analytics
###############################################################################

set -euo pipefail

# Configuration
ZTNA_VERSION="2.0"
TRUST_SCORE_THRESHOLD=75
SESSION_TIMEOUT=3600
MAX_FAILED_ATTEMPTS=3
DEVICE_REGISTRY="/var/lib/ztna/devices.db"
SESSION_STORE="/var/lib/ztna/sessions"
AUDIT_LOG="/var/log/ztna/audit.log"

mkdir -p "$(dirname "$DEVICE_REGISTRY")" "$SESSION_STORE" "$(dirname "$AUDIT_LOG")"

###############################################################################
# Device Trust Scoring
###############################################################################

calculate_device_trust_score() {
    local device_id=$1
    local trust_score=100
    
    echo "🔐 Calculating trust score for device: $device_id"
    
    # Factor 1: OS Security Posture (0-30 points)
    local os_score=$(check_os_security_posture "$device_id")
    trust_score=$((trust_score - (30 - os_score)))
    
    # Factor 2: Patch Level (0-20 points)
    local patch_score=$(check_patch_level "$device_id")
    trust_score=$((trust_score - (20 - patch_score)))
    
    # Factor 3: Endpoint Protection (0-20 points)
    local epp_score=$(check_endpoint_protection "$device_id")
    trust_score=$((trust_score - (20 - epp_score)))
    
    # Factor 4: Device Compliance (0-15 points)
    local compliance_score=$(check_device_compliance "$device_id")
    trust_score=$((trust_score - (15 - compliance_score)))
    
    # Factor 5: Behavioral Analysis (0-15 points)
    local behavior_score=$(analyze_device_behavior "$device_id")
    trust_score=$((trust_score - (15 - behavior_score)))
    
    # Store score
    sqlite3 "$DEVICE_REGISTRY" "
        INSERT OR REPLACE INTO trust_scores (device_id, score, timestamp)
        VALUES ('$device_id', $trust_score, datetime('now'));
    "
    
    echo "   Trust Score: $trust_score/100"
    echo "   OS Security: $os_score/30"
    echo "   Patch Level: $patch_score/20"
    echo "   EPP Status: $epp_score/20"
    echo "   Compliance: $compliance_score/15"
    echo "   Behavior: $behavior_score/15"
    
    echo "$trust_score"
}

check_os_security_posture() {
    local device_id=$1
    local score=30
    
    # Check firewall status
    if ! device_has_firewall_enabled "$device_id"; then
        score=$((score - 10))
    fi
    
    # Check disk encryption
    if ! device_has_disk_encryption "$device_id"; then
        score=$((score - 10))
    fi
    
    # Check secure boot
    if ! device_has_secure_boot "$device_id"; then
        score=$((score - 5))
    fi
    
    # Check password policy
    if ! device_has_strong_password_policy "$device_id"; then
        score=$((score - 5))
    fi
    
    echo "$score"
}

check_patch_level() {
    local device_id=$1
    local score=20
    
    # Get last update timestamp
    local last_update=$(sqlite3 "$DEVICE_REGISTRY" "
        SELECT last_update FROM devices WHERE device_id='$device_id';
    " || echo "0")
    
    if [[ "$last_update" == "0" ]]; then
        return
    fi
    
    local days_since_update=$(( ($(date +%s) - last_update) / 86400 ))
    
    if [[ $days_since_update -gt 30 ]]; then
        score=$((score - 15))
    elif [[ $days_since_update -gt 14 ]]; then
        score=$((score - 10))
    elif [[ $days_since_update -gt 7 ]]; then
        score=$((score - 5))
    fi
    
    echo "$score"
}

check_endpoint_protection() {
    local device_id=$1
    local score=20
    
    # Check antivirus status
    if ! device_has_active_antivirus "$device_id"; then
        score=$((score - 10))
    fi
    
    # Check EDR agent
    if ! device_has_edr_agent "$device_id"; then
        score=$((score - 5))
    fi
    
    # Check recent malware scan
    if ! device_has_recent_scan "$device_id"; then
        score=$((score - 5))
    fi
    
    echo "$score"
}

check_device_compliance() {
    local device_id=$1
    local score=15
    
    # Check if device is registered
    if ! is_device_registered "$device_id"; then
        score=$((score - 15))
        echo "$score"
        return
    fi
    
    # Check certificate validity
    if ! device_has_valid_certificate "$device_id"; then
        score=$((score - 5))
    fi
    
    # Check MDM enrollment
    if ! device_is_mdm_enrolled "$device_id"; then
        score=$((score - 5))
    fi
    
    # Check geo-location compliance
    if ! device_in_allowed_location "$device_id"; then
        score=$((score - 5))
    fi
    
    echo "$score"
}

analyze_device_behavior() {
    local device_id=$1
    local score=15
    
    # Get behavior history
    local failed_attempts=$(sqlite3 "$DEVICE_REGISTRY" "
        SELECT COUNT(*) FROM auth_attempts 
        WHERE device_id='$device_id' AND success=0 
        AND timestamp > datetime('now', '-1 hour');
    " || echo "0")
    
    local unusual_locations=$(sqlite3 "$DEVICE_REGISTRY" "
        SELECT COUNT(DISTINCT location) FROM sessions 
        WHERE device_id='$device_id' 
        AND timestamp > datetime('now', '-24 hours');
    " || echo "0")
    
    local unusual_hours=$(sqlite3 "$DEVICE_REGISTRY" "
        SELECT COUNT(*) FROM sessions 
        WHERE device_id='$device_id' 
        AND cast(strftime('%H', timestamp) as integer) NOT BETWEEN 8 AND 18
        AND timestamp > datetime('now', '-7 days');
    " || echo "0")
    
    # Deduct points for suspicious behavior
    if [[ $failed_attempts -gt 5 ]]; then
        score=$((score - 10))
    elif [[ $failed_attempts -gt 2 ]]; then
        score=$((score - 5))
    fi
    
    if [[ $unusual_locations -gt 3 ]]; then
        score=$((score - 3))
    fi
    
    if [[ $unusual_hours -gt 10 ]]; then
        score=$((score - 2))
    fi
    
    echo "$score"
}

###############################################################################
# Continuous Authentication
###############################################################################

create_session() {
    local user_id=$1
    local device_id=$2
    local ip_address=$3
    local location=$4
    
    echo "🔑 Creating ZTNA session..."
    
    # Calculate trust score
    local trust_score=$(calculate_device_trust_score "$device_id")
    
    if [[ $trust_score -lt $TRUST_SCORE_THRESHOLD ]]; then
        echo "❌ Access denied: Trust score $trust_score < threshold $TRUST_SCORE_THRESHOLD"
        log_auth_attempt "$user_id" "$device_id" "denied" "low_trust_score"
        return 1
    fi
    
    # Generate session token
    local session_id=$(openssl rand -hex 32)
    local session_start=$(date +%s)
    local session_expiry=$((session_start + SESSION_TIMEOUT))
    
    # Store session
    cat > "$SESSION_STORE/$session_id.json" << EOF
{
    "session_id": "$session_id",
    "user_id": "$user_id",
    "device_id": "$device_id",
    "ip_address": "$ip_address",
    "location": "$location",
    "trust_score": $trust_score,
    "start_time": $session_start,
    "expiry_time": $session_expiry,
    "last_activity": $session_start,
    "risk_level": "low"
}
EOF
    
    # Log to database
    sqlite3 "$DEVICE_REGISTRY" "
        INSERT INTO sessions (session_id, user_id, device_id, ip_address, location, trust_score, timestamp)
        VALUES ('$session_id', '$user_id', '$device_id', '$ip_address', '$location', $trust_score, datetime('now'));
    "
    
    log_auth_attempt "$user_id" "$device_id" "success" "session_created"
    
    echo "✅ Session created: $session_id"
    echo "   Trust Score: $trust_score"
    echo "   Expires: $(date -d "@$session_expiry")"
    
    echo "$session_id"
}

validate_session() {
    local session_id=$1
    
    if [[ ! -f "$SESSION_STORE/$session_id.json" ]]; then
        echo "❌ Session not found"
        return 1
    fi
    
    # Parse session data
    local session_data=$(cat "$SESSION_STORE/$session_id.json")
    local expiry_time=$(echo "$session_data" | jq -r '.expiry_time')
    local device_id=$(echo "$session_data" | jq -r '.device_id')
    local current_time=$(date +%s)
    
    # Check expiration
    if [[ $current_time -gt $expiry_time ]]; then
        echo "❌ Session expired"
        revoke_session "$session_id" "expired"
        return 1
    fi
    
    # Re-evaluate trust score periodically (every 5 minutes)
    local last_activity=$(echo "$session_data" | jq -r '.last_activity')
    if [[ $((current_time - last_activity)) -gt 300 ]]; then
        local new_trust_score=$(calculate_device_trust_score "$device_id")
        
        if [[ $new_trust_score -lt $TRUST_SCORE_THRESHOLD ]]; then
            echo "⚠️  Trust score degraded to $new_trust_score"
            revoke_session "$session_id" "trust_degradation"
            return 1
        fi
        
        # Update session with new trust score
        echo "$session_data" | jq ".trust_score = $new_trust_score | .last_activity = $current_time" > "$SESSION_STORE/$session_id.json"
    fi
    
    echo "✅ Session valid"
    return 0
}

revoke_session() {
    local session_id=$1
    local reason=$2
    
    echo "🚫 Revoking session $session_id (reason: $reason)"
    
    if [[ -f "$SESSION_STORE/$session_id.json" ]]; then
        local session_data=$(cat "$SESSION_STORE/$session_id.json")
        local user_id=$(echo "$session_data" | jq -r '.user_id')
        local device_id=$(echo "$session_data" | jq -r '.device_id')
        
        # Archive session
        mkdir -p "$SESSION_STORE/revoked"
        mv "$SESSION_STORE/$session_id.json" "$SESSION_STORE/revoked/"
        
        # Log revocation
        sqlite3 "$DEVICE_REGISTRY" "
            UPDATE sessions SET revoked=1, revoked_reason='$reason', revoked_at=datetime('now')
            WHERE session_id='$session_id';
        "
        
        log_audit "session_revoked" "$user_id" "$device_id" "$reason"
    fi
}

###############################################################################
# Micro-Segmentation
###############################################################################

create_network_policy() {
    local namespace=$1
    local app_label=$2
    local allowed_sources=$3
    
    echo "🔒 Creating micro-segmentation policy for $namespace/$app_label"
    
    cat > "/tmp/network-policy-$app_label.yaml" << EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ztna-policy-$app_label
  namespace: $namespace
spec:
  podSelector:
    matchLabels:
      app: $app_label
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          ztna-enabled: "true"
    - podSelector:
        matchLabels:
          ztna-verified: "true"
    ports:
    - protocol: TCP
      port: 443
  egress:
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 443
    - protocol: TCP
      port: 5432  # PostgreSQL
    - protocol: TCP
      port: 6379  # Redis
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: UDP
      port: 53  # DNS
EOF
    
    kubectl apply -f "/tmp/network-policy-$app_label.yaml"
    rm "/tmp/network-policy-$app_label.yaml"
    
    echo "✅ Network policy created"
}

apply_microsegmentation() {
    echo "🔐 Applying micro-segmentation policies..."
    
    # Get all namespaces
    local namespaces=$(kubectl get namespaces -o json | jq -r '.items[].metadata.name')
    
    for namespace in $namespaces; do
        if [[ "$namespace" =~ ^(kube-system|kube-public|kube-node-lease)$ ]]; then
            continue
        fi
        
        # Get all deployments in namespace
        local deployments=$(kubectl get deployments -n "$namespace" -o json | jq -r '.items[].metadata.name')
        
        for deployment in $deployments; do
            # Get app label
            local app_label=$(kubectl get deployment "$deployment" -n "$namespace" -o json | \
                jq -r '.spec.template.metadata.labels.app // .metadata.name')
            
            create_network_policy "$namespace" "$app_label" ""
        done
    done
    
    echo "✅ Micro-segmentation applied"
}

###############################################################################
# Behavioral Analytics
###############################################################################

analyze_user_behavior() {
    local user_id=$1
    
    echo "📊 Analyzing behavior for user: $user_id"
    
    # Get baseline behavior
    local baseline_login_hours=$(sqlite3 "$DEVICE_REGISTRY" "
        SELECT AVG(cast(strftime('%H', timestamp) as integer)) FROM sessions
        WHERE user_id='$user_id' AND timestamp > datetime('now', '-30 days')
        GROUP BY date(timestamp);
    " || echo "12")
    
    local baseline_locations=$(sqlite3 "$DEVICE_REGISTRY" "
        SELECT GROUP_CONCAT(DISTINCT location) FROM sessions
        WHERE user_id='$user_id' AND timestamp > datetime('now', '-30 days');
    " || echo "")
    
    local baseline_devices=$(sqlite3 "$DEVICE_REGISTRY" "
        SELECT GROUP_CONCAT(DISTINCT device_id) FROM sessions
        WHERE user_id='$user_id' AND timestamp > datetime('now', '-30 days');
    " || echo "")
    
    # Get recent activity
    local recent_sessions=$(sqlite3 "$DEVICE_REGISTRY" "
        SELECT session_id, device_id, location, strftime('%H', timestamp) as hour
        FROM sessions
        WHERE user_id='$user_id' AND timestamp > datetime('now', '-24 hours');
    ")
    
    # Detect anomalies
    local anomalies=()
    
    while IFS='|' read -r session_id device_id location hour; do
        # Check for unusual time
        local time_diff=$((hour - baseline_login_hours))
        if [[ ${time_diff#-} -gt 4 ]]; then
            anomalies+=("Unusual login time: ${hour}:00 (baseline: ${baseline_login_hours}:00)")
        fi
        
        # Check for new location
        if [[ ! "$baseline_locations" =~ $location ]]; then
            anomalies+=("New location detected: $location")
        fi
        
        # Check for new device
        if [[ ! "$baseline_devices" =~ $device_id ]]; then
            anomalies+=("New device detected: $device_id")
        fi
    done <<< "$recent_sessions"
    
    if [[ ${#anomalies[@]} -gt 0 ]]; then
        echo "⚠️  Behavioral anomalies detected:"
        for anomaly in "${anomalies[@]}"; do
            echo "   - $anomaly"
        done
        
        # Send alert
        send_behavioral_alert "$user_id" "${anomalies[@]}"
        
        return 1
    else
        echo "✅ No behavioral anomalies"
        return 0
    fi
}

send_behavioral_alert() {
    local user_id=$1
    shift
    local anomalies=("$@")
    
    local message="⚠️ *Behavioral Anomaly Alert*\n\n"
    message+="User: \`$user_id\`\n"
    message+="Detected Anomalies:\n"
    
    for anomaly in "${anomalies[@]}"; do
        message+="• $anomaly\n"
    done
    
    message+="\nRecommended Action: Verify user identity"
    
    if [[ -f /opt/telegram-bot/send-alert.sh ]]; then
        /opt/telegram-bot/send-alert.sh "Behavioral Anomaly" "$message"
    fi
}

###############################################################################
# Session Recording & Audit
###############################################################################

start_session_recording() {
    local session_id=$1
    local record_dir="/var/lib/ztna/recordings/$session_id"
    
    mkdir -p "$record_dir"
    
    # Start recording (simplified - would use proper session recording tool)
    echo "📹 Session recording started: $session_id"
    echo "$(date -Iseconds)|session_start|$session_id" >> "$record_dir/events.log"
}

log_session_event() {
    local session_id=$1
    local event_type=$2
    local event_data=$3
    
    local record_dir="/var/lib/ztna/recordings/$session_id"
    
    if [[ -d "$record_dir" ]]; then
        echo "$(date -Iseconds)|$event_type|$event_data" >> "$record_dir/events.log"
    fi
}

stop_session_recording() {
    local session_id=$1
    local record_dir="/var/lib/ztna/recordings/$session_id"
    
    if [[ -d "$record_dir" ]]; then
        echo "$(date -Iseconds)|session_end|$session_id" >> "$record_dir/events.log"
        echo "📹 Session recording stopped: $session_id"
        
        # Compress recording
        tar -czf "$record_dir.tar.gz" -C "$(dirname "$record_dir")" "$(basename "$record_dir")"
        rm -rf "$record_dir"
    fi
}

###############################################################################
# Device Helper Functions
###############################################################################

device_has_firewall_enabled() {
    local device_id=$1
    # Query device registry
    local firewall_status=$(sqlite3 "$DEVICE_REGISTRY" "
        SELECT firewall_enabled FROM devices WHERE device_id='$device_id';
    " || echo "0")
    [[ "$firewall_status" == "1" ]]
}

device_has_disk_encryption() {
    local device_id=$1
    local encryption_status=$(sqlite3 "$DEVICE_REGISTRY" "
        SELECT disk_encrypted FROM devices WHERE device_id='$device_id';
    " || echo "0")
    [[ "$encryption_status" == "1" ]]
}

device_has_secure_boot() {
    local device_id=$1
    local secure_boot=$(sqlite3 "$DEVICE_REGISTRY" "
        SELECT secure_boot FROM devices WHERE device_id='$device_id';
    " || echo "0")
    [[ "$secure_boot" == "1" ]]
}

device_has_strong_password_policy() {
    local device_id=$1
    local password_policy=$(sqlite3 "$DEVICE_REGISTRY" "
        SELECT strong_password_policy FROM devices WHERE device_id='$device_id';
    " || echo "0")
    [[ "$password_policy" == "1" ]]
}

device_has_active_antivirus() {
    local device_id=$1
    local av_status=$(sqlite3 "$DEVICE_REGISTRY" "
        SELECT antivirus_active FROM devices WHERE device_id='$device_id';
    " || echo "0")
    [[ "$av_status" == "1" ]]
}

device_has_edr_agent() {
    local device_id=$1
    local edr_status=$(sqlite3 "$DEVICE_REGISTRY" "
        SELECT edr_agent FROM devices WHERE device_id='$device_id';
    " || echo "0")
    [[ "$edr_status" == "1" ]]
}

device_has_recent_scan() {
    local device_id=$1
    local last_scan=$(sqlite3 "$DEVICE_REGISTRY" "
        SELECT last_scan FROM devices WHERE device_id='$device_id';
    " || echo "0")
    
    if [[ "$last_scan" == "0" ]]; then
        return 1
    fi
    
    local days_since_scan=$(( ($(date +%s) - last_scan) / 86400 ))
    [[ $days_since_scan -le 7 ]]
}

is_device_registered() {
    local device_id=$1
    local count=$(sqlite3 "$DEVICE_REGISTRY" "
        SELECT COUNT(*) FROM devices WHERE device_id='$device_id';
    " || echo "0")
    [[ "$count" -gt 0 ]]
}

device_has_valid_certificate() {
    local device_id=$1
    local cert_expiry=$(sqlite3 "$DEVICE_REGISTRY" "
        SELECT cert_expiry FROM devices WHERE device_id='$device_id';
    " || echo "0")
    
    if [[ "$cert_expiry" == "0" ]]; then
        return 1
    fi
    
    [[ $(date +%s) -lt $cert_expiry ]]
}

device_is_mdm_enrolled() {
    local device_id=$1
    local mdm_status=$(sqlite3 "$DEVICE_REGISTRY" "
        SELECT mdm_enrolled FROM devices WHERE device_id='$device_id';
    " || echo "0")
    [[ "$mdm_status" == "1" ]]
}

device_in_allowed_location() {
    local device_id=$1
    # Simplified - would check against geo-fence
    return 0
}

###############################################################################
# Logging & Audit
###############################################################################

log_auth_attempt() {
    local user_id=$1
    local device_id=$2
    local result=$3
    local reason=$4
    
    sqlite3 "$DEVICE_REGISTRY" "
        INSERT INTO auth_attempts (user_id, device_id, success, reason, timestamp)
        VALUES ('$user_id', '$device_id', $([ "$result" == "success" ] && echo "1" || echo "0"), '$reason', datetime('now'));
    "
    
    log_audit "auth_attempt" "$user_id" "$device_id" "$result:$reason"
}

log_audit() {
    local event_type=$1
    local user_id=$2
    local device_id=$3
    local details=$4
    
    local timestamp=$(date -Iseconds)
    echo "$timestamp|$event_type|$user_id|$device_id|$details" >> "$AUDIT_LOG"
}

###############################################################################
# Database Initialization
###############################################################################

init_database() {
    echo "💾 Initializing ZTNA database..."
    
    sqlite3 "$DEVICE_REGISTRY" << 'EOF'
CREATE TABLE IF NOT EXISTS devices (
    device_id TEXT PRIMARY KEY,
    user_id TEXT,
    firewall_enabled INTEGER DEFAULT 0,
    disk_encrypted INTEGER DEFAULT 0,
    secure_boot INTEGER DEFAULT 0,
    strong_password_policy INTEGER DEFAULT 0,
    antivirus_active INTEGER DEFAULT 0,
    edr_agent INTEGER DEFAULT 0,
    mdm_enrolled INTEGER DEFAULT 0,
    last_update INTEGER DEFAULT 0,
    last_scan INTEGER DEFAULT 0,
    cert_expiry INTEGER DEFAULT 0,
    registered_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS trust_scores (
    device_id TEXT,
    score INTEGER,
    timestamp TEXT,
    PRIMARY KEY (device_id, timestamp)
);

CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT,
    device_id TEXT,
    ip_address TEXT,
    location TEXT,
    trust_score INTEGER,
    timestamp TEXT,
    revoked INTEGER DEFAULT 0,
    revoked_reason TEXT,
    revoked_at TEXT
);

CREATE TABLE IF NOT EXISTS auth_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    device_id TEXT,
    success INTEGER,
    reason TEXT,
    timestamp TEXT
);

CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_device ON sessions(device_id);
CREATE INDEX IF NOT EXISTS idx_auth_device ON auth_attempts(device_id, timestamp);
EOF
    
    echo "✅ Database initialized"
}

###############################################################################
# Main Setup
###############################################################################

setup_ztna_advanced() {
    echo "🔐 Setting up Zero Trust Advanced (ZTNA 2.0)..."
    echo "Version: $ZTNA_VERSION"
    echo ""
    
    # Initialize database
    init_database
    
    # Apply micro-segmentation
    apply_microsegmentation
    
    echo ""
    echo "✅ ZTNA 2.0 setup complete!"
    echo ""
    echo "📊 Configuration:"
    echo "   - Trust Score Threshold: $TRUST_SCORE_THRESHOLD/100"
    echo "   - Session Timeout: $SESSION_TIMEOUT seconds"
    echo "   - Max Failed Attempts: $MAX_FAILED_ATTEMPTS"
    echo "   - Device Registry: $DEVICE_REGISTRY"
    echo "   - Audit Log: $AUDIT_LOG"
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    setup_ztna_advanced
fi
