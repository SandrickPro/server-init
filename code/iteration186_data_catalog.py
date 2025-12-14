#!/usr/bin/env python3
"""
Server Init - Iteration 186: Data Catalog Platform
Платформа каталога данных

Функционал:
- Metadata Management - управление метаданными
- Data Discovery - обнаружение данных
- Schema Registry - реестр схем
- Data Classification - классификация данных
- Search & Browse - поиск и навигация
- Data Quality Metrics - метрики качества
- Ownership Tracking - отслеживание владельцев
- Glossary Management - управление глоссарием
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid


class AssetType(Enum):
    """Тип актива"""
    DATABASE = "database"
    SCHEMA = "schema"
    TABLE = "table"
    VIEW = "view"
    COLUMN = "column"
    FILE = "file"
    DASHBOARD = "dashboard"
    REPORT = "report"
    PIPELINE = "pipeline"
    MODEL = "model"


class DataClassification(Enum):
    """Классификация данных"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    PII = "pii"
    PHI = "phi"
    PCI = "pci"


class DataType(Enum):
    """Тип данных"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    TIMESTAMP = "timestamp"
    ARRAY = "array"
    JSON = "json"
    BINARY = "binary"


class QualityStatus(Enum):
    """Статус качества"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNKNOWN = "unknown"


@dataclass
class Tag:
    """Тег"""
    tag_id: str
    name: str = ""
    description: str = ""
    color: str = "#3498db"
    category: str = ""  # domain, sensitivity, status, etc.


@dataclass
class GlossaryTerm:
    """Термин глоссария"""
    term_id: str
    name: str = ""
    definition: str = ""
    
    # Related
    synonyms: List[str] = field(default_factory=list)
    related_terms: List[str] = field(default_factory=list)
    
    # Classification
    domain: str = ""
    
    # Ownership
    owner: str = ""
    steward: str = ""
    
    # Status
    approved: bool = False


@dataclass
class DataAsset:
    """Актив данных"""
    asset_id: str
    name: str = ""
    description: str = ""
    
    # Type
    asset_type: AssetType = AssetType.TABLE
    
    # Location
    source_system: str = ""
    database: str = ""
    schema_name: str = ""
    path: str = ""
    
    # Classification
    classification: DataClassification = DataClassification.INTERNAL
    
    # Tags
    tags: List[str] = field(default_factory=list)  # tag_ids
    
    # Ownership
    owner: str = ""
    steward: str = ""
    team: str = ""
    
    # Quality
    quality_score: float = 0.0
    quality_status: QualityStatus = QualityStatus.UNKNOWN
    
    # Stats
    row_count: int = 0
    size_bytes: int = 0
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_accessed_at: Optional[datetime] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Column:
    """Колонка"""
    column_id: str
    name: str = ""
    description: str = ""
    
    # Parent
    table_asset_id: str = ""
    
    # Type
    data_type: DataType = DataType.STRING
    nullable: bool = True
    
    # Classification
    classification: DataClassification = DataClassification.INTERNAL
    is_pii: bool = False
    
    # Constraints
    is_primary_key: bool = False
    is_foreign_key: bool = False
    
    # Stats
    null_count: int = 0
    distinct_count: int = 0
    
    # Glossary
    glossary_term_id: Optional[str] = None


@dataclass
class Schema:
    """Схема данных"""
    schema_id: str
    name: str = ""
    version: str = "1.0.0"
    
    # Asset
    asset_id: str = ""
    
    # Columns
    columns: List[Column] = field(default_factory=list)
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    
    # Evolution
    previous_version: Optional[str] = None


@dataclass
class QualityMetrics:
    """Метрики качества"""
    metrics_id: str
    asset_id: str = ""
    
    # Scores (0-100)
    completeness: float = 0.0
    accuracy: float = 0.0
    consistency: float = 0.0
    timeliness: float = 0.0
    uniqueness: float = 0.0
    
    # Overall
    overall_score: float = 0.0
    
    # Issues
    issues_count: int = 0
    
    # Timing
    measured_at: datetime = field(default_factory=datetime.now)


class MetadataStore:
    """Хранилище метаданных"""
    
    def __init__(self):
        self.assets: Dict[str, DataAsset] = {}
        self.columns: Dict[str, List[Column]] = {}  # asset_id -> columns
        self.schemas: Dict[str, Schema] = {}
        
    def add_asset(self, asset: DataAsset):
        """Добавление актива"""
        self.assets[asset.asset_id] = asset
        
    def add_columns(self, asset_id: str, columns: List[Column]):
        """Добавление колонок"""
        self.columns[asset_id] = columns
        
    def get_asset(self, asset_id: str) -> Optional[DataAsset]:
        """Получение актива"""
        return self.assets.get(asset_id)
        
    def search(self, query: str) -> List[DataAsset]:
        """Поиск активов"""
        query_lower = query.lower()
        return [
            asset for asset in self.assets.values()
            if query_lower in asset.name.lower() or
               query_lower in asset.description.lower()
        ]


class TagManager:
    """Менеджер тегов"""
    
    def __init__(self):
        self.tags: Dict[str, Tag] = {}
        
    def create_tag(self, name: str, description: str = "", 
                  category: str = "", color: str = "#3498db") -> Tag:
        """Создание тега"""
        tag = Tag(
            tag_id=f"tag_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            category=category,
            color=color
        )
        self.tags[tag.tag_id] = tag
        return tag
        
    def get_tags_by_category(self, category: str) -> List[Tag]:
        """Получение тегов по категории"""
        return [t for t in self.tags.values() if t.category == category]


class GlossaryManager:
    """Менеджер глоссария"""
    
    def __init__(self):
        self.terms: Dict[str, GlossaryTerm] = {}
        
    def add_term(self, term: GlossaryTerm):
        """Добавление термина"""
        self.terms[term.term_id] = term
        
    def search_terms(self, query: str) -> List[GlossaryTerm]:
        """Поиск терминов"""
        query_lower = query.lower()
        results = []
        
        for term in self.terms.values():
            if query_lower in term.name.lower() or \
               query_lower in term.definition.lower() or \
               any(query_lower in syn.lower() for syn in term.synonyms):
                results.append(term)
                
        return results
        
    def get_terms_by_domain(self, domain: str) -> List[GlossaryTerm]:
        """Получение терминов по домену"""
        return [t for t in self.terms.values() if t.domain == domain]


class QualityAnalyzer:
    """Анализатор качества"""
    
    def __init__(self, metadata_store: MetadataStore):
        self.metadata_store = metadata_store
        self.metrics: Dict[str, QualityMetrics] = {}
        
    def analyze(self, asset_id: str) -> QualityMetrics:
        """Анализ качества"""
        # Simulate quality metrics
        metrics = QualityMetrics(
            metrics_id=f"metrics_{uuid.uuid4().hex[:8]}",
            asset_id=asset_id,
            completeness=random.uniform(80, 100),
            accuracy=random.uniform(85, 100),
            consistency=random.uniform(75, 100),
            timeliness=random.uniform(70, 100),
            uniqueness=random.uniform(90, 100)
        )
        
        metrics.overall_score = (
            metrics.completeness * 0.25 +
            metrics.accuracy * 0.25 +
            metrics.consistency * 0.2 +
            metrics.timeliness * 0.15 +
            metrics.uniqueness * 0.15
        )
        
        metrics.issues_count = int((100 - metrics.overall_score) / 5)
        
        self.metrics[asset_id] = metrics
        
        # Update asset quality
        asset = self.metadata_store.get_asset(asset_id)
        if asset:
            asset.quality_score = metrics.overall_score
            if metrics.overall_score >= 90:
                asset.quality_status = QualityStatus.EXCELLENT
            elif metrics.overall_score >= 75:
                asset.quality_status = QualityStatus.GOOD
            elif metrics.overall_score >= 50:
                asset.quality_status = QualityStatus.FAIR
            else:
                asset.quality_status = QualityStatus.POOR
                
        return metrics


class DataDiscovery:
    """Обнаружение данных"""
    
    def __init__(self, metadata_store: MetadataStore):
        self.metadata_store = metadata_store
        
    def discover_pii(self) -> List[DataAsset]:
        """Обнаружение PII данных"""
        return [
            asset for asset in self.metadata_store.assets.values()
            if asset.classification in [DataClassification.PII, DataClassification.PHI]
        ]
        
    def discover_by_owner(self, owner: str) -> List[DataAsset]:
        """Обнаружение по владельцу"""
        return [
            asset for asset in self.metadata_store.assets.values()
            if asset.owner == owner
        ]
        
    def discover_stale(self, days: int = 30) -> List[DataAsset]:
        """Обнаружение устаревших данных"""
        threshold = datetime.now() - timedelta(days=days)
        return [
            asset for asset in self.metadata_store.assets.values()
            if asset.last_accessed_at and asset.last_accessed_at < threshold
        ]


class DataCatalogPlatform:
    """Платформа каталога данных"""
    
    def __init__(self):
        self.metadata_store = MetadataStore()
        self.tag_manager = TagManager()
        self.glossary_manager = GlossaryManager()
        self.quality_analyzer = QualityAnalyzer(self.metadata_store)
        self.discovery = DataDiscovery(self.metadata_store)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        assets = list(self.metadata_store.assets.values())
        
        return {
            "total_assets": len(assets),
            "by_type": {
                at.value: len([a for a in assets if a.asset_type == at])
                for at in AssetType
            },
            "by_classification": {
                dc.value: len([a for a in assets if a.classification == dc])
                for dc in DataClassification if len([a for a in assets if a.classification == dc]) > 0
            },
            "total_tags": len(self.tag_manager.tags),
            "total_terms": len(self.glossary_manager.terms),
            "avg_quality_score": sum(a.quality_score for a in assets) / len(assets) if assets else 0
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 186: Data Catalog Platform")
    print("=" * 60)
    
    platform = DataCatalogPlatform()
    print("✓ Data Catalog Platform created")
    
    # Create tags
    print("\n🏷️ Creating Tags...")
    
    tags = [
        platform.tag_manager.create_tag("customer-data", "Customer related data", "domain", "#e74c3c"),
        platform.tag_manager.create_tag("financial", "Financial data", "domain", "#2ecc71"),
        platform.tag_manager.create_tag("marketing", "Marketing data", "domain", "#3498db"),
        platform.tag_manager.create_tag("sensitive", "Sensitive data", "sensitivity", "#e67e22"),
        platform.tag_manager.create_tag("deprecated", "Deprecated asset", "status", "#95a5a6"),
        platform.tag_manager.create_tag("verified", "Verified quality", "status", "#27ae60"),
    ]
    
    for tag in tags:
        print(f"  ✓ {tag.name} ({tag.category})")
        
    # Create glossary terms
    print("\n📖 Creating Glossary Terms...")
    
    terms = [
        GlossaryTerm(
            term_id="term_customer",
            name="Customer",
            definition="An individual or organization that purchases goods or services",
            synonyms=["client", "buyer", "consumer"],
            domain="sales",
            owner="data-team"
        ),
        GlossaryTerm(
            term_id="term_mrr",
            name="MRR",
            definition="Monthly Recurring Revenue - predictable revenue normalized to one month",
            synonyms=["monthly revenue", "recurring revenue"],
            domain="finance",
            owner="finance-team"
        ),
        GlossaryTerm(
            term_id="term_churn",
            name="Churn Rate",
            definition="Percentage of customers who stop using service during a period",
            synonyms=["attrition rate", "turnover rate"],
            domain="metrics",
            owner="analytics-team"
        ),
    ]
    
    for term in terms:
        platform.glossary_manager.add_term(term)
        print(f"  ✓ {term.name}: {term.definition[:50]}...")
        
    # Create data assets
    print("\n📊 Creating Data Assets...")
    
    assets = [
        DataAsset(
            asset_id="asset_customers",
            name="customers",
            description="Master customer data table containing all customer information",
            asset_type=AssetType.TABLE,
            source_system="PostgreSQL",
            database="production",
            schema_name="public",
            classification=DataClassification.PII,
            tags=["tag_customer-data", "tag_sensitive"],
            owner="data-team",
            steward="john.doe",
            row_count=1500000,
            size_bytes=512000000,
            last_accessed_at=datetime.now() - timedelta(hours=2)
        ),
        DataAsset(
            asset_id="asset_orders",
            name="orders",
            description="All customer orders with order details",
            asset_type=AssetType.TABLE,
            source_system="PostgreSQL",
            database="production",
            schema_name="public",
            classification=DataClassification.CONFIDENTIAL,
            tags=["tag_financial"],
            owner="data-team",
            row_count=5000000,
            size_bytes=2048000000,
            last_accessed_at=datetime.now() - timedelta(minutes=30)
        ),
        DataAsset(
            asset_id="asset_products",
            name="products",
            description="Product catalog with pricing and inventory",
            asset_type=AssetType.TABLE,
            source_system="PostgreSQL",
            database="production",
            schema_name="public",
            classification=DataClassification.INTERNAL,
            owner="product-team",
            row_count=50000,
            size_bytes=25000000,
            last_accessed_at=datetime.now() - timedelta(days=45)
        ),
        DataAsset(
            asset_id="asset_sales_dashboard",
            name="Sales Dashboard",
            description="Executive sales dashboard with KPIs",
            asset_type=AssetType.DASHBOARD,
            source_system="Tableau",
            classification=DataClassification.CONFIDENTIAL,
            tags=["tag_financial", "tag_verified"],
            owner="bi-team",
            last_accessed_at=datetime.now() - timedelta(hours=1)
        ),
        DataAsset(
            asset_id="asset_customer_360",
            name="customer_360",
            description="Aggregated customer view with all touchpoints",
            asset_type=AssetType.VIEW,
            source_system="Snowflake",
            database="analytics",
            schema_name="marts",
            classification=DataClassification.PII,
            tags=["tag_customer-data", "tag_marketing"],
            owner="analytics-team",
            row_count=1500000,
            size_bytes=768000000,
            last_accessed_at=datetime.now() - timedelta(hours=4)
        ),
        DataAsset(
            asset_id="asset_churn_model",
            name="churn_prediction_model",
            description="ML model for predicting customer churn",
            asset_type=AssetType.MODEL,
            source_system="MLflow",
            classification=DataClassification.INTERNAL,
            owner="ml-team",
            last_accessed_at=datetime.now() - timedelta(days=7)
        ),
    ]
    
    for asset in assets:
        platform.metadata_store.add_asset(asset)
        print(f"  ✓ {asset.name} ({asset.asset_type.value})")
        
    # Add columns
    print("\n📋 Adding Column Metadata...")
    
    customer_columns = [
        Column(column_id="col_1", name="customer_id", data_type=DataType.INTEGER, is_primary_key=True),
        Column(column_id="col_2", name="email", data_type=DataType.STRING, is_pii=True, classification=DataClassification.PII),
        Column(column_id="col_3", name="name", data_type=DataType.STRING, is_pii=True, classification=DataClassification.PII),
        Column(column_id="col_4", name="phone", data_type=DataType.STRING, is_pii=True, classification=DataClassification.PII),
        Column(column_id="col_5", name="created_at", data_type=DataType.TIMESTAMP),
        Column(column_id="col_6", name="segment", data_type=DataType.STRING),
    ]
    
    platform.metadata_store.add_columns("asset_customers", customer_columns)
    print(f"  customers: {len(customer_columns)} columns")
    
    # Analyze quality
    print("\n🔍 Analyzing Data Quality...")
    
    for asset in assets[:4]:
        metrics = platform.quality_analyzer.analyze(asset.asset_id)
        status_icon = "🟢" if asset.quality_status == QualityStatus.EXCELLENT else ("🟡" if asset.quality_status == QualityStatus.GOOD else "🔴")
        print(f"  {status_icon} {asset.name}: {metrics.overall_score:.1f}%")
        
    # Show asset catalog
    print("\n📚 Data Catalog:")
    
    print("\n  ┌────────────────────────┬────────────┬────────────────┬─────────────────┬──────────┐")
    print("  │ Asset                  │ Type       │ Classification │ Owner           │ Quality  │")
    print("  ├────────────────────────┼────────────┼────────────────┼─────────────────┼──────────┤")
    
    for asset in assets:
        name = asset.name[:22].ljust(22)
        atype = asset.asset_type.value[:10].ljust(10)
        classification = asset.classification.value[:14].ljust(14)
        owner = asset.owner[:15].ljust(15)
        quality = f"{asset.quality_score:.0f}%".rjust(8) if asset.quality_score > 0 else "N/A".rjust(8)
        print(f"  │ {name} │ {atype} │ {classification} │ {owner} │ {quality} │")
        
    print("  └────────────────────────┴────────────┴────────────────┴─────────────────┴──────────┘")
    
    # Search
    print("\n🔎 Search Results for 'customer':")
    
    results = platform.metadata_store.search("customer")
    for asset in results:
        print(f"  • {asset.name} - {asset.description[:50]}...")
        
    # PII Discovery
    print("\n🔒 PII Data Discovery:")
    
    pii_assets = platform.discovery.discover_pii()
    for asset in pii_assets:
        print(f"  ⚠️ {asset.name} ({asset.asset_type.value})")
        
    # Stale assets
    print("\n📅 Stale Assets (>30 days):")
    
    stale = platform.discovery.discover_stale(30)
    for asset in stale:
        days = (datetime.now() - asset.last_accessed_at).days if asset.last_accessed_at else "Never"
        print(f"  • {asset.name}: Last accessed {days} days ago")
        
    # Column details
    print("\n📊 Column Details (customers):")
    
    cols = platform.metadata_store.columns.get("asset_customers", [])
    
    print("\n  ┌────────────────┬────────────┬──────────┬─────────┬───────┐")
    print("  │ Column         │ Type       │ PII      │ PK      │ FK    │")
    print("  ├────────────────┼────────────┼──────────┼─────────┼───────┤")
    
    for col in cols:
        name = col.name[:14].ljust(14)
        dtype = col.data_type.value[:10].ljust(10)
        pii = "Yes" if col.is_pii else "No"
        pk = "Yes" if col.is_primary_key else "No"
        fk = "Yes" if col.is_foreign_key else "No"
        print(f"  │ {name} │ {dtype} │ {pii:^8} │ {pk:^7} │ {fk:^5} │")
        
    print("  └────────────────┴────────────┴──────────┴─────────┴───────┘")
    
    # Quality metrics
    print("\n📈 Quality Metrics (customers):")
    
    metrics = platform.quality_analyzer.metrics.get("asset_customers")
    if metrics:
        print(f"\n  Completeness:  {'█' * int(metrics.completeness/5)}{'░' * (20-int(metrics.completeness/5))} {metrics.completeness:.1f}%")
        print(f"  Accuracy:      {'█' * int(metrics.accuracy/5)}{'░' * (20-int(metrics.accuracy/5))} {metrics.accuracy:.1f}%")
        print(f"  Consistency:   {'█' * int(metrics.consistency/5)}{'░' * (20-int(metrics.consistency/5))} {metrics.consistency:.1f}%")
        print(f"  Timeliness:    {'█' * int(metrics.timeliness/5)}{'░' * (20-int(metrics.timeliness/5))} {metrics.timeliness:.1f}%")
        print(f"  Uniqueness:    {'█' * int(metrics.uniqueness/5)}{'░' * (20-int(metrics.uniqueness/5))} {metrics.uniqueness:.1f}%")
        print(f"\n  Overall Score: {metrics.overall_score:.1f}%")
        
    # Platform statistics
    print("\n📊 Platform Statistics:")
    
    stats = platform.get_statistics()
    
    print(f"\n  Total Assets: {stats['total_assets']}")
    print(f"  Total Tags: {stats['total_tags']}")
    print(f"  Glossary Terms: {stats['total_terms']}")
    print(f"  Avg Quality: {stats['avg_quality_score']:.1f}%")
    
    print("\n  By Type:")
    for atype, count in stats['by_type'].items():
        if count > 0:
            print(f"    • {atype}: {count}")
            
    print("\n  By Classification:")
    for classification, count in stats['by_classification'].items():
        print(f"    • {classification}: {count}")
        
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                      Data Catalog Dashboard                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Assets:                  {stats['total_assets']:>10}                     │")
    print(f"│ Total Tags:                    {stats['total_tags']:>10}                     │")
    print(f"│ Glossary Terms:                {stats['total_terms']:>10}                     │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Tables:                        {stats['by_type'].get('table', 0):>10}                     │")
    print(f"│ Views:                         {stats['by_type'].get('view', 0):>10}                     │")
    print(f"│ Dashboards:                    {stats['by_type'].get('dashboard', 0):>10}                     │")
    print(f"│ Average Quality:                 {stats['avg_quality_score']:>8.1f}%                   │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Data Catalog Platform initialized!")
    print("=" * 60)
