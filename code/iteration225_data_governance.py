#!/usr/bin/env python3
"""
Server Init - Iteration 225: Data Governance Platform
Платформа управления данными

Функционал:
- Data Catalog - каталог данных
- Data Lineage - происхождение данных
- Quality Rules - правила качества
- Privacy Compliance - соответствие приватности
- Access Policies - политики доступа
- Data Classification - классификация данных
- Retention Policies - политики хранения
- Audit Trail - аудит изменений
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid


class DataClassification(Enum):
    """Классификация данных"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    PII = "pii"


class DataFormat(Enum):
    """Формат данных"""
    TABLE = "table"
    FILE = "file"
    STREAM = "stream"
    API = "api"
    DOCUMENT = "document"


class QualityDimension(Enum):
    """Измерение качества"""
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    TIMELINESS = "timeliness"
    UNIQUENESS = "uniqueness"


class ComplianceType(Enum):
    """Тип соответствия"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    SOX = "sox"


@dataclass
class DataOwner:
    """Владелец данных"""
    owner_id: str
    name: str = ""
    email: str = ""
    department: str = ""
    team: str = ""


@dataclass
class DataAsset:
    """Актив данных"""
    asset_id: str
    name: str = ""
    description: str = ""
    
    # Location
    source_system: str = ""
    database: str = ""
    schema: str = ""
    table: str = ""
    
    # Classification
    classification: DataClassification = DataClassification.INTERNAL
    format: DataFormat = DataFormat.TABLE
    
    # Ownership
    owner: Optional[DataOwner] = None
    steward: Optional[DataOwner] = None
    
    # Schema
    columns: List[str] = field(default_factory=list)
    row_count: int = 0
    size_bytes: int = 0
    
    # Tags
    tags: List[str] = field(default_factory=list)
    compliance_tags: List[ComplianceType] = field(default_factory=list)
    
    # Dates
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class DataColumn:
    """Колонка данных"""
    column_id: str
    asset_id: str = ""
    name: str = ""
    data_type: str = ""
    description: str = ""
    is_nullable: bool = True
    is_pii: bool = False
    classification: DataClassification = DataClassification.INTERNAL


@dataclass
class DataLineage:
    """Линейка данных"""
    lineage_id: str
    source_asset_id: str = ""
    target_asset_id: str = ""
    transformation: str = ""
    pipeline_name: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class QualityRule:
    """Правило качества"""
    rule_id: str
    name: str = ""
    asset_id: str = ""
    dimension: QualityDimension = QualityDimension.COMPLETENESS
    condition: str = ""  # SQL condition
    threshold: float = 95.0  # Percentage
    is_active: bool = True


@dataclass
class QualityResult:
    """Результат проверки качества"""
    result_id: str
    rule_id: str = ""
    asset_id: str = ""
    passed: bool = True
    score: float = 100.0
    failed_records: int = 0
    checked_at: datetime = field(default_factory=datetime.now)


@dataclass
class AccessPolicy:
    """Политика доступа"""
    policy_id: str
    name: str = ""
    asset_id: str = ""
    allowed_roles: List[str] = field(default_factory=list)
    denied_roles: List[str] = field(default_factory=list)
    requires_approval: bool = False
    expires_at: Optional[datetime] = None


@dataclass
class RetentionPolicy:
    """Политика хранения"""
    policy_id: str
    name: str = ""
    classification: DataClassification = DataClassification.INTERNAL
    retention_days: int = 365
    archive_after_days: int = 180
    delete_after_days: int = 730


@dataclass
class AuditEntry:
    """Запись аудита"""
    entry_id: str
    asset_id: str = ""
    action: str = ""  # read, write, delete, export
    user: str = ""
    details: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


class DataCatalog:
    """Каталог данных"""
    
    def __init__(self):
        self.assets: Dict[str, DataAsset] = {}
        self.columns: Dict[str, List[DataColumn]] = {}
        
    def register_asset(self, name: str, source: str, database: str,
                      schema: str, table: str, classification: DataClassification,
                      owner: DataOwner = None) -> DataAsset:
        """Регистрация актива"""
        asset = DataAsset(
            asset_id=f"asset_{uuid.uuid4().hex[:8]}",
            name=name,
            source_system=source,
            database=database,
            schema=schema,
            table=table,
            classification=classification,
            owner=owner
        )
        self.assets[asset.asset_id] = asset
        self.columns[asset.asset_id] = []
        return asset
        
    def add_column(self, asset_id: str, name: str, data_type: str,
                  is_pii: bool = False, description: str = "") -> Optional[DataColumn]:
        """Добавление колонки"""
        if asset_id not in self.assets:
            return None
            
        column = DataColumn(
            column_id=f"col_{uuid.uuid4().hex[:8]}",
            asset_id=asset_id,
            name=name,
            data_type=data_type,
            is_pii=is_pii,
            description=description,
            classification=DataClassification.PII if is_pii else DataClassification.INTERNAL
        )
        
        self.columns[asset_id].append(column)
        self.assets[asset_id].columns.append(name)
        return column
        
    def search(self, query: str = "", classification: DataClassification = None,
              tags: List[str] = None) -> List[DataAsset]:
        """Поиск активов"""
        results = []
        
        for asset in self.assets.values():
            match = True
            
            if query and query.lower() not in asset.name.lower():
                match = False
                
            if classification and asset.classification != classification:
                match = False
                
            if tags and not any(t in asset.tags for t in tags):
                match = False
                
            if match:
                results.append(asset)
                
        return results


class LineageTracker:
    """Трекер линейки данных"""
    
    def __init__(self):
        self.lineages: List[DataLineage] = []
        
    def add_lineage(self, source_id: str, target_id: str,
                   transformation: str = "", pipeline: str = "") -> DataLineage:
        """Добавление линейки"""
        lineage = DataLineage(
            lineage_id=f"lin_{uuid.uuid4().hex[:8]}",
            source_asset_id=source_id,
            target_asset_id=target_id,
            transformation=transformation,
            pipeline_name=pipeline
        )
        self.lineages.append(lineage)
        return lineage
        
    def get_upstream(self, asset_id: str) -> List[str]:
        """Получить upstream активы"""
        return [l.source_asset_id for l in self.lineages 
                if l.target_asset_id == asset_id]
        
    def get_downstream(self, asset_id: str) -> List[str]:
        """Получить downstream активы"""
        return [l.target_asset_id for l in self.lineages 
                if l.source_asset_id == asset_id]


class QualityEngine:
    """Движок качества данных"""
    
    def __init__(self):
        self.rules: Dict[str, QualityRule] = {}
        self.results: List[QualityResult] = []
        
    def create_rule(self, name: str, asset_id: str,
                   dimension: QualityDimension, threshold: float = 95.0,
                   condition: str = "") -> QualityRule:
        """Создание правила"""
        rule = QualityRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name=name,
            asset_id=asset_id,
            dimension=dimension,
            threshold=threshold,
            condition=condition
        )
        self.rules[rule.rule_id] = rule
        return rule
        
    def check_rule(self, rule: QualityRule) -> QualityResult:
        """Проверка правила"""
        # Simulate quality check
        score = random.uniform(85, 100)
        passed = score >= rule.threshold
        
        result = QualityResult(
            result_id=f"res_{uuid.uuid4().hex[:8]}",
            rule_id=rule.rule_id,
            asset_id=rule.asset_id,
            passed=passed,
            score=score,
            failed_records=int((100 - score) * 10) if not passed else 0
        )
        
        self.results.append(result)
        return result


class DataGovernancePlatform:
    """Платформа управления данными"""
    
    def __init__(self):
        self.catalog = DataCatalog()
        self.lineage = LineageTracker()
        self.quality = QualityEngine()
        self.owners: Dict[str, DataOwner] = {}
        self.access_policies: Dict[str, AccessPolicy] = {}
        self.retention_policies: Dict[str, RetentionPolicy] = {}
        self.audit_log: List[AuditEntry] = []
        
    def register_owner(self, name: str, email: str,
                      department: str, team: str = "") -> DataOwner:
        """Регистрация владельца"""
        owner = DataOwner(
            owner_id=f"own_{uuid.uuid4().hex[:8]}",
            name=name,
            email=email,
            department=department,
            team=team
        )
        self.owners[owner.owner_id] = owner
        return owner
        
    def create_asset(self, name: str, source: str, database: str,
                    schema: str, table: str, classification: DataClassification,
                    owner_id: str = "") -> DataAsset:
        """Создание актива"""
        owner = self.owners.get(owner_id)
        asset = self.catalog.register_asset(
            name, source, database, schema, table, classification, owner
        )
        
        self.log_audit(asset.asset_id, "create", "system", f"Asset created: {name}")
        return asset
        
    def add_lineage(self, source_id: str, target_id: str,
                   transformation: str = "", pipeline: str = "") -> DataLineage:
        """Добавление линейки"""
        return self.lineage.add_lineage(source_id, target_id, transformation, pipeline)
        
    def create_quality_rule(self, name: str, asset_id: str,
                           dimension: QualityDimension,
                           threshold: float = 95.0) -> QualityRule:
        """Создание правила качества"""
        return self.quality.create_rule(name, asset_id, dimension, threshold)
        
    def run_quality_checks(self, asset_id: str = None) -> List[QualityResult]:
        """Запуск проверок качества"""
        results = []
        
        for rule in self.quality.rules.values():
            if asset_id and rule.asset_id != asset_id:
                continue
            result = self.quality.check_rule(rule)
            results.append(result)
            
        return results
        
    def create_access_policy(self, name: str, asset_id: str,
                            allowed_roles: List[str],
                            requires_approval: bool = False) -> AccessPolicy:
        """Создание политики доступа"""
        policy = AccessPolicy(
            policy_id=f"pol_{uuid.uuid4().hex[:8]}",
            name=name,
            asset_id=asset_id,
            allowed_roles=allowed_roles,
            requires_approval=requires_approval
        )
        self.access_policies[policy.policy_id] = policy
        return policy
        
    def create_retention_policy(self, name: str,
                               classification: DataClassification,
                               retention_days: int = 365) -> RetentionPolicy:
        """Создание политики хранения"""
        policy = RetentionPolicy(
            policy_id=f"ret_{uuid.uuid4().hex[:8]}",
            name=name,
            classification=classification,
            retention_days=retention_days
        )
        self.retention_policies[policy.policy_id] = policy
        return policy
        
    def log_audit(self, asset_id: str, action: str, user: str, details: str):
        """Запись в аудит"""
        entry = AuditEntry(
            entry_id=f"aud_{uuid.uuid4().hex[:8]}",
            asset_id=asset_id,
            action=action,
            user=user,
            details=details
        )
        self.audit_log.append(entry)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        assets = list(self.catalog.assets.values())
        
        by_classification = {}
        for a in assets:
            c = a.classification.value
            if c not in by_classification:
                by_classification[c] = 0
            by_classification[c] += 1
            
        pii_columns = 0
        for cols in self.catalog.columns.values():
            pii_columns += len([c for c in cols if c.is_pii])
            
        quality_results = self.quality.results
        passed = len([r for r in quality_results if r.passed])
        
        return {
            "total_assets": len(assets),
            "by_classification": by_classification,
            "total_columns": sum(len(c) for c in self.catalog.columns.values()),
            "pii_columns": pii_columns,
            "lineage_edges": len(self.lineage.lineages),
            "quality_rules": len(self.quality.rules),
            "quality_checks_passed": passed,
            "quality_checks_total": len(quality_results),
            "access_policies": len(self.access_policies),
            "audit_entries": len(self.audit_log)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 225: Data Governance Platform")
    print("=" * 60)
    
    platform = DataGovernancePlatform()
    print("✓ Data Governance Platform created")
    
    # Register owners
    print("\n👤 Registering Data Owners...")
    
    owners = [
        platform.register_owner("Data Engineering", "data-eng@company.com", "Engineering", "Data Platform"),
        platform.register_owner("Analytics Team", "analytics@company.com", "Analytics", "BI"),
        platform.register_owner("Compliance Team", "compliance@company.com", "Legal", "Compliance"),
    ]
    
    for owner in owners:
        print(f"  ✓ {owner.name} ({owner.department})")
        
    # Create data assets
    print("\n📊 Creating Data Assets...")
    
    assets_config = [
        ("users", "PostgreSQL", "main_db", "public", "users", DataClassification.PII, owners[0].owner_id),
        ("orders", "PostgreSQL", "main_db", "public", "orders", DataClassification.CONFIDENTIAL, owners[0].owner_id),
        ("products", "PostgreSQL", "main_db", "public", "products", DataClassification.INTERNAL, owners[0].owner_id),
        ("payments", "PostgreSQL", "main_db", "financial", "payments", DataClassification.RESTRICTED, owners[2].owner_id),
        ("events", "Kafka", "events_cluster", "public", "user_events", DataClassification.INTERNAL, owners[0].owner_id),
        ("analytics_users", "Snowflake", "analytics", "public", "dim_users", DataClassification.CONFIDENTIAL, owners[1].owner_id),
        ("analytics_orders", "Snowflake", "analytics", "public", "fact_orders", DataClassification.CONFIDENTIAL, owners[1].owner_id),
        ("reports", "S3", "reports-bucket", "", "daily_reports", DataClassification.INTERNAL, owners[1].owner_id),
    ]
    
    assets = []
    for name, source, db, schema, table, classification, owner_id in assets_config:
        asset = platform.create_asset(name, source, db, schema, table, classification, owner_id)
        asset.row_count = random.randint(10000, 10000000)
        asset.size_bytes = random.randint(1000000, 1000000000)
        asset.tags = [source.lower(), classification.value]
        assets.append(asset)
        
        class_icons = {
            DataClassification.PUBLIC: "🟢",
            DataClassification.INTERNAL: "🔵",
            DataClassification.CONFIDENTIAL: "🟡",
            DataClassification.RESTRICTED: "🔴",
            DataClassification.PII: "🟣"
        }
        print(f"  {class_icons[classification]} {name}: {source}/{db}.{table}")
        
    # Add columns
    print("\n📋 Adding Columns...")
    
    columns_config = [
        (assets[0].asset_id, [("id", "BIGINT", False), ("email", "VARCHAR", True), ("name", "VARCHAR", True), ("phone", "VARCHAR", True)]),
        (assets[1].asset_id, [("id", "BIGINT", False), ("user_id", "BIGINT", False), ("total", "DECIMAL", False), ("status", "VARCHAR", False)]),
        (assets[3].asset_id, [("id", "BIGINT", False), ("card_last4", "VARCHAR", True), ("amount", "DECIMAL", False)]),
    ]
    
    total_cols = 0
    for asset_id, cols in columns_config:
        for name, dtype, is_pii in cols:
            platform.catalog.add_column(asset_id, name, dtype, is_pii)
            total_cols += 1
            
    print(f"  ✓ Added {total_cols} columns to assets")
    
    # Add lineage
    print("\n🔗 Adding Data Lineage...")
    
    lineages = [
        (assets[0].asset_id, assets[5].asset_id, "ETL: users -> dim_users", "user_etl"),
        (assets[1].asset_id, assets[6].asset_id, "ETL: orders -> fact_orders", "orders_etl"),
        (assets[4].asset_id, assets[6].asset_id, "Stream: events -> fact_orders", "event_processor"),
        (assets[5].asset_id, assets[7].asset_id, "Report: dim_users -> reports", "report_generator"),
        (assets[6].asset_id, assets[7].asset_id, "Report: fact_orders -> reports", "report_generator"),
    ]
    
    for source_id, target_id, transform, pipeline in lineages:
        platform.add_lineage(source_id, target_id, transform, pipeline)
        source = platform.catalog.assets[source_id]
        target = platform.catalog.assets[target_id]
        print(f"  ✓ {source.name} -> {target.name}")
        
    # Create quality rules
    print("\n✅ Creating Quality Rules...")
    
    rules_config = [
        ("Users Completeness", assets[0].asset_id, QualityDimension.COMPLETENESS),
        ("Orders Accuracy", assets[1].asset_id, QualityDimension.ACCURACY),
        ("Payments Uniqueness", assets[3].asset_id, QualityDimension.UNIQUENESS),
        ("Events Timeliness", assets[4].asset_id, QualityDimension.TIMELINESS),
        ("Analytics Consistency", assets[5].asset_id, QualityDimension.CONSISTENCY),
    ]
    
    for name, asset_id, dimension in rules_config:
        rule = platform.create_quality_rule(name, asset_id, dimension, 95.0)
        print(f"  ✓ {name} ({dimension.value})")
        
    # Run quality checks
    print("\n🔍 Running Quality Checks...")
    
    results = platform.run_quality_checks()
    
    for result in results:
        rule = platform.quality.rules[result.rule_id]
        status = "✓ PASS" if result.passed else "✗ FAIL"
        print(f"  {status} {rule.name}: {result.score:.1f}%")
        
    # Create access policies
    print("\n🔐 Creating Access Policies...")
    
    policies_config = [
        ("Users Access", assets[0].asset_id, ["admin", "data_engineer"], True),
        ("Orders Access", assets[1].asset_id, ["admin", "data_engineer", "analyst"], False),
        ("Payments Access", assets[3].asset_id, ["admin", "compliance"], True),
    ]
    
    for name, asset_id, roles, approval in policies_config:
        policy = platform.create_access_policy(name, asset_id, roles, approval)
        approval_str = "(requires approval)" if approval else ""
        print(f"  ✓ {name}: {', '.join(roles)} {approval_str}")
        
    # Create retention policies
    print("\n📅 Creating Retention Policies...")
    
    retention_config = [
        ("PII Data", DataClassification.PII, 365),
        ("Confidential Data", DataClassification.CONFIDENTIAL, 730),
        ("Internal Data", DataClassification.INTERNAL, 1095),
        ("Restricted Data", DataClassification.RESTRICTED, 2555),
    ]
    
    for name, classification, days in retention_config:
        policy = platform.create_retention_policy(name, classification, days)
        print(f"  ✓ {name}: {days} days")
        
    # Display catalog
    print("\n📋 Data Catalog:")
    
    print("\n  ┌────────────────────┬────────────────┬───────────────┬──────────┐")
    print("  │ Asset              │ Source         │ Classification│ Rows     │")
    print("  ├────────────────────┼────────────────┼───────────────┼──────────┤")
    
    for asset in platform.catalog.assets.values():
        name = asset.name[:18].ljust(18)
        source = asset.source_system[:14].ljust(14)
        classif = asset.classification.value[:13].ljust(13)
        rows = f"{asset.row_count:,}"[:8].ljust(8)
        
        print(f"  │ {name} │ {source} │ {classif} │ {rows} │")
        
    print("  └────────────────────┴────────────────┴───────────────┴──────────┘")
    
    # Lineage graph
    print("\n🔗 Data Lineage Graph:")
    
    for asset in assets[:5]:
        downstream = platform.lineage.get_downstream(asset.asset_id)
        if downstream:
            targets = [platform.catalog.assets[d].name for d in downstream 
                      if d in platform.catalog.assets]
            if targets:
                print(f"  {asset.name} -> [{', '.join(targets)}]")
                
    # Classification distribution
    print("\n📊 Assets by Classification:")
    
    stats = platform.get_statistics()
    
    class_icons = {
        "public": "🟢",
        "internal": "🔵",
        "confidential": "🟡",
        "restricted": "🔴",
        "pii": "🟣"
    }
    
    for classif, count in stats["by_classification"].items():
        icon = class_icons.get(classif, "⚪")
        bar = "█" * count + "░" * (5 - count)
        print(f"  {icon} {classif:13s} [{bar}] {count}")
        
    # Quality summary
    print("\n✅ Quality Summary:")
    
    passed = stats["quality_checks_passed"]
    total = stats["quality_checks_total"]
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"  Rules: {stats['quality_rules']}")
    print(f"  Passed: {passed}/{total} ({pass_rate:.0f}%)")
    
    # PII columns
    print("\n🟣 PII Columns Detected:")
    
    for asset_id, columns in platform.catalog.columns.items():
        pii_cols = [c for c in columns if c.is_pii]
        if pii_cols:
            asset = platform.catalog.assets[asset_id]
            cols = ", ".join(c.name for c in pii_cols)
            print(f"  {asset.name}: {cols}")
            
    # Audit log
    print("\n📝 Recent Audit Entries:")
    
    for entry in platform.audit_log[-5:]:
        asset = platform.catalog.assets.get(entry.asset_id)
        asset_name = asset.name if asset else "unknown"
        time_str = entry.timestamp.strftime("%H:%M:%S")
        print(f"  [{time_str}] {entry.action}: {asset_name} - {entry.user}")
        
    # Statistics
    print("\n📈 Platform Statistics:")
    
    print(f"\n  Total Assets: {stats['total_assets']}")
    print(f"  Total Columns: {stats['total_columns']}")
    print(f"  PII Columns: {stats['pii_columns']}")
    print(f"  Lineage Edges: {stats['lineage_edges']}")
    print(f"  Access Policies: {stats['access_policies']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                     Data Governance Dashboard                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Data Assets:             {stats['total_assets']:>12}                        │")
    print(f"│ PII Columns:                   {stats['pii_columns']:>12}                        │")
    print(f"│ Lineage Connections:           {stats['lineage_edges']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Quality Rules:                 {stats['quality_rules']:>12}                        │")
    print(f"│ Pass Rate:                       {pass_rate:>10.0f}%                       │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Data Governance Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
