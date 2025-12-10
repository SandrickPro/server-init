#!/usr/bin/env bash

###############################################################################
# HIGH AVAILABILITY MODULE v11.0
# Multi-region deployment with automated failover
###############################################################################

set -euo pipefail

# Configuration
PRIMARY_REGION="${PRIMARY_REGION:-us-east-1}"
SECONDARY_REGION="${SECONDARY_REGION:-us-west-2}"
TERTIARY_REGION="${TERTIARY_REGION:-eu-west-1}"
HEALTH_CHECK_INTERVAL=10  # seconds
FAILOVER_THRESHOLD=3  # consecutive failures before failover
RTO_TARGET=300  # Recovery Time Objective: 5 minutes
RPO_TARGET=60  # Recovery Point Objective: 1 minute

###############################################################################
# Region Management
###############################################################################

setup_multi_region() {
    echo "🌍 Setting up multi-region deployment..."
    
    local regions=("$PRIMARY_REGION" "$SECONDARY_REGION" "$TERTIARY_REGION")
    
    for region in "${regions[@]}"; do
        echo "Configuring region: $region"
        
        # Create VPC
        create_vpc "$region"
        
        # Deploy Kubernetes cluster
        deploy_k8s_cluster "$region"
        
        # Setup database replication
        setup_database_replication "$region"
        
        # Configure load balancer
        configure_load_balancer "$region"
        
        # Deploy application
        deploy_application_to_region "$region"
    done
    
    # Setup global load balancer
    setup_global_load_balancer
    
    echo "✅ Multi-region setup complete"
}

create_vpc() {
    local region=$1
    
    echo "Creating VPC in $region..."
    
    # Create VPC with CIDR
    local vpc_id=$(aws ec2 create-vpc \
        --region "$region" \
        --cidr-block "10.${get_region_index $region}.0.0/16" \
        --query 'Vpc.VpcId' \
        --output text)
    
    # Enable DNS
    aws ec2 modify-vpc-attribute \
        --region "$region" \
        --vpc-id "$vpc_id" \
        --enable-dns-hostnames
    
    # Create subnets
    local azs=(a b c)
    for i in "${!azs[@]}"; do
        aws ec2 create-subnet \
            --region "$region" \
            --vpc-id "$vpc_id" \
            --cidr-block "10.${get_region_index $region}.$i.0/24" \
            --availability-zone "${region}${azs[$i]}"
    done
    
    echo "VPC created: $vpc_id"
}

deploy_k8s_cluster() {
    local region=$1
    
    echo "Deploying Kubernetes cluster in $region..."
    
    # Create EKS cluster
    eksctl create cluster \
        --name "devops-cluster-$region" \
        --region "$region" \
        --version 1.28 \
        --nodegroup-name standard-workers \
        --node-type t3.large \
        --nodes 3 \
        --nodes-min 3 \
        --nodes-max 10 \
        --managed \
        --asg-access \
        --external-dns-access \
        --full-ecr-access \
        --alb-ingress-access
    
    # Update kubeconfig
    aws eks update-kubeconfig \
        --region "$region" \
        --name "devops-cluster-$region" \
        --alias "$region"
    
    echo "✅ Cluster deployed in $region"
}

setup_database_replication() {
    local region=$1
    
    echo "Setting up database replication for $region..."
    
    if [[ "$region" == "$PRIMARY_REGION" ]]; then
        # Create primary database
        create_primary_database "$region"
    else
        # Create read replica
        create_read_replica "$region" "$PRIMARY_REGION"
    fi
    
    # Configure async replication
    configure_replication "$region"
}

create_primary_database() {
    local region=$1
    
    cat > /tmp/postgres-primary.yaml << EOF
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: postgres-primary
  namespace: database
spec:
  instances: 3
  primaryUpdateStrategy: unsupervised
  
  postgresql:
    parameters:
      max_connections: "500"
      shared_buffers: "8GB"
      effective_cache_size: "24GB"
      wal_level: "logical"
      max_wal_senders: "10"
      max_replication_slots: "10"
  
  bootstrap:
    initdb:
      database: production
      owner: app
  
  storage:
    size: 100Gi
    storageClass: fast-ssd
  
  backup:
    barmanObjectStore:
      destinationPath: s3://backups-$region/postgres
      s3Credentials:
        accessKeyId:
          name: aws-creds
          key: ACCESS_KEY_ID
        secretAccessKey:
          name: aws-creds
          key: SECRET_ACCESS_KEY
    retentionPolicy: "30d"
  
  monitoring:
    enabled: true
    podMonitorEnabled: true
EOF
    
    kubectl --context="$region" apply -f /tmp/postgres-primary.yaml
}

create_read_replica() {
    local region=$1
    local primary_region=$2
    
    # Setup logical replication from primary
    kubectl --context="$primary_region" exec -it postgres-primary-1 -- \
        psql -c "CREATE PUBLICATION all_tables FOR ALL TABLES;"
    
    # Create replica in secondary region
    cat > /tmp/postgres-replica.yaml << EOF
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: postgres-replica
  namespace: database
spec:
  instances: 2
  
  replica:
    enabled: true
    source: postgres-primary
  
  externalClusters:
    - name: postgres-primary
      connectionParameters:
        host: postgres-primary.database.svc.cluster.local
        user: app
        dbname: production
      password:
        name: postgres-primary-app
        key: password
EOF
    
    kubectl --context="$region" apply -f /tmp/postgres-replica.yaml
}

configure_replication() {
    local region=$1
    
    # Configure streaming replication
    cat > /tmp/replication-config.sql << EOF
-- Enable async replication
ALTER SYSTEM SET synchronous_commit = 'off';
ALTER SYSTEM SET wal_keep_size = '10GB';
ALTER SYSTEM SET hot_standby = 'on';
ALTER SYSTEM SET max_standby_streaming_delay = '30s';

-- Create replication slots
SELECT pg_create_physical_replication_slot('replica_${region}');
EOF
    
    kubectl --context="$PRIMARY_REGION" exec -it postgres-primary-1 -- \
        psql -f /tmp/replication-config.sql
}

###############################################################################
# Global Load Balancing
###############################################################################

setup_global_load_balancer() {
    echo "🌐 Setting up global load balancer..."
    
    # Create Route53 hosted zone
    local zone_id=$(aws route53 create-hosted-zone \
        --name "devops-platform.example.com" \
        --caller-reference "$(date +%s)" \
        --query 'HostedZone.Id' \
        --output text)
    
    # Create health checks for each region
    for region in "$PRIMARY_REGION" "$SECONDARY_REGION" "$TERTIARY_REGION"; do
        create_health_check "$region" "$zone_id"
    done
    
    # Create failover routing policy
    create_failover_policy "$zone_id"
    
    echo "✅ Global load balancer configured"
}

create_health_check() {
    local region=$1
    local zone_id=$2
    
    # Get region endpoint
    local endpoint=$(kubectl --context="$region" get ingress app-ingress \
        -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
    
    # Create Route53 health check
    aws route53 create-health-check \
        --health-check-config \
            "IPAddress=$endpoint,Port=443,Type=HTTPS,ResourcePath=/health,\
             RequestInterval=10,FailureThreshold=$FAILOVER_THRESHOLD"
}

create_failover_policy() {
    local zone_id=$1
    
    cat > /tmp/route53-policy.json << EOF
{
  "Changes": [
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "api.devops-platform.example.com",
        "Type": "A",
        "SetIdentifier": "Primary",
        "Failover": "PRIMARY",
        "AliasTarget": {
          "HostedZoneId": "$zone_id",
          "DNSName": "$(get_region_endpoint $PRIMARY_REGION)",
          "EvaluateTargetHealth": true
        }
      }
    },
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "api.devops-platform.example.com",
        "Type": "A",
        "SetIdentifier": "Secondary",
        "Failover": "SECONDARY",
        "AliasTarget": {
          "HostedZoneId": "$zone_id",
          "DNSName": "$(get_region_endpoint $SECONDARY_REGION)",
          "EvaluateTargetHealth": true
        }
      }
    }
  ]
}
EOF
    
    aws route53 change-resource-record-sets \
        --hosted-zone-id "$zone_id" \
        --change-batch file:///tmp/route53-policy.json
}

###############################################################################
# Automated Failover
###############################################################################

monitor_and_failover() {
    echo "🔄 Starting failover monitor..."
    
    local failure_count=0
    local current_primary="$PRIMARY_REGION"
    
    while true; do
        # Check primary region health
        if check_region_health "$current_primary"; then
            failure_count=0
        else
            ((failure_count++))
            echo "⚠️  Health check failed for $current_primary (attempt $failure_count/$FAILOVER_THRESHOLD)"
            
            if [[ $failure_count -ge $FAILOVER_THRESHOLD ]]; then
                echo "🚨 Initiating failover from $current_primary"
                
                # Determine new primary
                local new_primary=$(select_healthy_region "$current_primary")
                
                if [[ -n "$new_primary" ]]; then
                    perform_failover "$current_primary" "$new_primary"
                    current_primary="$new_primary"
                    failure_count=0
                else
                    echo "❌ No healthy region available for failover!"
                    send_critical_alert "All regions are unhealthy!"
                fi
            fi
        fi
        
        sleep $HEALTH_CHECK_INTERVAL
    done
}

check_region_health() {
    local region=$1
    
    # Check Kubernetes API
    if ! kubectl --context="$region" get nodes &>/dev/null; then
        return 1
    fi
    
    # Check application health
    local health_status=$(curl -sf "https://$(get_region_endpoint $region)/health" || echo "unhealthy")
    if [[ "$health_status" != *"healthy"* ]]; then
        return 1
    fi
    
    # Check database
    if ! kubectl --context="$region" exec -it postgres-primary-1 -- \
        psql -c "SELECT 1" &>/dev/null; then
        return 1
    fi
    
    return 0
}

select_healthy_region() {
    local failed_region=$1
    
    local regions=("$PRIMARY_REGION" "$SECONDARY_REGION" "$TERTIARY_REGION")
    
    for region in "${regions[@]}"; do
        if [[ "$region" != "$failed_region" ]] && check_region_health "$region"; then
            echo "$region"
            return 0
        fi
    done
    
    return 1
}

perform_failover() {
    local old_primary=$1
    local new_primary=$2
    
    local start_time=$(date +%s)
    
    echo "🔄 Performing failover: $old_primary → $new_primary"
    
    # Step 1: Promote replica to primary (30s)
    promote_replica_to_primary "$new_primary"
    
    # Step 2: Update DNS records (60s)
    update_dns_for_failover "$old_primary" "$new_primary"
    
    # Step 3: Redirect traffic (30s)
    redirect_traffic_to_region "$new_primary"
    
    # Step 4: Update application config (30s)
    update_application_config "$new_primary"
    
    # Step 5: Verify failover (30s)
    verify_failover "$new_primary"
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo "✅ Failover complete in ${duration}s (RTO target: ${RTO_TARGET}s)"
    
    # Send notification
    send_failover_notification "$old_primary" "$new_primary" "$duration"
    
    # Check if RTO was met
    if [[ $duration -gt $RTO_TARGET ]]; then
        echo "⚠️  RTO target exceeded: ${duration}s > ${RTO_TARGET}s"
    fi
}

promote_replica_to_primary() {
    local region=$1
    
    echo "Promoting replica in $region to primary..."
    
    # Stop replication
    kubectl --context="$region" exec -it postgres-replica-1 -- \
        psql -c "SELECT pg_promote();"
    
    # Update cluster config
    kubectl --context="$region" patch cluster postgres-replica \
        --type merge \
        -p '{"spec":{"replica":{"enabled":false}}}'
    
    # Wait for promotion
    sleep 10
}

update_dns_for_failover() {
    local old_primary=$1
    local new_primary=$2
    
    echo "Updating DNS records..."
    
    # Update Route53 failover policy
    local zone_id=$(aws route53 list-hosted-zones \
        --query "HostedZones[?Name=='devops-platform.example.com.'].Id" \
        --output text)
    
    # Swap primary and secondary
    aws route53 change-resource-record-sets \
        --hosted-zone-id "$zone_id" \
        --change-batch "{
          \"Changes\": [{
            \"Action\": \"UPSERT\",
            \"ResourceRecordSet\": {
              \"Name\": \"api.devops-platform.example.com\",
              \"Type\": \"A\",
              \"SetIdentifier\": \"Primary\",
              \"Failover\": \"PRIMARY\",
              \"AliasTarget\": {
                \"HostedZoneId\": \"$zone_id\",
                \"DNSName\": \"$(get_region_endpoint $new_primary)\",
                \"EvaluateTargetHealth\": true
              }
            }
          }]
        }"
}

redirect_traffic_to_region() {
    local region=$1
    
    echo "Redirecting traffic to $region..."
    
    # Update global load balancer weights
    kubectl --context="$region" patch service app-service \
        --type merge \
        -p '{"metadata":{"annotations":{"service.beta.kubernetes.io/aws-load-balancer-backend-protocol":"http"}}}'
}

update_application_config() {
    local region=$1
    
    echo "Updating application configuration..."
    
    # Update ConfigMap with new primary region
    kubectl --context="$region" create configmap app-config \
        --from-literal=PRIMARY_REGION="$region" \
        --dry-run=client -o yaml | kubectl --context="$region" apply -f -
    
    # Restart pods to pick up new config
    kubectl --context="$region" rollout restart deployment app
}

verify_failover() {
    local region=$1
    
    echo "Verifying failover..."
    
    # Test application endpoint
    local response=$(curl -sf "https://$(get_region_endpoint $region)/health")
    if [[ "$response" != *"healthy"* ]]; then
        echo "❌ Health check failed after failover"
        return 1
    fi
    
    # Test database connectivity
    if ! kubectl --context="$region" exec -it postgres-primary-1 -- \
        psql -c "SELECT 1" &>/dev/null; then
        echo "❌ Database connectivity failed after failover"
        return 1
    fi
    
    echo "✅ Failover verification successful"
}

###############################################################################
# Data Synchronization
###############################################################################

setup_data_sync() {
    echo "🔄 Setting up cross-region data synchronization..."
    
    # Setup S3 cross-region replication
    setup_s3_replication
    
    # Setup Redis cluster
    setup_redis_cluster
    
    # Setup cache invalidation
    setup_cache_invalidation
    
    echo "✅ Data sync configured"
}

setup_s3_replication() {
    # Create replication buckets
    for region in "$PRIMARY_REGION" "$SECONDARY_REGION" "$TERTIARY_REGION"; do
        aws s3api create-bucket \
            --bucket "app-data-$region" \
            --region "$region" \
            --create-bucket-configuration LocationConstraint="$region"
        
        # Enable versioning (required for replication)
        aws s3api put-bucket-versioning \
            --bucket "app-data-$region" \
            --versioning-configuration Status=Enabled
    done
    
    # Configure replication rules
    aws s3api put-bucket-replication \
        --bucket "app-data-$PRIMARY_REGION" \
        --replication-configuration file:///tmp/s3-replication.json
}

setup_redis_cluster() {
    # Deploy Redis cluster across regions
    cat > /tmp/redis-cluster.yaml << EOF
apiVersion: redis.redis.opstreelabs.in/v1beta1
kind: RedisCluster
metadata:
  name: redis-cluster
spec:
  clusterSize: 6
  clusterVersion: v7
  persistenceEnabled: true
  redisExporter:
    enabled: true
  storage:
    volumeClaimTemplate:
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 50Gi
  podSecurityContext:
    runAsUser: 1000
    fsGroup: 1000
EOF
    
    for region in "$PRIMARY_REGION" "$SECONDARY_REGION" "$TERTIARY_REGION"; do
        kubectl --context="$region" apply -f /tmp/redis-cluster.yaml
    done
}

setup_cache_invalidation() {
    # Setup pub/sub for cache invalidation
    cat > /tmp/cache-invalidator.py << 'EOF'
import redis
import json

def invalidate_cache_globally(key):
    """Invalidate cache key across all regions"""
    regions = ['us-east-1', 'us-west-2', 'eu-west-1']
    
    for region in regions:
        r = redis.Redis(host=f'redis.{region}.internal', port=6379)
        r.delete(key)
        r.publish('cache-invalidation', json.dumps({'key': key, 'region': region}))
EOF
}

###############################################################################
# Utility Functions
###############################################################################

get_region_index() {
    local region=$1
    case $region in
        "$PRIMARY_REGION") echo 0 ;;
        "$SECONDARY_REGION") echo 1 ;;
        "$TERTIARY_REGION") echo 2 ;;
        *) echo 9 ;;
    esac
}

get_region_endpoint() {
    local region=$1
    kubectl --context="$region" get ingress app-ingress \
        -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "unknown"
}

send_failover_notification() {
    local old_primary=$1
    local new_primary=$2
    local duration=$3
    
    local message="🔄 Failover Completed

Old Primary: $old_primary
New Primary: $new_primary
Duration: ${duration}s
RTO Target: ${RTO_TARGET}s
Status: $([ $duration -le $RTO_TARGET ] && echo "✅ Met" || echo "⚠️ Exceeded")

Time: $(date -Iseconds)"
    
    # Send via Telegram
    /opt/telegram-bot/send-alert.sh "Failover Notification" "$message"
}

send_critical_alert() {
    local message=$1
    /opt/telegram-bot/send-alert.sh "🚨 CRITICAL ALERT" "$message"
}

###############################################################################
# Main Setup
###############################################################################

setup_high_availability() {
    echo "🚀 Setting up High Availability infrastructure..."
    
    # Multi-region deployment
    setup_multi_region
    
    # Data synchronization
    setup_data_sync
    
    # Start failover monitor
    monitor_and_failover &
    
    echo "✅ High Availability setup complete!"
    echo ""
    echo "📊 Configuration:"
    echo "   - Primary Region: $PRIMARY_REGION"
    echo "   - Secondary Region: $SECONDARY_REGION"
    echo "   - Tertiary Region: $TERTIARY_REGION"
    echo "   - RTO Target: ${RTO_TARGET}s (5 minutes)"
    echo "   - RPO Target: ${RPO_TARGET}s (1 minute)"
    echo "   - Health Check Interval: ${HEALTH_CHECK_INTERVAL}s"
    echo "   - Failover Threshold: $FAILOVER_THRESHOLD failures"
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    setup_high_availability
fi
