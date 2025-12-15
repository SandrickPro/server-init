#!/usr/bin/env python3
"""
Server Init - Iteration 333: Global Load Balancer Platform
Платформа глобальной балансировки нагрузки

Функционал:
- Global Server Load Balancing (GSLB) - глобальная балансировка
- DNS-based Routing - маршрутизация на основе DNS
- Health Checking - проверка здоровья
- Geographic Routing - географическая маршрутизация
- Weighted Routing - взвешенная маршрутизация
- Failover Management - управление отказоустойчивостью
- Latency-based Routing - маршрутизация по задержке
- Traffic Management - управление трафиком
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import math


class RoutingPolicy(Enum):
    """Политика маршрутизации"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    GEOGRAPHIC = "geographic"
    LATENCY = "latency"
    FAILOVER = "failover"
    GEOPROXIMITY = "geoproximity"
    IP_HASH = "ip_hash"
    RANDOM = "random"


class EndpointStatus(Enum):
    """Статус endpoint"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    DRAINING = "draining"
    DISABLED = "disabled"


class HealthCheckProtocol(Enum):
    """Протокол проверки здоровья"""
    HTTP = "http"
    HTTPS = "https"
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"


class RecordType(Enum):
    """Тип DNS записи"""
    A = "A"
    AAAA = "AAAA"
    CNAME = "CNAME"
    MX = "MX"
    TXT = "TXT"
    NS = "NS"


class FailoverStrategy(Enum):
    """Стратегия отказоустойчивости"""
    ACTIVE_PASSIVE = "active_passive"
    ACTIVE_ACTIVE = "active_active"
    PRIORITY = "priority"
    AUTOMATIC = "automatic"


@dataclass
class Region:
    """Регион"""
    region_id: str
    name: str
    
    # Geographic
    continent: str = ""
    country: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    
    # Endpoints
    endpoint_ids: List[str] = field(default_factory=list)
    
    # Status
    is_active: bool = True
    
    # Traffic
    current_connections: int = 0
    requests_per_second: int = 0
    
    # Timestamp
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Endpoint:
    """Endpoint для балансировки"""
    endpoint_id: str
    name: str
    
    # Target
    ip_address: str = ""
    port: int = 443
    hostname: str = ""
    
    # Region
    region_id: str = ""
    
    # Weight
    weight: int = 100
    priority: int = 1
    
    # Status
    status: EndpointStatus = EndpointStatus.HEALTHY
    
    # Health
    health_score: float = 100.0
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    
    # Performance
    avg_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    
    # Capacity
    max_connections: int = 10000
    current_connections: int = 0
    
    # Traffic
    requests_total: int = 0
    requests_success: int = 0
    requests_failed: int = 0
    bytes_in: int = 0
    bytes_out: int = 0
    
    # Timestamps
    last_health_check: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class HealthCheck:
    """Проверка здоровья"""
    check_id: str
    name: str
    
    # Protocol
    protocol: HealthCheckProtocol = HealthCheckProtocol.HTTPS
    
    # Target
    path: str = "/health"
    port: int = 443
    
    # Timing
    interval_seconds: int = 30
    timeout_seconds: int = 10
    
    # Thresholds
    healthy_threshold: int = 3
    unhealthy_threshold: int = 3
    
    # Expected response
    expected_codes: List[int] = field(default_factory=lambda: [200, 201, 204])
    expected_body: str = ""
    
    # TLS
    verify_ssl: bool = True
    
    # Status
    is_enabled: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DNSRecord:
    """DNS запись"""
    record_id: str
    
    # Name
    name: str = ""
    
    # Type
    record_type: RecordType = RecordType.A
    
    # Value
    value: str = ""
    
    # TTL
    ttl: int = 60
    
    # Routing
    routing_policy: RoutingPolicy = RoutingPolicy.ROUND_ROBIN
    
    # Geographic (for geo routing)
    geo_location: str = ""  # continent, country, or subdivision
    
    # Weight (for weighted routing)
    weight: int = 100
    
    # Latency (for latency routing)
    latency_region: str = ""
    
    # Failover
    failover_type: str = ""  # primary, secondary
    
    # Health check
    health_check_id: str = ""
    
    # Status
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Pool:
    """Пул endpoints"""
    pool_id: str
    name: str
    
    # Endpoints
    endpoint_ids: List[str] = field(default_factory=list)
    
    # Routing
    routing_policy: RoutingPolicy = RoutingPolicy.ROUND_ROBIN
    
    # Health check
    health_check_id: str = ""
    
    # Failover
    failover_pool_id: str = ""
    failover_strategy: FailoverStrategy = FailoverStrategy.AUTOMATIC
    
    # Minimum healthy
    min_healthy_endpoints: int = 1
    
    # Session affinity
    session_affinity: bool = False
    session_ttl_seconds: int = 3600
    
    # Status
    is_healthy: bool = True
    healthy_endpoints: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TrafficPolicy:
    """Политика трафика"""
    policy_id: str
    name: str
    
    # Routing
    routing_policy: RoutingPolicy = RoutingPolicy.WEIGHTED
    
    # Rules
    rules: List[Dict[str, Any]] = field(default_factory=list)
    
    # Default pool
    default_pool_id: str = ""
    
    # Priority
    priority: int = 0
    
    # Status
    is_enabled: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class GeoMapping:
    """Географическое сопоставление"""
    mapping_id: str
    
    # Location
    continent: str = ""
    country: str = ""
    subdivision: str = ""
    
    # Target pool
    pool_id: str = ""
    
    # Priority
    priority: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class FailoverConfig:
    """Конфигурация отказоустойчивости"""
    config_id: str
    name: str
    
    # Primary
    primary_pool_id: str = ""
    
    # Secondary
    secondary_pool_id: str = ""
    
    # Strategy
    strategy: FailoverStrategy = FailoverStrategy.ACTIVE_PASSIVE
    
    # Thresholds
    failover_threshold: float = 50.0  # Failover if health below this %
    failback_threshold: float = 80.0  # Failback if health above this %
    
    # Timing
    failover_delay_seconds: int = 30
    failback_delay_seconds: int = 60
    
    # Status
    is_active: bool = True
    current_active_pool: str = ""
    failover_count: int = 0
    
    # Timestamps
    last_failover: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class HealthCheckResult:
    """Результат проверки здоровья"""
    result_id: str
    
    # Endpoint
    endpoint_id: str = ""
    health_check_id: str = ""
    
    # Result
    is_healthy: bool = True
    response_code: int = 0
    response_time_ms: float = 0.0
    
    # Error
    error_message: str = ""
    
    # Timestamp
    checked_at: datetime = field(default_factory=datetime.now)


@dataclass
class TrafficMetrics:
    """Метрики трафика"""
    metric_id: str
    
    # Target
    pool_id: str = ""
    endpoint_id: str = ""
    
    # Time
    timestamp: datetime = field(default_factory=datetime.now)
    interval_minutes: int = 5
    
    # Requests
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # Latency
    avg_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    
    # Throughput
    bytes_in: int = 0
    bytes_out: int = 0
    
    # Connections
    total_connections: int = 0
    active_connections: int = 0


class GlobalLoadBalancer:
    """Глобальный балансировщик нагрузки"""
    
    def __init__(self):
        self.regions: Dict[str, Region] = {}
        self.endpoints: Dict[str, Endpoint] = {}
        self.health_checks: Dict[str, HealthCheck] = {}
        self.dns_records: Dict[str, DNSRecord] = {}
        self.pools: Dict[str, Pool] = {}
        self.policies: Dict[str, TrafficPolicy] = {}
        self.geo_mappings: Dict[str, GeoMapping] = {}
        self.failover_configs: Dict[str, FailoverConfig] = {}
        self.health_results: Dict[str, HealthCheckResult] = {}
        self.traffic_metrics: Dict[str, TrafficMetrics] = {}
        
    async def create_region(self, name: str,
                           continent: str,
                           country: str,
                           latitude: float,
                           longitude: float) -> Region:
        """Создание региона"""
        region = Region(
            region_id=f"region_{uuid.uuid4().hex[:8]}",
            name=name,
            continent=continent,
            country=country,
            latitude=latitude,
            longitude=longitude
        )
        
        self.regions[region.region_id] = region
        return region
        
    async def create_endpoint(self, name: str,
                             ip_address: str,
                             port: int,
                             region_id: str,
                             weight: int = 100,
                             priority: int = 1,
                             hostname: str = "") -> Optional[Endpoint]:
        """Создание endpoint"""
        region = self.regions.get(region_id)
        if not region:
            return None
            
        endpoint = Endpoint(
            endpoint_id=f"ep_{uuid.uuid4().hex[:8]}",
            name=name,
            ip_address=ip_address,
            port=port,
            region_id=region_id,
            weight=weight,
            priority=priority,
            hostname=hostname,
            avg_latency_ms=random.uniform(10, 100)
        )
        
        region.endpoint_ids.append(endpoint.endpoint_id)
        self.endpoints[endpoint.endpoint_id] = endpoint
        return endpoint
        
    async def create_health_check(self, name: str,
                                 protocol: HealthCheckProtocol = HealthCheckProtocol.HTTPS,
                                 path: str = "/health",
                                 port: int = 443,
                                 interval: int = 30,
                                 timeout: int = 10) -> HealthCheck:
        """Создание проверки здоровья"""
        check = HealthCheck(
            check_id=f"hc_{uuid.uuid4().hex[:8]}",
            name=name,
            protocol=protocol,
            path=path,
            port=port,
            interval_seconds=interval,
            timeout_seconds=timeout
        )
        
        self.health_checks[check.check_id] = check
        return check
        
    async def create_pool(self, name: str,
                         endpoint_ids: List[str],
                         routing_policy: RoutingPolicy = RoutingPolicy.ROUND_ROBIN,
                         health_check_id: str = "",
                         session_affinity: bool = False) -> Pool:
        """Создание пула"""
        pool = Pool(
            pool_id=f"pool_{uuid.uuid4().hex[:8]}",
            name=name,
            endpoint_ids=endpoint_ids,
            routing_policy=routing_policy,
            health_check_id=health_check_id,
            session_affinity=session_affinity,
            healthy_endpoints=len(endpoint_ids)
        )
        
        self.pools[pool.pool_id] = pool
        return pool
        
    async def create_dns_record(self, name: str,
                               record_type: RecordType,
                               value: str,
                               ttl: int = 60,
                               routing_policy: RoutingPolicy = RoutingPolicy.ROUND_ROBIN,
                               weight: int = 100,
                               health_check_id: str = "") -> DNSRecord:
        """Создание DNS записи"""
        record = DNSRecord(
            record_id=f"dns_{uuid.uuid4().hex[:8]}",
            name=name,
            record_type=record_type,
            value=value,
            ttl=ttl,
            routing_policy=routing_policy,
            weight=weight,
            health_check_id=health_check_id
        )
        
        self.dns_records[record.record_id] = record
        return record
        
    async def create_traffic_policy(self, name: str,
                                   routing_policy: RoutingPolicy,
                                   default_pool_id: str,
                                   rules: List[Dict[str, Any]] = None) -> Optional[TrafficPolicy]:
        """Создание политики трафика"""
        if default_pool_id not in self.pools:
            return None
            
        policy = TrafficPolicy(
            policy_id=f"policy_{uuid.uuid4().hex[:8]}",
            name=name,
            routing_policy=routing_policy,
            default_pool_id=default_pool_id,
            rules=rules or []
        )
        
        self.policies[policy.policy_id] = policy
        return policy
        
    async def create_geo_mapping(self, continent: str = "",
                                country: str = "",
                                subdivision: str = "",
                                pool_id: str = "",
                                priority: int = 0) -> Optional[GeoMapping]:
        """Создание географического сопоставления"""
        if pool_id not in self.pools:
            return None
            
        mapping = GeoMapping(
            mapping_id=f"geo_{uuid.uuid4().hex[:8]}",
            continent=continent,
            country=country,
            subdivision=subdivision,
            pool_id=pool_id,
            priority=priority
        )
        
        self.geo_mappings[mapping.mapping_id] = mapping
        return mapping
        
    async def create_failover_config(self, name: str,
                                    primary_pool_id: str,
                                    secondary_pool_id: str,
                                    strategy: FailoverStrategy = FailoverStrategy.ACTIVE_PASSIVE,
                                    failover_threshold: float = 50.0) -> Optional[FailoverConfig]:
        """Создание конфигурации отказоустойчивости"""
        if primary_pool_id not in self.pools or secondary_pool_id not in self.pools:
            return None
            
        config = FailoverConfig(
            config_id=f"fo_{uuid.uuid4().hex[:8]}",
            name=name,
            primary_pool_id=primary_pool_id,
            secondary_pool_id=secondary_pool_id,
            strategy=strategy,
            failover_threshold=failover_threshold,
            current_active_pool=primary_pool_id
        )
        
        self.failover_configs[config.config_id] = config
        return config
        
    async def run_health_check(self, endpoint_id: str,
                              health_check_id: str) -> Optional[HealthCheckResult]:
        """Выполнение проверки здоровья"""
        endpoint = self.endpoints.get(endpoint_id)
        check = self.health_checks.get(health_check_id)
        
        if not endpoint or not check:
            return None
            
        # Simulate health check
        is_healthy = random.random() > 0.05  # 95% success rate
        response_time = random.uniform(10, 200) if is_healthy else random.uniform(500, 1000)
        
        result = HealthCheckResult(
            result_id=f"hcr_{uuid.uuid4().hex[:8]}",
            endpoint_id=endpoint_id,
            health_check_id=health_check_id,
            is_healthy=is_healthy,
            response_code=200 if is_healthy else 500,
            response_time_ms=response_time,
            error_message="" if is_healthy else "Connection timeout"
        )
        
        # Update endpoint status
        if is_healthy:
            endpoint.consecutive_successes += 1
            endpoint.consecutive_failures = 0
            if endpoint.consecutive_successes >= check.healthy_threshold:
                endpoint.status = EndpointStatus.HEALTHY
        else:
            endpoint.consecutive_failures += 1
            endpoint.consecutive_successes = 0
            if endpoint.consecutive_failures >= check.unhealthy_threshold:
                endpoint.status = EndpointStatus.UNHEALTHY
                
        endpoint.last_health_check = datetime.now()
        endpoint.avg_latency_ms = (endpoint.avg_latency_ms + response_time) / 2
        
        self.health_results[result.result_id] = result
        return result
        
    async def update_pool_health(self, pool_id: str):
        """Обновление здоровья пула"""
        pool = self.pools.get(pool_id)
        if not pool:
            return
            
        healthy_count = 0
        for ep_id in pool.endpoint_ids:
            ep = self.endpoints.get(ep_id)
            if ep and ep.status == EndpointStatus.HEALTHY:
                healthy_count += 1
                
        pool.healthy_endpoints = healthy_count
        pool.is_healthy = healthy_count >= pool.min_healthy_endpoints
        
    async def check_failover(self, config_id: str) -> bool:
        """Проверка необходимости failover"""
        config = self.failover_configs.get(config_id)
        if not config or not config.is_active:
            return False
            
        primary_pool = self.pools.get(config.primary_pool_id)
        secondary_pool = self.pools.get(config.secondary_pool_id)
        
        if not primary_pool or not secondary_pool:
            return False
            
        # Calculate primary pool health percentage
        total_endpoints = len(primary_pool.endpoint_ids)
        if total_endpoints == 0:
            return False
            
        health_percent = (primary_pool.healthy_endpoints / total_endpoints) * 100
        
        # Check if failover needed
        if config.current_active_pool == config.primary_pool_id:
            if health_percent < config.failover_threshold:
                # Failover to secondary
                config.current_active_pool = config.secondary_pool_id
                config.failover_count += 1
                config.last_failover = datetime.now()
                return True
        else:
            # Check if failback possible
            if health_percent >= config.failback_threshold:
                config.current_active_pool = config.primary_pool_id
                config.last_failover = datetime.now()
                return True
                
        return False
        
    def resolve_request(self, policy_id: str,
                       client_ip: str = "",
                       client_location: Dict[str, str] = None) -> Optional[Endpoint]:
        """Разрешение запроса к endpoint"""
        policy = self.policies.get(policy_id)
        if not policy:
            return None
            
        pool = self.pools.get(policy.default_pool_id)
        if not pool:
            return None
            
        # Get healthy endpoints
        healthy_endpoints = []
        for ep_id in pool.endpoint_ids:
            ep = self.endpoints.get(ep_id)
            if ep and ep.status == EndpointStatus.HEALTHY:
                healthy_endpoints.append(ep)
                
        if not healthy_endpoints:
            return None
            
        # Apply routing policy
        if pool.routing_policy == RoutingPolicy.ROUND_ROBIN:
            return healthy_endpoints[0]
        elif pool.routing_policy == RoutingPolicy.WEIGHTED:
            return self._weighted_select(healthy_endpoints)
        elif pool.routing_policy == RoutingPolicy.LATENCY:
            return min(healthy_endpoints, key=lambda e: e.avg_latency_ms)
        elif pool.routing_policy == RoutingPolicy.RANDOM:
            return random.choice(healthy_endpoints)
        elif pool.routing_policy == RoutingPolicy.IP_HASH:
            idx = hash(client_ip) % len(healthy_endpoints)
            return healthy_endpoints[idx]
        else:
            return healthy_endpoints[0]
            
    def _weighted_select(self, endpoints: List[Endpoint]) -> Endpoint:
        """Взвешенный выбор endpoint"""
        total_weight = sum(ep.weight for ep in endpoints)
        if total_weight == 0:
            return endpoints[0]
            
        rand = random.randint(1, total_weight)
        current = 0
        
        for ep in endpoints:
            current += ep.weight
            if rand <= current:
                return ep
                
        return endpoints[-1]
        
    def calculate_distance(self, lat1: float, lon1: float,
                          lat2: float, lon2: float) -> float:
        """Расчёт расстояния между точками (км)"""
        R = 6371  # Radius of Earth in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
        
    async def collect_traffic_metrics(self, pool_id: str) -> Optional[TrafficMetrics]:
        """Сбор метрик трафика"""
        pool = self.pools.get(pool_id)
        if not pool:
            return None
            
        total_requests = random.randint(10000, 100000)
        successful = int(total_requests * random.uniform(0.95, 0.999))
        
        metrics = TrafficMetrics(
            metric_id=f"tm_{uuid.uuid4().hex[:8]}",
            pool_id=pool_id,
            total_requests=total_requests,
            successful_requests=successful,
            failed_requests=total_requests - successful,
            avg_latency_ms=random.uniform(20, 100),
            p50_latency_ms=random.uniform(15, 50),
            p95_latency_ms=random.uniform(50, 200),
            p99_latency_ms=random.uniform(100, 500),
            bytes_in=random.randint(1000000, 100000000),
            bytes_out=random.randint(10000000, 1000000000),
            total_connections=random.randint(1000, 10000),
            active_connections=random.randint(100, 5000)
        )
        
        self.traffic_metrics[metrics.metric_id] = metrics
        return metrics
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_regions = len(self.regions)
        active_regions = sum(1 for r in self.regions.values() if r.is_active)
        
        total_endpoints = len(self.endpoints)
        healthy_endpoints = sum(1 for e in self.endpoints.values() if e.status == EndpointStatus.HEALTHY)
        
        total_pools = len(self.pools)
        healthy_pools = sum(1 for p in self.pools.values() if p.is_healthy)
        
        total_policies = len(self.policies)
        enabled_policies = sum(1 for p in self.policies.values() if p.is_enabled)
        
        total_health_checks = len(self.health_checks)
        
        total_dns_records = len(self.dns_records)
        active_records = sum(1 for r in self.dns_records.values() if r.is_active)
        
        total_failover_configs = len(self.failover_configs)
        
        return {
            "total_regions": total_regions,
            "active_regions": active_regions,
            "total_endpoints": total_endpoints,
            "healthy_endpoints": healthy_endpoints,
            "total_pools": total_pools,
            "healthy_pools": healthy_pools,
            "total_policies": total_policies,
            "enabled_policies": enabled_policies,
            "total_health_checks": total_health_checks,
            "total_dns_records": total_dns_records,
            "active_dns_records": active_records,
            "total_failover_configs": total_failover_configs
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 333: Global Load Balancer Platform")
    print("=" * 60)
    
    glb = GlobalLoadBalancer()
    print("✓ Global Load Balancer created")
    
    # Create regions
    print("\n🌍 Creating Regions...")
    
    regions_data = [
        ("US East", "North America", "USA", 37.4419, -122.1430),
        ("US West", "North America", "USA", 47.6062, -122.3321),
        ("EU West", "Europe", "Ireland", 53.3498, -6.2603),
        ("EU Central", "Europe", "Germany", 50.1109, 8.6821),
        ("Asia Pacific", "Asia", "Singapore", 1.3521, 103.8198),
        ("Asia Northeast", "Asia", "Japan", 35.6762, 139.6503),
        ("South America", "South America", "Brazil", -23.5505, -46.6333),
        ("Middle East", "Asia", "UAE", 25.2048, 55.2708)
    ]
    
    regions = []
    for name, continent, country, lat, lon in regions_data:
        region = await glb.create_region(name, continent, country, lat, lon)
        regions.append(region)
        print(f"  🌍 {name} ({continent})")
        
    # Create endpoints
    print("\n🎯 Creating Endpoints...")
    
    endpoints_data = [
        # US East
        (0, "us-east-web-1", "10.0.1.10", 443, 100, 1),
        (0, "us-east-web-2", "10.0.1.11", 443, 100, 1),
        (0, "us-east-web-3", "10.0.1.12", 443, 50, 2),
        # US West
        (1, "us-west-web-1", "10.0.2.10", 443, 100, 1),
        (1, "us-west-web-2", "10.0.2.11", 443, 100, 1),
        # EU West
        (2, "eu-west-web-1", "10.0.3.10", 443, 100, 1),
        (2, "eu-west-web-2", "10.0.3.11", 443, 100, 1),
        (2, "eu-west-web-3", "10.0.3.12", 443, 100, 1),
        # EU Central
        (3, "eu-central-web-1", "10.0.4.10", 443, 100, 1),
        (3, "eu-central-web-2", "10.0.4.11", 443, 100, 1),
        # Asia Pacific
        (4, "ap-web-1", "10.0.5.10", 443, 100, 1),
        (4, "ap-web-2", "10.0.5.11", 443, 100, 1),
        # Asia Northeast
        (5, "ap-ne-web-1", "10.0.6.10", 443, 100, 1),
        (5, "ap-ne-web-2", "10.0.6.11", 443, 100, 1),
        # South America
        (6, "sa-web-1", "10.0.7.10", 443, 100, 1),
        # Middle East
        (7, "me-web-1", "10.0.8.10", 443, 100, 1)
    ]
    
    endpoints = []
    for region_idx, name, ip, port, weight, priority in endpoints_data:
        endpoint = await glb.create_endpoint(name, ip, port, regions[region_idx].region_id, weight, priority)
        if endpoint:
            endpoints.append(endpoint)
            
    print(f"  ✓ Created {len(endpoints)} endpoints")
    
    # Create health checks
    print("\n❤️ Creating Health Checks...")
    
    health_checks_data = [
        ("HTTP Health Check", HealthCheckProtocol.HTTP, "/health", 80, 30, 10),
        ("HTTPS Health Check", HealthCheckProtocol.HTTPS, "/health", 443, 30, 10),
        ("TCP Health Check", HealthCheckProtocol.TCP, "", 443, 15, 5),
        ("API Health Check", HealthCheckProtocol.HTTPS, "/api/status", 443, 60, 15)
    ]
    
    health_checks = []
    for name, protocol, path, port, interval, timeout in health_checks_data:
        check = await glb.create_health_check(name, protocol, path, port, interval, timeout)
        health_checks.append(check)
        print(f"  ❤️ {name} ({protocol.value})")
        
    # Run health checks
    print("\n🔍 Running Health Checks...")
    
    for endpoint in endpoints:
        await glb.run_health_check(endpoint.endpoint_id, health_checks[1].check_id)
        
    print(f"  ✓ Health checks completed for {len(endpoints)} endpoints")
    
    # Create pools
    print("\n🏊 Creating Endpoint Pools...")
    
    pools_data = [
        ("US East Pool", [ep.endpoint_id for ep in endpoints[:3]], RoutingPolicy.ROUND_ROBIN),
        ("US West Pool", [ep.endpoint_id for ep in endpoints[3:5]], RoutingPolicy.WEIGHTED),
        ("EU Pool", [ep.endpoint_id for ep in endpoints[5:10]], RoutingPolicy.LATENCY),
        ("APAC Pool", [ep.endpoint_id for ep in endpoints[10:14]], RoutingPolicy.ROUND_ROBIN),
        ("Global Pool", [ep.endpoint_id for ep in endpoints], RoutingPolicy.GEOGRAPHIC)
    ]
    
    pools = []
    for name, ep_ids, policy in pools_data:
        pool = await glb.create_pool(name, ep_ids, policy, health_checks[1].check_id)
        pools.append(pool)
        await glb.update_pool_health(pool.pool_id)
        print(f"  🏊 {name} ({len(ep_ids)} endpoints, {policy.value})")
        
    # Create failover configs
    print("\n🔄 Creating Failover Configurations...")
    
    failover_configs_data = [
        ("US Failover", pools[0].pool_id, pools[1].pool_id, FailoverStrategy.ACTIVE_PASSIVE, 50.0),
        ("EU Failover", pools[2].pool_id, pools[0].pool_id, FailoverStrategy.ACTIVE_PASSIVE, 40.0),
        ("Global Failover", pools[4].pool_id, pools[2].pool_id, FailoverStrategy.AUTOMATIC, 30.0)
    ]
    
    failover_configs = []
    for name, primary, secondary, strategy, threshold in failover_configs_data:
        config = await glb.create_failover_config(name, primary, secondary, strategy, threshold)
        if config:
            failover_configs.append(config)
            print(f"  🔄 {name} ({strategy.value})")
            
    # Create geo mappings
    print("\n🗺️ Creating Geographic Mappings...")
    
    geo_mappings_data = [
        ("North America", "", "", pools[0].pool_id, 1),
        ("Europe", "", "", pools[2].pool_id, 1),
        ("Asia", "", "", pools[3].pool_id, 1),
        ("", "US", "", pools[0].pool_id, 2),
        ("", "DE", "", pools[2].pool_id, 2),
        ("", "JP", "", pools[3].pool_id, 2),
        ("South America", "", "", pools[4].pool_id, 1)
    ]
    
    geo_mappings = []
    for continent, country, subdivision, pool_id, priority in geo_mappings_data:
        mapping = await glb.create_geo_mapping(continent, country, subdivision, pool_id, priority)
        if mapping:
            geo_mappings.append(mapping)
            loc = continent or country or subdivision
            print(f"  🗺️ {loc} -> Pool")
            
    # Create traffic policies
    print("\n📋 Creating Traffic Policies...")
    
    policies_data = [
        ("Weighted Traffic", RoutingPolicy.WEIGHTED, pools[4].pool_id),
        ("Geographic Traffic", RoutingPolicy.GEOGRAPHIC, pools[4].pool_id),
        ("Latency-based Traffic", RoutingPolicy.LATENCY, pools[4].pool_id),
        ("Failover Traffic", RoutingPolicy.FAILOVER, pools[0].pool_id)
    ]
    
    policies = []
    for name, routing, default_pool in policies_data:
        policy = await glb.create_traffic_policy(name, routing, default_pool)
        if policy:
            policies.append(policy)
            print(f"  📋 {name} ({routing.value})")
            
    # Create DNS records
    print("\n📝 Creating DNS Records...")
    
    dns_records_data = [
        ("www.example.com", RecordType.A, "10.0.1.10", 60, RoutingPolicy.WEIGHTED, 100),
        ("api.example.com", RecordType.A, "10.0.2.10", 30, RoutingPolicy.LATENCY, 100),
        ("cdn.example.com", RecordType.CNAME, "cdn.cloudfront.net", 300, RoutingPolicy.ROUND_ROBIN, 100),
        ("app.example.com", RecordType.A, "10.0.3.10", 60, RoutingPolicy.GEOGRAPHIC, 100),
        ("global.example.com", RecordType.A, "10.0.4.10", 60, RoutingPolicy.FAILOVER, 100)
    ]
    
    dns_records = []
    for name, rtype, value, ttl, routing, weight in dns_records_data:
        record = await glb.create_dns_record(name, rtype, value, ttl, routing, weight)
        dns_records.append(record)
        print(f"  📝 {name} ({rtype.value})")
        
    # Collect metrics
    print("\n📊 Collecting Traffic Metrics...")
    
    metrics = []
    for pool in pools:
        metric = await glb.collect_traffic_metrics(pool.pool_id)
        if metric:
            metrics.append(metric)
            
    print(f"  ✓ Collected metrics for {len(metrics)} pools")
    
    # Check failover status
    print("\n🔄 Checking Failover Status...")
    
    for config in failover_configs:
        triggered = await glb.check_failover(config.config_id)
        status = "triggered" if triggered else "stable"
        print(f"  🔄 {config.name}: {status}")
        
    # Regions
    print("\n🌍 Regions:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Region             │ Continent        │ Country    │ Endpoints │ Connections │ RPS       │ Status            │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for region in regions:
        name = region.name[:18].ljust(18)
        continent = region.continent[:16].ljust(16)
        country = region.country[:10].ljust(10)
        ep_count = str(len(region.endpoint_ids)).ljust(9)
        conns = f"{region.current_connections:,}".ljust(11)
        rps = f"{region.requests_per_second:,}".ljust(9)
        
        status = "✓ Active" if region.is_active else "○ Inactive"
        status = status[:17].ljust(17)
        
        print(f"  │ {name} │ {continent} │ {country} │ {ep_count} │ {conns} │ {rps} │ {status} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Endpoints
    print("\n🎯 Endpoints:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                │ IP Address     │ Port │ Weight │ Priority │ Latency   │ Connections │ Status                         │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for endpoint in endpoints:
        name = endpoint.name[:19].ljust(19)
        ip = endpoint.ip_address[:14].ljust(14)
        port = str(endpoint.port).ljust(4)
        weight = str(endpoint.weight).ljust(6)
        priority = str(endpoint.priority).ljust(8)
        latency = f"{endpoint.avg_latency_ms:.1f}ms".ljust(9)
        conns = f"{endpoint.current_connections}/{endpoint.max_connections}".ljust(11)
        
        status_icon = {
            "healthy": "✓",
            "unhealthy": "✗",
            "degraded": "⚠",
            "draining": "↓",
            "disabled": "○"
        }.get(endpoint.status.value, "?")
        status = f"{status_icon} {endpoint.status.value}"[:30].ljust(30)
        
        print(f"  │ {name} │ {ip} │ {port} │ {weight} │ {priority} │ {latency} │ {conns} │ {status} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Pools
    print("\n🏊 Endpoint Pools:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Pool Name            │ Routing Policy  │ Endpoints │ Healthy │ Session Affinity │ Status                            │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for pool in pools:
        name = pool.name[:20].ljust(20)
        policy = pool.routing_policy.value[:15].ljust(15)
        total = str(len(pool.endpoint_ids)).ljust(9)
        healthy = str(pool.healthy_endpoints).ljust(7)
        affinity = "✓" if pool.session_affinity else "✗"
        affinity = affinity.ljust(16)
        
        status = "✓ Healthy" if pool.is_healthy else "✗ Unhealthy"
        status = status[:35].ljust(35)
        
        print(f"  │ {name} │ {policy} │ {total} │ {healthy} │ {affinity} │ {status} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Traffic Policies
    print("\n📋 Traffic Policies:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Policy Name            │ Routing Policy   │ Default Pool          │ Status                      │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for policy in policies:
        name = policy.name[:22].ljust(22)
        routing = policy.routing_policy.value[:16].ljust(16)
        
        default_pool = "Unknown"
        for p in pools:
            if p.pool_id == policy.default_pool_id:
                default_pool = p.name
                break
        default_pool = default_pool[:21].ljust(21)
        
        status = "✓ Enabled" if policy.is_enabled else "○ Disabled"
        status = status[:27].ljust(27)
        
        print(f"  │ {name} │ {routing} │ {default_pool} │ {status} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # DNS Records
    print("\n📝 DNS Records:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                       │ Type  │ Value                          │ TTL   │ Routing         │ Status           │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for record in dns_records:
        name = record.name[:26].ljust(26)
        rtype = record.record_type.value[:5].ljust(5)
        value = record.value[:30].ljust(30)
        ttl = f"{record.ttl}s".ljust(5)
        routing = record.routing_policy.value[:15].ljust(15)
        
        status = "✓ Active" if record.is_active else "○ Inactive"
        status = status[:16].ljust(16)
        
        print(f"  │ {name} │ {rtype} │ {value} │ {ttl} │ {routing} │ {status} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Failover Configurations
    print("\n🔄 Failover Configurations:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                 │ Strategy          │ Primary Pool        │ Secondary Pool      │ Threshold │ Failovers │ Status               │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for config in failover_configs:
        name = config.name[:20].ljust(20)
        strategy = config.strategy.value[:17].ljust(17)
        
        primary_name = "Unknown"
        secondary_name = "Unknown"
        for p in pools:
            if p.pool_id == config.primary_pool_id:
                primary_name = p.name
            if p.pool_id == config.secondary_pool_id:
                secondary_name = p.name
                
        primary = primary_name[:19].ljust(19)
        secondary = secondary_name[:19].ljust(19)
        threshold = f"{config.failover_threshold:.0f}%".ljust(9)
        failovers = str(config.failover_count).ljust(9)
        
        active_pool = "Primary" if config.current_active_pool == config.primary_pool_id else "Secondary"
        status = f"✓ {active_pool}"[:20].ljust(20)
        
        print(f"  │ {name} │ {strategy} │ {primary} │ {secondary} │ {threshold} │ {failovers} │ {status} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Traffic Metrics
    print("\n📊 Traffic Metrics:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Pool                 │ Requests     │ Success Rate │ Avg Latency │ P95 Latency │ Throughput    │ Active Conns                   │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for i, metric in enumerate(metrics):
        if i < len(pools):
            pool_name = pools[i].name[:20].ljust(20)
        else:
            pool_name = "Unknown"[:20].ljust(20)
            
        requests = f"{metric.total_requests:,}".ljust(12)
        success_rate = f"{(metric.successful_requests/metric.total_requests)*100:.1f}%".ljust(12)
        avg_lat = f"{metric.avg_latency_ms:.1f}ms".ljust(11)
        p95_lat = f"{metric.p95_latency_ms:.1f}ms".ljust(11)
        throughput = f"{(metric.bytes_in + metric.bytes_out) / 1000000:.1f}MB".ljust(13)
        active = f"{metric.active_connections:,}".ljust(30)
        
        print(f"  │ {pool_name} │ {requests} │ {success_rate} │ {avg_lat} │ {p95_lat} │ {throughput} │ {active} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Health Check Results
    print("\n❤️ Health Check Summary:")
    
    healthy_count = sum(1 for e in endpoints if e.status == EndpointStatus.HEALTHY)
    unhealthy_count = sum(1 for e in endpoints if e.status == EndpointStatus.UNHEALTHY)
    degraded_count = sum(1 for e in endpoints if e.status == EndpointStatus.DEGRADED)
    
    print(f"\n  Healthy Endpoints: {healthy_count}")
    print(f"  Unhealthy Endpoints: {unhealthy_count}")
    print(f"  Degraded Endpoints: {degraded_count}")
    
    avg_latency = sum(e.avg_latency_ms for e in endpoints) / len(endpoints) if endpoints else 0
    print(f"  Average Latency: {avg_latency:.1f}ms")
    
    # Statistics
    stats = glb.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Regions: {stats['active_regions']}/{stats['total_regions']} active")
    print(f"  Endpoints: {stats['healthy_endpoints']}/{stats['total_endpoints']} healthy")
    print(f"  Pools: {stats['healthy_pools']}/{stats['total_pools']} healthy")
    print(f"  Policies: {stats['enabled_policies']}/{stats['total_policies']} enabled")
    print(f"  DNS Records: {stats['active_dns_records']}/{stats['total_dns_records']} active")
    print(f"  Failover Configs: {stats['total_failover_configs']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Global Load Balancer Platform                    │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Global Regions:               {stats['active_regions']:>12}                      │")
    print(f"│ Healthy Endpoints:            {stats['healthy_endpoints']:>12}                      │")
    print(f"│ Healthy Pools:                {stats['healthy_pools']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Active DNS Records:           {stats['active_dns_records']:>12}                      │")
    print(f"│ Traffic Policies:             {stats['enabled_policies']:>12}                      │")
    print(f"│ Average Latency:              {avg_latency:>10.1f}ms                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Global Load Balancer Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
