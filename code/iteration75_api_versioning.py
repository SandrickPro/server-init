#!/usr/bin/env python3
"""
Server Init - Iteration 75: API Versioning & Lifecycle Management
Управление версиями API и жизненным циклом

Функционал:
- Version Management - управление версиями
- Deprecation Policies - политики устаревания
- Migration Paths - пути миграции
- Compatibility Checking - проверка совместимости
- API Documentation - документация API
- Traffic Routing - маршрутизация по версиям
- Sunset Notifications - уведомления о прекращении
- Analytics - аналитика использования версий
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
from collections import defaultdict
import uuid
import re


class VersionStatus(Enum):
    """Статус версии"""
    ALPHA = "alpha"
    BETA = "beta"
    STABLE = "stable"
    DEPRECATED = "deprecated"
    SUNSET = "sunset"
    RETIRED = "retired"


class BreakingChangeType(Enum):
    """Тип критического изменения"""
    ENDPOINT_REMOVED = "endpoint_removed"
    FIELD_REMOVED = "field_removed"
    FIELD_TYPE_CHANGED = "field_type_changed"
    REQUIRED_FIELD_ADDED = "required_field_added"
    RESPONSE_FORMAT_CHANGED = "response_format_changed"
    AUTH_CHANGED = "auth_changed"
    BEHAVIOR_CHANGED = "behavior_changed"


class CompatibilityLevel(Enum):
    """Уровень совместимости"""
    FULL = "full"             # Полная совместимость
    BACKWARD = "backward"     # Обратная совместимость
    FORWARD = "forward"       # Прямая совместимость
    BREAKING = "breaking"     # Критические изменения


@dataclass
class SemanticVersion:
    """Семантическая версия"""
    major: int = 1
    minor: int = 0
    patch: int = 0
    prerelease: str = ""
    
    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        return version
        
    @classmethod
    def parse(cls, version_str: str) -> "SemanticVersion":
        """Парсинг версии"""
        pattern = r"(\d+)\.(\d+)\.(\d+)(?:-(.+))?"
        match = re.match(pattern, version_str)
        
        if match:
            return cls(
                major=int(match.group(1)),
                minor=int(match.group(2)),
                patch=int(match.group(3)),
                prerelease=match.group(4) or ""
            )
        return cls()
        
    def __lt__(self, other: "SemanticVersion") -> bool:
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        return self.patch < other.patch


@dataclass
class APIEndpoint:
    """Эндпоинт API"""
    endpoint_id: str
    path: str
    method: str = "GET"
    
    # Схема
    request_schema: Dict[str, Any] = field(default_factory=dict)
    response_schema: Dict[str, Any] = field(default_factory=dict)
    
    # Параметры
    query_params: List[Dict[str, Any]] = field(default_factory=list)
    headers: List[Dict[str, Any]] = field(default_factory=list)
    
    # Документация
    summary: str = ""
    description: str = ""
    
    # Статус
    deprecated: bool = False
    deprecated_message: str = ""


@dataclass
class APIVersion:
    """Версия API"""
    version_id: str
    version: SemanticVersion
    
    # Статус
    status: VersionStatus = VersionStatus.ALPHA
    
    # Эндпоинты
    endpoints: Dict[str, APIEndpoint] = field(default_factory=dict)
    
    # Даты
    released_at: Optional[datetime] = None
    deprecated_at: Optional[datetime] = None
    sunset_at: Optional[datetime] = None
    
    # Документация
    release_notes: str = ""
    changelog: List[str] = field(default_factory=list)
    
    # Теги
    tags: List[str] = field(default_factory=list)


@dataclass
class BreakingChange:
    """Критическое изменение"""
    change_id: str
    
    # Тип
    change_type: BreakingChangeType = BreakingChangeType.BEHAVIOR_CHANGED
    
    # Детали
    endpoint: str = ""
    field: str = ""
    description: str = ""
    
    # Миграция
    migration_guide: str = ""
    
    # Версии
    introduced_in: str = ""
    affects_versions: List[str] = field(default_factory=list)


@dataclass
class MigrationPath:
    """Путь миграции"""
    migration_id: str
    
    # Версии
    from_version: str = ""
    to_version: str = ""
    
    # Шаги
    steps: List[Dict[str, Any]] = field(default_factory=list)
    
    # Автоматизация
    automated: bool = False
    automation_script: str = ""
    
    # Оценка
    effort_hours: float = 0.0
    risk_level: str = "low"  # low, medium, high
    
    # Документация
    documentation_url: str = ""


@dataclass
class DeprecationNotice:
    """Уведомление об устаревании"""
    notice_id: str
    
    # Что устаревает
    resource_type: str = ""  # version, endpoint, field
    resource_id: str = ""
    
    # Даты
    announced_at: datetime = field(default_factory=datetime.now)
    deprecated_at: datetime = field(default_factory=datetime.now)
    sunset_at: Optional[datetime] = None
    
    # Сообщение
    message: str = ""
    alternative: str = ""
    
    # Уведомлённые клиенты
    notified_clients: List[str] = field(default_factory=list)


@dataclass
class VersionUsageStats:
    """Статистика использования версии"""
    version: str
    
    # Метрики
    total_requests: int = 0
    unique_clients: int = 0
    error_rate: float = 0.0
    avg_latency_ms: float = 0.0
    
    # По эндпоинтам
    endpoint_usage: Dict[str, int] = field(default_factory=dict)
    
    # Период
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)


class VersionRouter:
    """Маршрутизатор версий"""
    
    def __init__(self):
        self.default_version: str = ""
        self.routing_rules: List[Dict[str, Any]] = []
        
    def set_default(self, version: str):
        """Установка версии по умолчанию"""
        self.default_version = version
        
    def add_rule(self, pattern: str, version: str, priority: int = 0):
        """Добавление правила маршрутизации"""
        self.routing_rules.append({
            "pattern": pattern,
            "version": version,
            "priority": priority
        })
        self.routing_rules.sort(key=lambda r: -r["priority"])
        
    def route(self, request: Dict[str, Any]) -> str:
        """Определение версии для запроса"""
        # 1. Из заголовка
        if "headers" in request:
            api_version = request["headers"].get("X-API-Version")
            if api_version:
                return api_version
                
            accept = request["headers"].get("Accept", "")
            # application/vnd.api.v2+json
            match = re.search(r"vnd\.api\.v(\d+)", accept)
            if match:
                return f"v{match.group(1)}"
                
        # 2. Из URL
        path = request.get("path", "")
        match = re.match(r"/api/v(\d+)/", path)
        if match:
            return f"v{match.group(1)}"
            
        # 3. Из query параметра
        query = request.get("query", {})
        if "version" in query:
            return query["version"]
            
        # 4. По правилам
        for rule in self.routing_rules:
            if re.match(rule["pattern"], path):
                return rule["version"]
                
        # 5. По умолчанию
        return self.default_version


class CompatibilityChecker:
    """Проверка совместимости"""
    
    def check_versions(self, old_version: APIVersion,
                        new_version: APIVersion) -> Dict[str, Any]:
        """Проверка совместимости версий"""
        breaking_changes = []
        warnings = []
        
        old_endpoints = set(old_version.endpoints.keys())
        new_endpoints = set(new_version.endpoints.keys())
        
        # Удалённые эндпоинты
        removed = old_endpoints - new_endpoints
        for endpoint_id in removed:
            breaking_changes.append({
                "type": BreakingChangeType.ENDPOINT_REMOVED.value,
                "endpoint": endpoint_id,
                "message": f"Endpoint {endpoint_id} was removed"
            })
            
        # Изменённые эндпоинты
        common = old_endpoints & new_endpoints
        for endpoint_id in common:
            old_ep = old_version.endpoints[endpoint_id]
            new_ep = new_version.endpoints[endpoint_id]
            
            # Проверка схемы запроса
            req_changes = self._check_schema_changes(
                old_ep.request_schema,
                new_ep.request_schema,
                "request"
            )
            breaking_changes.extend(req_changes)
            
            # Проверка схемы ответа
            resp_changes = self._check_schema_changes(
                old_ep.response_schema,
                new_ep.response_schema,
                "response"
            )
            breaking_changes.extend(resp_changes)
            
        # Новые эндпоинты (не breaking, но информация)
        added = new_endpoints - old_endpoints
        for endpoint_id in added:
            warnings.append({
                "type": "endpoint_added",
                "endpoint": endpoint_id,
                "message": f"New endpoint {endpoint_id} added"
            })
            
        compatibility = CompatibilityLevel.FULL
        if breaking_changes:
            compatibility = CompatibilityLevel.BREAKING
        elif warnings:
            compatibility = CompatibilityLevel.BACKWARD
            
        return {
            "compatibility": compatibility.value,
            "breaking_changes": breaking_changes,
            "warnings": warnings,
            "old_version": str(old_version.version),
            "new_version": str(new_version.version)
        }
        
    def _check_schema_changes(self, old_schema: Dict, new_schema: Dict,
                               context: str) -> List[Dict[str, Any]]:
        """Проверка изменений схемы"""
        changes = []
        
        old_fields = set(old_schema.get("properties", {}).keys())
        new_fields = set(new_schema.get("properties", {}).keys())
        
        # Удалённые поля
        for field in old_fields - new_fields:
            changes.append({
                "type": BreakingChangeType.FIELD_REMOVED.value,
                "field": field,
                "context": context,
                "message": f"Field '{field}' removed from {context}"
            })
            
        # Новые обязательные поля
        old_required = set(old_schema.get("required", []))
        new_required = set(new_schema.get("required", []))
        
        for field in new_required - old_required:
            if field in new_fields - old_fields:
                changes.append({
                    "type": BreakingChangeType.REQUIRED_FIELD_ADDED.value,
                    "field": field,
                    "context": context,
                    "message": f"New required field '{field}' added to {context}"
                })
                
        return changes


class DeprecationManager:
    """Менеджер устаревания"""
    
    def __init__(self):
        self.notices: Dict[str, DeprecationNotice] = {}
        
    def deprecate_version(self, version: APIVersion,
                          sunset_date: datetime,
                          message: str = "") -> DeprecationNotice:
        """Устаревание версии"""
        notice = DeprecationNotice(
            notice_id=f"dep_{uuid.uuid4().hex[:8]}",
            resource_type="version",
            resource_id=version.version_id,
            deprecated_at=datetime.now(),
            sunset_at=sunset_date,
            message=message or f"API version {version.version} is deprecated"
        )
        
        version.status = VersionStatus.DEPRECATED
        version.deprecated_at = datetime.now()
        version.sunset_at = sunset_date
        
        self.notices[notice.notice_id] = notice
        return notice
        
    def deprecate_endpoint(self, endpoint: APIEndpoint,
                            alternative: str = "",
                            message: str = "") -> DeprecationNotice:
        """Устаревание эндпоинта"""
        notice = DeprecationNotice(
            notice_id=f"dep_{uuid.uuid4().hex[:8]}",
            resource_type="endpoint",
            resource_id=endpoint.endpoint_id,
            deprecated_at=datetime.now(),
            message=message or f"Endpoint {endpoint.path} is deprecated",
            alternative=alternative
        )
        
        endpoint.deprecated = True
        endpoint.deprecated_message = message
        
        self.notices[notice.notice_id] = notice
        return notice
        
    def get_active_deprecations(self) -> List[DeprecationNotice]:
        """Активные уведомления об устаревании"""
        now = datetime.now()
        return [
            n for n in self.notices.values()
            if n.sunset_at is None or n.sunset_at > now
        ]


class APIVersioningPlatform:
    """Платформа версионирования API"""
    
    def __init__(self):
        self.versions: Dict[str, APIVersion] = {}
        self.breaking_changes: Dict[str, BreakingChange] = {}
        self.migration_paths: Dict[str, MigrationPath] = {}
        
        self.router = VersionRouter()
        self.compatibility_checker = CompatibilityChecker()
        self.deprecation_manager = DeprecationManager()
        
        self.usage_stats: Dict[str, VersionUsageStats] = {}
        
    def create_version(self, version_str: str,
                        status: VersionStatus = VersionStatus.ALPHA,
                        **kwargs) -> APIVersion:
        """Создание версии"""
        version = APIVersion(
            version_id=f"ver_{uuid.uuid4().hex[:8]}",
            version=SemanticVersion.parse(version_str),
            status=status,
            **kwargs
        )
        
        self.versions[version.version_id] = version
        return version
        
    def add_endpoint(self, version_id: str, path: str, method: str,
                      **kwargs) -> Optional[APIEndpoint]:
        """Добавление эндпоинта"""
        version = self.versions.get(version_id)
        if not version:
            return None
            
        endpoint = APIEndpoint(
            endpoint_id=f"{method.upper()}_{path.replace('/', '_')}",
            path=path,
            method=method.upper(),
            **kwargs
        )
        
        version.endpoints[endpoint.endpoint_id] = endpoint
        return endpoint
        
    def release_version(self, version_id: str) -> bool:
        """Релиз версии"""
        version = self.versions.get(version_id)
        if not version:
            return False
            
        version.status = VersionStatus.STABLE
        version.released_at = datetime.now()
        
        # Устанавливаем как default если это первая stable
        stable_versions = [v for v in self.versions.values() 
                          if v.status == VersionStatus.STABLE]
        if len(stable_versions) == 1:
            self.router.set_default(f"v{version.version.major}")
            
        return True
        
    def deprecate_version(self, version_id: str,
                           sunset_days: int = 180) -> Optional[DeprecationNotice]:
        """Устаревание версии"""
        version = self.versions.get(version_id)
        if not version:
            return None
            
        sunset_date = datetime.now() + timedelta(days=sunset_days)
        return self.deprecation_manager.deprecate_version(version, sunset_date)
        
    def check_compatibility(self, old_version_id: str,
                             new_version_id: str) -> Dict[str, Any]:
        """Проверка совместимости"""
        old_ver = self.versions.get(old_version_id)
        new_ver = self.versions.get(new_version_id)
        
        if not old_ver or not new_ver:
            return {"error": "Version not found"}
            
        return self.compatibility_checker.check_versions(old_ver, new_ver)
        
    def create_migration_path(self, from_version_id: str, to_version_id: str,
                               steps: List[Dict[str, Any]],
                               **kwargs) -> MigrationPath:
        """Создание пути миграции"""
        from_ver = self.versions.get(from_version_id)
        to_ver = self.versions.get(to_version_id)
        
        migration = MigrationPath(
            migration_id=f"mig_{uuid.uuid4().hex[:8]}",
            from_version=str(from_ver.version) if from_ver else "",
            to_version=str(to_ver.version) if to_ver else "",
            steps=steps,
            **kwargs
        )
        
        self.migration_paths[migration.migration_id] = migration
        return migration
        
    def route_request(self, request: Dict[str, Any]) -> str:
        """Маршрутизация запроса"""
        return self.router.route(request)
        
    def record_usage(self, version: str, endpoint: str,
                      latency_ms: float, error: bool = False):
        """Запись использования"""
        if version not in self.usage_stats:
            self.usage_stats[version] = VersionUsageStats(
                version=version,
                period_start=datetime.now()
            )
            
        stats = self.usage_stats[version]
        stats.total_requests += 1
        stats.endpoint_usage[endpoint] = stats.endpoint_usage.get(endpoint, 0) + 1
        
        # Обновление latency (скользящее среднее)
        stats.avg_latency_ms = (
            stats.avg_latency_ms * (stats.total_requests - 1) + latency_ms
        ) / stats.total_requests
        
        if error:
            current_errors = stats.error_rate * (stats.total_requests - 1)
            stats.error_rate = (current_errors + 1) / stats.total_requests
            
    def get_version_stats(self, version: str = None) -> Dict[str, Any]:
        """Статистика по версиям"""
        if version:
            stats = self.usage_stats.get(version)
            if stats:
                return {
                    "version": stats.version,
                    "total_requests": stats.total_requests,
                    "error_rate": f"{stats.error_rate*100:.2f}%",
                    "avg_latency_ms": f"{stats.avg_latency_ms:.2f}",
                    "top_endpoints": sorted(
                        stats.endpoint_usage.items(),
                        key=lambda x: -x[1]
                    )[:5]
                }
            return {}
            
        return {
            v: {
                "requests": s.total_requests,
                "error_rate": f"{s.error_rate*100:.2f}%"
            }
            for v, s in self.usage_stats.items()
        }
        
    def get_stats(self) -> Dict[str, Any]:
        """Статистика платформы"""
        versions_by_status = defaultdict(int)
        for v in self.versions.values():
            versions_by_status[v.status.value] += 1
            
        return {
            "total_versions": len(self.versions),
            "by_status": dict(versions_by_status),
            "total_endpoints": sum(len(v.endpoints) for v in self.versions.values()),
            "migration_paths": len(self.migration_paths),
            "deprecation_notices": len(self.deprecation_manager.notices),
            "default_version": self.router.default_version
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 75: API Versioning & Lifecycle")
    print("=" * 60)
    
    async def demo():
        platform = APIVersioningPlatform()
        print("✓ API Versioning Platform created")
        
        # Создание версий API
        print("\n📌 Creating API Versions...")
        
        v1 = platform.create_version(
            "1.0.0",
            status=VersionStatus.STABLE,
            release_notes="Initial stable release"
        )
        v1.released_at = datetime.now() - timedelta(days=365)
        print(f"  ✓ Version {v1.version} ({v1.status.value})")
        
        v2 = platform.create_version(
            "2.0.0",
            status=VersionStatus.STABLE,
            release_notes="Major release with breaking changes",
            changelog=[
                "New authentication system",
                "Improved response format",
                "Added pagination"
            ]
        )
        v2.released_at = datetime.now() - timedelta(days=90)
        print(f"  ✓ Version {v2.version} ({v2.status.value})")
        
        v3 = platform.create_version(
            "3.0.0-beta",
            status=VersionStatus.BETA,
            release_notes="Beta release with new features"
        )
        print(f"  ✓ Version {v3.version} ({v3.status.value})")
        
        # Добавление эндпоинтов
        print("\n🔗 Adding Endpoints...")
        
        # V1 endpoints
        for path, method, summary in [
            ("/users", "GET", "List users"),
            ("/users/{id}", "GET", "Get user"),
            ("/users", "POST", "Create user"),
            ("/products", "GET", "List products"),
        ]:
            ep = platform.add_endpoint(v1.version_id, path, method, summary=summary)
            
        print(f"  V1: {len(v1.endpoints)} endpoints")
        
        # V2 endpoints (с изменениями)
        for path, method, summary in [
            ("/users", "GET", "List users with pagination"),
            ("/users/{id}", "GET", "Get user by ID"),
            ("/users", "POST", "Create new user"),
            ("/products", "GET", "List products"),
            ("/orders", "GET", "List orders"),  # Новый
            ("/orders", "POST", "Create order"),  # Новый
        ]:
            ep = platform.add_endpoint(v2.version_id, path, method, summary=summary)
            
        print(f"  V2: {len(v2.endpoints)} endpoints")
        
        # V3 endpoints
        for path, method, summary in [
            ("/users", "GET", "List users"),
            ("/users/{id}", "GET", "Get user"),
            ("/users", "POST", "Create user"),
            ("/products", "GET", "List products"),
            ("/orders", "GET", "List orders"),
            ("/orders", "POST", "Create order"),
            ("/analytics", "GET", "Get analytics"),  # Новый
            ("/webhooks", "POST", "Register webhook"),  # Новый
        ]:
            ep = platform.add_endpoint(v3.version_id, path, method, summary=summary)
            
        print(f"  V3: {len(v3.endpoints)} endpoints")
        
        # Установка default version
        platform.router.set_default("v2")
        print(f"\n  Default version: {platform.router.default_version}")
        
        # Проверка совместимости
        print("\n🔍 Checking Compatibility...")
        
        compat = platform.check_compatibility(v1.version_id, v2.version_id)
        print(f"  V1 → V2: {compat['compatibility']}")
        print(f"    Breaking changes: {len(compat['breaking_changes'])}")
        print(f"    Warnings: {len(compat['warnings'])}")
        
        if compat['warnings']:
            print("    New features:")
            for w in compat['warnings'][:3]:
                print(f"      + {w['endpoint']}")
                
        # Deprecation
        print("\n⚠️ Deprecating V1...")
        
        notice = platform.deprecate_version(v1.version_id, sunset_days=90)
        if notice:
            print(f"  Notice ID: {notice.notice_id}")
            print(f"  Deprecated at: {notice.deprecated_at.strftime('%Y-%m-%d')}")
            print(f"  Sunset at: {notice.sunset_at.strftime('%Y-%m-%d')}")
            print(f"  V1 status: {v1.status.value}")
            
        # Создание пути миграции
        print("\n🔄 Creating Migration Path...")
        
        migration = platform.create_migration_path(
            v1.version_id,
            v2.version_id,
            steps=[
                {
                    "step": 1,
                    "action": "Update authentication",
                    "description": "Replace API key with OAuth 2.0 tokens",
                    "code_change": True
                },
                {
                    "step": 2,
                    "action": "Update pagination",
                    "description": "Add page and limit query parameters",
                    "code_change": True
                },
                {
                    "step": 3,
                    "action": "Update endpoints",
                    "description": "Use new /orders endpoints",
                    "code_change": False
                },
                {
                    "step": 4,
                    "action": "Test integration",
                    "description": "Run integration tests against v2",
                    "code_change": False
                }
            ],
            effort_hours=8,
            risk_level="medium",
            documentation_url="https://docs.api.example.com/migration/v1-to-v2"
        )
        print(f"  Migration: {migration.from_version} → {migration.to_version}")
        print(f"  Steps: {len(migration.steps)}")
        print(f"  Estimated effort: {migration.effort_hours}h")
        print(f"  Risk level: {migration.risk_level}")
        
        # Маршрутизация
        print("\n🚦 Request Routing...")
        
        test_requests = [
            {"path": "/api/v1/users", "headers": {}},
            {"path": "/api/v2/products", "headers": {}},
            {"path": "/api/users", "headers": {"X-API-Version": "v3"}},
            {"path": "/api/orders", "headers": {"Accept": "application/vnd.api.v2+json"}},
            {"path": "/api/analytics", "query": {"version": "v3"}},
            {"path": "/api/users", "headers": {}},  # Default
        ]
        
        for req in test_requests:
            version = platform.route_request(req)
            path = req.get("path", "")
            print(f"  {path[:25]:25} → {version}")
            
        # Симуляция использования
        print("\n📊 Recording Usage...")
        
        import random
        
        for _ in range(100):
            version = random.choice(["v1", "v2", "v2", "v2", "v3"])
            endpoint = random.choice(["/users", "/products", "/orders"])
            latency = random.uniform(10, 200)
            error = random.random() < 0.05
            
            platform.record_usage(version, endpoint, latency, error)
            
        print("  Recorded 100 requests")
        
        # Статистика по версиям
        print("\n📈 Version Statistics:")
        
        all_stats = platform.get_version_stats()
        for version, stats in all_stats.items():
            print(f"  {version}:")
            print(f"    Requests: {stats['requests']}")
            print(f"    Error Rate: {stats['error_rate']}")
            
        # Детальная статистика V2
        v2_stats = platform.get_version_stats("v2")
        if v2_stats:
            print(f"\n  V2 Details:")
            print(f"    Avg Latency: {v2_stats['avg_latency_ms']}ms")
            print(f"    Top Endpoints:")
            for ep, count in v2_stats['top_endpoints']:
                print(f"      {ep}: {count} requests")
                
        # Активные deprecations
        print("\n📋 Active Deprecations:")
        active_deps = platform.deprecation_manager.get_active_deprecations()
        for dep in active_deps:
            print(f"  - {dep.resource_type}: {dep.message[:40]}...")
            
        # Общая статистика
        print("\n📊 Platform Statistics:")
        stats = platform.get_stats()
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    {k}: {v}")
            else:
                print(f"  {key}: {value}")
                
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("API Versioning & Lifecycle Platform initialized!")
    print("=" * 60)
