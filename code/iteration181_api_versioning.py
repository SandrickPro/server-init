#!/usr/bin/env python3
"""
Server Init - Iteration 181: API Versioning Platform
Платформа версионирования API

Функционал:
- Version Management - управление версиями
- Breaking Change Detection - обнаружение breaking changes
- Deprecation Policies - политики устаревания
- Migration Guides - руководства миграции
- Compatibility Matrix - матрица совместимости
- Version Lifecycle - жизненный цикл версий
- Consumer Tracking - отслеживание потребителей
- Sunset Planning - планирование отключения
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
    DRAFT = "draft"
    BETA = "beta"
    STABLE = "stable"
    DEPRECATED = "deprecated"
    SUNSET = "sunset"
    RETIRED = "retired"


class ChangeType(Enum):
    """Тип изменения"""
    BREAKING = "breaking"
    NON_BREAKING = "non_breaking"
    ADDITIVE = "additive"
    DEPRECATION = "deprecation"
    BUG_FIX = "bug_fix"


class ChangeSeverity(Enum):
    """Серьёзность изменения"""
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"


class DeprecationReason(Enum):
    """Причина устаревания"""
    SECURITY = "security"
    PERFORMANCE = "performance"
    REDESIGN = "redesign"
    CONSOLIDATION = "consolidation"
    COMPLIANCE = "compliance"


class VersioningStrategy(Enum):
    """Стратегия версионирования"""
    URL_PATH = "url_path"  # /v1/resource
    QUERY_PARAM = "query_param"  # ?version=1
    HEADER = "header"  # X-API-Version: 1
    CONTENT_TYPE = "content_type"  # application/vnd.api.v1+json


@dataclass
class SemanticVersion:
    """Семантическая версия"""
    major: int = 1
    minor: int = 0
    patch: int = 0
    prerelease: str = ""
    build: str = ""
    
    def __str__(self):
        v = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            v += f"-{self.prerelease}"
        if self.build:
            v += f"+{self.build}"
        return v
        
    def bump_major(self):
        return SemanticVersion(self.major + 1, 0, 0)
        
    def bump_minor(self):
        return SemanticVersion(self.major, self.minor + 1, 0)
        
    def bump_patch(self):
        return SemanticVersion(self.major, self.minor, self.patch + 1)


@dataclass
class APIVersion:
    """Версия API"""
    version_id: str
    api_name: str = ""
    version: SemanticVersion = field(default_factory=SemanticVersion)
    
    # Status
    status: VersionStatus = VersionStatus.DRAFT
    
    # Lifecycle
    created_at: datetime = field(default_factory=datetime.now)
    released_at: Optional[datetime] = None
    deprecated_at: Optional[datetime] = None
    sunset_at: Optional[datetime] = None
    
    # Documentation
    changelog: str = ""
    migration_guide: str = ""
    
    # Strategy
    versioning_strategy: VersioningStrategy = VersioningStrategy.URL_PATH


@dataclass
class APIChange:
    """Изменение API"""
    change_id: str
    api_name: str = ""
    
    # Version info
    from_version: str = ""
    to_version: str = ""
    
    # Change details
    change_type: ChangeType = ChangeType.NON_BREAKING
    severity: ChangeSeverity = ChangeSeverity.MINOR
    
    # Description
    title: str = ""
    description: str = ""
    
    # Affected
    affected_endpoints: List[str] = field(default_factory=list)
    affected_schemas: List[str] = field(default_factory=list)
    
    # Migration
    migration_steps: List[str] = field(default_factory=list)
    code_examples: Dict[str, str] = field(default_factory=dict)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DeprecationNotice:
    """Уведомление об устаревании"""
    notice_id: str
    api_name: str = ""
    version: str = ""
    
    # Reason
    reason: DeprecationReason = DeprecationReason.REDESIGN
    description: str = ""
    
    # Timeline
    announced_at: datetime = field(default_factory=datetime.now)
    deprecated_at: Optional[datetime] = None
    sunset_date: Optional[datetime] = None
    
    # Alternative
    replacement_version: str = ""
    migration_guide_url: str = ""
    
    # Affected consumers
    affected_consumers: List[str] = field(default_factory=list)


@dataclass
class APIConsumer:
    """Потребитель API"""
    consumer_id: str
    name: str = ""
    contact_email: str = ""
    
    # Usage
    api_name: str = ""
    versions_used: List[str] = field(default_factory=list)
    
    # Metrics
    request_count: int = 0
    last_request: Optional[datetime] = None
    
    # Status
    migrated: bool = False
    migration_deadline: Optional[datetime] = None


@dataclass
class CompatibilityReport:
    """Отчёт о совместимости"""
    report_id: str
    api_name: str = ""
    
    # Versions
    base_version: str = ""
    target_version: str = ""
    
    # Analysis
    is_compatible: bool = True
    breaking_changes: List[str] = field(default_factory=list)
    deprecations: List[str] = field(default_factory=list)
    
    # Score
    compatibility_score: float = 100.0
    
    # Generated
    generated_at: datetime = field(default_factory=datetime.now)


class VersionManager:
    """Менеджер версий"""
    
    def __init__(self):
        self.versions: Dict[str, Dict[str, APIVersion]] = {}  # api_name -> version_str -> APIVersion
        
    def register_version(self, version: APIVersion):
        """Регистрация версии"""
        if version.api_name not in self.versions:
            self.versions[version.api_name] = {}
        self.versions[version.api_name][str(version.version)] = version
        
    def get_version(self, api_name: str, version_str: str) -> Optional[APIVersion]:
        """Получение версии"""
        return self.versions.get(api_name, {}).get(version_str)
        
    def get_latest_stable(self, api_name: str) -> Optional[APIVersion]:
        """Получение последней стабильной версии"""
        api_versions = self.versions.get(api_name, {})
        stable_versions = [v for v in api_versions.values() if v.status == VersionStatus.STABLE]
        if stable_versions:
            return max(stable_versions, key=lambda v: (v.version.major, v.version.minor, v.version.patch))
        return None
        
    def deprecate_version(self, api_name: str, version_str: str, sunset_date: datetime) -> bool:
        """Устаревание версии"""
        version = self.get_version(api_name, version_str)
        if version:
            version.status = VersionStatus.DEPRECATED
            version.deprecated_at = datetime.now()
            version.sunset_at = sunset_date
            return True
        return False


class ChangeDetector:
    """Детектор изменений"""
    
    def __init__(self):
        self.changes: Dict[str, List[APIChange]] = {}
        
    def detect_breaking_changes(self, old_schema: Dict, new_schema: Dict) -> List[APIChange]:
        """Обнаружение breaking changes"""
        changes = []
        
        # Check for removed endpoints
        old_endpoints = set(old_schema.get("endpoints", []))
        new_endpoints = set(new_schema.get("endpoints", []))
        
        removed = old_endpoints - new_endpoints
        for endpoint in removed:
            change = APIChange(
                change_id=f"change_{uuid.uuid4().hex[:8]}",
                change_type=ChangeType.BREAKING,
                severity=ChangeSeverity.MAJOR,
                title=f"Removed endpoint: {endpoint}",
                description=f"Endpoint {endpoint} has been removed",
                affected_endpoints=[endpoint]
            )
            changes.append(change)
            
        # Check for required field changes
        old_required = set(old_schema.get("required_fields", []))
        new_required = set(new_schema.get("required_fields", []))
        
        added_required = new_required - old_required
        for field in added_required:
            change = APIChange(
                change_id=f"change_{uuid.uuid4().hex[:8]}",
                change_type=ChangeType.BREAKING,
                severity=ChangeSeverity.MAJOR,
                title=f"New required field: {field}",
                description=f"Field {field} is now required"
            )
            changes.append(change)
            
        return changes
        
    def analyze_changes(self, api_name: str, from_v: str, to_v: str) -> List[APIChange]:
        """Анализ изменений между версиями"""
        key = f"{api_name}:{from_v}->{to_v}"
        return self.changes.get(key, [])


class DeprecationManager:
    """Менеджер устаревания"""
    
    def __init__(self):
        self.notices: Dict[str, DeprecationNotice] = {}
        
    def create_notice(self, api_name: str, version: str, reason: DeprecationReason,
                     sunset_date: datetime, replacement: str = "") -> DeprecationNotice:
        """Создание уведомления об устаревании"""
        notice = DeprecationNotice(
            notice_id=f"deprecation_{uuid.uuid4().hex[:8]}",
            api_name=api_name,
            version=version,
            reason=reason,
            sunset_date=sunset_date,
            replacement_version=replacement,
            deprecated_at=datetime.now()
        )
        self.notices[notice.notice_id] = notice
        return notice
        
    def get_upcoming_sunsets(self, days: int = 30) -> List[DeprecationNotice]:
        """Получение предстоящих отключений"""
        deadline = datetime.now() + timedelta(days=days)
        return [
            n for n in self.notices.values()
            if n.sunset_date and n.sunset_date <= deadline
        ]


class ConsumerTracker:
    """Трекер потребителей"""
    
    def __init__(self):
        self.consumers: Dict[str, APIConsumer] = {}
        
    def register_consumer(self, consumer: APIConsumer):
        """Регистрация потребителя"""
        self.consumers[consumer.consumer_id] = consumer
        
    def track_usage(self, consumer_id: str, api_name: str, version: str):
        """Отслеживание использования"""
        consumer = self.consumers.get(consumer_id)
        if consumer:
            consumer.request_count += 1
            consumer.last_request = datetime.now()
            if version not in consumer.versions_used:
                consumer.versions_used.append(version)
                
    def get_consumers_on_version(self, api_name: str, version: str) -> List[APIConsumer]:
        """Получение потребителей на версии"""
        return [
            c for c in self.consumers.values()
            if c.api_name == api_name and version in c.versions_used
        ]


class CompatibilityAnalyzer:
    """Анализатор совместимости"""
    
    def __init__(self, change_detector: ChangeDetector):
        self.change_detector = change_detector
        
    def analyze(self, api_name: str, base_version: str, target_version: str) -> CompatibilityReport:
        """Анализ совместимости"""
        report = CompatibilityReport(
            report_id=f"compat_{uuid.uuid4().hex[:8]}",
            api_name=api_name,
            base_version=base_version,
            target_version=target_version
        )
        
        changes = self.change_detector.analyze_changes(api_name, base_version, target_version)
        
        for change in changes:
            if change.change_type == ChangeType.BREAKING:
                report.breaking_changes.append(change.title)
                report.is_compatible = False
            elif change.change_type == ChangeType.DEPRECATION:
                report.deprecations.append(change.title)
                
        # Calculate score
        if report.breaking_changes:
            report.compatibility_score = max(0, 100 - len(report.breaking_changes) * 20)
        elif report.deprecations:
            report.compatibility_score = max(50, 100 - len(report.deprecations) * 10)
            
        return report


class MigrationPlanner:
    """Планировщик миграции"""
    
    def __init__(self, version_manager: VersionManager):
        self.version_manager = version_manager
        
    def create_migration_plan(self, api_name: str, from_version: str, to_version: str) -> Dict[str, Any]:
        """Создание плана миграции"""
        return {
            "api": api_name,
            "from_version": from_version,
            "to_version": to_version,
            "steps": [
                {"step": 1, "action": "Review breaking changes"},
                {"step": 2, "action": "Update client SDK"},
                {"step": 3, "action": "Test in staging environment"},
                {"step": 4, "action": "Update endpoint URLs"},
                {"step": 5, "action": "Deploy to production"},
                {"step": 6, "action": "Verify functionality"},
            ],
            "estimated_effort": "2-4 hours",
            "risk_level": "medium"
        }


class APIVersioningPlatform:
    """Платформа версионирования API"""
    
    def __init__(self):
        self.version_manager = VersionManager()
        self.change_detector = ChangeDetector()
        self.deprecation_manager = DeprecationManager()
        self.consumer_tracker = ConsumerTracker()
        self.compatibility_analyzer = CompatibilityAnalyzer(self.change_detector)
        self.migration_planner = MigrationPlanner(self.version_manager)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        all_versions = []
        for api_versions in self.version_manager.versions.values():
            all_versions.extend(api_versions.values())
            
        return {
            "total_apis": len(self.version_manager.versions),
            "total_versions": len(all_versions),
            "versions_by_status": {
                status.value: len([v for v in all_versions if v.status == status])
                for status in VersionStatus
            },
            "total_consumers": len(self.consumer_tracker.consumers),
            "deprecation_notices": len(self.deprecation_manager.notices)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 181: API Versioning Platform")
    print("=" * 60)
    
    platform = APIVersioningPlatform()
    print("✓ API Versioning Platform created")
    
    # Register API versions
    print("\n📋 Registering API Versions...")
    
    apis = ["users-api", "orders-api", "payments-api"]
    
    for api_name in apis:
        versions = [
            APIVersion(
                version_id=f"{api_name}_v1",
                api_name=api_name,
                version=SemanticVersion(1, 0, 0),
                status=VersionStatus.DEPRECATED,
                released_at=datetime.now() - timedelta(days=365),
                deprecated_at=datetime.now() - timedelta(days=30)
            ),
            APIVersion(
                version_id=f"{api_name}_v2",
                api_name=api_name,
                version=SemanticVersion(2, 0, 0),
                status=VersionStatus.STABLE,
                released_at=datetime.now() - timedelta(days=180)
            ),
            APIVersion(
                version_id=f"{api_name}_v3",
                api_name=api_name,
                version=SemanticVersion(3, 0, 0),
                status=VersionStatus.BETA,
                released_at=datetime.now() - timedelta(days=30)
            ),
        ]
        
        for v in versions:
            platform.version_manager.register_version(v)
            
        print(f"  ✓ {api_name}: {len(versions)} versions")
        
    # Show version matrix
    print("\n📊 Version Matrix:")
    
    print("\n  ┌────────────────┬────────────┬──────────────┬───────────────┐")
    print("  │ API            │ Version    │ Status       │ Released      │")
    print("  ├────────────────┼────────────┼──────────────┼───────────────┤")
    
    for api_name in apis:
        for v_str, version in platform.version_manager.versions[api_name].items():
            name = api_name[:14].ljust(14)
            ver = v_str[:10].ljust(10)
            status = version.status.value[:12].ljust(12)
            released = version.released_at.strftime("%Y-%m-%d") if version.released_at else "N/A"
            print(f"  │ {name} │ {ver} │ {status} │ {released:>13} │")
            
    print("  └────────────────┴────────────┴──────────────┴───────────────┘")
    
    # Register consumers
    print("\n👥 Registering API Consumers...")
    
    consumers = [
        APIConsumer(consumer_id="mobile-app", name="Mobile App", api_name="users-api", versions_used=["1.0.0", "2.0.0"], request_count=50000),
        APIConsumer(consumer_id="web-app", name="Web Application", api_name="users-api", versions_used=["2.0.0"], request_count=120000),
        APIConsumer(consumer_id="partner-a", name="Partner A Integration", api_name="orders-api", versions_used=["1.0.0"], request_count=8000),
        APIConsumer(consumer_id="partner-b", name="Partner B Integration", api_name="orders-api", versions_used=["2.0.0"], request_count=25000),
        APIConsumer(consumer_id="analytics", name="Analytics Service", api_name="payments-api", versions_used=["2.0.0", "3.0.0"], request_count=95000),
    ]
    
    for consumer in consumers:
        platform.consumer_tracker.register_consumer(consumer)
        print(f"  ✓ {consumer.name}: {consumer.api_name} ({', '.join(consumer.versions_used)})")
        
    # Create deprecation notices
    print("\n⚠️ Deprecation Notices...")
    
    notices = [
        platform.deprecation_manager.create_notice(
            "users-api", "1.0.0",
            DeprecationReason.REDESIGN,
            datetime.now() + timedelta(days=60),
            "2.0.0"
        ),
        platform.deprecation_manager.create_notice(
            "orders-api", "1.0.0",
            DeprecationReason.SECURITY,
            datetime.now() + timedelta(days=30),
            "2.0.0"
        ),
    ]
    
    for notice in notices:
        days_until = (notice.sunset_date - datetime.now()).days if notice.sunset_date else 0
        print(f"  ⚠️ {notice.api_name} v{notice.version}: Sunset in {days_until} days")
        print(f"     Reason: {notice.reason.value}, Replacement: v{notice.replacement_version}")
        
    # Breaking change detection
    print("\n🔍 Breaking Change Detection...")
    
    old_schema = {
        "endpoints": ["/users", "/users/{id}", "/users/{id}/profile", "/users/legacy"],
        "required_fields": ["id", "email"]
    }
    
    new_schema = {
        "endpoints": ["/users", "/users/{id}", "/users/{id}/profile", "/users/{id}/settings"],
        "required_fields": ["id", "email", "phone"]
    }
    
    changes = platform.change_detector.detect_breaking_changes(old_schema, new_schema)
    
    print(f"\n  Found {len(changes)} breaking changes:")
    for change in changes:
        print(f"    • [{change.severity.value.upper()}] {change.title}")
        
    # Compatibility analysis
    print("\n🔄 Compatibility Analysis...")
    
    # Store changes for analysis
    platform.change_detector.changes["users-api:1.0.0->2.0.0"] = changes
    
    report = platform.compatibility_analyzer.analyze("users-api", "1.0.0", "2.0.0")
    
    print(f"\n  Base: v{report.base_version} → Target: v{report.target_version}")
    print(f"  Compatible: {'Yes' if report.is_compatible else 'No'}")
    print(f"  Compatibility Score: {report.compatibility_score}%")
    print(f"  Breaking Changes: {len(report.breaking_changes)}")
    print(f"  Deprecations: {len(report.deprecations)}")
    
    # Migration plan
    print("\n📝 Migration Plan:")
    
    plan = platform.migration_planner.create_migration_plan("users-api", "1.0.0", "2.0.0")
    
    print(f"\n  API: {plan['api']}")
    print(f"  From: v{plan['from_version']} → To: v{plan['to_version']}")
    print(f"  Estimated Effort: {plan['estimated_effort']}")
    print(f"  Risk Level: {plan['risk_level']}")
    
    print("\n  Steps:")
    for step in plan['steps']:
        print(f"    {step['step']}. {step['action']}")
        
    # Consumers on deprecated versions
    print("\n📊 Consumers on Deprecated Versions:")
    
    deprecated_consumers = platform.consumer_tracker.get_consumers_on_version("users-api", "1.0.0")
    
    for consumer in deprecated_consumers:
        print(f"  • {consumer.name}: {consumer.request_count:,} requests")
        
    # Upcoming sunsets
    print("\n⏰ Upcoming Sunsets (next 90 days):")
    
    upcoming = platform.deprecation_manager.get_upcoming_sunsets(90)
    
    for notice in upcoming:
        days = (notice.sunset_date - datetime.now()).days if notice.sunset_date else 0
        print(f"  • {notice.api_name} v{notice.version}: {days} days remaining")
        
    # Platform statistics
    print("\n📈 Platform Statistics:")
    
    stats = platform.get_statistics()
    
    print(f"\n  Total APIs: {stats['total_apis']}")
    print(f"  Total Versions: {stats['total_versions']}")
    print(f"  Total Consumers: {stats['total_consumers']}")
    print(f"  Deprecation Notices: {stats['deprecation_notices']}")
    
    print("\n  Versions by Status:")
    for status, count in stats['versions_by_status'].items():
        if count > 0:
            print(f"    • {status}: {count}")
            
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    API Versioning Dashboard                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total APIs:                    {stats['total_apis']:>10}                     │")
    print(f"│ Total Versions:                {stats['total_versions']:>10}                     │")
    print(f"│ Active Consumers:              {stats['total_consumers']:>10}                     │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Stable Versions:               {stats['versions_by_status'].get('stable', 0):>10}                     │")
    print(f"│ Beta Versions:                 {stats['versions_by_status'].get('beta', 0):>10}                     │")
    print(f"│ Deprecated Versions:           {stats['versions_by_status'].get('deprecated', 0):>10}                     │")
    print(f"│ Pending Sunsets:               {len(upcoming):>10}                     │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("API Versioning Platform initialized!")
    print("=" * 60)
