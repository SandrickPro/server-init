#!/usr/bin/env python3
"""
Server Init - Iteration 220: API Versioning Platform
Платформа версионирования API

Функционал:
- Version Management - управление версиями
- Compatibility Check - проверка совместимости
- Migration Planning - планирование миграций
- Deprecation Tracking - отслеживание устаревания
- Version Routing - маршрутизация по версиям
- Breaking Change Detection - обнаружение breaking changes
- Documentation Generation - генерация документации
- Client SDK Management - управление клиентскими SDK
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid


class VersionStatus(Enum):
    """Статус версии"""
    DEVELOPMENT = "development"
    BETA = "beta"
    STABLE = "stable"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


class ChangeType(Enum):
    """Тип изменения"""
    BREAKING = "breaking"
    FEATURE = "feature"
    FIX = "fix"
    DEPRECATION = "deprecation"


class CompatibilityLevel(Enum):
    """Уровень совместимости"""
    FULL = "full"
    BACKWARD = "backward"
    FORWARD = "forward"
    NONE = "none"


class MigrationStatus(Enum):
    """Статус миграции"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class APIEndpoint:
    """API эндпоинт"""
    endpoint_id: str
    path: str = ""
    method: str = "GET"
    
    # Schema
    request_schema: Dict[str, Any] = field(default_factory=dict)
    response_schema: Dict[str, Any] = field(default_factory=dict)
    
    # Parameters
    path_params: List[str] = field(default_factory=list)
    query_params: List[str] = field(default_factory=list)
    
    # Deprecated
    deprecated: bool = False
    deprecated_at: Optional[datetime] = None
    replacement_endpoint: Optional[str] = None


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
    status: VersionStatus = VersionStatus.DEVELOPMENT
    
    # Endpoints
    endpoints: List[APIEndpoint] = field(default_factory=list)
    
    # Dates
    released_at: Optional[datetime] = None
    deprecated_at: Optional[datetime] = None
    sunset_at: Optional[datetime] = None
    
    # Base URL
    base_path: str = ""
    
    # Changelog
    changelog: List[str] = field(default_factory=list)


@dataclass
class BreakingChange:
    """Breaking change"""
    change_id: str
    
    # Versions
    from_version: str = ""
    to_version: str = ""
    
    # Change
    change_type: ChangeType = ChangeType.BREAKING
    description: str = ""
    
    # Impact
    affected_endpoints: List[str] = field(default_factory=list)
    impact_level: str = "high"  # high, medium, low
    
    # Migration
    migration_guide: str = ""
    
    # Time
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class Migration:
    """Миграция версии"""
    migration_id: str
    
    # Versions
    from_version: str = ""
    to_version: str = ""
    
    # Status
    status: MigrationStatus = MigrationStatus.PLANNED
    
    # Steps
    steps: List[str] = field(default_factory=list)
    current_step: int = 0
    
    # Clients
    total_clients: int = 0
    migrated_clients: int = 0
    
    # Dates
    planned_start: Optional[datetime] = None
    planned_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None


@dataclass
class ClientSDK:
    """Клиентский SDK"""
    sdk_id: str
    name: str = ""
    language: str = ""  # python, javascript, java, etc.
    
    # Version
    sdk_version: str = ""
    api_version: str = ""
    
    # Status
    latest: bool = False
    deprecated: bool = False
    
    # Downloads
    download_count: int = 0
    
    # Released
    released_at: datetime = field(default_factory=datetime.now)


@dataclass
class VersionUsage:
    """Использование версии"""
    version: str = ""
    
    # Metrics
    request_count: int = 0
    unique_clients: int = 0
    error_rate: float = 0
    
    # Trend
    trend_direction: str = "stable"  # up, down, stable
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)


class CompatibilityChecker:
    """Проверка совместимости"""
    
    def check(self, old_version: APIVersion, new_version: APIVersion) -> tuple[CompatibilityLevel, List[BreakingChange]]:
        """Проверка совместимости версий"""
        breaking_changes = []
        
        old_endpoints = {e.path + e.method: e for e in old_version.endpoints}
        new_endpoints = {e.path + e.method: e for e in new_version.endpoints}
        
        # Check removed endpoints
        for key, endpoint in old_endpoints.items():
            if key not in new_endpoints:
                breaking_changes.append(BreakingChange(
                    change_id=f"bc_{uuid.uuid4().hex[:8]}",
                    from_version=old_version.version,
                    to_version=new_version.version,
                    change_type=ChangeType.BREAKING,
                    description=f"Endpoint removed: {endpoint.method} {endpoint.path}",
                    affected_endpoints=[endpoint.path],
                    impact_level="high"
                ))
                
        # Check schema changes (simplified)
        for key, old_ep in old_endpoints.items():
            if key in new_endpoints:
                new_ep = new_endpoints[key]
                
                # Check if required params removed
                old_params = set(old_ep.query_params)
                new_params = set(new_ep.query_params)
                
                added_params = new_params - old_params
                if added_params:
                    # New required params = breaking change
                    breaking_changes.append(BreakingChange(
                        change_id=f"bc_{uuid.uuid4().hex[:8]}",
                        from_version=old_version.version,
                        to_version=new_version.version,
                        change_type=ChangeType.BREAKING,
                        description=f"New parameters added to {old_ep.path}: {added_params}",
                        affected_endpoints=[old_ep.path],
                        impact_level="medium"
                    ))
                    
        # Determine compatibility level
        if not breaking_changes:
            return CompatibilityLevel.FULL, breaking_changes
        elif len(breaking_changes) <= 2:
            return CompatibilityLevel.BACKWARD, breaking_changes
        else:
            return CompatibilityLevel.NONE, breaking_changes


class VersionRouter:
    """Маршрутизатор версий"""
    
    def __init__(self):
        self.routes: Dict[str, APIVersion] = {}
        self.default_version: Optional[str] = None
        
    def register(self, version: APIVersion):
        """Регистрация версии"""
        self.routes[version.version] = version
        
        if version.status == VersionStatus.STABLE and not self.default_version:
            self.default_version = version.version
            
    def route(self, requested_version: Optional[str]) -> Optional[APIVersion]:
        """Маршрутизация к версии"""
        if requested_version and requested_version in self.routes:
            return self.routes[requested_version]
            
        if self.default_version:
            return self.routes.get(self.default_version)
            
        return None


class APIVersioningPlatform:
    """Платформа версионирования API"""
    
    def __init__(self):
        self.versions: Dict[str, APIVersion] = {}
        self.breaking_changes: List[BreakingChange] = []
        self.migrations: Dict[str, Migration] = {}
        self.sdks: Dict[str, ClientSDK] = {}
        self.usage_stats: Dict[str, VersionUsage] = {}
        
        self.compatibility_checker = CompatibilityChecker()
        self.router = VersionRouter()
        
    def create_version(self, version: str, major: int = 1,
                      minor: int = 0, patch: int = 0) -> APIVersion:
        """Создание версии"""
        api_version = APIVersion(
            version_id=f"ver_{uuid.uuid4().hex[:8]}",
            version=version,
            major=major,
            minor=minor,
            patch=patch,
            base_path=f"/api/{version}"
        )
        
        self.versions[version] = api_version
        self.router.register(api_version)
        
        return api_version
        
    def add_endpoint(self, version: str, path: str, method: str = "GET",
                    request_schema: Dict = None, response_schema: Dict = None,
                    query_params: List[str] = None) -> Optional[APIEndpoint]:
        """Добавление эндпоинта"""
        api_version = self.versions.get(version)
        if not api_version:
            return None
            
        endpoint = APIEndpoint(
            endpoint_id=f"ep_{uuid.uuid4().hex[:8]}",
            path=path,
            method=method,
            request_schema=request_schema or {},
            response_schema=response_schema or {},
            query_params=query_params or []
        )
        
        api_version.endpoints.append(endpoint)
        return endpoint
        
    def release_version(self, version: str, status: VersionStatus = VersionStatus.STABLE):
        """Релиз версии"""
        api_version = self.versions.get(version)
        if not api_version:
            return
            
        api_version.status = status
        api_version.released_at = datetime.now()
        
        # Check compatibility with previous stable version
        stable_versions = [v for v in self.versions.values()
                         if v.status == VersionStatus.STABLE and v.version != version]
        
        if stable_versions:
            prev_version = max(stable_versions, key=lambda v: (v.major, v.minor, v.patch))
            compat, changes = self.compatibility_checker.check(prev_version, api_version)
            self.breaking_changes.extend(changes)
            
    def deprecate_version(self, version: str, sunset_days: int = 90):
        """Устаревание версии"""
        api_version = self.versions.get(version)
        if not api_version:
            return
            
        api_version.status = VersionStatus.DEPRECATED
        api_version.deprecated_at = datetime.now()
        api_version.sunset_at = datetime.now() + timedelta(days=sunset_days)
        
    def plan_migration(self, from_version: str, to_version: str,
                      steps: List[str] = None) -> Migration:
        """Планирование миграции"""
        migration = Migration(
            migration_id=f"mig_{uuid.uuid4().hex[:8]}",
            from_version=from_version,
            to_version=to_version,
            steps=steps or ["Analyze impact", "Update clients", "Test", "Deploy", "Monitor"],
            planned_start=datetime.now() + timedelta(days=7),
            planned_end=datetime.now() + timedelta(days=30)
        )
        
        self.migrations[migration.migration_id] = migration
        return migration
        
    async def execute_migration(self, migration_id: str) -> bool:
        """Выполнение миграции"""
        migration = self.migrations.get(migration_id)
        if not migration:
            return False
            
        migration.status = MigrationStatus.IN_PROGRESS
        migration.actual_start = datetime.now()
        
        # Simulate migration steps
        for i, step in enumerate(migration.steps):
            migration.current_step = i
            await asyncio.sleep(0.05)
            
            # Simulate client migration
            migration.migrated_clients = int(migration.total_clients * (i + 1) / len(migration.steps))
            
        migration.status = MigrationStatus.COMPLETED
        migration.actual_end = datetime.now()
        migration.migrated_clients = migration.total_clients
        
        return True
        
    def register_sdk(self, name: str, language: str,
                    sdk_version: str, api_version: str) -> ClientSDK:
        """Регистрация SDK"""
        sdk = ClientSDK(
            sdk_id=f"sdk_{uuid.uuid4().hex[:8]}",
            name=name,
            language=language,
            sdk_version=sdk_version,
            api_version=api_version,
            latest=True
        )
        
        # Mark previous SDKs for this language as not latest
        for existing in self.sdks.values():
            if existing.language == language and existing.name == name:
                existing.latest = False
                
        self.sdks[sdk.sdk_id] = sdk
        return sdk
        
    def record_usage(self, version: str, requests: int, clients: int, errors: int = 0):
        """Запись использования"""
        self.usage_stats[version] = VersionUsage(
            version=version,
            request_count=requests,
            unique_clients=clients,
            error_rate=errors / requests * 100 if requests > 0 else 0,
            period_end=datetime.now()
        )
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        return {
            "total_versions": len(self.versions),
            "stable_versions": len([v for v in self.versions.values() if v.status == VersionStatus.STABLE]),
            "deprecated_versions": len([v for v in self.versions.values() if v.status == VersionStatus.DEPRECATED]),
            "total_endpoints": sum(len(v.endpoints) for v in self.versions.values()),
            "breaking_changes": len(self.breaking_changes),
            "active_migrations": len([m for m in self.migrations.values() if m.status == MigrationStatus.IN_PROGRESS]),
            "total_sdks": len(self.sdks),
            "sdk_languages": len(set(s.language for s in self.sdks.values()))
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 220: API Versioning Platform")
    print("=" * 60)
    
    platform = APIVersioningPlatform()
    print("✓ API Versioning Platform created")
    
    # Create versions
    print("\n📋 Creating API Versions...")
    
    # V1
    v1 = platform.create_version("v1", 1, 0, 0)
    platform.add_endpoint("v1", "/users", "GET", query_params=["limit", "offset"])
    platform.add_endpoint("v1", "/users/{id}", "GET")
    platform.add_endpoint("v1", "/users", "POST")
    platform.add_endpoint("v1", "/orders", "GET", query_params=["status"])
    platform.add_endpoint("v1", "/orders/{id}", "GET")
    platform.release_version("v1")
    print(f"  ✓ {v1.version}: {len(v1.endpoints)} endpoints (stable)")
    
    # V2
    v2 = platform.create_version("v2", 2, 0, 0)
    platform.add_endpoint("v2", "/users", "GET", query_params=["limit", "offset", "sort"])
    platform.add_endpoint("v2", "/users/{id}", "GET")
    platform.add_endpoint("v2", "/users", "POST")
    platform.add_endpoint("v2", "/users/{id}/profile", "GET")  # New endpoint
    platform.add_endpoint("v2", "/orders", "GET", query_params=["status", "date_from", "date_to"])
    platform.add_endpoint("v2", "/orders/{id}", "GET")
    platform.add_endpoint("v2", "/orders/{id}/items", "GET")  # New endpoint
    platform.release_version("v2")
    print(f"  ✓ {v2.version}: {len(v2.endpoints)} endpoints (stable)")
    
    # V3 Beta
    v3 = platform.create_version("v3", 3, 0, 0)
    platform.add_endpoint("v3", "/users", "GET", query_params=["limit", "cursor", "filter"])
    platform.add_endpoint("v3", "/users/{id}", "GET")
    platform.add_endpoint("v3", "/graphql", "POST")  # New GraphQL endpoint
    platform.release_version("v3", VersionStatus.BETA)
    print(f"  ✓ {v3.version}: {len(v3.endpoints)} endpoints (beta)")
    
    # Deprecate V1
    print("\n⚠️ Deprecating Old Version...")
    platform.deprecate_version("v1", sunset_days=60)
    print(f"  ✓ v1 deprecated, sunset: {v1.sunset_at.strftime('%Y-%m-%d')}")
    
    # Record usage
    print("\n📊 Recording Usage Statistics...")
    platform.record_usage("v1", 50000, 120, 250)
    platform.record_usage("v2", 500000, 850, 1500)
    platform.record_usage("v3", 10000, 50, 100)
    
    # Plan migration
    print("\n🔄 Planning Migration...")
    migration = platform.plan_migration(
        "v1", "v2",
        ["Notify clients", "Update SDKs", "Parallel running", "Switch traffic", "Retire v1"]
    )
    migration.total_clients = 120
    print(f"  ✓ Migration {migration.migration_id[:12]}: v1 -> v2")
    
    # Execute migration
    print("\n⚡ Executing Migration...")
    await platform.execute_migration(migration.migration_id)
    print(f"  ✓ Migration completed: {migration.migrated_clients}/{migration.total_clients} clients")
    
    # Register SDKs
    print("\n📦 Registering Client SDKs...")
    
    sdks_config = [
        ("api-client-python", "python", "2.3.0", "v2"),
        ("api-client-js", "javascript", "2.1.0", "v2"),
        ("api-client-java", "java", "2.0.1", "v2"),
        ("api-client-go", "go", "2.0.0", "v2"),
        ("api-client-python", "python", "3.0.0-beta", "v3"),
    ]
    
    for name, lang, sdk_ver, api_ver in sdks_config:
        sdk = platform.register_sdk(name, lang, sdk_ver, api_ver)
        latest = "✓ latest" if sdk.latest else ""
        print(f"  ✓ {name} {sdk_ver} ({lang}) {latest}")
    
    # Display versions
    print("\n📋 API Version Inventory:")
    
    print("\n  ┌──────────┬────────────┬────────────┬────────────┬────────────┐")
    print("  │ Version  │ Status     │ Endpoints  │ Released   │ Sunset     │")
    print("  ├──────────┼────────────┼────────────┼────────────┼────────────┤")
    
    for version in platform.versions.values():
        ver = version.version.ljust(8)
        status = version.status.value[:10].ljust(10)
        eps = str(len(version.endpoints)).center(10)
        released = version.released_at.strftime("%Y-%m-%d") if version.released_at else "N/A"
        released = released.ljust(10)
        sunset = version.sunset_at.strftime("%Y-%m-%d") if version.sunset_at else "N/A"
        sunset = sunset.ljust(10)
        
        print(f"  │ {ver} │ {status} │ {eps} │ {released} │ {sunset} │")
        
    print("  └──────────┴────────────┴────────────┴────────────┴────────────┘")
    
    # Usage statistics
    print("\n📊 Version Usage:")
    
    total_requests = sum(u.request_count for u in platform.usage_stats.values())
    
    for version, usage in platform.usage_stats.items():
        pct = usage.request_count / total_requests * 100 if total_requests > 0 else 0
        bar_len = int(pct / 5)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        
        print(f"  {version:4s} [{bar}] {pct:5.1f}% ({usage.request_count:,} requests)")
        
    # Breaking changes
    print("\n⚠️ Breaking Changes:")
    
    if platform.breaking_changes:
        for change in platform.breaking_changes[:5]:
            print(f"  • {change.from_version} -> {change.to_version}: {change.description}")
    else:
        print("  No breaking changes detected")
        
    # SDKs by language
    print("\n📦 SDKs by Language:")
    
    by_language = {}
    for sdk in platform.sdks.values():
        if sdk.language not in by_language:
            by_language[sdk.language] = []
        by_language[sdk.language].append(sdk)
        
    for lang, sdks in by_language.items():
        latest = next((s for s in sdks if s.latest), None)
        latest_ver = latest.sdk_version if latest else "N/A"
        print(f"  {lang:12s}: {len(sdks)} version(s), latest: {latest_ver}")
        
    # Endpoints per version
    print("\n🔗 Endpoints per Version:")
    
    for version in platform.versions.values():
        print(f"\n  {version.version} ({version.status.value}):")
        for ep in version.endpoints[:3]:
            deprecated = " [DEPRECATED]" if ep.deprecated else ""
            print(f"    {ep.method:6s} {ep.path}{deprecated}")
        if len(version.endpoints) > 3:
            print(f"    ... and {len(version.endpoints) - 3} more")
            
    # Migration status
    print("\n🔄 Migrations:")
    
    for mig in platform.migrations.values():
        status_icons = {
            MigrationStatus.PLANNED: "📅",
            MigrationStatus.IN_PROGRESS: "🔄",
            MigrationStatus.COMPLETED: "✅",
            MigrationStatus.FAILED: "❌"
        }
        icon = status_icons.get(mig.status, "❓")
        
        print(f"  {icon} {mig.from_version} -> {mig.to_version}: {mig.status.value}")
        print(f"      Clients: {mig.migrated_clients}/{mig.total_clients}")
        
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📈 Platform Statistics:")
    
    print(f"\n  Total Versions: {stats['total_versions']}")
    print(f"  Stable: {stats['stable_versions']}")
    print(f"  Deprecated: {stats['deprecated_versions']}")
    print(f"  Total Endpoints: {stats['total_endpoints']}")
    print(f"  Breaking Changes: {stats['breaking_changes']}")
    print(f"  SDKs: {stats['total_sdks']} ({stats['sdk_languages']} languages)")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                     API Versioning Dashboard                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ API Versions:                  {stats['total_versions']:>12}                        │")
    print(f"│ Total Endpoints:               {stats['total_endpoints']:>12}                        │")
    print(f"│ Client SDKs:                   {stats['total_sdks']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Breaking Changes:              {stats['breaking_changes']:>12}                        │")
    print(f"│ Active Migrations:             {stats['active_migrations']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("API Versioning Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
