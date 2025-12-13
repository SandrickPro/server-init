#!/usr/bin/env python3
"""
Server Init - Iteration 86: Asset Management Platform
Платформа управления активами

Функционал:
- Asset Discovery - обнаружение активов
- Asset Inventory - инвентаризация активов
- Lifecycle Management - управление жизненным циклом
- Asset Relationships - связи между активами
- Asset Tracking - отслеживание активов
- Compliance Tracking - отслеживание соответствия
- Asset Depreciation - амортизация активов
- Asset Reports - отчёты по активам
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Tuple
from enum import Enum
from collections import defaultdict
import uuid
import random


class AssetType(Enum):
    """Тип актива"""
    SERVER = "server"
    VIRTUAL_MACHINE = "virtual_machine"
    CONTAINER = "container"
    DATABASE = "database"
    STORAGE = "storage"
    NETWORK_DEVICE = "network_device"
    LOAD_BALANCER = "load_balancer"
    LICENSE = "license"
    SOFTWARE = "software"
    CERTIFICATE = "certificate"
    CLOUD_RESOURCE = "cloud_resource"


class AssetStatus(Enum):
    """Статус актива"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DECOMMISSIONED = "decommissioned"
    PENDING = "pending"
    UNKNOWN = "unknown"


class LifecyclePhase(Enum):
    """Фаза жизненного цикла"""
    PROCUREMENT = "procurement"
    DEPLOYMENT = "deployment"
    PRODUCTION = "production"
    MAINTENANCE = "maintenance"
    END_OF_LIFE = "end_of_life"
    DECOMMISSIONED = "decommissioned"


class RelationshipType(Enum):
    """Тип связи"""
    RUNS_ON = "runs_on"
    DEPENDS_ON = "depends_on"
    CONTAINS = "contains"
    CONNECTS_TO = "connects_to"
    MANAGED_BY = "managed_by"
    LICENSED_BY = "licensed_by"


class ComplianceStatus(Enum):
    """Статус соответствия"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    EXEMPT = "exempt"


@dataclass
class AssetLocation:
    """Расположение актива"""
    datacenter: str = ""
    region: str = ""
    zone: str = ""
    rack: str = ""
    unit: str = ""
    cloud_provider: str = ""
    cloud_account: str = ""


@dataclass
class AssetFinancials:
    """Финансовая информация актива"""
    purchase_cost: float = 0.0
    current_value: float = 0.0
    monthly_cost: float = 0.0
    depreciation_rate: float = 0.0  # % в год
    purchase_date: Optional[datetime] = None
    warranty_end: Optional[datetime] = None
    vendor: str = ""
    contract_id: str = ""


@dataclass
class AssetSpecs:
    """Спецификации актива"""
    cpu_cores: int = 0
    memory_gb: float = 0.0
    storage_gb: float = 0.0
    os: str = ""
    os_version: str = ""
    architecture: str = ""
    custom_specs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Asset:
    """Актив"""
    asset_id: str
    name: str = ""
    description: str = ""
    
    # Тип и статус
    asset_type: AssetType = AssetType.SERVER
    status: AssetStatus = AssetStatus.ACTIVE
    lifecycle_phase: LifecyclePhase = LifecyclePhase.PRODUCTION
    
    # Идентификаторы
    serial_number: str = ""
    hostname: str = ""
    ip_addresses: List[str] = field(default_factory=list)
    mac_addresses: List[str] = field(default_factory=list)
    
    # Расположение
    location: Optional[AssetLocation] = None
    
    # Финансы
    financials: Optional[AssetFinancials] = None
    
    # Спецификации
    specs: Optional[AssetSpecs] = None
    
    # Владелец
    owner: str = ""
    team: str = ""
    environment: str = ""  # production, staging, dev
    
    # Теги
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Compliance
    compliance_status: ComplianceStatus = ComplianceStatus.PENDING_REVIEW
    compliance_frameworks: List[str] = field(default_factory=list)  # SOC2, ISO27001, etc.
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    end_of_life_date: Optional[datetime] = None


@dataclass
class AssetRelationship:
    """Связь между активами"""
    relationship_id: str
    source_asset_id: str = ""
    target_asset_id: str = ""
    relationship_type: RelationshipType = RelationshipType.DEPENDS_ON
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ComplianceCheck:
    """Проверка соответствия"""
    check_id: str
    asset_id: str = ""
    
    # Фреймворк
    framework: str = ""  # SOC2, ISO27001, PCI-DSS
    control_id: str = ""  # Например, CC6.1
    
    # Результат
    status: ComplianceStatus = ComplianceStatus.PENDING_REVIEW
    findings: List[str] = field(default_factory=list)
    remediation: str = ""
    
    # Время
    checked_at: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None


@dataclass
class LifecycleEvent:
    """Событие жизненного цикла"""
    event_id: str
    asset_id: str = ""
    
    # Переход
    from_phase: LifecyclePhase = LifecyclePhase.PROCUREMENT
    to_phase: LifecyclePhase = LifecyclePhase.DEPLOYMENT
    
    # Детали
    reason: str = ""
    performed_by: str = ""
    notes: str = ""
    
    # Время
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DiscoveredAsset:
    """Обнаруженный актив"""
    discovery_id: str
    
    # Данные обнаружения
    hostname: str = ""
    ip_address: str = ""
    mac_address: str = ""
    
    # Тип
    detected_type: AssetType = AssetType.SERVER
    
    # Сопоставление
    matched_asset_id: Optional[str] = None
    is_new: bool = True
    
    # Источник
    discovery_source: str = ""  # network_scan, cloud_api, agent
    
    # Время
    discovered_at: datetime = field(default_factory=datetime.now)


class AssetDiscovery:
    """Обнаружение активов"""
    
    def __init__(self):
        self.discovered: List[DiscoveredAsset] = []
        self.sources: List[str] = []
        
    def scan_network(self, subnet: str) -> List[DiscoveredAsset]:
        """Сканирование сети (симуляция)"""
        results = []
        
        # Симуляция обнаружения
        num_devices = random.randint(5, 15)
        
        for i in range(num_devices):
            discovered = DiscoveredAsset(
                discovery_id=f"disc_{uuid.uuid4().hex[:8]}",
                hostname=f"device-{i:03d}.local",
                ip_address=f"10.0.1.{100 + i}",
                mac_address=f"00:1A:2B:3C:4D:{i:02X}",
                detected_type=random.choice(list(AssetType)[:6]),
                discovery_source="network_scan"
            )
            results.append(discovered)
            self.discovered.append(discovered)
            
        return results
        
    def scan_cloud(self, provider: str, account: str) -> List[DiscoveredAsset]:
        """Сканирование облака (симуляция)"""
        results = []
        
        # Симуляция облачных ресурсов
        cloud_resources = [
            ("web-server-001", AssetType.VIRTUAL_MACHINE),
            ("api-server-001", AssetType.VIRTUAL_MACHINE),
            ("db-primary", AssetType.DATABASE),
            ("cache-cluster", AssetType.CLOUD_RESOURCE),
            ("storage-bucket", AssetType.STORAGE),
            ("load-balancer", AssetType.LOAD_BALANCER),
        ]
        
        for name, asset_type in cloud_resources:
            discovered = DiscoveredAsset(
                discovery_id=f"disc_{uuid.uuid4().hex[:8]}",
                hostname=f"{name}.{provider}",
                ip_address=f"172.16.{random.randint(1, 255)}.{random.randint(1, 255)}",
                detected_type=asset_type,
                discovery_source=f"cloud_api_{provider}"
            )
            results.append(discovered)
            self.discovered.append(discovered)
            
        return results
        
    def reconcile(self, existing_assets: Dict[str, Asset]) -> Dict[str, List[DiscoveredAsset]]:
        """Сверка обнаруженных активов с существующими"""
        result = {
            "new": [],
            "matched": [],
            "missing": []
        }
        
        existing_hostnames = {a.hostname: a.asset_id for a in existing_assets.values()}
        existing_ips = {}
        for a in existing_assets.values():
            for ip in a.ip_addresses:
                existing_ips[ip] = a.asset_id
                
        discovered_ips = set()
        
        for disc in self.discovered:
            discovered_ips.add(disc.ip_address)
            
            # Проверяем по hostname
            if disc.hostname in existing_hostnames:
                disc.matched_asset_id = existing_hostnames[disc.hostname]
                disc.is_new = False
                result["matched"].append(disc)
            # Проверяем по IP
            elif disc.ip_address in existing_ips:
                disc.matched_asset_id = existing_ips[disc.ip_address]
                disc.is_new = False
                result["matched"].append(disc)
            else:
                result["new"].append(disc)
                
        # Проверяем пропавшие активы
        for asset in existing_assets.values():
            if asset.status == AssetStatus.ACTIVE:
                found = any(ip in discovered_ips for ip in asset.ip_addresses)
                if not found and asset.ip_addresses:
                    result["missing"].append(asset)
                    
        return result


class LifecycleManager:
    """Менеджер жизненного цикла"""
    
    def __init__(self):
        self.events: List[LifecycleEvent] = []
        
        # Допустимые переходы
        self.transitions = {
            LifecyclePhase.PROCUREMENT: [LifecyclePhase.DEPLOYMENT],
            LifecyclePhase.DEPLOYMENT: [LifecyclePhase.PRODUCTION, LifecyclePhase.DECOMMISSIONED],
            LifecyclePhase.PRODUCTION: [LifecyclePhase.MAINTENANCE, LifecyclePhase.END_OF_LIFE],
            LifecyclePhase.MAINTENANCE: [LifecyclePhase.PRODUCTION, LifecyclePhase.END_OF_LIFE],
            LifecyclePhase.END_OF_LIFE: [LifecyclePhase.DECOMMISSIONED],
            LifecyclePhase.DECOMMISSIONED: []
        }
        
    def can_transition(self, from_phase: LifecyclePhase, to_phase: LifecyclePhase) -> bool:
        """Проверка допустимости перехода"""
        allowed = self.transitions.get(from_phase, [])
        return to_phase in allowed
        
    def transition(self, asset: Asset, to_phase: LifecyclePhase,
                    reason: str = "", performed_by: str = "") -> LifecycleEvent:
        """Переход жизненного цикла"""
        if not self.can_transition(asset.lifecycle_phase, to_phase):
            raise ValueError(
                f"Invalid transition from {asset.lifecycle_phase.value} to {to_phase.value}"
            )
            
        event = LifecycleEvent(
            event_id=f"lce_{uuid.uuid4().hex[:8]}",
            asset_id=asset.asset_id,
            from_phase=asset.lifecycle_phase,
            to_phase=to_phase,
            reason=reason,
            performed_by=performed_by
        )
        
        asset.lifecycle_phase = to_phase
        asset.updated_at = datetime.now()
        
        # Обновляем статус в зависимости от фазы
        if to_phase == LifecyclePhase.DECOMMISSIONED:
            asset.status = AssetStatus.DECOMMISSIONED
        elif to_phase == LifecyclePhase.MAINTENANCE:
            asset.status = AssetStatus.MAINTENANCE
        elif to_phase == LifecyclePhase.PRODUCTION:
            asset.status = AssetStatus.ACTIVE
            
        self.events.append(event)
        return event
        
    def get_history(self, asset_id: str) -> List[LifecycleEvent]:
        """История жизненного цикла"""
        return [e for e in self.events if e.asset_id == asset_id]


class ComplianceManager:
    """Менеджер соответствия"""
    
    def __init__(self):
        self.checks: List[ComplianceCheck] = []
        
        # Правила проверки
        self.rules: Dict[str, List[Dict[str, Any]]] = {
            "SOC2": [
                {"control_id": "CC6.1", "check": "encryption_at_rest"},
                {"control_id": "CC6.7", "check": "access_controls"},
                {"control_id": "CC7.2", "check": "monitoring_enabled"}
            ],
            "ISO27001": [
                {"control_id": "A.8.2", "check": "asset_classification"},
                {"control_id": "A.12.4", "check": "logging_enabled"},
                {"control_id": "A.18.1", "check": "compliance_review"}
            ],
            "PCI-DSS": [
                {"control_id": "1.1", "check": "firewall_config"},
                {"control_id": "3.4", "check": "data_encryption"},
                {"control_id": "10.2", "check": "audit_logs"}
            ]
        }
        
    def check_asset(self, asset: Asset, framework: str) -> List[ComplianceCheck]:
        """Проверка актива на соответствие"""
        results = []
        
        rules = self.rules.get(framework, [])
        
        for rule in rules:
            check = ComplianceCheck(
                check_id=f"cc_{uuid.uuid4().hex[:8]}",
                asset_id=asset.asset_id,
                framework=framework,
                control_id=rule["control_id"]
            )
            
            # Симуляция проверки
            passed = random.random() > 0.2  # 80% проходят
            
            if passed:
                check.status = ComplianceStatus.COMPLIANT
            else:
                check.status = ComplianceStatus.NON_COMPLIANT
                check.findings.append(f"Control {rule['control_id']} not satisfied")
                check.remediation = f"Implement {rule['check']} for this asset"
                check.due_date = datetime.now() + timedelta(days=30)
                
            results.append(check)
            self.checks.append(check)
            
        # Обновляем статус актива
        if all(c.status == ComplianceStatus.COMPLIANT for c in results):
            asset.compliance_status = ComplianceStatus.COMPLIANT
        elif any(c.status == ComplianceStatus.NON_COMPLIANT for c in results):
            asset.compliance_status = ComplianceStatus.NON_COMPLIANT
            
        return results


class DepreciationCalculator:
    """Калькулятор амортизации"""
    
    def calculate_straight_line(self, asset: Asset) -> Dict[str, float]:
        """Линейная амортизация"""
        if not asset.financials or not asset.financials.purchase_date:
            return {"current_value": 0, "depreciation": 0, "remaining_life_years": 0}
            
        purchase_cost = asset.financials.purchase_cost
        rate = asset.financials.depreciation_rate / 100  # Конвертируем в десятичную
        
        years_owned = (datetime.now() - asset.financials.purchase_date).days / 365
        
        total_depreciation = purchase_cost * rate * years_owned
        current_value = max(0, purchase_cost - total_depreciation)
        
        # Остаточный срок службы
        if rate > 0:
            total_life = 1 / rate
            remaining_life = max(0, total_life - years_owned)
        else:
            remaining_life = float('inf')
            
        return {
            "purchase_cost": purchase_cost,
            "current_value": current_value,
            "total_depreciation": total_depreciation,
            "years_owned": years_owned,
            "remaining_life_years": remaining_life,
            "depreciation_rate": asset.financials.depreciation_rate
        }


class AssetManagementPlatform:
    """Платформа управления активами"""
    
    def __init__(self):
        self.assets: Dict[str, Asset] = {}
        self.relationships: List[AssetRelationship] = []
        
        self.discovery = AssetDiscovery()
        self.lifecycle_manager = LifecycleManager()
        self.compliance_manager = ComplianceManager()
        self.depreciation_calc = DepreciationCalculator()
        
    def create_asset(self, name: str, asset_type: AssetType,
                      **kwargs) -> Asset:
        """Создание актива"""
        asset = Asset(
            asset_id=f"AST{uuid.uuid4().hex[:8].upper()}",
            name=name,
            asset_type=asset_type,
            **kwargs
        )
        self.assets[asset.asset_id] = asset
        return asset
        
    def update_asset(self, asset_id: str, **kwargs) -> Asset:
        """Обновление актива"""
        asset = self.assets.get(asset_id)
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")
            
        for key, value in kwargs.items():
            if hasattr(asset, key):
                setattr(asset, key, value)
                
        asset.updated_at = datetime.now()
        return asset
        
    def add_relationship(self, source_id: str, target_id: str,
                          rel_type: RelationshipType, description: str = "") -> AssetRelationship:
        """Добавление связи"""
        if source_id not in self.assets or target_id not in self.assets:
            raise ValueError("Both assets must exist")
            
        relationship = AssetRelationship(
            relationship_id=f"rel_{uuid.uuid4().hex[:8]}",
            source_asset_id=source_id,
            target_asset_id=target_id,
            relationship_type=rel_type,
            description=description
        )
        self.relationships.append(relationship)
        return relationship
        
    def get_relationships(self, asset_id: str, 
                           direction: str = "both") -> List[AssetRelationship]:
        """Получение связей актива"""
        results = []
        
        for rel in self.relationships:
            if direction in ["both", "outgoing"] and rel.source_asset_id == asset_id:
                results.append(rel)
            if direction in ["both", "incoming"] and rel.target_asset_id == asset_id:
                results.append(rel)
                
        return results
        
    def get_dependency_tree(self, asset_id: str, depth: int = 3) -> Dict[str, Any]:
        """Дерево зависимостей"""
        asset = self.assets.get(asset_id)
        if not asset:
            return {}
            
        tree = {
            "asset_id": asset_id,
            "name": asset.name,
            "type": asset.asset_type.value,
            "dependencies": []
        }
        
        if depth > 0:
            rels = self.get_relationships(asset_id, "outgoing")
            for rel in rels:
                if rel.relationship_type == RelationshipType.DEPENDS_ON:
                    subtree = self.get_dependency_tree(rel.target_asset_id, depth - 1)
                    if subtree:
                        tree["dependencies"].append(subtree)
                        
        return tree
        
    def discover_assets(self) -> Dict[str, List[DiscoveredAsset]]:
        """Обнаружение активов"""
        # Сканируем сеть
        self.discovery.scan_network("10.0.1.0/24")
        
        # Сканируем облако
        self.discovery.scan_cloud("aws", "prod-account")
        
        # Сверяем с существующими
        return self.discovery.reconcile(self.assets)
        
    def transition_lifecycle(self, asset_id: str, to_phase: LifecyclePhase,
                              reason: str = "", by: str = "") -> LifecycleEvent:
        """Переход жизненного цикла"""
        asset = self.assets.get(asset_id)
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")
            
        return self.lifecycle_manager.transition(asset, to_phase, reason, by)
        
    def check_compliance(self, asset_id: str, framework: str) -> List[ComplianceCheck]:
        """Проверка соответствия"""
        asset = self.assets.get(asset_id)
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")
            
        return self.compliance_manager.check_asset(asset, framework)
        
    def calculate_depreciation(self, asset_id: str) -> Dict[str, float]:
        """Расчёт амортизации"""
        asset = self.assets.get(asset_id)
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")
            
        return self.depreciation_calc.calculate_straight_line(asset)
        
    def get_inventory_summary(self) -> Dict[str, Any]:
        """Сводка инвентаря"""
        by_type = defaultdict(int)
        by_status = defaultdict(int)
        by_environment = defaultdict(int)
        by_compliance = defaultdict(int)
        
        total_value = 0
        total_cost = 0
        
        for asset in self.assets.values():
            by_type[asset.asset_type.value] += 1
            by_status[asset.status.value] += 1
            by_environment[asset.environment or "unknown"] += 1
            by_compliance[asset.compliance_status.value] += 1
            
            if asset.financials:
                total_value += asset.financials.current_value
                total_cost += asset.financials.monthly_cost
                
        return {
            "total_assets": len(self.assets),
            "by_type": dict(by_type),
            "by_status": dict(by_status),
            "by_environment": dict(by_environment),
            "by_compliance": dict(by_compliance),
            "total_value": total_value,
            "total_monthly_cost": total_cost,
            "relationships": len(self.relationships)
        }
        
    def get_expiring_assets(self, days: int = 90) -> List[Asset]:
        """Активы с истекающим сроком"""
        threshold = datetime.now() + timedelta(days=days)
        expiring = []
        
        for asset in self.assets.values():
            # Проверяем EOL
            if asset.end_of_life_date and asset.end_of_life_date <= threshold:
                expiring.append(asset)
                continue
                
            # Проверяем гарантию
            if asset.financials and asset.financials.warranty_end:
                if asset.financials.warranty_end <= threshold:
                    expiring.append(asset)
                    continue
                    
        return expiring


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 86: Asset Management Platform")
    print("=" * 60)
    
    async def demo():
        platform = AssetManagementPlatform()
        print("✓ Asset Management Platform created")
        
        # Создание активов
        print("\n📦 Creating Assets...")
        
        # Физический сервер
        server1 = platform.create_asset(
            "prod-db-server-001",
            AssetType.SERVER,
            description="Primary database server",
            hostname="prod-db-001.dc1.local",
            ip_addresses=["10.0.1.10", "192.168.1.10"],
            serial_number="SN-2023-001234",
            owner="dba-team",
            team="database",
            environment="production",
            location=AssetLocation(
                datacenter="DC1",
                region="us-east",
                rack="R42",
                unit="U22-U24"
            ),
            financials=AssetFinancials(
                purchase_cost=25000,
                current_value=20000,
                monthly_cost=500,
                depreciation_rate=20,  # 20% в год = 5 лет
                purchase_date=datetime.now() - timedelta(days=365),
                warranty_end=datetime.now() + timedelta(days=730),
                vendor="Dell"
            ),
            specs=AssetSpecs(
                cpu_cores=64,
                memory_gb=512,
                storage_gb=10000,
                os="Ubuntu",
                os_version="22.04 LTS"
            ),
            compliance_frameworks=["SOC2", "ISO27001"]
        )
        
        print(f"\n  🖥️ {server1.asset_id}: {server1.name}")
        print(f"     Type: {server1.asset_type.value}")
        print(f"     Location: {server1.location.datacenter}, {server1.location.rack}")
        print(f"     Value: ${server1.financials.purchase_cost:,.0f}")
        
        # VM
        vm1 = platform.create_asset(
            "api-server-001",
            AssetType.VIRTUAL_MACHINE,
            description="API Gateway Server",
            hostname="api-001.prod.local",
            ip_addresses=["10.0.2.50"],
            owner="platform-team",
            team="platform",
            environment="production",
            location=AssetLocation(
                cloud_provider="AWS",
                cloud_account="prod-123456",
                region="us-east-1",
                zone="us-east-1a"
            ),
            financials=AssetFinancials(
                monthly_cost=350,
                vendor="AWS"
            ),
            specs=AssetSpecs(
                cpu_cores=8,
                memory_gb=32,
                storage_gb=200,
                os="Amazon Linux",
                os_version="2023"
            )
        )
        
        print(f"\n  ☁️ {vm1.asset_id}: {vm1.name}")
        print(f"     Type: {vm1.asset_type.value}")
        print(f"     Cloud: {vm1.location.cloud_provider}")
        
        # База данных
        db1 = platform.create_asset(
            "postgres-primary",
            AssetType.DATABASE,
            description="Primary PostgreSQL Database",
            hostname="postgres.prod.local",
            ip_addresses=["10.0.1.100"],
            owner="dba-team",
            team="database",
            environment="production",
            financials=AssetFinancials(
                monthly_cost=1200,
                vendor="AWS RDS"
            ),
            specs=AssetSpecs(
                cpu_cores=16,
                memory_gb=128,
                storage_gb=2000,
                custom_specs={"engine": "PostgreSQL", "version": "15.4"}
            )
        )
        
        print(f"\n  🗄️ {db1.asset_id}: {db1.name}")
        
        # Лицензия
        license1 = platform.create_asset(
            "Enterprise License",
            AssetType.LICENSE,
            description="Enterprise Software License",
            owner="it-procurement",
            team="it",
            financials=AssetFinancials(
                purchase_cost=50000,
                purchase_date=datetime.now() - timedelta(days=180),
                warranty_end=datetime.now() + timedelta(days=185),  # Истекает через ~6 мес
                vendor="Microsoft",
                contract_id="MS-ENT-2024-001"
            ),
            tags={"license_type": "enterprise", "seats": "500"}
        )
        license1.end_of_life_date = datetime.now() + timedelta(days=185)
        
        print(f"\n  📜 {license1.asset_id}: {license1.name}")
        
        # SSL сертификат
        cert1 = platform.create_asset(
            "*.company.com SSL Certificate",
            AssetType.CERTIFICATE,
            description="Wildcard SSL Certificate",
            owner="security-team",
            team="security",
            tags={"domain": "*.company.com", "type": "wildcard"}
        )
        cert1.end_of_life_date = datetime.now() + timedelta(days=60)  # Истекает через 60 дней
        
        print(f"\n  🔐 {cert1.asset_id}: {cert1.name}")
        
        # Load Balancer
        lb1 = platform.create_asset(
            "prod-alb-001",
            AssetType.LOAD_BALANCER,
            description="Production Application Load Balancer",
            hostname="prod-alb.us-east-1.elb.amazonaws.com",
            owner="platform-team",
            team="platform",
            environment="production",
            location=AssetLocation(
                cloud_provider="AWS",
                region="us-east-1"
            ),
            financials=AssetFinancials(
                monthly_cost=150
            )
        )
        
        print(f"\n  ⚖️ {lb1.asset_id}: {lb1.name}")
        
        # Создание связей
        print("\n🔗 Creating Asset Relationships...")
        
        # VM runs on Server
        platform.add_relationship(
            vm1.asset_id, server1.asset_id,
            RelationshipType.RUNS_ON,
            "API server runs on physical database server"
        )
        
        # API depends on DB
        platform.add_relationship(
            vm1.asset_id, db1.asset_id,
            RelationshipType.DEPENDS_ON,
            "API server depends on PostgreSQL database"
        )
        
        # LB connects to API
        platform.add_relationship(
            lb1.asset_id, vm1.asset_id,
            RelationshipType.CONNECTS_TO,
            "Load balancer routes traffic to API servers"
        )
        
        print(f"  ✓ Created {len(platform.relationships)} relationships")
        
        # Отображение связей
        print("\n📊 Asset Relationships:")
        
        for rel in platform.relationships:
            source = platform.assets.get(rel.source_asset_id)
            target = platform.assets.get(rel.target_asset_id)
            
            print(f"  {source.name if source else rel.source_asset_id}")
            print(f"    └──[{rel.relationship_type.value}]──> {target.name if target else rel.target_asset_id}")
            
        # Дерево зависимостей
        print("\n🌳 Dependency Tree (API Server):")
        
        tree = platform.get_dependency_tree(vm1.asset_id)
        
        def print_tree(node, indent=0):
            prefix = "  " * indent + ("└── " if indent > 0 else "")
            print(f"  {prefix}{node['name']} ({node['type']})")
            for dep in node.get("dependencies", []):
                print_tree(dep, indent + 1)
                
        print_tree(tree)
        
        # Жизненный цикл
        print("\n🔄 Lifecycle Management:")
        
        # Создаём новый актив в фазе закупки
        new_server = platform.create_asset(
            "new-server-001",
            AssetType.SERVER,
            description="New server being provisioned",
            lifecycle_phase=LifecyclePhase.PROCUREMENT,
            status=AssetStatus.PENDING
        )
        
        print(f"\n  New Asset: {new_server.name}")
        print(f"  Initial Phase: {new_server.lifecycle_phase.value}")
        
        # Переходы жизненного цикла
        event1 = platform.transition_lifecycle(
            new_server.asset_id,
            LifecyclePhase.DEPLOYMENT,
            reason="Hardware received and rack-mounted",
            by="ops-team"
        )
        print(f"  → {event1.to_phase.value} ({event1.reason})")
        
        event2 = platform.transition_lifecycle(
            new_server.asset_id,
            LifecyclePhase.PRODUCTION,
            reason="Testing completed, ready for production",
            by="ops-team"
        )
        print(f"  → {event2.to_phase.value} ({event2.reason})")
        
        # История жизненного цикла
        history = platform.lifecycle_manager.get_history(new_server.asset_id)
        
        print(f"\n  Lifecycle History:")
        for event in history:
            print(f"    {event.timestamp.strftime('%H:%M:%S')}: "
                  f"{event.from_phase.value} → {event.to_phase.value}")
            
        # Проверка соответствия
        print("\n✅ Compliance Checking:")
        
        checks = platform.check_compliance(server1.asset_id, "SOC2")
        
        print(f"\n  Asset: {server1.name}")
        print(f"  Framework: SOC2")
        print(f"  Results:")
        
        for check in checks:
            status_icon = "✅" if check.status == ComplianceStatus.COMPLIANT else "❌"
            print(f"    {status_icon} {check.control_id}: {check.status.value}")
            if check.findings:
                for finding in check.findings:
                    print(f"       Finding: {finding}")
                    
        print(f"\n  Overall Status: {server1.compliance_status.value}")
        
        # Расчёт амортизации
        print("\n💰 Asset Depreciation:")
        
        depreciation = platform.calculate_depreciation(server1.asset_id)
        
        print(f"\n  Asset: {server1.name}")
        print(f"  Purchase Cost: ${depreciation['purchase_cost']:,.2f}")
        print(f"  Current Value: ${depreciation['current_value']:,.2f}")
        print(f"  Total Depreciation: ${depreciation['total_depreciation']:,.2f}")
        print(f"  Years Owned: {depreciation['years_owned']:.1f}")
        print(f"  Remaining Life: {depreciation['remaining_life_years']:.1f} years")
        
        # Обнаружение активов
        print("\n🔍 Asset Discovery:")
        
        discovery_results = platform.discover_assets()
        
        print(f"\n  New Assets Found: {len(discovery_results['new'])}")
        print(f"  Matched Assets: {len(discovery_results['matched'])}")
        print(f"  Missing Assets: {len(discovery_results.get('missing', []))}")
        
        if discovery_results['new']:
            print("\n  New Discovered Assets:")
            for disc in discovery_results['new'][:5]:
                print(f"    • {disc.hostname} ({disc.ip_address}) - {disc.detected_type.value}")
                
        # Активы с истекающим сроком
        print("\n⏰ Expiring Assets (90 days):")
        
        expiring = platform.get_expiring_assets(90)
        
        if expiring:
            for asset in expiring:
                if asset.end_of_life_date:
                    days_left = (asset.end_of_life_date - datetime.now()).days
                    print(f"\n  ⚠️ {asset.name}")
                    print(f"     Expires in: {days_left} days")
                    print(f"     EOL Date: {asset.end_of_life_date.strftime('%Y-%m-%d')}")
        else:
            print("  ✅ No assets expiring in the next 90 days")
            
        # Сводка инвентаря
        print("\n📊 Inventory Summary:")
        
        summary = platform.get_inventory_summary()
        
        print(f"\n  Total Assets: {summary['total_assets']}")
        print(f"  Total Value: ${summary['total_value']:,.2f}")
        print(f"  Monthly Cost: ${summary['total_monthly_cost']:,.2f}")
        print(f"  Relationships: {summary['relationships']}")
        
        print("\n  By Type:")
        for asset_type, count in sorted(summary['by_type'].items(), key=lambda x: -x[1]):
            icon = {
                "server": "🖥️",
                "virtual_machine": "☁️",
                "database": "🗄️",
                "license": "📜",
                "certificate": "🔐",
                "load_balancer": "⚖️"
            }.get(asset_type, "📦")
            print(f"    {icon} {asset_type:20} {count}")
            
        print("\n  By Status:")
        for status, count in summary['by_status'].items():
            icon = {
                "active": "🟢",
                "inactive": "⚪",
                "maintenance": "🟡",
                "decommissioned": "🔴",
                "pending": "🔵"
            }.get(status, "⚪")
            print(f"    {icon} {status:20} {count}")
            
        print("\n  By Environment:")
        for env, count in summary['by_environment'].items():
            print(f"    {env:20} {count}")
            
        print("\n  Compliance Status:")
        for compliance, count in summary['by_compliance'].items():
            icon = "✅" if compliance == "compliant" else "❌" if compliance == "non_compliant" else "⏳"
            print(f"    {icon} {compliance:20} {count}")
            
        # Asset Dashboard
        print("\n📋 Asset Dashboard:")
        print("  ┌────────────────────────────────────────────────────┐")
        print(f"  │ Total Assets:    {summary['total_assets']:>6}                          │")
        print(f"  │ Active:          {summary['by_status'].get('active', 0):>6}                          │")
        print(f"  │ Total Value:     ${summary['total_value']:>10,.0f}                │")
        print(f"  │ Monthly Cost:    ${summary['total_monthly_cost']:>10,.0f}                │")
        print("  └────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Asset Management Platform initialized!")
    print("=" * 60)
