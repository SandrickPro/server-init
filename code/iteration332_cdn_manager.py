#!/usr/bin/env python3
"""
Server Init - Iteration 332: CDN Manager Platform
Платформа управления Content Delivery Network

Функционал:
- Edge Location Management - управление точками присутствия
- Cache Configuration - конфигурация кеширования
- Origin Management - управление источниками
- SSL/TLS Management - управление сертификатами
- Traffic Routing - маршрутизация трафика
- Real-time Analytics - аналитика в реальном времени
- Purge Management - управление очисткой кеша
- Security Features - функции безопасности (WAF, DDoS)
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid


class DistributionStatus(Enum):
    """Статус дистрибуции"""
    DEPLOYED = "deployed"
    DEPLOYING = "deploying"
    DISABLED = "disabled"
    ERROR = "error"


class CachePolicy(Enum):
    """Политика кеширования"""
    AGGRESSIVE = "aggressive"
    STANDARD = "standard"
    MINIMAL = "minimal"
    BYPASS = "bypass"
    CUSTOM = "custom"


class OriginProtocol(Enum):
    """Протокол источника"""
    HTTP = "http"
    HTTPS = "https"
    HTTP_ONLY = "http_only"
    HTTPS_ONLY = "https_only"
    MATCH_VIEWER = "match_viewer"


class SSLPolicy(Enum):
    """Политика SSL"""
    TLS_1_0 = "tls_1_0"
    TLS_1_1 = "tls_1_1"
    TLS_1_2 = "tls_1_2"
    TLS_1_3 = "tls_1_3"


class GeoRestrictionType(Enum):
    """Тип гео-ограничений"""
    NONE = "none"
    WHITELIST = "whitelist"
    BLACKLIST = "blacklist"


class PurgeStatus(Enum):
    """Статус очистки кеша"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class SecurityLevel(Enum):
    """Уровень безопасности"""
    OFF = "off"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CUSTOM = "custom"


@dataclass
class EdgeLocation:
    """Edge-локация (PoP)"""
    location_id: str
    name: str
    
    # Geographic
    city: str = ""
    country: str = ""
    region: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    
    # Capacity
    bandwidth_gbps: float = 100.0
    storage_tb: float = 10.0
    
    # Performance
    avg_latency_ms: float = 10.0
    cache_hit_ratio: float = 0.95
    
    # Status
    is_active: bool = True
    health_score: float = 100.0
    
    # Traffic
    requests_per_second: int = 0
    bytes_transferred_gb: float = 0.0
    
    # Timestamp
    last_health_check: datetime = field(default_factory=datetime.now)


@dataclass
class Origin:
    """Источник контента"""
    origin_id: str
    name: str
    
    # Endpoint
    domain: str = ""
    port: int = 443
    protocol: OriginProtocol = OriginProtocol.HTTPS
    path: str = ""
    
    # Type
    origin_type: str = "custom"  # custom, s3, gcs, azure_blob
    
    # Health check
    health_check_path: str = "/health"
    health_check_interval: int = 30
    health_threshold: int = 3
    
    # Timeouts
    connect_timeout: int = 10
    read_timeout: int = 30
    
    # Status
    is_healthy: bool = True
    last_health_check: datetime = field(default_factory=datetime.now)
    
    # Weight for load balancing
    weight: int = 100
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CacheBehavior:
    """Поведение кеширования"""
    behavior_id: str
    
    # Path pattern
    path_pattern: str = "/*"
    
    # Cache settings
    policy: CachePolicy = CachePolicy.STANDARD
    ttl_seconds: int = 86400  # 24 hours
    min_ttl: int = 0
    max_ttl: int = 31536000  # 1 year
    
    # Cache key
    include_query_string: bool = True
    include_cookies: bool = False
    include_headers: List[str] = field(default_factory=list)
    
    # Compression
    compress_objects: bool = True
    
    # Origin
    origin_id: str = ""
    
    # Protocol
    viewer_protocol_policy: str = "redirect-to-https"
    
    # Priority
    priority: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Distribution:
    """CDN дистрибуция"""
    distribution_id: str
    name: str
    
    # Domain
    domain_name: str = ""
    cname_aliases: List[str] = field(default_factory=list)
    
    # Status
    status: DistributionStatus = DistributionStatus.DISABLED
    
    # Origins
    origin_ids: List[str] = field(default_factory=list)
    default_origin_id: str = ""
    
    # Cache behaviors
    behavior_ids: List[str] = field(default_factory=list)
    
    # SSL
    ssl_certificate_id: str = ""
    ssl_policy: SSLPolicy = SSLPolicy.TLS_1_2
    
    # Security
    waf_enabled: bool = False
    ddos_protection: bool = True
    security_level: SecurityLevel = SecurityLevel.MEDIUM
    
    # Geo restrictions
    geo_restriction_type: GeoRestrictionType = GeoRestrictionType.NONE
    geo_restriction_countries: List[str] = field(default_factory=list)
    
    # HTTP/2 and HTTP/3
    http2_enabled: bool = True
    http3_enabled: bool = False
    
    # Logging
    access_logging: bool = True
    log_bucket: str = ""
    
    # Price class
    price_class: str = "all"  # all, 100, 200
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)


@dataclass
class SSLCertificate:
    """SSL сертификат"""
    certificate_id: str
    name: str
    
    # Domains
    domain_name: str = ""
    san_domains: List[str] = field(default_factory=list)
    
    # Type
    cert_type: str = "managed"  # managed, custom
    
    # Validity
    issued_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=365))
    
    # Status
    is_valid: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PurgeRequest:
    """Запрос очистки кеша"""
    purge_id: str
    
    # Distribution
    distribution_id: str = ""
    
    # Type
    purge_type: str = "path"  # path, all, tag
    
    # Paths or tags
    paths: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Status
    status: PurgeStatus = PurgeStatus.PENDING
    progress: float = 0.0
    
    # Stats
    invalidated_objects: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class WAFRule:
    """WAF правило"""
    rule_id: str
    name: str
    
    # Type
    rule_type: str = "managed"  # managed, custom
    
    # Condition
    condition: str = ""
    
    # Action
    action: str = "block"  # block, allow, count
    
    # Priority
    priority: int = 0
    
    # Status
    is_enabled: bool = True
    
    # Stats
    matches_count: int = 0
    last_matched: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TrafficMetrics:
    """Метрики трафика"""
    metric_id: str
    
    # Distribution
    distribution_id: str = ""
    
    # Time range
    timestamp: datetime = field(default_factory=datetime.now)
    interval_minutes: int = 5
    
    # Requests
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    
    # Bytes
    bytes_downloaded: int = 0
    bytes_uploaded: int = 0
    
    # Errors
    error_4xx: int = 0
    error_5xx: int = 0
    
    # Latency
    avg_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    
    # Bandwidth
    bandwidth_mbps: float = 0.0


@dataclass
class RateLimitRule:
    """Правило ограничения скорости"""
    rule_id: str
    name: str
    
    # Limit
    requests_per_second: int = 100
    burst: int = 200
    
    # Scope
    scope: str = "ip"  # ip, header, path
    header_name: str = ""
    path_pattern: str = ""
    
    # Action
    action: str = "throttle"  # throttle, block
    
    # Status
    is_enabled: bool = True
    
    # Stats
    triggered_count: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


class CDNManager:
    """Менеджер CDN"""
    
    def __init__(self):
        self.edge_locations: Dict[str, EdgeLocation] = {}
        self.origins: Dict[str, Origin] = {}
        self.behaviors: Dict[str, CacheBehavior] = {}
        self.distributions: Dict[str, Distribution] = {}
        self.certificates: Dict[str, SSLCertificate] = {}
        self.purge_requests: Dict[str, PurgeRequest] = {}
        self.waf_rules: Dict[str, WAFRule] = {}
        self.metrics: Dict[str, TrafficMetrics] = {}
        self.rate_limits: Dict[str, RateLimitRule] = {}
        
        # Initialize edge locations
        self._init_edge_locations()
        
    def _init_edge_locations(self):
        """Инициализация edge-локаций"""
        locations_data = [
            ("New York", "USA", "North America", 40.7128, -74.0060, 500.0),
            ("Los Angeles", "USA", "North America", 34.0522, -118.2437, 400.0),
            ("London", "UK", "Europe", 51.5074, -0.1278, 450.0),
            ("Frankfurt", "Germany", "Europe", 50.1109, 8.6821, 350.0),
            ("Paris", "France", "Europe", 48.8566, 2.3522, 300.0),
            ("Tokyo", "Japan", "Asia Pacific", 35.6762, 139.6503, 400.0),
            ("Singapore", "Singapore", "Asia Pacific", 1.3521, 103.8198, 350.0),
            ("Sydney", "Australia", "Asia Pacific", -33.8688, 151.2093, 250.0),
            ("São Paulo", "Brazil", "South America", -23.5505, -46.6333, 200.0),
            ("Mumbai", "India", "Asia Pacific", 19.0760, 72.8777, 300.0),
            ("Seoul", "South Korea", "Asia Pacific", 37.5665, 126.9780, 350.0),
            ("Amsterdam", "Netherlands", "Europe", 52.3676, 4.9041, 400.0),
            ("Toronto", "Canada", "North America", 43.6532, -79.3832, 300.0),
            ("Hong Kong", "China", "Asia Pacific", 22.3193, 114.1694, 400.0),
            ("Dubai", "UAE", "Middle East", 25.2048, 55.2708, 200.0)
        ]
        
        for city, country, region, lat, lon, bw in locations_data:
            loc = EdgeLocation(
                location_id=f"edge_{city.lower().replace(' ', '_')}",
                name=f"{city} PoP",
                city=city,
                country=country,
                region=region,
                latitude=lat,
                longitude=lon,
                bandwidth_gbps=bw,
                avg_latency_ms=random.uniform(5, 30),
                cache_hit_ratio=random.uniform(0.85, 0.98)
            )
            self.edge_locations[loc.location_id] = loc
            
    async def create_origin(self, name: str,
                           domain: str,
                           port: int = 443,
                           protocol: OriginProtocol = OriginProtocol.HTTPS,
                           origin_type: str = "custom") -> Origin:
        """Создание источника"""
        origin = Origin(
            origin_id=f"origin_{uuid.uuid4().hex[:8]}",
            name=name,
            domain=domain,
            port=port,
            protocol=protocol,
            origin_type=origin_type
        )
        
        self.origins[origin.origin_id] = origin
        return origin
        
    async def create_cache_behavior(self, path_pattern: str,
                                   origin_id: str,
                                   policy: CachePolicy = CachePolicy.STANDARD,
                                   ttl_seconds: int = 86400,
                                   compress: bool = True) -> Optional[CacheBehavior]:
        """Создание поведения кеширования"""
        if origin_id not in self.origins:
            return None
            
        behavior = CacheBehavior(
            behavior_id=f"behavior_{uuid.uuid4().hex[:8]}",
            path_pattern=path_pattern,
            origin_id=origin_id,
            policy=policy,
            ttl_seconds=ttl_seconds,
            compress_objects=compress
        )
        
        self.behaviors[behavior.behavior_id] = behavior
        return behavior
        
    async def create_distribution(self, name: str,
                                 domain_name: str,
                                 default_origin_id: str,
                                 cname_aliases: List[str] = None) -> Optional[Distribution]:
        """Создание дистрибуции"""
        if default_origin_id not in self.origins:
            return None
            
        distribution = Distribution(
            distribution_id=f"dist_{uuid.uuid4().hex[:8]}",
            name=name,
            domain_name=domain_name,
            cname_aliases=cname_aliases or [],
            default_origin_id=default_origin_id,
            origin_ids=[default_origin_id],
            status=DistributionStatus.DEPLOYED
        )
        
        self.distributions[distribution.distribution_id] = distribution
        return distribution
        
    async def add_origin_to_distribution(self, distribution_id: str,
                                        origin_id: str) -> bool:
        """Добавление источника в дистрибуцию"""
        dist = self.distributions.get(distribution_id)
        origin = self.origins.get(origin_id)
        
        if not dist or not origin:
            return False
            
        if origin_id not in dist.origin_ids:
            dist.origin_ids.append(origin_id)
            dist.last_modified = datetime.now()
            
        return True
        
    async def add_behavior_to_distribution(self, distribution_id: str,
                                          behavior_id: str) -> bool:
        """Добавление поведения в дистрибуцию"""
        dist = self.distributions.get(distribution_id)
        behavior = self.behaviors.get(behavior_id)
        
        if not dist or not behavior:
            return False
            
        if behavior_id not in dist.behavior_ids:
            dist.behavior_ids.append(behavior_id)
            dist.last_modified = datetime.now()
            
        return True
        
    async def create_certificate(self, name: str,
                                domain_name: str,
                                san_domains: List[str] = None,
                                cert_type: str = "managed") -> SSLCertificate:
        """Создание SSL сертификата"""
        certificate = SSLCertificate(
            certificate_id=f"cert_{uuid.uuid4().hex[:8]}",
            name=name,
            domain_name=domain_name,
            san_domains=san_domains or [],
            cert_type=cert_type
        )
        
        self.certificates[certificate.certificate_id] = certificate
        return certificate
        
    async def attach_certificate(self, distribution_id: str,
                                certificate_id: str) -> bool:
        """Привязка сертификата к дистрибуции"""
        dist = self.distributions.get(distribution_id)
        cert = self.certificates.get(certificate_id)
        
        if not dist or not cert:
            return False
            
        dist.ssl_certificate_id = certificate_id
        dist.last_modified = datetime.now()
        
        return True
        
    async def enable_waf(self, distribution_id: str,
                        security_level: SecurityLevel = SecurityLevel.MEDIUM) -> bool:
        """Включение WAF"""
        dist = self.distributions.get(distribution_id)
        if not dist:
            return False
            
        dist.waf_enabled = True
        dist.security_level = security_level
        dist.last_modified = datetime.now()
        
        return True
        
    async def add_waf_rule(self, name: str,
                          rule_type: str,
                          condition: str,
                          action: str = "block",
                          priority: int = 0) -> WAFRule:
        """Добавление WAF правила"""
        rule = WAFRule(
            rule_id=f"waf_{uuid.uuid4().hex[:8]}",
            name=name,
            rule_type=rule_type,
            condition=condition,
            action=action,
            priority=priority
        )
        
        self.waf_rules[rule.rule_id] = rule
        return rule
        
    async def create_purge_request(self, distribution_id: str,
                                  paths: List[str] = None,
                                  purge_all: bool = False) -> Optional[PurgeRequest]:
        """Создание запроса очистки кеша"""
        if distribution_id not in self.distributions:
            return None
            
        purge = PurgeRequest(
            purge_id=f"purge_{uuid.uuid4().hex[:8]}",
            distribution_id=distribution_id,
            purge_type="all" if purge_all else "path",
            paths=paths or []
        )
        
        self.purge_requests[purge.purge_id] = purge
        
        # Simulate purge execution
        await self._execute_purge(purge.purge_id)
        
        return purge
        
    async def _execute_purge(self, purge_id: str):
        """Выполнение очистки кеша"""
        purge = self.purge_requests.get(purge_id)
        if not purge:
            return
            
        purge.status = PurgeStatus.IN_PROGRESS
        
        # Simulate purge progress
        purge.progress = 100.0
        purge.invalidated_objects = random.randint(100, 10000)
        purge.status = PurgeStatus.COMPLETED
        purge.completed_at = datetime.now()
        
    async def add_rate_limit(self, name: str,
                            rps: int,
                            burst: int,
                            scope: str = "ip",
                            action: str = "throttle") -> RateLimitRule:
        """Добавление правила ограничения скорости"""
        rule = RateLimitRule(
            rule_id=f"ratelimit_{uuid.uuid4().hex[:8]}",
            name=name,
            requests_per_second=rps,
            burst=burst,
            scope=scope,
            action=action
        )
        
        self.rate_limits[rule.rule_id] = rule
        return rule
        
    async def set_geo_restriction(self, distribution_id: str,
                                  restriction_type: GeoRestrictionType,
                                  countries: List[str] = None) -> bool:
        """Установка гео-ограничений"""
        dist = self.distributions.get(distribution_id)
        if not dist:
            return False
            
        dist.geo_restriction_type = restriction_type
        dist.geo_restriction_countries = countries or []
        dist.last_modified = datetime.now()
        
        return True
        
    async def update_edge_health(self, location_id: str,
                                rps: int,
                                bytes_gb: float,
                                health_score: float):
        """Обновление здоровья edge-локации"""
        location = self.edge_locations.get(location_id)
        if location:
            location.requests_per_second = rps
            location.bytes_transferred_gb = bytes_gb
            location.health_score = health_score
            location.last_health_check = datetime.now()
            
    async def collect_metrics(self, distribution_id: str) -> Optional[TrafficMetrics]:
        """Сбор метрик"""
        dist = self.distributions.get(distribution_id)
        if not dist:
            return None
            
        total_requests = random.randint(100000, 1000000)
        cache_hits = int(total_requests * random.uniform(0.85, 0.98))
        
        metrics = TrafficMetrics(
            metric_id=f"metrics_{uuid.uuid4().hex[:8]}",
            distribution_id=distribution_id,
            total_requests=total_requests,
            cache_hits=cache_hits,
            cache_misses=total_requests - cache_hits,
            bytes_downloaded=random.randint(1000000000, 10000000000),
            bytes_uploaded=random.randint(10000000, 100000000),
            error_4xx=random.randint(100, 1000),
            error_5xx=random.randint(10, 100),
            avg_latency_ms=random.uniform(10, 50),
            p95_latency_ms=random.uniform(50, 150),
            p99_latency_ms=random.uniform(100, 300),
            bandwidth_mbps=random.uniform(100, 10000)
        )
        
        self.metrics[metrics.metric_id] = metrics
        return metrics
        
    def get_behaviors_for_distribution(self, distribution_id: str) -> List[CacheBehavior]:
        """Получение поведений для дистрибуции"""
        dist = self.distributions.get(distribution_id)
        if not dist:
            return []
            
        return [self.behaviors[bid] for bid in dist.behavior_ids if bid in self.behaviors]
        
    def calculate_cache_hit_ratio(self, distribution_id: str) -> float:
        """Расчёт коэффициента попадания в кеш"""
        dist_metrics = [m for m in self.metrics.values() if m.distribution_id == distribution_id]
        
        if not dist_metrics:
            return 0.0
            
        total_requests = sum(m.total_requests for m in dist_metrics)
        total_hits = sum(m.cache_hits for m in dist_metrics)
        
        return total_hits / total_requests if total_requests > 0 else 0.0
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_locations = len(self.edge_locations)
        active_locations = sum(1 for l in self.edge_locations.values() if l.is_active)
        
        total_bandwidth = sum(l.bandwidth_gbps for l in self.edge_locations.values())
        
        total_distributions = len(self.distributions)
        deployed = sum(1 for d in self.distributions.values() if d.status == DistributionStatus.DEPLOYED)
        
        total_origins = len(self.origins)
        healthy_origins = sum(1 for o in self.origins.values() if o.is_healthy)
        
        total_certificates = len(self.certificates)
        valid_certs = sum(1 for c in self.certificates.values() if c.is_valid)
        
        waf_enabled = sum(1 for d in self.distributions.values() if d.waf_enabled)
        
        total_purges = len(self.purge_requests)
        completed_purges = sum(1 for p in self.purge_requests.values() if p.status == PurgeStatus.COMPLETED)
        
        total_requests = sum(m.total_requests for m in self.metrics.values())
        total_hits = sum(m.cache_hits for m in self.metrics.values())
        overall_hit_ratio = total_hits / total_requests if total_requests > 0 else 0.0
        
        return {
            "total_locations": total_locations,
            "active_locations": active_locations,
            "total_bandwidth_gbps": total_bandwidth,
            "total_distributions": total_distributions,
            "deployed_distributions": deployed,
            "total_origins": total_origins,
            "healthy_origins": healthy_origins,
            "total_certificates": total_certificates,
            "valid_certificates": valid_certs,
            "waf_enabled_distributions": waf_enabled,
            "total_purge_requests": total_purges,
            "completed_purges": completed_purges,
            "overall_cache_hit_ratio": overall_hit_ratio,
            "total_requests_processed": total_requests
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 332: CDN Manager Platform")
    print("=" * 60)
    
    cdn = CDNManager()
    print(f"✓ CDN Manager created with {len(cdn.edge_locations)} PoPs")
    
    # Simulate edge traffic
    print("\n📡 Simulating Edge Traffic...")
    
    for loc in cdn.edge_locations.values():
        await cdn.update_edge_health(
            loc.location_id,
            random.randint(10000, 100000),
            random.uniform(100, 1000),
            random.uniform(95, 100)
        )
        
    # Create origins
    print("\n🌐 Creating Origins...")
    
    origins_data = [
        ("Primary S3", "my-bucket.s3.amazonaws.com", 443, OriginProtocol.HTTPS, "s3"),
        ("Backup S3", "backup-bucket.s3-us-west-2.amazonaws.com", 443, OriginProtocol.HTTPS, "s3"),
        ("API Server", "api.example.com", 443, OriginProtocol.HTTPS, "custom"),
        ("Static Assets", "static.example.com", 443, OriginProtocol.HTTPS, "custom"),
        ("Video Origin", "video.example.com", 443, OriginProtocol.HTTPS, "custom"),
        ("Media Server", "media.example.com", 443, OriginProtocol.HTTPS, "custom")
    ]
    
    origins = []
    for name, domain, port, protocol, otype in origins_data:
        origin = await cdn.create_origin(name, domain, port, protocol, otype)
        origins.append(origin)
        print(f"  🌐 {name} -> {domain}")
        
    # Create cache behaviors
    print("\n📋 Creating Cache Behaviors...")
    
    behaviors_data = [
        ("/static/*", 0, CachePolicy.AGGRESSIVE, 2592000, True),  # 30 days
        ("/api/*", 0, CachePolicy.BYPASS, 0, False),
        ("/images/*", 0, CachePolicy.AGGRESSIVE, 604800, True),   # 7 days
        ("/video/*", 4, CachePolicy.STANDARD, 86400, False),      # 1 day
        ("/assets/*", 3, CachePolicy.AGGRESSIVE, 2592000, True),  # 30 days
        ("/*", 0, CachePolicy.STANDARD, 86400, True)              # Default
    ]
    
    behaviors = []
    for path, origin_idx, policy, ttl, compress in behaviors_data:
        behavior = await cdn.create_cache_behavior(path, origins[origin_idx].origin_id, policy, ttl, compress)
        if behavior:
            behaviors.append(behavior)
            print(f"  📋 {path} -> TTL {ttl}s, {policy.value}")
            
    # Create distributions
    print("\n🔗 Creating Distributions...")
    
    distributions_data = [
        ("Production CDN", "d1234567890.cloudfront.net", 0, ["cdn.example.com", "assets.example.com"]),
        ("Staging CDN", "d0987654321.cloudfront.net", 0, ["cdn-staging.example.com"]),
        ("Video CDN", "dvideo123456.cloudfront.net", 4, ["video.example.com"]),
        ("API CDN", "dapi789012.cloudfront.net", 2, ["api-cdn.example.com"])
    ]
    
    distributions = []
    for name, domain, origin_idx, aliases in distributions_data:
        dist = await cdn.create_distribution(name, domain, origins[origin_idx].origin_id, aliases)
        if dist:
            distributions.append(dist)
            print(f"  🔗 {name} ({domain})")
            
            # Add behaviors
            for behavior in behaviors[:4]:
                await cdn.add_behavior_to_distribution(dist.distribution_id, behavior.behavior_id)
                
    # Create certificates
    print("\n🔐 Creating SSL Certificates...")
    
    certs_data = [
        ("Primary Cert", "example.com", ["*.example.com", "cdn.example.com"]),
        ("Video Cert", "video.example.com", ["*.video.example.com"]),
        ("API Cert", "api.example.com", ["*.api.example.com"])
    ]
    
    certificates = []
    for name, domain, san in certs_data:
        cert = await cdn.create_certificate(name, domain, san)
        certificates.append(cert)
        print(f"  🔐 {name} -> {domain}")
        
    # Attach certificates
    for i, dist in enumerate(distributions[:3]):
        if i < len(certificates):
            await cdn.attach_certificate(dist.distribution_id, certificates[i].certificate_id)
            
    # Enable WAF
    print("\n🛡️ Enabling WAF...")
    
    for dist in distributions:
        await cdn.enable_waf(dist.distribution_id, SecurityLevel.HIGH)
        print(f"  🛡️ WAF enabled for {dist.name}")
        
    # Add WAF rules
    print("\n📜 Adding WAF Rules...")
    
    waf_rules_data = [
        ("SQL Injection", "managed", "SQLi", "block", 1),
        ("XSS Protection", "managed", "XSS", "block", 2),
        ("Rate Limiting", "custom", "rate > 1000", "throttle", 3),
        ("Bot Protection", "managed", "Bot", "block", 4),
        ("Geo Block", "custom", "geo:RU,CN", "block", 5)
    ]
    
    waf_rules = []
    for name, rtype, condition, action, priority in waf_rules_data:
        rule = await cdn.add_waf_rule(name, rtype, condition, action, priority)
        waf_rules.append(rule)
        print(f"  📜 {name} ({action})")
        
    # Add rate limits
    print("\n⏱️ Adding Rate Limits...")
    
    rate_limits_data = [
        ("Global Rate Limit", 1000, 2000, "ip", "throttle"),
        ("API Rate Limit", 100, 200, "ip", "block"),
        ("Login Rate Limit", 10, 20, "ip", "block")
    ]
    
    rate_limits = []
    for name, rps, burst, scope, action in rate_limits_data:
        rule = await cdn.add_rate_limit(name, rps, burst, scope, action)
        rate_limits.append(rule)
        print(f"  ⏱️ {name}: {rps} RPS")
        
    # Set geo restrictions
    print("\n🌍 Setting Geo Restrictions...")
    
    await cdn.set_geo_restriction(distributions[0].distribution_id, GeoRestrictionType.BLACKLIST, ["KP", "IR"])
    print("  🌍 Production CDN: Blocked KP, IR")
    
    # Create purge requests
    print("\n🗑️ Creating Purge Requests...")
    
    purge_data = [
        (0, ["/static/*", "/images/*"], False),
        (1, ["/api/cache/*"], False),
        (2, None, True)  # Purge all
    ]
    
    purges = []
    for dist_idx, paths, purge_all in purge_data:
        if dist_idx < len(distributions):
            purge = await cdn.create_purge_request(distributions[dist_idx].distribution_id, paths, purge_all)
            if purge:
                purges.append(purge)
                ptype = "all" if purge_all else f"{len(paths)} paths"
                print(f"  🗑️ {distributions[dist_idx].name}: {ptype}")
                
    # Collect metrics
    print("\n📊 Collecting Metrics...")
    
    metrics = []
    for dist in distributions:
        metric = await cdn.collect_metrics(dist.distribution_id)
        if metric:
            metrics.append(metric)
            
    print(f"  ✓ Collected metrics for {len(metrics)} distributions")
    
    # Edge Locations
    print("\n📍 Edge Locations (PoPs):")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Location              │ Region          │ Bandwidth │ Cache Hit │ RPS       │ Traffic GB │ Health  │ Status               │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    sorted_locs = sorted(cdn.edge_locations.values(), key=lambda x: x.bandwidth_gbps, reverse=True)
    
    for loc in sorted_locs:
        name = f"{loc.city}, {loc.country}"[:21].ljust(21)
        region = loc.region[:15].ljust(15)
        bandwidth = f"{loc.bandwidth_gbps:.0f} Gbps".ljust(9)
        hit_ratio = f"{loc.cache_hit_ratio*100:.1f}%".ljust(9)
        rps = f"{loc.requests_per_second:,}".ljust(9)
        traffic = f"{loc.bytes_transferred_gb:.0f}".ljust(10)
        health = f"{loc.health_score:.0f}%".ljust(7)
        
        status = "✓ Active" if loc.is_active else "✗ Inactive"
        status = status[:20].ljust(20)
        
        print(f"  │ {name} │ {region} │ {bandwidth} │ {hit_ratio} │ {rps} │ {traffic} │ {health} │ {status} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Origins
    print("\n🌐 Origins:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name              │ Domain                                  │ Type    │ Protocol │ Status           │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for origin in origins:
        name = origin.name[:17].ljust(17)
        domain = origin.domain[:39].ljust(39)
        otype = origin.origin_type[:7].ljust(7)
        protocol = origin.protocol.value[:8].ljust(8)
        
        status = "✓ Healthy" if origin.is_healthy else "✗ Unhealthy"
        status = status[:16].ljust(16)
        
        print(f"  │ {name} │ {domain} │ {otype} │ {protocol} │ {status} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Distributions
    print("\n🔗 Distributions:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name              │ Domain                           │ Origins │ Behaviors │ WAF     │ SSL       │ Status                       │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for dist in distributions:
        name = dist.name[:17].ljust(17)
        domain = dist.domain_name[:32].ljust(32)
        origins_count = str(len(dist.origin_ids)).ljust(7)
        behaviors_count = str(len(dist.behavior_ids)).ljust(9)
        waf = "✓" if dist.waf_enabled else "✗"
        waf = waf.ljust(7)
        ssl = "✓" if dist.ssl_certificate_id else "✗"
        ssl = ssl.ljust(9)
        
        status_icon = {"deployed": "✓", "deploying": "↻", "disabled": "○", "error": "✗"}.get(dist.status.value, "?")
        status = f"{status_icon} {dist.status.value}"[:28].ljust(28)
        
        print(f"  │ {name} │ {domain} │ {origins_count} │ {behaviors_count} │ {waf} │ {ssl} │ {status} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Cache Behaviors
    print("\n📋 Cache Behaviors:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Path Pattern      │ Policy      │ TTL        │ Query String │ Compress │ Protocol                      │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for behavior in behaviors:
        path = behavior.path_pattern[:17].ljust(17)
        policy = behavior.policy.value[:11].ljust(11)
        
        # Format TTL
        ttl_sec = behavior.ttl_seconds
        if ttl_sec >= 86400:
            ttl = f"{ttl_sec // 86400}d"
        elif ttl_sec >= 3600:
            ttl = f"{ttl_sec // 3600}h"
        else:
            ttl = f"{ttl_sec}s"
        ttl = ttl.ljust(10)
        
        query = "✓" if behavior.include_query_string else "✗"
        query = query.ljust(12)
        compress = "✓" if behavior.compress_objects else "✗"
        compress = compress.ljust(8)
        protocol = behavior.viewer_protocol_policy[:29].ljust(29)
        
        print(f"  │ {path} │ {policy} │ {ttl} │ {query} │ {compress} │ {protocol} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # SSL Certificates
    print("\n🔐 SSL Certificates:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name              │ Domain                    │ Type     │ Expires              │ Status    │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for cert in certificates:
        name = cert.name[:17].ljust(17)
        domain = cert.domain_name[:25].ljust(25)
        ctype = cert.cert_type[:8].ljust(8)
        expires = cert.expires_at.strftime("%Y-%m-%d")[:20].ljust(20)
        
        status = "✓ Valid" if cert.is_valid else "✗ Invalid"
        status = status[:9].ljust(9)
        
        print(f"  │ {name} │ {domain} │ {ctype} │ {expires} │ {status} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Traffic Metrics
    print("\n📊 Traffic Metrics:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Distribution        │ Requests     │ Cache Hits   │ Hit Ratio │ Avg Latency │ P95 Latency │ Bandwidth   │ Errors                    │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for i, metric in enumerate(metrics):
        if i < len(distributions):
            name = distributions[i].name[:19].ljust(19)
        else:
            name = "Unknown"[:19].ljust(19)
            
        requests = f"{metric.total_requests:,}"[:12].ljust(12)
        hits = f"{metric.cache_hits:,}"[:12].ljust(12)
        hit_ratio = f"{(metric.cache_hits/metric.total_requests)*100:.1f}%".ljust(9)
        avg_lat = f"{metric.avg_latency_ms:.1f}ms".ljust(11)
        p95_lat = f"{metric.p95_latency_ms:.1f}ms".ljust(11)
        bandwidth = f"{metric.bandwidth_mbps:.0f}Mbps".ljust(11)
        errors = f"4xx:{metric.error_4xx} 5xx:{metric.error_5xx}"[:25].ljust(25)
        
        print(f"  │ {name} │ {requests} │ {hits} │ {hit_ratio} │ {avg_lat} │ {p95_lat} │ {bandwidth} │ {errors} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # WAF Rules
    print("\n🛡️ WAF Rules:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Rule Name             │ Type     │ Condition              │ Action    │ Status            │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for rule in waf_rules:
        name = rule.name[:21].ljust(21)
        rtype = rule.rule_type[:8].ljust(8)
        condition = rule.condition[:22].ljust(22)
        action = rule.action[:9].ljust(9)
        
        status = "✓ Enabled" if rule.is_enabled else "○ Disabled"
        status = status[:17].ljust(17)
        
        print(f"  │ {name} │ {rtype} │ {condition} │ {action} │ {status} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Purge Requests
    print("\n🗑️ Purge Requests:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Distribution        │ Type     │ Paths/Tags                        │ Objects    │ Status                      │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for purge in purges:
        dist_name = "Unknown"
        for d in distributions:
            if d.distribution_id == purge.distribution_id:
                dist_name = d.name
                break
        dist_name = dist_name[:19].ljust(19)
        
        ptype = purge.purge_type[:8].ljust(8)
        paths = ", ".join(purge.paths[:2]) if purge.paths else "All"
        paths = paths[:35].ljust(35)
        objects = f"{purge.invalidated_objects:,}".ljust(10)
        
        status_icon = {"completed": "✓", "in_progress": "↻", "pending": "○", "failed": "✗"}.get(purge.status.value, "?")
        status = f"{status_icon} {purge.status.value}"[:27].ljust(27)
        
        print(f"  │ {dist_name} │ {ptype} │ {paths} │ {objects} │ {status} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Statistics
    stats = cdn.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Edge Locations: {stats['active_locations']}/{stats['total_locations']} active")
    print(f"  Total Bandwidth Capacity: {stats['total_bandwidth_gbps']:.0f} Gbps")
    print(f"  Distributions: {stats['deployed_distributions']}/{stats['total_distributions']} deployed")
    print(f"  Origins: {stats['healthy_origins']}/{stats['total_origins']} healthy")
    print(f"  SSL Certificates: {stats['valid_certificates']}/{stats['total_certificates']} valid")
    print(f"  WAF Enabled: {stats['waf_enabled_distributions']} distributions")
    print(f"  Overall Cache Hit Ratio: {stats['overall_cache_hit_ratio']*100:.1f}%")
    print(f"  Total Requests Processed: {stats['total_requests_processed']:,}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                       CDN Manager Platform                         │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Global PoPs:                  {stats['active_locations']:>12}                      │")
    print(f"│ Total Bandwidth:              {stats['total_bandwidth_gbps']:>8.0f} Gbps                    │")
    print(f"│ Active Distributions:         {stats['deployed_distributions']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Cache Hit Ratio:              {stats['overall_cache_hit_ratio']*100:>11.1f}%                     │")
    print(f"│ WAF Protected:                {stats['waf_enabled_distributions']:>12}                      │")
    print(f"│ Total Requests:               {stats['total_requests_processed']:>12,}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("CDN Manager Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
