#!/usr/bin/env bash

###############################################################################
# ADVANCED HEALTH CHECK SYSTEM v11.0
# Comprehensive health monitoring with predictive analytics
###############################################################################

set -euo pipefail

# Health check configuration
HEALTH_CHECK_INTERVAL=60  # seconds
HEALTH_CHECK_TIMEOUT=10
HEALTH_CHECK_LOG="/var/log/health-checks.log"
HEALTH_METRICS="/var/lib/health-metrics.db"

# Thresholds
CPU_THRESHOLD=80
MEMORY_THRESHOLD=85
DISK_THRESHOLD=90
LOAD_THRESHOLD=5.0
NETWORK_ERROR_THRESHOLD=100

###############################################################################
# Core Health Checks
###############################################################################

check_system_health() {
    local timestamp=$(date -Iseconds)
    local health_score=100
    local issues=()
    
    # CPU check
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    if (( $(echo "$cpu_usage > $CPU_THRESHOLD" | bc -l) )); then
        health_score=$((health_score - 20))
        issues+=("HIGH_CPU:$cpu_usage%")
    fi
    
    # Memory check
    local mem_usage=$(free | grep Mem | awk '{printf "%.0f", ($3/$2) * 100}')
    if [[ $mem_usage -gt $MEMORY_THRESHOLD ]]; then
        health_score=$((health_score - 20))
        issues+=("HIGH_MEMORY:$mem_usage%")
    fi
    
    # Disk check
    local disk_usage=$(df -h / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    if [[ $disk_usage -gt $DISK_THRESHOLD ]]; then
        health_score=$((health_score - 25))
        issues+=("HIGH_DISK:$disk_usage%")
    fi
    
    # Load average check
    local load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ',')
    if (( $(echo "$load_avg > $LOAD_THRESHOLD" | bc -l) )); then
        health_score=$((health_score - 15))
        issues+=("HIGH_LOAD:$load_avg")
    fi
    
    # Service checks
    check_critical_services || {
        health_score=$((health_score - 20))
        issues+=("SERVICES_DOWN")
    }
    
    # Network check
    check_network_health || {
        health_score=$((health_score - 10))
        issues+=("NETWORK_ISSUES")
    }
    
    # Log result
    log_health_result "$timestamp" "$health_score" "${issues[@]}"
    
    # Return status
    if [[ $health_score -ge 90 ]]; then
        return 0  # Healthy
    elif [[ $health_score -ge 70 ]]; then
        return 1  # Warning
    else
        return 2  # Critical
    fi
}

check_critical_services() {
    local services=("nginx" "postgresql" "redis" "prometheus")
    local failed=0
    
    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service" 2>/dev/null; then
            continue
        else
            ((failed++))
        fi
    done
    
    return $failed
}

check_network_health() {
    # Check network connectivity
    ping -c 1 -W 2 8.8.8.8 &>/dev/null || return 1
    
    # Check DNS resolution
    nslookup google.com &>/dev/null || return 1
    
    # Check for network errors
    local errors=$(netstat -i | grep -v "Kernel" | grep -v "Iface" | awk '{sum+=$4+$8} END {print sum}')
    if [[ $errors -gt $NETWORK_ERROR_THRESHOLD ]]; then
        return 1
    fi
    
    return 0
}

###############################################################################
# Advanced Health Checks
###############################################################################

check_application_health() {
    local app_health=100
    
    # Bot health
    if ! pgrep -f "devops_manager_bot.py" &>/dev/null; then
        app_health=$((app_health - 50))
    fi
    
    # Database health
    local db_connections=$(psql -U postgres -t -c "SELECT count(*) FROM pg_stat_activity;" 2>/dev/null || echo "0")
    if [[ $db_connections -gt 100 ]]; then
        app_health=$((app_health - 20))
    fi
    
    # Redis health
    local redis_memory=$(redis-cli info memory 2>/dev/null | grep "used_memory_human" | cut -d':' -f2 | tr -d '\r\n')
    if [[ -z "$redis_memory" ]]; then
        app_health=$((app_health - 30))
    fi
    
    echo $app_health
}

check_security_health() {
    local security_score=100
    
    # Check firewall
    if ! iptables -L &>/dev/null; then
        security_score=$((security_score - 40))
    fi
    
    # Check fail2ban
    if ! systemctl is-active --quiet fail2ban 2>/dev/null; then
        security_score=$((security_score - 20))
    fi
    
    # Check SSH config
    if grep -q "^PermitRootLogin yes" /etc/ssh/sshd_config 2>/dev/null; then
        security_score=$((security_score - 30))
    fi
    
    # Check for security updates
    local security_updates=$(apt list --upgradable 2>/dev/null | grep -i security | wc -l)
    if [[ $security_updates -gt 10 ]]; then
        security_score=$((security_score - 10))
    fi
    
    echo $security_score
}

###############################################################################
# Predictive Analytics
###############################################################################

predict_resource_exhaustion() {
    # Analyze trend over last 24 hours
    local current_disk=$(df -h / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    local disk_24h_ago=$(sqlite3 "$HEALTH_METRICS" "SELECT disk_usage FROM metrics WHERE timestamp > datetime('now', '-24 hours') ORDER BY timestamp ASC LIMIT 1;" 2>/dev/null || echo "$current_disk")
    
    local disk_growth=$((current_disk - disk_24h_ago))
    
    if [[ $disk_growth -gt 5 ]]; then
        local days_until_full=$(( (100 - current_disk) / disk_growth ))
        if [[ $days_until_full -lt 7 ]]; then
            echo "WARNING: Disk will be full in approximately $days_until_full days"
            send_alert "Disk space prediction" "Disk will be full in $days_until_full days. Current: ${current_disk}%"
        fi
    fi
}

analyze_performance_trends() {
    # Get CPU usage trend
    local avg_cpu=$(sqlite3 "$HEALTH_METRICS" "SELECT AVG(cpu_usage) FROM metrics WHERE timestamp > datetime('now', '-1 hour');" 2>/dev/null || echo "0")
    
    # Get memory usage trend
    local avg_mem=$(sqlite3 "$HEALTH_METRICS" "SELECT AVG(memory_usage) FROM metrics WHERE timestamp > datetime('now', '-1 hour');" 2>/dev/null || echo "0")
    
    # Detect anomalies
    local current_cpu=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    
    # If current CPU is 50% higher than average, it's an anomaly
    if (( $(echo "$current_cpu > $avg_cpu * 1.5" | bc -l) )); then
        send_alert "CPU Anomaly Detected" "Current: ${current_cpu}%, Avg: ${avg_cpu}%"
    fi
}

###############################################################################
# Self-Healing
###############################################################################

auto_remediate() {
    local issue_type=$1
    
    case $issue_type in
        HIGH_MEMORY)
            # Clear caches
            sync && echo 3 > /proc/sys/vm/drop_caches
            # Restart memory-hungry services
            systemctl restart redis 2>/dev/null || true
            ;;
        HIGH_DISK)
            # Clean old logs
            find /var/log -name "*.log" -mtime +30 -delete
            # Clean package cache
            apt-get clean 2>/dev/null || true
            ;;
        SERVICES_DOWN)
            # Restart critical services
            for service in nginx postgresql redis; do
                if ! systemctl is-active --quiet "$service" 2>/dev/null; then
                    systemctl restart "$service" 2>/dev/null || true
                fi
            done
            ;;
        HIGH_LOAD)
            # Kill non-essential processes
            pkill -TERM -f "some-non-essential-process" 2>/dev/null || true
            ;;
    esac
}

###############################################################################
# Metrics Storage
###############################################################################

store_metrics() {
    local timestamp=$(date -Iseconds)
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    local mem_usage=$(free | grep Mem | awk '{printf "%.0f", ($3/$2) * 100}')
    local disk_usage=$(df -h / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    local load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ',')
    
    # Create metrics database if not exists
    if [[ ! -f "$HEALTH_METRICS" ]]; then
        sqlite3 "$HEALTH_METRICS" "CREATE TABLE metrics (
            timestamp TEXT,
            cpu_usage REAL,
            memory_usage REAL,
            disk_usage INTEGER,
            load_average REAL
        );"
    fi
    
    # Insert metrics
    sqlite3 "$HEALTH_METRICS" "INSERT INTO metrics VALUES (
        '$timestamp',
        $cpu_usage,
        $mem_usage,
        $disk_usage,
        $load_avg
    );"
    
    # Clean old data (keep last 30 days)
    sqlite3 "$HEALTH_METRICS" "DELETE FROM metrics WHERE timestamp < datetime('now', '-30 days');"
}

###############################################################################
# Logging & Alerting
###############################################################################

log_health_result() {
    local timestamp=$1
    local score=$2
    shift 2
    local issues=("$@")
    
    local status="HEALTHY"
    if [[ $score -lt 90 ]]; then
        status="WARNING"
    fi
    if [[ $score -lt 70 ]]; then
        status="CRITICAL"
    fi
    
    # JSON log
    cat >> "$HEALTH_CHECK_LOG" << EOF
{
  "timestamp": "$timestamp",
  "health_score": $score,
  "status": "$status",
  "issues": [$(printf '"%s",' "${issues[@]}" | sed 's/,$//')],
  "system": {
    "cpu": "$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%",
    "memory": "$(free | grep Mem | awk '{printf "%.0f", ($3/$2) * 100}')%",
    "disk": "$(df -h / | tail -1 | awk '{print $5}')"
  }
}
EOF
    
    # Send alert if critical
    if [[ $score -lt 70 ]]; then
        send_alert "Health Check CRITICAL" "Score: $score. Issues: ${issues[*]}"
    fi
}

send_alert() {
    local title=$1
    local message=$2
    
    # Telegram alert (if bot configured)
    if [[ -f /opt/telegram-bot/send-alert.sh ]]; then
        bash /opt/telegram-bot/send-alert.sh "$title" "$message"
    fi
    
    # Email alert (if configured)
    if command -v mail &>/dev/null && [[ -n "${ALERT_EMAIL:-}" ]]; then
        echo "$message" | mail -s "$title" "$ALERT_EMAIL"
    fi
    
    # Syslog
    logger -t health-check -p daemon.crit "$title: $message"
}

###############################################################################
# Dashboard Export
###############################################################################

export_health_dashboard() {
    local output_file="/var/www/html/health-dashboard.html"
    
    cat > "$output_file" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>System Health Dashboard</title>
    <meta http-equiv="refresh" content="30">
    <style>
        body { font-family: Arial; background: #1a1a1a; color: #fff; padding: 20px; }
        .metric { background: #2a2a2a; padding: 15px; margin: 10px; border-radius: 5px; }
        .healthy { border-left: 5px solid #00ff00; }
        .warning { border-left: 5px solid #ffaa00; }
        .critical { border-left: 5px solid #ff0000; }
        h2 { margin-top: 0; }
    </style>
</head>
<body>
    <h1>🏥 System Health Dashboard</h1>
    <div id="metrics"></div>
    <script>
        // Auto-refresh metrics
        setInterval(() => location.reload(), 30000);
    </script>
</body>
</html>
EOF
    
    chmod 644 "$output_file"
}

###############################################################################
# Main Health Check Loop
###############################################################################

run_health_checks() {
    while true; do
        # Run checks
        check_system_health
        local system_status=$?
        
        local app_health=$(check_application_health)
        local security_health=$(check_security_health)
        
        # Store metrics
        store_metrics
        
        # Predictive analytics
        predict_resource_exhaustion
        analyze_performance_trends
        
        # Auto-remediation for critical issues
        if [[ $system_status -eq 2 ]]; then
            auto_remediate "CRITICAL"
        fi
        
        # Export dashboard
        export_health_dashboard
        
        # Sleep
        sleep $HEALTH_CHECK_INTERVAL
    done
}

# Run as daemon
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    run_health_checks
fi
