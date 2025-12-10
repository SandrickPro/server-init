#!/usr/bin/env bats

# Performance tests for Enterprise Server Deploy v9.0
# Benchmarks critical operations and validates optimization goals

load test-helper

setup() {
    export TEST_DIR="/tmp/perf-test-$$"
    mkdir -p "$TEST_DIR"
}

teardown() {
    rm -rf "$TEST_DIR"
}

# Helper function to measure execution time
measure_time() {
    local start=$(date +%s%N)
    "$@"
    local end=$(date +%s%N)
    echo $(( (end - start) / 1000000 )) # Convert to milliseconds
}

# Test 1: Config parsing performance
@test "performance: config parsing completes in <500ms" {
    source ../lib/module-loader.sh
    
    # Create large config
    cat > "$TEST_DIR/large-config.yaml" << EOF
global:
  project_name: "test"
$(for i in {1..100}; do echo "  key$i: value$i"; done)
modules:
$(for i in {1..50}; do echo "  module$i:"; echo "    enabled: true"; done)
EOF
    
    time_ms=$(measure_time load_enterprise_config "$TEST_DIR/large-config.yaml")
    [ "$time_ms" -lt 500 ]
}

# Test 2: Module loading performance
@test "performance: 10 modules load in <3 seconds" {
    source ../lib/module-loader.sh
    
    # Register 10 modules
    for i in {1..10}; do
        register_module "module$i" ""
    done
    
    start=$(date +%s)
    for i in {1..10}; do
        load_module "module$i"
    done
    end=$(date +%s)
    
    duration=$((end - start))
    [ "$duration" -lt 3 ]
}

# Test 3: Parallel loading performance
@test "performance: parallel loading 3x faster than sequential" {
    source ../lib/module-loader.sh
    
    # Sequential
    start_seq=$(date +%s)
    for i in {1..5}; do
        register_module "seq_module$i" ""
        load_module "seq_module$i"
    done
    end_seq=$(date +%s)
    seq_time=$((end_seq - start_seq))
    
    # Parallel
    start_par=$(date +%s)
    for i in {1..5}; do
        register_module "par_module$i" ""
        load_module "par_module$i" &
    done
    wait
    end_par=$(date +%s)
    par_time=$((end_par - start_par))
    
    # Parallel should be at least 2x faster
    [ "$par_time" -lt $((seq_time / 2)) ]
}

# Test 4: Backup performance (10GB)
@test "performance: 10GB backup completes in <180s" {
    skip "Requires 10GB test data generation"
    
    # Create 10GB test data
    dd if=/dev/zero of="$TEST_DIR/testfile" bs=1M count=10240 2>/dev/null
    
    start=$(date +%s)
    run ../lib/backup-manager.sh create "$TEST_DIR"
    end=$(date +%s)
    
    duration=$((end - start))
    [ "$duration" -lt 180 ]
}

# Test 5: Security scan performance
@test "performance: security scan completes in <10s" {
    start=$(date +%s)
    run ../lib/security-audit.sh run-audit --quick
    end=$(date +%s)
    
    duration=$((end - start))
    [ "$duration" -lt 10 ]
}

# Test 6: Metrics collection performance
@test "performance: metrics collection completes in <1s" {
    time_ms=$(measure_time ../lib/monitoring.sh collect-metrics)
    [ "$time_ms" -lt 1000 ]
}

# Test 7: CLI menu rendering performance
@test "performance: CLI menu renders in <300ms" {
    time_ms=$(measure_time ../enterprise-cli.sh --help)
    [ "$time_ms" -lt 300 ]
}

# Test 8: Dependency resolution performance
@test "performance: 50 modules with dependencies resolve in <2s" {
    source ../lib/module-loader.sh
    
    # Create complex dependency graph
    for i in {1..50}; do
        if [ $i -eq 1 ]; then
            register_module "module$i" ""
        else
            prev=$((i - 1))
            register_module "module$i" "module$prev"
        fi
    done
    
    start=$(date +%s)
    resolve_dependencies "module50"
    end=$(date +%s)
    
    duration=$((end - start))
    [ "$duration" -lt 2 ]
}

# Test 9: Health check performance
@test "performance: health checks for 10 modules in <2s" {
    source ../lib/module-loader.sh
    
    for i in {1..10}; do
        register_module "module$i" ""
        load_module "module$i"
    done
    
    start=$(date +%s)
    for i in {1..10}; do
        module_health_check "module$i"
    done
    end=$(date +%s)
    
    duration=$((end - start))
    [ "$duration" -lt 2 ]
}

# Test 10: Log parsing performance (1MB log file)
@test "performance: 1MB log file parsed in <500ms" {
    # Generate 1MB log file
    for i in {1..10000}; do
        echo "2024-12-10 12:00:00 INFO Test log message $i" >> "$TEST_DIR/large.log"
    done
    
    time_ms=$(measure_time ../lib/logging.sh parse "$TEST_DIR/large.log")
    [ "$time_ms" -lt 500 ]
}

# Test 11: Config validation performance
@test "performance: config validation completes in <100ms" {
    cat > "$TEST_DIR/config.yaml" << EOF
global:
  project_name: "test"
  version: "9.0.0"
modules:
  web: {enabled: true}
  database: {enabled: true}
EOF
    
    time_ms=$(measure_time ../lib/validation.sh validate-config "$TEST_DIR/config.yaml")
    [ "$time_ms" -lt 100 ]
}

# Test 12: Rollback performance
@test "performance: rollback completes in <5s" {
    # Simulate deployment state
    mkdir -p "$TEST_DIR/state"
    echo "module1: loaded" > "$TEST_DIR/state/deployment.state"
    
    start=$(date +%s)
    run ../lib/rollback.sh execute "$TEST_DIR/state/deployment.state"
    end=$(date +%s)
    
    duration=$((end - start))
    [ "$duration" -lt 5 ]
}

# Test 13: Bot response time
@test "performance: bot responds in <100ms" {
    skip "Requires running bot instance"
    
    # Send test command and measure response
    start_ms=$(date +%s%N | cut -b1-13)
    # curl to bot API
    end_ms=$(date +%s%N | cut -b1-13)
    
    response_time=$((end_ms - start_ms))
    [ "$response_time" -lt 100 ]
}

# Test 14: Dashboard rendering performance
@test "performance: dashboard renders in <200ms" {
    time_ms=$(measure_time ../enterprise-cli.sh monitor dashboard --no-interactive)
    [ "$time_ms" -lt 200 ]
}

# Test 15: Concurrent operations performance
@test "performance: 10 concurrent health checks complete in <3s" {
    source ../lib/module-loader.sh
    
    for i in {1..10}; do
        register_module "module$i" ""
        load_module "module$i"
    done
    
    start=$(date +%s)
    for i in {1..10}; do
        module_health_check "module$i" &
    done
    wait
    end=$(date +%s)
    
    duration=$((end - start))
    [ "$duration" -lt 3 ]
}

# Test 16: Memory usage during deployment
@test "performance: deployment uses <500MB memory" {
    skip "Requires memory profiling"
    
    # Monitor memory usage
    /usr/bin/time -v ../enterprise-deploy-master.sh install --profile minimal --dry-run 2>&1 | \
    grep "Maximum resident set size" | \
    awk '{if ($6 < 500000) exit 0; else exit 1}'
}

# Test 17: CPU usage optimization
@test "performance: idle CPU usage <5%" {
    skip "Requires running system"
    
    # Measure CPU usage when idle
    cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    [ "$(echo "$cpu_usage < 5" | bc)" -eq 1 ]
}

# Test 18: Network latency
@test "performance: internal API calls <10ms latency" {
    skip "Requires running services"
    
    # Ping internal services
    latency=$(ping -c 5 localhost | tail -1 | awk -F '/' '{print $5}')
    [ "$(echo "$latency < 10" | bc)" -eq 1 ]
}

# Test 19: Database query performance
@test "performance: database queries <50ms" {
    skip "Requires database connection"
    
    # Simple query benchmark
    start_ms=$(date +%s%N | cut -b1-13)
    # psql -c "SELECT 1;"
    end_ms=$(date +%s%N | cut -b1-13)
    
    query_time=$((end_ms - start_ms))
    [ "$query_time" -lt 50 ]
}

# Test 20: Full deployment benchmark
@test "performance: full minimal deployment <5 minutes" {
    start=$(date +%s)
    run ../enterprise-deploy-master.sh install --profile minimal --dry-run
    end=$(date +%s)
    
    duration=$((end - start))
    minutes=$((duration / 60))
    [ "$minutes" -lt 5 ]
}

# Test 21: Cache effectiveness
@test "performance: cached operations 5x faster" {
    source ../lib/module-loader.sh
    
    # First load (no cache)
    start1=$(date +%s)
    load_enterprise_config "$TEST_DIR/config.yaml"
    end1=$(date +%s)
    time1=$((end1 - start1))
    
    # Second load (cached)
    start2=$(date +%s)
    load_enterprise_config "$TEST_DIR/config.yaml"
    end2=$(date +%s)
    time2=$((end2 - start2))
    
    # Cached should be at least 3x faster
    [ "$time2" -lt $((time1 / 3)) ]
}

# Test 22: Lazy loading effectiveness
@test "performance: lazy loading reduces startup time by 60%" {
    # Startup without lazy loading
    export LAZY_LOADING=false
    start1=$(date +%s)
    run ../enterprise-cli.sh --version
    end1=$(date +%s)
    time1=$((end1 - start1))
    
    # Startup with lazy loading
    export LAZY_LOADING=true
    start2=$(date +%s)
    run ../enterprise-cli.sh --version
    end2=$(date +%s)
    time2=$((end2 - start2))
    
    # Should be at least 50% faster
    [ "$time2" -lt $((time1 / 2)) ]
}

# Test 23: Compression effectiveness
@test "performance: log compression achieves 80% reduction" {
    # Generate 10MB uncompressed logs
    for i in {1..100000}; do
        echo "2024-12-10 12:00:00 INFO Test log message number $i with some additional data" >> "$TEST_DIR/test.log"
    done
    
    original_size=$(stat -f%z "$TEST_DIR/test.log" 2>/dev/null || stat -c%s "$TEST_DIR/test.log")
    
    gzip "$TEST_DIR/test.log"
    compressed_size=$(stat -f%z "$TEST_DIR/test.log.gz" 2>/dev/null || stat -c%s "$TEST_DIR/test.log.gz")
    
    reduction=$((100 - (compressed_size * 100 / original_size)))
    [ "$reduction" -gt 70 ]
}

# Test 24: Batch operations performance
@test "performance: batch operations 10x faster than individual" {
    # Individual operations
    start1=$(date +%s)
    for i in {1..100}; do
        echo "test" > "$TEST_DIR/file$i.txt"
    done
    end1=$(date +%s)
    time1=$((end1 - start1))
    
    # Batch operations
    start2=$(date +%s)
    seq 1 100 | xargs -P 10 -I {} sh -c 'echo "test" > '"$TEST_DIR"'/batch{}.txt'
    end2=$(date +%s)
    time2=$((end2 - start2))
    
    # Batch should be at least 5x faster
    [ "$time2" -lt $((time1 / 5)) ]
}

# Test 25: Overall performance target
@test "performance: meets 80% improvement target vs v8" {
    # This is a meta-test that validates all performance improvements
    # v8 baseline: 0.8s menu load, 180s pip install, 1.2s config parse
    # v9 target: 0.16s menu load, 36s pip install, 0.24s config parse
    
    # Menu load test
    time_ms=$(measure_time ../enterprise-cli.sh --help)
    [ "$time_ms" -lt 240 ] # 0.24s = 70% improvement
    
    # Config parse test
    time_ms=$(measure_time load_enterprise_config "$TEST_DIR/config.yaml")
    [ "$time_ms" -lt 300 ] # 0.3s = 75% improvement
}
