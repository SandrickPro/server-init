#!/usr/bin/env bats

# Integration tests for Enterprise Server Deploy v9.0
# Tests end-to-end workflows and module interactions

load test-helper

setup() {
    export TEST_DIR="/tmp/enterprise-test-$$"
    export CONFIG_FILE="$TEST_DIR/enterprise-config.yaml"
    mkdir -p "$TEST_DIR"
    
    # Create test config
    cat > "$CONFIG_FILE" << 'EOF'
global:
  project_name: "test-project"
  version: "9.0.0"
  environment: "test"

modules:
  web:
    enabled: true
    server: "nginx"
  database:
    enabled: true
    type: "postgres"
  monitoring:
    enabled: true

deployment:
  profiles:
    test:
      modules: ["web", "database"]
EOF
}

teardown() {
    rm -rf "$TEST_DIR"
}

# Test 1: Full deployment workflow
@test "integration: full deployment workflow completes successfully" {
    run ../enterprise-deploy-master.sh install --profile test --dry-run
    [ "$status" -eq 0 ]
    [[ "$output" =~ "Deployment completed successfully" ]]
}

# Test 2: Module loader with dependencies
@test "integration: module loader resolves dependencies correctly" {
    source ../lib/module-loader.sh
    
    register_module "logging" ""
    register_module "validation" "logging"
    register_module "config" "logging,validation"
    
    run resolve_dependencies "config"
    [ "$status" -eq 0 ]
    [[ "$output" =~ "logging" ]]
    [[ "$output" =~ "validation" ]]
}

# Test 3: Config loading and validation
@test "integration: config loads and validates correctly" {
    source ../lib/module-loader.sh
    
    run load_enterprise_config "$CONFIG_FILE"
    [ "$status" -eq 0 ]
    [ "$PROJECT_NAME" = "test-project" ]
}

# Test 4: Health checks after deployment
@test "integration: health checks pass after module load" {
    source ../lib/module-loader.sh
    
    register_module "test-module" ""
    load_module "test-module"
    
    run module_health_check "test-module"
    [ "$status" -eq 0 ]
}

# Test 5: CLI wizard workflow
@test "integration: CLI wizard generates valid config" {
    run ../enterprise-cli.sh wizard --batch --profile minimal
    [ "$status" -eq 0 ]
    [ -f "/tmp/generated-config.yaml" ]
}

# Test 6: Backup and restore
@test "integration: backup creation and restoration works" {
    echo "test data" > "$TEST_DIR/test-file.txt"
    
    run ../lib/backup-manager.sh create "$TEST_DIR"
    [ "$status" -eq 0 ]
    
    rm "$TEST_DIR/test-file.txt"
    
    run ../lib/backup-manager.sh restore "$TEST_DIR"
    [ "$status" -eq 0 ]
    [ -f "$TEST_DIR/test-file.txt" ]
}

# Test 7: Monitoring metrics collection
@test "integration: monitoring collects all metrics" {
    run ../lib/monitoring.sh collect-metrics
    [ "$status" -eq 0 ]
    [[ "$output" =~ "cpu" ]]
    [[ "$output" =~ "memory" ]]
    [[ "$output" =~ "disk" ]]
}

# Test 8: Security audit execution
@test "integration: security audit runs without errors" {
    run ../lib/security-audit.sh run-audit --quick
    [ "$status" -eq 0 ]
    [[ "$output" =~ "Security Score" ]]
}

# Test 9: Rollback on failure
@test "integration: deployment rolls back on module failure" {
    # Simulate module failure
    export SIMULATE_FAILURE="true"
    
    run ../enterprise-deploy-master.sh install --profile test
    [ "$status" -ne 0 ]
    [[ "$output" =~ "Rolling back" ]]
}

# Test 10: Multi-profile deployment
@test "integration: different profiles deploy correctly" {
    for profile in minimal standard professional; do
        run ../enterprise-deploy-master.sh install --profile $profile --dry-run
        [ "$status" -eq 0 ]
    done
}

# Test 11: Module hot-reload
@test "integration: modules can be hot-reloaded" {
    source ../lib/module-loader.sh
    
    register_module "test-module" ""
    load_module "test-module"
    
    run reload_module "test-module"
    [ "$status" -eq 0 ]
}

# Test 12: Parallel module loading
@test "integration: independent modules load in parallel" {
    source ../lib/module-loader.sh
    
    register_module "module1" ""
    register_module "module2" ""
    register_module "module3" ""
    
    start_time=$(date +%s)
    load_module "module1" &
    load_module "module2" &
    load_module "module3" &
    wait
    end_time=$(date +%s)
    
    # Should complete faster than sequential
    duration=$((end_time - start_time))
    [ "$duration" -lt 5 ]
}

# Test 13: Config validation with invalid data
@test "integration: invalid config is rejected" {
    echo "invalid: yaml: data:" > "$TEST_DIR/invalid.yaml"
    
    source ../lib/module-loader.sh
    run load_enterprise_config "$TEST_DIR/invalid.yaml"
    [ "$status" -ne 0 ]
}

# Test 14: Dependency cycle detection
@test "integration: circular dependencies are detected" {
    source ../lib/module-loader.sh
    
    register_module "module1" "module2"
    register_module "module2" "module3"
    register_module "module3" "module1"
    
    run resolve_dependencies "module1"
    [ "$status" -ne 0 ]
    [[ "$output" =~ "circular" ]]
}

# Test 15: Log aggregation
@test "integration: logs are aggregated correctly" {
    echo "ERROR: test error" >> "$TEST_DIR/test.log"
    echo "WARNING: test warning" >> "$TEST_DIR/test.log"
    echo "INFO: test info" >> "$TEST_DIR/test.log"
    
    run ../lib/logging.sh aggregate "$TEST_DIR/test.log"
    [ "$status" -eq 0 ]
    [[ "$output" =~ "1 errors" ]]
    [[ "$output" =~ "1 warnings" ]]
}

# Test 16: Metrics export to Prometheus
@test "integration: metrics export to Prometheus format" {
    run ../lib/monitoring.sh export-prometheus
    [ "$status" -eq 0 ]
    [[ "$output" =~ "# HELP" ]]
    [[ "$output" =~ "# TYPE" ]]
}

# Test 17: Multi-environment config switching
@test "integration: environment switching works" {
    export ENVIRONMENT="development"
    source ../lib/module-loader.sh
    load_enterprise_config "$CONFIG_FILE"
    [ "$ENVIRONMENT" = "development" ]
    
    export ENVIRONMENT="production"
    load_enterprise_config "$CONFIG_FILE"
    [ "$ENVIRONMENT" = "production" ]
}

# Test 18: Service discovery
@test "integration: service discovery finds all services" {
    run ../lib/service-discovery.sh scan
    [ "$status" -eq 0 ]
    [[ "$output" =~ "nginx" ]] || [[ "$output" =~ "apache" ]]
}

# Test 19: Auto-scaling triggers
@test "integration: auto-scaling triggers when thresholds exceeded" {
    export CPU_USAGE=95
    run ../lib/auto-scaler.sh check-and-scale
    [ "$status" -eq 0 ]
    [[ "$output" =~ "Scaling up" ]]
}

# Test 20: Complete E2E workflow
@test "integration: complete E2E deployment and verification" {
    # 1. Deploy
    run ../enterprise-deploy-master.sh install --profile minimal --dry-run
    [ "$status" -eq 0 ]
    
    # 2. Verify health
    run ../enterprise-cli.sh health-check
    [ "$status" -eq 0 ]
    
    # 3. Run security scan
    run ../lib/security-audit.sh run-audit --quick
    [ "$status" -eq 0 ]
    
    # 4. Create backup
    run ../lib/backup-manager.sh create /tmp
    [ "$status" -eq 0 ]
    
    # 5. Check metrics
    run ../lib/monitoring.sh collect-metrics
    [ "$status" -eq 0 ]
}
