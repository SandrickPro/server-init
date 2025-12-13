#!/usr/bin/env python3
"""
Server Init - Iteration 63: Edge Computing & CDN Platform
Граничные вычисления и сеть доставки контента

Функционал:
- Edge Locations - граничные точки
- CDN Distribution - распределение контента
- Cache Management - управление кэшем
- Edge Functions - функции на границе
- Traffic Routing - маршрутизация трафика
- Origin Shield - защита источника
- Real-Time Analytics - аналитика в реальном времени
- Geo-Distribution - гео-распределение
"""

import json
import asyncio
import hashlib
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from collections import defaultdict
import uuid
import random


class EdgeLocationStatus(Enum):
    """Статус граничной точки"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DEGRADED = "degraded"


class CacheStatus(Enum):
    """Статус кэша"""
    HIT = "hit"
    MISS = "miss"
    STALE = "stale"
    BYPASS = "bypass"
    EXPIRED = "expired"


class RoutingPolicy(Enum):
    """Политика маршрутизации"""
    LATENCY = "latency"
    GEO = "geo"
    WEIGHTED = "weighted"
    FAILOVER = "failover"


class PurgeType(Enum):
    """Тип очистки кэша"""
    URL = "url"
    TAG = "tag"
    PREFIX = "prefix"
    ALL = "all"


@dataclass
class EdgeLocation:
    """Граничная точка"""
    location_id: str
    name: str
    
    # Местоположение
    region: str = ""
    city: str = ""
    country: str = ""
    continent: str = ""
    
    # Координаты
    latitude: float = 0.0
    longitude: float = 0.0
    
    # Статус
    status: EdgeLocationStatus = EdgeLocationStatus.ACTIVE
    
    # Характеристики
    capacity_gbps: float = 100.0
    current_load: float = 0.0
    
    # Время отклика
    avg_latency_ms: float = 5.0
    
    # Кэш
    cache_size_gb: float = 500.0
    cache_used_gb: float = 0.0


@dataclass
class CacheEntry:
    """Запись кэша"""
    cache_key: str
    
    # Контент
    content_hash: str = ""
    content_type: str = ""
    content_size: int = 0
    
    # TTL
    ttl_seconds: int = 3600
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=1))
    
    # Метаданные
    headers: Dict[str, str] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    # Статистика
    hit_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)


@dataclass
class Origin:
    """Источник контента"""
    origin_id: str
    name: str
    
    # Конфигурация
    origin_type: str = "http"  # http, s3, custom
    domain: str = ""
    port: int = 443
    protocol: str = "https"
    
    # Путь
    path_prefix: str = ""
    
    # Здоровье
    health_check_path: str = "/health"
    healthy: bool = True
    
    # Таймауты
    connect_timeout_ms: int = 5000
    read_timeout_ms: int = 30000


@dataclass
class Distribution:
    """Дистрибуция CDN"""
    distribution_id: str
    name: str
    
    # Домены
    domains: List[str] = field(default_factory=list)
    
    # Origins
    origins: List[str] = field(default_factory=list)  # Origin IDs
    
    # Поведения кэширования
    cache_behaviors: List[Dict[str, Any]] = field(default_factory=list)
    
    # Маршрутизация
    routing_policy: RoutingPolicy = RoutingPolicy.LATENCY
    
    # Статус
    enabled: bool = True
    
    # SSL
    ssl_certificate: str = ""
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class EdgeFunction:
    """Функция на границе"""
    function_id: str
    name: str
    
    # Код
    runtime: str = "javascript"
    code: str = ""
    
    # Триггер
    trigger: str = "viewer-request"  # viewer-request, viewer-response, origin-request, origin-response
    
    # Ресурсы
    memory_mb: int = 128
    timeout_ms: int = 5000
    
    # Статус
    enabled: bool = True
    
    # Версия
    version: int = 1
    
    # Время
    deployed_at: Optional[datetime] = None


@dataclass
class TrafficMetrics:
    """Метрики трафика"""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Запросы
    requests: int = 0
    bytes_served: int = 0
    
    # Кэш
    cache_hits: int = 0
    cache_misses: int = 0
    cache_hit_ratio: float = 0.0
    
    # Latency
    avg_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    
    # Ошибки
    errors_4xx: int = 0
    errors_5xx: int = 0
    
    # По регионам
    by_region: Dict[str, int] = field(default_factory=dict)


@dataclass
class RequestLog:
    """Лог запроса"""
    request_id: str
    
    # Запрос
    method: str = "GET"
    uri: str = ""
    query_string: str = ""
    
    # Клиент
    client_ip: str = ""
    user_agent: str = ""
    country: str = ""
    
    # Ответ
    status_code: int = 200
    bytes_sent: int = 0
    
    # Кэш
    cache_status: CacheStatus = CacheStatus.MISS
    
    # Время
    timestamp: datetime = field(default_factory=datetime.now)
    latency_ms: float = 0.0
    
    # Edge
    edge_location: str = ""


class CacheManager:
    """Менеджер кэша"""
    
    def __init__(self):
        self.caches: Dict[str, Dict[str, CacheEntry]] = {}  # location_id -> cache_key -> entry
        self.tags_index: Dict[str, Set[str]] = defaultdict(set)  # tag -> cache_keys
        
    def get(self, location_id: str, cache_key: str) -> tuple:
        """Получение из кэша"""
        cache = self.caches.get(location_id, {})
        entry = cache.get(cache_key)
        
        if not entry:
            return None, CacheStatus.MISS
            
        now = datetime.now()
        
        if entry.expires_at < now:
            return entry, CacheStatus.EXPIRED
            
        entry.hit_count += 1
        entry.last_accessed = now
        
        return entry, CacheStatus.HIT
        
    def put(self, location_id: str, cache_key: str, content_hash: str,
             content_type: str, content_size: int,
             ttl_seconds: int = 3600, tags: List[str] = None,
             headers: Dict[str, str] = None):
        """Сохранение в кэш"""
        if location_id not in self.caches:
            self.caches[location_id] = {}
            
        now = datetime.now()
        
        entry = CacheEntry(
            cache_key=cache_key,
            content_hash=content_hash,
            content_type=content_type,
            content_size=content_size,
            ttl_seconds=ttl_seconds,
            created_at=now,
            expires_at=now + timedelta(seconds=ttl_seconds),
            headers=headers or {},
            tags=tags or []
        )
        
        self.caches[location_id][cache_key] = entry
        
        # Индексируем теги
        for tag in entry.tags:
            self.tags_index[tag].add(f"{location_id}:{cache_key}")
            
    def purge(self, purge_type: PurgeType, value: str,
               location_id: str = None) -> int:
        """Очистка кэша"""
        purged = 0
        
        locations = [location_id] if location_id else list(self.caches.keys())
        
        for loc in locations:
            if loc not in self.caches:
                continue
                
            cache = self.caches[loc]
            keys_to_delete = []
            
            if purge_type == PurgeType.URL:
                if value in cache:
                    keys_to_delete.append(value)
                    
            elif purge_type == PurgeType.PREFIX:
                keys_to_delete = [k for k in cache if k.startswith(value)]
                
            elif purge_type == PurgeType.TAG:
                for key, entry in cache.items():
                    if value in entry.tags:
                        keys_to_delete.append(key)
                        
            elif purge_type == PurgeType.ALL:
                keys_to_delete = list(cache.keys())
                
            for key in keys_to_delete:
                del cache[key]
                purged += 1
                
        return purged
        
    def get_stats(self, location_id: str = None) -> Dict[str, Any]:
        """Статистика кэша"""
        if location_id:
            caches = {location_id: self.caches.get(location_id, {})}
        else:
            caches = self.caches
            
        total_entries = 0
        total_size = 0
        total_hits = 0
        
        for cache in caches.values():
            total_entries += len(cache)
            for entry in cache.values():
                total_size += entry.content_size
                total_hits += entry.hit_count
                
        return {
            "total_entries": total_entries,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "total_hits": total_hits
        }


class EdgeFunctionRuntime:
    """Среда выполнения Edge Functions"""
    
    def __init__(self):
        self.functions: Dict[str, EdgeFunction] = {}
        self.execution_logs: List[Dict[str, Any]] = []
        
    def deploy(self, name: str, code: str, trigger: str,
                runtime: str = "javascript", **kwargs) -> EdgeFunction:
        """Деплой функции"""
        function = EdgeFunction(
            function_id=f"func_{uuid.uuid4().hex[:8]}",
            name=name,
            code=code,
            trigger=trigger,
            runtime=runtime,
            deployed_at=datetime.now(),
            **kwargs
        )
        
        self.functions[name] = function
        return function
        
    async def execute(self, function_name: str, event: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение функции"""
        function = self.functions.get(function_name)
        
        if not function or not function.enabled:
            return {"error": "Function not found or disabled"}
            
        start_time = time.time()
        
        # Симуляция выполнения
        await asyncio.sleep(0.01)
        
        duration_ms = (time.time() - start_time) * 1000
        
        # Логирование
        self.execution_logs.append({
            "function_id": function.function_id,
            "function_name": function_name,
            "trigger": function.trigger,
            "duration_ms": duration_ms,
            "timestamp": datetime.now()
        })
        
        # Пример результата для разных триггеров
        if function.trigger == "viewer-request":
            return {
                "status": "continue",
                "request": event.get("request", {}),
                "modified": False
            }
        elif function.trigger == "viewer-response":
            return {
                "status": "continue",
                "response": event.get("response", {}),
                "headers_added": {}
            }
            
        return {"status": "ok"}


class TrafficRouter:
    """Маршрутизатор трафика"""
    
    def __init__(self):
        self.edges: Dict[str, EdgeLocation] = {}
        self.health_checks: Dict[str, bool] = {}
        
    def add_edge(self, edge: EdgeLocation):
        """Добавление edge location"""
        self.edges[edge.location_id] = edge
        self.health_checks[edge.location_id] = edge.status == EdgeLocationStatus.ACTIVE
        
    def route(self, client_location: Dict[str, Any],
               policy: RoutingPolicy) -> Optional[EdgeLocation]:
        """Маршрутизация к оптимальному edge"""
        available = [
            e for e in self.edges.values()
            if e.status == EdgeLocationStatus.ACTIVE
            and self.health_checks.get(e.location_id, False)
        ]
        
        if not available:
            return None
            
        if policy == RoutingPolicy.LATENCY:
            # Выбираем по минимальной задержке (учитываем расстояние)
            return min(available, key=lambda e: self._estimate_latency(e, client_location))
            
        elif policy == RoutingPolicy.GEO:
            # Выбираем по географической близости
            client_country = client_location.get("country", "")
            same_country = [e for e in available if e.country == client_country]
            
            if same_country:
                return same_country[0]
                
            client_continent = client_location.get("continent", "")
            same_continent = [e for e in available if e.continent == client_continent]
            
            if same_continent:
                return same_continent[0]
                
            return available[0]
            
        elif policy == RoutingPolicy.WEIGHTED:
            # Взвешенный выбор по свободной емкости
            weights = [(e, e.capacity_gbps - e.current_load) for e in available]
            total = sum(w[1] for w in weights)
            
            if total <= 0:
                return available[0]
                
            r = random.random() * total
            cumulative = 0
            
            for edge, weight in weights:
                cumulative += weight
                if r <= cumulative:
                    return edge
                    
            return available[0]
            
        elif policy == RoutingPolicy.FAILOVER:
            # Возвращаем первый здоровый
            return available[0]
            
        return available[0]
        
    def _estimate_latency(self, edge: EdgeLocation,
                           client_location: Dict[str, Any]) -> float:
        """Оценка задержки"""
        # Упрощённая формула на основе расстояния
        client_lat = client_location.get("latitude", 0)
        client_lon = client_location.get("longitude", 0)
        
        # Грубое расстояние
        lat_diff = abs(edge.latitude - client_lat)
        lon_diff = abs(edge.longitude - client_lon)
        distance = (lat_diff ** 2 + lon_diff ** 2) ** 0.5
        
        # ~0.1ms на градус + базовая задержка edge
        return edge.avg_latency_ms + distance * 0.1


class AnalyticsCollector:
    """Сборщик аналитики"""
    
    def __init__(self):
        self.request_logs: List[RequestLog] = []
        self.metrics_history: List[TrafficMetrics] = []
        
    def log_request(self, **kwargs) -> RequestLog:
        """Логирование запроса"""
        log = RequestLog(
            request_id=f"req_{uuid.uuid4().hex[:8]}",
            **kwargs
        )
        
        self.request_logs.append(log)
        
        # Ограничиваем размер
        if len(self.request_logs) > 100000:
            self.request_logs = self.request_logs[-50000:]
            
        return log
        
    def aggregate_metrics(self, window_minutes: int = 5) -> TrafficMetrics:
        """Агрегация метрик"""
        cutoff = datetime.now() - timedelta(minutes=window_minutes)
        
        recent_logs = [l for l in self.request_logs if l.timestamp > cutoff]
        
        if not recent_logs:
            return TrafficMetrics()
            
        cache_hits = len([l for l in recent_logs if l.cache_status == CacheStatus.HIT])
        cache_misses = len([l for l in recent_logs if l.cache_status == CacheStatus.MISS])
        
        latencies = sorted([l.latency_ms for l in recent_logs])
        
        by_region = defaultdict(int)
        for log in recent_logs:
            by_region[log.country] += 1
            
        metrics = TrafficMetrics(
            requests=len(recent_logs),
            bytes_served=sum(l.bytes_sent for l in recent_logs),
            cache_hits=cache_hits,
            cache_misses=cache_misses,
            cache_hit_ratio=cache_hits / len(recent_logs) if recent_logs else 0,
            avg_latency_ms=sum(latencies) / len(latencies),
            p95_latency_ms=latencies[int(len(latencies) * 0.95)] if latencies else 0,
            p99_latency_ms=latencies[int(len(latencies) * 0.99)] if latencies else 0,
            errors_4xx=len([l for l in recent_logs if 400 <= l.status_code < 500]),
            errors_5xx=len([l for l in recent_logs if 500 <= l.status_code < 600]),
            by_region=dict(by_region)
        )
        
        self.metrics_history.append(metrics)
        
        return metrics


class CDNPlatform:
    """Платформа CDN"""
    
    def __init__(self):
        self.distributions: Dict[str, Distribution] = {}
        self.origins: Dict[str, Origin] = {}
        
        self.cache_manager = CacheManager()
        self.traffic_router = TrafficRouter()
        self.edge_functions = EdgeFunctionRuntime()
        self.analytics = AnalyticsCollector()
        
        # Инициализация edge locations
        self._init_edge_locations()
        
    def _init_edge_locations(self):
        """Инициализация edge точек"""
        locations = [
            ("edge_us_east", "US East", "us-east-1", "New York", "US", "NA", 40.7, -74.0),
            ("edge_us_west", "US West", "us-west-2", "Los Angeles", "US", "NA", 34.0, -118.2),
            ("edge_eu_west", "EU West", "eu-west-1", "Dublin", "IE", "EU", 53.3, -6.2),
            ("edge_eu_central", "EU Central", "eu-central-1", "Frankfurt", "DE", "EU", 50.1, 8.7),
            ("edge_asia_east", "Asia East", "ap-northeast-1", "Tokyo", "JP", "AS", 35.7, 139.7),
            ("edge_asia_south", "Asia South", "ap-south-1", "Mumbai", "IN", "AS", 19.0, 72.9),
        ]
        
        for lid, name, region, city, country, continent, lat, lon in locations:
            edge = EdgeLocation(
                location_id=lid,
                name=name,
                region=region,
                city=city,
                country=country,
                continent=continent,
                latitude=lat,
                longitude=lon
            )
            self.traffic_router.add_edge(edge)
            
    def create_origin(self, name: str, domain: str, **kwargs) -> Origin:
        """Создание origin"""
        origin = Origin(
            origin_id=f"origin_{uuid.uuid4().hex[:8]}",
            name=name,
            domain=domain,
            **kwargs
        )
        
        self.origins[origin.origin_id] = origin
        return origin
        
    def create_distribution(self, name: str, domains: List[str],
                             origins: List[str], **kwargs) -> Distribution:
        """Создание дистрибуции"""
        distribution = Distribution(
            distribution_id=f"dist_{uuid.uuid4().hex[:8]}",
            name=name,
            domains=domains,
            origins=origins,
            **kwargs
        )
        
        self.distributions[distribution.distribution_id] = distribution
        return distribution
        
    async def handle_request(self, distribution_id: str,
                              request: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка запроса"""
        distribution = self.distributions.get(distribution_id)
        
        if not distribution or not distribution.enabled:
            return {"status": 404, "error": "Distribution not found"}
            
        start_time = time.time()
        
        # Определяем edge location
        client_location = request.get("client_location", {})
        edge = self.traffic_router.route(client_location, distribution.routing_policy)
        
        if not edge:
            return {"status": 503, "error": "No available edge"}
            
        uri = request.get("uri", "/")
        cache_key = self._generate_cache_key(distribution_id, uri, request.get("query", {}))
        
        # Проверяем кэш
        entry, cache_status = self.cache_manager.get(edge.location_id, cache_key)
        
        response = {
            "status": 200,
            "edge_location": edge.location_id,
            "cache_status": cache_status.value,
            "headers": {}
        }
        
        if cache_status == CacheStatus.HIT:
            response["content_hash"] = entry.content_hash
            response["content_type"] = entry.content_type
            response["headers"]["X-Cache"] = "HIT"
        else:
            # Fetch from origin
            origin = self._select_origin(distribution)
            
            if origin:
                # Симуляция fetch
                await asyncio.sleep(0.05)
                
                content_hash = hashlib.md5(uri.encode()).hexdigest()
                content_type = "text/html"
                content_size = random.randint(1000, 50000)
                
                # Сохраняем в кэш
                self.cache_manager.put(
                    edge.location_id,
                    cache_key,
                    content_hash,
                    content_type,
                    content_size,
                    ttl_seconds=3600
                )
                
                response["content_hash"] = content_hash
                response["content_type"] = content_type
                response["headers"]["X-Cache"] = "MISS"
            else:
                response["status"] = 502
                response["error"] = "Origin unavailable"
                
        latency_ms = (time.time() - start_time) * 1000
        
        # Логирование
        self.analytics.log_request(
            method=request.get("method", "GET"),
            uri=uri,
            client_ip=request.get("client_ip", ""),
            user_agent=request.get("user_agent", ""),
            country=client_location.get("country", ""),
            status_code=response["status"],
            bytes_sent=random.randint(1000, 50000),
            cache_status=cache_status,
            latency_ms=latency_ms,
            edge_location=edge.location_id
        )
        
        response["latency_ms"] = latency_ms
        
        return response
        
    def _generate_cache_key(self, distribution_id: str, uri: str,
                             query: Dict[str, Any]) -> str:
        """Генерация ключа кэша"""
        key_parts = [distribution_id, uri]
        
        if query:
            sorted_query = sorted(query.items())
            key_parts.append(str(sorted_query))
            
        return hashlib.md5(":".join(key_parts).encode()).hexdigest()
        
    def _select_origin(self, distribution: Distribution) -> Optional[Origin]:
        """Выбор origin"""
        for origin_id in distribution.origins:
            origin = self.origins.get(origin_id)
            if origin and origin.healthy:
                return origin
        return None
        
    def purge_cache(self, distribution_id: str, purge_type: PurgeType,
                     value: str) -> Dict[str, Any]:
        """Очистка кэша"""
        purged = self.cache_manager.purge(purge_type, value)
        
        return {
            "distribution_id": distribution_id,
            "purge_type": purge_type.value,
            "value": value,
            "purged_entries": purged
        }
        
    def get_stats(self) -> Dict[str, Any]:
        """Статистика платформы"""
        cache_stats = self.cache_manager.get_stats()
        metrics = self.analytics.aggregate_metrics()
        
        return {
            "distributions": len(self.distributions),
            "origins": len(self.origins),
            "edge_locations": len(self.traffic_router.edges),
            "edge_functions": len(self.edge_functions.functions),
            "cache": cache_stats,
            "traffic": {
                "requests": metrics.requests,
                "bytes_served": metrics.bytes_served,
                "cache_hit_ratio": round(metrics.cache_hit_ratio * 100, 2),
                "avg_latency_ms": round(metrics.avg_latency_ms, 2),
                "p95_latency_ms": round(metrics.p95_latency_ms, 2),
                "error_rate": round((metrics.errors_4xx + metrics.errors_5xx) / max(metrics.requests, 1) * 100, 2)
            }
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 63: Edge Computing & CDN Platform")
    print("=" * 60)
    
    async def demo():
        # Создание платформы
        cdn = CDNPlatform()
        print("✓ CDN Platform created")
        
        # Edge locations
        print(f"\n🌍 Edge Locations: {len(cdn.traffic_router.edges)}")
        for edge in cdn.traffic_router.edges.values():
            print(f"  ✓ {edge.name} ({edge.city}, {edge.country})")
            
        # Создание origin
        print("\n📦 Creating origins...")
        
        origin1 = cdn.create_origin(
            name="primary-origin",
            domain="origin.example.com",
            port=443,
            protocol="https",
            health_check_path="/health"
        )
        print(f"  ✓ Origin: {origin1.name} ({origin1.domain})")
        
        origin2 = cdn.create_origin(
            name="backup-origin",
            domain="backup.example.com",
            port=443,
            protocol="https"
        )
        print(f"  ✓ Origin: {origin2.name} ({origin2.domain})")
        
        # Создание дистрибуции
        print("\n📡 Creating distribution...")
        
        distribution = cdn.create_distribution(
            name="main-cdn",
            domains=["cdn.example.com", "static.example.com"],
            origins=[origin1.origin_id, origin2.origin_id],
            routing_policy=RoutingPolicy.LATENCY,
            cache_behaviors=[
                {"path_pattern": "*.js", "ttl": 86400, "compress": True},
                {"path_pattern": "*.css", "ttl": 86400, "compress": True},
                {"path_pattern": "*.jpg", "ttl": 604800},
                {"path_pattern": "/api/*", "ttl": 0, "forward_all_headers": True}
            ]
        )
        print(f"  ✓ Distribution: {distribution.name}")
        print(f"  Domains: {', '.join(distribution.domains)}")
        
        # Edge Function
        print("\n⚡ Deploying edge function...")
        
        edge_func = cdn.edge_functions.deploy(
            name="add-security-headers",
            trigger="viewer-response",
            runtime="javascript",
            code="""
            function handler(event) {
                const response = event.response;
                response.headers['x-frame-options'] = [{value: 'DENY'}];
                response.headers['x-content-type-options'] = [{value: 'nosniff'}];
                return response;
            }
            """,
            memory_mb=128
        )
        print(f"  ✓ Function: {edge_func.name} (trigger: {edge_func.trigger})")
        
        # Симуляция запросов
        print("\n🌐 Simulating requests...")
        
        client_locations = [
            {"country": "US", "continent": "NA", "latitude": 40.7, "longitude": -74.0},
            {"country": "DE", "continent": "EU", "latitude": 52.5, "longitude": 13.4},
            {"country": "JP", "continent": "AS", "latitude": 35.7, "longitude": 139.7},
            {"country": "IN", "continent": "AS", "latitude": 28.6, "longitude": 77.2},
        ]
        
        uris = ["/index.html", "/assets/app.js", "/images/logo.png", "/api/data"]
        
        results = defaultdict(int)
        
        for _ in range(100):
            location = random.choice(client_locations)
            uri = random.choice(uris)
            
            response = await cdn.handle_request(
                distribution.distribution_id,
                {
                    "method": "GET",
                    "uri": uri,
                    "client_location": location,
                    "client_ip": f"192.168.{random.randint(1,255)}.{random.randint(1,255)}",
                    "user_agent": "Mozilla/5.0"
                }
            )
            
            results[response["cache_status"]] += 1
            
        print(f"  Requests: 100")
        print(f"  Cache HIT: {results['hit']}")
        print(f"  Cache MISS: {results['miss']}")
        
        # Тест маршрутизации
        print("\n🔀 Testing routing...")
        
        for loc in client_locations[:3]:
            edge = cdn.traffic_router.route(loc, RoutingPolicy.LATENCY)
            print(f"  Client {loc['country']} -> {edge.name} ({edge.city})")
            
        # Очистка кэша
        print("\n🗑️ Cache purge...")
        
        purge_result = cdn.purge_cache(
            distribution.distribution_id,
            PurgeType.PREFIX,
            "/images/"
        )
        print(f"  Purged: {purge_result['purged_entries']} entries")
        
        # Статистика кэша
        print("\n📊 Cache Statistics:")
        cache_stats = cdn.cache_manager.get_stats()
        print(f"  Entries: {cache_stats['total_entries']}")
        print(f"  Size: {cache_stats['total_size_mb']} MB")
        print(f"  Total hits: {cache_stats['total_hits']}")
        
        # Метрики трафика
        print("\n📈 Traffic Metrics:")
        metrics = cdn.analytics.aggregate_metrics(window_minutes=60)
        print(f"  Requests: {metrics.requests}")
        print(f"  Bytes served: {metrics.bytes_served:,}")
        print(f"  Cache hit ratio: {metrics.cache_hit_ratio * 100:.1f}%")
        print(f"  Avg latency: {metrics.avg_latency_ms:.2f}ms")
        print(f"  P95 latency: {metrics.p95_latency_ms:.2f}ms")
        
        # Статистика по странам
        if metrics.by_region:
            print("\n  By country:")
            for country, count in sorted(metrics.by_region.items(), key=lambda x: -x[1])[:5]:
                print(f"    {country}: {count} requests")
                
        # Общая статистика
        print("\n📈 Platform Statistics:")
        stats = cdn.get_stats()
        print(f"  Distributions: {stats['distributions']}")
        print(f"  Origins: {stats['origins']}")
        print(f"  Edge locations: {stats['edge_locations']}")
        print(f"  Edge functions: {stats['edge_functions']}")
        print(f"  Traffic:")
        print(f"    Cache hit ratio: {stats['traffic']['cache_hit_ratio']}%")
        print(f"    Avg latency: {stats['traffic']['avg_latency_ms']}ms")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Edge Computing & CDN Platform initialized!")
    print("=" * 60)
