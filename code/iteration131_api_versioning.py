#!/usr/bin/env python3
"""
Server Init - Iteration 131: API Versioning Platform
Платформа версионирования API

Функционал:
- Version Management - управление версиями
- Deprecation Tracking - отслеживание устаревания
- Migration Paths - пути миграции
- Compatibility Checking - проверка совместимости
- Version Routing - маршрутизация по версиям
- API Documentation - документация API
- Breaking Change Detection - обнаружение критических изменений
- Client Version Analytics - аналитика версий клиентов
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
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


class ChangeType(Enum):
    """Тип изменения"""
    BREAKING = "breaking"
    FEATURE = "feature"
    FIX = "fix"
    DEPRECATION = "deprecation"
    SECURITY = "security"


class CompatibilityLevel(Enum):
    """Уровень совместимости"""
    FULL = "full"
    BACKWARD = "backward"
    FORWARD = "forward"
    NONE = "none"


@dataclass
class APIVersion:
    """Версия API"""
    version_id: str
    version: str = ""  # e.g., "v1", "v2.1"
    
    # Semantic version
    major: int = 1
    minor: int = 0
    patch: int = 0
    
    # Status
    status: VersionStatus = VersionStatus.STABLE
    
    # Dates
    released_at: datetime = field(default_factory=datetime.now)
    deprecated_at: Optional[datetime] = None
    sunset_at: Optional[datetime] = None
    
    # Endpoints
    endpoint_count: int = 0
    
    # Usage
    request_count: int = 0
    active_clients: int = 0


@dataclass
class APIEndpoint:
    """Эндпоинт API"""
    endpoint_id: str
    path: str = ""
    method: str = "GET"
    
    # Version
    introduced_in: str = ""
    deprecated_in: Optional[str] = None
    removed_in: Optional[str] = None
    
    # Schema
    request_schema: Dict = field(default_factory=dict)
    response_schema: Dict = field(default_factory=dict)
    
    # Description
    summary: str = ""
    description: str = ""


@dataclass
class BreakingChange:
    """Критическое изменение"""
    change_id: str
    from_version: str = ""
    to_version: str = ""
    
    # Details
    change_type: ChangeType = ChangeType.BREAKING
    endpoint: str = ""
    description: str = ""
    
    # Migration
    migration_guide: str = ""
    automated_migration: bool = False
    
    # Impact
    affected_clients: int = 0


@dataclass
class DeprecationNotice:
    """Уведомление об устаревании"""
    notice_id: str
    version: str = ""
    
    # Target
    endpoint: str = ""
    field: str = ""
    
    # Timeline
    deprecated_at: datetime = field(default_factory=datetime.now)
    sunset_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=180))
    
    # Replacement
    replacement: str = ""
    migration_guide: str = ""
    
    # Notification
    clients_notified: int = 0


@dataclass
class MigrationPath:
    """Путь миграции"""
    migration_id: str
    from_version: str = ""
    to_version: str = ""
    
    # Steps
    steps: List[Dict] = field(default_factory=list)
    
    # Complexity
    complexity: str = "medium"  # low, medium, high
    estimated_effort_hours: int = 0
    
    # Status
    automated: bool = False
    tested: bool = True


@dataclass
class ClientVersionStats:
    """Статистика версий клиентов"""
    client_id: str
    client_name: str = ""
    
    # Version usage
    versions_used: Dict[str, int] = field(default_factory=dict)
    
    # Current version
    current_version: str = ""
    last_request_at: datetime = field(default_factory=datetime.now)
    
    # Migration status
    using_deprecated: bool = False


class VersionManager:
    """Менеджер версий"""
    
    def __init__(self):
        self.versions: Dict[str, APIVersion] = {}
        
    def create(self, version: str, status: VersionStatus = VersionStatus.STABLE) -> APIVersion:
        """Создание версии"""
        # Parse version
        match = re.match(r'v?(\d+)(?:\.(\d+))?(?:\.(\d+))?', version)
        major = int(match.group(1)) if match else 1
        minor = int(match.group(2)) if match and match.group(2) else 0
        patch = int(match.group(3)) if match and match.group(3) else 0
        
        api_version = APIVersion(
            version_id=f"ver_{uuid.uuid4().hex[:8]}",
            version=version,
            major=major,
            minor=minor,
            patch=patch,
            status=status
        )
        self.versions[version] = api_version
        return api_version
        
    def deprecate(self, version: str, sunset_days: int = 180) -> Dict:
        """Пометить как устаревшую"""
        api_version = self.versions.get(version)
        if not api_version:
            return {"error": "Version not found"}
            
        api_version.status = VersionStatus.DEPRECATED
        api_version.deprecated_at = datetime.now()
        api_version.sunset_at = datetime.now() + timedelta(days=sunset_days)
        
        return {
            "version": version,
            "deprecated_at": api_version.deprecated_at.isoformat(),
            "sunset_at": api_version.sunset_at.isoformat()
        }
        
    def sunset(self, version: str) -> Dict:
        """Закат версии"""
        api_version = self.versions.get(version)
        if not api_version:
            return {"error": "Version not found"}
            
        api_version.status = VersionStatus.SUNSET
        api_version.sunset_at = datetime.now()
        
        return {"version": version, "status": "sunset"}
        
    def get_latest(self, stable_only: bool = True) -> Optional[APIVersion]:
        """Получить последнюю версию"""
        valid_versions = [
            v for v in self.versions.values()
            if not stable_only or v.status == VersionStatus.STABLE
        ]
        
        if not valid_versions:
            return None
            
        return max(valid_versions, key=lambda v: (v.major, v.minor, v.patch))
        
    def compare(self, v1: str, v2: str) -> int:
        """Сравнение версий"""
        ver1 = self.versions.get(v1)
        ver2 = self.versions.get(v2)
        
        if not ver1 or not ver2:
            return 0
            
        if (ver1.major, ver1.minor, ver1.patch) > (ver2.major, ver2.minor, ver2.patch):
            return 1
        elif (ver1.major, ver1.minor, ver1.patch) < (ver2.major, ver2.minor, ver2.patch):
            return -1
        return 0


class EndpointRegistry:
    """Реестр эндпоинтов"""
    
    def __init__(self):
        self.endpoints: Dict[str, Dict[str, APIEndpoint]] = defaultdict(dict)  # version -> path -> endpoint
        
    def register(self, version: str, path: str, method: str = "GET",
                  **kwargs) -> APIEndpoint:
        """Регистрация эндпоинта"""
        key = f"{method}:{path}"
        
        endpoint = APIEndpoint(
            endpoint_id=f"ep_{uuid.uuid4().hex[:8]}",
            path=path,
            method=method,
            introduced_in=version,
            **kwargs
        )
        
        self.endpoints[version][key] = endpoint
        return endpoint
        
    def deprecate_endpoint(self, version: str, path: str, method: str,
                            deprecated_in: str) -> Dict:
        """Пометить эндпоинт как устаревший"""
        key = f"{method}:{path}"
        endpoint = self.endpoints.get(version, {}).get(key)
        
        if not endpoint:
            return {"error": "Endpoint not found"}
            
        endpoint.deprecated_in = deprecated_in
        return {"endpoint": path, "deprecated_in": deprecated_in}
        
    def get_endpoints(self, version: str) -> List[APIEndpoint]:
        """Получить эндпоинты версии"""
        return list(self.endpoints.get(version, {}).values())


class CompatibilityChecker:
    """Проверка совместимости"""
    
    def __init__(self, endpoint_registry: EndpointRegistry):
        self.endpoint_registry = endpoint_registry
        self.breaking_changes: Dict[str, List[BreakingChange]] = defaultdict(list)
        
    def check(self, from_version: str, to_version: str) -> Dict[str, Any]:
        """Проверка совместимости между версиями"""
        from_endpoints = {f"{e.method}:{e.path}": e 
                         for e in self.endpoint_registry.get_endpoints(from_version)}
        to_endpoints = {f"{e.method}:{e.path}": e 
                       for e in self.endpoint_registry.get_endpoints(to_version)}
        
        removed = set(from_endpoints.keys()) - set(to_endpoints.keys())
        added = set(to_endpoints.keys()) - set(from_endpoints.keys())
        common = set(from_endpoints.keys()) & set(to_endpoints.keys())
        
        breaking_changes = []
        
        # Removed endpoints are breaking
        for key in removed:
            change = BreakingChange(
                change_id=f"break_{uuid.uuid4().hex[:8]}",
                from_version=from_version,
                to_version=to_version,
                endpoint=key,
                description=f"Endpoint {key} was removed"
            )
            breaking_changes.append(change)
            
        # Check schema changes
        for key in common:
            from_ep = from_endpoints[key]
            to_ep = to_endpoints[key]
            
            # Compare schemas (simplified)
            if from_ep.request_schema != to_ep.request_schema:
                change = BreakingChange(
                    change_id=f"break_{uuid.uuid4().hex[:8]}",
                    from_version=from_version,
                    to_version=to_version,
                    endpoint=key,
                    description=f"Request schema changed for {key}"
                )
                breaking_changes.append(change)
                
        key = f"{from_version}->{to_version}"
        self.breaking_changes[key] = breaking_changes
        
        level = CompatibilityLevel.FULL
        if breaking_changes:
            level = CompatibilityLevel.NONE
        elif removed:
            level = CompatibilityLevel.FORWARD
            
        return {
            "from_version": from_version,
            "to_version": to_version,
            "compatibility": level.value,
            "added_endpoints": len(added),
            "removed_endpoints": len(removed),
            "breaking_changes": len(breaking_changes)
        }


class DeprecationManager:
    """Менеджер устаревания"""
    
    def __init__(self):
        self.notices: Dict[str, DeprecationNotice] = {}
        
    def create_notice(self, version: str, endpoint: str,
                       sunset_days: int = 180, replacement: str = "",
                       **kwargs) -> DeprecationNotice:
        """Создание уведомления"""
        notice = DeprecationNotice(
            notice_id=f"deprec_{uuid.uuid4().hex[:8]}",
            version=version,
            endpoint=endpoint,
            sunset_at=datetime.now() + timedelta(days=sunset_days),
            replacement=replacement,
            **kwargs
        )
        self.notices[notice.notice_id] = notice
        return notice
        
    def get_active_notices(self) -> List[DeprecationNotice]:
        """Активные уведомления"""
        now = datetime.now()
        return [n for n in self.notices.values() if n.sunset_at > now]
        
    def get_sunset_notices(self) -> List[DeprecationNotice]:
        """Просроченные уведомления"""
        now = datetime.now()
        return [n for n in self.notices.values() if n.sunset_at <= now]


class MigrationManager:
    """Менеджер миграций"""
    
    def __init__(self, version_manager: VersionManager):
        self.version_manager = version_manager
        self.migrations: Dict[str, MigrationPath] = {}
        
    def create_path(self, from_version: str, to_version: str,
                     steps: List[Dict] = None, **kwargs) -> MigrationPath:
        """Создание пути миграции"""
        migration = MigrationPath(
            migration_id=f"mig_{uuid.uuid4().hex[:8]}",
            from_version=from_version,
            to_version=to_version,
            steps=steps or [],
            **kwargs
        )
        
        key = f"{from_version}->{to_version}"
        self.migrations[key] = migration
        return migration
        
    def find_path(self, from_version: str, to_version: str) -> List[MigrationPath]:
        """Найти путь миграции"""
        direct_key = f"{from_version}->{to_version}"
        if direct_key in self.migrations:
            return [self.migrations[direct_key]]
            
        # Try to find indirect path
        path = []
        current = from_version
        
        versions = sorted(
            self.version_manager.versions.values(),
            key=lambda v: (v.major, v.minor, v.patch)
        )
        
        for version in versions:
            if self.version_manager.compare(version.version, current) > 0:
                key = f"{current}->{version.version}"
                if key in self.migrations:
                    path.append(self.migrations[key])
                    current = version.version
                    
                if current == to_version:
                    break
                    
        return path


class VersionRouter:
    """Маршрутизатор версий"""
    
    def __init__(self, version_manager: VersionManager, endpoint_registry: EndpointRegistry):
        self.version_manager = version_manager
        self.endpoint_registry = endpoint_registry
        
    def route(self, path: str, method: str = "GET",
               requested_version: str = None) -> Dict[str, Any]:
        """Маршрутизация запроса"""
        # Determine version
        if requested_version:
            version = requested_version
        else:
            latest = self.version_manager.get_latest()
            version = latest.version if latest else "v1"
            
        # Find endpoint
        key = f"{method}:{path}"
        endpoint = self.endpoint_registry.endpoints.get(version, {}).get(key)
        
        if not endpoint:
            # Try fallback to latest
            for v in sorted(self.version_manager.versions.keys(), reverse=True):
                endpoint = self.endpoint_registry.endpoints.get(v, {}).get(key)
                if endpoint:
                    version = v
                    break
                    
        if not endpoint:
            return {"error": "Endpoint not found", "status": 404}
            
        # Check deprecation
        api_version = self.version_manager.versions.get(version)
        warnings = []
        
        if api_version and api_version.status == VersionStatus.DEPRECATED:
            warnings.append(f"Version {version} is deprecated")
            
        if endpoint.deprecated_in:
            warnings.append(f"Endpoint deprecated in {endpoint.deprecated_in}")
            
        return {
            "version": version,
            "endpoint": endpoint.endpoint_id,
            "path": endpoint.path,
            "method": endpoint.method,
            "warnings": warnings
        }


class ClientAnalytics:
    """Аналитика клиентов"""
    
    def __init__(self):
        self.clients: Dict[str, ClientVersionStats] = {}
        
    def track(self, client_id: str, version: str, client_name: str = "") -> None:
        """Отслеживание запроса"""
        if client_id not in self.clients:
            self.clients[client_id] = ClientVersionStats(
                client_id=client_id,
                client_name=client_name
            )
            
        client = self.clients[client_id]
        client.versions_used[version] = client.versions_used.get(version, 0) + 1
        client.current_version = version
        client.last_request_at = datetime.now()
        
    def get_version_distribution(self) -> Dict[str, int]:
        """Распределение по версиям"""
        distribution = defaultdict(int)
        
        for client in self.clients.values():
            for version, count in client.versions_used.items():
                distribution[version] += count
                
        return dict(distribution)
        
    def get_deprecated_users(self, deprecated_versions: Set[str]) -> List[ClientVersionStats]:
        """Клиенты на устаревших версиях"""
        users = []
        
        for client in self.clients.values():
            if client.current_version in deprecated_versions:
                client.using_deprecated = True
                users.append(client)
                
        return users


class APIVersioningPlatform:
    """Платформа версионирования API"""
    
    def __init__(self):
        self.version_manager = VersionManager()
        self.endpoint_registry = EndpointRegistry()
        self.compatibility_checker = CompatibilityChecker(self.endpoint_registry)
        self.deprecation_manager = DeprecationManager()
        self.migration_manager = MigrationManager(self.version_manager)
        self.router = VersionRouter(self.version_manager, self.endpoint_registry)
        self.analytics = ClientAnalytics()
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        versions = list(self.version_manager.versions.values())
        
        return {
            "total_versions": len(versions),
            "stable_versions": len([v for v in versions if v.status == VersionStatus.STABLE]),
            "deprecated_versions": len([v for v in versions if v.status == VersionStatus.DEPRECATED]),
            "total_endpoints": sum(len(eps) for eps in self.endpoint_registry.endpoints.values()),
            "deprecation_notices": len(self.deprecation_manager.notices),
            "migration_paths": len(self.migration_manager.migrations),
            "tracked_clients": len(self.analytics.clients)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 131: API Versioning Platform")
    print("=" * 60)
    
    async def demo():
        platform = APIVersioningPlatform()
        print("✓ API Versioning Platform created")
        
        # Create versions
        print("\n📦 Creating API Versions...")
        
        versions_data = [
            ("v1", VersionStatus.DEPRECATED),
            ("v1.1", VersionStatus.DEPRECATED),
            ("v2", VersionStatus.STABLE),
            ("v2.1", VersionStatus.STABLE),
            ("v3", VersionStatus.BETA)
        ]
        
        for version, status in versions_data:
            v = platform.version_manager.create(version, status)
            print(f"  ✓ {version} ({status.value})")
            
        # Register endpoints
        print("\n🔗 Registering Endpoints...")
        
        # V1 endpoints
        v1_endpoints = [
            ("/users", "GET", "List users"),
            ("/users/{id}", "GET", "Get user"),
            ("/users", "POST", "Create user"),
            ("/posts", "GET", "List posts")
        ]
        
        for path, method, summary in v1_endpoints:
            platform.endpoint_registry.register("v1", path, method, summary=summary)
            
        print(f"  ✓ v1: {len(v1_endpoints)} endpoints")
        
        # V2 endpoints (with changes)
        v2_endpoints = [
            ("/users", "GET", "List users with pagination"),
            ("/users/{id}", "GET", "Get user details"),
            ("/users", "POST", "Create user"),
            ("/users/{id}", "PUT", "Update user"),  # New
            ("/posts", "GET", "List posts"),
            ("/posts/{id}/comments", "GET", "Get comments")  # New
        ]
        
        for path, method, summary in v2_endpoints:
            platform.endpoint_registry.register("v2", path, method, summary=summary)
            
        print(f"  ✓ v2: {len(v2_endpoints)} endpoints")
        
        # V3 endpoints
        v3_endpoints = v2_endpoints + [
            ("/graphql", "POST", "GraphQL endpoint"),
            ("/webhooks", "POST", "Register webhook")
        ]
        
        for path, method, summary in v3_endpoints:
            platform.endpoint_registry.register("v3", path, method, summary=summary)
            
        print(f"  ✓ v3: {len(v3_endpoints)} endpoints")
        
        # Check compatibility
        print("\n🔍 Checking Compatibility...")
        
        compatibility_checks = [
            ("v1", "v2"),
            ("v2", "v2.1"),
            ("v2", "v3")
        ]
        
        for from_v, to_v in compatibility_checks:
            result = platform.compatibility_checker.check(from_v, to_v)
            
            compat_icon = {"full": "🟢", "backward": "🟡", "forward": "🟠", "none": "🔴"}.get(result["compatibility"], "⚪")
            
            print(f"  {compat_icon} {from_v} -> {to_v}: {result['compatibility']}")
            print(f"     Added: {result['added_endpoints']}, Removed: {result['removed_endpoints']}")
            print(f"     Breaking changes: {result['breaking_changes']}")
            
        # Create deprecation notices
        print("\n⚠️ Creating Deprecation Notices...")
        
        notices = [
            ("v1", "/users", "/api/v2/users", 90),
            ("v1", "/posts", "/api/v2/posts", 90)
        ]
        
        for version, endpoint, replacement, days in notices:
            notice = platform.deprecation_manager.create_notice(
                version, endpoint,
                sunset_days=days,
                replacement=replacement
            )
            print(f"  ✓ {endpoint} in {version}")
            print(f"    Replacement: {replacement}")
            print(f"    Sunset in: {days} days")
            
        # Create migration paths
        print("\n🛤️ Creating Migration Paths...")
        
        migrations = [
            ("v1", "v2", [
                {"action": "update_base_url", "from": "/api/v1", "to": "/api/v2"},
                {"action": "add_pagination", "endpoints": ["/users", "/posts"]},
                {"action": "update_auth", "from": "api_key", "to": "bearer_token"}
            ], "medium", 4),
            ("v2", "v3", [
                {"action": "add_graphql_support"},
                {"action": "update_rate_limits"}
            ], "low", 2)
        ]
        
        for from_v, to_v, steps, complexity, hours in migrations:
            migration = platform.migration_manager.create_path(
                from_v, to_v,
                steps=steps,
                complexity=complexity,
                estimated_effort_hours=hours
            )
            print(f"  ✓ {from_v} -> {to_v}")
            print(f"    Steps: {len(steps)}")
            print(f"    Complexity: {complexity}")
            print(f"    Effort: {hours}h")
            
        # Route requests
        print("\n🔀 Request Routing...")
        
        test_requests = [
            ("/users", "GET", "v2"),
            ("/users/123", "GET", None),  # Auto-select version
            ("/posts", "GET", "v1"),      # Deprecated
            ("/graphql", "POST", "v3")
        ]
        
        for path, method, version in test_requests:
            result = platform.router.route(path, method, version)
            
            if "error" in result:
                print(f"  ❌ {method} {path}: {result['error']}")
            else:
                warnings = " ⚠️" if result["warnings"] else ""
                print(f"  ✓ {method} {path} -> {result['version']}{warnings}")
                for warning in result["warnings"]:
                    print(f"    Warning: {warning}")
                    
        # Track client usage
        print("\n📊 Tracking Client Usage...")
        
        clients_data = [
            ("client_1", "Mobile App iOS", ["v2", "v2", "v2.1"]),
            ("client_2", "Mobile App Android", ["v1", "v1", "v2"]),
            ("client_3", "Web Dashboard", ["v2.1", "v2.1", "v3"]),
            ("client_4", "Legacy System", ["v1", "v1", "v1"])
        ]
        
        for client_id, name, versions in clients_data:
            for version in versions:
                platform.analytics.track(client_id, version, name)
                
        # Version distribution
        distribution = platform.analytics.get_version_distribution()
        
        print("\n  Version Distribution:")
        for version, count in sorted(distribution.items()):
            bar = "█" * (count * 2)
            print(f"    {version}: {bar} ({count})")
            
        # Find deprecated users
        deprecated = {"v1", "v1.1"}
        deprecated_users = platform.analytics.get_deprecated_users(deprecated)
        
        print(f"\n  ⚠️ Clients on deprecated versions: {len(deprecated_users)}")
        for client in deprecated_users:
            print(f"    - {client.client_name}: {client.current_version}")
            
        # Latest version
        print("\n📌 Version Info:")
        
        latest = platform.version_manager.get_latest()
        print(f"  Latest stable: {latest.version if latest else 'None'}")
        
        # Deprecate v1
        print("\n⏰ Deprecating v1...")
        
        result = platform.version_manager.deprecate("v1", sunset_days=90)
        print(f"  ✓ v1 deprecated")
        print(f"    Sunset: {result.get('sunset_at', 'N/A')}")
        
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Versions: {stats['total_versions']}")
        print(f"    Stable: {stats['stable_versions']}")
        print(f"    Deprecated: {stats['deprecated_versions']}")
        print(f"  Total Endpoints: {stats['total_endpoints']}")
        print(f"  Deprecation Notices: {stats['deprecation_notices']}")
        print(f"  Migration Paths: {stats['migration_paths']}")
        print(f"  Tracked Clients: {stats['tracked_clients']}")
        
        # Dashboard
        print("\n📋 API Versioning Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │               API Versioning Overview                       │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Versions:     {stats['total_versions']:>10}                        │")
        print(f"  │   Stable:           {stats['stable_versions']:>10}                        │")
        print(f"  │   Deprecated:       {stats['deprecated_versions']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Endpoints:    {stats['total_endpoints']:>10}                        │")
        print(f"  │ Deprecations:       {stats['deprecation_notices']:>10}                        │")
        print(f"  │ Migration Paths:    {stats['migration_paths']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Tracked Clients:    {stats['tracked_clients']:>10}                        │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("API Versioning Platform initialized!")
    print("=" * 60)
